"""Verified events and trust-tier derivation (spec §5)."""

import datetime

from . import AGENT_ACTOR, Result, frontmatter
from . import claims as claims_mod


def _verified_events(data: dict) -> tuple[list[dict], bool]:
    """Return valid events and whether the stored collection is malformed."""
    raw_events = data.get("verified")
    if raw_events is None:
        return [], False
    if not isinstance(raw_events, list) or not all(
        isinstance(event, dict) for event in raw_events
    ):
        return [], True
    return list(raw_events), False


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

    data, body = frontmatter.parse(note_text)
    events, malformed = _verified_events(data)
    if malformed:
        raise ValueError("verified frontmatter must be a list of event mappings")
    events.append(
        {
            "by": by,
            "at": at or datetime.date.today().isoformat(),
            "check": check,
        }
    )
    return _replace_verified_events(note_text, events, body)


def _replace_verified_events(note_text: str, events: list[dict], body: str) -> str:
    """Lexically replace only the verifier-owned top-level event list."""
    lines = note_text.splitlines(keepends=True)
    if not lines or lines[0] not in {"---\n", "---\r\n"}:
        envelope = frontmatter.serialize({"verified": events})
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
        if line.rstrip("\r\n").rstrip(" \t") == "verified:"
    ]
    if len(headers) > 1:
        raise ValueError("verified frontmatter must have one event list")
    newline = _line_ending(lines[headers[0] if headers else close]) or "\n"
    rendered = _render_verified_events(events, newline)
    if not headers:
        return "".join(lines[:close] + [rendered] + lines[close:])
    start = headers[0]
    end = start + 1
    while end < close and lines[end].startswith("  - "):
        end += 1
    return "".join(lines[:start] + [rendered] + lines[end:])


def _render_verified_events(events: list[dict], newline: str) -> str:
    """Serialize new event rows without touching neighboring frontmatter."""
    rendered = frontmatter.serialize({"verified": events}).splitlines()
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
    return events


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
    if malformed:
        return "unverified"
    checks = {str(event.get("check", "")) for event in events}
    machine_confirmed = _applicable_note_checks(data) <= checks
    citekey = data.get("citekey", "")

    for claim in claims_mod.parse_claims(note_text):
        if claim.tag != "quote" or not claim.in_managed or not claim.claim_id:
            continue
        address = claims_mod.claim_address(citekey, claim.claim_id)
        quote_checks = {
            f"quote:{address}:managed-region",
            f"quote:{address}:source-text",
        }
        if checks.isdisjoint(quote_checks):
            machine_confirmed = False

    if not machine_confirmed:
        return "unverified"
    if any(str(event.get("by", "")).startswith("human:") for event in events):
        return "human-reviewed"
    return "machine-confirmed"
