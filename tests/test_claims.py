from research_vault import claims

NOTE = """---
citationKey: "smith2020"
---
# Mortality decline

- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12%
  > across all strata.
- (paraphrase) Design is retrospective [@smith2020, p. 3] ^c-22222222
- (inference) Generalizes widely [@smith2020] [confidence:: moderate] [status:: live] ^c-33333333
- (open-question) What drives the decline? ^c-44444444
plain prose is not a claim
"""


def test_parse_counts_and_tags():
    parsed_claims = claims.parse_claims(NOTE)

    assert [claim.tag for claim in parsed_claims] == [
        "quote",
        "paraphrase",
        "inference",
        "open-question",
    ]


def test_quote_aggregates_its_blockquote_continuations():
    quote = claims.parse_claims(NOTE)[0]

    assert quote.quote_text == "Mortality fell 12% across all strata."
    assert quote.citation_key == "smith2020"
    assert quote.locator == "p. 12"
    assert quote.claim_id == "c-11111111"


def test_inline_fields():
    inference = claims.parse_claims(NOTE)[2]

    assert inference.fields == {"confidence": "moderate", "status": "live"}
    assert inference.locator is None


def test_open_question_may_lack_citation():
    open_question = claims.parse_claims(NOTE)[3]

    assert open_question.citation_key is None
    assert open_question.claim_id == "c-44444444"


def test_claim_link():
    assert claims.claim_link("smith2020", "c-11111111") == "smith2020#^c-11111111"


def test_fixture_vault_parses_wikilink_fields(fixture_vault):
    literature = (fixture_vault / "literatures" / "smith2020.md").read_text()
    inference = (
        fixture_vault / "wiki" / "concepts" / "mortality-trends.md"
    ).read_text()
    parsed_inference = claims.parse_claims(inference)[0]

    assert len(claims.parse_claims(literature)) >= 2
    assert parsed_inference.fields["supports"] == "[[smith2020#^c-11111111]]"
    assert parsed_inference.fields["disputes"] == "[[gone2019#^c-22222222]]"


def test_claims_carry_no_managed_flag():
    from research_vault import claims

    (claim,) = claims.parse_claims("- (quote) [@smith2020, p. 1] ^c-1\n  > text\n")
    assert not hasattr(claim, "in_managed")
    assert claim.quote_text == "text"


# --- boundaries the blanket mutation run (Plan W Task 25) found unpinned ------


def test_blockquote_lines_attach_only_to_the_quote_claim_directly_above():
    """A `  > ` line before any claim, after a non-quote claim, or after a
    plain line that closed the quote is not quote text; a plain line after a
    quote claim is neither quote text nor an error."""
    text = (
        "  > stray before any claim\n"
        "- (inference) An inference [@smith2020, p. 1] ^c-1\n"
        "  > not a quote continuation\n"
        "- (quote) [@smith2020, p. 2] ^c-2\n"
        "  > first line\n"
        "  > second line\n"
        "plain prose\n"
        "  > closed already\n"
        "- (quote) [@smith2020, p. 3] ^c-3\n"
    )
    parsed = claims.parse_claims(text)
    assert [(c.tag, c.claim_id, c.quote_text) for c in parsed] == [
        ("inference", "c-1", None),
        ("quote", "c-2", "first line second line"),
        ("quote", "c-3", None),
    ]
