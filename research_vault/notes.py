"""Literature-note identity, body witness, and canonical form (spec §3-§5)."""

import datetime
import hashlib
import re
from pathlib import Path

from . import Result, frontmatter


class InvalidCitekeyError(ValueError):
    """A citekey that cannot safely name one file in ``literatures``."""


_UNSAFE_IDENTIFIER = re.compile(r"[\s\x00-\x1f\x7f]")


def display_text(value) -> str:
    """Collapse a display-class value so it can never span a rendered line.

    Total by design: a capture is never held on ugly-but-real metadata. Without
    a line break, injected text cannot forge a claim line, a blockquote line, a
    heading, or a frontmatter boundary.
    """
    return "" if value is None else " ".join(str(value).split())


def note_body(text: str) -> str:
    """The body below the frontmatter: capture's, compared byte for byte."""
    _data, body = frontmatter.parse(text)
    return body


def body_sha256(text: str) -> str:
    return hashlib.sha256(note_body(text).encode("utf-8")).hexdigest()


def validate_managed_witness(note_bytes: bytes) -> tuple[Result, str]:
    """Return the four-state witness result without inventing I/O state."""
    try:
        text = note_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return Result.UNREACHABLE, "outage — literature note is not UTF-8"
    try:
        data, body = frontmatter.parse(text)
    except frontmatter.FrontmatterError:
        return Result.UNMATCHED, "schema-violation — malformed frontmatter"
    witnesses = [
        value
        for key, value in frontmatter._mapping_items(data)
        if key == "managed-sha256"
    ]
    if not witnesses:
        return Result.UNMATCHED, "schema-violation — missing managed-sha256"
    if len(witnesses) != 1:
        return Result.UNMATCHED, "schema-violation — duplicate managed-sha256"
    witness = witnesses[0]
    if not isinstance(witness, str) or re.fullmatch(r"[0-9a-f]{64}", witness) is None:
        return Result.UNMATCHED, "schema-violation — invalid managed-sha256"
    if witness != hashlib.sha256(body.encode("utf-8")).hexdigest():
        return Result.UNMATCHED, "schema-violation — stale managed-sha256"
    return Result.MATCHED, "matched"


def note_path(vault_root, citekey) -> Path:
    if (
        not isinstance(citekey, str)
        or not citekey
        or citekey in {".", ".."}
        or "/" in citekey
        or "\\" in citekey
        or _UNSAFE_IDENTIFIER.search(citekey) is not None
        or Path(citekey).is_absolute()
    ):
        raise InvalidCitekeyError(f"unsafe citekey: {citekey!r}")
    return Path(vault_root) / "literatures" / f"{citekey}.md"


def _valid_generated(value) -> bool:
    if not isinstance(value, dict):
        return False
    items = list(frontmatter._mapping_items(value))
    if len(items) != 2 or {key for key, _ in items} != {"by", "at"}:
        return False
    actor, at = value.get("by"), value.get("at")
    if not isinstance(actor, str) or not actor or not isinstance(at, str):
        return False
    try:
        parsed = datetime.datetime.fromisoformat(at)
    except ValueError:
        return False
    return at.endswith("Z") and parsed.tzinfo is not None


def generated_at_now(now: datetime.datetime | None = None) -> str:
    """Second-resolution, ``Z``-suffixed ISO 8601 — the one spelling every
    ``generated.at`` stamp of "now" uses, so they cannot drift into formats
    `_valid_generated` disagrees on.
    """
    moment = now if now is not None else datetime.datetime.now(datetime.UTC)
    return moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_changed(existing_text, candidate_text) -> bool:
    return existing_text is None or canonical_content(
        existing_text
    ) != canonical_content(candidate_text)


def canonical_content(note_text: str) -> str:
    """Exclude only a valid verifier-owned ``verified`` event list."""
    close, lines = _frontmatter_close(note_text)
    if close is None:
        return note_text
    if close < 0:
        # Do not infer body structure from an unterminated verifier boundary.
        return note_text
    try:
        data, _ = frontmatter.parse(note_text)
    except frontmatter.FrontmatterError:
        return note_text
    from .events import _valid_event

    verified = data.get("verified")
    valid_verified = isinstance(verified, list) and all(
        _valid_event(event) for event in verified
    )
    frontmatter_lines = lines[: close + 1]
    body = "".join(lines[close + 1 :])
    if not valid_verified:
        return note_text
    verified_index = _verified_list_index(frontmatter_lines)
    if verified_index is None:
        # A duplicate or non-list-looking lexical definition is not a
        # verifier-owned surface, even if the permissive flat parser kept a
        # list under the final key.
        return note_text
    if _verified_only_envelope(frontmatter_lines, verified_index):
        return body
    result = frontmatter_lines[:verified_index]
    index = verified_index + 1
    while index < close and frontmatter_lines[index].startswith("  - "):
        index += 1
    result.extend(frontmatter_lines[index:])
    return "".join(result) + body


def _frontmatter_close(text: str) -> tuple[int | None, list[str]]:
    """Return the closing delimiter line, or a malformed-frontmatter sentinel."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0] not in {"---\n", "---\r\n"}:
        return None, lines
    for index, line in enumerate(lines[1:], start=1):
        if line in {"---\n", "---\r\n"}:
            return index, lines
    return -1, lines


def _verified_list_index(lines: list[str]) -> int | None:
    """Find one syntactically top-level ``verified:`` event-list header."""
    verified_lines = [
        index for index, line in enumerate(lines[:-1]) if line.startswith("verified:")
    ]
    if len(verified_lines) != 1:
        return None
    index = verified_lines[0]
    if lines[index].rstrip("\r\n").rstrip(" \t") != "verified:":
        return None
    return index


def _verified_only_envelope(lines: list[str], verified_index: int) -> bool:
    """Whether frontmatter is solely the valid verifier-owned event list."""
    return verified_index == 1 and all(
        line.startswith("  - ") for line in lines[verified_index + 1 : -1]
    )
