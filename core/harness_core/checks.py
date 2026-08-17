"""Citation checkers (spec §6). Shared Outcome dataclass; four-state everywhere."""

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

from . import Result, bibliography, claims, inbox, webapi


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


def _doi_path(doi: str) -> str:
    """Encode DOI path data while preserving its prefix/suffix separator."""
    return quote(doi, safe="/")


def check_doi_exists(vault_root, doi: str, citekey: str | None = None) -> Outcome:
    """Return the four-state result of the DOI handle API lookup."""
    target = citekey or doi
    try:
        status, data = webapi.get_json(
            f"https://doi.org/api/handles/{_doi_path(doi)}", vault_root
        )
    except webapi.ApiError:
        return Outcome(
            "doi",
            target,
            Result.UNREACHABLE,
            "outage — DOI handle API unavailable",
            extra={"doi": doi},
        )

    if status == 404:
        return Outcome(
            "doi",
            target,
            Result.UNMATCHED,
            "mismatch — DOI does not resolve",
            extra={"doi": doi},
        )
    if status != 200:
        return Outcome(
            "doi",
            target,
            Result.UNREACHABLE,
            "outage — DOI handle API unavailable",
            extra={"doi": doi},
        )

    response_code = data.get("responseCode") if isinstance(data, dict) else None
    if type(response_code) is int and response_code == 100:
        return Outcome(
            "doi",
            target,
            Result.UNMATCHED,
            "mismatch — DOI does not resolve",
            extra={"doi": doi},
        )
    if type(response_code) is int and response_code == 1:
        return Outcome("doi", target, Result.MATCHED, "matched", extra={"doi": doi})
    return Outcome(
        "doi",
        target,
        Result.UNREACHABLE,
        "outage — unexpected DOI handle response",
        extra={"doi": doi},
    )


def registry_agency(vault_root, doi: str) -> str | None:
    """Return a validated DOI registration agency, or no route on any uncertainty."""
    try:
        status, data = webapi.get_json(
            f"https://doi.org/doiRA/{_doi_path(doi)}", vault_root
        )
    except webapi.ApiError:
        return None

    if status != 200 or not isinstance(data, list) or not data:
        return None
    record = data[0]
    if not isinstance(record, dict):
        return None
    record_doi = record.get("DOI")
    agency = record.get("RA")
    if not isinstance(record_doi, str) or not isinstance(agency, str):
        return None
    record_doi = record_doi.strip()
    if not record_doi or record_doi.casefold() != doi.strip().casefold():
        return None
    agency = agency.strip()
    if not agency:
        return None
    return agency
