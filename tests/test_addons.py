import json
import re
import zipfile
from pathlib import Path

import pytest

from research_vault import addons
from tests.conftest import must_replace


def test_declared_parses_both_tables_strictly():
    declaration = addons.declared()
    bbt = declaration.by_id["better-bibtex@iris-advies.com"]
    assert bbt == addons.Addon(
        "Better BibTeX",
        "better-bibtex@iris-advies.com",
        "required",
        None,
        "extensions.zotero.translators.better-bibtex.",
        "research, long-form writing",
    )
    doi = declaration.by_id["zoteroshortdoi@wiernik.org"]
    assert (doi.need, doi.min_version) == ("recommended", "2.2.0")
    assert {a.need for a in declaration.addons} == set(addons.NEEDS)
    needs = [a.need for a in declaration.addons]
    assert needs.count("required") == 1
    assert needs.count("recommended") == 7
    assert needs.count("optional") == 19
    assert needs.count("excluded") >= 20
    # ruling 9: never declared; spec 6.1 omits load-failure-only rows (DP7)
    for absent in (
        "zotero-mcp-plugin@autoagent.my",
        "getcitation@example.com",
        "zotadata@zotero.org",
    ):
        assert absent not in declaration.by_id
    assert declaration.settings_for("zoteroshortdoi@wiernik.org") == [
        addons.Setting("DOI Manager", "extensions.shortdoi.autoretrieve", ('"none"',)),
        addons.Setting("DOI Manager", "extensions.shortdoi.monthly_verify", ("false",)),
    ]
    assert (
        addons.Setting(
            "Citation counts",
            "extensions.citationcounts.autoretrieve",
            ('"none"', "unset"),
        )
        in declaration.settings
    )
    # DP9: onAdded stays false until Task 4's live leg verifies the key set
    assert (
        addons.Setting(
            "Linter for Zotero",
            "extensions.zotero.formatmetadata.lint.onAdded",
            ("false",),
        )
        in declaration.settings
    )
    # R37: MarkDB-Connect's keys as its 0.2.4 xpi ships them (read 2026-11-27)
    assert declaration.settings_for("daeda@mit.edu") == [
        addons.Setting(
            "MarkDB-Connect", "extensions.zotero.mdbc.removetags", ('"addonly"',)
        ),
        addons.Setting("MarkDB-Connect", "extensions.zotero.mdbc.sourcedir", ("set",)),
        addons.Setting(
            "MarkDB-Connect", "extensions.zotero.mdbc.matchstrategy", ('"citekeyyaml"',)
        ),
        addons.Setting(
            "MarkDB-Connect", "extensions.zotero.mdbc.yamlkeyword", ('"citationKey"',)
        ),
        addons.Setting(
            "MarkDB-Connect",
            "extensions.zotero.mdbc.filefilterstrategy",
            ('"customfileregexp"',),
        ),
        addons.Setting(
            "MarkDB-Connect", "extensions.zotero.mdbc.filepattern", ('"^.+\\\\.md$"',)
        ),
    ]
    rules = [
        s
        for s in declaration.settings
        if s.pref.startswith("extensions.zotero.formatmetadata.rule.")
    ]
    assert len(rules) == 29
    names = {a.name for a in declaration.addons}
    for setting in declaration.settings:
        assert setting.addon in names, setting
        for literal in setting.accepted:
            assert (
                literal in {"unset", "set", "true", "false"}
                or literal.lstrip("-").isdigit()
                or (literal.startswith('"') and literal.endswith('"'))
            ), literal


def _packaged(monkeypatch, tmp_path, text):
    package = tmp_path / "pkg"
    (package / "templates").mkdir(parents=True, exist_ok=True)
    (package / "templates" / "zotero-addons.md").write_text(text, encoding="utf-8")
    monkeypatch.setattr(addons.resources, "files", lambda _name: package)


_GOOD = (
    Path(__file__).resolve().parents[1]
    / "research_vault"
    / "templates"
    / "zotero-addons.md"
).read_text(encoding="utf-8")


def test_a_row_the_grammar_cannot_read_raises(monkeypatch, tmp_path):
    """A typo must not delete a check silently (designs cluster 5 (a) [added])."""
    _packaged(
        monkeypatch,
        tmp_path,
        must_replace(_GOOD, "| recommended |", "| recomended |"),
    )
    with pytest.raises(ValueError, match=r"zotero-addons\.md: unreadable row"):
        addons.declared()
    _packaged(
        monkeypatch, tmp_path, _GOOD + "| Nobody | `extensions.nobody.x` | `true` |\n"
    )
    with pytest.raises(ValueError, match="names no declared add-on"):
        addons.declared()


@pytest.mark.parametrize(
    ("old", "new", "reason"),
    [
        (
            "| `extensions.shortdoi.monthly_verify`",
            "| —",
            "(no preference)",
        ),
        ("| `false`, `unset`", "| `maybe`", "(accepted literals)"),
        ("| `false`, `unset`", "| ", "unreadable row"),
        (
            "`zoteroshortdoi@wiernik.org`",
            "zoteroshortdoi@wiernik.org",
            "unreadable row",
        ),
    ],
)
def test_a_cell_the_grammar_cannot_read_names_the_row(
    monkeypatch, tmp_path, old, new, reason
):
    """DP5: an empty or `—` Preference cell raises like a missing add-on id."""
    _packaged(monkeypatch, tmp_path, must_replace(_GOOD, old, new))
    with pytest.raises(ValueError, match=re.escape(reason)):
        addons.declared()


def test_a_table_row_outside_a_known_table_raises(monkeypatch, tmp_path):
    _packaged(monkeypatch, tmp_path, "| a | b |\n" + _GOOD)
    with pytest.raises(ValueError, match="outside a known table"):
        addons.declared()


def test_observe_reads_active_and_app_disabled_from_the_running_profile(tmp_path):
    (tmp_path / "extensions.json").write_text(
        json.dumps(
            {
                "addons": [
                    {
                        "id": "better-bibtex@iris-advies.com",
                        "type": "extension",
                        "location": "app-profile",
                        "version": "9.0.63",
                        "active": True,
                        "appDisabled": False,
                        "userDisabled": False,
                    },
                    {
                        "id": "zoteroshortdoi@wiernik.org",
                        "type": "extension",
                        "location": "app-profile",
                        "version": "1.6.0",
                        "active": False,
                        "appDisabled": True,
                        "userDisabled": False,
                    },
                    {
                        "id": "something@app",
                        "type": "extension",
                        "location": "app-global",
                        "version": "1",
                    },
                ]
            }
        )
    )
    observed = addons.observe(tmp_path)
    assert observed["better-bibtex@iris-advies.com"] == {
        "version": "9.0.63",
        "active": True,
        "appDisabled": False,
    }
    assert observed["zoteroshortdoi@wiernik.org"]["appDisabled"] is True
    assert "something@app" not in observed


def test_read_prefs_parses_user_pref_lines(tmp_path):
    (tmp_path / "prefs.js").write_text(
        'user_pref("extensions.zotero.sync.fulltext.enabled", false);\n'
        'user_pref("extensions.zotero.sync.storage.protocol", "webdav");\n'
        'user_pref("extensions.zotero.pmcid.auto", true);\n'
        'user_pref("extensions.zotero.httpServer.port", 23129);\n'
    )
    prefs = addons.read_prefs(tmp_path)
    assert prefs == {
        "extensions.zotero.sync.fulltext.enabled": False,
        "extensions.zotero.sync.storage.protocol": "webdav",
        "extensions.zotero.pmcid.auto": True,
        "extensions.zotero.httpServer.port": 23129,
    }


def test_read_prefs_keeps_the_raw_token_for_a_string_json_refuses(tmp_path):
    # A JS escape JSON does not accept must not fail the whole file: one odd
    # line would otherwise turn three doctor probes into a fault.
    odd = "it\\'s"  # the token as prefs.js carries it: it\'s, in double quotes
    (tmp_path / "prefs.js").write_text(
        f'user_pref("extensions.zotero.note.fontFamily", "{odd}");\n'
        'user_pref("extensions.zotero.pmcid.auto", true);\n'
    )
    prefs = addons.read_prefs(tmp_path)
    assert prefs == {
        "extensions.zotero.note.fontFamily": f'"{odd}"',
        "extensions.zotero.pmcid.auto": True,
    }


def test_a_foreign_addon_and_a_stray_line_are_passed_over_not_the_end_of_the_walk(
    tmp_path,
):
    """A theme and an app-global add-on listed FIRST do not stop `observe`
    from reading the profile add-on after them; a comment and a blank line
    before a `user_pref` do not stop `read_prefs` from reading it."""
    (tmp_path / "extensions.json").write_text(
        json.dumps(
            {
                "addons": [
                    {
                        "id": "theme@mozilla.org",
                        "type": "theme",
                        "location": "app-profile",
                    },
                    {"id": "global@app", "type": "extension", "location": "app-global"},
                    {
                        "id": "better-bibtex@iris-advies.com",
                        "type": "extension",
                        "location": "app-profile",
                        "version": "9.0.63",
                        "active": True,
                        "appDisabled": False,
                    },
                ]
            }
        )
    )
    assert addons.observe(tmp_path) == {
        "better-bibtex@iris-advies.com": {
            "version": "9.0.63",
            "active": True,
            "appDisabled": False,
        }
    }
    (tmp_path / "prefs.js").write_text(
        "// Mozilla User Preferences\n"
        "\n"
        'user_pref("extensions.zotero.pmcid.auto", true);\n'
        "not a pref line\n"
        'user_pref("extensions.zotero.dataDir", "D:\\\\Zotero");\n'
    )
    assert addons.read_prefs(tmp_path) == {
        "extensions.zotero.pmcid.auto": True,
        "extensions.zotero.dataDir": "D:\\Zotero",
    }


def test_observe_reads_an_extensions_file_without_an_addons_list_as_empty(tmp_path):
    (tmp_path / "extensions.json").write_text(json.dumps({"schemaVersion": 35}))
    assert addons.observe(tmp_path) == {}


def test_declared_names_a_non_utf8_declaration(monkeypatch, tmp_path):
    package = tmp_path / "pkg"
    (package / "templates").mkdir(parents=True)
    (package / "templates" / "zotero-addons.md").write_bytes(b"\xff\xfe")
    monkeypatch.setattr(addons.resources, "files", lambda _name: package)
    with pytest.raises(ValueError, match=r"zotero-addons\.md: not UTF-8"):
        addons.declared()


def test_read_prefs_reads_a_negative_number_not_a_quoted_token(tmp_path):
    """`raw.lstrip("-")` decides the branch: a `lstrip(None)`
    (whitespace-strip) or `rstrip("-")` mutant leaves the leading `-` in
    place, `isdigit()` then reads False, and the value falls through to
    `_string_pref`'s raw-token path instead of `int()`."""
    (tmp_path / "prefs.js").write_text(
        'user_pref("extensions.zotero.some.negative", -5);\n'
    )
    prefs = addons.read_prefs(tmp_path)
    assert prefs == {"extensions.zotero.some.negative": -5}


def _xpi(profile, addon_id, files):
    folder = profile / "extensions"
    folder.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(folder / f"{addon_id}.xpi", "w") as archive:
        for name, text in files.items():
            archive.writestr(name, text)


def test_literal_spells_values_as_prefs_js_does():
    assert addons.literal(True) == "true"
    assert addons.literal(False) == "false"
    assert addons.literal(2) == "2"
    assert addons.literal(-1) == "-1"
    assert addons.literal("none") == '"none"'
    assert addons.literal("") == '""'
    assert addons.literal('it"s') == '"it\\"s"'


def test_xpi_defaults_read_full_and_relative_keys(tmp_path):
    """Designs cluster 5 (a) [corrected]: BBT 9.0.68 ships `pref("git", "config")`
    with no semicolon and a key relative to its prefix; the five other surveyed
    xpis ship full keys with semicolons."""
    _xpi(
        tmp_path,
        "better-bibtex@iris-advies.com",
        {"prefs.js": 'pref("git", "config")\npref("autoExport", "immediate")\n'},
    )
    _xpi(
        tmp_path,
        "zoteroshortdoi@wiernik.org",
        {
            "defaults/preferences/prefs.js": (
                'pref("extensions.shortdoi.autoretrieve", "long");\n'
                'pref("extensions.shortdoi.monthly_verify", true);\n'
            )
        },
    )
    assert addons.xpi_defaults(tmp_path, "better-bibtex@iris-advies.com") == {
        "git": '"config"',
        "autoExport": '"immediate"',
    }
    assert addons.xpi_defaults(tmp_path, "zoteroshortdoi@wiernik.org") == {
        "extensions.shortdoi.autoretrieve": '"long"',
        "extensions.shortdoi.monthly_verify": "true",
    }
    # no xpi: nothing to read
    assert addons.xpi_defaults(tmp_path, "zotero-pmcid-fetcher@iris-advies.com") == {}


def test_set_accepts_any_value_but_an_absent_or_empty_one():
    """R37: `set` mirrors `unset` for a setting whose value is the person's own
    (MarkDB-Connect's source folder): any effective value but none or `""`."""
    assert addons.accepts(("set",), '"/v/literature"')
    assert addons.accepts(("set",), "true")
    assert not addons.accepts(("set",), '""')
    assert not addons.accepts(("set",), "unset")
    assert addons.accepts(('"none"', "unset"), "unset")
    assert not addons.accepts(('"none"',), '"long"')


def test_xpi_defaults_read_single_quoted_lines_as_prefs_js_literals(tmp_path):
    """ZotMoov 1.2.32's root prefs.js quotes with single quotes and builds two
    values with JSON.stringify (xpi read 2026-11-27, sha256 7770dc2c…). A
    single-quoted string reads as the double-quoted literal prefs.js would
    write; a value that is not a literal keeps its token, which no declared
    literal matches."""
    _xpi(
        tmp_path,
        "zotmoov@wileyy.com",
        {
            "prefs.js": (
                "// ZotMoov\n"
                "pref('extensions.zotmoov.enable_automove', true);\n"
                "pref('extensions.zotmoov.file_behavior', 'move');\n"
                "pref('extensions.zotmoov.dst_dir', '');\n"
                "pref('extensions.zotmoov.auto_process_delay', 5000);\n"
                "pref('extensions.zotmoov.allowed_fileext', "
                "JSON.stringify(['pdf', 'epub']))\n"
            )
        },
    )
    assert addons.xpi_defaults(tmp_path, "zotmoov@wileyy.com") == {
        "extensions.zotmoov.enable_automove": "true",
        "extensions.zotmoov.file_behavior": '"move"',
        "extensions.zotmoov.dst_dir": '""',
        "extensions.zotmoov.auto_process_delay": "5000",
        "extensions.zotmoov.allowed_fileext": "JSON.stringify(['pdf', 'epub'])",
    }


def test_xpi_defaults_root_prefs_js_wins_over_defaults_preferences(tmp_path):
    """DP21: the first occurrence wins, and the root prefs.js is read first."""
    _xpi(
        tmp_path,
        "both@x",
        {
            "defaults/preferences/a.js": 'pref("extensions.both.k", 1);\n',
            "prefs.js": 'pref("extensions.both.k", 2);\npref("extensions.both.k", 3);\n',
        },
    )
    assert addons.xpi_defaults(tmp_path, "both@x") == {"extensions.both.k": "2"}


def test_xpi_defaults_name_an_unreadable_archive_or_line(tmp_path):
    (tmp_path / "extensions").mkdir()
    (tmp_path / "extensions" / "broken@x.xpi").write_bytes(b"not a zip")
    with pytest.raises(addons.DefaultsUnreadableError, match=re.escape("broken@x.xpi")):
        addons.xpi_defaults(tmp_path, "broken@x")
    with pytest.raises(addons.DefaultsUnreadableError, match=re.escape("broken@x.xpi")):
        addons.xpi_defaults(tmp_path, "broken@x", keys=["extensions.other"])
    _xpi(
        tmp_path,
        "odd@x",
        {"prefs.js": 'pref("extensions.odd.a", true);\npref(extensions.odd.b, 1);\n'},
    )
    with pytest.raises(
        addons.DefaultsUnreadableError, match=re.escape("extensions.odd.b")
    ):
        addons.xpi_defaults(tmp_path, "odd@x")


def test_xpi_defaults_raises_on_an_unreadable_line_only_when_it_names_a_wanted_key(
    tmp_path,
):
    """DP22 / spec 6.1: a line naming the key the grammar cannot read is
    UNREACHABLE, never unset; a broken line about another key is not."""
    _xpi(
        tmp_path,
        "odd@x",
        {"prefs.js": 'pref("extensions.odd.a", true);\npref(extensions.odd.b, 1);\n'},
    )
    assert addons.xpi_defaults(tmp_path, "odd@x", keys=["extensions.odd.a"]) == {
        "extensions.odd.a": "true"
    }
    with pytest.raises(
        addons.DefaultsUnreadableError, match=re.escape("extensions.odd.b")
    ):
        addons.xpi_defaults(tmp_path, "odd@x", keys=["extensions.odd.b"])
    _xpi(tmp_path, "rel@x", {"prefs.js": "pref(git, 'off')\n"})
    with pytest.raises(addons.DefaultsUnreadableError, match="git"):
        addons.xpi_defaults(
            tmp_path, "rel@x", keys=["extensions.rel.git"], key_prefix="extensions.rel."
        )


def test_unreadable_pref_lines_are_the_lines_the_grammar_refuses(tmp_path):
    """DP22: the profile's prefs.js gets the same rule as an xpi's defaults:
    doctor reads which declared keys sit on a line it cannot parse."""
    (tmp_path / "prefs.js").write_text(
        "// Mozilla User Preferences\n"
        "\n"
        'user_pref("extensions.zotero.pmcid.auto", false);\n'
        "user_pref(extensions.shortdoi.autoretrieve, 'none');\n"
    )
    assert addons.unreadable_pref_lines(tmp_path) == (
        "user_pref(extensions.shortdoi.autoretrieve, 'none');",
    )


def test_effective_value_prefers_prefs_js_then_the_default_then_unset():
    prefs = {"extensions.shortdoi.autoretrieve": "none"}
    defaults = {"extensions.shortdoi.monthly_verify": "true", "git": '"config"'}
    prefix = "extensions.zotero.translators.better-bibtex."
    shortdoi = "extensions.shortdoi."
    assert (
        addons.effective_value(prefs, defaults, shortdoi + "autoretrieve", None)
        == '"none"'
    )
    assert (
        addons.effective_value(prefs, defaults, shortdoi + "monthly_verify", None)
        == "true"
    )
    assert addons.effective_value(prefs, defaults, prefix + "git", prefix) == '"config"'
    assert (
        addons.effective_value(prefs, defaults, "extensions.zotero.pmcid.auto", None)
        == "unset"
    )


@pytest.mark.parametrize(
    ("installed", "floor", "expected"),
    [
        ("2.2.0", "2.2.0", True),
        ("2.10.0", "2.2.0", True),
        ("1.7.0", "2.2.0", False),
        ("1.7.0-beta", "2.2.0", False),
        ("2.2.0-beta", "2.2.0", True),
        ("2.2", "2.2.0", True),
        ("v2", "2.2.0", None),
        ("", "2.2.0", None),
    ],
)
def test_version_at_least_compares_each_segments_leading_integer(
    installed, floor, expected
):
    assert addons.version_at_least(installed, floor) is expected


def test_bbt_auto_exports_decode_the_json_under_the_branch():
    prefs = {
        "extensions.zotero.translators.better-bibtex.autoExport.abc": (
            '{"type":"library","path":"D:\\\\Zotero\\\\kh-vault\\\\system\\\\'
            'bibliography.json","translatorID":"x"}'
        ),
        "extensions.zotero.translators.better-bibtex.git": "off",
    }
    assert addons.bbt_auto_exports(prefs) == [
        {
            "type": "library",
            "path": "D:\\Zotero\\kh-vault\\system\\bibliography.json",
            "translatorID": "x",
        }
    ]
    with pytest.raises(ValueError, match=re.escape("autoExport.bad")):
        addons.bbt_auto_exports(
            {"extensions.zotero.translators.better-bibtex.autoExport.bad": "{not json"}
        )


def test_xpi_defaults_name_a_corrupt_deflate_stream(tmp_path):
    """Fix round 1, item 3: zlib.error and friends become DefaultsUnreadableError."""
    folder = tmp_path / "extensions"
    folder.mkdir()
    xpi = folder / "deflated@x.xpi"
    body = "".join(f'pref("extensions.d.k{i}", {i});\n' for i in range(200))
    with zipfile.ZipFile(xpi, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("prefs.js", body)
    with zipfile.ZipFile(xpi) as archive:
        info = archive.getinfo("prefs.js")
    data = bytearray(xpi.read_bytes())
    start = info.header_offset + 30 + len(info.filename.encode()) + len(info.extra)
    for offset in range(start + 2, start + 12):
        data[offset] ^= 0xFF
    xpi.write_bytes(bytes(data))
    with pytest.raises(
        addons.DefaultsUnreadableError, match=re.escape("deflated@x.xpi")
    ):
        addons.xpi_defaults(tmp_path, "deflated@x")


@pytest.mark.parametrize(
    "error",
    [RuntimeError("encrypted"), NotImplementedError("method"), EOFError("short")],
)
def test_xpi_defaults_name_any_archive_read_failure(tmp_path, monkeypatch, error):
    _xpi(tmp_path, "odd@x", {"prefs.js": 'pref("extensions.odd.a", true);\n'})

    def refuse(self, name, pwd=None):
        raise error

    monkeypatch.setattr(zipfile.ZipFile, "read", refuse)
    with pytest.raises(addons.DefaultsUnreadableError, match=re.escape("odd@x.xpi")):
        addons.xpi_defaults(tmp_path, "odd@x")


def test_observe_keeps_only_a_string_version(tmp_path):
    """DP48c: a non-string version reads as None."""
    (tmp_path / "extensions.json").write_text(
        json.dumps(
            {
                "addons": [
                    {
                        "id": "a@x",
                        "type": "extension",
                        "location": "app-profile",
                        "version": 2.2,
                        "active": True,
                    }
                ]
            }
        )
    )
    assert addons.observe(tmp_path)["a@x"]["version"] is None
