import pytest

from harness_core import Result, checks, webapi


def test_citekey_check_matches_and_reports_missing_bibliography_entries(fixture_vault):
    """A bibliography omission must make only its cited key unmatched."""
    outs = checks.check_citekeys(
        fixture_vault, fixture_vault / "projects" / "brief" / "draft.md"
    )

    by_target = {out.target: out for out in outs}

    assert by_target["smith2020"].result is Result.MATCHED
    assert by_target["fabricated2020"].result is Result.UNMATCHED
    reason = by_target["fabricated2020"].reason
    assert reason == "mismatch — citekey not in bibliography"


def test_citekey_check_skips_a_note_with_no_citations(fixture_vault):
    """A citation-free note must not produce an empty or fabricated finding."""
    note = fixture_vault / "synthesis" / "index.md"

    outs = checks.check_citekeys(fixture_vault, note)

    assert len(outs) == 1
    assert outs[0].target == "synthesis/index.md"
    assert outs[0].result is Result.SKIPPED
    assert outs[0].reason == "no-identifier — note cites nothing"


def test_citekey_check_scans_citations_in_non_claim_prose(fixture_vault):
    """A checker restricted to parsed claims would miss prose citations."""
    note = fixture_vault / "synthesis" / "prose.md"
    note.write_text("See the background evidence [@prose-only2024].\n")

    outs = checks.check_citekeys(fixture_vault, note)

    assert len(outs) == 1
    assert outs[0].target == "prose-only2024"
    assert outs[0].result is Result.UNMATCHED
    assert outs[0].extra["note_path"] == "synthesis/prose.md"
    assert outs[0].extra["claims"] == []


def test_citekey_check_deduplicates_repeated_citations(fixture_vault):
    """Repeated citations to one key must stay one public outcome."""
    note = fixture_vault / "projects" / "brief" / "draft.md"
    note.write_text(
        note.read_text()
        + "\n- (inference) A second use [@smith2020, p. 13] ^c-88888888\n"
    )

    outs = checks.check_citekeys(fixture_vault, note)

    assert [out.target for out in outs] == ["fabricated2020", "smith2020"]
    smith = next(out for out in outs if out.target == "smith2020")
    assert smith.extra["claims"] == [
        {"claim_id": "c-66666666", "line_no": 7, "locator": "p. 12"},
        {"claim_id": "c-88888888", "line_no": 11, "locator": "p. 13"},
    ]


def test_citekey_outcome_carries_claim_line_origins(fixture_vault):
    """Later marker stamping needs the exact checked note and claim line."""
    note = fixture_vault / "projects" / "brief" / "draft.md"

    outs = checks.check_citekeys(fixture_vault, note)

    smith = next(out for out in outs if out.target == "smith2020")
    assert smith.extra == {
        "note_path": "projects/brief/draft.md",
        "claims": [{"claim_id": "c-66666666", "line_no": 7, "locator": "p. 12"}],
    }


def test_outcome_rejects_invalid_or_empty_reasons_and_has_fresh_extra_dicts():
    """Invalid reasons and shared metadata could corrupt every later check."""
    first = checks.Outcome("citekey", "smith2020", Result.MATCHED, "matched")
    second = checks.Outcome("citekey", "gone2019", Result.MATCHED, "matched")
    first.extra["origin"] = "one"

    with pytest.raises(ValueError, match="reason"):
        checks.Outcome("citekey", "bad", Result.MATCHED, "")
    with pytest.raises(ValueError, match="reason"):
        checks.Outcome("citekey", "bad", Result.MATCHED, "invalid reason")
    with pytest.raises(TypeError):
        checks.Outcome("citekey", "bad", Result.MATCHED)

    assert second.extra == {}


def _fake_get(monkeypatch, table):
    """Install deterministic external responses keyed by a URL fragment."""

    def fake(url, vault_root, params=None, headers=None, timeout=10.0):
        for fragment, response in table.items():
            if fragment in url:
                if isinstance(response, Exception):
                    raise response
                return response
        raise AssertionError(f"unexpected URL {url}")

    monkeypatch.setattr(webapi, "get_json", fake)


def test_doi_exists_matches_a_confirmed_handle_and_keeps_its_doi(
    net_vault, monkeypatch
):
    """A response-code success must remain a MATCHED DOI outcome."""
    _fake_get(
        monkeypatch,
        {"doi.org/api/handles/10.1000/xyz": (200, {"responseCode": 1})},
    )

    outcome = checks.check_doi_exists(net_vault, "10.1000/xyz")

    assert outcome.result is Result.MATCHED
    assert outcome.extra == {"doi": "10.1000/xyz"}


def test_doi_exists_uses_an_optional_citekey_as_the_note_target(net_vault, monkeypatch):
    """Orchestration may file note-level DOI findings against a citekey."""
    _fake_get(
        monkeypatch,
        {"doi.org/api/handles/10.1000/xyz": (200, {"responseCode": 1})},
    )

    outcome = checks.check_doi_exists(net_vault, "10.1000/xyz", "smith2020")

    assert outcome.target == "smith2020"
    assert outcome.extra == {"doi": "10.1000/xyz"}


@pytest.mark.parametrize(
    ("response", "doi"),
    [
        ((200, {"responseCode": 100}), "10.1/fake"),
        ((404, None), "10.1/not-found"),
    ],
)
def test_doi_exists_marks_only_explicit_not_found_responses_unmatched(
    net_vault, monkeypatch, response, doi
):
    """A handle's explicit no-match states must not be mistaken for outages."""
    _fake_get(monkeypatch, {"doi.org/api/handles/": response})

    outcome = checks.check_doi_exists(net_vault, doi)

    assert outcome.result is Result.UNMATCHED
    assert outcome.reason == "mismatch — DOI does not resolve"


@pytest.mark.parametrize(
    "response", [(500, {"responseCode": 1}), (503, {"responseCode": 100})]
)
def test_doi_exists_rejects_handle_codes_from_non_ok_statuses(
    net_vault, monkeypatch, response
):
    """Only a successful handle response may carry DOI existence semantics."""
    _fake_get(monkeypatch, {"doi.org/api/handles/": response})

    outcome = checks.check_doi_exists(net_vault, "10.1000/xyz")

    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason.startswith("outage")


def test_doi_exists_marks_api_outages_unreachable(net_vault, monkeypatch):
    """Transport errors must not turn into fabricated-DOI findings."""
    _fake_get(monkeypatch, {"doi.org/api/handles/": webapi.ApiError("down")})

    outcome = checks.check_doi_exists(net_vault, "10.1000/xyz")

    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason.startswith("outage")


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {"responseCode": "1"},
        {"responseCode": True},
        {"responseCode": 2},
    ],
)
def test_doi_exists_fails_closed_on_unexpected_handle_json(
    net_vault, monkeypatch, payload
):
    """Only numeric handle codes 1 and 100 carry DOI existence semantics."""
    _fake_get(monkeypatch, {"doi.org/api/handles/": (200, payload)})

    outcome = checks.check_doi_exists(net_vault, "10.1000/xyz")

    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason.startswith("outage")


def test_registry_agency_returns_a_nonempty_ra_from_documented_shape(
    net_vault, monkeypatch
):
    """A complete doiRA record selects its registration agency."""
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.5281/zenodo.1": (
                200,
                [{"DOI": "10.5281/zenodo.1", "RA": "DataCite"}],
            )
        },
    )

    assert checks.registry_agency(net_vault, "10.5281/zenodo.1") == "DataCite"


@pytest.mark.parametrize(
    "response",
    [
        webapi.ApiError("down"),
        (404, None),
        (200, None),
        (200, {"RA": "Crossref"}),
        (200, ["Crossref"]),
        (200, [{}]),
        (200, [{"DOI": "10.1/x", "RA": ""}]),
        (200, [{"DOI": "10.1/x", "RA": 7}]),
        (200, [{"DOI": 7, "RA": "Crossref"}]),
        (200, [{"DOI": "", "RA": "Crossref"}]),
        (200, [{"DOI": "10.1/other", "RA": "Crossref"}]),
    ],
)
def test_registry_agency_returns_none_for_outages_or_malformed_records(
    net_vault, monkeypatch, response
):
    """An invalid route must never silently choose the non-Crossref fallback."""
    _fake_get(monkeypatch, {"doi.org/doiRA/": response})

    assert checks.registry_agency(net_vault, "10.1/x") is None


def test_registry_agency_matches_doi_case_insensitively_after_trimming(
    net_vault, monkeypatch
):
    """DOI spelling differences must not reject a genuinely matching RA record."""
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.5281/zenodo.1": (
                200,
                [{"DOI": " 10.5281/ZENODO.1 ", "RA": "DataCite"}],
            )
        },
    )

    assert checks.registry_agency(net_vault, "10.5281/zenodo.1") == "DataCite"


def test_doi_paths_encode_query_and_fragment_data_without_escaping_separator(
    net_vault, monkeypatch
):
    """Reserved DOI suffix characters are path data, while its slash stays structural."""
    seen = []

    def fake(url, vault_root, params=None, headers=None, timeout=10.0):
        seen.append(url)
        if "/api/handles/" in url:
            return 200, {"responseCode": 1}
        return 200, [{"DOI": "10.1000/a?b#c", "RA": "Crossref"}]

    monkeypatch.setattr(webapi, "get_json", fake)

    checks.check_doi_exists(net_vault, "10.1000/a?b#c")
    checks.registry_agency(net_vault, "10.1000/a?b#c")

    assert seen == [
        "https://doi.org/api/handles/10.1000/a%3Fb%23c",
        "https://doi.org/doiRA/10.1000/a%3Fb%23c",
    ]


CROSSREF_METADATA = {
    "message": {
        "title": ["Mortality  decline"],
        "author": [{"family": "Smith", "given": "Jo"}],
        "issued": {"date-parts": [[2020]]},
    }
}


def _metadata_entry(**overrides):
    entry = {
        "id": "smith2020",
        "DOI": "10.1000/xyz",
        "title": "Mortality decline",
        "author": [{"family": "Smith", "given": "Jo"}],
        "issued": {"date-parts": [[2020]]},
    }
    entry.update(overrides)
    return entry


def _crossref_route(monkeypatch, remote=CROSSREF_METADATA):
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.1000/xyz": (
                200,
                [{"DOI": "10.1000/xyz", "RA": "Crossref"}],
            ),
            "api.crossref.org/works/10.1000/xyz": (200, remote),
        },
    )


def test_metadata_matches_case_insensitively_and_carries_note_target(
    net_vault, monkeypatch
):
    """Metadata compares case-insensitively but files against the CSL citekey."""
    _crossref_route(
        monkeypatch,
        {
            "message": {
                "title": ["MORTALITY DECLINE"],
                "author": [{"family": "SMITH", "given": "Josephine"}],
                "issued": {"date-parts": [[2020]]},
            }
        },
    )

    outcome = checks.check_metadata(
        net_vault, _metadata_entry(author=[{"family": "Smith", "given": "J."}])
    )

    assert outcome.result is Result.MATCHED
    assert outcome.target == "smith2020"
    assert outcome.extra == {"doi": "10.1000/xyz", "agency": "Crossref"}


def test_normalize_text_keeps_case_but_normalizes_crlf_dehyphenation():
    """Quote normalization must not silently make a case-mutated quote exact."""
    assert (
        checks.normalize_text("Mortali-\r\n ty\u00ad  Decline") == "Mortali ty Decline"
    )
    assert checks.normalize_text("Case") != checks.normalize_text("case")


def test_metadata_reports_title_divergence(net_vault, monkeypatch):
    """A well-shaped registry record with another title is a mismatch, not an outage."""
    _crossref_route(
        monkeypatch,
        {
            "message": {
                "title": ["A completely different paper"],
                "author": [{"family": "Smith", "given": "Jo"}],
                "issued": {"date-parts": [[2020]]},
            }
        },
    )

    outcome = checks.check_metadata(net_vault, _metadata_entry())

    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith("mismatch — title")


def test_metadata_reports_author_family_and_given_initial_divergence(
    net_vault, monkeypatch
):
    """Ordered families and conflicting first initials are independently compared."""
    _crossref_route(
        monkeypatch,
        {
            "message": {
                "title": ["Mortality decline"],
                "author": [
                    {"family": "Jones", "given": "Jo"},
                    {"family": "Smith", "given": "Ava"},
                ],
            }
        },
    )
    family = checks.check_metadata(
        net_vault,
        _metadata_entry(
            author=[
                {"family": "Smith", "given": "Jo"},
                {"family": "Jones", "given": "Ava"},
            ]
        ),
    )

    assert family.result is Result.UNMATCHED
    assert family.reason.startswith("mismatch — author family")

    _crossref_route(
        monkeypatch,
        {
            "message": {
                "title": ["Mortality decline"],
                "author": [{"family": "Smith", "given": "Anne"}],
            }
        },
    )
    initial = checks.check_metadata(net_vault, _metadata_entry())

    assert initial.result is Result.UNMATCHED
    assert initial.reason.startswith("mismatch — author given-name")


def test_metadata_compares_year_only_when_both_records_have_one(net_vault, monkeypatch):
    """An absent optional remote year is not a mismatch, but conflicting years are."""
    _crossref_route(
        monkeypatch,
        {
            "message": {
                "title": ["Mortality decline"],
                "author": [{"family": "Smith", "given": "Jo"}],
            }
        },
    )
    assert checks.check_metadata(net_vault, _metadata_entry()).result is Result.MATCHED

    _crossref_route(
        monkeypatch,
        {
            "message": {
                "title": ["Mortality decline"],
                "author": [{"family": "Smith", "given": "Jo"}],
                "issued": {"date-parts": [[2019]]},
            }
        },
    )
    outcome = checks.check_metadata(net_vault, _metadata_entry())

    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith("mismatch — year")


def test_metadata_uses_csl_content_negotiation_for_non_crossref_agencies(
    net_vault, monkeypatch
):
    """Any concrete non-Crossref agency uses the DOI CSL endpoint."""
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.5281/z.1": (
                200,
                [{"DOI": "10.5281/z.1", "RA": "DataCite"}],
            ),
            "doi.org/10.5281/z.1": (
                200,
                {"title": "Dataset of mortality", "author": [{"family": "Smith"}]},
            ),
        },
    )

    outcome = checks.check_metadata(
        net_vault,
        {
            "id": "smithdata",
            "DOI": "10.5281/z.1",
            "title": "Dataset of mortality",
            "author": [{"family": "Smith"}],
        },
    )

    assert outcome.result is Result.MATCHED
    assert outcome.extra == {"doi": "10.5281/z.1", "agency": "DataCite"}


def test_metadata_stops_when_registry_routing_is_unavailable(net_vault, monkeypatch):
    """An unknown route cannot silently use DOI content negotiation as a fallback."""
    monkeypatch.setattr(checks, "registry_agency", lambda vault, doi: None)
    _fake_get(monkeypatch, {"": AssertionError("metadata endpoint must not be called")})

    outcome = checks.check_metadata(net_vault, _metadata_entry())

    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason.startswith("outage — registry routing")
    assert outcome.extra == {"doi": "10.1000/xyz"}


@pytest.mark.parametrize(
    "remote",
    [
        None,
        {"message": []},
        {"message": {"title": "not-a-list", "author": []}},
        {"message": {"title": [], "author": []}},
        {"message": {"title": ["Mortality decline"], "author": [{}]}},
        {
            "message": {
                "title": ["Mortality decline"],
                "author": [],
                "issued": {"date-parts": "bad"},
            }
        },
    ],
)
def test_metadata_treats_malformed_crossref_shapes_as_unreachable(
    net_vault, monkeypatch, remote
):
    """Malformed nested Crossref JSON is an outage, never a false comparison."""
    _crossref_route(monkeypatch, remote)

    outcome = checks.check_metadata(net_vault, _metadata_entry())

    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason.startswith("outage")


@pytest.mark.parametrize(
    "status",
    [404, 500],
)
def test_metadata_rejects_non_ok_metadata_responses(net_vault, monkeypatch, status):
    """Only a 200 response may be interpreted as registry metadata."""
    _crossref_route(monkeypatch, CROSSREF_METADATA)

    def wrong_status(url, vault_root, params=None, headers=None, timeout=10.0):
        if "doiRA" in url:
            return 200, [{"DOI": "10.1000/xyz", "RA": "Crossref"}]
        return status, CROSSREF_METADATA

    monkeypatch.setattr(webapi, "get_json", wrong_status)
    outcome = checks.check_metadata(net_vault, _metadata_entry())

    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason.startswith("outage")


def test_metadata_treats_api_errors_as_unreachable(net_vault, monkeypatch):
    """A metadata transport failure cannot become a false metadata match."""
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.1000/xyz": (
                200,
                [{"DOI": "10.1000/xyz", "RA": "Crossref"}],
            ),
            "api.crossref.org/works/10.1000/xyz": webapi.ApiError("down"),
        },
    )

    outcome = checks.check_metadata(net_vault, _metadata_entry())

    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason.startswith("outage")
    assert outcome.extra == {"doi": "10.1000/xyz", "agency": "Crossref"}


def _notice_route(doi, agency="Crossref"):
    return (200, [{"DOI": doi, "RA": agency}])


def _works(updated_by):
    return 200, {"message": {"updated-by": updated_by}}


def test_update_notice_crossref_uses_encoded_works_path_and_keeps_warns(
    net_vault, monkeypatch
):
    """A blocking notice wins while every independent warning remains available."""
    seen = []

    def fake(url, vault_root, params=None, headers=None, timeout=10.0):
        seen.append(url)
        if "doiRA" in url:
            return _notice_route("10.1000/a?b#c")
        return _works(
            [
                {
                    "type": "Correction",
                    "updated": {"date-parts": [[2023, 1, 2]]},
                },
                {
                    "type": "Retraction",
                    "updated": {"date-parts": [[2024, 2, 3]]},
                },
                {
                    "type": "erratum",
                    "updated": {"date-parts": [[2023, 1, 2]]},
                },
            ]
        )

    monkeypatch.setattr(webapi, "get_json", fake)
    outcome = checks.check_update_notice(
        net_vault, {"id": "cite", "DOI": "10.1000/a?b#c"}, "2026-08-16"
    )

    assert seen == [
        "https://doi.org/doiRA/10.1000/a%3Fb%23c",
        "https://api.crossref.org/works/10.1000/a%3Fb%23c",
    ]
    assert outcome.result is Result.UNMATCHED
    assert outcome.target == "cite"
    assert outcome.reason == "retracted — retraction"
    assert outcome.extra == {
        "class": "blocking",
        "type": "retraction",
        "notice_date": "2024-02-03",
        "detection_date": "2026-08-16",
        "warn_notices": [
            {"type": "correction", "notice_date": "2023-01-02"},
            {"type": "erratum", "notice_date": "2023-01-02"},
        ],
    }


def test_update_notice_reinstatement_is_chronological_not_payload_order(
    net_vault, monkeypatch
):
    """A later blocking notice stays active even when the response is unordered."""
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.1000/chronology": _notice_route("10.1000/chronology"),
            "api.crossref.org/works/10.1000/chronology": _works(
                [
                    {
                        "type": "withdrawal",
                        "updated": {"date-parts": [[2024, 1, 1]]},
                    },
                    {
                        "type": "reinstatement",
                        "updated": {"date-parts": [[2023, 1, 1]]},
                    },
                    {
                        "type": "retraction",
                        "updated": {"date-parts": [[2020, 1, 1]]},
                    },
                    {
                        "type": "reinstatement",
                        "updated": {"date-parts": [[2021, 1, 1]]},
                    },
                ]
            ),
        },
    )

    outcome = checks.check_update_notice(
        net_vault, {"id": "cite", "DOI": "10.1000/chronology"}, "2026-08-16"
    )

    assert outcome.result is Result.UNMATCHED
    assert outcome.reason == "retracted — withdrawal"
    assert outcome.extra["notice_date"] == "2024-01-01"


def test_update_notice_unknown_blocking_date_never_auto_clears(net_vault, monkeypatch):
    """A reinstatement cannot silently clear a blocking notice with no known date."""
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.1000/unknown": _notice_route("10.1000/unknown"),
            "api.crossref.org/works/10.1000/unknown": _works(
                [
                    {"type": "retraction"},
                    {
                        "type": "reinstatement",
                        "updated": {"date-parts": [[2024, 1, 1]]},
                    },
                ]
            ),
        },
    )

    outcome = checks.check_update_notice(
        net_vault, {"id": "cite", "DOI": "10.1000/unknown"}, "2026-08-16"
    )

    assert outcome.result is Result.UNMATCHED
    assert outcome.extra["notice_date"] is None


def test_update_notice_stops_when_registry_routing_is_unavailable(
    net_vault, monkeypatch
):
    """An unknown agency is an outage, never permission to query OpenAlex."""
    monkeypatch.setattr(checks, "registry_agency", lambda vault, doi: None)
    _fake_get(monkeypatch, {"": AssertionError("remote notice API must not run")})

    outcome = checks.check_update_notice(
        net_vault, {"id": "cite", "DOI": "10.1000/no-route"}, "2026-08-16"
    )

    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason == "outage — registry routing unavailable"


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"message": []},
        {"message": {"updated-by": {}}},
        {"message": {"updated-by": ["not-an-object"]}},
        {"message": {"updated-by": [{"type": 7}]}},
        {
            "message": {
                "updated-by": [
                    {
                        "type": "retraction",
                        "updated": {"date-parts": [[True, 1, 1]]},
                    }
                ]
            }
        },
        {
            "message": {
                "updated-by": [{"type": "retraction", "updated": {"date-parts": []}}]
            }
        },
        {
            "message": {
                "updated-by": [{"type": "retraction", "updated": {"date-parts": [[]]}}]
            }
        },
    ],
)
def test_update_notice_rejects_malformed_crossref_json(net_vault, monkeypatch, payload):
    """Every required Crossref container/member is fail-closed."""
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.1000/bad": _notice_route("10.1000/bad"),
            "api.crossref.org/works/10.1000/bad": (200, payload),
        },
    )

    outcome = checks.check_update_notice(
        net_vault, {"id": "cite", "DOI": "10.1000/bad"}, "2026-08-16"
    )

    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason.startswith("outage")


@pytest.mark.parametrize("status", [404, 500])
def test_update_notice_rejects_non_ok_crossref_responses(
    net_vault, monkeypatch, status
):
    """Only a successful Crossref response has notice semantics."""
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.1000/status": _notice_route("10.1000/status"),
            "api.crossref.org/works/10.1000/status": (status, {"message": {}}),
        },
    )

    assert (
        checks.check_update_notice(
            net_vault, {"id": "cite", "DOI": "10.1000/status"}, "2026-08-16"
        ).result
        is Result.UNREACHABLE
    )


def test_update_notice_openalex_requires_a_boolean_and_encodes_identifier(
    net_vault, monkeypatch
):
    """A retracted OpenAlex record blocks before provider version status."""
    seen = []

    def fake(url, vault_root, params=None, headers=None, timeout=10.0):
        seen.append((url, params))
        if "doiRA" in url:
            return _notice_route("10.5281/a?b#c", "DataCite")
        return 200, {"is_retracted": True}

    monkeypatch.setattr(webapi, "get_json", fake)
    outcome = checks.check_update_notice(
        net_vault, {"id": "data", "DOI": "10.5281/a?b#c"}, "2026-08-16"
    )

    assert seen == [
        ("https://doi.org/doiRA/10.5281/a%3Fb%23c", None),
        (
            "https://api.openalex.org/works/https%3A%2F%2Fdoi.org%2F10.5281%2Fa%3Fb%23c",
            {"select": "is_retracted"},
        ),
    ]
    assert outcome.result is Result.UNMATCHED
    assert outcome.extra == {
        "class": "blocking",
        "type": "retraction",
        "notice_date": None,
        "detection_date": "2026-08-16",
    }


@pytest.mark.parametrize("value", ["false", 0, None, []])
def test_update_notice_openalex_rejects_non_boolean_retraction_values(
    net_vault, monkeypatch, value
):
    """OpenAlex's only accepted state is an actual JSON boolean."""
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.5281/openalex": _notice_route(
                "10.5281/openalex", "DataCite"
            ),
            "api.openalex.org/works/": (200, {"is_retracted": value}),
        },
    )

    outcome = checks.check_update_notice(
        net_vault, {"id": "data", "DOI": "10.5281/openalex"}, "2026-08-16"
    )

    assert outcome.result is Result.UNREACHABLE


def test_update_notice_datacite_requires_matching_provider_version(
    net_vault, monkeypatch
):
    seen = []

    def fake(url, vault_root, params=None, headers=None, timeout=10.0):
        seen.append((url, params))
        if "doiRA" in url:
            return _notice_route("10.5281/versioned", "DataCite")
        if "openalex" in url:
            return 200, {"is_retracted": False}
        if "api.datacite.org" in url:
            return 200, {
                "data": {
                    "id": "10.5281/versioned",
                    "type": "dois",
                    "attributes": {
                        "doi": "10.5281/versioned",
                        "version": "2",
                    },
                }
            }
        raise AssertionError(url)

    monkeypatch.setattr(webapi, "get_json", fake)

    outcome = checks.check_update_notice(
        net_vault,
        {"id": "data", "DOI": "10.5281/versioned", "version": "2"},
        "2026-08-16",
    )

    assert outcome.result is Result.MATCHED
    assert [url for url, _ in seen] == [
        "https://doi.org/doiRA/10.5281/versioned",
        "https://api.openalex.org/works/https%3A%2F%2Fdoi.org%2F10.5281%2Fversioned",
        "https://api.datacite.org/dois/10.5281/versioned",
    ]


@pytest.mark.parametrize(
    ("local_version", "payload", "expected"),
    [
        (None, {"data": {"attributes": {"version": "2"}}}, Result.UNREACHABLE),
        ("2", {"data": {"attributes": {}}}, Result.UNREACHABLE),
        ("2", {"data": {"attributes": {"version": ["2"]}}}, Result.UNREACHABLE),
        ("2", {"data": {"attributes": {"version": "3"}}}, Result.UNMATCHED),
    ],
    ids=["missing-local", "missing-remote", "ambiguous-remote", "mismatch"],
)
def test_update_notice_datacite_fails_closed_on_version_status(
    net_vault, monkeypatch, local_version, payload, expected
):
    payload["data"].setdefault("id", "10.5281/versioned")
    payload["data"].setdefault("type", "dois")
    payload["data"]["attributes"].setdefault("doi", "10.5281/versioned")
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.5281/versioned": _notice_route(
                "10.5281/versioned", "DataCite"
            ),
            "api.openalex.org/works/": (200, {"is_retracted": False}),
            "api.datacite.org/dois/": (200, payload),
        },
    )
    entry = {"id": "data", "DOI": "10.5281/versioned"}
    if local_version is not None:
        entry["version"] = local_version

    assert checks.check_update_notice(net_vault, entry, "2026-08-16").result is expected


ARXIV_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2401.12345</id>
    <published>2024-01-01T00:00:00Z</published>
    <updated>2024-02-01T00:00:00Z</updated>
    <link href="https://arxiv.org/abs/2401.12345v2" rel="alternate" type="text/html" />
    <link href="https://arxiv.org/pdf/2401.12345v2" rel="related" type="application/pdf" title="pdf" />
  </entry>
</feed>
"""
ARXIV_MULTI_FEED = ARXIV_FEED.replace(
    "</feed>",
    """  <entry>
    <id>http://arxiv.org/abs/2401.12345</id>
    <published>2024-01-01T00:00:00Z</published>
    <updated>2024-02-01T00:00:00Z</updated>
    <link href="https://arxiv.org/abs/2401.12345v2" rel="alternate" type="text/html" />
    <link href="https://arxiv.org/pdf/2401.12345v2" rel="related" type="application/pdf" title="pdf" />
  </entry>
</feed>""",
)


def test_update_notice_arxiv_establishes_latest_version_and_withdrawal_state(
    net_vault, monkeypatch
):
    seen = []

    def fake_json(url, vault_root, params=None, headers=None, timeout=10.0):
        if "doiRA" in url:
            return _notice_route("10.48550/arxiv.2401.12345", "DataCite")
        return 200, {"is_retracted": False}

    def fake_text(url, vault_root, params=None, headers=None, timeout=10.0):
        seen.append((url, params))
        return 200, ARXIV_FEED

    monkeypatch.setattr(webapi, "get_json", fake_json)
    monkeypatch.setattr(webapi, "get_text", fake_text)

    outcome = checks.check_update_notice(
        net_vault,
        {
            "id": "preprint",
            "DOI": "10.48550/arxiv.2401.12345",
            "URL": "https://arxiv.org/abs/2401.12345v2",
            "version": "v2",
        },
        "2026-08-16",
    )

    assert outcome.result is Result.MATCHED
    assert seen == [
        (
            "https://export.arxiv.org/api/query",
            {"id_list": "2401.12345"},
        )
    ]


def test_update_notice_arxiv_explicit_withdrawal_is_blocking(net_vault, monkeypatch):
    withdrawn = ARXIV_FEED.replace(
        '<link href="https://arxiv.org/pdf/2401.12345v2" rel="related" '
        'type="application/pdf" title="pdf" />',
        "<arxiv:comment>This submission has been withdrawn by the authors.</arxiv:comment>",
    )
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/": _notice_route("10.48550/arxiv.2401.12345", "DataCite"),
            "api.openalex.org/works/": (200, {"is_retracted": False}),
        },
    )
    monkeypatch.setattr(webapi, "get_text", lambda *_args, **_kwargs: (200, withdrawn))

    outcome = checks.check_update_notice(
        net_vault,
        {
            "id": "preprint",
            "DOI": "10.48550/arxiv.2401.12345",
            "URL": "https://arxiv.org/abs/2401.12345v2",
            "version": "v2",
        },
        "2026-08-16",
    )

    assert outcome.result is Result.UNMATCHED
    assert outcome.extra["class"] == "blocking"
    assert outcome.extra["type"] == "withdrawal"


@pytest.mark.parametrize(
    "feed",
    [
        ARXIV_MULTI_FEED,
        ARXIV_FEED.replace("2401.12345", "2401.99999", 1),
        ARXIV_FEED.replace("2401.12345v2", "2401.12345", 1),
        ARXIV_FEED.replace(
            '<link href="https://arxiv.org/pdf/2401.12345v2" rel="related" '
            'type="application/pdf" title="pdf" />',
            "",
        ),
        ARXIV_FEED.replace(
            "  </entry>",
            "    <arxiv:comment>This submission has been withdrawn.</arxiv:comment>\n"
            "  </entry>",
        ),
    ],
    ids=[
        "multiple-entries",
        "wrong-id",
        "unversioned-alternate",
        "missing-status-signal",
        "withdrawal-comment-with-live-pdf",
    ],
)
def test_update_notice_arxiv_malformed_or_ambiguous_status_is_unreachable(
    net_vault, monkeypatch, feed
):
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/": _notice_route("10.48550/arxiv.2401.12345", "DataCite"),
            "api.openalex.org/works/": (200, {"is_retracted": False}),
        },
    )
    monkeypatch.setattr(webapi, "get_text", lambda *_args, **_kwargs: (200, feed))
    outcome = checks.check_update_notice(
        net_vault,
        {
            "id": "preprint",
            "DOI": "10.48550/arxiv.2401.12345",
            "URL": "https://arxiv.org/abs/2401.12345v2",
            "version": "v2",
        },
        "2026-08-16",
    )

    assert outcome.result is Result.UNREACHABLE


@pytest.mark.parametrize(
    "payload",
    [
        {
            "data": {
                "id": "10.5281/versioned",
                "type": "works",
                "attributes": {"doi": "10.5281/versioned", "version": "2"},
            }
        },
        {
            "data": {
                "id": "10.5281/wrong",
                "type": "dois",
                "attributes": {"doi": "10.5281/versioned", "version": "2"},
            }
        },
        {
            "data": {
                "id": "10.5281/versioned",
                "type": "dois",
                "attributes": {"doi": "10.5281/wrong", "version": "2"},
            }
        },
    ],
    ids=["wrong-type", "wrong-id", "wrong-attributes-doi"],
)
def test_update_notice_datacite_binds_version_to_requested_doi(
    net_vault, monkeypatch, payload
):
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/": _notice_route("10.5281/versioned", "DataCite"),
            "api.openalex.org/works/": (200, {"is_retracted": False}),
            "api.datacite.org/dois/": (200, payload),
        },
    )

    outcome = checks.check_update_notice(
        net_vault,
        {"id": "data", "DOI": "10.5281/versioned", "version": "2"},
        "2026-08-16",
    )

    assert outcome.result is Result.UNREACHABLE


def test_update_notice_unknown_non_crossref_provider_is_unreachable(
    net_vault, monkeypatch
):
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.9999/other": _notice_route("10.9999/other", "mEDRA"),
        },
    )

    outcome = checks.check_update_notice(
        net_vault,
        {"id": "other", "DOI": "10.9999/other", "version": "1"},
        "2026-08-16",
    )

    assert outcome.result is Result.UNREACHABLE


def test_update_notice_rejects_arxiv_prefix_from_non_datacite_registry(
    net_vault, monkeypatch
):
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/": _notice_route("10.48550/arxiv.2401.12345", "mEDRA"),
        },
    )

    outcome = checks.check_update_notice(
        net_vault,
        {
            "id": "spoofed",
            "DOI": "10.48550/arxiv.2401.12345",
            "version": "v2",
        },
        "2026-08-16",
    )

    assert outcome.result is Result.UNREACHABLE


def test_update_notice_skips_only_when_both_identifiers_are_absent(net_vault):
    """PMID-only entries remain live-leg SKIPPED until the RW leg is reduced."""
    no_identifiers = checks.check_update_notice(net_vault, {"id": "none"}, "2026-08-16")
    pmid_only = checks.check_update_notice(
        net_vault, {"id": "pmid", "PMID": "12345"}, "2026-08-16"
    )

    assert no_identifiers.result is Result.SKIPPED
    assert pmid_only.result is Result.SKIPPED
    assert "RW batch" in pmid_only.reason


def test_rw_csv_matches_both_identifiers_and_blocking_beats_warning(tmp_path):
    """DOI and PMID hits are both considered instead of short-circuiting on DOI."""
    csv_file = tmp_path / "rw.csv"
    csv_file.write_text(
        "OriginalPaperDOI,OriginalPaperPubMedID,RetractionDate,RetractionNature\n"
        "https://doi.org/10.1000/doi-warn,111,2023-01-01,Expression of concern\n"
        ",111,2024-02-02,Retraction\n"
        "10.1000/bad-date,222,not-a-date,Retraction\n"
    )

    rw = checks.load_rw_csv(csv_file)
    outcome = checks.check_rw_batch(
        {"id": "cite", "DOI": "DOI:10.1000/DOI-WARN", "PMID": 111},
        rw,
        "2026-08-16",
    )

    assert outcome.result is Result.UNMATCHED
    assert outcome.reason == "retracted — retraction"
    assert outcome.extra == {
        "class": "blocking",
        "type": "retraction",
        "notice_date": "2024-02-02",
        "detection_date": "2026-08-16",
        "warn_notices": [
            {"type": "expression_of_concern", "notice_date": "2023-01-01"}
        ],
    }
    assert checks.check_rw_batch({"id": "bad", "PMID": "222"}, rw, "2026-08-16") is None


def test_reduce_update_notice_outcomes_applies_precedence_and_merges_warns():
    """The later orchestrator gets one target/outcome and every distinct warning."""
    live = checks.Outcome(
        "update-notice",
        "cite",
        Result.SKIPPED,
        "no-identifier — live leg needs a DOI; RW batch covers PMID",
        extra={"warn_notices": [{"type": "erratum", "notice_date": None}]},
    )
    rw = checks.Outcome(
        "update-notice",
        "cite",
        Result.MATCHED,
        "matched",
        extra={
            "warn_notices": [
                {"type": "correction", "notice_date": "2023-01-01"},
                {"type": "erratum", "notice_date": None},
            ]
        },
    )
    blocking = checks.Outcome(
        "update-notice",
        "cite",
        Result.UNMATCHED,
        "retracted — withdrawal",
        extra={
            "class": "blocking",
            "type": "withdrawal",
            "notice_date": "2024-01-01",
            "detection_date": "2026-08-16",
        },
    )
    outage = checks.Outcome(
        "update-notice", "cite", Result.UNREACHABLE, "outage — OpenAlex unavailable"
    )

    matched = checks.reduce_update_notice_outcomes(live, rw)
    unmatched = checks.reduce_update_notice_outcomes(outage, blocking)

    assert matched.result is Result.MATCHED
    assert matched.target == "cite"
    assert matched.extra["warn_notices"] == [
        {"type": "correction", "notice_date": "2023-01-01"},
        {"type": "erratum", "notice_date": None},
    ]
    assert unmatched.result is Result.UNMATCHED
    assert unmatched.reason == "retracted — withdrawal"


def test_merge_warn_notices_accepts_raw_groups_and_deduplicates_type_date():
    merged = checks._merge_warn_notices(
        [
            {"type": "correction", "notice_date": "2020-01-01"},
            {"type": "correction", "notice_date": "2020-01-01"},
        ],
        [
            {"type": "erratum", "notice_date": None},
            {"type": "retraction", "notice_date": "2020-01-02"},
            {"type": 7, "notice_date": "2020-01-03"},
        ],
    )

    assert merged == [
        {"type": "correction", "notice_date": "2020-01-01"},
        {"type": "erratum", "notice_date": None},
    ]


def test_reduce_update_notice_outcomes_fails_closed_on_target_mismatch():
    """A reducer must not attach one leg's outcome data to another target."""
    live = checks.Outcome(
        "update-notice", "live-target", Result.SKIPPED, "no-identifier — no DOI or PMID"
    )
    rw = checks.Outcome(
        "update-notice",
        "rw-target",
        Result.UNMATCHED,
        "retracted — retraction",
        extra={
            "class": "blocking",
            "type": "retraction",
            "notice_date": "2024-01-01",
            "detection_date": "2026-08-16",
            "warn_notices": [{"type": "erratum", "notice_date": "2023-01-01"}],
        },
    )

    outcome = checks.reduce_update_notice_outcomes(live, rw)

    assert outcome.result is Result.UNREACHABLE
    assert outcome.target == "live-target"
    assert outcome.reason == "outage — update-notice target mismatch"
    assert outcome.extra == {}


def test_reduce_update_notice_outcomes_keeps_the_winner_identity():
    """For matching legs, the chosen result, reason, extra, and target cohere."""
    live = checks.Outcome(
        "update-notice",
        "cite",
        Result.UNREACHABLE,
        "outage — update-notice service unavailable",
    )
    rw = checks.Outcome(
        "update-notice",
        "cite",
        Result.UNMATCHED,
        "retracted — withdrawal",
        extra={
            "class": "blocking",
            "type": "withdrawal",
            "notice_date": "2024-01-01",
            "detection_date": "2026-08-16",
        },
    )

    outcome = checks.reduce_update_notice_outcomes(live, rw)

    assert outcome.target == rw.target
    assert outcome.result is rw.result
    assert outcome.reason == rw.reason
    assert outcome.extra == rw.extra


def test_metadata_treats_malformed_csl_shape_as_unreachable(net_vault, monkeypatch):
    """Content-negotiated CSL must still provide typed title and author containers."""
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.5281/z.1": (
                200,
                [{"DOI": "10.5281/z.1", "RA": "DataCite"}],
            ),
            "doi.org/10.5281/z.1": (
                200,
                {"title": ["wrong CSL title type"], "author": "Smith"},
            ),
        },
    )

    outcome = checks.check_metadata(
        net_vault,
        {
            "id": "smithdata",
            "DOI": "10.5281/z.1",
            "title": "Dataset",
            "author": [{"family": "Smith"}],
        },
    )

    assert outcome.result is Result.UNREACHABLE


def test_metadata_skips_entries_without_a_doi(net_vault):
    """DOI-less sources are automatically exempt from registry metadata checks."""
    outcome = checks.check_metadata(net_vault, {"id": "webonly2024", "title": "Blog"})

    assert outcome.result is Result.SKIPPED
    assert outcome.target == "webonly2024"
