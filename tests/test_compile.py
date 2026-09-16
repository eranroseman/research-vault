import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from research_vault import Result, inbox, notes
from research_vault import compile as compile_mod
from research_vault.__main__ import main
from tests.conftest import must_replace


def test_stable_source_id_matches_the_tools_own_function():
    assert (
        compile_mod.stable_source_id("file", "fulltext/ABCD1234.md", "a" * 64)
        == "src-2a09635ec6bad4de1b13"
    )
    assert (
        compile_mod.stable_source_id("FILE", "fulltext/ABCD1234.md", "A" * 64)
        == "src-2a09635ec6bad4de1b13"
    )


def _note(vault, key="jakesch.etal2023a", sha="f" * 64):
    (vault / "literatures" / f"{key}.md").write_text(
        f'---\ntype: "literature"\ntitle: "Co-writing"\naliases:\n  - "Co-writing"\n'
        f'zotero-server-id: "S"\nzotero-item-key: "E352DFS8"\nzotero-item-version: 544\ncitationKey: "{key}"\n'
        f'attachments:\n  - {{key: "D7EJ9FTG", version: 551, md5: "m", contentType: "application/pdf", filename: "a.pdf"}}\n'
        f'fulltext:\n  - {{attachment-key: "D7EJ9FTG", sha256: "{sha}"}}\ncompile-input-sha256: "{sha}"\n'
        f'accessed: "2026-09-07"\ngenerated: {{by: "research_vault/0.1.0", at: "2026-09-07T00:00:00Z"}}\n---\n'
    )
    (vault / "fulltext").mkdir(exist_ok=True)
    (vault / "fulltext" / "D7EJ9FTG.md").write_text(
        '---\ntype: "fulltext"\n---\ntext\n'
    )


def test_ledger_record_and_bundle_shape(tmp_vault, monkeypatch):
    _note(tmp_vault)
    monkeypatch.setattr(compile_mod, "tool_root", lambda vault: None)
    with pytest.raises(compile_mod.ToolMissingError):
        compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    records = compile_mod.records_for(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    source_id, record = next(iter(records.items()))
    assert source_id == compile_mod.stable_source_id(
        "file", "fulltext/D7EJ9FTG.md", "f" * 64
    )
    assert record["origin"] == {"kind": "file", "locator": "fulltext/D7EJ9FTG.md"}
    assert record["content_sha256"] == "f" * 64
    assert record["title"] == "Co-writing"
    assert record["review_status"] == "unreviewed"
    assert record["pages"] == []
    assert record["retrieved_at"] == "2026-09-07"
    assert record["ingested_at"] == "2026-09-07"


def test_records_skip_notes_without_a_compile_input(tmp_vault):
    _note(tmp_vault)
    path = tmp_vault / "literatures" / "jakesch.etal2023a.md"
    text = must_replace(
        path.read_text(), 'compile-input-sha256: "' + "f" * 64 + '"\n', ""
    )
    path.write_text(text)
    assert (
        compile_mod.records_for(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
        == {}
    )


def test_ledger_record_skips_when_no_fulltext_entry_matches_the_compile_input(
    tmp_vault,
):
    """``next((...), None)`` must supply the ``None`` default for real: a
    ``compile-input-sha256`` that matches no ``fulltext[].sha256`` entry
    leaves the generator exhausted, and without the default that raises
    ``StopIteration`` instead of a graceful skip."""
    _note(tmp_vault)
    path = tmp_vault / "literatures" / "jakesch.etal2023a.md"
    text = must_replace(
        path.read_text(),
        'compile-input-sha256: "' + "f" * 64 + '"',
        'compile-input-sha256: "' + "b" * 64 + '"',
    )
    path.write_text(text)
    assert (
        compile_mod.records_for(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
        == {}
    )


def test_stable_source_id_normalizes_a_file_locator_through_pureposixpath():
    """``kind.casefold() == "file"`` selects normalization; a redundant path
    segment must hash the same as its normalized form for a file kind,
    proving ``PurePosixPath`` actually ran — an always-false comparison (a
    flipped operator, or a comparison against a casefolded value the
    right-hand side never can be) would leave both un-normalized instead,
    making them differ from a locator that never needed normalizing."""
    raw = compile_mod.stable_source_id("file", "fulltext//D7EJ9FTG.md", "a" * 64)
    normalized = compile_mod.stable_source_id("file", "fulltext/D7EJ9FTG.md", "a" * 64)
    assert raw == normalized


def test_stable_source_id_treats_a_missing_sha_as_empty_not_a_placeholder():
    """``(content_sha256 or '').casefold()``: a placeholder other than ``''``
    is invisible to a test that only ever passes ``None`` (both are falsy,
    so any fallback token would be reached the same way) — only comparing
    against an independently computed digest catches which literal was
    actually hashed."""
    result = compile_mod.stable_source_id("file", "fulltext/D7EJ9FTG.md", None)
    expected_digest = hashlib.sha256(b"file\0fulltext/D7EJ9FTG.md\0").hexdigest()
    assert result == f"src-{expected_digest[:20]}"


def test_stable_source_id_honours_surrogatepass_on_an_undecodable_locator():
    """Ordinary content never exercises the ``errors=`` handler at all (no
    encoding error occurs), so a garbled handler name or a dropped ``errors=``
    kwarg is invisible to any test that never actually triggers it: only a
    lone surrogate (the undecodable-byte case ``surrogatepass`` exists for)
    forces the handler to run. ``surrogatepass``, not the package's usual
    ``surrogateescape``, because it is the external tool's own
    ``ledgers.stable_source_id`` handler — matching it byte-for-byte is what
    makes the hash agree with the tool's, per the brief's printed code."""
    surrogate_locator = "fulltext/\udc80.md"
    result = compile_mod.stable_source_id("file", surrogate_locator, "a" * 64)
    assert re.fullmatch(r"src-[0-9a-f]{20}", result)


def test_ledger_record_matches_the_ledger_schema_exactly(tmp_vault):
    _note(tmp_vault)
    records = compile_mod.records_for(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    (record,) = records.values()
    assert record == {
        "origin": {"kind": "file", "locator": "fulltext/D7EJ9FTG.md"},
        "content_kind": "document",
        "authority": "unknown",
        "review_status": "unreviewed",
        "title": "Co-writing",
        "content_sha256": "f" * 64,
        "ingested_at": "2026-09-07",
        "retrieved_at": "2026-09-07",
        "refresh_due": None,
        "independence_key": "jakesch.etal2023a",
        "supersedes": None,
        "pages": [],
    }


def test_ledger_record_falls_back_to_the_citation_key_when_the_note_has_no_title(
    tmp_vault,
):
    key = "nokish2026"
    sha = "e" * 64
    (tmp_vault / "literatures" / f"{key}.md").write_text(
        f'---\ntype: "literature"\nzotero-server-id: "S"\nzotero-item-key: "E352DFS9"\n'
        f'zotero-item-version: 1\ncitationKey: "{key}"\n'
        f'attachments:\n  - {{key: "ABCDEFGH", version: 1, md5: "m", contentType: "application/pdf", filename: "a.pdf"}}\n'
        f'fulltext:\n  - {{attachment-key: "ABCDEFGH", sha256: "{sha}"}}\ncompile-input-sha256: "{sha}"\n'
        f'generated: {{by: "research_vault/0.1.0", at: "2026-09-07T00:00:00Z"}}\n---\n'
    )
    records = compile_mod.records_for(tmp_vault, [key], today="2026-09-07")
    (record,) = records.values()
    assert record["title"] == key
    assert record["retrieved_at"] == "2026-09-07"
    assert record["ingested_at"] == "2026-09-07"


def test_ledger_record_prefers_the_notes_own_accessed_date_over_ingestion_day(
    tmp_vault,
):
    """retrieved_at reads the note's own ``accessed`` date, not the ingestion
    date -- distinguishable only when the two differ, which the fixture's
    matching date (2026-09-07 for both) cannot show."""
    _note(tmp_vault)  # accessed: "2026-09-07"
    records = compile_mod.records_for(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-20"
    )
    (record,) = records.values()
    assert record["retrieved_at"] == "2026-09-07"
    assert record["ingested_at"] == "2026-09-20"


def test_selected_notes_continues_past_an_excluded_note_to_a_later_wanted_one(
    tmp_vault,
):
    """continue, not break: an excluded note that sorts before the wanted one
    must not stop the walk (literatures/*.md is read in filename order)."""
    _note(tmp_vault, key="aaa-excluded")
    _note(tmp_vault, key="zzz-wanted", sha="a" * 64)
    records = compile_mod.records_for(tmp_vault, ["zzz-wanted"], today="2026-09-07")
    assert len(records) == 1


def test_selected_notes_skips_a_note_with_no_provenance_without_raising(tmp_vault):
    """``provenance is None or ...`` short-circuits before touching
    ``.citation_key``; an ``and`` here would evaluate ``None.citation_key``
    and raise instead of skipping the unparseable note."""
    (tmp_vault / "literatures" / "broken.md").write_text("not frontmatter at all\n")
    _note(tmp_vault)
    records = compile_mod.records_for(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    assert len(records) == 1


def test_selected_notes_skips_a_non_utf8_note_without_crashing(tmp_vault):
    """A corrupted note anywhere in ``literatures/`` must not crash the whole
    ``compile`` operation (Task 2 review, R24) -- ``broken.md`` sorts before
    ``jakesch.etal2023a.md`` so this also kills a ``continue`` -> ``break``
    mutant: the wanted note, read later in the same walk, must still yield."""
    (tmp_vault / "literatures" / "broken.md").write_bytes(b"\xff\xfe")
    _note(tmp_vault)
    records = compile_mod.records_for(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    assert len(records) == 1


def test_selected_notes_skips_an_unreadable_note_without_crashing(tmp_vault):
    """A note path that raises ``OSError`` on read (here: a directory, not a
    file, so ``read_bytes()`` raises ``IsADirectoryError``) must be skipped
    the same way a bad-encoding note is -- proving the ``except`` tuple
    really catches ``OSError``, not only ``UnicodeError``. ``dir.md`` sorts
    before ``jakesch.etal2023a.md``."""
    (tmp_vault / "literatures" / "dir.md").mkdir()
    _note(tmp_vault)
    records = compile_mod.records_for(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    assert len(records) == 1


def test_select_reports_a_key_outside_the_captured_set_as_not_captured(tmp_vault):
    """Review I2: a requested key with no literature note registers nothing
    and must say so — ``UNMATCHED … not-captured``, the capture-to-compile
    seam's own code — rather than vanish from a plan that then reads clean."""
    _note(tmp_vault)
    records, rows = compile_mod.select(
        tmp_vault, ["jakesch.etal2023a", "nosuchkey"], today="2026-09-07"
    )
    assert len(records) == 1
    (row,) = rows
    assert row.check == "compile"
    assert row.target == "nosuchkey"
    assert row.result is Result.UNMATCHED
    assert row.reason == "not-captured — no literature note; capture it first"


def test_select_reports_a_captured_note_without_text_as_skipped(tmp_vault):
    """A captured note with no ``compile-input-sha256`` has nothing to
    compile: ``SKIPPED … no-fulltext``, the fourth state (as capture reports
    an item with no attachment to read), never a finding — but a row, so an
    empty selection cannot read as a pass."""
    _note(tmp_vault)
    path = tmp_vault / "literatures" / "jakesch.etal2023a.md"
    path.write_text(
        must_replace(path.read_text(), 'compile-input-sha256: "' + "f" * 64 + '"\n', "")
    )
    records, rows = compile_mod.select(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    assert records == {}
    (row,) = rows
    assert row.target == "jakesch.etal2023a"
    assert row.result is Result.SKIPPED
    assert row.reason == "no-fulltext — no compile input recorded; nothing to register"


def test_select_reports_each_requested_key_once_in_request_order(tmp_vault):
    _note(tmp_vault)
    _records, rows = compile_mod.select(
        tmp_vault, ["zzz", "aaa", "zzz", "jakesch.etal2023a"], today="2026-09-07"
    )
    assert [row.target for row in rows] == ["zzz", "aaa"]


def _fake_tool(
    tmp_path,
    monkeypatch,
    *,
    inspect_ok=True,
    apply_code=0,
    apply_changed_paths=("wiki/meta/ledgers/source-ledger.json",),
):
    root = tmp_path / "tool"
    (root / "scripts").mkdir(parents=True)
    script = root / "scripts" / "claude-obsidian.py"
    changed = json.dumps(list(apply_changed_paths))
    script.write_text(
        "import json,sys\n"
        "from pathlib import Path\n"
        "args=sys.argv[1:]\n"
        # Every invocation's argv, recorded so a test can check exactly what
        # reached the tool -- not just that something printed the right JSON.
        "calls=Path(__file__).resolve().parents[1]/'calls.jsonl'\n"
        "calls.open('a').write(json.dumps(args)+chr(10))\n"
        "if args[:2]==['transaction','inspect']:\n"
        f"    print(json.dumps({{'schema':'claude-obsidian.transaction-plan.v1','valid':{inspect_ok!s},'approval_sha256':'abc123','changed_paths':['wiki/meta/ledgers/source-ledger.json']}}))\n"
        "elif args[:2]==['transaction','apply']:\n"
        "    assert '--approved-plan-sha256' in args\n"
        f"    print(json.dumps({{'schema':'claude-obsidian.transaction-result.v1','operation_id':'op','changed_paths':{changed}}})); sys.exit({apply_code})\n"
    )
    monkeypatch.setattr(compile_mod, "tool_root", lambda vault: root)
    return root


def _calls(root):
    """Every argv the fake tool script received, in call order."""
    return [
        json.loads(line) for line in (root / "calls.jsonl").read_text().splitlines()
    ]


def _fake_tool_raw(tmp_path, monkeypatch, *, inspect=None, apply=None):
    """A fake tool whose ``inspect``/``apply`` leg prints fixed raw
    ``(stdout, stderr, exit_code)`` text, for a shape ``_fake_tool``'s
    always-valid-JSON script cannot produce — including Task 1's own tracer
    measurement of an invalid bundle (exit 2, stderr, no JSON at all). A leg
    not given refuses to run (KeyError): no test should reach a leg it did
    not configure.
    """
    root = tmp_path / "tool"
    (root / "scripts").mkdir(parents=True)
    script = root / "scripts" / "claude-obsidian.py"
    legs = {}
    if inspect is not None:
        legs["inspect"] = inspect
    if apply is not None:
        legs["apply"] = apply
    script.write_text(
        "import sys\n"
        f"legs={legs!r}\n"
        "args=sys.argv[1:]\n"
        "leg=args[1] if args[:1]==['transaction'] else None\n"
        "stdout,stderr,code=legs[leg]\n"
        "sys.stdout.write(stdout)\n"
        "sys.stderr.write(stderr)\n"
        "sys.exit(code)\n"
    )
    monkeypatch.setattr(compile_mod, "tool_root", lambda vault: root)
    return root


def test_plan_writes_the_bundle_and_apply_reports_four_state(
    tmp_vault, tmp_path, monkeypatch
):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    bundle_path, inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    assert bundle_path.parent == tmp_vault / ".research-vault" / "compile"
    bundle = json.loads(bundle_path.read_text())
    assert bundle["operation_type"] == "ingest"
    (write,) = bundle["writes"]
    assert write["path"] == "wiki/meta/ledgers/source-ledger.json"
    assert write["mode"] == "create"
    assert write["sha256"] == hashlib.sha256(write["content"].encode()).hexdigest()
    assert bundle["expected_hashes"] == {"wiki/meta/ledgers/source-ledger.json": None}
    assert json.loads(write["content"])["schema"] == "claude-obsidian.source-ledger.v1"
    assert inspected["approval_sha256"] == "abc123"

    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert outcome.result is Result.MATCHED
    assert "source-ledger.json" in outcome.reason


def test_plan_merges_into_an_existing_ledger_and_pins_its_hash(
    tmp_vault, tmp_path, monkeypatch
):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    ledger = tmp_vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True)
    existing = {
        "schema": "claude-obsidian.source-ledger.v1",
        "generated_at": "2026-09-01T00:00:00Z",
        "sources": {"src-keep": {"origin": {"kind": "url", "locator": "https://x/"}}},
    }
    ledger.write_text(json.dumps(existing))
    bundle_path, _ = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    bundle = json.loads(bundle_path.read_text())
    assert (
        bundle["expected_hashes"]["wiki/meta/ledgers/source-ledger.json"]
        == hashlib.sha256(ledger.read_bytes()).hexdigest()
    )
    merged = json.loads(bundle["writes"][0]["content"])["sources"]
    assert "src-keep" in merged
    assert len(merged) == 2
    assert bundle["writes"][0]["mode"] == "replace"


def test_plan_keeps_an_existing_record_with_the_notes_source_id(
    tmp_vault, tmp_path, monkeypatch
):
    """R19: a record already compiled by the tool (active, with pages[]) is not
    reset to unreviewed on a re-run — ``plan()`` merges with ``setdefault``
    semantics, never overwriting a source id already in the ledger."""
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    source_id = compile_mod.stable_source_id("file", "fulltext/D7EJ9FTG.md", "f" * 64)
    ledger = tmp_vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True)
    existing_record = {
        "origin": {"kind": "file", "locator": "fulltext/D7EJ9FTG.md"},
        "content_kind": "document",
        "authority": "primary",
        "review_status": "active",
        "title": "Co-writing",
        "content_sha256": "f" * 64,
        "ingested_at": "2026-09-01",
        "retrieved_at": "2026-09-01",
        "refresh_due": "2027-09-01",
        "independence_key": "jakesch.etal2023a",
        "supersedes": None,
        "pages": ["wiki/sources/Co-writing.md"],
    }
    existing = {
        "schema": "claude-obsidian.source-ledger.v1",
        "generated_at": "2026-09-01T00:00:00Z",
        "sources": {source_id: existing_record},
    }
    ledger.write_text(json.dumps(existing))
    bundle_path, _ = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    bundle = json.loads(bundle_path.read_text())
    merged = json.loads(bundle["writes"][0]["content"])["sources"]
    assert merged[source_id] == existing_record


def test_plan_retires_the_stale_record_for_a_refreshed_text(
    tmp_vault, tmp_path, monkeypatch
):
    """R30 (review C1): a refreshed text has a new id, and the old record for
    the same locator must go — the tool validates every file record's
    ``content_sha256`` against the file's current bytes on every bundle, so a
    stale record wedges every later ``compile``, vault-wide. The new record
    names the dropped id in ``supersedes``; ``pages[]`` is not carried (spec
    §4.5: pages are the tool's, filled once its pages exist). A record for
    another locator is untouched."""
    _note(tmp_vault)  # sha A
    _fake_tool(tmp_path, monkeypatch)
    old_id = compile_mod.stable_source_id("file", "fulltext/D7EJ9FTG.md", "f" * 64)
    bundle_path, _ = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    # The tool applied that plan and later compiled a page from the text.
    ledger = tmp_vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True)
    applied = json.loads(json.loads(bundle_path.read_text())["writes"][0]["content"])
    applied["sources"][old_id]["review_status"] = "active"
    applied["sources"][old_id]["pages"] = ["wiki/sources/Co-writing.md"]
    applied["sources"]["src-keep"] = {
        "origin": {"kind": "url", "locator": "https://x/"}
    }
    ledger.write_text(json.dumps(applied))
    # The text refreshed (a Zotero re-index) and capture rewrote the note: sha B.
    _note(tmp_vault, sha="b" * 64)
    (tmp_vault / "fulltext" / "D7EJ9FTG.md").write_text(
        '---\ntype: "fulltext"\n---\ntext, re-indexed\n'
    )
    bundle_path, _ = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-08"
    )
    merged = json.loads(json.loads(bundle_path.read_text())["writes"][0]["content"])[
        "sources"
    ]
    new_id = compile_mod.stable_source_id("file", "fulltext/D7EJ9FTG.md", "b" * 64)
    assert [
        sid
        for sid, record in merged.items()
        if record["origin"]["locator"] == "fulltext/D7EJ9FTG.md"
    ] == [new_id]
    assert merged[new_id]["supersedes"] == old_id
    assert merged[new_id]["pages"] == []
    assert merged[new_id]["content_sha256"] == "b" * 64
    assert merged[new_id]["review_status"] == "unreviewed"
    assert "src-keep" in merged


def test_plan_leaves_a_record_whose_origin_is_not_the_tools_shape_alone(
    tmp_vault, tmp_path, monkeypatch
):
    """The locator comparison reads ``origin.locator`` only where a record has
    the tool's shape; a hand-edited record whose ``origin`` is not an object
    matches nothing and stays — the tool's own validation reports it."""
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    ledger = tmp_vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_text(
        json.dumps(
            {
                "schema": "claude-obsidian.source-ledger.v1",
                "generated_at": "2026-09-01T00:00:00Z",
                "sources": {
                    "src-odd": {"origin": "fulltext/D7EJ9FTG.md"},
                    "src-bare": 7,
                },
            }
        )
    )
    bundle_path, _ = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    merged = json.loads(json.loads(bundle_path.read_text())["writes"][0]["content"])[
        "sources"
    ]
    assert merged["src-odd"] == {"origin": "fulltext/D7EJ9FTG.md"}
    assert merged["src-bare"] == 7
    new_id = compile_mod.stable_source_id("file", "fulltext/D7EJ9FTG.md", "f" * 64)
    assert merged[new_id]["supersedes"] is None


def test_plan_bundle_and_ledger_content_are_exact(tmp_vault, tmp_path, monkeypatch):
    """One golden-content check for both JSON documents ``plan()`` writes:
    the ledger the tool will read, and the bundle wrapping it. Exact string
    equality (not just parsed-value spot checks) is what tells apart an
    ``indent=2``/``sort_keys=True`` formatting mutant, a key-name-casing
    mutant on a dict literal that a later unconditional re-set of the same
    key would otherwise mask, and a wrong source id under a fresh ledger."""
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    bundle_path, _inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    bundle = json.loads(bundle_path.read_text())
    source_id = compile_mod.stable_source_id("file", "fulltext/D7EJ9FTG.md", "f" * 64)
    expected_ledger = {
        "schema": "claude-obsidian.source-ledger.v1",
        "generated_at": "2026-09-07T00:00:00Z",
        "sources": {
            source_id: {
                "origin": {"kind": "file", "locator": "fulltext/D7EJ9FTG.md"},
                "content_kind": "document",
                "authority": "unknown",
                "review_status": "unreviewed",
                "title": "Co-writing",
                "content_sha256": "f" * 64,
                "ingested_at": "2026-09-07",
                "retrieved_at": "2026-09-07",
                "refresh_due": None,
                "independence_key": "jakesch.etal2023a",
                "supersedes": None,
                "pages": [],
            }
        },
    }
    expected_content = json.dumps(expected_ledger, indent=2, sort_keys=True) + "\n"
    assert bundle["writes"][0]["content"] == expected_content
    assert (
        bundle["writes"][0]["sha256"]
        == hashlib.sha256(expected_content.encode()).hexdigest()
    )
    assert bundle_path.read_text() == json.dumps(bundle, indent=2) + "\n"
    assert bundle["schema"] == "claude-obsidian.transaction.v1"
    assert bundle["operation_type"] == "ingest"
    assert re.fullmatch(r"research-vault-compile-\d{8}T\d{6}Z", bundle["operation_id"])
    assert bundle_path.name == bundle["operation_id"] + ".json"


class _FrozenOperationClock(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        # UTC (4:30 the NEXT day) differs from naive local (23:30) on
        # purpose: a `datetime.UTC` -> `None` mutant would pick the wrong one.
        if tz is None:
            return cls(2026, 9, 7, 23, 30)
        return cls(2026, 9, 8, 4, 30, tzinfo=datetime.UTC)


def test_plan_operation_id_uses_the_utc_clock_and_format(
    tmp_vault, tmp_path, monkeypatch
):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    monkeypatch.setattr(compile_mod.datetime, "datetime", _FrozenOperationClock)
    bundle_path, _inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    assert bundle_path.name == "research-vault-compile-20260908T043000Z.json"


def test_plan_raises_tool_missing_with_the_exact_message(tmp_vault, monkeypatch):
    _note(tmp_vault)
    monkeypatch.setattr(compile_mod, "tool_root", lambda vault: None)
    with pytest.raises(compile_mod.ToolMissingError) as excinfo:
        compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    assert str(excinfo.value) == "claude-obsidian is not installed"


def test_plan_reports_a_corrupt_ledger_as_a_named_error(
    tmp_vault, tmp_path, monkeypatch
):
    """Review I3: an unparseable ledger was a JSONDecodeError traceback.
    ``notes.LedgerUnreadableError`` is the named error the CLI turns into
    exit 2 — an outage, never an empty ledger to merge into."""
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    ledger = tmp_vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("{not json")
    with pytest.raises(notes.LedgerUnreadableError) as excinfo:
        compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    assert str(excinfo.value).startswith(
        "wiki/meta/ledgers/source-ledger.json unreadable: "
    )


def test_plan_reports_a_ledger_that_is_not_an_object_as_a_named_error(
    tmp_vault, tmp_path, monkeypatch
):
    """A top-level array parses but has no ``sources`` object to merge into;
    without the guard it is an AttributeError traceback on ``.get``."""
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    ledger = tmp_vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("[]")
    with pytest.raises(notes.LedgerUnreadableError) as excinfo:
        compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    assert (
        str(excinfo.value)
        == "wiki/meta/ledgers/source-ledger.json unreadable: not an object"
    )


def test_plan_reports_a_root_without_the_script_as_tool_missing(tmp_vault, tmp_path):
    """Review I3: a stale ``claude_obsidian_root`` (or ``installPath``) is an
    outage, not a mismatch — the tool cannot run. ``tool_root`` runs for
    real here through the machine.json override, and the error names the
    path the person has to fix."""
    _note(tmp_vault)
    root = tmp_path / "gone"
    root.mkdir()
    rv_dir = tmp_vault / ".research-vault"
    rv_dir.mkdir()
    (rv_dir / "machine.json").write_text(
        json.dumps({"claude_obsidian_root": str(root)})
    )
    with pytest.raises(compile_mod.ToolMissingError) as excinfo:
        compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    assert str(excinfo.value) == (
        f"claude-obsidian script not found: {root / 'scripts' / 'claude-obsidian.py'}"
    )
    assert not (tmp_vault / ".research-vault" / "compile").exists()


def test_run_invokes_the_tool_with_the_running_interpreter(
    tmp_vault, tmp_path, monkeypatch
):
    """``sys.executable``, not a bare ``python3`` looked up on PATH: the
    wrapper's own interpreter is the one known to exist (a missing one was
    an uncaught FileNotFoundError)."""
    _note(tmp_vault)
    root = _fake_tool(tmp_path, monkeypatch)
    seen = []

    def run(argv, **kwargs):
        seen.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout="{}", stderr="")

    monkeypatch.setattr(compile_mod.subprocess, "run", run)
    compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    (argv,) = seen
    assert argv[:2] == [sys.executable, str(root / "scripts" / "claude-obsidian.py")]


def test_plan_records_the_tools_exit_and_stderr(tmp_vault, tmp_path, monkeypatch):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    _bundle_path, inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    assert inspected["exit"] == 0
    assert inspected["stderr"] == ""


def test_plan_reflects_an_invalid_bundle_exit_without_json(
    tmp_vault, tmp_path, monkeypatch
):
    """Task 1's own tracer measurement: ``transaction inspect`` on an invalid
    bundle RAISES (exit 2, stderr, no JSON at all). ``plan()`` must not crash
    reading that, and reports the tool's exit code and stderr verbatim."""
    _note(tmp_vault)
    _fake_tool_raw(
        tmp_path, monkeypatch, inspect=("", "bundle is invalid: bad hash\n", 2)
    )
    _bundle_path, inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    assert inspected == {"exit": 2, "stderr": "bundle is invalid: bad hash"}


def test_plan_recovers_from_unparseable_non_empty_inspect_stdout(
    tmp_vault, tmp_path, monkeypatch
):
    """Non-empty but invalid JSON on stdout (distinct from the empty-stdout
    case above, which the ``or "{}"`` fallback turns into valid JSON before
    ``json.loads`` ever sees it) is what actually reaches ``except
    ValueError:``. ``inspected`` must become ``{}`` there — a dict, so the
    later ``.setdefault`` calls still work — not ``None``."""
    _note(tmp_vault)
    _fake_tool_raw(tmp_path, monkeypatch, inspect=("not valid json output", "", 2))
    _bundle_path, inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    assert inspected == {"exit": 2, "stderr": ""}


def test_plan_can_run_twice_against_the_same_vault(tmp_vault, tmp_path, monkeypatch):
    _note(tmp_vault)
    root = _fake_tool(tmp_path, monkeypatch)
    compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    assert len([c for c in _calls(root) if c[:2] == ["transaction", "inspect"]]) == 2


def test_plan_tolerates_an_existing_ledger_without_a_sources_key(
    tmp_vault, tmp_path, monkeypatch
):
    """``.get("sources", {})`` must supply the empty-dict default for real —
    a ledger somehow missing the key merges as if it carried none, not
    crashes on ``dict(None)``."""
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    ledger = tmp_vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_text(
        json.dumps(
            {
                "schema": "claude-obsidian.source-ledger.v1",
                "generated_at": "2026-09-01T00:00:00Z",
            }
        )
    )
    bundle_path, _inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    content = json.loads(json.loads(bundle_path.read_text())["writes"][0]["content"])
    assert len(content["sources"]) == 1


def test_apply_maps_tool_exit_codes(tmp_vault, tmp_path, monkeypatch):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch, apply_code=2)
    bundle_path, _ = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith("mismatch")
    monkeypatch.setattr(compile_mod, "tool_root", lambda vault: None)
    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert outcome.result is Result.UNREACHABLE


def test_apply_reports_a_root_without_the_script_as_unreachable(tmp_vault, tmp_path):
    """The apply leg's shape of review I3: UNREACHABLE naming the path, never
    an UNMATCHED ``mismatch`` hold for what is an outage."""
    _note(tmp_vault)
    root = tmp_path / "gone"
    root.mkdir()
    rv_dir = tmp_vault / ".research-vault"
    rv_dir.mkdir()
    (rv_dir / "machine.json").write_text(
        json.dumps({"claude_obsidian_root": str(root)})
    )
    outcome = compile_mod.apply(tmp_vault, tmp_vault / "bundle.json", "abc123")
    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason == (
        "outage — claude-obsidian script not found: "
        f"{root / 'scripts' / 'claude-obsidian.py'}"
    )


def test_apply_maps_the_expected_hash_conflict_exit(tmp_vault, tmp_path, monkeypatch):
    """Task 1's tracer measurement: ``transaction apply`` exits 75 on an
    expected-hash conflict. The three-line stderr (not one) is what tells
    apart the exact ``[-1:]`` slice and the ``stderr or stdout`` precedence
    from a same-shaped neighbour mutant."""
    _note(tmp_vault)
    _fake_tool_raw(
        tmp_path,
        monkeypatch,
        apply=("", "line one\nline two\nline three: the real error\n", 75),
    )
    bundle_path = tmp_vault / "bundle.json"
    bundle_path.write_text("{}")
    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason == "mismatch — line three: the real error"


def test_apply_reports_no_paths_when_none_are_returned(
    tmp_vault, tmp_path, monkeypatch
):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch, apply_changed_paths=[])
    bundle_path, _inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert outcome.reason == "matched — no paths reported"


def test_apply_joins_multiple_changed_paths_with_a_comma(
    tmp_vault, tmp_path, monkeypatch
):
    _note(tmp_vault)
    _fake_tool(
        tmp_path,
        monkeypatch,
        apply_changed_paths=[
            "wiki/meta/ledgers/source-ledger.json",
            "inbox/review-queue.md",
        ],
    )
    bundle_path, _inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert (
        outcome.reason
        == "matched — wiki/meta/ledgers/source-ledger.json, inbox/review-queue.md"
    )


def test_apply_treats_non_json_success_stdout_as_no_paths(
    tmp_vault, tmp_path, monkeypatch
):
    """``changed`` must default to ``[]`` on a ``ValueError`` from a
    malformed success response — not ``None``, which ``.join()`` cannot
    format."""
    _note(tmp_vault)
    _fake_tool_raw(tmp_path, monkeypatch, apply=("not json", "", 0))
    bundle_path = tmp_vault / "bundle.json"
    bundle_path.write_text("{}")
    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert outcome.reason == "matched — no paths reported"


def test_apply_defaults_changed_paths_to_empty_when_the_key_is_absent(
    tmp_vault, tmp_path, monkeypatch
):
    """``.get("changed_paths", [])`` must supply ``[]`` for real when the
    tool's own JSON omits the field — not ``None``."""
    _note(tmp_vault)
    _fake_tool_raw(
        tmp_path,
        monkeypatch,
        apply=(json.dumps({"schema": "x", "operation_id": "op"}), "", 0),
    )
    bundle_path = tmp_vault / "bundle.json"
    bundle_path.write_text("{}")
    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert outcome.reason == "matched — no paths reported"


def test_apply_uses_the_real_vault_for_tool_root(tmp_vault):
    """No ``_fake_tool``: ``tool_root`` runs for real, so its ``vault``
    argument must be the one ``apply()`` was given, not a placeholder — a
    bad ``Path(None)`` argument raises instead of answering ``None``, so an
    ``UNREACHABLE`` outcome here (the real ``tool_root()`` finds no registry
    under the test's own HOME) proves the call went through correctly."""
    outcome = compile_mod.apply(tmp_vault, tmp_vault / "bundle.json", "abc123")
    assert outcome.result is Result.UNREACHABLE


# --- tool_root: real resolution, no monkeypatch -----------------------------


@pytest.fixture
def plugin_registry(_per_test_home):
    """The plugin registry's path under the test's own HOME, its directory
    made and the file absent — mirrors tests/test_scaffold.py's fixture of the
    same shape, so ``tool_root``'s own plugin-lookup branch runs for real."""
    registry = _per_test_home / ".claude" / "plugins" / "installed_plugins.json"
    registry.parent.mkdir(parents=True)
    return registry


def test_tool_root_prefers_a_machine_config_override(tmp_vault):
    rv_dir = tmp_vault / ".research-vault"
    rv_dir.mkdir()
    (rv_dir / "machine.json").write_text(
        json.dumps({"claude_obsidian_root": "/opt/claude-obsidian"})
    )
    assert compile_mod.tool_root(tmp_vault) == Path("/opt/claude-obsidian")


def test_tool_root_falls_back_to_the_plugin_registry_when_the_override_is_blank(
    tmp_vault, plugin_registry
):
    rv_dir = tmp_vault / ".research-vault"
    rv_dir.mkdir()
    (rv_dir / "machine.json").write_text(json.dumps({"claude_obsidian_root": "   "}))
    plugin_registry.write_text(
        json.dumps(
            {
                "plugins": {
                    compile_mod.PLUGIN_ID: [{"installPath": "/plugins/claude-obsidian"}]
                }
            }
        )
    )
    assert compile_mod.tool_root(tmp_vault) == Path("/plugins/claude-obsidian")


def test_tool_root_is_none_without_an_override_or_a_registry_entry(
    tmp_vault, plugin_registry
):
    assert compile_mod.tool_root(tmp_vault) is None


# --- cmd_compile: the CLI face, through the one binary ----------------------


def test_cmd_compile_plans_and_prints_the_apply_line(
    tmp_vault, tmp_path, monkeypatch, capsys
):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    code = main(["compile", "jakesch.etal2023a", "--vault", str(tmp_vault)])
    out = capsys.readouterr().out
    assert code == 0
    assert '"valid": true' in out
    assert "apply with: python3 -m research_vault compile --vault" in out
    assert "--approved-plan-sha256 abc123" in out
    printed, _apply_line = out.rsplit("\napply with:", 1)
    assert printed == json.dumps(json.loads(printed), indent=2)


def test_cmd_compile_prints_the_sha_placeholder_when_the_tool_omits_it(
    tmp_vault, tmp_path, monkeypatch, capsys
):
    _note(tmp_vault)
    inspect_json = json.dumps(
        {
            "schema": "claude-obsidian.transaction-plan.v1",
            "valid": True,
            "changed_paths": [],
        }
    )
    _fake_tool_raw(tmp_path, monkeypatch, inspect=(inspect_json, "", 0))
    code = main(["compile", "jakesch.etal2023a", "--vault", str(tmp_vault)])
    assert code == 0
    # Exact substring: '<SHA>', 'XX<sha>XX' and the None-default fallback all
    # print something that is not this literal verbatim.
    assert "--approved-plan-sha256 <sha>" in capsys.readouterr().out


def test_cmd_compile_reports_an_invalid_plan_as_exit_1(
    tmp_vault, tmp_path, monkeypatch
):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch, inspect_ok=False)
    code = main(["compile", "jakesch.etal2023a", "--vault", str(tmp_vault)])
    assert code == 1


def test_cmd_compile_reports_the_tool_missing_as_exit_3(tmp_vault, capsys):
    """No ``_fake_tool``: ``tool_root`` runs for real under the test's own
    HOME, which carries no plugin registry, so this is also the second real
    (non-monkeypatched) path through ``tool_root``."""
    _note(tmp_vault)
    code = main(["compile", "jakesch.etal2023a", "--vault", str(tmp_vault)])
    assert code == 3
    assert "UNREACHABLE compile — outage" in capsys.readouterr().err


def test_cmd_compile_selects_the_whole_captured_set_with_all(
    tmp_vault, tmp_path, monkeypatch, capsys
):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    code = main(["compile", "--all", "--vault", str(tmp_vault)])
    assert code == 0
    printed, _apply_line = capsys.readouterr().out.rsplit("\napply with:", 1)
    bundle = json.loads(printed)
    written = json.loads(Path(bundle["bundle"]).read_text())
    (write,) = written["writes"]
    assert "src-" in next(iter(json.loads(write["content"])["sources"]))


def test_cmd_compile_applies_and_reports_matched(
    tmp_vault, tmp_path, monkeypatch, capsys
):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    bundle_path, inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    code = main(
        [
            "compile",
            "--vault",
            str(tmp_vault),
            "--bundle",
            str(bundle_path),
            "--approved-plan-sha256",
            inspected["approval_sha256"],
        ]
    )
    assert code == 0
    assert "MATCHED" in capsys.readouterr().out


def test_cmd_compile_holds_an_unmatched_apply(tmp_vault, tmp_path, monkeypatch, capsys):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch, apply_code=2)
    bundle_path, inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    code = main(
        [
            "compile",
            "--vault",
            str(tmp_vault),
            "--bundle",
            str(bundle_path),
            "--approved-plan-sha256",
            inspected["approval_sha256"],
        ]
    )
    assert code == 1
    assert "UNMATCHED" in capsys.readouterr().out
    (held,) = [f for f in inbox.load(tmp_vault) if f.check == "compile"]
    assert held.reason.startswith("mismatch")


def test_cmd_compile_apply_reports_unreachable_as_exit_3(
    tmp_vault, tmp_path, monkeypatch, capsys
):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    bundle_path, inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    monkeypatch.setattr(compile_mod, "tool_root", lambda vault: None)
    code = main(
        [
            "compile",
            "--vault",
            str(tmp_vault),
            "--bundle",
            str(bundle_path),
            "--approved-plan-sha256",
            inspected["approval_sha256"],
        ]
    )
    assert code == 3
    assert "UNREACHABLE" in capsys.readouterr().out


def test_compile_needs_a_key_or_all(tmp_vault, capsys):
    """Review I2: no KEY and no ``--all`` planned an empty bundle that read
    as valid. ``capture``'s own refusal, verbatim in shape."""
    with pytest.raises(SystemExit) as excinfo:
        main(["compile", "--vault", str(tmp_vault)])
    assert excinfo.value.code == 2
    err = capsys.readouterr().err
    assert err.endswith("error: compile needs at least one KEY or --all\n")


def test_cmd_compile_reports_an_unknown_key_and_plans_nothing(
    tmp_vault, tmp_path, monkeypatch, capsys
):
    """One row, held under ``compile``, exit 1, and no bundle: a selection
    that registers nothing has nothing to plan, and a plan that would only
    rewrite ``generated_at`` must not read as a pass."""
    _note(tmp_vault)
    root = _fake_tool(tmp_path, monkeypatch)
    code = main(["compile", "nosuchkey", "--vault", str(tmp_vault)])
    out, err = capsys.readouterr()
    assert code == 1
    assert (
        out
        == "UNMATCHED nosuchkey — not-captured — no literature note; capture it first\n"
    )
    assert err == "compile: nothing to register\n"
    assert not (root / "calls.jsonl").exists()
    assert not (tmp_vault / ".research-vault" / "compile").exists()
    (held,) = [f for f in inbox.load(tmp_vault) if f.check == "compile"]
    assert held.target == "nosuchkey"
    assert held.reason.startswith("not-captured")


def test_cmd_compile_reports_a_captured_key_without_text_and_plans_nothing(
    tmp_vault, tmp_path, monkeypatch, capsys
):
    """SKIPPED is never held, but a selection of only SKIPPED rows registered
    nothing — the one place a SKIPPED row moves the exit."""
    _note(tmp_vault)
    path = tmp_vault / "literatures" / "jakesch.etal2023a.md"
    path.write_text(
        must_replace(path.read_text(), 'compile-input-sha256: "' + "f" * 64 + '"\n', "")
    )
    _fake_tool(tmp_path, monkeypatch)
    code = main(["compile", "jakesch.etal2023a", "--vault", str(tmp_vault)])
    out, err = capsys.readouterr()
    assert code == 1
    assert out == (
        "SKIPPED jakesch.etal2023a — no-fulltext — no compile input recorded; "
        "nothing to register\n"
    )
    assert err == "compile: nothing to register\n"
    assert [f for f in inbox.load(tmp_vault) if f.check == "compile"] == []


def test_cmd_compile_all_on_a_vault_with_no_notes_registers_nothing(
    tmp_vault, tmp_path, monkeypatch, capsys
):
    _fake_tool(tmp_path, monkeypatch)
    code = main(["compile", "--all", "--vault", str(tmp_vault)])
    out, err = capsys.readouterr()
    assert code == 1
    assert out == ""
    assert err == "compile: nothing to register\n"


def test_cmd_compile_prints_the_rows_before_a_plan_that_registers_the_rest(
    tmp_vault, tmp_path, monkeypatch, capsys
):
    """A mixed selection: the row for the key that registered nothing, then
    the plan for the one that did; the UNMATCHED row sets exit 1 even though
    the plan is valid, exactly as a capture run with one UNMATCHED item."""
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    code = main(
        ["compile", "nosuchkey", "jakesch.etal2023a", "--vault", str(tmp_vault)]
    )
    out = capsys.readouterr().out
    assert code == 1
    row, rest = out.split("\n", 1)
    assert (
        row
        == "UNMATCHED nosuchkey — not-captured — no literature note; capture it first"
    )
    assert rest.startswith("{")
    assert "apply with: python3 -m research_vault compile --vault" in rest


def test_cmd_compile_a_skipped_row_beside_a_valid_plan_exits_zero(
    tmp_vault, tmp_path, monkeypatch, capsys
):
    _note(tmp_vault)
    _note(tmp_vault, key="notext", sha="a" * 64)
    path = tmp_vault / "literatures" / "notext.md"
    path.write_text(
        must_replace(path.read_text(), 'compile-input-sha256: "' + "a" * 64 + '"\n', "")
    )
    _fake_tool(tmp_path, monkeypatch)
    code = main(["compile", "notext", "jakesch.etal2023a", "--vault", str(tmp_vault)])
    out = capsys.readouterr().out
    assert code == 0
    assert out.startswith("SKIPPED notext — no-fulltext — ")


def test_cmd_compile_reports_a_corrupt_ledger_as_exit_2(
    tmp_vault, tmp_path, monkeypatch, capsys
):
    """Review I3: the sibling verbs' "could not run" shape — one stderr
    line, exit 2 — for the named failure, never a traceback."""
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    ledger = tmp_vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("{not json")
    code = main(["compile", "jakesch.etal2023a", "--vault", str(tmp_vault)])
    out, err = capsys.readouterr()
    assert code == 2
    assert out == ""
    assert err.startswith(
        "compile unavailable: wiki/meta/ledgers/source-ledger.json unreadable: "
    )


def test_cmd_compile_reports_a_missing_script_as_exit_3(tmp_vault, tmp_path, capsys):
    """A stale root on the plan leg: UNREACHABLE on stderr, naming the
    path, exit 3 — never a ``mismatch`` hold in the review queue."""
    _note(tmp_vault)
    root = tmp_path / "gone"
    root.mkdir()
    rv_dir = tmp_vault / ".research-vault"
    rv_dir.mkdir()
    (rv_dir / "machine.json").write_text(
        json.dumps({"claude_obsidian_root": str(root)})
    )
    code = main(["compile", "jakesch.etal2023a", "--vault", str(tmp_vault)])
    out, err = capsys.readouterr()
    assert code == 3
    assert out == ""
    assert err == (
        "UNREACHABLE compile — outage — claude-obsidian script not found: "
        f"{root / 'scripts' / 'claude-obsidian.py'}\n"
    )
    assert [f for f in inbox.load(tmp_vault) if f.check == "compile"] == []


def test_cmd_compile_apply_holds_a_missing_script_as_unreachable(
    tmp_vault, tmp_path, monkeypatch, capsys
):
    """The apply leg with a stale root: the UNREACHABLE row is held (an
    outage is a finding on the apply leg, as for ``capture``), exit 3."""
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    bundle_path, inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    root = tmp_path / "gone"
    root.mkdir()
    monkeypatch.setattr(compile_mod, "tool_root", lambda vault: root)
    code = main(
        [
            "compile",
            "--vault",
            str(tmp_vault),
            "--bundle",
            str(bundle_path),
            "--approved-plan-sha256",
            inspected["approval_sha256"],
        ]
    )
    out = capsys.readouterr().out
    assert code == 3
    assert out == (
        f"UNREACHABLE {bundle_path.stem} — outage — claude-obsidian script not "
        f"found: {root / 'scripts' / 'claude-obsidian.py'}\n"
    )
    (held,) = [f for f in inbox.load(tmp_vault) if f.check == "compile"]
    assert held.result == Result.UNREACHABLE.value
    assert held.reason.startswith("outage — claude-obsidian script not found: ")


def test_compile_refuses_an_approved_hash_without_a_bundle(tmp_vault, capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["compile", "--vault", str(tmp_vault), "--approved-plan-sha256", "abc123"])
    assert excinfo.value.code == 2
    # An exact suffix, not `in`: a mutant that wraps the whole message in
    # "XX...XX" still contains "--bundle" as a substring, so `in` alone
    # would not catch it; the trailing "XX" breaks an exact suffix match.
    err = capsys.readouterr().err
    assert err.endswith("error: compile: --approved-plan-sha256 requires --bundle\n")


def test_compile_requires_the_vault_flag():
    with pytest.raises(SystemExit) as excinfo:
        main(["compile", "somekey"])
    assert excinfo.value.code == 2


def test_compile_subparser_accepts_the_shared_base_flag(
    tmp_vault, tmp_path, monkeypatch
):
    """``parents=[common]`` is what gives ``compile`` the ``--base`` flag
    every other verb shares; dropped, argparse would refuse it as unknown."""
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    code = main(
        [
            "compile",
            "jakesch.etal2023a",
            "--vault",
            str(tmp_vault),
            "--base",
            "http://localhost:23129",
        ]
    )
    assert code == 0


# --- exact argv reaching the tool --------------------------------------


def test_run_invokes_the_tool_with_the_exact_argv(tmp_vault, tmp_path, monkeypatch):
    _note(tmp_vault)
    root = _fake_tool(tmp_path, monkeypatch)
    bundle_path, _inspected = compile_mod.plan(
        tmp_vault, ["jakesch.etal2023a"], today="2026-09-07"
    )
    assert _calls(root)[-1] == [
        "transaction",
        "inspect",
        str(bundle_path),
        "--vault",
        str(tmp_vault),
    ]

    compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert _calls(root)[-1] == [
        "transaction",
        "apply",
        str(bundle_path),
        "--approved-plan-sha256",
        "abc123",
        "--vault",
        str(tmp_vault),
    ]
