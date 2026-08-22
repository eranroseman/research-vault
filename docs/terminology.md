# Terminology reference

This document is the naming authority for knowledge-harness vault and tooling vocabulary: the cost model that governs renames, the ruled precedence order for anchor sources, the resulting adoptions and deviations, and the current user-facing inventory. Decisions carry inline dates. The naming pass, its promotion analysis, and the historical proposal sheet that got us here are not reproduced below — they live in this file's git history.

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

## 3. Adoptions and deviations

### 3.1 Current adoptions (inverted T1–T8 order)

| Term or contract | Authority | Current status |
|---|---|---|
| OKF v0.2 reserved files (`index.md`, `log.md`), non-empty concept `type` | OKF (T1) | Adopted; vaults are structural OKF bundles. |
| Optional `description` / `stale_after` (pass-through fields; no writer rewrites them) | OKF (T1) | Adopted per-note fields. |
| `generated: {by, at}` on machine-written notes | OKF (T1) | Adopted alongside `verified` events. |
| Actor convention (`knowledge_harness/<version>` for process-written records; `human:`-prefixed actor for human-attributed ones) | OKF (T1) | Adopted; previously an S-promotion, now a plain T1 base application. |
| `verified` event shape `{by, at, check}` | OKF (T1), harness `check` extension | Adopted; previously an S-promotion, now a plain T1 base application. |
| Trust tier names: `unverified` → `machine-confirmed` → `human-reviewed` (cumulative) | OKF (T1) | Adopted; previously an S-promotion, now a plain T1 base application. |
| `accessed` | CSL (T2) | Adopted; the former stack-consistency defect is closed. |
| `supports` / `disputes` (field names) | CiTO (T3) | Adopted for typed claim links. The structural choice to type the lineage at all — rather than OKF's untyped links — is tracked as a deviation below; only the field names are the adoption here. |
| `unscreened` / `included` / `excluded` | PRISMA/Covidence (T4) | Adopted for literature screening; `superseded` remains the scholarly-succession state. |
| `synthesis/` and `type: synthesis` | Evidence-synthesis vocabulary (T4) | Adopted; the OpenAlex `topic` collision is gone. |
| Synthesis-page lifecycle: `status: draft \| stable \| deprecated` + `generated.at` | OKF (T1) | Adopted; supersedes the Appleton `growth`/`planted`/`last-tended` fields — `generated.at` covers recency, and no cost class rescues a parallel three-state system (superseded 2026-08-20 with the OKF inversion). |
| `draft` (shared project/synthesis value) | OKF (T1) | Adopted where shared; the surrounding lifecycles (`parked/published/corrected/withdrawn`, `unscreened/included/excluded`) remain kind-specific. |
| `inbox/`, `log/`, `projects/` | GTD/PARA and log convention (T6) | Ruled current folder vocabulary. |
| `fixity-sha256` | OAIS/NDSA (T3/T4) | Adopted archival term. |
| `failed-verification` | Wikipedia template vocabulary (T6) | Adopted exact inline-field name. |
| `item`, `issued`/`date-parts`, `author`, `locator`/`label`, CSL item types | CSL (T2) | Base applications in the bibliographic layer. |

### 3.2 Current documented deviations

Two of the rows below are not OKF-forced — they deviate from a lower tier (Crossref, OpenAlex) that OKF is silent on. The "base term" column names whichever tier's vocabulary we decline.

| Concept | Base term (tier) | Harness contract | Forcing class |
|---|---|---|---|
| Per-claim attribution | Footnotes keyed to `sources[].id` (OKF, T1) | Pandoc `[@citekey, locator]` | **1** — permanent CSL/BBT/Zotero/Pandoc surface mismatch |
| Source identity | `sources` / `resource` (OKF, T1) | `citekey` / `doi` / `url` | **1 + 2** — toolchain binding and richer registry identity |
| Untyped lineage | Untyped links (OKF, T1) | Typed `supports` / `disputes` claim links | **2** — stance is trust substance; the field names themselves are CiTO-anchored (§3.1) |
| Literature lifecycle (screening states) | `draft`/`stable`/`deprecated` (OKF, T1) | `unscreened`/`included`/`excluded`/`superseded` | **2** — screening is not document maturity |
| Project lifecycle | `draft`/`stable`/`deprecated` (OKF, T1) | `draft`/`parked`/`published`/`corrected`/`withdrawn` | **2** — publication/correction gate states would be lost |
| Source vs. venue | `source` = journal/repository/outlet (OpenAlex, T5) | `source` = the cited document (scholarly sense, T4); `venue` names the outlet | **4** — OpenAlex's term already means something else in our context |
| Update-notice taxonomy | Flat `update-type` taxonomy, Crossref-DOI-scoped only (Crossref, T3) | Two-class blocking/warn split; DataCite-registered DOIs route through OpenAlex `is_retracted` (reusing Crossref's own `retraction` type name rather than inventing a new one) — any other non-Crossref, non-DataCite registration agency returns UNREACHABLE rather than being silently treated as clean | **1 + 2** — registry-scope mismatch (DataCite/arXiv items don't expose Crossref's taxonomy at all) plus the flat taxonomy carries no closure-class structure |
| Replacement relation | Identity merge (OKF, T1) | `superseded` / `superseded-by` | **3** — also covers succession between distinct scholarly works |

The former `retrieved` deviation (⚠ stack-consistency defect) is closed: `accessed` shipped with this wave (§3.1).

## 4. Standing rules and current inventory

### Standing rules

- The inverted T1–T8 precedence order remains the default source of names; deviation requires one of the four cost classes.
- One canonical term represents each concept. No compatibility aliases are needed before the first vault.
- Recorded API facts remain boundary-verbatim, with source field names, index, and access date.
- Reserved basenames: root `index.md` carries `type: "index"` and `okf_version: "0.2"`; root `log.md` carries exactly `type: "log"` (machine-regenerated). Every *nested* `index.md` (e.g. `synthesis/index.md`) is permanently frontmatter-free — reserved and excluded from the OKF `type` requirement outright, not merely lacking one yet.
- The naming pass completed 2026-08-20; the foundation spec's validation-slice gate is cleared. New terms walk the tiers; placeholder status no longer exists — every term is A, S, or D.

### 4.1 Vault paths and note kinds

Legend: **A** externally anchored · **S** ruled convention · **D** documented deviation.

| Current term | Status |
|---|---|
| `inbox/`; `inbox/review-queue.md` (`type: "review-queue"`) | A/S — GTD inbox; typed append-only review queue |
| `literatures/`; `type: literature` | A/S — ZotLit/Ahrens projection vocabulary |
| `synthesis/`; `synthesis/index.md`; `type: synthesis` | A — evidence-synthesis vocabulary; nested index is reserved |
| `log/`; `log/YYYY-MM-DD.md` (`type: "daily"`); root `log.md` (`type: "log"`, single writer via `okf.regenerate_log`, called from `import-note` and `mark-withdrawn` (and once at scaffold time)) | A/S — append-only daily directory plus distinct reserved root tail |
| `projects/`; `type: project` | A/S — PARA/GTD project vocabulary |
| `system/`; `system/templates/`; `system/bases/`; `AGENTS.md` (`type: "guide"`); `.harness/`; `hk-` markers | S — ruled harness conventions; `system/` sorts last, out of the knowledge folders' way (renamed from `x/`) |
| root `index.md` (`type: "index"`, `okf_version: "0.2"`) | A — OKF bundle root, links to every vault folder |

### 4.2 Claim and metadata language

| Current term | Status |
|---|---|
| `[@citekey, locator]`, `^claim-id`, claim link | A/D — Pandoc/CSL and Obsidian block-link surfaces |
| `[supports::]` / `[disputes::]` | A — CiTO names; typed lineage is a class-2 OKF deviation |
| `[failed-verification::]` | A/S — exact verifier-owned failure projection |
| `accessed`, `fixity-sha256` | A — CSL and OAIS/NDSA |
| `generated: {by, at}`, optional `description`/`stale_after` | A — OKF v0.2 |
| literature `unscreened`/`included`/`excluded`/`superseded` | D — PRISMA screening semantics |
| synthesis `draft`/`stable`/`deprecated` | A — OKF lifecycle; supersedes Appleton `growth`/`planted`/`last-tended` (superseded 2026-08-20) |
| project `draft`/`parked`/`published`/`corrected`/`withdrawn` | D — publication lifecycle |
| `verified` events `{by, at, check}`; actor convention | A — OKF with harness `check` extension |
| `managed-sha256` | S — bridge/verifier-owned exact managed-region witness |

### 4.3 Commands and process vocabulary

| Current term | Status |
|---|---|
| CLI `probe`, `import-note`, `staleness`, `backfill-selectors`, `verify`, `factcheck`, `trust-tier`, `inbox`, `finding`, `scaffold`, `doctor` | A/S — CLI subcommand set (mixed verb/noun forms — conventional for CLIs, not uniformly verbs); `finding` is the §3 review-record writer, general to every non-deterministic-pipeline finding (factcheck-draft's adjudications, Task 5's holds); `factcheck` is a read-only report (deterministic claim selection for one factored-verification pass, spec §6) — same shape as `verify`, writes nothing, sits beside `finding` the way `verify-citations` sits beside `factcheck-draft`; `trust-tier` (Task 4) is a read-only report over `events.trust_tier` (spec §5's cumulative unverified/machine-confirmed/human-reviewed derivation) — same shape as `factcheck`/`verify`, writes nothing; `project`'s resume-orientation step calls it once per cited note to display that note's tier |
| CLI publish surface `arm-publish`, `disarm-publish`, `mark-published`, `mark-corrected`, `mark-withdrawn`, `park`, `ack` | S — spec §6's own words: the gate is *armed*, the day-one menu reads *mark-published*/*park*, the post-publish menu *corrected*/*withdrawn*; `ack` is the §3 acknowledgment's serialization spelling (§4.4) |
| skills `setup-vault`, `project`, `find-sources`, `import-source`, `verify-citations`, `factcheck-draft`, `publish`, `evidence-conventions`, `synthesis-conventions` | S — ruled current names |
| `MATCHED`/`UNMATCHED`/`UNREACHABLE`/`SKIPPED` | S — trust distinction retained over developer-only pytest vocabulary |
| evidence layer, synthesis layer, admission, information flow, project flow | A/S — current process vocabulary |

### 4.4 Identifier inventory (adopted 2026-08-21, core naming audit)

Check ids, doctor probe ids, and reason codes are governed coined identifiers (S) written verbatim
to durable surfaces (`inbox/review-queue.md`, doctor output). Grammar: kebab-case slugs; per-claim
checks use composite ids `check:{claim-link}:{target-kind}` (e.g. `quote:{claim-link}:managed-region`).

| Group | Members | Status |
|---|---|---|
| check ids | `citekey`, `doi`, `metadata`, `quote`, `update-notice`, `evidence-layer`, `identifier-discovery`, `web-archive`, `screening-state` (renamed from `source-status`), `disputed-claim` (renamed from `contested`), `publish` (the project-level publication event `mark-published`/`mark-corrected` mints, §5), `factcheck` (Task 3 — §6's factored-verification row; LLM-adjudicated, never mints a `verified` event, only findings via the `finding` verb) | S — spec §6 rows carry these slugs backticked; `factcheck` is this document's own coinage for a row the spec names in prose but does not slug |
| doctor probe ids | `tree`, `machine-config`, `zotero`, `bbt`, `autoexport`, `staleness`, `remote`, `backup`, `inbox`, `okf` | S — doctor rows use the Outcome vocabulary (`check`/`result`/`reason`; `Probe` shape unified 2026-08-21) |
| reason codes | the `REASON_CODES` set at HEAD, incl. `superseded-note` (renamed from `superseded-source`), `fuzzy-quote`, `not-admitted`, `drift`, `outage`, `budget-cap` (Task 3 — factored-verification's budget-cap exclusions; the finding naming the skipped set) | S — one registry, code is authoritative; additions require a reference row |

Register split, ruled: **`surface`** (enforcement point — `--surface`, `CLOSING_BY_SURFACE`) is spec §6's
anchored vocabulary; this document's "tool surface" (T2 prose) is a different register and never
co-occurs with it on a vault/CLI surface. Both stand.

Field/concept pairs, ruled: **`ack`** is the spec-§3 serialization spelling of the concept
**Acknowledgment** (CONTEXT.md) — not an ungoverned abbreviation. **`rw`** = Retraction Watch
(community's own shorthand) on CLI flags and internal names; registry recorded here.
`hk-selector` (renamed from `hk-sel` 2026-08-21) spells its noun on the durable note surface.

Deferred with a home (not endorsed, not lost): module/function stutter (`checks.check_metadata` …)
and noun-named functions — per-name judgment at the architecture deepening pass (the two findings
collide: de-stuttering creates noun functions); `FileImage`/`CapturedOutput` naming vs git's `blob`
vocabulary — same pass.
