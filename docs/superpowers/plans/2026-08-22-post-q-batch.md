# Post-Q Batch — Task

> **Promoted to the standalone PRE-SLICE plan (2026-08-22)**: the single dispatch between Plan Q's merge and the slice's Phase 2 — instrument freeze for §9. One branch, ordered as numbered — the rename precedes the index so the seven names are written once, correctly. (The polish pass + four-state dedup stay in their own POST-slice plan: they exist to be informed by slice usage.)

1. **Rename `project` → `project-flow`** (ruled 2026-08-22: class-4 collision with CONTEXT.md's *Project* dissolved by using the glossary's other governed noun, *Project flow*): skill directory, terminology §4.3 skills row, routing-table references in `find-sources` and `import-source`, its content test, judged grep for retired references. Entry family now uniformly two-part.
2. **C-7 index**: the seven entry names + one clause each into the vault AGENTS.md template (post-rename names); whole-file test pin updates same commit; `test_skill_contracts.py:153` self-validates the citations.
3. **C-1**: `verify-citations` de-enumerates check ids — canonical obsidian-cli form: "run the CLI; its output is always up to date"; teach the four states, not the fourteen ids.
4. **C-2**: two registry codes out of scope, not one — corrected AND test-pinned; **the enumeration checker** lands here (every check id a SKILL.md enumerates must be one `verify` can emit — the `test_skill_contracts.py:133` instrument generalized).
5. **C-3**: align `find-sources`' credential counts to `redact_url` (3 query-string-auth APIs; 6 redacted params).
6. **C-6**: drop `setup-vault`'s 14-path inventory; keep the six test-pinned paths as an honesty rule, not an inventory.
7. **C-5**: one vendoring-note line — upstream prose describes upstream's corpus.
8. **Migrate step 5**: `import-source` §7–9 → `skills/import-source/references/` + pointer table (find-sources shape); content unchanged, tests unmoved.
9. **Leading word**: the never-hand-write refrain's five spellings collapse to *the CLI writes* (inline token per site).
10. **Prohibition cuts**: "not as a raw dump" (find-sources:88), "not in raw run order" (verify-citations:27) — recipes already present.

11. **Cross-read our-wiring** (docs/2026-08-22-references-cross-read.md): fold the credential-count fix into item 5 ("several", defer to `redact_url`); SKILL.md sources mailto from harness config + states vendored scripts don't read it.
12. **Cross-read annotations**: one vendoring-note section carrying the six upstream-fact annotations per the report's triage; SKILL.md routing guards (no single-DOI lookups via paginate; openalex row points at openalex_abstract.py; OPENALEX_API_KEY env caution).

13. **Ecosystem steals** (audit §6, adopted set): routing guard line in project-flow; compilation-value line in synthesis-conventions; partial-read honesty rule (import-source + factcheck-draft); "validates declarations, not their truth" + the why-one-pass sentence in factcheck-draft; disposition rationalization table in publish (seed rows ported from finishing-a-development-branch per audit §7); publish announces gate-armed at start; setup-vault fails closed on ambiguous vault selection.
14. All §6 deferred items carry their triggers in the audit doc — none land here.

15. **Apply the index to the live vault**: the scaffolded vault at ~/kh-vault predates the template's routing index — after item 2 lands, update the live vault's AGENTS.md to the new template content (one file; the vault repo commit is the author's or this batch's final step with the author's consent).

16. **SKIPPED entries excluded from the unacknowledged count** (slice finding 14): review-queue entries with `result:: SKIPPED` keep being recorded (audit trail) but are excluded from doctor's inbox probe count and every drain surface's "unacknowledged" arithmetic — does-not-apply needs no acknowledgment, and counting it manufactures rubber-stamp pressure. Regression test: a queue holding only SKIPPED entries reports zero unacknowledged; mixed queues count only non-SKIPPED.

17. **Two-tier citekey check** (spec §4 as ruled 2026-08-22): the citekey closing check tightens — a cited citekey must have a literature note (`literatures/<citekey>.md`); bibliography presence alone resolves imports but does not confer citability. Reason code for the new failure class gets its §4.4 row (suggested: `not-imported` — distinct from `not-admitted`). Regression tests: cite-with-note passes; cite-with-bibliography-only fails citekey with `not-imported`; cite-absent-everywhere fails with the existing class. The note's OWN citekey row (note-vs-bibliography identity) keeps current semantics.

18. **Free-region destruction fix** (no-fabrication audit defect 5, pulled forward 2026-08-22 — authored digests will live in exactly this region): `notes.py:151` — an existing note whose managed-close marker cannot be found REFUSES the import (loud fail, reason-coded review record per the uniform-wiring contract) instead of silently replacing the body with `SEED_FREE`. Never-delete (§5) applies to the free region. Regression tests: existing note with exact marker → free region byte-preserved (already pinned); existing note with mangled/absent marker → import refuses, nothing overwritten, record filed; fresh note (no existing file) → seeds normally.

19. **Duplicate-anchor render assert** (claim-anchor audit 2026-08-22, code-side): `notes._assert_managed_body_parses` compares ordered id lists and passes on duplicates, so two identical keyless quotes render duplicate `^id` anchors undetected (ids truncate to 8 hex chars). One-line render-time uniqueness assert; regression test: two identical keyless annotation texts → render refuses.

NOT in this batch: four-state dedup (migrate 3–4 — RED-gated); anything the in-flight references cross-read confirms (triaged separately when it reports); **the remaining trust-core remediation** (audit defects 1–3 — inert RW date parsing, UNMATCHED→MATCHED reduction, vacuous machine-confirmed tier — plus the "unresolved"-placeholder and archive-url fixes, the RW-leg arming question surfaced 2026-08-22 (`--rw-csv` has no default and no shipped local surface passes it — decide the drill/CI arming story alongside the date fix), and the additive Crossref `relation.is-retracted-by` field read in the update-notice leg): its own plan, gating slice Phases 4–6 and the drill (Plan S second sequencing gate, ruled 2026-08-22). Defect 4 (tier-2 citability) is item 17 here; defect 5 is item 18.

Acceptance: suite green offline; `test_skill_contracts` green over the renamed set; judged greps (retired `project` skill references, no returned prohibitions); merge + push in the same motion.
