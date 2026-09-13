"""Offline, warn-tier integrity lints for research-vault."""

from __future__ import annotations

import os
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from . import claims as claims_mod
from . import frontmatter, gitstate, notes
from .outcome import Outcome, Result
from .pathcodec import RepoPath

if TYPE_CHECKING:
    from collections.abc import Mapping

ANCHOR = re.compile(r"\^(c-[A-Za-z0-9-]+)\s*$")
FAILED_VERIFICATION = re.compile(
    r"\[failed-verification:: [A-Za-z0-9-]+/\d{4}-\d{2}-\d{2}\]"
)
CLAIM_LINK = re.compile(r"\[\[([A-Za-z0-9_.:-]+#\^c-[A-Za-z0-9-]+)\]\]")
# ``published/<project>-<YYYY-MM-DD>-<HHMMSS>``. The time component is
# uniform, never conditional: a suffix that appeared only on the
# second tag of a day would be the shape that breaks this pattern and the
# newest-tag ordering below, whereas one every tag carries costs this regex
# once and keeps a plain lexicographic sort chronological to the second.
PUBLISHED_TAG = re.compile(r"^published/(.+)-\d{4}-\d{2}-\d{2}-\d{6}$")
TRANSITION_FIELD = re.compile(
    r"\[(status|deprecated-at|deprecated-by|reason|superseded-by):: ([^\]]*)\]"
)
# §5: deprecation is a transition record carrying these four fields; a
# successor pointer is optional (present only "where a successor exists").
_DEPRECATION_REQUIRED_FIELDS = {"status", "deprecated-at", "deprecated-by", "reason"}
_DEPRECATION_OPTIONAL_FIELDS = {"superseded-by"}


def _git(vault_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=vault_root, capture_output=True, text=True, check=False
    )


def _deduplicate(outcomes: list[Outcome]) -> list[Outcome]:
    """Return stable findings; repeated references must not flood the inbox."""

    def extra_key(extra: Mapping) -> tuple[tuple[str, str], ...]:
        return tuple(sorted((key, repr(value)) for key, value in extra.items()))

    seen = set()
    result = []
    for outcome in sorted(
        outcomes,
        key=lambda item: (
            item.check,
            item.target,
            item.reason,
            extra_key(item.extra),
        ),
    ):
        key = (
            outcome.check,
            outcome.target,
            outcome.result,
            outcome.reason,
            extra_key(outcome.extra),
        )
        if key not in seen:
            seen.add(key)
            result.append(outcome)
    return result


def _relative(vault_root: Path, path: Path) -> bytes:
    return os.fsencode(path.relative_to(vault_root))


def _path(vault_root: Path, raw_path: bytes) -> Path:
    # A bytes join: raw_path is an exact repository path that need not be valid
    # UTF-8, and pathlib cannot hold bytes (Path(b"...") raises TypeError), so the
    # join has to happen on the byte plane before the surrogateescape decode.
    return Path(
        os.path.join(  # noqa: PTH118
            os.fsencode(vault_root), raw_path
        ).decode(errors="surrogateescape")
    )


def _parse_frontmatter(text: str) -> tuple[dict, bool]:
    try:
        data, _ = frontmatter.parse(text)
    except frontmatter.FrontmatterError:
        return {}, False
    return data, True


def _schema_outcome(check: str, target, extra: dict | None = None) -> Outcome:
    return Outcome(
        check,
        target,
        Result.UNMATCHED,
        "schema-violation — malformed frontmatter",
        extra=extra or {},
    )


def _is_append_only_path(rel: bytes) -> bool:
    """The durable-append surfaces this lint protects (terminology §4.1).

    An applied propagation plan (``system/propagations/``, decision 01) is a
    write-once record: an append-only file that never grows, so the same
    prefix check refuses any rewrite of it.
    """
    return (
        rel == b"inbox/review-queue.md"
        or rel.startswith((b"log/", b"system/propagations/"))
        or (rel.startswith(b"projects/") and rel.endswith(b"/search-log.md"))
    )


def lint_append_only(
    vault_root,
    base_snapshot: gitstate.Snapshot | None = None,
    candidate_snapshot: gitstate.Snapshot | None = None,
) -> list[Outcome]:
    """Detect deleted historical content, one finding for every affected file."""
    vault = Path(vault_root)
    if base_snapshot is None:
        try:
            base_snapshot = gitstate.snapshot_tree(vault, "HEAD")
        except gitstate.GitStateError:
            base_snapshot = gitstate.Snapshot({})
    if candidate_snapshot is None:
        candidate_snapshot = gitstate.snapshot_worktree(vault)
    outcomes = []
    paths = set(base_snapshot.images) | set(candidate_snapshot.images)
    for rel in sorted(paths):
        if not _is_append_only_path(rel):
            continue
        old = base_snapshot.image(rel)
        new = candidate_snapshot.image(rel)
        old_bytes = old.data if old is not None and old.kind == "file" else None
        new_bytes = new.data if new is not None and new.kind == "file" else None
        if old_bytes is not None and (
            new_bytes is None or not new_bytes.startswith(old_bytes)
        ):
            outcomes.append(
                Outcome(
                    "append-only",
                    RepoPath(rel),
                    Result.UNMATCHED,
                    "drift — append-only file rewrote history",
                )
            )
    return outcomes


def _claim_blocks(text: str) -> dict[str, str]:
    """Return full anchored claim blocks, including quote and selector continuations."""
    blocks = {}
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        match = ANCHOR.search(line.rstrip("\r\n"))
        if match is None:
            continue
        block = [line]
        for continuation in lines[index + 1 :]:
            if continuation.startswith(("  > ", "  <!-- rv-selector")):
                block.append(continuation)
            else:
                break
        blocks[match.group(1)] = "".join(block)
    return blocks


def _block_lines(block: str) -> list[str]:
    return block.splitlines(keepends=True)


def _line_content_and_ending(line: str) -> tuple[str, str]:
    match = re.search(r"(?:\r\n|\n|\r)$", line)
    if match is None:
        return line, ""
    return line[: match.start()], match.group()


def _remove_single_marker(line: str) -> str | None:
    """Remove one marker and its one separator; reject all other marker shapes."""
    matches = list(FAILED_VERIFICATION.finditer(line))
    if len(matches) != 1:
        return None
    match = matches[0]
    if match.start() and line[match.start() - 1].isspace():
        return line[: match.start() - 1] + line[match.end() :]
    if match.end() < len(line) and line[match.end()].isspace():
        return line[: match.start()] + line[match.end() + 1 :]
    return line[: match.start()] + line[match.end() :]


def _normalize_marker_transition(old_block: str, new_block: str) -> tuple[str, str]:
    """Normalize exactly one marker addition/removal, never a marker replacement."""
    old_lines = _block_lines(old_block)
    new_lines = _block_lines(new_block)
    if len(old_lines) != len(new_lines) or old_lines[1:] != new_lines[1:]:
        return old_block, new_block
    old_content, old_ending = _line_content_and_ending(old_lines[0])
    new_content, new_ending = _line_content_and_ending(new_lines[0])
    old_count = len(FAILED_VERIFICATION.findall(old_content))
    new_count = len(FAILED_VERIFICATION.findall(new_content))
    if (old_count, new_count) == (0, 1):
        stripped = _remove_single_marker(new_content)
        if stripped is not None:
            new_lines[0] = stripped + new_ending
    elif (old_count, new_count) == (1, 0):
        stripped = _remove_single_marker(old_content)
        if stripped is not None:
            old_lines[0] = stripped + old_ending
    return "".join(old_lines), "".join(new_lines)


def _without_fields(line: str, names: set[str]) -> str:
    return re.sub(
        r"\s+\[(" + "|".join(re.escape(name) for name in names) + r"):: [^\]]*\]",
        "",
        line,
    )


def _is_complete_deprecation_transition(old_block: str, new_block: str) -> bool:
    old_block, new_block = _normalize_marker_transition(old_block, new_block)
    old_lines = _block_lines(old_block)
    new_lines = _block_lines(new_block)
    if len(old_lines) != len(new_lines) or old_lines[1:] != new_lines[1:]:
        return False
    old_line, old_ending = _line_content_and_ending(old_lines[0])
    new_line, new_ending = _line_content_and_ending(new_lines[0])
    if old_ending != new_ending:
        return False
    required = _DEPRECATION_REQUIRED_FIELDS
    optional = _DEPRECATION_OPTIONAL_FIELDS
    fields: dict[str, list[str]] = {name: [] for name in required | optional}
    for name, value in TRANSITION_FIELD.findall(new_line):
        fields[name].append(value)
    if any(len(fields[name]) != 1 for name in required):
        return False
    if any(len(fields[name]) > 1 for name in optional):
        return False
    if fields["status"] != ["deprecated"]:
        return False
    if any(not fields[name][0].strip() for name in required - {"status"}):
        return False
    if fields["superseded-by"] and not fields["superseded-by"][0].strip():
        return False
    try:
        date.fromisoformat(fields["deprecated-at"][0])
    except ValueError:
        return False
    if TRANSITION_FIELD.search(old_line) and "[status:: deprecated]" in old_line:
        return False
    old_base = _without_fields(old_line, {"status"})
    new_base = _without_fields(new_line, required | optional)
    return old_base == new_base


def _claim_target(rel: bytes, text: str, claim_id: str):
    data, parsed = _parse_frontmatter(text)
    citation_key = data.get("citationKey") if parsed else None
    if isinstance(citation_key, str) and citation_key:
        return claims_mod.claim_link(citation_key, claim_id)
    return RepoPath(rel)


def lint_claim_immutability(
    vault_root,
    base_snapshot: gitstate.Snapshot | None = None,
    candidate_snapshot: gitstate.Snapshot | None = None,
) -> list[Outcome]:
    """Require committed claims to stay byte-identical absent a real transition."""
    vault = Path(vault_root)
    outcomes = []
    roots = (b"literatures/", b"projects/")
    if base_snapshot is None:
        try:
            base_snapshot = gitstate.snapshot_tree(vault, "HEAD")
        except gitstate.GitStateError:
            base_snapshot = gitstate.Snapshot({})
    if candidate_snapshot is None:
        candidate_snapshot = gitstate.snapshot_worktree(vault)
    markdown_paths = {
        rel
        for rel in set(base_snapshot.images) | set(candidate_snapshot.images)
        if rel.endswith(b".md") and any(rel.startswith(root) for root in roots)
    }
    for rel in sorted(markdown_paths):
        base_image = base_snapshot.image(rel)
        if base_image is None or base_image.kind != "file":
            continue
        head_bytes = base_image.data or b""
        head = head_bytes.decode(errors="surrogateescape")
        candidate_image = candidate_snapshot.image(rel)
        current = (
            (candidate_image.data or b"").decode(errors="surrogateescape")
            if candidate_image is not None and candidate_image.kind == "file"
            else ""
        )
        _, parsed = _parse_frontmatter(current if candidate_image is not None else head)
        if candidate_image is not None and not parsed:
            outcomes.append(_schema_outcome("claim-immutability", RepoPath(rel)))
        old_blocks = _claim_blocks(head)
        new_blocks = _claim_blocks(current)
        for claim_id, old_block in old_blocks.items():
            new_block = new_blocks.get(claim_id)
            if new_block is not None:
                normalized_old, normalized_new = _normalize_marker_transition(
                    old_block, new_block
                )
                unchanged = normalized_old == normalized_new
            else:
                unchanged = False
            if unchanged or (
                new_block and _is_complete_deprecation_transition(old_block, new_block)
            ):
                continue
            outcomes.append(
                Outcome(
                    "claim-immutability",
                    _claim_target(rel, head, claim_id),
                    Result.UNMATCHED,
                    f"drift — claim ^{claim_id} mutated or vanished without deprecation",
                    extra={"note_path": RepoPath(rel), "claim_id": claim_id},
                )
            )
    return _deduplicate(outcomes)


def _current_paths(vault_root: Path, prefix: str) -> set[bytes]:
    base = vault_root / prefix
    if not base.is_dir():
        return set()
    return {_relative(vault_root, path) for path in base.rglob("*") if path.is_file()}


def _project_status(
    vault_root: Path,
    prefix: str,
    tag: str | None = None,
    snapshot: gitstate.Snapshot | None = None,
) -> tuple[set[str], list[bytes]]:
    paths = (
        gitstate.revision_paths(vault_root, tag, prefix)
        if tag
        else (
            {
                path
                for path, image in snapshot.images.items()
                if path.startswith(prefix.encode() + b"/") and image.kind == "file"
            }
            if snapshot is not None
            else _current_paths(vault_root, prefix)
        )
    )
    statuses, malformed = set(), []
    for rel in sorted(path for path in paths if path.endswith(b".md")):
        if tag:
            raw = gitstate.blob_bytes(vault_root, tag, rel)
            text = raw.decode(errors="surrogateescape") if raw is not None else ""
        elif snapshot is not None:
            # rel came out of snapshot.images just above, so the image is present.
            image = snapshot.images[rel]
            text = (image.data or b"").decode(errors="surrogateescape")
        else:
            text = _path(vault_root, rel).read_bytes().decode(errors="surrogateescape")
        data, parsed = _parse_frontmatter(text)
        if not parsed:
            malformed.append(rel)
        elif isinstance(data.get("status"), str):
            statuses.add(data["status"])
    return statuses, malformed


def _project_differs(
    vault_root: Path,
    tag: str,
    prefix: str,
    snapshot: gitstate.Snapshot | None = None,
) -> bool:
    prior = gitstate.snapshot_tree(vault_root, tag)
    current = (
        snapshot if snapshot is not None else gitstate.snapshot_worktree(vault_root)
    )
    raw_prefix = prefix.encode() + b"/"
    paths = {
        path
        for path in set(prior.images) | set(current.images)
        if path == prefix.encode() or path.startswith(raw_prefix)
    }
    return any(
        gitstate.images_differ(prior.image(path), current.image(path)) for path in paths
    )


# The statuses whose project this lint watches. `corrected` is watched because
# a corrected publication is exactly the artifact a corrections regime needs
# watched, and `mark-corrected` writes `corrected` over `published` — keying on
# `published` alone ended the watch at the moment the stakes rose. `withdrawn`
# and `parked` are unwatched **by design**, recorded here as a ruling rather
# than left as a side effect of which statuses `_project_status` happens to
# read: both say the project no longer stands as a publication, so divergence
# from its tag is expected rather than reportable.
WATCHED_PUBLICATION_STATUSES = frozenset({"published", "corrected"})


def _newest_published_tags(vault: Path) -> dict[str, str]:
    """Map each project to its newest ``published/*`` tag.

    ``PUBLISHED_TAG``'s prefix is constant per project and its suffix is a
    zero-padded ISO date and time, so lexicographic max is the newest tag —
    including between two tags minted on the same day. The newest tag is the
    only sound comparison basis: a correction's tree differs from the original
    tag by construction, and ADR 0003 forbids deleting that tag, so comparing
    against anything older would report every legitimate correction as drift.
    """
    newest: dict[str, str] = {}
    for tag in _git(vault, "tag", "--list", "published/*").stdout.split():
        match = PUBLISHED_TAG.match(tag)
        if match is None:
            continue
        project = match.group(1)
        newest[project] = max(newest.get(project, ""), tag)
    return newest


def lint_published_drift(
    vault_root, candidate_snapshot: gitstate.Snapshot | None = None
) -> list[Outcome]:
    """Compare each project's newest published tag to the working tree.

    Untracked files included; ``_deduplicate`` collapses the result on the
    project directory, so a project answers with one drift outcome either way.
    """
    vault = Path(vault_root)
    outcomes: list[Outcome] = []
    for project, tag in sorted(_newest_published_tags(vault).items()):
        project_dir = f"projects/{project}"
        if not _project_differs(vault, tag, project_dir, candidate_snapshot):
            continue
        current_statuses, malformed = _project_status(
            vault, project_dir, snapshot=candidate_snapshot
        )
        outcomes.extend(
            _schema_outcome("published-drift", RepoPath(rel)) for rel in malformed
        )
        if current_statuses:
            watched = bool(current_statuses & WATCHED_PUBLICATION_STATUSES)
        else:
            prior_statuses, prior_malformed = _project_status(vault, project_dir, tag)
            outcomes.extend(
                _schema_outcome("published-drift", RepoPath(rel))
                for rel in prior_malformed
            )
            watched = bool(prior_statuses & WATCHED_PUBLICATION_STATUSES)
        if watched:
            outcomes.append(
                Outcome(
                    "published-drift",
                    RepoPath(project_dir.encode()),
                    Result.UNMATCHED,
                    "drift — published project diverged from its tag",
                )
            )
    return _deduplicate(outcomes)


def _origin(vault_root: Path, note_file: Path, claim) -> tuple[str | RepoPath, dict]:
    """The claim's target — its anchor link, else the note's repo path — and its origin extra."""
    vault = Path(vault_root)
    note = Path(note_file)
    rel = _relative(vault, note)
    data, parsed = _parse_frontmatter(note.read_text())
    citation_key = data.get("citationKey") if parsed else None
    target: str | RepoPath
    if claim.claim_id and isinstance(citation_key, str) and citation_key:
        target = claims_mod.claim_link(citation_key, claim.claim_id)
    else:
        target = RepoPath(rel)
    return target, {
        "note_path": RepoPath(rel),
        "claim_id": claim.claim_id,
    }


def disputed_claim_links(vault_root: Path) -> tuple[set[str], list[Outcome]]:
    disputed, outcomes = set(), []
    for path in (
        sorted((vault_root / "wiki").rglob("*.md"))
        if (vault_root / "wiki").is_dir()
        else []
    ):
        rel = _relative(vault_root, path)
        text = path.read_text()
        data, parsed = _parse_frontmatter(text)
        if not parsed:
            outcomes.append(_schema_outcome("disputed-claim", RepoPath(rel)))
        page_key = data.get("citationKey") if parsed else None
        if not isinstance(page_key, str) or not page_key:
            page_key = path.stem
        for claim in claims_mod.parse_claims(text):
            if "disputes" not in claim.fields:
                continue
            if claim.claim_id:
                disputed.add(claims_mod.claim_link(page_key, claim.claim_id))
            disputed.update(CLAIM_LINK.findall(claim.fields.get("supports", "")))
    return disputed, outcomes


def lint_disputed_claim(vault_root, note_file) -> list[Outcome]:
    vault, note = Path(vault_root), Path(note_file)
    disputed, outcomes = disputed_claim_links(vault)
    text = note.read_text()
    for claim in claims_mod.parse_claims(text):
        _target, extra = _origin(vault, note, claim)
        for claim_link in CLAIM_LINK.findall(claim.fields.get("supports", "")):
            if claim_link in disputed:
                outcomes.append(
                    Outcome(
                        "disputed-claim",
                        claim_link,
                        Result.UNMATCHED,
                        f"disputed-claim — {claim_link} has standing counter-evidence",
                        extra=extra,
                    )
                )
    return _deduplicate(outcomes)


def _literature_files(snapshot: gitstate.Snapshot) -> dict[bytes, gitstate.FileImage]:
    """Every literature note in the snapshot: `literatures/<key>.md`, flat.

    The one shape capture writes (`notes.note_path` refuses a `/` in the key)
    and the captured set's own definition (decision 08: `literatures/*.md`);
    every reader of the directory globs flat so a nested file is a literature
    note nowhere rather than somewhere.
    """
    return {
        raw_path: image
        for raw_path, image in snapshot.images.items()
        if raw_path.startswith(b"literatures/")
        and b"/" not in raw_path[len(b"literatures/") :]
        and raw_path.endswith(b".md")
        and image.kind == "file"
    }


def _body_bytes(image: gitstate.FileImage | None) -> bytes | None:
    """The note body below the frontmatter, or None when it cannot be read."""
    if image is None or image.kind != "file":
        return None
    try:
        text = (image.data or b"").decode("utf-8")
        return notes.note_body(text).encode("utf-8")
    except (UnicodeDecodeError, frontmatter.FrontmatterError):
        return None


# Machine-owned frontmatter fields: every field capture writes; a change to any
# without a `generated` bump by the machine actor is drift. Legality rides on
# the `generated` writer attestation, not on where in the note the field sits.
_MACHINE_OWNED_FRONTMATTER_KEYS = notes.CAPTURE_FIELDS
# docs/terminology.md's actor convention: process-written records carry
# `research_vault/<version>`, so this class test — not an exact-version
# match — survives a `__version__` bump without flagging every prior note.
_MACHINE_ACTOR_PREFIX = "research_vault/"


def _frontmatter(image: gitstate.FileImage | None) -> dict | None:
    if image is None or image.kind != "file":
        return None
    try:
        text = (image.data or b"").decode("utf-8")
    except UnicodeDecodeError:
        return None
    try:
        data, _ = frontmatter.parse(text)
    except frontmatter.FrontmatterError:
        return None
    return data


def _field(data: dict | None, key: str):
    """One frontmatter value, or None for an absent key or unparseable side.

    An unparseable side (`data is None`) must not be able to hide a change —
    it has to compare unequal to whatever the other, parseable side holds, the
    same fail-closed shape `_body_bytes` already uses for the note body.
    """
    return data.get(key) if data is not None else None


def _machine_attested(generated) -> bool:
    """Whether `generated` is validly shaped AND its `by` is machine-class.

    Shape first: `notes._valid_generated` is the one place this field's shape
    is defined, so a malformed `generated` (missing `at`, extra keys, a bad
    timestamp) can never attest a change here even if `by` looks right.
    """
    return notes._valid_generated(generated) and generated["by"].startswith(
        _MACHINE_ACTOR_PREFIX
    )


def _frontmatter_attestation_outcomes(raw_path, base_data, candidate_data):
    """Flag a machine-owned frontmatter change with no matching writer attestation.

    Legality rule: a change to any machine-owned key is legal iff `generated`
    also changed in the same diff with `by` the machine actor class.
    `generated` is itself a capture field, so the same loop guards it and it
    cannot legalize its own unattested change. Attestation is
    per-file-per-diff: one legitimate `generated` bump also legalizes any
    other machine-owned key riding along unattested in the same diff.

    Stated boundary, not a compliance control: this catches accidents and
    oblivious agents. Forging the attestation — hand-writing a machine-class
    `by` — is deliberate circumvention (recorded-bypass class), and so is
    piggy-backing an unrelated edit onto someone else's legitimate bump;
    neither is this check's job to catch.
    """
    base_generated = _field(base_data, "generated")
    candidate_generated = _field(candidate_data, "generated")
    generated_changed = base_generated != candidate_generated
    # An unparseable base (`base_data is None`) has no prior state to compare
    # against, so a validly machine-shaped candidate `generated` must not be
    # read as evidence of a legitimate write — that would let an unreadable
    # base auto-attest a sibling machine-owned key change hiding behind it.
    attested = (
        base_data is not None
        and generated_changed
        and _machine_attested(candidate_generated)
    )
    return [
        Outcome(
            "evidence-layer",
            RepoPath(raw_path),
            Result.UNMATCHED,
            f"drift — {key} changed without writer attestation",
        )
        for key in sorted(_MACHINE_OWNED_FRONTMATTER_KEYS)
        if _field(base_data, key) != _field(candidate_data, key) and not attested
    ]


def lint_evidence_layer(
    base_snapshot: gitstate.Snapshot,
    candidate_snapshot: gitstate.Snapshot,
) -> list[Outcome]:
    """Validate witnesses and expose every base-to-candidate body change."""
    outcomes = []
    base_files = _literature_files(base_snapshot)
    candidate_files = _literature_files(candidate_snapshot)

    for raw_path, image in sorted(candidate_files.items()):
        result, reason = notes.validate_managed_witness(image.data or b"")
        if result is not Result.MATCHED:
            outcomes.append(
                Outcome(
                    "evidence-layer",
                    RepoPath(raw_path),
                    result,
                    reason,
                )
            )

    removed = set(base_files) - set(candidate_files)
    added = set(candidate_files) - set(base_files)
    paired_removed = set()
    paired_added = set()
    removed_by_body: dict[bytes, list[bytes]] = {}
    for raw_path in removed:
        body = _body_bytes(base_files[raw_path])
        if body is not None:
            removed_by_body.setdefault(body, []).append(raw_path)
    for raw_path in sorted(added):
        body = _body_bytes(candidate_files[raw_path])
        candidates = removed_by_body.get(body, []) if body is not None else []
        if candidates:
            old_path = sorted(candidates)[0]
            candidates.remove(old_path)
            paired_removed.add(old_path)
            paired_added.add(raw_path)
            outcomes.append(
                Outcome(
                    "evidence-layer",
                    RepoPath(raw_path),
                    Result.UNMATCHED,
                    "drift — literature note renamed",
                    extra={"prior_path": RepoPath(old_path)},
                )
            )
    outcomes.extend(
        Outcome(
            "evidence-layer",
            RepoPath(raw_path),
            Result.UNMATCHED,
            "drift — literature note added",
        )
        for raw_path in sorted(added - paired_added)
    )
    outcomes.extend(
        Outcome(
            "evidence-layer",
            RepoPath(raw_path),
            Result.UNMATCHED,
            "drift — literature note deleted",
        )
        for raw_path in sorted(removed - paired_removed)
    )
    for raw_path in sorted(set(base_files) & set(candidate_files)):
        old = _body_bytes(base_files[raw_path])
        new = _body_bytes(candidate_files[raw_path])
        if old != new:
            outcomes.append(
                Outcome(
                    "evidence-layer",
                    RepoPath(raw_path),
                    Result.UNMATCHED,
                    "drift — literature note body changed",
                )
            )
        outcomes.extend(
            _frontmatter_attestation_outcomes(
                raw_path,
                _frontmatter(base_files[raw_path]),
                _frontmatter(candidate_files[raw_path]),
            )
        )
    return _deduplicate(outcomes)
