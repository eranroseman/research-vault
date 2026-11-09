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
    clock,
    events,
    frontmatter,
    gitstate,
    identify,
    inbox,
    lifecycle,
    lints,
    literature_notes,
    propagate,
    quotes,
    structure,
)
from .markers import (
    _mutate_marker,
    _read_note_text,
    _safe_relative,
    _split_line_ending,
    _terminal_anchor_match,
    _without_own_marks,
    _write_note_text,
)
from .pathcodec import (
    RepoPath,
    decode_repo_path,
    encode_repo_path,
)
from .zotero import DEFAULT_BASE, ZoteroClient  # DEFAULT_BASE re-exported for the CLI

_OMITTED_BIBLIOGRAPHY = object()


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
            "dead-link",
            "capture-monitor",
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
            "dead-link",
            "capture-monitor",
        }
    ),
}
CLOSING_CHECKS = frozenset().union(*CLOSING_BY_SURFACE.values())


def _extra_path(vault_root, outcome, key):
    if key not in outcome.path_extra_fields:
        return None
    return _safe_relative(vault_root, outcome.extra.get(key), "repo-path")


def _note_bytes(data: bytes) -> bytes:
    """A note's scope bytes: verifier events and verify's own marks excluded."""
    text = literature_notes.canonical_content(data.decode(errors="surrogateescape"))
    return _without_own_marks(text).encode(errors="surrogateescape")


def _claim_bytes_from_text(text, claim_id):
    """Hash one anchored claim and its continuations, ignoring our marker."""
    lines = literature_notes.canonical_content(text).splitlines(keepends=True)
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
        candidate = literature_notes.note_path(vault, citation_key)
        raw_path = os.fsencode(candidate.relative_to(vault))
    except literature_notes.InvalidCitationKeyError:
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
            candidate = literature_notes.note_path(Path(vault_root), citation_key)
            raw_path = os.fsencode(candidate.relative_to(vault_root))
        except (literature_notes.InvalidCitationKeyError, ValueError):
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


def _with_reason(data: bytes, outcome, _candidate_image, _base_snapshot) -> bytes:
    return data + b"\x00" + outcome.reason.encode("utf-8")


def _verifier_lists_bytes(image) -> bytes:
    """#206's ack basis: what the lists hold that verify does not itself write.

    A verify run appends `verified` events and rewrites `failed-verification`
    rows in the candidate it plans over, so hashing the lists whole would
    change the hash between the run that raises a row and the run after the
    ack, and the ack would never hold. Verify's own events (machine-class `by`)
    and the verify-owned failure rows are therefore left out; what remains is
    the lists' hand-written content, canonical JSON.
    """
    data: dict = {}
    if image is not None and image.kind == "file":
        try:
            data, _ = frontmatter.parse(
                (image.data or b"").decode(errors="surrogateescape")
            )
        except frontmatter.FrontmatterError:
            data = {}
    parsed, malformed = events._verified_events(data)
    written = [
        event
        for event in parsed
        if not str(event["by"]).startswith(lints._MACHINE_ACTOR_PREFIX)
    ]
    return json.dumps(
        {"verified": written, "malformed": malformed}, sort_keys=True, default=str
    ).encode("utf-8")


def _lists_with_reason(_data: bytes, outcome, candidate_image, base_snapshot) -> bytes:
    """The base's tree oid, the person's additions in the candidate, and the
    row's reason. The base of a verify run is always a tree snapshot (an unborn
    HEAD's is the empty tree); one that is not has no oid to stand on."""
    tree = base_snapshot.tree if base_snapshot is not None else None
    if tree is None:
        raise TypeError(
            "a verifier-list row's hash needs a base snapshot read from a tree"
        )
    basis = tree.encode("ascii") + b"\x00" + _verifier_lists_bytes(candidate_image)
    return _with_reason(basis, outcome, candidate_image, base_snapshot)


# An outcome's `extra["hash_basis"]` names what its repo-path hash covers
# beyond the target's bytes; each basis is called `(data, outcome,
# candidate_image, base_snapshot)`. Several rows on one note would otherwise
# share one hash, so `_file_effects` would file the first and one ack would
# accept all.
# - `lints.MONITOR_ROW` ("monitor-row"): the note's bytes plus the row's reason;
#   each capture-monitor row is its own record, and any byte change still
#   lapses its ack (ruling P4).
# - `lints.VERIFIER_LISTS` ("verifier-lists"): on the committed tree, the
#   person's additions and the removed entry, not the note's bytes (which
#   exclude the lists): the base snapshot's tree oid (the empty tree's when the
#   base is the empty tree), the candidate's hand-written `verified` events
#   (`_verifier_lists_bytes`), and the row's reason. An ack covers that row; a
#   later well-formed list edit by a person, or a repeat removal after any
#   commit, changes the hash and raises it again (#206, rulings P13, P14, P15,
#   R16 and R17). The tree oid, not the commit id: two commits with the same
#   tree hash the same. Accepted cost (R26): an acked removal is raised again
#   wherever its base moves. Left uncommitted while other files are committed,
#   it is raised after that commit; carried by a commit a history rewrite gives
#   a new parent (a rebase onto a moved main, a squash or rebase merge, a
#   cherry-pick, an amend, a conflicted merge concluded at the hook), it is
#   raised again on the rewritten commit. Each takes a second ack. The hook's
#   path (removal and ack in one commit) is rewrite-free only while that
#   commit is never rewritten.
_HASH_BASES = {
    lints.MONITOR_ROW: _with_reason,
    lints.VERIFIER_LISTS: _lists_with_reason,
}


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
    basis = _HASH_BASES.get(outcome.extra.get("hash_basis"))
    if basis is not None:
        data = basis(data, outcome, candidate_image, base_snapshot)
    return hashlib.sha256(data).hexdigest()[:16]


def _repo_path_hash(vault_root, outcome, *, base_snapshot, candidate_snapshot):
    """The identity of a repo-path target, from the candidate snapshot.

    A candidate snapshot IS the vault as far as this hash is concerned:
    reading the worktree instead would let a concurrent edit leak into an
    identity the transaction has already fixed. The one production caller
    always supplies one; a missing snapshot is a caller bug, not a plane.
    """
    if candidate_snapshot is None:
        raise TypeError("a repo-path target's hash needs candidate_snapshot")
    raw_target = decode_repo_path(outcome.target)
    return _snapshot_path_hash(
        vault_root, outcome, raw_target, base_snapshot, candidate_snapshot
    )


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
                            once=True,
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
        if outcome.check not in CLOSING_CHECKS:
            continue
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


def _filing_key(outcome, target_hash):
    """The identity one review-queue record files an outcome under: two
    outcomes with the same key are one record and one ack."""
    return (
        outcome.check,
        outcome.target,
        outcome.target_kind,
        outcome.result.value,
        target_hash,
        *_notice_fingerprint(outcome),
    )


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
            key = _filing_key(outcome, target_hash)
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


# The re-check's sentinel for "every commit HEAD reaches" (`verify
# --recheck-commits all`, and publish before a project's first publication).
WHOLE_HISTORY = object()


# The two-version lints, the ones that compare a base and a candidate snapshot:
# the worktree leg runs them once, and the per-commit re-check (spec §5.3.1,
# Q2) runs them for every commit against its parent. `lint_evidence_layer`
# also yields Task 4's `capture-monitor` rows and Task 7's verifier-list rows.
# Each lint is reached through `lints` at call time, so one patched in a test
# is the one that runs.
def _evidence_layer(_repository, base_snapshot, candidate_snapshot):
    return lints.lint_evidence_layer(base_snapshot, candidate_snapshot)


def _append_only(repository, base_snapshot, candidate_snapshot):
    return lints.lint_append_only(repository, base_snapshot, candidate_snapshot)


def _claim_immutability(repository, base_snapshot, candidate_snapshot):
    return lints.lint_claim_immutability(repository, base_snapshot, candidate_snapshot)


_HISTORY_LINTS = {
    "evidence-layer": _evidence_layer,
    "append-only": _append_only,
    "claim-immutability": _claim_immutability,
}
HISTORY_CHECKS = tuple(_HISTORY_LINTS)

# Ruling R18: the verifier-list rows hash on the base's tree, so they are
# per-commit rows, computed only where the base is the candidate's parent. A
# range leg over more than one commit leaves them to the re-check, and says so
# once whenever no re-check covers its range (P34), rather than dropping them
# in silence.
LIST_ROWS_NOTICE = (
    "evidence-layer: verifier-list rows are per-commit and this range spans "
    "more than one commit; they need --recheck-commits from the range's base, "
    "over the committed HEAD"
)


def _history_lints(repository, base_snapshot, candidate_snapshot):
    """The `HISTORY_CHECKS` lints over one base and candidate."""
    return [
        outcome
        for check in HISTORY_CHECKS
        for outcome in _HISTORY_LINTS[check](
            repository, base_snapshot, candidate_snapshot
        )
    ]


def _stamped(outcome, commit):
    """The outcome again, its `extra` carrying the commit that raised it. An
    `Outcome` stores its repo paths encoded, so they are decoded back into
    `RepoPath`s to keep their kind (the target's and `note_path`'s)."""
    target = outcome.target
    if outcome.target_kind == "repo-path":
        target = RepoPath(decode_repo_path(target))
    extra = {
        key: RepoPath(decode_repo_path(value))
        if key in outcome.path_extra_fields
        else value
        for key, value in outcome.extra.items()
    }
    return checks.Outcome(
        outcome.check,
        target,
        outcome.result,
        outcome.reason,
        {**extra, "commit": commit},
    )


def _row_path(outcome):
    """The file a two-version row is about: its target, or a claim's note."""
    if outcome.target_kind == "repo-path":
        return decode_repo_path(outcome.target)
    if "note_path" in outcome.path_extra_fields:
        return decode_repo_path(outcome.extra["note_path"])
    return None


def _unmatched(repository, base_snapshot, candidate_snapshot):
    """The two-version lints' UNMATCHED rows, keyed by check, target, reason."""
    return {
        (outcome.check, outcome.target, outcome.reason): outcome
        for outcome in _history_lints(repository, base_snapshot, candidate_snapshot)
        if outcome.result is Result.UNMATCHED
    }


def _holders(outcome, bases):
    """The parents a merge row must be raised against: those that hold its
    path. None may: then the path is wholly the merge's, nothing arrived from
    a side, and a row raised against any parent stands (a hand rename at the
    merge reads `renamed` against one side and as an attested add against the
    other). A row that names no path is held by every parent."""
    raw_path = _row_path(outcome)
    if raw_path is None:
        return range(len(bases))
    return [
        index for index, base in enumerate(bases) if base.image(raw_path) is not None
    ]


def _commit_rows(repository, commit, bases, candidate, *, hasher, own_rows):
    """One commit's rows, each with the base it was raised against.

    A merge reads as `git diff --cc` does (rulings P28, P31): a change that
    arrived from exactly one side was judged at that side's own commit, which
    the replay visits, and re-raising it at the merge under the merged bytes
    would only break the acks filed there. A change the merge itself made
    shows against every parent that holds the path, and it stays. So a merge
    row is kept when it is raised against every parent holding its path (a
    parent lacking the path stands aside; when none holds it, the path is the
    merge's own and a row against any parent stands); a single-parent commit
    keeps every row that test leaves.

    A row is new at a commit, or it is not raised there (ruling P33): one a
    parent's own tree already raises on the same bytes (the same check,
    target, reason and hash) arrived from that parent, so a stale witness a
    commit leaves untouched stays the commit's that wrote it. A merge that
    rewrites a note's bytes lapses that note's acks as any edit does. Each
    kept finding is one row, not one per parent. ``hasher(outcome, base,
    candidate)`` is the row's acknowledgment hash; ``own_rows(snapshot)`` is
    that tree's own rows (`_unmatched` against itself) with their hashes."""
    raised = [_unmatched(repository, base, candidate) for base in bases]

    def inherited(key, outcome, base):
        digest = hasher(outcome, base, candidate)
        return any(
            key in own_rows(parent) and own_rows(parent)[key] == digest
            for parent in bases
        )

    rows = []
    kept = set()
    for base, by_key in zip(bases, raised, strict=True):
        for key, outcome in by_key.items():
            if key in kept:
                continue
            if all(
                key in raised[index] for index in _holders(outcome, bases)
            ) and not inherited(key, outcome, base):
                kept.add(key)
                rows.append((_stamped(outcome, commit), base, candidate))
    return rows


def _history_outcomes(repository, base_ref, hasher):
    """Every commit since ``base_ref`` against its parents, oldest first:
    ``(outcome, base snapshot, candidate snapshot)``, each outcome's `extra`
    naming its commit. A root commit's parent is the empty tree.

    The lints read whole trees, as the pre-commit hook does (ruling R20): a
    row can depend on a path the commit did not touch. A commit with at most
    one parent whose tree equals that parent's changed nothing and is
    skipped; a merge always runs, since `-s ours` keeps one side's tree and
    still drops the other's changes (P31). Each tree is read once, each blob
    once across them, and a tree's own rows are linted only when a commit on
    top of it raised something (`_commit_rows`)."""
    snapshots: dict[str, gitstate.Snapshot] = {}
    blobs: dict[bytes, bytes] = {}
    own: dict[str | None, dict] = {}

    def snapshot(revision):
        if revision not in snapshots:
            snapshots[revision] = gitstate.snapshot_tree(repository, revision, blobs)
        return snapshots[revision]

    def own_rows(tree_snapshot):
        # A tree's own rows have no base: linted against itself, a tree raises
        # only candidate-only rows, whose hashes read the candidate alone (P57).
        if tree_snapshot.tree not in own:
            own[tree_snapshot.tree] = {
                key: hasher(outcome, None, tree_snapshot)
                for key, outcome in _unmatched(
                    repository, tree_snapshot, tree_snapshot
                ).items()
            }
        return own[tree_snapshot.tree]

    rows = []
    for commit, parents in gitstate.commit_parents(
        repository, None if base_ref is WHOLE_HISTORY else base_ref
    ):
        candidate = snapshot(commit)
        bases = [snapshot(parent) for parent in parents] or [
            snapshot(gitstate._empty_tree(repository))
        ]
        if len(bases) == 1 and bases[0].tree == candidate.tree:
            continue
        rows.extend(
            _commit_rows(
                repository, commit, bases, candidate, hasher=hasher, own_rows=own_rows
            )
        )
    return rows


def _two_version_rows(repository, snapshots, recheck_commits, *, git_base, hasher):
    """The worktree leg's two-version rows, the re-check's, and any notice.

    Where the leg's base is the candidate's parent
    (`gitstate.base_is_candidates_parent`) it keeps every row. When the
    candidate is the committed HEAD and the re-check covers the leg's whole
    range (`gitstate.replay_covers`), the leg leaves every two-version row to
    it and keeps only its candidate-only rows (rulings P29, P32): the replay
    judges each edit at its own commit, on that commit's bytes, where the
    hook filed its ack. Otherwise, over more than one commit, the leg keeps
    its rows but the verifier-list ones, which no re-check covers then, and
    says so once (rulings R18, P34)."""
    leg = _history_lints(repository, snapshots.base, snapshots.candidate)
    notices = []
    if gitstate.base_is_candidates_parent(repository, snapshots):
        pass
    elif (
        recheck_commits is not None
        and snapshots.candidate_name == "HEAD"
        and gitstate.replay_covers(
            repository,
            None if recheck_commits is WHOLE_HISTORY else recheck_commits,
            "HEAD" if git_base is None else git_base,
        )
    ):
        own = _unmatched(repository, snapshots.candidate, snapshots.candidate)
        # The replay keeps UNMATCHED rows only, so a leg row of any other
        # result (an UNREACHABLE witness outage) stays here (ruling P42).
        leg = [
            o
            for o in leg
            if o.result is not Result.UNMATCHED or (o.check, o.target, o.reason) in own
        ]
    else:
        leg = [o for o in leg if o.extra.get("hash_basis") != lints.VERIFIER_LISTS]
        notices.append(LIST_ROWS_NOTICE)
    history = (
        _history_outcomes(repository, recheck_commits, hasher)
        if recheck_commits is not None
        else []
    )
    return leg, history, notices


def _once_each(outcomes, hashes, history_ids):
    """Drop a row the re-check raised again: the same reason under the same
    filing key is the same row. The copy from the first commit in the range
    that raised it stands, since it names that commit; a leg row the re-check
    also raised goes. Two reasons under one key stay two rows, filed as one record, as
    the leg's own rows are."""

    def key(outcome):
        return (*_filing_key(outcome, hashes[id(outcome)]), outcome.reason)

    first: dict[tuple, int] = {}
    for outcome in outcomes:
        if id(outcome) in history_ids:
            first.setdefault(key(outcome), id(outcome))
    return [o for o in outcomes if first.get(key(o), id(o)) == id(o)]


def _plan_state(
    vault_root,
    network=True,
    detection_date=None,
    rw_csv=None,
    base=DEFAULT_BASE,
    *,
    repository_root=None,
    snapshots,
    recheck_commits=None,
    git_base=None,
):
    """Compute one complete projection inside a materialized candidate.

    ``base`` is the Zotero base URL the lifecycle leg reads (ingest spec
    §3.4); ``verify_state`` forwards it positionally. ``recheck_commits`` is
    the re-check's base (`_history_outcomes`), None for no re-check.
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
    # `literature/` flat, as every reader of it globs (`_claim_notes`, the
    # captured set, the linter, `--all`): a nested file is a literature note
    # nowhere, so nothing here stamps a claim `clear_marker_for` cannot reach.
    note_files = [
        path
        for path in sorted((vault / "literature").glob("*.md"))
        if not structure.is_excluded(path, vault)
    ] + [
        path
        for folder in ("wiki", "projects")
        for path in sorted((vault / folder).rglob("*.md"))
        if not structure.is_excluded(path, vault)
    ]
    for path in note_files:
        raw.extend(file_outcomes(vault, path, bibliography_universe))
    for path in sorted(vault.rglob("*.md")):
        if structure.is_excluded(path, vault):
            continue
        if structure.is_reserved(path.relative_to(vault).as_posix()):
            continue
        raw.extend(structure.check_note_frontmatter(vault, path))
    raw.extend(structure.check_reserved(vault))
    raw.extend(structure.check_log_dir(vault))
    raw.extend(structure.check_tree(vault))
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

    def hasher(outcome, base_snapshot, candidate_snapshot):
        return _target_hash(
            vault,
            outcome,
            bibliography_universe,
            base_snapshot=base_snapshot,
            candidate_snapshot=candidate_snapshot,
        )

    leg, history, notices = _two_version_rows(
        repository, snapshots, recheck_commits, git_base=git_base, hasher=hasher
    )
    raw.extend(leg)
    raw.extend(lints.lint_published_drift(repository, snapshots.candidate))
    raw.extend(propagate.lint_propagation(vault))
    raw.extend(
        captured.lint_captured_set(
            vault, as_of=detection_date, bibliography_universe=bibliography_universe
        )
    )
    raw.extend(outcome for outcome, _base, _candidate in history)
    raw, authoritative, hashes = _hashed(
        vault, raw, history, bibliography_universe, snapshots
    )
    effective = _effective(authoritative, hashes, vault)
    warning_effective = _warning_effectiveness(authoritative, hashes, vault)
    _apply_state_transitions(vault, authoritative, detection_date, stamp=effective)
    _file_effects(vault, effective, hashes, warning_effective, detection_date)
    counts: dict[str, int] = {}
    for outcome in effective:
        counts[outcome.result.value] = counts.get(outcome.result.value, 0) + 1
    report = {"outcomes": raw, "counts": counts, "notices": notices}
    return report, effective, hashes, warning_effective


def _hashed(vault, raw, history, bibliography_universe, snapshots):
    """Hash every authoritative outcome, then drop the re-check's repeats
    (`_once_each`).

    A re-check row hashes on its own commit's snapshots, so an ack filed when
    that commit was verified (the hook's index against HEAD) is the same ack;
    every other row on the run's base and candidate."""
    planes = {id(outcome): (base, candidate) for outcome, base, candidate in history}
    authoritative = [
        outcome for outcome in raw if outcome.extra.get("synthetic_offline") is not True
    ]
    hashes = {}
    for outcome in authoritative:
        base_snapshot, candidate_snapshot = planes.get(
            id(outcome), (snapshots.base, snapshots.candidate)
        )
        hashes[id(outcome)] = _target_hash(
            vault,
            outcome,
            bibliography_universe,
            base_snapshot=base_snapshot,
            candidate_snapshot=candidate_snapshot,
        )
    if not history:
        return raw, authoritative, hashes
    kept = {id(o) for o in _once_each(authoritative, hashes, set(planes))}
    raw = [o for o in raw if id(o) in kept or o.extra.get("synthetic_offline") is True]
    return raw, [o for o in authoritative if id(o) in kept], hashes


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
    recheck_commits: str | object | None = None,
):
    """Run one immutable collect/plan/apply/manifest/publication transaction.

    ``recheck_commits`` also replays the two-version lints for every commit
    reachable from HEAD and not from it (a ref, or `WHOLE_HISTORY`), each
    against its parent, a merge against every parent (spec §5.3.1, Q2)."""
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
            recheck_commits=recheck_commits,
            git_base=git_base,
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


def row_line(outcome) -> str:
    """One printed row: result, check, target and reason, and for a row the
    re-check raised at a past commit, that commit (ruling P40), since the
    vault as it stands may no longer show the edit."""
    line = f"{outcome.result.value} {outcome.check} {outcome.target} — {outcome.reason}"
    commit = outcome.extra.get("commit")
    return f"{line} (commit {commit[:7]})" if isinstance(commit, str) else line


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
            blockers.append(row_line(outcome))
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
        row_line(outcome) for outcome in genuine if outcome.result is Result.UNREACHABLE
    ]
    return (3, tuple(unreachable)) if unreachable else (0, ())
