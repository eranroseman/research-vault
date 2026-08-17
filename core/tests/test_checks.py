import pytest

from harness_core import Result, checks


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
