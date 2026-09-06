# research-vault as an assembly: obligations, component register, and lanes

Disposition: current (2026-09-06)

Status: draft for author review (2026-09-05) — nothing here is decided except the rows marked **chosen**.

## 1. Evidence standard

Four labels, used wherever a reader could not otherwise tell which applies. Unlabelled prose is **proposed**.

- **measured** — established by a live read or command on this machine, with the date and the artefact or endpoint in §14.
- **read** — established from a source file, a shipped artefact, or vendor documentation, with the file and line, the URL, or the artefact named in §14.
- **chosen** — the author picked it in the 2026-09-05 brainstorm. Re-pickable, but not this document's to overturn.
- **open** — not yet answered. Carried in §15.

A fact with no method is not a fact here.

**Facts have a shelf life, and inherited facts have none at all.** The sourcing catalogue judged plugin loadability against Zotero 9.0.6 — a value carried from a deleted standing-facts file — while this machine had run 10.0.1 since 2026-08-26, including on 2026-09-04, the catalogue's own date (§7.3, §14). That fact was wrong when written, not stale by elapse. The obligation stands either way: every environment row in §14 carries its date, a lane relying on one older than its own start date re-measures rather than cites, and a row with no probe of its own is not a dated fact at all.

**This document has already demonstrated the failure it describes.** Between its first probe run and its first commit, the author enabled PMCID auto-fetch and re-enabled Zoplicate, and four §14 rows became false inside seventeen minutes. The rows below are re-measured as of 19:0x on 2026-09-05, and they will decay the same way.

## 2. What this spec is, and what binds

This spec turns research-vault from a package that implements a research workflow into a **distribution**: a pinned set of third-party components, thin glue, and a setup/doctor/drift mechanism that keeps the set honest.

It names no component winners. It fixes the **obligations** components answer to (§4), the **step map** and **register** that record what was chosen and why (§5), the **classes** each component belongs to and how each is pinned (§6), and the **lanes** that do the choosing (§7).

What binds: the **measured environment** (§14) and the **author's choices** (§3).

What does not bind, and why each is still useful:

- `CONTEXT.md` and `docs/adr/` are non-binding. ADRs 0004 and 0005 carry `Status: suspended (2026-09-03)` and say on their face that nothing new builds on them until they return to accepted or are superseded. Their disposition belongs to issue #116, not here; the vocabulary will not be stable until the lanes have run.
- `docs/superpowers/specs/2026-09-04-import-redesign-design.md` is demoted from decision to **fact source**. Its probes remain citable under §1's shelf-life rule; its choices are re-opened.
- `docs/superpowers/specs/2026-08-16-foundation-spec.md` is demoted on the same terms, and this spec re-opens three of its choices by name: **research-vault-owned note generation** (an unscreened `build` under §5.2), **MarkDB-Connect as the sole vault→Zotero write-back** (a Zotero plugin not among the 23 installed, which is why lane 2's scope reads "all 23 installed, plus the author's named not-installed candidates"), and **ZotLit as later-adoptable UI**. Its file conventions, including the daily log, remain **read**.
- Existing code enters as **cost** and as **evidence**, never as authority. §11 states the audit that acts on that.

## 3. Decisions

All **chosen** 2026-09-05 unless noted.

01. **Distribution over implementation.** research-vault is a pinned component set plus glue. Existing code survives only where a named step (§5.0) needs it and no component fills the gap.

02. **Audit before deletion.** Every CLI verb receives a one-line disposition, and so does every module and entry point no verb reaches — including the three files in `hooks/` (847 lines) and `hooks/hooks.json`. The verb is the decision unit; the module is the record unit. The mutation suite and the linter work are preserved where their subject survives. §11.

03. **Two runtime tiers, and the mechanical tier splits in two — for both substrate apps.** A human-driven step may require a GUI. A mechanical check requires **no human in a GUI**, and its two carriers have opposite preconditions: **mechanical-live** talks to a running app; **mechanical-cold** reads that app's files on disk and wants it closed. *This is a repair of the original wording, forced by evidence.*

    | Substrate | mechanical-live                                                                              | mechanical-cold                                                    |
    | --------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
    | Zotero    | the local API — which exposes no plugin enumeration (§14) and runs inside the Zotero process | `extensions.json`, `prefs.js` — readable with Zotero closed        |
    | Obsidian  | the official CLI, which requires the desktop app running and takes no version parameter      | `<configDir>/plugins/<id>/manifest.json`, `community-plugins.json` |

    Obsidian carries the sharper version of the same hazard: its restricted-mode gate lives in Chromium localStorage, whose LevelDB is only reliably read with the app closed — presence is evidence there, absence is not (§6.2). Whether either app's files are *fully current* only after exit is **open**: Zotero's two were observed rewritten while it was running (§15.13). The register's `tier` column carries which carrier a check uses.

04. **One assembly spec; lane 0 executed inside it, lanes 1–4 after it.** Not six lane specs up front, and not lane-local specs with the glue arriving last.

05. **Lane order is the dependency order in §7**: 0, then 1, then 2 and 3a concurrently, then 3b, then 4. *This supersedes the earlier choice of Zotero plugin curation as first lane* — curation produces a document, while a distribution's claim is install + pin + drift, and lanes 1 and 2 are mutually dependent until lane 0 breaks the cycle.

06. **A status-marking pass runs before this spec's lanes.** §10.

07. **Requirements are indexed, not translated.** §4.

08. **The build bar scales with embedded knowledge.** §5.2.

09. **Cold start is a spec requirement with a mechanical check.** §8.

10. **The repository goes public**, after §12's preconditions are met.

11. **URL-only sources: the cut is cited versus consulted.** Proposed with its evidence in §7.2; lane 1 confirms or overturns it. Not settled here.

## 4. Obligations index

The five founding documents are indexed, never translated. An index row cites; it does not say what the system shall do. That keeps interpretation with the lane that has the evidence, and keeps this spec from resolving conflicts it has not earned.

| Source                    | What it carries                             | Step it binds              | Lane that screens against it |
| ------------------------- | ------------------------------------------- | -------------------------- | ---------------------------- |
| PRISMA-S                  | reporting items for a literature search     | `search`                   | **lane 4**                   |
| PRISMA-ScR                | the scoping-review extension checklist      | `scoping-review`           | **lane 4**                   |
| ACM submission guidelines | manuscript and reference-format obligations | `long-form`                | **lane 4**                   |
| Notetaking for Historians | a prose-first, low-machinery vault workflow | `vault-setup`, `daily-log` | lane 3a                      |
| Karpathy's llm-wiki gist  | the LLM-maintained-wiki maintenance pattern | `compile`                  | lane 1                       |

**These are screening criteria, not work items.** PRISMA-S, PRISMA-ScR and the ACM guidelines are the **floors lane 4 screens candidate skills against** — a MedSci or K-Dense skill earns adoption by satisfying checklist items, and fails on the ones it does not reach. That is exactly the floor definition below, so the index rows are lane 4's floor sources rather than specs somebody must write first.

The distinction that keeps this honest: **screening a component against an obligation is not the same as specifying the step.** Issues #117 and #119 own specifying the `search` and `scoping-review` steps, and their output would refine lane 4's floors — but lane 4 does not wait on them, because a checklist is a screening instrument whether or not a step spec exists yet. A lane *screens against* an obligation; it does not own the step. The step column is the register's key (§5.0).

Two properties the index must have:

- **Conflicts are recorded as conflicts.** These five pull apart — history-notes is prose-first and low-machinery, PRISMA-ScR is protocol-driven and checklist-bound, ACM is a submission format. A row may read *"history-notes and PRISMA-ScR pull opposite ways here; the answering party resolves"*. An implicit conflict where each lane silently picks a side is strictly worse.
- **The sources live in the vault, not in a URL.** All five are admitted to Zotero and captured, making them the first sources the pipeline handles. The index then cites literature notes rather than links, and lane 1's capture contract gets its first real test case from the documents that define the work.

**Definitions the rest of the spec leans on.** A **floor** is a numbered requirement a lane writes into its scoping review *before* it screens candidates; this index's rows are its sources. `floor_failed` cites a floor by lane and number, and the register's linter rejects a value that does not resolve to one. A **re-run** re-opens a named lane against a candidate set the gap defines, and needs the author's approval.

**Gap pass.** Mechanically: every obligation in this index with no register row citing it (§5.1's `obligations` column). Run per-lane at close, then once at the end. A gap found at lane close is a floor amendment; the same gap found after every lane has run is a re-run.

## 5. The step map and the component register

### 5.0 The step map

The steps are the register's key domain, closed for this spec's lanes and extended only by an author decision:

`vault-setup`, `capture`, `compile`, `search`, `scoping-review`, `long-form`, `daily-log`, `publish`

§4 seeds it. Each lane appends the components that serve a step and may not invent one. A verb serving a step no lane covers is dispositioned `deferred`, never `serves nothing` (§11).

### 5.1 Register shape

Keyed on `(step, component)`, with an empty `step` permitted for a component that serves none. Lanes append rows and may supersede their own; a named header block carries what is not a row.

| Column                     | Meaning                                                                |
| -------------------------- | ---------------------------------------------------------------------- |
| `step`                     | the step served, from §5.0; may be empty                               |
| `component`                | what serves it, or empty                                               |
| `class`                    | one of §6's four                                                       |
| `disposition`              | `adopt` \| `adapt` \| `build` \| `gap` \| `reject` \| `open`           |
| `pin`                      | the pinned identifier, in the class's own vocabulary                   |
| `pin_semantics`            | `held` or `verified-against` — §6                                      |
| `provisioning`             | how it is installed                                                    |
| `tier`                     | `gui` \| `mechanical-live` \| `mechanical-cold`                        |
| `obligations`              | the §4 rows this component answers; the gap pass reads this column     |
| `floor_failed`             | required on `build` and `adapt` at the high bar; empty otherwise       |
| `candidates_screened`      | required on `build` and `adapt` at the high bar; empty otherwise       |
| `superseded_by_row`        | set when a later row replaces this one; rows are closed, never deleted |
| `closed_on`                | the date the row was closed                                            |
| `decided_by`, `decided_on` | the lane and the date                                                  |

**Header block**, written by this spec and amended only by an author decision: the cold-start reading list (§8), and each row's handoff condition where one exists (§6.3).

### 5.2 The build bar scales with embedded knowledge

The adopt→build gap is not uniform. Writing and maintaining a skill is an art, and an adopted one keeps improving without us; a mature tool carries edge cases we have not hit yet; a glue script carries almost nothing, and adopting one imposes a pin, a drift check, an upgrade path and a licence review that can cost more than the code. **Adopt-first is not dogma, and the counterweight is stated here rather than discovered later.**

| Tier               | Examples                              | Bar for `build` or `adapt`                                   |
| ------------------ | ------------------------------------- | ------------------------------------------------------------ |
| **Prompt-bearing** | skills, agents, the compile engine    | **high** — `floor_failed` and `candidates_screened` required |
| **Mature tool**    | Better BibTeX, Zotero plugins, ZotLit | **high** — same                                              |
| **Glue**           | a doctor probe, a tag map, a lint     | **low** — one line of reason                                 |

`adopt`, `gap`, `reject` and `open` carry no constraint at any tier. `adapt` carries the same constraint as `build` at the high bar, because otherwise a lane that wants to build without screening simply writes `adapt` — and `research_vault/zotero.py` already exists, which makes that evasion available for the very decision this rule was written for.

The rule exists because a documented prior belief — that writing our own Zotero connector is simpler and better than adopting one — may well be correct and cannot be evaluated, because no screening record was kept. It does not forbid building. It makes a build verdict falsifiable. Capture sits in the **mature tool** tier, not the glue tier: its candidates carry years of edge-case handling this repository has already hit.

This is a schema constraint and a lint, not an ADR. The ADR register records decisions about the vault and the product; this is about how components are chosen, and that register is suspended regardless. The higher rung — the discipline living in the `software-development` brainstorming skill so no repository needs the rule — is filed upstream, not built here.

## 6. Component classes

Four classes, four mechanisms. A distribution that says "pin" without saying which mechanism is saying nothing.

### 6.1 Zotero plugin (XPI)

Three legs, two closed and one machine-local.

| Leg          | Mechanism                                                                                                                                                   |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| install      | human, Zotero UI — a setup wizard step                                                                                                                      |
| pin (hold)   | the author's global auto-update toggle, set once, in a GUI                                                                                                  |
| pin (verify) | doctor reads `prefs.js` for `extensions.update.autoUpdateDefault == false` **and** asserts no addon carries `applyBackgroundUpdates == 2` — mechanical-cold |
| drift        | `extensions.json`, mechanical-cold                                                                                                                          |

`pin_semantics` is **held on this machine only**. Nothing in setup establishes it elsewhere: the install leg installs whatever is current rather than a named version, the hold is a preference flipped by hand, and the one tracer that would have tested a mechanical route (`user.js`) was cancelled when the author's toggle answered T2 directly. Un-cancelling it, or specifying the wizard step that replaces it, is §15.14. Measured before the toggle, this class's pin would have been `verified-against`.

`applyBackgroundUpdates == 2` is `AUTOUPDATE_ENABLE`, which overrides the global off for one addon. All 23 currently sit at `1`. Doctor asserts the absence of a `2`, not merely the presence of the global `false`, because either alone is insufficient.

**The class carries a silent-failure mode, live on this machine.** `zoteroshortdoi@wiernik.org 1.6.0` is `appDisabled` — its manifest caps at `9.0.*` and Zotero refuses it. A plugin the vault relies on that Zotero will not load is a check that never runs and never says so. Doctor's per-plugin report is therefore a triple — present, loads on the running version, automatic mode on — **proposed, pending T3**.

**The local API sees plugin effects even though it cannot enumerate plugins.** A plugin is detectable by its library footprint, and that footprint carries per-item state the vault needs, not merely a presence signal (§14). That is a second, independent detection channel, mechanical-live, and lane 0 uses both.

### 6.2 Obsidian plugin

| Leg            | Mechanism                                                                                                             |
| -------------- | --------------------------------------------------------------------------------------------------------------------- |
| install        | file drop into `<configDir>/plugins/<id>/` plus the id in `community-plugins.json`, or BRAT                           |
| pin            | BRAT's `pluginSubListFrozenVersion` — the only route Obsidian's own documentation endorses — **proposed, pending T5** |
| verify / drift | `<configDir>/plugins/<id>/manifest.json` `version` — **proposed, pending T5**                                         |

`pin_semantics`: **held** on the BRAT route; **verified-against** on the file-drop route, which freezes nothing and only permits a comparison.

Two constraints, both **read**: the config directory is user-overridable, so no path may be hardcoded; and restricted mode is gated by a key in Obsidian's Chromium localStorage, **outside the vault**, so a purely file-based installer silently no-ops on a fresh vault. Restricted mode is a **setup precondition**, not a check.

**There is no research-vault Obsidian vault on this machine** (measured). Every Obsidian fact gathered so far describes a sibling project's vault. `research_vault/templates/vault/` ships 15 files and **none under `.obsidian/`**, so the scaffold produces a vault Obsidian has never configured, while shipping two `.base` files whose minimum Obsidian version is recorded nowhere. Lane 3a opens by creating the vault this class is about, which is also what unblocks T5.

### 6.3 Claude Code plugin or skill

`pin_semantics`: **held**, by sha.

The mechanism this class should adopt is under construction in the sibling `agent-plugins` repository and does not yet exist: no `bin/`, no `upstream/skills.json`, no `upstream-watch.yml`, gates S1–S5 unverified, doctor exit semantics unspecified, no rollback story (read, §14). We borrow a **design**, and this spec says so rather than inheriting an unbuilt thing as though it were proven.

Blocking stalls lane 1 on another project's schedule; building our own violates the priority order for a class about to have an owner. **Chosen: an interim** — a sha pin in the marketplace entry, plus `git ls-remote` for drift. Two lines, not a build.

**Handoff condition**, carried in the register's header block: when `agent-plugins` ships `bin/setup` and `bin/doctor` with gates S1–S5 verified, research-vault adopts them, and the interim row is closed with `superseded_by_row` — never deleted.

Our two extra classes — Zotero profile-file pinning and Obsidian BRAT freezing — are requirements that sibling's spec never considered. They are filed upstream while it is still in design (#103, #104, #113–115 are the existing pattern), rather than discovered as a mismatch after it ships.

### 6.4 Python dependency

`pyproject` plus a lock; `pin_semantics`: **held**, by the lock. The mechanism is standard; **the lock does not yet exist** — measured 2026-09-05, no lock file in the tree, and `pyproject.toml:18` pins `pypdf>=4` as an open range. Generating it and pinning the optional groups is §15.15.

### 6.5 An unpinned installer already ships

`research_vault/scaffold.py:23` declares `PROVISION_COMPANIONS = ["kepano/obsidian-skills"]`, and `skills/setup-vault/SKILL.md:42` instructs `claude plugin install kepano/obsidian-skills`. No version, no pin, no drift check. The problem this spec exists to solve is live in the package, and it is register row zero.

## 7. Lanes

### 7.0 Lane 0 — substrate audit

Executed **inside this spec**, by an agent under author review, before the register opens. Measurement, not selection, so it has no lane dependencies — but §8's cold-start contract depends on it, because a register with no rows is not a starting state.

It exists because lanes 1 and 2 are otherwise circular: capture must parse and preserve what plugins wrote, and which plugins to keep depends on what capture consumes.

Output: what is installed, what is active, and **what grammar is already in the library**, using both detection channels from §6.1. The unit is the 23 installed addons, not the 12 the author named — a distribution with an undispositioned remainder has no drift semantics.

Two grammar facts already measured, which are requirements rather than risks:

- **The library already carries both generations of attachment-scanner's signal**: `#nosource` (146 items), `#broken` (3) and `#duplicate` (2) from the simple preset, and `❌ nosource` (154), `🚫 broken` (4) and `❓ nonfile` (1) from the emoji preset configured at `prefs.js:32-35`; `‼️ duplicate` has not been written. **134 items carry both `#nosource` and `❌ nosource`** — the same fact told twice. Capture reads both generations and de-duplicates; it never recomputes the judgement, which is attachment-scanner's to make.
- **PMCID and PMID arrive as Extra lines, not tags** — measured today: zero of 2,673 tags are identifier-shaped, while sampled top items carry `PMCID: …\nPMID: …` in Extra. Held provisionally: `extensions.zotero.pmcid.tags` was enabled in the same session, so this is lane 0's starting picture, not what the plugin will write going forward (§15.5).

**Tag-vocabulary control is a lint obligation, not an idea.** 2,673 tags, of which 1,526 are manual and 1,147 automatic; a normalisation scan finds **280 near-duplicate clusters covering 627 tags** — 23% of the vocabulary — from case, number, separator and abbreviation variance. Two jobs, not one: **normalise at read** (a canonical map in capture; covers both kinds, survives re-import, zero writes, reversible) and **canonicalise at rest** (durable only for the 1,526 manual tags, since automatic ones regrow on refresh; irreversible, because a Zotero rename merges on collision and leaves no record of the original form — export the tag→item map first). Application at rest is `adopt`, not `build`: Zotero's native tag rename merges on collision, and Zutilo 4.2.2 is already installed with bulk tag operations. The agent's contribution is clustering and proposal, which needs no writes.

### 7.1 Lane 1 — capture and compile, together

The author's original items 2 and 3 are one lane. They share the capture→compile seam, which is the seam the previous design broke, and deciding them apart forces a re-run.

Lane 1 fixes the seam contract: capture preserves the Extra field byte-identical, reads a **declared** tag vocabulary, and writes the compile input in a format the engine it chooses accepts.

### 7.2 Lane 1 open item — URL-only sources

The claim that a URL-only entry gains nothing from Zotero is right about organisation and wrong about three things. **Identity**: a cited URL needs a bibliography entry with an accessed date, and only Zotero plus Better BibTeX mints one here. **Link rot**: this is the one source class that disappears, and `research_vault/archive.py` — sole writer of `archive-url`, Wayback-confirmed, four-state honest — already answers it and keys on the citekey, so skipping Zotero leaves it nothing to key on. **PRISMA**: PRISMA-S covers grey literature and web searching, and a scoping review citing a source whose provenance it cannot report fails its own checklist.

**Proposed cut**: cited or plausibly cited → Zotero; consulted only → no item, never citable. A wrong save costs a junk item attachment-scanner already cleans; a wrong skip costs an unrecoverable dead link. If consulted-not-cited volume becomes noise, the remedy is Zotero-side, never a second identity system. Lane 1 confirms or overturns it, and the row also decides whether `archive.py` survives §11's audit.

### 7.3 Lanes 2–4

| Lane | Scope                                                                | Notes                                                                                                                                                                                                                                           |
| ---- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2    | Zotero plugins                                                       | a choice *within* lane 1's contract, measured against 10.0.1, over all 23 installed plus the author's named not-installed candidates                                                                                                            |
| 3a   | Obsidian vault creation and seam-free plugins                        | opens by creating the vault that does not exist (§6.2); unblocks T5                                                                                                                                                                             |
| 3b   | Obsidian plugins that read Zotero — ZotLit, `obsidian-reference-map` | decided inside lane 1's seam contract, after lane 2 pins Better BibTeX                                                                                                                                                                          |
| 4    | Skills curation — MedSci, K-Dense                                    | screens candidates against §4's floors: PRISMA-S, PRISMA-ScR and the ACM guidelines. **Not blocked** on issues #117 and #119 — a checklist screens components whether or not the step spec exists — though their output would refine the floors |

Lanes 2 and 3a are seam-free and may run concurrently. Lane 1 must not be split. Lane 3b is **not** seam-free: `obsidian-reference-map` requires Better BibTeX's local server and is reported broken against BBT 9.0.57+, a hard dependency on a lane-2 component at a version lane 2 has not pinned.

Each lane runs as a **scoping review**: a bounded question, a screened candidate set, recorded exclusions. That builds the scoping-review method by using it, and yields the well-formed evidence this repository's prior-art notes were reaching for without the terminology. ("Scoping review" therefore names both a workflow step in §5.0 and the method a lane runs; where it matters, the step is written `scoping-review`.)

**Lane 2's inherited evidence is wrong in a specific way.** The 36-repository catalogue read **repository manifests**; the machine runs **shipped `.xpi` manifests**, and they differ — `zoterotldr` and `scite` are both active on 10.0.1 while the catalogue records ranges that would refuse them. Seventeen catalogue rows say "loads on 9.0.6"; none mentions 10.0.1. Lane 2 re-measures loadability from the installed `.xpi`.

## 8. Cold-start contract

A session opening lane N reads exactly: the component register, this spec in full, and the closed scoping reviews of every lane this one depends on. Lane 0 has no prior lane. The spec is one file, and reading it whole is cheaper than adjudicating which section a column needs.

That list is named in the register's header block and budgeted in lines. **Doctor** (§9) fails if the list points at anything marked `historical` or `pending-map`; the status linter (§10) runs before the register exists and cannot see the list.

The contract exists because the expensive part of entering this repository is not reading volume, it is inferring which material still binds. The register answers that in one screen.

## 9. Setup, doctor, drift, and the upgrade act

**A doctor already exists, and it repairs before it probes.** `research_vault/scaffold.py:322` calls `scaffold_vault(vault)` unconditionally, then returns eight probes — tree, machine-config, zotero, bbt, autoexport, staleness, remote, backup — and **none concerns an installed component**. This spec extends it rather than starting a second one, and separates the two acts: the component checks are read-only and run in a `--check-only` mode that skips the scaffold write, so §6.1's "no write from research-vault" survives and drift cannot be repaired away before it is reported. Adopt-over-build applied to our own code.

**Doctor runs in two phases and reports which it completed, per substrate app.** The live phase needs the relevant app up — four of the eight existing probes already fail `zotero down` without it, and the Obsidian CLI needs the desktop app running. The cold phase needs that app down. A cold check attempted while its app is running reports `SKIPPED — <app> running`, never a stale `MATCHED`, and doctor states which apps it found running so a partial run is never mistaken for a clean one. Doctor gains, per §6:

- the Zotero pin verification pair — cold;
- the per-plugin triple, **proposed, pending T3** — cold for presence and version, live for effects;
- the Obsidian manifest version read, **proposed, pending T5** — cold;
- the Claude Code sha comparison via `git ls-remote`;
- a merge check for the Zoplicate path (§15.3).

Doctor's exit semantics are **open** — the borrowed spec never states them, so any behaviour assumed here would be our own design wearing borrowed clothes (§15.1). **Rollback is open too** (§15.2): the borrowed spec has no rollback story for a failed setup or update, its only rollback text covers a one-time marketplace cutover, and setup as designed is forward-converging with no inverse.

### 9.1 The upgrade act

A distribution that pins four classes must say how a pin is deliberately moved. Per class: **bump** the pinned identifier, **re-verify** by that class's verify leg, **revert** to the prior row if verification fails. The register records it as a new row with the old row closed via `superseded_by_row` — never an in-place edit, and never a deletion. Blocked on §15.2, because revert has no defined mechanism yet.

## 10. The status-marking pass

Runs before this spec's lanes, as its own bounded task with its own approval. Nothing moves, nothing is deleted.

Scope, measured after the pass ran: **180 markdown files** — `docs/` 106, `.superpowers/` 71, root 3. The figure this section first carried, 202, predated the `skills/` exclusion below.

**The pass writes a second, distinct line and does not touch the existing `Status:` line.** That line's vocabulary (`accepted`, `suspended`, `draft`, `APPROVED`, `SUPERSEDED`) is a lifecycle axis this pass has no business overwriting — §2 depends on ADRs 0004 and 0005 still reading `suspended`. The new line is `Disposition: <value> (<date>)`, written **immediately after the document's first heading of any level** (`^#{1,6}\s`), with top-of-file as the fallback for the four files that carry no heading at all. `CLAUDE.md` is out of scope by name: it is an 11-byte import directive, not a document.

**No frontmatter route, because `skills/` is out of scope.** An earlier draft put the marker in a `disposition:` frontmatter key for files opening with YAML, and was rejected for shipping a repo-internal marker into an installed plugin. The body route that replaced it shipped one too — as the first line of nine `SKILL.md` prompt bodies — which this pass's own review caught. `skills/**` is therefore excluded outright, on the rule the exclusion list now runs on: **does this path ship to a consumer?** `research_vault/templates/**` ships and was already excluded; `skills/**` ships and now is. Nothing in scope opens with YAML, so the frontmatter question has no remaining member.

**The any-level anchor is a measurement, not a preference.** Twenty-one in-scope files — the `.superpowers/sdd/…/task-*-brief.md` set — open at `###`, so a `^#\s` anchor would have no anchor for them. Only the four bare-prose `docs/research/**/README.md` files carry no heading of any level. Two classes, not three.

Closed vocabulary, with a precedence rule because more than one value can fit — **first match wins, in this order**:

| Status                    | Test                                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------ |
| `sibling-project`         | belongs to another product's register                                                |
| `superseded-by: <path>`   | an explicit supersession already exists                                              |
| `pending-issue: <number>` | disposition belongs to a tracked issue — ADRs 0004 and 0005 are `pending-issue: 116` |
| `historical`              | a dated pass that closed — evidence, never a live decision                           |
| `pending-map`             | disposition needs the register                                                       |
| `current`                 | still binding                                                                        |

`pending-map` and `pending-issue` are load-bearing. Without them the pass guesses the dispositions it was sequenced to avoid, and the two documents §2 singles out fit no other value.

Orthogonal flag, not a status: `should-be-scoping-review`. A document may be `historical` **and** flagged as a scoping review the workflow should later replace. That flag produces the test-case set.

**Issues are in scope too.** The 66 open issues get a parallel one-word disposition — `absorbed-by: <spec §>`, `superseded`, `still-open`, `pending-map` — under the same linter. #96, #97, #62, #63, #78 and #118 are the first six to close against this spec; #116, #117 and #119 stay open and are named in §2, §4 and §7.3.

Three premises the pass started with were false, and it is scoped to the corrected ones (all measured):

- The named siblings — the coaching apps, the ADHD pilot, archify, Memoria — own **zero** files in the main tree. The sibling that does own files is `software-development`/`sensemaking`, whose **six** documents self-declare it. The figure this section first carried, two, came from a filename regex rather than a content test.
- `superseded` is a **domain term for source state** here, not a status marker. Explicit document-to-document supersession is **one whole-document pair**, not the 44 a naive grep suggests and not the three this section first carried — the other two are section-scoped.
- The `.superpowers/sdd/` workspace is retained-and-closed by deliberate commits, not abandoned.

**Its own linter**, per this repository's rule that a mechanical process gets a mechanical check: every `.md` in scope carries exactly one `Disposition:` line, positionally defined as the first line matching `^Disposition:` within the five lines after the document's first heading of any level, or at top of file for the four headingless ones; every `superseded-by` target resolves. `Status:` lines elsewhere in a body are out of scope, so the six sdd review files whose per-finding verdicts read `Status: **CONFIRMED.**` do not fail it.

**Scope bound.** The pass marks documents. The material that most often goes stale here is **environment facts**, and `AGENTS.md` already carries the rule for those. §1's shelf-life clause is where environment staleness is handled; the pass does not duplicate it.

## 11. Code disposition audit

Measured inputs: 29 modules and 10,597 lines in `research_vault/`, plus 847 lines in three `hooks/` files that no verb reaches; 21 CLI verbs; 45 test files and 24,571 lines; 25 mutation sidecars of which 18 are stale against their own declared source hash.

**The audit unit is the verb, not the module.** Only nine of the 29 modules are named by a verb; the other twenty serve only transitively, and nine of those are not imported by the CLI at all. `frontmatter` is imported by 12 modules and `pathcodec` by 10, so every module transitively "serves" something and a module-level criterion never cuts. The import graph is also blind to real coupling: `hooks/stop_publish_gate.py:15` matches `research_vault/publish.py:36` by filename, not by import.

Each verb receives a one-line disposition against §5.0's step map: **serves step X**, **serves the distribution mechanism** (setup / doctor / drift — `probe`, `doctor` and `scaffold` are known members), **serves a deferred step**, or **serves nothing**. The fourth value is required by this spec's own commitments: §9 keeps `doctor`, §6.5 makes `scaffold` register row zero, and `AGENTS.md` makes `probe` the sanctioned source of environment facts. Deletion follows the disposition; the disposition is a recorded judgement, never a silence.

Two cautions:

- **"Preserve the mutation suite where its subject survives" must not preserve rot.** 18 of 25 sidecars are already stale, and the plan that retires them (`docs/superpowers/plans/2026-08-24-plan-w-quality-tail.md`) has unchecked steps. The audit dispositions the sidecars alongside the code.
- **Coverage data is unusable and must be regenerated.** The local `.coverage` resolves against `/home/eranr/New folder/research_vault/`, a foreign checkout — the wrong-tree trap `docs/testing.md` warns about. It is not committed, so the remedy is deleting a stale local file, not stripping the repository. "Does this verb actually run" has no data until a fresh run.

## 12. Cutover: going public

**Chosen.** It closes the marketplace-bootstrap item, since the bootstrap against a private repository was never tested. §15.1, §15.2 and §15.10, and §6.3's handoff, remain open against the Claude Code class.

Three preconditions, all measured, none blocking the decision and all blocking the flip:

1. **260.6 MB (248.5 MiB) of raw Claude Code session transcripts sit in git history** — 120 `.jsonl` blobs under `docs/research/raw/*transcripts*`, the largest at 32 MB, 32 MB and 23 MB. Untracked today; present in every clone forever. Publishing the repository publishes everything those sessions saw.
2. **Eight PDFs were committed and later removed.** Four are 2026 copyrighted papers, one a 2014 journal article, the rest US-government ICD/ICS documents. All eight lived in `sources/`; commit `52bc0fb` (2026-08-27) removed them and gitignored the folder in one act, which fixes the working tree and not the history — those are the paths a rewrite must strip. The ISO standards the folder holds now were added afterwards and were never committed.
3. **The current tree carries what neither route removes.** `docs/research/2026-09-04-import-sourcing.md` reproduces verbatim source text from candidate repositories, eight of which record no LICENSE file — all-rights-reserved by default — and 15 tracked files carry the author's absolute local paths. A history rewrite and a squashed tree both preserve HEAD. Reduce the unlicensed candidates to citation plus paraphrase, and sweep the paths.

Route: a history rewrite before the flip, or a fresh public repository from a squashed tree. Its own task with its own approval, not work that rides along inside a lane.

## 13. Tracers

A tracer is one cheap check that can falsify a decision, run before the decision is built on. Two of the four classes currently have mechanisms declared on tracers that have not run; those legs are marked **proposed** in §6 rather than asserted.

|     | Tracer                                                                                                                                                          | Result                                                                                                                              |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| T1  | enumerate installed Zotero plugins with no GUI                                                                                                                  | **passed** — `extensions.json` is plain JSON and carries every field needed                                                         |
| T2  | is plugin auto-update on                                                                                                                                        | **answered by author action, not by tracer** — it was on; now `false` at `prefs.js:49`. §6.1 records what this leaves unestablished |
| T3  | doctor's per-plugin triple on one plugin, before screening many                                                                                                 | **open** — §6.1 and §9 depend on it                                                                                                 |
| T4  | status linter over a hand-marked sample                                                                                                                         | open                                                                                                                                |
| T5  | Obsidian plugin version readable by file                                                                                                                        | **open, blocked on §6.2's missing vault** — §6.2's pin and verify legs depend on it                                                 |
| T6  | install from zero on a scratch vault: setup establishes the Zotero hold pin and the BRAT freeze on a machine that is not the author's, then doctor reports both | open, post-spec — falsifies §6.1's `held` and §6.2's pin leg                                                                        |

"Cutover" is reserved for §12. A tracer that would have written to the author's Zotero profile (`user.js`) was **cancelled** when the author's toggle answered T2; §15.14 carries what that leaves open.

## 14. Mechanism claims and their sources

Zotero runtime rows re-measured 2026-09-05 evening, after the author enabled PMCID auto-fetch and re-enabled Zoplicate. Read-only throughout.

| Fact                             | Value                                                                                                                                                                                                                                                                                                                                                                               | Established                                                                                  |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Zotero, Better BibTeX            | 10.0.1 on Windows; BBT 9.0.63; local API reachable from WSL2                                                                                                                                                                                                                                                                                                                        | live probe 2026-09-04, re-confirmed 2026-09-05                                               |
| Zotero has run 10.0.1 since      | `compatibility.ini` `LastVersion=10.0.1_20260824184713`, mtime 2026-08-26; `prefs.js:39` `extensions.lastAppVersion = "10.0.1"`                                                                                                                                                                                                                                                     | measured                                                                                     |
| Zotero profile                   | `…/AppData/Roaming/Zotero/Zotero/Profiles/881hrcxd.default`, sole profile per `profiles.ini`                                                                                                                                                                                                                                                                                        | measured                                                                                     |
| Zotero data directory            | `D:\Zotero` per `extensions.zotero.dataDir`, not the Windows default                                                                                                                                                                                                                                                                                                                | measured                                                                                     |
| `extensions.json`                | plain JSON, schemaVersion 37, 23 addons, each with id, version, `active`, `userDisabled`, `appDisabled`, `applyBackgroundUpdates`, `targetApplications`                                                                                                                                                                                                                             | measured                                                                                     |
| addon states                     | **13 active, 9 user-disabled, 1 app-disabled**; the app-disabled one is `zoteroshortdoi` 1.6.0                                                                                                                                                                                                                                                                                      | measured, after the author's re-enable                                                       |
| `zoteroshortdoi` 1.6.0           | `appDisabled=true`; manifest caps `9.0.*`. The ingest spec's "6.0 to 7" is stale; the conclusion is not                                                                                                                                                                                                                                                                             | measured                                                                                     |
| auto-update, before the toggle   | both prefs absent; defaults `true` read from `omni.ja` `defaults/preferences/zotero.js`; `applyBackgroundUpdates=1` on all 23. A daily background check runs near 17:33:53Z, and 13 of 23 carry stamps in a ~11-second time-of-day band across dates from 2026-08-05 to **2026-09-03**, the most recent — corroborated by matching `.xpi` mtimes. It did **not** fire on 2026-09-05 | measured                                                                                     |
| auto-update, after the toggle    | `prefs.js:49` `extensions.update.autoUpdateDefault = false`; still no per-addon override — the value set across all 23 is `{1}`                                                                                                                                                                                                                                                     | measured                                                                                     |
| `addonStartup.json.lz4`          | mozLz4 container, no decoder available; unnecessary, `extensions.json` carries the same fields                                                                                                                                                                                                                                                                                      | measured                                                                                     |
| plugin enumeration over the wire | none — `/api/` answers 200 with the stub body `Nothing to see here.` and every enumeration path under it 404s; BBT JSON-RPC's 14 methods expose nothing                                                                                                                                                                                                                             | measured                                                                                     |
| plugin **effects** over the wire | `/api/users/0/tags` returns 2,673 tags (the endpoint pages at 100; this is a full walk). Both attachment-scanner generations are present: `#nosource` 146 items, `#broken` 3, `#duplicate` 2, `❌ nosource` 154, `🚫 broken` 4, `❓ nonfile` 1, `‼️ duplicate` 0. **134 items carry both `#nosource` and `❌ nosource`**                                                            | measured, two independent runs                                                               |
| tag vocabulary                   | 2,673 tags: 1,526 manual (`type 0`), 1,147 automatic (`type 1`). A case/number/separator normalisation finds 280 near-duplicate clusters covering 627 tags                                                                                                                                                                                                                          | measured                                                                                     |
| identifier tags                  | zero of 2,673 tags are identifier-shaped; sampled top items carry `PMCID:`/`PMID:` in Extra. Provisional — `pmcid.tags` was enabled in the same session                                                                                                                                                                                                                             | measured                                                                                     |
| attachment-scanner               | 0.5.1 active; `prefs.js:28-31` `monitor_attachments`, `remove_pubmed_entry`, `remove_snapshot`, `scan_nonfiles` all true; `prefs.js:32-35` configures the emoji preset. The author reports long use with no loss of needed files, only browser-plugin byproducts; the finding that survives is the two-generation grammar, not a data-loss risk                                     | measured; author 2026-09-05                                                                  |
| PMCID fetcher                    | 1.0.3 loads; `prefs.js:111` `extensions.zotero.pmcid.auto = true` — **auto-fetch is on**; `prefs.js:113` `extensions.zotero.pmcid.tags = true`                                                                                                                                                                                                                                      | measured, after the author enabled it                                                        |
| Zoplicate                        | 5.1.1, **active** (it had been user-disabled by mistake); manifest `8.999–10.0.*`, AGPL-3.0                                                                                                                                                                                                                                                                                         | measured; author 2026-09-05                                                                  |
| attachment-scanner manifest      | `6.999`–`*`, MIT, read from the released `.xpi`                                                                                                                                                                                                                                                                                                                                     | read                                                                                         |
| Zotero 10 local API writes       | POST/PUT/PATCH/DELETE for items, collections and saved searches, plus tag deletion, full-text writes and file uploads; reads unauthenticated, writes need a runtime key from `POST /api/local/authorize` behind a confirmation dialog. No key exists — `localAPIKeys.json` is absent                                                                                                | read (`docs/research/2026-09-05-zotero-api-reading.md:47-75`); absence measured              |
| collection membership            | carried only by the item; `Zotero.Collection.toJSON` emits no roster; no collection-items write endpoint, and the local API returns **405** for `/collections/<key>/items`. Filing an item is a GET-then-`PATCH` of the item, `collections` as a complete list, 412 race between                                                                                                    | read (`collection.js:827-838`, `server_localAPI.js:1050-1066`); 405 read from the route gate |
| local-API `PATCH` hazard         | runs `fromJSON(merged, {strict: false})`, enabling Extra migration — can move `Extra:` lines into empty real fields, rewrite Extra, flip `itemType` on a recognised `type:` line, and bumps `dateModified` and `clientVersion`. 2,723 of 2,844 items are at version 0                                                                                                               | read (`server_localAPI.js:1973-1999, 2195-2226`; `item.js:5634-5676`); counts measured       |
| sync undoes removals             | member properties including collections and tags are combined on sync, "so any removals will be automatically undone" — reconcile-by-absence is unsound across devices                                                                                                                                                                                                              | read (`syncLocal.js:1926-1930`)                                                              |
| Zoplicate merge path             | imports `mergeItems.mjs` directly, never `Zotero.Items.merge` — the shim BBT monkey-patches — so a merge **skips BBT citation-key consolidation**; loser's collections and tags union onto the master, loser trashed with memberships intact (55 trashed items still hold a live membership)                                                                                        | read (`mergeItems.mjs:46, 49-70`); count measured                                            |
| markdb-connect state             | installed and configured, tag `ObsCite` on 3 items. `mdbc.removetags` unset → defaults to the destructive `keepsynced`; `sourcedir` `C:\Users\eranr\Memoria-test\20-sources\01-papers` whose parent does not exist; `obsidianvaultname` `research-wiki`; `yamlkeyword` `citekey`. A run today strips the 3 tags                                                                     | measured; branch read from `mdbc.js`                                                         |
| catalogue staleness              | compatibility judged against Zotero 9.0.6; 17 of 36 rows say "loads on 9.0.6", none mentions 10.0.1; the catalogue read repository manifests while the machine runs shipped `.xpi` manifests, and `zoterotldr` and `scite` differ                                                                                                                                                   | measured                                                                                     |
| existing doctor                  | `research_vault/scaffold.py:322` calls `scaffold_vault(vault)` unconditionally before returning eight probes — tree, machine-config, zotero, bbt, autoexport, staleness, remote, backup — none about installed components; four of them fail `zotero down`                                                                                                                          | read                                                                                         |
| unpinned installer               | `scaffold.py:23` `PROVISION_COMPANIONS = ["kepano/obsidian-skills"]`; `skills/setup-vault/SKILL.md:42`                                                                                                                                                                                                                                                                              | read                                                                                         |
| borrowed mechanism               | `agent-plugins` has no `bin/`, no `upstream/skills.json`, no `upstream-watch.yml`; gates S1–S5 unverified; doctor exit semantics unspecified; no rollback story                                                                                                                                                                                                                     | read                                                                                         |
| Obsidian pinning                 | BRAT `pluginSubListFrozenVersion` (`src/settings.ts`) is the only documentation-endorsed route; `manifest.json` `version` is the only installed-version record; restricted mode is gated in Chromium localStorage outside the vault                                                                                                                                                 | read, docs.obsidian.md and the BRAT source                                                   |
| no research-vault vault          | Obsidian knows only sibling vaults; `research_vault/templates/vault/` ships 15 files, none under `.obsidian/`                                                                                                                                                                                                                                                                       | measured                                                                                     |
| corpus                           | 180 `.md` in scope after the `skills/` exclusion (`docs/` 106, `.superpowers/` 71, root 3); one whole-document supersession pair; six documents self-declare the sibling; the named siblings own zero main-tree files                                                                                                                                                               | measured                                                                                     |
| issues                           | 66 open; none older than 2026-08-25 by `updatedAt`, an instrument comment and label edits also bump                                                                                                                                                                                                                                                                                 | measured                                                                                     |
| code                             | 29 modules / 10,597 lines in `research_vault/` (`hooks/` is a further 847 lines in 3 files, excluded from that count); 21 verbs; 9 modules named by a verb, 9 reachable only transitively; 45 test files / 24,571 lines; 25 sidecars, 18 stale                                                                                                                                      | measured                                                                                     |
| Python pin                       | no lock file in the tree; `pyproject.toml:18` `pypdf>=4`                                                                                                                                                                                                                                                                                                                            | measured                                                                                     |
| coverage data                    | the local `.coverage` resolves against `/home/eranr/New folder/research_vault/` — a foreign checkout, unusable; not tracked in git                                                                                                                                                                                                                                                  | measured                                                                                     |
| git history                      | 120 transcript blobs totalling 260.6 MB (248.5 MiB); 8 PDFs added in `3719086` and removed in `52bc0fb`, all under `sources/`; `sources/` gitignored with 0 tracked and the ISO standards never committed; 15 tracked files carry absolute local paths                                                                                                                              | measured                                                                                     |

## 15. Open items carried forward

01. Doctor's exit semantics (§9).

02. Rollback for a failed setup or update, which also blocks §9.1's revert leg.

03. **The Zoplicate merge path, now a measured hazard rather than an inferred one.** Zoplicate imports `mergeItems.mjs` directly and never calls `Zotero.Items.merge` — the deprecated shim Better BibTeX monkey-patches — so **a Zoplicate merge skips BBT's citation-key consolidation** (read, `mergeItems.mjs:46, 49-70`). The merge union-merges the loser's collections and tags onto the master, records `dc:replaces`, and trashes the loser without stripping its memberships; 55 trashed items still hold membership in a live collection (measured). Since the citekey is the vault's identity, a merge can leave the survivor keyed differently from the vault note whatever the vault wrote. Zoplicate is active as of 2026-09-05. Lane 2 owns the fix; doctor's merge check (§9) is the interim detector.

04. URL-only sources — cited versus consulted (§7.2).

05. What the PMCID fetcher writes going forward, now that `pmcid.tags` is on: Extra lines, tags, or both (§7.0).

06. The `.py.manifest.json` sidecars: retire with mutate4py, or keep (§11).

07. Zoplicate merge semantics (item 3) are the open part; duplicate detection itself now has an owner, while `zotero-format-metadata` detects and reports but does not merge.

08. The glossary and the two suspended ADRs — handed to issue #116 (§2).

09. The remaining 11 of 23 installed addons, undispositioned, including one that copies attachments to a OneDrive path (§7.0).

10. The `upstream-watch` schedule: the borrowed spec names a scheduled workflow and gives no interval (§6.3).

11. The `long-form` **step** has no lane and no issue. The ACM guidelines themselves are owned — they are one of lane 4's screening floors (§4) — but nothing schedules the step they bind.

12. The `daily-log` step has no lane, no register row and no issue; `research_vault/appendlog.py` is its only carrier and enters §11's audit named by no verb (§4).

13. Whether either substrate app flushes its files fully only on exit (§3.3). Zotero's `prefs.js` and `extensions.json` were both observed rewritten while it was running, so the cold-read precondition is provisional there. The Obsidian half is unmeasured entirely — `manifest.json` and `community-plugins.json` write cadence is unknown, and its localStorage LevelDB gives evidence on presence but never on absence while the app is live.

14. A mechanical route to establishing the Zotero pin on a machine that is not the author's — un-cancel the `user.js` tracer, or specify the wizard step that replaces it (§6.1, §13).

15. The Python lock does not exist; `pypdf>=4` is an open range (§6.4).

16. **Vault-owned state inside Zotero — answered: strict one-way now, no collection subtree.** The requirement is real and is a PRISMA-ScR obligation, not a convenience: a scoping review's item set must be reachable as a set, because the flow counts depend on it. The collection route is nonetheless rejected, on a measured write surface.

    **Collection membership is carried only by the item.** `Zotero.Collection.toJSON` emits `{key, version, name, parentCollection, relations}` and no roster; there is no collection-items write endpoint, and on the local API `/collections/<key>/items` is routed to the Items endpoint whose write gate returns **405** for that path (read: `collection.js:827-838`, `server_localAPI.js:1050-1066`). Filing an existing item therefore means GET-then-`PATCH` of the **item**, with `collections` sent as a complete list, and a 412 race between the two calls. Worse, local-API `PATCH` runs `fromJSON(merged, {strict: false})`, which enables Extra-field migration: a membership-only patch re-runs Zotero's normalisation over a record the vault merely read — it can move `Extra:` lines into empty real fields, rewrite Extra, change `itemType` if Extra carries a recognised `type:` line, and bumps `dateModified` and `clientVersion`, marking the item for sync upload. 2,723 of 2,844 items sit at version 0 today; every filed item leaves that state.

    So the author's additivity insight is **correct about collection objects and irrelevant to membership** — tags are equally additive, so it does not discriminate between routes. The subtree is a small owned surface; the membership is not, and it costs the same per item as a tag while buying nesting the vault's two or three flat facets do not need.

    **What is chosen for now: nothing.** The repository contains no literature notes, so there is no vault state to project. This matches the prior art's own recommendation.

    **When presence becomes worth showing**, the route is a single tag through **markdb-connect, which is already installed** — `item.addTag; saveTx()`, no `strict:false`, no API key, no authorize dialog, and no vault code. Its gating unknown is whether Windows-side Zotero can enumerate a `\\wsl.localhost\…` path; if not, the route collapses to the vault writing the tag itself over the local API, with the full hazard set above.

    **It is currently misconfigured in a destructive direction**, and this must be fixed before it is ever run: `mdbc.removetags` is unset and therefore defaults to `keepsynced`, the branch that removes tags for notes it cannot find; `sourcedir` is `C:\Users\eranr\Memoria-test\20-sources\01-papers`, whose `20-sources` parent does not exist; `obsidianvaultname` is `research-wiki`; and `yamlkeyword` is `citekey` where this spec standardises on `citationKey`. A run today would enumerate zero notes and strip the 3 live `ObsCite` tags — issue #31's data-loss mode, armed on this machine (all measured 2026-09-05).

    **Route-independent failure mode, and it is the one that bites:** Zotero sync states that member properties including collections and tags are combined, *"so any removals will be automatically undone"* (read, `syncLocal.js:1926-1930`). Any reconcile-by-absence loop is unsound across devices, whatever is written.

    Retained split if this ever opens: **scope** in Zotero, **screening state** in the vault, so one fact never gets two homes. A saved search needs no API write at all — the author saves one Advanced Search by hand — and buys negation and composition, at the cost of being structurally flat and not a drop target.
