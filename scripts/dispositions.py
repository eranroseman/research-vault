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

# One test governs this list: DOES THIS PATH SHIP TO A CONSUMER? A Disposition
# line is repo bookkeeping, and bookkeeping that travels out of the repository
# lands in front of a reader who cannot act on it.
#   research_vault/templates/** ships into a user's vault;
#   skills/** ships in the installed plugin — a SKILL.md body is a prompt, so a
#     marker there is repo bookkeeping injected into what an agent reads as
#     instruction, and their references/** are that prompt's own pages;
#   .out-of-scope/** declares its disposition by path.
# `CLAUDE.md` is excluded on a different ground: it is an 11-byte import
# directive, not a document (spec §10).
EXCLUDED_PREFIXES = (
    "research_vault/templates/",
    ".out-of-scope/",
    "skills/",
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


_FENCE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})")


def unfenced(lines: list[str]) -> list[bool]:
    """One flag per line: True where the line is document text, not code.

    The module's single fence scanner. CommonMark §4.5: an opening fence is
    three or more backticks or tildes indented at most three spaces, and it
    closes on a fence of the SAME character and at least the same length. The
    `startswith("```")` toggle this replaces got both halves wrong — it missed
    the five in-scope files whose fences are indented one to three spaces, and
    it mis-tracked four-backtick blocks, where the inner three-backtick fences
    (this plan has them) flipped the state off halfway through.

    All four consumers go through it: `anchor`, `read_marker`,
    `displaced_markers` and `apply_marker`'s window scan. Two of them used a
    raw `startswith` until the second fix wave, which left a fenced example in
    the window readable as the document's own marker — and overwritable.

    COMPLETE FOR COLUMN-0 CONSUMERS; revisit if a caller matches indented.
    That completeness is a property of the callers, not of the parser. Every
    caller here matches at column 0 — `anchor` matches `^#{1,6} ` and the
    marker scans match `Disposition: ` — and a fence indented four or more
    spaces sits inside a list item, whose content therefore cannot begin at
    column 0 either. Lazy continuation, which could put content at column 0
    inside a list item, applies to paragraphs and not to fenced code.
    """
    flags = []
    opener = ""
    for line in lines:
        match = _FENCE.match(line)
        if opener:
            flags.append(False)
            fence = match["fence"] if match else ""
            if fence[:1] == opener[:1] and len(fence) >= len(opener):
                opener = ""
        elif match:
            opener = match["fence"]
            flags.append(False)
        else:
            flags.append(True)
    return flags


def anchor(lines: list[str]) -> int:
    """The index the marker window opens at: after the first heading, else 0.

    Any level (spec §10): 21 in-scope files open at `###`, and only the four
    bare-prose `docs/research/**/README.md` files carry no heading at all.
    Fence-aware — a `# ` inside a fenced block is a shell comment, not a
    heading. No file in scope trips that today; new documents arrive without
    asking.
    """
    for index, (line, outside) in enumerate(zip(lines, unfenced(lines), strict=True)):
        if outside and _HEADING.match(line):
            return index + 1
    return 0


def read_marker(text: str) -> Marker | None:
    """The document's marker, or None when it carries none. Raises on malformed.

    Fence-aware, like every other marker scan: a `Disposition:` line quoted
    inside a fenced block that happens to fall in the window is an EXAMPLE, and
    reading it as the document's own verdict would let `apply` overwrite a
    document's prose. No in-scope file trips it today; new documents arrive
    without asking.
    """
    lines = text.split("\n")
    start = anchor(lines)
    window = slice(start, start + WINDOW)
    found = [
        line
        for line, outside in zip(lines[window], unfenced(lines)[window], strict=True)
        if outside and line.startswith("Disposition: ")
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


def displaced_markers(lines: list[str]) -> list[int]:
    """Indices of `Disposition:` lines sitting OUTSIDE the anchor window.

    A marker here reads as absent — `read_marker` only looks in the window — so
    a re-sweep would add a second one and the two could disagree while the
    linter, reading the same window, saw nothing wrong. Fenced lines are
    examples quoted in prose, never markers, so `unfenced` excludes them.
    """
    start = anchor(lines)
    window = range(start, start + WINDOW)
    return [
        index
        for index, (line, outside) in enumerate(
            zip(lines, unfenced(lines), strict=True)
        )
        if outside and line.startswith("Disposition: ") and index not in window
    ]


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
# Surfaces a repository reader lands on first, or that AGENTS.md points agents
# at — binding by construction.
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
    """One reviewable row per in-scope document, header first, then issues.

    Both halves are `existing`-wins: a marked document and a row already in the
    committed table each beat the classifier. That symmetry is the human gate —
    re-running `propose` at any time hands the review back untouched.
    """
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
    reviewed = existing_issue_rows(root)
    for issue in issues or []:
        key = f"issue:{issue['number']}"
        existing = reviewed.get(key)
        proposal = propose_issue_or_existing(int(issue["number"]), existing)
        # `Note` carries the author's *reason* once the table exists. The issue
        # title only ever seeds a row no reviewed table covers yet.
        note = (
            existing.note
            if existing is not None
            else issue_note(proposal, issue["title"])
        )
        # The doubled tab is the flag column, always empty on an issue row: the
        # `should-be-scoping-review` hint reads a filename, and an issue has none.
        lines.append(
            f"{key}\t{proposal.value}\t{proposal.argument}\t\t{proposal.rule}\t{note}"
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
§10 and maintained by `scripts/dispositions.py`. One row per issue the pass
dispositioned, closed issues included: closing an issue is one of the things a
disposition decides, so the row outlives it as the record of why.
Issue vocabulary: `absorbed-by: <spec §>`, `superseded`, `still-open`,
`pending-map` — a different axis from the `Disposition:` line above, which is
this file's own marker in the *document* vocabulary.
`tests/test_dispositions.py` refuses an off-vocabulary row and, where `gh` is
usable, an open issue with no row.

The `Title` column is read from GitHub at write time and is not round-tripped
into a proposal row; a re-render given no fresh listing carries the committed
cells forward rather than blanking them. `Note` holds the author's *reason*,
and never the title again. A reader gets both without clicking through.

| Issue | Title | Disposition | Note |
| --- | --- | --- | --- |
"""


def propose_issue(number: int) -> Proposal:
    if number in _ABSORBED:
        return Proposal("absorbed-by", _ABSORBED[number], False, "spec-named-absorbed")
    if number in _STILL_OPEN:
        return Proposal("still-open", "", False, "spec-named-open")
    return Proposal("pending-map", "", False, "residual")


def issue_note(proposal: Proposal, title: str) -> str:
    """The seed note for an issue no reviewed table covers yet.

    `Note` promises a REASON. Writing the title into it for every row made nine
    rows state the subject twice and no reason once, so where §10 decides the
    disposition it also supplies the reason and this says so. Where it does
    not, the title is the seed and must stay: the TSV carries no title column,
    so the note is the only place a reviewer sees which issue the row is about.
    `render_issue_table` blanks a seed note that survives review unedited, and
    `apply` reports the row by number — a reason nobody wrote is a shortfall,
    and a shortfall must not stop the unattended write.
    """
    if proposal.rule == "spec-named-absorbed":
        return f"§10 names this as absorbed by {proposal.argument}"
    if proposal.rule == "spec-named-open":
        return "§10 names this as staying open"
    return title


def existing_issue_rows(root: Path = ROOT) -> dict[str, Row]:
    """The committed table's rows by key — empty before the table exists.

    The issue half's equivalent of reading a marker out of a document: the
    committed table IS the record, the same way the file is for a document.
    """
    table = root / ISSUE_TABLE
    if not table.is_file():
        return {}
    return {row.key: row for row in read_issue_table(table.read_text(encoding="utf-8"))}


def propose_issue_or_existing(number: int, existing: Row | None) -> Proposal:
    """A row already in the committed table wins over the classifier.

    The exact mirror of `propose_or_existing`, which the issue half never got.
    Without it the plan's own merge-time top-up — a bare `propose
    --issues-json` — hands back the classifier's guesses for every issue the
    author decided, and the next `apply` writes them over the reviewed table.
    Measured 2026-09-06 with the mirror missing: 42 of 66 values reverted and
    57 notes overwritten in one command.
    """
    if existing is None:
        return propose_issue(number)
    return Proposal(existing.value, existing.argument, False, "existing")


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
        # The preamble promises Note carries a reason. A Note repeating Title
        # states the subject twice and the reason never, while looking filled
        # in — so render it EMPTY, which is what a missing reason looks like.
        # Refusing it instead made the seed note `emit` writes unappliable and
        # closed the unattended merge-time path: publishing something FALSE is
        # an invariant violation, publishing something INCOMPLETE is a
        # shortfall, and `rows_without_reason` is how the shortfall is reported.
        # The pipe check above still raises — a pipe drops the row in silence,
        # which is falsification, not absence.
        #
        # A Note publishes only when it can be VERIFIED not to be the seed, so
        # an unknown title blanks it too. `emit` seeds a row no committed table
        # covers with the GitHub title, and with no title to compare against
        # that seed shipped as the row's reason — a blank Title beside the
        # title itself sitting in Note, which the preamble says never happens.
        # Unverifiable is unverified: blank, and reported.
        #
        # Truthiness, not `row.key in titles`: after one such write the key IS
        # in the carried-forward titles, with the blank cell it just rendered.
        # A membership test would read that blank as a known title, republish
        # the seed, and undo itself on the second apply.
        note = row.note if title and row.note != title else ""
        disposition = row.value + (f": {row.argument}" if row.argument else "")
        number = row.key.removeprefix("issue:")
        lines.append(f"| {number} | {title} | {disposition} | {note} |\n")
    return "".join(lines)


def rows_without_reason(text: str) -> list[str]:
    """The issue numbers a rendered table ships with an empty Note, ascending.

    `Note` promises a reason and the renderer blanks one it cannot verify to be
    a reason — one that repeats the Title, and one whose Title is unknown — so
    an empty cell is the visible form of a reason nobody has written yet, or
    one the renderer could not confirm. `apply` prints this list rather than
    raising: the merge-time top-up runs unattended, and an exception there
    abandons the whole write over a cell no automation can fill.
    """
    return sorted(
        (
            row.key.removeprefix("issue:")
            for row in read_issue_table(text)
            if not row.note
        ),
        key=int,
    )


def read_issue_titles(text: str) -> dict[str, str]:
    """The Title cells the table already carries, by key.

    `read_issue_table` deliberately drops Title, which makes the committed
    table the ONLY copy of it: nothing else in the repository holds a rendered
    issue title. So a re-render with no fresh `--issues-json` has to carry them
    forward here or write 66 blank cells that nothing can recover.
    """
    return {
        f"issue:{match['number']}": match["title"].strip()
        for line in text.split("\n")
        if (match := _TABLE_ROW.match(line))
    }


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
        # The rule names WHERE A VALUE CAME FROM, and the table does not record
        # it. Deriving one from the value fabricated provenance: 31 of 66 rows
        # read back claiming `spec-named-open` though §10 names exactly three
        # (#116, #117, #119) — every author-decided still-open row asserted a
        # spec authority it does not have. The table is the source; say so.
        rows.append(
            Row(
                f"issue:{match['number']}",
                value,
                argument,
                False,
                "read-from-table",
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
    # The value checks above cover the vocabulary but not the SHAPE, which is
    # where `--date 2026-9-6` got through: every document was rewritten with a
    # marker the reader then rejects, exit 0. Validate against the one grammar
    # the reader uses rather than a second description of it.
    if _MARKER.match(rendered) is None:
        raise MarkerError(f"would write a marker read_marker rejects: {rendered!r}")
    return rendered


def _drop_line(lines: list[str], index: int) -> list[str]:
    """Remove one line, closing the blank-line gap it would otherwise leave."""
    remaining = lines[:index] + lines[index + 1 :]
    before = remaining[index - 1] if index else None
    after = remaining[index] if index < len(remaining) else None
    if before == "" and after == "":
        del remaining[index]
    return remaining


def apply_marker(text: str, line: str) -> str:
    """Write the marker at its anchor, MOVING one that has drifted out of window.

    A marker pushed below the five-line window reads as ABSENT to
    `read_marker`, so inserting beside it leaves the file with two markers that
    can disagree — while the linter, which also reads the window, passes.
    Moving is what keeps the count at one; the result is byte-identical on a
    second run, because the marker is then back inside the window.

    A fenced `Disposition:` line is an EXAMPLE, not a marker: this repository's
    own plan quotes the table preamble inside a code block, and moving that
    would edit a document's prose. `unfenced` is what tells them apart.

    The drop runs BEFORE the window scan, and that order is the whole guarantee.
    Scanning first returned on the in-window hit, so a file carrying BOTH an
    in-window and a displaced marker kept both — the one case where the count
    was already two, and the only case the docstring's promise was for.
    """
    lines = text.split("\n")
    for index in reversed(displaced_markers(lines)):
        lines = _drop_line(lines, index)
    # After the drops: every index has moved, and a marker dropped from ABOVE
    # the first heading moves the anchor itself. The flags are re-derived for
    # the same reason.
    start = anchor(lines)
    outside = unfenced(lines)
    for index in range(start, min(start + WINDOW, len(lines))):
        if outside[index] and lines[index].startswith("Disposition: "):
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

    # Separate issue rows from document rows. The table render below OWNS
    # `docs/issue-dispositions.md`: it writes the whole file, marker preamble
    # included, so its own in-scope document row is a no-op here. Applying both
    # in one call would write the document row's marker and then overwrite the
    # entire file with the render, silently discarding the reviewed row — two
    # writers, one file, last one wins.
    issue_rows = [row for row in rows if row.key.startswith("issue:")]
    document_rows = [
        row
        for row in rows
        if not row.key.startswith("issue:") and row.key != ISSUE_TABLE
    ]

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
        table = root / ISSUE_TABLE
        # A blanked Title is unrecoverable: `read_issue_table` does not read it
        # back and no other file holds one. Both operational commands in the
        # plan omit `--issues-json`, so the loss is on the ordinary path rather
        # than the exotic one.
        #
        # PER KEY, not all-or-nothing. The earlier `if not titles` carried the
        # committed cells forward only when the flag was absent entirely, so a
        # supplied listing that omitted one issue — a truncated `gh --limit` is
        # the reachable case, and this plan warns about it twice — blanked that
        # row's Title in silence. The supplied listing wins where it speaks;
        # the committed table fills every gap.
        committed = (
            read_issue_titles(table.read_text(encoding="utf-8"))
            if table.is_file()
            else {}
        )
        if not committed and not titles:
            raise MarkerError(
                f"{ISSUE_TABLE} offers no Title cell to carry forward and none "
                "were supplied: "
                "every Title cell would be written blank and nothing reads it back"
            )
        titles = committed | (titles or {})
        table.write_text(render_issue_table(issue_rows, date, titles), encoding="utf-8")
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
        # `root=ROOT` named rather than defaulted: a default binds at import,
        # so only the explicit argument follows a test that points the module
        # at a temporary repository.
        text = emit(root=ROOT, issues=issues)
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
        written = apply_rows(rows, root=ROOT, date=args.date, titles=titles_dict)
        documents = [path for path in written if path != ISSUE_TABLE]
        table = " and the issue table" if len(documents) != len(written) else ""
        print(f"marked {len(documents)} documents{table} from {args.proposal}")
        # A row with no reason still ships — it is incomplete, not false. Say
        # which ones, so the shortfall is visible to whoever reads the run
        # rather than discovered later by reading 66 table rows.
        if ISSUE_TABLE in written:
            numbers = rows_without_reason(
                (ROOT / ISSUE_TABLE).read_text(encoding="utf-8")
            )
            if numbers:
                print(
                    f"{len(numbers)} issue row(s) shipped with no reason: "
                    + ", ".join(numbers)
                )
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
