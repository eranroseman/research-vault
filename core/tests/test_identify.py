"""Tests for safe external identifier discovery."""

import pytest

from harness_core import Result, checks, identify, webapi


def _fake_get(monkeypatch, table):
    def fake(url, vault_root, params=None, headers=None, timeout=10.0):
        for fragment, response in table.items():
            if fragment in url:
                if isinstance(response, Exception):
                    raise response
                return response
        raise AssertionError(f"unexpected URL {url}")

    monkeypatch.setattr(webapi, "get_json", fake)


def _entry(**overrides):
    entry = {
        "id": "smith2020",
        "title": "Mortality  Decline",
        "author": [{"family": "Smith"}],
        "issued": {"date-parts": [[2020]]},
    }
    entry.update(overrides)
    return entry


def test_discover_matches_exact_casefolded_crossref_title_and_single_pmid(
    net_vault, monkeypatch
):
    _fake_get(
        monkeypatch,
        {
            "api.crossref.org/works": (
                200,
                {
                    "message": {
                        "items": [
                            {"DOI": "10.1000/found", "title": ["mortality decline"]},
                            {"DOI": "10.1000/other", "title": ["Something else"]},
                        ]
                    }
                },
            ),
            "esearch.fcgi": (200, {"esearchresult": {"idlist": ["11111"]}}),
        },
    )

    outcome = identify.discover(net_vault, _entry())

    assert outcome.result is Result.MATCHED
    assert outcome.extra == {"identifiers": {"DOI": "10.1000/found", "PMID": "11111"}}
    record = checks.outcome_to_record(outcome)
    assert record["extra"]["identifiers"] == {
        "DOI": "10.1000/found",
        "PMID": "11111",
    }
    record["extra"]["identifiers"]["DOI"] = "detached"
    assert outcome.extra["identifiers"]["DOI"] == "10.1000/found"


def test_discover_skips_when_both_healthy_providers_find_no_identifier(
    net_vault, monkeypatch
):
    _fake_get(
        monkeypatch,
        {
            "api.crossref.org/works": (
                200,
                {"message": {"items": [{"DOI": "10.1000/wrong", "title": ["Other"]}]}},
            ),
            "esearch.fcgi": (200, {"esearchresult": {"idlist": []}}),
        },
    )

    outcome = identify.discover(net_vault, _entry())

    assert outcome.result is Result.SKIPPED
    assert outcome.extra == {"identifiers": {}}


@pytest.mark.parametrize(
    "response",
    [
        webapi.ApiError("down"),
        (503, {"message": {"items": []}}),
        (200, {"message": {"items": {}}}),
        (200, {"message": {"items": [{"DOI": "10.1000/x", "title": "bad"}]}}),
    ],
)
def test_discover_marks_crossref_outage_or_bad_response_unreachable(
    net_vault, monkeypatch, response
):
    _fake_get(
        monkeypatch,
        {
            "api.crossref.org/works": response,
            "esearch.fcgi": (200, {"esearchresult": {"idlist": []}}),
        },
    )

    outcome = identify.discover(net_vault, _entry())

    assert outcome.result is Result.UNREACHABLE
    assert outcome.extra == {"identifiers": {}}


@pytest.mark.parametrize(
    "response",
    [
        webapi.ApiError("down"),
        (500, {"esearchresult": {"idlist": []}}),
        (200, {"esearchresult": {"idlist": "11111"}}),
        (200, {"esearchresult": {"idlist": [11111]}}),
    ],
)
def test_discover_marks_pubmed_outage_or_bad_response_unreachable(
    net_vault, monkeypatch, response
):
    _fake_get(
        monkeypatch,
        {
            "api.crossref.org/works": (200, {"message": {"items": []}}),
            "esearch.fcgi": response,
        },
    )

    outcome = identify.discover(net_vault, _entry())

    assert outcome.result is Result.UNREACHABLE
    assert outcome.extra == {"identifiers": {}}


def test_discover_keeps_crossref_identifier_when_pubmed_is_unreachable(
    net_vault, monkeypatch
):
    _fake_get(
        monkeypatch,
        {
            "api.crossref.org/works": (
                200,
                {
                    "message": {
                        "items": [
                            {"DOI": "10.1000/found", "title": ["MORTALITY DECLINE"]}
                        ]
                    }
                },
            ),
            "esearch.fcgi": webapi.ApiError("down"),
        },
    )

    outcome = identify.discover(net_vault, _entry())

    assert outcome.result is Result.UNREACHABLE
    assert outcome.extra == {"identifiers": {"DOI": "10.1000/found"}}


def test_discover_keeps_pubmed_identifier_when_crossref_is_unreachable(
    net_vault, monkeypatch
):
    _fake_get(
        monkeypatch,
        {
            "api.crossref.org/works": webapi.ApiError("down"),
            "esearch.fcgi": (200, {"esearchresult": {"idlist": ["11111"]}}),
        },
    )

    outcome = identify.discover(net_vault, _entry())

    assert outcome.result is Result.UNREACHABLE
    assert outcome.extra == {"identifiers": {"PMID": "11111"}}


def test_discover_uses_the_documented_crossref_and_pubmed_query_parameters(
    net_vault, monkeypatch
):
    seen = {}

    def fake(url, vault_root, params=None, headers=None, timeout=10.0):
        seen[url] = params
        if "api.crossref.org/works" in url:
            return 200, {"message": {"items": []}}
        if "esearch.fcgi" in url:
            return 200, {"esearchresult": {"idlist": []}}
        raise AssertionError(f"unexpected URL {url}")

    monkeypatch.setattr(webapi, "get_json", fake)

    identify.discover(net_vault, _entry())

    assert seen["https://api.crossref.org/works"] == {
        "query.bibliographic": "Mortality  Decline Smith 2020",
        "rows": 2,
    }
    assert seen["https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"] == {
        "db": "pubmed",
        "term": "Mortality  Decline[Title]",
        "retmode": "json",
    }


@pytest.mark.parametrize(
    "issued",
    [None, {"date-parts": "malformed"}, {"date-parts": [[True]]}],
)
def test_discover_omits_an_absent_or_malformed_issued_year_without_failing(
    net_vault, monkeypatch, issued
):
    crossref_queries = []

    def fake(url, vault_root, params=None, headers=None, timeout=10.0):
        if "api.crossref.org/works" in url:
            crossref_queries.append(params["query.bibliographic"])
            return 200, {"message": {"items": []}}
        if "esearch.fcgi" in url:
            return 200, {"esearchresult": {"idlist": []}}
        raise AssertionError(f"unexpected URL {url}")

    monkeypatch.setattr(webapi, "get_json", fake)

    outcome = identify.discover(
        net_vault,
        _entry(issued=issued),
    )

    assert outcome.result is Result.SKIPPED
    assert outcome.extra == {"identifiers": {}}
    assert crossref_queries == ["Mortality  Decline Smith"]


def test_discover_does_not_query_an_entry_that_already_has_a_doi(
    net_vault, monkeypatch
):
    def fail(*args, **kwargs):
        raise AssertionError("existing DOI must not be rediscovered")

    monkeypatch.setattr(webapi, "get_json", fail)

    outcome = identify.discover(net_vault, _entry(DOI="10.1000/already"))

    assert outcome.result is Result.SKIPPED
    assert outcome.extra == {"identifiers": {}}
