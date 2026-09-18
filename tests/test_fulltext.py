import hashlib

from research_vault import frontmatter, fulltext


def test_verdict_separates_absent_partial_empty_and_complete():
    assert fulltext.verdict(None) == (False, "no-index")
    assert fulltext.verdict(
        {"content": "x" * 900, "indexedPages": 100, "totalPages": 143}
    ) == (False, "partial — indexedPages 100 of 143")
    assert fulltext.verdict(
        {"content": "Masthead " * 12, "indexedPages": 9, "totalPages": 9}
    ) == (False, "empty — 108 characters below floor 500")
    assert fulltext.verdict(
        {"content": "y" * 600, "indexedChars": 600, "totalChars": 600}
    ) == (True, "complete")
    assert fulltext.verdict(
        {"content": "y" * 600, "indexedChars": 600, "totalChars": 700}
    ) == (False, "partial — indexedChars 600 of 700")


def test_write_renders_deterministic_frontmatter_and_verbatim_body(tmp_vault):
    response = {"content": "Page one\fPage two", "indexedPages": 2, "totalPages": 2}
    path, digest = fulltext.write(tmp_vault, "D7EJ9FTG", "E352DFS8", response)
    assert path == tmp_vault / "fulltext" / "D7EJ9FTG.md"
    raw = path.read_bytes()
    assert digest == hashlib.sha256(raw).hexdigest() == fulltext.sha256_of(path)
    data, body = frontmatter.parse(raw.decode())
    assert data == {
        "type": "fulltext",
        "zotero-attachment-key": "D7EJ9FTG",
        "zotero-item-key": "E352DFS8",
        "indexedPages": 2,
        "totalPages": 2,
    }
    assert body == "Page one\fPage two"
    _again, digest_again = fulltext.write(tmp_vault, "D7EJ9FTG", "E352DFS8", response)
    assert digest_again == digest


def test_write_refuses_an_unsafe_attachment_key(tmp_vault):
    import pytest

    with pytest.raises(ValueError, match="unsafe attachment key"):
        fulltext.write(tmp_vault, "../x", "E352DFS8", {"content": "c"})


# --- boundaries pinned against mutation survivors -----------------------------


def test_verdict_floor_is_inclusive_and_a_half_missing_pair_is_malformed():
    """Exactly FULLTEXT_MIN_CHARS characters is complete; a pair with either
    half missing or non-integer is malformed, named by its unit."""
    assert fulltext.verdict(
        {"content": "y" * 500, "indexedPages": 1, "totalPages": 1}
    ) == (True, "complete")
    assert fulltext.verdict(
        {"content": "y" * 499, "indexedPages": 1, "totalPages": 1}
    ) == (False, "empty — 499 characters below floor 500")
    assert fulltext.verdict({"content": "y" * 600, "indexedPages": 1}) == (
        False,
        "malformed — indexedPages pair missing",
    )
    assert fulltext.verdict({"content": "y" * 600, "totalChars": "600"}) == (
        False,
        "malformed — indexedChars pair missing",
    )


def test_write_renders_a_char_indexed_response_and_no_content_as_an_empty_body(
    tmp_vault,
):
    path, _digest = fulltext.write(
        tmp_vault,
        "D7EJ9FTG",
        "E352DFS8",
        {"content": None, "indexedChars": 600, "totalChars": 600},
    )
    data, body = frontmatter.parse(path.read_text())
    assert data == {
        "type": "fulltext",
        "zotero-attachment-key": "D7EJ9FTG",
        "zotero-item-key": "E352DFS8",
        "indexedChars": 600,
        "totalChars": 600,
    }
    assert body == ""


def test_write_refuses_a_total_without_its_indexed_half(tmp_vault):
    """`totalPages` alone is not a pair: the writer now refuses it the same
    way `verdict` calls it malformed (row 25 — `_render` guards symmetrically)."""
    import pytest

    with pytest.raises(ValueError, match="malformed — indexedPages pair missing"):
        fulltext.write(
            tmp_vault, "D7EJ9FTG", "E352DFS8", {"content": "c", "totalPages": 3}
        )


def test_write_creates_the_fulltext_directory_and_keeps_line_endings(tmp_vault):
    import shutil

    if (tmp_vault / "fulltext").exists():
        shutil.rmtree(tmp_vault / "fulltext")
    path, _digest = fulltext.write(
        tmp_vault,
        "D7EJ9FTG",
        "E352DFS8",
        {"content": "one\r\ntwo\n", "indexedPages": 1, "totalPages": 1},
    )
    assert path.read_bytes().endswith(b"---\none\r\ntwo\n")


def test_verdict_names_the_neither_pair_case_and_an_indexed_count_over_total():
    """Row 25: a response with neither pair is malformed under a label naming
    both units; `indexed > total` is malformed, never partial and never usable."""
    assert fulltext.verdict({"content": "y" * 600}) == (
        False,
        "malformed — indexedPages/indexedChars pair missing",
    )
    assert fulltext.verdict(
        {"content": "y" * 600, "indexedPages": 3, "totalPages": 2}
    ) == (False, "malformed — indexed exceeds total")


def test_render_refuses_a_non_numeric_pair_with_the_malformed_label(tmp_vault):
    import pytest

    with pytest.raises(ValueError, match="malformed — indexedChars pair missing"):
        fulltext.write(
            tmp_vault,
            "D7EJ9FTG",
            "E352DFS8",
            {"content": "c", "indexedChars": "x", "totalChars": 1},
        )
