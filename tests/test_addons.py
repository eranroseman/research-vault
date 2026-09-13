import json

from research_vault import addons


def test_declared_parses_the_packaged_table():
    rows = addons.declared()
    assert rows[0] == addons.Addon(
        "Better BibTeX", "better-bibtex@iris-advies.com", "required", None
    )
    assert any(
        r.addon_id == "zoteroshortdoi@wiernik.org"
        and r.auto_pref == "extensions.shortdoi.autoretrieve"
        for r in rows
    )
    assert {r.need for r in rows} <= {"required", "recommended", "optional"}


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
