"""Regression tests for evidence-text injection.

Evidence strings arrive from Zotero and are interpolated into a line-oriented
markdown grammar. A line break inside one of them can forge a claim line, a
heading, or a frontmatter boundary. These tests pin the two neutralization
rules that outlive the retired renderer — the display class collapses, the
identifier class rejects — and the serializer boundary they both lean on.
"""

import pytest

from research_vault import claims, frontmatter, literature_notes

# --- Display class: collapse, never reject -------------------------------


def test_display_text_collapse_cannot_forge_a_second_claim_line():
    forged = "1]\n  > x\n- (quote) [@smith2020] ^c-11111111"

    line = f"- (quote) [@smith2020, p. {literature_notes.display_text(forged)}] ^c-22222222"

    parsed = claims.parse_claims(line)
    assert len(parsed) == 1
    assert parsed[0].claim_id == "c-22222222"
    assert sum(text.startswith("- (") for text in line.split("\n")) == 1


def test_display_text_collapse_keeps_ugly_but_real_metadata():
    assert literature_notes.display_text("S12–S14") == "S12–S14"


# --- Identifier class: reject, never alter -------------------------------


@pytest.mark.parametrize(
    "hostile",
    ["smith\n2020", "smith\r2020", "smith 2020", "smith\t2020", "smith\x0b2020"],
)
def test_citation_key_carrying_whitespace_is_rejected_not_repaired(tmp_path, hostile):
    with pytest.raises(literature_notes.InvalidCitationKeyError):
        literature_notes.note_path(tmp_path, hostile)


# --- Serializer boundary: fail loudly ------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "a\nb",
        "a\rb",
        "a\x00b",
        "a\x1fb",
        "a\x7fb",
        "a\x85b",
        "a\u2028b",
        "a\u2029b",
    ],
)
def test_emit_scalar_rejects_every_character_splitlines_breaks_on(value):
    """The reject class must equal the parser's line-break set.

    A narrower class is corrupt-on-write: a DOI carrying U+2028 serialized
    cleanly, was written once, and then failed every later parse. `doi`, `url`,
    `pmid` and `version` reach frontmatter without collapse or validation, so
    this boundary is the only thing standing between them and a note that
    cannot be read back.
    """
    with pytest.raises(frontmatter.FrontmatterError):
        frontmatter.serialize({"title": value})


def test_emit_scalar_still_accepts_ordinary_text():
    assert 'title: "Mortality decline"' in frontmatter.serialize(
        {"title": "Mortality decline"}
    )
