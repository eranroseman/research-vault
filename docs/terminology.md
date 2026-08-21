# Terminology — decisions, precedence, inventory, and the naming pass

Consolidated living record (consolidated 2026-08-20 from the same-day `terminology-decision` and `user-facing-terminology` documents; all rulings author-confirmed; rulings carry their dates inline). Owns four things: the **cost model**, the **ruled precedence order** for anchor sources, the **decisions** taken against it (adoptions and deviations), and the **complete user-facing inventory** with anchor candidates — the working package for the **naming pass, which blocks §9 slice execution**.

## 1. Cost model

**Rename churn is priced at zero** (~10 minutes of implementation time pre-users; occurrence counts are not costs; sunk effort is not an argument). Exactly four real cost classes justify deviating from the precedence order:

1. **Permanent surface mismatch** — with tool surfaces we don't control.
2. **Information loss** — the base term carries less structure than the concept needs.
3. **Semantic falsification** — the base term would make our records state something false.
4. **Collision/ambiguity** — the base term already means something else in our context.

No class binding ⇒ the precedence order's term is adopted. Taste never justifies deviation.

**The cost model governs decisions, not just names** (author correction — third instance of the settled/sunk-cost error class): pre-first-vault, ANY prior ruling reverses at churn cost unless a real cost class binds. Precedent is information, never constraint — citing a prior ruling is an input to re-deriving from current facts, not a reason by itself. This is pre-alpha: everything is ten minutes away from different.

## 2. Precedence order for anchor sources (RULED)

**INVERTED by author ruling 2026-08-20 (Reading A: OKF leads; the four-cost model still governs every deviation).** Eight tiers, ordered by the ruling and then by cost of contradiction, evaluated per surface — a lower tier wins only where higher tiers are silent.

- **T1 — OKF** (Open Knowledge Format; the vault is a structurally conformant OKF bundle per ADR 0001): its vocabulary is the first source of names wherever it speaks.
- **T2 — Toolchain surfaces the user physically inhabits** (contradiction = class-1, paid daily): **CSL first** (fields in `bibliography.json`, pandoc citations), Zotero UI, BBT/ZotLit conventions, Obsidian (aliases, block links, properties, Bases), Dataview field syntax, Markdown.
- **T3 — Authorities of record**: Crossref (update types), DataCite (relation types), DOI system, W3C (Web Annotation selectors, PROV), CiTO/SPAR (citation typing), IETF where applicable.
- **T4 — Scholarly-method vocabularies**: PRISMA/Cochrane/Covidence, GRADE, ICD 203/206, plain scholarly English.
- **T5 — Cross-cutting aggregators**: OpenAlex, Wikidata, scite.
- **T6 — Community conventions**: llm-wiki, Ideaverse/LYT, Ahrens/PKM, Appleton, GTD/PARA, Wikipedia template vocabulary.
- **T7 — Developer-tool conventions, dev-facing surfaces only** (never vault prose): pytest outcomes, GitHub checks, Vale severities, CLI verb lore.
- **T8 — Author's coinage** — only where T1–T7 are silent.

**Tie-breakers:** (1) the vocabulary whose data we record beats the one we merely resemble; (2) verbatim machine-readable identifiers beat prose labels; (3) versioned spec beats living wiki beats blog; (4) surface fit is absolute.

Domain-scoped authorities (Crossref updates, W3C selectors) retain authority inside their domains regardless of tier walk order.

### Inversion deltas (ruled with the inversion; supersede conflicting rows below)

Applying the cost model against OKF-as-T1 across its whole vocabulary (`type, title, description, resource, tags, sources, generated, verified, status, stale_after`, footnote attribution, actor convention, reserved files):

**New adoptions (no class binds):**
- `stale_after` — optional per-note expiry, adopted (the earlier skip rationale, "duplicates what rot-watch derives," is not one of the four classes).
- `generated` (`generated.by`/`generated.at`) — adopted on machine-written notes alongside `verified` events.
- `description` — adopted as an optional frontmatter field (OKF recommended; no incumbent).
- **Synthesis-page lifecycle**: `status: draft | stable | deprecated` (OKF) replaces the Appleton maturity fields — `growth`/`planted`/`last-tended` are superseded (`generated.at` covers recency; Appleton is T6 and no cost class rescues a parallel three-state system). Supersedes §9 row 23.
- Actor convention, `verified` event shape, tier names, reserved `index.md`/`log.md`: previously S-promotions — now plain T1 base applications.

**New documented deviations (classes bind):**
- **Per-claim attribution**: OKF footnotes keyed to `sources[].id` vs `[@citekey, locator]` — deviation, **class 1** (pandoc/CSL/BBT/Zotero surfaces; the §6 citekey universe and its gates are built on citekeys).
- **`sources` frontmatter field / `resource` URI**: vs our `citekey`/`doi`/`url` provenance keys — deviation, **class 1 + 2** (CSL/registry identity is richer and toolchain-bound; adding OKF's synonyms would violate one-term-per-concept).
- **Lineage as untyped links**: vs stance-typed `supports`/`disputes` claim links — deviation, **class 2** (trust substance).
- **Screening states**: OKF's three-state lifecycle vs PRISMA `unscreened/included/excluded` on literature notes — deviation, **class 2** (screening is not a document lifecycle).
- **Project lifecycle**: OKF's three states vs `draft/parked/published/corrected/withdrawn` — deviation, **class 2** (publication and correction states carry gate semantics OKF's set cannot express). `draft` itself is now a T1 base application.

CSL's bibliographic vocabulary (`item`, `issued`, `author`, `locator`) is untouched — OKF is silent on bibliographic identity, so T2 governs there exactly as T1 CSL did before.

## 3. Current adoptions (inverted T1–T8 order)

| Term or contract | Authority | Current status |
|---|---|---|
| OKF v0.2 reserved files, non-empty concept type, optional description/stale_after, generated.by/at, and verified events | OKF (T1) | Adopted; vaults are structural OKF bundles. |
| accessed | CSL (T2) | Adopted; the former stack-consistency defect is closed. |
| supports / disputes | CiTO (T3) | Anchored adoption for typed claim links, not a naming deviation. |
| unscreened / included / excluded | PRISMA/Covidence (T4) | Adopted for literature screening; superseded remains the scholarly-succession state. |
| synthesis/ and type: synthesis | Evidence-synthesis vocabulary (T4) | Adopted; the OpenAlex topic collision is gone. |
| inbox/, log/, projects/ | GTD/PARA and log convention (T6) | Ruled current folder vocabulary. |
| fixity-sha256 | OAIS/NDSA (T3/T4) | Adopted archival term. |
| failed-verification | Wikipedia template vocabulary (T6) | Adopted exact inline-field name. |
| draft | OKF (T1) | Adopted where shared; synthesis and project lifecycles remain kind-specific. |
| item, issued/date-parts, author, locator/label, CSL item types | CSL (T2) | Base applications in the bibliographic layer. |

## 4. Current documented deviations

| Concept | OKF base | Harness contract | Forcing class |
|---|---|---|---|
| Per-claim attribution | footnotes keyed to sources[].id | Pandoc [@citekey, locator] | **1** — permanent CSL/BBT/Zotero/Pandoc surface mismatch |
| Source identity | sources / resource | citekey / doi / url | **1 + 2** — toolchain binding and richer registry identity |
| Lineage | untyped links | typed supports / disputes claim links | **2** — stance is trust substance; the names themselves are CiTO-anchored |
| Literature lifecycle | draft/stable/deprecated | unscreened/included/excluded/superseded | **2** — screening is not document maturity |
| Project lifecycle | draft/stable/deprecated | draft/parked/published/corrected/withdrawn | **2** — publication/correction gate states would be lost |
| Replacement relation | identity merge | superseded / superseded-by | **3** — also covers succession between distinct scholarly works |

The prior retrieved defect is closed by accessed. The prior stance-link deviation is now the lineage deviation above with CiTO-anchored field names.

## 5. Standing rules

- The inverted T1–T8 precedence order remains the default source of names; deviation requires one of the four cost classes.
- One canonical term represents each concept. No compatibility aliases are needed before the first vault.
- Recorded API facts remain boundary-verbatim, with source field names, index, and access date.
- Reserved basename index.md and log.md files have no concept frontmatter, except the bundle-root index.md, whose frontmatter is exactly okf_version: "0.2".
- The naming pass is complete. Section 10 remains the intentional old/new migration record; older proposal reasoning in §9 is historical, not current authority.

## 6. Current user-facing inventory

Plans A–B are built and Plan C is active. Legend: **A** externally anchored · **S** ruled convention · **D** documented deviation.

### 6.1 Vault paths and note kinds

| Current term | Status |
|---|---|
| inbox/; inbox/review-queue.md | A/S — GTD inbox; typed append-only review queue |
| literatures/; type: literature | A/S — ZotLit/Ahrens projection vocabulary |
| synthesis/; synthesis/index.md; type: synthesis | A — evidence-synthesis vocabulary; nested index is reserved |
| log/; log/YYYY-MM-DD.md; root log.md | A/S — append-only daily directory plus distinct reserved root tail |
| projects/; type: project | A/S — PARA/GTD project vocabulary |
| x/; AGENTS.md; .harness/; hk- markers | S — ruled harness conventions |
| root index.md | A — OKF bundle root with exactly okf_version: "0.2" |

### 6.2 Claim and metadata language

| Current term | Status |
|---|---|
| [@citekey, locator], ^claim-id, claim link | A/D — Pandoc/CSL and Obsidian block-link surfaces |
| [supports::] / [disputes::] | A — CiTO names; typed lineage is a class-2 OKF deviation |
| [failed-verification::] | A/S — exact verifier-owned failure projection |
| accessed, fixity-sha256 | A — CSL and OAIS/NDSA |
| generated: {by, at}, optional description/stale_after | A — OKF v0.2 |
| literature unscreened/included/excluded/superseded | D — PRISMA screening semantics |
| synthesis draft/stable/deprecated | A — OKF lifecycle |
| project draft/parked/published/corrected/withdrawn | D — publication lifecycle |
| verified events {by, at, check}; actor convention | A — OKF with harness check extension |
| managed-sha256 | S — bridge/verifier-owned exact managed-region witness |

### 6.3 Commands and process vocabulary

| Current term | Status |
|---|---|
| CLI probe, import-note, staleness, backfill-selectors, verify, inbox, scaffold, doctor | A/S — conventional CLI verbs |
| skills setup-vault, project, find-sources, import-source, verify-citations, factcheck-draft, publish, evidence-conventions, synthesis-conventions | Ruled current names |
| MATCHED/UNMATCHED/UNREACHABLE/SKIPPED | S — trust distinction retained over developer-only pytest vocabulary |
| evidence layer, synthesis layer, admission, information flow, project flow | A/S — current process vocabulary |

## 7. Naming-pass status

The pass is complete under the inverted order: OKF structural and metadata terms first; toolchain-bound CSL/Pandoc terms next; CiTO stance names and PRISMA screening language where their domains govern; community vocabulary only where higher tiers are silent. Section 10 is the binding execution manifest. There are no remaining placeholder names blocking the validation slice.

## 8. Superseded promotion analysis

This section previously analyzed semi-anchored names before the naming pass. That analysis is retained only in Git history; its live conclusions were superseded by the 2026-08-20 inversion and wholesale ruling. In particular, the former Appleton-stage adoption and the conclusion that find-papers should remain were superseded: synthesis now uses OKF draft/stable/deprecated, and the entry skill is find-sources. Current promotions and deviations are recorded in §§3–6; §9 below is a historical proposal sheet and §10 is preserved migration evidence.

## 9. Historical naming-pass proposal sheet — **RULED, THEN PARTLY SUPERSEDED**

This table preserves the pre-inversion decision record. All 25 rows were confirmed wholesale on 2026-08-20, but the later OKF inversion and skill-name review supersede rows 20 and 23 as noted; §10 is the binding migration record.

| # | Current | Proposed | Rationale |
|---|---|---|---|
| 1 | plugin `knowledge-harness` (cascades `.harness/`, `hk-`) | **keep** | T7 free choice; descriptive, matches repo; nothing anchors an alternative. Cascade holds: `.harness/`, `hk-managed`, `hk-sel` stay. |
| 2 | `atlas/` + `topic` note + "synthesis layer" | **`synthesis/` + `synthesis` note** (layer name unchanged) | The axis decision: T3 (Cochrane — the field is literally *evidence synthesis*) names folder, note kind, and layer with one word, and discharges the mandatory `topic` collision rename. Beats T5 `wiki/` (ecosystem) per tier order. |
| 3 | `+/` | **`inbox/`** | GTD mass vocabulary; the folder literally holds the review inbox and fleeting captures. The `+`-sorts-first trick is configurable in Obsidian anyway — legibility beats a sort hack. |
| 4 | `literatures/` | **keep** | The only folder with a T1 anchor (ZotLit v2 default) — keeping is a zero-cost toolchain alignment #8 deliberately preserved. Beats `references/` by tie-breaker 1 (a surface we may inhabit vs a vocabulary we resemble). |
| 5 | `calendar/` | **`log/`** | The folder is an append-only machine-written run log, not a planner — "calendar" borders class-3 misdescription. `log/` is llm-wiki/OKF convention (T5) and plainly true. Obsidian's Daily-notes plugin points at any folder name. |
| 6 | `efforts/` + `effort` note | **`projects/` + `project` note** | PARA/GTD mass vocabulary; the spec itself calls this the "PARA sliver"; synergy with the `project` skill (one word, one concept). |
| 7 | `x/` | **keep** | Low stakes; shortness is functional in paths; no anchor argues otherwise. |
| 8 | `retrieved` | **`accessed`** | Fixes the ⚠ stack defect: CSL (T1) names the variable `accessed`; tie-breaker 2 (machine identifier beats prose label). |
| 9 | `attachment-sha256` | **`fixity-sha256`** | OAIS/NDSA `fixity` is THE archival term for exactly this role (verbatim T2-adjacent anchor); algorithm suffix stays explicit. |
| 10 | `[verify-failed::]` | **`[failed-verification::]`** | Wikipedia's `{{failed verification}}` — mass-deployed template name, verbatim (T5 but unanimous and famous). |
| 11 | `[supported-by::]` / `[contested-by::]` | **`[supports::]` / `[disputes::]`** | CiTO verbatim (T2 authority for citation typing) — shorter, machine-aligned, and upgrades the D-status deviation into an anchored adoption. scite's `mentioning` reserved as an optional neutral third stance. |
| 12 | Four-state `MATCHED/UNMATCHED/UNREACHABLE/SKIPPED` | **keep** | pytest names are barred from vault prose by the T6 surface rule (these states appear in inbox entries and skill output, not just CLI), and UNMATCHED-vs-UNREACHABLE is *the* trust distinction — "failed/error" blurs it for non-developers. |
| 13 | Source `status: unreviewed/active/rejected` | **`unscreened/included/excluded`** (+ `superseded` unchanged) | PRISMA/Covidence screening states (T3) — the academic user's professional vocabulary; the strongest domain anchor in the inventory. |
| 14 | Effort `status: drafting` | **`draft`** | OKF verbatim (T4); also the universal word. `parked` stays — plain English, no anchor conflict. |
| 15 | `[confidence:: low/moderate/high]` | **keep — promote to ICD-anchored** | Current name AND values are ICD 203 verbatim already. GRADE's `certainty` would force its 4-level scale (adds *very low*) — a substantive change, not a rename; note as a slice-time option. |
| 16 | "claim address" | **"claim link"** | Micropub `claim` (cited definition) + Obsidian **block link** (T1 — the app's own name for `#^id` links). |
| 17 | `notice-date`/`detection-date` | **keep** | Self-explaining to scholars; bi-temporal literature (`valid/transaction time`) cited as semantics, but its jargon loses legibility (tie-breaker 4: this is vault prose surface). |
| 18 | Trust tiers, actor convention, `verified` events | **keep — promote per §8** | OKF names verbatim; derivation ours, `check` extension documented. |
| 19 | Check names, reason codes, doctor probes | **keep** | Each domain-anchored; the sets are spec-fixed; per-word stakes low. |
| 20 | `find-papers` | **historical keep; superseded by `find-sources`** | The later skill-name review chose the broader trust-core term because admissible sources are not limited to papers. |
| 21 | `atlas-conventions` skill | **`synthesis-conventions`** | Cascade of row 2. |
| 22 | Other skill names, dispositions, `park`, flags | **keep** | Plain-descriptive ruling; no anchor argues. |
| 23 | `growth: seedling …` | **historical adoption; superseded by synthesis `status: draft/stable/deprecated`** | The OKF inversion made the T1 lifecycle binding; `generated.at` supplies recency without parallel Appleton fields. |
| 24 | `authority` | **keep** | Library science's own word (T3); ICD's `source-descriptor` noted as alternative in the skill doc. |
| 25 | `+/review-queue.md` | **`inbox/review-queue.md`** | Path follows row 3; filename unchanged (Covidence review-queue semantics). |

**Net effect if confirmed wholesale:** six renames in vault paths/kinds (rows 2, 3, 5, 6, 8, 13), four inline-field renames (9, 10, 11 ×2), one skill rename (21), one value-set completion (23) — all pre-vault, all ~10-minute Codex operations; the ⚠ defect closes (8); one D-status deviation upgrades to an anchored adoption (11); the collision debt clears (2). Everything else is keep-and-promote.


---

## 10. Rename-wave execution manifest (for the implementing agent)

The naming pass is ruled; this manifest is its implementation order. **One coherent wave**: spec + code + templates + active plan documents move in a single commit (or one commit immediately after the in-flight Plan C merge — implementer's call on worktree state; do not interleave with unrelated work).

### History rule

**Living surfaces rename; history does not.** In scope: `core/` (code, templates, tests), `hooks/`, `skills/`, `docs/specs/` (the spec), the ACTIVE plan (`2026-08-17-plan-c-*`), `README.md`, this document's §6 inventory (statuses flip to current after the wave). Out of scope — never rewrite: `research/`, `analysis/`, completed plans (A, B), audit documents, closed GitHub tickets, git history.

### Rename pairs

**Paths / folders / types** (scaffold `VAULT_DIRS`, templates, fixtures, spec §3 tree, AGENTS.md template, hook vault-detection, tests):

| Old | New |
|---|---|
| `atlas/` | `synthesis/` |
| `atlas/index.md` | `synthesis/index.md` |
| `+/` | `inbox/` |
| `+/review-queue.md` | `inbox/review-queue.md` (`INBOX_PATH` constant) |
| `calendar/` | `log/` (daily log files `log/YYYY-MM-DD.md`) |
| `efforts/` | `projects/` |
| type `topic` | type `synthesis` |
| type `effort` | type `project` |
| publish flag field `"effort"` | `"project"` |
| skill `atlas-conventions` | `synthesis-conventions` |
| skill `vault-setup` | `setup-vault` (verb-first entry-point grammar; skills-name review, ruled 2026-08-20) |
| skill `find-papers` | `find-sources` (vocabulary coherence with the ruled trust-core term; "papers" narrower than the admissible corpus) |

Unchanged: `literatures/`, `x/`, plugin name + `hk-`/`.harness` cascade, type `literature`, type `daily`; skills `project` (noun sanctioned for the frame-opener), `import-source` (singular is honest: find many, import one), `verify-citations`, `factcheck-draft`, `publish`, `evidence-conventions`. **Skill-name grammar system (ruled):** entry points verb-first; the frame-opener may be a noun; guards/references are noun phrases.

**Frontmatter keys / values** (notes.py `MANAGED_FIELDS` + render, events, lints, templates, spec §5):

| Old | New |
|---|---|
| `retrieved` | `accessed` (day-one preservation logic follows the key) |
| `attachment-sha256` | `fixity-sha256` (ack-scope and no-op references follow) |
| status `unreviewed` | `unscreened` |
| status `active` | `included` |
| status `rejected` | `excluded` (`superseded` unchanged; source-status lint strings follow) |
| effort/project status `drafting` | `draft` (`parked/published/corrected/withdrawn` unchanged) |
| `growth`/`planted`/`last-tended` | removed; synthesis uses `status: draft/stable/deprecated` plus `generated.at` (inversion supersession) |

**Inline fields** (claims parser, stamp/clear logic, canonical_content exclusion set per rulings 9/11, contested-set lint, fixtures, spec §5):

| Old | New |
|---|---|
| `[verify-failed:: …]` | `[failed-verification:: …]` |
| `[supported-by:: …]` | `[supports:: …]` |
| `[contested-by:: …]` | `[disputes:: …]` |

**Prose/identifiers**: "claim address" → "claim link" in user-facing prose and docstrings; rename the `claim_address()` identifier too (one-term rule), signature unchanged.

### Acceptance

1. Full suite green, offline and live (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1`).
2. `grep -rE "atlas|efforts/|calendar/|retrieved|attachment-sha256|verify-failed|supported-by|contested-by|unreviewed|drafting|\+/review-queue" core/ hooks/ skills/ docs/specs/ README.md` returns nothing (modulo the words in ordinary prose senses — judge hits, don't blind-replace).
3. Spec, templates, and code agree on every renamed string; Plan C document updated to match its own implementation.
4. This document's §6 inventory updated: confirmed terms move to their new names with status A/S per §8's promotion shortlist; §4's stance-link row moves from deviation to anchored adoption (CiTO); the ⚠ defect row closes.
5. Terminology-related spec sections (§3, §5, §7 skill list, §9 drills) reflect the ruled names.

**Inversion additions (ride this wave):** adopt `stale_after` (optional) + `generated.by/.at` on machine-written notes + optional `description`; synthesis-page frontmatter `growth`/`planted`/`last-tended` → `status: draft|stable|deprecated` + `generated.at` (supersedes the earlier Appleton row); spec §3/§5 updated accordingly.

**OKF structural conformance (ruled 2026-08-20, rides this wave):** add root `index.md` (home page, `okf_version: "0.2"` frontmatter — the one index permitted frontmatter), root `log.md` (machine-maintained dehydrated tail over `log/YYYY-MM-DD.md`, single writer, regenerated), and `type` frontmatter on every machine-written `.md` (`inbox/review-queue.md`, `AGENTS.md`, scaffolded files). OKF's status in §8 upgrades from "OKF-derived, documented divergence" to **structural conformance target** — version-tracking obligation accepted for vault survivability. Fleeting human notes remain the tolerated residual.

**Post-wave: the naming-pass gate on §9 slice execution is CLEARED.**
