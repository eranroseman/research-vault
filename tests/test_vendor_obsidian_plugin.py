import hashlib
import json
from pathlib import Path

import pytest

from research_vault import obsidian_plugins
from scripts import vendor_obsidian_plugin as vendor

SEED = (
    Path(__file__).resolve().parents[1]
    / "research_vault"
    / "templates"
    / "obsidian"
    / "plugins"
)


def _seeded():
    return [p for p in obsidian_plugins.declared().plugins if p.need == "seeded"]


@pytest.mark.parametrize("plugin", _seeded(), ids=lambda p: p.plugin_id)
def test_each_seeded_plugin_carries_its_assets_record_and_licence(plugin):
    folder = SEED / plugin.plugin_id
    source = json.loads((folder / "SOURCE.json").read_text())
    assert set(source) == {
        "repo",
        "tag",
        "commit",
        "assets",
        "licence",
        "bundled",
        "source",
        "redistributable",
        "measured",
        "method",
    }
    assert source["tag"] == plugin.pin
    assert source["redistributable"] is True
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["id"] == plugin.plugin_id
    assert (
        manifest["version"] == plugin.pin
    )  # the tag is the version; SOURCE.json has no version field
    for name, digest in source["assets"].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest, name
    assert (folder / "LICENSE").is_file()
    assert (folder / "THIRD-PARTY-NOTICES").is_file()
    assert vendor.has_source_obligation(source["licence"]) is False
    assert all(
        vendor.has_source_obligation(dep["licence"]) is False
        for dep in source["bundled"]
    )


@pytest.mark.parametrize(
    "plugin",
    [p for p in obsidian_plugins.declared().plugins if p.need == "recommended"],
    ids=lambda p: p.plugin_id,
)
def test_a_recommended_plugin_ships_no_asset(plugin):
    folder = SEED / plugin.plugin_id
    if folder.exists():
        # data.json (Task 2) and, for a plugin the script demoted, the
        # SOURCE.json that says why; neither loads anything in Obsidian.
        assert {p.name for p in folder.iterdir()} <= {"data.json", "SOURCE.json"}


@pytest.mark.parametrize(
    ("licence", "obligation"),
    [
        ("MIT", False),
        ("Apache-2.0", False),
        ("BSD-3-Clause", False),
        ("ISC", False),
        ("0BSD", False),
        ("GPL-3.0", True),
        ("GPL-3.0-only", True),
        ("AGPL-3.0-or-later", True),
        ("LGPL-2.1", True),
        ("MPL-2.0", True),
        ("CPAL-1.0", True),
        ("EUPL-1.2", True),
        ("UNLICENSED", None),
        ("", None),
        (None, None),
        ("SEE LICENSE IN x", None),
    ],
)
def test_has_source_obligation_reads_spdx_and_refuses_the_unknown(licence, obligation):
    assert vendor.has_source_obligation(licence) is obligation


def test_verdict_demotes_copyleft_placeholder_and_unestablished(tmp_path):
    assert (
        vendor.verdict("MIT", [{"name": "a", "licence": "MIT"}], holder="Jane Doe")
        == "seeded"
    )
    assert (
        vendor.verdict("MIT", [{"name": "ical.js", "licence": "MPL-2.0"}], holder="X")
        == "recommended"
    )
    assert vendor.verdict("GPL-3.0", [], holder="X") == "recommended"
    assert (
        vendor.verdict("MIT", [], holder="Local") == "recommended"
    )  # a placeholder holder does not establish the grant
    assert vendor.verdict(None, [], holder="X") == "recommended"


def test_attribution_names_every_seeded_plugin_id():
    text = (Path(__file__).resolve().parents[1] / "ATTRIBUTION.md").read_text()
    for plugin in _seeded():
        assert f"`{plugin.plugin_id}`" in text, plugin.plugin_id
    assert "SOURCE.json" in text
    assert "provenance header at the top of the file" not in text


def test_pyproject_license_expression_names_every_vendored_licence():
    import tomllib

    pyproject = tomllib.loads(
        (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text()
    )
    expression = pyproject["project"]["license"]
    licences = {
        json.loads((SEED / p.plugin_id / "SOURCE.json").read_text())["licence"]
        for p in _seeded()
    }
    # The bundled code ships inside main.js, so its licences ride too; an
    # `A OR B` choice is covered when the expression names one side.
    bundled = {
        dep["licence"]
        for p in _seeded()
        for dep in json.loads((SEED / p.plugin_id / "SOURCE.json").read_text())[
            "bundled"
        ]
    }
    for licence in licences | bundled | {"MIT"}:
        choices = licence.strip("()").split(" OR ")
        assert any(choice in expression.split(" AND ") for choice in choices), licence
    files = pyproject["project"]["license-files"]
    assert "research_vault/templates/obsidian/plugins/*/LICENSE" in files
    assert "research_vault/templates/obsidian/plugins/*/THIRD-PARTY-NOTICES" in files


# The network legs, faked: write_plugin reads every URL through vendor._get,
# so a dict of canned bodies keeps these hermetic.

_REPO = "someone/sample-plugin"
_COMMIT = "c0ffee" * 6 + "abcd"
_MIT = (
    b"MIT License\n\nCopyright (c) 2024 Jane Doe\n\n"
    b"Permission is hereby granted, free of charge, to any person ...\n"
)
_GPL = b"                    GNU GENERAL PUBLIC LICENSE\n                       Version 3, 29 June 2007\n"


def _web(
    *,
    licence=_MIT,
    dependencies=None,
    lock=None,
    styles=True,
    version="1.2.0",
    npm=None,
):
    api = "https://api.github.com/repos/" + _REPO
    raw = f"https://raw.githubusercontent.com/{_REPO}/{_COMMIT}/"
    assets = {
        "main.js": b"console.log('x')\n",
        "manifest.json": json.dumps(
            {"id": "sample-plugin", "version": version}
        ).encode(),
    }
    if styles:
        assets["styles.css"] = b".x{}\n"
    pages = {
        "registry": json.dumps(
            [{"id": "other", "repo": "o/o"}, {"id": "sample-plugin", "repo": _REPO}]
        ).encode(),
        f"{api}/git/ref/tags/1.2.0": json.dumps(
            {"object": {"type": "tag", "url": f"{api}/git/tags/abc"}}
        ).encode(),
        f"{api}/git/tags/abc": json.dumps(
            {"object": {"type": "commit", "sha": _COMMIT}}
        ).encode(),
        f"{api}/git/trees/{_COMMIT}": json.dumps(
            {
                "tree": [
                    {"path": "LICENSE", "type": "blob"},
                    {"path": "src", "type": "tree"},
                ]
            }
        ).encode(),
        f"{raw}LICENSE": licence,
        f"{raw}package.json": json.dumps({"dependencies": dependencies or {}}).encode(),
        f"{api}/releases/tags/1.2.0": json.dumps(
            {
                "assets": [
                    {"name": n, "browser_download_url": f"https://dl/{n}"}
                    for n in assets
                ]
            }
        ).encode(),
    }
    if lock is not None:
        pages[f"{raw}package-lock.json"] = json.dumps(lock).encode()
    for name, body in assets.items():
        pages[f"https://dl/{name}"] = body
    for url, body in (npm or {}).items():
        pages[f"https://registry.npmjs.org/{url}"] = json.dumps(body).encode()
    return pages, assets


@pytest.fixture
def fake(monkeypatch, tmp_path):
    def install(pages):
        def get(url):
            if url not in pages:
                raise vendor.urllib.error.HTTPError(url, 404, "Not Found", None, None)  # type: ignore[arg-type]
            return pages[url]

        monkeypatch.setattr(vendor, "_get", get)
        monkeypatch.setattr(vendor, "PLUGINS", tmp_path)
        return tmp_path / "sample-plugin"

    return install


def test_write_plugin_seeds_byte_for_byte_with_the_lockfile_version(fake):
    pages, assets = _web(
        dependencies={"tiny": "^2.0.0", "obsidian": "obsidianmd/obsidian-api#master"},
        lock={"packages": {"node_modules/tiny": {"version": "2.3.1"}}},
        npm={"tiny/2.3.1": {"version": "2.3.1", "license": "ISC"}},
    )
    folder = fake(pages)
    assert (
        vendor.write_plugin(
            "sample-plugin", "1.2.0", registry="registry", today="2026-01-02"
        )
        == "seeded"
    )
    for name, body in assets.items():
        assert (folder / name).read_bytes() == body
    assert (folder / "LICENSE").read_bytes() == _MIT
    source = json.loads((folder / "SOURCE.json").read_text())
    assert source["commit"] == _COMMIT
    assert source["licence"] == "MIT"
    assert source["redistributable"] is True
    assert source["assets"] == {
        n: hashlib.sha256(b).hexdigest() for n, b in assets.items()
    }
    assert source["bundled"] == [
        {
            "name": "tiny",
            "version": "2.3.1",
            "licence": "ISC",
            "url": "https://www.npmjs.com/package/tiny",
        }
    ]
    assert "tiny 2.3.1" in (folder / "THIRD-PARTY-NOTICES").read_text()


def test_write_plugin_demotes_a_copyleft_licence_and_removes_stale_assets(fake):
    pages, _ = _web(licence=_GPL)
    folder = fake(pages)
    folder.mkdir()
    (folder / "data.json").write_text("{}\n")
    (folder / "main.js").write_text("stale")
    assert (
        vendor.write_plugin("sample-plugin", "1.2.0", registry="registry")
        == "recommended"
    )
    assert sorted(p.name for p in folder.iterdir()) == ["SOURCE.json", "data.json"]
    source = json.loads((folder / "SOURCE.json").read_text())
    assert source["redistributable"] is False
    assert source["licence"] == "GPL-3.0"
    assert source["assets"] == {}


def test_write_plugin_demotes_a_dependency_the_registry_cannot_answer(fake):
    pages, _ = _web(dependencies={"ghost": "^1.0.0"})
    folder = fake(pages)
    assert (
        vendor.write_plugin("sample-plugin", "1.2.0", registry="registry")
        == "recommended"
    )
    assert not (folder / "main.js").exists()


def test_write_plugin_refuses_a_manifest_off_the_tag_and_writes_nothing(fake):
    pages, _ = _web(version="1.1.9", styles=False)
    folder = fake(pages)
    with pytest.raises(SystemExit, match="manifest version"):
        vendor.write_plugin("sample-plugin", "1.2.0", registry="registry")
    assert not folder.exists() or not any(folder.iterdir())
