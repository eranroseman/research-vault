import pytest

from harness_core import Result, checks, webapi


def test_citekey_check_matches_and_reports_missing_bibliography_entries(fixture_vault):
    """A bibliography omission must make only its cited key unmatched."""
    outs = checks.check_citekeys(
        fixture_vault, fixture_vault / "efforts" / "brief" / "draft.md"
    )

    by_target = {out.target: out for out in outs}

    assert by_target["smith2020"].result is Result.MATCHED
    assert by_target["fabricated2020"].result is Result.UNMATCHED
    reason = by_target["fabricated2020"].reason
    assert reason == "mismatch — citekey not in bibliography"


def test_citekey_check_skips_a_note_with_no_citations(fixture_vault):
    """A citation-free note must not produce an empty or fabricated finding."""
    note = fixture_vault / "atlas" / "index.md"

    outs = checks.check_citekeys(fixture_vault, note)

    assert len(outs) == 1
    assert outs[0].target == str(note)
    assert outs[0].result is Result.SKIPPED
    assert outs[0].reason == "no-identifier — note cites nothing"


def test_citekey_check_scans_citations_in_non_claim_prose(fixture_vault):
    """A checker restricted to parsed claims would miss prose citations."""
    note = fixture_vault / "atlas" / "prose.md"
    note.write_text("See the background evidence [@prose-only2024].\n")

    outs = checks.check_citekeys(fixture_vault, note)

    assert len(outs) == 1
    assert outs[0].target == "prose-only2024"
    assert outs[0].result is Result.UNMATCHED
    assert outs[0].extra["note_path"] == "atlas/prose.md"
    assert outs[0].extra["claims"] == []


def test_citekey_check_deduplicates_repeated_citations(fixture_vault):
    """Repeated citations to one key must stay one public outcome."""
    note = fixture_vault / "efforts" / "brief" / "draft.md"
    note.write_text(
        note.read_text()
        + "\n- (inference) A second use [@smith2020, p. 13] ^c-88888888\n"
    )

    outs = checks.check_citekeys(fixture_vault, note)

    assert [out.target for out in outs] == ["fabricated2020", "smith2020"]
    smith = next(out for out in outs if out.target == "smith2020")
    assert smith.extra["claims"] == [
        {"claim_id": "c-66666666", "line_no": 6, "locator": "p. 12"},
        {"claim_id": "c-88888888", "line_no": 10, "locator": "p. 13"},
    ]


def test_citekey_outcome_carries_claim_line_origins(fixture_vault):
    """Later marker stamping needs the exact checked note and claim line."""
    note = fixture_vault / "efforts" / "brief" / "draft.md"

    outs = checks.check_citekeys(fixture_vault, note)

    smith = next(out for out in outs if out.target == "smith2020")
    assert smith.extra == {
        "note_path": "efforts/brief/draft.md",
        "claims": [{"claim_id": "c-66666666", "line_no": 6, "locator": "p. 12"}],
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


@pytest.fixture
def net_vault(fixture_vault):
    harness = fixture_vault / ".harness"
    harness.mkdir(exist_ok=True)
    (harness / "machine.json").write_text('{"mailto": "eran@example.edu"}')
    return fixture_vault


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
