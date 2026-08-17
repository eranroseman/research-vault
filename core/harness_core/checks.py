"""Citation checkers (spec §6). Shared Outcome dataclass; four-state everywhere."""

import unicodedata
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


def normalize_text(s: str) -> str:
    """Normalize quote text without changing its case."""
    text = unicodedata.normalize("NFKC", s or "")
    text = text.replace("\u00ad", "").replace("-\r\n", "").replace("-\n", "")
    return " ".join(text.split())


def _metadata_text(value: str) -> str:
    """Metadata comparisons are case-insensitive; quote matching is not."""
    return normalize_text(value).casefold()


def _metadata_authors(value) -> list[tuple[str, str]] | None:
    """Return comparable CSL authors, or reject an invalid author shape."""
    if value is None:
        return []
    if not isinstance(value, list):
        return None

    authors = []
    for author in value:
        if not isinstance(author, dict):
            return None
        family = author.get("family")
        if not isinstance(family, str) or not family.strip():
            family = author.get("literal")
        if not isinstance(family, str) or not family.strip():
            return None
        given = author.get("given")
        if given is not None and not isinstance(given, str):
            return None
        authors.append((_metadata_text(family), _metadata_text(given or "")[:1]))
    return authors


def _metadata_year(value) -> tuple[bool, int | None]:
    """Return (well_formed, optional_year) for CSL's optional issued date."""
    if value is None:
        return True, None
    if not isinstance(value, dict):
        return False, None
    parts = value.get("date-parts")
    if parts is None or parts == []:
        return True, None
    if not isinstance(parts, list) or not isinstance(parts[0], list):
        return False, None
    if not parts[0]:
        return True, None
    year = parts[0][0]
    if type(year) is not int:
        return False, None
    return True, year


def _crossref_csl(payload) -> dict | None:
    """Convert the typed Crossref works envelope into the comparable CSL subset."""
    if not isinstance(payload, dict):
        return None
    message = payload.get("message")
    if not isinstance(message, dict):
        return None
    titles = message.get("title")
    if not isinstance(titles, list) or not titles or not isinstance(titles[0], str):
        return None
    remote = dict(message)
    remote["title"] = titles[0]
    return remote


def _metadata_extra(doi: str, agency: str | None = None) -> dict:
    extra = {"doi": doi}
    if agency is not None:
        extra["agency"] = agency
    return extra


def check_metadata(vault_root, entry: dict) -> Outcome:
    """Compare a bibliography entry with metadata from its registered DOI agency."""
    target = entry.get("id", "?")
    doi = entry.get("DOI") or entry.get("doi")
    if not isinstance(doi, str) or not doi.strip():
        return Outcome(
            "metadata", target, Result.SKIPPED, "no-identifier — item has no DOI"
        )
    doi = doi.strip()

    agency = registry_agency(vault_root, doi)
    if agency is None:
        return Outcome(
            "metadata",
            target,
            Result.UNREACHABLE,
            "outage — registry routing unavailable",
            extra=_metadata_extra(doi),
        )

    try:
        if agency.casefold() == "crossref":
            status, payload = webapi.get_json(
                f"https://api.crossref.org/works/{_doi_path(doi)}", vault_root
            )
            remote = _crossref_csl(payload) if status == 200 else None
        else:
            status, remote = webapi.get_json(
                f"https://doi.org/{_doi_path(doi)}",
                vault_root,
                headers={"Accept": "application/vnd.citationstyles.csl+json"},
            )
    except webapi.ApiError:
        return Outcome(
            "metadata",
            target,
            Result.UNREACHABLE,
            "outage — registry metadata unavailable",
            extra=_metadata_extra(doi, agency),
        )

    extra = _metadata_extra(doi, agency)
    if status != 200 or not isinstance(remote, dict):
        return Outcome(
            "metadata",
            target,
            Result.UNREACHABLE,
            "outage — registry record unavailable",
            extra=extra,
        )

    remote_title = remote.get("title")
    remote_authors = _metadata_authors(remote.get("author"))
    remote_year_ok, remote_year = _metadata_year(remote.get("issued"))
    if (
        not isinstance(remote_title, str)
        or remote_authors is None
        or not remote_year_ok
    ):
        return Outcome(
            "metadata",
            target,
            Result.UNREACHABLE,
            "outage — malformed registry metadata",
            extra=extra,
        )

    local_title = entry.get("title")
    local_authors = _metadata_authors(entry.get("author"))
    local_year_ok, local_year = _metadata_year(entry.get("issued"))
    if not isinstance(local_title, str) or local_authors is None or not local_year_ok:
        return Outcome(
            "metadata",
            target,
            Result.UNREACHABLE,
            "outage — malformed bibliography metadata",
            extra=extra,
        )

    if _metadata_text(local_title) != _metadata_text(remote_title):
        return Outcome(
            "metadata",
            target,
            Result.UNMATCHED,
            "mismatch — title differs from registry",
            extra=extra,
        )
    if [family for family, _ in local_authors] != [
        family for family, _ in remote_authors
    ]:
        return Outcome(
            "metadata",
            target,
            Result.UNMATCHED,
            "mismatch — author family names differ",
            extra=extra,
        )
    if any(
        local_given and remote_given and local_given != remote_given
        for (_, local_given), (_, remote_given) in zip(
            local_authors, remote_authors, strict=True
        )
    ):
        return Outcome(
            "metadata",
            target,
            Result.UNMATCHED,
            "mismatch — author given-name initials differ",
            extra=extra,
        )
    if local_year is not None and remote_year is not None and local_year != remote_year:
        return Outcome(
            "metadata",
            target,
            Result.UNMATCHED,
            "mismatch — year differs",
            extra=extra,
        )
    return Outcome("metadata", target, Result.MATCHED, "matched", extra=extra)
