# Task 22 report — `skipped_digest` → `skipped_sha256`

Disposition: historical (2026-09-06)

**Status:** Done. Pure rename, scope held to one function, one dict key, and their direct references (plus the two `test_finding_cli.py` sites the Step 4 judged grep identified as the same hash-sense, living-surface category).

**Commits:** One commit, message `refactor: skipped_digest becomes skipped_sha256 (one sense per term)` (brief's exact wording). The report file rode the same commit.

Files changed: `research_vault/factcheck.py`, `research_vault/factcheck.py.manifest.json` (regenerated), `tests/test_factcheck.py`, `tests/test_finding_cli.py`, `skills/factcheck-draft/SKILL.md`, `.superpowers/sdd/2026-08-22-post-q-batch/task-22-report.md`.
Excluded: `.superpowers/sdd/2026-08-22-post-q-batch/progress.md` (controller-owned, left untouched, not staged).

**Test summary:** RED confirmed (`AttributeError: module 'research_vault.factcheck' has no attribute 'skipped_sha256'`, then `KeyError: 'skipped_sha256'`) before implementation; full offline suite green at **1714 passed / 7 skipped** after — unchanged from baseline, as expected for a pure rename. `ruff check`, `ruff format --check`, `mypy research_vault/`, and the publish-gate hook all pass on the changed files (repo-wide `ruff check`/`format --check` show 5 pre-existing, unrelated findings in `skills/find-sources/scripts/`, confirmed untouched by `git status`).

## Step-by-step record

**Step 1 (RED):** Renamed every occurrence in `tests/test_factcheck.py` first: the section comment (line 199), the test name (`test_skipped_sha256_is_order_independent_and_content_sensitive`, was `test_skipped_digest_...`), both call sites, the neighbouring test's own name (`test_run_reports_cap_selected_skipped_and_a_sha256_only_when_something_skipped`, was `...a_digest_only...`), and the report-key assertion. Ran `./.venv/bin/python -m pytest tests/test_factcheck.py -q`:

```
FAILED tests/test_factcheck.py::test_skipped_sha256_is_order_independent_and_content_sensitive
  AttributeError: module 'research_vault.factcheck' has no attribute 'skipped_sha256'
FAILED tests/test_factcheck.py::test_run_reports_cap_selected_skipped_and_a_sha256_only_when_something_skipped
  KeyError: 'skipped_sha256'
2 failed, 12 passed in 3.47s
```

Exactly the brief's expected failure — the rename's own proof, no new-behaviour test added.

**Step 2 (implement):** Renamed `skipped_digest` → `skipped_sha256` in `research_vault/factcheck.py` (function def, ~line 165, and the `run()` report key, ~line 192). Reworded the hash-sense *digest* in both docstrings it touches: `skipped_sha256`'s "Return a content-derived SHA-256 hex value of one skipped set" (was "a content-derived digest") and `claim_text_hash`'s "the stable SHA-256 hex value" (was "hex digest", line 41 — one line off the brief's ~39, content unchanged). `hashlib.sha256(...).hexdigest()` call sites untouched (stdlib API, per brief). Focused file: 14 passed.

**Step 3 (skill surface):** Updated `skills/factcheck-draft/SKILL.md`: the JSON example key (line 28), the `SKIPPED_DIGEST` placeholder in the budget-cap `finding` command (line 62, now `SKIPPED_SHA256`), and the prose naming the script's own function (line 66, controller-confirmed drift from the brief's cited ~64). Checked for whole-file test pins: `grep -rn "skipped_digest\|SKIPPED_DIGEST" tests/` returned nothing — `tests/test_finding_cli.py`'s `factcheck-draft` token-list pin (lines ~409–428) does not include `skipped_digest`/`SKIPPED_DIGEST` among its pinned tokens, so no pin needed updating (confirmed against the controller's fact 2 before touching anything).

**Step 4 (judged grep):** Ran `grep -rn "digest" --include="*.py" --include="*.md" --include="*.json" .` and classified every hit:

- **Hash sense, living surface → renamed.** `research_vault/factcheck.py` and `tests/test_factcheck.py` sites (Steps 1–2 above), `skills/factcheck-draft/SKILL.md` sites (Step 3), plus `tests/test_finding_cli.py`: the `"The digest-as-target-hash design exists..."` docstring (line 315 → `"The sha256-as-target-hash design exists..."`) and the `digest-aaaa`/`digest-bbbb` fixture values (lines 331, 357 → `sha256-aaaa`/`sha256-bbbb`) — this test documents the same `--target-hash` dedup mechanism `skipped_sha256` feeds, so it's a direct reference of the renamed concept, not incidental prose.
- **`hexdigest()` → stayed** (stdlib API): `research_vault/inbox.py`, `research_vault/verify.py`, `research_vault/notes.py`, `tests/conftest.py`, `tests/test_lints.py`, `tests/test_notes.py`, `tests/test_verify_cli.py` — all untouched.
- **Generic hash-sense prose, not a reference of `skipped_digest` → stayed, on scope grounds.** `research_vault/verify.py:244-245,403,406` ("a validly-shaped digest", "not digest-shaped", "recorded fixity digest") describes the `fixity-sha256`/`managed-sha256` value informally, using "digest" in its standard cryptography sense (as in "message digest") rather than as this repo's contested identifier sense. It is not a reference to the function or key being renamed here, and the brief — precise everywhere else down to exact line numbers — named `test_finding_cli.py` as the sole extra site and stayed silent on `verify.py`, consistent with the controller's scope ruling ("rename one function, one dict key, and their references"). Left in place; routed to Concerns below rather than swept in.
- **Authored-account sense → stayed** (the reserved sense): `docs/superpowers/specs/2026-08-16-foundation-spec.md:157,159-161` (evidence-layer digest, digest lexical-faithfulness lint, digest regression references), `research/validation-slice/2026-08-22-skills-layer-audit.md:427`, `research/validation-slice/2026-08-22-slice-findings.md:42,44`, `research/prior-art/2026-08-24-summary-quality-evaluation-python.md`, `research/prior-art/2026-08-24-zotero-fulltext-indexing.md`, `research/validation-slice/2026-08-22-case-study-question-bank.md`, `research/prior-art/zotero-bridge-design-space.md`.
- **Write-once records stand as written** (AGENTS.md): all of the above research/plan docs are additionally write-once; also `docs/product-landscape/2026-08-22-review-findings.md`, `docs/superpowers/plans/2026-08-22-post-q-batch.md` (this task's own plan text), `docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md`, `docs/superpowers/plans/2026-08-24-plan-w-quality-tail.md` (unrelated "digest-checked" file-integrity sense, future/not-yet-run plan), `research/validation-slice/2026-08-24-concern-disposition-sweep.md:66,71` (a different, deferred concern — the 64-char fixity literal, owned by Task 17), `docs/product-landscape/2026-08-22-adoption-plan.md:549` (quoting a competitor's YAML frontmatter verbatim, a `digests/` directory name that is not this repo's vocabulary at all), `research/harness-audits/raw-component-maps/2-caveman.json:107`, `research/raw/wide-prior-art/research-object-standards.json:53`, `research/prior-art/plugin-packaging-mechanics.md:22` — all describing other systems or the past, none this repo's living code.
- **Governed identifiers, untouched:** `factcheck` check id, `budget-cap` reason code, `SKIPPED` — none renamed, confirmed by grep that none of these strings were altered anywhere in the diff.

**Step 5 (sidecar manifest):** One attempt, clean:

```
./.venv/bin/python -m pytest tests -q --cov=research_vault --cov-branch --cov-report=lcov:lcov.info
  1714 passed, 7 skipped in 87.70s
./.venv/bin/python -m mutate4py research_vault/factcheck.py --lcov lcov.info --manifest-file
  exit 0 — Total mutation sites: 23, Covered: 19, Uncovered: 4, Changed: 0
```

`research_vault/factcheck.py.manifest.json` now carries `"id": "func/skipped_sha256"` / `"name": "skipped_sha256"` (was `func/skipped_digest`), and refreshed `module_hash` (`e9eb8422...` was `1ba61d2a...`) and `source_sha256` (`76fd814a...` was `d932597f...`) plus refreshed per-function hashes for `claim_text_hash`, `skipped_sha256`, and `run` (the three functions whose source text changed). No escape-hatch needed — regeneration was clean on the first attempt. `lcov.info` is gitignored and left untracked, not committed.

Re-verified rather than assumed: `grep -n "skipped_digest" mutation-baseline.txt` → no hits, confirming the brief's claim that no baseline key needs editing.

**Step 6:** Full offline suite green (1714 passed / 7 skipped, unchanged from baseline). Gates: `ruff check` / `ruff format --check` clean on changed files (repo-wide runs surface 5 pre-existing, unrelated findings in `skills/find-sources/scripts/*`, confirmed via `git status --short skills/find-sources/` to have zero pending changes — not introduced by this task). `mypy research_vault/`: "Success: no issues found in 27 source files." `echo '{}' | ./.venv/bin/python hooks/stop_publish_gate.py`: exit 0, no output. `pre-commit run --all-files` was **not** run per the global constraint (shared stash-stack risk across checkouts) — reporting this precondition as unmeetable rather than skipping silently.

Import canary run in-tree before trusting any test result: `./.venv/bin/python -c "import research_vault.factcheck as fc; print(fc.__file__)"` resolved to this worktree's own `research_vault/factcheck.py`, with `hasattr(fc, 'skipped_sha256') == True` and `hasattr(fc, 'skipped_digest') == False` — confirming the suite exercised this worktree's code, not a parent-repo editable install.

## Concerns

- **`research_vault/verify.py:244-245,403,406`** still use "digest" in its generic cryptography sense ("a validly-shaped digest", "digest-shaped") to describe the `fixity-sha256`/`managed-sha256` value. Left unrenamed — out of this task's scope (not a reference to `skipped_digest`, and the brief named no site there). Destination: a terminology-polish pass, if `docs/terminology.md` §4.3's "one sense per term" ruling is later extended to prose describing fixity mechanics generally, not just to named report fields.
- **`.superpowers/sdd/2026-08-22-post-q-batch/progress.md`** is modified in the working tree (controller-owned, pre-existing before this task started). Left untouched and excluded from this commit's pathspec per the global constraint. Destination: whoever owns that ledger (the controller) reconciles it; no action taken here.

______________________________________________________________________

## Controller addendum — a recorded deviation and its cause (2026-08-25)

**This section is the controller's, not the implementer's.** The deviation below
traces to a controller error; the implementer followed its brief exactly.

### The deviation

This commit renames a docstring and two fixture strings in
`tests/test_finding_cli.py` — `"digest-as-target-hash"` → `"sha256-as-target-hash"`,
and the `--target-hash` inputs `digest-aaaa` / `digest-bbbb` →
`sha256-aaaa` / `sha256-bbbb`.

Those are **not** references to the renamed function or dict key. They are
opaque test inputs whose text happened to contain the word. The plan's Task 22
says: *"Scope bound — rename this and nothing else. … This task renames one
function, one dict key, and their references."* By that bound, these three
edits are out of scope.

### Why they were made

The dispatch pointed the implementer at `task-22-brief.md` as generated on
**2026-08-23 18:09**. The plan was last amended **2026-08-25 03:38**. The brief
was two days stale and was never regenerated — the controller confirmed the file
existed and skipped the regeneration step.

The two versions differ materially. The stale brief carries a **judged-grep
step** requiring every occurrence of *digest* to be ruled by sense, and names
these exact `tests/test_finding_cli.py` sites as in-scope renames. The current
plan drops that step and adds the narrower bound quoted above.

So the implementer did precisely what its brief required. The scope excess is
the controller's, from dispatching against an artifact it had not refreshed.

### Disposition: accepted (orchestrator ruling, 2026-08-25)

Accepted rather than reverted, for reasons that belong in the record rather than
resting on authority:

- the changed strings are the exact class the earlier plan version deliberately
  required — fixtures documenting the very `--target-hash` dedup mechanism
  `skipped_sha256` feeds;
- the current bound's purpose is **scope containment during the instrument
  freeze**, and these edits are semantically inert: the values are arbitrary
  opaque inputs and the suite is unchanged at 1714 passed / 7 skipped;
- a revert round would churn more tree than the deviation does, while
  re-introducing stale naming — **the bound protects against creep, not against
  coherence.**

The author may override with a ride-along revert in a later task if they read
"and nothing else" more strictly than the orchestrator did.

### The process fix

Regenerate every task brief immediately before dispatch; never reuse one found
on disk. The prior rule — "generate the brief and confirm existence before
writing the dispatch", adopted at Task 15 — guarded against a **missing** brief
and not against a **stale** one. **Existence is not currency.** This session's
other briefs (2e, 11, 12) were all freshly generated; Task 22 was the only reuse.
