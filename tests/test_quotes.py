import os

import pytest

from research_vault import Result, quotes
from research_vault.checks import Outcome
from research_vault.pathcodec import RepoPath


def test_levenshtein_ratio_bounds():
    assert quotes.levenshtein_ratio("abc", "abc") == 1.0
    assert quotes.levenshtein_ratio("abc", "abd") > 0.6
    assert quotes.levenshtein_ratio("abc", "xyz") < 0.4


def test_exact_after_normalization_uses_a_different_managed_quote_as_fallback(
    fixture_vault,
):
    outs = quotes.check_all_quotes(
        fixture_vault, fixture_vault / "projects" / "brief" / "draft.md"
    )

    assert len(outs) == 1
    assert outs[0].result is Result.MATCHED
    assert outs[0].target == "smith2020#^c-66666666"
    assert outs[0].extra == {
        "note_path": "path-bytes:projects/brief/draft.md",
        "claim_id": "c-66666666",
        "line_no": 7,
        "target": "managed-region",
    }


def test_same_address_mismatch_does_not_fall_back_to_a_matching_other_quote(
    fixture_vault,
):
    source = fixture_vault / "literature" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
            "- (quote) [@smith2020, p. 13] ^c-66666666\n"
            "  > A wholly unrelated source passage.\n"
            "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
        )
    )

    out = quotes.check_all_quotes(
        fixture_vault, fixture_vault / "projects" / "brief" / "draft.md"
    )[0]

    assert out.result is Result.UNMATCHED
    assert out.reason == "mismatch — quote absent from literature note"


def test_empty_same_address_source_quote_falls_back_to_extractable_quote(
    fixture_vault,
):
    source = fixture_vault / "literature" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
            "- (quote) [@smith2020, p. 13] ^c-66666666\n"
            "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
        )
    )

    out = quotes.check_all_quotes(
        fixture_vault, fixture_vault / "projects" / "brief" / "draft.md"
    )[0]

    assert out.result is Result.MATCHED
    assert out.reason == "matched"


def test_fuzzy_goes_to_inbox_tier(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text().replace(
            "Mortality fell 12% across all strata.",
            "Mortality fell 12% across all stratum.",
        )
    )

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert out.result is Result.UNMATCHED
    assert out.reason == "fuzzy-quote — best ratio 0.95"
    assert out.extra["target"] == "managed-region"


def test_case_only_difference_is_not_normalized_to_an_exact_match(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text().replace(
            "Mortality fell 12% across all strata.",
            "mortality fell 12% across all strata.",
        )
    )

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert out.result is Result.UNMATCHED
    assert out.reason == "fuzzy-quote — best ratio 0.97"


def test_absent_quote_is_mismatch(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text().replace(
            "Mortality fell 12% across all strata.",
            "Entirely fabricated sentence with nothing in common whatsoever here.",
        )
    )

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert out.result is Result.UNMATCHED
    assert out.reason == "mismatch — quote absent from literature note"


def test_no_comparison_text_is_unreachable(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(draft.read_text().replace("smith2020, p. 12", "gone2019, p. 1"))

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert out.result is Result.UNREACHABLE
    assert out.reason == "outage — no extractable comparison text"
    assert out.extra == {
        "note_path": "path-bytes:projects/brief/draft.md",
        "claim_id": "c-66666666",
        "line_no": 7,
        "target": "managed-region",
    }


def test_textless_quote_is_schema_violation_on_its_claim_link(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    lines = draft.read_text().splitlines(keepends=True)
    draft.write_text("".join(line for line in lines if not line.startswith("  > ")))

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert (out.check, out.target, out.result, out.reason) == (
        "quote",
        "smith2020#^c-66666666",
        Result.UNMATCHED,
        "schema-violation — quote claim has no text",
    )
    assert out.extra == {
        "note_path": "path-bytes:projects/brief/draft.md",
        "claim_id": "c-66666666",
        "line_no": 7,
        "target": "managed-region",
    }


def test_a_ratio_exactly_at_the_fuzzy_threshold_is_fuzzy_not_mismatch(
    fixture_vault, monkeypatch
):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text().replace(
            "Mortality fell 12% across all strata.", "Something else entirely."
        )
    )
    monkeypatch.setattr(
        quotes, "levenshtein_ratio", lambda a, b: quotes.FUZZY_THRESHOLD
    )

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert (out.check, out.result) == ("quote", Result.UNMATCHED)
    assert out.reason == "fuzzy-quote — best ratio 0.90"


def test_an_anchorless_claim_and_a_quoteless_source_row_under_the_quote_check(
    fixture_vault,
):
    """Both early exits file under check `quote`: no anchor targets the
    citation key alone; a source with no extractable text is an outage on
    the claim link."""
    from research_vault.claims import Claim

    anchorless = Claim("quote", "smith2020", None, None, 3, quote_text="x")
    out = quotes.check_quote(fixture_vault, anchorless, "smith2020")
    assert (out.check, out.target, out.result, out.reason) == (
        "quote",
        "smith2020",
        Result.UNMATCHED,
        "schema-violation — quote claim has no anchor",
    )

    (fixture_vault / "literature" / "smith2020.md").write_text(
        '---\ntype: "literature"\n---\n# Smith\n'
    )
    anchored = Claim("quote", "smith2020", None, "c-66666666", 3, quote_text="x")
    out = quotes.check_quote(fixture_vault, anchored, "smith2020")
    assert (out.check, out.target, out.result, out.reason) == (
        "quote",
        "smith2020#^c-66666666",
        Result.UNREACHABLE,
        "outage — no extractable comparison text",
    )


def test_no_quote_claims_returns_one_controlled_skipped_outcome(fixture_vault):
    note = fixture_vault / "wiki" / "concepts" / "clean.md"
    note.write_text("# Clean\n")

    outs = quotes.check_all_quotes(fixture_vault, note)

    assert len(outs) == 1
    assert outs[0].check == "quote"
    assert outs[0].target == "path-bytes:wiki/concepts/clean.md"
    assert outs[0].result is Result.SKIPPED
    assert outs[0].reason == "no-identifier — note has no quote claims"


def test_unanchored_quote_is_schema_violation_with_its_note_origin(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(draft.read_text().replace(" ^c-66666666", ""))

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert out.target == "smith2020"
    assert out.result is Result.UNMATCHED
    assert out.reason == "schema-violation — quote claim has no anchor"
    assert out.extra == {
        "note_path": "path-bytes:projects/brief/draft.md",
        "claim_id": None,
        "line_no": 7,
        "target": "managed-region",
    }


def test_uncited_quote_is_schema_violation_with_its_note_origin(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(draft.read_text().replace(" [@smith2020, p. 12]", ""))

    out = quotes.check_all_quotes(fixture_vault, draft)[0]

    assert out.target == "path-bytes:projects/brief/draft.md"
    assert out.result is Result.UNMATCHED
    assert out.reason == "schema-violation — quote claim has no citation key"
    assert out.extra == {
        "note_path": "path-bytes:projects/brief/draft.md",
        "claim_id": "c-66666666",
        "line_no": 7,
        "target": "managed-region",
    }


def test_quote_producers_type_note_paths_but_keep_claim_links_identifiers(
    fixture_vault,
):
    note = fixture_vault / "projects" / "brief" / "draft.md"
    claim = quotes.check_all_quotes(fixture_vault, note)[0]

    assert claim.target_kind == "identifier"
    assert claim.path_extra_fields == ("note_path",)
    assert claim.extra["note_path"] == "path-bytes:projects/brief/draft.md"

    note_without_claims = fixture_vault / "wiki" / "concepts" / "clean.md"
    note_without_claims.write_text("# Clean\n")
    fallback = quotes.check_all_quotes(fixture_vault, note_without_claims)[0]
    assert fallback.target == "path-bytes:wiki/concepts/clean.md"
    assert fallback.target_kind == "repo-path"


def test_kind_is_not_inferred_from_slash_or_prefix_text():
    path_outcome = Outcome(
        "quote", RepoPath(b"note.md"), Result.SKIPPED, "no-identifier — none"
    )
    identifier = Outcome(
        "quote", "path-bytes:note.md", Result.SKIPPED, "no-identifier — none"
    )
    slash_identifier = Outcome("quote", "doi/with/slash", Result.MATCHED, "matched")

    assert path_outcome.target == identifier.target
    assert path_outcome.target_kind == "repo-path"
    assert identifier.target_kind == slash_identifier.target_kind == "identifier"


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads everything")
def test_check_all_quotes_reports_an_undecodable_or_unreadable_note(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_bytes(b"\xff\xfe- (quote) [@smith2020, p. 1] ^c-1\n")
    (row,) = quotes.check_all_quotes(fixture_vault, draft)
    assert (row.check, row.result) == ("quote", Result.UNMATCHED)
    # The tail is the codec's; the byte it names is the one the fixture planted.
    assert row.reason.startswith(
        "schema-violation — not UTF-8: 'utf-8' codec can't decode byte 0xff"
    )
    assert row.target == "path-bytes:projects/brief/draft.md"
    draft.write_text("- (quote) [@smith2020, p. 1] ^c-1\n  > x\n")
    draft.chmod(0)
    try:
        (row,) = quotes.check_all_quotes(fixture_vault, draft)
    finally:
        draft.chmod(0o644)
    assert (row.result, row.reason.split(" — ")[0]) == (Result.UNREACHABLE, "outage")


def test_check_all_quotes_reports_an_undecodable_source_note_on_the_claim(
    fixture_vault,
):
    """The literature note a quote claim cites cannot be read: that claim's
    row says so, under the claim link, and the other claims are judged."""
    (fixture_vault / "literature" / "smith2020.md").write_bytes(b"\xff\xfe")
    rows = quotes.check_all_quotes(
        fixture_vault, fixture_vault / "projects" / "brief" / "draft.md"
    )
    assert rows
    assert all(
        r.reason.startswith(
            "schema-violation — not UTF-8: 'utf-8' codec can't decode byte 0xff"
        )
        for r in rows
    )
    assert all(str(r.target).startswith("smith2020#^") for r in rows)
