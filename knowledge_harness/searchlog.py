"""PRISMA-S search provenance: ``projects/<name>/search-log.md`` (spec §7 `find-sources` row).

`find-sources` is literature search upstream of Zotero admission — the
skill presents candidates, a human admits what belongs into Zotero, and
`import-source` catalogs what was admitted. This module is the durable
record of the search itself, the trail a methods reviewer reconstructs
(PRISMA-S): every run appends the query as run, the source searched, the
date, and the hit count; every candidate a human declines to admit gets its
own line with a reason code, so "we looked and found nothing worth adding"
stays distinguishable from "we never looked."

Two record kinds share one append-only file, mirroring how
``inbox/review-queue.md`` carries both findings and acknowledgments:

``SearchEntry``
    One completed search run. ``query``/``source``/``date``/``hits`` are the
    brief's four required fields; ``actor`` rides along per §5's actor
    convention (every generating identity is recorded), the same way every
    other durable writer in this package stamps one.

``NotAdmittedEntry``
    One candidate a human declined to admit into Zotero, with a
    contract-approved reason code (``inbox.REASON_CODES`` — the one registry
    shared by import-source holds, deprecations, acknowledgments, and this).
    ``source`` is optional: a candidate can arrive by hand, outside any one
    search run.

This is a **second writer of the same durable-append pattern** as
``inbox.py``, not a second pattern — and the primitives that pattern is
made of are shared code, not shared prose. The field regex, the
single-line/no-control-character text rule, the bracket-escaping pair,
the line serializer, and the directory-fsync primitive live in
``appendlog.py`` and are imported here (Task 6 review, 2026-08-22: an
earlier draft copied these six instead, and the copy had already drifted
on a docstring word and dropped a load-bearing safety comment — copying
"the pattern" turned out to mean copying the bug surface too). What
stays genuinely separate, because the two files' record shapes and
sequencing differ, is everything above the primitive layer: the
frontmatter-type guard, the two record dataclasses, and the
create-or-validate/append sequencing. Also reused directly, never
re-derived: ``inbox.validate_reason``/``inbox.REASON_CODES`` (one
governed reason-code vocabulary) and ``publish.project_dir`` (one
project-path safety check — symlink and traversal refusal).

Never write this file by hand, and never write it from prose: every line is
one of the two append functions below, called only through the CLI's
``search-log`` verb.
"""

import datetime
import os
import re
from dataclasses import dataclass
from pathlib import Path

from . import AGENT_ACTOR, frontmatter, inbox
from .appendlog import (
    _FIELD,
    _serialize,
    _sync_directory,
    _unescape_field_value,
    _validate_text,
)
from .publish import PublishError, project_dir

SEARCH_LOG_TYPE = "search-log"
_SEARCH_REQUIRED = {"query", "source", "date", "hits", "actor"}
_NOT_ADMITTED_REQUIRED = {"candidate", "date", "reason", "actor"}
_NOT_ADMITTED_OPTIONAL = {"source"}


class SearchLogError(ValueError):
    """Raised when a search-log line cannot be parsed, or an append is refused."""


@dataclass(frozen=True)
class SearchEntry:
    query: str
    source: str
    date: str
    hits: int
    actor: str = AGENT_ACTOR


@dataclass(frozen=True)
class NotAdmittedEntry:
    candidate: str
    reason: str
    date: str
    actor: str = AGENT_ACTOR
    source: str | None = None


def _validate_optional_text(name: str, value) -> str | None:
    return None if value is None else _validate_text(name, value)


def _validate_date(name: str, value) -> str:
    value = _validate_text(name, value)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise SearchLogError(f"{name} must be a YYYY-MM-DD calendar date")
    try:
        parsed = datetime.date.fromisoformat(value)
    except ValueError as error:
        raise SearchLogError(f"{name} must be a YYYY-MM-DD calendar date") from error
    if parsed.isoformat() != value:
        raise SearchLogError(f"{name} must be a YYYY-MM-DD calendar date")
    return value


def _validate_hits(value) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SearchLogError("hits must be a non-negative integer")
    return value


def _resolved_date(date) -> str:
    return _validate_date(
        "date", datetime.date.today().isoformat() if date is None else date
    )


def search_log_path(vault, project) -> Path:
    """Resolve ``projects/<project>/search-log.md`` under an existing project."""
    try:
        directory = project_dir(vault, project)
    except PublishError as error:
        raise SearchLogError(str(error)) from error
    return directory / "search-log.md"


def _body(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text()
    if not text:
        return ""
    try:
        data, body = frontmatter.parse(text)
    except frontmatter.FrontmatterError as error:
        raise SearchLogError(f"malformed search-log frontmatter: {error}") from error
    if list(frontmatter._mapping_items(data)) != [("type", SEARCH_LOG_TYPE)]:
        raise SearchLogError(
            f"search-log frontmatter must contain exactly type: {SEARCH_LOG_TYPE!r}"
        )
    return body


def _prepare_append(vault, project) -> tuple[Path, bool]:
    """Create-or-validate the file, returning whether a new one was created.

    ``created`` must be read before anything below writes — Task 6 review
    (2026-08-22): an earlier draft computed it from ``path.exists()`` *after*
    this function's own write had already created the file, so it was always
    ``True`` and the directory-entry fsync in ``_append_line`` could never
    run. ``inbox._prepare_append`` gets this right for the same reason; this
    mirrors it exactly.
    """
    path = search_log_path(vault, project)
    created = not path.exists()
    if created or not path.read_bytes():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(frontmatter.serialize({"type": SEARCH_LOG_TYPE}))
    else:
        _body(path)  # validates the existing frontmatter before appending
    return path, created


def _append_line(vault, project, fields, *, durable: bool) -> Path:
    path, created = _prepare_append(vault, project)
    with path.open("a", encoding="utf-8", newline="") as handle:
        handle.write(_serialize(fields))
        if durable:
            handle.flush()
            os.fsync(handle.fileno())
    if durable and created:
        _sync_directory(path.parent)
    return path


def append_search(
    vault,
    project,
    query: str,
    source: str,
    hits: int,
    date: str | None = None,
    actor: str = AGENT_ACTOR,
    durable: bool = False,
) -> SearchEntry:
    """Append one PRISMA-S search-run entry: query as run, source, date, hits."""
    entry = SearchEntry(
        query=_validate_text("query", query),
        source=_validate_text("source", source),
        date=_resolved_date(date),
        hits=_validate_hits(hits),
        actor=_validate_text("actor", actor),
    )
    _append_line(
        vault,
        project,
        [
            ("query", entry.query),
            ("source", entry.source),
            ("date", entry.date),
            ("hits", str(entry.hits)),
            ("actor", entry.actor),
        ],
        durable=durable,
    )
    return entry


def append_not_admitted(
    vault,
    project,
    candidate: str,
    reason: str,
    source: str | None = None,
    date: str | None = None,
    actor: str = AGENT_ACTOR,
    durable: bool = False,
) -> NotAdmittedEntry:
    """Append one not-admitted-candidate entry with a governed reason code."""
    inbox.validate_reason(reason)
    entry = NotAdmittedEntry(
        candidate=_validate_text("candidate", candidate),
        reason=reason,
        date=_resolved_date(date),
        actor=_validate_text("actor", actor),
        source=_validate_optional_text("source", source),
    )
    _append_line(
        vault,
        project,
        [
            ("candidate", entry.candidate),
            ("source", entry.source),
            ("date", entry.date),
            ("reason", entry.reason),
            ("actor", entry.actor),
        ],
        durable=durable,
    )
    return entry


def _line_fields(line: str, number: int) -> dict[str, str]:
    if not line.startswith("- "):
        raise SearchLogError(f"unparseable search-log line {number}: {line!r}")
    fields = list(_FIELD.finditer(line))
    if not fields or " ".join(field.group(0) for field in fields) != line[2:]:
        raise SearchLogError(f"unparseable search-log line {number}: {line!r}")
    data = {
        field.group("key"): _unescape_field_value(field.group("value"))
        for field in fields
    }
    if len(data) != len(fields):
        raise SearchLogError(f"duplicate search-log field on line {number}: {line!r}")
    return data


def load(vault, project) -> list[SearchEntry | NotAdmittedEntry]:
    """Load every search-run and not-admitted record, in file order."""
    path = search_log_path(vault, project)
    if not path.exists():
        return []
    entries: list[SearchEntry | NotAdmittedEntry] = []
    for number, line in enumerate(_body(path).splitlines(), start=1):
        if not line.strip():
            continue
        data = _line_fields(line, number)
        if "query" in data:
            if data.keys() != _SEARCH_REQUIRED:
                raise SearchLogError(f"unparseable search-log line {number}: {line!r}")
            try:
                hits = int(data["hits"])
            except ValueError as error:
                raise SearchLogError(
                    f"invalid search-log line {number}: hits must be an integer"
                ) from error
            entries.append(
                SearchEntry(
                    query=_validate_text("query", data["query"]),
                    source=_validate_text("source", data["source"]),
                    date=_validate_date("date", data["date"]),
                    hits=_validate_hits(hits),
                    actor=_validate_text("actor", data["actor"]),
                )
            )
        elif "candidate" in data:
            if (
                not data.keys() >= _NOT_ADMITTED_REQUIRED
                or not data.keys() <= _NOT_ADMITTED_REQUIRED | _NOT_ADMITTED_OPTIONAL
            ):
                raise SearchLogError(f"unparseable search-log line {number}: {line!r}")
            inbox.validate_reason(data["reason"])
            entries.append(
                NotAdmittedEntry(
                    candidate=_validate_text("candidate", data["candidate"]),
                    reason=data["reason"],
                    date=_validate_date("date", data["date"]),
                    actor=_validate_text("actor", data["actor"]),
                    source=_validate_optional_text("source", data.get("source")),
                )
            )
        else:
            raise SearchLogError(f"unparseable search-log line {number}: {line!r}")
    return entries
