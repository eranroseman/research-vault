# Substrate Components, Plan E: The Seeded `.obsidian/`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `.obsidian/` a new vault opens with — a core-heavy `core-plugins.json`, the community plugins the licence permits vendored at their pins, the rest recommended with their `data.json` seeded, the Obsidian plugins that read Zotero, the `app.json` that keeps new notes and links where detection reaches — copied once by scaffold, declared in two tables doctor reads, observed by a new `obsidian` check, and measured on a cold open.

**Architecture:** The seed lives at `research_vault/templates/obsidian/` (outside `templates/vault/`, so doctor's repair never reinstalls a removed plugin) and is copied as one unit into a sibling temporary directory and renamed into place, only with `--with-obsidian`; an existing `.obsidian/` is left alone and named. `scripts/vendor_obsidian_plugin.py` fetches a pinned release's assets byte for byte, records the licence at the pin (bundled dependencies included) in `SOURCE.json`, and demotes a plugin whose licence carries a source obligation to recommended. A packaged declaration, `templates/obsidian-plugins.md`, is embedded in the README and read by doctor's `obsidian` probe, which compares `community-plugins.json`, `core-plugins.json`, each vendored plugin's installed version against its pin, and every declared key in `data.json` and `app.json`.

**Tech Stack:** Python 3.12 in `.venv`; stdlib `urllib`, `json`, `hashlib`, `tempfile`; GitHub's releases API and `obsidianmd/obsidian-releases`' `community-plugins.json` registry for the vendoring script (network, run by hand); Obsidian 1.13.7 with its CLI on the scratch vault for the live legs; PyYAML for the `.base` test.

**Spec:** `docs/superpowers/specs/2026-10-03-substrate-components-design.md` §4 whole, §6.2's mode row (#161), §6.3, §8's Obsidian legs, §11's assembly, `ATTRIBUTION.md`, `pyproject.toml` and `okf-conformance.md` amendments; decision 06–08 and 18. Screen B §9 and screen C §8 carry every setting; designs cluster 5 (c)–(d) and cluster 6 the mechanisms; research Q10–Q12, Q16, Q28. Cites as in Plan A.

**Precondition:** Plans A–D have merged to `main`. §9 binds it: nothing here merges before detection and the capture monitor exist on `main`.

## Global Constraints

Plan A's Global Constraints apply verbatim; branch names are `substrate-e/<task-slug>`. Four more:

- Nothing under `research_vault/templates/` has a path component starting with a dot, and nothing under `research_vault/templates/obsidian/` is a `.md` file (the walker is excluded there only in a vault, never in the package tree). Both are tests in Task 1 and hold for every later task.
- The vendoring script is the only writer of a plugin folder's `main.js`, `manifest.json`, `styles.css`, `LICENSE`, `THIRD-PARTY-NOTICES` and `SOURCE.json`; `data.json` is hand-written and canonical JSON. A plugin's seeded or recommended status is what the script wrote, never a hand edit (decision 06).
- Every JSON file the seed ships is canonical `json.dumps(obj, indent=2, ensure_ascii=False) + "\n"` (`tests/test_config_validity.py::_canonical`), except the vendored release assets, which are byte for byte upstream's.
- A live leg records the Obsidian version, the host locale and the date; a plugin that fails its load check drops to recommended or out, in the same commit as the record.

## Deviations from the spec, settled here

1. **Homepage opens a file, not a workspace layout.** Screen B §9 seeds Homepage with `kind="Workspace"` and a layout shipped in `workspaces.json`. A layout is an Obsidian-version-specific JSON blob that can only be captured from a running app; the seed ships `kind="File"`, `value="index.md"` instead, and the record says so. Core Workspaces stays on.
2. **Auto Note Mover's `newLinkFormat`.** Its screen B row says `app.json newLinkFormat="relative"`; decision 10 and §4.5 say `absolute`. The spec wins; the plugin's rule destinations are off the roster either way.
3. **Tasks is seeded** as the spec says (§4.2), though screen B §9 excluded it on its root-level status report: the report is covered by the register row and the type mapping of §4.6/designs cluster 6(e) (a bare root `.md` is stamped `fleeting`), both in Task 2.
4. **Reference Map, Citation Suite and Better Pandoc Reference List are recommended, not seeded** (copyleft; spec §4.3), and Zotero Deep Linker until the script establishes its licence; their settings are seeded as `data.json`.
5. **Doctor's `obsidian` row and the `advisory` row share one declaration.** An excluded plugin found in `community-plugins.json` is an `advisory` fact (as an active excluded Zotero add-on is), not an `obsidian` failure; `obsidian` is UNMATCHED only for a declared key off its values on an enabled plugin (§6.3).

______________________________________________________________________

### Task 1: Packaging and scaffold — the seed as one unit (§4.6, Q11, Q12)

**Files:**

- Create: `research_vault/templates/obsidian/README-SEED.txt` (a one-line marker so the directory exists before Task 2 fills it; deleted in Task 2)
- Modify: `research_vault/scaffold.py:11-27,48-55,160-205,225-275` (`with_obsidian`, the one-unit copy, the skip line), `research_vault/__main__.py` (`scaffold --with-obsidian`), `research_vault/templates/research-vault/machine.json.example` (`obsidian_config_dir`)
- Test: `tests/test_templates.py:13-50,176-200`, `tests/test_scaffold.py:20-38,95-130,580-600`, `tests/test_verify_cli.py:712-724`

**Interfaces:**

- Produces: `scaffold.scaffold_vault(dest, with_ci=False, with_rw_ci=False, with_obsidian=False) -> list[str]`; with `with_obsidian`, `.obsidian/` is one created path (`".obsidian/"`), copied from `templates/obsidian/` into `dest/.obsidian.research-vault-seed-<pid>` and renamed into place; an existing `.obsidian/` is skipped with the stdout line `skipped .obsidian/: already present — to seed it, close Obsidian, move .obsidian/ aside and run scaffold again`; `scaffold.OBSIDIAN_DIR = ".obsidian"`, `scaffold.OBSIDIAN_TEMPLATE = "obsidian"`; the git cost is one `check-ignore`, one `add`, whatever the plugin count. Doctor's `_tree_probe` calls `scaffold_vault(vault)` with the default, so repair never seeds.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_templates.py`:

```python
def test_package_data_glob_reaches_every_template_file():
    """Designs cluster 6(a): setuptools' build_py uses the standard-library glob,
    which skips dot entries at any depth. The hermetic form of that call must
    equal the rglob file set, and no template path may carry a dot component."""
    import glob

    globbed = {Path(p).relative_to(TEMPLATES).as_posix() for p in glob.glob(str(TEMPLATES / "**" / "*"), recursive=True) if Path(p).is_file()}
    walked = {p.relative_to(TEMPLATES).as_posix() for p in TEMPLATES.rglob("*") if p.is_file()}
    assert globbed == walked
    dotted = [p for p in walked if any(part.startswith(".") for part in p.split("/"))]
    assert dotted == []


def test_no_markdown_under_the_obsidian_seed():
    """verify walks every *.md in a vault; the seed is excluded there (#194) but a
    plugin README in the package would be shipped for nothing."""
    seed = TEMPLATES / "obsidian"
    assert seed.is_dir()
    assert [p for p in seed.rglob("*.md")] == []
```

`EXPECTED_PATHS` (`:13-32`) stays an exact set of the non-seed assets; change `test_all_canonical_template_paths_are_packaged` to compare `actual - {p for p in actual if p.startswith("obsidian/")}` with `EXPECTED_PATHS` and to assert the `obsidian/` subset is non-empty from Task 2 on (for this task, the marker file). The `machine.json.example` pin (`:194-200`) gains `"obsidian_config_dir": ""` (alphabetical, after `mailto`); `tests/test_scaffold.py:112-125`'s byte pin likewise.

Append to `tests/test_scaffold.py`:

```python
def test_scaffold_seeds_obsidian_only_when_asked_and_as_one_unit(tmp_path):
    vault = tmp_path / "vault"
    created = scaffold.scaffold_vault(vault, with_obsidian=True)
    assert ".obsidian/" in created
    assert (vault / ".obsidian").is_dir()
    assert git(vault, "show", "--format=", "--name-only", "HEAD").splitlines() == sorted(TRACKABLE_CREATED + [p for p in git(vault, "ls-files", ".obsidian").splitlines()])
    assert git(vault, "ls-files", ".obsidian/workspace.json") == ""  # ignored by the seeded gitignore
    plain = tmp_path / "plain"
    assert ".obsidian/" not in scaffold.scaffold_vault(plain)
    assert not (plain / ".obsidian").exists()


def test_scaffold_leaves_an_existing_obsidian_alone_and_says_so(tmp_path, capsys):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / ".obsidian").mkdir()
    (vault / ".obsidian" / "app.json").write_text("{}")
    created = scaffold.scaffold_vault(vault, with_obsidian=True)
    assert ".obsidian/" not in created
    assert (vault / ".obsidian" / "app.json").read_text() == "{}"
    assert sorted((vault / ".obsidian").iterdir()) == [vault / ".obsidian" / "app.json"]
    assert "skipped .obsidian/: already present — to seed it, close Obsidian, move .obsidian/ aside and run scaffold again" in capsys.readouterr().out


def test_scaffold_git_cost_does_not_grow_with_the_plugin_count(tmp_path, monkeypatch):
    """Designs cluster 6(c): one candidate, one created path, whatever the seed holds."""
    calls: list[tuple] = []
    real = scaffold._git

    def counting(vault, *args, **kwargs):
        calls.append(args)
        return real(vault, *args, **kwargs)

    monkeypatch.setattr(scaffold, "_git", counting)
    scaffold.scaffold_vault(tmp_path / "small", with_obsidian=True)
    small = len(calls)
    calls.clear()
    seed = tmp_path / "big-seed"
    shutil.copytree(scaffold._seed_root(), seed)
    for i in range(150):
        (seed / "plugins" / f"p{i}").mkdir(parents=True)
        (seed / "plugins" / f"p{i}" / "data.json").write_text("{}\n")
    monkeypatch.setattr(scaffold, "_seed_root", lambda: seed)
    scaffold.scaffold_vault(tmp_path / "big", with_obsidian=True)
    assert len(calls) == small


def test_a_tracked_but_deleted_obsidian_is_a_conflict(tmp_path):
    vault = tmp_path / "vault"
    scaffold.scaffold_vault(vault, with_obsidian=True)
    shutil.rmtree(vault / ".obsidian")
    git(vault, "add", "-A")
    with pytest.raises(ValueError, match="conflict"):
        scaffold.scaffold_vault(vault, with_obsidian=True)


def test_doctor_repair_never_seeds_obsidian(tmp_vault):
    from research_vault import doctor

    probe = doctor._tree_probe(tmp_vault)
    assert probe.result is Result.MATCHED
    assert not (tmp_vault / ".obsidian").exists()
```

(`import shutil` and `from research_vault import Result` at the top of `tests/test_scaffold.py`.) In `tests/test_verify_cli.py:712-724`, add `"--with-obsidian"` to the scaffold invocation and assert `".obsidian/"` is printed.

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_templates.py tests/test_scaffold.py tests/test_verify_cli.py -q -k "glob or obsidian or seed"`
Expected: FAIL — no `with_obsidian`, no `templates/obsidian/`.

- [ ] **Step 3: The marker and `scaffold.py`**

Create `research_vault/templates/obsidian/README-SEED.txt` with one line: `The seeded .obsidian/ (lanes 2-3 spec §4); scaffold copies this directory as .obsidian/ with --with-obsidian.` (Task 2 replaces it with the real seed.)

`research_vault/scaffold.py` — add after `_LOCAL_ONLY_PATHS`:

```python
OBSIDIAN_DIR = ".obsidian"
OBSIDIAN_TEMPLATE = "obsidian"
_OBSIDIAN_UNIT = ".obsidian/"
_SKIPPED_OBSIDIAN = (
    "skipped .obsidian/: already present — to seed it, close Obsidian, move "
    ".obsidian/ aside and run scaffold again"
)


def _seed_root():
    return resources.files("research_vault").joinpath("templates", OBSIDIAN_TEMPLATE)


def _copy_obsidian_seed(vault: Path, created: list[str]) -> None:
    """Copy the seed as one unit (spec §4.6): into a sibling temporary directory,
    then one rename into place, so a concurrently created `.obsidian/` makes the
    rename fail instead of leaving half a seed. An existing folder is left
    alone and named on stdout; setup-vault relays the line."""
    target = vault / OBSIDIAN_DIR
    if target.exists() or target.is_symlink():
        print(_SKIPPED_OBSIDIAN)
        return
    staging = vault / f"{OBSIDIAN_DIR}.research-vault-seed-{os.getpid()}"
    with resources.as_file(_seed_root()) as source:
        shutil.copytree(source, staging)
    try:
        staging.rename(target)
    except OSError:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    created.append(_OBSIDIAN_UNIT)
```

(`import os` at the top.) `scaffold_vault(dest, with_ci=False, with_rw_ci=False, with_obsidian=False)`: after `_render_glossary_if_absent` and before the sentinels, `if with_obsidian: _copy_obsidian_seed(vault, created)`. `_owned_paths(templates, with_ci, with_rw_ci, with_obsidian)` appends `OBSIDIAN_DIR` when asked; `_preflight_conflicts` adds the candidate `OBSIDIAN_DIR` when asked and the folder is absent — `_is_tracked(vault, ".obsidian")` already answers for a directory (`ls-files --error-unmatch` takes a pathspec; `cat-file -e HEAD:.obsidian` sees a tree). `_trackable_paths` passes `.obsidian/` through `check-ignore` as the one candidate; `_commit_created_paths` runs `git add -- .obsidian/` (which skips the ignored `workspace*`) and the pathspec commit names `.obsidian/`. `__main__.cmd_scaffold` and the parser gain `--with-obsidian` (`store_true`). `machine.json.example` gains `"obsidian_config_dir": ""` with the comment-free canonical form (`tests/test_config_validity.py` checks it).

- [ ] **Step 4: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS.

- [ ] **Step 5: Form, commit, branch**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests
git switch -c substrate-e/seed-packaging
git commit -m "feat(scaffold): the .obsidian/ seed at templates/obsidian/, copied as one unit with --with-obsidian; an existing folder is left alone and named (§4.6)" -- research_vault/templates/obsidian/README-SEED.txt research_vault/scaffold.py research_vault/__main__.py research_vault/templates/research-vault/machine.json.example tests/test_templates.py tests/test_scaffold.py tests/test_verify_cli.py
git push -u origin substrate-e/seed-packaging
```

______________________________________________________________________

### Task 2: The seed's own files, the settings, the declaration, #202 and the register rows (§4.1, §4.2, §4.3, §4.5, Q16)

**Files:**

- Create: under `research_vault/templates/obsidian/`: `app.json`, `core-plugins.json`, `community-plugins.json`, `daily-notes.json`, `templates.json`, `zk-prefixer.json`, `webviewer.json`, `plugins/<id>/data.json` for every seeded and recommended plugin that has settings; `research_vault/templates/obsidian-plugins.md` (the declaration); `research_vault/templates/vault/system/templates/weekly.md`, `monthly.md`
- Delete: `research_vault/templates/obsidian/README-SEED.txt`, `research_vault/templates/vault/system/bases/open-questions.base`
- Modify: `research_vault/templates/vault/index.md:17-19` (the query block), `research_vault/stamp.py:126-137` (the root bare-file fallback), `README.md` (embeds the declaration), `docs/agents/okf-conformance.md` (three rows), `research_vault/templates/vault/gitignore` (unchanged: `.obsidian/workspace*` is already there)
- Test: `tests/test_templates.py`, `tests/test_scaffold.py`, `tests/test_stamp.py`, `tests/test_structure.py`, `tests/test_config_validity.py`

**Interfaces:**

- Produces: the seed tree below; `addons`-style loader `research_vault/obsidian_plugins.py` with `Plugin(name, plugin_id, need, pin, licence, workflows)` (`need ∈ {"seeded", "recommended", "excluded"}`), `Setting(plugin, file, key, accepted: tuple[str, ...])` (file is `data.json`, `app.json` or `core-plugins.json`; `key` a dotted JSON path; accepted values are JSON literals or `unset`) and `declared() -> Declaration` (strict, as Plan D's); stamp stamps a bare root `.md` as `fleeting`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_templates.py`:

````python
import json as _json

SEED = TEMPLATES / "obsidian"
CORE_IDS = {
    "file-explorer", "global-search", "switcher", "graph", "backlink", "canvas", "outgoing-link",
    "tag-pane", "properties", "page-preview", "daily-notes", "templates", "note-composer",
    "command-palette", "slash-command", "editor-status", "bookmarks", "markdown-importer",
    "zk-prefixer", "random-note", "outline", "word-count", "slides", "audio-recorder",
    "workspaces", "file-recovery", "publish", "sync", "bases", "footnotes", "webviewer",
}
CORE_OFF = {"properties", "canvas", "sync", "publish", "markdown-importer"}


def test_core_plugins_json_names_every_registered_id_in_object_form():
    """Screen B §7.4: a missing id makes Obsidian rewrite the file on first open."""
    core = _json.loads((SEED / "core-plugins.json").read_text())
    assert set(core) == CORE_IDS
    assert {k for k, v in core.items() if v is False} == CORE_OFF
    assert all(isinstance(v, bool) for v in core.values())


def test_app_json_keeps_new_notes_links_and_attachments_where_detection_reaches():
    app = _json.loads((SEED / "app.json").read_text())
    assert app == {
        "alwaysUpdateLinks": True,
        "attachmentFolderPath": "inbox",
        "newFileFolderPath": "inbox",
        "newFileLocation": "folder",
        "newLinkFormat": "absolute",
        "useMarkdownLinks": True,
    }
    assert "userIgnoreFilters" not in app  # literature/ stays visible (§4.5)


def test_core_settings_files_route_new_notes_off_the_machine_folders():
    assert _json.loads((SEED / "daily-notes.json").read_text()) == {"folder": "daily", "format": "YYYY-MM-DD", "template": "system/templates/daily"}
    assert _json.loads((SEED / "templates.json").read_text()) == {"folder": "system/templates"}
    assert _json.loads((SEED / "zk-prefixer.json").read_text()) == {"folder": "inbox", "format": "YYYYMMDDHHmm", "template": ""}
    assert _json.loads((SEED / "webviewer.json").read_text()) == {"markdownPath": "inbox"}


def test_community_plugins_json_lists_exactly_the_vendored_ids():
    from research_vault import obsidian_plugins

    declaration = obsidian_plugins.declared()
    seeded = sorted(p.plugin_id for p in declaration.plugins if p.need == "seeded")
    assert _json.loads((SEED / "community-plugins.json").read_text()) == seeded
    for plugin in declaration.plugins:
        folder = SEED / "plugins" / plugin.plugin_id
        if plugin.need == "seeded":
            assert (folder / "manifest.json").is_file(), plugin.plugin_id  # Task 3 vendors them
        elif plugin.need == "recommended":
            assert not (folder / "manifest.json").exists(), plugin.plugin_id  # data.json only loads nothing (Q10)
        else:
            assert not folder.exists(), plugin.plugin_id


def test_seeded_settings_satisfy_the_declaration():
    """Designs cluster 5(d): a repo test asserts the seed's own files meet the
    declared keys, so doctor's drift notes on a fresh vault are empty."""
    from research_vault import obsidian_plugins

    declaration = obsidian_plugins.declared()
    for setting in declaration.settings:
        plugin = declaration.by_name[setting.plugin]
        if setting.file == "data.json":
            path = SEED / "plugins" / plugin.plugin_id / "data.json"
        else:
            path = SEED / setting.file
        value = obsidian_plugins.read_key(path, setting.key)
        assert value in setting.accepted, (setting, value)


def test_every_seeded_base_parses_and_reads_no_note_body():
    import yaml

    for base in (TEMPLATES / "vault" / "system" / "bases").glob("*.base"):
        document = yaml.safe_load(base.read_text())
        assert "views" in document, base
        assert "file.content" not in base.read_text(), base  # #202: Bases cannot read bodies
    assert not (TEMPLATES / "vault" / "system" / "bases" / "open-questions.base").exists()


def test_index_uses_a_core_search_block_for_open_questions():
    text = asset("vault/index.md").read_text()
    assert '```query\npath:projects/ "(open-question)"\n```' in text
    assert "open-questions.base" not in text
````

Update `EXPECTED_PATHS`: drop `vault/system/bases/open-questions.base`, add `vault/system/templates/weekly.md`, `vault/system/templates/monthly.md`, `obsidian-plugins.md`; the `index.md` byte pins (`tests/test_templates.py:85-101`, `tests/test_scaffold.py:95-108`) replace the `open-questions.base` paragraph with:

````markdown
Open questions, wherever a claim line carries one:

```query
path:projects/ "(open-question)"
````

````

`tests/test_scaffold.py::EXPECTED_CREATED` drops `system/bases/open-questions.base` and gains the two templates. Append to `tests/test_stamp.py`:

```python
def test_a_bare_root_note_is_stamped_fleeting(tmp_path):
    """Designs cluster 6(e): Tasks' status report and Web viewer's extract land at
    the root with no frontmatter; the type mapping stamps them fleeting."""
    (tmp_path / "Tasks Status Report 2026-10-24.md").write_text("report\n")
    (tmp_path / "typed.md").write_text('---\ntitle: "x"\n---\n')
    stamped, reported = stamp.stamp_types(tmp_path)
    assert stamped == ["Tasks Status Report 2026-10-24.md"]
    assert ("typed.md", "no-type") in reported  # frontmatter without type: still a person's call
````

Append to `tests/test_config_validity.py`'s `JSON_MANIFESTS` the seed's own JSON files and every `plugins/*/data.json` (a glob over `research_vault/templates/obsidian/`, excluding `manifest.json` and `SOURCE.json`, which Task 3 pins separately).

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_templates.py tests/test_scaffold.py tests/test_stamp.py -q -k "core_plugins or app_json or core_settings or community or seeded_settings or base or index or bare_root"`
Expected: FAIL throughout.

- [ ] **Step 3: The seed's own files**

Write these under `research_vault/templates/obsidian/` (canonical JSON, keys sorted):

`core-plugins.json` — every id of `CORE_IDS`, `true` except the five of `CORE_OFF`. `app.json`:

```json
{
  "alwaysUpdateLinks": true,
  "attachmentFolderPath": "inbox",
  "newFileFolderPath": "inbox",
  "newFileLocation": "folder",
  "newLinkFormat": "absolute",
  "useMarkdownLinks": true
}
```

`daily-notes.json` `{"folder": "daily", "format": "YYYY-MM-DD", "template": "system/templates/daily"}`; `templates.json` `{"folder": "system/templates"}`; `zk-prefixer.json` `{"folder": "inbox", "format": "YYYYMMDDHHmm", "template": ""}`; `webviewer.json` `{"markdownPath": "inbox"}` (Save page's destination; Extract selection writes the root and gets the register row). `community-plugins.json`: the sorted ids of the seeded plugins (Step 5's table). Delete `README-SEED.txt`.

`plugins/<id>/data.json` for the seeded plugins with settings:

```text
dataview/data.json                 {"enableDataviewJs": false, "enableInlineDataviewJs": false, "taskCompletionTracking": false}
calendar/data.json                 {"weeklyNoteFolder": "daily/weekly", "weeklyNoteTemplate": "system/templates/weekly"}
periodic-notes/data.json           {"daily": {"enabled": true, "folder": "daily", "format": "", "template": "system/templates/daily"},
                                    "weekly": {"enabled": true, "folder": "daily/weekly", "format": "", "template": "system/templates/weekly"},
                                    "monthly": {"enabled": true, "folder": "daily/monthly", "format": "", "template": "system/templates/monthly"},
                                    "quarterly": {"enabled": false}, "yearly": {"enabled": false}}
homepage/data.json                 {"version": 4, "separateMobile": false,
                                    "homepages": {"Main Homepage": {"kind": "File", "value": "index.md", "openOnStartup": true, "autoCreate": false,
                                                  "commands": [], "openWhenEmpty": false, "alwaysApply": false}}}
obsidian-icon-folder/data.json     {"iconPacksPath": ".obsidian/icons", "iconsInNotesEnabled": false}
obsidian-footnotes/data.json       {"settingsVersion": 2, "lintOnSave": false, "lintOnFootnoteCreation": false, "enableFootnotePrefix": false}
novel-word-count/data.json         {"writeCountsToFile": false}
better-word-count/data.json        {"collectStats": false}
auto-note-mover/data.json          {"use_regex_to_check_for_excluded_folder": true,
                                    "excluded_folder": [{"folder": "^(inbox|literature|fulltext|wiki|log|system|projects|daily)(/|$)"}, {"folder": "^/$"}],
                                    "folder_tag_pattern": []}
obsidian-citation-plugin/data.json {"citationExportPath": "system/bibliography.json", "citationExportFormat": "csl-json",
                                    "markdownCitationTemplate": "[@{{citekey}}]", "literatureNoteFolder": "Reading notes",
                                    "literatureNoteTitleTemplate": "@{{citekey}}", "literatureNoteContentTemplate": "---\ntype: \"reading-note\"\n---\n\n"}
zotero-annotation-to-pandoc/data.json {"source": "betterbibtex", "autoConvert": true}
```

Outliner, Callout Manager, Hider, Tasks and Zotero Cite Links ship no `data.json`. Recommended plugins (folder with `data.json` only):

```text
templater-obsidian/data.json       {"data_version": 2, "templates_folder": "system/templates",
                                    "ignore_folders_on_creation": [{"folder": "literature"}, {"folder": "fulltext"}, {"folder": "wiki"}, {"folder": "log"}, {"folder": "system/propagations"}, {"folder": "inbox/review-queue.md"}],
                                    "startup_templates": []}
quickadd/data.json                 {"choices": [], "disableOnlineFeatures": true, "templateFolderPaths": ["system/templates"], "enableUriCallbacks": false}
obsidian-pandoc/data.json          {"extraArguments": ""}
obsidian-kanban/data.json          {"new-note-folder": "inbox", "link-date-to-daily-note": false}
tasknotes/data.json                {"excludedFolders": "literature,fulltext,wiki,log,system/propagations,log.md,inbox/review-queue.md,system/bibliography.json",
                                    "taskIdentificationMethod": "property", "taskPropertyName": "type", "taskPropertyValue": "task",
                                    "tasksFolder": "TaskNotes/Tasks", "inlineTaskConvertFolder": "", "pomodoroStorageLocation": "plugin",
                                    "enableAPI": false, "enableMCP": false, "webhooks": [],
                                    "icsIntegration": {"enableAutoExport": false, "defaultNoteFolder": "inbox"},
                                    "calendarViewSettings": {"enableTimeblocking": false}, "enableGoogleCalendar": false, "enableMicrosoftCalendar": false,
                                    "starterNoteCreated": true}
omnisearch/data.json               {"httpApiEnabled": false}
editing-toolbar/data.json          {"ai": {"enabled": false, "consentAccepted": false, "onboardingShown": true}}
citation-suite/data.json           {"brackets": true}
reference-map/data.json            {"pullFromZotero": false, "searchCiteKeyPath": "system/bibliography.json", "searchCiteKey": true,
                                    "autoUpdateCitekeyFile": true, "folder": "", "modalCreateTemplate": "---\ntype: reference\n---\n", "zoteroGroups": []}
simple-citations/data.json         {"jsonPaths": "system/bibliography.json", "optionalFields": ["type"], "folderPath": "",
                                    "autoAddCitations": false, "autoSyncCitations": false, "autoUpdateCitations": false}
zotero-lib-view/data.json          {"exportPath": "zotero-lib-view", "exportTitle": "{{citeKey}}", "imagesCopy": false, "autoImportOnBibChange": false,
                                    "templateType": "Custom", "templateContent": "---\ntype: zotero-lib-view\n---\n", "highlightCitationsFormat": "Pandoc"}
```

Advanced Tables, Focus Mode, Typewriter Scroll, Better Pandoc Reference List and Zotero Deep Linker need no settings and get no folder. `research_vault/templates/vault/system/templates/weekly.md` and `monthly.md` are `---\ntype: "daily"\n---\n`.

- [ ] **Step 4: #202 and the type mapping**

Delete `research_vault/templates/vault/system/bases/open-questions.base`. `research_vault/templates/vault/index.md:17-19` becomes the query block of Step 1. `research_vault/stamp.py:131-133`:

```python
            derived = structure.expected_type(relative)
            if derived is None and (structure.is_fleeting(relative) or "/" not in relative):
                # Designs cluster 6(e): a bare file at the vault root (Tasks'
                # status report, Web viewer's extract) is stamped fleeting; a
                # root file carrying frontmatter without a type stays reported.
                derived = "fleeting"
```

- [ ] **Step 5: The declaration and its loader**

Create `research_vault/templates/obsidian-plugins.md`:

```markdown
### Plugins

| Plugin                       | Id                              | Need        | Pin    | Licence   | Workflows                                          |
| ---------------------------- | ------------------------------- | ----------- | ------ | --------- | -------------------------------------------------- |
| Dataview                     | `dataview`                      | seeded      | 0.5.68 | MIT       | personal knowledge management, analysis and reports |
| Calendar                     | `calendar`                      | seeded      | 1.5.10 | MIT       | daily logs                                         |
| Periodic Notes               | `periodic-notes`                | seeded      | 0.0.17 | MIT       | daily logs                                         |
| Homepage                     | `homepage`                      | seeded      | 4.5.0  | MIT       | personal knowledge management                      |
| Outliner                     | `obsidian-outliner`             | seeded      | 4.10.2 | MIT       | long-form writing                                  |
| Callout Manager              | `callout-manager`               | seeded      | 1.1.2  | MIT       | long-form writing                                  |
| Iconize                      | `obsidian-icon-folder`          | seeded      | 2.14.7 | MIT       | personal knowledge management                      |
| Footnote Shortcut            | `obsidian-footnotes`            | seeded      | 0.2.0  | MIT       | long-form writing                                  |
| Better Word Count            | `better-word-count`             | seeded      | 0.10.1 | MIT       | long-form writing                                  |
| Novel word count             | `novel-word-count`              | seeded      | 5.0.0  | MIT       | long-form writing                                  |
| Hider                        | `obsidian-hider`                | seeded      | 1.7.1  | MIT       | personal knowledge management                      |
| Auto Note Mover              | `auto-note-mover`               | seeded      | 1.2.0  | MIT       | personal knowledge management                      |
| Tasks                        | `obsidian-tasks-plugin`         | seeded      | 8.4.0  | MIT       | personal knowledge management, daily logs          |
| Citations                    | `obsidian-citation-plugin`      | seeded      | 0.4.5  | MIT       | long-form writing, research                        |
| Zotero Cite Links            | `zotero-cite-links`             | seeded      | 0.2.0  | MIT       | research, long-form writing                        |
| Zotero Annotation Citations  | `zotero-annotation-to-pandoc`   | seeded      | 1.0.3  | MIT       | research, long-form writing                        |
| Omnisearch                   | `omnisearch`                    | recommended | 1.31.0 | GPL-3.0   | personal knowledge management                      |
| Advanced Tables              | `table-editor-obsidian`         | recommended | 0.23.2 | GPL-3.0   | long-form writing                                  |
| Editing Toolbar              | `editing-toolbar`               | recommended | 4.1.5  | MPL-2.0   | long-form writing                                  |
| Focus Mode                   | `obsidian-focus-mode`           | recommended | 1.12.0 | MPL-2.0   | long-form writing                                  |
| Kanban                       | `obsidian-kanban`               | recommended | 2.0.51 | GPL-3.0   | personal knowledge management                      |
| TaskNotes                    | `tasknotes`                     | recommended | 4.13.8 | MIT (bundles MPL-2.0 ical.js) | personal knowledge management, daily logs |
| Templater                    | `templater-obsidian`            | recommended | 2.25.1 | AGPL-3.0  | long-form writing                                  |
| QuickAdd                     | `quickadd`                      | recommended | 2.30.0 | MIT       | personal knowledge management                      |
| Pandoc Plugin                | `obsidian-pandoc`               | recommended | 0.4.1  | MIT (embeds Obsidian CSS) | analysis and reports, long-form writing |
| Typewriter Scroll            | `cm-typewriter-scroll-obsidian` | recommended | 0.2.2  | none at the pin | long-form writing                            |
| Citation Suite               | `citation-suite`                | recommended | 2.2.0  | AGPL-3.0  | long-form writing, research                        |
| Better Pandoc Reference List | `better-pandoc-reference-list`  | recommended | 3.1.0  | GPL-3.0   | long-form writing, research                        |
| Reference Map                | `reference-map`                 | recommended | 1.8.1  | GPL-3.0   | research, personal knowledge management            |
| Simple Citations             | `simple-citations`              | recommended | 1.10.0 | MIT       | long-form writing, analysis and reports, research  |
| Zotero Lib View              | `zotero-lib-view`               | recommended | 1.2.14 | MIT (grant in package.json only) | research, personal knowledge management |
| Zotero Deep Linker           | `zotero-deep-linker`            | recommended | 0.2.0  | MIT (placeholder holder) | research, personal knowledge management |
| Git                          | `obsidian-git`                  | excluded    | —      | —         | —                                                  |
| Longform                     | `longform`                      | excluded    | —      | —         | —                                                  |
| Advanced URI                 | `obsidian-advanced-uri`         | excluded    | —      | —         | —                                                  |
| Tag Wrangler                 | `tag-wrangler`                  | excluded    | —      | —         | —                                                  |
| Note Refactor                | `note-refactor-obsidian`        | excluded    | —      | —         | —                                                  |
| Excalidraw                   | `obsidian-excalidraw-plugin`    | excluded    | —      | —         | —                                                  |
| Quadro                       | `quadro`                        | excluded    | —      | —         | —                                                  |
| Local REST API               | `obsidian-local-rest-api`       | excluded    | —      | —         | —                                                  |
| Claudian                     | `realclaudian`                  | excluded    | —      | —         | —                                                  |
| Copilot                      | `copilot`                       | excluded    | —      | —         | —                                                  |
| Agent Client                 | `agent-client`                  | excluded    | —      | —         | —                                                  |
| Remotely Save                | `remotely-save`                 | excluded    | —      | —         | —                                                  |
| Importer                     | `obsidian-importer`             | excluded    | —      | —         | —                                                  |
| Enhancing Export             | `obsidian-enhancing-export`     | excluded    | —      | —         | —                                                  |
| ZotLit                       | `zotlit`                        | excluded    | —      | —         | —                                                  |
| Zotero Integration           | `obsidian-zotero-desktop-connector` | excluded | —      | —         | —                                                  |
| Citation Extended            | `citation-extended`             | excluded    | —      | —         | —                                                  |
| Citation Links               | `citation-links`                | excluded    | —      | —         | —                                                  |
| Deep Sit                     | `deep-sit`                      | excluded    | —      | —         | —                                                  |

### Declared plugin settings

| Plugin                      | File                | Key                                       | Accepted          |
| --------------------------- | ------------------- | ----------------------------------------- | ----------------- |
| Core                        | `core-plugins.json` | `sync`                                    | `false`           |
| Core                        | `core-plugins.json` | `publish`                                 | `false`           |
| Core                        | `core-plugins.json` | `canvas`                                  | `false`           |
| Core                        | `core-plugins.json` | `properties`                              | `false`           |
| Core                        | `core-plugins.json` | `markdown-importer`                       | `false`           |
| Core                        | `app.json`          | `useMarkdownLinks`                        | `true`            |
| Core                        | `app.json`          | `newLinkFormat`                           | `"absolute"`      |
| Core                        | `app.json`          | `newFileLocation`                         | `"folder"`        |
| Core                        | `app.json`          | `newFileFolderPath`                       | `"inbox"`         |
| Core                        | `app.json`          | `attachmentFolderPath`                    | `"inbox"`         |
| Core                        | `daily-notes.json`  | `folder`                                  | `"daily"`         |
| Core                        | `zk-prefixer.json`  | `folder`                                  | `"inbox"`         |
| Dataview                    | `data.json`         | `enableDataviewJs`                        | `false`, `unset`  |
| Dataview                    | `data.json`         | `enableInlineDataviewJs`                  | `false`, `unset`  |
| Iconize                     | `data.json`         | `iconPacksPath`                           | `".obsidian/icons"` |
| Footnote Shortcut           | `data.json`         | `lintOnSave`                              | `false`           |
| Novel word count            | `data.json`         | `writeCountsToFile`                       | `false`, `unset`  |
| Better Word Count           | `data.json`         | `collectStats`                            | `false`, `unset`  |
| Auto Note Mover             | `data.json`         | `use_regex_to_check_for_excluded_folder`  | `true`            |
| Homepage                    | `data.json`         | `homepages.Main Homepage.autoCreate`      | `false`           |
| Citations                   | `data.json`         | `citationExportPath`                      | `"system/bibliography.json"` |
| Citations                   | `data.json`         | `literatureNoteFolder`                    | `"Reading notes"` |
| Zotero Annotation Citations | `data.json`         | `source`                                  | `"betterbibtex"`, `unset` |
| Omnisearch                  | `data.json`         | `httpApiEnabled`                          | `false`, `unset`  |
| Editing Toolbar             | `data.json`         | `ai.enabled`                              | `false`           |
| Kanban                      | `data.json`         | `new-note-folder`                         | `"inbox"`         |
| TaskNotes                   | `data.json`         | `enableAPI`                               | `false`           |
| TaskNotes                   | `data.json`         | `enableMCP`                               | `false`           |
| TaskNotes                   | `data.json`         | `tasksFolder`                             | `"TaskNotes/Tasks"` |
| Templater                   | `data.json`         | `templates_folder`                        | `"system/templates"` |
| Templater                   | `data.json`         | `startup_templates`                       | `[]`              |
| QuickAdd                    | `data.json`         | `disableOnlineFeatures`                   | `true`            |
| QuickAdd                    | `data.json`         | `enableUriCallbacks`                      | `false`           |
| Reference Map               | `data.json`         | `pullFromZotero`                          | `false`           |
| Reference Map               | `data.json`         | `searchCiteKeyPath`                       | `"system/bibliography.json"` |
| Simple Citations            | `data.json`         | `autoAddCitations`                        | `false`, `unset`  |
| Simple Citations            | `data.json`         | `autoSyncCitations`                       | `false`, `unset`  |
| Zotero Lib View             | `data.json`         | `autoImportOnBibChange`                   | `false`, `unset`  |
| Zotero Lib View             | `data.json`         | `exportPath`                              | `"zotero-lib-view"` |
```

Create `research_vault/obsidian_plugins.py` on the shape of Plan D's `addons.py`: `Plugin`, `Setting`, `Declaration` (`by_id`, `by_name`, `settings_for(plugin_id)`), `declared()` (strict: the tables are `### Plugins` and `### Declared plugin settings` — the second heading differs from the Zotero table's so the README carries no duplicate heading; `need ∈ {"seeded", "recommended", "excluded"}`, every settings row names a plugin or `Core`, every accepted literal is JSON or `unset`), and:

```python
def read_key(path: Path, dotted: str) -> str:
    """The JSON literal at a dotted key in a JSON file, or `unset`; an unparseable
    file raises `ConfigUnreadable` (doctor reports UNREACHABLE: Obsidian rewrites
    these files non-atomically, screen B §7.37)."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return "unset"
    except (OSError, UnicodeError, ValueError) as error:
        raise ConfigUnreadable(f"{path.name}: {error}") from error
    node = document
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return "unset"
        node = node[part]
    return json.dumps(node, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
```

(A dotted key with a space, `homepages.Main Homepage.autoCreate`, splits on `.` only.) `README.md` gains, after the Zotero add-ons section, a `## Obsidian plugins` section embedding `obsidian-plugins.md` whole with two sentences: “A new vault's `.obsidian/` is seeded by `scaffold --with-obsidian` from this declaration: seeded plugins are vendored at their pin (their licence permits redistribution with no source obligation), recommended ones ship only their settings and are installed by the person from Obsidian's community list, excluded ones are not declared further. Doctor's `obsidian` row compares the configured folder with it.” A `tests/test_templates.py` test asserts the embed as the Zotero one does.

- [ ] **Step 6: The register rows**

`docs/agents/okf-conformance.md`'s register gains three rows:

```markdown
| Tasks' status-review report: a timestamped `.md` at the vault root with no frontmatter | OKF §11 rule 1 | 1 — written by a seeded plugin's button at a hard-coded root path (`StatusRegistryReport.ts:21` @ Tasks `9173205`); the type mapping stamps a bare root file `fleeting` at the next commit (`research_vault/stamp.py`), so the file conforms once staged (spec ruling 7) |
| Web viewer's Extract selection: a root `.md` with no frontmatter | OKF §11 rule 1 | 1 — a core plugin with no folder setting for the extract (screen B §7, item 734); the same root type mapping converges it; Save page writes `inbox/`, which row 2 covers |
| Unique note creator's inserted link names a note that does not yet exist | OKF §6.1 (a link resolves) | 1 — the created note lands in `inbox/` (`zk-prefixer.json` `folder`), typed fleeting by the mapping; the dangling link lasts until the person writes the note, and `dead-link` reports it only under `wiki/` |
```

- [ ] **Step 7: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: `test_community_plugins_json_lists_exactly_the_vendored_ids` fails on the missing `manifest.json` files until Task 3 vendors them; mark it `xfail(strict=True, reason="Task 3 vendors the assets")` in this commit and remove the mark in Task 3. Everything else PASS.

- [ ] **Step 8: Form, commit, branch, close #202**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat README.md research_vault/templates/obsidian-plugins.md docs/agents/okf-conformance.md
git switch -c substrate-e/seed-files
git commit -m "feat(seed): the .obsidian/ settings, the plugin declaration, open-questions as a core Search block, bare root notes stamped fleeting (§4.1, §4.2, §4.5, #202)" -- research_vault/templates/obsidian research_vault/templates/obsidian-plugins.md research_vault/obsidian_plugins.py research_vault/templates/vault/index.md research_vault/templates/vault/system/templates/weekly.md research_vault/templates/vault/system/templates/monthly.md research_vault/stamp.py README.md docs/agents/okf-conformance.md tests/test_templates.py tests/test_scaffold.py tests/test_stamp.py tests/test_config_validity.py
git rm -q research_vault/templates/vault/system/bases/open-questions.base && git commit -m "chore(seed): open-questions.base goes — Bases cannot read a note body (#202)" -- research_vault/templates/vault/system/bases/open-questions.base
git push -u origin substrate-e/seed-files
```

After the merge: `gh issue close 202 --comment "Closed by Plan E Task 2: open-questions.base is deleted (Bases 1.13.7 exposes no file.content); index.md carries a core Search block, path:projects/ \"(open-question)\", which Plan E's cold-open leg confirms matches a claim line."`

______________________________________________________________________

### Task 3: The vendoring script, `SOURCE.json`, licences, ATTRIBUTION (§4.2, §4.6, decision 06)

**Files:**

- Create: `scripts/vendor_obsidian_plugin.py`; under `research_vault/templates/obsidian/plugins/<id>/` for every seeded plugin: `main.js`, `manifest.json`, `styles.css` (when the release ships one), `LICENSE`, `THIRD-PARTY-NOTICES`, `SOURCE.json`
- Modify: `pyproject.toml:11` (`license`, `license-files`), `ATTRIBUTION.md:7-8,36-60` (vendored plugins; `SOURCE.json` as the record)
- Test: `tests/test_vendor_obsidian_plugin.py` (new), `tests/test_templates.py` (the `xfail` of Task 2 removed), `tests/test_config_validity.py` (licence expression; `SOURCE.json` canonical)

**Interfaces:**

- Produces: `python scripts/vendor_obsidian_plugin.py <plugin id> <tag> [--registry URL]` — resolves `repo` from `obsidianmd/obsidian-releases`' `community-plugins.json`, downloads the release's `main.js`, `manifest.json` and `styles.css` at `<tag>`, the repository's `LICENSE*` and `package.json` at the tag's commit, reads every runtime dependency's licence from the npm registry at its resolved version, writes the asset bytes unchanged, `LICENSE` (the repository's), `THIRD-PARTY-NOTICES` (one block per bundled dependency: name, version, licence, URL) and `SOURCE.json`:

  ```json
  {"repo": "blacksmithgu/obsidian-dataview", "tag": "0.5.68", "commit": "29b1ad8…", "assets": {"main.js": "<sha256>", "manifest.json": "<sha256>", "styles.css": "<sha256>"},
   "licence": "MIT", "bundled": [{"name": "…", "version": "…", "licence": "MIT"}], "source": null, "redistributable": true,
   "measured": "2026-10-24", "method": "LICENSE at the tag's commit; package.json dependencies resolved against registry.npmjs.org; the asset is the release artifact, built from the tag per the release notes"}
  ```

  A plugin whose own licence or any bundled licence carries a source obligation (GPL, LGPL, AGPL, MPL, EUPL, CPAL), or whose licence cannot be established (no `LICENSE*` file, a placeholder holder, a licence named only in `package.json`), is written as recommended: `data.json` is kept, no asset is written, and `SOURCE.json` records `"redistributable": false` with the reason; the script prints which. The script never edits `obsidian-plugins.md`; a mismatch between its verdict and the table's `Need` is a test failure the executor resolves by changing the table.

- Consumes: Task 2's declaration.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_vendor_obsidian_plugin.py`:

```python
import hashlib
import json
from pathlib import Path

import pytest

from research_vault import obsidian_plugins
from scripts import vendor_obsidian_plugin as vendor

SEED = Path(__file__).resolve().parents[1] / "research_vault" / "templates" / "obsidian" / "plugins"


def _seeded():
    return [p for p in obsidian_plugins.declared().plugins if p.need == "seeded"]


@pytest.mark.parametrize("plugin", _seeded(), ids=lambda p: p.plugin_id)
def test_each_seeded_plugin_carries_its_assets_record_and_licence(plugin):
    folder = SEED / plugin.plugin_id
    source = json.loads((folder / "SOURCE.json").read_text())
    assert set(source) == {"repo", "tag", "commit", "assets", "licence", "bundled", "source", "redistributable", "measured", "method"}
    assert source["tag"] == plugin.pin
    assert source["redistributable"] is True
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["id"] == plugin.plugin_id
    assert manifest["version"] == plugin.pin  # the tag is the version; SOURCE.json has no version field
    for name, digest in source["assets"].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest, name
    assert (folder / "LICENSE").is_file()
    assert (folder / "THIRD-PARTY-NOTICES").is_file()
    assert vendor.has_source_obligation(source["licence"]) is False
    assert all(vendor.has_source_obligation(dep["licence"]) is False for dep in source["bundled"])


@pytest.mark.parametrize("plugin", [p for p in obsidian_plugins.declared().plugins if p.need == "recommended"], ids=lambda p: p.plugin_id)
def test_a_recommended_plugin_ships_no_asset(plugin):
    folder = SEED / plugin.plugin_id
    if folder.exists():
        assert sorted(p.name for p in folder.iterdir()) == ["data.json"]


@pytest.mark.parametrize(
    ("licence", "obligation"),
    [("MIT", False), ("Apache-2.0", False), ("BSD-3-Clause", False), ("ISC", False), ("0BSD", False),
     ("GPL-3.0", True), ("GPL-3.0-only", True), ("AGPL-3.0-or-later", True), ("LGPL-2.1", True), ("MPL-2.0", True), ("CPAL-1.0", True), ("EUPL-1.2", True),
     ("UNLICENSED", None), ("", None), (None, None), ("SEE LICENSE IN x", None)],
)
def test_has_source_obligation_reads_spdx_and_refuses_the_unknown(licence, obligation):
    assert vendor.has_source_obligation(licence) is obligation


def test_verdict_demotes_copyleft_placeholder_and_unestablished(tmp_path):
    assert vendor.verdict("MIT", [{"name": "a", "licence": "MIT"}], holder="Jane Doe") == "seeded"
    assert vendor.verdict("MIT", [{"name": "ical.js", "licence": "MPL-2.0"}], holder="X") == "recommended"
    assert vendor.verdict("GPL-3.0", [], holder="X") == "recommended"
    assert vendor.verdict("MIT", [], holder="Local") == "recommended"  # a placeholder holder does not establish the grant
    assert vendor.verdict(None, [], holder="X") == "recommended"


def test_attribution_names_every_seeded_plugin_id():
    text = (Path(__file__).resolve().parents[1] / "ATTRIBUTION.md").read_text()
    for plugin in _seeded():
        assert f"`{plugin.plugin_id}`" in text, plugin.plugin_id
    assert "SOURCE.json" in text
    assert "provenance header at the top of the file" not in text


def test_pyproject_license_expression_names_every_vendored_licence():
    import tomllib

    pyproject = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text())
    expression = pyproject["project"]["license"]
    licences = {json.loads((SEED / p.plugin_id / "SOURCE.json").read_text())["licence"] for p in _seeded()}
    for licence in licences | {"MIT"}:
        assert licence in expression, licence
    files = pyproject["project"]["license-files"]
    assert "research_vault/templates/obsidian/plugins/*/LICENSE" in files
    assert "research_vault/templates/obsidian/plugins/*/THIRD-PARTY-NOTICES" in files
```

In `tests/test_config_validity.py`, add every `plugins/*/SOURCE.json` and `plugins/*/data.json` to the canonical-JSON check (`manifest.json`, `main.js`, `styles.css` are upstream bytes and stay out). Remove Task 2's `xfail`.

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_vendor_obsidian_plugin.py tests/test_templates.py -q -k "vendor or seeded_plugin or recommended_plugin or attribution or license or community"`
Expected: FAIL — no script, no assets.

- [ ] **Step 3: `scripts/vendor_obsidian_plugin.py`**

```python
"""Vendor one Obsidian community plugin at a pinned release (lanes 2-3 spec §4.2, §4.6).

Run by hand, with network: it resolves the plugin's repository from the
community registry, fetches the release assets at the tag byte for byte, reads
the licence at the tag's commit and every runtime dependency's licence from the
npm registry, and writes the plugin folder under
research_vault/templates/obsidian/plugins/<id>/ with LICENSE,
THIRD-PARTY-NOTICES and SOURCE.json. A licence with a source obligation, or one
that cannot be established, makes the plugin recommended: data.json stays, no
asset is written, SOURCE.json says why. The script never edits the declaration
table; a test compares the two.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "research_vault" / "templates" / "obsidian" / "plugins"
REGISTRY = "https://raw.githubusercontent.com/obsidianmd/obsidian-releases/HEAD/community-plugins.json"
ASSETS = ("main.js", "manifest.json", "styles.css")
# SPDX families that carry a source obligation on redistribution. Anything not
# matched here and not in PERMISSIVE is "not established" and demotes too.
COPYLEFT = re.compile(r"^(GPL|LGPL|AGPL|MPL|EUPL|CPAL|CDDL|OSL|EPL|CECILL|SSPL)\b", re.IGNORECASE)
PERMISSIVE = re.compile(r"^(MIT|ISC|0BSD|BSD-[123]-Clause|Apache-2\.0|Unlicense|Zlib|CC0-1\.0|BlueOak-1\.0\.0|WTFPL|PSF-2\.0|Python-2\.0)$", re.IGNORECASE)
PLACEHOLDER_HOLDERS = {"", "local", "your name", "author", "[fullname]", "<copyright holders>"}


def has_source_obligation(licence) -> bool | None:
    """True for a copyleft family, False for a permissive licence, None when the
    licence is not established (unknown expression, empty, UNLICENSED)."""
    if not isinstance(licence, str) or not licence.strip():
        return None
    text = licence.strip()
    if " OR " in text or " AND " in text or "(" in text:
        parts = re.split(r"\s+(?:OR|AND)\s+", text.strip("()"))
        verdicts = [has_source_obligation(part) for part in parts]
        if " OR " in text and False in verdicts:
            return False
        return None if None in verdicts else any(verdicts)
    if COPYLEFT.match(text):
        return True
    if PERMISSIVE.match(text):
        return False
    return None


def verdict(licence, bundled: list[dict], *, holder: str) -> str:
    own = has_source_obligation(licence)
    if own is not False:
        return "recommended"
    if holder.strip().lower() in PLACEHOLDER_HOLDERS:
        return "recommended"
    for dependency in bundled:
        if has_source_obligation(dependency.get("licence")) is not False:
            return "recommended"
    return "seeded"


def _get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310 — https only, run by hand
        return response.read()


def _json(url: str):
    return json.loads(_get(url).decode("utf-8"))


def resolve_repo(plugin_id: str, registry: str) -> str:
    for entry in _json(registry):
        if entry.get("id") == plugin_id:
            return entry["repo"]
    raise SystemExit(f"{plugin_id}: not in the community registry")


def release(repo: str, tag: str) -> dict:
    return _json(f"https://api.github.com/repos/{repo}/releases/tags/{tag}")


def commit_for(repo: str, tag: str) -> str:
    ref = _json(f"https://api.github.com/repos/{repo}/git/ref/tags/{tag}")["object"]
    if ref["type"] == "tag":  # an annotated tag points at a tag object first
        ref = _json(ref["url"])["object"]
    return ref["sha"]


def licence_at(repo: str, commit: str) -> tuple[str | None, str, str]:
    """(SPDX id or None, LICENSE text, copyright holder) from the LICENSE* file at the commit."""
    tree = _json(f"https://api.github.com/repos/{repo}/git/trees/{commit}")["tree"]
    names = [e["path"] for e in tree if e["type"] == "blob" and e["path"].upper().startswith(("LICENSE", "LICENCE", "COPYING"))]
    if not names:
        return None, "", ""
    text = _get(f"https://raw.githubusercontent.com/{repo}/{commit}/{names[0]}").decode("utf-8", errors="replace")
    holder_match = re.search(r"Copyright\s+(?:\(c\)\s*)?(?:\d{4}[-–,\s\d]*)?\s*(.+)", text)
    holder = holder_match.group(1).strip() if holder_match else ""
    spdx = _spdx_from_text(text)
    return spdx, text, holder


def _spdx_from_text(text: str) -> str | None:
    head = text[:600]
    if "MIT License" in head or "Permission is hereby granted, free of charge" in text:
        return "MIT"
    if "Apache License" in head and "2.0" in head:
        return "Apache-2.0"
    if "GNU AFFERO GENERAL PUBLIC LICENSE" in head:
        return "AGPL-3.0"
    if "GNU GENERAL PUBLIC LICENSE" in head:
        return "GPL-3.0" if "Version 3" in head else "GPL-2.0"
    if "GNU LESSER GENERAL PUBLIC LICENSE" in head:
        return "LGPL-3.0" if "Version 3" in head else "LGPL-2.1"
    if "Mozilla Public License" in head:
        return "MPL-2.0"
    if "ISC License" in head:
        return "ISC"
    if "BSD" in head and "Redistribution and use in source and binary forms" in text:
        return "BSD-3-Clause" if "Neither the name" in text else "BSD-2-Clause"
    return None


def bundled_dependencies(repo: str, commit: str) -> list[dict]:
    """Every runtime dependency of package.json at the commit, with the licence
    the npm registry records for the version the lockfile resolves (or the range's
    highest match when there is no lockfile)."""
    try:
        package = _json(f"https://raw.githubusercontent.com/{repo}/{commit}/package.json")
    except Exception:  # noqa: BLE001 — a missing package.json means no declared dependencies
        return []
    out = []
    for name, spec in sorted((package.get("dependencies") or {}).items()):
        version = re.sub(r"^[\^~>=<\s]+", "", str(spec)).split(" ")[0] or "latest"
        try:
            metadata = _json(f"https://registry.npmjs.org/{name}/{version}")
            licence = metadata.get("license")
            if isinstance(licence, dict):
                licence = licence.get("type")
            version = metadata.get("version", version)
        except Exception:  # noqa: BLE001 — recorded as not established, which demotes
            licence = None
        out.append({"name": name, "version": version, "licence": licence, "url": f"https://www.npmjs.com/package/{name}"})
    return out


def write_plugin(plugin_id: str, tag: str, *, registry: str = REGISTRY, today: str | None = None) -> str:
    repo = resolve_repo(plugin_id, registry)
    commit = commit_for(repo, tag)
    spdx, licence_text, holder = licence_at(repo, commit)
    bundled = bundled_dependencies(repo, commit)
    decision = verdict(spdx, bundled, holder=holder)
    folder = PLUGINS / plugin_id
    folder.mkdir(parents=True, exist_ok=True)
    source = {
        "repo": repo,
        "tag": tag,
        "commit": commit,
        "assets": {},
        "licence": spdx,
        "bundled": bundled,
        "source": None if decision == "seeded" else f"https://github.com/{repo}/tree/{tag}",
        "redistributable": decision == "seeded",
        "measured": today or datetime.date.today().isoformat(),
        "method": (
            "LICENSE at the tag's commit (SPDX read from its text); package.json dependencies at the "
            "commit resolved against registry.npmjs.org; the assets are the GitHub release artifacts at the tag"
            if decision == "seeded"
            else f"demoted to recommended: licence {spdx!r}, holder {holder!r}, bundled {[d['licence'] for d in bundled]}"
        ),
    }
    if decision == "seeded":
        assets = {a["name"]: a["browser_download_url"] for a in release(repo, tag)["assets"]}
        for name in ASSETS:
            if name not in assets:
                if name == "styles.css":
                    continue
                raise SystemExit(f"{plugin_id} {tag}: release ships no {name}")
            data = _get(assets[name])
            (folder / name).write_bytes(data)
            source["assets"][name] = hashlib.sha256(data).hexdigest()
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("version") != tag:
            raise SystemExit(f"{plugin_id}: manifest version {manifest.get('version')!r} is not the tag {tag!r}")
        (folder / "LICENSE").write_text(licence_text, encoding="utf-8")
        notices = "\n\n".join(
            f"{d['name']} {d['version']}\nLicence: {d['licence']}\n{d['url']}" for d in bundled
        ) or "No bundled third-party dependencies declared at the pin.\n"
        (folder / "THIRD-PARTY-NOTICES").write_text(notices, encoding="utf-8")
    else:
        for name in (*ASSETS, "LICENSE", "THIRD-PARTY-NOTICES"):
            (folder / name).unlink(missing_ok=True)
    (folder / "SOURCE.json").write_text(json.dumps(source, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return decision


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("plugin_id")
    parser.add_argument("tag")
    parser.add_argument("--registry", default=REGISTRY)
    args = parser.parse_args(argv)
    decision = write_plugin(args.plugin_id, args.tag, registry=args.registry)
    print(f"{args.plugin_id} {args.tag}: {decision}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Run `mypy scripts/vendor_obsidian_plugin.py` (`scripts` is in `[tool.mypy] files`).

- [ ] **Step 4: Vendor the sixteen, then reconcile the table**

```bash
for spec in dataview:0.5.68 calendar:1.5.10 periodic-notes:0.0.17 homepage:4.5.0 obsidian-outliner:4.10.2 callout-manager:1.1.2 obsidian-icon-folder:2.14.7 obsidian-footnotes:0.2.0 better-word-count:0.10.1 novel-word-count:5.0.0 obsidian-hider:1.7.1 auto-note-mover:1.2.0 obsidian-tasks-plugin:8.4.0 obsidian-citation-plugin:0.4.5 zotero-cite-links:0.2.0 zotero-annotation-to-pandoc:1.0.3; do python scripts/vendor_obsidian_plugin.py "${spec%%:*}" "${spec##*:}"; done
```

A plugin the script demotes stays in the table as `recommended` and its `community-plugins.json` entry goes; record the reason from its `SOURCE.json` in the task report. If a release at the pinned tag ships no `main.js` (Zotero Cite Links and Zotero Annotation Citations were pinned at commits "after" a release in screen C), vendor the nearest release tag at or above the pinned commit and change the table's `Pin`. For `SOURCE.json` of a recommended plugin, the folder keeps `data.json` beside it only if Task 2 wrote one; otherwise `SOURCE.json` is the only file, which loads nothing in Obsidian.

- [ ] **Step 5: `pyproject.toml` and ATTRIBUTION**

`pyproject.toml:11`: `license = "MIT AND <every distinct SPDX id in the seeded SOURCE.json files, joined with AND>"` and, below it:

```toml
license-files = [
  "LICENSE",
  "research_vault/templates/obsidian/plugins/*/LICENSE",
  "research_vault/templates/obsidian/plugins/*/THIRD-PARTY-NOTICES",
]
```

`ATTRIBUTION.md:7-8`: replace “Vendored files each carry their own provenance header at the top of the file, or directly after the YAML frontmatter when the file must open with one (a skill or agent file); this document is the index, not the record.” with “A vendored text file carries its provenance header at the top, or directly after the YAML frontmatter when the file must open with one (a skill or agent file). A vendored Obsidian plugin is byte for byte its upstream release and cannot carry a header: its record is `SOURCE.json` beside it (repository, tag, commit, asset hashes, licence, bundled dependencies, method, date), written only by `scripts/vendor_obsidian_plugin.py`. This document is the index, not the record.” Under `## Vendored source`, add a table **Obsidian plugins, seeded** with one row per seeded plugin: name, `id`, author, licence, pin — and the exit line: “Stop seeding them and a vault keeps ordinary Obsidian plugin folders the person can update or remove from Settings; nothing in the vault's content depends on them.”

- [ ] **Step 6: Run the suite, commit, branch**

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy && pyproject-fmt pyproject.toml
ruff check --fix scripts tests && ruff format scripts tests && mdformat ATTRIBUTION.md research_vault/templates/obsidian-plugins.md README.md
git switch -c substrate-e/vendored-plugins
git add research_vault/templates/obsidian/plugins
git commit -m "feat(seed): vendor the seeded plugins at their pins with LICENSE, THIRD-PARTY-NOTICES and SOURCE.json; the vendoring script decides seeded or recommended (§4.2, §4.6)" -- scripts/vendor_obsidian_plugin.py research_vault/templates/obsidian pyproject.toml ATTRIBUTION.md README.md research_vault/templates/obsidian-plugins.md tests/test_vendor_obsidian_plugin.py tests/test_templates.py tests/test_config_validity.py
git push -u origin substrate-e/vendored-plugins
```

(`git add` on the plugin tree first: a pathspec commit of a directory needs the new files in the index; `research_vault/templates/obsidian` is the pathspec.) The dev lane's form hooks must not reformat `main.js`: confirm `.pre-commit-config.yaml` selects no JavaScript or CSS owner (it does not today), and that mdformat's selection excludes `THIRD-PARTY-NOTICES` (no `.md` suffix).

______________________________________________________________________

### Task 4: Doctor's `obsidian` check, the compile tool's mode row, the component finding (§6.3, #161)

**Files:**

- Modify: `research_vault/doctor.py` (`_obsidian_probe`; `_compile_tool_probe(vault)` with the mode), `research_vault/__main__.py:42-59` (`obsidian` in both hard sets), `research_vault/inbox.py` (`obsidian` in `CHECK_IDS` and `COMPONENT_CHECKS`), `research_vault/verify.py` (publish-closing), `docs/agents/terminology.md:137,139`, `skills/publish/SKILL.md:33`, `skills/setup-vault/SKILL.md:65`
- Test: `tests/test_doctor.py`, `tests/test_okf.py:80-94`, `tests/test_templates.py:176-200`

**Interfaces:**

- Produces: `doctor._obsidian_probe(vault, config) -> Probe` — reads `config["obsidian_config_dir"]` (default `.obsidian`), SKIPPED when the folder is absent, UNREACHABLE naming the file when any config file it needs does not parse, UNMATCHED with per-plugin facts when an enabled plugin's (or Core's) declared key is off its accepted values, MATCHED with notes otherwise: `pinned <tag>, installed <version>` for each vendored plugin whose `manifest.json` version differs from `SOURCE.json`'s tag, `core-plugins.json drifts: <id>=<value>` for a core id off the seed, `recommended plugin <id> installed`, `excluded plugin <id> enabled` (also an `advisory` fact). `doctor._compile_tool_probe(vault)` adds the mode: absent `.vault-meta/mode.json` reads as `generic` (MATCHED); `{"mode": "generic"}` MATCHED; another mode or a malformed file is UNMATCHED in this warn-only probe, with both findings in one reason. `COMPONENT_PROBES` gains `obsidian`; `COMPONENT_CHECKS` gains `obsidian`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_doctor.py` (adding `"obsidian"` to `PROBE_NAMES` after `"compile-tool"` and to `HARD_UNMATCHED` and `HARD_UNREACHABLE`; `tests/test_okf.py:80-94` likewise):

```python
def _seeded_vault(tmp_path):
    vault = tmp_path / "vault"
    scaffold.scaffold_vault(vault, with_obsidian=True)
    (vault / ".research-vault" / "machine.json").write_text(json.dumps({"mailto": "e@example.edu"}))
    return vault


def test_obsidian_probe_passes_a_fresh_seed_with_no_notes(tmp_path):
    vault = _seeded_vault(tmp_path)
    probe = doctor._obsidian_probe(vault, {})
    assert probe == doctor.Probe("obsidian", Result.MATCHED, ".obsidian: every declared key holds; no drift from the seed")


def test_obsidian_probe_notes_a_version_bump_and_core_drift_but_fails_only_a_declared_key(tmp_path):
    vault = _seeded_vault(tmp_path)
    manifest = vault / ".obsidian" / "plugins" / "dataview" / "manifest.json"
    manifest.write_text(json.dumps({**json.loads(manifest.read_text()), "version": "0.5.69"}))
    core = vault / ".obsidian" / "core-plugins.json"
    core.write_text(json.dumps({**json.loads(core.read_text()), "slides": False}))
    probe = doctor._obsidian_probe(vault, {})
    assert probe.result is Result.MATCHED
    assert "dataview pinned 0.5.68, installed 0.5.69" in probe.reason
    assert "core-plugins.json drifts: slides=false" in probe.reason
    core.write_text(json.dumps({**json.loads(core.read_text()), "sync": True}))
    probe = doctor._obsidian_probe(vault, {})
    assert probe.result is Result.UNMATCHED
    assert probe.reason == "Core core-plugins.json sync=true (accepted false)"
    assert probe.facts == (("core", ("core-plugins.json sync=true (accepted false)",)),)


def test_obsidian_probe_judges_a_data_json_key_only_on_an_enabled_plugin(tmp_path):
    vault = _seeded_vault(tmp_path)
    data = vault / ".obsidian" / "plugins" / "dataview" / "data.json"
    data.write_text(json.dumps({"enableDataviewJs": True}))
    probe = doctor._obsidian_probe(vault, {})
    assert probe.result is Result.UNMATCHED
    assert probe.reason == "Dataview data.json enableDataviewJs=true (accepted false, unset)"
    enabled = vault / ".obsidian" / "community-plugins.json"
    enabled.write_text(json.dumps([p for p in json.loads(enabled.read_text()) if p != "dataview"]))
    assert doctor._obsidian_probe(vault, {}).result is Result.MATCHED  # a disabled plugin's key is not judged


def test_obsidian_probe_is_unreachable_on_a_truncated_config_file(tmp_path):
    """Screen B §7.37: Obsidian rewrites these files non-atomically; a 0-byte or
    half-written file is an outage to read again, never a verdict."""
    vault = _seeded_vault(tmp_path)
    (vault / ".obsidian" / "plugins" / "dataview" / "data.json").write_text('{"enableDataviewJs": fal')
    probe = doctor._obsidian_probe(vault, {})
    assert probe.result is Result.UNREACHABLE
    assert "plugins/dataview/data.json" in probe.reason


def test_obsidian_probe_reads_the_configured_folder_and_skips_an_absent_one(tmp_path):
    vault = _seeded_vault(tmp_path)
    (vault / ".obsidian").rename(vault / "obsidian-work")
    assert doctor._obsidian_probe(vault, {}) == doctor.Probe("obsidian", Result.SKIPPED, ".obsidian absent")
    probe = doctor._obsidian_probe(vault, {"obsidian_config_dir": "obsidian-work"})
    assert probe.result is Result.MATCHED
    assert probe.reason.startswith("obsidian-work:")


def test_obsidian_probe_reports_recommended_and_excluded_plugins_present(tmp_path):
    vault = _seeded_vault(tmp_path)
    (vault / ".obsidian" / "plugins" / "omnisearch" / "manifest.json").write_text(json.dumps({"id": "omnisearch", "version": "1.31.0"}))
    enabled = vault / ".obsidian" / "community-plugins.json"
    enabled.write_text(json.dumps([*json.loads(enabled.read_text()), "omnisearch", "obsidian-git"]))
    probe = doctor._obsidian_probe(vault, {})
    assert probe.result is Result.MATCHED
    assert "recommended plugin omnisearch installed" in probe.reason
    assert "excluded plugin obsidian-git enabled" in probe.reason


def test_compile_tool_probe_reads_the_vaults_mode(tmp_vault, monkeypatch):
    monkeypatch.setattr(doctor, "_installed_plugins", lambda: {COMPILE_PLUGIN: [{"gitCommitSha": "32ac5a02c4e0"}]})
    assert doctor._compile_tool_probe(tmp_vault).reason == f"{COMPILE_PLUGIN} at 32ac5a0; mode generic (no .vault-meta/mode.json)"
    meta = tmp_vault / ".vault-meta"
    meta.mkdir()
    (meta / "mode.json").write_text(json.dumps({"mode": "generic"}))
    assert doctor._compile_tool_probe(tmp_vault).result is Result.MATCHED
    (meta / "mode.json").write_text(json.dumps({"mode": "lyt"}))
    probe = doctor._compile_tool_probe(tmp_vault)
    assert probe.result is Result.UNMATCHED
    assert "mode lyt, the vault runs generic" in probe.reason
    (meta / "mode.json").write_text("{bad")
    assert doctor._compile_tool_probe(tmp_vault).result is Result.UNMATCHED
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_doctor.py tests/test_okf.py -q -k "obsidian or compile_tool or thirteen or probes"`
Expected: FAIL.

- [ ] **Step 3: The probes**

In `research_vault/doctor.py`:

```python
def _obsidian_probe(vault: Path, config: dict) -> Probe:
    """Spec §6.3: cold reads of the configured Obsidian folder against the packaged
    declaration. UNMATCHED only for a declared key off its values on an enabled
    plugin; an unparseable file is UNREACHABLE (Obsidian rewrites them
    non-atomically); drift from the seed is a note; an absent folder is SKIPPED."""
    from . import obsidian_plugins  # noqa: PLC0415

    configured = config.get("obsidian_config_dir")
    folder_name = configured if isinstance(configured, str) and configured.strip() else ".obsidian"
    folder = vault / folder_name
    if not folder.is_dir():
        return Probe("obsidian", Result.SKIPPED, f"{folder_name} absent")
    try:
        declaration = obsidian_plugins.declared()
    except (OSError, ValueError) as error:
        return Probe("obsidian", Result.UNMATCHED, f"plugin declaration malformed: {error}")
    try:
        enabled = set(json.loads((folder / "community-plugins.json").read_text(encoding="utf-8"))) if (folder / "community-plugins.json").is_file() else set()
        core = json.loads((folder / "core-plugins.json").read_text(encoding="utf-8")) if (folder / "core-plugins.json").is_file() else {}
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        return Probe("obsidian", Result.UNREACHABLE, f"{folder_name}: config unreadable, read again: {error}")
    failures: list[tuple[str, tuple[str, ...]]] = []
    notes_out: list[str] = []
    seed_core = json.loads((_seed_file("core-plugins.json")).read_text(encoding="utf-8"))
    for plugin_id, value in sorted(core.items()):
        if seed_core.get(plugin_id) is not None and seed_core[plugin_id] != value:
            notes_out.append(f"core-plugins.json drifts: {plugin_id}={json.dumps(value)}")
    for plugin in declaration.plugins:
        plugin_folder = folder / "plugins" / plugin.plugin_id
        manifest = plugin_folder / "manifest.json"
        if plugin.need == "seeded" and manifest.is_file():
            try:
                installed = json.loads(manifest.read_text(encoding="utf-8")).get("version")
            except (OSError, UnicodeError, ValueError) as error:
                return Probe("obsidian", Result.UNREACHABLE, f"{folder_name}: plugins/{plugin.plugin_id}/manifest.json unreadable, read again: {error}")
            if installed != plugin.pin:
                notes_out.append(f"{plugin.plugin_id} pinned {plugin.pin}, installed {installed}")
        if plugin.need == "recommended" and manifest.is_file():
            notes_out.append(f"recommended plugin {plugin.plugin_id} installed")
        if plugin.need == "excluded" and plugin.plugin_id in enabled:
            notes_out.append(f"excluded plugin {plugin.plugin_id} enabled")
    for setting in declaration.settings:
        if setting.plugin == "Core":
            path, component, shown = folder / setting.file, "core", "Core"
        else:
            plugin = declaration.by_name[setting.plugin]
            if plugin.plugin_id not in enabled:
                continue
            path, component, shown = folder / "plugins" / plugin.plugin_id / setting.file, plugin.plugin_id, plugin.name
        try:
            value = obsidian_plugins.read_key(path, setting.key)
        except obsidian_plugins.ConfigUnreadable as error:
            return Probe("obsidian", Result.UNREACHABLE, f"{folder_name}: {path.relative_to(folder).as_posix()} unreadable, read again: {error}")
        if value not in setting.accepted:
            fact = f"{setting.file} {setting.key}={value} (accepted {', '.join(setting.accepted)})"
            existing = dict(failures)
            existing[component] = (*existing.get(component, ()), fact)
            failures = list(existing.items())
    if failures:
        names = {"core": "Core", **{p.plugin_id: p.name for p in declaration.plugins}}
        return Probe("obsidian", Result.UNMATCHED, "; ".join(f"{names[c]} {f}" for c, fs in failures for f in fs), facts=tuple(failures))
    detail = "; ".join(notes_out) if notes_out else "every declared key holds; no drift from the seed"
    return Probe("obsidian", Result.MATCHED, f"{folder_name}: {detail}")


def _seed_file(name: str):
    from importlib import resources  # noqa: PLC0415

    return resources.files("research_vault").joinpath("templates", "obsidian", name)
```

`_compile_tool_probe(vault)` appends the mode: read `vault/.vault-meta/mode.json`; absent gives `; mode generic (no .vault-meta/mode.json)`; `{"mode": "generic"}` gives `; mode generic`; another string is UNMATCHED with `; mode <x>, the vault runs generic (CONTEXT.md's paths)`; a malformed file is UNMATCHED `; mode.json unreadable`. Its sha half is unchanged, and both findings share the one cell (assembly §9's accepted defect). `doctor()` inserts `_obsidian_probe(vault, config)` after `_compile_tool_probe(vault)`; `COMPONENT_PROBES` gains `"obsidian"`; `cold_rows` includes it. `__main__.DOCTOR_HARD_UNMATCHED` and `DOCTOR_HARD_UNREACHABLE` gain `"obsidian"`; `inbox.CHECK_IDS` and `COMPONENT_CHECKS` gain `"obsidian"`; `verify.CLOSING_BY_SURFACE["publish"]` gains it; `docs/agents/terminology.md:137,139` gain `obsidian` in both rows; `skills/publish/SKILL.md:33` gains it. `skills/setup-vault/SKILL.md:65`: replace “No doctor row observes it yet (lane 3a).” with “Doctor's `compile-tool` row reports it beside the tool's pin; a mode other than generic is a warning.”

- [ ] **Step 4: Run the suite, commit, branch, close #161**

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat docs/agents/terminology.md skills/publish/SKILL.md skills/setup-vault/SKILL.md
git switch -c substrate-e/obsidian-check
git commit -m "feat(doctor): the obsidian check reads the configured folder cold against the plugin declaration; compile-tool reports the vault's mode (§6.3, #161)" -- research_vault/doctor.py research_vault/__main__.py research_vault/inbox.py research_vault/verify.py docs/agents/terminology.md skills/publish/SKILL.md skills/setup-vault/SKILL.md tests/test_doctor.py tests/test_okf.py
git push -u origin substrate-e/obsidian-check
```

After the merge: `gh issue close 161 --comment "Closed by Plan E Tasks 2 and 4: compile-tool reports the vault's mode (absent reads as generic); every seeded .base is YAML-parsed by a repository test and reads no note body; the cold-open leg opens them in Obsidian (Task 6)."`

______________________________________________________________________

### Task 5: setup-vault — the seed, the trust prompt, the verification (§4.7, Q28)

**Files:**

- Modify: `skills/setup-vault/SKILL.md:17-25,44-65`, `research_vault/templates/vault/AGENTS.md` (one sentence on `.obsidian/`)

- Test: `tests/test_skill_files.py:28-40,100-145`, `tests/test_templates.py:123-170`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_skill_files.py` (reading the skill through its `_skill_text()`):

```python
def test_setup_vault_seeds_obsidian_and_hands_consent_to_the_trust_prompt():
    text = _skill_text()
    assert "python3 -m research_vault scaffold --vault PATH [--with-ci] [--with-rw-ci] [--with-obsidian]" in text
    assert "Do you trust the author of this vault?" in text
    assert "Trust author and enable plugins" in text
    assert "eval Object.keys(app.plugins.plugins)" in text
    assert "dev:errors" in text
    assert "Never run `plugins:restrict on`" in text
    assert "setEnable(false)" in text
    assert "`plugins:enabled`" in text  # named as the command that cannot show whether a plugin loaded
    assert "skipped .obsidian/" in text
    assert "LANG" in text
    assert "python3 -m research_vault seal --vault PATH" in text
```

- [ ] **Step 2: Run the test to see it fail**

Run: `python -m pytest tests/test_skill_files.py -q -k "trust_prompt"`
Expected: FAIL.

- [ ] **Step 3: The skill**

`skills/setup-vault/SKILL.md:17-23`: the command becomes `python3 -m research_vault scaffold --vault PATH [--with-ci] [--with-rw-ci] [--with-obsidian]`, and the paragraph gains: “Ask separately whether they want the seeded `.obsidian/` (`--with-obsidian`): the plugins the vault declares, vendored at their pins, with their settings. Scaffold copies it once and only into a vault that has none; if it prints `skipped .obsidian/: already present`, relay the line and its fix (close Obsidian, move `.obsidian/` aside, run scaffold again) — never merge files into an existing `.obsidian/` by hand. Run scaffold before the compile tool's adopt step: adopt writes `.obsidian/` files when they are missing, and a seed that arrives second is skipped whole.”

Add a section after `## Diagnose`:

```markdown
## Obsidian's trust prompt

Obsidian 1.13.7 shows **Do you trust the author of this vault?** on every open of a vault whose `.obsidian/plugins/` holds a loadable manifest, until the person clicks **Trust author and enable plugins**; that click enables exactly the ids in `community-plugins.json` and is the consent step (lanes 2–3 spec §4.7). Tell the person to expect it on the first open and that the choice is kept per vault registration, outside the vault, so a second machine prompts again. Never run `plugins:restrict on` or `eval app.plugins.setEnable(false)`: either silences the prompt for that vault permanently with the plugins off and no message. After the person has clicked, verify with the Obsidian CLI that every seeded plugin loaded — `obsidian eval Object.keys(app.plugins.plugins)` lists the loaded ids and `obsidian dev:errors` must be empty; `plugins:enabled` lists configured ids whether or not they loaded and proves nothing. Novel word count fails to load when the process locale is `C.UTF-8` (`LANG` on WSL and in containers): a `RangeError` in `dev:errors` naming `Intl` is that host fact, not the seed's; tell the person to start Obsidian with `LANG` unset or `C`. Then `python3 -m research_vault seal --vault PATH` after the compile tool's adopt step, so the tool's own files under `wiki/` enter the compiled-page record.
```

`research_vault/templates/vault/AGENTS.md` gains, after the `.research-vault/` line: `` `.obsidian/` is the person's Obsidian configuration, seeded once by scaffold; doctor's `obsidian` row compares it with the declared settings and never rewrites it. `` (update the byte pin in `tests/test_templates.py`).

- [ ] **Step 4: Run the suite, commit, branch**

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider
mdformat skills/setup-vault/SKILL.md research_vault/templates/vault/AGENTS.md
git switch -c substrate-e/setup-vault
git commit -m "docs(skill): setup-vault seeds .obsidian/ on request, hands consent to Obsidian's trust prompt and verifies loaded plugins through the CLI (§4.7)" -- skills/setup-vault/SKILL.md research_vault/templates/vault/AGENTS.md tests/test_skill_files.py tests/test_templates.py
git push -u origin substrate-e/setup-vault
```

______________________________________________________________________

### Task 6: The cold open and the other Obsidian legs (§8)

Attended, on the scratch Obsidian vault with Obsidian 1.13.7 and its CLI; `LANG` unset or `C` for the host (screen B §7.38). Record every result with the date and the Obsidian version in `docs/superpowers/specs/2026-10-03-substrate-components-design-section-1-research.md` under a new heading `## The cold open (measured <date>)`, in the style of its trust-prompt section.

- [ ] **Step 1: Scaffold and open**

`python -m research_vault scaffold --vault <scratch> --with-obsidian`, register the vault in Obsidian, open it. Expected: the trust prompt; after **Trust author and enable plugins**, `obsidian eval Object.keys(app.plugins.plugins)` lists every seeded id and `obsidian dev:errors` is empty. A plugin that is not listed, or named in `dev:errors`, drops to recommended in the table (its folder keeps `data.json` and `SOURCE.json` only) in the same commit; Reference Map, Zotero Annotation Citations and Zotero Deep Linker never loaded in the screen's run and are the ones to watch.

- [ ] **Step 2: Links, embeds, the Search block**

Capture one item from the test Zotero into the scratch vault, compile it, seal, and open a wiki page: a `/`-led markdown link resolves in Obsidian's preview and hover; `![](/wiki/fig.png)` with `|480` as the alt text renders at that width; `![](/system/bases/trust-tier.base)` renders the base; a claim line in `projects/p/draft.md` with `(open-question)` appears under the root index's Search block. Record each; a failure of the `/`-led link is a spec-level finding (decision 10) to report, not to patch here.

- [ ] **Step 3: Screen C's plugins**

For Citations, Zotero Cite Links, Simple Citations and Zotero Lib View (the last two installed from the community list over their seeded `data.json`): with `system/bibliography.json` holding the captured item, the key resolves in each plugin's picker. For Reference Map, Zotero Annotation Citations and Zotero Deep Linker: the load check of Step 1. A plugin whose key resolution fails drops out of the table (seeded or recommended) in the same commit.

- [ ] **Step 4: Recommended plugins over their seed**

Install each recommended plugin from the community list, let it load once, and diff its `data.json` against the seed's: a plugin that rewrote a seeded key (a migration) gets the migrated value seeded instead, in the same commit; a plugin whose rewrite drops a confining key is demoted to a prose recommendation with no `data.json`.

- [ ] **Step 5: Novel word count on a valid-locale host; the Bases File keys**

With `LANG` unset, Novel word count loads (Step 1 covers it); with `LANG=C.UTF-8` it fails with the `Intl` `RangeError` — record both. Read Obsidian's Bases File key set from `app.js` (`@2173021` in 1.13.7) and assert in `tests/test_templates.py` that every `file.<key>` a seeded `.base` uses is in that set (replace the `file.content` absence check with the full-set check once the keys are recorded).

- [ ] **Step 6: Commit the records and corrections**

```bash
git switch -c substrate-e/cold-open
git commit -m "docs(research): the cold open of the seeded .obsidian/ measured; seed corrected from the legs" -- docs/superpowers/specs/2026-10-03-substrate-components-design-section-1-research.md research_vault/templates/obsidian research_vault/templates/obsidian-plugins.md README.md tests/test_templates.py tests/test_vendor_obsidian_plugin.py
git push -u origin substrate-e/cold-open
```

(Only the files a leg changed.)

______________________________________________________________________

### Task 7: The records, the review, the baseline

**Files:**

- Modify: `docs/superpowers/specs/2026-09-05-assembly-design.md` (decision 17's Obsidian half; §6.2's restricted-mode paragraph; §13 T3 and T5; §15 items 13 and 17), `docs/superpowers/specs/2026-10-03-substrate-components-design.md` (§8's legs marked run), `mutation-baseline.txt`

- [ ] **Step 1: The assembly amendments**

Decision 17 (`:84`): after `Obsidian: a **seeded `.obsidian/`folder** in`research_vault/templates/vault/`,` add `*(amended 2026-10-24: at `research_vault/templates/obsidian/`, outside `templates/vault/`, copied once by `scaffold --with-obsidian`, never by doctor's repair — lanes 2–3 spec §4.6)*`. §6.2's paragraph beginning `Two constraints, both **read**:` gains at its end: `*Amended 2026-10-24 (lanes 2–3 spec §4.7): the consent step is Obsidian's own trust prompt, shown on every open of a vault whose `.obsidian/plugins/`holds a loadable manifest until the person clicks Trust author and enable plugins; setup verifies loaded plugins through the CLI and never calls`plugins:restrict on`.*` §13's table: T3's result becomes `**passed** — doctor's `plugins`row has read presence,`appDisabled`and version from`extensions.json` since 2026-09-07; the lanes 2–3 spec's declaration (2026-10-24) reads effective preference values too`; T5's becomes `**passed 2026-10-24 by the lanes 2–3 spec's cold-open leg (§8)**: doctor's `obsidian`row reads`manifest.json` versions against the seed's pins`. §15 item 13: append `**The Obsidian half: the cold-open leg measured `community-plugins.json`and`core-plugins.json`written on every toggle while the app runs (screen B §7.37), so doctor's`obsidian` row reads the last write; a truncated file is UNREACHABLE.**` Item 17: append `**Answered 2026-10-24: the sha256 comparison is rejected (a plugin update rewrites `main.js`by design, and first open rewrites`core-plugins.json`); doctor compares the pinned tag in `SOURCE.json`with the installed`manifest.json` version and notes the difference.**`

- [ ] **Step 2: The spec's §8**

Prefix each §8 bullet that ran with the date it ran and the plan task (`*Run 2026-…, Plan E Task 6.*`), so the list reads as a record; a leg that could not run keeps its bullet and gains the reason.

- [ ] **Step 3: Review, baseline, closes**

As Plan A Task 11: the gate over `obsidian_plugins.py`, `scaffold.py`, `doctor.py`, `stamp.py`; survivors in `read_key`, `_copy_obsidian_seed`, `_obsidian_probe` and `verdict` need a reason or a killing test. The whole-plan review over Plans A–E's `main` range (the spec's whole execution), findings filed. Verify `gh issue view 161 202 --json state`. Confirm every issue the spec carries (§11's list) is closed: `for n in 161 170 172 174 183 185 188 189 190 191 192 193 194 195 196 202 203 204 205 206 207 208 209 210 211 212; do printf '%s ' $n; gh issue view $n --json state --jq .state; done` — every line `CLOSED`, and #178's item 3 comment present.

```bash
mdformat docs/superpowers/specs/2026-09-05-assembly-design.md docs/superpowers/specs/2026-10-03-substrate-components-design.md
git switch -c substrate-e/close
git commit -m "docs(spec): assembly decision 17, §6.2, §13 T3/T5, §15 items 13 and 17 amended; the lanes 2-3 spec's §8 legs recorded" -- docs/superpowers/specs/2026-09-05-assembly-design.md docs/superpowers/specs/2026-10-03-substrate-components-design.md mutation-baseline.txt
git push -u origin substrate-e/close
```

Merge `--ff-only` when green. The spec is executed; its status line (Plan A Task 0) stays "the active spec" until the operator opens the next one.

______________________________________________________________________

## Coverage notes

- §4.1 (core plugins, settings files): Task 2. §4.2 (vendored and recommended, the script decides): Tasks 2–3. §4.3 (the Zotero-reading plugins; their load and key-resolution legs): Tasks 2, 3, 6. §4.4 landed in Plan A. §4.5 (`app.json`): Task 2. §4.6 (packaging, scaffold's one unit, the skip line, `SOURCE.json`, `.claude/settings.json`'s rename was Plan C's): Tasks 1, 3. §4.7 (the trust prompt): Task 5, measured in Task 6.
- §6.2's mode row (#161): Task 4. §6.3 (`obsidian`): Task 4. #202: Task 2.
- §8's Obsidian legs: Task 6 (the Bases column resize ran in Plan C Task 2).
- §11: assembly decision 17, §6.2, §13, §15 items 13 and 17 (Task 7); `ATTRIBUTION.md` and `pyproject.toml` (Task 3); `okf-conformance.md`'s three rows (Task 2); `setup-vault` (Task 5); `README.md`'s plugin tables (Task 2).
- Deviations recorded in the header: Homepage's `File` kind; `newLinkFormat` absolute over Auto Note Mover's row; Tasks seeded under its register row; the copyleft Zotero-reading plugins recommended; excluded-plugin presence as an `advisory` fact.
