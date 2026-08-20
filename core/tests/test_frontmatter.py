import pytest

from harness_core import frontmatter

SAMPLE = {
    "citekey": "smith2020",
    "type": "literature",
    "doi": "10.1000/xyz",
    "accessed": "2026-08-16",
    "fixity-sha256": ["aa11", "bb22"],
    "status": "unscreened",
    "verified": [
        {"by": "harness_core/0.1.0", "at": "2026-08-16", "check": "doi"},
    ],
    "aliases": ["Smith 2020 — Mortality decline"],
}


def test_roundtrip():
    text = frontmatter.serialize(SAMPLE) + "body line\n"
    data, body = frontmatter.parse(text)
    assert data == SAMPLE
    assert body == "body line\n"


def test_serialize_shape():
    text = frontmatter.serialize(SAMPLE)
    assert text.startswith("---\n")
    assert text.endswith("---\n")
    assert 'citekey: "smith2020"' in text
    assert "fixity-sha256:" in text
    assert '- {by: "harness_core/0.1.0", at: "2026-08-16", check: "doi"}' in text


def test_parse_no_frontmatter():
    data, body = frontmatter.parse("just a body\n")
    assert data == {}
    assert body == "just a body\n"


def test_parse_crlf_frontmatter_preserves_mixed_newline_body():
    text = frontmatter.serialize(SAMPLE).replace("\n", "\r\n")
    body = "free\r\nregion\nkept\r\n"

    data, parsed_body = frontmatter.parse(text + body)

    assert data == SAMPLE
    assert parsed_body == body


def test_quotes_in_titles_roundtrip():
    data = {"aliases": ['The "gold standard" myth'], "citekey": "x2020"}
    parsed, _ = frontmatter.parse(frontmatter.serialize(data))
    assert parsed == data


def test_inline_dict_value_with_comma_space_roundtrip():
    data = {"verified": [{"check": "title, author"}]}
    parsed, _ = frontmatter.parse(frontmatter.serialize(data))
    assert parsed == data


def test_inline_dict_value_with_colon_space_roundtrip():
    data = {"verified": [{"check": "title: author"}]}
    parsed, _ = frontmatter.parse(frontmatter.serialize(data))
    assert parsed == data


def test_inline_dict_value_with_escaped_quote_roundtrip():
    data = {"verified": [{"check": 'title "author"'}]}
    parsed, _ = frontmatter.parse(frontmatter.serialize(data))
    assert parsed == data


def test_top_level_inline_mapping_with_iso_datetime_roundtrips():
    data = {
        "generated": {
            "by": "harness_core/0.1.0",
            "at": "2026-08-20T12:34:56Z",
        }
    }

    text = frontmatter.serialize(data)
    parsed, _ = frontmatter.parse(text)

    assert 'generated: {by: "harness_core/0.1.0", at: "2026-08-20T12:34:56Z"}' in text
    assert parsed == data


def test_top_level_inline_mapping_preserves_duplicate_key_provenance():
    parsed, _ = frontmatter.parse(
        '---\ngenerated: {by: "first", by: "second", at: "2026-08-20T12:34:56Z"}\n---\n'
    )

    assert list(frontmatter._mapping_items(parsed["generated"])) == [
        ("by", "first"),
        ("by", "second"),
        ("at", "2026-08-20T12:34:56Z"),
    ]


def test_parse_rejects_nested_maps():
    bad = '---\nouter:\n  inner: "x"\n---\n'
    with pytest.raises(frontmatter.FrontmatterError):
        frontmatter.parse(bad)
