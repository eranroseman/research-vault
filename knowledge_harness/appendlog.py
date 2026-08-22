"""Shared primitives for append-only ``[key:: value]`` durable files.

Both ``inbox.py`` (``inbox/review-queue.md``) and ``searchlog.py``
(``projects/<name>/search-log.md``) write durable, append-only Markdown
files sharing one inline field grammar. The two writers shipped with six
of these primitives copied rather than shared (Task 6, 2026-08-22 review)
and the copy had already drifted on one docstring word and dropped an
8-line safety comment — this module is the correction: one field regex,
one text-validation rule, one escaping pair, one line serializer, and one
directory-fsync primitive, so the two writers cannot silently drift again
on what "durable" or "well-formed" means. Everything else — record
shapes, frontmatter-type guards, append sequencing, the reason-code
registry — stays owned by each file; only these six are shared.

Both call sites import these under their original (leading-underscore)
names, the same cross-module convention ``verify.py``'s
``_read_note_text``/``_write_note_text`` already use elsewhere in this
package: the underscore signals package-internal, not module-private.
"""

import os
import re
from pathlib import Path

#: One ``[key:: value]`` field. Shared verbatim by both durable-append
#: writers' line parsers.
_FIELD = re.compile(r"\[(?P<key>[a-z-]+):: (?P<value>(?:\\\]|[^\]])*)\]")


def _validate_text(name: str, value) -> str:
    # The reject class must equal ``load``'s break set, not a narrower trio.
    # ``load`` splits the body with ``str.splitlines()``, so \v, \f, \x1c-\x1e,
    # \x85, U+2028 and U+2029 each end a line for the reader while passing an
    # ``"\n" in value`` writer check — a row written across two physical lines
    # that no later read can parse. Every file this module serves is
    # append-only, so that is permanent: one such write bricks every reader
    # of that file, for good. ``splitlines() != [value]`` also catches a
    # trailing separator, which ``in``-checks miss entirely.
    if (
        not isinstance(value, str)
        or not value.strip()
        or "\0" in value
        or value.splitlines() != [value]
    ):
        raise ValueError(f"{name} must be a nonempty single-line string")
    return value


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
    """fsync a directory's own entry list, after a durable write created one.

    Callers must invoke this only when a new directory entry was actually
    created by the write it follows (see ``inbox.append_entry`` and
    ``searchlog._append_line`` for the ``created`` bookkeeping this
    depends on) — fsyncing the directory when no entry changed is a no-op
    that hides a bug in the caller's own sequencing rather than reporting one.
    """
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
