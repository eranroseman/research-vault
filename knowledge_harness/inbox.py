"""The shared review inbox: ``inbox/review-queue.md`` (spec §3)."""

import datetime
import hashlib
import os
import re
from dataclasses import dataclass, replace
from pathlib import Path

from . import AGENT_ACTOR, frontmatter
from .appendlog import (
    _FIELD,
    _serialize,
    _sync_directory,
    _unescape_field_value,
    _validate_optional_text,
    _validate_text,
)
from .outcome import Result
from .pathcodec import PathCodecError, decode_repo_path

INBOX_PATH = "inbox/review-queue.md"
INBOX_TYPE = "review-queue"
_OMITTED_HASH = object()
REASON_CODES = frozenset(
    {
        "contradiction",
        "low-confidence",
        "schema-violation",
        "mismatch",
        "not-admitted",
        "not-imported",
        "outage",
        "stale",
        "drift",
        "disputed-claim",
        "superseded-note",
        "missing-archive",
        "fuzzy-quote",
        "no-identifier",
        "retracted",
        "warn-notice",
        "matched",
        "manual",
        "budget-cap",
    }
)
# The governed check-id registry (terminology §4.4). ``append_entry`` itself
# stays silent on check ids — the deterministic pipeline (verify.py, lints.py)
# legitimately files ids this registry does not carry (``staleness``,
# ``append-only``, ``claim-immutability``, ``published-drift``,
# ``publish-gate``), so validating here would break it. The `finding` CLI
# verb is the boundary where this registry is actually enforced: it is the
# only writer that takes a check id from outside the process, so it is the
# only place a typo or an unregistered id can enter — including
# ``import-note``'s own hold wiring, which writes through that same verb.
CHECK_IDS = frozenset(
    {
        "citekey",
        "doi",
        "metadata",
        "quote",
        "update-notice",
        "evidence-layer",
        "identifier-discovery",
        "web-archive",
        "screening-state",
        "disputed-claim",
        "publish",
        "factcheck",
        # Task 5. ``autoexport`` is cross-registered from the doctor probe-id
        # group: an import held on the bibliography auto-export names the same
        # observation doctor reports. ``render`` covers the render-rejection
        # class (§4.4 coinage); ``integrate`` covers `import-source`'s surgical
        # integrate-at-import holds (spec §7's own word).
        "autoexport",
        "render",
        "integrate",
    }
)
_REASON = re.compile(
    rf"(?:{'|'.join(re.escape(code) for code in sorted(REASON_CODES, key=len, reverse=True))})(?:$|\s+\S.*)"
)
# Checks whose findings record a repeatable human act rather than a machine
# observation. Their ids carry a reason discriminator so two genuinely distinct
# acts on one target on one day stay separately acknowledgeable, while a retry
# of the same act still collapses to one row.
REPEATABLE_ACT_CHECKS = frozenset({"publish-gate"})
_FINDING_FIELDS = {"id", "check", "target", "result", "date", "actor", "reason"}
_ACK_FIELDS = {"ack", "actor", "reason"}
_FINDING_OPTIONAL_FIELDS = {
    "target-kind",
    "target-hash",
    "notice-class",
    "notice-type",
    "notice-date",
    "detection-date",
}
_ACK_OPTIONAL_FIELDS = {
    "target-kind",
    "target-hash",
    "notice-class",
    "notice-type",
    "notice-date",
}
_NOTICE_TYPES = {
    "blocking": {"retraction", "partial_retraction", "removal", "withdrawal"},
    "warn": {"expression_of_concern", "correction", "corrigendum", "erratum"},
}


class InboxError(ValueError):
    """Raised when an inbox line cannot be parsed as a review record."""


@dataclass(frozen=True)
class Finding:
    id: str
    check: str = ""
    target: str = ""
    target_kind: str = "identifier"
    result: str = ""
    date: str = ""
    actor: str = ""
    reason: str = ""
    ack_of: str | None = None
    target_hash: str | None = None
    notice_class: str | None = None
    notice_type: str | None = None
    notice_date: str | None = None
    detection_date: str | None = None


def validate_reason(reason: str) -> str:
    """Return a reason with a contract-approved code prefix or raise ValueError.

    ``reason`` is the one durable field ``_validate_text`` never sees, and its
    free-text tail is the only part of a review record an LLM authors directly
    (the shipped skills compose `finding` reasons in prose). ``_REASON`` ends in
    ``.*``, and outside DOTALL ``.`` still matches every splitlines separator
    except ``\\n`` — so the same line-break class ``_validate_text`` rejects rode
    a code-prefixed reason straight onto a durable line and bricked the
    append-only queue. The check below is ``_validate_text``'s, deliberately
    spelled the same way: whatever the writer accepts, ``load`` must read back.
    """
    if (
        not isinstance(reason, str)
        or "\0" in reason
        or reason.splitlines() != [reason]
        or not _REASON.fullmatch(reason)
    ):
        raise ValueError(
            "reason must be a supported code, optionally followed by free text: "
            f"{reason!r}"
        )
    return reason


def _validate_target_kind(target: str, target_kind) -> str:
    if target_kind not in {"identifier", "repo-path"}:
        raise ValueError("target_kind must be identifier or repo-path")
    if target_kind == "repo-path":
        decode_repo_path(target)
    return target_kind


def _validate_date(name: str, value) -> str:
    value = _validate_text(name, value)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"{name} must be a YYYY-MM-DD calendar date")
    try:
        parsed = datetime.date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{name} must be a YYYY-MM-DD calendar date") from error
    if parsed.isoformat() != value:
        raise ValueError(f"{name} must be a YYYY-MM-DD calendar date")
    return value


def _validate_optional_date(name: str, value) -> str | None:
    return None if value is None else _validate_date(name, value)


_PARTIAL_DATE = re.compile(r"(?P<year>\d{4})(?:-(?P<month>\d{2})(?:-(?P<day>\d{2}))?)?")


def _validate_partial_date(name: str, value) -> str:
    """Validate Crossref's own precision (``YYYY``, ``YYYY-MM``, or
    ``YYYY-MM-DD``) rather than pad it to a full date. A missing month/day
    skips range validation for that part; a present-but-invalid one
    (``2023-13``, ``2023-06-31``) still fails it."""
    value = _validate_text(name, value)
    match = _PARTIAL_DATE.fullmatch(value)
    if not match:
        raise ValueError(f"{name} must be a YYYY, YYYY-MM, or YYYY-MM-DD date")
    year = int(match.group("year"))
    month, day = match.group("month"), match.group("day")
    try:
        datetime.date(
            year,
            int(month) if month is not None else 1,
            int(day) if day is not None else 1,
        )
    except ValueError as error:
        raise ValueError(
            f"{name} must be a YYYY, YYYY-MM, or YYYY-MM-DD date"
        ) from error
    return value


def _validate_optional_partial_date(name: str, value) -> str | None:
    return None if value is None else _validate_partial_date(name, value)


def _validate_notice_fingerprint(
    check,
    notice_class,
    notice_type,
    notice_date,
    detection_date=None,
):
    notice_class = _validate_optional_text("notice_class", notice_class)
    notice_type = _validate_optional_text("notice_type", notice_type)
    notice_date = _validate_optional_partial_date("notice_date", notice_date)
    detection_date = _validate_optional_date("detection_date", detection_date)
    if notice_class is None and notice_type is None:
        if notice_date is not None or detection_date is not None:
            raise ValueError("notice dates require a complete notice fingerprint")
        return notice_class, notice_type, notice_date, detection_date
    if notice_class is None or notice_type is None:
        raise ValueError("notice_class and notice_type must be provided together")
    if check != "update-notice":
        raise ValueError("notice fingerprints are valid only for update-notice")
    if (
        notice_class not in _NOTICE_TYPES
        or notice_type not in _NOTICE_TYPES[notice_class]
    ):
        raise ValueError("notice_class and notice_type are incoherent")
    return notice_class, notice_type, notice_date, detection_date


def _validate_notice_record(result, notice_class) -> None:
    if notice_class is None:
        return
    result_value = result.value if isinstance(result, Result) else result
    if result_value != Result.UNMATCHED.value:
        raise ValueError("notice findings must be UNMATCHED")


def _file(vault) -> Path:
    return Path(vault) / INBOX_PATH


def _body(queue: Path) -> str:
    if not queue.exists():
        return ""
    text = queue.read_text()
    if not text:
        return ""
    try:
        data, body = frontmatter.parse(text)
    except frontmatter.FrontmatterError as error:
        raise InboxError(f"malformed inbox frontmatter: {error}") from error
    if list(frontmatter._mapping_items(data)) != [("type", INBOX_TYPE)]:
        raise InboxError(f"inbox frontmatter must contain exactly type: {INBOX_TYPE!r}")
    return body


def _prepare_append(vault) -> tuple[Path, bool]:
    queue = _file(vault)
    created = not queue.exists()
    if created or not queue.read_bytes():
        queue.parent.mkdir(parents=True, exist_ok=True)
        queue.write_text(frontmatter.serialize({"type": INBOX_TYPE}))
    else:
        _body(queue)
    return queue, created


def finding_id(
    check,
    target,
    date,
    target_hash,
    notice_class,
    notice_type,
    notice_date,
    target_kind="identifier",
    reason=None,
) -> str:
    identity = f"kind-{len(target_kind)}:{target_kind};target-{len(target)}:{target}"
    finding_id = f"{check}/{identity}/{date}"
    if notice_class is not None:
        finding_id += f"/{notice_class}/{notice_type}/{notice_date or 'unknown'}"
    if target_hash is not None:
        discriminator = hashlib.sha256(target_hash.encode()).hexdigest()[:16]
        finding_id += f"/scope-{discriminator}"
    if check in REPEATABLE_ACT_CHECKS and reason is not None:
        # Reconstructible on load: reason is already a persisted, validated
        # field, so this needs no addition to the inline-field grammar.
        discriminator = hashlib.sha256(reason.encode()).hexdigest()[:16]
        finding_id += f"/act-{discriminator}"
    return finding_id


def append_entry(
    vault,
    check,
    target,
    result: Result,
    reason: str,
    actor: str = AGENT_ACTOR,
    date: str | None = None,
    target_hash: str | None = None,
    notice_class: str | None = None,
    notice_type: str | None = None,
    notice_date: str | None = None,
    detection_date: str | None = None,
    target_kind: str = "identifier",
    durable: bool = False,
) -> Finding:
    """Append a finding record and return its immutable representation."""
    check = _validate_text("check", check)
    target = _validate_text("target", target)
    try:
        target_kind = _validate_target_kind(target, target_kind)
    except PathCodecError as error:
        raise ValueError("target is not a canonical repo path") from error
    if not isinstance(result, Result):
        raise TypeError("result must be a Result")
    validate_reason(reason)
    actor = _validate_text("actor", actor)
    target_hash = _validate_optional_text("target_hash", target_hash)
    date = _validate_date(
        "date",
        datetime.datetime.now(datetime.UTC).date().isoformat()
        if date is None
        else date,
    )
    notice_class, notice_type, notice_date, detection_date = (
        _validate_notice_fingerprint(
            check,
            notice_class,
            notice_type,
            notice_date,
            detection_date,
        )
    )
    _validate_notice_record(result, notice_class)
    entry = Finding(
        id=finding_id(
            check,
            target,
            date,
            target_hash,
            notice_class,
            notice_type,
            notice_date,
            target_kind,
            reason,
        ),
        check=check,
        target=target,
        target_kind=target_kind,
        result=result.value,
        date=date,
        actor=actor,
        reason=reason,
        target_hash=target_hash,
        notice_class=notice_class,
        notice_type=notice_type,
        notice_date=notice_date,
        detection_date=detection_date,
    )
    fields = [
        ("id", entry.id),
        ("check", entry.check),
        ("target", entry.target),
        ("target-kind", entry.target_kind),
        ("result", entry.result),
        ("date", entry.date),
        ("actor", entry.actor),
        ("reason", entry.reason),
        ("target-hash", entry.target_hash),
        ("notice-class", entry.notice_class),
        ("notice-type", entry.notice_type),
        ("notice-date", entry.notice_date),
        ("detection-date", entry.detection_date),
    ]
    queue_path, created = _prepare_append(vault)
    with queue_path.open("a", encoding="utf-8", newline="") as queue:
        queue.write(_serialize(fields))
        if durable:
            queue.flush()
            os.fsync(queue.fileno())
    if durable and created:
        _sync_directory(queue_path.parent)
    return entry


def append_ack(
    vault,
    finding_id,
    reason: str,
    actor: str,
    target_hash=None,
    notice_class=None,
    notice_type=None,
    notice_date=None,
) -> Finding:
    """Append a human acknowledgment for a finding."""
    finding_id = _validate_text("finding_id", finding_id)
    actor = _validate_text("actor", actor)
    if not actor.startswith("human:") or not actor.removeprefix("human:").strip():
        raise ValueError(f"acknowledgment requires a human: actor, got {actor!r}")
    validate_reason(reason)
    target_hash = _validate_optional_text("target_hash", target_hash)
    notice_class, notice_type, notice_date, _ = _validate_notice_fingerprint(
        "update-notice" if notice_class is not None or notice_type is not None else "",
        notice_class,
        notice_type,
        notice_date,
    )
    matches = [
        entry
        for entry in load(vault)
        if entry.ack_of is None and entry.id == finding_id
    ]
    if len(matches) != 1:
        raise ValueError("acknowledgment must reference exactly one finding")
    finding = matches[0]
    if target_hash is None:
        target_hash = finding.target_hash
    elif target_hash != finding.target_hash:
        raise ValueError("acknowledgment target hash does not match finding")
    fingerprint = (finding.notice_class, finding.notice_type, finding.notice_date)
    supplied = (notice_class, notice_type, notice_date)
    if notice_class is None and notice_type is None and notice_date is None:
        notice_class, notice_type, notice_date = fingerprint
    elif supplied != fingerprint:
        raise ValueError("acknowledgment notice fingerprint does not match finding")
    entry = Finding(
        id=f"ack/{finding_id}",
        ack_of=finding_id,
        target_kind=finding.target_kind,
        actor=actor,
        reason=reason,
        target_hash=target_hash,
        notice_class=notice_class,
        notice_type=notice_type,
        notice_date=notice_date,
    )
    fields = [
        ("ack", entry.ack_of),
        ("actor", entry.actor),
        ("reason", entry.reason),
        ("target-kind", entry.target_kind),
        ("target-hash", entry.target_hash),
        ("notice-class", entry.notice_class),
        ("notice-type", entry.notice_type),
        ("notice-date", entry.notice_date),
    ]
    queue_path, _created = _prepare_append(vault)
    with queue_path.open("a", encoding="utf-8", newline="") as queue:
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


def load(vault) -> list[Finding]:
    """Load all finding and acknowledgment records from the append-only inbox."""
    queue = _file(vault)
    if not queue.exists():
        return []
    entries: list[Finding] = []
    for number, line in enumerate(_body(queue).splitlines(), start=1):
        if not line.strip():
            continue
        data = _line_fields(line, number)
        if "ack" in data:
            if (
                "id" in data
                or not data.keys() >= _ACK_FIELDS
                or not data.keys() <= _ACK_FIELDS | _ACK_OPTIONAL_FIELDS
            ):
                raise InboxError(f"unparseable inbox line {number}: {line!r}")
            try:
                _validate_text("ack", data["ack"])
                actor = _validate_text("actor", data["actor"])
                if (
                    not actor.startswith("human:")
                    or not actor.removeprefix("human:").strip()
                ):
                    raise ValueError("ack actor must identify a human")
                _validate_optional_text("target_hash", data.get("target-hash"))
                notice_class, notice_type, notice_date, _ = (
                    _validate_notice_fingerprint(
                        "update-notice"
                        if data.get("notice-class") is not None
                        or data.get("notice-type") is not None
                        else "",
                        data.get("notice-class"),
                        data.get("notice-type"),
                        data.get("notice-date"),
                    )
                )
                validate_reason(data["reason"])
                candidates = [
                    entry
                    for entry in entries
                    if entry.ack_of is None and entry.id == data["ack"]
                ]
                coherent = [
                    entry
                    for entry in candidates
                    if entry.target_hash == data.get("target-hash")
                    and entry.target_kind == data.get("target-kind", "identifier")
                    and (
                        entry.notice_class,
                        entry.notice_type,
                        entry.notice_date,
                    )
                    == (notice_class, notice_type, notice_date)
                ]
                if len(coherent) != 1:
                    raise ValueError(
                        "acknowledgment must reference one hash/fingerprint-coherent finding"
                    )
            except (TypeError, ValueError) as error:
                raise InboxError(
                    f"invalid acknowledgment on inbox line {number}: {line!r}"
                ) from error
            entries.append(
                Finding(
                    id=f"ack/{data['ack']}",
                    ack_of=data["ack"],
                    actor=data["actor"],
                    reason=data["reason"],
                    target_kind=data.get("target-kind", "identifier"),
                    target_hash=data.get("target-hash"),
                    notice_class=notice_class,
                    notice_type=notice_type,
                    notice_date=notice_date,
                )
            )
        elif "id" in data:
            if (
                not data.keys() >= _FINDING_FIELDS
                or not data.keys() <= _FINDING_FIELDS | _FINDING_OPTIONAL_FIELDS
            ):
                raise InboxError(f"unparseable inbox line {number}: {line!r}")
            try:
                check = _validate_text("check", data["check"])
                target = _validate_text("target", data["target"])
                target_kind = _validate_target_kind(
                    target, data.get("target-kind", "identifier")
                )
                actor = _validate_text("actor", data["actor"])
                date = _validate_date("date", data["date"])
                if data["result"] not in Result.__members__:
                    raise ValueError("invalid result")
                _validate_optional_text("target_hash", data.get("target-hash"))
                notice_class, notice_type, notice_date, detection_date = (
                    _validate_notice_fingerprint(
                        check,
                        data.get("notice-class"),
                        data.get("notice-type"),
                        data.get("notice-date"),
                        data.get("detection-date"),
                    )
                )
                validate_reason(data["reason"])
                _validate_notice_record(data["result"], notice_class)
                expected_id = finding_id(
                    check,
                    target,
                    date,
                    data.get("target-hash"),
                    notice_class,
                    notice_type,
                    notice_date,
                    target_kind,
                    data["reason"],
                )
                if data["id"] != expected_id:
                    raise ValueError("finding id does not match fields")
            except (TypeError, ValueError) as error:
                raise InboxError(
                    f"invalid finding on inbox line {number}: {line!r}"
                ) from error
            entries.append(
                Finding(
                    id=data["id"],
                    check=check,
                    target=target,
                    target_kind=target_kind,
                    result=data["result"],
                    date=date,
                    actor=actor,
                    reason=data["reason"],
                    target_hash=data.get("target-hash"),
                    notice_class=notice_class,
                    notice_type=notice_type,
                    notice_date=notice_date,
                    detection_date=detection_date,
                )
            )
        else:
            raise InboxError(f"unparseable inbox line {number}: {line!r}")
    return entries


def _scope_acknowledged(entries: list[Finding], finding: Finding) -> bool:
    """Whether a human ack closes this exact standing scope."""
    fingerprint = (
        finding.notice_class,
        finding.notice_type,
        finding.notice_date,
    )
    if finding.check == "update-notice" and finding.notice_class is None:
        # Legacy rows did not persist a discriminator. Close only an
        # unambiguous directly referenced row; never let it stand for a later
        # fingerprinted notice.
        colliding = [
            entry
            for entry in entries
            if entry.ack_of is None and entry.id == finding.id
        ]
        return len(colliding) == 1 and any(
            ack.ack_of == finding.id
            and ack.actor.startswith("human:")
            and ack.target_hash == finding.target_hash
            and ack.notice_class is None
            for ack in entries
        )
    if finding.check in REPEATABLE_ACT_CHECKS:
        # A repeatable human act is a discrete event, not a standing condition:
        # an acknowledgment closes exactly the act it references. Without this,
        # the per-act id discriminator is defeated — one ack would filter every
        # later act on the same target out of open_entries/summary.
        return any(
            ack.ack_of == finding.id
            and ack.actor.startswith("human:")
            and ack.target_hash == finding.target_hash
            for ack in entries
        )
    scope_ids = {
        entry.id
        for entry in entries
        if entry.ack_of is None
        and entry.check == finding.check
        and entry.target == finding.target
        and entry.target_kind == finding.target_kind
        and entry.target_hash == finding.target_hash
        and (
            finding.check != "update-notice"
            or (entry.notice_class, entry.notice_type, entry.notice_date) == fingerprint
        )
    }
    return any(
        ack.ack_of in scope_ids
        and ack.actor.startswith("human:")
        and ack.target_hash == finding.target_hash
        and (
            finding.check != "update-notice"
            or (ack.notice_class, ack.notice_type, ack.notice_date) == fingerprint
        )
        for ack in entries
    )


def is_acknowledged(
    vault,
    check,
    target,
    current_hash=_OMITTED_HASH,
    notice_class=None,
    notice_type=None,
    notice_date=None,
    target_kind="identifier",
) -> bool:
    """Return whether a standing scope acknowledgement matches this hash."""
    entries = load(vault)
    try:
        target_kind = _validate_target_kind(target, target_kind)
    except (TypeError, ValueError, PathCodecError):
        return False
    latest = next(
        (
            entry
            for entry in reversed(entries)
            if entry.ack_of is None
            and entry.check == check
            and entry.target == target
            and entry.target_kind == target_kind
            and (
                check != "update-notice"
                or (
                    entry.notice_class,
                    entry.notice_type,
                    entry.notice_date,
                )
                == (notice_class, notice_type, notice_date)
            )
        ),
        None,
    )
    if latest is None:
        return False
    latest = replace(
        latest,
        target_hash=(
            latest.target_hash if current_hash is _OMITTED_HASH else current_hash
        ),
    )
    return _scope_acknowledged(entries, latest)


def open_entries(vault) -> list[Finding]:
    """Return findings not closed by a matching human acknowledgment."""
    entries = load(vault)
    return [
        entry
        for entry in entries
        if entry.ack_of is None and not _scope_acknowledged(entries, entry)
    ]


def summary(vault) -> dict:
    """Return the count and age basis used by inbox orientation surfaces.

    SKIPPED findings stay in ``open_entries()`` — verify's dedup keys off
    that list to avoid re-filing them — but are excluded from the count and
    age basis returned here.

    ``oldest_age_days`` is the whole number of days between today (UTC) and
    ``oldest``, derived from that same filtered basis — supplying the fact
    so a caller never has to do this date math itself. It is ``None`` exactly
    when ``oldest`` is ``None`` (nothing unacknowledged to age); a freshly
    filed entry reports ``0``, not ``None``.
    """
    entries = [
        entry for entry in open_entries(vault) if entry.result != Result.SKIPPED.value
    ]
    oldest = min((entry.date for entry in entries if entry.date), default=None)
    oldest_age_days = (
        None
        if oldest is None
        else (
            datetime.datetime.now(datetime.UTC).date()
            - datetime.date.fromisoformat(oldest)
        ).days
    )
    return {
        "unacknowledged": len(entries),
        "oldest": oldest,
        "oldest_age_days": oldest_age_days,
    }
