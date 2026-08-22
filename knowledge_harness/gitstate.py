"""Immutable Git/worktree snapshots and exact projection publication."""

from __future__ import annotations

import os
import stat
import subprocess
import tempfile
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING

from .pathcodec import RepoPath, encode_repo_path

if TYPE_CHECKING:
    from collections.abc import Mapping

ZERO_OID = "0" * 40


class GitStateError(RuntimeError):
    """Snapshot, projection, manifest, or publication state is incoherent."""


@dataclass(frozen=True)
class FileImage:
    raw_path: bytes
    kind: str
    mode: int
    data: bytes | None

    def __post_init__(self) -> None:
        RepoPath(self.raw_path)
        if self.kind not in {"file", "directory", "symlink", "special"}:
            raise ValueError("unknown file-image kind")
        if self.kind in {"file", "symlink"} and type(self.data) is not bytes:
            raise TypeError("file and symlink images require bytes")
        if self.kind in {"directory", "special"} and self.data is not None:
            raise TypeError("directory and special images cannot carry bytes")


@dataclass(frozen=True)
class Snapshot:
    images: Mapping[bytes, FileImage]

    def __post_init__(self) -> None:
        copied = {}
        for raw_path, image in self.images.items():
            if type(raw_path) is not bytes or image.raw_path != raw_path:
                raise TypeError("snapshot keys must equal raw image paths")
            copied[raw_path] = image
        object.__setattr__(self, "images", MappingProxyType(copied))

    def image(self, raw_path: bytes) -> FileImage | None:
        return self.images.get(raw_path)


def images_differ(before: FileImage | None, after: FileImage | None) -> bool:
    """Whether two snapshot images differ in content — the one definition.

    Git tracks no directory of its own, so a directory entry present on one
    side and absent on the other carries nothing and is not a difference.
    `publish._require_clean_project` and `lints._project_differs` both ask this
    question about the same ``projects/<name>`` prefix, moments apart: a
    publication refused for a bare empty directory, or a tag reported as
    drifted the instant it was minted, is the disagreement between two answers.
    """
    if before == after:
        return False
    return not all(
        image is None or image.kind == "directory" for image in (before, after)
    )


@dataclass(frozen=True)
class VerificationSnapshots:
    base_tree: str
    base: Snapshot
    expected_head: str | None
    head_tree: str
    head: Snapshot
    candidate_name: str
    candidate: Snapshot
    live: Snapshot


@dataclass(frozen=True)
class CapturedOutput:
    raw_path: bytes
    mode: int
    data: bytes

    def __post_init__(self) -> None:
        RepoPath(self.raw_path)
        if type(self.data) is not bytes:
            raise TypeError("captured output data must be bytes")
        if self.mode not in {0o100644, 0o100755}:
            raise ValueError("captured outputs must be regular Git files")

    @property
    def image(self) -> FileImage:
        return FileImage(self.raw_path, "file", self.mode, self.data)


def _git(
    vault_root: Path,
    *args,
    stdin: bytes | None = None,
    env: Mapping[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", *args],
        cwd=Path(vault_root),
        input=stdin,
        capture_output=True,
        env=None if env is None else {**os.environ, **env},
        check=False,
    )
    if check and result.returncode != 0:
        operation = args[0] if args and isinstance(args[0], str) else "operation"
        try:
            operation.encode("ascii")
        except UnicodeEncodeError:
            operation = "operation"
        raise GitStateError(f"git {operation} failed with status {result.returncode}")
    return result


def _oid(result: subprocess.CompletedProcess[bytes], description: str) -> str:
    try:
        value = result.stdout.decode("ascii").strip()
    except UnicodeDecodeError as error:
        raise GitStateError(f"{description} returned a non-ASCII object id") from error
    if len(value) != 40 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise GitStateError(f"{description} returned an invalid object id")
    return value


def _empty_tree(vault_root: Path) -> str:
    return _oid(
        _git(vault_root, "hash-object", "-w", "-t", "tree", "--stdin", stdin=b""),
        "empty-tree storage",
    )


def _tree_oid(vault_root: Path, revision: str, description: str) -> str:
    result = _git(
        vault_root,
        "rev-parse",
        "--verify",
        f"{revision}^{{tree}}",
        check=False,
    )
    if result.returncode != 0:
        raise GitStateError(f"{description} is not an available tree: {revision}")
    tree = _oid(result, description)
    if _git(vault_root, "cat-file", "-e", f"{tree}^{{tree}}", check=False).returncode:
        raise GitStateError(f"{description} tree is unavailable: {revision}")
    return tree


def _git_mode(mode: int) -> tuple[str, int]:
    if mode == 0o040000:
        return "directory", mode
    if mode == 0o120000:
        return "symlink", mode
    if mode in {0o100644, 0o100755}:
        return "file", mode
    return "special", mode


def snapshot_tree(vault_root: Path, tree: str) -> Snapshot:
    """Read one tree recursively without decoding or newline-splitting paths."""
    tree_oid = _tree_oid(Path(vault_root), tree, "tree snapshot")
    result = _git(Path(vault_root), "ls-tree", "-rz", "-t", "--full-tree", tree_oid)
    images = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        try:
            header, raw_path = record.split(b"\t", 1)
            mode_text, object_type, oid = header.split(b" ", 2)
            mode = int(mode_text, 8)
        except (ValueError, TypeError) as error:
            raise GitStateError("malformed NUL-delimited ls-tree record") from error
        RepoPath(raw_path)
        kind, normalized_mode = _git_mode(mode)
        data = None
        if kind in {"file", "symlink"}:
            data = _git(Path(vault_root), "cat-file", "blob", oid).stdout
        elif object_type != b"tree":
            kind = "special"
        images[raw_path] = FileImage(raw_path, kind, normalized_mode, data)
    return Snapshot(images)


def _normalized_live_image(
    root: bytes, raw_path: bytes, st: os.stat_result
) -> FileImage:
    absolute = os.path.join(root, raw_path)
    if stat.S_ISDIR(st.st_mode):
        return FileImage(raw_path, "directory", 0o040000, None)
    if stat.S_ISLNK(st.st_mode):
        target = os.readlink(absolute)
        if type(target) is not bytes:
            target = os.fsencode(target)
        after = os.lstat(absolute)
        if _stat_fingerprint(after) != _stat_fingerprint(st):
            raise GitStateError(
                f"worktree changed while snapshotting {encode_repo_path(raw_path)}"
            )
        return FileImage(raw_path, "symlink", 0o120000, target)
    if stat.S_ISREG(st.st_mode):
        with open(absolute, "rb") as stream:
            opened_before = os.fstat(stream.fileno())
            data = stream.read()
            opened_after = os.fstat(stream.fileno())
        if not (
            _stat_fingerprint(st)
            == _stat_fingerprint(opened_before)
            == _stat_fingerprint(opened_after)
        ):
            raise GitStateError(
                f"worktree changed while snapshotting {encode_repo_path(raw_path)}"
            )
        mode = 0o100755 if st.st_mode & 0o111 else 0o100644
        return FileImage(raw_path, "file", mode, data)
    return FileImage(raw_path, "special", stat.S_IFMT(st.st_mode), None)


def _stat_fingerprint(st: os.stat_result) -> tuple[int, ...]:
    return (
        st.st_dev,
        st.st_ino,
        st.st_mode,
        st.st_size,
        st.st_mtime_ns,
        st.st_ctime_ns,
    )


def snapshot_worktree(vault_root: Path) -> Snapshot:
    """Capture every live node once, excluding only the root .git subtree."""
    root = os.fsencode(os.path.abspath(Path(vault_root)))
    images = {}

    def visit(relative: bytes) -> None:
        absolute = root if not relative else os.path.join(root, relative)
        try:
            entries = list(os.scandir(absolute))
        except OSError as error:
            display = "vault" if not relative else encode_repo_path(relative)
            raise GitStateError(f"cannot snapshot {display}: {error}") from error
        for entry in entries:
            name = entry.name if type(entry.name) is bytes else os.fsencode(entry.name)
            if not relative and name == b".git":
                continue
            raw_path = name if not relative else relative + b"/" + name
            RepoPath(raw_path)
            try:
                st = entry.stat(follow_symlinks=False)
                image = _normalized_live_image(root, raw_path, st)
            except OSError as error:
                raise GitStateError(
                    f"cannot snapshot {encode_repo_path(raw_path)}: {error}"
                ) from error
            images[raw_path] = image
            if image.kind == "directory":
                visit(raw_path)

    visit(b"")
    return Snapshot(images)


def resolve_snapshots(
    vault_root: Path,
    *,
    git_base: str | None = None,
    candidate: str = "worktree",
) -> VerificationSnapshots:
    """Resolve base, expected HEAD, selected candidate, and live preimage once."""
    vault = Path(vault_root)
    if candidate not in {"worktree", "index", "HEAD"}:
        raise GitStateError(f"unknown git candidate: {candidate}")
    head_result = _git(vault, "rev-parse", "--verify", "HEAD", check=False)
    if head_result.returncode == 0:
        expected_head = _oid(head_result, "expected HEAD")
    else:
        symbolic = _git(vault, "symbolic-ref", "-q", "HEAD", check=False)
        if symbolic.returncode != 0:
            raise GitStateError(
                "expected HEAD is neither a commit nor an unborn branch"
            )
        try:
            head_ref = symbolic.stdout.decode("ascii").strip()
        except UnicodeDecodeError as error:
            raise GitStateError("expected HEAD symbolic ref is not ASCII") from error
        if (
            not head_ref
            or _git(vault, "check-ref-format", head_ref, check=False).returncode != 0
        ):
            raise GitStateError("expected HEAD has an invalid symbolic ref")
        exists = _git(vault, "show-ref", "--verify", "--quiet", head_ref, check=False)
        if exists.returncode == 0:
            raise GitStateError("expected HEAD ref exists but cannot be resolved")
        if exists.returncode != 1:
            raise GitStateError("expected HEAD unborn-state check failed")
        expected_head = None
    if expected_head is None:
        head_tree = _empty_tree(vault)
    else:
        head_tree = _tree_oid(vault, expected_head, "expected HEAD")
    base_tree = (
        head_tree if git_base is None else _tree_oid(vault, git_base, "explicit base")
    )
    base_snapshot = snapshot_tree(vault, base_tree)
    head_snapshot = (
        base_snapshot if head_tree == base_tree else snapshot_tree(vault, head_tree)
    )
    candidate_tree = None
    if candidate == "index":
        index_path_result = _git(vault, "rev-parse", "--git-path", "index")
        index_path = Path(os.fsdecode(index_path_result.stdout.strip()))
        if not index_path.is_absolute():
            index_path = vault / index_path
        try:
            index_bytes = index_path.read_bytes()
        except OSError as error:
            raise GitStateError(f"cannot snapshot live index: {error}") from error
        descriptor, private_index = tempfile.mkstemp(prefix="harness-index-snapshot-")
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(index_bytes)
            candidate_tree = _oid(
                _git(
                    vault,
                    "write-tree",
                    env={"GIT_INDEX_FILE": private_index},
                ),
                "index candidate",
            )
        finally:
            with suppress(FileNotFoundError):
                os.unlink(private_index)
        candidate_snapshot = snapshot_tree(vault, candidate_tree)
        live = snapshot_worktree(vault)
    elif candidate == "HEAD":
        candidate_tree = head_tree
        candidate_snapshot = head_snapshot
        live = snapshot_worktree(vault)
    else:
        live = snapshot_worktree(vault)
        candidate_snapshot = live
    return VerificationSnapshots(
        base_tree,
        base_snapshot,
        expected_head,
        head_tree,
        head_snapshot,
        candidate,
        candidate_snapshot,
        live,
    )


def blob_bytes(vault_root: Path, revision: str, relative: str | bytes) -> bytes | None:
    spec = (
        revision.encode() + b":" + relative
        if isinstance(relative, bytes)
        else f"{revision}:{relative}"
    )
    result = _git(Path(vault_root), "show", spec, check=False)
    return result.stdout if result.returncode == 0 else None


def revision_paths(vault_root: Path, revision: str, *prefixes: str) -> set[bytes]:
    result = _git(
        Path(vault_root),
        "ls-tree",
        "-rz",
        "--name-only",
        revision,
        "--",
        *prefixes,
        check=False,
    )
    return set() if result.returncode else {p for p in result.stdout.split(b"\0") if p}


def _root_bytes(vault_root: Path) -> bytes:
    return os.fsencode(os.path.abspath(Path(vault_root)))


def _absolute(vault_root: Path, raw_path: bytes) -> bytes:
    RepoPath(raw_path)
    root = _root_bytes(vault_root)
    current = root
    for component in raw_path.split(b"/")[:-1]:
        current = os.path.join(current, component)
        try:
            st = os.lstat(current)
        except FileNotFoundError as error:
            raise GitStateError(
                f"missing parent for {encode_repo_path(raw_path)}"
            ) from error
        if not stat.S_ISDIR(st.st_mode):
            raise GitStateError(f"unsafe parent for {encode_repo_path(raw_path)}")
    return os.path.join(root, raw_path)


def live_image(vault_root: Path, raw_path: bytes) -> FileImage | None:
    absolute = _absolute(vault_root, raw_path)
    try:
        st = os.lstat(absolute)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise GitStateError(
            f"cannot read {encode_repo_path(raw_path)}: {error}"
        ) from error
    return _normalized_live_image(_root_bytes(vault_root), raw_path, st)


_SCRATCH_PREFIX = b".harness-projection-"


def _scratch_owner(name: bytes) -> int | None:
    """Return the pid a projection scratch name encodes, else None."""
    if not name.startswith(_SCRATCH_PREFIX):
        return None
    parts = name[len(_SCRATCH_PREFIX) :].split(b"-")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        return None
    return int(parts[0])


def _owner_is_live(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        return True
    return True


def _sweep_stranded_scratch(vault_root: Path, outputs) -> None:
    """Remove projection scratch files stranded by a killed run.

    A scratch file must sit beside its destination or ``os.replace`` stops
    being atomic, so it cannot live outside the vault; one left by a SIGKILL
    is unreachable and would otherwise surface as an untracked vault node.
    Only files whose owning process is gone are swept, so a concurrent
    projection's live scratch is never touched.
    """
    swept = set()
    for output in outputs:
        parent = os.path.dirname(_absolute(vault_root, output.raw_path))
        if parent in swept:
            continue
        swept.add(parent)
        try:
            names = os.listdir(parent)
        except OSError:
            continue
        for name in names:
            raw = name if type(name) is bytes else os.fsencode(name)
            pid = _scratch_owner(raw)
            if pid is None or pid == os.getpid() or _owner_is_live(pid):
                continue
            with suppress(OSError):
                os.unlink(os.path.join(parent, raw))


def _temp_name(parent: bytes) -> tuple[int, bytes]:
    for number in range(1000):
        name = os.path.join(
            parent, f".harness-projection-{os.getpid()}-{number}".encode()
        )
        try:
            return os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), name
        except FileExistsError:
            continue
    raise OSError("cannot allocate projection temporary file")


def _atomic_install(vault_root: Path, output: CapturedOutput) -> None:
    absolute = _absolute(vault_root, output.raw_path)
    descriptor, temporary = _temp_name(os.path.dirname(absolute))
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            stream.write(output.data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o755 if output.mode == 0o100755 else 0o644)
        os.replace(temporary, absolute)
    finally:
        with suppress(FileNotFoundError):
            os.unlink(temporary)


def _restore_image(vault_root: Path, raw_path: bytes, image: FileImage | None) -> None:
    absolute = _absolute(vault_root, raw_path)
    if image is None:
        os.unlink(absolute)
    elif image.kind == "file":
        _atomic_install(
            vault_root, CapturedOutput(raw_path, image.mode, image.data or b"")
        )
    elif image.kind == "symlink":
        temporary = absolute + b".harness-rollback"
        try:
            os.symlink(image.data or b"", temporary)
            os.replace(temporary, absolute)
        finally:
            with suppress(FileNotFoundError):
                os.unlink(temporary)
    else:
        raise GitStateError("cannot restore a non-file projection preimage")


def _unique_outputs(outputs) -> list[CapturedOutput]:
    by_path = {}
    for output in outputs:
        if not isinstance(output, CapturedOutput):
            raise TypeError("projection outputs must be CapturedOutput values")
        if output.raw_path in by_path:
            raise GitStateError(
                f"duplicate projection output {encode_repo_path(output.raw_path)}"
            )
        by_path[output.raw_path] = output
    return [by_path[path] for path in sorted(by_path)]


def apply_outputs(
    vault_root: Path, preimage: Snapshot, outputs
) -> tuple[CapturedOutput, ...]:
    """Apply one sorted projection with preimage CAS and owned rollback."""
    ordered = _unique_outputs(outputs)
    _sweep_stranded_scratch(vault_root, ordered)
    for output in ordered:
        if live_image(vault_root, output.raw_path) != preimage.image(output.raw_path):
            raise GitStateError(
                f"projection destination diverged: {encode_repo_path(output.raw_path)}"
            )
    installed = []
    failed_path = None
    try:
        for output in ordered:
            failed_path = output.raw_path
            if live_image(vault_root, output.raw_path) != preimage.image(
                output.raw_path
            ):
                raise GitStateError("diverged before atomic replace")
            _atomic_install(vault_root, output)
            installed.append(output)
    except (OSError, GitStateError) as primary:
        primary_path = failed_path or (ordered[0].raw_path if ordered else b"unknown")
        message = f"projection failed at {encode_repo_path(primary_path)}: {primary}"
        try:
            rollback_outputs(vault_root, preimage, installed)
        except GitStateError as rollback:
            message += f"; {rollback}"
        raise GitStateError(message) from primary
    return tuple(ordered)


def rollback_outputs(vault_root: Path, preimage: Snapshot, outputs) -> None:
    """Restore owned installed postimages without overwriting a successor."""
    ordered = _unique_outputs(outputs)
    first_error = None
    first_path = None
    for output in reversed(ordered):
        # The try/except cannot be hoisted out of the loop: rollback must attempt
        # every remaining output and surface only the first failure.
        try:
            if live_image(vault_root, output.raw_path) != output.image:
                raise GitStateError("diverged")
            _restore_image(vault_root, output.raw_path, preimage.image(output.raw_path))
        except (OSError, GitStateError) as error:  # noqa: PERF203
            if first_error is None:
                first_error = error
                first_path = output.raw_path
    if first_error is not None and first_path is not None:
        raise GitStateError(
            f"rollback failed at {encode_repo_path(first_path)}: {first_error}"
        ) from first_error


def validate_manifest_destination(vault_root: Path, destination: Path) -> Path:
    vault = Path(vault_root).resolve()
    path = Path(destination)
    try:
        resolved = path.resolve(strict=False)
    except OSError as error:
        raise GitStateError(f"cannot resolve changed-path manifest: {error}") from error
    try:
        resolved.relative_to(vault)
    except ValueError:
        pass
    else:
        raise GitStateError("changed-path manifest must be outside the vault")
    parent = resolved.parent
    if not parent.is_dir():
        raise GitStateError("changed-path manifest parent must already exist")
    if resolved.exists():
        if not resolved.is_file():
            raise GitStateError("changed-path manifest destination must be a file")
        try:
            descriptor = os.open(resolved, os.O_WRONLY)
            os.close(descriptor)
        except OSError as error:
            raise GitStateError(
                f"changed-path manifest is not writable: {error}"
            ) from error
    else:
        try:
            descriptor, probe = tempfile.mkstemp(
                prefix=".harness-manifest-probe-", dir=parent
            )
            os.close(descriptor)
            os.unlink(probe)
        except OSError as error:
            raise GitStateError(
                f"changed-path manifest parent is not writable: {error}"
            ) from error
    return resolved


def _allowed_manifest_path(raw_path: bytes, image: FileImage | None) -> bool:
    if image is None or image.kind != "file" or not raw_path.endswith(b".md"):
        return False
    if raw_path == b"inbox/review-queue.md":
        return True
    return any(
        raw_path.startswith(prefix)
        for prefix in (b"literatures/", b"synthesis/", b"projects/")
    )


def validate_planned_outputs(outputs) -> tuple[CapturedOutput, ...]:
    """Validate the complete verifier output allowlist before the first write."""
    planned = tuple(_unique_outputs(outputs))
    for output in planned:
        if not _allowed_manifest_path(output.raw_path, output.image):
            raise GitStateError(
                f"planned output is outside the verifier allowlist: "
                f"{encode_repo_path(output.raw_path)}"
            )
    return planned


def audit_and_write_manifest(
    vault_root: Path,
    before: Snapshot,
    planned_outputs,
    destination: Path,
) -> tuple[CapturedOutput, ...]:
    """Require planned == actual == manifest and return exact after buffers."""
    manifest = validate_manifest_destination(vault_root, destination)
    planned = _unique_outputs(planned_outputs)
    planned_by_path = {output.raw_path: output for output in planned}
    planned_paths = set(planned_by_path)
    after = snapshot_worktree(vault_root)
    actual_paths = {
        raw_path
        for raw_path in set(before.images) | set(after.images)
        if before.image(raw_path) != after.image(raw_path)
    }
    if actual_paths != planned_paths:
        raise GitStateError("planned and actual changed-path sets differ")
    for raw_path in sorted(actual_paths):
        image = after.image(raw_path)
        if not _allowed_manifest_path(raw_path, image):
            raise GitStateError(
                f"changed path is outside the verifier allowlist: {encode_repo_path(raw_path)}"
            )
        if image != planned_by_path[raw_path].image:
            raise GitStateError(
                f"actual postimage differs from planned output: {encode_repo_path(raw_path)}"
            )
    try:
        with manifest.open("wb") as stream:
            for output in planned:
                stream.write(output.raw_path + b"\0")
    except OSError as error:
        raise GitStateError(f"cannot write changed-path manifest: {error}") from error
    return tuple(planned)


def _snapshot_index(vault_root: Path, raw_paths: set[bytes]) -> Snapshot:
    result = _git(Path(vault_root), "ls-files", "--stage", "-z")
    images = {}
    stages: dict[bytes, list[int]] = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        try:
            header, raw_path = record.split(b"\t", 1)
            mode_text, oid, stage_text = header.split(b" ", 2)
            mode, stage = int(mode_text, 8), int(stage_text)
        except (ValueError, TypeError) as error:
            raise GitStateError("malformed NUL-delimited index record") from error
        if raw_path not in raw_paths:
            continue
        stages.setdefault(raw_path, []).append(stage)
        if stage == 0:
            kind, normalized_mode = _git_mode(mode)
            data = None
            if kind in {"file", "symlink"}:
                data = _git(Path(vault_root), "cat-file", "blob", oid).stdout
            images[raw_path] = FileImage(raw_path, kind, normalized_mode, data)
    if any(values != [0] for values in stages.values()):
        raise GitStateError("live index contains unmerged entries")
    return Snapshot(images)


def validate_dirty_overlap(
    vault_root: Path, snapshots: VerificationSnapshots, outputs
) -> None:
    """Refuse publication outputs that differ from expected HEAD anywhere."""
    ordered = _unique_outputs(outputs)
    head = snapshots.head
    index = _snapshot_index(vault_root, {output.raw_path for output in ordered})
    for output in ordered:
        expected = head.image(output.raw_path)
        if (
            snapshots.candidate.image(output.raw_path) != expected
            or snapshots.live.image(output.raw_path) != expected
            or index.image(output.raw_path) != expected
        ):
            raise GitStateError(
                f"dirty overlapping output: {encode_repo_path(output.raw_path)}"
            )


def publish_outputs(
    vault_root: Path, snapshots: VerificationSnapshots, outputs, message: str
) -> str | None:
    """Publish exact captured output blobs with a private index and HEAD CAS."""
    ordered = _unique_outputs(outputs)
    if not ordered:
        return None
    if type(message) is not str or not message.strip() or "\0" in message:
        raise GitStateError("snapshot commit message must be nonempty")
    vault = Path(vault_root)
    blob_oids = {
        output.raw_path: _oid(
            _git(vault, "hash-object", "-w", "--stdin", stdin=output.data),
            "projection blob",
        )
        for output in ordered
    }
    try:
        descriptor, index_name = tempfile.mkstemp(prefix="harness-publish-index-")
    except OSError as error:
        raise GitStateError("cannot create private publication index") from error
    os.close(descriptor)
    os.unlink(index_name)
    env = {"GIT_INDEX_FILE": index_name}
    try:
        _git(vault, "read-tree", snapshots.head_tree, env=env)
        for output in ordered:
            cacheinfo = (
                f"{output.mode:o},{blob_oids[output.raw_path]},".encode()
                + output.raw_path
            )
            try:
                _git(vault, "update-index", "--add", "--cacheinfo", cacheinfo, env=env)
            except GitStateError as error:
                raise GitStateError(
                    f"cannot publish {encode_repo_path(output.raw_path)}: {error}"
                ) from error
        tree = _oid(_git(vault, "write-tree", env=env), "projection tree")
        commit_args = ["commit-tree", tree]
        if snapshots.expected_head is not None:
            commit_args.extend(["-p", snapshots.expected_head])
        commit = _oid(
            _git(vault, *commit_args, stdin=(message.rstrip() + "\n").encode()),
            "projection commit",
        )
        expected_old = snapshots.expected_head or ZERO_OID
        published = _git(
            vault,
            "update-ref",
            "HEAD",
            commit,
            expected_old,
            check=False,
        )
        if published.returncode != 0:
            raise GitStateError(
                f"concurrent HEAD update-ref failed with status {published.returncode}"
            )
        return commit
    finally:
        with suppress(FileNotFoundError):
            os.unlink(index_name)


def materialize_snapshot(snapshot: Snapshot, destination: Path) -> None:
    """Materialize the safe regular-file/directory view used by collectors."""
    root = os.fsencode(destination)
    os.makedirs(root, exist_ok=True)
    for raw_path in sorted(snapshot.images):
        image = snapshot.images[raw_path]
        absolute = os.path.join(root, raw_path)
        if image.kind == "directory":
            os.makedirs(absolute, exist_ok=True)
        elif image.kind == "file":
            os.makedirs(os.path.dirname(absolute), exist_ok=True)
            with open(absolute, "wb") as stream:
                stream.write(image.data or b"")
            os.chmod(absolute, 0o755 if image.mode == 0o100755 else 0o644)
        # Symlinks and special nodes stay solely in the immutable candidate.
        # Creating them in the planning tree could let a collector follow a
        # mutable target outside the captured snapshot.


def restore_candidate_nonfiles(candidate: Snapshot, planned: Snapshot) -> Snapshot:
    """Overlay skipped immutable non-files after safe planning-tree capture."""
    images = dict(planned.images)
    for raw_path, image in candidate.images.items():
        if image.kind == "file":
            continue
        actual = planned.image(raw_path)
        if image.kind == "directory":
            if actual is None or actual.kind != "directory":
                raise GitStateError(
                    f"planning changed candidate directory {encode_repo_path(raw_path)}"
                )
        elif actual is not None:
            raise GitStateError(
                f"planning replaced candidate non-file {encode_repo_path(raw_path)}"
            )
        images[raw_path] = image
    return Snapshot(images)


def outputs_between(before: Snapshot, after: Snapshot) -> tuple[CapturedOutput, ...]:
    """Return regular-file postimages that differ from the selected candidate."""
    outputs = []
    for raw_path in sorted(set(before.images) | set(after.images)):
        if before.image(raw_path) == after.image(raw_path):
            continue
        image = after.image(raw_path)
        if image is None or image.kind != "file":
            raise GitStateError(
                f"projection produced unsupported node change {encode_repo_path(raw_path)}"
            )
        outputs.append(CapturedOutput(raw_path, image.mode, image.data or b""))
    return tuple(outputs)
