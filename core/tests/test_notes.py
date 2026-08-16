import pytest

from harness_core import frontmatter, notes


ITEM = {"id": "smith2020", "type": "article-journal", "title": "Mortality decline",
        "DOI": "10.1000/xyz"}


def test_note_path(tmp_vault):
    assert notes.note_path(tmp_vault, "smith2020").as_posix().endswith(
        "literatures/smith2020.md")


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
    assert notes.MANAGED_OPEN in body and notes.MANAGED_CLOSE in body
    assert body.rstrip().endswith("## Notes")


def test_free_region_survives_rerender():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    edited = v1 + "my own prose [[link]] under the markers\n"
    v2 = notes.render_note(ITEM, ["aa11", "bb22"], [], existing=edited,
                           retrieved="2026-08-17")
    assert "my own prose [[link]] under the markers" in v2
    data, _ = frontmatter.parse(v2)
    assert data["retrieved"] == "2026-08-16"          # day-one value preserved
    assert data["attachment-sha256"] == ["aa11", "bb22"]  # managed metadata updated


def test_rerender_idempotent():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    v2 = notes.render_note(ITEM, ["aa11"], [], existing=v1, retrieved="2026-08-16")
    assert v1 == v2


def test_unowned_frontmatter_fields_survive_rerender():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    data, body = frontmatter.parse(v1)
    data["verified"] = [{"by": "harness_core/0.1.0", "at": "2026-08-16", "check": "doi"}]
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
    v2 = notes.render_note(ITEM, ["aa11"], [], existing=with_blanks, retrieved="2026-08-16")
    assert v2.endswith("\n## Notes\n\n\n\nspaced prose\n")
    emptied = v2[: v2.index(notes.MANAGED_CLOSE) + len(notes.MANAGED_CLOSE) + 1]
    v3 = notes.render_note(ITEM, ["aa11"], [], existing=emptied, retrieved="2026-08-16")
    assert v3.endswith(notes.MANAGED_CLOSE + "\n")   # emptied region stays empty


QUOTE_ANN = {"key": "ANNKEY01", "type": "highlight", "citekey": "smith2020",
             "annotationText": "Mortality fell 12% (95% CI 8-16).",
             "comment": "", "pageLabel": "12",
             "context_prefix": "the cohort showed that ",
             "context_suffix": " across all strata studied"}

COMMENT_ANN = {"key": "ANNKEY02", "type": "note", "citekey": "smith2020",
               "annotationText": "", "comment": "Design is retrospective only",
               "pageLabel": "3"}


def test_claim_id_stable_from_key():
    a = notes.claim_id(QUOTE_ANN)
    b = notes.claim_id(dict(QUOTE_ANN, annotationText="edited text"))
    assert a == b                      # key wins over text
    assert a.startswith("c-") and len(a) == 10


def test_claim_id_from_text_when_no_key():
    ann = dict(QUOTE_ANN, key=None)
    a = notes.claim_id(ann)
    b = notes.claim_id(dict(ann, annotationText="Mortality  fell 12% (95% CI 8-16)."))
    assert a == b                      # whitespace-normalized


def test_render_quote_claim():
    out = notes.render_claim(QUOTE_ANN)
    lines = out.split("\n")
    cid = notes.claim_id(QUOTE_ANN)
    assert lines[0] == f"- (quote) [@smith2020, p. 12] ^{cid}"
    assert lines[1] == "  > Mortality fell 12% (95% CI 8-16)."
    assert lines[2] == \
        '  <!-- hk-sel prefix="the cohort showed that " ' \
        'suffix=" across all strata studied" -->'


def test_rerender_ignores_close_marker_inside_annotation_text():
    ann = dict(QUOTE_ANN, annotationText=notes.MANAGED_CLOSE)
    v1 = notes.render_note(ITEM, ["aa11"], [ann], existing=None,
                           retrieved="2026-08-16")
    edited = v1 + "\n\nfree tail with exact bytes\r\n"
    v2 = notes.render_note(ITEM, ["aa11"], [ann], existing=edited,
                           retrieved="2026-08-16")
    assert v2 == edited


def test_render_multiline_quote_prefixes_every_line():
    ann = dict(QUOTE_ANN, annotationText="first line\n\nthird line",
               context_prefix="", context_suffix="")
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
    assert out.split("\n")[0] == \
        f"- (paraphrase) Design is retrospective only [@smith2020, p. 3] ^{cid}"


def test_render_multiline_comment_collapses_whitespace():
    ann = dict(COMMENT_ANN, comment="  Design is\nretrospective\t only  ")
    cid = notes.claim_id(ann)
    assert notes.render_claim(ann) == \
        f"- (paraphrase) Design is retrospective only [@smith2020, p. 3] ^{cid}"


def test_selector_values_are_html_escaped():
    ann = dict(QUOTE_ANN,
               context_prefix='lead "quoted" & -->',
               context_suffix='tail "quoted" & -->')
    selector = notes.render_claim(ann).split("\n")[-1]
    assert selector == \
        '  <!-- hk-sel prefix="lead &quot;quoted&quot; &amp; --&gt;" ' \
        'suffix="tail &quot;quoted&quot; &amp; --&gt;" -->'


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


def test_sha256_file(tmp_path):
    f = tmp_path / "x.pdf"
    f.write_bytes(b"pdfbytes")
    assert len(notes.sha256_file(f)) == 64
