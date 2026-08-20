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

**Seven tiers, ordered by the cost of contradiction, evaluated per surface** — a lower tier can win only on a surface the higher tiers are silent about.

- **T1 — Toolchain surfaces the user physically inhabits** (contradiction = class-1, paid daily): **CSL first** (fields in `bibliography.json`, pandoc citations), Zotero UI, BBT/ZotLit conventions, Obsidian (aliases, block links, properties, Bases), Dataview field syntax, Markdown.
- **T2 — Authorities of record** (own semantics AND the data we record; contradiction risks class-3 at boundaries): Crossref (update types), DataCite (relation types), DOI system, W3C (Web Annotation selectors, PROV), CiTO/SPAR (citation typing), IETF where applicable.
- **T3 — Scholarly-method vocabularies** the target user speaks professionally: PRISMA/Cochrane/Covidence (screening, evidence synthesis), GRADE (certainty), ICD 203/206 (sourcing, analytic confidence), plain scholarly English.
- **T4 — Cross-cutting aggregators** (documented, maintained, not inhabited): **OpenAlex** (its ruled home, after CSL), Wikidata, OKF, scite.
- **T5 — Community conventions**: llm-wiki (index.md, wiki/, log), Ideaverse/LYT, Ahrens/PKM, Appleton, GTD/PARA, Wikipedia template vocabulary.
- **T6 — Developer-tool conventions, dev-facing surfaces only** (never vault prose): pytest outcomes, GitHub checks/branch protection, Vale severities, CLI verb lore (doctor, scaffold, probe).
- **T7 — Author's coinage** — only where T1–T6 are silent; author-anchored terms (information flow / project flow) live here by choice.

**Tie-breakers:** (1) the vocabulary whose data we record beats the one we merely resemble; (2) verbatim machine-readable identifiers beat prose labels; (3) versioned spec beats living wiki beats blog; (4) surface fit is absolute.

Domain-scoped authorities (Crossref updates, W3C selectors) retain authority inside their domains regardless of tier walk order.

## 3. Adoptions (precedence applies)

| Term | Source | Status |
|---|---|---|
| `item`, `issued`/`date-parts`, `author`, `locator`/`label`, CSL item types | CSL (T1) | Base applications — the bibliographic layer speaks CSL wholesale; `literature note` names an item's vault projection. |
| `doi`, `pmid` | Registries + CSL + OpenAlex | Aligned everywhere. |
| `cited_by_count` and all recorded API facts | Boundary rule | Recorded verbatim under the source's field names + index + retrieval date. |
| `is_retracted` | OpenAlex (T4) | Verbatim in checker records; internal taxonomy is Crossref's (deviation table). |
| `dehydrated` | OpenAlex | Adopted for index-line/summary projections of full notes. |
| `canonical` | OpenAlex | The surviving entity in any merge/supersession. |
| `topic` | OpenAlex | Adopted for their classification entities ⇒ our synthesis note must be renamed (naming pass, mandatory). |
| Entity framing: IDs as curatable judgments; merged-away IDs permanently redirect to canonical | OpenAlex | Adopted as semantics (spec §5); checkers follow redirects and record the canonical ID verified against. |

**Precedence resolutions (not deviations):** `work` vs `item` and `publication_date` vs `issued` are decided by the order itself — CSL (T1) outranks OpenAlex (T4).

## 4. Documented deviations (a cost class forces each; anchors per deviation)

| Concept | Base term | Our term | Forcing class | Our term's own anchors |
|---|---|---|---|---|
| The cited document (trust core) | OpenAlex `source` = venue | `source` (primary/cited source; `source-sha256`) | **4** — collision | ICD 206 *Source Reference Citation*; scholarly English. Resolution: their entity enters our prose as **`venue`** (OpenAlex's own former name; also DBLP's standard term). |
| Access provenance | OpenAlex `created_date`/`updated_date` | `retrieved` | **3** — theirs describe their record's lifecycle | ⚠ **STACK-CONSISTENCY DEFECT**: CSL (T1) names this variable **`accessed`**; `retrieved` leans on Wikidata's label and APA prose (T4/below). No forcing class was recorded. **Naming pass must rename to `accessed` or supply the missing class.** |
| Post-publication status (internal) | OpenAlex `is_retracted` boolean | Crossref update-type taxonomy, bi-temporal | **2** — boolean discards the taxonomy the gates run on | Crossref (T2) — verbatim already. |
| Citation relations | OpenAlex `referenced_works`/`related_works` | `supported-by`/`contested-by` | **2** — untyped work-level vs stance-typed claim-level | **CiTO** `cito:supports`/`cito:disputes` (T2 — would anchor names verbatim as `[supports::]`/`[disputes::]`); scite stance vocabulary (semantic precedent; its `mentioning` offers a neutral third stance if wanted). Pass's call. |
| Replacement relation | OpenAlex `merged-away` | `superseded`/`superseded-by` | **3** — merging is identity resolution; ours also covers scholarly succession (distinct works) | DataCite `IsObsoletedBy`/`Obsoletes` (T2), IETF `Obsoletes:` headers, Wikidata deprecation family, scholarly English. If the slice shows identity-vs-succession needs separate fields, the pass may split `merged` out as the OpenAlex-aligned special case. |

## 5. Standing rules

- **The precedence order is the default source of names.** Any new concept walks the tiers; deviation requires naming its forcing class in this document.
- **One canonical term per concept**; adopted or deviated, never both.
- **Recorded API facts are boundary-verbatim** (source's field names + index + retrieval date).
- **Semantics migrate freely; deviations are about names only.**
- Interior coinages are **temporary placeholders — not decided, not settled** (author's ruling). The pre-slice **naming pass** owns them: walk the tiers, default to the first vocabulary that names the concept, free coinage only where none does. **The pass blocks §9 slice execution** — the first real vault mints names into git history under deprecate-never-delete, the moment placeholders become permanent.

## 6. User-facing inventory

Harvested from the approved spec and as-built code (Plans A–B merged, Plan C in flight; the grep pass included live check names such as `identifier-discovery`). Legend: **A** anchored · **S** semi-anchored (our name, adopted precedent) · **P** placeholder · **D** documented deviation (§4).

### 6.1 Vault folders and files

| Term | Status | Anchor candidates (for P) |
|---|---|---|
| `+/` (fleeting inbox) | S-weak (Ideaverse `+`; sorts first) | GTD **`inbox/`** (mass vocabulary) vs keep `+` (functional sort argument). |
| `literatures/` | S (ZotLit v2 default folder — toolchain; Ideaverse-adjacent) | Keep (zero-cost ZotLit alignment, #8 kept that UI door open) vs `references/` (CSL: a bibliography is a reference list; Ahrens). |
| `atlas/` | S-weak (Ideaverse) | **llm-wiki `wiki/`** (all 7 surveyed implementations) vs evidence-synthesis **`synthesis/`** (T3 — pairs with the layer name) vs keep. |
| `calendar/` | S-weak (Ideaverse) | Obsidian **Daily notes** plugin (`daily/`, T1-ish) vs llm-wiki/OKF **`log/`** (append-only semantics) vs keep. |
| `efforts/` | S-weak (Ideaverse) | PARA/GTD **`projects/`** (mass; synergy with the `project` skill; spec already calls this the "PARA sliver") vs keep. |
| `x/` | S-weak (Ideaverse) | Keep, or `system/`/`meta/` (weak). Low stakes. |
| `AGENTS.md` | A (harness-ecosystem convention) | — |
| `+/review-queue.md` | P | Covidence/Rayyan **screening/review queue** (T3) anchors the semantics; name survives. |
| `atlas/index.md` | S (llm-wiki convention — every surveyed implementation) | Keep `index.md`. |
| `x/bibliography.json` | S (content is CSL) | — |
| `calendar/YYYY-MM-DD.md` + entry format | P | Follows the calendar/daily/log folder decision. |
| `.harness/`, `hk-` marker prefixes (`%%hk-managed%%`, `hk-sel`) | P | Cascade from the **plugin name** decision — decide that first. |
| "managed region" | S (ZotLit convention) | — |

### 6.2 Note kinds (`type` values)

| Term | Status | Anchor candidates |
|---|---|---|
| `literature` | S (Ahrens "literature note" — the PKM mass term; ZotLit's own docs) | Keep. |
| `topic` (synthesis page) | **P + collision — mandatory rename** | **`synthesis`** (T3, Cochrane/PRISMA — one word could name folder, layer, and note kind) vs llm-wiki **`concept`** (T5; weak collision with OpenAlex's deprecated concepts) vs Matuschak **`evergreen`** (T5). |
| `effort` | P | PARA **`project`** (with the folder decision). |
| `daily` | S (Obsidian Daily notes plugin — toolchain) | Keep. |

### 6.3 Claim language

| Term | Status | Anchor candidates (for P) |
|---|---|---|
| Evidence-boundary tags `(quote)(paraphrase)(inference)(open-question)` | S (PROV/ICD 203 semantics) | Current names plainer than both anchors; keep, cite. |
| `[@citekey]`, `[@citekey, p. N]` | A (pandoc/CSL) | — |
| `^claim-id` anchors; "claim address" | Syntax A (Obsidian block links); "claim" S (micropub/nanopub); "address" P | **"claim link"** = micropub `claim` + Obsidian **block link** at once. |
| Blockquotes; inline fields `[k:: v]` | A (Markdown; Dataview) | — |
| `[confidence:: low\|moderate\|high]` | S (ICD 203) | GRADE alternative name: `[certainty-…]` (GRADE says *certainty*). |
| `[confidence-reason::]` | P | **GRADE** explanatory-footnote/downgrade-reason semantics. |
| `[status:: live/deprecated]` + transition fields | S (Wikidata-shaped); `superseded-by` D | — |
| `[supported-by::]`/`[contested-by::]` | D | CiTO verbatim option — §4. |
| `[retraction-ack::]` | P (name); mechanism spec-fixed | Wikipedia intentional-citation convention (semantics). |
| `[verify-failed::]` | P | **Wikipedia `{{failed verification}}`** — rename `[failed-verification::]` for a verbatim mass-deployed anchor. |
| Selector comment `hk-sel prefix/suffix` | S (W3C selector semantics); `hk-` P | Prefix cascades from plugin name; fields already WADM-named. |

### 6.4 Frontmatter keys

| Term | Status | Anchor candidates (for P) |
|---|---|---|
| `citekey`, `zotero-key`, `doi`, `pmid`, `url`, `aliases`, `title` | A | — |
| `version` | S (Force11) | — |
| `retrieved` | D ⚠ | See §4 — likely becomes CSL `accessed`. |
| `attachment-sha256` | P (name; OAIS semantics) | **OAIS/NDSA `fixity`** — `fixity-sha256` anchors verbatim. |
| `archive-url` | S (Wikidata P1065) | — |
| `authority` | S (library-science authority control; ICD 206 source descriptors) | Alternative verbatim name: `source-descriptor` (ICD 206). |
| Source `status: unreviewed/active/rejected` (+ `superseded` D) | P (values) | **PRISMA/Covidence screening states**: `unscreened/included/excluded` — the strongest domain anchor in the inventory. |
| `verified` events `{by, at, check}` | S (OKF's exact field name + shape) | Keep. |
| Actor convention `human:`/`agent/ver`/`process:` | S (OKF) | — |
| `growth`, `planted`, `last-tended` | S (Appleton) | Adopt her full stage set verbatim (seedling/budding/evergreen). |
| Effort `status: drafting/parked` (+ `published/corrected/withdrawn` anchored) | P | OKF `draft`; journal lifecycle (*in preparation/submitted*); `parked` ↔ GTD *someday* / Ideaverse *sleeping*. |

### 6.5 Verification vocabulary

| Term | Status | Anchor candidates (for P) |
|---|---|---|
| Four-state `MATCHED/UNMATCHED/UNREACHABLE/SKIPPED` | P (names; distinction spec-fixed) | **pytest `passed/failed/error/skipped`** (T6, 1:1 — *error* = could-not-run is exactly UNREACHABLE) vs GitHub check conclusions vs keep (more precise about comparison semantics). Genuine trade-off. |
| Check names (`citekey, doi, metadata, update-notice, quote, staleness, identifier-discovery, web-archive, evidence-layer, append-only, claim-immutability, published-drift, source-status, contested`) | P each | Each check's own domain anchors it; keep, cite per-check. |
| Trust tiers `unverified/machine-confirmed/human-reviewed` | S (OKF's tier names verbatim) | Keep at zero cost. |
| Reason codes (17, spec-fixed set) | P (words) | Covidence exclusion-reason discipline anchors the *set*; per-word stakes low. |
| Update-notice blocking/warn type sets | A (Crossref) | — |
| `notice-date`/`detection-date` | P (names; bi-temporal semantics anchored) | Bi-temporal DB vocabulary (Snodgrass/SQL:2011 *valid/transaction time*; Zep `valid_at/created_at`) — `valid-at`/`recorded-at` verbatim option vs keep (more self-explaining). |
| Inbox entry/ack fields (`[id::]`, `[ack::]`, `[target-hash::]`); "review inbox", "standing ack" | P | Covidence review-queue semantics; keep names. |
| `COMMIT_CLOSING`/`PUBLISH_CLOSING`; closing-class/warn-tier | P | **Vale severities** `error/warning` (T6) — instantly legible to CI users. |
| Publish gate / armed / 8-block bound / bypass token | S (GitHub required-checks + press-check precedent) | Keep. |
| `doctor` + probe names | S (`doctor` = brew/flutter/npm CLI convention); probes anchored by subjects | Keep. |

### 6.6 Commands

| Term | Status | Anchor candidates |
|---|---|---|
| CLI verbs `probe, import-note, staleness, backfill-selectors, verify, inbox, scaffold, doctor` + flags | S (CLI conventions: doctor, scaffold=Rails/Yeoman, probe=k8s, verify=git family) | Keep; `import-note` follows folder/kind renames. |
| Skill names (nine) | P each | `find-papers` → PRISMA *identification* (`identify-papers`) option; `factcheck-draft` S (IFCN "fact-check"); conventions skills cascade from folder/layer renames; style (plain-descriptive) is a #11 decision, words are not. |
| Dispositions `mark-published/park/keep-drafting`; typed `discard` | P | `park` ↔ GTD someday / Ideaverse sleeping. Low stakes. |
| Plugin name `knowledge-harness` | P — **the one genuinely free name; cascades to `.harness/`, `hk-`, skill namespace** | Decide first. |

### 6.7 Process vocabulary

| Term | Status | Anchor candidates |
|---|---|---|
| "vault" | A (Obsidian) | — |
| evidence layer / synthesis layer | P | **Evidence synthesis** (Cochrane — the field's own name splits into exactly our two layers; best single anchor discovery of the pass). |
| "admission" | S (STORM source-admission, cited in spec) | Keep. |
| information flow / project flow | T7 by choice (author's coinage) | Keep. |
| "thin slice", "drill" | P (pre-user build vocabulary) | XP *tracer bullet/walking skeleton*; optional. |
| `dehydrated`, `canonical`, `venue` | A/D per §3–§4 | — |

## 7. Naming-pass decision order

1. **Plugin name** (cascades: `.harness/`, `hk-` markers, skill namespace).
2. **The evidence/synthesis axis** — one choice names the layer, the folder, and the synthesis-note kind, and discharges the mandatory `topic` rename (T3 `synthesis` leads unless ruled otherwise).
3. **Folders** — with #2 decided, the remaining five are independent (`inbox/`, `references/` vs `literatures/`, `daily/` vs `log/` vs `calendar/`, `projects/` vs `efforts/`, `x/`).
4. **Four-state names** (pytest vs current) and **screening statuses** (PRISMA mapping) — recorded into events/inbox forever after the first vault.
5. **The ⚠ `retrieved`→`accessed` defect** — rename per CSL (T1) or supply the forcing class the original ruling lacked.
6. Check names, reason codes, remaining inline fields (`failed-verification`, `fixity`), skill verbs — S-or-keep at leisure, before the vault exists.
7. Everything marked A or D (post-⚠-resolution) is out of scope.


---

## 8. Promotion analysis: implications of making each S an A

Added 2026-08-20. **S → A means one of two things**: *(adopt)* rename to the anchor's exact term so the word IS the external vocabulary, or *(commit)* declare the anchor normative — we track its changes and owe conformance. Either way, promotion **locks the term against the naming pass** (A is out of the pass's scope) and prices every future rename at a real cost class. General law surfaced by this analysis: **promotion is sound only for T1–T3 anchors (stable, versioned, or professionally spoken); T5 community anchors can inspire but cannot govern — promoting against them creates fictional conformance to an unversioned source.** T4 is case-by-case.

| S term | Anchor (tier) | Promotion path | What we gain | What it costs / risks | Verdict |
|---|---|---|---|---|---|
| `literatures/` | ZotLit default folder (T1) | commit (name already matches) | If ZotLit is ever adopted as UI (#8 kept the door open), zero-config compatibility becomes *guaranteed*, not incidental | Couples a folder name to one plugin's default; ZotLit could change it; blocks the `references/` naming-pass option | **Defer to the pass** — promote only if the pass keeps the name *because of* ZotLit |
| `literature` (note kind) | Ahrens (T5 mass term) + ZotLit docs | commit | The PKM world's own word; every tutorial ever written explains it for us | Ahrens is a book, not a spec — nothing to conform to; harmless but fictional | **Leave S** — the anchor governs usage, not us |
| `atlas/`, `calendar/`, `efforts/`, `x/`, `+` | Ideaverse (T5, informal artifact) | commit | None beyond familiarity to LYT users | Milo can reorganize Ideaverse tomorrow; conformance is fiction; **locks the six folders the naming pass most needs freedom on** | **Leave S / actively do not promote** — strongest do-not case in the table |
| `atlas/index.md` | llm-wiki convention (T5, but unanimous across 7 implementations) | commit | Interop with any llm-wiki-reading tool; `index.md` is also a web-server convention (near-T1) | Convention is informal but redundantly anchored; risk ≈ nil | **Promote** — cheap, real, survives the atlas folder rename (filename is what matters) |
| "managed region" | ZotLit (T1 convention) | commit | Regeneration semantics documented by ZotLit for free; marker interop if ZotLit adopted | Our markers are `hk-` not `zt-` — promotion covers the *concept*, not the delimiter; fine | **Promote the concept**, keep `hk-` delimiters (plugin-name cascade) |
| Evidence-boundary tags | PROV/ICD 203 semantics (T2/T3) | commit (semantic conformance) | The tags gain an auditable definition: quote ⇔ `wasQuotedFrom`, inference ⇔ ICD judgment — reviewers can check our usage against a spec | Obligates the evidence-conventions skill to teach the mapping; PROV is frozen (safe); ICD amendable (slow) | **Promote semantically** — this is the trust core; an external definition strengthens it. Names stay ours (already plainer) |
| `[confidence::]` scale | ICD 203 (T3) | adopt values verbatim (already `low/moderate/high`) + commit | The IC's calibrated usage guidance comes free; GRADE crosswalk documented | GRADE says *certainty* — committing to ICD forecloses the GRADE rename | **Promote to ICD** unless the pass prefers GRADE's word; both T3, either sound |
| Status/transition fields (`live/deprecated` + actor/date/reason) | Wikidata deprecation family (T4) | commit | Mass-deployed semantics for deprecate-never-delete; ranks precedent for future needs | Wikidata property semantics evolve by community process; loose coupling only | **Promote semantics, not names** — current state, made explicit |
| Selector fields (`exact/prefix/suffix`) | W3C WADM (T2) | **already verbatim** — commit formally | Conformance claim becomes checkable; future WADM export is a projection, not a translation | W3C TR is frozen — no drift risk | **Promote** — free and real; the strongest promotion candidate |
| "claim" | Micropublications/nanopub (T2-ish, academic spec) | commit | The trust object gains a published formal model; "claim" usage auditable against it | Micropub is a paper-spec (frozen, unmaintained) — anchor is stable but dead; conformance partial by design (we flattened the tri-graph) | **Promote as cited definition**, not conformance |
| `version` | Force11 (T3 principles) | commit | Citation-principles pedigree for reviewers | Principles, not schema — nothing concrete to conform to | **Leave S** — cite, don't commit |
| `archive-url` | Wikidata P1065 (T4) | adopt name? (`archive-url` vs P1065 "archive URL" — already matches) | Alignment is already exact | None | **Promote by observation** — it is A in all but label; record it |
| `authority` | Library-science authority control + ICD 206 source descriptors (T3) | adopt ICD's `source-descriptor`? | ICD verbatim would make the field auditable against ICD 206's descriptor list | Renames a field for a standard the user doesn't read daily; `authority` is the librarian's own word | **Leave S**, offer the pass both words |
| `verified` events | OKF (T4, versioned v0.2) | commit to OKF conformance | Interop with OKF consumers; schema documented externally; `{by, at, check}` = their shape + our extension | OKF is young (v0.2, one vendor); committing means tracking 0.3+; our `check` field is already an extension — full conformance impossible | **Promote as "OKF-derived, documented divergence"** — commit to the actor convention and tier names, not whole-schema conformance |
| Actor convention | OKF (T4) | adopt verbatim (already is) + commit | One line of external doc replaces ours | Same OKF-youth risk, but the convention is tiny and stable | **Promote** — smallest possible conformance surface |
| Trust tiers | OKF tier names verbatim (T4) | commit | Names externally defined; derivation stays ours | Tier *derivation* is ours (stricter than OKF's advisory tiers) — commit names only or the divergence becomes non-conformance | **Promote names only**, derivation explicitly ours |
| `growth/planted/last-tended` + stages | Appleton (T5, personal essay) | adopt her full stage set | Digital-garden users recognize it instantly | Essay-anchored — no spec; her stages are hers to change | **Adopt values, leave status S** — same as Ahrens |
| Publish gate family | GitHub required checks + press-check (T6/precedent) | commit to GitHub vocabulary? | CI users' instant legibility | T6 never names vault prose — the gate speaks in skill prose too; partial surface only | **Leave S** — T6 scope rule bars full promotion |
| `doctor`, CLI verbs | CLI conventions (T6) | commit (names already conventional) | Self-documenting to any developer | Convention, not spec — nothing to track | **Promote by observation** — costless; record as A-by-convention on the CLI surface |
| "admission" | STORM (T4 paper) | commit as cited definition | The trust boundary's key verb gains a citable origin | Paper-anchored; frozen | **Promote as cited definition** (like "claim") |

### Promotion summary

- **Promote now (real, free):** WADM selector fields; `atlas/index.md`; managed-region concept; actor convention; OKF tier *names*; `archive-url`; CLI-surface verbs by observation; evidence-boundary tags *semantically*.
- **Promote as cited definition (anchor frozen/dead but stable):** "claim" (micropub), "admission" (STORM).
- **Promote with scoped divergence:** `verified` events (OKF-derived, `check` extension documented).
- **Defer to the naming pass (promotion would pre-empt it):** `literatures/`, `[confidence::]` ICD-vs-GRADE.
- **Do not promote (T5 anchors cannot govern):** the five Ideaverse folder names, `literature` note kind, Appleton statuses, Ahrens-anchored terms — they stay S by design; T5 inspires, never governs.


---

## 9. Naming-pass proposal sheet — **RULED (author confirmed wholesale, 2026-08-20)**

One concrete proposal per open term, derived from the ruled tier order, tie-breakers, and the §8 promotion analysis. **All 25 rows confirmed wholesale — the naming pass is DECIDED; the §9-slice gate clears when the rename wave (§10) lands.** Cascade decisions first; every A-status term not listed is unchanged by definition.

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
| 20 | `find-papers` | **keep** | #11 ruled plain-descriptive style; PRISMA's *identification* noted in the skill's doc line, not its name. |
| 21 | `atlas-conventions` skill | **`synthesis-conventions`** | Cascade of row 2. |
| 22 | Other skill names, dispositions, `park`, flags | **keep** | Plain-descriptive ruling; no anchor argues. |
| 23 | `growth: seedling …` | **adopt Appleton's full stage set** (`seedling/budding/evergreen`) | Already S to her essay; the complete value set costs nothing and is recognizable to garden-vocabulary users. Status stays S (T5 inspires, never governs). |
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
| `growth` values | full Appleton set `seedling/budding/evergreen` |

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

**OKF structural conformance (ruled 2026-08-20, rides this wave):** add root `index.md` (home page, `okf_version: "0.2"` frontmatter — the one index permitted frontmatter), root `log.md` (machine-maintained dehydrated tail over `log/YYYY-MM-DD.md`, single writer, regenerated), and `type` frontmatter on every machine-written `.md` (`inbox/review-queue.md`, `AGENTS.md`, scaffolded files). OKF's status in §8 upgrades from "OKF-derived, documented divergence" to **structural conformance target** — version-tracking obligation accepted for vault survivability. Fleeting human notes remain the tolerated residual.

**Post-wave: the naming-pass gate on §9 slice execution is CLEARED.**
