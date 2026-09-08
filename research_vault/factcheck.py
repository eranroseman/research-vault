"""Deterministic claim selection and hashing for factored verification (spec §6).

Factored verification is LLM judgment — it never blocks and never mints a
`verified` event — but *which* claims a pass spends its budget on is decided
here, mechanically. This module computes a selection and writes nothing.

Forked from K-Dense-AI/scientific-agent-skills, skill `scientific-writing`,
pinned commit 336c4f8
(https://github.com/K-Dense-AI/scientific-agent-skills/tree/336c4f8/skills/scientific-writing),
license MIT, copyright (c) 2025 K-Dense Inc. Ported from it: SHA-256 hashing
of a claim's ``outcome.normalize_text`` form at the full 64 hex characters,
and verified-evidence-only counting — a citation counts as backed only where
``events.verified_checks()`` carries a genuine entry.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path

from . import claims as claims_mod
from . import events, lints
from .outcome import normalize_text

DEFAULT_CAP = 30
_ELIGIBLE_TAGS = ("paraphrase", "inference", "quote")


@dataclass(frozen=True)
class ClaimRef:
    """One claim eligible for a factored-verification pass."""

    claim_link: str
    tag: str
    line_no: int
    text_hash: str


def claim_text_hash(text: str) -> str:
    """Return the stable SHA-256 hex value of one claim's normalized text."""
    return hashlib.sha256(normalize_text(text).encode()).hexdigest()


def _claim_source_text(lines: list[str], claim: claims_mod.Claim) -> str:
    """Return the claim's declared text span: its line, plus quote continuations."""
    block = [lines[claim.line_no - 1]]
    if claim.tag == "quote":
        for line in lines[claim.line_no :]:
            if line.startswith("  > "):
                block.append(line)
            else:
                break
    return "\n".join(block)


def eligible_claims(vault_root, draft_path) -> list[ClaimRef]:
    """Return quote/paraphrase/inference claims with a resolvable citation key.

    Excludes `open-question` claims (no derivation edge — nothing to check
    against) and any claim whose citation key does not resolve to an existing
    literature note (the Iron Law's job, not this one, to catch — a claim
    that reaches a draft with a dangling citation key is a different gate's
    defect). Returned in document order.
    """
    vault = Path(vault_root)
    text = Path(draft_path).read_text(encoding="utf-8")
    lines = text.splitlines()
    refs = []
    for claim in claims_mod.parse_claims(text):
        if (
            claim.tag not in _ELIGIBLE_TAGS
            or not claim.citation_key
            or not claim.claim_id
        ):
            continue
        note = vault / "literatures" / f"{claim.citation_key}.md"
        if not note.is_file():
            continue
        source = _claim_source_text(lines, claim)
        refs.append(
            ClaimRef(
                claim_link=claims_mod.claim_link(claim.citation_key, claim.claim_id),
                tag=claim.tag,
                line_no=claim.line_no,
                text_hash=claim_text_hash(source),
            )
        )
    return refs


def _has_verified_event(vault_root, citation_key: str) -> bool:
    """Verified-evidence-only counting: never assume a note is backed."""
    note = Path(vault_root) / "literatures" / f"{citation_key}.md"
    if not note.is_file():
        return False
    return bool(events.verified_checks(note.read_text(encoding="utf-8")))


def contested_adjacent_links(vault_root, draft_path) -> set[str]:
    """Return this draft's own claim links that support disputed evidence.

    A claim carrying a `supports` link to standing counter-evidence is
    exactly what "contested-adjacent" names. The disputed-evidence *set* is
    reused from ``lints.disputed_claim_links`` (spec §6's disputed-claim
    lint) rather than re-derived here; only "which of *this draft's* claims
    point at it" is computed locally, since `lint_disputed_claim`'s own
    Outcome targets the disputed evidence being cited, not the citing claim
    a factored-verification pass would actually schedule.
    """
    disputed, _schema_outcomes = lints.disputed_claim_links(Path(vault_root))
    text = Path(draft_path).read_text(encoding="utf-8")
    contested = set()
    for claim in claims_mod.parse_claims(text):
        if not claim.citation_key or not claim.claim_id:
            continue
        supports = lints.CLAIM_LINK.findall(claim.fields.get("supports", ""))
        if any(link in disputed for link in supports):
            contested.add(claims_mod.claim_link(claim.citation_key, claim.claim_id))
    return contested


def _bucket(ref: ClaimRef, contested: set[str], has_verified_event: bool) -> int:
    if ref.tag in {"paraphrase", "inference"} and not has_verified_event:
        return 0
    if ref.claim_link in contested:
        return 1
    if ref.tag in {"paraphrase", "inference"}:
        return 2
    return 3


def select_claims(
    vault_root,
    refs: list[ClaimRef],
    contested: set[str],
    cap: int = DEFAULT_CAP,
) -> tuple[list[ClaimRef], list[ClaimRef]]:
    """Deterministically order and cap claims for one factored-verification pass.

    Order (spec §6, binding — not the plan's illustrative "e.g."):
    inference/paraphrase claims lacking any `verified` event first,
    contested-adjacent claims boosted, quote claims last (already
    deterministically covered by the quote checker). Ties within a bucket
    keep document order. Returns (selected, skipped); `skipped` is never
    silently dropped — the caller records it via the `finding` verb.
    """
    if cap < 0:
        raise ValueError("cap must be non-negative")
    verified_cache: dict[str, bool] = {}

    def has_verified_event(claim_link: str) -> bool:
        citation_key = claim_link.split("#^", 1)[0]
        if citation_key not in verified_cache:
            verified_cache[citation_key] = _has_verified_event(vault_root, citation_key)
        return verified_cache[citation_key]

    ordered = sorted(
        enumerate(refs),
        key=lambda pair: (
            _bucket(pair[1], contested, has_verified_event(pair[1].claim_link)),
            pair[0],
        ),
    )
    ordered_refs = [ref for _, ref in ordered]
    return ordered_refs[:cap], ordered_refs[cap:]


def skipped_sha256(skipped: list[ClaimRef]) -> str:
    """Return a content-derived SHA-256 hex value of one skipped set.

    Used as the skipped-set finding's `target_hash` so a same-day rerun
    with an unchanged skipped set is idempotent (the `finding` verb's own
    dedup), while a genuinely different skipped set gets its own record —
    neither collides nor silently overwrites the other.
    """
    joined = "\n".join(sorted(ref.claim_link for ref in skipped))
    return hashlib.sha256(joined.encode()).hexdigest()


def run(vault_root, draft_path, cap: int = DEFAULT_CAP) -> dict:
    """Run one end-to-end selection pass and return a JSON-able report.

    The path-resolution and JSON-printing wrapper lives in
    ``research_vault.__main__.cmd_factcheck`` — the `factcheck` subcommand
    — not here, so this module has exactly one entry point for library
    callers and tests alike.
    """
    refs = eligible_claims(vault_root, draft_path)
    contested = contested_adjacent_links(vault_root, draft_path)
    selected, skipped = select_claims(vault_root, refs, contested, cap)
    return {
        "cap": cap,
        "selected": [asdict(ref) for ref in selected],
        "skipped": [asdict(ref) for ref in skipped],
        "skipped_sha256": skipped_sha256(skipped) if skipped else None,
    }
