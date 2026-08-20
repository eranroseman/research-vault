# Terminology — decisions, precedence, inventory, and the naming pass

Consolidated record, 2026-08-20 (merges and supersedes the same-day `terminology-decision` and `user-facing-terminology` documents; all rulings author-confirmed). Owns four things: the **cost model**, the **ruled precedence order** for anchor sources, the **decisions** taken against it (adoptions and deviations), and the **complete user-facing inventory** with anchor candidates — the working package for the **naming pass, which blocks §9 slice execution**.

## 1. Cost model

**Rename churn is priced at zero** (~10 minutes of implementation time pre-users; occurrence counts are not costs; sunk effort is not an argument). Exactly four real cost classes justify deviating from the precedence order:

1. **Permanent surface mismatch** — with tool surfaces we don't control.
2. **Information loss** — the base term carries less structure than the concept needs.
3. **Semantic falsification** — the base term would make our records state something false.
4. **Collision/ambiguity** — the base term already means something else in our context.

No class binding ⇒ the precedence order's term is adopted. Taste never justifies deviation.

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
