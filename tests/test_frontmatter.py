import pytest

from research_vault import frontmatter

SAMPLE = {
    "citationKey": "smith2020",
    "type": "literature",
    "doi": "10.1000/xyz",
    "accessed": "2026-08-16",
    "fixity-sha256": ["aa11", "bb22"],
    "status": "unscreened",
    "verified": [
        {"by": "research_vault/0.1.0", "at": "2026-08-16", "check": "doi"},
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
    assert 'citationKey: "smith2020"' in text
    assert "fixity-sha256:" in text
    assert '- {by: "research_vault/0.1.0", at: "2026-08-16", check: "doi"}' in text


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
    data = {"aliases": ['The "gold standard" myth'], "citationKey": "x2020"}
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
            "by": "research_vault/0.1.0",
            "at": "2026-08-20T12:34:56Z",
        }
    }

    text = frontmatter.serialize(data)
    parsed, _ = frontmatter.parse(text)

    assert 'generated: {by: "research_vault/0.1.0", at: "2026-08-20T12:34:56Z"}' in text
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
# Byte-surgical single-field writers share this with `serialize`, so it had no
# direct test of its own before this round even though `serialize` exercised it
# indirectly.


def test_render_field_renders_a_scalar():
    assert (
        frontmatter.render_field("citationKey", "smith2020")
        == 'citationKey: "smith2020"'
    )


def test_render_field_renders_an_int_scalar():
    assert frontmatter.render_field("count", 3) == "count: 3"


def test_render_field_renders_a_one_level_mapping():
    line = frontmatter.render_field(
        "generated", {"by": "research_vault/0.1.0", "at": "2026-08-20T12:34:56Z"}
    )
    assert line == 'generated: {by: "research_vault/0.1.0", at: "2026-08-20T12:34:56Z"}'


def test_render_field_round_trips_through_parse():
    mapping = {"by": "research_vault/0.1.0", "at": "2026-08-20T12:34:56Z"}
    line = frontmatter.render_field("generated", mapping)

    data, _ = frontmatter.parse(f"---\n{line}\n---\n")

    assert data["generated"] == mapping


def test_serialize_delegates_to_render_field_for_a_dict_valued_key():
    """`serialize`'s non-list branch calls `render_field` directly, so this
    pins call-site agreement rather than proving the two outputs could not
    diverge — they share one code path, not two independent ones that happen
    to agree.
    """
    mapping = {"by": "research_vault/0.1.0", "at": "2026-08-20T12:34:56Z"}
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
    mapping = {"by": "research_vault/0.1.0", "at": "2026-08-16", "check": "doi"}
    field_line = frontmatter.render_field("verified", mapping)
    field_inner = field_line.split(": ", 1)[1]
    list_line = frontmatter.serialize({"verified": [mapping]}).splitlines()[2]
    assert list_line == f"  - {field_inner}"


# --- the sourcing screen's four gaps (pre-lane-2 spec §5.1) --------------------
# python-frontmatter 1.3.0 failed every must below (measured 2026-09-17); the
# in-tree module stays, so each gap the screen found untested is pinned here.


def test_m4_serialize_is_byte_identical_for_serializer_emitted_text():
    """M4: `serialize(parse(x)[0]) == x` for text the serializer wrote — no
    quote style changes, no reflow of inline mappings or list indents, the
    trailing newline kept — and `serialize()`'s lines splice lexically into
    an existing block (events.py's list writer relies on it)."""
    data = {
        "citationKey": "smith2020",
        "title": 'The "gold standard" myth',
        "date": "2020-01-01",
        "count": 3,
        "aliases": ["Smith 2020", "2020-01-01"],
        "generated": {"by": "research_vault/0.1.0", "at": "2026-08-20T12:34:56Z"},
        "verified": [
            {"by": "research_vault/0.1.0", "at": "2026-08-16", "check": "doi"}
        ],
    }
    text = frontmatter.serialize(data)
    parsed, body = frontmatter.parse(text + "body\n")
    assert frontmatter.serialize(parsed) == text
    assert body == "body\n"
    assert text.endswith("\n")
    lines = text.splitlines()
    assert lines[0] == "---"
    assert lines[-1] == "---"
    # The lines between the fences are the exact lines a byte-surgical writer
    # splices: no line is reflowed relative to its standalone rendering.
    for key, value in data.items():
        if not isinstance(value, list):
            assert frontmatter.render_field(key, value) in lines[1:-1]


def test_m5_key_order_is_source_order_on_parse_and_insertion_order_on_dump():
    """M5: the header a reader compares order-exactly (`inbox.py`,
    `searchlog.py`) never sees keys sorted; a dict dumps in insertion order
    and parses back in source order, whatever the alphabet says."""
    data = {"zulu": "1", "alpha": "2", "mike": "3"}
    text = frontmatter.serialize(data)
    assert text.splitlines()[1:-1] == ['zulu: "1"', 'alpha: "2"', 'mike: "3"']
    parsed, _ = frontmatter.parse(text)
    assert list(parsed) == ["zulu", "alpha", "mike"]
    assert list(frontmatter._mapping_items(parsed)) == list(data.items())


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('"no"', "no"),
        ("no", "no"),
        ("yes", "yes"),
        ("1.0", "1.0"),
        ("0x1f", "0x1f"),
        ("2020-01-01", "2020-01-01"),
        ("1e3", "1e3"),
        ("null", "null"),
        ("~", "~"),
        ("42", 42),
        ("-7", -7),
        ('"42"', "42"),
        ('"a \\"b\\" c"', 'a "b" c'),
    ],
)
def test_m7_parse_scalar_never_coerces_a_yaml_1_1_shape(raw, expected):
    """M7: only a bare optional-minus integer becomes an int; `no`, dates,
    floats, hex, `null` and `~` stay the strings the person wrote."""
    assert frontmatter._parse_scalar(raw) == expected
    assert type(frontmatter._parse_scalar(raw)) is type(expected)


@pytest.mark.parametrize("fence", ["----", "---  ", "--- ", " ---", "----\r"])
def test_m8_the_boundary_grammar_is_exact_and_shared_with_the_writers(fence):
    """M8: `---` alone on its line, LF or CRLF, is a boundary; nothing else is.
    The byte-surgical writers spell the same grammar (`stamp._has_delimiter`,
    `events._replace_frontmatter_list`'s fence test, `literature_notes.
    rename_frontmatter_key` through `_FRONTMATTER_OPEN`/`_FRONTMATTER_CLOSE`)."""
    from research_vault import events, literature_notes, stamp

    text = f'{fence}\ntype: "x"\n---\nbody\n'
    assert frontmatter.parse(text) == ({}, text)  # not an opening
    assert stamp._has_delimiter(text) is False
    row = {"by": "research_vault/0.1.0", "at": "2026-08-16", "check": "doi"}
    envelope = frontmatter.serialize({"verified": [row]})
    if text.splitlines(keepends=True)[0].endswith("\r\n"):
        envelope = envelope.replace("\n", "\r\n")
    # A loose fence check would take `----` as an opening and splice the list
    # inside the fake block; the exact grammar envelopes a fresh block instead.
    assert (
        events._replace_frontmatter_list(text, "verified", [row], text)
        == envelope + text
    )
    assert literature_notes.rename_frontmatter_key(text, "type", "kind") == text
    unterminated = f'---\ntype: "x"\n{fence}\nbody\n'
    with pytest.raises(frontmatter.FrontmatterError, match="unterminated"):
        frontmatter.parse(unterminated)  # not a closing either


def test_read_okf_reads_nested_yaml_the_flat_parser_refuses():
    text = (
        "---\ntitle: A page\ntype: concept\ntags:\n  - a\n  - b\n"
        "meta:\n  nested: 1\n---\nbody\n"
    )
    data, body = frontmatter.read_okf(text)
    assert data == {
        "title": "A page",
        "type": "concept",
        "tags": ["a", "b"],
        "meta": {"nested": 1},
    }
    assert body == "body\n"


def test_read_okf_splits_on_the_same_delimiters_as_parse():
    text = "---\r\ntype: concept\r\n---\r\nbody\r\n"
    assert frontmatter.read_okf(text)[1] == frontmatter.parse(text)[1] == "body\r\n"
    assert frontmatter.read_okf("no block\n") == ({}, "no block\n")
    with pytest.raises(frontmatter.FrontmatterError, match="unterminated"):
        frontmatter.read_okf("---\ntype: concept\nbody\n")


@pytest.mark.parametrize("value", ["null", "~", "NULL", "Null", ""])
def test_read_okf_rule_2_reads_every_null_spelling_as_missing(value):
    """OKF's reference reader tests `not fm.get("type")`; BaseLoader would read
    `null` as the string "null" and pass it (Q18)."""
    data, _ = frontmatter.read_okf(f"---\ntype: {value}\n---\n")
    assert not frontmatter.okf_type(data)


def test_read_okf_keeps_a_quoted_null_as_present():
    data, _ = frontmatter.read_okf('---\ntype: "null"\n---\n')
    assert frontmatter.okf_type(data)


def test_read_okf_leaves_a_date_shaped_scalar_as_text():
    """The reference loader removes the timestamp resolver: `2026-13-45` is text,
    not a ValueError and not a datetime."""
    data, _ = frontmatter.read_okf(
        "---\ntype: daily\nday: 2026-13-45\nreal: 2026-10-24\n---\n"
    )
    assert data["day"] == "2026-13-45"
    assert data["real"] == "2026-10-24"


def test_read_okf_refuses_a_duplicate_key_and_a_non_mapping_block():
    with pytest.raises(frontmatter.FrontmatterError, match="duplicate key 'type'"):
        frontmatter.read_okf("---\ntype: a\ntype: b\n---\n")
    with pytest.raises(frontmatter.FrontmatterError, match="not a mapping"):
        frontmatter.read_okf("---\n- a\n- b\n---\n")
    with pytest.raises(frontmatter.FrontmatterError, match="not a mapping"):
        frontmatter.read_okf("---\njust a scalar\n---\n")


def test_read_okf_turns_an_unhashable_key_into_a_frontmatter_error():
    """`date: {{date}}` is a Templater placeholder; without a hashability check the
    duplicate-key constructor raises a bare TypeError (Q18)."""
    with pytest.raises(frontmatter.FrontmatterError):
        frontmatter.read_okf("---\ndate: {{date}}\n---\n")


def test_read_okf_refuses_a_custom_tag_and_an_unquoted_colon_title():
    with pytest.raises(frontmatter.FrontmatterError):
        frontmatter.read_okf("---\ntype: !custom x\n---\n")
    with pytest.raises(frontmatter.FrontmatterError):
        frontmatter.read_okf("---\ntitle: A: B\ntype: concept\n---\n")


def test_read_okf_reads_an_empty_block_as_an_empty_mapping():
    assert frontmatter.read_okf("---\n\n---\nbody\n") == ({}, "body\n")


def test_read_okf_names_a_missing_pyyaml_as_its_own_error(pyyaml_missing):
    with pytest.raises(frontmatter.DependencyMissingError, match="PyYAML"):
        frontmatter.read_okf("---\ntype: a\n---\n")


@pytest.mark.parametrize(
    ("text", "cause", "mark"),
    [
        # A constructor fault keeps its cause: PyYAML's own message leads with
        # the context and its mark, so its first two lines never named it.
        (
            "---\ndate: {{date}}\n---\n",
            "while constructing a mapping, found unhashable key {'date': None}",
            "(line 2, column 8)",
        ),
        (
            "---\ntype: a\ntype: b\n---\n",
            "while constructing a mapping, found duplicate key 'type'",
            "(line 3, column 1)",
        ),
        # The line is the file's, not the block's: the opening delimiter is
        # line 1, and a CRLF is one break. C and pure loaders word this cause
        # differently; the mark is shared.
        (
            "---\r\ntype: concept\r\ntitle: A: B\r\n---\r\n",
            "mapping values are not allowed",
            "(line 3, column 9)",
        ),
    ],
)
def test_read_okf_names_the_cause_on_one_line_at_the_files_line(text, cause, mark):
    with pytest.raises(frontmatter.FrontmatterError) as caught:
        frontmatter.read_okf(text)
    message = str(caught.value)
    assert message.startswith(f"frontmatter is not valid YAML: {cause}")
    assert message.endswith(f" {mark}")
    assert "\n" not in message


def test_read_okf_reports_a_markless_fault_on_one_line():
    """A reader fault (a control character) carries no problem or mark: its
    first line is the cause, and the block offset after it is dropped."""
    with pytest.raises(frontmatter.FrontmatterError) as caught:
        frontmatter.read_okf("---\na: \x07\n---\n")
    message = str(caught.value)
    assert message.startswith(
        "frontmatter is not valid YAML: unacceptable character #x0007"
    )
    assert "\n" not in message
    assert "position" not in message


@pytest.mark.parametrize(
    ("value", "error"),
    [
        pytest.param("!!int abc", "ValueError", id="int"),
        pytest.param("!!float abc", "ValueError", id="float"),
        pytest.param("!!bool abc", "KeyError", id="bool"),
        pytest.param("!!timestamp abc", "AttributeError", id="timestamp"),
        pytest.param("!!int", "IndexError", id="bare-int"),
        pytest.param("!!map [a]", "TypeError", id="map-of-a-sequence"),
        # No tag: the implicit int resolver matches `0b_`, which int() refuses.
        pytest.param("0b_", "ValueError", id="implicit-binary"),
    ],
)
def test_read_okf_refuses_a_value_its_constructor_cannot_build(value, error):
    """PyYAML's typed constructors raise plain Python errors, not YAMLError
    (`int("abc")`, a `!!bool` table lookup, a timestamp regex that does not
    match): content, so a FrontmatterError on one line like any other
    fault, never a traceback out of the structure check or stamp."""
    with pytest.raises(frontmatter.FrontmatterError) as caught:
        frontmatter.read_okf(f"---\ntitle: {value}\n---\nbody\n")
    message = str(caught.value)
    assert message.startswith(
        f"frontmatter is not valid YAML: cannot construct a value ({error}: "
    )
    assert "\n" not in message
