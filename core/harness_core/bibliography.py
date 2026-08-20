"""The in-repo citekey universe: x/bibliography.json (spec §4)."""

import json
import stat
import subprocess
from pathlib import Path

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


def _canonical(items):
    return json.dumps(sorted(items, key=lambda i: i["id"]), indent=1, sort_keys=True)


def write_and_commit(vault_root, items) -> bool:
    p = _path(vault_root)
    new = _canonical(items)
    if p.is_file() and p.read_text() == new:
        return False
    p.write_text(new)
    subprocess.run(["git", "add", BIB_PATH], cwd=vault_root, check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-q",
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
