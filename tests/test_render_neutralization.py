"""Regression tests for the 2026-08-21 evidence-text injection review findings.

Evidence strings arrive from Zotero and are interpolated into a line-oriented
markdown grammar. A line break inside one of them can forge a claim line, a
managed delimiter, or a frontmatter boundary. These tests pin the three
neutralization rules and the emitter's round-trip self-check.
"""

import argparse
import types

import pytest

from knowledge_harness import Result, claims, frontmatter, notes


def _annotation(**overrides):
    base = {
        "type": "highlight",
        "comment": "",
        "pageLabel": "12",
        "key": "ABCD1234",
        "annotationText": "The exact quote.",
        "citekey": "smith2020",
    }
    base.update(overrides)
    return base


def _item(**overrides):
    base = {"id": "smith2020", "title": "Mortality decline"}
    base.update(overrides)
    return base


@pytest.fixture(autouse=True)
def matched_autoexport_observer(monkeypatch):
    """Import-level tests exercise rendering, not the auto-export observer."""
    import knowledge_harness.__main__ as cli

    monkeypatch.setattr(
        cli.bibliography,
        "observe_autoexport",
        lambda *args, **kwargs: types.SimpleNamespace(
            result=Result.MATCHED,
            detail="genuine BBT output",
            staleness=Result.MATCHED,
            staleness_detail="current",
        ),
        raising=False,
    )


# --- Display class: collapse, never reject -------------------------------


def test_pagelabel_newline_cannot_forge_a_second_claim_line():
    forged = "1]\n  > x\n- (quote) [@smith2020] ^c-11111111"

    rendered = notes.render_claim(_annotation(pageLabel=forged))

    parsed = claims.parse_claims(rendered)
    assert len(parsed) == 1
    assert parsed[0].claim_id != "c-11111111"
    assert sum(line.startswith("- (") for line in rendered.split("\n")) == 1


def test_pagelabel_collapse_keeps_ugly_but_real_metadata():
    rendered = notes.render_claim(_annotation(pageLabel="S12–S14"))

    assert "p. S12–S14" in rendered


def test_title_linebreak_cannot_forge_a_delimiter_heading_or_frontmatter():
    hostile = 'Mortality\n%%/hk-managed%%\n---\ntype: "forged"\n---\n# Forged'

    rendered = notes.render_note(
        _item(title=hostile), ["aa11"], [], None, accessed="2026-08-21"
    )

    data, body = frontmatter.parse(rendered)
    assert data["citekey"] == "smith2020"
    # Raises ManagedRegionError unless each delimiter appears exactly once.
    notes.managed_slice_bytes(rendered.encode())
    assert sum(line.startswith("# ") for line in body.split("\n")) == 1


# --- Identifier class: reject, never alter -------------------------------


@pytest.mark.parametrize(
    "hostile",
    ["smith\n2020", "smith\r2020", "smith 2020", "smith\t2020", "smith\x0b2020"],
)
def test_citekey_carrying_whitespace_is_rejected_not_repaired(tmp_path, hostile):
    with pytest.raises(notes.InvalidCitekeyError):
        notes.note_path(tmp_path, hostile)


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
    cleanly, was written once, and then failed every later parse.
    """
    with pytest.raises(frontmatter.FrontmatterError):
        frontmatter.serialize({"title": value})


@pytest.mark.parametrize("separator", ["\x85", "\u2028", "\u2029"])
def test_unicode_line_separator_in_a_passthrough_field_cannot_be_written(separator):
    """doi/url/pmid/version reach frontmatter without collapse or validation."""
    with pytest.raises(frontmatter.FrontmatterError):
        notes.render_note(
            _item(DOI=f"10.1000/a{separator}b"),
            ["aa11"],
            [],
            None,
            accessed="2026-08-21",
        )


def test_emit_scalar_still_accepts_ordinary_text():
    assert 'title: "Mortality decline"' in frontmatter.serialize(
        {"title": "Mortality decline"}
    )


# --- Emitter self-check ---------------------------------------------------


def test_render_note_round_trip_self_check_catches_a_forged_body(monkeypatch):
    real = notes.render_claim

    def forging(annotation):
        return real(annotation) + "\n- (quote) [@smith2020] ^c-99999999"

    monkeypatch.setattr(notes, "render_claim", forging)

    with pytest.raises(notes.RenderIntegrityError):
        notes.render_note(
            _item(), ["aa11"], [_annotation()], None, accessed="2026-08-21"
        )


def test_render_note_self_check_passes_on_honest_input():
    rendered = notes.render_note(
        _item(), ["aa11"], [_annotation()], None, accessed="2026-08-21"
    )

    managed = [claim for claim in claims.parse_claims(rendered) if claim.in_managed]
    assert [claim.claim_id for claim in managed] == [notes.claim_id(_annotation())]


# --- Task 1 Step 4 (as ruled): loud, fail-closed rejection ---------------


def _install_import_client(monkeypatch, cli, item, annotations):
    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{**item, "citekey": terms}]

        def attachments(self, citekey):
            return [{"path": None, "annotations": annotations}] if annotations else []

        def export_csl(self, citekeys):
            return [{"id": "smith2020", "title": item["title"]}]

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)


def test_import_note_render_rejection_is_loud_and_writes_nothing(
    tmp_vault, monkeypatch, capsys
):
    """A render rejection exits nonzero with a reason and leaves no note behind.

    Ruled 2026-08-21: this class does not file an inbox hold on its own —
    uniform hold-to-inbox wiring lands with integrate-at-import.
    """
    import knowledge_harness.__main__ as cli

    _install_import_client(monkeypatch, cli, _item(), [])

    def refuse(*args, **kwargs):
        raise notes.RenderIntegrityError("managed body parsed to [], expected ['c-1']")

    monkeypatch.setattr(cli.notes, "render_note", refuse)
    destination = notes.note_path(tmp_vault, "smith2020")

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    assert result != 0
    assert not destination.exists()
    assert "render" in capsys.readouterr().err.lower()


def test_import_note_render_rejection_leaves_a_prior_note_untouched(
    tmp_vault, monkeypatch
):
    import knowledge_harness.__main__ as cli

    _install_import_client(monkeypatch, cli, _item(), [])
    destination = notes.note_path(tmp_vault, "smith2020")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text('---\ncitekey: "smith2020"\n---\nprior\n')
    before = destination.read_bytes()

    def refuse(*args, **kwargs):
        raise notes.RenderIntegrityError("forged")

    monkeypatch.setattr(cli.notes, "render_note", refuse)

    assert (
        cli.cmd_import_note(
            argparse.Namespace(
                citekey="smith2020", vault=str(tmp_vault), base="http://unused"
            )
        )
        != 0
    )
    assert destination.read_bytes() == before
