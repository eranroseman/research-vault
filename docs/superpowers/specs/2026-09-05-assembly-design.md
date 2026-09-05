# research-vault as an assembly: obligations, component register, and lanes

Status: draft for author review (2026-09-05) — nothing here is decided except the rows marked **chosen**.

## 1. Evidence standard

Four labels, used wherever a reader could not otherwise tell which applies. Unlabelled prose is **proposed**.

- **measured** — established by a live read or command on this machine, with the date and the command in §14.
- **read** — established by reading a source file, a shipped artifact, or vendor documentation, with the location in §14.
- **chosen** — the author picked it in the 2026-09-05 brainstorm. Re-pickable, but not this document's to overturn.
- **open** — not yet answered. Carried in §15.

A fact with no method is not a fact here. Where this document contradicts working code or an earlier spec, it names the thing it contradicts.

**Facts have a shelf life.** A plugin-version fact on this machine expired inside one day: the sourcing catalogue's compatibility column was taken against Zotero 9.0.6 and the machine now runs 10.0.1 (§14). Every environment row in §14 carries its date, and a lane that relies on one older than its own start date re-measures it rather than citing it.

## 2. What this spec is, and what binds

This spec turns research-vault from a package that implements a research workflow into a **distribution**: a pinned set of third-party components, thin glue, and a setup/doctor/drift mechanism that keeps the set honest.

It names no component winners. It fixes the **obligations** the components must answer to (§4), the **register** that records what was chosen and why (§5), the **classes** each component belongs to and how each class is pinned (§6), and the **lanes** that do the choosing (§7).

What binds:

- The **measured environment** — §14.
- The **author's choices** — §3.

What does not bind, and why it is still useful:

- `CONTEXT.md` and `docs/adr/` are non-binding. ADRs 0004 and 0005 read `suspended (2026-09-03) — under re-derivation`. Their disposition belongs to issue #116, not here; this spec hands it forward rather than settling it, because the vocabulary will not be stable until the lanes have run.
- `docs/superpowers/specs/2026-09-04-import-redesign-design.md` is demoted from decision to **fact source**. Its §9 probes and the sourcing note behind it remain citable under §1's shelf-life rule. Its choices are re-opened.
- Existing code enters as **cost** and as **evidence**, never as authority. "We already built it" is not an argument, and §11 states the audit that acts on that.

## 3. Decisions

All **chosen** 2026-09-05 unless noted.

1. **Distribution over implementation.** research-vault is a pinned component set plus glue. Existing code survives only where a named workflow step needs it and no component fills the gap.
2. **Audit before deletion.** Every module in `research_vault/` receives a one-line disposition before anything is cut. The mutation suite and the linter work are preserved where their subject survives. §11.
3. **Two runtime tiers, restated.** A human-driven step may require a GUI. A mechanical check requires **no human in a GUI**; its carriers are the Zotero profile filesystem and the Zotero local API. *This is a repair of the original wording, forced by evidence*: the local API exposes no plugin enumeration and itself needs the Zotero process running, while the profile files are readable with Zotero closed and are only fully current after it exits (§6.1, §14). The mechanical tier therefore prefers Zotero **closed**, which is the inverse of the assumption it started from.
4. **One assembly spec, lanes executed inside and after it.** Not six lane specs up front, and not lane-local specs with the glue arriving last.
5. **Lane order is 0 → 4 as in §7.** *This supersedes the earlier choice of Zotero plugin curation as the first lane*, which was the weakest of the six: curation produces a document, while a distribution's claim is install + pin + drift, and lanes 1 and 2 are mutually dependent until lane 0 breaks the cycle.
6. **A status-marking pass runs before this spec's lanes.** §10.
7. **Requirements are indexed, not translated.** §4.
8. **A `build` disposition must name the floor no candidate met and the candidate set screened.** Enforced as a register schema constraint, not as prose. §5.2.
9. **Cold start is a spec requirement with a mechanical check.** §8.
10. **The repository goes public**, after the cutover preconditions in §12 are met.
11. **URL-only sources: the cut is cited versus consulted, not URL versus document.** Recorded as a lane 1 open item with its evidence, not settled here. §7.2.

## 4. Obligations index

The five founding documents are indexed, never translated. An index row cites; it does not say what the system shall do. That keeps interpretation with the lane that has the evidence to interpret, and it keeps this spec from resolving conflicts it has not earned.

| Source | What it carries | Answering lane |
| --- | --- | --- |
| PRISMA-S | reporting items for a literature search | search |
| PRISMA-ScR | the scoping-review extension checklist | scoping review |
| ACM submission guidelines | manuscript and reference-format obligations | long form |
| Notetaking for Historians (Obsidian publish) | a prose-first, low-machinery vault workflow | vault layout, daily log |
| Karpathy's llm-wiki gist | the LLM-maintained-wiki maintenance pattern | compile |

Two properties the index must have:

- **Conflicts are recorded as conflicts.** These five pull apart — history-notes is prose-first and low-machinery, PRISMA-ScR is protocol-driven and checklist-bound, ACM is a submission format. A row may read *"history-notes and PRISMA-ScR pull opposite ways here; lane N resolves"*. An implicit conflict where each lane silently picks a side is strictly worse.
- **The sources live in the vault, not in a URL.** All five are admitted to Zotero and captured, making them the first sources the pipeline handles. The index then cites literature notes rather than links, the guidelines outlive their URLs, and lane 1's capture contract gets its first real test case from the documents that define the work.

**Gap pass.** Per-lane at close, then once at the end. A gap found at lane close is a floor amendment; the same gap found after every lane has run is a re-run.

## 5. The component register

### 5.1 Shape

One row per workflow step. The register is the artifact that outlives this spec; lanes append to it and nothing else may.

| Column | Meaning |
| --- | --- |
| `step` | the workflow step served |
| `component` | what serves it, or empty |
| `class` | one of §6's four |
| `disposition` | `adopt` \| `adapt` \| `build` \| `gap` \| `open` |
| `pin` | the pinned identifier, in the class's own vocabulary |
| `pin_semantics` | `held` or `verified-against` — see §6 |
| `provisioning` | how it is installed |
| `tier` | `gui` or `mechanical` |
| `decided_by` | the lane that closed the row |
| `decided_on` | the date |

### 5.2 The build-disposition constraint

A row with `disposition: build` must carry two further non-empty fields:

- `floor_failed` — the requirement floor that no candidate met.
- `candidates_screened` — the set measured against it.

`adopt`, `adapt` and `gap` require neither. The register's linter fails a `build` row missing either field.

The rule exists because a documented prior belief in this project — that writing our own Zotero connector is simpler and better than adopting one — may well be correct and cannot be evaluated, because no screening record was kept. The constraint does not forbid building. It makes a build verdict falsifiable.

This is a schema constraint and a lint, not an ADR. The ADR register records decisions about the vault and the product; this is a decision about how components are chosen, and that register is suspended under re-derivation regardless. The higher rung — the discipline living in the `software-development` brainstorming skill so no repository needs the rule — is filed upstream, not built here.

## 6. Component classes

Four classes, four different mechanisms. A distribution that says "pin" without saying which mechanism is saying nothing.

### 6.1 Zotero plugin (XPI)

All three legs are closed, and none requires a write from research-vault.

| Leg | Mechanism |
| --- | --- |
| install | human, Zotero UI — a setup wizard step |
| pin (hold) | the author's global auto-update toggle, set once |
| pin (verify) | doctor reads `prefs.js` for `extensions.update.autoUpdateDefault == false` **and** asserts no addon carries `applyBackgroundUpdates == 2` |
| drift | `extensions.json`, read with Zotero closed |

`pin_semantics` for this class is **held**, and only because the toggle is off. Measured before the toggle: auto-update was on by default, no addon overrode it, and it fired during the probe window (§14). Had the toggle not existed, this class's pin would have been `verified-against` — a version you notice changing, not a version you hold.

`applyBackgroundUpdates == 2` is `AUTOUPDATE_ENABLE`, which overrides the global off for one addon. All 23 currently sit at `1` (`AUTOUPDATE_DEFAULT`). Doctor asserts the absence of a `2`, not merely the presence of the global `false`, because either alone is insufficient.

**The class carries a silent-failure mode, live on this machine.** `zoteroshortdoi@wiernik.org 1.6.0` is `appDisabled` — its manifest caps at `9.0.*` and Zotero refuses it. A plugin the vault relies on that Zotero will not load is a check that never runs and never says so. Doctor's per-plugin report is therefore a triple: present, loads on the running Zotero version, and automatic mode on.

**The local API sees plugin effects even though it cannot enumerate plugins.** `/api/users/0/tags` returns `#broken`, `#duplicate`, `#nosource` (measured). A plugin is detectable by its library footprint. That is a second, independent detection channel and lane 0 uses both.

### 6.2 Obsidian plugin

| Leg | Mechanism |
| --- | --- |
| install | file drop into `<configDir>/plugins/<id>/` plus the id in `community-plugins.json`, or BRAT |
| pin | BRAT's `pluginSubListFrozenVersion` — the only pinning route Obsidian's own documentation endorses |
| verify / drift | `<configDir>/plugins/<id>/manifest.json` `version`, the only place an installed version is recorded |

Two constraints, both **read**:

- The config directory is user-overridable, so no path may be hardcoded.
- Restricted mode is gated by a key in Obsidian's Chromium localStorage, **outside the vault**. A purely file-based installer silently no-ops on a fresh vault. Restricted mode is therefore a **setup precondition**, not a check — it needs a human in Settings or the official CLI.

**There is no research-vault Obsidian vault on this machine** (measured). Every Obsidian fact gathered so far describes a sibling project's vault. `research_vault/templates/vault/` ships 15 files and **none under `.obsidian/`**, so the scaffold produces a vault Obsidian has never configured, while shipping two `.base` files whose minimum Obsidian version is recorded nowhere. Lane 3 opens by creating the vault this class is about.

### 6.3 Claude Code plugin or skill

`pin_semantics`: **held**, by sha.

The mechanism this class should adopt is under construction in the sibling `agent-plugins` repository and does not yet exist: no `bin/`, no `upstream/skills.json`, no `upstream-watch.yml`, gates S1–S5 unverified, doctor's exit semantics unspecified, and no rollback story for a failed setup or update (read, §14). We are borrowing a **design**, and this spec says so rather than inheriting an unbuilt thing as though it were proven.

Three routes were weighed. Blocking stalls lane 1 on another project's schedule. Building our own violates the adopt-first order for a class about to have an owner. **Chosen: an interim** — a sha pin in the marketplace entry, which the ingest spec measured working, plus `git ls-remote` for drift. Two lines, not a build. The handoff condition is written into the register: when `agent-plugins` ships `bin/setup` and `bin/doctor` with gates S1–S5 verified, research-vault adopts them and deletes the interim.

Our two extra classes — Zotero profile-file pinning and Obsidian BRAT freezing — are requirements that sibling's spec never considered. They are filed upstream while it is still in design, following the pattern this repository already runs (#103, #104, #113–115), rather than discovered as a mismatch after it ships.

### 6.4 Python dependency

`pyproject` plus a lock. Standard, and the only class with nothing open.

### 6.5 An unpinned installer already ships

`research_vault/scaffold.py:23` declares `PROVISION_COMPANIONS = ["kepano/obsidian-skills"]`, and `skills/setup-vault/SKILL.md:42` instructs `claude plugin install kepano/obsidian-skills`. No version, no pin, no drift check. The problem this spec exists to solve is live in the package, and it is register row zero.

## 7. Lanes

### 7.0 Lane 0 — substrate audit

Measurement, not selection, therefore no dependencies. It exists because lanes 1 and 2 are otherwise circular: capture must parse and preserve what plugins wrote, and which plugins to keep depends on what capture consumes.

Output: what is installed, what is active, and **what grammar is already in the library**. Both detection channels from §6.1. The 23 installed addons are the unit, not the 12 the author named — a distribution with an undispositioned remainder has no drift semantics.

Two grammar facts already measured, which are requirements rather than risks:

- The library carries attachment-scanner's simple tag preset (`#nosource`, `#broken`, `#duplicate`) while `prefs.js` now configures its emoji preset (`❌ nosource`, `🚫 broken`, `❓ nonfile`, `‼️ duplicate`). One library, two generations of one signal. Capture reads both.
- The PMCID fetcher is configured to add fetched identifiers as Zotero keywords, so PMCID and PMID may arrive as **tags** as well as Extra lines. Lane 0 measures which; §14 records the sourcing note's Extra-line reading and does not assume it is the only path.

### 7.1 Lane 1 — capture and compile, together

The author's original items 2 and 3 are one lane. They share the capture→compile seam, which is the seam the previous design broke, and deciding them apart is what forces a re-run.

Lane 1 fixes the seam contract: capture preserves the Extra field byte-identical, reads a **declared** tag vocabulary, and writes the compile input in a format the chosen engine actually accepts.

### 7.2 Lane 1 open item — URL-only sources

Recorded with its evidence rather than settled.

The claim that a URL-only entry gains nothing from Zotero is right about organisation and wrong about three things. **Identity**: a cited URL needs a bibliography entry with an accessed date, and only Zotero plus Better BibTeX mints one here. **Link rot**: this is the one source class that disappears, and `research_vault/archive.py` — the sole writer of `archive-url`, Wayback-confirmed, four-state honest — already answers it and keys on the citekey, so skipping Zotero leaves it nothing to key on. **PRISMA**: PRISMA-S covers grey literature and web searching, and a scoping review citing a source whose provenance it cannot report fails its own checklist.

The proposed cut is therefore **cited or plausibly cited** → Zotero, and **consulted only** → no item, never citable. A wrong save costs a junk item that attachment-scanner already cleans; a wrong skip costs an unrecoverable dead link. If consulted-not-cited volume becomes noise, the remedy is Zotero-side, never a second identity system.

This row also decides whether `archive.py` survives §11's audit, which is why the audit follows the step map rather than preceding it.

### 7.3 Lanes 2–4

| Lane | Scope | Notes |
| --- | --- | --- |
| 2 | Zotero plugins | a choice *within* lane 1's contract, measured against 10.0.1, over all 23 installed |
| 3 | Obsidian plugins | seam-free; opens by creating the vault that does not exist (§6.2) |
| 4 | Skills curation — MedSci, K-Dense | consumers of the workflow steps, so it follows the search and scoping-review specs |

Lanes 2 and 3 are seam-free and may run concurrently. Lane 1 must not be split.

Each lane runs as a **scoping review**: a bounded question, a screened candidate set, recorded exclusions. That builds the scoping-review workflow by using it, and yields the well-formed evidence the repository's existing prior-art notes were reaching for without the terminology.

**Lane 2's inherited evidence is stale in a specific way.** The 36-repository catalogue read **repository manifests**; the machine runs **shipped `.xpi` manifests**, and they differ — `zoterotldr` and `scite` are both active on 10.0.1 while the catalogue records ranges that would refuse them. Seventeen catalogue rows say "loads on 9.0.6"; none mentions 10.0.1. Lane 2 re-measures loadability from the installed `.xpi`, not from the catalogue.

## 8. Cold-start contract

A session opening lane N reads exactly: the component register, this spec's §3 and §15, and the prior lane's scoping review. Nothing else.

That list is named in the register and budgeted in lines. The status linter (§10) fails if the list points at anything marked `historical` or `pending-map`.

The contract exists because the expensive part of entering this repository is not reading volume, it is inferring which material still binds. The register answers that in one screen.

## 9. Setup, doctor, and drift

**A doctor already exists.** `research_vault/scaffold.py:322` runs eight probes — tree, machine, zotero, bbt, autoexport, staleness, remote, backup — and **none concerns an installed component**. This spec extends it rather than starting a second one. Adopt-over-build applied to our own code.

Doctor gains, per §6:

- the Zotero pin verification pair (`autoUpdateDefault == false`, no addon at `applyBackgroundUpdates == 2`);
- the per-plugin triple (present, loads on the running version, automatic mode on);
- the Obsidian manifest version read;
- the Claude Code sha comparison via `git ls-remote`;
- a merge check for the Zoplicate path (§15).

Doctor's exit semantics are **open** — the borrowed spec never states them, so any behaviour assumed here would be our own design wearing borrowed clothes. §15 carries it.

**Rollback is open too.** The borrowed spec has no rollback story for a failed setup or update; its only rollback text covers a one-time marketplace cutover. Setup as designed is forward-converging with no inverse, and its nearest safety property is "never delete a squatting file or link — move it aside and report".

## 10. The status-marking pass

Runs before this spec's lanes, as its own bounded task with its own approval. Nothing moves, nothing is deleted.

Scope, measured: **201 markdown files** — `docs/` 103, `.superpowers/` 71, `skills/` 23, root 4 — of which **25** already carry a header status marker.

The convention already exists and is reused rather than invented: line 3 after the H1, `Status: <state> (<date>) — <reason>`, as the five ADRs and both specs write it.

Closed vocabulary, every value decidable without the register:

| Status | Test |
| --- | --- |
| `sibling-project` | belongs to another product's register |
| `superseded-by: <path>` | an explicit supersession already exists |
| `historical` | a dated pass that closed — evidence, never a live decision |
| `current` | still binding |
| `pending-map` | disposition needs the register |

`pending-map` is load-bearing. Without it the pass guesses the dispositions it was sequenced to avoid.

Orthogonal flag, not a status: `should-be-scoping-review`. A document may be `historical` **and** flagged as a scoping review the workflow should later replace. That flag produces the test-case set.

Three premises the pass started with were false, and the pass is scoped to the corrected ones (all measured):

- The named siblings — the coaching apps, the ADHD pilot, archify, Memoria — own **zero** files in the main tree. The sibling that does own files is `software-development`/`sensemaking`, whose two documents self-declare it.
- `superseded` is a **domain term for source state** in this repository, not a status marker. Explicit document-to-document supersession is **3 pairs**, not the 44 a naive grep suggests.
- The `.superpowers/sdd/` workspace is retained-and-closed by deliberate commits, not abandoned.

**Its own linter**, per this repository's rule that a mechanical process gets a mechanical check: every `.md` in scope carries one status from the closed vocabulary, every `superseded-by` target resolves, no file carries two.

**Scope bound.** The pass marks documents. The material that most often goes stale here is **environment facts**, and `AGENTS.md` already carries the rule for those — recorded where they are used, each with its method and date. The pass does not duplicate that rule; §1's shelf-life clause is where environment staleness is handled.

## 11. Code disposition audit

Measured inputs: 29 modules, 10,597 lines, 21 CLI verbs, 45 test files, 24,571 lines, 25 mutation sidecars of which 18 are stale against their own declared source hash.

**The audit unit is the verb, not the module.** Nine modules are named by no verb and are reachable only transitively, and `frontmatter` is imported by 12 modules while `pathcodec` is imported by 10 — so every module transitively "serves" something and a module-level criterion never cuts. The import graph is also blind to real coupling: `hooks/stop_publish_gate.py:15` matches `research_vault/publish.py:36` by filename, not by import.

Each verb receives a one-line disposition against the step map: serves step X, serves nothing, or serves a deferred workflow. Deletion follows the disposition; the disposition is a recorded judgement, never a silence.

Two cautions:

- **"Preserve the mutation suite where its subject survives" must not preserve rot.** 18 of 25 sidecars are already stale, and the plan that retires them (`docs/superpowers/plans/2026-08-24-plan-w-quality-tail.md`) has unchecked steps. The audit dispositions the sidecars alongside the code.
- **Coverage data is unusable and must be regenerated.** The committed `.coverage` resolves against `/home/eranr/New folder/research_vault/`, a foreign checkout — the exact wrong-tree trap `docs/testing.md` warns about. "Does this verb actually run" has no data until a fresh run.

## 12. Cutover: going public

Going public is **chosen**, and it closes the Claude Code class's last open item, since the marketplace bootstrap against a private repository was never tested.

Two preconditions, both measured, neither blocking the decision and both blocking the flip:

1. **248.5 MB of raw Claude Code session transcripts sit in git history** — `docs/research/raw/knowledge-harness-transcripts/*.jsonl` and its post-rename twin, with single files at 32 MB, 23 MB and 19 MB. Untracked today; present in every clone forever. Publishing the repository publishes everything those sessions saw.
2. **Eight PDFs were committed and later removed.** Four are 2026 copyrighted papers, one is a 2014 journal article, and the remainder are US-government ICD/ICS documents.

Clean by contrast: `sources/` is gitignored with zero tracked files, and the ISO standards it currently holds were **never** committed.

Route: a history rewrite before the flip, or a fresh public repository from a squashed tree. This is its own task with its own approval, not work that rides along inside a lane.

## 13. Tracers

A tracer is one cheap check that can falsify a decision, run before the decision is built on.

| | Tracer | Result |
| --- | --- | --- |
| T1 | enumerate installed Zotero plugins, no GUI | **passed** — `extensions.json` is plain JSON and carries every field needed |
| T2 | is plugin auto-update on | **passed after author action** — was on and firing; now `false` at `prefs.js:49` |
| T3 | doctor's per-plugin triple on one plugin before screening many | open |
| T4 | status linter over a hand-marked sample | open |
| T5 | Obsidian plugin version readable by file | open, and blocked on §6.2's missing vault |
| T6 | cutover — scratch vault, setup from zero, doctor green | open, post-spec |

A tracer that would have required writing to the author's Zotero profile (`user.js`) was **cancelled**: the author's GUI toggle answered T2 directly, and the file remains absent.

## 14. Mechanism claims and their sources

All probes 2026-09-05 unless noted, on this machine, read-only.

| Fact | Value | Established |
| --- | --- | --- |
| Zotero, Better BibTeX | 10.0.1 on Windows; BBT 9.0.63; local API reachable from WSL2 | live probe 2026-09-04 |
| Zotero profile | `/mnt/c/Users/eranr/AppData/Roaming/Zotero/Zotero/Profiles/881hrcxd.default`, sole profile per `profiles.ini` | measured |
| Zotero data directory | `D:\Zotero` per `extensions.zotero.dataDir`, not the Windows default | measured |
| `extensions.json` | plain JSON, schemaVersion 37, 23 addons, each with id, version, `active`, `userDisabled`, `appDisabled`, `applyBackgroundUpdates`, `targetApplications` | measured |
| addon states | 12 active, 10 user-disabled, 1 app-disabled | measured |
| `zoteroshortdoi` 1.6.0 | `appDisabled=true`; manifest caps `9.0.*`. The ingest spec's "6.0 to 7" is stale; the conclusion is not | measured |
| auto-update, before | both prefs absent; defaults `true` read from `omni.ja` `defaults/preferences/zotero.js`; `applyBackgroundUpdates=1` on all 23; fired 2026-09-05 17:33:54Z with 15 addons stamped in an 11-second window | measured / read |
| auto-update, after | `prefs.js:49` `extensions.update.autoUpdateDefault = false`, file written 18:17:19; still no per-addon override | measured |
| `addonStartup.json.lz4` | mozLz4 container, no decoder available; unnecessary, `extensions.json` carries the same fields | measured |
| plugin enumeration over the wire | none — local API `/api/` returns 404s, BBT JSON-RPC's 14 methods expose nothing | measured |
| plugin **effects** over the wire | `/api/users/0/tags` returns `#broken`, `#duplicate`, `#nosource` | measured |
| attachment-scanner | 0.5.1 active; `prefs.js:28-31` `monitor_attachments`, `remove_pubmed_entry`, `remove_snapshot`, `scan_nonfiles` all true; library holds the simple tag preset while `prefs.js:32-35` configures the emoji preset | measured |
| PMCID fetcher | 1.0.3 loads; auto-fetch checkbox unchecked, gate pref absent; "add as keywords" checked | measured; author screenshot 2026-09-05 |
| Zoplicate | 5.1.1, user-disabled by mistake, to be re-enabled; manifest `8.999–10.0.*`, AGPL-3.0 | measured; author 2026-09-05 |
| attachment-scanner manifest | `6.999`–`*`, MIT, read from the released `.xpi` | read |
| catalogue staleness | compatibility column taken at Zotero 9.0.6; 17 of 36 rows say "loads on 9.0.6", none mentions 10.0.1; the catalogue read repository manifests while the machine runs shipped `.xpi` manifests, and `zoterotldr` and `scite` differ | measured |
| existing doctor | `research_vault/scaffold.py:322`, eight probes, none about installed components | read |
| unpinned installer | `scaffold.py:23` `PROVISION_COMPANIONS = ["kepano/obsidian-skills"]`; `skills/setup-vault/SKILL.md:42` | read |
| borrowed mechanism | `agent-plugins` has no `bin/`, no `upstream/skills.json`, no `upstream-watch.yml`; gates S1–S5 unverified; doctor exit semantics unspecified; no rollback story | read |
| Obsidian pinning | BRAT `pluginSubListFrozenVersion` is the only documentation-endorsed route; `manifest.json` `version` is the only installed-version record; restricted mode is gated in Chromium localStorage outside the vault | read |
| `obsidian-reference-map` | unmaintained since 2024-01-01; GPL-3.0 LICENSE against an MIT `package.json`; needs Better BibTeX's local server; reported broken against BBT 9.0.57+ | read |
| no research-vault vault | Obsidian knows only sibling vaults; `research_vault/templates/vault/` ships 15 files, none under `.obsidian/` | measured |
| corpus | 201 `.md` in scope (docs 103, `.superpowers` 71, skills 23, root 4); 25 carry a status marker; 3 explicit supersession pairs; named siblings own zero main-tree files | measured |
| issues | 66 open; none older than 2026-08-25 by `updatedAt`, an instrument that comment and label edits also bump | measured |
| code | 29 modules / 10,597 lines; 21 verbs; 45 test files / 24,571 lines; 25 sidecars, 18 stale; 9 modules named by no verb | measured |
| coverage data | resolves against `/home/eranr/New folder/research_vault/` — a foreign checkout, unusable | measured |
| git history | 248.5 MB of session transcripts; 8 PDFs added then removed; `sources/` gitignored with 0 tracked and the ISO standards never committed | measured |

## 15. Open items carried forward

1. Doctor's exit semantics (§9).
2. Rollback for a failed setup or update (§9).
3. The Zoplicate merge path: Zotero trashes the losing item and records `dc:replaces`, and whether a pinned `Citation Key:` Extra line survives the merge is inferred in both directions and never observed. Since the citekey is the vault's identity, a merge is an identity event.
4. URL-only sources — cited versus consulted (§7.2).
5. Whether PMCID and PMID arrive as tags, Extra lines, or both (§7.0).
6. The `.py.manifest.json` sidecars: retire with mutate4py, or keep (§11).
7. Duplicate detection has no owner while Zoplicate is disabled; `zotero-format-metadata` detects and reports but does not merge (§7.0).
8. The glossary and the two suspended ADRs — handed to issue #116, not settled here (§2).
9. The remaining 11 of 23 installed addons, undispositioned, including one that copies attachments to a OneDrive path (§7.0).
10. The `upstream-watch` schedule: the borrowed spec names a scheduled workflow and gives no interval (§6.3).
