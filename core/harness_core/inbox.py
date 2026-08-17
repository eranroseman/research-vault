"""The shared review inbox: ``+/review-queue.md`` (spec §3)."""

import datetime
import re
from dataclasses import dataclass
from pathlib import Path

from . import AGENT_ACTOR, Result

INBOX_PATH = "+/review-queue.md"
_OMITTED_HASH = object()
REASON_CODES = frozenset(
    {
        "contradiction",
        "low-confidence",
        "schema-violation",
        "mismatch",
        "not-admitted",
        "outage",
        "stale",
        "drift",
        "contested",
        "superseded-source",
        "missing-archive",
        "fuzzy-quote",
        "no-identifier",
        "retracted",
        "warn-notice",
        "matched",
        "manual",
    }
)
_FIELD = re.compile(r"\[(?P<key>[a-z-]+):: (?P<value>(?:\\\]|[^\]])*)\]")
_REASON = re.compile(
    rf"(?:{'|'.join(re.escape(code) for code in sorted(REASON_CODES, key=len, reverse=True))})(?:$|\s+\S.*)"
)
_ENTRY_FIELDS = {"id", "check", "target", "result", "date", "actor", "reason"}
_ACK_FIELDS = {"ack", "actor", "reason"}


class InboxError(ValueError):
    """Raised when an inbox line cannot be parsed as a review record."""


@dataclass
class Entry:
    id: str
    check: str = ""
    target: str = ""
    result: str = ""
    date: str = ""
    actor: str = ""
    reason: str = ""
    ack_of: str | None = None
    target_hash: str | None = None
    notice_date: str | None = None
    detection_date: str | None = None


def validate_reason(reason: str) -> str:
    """Return a reason with a contract-approved code prefix or raise ValueError."""
    if not isinstance(reason, str) or "\n" in reason or not _REASON.fullmatch(reason):
        raise ValueError(
            "reason must be a supported code, optionally followed by free text: "
            f"{reason!r}"
        )
    return reason


def _file(vault) -> Path:
    return Path(vault) / INBOX_PATH


def _serialize(fields: list[tuple[str, str | None]]) -> str:
    return (
        "- "
        + " ".join(
            f"[{key}:: {_escape_field_value(value)}]" for key, value in fields if value
        )
        + "\n"
    )


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


def append_entry(
    vault,
    check,
    target,
    result: Result,
    reason: str,
    actor: str = AGENT_ACTOR,
    date: str | None = None,
    target_hash: str | None = None,
    notice_date: str | None = None,
    detection_date: str | None = None,
) -> Entry:
    """Append a finding record and return its immutable representation."""
    validate_reason(reason)
    date = date or datetime.date.today().isoformat()
    entry = Entry(
        id=f"{check}/{target}/{date}",
        check=check,
        target=target,
        result=result.value,
        date=date,
        actor=actor,
        reason=reason,
        target_hash=target_hash,
        notice_date=notice_date,
        detection_date=detection_date,
    )
    fields = [
        ("id", entry.id),
        ("check", entry.check),
        ("target", entry.target),
        ("result", entry.result),
        ("date", entry.date),
        ("actor", entry.actor),
        ("reason", entry.reason),
        ("target-hash", entry.target_hash),
        ("notice-date", entry.notice_date),
        ("detection-date", entry.detection_date),
    ]
    with _file(vault).open("a") as queue:
        queue.write(_serialize(fields))
    return entry


def append_ack(vault, entry_id, reason: str, actor: str, target_hash=None) -> Entry:
    """Append a human acknowledgment for a finding."""
    if not actor.startswith("human:"):
        raise ValueError(f"acknowledgment requires a human: actor, got {actor!r}")
    validate_reason(reason)
    entry = Entry(
        id=f"ack/{entry_id}",
        ack_of=entry_id,
        actor=actor,
        reason=reason,
        target_hash=target_hash,
    )
    fields = [
        ("ack", entry.ack_of),
        ("actor", entry.actor),
        ("reason", entry.reason),
        ("target-hash", entry.target_hash),
    ]
    with _file(vault).open("a") as queue:
        queue.write(_serialize(fields))
    return entry


def _line_fields(line: str, number: int) -> dict[str, str]:
    if not line.startswith("- "):
        raise InboxError(f"unparseable inbox line {number}: {line!r}")
    fields = list(_FIELD.finditer(line))
    if not fields or " ".join(field.group(0) for field in fields) != line[2:]:
        raise InboxError(f"unparseable inbox line {number}: {line!r}")
    data = {
        field.group("key"): _unescape_field_value(field.group("value"))
        for field in fields
    }
    if len(data) != len(fields):
        raise InboxError(f"duplicate inbox field on line {number}: {line!r}")
    return data


def load(vault) -> list[Entry]:
    """Load all finding and acknowledgment records from the append-only inbox."""
    entries = []
    for number, line in enumerate(_file(vault).read_text().splitlines(), start=1):
        if not line.strip():
            continue
        data = _line_fields(line, number)
        if "ack" in data:
            if "id" in data or not data.keys() >= _ACK_FIELDS:
                raise InboxError(f"unparseable inbox line {number}: {line!r}")
            _validate_loaded_reason(data["reason"], number, line)
            entries.append(
                Entry(
                    id=f"ack/{data['ack']}",
                    ack_of=data["ack"],
                    actor=data["actor"],
                    reason=data["reason"],
                    target_hash=data.get("target-hash"),
                )
            )
        elif "id" in data:
            if not data.keys() >= _ENTRY_FIELDS:
                raise InboxError(f"unparseable inbox line {number}: {line!r}")
            _validate_loaded_reason(data["reason"], number, line)
            entries.append(
                Entry(
                    id=data["id"],
                    check=data["check"],
                    target=data["target"],
                    result=data["result"],
                    date=data["date"],
                    actor=data["actor"],
                    reason=data["reason"],
                    target_hash=data.get("target-hash"),
                    notice_date=data.get("notice-date"),
                    detection_date=data.get("detection-date"),
                )
            )
        else:
            raise InboxError(f"unparseable inbox line {number}: {line!r}")
    return entries


def _validate_loaded_reason(reason: str, number: int, line: str) -> None:
    try:
        validate_reason(reason)
    except ValueError as error:
        raise InboxError(f"invalid reason on inbox line {number}: {line!r}") from error


def _scope_acknowledged(entries: list[Entry], check, target, target_hash) -> bool:
    """Whether a human ack closes the whole check/target/hash standing scope."""
    scope_ids = {
        entry.id
        for entry in entries
        if entry.ack_of is None
        and entry.check == check
        and entry.target == target
        and entry.target_hash == target_hash
    }
    return any(
        ack.ack_of in scope_ids
        and ack.actor.startswith("human:")
        and ack.target_hash == target_hash
        for ack in entries
    )


def is_acknowledged(vault, check, target, current_hash=_OMITTED_HASH) -> bool:
    """Return whether a standing scope acknowledgement matches this hash."""
    entries = load(vault)
    latest = next(
        (
            entry
            for entry in reversed(entries)
            if entry.ack_of is None and entry.check == check and entry.target == target
        ),
        None,
    )
    if latest is None:
        return False
    target_hash = latest.target_hash if current_hash is _OMITTED_HASH else current_hash
    return _scope_acknowledged(entries, check, target, target_hash)


def open_entries(vault) -> list[Entry]:
    """Return findings not closed by a matching human acknowledgment."""
    entries = load(vault)
    return [
        entry
        for entry in entries
        if entry.ack_of is None
        and not _scope_acknowledged(
            entries, entry.check, entry.target, entry.target_hash
        )
    ]


def summary(vault) -> dict:
    """Return the count and age basis used by inbox orientation surfaces."""
    entries = open_entries(vault)
    return {
        "unacknowledged": len(entries),
        "oldest": min((entry.date for entry in entries if entry.date), default=None),
    }
