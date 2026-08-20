import builtins
import re

from harness_core import checks, notes, selectors

TEXT = (
    "Background prose before the finding. The cohort showed that "
    "Mortality fell 12% across all strata. Further discussion follows here."
)


def test_find_context_slices_32():
    ctx = selectors.find_context(TEXT, "Mortality fell 12% across all strata.")
    assert ctx is not None
    prefix, suffix = ctx
    assert prefix.endswith("showed that ")
    assert len(prefix) <= 32
    assert suffix.startswith(" Further")
    assert len(suffix) <= 32


def test_find_context_normalized_match():
    assert selectors.find_context(TEXT, "Mortality  fell 12% across all strata.")


def test_find_context_absent_returns_none():
    assert selectors.find_context(TEXT, "Sentence that is not there.") is None


def test_find_context_matches_checks_normalize_text_for_composition_and_crlf():
    raw = "Before e\u0301 and 가-\r\nword\u00ad  after quote Tail"
    quote = "é and 가word after quote"

    context = selectors.find_context(raw, quote)

    assert context == ("Before ", " Tail")
    assert checks.normalize_text(raw).find(checks.normalize_text(quote)) >= 0


def test_find_context_suffix_does_not_start_with_composing_mark():
    raw = "Before quote e\u0301tail"

    context = selectors.find_context(raw, "quote")

    assert context == ("Before ", " e\u0301tail")
    assert not context[1].startswith("\u0301")


def test_attach_contexts_counts():
    anns = [
        {
            "annotationText": "Mortality fell 12% across all strata.",
            "type": "highlight",
        },
        {"annotationText": "not present", "type": "highlight"},
    ]
    n = selectors.attach_contexts(anns, TEXT)
    assert n == 1
    assert anns[0]["context_prefix"].endswith("showed that ")
    assert "context_prefix" not in anns[1]


def test_unescape_inverts_notes_escaping_for_entity_looking_input():
    value = '" & --> &quot; &#x27; &amp;'
    ann = {
        "key": "K1",
        "type": "highlight",
        "citekey": "x2020",
        "annotationText": "quote",
        "comment": "",
        "pageLabel": "1",
        "context_prefix": value,
        "context_suffix": "tail",
    }
    rendered = notes.render_claim(ann)
    selector = next(line for line in rendered.splitlines() if "hk-sel" in line)
    prefix_escaped = re.search(r'prefix="([^"]*)"', selector).group(1)
    assert selectors.unescape_selector(prefix_escaped) == value


def test_unescape_inverts_newline_selector_escaping():
    value = "before\r\nafter\n"
    ann = {
        "key": "K2",
        "type": "highlight",
        "citekey": "x2020",
        "annotationText": "quote",
        "comment": "",
        "pageLabel": "1",
        "context_prefix": value,
        "context_suffix": "tail",
    }
    selector = next(
        line for line in notes.render_claim(ann).splitlines() if "hk-sel" in line
    )
    prefix_escaped = re.search(r'prefix="([^"]*)"', selector).group(1)
    assert selectors.unescape_selector(prefix_escaped) == value


def test_pdf_text_degrades_without_pypdf(monkeypatch, tmp_path):
    real_import = builtins.__import__

    def no_pypdf(name, *args):
        if name == "pypdf":
            raise ImportError("absent")
        return real_import(name, *args)

    monkeypatch.setattr(builtins, "__import__", no_pypdf)
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-1.4 minimal")
    assert selectors.pdf_text(pdf) is None


def test_pdf_text_degrades_when_pypdf_import_raises(monkeypatch, tmp_path):
    real_import = builtins.__import__

    def broken_pypdf(name, *args):
        if name == "pypdf":
            raise RuntimeError("broken optional install")
        return real_import(name, *args)

    monkeypatch.setattr(builtins, "__import__", broken_pypdf)
    assert selectors.pdf_text(tmp_path / "x.pdf") is None


def test_pdf_text_degrades_when_extraction_raises(monkeypatch, tmp_path):
    class BrokenReader:
        def __init__(self, _):
            raise ValueError("broken")

    class FakePypdf:
        PdfReader = BrokenReader

    monkeypatch.setitem(__import__("sys").modules, "pypdf", FakePypdf)
    assert selectors.pdf_text(tmp_path / "x.pdf") is None
