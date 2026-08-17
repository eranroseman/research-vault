from harness_core import Result, quotes


def test_levenshtein_ratio_bounds():
    assert quotes.levenshtein_ratio("abc", "abc") == 1.0
    assert quotes.levenshtein_ratio("abc", "abd") > 0.6
    assert quotes.levenshtein_ratio("abc", "xyz") < 0.4


def test_exact_after_normalization_uses_a_different_managed_quote_as_fallback(
    fixture_vault,
):
    outs = quotes.check_all_quotes(
        fixture_vault, fixture_vault / "efforts" / "brief" / "draft.md"
    )

    assert len(outs) == 1
    assert outs[0].result is Result.MATCHED
    assert outs[0].target == "smith2020#^c-66666666"
    assert outs[0].extra == {
        "note_path": "efforts/brief/draft.md",
        "claim_id": "c-66666666",
        "line_no": 6,
        "target": "managed-region",
    }


def test_same_address_mismatch_does_not_fall_back_to_a_matching_other_quote(
    fixture_vault,
):
    source = fixture_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
            "- (quote) [@smith2020, p. 13] ^c-66666666\n"
            "  > A wholly unrelated source passage.\n"
            "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
        )
    )

    out = quotes.check_all_quotes(
        fixture_vault, fixture_vault / "efforts" / "brief" / "draft.md"
    )[0]

    assert out.result is Result.UNMATCHED
    assert out.reason == "mismatch — quote absent from source note"


def test_fuzzy_goes_to_inbox_tier(fixture_vault):
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text().replace(
            "Mortality fell 12% across all strata.",
            "Mortality fell 12% across all stratum.",
        )
    )

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert out.result is Result.UNMATCHED
    assert out.reason.startswith("fuzzy-quote")
    assert out.extra["target"] == "managed-region"


def test_case_only_difference_is_not_normalized_to_an_exact_match(fixture_vault):
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text().replace(
            "Mortality fell 12% across all strata.",
            "mortality fell 12% across all strata.",
        )
    )

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert out.result is Result.UNMATCHED
    assert out.reason.startswith("fuzzy-quote")


def test_absent_quote_is_mismatch(fixture_vault):
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text().replace(
            "Mortality fell 12% across all strata.",
            "Entirely fabricated sentence with nothing in common whatsoever here.",
        )
    )

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert out.result is Result.UNMATCHED
    assert out.reason.startswith("mismatch")


def test_no_comparison_text_is_unreachable(fixture_vault):
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(draft.read_text().replace("smith2020, p. 12", "gone2019, p. 1"))

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert out.result is Result.UNREACHABLE
    assert out.reason == "outage — no extractable comparison text"
    assert out.extra == {
        "note_path": "efforts/brief/draft.md",
        "claim_id": "c-66666666",
        "line_no": 6,
        "target": "managed-region",
    }


def test_no_quote_claims_returns_one_controlled_skipped_outcome(fixture_vault):
    note = fixture_vault / "atlas" / "index.md"

    outs = quotes.check_all_quotes(fixture_vault, note)

    assert len(outs) == 1
    assert outs[0].check == "quote"
    assert outs[0].target == "atlas/index.md"
    assert outs[0].result is Result.SKIPPED
    assert outs[0].reason == "no-identifier — note has no quote claims"


def test_unanchored_quote_is_schema_violation_with_its_note_origin(fixture_vault):
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(draft.read_text().replace(" ^c-66666666", ""))

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert out.target == "smith2020"
    assert out.result is Result.UNMATCHED
    assert out.reason == "schema-violation — quote claim has no anchor"
    assert out.extra == {
        "note_path": "efforts/brief/draft.md",
        "claim_id": None,
        "line_no": 6,
        "target": "managed-region",
    }


def test_uncited_quote_is_schema_violation_with_its_note_origin(fixture_vault):
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(draft.read_text().replace(" [@smith2020, p. 12]", ""))

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert out.target == "efforts/brief/draft.md"
    assert out.result is Result.UNMATCHED
    assert out.reason == "schema-violation — quote claim has no citekey"
    assert out.extra == {
        "note_path": "efforts/brief/draft.md",
        "claim_id": "c-66666666",
        "line_no": 6,
        "target": "managed-region",
    }
