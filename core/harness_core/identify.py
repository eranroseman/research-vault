"""Identifier discovery before an automatic SKIPPED result becomes final."""

from . import Result, webapi
from .checks import Outcome, metadata_year, normalize_text


def _target(entry: dict) -> str:
    value = entry.get("id") if isinstance(entry, dict) else None
    return value if isinstance(value, str) and value else "?"


def _missing_doi(entry: dict) -> bool:
    for key in ("DOI", "doi"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return False
    return True


def _title(entry: dict) -> str | None:
    value = entry.get("title") if isinstance(entry, dict) else None
    if not isinstance(value, str) or not value.strip():
        return None
    return value


def _query_terms(entry: dict, title: str) -> str:
    family = ""
    authors = entry.get("author")
    if isinstance(authors, list) and authors and isinstance(authors[0], dict):
        candidate = authors[0].get("family")
        if isinstance(candidate, str) and candidate.strip():
            family = candidate

    _, issued_year = metadata_year(entry.get("issued"))
    year = str(issued_year) if issued_year is not None else ""
    return " ".join(part for part in (title, family, year) if part)


def _crossref_doi(vault_root, entry: dict, title: str) -> tuple[str | None, bool]:
    """Return (DOI, provider_failed) from a strictly validated Crossref response."""
    try:
        status, data = webapi.get_json(
            "https://api.crossref.org/works",
            vault_root,
            params={"query.bibliographic": _query_terms(entry, title), "rows": 2},
        )
    except webapi.ApiError:
        return None, True

    if status != 200 or not isinstance(data, dict):
        return None, True
    message = data.get("message")
    if not isinstance(message, dict):
        return None, True
    items = message.get("items")
    if not isinstance(items, list):
        return None, True
    if not items:
        return None, False

    top = items[0]
    if not isinstance(top, dict):
        return None, True
    titles = top.get("title")
    doi = top.get("DOI")
    if (
        not isinstance(titles, list)
        or not titles
        or not isinstance(titles[0], str)
        or not isinstance(doi, str)
        or not doi.strip()
    ):
        return None, True
    if normalize_text(titles[0]).casefold() != normalize_text(title).casefold():
        return None, False
    return doi.strip(), False


def _pubmed_pmid(vault_root, title: str) -> tuple[str | None, bool]:
    """Return (PMID, provider_failed) from a strictly validated ESearch response."""
    try:
        status, data = webapi.get_json(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            vault_root,
            params={"db": "pubmed", "term": f"{title}[Title]", "retmode": "json"},
        )
    except webapi.ApiError:
        return None, True

    if status != 200 or not isinstance(data, dict):
        return None, True
    result = data.get("esearchresult")
    if not isinstance(result, dict):
        return None, True
    ids = result.get("idlist")
    if not isinstance(ids, list) or not all(isinstance(item, str) for item in ids):
        return None, True
    if len(ids) != 1:
        return None, False
    pmid = ids[0].strip()
    if not pmid or not pmid.isdecimal() or pmid == "0":
        return None, True
    return pmid, False


def discover(vault_root, entry: dict) -> Outcome:
    """Discover DOI/PMID safely, returning a four-state discovery outcome."""
    target = _target(entry)
    identifiers = {}
    extra = {"identifiers": identifiers}
    if not isinstance(entry, dict) or not _missing_doi(entry):
        return Outcome(
            "identifier-discovery",
            target,
            Result.SKIPPED,
            "no-identifier — discovery not needed",
            extra,
        )

    title = _title(entry)
    if title is None:
        return Outcome(
            "identifier-discovery",
            target,
            Result.SKIPPED,
            "no-identifier — title unavailable for discovery",
            extra,
        )

    doi, crossref_failed = _crossref_doi(vault_root, entry, title)
    if doi is not None:
        identifiers["DOI"] = doi
    pmid, pubmed_failed = _pubmed_pmid(vault_root, title)
    if pmid is not None:
        identifiers["PMID"] = pmid

    if crossref_failed or pubmed_failed:
        return Outcome(
            "identifier-discovery",
            target,
            Result.UNREACHABLE,
            "outage — identifier discovery unavailable",
            extra,
        )
    if identifiers:
        return Outcome("identifier-discovery", target, Result.MATCHED, "matched", extra)
    return Outcome(
        "identifier-discovery",
        target,
        Result.SKIPPED,
        "no-identifier — discovery found nothing",
        extra,
    )
