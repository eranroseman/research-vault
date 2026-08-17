"""Citation checkers (spec §6). Shared Outcome dataclass; four-state everywhere."""

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from . import Result, bibliography, claims, inbox


@dataclass
class Outcome:
    check: str
    target: str
    result: Result
    reason: str
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        self.reason = inbox.validate_reason(self.reason)
        self.extra = dict(self.extra)


def _claim_origins(note_text: str) -> dict[str, list[dict]]:
    """Map cited keys to the claim lines that contain them."""
    origins = defaultdict(list)
    lines = note_text.splitlines()
    for claim in claims.parse_claims(note_text):
        for citation in claims.CITE_RE.finditer(lines[claim.line_no - 1]):
            origins[citation.group("key")].append(
                {
                    "claim_id": claim.claim_id,
                    "line_no": claim.line_no,
                    "locator": citation.group("loc"),
                }
            )
    return origins


def check_citekeys(vault_root, note_path: Path) -> list[Outcome]:
    """Check every citation in a note against the local bibliography universe."""
    vault = Path(vault_root).resolve()
    note = Path(note_path).resolve()
    note_text = note.read_text()
    cited = sorted({match.group("key") for match in claims.CITE_RE.finditer(note_text)})
    if not cited:
        return [
            Outcome(
                "citekey",
                str(note),
                Result.SKIPPED,
                "no-identifier — note cites nothing",
            )
        ]

    bibliography_universe = bibliography.load(vault)
    origins = _claim_origins(note_text)
    note_path = str(note.relative_to(vault))
    outcomes = []
    for citekey in cited:
        result = (
            Result.MATCHED
            if citekey in bibliography_universe.citekeys
            else Result.UNMATCHED
        )
        reason = (
            "matched"
            if result is Result.MATCHED
            else "mismatch — citekey not in bibliography"
        )
        outcomes.append(
            Outcome(
                "citekey",
                citekey,
                result,
                reason,
                extra={"note_path": note_path, "claims": origins[citekey]},
            )
        )
    return outcomes
