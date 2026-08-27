### Task 22: Rename `skipped_digest` → `skipped_sha256` (terminology ruling 2026-08-23)

**RULING (author, 2026-08-23; motivation revised same day) — name the value what it is.** The report field holds a SHA-256 hex string, so it takes the algorithm's own name, in the form `fixity-sha256` and `managed-sha256` already use where the value is durable.

**This is a precision fix, not a collision fix.** It was first ruled to free the word *digest* for the authored per-source account; that account is now named **summary** (the walk above), so nothing collides and nothing downstream waits on this task. It stays in the batch because `skipped_digest` names the shape of the value less honestly than the codebase does everywhere else, and churn is priced at zero (`docs/terminology.md` §1). **If the implementer hits any friction in Step 4, drop the task rather than spend the instrument-freeze window on it** — that is the honest trade now that no collision forces it.

**Non-negotiables:** no alias, no deprecation shim, no back-compat key in the JSON report. `skipped_digest` is a report surface a skill reads, not a persisted vault record — `docs/terminology.md` §4.3 rules that living-surface names rename outright, unlike reason codes and check ids. One verb, one name, one commit.

**Scope bound — rename this and nothing else.** The `factcheck` check id, the `budget-cap` reason code, and the word `skipped` (the four-state result, ADR 0002) are governed vocabulary and stay exactly as they are. This task renames one function, one dict key, and their references.

**Files:** Modify: `knowledge_harness/factcheck.py` (function def + the report dict key); `skills/factcheck-draft/SKILL.md` (the JSON example and the prose sentence naming the field); `tests/test_factcheck.py` (the section marker, the two assertions, the None-case assertion); `knowledge_harness/factcheck.py.manifest.json` (regenerated, see Step 4). Line numbers read at this authoring: `factcheck.py:165,192`; `SKILL.md:28,64`; `tests/test_factcheck.py:199-227` — re-locate by content if drifted. **Also `factcheck.py:39` (`claim_text_hash`'s docstring, "the stable SHA-256 hex digest of one claim's normalized text")** — found 2026-08-23 by the naming sweep, missed by the first site list; the word *digest* there is the hash sense in prose, so it reads "SHA-256 hex value" after this task. `hexdigest()` itself is stdlib and never renames.

- [ ] **Step 1: Tests first.** Rename the assertions in `tests/test_factcheck.py` to the new name and run: FAIL (`AttributeError: module 'knowledge_harness.factcheck' has no attribute 'skipped_sha256'`). This is a rename, so the RED phase is the rename's own proof, not a new behavior test — do not add coverage here.
- [ ] **Step 2: Rename in `factcheck.py`** — the `def`, the call site inside `run()`, the report dict key, and the docstring's own use of the word. Tests: PASS.
- [ ] **Step 3: Skill prose** — update both `skills/factcheck-draft/SKILL.md` sites (the JSON example field and the sentence describing `--target-hash`), then update that file's whole-file test pin in the SAME commit (Global Constraints).
- [ ] **Step 4: Mutation sidecar.** `mutation-baseline.txt` carries NO entry for this function (verified 2026-08-23 — the eight `factcheck` baseline keys name other functions), so **no baseline key needs editing**. The sidecar `knowledge_harness/factcheck.py.manifest.json` does carry `func/skipped_digest` plus a `module_hash`/`source_sha256` over the file, both of which the rename invalidates: regenerate it through the gate script's own path (`scripts/mutation_gate.py` always invokes mutate4py with `--manifest-file`; gate mode already scopes to files changed vs the base ref) and commit the regenerated sidecar. **If regeneration is not clean, commit the rename anyway and record the stale manifest in the commit body** — mutate4py's role is frozen until the post-deepening checkpoint (spec §10), so a stale sidecar for one module is an accepted, recorded cost and never a reason to open a new mutation experiment. **If this task runs AFTER Part 4's Task 25 (mutmut adopted, mutate4py sidecars retired), skip this step entirely — there is no sidecar to regenerate.**
- [ ] **Step 5: Verification.** `grep -rn "skipped_digest" . --exclude-dir=.git` returns nothing outside this plan's own text. Full offline suite green.
- [ ] **Step 6: Commit** `refactor: rename skipped_digest to skipped_sha256 (one sense per term)`.

**Ordering:** independent of every other task in this plan — it touches `factcheck.py` and its own tests, which no other task modifies. Run it anywhere in the batch. If it lands before Task 21, its acceptance rides Task 21's suite and merge; if after, it carries its own suite run and merges on its own.

______________________________________________________________________

## Part 4 — SPLIT OUT (2026-08-24, review finding: the plan outgrew its "single dispatch" header)

The non-gating post-merge tail (mutmut adoption, comment sweep, hermeticity, version currency, CI hardening, full baseline) now lives in its own plan: `docs/superpowers/plans/2026-08-24-plan-w-quality-tail.md`. It runs on main AFTER this plan's Task 21 merge; nothing in it gates the slice.

## NOT in this plan

Four-state dedup (migrate 3–4 — RED-gated) · anything the in-flight references cross-read confirms beyond items 11–12's decided set (triaged separately when it reports) · the skills polish pass + skill-eval lane (POST-slice, informed by usage).

Plan V was absorbed here as Part 2 on 2026-08-22 — the two plans were forced serial by shared `checks.py` test surfaces, and Phase 3's imports run the very checks Part 2 remediates, so one combined merge unblocks slice Phases 2–6 and the drill together. (Its standalone file was removed with the implemented-plans sweep, 2026-08-23; git history holds it.)

## Self-Review (at authoring)

- **Item coverage**: all 19 numbered items of the ruled list map to Tasks 1–13 (items 3+4→T3; 5+7+11+12→T4; 9+10→T7; 13+14→T8; 15→T13); audit defects map 4→T10, 5→T11, 1→T14, 2→T15, 3→T16, fixity pair→T17, archive→T18, 6→T19, relation→T20, spec gaps 86/98/99→T16/T21. Nothing dropped; item 14 is an explicit no-op verification. **Task 22 (added 2026-08-23)** sits outside the original 19-item list — a terminology ruling made after this plan was authored, appended rather than renumbered. **Part 4 (Tasks 23–25, added 2026-08-23)** is the mutmut adoption, author-ruled on the landed pilot; non-gating by placement (post-Task-21), so the slice never waits on it. Commit-note: 3cfb79b's message says "Part 3 — mutmut adoption" but its content is Task 22 (terminology) — a parallel session's uncommitted work swept in under the wrong label; THIS commit carries the actual mutmut Part 4.
- **Placeholder scan**: code tasks (9–12, 14–21) carry failing-test shapes with located scaffolding sources and exact implementation deltas; prose tasks name their content source docs (audit adjudication, cross-read triage) where the decided text is itemized — copy-verbatim instructions, not TBDs.
- **Order dependencies**: T1 (rename) before T2 (index) before T13 (live vault gets the final template). T10's reason-code registration is same-commit with its check (dialect-surface rule). Part 2 runs after Part 1 (shared `checks.py`/inbox test surfaces — T10 and T14–15 touch the same file family). Acceptance consolidates at T21: full suite offline AND live, the audit's reproductions unreproducible, BOTH Plan S sequencing gates marked satisfied.
- **Line numbers** read at 8e98a02/dd4e9f9; re-locate by content if drifted.
