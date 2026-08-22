"""Offline, warn-tier integrity lints for the knowledge harness."""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Mapping
from datetime import date
from pathlib import Path

from . import claims as claims_mod
from . import frontmatter, gitstate, notes
from .outcome import Outcome, Result
from .pathcodec import RepoPath

ANCHOR = re.compile(r"\^(c-[A-Za-z0-9-]+)\s*$")
FAILED_VERIFICATION = re.compile(
    r"\[failed-verification:: [A-Za-z0-9-]+/\d{4}-\d{2}-\d{2}\]"
)
CLAIM_LINK = re.compile(r"\[\[([A-Za-z0-9_.:-]+#\^c-[A-Za-z0-9-]+)\]\]")
PUBLISHED_TAG = re.compile(r"^published/(.+)-\d{4}-\d{2}-\d{2}$")
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
    return Path(
        os.path.join(os.fsencode(vault_root), raw_path).decode(errors="surrogateescape")
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
        if rel != b"inbox/review-queue.md" and not rel.startswith(b"log/"):
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
            if continuation.startswith(("  > ", "  <!-- hk-selector")):
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
    fields = {name: [] for name in required | optional}
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
    citekey = data.get("citekey") if parsed else None
    if isinstance(citekey, str) and citekey:
        return claims_mod.claim_link(citekey, claim_id)
    return RepoPath(rel)


def lint_claim_immutability(
    vault_root,
    base_snapshot: gitstate.Snapshot | None = None,
    candidate_snapshot: gitstate.Snapshot | None = None,
) -> list[Outcome]:
    """Require committed claims to stay byte-identical absent a real transition."""
    vault = Path(vault_root)
    outcomes = []
    roots = (b"literatures/", b"synthesis/", b"projects/")
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
            image = snapshot.image(rel)
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
    return any(prior.image(path) != current.image(path) for path in paths)


def lint_published_drift(
    vault_root, candidate_snapshot: gitstate.Snapshot | None = None
) -> list[Outcome]:
    """Compare every published tag to the working tree, including untracked files."""
    vault = Path(vault_root)
    tags = sorted(_git(vault, "tag", "--list", "published/*").stdout.split())
    outcomes = []
    for tag in tags:
        match = PUBLISHED_TAG.match(tag)
        if match is None:
            continue
        project_dir = f"projects/{match.group(1)}"
        if not _project_differs(vault, tag, project_dir, candidate_snapshot):
            continue
        current_statuses, malformed = _project_status(
            vault, project_dir, snapshot=candidate_snapshot
        )
        for rel in malformed:
            outcomes.append(_schema_outcome("published-drift", RepoPath(rel)))
        if current_statuses:
            published = "published" in current_statuses
        else:
            prior_statuses, prior_malformed = _project_status(vault, project_dir, tag)
            for rel in prior_malformed:
                outcomes.append(_schema_outcome("published-drift", RepoPath(rel)))
            published = "published" in prior_statuses
        if published:
            outcomes.append(
                Outcome(
                    "published-drift",
                    RepoPath(project_dir.encode()),
                    Result.UNMATCHED,
                    "drift — published project diverged from its tag",
                )
            )
    return _deduplicate(outcomes)


def _origin(
    vault_root: Path, note_file: Path, claim, fallback: str
) -> tuple[object, dict]:
    vault = Path(vault_root)
    note = Path(note_file)
    rel = _relative(vault, note)
    data, parsed = _parse_frontmatter(note.read_text())
    citekey = data.get("citekey") if parsed else None
    if claim.claim_id and isinstance(citekey, str) and citekey:
        target = claims_mod.claim_link(citekey, claim.claim_id)
    else:
        target = fallback if fallback else RepoPath(rel)
    return target, {
        "note_path": RepoPath(rel),
        "claim_id": claim.claim_id,
    }


def _note_status(vault_root: Path, citekey: str) -> tuple[str | None, str | None, bool]:
    path = vault_root / "literatures" / f"{citekey}.md"
    if not path.is_file():
        return None, None, True
    data, parsed = _parse_frontmatter(path.read_text())
    if not parsed:
        return None, None, False
    return data.get("status"), data.get("superseded-by"), True


def lint_screening_state(vault_root, note_file) -> list[Outcome]:
    vault, note = Path(vault_root), Path(note_file)
    text = note.read_text()
    outcomes = []
    lines = text.splitlines()
    for claim in claims_mod.parse_claims(text):
        citekeys = [
            match.group("key")
            for match in claims_mod.CITE_RE.finditer(lines[claim.line_no - 1])
        ]
        for citekey in citekeys:
            target, extra = _origin(vault, note, claim, citekey)
            status, successor, parsed = _note_status(vault, citekey)
            if not parsed:
                outcomes.append(_schema_outcome("screening-state", target, extra))
            elif status in {"excluded", "superseded"}:
                suffix = f" (superseded-by {successor})" if successor else ""
                outcomes.append(
                    Outcome(
                        "screening-state",
                        target,
                        Result.UNMATCHED,
                        f"superseded-note — cites {citekey} with status {status}{suffix}",
                        extra=extra,
                    )
                )
    return _deduplicate(outcomes)


def _disputed_claim_links(vault_root: Path) -> tuple[set[str], list[Outcome]]:
    disputed, outcomes = set(), []
    for path in (
        sorted((vault_root / "synthesis").rglob("*.md"))
        if (vault_root / "synthesis").is_dir()
        else []
    ):
        rel = _relative(vault_root, path)
        text = path.read_text()
        data, parsed = _parse_frontmatter(text)
        if not parsed:
            outcomes.append(_schema_outcome("disputed-claim", RepoPath(rel)))
        page_key = data.get("citekey") if parsed else None
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
    disputed, outcomes = _disputed_claim_links(vault)
    text = note.read_text()
    for claim in claims_mod.parse_claims(text):
        target, extra = _origin(vault, note, claim, "")
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


def lint_web_archive(vault_root) -> list[Outcome]:
    vault = Path(vault_root)
    outcomes = []
    literature = vault / "literatures"
    if not literature.is_dir():
        return outcomes
    for path in sorted(literature.glob("*.md")):
        rel = _relative(vault, path)
        data, parsed = _parse_frontmatter(path.read_text())
        if not parsed:
            outcomes.append(_schema_outcome("web-archive", RepoPath(rel)))
            continue
        if data.get("url") and not data.get("doi") and not data.get("archive-url"):
            target = (
                data.get("citekey")
                if isinstance(data.get("citekey"), str)
                else RepoPath(rel)
            )
            outcomes.append(
                Outcome(
                    "web-archive",
                    target,
                    Result.UNMATCHED,
                    "missing-archive — web source has no archive-url",
                )
            )
    return _deduplicate(outcomes)


def _literature_files(snapshot: gitstate.Snapshot) -> dict[bytes, gitstate.FileImage]:
    return {
        raw_path: image
        for raw_path, image in snapshot.images.items()
        if raw_path.startswith(b"literatures/")
        and raw_path.endswith(b".md")
        and image.kind == "file"
    }


def _managed_bytes(image: gitstate.FileImage | None) -> bytes | None:
    if image is None or image.kind != "file":
        return None
    try:
        return notes.managed_slice_bytes(image.data or b"")
    except notes.ManagedRegionError:
        return None


def lint_evidence_layer(
    base_snapshot: gitstate.Snapshot,
    candidate_snapshot: gitstate.Snapshot,
) -> list[Outcome]:
    """Validate witnesses and expose every base-to-candidate managed change."""
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
    removed_by_managed = {}
    for raw_path in removed:
        managed = _managed_bytes(base_files[raw_path])
        if managed is not None:
            removed_by_managed.setdefault(managed, []).append(raw_path)
    for raw_path in sorted(added):
        managed = _managed_bytes(candidate_files[raw_path])
        candidates = removed_by_managed.get(managed, []) if managed is not None else []
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
                    "drift — managed literature note renamed",
                    extra={"prior_path": RepoPath(old_path)},
                )
            )
    for raw_path in sorted(added - paired_added):
        outcomes.append(
            Outcome(
                "evidence-layer",
                RepoPath(raw_path),
                Result.UNMATCHED,
                "drift — managed literature note added",
            )
        )
    for raw_path in sorted(removed - paired_removed):
        outcomes.append(
            Outcome(
                "evidence-layer",
                RepoPath(raw_path),
                Result.UNMATCHED,
                "drift — managed literature note deleted",
            )
        )
    for raw_path in sorted(set(base_files) & set(candidate_files)):
        old = _managed_bytes(base_files[raw_path])
        new = _managed_bytes(candidate_files[raw_path])
        if old != new:
            outcomes.append(
                Outcome(
                    "evidence-layer",
                    RepoPath(raw_path),
                    Result.UNMATCHED,
                    "drift — managed literature region changed",
                )
            )
    return _deduplicate(outcomes)
