import json
import os

from research_vault import Result, captured
from research_vault.pathcodec import decode_repo_path


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
        lines.append(
            'compile-input-sha256: "' + "f" * 64 + '"'
        )  # a decoy: the structural leg compares per attachment, never this
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
    # [[wiki/Other page]] and [[Other page.md]] are the two forms Obsidian resolves
    # for one file; neither may add a row (rule 2 is a trailing path form, not a stem).
    (pages / "Mortality decline.md").write_text(
        '---\ntype: source\nsources:\n  - "[[Mortality decline]]"\n---\n[[smith2020]] [@smith2020] [[Other page]] [[wiki/Other page]] [[Other page.md]] [[ghost2020]] [@ghost2021]\n'
    )
    (tmp_vault / "wiki" / "Other page.md").write_text("---\ntype: concept\n---\n")
    outcomes = captured.lint_captured_set(tmp_vault)
    bad = sorted(o.reason for o in outcomes if o.result is Result.UNMATCHED)
    assert bad == [
        "not-captured — wiki/sources/Mortality decline.md cites [@ghost2021], not in the captured set",
        "not-captured — wiki/sources/Mortality decline.md links [[ghost2020]], not a page and not in the captured set",
    ]


def test_a_wikilink_resolves_by_a_note_alias_when_no_page_carries_the_name(tmp_vault):
    _note(
        tmp_vault, "smith2020", "SMITH001", title="Mortality decline"
    )  # aliases: ["Mortality decline"]; no page has that stem
    page = tmp_vault / "wiki" / "sources" / "A.md"
    page.parent.mkdir(parents=True)
    page.write_text("---\ntype: source\n---\n[[Mortality decline]] [[Nobody at all]]\n")
    bad = [
        o.reason
        for o in captured.lint_captured_set(tmp_vault)
        if o.result is Result.UNMATCHED
    ]
    assert bad == [
        "not-captured — wiki/sources/A.md links [[Nobody at all]], not a page and not in the captured set"
    ]


def test_an_unreadable_page_is_an_outage_row_and_the_walk_goes_on(
    tmp_vault, monkeypatch
):
    """One page nobody can read must not end the walk. cmd_verify catches OSError, so
    without this leg a single chmod-000 page is exit 2 'verification unavailable' for
    the whole run instead of one UNREACHABLE row against that page."""
    pages = tmp_vault / "wiki" / "sources"
    pages.mkdir(parents=True)
    (pages / "A.md").write_text("---\ntype: source\n---\n[@ghost2021]\n")
    (pages / "B.md").write_text("---\ntype: source\n---\n[@ghost2022]\n")
    real = captured.Path.read_text

    def refuse(self, *args, **kwargs):
        if self.name == "A.md":
            raise PermissionError(13, "Permission denied")
        return real(self, *args, **kwargs)

    monkeypatch.setattr(captured.Path, "read_text", refuse)
    rows = [
        (o.result, o.reason.split(" — ")[0])
        for o in captured.lint_captured_set(tmp_vault)
        if "wiki/sources" in str(o.target)
    ]
    assert rows == [(Result.UNREACHABLE, "outage"), (Result.UNMATCHED, "not-captured")]


def test_a_finding_names_the_link_as_written_and_can_be_written_to_the_queue(tmp_vault):
    """Two faults in one row. [[Ghost.md]] must be reported as written, or grepping
    the vault for the finding's text fails. And a byte surrogateescape kept alive as a
    lone surrogate must not reach inbox.append_entry's utf-8 stream, where it raises
    UnicodeEncodeError — a ValueError cmd_verify deliberately does not catch, so the
    run would die at the moment the finding was filed. lint_captured_set returns a
    fine-looking Outcome either way, which is why the pin is on the reason's *bytes*."""
    pages = tmp_vault / "wiki" / "sources"
    pages.mkdir(parents=True)
    (pages / "A.md").write_bytes(b"---\ntype: source\n---\n[[Ghost.md]] [[Fo\xffo]]\n")
    reasons = [
        o.reason
        for o in captured.lint_captured_set(tmp_vault)
        if o.result is Result.UNMATCHED
    ]
    for reason in reasons:
        reason.encode("utf-8")  # exactly what append_entry's stream does
    assert reasons == [
        "not-captured — wiki/sources/A.md links [[Ghost.md]], not a page and not in the captured set",
        "not-captured — wiki/sources/A.md links [[Fo\ufffdo]], not a page and not in the captured set",
    ]


def test_a_page_whose_own_name_is_not_utf8_still_yields_a_writable_reason(tmp_vault):
    """The same UnicodeEncodeError, reached by the other route: the path is
    interpolated into the reason too, and a byte in a *filename* survives
    os.fsdecode as a lone surrogate exactly as one in the body does. The target
    keeps the exact bytes through RepoPath; only the human-readable reason is
    replaced, because body-or-path text in a reason has no codec of its own."""
    pages = tmp_vault / "wiki" / "sources"
    pages.mkdir(parents=True)
    (pages / os.fsdecode(b"A\xff.md")).write_text("---\ntype: source\n---\n[[Ghost]]\n")
    rows = [
        o for o in captured.lint_captured_set(tmp_vault) if o.result is Result.UNMATCHED
    ]
    for row in rows:
        row.reason.encode("utf-8")  # exactly what append_entry's stream does
    assert [r.reason for r in rows] == [
        "not-captured — wiki/sources/A\ufffd.md links [[Ghost]], not a page and not in the captured set"
    ]
    assert decode_repo_path(rows[0].target) == b"wiki/sources/A\xff.md"


def test_a_root_file_named_literatures_is_still_a_page(tmp_vault):
    """The evidence-folder guard reads the unstripped parts: with_suffix("") turns a
    root-level `literatures.md` into `literatures`, and the guard would drop its name,
    making [[literatures]] a blocking finding."""
    (tmp_vault / "literatures.md").write_text("---\ntype: concept\n---\n")
    pages = tmp_vault / "wiki" / "sources"
    pages.mkdir(parents=True)
    (pages / "A.md").write_text("---\ntype: source\n---\n[[literatures]]\n")
    assert [
        o.reason
        for o in captured.lint_captured_set(tmp_vault)
        if o.result is Result.UNMATCHED
    ] == []


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
    # "20260102" and "2026-W01-1" are what date.fromisoformat accepts and this
    # module does not: measured 2026-09-08, the second parses as 2025-12-29, a day
    # nobody typing it would recognise. The shape is refused before the parse.
    for bad in ("2026-13-01", "20260102", "2026-W01-1", "2026-1-2", ""):
        try:
            clock.today(bad)
        except ValueError:
            continue
        raise AssertionError(
            f"an invalid as_of must be refused, never read as today: {bad!r}"
        )


def test_a_stray_byte_under_wiki_is_a_row_not_a_traceback(tmp_vault):
    """verify's except tuple excludes ValueError, so a UnicodeDecodeError out of
    this lint would end the run with a traceback instead of a finding."""
    page = tmp_vault / "wiki" / "sources"
    page.mkdir(parents=True)
    (page / "Co-writing.md").write_bytes(b"---\ntype: source\n---\n\xff [@ghost2021]\n")
    bad = [
        o.reason
        for o in captured.lint_captured_set(tmp_vault)
        if o.result is Result.UNMATCHED
    ]
    assert bad == [
        "not-captured — wiki/sources/Co-writing.md cites [@ghost2021], not in the captured set"
    ]


def test_a_sources_array_is_a_schema_violation_not_an_attribute_error(tmp_vault):
    """The tool's schema always writes an object; an array reaches .items(), which
    has to be inside the same guard as the read."""
    _ledger(tmp_vault, [])
    rows = [
        (o.result, o.reason)
        for o in captured.lint_captured_set(tmp_vault)
        if "source-ledger" in str(o.target)
    ]
    assert rows == [(Result.UNMATCHED, "schema-violation — source ledger unreadable")]


def test_an_unreadable_ledger_is_an_outage_not_a_verdict_on_its_content(
    tmp_vault, monkeypatch
):
    """A permission or disk fault is not a schema violation: nothing read the
    content, so nothing may rule on it (ADR 0002). _read_notes types the identical
    OSError the same way one function above."""
    _ledger(tmp_vault, {})

    def refuse(self, *args, **kwargs):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(captured.Path, "read_text", refuse)
    rows = [
        (o.result, o.reason.split(" — ")[0])
        for o in captured.lint_captured_set(tmp_vault)
        if "source-ledger" in str(o.target)
    ]
    assert rows == [(Result.UNREACHABLE, "outage")]


def test_one_verdict_per_run_never_matched_and_unmatched_at_once(tmp_vault):
    """The textual half is clean and the structural half is not. Deciding MATCHED
    before the structural rows exist puts both verdicts on one check in one report."""
    _note(tmp_vault, "smith2020", "SMITH001", text_key="ATT00001", sha="a" * 64)
    _ledger(
        tmp_vault,
        {
            "src-1": {
                "origin": {"kind": "file", "locator": "fulltext/ATT00002.md"},
                "content_sha256": "b" * 64,
            }
        },
    )
    assert [o.result for o in captured.lint_captured_set(tmp_vault)] == [
        Result.UNMATCHED
    ]


def test_quiet_vault_is_matched_and_a_missing_ledger_is_skipped(tmp_vault):
    outcomes = captured.lint_captured_set(tmp_vault)
    assert [(o.target, o.result) for o in outcomes] == [
        ("captured-set", Result.MATCHED),
        ("wiki/meta/ledgers/source-ledger.json", Result.SKIPPED),
    ]
