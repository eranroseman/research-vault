# User-facing terminology inventory

2026-08-20. The complete list of terms a vault user encounters, harvested from the approved spec and the as-built code (Plans A–B merged, Plan C in flight). **This is the naming pass's working input** (the pass blocks §9 slice execution; rules in [2026-08-20-terminology-decision.md](2026-08-20-terminology-decision.md): walk CSL → OpenAlex → domain authorities; free coinage only where no vocabulary names the concept).

Status legend: **A** = anchored (external vocabulary or toolchain surface — renaming pays a real cost class) · **P** = placeholder (free to rename until the first real vault) · **D** = documented deviation (terminology doc) · **S** = semi-anchored (our coinage, but shaped by an adopted precedent).

## 1. Vault folders and files (seen daily, in every path)

| Term | Status |
|---|---|
| `+/` (fleeting inbox) | P |
| `literatures/` | P |
| `atlas/` | P |
| `calendar/` | P |
| `efforts/` | P |
| `x/` (templates, bases, bibliography) | P |
| `AGENTS.md` | A (harness-ecosystem convention) |
| `+/review-queue.md` (the review inbox) | P |
| `atlas/index.md` (the atlas index) | P |
| `x/bibliography.json` | S (content is CSL) |
| `calendar/YYYY-MM-DD.md` (daily log) | P (name); entry format `- HH:MM <actor> — <action>` P |
| `.harness/` (machine-local: `machine.json`, publish flag) | P |
| `%%hk-managed%%` / `%%/hk-managed%%` (managed region markers) | P (`hk-` prefix); "managed region" S (ZotLit convention) |

## 2. Note kinds and their `type` values

| Term | Status |
|---|---|
| `literature` (note; "literature note") | P (the concept "item projection" is CSL-anchored; the note name is ours) |
| `topic` (synthesis page) | **P + collision** — must be renamed (OpenAlex `topic` adopted for classification entities; the pass owes this one) |
| `effort` (note/folder; "manuscript/deliverable") | P |
| `daily` | P |

## 3. Claim language (written and read in every note)

| Term | Status |
|---|---|
| Evidence-boundary tags: `(quote)` `(paraphrase)` `(inference)` `(open-question)` | S (grounded in PROV/ICD 203 semantics; names ours) |
| `[@citekey]`, `[@citekey, p. N]` (citation + locator) | A (pandoc/CSL) |
| `^claim-id` / `c-<8hex>` anchors; "claim address" `citekey#^id` | P ("claim address"); anchor syntax A (Obsidian blocks) |
| Blockquote quote lines (`> …`) | A (Markdown/§5) |
| Inline fields `[key:: value]` | A (Dataview convention) |
| `[confidence:: low|moderate|high]` | S (ICD 203 scale) |
| `[confidence-reason:: …]` | P |
| `[status:: live]` / `[status:: deprecated]` + `[deprecated-at::]` `[deprecated-by::]` `[reason::]` `[superseded-by::]` | S (Wikidata-shaped); `superseded-by` D (vs OpenAlex `merged-away`) |
| `[supported-by::]` / `[contested-by::]` (stance links) | D (vs `referenced_works`; stance-typed) |
| `[retraction-ack:: <code> …]` | P (name); mechanism spec-fixed |
| `[verify-failed:: <check>/<date>]` | P |
| Selector comment `<!-- hk-sel prefix=".." suffix=".." -->` | S (W3C selector semantics; `hk-sel` P) |

## 4. Frontmatter keys (literature/topic/effort notes)

| Term | Status |
|---|---|
| `citekey` | A (BBT/pandoc) |
| `zotero-key` | A (ZotLit convention) |
| `doi`, `pmid`, `url` | A (registries) |
| `version` | S (Force11 designator) |
| `retrieved` | D (vs OpenAlex dates; Wikidata P813 semantics) |
| `attachment-sha256` | P (name); fixity semantics OAIS-anchored |
| `archive-url` | S (Wikidata P1065 semantics) |
| `authority` | P |
| `status: unreviewed | active | superseded | rejected` (source-level) | P (values); `superseded` D |
| `verified` events `{by, at, check}` | S (OKF-shaped); "verified" P |
| Actor convention `human:<id>` / `<agent>/<version>` / `process:<id>` | S (OKF) |
| `aliases` | A (Obsidian) |
| `title`, `growth`, `planted`, `last-tended` (topic pages) | `title` A; `growth`/`planted`/`last-tended` S (Appleton maturity) |
| `status: drafting | parked | published | corrected | withdrawn` (efforts) | P (values; `corrected` IFCN-shaped) |

## 5. Verification vocabulary (CLI output, inbox lines, hook warnings)

| Term | Status |
|---|---|
| Four-state results: `MATCHED / UNMATCHED / UNREACHABLE / SKIPPED` | P (names; the four-way distinction is spec-fixed) |
| Check names: `citekey`, `doi`, `metadata`, `update-notice`, `quote`, `staleness`, `identifier-discovery`, `web-archive`, `evidence-layer`, `append-only`, `claim-immutability`, `published-drift`, `source-status`, `contested` | P (each; `update-notice` Crossref-shaped) |
| Trust tiers: `unverified → machine-confirmed → human-reviewed` | S (OKF tiers); names P |
| Reason codes: `contradiction, low-confidence, schema-violation, mismatch, not-admitted, outage, stale, drift, contested, superseded-source, missing-archive, fuzzy-quote, no-identifier, retracted, warn-notice, matched, manual` | P (set is spec-fixed; each name renameable) |
| Blocking class / warn class (update-notice types) | A (Crossref taxonomy: `retraction, partial_retraction, removal, withdrawal, expression_of_concern, correction, corrigendum, erratum, reinstatement`) |
| `notice-date` / `detection-date` (bi-temporal) | P (names); bi-temporal semantics anchored (Zep precedent) |
| Inbox entry / acknowledgment (`[id::]`, `[ack::]`, `[target-hash::]`) | P |
| "review inbox", "inbox drain", "standing ack" | P |
| `COMMIT_CLOSING` / `PUBLISH_CLOSING` surfaces; "closing-class", "warn-tier" | P |
| "publish gate", "armed", "8-block bound", "bypass token" | P |
| "doctor" probes: `tree, machine-config, zotero, bbt, autoexport, staleness, remote, backup, inbox` | P (probe names); "doctor" P |

## 6. Commands the user types

| Term | Status |
|---|---|
| CLI verbs: `probe, import-note, staleness, backfill-selectors, verify, inbox, scaffold, doctor` (+ flags `--vault, --offline, --rw-csv, --surface, --with-ci, --base`) | P (each) |
| Skill names (Plan D set): `vault-setup, project, find-papers, import-source, verify-citations, factcheck-draft, publish, evidence-conventions, atlas-conventions` | P (each; `atlas-conventions` inherits the atlas rename; plain-descriptive style is a #11 decision, the specific words are not) |
| Publish dispositions: `mark-published / park / keep-drafting`; typed `discard` | P |
| Plugin name `knowledge-harness` | P |

## 7. Process vocabulary (docs, skill prose, AGENTS.md)

| Term | Status |
|---|---|
| "vault", "evidence layer", "synthesis layer" | "vault" A (Obsidian); layers P |
| "admission" (into Zotero) | P (STORM admission-control semantics) |
| "managed region" / "free region" | S / P |
| "information flow" / "project flow" | P (author's own framing — likely keep) |
| "thin slice", "drill" | P (build vocabulary, pre-user only) |
| "dehydrated" (index-line projections) | A (adopted from OpenAlex) |
| "canonical" | A (adopted) |
| "venue" (OpenAlex `source` entities) | D (resolution term) |

## Naming-pass checklist derived from this inventory

1. The **collision debt**: rename the synthesis-note kind (`topic` page) — mandatory.
2. The **six structural placeholders**: `atlas, efforts, literatures, calendar, +, x` — folder names appear in every path and wikilink; decide once.
3. The **four-state names** and **trust-tier names** — recorded into events/inbox forever after the first vault.
4. **Check names + reason codes** — recorded into inbox history; the set is spec-fixed, the words are not.
5. Skill and CLI verb names — user muscle memory; cheap now, habit-priced later.
6. Everything marked A or D is out of the pass's scope (anchored or already adjudicated).


---

# Anchor candidates per placeholder (naming-pass research substrate)

Added 2026-08-20. For every **P** above: candidate external vocabularies or toolchain surfaces that could anchor (**A**) or semi-anchor (**S**) the term. Candidates only — the pass decides. Corrections found while anchoring are marked ⚠ (terms mislabeled P that already have anchors).

## Corrections to the inventory

- ⚠ **Trust tiers `unverified / machine-confirmed / human-reviewed`** — these ARE OKF's tier names, adopted verbatim in #9. Relabel **S (OKF)**; the pass may keep them at zero cost.
- ⚠ **`verified` (event list name)** — OKF's exact field name. Relabel **S (OKF)**.
- ⚠ **`doctor`** — mass CLI convention (`brew doctor`, `flutter doctor`, `npm doctor`). Relabel **S (CLI toolchain)**.
- ⚠ **`atlas/index.md`** — every llm-wiki implementation surveyed uses `index.md` (Karpathy, hermes, SamurAIGPT, llmwiki). Relabel **S (llm-wiki convention)**.
- ⚠ **`literatures/`, `atlas/`, `calendar/`, `efforts/`, `+`, `x/`** — all six are Ideaverse Lite's own folder vocabulary (observed artifact, research/ideaverse-lite-structure.md), and `literatures/` is additionally ZotLit v2's default folder. Weak semi-anchors exist; alternatives below may anchor harder.

## Folders

| Placeholder | Anchor candidates | Notes |
|---|---|---|
| `+/` | GTD **inbox** (`inbox/`) — mass vocabulary; or keep `+` (Ideaverse; sorts first — a functional argument) | GTD wins on legibility; `+` wins on sort order. |
| `literatures/` | **ZotLit default** (keep — toolchain surface!); or `references/` (CSL: a bibliography IS a reference list; Ahrens "reference notes") | Keeping = zero-cost toolchain alignment if ZotLit is ever adopted as UI (#8 kept that door open). |
| `atlas/` | **llm-wiki `wiki/`** (all 7 surveyed implementations); or evidence-synthesis `synthesis/` (Cochrane — the field is literally named *evidence synthesis*); or keep `atlas` (Ideaverse) | `synthesis/` is the strongest domain anchor for a research harness and pairs with the layer rename below; `wiki/` is the strongest ecosystem anchor. |
| `calendar/` | Obsidian **Daily notes** core plugin (`daily/` — toolchain surface); llm-wiki/OKF `log` (`log/`); keep `calendar` (Ideaverse) | `log/` matches the append-only run-log semantics best; `daily/` matches the Obsidian plugin users see. |
| `efforts/` | PARA/GTD **`projects/`** (mass vocabulary; synergy with the `project` skill); keep `efforts` (Ideaverse) | Spec already calls this the "PARA sliver" — `projects/` names it honestly. |
| `x/` | Keep `x` (Ideaverse); or `system/` / `meta/` (generic, weak) | Only Ideaverse anchors it; low stakes. |
| `+/review-queue.md` | Covidence/Rayyan **screening/review queue** (SR-product vocabulary, S) | Name survives; anchor documents it. |
| `.harness/`, `hk-` prefixes | Follow the **plugin name** — one decision cascades to all three | Decide plugin name first. |

## Note kinds

| Placeholder | Anchor candidates | Notes |
|---|---|---|
| `literature` note | **Ahrens "literature note"** (the PKM mass term) + ZotLit's own docs use it | Effectively S already — relabel. |
| synthesis page (must rename off `topic`) | Evidence-synthesis **`synthesis` note** (Cochrane/PRISMA field vocabulary); llm-wiki **`concept` page** (Karpathy typed-page taxonomy — caveat: OpenAlex's deprecated `concepts` entity, weak collision); Matuschak **`evergreen`** (PKM mass) | `synthesis` doubles as the layer name (spec already says "synthesis layer") — one word anchors folder, layer, and note kind. |
| `effort` note | PARA **`project`** | With the folder. |
| `daily` note | Obsidian **Daily notes** plugin (toolchain surface) | Effectively A — relabel. |

## Claim language

| Placeholder | Anchor candidates | Notes |
|---|---|---|
| "claim" / "claim address" | **Micropublications/nanopub `claim`** (domain model we cite in §5) for the concept; Obsidian **"block link"** (the app's own name for `#^id` links) for the address | "claim link" = both anchors at once. |
| `[confidence-reason::]` | **GRADE** — explanatory footnotes / reasons for (down)grading certainty | Semantics already GRADE-shaped; name could become `[certainty-reason::]` (GRADE says *certainty*). |
| `[retraction-ack::]` | **Wikipedia intentional-citation convention** (`{{retracted|intentional=yes}}`) | Semantics anchored; name fine. |
| `[verify-failed::]` | **Wikipedia `{{failed verification}}`** — the exact mass-deployed template name | Rename to `[failed-verification::]` for a verbatim anchor. |
| `attachment-sha256` | **OAIS/NDSA `fixity`** — THE archival term for exactly this | `fixity-sha256` or `fixity:` anchors it verbatim. |
| `authority` | **Library science "authority"** (authority control/records) + ICD 206 *source descriptor* | Effectively S already; alternative name `source-descriptor` (ICD 206 verbatim). |
| Evidence-boundary tag names | PROV verbatim would be `wasQuotedFrom`-style (rejected — carrier); ICD 203's triple is *information / assumption / judgment* | Current names are plainer than both anchors; likely keep, cite. |

## Statuses and enums

| Placeholder | Anchor candidates | Notes |
|---|---|---|
| Source `status: unreviewed/active/rejected` | **PRISMA/Covidence screening states**: `unscreened / included / excluded` (+ our `superseded`, already adjudicated) | The strongest domain anchor in the whole list — the academic user already thinks in screening states. |
| Effort `status: drafting/parked` | **OKF `draft`**; journal lifecycle (*in preparation / submitted*); `parked` ↔ GTD *someday* / Ideaverse *sleeping* | `published/corrected/withdrawn` already anchored (tags + IFCN/Crossref). |
| `growth: seedling` etc. | **Appleton's garden stages verbatim** (seedling/budding/evergreen) | Already S; adopt her full value set. |

## Verification vocabulary

| Placeholder | Anchor candidates | Notes |
|---|---|---|
| Four-state `MATCHED/UNMATCHED/UNREACHABLE/SKIPPED` | **pytest outcomes** `passed/failed/error/skipped` (toolchain the test suite already speaks; *error* = "check could not run" is exactly UNREACHABLE's semantics); or **GitHub check-run conclusions** `success/failure/neutral/skipped` (CI surface) | pytest mapping is 1:1 and instantly legible; current names are more precise about *comparison* semantics. Genuine trade-off for the pass. |
| Check names | Each check's own domain: `doi` (DOI system), `update-notice` (Crossref), `quote` (WADM exact-match), `staleness` (BBT auto-export issue vocabulary) | Keep, cite per-check. |
| Reason codes | **Covidence exclusion-reason discipline** anchors the *set* (controlled, countable); individual words generic | Low per-word stakes. |
| `notice-date` / `detection-date` | **Bi-temporal database vocabulary** (Snodgrass/SQL:2011): *valid time / transaction time*; Zep's `valid_at/created_at` | `valid-at`/`recorded-at` would anchor verbatim; current names are more self-explaining. |
| closing-class / warn-tier | **Vale severity** `error/warning/suggestion` (prose-CI toolchain from our own gates research) | `error`-class/`warning`-tier reads instantly to any CI user. |
| publish gate / armed / bypass | **GitHub required status checks / branch protection** vocabulary; "gate" is CI-standard | Effectively S; keep. |
| Doctor probe names | Per-probe: `remote` (git), `bbt` (product), `tree` (fs) | Anchored by their subjects. |

## Commands

| Placeholder | Anchor candidates | Notes |
|---|---|---|
| CLI verbs | `scaffold` (Rails/Yeoman convention), `doctor` (brew/flutter), `verify` (git-verify-* family), `probe` (k8s liveness probes!), `inbox` (GTD) | Mostly conventional already; relabel S. |
| `find-papers` | OpenAlex/Semantic Scholar **works search**; PRISMA *identification* phase | `identify-papers` would anchor to PRISMA's own phase name. |
| `factcheck-draft` | **IFCN/ClaimReview "fact-check"** — the field's name | Effectively S. |
| `import-source`, conventions skills | Follow the folder/layer renames | Cascade decisions. |
| Dispositions `park` | GTD *someday*; Ideaverse *sleeping* | Low stakes. |
| Plugin name `knowledge-harness` | None — the one genuinely free name; cascades to `.harness/`, `hk-` markers, skill namespace | Decide first; everything hk-prefixed follows. |

## Process vocabulary

| Placeholder | Anchor candidates | Notes |
|---|---|---|
| evidence layer / synthesis layer | **Evidence synthesis** (Cochrane — the field's own name splits into exactly our two layers) | The single best anchor discovery of this pass: the domain already named our architecture. |
| admission | **STORM source-admission** (cited in spec) | Relabel S. |
| information flow / project flow | Author's coinage | Keep — author-anchored. |
| thin slice | XP **tracer bullet / walking skeleton** | Build-only vocabulary; optional. |

## Suggested decision order for the pass

1. **Plugin name** (cascades: `.harness/`, `hk-` markers, skill namespace).
2. **The evidence/synthesis axis** (one choice names the layer, the folder, and the synthesis-note kind — and discharges the mandatory `topic` rename).
3. Folders (with #2 decided, the remaining five are independent).
4. Four-state names (pytest vs current) and screening statuses (PRISMA mapping).
5. Everything else is S-or-keep at leisure.
