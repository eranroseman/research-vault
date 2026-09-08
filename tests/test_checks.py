import dataclasses

import pytest

from research_vault import Result, checks, webapi
from research_vault.pathcodec import RepoPath


def test_citation_key_check_matches_and_reports_missing_bibliography_entries(
    fixture_vault,
):
    """A bibliography omission must make only its cited key unmatched."""
    outs = checks.check_citation_keys(
        fixture_vault, fixture_vault / "projects" / "brief" / "draft.md"
    )

    by_target = {out.target: out for out in outs}

    assert by_target["smith2020"].result is Result.MATCHED
    assert by_target["fabricated2020"].result is Result.UNMATCHED
    assert by_target["smith2020"].check == "citation-key"
    reason = by_target["fabricated2020"].reason
    assert reason == "mismatch — citation key not in bibliography"


def test_citation_key_check_skips_a_note_with_no_citations(fixture_vault):
    """A citation-free note must not produce an empty or fabricated finding."""
    note = fixture_vault / "wiki" / "concepts" / "clean.md"
    note.write_text("# Clean\n")

    outs = checks.check_citation_keys(fixture_vault, note)

    assert len(outs) == 1
    assert outs[0].target == "path-bytes:wiki/concepts/clean.md"
    assert outs[0].target_kind == "repo-path"
    assert outs[0].result is Result.SKIPPED
    assert outs[0].reason == "no-identifier — note cites nothing"


def test_citation_key_check_scans_citations_in_non_claim_prose(fixture_vault):
    """A checker restricted to parsed claims would miss prose citations."""
    note = fixture_vault / "wiki" / "concepts" / "prose.md"
    note.write_text("See the background evidence [@prose-only2024].\n")

    outs = checks.check_citation_keys(fixture_vault, note)

    assert len(outs) == 1
    assert outs[0].target == "prose-only2024"
    assert outs[0].result is Result.UNMATCHED
    assert outs[0].extra["note_path"] == "path-bytes:wiki/concepts/prose.md"
    assert checks.outcome_to_record(outs[0])["extra"]["claims"] == []


def test_citation_key_check_deduplicates_repeated_citations(fixture_vault):
    """Repeated citations to one key must stay one public outcome."""
    note = fixture_vault / "projects" / "brief" / "draft.md"
    note.write_text(
        note.read_text()
        + "\n- (inference) A second use [@smith2020, p. 13] ^c-88888888\n"
    )

    outs = checks.check_citation_keys(fixture_vault, note)

    assert [out.target for out in outs] == ["fabricated2020", "smith2020"]
    smith = next(out for out in outs if out.target == "smith2020")
    assert checks.outcome_to_record(smith)["extra"]["claims"] == [
        {"claim_id": "c-66666666", "line_no": 7, "locator": "p. 12"},
        {"claim_id": "c-88888888", "line_no": 11, "locator": "p. 13"},
    ]


def test_citation_key_outcome_carries_claim_line_origins(fixture_vault):
    """Later marker stamping needs the exact checked note and claim line."""
    note = fixture_vault / "projects" / "brief" / "draft.md"

    outs = checks.check_citation_keys(fixture_vault, note)

    smith = next(out for out in outs if out.target == "smith2020")
    assert checks.outcome_to_record(smith)["extra"] == {
        "note_path": "path-bytes:projects/brief/draft.md",
        "claims": [{"claim_id": "c-66666666", "line_no": 7, "locator": "p. 12"}],
    }


def test_cited_citation_key_requires_literature_note(tmp_vault):
    """Bibliography membership alone must not satisfy citability."""
    note = tmp_vault / "projects" / "draft.md"
    note.write_text("See the evidence [@smith2020].\n")

    outs = checks.check_citation_keys(tmp_vault, note, {"smith2020": {}})

    assert len(outs) == 1
    assert outs[0].result is Result.UNMATCHED
    assert outs[0].check == "citation-key"
    assert outs[0].reason.startswith("not-captured")
    assert outs[0].reason == "not-captured — cited citation key has no literature note"


def test_cited_citation_key_with_note_passes(tmp_vault):
    """A bibliography entry backed by a literature note still MATCHES."""
    (tmp_vault / "literatures" / "smith2020.md").write_text(
        '---\ncitationKey: "smith2020"\n---\n'
    )
    note = tmp_vault / "projects" / "draft.md"
    note.write_text("See the evidence [@smith2020].\n")

    outs = checks.check_citation_keys(tmp_vault, note, {"smith2020": {}})

    assert len(outs) == 1
    assert outs[0].result is Result.MATCHED
    assert outs[0].reason == "matched"


def test_cited_citation_key_absent_everywhere(tmp_vault):
    """A citation key outside the bibliography keeps the existing mismatch reason."""
    note = tmp_vault / "projects" / "draft.md"
    note.write_text("See the evidence [@fabricated2020].\n")

    outs = checks.check_citation_keys(tmp_vault, note, {})

    assert len(outs) == 1
    assert outs[0].result is Result.UNMATCHED
    assert outs[0].reason == "mismatch — citation key not in bibliography"


def test_outcome_rejects_invalid_reasons_and_detaches_caller_graphs():
    """Outcome detaches every caller graph and exposes no mutation path."""
    first_input = {"nested": {"items": ["one"]}}
    second_input = {"nested": {"items": ["two"]}}
    first = checks.Outcome(
        "citation-key", "smith2020", Result.MATCHED, "matched", first_input
    )
    second = checks.Outcome(
        "citation-key", "gone2019", Result.MATCHED, "matched", second_input
    )
    first_input["nested"]["items"].append("caller mutation")
    second_input["nested"] = {"items": []}

    with pytest.raises(ValueError, match="reason"):
        checks.Outcome("citation-key", "bad", Result.MATCHED, "")
    with pytest.raises(ValueError, match="reason"):
        checks.Outcome("citation-key", "bad", Result.MATCHED, "invalid reason")
    with pytest.raises(TypeError):
        checks.Outcome("citation-key", "bad", Result.MATCHED)

    assert first.extra["nested"]["items"] == ["one"]
    assert second.extra["nested"]["items"] == ["two"]


def test_outcome_assigns_typed_paths_once_and_is_frozen_unhashable():
    outcome = checks.Outcome(
        "quote",
        RepoPath(b"wiki/concepts/no-slash-needed.md"),
        Result.UNMATCHED,
        "mismatch — quote",
        extra={
            "note_path": RepoPath(b"projects/a b.md"),
            "origin": RepoPath(b"literatures/\xff.md"),
            "identifier": "path-bytes:looks/like/a/path",
        },
    )

    assert outcome.target == "path-bytes:wiki/concepts/no-slash-needed.md"
    assert outcome.target_kind == "repo-path"
    assert outcome.path_extra_fields == ("note_path", "origin")
    assert outcome.extra["note_path"] == "path-bytes:projects/a%20b.md"
    assert outcome.extra["origin"] == "path-bytes:literatures/%FF.md"
    assert outcome.extra["identifier"] == "path-bytes:looks/like/a/path"
    for name in ("target", "target_kind", "path_extra_fields"):
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(outcome, name, "changed")
    with pytest.raises(TypeError):
        hash(outcome)

    replaced = dataclasses.replace(
        outcome,
        target=RepoPath(b"wiki/concepts/new.md"),
        extra={"identifier": "plain"},
    )
    assert replaced.target_kind == "repo-path"
    assert replaced.target == "path-bytes:wiki/concepts/new.md"
    assert replaced.path_extra_fields == ()


@pytest.mark.parametrize(
    "extra",
    [
        {"raw": b"bytes"},
        {"nested": [b"bytes"]},
        {"nested": {"path": RepoPath(b"x/a.md")}},
        {1: "non-string key"},
        {"set": {"x"}},
        {"frozen": frozenset({"x"})},
        {"object": object()},
    ],
)
def test_outcome_rejects_non_json_or_nested_typed_path_values(extra):
    with pytest.raises((TypeError, ValueError)):
        checks.Outcome("doi", "id", Result.MATCHED, "matched", extra)


def test_record_round_trip_returns_fresh_typed_values():
    source = checks.Outcome(
        "quote",
        RepoPath(b"wiki/concepts/\xff.md"),
        Result.UNMATCHED,
        "mismatch — quote",
        {
            "note_path": RepoPath(b"projects/a.md"),
            "claims": [{"id": "c-1", "locators": [1, 2]}],
        },
    )
    record = checks.outcome_to_record(source)
    assert record == {
        "check": "quote",
        "target": "path-bytes:wiki/concepts/%FF.md",
        "target_kind": "repo-path",
        "result": "UNMATCHED",
        "reason": "mismatch — quote",
        "extra": {
            "note_path": "path-bytes:projects/a.md",
            "claims": [{"id": "c-1", "locators": [1, 2]}],
        },
        "path_extra_fields": ["note_path"],
    }
    record["extra"]["claims"][0]["locators"].append(3)
    assert source.extra["claims"][0]["locators"] == [1, 2]

    rebuilt = checks.outcome_from_record(checks.outcome_to_record(source))
    assert checks.outcome_to_record(rebuilt) == checks.outcome_to_record(source)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda r: r.pop("target_kind"),
        lambda r: r.__setitem__("target_kind", "path"),
        lambda r: r.__setitem__("path_extra_fields", ["x", "x"]),
        lambda r: r.__setitem__("path_extra_fields", ["z", "a"]),
        lambda r: (
            r.__setitem__("extra", {"note_path": "path-bytes:a%2f"}),
            r.__setitem__("path_extra_fields", ["note_path"]),
        ),
        lambda r: r.__setitem__("unknown", 1),
    ],
)
def test_record_reconstruction_rejects_missing_malformed_or_duplicate_metadata(
    mutator,
):
    record = checks.outcome_to_record(
        checks.Outcome("doi", "id", Result.MATCHED, "matched")
    )
    mutator(record)
    with pytest.raises((TypeError, ValueError)):
        checks.outcome_from_record(record)


@pytest.mark.parametrize(
    ("mutator", "error", "refusal"),
    [
        (lambda r: r.__setitem__("check", 7), TypeError, "text fields must be strings"),
        (
            lambda r: r.__setitem__("target", 7),
            TypeError,
            "text fields must be strings",
        ),
        (
            lambda r: r.__setitem__("reason", 7),
            TypeError,
            "text fields must be strings",
        ),
        (lambda r: r.__setitem__("result", 7), TypeError, "result must be text"),
        (lambda r: r.__setitem__("extra", []), TypeError, "extra must be an object"),
        (
            lambda r: r.__setitem__("path_extra_fields", "note_path"),
            TypeError,
            "JSON array of strings",
        ),
        (
            lambda r: r.__setitem__("path_extra_fields", [7]),
            TypeError,
            "JSON array of strings",
        ),
        (
            lambda r: r.__setitem__("path_extra_fields", ["note_path"]),
            ValueError,
            "does not name a string",
        ),
        (
            lambda r: (
                r.__setitem__("extra", {"note_path": 7}),
                r.__setitem__("path_extra_fields", ["note_path"]),
            ),
            ValueError,
            "does not name a string",
        ),
    ],
    ids=[
        "check-not-text",
        "target-not-text",
        "reason-not-text",
        "result-not-text",
        "extra-not-an-object",
        "path-fields-not-a-list",
        "path-fields-item-not-text",
        "path-field-absent-from-extra",
        "path-field-value-not-text",
    ],
)
def test_record_reconstruction_names_the_field_whose_type_is_wrong(
    mutator, error, refusal
):
    """A record arrives as parsed JSON, so every field's type is an open question.

    `outcome_from_record` is the trust boundary between a JSON file and a typed
    Outcome: nothing upstream of it has checked that `check` is text or that
    `path_extra_fields` is a sorted array naming real string entries in `extra`.
    Each guard is asserted separately, and by message, because a record that
    fails the wrong guard is a record whose defect has been misdiagnosed —
    TypeError says the shape is wrong, ValueError that the shape is right and
    the content disagrees with itself.
    """
    record = checks.outcome_to_record(
        checks.Outcome("doi", "id", Result.MATCHED, "matched")
    )
    mutator(record)

    with pytest.raises(error, match=refusal):
        checks.outcome_from_record(record)


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


def test_normalize_text_keeps_case_but_normalizes_crlf_dehyphenation():
    """Quote normalization must not silently make a case-mutated quote exact."""
    assert (
        checks.normalize_text("Mortali-\r\n ty\u00ad  Decline") == "Mortali ty Decline"
    )
    assert checks.normalize_text("Case") != checks.normalize_text("case")


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
    assert checks.outcome_to_record(outcome)["extra"] == {
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


def test_partial_date_parts_keep_precision():
    """Crossref's optional date-parts precision must survive unpadded."""
    assert checks._notice_date_from_updated({"date-parts": [[2023]]}) == "2023"
    assert checks._notice_date_from_updated({"date-parts": [[2023, 6]]}) == "2023-06"
    assert (
        checks._notice_date_from_updated({"date-parts": [[2023, 6, 15]]})
        == "2023-06-15"
    )


def test_partial_date_parts_still_reject_an_explicit_zero_month_or_day():
    """An explicit 0 is not "absent" — it must still fail range validation,
    not be silently treated as a missing part and laundered through."""
    assert (
        checks._notice_date_from_updated({"date-parts": [[2023, 0]]}) is checks._INVALID
    )
    assert (
        checks._notice_date_from_updated({"date-parts": [[2023, 6, 0]]})
        is checks._INVALID
    )


def _notice(notice_type, notice_date):
    return {"type": notice_type, "notice_date": notice_date}


def test_ambiguous_reinstatement_does_not_clear():
    """A year-only retraction and a same-year full-date reinstatement cannot be
    ordered — the reinstatement could have preceded the retraction — so the
    alert must stand."""
    notices = [_notice("retraction", "2023"), _notice("reinstatement", "2023-06-15")]

    assert checks._active_blocking_notices(notices) == [_notice("retraction", "2023")]


def test_ambiguous_reinstatement_does_not_clear_reversed_precision():
    """The same ambiguity with precision roles reversed: a full-date retraction
    and a year-only reinstatement in the same year still cannot be ordered."""
    notices = [
        _notice("retraction", "2023-06-15"),
        _notice("reinstatement", "2023"),
    ]

    assert checks._active_blocking_notices(notices) == [
        _notice("retraction", "2023-06-15")
    ]


def test_equal_partial_dates_do_not_clear():
    """Two year-only dates that read identically as strings carry no evidence
    of day-level order — the reinstatement could be the earlier of the two —
    so the alert must stand."""
    notices = [_notice("retraction", "2023"), _notice("reinstatement", "2023")]

    assert checks._active_blocking_notices(notices) == [_notice("retraction", "2023")]


def test_unambiguous_full_date_reinstatement_still_clears():
    """The ordinary case, unchanged: two full dates, a later reinstatement
    clears the retraction exactly as before this fix."""
    notices = [
        _notice("retraction", "2023-06-15"),
        _notice("reinstatement", "2023-06-16"),
    ]

    assert checks._active_blocking_notices(notices) == []


def test_same_day_full_date_reinstatement_still_clears():
    """`>=` is load-bearing: a same-day reinstatement still clears today."""
    notices = [
        _notice("retraction", "2023-06-15"),
        _notice("reinstatement", "2023-06-15"),
    ]

    assert checks._active_blocking_notices(notices) == []


def test_differing_precision_reinstatement_still_clears_when_not_a_prefix():
    """A month-only retraction and a full-date reinstatement the following
    month: neither string is a prefix of the other, so the comparison is
    decisive and the later reinstatement clears — differing precision is not,
    by itself, ambiguity."""
    notices = [
        _notice("retraction", "2023-06"),
        _notice("reinstatement", "2023-07-01"),
    ]

    assert checks._active_blocking_notices(notices) == []


def test_update_notice_year_only_retraction_survives_same_year_reinstatement(
    net_vault, monkeypatch
):
    """End-to-end: Crossref reports the retraction with year-only precision
    and a same-year, fully-dated reinstatement. The alert must stand."""
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.1000/year-only": _notice_route("10.1000/year-only"),
            "api.crossref.org/works/10.1000/year-only": _works(
                [
                    {"type": "retraction", "updated": {"date-parts": [[2023]]}},
                    {
                        "type": "reinstatement",
                        "updated": {"date-parts": [[2023, 6, 15]]},
                    },
                ]
            ),
        },
    )

    outcome = checks.check_update_notice(
        net_vault, {"id": "cite", "DOI": "10.1000/year-only"}, "2026-08-16"
    )

    assert outcome.result is Result.UNMATCHED
    assert outcome.reason == "retracted — retraction"
    assert outcome.extra["notice_date"] == "2023"


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


def test_crossref_notices_reads_relation_is_retracted_by_with_no_updated_by():
    """Crossref can express retraction solely through relation.is-retracted-by
    with no updated-by entry at all -- the second read this task adds."""
    payload = {
        "message": {
            "relation": {"is-retracted-by": [{"id": "10.1/notice", "id-type": "doi"}]}
        }
    }

    blocking, warns = checks._crossref_notices(payload)

    assert blocking == [
        {
            "type": "retraction",
            "notice_date": None,
            "source": "relation",
            "id": "10.1/notice",
        }
    ]
    assert warns == []


def test_crossref_notices_relation_retraction_does_not_double_count_updated_by_retraction():
    """A relation retraction naming the same work as an already-established
    updated-by retraction is not double-counted -- same-type dedup."""
    payload = {
        "message": {
            "updated-by": [
                {"type": "retraction", "updated": {"date-parts": [[2024, 1, 1]]}}
            ],
            "relation": {"is-retracted-by": [{"id": "10.1/notice", "id-type": "doi"}]},
        }
    }

    blocking, warns = checks._crossref_notices(payload)

    assert blocking == [{"type": "retraction", "notice_date": "2024-01-01"}]
    assert warns == []


def test_crossref_notices_relation_retraction_adds_alongside_updated_by_withdrawal():
    """Dedup is same-type only: a withdrawal and a relation-sourced
    retraction are distinct signals, so the relation retraction is new
    information and must be added, not suppressed by the differently-typed
    updated-by notice -- both notices exist afterward."""
    payload = {
        "message": {
            "updated-by": [
                {"type": "withdrawal", "updated": {"date-parts": [[2024, 1, 1]]}}
            ],
            "relation": {"is-retracted-by": [{"id": "10.1/notice", "id-type": "doi"}]},
        }
    }

    blocking, warns = checks._crossref_notices(payload)

    assert blocking == [
        {"type": "withdrawal", "notice_date": "2024-01-01"},
        {
            "type": "retraction",
            "notice_date": None,
            "source": "relation",
            "id": "10.1/notice",
        },
    ]
    assert warns == []


def test_crossref_notices_relation_multiple_entries_each_append_their_own_notice():
    """Every well-formed relation entry appends its own blocking notice --
    not just the first one encountered. Two distinct linked DOIs are two
    distinct pieces of signal, both kept, each with its own id."""
    payload = {
        "message": {
            "relation": {
                "is-retracted-by": [
                    {"id": "10.1/first", "id-type": "doi"},
                    {"id": "10.1/second", "id-type": "doi"},
                ]
            }
        }
    }

    blocking, warns = checks._crossref_notices(payload)

    assert blocking == [
        {
            "type": "retraction",
            "notice_date": None,
            "source": "relation",
            "id": "10.1/first",
        },
        {
            "type": "retraction",
            "notice_date": None,
            "source": "relation",
            "id": "10.1/second",
        },
    ]
    assert warns == []


@pytest.mark.parametrize(
    "relation",
    [
        [],
        "bad",
        7,
        {"is-retracted-by": {}},
        {"is-retracted-by": "bad"},
        {"is-retracted-by": 7},
        {"is-retracted-by": ["not-a-dict"]},
        {"is-retracted-by": [{"id-type": "doi"}]},
        {"is-retracted-by": [{"id": 7, "id-type": "doi"}]},
        {"is-retracted-by": [{"id": "", "id-type": "doi"}]},
        {"has-preprint": [{"id": "10.1/preprint", "id-type": "doi"}]},
    ],
)
def test_crossref_notices_ignores_malformed_relation_entries_without_erasing_updated_by(
    relation,
):
    """A malformed relation.is-retracted-by shape is additive-only: it is
    skipped, never a reason to discard the verdict updated-by already
    established -- the opposite of updated-by's own fail-closed bail-out."""
    payload = {
        "message": {
            "updated-by": [
                {"type": "withdrawal", "updated": {"date-parts": [[2024, 1, 1]]}}
            ],
            "relation": relation,
        }
    }

    blocking, warns = checks._crossref_notices(payload)

    assert blocking == [{"type": "withdrawal", "notice_date": "2024-01-01"}]
    assert warns == []


def test_active_blocking_notices_undated_relation_retraction_survives_reinstatement():
    """An undated relation-sourced retraction can never be auto-cleared: its
    chronological order against a dated reinstatement is undecidable, so the
    escape path is human ack/adjudication, not automatic clearance."""
    notices = [
        {
            "type": "retraction",
            "notice_date": None,
            "source": "relation",
            "id": "10.1/notice",
        },
        {"type": "reinstatement", "notice_date": "2024-01-01"},
    ]

    assert checks._active_blocking_notices(notices) == [
        {
            "type": "retraction",
            "notice_date": None,
            "source": "relation",
            "id": "10.1/notice",
        }
    ]


def test_update_notice_relation_only_retraction_blocks_without_leaking_internal_keys(
    net_vault, monkeypatch
):
    """End-to-end: a relation-only retraction (no updated-by at all) blocks,
    and the notice dict's internal source/id bookkeeping keys never reach
    the Outcome extra -- _blocking_outcome builds extra explicitly from
    type/notice_date only."""
    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/10.1000/relation-only": _notice_route(
                "10.1000/relation-only"
            ),
            "api.crossref.org/works/10.1000/relation-only": (
                200,
                {
                    "message": {
                        "relation": {
                            "is-retracted-by": [{"id": "10.1/notice", "id-type": "doi"}]
                        }
                    }
                },
            ),
        },
    )

    outcome = checks.check_update_notice(
        net_vault, {"id": "cite", "DOI": "10.1000/relation-only"}, "2026-08-16"
    )

    assert outcome.result is Result.UNMATCHED
    assert outcome.reason == "retracted — retraction"
    assert checks.outcome_to_record(outcome)["extra"] == {
        "class": "blocking",
        "type": "retraction",
        "notice_date": None,
        "detection_date": "2026-08-16",
    }


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
    assert checks.outcome_to_record(outcome)["extra"] == {
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
        ("2", {"data": {"attributes": {}}}, Result.UNREACHABLE),
        ("2", {"data": {"attributes": {"version": ["2"]}}}, Result.UNREACHABLE),
        ("2", {"data": {"attributes": {"version": "3"}}}, Result.UNMATCHED),
    ],
    ids=["missing-remote", "ambiguous-remote", "mismatch"],
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


def test_update_notice_datacite_skips_when_local_version_is_absent(
    net_vault, monkeypatch
):
    """A locally absent version will never resolve by retrying — skip, don't hold."""
    seen = []

    def fake(url, vault_root, params=None, headers=None, timeout=10.0):
        seen.append(url)
        if "doiRA" in url:
            return _notice_route("10.5281/versioned", "DataCite")
        if "openalex" in url:
            return 200, {"is_retracted": False}
        raise AssertionError(f"unexpected URL {url}")

    monkeypatch.setattr(webapi, "get_json", fake)

    outcome = checks.check_update_notice(
        net_vault, {"id": "data", "DOI": "10.5281/versioned"}, "2026-08-16"
    )

    assert outcome.result is Result.SKIPPED
    assert outcome.reason == "no-identifier — item has no local version"
    assert not any("api.datacite.org" in url for url in seen)


def test_update_notice_arxiv_skips_when_local_version_is_absent(net_vault, monkeypatch):
    """The arXiv twin of the DataCite missing-local-version skip."""
    seen = []

    def fake_json(url, vault_root, params=None, headers=None, timeout=10.0):
        if "doiRA" in url:
            return _notice_route("10.48550/arxiv.2401.12345", "DataCite")
        return 200, {"is_retracted": False}

    def fake_text(url, vault_root, params=None, headers=None, timeout=10.0):
        seen.append(url)
        raise AssertionError("no arXiv feed request should be made")

    monkeypatch.setattr(webapi, "get_json", fake_json)
    monkeypatch.setattr(webapi, "get_text", fake_text)

    outcome = checks.check_update_notice(
        net_vault,
        {
            "id": "preprint",
            "DOI": "10.48550/arxiv.2401.12345",
            "URL": "https://arxiv.org/abs/2401.12345v2",
        },
        "2026-08-16",
    )

    assert outcome.result is Result.SKIPPED
    assert outcome.reason == "no-identifier — item has no local version"
    assert seen == []


def test_update_notice_arxiv_malformed_local_version_stays_unreachable(
    net_vault, monkeypatch
):
    """A present-but-malformed local version is not absent — still an outage."""

    def fake_text(url, vault_root, params=None, headers=None, timeout=10.0):
        raise AssertionError("no arXiv feed request should be made")

    _fake_get(
        monkeypatch,
        {
            "doi.org/doiRA/": _notice_route("10.48550/arxiv.2401.12345", "DataCite"),
            "api.openalex.org/works/": (200, {"is_retracted": False}),
        },
    )
    monkeypatch.setattr(webapi, "get_text", fake_text)

    outcome = checks.check_update_notice(
        net_vault,
        {
            "id": "preprint",
            "DOI": "10.48550/arxiv.2401.12345",
            "URL": "https://arxiv.org/abs/2401.12345v2",
            "version": "2",
        },
        "2026-08-16",
    )

    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason == "outage — arXiv version status unavailable"


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


def test_rw_date_accepts_production_formats():
    """Retraction Watch's production CSV ships M/D/Y and M/D/Y H:M, not just ISO."""
    assert checks._rw_date("1/2/2023 0:00") == "2023-01-02"
    assert checks._rw_date("12/31/2019") == "2019-12-31"
    assert checks._rw_date("2023-01-02") == "2023-01-02"  # ISO still accepted
    assert checks._rw_date("not a date") is checks._INVALID
    assert checks._rw_date("13/45/2023 0:00") is checks._INVALID


def test_rw_csv_matches_both_identifiers_and_blocking_beats_warning(tmp_path):
    """DOI and PMID hits are both considered instead of short-circuiting on DOI."""
    csv_file = tmp_path / "rw.csv"
    csv_file.write_text(
        "OriginalPaperDOI,OriginalPaperPubMedID,RetractionDate,RetractionNature\n"
        "https://doi.org/10.1000/doi-warn,111,2023-01-01,Expression of concern\n"
        ",111,2/2/2024 0:00,Retraction\n"
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
    assert checks.outcome_to_record(outcome)["extra"] == {
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
    assert checks.outcome_to_record(matched)["extra"]["warn_notices"] == [
        {"type": "correction", "notice_date": "2023-01-01"},
        {"type": "erratum", "notice_date": None},
    ]
    assert unmatched.result is Result.UNMATCHED
    assert unmatched.reason == "retracted — withdrawal"


def test_reduce_preserves_nonblocking_unmatched_over_matched():
    """A ran-and-disagreed non-blocking UNMATCHED must outrank a MATCHED."""
    live = checks.Outcome(
        "update-notice",
        "cite",
        Result.UNMATCHED,
        "mismatch — version differs",
        extra={"warn_notices": []},
    )
    rw = checks.Outcome(
        "update-notice",
        "cite",
        Result.MATCHED,
        "matched",
        extra={"warn_notices": [{"type": "correction", "notice_date": None}]},
    )

    reduced = checks.reduce_update_notice_outcomes(live, rw)

    assert reduced.result is Result.UNMATCHED  # ran-and-disagreed survives
    assert reduced.extra.get("warn_notices")  # RW's warns still merged


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


def test_notice_reducer_rebuilds_through_typed_records_without_mutating_sources():
    live = checks.Outcome(
        "update-notice",
        RepoPath(b"literatures/\xff.md"),
        Result.MATCHED,
        "matched",
        {
            "note_path": RepoPath(b"literatures/\xff.md"),
            "warn_notices": [{"type": "correction", "notice_date": "2026-01-01"}],
        },
    )
    rw = checks.Outcome(
        "update-notice",
        RepoPath(b"literatures/\xff.md"),
        Result.UNREACHABLE,
        "outage — RW unavailable",
        {"note_path": RepoPath(b"literatures/\xff.md")},
    )
    live_record = checks.outcome_to_record(live)
    rw_record = checks.outcome_to_record(rw)

    reduced = checks.reduce_update_notice_outcomes(live, rw)

    assert reduced is not live
    assert reduced is not rw
    assert reduced.target_kind == "repo-path"
    assert reduced.path_extra_fields == ("note_path",)
    assert reduced.extra["warn_notices"][0]["type"] == "correction"
    assert checks.outcome_to_record(live) == live_record
    assert checks.outcome_to_record(rw) == rw_record
