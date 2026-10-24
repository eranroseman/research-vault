# Substrate Components, Plan D: The Zotero Declaration and Doctor

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Declare §3's add-ons the way doctor can read them — two tables, every setting a literal, a version floor, excluded add-ons named — and observe them: effective values from `prefs.js` or the shipped `.xpi` default (#190), the floor and `appDisabled` (#191), Better BibTeX auto-exports into the vault, and the component findings capture files that close publish (§6.4). Carry #172 into `docs/agents/sourcing.md`.

**Architecture:** `research_vault/templates/zotero-addons.md` becomes two strictly parsed tables that `README.md` embeds whole; `addons.py` grows a `Declaration` with `Addon` and `Setting` rows, an `.xpi` default reader and a literal comparison; `doctor.py`'s `plugins` probe compares effective values and the floor, a new warn-only `advisory` probe reports `appDisabled` recommended add-ons and active excluded ones, and `Probe` gains per-component facts. `doctor.cold_rows` is the network-free, repair-free subset capture runs after every successful run, filing each failing component under the probe's id with a hash over the failing facts; verify replays open component rows as publish-closing outcomes.

**Tech Stack:** Python 3.12 in `.venv`; stdlib `zipfile` for the `.xpi`; pytest; the test Zotero (`localhost:23129`) for the live legs.

**Spec:** `docs/superpowers/specs/2026-10-03-substrate-components-design.md` §3 (the tables), §6.1, §6.2 (the Better BibTeX auto-export row; the mode row is Plan E's), §6.4, §8's Zotero legs for Linter, ZotMoov and `extensions.json`, §11's `README.md` tables, `sourcing.md` and assembly amendments. Designs cluster 5 (a), (b), (e) and research Q13, Q14 carry the mechanisms. Screen A's §8 table carries the exact preference keys this plan declares. Cites as in Plan A.

**Precondition:** Plans A–C have merged to `main`.

## Global Constraints

Plan A's Global Constraints apply verbatim; branch names are `substrate-d/<task-slug>`. Two more:

- A preference literal in the declaration is spelled as `prefs.js` spells it: `true`, `false`, a bare integer, or a double-quoted JSON string; `unset` means an absent key is accepted. The comparison is between literals, never between decoded values.
- `python -m research_vault doctor` on the operator's production profile is expected to exit 1 after Task 2 until §3's values are set (spec §10, "the operator's production acts"); the plan does not set them.

## Deviations from the spec, settled here

1. **Which doctor ids become check ids.** §6.4 files component findings and §7 coins check ids only for `advisory` and `obsidian`. A finding needs a check id `record_finding` accepts, so the probe ids `plugins`, `bbt-git`, `advisory` and `compile-tool` (and `obsidian`, from Plan E) join `inbox.CHECK_IDS` and terminology §4.4's check-ids row alongside their doctor-probe row (`tests/test_config_validity.py` and `tests/test_skill_contracts.py` accept a name in both rows). `fulltext-sync` runs in the cold set but never fails, so it files nothing; `pyyaml` and `deny-rules` are setup facts, not components, and stay out of the cold set.
2. **Component findings' reason code.** Doctor reasons are free text; a finding's reason must start with a registered code. Capture files them as `mismatch — <component>: <facts>`.
3. **Actions and Tags' settings are not declarable as literals** (a JSON rule set); its row is `optional` with no settings row, and the capture monitor observes its effects (ruling 5). Reading Time has no settings; "its load check first" is Plan E's Obsidian-style load check applied to a Zotero add-on only in the setup wizard's prose.

______________________________________________________________________

### Task 1: The declaration — two tables, strictly parsed, embedded whole (#190 format half)

**Files:**

- Modify: `research_vault/templates/zotero-addons.md` (rewritten), `research_vault/addons.py:9-52` (`Addon`, `Setting`, `Declaration`, `declared`), `README.md:116-127` (the section embeds the whole file), `skills/setup-vault/SKILL.md:50`
- Test: `tests/test_addons.py:8-18`, `tests/test_templates.py:396-398`, `tests/test_doctor.py` (the fixture rows that read `auto_pref`)

**Interfaces:**

- Produces: `addons.Addon(name, addon_id, need, min_version: str | None, key_prefix: str | None, workflows: str)` with `need ∈ {"required", "recommended", "optional", "excluded"}`; `addons.Setting(addon: str, pref: str, accepted: tuple[str, ...])` where each accepted literal is a `prefs.js` token or `unset`; `addons.Declaration(addons: list[Addon], settings: list[Setting])` with `by_id: dict[str, Addon]` and `settings_for(addon_id) -> list[Setting]`; `addons.declared() -> Declaration`, raising `ValueError` when any `|` line under either header fails to parse or a settings row names an add-on the first table lacks. `addons.NEEDS`.

- [ ] **Step 1: Write the failing tests**

Replace `tests/test_addons.py::test_declared_parses_the_packaged_table` with:

```python
def test_declared_parses_both_tables_strictly():
    declaration = addons.declared()
    bbt = declaration.by_id["better-bibtex@iris-advies.com"]
    assert bbt == addons.Addon(
        "Better BibTeX", "better-bibtex@iris-advies.com", "required", None,
        "extensions.zotero.translators.better-bibtex.", "research, long-form writing",
    )
    doi = declaration.by_id["zoteroshortdoi@wiernik.org"]
    assert (doi.need, doi.min_version) == ("recommended", "2.2.0")
    assert {a.need for a in declaration.addons} == {"required", "recommended", "optional", "excluded"}
    assert len([a for a in declaration.addons if a.need == "required"]) == 1
    assert len([a for a in declaration.addons if a.need == "recommended"]) == 7
    assert len([a for a in declaration.addons if a.need == "optional"]) == 19
    assert len([a for a in declaration.addons if a.need == "excluded"]) >= 20
    assert "zotero-mcp-plugin@autoagent.my" not in declaration.by_id  # ruling 9: never declared
    assert declaration.settings_for("zoteroshortdoi@wiernik.org") == [
        addons.Setting("DOI Manager", "extensions.shortdoi.autoretrieve", ('"none"',)),
        addons.Setting("DOI Manager", "extensions.shortdoi.monthly_verify", ("false",)),
    ]
    assert addons.Setting("Citation counts", "extensions.citationcounts.autoretrieve", ('"none"', "unset")) in declaration.settings
    assert sum(1 for s in declaration.settings if s.pref.startswith("extensions.zotero.formatmetadata.rule.")) == 29
    for setting in declaration.settings:
        assert setting.addon in {a.name for a in declaration.addons}, setting
        for literal in setting.accepted:
            assert literal == "unset" or literal in {"true", "false"} or literal.lstrip("-").isdigit() or (literal.startswith('"') and literal.endswith('"')), literal


def test_a_row_the_grammar_cannot_read_raises(monkeypatch, tmp_path):
    """A typo must not delete a check silently (designs cluster 5 (a) [added])."""
    package = tmp_path / "pkg"
    (package / "templates").mkdir(parents=True)
    good = (Path(__file__).resolve().parents[1] / "research_vault" / "templates" / "zotero-addons.md").read_text()
    bad = good.replace("| recommended |", "| recomended |", 1)
    (package / "templates" / "zotero-addons.md").write_text(bad)
    monkeypatch.setattr(addons.resources, "files", lambda _name: package)
    with pytest.raises(ValueError, match="zotero-addons.md: unreadable row"):
        addons.declared()
    orphan = good + '| Nobody | `extensions.nobody.x` | `true` |\n'
    (package / "templates" / "zotero-addons.md").write_text(orphan)
    with pytest.raises(ValueError, match="names no declared add-on"):
        addons.declared()
```

(add `from pathlib import Path` to the test module). `tests/test_templates.py:396-398` stays: it asserts the whole template is in the README.

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_addons.py tests/test_templates.py -q -k "declared or row_the_grammar or readme_embeds"`
Expected: FAIL — `Declaration`, `Setting` missing.

- [ ] **Step 3: The template**

`research_vault/templates/zotero-addons.md` becomes the two tables below, verbatim (mdformat aligns the columns; the parser reads cells, not alignment). A `—` cell means none.

```markdown
### Add-ons

| Add-on                        | Add-on id                                    | Need        | Minimum version | Key prefix                                     | Workflows                                                  |
| ----------------------------- | -------------------------------------------- | ----------- | --------------- | ---------------------------------------------- | ---------------------------------------------------------- |
| Better BibTeX                 | `better-bibtex@iris-advies.com`              | required    | —               | `extensions.zotero.translators.better-bibtex.` | research, long-form writing                                |
| PMCID fetcher                 | `zotero-pmcid-fetcher@iris-advies.com`       | recommended | —               | —                                              | research                                                   |
| DOI Manager                   | `zoteroshortdoi@wiernik.org`                 | recommended | 2.2.0           | —                                              | research                                                   |
| Meta Refresh                  | `metarefresh@zhibo.ark0`                     | recommended | —               | —                                              | research                                                   |
| Linter for Zotero             | `zotero-format-metadata@northword.cn`        | recommended | —               | —                                              | research, personal knowledge management, long-form writing |
| Zotero Duplicate Cleaner      | `zotero-dedup@local.dev`                     | recommended | —               | —                                              | research                                                   |
| Attachment Scanner            | `attachmentscanner@changlab.um.edu.mo`       | recommended | —               | —                                              | research                                                   |
| RapidOCR for Zotero           | `pdfocrforzotero@example.com`                | recommended | —               | —                                              | research                                                   |
| MarkDB-Connect                | `daeda@mit.edu`                              | optional    | —               | —                                              | personal knowledge management                              |
| arXiv Workflow                | `arxiv@allanchain.github.com`                | optional    | —               | —                                              | research                                                   |
| scite                         | `scite-zotero-plugin@scite.ai`               | optional    | —               | —                                              | research                                                   |
| PubPeer                       | `zotero-pubpeer@pubpeer.com`                 | optional    | —               | —                                              | research, long-form writing                                |
| Citation counts               | `zotero-citation-counts@tangzhao20`          | optional    | —               | —                                              | research                                                   |
| open-citations                | `open-citations@zotero-plugin.org`           | optional    | —               | —                                              | research                                                   |
| Google Scholar citation count | `justin@justinribeiro.com`                   | optional    | —               | —                                              | research                                                   |
| ZotSeek                       | `zotseek@zotero.org`                         | optional    | —               | —                                              | personal knowledge management, research                    |
| Better Notes                  | `Knowledge4Zotero@windingwind.com`           | optional    | —               | —                                              | research, personal knowledge management, long-form writing |
| Zutilo                        | `zutilo@www.wesailatdawn.com`                | optional    | —               | —                                              | personal knowledge management, long-form writing           |
| Open PDF                      | `zotero-open-pdf@iris-advies.com`            | optional    | —               | —                                              | research, personal knowledge management                    |
| KeepZotero                    | `keepzotero@yhmtsai`                         | optional    | —               | —                                              | research                                                   |
| Zotero Focused Mode           | `zotero-focused-mode@jaeheelee.de`           | optional    | —               | —                                              | research                                                   |
| Actions and Tags              | `zoterotag@euclpts.com`                      | optional    | —               | —                                              | personal knowledge management                              |
| ZotMoov                       | `zotmoov@wileyy.com`                         | optional    | —               | —                                              | personal knowledge management                              |
| zotxt                         | `zotxt@e6h.org`                              | optional    | —               | —                                              | long-form writing                                          |
| zotero-docling                | `zotero-docling@max3925vats`                 | optional    | —               | —                                              | research, analysis and reports                             |
| MinerU for Zotero             | `mineru-for-zotero@asianfleet.github.io`     | optional    | —               | —                                              | analysis and reports, long-form writing, research          |
| Reading Time                  | `reading-time@local`                         | optional    | —               | —                                              | personal knowledge management                              |
| Zoplicate                     | `zoplicate@chenglongma.com`                  | excluded    | —               | —                                              | —                                                          |
| DOI Fix                       | `doi-fix@zotero.org`                         | excluded    | —               | —                                              | —                                                          |
| Metadata Hunter               | `metadatahunter@federicotorrielli.github.io` | excluded    | —               | —                                              | —                                                          |
| ZotMeta                       | `zotmeta@roadtodream.tech`                   | excluded    | —               | —                                              | —                                                          |
| zotero-ner                    | `zotero-name-normalizer@marcinmilkowski.pl`  | excluded    | —               | —                                              | —                                                          |
| Scholar Sidekick              | `scholar-sidekick@scholar-sidekick.com`      | excluded    | —               | —                                              | —                                                          |
| arxiv-marker                  | `arxiv-marker@lele.dev`                      | excluded    | —               | —                                              | —                                                          |
| Cita                          | `zotero-wikicite@wikidata.org`               | excluded    | —               | —                                              | —                                                          |
| zotero-openalex               | `zotero-openalex@example.com`                | excluded    | —               | —                                              | —                                                          |
| Zotero TLDR                   | `zoterotldr@syt.com`                         | excluded    | —               | —                                              | —                                                          |
| zotero-citation-tally         | `dev@daeh.info`                              | excluded    | —               | —                                              | —                                                          |
| zotero-getcitation            | `getcitation@example.com`                    | excluded    | —               | —                                              | —                                                          |
| semantic-zotero               | `tomasdanis26@gmail.com`                     | excluded    | —               | —                                              | —                                                          |
| Zotero Attanger               | `zoteroattanger@polygon.org`                 | excluded    | —               | —                                              | —                                                          |
| Zotero OCR                    | `zotero-ocr@bib.uni-mannheim.de`             | excluded    | —               | —                                              | —                                                          |
| Zotadata                      | `zotadata@zotero.org`                        | excluded    | —               | —                                              | —                                                          |
| Mktero                        | `mktero@tenglvjun.github.io`                 | excluded    | —               | —                                              | —                                                          |
| Chartero                      | `chartero@volatile.static`                   | excluded    | —               | —                                              | —                                                          |
| Add-on Market for Zotero      | `zoteroAddons@ytshen.com`                    | excluded    | —               | —                                              | —                                                          |
| Notero                        | `notero@vanoni.dev`                          | excluded    | —               | —                                              | —                                                          |
| Zotero Reading List           | `reading-list@hotmail.com`                   | excluded    | —               | —                                              | —                                                          |
| Folder Import for Zotero      | `zotero-folder-import@iris-advies.com`       | excluded    | —               | —                                              | —                                                          |
| Zotero Watch Folder           | `watch-folder@zotero-plugin.org`             | excluded    | —               | —                                              | —                                                          |
| Replication Checker (FLoRA)   | `replication-checker@forrt.org`              | excluded    | —               | —                                              | —                                                          |

### Declared settings

| Add-on             | Preference                                                            | Accepted           |
| ------------------ | --------------------------------------------------------------------- | ------------------ |
| PMCID fetcher      | `extensions.zotero.pmcid.auto`                                        | `false`            |
| PMCID fetcher      | `extensions.zotero.pmcid.tags`                                        | `false`            |
| DOI Manager        | `extensions.shortdoi.autoretrieve`                                    | `"none"`           |
| DOI Manager        | `extensions.shortdoi.monthly_verify`                                  | `false`            |
| Meta Refresh       | `extensions.zotero.metarefresh.titleSimilarityThreshold`              | `"2"`              |
| Meta Refresh       | `extensions.zotero.metarefresh.useS2`                                 | `false`            |
| Meta Refresh       | `extensions.zotero.metarefresh.useOpenAlex`                           | `false`            |
| Meta Refresh       | `extensions.zotero.metarefresh.fieldConferenceName`                   | `false`            |
| Meta Refresh       | `extensions.zotero.metarefresh.backupToExtra`                         | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.lint.onAdded`                       | `true`             |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.require-language`              | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.require-doi`                   | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.require-journal-abbr`          | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.require-short-title`           | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.require-university-place`      | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.no-value-nullish`              | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.no-field-misuse`               | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.no-title-trailing-dot`         | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.no-issue-extra-zeros`          | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.no-pages-extra-zeros`          | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.no-volume-extra-zeros`         | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-title-sentence-case`   | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-shortTitle-sentence-case` | `false`         |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-bookTitle-sentence-case` | `false`          |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-proceedingsTitle-sentence-case` | `false`   |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-title-chemical-formula` | `false`           |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-creators-case`         | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-creators-pinyin`       | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-date-format`           | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-filing-date-format`    | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-issue-date-format`     | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-priority-date-format`  | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-extra-order`           | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-doi-long`              | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-publication-title-alias` | `false`          |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-publication-title-case` | `false`           |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-pages-range`           | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-conference-abbr`       | `false`            |
| Linter for Zotero  | `extensions.zotero.formatmetadata.rule.correct-thesis-type`           | `false`            |
| Attachment Scanner | `extensions.attachmentscanner.monitor_attachments`                    | `true`             |
| Attachment Scanner | `extensions.attachmentscanner.scan_duplicates`                        | `false`            |
| MarkDB-Connect     | `extensions.zotero.mdbc.removetags`                                   | `"addonly"`        |
| arXiv Workflow     | `extensions.zotero.arxiv-workflow.merge.arXivExtra`                   | `true`             |
| arXiv Workflow     | `extensions.zotero.arxiv-workflow.features.arXivUpdate`               | `false`            |
| arXiv Workflow     | `extensions.zotero.arxiv-workflow.merge.trashUnannotatedPDF`          | `false`            |
| Citation counts    | `extensions.citationcounts.autoretrieve`                              | `"none"`, `unset`  |
| open-citations     | `extensions.zotero.opencitations.writeExtra`                          | `false`, `unset`   |
| Google Scholar citation count | `extensions.zotero.gscc.useAutoCountUpdate`                | `false`, `unset`   |
| ZotSeek            | `extensions.zotero.zotseek.mcpServer.enabled`                         | `false`, `unset`   |
| Better Notes       | `extensions.zotero.Knowledge4Zotero.annotationNote.enableTagSync`     | `false`            |
| Better Notes       | `extensions.zotero.Knowledge4Zotero.syncNoteIds`                      | `""`               |
| Better Notes       | `extensions.zotero.Knowledge4Zotero.sync.autoSyncLinkedNotes`         | `false`, `unset`   |
| ZotMoov            | `extensions.zotmoov.file_behavior`                                    | `"copy"`           |
| ZotMoov            | `extensions.zotmoov.enable_automove`                                  | `false`            |
| zotero-docling     | `extensions.zoteroDocling.autoConvert`                                | `false`, `unset`   |
| MinerU for Zotero  | `extensions.zotero.mineruForZotero.apiEnabled`                        | `false`, `unset`   |
```

The Linter rows are the 28 keys section-1 research lists plus `require-doi` (screen A, facts for the spec, item 5); Task 4's live leg verifies the key set against the 3.3.2 `.xpi` and corrects any row before the add-on's `plugins` row can pass.

- [ ] **Step 4: `addons.py`'s parser**

Replace `addons.py:9-52` with:

```python
NEEDS = ("required", "recommended", "optional", "excluded")
_CELL = r"\|\s*(?P<{name}>[^|]*?)\s*"
_ADDON_ROW = re.compile(
    "^" + _CELL.format(name="name") + _CELL.format(name="id") + _CELL.format(name="need")
    + _CELL.format(name="min") + _CELL.format(name="prefix") + _CELL.format(name="workflows") + r"\|$"
)
_SETTING_ROW = re.compile(
    "^" + _CELL.format(name="addon") + _CELL.format(name="pref") + _CELL.format(name="accepted") + r"\|$"
)
_LITERAL = re.compile(r'^(?:true|false|-?\d+|"(?:[^"\\]|\\.)*"|unset)$')
_NONE = "—"


class Addon(NamedTuple):
    name: str
    addon_id: str
    need: str
    min_version: str | None
    key_prefix: str | None
    workflows: str


class Setting(NamedTuple):
    addon: str
    pref: str
    accepted: tuple[str, ...]


class Declaration(NamedTuple):
    addons: list[Addon]
    settings: list[Setting]

    @property
    def by_id(self) -> dict[str, Addon]:
        return {addon.addon_id: addon for addon in self.addons}

    def settings_for(self, addon_id: str) -> list[Setting]:
        name = self.by_id[addon_id].name
        return [setting for setting in self.settings if setting.addon == name]


def _code(cell: str) -> str | None:
    """A backticked cell's text; `—` or empty is None; anything else is a grammar fault."""
    if cell in {"", _NONE}:
        return None
    if cell.startswith("`") and cell.endswith("`") and len(cell) > 2:
        return cell[1:-1]
    raise ValueError(f"zotero-addons.md: unreadable row cell {cell!r}")


def declared() -> Declaration:
    """The packaged declaration (decomposition decision 17, spec §6.1): two tables.

    Every `|` line under either header must parse, or this raises: a typo must
    never delete a check silently. A settings row must name an add-on of the
    first table.
    """
    declaration = resources.files("research_vault").joinpath("templates/zotero-addons.md")
    try:
        text = declaration.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"zotero-addons.md: not UTF-8: {error}") from error
    addons: list[Addon] = []
    settings: list[Setting] = []
    table = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("### "):
            table = line[4:].strip().lower()
            continue
        if not line.startswith("|") or set(line) <= {"|", "-", " "}:
            continue
        if table == "add-ons":
            match = _ADDON_ROW.match(line)
            if match is None or match.group("name") == "Add-on":
                if match is not None:
                    continue
                raise ValueError(f"zotero-addons.md: unreadable row {line!r}")
            need = match.group("need")
            if need not in NEEDS:
                raise ValueError(f"zotero-addons.md: unreadable row {line!r} (need {need!r})")
            minimum = match.group("min")
            addons.append(
                Addon(
                    match.group("name"),
                    _code(match.group("id")) or "",
                    need,
                    None if minimum in {"", _NONE} else minimum,
                    _code(match.group("prefix")),
                    match.group("workflows"),
                )
            )
            if not addons[-1].addon_id:
                raise ValueError(f"zotero-addons.md: unreadable row {line!r} (no id)")
        elif table == "declared settings":
            match = _SETTING_ROW.match(line)
            if match is None:
                raise ValueError(f"zotero-addons.md: unreadable row {line!r}")
            if match.group("addon") == "Add-on":
                continue
            accepted = tuple(
                literal for literal in (_code(part.strip()) for part in match.group("accepted").split(", ")) if literal is not None
            )
            if not accepted or any(_LITERAL.match(literal) is None for literal in accepted):
                raise ValueError(f"zotero-addons.md: unreadable row {line!r} (accepted literals)")
            settings.append(Setting(match.group("addon"), _code(match.group("pref")) or "", accepted))
        else:
            raise ValueError(f"zotero-addons.md: a table row outside a known table: {line!r}")
    names = {addon.name for addon in addons}
    for setting in settings:
        if setting.addon not in names:
            raise ValueError(f"zotero-addons.md: settings row names no declared add-on: {setting.addon!r}")
    return Declaration(addons, settings)
```

`_PREF` (`addons.py:15`) becomes the grammar Task 2 needs: `re.compile(r'^(?:user_)?pref\("(?P<name>[^"]+)",\s*(?P<value>.+?)\);?\s*$')`.

- [ ] **Step 5: README and the skill**

`README.md:116-127` — the section becomes:

```markdown
## Zotero add-ons

Installing a Zotero add-on is a human step in the setup wizard. Doctor reads these two tables (packaged as `research_vault/templates/zotero-addons.md`): the first names every add-on the vault declares — required, recommended, optional, or excluded on harm grounds (the lanes 2–3 spec §3) — the second the preference values each must hold, as `prefs.js` spells them. Doctor's `plugins` row fails when a required add-on is not active, an active add-on is below its minimum version, or an active add-on's effective value (its `prefs.js` line, else the default shipped in its `.xpi`) is not an accepted literal; its `advisory` row warns when a recommended add-on is `appDisabled` or an excluded one is active. `DOI Manager`'s two values must be in `prefs.js` before the add-on is installed.

<the two tables, verbatim>
```

`skills/setup-vault/SKILL.md:50` becomes: `` Zotero .xpi installs are human-only wizard steps. The add-ons the vault asks for are declared once, in the two tables `README.md` embeds from `research_vault/templates/zotero-addons.md`: every add-on with its id and need (required, recommended, optional, excluded) and every preference value an add-on must hold, spelled as `prefs.js` spells it. Walk the person through installing each *required* row in Zotero's Add-ons window and setting each declared value — DOI Manager's two values in `prefs.js` before the add-on is installed, Meta Refresh's `titleSimilarityThreshold` seeded in `prefs.js` because its preferences pane clamps a typed value; never download, never install, never click, and never close Zotero for the user. Doctor's `plugins` probe reads the same tables and fails until the declared values hold; its `advisory` probe warns on an `appDisabled` recommended add-on or an active excluded one. `` (`tests/test_skill_files.py:110-116` pins the needles `Zotero .xpi installs are human-only wizard steps`, `never download`, `never click`, `never close Zotero`, `research_vault/templates/zotero-addons.md`, `README`; all kept.)

- [ ] **Step 6: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider`
Expected: `tests/test_doctor.py` fails where it reads `addon.auto_pref` (`doctor.py:275-280`) — Task 2 rewrites the probe; land this task with the probe's reference to `auto_pref` replaced by a temporary `declaration.settings_for(...)` no-op so the suite is green, or land Tasks 1 and 2 on one branch. The plan takes the second route: continue to Task 2 on the same branch.

______________________________________________________________________

### Task 2: Effective values, the floor, `advisory`, the auto-export check (#190, #191, §6.2)

**Files:**

- Modify: `research_vault/addons.py` (`xpi_defaults`, `literal`, `effective_value`, `version_at_least`, `bbt_auto_exports`), `research_vault/doctor.py:19-24,230-283,449-472` (`Probe.facts`, `_plugins_probe`, `_advisory_probe`, `_bbt_git_probe` through the prefix), `research_vault/__main__.py:42-59` (`advisory` warn-only)
- Modify: `docs/agents/terminology.md:139`, `tests/test_doctor.py::PROBE_NAMES`, `tests/test_okf.py:80-94`
- Test: `tests/test_addons.py`, `tests/test_doctor.py:243-283,320-335,560-570`

**Interfaces:**

- Produces: `addons.literal(value: str | bool | int) -> str` (the `prefs.js` spelling); `addons.xpi_defaults(profile_dir, addon_id) -> dict[str, str]` (key → literal from the `.xpi`'s `prefs.js` then `defaults/preferences/*.js`; `{}` when the xpi is absent; raises `addons.DefaultsUnreadable(message)` when the xpi exists but cannot be opened or a `pref(` line cannot be read); `addons.effective_value(prefs, defaults, key, key_prefix) -> str` (`prefs.js` first, then the default under the full key, then the key minus the prefix, else `"unset"`); `addons.version_at_least(installed: str, floor: str) -> bool | None` (each segment's leading integer; `None` when a segment has none); `addons.bbt_auto_exports(prefs) -> list[dict]` (every JSON object under `extensions.zotero.translators.better-bibtex.autoExport.`); `doctor.Probe(check, result, reason, facts: tuple[tuple[str, tuple[str, ...]], ...] = ())` — per-component failing facts; probes `plugins` (hard) and `advisory` (warn-only) with the semantics below.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_addons.py`:

```python
import zipfile


def _xpi(profile, addon_id, files):
    folder = profile / "extensions"
    folder.mkdir(exist_ok=True)
    with zipfile.ZipFile(folder / f"{addon_id}.xpi", "w") as archive:
        for name, text in files.items():
            archive.writestr(name, text)


def test_literal_spells_values_as_prefs_js_does():
    assert addons.literal(True) == "true" and addons.literal(False) == "false"
    assert addons.literal(2) == "2" and addons.literal(-1) == "-1"
    assert addons.literal("none") == '"none"' and addons.literal("") == '""'
    assert addons.literal('it"s') == '"it\\"s"'


def test_xpi_defaults_read_full_and_relative_keys(tmp_path):
    """Designs cluster 5 (a) [corrected]: BBT 9.0.68 ships `pref("git", "config")`
    with no semicolon and a key relative to its prefix; the five other surveyed
    xpis ship full keys with semicolons."""
    _xpi(tmp_path, "better-bibtex@iris-advies.com", {"prefs.js": 'pref("git", "config")\npref("autoExport", "immediate")\n'})
    _xpi(tmp_path, "zoteroshortdoi@wiernik.org", {"defaults/preferences/prefs.js": 'pref("extensions.shortdoi.autoretrieve", "long");\npref("extensions.shortdoi.monthly_verify", true);\n'})
    assert addons.xpi_defaults(tmp_path, "better-bibtex@iris-advies.com") == {"git": '"config"', "autoExport": '"immediate"'}
    assert addons.xpi_defaults(tmp_path, "zoteroshortdoi@wiernik.org") == {
        "extensions.shortdoi.autoretrieve": '"long"',
        "extensions.shortdoi.monthly_verify": "true",
    }
    assert addons.xpi_defaults(tmp_path, "zotero-pmcid-fetcher@iris-advies.com") == {}  # no xpi: nothing to read


def test_xpi_defaults_name_an_unreadable_archive_or_line(tmp_path):
    (tmp_path / "extensions").mkdir()
    (tmp_path / "extensions" / "broken@x.xpi").write_bytes(b"not a zip")
    with pytest.raises(addons.DefaultsUnreadable, match="broken@x.xpi"):
        addons.xpi_defaults(tmp_path, "broken@x")
    _xpi(tmp_path, "odd@x", {"prefs.js": 'pref("extensions.odd.a", true);\npref(extensions.odd.b, 1);\n'})
    with pytest.raises(addons.DefaultsUnreadable, match="extensions.odd.b"):
        addons.xpi_defaults(tmp_path, "odd@x")


def test_effective_value_prefers_prefs_js_then_the_default_then_unset():
    prefs = {"extensions.shortdoi.autoretrieve": "none"}
    defaults = {"extensions.shortdoi.monthly_verify": "true", "git": '"config"'}
    prefix = "extensions.zotero.translators.better-bibtex."
    assert addons.effective_value(prefs, defaults, "extensions.shortdoi.autoretrieve", None) == '"none"'
    assert addons.effective_value(prefs, defaults, "extensions.shortdoi.monthly_verify", None) == "true"
    assert addons.effective_value(prefs, defaults, prefix + "git", prefix) == '"config"'
    assert addons.effective_value(prefs, defaults, "extensions.zotero.pmcid.auto", None) == "unset"


@pytest.mark.parametrize(
    ("installed", "floor", "expected"),
    [("2.2.0", "2.2.0", True), ("2.10.0", "2.2.0", True), ("1.7.0", "2.2.0", False), ("1.7.0-beta", "2.2.0", False), ("2.2.0-beta", "2.2.0", True), ("v2", "2.2.0", None), ("", "2.2.0", None)],
)
def test_version_at_least_compares_each_segments_leading_integer(installed, floor, expected):
    assert addons.version_at_least(installed, floor) is expected


def test_bbt_auto_exports_decode_the_json_under_the_branch():
    prefs = {
        "extensions.zotero.translators.better-bibtex.autoExport.abc": '{"type":"library","path":"D:\\\\Zotero\\\\kh-vault\\\\system\\\\bibliography.json","translatorID":"x"}',
        "extensions.zotero.translators.better-bibtex.git": "off",
    }
    assert addons.bbt_auto_exports(prefs) == [{"type": "library", "path": "D:\\Zotero\\kh-vault\\system\\bibliography.json", "translatorID": "x"}]
    with pytest.raises(ValueError, match="autoExport.bad"):
        addons.bbt_auto_exports({"extensions.zotero.translators.better-bibtex.autoExport.bad": "{not json"})
```

Rewrite `tests/test_doctor.py::_profile` so the second add-on is `zoteroshortdoi@wiernik.org` at `"2.2.0"`, `active: True` by default, and its `prefs.js` holds the declared literals (`autoretrieve` `"none"`, `monthly_verify` `false`, `pmcid.auto` `false`, `pmcid.tags` `false`), keeping a `doi_auto` switch that writes `"long"` instead of `"none"`. Update `:320-335` (`plugins` MATCHED; the reason names each add-on's state; an undeclared active add-on is listed as `undeclared`) and `:560-570`:

```python
    assert by["plugins"] == doctor.Probe(
        "plugins",
        Result.UNMATCHED,
        'DOI Manager extensions.shortdoi.autoretrieve="long" (accepted "none")',
        facts=(("zoteroshortdoi@wiernik.org", ('extensions.shortdoi.autoretrieve="long" (accepted "none")',)),),
    )
```

Append to `tests/test_doctor.py` (adding `"advisory"` to `PROBE_NAMES` after `"plugins"` and to `WARN_ONLY`; `tests/test_okf.py:80-94` likewise):

```python
def _profile_with(tmp_path, addons_list, prefs_lines, xpis=()):
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "extensions.json").write_text(json.dumps({"addons": addons_list}))
    (profile / "prefs.js").write_text("".join(f'user_pref("{k}", {v});\n' for k, v in prefs_lines))
    from tests.test_addons import _xpi

    for addon_id, files in xpis:
        _xpi(profile, addon_id, files)
    return profile


def _addon(addon_id, version="1.0.0", active=True, app_disabled=False):
    return {"id": addon_id, "type": "extension", "location": "app-profile", "version": version, "active": active, "appDisabled": app_disabled}


def test_plugins_reads_the_xpi_default_when_prefs_js_lacks_the_key(tmp_vault, tmp_path, monkeypatch):
    profile = _profile_with(
        tmp_path,
        [_addon("better-bibtex@iris-advies.com", "9.0.68"), _addon("zotero-pmcid-fetcher@iris-advies.com", "1.0.3")],
        [],
        xpis=[("zotero-pmcid-fetcher@iris-advies.com", {"prefs.js": 'pref("extensions.zotero.pmcid.auto", true);\npref("extensions.zotero.pmcid.tags", false);\n'})],
    )
    vault = _profiled_vault(tmp_vault, tmp_path, profile)
    by = {p.check: p for p in doctor.doctor(vault, client=_ready_client(monkeypatch))}
    assert by["plugins"].result is Result.UNMATCHED
    assert by["plugins"].reason == "PMCID fetcher extensions.zotero.pmcid.auto=true (accepted false)"


def test_plugins_is_unreachable_when_a_needed_default_cannot_be_read(tmp_vault, tmp_path, monkeypatch):
    profile = _profile_with(tmp_path, [_addon("better-bibtex@iris-advies.com", "9.0.68"), _addon("zotero-pmcid-fetcher@iris-advies.com")], [])
    (profile / "extensions" ).mkdir(exist_ok=True)
    (profile / "extensions" / "zotero-pmcid-fetcher@iris-advies.com.xpi").write_bytes(b"not a zip")
    vault = _profiled_vault(tmp_vault, tmp_path, profile)
    by = {p.check: p for p in doctor.doctor(vault, client=_ready_client(monkeypatch))}
    assert by["plugins"].result is Result.UNREACHABLE
    assert "zotero-pmcid-fetcher@iris-advies.com.xpi" in by["plugins"].reason


def test_an_unmatched_addon_outranks_an_unreadable_default(tmp_vault, tmp_path, monkeypatch):
    profile = _profile_with(
        tmp_path,
        [_addon("better-bibtex@iris-advies.com", "9.0.68"), _addon("zotero-pmcid-fetcher@iris-advies.com"), _addon("zoteroshortdoi@wiernik.org", "2.2.0")],
        [("extensions.shortdoi.autoretrieve", '"long"'), ("extensions.shortdoi.monthly_verify", "false")],
    )
    (profile / "extensions").mkdir(exist_ok=True)
    (profile / "extensions" / "zotero-pmcid-fetcher@iris-advies.com.xpi").write_bytes(b"not a zip")
    vault = _profiled_vault(tmp_vault, tmp_path, profile)
    by = {p.check: p for p in doctor.doctor(vault, client=_ready_client(monkeypatch))}
    assert by["plugins"].result is Result.UNMATCHED


def test_version_floor_and_advisory_rows(tmp_vault, tmp_path, monkeypatch):
    """#191: 1.6.0 appDisabled is advisory's warning while plugins passes; an
    active 1.7.0 is below the floor; an active excluded add-on is advisory's."""
    profile = _profile_with(
        tmp_path,
        [_addon("better-bibtex@iris-advies.com", "9.0.68"), _addon("zoteroshortdoi@wiernik.org", "1.6.0", active=False, app_disabled=True), _addon("zoplicate@chenglongma.com", "5.1.1")],
        [],
    )
    vault = _profiled_vault(tmp_vault, tmp_path, profile)
    by = {p.check: p for p in doctor.doctor(vault, client=_ready_client(monkeypatch))}
    assert by["plugins"].result is Result.MATCHED
    assert by["advisory"] == doctor.Probe(
        "advisory", Result.UNMATCHED,
        "DOI Manager appDisabled (recommended); Zoplicate active (excluded on harm grounds)",
        facts=(("zoteroshortdoi@wiernik.org", ("appDisabled (recommended)",)), ("zoplicate@chenglongma.com", ("active (excluded on harm grounds)",))),
    )
    profile = _profile_with(tmp_path / "second", [_addon("better-bibtex@iris-advies.com", "9.0.68"), _addon("zoteroshortdoi@wiernik.org", "1.7.0-beta")], [("extensions.shortdoi.autoretrieve", '"none"'), ("extensions.shortdoi.monthly_verify", "false")])
    vault = _profiled_vault(tmp_vault, tmp_path, profile)
    by = {p.check: p for p in doctor.doctor(vault, client=_ready_client(monkeypatch))}
    assert by["plugins"].reason == "DOI Manager 1.7.0-beta below 2.2.0"


def test_bbt_auto_export_into_the_vault_fails_plugins(tmp_vault, tmp_path, monkeypatch):
    target = str(tmp_vault / "system" / "bibliography.json").replace("/", "\\")
    export = json.dumps({"type": "library", "path": "D:\\Zotero\\" + target.split("\\", 1)[1], "translatorID": "x"})
    profile = _profile_with(
        tmp_path,
        [_addon("better-bibtex@iris-advies.com", "9.0.68")],
        [("extensions.zotero.translators.better-bibtex.autoExport.abc", json.dumps(export))],
    )
    vault = _profiled_vault(tmp_vault, tmp_path, profile)
    by = {p.check: p for p in doctor.doctor(vault, client=_ready_client(monkeypatch))}
    assert by["plugins"].result is Result.UNMATCHED
    assert "Better BibTeX auto-export targets system/bibliography.json" in by["plugins"].reason
```

(`_profiled_vault`'s `path_map` maps the Windows prefix `D:\\Zotero\\` to `<tmp_path>/`, so build the export's path from `tmp_path`-relative pieces so `paths.to_local` resolves it into the vault; adjust the string arithmetic to the fixture's actual layout.) Also test `bbt-git`: `git` read through the prefix, `"off"` MATCHED, `"config"` MATCHED only without a BBT opt-in in `.git/config`, `"always"` UNMATCHED.

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_addons.py tests/test_doctor.py tests/test_okf.py -q`
Expected: FAIL throughout.

- [ ] **Step 3: `addons.py`'s readers**

Append to `research_vault/addons.py`:

```python
import zipfile

class DefaultsUnreadable(RuntimeError):
    """An xpi exists but cannot be read, or a `pref(` line in it cannot be parsed."""


def literal(value: str | bool | int) -> str:
    """A decoded preference as prefs.js spells it."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return json.dumps(value, ensure_ascii=False)


def xpi_defaults(profile_dir: Path, addon_id: str) -> dict[str, str]:
    """The shipped defaults of one add-on: `prefs.js` at the archive root, then
    every `defaults/preferences/*.js` (designs cluster 5 (a), measured). Keys
    are as written — full, or relative to the add-on's prefix (Better BibTeX)."""
    xpi = Path(profile_dir) / "extensions" / f"{addon_id}.xpi"
    if not xpi.is_file():
        return {}
    defaults: dict[str, str] = {}
    try:
        with zipfile.ZipFile(xpi) as archive:
            names = [n for n in archive.namelist() if n == "prefs.js" or (n.startswith("defaults/preferences/") and n.endswith(".js"))]
            for name in sorted(names, key=lambda n: (n != "prefs.js", n)):
                for line in archive.read(name).decode("utf-8", errors="replace").splitlines():
                    stripped = line.strip()
                    if not stripped.startswith(("pref(", "user_pref(")):
                        continue
                    match = _PREF.match(stripped)
                    if match is None:
                        raise DefaultsUnreadable(f"{xpi.name}: unreadable preference line {stripped!r}")
                    defaults[match.group("name")] = _literal_token(match.group("value").strip())
    except (OSError, zipfile.BadZipFile) as error:
        raise DefaultsUnreadable(f"{xpi.name}: {error}") from error
    return defaults


def _literal_token(raw: str) -> str:
    if raw in {"true", "false"} or raw.lstrip("-").isdigit():
        return raw
    return literal(_string_pref(raw)) if raw.startswith('"') else raw


def effective_value(prefs: dict, defaults: dict[str, str], key: str, key_prefix: str | None) -> str:
    """prefs.js first, then the shipped default under the full key, then under
    the key minus the add-on's prefix; `unset` when none holds it."""
    if key in prefs:
        return literal(prefs[key])
    if key in defaults:
        return defaults[key]
    if key_prefix and key.startswith(key_prefix) and key[len(key_prefix):] in defaults:
        return defaults[key[len(key_prefix):]]
    return "unset"


def version_at_least(installed: str, floor: str) -> bool | None:
    """Each segment's leading integer (#191): `1.7.0-beta` reads as 1.7.0; a
    segment with no leading digits is None, which the probe names."""

    def parse(text: str) -> list[int] | None:
        parts = []
        for segment in text.split("."):
            match = re.match(r"\d+", segment)
            if match is None:
                return None
            parts.append(int(match.group(0)))
        return parts

    have, want = parse(installed), parse(floor)
    if have is None or want is None:
        return None
    width = max(len(have), len(want))
    have += [0] * (width - len(have))
    want += [0] * (width - len(want))
    return have >= want


BBT_PREFIX = "extensions.zotero.translators.better-bibtex."
BBT_AUTO_EXPORT = BBT_PREFIX + "autoExport."


def bbt_auto_exports(prefs: dict) -> list[dict]:
    """Every auto-export Better BibTeX keeps as a JSON string under its branch
    (designs cluster 5 (e), measured on 9.0.68); an unparseable one raises."""
    exports = []
    for key in sorted(k for k in prefs if k.startswith(BBT_AUTO_EXPORT)):
        value = prefs[key]
        if isinstance(value, str) and value.startswith('"'):
            value = _string_pref(value)
        try:
            document = json.loads(value) if isinstance(value, str) else value
        except ValueError as error:
            raise ValueError(f"{key}: {error}") from error
        if isinstance(document, dict):
            exports.append(document)
    return exports
```

`read_prefs` keeps decoding `user_pref` lines; `_PREF` accepts both spellings and an optional semicolon (Task 1).

- [ ] **Step 4: `doctor.py`**

`Probe` gains `facts: tuple[tuple[str, tuple[str, ...]], ...] = ()`. `_bbt_git_probe(profile, vault)` resolves `git` through `addons.effective_value(prefs, defaults, addons.BBT_PREFIX + "git", addons.BBT_PREFIX)` with the BBT xpi defaults: `"off"` MATCHED; `"config"` MATCHED only when `vault/.git/config` holds no `[zotero]` section with a Better BibTeX opt-in (the key name is measured in Task 4; until then any `[zotero]` section counts); anything else UNMATCHED with `facts=(("better-bibtex@iris-advies.com", (f"git={value}",)),)`. Replace `_plugins_probe` with:

```python
def _machine_folders(vault: Path) -> tuple[str, ...]:
    """Ruling 1's roster as vault-relative prefixes a Better BibTeX export must not target."""
    return ("literature/", "wiki/", "log/", "fulltext/", "system/propagations/", "log.md", "inbox/review-queue.md", "system/bibliography.json")


def _export_targets_vault(export: dict, vault: Path) -> str | None:
    raw = export.get("path")
    if not isinstance(raw, str) or not raw:
        return None
    try:
        local = paths.to_local(raw, vault) if _WINDOWS_PATH.match(raw) else Path(raw)
        relative = local.resolve().relative_to(vault.resolve()).as_posix()
    except (paths.PathError, OSError, ValueError, AttributeError, TypeError):
        return None
    return relative if any(relative == f or relative.startswith(f) for f in _machine_folders(vault)) else None


_WINDOWS_PATH = re.compile(r"^[A-Za-z]:\\|^\\\\")


def _plugins_probe(profile, vault: Path) -> Probe:
    if isinstance(profile, _ProfileHold):
        return Probe("plugins", profile.result, profile.reason)
    try:
        observed = addons.observe(profile.path)
    except OSError as error:
        return Probe("plugins", Result.UNREACHABLE, f"extensions.json unreadable: {error}")
    except (UnicodeError, ValueError, KeyError, AttributeError, TypeError) as error:
        return Probe("plugins", Result.UNMATCHED, f"extensions.json malformed: {error}")
    try:
        declaration = addons.declared()
    except (OSError, ValueError) as error:
        return Probe("plugins", Result.UNMATCHED, f"add-on declaration malformed: {error}")
    failures: list[tuple[str, tuple[str, ...]]] = []
    unreachable: list[str] = []
    notes_out: list[str] = []
    for addon in declaration.addons:
        if addon.need == "excluded":
            continue
        seen = observed.get(addon.addon_id)
        state = "missing" if seen is None else "appDisabled" if seen["appDisabled"] else "inactive" if not seen["active"] else "active"
        notes_out.append(f"{addon.addon_id} {state}")
        facts: list[str] = []
        if addon.need == "required" and state != "active":
            facts.append(state)
        if state == "active" and addon.min_version:
            at_least = addons.version_at_least(seen["version"] or "", addon.min_version)
            if at_least is None:
                facts.append(f"version {seen['version']!r} unreadable against floor {addon.min_version}")
            elif not at_least:
                facts.append(f"{seen['version']} below {addon.min_version}")
        if state == "active" and declaration.settings_for(addon.addon_id):
            defaults: dict[str, str] | None
            defaults_error = ""
            try:
                defaults = addons.xpi_defaults(profile.path, addon.addon_id)
            except addons.DefaultsUnreadable as error:
                defaults, defaults_error = None, str(error)
            for setting in declaration.settings_for(addon.addon_id):
                if setting.pref in profile.prefs or defaults is not None:
                    value = addons.effective_value(profile.prefs, defaults or {}, setting.pref, addon.key_prefix)
                else:
                    unreachable.append(f"{addon.name}: {setting.pref} needs the shipped default and {defaults_error}")
                    continue
                if value not in setting.accepted:
                    facts.append(f"{setting.pref}={value} (accepted {', '.join(setting.accepted)})")
        if facts:
            failures.append((addon.addon_id, tuple(facts)))
    for addon_id in sorted(set(observed) - set(declaration.by_id)):
        notes_out.append(f"{addon_id} undeclared")
    try:
        for export in addons.bbt_auto_exports(profile.prefs):
            hit = _export_targets_vault(export, vault)
            if hit is not None:
                failures.append(("better-bibtex@iris-advies.com", (f"Better BibTeX auto-export targets {hit}",)))
    except ValueError as error:
        unreachable.append(f"Better BibTeX auto-export unreadable: {error}")
    if failures:
        shown = "; ".join(f"{declaration.by_id[i].name} {fact}" for i, fs in failures for fact in fs)
        return Probe("plugins", Result.UNMATCHED, shown, facts=tuple(failures))
    if unreachable:
        return Probe("plugins", Result.UNREACHABLE, "; ".join(unreachable))
    return Probe("plugins", Result.MATCHED, "; ".join(notes_out))


def _advisory_probe(profile) -> Probe:
    """Warn-only (#191, Q14): a recommended or required add-on Zotero refuses to
    load, and an add-on excluded on harm grounds that is active."""
    if isinstance(profile, _ProfileHold):
        return Probe("advisory", profile.result, profile.reason)
    try:
        observed = addons.observe(profile.path)
        declaration = addons.declared()
    except (OSError, UnicodeError, ValueError, KeyError, AttributeError, TypeError) as error:
        return Probe("advisory", Result.SKIPPED, f"plugins row carries the fault: {error}")
    warnings: list[tuple[str, tuple[str, ...]]] = []
    for addon in declaration.addons:
        seen = observed.get(addon.addon_id)
        if seen is None:
            continue
        if addon.need in {"required", "recommended"} and seen["appDisabled"]:
            warnings.append((addon.addon_id, (f"appDisabled ({addon.need})",)))
        if addon.need == "excluded" and seen["active"]:
            warnings.append((addon.addon_id, ("active (excluded on harm grounds)",)))
    if warnings:
        shown = "; ".join(f"{declaration.by_id[i].name} {fact}" for i, fs in warnings for fact in fs)
        return Probe("advisory", Result.UNMATCHED, shown, facts=tuple(warnings))
    return Probe("advisory", Result.MATCHED, "no appDisabled recommended add-on, no active excluded add-on")
```

`doctor()` inserts `_advisory_probe(profile)` after `_plugins_probe(profile, vault)`. `__main__.DOCTOR_WARN_ONLY` gains `"advisory"`; `docs/agents/terminology.md:139` gains `` `advisory` ``. The `_WINDOWS_FILE_URL` path-shim logic is untouched; `_export_targets_vault` reuses `paths.to_local` for Windows paths only.

- [ ] **Step 5: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS. `tests/test_doctor.py::test_doctor_reports_the_thirteen_probes_in_order` and `test_cmd_doctor_sets_partition_the_thirteen_probes` carry the new names (`advisory`).

- [ ] **Step 6: Form, commit, branch (Tasks 1 and 2), close #190 and #191**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat research_vault/templates/zotero-addons.md README.md skills/setup-vault/SKILL.md docs/agents/terminology.md
git switch -c substrate-d/declaration
git commit -m "feat(doctor): the two-table add-on declaration; effective values from prefs.js or the xpi default; the 2.2.0 floor; advisory; Better BibTeX auto-exports into the vault (#190, #191)" -- research_vault/templates/zotero-addons.md research_vault/addons.py research_vault/doctor.py research_vault/__main__.py README.md skills/setup-vault/SKILL.md docs/agents/terminology.md tests/test_addons.py tests/test_doctor.py tests/test_okf.py tests/test_templates.py
git push -u origin substrate-d/declaration
```

After the merge:

```bash
gh issue close 190 --comment "Closed by Plan D Tasks 1-2: the declaration is two tables (add-ons; declared settings with prefs.js literals, several accepted, unset), parsed strictly; doctor compares each effective value — prefs.js, else the xpi's shipped default — with the accepted literals, so DOI Manager's \"none\" and every confining value of the lanes 2-3 screen can be declared."
gh issue close 191 --comment "Closed by Plan D Task 2: DOI Manager's row carries a 2.2.0 minimum version compared by each segment's leading integer; an active build below it fails plugins; an appDisabled recommended add-on is the warn-only advisory row, so 1.6.0 no longer passes."
```

______________________________________________________________________

### Task 3: Component findings at capture, closing publish (§6.4, Q13)

**Files:**

- Modify: `research_vault/doctor.py` (`COMPONENT_PROBES`, `cold_rows`), `research_vault/capture.py:433-579` (files the rows), `research_vault/inbox.py:67-91` (the component check ids; `component_rows`), `research_vault/verify.py:53-79,720-800` (replay; publish-closing), `research_vault/__main__.py` (`_hold`'s hash parameter)
- Modify: `docs/agents/terminology.md:137`, `skills/publish/SKILL.md:33`, `skills/capture-source/SKILL.md` (one sentence), `docs/superpowers/specs/2026-09-05-assembly-design.md` §9 (the `prefs.js` amendment)
- Test: `tests/test_doctor.py`, `tests/test_capture.py`, `tests/test_verify_cli.py`

**Interfaces:**

- Produces: `doctor.COMPONENT_PROBES = ("fulltext-sync", "bbt-git", "plugins", "advisory", "compile-tool")` (Plan E appends `obsidian`); `doctor.cold_rows(vault_root) -> list[Probe]` — those probes only, no network, no repair, reading `machine.json` and the profile cold; `inbox.COMPONENT_CHECKS = frozenset({"plugins", "bbt-git", "advisory", "compile-tool"})` joining `CHECK_IDS`; `inbox.component_rows(vault) -> list[Finding]` (open entries whose check is a component check); `capture` files one finding per failing component: check = probe id, target = component id, reason `mismatch — <component>: <facts>`, `target_hash = sha256("\n".join(facts))[:16]`; `verify._plan_state` replays open component rows as `Outcome(check, target, UNMATCHED, reason, extra={"component": True})` with the stored hash; `CLOSING_BY_SURFACE["publish"]` gains the component checks.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_doctor.py`:

```python
def test_cold_rows_run_no_network_and_no_repair(tmp_vault, tmp_path, monkeypatch):
    """§6.4: the subset capture runs. No ZoteroClient is built, scaffold never runs."""
    from research_vault import scaffold

    profile = _profile(tmp_path)
    vault = _profiled_vault(tmp_vault, tmp_path, profile)
    monkeypatch.setattr(scaffold, "scaffold_vault", lambda *a, **k: pytest.fail("repair ran"))
    monkeypatch.setattr(doctor, "ZoteroClient", lambda *a, **k: pytest.fail("network client built"))
    rows = doctor.cold_rows(vault)
    assert [p.check for p in rows] == list(doctor.COMPONENT_PROBES)
    assert all(p.result is not Result.UNREACHABLE or "zotero" not in p.reason for p in rows)
```

Append to `tests/test_capture.py`:

```python
def test_capture_files_each_failing_component_hashed_on_its_facts(tmp_vault, tmp_path, monkeypatch):
    """§6.4: one finding per failing component under the probe's id; the hash
    covers only the failing facts, so an auto-update re-fires nothing."""
    import hashlib

    from research_vault import doctor, inbox

    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    probes = [
        doctor.Probe("plugins", Result.UNMATCHED, "PMCID fetcher extensions.zotero.pmcid.auto=true (accepted false)", facts=(("zotero-pmcid-fetcher@iris-advies.com", ("extensions.zotero.pmcid.auto=true (accepted false)",)),)),
        doctor.Probe("advisory", Result.UNMATCHED, "Zoplicate active (excluded on harm grounds)", facts=(("zoplicate@chenglongma.com", ("active (excluded on harm grounds)",)),)),
        doctor.Probe("bbt-git", Result.MATCHED, "git=off"),
    ]
    monkeypatch.setattr(capture.doctor, "cold_rows", lambda vault: probes)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    rows = sorted(((f.check, f.target, f.reason, f.target_hash) for f in inbox.open_entries(tmp_vault) if f.check in inbox.COMPONENT_CHECKS))
    assert rows == [
        ("advisory", "zoplicate@chenglongma.com", "mismatch — zoplicate@chenglongma.com: active (excluded on harm grounds)", hashlib.sha256(b"active (excluded on harm grounds)").hexdigest()[:16]),
        ("plugins", "zotero-pmcid-fetcher@iris-advies.com", "mismatch — zotero-pmcid-fetcher@iris-advies.com: extensions.zotero.pmcid.auto=true (accepted false)", hashlib.sha256(b"extensions.zotero.pmcid.auto=true (accepted false)").hexdigest()[:16]),
    ]
    capture.capture(tmp_vault, client, ["E352DFS8"])
    assert len([f for f in inbox.open_entries(tmp_vault) if f.check in inbox.COMPONENT_CHECKS]) == 2  # no duplicate rows
```

Append to `tests/test_verify_cli.py`:

```python
def test_open_component_rows_close_publish_until_acknowledged(net_vault):
    from research_vault import inbox, verify

    assert inbox.COMPONENT_CHECKS <= inbox.CHECK_IDS
    assert inbox.COMPONENT_CHECKS <= verify.CLOSING_BY_SURFACE["publish"]
    assert not (inbox.COMPONENT_CHECKS & verify.CLOSING_BY_SURFACE["commit"])
    inbox.append_entry(net_vault, "plugins", "zoplicate@chenglongma.com", Result.UNMATCHED, "mismatch — zoplicate@chenglongma.com: active (excluded on harm grounds)", target_hash="abcdef0123456789")
    _report, effective, _hashes, warning = verify.verify_state(net_vault, network=False)
    (row,) = [o for o in effective if o.check == "plugins"]
    assert row.extra.get("component") is True
    assert verify.surface_decision("publish", effective, warning)[0] == 1
    assert verify.surface_decision("commit", effective, warning)[0] == 0
    finding = next(f for f in inbox.open_entries(net_vault) if f.check == "plugins")
    inbox.append_ack(net_vault, finding.id, "manual — accepted until the fetcher is reconfigured", "human:eran")
    _report, effective, _hashes, warning = verify.verify_state(net_vault, network=False)
    assert verify.surface_decision("publish", effective, warning)[0] == 0
    assert len([f for f in inbox.load(net_vault) if f.check == "plugins" and f.ack_of is None]) == 1  # replay never re-files
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_doctor.py tests/test_capture.py tests/test_verify_cli.py -q -k "cold_rows or component"`
Expected: FAIL.

- [ ] **Step 3: `doctor.cold_rows`, the registries, capture, verify**

`research_vault/doctor.py`:

```python
# The network-free, repair-free probes capture runs after every successful run
# (spec §6.4, Q13): the component rows. `tree` repairs, the Zotero rows need
# the app, `pyyaml` and `deny-rules` are setup facts, not components.
COMPONENT_PROBES = ("fulltext-sync", "bbt-git", "plugins", "advisory", "compile-tool")


def cold_rows(vault_root) -> list[Probe]:
    vault = Path(vault_root)
    config, _machine = _machine_config(vault)
    profile = _profile_facts(config)
    return [
        _fulltext_sync_probe(profile),
        _bbt_git_probe(profile, vault),
        _plugins_probe(profile, vault),
        _advisory_probe(profile),
        _compile_tool_probe(vault),
    ]
```

(`_compile_tool_probe(vault=None)` gains the optional argument here and ignores it until Plan E reads the mode from it; the existing no-argument call in `doctor()` and `tests/test_doctor.py:956` keep working.) `research_vault/inbox.py`: `COMPONENT_CHECKS = frozenset({"plugins", "bbt-git", "advisory", "compile-tool"})` and `CHECK_IDS` gains the four with the comment `# Component findings capture files from doctor's cold rows (spec §6.4).`; add:

```python
def component_rows(vault) -> list[Finding]:
    return [entry for entry in open_entries(vault) if entry.check in COMPONENT_CHECKS]
```

An add-on id (`zotero-pmcid-fetcher@iris-advies.com`) is an `identifier` target: `inbox._validate_target_kind` (`inbox.py:171-176`) constrains only the `repo-path` kind, and `_validate_text` wants single-line text, so `@` and `.` pass (checked 2026-10-24). `research_vault/capture.py::capture`, after the CSL update and before `return outcomes`:

```python
    for probe in doctor.cold_rows(vault):
        if probe.result is not Result.UNMATCHED or probe.check not in inbox.COMPONENT_CHECKS:
            continue
        for component, facts in probe.facts:
            digest = hashlib.sha256("\n".join(facts).encode("utf-8")).hexdigest()[:16]
            outcomes.append(
                Outcome(probe.check, component, Result.UNMATCHED, f"mismatch — {component}: {'; '.join(facts)}", extra={"target_hash": digest})
            )
```

(`capture.py` imports `doctor` and `inbox`; `doctor` imports `scaffold`, `addons`, `paths`, `zotero` and none of them import `capture`.) `cmd_capture`'s `_print_and_hold` files these under the *row's* check with its hash: change `_print_and_hold` so a row whose `extra` carries `target_hash` is held under `outcome.check` with `target_hash=outcome.extra["target_hash"]` (pass both through `_hold` → `record_finding`); every other row keeps today's behaviour (the verb's check, no hash). `research_vault/verify.py::_plan_state`, after `lint_captured_set`:

```python
    for entry in inbox.component_rows(repository):
        replay = checks.Outcome(entry.check, entry.target, Result.UNMATCHED, entry.reason, {"component": True, "target_hash": entry.target_hash or ""})
        raw.append(replay)
```

and the hashes dict uses `outcome.extra["target_hash"]` for a replay (as Plan B did for history rows). `CLOSING_BY_SURFACE["publish"]` gains the four ids. `docs/agents/terminology.md:137` gains `plugins`, `bbt-git`, `advisory` and `compile-tool` in the check-ids row; `skills/publish/SKILL.md:33` gains them with the sentence “A component row names a Zotero add-on, the compile tool or an Obsidian plugin off its declared settings; acknowledge it or fix the setting.” `skills/capture-source/SKILL.md` gains after the outcome table: “Capture also runs doctor's cold rows and files one review record per add-on or tool off its declared settings (`plugins`, `advisory`, `bbt-git`, `compile-tool`); these hold publish until the setting is fixed or the row acknowledged.”

- [ ] **Step 4: The assembly spec's §9 amendment**

Append to assembly §9, after the paragraph `**Doctor runs in two phases and reports which it completed, per substrate app.**`:

```markdown
*Amended 2026-10-24 (lanes 2–3 spec §6.4, research Q13):* the cold-read rule is relaxed for Zotero's `prefs.js` by measurement — Zotero 10.0.5 runs on Gecko ESR 140, which saves `prefs.js` 500 ms after any change, off the main thread (`Preferences.cpp`, `PREF_DELAY_MS=500`; `preferences.allow.omt-write` defaults true and `omni.ja` does not override it; production's `prefs.js` was last written 2026-10-06 16:51 while Zotero had run since 2026-10-04), so a read while Zotero runs is current and capture's component rows read it live. `extensions.json`'s write timing is Plan D Task 4's measurement; until it is recorded here, a `plugins` row read while Zotero runs is a reading of the last write, not a guarantee.
```

- [ ] **Step 5: Run the suite, commit, branch**

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat docs/agents/terminology.md skills/publish/SKILL.md skills/capture-source/SKILL.md docs/superpowers/specs/2026-09-05-assembly-design.md
git switch -c substrate-d/component-findings
git commit -m "feat(capture): doctor's cold rows file one finding per failing component, hashed on the failing facts; open component rows close publish (§6.4)" -- research_vault/doctor.py research_vault/capture.py research_vault/inbox.py research_vault/verify.py research_vault/__main__.py docs/agents/terminology.md skills/publish/SKILL.md skills/capture-source/SKILL.md docs/superpowers/specs/2026-09-05-assembly-design.md tests/test_doctor.py tests/test_capture.py tests/test_verify_cli.py
git push -u origin substrate-d/component-findings
```

______________________________________________________________________

### Task 4: The live legs on the test Zotero (§8)

Attended, against `localhost:23129`. Each leg records its date, versions and result in the task report; a leg that cannot run leaves its item as the task says.

- [ ] **Step 1: Linter for Zotero's key set and on-add behaviour**

Install Linter 3.3.2 on the test instance. Read its shipped `prefs.js` out of the xpi (`python -c "from research_vault import addons; print(addons.xpi_defaults(PROFILE, 'zotero-format-metadata@northword.cn'))"`) and compare the `rule.*` keys with the 29 rows of the declaration: every declared key must exist; a declared key the xpi lacks is removed from the table, a destructive rule the xpi has and the table lacks is added, in the same commit. Set the 29 keys false and `lint.onAdded=true`, then `python -m research_vault add --vault <scratch> --base http://localhost:23129 --item messy.json` with a `date: "Spring 2020"`, `pages: "100-110"`, a lower-case title and a `language: ""`; after the add's capture, read the note: only lossless changes (the format rules) may have landed. Then measure timing: run `add` and compare the captured `zotero-item-version` with `client.item(key)["version"]` 15 s later; if the version moved, the lint landed after capture's read and the next capture raises monitor rows — record that as the known cost. If any value was guessed or lost, set the rule's row and comment on #197/#200.

- [ ] **Step 2: ZotMoov at its declared settings**

Install ZotMoov 1.2.32 with `file_behavior="copy"`, `enable_automove=false`. Add an item with a PDF attachment, wait 30 s, confirm the attachment is still an `imported_file` under Zotero's storage (`client.children(key)`) and no file moved. Record.

- [ ] **Step 3: `extensions.json` write timing while Zotero runs**

With Zotero running, note `extensions.json`'s mtime; disable and re-enable an add-on in the Add-ons window; read the mtime again at 1 s, 5 s and 30 s. If the file is rewritten within seconds, append the measured fact to assembly §9's 2026-10-24 amendment (`extensions.json` is saved within N s of a change while Zotero runs); if it is rewritten only on exit, say so there and in `skills/setup-vault/SKILL.md` (doctor's `plugins` row reads the state at Zotero's last exit).

- [ ] **Step 4: The Better BibTeX branch names**

On the test instance with one auto-export configured, read `prefs.js` and record the exact key the exports live under and the `git` opt-in key in `.git/config` (`auto-export.ts:180-254`); if either differs from `addons.BBT_AUTO_EXPORT` or `_bbt_git_probe`'s section name, change the constant and its test in the same commit.

- [ ] **Step 5: Commit the measured corrections**

```bash
git switch -c substrate-d/live-corrections
git commit -m "fix(doctor): the add-on declaration and probes corrected from the test-instance legs (Linter keys, ZotMoov, extensions.json timing, BBT branch)" -- research_vault/templates/zotero-addons.md README.md research_vault/addons.py research_vault/doctor.py docs/superpowers/specs/2026-09-05-assembly-design.md skills/setup-vault/SKILL.md tests/test_addons.py tests/test_doctor.py
git push -u origin substrate-d/live-corrections
```

(Only the files a leg changed.)

______________________________________________________________________

### Task 5: #172, the step map, the records, the review

**Files:**

- Modify: `docs/agents/sourcing.md` (the quotation rule; the first high-bar `build` record), the evidence record #172 names (its two fragments paraphrased), `docs/superpowers/specs/2026-09-05-assembly-design.md` (§5.0 step map; §15 items 09 and 13), `mutation-baseline.txt`

- [ ] **Step 1: #172 — the quotation rule and the record**

Read `gh issue view 172 --comments` for the file and the two fragments; paraphrase both in that file (keep the cite, drop the verbatim text). Append to `docs/agents/sourcing.md` after `## The build bar`'s rule paragraphs:

```markdown
## Quoting a source

A screen or a research record quotes at most one line from a body it cites, and only from a body whose licence is recorded at the pin it reads; an inline fragment from an unlicensed body — a gist with no licence file, a proprietary binary — is paraphrased and cited, never quoted (#172, 2026-10-24). The repository is public, and a record that carries another's text carries their terms.
```

and, under `## The build bar` after the `*Recorded 2026-09-17:*` line:

```markdown
*Recorded 2026-10-24:* the first `build` verdict at the high bar is the lanes 2–3 spec's §3.4 — a research-vault library module for identifier completion and registry checks (#140), mature-tool tier. Assembly decision 19 deferred the component register and its linter, so the `floor_failed` must (screen A's A3 part 1, `…-zotero-screen-evidence.md`) was checked by hand against every candidate named there; the register row is owed when lane 5 opens it.
```

- [ ] **Step 1b: The ingest spec's `:448` and three issue comments**

In `docs/superpowers/specs/2026-09-06-import-redesign-design.md`, the paragraph beginning “**Provisioning the enrichment plugins is part of setup, and carries two obligations.**” gains at its end: “*Amended 2026-10-24 (lanes 2–3 spec §6.1, #190, #191): the declaration is two tables — add-ons with need and minimum version, and declared preference values as `prefs.js` literals — and doctor compares each effective value (the `prefs.js` line, else the `.xpi`'s shipped default); the sentence that automatic mode must be switched on is withdrawn: the DOI Manager's and the PMCID fetcher's automatic modes are declared off (screen A rows 5 and 7).*”

```bash
gh issue comment 135 --body "Lanes 2-3 spec §3.2 (Plan D Task 1): Actions and Tags is declared optional with rules carrying no event triggers; a narrower variant — no script or triggerAction rule with an event or shown in the collection menu — carries this issue's right-click route. Its effects are observed by the capture monitor (ruling 5), not declared as literals."
gh issue comment 140 --body "Lanes 2-3 spec §3.4 records the build verdict (mature-tool tier, floor_failed screen A's A3 part 1): a research-vault library module for identifier completion and registry checks, as a CLI verb plus a skill, designed in its own spec after this one. Plan D Task 5 recorded it in docs/agents/sourcing.md as the first high-bar build."
gh issue comment 151 --body "Lanes 2-3 spec decision 21: URL-source acquisition (assembly §7.2.1) moves to its own spec with this issue as its home; nothing in Plans A-E touches it."
```

- [ ] **Step 2: The step map and §15**

Assembly §5.0's step list becomes “`vault-setup`, `capture`, `compile`, `search`, `scoping-review`, `long-form`, `daily-log`, `publish`, `analysis-reports`, `knowledge-management`” with the sentence “*Amended 2026-10-24 (lanes 2–3 spec, ruling 6): `analysis-reports` and `knowledge-management` join the map; the add-on declaration's workflows column names them.*” §15 item 09 gains “**Closed 2026-10-24: every one of the 23 installed add-ons, and 31 more, is dispositioned in the lanes 2–3 spec §3 and screen A §8.**”; item 13 gains “**The `prefs.js` half is answered by §9's 2026-10-24 amendment; `extensions.json` and the Obsidian half are measured by the lanes 2–3 plans D (Task 4) and E.**”

- [ ] **Step 3: Review, baseline, closes**

As Plan A Task 11. Verify `gh issue view 190 191 172 --json state`; close #172 after Step 1 lands: `gh issue close 172 --comment "Closed by Plan D Task 5: the two fragments are paraphrased; docs/agents/sourcing.md carries the quotation rule."`

```bash
mdformat docs/agents/sourcing.md docs/superpowers/specs/2026-09-05-assembly-design.md
git switch -c substrate-d/close
git commit -m "docs: the quotation rule and the first high-bar build recorded in sourcing.md (#172); the step map gains analysis-reports and knowledge-management" -- docs/agents/sourcing.md docs/superpowers/specs/2026-09-05-assembly-design.md docs/superpowers/specs/2026-10-03-substrate-components-design-section-1-research.md mutation-baseline.txt
git push -u origin substrate-d/close
```

(Replace the research-file path with the one #172 names.) Merge `--ff-only` when green. Plan E opens from this `main`.

______________________________________________________________________

## Coverage notes

- §3.1–§3.3 as the declaration: Task 1 (every row, need and setting); §3.4's record: Task 5.
- §6.1 (#190, #191, excluded add-ons, `bbt-git`, the `plugins` behaviour change): Tasks 1–2. §6.2's Better BibTeX auto-export row: Task 2 (the mode row is Plan E's; the deny-rules and PyYAML rows are Plans C and A's).
- §6.4 (component findings; the `prefs.js` amendment to assembly §9): Task 3; `extensions.json`'s timing: Task 4.
- §8's Zotero legs for Linter, ZotMoov and `extensions.json`: Task 4 (Attachment Scanner's and arXiv Workflow's legs ran in Plan B Task 10).
- §11: `README.md`'s tables (Task 1), `sourcing.md` (#172 and the build record, Task 5), assembly §5.0, §9, §15 items 09 and 13 (Tasks 3, 5), `setup-vault`'s declaration pointer (Task 1), `publish` and `capture-source` (Task 3).
- Deviations: four probe ids dual-listed as check ids; component reasons under `mismatch`; Actions and Tags declared without a settings row.
