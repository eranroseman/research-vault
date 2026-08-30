"""Shared primitives for append-only ``[key:: value]`` durable files.

``inbox.py`` and ``searchlog.py`` both write one, so the field grammar, the
text rules, the escaping pair, the serializer, and the directory fsync live
here — one definition each, and neither writer can drift from the other.
"""

import os
import re
from pathlib import Path

#: One ``[key:: value]`` field. Shared verbatim by both durable-append
#: writers' line parsers.
_FIELD = re.compile(r"\[(?P<key>[a-z-]+):: (?P<value>(?:\\\]|[^\]])*)\]")


def _validate_text(name: str, value) -> str:
    # Reject every break a reader's ``str.splitlines()`` honours — \v, \f,
    # \x1c-\x1e, \x85, U+2028, U+2029 — not only "\n": in an append-only file
    # one row written across two physical lines is unparseable forever.
    if (
        not isinstance(value, str)
        or not value.strip()
        or "\0" in value
        or value.splitlines() != [value]
    ):
        raise ValueError(f"{name} must be a nonempty single-line string")
    return value


def _validate_optional_text(name: str, value) -> str | None:
    return None if value is None else _validate_text(name, value)


def _escape_field_value(value: str) -> str:
    """Escape a closing bracket without changing ordinary legacy field values."""
    if "]" not in value:
        return value
    return value.replace("\\", "\\\\").replace("]", r"\]")


def _unescape_field_value(value: str) -> str:
    """Reverse the bracket escape while preserving unescaped legacy backslashes."""
    if r"\]" not in value:
        return value
    return value.replace(r"\]", "]").replace(r"\\", "\\")


def _serialize(fields: list[tuple[str, str | None]]) -> str:
    return (
        "- "
        + " ".join(
            f"[{key}:: {_escape_field_value(value)}]" for key, value in fields if value
        )
        + "\n"
    )


def _sync_directory(path: Path) -> None:
    """fsync a directory's entry list; callers invoke it only when a write created one."""
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
