# Post-Q Batch — Task

> The skills-layer audit's accepted fixes + the ruled rename. Rides as Task 0 of the next dispatch after Plan Q merges (standing practice: micro-batches amortize into the next plan unless urgent). One branch, ordered as numbered — the rename precedes the index so the seven names are written once, correctly.

1. **Rename `project` → `project-flow`** (ruled 2026-08-22: class-4 collision with CONTEXT.md's *Project* dissolved by using the glossary's other governed noun, *Project flow*): skill directory, terminology §4.3 skills row, routing-table references in `find-sources` and `import-source`, its content test, judged grep for retired references. Entry family now uniformly two-part.
2. **C-7 index**: the seven entry names + one clause each into the vault AGENTS.md template (post-rename names); whole-file test pin updates same commit; `test_skill_contracts.py:153` self-validates the citations.
3. **C-1**: `verify-citations` de-enumerates check ids ("grouped by check id as the CLI reports them"; teach the four states, not the fourteen ids).
4. **C-2**: two registry codes out of scope, not one — corrected AND test-pinned; **the enumeration checker** lands here (every check id a SKILL.md enumerates must be one `verify` can emit — the `test_skill_contracts.py:133` instrument generalized).
5. **C-3**: align `find-sources`' credential counts to `redact_url` (3 query-string-auth APIs; 6 redacted params).
6. **C-6**: drop `setup-vault`'s 14-path inventory; keep the six test-pinned paths as an honesty rule, not an inventory.
7. **C-5**: one vendoring-note line — upstream prose describes upstream's corpus.
8. **Migrate step 5**: `import-source` §7–9 → `skills/import-source/references/` + pointer table (find-sources shape); content unchanged, tests unmoved.
9. **Leading word**: the never-hand-write refrain's five spellings collapse to *the CLI writes* (inline token per site).
10. **Prohibition cuts**: "not as a raw dump" (find-sources:88), "not in raw run order" (verify-citations:27) — recipes already present.

NOT in this batch: four-state dedup (migrate 3–4 — RED-gated); anything the in-flight references cross-read confirms (triaged separately when it reports).

Acceptance: suite green offline; `test_skill_contracts` green over the renamed set; judged greps (retired `project` skill references, no returned prohibitions); merge + push in the same motion.
