"""The `search-log` verb: PRISMA-S search provenance (spec §7 `find-sources` row).

Project-scoped, append-only ``projects/<name>/search-log.md``. Two record
kinds through one verb, mutually exclusive per call: a search-run entry
(query as run, source searched, date, hit count) and a not-admitted-candidate
entry (candidate, reason code, date). Mirrors ``inbox.py``'s durable-append
pattern (``knowledge_harness/searchlog.py``) rather than inventing a second
one; reuses ``inbox.validate_reason``/``inbox.REASON_CODES`` for the reason
field and ``publish.project_dir`` for project resolution, so the reason-code
registry and the project-path safety checks each still have exactly one
owner.
"""

from pathlib import Path

from knowledge_harness import AGENT_ACTOR, searchlog
from knowledge_harness.__main__ import main

FIND_SOURCES_SKILL = (
    Path(__file__).resolve().parents[1] / "skills" / "find-sources" / "SKILL.md"
)


def _log_path(vault, project="brief"):
    return vault / "projects" / project / "search-log.md"


def test_search_log_appends_a_search_entry_and_prints_a_summary(fixture_vault, capsys):
    code = main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--query",
            "(mortality[Title]) AND 2020:2026[dp]",
            "--source",
            "PubMed",
            "--hits",
            "12",
        ]
    )

    assert code == 0
    out = capsys.readouterr().out
    assert "PubMed" in out
    assert "12" in out

    entries = searchlog.load(fixture_vault, "brief")
    assert len(entries) == 1
    entry = entries[0]
    assert isinstance(entry, searchlog.SearchEntry)
    assert entry.query == "(mortality[Title]) AND 2020:2026[dp]"
    assert entry.source == "PubMed"
    assert entry.hits == 12
    assert entry.actor == AGENT_ACTOR


def test_search_log_file_carries_search_log_frontmatter_type(fixture_vault):
    main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--query",
            "q",
            "--source",
            "PubMed",
            "--hits",
            "1",
        ]
    )

    text = _log_path(fixture_vault).read_text()
    assert text.startswith('---\ntype: "search-log"\n---\n')


def test_search_log_accepts_hits_zero_and_round_trips(fixture_vault):
    """Zero hits is a reportable result, never silence (global four-state rule)."""
    code = main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--query",
            "an unusually specific query",
            "--source",
            "Europe PMC",
            "--hits",
            "0",
        ]
    )

    assert code == 0
    entry = searchlog.load(fixture_vault, "brief")[0]
    assert entry.hits == 0


def test_search_log_appends_a_not_admitted_entry_with_a_reason_code(
    fixture_vault, capsys
):
    code = main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--not-admitted",
            "Some Preprint Title (bioRxiv, 2024)",
            "--reason",
            "not-admitted — preprint only, no peer-reviewed version found",
            "--source",
            "bioRxiv",
        ]
    )

    assert code == 0
    out = capsys.readouterr().out
    assert "Some Preprint Title" in out

    entries = searchlog.load(fixture_vault, "brief")
    assert len(entries) == 1
    entry = entries[0]
    assert isinstance(entry, searchlog.NotAdmittedEntry)
    assert entry.candidate == "Some Preprint Title (bioRxiv, 2024)"
    assert entry.reason == "not-admitted — preprint only, no peer-reviewed version found"
    assert entry.source == "bioRxiv"


def test_search_log_not_admitted_source_is_optional(fixture_vault):
    code = main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--not-admitted",
            "A candidate found by hand, no search attached",
            "--reason",
            "not-admitted — duplicate of an already-admitted item",
        ]
    )

    assert code == 0
    entry = searchlog.load(fixture_vault, "brief")[0]
    assert entry.source is None


def test_search_log_refuses_when_neither_query_nor_not_admitted_given(
    fixture_vault, capsys
):
    code = main(
        ["search-log", "--vault", str(fixture_vault), "--project", "brief"]
    )

    assert code == 2
    assert "exactly one of" in capsys.readouterr().err
    assert not _log_path(fixture_vault).exists()


def test_search_log_refuses_when_both_query_and_not_admitted_given(
    fixture_vault, capsys
):
    code = main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--query",
            "q",
            "--source",
            "PubMed",
            "--hits",
            "1",
            "--not-admitted",
            "candidate",
            "--reason",
            "not-admitted — dup",
        ]
    )

    assert code == 2
    assert "exactly one of" in capsys.readouterr().err
    assert not _log_path(fixture_vault).exists()


def test_search_log_refuses_a_query_entry_missing_source_or_hits(fixture_vault, capsys):
    code = main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--query",
            "q",
        ]
    )

    assert code == 2
    assert "--source" in capsys.readouterr().err
    assert not _log_path(fixture_vault).exists()


def test_search_log_refuses_a_not_admitted_entry_missing_reason(fixture_vault, capsys):
    code = main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--not-admitted",
            "candidate",
        ]
    )

    assert code == 2
    assert "--reason" in capsys.readouterr().err
    assert not _log_path(fixture_vault).exists()


def test_search_log_refuses_an_unregistered_reason_code(fixture_vault, capsys):
    code = main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--not-admitted",
            "candidate",
            "--reason",
            "invented-code — not in the registry",
        ]
    )

    assert code == 2
    assert not _log_path(fixture_vault).exists()


def test_search_log_refuses_a_malformed_date(fixture_vault, capsys):
    code = main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--query",
            "q",
            "--source",
            "PubMed",
            "--hits",
            "1",
            "--date",
            "not-a-date",
        ]
    )

    assert code == 2
    assert not _log_path(fixture_vault).exists()


def test_search_log_refuses_a_negative_hit_count(fixture_vault, capsys):
    code = main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--query",
            "q",
            "--source",
            "PubMed",
            "--hits",
            "-1",
        ]
    )

    assert code == 2
    assert "non-negative" in capsys.readouterr().err
    assert not _log_path(fixture_vault).exists()


def test_search_log_refuses_when_the_project_does_not_exist(tmp_vault, capsys):
    code = main(
        [
            "search-log",
            "--vault",
            str(tmp_vault),
            "--project",
            "nosuch",
            "--query",
            "q",
            "--source",
            "PubMed",
            "--hits",
            "1",
        ]
    )

    assert code == 2
    assert "project" in capsys.readouterr().err.lower()


def test_search_log_is_append_only_across_two_runs(fixture_vault):
    """Two genuinely distinct runs of the same query are both retained — a
    search log is a PRISMA-S trail, not a deduplicated index."""
    args = [
        "search-log",
        "--vault",
        str(fixture_vault),
        "--project",
        "brief",
        "--query",
        "mortality decline",
        "--source",
        "PubMed",
        "--hits",
        "5",
    ]

    assert main(args + ["--date", "2026-08-20"]) == 0
    assert main(args + ["--date", "2026-08-21"]) == 0

    entries = searchlog.load(fixture_vault, "brief")
    assert [entry.date for entry in entries] == ["2026-08-20", "2026-08-21"]


def test_search_log_round_trips_a_query_carrying_escaped_characters(fixture_vault):
    tricky = r"title:[crispr] AND note\path"
    code = main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--query",
            tricky,
            "--source",
            "arXiv",
            "--hits",
            "3",
        ]
    )

    assert code == 0
    entry = searchlog.load(fixture_vault, "brief")[0]
    assert entry.query == tricky


def test_search_log_accepts_an_explicit_actor_and_date(fixture_vault):
    code = main(
        [
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--query",
            "q",
            "--source",
            "PubMed",
            "--hits",
            "1",
            "--actor",
            "human:eran",
            "--date",
            "2026-08-19",
        ]
    )

    assert code == 0
    entry = searchlog.load(fixture_vault, "brief")[0]
    assert entry.actor == "human:eran"
    assert entry.date == "2026-08-19"


def test_search_log_is_reachable_through_the_one_binary_cli(fixture_vault):
    """Proves `search-log` is genuinely wired into the shared dispatch table —
    ``python3 -m knowledge_harness search-log``, not a second binary."""
    import subprocess
    import sys

    repo = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "knowledge_harness",
            "search-log",
            "--vault",
            str(fixture_vault),
            "--project",
            "brief",
            "--query",
            "q",
            "--source",
            "PubMed",
            "--hits",
            "1",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert _log_path(fixture_vault).exists()


# --- skill content -----------------------------------------------------


def test_find_sources_skill_routes_every_mechanical_act_through_the_verb():
    text = FIND_SOURCES_SKILL.read_text(encoding="utf-8")
    for token in (
        "knowledge_harness search-log",
        "--not-admitted",
        "--reason",
        "not-admitted",
        "MATCHED",
        "UNMATCHED",
        "UNREACHABLE",
        "SKIPPED",
        "import-source",
    ):
        assert token in text, f"find-sources/SKILL.md never mentions {token!r}"
