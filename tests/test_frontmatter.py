import pytest

from knowledge_harness import frontmatter

SAMPLE = {
    "citekey": "smith2020",
    "type": "literature",
    "doi": "10.1000/xyz",
    "accessed": "2026-08-16",
    "fixity-sha256": ["aa11", "bb22"],
    "status": "unscreened",
    "verified": [
        {"by": "knowledge_harness/0.1.0", "at": "2026-08-16", "check": "doi"},
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
    assert '- {by: "knowledge_harness/0.1.0", at: "2026-08-16", check: "doi"}' in text


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
            "by": "knowledge_harness/0.1.0",
            "at": "2026-08-20T12:34:56Z",
        }
    }

    text = frontmatter.serialize(data)
    parsed, _ = frontmatter.parse(text)

    assert (
        'generated: {by: "knowledge_harness/0.1.0", at: "2026-08-20T12:34:56Z"}' in text
    )
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


# --- `render_field`: the one spelling of a frontmatter line -----------------
# `archive.set_archive_url` and `archive._bump_generated` are byte-surgical
# single-field writers that share this with `serialize`, so it had no direct
# test of its own before this round even though `serialize` exercised it
# indirectly.


def test_render_field_renders_a_scalar():
    assert frontmatter.render_field("citekey", "smith2020") == 'citekey: "smith2020"'


def test_render_field_renders_an_int_scalar():
    assert frontmatter.render_field("count", 3) == "count: 3"


def test_render_field_renders_a_one_level_mapping():
    line = frontmatter.render_field(
        "generated", {"by": "knowledge_harness/0.1.0", "at": "2026-08-20T12:34:56Z"}
    )
    assert (
        line == 'generated: {by: "knowledge_harness/0.1.0", at: "2026-08-20T12:34:56Z"}'
    )


def test_render_field_round_trips_through_parse():
    mapping = {"by": "knowledge_harness/0.1.0", "at": "2026-08-20T12:34:56Z"}
    line = frontmatter.render_field("generated", mapping)

    data, _ = frontmatter.parse(f"---\n{line}\n---\n")

    assert data["generated"] == mapping


def test_render_field_matches_serialize_for_the_same_key_and_value():
    """A standalone `render_field` call and `serialize`'s own line for the
    identical key/value must be byte-identical — the one spelling a byte-
    surgical single-field writer and a full re-render must never drift apart
    into two different formats.
    """
    mapping = {"by": "knowledge_harness/0.1.0", "at": "2026-08-20T12:34:56Z"}
    standalone = frontmatter.render_field("generated", mapping)
    from_serialize = next(
        line
        for line in frontmatter.serialize({"generated": mapping}).splitlines()
        if line.startswith("generated:")
    )
    assert standalone == from_serialize


def test_render_field_mapping_matches_the_same_mapping_as_a_list_item():
    """The inline-dict grammar has one spelling, shared by a top-level
    `key: {...}` field and a `  - {...}` list item.
    """
    mapping = {"by": "knowledge_harness/0.1.0", "at": "2026-08-16", "check": "doi"}
    field_line = frontmatter.render_field("verified", mapping)
    field_inner = field_line.split(": ", 1)[1]
    list_line = frontmatter.serialize({"verified": [mapping]}).splitlines()[2]
    assert list_line == f"  - {field_inner}"
