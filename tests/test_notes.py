import datetime
import hashlib
import re

import pytest

from knowledge_harness import AGENT_ACTOR, Result, events, frontmatter, notes

ITEM = {
    "id": "smith2020",
    "type": "article-journal",
    "title": "Mortality decline",
    "DOI": "10.1000/xyz",
}

GENERATED_AT = "2026-08-20T12:34:56Z"
LATER_GENERATED_AT = "2026-08-21T01:02:03Z"


def test_fresh_note_uses_okf_literature_metadata():
    text = notes.render_note(
        ITEM,
        ["aa11"],
        [],
        existing=None,
        accessed="2026-08-20",
        generated_at=GENERATED_AT,
    )

    data, _ = frontmatter.parse(text)

    assert data["accessed"] == "2026-08-20"
    assert data["fixity-sha256"] == ["aa11"]
    assert data["status"] == "unscreened"
    assert data["generated"] == {
        "by": "knowledge_harness/0.1.0",
        "at": GENERATED_AT,
    }


def test_generated_at_changes_only_with_renderer_owned_projection():
    first = notes.render_note(
        ITEM,
        ["aa11"],
        [],
        existing=None,
        accessed="2026-08-20",
        generated_at=GENERATED_AT,
    )

    identical = notes.render_note(
        ITEM,
        ["aa11"],
        [],
        existing=first,
        accessed="2026-08-21",
        generated_at=LATER_GENERATED_AT,
    )
    changed = notes.render_note(
        ITEM,
        ["aa11", "bb22"],
        [],
        existing=first,
        accessed="2026-08-21",
        generated_at=LATER_GENERATED_AT,
    )

    assert identical == first
    unchanged_data, _ = frontmatter.parse(identical)
    changed_data, _ = frontmatter.parse(changed)
    assert unchanged_data["accessed"] == "2026-08-20"
    assert unchanged_data["generated"]["at"] == GENERATED_AT
    assert changed_data["generated"]["at"] == LATER_GENERATED_AT


def test_rerender_repairs_incomplete_generation_metadata_with_injected_time():
    first = notes.render_note(
        ITEM,
        ["aa11"],
        [],
        existing=None,
        accessed="2026-08-20",
        generated_at=GENERATED_AT,
    )
    data, body = frontmatter.parse(first)
    data["generated"] = {"by": "knowledge_harness/0.1.0"}
    incomplete = frontmatter.serialize(data) + body

    repaired = notes.render_note(
        ITEM,
        ["aa11"],
        [],
        existing=incomplete,
        accessed="2026-08-21",
        generated_at=LATER_GENERATED_AT,
    )

    repaired_data, _ = frontmatter.parse(repaired)
    assert repaired_data["generated"]["at"] == LATER_GENERATED_AT


def test_optional_okf_fields_pass_through_without_becoming_defaults():
    first = notes.render_note(
        ITEM,
        ["aa11"],
        [],
        existing=None,
        accessed="2026-08-20",
        generated_at=GENERATED_AT,
    )
    data, body = frontmatter.parse(first)
    assert "description" not in data
    assert "stale_after" not in data
    data["description"] = "A durable description"
    data["stale_after"] = "2026-09-20T00:00:00Z"

    rerendered = notes.render_note(
        ITEM,
        ["aa11"],
        [],
        existing=frontmatter.serialize(data) + body,
        accessed="2026-08-21",
        generated_at=LATER_GENERATED_AT,
    )

    kept, _ = frontmatter.parse(rerendered)
    assert kept["description"] == "A durable description"
    assert kept["stale_after"] == "2026-09-20T00:00:00Z"
    assert kept["generated"]["at"] == GENERATED_AT


def test_generated_metadata_is_substantive_canonical_content():
    first = notes.render_note(
        ITEM,
        ["aa11"],
        [],
        existing=None,
        accessed="2026-08-20",
        generated_at=GENERATED_AT,
    )
    changed = first.replace(GENERATED_AT, LATER_GENERATED_AT)

    assert notes.content_changed(first, changed)


def test_note_path(tmp_vault):
    assert (
        notes.note_path(tmp_vault, "smith2020")
        .as_posix()
        .endswith("literatures/smith2020.md")
    )


@pytest.mark.parametrize(
    "citekey",
    # An absolute-path ESCAPE fixture: the value is a citekey that note_path must
    # reject, never a temporary file this test writes to.
    ["", "../escape", "/tmp/escape", "..\\escape", "nested/escape"],  # noqa: S108
)
def test_note_path_rejects_unsafe_citekeys(tmp_vault, citekey):
    with pytest.raises(notes.InvalidCitekeyError):
        notes.note_path(tmp_vault, citekey)


def test_fresh_note_shape():
    text = notes.render_note(ITEM, ["aa11"], [], existing=None, accessed="2026-08-16")
    data, body = frontmatter.parse(text)
    assert data["citekey"] == "smith2020"
    assert data["type"] == "literature"
    assert data["doi"] == "10.1000/xyz"
    assert data["accessed"] == "2026-08-16"
    assert data["fixity-sha256"] == ["aa11"]
    assert data["status"] == "unscreened"
    assert data["aliases"] == ["Mortality decline"]
    assert notes.MANAGED_OPEN in body
    assert notes.MANAGED_CLOSE in body
    assert body.rstrip().endswith("## Notes")


def test_free_region_survives_rerender():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, accessed="2026-08-16")
    edited = v1 + "my own prose [[link]] under the markers\n"
    v2 = notes.render_note(
        ITEM, ["aa11", "bb22"], [], existing=edited, accessed="2026-08-17"
    )
    assert "my own prose [[link]] under the markers" in v2
    data, _ = frontmatter.parse(v2)
    assert data["accessed"] == "2026-08-16"  # day-one value preserved
    assert data["fixity-sha256"] == ["aa11", "bb22"]  # managed metadata updated


def test_rerender_idempotent():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, accessed="2026-08-16")
    v2 = notes.render_note(ITEM, ["aa11"], [], existing=v1, accessed="2026-08-16")
    assert v1 == v2


def test_unowned_frontmatter_fields_survive_rerender():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, accessed="2026-08-16")
    data, body = frontmatter.parse(v1)
    data["verified"] = [
        {"by": "knowledge_harness/0.1.0", "at": "2026-08-16", "check": "doi"}
    ]
    data["superseded-by"] = "smith2024"
    data["authority"] = "peer-reviewed journal"
    data["archive-url"] = "https://web.archive.org/web/x"
    edited = frontmatter.serialize(data) + body
    v2 = notes.render_note(ITEM, ["aa11"], [], existing=edited, accessed="2026-08-17")
    kept, _ = frontmatter.parse(v2)
    assert kept["verified"] == data["verified"]
    assert kept["superseded-by"] == "smith2024"
    assert kept["authority"] == "peer-reviewed journal"
    assert kept["archive-url"] == "https://web.archive.org/web/x"


def test_rerender_preserves_duplicate_key_verified_as_rejected_evidence():
    existing = notes.render_note(
        ITEM, ["aa11"], [], existing=None, accessed="2026-08-16"
    )
    verifier_state = """verified:
  - {by: "bot", at: "2026-08-16", check: "metadata", check: "doi"}
  - {by: "bot", at: "2026-08-16", check: "metadata"}
  - {by: "bot", at: "2026-08-16", check: "update-notice"}
"""
    malformed = existing.replace(
        f"---\n{notes.MANAGED_OPEN}",
        f"{verifier_state}---\n{notes.MANAGED_OPEN}",
        1,
    )

    assert events.verified_checks(malformed) == []
    assert events.trust_tier(malformed) == "unverified"

    rerendered = notes.render_note(
        {**ITEM, "title": "Revised title"},
        ["aa11"],
        [],
        existing=malformed,
        accessed="2026-08-17",
        generated_at="2026-08-17T00:00:00Z",
    )

    assert notes.content_changed(malformed, rerendered) is True
    assert events.verified_checks(rerendered) == []
    assert events.trust_tier(rerendered) == "unverified"
    with pytest.raises(ValueError, match="verified"):
        events.record_failure(rerendered, "doi", Result.UNMATCHED)


def test_rerender_preserves_duplicate_key_failures_as_rejected_evidence():
    existing = notes.render_note(
        ITEM, ["aa11"], [], existing=None, accessed="2026-08-16"
    )
    verifier_state = """verified:
  - {by: "bot", at: "2026-08-16", check: "doi"}
  - {by: "bot", at: "2026-08-16", check: "metadata"}
  - {by: "bot", at: "2026-08-16", check: "update-notice"}
failed-verification:
  - {check: "doi", check: "legacy-check", result: "UNMATCHED"}
"""
    malformed = existing.replace(
        f"---\n{notes.MANAGED_OPEN}",
        f"{verifier_state}---\n{notes.MANAGED_OPEN}",
        1,
    )

    assert events.current_failures(malformed) == []
    assert events.trust_tier(malformed) == "unverified"

    rerendered = notes.render_note(
        {**ITEM, "title": "Revised title"},
        ["aa11"],
        [],
        existing=malformed,
        accessed="2026-08-17",
        generated_at="2026-08-17T00:00:00Z",
    )

    assert notes.content_changed(malformed, rerendered) is True
    assert events.current_failures(rerendered) == []
    assert events.trust_tier(rerendered) == "unverified"
    with pytest.raises(ValueError, match="failed-verification"):
        events.record_pass(rerendered, "doi", Result.MATCHED, at="2026-08-17")


def test_rerender_preserves_scalar_before_verified_list_as_rejected_evidence():
    existing = notes.render_note(
        ITEM, ["aa11"], [], existing=None, accessed="2026-08-16"
    )
    verifier_state = """verified: "shadow"
verified:
  - {by: "bot", at: "2026-08-16", check: "doi"}
  - {by: "bot", at: "2026-08-16", check: "metadata"}
  - {by: "bot", at: "2026-08-16", check: "update-notice"}
"""
    malformed = existing.replace(
        f"---\n{notes.MANAGED_OPEN}",
        f"{verifier_state}---\n{notes.MANAGED_OPEN}",
        1,
    )

    assert events.trust_tier(malformed) == "unverified"

    rerendered = notes.render_note(
        {**ITEM, "title": "Revised title"},
        ["aa11"],
        [],
        existing=malformed,
        accessed="2026-08-17",
        generated_at="2026-08-17T00:00:00Z",
    )

    assert notes.content_changed(malformed, rerendered) is True
    assert events.verified_checks(rerendered) == []
    assert events.trust_tier(rerendered) == "unverified"
    with pytest.raises(ValueError, match="verified"):
        events.record_failure(rerendered, "doi", Result.UNMATCHED)


def test_rerender_preserves_failure_list_before_empty_duplicate_as_rejected():
    existing = notes.render_note(
        ITEM, ["aa11"], [], existing=None, accessed="2026-08-16"
    )
    verifier_state = """verified:
  - {by: "bot", at: "2026-08-16", check: "doi"}
  - {by: "bot", at: "2026-08-16", check: "metadata"}
  - {by: "bot", at: "2026-08-16", check: "update-notice"}
failed-verification:
  - {check: "doi", result: "UNMATCHED"}
failed-verification:
"""
    malformed = existing.replace(
        f"---\n{notes.MANAGED_OPEN}",
        f"{verifier_state}---\n{notes.MANAGED_OPEN}",
        1,
    )

    assert events.trust_tier(malformed) == "unverified"

    rerendered = notes.render_note(
        {**ITEM, "title": "Revised title"},
        ["aa11"],
        [],
        existing=malformed,
        accessed="2026-08-17",
        generated_at="2026-08-17T00:00:00Z",
    )

    assert notes.content_changed(malformed, rerendered) is True
    assert events.current_failures(rerendered) == []
    assert events.trust_tier(rerendered) == "unverified"
    with pytest.raises(ValueError, match="failed-verification"):
        events.record_pass(rerendered, "doi", Result.MATCHED, at="2026-08-17")


def test_free_region_byte_exact():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, accessed="2026-08-16")
    with_blanks = v1 + "\n\n\nspaced prose\n"
    v2 = notes.render_note(
        ITEM, ["aa11"], [], existing=with_blanks, accessed="2026-08-16"
    )
    assert v2.endswith("\n## Notes\n\n\n\nspaced prose\n")
    emptied = v2[: v2.index(notes.MANAGED_CLOSE) + len(notes.MANAGED_CLOSE) + 1]
    v3 = notes.render_note(ITEM, ["aa11"], [], existing=emptied, accessed="2026-08-16")
    assert v3.endswith(notes.MANAGED_CLOSE + "\n")  # emptied region stays empty


def test_existing_note_without_marker_refuses_render():
    existing = "---\ntype: literature\n---\nhand-written prose, no marker\n"
    with pytest.raises(
        notes.RenderIntegrityError,
        match=r"^existing note has no managed-close marker — refusing to overwrite the body$",
    ):
        notes.render_note(ITEM, ["aa11"], [], existing=existing, accessed="2026-08-16")


@pytest.mark.parametrize("existing", [None, ""], ids=["none", "empty-string"])
def test_fresh_note_still_seeds(existing):
    text = notes.render_note(
        ITEM, ["aa11"], [], existing=existing, accessed="2026-08-16"
    )
    assert text.endswith(notes.SEED_FREE)


QUOTE_ANN = {
    "key": "ANNKEY01",
    "type": "highlight",
    "citekey": "smith2020",
    "annotationText": "Mortality fell 12% (95% CI 8-16).",
    "comment": "",
    "pageLabel": "12",
    "context_prefix": "the cohort showed that ",
    "context_suffix": " across all strata studied",
}

COMMENT_ANN = {
    "key": "ANNKEY02",
    "type": "note",
    "citekey": "smith2020",
    "annotationText": "",
    "comment": "Design is retrospective only",
    "pageLabel": "3",
}


def test_claim_id_stable_from_key():
    a = notes.claim_id(QUOTE_ANN)
    b = notes.claim_id(dict(QUOTE_ANN, annotationText="edited text"))
    assert a == b  # key wins over text
    assert a.startswith("c-")
    assert len(a) == 10


def test_claim_id_from_text_when_no_key():
    ann = dict(QUOTE_ANN, key=None)
    a = notes.claim_id(ann)
    b = notes.claim_id(dict(ann, annotationText="Mortality  fell 12% (95% CI 8-16)."))
    assert a == b  # whitespace-normalized


def test_duplicate_anchors_refuse_render():
    ann = dict(QUOTE_ANN, key=None)  # identical text -> identical anchor
    cid = notes.claim_id(ann)
    pattern = f"^{re.escape(f'duplicate claim anchors in render: {[cid, cid]!r}')}$"
    with pytest.raises(notes.RenderIntegrityError, match=pattern):
        notes.render_note(
            ITEM, ["aa11"], [ann, dict(ann)], existing=None, accessed="2026-08-16"
        )


def test_duplicate_keyless_empty_text_anchors_refuse_render():
    # Two keyless, comment-only annotations: annotationText is empty for
    # both, so claim_id hashes b"" for both regardless of comment (issue
    # #16) -> same anchor c-e3b0c442, not merely a coincidental text match.
    first = dict(COMMENT_ANN, key=None, comment="Design is retrospective only")
    second = dict(COMMENT_ANN, key=None, comment="A completely different remark")
    cid = notes.claim_id(first)
    assert cid == "c-e3b0c442"
    pattern = f"^{re.escape(f'duplicate claim anchors in render: {[cid, cid]!r}')}$"
    with pytest.raises(notes.RenderIntegrityError, match=pattern):
        notes.render_note(
            ITEM, ["aa11"], [first, second], existing=None, accessed="2026-08-16"
        )


def test_distinct_keyed_annotations_still_render():
    text = notes.render_note(
        ITEM,
        ["aa11"],
        [QUOTE_ANN, COMMENT_ANN],
        existing=None,
        accessed="2026-08-16",
    )
    assert notes.claim_id(QUOTE_ANN) != notes.claim_id(COMMENT_ANN)
    assert f"^{notes.claim_id(QUOTE_ANN)}" in text
    assert f"^{notes.claim_id(COMMENT_ANN)}" in text


def test_distinct_keyless_annotations_still_render():
    first = dict(QUOTE_ANN, key=None)
    second = dict(QUOTE_ANN, key=None, annotationText="A wholly different quote.")
    text = notes.render_note(
        ITEM, ["aa11"], [first, second], existing=None, accessed="2026-08-16"
    )
    assert notes.claim_id(first) != notes.claim_id(second)
    assert f"^{notes.claim_id(first)}" in text
    assert f"^{notes.claim_id(second)}" in text


def test_parse_mismatch_still_raises_when_anchors_are_unique(monkeypatch):
    """The duplicate-anchor guard must not shadow a genuine parse mismatch."""
    from knowledge_harness import claims as claims_mod

    real_parse_claims = claims_mod.parse_claims

    def corrupted_parse_claims(text):
        parsed = real_parse_claims(text)
        if parsed:
            parsed[0].claim_id = "c-deadbeef"
        return parsed

    monkeypatch.setattr(claims_mod, "parse_claims", corrupted_parse_claims)
    with pytest.raises(
        notes.RenderIntegrityError,
        match=r"^managed body parsed to \['c-deadbeef'\], expected \['.+'\]$",
    ):
        notes.render_note(
            ITEM, ["aa11"], [QUOTE_ANN], existing=None, accessed="2026-08-16"
        )


def test_render_quote_claim():
    out = notes.render_claim(QUOTE_ANN)
    lines = out.split("\n")
    cid = notes.claim_id(QUOTE_ANN)
    assert lines[0] == f"- (quote) [@smith2020, p. 12] ^{cid}"
    assert lines[1] == "  > Mortality fell 12% (95% CI 8-16)."
    assert (
        lines[2] == '  <!-- hk-selector prefix="the cohort showed that " '
        'suffix=" across all strata studied" -->'
    )


def test_rerender_ignores_close_marker_inside_annotation_text():
    ann = dict(QUOTE_ANN, annotationText=notes.MANAGED_CLOSE)
    v1 = notes.render_note(ITEM, ["aa11"], [ann], existing=None, accessed="2026-08-16")
    edited = v1 + "\n\nfree tail with exact bytes\r\n"
    v2 = notes.render_note(
        ITEM, ["aa11"], [ann], existing=edited, accessed="2026-08-16"
    )
    assert v2 == edited


def test_render_multiline_quote_prefixes_every_line():
    ann = dict(
        QUOTE_ANN,
        annotationText="first line\n\nthird line",
        context_prefix="",
        context_suffix="",
    )
    cid = notes.claim_id(ann)
    assert notes.render_claim(ann).split("\n") == [
        f"- (quote) [@smith2020, p. 12] ^{cid}",
        "  > first line",
        "  > ",
        "  > third line",
    ]


def test_render_comment_claim():
    out = notes.render_claim(COMMENT_ANN)
    cid = notes.claim_id(COMMENT_ANN)
    assert (
        out.split("\n")[0]
        == f"- (paraphrase) Design is retrospective only [@smith2020, p. 3] ^{cid}"
    )


def test_render_multiline_comment_collapses_whitespace():
    ann = dict(COMMENT_ANN, comment="  Design is\nretrospective\t only  ")
    cid = notes.claim_id(ann)
    assert (
        notes.render_claim(ann)
        == f"- (paraphrase) Design is retrospective only [@smith2020, p. 3] ^{cid}"
    )


def test_selector_values_are_html_escaped():
    ann = dict(
        QUOTE_ANN,
        context_prefix='lead "quoted" & -->',
        context_suffix='tail "quoted" & -->',
    )
    selector = notes.render_claim(ann).split("\n")[-1]
    assert (
        selector == '  <!-- hk-selector prefix="lead &quot;quoted&quot; &amp; --&gt;" '
        'suffix="tail &quot;quoted&quot; &amp; --&gt;" -->'
    )


def test_selector_values_escape_newlines_on_one_line():
    ann = dict(
        QUOTE_ANN,
        context_prefix="lead\r\nquoted",
        context_suffix="tail\nquoted",
    )

    selector = notes.render_claim(ann).split("\n")[-1]

    assert selector == (
        '  <!-- hk-selector prefix="lead&#13;&#10;quoted" suffix="tail&#10;quoted" -->'
    )


def test_selector_values_escape_full_control_class_on_one_line():
    # NEL (\x85), DEL (\x7f), and the Unicode line/paragraph separators are
    # not touched by html.escape() and are not among the \r/\n pair the old
    # implementation handled, but str.splitlines() (used by the claims
    # parser) treats all of them as line breaks. They are stripped rather
    # than entity-escaped like \r/\n: html.unescape (the real round-trip
    # consumer, harness_core.selectors.unescape_selector) maps a numeric
    # reference like "&#133;" to an unrelated Windows-1252 lookalike instead
    # of back to \x85, so entity-escaping them would silently corrupt
    # retained context on a future round trip. A prefix carrying NEL
    # immediately followed by claim-list-item markup must stay neutralized
    # on one physical line rather than risk being read back as a new line.
    ann = dict(
        QUOTE_ANN,
        context_prefix="lead\x85- (quote) [@evil] ^c-x",
        context_suffix="tail\x7f\u2028\u2029",
    )

    selector = notes.render_claim(ann).split("\n")[-1]

    assert selector == (
        '  <!-- hk-selector prefix="lead- (quote) [@evil] ^c-x" suffix="tail" -->'
    )


def test_render_note_round_trip_stays_quiet_with_hostile_selector_context():
    # Before the escaping hardening, this exact context_prefix (a bare NEL
    # immediately followed by "- (quote) [@evil] ^c-x") survived into the
    # rendered selector comment unescaped. The claims parser splits on NEL
    # the same way it splits on \n, so the tail forged a second, bogus claim
    # line inside the managed body and render_note's own round-trip
    # parse-back check raised RenderIntegrityError. It must now stay quiet.
    ann = dict(QUOTE_ANN, context_prefix="lead\x85- (quote) [@evil] ^c-x")

    text = notes.render_note(
        ITEM, ["aa11"], [ann], existing=None, accessed="2026-08-16"
    )

    assert "\x85" not in text


def test_content_changed_compares_complete_rendered_candidate():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, accessed="2026-08-16")
    identical = notes.render_note(
        ITEM, ["aa11"], [], existing=v1, accessed="2026-08-17"
    )
    changed = notes.render_note(
        {**ITEM, "title": "Updated title"},
        ["aa11"],
        [],
        existing=v1,
        accessed="2026-08-17",
        generated_at="2026-08-17T00:00:00Z",
    )

    assert notes.content_changed(v1, identical) is False
    assert notes.content_changed(v1, changed) is True
    assert notes.content_changed(None, identical) is True


def test_canonical_content_excludes_only_valid_verifier_owned_surfaces():
    base = """---
citekey: "x"
verified:
  - {by: "bot", at: "2026-08-16", check: "doi"}
status: "included"
---
- (quote) text [failed-verification:: quote/2026-08-16] ^c-1
plain [failed-verification:: quote/2026-08-16]
"""
    changed_events = base.replace('check: "doi"', 'check: "metadata"')
    changed_marker = base.replace("quote/2026-08-16", "quote/2026-08-17", 1)
    deprecated = base.replace('status: "included"', 'status: "deprecated"')

    assert notes.canonical_content(base) == notes.canonical_content(changed_events)
    assert notes.canonical_content(base) != notes.canonical_content(changed_marker)
    assert notes.content_changed(base, changed_events) is False
    assert notes.content_changed(base, changed_marker) is True
    assert notes.content_changed(base, deprecated) is True
    assert "plain [failed-verification" in notes.canonical_content(base)


def test_canonical_content_keeps_malformed_verified_scalar_and_marker_lookalike():
    text = """---
verified: "not-a-list"
---
- (quote) text [failed-verification:: bad date] ^c-1
"""
    assert notes.canonical_content(text) == text


def test_canonical_content_keeps_mixed_verified_list_byte_for_byte():
    text = """---
verified:
  - {by: "bot", at: "2026-08-16", check: "doi"}
  - "not-an-event"
---
- (quote) live [failed-verification:: quote/2026-08-16] ^c-1
"""

    canonical = notes.canonical_content(text)

    assert '  - "not-an-event"\n' in canonical
    assert "live [failed-verification" in canonical


def test_deprecation_transition_fields_are_all_substantive():
    base = """---
citekey: "x"
status: "included"
deprecated-at: ""
deprecated-by: ""
reason: ""
---
body
"""
    transitions = [
        base.replace('status: "included"', 'status: "deprecated"'),
        base.replace('deprecated-at: ""', 'deprecated-at: "2026-08-16"'),
        base.replace('deprecated-by: ""', 'deprecated-by: "human:eran"'),
        base.replace('reason: ""', 'reason: "superseded source"'),
    ]

    assert all(notes.content_changed(base, changed) for changed in transitions)


def test_canonical_content_preserves_markers_in_frontmatter_prose_fences_and_continuations():
    text = """---
verified: "not-a-list"
marker: "[failed-verification:: quote/2026-08-16]"
---
prose [failed-verification:: quote/2026-08-16]
```md
- (quote) code [failed-verification:: quote/2026-08-16] ^c-1
```
- (quote) live [failed-verification:: quote/2026-08-16] ^c-2
  > continuation [failed-verification:: quote/2026-08-16]
"""
    canonical = notes.canonical_content(text)
    assert 'marker: "[failed-verification:: quote/2026-08-16]"' in canonical
    assert "prose [failed-verification" in canonical
    assert "code [failed-verification" in canonical
    assert "continuation [failed-verification" in canonical
    assert "live [failed-verification" in canonical


def test_canonical_content_preserves_crlf_and_unterminated_frontmatter():
    text = '---\r\nverified:\r\n  - {by: "bot"}\r\n---\r\n- (quote) x [failed-verification:: quote/2026-08-16] ^c-1\r\n'
    assert "\r\n" in notes.canonical_content(text)
    malformed = (
        '---\nverified:\n  - {by: "bot"}\n'
        "- (quote) unterminated [failed-verification:: quote/2026-08-16] ^c-1\n"
    )
    assert notes.canonical_content(malformed) == malformed


def test_canonical_content_keeps_fenced_marker_rows_until_matching_closure():
    text = """~~~markdown
- (quote) tilde [failed-verification:: quote/2026-08-16] ^c-1
```
- (quote) mismatched [failed-verification:: quote/2026-08-16] ^c-2
~~
- (quote) short [failed-verification:: quote/2026-08-16] ^c-3
~~~~
- (quote) live [failed-verification:: quote/2026-08-16] ^c-4
"""

    canonical = notes.canonical_content(text)

    assert canonical == text


def test_canonical_content_preserves_short_fence_lookalike_outside_a_fence():
    text = "~~\nprose [failed-verification:: quote/2026-08-16]\n"

    assert notes.canonical_content(text) == text


def test_canonical_content_keeps_multiple_terminal_markers_substantive():
    text = (
        "- (quote) anchored [failed-verification:: quote/2026-08-16] "
        "[failed-verification:: citekey/2026-08-17] ^c-1\n"
        "- (paraphrase) unanchored [failed-verification:: quote/2026-08-16] "
        "[failed-verification:: citekey/2026-08-17]\n"
    )

    assert notes.canonical_content(text) == text


def test_sha256_file(tmp_path):
    f = tmp_path / "x.pdf"
    f.write_bytes(b"pdfbytes")
    assert len(notes.sha256_file(f)) == 64


@pytest.mark.parametrize(
    ("managed", "expected"),
    [
        (
            b"%%hk-managed%%\nbody\n%%/hk-managed%%\nfree",
            b"%%hk-managed%%\nbody\n%%/hk-managed%%\n",
        ),
        (
            b"%%hk-managed%%\r\nbody\r\n%%/hk-managed%%\r\nfree",
            b"%%hk-managed%%\r\nbody\r\n%%/hk-managed%%\r\n",
        ),
        (
            b"%%hk-managed%%\nbody\n%%/hk-managed%%",
            b"%%hk-managed%%\nbody\n%%/hk-managed%%",
        ),
    ],
)
def test_managed_slice_hashes_exact_delimiters_and_actual_line_endings(
    managed, expected
):
    note = b'---\ntype: "literature"\n---\n' + managed
    assert notes.managed_slice_bytes(note) == expected
    assert notes.managed_sha256(note) == hashlib.sha256(expected).hexdigest()


@pytest.mark.parametrize(
    "body",
    [
        b"body only\n",
        b"%%hk-managed%%\nbody\n",
        b"%%/hk-managed%%\n%%hk-managed%%\n",
        b"%%hk-managed%%\n%%hk-managed%%\n%%/hk-managed%%\n",
        b"%%hk-managed%%\n%%/hk-managed%%\n%%/hk-managed%%\n",
        b" %%hk-managed%%\n%%/hk-managed%%\n",
        b"%%hk-managed%% \n%%/hk-managed%%\n",
        b"%%hk-managed%%\n\t%%/hk-managed%%\n",
        b"%%hk-managed%%\vbody\n%%/hk-managed%%\n",
        b"%%hk-managed%%\nbody\n%%/hk-managed%%\v",
    ],
)
def test_managed_slice_rejects_missing_duplicate_nested_reordered_or_fuzzy_markers(
    body,
):
    with pytest.raises(notes.ManagedRegionError):
        notes.managed_slice_bytes(b"---\n---\n" + body)


def test_renderer_emits_and_preserves_exact_managed_witness():
    first = notes.render_note(
        ITEM,
        ["aa11"],
        [],
        existing=None,
        accessed="2026-08-20",
        generated_at=GENERATED_AT,
    )
    data, _ = frontmatter.parse(first)
    assert data["managed-sha256"] == notes.managed_sha256(first.encode())

    same = notes.render_note(
        ITEM,
        ["aa11"],
        [],
        existing=first,
        accessed="2026-08-21",
        generated_at=LATER_GENERATED_AT,
    )
    assert same == first

    changed = first.replace("# Mortality decline", "# Changed")
    rerendered = notes.render_note(
        {**ITEM, "title": "Changed"},
        ["aa11"],
        [],
        existing=changed,
        accessed="2026-08-21",
        generated_at=LATER_GENERATED_AT,
    )
    changed_data, _ = frontmatter.parse(rerendered)
    assert changed_data["managed-sha256"] == notes.managed_sha256(rerendered.encode())
    assert changed_data["generated"]["at"] == LATER_GENERATED_AT


@pytest.mark.parametrize(
    "witness",
    [None, 42, "", "A" * 64, "a" * 63, "g" * 64, "0" * 64],
)
def test_managed_witness_validation_rejects_missing_malformed_or_stale(witness):
    text = notes.render_note(ITEM, ["aa11"], [], existing=None, accessed="2026-08-20")
    data, body = frontmatter.parse(text)
    if witness is None:
        data.pop("managed-sha256")
    else:
        data["managed-sha256"] = witness
    invalid = (frontmatter.serialize(data) + body).encode()

    result, reason = notes.validate_managed_witness(invalid)

    assert result is Result.UNMATCHED
    assert reason.startswith("schema-violation")


@pytest.mark.parametrize("valid_last", [False, True])
def test_managed_witness_rejects_duplicate_top_level_keys_in_either_order(valid_last):
    text = notes.render_note(ITEM, ["aa11"], [], existing=None, accessed="2026-08-20")
    valid = frontmatter.parse(text)[0]["managed-sha256"]
    bad, good = 'managed-sha256: "bad"\n', f'managed-sha256: "{valid}"\n'
    duplicate = (bad + good) if valid_last else (good + bad)
    original_line = f'managed-sha256: "{valid}"\n'
    note = text.replace(original_line, duplicate, 1).encode()

    result, reason = notes.validate_managed_witness(note)

    assert result is Result.UNMATCHED
    assert reason.startswith("schema-violation")


# --- `_valid_generated`: the sole definition of `generated`'s shape --------
# The attestation guard (`lints._machine_attested`), the re-render trigger
# (`render_note`'s `projection_changed`), and `archive._bump_generated`'s
# round-trip check all bottom out in this one predicate. It had no direct
# test before this round.

# A parsed frontmatter dict from a source line with a duplicate `by`: the
# unique key set is still exactly {by, at} (so the keyset-equality clause
# alone would accept it), but the item COUNT is 3, not 2. `len(items) != 2`
# is the sole rejecter of this shape — last-value-wins `.get("by")` would
# otherwise read the second, machine-actor-looking `by` and ignore that a
# forged decoy preceded it.
_DUPLICATE_BY_LAST_WINS = frontmatter.parse(
    '---\ngenerated: {by: "human:eran", by: "knowledge_harness/0.1.0", '
    'at: "2026-08-24T00:00:00Z"}\n---\n'
)[0]["generated"]


@pytest.mark.parametrize(
    "value",
    [
        None,
        "not-a-dict",
        42,
        [],
        {"by": "knowledge_harness/0.1.0"},
        {"at": "2026-08-20T12:34:56Z"},
        {"by": "knowledge_harness/0.1.0", "at": "2026-08-20T12:34:56Z", "extra": "x"},
        {"by": "knowledge_harness/0.1.0", "when": "2026-08-20T12:34:56Z"},
        {"by": "", "at": "2026-08-20T12:34:56Z"},
        {"by": 42, "at": "2026-08-20T12:34:56Z"},
        {"by": "knowledge_harness/0.1.0", "at": 42},
        {"by": "knowledge_harness/0.1.0", "at": "not-a-timestamp"},
        {"by": "knowledge_harness/0.1.0", "at": "2026-08-20T12:34:56+00:00"},
        {"by": "knowledge_harness/0.1.0", "at": "2026-08-20"},
        _DUPLICATE_BY_LAST_WINS,
    ],
    ids=[
        "none",
        "string",
        "int",
        "empty-list",
        "missing-at",
        "missing-by",
        "extra-key",
        "wrong-key-names",
        "empty-by",
        "by-not-a-string",
        "at-not-a-string",
        "at-unparseable",
        "at-offset-not-z",
        "at-date-only",
        "duplicate-by-last-wins",
    ],
)
def test_valid_generated_rejects_every_malformed_shape(value):
    assert notes._valid_generated(value) is False


def test_valid_generated_accepts_the_one_true_shape():
    assert (
        notes._valid_generated(
            {"by": "knowledge_harness/0.1.0", "at": "2026-08-20T12:34:56Z"}
        )
        is True
    )


# --- `generated_at_now`: the one spelling of "now" --------------------------


def test_generated_at_now_output_satisfies_valid_generated():
    stamp = notes.generated_at_now()
    assert stamp.endswith("Z")
    assert "." not in stamp
    assert notes._valid_generated({"by": AGENT_ACTOR, "at": stamp}) is True


def test_generated_at_now_truncates_microseconds_and_formats_utc_offset_as_z():
    moment = datetime.datetime(2026, 8, 24, 15, 4, 5, 123456, tzinfo=datetime.UTC)

    assert notes.generated_at_now(moment) == "2026-08-24T15:04:05Z"
