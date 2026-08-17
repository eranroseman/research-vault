import pytest

from harness_core import frontmatter, notes

ITEM = {
    "id": "smith2020",
    "type": "article-journal",
    "title": "Mortality decline",
    "DOI": "10.1000/xyz",
}


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
    text = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    data, body = frontmatter.parse(text)
    assert data["citekey"] == "smith2020"
    assert data["type"] == "literature"
    assert data["doi"] == "10.1000/xyz"
    assert data["retrieved"] == "2026-08-16"
    assert data["attachment-sha256"] == ["aa11"]
    assert data["status"] == "unreviewed"
    assert data["aliases"] == ["Mortality decline"]
    assert notes.MANAGED_OPEN in body
    assert notes.MANAGED_CLOSE in body
    assert body.rstrip().endswith("## Notes")


def test_free_region_survives_rerender():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    edited = v1 + "my own prose [[link]] under the markers\n"
    v2 = notes.render_note(
        ITEM, ["aa11", "bb22"], [], existing=edited, retrieved="2026-08-17"
    )
    assert "my own prose [[link]] under the markers" in v2
    data, _ = frontmatter.parse(v2)
    assert data["retrieved"] == "2026-08-16"  # day-one value preserved
    assert data["attachment-sha256"] == ["aa11", "bb22"]  # managed metadata updated


def test_rerender_idempotent():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    v2 = notes.render_note(ITEM, ["aa11"], [], existing=v1, retrieved="2026-08-16")
    assert v1 == v2


def test_unowned_frontmatter_fields_survive_rerender():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    data, body = frontmatter.parse(v1)
    data["verified"] = [
        {"by": "harness_core/0.1.0", "at": "2026-08-16", "check": "doi"}
    ]
    data["superseded-by"] = "smith2024"
    data["authority"] = "peer-reviewed journal"
    data["archive-url"] = "https://web.archive.org/web/x"
    edited = frontmatter.serialize(data) + body
    v2 = notes.render_note(ITEM, ["aa11"], [], existing=edited, retrieved="2026-08-17")
    kept, _ = frontmatter.parse(v2)
    assert kept["verified"] == data["verified"]
    assert kept["superseded-by"] == "smith2024"
    assert kept["authority"] == "peer-reviewed journal"
    assert kept["archive-url"] == "https://web.archive.org/web/x"


def test_free_region_byte_exact():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    with_blanks = v1 + "\n\n\nspaced prose\n"
    v2 = notes.render_note(
        ITEM, ["aa11"], [], existing=with_blanks, retrieved="2026-08-16"
    )
    assert v2.endswith("\n## Notes\n\n\n\nspaced prose\n")
    emptied = v2[: v2.index(notes.MANAGED_CLOSE) + len(notes.MANAGED_CLOSE) + 1]
    v3 = notes.render_note(ITEM, ["aa11"], [], existing=emptied, retrieved="2026-08-16")
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
    v1 = notes.render_note(ITEM, ["aa11"], [ann], existing=None, retrieved="2026-08-16")
    edited = v1 + "\n\nfree tail with exact bytes\r\n"
    v2 = notes.render_note(
        ITEM, ["aa11"], [ann], existing=edited, retrieved="2026-08-16"
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
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    identical = notes.render_note(
        ITEM, ["aa11"], [], existing=v1, retrieved="2026-08-17"
    )
    changed = notes.render_note(
        {**ITEM, "title": "Updated title"},
        ["aa11"],
        [],
        existing=v1,
        retrieved="2026-08-17",
    )

    assert notes.content_changed(v1, identical) is False
    assert notes.content_changed(v1, changed) is True
    assert notes.content_changed(None, identical) is True


def test_canonical_content_excludes_only_valid_verifier_owned_surfaces():
    base = """---
citekey: "x"
verified:
  - {by: "bot", at: "2026-08-16", check: "doi"}
status: "active"
---
- (quote) text [verify-failed:: quote/2026-08-16] ^c-1
plain [verify-failed:: quote/2026-08-16]
"""
    changed_events = base.replace('check: "doi"', 'check: "metadata"')
    changed_marker = base.replace("quote/2026-08-16", "quote/2026-08-17", 1)
    deprecated = base.replace('status: "active"', 'status: "deprecated"')

    assert notes.canonical_content(base) == notes.canonical_content(changed_events)
    assert notes.canonical_content(base) == notes.canonical_content(changed_marker)
    assert notes.content_changed(base, changed_events) is False
    assert notes.content_changed(base, deprecated) is True
    assert "plain [verify-failed" in notes.canonical_content(base)


def test_canonical_content_keeps_malformed_verified_scalar_and_marker_lookalike():
    text = """---
verified: "not-a-list"
---
- (quote) text [verify-failed:: bad date] ^c-1
"""
    assert notes.canonical_content(text) == text


def test_canonical_content_keeps_mixed_verified_list_byte_for_byte():
    text = """---
verified:
  - {by: "bot", at: "2026-08-16", check: "doi"}
  - "not-an-event"
---
- (quote) live [verify-failed:: quote/2026-08-16] ^c-1
"""

    canonical = notes.canonical_content(text)

    assert '  - "not-an-event"\n' in canonical
    assert "live [verify-failed" not in canonical


def test_deprecation_transition_fields_are_all_substantive():
    base = """---
citekey: "x"
status: "active"
deprecated-at: ""
deprecated-by: ""
reason: ""
---
body
"""
    transitions = [
        base.replace('status: "active"', 'status: "deprecated"'),
        base.replace('deprecated-at: ""', 'deprecated-at: "2026-08-16"'),
        base.replace('deprecated-by: ""', 'deprecated-by: "human:eran"'),
        base.replace('reason: ""', 'reason: "superseded source"'),
    ]

    assert all(notes.content_changed(base, changed) for changed in transitions)


def test_canonical_content_preserves_markers_in_frontmatter_prose_fences_and_continuations():
    text = """---
verified: "not-a-list"
marker: "[verify-failed:: quote/2026-08-16]"
---
prose [verify-failed:: quote/2026-08-16]
```md
- (quote) code [verify-failed:: quote/2026-08-16] ^c-1
```
- (quote) live [verify-failed:: quote/2026-08-16] ^c-2
  > continuation [verify-failed:: quote/2026-08-16]
"""
    canonical = notes.canonical_content(text)
    assert 'marker: "[verify-failed:: quote/2026-08-16]"' in canonical
    assert "prose [verify-failed" in canonical
    assert "code [verify-failed" in canonical
    assert "continuation [verify-failed" in canonical
    assert "live [verify-failed" not in canonical


def test_canonical_content_preserves_crlf_and_unterminated_frontmatter():
    text = '---\r\nverified:\r\n  - {by: "bot"}\r\n---\r\n- (quote) x [verify-failed:: quote/2026-08-16] ^c-1\r\n'
    assert "\r\n" in notes.canonical_content(text)
    malformed = (
        '---\nverified:\n  - {by: "bot"}\n'
        "- (quote) unterminated [verify-failed:: quote/2026-08-16] ^c-1\n"
    )
    assert notes.canonical_content(malformed) == malformed


def test_canonical_content_keeps_fenced_marker_rows_until_matching_closure():
    text = """~~~markdown
- (quote) tilde [verify-failed:: quote/2026-08-16] ^c-1
```
- (quote) mismatched [verify-failed:: quote/2026-08-16] ^c-2
~~
- (quote) short [verify-failed:: quote/2026-08-16] ^c-3
~~~~
- (quote) live [verify-failed:: quote/2026-08-16] ^c-4
"""

    canonical = notes.canonical_content(text)

    assert canonical == text.replace("live [verify-failed:: quote/2026-08-16]", "live")
    assert "live [verify-failed:: quote/2026-08-16]" not in canonical


def test_canonical_content_preserves_short_fence_lookalike_outside_a_fence():
    text = "~~\nprose [verify-failed:: quote/2026-08-16]\n"

    assert notes.canonical_content(text) == text


def test_canonical_content_removes_multiple_terminal_markers_only():
    text = (
        "- (quote) anchored [verify-failed:: quote/2026-08-16] "
        "[verify-failed:: citekey/2026-08-17] ^c-1\n"
        "- (paraphrase) unanchored [verify-failed:: quote/2026-08-16] "
        "[verify-failed:: citekey/2026-08-17]\n"
    )

    assert notes.canonical_content(text) == (
        "- (quote) anchored ^c-1\n- (paraphrase) unanchored\n"
    )


def test_sha256_file(tmp_path):
    f = tmp_path / "x.pdf"
    f.write_bytes(b"pdfbytes")
    assert len(notes.sha256_file(f)) == 64
