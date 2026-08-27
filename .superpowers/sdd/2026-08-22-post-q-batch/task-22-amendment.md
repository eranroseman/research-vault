______________________________________________________________________

## Part 3: One sense per term (ruled 2026-08-23)

### Task 22: `skipped_digest` → `skipped_sha256`

**The ruling, as written for the implementer:**

- One sense per term, repo-wide — *digest* reserved for the authored account; the SHA-256 value takes the algorithm's name, matching `fixity-sha256` / `managed-sha256`.
- Stands on its own merits — implement as ruled even if the ADR package is rejected, because the value is a sha256 and the codebase names that everywhere else it matters. No dependency on unapproved work.
- Non-negotiables: no alias, no shim, no back-compat key. Justified in-repo: `docs/terminology.md` §4.3 rules living-surface names rename outright, unlike reason codes and check ids.
- Scope bound: the `factcheck` check id, `budget-cap` reason code, and `SKIPPED` (the four-state result) are governed and untouched.
- Mutation instrument: verified `mutation-baseline.txt` has no key for this function — nothing to edit there. The sidecar manifest does carry `func/skipped_digest` plus `module_hash`/`source_sha256`; regenerate it in the same commit, and if regeneration isn't clean, commit anyway and record the stale sidecar — mutate4py's role is frozen until the post-deepening checkpoint, so no new experiment gets opened over one module.
- Independent of every other task; rides Task 21's acceptance if it lands first, otherwise carries its own.

The rename changes the **name** only. The value is the same SHA-256 hex string, computed the same way over the same input, so review-queue records already carrying it as `target_hash` keep working: no migration, no dedup break, no reopened findings.

**Files:** Modify: `knowledge_harness/factcheck.py` (`skipped_digest`, ~line 165; the `run()` report key, ~line 192); `tests/test_factcheck.py`; `skills/factcheck-draft/SKILL.md`; `knowledge_harness/factcheck.py.manifest.json` (regenerated, not hand-edited).

- [ ] **Step 1: Failing test** — rename every occurrence in `tests/test_factcheck.py`: the section comment (~199), the test name (~202), both call sites (~206–207), the report-key assertion (~227), and the *digest* in the neighbouring test's own name (~213, `test_run_reports_cap_selected_skipped_and_a_digest_only_when_something_skipped`). Run `python -m pytest tests/test_factcheck.py -q` — **Expected: FAIL** (`factcheck` has no attribute `skipped_sha256`; the report carries no `skipped_sha256` key).

- [ ] **Step 2: Implement** — rename the function and the `run()` report key in `knowledge_harness/factcheck.py`, and reword hash-sense *digest* in the docstrings it touches (`skipped_digest`'s "content-derived digest"; `claim_text_hash`'s "SHA-256 hex digest", ~line 41). `hashlib`'s `.hexdigest()` is the standard library's own API — it is not ours to rename, at any call site. Re-run the focused file: PASS.

- [ ] **Step 3: The skill surface** — `skills/factcheck-draft/SKILL.md`: the JSON example key (~28), the prose naming the script's own function (~64), and the `SKIPPED_DIGEST` placeholder in the budget-cap `finding` command (~62). Whole-file test pins update in the same commit as the prose they pin: `grep -rn "skipped_digest\|SKIPPED_DIGEST" tests/` and update every pin it hits.

- [ ] **Step 4: Judged grep** — `grep -rn "digest" --include="*.py" --include="*.md" --include="*.json" .`, and rule each hit by sense:
  - **hash sense, living surface → renames.** Includes `tests/test_finding_cli.py`: the "digest-as-target-hash" docstring (~315) and the `digest-aaaa`/`digest-bbbb` fixture values (~331, ~357).
  - **`hexdigest()` → stays** (standard-library API, see Step 2).
  - **authored-account sense → stays.** The spec's digest-authoring register, the digest lexical-faithfulness lint, and skill prose about a digest as a written account are the sense the ruling reserves.
  - **write-once records stand as written** — `research/`, `analysis/`, completed plans, accepted ADRs, dated audit and finding reports describe the past (AGENTS.md).
  - **the three governed identifiers stay**: the `factcheck` check id, the `budget-cap` reason code, `SKIPPED`.

  Record the judgment list in the commit body.

- [ ] **Step 5: Sidecar manifest, same commit** — regenerate rather than hand-edit:

```sh
source .venv/bin/activate
python -m pytest tests -q --cov=knowledge_harness --cov-branch --cov-report=lcov:lcov.info
python -m mutate4py knowledge_harness/factcheck.py --lcov lcov.info --manifest-file
```

  Confirm `knowledge_harness/factcheck.py.manifest.json` now carries `func/skipped_sha256` and refreshed `module_hash`/`source_sha256`. **One attempt only.** If the run aborts or the manifest does not refresh, commit the stale sidecar anyway and record that plainly in the commit body — no debugging, no second experiment, no new lane: mutate4py's role is frozen until the post-deepening checkpoint. Re-verify rather than assume the baseline claim: `grep -n "skipped_digest" mutation-baseline.txt` — expected: no hits, so nothing to edit there.

- [ ] **Step 6:** Full offline suite green. **One** commit: `refactor: skipped_digest becomes skipped_sha256 (one sense per term)`, with Step 4's judgment list and Step 5's sidecar outcome in the body.
