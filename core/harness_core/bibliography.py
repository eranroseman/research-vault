"""The in-repo citekey universe: x/bibliography.json (spec §4)."""

import json
import os
import shutil
import stat
import subprocess
import tempfile
import time
from pathlib import Path
from typing import NamedTuple

from . import Result
from .zotero import ZoteroError

BIB_PATH = "x/bibliography.json"


class Bibliography:
    def __init__(self, items):
        self._by_id = {i["id"]: i for i in items}

    @property
    def citekeys(self):
        return set(self._by_id)

    def entry(self, citekey):
        return self._by_id.get(citekey)


class BibliographyError(ValueError):
    """A bibliography that cannot safely participate in verification."""

    def __init__(self, message: str, result: Result):
        super().__init__(message)
        self.result = result


class AutoexportObservation(NamedTuple):
    result: Result
    detail: str
    staleness: Result
    staleness_detail: str


class _TargetState(NamedTuple):
    result: Result
    detail: str
    fingerprint: list[tuple[str, str]] | None = None
    snapshot: bytes | None = None
    contained: bool = True


class _TargetBoundary(NamedTuple):
    vault: Path
    target: Path
    ancestor_ids: tuple[tuple[int, int], ...]


class _ContainmentError(OSError):
    """The lexical vault-to-bibliography path no longer names its pinned tree."""


class _IndexIntentError(OSError):
    """The live bibliography index entry contains user staging intent."""


class _IndexPublicationError(OSError):
    """The live index could not be published and HEAD could not be restored."""


class _LiveIndexLock(NamedTuple):
    live_index: Path
    path: Path
    descriptor: int


def _path(vault_root):
    return Path(os.path.abspath(os.fspath(vault_root))) / BIB_PATH


def load(vault_root) -> Bibliography:
    p = _path(vault_root)
    try:
        try:
            path_stat = p.stat()
        except FileNotFoundError:
            return Bibliography([])
        if not stat.S_ISREG(path_stat.st_mode):
            raise BibliographyError(
                "bibliography is not a regular file", Result.UNMATCHED
            )
        text = p.read_text()
    except BibliographyError:
        raise
    except (OSError, UnicodeError) as error:
        raise BibliographyError(
            "bibliography is unreadable", Result.UNREACHABLE
        ) from error
    try:
        items = json.loads(text)
        _validate_items(items)
    except (TypeError, ValueError) as error:
        raise BibliographyError(
            "bibliography has invalid JSON or schema", Result.UNMATCHED
        ) from error
    return Bibliography(items)


def _validate_items(items) -> None:
    if not isinstance(items, list):
        raise ValueError("bibliography must be a list")
    seen = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"bibliography item {index} must be an object")
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError(f"bibliography item {index} has no valid id")
        if (
            item_id in {".", ".."}
            or "/" in item_id
            or "\\" in item_id
            or "\0" in item_id
            or "\r" in item_id
            or "\n" in item_id
            or Path(item_id).is_absolute()
        ):
            raise ValueError(f"bibliography item {index} has an unsafe id")
        if item_id in seen:
            raise ValueError(f"bibliography item {index} has a duplicate id")
        seen.add(item_id)
        for field in ("DOI", "doi"):
            value = item.get(field)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"bibliography item {index} has a non-string {field}")


def _absolute_vault(vault_root) -> Path:
    return Path(os.path.abspath(os.fspath(vault_root)))


def _open_parent_chain(target: Path, expected_ids=None):
    """Open the target's parent from / without following a symlink component."""
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(os.sep, flags)
    identities = []
    try:
        root_stat = os.fstat(descriptor)
        identities.append((root_stat.st_dev, root_stat.st_ino))
        if expected_ids is not None and identities[0] != expected_ids[0]:
            raise _ContainmentError("filesystem root identity changed")
        for index, component in enumerate(target.parent.parts[1:], start=1):
            child = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
            child_stat = os.fstat(descriptor)
            identity = (child_stat.st_dev, child_stat.st_ino)
            identities.append(identity)
            if expected_ids is not None and (
                index >= len(expected_ids) or identity != expected_ids[index]
            ):
                raise _ContainmentError(
                    "vault-to-bibliography ancestor identity changed"
                )
        if expected_ids is not None and len(identities) != len(expected_ids):
            raise _ContainmentError("vault-to-bibliography ancestor chain changed")
        return descriptor, tuple(identities)
    except Exception:
        os.close(descriptor)
        raise


def _pin_target_boundary(vault_root) -> _TargetBoundary:
    vault = _absolute_vault(vault_root)
    target = vault / BIB_PATH
    try:
        descriptor, identities = _open_parent_chain(target)
    except OSError as error:
        raise _ContainmentError(
            f"unsafe vault-to-bibliography path: {error}"
        ) from error
    os.close(descriptor)
    return _TargetBoundary(vault, target, identities)


def _guard_boundary(boundary: _TargetBoundary) -> None:
    try:
        descriptor, _identities = _open_parent_chain(
            boundary.target, boundary.ancestor_ids
        )
    except OSError as error:
        raise _ContainmentError(
            f"unsafe vault-to-bibliography path: {error}"
        ) from error
    os.close(descriptor)


def _git_output(command, *, vault, env=None, input_bytes=None) -> bytes:
    return subprocess.run(
        command,
        cwd=vault,
        env=env,
        check=True,
        input=input_bytes,
        capture_output=True,
    ).stdout


def _head_bibliography_entry(vault: Path, expected_parent: str | None):
    if expected_parent is None:
        return None
    output = _git_output(
        ["git", "ls-tree", "-z", expected_parent, "--", BIB_PATH], vault=vault
    )
    if not output:
        return None
    metadata, _path = output.removesuffix(b"\0").split(b"\t", 1)
    mode, object_type, object_id = metadata.split()
    return mode, object_type, object_id


def _index_bibliography_entry(vault: Path, environment):
    output = _git_output(
        ["git", "ls-files", "--stage", "-z", "--", BIB_PATH],
        vault=vault,
        env=environment,
    )
    records = [record for record in output.split(b"\0") if record]
    if not records:
        return None
    if len(records) != 1:
        return b"conflict", output, b""
    metadata, _path = records[0].split(b"\t", 1)
    mode, object_id, stage = metadata.split()
    return mode, b"blob" if stage == b"0" else b"conflict", object_id


def _lock_path_is_owned(lock: _LiveIndexLock) -> bool:
    try:
        descriptor_stat = os.fstat(lock.descriptor)
        path_stat = os.stat(lock.path, follow_symlinks=False)
    except OSError:
        return False
    return (descriptor_stat.st_dev, descriptor_stat.st_ino) == (
        path_stat.st_dev,
        path_stat.st_ino,
    )


def _release_live_index_lock(lock: _LiveIndexLock) -> None:
    try:
        if _lock_path_is_owned(lock):
            lock.path.unlink()
    finally:
        os.close(lock.descriptor)


def _refresh_live_index_lock(lock: _LiveIndexLock) -> _LiveIndexLock:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(lock.path, flags)
    refreshed = _LiveIndexLock(lock.live_index, lock.path, descriptor)
    if not _lock_path_is_owned(refreshed):
        os.close(descriptor)
        raise OSError("live index lock changed while being updated")
    os.close(lock.descriptor)
    return refreshed


def _acquire_live_index_lock(vault: Path, empty_index: Path) -> _LiveIndexLock:
    raw_path = (
        _git_output(["git", "rev-parse", "--git-path", "index"], vault=vault)
        .decode()
        .strip()
    )
    index_path = Path(raw_path)
    if not index_path.is_absolute():
        index_path = vault / index_path
    lock_path = Path(f"{index_path}.lock")
    descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
    lock = _LiveIndexLock(index_path, lock_path, descriptor)
    try:
        source = index_path if index_path.exists() else empty_index
        with (
            source.open("rb") as current,
            os.fdopen(os.dup(descriptor), "wb") as locked,
        ):
            shutil.copyfileobj(current, locked)
    except BaseException:
        _release_live_index_lock(lock)
        raise
    return lock


def _rollback_head(vault: Path, expected_parent: str | None, commit: str) -> None:
    command = (
        ["git", "update-ref", "HEAD", expected_parent, commit]
        if expected_parent
        else ["git", "update-ref", "-d", "HEAD", commit]
    )
    subprocess.run(command, cwd=vault, check=True, capture_output=True)


def commit_autoexport(
    vault_root, snapshot: bytes, *, _boundary: _TargetBoundary | None = None
) -> bool:
    """Commit exactly a validated BBT snapshot without rereading its target."""
    if not isinstance(snapshot, bytes):
        raise TypeError("snapshot must be bytes")
    boundary = _pin_target_boundary(vault_root) if _boundary is None else _boundary
    _guard_boundary(boundary)
    vault = boundary.vault

    head = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=vault,
        check=False,
        capture_output=True,
    )
    has_head = head.returncode == 0
    expected_parent = head.stdout.decode().strip() if has_head else None
    if has_head:
        committed = subprocess.run(
            ["git", "show", f"{expected_parent}:{BIB_PATH}"],
            cwd=vault,
            check=False,
            capture_output=True,
        )
        if committed.returncode == 0 and committed.stdout == snapshot:
            return False

    blob = (
        _git_output(
            ["git", "hash-object", "-w", "--stdin"],
            vault=vault,
            input_bytes=snapshot,
        )
        .decode()
        .strip()
    )
    expected_old = expected_parent or ("0" * len(blob))

    with tempfile.TemporaryDirectory(prefix="harness-bibliography-index-") as tmp:
        tree_index = str(Path(tmp) / "tree-index")
        environment = os.environ.copy()
        environment["GIT_INDEX_FILE"] = tree_index
        subprocess.run(
            ["git", "read-tree", expected_parent]
            if expected_parent
            else ["git", "read-tree", "--empty"],
            cwd=vault,
            env=environment,
            check=True,
        )
        subprocess.run(
            [
                "git",
                "update-index",
                "--add",
                "--cacheinfo",
                "100644",
                blob,
                BIB_PATH,
            ],
            cwd=vault,
            env=environment,
            check=True,
        )
        tree = (
            _git_output(["git", "write-tree"], vault=vault, env=environment)
            .decode()
            .strip()
        )
        commit_command = ["git", "commit-tree", tree]
        if expected_parent:
            commit_command.extend(["-p", expected_parent])
        commit = (
            _git_output(
                commit_command,
                vault=vault,
                input_bytes=b"chore: bibliography export\n",
            )
            .decode()
            .strip()
        )

        empty_index = Path(tmp) / "empty-index"
        empty_environment = os.environ.copy()
        empty_environment["GIT_INDEX_FILE"] = str(empty_index)
        subprocess.run(
            ["git", "read-tree", "--empty"],
            cwd=vault,
            env=empty_environment,
            check=True,
        )

        live_index_lock = _acquire_live_index_lock(vault, empty_index)
        try:
            locked_environment = os.environ.copy()
            locked_environment["GIT_INDEX_FILE"] = str(live_index_lock.path)
            if _index_bibliography_entry(
                vault, locked_environment
            ) != _head_bibliography_entry(vault, expected_parent):
                raise _IndexIntentError(
                    "live index bibliography differs from expected HEAD"
                )
            subprocess.run(
                [
                    "git",
                    "update-index",
                    "--add",
                    "--cacheinfo",
                    "100644",
                    blob,
                    BIB_PATH,
                ],
                cwd=vault,
                env=locked_environment,
                check=True,
            )
            live_index_lock = _refresh_live_index_lock(live_index_lock)
            subprocess.run(
                ["git", "update-ref", "HEAD", commit, expected_old],
                cwd=vault,
                check=True,
            )
            try:
                os.replace(live_index_lock.path, live_index_lock.live_index)
            except OSError as publication_error:
                try:
                    _rollback_head(vault, expected_parent, commit)
                except (OSError, subprocess.SubprocessError) as rollback_error:
                    raise _IndexPublicationError(
                        "index publication failed and could not roll back HEAD "
                        f"safely: {publication_error}; {rollback_error}"
                    ) from rollback_error
                raise
        finally:
            _release_live_index_lock(live_index_lock)
    return True


def _fingerprint(items):
    _validate_items(items)
    fingerprint = []
    for index, item in enumerate(items):
        item_id = item.get("id")
        title = item.get("title", "")
        if not isinstance(title, str):
            raise ValueError(f"bibliography item {index} has no valid title")
        fingerprint.append((item_id, title))
    return sorted(fingerprint)


def _unsafe_target(detail: str) -> _TargetState:
    return _TargetState(Result.UNMATCHED, detail, contained=False)


def _target_state(boundary: _TargetBoundary) -> _TargetState:
    try:
        parent_fd, _identities = _open_parent_chain(
            boundary.target, boundary.ancestor_ids
        )
    except OSError as error:
        return _unsafe_target(f"unsafe vault-to-bibliography path: {error}")

    descriptor = None
    try:
        name = boundary.target.name
        try:
            path_stat = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return _TargetState(Result.UNMATCHED, "bibliography auto-export absent")
        except OSError as error:
            return _TargetState(
                Result.UNREACHABLE,
                f"bibliography auto-export unreadable: {error}",
            )
        if stat.S_ISLNK(path_stat.st_mode):
            return _unsafe_target("bibliography auto-export is a symlink")
        if not stat.S_ISREG(path_stat.st_mode):
            return _TargetState(
                Result.UNMATCHED,
                "bibliography auto-export is not a regular file",
            )

        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(name, flags, dir_fd=parent_fd)
        except FileNotFoundError:
            return _TargetState(Result.UNMATCHED, "bibliography auto-export absent")
        except OSError as error:
            return _TargetState(
                Result.UNREACHABLE,
                f"bibliography auto-export unreadable: {error}",
            )
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode) or (
            path_stat.st_dev,
            path_stat.st_ino,
        ) != (opened_stat.st_dev, opened_stat.st_ino):
            return _unsafe_target("bibliography auto-export changed while being read")
        with os.fdopen(descriptor, "rb") as export:
            descriptor = None
            snapshot = export.read()
    except OSError as error:
        return _TargetState(
            Result.UNREACHABLE,
            f"bibliography auto-export unreadable: {error}",
        )
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(parent_fd)

    try:
        fingerprint = _fingerprint(json.loads(snapshot.decode("utf-8")))
    except UnicodeError as error:
        return _TargetState(
            Result.UNREACHABLE,
            f"bibliography auto-export unreadable: {error}",
        )
    except (TypeError, ValueError):
        return _TargetState(
            Result.UNMATCHED,
            "bibliography auto-export has invalid JSON or schema",
        )
    return _TargetState(
        Result.MATCHED,
        "bibliography auto-export is valid",
        fingerprint,
        snapshot,
    )


def _compare_target(state: _TargetState, evidence) -> _TargetState:
    if state.result is not Result.MATCHED:
        return state
    if state.fingerprint != evidence:
        return _TargetState(
            Result.UNMATCHED,
            "bibliography auto-export does not match on-demand export",
            state.fingerprint,
            state.snapshot,
            state.contained,
        )
    return _TargetState(
        Result.MATCHED,
        "bibliography auto-export matches on-demand export",
        state.fingerprint,
        state.snapshot,
        state.contained,
    )


def _poll_window(boundary, evidence, settle_seconds, poll_interval, clock, sleeper):
    deadline = clock() + max(0, settle_seconds)
    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            return _compare_target(_target_state(boundary), evidence)
        sleeper(min(poll_interval, remaining))
        if clock() >= deadline:
            return _compare_target(_target_state(boundary), evidence)
        compared = _compare_target(_target_state(boundary), evidence)
        if not compared.contained or compared.result in {
            Result.MATCHED,
            Result.UNREACHABLE,
        }:
            return compared


def _observation(state: _TargetState) -> AutoexportObservation:
    return AutoexportObservation(state.result, state.detail, state.result, state.detail)


def _committed_state(vault_root, evidence) -> _TargetState:
    try:
        committed = subprocess.run(
            ["git", "show", f"HEAD:{BIB_PATH}"],
            cwd=vault_root,
            check=False,
            capture_output=True,
        )
    except OSError as error:
        return _TargetState(
            Result.UNREACHABLE,
            f"committed bibliography is unreadable: {error}",
        )
    if committed.returncode != 0:
        return _TargetState(
            Result.UNREACHABLE, "committed bibliography cannot be read from HEAD"
        )
    try:
        fingerprint = _fingerprint(json.loads(committed.stdout.decode("utf-8")))
    except UnicodeError as error:
        return _TargetState(
            Result.UNREACHABLE, f"committed bibliography is unreadable: {error}"
        )
    except (TypeError, ValueError):
        return _TargetState(
            Result.UNMATCHED,
            "committed bibliography has invalid JSON or schema",
        )
    if fingerprint != evidence:
        return _TargetState(
            Result.UNMATCHED,
            "committed bibliography does not match on-demand export",
            fingerprint,
        )
    return _TargetState(
        Result.MATCHED,
        "committed bibliography matches on-demand export",
        fingerprint,
    )


def observe_autoexport(
    vault_root,
    client,
    *,
    settle_seconds=60,
    poll_interval=1,
    monotonic=None,
    sleep=None,
) -> AutoexportObservation:
    """Observe BBT's sole-writer target and commit it only after it matches evidence."""
    if poll_interval <= 0:
        raise ValueError("poll_interval must be greater than zero")
    clock = time.monotonic if monotonic is None else monotonic
    sleeper = time.sleep if sleep is None else sleep

    try:
        boundary = _pin_target_boundary(vault_root)
    except OSError as error:
        boundary = None
        captured = _unsafe_target(f"unsafe vault-to-bibliography path: {error}")
    else:
        captured = _target_state(boundary)
    try:
        evidence = _fingerprint(client.export_csl(None))
    except ZoteroError as error:
        failed = _TargetState(error.result, str(error))
        return _observation(failed)
    except (TypeError, ValueError) as error:
        failed = _TargetState(
            Result.UNREACHABLE, f"malformed on-demand export: {error}"
        )
        return _observation(failed)
    if boundary is None or not captured.contained:
        return _observation(captured)
    if captured.result is Result.UNREACHABLE:
        return _observation(captured)

    compared = _compare_target(captured, evidence)
    if compared.result is not Result.MATCHED:
        compared = _poll_window(
            boundary,
            evidence,
            settle_seconds,
            poll_interval,
            clock,
            sleeper,
        )
    if not compared.contained or compared.result is not Result.MATCHED:
        return _observation(compared)

    snapshot = compared.snapshot
    assert snapshot is not None
    try:
        commit_autoexport(boundary.vault, snapshot, _boundary=boundary)
    except _ContainmentError as error:
        return _observation(_unsafe_target(str(error)))
    except (OSError, subprocess.SubprocessError) as error:
        final = _compare_target(_target_state(boundary), evidence)
        return AutoexportObservation(
            Result.UNREACHABLE,
            f"bibliography commit failed: {error}",
            final.result,
            final.detail,
        )

    final = _compare_target(_target_state(boundary), evidence)
    committed = _committed_state(boundary.vault, evidence)
    if committed.result is not Result.MATCHED:
        return AutoexportObservation(
            committed.result,
            committed.detail,
            final.result,
            final.detail,
        )
    # The validated window comparison is the result; a target BBT rewrote after
    # it was captured is warn-only staleness for the next pass, not a failure.
    return AutoexportObservation(
        compared.result,
        compared.detail,
        final.result,
        final.detail,
    )


def staleness(vault_root, client) -> Result:
    p = _path(vault_root)
    try:
        path_stat = p.stat()
    except FileNotFoundError:
        return Result.SKIPPED
    except OSError:
        return Result.UNREACHABLE
    if not stat.S_ISREG(path_stat.st_mode):
        return Result.UNMATCHED
    try:
        fresh = client.export_csl(None)
        fresh_fingerprint = _fingerprint(fresh)
    except (ZoteroError, TypeError, ValueError):
        return Result.UNREACHABLE
    try:
        committed_text = p.read_text()
    except (OSError, UnicodeError):
        return Result.UNREACHABLE
    try:
        committed = json.loads(committed_text)
        committed_fingerprint = _fingerprint(committed)
    except (TypeError, ValueError):
        return Result.UNMATCHED
    return (
        Result.MATCHED
        if committed_fingerprint == fresh_fingerprint
        else Result.UNMATCHED
    )
