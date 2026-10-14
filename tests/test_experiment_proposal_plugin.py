"""Plugin-scoped checks for ``plugins/experiment-proposal``.

Spec: ``docs/superpowers/specs/2026-10-13-experiment-proposal-plugin-design.md``,
section Tests. The plugin is a second plugin in this repository's marketplace
and shares no code with ``research_vault``; the repository's skill tests glob
only the root ``skills/``, so this module carries the plugin's own contract:
manifests, skill frontmatter and Codex metadata, provenance headers, licence
notices, the checklist's grammar and graph, the citations the skills make, the
paths they name, the vendored scripts and the R template.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "experiment-proposal"
MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"


def _canonical(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------
# Manifests
# --------------------------------------------------------------------------


def test_plugin_manifest_is_valid_and_canonical():
    """A manifest the plugin loader cannot parse fails at load with no message;
    a non-canonical one drifts from the repository's one JSON form owner."""
    assert MANIFEST.is_file(), f"{MANIFEST.relative_to(ROOT)} is missing"
    raw = MANIFEST.read_text(encoding="utf-8")
    manifest = json.loads(raw)
    assert raw == _canonical(manifest), (
        "plugin.json is not in canonical JSON form. Fix it with:\n"
        "    python -m json.tool --indent 2 --no-ensure-ascii "
        f"{MANIFEST.relative_to(ROOT)} {MANIFEST.relative_to(ROOT)}"
    )
    assert manifest["name"] == "experiment-proposal"
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]), manifest["version"]
    for key in ("description", "author", "license"):
        assert key in manifest, f"plugin.json lacks {key}"
    assert manifest["license"] == "MIT"


def test_marketplace_entry_names_the_plugin_and_resolves_to_its_folder():
    """The entry's name equals the manifest's name, carries no version (the
    version has one writer: plugin.json), and its source resolves to the folder
    that holds the plugin's own .claude-plugin/plugin.json."""
    market = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    entries = [p for p in market["plugins"] if p["name"] == "experiment-proposal"]
    assert len(entries) == 1, (
        "marketplace.json needs exactly one experiment-proposal entry"
    )
    entry = entries[0]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert entry["name"] == manifest["name"]
    assert "version" not in entry
    assert entry["source"] == "./plugins/experiment-proposal"
    source = (ROOT / entry["source"]).resolve()
    assert (source / ".claude-plugin" / "plugin.json") == MANIFEST.resolve()
    assert entry["description"].strip()


def test_plugin_ships_its_own_mit_licence():
    """A subdirectory install does not ship the repository's root LICENSE."""
    text = (PLUGIN / "LICENSE").read_text(encoding="utf-8")
    assert text.startswith("MIT License")
    assert "Copyright (c) 2026 Eran Roseman" in text
    assert "Permission is hereby granted, free of charge" in text
