"""Citation checkers (spec §6). Shared Outcome dataclass; four-state everywhere."""

import csv
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date as _Date
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
                str(note.relative_to(vault)),
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


BLOCKING_TYPES = {"retraction", "partial_retraction", "removal", "withdrawal"}
WARN_TYPES = {"expression_of_concern", "correction", "corrigendum", "erratum"}
_INVALID = object()


def _norm_type(value) -> str | None:
    """Normalize a remote notice type, rejecting non-string members."""
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower().replace(" ", "_")
    return normalized or None


def _normalize_doi(value) -> str | None:
    """Return a canonical DOI key without accepting arbitrary scalar values."""
    if not isinstance(value, str):
        return None
    doi = value.strip()
    if doi.casefold().startswith("doi:"):
        doi = doi[4:].strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "http://dx.doi.org/"):
        if doi.casefold().startswith(prefix):
            doi = doi[len(prefix) :]
            break
    doi = doi.strip()
    return doi.casefold() if doi else None


def _normalize_pmid(value) -> str | None:
    """Return a numeric PMID key while excluding Python's bool-as-int leak."""
    if type(value) is int:
        value = str(value)
    if not isinstance(value, str):
        return None
    pmid = value.strip()
    if pmid.casefold().startswith("pmid:"):
        pmid = pmid[5:].strip()
    return pmid if pmid.isdecimal() and pmid != "0" else None


def _entry_identifiers(entry: dict) -> tuple[str | None, str | None]:
    if not isinstance(entry, dict):
        return None, None
    return (
        _normalize_doi(entry.get("DOI") or entry.get("doi")),
        _normalize_pmid(entry.get("PMID") or entry.get("pmid")),
    )


def _notice_target(entry: dict, doi: str | None, pmid: str | None) -> str:
    if isinstance(entry, dict) and isinstance(entry.get("id"), str) and entry["id"]:
        return entry["id"]
    return doi or pmid or "?"


def _notice_date_from_updated(value):
    """Validate Crossref's optional date-parts and return an ISO date or None."""
    if value is None:
        return None
    if not isinstance(value, dict):
        return _INVALID
    if "date-parts" not in value or value["date-parts"] is None:
        return None
    date_parts = value["date-parts"]
    if not isinstance(date_parts, list):
        return _INVALID
    if not date_parts:
        return _INVALID
    if len(date_parts) != 1 or not isinstance(date_parts[0], list):
        return _INVALID
    parts = date_parts[0]
    if not parts:
        return _INVALID
    if len(parts) > 3 or any(type(part) is not int for part in parts):
        return _INVALID
    year, month, day = (parts + [1, 1])[:3]
    try:
        return _Date(year, month, day).isoformat()
    except ValueError:
        return _INVALID


def _crossref_notices(payload) -> tuple[list[dict], list[dict]] | None:
    """Validate Crossref's envelope and separate blocking/warn notice records."""
    if not isinstance(payload, dict) or not isinstance(payload.get("message"), dict):
        return None
    message = payload["message"]
    updates = message.get("updated-by", [])
    if not isinstance(updates, list):
        return None

    blocking, warns = [], []
    for update in updates:
        if not isinstance(update, dict):
            return None
        notice_type = _norm_type(update.get("type"))
        if notice_type is None:
            return None
        notice_date = _notice_date_from_updated(update.get("updated"))
        if notice_date is _INVALID:
            return None
        notice = {"type": notice_type, "notice_date": notice_date}
        if notice_type in BLOCKING_TYPES:
            blocking.append(notice)
        elif notice_type in WARN_TYPES:
            warns.append(notice)
        elif notice_type == "reinstatement":
            blocking.append({"type": "reinstatement", "notice_date": notice_date})
    return blocking, warns


def _active_blocking_notices(notices: list[dict]) -> list[dict]:
    """Remove only dated blocks that a later dated reinstatement clears."""
    reinstatements = [
        notice["notice_date"]
        for notice in notices
        if notice["type"] == "reinstatement" and notice["notice_date"] is not None
    ]
    return [
        notice
        for notice in notices
        if notice["type"] != "reinstatement"
        and (
            notice["notice_date"] is None
            or not any(
                reinstatement >= notice["notice_date"]
                for reinstatement in reinstatements
            )
        )
    ]


def _effective_blocking(notices: list[dict]) -> dict | None:
    """Choose a stable active blocker, preferring the most recent known notice."""
    if not notices:
        return None
    return max(
        notices,
        key=lambda notice: (
            notice["notice_date"] is not None,
            notice["notice_date"] or "",
            notice["type"],
        ),
    )


def _merge_warn_notices(*outcomes: Outcome | None) -> list[dict]:
    """Merge well-formed warning notices in deterministic, de-duplicated order."""
    notices = set()
    for outcome in outcomes:
        if outcome is None or not isinstance(outcome.extra, dict):
            continue
        values = outcome.extra.get("warn_notices", [])
        if not isinstance(values, list):
            continue
        for value in values:
            if not isinstance(value, dict):
                continue
            notice_type = _norm_type(value.get("type"))
            notice_date = value.get("notice_date")
            if notice_type not in WARN_TYPES or not (
                notice_date is None or isinstance(notice_date, str)
            ):
                continue
            notices.add((notice_type, notice_date))
    return [
        {"type": notice_type, "notice_date": notice_date}
        for notice_type, notice_date in sorted(
            notices, key=lambda notice: (notice[0], notice[1] is None, notice[1] or "")
        )
    ]


def _blocking_outcome(
    target: str, notice: dict, detection_date: str, warns=()
) -> Outcome:
    extra = {
        "class": "blocking",
        "type": notice["type"],
        "notice_date": notice["notice_date"],
        "detection_date": detection_date,
    }
    if warns:
        extra["warn_notices"] = list(warns)
    return Outcome(
        "update-notice",
        target,
        Result.UNMATCHED,
        f"retracted — {notice['type']}",
        extra=extra,
    )


def check_update_notice(vault_root, entry: dict, detection_date: str) -> Outcome:
    """Check a registered DOI for update notices, retaining warning-tier notices."""
    doi, pmid = _entry_identifiers(entry)
    target = _notice_target(entry, doi, pmid)
    if doi is None and pmid is None:
        return Outcome(
            "update-notice", target, Result.SKIPPED, "no-identifier — no DOI or PMID"
        )
    if doi is None:
        return Outcome(
            "update-notice",
            target,
            Result.SKIPPED,
            "no-identifier — live leg needs a DOI; RW batch covers PMID",
        )

    agency = registry_agency(vault_root, doi)
    if agency is None:
        return Outcome(
            "update-notice",
            target,
            Result.UNREACHABLE,
            "outage — registry routing unavailable",
        )

    try:
        if agency.casefold() == "crossref":
            status, payload = webapi.get_json(
                f"https://api.crossref.org/works/{_doi_path(doi)}", vault_root
            )
            notices = _crossref_notices(payload) if status == 200 else None
            if notices is None:
                return Outcome(
                    "update-notice",
                    target,
                    Result.UNREACHABLE,
                    "outage — malformed Crossref notice record",
                )
            blocking, warns = notices
            active = _effective_blocking(_active_blocking_notices(blocking))
            warns = _merge_warn_notices(
                Outcome(
                    "update-notice",
                    target,
                    Result.MATCHED,
                    "matched",
                    {"warn_notices": warns},
                )
            )
            if active is not None:
                return _blocking_outcome(target, active, detection_date, warns)
            return Outcome(
                "update-notice",
                target,
                Result.MATCHED,
                "matched",
                extra={"warn_notices": warns} if warns else {},
            )

        identifier = quote(f"https://doi.org/{doi}", safe="")
        status, payload = webapi.get_json(
            f"https://api.openalex.org/works/{identifier}",
            vault_root,
            params={"select": "is_retracted"},
        )
        if status != 200 or not isinstance(payload, dict):
            return Outcome(
                "update-notice",
                target,
                Result.UNREACHABLE,
                "outage — malformed OpenAlex notice record",
            )
        is_retracted = payload.get("is_retracted")
        if type(is_retracted) is not bool:
            return Outcome(
                "update-notice",
                target,
                Result.UNREACHABLE,
                "outage — malformed OpenAlex notice record",
            )
        if is_retracted:
            return _blocking_outcome(
                target,
                {"type": "retraction", "notice_date": None},
                detection_date,
            )
        return Outcome("update-notice", target, Result.MATCHED, "matched")
    except webapi.ApiError:
        return Outcome(
            "update-notice",
            target,
            Result.UNREACHABLE,
            "outage — update-notice service unavailable",
        )


def _rw_date(value) -> str | None | object:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if not isinstance(value, str):
        return _INVALID
    try:
        return _Date.fromisoformat(value.strip()).isoformat()
    except ValueError:
        return _INVALID


def load_rw_csv(path: Path) -> dict:
    """Load well-formed Retraction Watch rows into DOI and PMID indexes."""
    by_doi: dict[str, list[dict]] = defaultdict(list)
    by_pmid: dict[str, list[dict]] = defaultdict(list)
    with Path(path).open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not isinstance(row, dict):
                continue
            notice_type = _norm_type(row.get("RetractionNature"))
            notice_date = _rw_date(row.get("RetractionDate"))
            doi = _normalize_doi(row.get("OriginalPaperDOI"))
            pmid = _normalize_pmid(row.get("OriginalPaperPubMedID"))
            if (
                notice_type not in BLOCKING_TYPES | WARN_TYPES
                or notice_date is _INVALID
                or (doi is None and pmid is None)
            ):
                continue
            record = {"type": notice_type, "notice_date": notice_date}
            if doi is not None:
                by_doi[doi].append(record)
            if pmid is not None:
                by_pmid[pmid].append(record)
    return {"doi": dict(by_doi), "pmid": dict(by_pmid)}


def _rw_hits(index, identifier: str | None) -> list[dict]:
    if identifier is None or not isinstance(index, dict):
        return []
    values = index.get(identifier, [])
    if isinstance(values, dict):
        values = [values]
    if not isinstance(values, list):
        return []
    return [value for value in values if isinstance(value, dict)]


def check_rw_batch(entry: dict, rw: dict, detection_date: str) -> Outcome | None:
    """Return the RW leg outcome after evaluating both normalized identifiers."""
    doi, pmid = _entry_identifiers(entry)
    target = _notice_target(entry, doi, pmid)
    if not isinstance(rw, dict):
        return None
    hits = _rw_hits(rw.get("doi"), doi) + _rw_hits(rw.get("pmid"), pmid)
    notices = {
        (notice_type, notice_date)
        for hit in hits
        for notice_type, notice_date in [
            (_norm_type(hit.get("type", hit.get("nature"))), hit.get("notice_date"))
        ]
        if notice_type in BLOCKING_TYPES | WARN_TYPES
        and (notice_date is None or isinstance(notice_date, str))
    }
    blocking = [
        {"type": notice_type, "notice_date": notice_date}
        for notice_type, notice_date in notices
        if notice_type in BLOCKING_TYPES
    ]
    warns = [
        {"type": notice_type, "notice_date": notice_date}
        for notice_type, notice_date in notices
        if notice_type in WARN_TYPES
    ]
    active = _effective_blocking(blocking)
    warns = _merge_warn_notices(
        Outcome(
            "update-notice", target, Result.MATCHED, "matched", {"warn_notices": warns}
        )
    )
    if active is not None:
        return _blocking_outcome(target, active, detection_date, warns)
    if warns:
        return Outcome(
            "update-notice",
            target,
            Result.MATCHED,
            "matched",
            extra={"warn_notices": warns},
        )
    return None


def reduce_update_notice_outcomes(
    live: Outcome | None, rw: Outcome | None
) -> Outcome | None:
    """Reduce live/RW notice legs to one deterministic outcome for orchestration."""
    outcomes = [outcome for outcome in (live, rw) if isinstance(outcome, Outcome)]
    if not outcomes:
        return None
    if len(outcomes) == 2 and outcomes[0].target != outcomes[1].target:
        return Outcome(
            "update-notice",
            outcomes[0].target,
            Result.UNREACHABLE,
            "outage — update-notice target mismatch",
        )
    warnings = _merge_warn_notices(*outcomes)
    blocking = [
        outcome
        for outcome in outcomes
        if outcome.result is Result.UNMATCHED
        and outcome.extra.get("class") == "blocking"
    ]
    if blocking:
        chosen = max(
            blocking,
            key=lambda outcome: (
                outcome.extra.get("notice_date") is not None,
                outcome.extra.get("notice_date") or "",
                outcome.extra.get("type") or "",
            ),
        )
    else:
        chosen = next(
            (
                outcome
                for result in (Result.UNREACHABLE, Result.MATCHED, Result.SKIPPED)
                for outcome in outcomes
                if outcome.result is result
            ),
            outcomes[0],
        )
    extra = dict(chosen.extra)
    if warnings:
        extra["warn_notices"] = warnings
    else:
        extra.pop("warn_notices", None)
    return Outcome(
        chosen.check, chosen.target, chosen.result, chosen.reason, extra=extra
    )
