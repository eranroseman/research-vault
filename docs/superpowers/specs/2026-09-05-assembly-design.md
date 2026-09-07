# research-vault as an assembly: obligations, component register, and lanes

Disposition: current (2026-09-06)

Status: draft for author review (2026-09-05), **amended 2026-09-06** — nothing here is decided except the rows marked **chosen**.

The amendment adds decisions 12–18 to §3 and rewrites §4, §5, §6, §7.3, §8, §9, §13, §14 and §15 under them. **§3's 2026-09-05 rows are not edited**: a decision reversed on a later day is recorded as a later decision naming what it supersedes, never as a rewrite of the earlier one. That is the `superseded_by_row` rule §5.1 applies to the register, applied to this document's own decisions.

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

It names no component winners. It fixes the **obligations** components answer to (§4), the **step map** and **register** that record what was chosen and point at why (§5), the **classes** each component belongs to and which of them can be pinned at all (§6), and the **lanes** that do the choosing (§7).

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

    Obsidian carries the sharper version of the same hazard: its restricted-mode gate lives in Chromium localStorage, whose LevelDB is only reliably read with the app closed — presence is evidence there, absence is not (§6.2). Whether either app's files are *fully current* only after exit is **open**: Zotero's two were observed rewritten while it was running (§15.13). *(The last sentence of this row read "The register's `tier` column carries which carrier a check uses." Decision 18 supersedes it: the carrier is a property of the check, and it moves to the probe.)*

04. **One assembly spec; lane 0 executed inside it, lanes 1–4 after it.** Not six lane specs up front, and not lane-local specs with the glue arriving last.

05. **Lane order is the dependency order in §7**: 0, then 1, then 2 and 3a concurrently, then 3b, then 4. *This supersedes the earlier choice of Zotero plugin curation as first lane* — curation produces a document, while a distribution's claim is install + pin + drift, and lanes 1 and 2 are mutually dependent until lane 0 breaks the cycle.

06. **A status-marking pass runs before this spec's lanes.** §10.

07. **Requirements are indexed, not translated.** §4.

08. **The build bar scales with embedded knowledge.** §5.2.

09. **Cold start is a spec requirement with a mechanical check.** §8.

10. **The repository goes public**, after §12's preconditions are met.

11. **URL-only sources: the cut is cited versus consulted.** Proposed with its evidence in §7.2; lane 1 confirms or overturns it. Not settled here.

**Chosen 2026-09-06.** Each names what it supersedes.

12. **Two of four classes cannot be pinned by us, and the spec stops claiming otherwise.** Claude Code and Python pin through mechanisms that already exist — a marketplace sha, a `ref` in `upstream/skills.json`, `pyproject.toml`. Zotero and Obsidian are **provisioned and observed, never held**: Zotero's plugin auto-update is on by default (measured, §14), it is a *global* preference covering plugins unrelated to this vault, and a guarantee that depends on a human keeping it off on every machine indefinitely is a guarantee in name only. *Supersedes §6.1's and §6.2's pin legs, and the `held` semantics claimed for both.*

13. **The build bar leaves this document.** It moves to `docs/agents/sourcing.md`, pointed to from `AGENTS.md`, because it is long and episodic — it fires only when a screen concludes `build` or `adapt`. A durable rule does not live in a spec that expires when the lanes finish. *Supersedes decision 08 and deletes §5.2.*

14. **The register carries facts and pointers, not justification.** Eight columns in `docs/component-register.md`. `pin`, `pin_semantics` and `provisioning` leave because each class's own registry holds them — and for two classes there is nothing to hold. `class` leaves because the registries partition the components between them, so the row need not restate which one a component is in. `candidates_screened` leaves because nothing in this document ever defined its contents, and `decided_by`/`decided_on` are subsumed by `decided_in`, which names a dated screen. *Supersedes §5.1's column table. `tier` also leaves, but for a reason this row got wrong — see decision 18.*

15. **Lanes run sourcing screens, not scoping reviews.** A scoping review is a research method over literature — a question, a search, eligibility screening, charting, a flow diagram. Choosing software against acceptance criteria is not that, and §7.3 previously admitted the collision (*"names both a workflow step and the method a lane runs"*) without fixing it. The repository's own prior art already uses the right word: `docs/research/2026-09-01-pre-spec-sourcing-screen.md`. `scoping-review` in §5.0 returns to meaning only the research method, owned by #119. *Supersedes §7.3's naming **and §10's `should-be-scoping-review` flag**.*

    The flag is the wider half. It is set on **42 documents** in `docs/document-dispositions.tsv`, and they are not one kind of thing: some are literature comparisons, but others — `docs/research/2026-09-01-pre-spec-sourcing-screen.md` most plainly — are sourcing screens, so the flag currently promises to replace them with a research method they were never an instance of. **The TSV is a reviewed artifact and this spec does not touch it**; §15.19 carries the split.

16. **No second setup mechanism.** research-vault extends `research_vault/scaffold.py`'s existing `doctor()` with a read-only `--check-only` mode. The sibling's `bin/setup` shape — declarations in-repo never read from the machine, one script with check as its second mode, a scratch `HOME` as a complete test fixture — is adopted as *principles*; the script is not copied, because this repository already has the thing it would duplicate. *Confirms §9 against a contrary proposal.*

17. **What the two unpinnable classes ship instead of a pin.** Zotero: a **table in `README.md`**, required and recommended, each row carrying its addon id — the human who runs the Zotero wizard reads the README, and the id column makes that same table the artifact doctor parses, so the human's list and the machine's list cannot disagree. Obsidian: a **seeded `.obsidian/` folder** in `research_vault/templates/vault/`, plugins installed and settings tuned, copied by scaffold into a new vault. *Supersedes `skills/setup-vault/SKILL.md:44`'s prose naming of two plugins without ids, which becomes a pointer to the table. Lane 2 populates the table; lane 3a produces the folder.*

    **The Obsidian half is blocked by packaging, measured 2026-09-06.** `pyproject.toml:56` declares package data as `templates/**/*`, and Python's `glob` does not match entries beginning with a dot: built against a template tree containing `.obsidian/plugins/demo/manifest.json`, that pattern returns **zero** matches under `.obsidian/`. A seeded folder would ship in a git checkout and be absent from an installed wheel — the linter green in CI, the class empty on a user's machine. The repository already works around this for files by storing them dotless and renaming on copy (`_DOTLESS_TEMPLATE_RENAMES`, `scaffold.py:70`), but that map is keyed on whole file paths and cannot rename a directory. Lane 3a must fix the packaging before it produces the folder, not after.

18. **`tier` was two columns wearing one name, and neither half belonged in the register.** Decision 14 removed it in one motion and justified the removal as "`tier` left with the pin legs it described" — true of nothing. The column named by decision 03 carried a check's **runtime carrier** (`gui`, `mechanical-live`, `mechanical-cold`); the tier the build bar reads is a **component's kind** (prompt-bearing, mature tool, glue). Removing one column silently removed two mechanisms' discriminators, which is the deletion test failing: the complexity did not vanish, it reappeared in three callers — the build bar, §9's two-phase doctor, and §5.1's linter.

    Each half now goes where the fact actually lives, rather than back into the register:

    - **The runtime carrier is a property of the check, not of the component**, so it belongs to the probe that runs it (§9). One component can be observed cold *and* live — §6.1's two detection channels are exactly that — which a single column on the component's row could never have expressed. Putting it there was the original error, and decision 03's placement is what decision 18 supersedes, not its content.
    - **The build bar's tier is a property of the screen's reasoning**, so the **sourcing screen declares it** and the linter reads it through `decided_in`. `docs/agents/sourcing.md` is where that rule lives (decision 13), so the tier table lives beside the rule that consumes it rather than in a register that decision 14 just emptied of justification.

    *Supersedes decision 03's placement of the carrier, and corrects decision 14's stated reason.*

19. **The lanes run next; infrastructure is built only where it blocks them.** Everything this spec's reviews surfaced — a doctor redesign, a register linter, a `check_metadata` split — is *developing*, and the nine-item route the author set out is *adopting*. The structural argument agrees with the priority argument: §9's five new probes are all for components **the lanes have not chosen yet**, so building the doctor now is building against a guess. Doctor's redesign, the seeded-tree hash and the `--check-only` mode wait for a lane to state what it needs. *Applies the author's standing order — adopt, then adapt, then develop — to this spec's own findings.*

20. **The register linter's third check is deleted, not narrowed.** *Supersedes §5.1's union-resolution rule in full.*

21. **Known quality debt is carried in the open rather than paid now, and CI is re-shaped to stay legible while it is.** Two functions sit above the CRAP ceiling. `_bump_generated` is a coverage gap in `archive.py`, **whose survival is open** — §7.2 makes lane 1's URL-only cut decide whether the module lives — so writing its tests now may test code about to be deleted. `check_metadata` is CC 37 at 100% coverage, so only a split moves it, and that is develop-work decision 19 outranks. **The ceiling stays 30**; `986086e` rejected moving it and this row does not reopen that.

    What changes is the wiring, because a hard-failing step made the debt indistinguishable from breakage: it failed 189 consecutive runs and **skipped every step below it**, so drywall and the mutation gate had not run since 2026-08-25, and a genuinely broken test read exactly like the standing debt — which is how a red suite shipped on 2026-09-06 unnoticed. The step is now `continue-on-error`, a dated deferral naming its own exit condition. Branch protection follows **after lane 4**, not before. *Supersedes §15.22's filing of the CRAP failure as an issue to open.*

22. **One spec and one plan open at a time, and every lane gets its own.** This document is the **decomposition plus lane 0**, and nothing more. Each lane then gets a spec of its own — through the full brainstorming cycle, not a section here — and each spec gets a plan of its own. The work-in-progress limit is **at most one open spec and one open plan at any moment**, which is what stops a second lane's design from being written against a first lane's unfinished contract. *Supersedes the reading of §7 in which the lanes are stages of this spec; they are successors to it.*

23. **Lane 1 runs first**, per §7.3's own text — lane 2 is "a choice *within* lane 1's contract" — and per the author's original route, which opens with the engine and the integration. The circularity that made lane 2 look primary was real and is already broken: lane 0 measured the tag grammar, both attachment-scanner generations and the Extra-field facts, so lane 1 has what it needed from lane 2 without running it. Lane 1's URL-only cut also decides `archive.py`, which is what unblocks decision 21's carried debt.

24. **The code disposition audit (§11) runs after each lane, including lane 0.** Not one sweep at the end: a verb's disposition depends on which steps survive, so the lane that decides a step dispositions the code serving it while the reasoning is still in hand. **Lane 0 is complete, so its audit is now due** — that is this document's own tail, not a future lane's. *Supersedes §11's implied single-pass timing.*

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

**Definitions the rest of the spec leans on.** A **floor** is a numbered *must* a lane writes into its **sourcing screen** before it screens candidates; this index's rows are its sources. `floor_failed` cites one by screen and number, and the register's linter rejects a value that does not resolve. The rule that requires musts to be numbered, and the build bar that requires a `build` verdict to cite one, live in `docs/agents/sourcing.md` (decision 13). A **re-run** re-opens a named lane against a candidate set the gap defines, and needs the author's approval.

**Gap pass.** Mechanically: every obligation in this index with no register row citing it (§5.1's `obligations` column). Run per-lane at close, then once at the end. A gap found at lane close is a floor amendment; the same gap found after every lane has run is a re-run.

## 5. The step map and the component register

### 5.0 The step map

The steps are the register's key domain, closed for this spec's lanes and extended only by an author decision:

`vault-setup`, `capture`, `compile`, `search`, `scoping-review`, `long-form`, `daily-log`, `publish`

§4 seeds it. Each lane appends the components that serve a step and may not invent one. A verb serving a step no lane covers is dispositioned `deferred`, never `serves nothing` (§11).

### 5.1 Register shape

**The artifact is `docs/component-register.md`** — a committed markdown table, the shape `docs/issue-dispositions.md` already proves: a human reads it on GitHub, a linter parses it, mdformat owns its form. The width objection that argued against a table at fourteen columns does not survive at eight: laying the eight columns out over the components §14 already names gives rows of roughly 110 characters, against the issue table's committed rows of 120 and more. That is an estimate over an artifact that does not exist yet, not a measurement, and it is written here as one.

Keyed on `(step, component)`, with an empty `step` permitted for a component that serves none. Lanes append rows and may supersede their own; a named header block carries what is not a row.

| Column              | Meaning                                                                             |
| ------------------- | ----------------------------------------------------------------------------------- |
| `step`              | the step served, from §5.0; may be empty                                            |
| `component`         | what serves it, or empty                                                            |
| `disposition`       | `adopt` \| `adapt` \| `build` \| `gap` \| `reject` \| `open`                        |
| `obligations`       | the §4 rows this component answers; the gap pass reads this column                  |
| `decided_in`        | the sourcing screen that decided it                                                 |
| `floor_failed`      | on `build` and `adapt`, the numbered must no candidate met, cited into `decided_in` |
| `superseded_by_row` | set when a later row replaces this one; rows are closed, never deleted              |
| `closed_on`         | the date the row was closed                                                         |

**Eight columns left the table** (decision 14). `pin`, `pin_semantics` and `provisioning` belong to the class's own registry (§6), and for Zotero and Obsidian no pin exists to record at all. `class` left because the four registries partition the components between them, so the row need not restate the partition. `candidates_screened` left because nothing in this document ever defined its contents — the screen's own candidate table is that record. `decided_by` and `decided_on` are subsumed by `decided_in`, which names a dated screen. `tier` left too, but not for the reason decision 14 first gave; decision 18 has it.

The register's linter checks two things: every `decided_in` resolves, and every `floor_failed` resolves to a numbered must inside its `decided_in`. That third check is what replaces holding a copy — the register and the registries are proved to agree rather than one restating the other.

**A third check was specified and is now deleted** (decision 20). It required every `component` to resolve in one of the four class registries. Written that way it rejected four of the six values in its own `disposition` column — a `build` row names something we wrote, and `gap`, `open` and `reject` rows may carry no component at all. Narrowing it to `adopt` and `adapt` made it correct and left it pointless: one caller, and what it buys is typo-detection the row's author performs while writing the row. Its deletion test says *vanishes* — four parsers, the exactly-one-hit arbitration and both error paths go with it, and nothing reappears anywhere.

Three of the four registries do not exist yet and two have no specified format at all, so the rule was written about artifacts before they had a shape. That is this document's own recurring defect wearing a mechanism's clothes. If the check earns itself once the registries are real, it can be written then, against something readable.

### 5.2 The build bar has moved

**Superseded by decision 13.** The rule — that a `build` or `adapt` verdict at the high bar must name the must no candidate met — now lives in `docs/agents/sourcing.md`, pointed to from `AGENTS.md` under `## Agent skills`.

It moved on two criteria. **Length**: it is a rule plus a three-tier table, far past the one sentence that makes inlining cheaper than pointing. **Frequency**: it fires only when a screen concludes `build` or `adapt` — the issue tracker's shape, not the design discipline's. And it moved *out of this spec* because a rule that outlives the lanes does not belong in a document that expires with them.

## 6. Component classes

Four classes, and — **decision 12** — not four pin mechanisms. Two classes carry pinning of their own that we use; two carry none we control, and for those the honest legs are **declare, provision, observe**. A distribution that says "pin" for a class it cannot pin is saying something false, which is worse than saying nothing.

| Class           | Pinned by us? | The mechanism, or what replaces it                                    |
| --------------- | ------------- | --------------------------------------------------------------------- |
| Zotero plugin   | no            | declared in `README.md`; installed by the human; observed by doctor   |
| Obsidian plugin | no            | declared and provisioned as a seeded `.obsidian/`; observed by doctor |
| Claude Code     | **yes**       | `marketplace.json` `sha`, `upstream/skills.json` `ref`                |
| Python          | **yes**       | `pyproject.toml`, plus a lock                                         |

The two unpinned classes are not thereby unmanaged. What we owe them is a **declaration** the human installs from and the machine reads, and a **verdict** — is what is installed the thing we asked for, and does it work. That is a weaker guarantee than a pin, and the register records it as one.

### 6.1 Zotero plugin (XPI)

| Leg     | Mechanism                                                                                |
| ------- | ---------------------------------------------------------------------------------------- |
| declare | a table in `README.md` — required and recommended, each row carrying its **addon id**    |
| install | human, Zotero UI — a setup wizard step                                                   |
| observe | doctor reads `extensions.json` for presence, `active`, `appDisabled`, and version — cold |

**The pin legs are gone** (decision 12, superseding this section's earlier three-leg table). The prior design held the pin through the author's global auto-update toggle. Measured 2026-09-06 from `omni.ja`: `extensions.update.autoUpdateDefault` **defaults to `true`**, so that toggle was an artifact of this session, not a property of a Zotero install. A distribution whose pin requires every user to find a global preference and hold it off indefinitely has not pinned anything — it has written a rule where it needed a mechanism, which is the ladder's bottom rung. Zotero plugins update themselves; the design now says so.

**`README.md` is the declaration** (Q15). Not a docs page and not a code constant: the human who has to run the Zotero UI wizard reads the README, and a list they cannot see is a list they will not install from. The addon id column is what makes the same table machine-readable, so doctor parses the artifact the human reads rather than a second copy that can disagree with it. This is the shape `docs/issue-dispositions.md` already proves in this repo. `skills/setup-vault/SKILL.md:44` today names two plugins in prose with no ids; it becomes a pointer to the table.

**`appDisabled` is Zotero's own verdict on the question doctor would otherwise have to compute.** `extensions.json` carries a computed `appDisabled` boolean per addon — Zotero has already evaluated the manifest's version range against the running application. Doctor reads that field rather than parsing `strict_min_version`/`strict_max_version` and reimplementing the comparison, which would be a second, worse copy of a decision the host already made.

**It is not the whole check, and this section said it was.** `appDisabled` answers *can Zotero load this*, and says nothing about *is Zotero loading it*. §14 records **9 of 23 addons user-disabled**, Zoplicate among them — "it had been user-disabled by mistake". A required plugin the author switched off reads present, `appDisabled = false`, correct version; a check that stopped there would report MATCHED for a plugin that is not running, which is the silent failure this paragraph was written to prevent. The observe leg therefore reads **`active`** as well — that is the field answering the question — and `appDisabled` is what separates *the author turned it off* from *Zotero refused it*, two findings needing two different repairs. Live on this machine: `zoteroshortdoi@wiernik.org 1.6.0` is `appDisabled` — its manifest caps at `9.0.*`. A plugin the vault relies on that Zotero will not load is a check that never runs and never says so; `appDisabled` makes catching that a field read.

**The local API sees plugin effects even though it cannot enumerate plugins.** A plugin is detectable by its library footprint, and that footprint carries per-item state the vault needs, not merely a presence signal (§14). That is a second, independent detection channel, mechanical-live, and lane 0 uses both.

### 6.2 Obsidian plugin

| Leg       | Mechanism                                                                          |
| --------- | ---------------------------------------------------------------------------------- |
| declare   | the contents of a seeded `.obsidian/` shipped in `research_vault/templates/vault/` |
| provision | scaffold copies it into a new vault — plugins present and configured on first open |
| observe   | doctor reads `<configDir>/plugins/<id>/manifest.json` `version` — mechanical-cold  |

**The BRAT pin leg is gone** (decision 12, superseding the earlier `pluginSubListFrozenVersion` route). BRAT freezes a version for plugins installed *through BRAT*, which is the beta-distribution channel; it is not a pin over community plugins installed normally, and adopting it would have added a dependency to buy a guarantee it does not give for the plugins we actually want. What replaces it is what the author specified: **a `.obsidian/` folder finely tuned for research-vault**, shipped with the plugins installed and their settings set. That provisions a working vault on first open — the outcome the pin was reaching for — without pretending the versions are held afterwards. What we know, and the limit of it: **the seeded tree carries no lock**, and updates are applied by the user from Obsidian's own settings, at a time we neither choose nor see. Whether Obsidian ever updates a community plugin without being asked is unmeasured and does not change the design — either way we observe the installed version rather than hold it.

The seeded folder is a **vendored artifact**: it carries third-party plugin code, so it records provenance and the version seeded, exactly as any vendored source in this repo does. **§15 carries the open item** — what proves the seeded tree still matches what was seeded, since a folder of copied plugin code has no lock and drifts silently once Obsidian updates it in place.

Two constraints, both **read**: the config directory is user-overridable, so no path may be hardcoded; and restricted mode is gated by a key in Obsidian's Chromium localStorage, **outside the vault**, so a purely file-based installer silently no-ops on a fresh vault. Restricted mode is a **setup precondition**, not a check — and it is the reason the seeded folder alone does not finish the job.

**There is no research-vault Obsidian vault on this machine** (measured). Every Obsidian fact gathered so far describes a sibling project's vault. `research_vault/templates/vault/` ships 15 files and **none under `.obsidian/`**, so the scaffold produces a vault Obsidian has never configured, while shipping two `.base` files whose minimum Obsidian version is recorded nowhere. Lane 3a opens by creating the vault this class is about, and its output *is* the seeded folder.

### 6.3 Claude Code plugin or skill

**Held, by sha** — the first of the two classes we can actually pin.

**The handoff condition has fired.** This section previously said the mechanism was "under construction in the sibling `agent-plugins` repository and does not yet exist: no `bin/`, no `upstream/skills.json`". Read at `agent-plugins@b8df1d6`, 2026-09-06 20:00, all of it now exists: `bin/setup` (723 lines, with a `--check` mode), `bin/doctor`, `bin/upstream-watch`, `bin/bump-superpowers`, `upstream/skills.json`, `.claude-plugin/marketplace.json` whose curated entries carry `git-subdir`, `url`, `path`, `ref`, **`sha`** and `version`, and 19 `tests/test-*.sh`. **The sha is the scope, not the date**: `bin/setup` passed through 614, 620, 716, 722 and 723 lines in a single afternoon, so a figure carrying only a date is stale before it is committed — this row's first draft recorded 614 and was already four commits behind when it landed. The interim was designed against an absence that lasted one day.

So the interim is not needed, and **what we adopt is the shape, not the script**. Two pinning surfaces, both already proven in the sibling: a `sha` in the marketplace entry, and a `ref` per source in `upstream/skills.json`. Drift is `git ls-remote` against each. We adopt those file shapes as-is — the first rung of the priority order, and the first place in this spec where adopt actually wins.

**Both surfaces have to be created here; neither is present** (measured 2026-09-06). This repository has `.claude-plugin/marketplace.json`, but it publishes *research-vault itself* — one entry, `"source": "./"`, no third-party rows and nowhere to put a `sha`. There is no `upstream/` directory at all. Adopting a file shape from the sibling means writing two files, and this spec says so rather than implying they are sitting there waiting for a field.

**We do not adopt `bin/setup` itself.** It is not vendored here, nothing in research-vault runs it, and it handles none of Zotero, Obsidian or Python — the three classes that make this repo's setup problem different from the sibling's. It solves the Claude Code class, which is the one class we can pin with two file fields. Copying a script to reuse two fields inverts the ladder.

Our two extra classes — Zotero and Obsidian — are requirements that sibling's spec never considered, and per decision 12 they are *unpinnable*, so there is nothing to file upstream about pinning them. What remains fileable is the observe leg, if the sibling ever grows non-Claude-Code classes.

### 6.4 Python dependency

`pyproject` plus a lock; **held**, by the lock. The mechanism is standard; **the lock does not yet exist** — measured 2026-09-05, no lock file in the tree, and `pyproject.toml:18` pins `pypdf>=4` as an open range. Generating it and pinning the optional groups is §15.15.

### 6.5 An unpinned installer already ships

`research_vault/scaffold.py:23` declares `PROVISION_COMPANIONS = ["kepano/obsidian-skills"]`, and `skills/setup-vault/SKILL.md:42` instructs `claude plugin install kepano/obsidian-skills`. No version, no pin, no drift check. The problem this spec exists to solve is live in the package, and it is register row zero.

**Row zero's pin now has a home.** It is a Claude Code plugin — the class that *can* be pinned (§6.3) — so the fix is not new machinery: add a third-party entry carrying a `sha` to `.claude-plugin/marketplace.json`, which today publishes only this repository, and let the hardcoded list in `scaffold.py` read from that entry rather than restate it. Two constants become one declaration. Decision 12 narrows this repo's pin problem to the two classes where a pin exists, and row zero is in one of them.

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
| 3b   | Obsidian plugins that read Zotero — ZotLit, `obsidian-reference-map` | decided inside lane 1's seam contract, after lane 2 dispositions Better BibTeX and records the version observed                                                                                                                                 |
| 4    | Skills curation — MedSci, K-Dense                                    | screens candidates against §4's floors: PRISMA-S, PRISMA-ScR and the ACM guidelines. **Not blocked** on issues #117 and #119 — a checklist screens components whether or not the step spec exists — though their output would refine the floors |

Lanes 2 and 3a are seam-free and may run concurrently. Lane 1 must not be split. Lane 3b is **not** seam-free: `obsidian-reference-map` requires Better BibTeX's local server and is reported broken against BBT 9.0.57+, a hard dependency on a lane-2 component at a version nobody pins (decision 12) — so the constraint lane 3b inherits is an observed version that can change under it, not a held one.

Each lane runs a **sourcing screen**: a bounded question, a screened candidate set, recorded exclusions, and a handoff (decision 15).

The earlier text called this a scoping review and then admitted the collision instead of fixing it. A scoping review is a **research method over literature**, with a protocol, a PRISMA-ScR flow and reportable counts. Picking software shares its bookkeeping — you screen candidates and record why you dropped them — and none of its subject matter. Reusing the name would have made §5.0's `scoping-review` step and lane 4's method the same word for two unrelated things, in a repository whose `CONTEXT.md` exists to stop exactly that. `scoping-review` now names only the workflow step; a lane runs a sourcing screen.

`docs/agents/sourcing.md` carries the definition, because nothing else did: `docs/superpowers/reqs/2026-09-02-sourcing.md` describes only searching and reporting and puts *"screening, ranking, rejecting"* outside its boundary, and it is a `sibling-project` document self-declared "Not confirmed". An earlier draft of this section cited it as the definition; it is a neighbour, not a source.

**Lane 2's inherited evidence is wrong in a specific way.** The 36-repository catalogue read **repository manifests**; the machine runs **shipped `.xpi` manifests**, and they differ — `zoterotldr` and `scite` are both active on 10.0.1 while the catalogue records ranges that would refuse them. Seventeen catalogue rows say "loads on 9.0.6"; none mentions 10.0.1. Lane 2 re-measures loadability from the installed `.xpi`.

## 8. Cold-start contract

A session opening lane N reads exactly: the component register, this spec in full, and the closed sourcing screens of every lane this one depends on. Lane 0 has no prior lane. The spec is one file, and reading it whole is cheaper than adjudicating which section a column needs.

That list is named in the register's header block. **Doctor** (§9) fails if the list points at anything marked `historical` or `pending-map`; the status linter (§10) runs before the register exists and cannot see the list.

**The line budget is dropped.** It was a number with no mechanism — nothing measured it, nothing failed on it, and a budget that only a reader can enforce is a rule where the ladder asks for a mechanism or nothing. What the budget was protecting is protected by the list itself: naming three things to read is the bound. The one enforceable half — that everything named still binds — is the doctor check above, and it stays.

The contract exists because the expensive part of entering this repository is not reading volume, it is inferring which material still binds. The register answers that in one screen.

## 9. Setup, doctor, drift, and the upgrade act

**A doctor already exists, and it repairs before it probes.** `research_vault/scaffold.py`'s `doctor()` at :347 calls `scaffold_vault(vault)` at :356, unconditionally, then returns eight probes — tree, machine-config, zotero, bbt, autoexport, staleness, remote, backup — and **none concerns an installed component**. This spec extends it rather than starting a second one, and separates the two acts: the component checks are read-only and run in a `--check-only` mode that skips the scaffold write, so the observe legs of §6.1 and §6.2 stay read-only and drift cannot be repaired away before it is reported. Adopt-over-build applied to our own code.

**Corrected 2026-09-06, same day, by measurement.** This paragraph first claimed that `doctor()` repairs the vault tree before reporting on it, so tree drift is "repaired away before it is observed". **That is false**, and it is this document's seventh instance of its own recurring shape — a claim adopted from a reviewer, scoped wider than the evidence, published in a commit whose message named that very shape.

What was measured instead, by deleting a required directory from a scaffolded, committed vault and calling `doctor()`: `_preflight_conflicts` (`scaffold.py:180-207`) sees the tracked path still in HEAD and absent on disk, raises, and doctor reports `tree UNMATCHED — vault tree repair failed: scaffold conflict with tracked path: projects/.gitkeep`. **The directory is not recreated and the drift is reported.** In the realistic drift case the repair always raises, so the fused call repairs only where nothing is committed — a vault that does not exist, or an uncommitted test fixture.

**Two defects survive the correction, and they are not the one first claimed.** `doctor` against a path that does not exist runs `git init` and a first commit, then reports `tree MATCHED` — **silent provisioning from a verb whose name promises a diagnosis**. And the repair's failure is reported through the `tree` row rather than as its own finding, so "the tree is incomplete" and "the repair could not run" arrive in the same cell.

**`--check-only` as §9 defines it does not make doctor read-only.** The definition is "skips the scaffold write", and `scaffold_vault` is not doctor's only writer: `observe_autoexport` calls `commit_autoexport` (`bibliography.py:707`, `:297`), which writes git objects and moves `HEAD` whenever the export matches evidence. A mode named for reading must either cover that write or stop claiming the word.

**App liveness is a separate input and is never inferred from a client's reachability.** The Zotero local API is a preference that can be off while Zotero runs, so an unreachable client is evidence of nothing about the process. A design that reads `running = False` from a failed `ready()` would permit the cold read of a live profile — minting exactly the stale `MATCHED` this section forbids. Liveness is therefore supplied to the observation, `None` is a legitimate value meaning *undetermined*, and undetermined fails safe to `SKIPPED`. Three independent interface designs converged on this constraint, which is why it is recorded here as a requirement rather than left to whichever design is chosen.

**Doctor runs in two phases and reports which it completed, per substrate app.** The live phase needs the relevant app up — four of the eight existing probes already fail `zotero down` without it, and the Obsidian CLI needs the desktop app running. The cold phase needs that app down. A cold check attempted while its app is running reports `SKIPPED — <app> running`, never a stale `MATCHED`, and doctor states which apps it found running so a partial run is never mistaken for a clean one. Doctor gains, per §6:

- **the README declaration read**, comparing the table decision 17 puts in `README.md` against what `extensions.json` reports — the check that makes the human's list and the machine's list one artifact rather than two that can disagree;
- the Zotero per-plugin observe leg — presence, `active`, `appDisabled` and version from `extensions.json`, cold; effects over the local API, live (§6.1). **Not a pin check**: the pair the first of these bullets used to name (`autoUpdateDefault == false` plus no `applyBackgroundUpdates == 2`) went with decision 12;
- the Obsidian manifest version read, **proposed, pending T5** — cold, and it reports a version without asserting a pin (§6.2);
- the Claude Code sha comparison via `git ls-remote`;
- a merge check for the Zoplicate path (§15.3).

Doctor's exit semantics are **open** — the borrowed spec never states them, so any behaviour assumed here would be our own design wearing borrowed clothes (§15.1). **Rollback is open too** (§15.2): the borrowed spec has no rollback story for a failed setup or update, its only rollback text covers a one-time marketplace cutover, and setup as designed is forward-converging with no inverse.

**No second setup mechanism** (decision 16). The sibling ships `bin/setup`; research-vault does not get one. This section's own rule — *a doctor already exists, so extend it* — decides it, and the three facts confirm it: `scaffold.doctor()` is working code with eight probes, nothing in research-vault runs the sibling's script, and the projects are separate for now so sharing it is not available either. What we adopt from the sibling is its **principles** — declarations live in-repo, check is a second mode of the thing that acts, tests run against a scratch `HOME` — not a script whose job this repo already does, for three classes it does not cover.

### 9.1 The upgrade act

**The act narrows to the two classes that have pins** (decision 12). For Claude Code and Python: **bump** the pinned identifier, **re-verify**, **revert** to the prior row if verification fails. The register records it as a new row with the old closed via `superseded_by_row` — never an in-place edit, never a deletion. Blocked on §15.2, because revert has no defined mechanism yet.

For Zotero and Obsidian there is no pin to move, so there is no upgrade act — those components upgrade themselves, and what the register gets is not a bump but a **re-observation**: doctor reports the version it now finds, and a changed value opens a row only if something broke. The distinction matters because the previous text implied a deliberate act existed for all four classes, which would have had us writing an upgrade procedure for a thing we do not control.

## 10. The status-marking pass

Runs before this spec's lanes, as its own bounded task with its own approval. Nothing moves, nothing is deleted.

Scope, measured after the pass ran: **180 markdown files** — `docs/` 106, `.superpowers/` 71, root 3. This amendment then added `docs/agents/sourcing.md`, making it 181 and `docs/` 107; the count is a dated scope for that pass, not a standing fact. The figure this section first carried, 202, predated the `skills/` exclusion below.

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

Orthogonal flag, not a status: `should-be-scoping-review`. A document may be `historical` **and** flagged as work the workflow should later replace. That flag produces the test-case set. **Decision 15 supersedes its name and narrows its meaning**: it was set on 42 documents that are not one kind of thing, and for the sourcing screens among them it names the wrong successor entirely. §15.19 carries the split; the flagged set is unchanged until then.

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

**Chosen.** It closes the marketplace-bootstrap item, since the bootstrap against a private repository was never tested. §15.1, §15.2 and §15.10 remain open against the Claude Code class. §6.3's handoff no longer does — it fired on 2026-09-06.

Three preconditions, all measured, none blocking the decision and all blocking the flip:

1. **260.6 MB (248.5 MiB) of raw Claude Code session transcripts sit in git history** — 120 `.jsonl` blobs under `docs/research/raw/*transcripts*`, the largest at 32 MB, 32 MB and 23 MB. Untracked today; present in every clone forever. Publishing the repository publishes everything those sessions saw.
2. **Eight PDFs were committed and later removed.** Four are 2026 copyrighted papers, one a 2014 journal article, the rest US-government ICD/ICS documents. All eight lived in `sources/`; commit `52bc0fb` (2026-08-27) removed them and gitignored the folder in one act, which fixes the working tree and not the history — those are the paths a rewrite must strip. The ISO standards the folder holds now were added afterwards and were never committed.
3. **The current tree carries what neither route removes.** `docs/research/2026-09-04-import-sourcing.md` reproduces verbatim source text from candidate repositories, eight of which record no LICENSE file — all-rights-reserved by default — and 15 tracked files carry the author's absolute local paths. A history rewrite and a squashed tree both preserve HEAD. Reduce the unlicensed candidates to citation plus paraphrase, and sweep the paths.

Route: a history rewrite before the flip, or a fresh public repository from a squashed tree. Its own task with its own approval, not work that rides along inside a lane.

## 13. Tracers

A tracer is one cheap check that can falsify a decision, run before the decision is built on.

**T2 and T6 are withdrawn** — not passed, not failed, *dissolved*. Both tested pin legs that decision 12 removed: T2 asked whether Zotero auto-update is on (it is, by default, and we no longer try to hold it off), and T6 asked whether setup could establish the Zotero hold and the BRAT freeze on a foreign machine (neither is now claimed). A tracer whose decision no longer exists is not an open item; deleting it is what keeps §15 honest about what is actually outstanding.

|     | Tracer                                                                                 | Result                                                                       |
| --- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| T1  | enumerate installed Zotero plugins with no GUI                                         | **passed** — `extensions.json` is plain JSON and carries every field needed  |
| T3  | doctor reads presence, `appDisabled` and version for one plugin from `extensions.json` | **open, and now cheap** — three field reads, no version-range logic (§6.1)   |
| T4  | status linter over a hand-marked sample                                                | open                                                                         |
| T5  | Obsidian plugin version readable by file                                               | **open, blocked on §6.2's missing vault** — §6.2's observe leg depends on it |

"Cutover" is reserved for §12. The cancelled `user.js` tracer stays cancelled, and §15.14 closes alongside T2 — both asked how to establish a hold this design no longer attempts.

## 14. Mechanism claims and their sources

Zotero runtime rows re-measured 2026-09-05 evening, after the author enabled PMCID auto-fetch and re-enabled Zoplicate. Read-only throughout.

**Errata, 2026-09-06.** Two rows were sound when written and are wrong now. Both are corrected in place and marked; the original reading is kept, because a measurement log that quietly rewrites itself cannot be audited.

- **`borrowed mechanism`** — measured 2026-09-05 as an absence. `agent-plugins` shipped `bin/setup` in `3300d55` on 2026-09-05 and the row was stale within the day. This is the sixth instance of this spec's recurring defect shape: *a claim sound at the moment of writing, scoped wider than its evidence.* "Does not yet exist" is a claim about the future wearing a measurement's clothes; "did not exist at 2026-09-05" is what was actually seen.
- **`Obsidian pinning`** — the BRAT reading is accurate and no longer load-bearing. Decision 12 drops the pin leg it supported.

| Fact                             | Value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Established                                                                                  |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Zotero, Better BibTeX            | 10.0.1 on Windows; BBT 9.0.63; local API reachable from WSL2                                                                                                                                                                                                                                                                                                                                                                                                                                                         | live probe 2026-09-04, re-confirmed 2026-09-05                                               |
| Zotero has run 10.0.1 since      | `compatibility.ini` `LastVersion=10.0.1_20260824184713`, mtime 2026-08-26; `prefs.js:39` `extensions.lastAppVersion = "10.0.1"`                                                                                                                                                                                                                                                                                                                                                                                      | measured                                                                                     |
| Zotero profile                   | `…/AppData/Roaming/Zotero/Zotero/Profiles/881hrcxd.default`, sole profile per `profiles.ini`                                                                                                                                                                                                                                                                                                                                                                                                                         | measured                                                                                     |
| Zotero data directory            | `D:\Zotero` per `extensions.zotero.dataDir`, not the Windows default                                                                                                                                                                                                                                                                                                                                                                                                                                                 | measured                                                                                     |
| `extensions.json`                | plain JSON, schemaVersion 37, 23 addons, each with id, version, `active`, `userDisabled`, `appDisabled`, `applyBackgroundUpdates`, `targetApplications`                                                                                                                                                                                                                                                                                                                                                              | measured                                                                                     |
| addon states                     | **13 active, 9 user-disabled, 1 app-disabled**; the app-disabled one is `zoteroshortdoi` 1.6.0                                                                                                                                                                                                                                                                                                                                                                                                                       | measured, after the author's re-enable                                                       |
| `zoteroshortdoi` 1.6.0           | `appDisabled=true`; manifest caps `9.0.*`. The ingest spec's "6.0 to 7" is stale; the conclusion is not                                                                                                                                                                                                                                                                                                                                                                                                              | measured                                                                                     |
| auto-update, before the toggle   | both prefs absent; defaults `true` read from `omni.ja` `defaults/preferences/zotero.js`; `applyBackgroundUpdates=1` on all 23. A daily background check runs near 17:33:53Z, and 13 of 23 carry stamps in a ~11-second time-of-day band across dates from 2026-08-05 to **2026-09-03**, the most recent — corroborated by matching `.xpi` mtimes. It did **not** fire on 2026-09-05                                                                                                                                  | measured                                                                                     |
| auto-update, after the toggle    | `prefs.js:49` `extensions.update.autoUpdateDefault = false`; still no per-addon override — the value set across all 23 is `{1}`. **This state is an artifact of this session, not a property of a Zotero install** — the default is `true`, so no other machine starts here (decision 12)                                                                                                                                                                                                                            | measured                                                                                     |
| `addonStartup.json.lz4`          | mozLz4 container, no decoder available; unnecessary, `extensions.json` carries the same fields                                                                                                                                                                                                                                                                                                                                                                                                                       | measured                                                                                     |
| plugin enumeration over the wire | none — `/api/` answers 200 with the stub body `Nothing to see here.` and every enumeration path under it 404s; BBT JSON-RPC's 14 methods expose nothing                                                                                                                                                                                                                                                                                                                                                              | measured                                                                                     |
| plugin **effects** over the wire | `/api/users/0/tags` returns 2,673 tags (the endpoint pages at 100; this is a full walk). Both attachment-scanner generations are present: `#nosource` 146 items, `#broken` 3, `#duplicate` 2, `❌ nosource` 154, `🚫 broken` 4, `❓ nonfile` 1, `‼️ duplicate` 0. **134 items carry both `#nosource` and `❌ nosource`**                                                                                                                                                                                             | measured, two independent runs                                                               |
| tag vocabulary                   | 2,673 tags: 1,526 manual (`type 0`), 1,147 automatic (`type 1`). A case/number/separator normalisation finds 280 near-duplicate clusters covering 627 tags                                                                                                                                                                                                                                                                                                                                                           | measured                                                                                     |
| identifier tags                  | zero of 2,673 tags are identifier-shaped; sampled top items carry `PMCID:`/`PMID:` in Extra. Provisional — `pmcid.tags` was enabled in the same session                                                                                                                                                                                                                                                                                                                                                              | measured                                                                                     |
| attachment-scanner               | 0.5.1 active; `prefs.js:28-31` `monitor_attachments`, `remove_pubmed_entry`, `remove_snapshot`, `scan_nonfiles` all true; `prefs.js:32-35` configures the emoji preset. The author reports long use with no loss of needed files, only browser-plugin byproducts; the finding that survives is the two-generation grammar, not a data-loss risk                                                                                                                                                                      | measured; author 2026-09-05                                                                  |
| PMCID fetcher                    | 1.0.3 loads; `prefs.js:111` `extensions.zotero.pmcid.auto = true` — **auto-fetch is on**; `prefs.js:113` `extensions.zotero.pmcid.tags = true`                                                                                                                                                                                                                                                                                                                                                                       | measured, after the author enabled it                                                        |
| Zoplicate                        | 5.1.1, **active** (it had been user-disabled by mistake); manifest `8.999–10.0.*`, AGPL-3.0                                                                                                                                                                                                                                                                                                                                                                                                                          | measured; author 2026-09-05                                                                  |
| attachment-scanner manifest      | `6.999`–`*`, MIT, read from the released `.xpi`                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | read                                                                                         |
| Zotero 10 local API writes       | POST/PUT/PATCH/DELETE for items, collections and saved searches, plus tag deletion, full-text writes and file uploads; reads unauthenticated, writes need a runtime key from `POST /api/local/authorize` behind a confirmation dialog. No key exists — `localAPIKeys.json` is absent                                                                                                                                                                                                                                 | read (`docs/research/2026-09-05-zotero-api-reading.md:47-75`); absence measured              |
| collection membership            | carried only by the item; `Zotero.Collection.toJSON` emits no roster; no collection-items write endpoint, and the local API returns **405** for `/collections/<key>/items`. Filing an item is a GET-then-`PATCH` of the item, `collections` as a complete list, 412 race between                                                                                                                                                                                                                                     | read (`collection.js:827-838`, `server_localAPI.js:1050-1066`); 405 read from the route gate |
| local-API `PATCH` hazard         | runs `fromJSON(merged, {strict: false})`, enabling Extra migration — can move `Extra:` lines into empty real fields, rewrite Extra, flip `itemType` on a recognised `type:` line, and bumps `dateModified` and `clientVersion`. 2,723 of 2,844 items are at version 0                                                                                                                                                                                                                                                | read (`server_localAPI.js:1973-1999, 2195-2226`; `item.js:5634-5676`); counts measured       |
| sync undoes removals             | member properties including collections and tags are combined on sync, "so any removals will be automatically undone" — reconcile-by-absence is unsound across devices                                                                                                                                                                                                                                                                                                                                               | read (`syncLocal.js:1926-1930`)                                                              |
| Zoplicate merge path             | imports `mergeItems.mjs` directly, never `Zotero.Items.merge` — the shim BBT monkey-patches — so a merge **skips BBT citation-key consolidation**; loser's collections and tags union onto the master, loser trashed with memberships intact (55 trashed items still hold a live membership)                                                                                                                                                                                                                         | read (`mergeItems.mjs:46, 49-70`); count measured                                            |
| markdb-connect state             | installed and configured, tag `ObsCite` on 3 items. `mdbc.removetags` unset → defaults to the destructive `keepsynced`; `sourcedir` `C:\Users\eranr\Memoria-test\20-sources\01-papers` whose parent does not exist; `obsidianvaultname` `research-wiki`; `yamlkeyword` `citekey`. A run today strips the 3 tags                                                                                                                                                                                                      | measured; branch read from `mdbc.js`                                                         |
| catalogue staleness              | compatibility judged against Zotero 9.0.6; 17 of 36 rows say "loads on 9.0.6", none mentions 10.0.1; the catalogue read repository manifests while the machine runs shipped `.xpi` manifests, and `zoterotldr` and `scite` differ                                                                                                                                                                                                                                                                                    | measured                                                                                     |
| existing doctor                  | `research_vault/scaffold.py`'s `doctor()` at :347 calls `scaffold_vault(vault)` at :356, unconditionally before returning eight probes — tree, machine-config, zotero, bbt, autoexport, staleness, remote, backup — none about installed components; four of them fail `zotero down`                                                                                                                                                                                                                                 | read                                                                                         |
| unpinned installer               | `scaffold.py:23` `PROVISION_COMPANIONS = ["kepano/obsidian-skills"]`; `skills/setup-vault/SKILL.md:42`                                                                                                                                                                                                                                                                                                                                                                                                               | read                                                                                         |
| borrowed mechanism ~~absent~~    | **superseded.** At `agent-plugins@b8df1d6` (2026-09-06 20:00) it ships `bin/setup` (723 lines, `--check` mode), `bin/doctor`, `bin/upstream-watch`, `bin/bump-superpowers`, `upstream/skills.json`, a `marketplace.json` whose curated entries carry `sha`, and 19 `tests/test-*.sh`. *Read 2026-09-05: no `bin/`, no `upstream/skills.json`, no `upstream-watch.yml`.* Scoped by sha, not date — `bin/setup` changed five times on 2026-09-06. Doctor exit semantics and rollback remain unspecified (§15.1, §15.2) | re-read 2026-09-06                                                                           |
| Obsidian pinning                 | BRAT `pluginSubListFrozenVersion` (`src/settings.ts`) is the only documentation-endorsed route, and it covers only plugins installed *through BRAT* — **not a pin over normally-installed community plugins**, which is why decision 12 drops it; `manifest.json` `version` is the only installed-version record; restricted mode is gated in Chromium localStorage outside the vault                                                                                                                                | read, docs.obsidian.md and the BRAT source                                                   |
| no research-vault vault          | Obsidian knows only sibling vaults; `research_vault/templates/vault/` ships 15 files, none under `.obsidian/`                                                                                                                                                                                                                                                                                                                                                                                                        | measured                                                                                     |
| corpus                           | 180 `.md` in scope after the `skills/` exclusion (`docs/` 106, `.superpowers/` 71, root 3); one whole-document supersession pair; six documents self-declare the sibling; the named siblings own zero main-tree files                                                                                                                                                                                                                                                                                                | measured                                                                                     |
| issues                           | 66 open; none older than 2026-08-25 by `updatedAt`, an instrument comment and label edits also bump                                                                                                                                                                                                                                                                                                                                                                                                                  | measured                                                                                     |
| code                             | 29 modules / 10,597 lines in `research_vault/` (`hooks/` is a further 847 lines in 3 files, excluded from that count); 21 verbs; 9 modules named by a verb, 9 reachable only transitively; 45 test files / 24,571 lines; 25 sidecars, 18 stale                                                                                                                                                                                                                                                                       | measured                                                                                     |
| Python pin                       | no lock file in the tree; `pyproject.toml:18` `pypdf>=4`                                                                                                                                                                                                                                                                                                                                                                                                                                                             | measured                                                                                     |
| coverage data                    | the local `.coverage` resolves against `/home/eranr/New folder/research_vault/` — a foreign checkout, unusable; not tracked in git                                                                                                                                                                                                                                                                                                                                                                                   | measured                                                                                     |
| git history                      | 120 transcript blobs totalling 260.6 MB (248.5 MiB); 8 PDFs added in `3719086` and removed in `52bc0fb`, all under `sources/`; `sources/` gitignored with 0 tracked and the ISO standards never committed; 15 tracked files carry absolute local paths                                                                                                                                                                                                                                                               | measured                                                                                     |

## 15. Open items carried forward

01. ~~Doctor's exit semantics (§9).~~ **Closed — the item was false.** They are implemented and tested: `research_vault/__main__.py:45-47` carries `DOCTOR_HARD_UNMATCHED`, `DOCTOR_HARD_UNREACHABLE` and `DOCTOR_WARN_ONLY`, and five tests exercise them. The spec inherited this as open from the sibling's unspecified design and never checked its own code. What is genuinely open is smaller and is item 20: those three sets live in a different module from the probes they classify, so a new check is warn-only until someone remembers to add it.

02. Rollback for a failed setup or update, which also blocks §9.1's revert leg.

03. **The Zoplicate merge path, now a measured hazard rather than an inferred one.** Zoplicate imports `mergeItems.mjs` directly and never calls `Zotero.Items.merge` — the deprecated shim Better BibTeX monkey-patches — so **a Zoplicate merge skips BBT's citation-key consolidation** (read, `mergeItems.mjs:46, 49-70`). The merge union-merges the loser's collections and tags onto the master, records `dc:replaces`, and trashes the loser without stripping its memberships; 55 trashed items still hold membership in a live collection (measured). Since the citekey is the vault's identity, a merge can leave the survivor keyed differently from the vault note whatever the vault wrote. Zoplicate is active as of 2026-09-05. Lane 2 owns the fix; doctor's merge check (§9) is the interim detector.

04. URL-only sources — cited versus consulted (§7.2).

05. What the PMCID fetcher writes going forward, now that `pmcid.tags` is on: Extra lines, tags, or both (§7.0).

06. The `.py.manifest.json` sidecars: retire with mutate4py, or keep (§11).

07. Zoplicate merge semantics (item 3) are the open part; duplicate detection itself now has an owner, while `zotero-format-metadata` detects and reports but does not merge.

08. The glossary and the two suspended ADRs — handed to issue #116 (§2).

09. The remaining 11 of 23 installed addons, undispositioned, including one that copies attachments to a OneDrive path (§7.0).

10. The `upstream-watch` schedule. `agent-plugins` now ships `bin/upstream-watch`, so the script exists; **the interval still does not** — a watcher with no cadence is a drift detector that fires when someone remembers to run it (§6.3).

11. The `long-form` **step** has no lane and no issue. The ACM guidelines themselves are owned — they are one of lane 4's screening floors (§4) — but nothing schedules the step they bind.

12. The `daily-log` step has no lane, no register row and no issue; `research_vault/appendlog.py` is its only carrier and enters §11's audit named by no verb (§4).

13. Whether either substrate app flushes its files fully only on exit (§3.3). Zotero's `prefs.js` and `extensions.json` were both observed rewritten while it was running, so the cold-read precondition is provisional there. The Obsidian half is unmeasured entirely — `manifest.json` and `community-plugins.json` write cadence is unknown, and its localStorage LevelDB gives evidence on presence but never on absence while the app is live.

14. ~~A mechanical route to establishing the Zotero pin on a machine that is not the author's.~~ **Closed by decision 12** — the item asked how to establish a hold this design no longer attempts. What replaces it is item 17.

15. The Python lock does not exist; `pypdf>=4` is an open range (§6.4).

16. **Vault-owned state inside Zotero — answered: strict one-way now, no collection subtree.** The requirement is real and is a PRISMA-ScR obligation, not a convenience: a scoping review's item set must be reachable as a set, because the flow counts depend on it. The collection route is nonetheless rejected, on a measured write surface.

    **Collection membership is carried only by the item.** `Zotero.Collection.toJSON` emits `{key, version, name, parentCollection, relations}` and no roster; there is no collection-items write endpoint, and on the local API `/collections/<key>/items` is routed to the Items endpoint whose write gate returns **405** for that path (read: `collection.js:827-838`, `server_localAPI.js:1050-1066`). Filing an existing item therefore means GET-then-`PATCH` of the **item**, with `collections` sent as a complete list, and a 412 race between the two calls. Worse, local-API `PATCH` runs `fromJSON(merged, {strict: false})`, which enables Extra-field migration: a membership-only patch re-runs Zotero's normalisation over a record the vault merely read — it can move `Extra:` lines into empty real fields, rewrite Extra, change `itemType` if Extra carries a recognised `type:` line, and bumps `dateModified` and `clientVersion`, marking the item for sync upload. 2,723 of 2,844 items sit at version 0 today; every filed item leaves that state.

    So the author's additivity insight is **correct about collection objects and irrelevant to membership** — tags are equally additive, so it does not discriminate between routes. The subtree is a small owned surface; the membership is not, and it costs the same per item as a tag while buying nesting the vault's two or three flat facets do not need.

    **What is chosen for now: nothing.** The repository contains no literature notes, so there is no vault state to project. This matches the prior art's own recommendation.

    **When presence becomes worth showing**, the route is a single tag through **markdb-connect, which is already installed** — `item.addTag; saveTx()`, no `strict:false`, no API key, no authorize dialog, and no vault code. Its gating unknown is whether Windows-side Zotero can enumerate a `\\wsl.localhost\…` path; if not, the route collapses to the vault writing the tag itself over the local API, with the full hazard set above.

    **It is currently misconfigured in a destructive direction**, and this must be fixed before it is ever run: `mdbc.removetags` is unset and therefore defaults to `keepsynced`, the branch that removes tags for notes it cannot find; `sourcedir` is `C:\Users\eranr\Memoria-test\20-sources\01-papers`, whose `20-sources` parent does not exist; `obsidianvaultname` is `research-wiki`; and `yamlkeyword` is `citekey` where this spec standardises on `citationKey`. A run today would enumerate zero notes and strip the 3 live `ObsCite` tags — issue #31's data-loss mode, armed on this machine (all measured 2026-09-05).

    **Route-independent failure mode, and it is the one that bites:** Zotero sync states that member properties including collections and tags are combined, *"so any removals will be automatically undone"* (read, `syncLocal.js:1926-1930`). Any reconcile-by-absence loop is unsound across devices, whatever is written.

    Retained split if this ever opens: **scope** in Zotero, **screening state** in the vault, so one fact never gets two homes. A saved search needs no API write at all — the author saves one Advanced Search by hand — and buys negation and composition, at the cost of being structurally flat and not a drop target.

17. **What proves the seeded `.obsidian/` still matches what was seeded — answered: nothing new records it, because the package already does.** The folder ships third-party plugin code with no lock, and the observe leg reads only `manifest.json` `version`, which says what is installed and never whether it is what we shipped.

    The eliminate move is that **the seeded-state record is the installed package itself**. `importlib.resources` still holds the exact bytes scaffold copied, and `_vault_template_paths()` (`scaffold.py:78`) already enumerates them for the copy, the owned-path set and the conflict preflight. The probe is a sha256 comparison over that same enumeration — no manifest to write, no second record to go stale, and one more caller for an enumeration that already earns its keep. A hash file recorded at seed time would have been a new module whose deletion test says *vanishes*.

    Two limits, both stated rather than discovered later. **The check proves the tree is unchanged, never that it is the tree Obsidian loads** — the config directory is user-overridable (§6.2), so the reason string must name the path it compared. And **doctor's probes cannot reach the acknowledgment mechanism**, so a legitimate plugin update leaves the row permanently `UNMATCHED`: an ack is scoped to a content hash (`CONTEXT.md`), and nothing connects a doctor row to one. That second limit is a real gap, carried as item 21, and it is the reason this answer is a mechanism rather than a finished design.

18. **Where the new mechanisms live if research-vault moves into `agent-plugins` — answered: the question was malformed, and the deferral costs nothing.** The premise was that `scaffold.doctor()` and the sibling's `bin/doctor` are two adapters at one seam. Read side by side they are not: the sibling's is an unparameterised read-only report about the machine, and ours is a targeted converger that writes into a named vault before probing it. **Two modules sharing a name, not one seam with two adapters** — and by the two-adapters rule there is no seam to place, so a shared doctor interface, a `bin/doctor` shim and a machine-readable envelope are all structure with no caller. Deleting each of them removes nothing from either repository.

    **The measured unbuild cost of deferring is zero lines**: none of the four new mechanisms is written yet. It stays zero if two things hold, and both are correct whether or not the move happens — so they are not hedges. **Declarations are accepted as parameters, never resolved from the current directory**: a parser that finds its own `README.md` cannot be exercised past its interface and breaks on relocation, while one that takes a path leaves the single line of resolution with the caller that has the context to answer it. And **doctor moves out of `scaffold.py`**, whose module docstring says it creates vaults; that is pure relocation with no behaviour change, and it is cheapest before four new mechanisms are written into the wrong file.

    *The move itself remains the author's and undecided. What is closed is the claim that deferring it has a cost.*

19. **`should-be-scoping-review` is set on 42 documents and means two different things** (§10, decision 15). Some carry it because they are informal literature comparisons a real scoping review should replace; others are **sourcing screens**, where the flag names the wrong successor entirely — `docs/research/2026-09-01-pre-spec-sourcing-screen.md` is the clearest case, since decision 15 cites it as the repository's own correct use of the word. Splitting the flag means re-reading 42 rows of a human-reviewed artifact, so it is scheduled rather than done here, and `docs/document-dispositions.tsv` is untouched by this amendment.

20. **The write-side gate is a mechanism hung on a seam that alters nothing** — the repository's own instance of the defect this spec keeps finding. Measured 2026-09-06: `main` has **no branch protection and no rulesets**, and every workflow run in repository history is a `push`, so the **186 consecutive red runs since 2026-08-25** blocked nothing and gated nothing. Meanwhile `.git/hooks/pre-commit` does not exist in this checkout, so `git commit` never runs the six form owners — while `scaffold.py:272` installs a `pre-commit` hook into **every consumer vault** the product creates. Commit time is an existing seam with a proven adapter; the development checkout is the one place it was never wired. The 2026-08-22 ruling declined the pre-commit *framework's* stashing hook and was recorded as declining the rung. Naming the lane `(advisory)` describes a posture nothing implements.

21. **Doctor's three severity sets live in a different module from the probes they classify** (`__main__.py:45-47`), and are duplicated verbatim in `tests/test_doctor.py:20`. A check absent from all three sets renders warn-only, so §9's five new probes are benign-by-default until someone edits a file they are not working in. This is what remains of item 01 after it closed.

22. **Nothing connects a doctor row to an acknowledgment.** An ack is scoped to a content hash and lets a check stand down without erasing the finding (`CONTEXT.md`); `Probe` carries `check`, `result` and `reason` and no path or hash. Every observe leg added by §6 — the seeded tree above all — reports drift that a human has already accepted, every run, with no way to say so. The four-state result cannot express *known and accepted*.

23. **Also found, and out of scope for this spec** — all four now dispositioned, none carried here: the first three are issues **#125**, **#126** and **#127** (filed 2026-09-07); the fourth is decision 21's dated deferral. Kept for the record: the mutation gate has never evaluated a mutant, because its only firing condition is a pull request and this repository has none; the OKF pin is written twice, in `quality.yml` and in ADR 0001, with nothing comparing the copies; scaffold spawns roughly three git subprocesses per seeded file, which the seeded `.obsidian/` multiplies; and the CRAP ceiling fails on two functions, `_bump_generated` (43.1) and `check_metadata` (37.0), against a limit of 30 — **that one is no longer an issue to open; decision 21 carries it as a dated deferral.**
