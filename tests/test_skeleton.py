import json
from pathlib import Path

import research_vault
from research_vault import frontmatter

REPO = Path(__file__).resolve().parents[1]


def test_version_and_result_enum():
    assert research_vault.__version__ == "0.1.0"
    assert [r.name for r in research_vault.Result] == [
        "MATCHED",
        "UNMATCHED",
        "UNREACHABLE",
        "SKIPPED",
    ]


def test_plugin_manifest_valid():
    manifest = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "research-vault"
    assert manifest["version"] == "0.1.0"
    for key in ("description", "author", "license"):
        assert key in manifest


def test_marketplace_lists_plugin():
    market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())
    names = [p["name"] for p in market["plugins"]]
    assert "research-vault" in names


def test_tmp_vault_fixture(tmp_vault):
    for d in ("inbox", "literatures", "wiki", "log", "projects", "system"):
        assert (tmp_vault / d).is_dir()
    assert (tmp_vault / ".git").is_dir()


def test_fixture_daily_note_uses_ruled_type(fixture_vault):
    data, _ = frontmatter.parse((fixture_vault / "log" / "2026-08-16.md").read_text())

    assert data["type"] == "daily"
