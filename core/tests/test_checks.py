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
