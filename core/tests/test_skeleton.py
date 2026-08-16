import json
from pathlib import Path

import harness_core


REPO = Path(__file__).resolve().parents[2]


def test_version_and_result_enum():
    assert harness_core.__version__ == "0.1.0"
    assert [r.name for r in harness_core.Result] == [
        "MATCHED", "UNMATCHED", "UNREACHABLE", "SKIPPED",
    ]


def test_plugin_manifest_valid():
    manifest = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "knowledge-harness"
    assert manifest["version"] == "0.1.0"
    for key in ("description", "author", "license"):
        assert key in manifest


def test_marketplace_lists_plugin():
    market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())
    names = [p["name"] for p in market["plugins"]]
    assert "knowledge-harness" in names


def test_tmp_vault_fixture(tmp_vault):
    for d in ("+", "literatures", "atlas", "calendar", "efforts", "x"):
        assert (tmp_vault / d).is_dir()
    assert (tmp_vault / ".git").is_dir()
