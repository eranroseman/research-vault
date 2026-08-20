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
