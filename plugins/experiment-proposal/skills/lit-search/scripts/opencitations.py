#!/usr/bin/env python3
# Vendored from https://github.com/hutzelmann/thesis-proposal-skills @ a38b7b117513b9e4e50f08770d0049aae3e75398
# (skills/proposal-lit-search/scripts/opencitations.py), license MIT (© 2026 Thomas Hutzelmann).
# Renamed into the experiment-proposal plugin as skills/lit-search/scripts/opencitations.py.
# Do not hand-edit this file; re-vendor from upstream to update it.
"""OpenCitations Index client — citation-graph edges only, no text search.

API base URL: https://api.opencitations.net/index/v2
(Use api.opencitations.net directly; the old opencitations.net/index/api/v2
URLs merely redirect here.)

Key policy: no key required. An optional access token from the environment
variable OPENCITATIONS_TOKEN is sent as the ``authorization`` header when
present (OpenCitations asks heavy users to register for one).

Graph-ONLY source: exposes ``references(doi)`` and ``citations(doi)`` but no
``search()``. The Index knows only identifiers, not metadata, so entries are
minimal: ``{"DOI": <doi>, "_source": "opencitations"}``. Callers MUST enrich
these DOIs via crossref/openalex to obtain titles, authors, and years.
Rows whose id list carries no ``doi:`` token are skipped. A 404 for a DOI
means "unknown to the index" and yields ``[]``, not an error.
"""

from __future__ import annotations

import os
import urllib.parse

import common

API_BASE = "https://api.opencitations.net/index/v2"
MIN_INTERVAL = 0.5


def _headers() -> dict[str, str]:
    token = os.environ.get("OPENCITATIONS_TOKEN")
    return {"authorization": token} if token else {}


def _doi_from_ids(ids: str) -> str | None:
    """Extract the doi from a space-separated id list like
    'omid:br/06123 doi:10.1145/123 openalex:W123'."""
    for token in ids.split():
        if token.lower().startswith("doi:"):
            return common.clean_doi(token[4:])
    return None


def _edges(endpoint: str, doi: str, field: str, limit: int) -> list[dict]:
    cleaned = common.clean_doi(doi)
    if not cleaned:
        raise common.SourceError("opencitations: empty or malformed DOI")
    url = f"{API_BASE}/{endpoint}/doi:{urllib.parse.quote(cleaned, safe='/:')}"
    try:
        rows = common.http_json(url, headers=_headers(),
                                source="opencitations", min_interval=MIN_INTERVAL)
    except common.SourceError as exc:
        if "HTTP 404" in str(exc):
            return []  # DOI unknown to the index — empty result, not an outage
        raise
    results: list[dict] = []
    seen: set[str] = set()
    for row in rows:
        edge_doi = _doi_from_ids(row.get(field, ""))
        if not edge_doi or edge_doi in seen:
            continue
        seen.add(edge_doi)
        results.append({"DOI": edge_doi, "_source": "opencitations"})
        if len(results) >= limit:
            break
    return results


def references(doi: str, limit: int = 30) -> list[dict]:
    """DOIs of works that `doi` cites (outgoing edges; 'cited' field)."""
    return _edges("references", doi, "cited", limit)


def citations(doi: str, limit: int = 30) -> list[dict]:
    """DOIs of works that cite `doi` (incoming edges; 'citing' field)."""
    return _edges("citations", doi, "citing", limit)
