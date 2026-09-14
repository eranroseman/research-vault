import json

import pytest

from research_vault import Result, bibliography

ITEMS = [
    {"id": "smith2020", "type": "article-journal", "title": "Mortality decline"},
    {"id": "gone2019", "type": "article-journal", "title": "Old result"},
]


def test_write_sorts_by_id_and_load_reads_it_back(tmp_vault):
    path = bibliography.write(tmp_vault, ITEMS)

    assert path == tmp_vault / "system" / "bibliography.json"
    raw = path.read_text()
    assert raw.endswith("\n")
    assert [item["id"] for item in json.loads(raw)] == ["gone2019", "smith2020"]
    assert bibliography.load(tmp_vault) == {item["id"]: item for item in ITEMS}


def test_write_refuses_items_without_string_ids(tmp_vault):
    with pytest.raises(bibliography.BibliographyError) as error:
        bibliography.write(tmp_vault, [{"type": "book"}])
    assert error.value.result is Result.UNMATCHED
    assert not (tmp_vault / "system" / "bibliography.json").exists()


def test_load_returns_empty_universe_when_file_is_absent(tmp_vault):
    assert bibliography.load(tmp_vault) == {}


@pytest.mark.parametrize(
    "contents",
    [
        "{",
        '{"items": []}',
        '["not-an-entry"]',
        '[{"id": "x", "DOI": 123}]',
        '[{"id": ""}]',
        '[{"id": "bad\\nkey"}]',
        '[{"id": "../escape"}]',
    ],
    ids=[
        "truncated-json",
        "wrong-top-level",
        "wrong-entry",
        "non-string-doi",
        "empty-id",
        "multiline-id",
        "unsafe-id",
    ],
)
def test_load_classifies_readable_invalid_bibliography_as_unmatched(
    tmp_vault, contents
):
    (tmp_vault / bibliography.BIB_PATH).write_text(contents)

    with pytest.raises(bibliography.BibliographyError) as caught:
        bibliography.load(tmp_vault)

    assert caught.value.result is Result.UNMATCHED


def test_load_classifies_undecodable_bibliography_as_unreachable(tmp_vault):
    (tmp_vault / bibliography.BIB_PATH).write_bytes(b"\xff\xfe")

    with pytest.raises(bibliography.BibliographyError) as caught:
        bibliography.load(tmp_vault)

    assert caught.value.result is Result.UNREACHABLE


def test_autoexport_surface_is_gone():
    for name in ("observe_autoexport", "staleness", "commit_autoexport"):
        assert not hasattr(bibliography, name)


# --- boundaries the blanket mutation run (Plan W Task 25) found unpinned ------


def test_write_renders_two_space_indented_json_with_non_ascii_kept(tmp_vault):
    """The CSL file's bytes are a committed artifact: two-space indent,
    non-ASCII as is, one trailing newline, UTF-8."""
    path = bibliography.write(
        tmp_vault, [{"id": "müller2020", "type": "book", "title": "Größe → x"}]
    )
    assert (
        path.read_bytes()
        == (
            '[\n  {\n    "id": "müller2020",\n    "type": "book",\n'
            '    "title": "Größe → x"\n  }\n]\n'
        ).encode()
    )
