"""Citation checkers (spec §6). Shared Outcome dataclass; four-state everywhere."""

import csv
import json
import math
import os
import re
import unicodedata
import xml.etree.ElementTree as ElementTree
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date as _Date
from pathlib import Path
from types import MappingProxyType
from typing import Literal
from urllib.parse import quote, urlsplit

from . import Result, bibliography, claims, inbox, webapi
from .pathcodec import RepoPathValue, decode_repo_path, encode_repo_path

_RECORD_FIELDS = {
    "check",
    "target",
    "target_kind",
    "result",
    "reason",
    "extra",
    "path_extra_fields",
}
_CSV_FIELDS = (
    "check",
    "target",
    "target_kind",
    "result",
    "reason",
    "extra",
    "path_extra_fields",
)


def _freeze_json(value, active: set[int]):
    if value is None or type(value) in {str, bool, int}:
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("Outcome extras require finite JSON numbers")
        return value
    if isinstance(value, RepoPathValue):
        raise TypeError("RepoPathValue is valid only as a direct extra value")
    if isinstance(value, (bytes, bytearray, memoryview, set, frozenset)):
        raise TypeError("Outcome extras must be a JSON-shaped graph")
    if isinstance(value, Mapping):
        identity = id(value)
        if identity in active:
            raise ValueError("Outcome extra graph contains a cycle")
        active.add(identity)
        try:
            result = {}
            for key, item in value.items():
                if type(key) is not str:
                    raise TypeError("Outcome extra mapping keys must be strings")
                result[key] = _freeze_json(item, active)
            return MappingProxyType(result)
        finally:
            active.remove(identity)
    if isinstance(value, (list, tuple)):
        identity = id(value)
        if identity in active:
            raise ValueError("Outcome extra graph contains a cycle")
        active.add(identity)
        try:
            return tuple(_freeze_json(item, active) for item in value)
        finally:
            active.remove(identity)
    raise TypeError(f"unsupported Outcome extra value: {type(value).__name__}")


def _thaw_json(value):
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


@dataclass(frozen=True)
class Outcome:
    check: str
    target: str | RepoPathValue
    result: Result
    reason: str
    extra: Mapping[str, object] = field(default_factory=dict)
    target_kind: Literal["identifier", "repo-path"] = field(init=False)
    path_extra_fields: tuple[str, ...] = field(init=False)
    __hash__ = None

    def __post_init__(self):
        if type(self.check) is not str or not self.check:
            raise TypeError("Outcome check must be a nonempty string")
        if not isinstance(self.result, Result):
            raise TypeError("Outcome result must be a Result")
        if type(self.target) is str:
            target = self.target
            target_kind = "identifier"
        elif isinstance(self.target, RepoPathValue):
            target = encode_repo_path(self.target.raw)
            target_kind = "repo-path"
        else:
            raise TypeError("Outcome target must be an identifier or RepoPathValue")
        if not target or any(character in target for character in "\r\n\0"):
            raise ValueError("Outcome target must be nonempty single-line text")
        if not isinstance(self.extra, Mapping):
            raise TypeError("Outcome extra must be a mapping")
        direct = {}
        path_fields = []
        for key, value in self.extra.items():
            if type(key) is not str:
                raise TypeError("Outcome extra mapping keys must be strings")
            if isinstance(value, RepoPathValue):
                direct[key] = encode_repo_path(value.raw)
                path_fields.append(key)
            else:
                direct[key] = value
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "target_kind", target_kind)
        object.__setattr__(self, "path_extra_fields", tuple(sorted(path_fields)))
        object.__setattr__(self, "reason", inbox.validate_reason(self.reason))
        object.__setattr__(self, "extra", _freeze_json(direct, set()))


def outcome_to_record(outcome: Outcome) -> dict[str, object]:
    """Return one detached JSON record after revalidating typed path metadata."""
    if not isinstance(outcome, Outcome):
        raise TypeError("expected Outcome")
    if outcome.target_kind == "repo-path":
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
        "extra": _thaw_json(outcome.extra),
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
    mutable_extra = _thaw_json(_freeze_json(extra, set()))
    for field_name in path_fields:
        if (
            field_name not in mutable_extra
            or type(mutable_extra[field_name]) is not str
        ):
            raise ValueError("Outcome path extra metadata does not name a string")
        mutable_extra[field_name] = RepoPathValue(
            decode_repo_path(mutable_extra[field_name])
        )
    typed_target: str | RepoPathValue = target
    if kind == "repo-path":
        typed_target = RepoPathValue(decode_repo_path(target))
    outcome = Outcome(check, typed_target, result_value, reason, mutable_extra)
    if (
        outcome.target_kind != kind
        or list(outcome.path_extra_fields) != path_fields
        or outcome.target != target
    ):
        raise ValueError("Outcome record path metadata is incoherent")
    return outcome


def outcome_to_csv_row(outcome: Outcome) -> dict[str, str]:
    record = outcome_to_record(outcome)
    return {
        "check": record["check"],
        "target": record["target"],
        "target_kind": record["target_kind"],
        "result": record["result"],
        "reason": record["reason"],
        "extra": json.dumps(record["extra"], sort_keys=True, separators=(",", ":")),
        "path_extra_fields": json.dumps(
            record["path_extra_fields"], separators=(",", ":")
        ),
    }


def outcome_from_csv_row(row: Mapping[str, str]) -> Outcome:
    if (
        not isinstance(row, Mapping)
        or set(row) != set(_CSV_FIELDS)
        or any(type(value) is not str for value in row.values())
    ):
        raise ValueError("Outcome CSV row has invalid columns")
    try:
        extra = json.loads(row["extra"])
        path_fields = json.loads(row["path_extra_fields"])
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError("Outcome CSV JSON columns are invalid") from error
    return outcome_from_record(
        {
            "check": row["check"],
            "target": row["target"],
            "target_kind": row["target_kind"],
            "result": row["result"],
            "reason": row["reason"],
            "extra": extra,
            "path_extra_fields": path_fields,
        }
    )


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


def check_citekeys(
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
                "citekey",
                RepoPathValue(relative_raw),
                Result.SKIPPED,
                "no-identifier — note cites nothing",
            )
        ]

    if bibliography_universe is None:
        bibliography_universe = bibliography.load(vault)
    origins = _claim_origins(note_text)
    typed_note_path = RepoPathValue(relative_raw)
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
                extra={"note_path": typed_note_path, "claims": origins[citekey]},
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
    remote_year_ok, remote_year = metadata_year(remote.get("issued"))
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
    local_year_ok, local_year = metadata_year(entry.get("issued"))
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
        return _provider_unreachable(target, "DataCite")
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
    if local_version is None or re.fullmatch(r"v[1-9]\d*", local_version) is None:
        return _provider_unreachable(target, "arXiv")
    status, text = webapi.get_text(
        "https://export.arxiv.org/api/query",
        vault_root,
        params={"id_list": identifier},
    )
    if status != 200 or not isinstance(text, str):
        return _provider_unreachable(target, "arXiv")
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError:
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
        if agency.casefold() == "datacite":
            return _datacite_version_outcome(vault_root, entry, doi, target)
        return _provider_unreachable(target, "provider")
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
                for result in (Result.UNREACHABLE, Result.MATCHED, Result.SKIPPED)
                for outcome in outcomes
                if outcome.result is result
            ),
            outcomes[0],
        )
    record = outcome_to_record(chosen)
    extra = record["extra"]
    if warnings:
        extra["warn_notices"] = warnings
    else:
        extra.pop("warn_notices", None)
    return outcome_from_record(record)
