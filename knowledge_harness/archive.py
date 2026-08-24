"""Web-source archival: the single writer of literature ``archive-url`` (spec §7).

Rescue is impossible at rot time, so the snapshot has to exist at import — a
source cataloged unarchived stays unarchived for as long as the record lives.
This owns that act. Writing ``archive-url`` was previously prose's job, which
put an LLM's hand inside ``literatures/``; giving the field a machine owner is
what keeps the evidence layer's never-free-written rule intact.

Four-state honesty on an outward call: ``archive-url`` is written only on a
snapshot the Wayback Machine confirms it is serving. A Save Page Now failure or
timeout is UNREACHABLE — reported, retried on the next refresh, never a
fabricated URL. Nothing here ever composes an archive URL itself; it records
only what the availability API returns, and only from the archive's own host.
"""

import datetime
import urllib.parse

from . import AGENT_ACTOR, Result, frontmatter, notes, webapi
from .outcome import Outcome
from .verify import _read_note_text, _write_note_text

SAVE_ENDPOINT = "https://web.archive.org/save/"
AVAILABILITY_ENDPOINT = "https://archive.org/wayback/available"
# The only hosts a recorded snapshot may live on. A snapshot URL is durable
# vault content, so an odd or hostile response must never be able to write an
# arbitrary destination into a literature note.
ARCHIVE_HOSTS = frozenset({"web.archive.org", "archive.org"})
CHECK = "web-archive"


class ArchiveError(RuntimeError):
    """The verb cannot operate at all — no citekey, no note, no frontmatter."""


def _note_frontmatter(vault_root, citekey: str):
    try:
        path = notes.note_path(vault_root, citekey)
    except notes.InvalidCitekeyError as error:
        raise ArchiveError(str(error)) from error
    if not path.is_file():
        raise ArchiveError(f"no literature note for {citekey}")
    try:
        text = _read_note_text(path)
        data, _ = frontmatter.parse(text)
    except (OSError, UnicodeError) as error:
        raise ArchiveError(f"cannot read {citekey}: {error}") from error
    except frontmatter.FrontmatterError as error:
        raise ArchiveError(f"malformed frontmatter in {citekey}: {error}") from error
    if not data:
        # ``frontmatter.parse`` returns an empty mapping for a note with no
        # fences at all. That is a malformed literature note, not a note that
        # merely lacks a url — refuse rather than report it as "not a web
        # source", which would read as a clean answer.
        raise ArchiveError(f"{citekey} has no frontmatter")
    return path, text, data


def _string_field(data, key: str) -> str:
    value = data.get(key)
    return value.strip() if isinstance(value, str) and value.strip() else ""


def is_archive_url(url) -> bool:
    """Whether a URL is a well-formed snapshot address on the archive's host."""
    if not isinstance(url, str) or not url or url.splitlines() != [url]:
        return False
    parts = urllib.parse.urlsplit(url)
    return parts.scheme in {"http", "https"} and parts.netloc in ARCHIVE_HOSTS


def set_archive_url(note_text: str, url: str) -> str:
    """Insert or replace the note's single top-level ``archive-url`` line.

    Byte-surgical for the same reason ``publish._set_status`` is: every other
    line — the managed region, its witness, human-added keys — must survive
    untouched, and the parse-back below refuses to hand back a note this
    write broke.
    """
    lines = note_text.splitlines(keepends=True)
    fence = {"---\n", "---\r\n"}
    if not lines or lines[0] not in fence:
        raise ArchiveError("literature note has no frontmatter")
    close = next(
        (index for index, line in enumerate(lines[1:], start=1) if line in fence),
        None,
    )
    if close is None:
        raise ArchiveError("literature note frontmatter is unterminated")
    existing = [
        index for index in range(1, close) if lines[index].startswith("archive-url:")
    ]
    if len(existing) > 1:
        raise ArchiveError(f"note carries {len(existing)} archive-url fields, need one")
    # _emit_scalar quotes and escapes exactly as the serializer does, and fails
    # loudly on any character that could forge a second frontmatter line.
    field = f"archive-url: {frontmatter._emit_scalar(url)}"
    if existing:
        line = lines[existing[0]]
        ending = (
            "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        )
        lines[existing[0]] = field + ending
    else:
        ending = "\r\n" if lines[close].endswith("\r\n") else "\n"
        lines.insert(close, field + ending)
    updated = "".join(lines)
    try:
        data, _ = frontmatter.parse(updated)
    except frontmatter.FrontmatterError as error:
        raise ArchiveError(
            f"archive-url write broke the frontmatter: {error}"
        ) from error
    if data.get("archive-url") != url:
        raise ArchiveError(f"archive-url write did not round-trip: {url!r}")
    return updated


def _closest_snapshot(payload) -> str | None:
    """Return a confirmed, available snapshot URL from a strictly read response."""
    if not isinstance(payload, dict):
        return None
    snapshots = payload.get("archived_snapshots")
    if not isinstance(snapshots, dict):
        return None
    closest = snapshots.get("closest")
    if not isinstance(closest, dict) or closest.get("available") is not True:
        return None
    if str(closest.get("status", "")) != "200":
        return None
    url = closest.get("url")
    return url if is_archive_url(url) else None


def _outage(target: str, detail: str) -> Outcome:
    return Outcome(CHECK, target, Result.UNREACHABLE, f"outage — {detail}")


def _generated_at() -> str:
    now = datetime.datetime.now(datetime.UTC).replace(microsecond=0)
    return now.isoformat().replace("+00:00", "Z")


def _bump_generated(note_text: str, at: str) -> str:
    """Attest this write in the note's ``generated`` field, inserted or replaced.

    Byte-surgical for the same reason ``set_archive_url`` is: every other
    line — the managed region, its witness, human-added keys — must survive
    untouched, and the parse-back below refuses to hand back a note this
    write broke. Gaining a snapshot is a meaningful content change (task 17b
    step 2b), so this write carries the same writer attestation a re-render
    would, keeping the evidence-layer guard from reading it as a hand-edit.
    """
    lines = note_text.splitlines(keepends=True)
    fence = {"---\n", "---\r\n"}
    if not lines or lines[0] not in fence:
        raise ArchiveError("literature note has no frontmatter")
    close = next(
        (index for index, line in enumerate(lines[1:], start=1) if line in fence),
        None,
    )
    if close is None:
        raise ArchiveError("literature note frontmatter is unterminated")
    existing = [
        index for index in range(1, close) if lines[index].startswith("generated:")
    ]
    if len(existing) > 1:
        raise ArchiveError(f"note carries {len(existing)} generated fields, need one")
    inner = ", ".join(
        f"{key}: {frontmatter._emit_scalar(value)}"
        for key, value in (("by", AGENT_ACTOR), ("at", at))
    )
    field = f"generated: {{{inner}}}"
    if existing:
        line = lines[existing[0]]
        ending = (
            "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        )
        lines[existing[0]] = field + ending
    else:
        ending = "\r\n" if lines[close].endswith("\r\n") else "\n"
        lines.insert(close, field + ending)
    updated = "".join(lines)
    try:
        data, _ = frontmatter.parse(updated)
    except frontmatter.FrontmatterError as error:
        raise ArchiveError(f"generated write broke the frontmatter: {error}") from error
    if data.get("generated") != {"by": AGENT_ACTOR, "at": at}:
        raise ArchiveError(f"generated write did not round-trip: {at!r}")
    return updated


def _record(path, text, url, target) -> Outcome:
    updated = _bump_generated(set_archive_url(text, url), _generated_at())
    _write_note_text(path, updated)
    return Outcome(CHECK, target, Result.MATCHED, "matched", extra={"archive_url": url})


def archive_source(vault_root, citekey: str, snapshot: str | None = None) -> Outcome:
    """Archive one web source and record the snapshot, or report why it could not."""
    path, text, data = _note_frontmatter(vault_root, citekey)
    target = _string_field(data, "citekey") or citekey

    recorded = _string_field(data, "archive-url")
    if recorded:
        return Outcome(
            CHECK,
            target,
            Result.MATCHED,
            "matched",
            extra={"archive_url": recorded, "already_recorded": True},
        )

    url = _string_field(data, "url")
    # Exactly ``lints.lint_web_archive``'s own condition, so this verb answers
    # every note that lint reports and stays silent on every note it does not.
    if not url or _string_field(data, "doi"):
        return Outcome(
            CHECK, target, Result.SKIPPED, "no-identifier — not a web source"
        )

    if snapshot is not None:
        if not is_archive_url(snapshot):
            return Outcome(
                CHECK,
                target,
                Result.UNMATCHED,
                "missing-archive — supplied snapshot is not a web.archive.org URL",
            )
        try:
            status = webapi.get_status(snapshot, vault_root, query_mailto=False)
        except webapi.ApiError as error:
            return _outage(target, f"supplied snapshot unreachable: {error}")
        if status == 404:
            return Outcome(
                CHECK,
                target,
                Result.UNMATCHED,
                "missing-archive — supplied snapshot 404s",
            )
        return _record(path, text, snapshot, target)

    try:
        webapi.get_status(
            SAVE_ENDPOINT + url, vault_root, query_mailto=False, timeout=60.0
        )
    except webapi.ApiError as error:
        return _outage(target, f"Save Page Now unavailable: {error}")

    try:
        status, payload = webapi.get_json(
            AVAILABILITY_ENDPOINT, vault_root, params={"url": url}
        )
    except webapi.ApiError as error:
        return _outage(target, f"snapshot confirmation unavailable: {error}")
    if status != 200:
        return _outage(target, f"snapshot confirmation returned HTTP {status}")

    confirmed = _closest_snapshot(payload)
    if confirmed is None:
        return Outcome(
            CHECK,
            target,
            Result.UNMATCHED,
            "missing-archive — the archive is serving no snapshot for this URL",
        )
    return _record(path, text, confirmed, target)
