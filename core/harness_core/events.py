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
    data["verified"] = events
    rendered = frontmatter.serialize(data) + body
    return rendered.replace("\n", "\r\n") if "\r\n" in note_text else rendered


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
