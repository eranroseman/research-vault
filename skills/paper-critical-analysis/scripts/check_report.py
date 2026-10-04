#!/usr/bin/env python3
"""Check a critical-analysis report and its evidence file against the templates.

Usage: python3 check_report.py REPORT.md [EVIDENCE.md]

EVIDENCE.md defaults to REPORT.md with ``.evidence.md`` in place of ``.md``.
The required headings are read from ``templates/report-template.md`` and
``templates/evidence-template.md`` beside this script; the templates are the
single source of truth for structure.

Errors (exit status 1):

- a required heading is missing;
- a section is empty: it holds nothing but its template's own text, line for
  line (a parent heading whose subsections hold the content may stay bare,
  and the ``Key:`` line always counts as content);
- a ``{{placeholder}}`` is still in place;
- the template's preamble, everything above its first thematic break, is
  still in place;
- a critical-discussion topic cites no locator, no named front-matter part or
  "whole paper", and no N/C/W/J ID, and says neither "not applicable" nor
  "not assessable";
- Credibility states no confidence level (high, medium, or low);
- a Coverage lead line from the template is missing or unfilled;
- a sentence containing "derived" cites no C, W or J entry (a table header
  row is exempt);
- the ``Key:`` provenance line is missing;
- a mandated-check slot in the evidence file's External-check list is
  missing, unfilled, or cites an ID the evidence file never defines;
- the ledger is broken: an ID defined in the evidence file appears neither in
  the report nor on Coverage's "Evidence file only" line, or the report cites
  an ID the evidence file never defines;
- the evidence file is missing.

A line inside a fenced code block is never a heading or a placeholder.
Warnings (exit status 0) point at things only a reader can judge.
"""

import argparse
import re
import sys
from pathlib import Path

Heading = tuple[str, str]  # (prefix the line must start with, heading as written)
Section = tuple[int, str, list[str]]  # (level, heading line, body lines)

SKILL_DIR = Path(__file__).resolve().parents[1]
REPORT_TEMPLATE = SKILL_DIR / "templates" / "report-template.md"
EVIDENCE_TEMPLATE = SKILL_DIR / "templates" / "evidence-template.md"

# mdformat renders a thematic break as a run of underscores; accept the raw
# forms too so a hand-written template still parses.
BREAK_RE = re.compile(r"^(?:_{3,}|-{3,}|\*{3,})\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+\S")
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")
PLACEHOLDER_RE = re.compile(r"\{\{")
NOT_APPLICABLE_RE = re.compile(r"\bnot (?:applicable|assessable)\b", re.IGNORECASE)
# "none found", "not checked", "not applicable" each need a tail saying where
# you looked or why: a following ":" ";" "," or a "because"-style connective.
BARE_PHRASE_RE = re.compile(
    r"\b(none found|not checked|not applicable)\b"
    r"(?!\s*[:;,]\s*\S)(?!\s+(?:because|since|as|for)\b)",
    re.IGNORECASE,
)
# A stated level, after the word ("Confidence: medium", "confidence is low")
# or before it ("medium confidence"); "confidence interval" is not one.
CONFIDENCE_RE = re.compile(
    r"\bconfidence(?:\s+level)?(?:\s*:\s*|\s+(?:is|was|remains|stays)\s+)"
    r"(?:high|medium|low)\b|\b(?:high|medium|low)\s+confidence\b",
    re.IGNORECASE,
)
BARE_SIGNIFICANT_RE = re.compile(
    r"(?<!statistically )(?<!non-)(?<!non )\bsignificant\b", re.IGNORECASE
)
# Explicit locators only: a word like "results" would let every critique pass.
LOCATOR_RE = re.compile(
    r"§\s*\d|\b(?i:sections?|sect\.|p\.|pp\.|pages?|fig\.|figures?|tables?|"
    r"appendix|appendices|eq\.|equations?|footnotes?|references?)\s*(?:[A-Z]|\d|\[)"
)
SECTION_NAME_RE = re.compile(r"\b(?:Abstract|Introduction|Related Work|Conclusions?)\b")
# SKILL.md's Locators section: a named front-matter part, or "whole paper".
FRONT_MATTER_RE = re.compile(
    r"\b(?:whole paper|title|abstract|author block|keywords)\b", re.IGNORECASE
)
ID_RE = re.compile(r"\b[NCWJ]\d+\b")
CWJ_ID_RE = re.compile(r"\b[CWJ]\d+\b")
DEFINED_ID_RE = re.compile(r"^- ([NCWJ]\d+):", re.MULTILINE)
DERIVED_RE = re.compile(r"\bderived\b", re.IGNORECASE)
# An abbreviation such as p., pp., Fig., Eq., Sect., Sec., Tab., cf., vs.,
# e.g., i.e. or et al. does not end a sentence.
SENTENCE_SPLIT_RE = re.compile(
    r"(?<=[.!?])(?<!\bp\.)(?<!\bpp\.)(?<!\b[Ff]ig\.)(?<!\b[Ee]q\.)"
    r"(?<!\b[Ss]ect\.)(?<!\be\.g\.)(?<!\bi\.e\.)(?<!\bal\.)"
    r"(?<!\bcf\.)(?<!\bvs\.)(?<!\b[Ss]ec\.)(?<!\b[Tt]ab\.)\s+"
)
TABLE_SEPARATOR_RE = re.compile(r"^\|?\s*:?-{3,}")
KEY_LINE_RE = re.compile(r"^Key: ", re.MULTILINE)


def _without_key_lines(text: str) -> str:
    """The ``Key:`` legend names (W12) and "derived" as examples; the ledger
    and derived rules must not read the legend as citations."""
    return "\n".join(line for line in text.splitlines() if not line.startswith("Key: "))


def fenced(lines: list[str]) -> list[bool]:
    """Whether each line belongs to a fenced code block, fence lines included.
    A fence opens on three or more backticks or tildes and closes on the next
    line starting with the same run, so ``~~~`` inside a backtick fence stays
    code."""
    flags: list[bool] = []
    fence = ""
    for line in lines:
        stripped = line.strip()
        if fence:
            flags.append(True)
            if stripped.startswith(fence):
                fence = ""
            continue
        match = FENCE_RE.match(stripped)
        fence = match.group(1) if match else ""
        flags.append(bool(match))
    return flags


def template_headings(path: Path) -> list[Heading]:
    """Required headings from a template: every heading after its first
    thematic break, outside fenced code. A heading carrying a
    ``{{placeholder}}`` matches by the prefix up to the braces."""
    required: list[Heading] = []
    seen_break = False
    lines = path.read_text(encoding="utf-8").splitlines()
    for line, in_fence in zip(lines, fenced(lines), strict=True):
        if in_fence:
            continue
        if not seen_break:
            seen_break = bool(BREAK_RE.match(line))
        elif HEADING_RE.match(line):
            full = line.rstrip()
            prefix = full.split("{{")[0].rstrip() if "{{" in full else full
            required.append((prefix, full))
    return required


def _report_headings() -> list[Heading]:
    return template_headings(REPORT_TEMPLATE)


def is_topic(heading: str) -> bool:
    """A critical-discussion topic: a level-3 heading between ``## 3.`` and
    ``## 4.`` in the report template, excluding the Verdicts block. Matched
    case-insensitively, like the structure check."""
    topics = []
    inside = False
    for prefix, _ in _report_headings():
        if prefix.startswith("## 3."):
            inside = True
        elif prefix.startswith("## "):
            inside = False
        elif (
            inside
            and prefix.startswith("### ")
            and not prefix.startswith("### Verdicts")
        ):
            topics.append(prefix.lower())
    return any(heading.lower().startswith(topic) for topic in topics)


def template_leads(path: Path, heading: str) -> dict[str, str]:
    """A template section's ``- <lead>: …`` bullets: each lead (the text
    between ``- `` and the first colon) with its stripped template line. A
    ledger-entry example such as ``- W1:`` is not a lead."""
    text = path.read_text(encoding="utf-8")
    section = text[text.index(heading) :]
    end = section.find("\n## ", 1)
    if end != -1:
        section = section[:end]
    return {
        line[2 : line.index(":")]: line.strip()
        for line in section.splitlines()
        if line.startswith("- ") and ":" in line and not DEFINED_ID_RE.match(line)
    }


def coverage_leads() -> list[str]:
    """The Coverage section's required lead words, from the template's own
    bullets."""
    return list(template_leads(REPORT_TEMPLATE, "## 4."))


def external_check_leads() -> list[str]:
    """The External-check section's mandated-slot leads, from the evidence
    template's own bullets, excluding the ``- W1:`` entry-shape example."""
    return list(template_leads(EVIDENCE_TEMPLATE, "## External-check list"))


def lead_line(section: str, lead: str) -> str | None:
    """The first line of ``section`` starting ``- <lead>:``, stripped."""
    stripped = [line.strip() for line in section.splitlines()]
    return next((line for line in stripped if line.startswith(f"- {lead}:")), None)


def is_unfilled(line: str, lead: str, template_line: str) -> bool:
    """Nothing after the lead's colon, or the template's own line verbatim."""
    return not line[len(f"- {lead}:") :].strip() or line == template_line


def sections(lines: list[str]) -> list[Section]:
    """Split lines into sections; text before the first heading is dropped. A
    line inside a fenced code block is body, never a heading."""
    out: list[Section] = []
    level = 0
    heading = ""
    body: list[str] = []
    for line, in_fence in zip(lines, fenced(lines), strict=True):
        match = None if in_fence else HEADING_RE.match(line)
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


def has_content(body: list[str], own_text: set[str]) -> bool:
    """A body holds content when one of its lines, stripped, is non-blank and
    is not a line of the template; the ``Key:`` line always counts."""
    return any(
        line.startswith("Key: ") or (line.strip() and line.strip() not in own_text)
        for line in body
    )


def structure_errors(
    label: str, lines: list[str], found: list[Section], template: Path
) -> list[str]:
    """Missing headings, empty sections, the template preamble, and leftover
    placeholders, each judged against ``template``, the file's own."""
    template_lines = template.read_text(encoding="utf-8").splitlines()
    own_text = {line.strip() for line in template_lines if line.strip()}
    errors: list[str] = []
    headings = [heading.lower() for _, heading, _ in found]
    for prefix, full in template_headings(template):
        if not any(heading.startswith(prefix.lower()) for heading in headings):
            errors.append(f"{label}: missing heading: {full}")
    if any(line.strip() == template_lines[0].strip() for line in lines):
        errors.append(
            f"{label}: template preamble still in place; keep only what is below "
            "the template's first thematic break"
        )
    for index, (level, heading, body) in enumerate(found):
        if has_content(body, own_text):
            continue
        next_level = found[index + 1][0] if index + 1 < len(found) else 0
        if level == 1 or next_level <= level:
            what = (
                " (nothing but the template's own text)"
                if any(line.strip() for line in body)
                else ""
            )
            errors.append(f"{label}: empty section{what}: {heading}")
    for number, (line, in_fence) in enumerate(
        zip(lines, fenced(lines), strict=True), start=1
    ):
        if not in_fence and PLACEHOLDER_RE.search(line):
            errors.append(
                f"{label}: line {number}: template placeholder still in place"
            )
    return errors


def evidence_errors(found: list[Section]) -> list[str]:
    """Each topic cites a locator, a named front-matter part or an N/C/W/J
    ID, or says not applicable or not assessable."""
    errors: list[str] = []
    for index, (level, heading, _) in enumerate(found):
        if level != 3 or not is_topic(heading):
            continue
        text = section_text(found, index)
        if (
            NOT_APPLICABLE_RE.search(text)
            or LOCATOR_RE.search(text)
            or ID_RE.search(text)
            or SECTION_NAME_RE.search(text)
            or FRONT_MATTER_RE.search(text)
        ):
            continue
        errors.append(f"report: no locator or ID cited: {heading}")
    return errors


def derived_errors(lines: list[str]) -> list[str]:
    """Every sentence containing "derived" cites the C, W or J entry holding
    the computation. A sentence ends at ., !, ? or the line break; the
    abbreviations p., pp., Fig., Eq., Sect., Sec., Tab., cf., vs., e.g., i.e.,
    or et al. do not end one. A table header row, a ``|`` line above a
    separator row, names columns and is exempt; data rows are checked."""
    errors: list[str] = []
    for index, line in enumerate(lines):
        header = (
            line.startswith("|")
            and index + 1 < len(lines)
            and TABLE_SEPARATOR_RE.match(lines[index + 1].strip())
        )
        if line.startswith("Key: ") or header:
            continue
        errors.extend(
            [
                f"report: line {index + 1}: derived number cites no C, W or J entry"
                for sentence in SENTENCE_SPLIT_RE.split(line)
                if DERIVED_RE.search(sentence) and not CWJ_ID_RE.search(sentence)
            ]
        )
    return errors


def coverage_errors(found: list[Section]) -> list[str]:
    """Each Coverage lead from the template is present and filled."""
    coverage = find_section(found, "## 4.")
    if coverage is None:
        return []  # the missing heading is already reported
    errors: list[str] = []
    for lead, template_line in template_leads(REPORT_TEMPLATE, "## 4.").items():
        line = lead_line(coverage, lead)
        if line is None:
            errors.append(f"report: Coverage is missing its '{lead}' line")
        elif is_unfilled(line, lead, template_line):
            errors.append(f"report: Coverage '{lead}' line is unfilled")
    return errors


def slot_errors(found: list[Section], defined: set[str]) -> list[str]:
    """Each mandated-check slot is present, filled, and cites only IDs the
    evidence file defines."""
    external = find_section(found, "## External-check list")
    if external is None:
        return []  # the missing heading is already reported
    errors: list[str] = []
    leads = template_leads(EVIDENCE_TEMPLATE, "## External-check list")
    for lead, template_line in leads.items():
        line = lead_line(external, lead)
        if line is None:
            errors.append(f"evidence: External-check list is missing its '{lead}' slot")
        elif is_unfilled(line, lead, template_line):
            errors.append(f"evidence: External-check list '{lead}' slot is unfilled")
        else:
            errors.extend(
                f"evidence: External-check list '{lead}' slot cites {entry}, "
                "which the evidence file never defines"
                for entry in dict.fromkeys(ID_RE.findall(line))
                if entry not in defined
            )
    return errors


def ledger_errors(report_text: str, evidence_text: str) -> list[str]:
    """Every ID defined in the evidence file appears in the report (the
    "Evidence file only" line counts); every ID the report cites is defined."""
    defined = set(DEFINED_ID_RE.findall(evidence_text))
    cited = set(ID_RE.findall(_without_key_lines(report_text)))
    errors = [
        f"report: broken ledger: {entry} is defined in the evidence file and "
        "appears neither in the report nor on Coverage's 'Evidence file only' line"
        for entry in sorted(defined - cited)
    ]
    errors.extend(
        f"report: broken ledger: {entry} is cited and the evidence file never "
        "defines it"
        for entry in sorted(cited - defined)
    )
    return errors


def phrase_warnings(label: str, lines: list[str]) -> list[str]:
    """Bare 'none found' / 'not checked' / 'not applicable' without a tail."""
    return [
        f"{label}: line {number}: bare '{match.group(1)}'; add where you looked or why"
        for number, line in enumerate(lines, start=1)
        for match in BARE_PHRASE_RE.finditer(line)
    ]


def check_report(text: str, evidence_text: str | None) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for the report, and the cross-file rules."""
    lines = text.splitlines()
    found = sections(lines)
    errors = structure_errors("report", lines, found, REPORT_TEMPLATE)
    errors.extend(evidence_errors(found))
    errors.extend(derived_errors(lines))
    errors.extend(coverage_errors(found))
    credibility = find_section(found, "### Credibility")
    if credibility is not None and not CONFIDENCE_RE.search(credibility):
        errors.append("report: Credibility states no confidence (high, medium, or low)")
    if not KEY_LINE_RE.search(text):
        errors.append("report: missing provenance key (the 'Key:' line)")
    if evidence_text is not None:
        errors.extend(ledger_errors(text, evidence_text))

    warnings = phrase_warnings("report", lines)
    bare = len(BARE_SIGNIFICANT_RE.findall(text))
    if bare:
        warnings.append(
            f"report: 'significant' appears {bare} time(s) without 'statistically'; "
            "fine in prose, wrong for a test result"
        )
    return errors, warnings


def check_evidence(text: str) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for the evidence file."""
    lines = text.splitlines()
    found = sections(lines)
    errors = structure_errors("evidence", lines, found, EVIDENCE_TEMPLATE)
    errors.extend(slot_errors(found, set(DEFINED_ID_RE.findall(text))))
    return errors, phrase_warnings("evidence", lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("report", type=Path, help="the report Markdown file")
    parser.add_argument(
        "evidence",
        type=Path,
        nargs="?",
        help=(
            "the evidence file; defaults to REPORT with .evidence.md in place of .md"
        ),
    )
    args = parser.parse_args(argv)
    evidence_path = args.evidence or args.report.with_suffix(".evidence.md")

    evidence_text: str | None = None
    errors: list[str] = []
    warnings: list[str] = []
    if evidence_path.is_file():
        evidence_text = evidence_path.read_text(encoding="utf-8")
        errors, warnings = check_evidence(evidence_text)
    else:
        errors.append(f"evidence: file not found: {evidence_path}")
    report_errors, report_warnings = check_report(
        args.report.read_text(encoding="utf-8"), evidence_text
    )
    errors = report_errors + errors
    warnings = report_warnings + warnings

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
