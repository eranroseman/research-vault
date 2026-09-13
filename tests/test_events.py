import pytest

from research_vault import Result, events, frontmatter
from tests.conftest import must_replace

BASE = """---
citationKey: "smith2020"
type: "literature"
doi: "10.1000/xyz"
---
- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12% across all strata.
"""

PMID_ONLY = """---
citationKey: "pmid2020"
type: "literature"
pmid: "12345"
---
"""

NO_ID_QUOTE = """---
citationKey: "noid2020"
type: "literature"
---
- (quote) [@noid2020, p. 1] ^c-11111111
  > A quoted sentence.
"""


def test_record_pass_appends_event_and_preserves_note_contents():
    out = events.record_pass(BASE, "doi", Result.MATCHED, at="2026-08-16")

    data, body = frontmatter.parse(out)

    assert data["citationKey"] == "smith2020"
    assert data["doi"] == "10.1000/xyz"
    assert (
        body
        == """- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12% across all strata.
"""
    )
    assert events.verified_checks(out) == [
        {"by": "research_vault/0.1.0", "at": "2026-08-16", "check": "doi"}
    ]


def test_record_pass_on_bare_mapping_note_writes_one_verified_block():
    text = (
        '---\ntype: "literature"\n'
        'verified: {by: "human:eran", at: "2026-08-02T09:00:00Z"}\n---\nbody\n'
    )
    updated = events.record_pass(text, "doi", Result.MATCHED, at="2026-09-02")
    assert updated.count("verified:") == 1
    data, _ = frontmatter.parse(updated)
    assert len(data["verified"]) == 2


def test_record_pass_preserves_crlf_body_without_double_carriage_returns():
    crlf = must_replace(BASE, "\n", "\r\n", -1)
    out = events.record_pass(crlf, "doi", Result.MATCHED, at="2026-08-16")
    assert "\r\r\n" not in out
    assert out.endswith("  > Mortality fell 12% across all strata.\r\n")


def test_record_pass_lexically_changes_only_verified_events_with_crlf():
    from research_vault import notes

    text = (
        "---\r\n"
        "citationKey: smith2020\r\n"
        "status: included\r\n"
        "deprecated-at: 2026-08-16\r\n"
        "---\r\n"
        "- (quote) body ^c-11111111\r\n"
    )

    out = events.record_pass(text, "doi", Result.MATCHED, at="2026-08-17")

    assert "\r\r\n" not in out
    assert "citationKey: smith2020\r\nstatus: included\r\n" in out
    assert out.endswith("- (quote) body ^c-11111111\r\n")
    assert notes.canonical_content(out) == notes.canonical_content(text)


@pytest.mark.parametrize("newline", ["\n", "\r\n"], ids=["lf", "crlf"])
@pytest.mark.parametrize(
    "frontmatter_line", ["", 'status: "included"'], ids=["empty", "nonempty"]
)
def test_record_pass_inserts_events_before_preclose_blank(newline, frontmatter_line):
    from research_vault import notes

    existing_fields = f"{frontmatter_line}{newline}" if frontmatter_line else ""
    body = f"- (quote) body ^c-11111111{newline}"
    text = f"---{newline}{existing_fields}{newline}---{newline}{body}"

    out = events.record_pass(text, "doi", Result.MATCHED, at="2026-08-17")

    event = '  - {by: "research_vault/0.1.0", at: "2026-08-17", check: "doi"}'
    assert out == (
        f"---{newline}{existing_fields}verified:{newline}{event}{newline}"
        f"{newline}---{newline}{body}"
    )
    data, parsed_body = frontmatter.parse(out)
    assert data.get("status") == ("included" if frontmatter_line else None)
    assert parsed_body == body
    assert events.verified_checks(out) == [
        {"by": "research_vault/0.1.0", "at": "2026-08-17", "check": "doi"}
    ]
    assert notes.canonical_content(out) == notes.canonical_content(text)
    if newline == "\r\n":
        assert "\r\r\n" not in out
        assert "\n" not in must_replace(out, "\r\n", "", -1)


@pytest.mark.parametrize("newline", ["\n", "\r\n"], ids=["lf", "crlf"])
def test_record_pass_owned_only_envelope_canonicalizes_to_body(newline):
    from research_vault import notes

    body = f"- (quote) body-only ^c-11111111{newline}"
    first = events.record_pass(body, "doi", Result.MATCHED, at="2026-08-16")
    second = events.record_pass(first, "metadata", Result.MATCHED, at="2026-08-17")
    with_status = must_replace(
        first, f"verified:{newline}", f'status: "deprecated"{newline}verified:{newline}'
    )

    assert first.endswith(body)
    if newline == "\r\n":
        assert "\r\r\n" not in first
        assert "\n" not in must_replace(first, "\r\n", "", -1)
    assert notes.canonical_content(first) == notes.canonical_content(body)
    assert notes.canonical_content(second) == notes.canonical_content(body)
    assert events.verified_checks(second) == [
        {"by": "research_vault/0.1.0", "at": "2026-08-16", "check": "doi"},
        {
            "by": "research_vault/0.1.0",
            "at": "2026-08-17",
            "check": "metadata",
        },
    ]
    assert notes.content_changed(body, with_status)


def test_record_pass_rejects_non_matched():
    for result in (Result.UNMATCHED, Result.UNREACHABLE, Result.SKIPPED):
        with pytest.raises(ValueError, match="only MATCHED mints verified events"):
            events.record_pass(BASE, "doi", result)


def test_trust_tier_progression():
    assert events.trust_tier(BASE) == "unverified"
    text = BASE
    for check in ("doi", "metadata", "update-notice"):
        text = events.record_pass(text, check, Result.MATCHED, at="2026-08-16")
    assert events.trust_tier(text) == "unverified"

    text = events.record_pass(
        text,
        "quote:smith2020#^c-11111111:managed-region",
        Result.MATCHED,
        at="2026-08-16",
    )
    assert events.trust_tier(text) == "machine-confirmed"

    text = events.record_pass(
        text, "doi", Result.MATCHED, by="human:eran", at="2026-08-17"
    )
    assert events.trust_tier(text) == "human-reviewed"


def test_no_identifier_no_claims_note_is_unverified():
    """An empty applicable-check set must not vacuously satisfy machine-confirmed."""
    text = "---\ntype: literature\ncitationKey: url2024only\nurl: https://example.org\n---\nbody\n"
    assert events.trust_tier(text) == "unverified"


def test_frontmatterless_text_is_unverified():
    """No frontmatter means no applicable checks and no quote claims — still not machine-confirmed."""
    assert events.trust_tier("just some text\n") == "unverified"


def test_identifier_less_note_with_matched_quote_is_machine_confirmed():
    """The floor is OR, not AND: a matched managed quote clears it on its own
    even with an empty applicable-check set (no doi/pmid)."""
    text = events.record_pass(
        NO_ID_QUOTE,
        "quote:noid2020#^c-11111111:managed-region",
        Result.MATCHED,
        at="2026-08-16",
    )
    assert events.trust_tier(text) == "machine-confirmed"


def test_identifier_less_note_with_matched_quote_and_human_event_is_human_reviewed():
    """human-reviewed inherits the same OR: a human: event on top of a
    matched managed quote reaches it with no doi/pmid present."""
    text = events.record_pass(
        NO_ID_QUOTE,
        "quote:noid2020#^c-11111111:managed-region",
        Result.MATCHED,
        at="2026-08-16",
    )
    text = events.record_pass(
        text,
        "quote:noid2020#^c-11111111:managed-region",
        Result.MATCHED,
        by="human:eran",
        at="2026-08-17",
    )
    assert events.trust_tier(text) == "human-reviewed"


def test_identifier_less_note_with_human_event_and_no_quotes_is_unverified():
    """A human: event alone no longer derives human-reviewed when the note
    has neither an applicable check nor a managed quote claim — the floor
    applies before the human-actor check runs."""
    text = '---\ncitationKey: "noid2020"\ntype: "literature"\n---\nbody\n'
    text = events.record_pass(
        text, "doi", Result.MATCHED, by="human:eran", at="2026-08-16"
    )
    assert events.trust_tier(text) == "unverified"


def test_human_event_alone_is_not_human_reviewed():
    text = events.record_pass(
        BASE, "doi", Result.MATCHED, by="human:eran", at="2026-08-16"
    )

    assert events.trust_tier(text) == "unverified"


def test_pmid_only_requires_update_notice_coverage():
    assert events.trust_tier(PMID_ONLY) == "unverified"

    text = events.record_pass(
        PMID_ONLY, "update-notice", Result.MATCHED, at="2026-08-16"
    )

    assert events.trust_tier(text) == "machine-confirmed"


def test_each_quote_claim_requires_its_own_address():
    text = BASE + (
        "- (quote) [@smith2020, p. 13] ^c-22222222\n  > The decline was sustained.\n"
    )
    for check in ("doi", "metadata", "update-notice"):
        text = events.record_pass(text, check, Result.MATCHED, at="2026-08-16")
    text = events.record_pass(
        text,
        "quote:smith2020#^c-11111111:managed-region",
        Result.MATCHED,
        at="2026-08-16",
    )

    assert events.trust_tier(text) == "unverified"


def test_quote_coverage_requires_a_supported_comparison_target():
    text = BASE
    for check in ("doi", "metadata", "update-notice"):
        text = events.record_pass(text, check, Result.MATCHED, at="2026-08-16")
    text = events.record_pass(
        text,
        "quote:smith2020#^c-11111111:unsupported-target",
        Result.MATCHED,
        at="2026-08-16",
    )

    assert events.trust_tier(text) == "unverified"


def test_source_text_quote_coverage_is_machine_confirmed():
    text = BASE
    for check in ("doi", "metadata", "update-notice"):
        text = events.record_pass(text, check, Result.MATCHED, at="2026-08-16")
    text = events.record_pass(
        text,
        "quote:smith2020#^c-11111111:source-text",
        Result.MATCHED,
        at="2026-08-16",
    )

    assert events.trust_tier(text) == "machine-confirmed"


def _with_verified(value):
    data, body = frontmatter.parse(BASE)
    data["verified"] = value
    return frontmatter.serialize(data) + body


def _machine_confirmed_text():
    text = BASE
    for check in (
        "doi",
        "metadata",
        "update-notice",
        "quote:smith2020#^c-11111111:managed-region",
    ):
        text = events.record_pass(text, check, Result.MATCHED, at="2026-08-16")
    return text


@pytest.mark.parametrize(
    "malformed",
    [
        _with_verified("corrupt"),
        _with_verified(
            frontmatter.parse(_machine_confirmed_text())[0]["verified"] + ["corrupt"]
        ),
    ],
    ids=["scalar", "mixed-list"],
)
def test_malformed_verified_events_fail_closed_on_read(malformed):
    assert events.verified_checks(malformed) == []
    assert events.trust_tier(malformed) == "unverified"


@pytest.mark.parametrize(
    "malformed",
    [
        _with_verified("corrupt"),
        _with_verified(
            frontmatter.parse(_machine_confirmed_text())[0]["verified"] + ["corrupt"]
        ),
    ],
    ids=["scalar", "mixed-list"],
)
def test_record_pass_rejects_malformed_verified_events(malformed):
    with pytest.raises(ValueError, match="verified"):
        events.record_pass(malformed, "doi", Result.MATCHED, at="2026-08-16")


@pytest.mark.parametrize(
    "event",
    [
        {"check": "doi"},
        {"by": 7, "at": "2026-08-16", "check": "doi"},
        {"by": "human:eran", "at": "2026-02-30", "check": "doi"},
        {"by": "", "at": "2026-08-16", "check": "doi"},
    ],
    ids=["check-only", "wrong-type", "invalid-date", "empty"],
)
def test_invalid_event_rows_never_elevate_trust_or_survive_reads(event):
    data, body = frontmatter.parse(_machine_confirmed_text())
    data["verified"].append(event)
    malformed = frontmatter.serialize(data) + body

    assert events.verified_checks(malformed) == []
    assert events.trust_tier(malformed) == "unverified"
    with pytest.raises(ValueError, match="verified"):
        events.record_pass(malformed, "doi", Result.MATCHED, at="2026-08-17")


def test_checkless_by_at_event_is_valid_and_elevates_to_human_reviewed():
    """OKF's own `verified` shape (a `{by, at}` mapping with no `check`) is a
    valid foreign event per the read-path contract, not a malformed row. On
    top of an already machine-confirmed note it counts toward the human:
    actor test and elevates the tier."""
    data, body = frontmatter.parse(_machine_confirmed_text())
    data["verified"].append({"by": "human:eran", "at": "2026-08-16"})
    text = frontmatter.serialize(data) + body

    assert len(events.verified_checks(text)) == len(data["verified"])
    assert events.trust_tier(text) == "human-reviewed"


def test_historical_pass_is_demoted_by_current_failure_and_recovers_on_match():
    """``update-notice`` is applicable (BASE carries a DOI), so a current
    failure on it demotes trust — unlike the retired ``doi``/``metadata``
    checks, which no longer sit in the applicable set at all."""
    confirmed = _machine_confirmed_text()

    failed = events.record_failure(confirmed, "update-notice", Result.UNMATCHED)

    assert events.trust_tier(failed) == "unverified"
    assert events.current_failures(failed) == [
        {"check": "update-notice", "result": "UNMATCHED"}
    ]
    assert events.verified_checks(failed) == events.verified_checks(confirmed)

    recovered = events.record_pass(
        failed, "update-notice", Result.MATCHED, at="2026-08-17"
    )

    assert events.current_failures(recovered) == []
    assert events.trust_tier(recovered) == "machine-confirmed"
    assert (
        len(events.verified_checks(recovered))
        == len(events.verified_checks(confirmed)) + 1
    )


def test_match_clears_only_exact_current_failure_identity():
    confirmed = _machine_confirmed_text()
    quote_check = "quote:smith2020#^c-11111111:managed-region"
    failed = events.record_failure(confirmed, "doi", Result.UNMATCHED)
    failed = events.record_failure(failed, quote_check, Result.UNREACHABLE)

    doi_recovered = events.record_pass(failed, "doi", Result.MATCHED, at="2026-08-17")

    assert events.current_failures(doi_recovered) == [
        {"check": quote_check, "result": "UNREACHABLE"}
    ]
    assert events.trust_tier(doi_recovered) == "unverified"


def test_failure_projection_is_sorted_idempotent_and_rejects_malformed_state():
    first = events.record_failure(BASE, "update-notice", Result.UNREACHABLE)
    second = events.record_failure(first, "doi", Result.UNMATCHED)
    repeated = events.record_failure(second, "doi", Result.UNMATCHED)

    assert repeated == second
    assert events.current_failures(second) == [
        {"check": "doi", "result": "UNMATCHED"},
        {"check": "update-notice", "result": "UNREACHABLE"},
    ]

    data, body = frontmatter.parse(second)
    data["failed-verification"] = [{"check": "doi"}]
    malformed = frontmatter.serialize(data) + body
    original = malformed.encode()
    with pytest.raises(ValueError, match="failed-verification"):
        events.record_failure(malformed, "doi", Result.UNMATCHED)
    assert malformed.encode() == original


@pytest.mark.parametrize(
    ("check", "at"),
    [
        ("doi", "2026-02-30"),
        ("doi", ""),
        ("doi\nother", "2026-08-16"),
    ],
)
def test_record_pass_rejects_invalid_new_event_fields(check, at):
    with pytest.raises(ValueError, match="must be"):
        events.record_pass(BASE, check, Result.MATCHED, by="human:eran", at=at)


@pytest.mark.parametrize("field", ["verified", "failed-verification"])
def test_duplicate_verifier_state_headers_fail_closed(field):
    rows = (
        '  - {by: "human:eran", at: "2026-08-16", check: "doi"}\n'
        if field == "verified"
        else '  - {check: "doi", result: "UNMATCHED"}\n'
    )
    text = f"---\n{field}:\n{rows}{field}:\n{rows}---\nbody\n"

    assert events.verified_checks(text) == []
    assert events.current_failures(text) == []
    assert events.trust_tier(text) == "unverified"
    with pytest.raises(ValueError, match=field):
        events.record_pass(text, "doi", Result.MATCHED, at="2026-08-17")


def test_duplicate_keys_inside_verified_event_fail_closed():
    confirmed = _machine_confirmed_text()
    malformed = must_replace(
        confirmed, 'check: "doi"}', 'check: "metadata", check: "doi"}'
    )

    assert events.verified_checks(malformed) == []
    assert events.trust_tier(malformed) == "unverified"
    with pytest.raises(ValueError, match="verified"):
        events.record_pass(malformed, "doi", Result.MATCHED, at="2026-08-17")
    with pytest.raises(ValueError, match="verified"):
        events.record_failure(malformed, "doi", Result.UNMATCHED)


def test_duplicate_keys_inside_current_failure_fail_closed():
    failed = events.record_failure(_machine_confirmed_text(), "doi", Result.UNMATCHED)
    malformed = must_replace(
        failed,
        'check: "doi", result: "UNMATCHED"}',
        'check: "metadata", check: "doi", result: "UNMATCHED"}',
    )

    assert events.current_failures(malformed) == []
    assert events.trust_tier(malformed) == "unverified"
    with pytest.raises(ValueError, match="failed-verification"):
        events.record_pass(malformed, "doi", Result.MATCHED, at="2026-08-17")
    with pytest.raises(ValueError, match="failed-verification"):
        events.record_failure(malformed, "doi", Result.UNMATCHED)


@pytest.mark.parametrize("field", ["verified", "failed-verification"])
def test_duplicate_scalar_and_list_verifier_headers_fail_closed(field):
    text = _machine_confirmed_text()
    if field == "failed-verification":
        text = events.record_failure(text, "doi", Result.UNMATCHED)
    malformed = must_replace(text, f"{field}:\n", f'{field}: "shadow"\n{field}:\n')

    assert events.trust_tier(malformed) == "unverified"
    with pytest.raises(ValueError, match=field):
        events.record_pass(malformed, "doi", Result.MATCHED, at="2026-08-17")


def test_bare_verified_mapping_is_one_element_list():
    text = (
        '---\ntype: "literature"\n'
        'verified: {by: "human:eran", at: "2026-08-02T09:00:00Z"}\n---\nbody\n'
    )
    data, _ = frontmatter.parse(text)
    events_list, malformed = events._verified_events(data)
    assert not malformed
    assert len(events_list) == 1


def test_foreign_by_at_event_does_not_poison_the_list():
    data = {
        "verified": [
            {"by": "human:eran", "at": "2026-08-02T09:00:00Z"},
            {"by": "research_vault/0.1.0", "at": "2026-09-01", "check": "doi"},
        ]
    }
    events_list, malformed = events._verified_events(data)
    assert not malformed
    assert len(events_list) == 2


def test_foreign_human_event_without_check_stays_unverified():
    # Trust tiers are cumulative (unverified -> machine-confirmed ->
    # human-reviewed): human-reviewed only applies on top of a
    # machine-confirmed note. A note whose only verified event is a
    # check-less foreign `human:` mapping has no deterministic check
    # coverage at all, so it cannot be machine-confirmed, and therefore
    # cannot be human-reviewed either -- it stays "unverified".
    text = (
        '---\ncitationKey: "noid2020"\ntype: "literature"\n'
        'verified: {by: "human:eran", at: "2026-08-02T09:00:00Z"}\n---\nbody\n'
    )
    assert events.trust_tier(text) == "unverified"


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({"DOI": "10.1000/xyz"}, {"update-notice"}),
        ({"doi": "10.1000/xyz"}, {"update-notice"}),
        ({"extra": ["PMID: 28503678", "PMCID: PMC5428074"]}, {"update-notice"}),
        ({"extra": "PMID: 28503678"}, {"update-notice"}),
        ({"title": "no identifiers"}, set()),
    ],
)
def test_applicable_note_checks_is_update_notice_or_nothing(data, expected):
    assert events._applicable_note_checks(data) == expected
