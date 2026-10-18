# Declare, provision, observe: the Zotero and Obsidian components research-vault cannot pin, and how it sees what they do

Status: **the active spec** (2026-10-17), beside the open decomposition (`2026-09-05-assembly-design.md`). It carries lanes 2, 3a and 3b of the assembly spec's §7.3. It succeeds `2026-09-17-pre-lane-2-design.md`, whose plan closed on 2026-09-23 (milestone `pre-lane-2`, 19 of 19 issues closed); that spec's `:3` status line becomes an execution record in this spec's commits (§11).

**What this spec is.** One argument: assembly decision 12's three legs for the two component classes research-vault cannot pin — **declare, provision, observe** — where *observe* covers both a component's state (doctor) and its effects (machine-surface detection and the capture monitor). The operator's rulings exempt ordinary editing and commands on the person's selection only because research-vault sees every change to what it owns (§2, ruling 5), so the detection work and the declarations it licenses are one design. Plans are the plan writer's call; §9 gives the ordering that binds them.

**How to read.** Every `file:line` is at the HEAD of branch `lanes-2-3-spec`; `research_vault/` and `hooks/` there are byte-identical to `3780fb7` and to `origin/main` at `13035fb` (checked 2026-10-17). Evidence siblings carry the per-must results; this spec carries the verdicts:

- `2026-10-03-substrate-components-design-zotero-screen-evidence.md` — **screen A**, Zotero add-ons; "row N" means its §3 row.
- `2026-10-03-substrate-components-design-obsidian-screen-evidence.md` — **screen B**, seam-free Obsidian plugins.
- `2026-10-03-substrate-components-design-obsidian-zotero-screen-evidence.md` — **screen C**, Obsidian plugins that read Zotero.
- `2026-10-03-substrate-components-design-section-3-designs.md` — six reviewed designs for §5 and §6 ("designs").
- `2026-10-03-substrate-components-design-section-3-research.md` — the technical questions resolved against code, documentation and measurement ("research").

**What binds.** The decisions in §1; the rulings in §2; ADRs 0001–0003; the ingest spec's invariants as amended in §11; the measured environment, dated. A section that cites a design or research record adopts that record's corrected design for the item, including its acceptance tests, unless the section says otherwise.

______________________________________________________________________

## 1. Decisions

Rulings only; each section carries the argument. "Operator" marks a decision the operator made; the rest follow from the screens, the designs and the research.

01. **One spec** for lanes 2, 3a and 3b, themed declare, provision, observe (operator, 2026-10-04).
02. **Annotation handling stays with lane 4** (operator, 2026-10-04, #18). Assembly decision 28 stands; the ingest spec's `:137` claim to supersede it is amended (§11).
03. **Rulings 1–9** (§2) are the standards every component was judged by.
04. **Zotero add-ons:** Better BibTeX required; seven recommended; nineteen optional; the rest not declared (§3).
05. **A research-vault library module is a `build`** for identifier completion and for checking fields against the registry record, as a script plus a skill, designed in its own spec (operator, 2026-10-06; §3.4).
06. **The Obsidian seed** is a core-heavy `core-plugins.json` plus community plugins vendored only where their licence at the pin permits redistribution with no source obligation; copyleft and licence-unclear plugins are recommended with their `data.json` seeded (operator, 2026-10-17; §4).
07. **The seed lives at `templates/obsidian/`**, copied once by scaffold; an existing `.obsidian/` is left alone (§4.6).
08. **Obsidian's own trust prompt is the consent step** for community plugins; setup never calls `plugins:restrict on` (§4.7).
09. **`daily/` is the person's diary; `log/` is the machines' activity record**, its day files retyped from `daily` to `log` (operator, 2026-10-04; §4.4).
10. **Links are markdown links with a `/`-led vault path**, kept so by a fix-then-fail normaliser at commit (operator, 2026-10-04; §5.2).
11. **The commit hook never stages.** It runs one fixer on staged files and refuses the commit if the fixer changed any (§5.1).
12. **The capture monitor holds at commit and at publish;** publish re-checks every commit since the last publication (§5.3).
13. **Compiled `wiki/` pages:** a content edit refuses the commit until sealed or acknowledged; a link-only change from a rename reseals itself (operator, 2026-10-17, option C; §5.4).
14. **Merges become propagations** (#183): the loser's citation key maps to the survivor's through `propagate` (operator, 2026-10-17; §5.3.6).
15. **Zotero tags split into `zotero-tags` and a slugged `tags`; field names fold to Zotero's base names** (operator, 2026-10-17; §5.3.4).
16. **Agent shell writes are detected, not prevented.** The seed carries Claude Code `Edit(...)` deny rules for the roster as a speed bump; acknowledgements are not restricted to the person's terminal (operator, 2026-10-17; §5.7).
17. **Component problems close publish:** doctor's cold checks run at capture and file per-component findings, including excluded add-ons found active (operator, 2026-10-17; §6).
18. **The component register opens at lane 5** (operator, 2026-10-17).
19. **PyYAML becomes a runtime dependency** for reading OKF frontmatter, failing closed when absent (#194; §5.6).
20. **#172 is carried here:** the rule against quoting unlicensed sources moves into `docs/agents/sourcing.md` (operator, 2026-10-17; §11).
21. **Moved elsewhere:** URL-source acquisition to its own spec (#151); whether a clean Retraction Watch lookup by PMID counts as verification, to #185 (operator, 2026-10-17).

______________________________________________________________________

## 2. Rulings

Recorded in each evidence file's "Standards as applied" section, in the order the operator gave them (2026-10-03 to 2026-10-17).

1. **Machine surfaces are the guard's roster** (`hooks/pretooluse_guard.py:11-23`): `literature/`, `log/`, `wiki/`, `fulltext/`, `system/propagations/`, root `log.md`, `inbox/review-queue.md` and `system/bibliography.json`. The rest of `system/` is hand-edited. `README.md:7`'s wholesale "`system/`" is drift (#192).
2. **Merging duplicates is Zotero's own behaviour**, not judged in an add-on. This spec solves #183 instead (§5.3.6).
3. **Approval gates and unmonitored backups count for nothing.** A confirm dialog, a preview, a backup line or a history nobody watches does not make a write safe.
4. **Values must be right by construction.** A written value comes from an authoritative source looked up by identifier, or is a format change that keeps the information. A removal is allowed only by a definite test: an exact placeholder, a nonexistent file, an exact duplicate kept on the item. A re-key passes, because lifecycle detects it and `propagate` repairs it.
5. **A component is judged on what it adds beyond ordinary editing.** For Obsidian, beyond editing the open note; for Zotero, beyond commands the person runs on the items they selected. Counted paths are automatic, on-add, on-create, scheduled, bulk, remote, or writes to other notes or files. Obsidian's own vault operations — a rename with its link update, a move, a delete, creating a note by following a link or from a menu, File recovery's restore — are app behaviour. A direct edit to one specific note shown in another view (a Bases cell, a checkbox in a query result) is editing that note. A handler that only inserts into the open note is open-note editing. An item a command creates from the person's selection is part of that command. A tag written because an item's citation key exactly matches a key in a vault note is a value by identifier. This ruling holds only because research-vault detects machine-surface changes whoever makes them (§5).
6. **Include anything that aids one of the five workflows and does no harm.** The workflows: research; analysis and reports; personal knowledge management; long-form writing; daily logs. The step map (assembly §5.0) gains `analysis-reports` and `knowledge-management`. Harm is an unconfined counted path under ruling 5, a load failure, or a destructive write. Two add-ons whose writes fight each other are not both declared.
7. **An OKF conformance break is accepted where the value justifies it**, as a row in the deviation register together with the verify exemption or type mapping that keeps the commit gate open for that plugin's files.
8. **A redistribution licence decides only how an Obsidian plugin is declared:** seeded (vendored) or recommended (the person installs it). It is not harm.
9. **Agent access to Zotero is research-vault's own client** (`research_vault/zotero.py`); an add-on whose job is agent access is not declared.

______________________________________________________________________

## 3. Zotero add-ons

**Declare:** the README add-on tables, packaged as `research_vault/templates/zotero-addons.md`, which doctor reads (§6.1 gives the new shape). **Provision:** the person installs, in the setup wizard. **Observe:** doctor and the capture-time component check (§6).

### 3.1 Required and recommended

| Add-on                   | Need        | Job                                            | Declared settings                                                                                                                                                | Notes                                                                                                                                                                                                                                  |
| ------------------------ | ----------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Better BibTeX            | required    | citation keys                                  | no auto-export may target `system/bibliography.json` or a machine folder                                                                                         | One failing path, named: the File-menu AUX scan strips its tag from uncited items library-wide (row 1). No alternative mints keys.                                                                                                     |
| PMCID fetcher            | recommended | PMID, PMCID                                    | `extensions.zotero.pmcid.auto=false`, `extensions.zotero.pmcid.tags=false`                                                                                       | Automatic mode writes Extra back from a stale snapshot; its tag fetch sends a PMCID as a PMID (row 5; #213). Leaves the table when the library module ships (§3.4).                                                                    |
| DOI Manager 2.2.0        | recommended | DOI validation and cleaning                    | `extensions.shortdoi.autoretrieve=none`, `extensions.shortdoi.monthly_verify=false`, in `prefs.js` before install; minimum version 2.2.0                         | Every menu command first fills an empty DOI from a Crossref metadata guess (rows 6–7; #217). Replaces 1.6.0, which Zotero 10 disables (#191). Leaves the table when the library module ships.                                          |
| Meta Refresh             | recommended | fields from the registry record, by identifier | `titleSimilarityThreshold="2"`, `useS2=false`, `useOpenAlex=false`, `fieldConferenceName=false`, `backupToExtra=false` (prefix `extensions.zotero.metarefresh.`) | The threshold must be seeded: the preferences pane clamps a typed value to 0–1 (row 12). Restore still acts on backup lines written before the setting. Becomes optional when the library module ships.                                |
| Linter for Zotero        | recommended | consistency on add; duplicate report           | `lint.onAdded=true`; `rule.require-language=false`; every guessing or destructive rule `false` by its `rule.<id>` key                                            | The key set is verified live in the plan (§8). Per-rule menus run a rule whatever its key says (row 9; #197, #200).                                                                                                                    |
| Zotero Duplicate Cleaner | recommended | duplicate resolution                           | —                                                                                                                                                                | Acts only on groups the person ticks (row 46). A merge is followed by `propagate` (§5.3.6).                                                                                                                                            |
| Attachment Scanner       | recommended | attachment integrity                           | `monitor_attachments=true`, `scan_duplicates=false`                                                                                                              | Its trash options fire on any modify, removing only snapshots beside a PDF or EPUB and PubMed links; that is safe only once #189 makes a dropped child a finding (§5.3.5). `scan_duplicates` would tag RapidOCR's twin (row 26; #216). |
| RapidOCR for Zotero      | recommended | OCR of scanned PDFs                            | —                                                                                                                                                                | Chinese-primary model: ASCII letters, no accented letters; fits an English library. Non-English OCR is a recorded gap (rows 30, 32). Production holds 19 scanned PDFs, 407 pages, all English (research).                              |

**The DOI chain.** A DOI Manager command can fill a wrong DOI, and Meta Refresh then applies that record's metadata by identifier. No setting removes the guess. The capture monitor reports both changes, with old and new values, and holds publish until they are acknowledged (§5.3). The library module removes the guess (§3.4).

### 3.2 Optional

Declared with their settings and observed by doctor; installing them is the person's choice.

| Add-on                        | Workflows                                 | Declared settings (row)                                                                                                                                                                                                  |
| ----------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| MarkDB-Connect                | knowledge management                      | `mdbc.removetags=addonly`, plus its source-folder and key settings (row 36; ruling 5's citation-key reading)                                                                                                             |
| arXiv Workflow                | research                                  | `merge.arXivExtra=true`, `features.arXivUpdate=false`, `merge.trashUnannotatedPDF=false` (row 4); recommended once its merge has run on the test instance and `propagate` followed the re-key; the repair route for #187 |
| scite                         | research                                  | — (row 18)                                                                                                                                                                                                               |
| PubPeer                       | research, long-form                       | — (row 48)                                                                                                                                                                                                               |
| Citation counts (tangzhao20)  | research                                  | `autoretrieve=none` (row 21)                                                                                                                                                                                             |
| open-citations                | research                                  | `writeExtra=false` (row 22)                                                                                                                                                                                              |
| Google Scholar citation count | research                                  | `useAutoCountUpdate=false` (row 23)                                                                                                                                                                                      |
| ZotSeek                       | knowledge management, research            | `zotseek.mcpServer.enabled=false` (row 52)                                                                                                                                                                               |
| Better Notes                  | research, knowledge management, long-form | tag sync and auto-sync off (row 37)                                                                                                                                                                                      |
| Zutilo                        | knowledge management, long-form           | — (row 3)                                                                                                                                                                                                                |
| Open PDF                      | research, knowledge management            | — (row 28)                                                                                                                                                                                                               |
| KeepZotero                    | research                                  | — (row 40)                                                                                                                                                                                                               |
| Zotero Focused Mode           | research                                  | — (row 41)                                                                                                                                                                                                               |
| Actions and Tags              | knowledge management                      | rules with no event triggers (row 38); a narrower variant carries #135's route                                                                                                                                           |
| ZotMoov                       | knowledge management                      | copy mode, `enable_automove=false` (row 27)                                                                                                                                                                              |
| zotxt                         | long-form                                 | — (row 49)                                                                                                                                                                                                               |
| zotero-docling                | research, analysis and reports            | `autoConvert=false`; needs a server the person hosts (row 33)                                                                                                                                                            |
| MinerU for Zotero             | analysis and reports, long-form, research | `apiEnabled=false` (row 35)                                                                                                                                                                                              |
| Reading Time                  | knowledge management                      | its load check first (row 53)                                                                                                                                                                                            |

### 3.3 Not declared

Screen A §8 classifies every row. The grounds:

- **Agent access** (ruling 9): Zotero MCP.
- **Harm with no confining setting:** Zoplicate (its bulk-merge pre-fill from siblings), ZotMeta (identifiers taken from PDF text, #214; its writes fight the PMCID fetcher's), Zotero OCR (writes beside a linked PDF with no existence check, #215), DOI Fix, Zotero Reading List, and the other harm rows.
- **Fighting another writer:** citation-count add-ons that strip each other's Extra lines.
- **Not loadable on Zotero 10.0.5:** DOI Manager 1.6.0 and the load-failure rows.

### 3.4 Build verdict: a research-vault library module

**Verdict `build`, mature-tool tier** (`docs/agents/sourcing.md`, the high bar). Home #140; designed in its own spec after this one (§10).

**Jobs.** (1) Identifier completion and verification: DOI, PMID and PMCID, looked up only by identifier from an authoritative source and written to Zotero's native fields. (2) Checking pages, issue, volume, date, venue and creators against the registry record for the item's identifier. Both run as an audit over the whole library that reports a worklist with item keys, with an optional repair of what the audit found.

**`floor_failed`: screen A's A3 part (1)** — every value written comes from an authoritative source looked up by identifier, or is a lossless format change. No candidate meets it for these jobs in every path it offers:

- **DOI Manager 2.2.0:** every menu command first fills an empty DOI from a Crossref metadata query, and no setting removes it (rows 6–7; #217).
- **DOI Fix:** Retrieve takes a single OpenURL hit unchecked; Update validates against Crossref only and replaces a valid DataCite DOI with a title match (row 8).
- **PMCID fetcher:** writes Extra back from a stale snapshot, losing concurrent edits; its tag fetch attached unrelated MeSH headings to two production items (row 5; #213).
- **Linter for Zotero:** `require-doi` fills from an unchecked Crossref match; its extra-zeros helper shifted six production page ranges and one issue range (row 9; #197, #200).
- **ZotMeta:** takes a DOI or arXiv ID from the first matching string in the PDF's text and overwrites title and creators from it (row 11; #214).
- **For job (2), no candidate reports a field that disagrees with the registry record.** Meta Refresh corrects from the record but files nothing, and passes A3 only with five non-default keys (row 12).

**Form: a script plus a skill** (operator, 2026-10-06). A CLI verb in `research_vault` performs every Zotero write — the README's rule that the agent composes and explains while the CLI writes — reusing `research_vault/zotero.py`, the capture ledger, findings and acknowledgement, and the repository's tests and mutation gate. A skill on top carries the judgement rules cannot, such as whether a borderline registry record is the same work. The local API applies every PATCH with `fromJSON(json, {strict: false})` (Zotero 10.0.5 `server_localAPI.js:1983`, read 2026-10-06), re-running Zotero's normalisation over the record, so every write runs a pre-flight that computes what that normalisation would change and refuses or plans around it. The module's spec opens by measuring that round trip on the test instance against a sample of real items.

**Rejected form: research-vault's own Zotero plugin.** Writing in-process (`item.setField`, `saveTx`) would avoid the PATCH normalisation and live in Zotero's UI. Against it: a second codebase in a second language outside pytest, the mutation gate and CI, testable only against a running Zotero; an `.xpi` to ship with version caps, an update channel and a human install step; the common scaffolding (zotero-plugin-toolkit) carries the unprompted-install route (#199); and agents could drive it only through an endpoint, a remote write route that ruling 5 counts against it.

**Transition.** Until the module ships, §3.1's DOI Manager, PMCID fetcher and Meta Refresh rows stand. When it ships, the first two leave the table and Meta Refresh becomes optional; the README tables and doctor's rows change in the same commit.

______________________________________________________________________

## 4. The seeded `.obsidian/`

**Declare and provision:** the seed tree, copied into a new vault by scaffold. **Observe:** doctor's `obsidian` check (§6.3) and §5's detection.

### 4.1 Core plugins (`core-plugins.json`)

Written in object form with every registered id present, so Obsidian does not rewrite the file on first open (screen B §7.4).

- **On:** Files, Search, Quick switcher, Backlinks, Outgoing links, Tags view, Bookmarks, Page preview, Outline, Command palette, Word count, Editor status, Footnotes view, Graph view, File recovery, Templates, Daily notes, Workspaces, Slash commands, Audio recorder, Random note, Slides, Bases, Note composer, Unique note creator, Web viewer.
- **Off:** Properties view (it passes only if every machine folder is hidden from Search, Graph and Tags), Canvas, Sync, Publish, Format converter.
- **Settings files:** `daily-notes.json` (folder `daily`, format `YYYY-MM-DD`, template `system/templates/daily`); `templates.json` (folder `system/templates`); `zk-prefixer.json` and `webviewer.json`, routed so their new notes land outside machine folders.
- Bases is kept: the template ships `.base` views; its counted path is a create through Obsidian's CLI, off unless the person enables the CLI; its OKF fail falls under ruling 7. Sync is off but, if the person enables it, merges `"sync": true` back into the file from another device; doctor reports that as drift (§6.3).

### 4.2 Community plugins

**Seeded (vendored)** where the plugin's licence at its pin, bundled components included, permits redistribution with no source obligation. Expected: Dataview, Calendar, Periodic Notes, Homepage, Outliner, Callout Manager, Iconize, Footnote Shortcut, Better Word Count, Novel word count, Hider, Auto Note Mover and Tasks; Kanban and TaskNotes once #194 lands, if their licence check passes. Settings per screen B §9.

**Recommended, with `data.json` seeded,** where the licence carries a source obligation (GPL, AGPL, MPL, for the plugin or a bundled component) or is not established. Expected: Omnisearch, Advanced Tables, Editing Toolbar and Focus Mode; Templater and QuickAdd, whose remote routes must stay off, which the seed cannot lock; Pandoc Plugin and Typewriter Scroll (licence). A seeded `data.json` survives a later community install and update; a plugin folder holding only `data.json` loads nothing and raises no prompt; recommended ids stay out of `community-plugins.json` (research Q10).

**The vendoring script decides, not these lists.** `scripts/vendor_obsidian_plugin.py` (to be created) records each plugin's licence at its pin, bundled components included, in `SOURCE.json`. A plugin whose licence carries a source obligation, or is not established, is written as recommended: its settings only. The lists above are the expected outcome, not an override (designs, cluster 6(b)).

**Excluded:** Canvas, Sync, Publish, Format converter, Git, Longform (remote routes), Advanced URI, Tag Wrangler, Note Refactor, Excalidraw, Quadro, Local REST API, the agent hosts (Claudian, Copilot, Agent Client), Remotely Save, Importer, Enhancing Export and the theme-only plugins (screen B §9).

### 4.3 Obsidian plugins that read Zotero (screen C §8)

None writes a literature note or a machine folder (C1). **Seeded:** Citations, Zotero Cite Links, Zotero Annotation Citations. **Recommended with settings seeded:** Citation Suite, Better Pandoc Reference List and Reference Map (copyleft); Simple Citations and Zotero Lib View (they need an export folder or a Better BibTeX auto-export the person sets up); Zotero Deep Linker until the vendoring script establishes its licence (its copyright holder is a placeholder). **Excluded:** ZotLit, Zotero Integration, Citation Extended, Citation Links, and Deep Sit until production Better BibTeX is 9.0.65 or later.

Before any of these ships, the plan runs a load check and a key-resolution check for each (§8). Reference Map, Zotero Annotation Citations and Zotero Deep Linker never loaded in the live run; key resolution against capture's bibliography file was never measured for Citations, Zotero Cite Links, Simple Citations and Zotero Lib View; Zotero Deep Linker's Better BibTeX route failed on 9.0.63. A plugin that fails drops out.

### 4.4 `daily/` and `log/`

- **`daily/`** is the person's diary. Core Daily notes writes it, OKF type `daily`; the type map derives the type from the top folder at any depth, so weekly and monthly notes under `daily/` are typed `daily`. Scaffold seeds `daily/.gitkeep` through `_EMPTY_ROOTS`, not `VAULT_DIRS`, so deleting an unused diary folder never blocks a commit. `daily/` is not a machine surface. `daily` is the most common Daily-notes folder among 403 public vaults measured on 2026-10-04 (19%; "Daily Notes" 12%).
- **`log/`** stays the machines' activity record; its only writer is publish (`research_vault/publish.py:416-430`). Its day files are retyped from `daily` to `log`, matching root `log.md`. `system/templates/daily.md` becomes the diary template and drops its `log/` comment; `log/` needs no template. There are no existing vaults, so no migration is owed (operator, 2026-10-17).
- Designs, cluster 3(a), carries the file list and tests.

### 4.5 `app.json` and the formatter lists

- `useMarkdownLinks=true` and `newLinkFormat="absolute"`: Obsidian writes vault-absolute paths without the leading `/`; the normaliser adds it (§5.2).
- `newFileLocation="folder"`, `newFileFolderPath="inbox"`: new notes land in `inbox/` as fleeting notes, never in a machine folder.
- `attachmentFolderPath="inbox"`: pasted attachments land outside `wiki/`, so they do not drift compiled pages.
- `alwaysUpdateLinks=true`: Obsidian runs the link update on rename either way (screen B §7.52); the prompt is an approval gate.
- `literature/` stays out of `userIgnoreFilters`.
- The seed's `prettierignore` and `markdownlintignore` gain `/wiki/`, `/log.md` and `/system/compiled-pages.json`, removing two formatter writers (designs, cluster 2(a)).

### 4.6 Packaging and scaffold

- The seed is stored at **`templates/obsidian/`**, outside `templates/vault/`, so doctor's repair, which re-runs scaffold, never reinstalls a plugin the person removed. Scaffold copies it as one unit, and only when asked (`with_obsidian=True`); doctor's call leaves it off (research Q11).
- Python's `glob`, which setuptools uses for package data, skips dot entries at any depth. A hermetic test asserts that `glob("templates/**/*", recursive=True)` equals the `rglob` file set and that no template path has a component starting with a dot.
- Scaffold copies the tree into a sibling temporary directory and renames it into place, so a concurrently created `.obsidian/` makes the rename fail instead of leaving half a seed. The unit is one candidate and one created path, so the git cost no longer grows with the plugin count (designs, cluster 6(c)).
- **An existing `.obsidian/` is left alone.** Scaffold prints a line naming the skipped seed and the fix: close Obsidian, move `.obsidian/` aside, re-run scaffold. setup-vault runs scaffold before the compile tool's adopt step, which writes `.obsidian/` files when they are missing (`transaction.py:111-114` @ `32ac5a0`).
- Each vendored plugin folder holds the release assets byte for byte plus `LICENSE`, `THIRD-PARTY-NOTICES` and `SOURCE.json` (`{repo, tag, commit, assets, licence, source, measured, method}`). An Obsidian update rewrites `main.js`, so byte hashes drift after install by design; doctor compares the pinned tag with the installed `manifest.json` version instead (§6.3).
- `.claude/settings.json` (the deny rules of §5.7) ships as `templates/vault/claude/settings.json` under the same first-component rename.

### 4.7 Restricted mode

Obsidian 1.13.7 shows "Do you trust the author of this vault?" on every load of a vault whose `.obsidian/plugins/` holds a loadable manifest, until the person clicks **Trust author and enable plugins**, which enables exactly the ids in `community-plugins.json`. The decision is kept per vault registration, outside the vault, so a freshly scaffolded vault always prompts (measured 2026-10-06 on the scratch vault; read in `app.js`). Setup tells the person to expect the prompt and verifies afterwards with `eval Object.keys(app.plugins.plugins)` and `dev:errors` — not `plugins:enabled`, which lists configured ids whether or not they loaded. Setup never calls `plugins:restrict on` or `setEnable(false)`: either silences the prompt for that vault permanently.

______________________________________________________________________

## 5. Observe: detection and the capture monitor

Ruling 5 rests on this section. Designs clusters 1–4 and the research carry the mechanisms, costs and acceptance tests; this section states what is adopted.

### 5.1 The commit hook (#203)

- The hook never stages: `pre-commit:24-27` (stamp, then `git add`) is deleted.
- One fixer, `stamp-type --paths`, also normalises links (§5.2) and regenerates root `log.md`. Writers call it on their own paths.
- The hook runs the fixer on staged files whose worktree copy equals the staged blob, then runs verify. If the fixer changed any file, the hook exits 1 naming the files to re-stage. Re-running the same commit passes; under `git commit -- <paths>` no re-staging is needed. A partially staged file is reported, not rewritten (research Q1, measured).
- The whole-vault type sweeps in `capture` and `mark-withdrawn`, and capture's `regenerate_log`, are dropped (designs, cluster 3(b), option (i)). This closes #178 item 3 and #174's exit-2 leg.

### 5.2 Links: markdown with a `/`-led path

- `research_vault/links.py` (to be created) parses, resolves and renders both link forms, following Obsidian's `getLinkpathDest`: case-insensitive; a dotless name resolves only as `<name>.md`; `literature/` resolves only through the captured set. It replaces `captured._WIKILINK` and `_page_names`. **`captured.py` switches to it first**, before any other link change, or the commit gate silently stops checking link targets.
- Rendering follows Obsidian's `generateMarkdownLink`: `[[x]]` becomes `[basename](/path/x.md)`, subpaths carried, spaces encoded.
- **The normaliser** rewrites every `[[…]]` it can resolve and adds the `/` to a markdown destination that resolves to one file. It leaves URIs, `./`, `../`, ambiguous and dead targets alone and files them as "resolve by hand" rows (dead ones under `dead-link`, §5.4), so commits cannot loop. It masks code fences, inline code and comments; skips anchored claim blocks whole and masks `[k:: …]` spans elsewhere (research Q19); refuses a rewrite that leaves frontmatter unparseable; and skips `literature/`, `log/`, root `log.md`, `inbox/review-queue.md`, `system/propagations/` and `wiki/` (compiled pages are normalised at seal, §5.4).
- Callers change in order: `captured._textual`; `propagate`, through the resolver rather than a regex; `literature_notes.py:425,440`; the seed `index.md`; `okf.py:32` (to `/log/…`); the skills' link instructions (`capture-source`, `synthesis-conventions`, `evidence-conventions`, `setup-vault`).
- The OKF register's claim-link row stays, its reason corrected: the constraint is the vault's three frozen claim readers (`claims.py:12`, `lints.py:24` and the claim-immutability byte comparison), not Dataview.

### 5.3 The capture monitor and `literature/`

#### 5.3.1 The monitor

A new verify check, **`capture-monitor`**, sits beside `_frontmatter_attestation_outcomes` (`lints.py:698-724`) inside `lint_evidence_layer`'s pair loops. For every literature note an attested writer changed — capture, a compile refresh, `propagate`, a restore — it reports every snapshot field added, changed or removed; every attachment that left the tuple or changed `md5` under the same key; and a changed `zotero-server-id` or `zotero-item-key` at the same path. Unattested changes keep their existing `evidence-layer` rows.

- **Hold set:** every snapshot field except the tag fields (`zotero-tags` and `tags`), plus the attachment and identity rows; Extra is held whole. Tag-only changes are filed as one non-blocking summary row per capture run, naming the notes.
- **Reasons are built, not copied.** Each value is encoded with `json.dumps(ensure_ascii=True)` and capped, because `append_entry` refuses line breaks; the full values stay in `git diff`.
- **Ack scope:** the repo-path hash over the note's normalised bytes, so any later byte change lapses the acknowledgement (designs, cluster 1).
- **Holds at commit and at publish.** Publish re-checks every commit since the last publication with `--diff-merges=combined`, so a `--no-verify` commit, or a hook that could not import `research_vault`, is still caught (0.98 s for 304 commits, measured). Publish creates annotated tags, which `push.followTags` pushes, so a fresh clone does not re-check the whole history. CI re-checks each commit in `rev-list HEAD --not $BASE` (research Q2).

#### 5.3.2 #205: an older render restored

It lands with the monitor, as its own predicate with the reason `drift — older render restored: version N < M`, comparing `zotero-item-version` with the ledger. The `generated.at` tie-break needs the clock (designs, cluster 1).

#### 5.3.3 #206: the verified lists

`verified` events are append-only. A failure row may be added or change its `result`; it may be removed only when the same diff appends an event for that check. These rows hash on the lists themselves, not the note's bytes.

#### 5.3.4 Snapshot fields (#185, #188, #195)

- **#185:** the snapshot carries Zotero 10's native `PMID` and `PMCID`, and `events.py` reads the native field.
- **#188:** type-specific fields (`proceedingsTitle`, `bookTitle`, `websiteTitle`, `blogTitle`, `repository`, `company` and the rest) fold to Zotero's base field names through Zotero's own schema mapping (`/api/schema`), so a change of item type is not read as a removed field. If the schema read fails, capture refuses rather than snapshot unfolded names. The ingest spec's "no field is renamed" sentence is amended: the names and the mapping stay Zotero's (§11).
- **#195:** `zotero-tags` holds Zotero's tag list exactly (today's `tags`, renamed). `tags` carries a slugged copy Obsidian can read: every entry, both tag types; punctuation Obsidian rejects becomes `-`; `/` is kept, so it nests; duplicates are removed ignoring case; empty and all-digit results are dropped; no `zotero/` prefix. Obsidian's character class is copied literally, not approximated with Python's `\s` and `\d`. Both keys join `CAPTURE_FIELDS`.

#### 5.3.5 #189: a trashed attachment

`lifecycle.py:86-91` is deleted. A trashed attachment is drift the monitor reports, not a refusal of the whole note.

#### 5.3.6 #183: merges

A merge becomes a propagation. Lifecycle's `merged` classification yields the successor's item key from `dc:replaces`, and `propagate` plans the loser's citation key → the survivor's under its existing plan, sha256-approval and residue machinery. The merged-away note leaves the captured set, so its bibliography entry does not fall out of the library route and get refused by the item-export fallback (`capture.py:301`). If the survivor has no literature note, the plan renames the loser's note to the survivor's key, exactly as a re-key does, and the next capture re-renders it from the survivor. If the survivor already has one, the plan deletes the loser's note: it is wholly machine-written, and the merge moved the loser's Zotero child notes onto the survivor, so nothing person-written is lost. Verified events and acknowledgments keyed on the old address are #146's question and stay there.

#### 5.3.7 #196: the bibliography and its notes

A bibliography entry changes only when its note re-renders. Capture regenerates `system/bibliography.json` entries for the items it rendered, and each note carries a `csl-sha256` of its entry, which verify compares exactly (research Q20).

### 5.4 Compiled `wiki/` pages (#212, #208)

- A tracked record, **`system/compiled-pages.json`**, holds the hash of every file under `wiki/`: pages, `.base`, `.canvas` and attachments. A new check, **`compiled-layer`**, compares each file's bytes with its entry.
- **Custody rule:** an entry may change only when the file's current bytes equal the entry, or equal the *latest* complete compile-journal write for that exact path. Seal moves an entry from journal to record, normalises the page's links and records the new hash. Callers: `capture` after compile, setup-vault's adopt step, `propagate.apply`, and a new `seal` verb — not the commit hook.
- **A content edit refuses the commit** until it is sealed or acknowledged (operator, option C). **A change that consists only of link targets now resolving to a renamed file reseals itself:** a definite test through §5.2's resolver.
- **Sealing also updates the compile tool's recorded `content_sha256`.** The tool refuses to recompile a page whose bytes no longer match it (`compile.py:283-286`), so an unsealed edit would otherwise surface weeks later as a compile refusal.
- A fresh compile before seal matches the latest journal locally and files no row; CI reads only the record.
- **#208:** embeds resolve against every file. An unresolved markdown destination, or a wikilink target containing `/` or ending in an attachment extension, reports the new reason code `dead-link` under its own check, so acknowledging a dead embed cannot hide a missing citation on the same page.
- Whether a Bases column resize writes the `.base` file is a live check (§8). If it does, a resize costs an acknowledgement, which is accepted.

### 5.5 `fulltext/`, non-`.md` files, `log/` and reserved names

- **`text-layer` (#207):** each text file carries `managed-sha256`, the hash of the render without that line, and `zotero-attachment-key` must equal the file stem. Edits hold **publish**; the folder is gitignored, so the check runs at publish, at the Stop gate and in plain verify. Rows carry no note path, claim id or line number, so verify never writes a marker into the file. A deleted text file gives no row, since a fresh clone lacks every text.
- **`type: fulltext` is reserved** for `fulltext/`, tested before `inbox/`'s early return, so a moved text file is refused at commit (`CONTEXT.md` amended).
- **#211:** any file in `literature/` other than `<key>.md` and `.gitkeep` is a `tree` row, and so is any path under `fulltext/` in a committed candidate (a force-added text).
- **OS litter** (`.DS_Store`, AppleDouble `._*`, `desktop.ini`) joins #194's walker predicate and the seeded gitignore.
- **#204:** `regenerate_log` renders only stems that are real dates and copies only lines in the writer's format; strays get findings under their own paths. The date check moves to `structure.py`.
- **#209:** one `structure.is_reserved` check. An empty nested `index.md` or `log.md` is valid (OKF §8, §9). One body-shape rule covers every folder; until #212's record lands, other reserved names under `wiki/` are refused by name. The tool's `wiki/log.md` and `wiki/canvases/index.md` get OKF register rows (ruling 7).
- **#210:** root `log.md` must equal its render byte for byte; a missing one passes; the fixer repairs it (§5.1).
- **#174** reports an unwritable file and continues; **#170**'s four `write_text` sites gain `encoding` (one tested under an ASCII locale, the others by an AST test).

### 5.6 Frontmatter and dot-directories (#194)

- One predicate excludes every dot-directory, and OS litter, from every walker; `verify.py:745-748`, `lints.py:503`, `publish.py:135`, `markers.py:180` and `stamp.py:52` switch to it.
- **`read_okf`**, beside the flat capture parser, reads OKF frontmatter with PyYAML (`CSafeLoader`, falling back to `SafeLoader`) and OKF's reference loader's resolver table (timestamp resolver removed); a duplicate-key constructor that checks hashability first; `parse`'s delimiter regexes; rejection of a non-mapping block; and OKF's `not value` test for rule 2. `structure.py:151`'s `sorted()` takes `key=str`.
- **It fails closed:** a missing PyYAML returns a distinct exit code the hook refuses, and doctor reports it.
- `read_okf` also runs at seal, so a compile-tool page with an unquoted `title: A: B` fails inside the session that can redo it. Stamp replaces a null `type:` line rather than adding a second.

### 5.7 Agent shell writes (#193)

- **Detection is the boundary.** The guard stays as it is; `tests/test_hooks.py:812-820` pins its silence on Bash.
- **The seed carries eight `Edit(...)` deny rules** for the roster in `.claude/settings.json`. Measured with Claude Code 2.1.273: they refuse redirects, `tee`, `sed -i`, `cp`, `mv`, `touch`, `rm` and `rm -r`; `python3 -c`, `perl -i`, `truncate`, `find -delete`, `git checkout` and `script` wrappers still write. A plugin cannot ship these rules, so they live in the vault, and doctor compares them with the guard's roster (§6.2).
- **Acknowledgements are not restricted to the person's terminal** (operator, 2026-10-17). Any process running as the person can write an `ack`, so "holds until acknowledged" is as strong as the process that acknowledges.
- The vault guide (`templates/vault/AGENTS.md:28`), `README.md:7` and `skills/synthesis-conventions/SKILL.md:12` state the coverage exactly: common shell forms are refused in sessions started at the vault root; interpreters, scripts and git restores are caught only where §5's detection covers them.

______________________________________________________________________

## 6. Doctor and the capture-time component check

### 6.1 The add-on declaration (#190, #191)

- When `prefs.js` lacks a key, doctor reads the shipped default from the add-on's `.xpi` (`prefs.js`, then `defaults/preferences/*.js`; stdlib `zipfile`). Better BibTeX's relative keys resolve through a key-prefix cell. A line naming the key that the grammar cannot read is UNREACHABLE, never `unset`.
- The declaration becomes two tables in `templates/zotero-addons.md`, embedded whole in the README: **add-ons** (name, id, need — required, recommended, optional or excluded — minimum version, key prefix) and **declared settings** (add-on, preference, accepted literals or `unset`, any of several). Every `|` line under either header must parse, or loading the declaration raises. This replaces `auto_pref` (`addons.py:9-22`, `doctor.py:275-280`).
- **#191:** a minimum version per row (DOI Manager 2.2.0), compared by each segment's leading integer with no new dependency. An `appDisabled` add-on that §3 recommends is reported by a new warn-only check, **`advisory`**.
- **Excluded add-ons:** every add-on §3.3 excludes on harm grounds is listed with need `excluded`, and one found active is reported. Only DOI Manager 1.6.0 (whose id the 2.2.0 floor owns), load-failure-only rows and Zotero MCP are omitted.
- Better BibTeX's `git` preference stays out of the settings table and in `bbt-git`, which passes `off`, or `config` only when the vault's `.git/config` holds no Better BibTeX opt-in.
- **Behaviour change:** `plugins` fails when an active add-on's effective value is not accepted. Production fails until §3's values are set (§10).

### 6.2 Doctor rows

- **#161:** the compile tool's mode joins `compile-tool`; an absent `.vault-meta/mode.json` reads as generic. The seeded `.base` files are YAML-parsed by a repository test and opened in Obsidian by the live leg.
- **Better BibTeX auto-export:** `plugins` fails when an export targets `system/bibliography.json` or a machine folder of this vault (Windows paths through `paths.to_local`).
- **Deny rules:** a row compares the vault's `.claude/settings.json` deny list with the guard's roster.
- **PyYAML:** a row reports it missing (§5.6).

### 6.3 The `obsidian` check

A new hard check reads, cold, the configured Obsidian folder (`obsidian_config_dir` in `machine.json`, default `.obsidian`): `community-plugins.json`; `core-plugins.json`; each plugin's `manifest.json` version against its `SOURCE.json` tag, a pinned-versus-installed note rather than a hash; and the declared keys in `data.json` and `app.json`. A declared key off its values on an enabled plugin is UNMATCHED; an unparseable config file is UNREACHABLE, because Obsidian rewrites these files non-atomically; drift from the seed is a note in the MATCHED reason; an absent folder is SKIPPED. The seeded and recommended plugins share one packaged declaration, embedded in the README.

### 6.4 Component findings at capture, closing publish

Capture runs doctor's cold rows — those with no network and no repair, including `bbt-git` and `fulltext-sync` — and files each failing component as a finding. The hash covers only the failing facts (keys off their values, active or `appDisabled`, below the floor), never the version, so an auto-update re-fires nothing. Verify treats open component findings as publish-closing, and verify and capture share one `inbox` function for their acknowledged and open-row skips. Assembly §9's cold-read rule gains a dated amendment for `prefs.js`: Zotero 10.0.5 (Gecko ESR 140) saves it 500 ms after any change, off the main thread, so a read while Zotero runs is current (research Q13). `extensions.json`'s write timing is measured before the amendment covers it (§8).

______________________________________________________________________

## 7. New names

Check ids `capture-monitor`, `compiled-layer`, `dead-link`, `text-layer` (pipeline-only, as `append-only` is), `advisory` and `obsidian`; the reason code `dead-link`; the steps `analysis-reports` and `knowledge-management`; the verb `seal`. Each joins `CHECK_IDS` or `REASON_CODES` and `docs/agents/terminology.md` §4.4, with the pins designs cluster 1 lists (`tests/test_config_validity.py:157`, `tests/test_skill_contracts.py`, `skills/publish/SKILL.md:33`).

______________________________________________________________________

## 8. Live checks owed

Each is a plan task, on the test Zotero (`localhost:23129`) or the scratch Obsidian vault, before the item it gates ships:

- **Linter for Zotero:** the per-rule key set, and that `lint.onAdded=true` with those keys writes only lossless values on add; its timing against `add`'s key wait.
- **ZotMoov** at its declared settings; **Attachment Scanner**'s automatic trash after #189.
- **arXiv Workflow:** its merge leg, then `propagate` following the re-key.
- **#185, #188:** Zotero accepting `PMID` and `PMCID` per item type; the field fold through `/api/schema`.
- **`extensions.json`** write timing while Zotero runs (§6.4).
- **Obsidian cold open** of a scaffolded, seeded vault: the trust prompt; every seeded plugin loaded (`eval Object.keys(app.plugins.plugins)`, empty `dev:errors`, `LANG` unset or `C`); `/`-led markdown links resolving; a `|480` size embed and a `.base` embed rendering; whether a Bases column resize writes the file; the Search block matching a claim line in `projects/`.
- **Screen C:** the load check for Reference Map, Zotero Annotation Citations and Zotero Deep Linker; key resolution against capture's bibliography file for Citations, Zotero Cite Links, Simple Citations and Zotero Lib View.
- **Recommended plugins:** each installed over its seeded `data.json`, and the file diffed after first load.
- **Novel word count** on a host whose language list holds only valid tags.
- **The deny rules** re-run against the shipped `.claude/settings.json`.
- **`read_okf`** against a compile-tool page with an unquoted `title: A: B`.

______________________________________________________________________

## 9. Order

One constraint binds the plans:

1. **Before the seeded `.obsidian/` ships:** §5's detection and the capture monitor — `captured.py` on the link resolver, the commit hook (§5.1), the monitor with #205, #185 and #188, #189, #196, #206, the compiled-page record (§5.4), `text-layer`, and #194's predicate and reader. The packaging test and scaffold's one-unit copy (§4.6) may land earlier.
2. **Before lane 4 opens:** #190 (§6.1), #193 (§5.7) and #172 (§11).

Within the monitor, designs cluster 1's order holds: #185 and #188; then the monitor with #205; then #189 and #196; then #206; then #183.

______________________________________________________________________

## 10. Sent onward

- **The library module** (§3.4): its own spec, after this one; home #140.
- **URL-source acquisition** (assembly §7.2.1): its own spec; home #151.
- **Lane 4:** annotation handling, with #18's must (pass Zotero's annotation colour through raw; adopt no colour taxonomy). Its skill screen fails a skill that writes a roster path other than through a research-vault verb or `transaction apply` — including `git checkout`, `restore`, `stash` or `reset`, `perl -i`, `truncate`, `find -delete`, `script` wrappers and raw appends to the review queue — or that bypasses the commit gate (`--no-verify`, `core.hooksPath`, or leaving the hook unable to import `research_vault`). Skills are prompt-bearing tier, so an `adapt` verdict names this must as `floor_failed`.
- **Lane 5:** the component register (assembly decisions 14, 19, 20).
- **#185:** whether a clean Retraction Watch lookup by PMID counts as verification.
- **The operator's production acts** (not plan tasks): set Linter's `lint.onAdded=false` until §3.1's key set is verified (#197, #200); set `pmcid.tags=false`, then remove the stray MeSH headings from `4JZGJN4M` and `KG3GZH6S` (#213); restore attachment `2FF57ABS` from the trash (#198); rule on the history rewrite (#181); the toolkit install route (#199); set §3's declared values so `plugins` passes.
- **Upstream filings** (the operator's act): #199, #200, #201, #213, #214, #215, #216, #217.

______________________________________________________________________

## 11. Amendments this spec makes

Each lands, dated, in the commit that makes it true:

- **Pre-lane-2 spec `:3`:** becomes an execution record (executed 2026-09-17 to 2026-09-23; binds until superseded; amended from here).
- **Assembly spec:** a 2026-10-17 State line at §7.1; §7.3's lanes 2, 3a and 3b point here; decision 17's Obsidian half points at `templates/obsidian/` (§4.6); §5.0's step map gains `analysis-reports` and `knowledge-management`; §6.2's restricted-mode paragraph names Obsidian's trust prompt (§4.7); §9 gains the `prefs.js` amendment (§6.4); §13's T3 passes and T5 becomes §8's cold-open leg; §15 items 03 (closed by §5.3.6), 05 (answered by row 5), 09 (every add-on dispositioned, §3), 13 (the `prefs.js` half answered) and 17 (answered by doctor's pinned-versus-installed row) are marked.
- **Ingest spec:** `:133` (tags split and field names folded, §5.3.4); `:137` (decision 28 stands); `:195` (a trashed attachment is drift, §5.3.5); `:448` (the add-on declaration's new shape, §6.1).
- **`CONTEXT.md`:** **Log** is machine-written and typed `log`; a new **Daily note** entry (person-owned, `daily/`); `type: fulltext` is reserved; the snapshot's field names fold to base names.
- **`docs/agents/okf-conformance.md`:** the claim-link row's reason corrected (§5.2); new rows for Tasks, Web viewer, Unique note creator, and the tool's `wiki/log.md` and `wiki/canvases/index.md` (ruling 7), each with its exemption or type mapping; the text layer named at `:42`.
- **`docs/agents/sourcing.md`:** the quotation rule (#172) — quote at most one line, only from a body whose licence is recorded at the pin, never an inline fragment from an unlicensed body; and the record of this spec's first high-bar `build` (§3.4), naming that decision 19 deferred the register linter and that the must was checked by hand.
- **`docs/agents/terminology.md`:** §7's names.
- **`README.md`:** the add-on tables (§6.1); `:7`'s machine-surface sentence (#192, §5.7).
- **`templates/vault/AGENTS.md`:** `:7` and `:28` (§5.7).
- **`ATTRIBUTION.md`:** vendored plugins and `SOURCE.json` (§4.6).
- **`pyproject.toml`:** PyYAML as a runtime dependency (§5.6); `license-files` for the vendored licences.
- **Skills:** `setup-vault` (the trust prompt, scaffold before adopt, the declaration pointer), `capture-source`, `synthesis-conventions`, `evidence-conventions`, `project-flow` and `publish` (new check ids).

**Issues this spec closes:** #161, #170, #172, #174, #183, #185, #188, #189, #190, #191, #192, #193, #194, #195, #196, #202, #203, #204, #205, #206, #207, #208, #209, #210, #211, #212, and #178 item 3. **Issues it updates:** #135 (the Actions and Tags route), #140 (the build verdict), #146 (the records half of a merge), #151 (the URL-source spec), #187 (arXiv Workflow as the repair route), #197 and #198 (production acts).
