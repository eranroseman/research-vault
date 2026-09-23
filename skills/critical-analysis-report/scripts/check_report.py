#!/usr/bin/env python3
"""Check a critical-analysis report and its notes file against the templates.

Usage: python3 check_report.py REPORT.md [NOTES.md]

NOTES.md defaults to REPORT.md with ``.notes.md`` in place of ``.md``.

Errors (exit status 1): a required heading is missing, a section has no text,
a ``{{placeholder}}`` from a template is still in place, the notes file is
missing, a critical-discussion topic neither cites a locator in the paper
nor says "not applicable", or Credibility states no confidence. Warnings
(exit status 0) point at things only a reader can judge.
"""

import argparse
import re
import sys
from pathlib import Path

Heading = tuple[str, str]  # (prefix the line must start with, heading as written)
Section = tuple[int, str, list[str]]  # (level, heading line, body lines)

SECTION_HEADINGS: tuple[Heading, ...] = (
    ("### 1.1", "### 1.1 Title and authors"),
    ("### 1.2", "### 1.2 Publication venue"),
    ("### 1.3", "### 1.3 The authors' previous work"),
    ("### 1.4", "### 1.4 Motivation"),
    ("### 1.5", "### 1.5 Related work and references"),
    ("### 2.1", "### 2.1 Problem"),
    ("### 2.2", "### 2.2 Method"),
    ("### 2.3", "### 2.3 Results"),
    ("### 2.4", "### 2.4 Discussion"),
    ("### 2.5", "### 2.5 Conclusion"),
)
TOPIC_HEADINGS: tuple[Heading, ...] = tuple(
    (f"### {topic}", f"### {topic}")
    for topic in (
        "Importance",
        "Credibility",
        "Novelty",
        "Applicability",
        "Generalizability",
        "Scalability",
        "Assumptions",
        "Readability",
        "Ethics",
    )
)
REPORT_HEADINGS: tuple[Heading, ...] = (
    ("# Critical analysis", "# Critical analysis: <paper title>"),
    ("## 1.", "## 1. Context"),
    *SECTION_HEADINGS[:5],
    ("## 2.", "## 2. Summary"),
    *SECTION_HEADINGS[5:],
    ("## 3.", "## 3. Critical discussion"),
    *TOPIC_HEADINGS,
    ("## 4.", "## 4. Coverage"),
)
NOTES_HEADINGS: tuple[Heading, ...] = (
    ("# Notes", "# Notes: <paper title>"),
    ("## Identity", "## Identity"),
    ("## Section map", "## Section map"),
    ("## Promises", "## Promises"),
    ("## Method family", "## Method family"),
    ("## Template answers", "## Template answers"),
    *SECTION_HEADINGS,
    *TOPIC_HEADINGS,
    ("## Reference counts", "## Reference counts"),
    ("## Related work checks", "## Related work checks"),
    ("## Lookups", "## Lookups"),
    ("## Gaps", "## Gaps"),
    ("## Coverage", "## Coverage"),
)

TOPIC_LEVEL = 3  # the nine topics are ### headings
HEADING_RE = re.compile(r"^(#{1,6})\s+\S")
PLACEHOLDER_RE = re.compile(r"\{\{")
NOT_APPLICABLE_RE = re.compile(r"\bnot applicable\b", re.IGNORECASE)
# "none found", "not checked", "not applicable" each need a tail saying where
# you looked or why: a following ":" ";" "," or a "because"-style connective.
BARE_PHRASE_RE = re.compile(
    r"\b(none found|not checked|not applicable)\b"
    r"(?!\s*[:;,]\s*\S)(?!\s+(?:because|since|as|for)\b)",
    re.IGNORECASE,
)
CONFIDENCE_RE = re.compile(
    r"\bconfidence\b.*?\b(?:high|medium|low)\b", re.IGNORECASE | re.DOTALL
)
VERIFIED_RE = re.compile(r"verif", re.IGNORECASE)
BARE_SIGNIFICANT_RE = re.compile(
    r"(?<!statistically )(?<!non-)(?<!non )\bsignificant\b", re.IGNORECASE
)
# Explicit locators only: a word like "results" would let every critique pass.
LOCATOR_RE = re.compile(
    r"§\s*\d|\b(?i:sections?|sect\.|p\.|pp\.|pages?|fig\.|figures?|tables?|"
    r"appendix|appendices|eq\.|equations?|footnotes?)\s*(?:[A-Z]|\d)"
)
SECTION_NAME_RE = re.compile(r"\b(?:Abstract|Introduction|Related Work|Conclusions?)\b")


def sections(lines: list[str]) -> list[Section]:
    """Split lines into sections; text before the first heading is dropped."""
    out: list[Section] = []
    level = 0
    heading = ""
    body: list[str] = []
    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            if level:
                out.append((level, heading, body))
            level, heading, body = len(match.group(1)), line.rstrip(), []
        elif level:
            body.append(line)
    if level:
        out.append((level, heading, body))
    return out


def section_text(found: list[Section], index: int) -> str:
    """Body of section ``index`` plus the bodies of its deeper subsections."""
    level, _, body = found[index]
    parts = list(body)
    for next_level, _, next_body in found[index + 1 :]:
        if next_level <= level:
            break
        parts.extend(next_body)
    return "\n".join(parts)


def find_section(found: list[Section], prefix: str) -> str | None:
    """Text of the first section whose heading starts with ``prefix``."""
    for index, (_, heading, _) in enumerate(found):
        if heading.lower().startswith(prefix.lower()):
            return section_text(found, index)
    return None


def structure_errors(
    label: str, lines: list[str], found: list[Section], required: tuple[Heading, ...]
) -> list[str]:
    """Missing headings, empty sections, and leftover placeholders."""
    errors: list[str] = []
    headings = [heading.lower() for _, heading, _ in found]
    for prefix, full in required:
        if not any(heading.startswith(prefix.lower()) for heading in headings):
            errors.append(f"{label}: missing heading: {full}")
    for index, (level, heading, body) in enumerate(found):
        if any(line.strip() for line in body):
            continue
        next_level = found[index + 1][0] if index + 1 < len(found) else 0
        if level == 1 or next_level <= level:
            errors.append(f"{label}: empty section: {heading}")
    for number, line in enumerate(lines, start=1):
        if PLACEHOLDER_RE.search(line):
            errors.append(
                f"{label}: line {number}: template placeholder still in place"
            )
    return errors


def evidence_errors(found: list[Section]) -> list[str]:
    """Each critical-discussion topic cites a location or says not applicable."""
    errors: list[str] = []
    prefixes = [prefix.lower() for prefix, _ in TOPIC_HEADINGS]
    for index, (level, heading, _) in enumerate(found):
        is_topic = any(heading.lower().startswith(p) for p in prefixes)
        if level != TOPIC_LEVEL or not is_topic:
            continue
        text = section_text(found, index)
        if NOT_APPLICABLE_RE.search(text) or LOCATOR_RE.search(text):
            continue
        if SECTION_NAME_RE.search(text):
            continue
        errors.append(f"report: no locator cited: {heading}")
    return errors


def phrase_warnings(label: str, lines: list[str]) -> list[str]:
    """Bare 'none found' / 'not checked' / 'not applicable' without a tail."""
    return [
        f"{label}: line {number}: bare '{match.group(1)}'; add where you looked or why"
        for number, line in enumerate(lines, start=1)
        for match in BARE_PHRASE_RE.finditer(line)
    ]


def check_report(text: str) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for the report text."""
    lines = text.splitlines()
    found = sections(lines)
    errors = structure_errors("report", lines, found, REPORT_HEADINGS)
    errors.extend(evidence_errors(found))
    credibility = find_section(found, "### Credibility")
    if credibility is not None and not CONFIDENCE_RE.search(credibility):
        errors.append("report: Credibility states no confidence (high, medium, or low)")

    warnings = phrase_warnings("report", lines)
    coverage = find_section(found, "## 4.")
    if coverage is not None and not VERIFIED_RE.search(coverage):
        warnings.append("report: Coverage does not say how the report was verified")
    bare = len(BARE_SIGNIFICANT_RE.findall(text))
    if bare:
        warnings.append(
            f"report: 'significant' appears {bare} time(s) without 'statistically'; "
            "fine in prose, wrong for a test result"
        )
    return errors, warnings


def check_notes(text: str) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for the notes text."""
    lines = text.splitlines()
    errors = structure_errors("notes", lines, sections(lines), NOTES_HEADINGS)
    return errors, phrase_warnings("notes", lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("report", type=Path, help="the report Markdown file")
    parser.add_argument(
        "notes",
        type=Path,
        nargs="?",
        help="the notes file; defaults to REPORT with .notes.md in place of .md",
    )
    args = parser.parse_args(argv)
    notes_path = args.notes or args.report.with_suffix(".notes.md")

    errors, warnings = check_report(args.report.read_text(encoding="utf-8"))
    if notes_path.is_file():
        notes_errors, notes_warnings = check_notes(
            notes_path.read_text(encoding="utf-8")
        )
        errors.extend(notes_errors)
        warnings.extend(notes_warnings)
    else:
        errors.append(f"notes: file not found: {notes_path}")

    for message in errors:
        sys.stdout.write(f"error: {message}\n")
    for message in warnings:
        sys.stdout.write(f"warning: {message}\n")
    if errors:
        sys.stdout.write(f"{len(errors)} error(s)\n")
        return 1
    sys.stdout.write("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
