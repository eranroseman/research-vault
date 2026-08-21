"""Quote verification against managed literature-note quote claims (spec §6)."""

import os
from pathlib import Path

from . import claims as claims_mod
from .notes import note_path
from .outcome import Outcome, Result, normalize_text
from .pathcodec import RepoPath

FUZZY_THRESHOLD = 0.90


def levenshtein_ratio(a: str, b: str) -> float:
    """Return the classic edit-distance similarity ratio for two strings."""
    if not a and not b:
        return 1.0
    previous = list(range(len(b) + 1))
    for index_a, char_a in enumerate(a, start=1):
        current = [index_a]
        for index_b, char_b in enumerate(b, start=1):
            current.append(
                min(
                    previous[index_b] + 1,
                    current[index_b - 1] + 1,
                    previous[index_b - 1] + (char_a != char_b),
                )
            )
        previous = current
    return 1.0 - previous[-1] / max(len(a), len(b))


def _source_quotes(vault_root, citekey: str) -> dict[str | None, str]:
    """Return managed source quotes keyed by their claim IDs."""
    source = note_path(vault_root, citekey)
    if not source.is_file():
        return {}
    return {
        claim.claim_id: claim.quote_text
        for claim in claims_mod.parse_claims(source.read_text())
        if claim.tag == "quote" and claim.in_managed and claim.quote_text
    }


def _extra(claim, checked_note_path: RepoPath | None) -> dict:
    extra = {"target": "managed-region"}
    if checked_note_path is not None:
        extra = {
            "note_path": checked_note_path,
            "claim_id": claim.claim_id,
            "line_no": claim.line_no,
            **extra,
        }
    return extra


def check_quote(
    vault_root,
    claim,
    source_citekey: str,
    checked_note_path: RepoPath | None = None,
) -> Outcome:
    """Compare one quote claim with its linked managed-region source text."""
    extra = _extra(claim, checked_note_path)
    if not claim.claim_id:
        return Outcome(
            "quote",
            source_citekey,
            Result.UNMATCHED,
            "schema-violation — quote claim has no anchor",
            extra=extra,
        )
    if not claim.quote_text:
        return Outcome(
            "quote",
            claims_mod.claim_link(source_citekey, claim.claim_id),
            Result.UNMATCHED,
            "schema-violation — quote claim has no text",
            extra=extra,
        )

    claim_link = claims_mod.claim_link(source_citekey, claim.claim_id)
    source_quotes = _source_quotes(vault_root, source_citekey)
    if claim.claim_id in source_quotes:
        candidates = [source_quotes[claim.claim_id]]
    else:
        candidates = list(source_quotes.values())
    candidates = [candidate for candidate in candidates if candidate]
    if not candidates:
        return Outcome(
            "quote",
            claim_link,
            Result.UNREACHABLE,
            "outage — no extractable comparison text",
            extra=extra,
        )

    ours = normalize_text(claim.quote_text)
    normalized_candidates = [normalize_text(candidate) for candidate in candidates]
    if ours in normalized_candidates:
        return Outcome("quote", claim_link, Result.MATCHED, "matched", extra=extra)

    best = max(
        levenshtein_ratio(ours, candidate) for candidate in normalized_candidates
    )
    if best >= FUZZY_THRESHOLD:
        return Outcome(
            "quote",
            claim_link,
            Result.UNMATCHED,
            f"fuzzy-quote — best ratio {best:.2f}",
            extra=extra,
        )
    return Outcome(
        "quote",
        claim_link,
        Result.UNMATCHED,
        "mismatch — quote absent from literature note",
        extra=extra,
    )


def check_all_quotes(vault_root, note_file: Path) -> list[Outcome]:
    """Check all citable quote claims in a note against managed source regions."""
    vault = Path(vault_root).resolve()
    note = Path(note_file).resolve()
    relative_note_path = RepoPath(os.fsencode(note.relative_to(vault)))
    quote_claims = [
        claim
        for claim in claims_mod.parse_claims(note.read_text())
        if claim.tag == "quote"
    ]
    if not quote_claims:
        return [
            Outcome(
                "quote",
                relative_note_path,
                Result.SKIPPED,
                "no-identifier — note has no quote claims",
                extra={"target": "managed-region"},
            )
        ]
    outcomes = []
    for claim in quote_claims:
        if not claim.citekey:
            outcomes.append(
                Outcome(
                    "quote",
                    relative_note_path,
                    Result.UNMATCHED,
                    "schema-violation — quote claim has no citekey",
                    extra=_extra(claim, relative_note_path),
                )
            )
        else:
            outcomes.append(
                check_quote(vault, claim, claim.citekey, relative_note_path)
            )
    return outcomes
