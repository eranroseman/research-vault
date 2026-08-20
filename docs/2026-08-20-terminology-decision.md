# Terminology decision — OpenAlex vocabulary vs harness vocabulary

Decision record, 2026-08-20. Question: adopt OpenAlex terms (help.openalex.org/data) as standard terminology? **Answer: no wholesale adoption; one borrow; boundary-verbatim rule for recorded API facts.** The vault glossary seed (Plan D) cites this document.

## Cost model

**Rename churn is priced at zero.** Pre-users, with mechanical rename tooling and a test suite, any interior rename is ~10 minutes of implementation time; occurrence counts are not costs, and defending a term by implementation weight is sunk-effort reasoning. Exactly four real cost classes exist:

1. **Permanent surface mismatch** — with tool surfaces we don't control (Zotero UI, CSL fields, Obsidian, Crossref taxonomy): a perpetual translation burden, paid forever.
2. **Information loss** — the foreign term carries less structure than ours.
3. **Semantic falsification** — the foreign term would make our records state something false.
4. **Collision/ambiguity** — same word, different concept; permanent per-reader cost.

A switch with none of these costs is **free**, and the verdict on it is taste — which must be said plainly, not dressed as necessity.

## The comparison

| OpenAlex term | Our term | Same concept? | Verdict | Real cost of switching to theirs |
|---|---|---|---|---|
| `work` | `item` (CSL/Zotero); `literature note` (vault projection) | Mostly | **Ours** | Class 1: Zotero UI and CSL fields say `item` forever — eternal translation at daily surfaces. (Their `work`-as-abstract-entity advantage is covered by our supersession.) |
| `source` (venue: journal/repository) | `source` (the cited document; `source-sha256`, admission) | **No — collision** | **Ours; theirs stays API-side** | Class 4: adopting theirs makes the trust core's own language ambiguous. |
| `topic` (classification taxonomy) | `topic page` (atlas synthesis note) | **No — collision** | **Ours; label theirs `openalex-topic` if recorded** | Class 4. |
| `is_retracted` (boolean) | update-notice blocking class (12-type, bi-temporal) | Ours ⊃ theirs | **Ours; theirs verbatim in checker `extra`** | Class 2: boolean discards taxonomy, dates, reinstatement. |
| `created_date` / `updated_date` | `retrieved`; detection date | **No** | **Ours** | Class 3: theirs describe *their record's* lifecycle; using their names would misstate our access provenance. |
| `publication_date` | CSL `issued`/`date-parts` | Yes | **Ours (CSL)** | Class 1: CSL is the bibliography format contract (pandoc, BBT, Crossref). |
| `referenced_works` / `related_works` | `supported-by` / `contested-by` | **No** | **Ours** | Class 2: theirs are untyped work-level edges; ours are stance-typed claim-level. |
| `cited_by_count` | index-labeled counts | Yes | **Theirs at the boundary** | Free — already the rule: recorded API facts carry the source's field names + retrieval date. |
| `doi`, `pmid` | `doi`, `pmid` | Yes | Tie | Already aligned (registry-anchored). |
| `author` | CSL `author` | Yes | Tie | Already aligned. |
| `merged-away` / canonical | `superseded` / `superseded-by` | Yes | **Ours — by taste only** | **None.** No class applies; a genuinely free switch. Default rests on family coherence with the Wikidata-anchored deprecation vocabulary (§5). Standing offer: call it the other way and it renames in minutes. |
| `dehydrated` (object) | *(no incumbent)* | — | **Borrow** | Free; enters the glossary with source attribution — names our index-line/summary projections. |
| native/vocabulary entities; IDs as curatable judgments | citekey (judgment) / zotero-key (invariant) | Analogous | **Ours** | Nothing to adopt beyond the framing (cited in §5 precedents). |
| institutions, publishers, funders, keywords, locations, abstract_inverted_index | *(no counterpart)* | — | — | Outside the harness's model. |

## Standing rules

- **One canonical term per concept**; foreign vocabularies live at their API boundaries; loanwords enter through the glossary with source attribution.
- **Recorded API facts are boundary-verbatim**: the checker records what it verified under the source's own field names, plus index + retrieval date.
- **Semantics migrate freely; names migrate only when a real cost class favors it.** (OpenAlex's merge/redirect semantics are adopted in §5 under our names — the intended direction of travel.)
- Interior coinages (`atlas`, `efforts`, `literatures`, `trust tier`, four-state names, `claim address`) are **temporary placeholders — not decided, not settled** (author's ruling, 2026-08-20). They exist so implementation could proceed; none carries any commitment. **A deliberate naming pass is REQUIRED before the first real vault exists** — that vault mints these strings into git history under deprecate-never-delete, which is the moment placeholders silently become permanent vocabulary. The naming pass is a pre-slice gate: it blocks §9 slice execution, not Plan D implementation (renames stay ~10 minutes until then).
