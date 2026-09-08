import json

from research_vault import Result, captured


def _note(vault, key, item_key, *, title=None, text_key=None, sha=None):
    lines = [
        "---",
        'type: "literature"',
        f'title: "{title or key}"',
        "aliases:",
        f'  - "{title or key}"',
        'zotero-server-id: "S"',
        f'zotero-item-key: "{item_key}"',
        "zotero-item-version: 1",
        f'citationKey: "{key}"',
        "attachments:",
        "fulltext:",
    ]
    if text_key:
        lines.append(f'  - {{attachment-key: "{text_key}", sha256: "{sha}"}}')
        lines.append(f'compile-input-sha256: "{sha}"')
    lines += ["---", ""]
    (vault / "literatures" / f"{key}.md").write_text("\n".join(lines))


def _ledger(vault, records):
    path = vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema": "claude-obsidian.source-ledger.v1",
                "generated_at": "2026-09-07T00:00:00Z",
                "sources": records,
            }
        )
    )


def test_captured_set_is_the_recorded_keys_not_the_filenames(tmp_vault):
    _note(tmp_vault, "smith2020", "SMITH001")
    (tmp_vault / "literatures" / "renamed2020.md").write_text(
        (tmp_vault / "literatures" / "smith2020.md")
        .read_text()
        .replace('citationKey: "smith2020"', 'citationKey: "smith2020a"')
    )
    (tmp_vault / "literatures" / "junk.md").write_text("no frontmatter\n")
    assert captured.captured_set(tmp_vault) == {
        "smith2020": "SMITH001",
        "smith2020a": "SMITH001",
    }


def test_a_note_the_reader_cannot_take_is_a_row_not_a_silent_omission(tmp_vault):
    """Decision 08 drops a corrupt note's key from the captured set; this lint is what says so."""
    _note(tmp_vault, "smith2020", "E352DFS8")
    (tmp_vault / "literatures" / "broken.md").write_text(
        "---\ntype: literature\n"
    )  # unterminated frontmatter
    (tmp_vault / "literatures" / "stray.md").write_text(
        '---\ntype: "literature"\n---\nno tuple\n'
    )
    rows = sorted(
        (str(o.target).rsplit("/", 1)[-1], o.result, o.reason.split(" — ")[0])
        for o in captured.lint_captured_set(tmp_vault)
        if "literatures/" in str(o.target)
    )
    assert rows == [
        ("broken.md", Result.UNMATCHED, "schema-violation"),
        ("stray.md", Result.UNMATCHED, "schema-violation"),
    ]
    assert captured.captured_set(tmp_vault) == {
        "smith2020": "E352DFS8"
    }  # the set is what capture's CSL selection reads


def test_textual_half_resolves_pages_aliases_and_keys_and_reports_the_rest(tmp_vault):
    _note(tmp_vault, "smith2020", "SMITH001", title="Mortality decline")
    pages = tmp_vault / "wiki" / "sources"
    pages.mkdir(parents=True)
    (pages / "Mortality decline.md").write_text(
        '---\ntype: source\nsources:\n  - "[[Mortality decline]]"\n---\n[[smith2020]] [@smith2020] [[Other page]] [[ghost2020]] [@ghost2021]\n'
    )
    (tmp_vault / "wiki" / "Other page.md").write_text("---\ntype: concept\n---\n")
    outcomes = captured.lint_captured_set(tmp_vault)
    bad = sorted(o.reason for o in outcomes if o.result is Result.UNMATCHED)
    assert bad == [
        "not-captured — wiki/sources/Mortality decline.md cites [@ghost2021], not in the captured set",
        "not-captured — wiki/sources/Mortality decline.md links [[ghost2020]], not a page and not in the captured set",
    ]


def test_structural_half_checks_locators_and_hashes(tmp_vault):
    _note(tmp_vault, "smith2020", "SMITH001", text_key="ATT00001", sha="a" * 64)
    _ledger(
        tmp_vault,
        {
            "src-1": {
                "origin": {"kind": "file", "locator": "fulltext/ATT00001.md"},
                "content_sha256": "a" * 64,
            },
            "src-2": {
                "origin": {"kind": "file", "locator": "fulltext/ATT00002.md"},
                "content_sha256": "b" * 64,
            },
            "src-3": {
                "origin": {"kind": "file", "locator": "fulltext/ATT00001.md"},
                "content_sha256": "c" * 64,
            },
            "src-4": {
                "origin": {"kind": "url", "locator": "https://example.org/"},
                "content_sha256": None,
            },
        },
    )
    outcomes = captured.lint_captured_set(tmp_vault)
    reasons = sorted(o.reason for o in outcomes if o.result is Result.UNMATCHED)
    assert reasons == [
        "not-captured — ledger src-2 names fulltext/ATT00002.md, which no capture wrote",
        "recompile-needed — ledger src-3 holds c"
        + "c" * 63
        + " for fulltext/ATT00001.md; the note records a"
        + "a" * 63,
    ]


def test_structural_half_applies_the_tools_staleness_predicate_as_of(tmp_vault):
    _note(tmp_vault, "smith2020", "SMITH001", text_key="ATT00001", sha="a" * 64)
    active = {
        "origin": {"kind": "file", "locator": "fulltext/ATT00001.md"},
        "content_sha256": "a" * 64,
        "review_status": "active",
        "retrieved_at": "2026-02-01T00:00:00Z",
        "refresh_due": "2026-03-01T00:00:00Z",
    }

    def unmatched(as_of):
        return [
            o.reason
            for o in captured.lint_captured_set(tmp_vault, as_of=as_of)
            if o.result is Result.UNMATCHED
        ]

    _ledger(tmp_vault, {"src-1": active})
    assert unmatched("2026-09-07") == [
        "recompile-needed — ledger src-1 stale: observed 2026-02-01T00:00:00Z, refresh due 2026-03-01T00:00:00Z, as of 2026-09-07"
    ]
    assert unmatched("2026-02-15") == []
    assert (
        unmatched("2026-01-15") != []
    )  # observed after as_of is stale too: the tool's predicate, verbatim
    _ledger(tmp_vault, {"src-1": {**active, "refresh_due": None}})
    assert unmatched("2026-02-15")[0].startswith(
        "recompile-needed — ledger src-1 stale: observed 2026-02-01T00:00:00Z, refresh due None"
    )
    _ledger(
        tmp_vault,
        {"src-1": {**active, "review_status": "unreviewed", "refresh_due": None}},
    )
    assert (
        unmatched("2026-09-07") == []
    )  # what the wrapper writes is never judged stale


def test_clock_today_takes_the_instant_or_reads_utc():
    import re

    from research_vault import clock

    assert clock.today("2026-01-02") == "2026-01-02"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", clock.today())
    try:
        clock.today("2026-13-01")
    except ValueError:
        pass
    else:
        raise AssertionError("an invalid as_of must be refused, never read as today")


def test_quiet_vault_is_matched_and_a_missing_ledger_is_skipped(tmp_vault):
    outcomes = captured.lint_captured_set(tmp_vault)
    assert [(o.target, o.result) for o in outcomes] == [
        ("captured-set", Result.MATCHED),
        ("wiki/meta/ledgers/source-ledger.json", Result.SKIPPED),
    ]
