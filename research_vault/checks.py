"""Citation checkers (spec §6). Shared Outcome dataclass; four-state everywhere."""

import csv
import os
import re
from collections import defaultdict
from collections.abc import Mapping
from datetime import date as _date
from datetime import datetime as _datetime
from pathlib import Path
from urllib.parse import quote, urlsplit

from . import bibliography, claims, webapi
from .outcome import (
    Outcome,
    Result,
    _detached_extra,
    normalize_text,  # noqa: F401  (re-exported vocabulary)
)
from .pathcodec import RepoPath, decode_repo_path

_RECORD_FIELDS = {
    "check",
    "target",
    "target_kind",
    "result",
    "reason",
    "extra",
    "path_extra_fields",
}


def outcome_to_record(outcome: Outcome) -> dict[str, object]:
    """Return one detached JSON record after revalidating typed path metadata."""
    if not isinstance(outcome, Outcome):
        raise TypeError("expected Outcome")
    if outcome.target_kind == "repo-path":
        # __post_init__ encodes every RepoPath target to text, so this narrow only
        # re-states an established invariant; it raises exactly what the delegated
        # decode_repo_path type check would raise, so behaviour is unchanged.
        if not isinstance(outcome.target, str):
            raise TypeError("encoded repository path must be text")
        decode_repo_path(outcome.target)
    elif outcome.target_kind != "identifier":
        raise ValueError("invalid Outcome target kind")
    if tuple(sorted(set(outcome.path_extra_fields))) != outcome.path_extra_fields:
        raise ValueError("invalid Outcome path metadata")
    for field_name in outcome.path_extra_fields:
        value = outcome.extra.get(field_name)
        if type(value) is not str:
            raise ValueError("typed Outcome path extra is missing")
        decode_repo_path(value)
    return {
        "check": outcome.check,
        "target": outcome.target,
        "target_kind": outcome.target_kind,
        "result": outcome.result.value,
        "reason": outcome.reason,
        "extra": _detached_extra(outcome.extra),
        "path_extra_fields": list(outcome.path_extra_fields),
    }


def outcome_from_record(record: Mapping[str, object]) -> Outcome:
    """Rebuild a typed Outcome from its exact JSON record contract."""
    if not isinstance(record, Mapping) or set(record) != _RECORD_FIELDS:
        raise ValueError("Outcome record has missing or unknown fields")
    check = record["check"]
    target = record["target"]
    kind = record["target_kind"]
    result = record["result"]
    reason = record["reason"]
    extra = record["extra"]
    path_fields = record["path_extra_fields"]
    if type(check) is not str or type(target) is not str or type(reason) is not str:
        raise TypeError("Outcome record text fields must be strings")
    if kind not in {"identifier", "repo-path"}:
        raise ValueError("Outcome record target_kind is invalid")
    if type(result) is not str:
        raise TypeError("Outcome record result must be text")
    try:
        result_value = Result(result)
    except ValueError as error:
        raise ValueError("Outcome record result is invalid") from error
    if not isinstance(extra, Mapping):
        raise TypeError("Outcome record extra must be an object")
    if not isinstance(path_fields, list) or any(
        type(field_name) is not str for field_name in path_fields
    ):
        raise TypeError("Outcome path_extra_fields must be a JSON array of strings")
    if path_fields != sorted(set(path_fields)):
        raise ValueError("Outcome path_extra_fields must be sorted and unique")
    mutable_extra = _detached_extra(extra)
    for field_name in path_fields:
        if (
            field_name not in mutable_extra
            or type(mutable_extra[field_name]) is not str
        ):
            raise ValueError("Outcome path extra metadata does not name a string")
        mutable_extra[field_name] = RepoPath(
            decode_repo_path(mutable_extra[field_name])
        )
    typed_target: str | RepoPath = target
    if kind == "repo-path":
        typed_target = RepoPath(decode_repo_path(target))
    outcome = Outcome(check, typed_target, result_value, reason, mutable_extra)
    if (
        outcome.target_kind != kind
        or list(outcome.path_extra_fields) != path_fields
        or outcome.target != target
    ):
        raise ValueError("Outcome record path metadata is incoherent")
    return outcome


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


def check_citation_keys(
    vault_root, note_path: Path, bibliography_universe=None
) -> list[Outcome]:
    """Check every citation in a note against the local bibliography universe."""
    vault = Path(vault_root).resolve()
    note = Path(note_path).resolve()
    relative_raw = os.fsencode(note.relative_to(vault))
    note_text = note.read_text()
    cited = sorted({match.group("key") for match in claims.CITE_RE.finditer(note_text)})
    if not cited:
        return [
            Outcome(
                "citation-key",
                RepoPath(relative_raw),
                Result.SKIPPED,
                "no-identifier — note cites nothing",
            )
        ]

    if bibliography_universe is None:
        bibliography_universe = bibliography.load(vault)
    origins = _claim_origins(note_text)
    typed_note_path = RepoPath(relative_raw)
    outcomes = []
    for citation_key in cited:
        if citation_key not in bibliography_universe:
            result = Result.UNMATCHED
            reason = "mismatch — citation key not in bibliography"
        elif not (vault / "literatures" / f"{citation_key}.md").is_file():
            # Tier 2: bibliography membership alone is not citability — the
            # cited source needs an imported literature note to verify a
            # quote or paraphrase against.
            result = Result.UNMATCHED
            reason = "not-captured — cited citation key has no literature note"
        else:
            result = Result.MATCHED
            reason = "matched"
        outcomes.append(
            Outcome(
                "citation-key",
                citation_key,
                result,
                reason,
                extra={"note_path": typed_note_path, "claims": origins[citation_key]},
            )
        )
    return outcomes


def _doi_path(doi: str) -> str:
    """Encode DOI path data while preserving its prefix/suffix separator."""
    return quote(doi, safe="/")


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


def metadata_year(value) -> tuple[bool, int | None]:
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
    """Validate Crossref's optional date-parts and return it at its own
    precision: ``YYYY``, ``YYYY-MM``, or ``YYYY-MM-DD``. A missing month/day
    defaults to 1 for range validation only and is never emitted; a present
    but out-of-range month/day (including 0) still fails validation."""
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
    year, month, day = [*parts, None, None][:3]
    try:
        _date(year, month if month is not None else 1, day if day is not None else 1)
    except ValueError:
        return _INVALID
    if day is not None:
        return f"{year:04d}-{month:02d}-{day:02d}"
    if month is not None:
        return f"{year:04d}-{month:02d}"
    return f"{year:04d}"


def _crossref_notices(payload) -> tuple[list[dict], list[dict]] | None:
    """Validate Crossref's envelope and separate blocking/warn notice records.
    Also reads relation.is-retracted-by as a second, additive retraction
    signal: it can only add a blocking notice, never invalidate an
    updated-by verdict already established above, so a malformed relation
    entry is skipped rather than failing the whole payload. Each relation
    notice carries no date, so undated relation notices never auto-clear;
    reinstatement requires a dated source or a human ack."""
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

    # A withdrawal and a retraction are distinct signals, so the weaker
    # must not mask the stronger.
    already_retracted = any(notice["type"] == "retraction" for notice in blocking)
    relation = message.get("relation")
    retracted_by = (
        relation.get("is-retracted-by") if isinstance(relation, dict) else None
    )
    if not isinstance(retracted_by, list):
        retracted_by = []
    if not already_retracted:
        for entry in retracted_by:
            if not (
                isinstance(entry, dict)
                and isinstance(entry.get("id"), str)
                and entry["id"]
            ):
                continue
            blocking.append(
                {
                    "type": "retraction",
                    "notice_date": None,
                    "source": "relation",
                    "id": entry["id"],
                }
            )
    return blocking, warns


def _dates_incomparable(a: str, b: str) -> bool:
    """True when neither date's range can be shown to precede the other's.
    ISO date-precision strings denote nested-or-disjoint intervals, so one
    being a prefix of the other (equality included) is an exact test for
    interval overlap, not a heuristic — except two full (``YYYY-MM-DD``)
    dates, which denote single days and are always comparable."""
    if len(a) == 10 and len(b) == 10:
        return False
    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
    return longer.startswith(shorter)


def _reinstatement_clears(reinstatement_date: str, notice_date: str) -> bool:
    """A reinstatement clears a blocking notice only when the two dates'
    precisions leave no ambiguity about which came first."""
    if _dates_incomparable(reinstatement_date, notice_date):
        return False
    return reinstatement_date >= notice_date


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
                _reinstatement_clears(reinstatement, notice["notice_date"])
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


def _merge_warn_notices(*notice_groups) -> list[dict]:
    """Merge warning notices in deterministic, de-duplicated order."""
    notices = set()
    for values in notice_groups:
        if not isinstance(values, (list, tuple)):
            continue
        for value in values:
            if not isinstance(value, Mapping):
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


def _provider_unreachable(target: str, provider: str) -> Outcome:
    return Outcome(
        "update-notice",
        target,
        Result.UNREACHABLE,
        f"outage — {provider} version status unavailable",
    )


def _provider_skipped(target: str) -> Outcome:
    return Outcome(
        "update-notice",
        target,
        Result.SKIPPED,
        "no-identifier — item has no local version",
    )


def _version_mismatch(target: str, provider: str) -> Outcome:
    return Outcome(
        "update-notice",
        target,
        Result.UNMATCHED,
        f"mismatch — {provider} version differs",
    )


def _nonempty_version(value) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _datacite_version_outcome(
    vault_root, entry: dict, doi: str, target: str
) -> Outcome:
    local_version = _nonempty_version(entry.get("version"))
    if local_version is None:
        return _provider_skipped(target)
    status, payload = webapi.get_json(
        f"https://api.datacite.org/dois/{_doi_path(doi)}", vault_root
    )
    data = payload.get("data") if isinstance(payload, dict) else None
    attributes = data.get("attributes") if isinstance(data, dict) else None
    remote_version = (
        _nonempty_version(attributes.get("version"))
        if isinstance(attributes, dict)
        else None
    )
    if (
        status != 200
        or not isinstance(data, dict)
        or data.get("type") != "dois"
        or _normalize_doi(data.get("id")) != doi
        or not isinstance(attributes, dict)
        or _normalize_doi(attributes.get("doi")) != doi
        or remote_version is None
    ):
        return _provider_unreachable(target, "DataCite")
    if remote_version != local_version:
        return _version_mismatch(target, "DataCite")
    return Outcome("update-notice", target, Result.MATCHED, "matched")


def _arxiv_identifier(doi: str) -> str | None:
    prefix = "10.48550/arxiv."
    if not doi.startswith(prefix):
        return None
    identifier = doi[len(prefix) :]
    if not identifier or re.fullmatch(r"[a-z0-9./-]+", identifier) is None:
        return None
    return identifier


def _arxiv_identity(value: str | None, kind: str) -> tuple[str, str] | None:
    if not isinstance(value, str):
        return None
    parts = urlsplit(value.strip())
    if parts.scheme not in {"http", "https"} or parts.netloc.casefold() != "arxiv.org":
        return None
    match = re.fullmatch(
        rf"/{kind}/(?P<id>.+?)(?P<version>v[1-9]\d*)(?:\.pdf)?", parts.path
    )
    if match is None or parts.query or parts.fragment:
        return None
    return match.group("id").casefold(), match.group("version")


def _arxiv_base_identity(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    parts = urlsplit(value.strip())
    if (
        parts.scheme not in {"http", "https"}
        or parts.netloc.casefold() != "arxiv.org"
        or not parts.path.startswith("/abs/")
        or parts.query
        or parts.fragment
    ):
        return None
    identifier = parts.path.removeprefix("/abs/")
    return identifier.casefold() if identifier else None


def _explicit_arxiv_withdrawal(comment: str | None) -> bool:
    if not isinstance(comment, str):
        return False
    return (
        re.search(
            r"(?:^|\b)(?:this submission|the submission|this paper|the paper) "
            r"(?:has been|was|is) withdrawn\b|^\s*withdrawn\b",
            comment.casefold(),
        )
        is not None
    )


def _arxiv_version_outcome(
    vault_root, entry: dict, identifier: str, target: str, detection_date: str
) -> Outcome:
    local_version = _nonempty_version(entry.get("version"))
    if local_version is None:
        return _provider_skipped(target)
    if re.fullmatch(r"v[1-9]\d*", local_version) is None:
        return _provider_unreachable(target, "arXiv")
    status, text = webapi.get_text(
        "https://export.arxiv.org/api/query",
        vault_root,
        params={"id_list": identifier},
    )
    if status != 200 or not isinstance(text, str):
        return _provider_unreachable(target, "arXiv")
    # defusedxml is lazy-imported here (spec §8 dependency discipline): the gate path
    # never parses XML, so core startup is unchanged. Its hardened parser is
    # byte-equivalent on well-formed input and still raises the stdlib ParseError on
    # malformed input; entity/DTD/external-reference attacks raise DefusedXmlException
    # (a ValueError, NOT a ParseError), which maps to the same UNREACHABLE outcome.
    from defusedxml.common import DefusedXmlException
    from defusedxml.ElementTree import ParseError, fromstring

    try:
        root = fromstring(text)
    except (ParseError, DefusedXmlException):
        return _provider_unreachable(target, "arXiv")
    atom = "{http://www.w3.org/2005/Atom}"
    arxiv = "{http://arxiv.org/schemas/atom}"
    entries = root.findall(f"{atom}entry")
    if len(entries) != 1:
        return _provider_unreachable(target, "arXiv")
    remote = entries[0]
    base_identity = _arxiv_base_identity(remote.findtext(f"{atom}id"))
    if base_identity != identifier.casefold():
        return _provider_unreachable(target, "arXiv")
    alternate_identities = [
        _arxiv_identity(link.get("href"), "abs")
        for link in remote.findall(f"{atom}link")
        if link.get("rel") == "alternate" and link.get("type") == "text/html"
    ]
    if len(alternate_identities) != 1 or alternate_identities[0] is None:
        return _provider_unreachable(target, "arXiv")
    identity = alternate_identities[0]
    if identity[0] != identifier.casefold():
        return _provider_unreachable(target, "arXiv")
    remote_version = identity[1]
    comment = remote.findtext(f"{arxiv}comment")
    withdrawn = _explicit_arxiv_withdrawal(comment)
    pdf_identities = [
        _arxiv_identity(link.get("href"), "pdf")
        for link in remote.findall(f"{atom}link")
        if link.get("rel") == "related" and link.get("type") == "application/pdf"
    ]
    if withdrawn and not pdf_identities:
        return _blocking_outcome(
            target,
            {"type": "withdrawal", "notice_date": None},
            detection_date,
        )
    if withdrawn:
        return _provider_unreachable(target, "arXiv")
    if pdf_identities != [(identifier.casefold(), remote_version)]:
        return _provider_unreachable(target, "arXiv")
    if remote_version != local_version:
        return _version_mismatch(target, "arXiv")
    return Outcome("update-notice", target, Result.MATCHED, "matched")


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
            warns = _merge_warn_notices(warns)
            if active is not None:
                return _blocking_outcome(target, active, detection_date, warns)
            return Outcome(
                "update-notice",
                target,
                Result.MATCHED,
                "matched",
                extra={"warn_notices": warns} if warns else {},
            )

        if agency.casefold() != "datacite":
            return _provider_unreachable(target, "provider")
        arxiv_identifier = _arxiv_identifier(doi)

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
        if arxiv_identifier is not None:
            return _arxiv_version_outcome(
                vault_root, entry, arxiv_identifier, target, detection_date
            )
        return _datacite_version_outcome(vault_root, entry, doi, target)
    except webapi.ApiError:
        return Outcome(
            "update-notice",
            target,
            Result.UNREACHABLE,
            "outage — update-notice service unavailable",
        )


# Retraction Watch's production export ships these US-style date shapes
# alongside ISO.
_RW_DATE_FORMATS = ("%m/%d/%Y %H:%M", "%m/%d/%Y")


def _rw_date(value) -> str | object | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if not isinstance(value, str):
        return _INVALID
    text = value.strip()
    try:
        return _date.fromisoformat(text).isoformat()
    except ValueError:
        pass
    for fmt in _RW_DATE_FORMATS:
        try:
            # Calendar date only; no tzinfo applies to a bare RW export date.
            return _datetime.strptime(text, fmt).date().isoformat()  # noqa: DTZ007
        except ValueError:
            continue
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
    warns = _merge_warn_notices(warns)
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
    if len(outcomes) == 2 and (
        outcomes[0].target != outcomes[1].target
        or outcomes[0].target_kind != outcomes[1].target_kind
    ):
        record = outcome_to_record(outcomes[0])
        record["result"] = Result.UNREACHABLE.value
        record["reason"] = "outage — update-notice target mismatch"
        record["extra"] = {}
        record["path_extra_fields"] = []
        return outcome_from_record(record)
    warnings = _merge_warn_notices(
        *(outcome.extra.get("warn_notices", []) for outcome in outcomes)
    )
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
                for result in (
                    Result.UNREACHABLE,
                    Result.UNMATCHED,
                    Result.MATCHED,
                    Result.SKIPPED,
                )
                for outcome in outcomes
                if outcome.result is result
            ),
            outcomes[0],
        )
    record = outcome_to_record(chosen)
    extra = record["extra"]
    if not isinstance(extra, dict):  # outcome_to_record always detaches extra to a dict
        raise TypeError("Outcome record extra must be an object")
    if warnings:
        extra["warn_notices"] = warnings
    else:
        extra.pop("warn_notices", None)
    return outcome_from_record(record)
