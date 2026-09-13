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
