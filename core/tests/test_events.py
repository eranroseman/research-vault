import pytest

from harness_core import Result, events, frontmatter

BASE = """---
citekey: "smith2020"
type: "literature"
doi: "10.1000/xyz"
---
%%hk-managed%%
- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12% across all strata.
%%/hk-managed%%

## Notes
Free-region content remains untouched.
"""

PMID_ONLY = """---
citekey: "pmid2020"
type: "literature"
pmid: "12345"
---
%%hk-managed%%
%%/hk-managed%%
"""


def test_record_pass_appends_event_and_preserves_note_contents():
    out = events.record_pass(BASE, "doi", Result.MATCHED, at="2026-08-16")

    data, body = frontmatter.parse(out)

    assert data["citekey"] == "smith2020"
    assert data["doi"] == "10.1000/xyz"
    assert (
        body
        == """%%hk-managed%%
- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12% across all strata.
%%/hk-managed%%

## Notes
Free-region content remains untouched.
"""
    )
    assert events.verified_checks(out) == [
        {"by": "harness_core/0.1.0", "at": "2026-08-16", "check": "doi"}
    ]


def test_record_pass_preserves_crlf_body_without_double_carriage_returns():
    crlf = BASE.replace("\n", "\r\n")
    out = events.record_pass(crlf, "doi", Result.MATCHED, at="2026-08-16")
    assert "\r\r\n" not in out
    assert out.endswith("Free-region content remains untouched.\r\n")


def test_record_pass_lexically_changes_only_verified_events_with_crlf():
    from harness_core import notes

    text = (
        "---\r\n"
        "citekey: smith2020\r\n"
        "status: active\r\n"
        "deprecated-at: 2026-08-16\r\n"
        "---\r\n"
        "- (quote) body ^c-11111111\r\n"
    )

    out = events.record_pass(text, "doi", Result.MATCHED, at="2026-08-17")

    assert "\r\r\n" not in out
    assert "citekey: smith2020\r\nstatus: active\r\n" in out
    assert out.endswith("- (quote) body ^c-11111111\r\n")
    assert notes.canonical_content(out) == notes.canonical_content(text)


@pytest.mark.parametrize("newline", ["\n", "\r\n"], ids=["lf", "crlf"])
def test_record_pass_owned_only_envelope_canonicalizes_to_body(newline):
    from harness_core import notes

    body = f"- (quote) body-only ^c-11111111{newline}"
    first = events.record_pass(body, "doi", Result.MATCHED, at="2026-08-16")
    second = events.record_pass(first, "metadata", Result.MATCHED, at="2026-08-17")
    with_status = first.replace(
        f"verified:{newline}", f'status: "deprecated"{newline}verified:{newline}', 1
    )

    assert first.endswith(body)
    if newline == "\r\n":
        assert "\r\r\n" not in first
        assert "\n" not in first.replace("\r\n", "")
    assert notes.canonical_content(first) == notes.canonical_content(body)
    assert notes.canonical_content(second) == notes.canonical_content(body)
    assert events.verified_checks(second) == [
        {"by": "harness_core/0.1.0", "at": "2026-08-16", "check": "doi"},
        {
            "by": "harness_core/0.1.0",
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


def test_each_managed_quote_requires_its_own_address():
    text = BASE.replace(
        "%%/hk-managed%%",
        "- (quote) [@smith2020, p. 13] ^c-22222222\n"
        "  > The decline was sustained.\n"
        "%%/hk-managed%%",
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
