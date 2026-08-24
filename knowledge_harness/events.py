"""Verified events and trust-tier derivation (spec §5)."""

import datetime
import re

from . import AGENT_ACTOR, frontmatter
from . import claims as claims_mod
from .outcome import Result

FAILURES_FIELD = "failed-verification"
_QUOTE_CHECK = re.compile(
    r"^quote:(?P<claim_link>[^\r\n:]+#\^[^\r\n:]+):(?P<target>managed-region|source-text)$"
)


def _single_line(value) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and "\n" not in value
        and "\r" not in value
        and "\0" not in value
    )


def _calendar_date(value) -> bool:
    if not _single_line(value) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        return datetime.date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _valid_event(event) -> bool:
    return (
        type(event) is dict
        and set(event) == {"by", "at", "check"}
        and _single_line(event["by"])
        and _calendar_date(event["at"])
        and _single_line(event["check"])
    )


def _duplicate_header(note_text: str, field: str) -> bool:
    lines = note_text.splitlines()
    if not lines or lines[0] != "---":
        return False
    close = next(
        (index for index, line in enumerate(lines[1:], 1) if line == "---"), None
    )
    if close is None:
        return False
    return sum(line.startswith(f"{field}:") for line in lines[1:close]) > 1


def _verified_events(data: dict) -> tuple[list[dict], bool]:
    """Return valid events and whether the stored collection is malformed."""
    raw_events = data.get("verified")
    if raw_events is None:
        return [], False
    if not isinstance(raw_events, list) or not all(
        _valid_event(event) for event in raw_events
    ):
        return [], True
    return list(raw_events), False


def _failure_rows(data: dict) -> tuple[list[dict], bool]:
    raw = data.get(FAILURES_FIELD)
    if raw is None:
        return [], False
    valid_results = {result.value for result in Result if result is not Result.MATCHED}
    if not isinstance(raw, list) or not all(
        type(row) is dict
        and set(row) == {"check", "result"}
        and _single_line(row["check"])
        and row["result"] in valid_results
        for row in raw
    ):
        return [], True
    checks = [row["check"] for row in raw]
    if len(checks) != len(set(checks)) or checks != sorted(checks):
        return [], True
    return list(raw), False


def record_pass(
    note_text: str,
    check: str,
    result: Result,
    by: str = AGENT_ACTOR,
    at: str | None = None,
) -> str:
    """Append a verification event for a successful deterministic check."""
    if result is not Result.MATCHED:
        raise ValueError(f"only MATCHED mints verified events, got {result}")
    if not _single_line(by):
        raise ValueError("verified event by must be a nonempty single-line string")
    if not _single_line(check):
        raise ValueError("verified event check must be a nonempty single-line string")
    at = datetime.datetime.now(datetime.UTC).date().isoformat() if at is None else at
    if not _calendar_date(at):
        raise ValueError("verified event at must be a YYYY-MM-DD calendar date")

    data, body = frontmatter.parse(note_text)
    events, malformed = _verified_events(data)
    if malformed or _duplicate_header(note_text, "verified"):
        raise ValueError("verified frontmatter must be a list of event mappings")
    failures, malformed_failures = _failure_rows(data)
    if malformed_failures or _duplicate_header(note_text, FAILURES_FIELD):
        raise ValueError(
            "failed-verification frontmatter must be a deterministic list of mappings"
        )
    failures = [row for row in failures if row["check"] != check]
    events.append(
        {
            "by": by,
            "at": at,
            "check": check,
        }
    )
    without_failure = _replace_frontmatter_list(
        note_text, FAILURES_FIELD, failures, body
    )
    _, updated_body = frontmatter.parse(without_failure)
    return _replace_frontmatter_list(without_failure, "verified", events, updated_body)


def record_failure(note_text: str, check: str, result: Result) -> str:
    """Upsert one deterministic current-failure projection row."""
    if result is Result.MATCHED or not isinstance(result, Result):
        raise ValueError("record_failure requires a non-MATCHED Result")
    if not _single_line(check):
        raise ValueError("failure check must be a nonempty single-line string")
    data, body = frontmatter.parse(note_text)
    _, malformed_events = _verified_events(data)
    if malformed_events or _duplicate_header(note_text, "verified"):
        raise ValueError("verified frontmatter must be a list of event mappings")
    failures, malformed = _failure_rows(data)
    if malformed or _duplicate_header(note_text, FAILURES_FIELD):
        raise ValueError(
            "failed-verification frontmatter must be a deterministic list of mappings"
        )
    by_check = {row["check"]: row for row in failures}
    by_check[check] = {"check": check, "result": result.value}
    updated = [by_check[key] for key in sorted(by_check)]
    if updated == failures:
        return note_text
    return _replace_frontmatter_list(note_text, FAILURES_FIELD, updated, body)


def _replace_frontmatter_list(
    note_text: str, field: str, rows: list[dict], body: str
) -> str:
    """Lexically replace one top-level flat-parser list without neighboring churn."""
    lines = note_text.splitlines(keepends=True)
    if not lines or lines[0] not in {"---\n", "---\r\n"}:
        if not rows:
            return note_text
        envelope = frontmatter.serialize({field: rows})
        newline = _first_line_ending(body)
        if newline == "\r\n":
            envelope = envelope.replace("\n", newline)
        return envelope + body
    close = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line in {"---\n", "---\r\n"}
        ),
        None,
    )
    if close is None:
        # ``frontmatter.parse`` has already rejected this, but leave the
        # defensive fallback byte-preserving if its grammar grows later.
        return note_text
    headers = [
        index
        for index, line in enumerate(lines[1:close], start=1)
        if line.rstrip("\r\n").rstrip(" \t") == f"{field}:"
    ]
    if len(headers) > 1:
        raise ValueError(f"{field} frontmatter must have one list")
    if not headers and not rows:
        return note_text
    newline = _line_ending(lines[headers[0] if headers else close]) or "\n"
    rendered = _render_frontmatter_list(field, rows, newline) if rows else ""
    if not headers:
        insert = close - 1 if lines[close - 1] in {"\n", "\r\n"} else close
        return "".join([*lines[:insert], rendered, *lines[insert:]])
    start = headers[0]
    end = start + 1
    while end < close and lines[end].startswith("  - "):
        end += 1
    return "".join([*lines[:start], rendered, *lines[end:]])


def _render_frontmatter_list(field: str, rows: list[dict], newline: str) -> str:
    rendered = frontmatter.serialize({field: rows}).splitlines()
    return "".join(f"{line}{newline}" for line in rendered[1:-1])


def _line_ending(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return ""


def _first_line_ending(text: str) -> str:
    for line in text.splitlines(keepends=True):
        ending = _line_ending(line)
        if ending:
            return ending
    return "\n"


def verified_checks(note_text: str) -> list[dict]:
    """Return the note's verification-event list."""
    data, _ = frontmatter.parse(note_text)
    events, _ = _verified_events(data)
    return [] if _duplicate_header(note_text, "verified") else events


def current_failures(note_text: str) -> list[dict]:
    """Return valid deterministic current-failure projection rows."""
    data, _ = frontmatter.parse(note_text)
    failures, _ = _failure_rows(data)
    return [] if _duplicate_header(note_text, FAILURES_FIELD) else failures


def _applicable_note_checks(data: dict) -> set[str]:
    if data.get("doi"):
        return {"doi", "metadata", "update-notice"}
    if data.get("pmid"):
        return {"update-notice"}
    return set()


def trust_tier(note_text: str) -> str:
    """Derive a note's cumulative verification tier from its events."""
    data, _ = frontmatter.parse(note_text)
    events, malformed = _verified_events(data)
    failures, malformed_failures = _failure_rows(data)
    if (
        malformed
        or malformed_failures
        or _duplicate_header(note_text, "verified")
        or _duplicate_header(note_text, FAILURES_FIELD)
    ):
        return "unverified"
    checks = {str(event.get("check", "")) for event in events}
    applicable = _applicable_note_checks(data)
    machine_confirmed = applicable <= checks
    citekey = data.get("citekey", "")

    for row in failures:
        check = row["check"]
        quote = _QUOTE_CHECK.fullmatch(check)
        if check in applicable or (
            quote is not None and quote.group("claim_link").split("#^", 1)[0] == citekey
        ):
            machine_confirmed = False

    has_managed_quotes = False
    for claim in claims_mod.parse_claims(note_text):
        if claim.tag != "quote" or not claim.in_managed or not claim.claim_id:
            continue
        has_managed_quotes = True
        claim_link = claims_mod.claim_link(citekey, claim.claim_id)
        quote_checks = {
            f"quote:{claim_link}:managed-region",
            f"quote:{claim_link}:source-text",
        }
        if checks.isdisjoint(quote_checks):
            machine_confirmed = False

    if not applicable and not has_managed_quotes:
        # A subset test over an empty applicable set is vacuously true; require
        # at least one deterministic check to have run and matched instead.
        machine_confirmed = False

    if not machine_confirmed:
        return "unverified"
    if any(str(event.get("by", "")).startswith("human:") for event in events):
        return "human-reviewed"
    return "machine-confirmed"
