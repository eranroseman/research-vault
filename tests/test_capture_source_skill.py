from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
SKILL = REPOSITORY / "skills" / "capture-source" / "SKILL.md"


def test_capture_source_replaces_import_source():
    assert SKILL.is_file()
    assert not (REPOSITORY / "skills" / "import-source").exists()
    text = SKILL.read_text()
    assert text.startswith("---\nname: capture-source\ndescription: Use when ")
    assert "disable-model-invocation: true\n---\n" in text


def test_capture_source_keeps_the_kept_rules():
    text = SKILL.read_text()
    for needle in (
        "No project is required",
        "project-independent",
        "zero projects",
        "Citation Key",
        "Better BibTeX",
        "SKIPPED applied to reading",
        "the range you did not read named",
        "python3 -m research_vault capture",
        "python3 -m research_vault add",
        "python3 -m research_vault propagate",
        "matched — NOOP",
        # The exact line capture prints (its `_refused` reason): the table
        # once carried a `re-keyed` row capture never emitted.
        "`UNMATCHED KEY — re-keyed — old → new; run propagate`",
        "a SKIPPED line is never filed",
        "no-fulltext",
        "database-changed",
        "python3 -m research_vault compile",
        "--approved-plan-sha256",
        "wiki-ingest",
        "recompile-needed",
        "![[<page path>]]",
    ):
        assert needle in text, needle
    assert "import-note" not in text
    assert "managed region" not in text
    assert "auto-export" not in text


def test_synthesis_conventions_names_the_tool_and_the_seam():
    text = (REPOSITORY / "skills" / "synthesis-conventions" / "SKILL.md").read_text()
    for needle in (
        "claude-obsidian",
        "transaction inspect",
        "wiki-ingest",
        "`captured-set`",
        "[[<citation key>]]",
        "wiki/index.md",
        "two or more captured sources",
        "python3 -m research_vault compile",
    ):
        assert needle in text, needle
    assert "synthesis/" not in text
