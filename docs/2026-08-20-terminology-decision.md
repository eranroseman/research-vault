# Terminology decision — OpenAlex as base vocabulary

Decision record, 2026-08-20 (supersedes the same-day first version; author's ruling). **OpenAlex's vocabulary (help.openalex.org/data) is the base terminology. We deviate only where a real cost class forces it, and every deviation is documented here.** The vault glossary seed (Plan D) and the pre-slice naming pass cite this document.

## Cost model (unchanged)

**Rename churn is priced at zero** (~10 minutes of implementation time pre-users; occurrence counts are not costs; sunk effort is not an argument). Exactly four real cost classes justify deviating from the base:

1. **Permanent surface mismatch** — with tool surfaces we don't control (Zotero UI, CSL fields, Obsidian, Crossref taxonomy).
2. **Information loss** — the base term carries less structure than the concept needs.
3. **Semantic falsification** — the base term would make our records state something false.
4. **Collision/ambiguity** — the base term already means something else in our context.

No class binding ⇒ the OpenAlex term is adopted. Taste never justifies deviation.

## Adoptions (base applies)

| OpenAlex term | Status |
|---|---|
| `doi`, `pmid`, `author` | Adopted (already aligned; registry/CSL-anchored on both sides). |
| `cited_by_count` and all recorded API facts | Adopted verbatim at the recording boundary, with index + retrieval date. |
| `is_retracted` | Adopted verbatim in checker records (`extra`); see deviations for the internal taxonomy. |
| `dehydrated` | Adopted for our index-line/summary projections of full notes. |
| `canonical` | Adopted as the adjective for the surviving entity in any merge/supersession. |
| `topic` | Adopted for OpenAlex's classification entities. **Consequence for the naming pass:** our synthesis note (placeholder "topic page") must take a non-colliding name — the pass owns the choice. |
| Entity framing: native IDs as curatable judgments; merge semantics (merged-away IDs permanently redirect to canonical) | Adopted as semantics (spec §5 precedents; checkers follow redirects and record the canonical ID verified against). |

## Documented deviations (a cost class forces each)

| Concept | OpenAlex term | Our term | Forcing class |
|---|---|---|---|
| The bibliographic record | `work` | `item` (CSL/Zotero); `literature note` for its vault projection | **1** — Zotero's UI and CSL's fields say `item` forever; adopting `work` buys an eternal translation layer at daily surfaces. |
| The cited document (trust core sense) | their `source` = venue | `source` (primary/cited source; `source-sha256`) | **4** — collision. Resolution: their concept enters our prose as **`venue`** (OpenAlex's own former name for the entity), freeing `source` for the scholarly-English meaning our trust core uses. |
| Publication date | `publication_date` | CSL `issued`/`date-parts` | **1** — CSL is the bibliography format contract (pandoc, BBT, Crossref). |
| Record-lifecycle vs access provenance | `created_date`/`updated_date` | `retrieved`; detection date | **3** — theirs describe *their record's* lifecycle; their names on our fields would misstate what we recorded. |
| Post-publication status | `is_retracted` (boolean) internally | update-notice blocking class (Crossref 12-type, bi-temporal, reinstatement) | **2** — the boolean discards the taxonomy the gates run on. (Boundary recording stays verbatim, above.) |
| Citation relations | `referenced_works`/`related_works` | `supported-by`/`contested-by` | **2** — theirs are untyped work-level edges; ours are stance-typed claim-level, the trust substance. |
| Replacement relation | `merged-away` | `superseded`/`superseded-by` | **3** — scope: OpenAlex merging is identity resolution (two records, one work). Our relation also covers scholarly succession (an old study superseded by a new one — distinct works; calling that a "merge" would be false). The duplicate-work case (preprint↔published) is the overlap where semantics were adopted; if the slice shows the identity-vs-succession distinction needs its own fields, the naming pass may split `merged` out as the OpenAlex-aligned special case. |

## Standing rules

- **OpenAlex is the default source of names.** Any new concept checks OpenAlex first; deviation requires naming its forcing class in this document.
- **One canonical term per concept**; adopted or deviated, never both.
- **Recorded API facts are boundary-verbatim** (source's field names + index + retrieval date).
- **Semantics migrate freely; deviations are about names only** — every deviation above still adopts the base semantics where they fit.
- Interior coinages (`atlas`, `efforts`, `literatures`, `trust tier`, four-state names, `claim address`) remain **temporary placeholders — not decided, not settled**. OpenAlex has no counterparts for these concepts (it does not model vaults, claims, or verification), so the pre-slice **naming pass** owns them, under this document's rule: where OpenAlex (or another anchored vocabulary: CSL, Crossref, W3C) has a term, default to it; free coinage only where none exists. The pass also owes the synthesis-note rename (collision with adopted `topic`). **The naming pass blocks §9 slice execution** — the first real vault mints names into git history under deprecate-never-delete, the moment placeholders become permanent.
