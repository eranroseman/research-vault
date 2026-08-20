import pytest

from harness_core import Result, events, frontmatter, notes

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
        "by": "harness_core/0.1.0",
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
    data["generated"] = {"by": "harness_core/0.1.0"}
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
    ["", "../escape", "/tmp/escape", "..\\escape", "nested/escape"],
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
        {"by": "harness_core/0.1.0", "at": "2026-08-16", "check": "doi"}
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
verification-failures:
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
    with pytest.raises(ValueError, match="verification-failures"):
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
verification-failures:
  - {check: "doi", result: "UNMATCHED"}
verification-failures:
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
    with pytest.raises(ValueError, match="verification-failures"):
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


def test_render_quote_claim():
    out = notes.render_claim(QUOTE_ANN)
    lines = out.split("\n")
    cid = notes.claim_id(QUOTE_ANN)
    assert lines[0] == f"- (quote) [@smith2020, p. 12] ^{cid}"
    assert lines[1] == "  > Mortality fell 12% (95% CI 8-16)."
    assert (
        lines[2] == '  <!-- hk-sel prefix="the cohort showed that " '
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
        selector == '  <!-- hk-sel prefix="lead &quot;quoted&quot; &amp; --&gt;" '
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
        '  <!-- hk-sel prefix="lead&#13;&#10;quoted" suffix="tail&#10;quoted" -->'
    )


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
