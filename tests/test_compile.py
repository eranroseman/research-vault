import hashlib
import json
from pathlib import Path

import pytest

from research_vault import Result, inbox
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


def _fake_tool(tmp_path, monkeypatch, *, inspect_ok=True, apply_code=0):
    root = tmp_path / "tool"
    (root / "scripts").mkdir(parents=True)
    script = root / "scripts" / "claude-obsidian.py"
    script.write_text(
        "import json,sys\n"
        "args=sys.argv[1:]\n"
        "if args[:2]==['transaction','inspect']:\n"
        f"    print(json.dumps({{'schema':'claude-obsidian.transaction-plan.v1','valid':{inspect_ok!s},'approval_sha256':'abc123','changed_paths':['wiki/meta/ledgers/source-ledger.json']}}))\n"
        "elif args[:2]==['transaction','apply']:\n"
        "    assert '--approved-plan-sha256' in args\n"
        f"    print(json.dumps({{'schema':'claude-obsidian.transaction-result.v1','operation_id':'op','changed_paths':['wiki/meta/ledgers/source-ledger.json']}})); sys.exit({apply_code})\n"
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


def test_compile_refuses_an_approved_hash_without_a_bundle(tmp_vault, capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["compile", "--vault", str(tmp_vault), "--approved-plan-sha256", "abc123"])
    assert excinfo.value.code == 2
    assert "--bundle" in capsys.readouterr().err
