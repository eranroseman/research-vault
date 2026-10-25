#!/usr/bin/env python3
"""Check the shapes of the experiment-proposal plugin's files.

Usage:
    check_proposal.py [--json] brief proposal/design-brief.md
    check_proposal.py [--json] review proposal/review.md
    check_proposal.py [--json] draft proposal/draft.md [--sections "A, B, ..."]
        [--words 2000-4000] [--references 15-20] [--review-section "<heading>"]
        [--supervisor "<name>"]
    check_proposal.py [--json] draft proposal/draft.md --numbers
    check_proposal.py [--json] draft proposal/draft.md --placeholders [--placeholder-list "<heading>"]

Exit 0: clean. Exit 1: defects, one per line as `<file>:<line>: <message>`
(a JSON list with --json). Exit 2: a file could not be read, the arguments
were malformed, or the interpreter is older than 3.11.

The two reports judge nothing, skip the mechanics and exit 0; --json gives
{"numbers": [...]} and
{"placeholders": [...], "unlisted": [...], "unused": [...]}.

--references bounds the citations in the section --review-section names
(default "Literature review"): a [n] list by the numbers cited there, any
other list by each entry's first surname and year; the list's total is a
stderr line.

The review header may carry a fifth line, Checker: draft <options>, the
option set the pass ran, checked as such; an optional ## Judged section
follows Items; not confirmed is a result of the four attested items only
and counts under Fail.

Each defect line ends ` [<rule>; item <ID>]`, the rule a short slug and the
ID the checklist item that owns it (`none` for a shape rule); --json carries
them as the keys rule and item. Informational lines go to stderr and never
into --json.

This script is the single source of truth for the three shapes. The files
references/brief.md and references/review.md describe the same shapes in
prose for the skills that write them. The item set comes from the checklist
beside this script, so no item is duplicated here.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence

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
CHECKER_LINE = "Checker:"
JUDGED = "Judged"
ATTESTED_RESULT = "not confirmed"
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
RESULTS = (
    "pass narrowly",
    "pass",
    "fail (waived)",
    "fail",
    "not confirmed",
    "not checked",
)
FAILING = ("fail", "fail (waived)", "not confirmed")
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
LIST_ITEM = re.compile(r"^(?:[-*] |\d+\. |\[\d+\] )")
NUMBERED_ENTRY = re.compile(r"^\[(\d+)\] ")
CITATION = re.compile(r"\[(\d+(?:\s*[,\u2013-]\s*\d+)*)\]")
RANGE = re.compile(r"^(\d+)\s*[\u2013-]\s*(\d+)$")
RANGE_MAX = 200  # `[1-999]` is a typo, not nine hundred entries
YEAR = re.compile(r"\b(?:19|20)\d{2}[a-z]?\b")
SURNAME = re.compile(r"^\s*([^,(]+?)\s*(?:,|\()")
DEFAULT_REVIEW_SECTION = "Literature review"
SUPERVISION = re.compile(
    r"under\s+the\s+supervision\s+of\s+([^\n]{1,60})", re.IGNORECASE
)
NUMBERING = re.compile(r"^\d+(?:\.\d+)*\.?\s*")
PLACEHOLDER = re.compile(r"\[[A-Z][A-Z0-9 _-]*\]|\bTODO\b|\bTBD\b")
INLINE_CODE = re.compile(r"`[^`]*`")
HEADING_NUMBER = re.compile(r"^(#{1,6} )((?:\d+|[A-Z])(?:\.\d+)*\.?\s*)")
MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?")
PERCENT = re.compile(r"\d[\d,]*(?:\.\d+)?\s?%")
INTEGER = re.compile(
    r"(?<![\w.,])\d{1,3}(?:,\d{3})+(?!\w|[.,]\d)|(?<![\w.,])\d+(?!\w|[.,]\d)"
)
NUMBERS_YEAR = (1900, 2099)
WINDOW = 6  # words either side of a reported number


def _norm(text: str) -> str:
    """A heading as a key: numbering stripped, lower case, letters and digits."""
    return re.sub(r"[^a-z0-9 ]+", " ", NUMBERING.sub("", text.strip()).lower()).strip()


def _singular(text: str) -> str:
    """Each word of a normalised heading without a trailing `es`, else `s`,
    else `e` (never below one letter), so `questions` and `question` meet at
    `question` and `procedures` and `procedure` at `procedur`."""
    return " ".join(re.sub(r"(?<=.)(?:es|s|e)$", "", word) for word in text.split())


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
    rule: str  # a short slug naming the rule the line breaks
    item: str | None  # the checklist item that owns the rule; None for a shape rule

    def render(self) -> str:
        owner = "none" if self.item is None else self.item
        return f"{self.path}:{self.line}: {self.message} [{self.rule}; item {owner}]"


class Adder(Protocol):
    def __call__(
        self, line: int, message: str, rule: str, item: str | None = None
    ) -> None: ...


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
    add: Adder,
    body: Iterable[tuple[int, str]],
    labels: Sequence[str],
    where: str,
    rules: tuple[str, str],
    item: str | None,
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
                rules[0],
                item,
            )
    expected = [f"- {label}:" for label in labels]
    found = [line.split(":", 1)[0] + ":" for _, line in dashes]
    if found != expected:
        at = dashes[0][0] if dashes else (body[0][0] if body else 0)
        add(
            at,
            f"{where}: lines must be exactly {', '.join(expected)} in that order; found {', '.join(found) or 'none'}",
            rules[1],
            item,
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
        add(1, "header: no `Draft: <path>` line", "header-draft")
    status = next((m for line in header if (m := HEADER_STATUS.match(line))), None)
    if status is None:
        add(
            1,
            "header: no `Status: open` or `Status: frozen YYYY-MM-DD` line",
            "header-status",
        )
    if not any(HEADER_VERSION.match(line) for line in header):
        add(
            1,
            "header: no `Checklist: experiment-proposal <version>` line",
            "header-version",
        )
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
            add(
                number,
                f"entry heading must be `### <ID> <title>`: {heading[:60]}",
                "entry-heading",
            )
            continue
        item_id = match.group(1)
        if item_id not in design_tree:
            add(
                number,
                f"entry {item_id} is not a design-tree item",
                "entry-not-design-tree",
                item_id,
            )
        if item_id in entries:
            add(number, f"entry {item_id} appears twice", "entry-duplicate", item_id)
        values = labelled_lines(
            add,
            body,
            ENTRY_LINES,
            f"entry {item_id}",
            ("entry-extra-line", "entry-lines"),
            item_id,
        )
        for label in ENTRY_LINES:
            if label in values and not values[label][1]:
                add(
                    values[label][0],
                    f"entry {item_id}: {label} is empty",
                    "entry-empty",
                    item_id,
                )
        status_line, status_value = values.get("Status", (number, ""))
        if status_value not in STATUSES:
            add(
                status_line,
                f"entry {item_id}: Status must be settled, pilot settles or provisional; found {status_value!r}",
                "entry-status",
                item_id,
            )
        if "Decision" in values:
            decision_line, decision = values["Decision"]
            length = len("- Decision: " + decision)
            if length > DECISION_MAX:
                add(
                    decision_line,
                    f"entry {item_id}: Decision line is {length} characters; at most {DECISION_MAX}",
                    "decision-length",
                    item_id,
                )
        entries[item_id] = status_value
    if list(entries) != sorted(entries, key=item_key):
        add(start, "entries are not in checklist order", "entry-order")
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
            add(
                number,
                "Open items: provisional items come before the commands",
                "open-order",
                item_id,
            )
        if item_id not in entries:
            add(
                number,
                f"Open items names item {item_id}, which has no entry",
                "open-no-entry",
                item_id,
            )
        elif entries[item_id] != "provisional":
            add(
                number,
                f"Open items names item {item_id}, whose entry is {entries[item_id]}, not provisional",
                "open-not-provisional",
                item_id,
            )
    for item_id, entry_status in entries.items():
        if entry_status == "provisional" and item_id not in referenced:
            add(
                start,
                f"entry {item_id} is provisional but not listed under Open items",
                "open-missing",
                item_id,
            )


def amendment_defects(add: Adder, lines: Sequence[str], span: tuple[int, int]) -> None:
    """`## Amendments`: each block a dated heading and the three labelled lines."""
    start, end = span
    for number, heading, body in blocks_of(lines, start, end):
        if AMENDMENT.match("### " + heading) is None:
            add(
                number,
                f"amendment heading must be `### YYYY-MM-DD, item <ID>, <title>`: {heading[:60]}",
                "amendment-heading",
            )
        labelled_lines(
            add,
            body,
            AMENDMENT_LINES,
            f"amendment at line {number}",
            ("amendment-extra-line", "amendment-lines"),
            None,
        )


def check_brief(path: Path, items: dict[str, Item]) -> list[Defect]:
    lines = path.read_text(encoding="utf-8").splitlines()
    defects: list[Defect] = []

    def add(line: int, message: str, rule: str, item: str | None = None) -> None:
        defects.append(Defect(str(path), line, message, rule, item))

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
                "section-unknown",
            )
    if [n for n in names if n in BRIEF_SECTIONS] != list(BRIEF_SECTIONS):
        add(
            first,
            "sections must be Decisions, Looked up, Open items, in that order (Amendments optional, last)",
            "section-order",
        )
    if "Amendments" in names and names[-1] != "Amendments":
        add(
            sections[names.index("Amendments")][1],
            "Amendments must be the last section",
            "amendments-last",
        )
    design_tree = {i for i, it in items.items() if it.scope == "design-tree"}
    entries: dict[str, str] = {}
    if "Decisions" in by_name:
        entries = decisions_of(add, lines, by_name["Decisions"], design_tree)
    if "Open items" in by_name:
        open_items_defects(add, lines, by_name["Open items"], entries)
    if frozen:
        for item_id in sorted(design_tree - set(entries), key=item_key):
            add(
                1,
                f"frozen brief has no entry for design-tree item {item_id}",
                "frozen-missing",
                item_id,
            )
    if "Amendments" in by_name:
        amendment_defects(add, lines, by_name["Amendments"])
    return defects


QUOTED = re.compile(r'"[^"]*"')


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
                "row-shape",
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
            add(number, f"row {item_id} is not a checklist item", "row-not-item")
            continue
        results[item_id] = result
        if item.kind == "defend-stage" and result != "not checked":
            add(
                number,
                f"row {item_id} is a defend-stage item and must read `not checked`",
                "row-defend",
                item_id,
            )
        if item.kind != "defend-stage" and result == "not checked":
            add(
                number,
                f"row {item_id} reads `not checked`; only items 13.2 and 13.3 may",
                "row-not-checked",
                item_id,
            )
        if result == ATTESTED_RESULT and item.kind != "attested":
            add(
                number,
                f"row {item_id}: attested result on a draft-checked item",
                "row-attested",
                item_id,
            )
        if result in ("pass", "pass narrowly"):
            if item.kind == "draft-checked" and QUOTE.search(rest) is None:
                add(
                    number,
                    f"row {item_id} passes without a quoted passage and its location",
                    "row-quote",
                    item_id,
                )
            if item.kind == "attested" and CONFIRMED.search(rest) is None:
                add(
                    number,
                    f"row {item_id} passes without `confirmed by the user, <date>`",
                    "row-confirmed",
                    item_id,
                )
            for quoted in QUOTED.findall(rest):
                placeholder = PLACEHOLDER.search(quoted)
                if placeholder is not None:
                    add(
                        number,
                        f"row {item_id} passes on a placeholder: {placeholder.group(0)}",
                        "pass-placeholder",
                        item_id,
                    )
                    break
    missing = [i for i in expected if i not in found]
    extra = [i for i in found if i not in expected]
    if missing:
        add(start, f"{name}: missing rows for {', '.join(missing)}", "rows-missing")
    if extra:
        add(start, f"{name}: unexpected rows {', '.join(extra)}", "rows-extra")
    if not missing and not extra and found != list(expected):
        add(start, f"{name}: rows are not in checklist order", "rows-order")


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
                    "fix-order",
                )
            else:
                seen_max = max(seen_max, value)
    return max(seen_max, max(markers, default=0))


def _lines_in(lines: Sequence[str], section: tuple[int, int]) -> list[str]:
    start, end = section
    return [clean(lines[number - 1]) for number in range(start + 1, end + 1)]


class _OptionError(ValueError):
    """argparse's error, raised instead of exiting, for the Checker line."""


class _QuietParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise _OptionError(message)


def checker_line_defect(line: str) -> str | None:
    """Why a `Checker:` header line is not a `draft` option set, or None."""
    try:
        tokens = shlex.split(line[len(CHECKER_LINE) :])
    except ValueError as exc:
        return f"unbalanced quotes ({exc})"
    if not tokens or tokens[0] != "draft":
        return "must begin `Checker: draft`"
    parser = _QuietParser(add_help=False, allow_abbrev=False)
    add_draft_options(parser)
    try:
        args, extra = parser.parse_known_args(tokens[1:])
    except _OptionError as exc:
        return str(exc)
    if extra:
        return f"unknown option(s): {' '.join(extra)}"
    given = {token.split("=", 1)[0] for token in tokens[1:] if token.startswith("--")}
    missing = [option for option in ("--words", "--references") if option not in given]
    if missing:
        return "missing " + " and ".join(missing)
    try:
        parse_range(args.words)
        parse_range(args.references)
    except ValueError:
        return "--words and --references take LOW-HIGH"
    return None


def check_review(path: Path, items: dict[str, Item]) -> list[Defect]:
    lines = path.read_text(encoding="utf-8").splitlines()
    defects: list[Defect] = []

    def add(line: int, message: str, rule: str, item: str | None = None) -> None:
        defects.append(Defect(str(path), line, message, rule, item))

    sections = sections_of(lines)
    names = [name for name, _, _ in sections]
    first = sections[0][1] if sections else 1
    header = header_of(lines, sections)
    for prefix in REVIEW_HEADER:
        if not any(line.startswith(prefix) for line in header):
            add(1, f"header: no `{prefix}` line", "header-line")
    for line in header:
        if line.startswith(CHECKER_LINE) and (why := checker_line_defect(line)):
            add(
                1,
                f"header: Checker line is not a draft option set: {why}",
                "checker-line",
                "3.1",
            )
    expected_sections = list(REVIEW_SECTIONS)
    if JUDGED in names:
        expected_sections.insert(1, JUDGED)
    if names != expected_sections:
        add(
            first,
            "sections must be Items, Cross-section consistency, Brief against draft, Substance tests, Summary, Waivers, Hand-off, in that order (Judged, optional, after Items)",
            "sections",
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
                "waiver-entry",
                item_id,
            )
        for item_id in sorted(waived_entries - waived_rows, key=item_key):
            add(
                by_name["Waivers"][0],
                f"Waivers names {item_id}, whose row is not `fail (waived)`",
                "waiver-row",
                item_id,
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
                "summary-shape",
            )
        else:
            number, match = summary
            computed = (
                sum(1 for r in results.values() if r != "not checked"),
                sum(1 for r in results.values() if r in ("pass", "pass narrowly")),
                sum(1 for r in results.values() if r in FAILING),
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
                        "summary-count",
                    )
    if "Hand-off" in by_name:
        text = "\n".join(_lines_in(lines, by_name["Hand-off"]))
        if DEFEND not in text and not all(command in text for command in INSTALL):
            add(
                by_name["Hand-off"][0],
                "Hand-off: neither the defend command nor both install commands are present",
                "handoff",
            )
    return defects


def cited_numbers(text: str) -> set[int]:
    """Every entry number a `[n]`, `[n, m]` or `[n-m]` citation in the text names."""
    numbers: set[int] = set()
    for match in CITATION.finditer(text):
        for part in re.split(r"\s*,\s*", match.group(1)):
            span = RANGE.match(part)
            if span is not None:
                low, high = int(span.group(1)), int(span.group(2))
                numbers.update(range(low, min(high, low + RANGE_MAX) + 1))
            elif part.isdecimal():
                numbers.add(int(part))
    return numbers


def first_surname(entry: str) -> str | None:
    """An author-year entry's first surname: the text after the list marker up
    to the first comma or opening parenthesis, so `Card, S. K., English, ...`
    gives `Card` and `ISO (2000).` gives `ISO`."""
    match = SURNAME.match(LIST_ITEM.sub("", entry, count=1))
    return match.group(1) if match else None


def year_of(entry: str) -> str | None:
    match = YEAR.search(entry)
    return match.group(0) if match else None


def mentions(text: str, token: str) -> bool:
    """`token` occurs in `text` as a whole token."""
    return re.search(rf"(?<!\w){re.escape(token)}(?!\w)", text) is not None


def _listed_entries(entry_lines: Sequence[str]) -> list[str]:
    """One string per list-marker line, joined with a space to the lines that
    continue it up to the next marker or blank line, so a hard-wrapped entry
    keeps a year that landed on its continuation line."""
    listed: list[str] = []
    continues = False
    for line in entry_lines:
        if LIST_ITEM.match(line):
            listed.append(line)
            continues = True
        elif not line.strip():
            continues = False
        elif continues:
            listed[-1] += " " + line.strip()
    return listed


def _count_numbered(
    add: Adder,
    lines: Sequence[str],
    body_end: int,
    in_appendix: Callable[[int], bool],
    listed: Sequence[str],
    section_text: str,
    body_text: str,
) -> int:
    """`[n]` mode: the entries the section cites; a body citation with no
    entry is a defect under item 3.3; an entry cited nowhere is informational."""
    numbers = {int(m.group(1)) for line in listed if (m := NUMBERED_ENTRY.match(line))}
    for n in range(1, body_end + 1):
        if in_appendix(n):
            continue
        for number in sorted(cited_numbers(clean(lines[n - 1])) - numbers):
            add(
                n,
                f"references: [{number}] is cited but has no entry in the list",
                "citation-no-entry",
                "3.3",
            )
    for number in sorted(numbers - cited_numbers(body_text)):
        print(f"references: entry [{number}] is not cited", file=sys.stderr)
    return len(cited_numbers(section_text) & numbers)


def _count_author_year(
    entries: Sequence[str], section_text: str, body_text: str
) -> int:
    """Author-year mode: an entry is cited where its first surname and its
    year both occur; no cited-without-entry defect, since a surname in prose
    is no citation the checker can prove."""
    cited = 0
    for entry in entries:
        surname, year = first_surname(entry), year_of(entry)
        if surname is None or year is None:
            print(
                f"references: entry without a surname and year: {entry[:60]}",
                file=sys.stderr,
            )
            continue
        if mentions(section_text, surname) and mentions(section_text, year):
            cited += 1
        elif not (mentions(body_text, surname) and mentions(body_text, year)):
            print(f"references: entry {surname} ({year}) is not cited", file=sys.stderr)
    return cited


def check_draft(
    path: Path,
    sections: Sequence[str],
    words: tuple[int, int],
    references: tuple[int, int],
    supervisor: str | None,
    review_section: str,
) -> list[Defect]:
    lines = path.read_text(encoding="utf-8").splitlines()
    defects: list[Defect] = []

    def add(line: int, message: str, rule: str, item: str | None = None) -> None:
        defects.append(Defect(str(path), line, message, rule, item))

    heads = _headings(lines)

    def block(index: int) -> tuple[int, int]:
        return _block_of(heads, index, len(lines))

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
                "sections",
                "3.2",
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
            "words",
            "13.5",
        )
    if references_index is None:
        add(1, "references: no `References` heading", "references-heading", "5.1")
    else:
        start, end = block(references_index)
        entry_lines = [clean(lines[n - 1]) for n in range(start + 1, end + 1)]
        listed = _listed_entries(entry_lines)
        entries = listed or [
            para for para in "\n".join(entry_lines).split("\n\n") if para.strip()
        ]
        print(f"references: {len(entries)} entries in the list", file=sys.stderr)
        review_index = find(review_section)
        if review_index is None:
            add(
                1,
                f"references: no `{review_section}` section to count citations in",
                "references-section",
                "5.1",
            )
        else:
            r_start, r_end = block(review_index)
            section_text = " ".join(
                clean(lines[n - 1]) for n in range(r_start + 1, r_end + 1)
            )
            if listed and all(NUMBERED_ENTRY.match(line) for line in listed):
                cited = _count_numbered(
                    add, lines, body_end, in_appendix, listed, section_text, body
                )
            else:
                cited = _count_author_year(entries, section_text, body)
            if not references[0] <= cited <= references[1]:
                add(
                    heads[references_index][1],
                    f"references: the {review_section} cites {cited} of the list's "
                    f"{len(entries)} entries; the template asks for "
                    f"{references[0]} to {references[1]}",
                    "references-count",
                    "5.1",
                )
    intro = find("introduction")
    if intro is not None:
        start, end = block(intro)
        if not any(
            clean(lines[n - 1]).startswith(("- ", "* "))
            for n in range(start + 1, end + 1)
        ):
            add(
                start,
                "introduction: no bullet list of contributions",
                "contributions",
                "4.3",
            )
    consent_blocks = [
        block(i)
        for i, (text, number, _) in enumerate(heads)
        if "consent" in text.lower() and in_appendix(number)
    ]
    searched = consent_blocks or appendix_ranges
    appendix_text = re.sub(
        r"\s+",
        " ",
        "\n".join(
            clean(lines[n - 1])
            for start, end in searched
            for n in range(start, end + 1)
        ),
    )
    match = SUPERVISION.search(appendix_text)
    if match is None:
        add(
            1,
            "appendix: no consent sentence saying the study is under the supervision of the instructor",
            "supervision",
            "12.3",
        )
    else:
        if not consent_blocks:
            print(
                "supervision sentence found outside a consent-headed appendix",
                file=sys.stderr,
            )
        if supervisor and supervisor.lower() not in match.group(1).lower():
            add(
                1,
                f"appendix: the supervision sentence names {match.group(1).strip()!r}, not {supervisor!r}",
                "supervisor-name",
                "12.3",
            )
    return defects


def _headings(lines: Sequence[str]) -> list[tuple[str, int, int]]:
    """(text, line number, level) of every heading, numbering as written."""
    return [
        (clean(m.group(2)), number, len(m.group(1)))
        for number, raw in enumerate(lines, 1)
        if (m := HEADING.match(clean(raw)))
    ]


def _block_of(
    heads: Sequence[tuple[str, int, int]], index: int, last: int
) -> tuple[int, int]:
    """A section runs to the next heading at its own level or higher, so a
    `###` subheading stays inside its `##` section."""
    start, level = heads[index][1], heads[index][2]
    for _text, number, other_level in heads[index + 1 :]:
        if other_level <= level:
            return start, number - 1
    return start, last


def _heading_of(heads: Sequence[tuple[str, int, int]], line: int) -> str:
    text = "(no heading)"
    for heading, number, _ in heads:
        if number > line:
            break
        text = heading
    return text


def _blank(text: str, pattern: re.Pattern[str]) -> str:
    """The text with every match replaced by spaces, so offsets stay put."""
    return pattern.sub(lambda m: " " * len(m.group(0)), text)


def _window(text: str, start: int, end: int) -> str:
    before = text[:start].split()[-WINDOW:]
    after = text[end:].split()[:WINDOW]
    return " ".join([*before, text[start:end], *after])


def numbers_report(lines: Sequence[str]) -> list[dict]:
    """Every money and percent figure, and every non-year integer of two or
    more digits that occurs twice or more, outside the References section,
    grouped by value in order of first occurrence, each occurrence with its
    heading, line and the six words either side. Citation brackets, inline
    code and a heading's own number are blanked first."""
    heads = _headings(lines)
    skip: tuple[int, int] = (0, -1)
    for index, (text, _, _) in enumerate(heads):
        if _matches(text, "references"):
            skip = _block_of(heads, index, len(lines))
            break
    groups: dict[str, list[dict]] = {}
    always: set[str] = set()

    def record(value: str, number: int, line: str, start: int, end: int) -> None:
        groups.setdefault(value, []).append(
            {
                "heading": _heading_of(heads, number),
                "line": number,
                "text": _window(line, start, end),
            }
        )

    for number, raw in enumerate(lines, 1):
        if skip[0] <= number <= skip[1]:
            continue
        line = clean(raw)
        masked = _blank(_blank(line, CITATION), INLINE_CODE)
        heading = HEADING_NUMBER.match(masked)
        if heading is not None:
            masked = (
                masked[: heading.start(2)]
                + " " * len(heading.group(2))
                + masked[heading.end(2) :]
            )
        hits: list[tuple[int, int, str]] = []  # recorded in line order, not by pattern
        for pattern, suffix in ((MONEY, ""), (PERCENT, "%")):
            for m in pattern.finditer(masked):
                digits = re.sub(r"[\s,%$]", "", m.group(0))
                value = ("$" if pattern is MONEY else "") + digits + suffix
                always.add(value)
                hits.append((m.start(), m.end(), value))
            masked = _blank(masked, pattern)
        for m in INTEGER.finditer(masked):
            digits = m.group(0).replace(",", "")
            if len(digits) < 2:
                continue
            if (
                "," not in m.group(0)
                and len(digits) == 4
                and NUMBERS_YEAR[0] <= int(digits) <= NUMBERS_YEAR[1]
            ):
                continue
            hits.append((m.start(), m.end(), digits))
        for start, end, value in sorted(hits):
            record(value, number, line, start, end)
    return [
        {"value": value, "locations": locations}
        for value, locations in groups.items()
        if value in always or len(locations) >= 2
    ]


def render_numbers(report: Sequence[dict]) -> list[str]:
    out: list[str] = []
    for group in report:
        out.append(f"{group['value']}: {len(group['locations'])} occurrences")
        out.extend(
            f"  {loc['heading']} (line {loc['line']}): {loc['text']}"
            for loc in group["locations"]
        )
    return out


def placeholders_report(lines: Sequence[str], list_heading: str | None) -> dict:
    """Every placeholder with its heading and line; with a list heading, the
    placeholders used outside that block and not listed in it, and the
    reverse."""
    heads = _headings(lines)
    listing: tuple[int, int] | None = None
    if list_heading is not None:
        for index, (text, _, _) in enumerate(heads):
            if _matches(text, list_heading):
                listing = _block_of(heads, index, len(lines))
                break
        if listing is None:
            print(
                f"placeholder list heading `{list_heading}` not found", file=sys.stderr
            )
    occurrences: list[dict] = []
    used: set[str] = set()
    listed: set[str] = set()
    for number, raw in enumerate(lines, 1):
        line = clean(raw)
        for m in PLACEHOLDER.finditer(line):
            occurrences.append(
                {
                    "text": m.group(0),
                    "heading": _heading_of(heads, number),
                    "line": number,
                }
            )
            in_listing = listing is not None and listing[0] <= number <= listing[1]
            (listed if in_listing else used).add(m.group(0))
    if list_heading is None:
        return {"placeholders": occurrences, "unlisted": [], "unused": []}
    return {
        "placeholders": occurrences,
        "unlisted": sorted(used - listed),
        "unused": sorted(listed - used),
    }


def render_placeholders(report: dict, listed: bool) -> list[str]:
    out = [
        f"{p['text']}: {p['heading']} (line {p['line']})"
        for p in report["placeholders"]
    ]
    if listed:
        out.append("used but not listed: " + (", ".join(report["unlisted"]) or "none"))
        out.append("listed but unused: " + (", ".join(report["unused"]) or "none"))
    return out


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


def add_draft_options(parser: argparse.ArgumentParser) -> None:
    """The `draft` options a review's `Checker:` line may carry."""
    parser.add_argument("--sections", default=", ".join(DEFAULT_SECTIONS))
    parser.add_argument("--words", default="2000-4000")
    parser.add_argument("--references", default="15-20")
    parser.add_argument("--review-section", default=DEFAULT_REVIEW_SECTION)
    parser.add_argument("--supervisor")


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
    add_draft_options(draft)
    reports = draft.add_mutually_exclusive_group()
    reports.add_argument(
        "--numbers", action="store_true", help="report repeated numbers; judges nothing"
    )
    reports.add_argument(
        "--placeholders",
        action="store_true",
        help="report placeholders; judges nothing",
    )
    draft.add_argument(
        "--placeholder-list", help="the heading of the draft's own placeholder list"
    )
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
    elif args.numbers or args.placeholders:
        lines = path.read_text(encoding="utf-8").splitlines()
        if args.numbers:
            numbers = numbers_report(lines)
            text = (
                json.dumps({"numbers": numbers}, indent=2, ensure_ascii=False)
                if args.json
                else "\n".join(render_numbers(numbers))
            )
        else:
            report = placeholders_report(lines, args.placeholder_list)
            text = (
                json.dumps(report, indent=2, ensure_ascii=False)
                if args.json
                else "\n".join(
                    render_placeholders(report, args.placeholder_list is not None)
                )
            )
        print(text)
        return 0
    else:
        try:
            words, references = parse_range(args.words), parse_range(args.references)
        except ValueError:
            parser.error(
                "--words and --references take two integers as LOW-HIGH, for example 2000-4000"
            )
        defects = check_draft(
            path,
            tuple(s.strip() for s in args.sections.split(",") if s.strip()),
            words,
            references,
            args.supervisor,
            args.review_section,
        )
    if args.json:
        print(json.dumps([asdict(d) for d in defects], indent=2))
    else:
        for defect in defects:
            print(defect.render())
    return 1 if defects else 0


if __name__ == "__main__":
    raise SystemExit(main())
