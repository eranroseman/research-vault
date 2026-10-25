"""The lit-search wrapper, litsearch.py, over stubbed vendored functions (spec
v3, section 3). The nine vendored modules are imported in-process from the
plugin's scripts directory; every network entry point is replaced, so no test
here reaches a socket (the suite's socket block would raise if one did)."""

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "experiment-proposal" / "skills" / "lit-search" / "scripts"


def _load():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("litsearch", SCRIPTS / "litsearch.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


wrapper = _load()

RECORD = {
    "type": "article-journal",
    "title": "A title\nsplit across lines: with a colon",
    "_source": "crossref,openalex",
    "DOI": "10.1000/xyz123",
    "author": [{"family": "Doe", "given": "J."}, {"family": "Roe", "given": "R."}],
    "issued": {"year": 2024},
    "container-title": "A Journal",
    "abstract": "x" * 400,
}
SECOND = {
    "type": "paper-conference",
    "title": "Second Title",
    "_source": "arxiv",
    "URL": "https://arxiv.org/abs/0000.00000",
    "author": [{"family": "Poe"}],
    "issued": {"year": 2023},
    "abstract": "short",
}


@pytest.fixture
def federate(monkeypatch):
    """search.federate replaced: records two fixed entries, logs each call."""
    calls: list[tuple] = []

    def fake(query, limit, sources):
        calls.append((query, limit, tuple(sources)))
        return [dict(RECORD), dict(SECOND)]

    monkeypatch.setattr(wrapper.search, "federate", fake)
    monkeypatch.setattr(
        wrapper.dblp,
        "search",
        lambda query, limit=10: pytest.fail("dblp ran without --dblp-query"),
    )
    return calls


def test_a_title_with_a_newline_yields_output_that_strict_parses(federate, capsys):
    assert wrapper.main(["search", "q"]) == 0
    out, err = capsys.readouterr()
    records = yaml.safe_load(out)
    assert [r["title"] for r in records] == [RECORD["title"], "Second Title"]
    assert records[0]["author"] == [{"family": "Doe"}, {"family": "Roe"}]
    assert records[0]["issued"] == {"year": 2024}
    assert records[0]["DOI"] == "10.1000/xyz123"
    assert records[0]["container-title"] == "A Journal"
    assert len(records[0]["abstract"]) == 300
    assert "URL" not in records[1]
    assert "type" not in records[1]
    assert federate == [
        ("q", 10, ("crossref", "arxiv", "semantic_scholar", "openalex"))
    ]
    assert 'crossref(1, 1) query="q"' in err
    assert 'openalex(1, 1) query="q"' in err
    assert 'arxiv(1, 1) query="q"' in err
    assert "candidates: 2 (after exclude: 2)" in err


def test_full_output_keeps_given_names_the_url_the_type_and_the_source(
    federate, capsys
):
    assert wrapper.main(["search", "q", "--full"]) == 0
    records = yaml.safe_load(capsys.readouterr().out)
    assert records[0]["author"][0] == {"family": "Doe", "given": "J."}
    assert records[0]["source"] == "crossref,openalex"
    assert records[0]["type"] == "article-journal"
    assert len(records[0]["abstract"]) == 400
    assert records[1]["URL"] == "https://arxiv.org/abs/0000.00000"


def test_compact_is_the_default_named_and_exclusive_with_full(federate, capsys):
    assert wrapper.main(["search", "q", "--compact"]) == 0
    named = capsys.readouterr().out
    assert len(yaml.safe_load(named)[0]["abstract"]) == 300
    assert wrapper.main(["search", "q"]) == 0
    assert capsys.readouterr().out == named
    with pytest.raises(SystemExit) as exit_info:
        wrapper.main(["search", "q", "--compact", "--full"])
    assert exit_info.value.code == 2
    assert "not allowed with argument" in capsys.readouterr().err


def test_the_exclude_file_is_honoured_by_doi_and_by_title(federate, capsys, tmp_path):
    judged = tmp_path / "lit-search-judged.txt"
    judged.write_text(
        "# seeded from the draft\n"
        "https://doi.org/10.1000/XYZ123 | kept | already in the draft\n"
        "second title | rejected | off topic\n",
        encoding="utf-8",
    )
    assert wrapper.main(["search", "q", "--exclude", str(judged)]) == 1
    out, err = capsys.readouterr()
    assert out == ""
    assert "candidates: 2 (after exclude: 0)" in err
    assert "no candidates left this round" in err
    assert 'crossref(1, 0) query="q"' in err
    judged.write_text("second title | rejected | off topic\n", encoding="utf-8")
    assert wrapper.main(["search", "q", "--exclude", str(judged)]) == 0
    out, err = capsys.readouterr()
    assert [r["title"] for r in yaml.safe_load(out)] == [RECORD["title"]]
    assert 'arxiv(1, 0) query="q"' in err


def test_a_planted_429_note_yields_the_skip_line_and_no_second_call(
    monkeypatch, capsys
):
    calls: list[str] = []

    def degraded(query, limit, sources):
        calls.append(query)
        print("note: source degraded — semantic_scholar: HTTP 429", file=sys.stderr)  # noqa: T201
        print("sources: crossref(1)", file=sys.stderr)  # noqa: T201
        return [dict(RECORD)]

    monkeypatch.setattr(wrapper.search, "federate", degraded)
    assert wrapper.main(["search", "q"]) == 0
    err = capsys.readouterr().err
    assert calls == ["q"]
    assert (
        "note: source degraded — semantic_scholar: HTTP 429" in err
    )  # relayed verbatim
    assert "sources: crossref(1)" in err
    assert (
        "semantic_scholar: skipped (HTTP 429); snowball's graph endpoints cover it"
        in err
    )
    assert err.index("HTTP 429\n") < err.index("semantic_scholar: skipped")


def test_dblp_runs_separately_on_its_own_short_query(federate, monkeypatch, capsys):
    dblp_calls: list[tuple] = []

    def fake_dblp(query, limit=10):
        dblp_calls.append((query, limit))
        return [
            {
                "type": "paper-conference",
                "title": "From DBLP",
                "_source": "dblp",
                "DOI": "10.1000/dblp1",
            }
        ]

    monkeypatch.setattr(wrapper.dblp, "search", fake_dblp)
    code = wrapper.main(
        [
            "search",
            "health coach empathy response length",
            "--dblp-query",
            "health coach",
        ]
    )
    assert code == 0
    out, err = capsys.readouterr()
    assert dblp_calls == [("health coach", 10)]
    assert "dblp" not in federate[0][2]
    assert 'dblp(1, 1) query="health coach"' in err
    assert 'crossref(1, 1) query="health coach empathy response length"' in err
    assert "From DBLP" in out


def test_a_dblp_challenge_carries_the_vendored_browser_hint(
    federate, monkeypatch, capsys
):
    message = (
        "dblp: API returned an Anubis browser-verification page (HTTP 200, text/html)"
    )

    def challenged(query, limit=10):
        raise wrapper.common.SourceError(message, kind="challenge")

    monkeypatch.setattr(wrapper.dblp, "search", challenged)
    assert wrapper.main(["search", "q", "--dblp-query", "short"]) == 0
    err = capsys.readouterr().err
    hint = wrapper.search.BROWSER_HINT.format(source="dblp")
    assert f"note: source degraded — {message}. {hint}\n" in err
    assert 'see "If a source asks for browser verification"' in err
    assert "dblp(" not in err


def test_a_dblp_degradation_of_another_kind_and_an_unexpected_error_are_noted(
    federate, monkeypatch, capsys
):
    def refused(query, limit=10):
        raise wrapper.common.SourceError("dblp: HTTP 503", kind="http", status=503)

    monkeypatch.setattr(wrapper.dblp, "search", refused)
    assert wrapper.main(["search", "q", "--dblp-query", "short"]) == 0
    err = capsys.readouterr().err
    assert "note: source degraded — dblp: HTTP 503\n" in err
    assert "browser" not in err

    def broken(query, limit=10):
        raise KeyError("text a server sent")

    monkeypatch.setattr(wrapper.dblp, "search", broken)
    assert wrapper.main(["search", "q", "--dblp-query", "short"]) == 0
    out, err = capsys.readouterr()
    assert "note: source failed unexpectedly — dblp: KeyError\n" in err
    assert "text a server sent" not in err
    assert len(yaml.safe_load(out)) == 2


def test_snowball_uses_the_vendored_expand_and_enrichment_and_drops_the_seed(
    monkeypatch, capsys
):
    seen: dict = {}

    def fake_expand(seeds, limit, direction):
        seen["expand"] = (list(seeds), limit, direction)
        return [
            {"DOI": "10.1000/bare", "_source": "opencitations"},
            dict(RECORD),
            {"title": "The seed", "DOI": "10.1000/seed", "_source": "openalex"},
        ]

    def fake_enrich(items):
        seen["enrich"] = len(items)
        return [dict(item, title=item.get("title") or "Enriched") for item in items]

    monkeypatch.setattr(wrapper.snowball, "expand", fake_expand)
    monkeypatch.setattr(wrapper.snowball, "enrich_bare_dois", fake_enrich)
    assert wrapper.main(["snowball", "https://doi.org/10.1000/SEED"]) == 0
    out, err = capsys.readouterr()
    assert seen["expand"] == (["https://doi.org/10.1000/SEED"], 5, "both")
    assert seen["enrich"] == 3
    titles = [r["title"] for r in yaml.safe_load(out)]
    assert "The seed" not in titles
    assert "Enriched" in titles
    assert 'opencitations(1, 1) query="https://doi.org/10.1000/SEED"' in err
    assert "semantic_scholar: skipped" not in err


def test_out_writes_the_file_and_prints_nothing_on_stdout(federate, capsys, tmp_path):
    target = tmp_path / "notes" / "round-1.yaml"
    target.parent.mkdir()
    assert wrapper.main(["search", "q", "--out", str(target)]) == 0
    out, err = capsys.readouterr()
    assert out == ""
    assert f"wrote 2 records to {target}" in err
    assert len(yaml.safe_load(target.read_text(encoding="utf-8"))) == 2


def test_an_unknown_source_and_a_missing_exclude_file_are_exit_2(
    federate, capsys, tmp_path
):
    with pytest.raises(SystemExit) as exit_info:
        wrapper.main(["search", "q", "--sources", "crossref,nowhere"])
    assert exit_info.value.code == 2
    assert (
        wrapper.main(["search", "q", "--exclude", str(tmp_path / "missing.txt")]) == 2
    )
    assert "cannot read" in capsys.readouterr().err
