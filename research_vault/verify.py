"""The verification transaction: collect, plan, apply, publish (spec §6).

Extracted from ``__main__`` so hooks and tests consume a public seam rather
than the CLI entrypoint's private names.
"""

import hashlib
import json
import os
import re
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from . import (
    Result,
    bibliography,
    captured,
    checks,
    claims,
    clock,
    events,
    frontmatter,
    gitstate,
    identify,
    inbox,
    lifecycle,
    lints,
    notes,
    propagate,
    quotes,
    structure,
)
from .pathcodec import (
    PathCodecError,
    RepoPath,
    decode_repo_path,
    encode_repo_path,
)
from .zotero import DEFAULT_BASE, ZoteroClient  # DEFAULT_BASE re-exported for the CLI

_OMITTED_BIBLIOGRAPHY = object()

_ANY_VERIFY_MARKER = r"\[failed-verification:: [A-Za-z0-9-]+/\d{4}-\d{2}-\d{2}\]"
# The writer's own shape, both placements: `before + "[marker] " + anchor`
# after a space-terminated `before`, or `content + " [marker]"`.
_OWN_MARK = re.compile(rf" {_ANY_VERIFY_MARKER}")


def _without_own_marks(text: str) -> str:
    """An ack scope hashes what the person wrote, never the tool's own marks.

    Every scope leg strips verify's ``[failed-verification:: …]`` marker before
    hashing, so the scope is invariant under the tool's own stamp and clear
    (open point 07, ruling 5) — the body-marker counterpart of what
    ``canonical_content`` already does with ``verified`` events.
    """
    return _OWN_MARK.sub("", text)


def _read_note_text(path):
    with Path(path).open("r", encoding="utf-8", newline="") as note:
        return note.read()


def _write_note_text(path, text):
    with Path(path).open("w", encoding="utf-8", newline="") as note:
        note.write(text)


CLOSING_BY_SURFACE = {
    "audit": frozenset(),
    "commit": frozenset(
        {
            "citation-key",
            "evidence-layer",
            "okf-frontmatter",
            "okf-structure",
            "tree",
            "propagation",
            "captured-set",
        }
    ),
    "publish": frozenset(
        {
            "citation-key",
            "evidence-layer",
            "quote",
            "update-notice",
            "okf-frontmatter",
            "okf-structure",
            "tree",
            "propagation",
            "captured-set",
        }
    ),
}
CLOSING_CHECKS = frozenset().union(*CLOSING_BY_SURFACE.values())


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


def _extra_path(vault_root, outcome, key):
    if key not in outcome.path_extra_fields:
        return None
    return _safe_relative(vault_root, outcome.extra.get(key), "repo-path")


def _note_bytes(data: bytes) -> bytes:
    """A note's scope bytes: verifier events and verify's own marks excluded."""
    text = notes.canonical_content(data.decode(errors="surrogateescape"))
    return _without_own_marks(text).encode(errors="surrogateescape")


def _claim_bytes_from_text(text, claim_id):
    """Hash one anchored claim and its continuations, ignoring our marker."""
    lines = notes.canonical_content(text).splitlines(keepends=True)
    for index, line in enumerate(lines):
        content, _ = _split_line_ending(line)
        if _terminal_anchor_match(content, claim_id):
            block = [line]
            for continuation in lines[index + 1 :]:
                if continuation.startswith(("  > ", "  <!-- rv-selector")):
                    block.append(continuation)
                else:
                    break
            return _without_own_marks("".join(block)).encode(errors="surrogateescape")
    return None


def _claim_bytes(path, claim_id):
    try:
        return _claim_bytes_from_text(_read_note_text(path), claim_id)
    except (OSError, UnicodeError):
        return None


def _append_only_basis(vault_root, raw_path, base_snapshot=None):
    if base_snapshot is not None:
        image = base_snapshot.image(raw_path)
        return image.data or b"" if image is not None and image.kind == "file" else b""
    return gitstate.blob_bytes(vault_root, "HEAD", raw_path) or b""


def _directory_bytes(path):
    if not path.is_dir():
        return None
    chunks: list[bytes] = []
    root = path.resolve()
    try:
        children = sorted(path.rglob("*"))
    except OSError:
        return b"unreadable-directory"
    for child in children:
        try:
            relative = os.fsencode(child.relative_to(path).as_posix())
        except ValueError:
            continue
        try:
            if child.is_symlink():
                try:
                    # os.readlink, NOT Path.readlink(): pathlib normalises the stored
                    # target ("./a//b" -> "a/b", "t/" -> "t"), and this byte string
                    # feeds the verification hash, so normalising would change it.
                    link_target = os.fsencode(os.readlink(child))  # noqa: PTH115
                except OSError:
                    link_target = b"unreadable-link"
                chunks.extend((relative, b"symlink", link_target))
                continue
            if not child.is_file():
                continue
            child.resolve().relative_to(root)
        except ValueError:
            chunks.extend((relative, b"outside"))
            continue
        except OSError:
            chunks.extend((relative, b"unreadable"))
            continue
        try:
            data = child.read_bytes()
        except OSError:
            chunks.extend((relative, b"unreadable"))
            continue
        if child.suffix == ".md":
            data = _note_bytes(data)
        chunks.extend((relative, data))
    return b"\0".join(chunks)


def _snapshot_directory_bytes(snapshot, raw_path):
    prefix = raw_path + b"/"
    chunks: list[bytes] = []
    for child_path in sorted(snapshot.images):
        if not child_path.startswith(prefix):
            continue
        image = snapshot.images[child_path]
        relative = child_path[len(prefix) :]
        if image.kind == "symlink":
            chunks.extend((relative, b"symlink", image.data or b""))
        elif image.kind == "file":
            data = image.data or b""
            if child_path.endswith(b".md"):
                data = _note_bytes(data)
            chunks.extend((relative, data))
    return b"\0".join(chunks)


def _note_for_citation_key(vault_root, citation_key):
    try:
        vault = Path(vault_root)
        candidate = notes.note_path(vault, citation_key)
        raw_path = os.fsencode(candidate.relative_to(vault))
    except notes.InvalidCitationKeyError:
        return None
    except ValueError:
        return None
    return _safe_relative(vault, encode_repo_path(raw_path), "repo-path")


def _managed_witness(data) -> str | None:
    """The note's ``managed-sha256`` when capture wrote a well-formed one."""
    value = data.get("managed-sha256")
    if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value):
        return value
    return None


def _citation_key_hash(vault_root, citation_key, candidate_snapshot=None):
    """The scope a note-targeted finding is acknowledged against (open point 07).

    The note's ``managed-sha256`` is the body hash capture writes, so an ack
    survives a frontmatter-only change and lapses when the body moves
    (decision 21). The ``_note_bytes`` digest is the fallback only for a note
    capture never wrote.
    """
    if candidate_snapshot is not None:
        try:
            candidate = notes.note_path(Path(vault_root), citation_key)
            raw_path = os.fsencode(candidate.relative_to(vault_root))
        except (notes.InvalidCitationKeyError, ValueError):
            return None
        image = candidate_snapshot.image(raw_path)
        if image is None or image.kind != "file":
            return None
        raw = image.data or b""
        try:
            data, _ = frontmatter.parse(raw.decode(errors="surrogateescape"))
        except (UnicodeError, frontmatter.FrontmatterError):
            data = {}
        witness = _managed_witness(data)
        if witness is not None:
            return witness
        return hashlib.sha256(_note_bytes(raw)).hexdigest()[:16]
    note = _note_for_citation_key(vault_root, citation_key)
    if note and note.is_file():
        try:
            data, _ = frontmatter.parse(_read_note_text(note))
        except (OSError, UnicodeError, frontmatter.FrontmatterError):
            data = {}
        witness = _managed_witness(data)
        if witness is not None:
            return witness
        return hashlib.sha256(_note_bytes(note.read_bytes())).hexdigest()[:16]
    return None


def _claim_anchor_hash(
    vault_root,
    target,
    raw_origin,
    origin,
    origin_image,
    *,
    base_snapshot,
    candidate_snapshot,
):
    """The identity of a ``citation-key#^claim`` target, or None if its bytes are gone.

    The cited note's own ``managed-sha256`` wins where the note carries a
    validly-shaped one (open point 07); a note with none, or a value that
    doesn't look like a digest, hashes as ``_citation_key_hash``'s fallback.
    Failing that, the claim's bytes are read from whichever plane still
    holds them — candidate image, worktree note, base image or HEAD, then
    the citation key's note. None is not an error here: it means no plane holds
    the claim any more, and the caller falls back to the coarser identities
    below.
    """
    citation_key, claim_id = target.split("#^", 1)
    known_citation_key_hash = _citation_key_hash(
        vault_root, citation_key, candidate_snapshot=candidate_snapshot
    )
    if known_citation_key_hash is not None:
        return known_citation_key_hash
    data = (
        _claim_bytes_from_text(
            (origin_image.data or b"").decode(errors="surrogateescape"), claim_id
        )
        if origin_image is not None and origin_image.kind == "file"
        else _claim_bytes(origin, claim_id)
        if origin
        else None
    )
    if data is None and raw_origin is not None:
        base_image = (
            base_snapshot.image(raw_origin) if base_snapshot is not None else None
        )
        head = (
            base_image.data
            if base_image is not None and base_image.kind == "file"
            else gitstate.blob_bytes(vault_root, "HEAD", raw_origin)
            if base_snapshot is None
            else None
        )
        if head is not None:
            data = _claim_bytes_from_text(
                head.decode(errors="surrogateescape"), claim_id
            )
    if data is None and candidate_snapshot is None:
        note = _note_for_citation_key(vault_root, citation_key)
        data = _claim_bytes(note, claim_id) if note else None
    if data is not None:
        return hashlib.sha256(data).hexdigest()[:16]
    return None


def _snapshot_path_hash(
    vault_root, outcome, raw_target, base_snapshot, candidate_snapshot
):
    """The identity a captured candidate snapshot gives this repo path.

    Symlinks and special files carry no content a hash could stand for, so they
    have no identity at all. Everything else resolves to bytes: an append-only
    target hashes its immutable basis, a file its own (note-normalised) bytes, a
    directory its listing, and a path absent from the candidate falls back to
    the base image so a deletion keeps a stable acknowledgment hash.
    """
    candidate_image = candidate_snapshot.image(raw_target)
    if candidate_image is not None and candidate_image.kind in {
        "symlink",
        "special",
    }:
        return None
    if outcome.check == "append-only":
        data = _append_only_basis(vault_root, raw_target, base_snapshot)
    elif candidate_image is not None and candidate_image.kind == "file":
        data = candidate_image.data or b""
        if raw_target.endswith(b".md"):
            data = _note_bytes(data)
    elif candidate_image is not None and candidate_image.kind == "directory":
        data = _snapshot_directory_bytes(candidate_snapshot, raw_target)
    else:
        base_image = (
            base_snapshot.image(raw_target) if base_snapshot is not None else None
        )
        data = (
            base_image.data
            if base_image is not None and base_image.kind == "file"
            else b""
        ) or b""
        if raw_target.endswith(b".md"):
            data = _note_bytes(data)
    return hashlib.sha256(data).hexdigest()[:16]


def _worktree_path_hash(vault_root, outcome, raw_target, base_snapshot):
    """The identity the live worktree gives this repo path, else git's.

    A path containment refuses, and a path no longer on disk, are both still
    identifiable from the base snapshot or from HEAD — that is what holds a
    deletion's acknowledgment hash steady across the transaction that deleted
    it. Live symlinks and special files have no content identity.
    """
    base_image = base_snapshot.image(raw_target) if base_snapshot is not None else None
    path = _safe_relative(vault_root, outcome.target, outcome.target_kind)
    if path is None:
        data = (
            base_image.data
            if base_image is not None and base_image.kind == "file"
            else None
        )
        if data is None:
            return None
        if raw_target.endswith(b".md"):
            data = _note_bytes(data)
        return hashlib.sha256(data).hexdigest()[:16]
    live_target = gitstate.live_image(Path(vault_root), raw_target)
    if live_target is not None and live_target.kind in {"symlink", "special"}:
        return None
    if outcome.check == "append-only":
        data = _append_only_basis(vault_root, raw_target, base_snapshot)
    elif path.is_file():
        data = path.read_bytes()
        if path.suffix == ".md":
            data = _note_bytes(data)
    elif path.is_dir():
        data = _directory_bytes(path)
    else:
        data = (
            base_image.data
            if base_image is not None and base_image.kind == "file"
            else gitstate.blob_bytes(vault_root, "HEAD", raw_target)
            if base_snapshot is None
            else b""
        ) or b""
        if raw_target.endswith(b".md"):
            data = _note_bytes(data)
    return hashlib.sha256(data).hexdigest()[:16] if data is not None else None


def _repo_path_hash(vault_root, outcome, *, base_snapshot, candidate_snapshot):
    """The identity of a repo-path target, from whichever plane is authoritative.

    A candidate snapshot, when the caller supplied one, IS the vault as far as
    this hash is concerned: reading the worktree instead would let a concurrent
    edit leak into an identity the transaction has already fixed.
    """
    raw_target = decode_repo_path(outcome.target)
    if candidate_snapshot is not None:
        return _snapshot_path_hash(
            vault_root, outcome, raw_target, base_snapshot, candidate_snapshot
        )
    return _worktree_path_hash(vault_root, outcome, raw_target, base_snapshot)


def _identifier_hash(
    vault_root,
    target,
    bibliography_universe,
    raw_origin,
    origin,
    origin_image,
    *,
    base_snapshot,
    candidate_snapshot,
):
    """The identity of a bare identifier: its note where one exists, else its entry.

    A note is preferred over a bibliography entry wherever the identifier has
    one — its validly-shaped ``managed-sha256`` first, then candidate image,
    worktree, base image or HEAD — so an identifier and the note carrying it
    never disagree about what was acknowledged. A note whose witness is absent
    or not digest-shaped falls through the same as one with none recorded.
    Only an identifier with no note at all falls through to the canonical
    bibliography record.
    """
    known_citation_key_hash = _citation_key_hash(
        vault_root, target, candidate_snapshot=candidate_snapshot
    )
    if known_citation_key_hash is not None:
        return known_citation_key_hash
    if origin_image is not None and origin_image.kind == "file":
        data = _note_bytes(origin_image.data or b"")
        return hashlib.sha256(data).hexdigest()[:16]
    if origin and origin.is_file():
        data = _note_bytes(origin.read_bytes())
        return hashlib.sha256(data).hexdigest()[:16]
    if raw_origin is not None:
        base_image = (
            base_snapshot.image(raw_origin) if base_snapshot is not None else None
        )
        # Named apart from the `data: bytes` above, as in _claim_anchor_hash:
        # this is the pre-transaction note, and it may legitimately be absent.
        head = (
            base_image.data
            if base_image is not None and base_image.kind == "file"
            else gitstate.blob_bytes(vault_root, "HEAD", raw_origin)
            if base_snapshot is None
            else None
        )
        if head is not None:
            return hashlib.sha256(_note_bytes(head)).hexdigest()[:16]
    if bibliography_universe is _OMITTED_BIBLIOGRAPHY:
        entry = bibliography.load(vault_root).get(target)
    elif bibliography_universe is not None:
        entry = bibliography_universe.get(target)
    else:
        entry = None
    if entry is not None:
        data = json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(data).hexdigest()[:16]
    return None


def _target_hash(
    vault_root,
    outcome,
    bibliography_universe=_OMITTED_BIBLIOGRAPHY,
    *,
    base_snapshot=None,
    candidate_snapshot=None,
):
    """Return the stable, kind-aware acknowledgment hash for an outcome.

    Three identities, tried in the order they nest. A claim anchor is the
    narrowest and the only one that falls through — when no plane still holds
    the claim, the outcome is still identifiable by the note or identifier it
    came from. A repo path is answered entirely by its plane. A bare identifier
    is answered by its note or its bibliography entry.

    The claim origin is resolved up front, for every kind: ``decode_repo_path``
    and ``_extra_path`` reject a malformed ``note_path``, and that rejection is
    part of the contract regardless of which leg would have run.
    """
    target = outcome.target
    raw_origin = (
        decode_repo_path(outcome.extra["note_path"])
        if "note_path" in outcome.path_extra_fields
        else None
    )
    origin_image = (
        candidate_snapshot.image(raw_origin)
        if candidate_snapshot is not None and raw_origin is not None
        else None
    )
    origin = (
        None
        if candidate_snapshot is not None
        else _extra_path(vault_root, outcome, "note_path")
    )
    if isinstance(target, str) and "#^" in target:
        anchored = _claim_anchor_hash(
            vault_root,
            target,
            raw_origin,
            origin,
            origin_image,
            base_snapshot=base_snapshot,
            candidate_snapshot=candidate_snapshot,
        )
        if anchored is not None:
            return anchored

    if outcome.target_kind == "repo-path":
        return _repo_path_hash(
            vault_root,
            outcome,
            base_snapshot=base_snapshot,
            candidate_snapshot=candidate_snapshot,
        )

    if isinstance(target, str):
        return _identifier_hash(
            vault_root,
            target,
            bibliography_universe,
            raw_origin,
            origin,
            origin_image,
            base_snapshot=base_snapshot,
            candidate_snapshot=candidate_snapshot,
        )
    return None


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


def _mutate_marker(vault_root, outcome, date, *, clear=False):
    if outcome.check not in CLOSING_CHECKS:
        return
    for relative, claim_id, line_no in _origins(outcome):
        path = _safe_relative(vault_root, relative, "repo-path")
        if path is None or not path.is_file():
            continue
        if path.relative_to(Path(vault_root)).parts[0] == "wiki":
            # The compiled layer is the tool's write scope (ingest spec §4.4):
            # verify reads it and never writes into it.
            continue
        lines = _read_note_text(path).splitlines(keepends=True)
        for index, line in enumerate(lines):
            content, ending = _split_line_ending(line)
            anchor = _terminal_anchor_match(content, claim_id)
            anchored = anchor is not None
            numbered = isinstance(line_no, int) and index == line_no - 1
            if not anchored and not numbered:
                continue
            terminal_claim_id = claim_id if anchored else None
            pattern = _terminal_marker_pattern(outcome.check, terminal_claim_id)
            replacement = (
                pattern.sub(" " if isinstance(terminal_claim_id, str) else "", content)
                if clear
                else line
            )
            if not clear and pattern.search(content) is None:
                if anchored:
                    before = content[: anchor.start()]
                    terminal_anchor = content[anchor.start() :]
                    replacement = (
                        before
                        + f"[failed-verification:: {outcome.check}/{date}] "
                        + terminal_anchor
                    )
                else:
                    replacement = (
                        content + f" [failed-verification:: {outcome.check}/{date}]"
                    )
                replacement += ending
            elif clear:
                replacement += ending
            if replacement != line:
                lines[index] = replacement
                _write_note_text(path, "".join(lines))
            break


def _cites(content, citation_key):
    """Whether a line cites exactly ``citation_key`` (never a longer key)."""
    return any(
        match.group("key") == citation_key for match in claims.CITE_RE.finditer(content)
    )


def _claim_notes(vault: Path) -> list[Path]:
    """The notes ``_plan_state`` scans for claim lines, minus the compiled layer."""
    return sorted((vault / "projects").rglob("*.md")) + sorted(
        (vault / "literatures").glob("*.md")
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
    are ``projects/**/*.md`` and ``literatures/*.md``: ``_plan_state`` scans
    both for claim lines, and a capture-rendered literature note matches
    nothing only because it carries none — a hand-authored one does receive
    markers. Anything under ``wiki/`` is skipped, mirroring the writer's own
    guard (ingest spec §4.4). Returns whether a marker was removed.
    """
    # The root exactly as `gitstate._absolute` builds a `path-bytes:` candidate
    # from it (abspath, not resolve: no symlink is followed), so the two meet
    # in the `wiki/` guard when `cmd_ack` was handed `--vault .`.
    vault = Path(os.fsdecode(gitstate._root_bytes(Path(vault_root))))
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
    cleared = False
    for path in candidates:
        if path is None or not path.is_file():
            continue
        if path.relative_to(vault).parts[0] == "wiki":
            # The compiled layer is the tool's write scope (ingest spec §4.4):
            # verify never writes a marker there, so there is none to clear.
            continue
        lines = _read_note_text(path).splitlines(keepends=True)
        changed = False
        for index, line in enumerate(lines):
            content, ending = _split_line_ending(line)
            if claim_id is not None:
                if _terminal_anchor_match(content, claim_id) is None:
                    continue
                terminal_claim_id: str | None = claim_id
            elif citation_key is not None:
                if not _cites(content, citation_key):
                    continue
                # The writer put the marker before the citing line's own
                # anchor when it has one, after the line otherwise.
                anchor = claims.ANCHOR_RE.search(content)
                terminal_claim_id = anchor.group("id") if anchor else None
            else:
                terminal_claim_id = None
            # `_mutate_marker`'s clear substitution: the pattern's lookahead keeps
            # the anchor, and the single space closes the gap the marker left.
            pattern = _terminal_marker_pattern(check, terminal_claim_id)
            replacement = pattern.sub(
                " " if isinstance(terminal_claim_id, str) else "", content
            )
            if replacement != content:
                lines[index] = replacement + ending
                changed = True
        if changed:
            _write_note_text(path, "".join(lines))
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


def file_outcomes(vault_root, path, bibliography_universe=None):
    outcomes = quotes.check_all_quotes(vault_root, path) + lints.lint_disputed_claim(
        vault_root, path
    )
    if bibliography_universe is not None:
        outcomes = (
            checks.check_citation_keys(vault_root, path, bibliography_universe)
            + outcomes
        )
    return outcomes


def _bibliography_entries(bib):
    return [bib[citation_key] for citation_key in sorted(bib)]


def _network_outcomes(vault_root, entry, detection_date, notice_lookup):
    """Produce one reduced update-notice outcome for a bibliography entry."""
    if entry.get("_discovery_unreachable") and not (
        entry.get("DOI") or entry.get("doi")
    ):
        live = checks.Outcome(
            "update-notice",
            entry["id"],
            Result.UNREACHABLE,
            "outage — identifier discovery unavailable",
        )
    else:
        live = checks.check_update_notice(vault_root, entry, detection_date)
    rw_leg = (
        checks.check_rw_batch(entry, notice_lookup, detection_date)
        if notice_lookup is not None
        else None
    )
    reduced = checks.reduce_update_notice_outcomes(live, rw_leg)
    return [reduced] if reduced is not None else []


def _offline_network_outcomes(entry, detection_date, notice_lookup):
    rw_leg = (
        checks.check_rw_batch(entry, notice_lookup, detection_date)
        if notice_lookup is not None
        else None
    )
    if rw_leg is not None:
        return [rw_leg]
    return [
        checks.Outcome(
            "update-notice",
            entry["id"],
            Result.UNREACHABLE,
            "outage — network disabled",
            {"synthetic_offline": True},
        )
    ]


# The annotation pins the ARITY (exactly three), which is what the splat at the
# is_acknowledged call site needs; the element types stay Any because they are read
# straight off the JSON extra mapping and nothing here verifies them. Claiming
# `str | None` would be asserted, not verified.
def _notice_fingerprint(outcome) -> tuple[Any, Any, Any]:
    if outcome.check != "update-notice":
        return None, None, None
    return (
        outcome.extra.get("class"),
        outcome.extra.get("type"),
        outcome.extra.get("notice_date"),
    )


def _effective(outcomes, hashes, vault_root):
    return [
        outcome
        for outcome in outcomes
        if outcome.result is Result.MATCHED
        or not inbox.is_acknowledged(
            vault_root,
            outcome.check,
            outcome.target,
            hashes[id(outcome)],
            *_notice_fingerprint(outcome),
            target_kind=outcome.target_kind,
        )
    ]


def _projection_identity(outcome):
    if outcome.check == "update-notice":
        return outcome.target, outcome.check
    if outcome.check == "quote" and isinstance(outcome.target, str):
        comparison_target = outcome.extra.get("target", "managed-region")
        if (
            "#^" in outcome.target
            and isinstance(comparison_target, str)
            and comparison_target
        ):
            citation_key = outcome.target.split("#^", 1)[0]
            return citation_key, f"quote:{outcome.target}:{comparison_target}"
    return None


def _apply_state_transitions(vault_root, raw, detection_date, *, stamp):
    """Project raw current state after the candidate-bound decision is frozen.

    ``stamp`` is the effective set. A ``[failed-verification:: <check>/<date>]``
    marker means a raw failure no person has acknowledged, standing beside the
    inbox row it mirrors — both closed by the same ack (open point 09), both
    reopened when the ack lapses on a content-hash change — so only an outcome
    still effective is stamped. The note's verified event and failure row and
    the MATCHED clear run over every raw outcome as before.
    """
    stamp_ids = {id(outcome) for outcome in stamp}
    for outcome in raw:
        projection = _projection_identity(outcome)
        if projection is not None:
            citation_key, check = projection
            note = _note_for_citation_key(vault_root, citation_key)
            if note and note.is_file():
                try:
                    text = _read_note_text(note)
                    updated = (
                        events.record_pass(
                            text,
                            check,
                            Result.MATCHED,
                            at=detection_date,
                        )
                        if outcome.result is Result.MATCHED
                        else events.record_failure(text, check, outcome.result)
                    )
                except (
                    OSError,
                    UnicodeError,
                    ValueError,
                    frontmatter.FrontmatterError,
                ):
                    pass
                else:
                    if updated != text:
                        _write_note_text(note, updated)
        if outcome.result is Result.UNMATCHED:
            if id(outcome) in stamp_ids:
                _mutate_marker(vault_root, outcome, detection_date)
        elif outcome.result is Result.MATCHED:
            _mutate_marker(vault_root, outcome, detection_date, clear=True)


def _warning_effectiveness(outcomes, hashes, vault_root):
    frozen: dict[object, bool] = {}
    for outcome in outcomes:
        statuses = []
        for index, warning in enumerate(outcome.extra.get("warn_notices", [])):
            warning_type = warning.get("type") if isinstance(warning, Mapping) else None
            notice_date = (
                warning.get("notice_date") if isinstance(warning, Mapping) else None
            )
            effective = isinstance(warning_type, str) and not inbox.is_acknowledged(
                vault_root,
                outcome.check,
                outcome.target,
                hashes[id(outcome)],
                "warn",
                warning_type,
                notice_date,
                target_kind=outcome.target_kind,
            )
            frozen[(id(outcome), index)] = effective
            statuses.append(effective)
        frozen[id(outcome)] = any(statuses)
    return frozen


def _file_effects(vault_root, effective, hashes, warning_effective, detection_date):
    """File findings from the frozen candidate-bound decision state."""
    open_keys = set()
    for entry in inbox.open_entries(vault_root):
        open_keys.add(
            (
                entry.check,
                entry.target,
                entry.target_kind,
                entry.result,
                entry.target_hash,
                entry.notice_class,
                entry.notice_type,
                entry.notice_date,
            )
        )
    for outcome in effective:
        target_hash = hashes[id(outcome)]
        if outcome.result is not Result.MATCHED:
            notice_class, notice_type, notice_date = _notice_fingerprint(outcome)
            key = (
                outcome.check,
                outcome.target,
                outcome.target_kind,
                outcome.result.value,
                target_hash,
                notice_class,
                notice_type,
                notice_date,
            )
            if key not in open_keys:
                inbox.append_entry(
                    vault_root,
                    outcome.check,
                    outcome.target,
                    outcome.result,
                    outcome.reason,
                    date=detection_date,
                    target_hash=target_hash,
                    notice_class=notice_class,
                    notice_type=notice_type,
                    notice_date=notice_date,
                    detection_date=(
                        outcome.extra.get("detection_date", detection_date)
                        if notice_class is not None
                        else None
                    ),
                    target_kind=outcome.target_kind,
                )
                open_keys.add(key)
        for index, warning in enumerate(outcome.extra.get("warn_notices", [])):
            if not warning_effective[(id(outcome), index)]:
                continue
            warning_type = warning.get("type")
            if not isinstance(warning_type, str):
                continue
            notice_date = warning.get("notice_date")
            key = (
                outcome.check,
                outcome.target,
                outcome.target_kind,
                Result.UNMATCHED.value,
                target_hash,
                "warn",
                warning_type,
                notice_date,
            )
            if key not in open_keys:
                inbox.append_entry(
                    vault_root,
                    outcome.check,
                    outcome.target,
                    Result.UNMATCHED,
                    f"warn-notice — {warning_type}",
                    date=detection_date,
                    target_hash=target_hash,
                    notice_class="warn",
                    notice_type=warning_type,
                    notice_date=notice_date,
                    detection_date=warning.get("detection_date", detection_date),
                    target_kind=outcome.target_kind,
                )
                open_keys.add(key)


def _plan_state(
    vault_root,
    network=True,
    detection_date=None,
    rw_csv=None,
    base=DEFAULT_BASE,
    *,
    repository_root=None,
    snapshots,
):
    """Compute one complete projection inside a materialized candidate.

    ``base`` is the Zotero base URL the lifecycle leg reads (ingest spec
    §3.4); ``verify_state`` forwards it positionally.
    """
    vault = Path(vault_root)
    repository = Path(repository_root) if repository_root is not None else vault
    detection_date = detection_date or clock.today()
    raw = []
    try:
        bibliography_universe = bibliography.load(vault)
    except bibliography.BibliographyError as error:
        bibliography_universe = None
        reason = (
            "schema-violation — bibliography JSON/schema invalid"
            if error.result is Result.UNMATCHED
            else "outage — bibliography unreadable"
        )
        raw.append(
            checks.Outcome(
                "citation-key",
                RepoPath(os.fsencode(bibliography.BIB_PATH)),
                error.result,
                reason,
            )
        )
    note_files = [
        path
        for folder in ("literatures", "wiki", "projects")
        for path in sorted((vault / folder).rglob("*.md"))
    ]
    for path in note_files:
        raw.extend(file_outcomes(vault, path, bibliography_universe))
    for path in sorted(vault.rglob("*.md")):
        if structure.is_excluded(path, vault):
            continue
        if path.name == "index.md" or path.name == "log.md":
            continue
        raw.extend(structure.check_note_frontmatter(vault, path))
    raw.extend(structure.check_reserved(vault))
    raw.append(structure.check_tree(vault))
    if network:
        raw.extend(lifecycle.lint_lifecycle(vault, ZoteroClient(base=base)))
    else:
        raw.append(
            checks.Outcome(
                "lifecycle",
                "vault",
                Result.UNREACHABLE,
                "outage — network disabled",
                {"synthetic_offline": True},
            )
        )
    # `cmd_verify` mirrors this same falsy-rw_csv predicate to print the
    # unarmed-RW-leg stdout line.
    notice_lookup = checks.load_rw_csv(rw_csv) if rw_csv else None
    entries = (
        _bibliography_entries(bibliography_universe)
        if bibliography_universe is not None
        else []
    )
    for original in entries:
        entry = dict(original)
        if network and not (entry.get("DOI") or entry.get("doi")):
            discovery = identify.discover(vault, entry)
            raw.append(discovery)
            identifiers = discovery.extra.get("identifiers", {})
            if isinstance(identifiers, Mapping):
                entry.update(identifiers)
            entry["_discovery_unreachable"] = discovery.result is Result.UNREACHABLE
        if network:
            raw.extend(_network_outcomes(vault, entry, detection_date, notice_lookup))
        else:
            raw.extend(_offline_network_outcomes(entry, detection_date, notice_lookup))
    base_snapshot = snapshots.base
    candidate_snapshot = snapshots.candidate
    raw.extend(lints.lint_evidence_layer(base_snapshot, candidate_snapshot))
    raw.extend(lints.lint_append_only(repository, base_snapshot, candidate_snapshot))
    raw.extend(
        lints.lint_claim_immutability(repository, base_snapshot, candidate_snapshot)
    )
    raw.extend(lints.lint_published_drift(repository, candidate_snapshot))
    raw.extend(propagate.lint_propagation(vault))
    raw.extend(captured.lint_captured_set(vault, as_of=detection_date))
    authoritative = [
        outcome for outcome in raw if outcome.extra.get("synthetic_offline") is not True
    ]
    hashes = {
        id(outcome): _target_hash(
            vault,
            outcome,
            bibliography_universe,
            base_snapshot=base_snapshot,
            candidate_snapshot=candidate_snapshot,
        )
        for outcome in authoritative
    }
    effective = _effective(authoritative, hashes, vault)
    warning_effective = _warning_effectiveness(authoritative, hashes, vault)
    _apply_state_transitions(vault, authoritative, detection_date, stamp=effective)
    _file_effects(vault, effective, hashes, warning_effective, detection_date)
    counts: dict[str, int] = {}
    for outcome in effective:
        counts[outcome.result.value] = counts.get(outcome.result.value, 0) + 1
    return {"outcomes": raw, "counts": counts}, effective, hashes, warning_effective


def _candidate_destinations_match_live(snapshots, outputs):
    if snapshots.candidate_name == "worktree":
        return
    for output in outputs:
        if snapshots.candidate.image(output.raw_path) != snapshots.live.image(
            output.raw_path
        ):
            raise gitstate.GitStateError(
                "selected candidate differs from live projection destination: "
                f"{encode_repo_path(output.raw_path)}"
            )


def _rollback_prepublication(vault, snapshots, outputs, primary):
    try:
        gitstate.rollback_outputs(vault, snapshots.live, outputs)
    except gitstate.GitStateError as rollback:
        raise gitstate.GitStateError(f"{primary}; {rollback}") from primary
    raise primary


def verify_state(
    vault_root,
    network=True,
    detection_date=None,
    rw_csv=None,
    base=DEFAULT_BASE,
    *,
    git_base=None,
    git_candidate="worktree",
    changed_paths_file=None,
    commit_projected=None,
):
    """Run one immutable collect/plan/apply/manifest/publication transaction."""
    vault = Path(vault_root)
    resolved_manifest = (
        gitstate.validate_manifest_destination(vault, Path(changed_paths_file))
        if changed_paths_file is not None
        else None
    )
    snapshots = gitstate.resolve_snapshots(
        vault, git_base=git_base, candidate=git_candidate
    )
    with tempfile.TemporaryDirectory(
        prefix="research-vault-verification-plan-"
    ) as temporary:
        planning = Path(temporary)
        gitstate.materialize_snapshot(snapshots.candidate, planning)
        report, effective, hashes, warning_effective = _plan_state(
            planning,
            network,
            detection_date,
            rw_csv,
            base,
            repository_root=vault,
            snapshots=snapshots,
        )
        planned_snapshot = gitstate.restore_candidate_nonfiles(
            snapshots.candidate, gitstate.snapshot_worktree(planning)
        )
        outputs = gitstate.outputs_between(snapshots.candidate, planned_snapshot)
    outputs = gitstate.validate_planned_outputs(outputs)
    _candidate_destinations_match_live(snapshots, outputs)
    if commit_projected is not None:
        gitstate.validate_dirty_overlap(vault, snapshots, outputs)
    gitstate.apply_outputs(vault, snapshots.live, outputs)
    captured = outputs
    if resolved_manifest is not None:
        try:
            captured = gitstate.audit_and_write_manifest(
                vault,
                snapshots.live,
                outputs,
                resolved_manifest,
            )
        except gitstate.GitStateError as error:
            _rollback_prepublication(vault, snapshots, outputs, error)
    if commit_projected is not None:
        gitstate.publish_outputs(vault, snapshots, captured, commit_projected)
    return report, effective, hashes, warning_effective


def surface_decision(surface, effective, warning_effective):
    """Return the shared exit decision and rendered blockers for one surface."""
    closing = CLOSING_BY_SURFACE[surface]
    blockers = []
    genuine = [
        outcome
        for outcome in effective
        if outcome.extra.get("synthetic_offline") is not True
    ]
    for outcome in genuine:
        if outcome.result is Result.UNMATCHED and outcome.check in closing:
            blockers.append(
                f"UNMATCHED {outcome.check} {outcome.target} — {outcome.reason}"
            )
        for index, warning in enumerate(outcome.extra.get("warn_notices", ())):
            if outcome.check not in closing or not warning_effective.get(
                (id(outcome), index), warning_effective.get(id(outcome), False)
            ):
                continue
            warning_type = warning.get("type") if isinstance(warning, Mapping) else None
            if isinstance(warning_type, str):
                blockers.append(
                    f"UNMATCHED {outcome.check} {outcome.target} — "
                    f"warn-notice — {warning_type}"
                )
    if blockers:
        return 1, tuple(blockers)
    if surface == "audit":
        return 0, ()
    unreachable = [
        f"UNREACHABLE {outcome.check} {outcome.target} — {outcome.reason}"
        for outcome in genuine
        if outcome.result is Result.UNREACHABLE
    ]
    return (3, tuple(unreachable)) if unreachable else (0, ())
