from harness_core import frontmatter


SAMPLE = {
    "citekey": "smith2020",
    "type": "literature",
    "doi": "10.1000/xyz",
    "retrieved": "2026-08-16",
    "attachment-sha256": ["aa11", "bb22"],
    "status": "unreviewed",
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
    assert text.startswith("---\n") and text.endswith("---\n")
    assert 'citekey: "smith2020"' in text
    assert "attachment-sha256:" in text
    assert '- {by: "harness_core/0.1.0", at: "2026-08-16", check: "doi"}' in text


def test_parse_no_frontmatter():
    data, body = frontmatter.parse("just a body\n")
    assert data == {} and body == "just a body\n"


def test_quotes_in_titles_roundtrip():
    data = {"aliases": ['The "gold standard" myth'], "citekey": "x2020"}
    parsed, _ = frontmatter.parse(frontmatter.serialize(data))
    assert parsed == data


def test_parse_rejects_nested_maps():
    bad = '---\nouter:\n  inner: "x"\n---\n'
    try:
        frontmatter.parse(bad)
        assert False, "should raise"
    except frontmatter.FrontmatterError:
        pass
