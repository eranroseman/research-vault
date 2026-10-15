#!/usr/bin/env python3
"""Check the shapes of the experiment-proposal plugin's files.

Usage:
    check_proposal.py [--json] brief proposal/design-brief.md
    check_proposal.py [--json] review proposal/review.md
    check_proposal.py [--json] draft proposal/draft.md [--sections "A, B, ..."]
        [--words 2000-4000] [--references 15-20] [--supervisor "<name>"]

Exit 0: clean. Exit 1: defects, one per line as `<file>:<line>: <message>`
(a JSON list with --json). Exit 2: a file could not be read, the arguments
were malformed, or the interpreter is older than 3.11.

This script is the single source of truth for the three shapes. The files
references/brief.md and references/review.md describe the same shapes in
prose for the skills that write them. The item set comes from the checklist
beside this script, so no item is duplicated here.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Callable, Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

CHECKLIST = Path(__file__).resolve().parents[1] / "references" / "checklist.md"

ITEM = re.compile(
    r"^- \*\*(\d{1,2}\.\d{1,2})\*\* "
    r"\((draft-checked|attested|defend-stage); (design-tree|review-only); "
    r"depends on ([^)]+)\) (.+)$"
)
# the first plugin version whose brief shape this checker checks; bump when the shape changes
SHAPE_VERSION = (0, 2)
STATUSES = ("settled", "pilot settles", "provisional")
ENTRY_LINES = ("Decision", "Rationale", "Would change if", "Status", "Source")
AMENDMENT_LINES = ("New decision", "Reason", "Replaces")
DECISION_MAX = 400
BRIEF_SECTIONS = ("Decisions", "Looked up", "Open items")
HEADER_DRAFT = re.compile(r"^Draft: \S")
HEADER_STATUS = re.compile(r"^Status: (open|frozen \d{4}-\d{2}-\d{2})$")
HEADER_VERSION = re.compile(r"^Checklist: experiment-proposal \d+\.\d+\.\d+$")
ENTRY = re.compile(r"^### (\d{1,2}\.\d{1,2}) (.+)$")
AMENDMENT = re.compile(r"^### \d{4}-\d{2}-\d{2}, item (\d{1,2}\.\d{1,2}), .+$")
OPEN_LINE = re.compile(r"^\d+\. (.+)$")
OPEN_REF = re.compile(r"\bItems? (\d{1,2}\.\d{1,2})\b")
COMMAND = "/experiment-proposal:"
REVIEW_HEADER = ("Brief:", "Draft:", "Date:", "Checklist:")
REVIEW_SECTIONS = (
    "Items",
    "Cross-section consistency",
    "Brief against draft",
    "Substance tests",
    "Summary",
    "Waivers",
    "Hand-off",
)
SUBSTANCE = ("13.6", "13.7", "13.8", "13.9", "13.10", "13.11")
RESULTS = ("pass narrowly", "pass", "fail (waived)", "fail", "not checked")
ROW = re.compile(
    r"^- \*\*(\d{1,2}\.\d{1,2})\*\* ("
    + "|".join(re.escape(r) for r in RESULTS)
    + r")(?: \(fix (\d+) applied\))?(?::\s*(.*))?$"
)
FIX = re.compile(r"\bfix (\d+)\b", re.IGNORECASE)
APPLIED = re.compile(r"\(fix (\d+) applied\)", re.IGNORECASE)
QUOTE = re.compile(r'"[^"]+"\s*\([^)]+\)')
CONFIRMED = re.compile(r"confirmed by the user, \d{4}-\d{2}-\d{2}")
SUMMARY = re.compile(
    r"^Items checked: (\d+)\. Pass: (\d+)\. Fail: (\d+)\. Not checked \(defend-stage\): (\d+)\. "
    r"Consistency and brief findings: (\d+)\. Fixes proposed: (\d+)\. Waivers: (\d+)\.$"
)
SUMMARY_LABELS = (
    "Items checked",
    "Pass",
    "Fail",
    "Not checked (defend-stage)",
    "Consistency and brief findings",
    "Fixes proposed",
    "Waivers",
)
DEFEND = "/oss:research-grill defend"
INSTALL = (
    "claude plugin marketplace add scdenney/open-science-skills",
    "claude plugin install oss@open-science-skills",
)
HEADING = re.compile(r"^(#{1,6}) (.+)$")
LIST_ITEM = re.compile(r"^(?:[-*] |\d+\. )")
SUPERVISION = re.compile(
    r"under\s+the\s+supervision\s+of\s+([^\n]{1,60})", re.IGNORECASE
)
NUMBERING = re.compile(r"^\d+(?:\.\d+)*\.?\s*")


def _norm(text: str) -> str:
    """A heading as a key: numbering stripped, lower case, letters and digits."""
    return re.sub(r"[^a-z0-9 ]+", " ", NUMBERING.sub("", text.strip()).lower()).strip()


def _singular(text: str) -> str:
    """Each word of a normalised heading without a trailing `es`, else a
    trailing `s`, so `questions` and `question` meet at `question`."""
    return " ".join(re.sub(r"(?<=.)(?:es|s)$", "", word) for word in text.split())


def _matches(heading: str, name: str) -> bool:
    """`## 2. Literature Review` matches `Literature review`; `## Appendices` and
    `## Appendix B: consent form` both match `Appendix`, but only `## Appendix B...`
    matches `Appendix B`. A name with ` or ` (in any case) matches a heading that
    starts with either side; singular and plural words meet."""
    key = _singular(_norm(heading))
    for side in re.split(r"\s+or\s+", name, flags=re.IGNORECASE):
        target = _norm(side)
        if not target:
            continue
        if key.startswith("append" if target == "appendix" else _singular(target)):
            return True
    return False


@dataclass(frozen=True)
class Item:
    kind: str
    scope: str
    depends: tuple[str, ...]
    text: str
    line: int


@dataclass(frozen=True)
class Defect:
    path: str
    line: int
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


Adder = Callable[[int, str], None]


def clean(line: str) -> str:
    """The line as its author wrote it: mdformat's escapes undone, trailing
    spaces dropped."""
    for escaped, plain in (("\\_", "_"), ("\\*", "*"), ("\\[", "["), ("\\]", "]")):
        line = line.replace(escaped, plain)
    return line.rstrip()


def item_key(item_id: str) -> tuple[int, int]:
    step, number = item_id.split(".")
    return int(step), int(number)


def read_checklist(path: Path = CHECKLIST) -> dict[str, Item]:
    """Every item line under a `## Step` heading, by the pinned grammar."""
    items: dict[str, Item] = {}
    in_steps = False
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = clean(raw)
        if line.startswith("## "):
            in_steps = line.startswith("## Step ")
            continue
        if not in_steps or not line.startswith("- "):
            continue
        match = ITEM.match(line)
        if match is None:
            raise ValueError(f"{path}:{number}: not an item line: {line[:80]}")
        item_id, kind, scope, depends, text = match.groups()
        if item_id in items:
            raise ValueError(f"{path}:{number}: duplicate item {item_id}")
        deps = () if depends == "none" else tuple(d.strip() for d in depends.split(","))
        items[item_id] = Item(kind, scope, deps, text, number)
    return items


def sections_of(lines: Sequence[str]) -> list[tuple[str, int, int]]:
    """(name, heading line number, last line number) for every `## ` heading."""
    heads = [
        (clean(line)[3:].strip(), number)
        for number, line in enumerate(lines, 1)
        if clean(line).startswith("## ")
    ]
    out = []
    for index, (name, start) in enumerate(heads):
        end = heads[index + 1][1] - 1 if index + 1 < len(heads) else len(lines)
        out.append((name, start, end))
    return out


def blocks_of(
    lines: Sequence[str], start: int, end: int
) -> list[tuple[int, str, list[tuple[int, str]]]]:
    """The `### ` blocks between two line numbers (1-based, inclusive):
    (heading line, heading text, the body as (line, text) pairs)."""
    blocks: list[tuple[int, str, list[tuple[int, str]]]] = []
    for number in range(start + 1, end + 1):
        line = clean(lines[number - 1])
        if line.startswith("### "):
            blocks.append((number, line[4:], []))
        elif blocks:
            blocks[-1][2].append((number, line))
    return blocks


def labelled_lines(
    add: Adder, body: Iterable[tuple[int, str]], labels: Sequence[str], where: str
) -> dict[str, tuple[int, str]]:
    """The dash lines of a block are exactly `- <label>:` for the labels, in
    order; blank lines are allowed; any other line is reported. Returns
    label -> (line number, value)."""
    body = list(body)
    dashes = [(n, line) for n, line in body if line.startswith("- ")]
    for n, line in body:
        if line.strip() and not line.startswith("- "):
            add(
                n,
                f"{where}: unexpected line (a block is its labelled lines only): {line[:60]}",
            )
    expected = [f"- {label}:" for label in labels]
    found = [line.split(":", 1)[0] + ":" for _, line in dashes]
    if found != expected:
        at = dashes[0][0] if dashes else (body[0][0] if body else 0)
        add(
            at,
            f"{where}: lines must be exactly {', '.join(expected)} in that order; found {', '.join(found) or 'none'}",
        )
    values: dict[str, tuple[int, str]] = {}
    for n, line in dashes:
        label, _, value = line[2:].partition(":")
        values[label] = (n, value.strip())
    return values


def header_of(
    lines: Sequence[str], sections: Sequence[tuple[str, int, int]]
) -> list[str]:
    first = sections[0][1] if sections else len(lines) + 1
    return [clean(line) for line in lines[: first - 1]]


def header_defects(add: Adder, header: Sequence[str]) -> re.Match[str] | None:
    """The three header lines. Returns the match of the Status line, or None."""
    if not any(HEADER_DRAFT.match(line) for line in header):
        add(1, "header: no `Draft: <path>` line")
    status = next((m for line in header if (m := HEADER_STATUS.match(line))), None)
    if status is None:
        add(1, "header: no `Status: open` or `Status: frozen YYYY-MM-DD` line")
    if not any(HEADER_VERSION.match(line) for line in header):
        add(1, "header: no `Checklist: experiment-proposal <version>` line")
    return status


def _checklist_version(header: Sequence[str]) -> str | None:
    """The `<major>.<minor>.<patch>` of the `Checklist:` line, or None."""
    return next(
        (line.rsplit(" ", 1)[1] for line in header if HEADER_VERSION.match(line)), None
    )


def _older_than_shape(version: str) -> bool:
    major, minor, _patch = version.split(".")
    return (int(major), int(minor)) < SHAPE_VERSION


def decisions_of(
    add: Adder,
    lines: Sequence[str],
    span: tuple[int, int],
    design_tree: set[str],
) -> dict[str, str]:
    """The entries under `## Decisions`, checked. Returns item id -> Status value."""
    entries: dict[str, str] = {}
    start, end = span
    for number, heading, body in blocks_of(lines, start, end):
        match = ENTRY.match("### " + heading)
        if match is None:
            add(number, f"entry heading must be `### <ID> <title>`: {heading[:60]}")
            continue
        item_id = match.group(1)
        if item_id not in design_tree:
            add(number, f"entry {item_id} is not a design-tree item")
        if item_id in entries:
            add(number, f"entry {item_id} appears twice")
        values = labelled_lines(add, body, ENTRY_LINES, f"entry {item_id}")
        for label in ENTRY_LINES:
            if label in values and not values[label][1]:
                add(values[label][0], f"entry {item_id}: {label} is empty")
        status_line, status_value = values.get("Status", (number, ""))
        if status_value not in STATUSES:
            add(
                status_line,
                f"entry {item_id}: Status must be settled, pilot settles or provisional; found {status_value!r}",
            )
        if "Decision" in values:
            decision_line, decision = values["Decision"]
            length = len("- Decision: " + decision)
            if length > DECISION_MAX:
                add(
                    decision_line,
                    f"entry {item_id}: Decision line is {length} characters; at most {DECISION_MAX}",
                )
        entries[item_id] = status_value
    if list(entries) != sorted(entries, key=item_key):
        add(start, "entries are not in checklist order")
    return entries


def open_items_defects(
    add: Adder,
    lines: Sequence[str],
    span: tuple[int, int],
    entries: dict[str, str],
) -> None:
    """`## Open items`: provisional items first, then the commands; every
    provisional entry listed and every item named a provisional entry."""
    start, end = span
    seen_command = False
    referenced: set[str] = set()
    for number in range(start + 1, end + 1):
        line = clean(lines[number - 1])
        if OPEN_LINE.match(line) is None:
            continue
        if COMMAND in line:
            seen_command = True
            continue
        ref = OPEN_REF.search(line)
        if ref is None:
            continue
        item_id = ref.group(1)
        referenced.add(item_id)
        if seen_command:
            add(number, "Open items: provisional items come before the commands")
        if item_id not in entries:
            add(number, f"Open items names item {item_id}, which has no entry")
        elif entries[item_id] != "provisional":
            add(
                number,
                f"Open items names item {item_id}, whose entry is {entries[item_id]}, not provisional",
            )
    for item_id, entry_status in entries.items():
        if entry_status == "provisional" and item_id not in referenced:
            add(
                start,
                f"entry {item_id} is provisional but not listed under Open items",
            )


def amendment_defects(add: Adder, lines: Sequence[str], span: tuple[int, int]) -> None:
    """`## Amendments`: each block a dated heading and the three labelled lines."""
    start, end = span
    for number, heading, body in blocks_of(lines, start, end):
        if AMENDMENT.match("### " + heading) is None:
            add(
                number,
                f"amendment heading must be `### YYYY-MM-DD, item <ID>, <title>`: {heading[:60]}",
            )
        labelled_lines(add, body, AMENDMENT_LINES, f"amendment at line {number}")


def check_brief(path: Path, items: dict[str, Item]) -> list[Defect]:
    lines = path.read_text(encoding="utf-8").splitlines()
    defects: list[Defect] = []

    def add(line: int, message: str) -> None:
        defects.append(Defect(str(path), line, message))

    sections = sections_of(lines)
    names = [name for name, _, _ in sections]
    first = sections[0][1] if sections else 1
    by_name = {name: (start, end) for name, start, end in sections}
    header = header_of(lines, sections)
    status = header_defects(add, header)
    version = _checklist_version(header)
    frozen = status is not None and status.group(1).startswith("frozen")
    if frozen and version is not None and _older_than_shape(version):
        print(
            f"{path}: brief frozen under checklist {version}; "
            "only the header and Amendments are checked",
            file=sys.stderr,
        )
        if "Amendments" in by_name:
            amendment_defects(add, lines, by_name["Amendments"])
        return defects
    for name, start, _ in sections:
        if name not in BRIEF_SECTIONS and name != "Amendments":
            add(
                start,
                f"section `## {name}` is not one of Decisions, Looked up, Open items, Amendments",
            )
    if [n for n in names if n in BRIEF_SECTIONS] != list(BRIEF_SECTIONS):
        add(
            first,
            "sections must be Decisions, Looked up, Open items, in that order (Amendments optional, last)",
        )
    if "Amendments" in names and names[-1] != "Amendments":
        add(
            sections[names.index("Amendments")][1],
            "Amendments must be the last section",
        )
    design_tree = {i for i, it in items.items() if it.scope == "design-tree"}
    entries: dict[str, str] = {}
    if "Decisions" in by_name:
        entries = decisions_of(add, lines, by_name["Decisions"], design_tree)
    if "Open items" in by_name:
        open_items_defects(add, lines, by_name["Open items"], entries)
    if frozen:
        for item_id in sorted(design_tree - set(entries), key=item_key):
            add(1, f"frozen brief has no entry for design-tree item {item_id}")
    if "Amendments" in by_name:
        amendment_defects(add, lines, by_name["Amendments"])
    return defects


def _review_rows(
    add: Adder,
    lines: Sequence[str],
    items: dict[str, Item],
    section: tuple[int, int],
    name: str,
    expected: Sequence[str],
    results: dict[str, str],
) -> None:
    start, end = section
    found: list[str] = []
    for number in range(start + 1, end + 1):
        line = clean(lines[number - 1])
        if not line.startswith("- **"):
            continue
        match = ROW.match(line)
        if match is None:
            add(
                number,
                f"row does not fit `- **<ID>** <result>[ (fix N applied)][: ...]`: {line[:60]}",
            )
            continue
        item_id, result, _fix, rest = (
            match.group(1),
            match.group(2),
            match.group(3),
            match.group(4) or "",
        )
        found.append(item_id)
        item = items.get(item_id)
        if item is None:
            add(number, f"row {item_id} is not a checklist item")
            continue
        results[item_id] = result
        if item.kind == "defend-stage" and result != "not checked":
            add(
                number,
                f"row {item_id} is a defend-stage item and must read `not checked`",
            )
        if item.kind != "defend-stage" and result == "not checked":
            add(
                number,
                f"row {item_id} reads `not checked`; only items 13.2 and 13.3 may",
            )
        if result in ("pass", "pass narrowly"):
            if item.kind == "draft-checked" and QUOTE.search(rest) is None:
                add(
                    number,
                    f"row {item_id} passes without a quoted passage and its location",
                )
            if item.kind == "attested" and CONFIRMED.search(rest) is None:
                add(
                    number,
                    f"row {item_id} passes without `confirmed by the user, <date>`",
                )
    missing = [i for i in expected if i not in found]
    extra = [i for i in found if i not in expected]
    if missing:
        add(start, f"{name}: missing rows for {', '.join(missing)}")
    if extra:
        add(start, f"{name}: unexpected rows {', '.join(extra)}")
    if not missing and not extra and found != list(expected):
        add(start, f"{name}: rows are not in checklist order")


QUOTED = re.compile(r'"[^"]*"')


def _fix_numbers(add: Adder, lines: Sequence[str]) -> int:
    """Fix numbers in order of first appearance; a draft's own words inside a
    quoted passage are not fixes. An `(fix N applied)` marker counts N as
    proposed but never triggers the order rule: a definition may skip the
    numbers that a marker covers. Returns the number of fixes proposed."""
    unquoted = [QUOTED.sub("", clean(raw)) for raw in lines]
    markers = {int(m.group(1)) for text in unquoted for m in APPLIED.finditer(text)}
    seen_max = 0
    for number, text in enumerate(unquoted, 1):
        for match in FIX.finditer(APPLIED.sub("", text)):
            value = int(match.group(1))
            missing = next(
                (n for n in range(seen_max + 1, value) if n not in markers), None
            )
            if missing is not None:
                add(
                    number,
                    f"fix {value} appears before fix {missing}; fixes are numbered in order of appearance",
                )
            else:
                seen_max = max(seen_max, value)
    return max(seen_max, max(markers, default=0))


def _lines_in(lines: Sequence[str], section: tuple[int, int]) -> list[str]:
    start, end = section
    return [clean(lines[number - 1]) for number in range(start + 1, end + 1)]


def check_review(path: Path, items: dict[str, Item]) -> list[Defect]:
    lines = path.read_text(encoding="utf-8").splitlines()
    defects: list[Defect] = []

    def add(line: int, message: str) -> None:
        defects.append(Defect(str(path), line, message))

    sections = sections_of(lines)
    names = [name for name, _, _ in sections]
    first = sections[0][1] if sections else 1
    header = header_of(lines, sections)
    for prefix in REVIEW_HEADER:
        if not any(line.startswith(prefix) for line in header):
            add(1, f"header: no `{prefix}` line")
    if names != list(REVIEW_SECTIONS):
        add(
            first,
            "sections must be Items, Cross-section consistency, Brief against draft, Substance tests, Summary, Waivers, Hand-off, in that order",
        )
    by_name = {name: (start, end) for name, start, end in sections}
    results: dict[str, str] = {}
    ordered = sorted(items, key=item_key)
    if "Items" in by_name:
        _review_rows(
            add,
            lines,
            items,
            by_name["Items"],
            "Items",
            [i for i in ordered if i not in SUBSTANCE],
            results,
        )
    if "Substance tests" in by_name:
        _review_rows(
            add,
            lines,
            items,
            by_name["Substance tests"],
            "Substance tests",
            [i for i in SUBSTANCE if i in items],
            results,
        )
    fixes = _fix_numbers(add, lines)
    findings = sum(
        1
        for name in ("Cross-section consistency", "Brief against draft")
        if name in by_name
        for line in _lines_in(lines, by_name[name])
        if line.lower().startswith("- fail")
    )
    waiver_lines = (
        [
            line
            for line in _lines_in(lines, by_name["Waivers"])
            if line.startswith("- ") and line.strip() != "- none"
        ]
        if "Waivers" in by_name
        else []
    )
    waivers = len(waiver_lines)
    waived_rows = {
        item_id for item_id, result in results.items() if result == "fail (waived)"
    }
    waived_entries = {
        m.group(1)
        for line in waiver_lines
        if (m := re.match(r"^- (\d{1,2}\.\d{1,2}) waived\b", line))
    }
    if "Waivers" in by_name:
        for item_id in sorted(waived_rows - waived_entries, key=item_key):
            add(
                by_name["Waivers"][0],
                f"row {item_id} is waived but has no Waivers entry",
            )
        for item_id in sorted(waived_entries - waived_rows, key=item_key):
            add(
                by_name["Waivers"][0],
                f"Waivers names {item_id}, whose row is not `fail (waived)`",
            )
    if "Summary" in by_name:
        start, end = by_name["Summary"]
        summary = next(
            (
                (number, m)
                for number in range(start + 1, end + 1)
                if (m := SUMMARY.match(clean(lines[number - 1])))
            ),
            None,
        )
        if summary is None:
            add(
                start,
                "Summary: no line of the shape `Items checked: N. Pass: N. Fail: N. Not checked (defend-stage): N. Consistency and brief findings: N. Fixes proposed: N. Waivers: N.`",
            )
        else:
            number, match = summary
            computed = (
                sum(1 for r in results.values() if r != "not checked"),
                sum(1 for r in results.values() if r in ("pass", "pass narrowly")),
                sum(1 for r in results.values() if r in ("fail", "fail (waived)")),
                sum(1 for r in results.values() if r == "not checked"),
                findings,
                fixes,
                waivers,
            )
            for label, expected_value, stated in zip(
                SUMMARY_LABELS, computed, match.groups(), strict=True
            ):
                if int(stated) != expected_value:
                    add(
                        number,
                        f"Summary: {label} says {stated}, the rows give {expected_value}",
                    )
    if "Hand-off" in by_name:
        text = "\n".join(_lines_in(lines, by_name["Hand-off"]))
        if DEFEND not in text and not all(command in text for command in INSTALL):
            add(
                by_name["Hand-off"][0],
                "Hand-off: neither the defend command nor both install commands are present",
            )
    return defects


def check_draft(
    path: Path,
    sections: Sequence[str],
    words: tuple[int, int],
    references: tuple[int, int],
    supervisor: str | None,
) -> list[Defect]:
    lines = path.read_text(encoding="utf-8").splitlines()
    defects: list[Defect] = []

    def add(line: int, message: str) -> None:
        defects.append(Defect(str(path), line, message))

    heads: list[tuple[str, int, int]] = []  # (text, line number, level)
    for number, raw in enumerate(lines, 1):
        match = HEADING.match(clean(raw))
        if match is not None:
            heads.append((clean(match.group(2)), number, len(match.group(1))))

    def block(index: int) -> tuple[int, int]:
        """A section runs to the next heading at its own level or higher, so a
        `###` subheading stays inside its `##` section."""
        start, level = heads[index][1], heads[index][2]
        end = len(lines)
        for _text, number, other_level in heads[index + 1 :]:
            if other_level <= level:
                end = number - 1
                break
        return start, end

    def find(prefix: str, from_index: int = 0) -> int | None:
        for index in range(from_index, len(heads)):
            if _matches(heads[index][0], prefix):
                return index
        return None

    position = 0
    previous = "the start"
    for name in sections:
        index = find(name, position)
        if index is None:
            add(
                heads[position - 1][1] if position else 1,
                f"sections: `{name}` not found after `{previous}`",
            )
        else:
            position = index + 1
            previous = name
    references_index = find("references")
    appendix_ranges = [
        block(i) for i, (text, _, _) in enumerate(heads) if _matches(text, "Appendix")
    ]
    body_end = (
        heads[references_index][1] - 1 if references_index is not None else len(lines)
    )

    def in_appendix(number: int) -> bool:
        return any(start <= number <= end for start, end in appendix_ranges)

    body = " ".join(
        clean(lines[n - 1]) for n in range(1, body_end + 1) if not in_appendix(n)
    )
    count = len(body.split())
    if not words[0] <= count <= words[1]:
        add(
            1,
            f"words: the body has {count} words; the template asks for {words[0]} to {words[1]}",
        )
    if references_index is None:
        add(1, "references: no `References` heading")
    else:
        start, end = block(references_index)
        entry_lines = [clean(lines[n - 1]) for n in range(start + 1, end + 1)]
        listed = [line for line in entry_lines if LIST_ITEM.match(line)]
        if listed:
            found_refs = len(listed)
        else:
            found_refs = sum(
                1 for para in "\n".join(entry_lines).split("\n\n") if para.strip()
            )
        if not references[0] <= found_refs <= references[1]:
            add(
                heads[references_index][1],
                f"references: {found_refs} entries; the template asks for {references[0]} to {references[1]}",
            )
    intro = find("introduction")
    if intro is not None:
        start, end = block(intro)
        if not any(
            clean(lines[n - 1]).startswith(("- ", "* "))
            for n in range(start + 1, end + 1)
        ):
            add(start, "introduction: no bullet list of contributions")
    appendix_text = re.sub(
        r"\s+",
        " ",
        "\n".join(
            clean(lines[n - 1])
            for start, end in appendix_ranges
            for n in range(start, end + 1)
        ),
    )
    match = SUPERVISION.search(appendix_text)
    if match is None:
        add(
            1,
            "appendix: no consent sentence saying the study is under the supervision of the instructor",
        )
    elif supervisor and supervisor.lower() not in match.group(1).lower():
        add(
            1,
            f"appendix: the supervision sentence names {match.group(1).strip()!r}, not {supervisor!r}",
        )
    return defects


DEFAULT_SECTIONS = (
    "Introduction",
    "Literature review",
    "Research questions or Hypotheses",
    "Participants",
    "Materials",
    "Procedure",
    "Design",
    "Appendix",
)


def parse_range(text: str) -> tuple[int, int]:
    low, high = text.split("-", 1)
    return int(low), int(high)


def main(argv: Sequence[str] | None = None) -> int:
    # The script runs standalone on whatever python3 the user has, below the repo floor.
    if sys.version_info < (3, 11):  # noqa: UP036
        print("check_proposal.py needs Python 3.11 or later", file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--json", action="store_true", help="print the defects as a JSON list"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("brief", "review"):
        commands.add_parser(name).add_argument("path")
    draft = commands.add_parser("draft")
    draft.add_argument("path")
    draft.add_argument("--sections", default=", ".join(DEFAULT_SECTIONS))
    draft.add_argument("--words", default="2000-4000")
    draft.add_argument("--references", default="15-20")
    draft.add_argument("--supervisor")
    args = parser.parse_args(argv)
    path = Path(args.path)
    try:
        path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        print(f"{path}: cannot read: {error}", file=sys.stderr)
        return 2
    try:
        items = read_checklist() if args.command != "draft" else {}
    except (OSError, ValueError) as error:
        print(
            f"{CHECKLIST}: the plugin's checklist is unreadable: {error}",
            file=sys.stderr,
        )
        return 2
    if args.command == "brief":
        defects = check_brief(path, items)
    elif args.command == "review":
        defects = check_review(path, items)
    else:
        try:
            words, references = parse_range(args.words), parse_range(args.references)
        except ValueError:
            parser.error(
                "--words and --references take two integers as LOW-HIGH, for example 2000-4000"
            )
        defects = check_draft(
            path,
            tuple(s.strip() for s in args.sections.split(",")),
            words,
            references,
            args.supervisor,
        )
    if args.json:
        print(json.dumps([asdict(d) for d in defects], indent=2))
    else:
        for defect in defects:
            print(defect.render())
    return 1 if defects else 0


if __name__ == "__main__":
    raise SystemExit(main())
