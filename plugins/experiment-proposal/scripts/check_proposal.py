#!/usr/bin/env python3
"""Check the shapes of the experiment-proposal plugin's files.

Usage:
    check_proposal.py [--json] brief proposal/design-brief.md
    check_proposal.py [--json] review proposal/review.md
    check_proposal.py [--json] draft proposal/draft.md [--sections "A, B, ..."]
        [--words 2000-4000] [--references 15-20] [--supervisor "<name>"]

Exit 0: clean. Exit 1: defects, one per line as `<file>:<line>: <message>`
(a JSON list with --json). Exit 2: a file could not be read.

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
    status = header_defects(add, header_of(lines, sections))
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
    by_name = {name: (start, end) for name, start, end in sections}
    design_tree = {i for i, it in items.items() if it.scope == "design-tree"}
    entries: dict[str, str] = {}
    if "Decisions" in by_name:
        entries = decisions_of(add, lines, by_name["Decisions"], design_tree)
    if "Open items" in by_name:
        open_items_defects(add, lines, by_name["Open items"], entries)
    if status is not None and status.group(1).startswith("frozen"):
        for item_id in sorted(design_tree - set(entries), key=item_key):
            add(1, f"frozen brief has no entry for design-tree item {item_id}")
    if "Amendments" in by_name:
        amendment_defects(add, lines, by_name["Amendments"])
    return defects


def check_review(
    path: Path,
    items: dict[str, Item],  # noqa: ARG001 -- stub; Task 3 replaces it
) -> list[Defect]:
    return [Defect(str(path), 0, "review: not implemented yet")]


def check_draft(
    path: Path,
    sections: Sequence[str],  # noqa: ARG001 -- stub; Task 4 replaces it
    words: tuple[int, int],  # noqa: ARG001
    references: tuple[int, int],  # noqa: ARG001
    supervisor: str | None,  # noqa: ARG001
) -> list[Defect]:
    return [Defect(str(path), 0, "draft: not implemented yet")]


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
        defects = check_draft(
            path,
            tuple(s.strip() for s in args.sections.split(",")),
            parse_range(args.words),
            parse_range(args.references),
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
