"""The CSL JSON file: one entry per captured item (ingest spec §3.2).

Capture exports each rendered item's entry before rendering it and rewrites
only those entries at the end of the run (#196): an entry moves only with its
note, which records the entry's hash as `csl-sha256`. Verify reads the file as
the citation-key universe. No auto-export, no observation, no byte-compare
against a third-party writer.
"""

import hashlib
import json
import os
import stat
from collections.abc import Iterable, Mapping
from pathlib import Path

from . import Result

BIB_PATH = "system/bibliography.json"


class BibliographyError(ValueError):
    """A bibliography that cannot safely participate in verification."""

    def __init__(self, message: str, result: Result):
        super().__init__(message)
        self.result = result


def _path(vault_root) -> Path:
    # abspath, NOT Path.resolve(): resolve() follows symlinks.
    return Path(os.path.abspath(os.fspath(vault_root))) / BIB_PATH  # noqa: PTH100


def load(vault_root) -> dict[str, dict]:
    p = _path(vault_root)
    try:
        try:
            path_stat = p.stat()
        except FileNotFoundError:
            return {}
        if not stat.S_ISREG(path_stat.st_mode):
            raise BibliographyError(
                "bibliography is not a regular file", Result.UNMATCHED
            )
        text = p.read_text(encoding="utf-8")
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
    return {item["id"]: item for item in items}


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


def write(vault_root, items: list[dict]) -> Path:
    """Regenerate the whole file, sorted by citation key, or write nothing."""
    try:
        _validate_items(items)
    except (TypeError, ValueError) as error:
        raise BibliographyError(
            "refusing to write an invalid bibliography", Result.UNMATCHED
        ) from error
    ordered = sorted(items, key=lambda item: item["id"])
    target = _path(vault_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(ordered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return target


def entry_sha256(entry: dict) -> str:
    """The hash a literature note records of its own CSL entry (#196): canonical
    JSON, sorted keys, no whitespace, so the same entry hashes the same whatever
    Better BibTeX's key order was."""
    canonical = json.dumps(
        entry, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def update(vault_root, rendered: Mapping[str, dict], keep: Iterable[str]) -> Path:
    """Replace the rendered items' entries, keep every other captured key's
    entry as it stands, drop the rest (a merged-away or re-keyed key), write
    whole. An unreadable or invalid existing file raises `BibliographyError`
    rather than being overwritten from a partial read."""
    existing = load(vault_root)
    wanted = set(keep)
    merged = {key: entry for key, entry in existing.items() if key in wanted}
    merged.update(rendered)
    return write(vault_root, list(merged.values()))
