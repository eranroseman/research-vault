"""Verified events and trust-tier derivation (spec §5)."""

import datetime

from . import AGENT_ACTOR, Result, frontmatter
from . import claims as claims_mod


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
    events = list(data.get("verified", []))
    events.append(
        {
            "by": by,
            "at": at or datetime.date.today().isoformat(),
            "check": check,
        }
    )
    data["verified"] = events
    return frontmatter.serialize(data) + body


def verified_checks(note_text: str) -> list[dict]:
    """Return the note's verification-event list."""
    data, _ = frontmatter.parse(note_text)
    return list(data.get("verified", []))


def _applicable_note_checks(data: dict) -> set[str]:
    if data.get("doi"):
        return {"doi", "metadata", "update-notice"}
    if data.get("pmid"):
        return {"update-notice"}
    return set()


def trust_tier(note_text: str) -> str:
    """Derive a note's cumulative verification tier from its events."""
    data, _ = frontmatter.parse(note_text)
    events = verified_checks(note_text)
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
