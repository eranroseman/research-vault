# Plan W: Quality Tail — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Steps use `- [ ]`. Split from the pre-slice batch 2026-08-24 (review finding: the batch's header promised a single gating dispatch; this tail is non-gating and runs on main AFTER the batch's Task 21 merge).

**Goal:** The post-merge quality tail: mutmut adoption (author-ruled on the landed pilot), comment hygiene, suite hermeticity + speed, version currency, CI hardening, and the full 26-module mutation baseline.

## Global Constraints

- Runs on main, post-batch-merge. Read this plan from origin/main at each task start.
- Every test Run begins `source .venv/bin/activate`. Suite green at each task's end. Conventional commits, pathspec form (`git commit -- <files>`).
- Task numbering preserved from the batch (23–25 with 24b/c/d) so ledger references stay valid.

______________________________________________________________________

## Part 4: mutmut adoption (author-ruled 2026-08-23 on pilot data — NON-GATING: runs AFTER Task 21's merge; slice Phases 2–6 unblock at Task 21 regardless)

The pilot (report: /home/eranr/kh-mutmut-pilot-report.md; mutmut 3.7.0) measured all three representative modules to completion including events.py — the exit-4 class is structurally absent under mutmut's env-var schemata (collection-time code stays importable; a collection-breaking mutant counts as a kill, verified live). Baseline correspondence sane (all 19 function-level mutate4py survivor locations carried). Cost: two documented tool-defect shims (embedded verbatim in the report): a sitecustomize shim for mutmut's config-load-at-import (false-kill risk otherwise) and a launcher widening pytest 9's re-escaped control-char node ids. Each Part 4 task runs on main after the Task 21 merge, conventional commit per task.

### Task 23: Ruling record + shims land with provenance

**Files:** Modify: `docs/superpowers/specs/2026-08-16-foundation-spec.md` (§10 mutate4py exit-rule entry). Create: `scripts/mutmut_shims/sitecustomize.py`, `scripts/mutmut_shims/run_mutmut.py` (the launcher), `docs/research/2026-08-23-mutmut-defect-reports.md`.

- [ ] **Step 1:** Spec §10 amendment appended to the exit-rule entry: *"CLOSED EARLY by author ruling 2026-08-23 on the landed pilot (its pre-registered method ran; report banked): switch to mutmut 3.7.0. The upstream-responsiveness branch is superseded — the pilot showed complete coverage where the pin had a 23% hole over trust-core modules; the mutate4py upstream reports remain queued for filing as citizenship."*
- [ ] **Step 2:** Copy both shim files VERBATIM from the pilot report into `scripts/mutmut_shims/`, each with a header comment naming the upstream defect it works around and the report as provenance. Draft the two mutmut upstream defect reports (config-at-import; node-id re-escaping) into `docs/research/2026-08-23-mutmut-defect-reports.md` — ready-to-file, the author posts.
- [ ] **Step 3:** Pin `mutmut==3.7.0` in dev extras. Commit `feat: adopt mutmut 3.7.0 — ruling, shims, upstream report drafts`.

Pilot registered 2026-08-25 (plugin-comparison validation, blind spot b): route ONE of this plan's controller rulings through an issue comment instead of the direct dialog channel and record the round-trip time against the blocked implementer — the tickets-as-backbone model assumes tracker-mediated rulings are viable and no event has tested it. One ruling, measured, then revert to dialog.

Measured caveat for this Part (Task 19b round 2, 2026-08-24): a `coverage.py` 100%-branch number can be true and misleading — short-circuit sub-expressions inside a single `return` are outside its branch model (the `pretooluse_guard.py:75` fail-open guard sat invisible under 100%). Mutation results are the check on coverage numbers, not the other way around; treat "100% branch" as "100% of what the model sees." Same family, from Task 20: a correct observation can carry a wrong conclusion — "2 of 9 cases only go red under both guards" was true, "so one guard is redundant" would have shipped an uncaught TypeError; honest self-reports are worth more than silence AND still need checking, and the honesty is what makes the wrong conclusion persuasive.

### Task 24: Gate script speaks mutmut

**Files:** Modify: `scripts/mutation_gate.py`, `tests/test_mutation_gate.py`.

- [ ] **Step 1: Failing tests first** — port the existing gate contract to mutmut's result format: survivor extraction from `mutmut results`/its cache, baseline compare (no-new-survivors), `--update-baseline` writes the full-module baseline, refuse-to-write on any module failure (the Q1 guard survives the port), two-class failure attribution retained, `PYTHONDONTWRITEBYTECODE=1` exported on every invocation (pin the env var in a test — its failure mode is a quietly wrong baseline).
- [ ] **Step 2:** Implement; per-module invocation through `scripts/mutmut_shims/run_mutmut.py`; keep `--out-dir` durability + resume. Full suite. Commit `feat: mutation gate runs mutmut`.

### Task 24b: Comment-hygiene sweep (ruled 2026-08-23 — runs BEFORE Task 25 so the baseline hashes the cleaned tree once; docstrings live in the AST)

**Files:** Modify: `research_vault/*.py`, `scripts/*.py`, `tests/*.py` (comments and docstrings only — zero behavior changes).

- [ ] **Step 1:** Detect mechanically: grep the Python tree for date stamps, ruling language, and plan/task references in comments and docstrings (`2026-`, `ruled`, `Plan [A-Z]\b`, `Task [0-9]`, `previously`, `postmortem`, `superseded`, `renamed from`).
- [ ] **Step 2:** Judge each hit against the house doctrine: a comment states a constraint the code cannot show; provenance, history, and correctness arguments belong to git log. Delete what fails; keep load-bearing constraints (e.g. copyright/license/pinned-commit headers in vendored code stay). Record the judged keep-list in the commit body.
- [ ] **Step 3:** Full offline suite green (comments only — any test failure means the sweep touched behavior; revert that hunk). Commit `style: comment-hygiene sweep — history and rulings out, constraints stay`.

### Task 24c: Suite hermeticity + fixture speed (decided 2026-08-24 — runs BEFORE Task 25: the mutation gate re-executes covering test slices per mutant, so every second cut here multiplies by mutant count)

Headline defect, fixed first: the offline suite is NOT hermetic — 97 connects to localhost:23119 in one offline run (unmarked tests in test_verify_cli.py, test_okf.py, test_publish.py do real BBT CSL exports). Offline green was machine-dependent: Zotero up = live calls; Zotero down = each connect eats the 5 s timeout. Measured baseline: serial 67.4 s / 1532 tests; proof of fixability: with sockets patched out, those files pass 233/233 with zero assertions needing a socket.

**Files:** Modify: `tests/conftest.py`, `pyproject.toml` ([tool.pytest.ini_options]), the fixture sites the steps name; `docs/testing.md` (one doctrine line, same commit as Step 2).

- [ ] **Step 1: `dead_base` fixture** — bind an ephemeral port, close it, hand out `http://127.0.0.1:<port>` (measured: 1 ms refusal vs 5029 ms on port 1 under WSL2). Replace the dead-port test bases; this is the only fix that reaches `test_probe_unreachable`'s subprocess CLI. (−15 s)
- [ ] **Step 2: Socket-block offline runs** — autouse conftest patch (or pytest-socket) raising on any connect, disabled when RV_LIVE/RV_LIVE_NET is set. Sweep the unmarked live-touching tests onto dead_base/fixtures until offline passes fully blocked. Add one line to docs/testing.md: offline runs are socket-blocked; a test needing network carries a live marker. (−9 s, and offline green stops depending on Zotero)
- [ ] **Step 3: Session-scoped template vault** — build one vault per worker, `copytree` per test (measured 0.319 s vs 0.554 s per 30 builds; `.git` copies fine, function-scope copy keeps isolation). (−8 s)
- [ ] **Step 4b (config audit 2026-08-24):** `addopts = ["--strict-markers"]` in pyproject — verified safe (suite uses only live/live_net/parametrize/skip; the xdist ruling forbids `-n` in addopts, not addopts). Without it a typo'd `live_net` mark runs silently and makes REAL external API calls in offline runs.
- [ ] **Step 4:** `tmp_path_retention_policy = "failed"` in pyproject (−3 s; kills the 249 MB retained pile). Then `--dist worksteal` in the workflow's pytest invocations (tail latency only, safe once the 5 s tests are gone).
- [ ] **Step 5: Acceptance** — offline suite green with sockets blocked and ZERO connects to 23119; serial ≤ ~40 s; live suite (both flags) still green. Commit `perf: hermetic offline suite + fixture speed`.

### Task 24d: Version currency (checked 2026-08-24 — runs BEFORE Task 25 so the baseline hashes the post-ruff tree; a later ruff bump would force a re-baseline)

- [ ] **Step 1: ruff 0.15.21 → 0.16.4, by the recorded protocol** (pyproject's own upgrade note): diff `ruff check --isolated --show-settings` against the deliberately-unselected families (BLE/D/TRY/PL — extend-select cannot unselect defaults); move any newly default-enabled skip into `ignore` with its recorded rationale intact. Three places move together: the dep pin, `required-version`, the pre-commit lane. Land trivial autofixes in the same commit; report anything larger.
- [ ] **Step 2 (sharpened by the 2026-08-24 CI audit — shellcheck is the lane's ONE unpinned tool, riding the runner image; when ubuntu-latest migrates to 26.04 it jumps to 0.11.x and the vault pre-commit template starts failing on a change nobody made):** install shellcheck by the shfmt pattern — pinned version + release URL + `sha256sum -c` digest — and delete the ships-in-the-image exception; the "pinned exact, like every other tool" comment becomes true. Also: `pyproject-fmt` 2.28.0 → 2.28.1.
- [ ] **Step 3: Actions v4/v5 → v7** in `.github/workflows/quality.yml` AND both vault CI templates (`research_vault/templates/ci/{verify,rw-batch}.yml`) — the templates render into every user vault, so stale actions ship to users, not just this repo. Template pins update same commit.
- [ ] **Step 4 (CI-audit folds, same files):** (a) `raven-actions/actionlint@v2` is the lane's one floating third-party tag executing arbitrary code — ELIMINATE it via the pinned-binary-download pattern (actionlint ships release assets; digest-checked like shfmt); SHA-pinning is the fallback only if the binary route fights the job. (b) actionlint's invocation gains the two vault CI templates as file arguments — they render into every user vault and have never been lint-checked. (c) `shfmt`'s install gains its digest check (verified: `fb096c5d1ac6beabbdbaa2874d025badb03ee07929f0c9ff67563ce8c75398b1  shfmt_v3.13.1_linux_amd64`) — a tag pin is not a content pin. (d) Add the concurrency group (`${{ github.workflow }}-${{ github.ref }}`, `cancel-in-progress` ONLY for pull_request — cancelling a push-to-main run would abandon a landing). (e) `persist-credentials: false` on checkout (verified: nothing after checkout fetches); fetch-depth comment names the mutation-gate consumer.
- [ ] **Step 4c (pyproject audit folds, 2026-08-24):** (a) version single-sourced: `dynamic = ["version"]` reading `research_vault.__version__` — eliminates the one untested copy; the two remaining are test-pinned. (b) `pytest` pinned exact (lane doctrine: dev tools pin exact; it currently floats across a major); `pypdf>=4` keeps its floor WITH a comment (user-installed feature-detected extra — floors are the design there). (c) mypy gains `python_version = "3.11"` and ruff's floor comment updates two→three movers; mypy `files` grows to cover `scripts/` and `hooks/` (the gate logic and shipped hooks are type-unchecked today) — report rather than land if the new surface yields non-trivial errors. (d) `[project]` gains `license` (SPDX form) + `urls` matching plugin.json — coupled: SPDX string needs `setuptools>=77`, so the build floor bumps in the same commit, with one comment on why the backend floor floats at all.
- [ ] **Step 5:** Suite green; commit `chore: version currency + CI hardening — every tool pinned and digest-checked`.

### Task 25: Full 26-module baseline — the hole closes

- [ ] **Step 1:** Blanket baseline over ALL 26 modules (including the six mutate4py could not measure) under the 8 GB cap; record per-module wall-clock and the one-time stats-build cost in the task report.
- [ ] **Step 1b (CI audit 2026-08-24 — the mutation gate has NEVER actually executed: push runs no-op by construction and this repo has zero PR runs, so every claim in the gate's comment block is reasoned, not observed):** after the port and baseline land, `gh workflow run quality.yml --ref <branch-touching-core>` and OBSERVE a real gate execution end-to-end. Then set `timeout-minutes` from the measured bound — do not invent the number before the first real run measures it.
- [ ] **Step 2:** Commit `mutation-baseline.txt` (now complete — the exclusion list and its gate logic RETIRE in the same commit); update `.github/workflows/quality.yml` to the mutmut path. The spec §10 re-baseline-checkpoint task for "closing the six" is satisfied — note it in the commit body. Task 22's Step 4 stale-manifest allowance dissolves here too (mutate4py sidecars retire wholesale).
- [ ] **Step 3:** Retire the mutate4py pin (drop from dev extras; venv patches die with the venv; the sidecar manifests and any mutate4py-only gate branches removed). The mutate4py upstream reports stay queued for the author. Commit `feat: complete 26-module mutation baseline; mutate4py retired`.
