"""The §10 status-marking pass: scope, read, propose, and apply the Disposition line.

Repo maintenance, not product. Deliberately not a `research_vault` module and not
a CLI verb: §11 dispositions every verb against the step map, and a maintenance
verb would serve none of them.
"""

import re
import subprocess
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
_CURRENT_PREFIXES = (
    "skills/",
    "docs/agents/",
    "docs/adr/0001-",
    "docs/adr/0002-",
    "docs/adr/0003-",
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
