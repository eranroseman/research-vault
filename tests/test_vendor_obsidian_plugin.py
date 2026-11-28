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
    assert {"main.js", "manifest.json"} <= set(source["assets"])
    assert {p.name for p in folder.iterdir() if p.name in vendor.ASSETS} == set(
        source["assets"]
    )
    for name, digest in source["assets"].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest, name
    assert vendor.copyleft_banner((folder / "main.js").read_bytes()) is None
    if vendor.HOLDER_IN_TEXT.match(source["licence"]):
        holder = vendor.holder_of((folder / "LICENSE").read_text(errors="replace"))
        assert not vendor.is_placeholder(holder), holder
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
        ("(MIT OR GPL-3.0-or-later)", False),
        ("MIT AND Zlib", False),
        ("(MIT OR GPL-3.0) AND MPL-2.0", True),
        ("MPL-2.0 AND (MIT OR Apache-2.0)", True),
        ("(MIT OR Apache-2.0) AND (ISC OR BSD-3-Clause)", False),
        ("MIT AND Apache-2.0 OR GPL-3.0", False),
        ("GPL-2.0 OR LGPL-2.1", True),
        ("MIT AND Unknown-1.0", None),
        ("GPL-2.0-or-later WITH Classpath-exception-2.0", True),
        ("(MIT OR", None),
        ("MIT)", None),
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


@pytest.mark.parametrize(
    ("text", "holder", "placeholder"),
    [
        ("MIT License\n\nCopyright (c) 2021 Jane Doe\n", "Jane Doe", False),
        ("Copyright (c) [year] [fullname]\n", "[year] [fullname]", True),
        ("Copyright (c) 2024 <copyright holders>\n", "<copyright holders>", True),
        ("Copyright 2020 Local\n", "Local", True),
        (
            "2. Grant of Copyright License. Subject to the terms\n",
            "",
            True,
        ),
    ],
)
def test_holder_is_read_from_a_copyright_line_and_templates_are_refused(
    text, holder, placeholder
):
    assert vendor.holder_of(text) == holder
    assert vendor.is_placeholder(vendor.holder_of(text)) is placeholder


def test_verdict_reads_a_holder_only_where_the_licence_text_names_one():
    assert vendor.verdict("MIT", [], holder="[year] [fullname]") == "recommended"
    # Apache-2.0 names its Licensor outside LICENSE; the appendix template is
    # not a holder.
    assert vendor.verdict("Apache-2.0", [], holder="") == "seeded"


def test_copyleft_banner_finds_bundled_copyleft_code():
    assert vendor.copyleft_banner(b"/*! @license MPL-2.0 */ x()") is not None
    assert (
        vendor.copyleft_banner(b"// GNU Lesser General Public License v2.1") is not None
    )
    assert vendor.copyleft_banner(b"/* Licensed under the MIT license. */") is None


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
    # `A OR B` choice is covered when the expression names one side, an
    # `A AND B` side when it names both.
    bundled = {
        dep["licence"]
        for p in _seeded()
        for dep in json.loads((SEED / p.plugin_id / "SOURCE.json").read_text())[
            "bundled"
        ]
    }
    named = set(expression.split(" AND "))
    used = set()
    for licence in licences | bundled | {"MIT"}:
        choices = licence.strip("()").split(" OR ")
        covering = [c for c in choices if set(c.split(" AND ")) <= named]
        assert covering, licence
        used |= set(covering[0].split(" AND "))
    # exact: a licence no vendored file carries is not claimed either
    assert named == used, named - used
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
    dev_dependencies=None,
    lock=None,
    yarn=None,
    main_js=b"console.log('x')\n",
    styles=True,
    version="1.2.0",
    npm=None,
):
    api = "https://api.github.com/repos/" + _REPO
    raw = f"https://raw.githubusercontent.com/{_REPO}/{_COMMIT}/"
    assets = {
        "main.js": main_js,
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
        f"{raw}package.json": json.dumps(
            {
                "dependencies": dependencies or {},
                "devDependencies": dev_dependencies or {},
            }
        ).encode(),
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
    if yarn is not None:
        pages[f"{raw}yarn.lock"] = yarn.encode()
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


def test_write_plugin_demotes_a_main_js_that_bundles_copyleft_code(fake):
    pages, _ = _web()
    pages["https://dl/main.js"] = b"/*! @license GPL-3.0 */\nconsole.log('x')\n"
    folder = fake(pages)
    assert (
        vendor.write_plugin("sample-plugin", "1.2.0", registry="registry")
        == "recommended"
    )
    assert sorted(p.name for p in folder.iterdir()) == ["SOURCE.json"]
    source = json.loads((folder / "SOURCE.json").read_text())
    assert source["redistributable"] is False
    assert "@license GPL" in source["method"]


def test_write_plugin_leaves_no_record_when_a_write_fails(fake, monkeypatch):
    pages, _ = _web()
    folder = fake(pages)
    folder.mkdir()
    (folder / "SOURCE.json").write_text('{"redistributable": true}\n')
    original = Path.write_bytes

    def failing(self, data):
        if self.name == "LICENSE":
            raise OSError("disk full")
        return original(self, data)

    monkeypatch.setattr(Path, "write_bytes", failing)
    with pytest.raises(OSError, match="disk full"):
        vendor.write_plugin("sample-plugin", "1.2.0", registry="registry")
    assert not (folder / "SOURCE.json").exists()


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


def _names(folder):
    source = json.loads((folder / "SOURCE.json").read_text())
    return [(d["name"], d["version"]) for d in source["bundled"]]


def _mit(*specs):
    return {s: {"version": s.split("/")[-1], "license": "MIT"} for s in specs}


def test_bundled_is_the_lockfiles_transitive_production_closure(fake):
    # jszip's pako is two levels down and nested at a second version; npm marks
    # the dev-only tree `dev`, which stays out.
    pages, _ = _web(
        dependencies={"jszip": "^3.10.1"},
        dev_dependencies={"jest": "^29"},
        lock={
            "lockfileVersion": 3,
            "packages": {
                "": {
                    "name": "sample-plugin",
                    "dependencies": {"jszip": "^3.10.1"},
                    "devDependencies": {"jest": "^29"},
                },
                "node_modules/jszip": {"version": "3.10.1"},
                "node_modules/lie": {"version": "3.3.0"},
                "node_modules/pako": {"version": "1.0.11"},
                "node_modules/lie/node_modules/pako": {"version": "2.1.0"},
                "node_modules/jest": {"version": "29.7.0", "dev": True},
                "node_modules/ms": {"version": "2.1.3", "dev": True},
                "node_modules/fsevents": {"version": "2.3.3", "devOptional": True},
            },
        },
        npm=_mit(
            "jszip/3.10.1", "lie/3.3.0", "pako/1.0.11", "pako/2.1.0", "fsevents/2.3.3"
        ),
    )
    folder = fake(pages)
    assert vendor.write_plugin("sample-plugin", "1.2.0", registry="registry") == (
        "seeded"
    )
    assert _names(folder) == [
        ("fsevents", "2.3.3"),
        ("jszip", "3.10.1"),
        ("lie", "3.3.0"),
        ("pako", "1.0.11"),
        ("pako", "2.1.0"),
    ]
    notices = (folder / "THIRD-PARTY-NOTICES").read_text()
    assert "pako 1.0.11" in notices
    assert "jest" not in notices
    method = json.loads((folder / "SOURCE.json").read_text())["method"]
    assert "production closure of package-lock.json" in method
    assert "main.js scanned for a copyleft licence banner" in method


def test_yarn_v1_closure_follows_entries_and_v1_npm_nests():
    yarn = (
        "# yarn lockfile v1\n\n"
        '"handlebars@^4.7.6":\n  version "4.7.8"\n'
        '  resolved "https://registry.yarnpkg.com/handlebars/-/h.tgz"\n'
        '  dependencies:\n    source-map "^0.6.1"\n'
        '    "@x/y" "1"\n\n'
        'source-map@^0.6.1, source-map@~0.6.0:\n  version "0.6.1"\n\n'
        '"@x/y@1":\n  version "1.0.0"\n\n'
        'jest@^29:\n  version "29.7.0"\n'
    )
    package = {"dependencies": {"handlebars": "^4.7.6"}, "devDependencies": {}}
    locked = {
        (p.name, p.version, p.production) for p in vendor.yarn_lock(yarn, package)
    }
    assert locked == {
        ("handlebars", "4.7.8", True),
        ("source-map", "0.6.1", True),
        ("@x/y", "1.0.0", True),
        ("jest", "29.7.0", False),
    }
    v1 = {
        "lockfileVersion": 1,
        "dependencies": {
            "a": {"version": "1.0.0", "dependencies": {"b": {"version": "2.0.0"}}},
            "c": {"version": "3.0.0", "dev": True},
        },
    }
    assert {(p.name, p.production) for p in vendor.npm_lock(v1)} == {
        ("a", True),
        ("b", True),
        ("c", False),
    }
    with pytest.raises(SystemExit, match="Yarn 2"):
        vendor.yarn_lock("__metadata:\n  version: 6\n", package)


def test_a_dev_dependency_named_in_main_js_is_bundled(fake):
    pages, _ = _web(
        dev_dependencies={"moment": "^2", "tslib": "^2", "ms": "^2", "rollup": "^4"},
        main_js=b'var m = require("moment");\n// items, msg, 100ms\n'
        b"/* rollup's commonjs helpers */\n",
        lock={
            "packages": {
                "node_modules/moment": {"version": "2.29.4", "dev": True},
                "node_modules/tslib": {"version": "2.8.1", "dev": True},
                "node_modules/ms": {"version": "2.1.3", "dev": True},
                "node_modules/rollup": {"version": "4.0.0", "dev": True},
            }
        },
        npm=_mit("moment/2.29.4", "rollup/4.0.0"),
    )
    folder = fake(pages)
    assert vendor.write_plugin("sample-plugin", "1.2.0", registry="registry") == (
        "seeded"
    )
    assert _names(folder) == [("moment", "2.29.4"), ("rollup", "4.0.0")]


@pytest.mark.parametrize(
    ("name", "text", "present"),
    [
        ("pako", 'i=e("pako"),s=e("./utils")', True),
        ("pako", "this._pakoAction=e", False),
        ("jszip", "node_modules/jszip/lib/index.js", True),
        ("lodash.merge", "// lodash.merge 4.6.2", True),
        ("lodash", "lodash.merge", True),
        ("@codemirror/view", 'require("@codemirror/view")', True),
        ("ms", "100ms items", False),
        ("Moment", "moment", False),
    ],
)
def test_in_bundle_matches_a_whole_name_case_sensitively(name, text, present):
    tokens = set(vendor._NAME_CHAR.findall(text))
    assert vendor.in_bundle(name, text) is present
    assert vendor.in_bundle(name, text, tokens) is present


def test_host_provided_subtracts_only_what_main_js_requires(fake):
    """R64: a documented external that main.js only require()s is the app's;
    one main.js also carries in a path, or never names, stays listed.
    Where the lockfile resolved it from does not matter."""
    lishid = "git+ssh://git@github.com/lishid/cm-language.git#1aadcc2"
    pages, _ = _web(
        dependencies={
            "obsidian": "^1.4.0",
            "@codemirror/language": "https://github.com/lishid/cm-language",
            "@codemirror/state": "^6.0.1",
            "electron": "^30",
        },
        lock={
            "packages": {
                "node_modules/obsidian": {"version": "1.4.11", "resolved": lishid},
                "node_modules/@codemirror/language": {
                    "version": "6.6.0",
                    "resolved": lishid,
                },
                "node_modules/@codemirror/state": {
                    "version": "6.2.1",
                    "resolved": "https://registry.npmjs.org/@codemirror/state/-/state-6.2.1.tgz",
                },
                "node_modules/electron": {
                    "version": "30.0.0",
                    "resolved": "git+https://github.com/obsidianmd/x.git",
                },
            }
        },
        main_js=(
            b'var obsidian = require("obsidian"); new obsidian.Notice(".obsidian/x");\n'
            b"var l = require('@codemirror/language');\n"
            b"// node_modules/@codemirror/state/dist/index.js\n"
        ),
        npm={
            "@codemirror/state/6.2.1": {"version": "6.2.1", "license": "MIT"},
            "electron/30.0.0": {"version": "30.0.0", "license": "MIT"},
        },
    )
    folder = fake(pages)
    assert vendor.write_plugin("sample-plugin", "1.2.0", registry="registry") == (
        "seeded"
    )
    assert _names(folder) == [("@codemirror/state", "6.2.1"), ("electron", "30.0.0")]
    method = json.loads((folder / "SOURCE.json").read_text())["method"]
    assert "Obsidian's documented externals" in method


@pytest.mark.parametrize(
    ("name", "main_js", "subtracted"),
    [
        ("obsidian", 'const o = require("obsidian");', True),
        ("@codemirror/view", "e=require( '@codemirror/view' )", True),
        ("@lezer/lr", 'require("@lezer/lr");require("@lezer/lr")', True),
        ("fs", 'require("fs").readFileSync', True),
        # an identifier bound to the module, a config-folder string
        ("obsidian", 'var obsidian=require("obsidian");obsidian.Notice', True),
        ("obsidian", "require('obsidian'); p = \".obsidian/plugins\"", True),
        # mixed: required and also carried in the bundle
        ("@codemirror/view", 'require("@codemirror/view");/*@codemirror/view*/', False),
        (
            "@codemirror/state",
            'require("@codemirror/state");// node_modules/@codemirror/state/dist',
            False,
        ),
        ("obsidian", 'require("obsidian"); type: "obsidian"', False),
        # bundled only, or a subpath, or an aliased require
        ("@codemirror/state", '__commonJS({"@codemirror/state"(e){}})', False),
        ("@codemirror/state", 'require("@codemirror/state/dist/x")', False),
        ("electron", 'require2("electron")', False),
        # never named: over-attribution keeps it
        ("@codemirror/view", "console.log(1)", False),
        # not a documented external
        ("jszip", 'require("jszip")', False),
    ],
)
def test_is_host_provided_reads_require_only_occurrences(name, main_js, subtracted):
    assert vendor.is_host_provided(name, main_js) is subtracted


def test_is_host_provided_keeps_everything_without_a_main_js():
    assert vendor.is_host_provided("obsidian", None) is False


def test_host_provided_is_the_sample_plugins_externals_and_node_builtins():
    assert len(vendor.OBSIDIAN_EXTERNALS) == 13
    assert {"obsidian", "electron", "@lezer/lr", "@codemirror/collab"} <= (
        vendor.HOST_PROVIDED
    )
    assert {"fs", "path", "worker_threads", "fs/promises"} <= vendor.NODE_BUILTINS
    assert not any(n.startswith("node:") for n in vendor.NODE_BUILTINS)


def test_cc_by_4_0_is_established_and_carries_no_source_obligation():
    """R65: attribution only; the notices discharge its BY term."""
    assert vendor.has_source_obligation("CC-BY-4.0") is False
    assert vendor.has_source_obligation("(MIT AND CC-BY-4.0)") is False
    assert (
        vendor.verdict("MIT", [{"name": "icons", "licence": "CC-BY-4.0"}], holder="X")
        == "seeded"
    )
    assert vendor.has_source_obligation("CC-BY-SA-4.0") is None  # not established


def test_without_a_lockfile_the_closure_walks_the_registry_at_range_floors(fake):
    pages, _ = _web(
        dependencies={"chart.js": "^4.3.0"},
        dev_dependencies={
            "@codemirror/language": "https://github.com/lishid/cm-language",
            "@codemirror/view": "^6.4.0",
            "typescript": "^5",
        },
        main_js=b'require("@codemirror/language");require("@codemirror/view")\n',
        npm={
            "chart.js/4.3.0": {
                "version": "4.3.0",
                "license": "MIT",
                "dependencies": {"@kurkle/color": "^0.3.0"},
            },
            "@kurkle/color/0.3.0": {"version": "0.3.0", "license": "MIT"},
            "@codemirror/view/6.4.0": {"version": "6.4.0", "license": "MIT"},
        },
    )
    folder = fake(pages)
    assert vendor.write_plugin("sample-plugin", "1.2.0", registry="registry") == (
        "seeded"
    )
    # @codemirror/view is a dev name main.js only require()s: the app's (R64)
    assert _names(folder) == [("@kurkle/color", "0.3.0"), ("chart.js", "4.3.0")]
    method = json.loads((folder / "SOURCE.json").read_text())["method"]
    assert "no lockfile this script reads at the commit" in method


def test_without_a_package_json_nothing_is_bundled(fake):
    pages, _ = _web()
    del pages[f"https://raw.githubusercontent.com/{_REPO}/{_COMMIT}/package.json"]
    folder = fake(pages)
    assert vendor.write_plugin("sample-plugin", "1.2.0", registry="registry") == (
        "seeded"
    )
    assert _names(folder) == []
    assert (
        "No bundled third-party package" in (folder / "THIRD-PARTY-NOTICES").read_text()
    )
    method = json.loads((folder / "SOURCE.json").read_text())["method"]
    assert "no package.json at the commit" in method


def test_a_stale_lockfile_is_refused_for_the_registry_walk(fake):
    # The lockfile's root still lists a runtime dependency package.json moved
    # to dev: it describes an earlier tree, whose babel would be "production".
    pages, _ = _web(
        dependencies={"jszip": "^3.10.1"},
        dev_dependencies={"@rollup/plugin-babel": "^6"},
        lock={
            "lockfileVersion": 2,
            "packages": {
                "": {
                    "version": "0.0.1",
                    "dependencies": {"jszip": "^3.10.1", "@rollup/plugin-babel": "^6"},
                },
                "node_modules/jszip": {"version": "3.10.1"},
                "node_modules/@rollup/plugin-babel": {"version": "6.0.4"},
                "node_modules/caniuse-lite": {"version": "1.0.3"},
            },
        },
        npm={
            "jszip/3.10.1": {
                "version": "3.10.1",
                "license": "(MIT OR GPL-3.0-or-later)",
                "dependencies": {"pako": "~1.0.2"},
            },
            "pako/1.0.2": {"version": "1.0.2", "license": "(MIT AND Zlib)"},
        },
    )
    folder = fake(pages)
    assert vendor.write_plugin("sample-plugin", "1.2.0", registry="registry") == (
        "seeded"
    )
    assert _names(folder) == [("jszip", "3.10.1"), ("pako", "1.0.2")]
    method = json.loads((folder / "SOURCE.json").read_text())["method"]
    assert "package-lock.json names other dependencies than package.json" in method
    assert not vendor.stale({"packages": {"": {"version": "9"}}}, {"version": "1"})


def test_pnpm_v9_closure_follows_snapshots_and_refuses_a_stale_root():
    pnpm = (
        "lockfileVersion: '9.0'\n\nimporters:\n\n  .:\n    dependencies:\n"
        "      jszip:\n        specifier: ^3.10.1\n        version: 3.10.1\n"
        "    devDependencies:\n      '@codemirror/language':\n"
        "        specifier: https://github.com/lishid/cm-language\n"
        "        version: https://codeload.github.com/lishid/cm-language/tar.gz/cc6a\n"
        "\npackages:\n\n  jszip@3.10.1:\n    resolution: {integrity: x}\n"
        "\nsnapshots:\n\n  jszip@3.10.1:\n    dependencies:\n      pako: 1.0.11\n"
        "      lie: 3.3.0(peer@1.0.0)\n\n  lie@3.3.0(peer@1.0.0): {}\n\n"
        "  pako@1.0.11: {}\n\n"
        "  '@codemirror/language@https://codeload.github.com/lishid/cm-language/tar.gz/cc6a':\n"
        "    dependencies:\n      '@lezer/lr': 1.4.0\n\n  '@lezer/lr@1.4.0': {}\n"
    )
    package = {
        "dependencies": {"jszip": "^3.10.1"},
        "devDependencies": {"@codemirror/language": "x"},
    }
    locked = vendor.pnpm_lock(pnpm, package)
    assert locked is not None
    assert {(p.name, p.version, p.production) for p in locked} == {
        ("jszip", "3.10.1", True),
        ("pako", "1.0.11", True),
        ("lie", "3.3.0", True),
        (
            "@codemirror/language",
            "https://codeload.github.com/lishid/cm-language/tar.gz/cc6a",
            False,
        ),
        ("@lezer/lr", "1.4.0", False),
    }
    language = next(p for p in locked if p.name == "@codemirror/language")
    assert vendor.is_host_provided(language.name, 'require("@codemirror/language")')
    assert vendor.pnpm_lock(pnpm, {"dependencies": {"other": "1"}}) is None
    with pytest.raises(SystemExit, match="lockfileVersion 9"):
        vendor.pnpm_lock("lockfileVersion: '6.0'\n", package)


@pytest.mark.parametrize(
    ("spec", "floor"),
    [
        ("^2.11.2", "2.11.2"),
        ("0.10.x", "0.10.0"),
        ("~0.6", "0.6.0"),
        ("^1 || ^2", "1.0.0"),
        (">=1.2 <2", "1.2.0"),
        ("*", "latest"),
        ("2.0.0-beta.1", "2.0.0-beta.1"),
        (
            "https://github.com/lishid/cm-language",
            "https://github.com/lishid/cm-language",
        ),
    ],
)
def test_floor_is_a_registry_version(spec, floor):
    assert vendor._floor(spec) == floor


_DEMOTION = obsidian_plugins.Demotion(
    "Sample", "1.2.0", "Obsidian 9.9.9", "fails to load: TypeError x", "2026-11-27"
)


def test_write_plugin_demotes_a_declared_load_failure_after_the_licence_screen(
    fake, monkeypatch
):
    """R63: a measured load failure demotes an MIT plugin; the record keeps the
    licence screen's answer and names the error first."""
    pages, _ = _web()
    folder = fake(pages)
    monkeypatch.setattr(
        vendor,
        "load_demotion",
        lambda pid: _DEMOTION if pid == "sample-plugin" else None,
    )
    assert (
        vendor.write_plugin("sample-plugin", "1.2.0", registry="registry")
        == "recommended"
    )
    assert sorted(p.name for p in folder.iterdir()) == ["SOURCE.json"]
    source = json.loads((folder / "SOURCE.json").read_text())
    assert source["assets"] == {}
    assert source["redistributable"] is True  # the licence permits it
    assert source["source"] == f"https://github.com/{_REPO}/tree/1.2.0"
    assert source["method"].startswith(
        f"{vendor.LOAD_DEMOTED}: fails to load: TypeError x (Sample 1.2.0 on "
        "Obsidian 9.9.9, measured 2026-11-27); licence screen: LICENSE at the tag's"
    )


def test_reapply_demotes_the_committed_record_offline_and_is_idempotent(
    fake, monkeypatch
):
    pages, _ = _web()
    folder = fake(pages)
    assert (
        vendor.write_plugin("sample-plugin", "1.2.0", registry="registry") == "seeded"
    )
    seeded = json.loads((folder / "SOURCE.json").read_text())
    (folder / "data.json").write_text("{}\n")

    def offline(url):
        raise AssertionError(f"reapply fetched {url}")

    monkeypatch.setattr(vendor, "_get", offline)
    monkeypatch.setattr(vendor, "load_demotion", lambda pid: None)
    assert vendor.reapply("sample-plugin") == "seeded"  # nothing declared: untouched
    assert (folder / "main.js").exists()
    monkeypatch.setattr(vendor, "load_demotion", lambda pid: _DEMOTION)
    assert vendor.main(["sample-plugin", "--reapply"]) == 0
    assert sorted(p.name for p in folder.iterdir()) == ["SOURCE.json", "data.json"]
    once = json.loads((folder / "SOURCE.json").read_text())
    assert once == {
        **seeded,
        "assets": {},
        "source": f"https://github.com/{_REPO}/tree/1.2.0",
        "method": vendor.demoted_method(_DEMOTION, seeded["method"]),
    }
    assert vendor.reapply("sample-plugin") == "recommended"
    assert json.loads((folder / "SOURCE.json").read_text()) == once
    monkeypatch.setattr(vendor, "load_demotion", lambda pid: None)
    with pytest.raises(SystemExit, match="run with network"):
        vendor.reapply("sample-plugin")


def test_main_needs_a_tag_unless_reapplying(capsys):
    with pytest.raises(SystemExit):
        vendor.main(["sample-plugin"])
    assert "a tag is required" in capsys.readouterr().err


@pytest.mark.parametrize(
    "demotion", obsidian_plugins.declared().demotions, ids=lambda d: d.plugin
)
def test_each_declared_load_demotion_is_what_the_record_says(demotion):
    """The Need column is what the script wrote (decision 06): a demoted plugin
    is recommended, at the version measured, and its committed record carries
    the measured error and no asset."""
    plugin = obsidian_plugins.declared().by_name[demotion.plugin]
    assert plugin.need == "recommended"
    assert plugin.pin == demotion.version
    source = json.loads((SEED / plugin.plugin_id / "SOURCE.json").read_text())
    assert source["assets"] == {}
    assert source["method"].startswith(f"{vendor.LOAD_DEMOTED}: {demotion.error} (")


def test_a_recommended_record_ships_no_asset_and_a_seeded_one_is_not_demoted():
    declaration = obsidian_plugins.declared()
    for plugin in declaration.plugins:
        record = SEED / plugin.plugin_id / "SOURCE.json"
        if plugin.need == "recommended" and record.is_file():
            assert json.loads(record.read_text())["assets"] == {}, plugin.plugin_id
        if plugin.need == "seeded":
            assert declaration.demotion_for(plugin.plugin_id) is None
