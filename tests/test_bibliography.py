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


# --- boundaries pinned against mutation survivors -----------------------------


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


def test_entry_sha256_is_the_canonical_json_hash():
    from research_vault import bibliography

    entry = {"id": "a", "title": "T", "author": [{"family": "S"}]}
    assert bibliography.entry_sha256(entry) == bibliography.entry_sha256(
        {"title": "T", "author": [{"family": "S"}], "id": "a"}
    )
    assert bibliography.entry_sha256(entry) != bibliography.entry_sha256(
        {**entry, "title": "U"}
    )


def test_update_replaces_rendered_entries_keeps_the_rest_and_drops_uncaptured_keys(
    tmp_vault,
):
    from research_vault import bibliography

    bibliography.write(
        tmp_vault,
        [
            {"id": "a", "title": "A"},
            {"id": "b", "title": "B"},
            {"id": "gone", "title": "G"},
        ],
    )
    bibliography.update(tmp_vault, {"a": {"id": "a", "title": "A2"}}, keep={"a", "b"})
    assert bibliography.load(tmp_vault) == {
        "a": {"id": "a", "title": "A2"},
        "b": {"id": "b", "title": "B"},
    }
