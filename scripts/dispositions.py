"""The §10 status-marking pass: scope, read, propose, and apply the Disposition line.

Repo maintenance, not product. Deliberately not a `research_vault` module and not
a CLI verb: §11 dispositions every verb against the step map, and a maintenance
verb would serve none of them.
"""

import argparse
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


def emit(root: Path = ROOT) -> str:
    """One reviewable row per in-scope document, header first."""
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.dispositions")
    sub = parser.add_subparsers(dest="command", required=True)
    propose_cmd = sub.add_parser("propose", help="write the reviewable proposal")
    propose_cmd.add_argument("--out", default="disposition-proposal.tsv")
    args = parser.parse_args(argv)
    if args.command == "propose":
        text = emit()
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"proposed {len(parse_rows(text))} rows to {args.out}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
