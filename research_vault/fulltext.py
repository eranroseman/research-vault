"""The text layer: one OKF-conformant file per indexed attachment (spec §3.6).

Derived, gitignored, regenerable from Zotero's index; Obsidian indexes it;
the literature note records each file's sha256. The hash is machine-local.
"""

import hashlib
import re
from pathlib import Path
from typing import NamedTuple

from . import Result, frontmatter
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
    if "indexedPages" in response or "totalPages" in response:
        unit, indexed, total = (
            "indexedPages",
            response.get("indexedPages"),
            response.get("totalPages"),
        )
    elif "indexedChars" in response or "totalChars" in response:
        unit, indexed, total = (
            "indexedChars",
            response.get("indexedChars"),
            response.get("totalChars"),
        )
    else:
        return TextVerdict(False, "malformed — indexedPages/indexedChars pair missing")
    if not isinstance(indexed, int) or not isinstance(total, int):
        return TextVerdict(False, f"malformed — {unit} pair missing")
    if indexed > total:
        return TextVerdict(False, "malformed — indexed exceeds total")
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


WITNESS = "managed-sha256"
_WITNESS_LINE = re.compile(rb'^managed-sha256: "[0-9a-f]{64}"\r?\n', re.MULTILINE)


def _render(attachment_key, item_key, response) -> str:
    fields: list[tuple[str, object]] = [
        ("type", "fulltext"),
        ("zotero-attachment-key", attachment_key),
        ("zotero-item-key", item_key),
    ]
    for pair in (("indexedPages", "totalPages"), ("indexedChars", "totalChars")):
        if pair[0] in response or pair[1] in response:
            values = [response.get(name) for name in pair]
            if not all(isinstance(value, int) for value in values):
                raise ValueError(f"malformed — {pair[0]} pair missing")
            fields.extend(zip(pair, values, strict=True))
    body = response.get("content") or ""
    without = frontmatter.serialize(dict(fields)) + body
    # #207: the self-witness — the hash of the render with its own line absent,
    # emitted as the last frontmatter key. Any byte change afterwards (body,
    # value, added key, requoting) reads as stale.
    digest = hashlib.sha256(without.encode("utf-8")).hexdigest()
    return frontmatter.serialize(dict([*fields, (WITNESS, digest)])) + body


def witness_of(raw: bytes) -> str:
    """The witness `raw` should carry: the hash of its bytes without the one witness line."""
    return hashlib.sha256(_WITNESS_LINE.sub(b"", raw, count=1)).hexdigest()


def validate_text(raw: bytes, stem: str) -> tuple[Result, str]:
    """#207's check side: exactly one well-formed witness line, equal to the
    hash of everything else; the attachment key equal to the file stem."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return Result.UNREACHABLE, "outage — text file is not UTF-8"
    try:
        data, _body = frontmatter.parse(text)
    except frontmatter.FrontmatterError:
        return Result.UNMATCHED, "schema-violation — malformed frontmatter"
    witnesses = [
        value for key, value in frontmatter._mapping_items(data) if key == WITNESS
    ]
    if not witnesses:
        return Result.UNMATCHED, "schema-violation — missing managed-sha256"
    if len(witnesses) != 1:
        return Result.UNMATCHED, "schema-violation — duplicate managed-sha256"
    witness = witnesses[0]
    if not isinstance(witness, str) or re.fullmatch(r"[0-9a-f]{64}", witness) is None:
        return Result.UNMATCHED, "schema-violation — invalid managed-sha256"
    if witness != witness_of(raw):
        return Result.UNMATCHED, "schema-violation — stale managed-sha256"
    if data.get("zotero-attachment-key") != stem:
        return Result.UNMATCHED, "schema-violation — key does not match file name"
    return Result.MATCHED, "matched"


def write(vault_root, attachment_key, item_key, response) -> tuple[Path, str]:
    target = path_for(vault_root, attachment_key)
    target.parent.mkdir(parents=True, exist_ok=True)
    text = _render(attachment_key, item_key, response)
    with target.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return target, hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_of(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
