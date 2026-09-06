"""The §10 status-marking pass: scope, read, propose, and apply the Disposition line.

Repo maintenance, not product. Deliberately not a `research_vault` module and not
a CLI verb: §11 dispositions every verb against the step map, and a maintenance
verb would serve none of them.
"""

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]

# Excluded from marking, each for its own reason:
#   research_vault/templates/** ships into a user's vault — a repo-internal
#     marker has no business travelling with the product;
#   .out-of-scope/** declares its disposition by path;
#   skills/find-sources/references/** are 11 vendored upstream files whose own
#     header reads "Do not hand-edit this file; re-vendor from upstream"; their
#     disposition belongs to the vendoring decision in find-sources/SKILL.md,
#     which is repo-owned and marked. Same reasoning .pre-commit-config.yaml
#     already applies to their sibling scripts/*.py;
#   CLAUDE.md is an 11-byte import directive, not a document (spec §10).
EXCLUDED_PREFIXES = (
    "research_vault/templates/",
    ".out-of-scope/",
    "skills/find-sources/references/",
)
EXCLUDED_PATHS = frozenset({"CLAUDE.md"})

WINDOW = 5

DOCUMENT_VALUES = (
    "sibling-project",
    "superseded-by",
    "pending-issue",
    "historical",
    "pending-map",
    "current",
)
ARGUMENT_VALUES = frozenset({"superseded-by", "pending-issue"})
FLAG = "should-be-scoping-review"

_HEADING = re.compile(r"^#{1,6} ")

_MARKER = re.compile(
    r"^Disposition: (?P<value>[a-z-]+)(?:: (?P<argument>\S+))?"
    r" \((?P<date>\d{4}-\d{2}-\d{2})\)(?P<flag> \[" + FLAG + r"\])?$"
)


class MarkerError(ValueError):
    """A Disposition line that exists but does not parse, or parses off-vocabulary."""


class Marker(NamedTuple):
    value: str
    argument: str
    date: str
    flag: bool


def in_scope(root: Path = ROOT) -> list[str]:
    """Every tracked Markdown file this pass marks, repo-relative and sorted."""
    listing = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--", "*.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split("\n")
    return sorted(
        path
        for path in listing
        if path
        and path not in EXCLUDED_PATHS
        and not path.startswith(EXCLUDED_PREFIXES)
    )


def anchor(lines: list[str]) -> int:
    """The index the marker window opens at: after the first heading, else 0.

    Any level (spec §10): 21 in-scope files open at `###`, and only the four
    bare-prose `docs/research/**/README.md` files carry no heading at all.
    Fence-aware — a `# ` inside a fenced block is a shell comment, not a
    heading. No file in scope trips that today; new documents arrive without
    asking.
    """
    fenced = False
    for index, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if not fenced and _HEADING.match(line):
            return index + 1
    return 0


def read_marker(text: str) -> Marker | None:
    """The document's marker, or None when it carries none. Raises on malformed."""
    lines = text.split("\n")
    start = anchor(lines)
    found = [
        line
        for line in lines[start : start + WINDOW]
        if line.startswith("Disposition: ")
    ]
    if not found:
        return None
    if len(found) > 1:
        raise MarkerError(f"{len(found)} Disposition lines in the anchor window")
    match = _MARKER.match(found[0])
    if match is None:
        raise MarkerError(f"unparsable Disposition line: {found[0]!r}")
    value = match["value"]
    if value not in DOCUMENT_VALUES:
        raise MarkerError(f"{value!r} is not one of {DOCUMENT_VALUES}")
    argument = match["argument"] or ""
    if (value in ARGUMENT_VALUES) != bool(argument):
        raise MarkerError(f"{value!r} carries argument {argument!r}")
    return Marker(value, argument, match["date"], bool(match["flag"]))


# The two documents that self-declare a sibling product, by filename.
_SIBLING = re.compile(r"^docs/\d{4}-\d{2}-\d{2}-proposed-adr-software-development-")
# §10 names these two: their disposition belongs to a tracked issue, not to us.
_PENDING_ISSUE = {
    "docs/adr/0004-citekey-is-the-only-identity.md": "116",
    "docs/adr/0005-better-bibtex-owns-the-bibliography-export.md": "116",
}
# Dated passes that closed. Evidence, never a live decision.
_HISTORICAL_PREFIXES = (
    ".superpowers/sdd/",
    "docs/research/rethink-audits/",
    "docs/research/harness-audits/",
    "docs/research/raw/",
)
# Surfaces that ship or that AGENTS.md points agents at — binding by construction.
_CURRENT_PATHS = frozenset(
    {
        "AGENTS.md",
        "CONTEXT.md",
        "README.md",
        "docs/testing.md",
        "docs/terminology.md",
        "docs/superpowers/specs/2026-09-05-assembly-design.md",
    }
)
# `docs/adr/` whole, not an enumeration of 0001-0003: an accepted decision
# record is current by construction, and 0004/0005 are carved out by the
# earlier `_PENDING_ISSUE` rule rather than by omission here. The enumeration
# would also drop a future ADR 0006 into the pending-map residual.
_CURRENT_PREFIXES = (
    "skills/",
    "docs/agents/",
    "docs/adr/",
)
_SCOPING_REVIEW_HINTS = (
    "survey",
    "analysis",
    "landscape",
    "catalogue",
    "sourcing",
    "prior-art",
    "competitive",
)


class Proposal(NamedTuple):
    value: str
    argument: str
    flag: bool
    rule: str


def _declares_superseded(text: str) -> bool:
    """SUPERSEDED in the anchor window only — the sdd reports say it in their bodies."""
    lines = text.split("\n")
    start = anchor(lines)
    return any("SUPERSEDED" in line for line in lines[start : start + WINDOW])


def propose(path: str, text: str) -> Proposal:
    """§10's precedence order, first match wins, with the rule that fired named.

    `pending-map` and `current` are not mechanically separable, so `current` is
    an allow-list and `pending-map` is the residual. Every residual row is what
    the author's review is for.
    """
    flag = any(hint in path for hint in _SCOPING_REVIEW_HINTS)
    if _SIBLING.match(path):
        return Proposal("sibling-project", "", flag, "sibling-filename")
    if _declares_superseded(text):
        return Proposal("superseded-by", "?", flag, "header-superseded")
    if path in _PENDING_ISSUE:
        return Proposal("pending-issue", _PENDING_ISSUE[path], flag, "spec-named-issue")
    if path.startswith(_HISTORICAL_PREFIXES):
        return Proposal("historical", "", flag, "closed-pass-path")
    if path in _CURRENT_PATHS or path.startswith(_CURRENT_PREFIXES):
        return Proposal("current", "", flag, "shipped-surface")
    return Proposal("pending-map", "", flag, "residual")


HEADER = "key\tvalue\targument\tflag\trule\tnote"


class Row(NamedTuple):
    key: str
    value: str
    argument: str
    flag: bool
    rule: str
    note: str


def propose_or_existing(path: str, text: str) -> Proposal:
    """A marker already in the file wins over the classifier.

    `propose` is pure, so re-emitting over a corpus the author has already
    reviewed would hand back the classifier's guesses and the next `apply`
    would quietly undo the review. The file is the record; the classifier only
    fills blanks. This is also what makes re-running `propose` mid-review safe.
    """
    marker = read_marker(text)
    if marker is None:
        return propose(path, text)
    return Proposal(marker.value, marker.argument, marker.flag, "existing")


def emit(root: Path = ROOT, issues: list[dict] | None = None) -> str:
    """One reviewable row per in-scope document, header first, then issues."""
    lines = [HEADER]
    for path in in_scope(root):
        proposal = propose_or_existing(path, (root / path).read_text(encoding="utf-8"))
        lines.append(
            "\t".join(
                [
                    path,
                    proposal.value,
                    proposal.argument,
                    FLAG if proposal.flag else "",
                    proposal.rule,
                    "",
                ]
            )
        )
    for issue in issues or []:
        proposal = propose_issue(int(issue["number"]))
        lines.append(
            "\t".join(
                [
                    f"issue:{issue['number']}",
                    proposal.value,
                    proposal.argument,
                    "",
                    proposal.rule,
                    issue["title"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def parse_rows(text: str) -> list[Row]:
    """The reviewed file back into rows. The author's edits are the authority."""
    rows = []
    for line in text.split("\n"):
        if not line or line == HEADER:
            continue
        fields = line.split("\t")
        if len(fields) != 6:
            raise MarkerError(f"{len(fields)} columns, expected 6: {line!r}")
        key, value, argument, flag, rule, note = fields
        if flag not in ("", FLAG):
            raise MarkerError(f"flag column is {flag!r}, expected '' or {FLAG!r}")
        rows.append(Row(key, value, argument, flag == FLAG, rule, note))
    return rows


ISSUE_VALUES = ("absorbed-by", "superseded", "still-open", "pending-map")
ISSUE_TABLE = "docs/issue-dispositions.md"

# §10 names these six as the first to close against the assembly spec, and
# these three as staying open (§2, §4, §7.3). Sections are this plan's reading
# of where each issue's subject now lives; the author's review is the authority.
_ABSORBED = {96: "§6", 97: "§5.2", 62: "§9", 63: "§9", 78: "§9", 118: "§5"}
_STILL_OPEN = frozenset({116, 117, 119})

# mdformat's `tables` extension pads every cell to the column width (measured
# 2026-09-05: `| 96    | absorbed-by: §6 | X     |`), so the reader tolerates
# padding even though the renderer emits none.
_TABLE_ROW = re.compile(
    r"^\|\s*(?P<number>\d+)\s*\|\s*(?P<title>[^|]*?)\s*\|"
    r"\s*(?P<disposition>[^|]+?)\s*\|\s*(?P<note>[^|]*?)\s*\|$"
)

_TABLE_PREAMBLE = """# Issue dispositions

Disposition: current (%(date)s)

Written by the status-marking pass of `docs/superpowers/specs/2026-09-05-assembly-design.md`
§10 and maintained by `scripts/dispositions.py`. One row per open issue.
Vocabulary: `absorbed-by: <spec §>`, `superseded`, `still-open`, `pending-map`.
`tests/test_dispositions.py` refuses an off-vocabulary row and, where `gh` is
usable, an open issue with no row.

The `Title` column is read from GitHub at write time and is not round-tripped:
the proposal's own last column carries the author's *reason*, which is what
`Note` holds. A reader gets both without clicking through.

| Issue | Title | Disposition | Note |
| --- | --- | --- | --- |
"""


def propose_issue(number: int) -> Proposal:
    if number in _ABSORBED:
        return Proposal("absorbed-by", _ABSORBED[number], False, "spec-named-absorbed")
    if number in _STILL_OPEN:
        return Proposal("still-open", "", False, "spec-named-open")
    return Proposal("pending-map", "", False, "residual")


def render_issue_table(
    rows: list[Row], date: str = "", titles: dict | None = None
) -> str:
    """The committed table, highest issue number first.

    The sort is not cosmetic: the table is a tracked file regenerated from
    `gh issue list`, and without a fixed order every regeneration would produce
    a diff that is only row movement.
    """
    date = date or _dt.datetime.now(_dt.UTC).date().isoformat()
    titles = titles or {}
    lines = [_TABLE_PREAMBLE % {"date": date}]
    for row in sorted(rows, key=lambda row: -int(row.key.removeprefix("issue:"))):
        title = titles.get(row.key, "")
        # A `|` ends the cell, so a pipe-bearing issue title would render a row
        # `_TABLE_ROW` cannot match — and `read_issue_table` would drop it with
        # no error at all. Refuse loudly instead, the way `parse_rows` refuses a
        # tab. No open issue carries one today; the check is for the one that will.
        for cell in (row.value, row.argument, row.note, title):
            if "|" in cell:
                raise MarkerError(
                    f"{row.key}: a pipe in {cell!r} would end the table cell and drop the row"
                )
        disposition = row.value + (f": {row.argument}" if row.argument else "")
        number = row.key.removeprefix("issue:")
        lines.append(f"| {number} | {title} | {disposition} | {row.note} |\n")
    return "".join(lines)


def read_issue_table(text: str) -> list[Row]:
    rows = []
    for line in text.split("\n"):
        match = _TABLE_ROW.match(line)
        if match is None:  # the header and separator rows carry no digits
            continue
        disposition = match["disposition"].strip()
        value, _, argument = disposition.partition(": ")
        if value not in ISSUE_VALUES:
            raise MarkerError(f"{value!r} is not one of {ISSUE_VALUES}")
        rule = (
            "spec-named-absorbed"
            if value == "absorbed-by"
            else ("spec-named-open" if value == "still-open" else "residual")
        )
        # The title is render-only — GitHub owns it and it is re-read on every
        # write, so nothing is lost by not parsing it back.
        rows.append(
            Row(
                f"issue:{match['number']}",
                value,
                argument,
                False,
                rule,
                match["note"].strip(),
            )
        )
    return rows


def marker_line(value: str, argument: str, flag: bool, date: str) -> str:
    """Render one marker, rejecting anything read_marker would reject."""
    if value not in DOCUMENT_VALUES:
        raise MarkerError(f"{value!r} is not one of {DOCUMENT_VALUES}")
    if (value in ARGUMENT_VALUES) != bool(argument):
        raise MarkerError(f"{value!r} carries argument {argument!r}")
    if argument == "?":
        raise MarkerError(f"{value!r} still carries the unreviewed '?' target")
    rendered = f"Disposition: {value}"
    if argument:
        rendered += f": {argument}"
    rendered += f" ({date})"
    if flag:
        rendered += f" [{FLAG}]"
    return rendered


def apply_marker(text: str, line: str) -> str:
    """Write the marker at its anchor, replacing one already in the window."""
    lines = text.split("\n")
    start = anchor(lines)
    for index in range(start, min(start + WINDOW, len(lines))):
        if lines[index].startswith("Disposition: "):
            lines[index] = line
            return "\n".join(lines)
    prefix, rest = lines[:start], lines[start:]
    if rest and rest[0] == "":
        rest = rest[1:]
    block = ([""] if prefix else []) + [line, ""]
    return "\n".join(prefix + block + rest)


def apply_rows(
    rows: list[Row], root: Path = ROOT, date: str = "", titles: dict | None = None
) -> list[str]:
    """Write every document row. Returns the repo-relative paths touched.

    Hand-edited cells in the proposal are trusted: tabs or newlines in `note` or
    `argument` are not validated here, but parse_rows' six-column check catches
    tabs before this runs, so a tab becomes a loud MarkerError rather than a silent
    drop. Newlines in hand-edited cells are structurally impossible in TSV.
    """
    # `_dt.UTC`, not `_dt.timezone.utc`: ruff's UP017 wants the alias and DTZ
    # wants an aware call, and eight call sites in `research_vault/` already use
    # this exact form. The date on a marker is a record date, and `--date` is the
    # path for a human-chosen one — this is only the unattended fallback.
    date = date or _dt.datetime.now(_dt.UTC).date().isoformat()
    tracked = set(in_scope(root)) if root == ROOT else None

    # Separate issue rows from document rows
    issue_rows = [row for row in rows if row.key.startswith("issue:")]
    document_rows = [row for row in rows if not row.key.startswith("issue:")]

    written = []
    for row in document_rows:
        line = marker_line(row.value, row.argument, row.flag, date)
        if (
            row.value == "superseded-by"
            and tracked is not None
            and row.argument not in tracked
        ):
            raise MarkerError(
                f"{row.key}: superseded-by target {row.argument!r} does not resolve"
            )
        path = root / row.key
        path.write_text(
            apply_marker(path.read_text(encoding="utf-8"), line), encoding="utf-8"
        )
        written.append(row.key)

    if issue_rows:
        (root / ISSUE_TABLE).write_text(
            render_issue_table(issue_rows, date, titles), encoding="utf-8"
        )
        written.append(ISSUE_TABLE)

    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.dispositions")
    sub = parser.add_subparsers(dest="command", required=True)
    propose_cmd = sub.add_parser("propose", help="write the reviewable proposal")
    propose_cmd.add_argument("--out", default="disposition-proposal.tsv")
    propose_cmd.add_argument("--issues-json", default="")
    apply_cmd = sub.add_parser("apply", help="write markers from a reviewed proposal")
    apply_cmd.add_argument("proposal")
    apply_cmd.add_argument("--date", default="")
    apply_cmd.add_argument("--issues-json", default="")
    args = parser.parse_args(argv)
    if args.command == "propose":
        issues = (
            json.loads(Path(args.issues_json).read_text(encoding="utf-8"))
            if args.issues_json
            else None
        )
        text = emit(issues=issues)
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"proposed {len(parse_rows(text))} rows to {args.out}")
        return 0
    if args.command == "apply":
        rows = parse_rows(Path(args.proposal).read_text(encoding="utf-8"))
        titles_dict = None
        if args.issues_json:
            issues_list = json.loads(Path(args.issues_json).read_text(encoding="utf-8"))
            titles_dict = {
                f"issue:{issue['number']}": issue["title"] for issue in issues_list
            }
        written = apply_rows(rows, date=args.date, titles=titles_dict)
        documents = [path for path in written if path != ISSUE_TABLE]
        table = " and the issue table" if len(documents) != len(written) else ""
        print(f"marked {len(documents)} documents{table} from {args.proposal}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
