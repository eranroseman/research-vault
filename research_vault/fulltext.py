"""The text layer: one OKF-conformant file per indexed attachment (spec §3.6).

Derived, gitignored, regenerable from Zotero's index; Obsidian indexes it;
the literature note records each file's sha256. The hash is machine-local.
"""

import hashlib
from pathlib import Path
from typing import NamedTuple

from . import frontmatter
from .zotero import ITEM_KEY

FULLTEXT_DIR = "fulltext"
# Four times the largest masthead §9 measured on a scanned PDF (126 chars)
# and an order of magnitude below one page of body text.
FULLTEXT_MIN_CHARS = 500


class TextVerdict(NamedTuple):
    usable: bool
    reason: str


def verdict(response) -> TextVerdict:
    """The two tests §3.3 step 3 requires: page/char completeness, then a content floor."""
    if response is None:
        return TextVerdict(False, "no-index")
    if "indexedPages" in response:
        indexed, total, unit = (
            response.get("indexedPages"),
            response.get("totalPages"),
            "indexedPages",
        )
    else:
        indexed, total, unit = (
            response.get("indexedChars"),
            response.get("totalChars"),
            "indexedChars",
        )
    if not isinstance(indexed, int) or not isinstance(total, int):
        return TextVerdict(False, f"malformed — {unit} pair missing")
    if indexed < total:
        return TextVerdict(False, f"partial — {unit} {indexed} of {total}")
    length = len(response.get("content") or "")
    if length < FULLTEXT_MIN_CHARS:
        return TextVerdict(
            False, f"empty — {length} characters below floor {FULLTEXT_MIN_CHARS}"
        )
    return TextVerdict(True, "complete")


def path_for(vault_root, attachment_key) -> Path:
    if not ITEM_KEY.match(attachment_key or ""):
        raise ValueError(f"unsafe attachment key: {attachment_key!r}")
    return Path(vault_root) / FULLTEXT_DIR / f"{attachment_key}.md"


def _render(attachment_key, item_key, response) -> str:
    fields: list[tuple[str, object]] = [
        ("type", "fulltext"),
        ("zotero-attachment-key", attachment_key),
        ("zotero-item-key", item_key),
    ]
    for pair in (("indexedPages", "totalPages"), ("indexedChars", "totalChars")):
        if pair[0] in response:
            fields.extend((name, int(response[name])) for name in pair)
    return frontmatter.serialize(dict(fields)) + (response.get("content") or "")


def write(vault_root, attachment_key, item_key, response) -> tuple[Path, str]:
    target = path_for(vault_root, attachment_key)
    target.parent.mkdir(parents=True, exist_ok=True)
    text = _render(attachment_key, item_key, response)
    with target.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return target, hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_of(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
