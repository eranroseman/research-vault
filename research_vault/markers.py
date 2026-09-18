"""verify's marker writer and clearer: `[failed-verification:: <check>/<date>]`.

Markers live where a check's origin is — a claim line's terminal anchor, or
the numbered line — and never under `wiki/` (the compiled layer is the tool's
write scope, ingest spec §4.4). One rewriter serves the stamp (first matching
line, then stop) and the clear (every matching line). `verify` imports from
here; this module imports nothing from `verify`.
"""

import os
import re
from collections.abc import Mapping
from pathlib import Path

from . import claims, gitstate
from .pathcodec import PathCodecError, decode_repo_path

_ANY_VERIFY_MARKER = r"\[failed-verification:: [A-Za-z0-9-]+/\d{4}-\d{2}-\d{2}\]"
# The writer's own shape, both placements: `before + "[marker] " + anchor`
# after a space-terminated `before`, or `content + " [marker]"`.
_OWN_MARK = re.compile(rf" {_ANY_VERIFY_MARKER}")


def _without_own_marks(text: str) -> str:
    """An ack scope hashes what the person wrote, never the tool's own marks.

    Every scope leg strips verify's ``[failed-verification:: …]`` marker before
    hashing, so the scope is invariant under the tool's own stamp and clear
    (open point 07) — the body-marker counterpart of what
    ``canonical_content`` already does with ``verified`` events.
    """
    return _OWN_MARK.sub("", text)


def _read_note_text(path):
    with Path(path).open("r", encoding="utf-8", newline="") as note:
        return note.read()


def _write_note_text(path, text):
    with Path(path).open("w", encoding="utf-8", newline="") as note:
        note.write(text)


def _safe_relative(vault_root, target, target_kind="identifier"):
    """Return an exact vault path only for explicit canonical repo-path metadata."""
    if target_kind != "repo-path" or not isinstance(target, str):
        return None
    try:
        raw = decode_repo_path(target)
        absolute = gitstate._absolute(Path(vault_root), raw)
        image = gitstate.live_image(Path(vault_root), raw)
    except (PathCodecError, gitstate.GitStateError, OSError):
        return None
    if image is not None and image.kind in {"symlink", "special"}:
        return None
    return Path(os.fsdecode(absolute))


def _root(vault_root) -> Path:
    """The root exactly as `gitstate._absolute` builds a `path-bytes:`
    candidate from it (abspath, not resolve: no symlink is followed), so the
    guard below and the candidate meet even when the caller was handed
    `--vault .`."""
    return Path(os.fsdecode(gitstate._root_bytes(Path(vault_root))))


def _under_wiki(root: Path, path: Path) -> bool:
    # The compiled layer is the tool's write scope (ingest spec §4.4): verify
    # reads it and never writes into it, so there is no marker to stamp or clear.
    return path.relative_to(root).parts[0] == "wiki"


def _origins(outcome):
    """Yield only the exact claim origins supplied by a checker."""
    note_path = (
        outcome.extra.get("note_path")
        if "note_path" in outcome.path_extra_fields
        else None
    )
    if outcome.check == "citation-key":
        for claim in outcome.extra.get("claims", []):
            if isinstance(claim, Mapping):
                claim_id = claim.get("claim_id")
                line_no = claim.get("line_no")
                if isinstance(claim_id, str) or isinstance(line_no, int):
                    yield note_path, claim_id, line_no
        return
    claim_id = outcome.extra.get("claim_id")
    line_no = outcome.extra.get("line_no")
    if isinstance(note_path, str) and (
        isinstance(claim_id, str) or isinstance(line_no, int)
    ):
        yield note_path, claim_id, line_no


def _rewrite_marker_lines(path, check, matcher, *, clear, first_only, date=None):
    """Row 54: the one line rewriter. ``matcher(index, content)`` answers
    ``(selected, terminal_claim_id)``; on a selected line the marker for
    ``check`` is cleared (``clear``) or stamped (dated ``date``) — before the
    terminal anchor when the line has one, at the end otherwise. With
    ``first_only`` the walk stops at the first selected line whether or not
    it changed. Writes once, at the end; returns whether anything changed."""
    lines = _read_note_text(path).splitlines(keepends=True)
    changed = False
    for index, line in enumerate(lines):
        content, ending = _split_line_ending(line)
        selected, terminal_claim_id = matcher(index, content)
        if not selected:
            continue
        pattern = _terminal_marker_pattern(check, terminal_claim_id)
        if clear:
            # The pattern's lookahead keeps the anchor; the single space closes
            # the gap the marker left.
            replacement = pattern.sub(
                " " if isinstance(terminal_claim_id, str) else "", content
            )
        elif pattern.search(content) is None:
            marker = f"[failed-verification:: {check}/{date}]"
            if isinstance(terminal_claim_id, str):
                anchor = _terminal_anchor_match(content, terminal_claim_id)
                replacement = (
                    content[: anchor.start()] + marker + " " + content[anchor.start() :]
                )
            else:
                replacement = content + " " + marker
        else:
            replacement = content
        if replacement != content:
            lines[index] = replacement + ending
            changed = True
        if first_only:
            break
    if changed:
        _write_note_text(path, "".join(lines))
    return changed


def _mutate_marker(vault_root, outcome, date, *, clear=False):
    """Stamp (or clear) the marker at each origin of a closing check's outcome;
    the caller decides which outcomes qualify (`verify._apply_state_transitions`)."""
    root = _root(vault_root)
    for relative, claim_id, line_no in _origins(outcome):
        path = _safe_relative(vault_root, relative, "repo-path")
        if path is None or not path.is_file() or _under_wiki(root, path):
            continue

        def matcher(index, content, claim_id=claim_id, line_no=line_no):
            if _terminal_anchor_match(content, claim_id) is not None:
                return True, claim_id
            if isinstance(line_no, int) and index == line_no - 1:
                return True, None
            return False, None

        _rewrite_marker_lines(
            path, outcome.check, matcher, clear=clear, first_only=True, date=date
        )


def _cites(content, citation_key):
    """Whether a line cites exactly ``citation_key`` (never a longer key)."""
    return any(
        match.group("key") == citation_key for match in claims.CITE_RE.finditer(content)
    )


def _claim_notes(vault: Path) -> list[Path]:
    """The notes ``_plan_state`` scans for claim lines, minus the compiled layer.

    ``literature/`` flat, the same rule as every reader of it (decision 08).
    """
    return sorted((vault / "projects").rglob("*.md")) + sorted(
        (vault / "literature").glob("*.md")
    )


def clear_marker_for(vault_root, check: str, target: str) -> bool:
    """Open point 09: a human acknowledgment stands the marker down.

    Markers live where ``_mutate_marker`` writes them — at each claim's origin
    — so a ``<citation key>#^<claim id>`` target names every note carrying the
    anchor, which confines the edit to the claim line; a bare citation-key
    target of a ``citation-key`` finding (verify's own shape: the claim list
    rides in the outcome's ``extra`` and the inbox row does not persist it)
    names every line citing ``[@<key>``, the citation regex keeping
    ``smith2020`` from matching ``smith2020a``; a ``path-bytes:`` target names
    the file itself, and every terminal marker for the check in it. The notes
    are ``projects/**/*.md`` and ``literature/*.md``: ``_plan_state`` scans
    both for claim lines, and a capture-rendered literature note matches
    nothing only because it carries none — a hand-authored one does receive
    markers. Anything under ``wiki/`` is skipped, mirroring the writer's own
    guard (ingest spec §4.4). Returns whether a marker was removed.
    """
    vault = _root(vault_root)
    claim_id: str | None = None
    citation_key: str | None = None
    if "#^" in target:
        claim_id = target.split("#^", 1)[1]
        candidates = _claim_notes(vault)
    elif target.startswith("path-bytes:"):
        candidates = [_safe_relative(vault, target, "repo-path")]
    elif check == "citation-key":
        citation_key = target
        candidates = _claim_notes(vault)
    else:
        return False

    def matcher(_index, content):
        if claim_id is not None:
            if _terminal_anchor_match(content, claim_id) is None:
                return False, None
            return True, claim_id
        if citation_key is not None:
            if not _cites(content, citation_key):
                return False, None
            # The writer put the marker before the citing line's own anchor
            # when it has one, after the line otherwise.
            anchor = claims.ANCHOR_RE.search(content)
            return True, anchor.group("id") if anchor else None
        return True, None

    cleared = False
    for path in candidates:
        if path is None or not path.is_file() or _under_wiki(vault, path):
            continue
        if _rewrite_marker_lines(path, check, matcher, clear=True, first_only=False):
            cleared = True
    return cleared


def _terminal_marker_pattern(check, claim_id):
    marker = r"\[failed-verification:: " + re.escape(check) + r"/\d{4}-\d{2}-\d{2}\]"
    if isinstance(claim_id, str):
        trailing = rf"(?:{_ANY_VERIFY_MARKER} )*\^{re.escape(claim_id)}[ \t]*$"
        return re.compile(rf" {marker} (?={trailing})")
    trailing = rf"(?: {_ANY_VERIFY_MARKER})*[ \t]*$"
    return re.compile(rf" {marker}(?={trailing})")


def _terminal_anchor_match(content, claim_id):
    if not isinstance(claim_id, str):
        return None
    return re.search(rf"\^{re.escape(claim_id)}[ \t]*$", content)


def _split_line_ending(line):
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""
