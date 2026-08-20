"""The in-repo citekey universe: x/bibliography.json (spec §4)."""

import json
import os
import stat
import subprocess
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


def _path(vault_root):
    return Path(vault_root) / BIB_PATH


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


def commit_autoexport(vault_root) -> bool:
    """Commit the genuine BBT target without changing its bytes or other state."""
    p = _path(vault_root)
    head = subprocess.run(
        ["git", "show", f"HEAD:{BIB_PATH}"],
        cwd=vault_root,
        check=False,
        capture_output=True,
    )
    if head.returncode == 0 and head.stdout == p.read_bytes():
        return False
    subprocess.run(["git", "add", "--", BIB_PATH], cwd=vault_root, check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-q",
            "--no-verify",
            "--only",
            "-m",
            "chore: bibliography export",
            "--",
            BIB_PATH,
        ],
        cwd=vault_root,
        check=True,
    )
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


def _target_state(vault_root) -> _TargetState:
    target = _path(vault_root)
    try:
        parent_stat = target.parent.lstat()
    except FileNotFoundError:
        return _TargetState(Result.UNMATCHED, "bibliography auto-export absent")
    except OSError as error:
        return _TargetState(
            Result.UNREACHABLE, f"bibliography auto-export unreadable: {error}"
        )
    if not stat.S_ISDIR(parent_stat.st_mode):
        return _TargetState(
            Result.UNMATCHED,
            "bibliography auto-export parent is not a regular directory",
        )
    try:
        path_stat = target.lstat()
    except FileNotFoundError:
        return _TargetState(Result.UNMATCHED, "bibliography auto-export absent")
    except OSError as error:
        return _TargetState(
            Result.UNREACHABLE, f"bibliography auto-export unreadable: {error}"
        )
    if not stat.S_ISREG(path_stat.st_mode):
        return _TargetState(
            Result.UNMATCHED,
            "bibliography auto-export is not a regular file",
        )

    descriptor = None
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(target, flags)
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode) or (
            path_stat.st_dev,
            path_stat.st_ino,
        ) != (opened_stat.st_dev, opened_stat.st_ino):
            return _TargetState(
                Result.UNMATCHED,
                "bibliography auto-export changed while being read",
            )
        with os.fdopen(descriptor, "r", encoding="utf-8") as export:
            descriptor = None
            text = export.read()
    except (OSError, UnicodeError) as error:
        return _TargetState(
            Result.UNREACHABLE, f"bibliography auto-export unreadable: {error}"
        )
    finally:
        if descriptor is not None:
            os.close(descriptor)

    try:
        fingerprint = _fingerprint(json.loads(text))
    except (TypeError, ValueError):
        return _TargetState(
            Result.UNMATCHED,
            "bibliography auto-export has invalid JSON or schema",
        )
    return _TargetState(
        Result.MATCHED, "bibliography auto-export is valid", fingerprint
    )


def _compare_target(state: _TargetState, evidence) -> _TargetState:
    if state.result is not Result.MATCHED:
        return state
    if state.fingerprint != evidence:
        return _TargetState(
            Result.UNMATCHED,
            "bibliography auto-export does not match on-demand export",
            state.fingerprint,
        )
    return _TargetState(
        Result.MATCHED,
        "bibliography auto-export matches on-demand export",
        state.fingerprint,
    )


def _poll_window(vault_root, evidence, settle_seconds, poll_interval, clock, sleeper):
    deadline = clock() + max(0, settle_seconds)
    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            return _compare_target(_target_state(vault_root), evidence)
        sleeper(min(poll_interval, remaining))
        if clock() >= deadline:
            return _compare_target(_target_state(vault_root), evidence)
        compared = _compare_target(_target_state(vault_root), evidence)
        if compared.result in {Result.MATCHED, Result.UNREACHABLE}:
            return compared


def _observation(state: _TargetState) -> AutoexportObservation:
    return AutoexportObservation(state.result, state.detail, state.result, state.detail)


def _committed_state(vault_root, evidence) -> _TargetState:
    committed = subprocess.run(
        ["git", "show", f"HEAD:{BIB_PATH}"],
        cwd=vault_root,
        check=False,
        capture_output=True,
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

    captured = _target_state(vault_root)
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
    if captured.result is Result.UNREACHABLE:
        return _observation(captured)

    compared = _compare_target(captured, evidence)
    if compared.result is not Result.MATCHED:
        compared = _poll_window(
            vault_root,
            evidence,
            settle_seconds,
            poll_interval,
            clock,
            sleeper,
        )
    if compared.result is Result.UNREACHABLE:
        return _observation(compared)
    if compared.result is not Result.MATCHED:
        try:
            client.register_autoexport(str(_path(vault_root)))
        except ZoteroError as error:
            failed = _TargetState(error.result, str(error))
            return _observation(failed)
        compared = _poll_window(
            vault_root,
            evidence,
            settle_seconds,
            poll_interval,
            clock,
            sleeper,
        )
    if compared.result is not Result.MATCHED:
        return _observation(compared)

    try:
        commit_autoexport(vault_root)
    except (OSError, subprocess.SubprocessError) as error:
        failed = _TargetState(
            Result.UNREACHABLE, f"bibliography commit failed: {error}"
        )
        return _observation(failed)

    # `git commit --only -- path` rereads the worktree. Re-observe so a genuine
    # BBT rewrite racing bookkeeping can never be reported as the validated state.
    final = _compare_target(_target_state(vault_root), evidence)
    committed = _committed_state(vault_root, evidence)
    if committed.result is not Result.MATCHED:
        return AutoexportObservation(
            committed.result,
            committed.detail,
            final.result,
            final.detail,
        )
    return _observation(final)


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
