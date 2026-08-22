# Plan Q: Dev-Quality Lane (mutation baseline + advisory gates) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the dev-quality lane for the harness's own code: an extended ruff regression-rule set, a one-time mutate4py blanket baseline with committed sidecar manifests, a "no new survivors" differential gate, a crap4py CRAP-score ceiling, and a drywall duplicate gate — wired into one advisory GitHub Actions workflow.

**Architecture:** Three tool adoptions (live-reviewed 2026-08-20, see `research/code-quality-tools-gabadi.md`) land as pinned dev dependencies; a small gate script turns mutate4py's exit-0-even-with-survivors output into a baseline-compared pass/fail; the blanket run commits per-module sidecar manifests so differential reruns persist across clones with zero CI state. Everything measures **harness code quality only** — nothing here touches the vault's publish-gate closing sets.

**Tech Stack:** Python ≥3.11 for the lane (repo core stays ≥3.10; the lane's CI job runs 3.12), pytest + pytest-cov (LCOV branch coverage), mutate4py 0.1.4, crap4py 0.1.1, drywall 0.1.3, GitHub Actions.

## Global Constraints

- **Sequencing gate: execute only after Plan T (terminology wave) is merged to main.** The wave renames identifiers; `ast.unparse()` manifest hashes change wholesale, and a pre-wave baseline is dead weight. **Parallelizable with Plan D** (author ruling 2026-08-20) — D is skills/markdown; any core-Python overlap costs one differential top-up after both merge.
- Worktree via `superpowers:using-git-worktrees`, branch `build/quality-lane`.
- **As-built HEAD governs**: the module list, folder names, and skill names in this plan reflect pre-wave state; use the post-wave names at HEAD wherever they differ, and record adaptations in the commit message.
- Every test Run begins `python3 -m venv .venv 2>/dev/null; source .venv/bin/activate && pip install -e ".[dev]" -q` (idempotent; PEP 668).
- Tool versions are **pinned exact** (single-maintainer v0.1.x tools — treat as removable; upgrades are deliberate acts).
- mutate4py always runs with `--manifest-file` (sidecar JSON). The embedded-in-source mode appends a footer to production files — never acceptable in this repo.
- The lane is **advisory**: the workflow fails visibly but is not a required check (no branch protection exists; do not add any).
- Live-measured costs to expect (2026-08-20, 4 workers): ~1,250 mutation sites repo-wide; blanket with test-contexts narrowing ~10–15 min; contexts DB build (one isolated coverage session per collected test, 452 tests) ~10–15 min, one-time; full suite 37 s. **Re-measured 2026-08-22 at Task 4 dispatch (suite grew to 1454 tests, serial 78 s): contexts build ~35–50 min; no-contexts fallback ~7 h — see Step 5's amended stop-and-report fallback.** **Amended again same day (Task 4 execution finding): `--max-workers > 0` provisions worker copies via `uv venv` + `uv sync`, which fails on the pre-existing `requires-python = ">=3.10"` vs mutate4py's `>=3.11` floor. Ruled: raise `requires-python` to `">=3.11"` in the same task (one line; the 3.10 claim was untested — dev venv is 3.12.3, no CI matrix exists — an unexercised support claim, not a contract). Then run with workers as planned. Note: ruff infers its target from `requires-python`, so expect possible new UP-rule suggestions after the bump — land trivial ones in the same commit, report anything larger. Serial mode is NOT the fix: serial no-contexts extrapolates to ~28 h, and even serial-with-contexts multiplies every Step 5/6 estimate by the worker count.**
- **Pre-baseline over-engineering pass (author-triaged, outside this plan's tasks):** after Plan T merges and before Task 3's blanket baseline, the author's session runs `/ponytail-audit` (whole-repo over-engineering sweep — delete/stdlib/native/yagni/shrink, ranked report, applies nothing); author-accepted cuts land as one simplification batch **first**, so the mutation manifests hash the simplified tree (same AST-ordering reason ruff fixes precede the baseline). It is LLM judgment — a report for triage, never a CI gate; deterministic-only closure holds.
- Commit messages conventional; one commit per task.

## File Structure

- Modify: `pyproject.toml` (dev extras + ruff rule extension), `.gitignore`, `knowledge_harness/__main__.py` + `tests/*` (lint fixes)
- Create: `scripts/mutation_gate.py` (gate + baseline updater), `tests/test_mutation_gate.py`, `mutation-baseline.txt` (committed survivor baseline), `knowledge_harness/*.py.manifest.json` (one sidecar per module, committed), `.github/workflows/quality.yml`

______________________________________________________________________

### Task 0: Post-D batch (folded 2026-08-22 — the standalone doc's fixed overhead exceeded its size; this task satisfies Task 4's churn gate by construction)

Suite green offline AND live at the end of this task (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>`; Zotero running).

#### F-4 RULING (2026-08-22): the information flow enters at admission, not at search

Spec §7's two-flow accounting is explicit: the information flow (find → human admits via Zotero → catalog → integrate) is continuous and project-independent. The shipped surface inverted that by gating entry on a project. Ruled:

- **`import-source` and everything downstream of admission runs standalone** — catalog, index, log, integrate-at-import need no project. A human may admit a source found by any means (a colleague's email, a footnote chase); the harness catalogs it regardless.
- **`find-sources` alone stays project-scoped** — its deliverable is the PRISMA-S trail, which is per-review by definition (the existing ruling stands unchanged).
- Fix whatever check enforces the project gate on the import path; regression test: `import-source` on a fresh vault with zero projects completes catalog/index/log.

## Fixes (from the shipped-state review)

1. **F-5**: `import-source` prose never says where to read the citekey after admission — one sentence (BBT column / citation key in Zotero's UI). First real import hits this.
2. **F-3**: same-day correction impossible — pass `--date` through to the disposition verbs; NEVER a tag suffix (breaks `PUBLISHED_TAG` parsing and F-2's newest-tag ordering; shape recorded by the executor, adopted).
3. `trust-tier` exits 1 where sibling verbs exit 2 — align to the exit-code contract.
4. Empty-directory disagreement between `_require_clean_project` and `_project_differs` — one definition of "clean", tested.
5. `search-log` silently discards cross-kind flags — reject loudly.

## Duplication + prose (audit accepted wholesale — house comment doctrine: postmortems are the author talking to the reviewer, noise once merged; git log holds them)

6. `_validate_optional_text` copied `searchlog.py` ← `inbox.py` → move into `appendlog.py` (the module that exists to stop this drift), import in both.
7. Docstring/comment shrinks as itemized in the audit: `appendlog.py` (module docstring 19→3, condition comment 8→1, fsync 8→1), `searchlog.py` (48→8, `_prepare_append` postmortem → one line), `factcheck.py` (42→~12 keeping copyright/license/pinned-commit — those are load-bearing; `_bucket` 10→0, its sibling docstring covers it), `__main__.py` (`record_finding` 30→~5 keeping the id-collision rationale), `lints.py` (9→2), `webapi.py` bool-docstring kept at 3 lines with the three pasted copies (archive ×2, verify ×1) deleted.
8. Code: `searchlog.py` regex-then-isoformat → isoformat round-trip alone (the round-trip already rejects everything the regex does; drop `re`); `factcheck.ClaimRef.to_dict` → `dataclasses.asdict` at call sites; `lints.py` append-only path test → one expression; the four `cmd_mark_*` → one `{verb: publish.fn}` dict + `cmd_disposition`; frozenset-of-one → inline `check != "factcheck"`.

## Deferred with homes (do NOT implement here)

- Architecture-pass inputs (append to the deepening pass's evidence list, not this batch): `paths.project_dir` extraction; `finding_id` collision guard in `verify._file_effects`; the third `_git` copy; `publish.py`'s private verify imports; `searchlog`'s unused parser + unwired `durable=`.
- Vendored fork (3,478 lines): "re-vendor, never hand-edit" policy makes pruning a policy change, not a cut — flagged as the largest lever if that policy ever reopens; excluded from this batch.
- Plan D checkboxes stay unticked: the merged history is the completion record (AGENTS.md history rule, executor's reading confirmed).
- The two `HARNESS_LIVE_AUTOEXPORT_VAULT` skips stay honest ("not run", never "passed") until the slice's human BBT step exists.

Acceptance: suite green offline and live; F-4's standalone-import regression test present; judged grep confirms no postmortem prose returned; one merge, pushed in the same motion.

______________________________________________________________________

### Task 1: Pinned dev dependencies and hygiene

**Files:**

- Modify: `pyproject.toml`, `.gitignore`

**Interfaces:**

- Produces: installable `dev` extra containing `pytest-cov==7.1.0`, `mutate4py==0.1.4`, `crap4py==0.1.1`, `drywall==0.1.3`, `mypy==2.3.1` (later tasks and CI install exactly this).

- [ ] **Step 1: Extend the dev extra** in `pyproject.toml`:

```toml
dev = [
    "pytest>=8",
    "ruff==0.15.21",
    "pytest-cov==7.1.0",
    "mutate4py==0.1.4",
    "crap4py==0.1.1",
    "drywall==0.1.3",
    "mypy==2.3.1",
    "pyzotero[cli]==1.14.0",  # dev-lane agent instrument (adopted 2026-08-22 by contract match:
                              # canonical library, local-API-first, read-only by default, local
                              # writes gated behind Zotero's own consent dialog — admission stays
                              # human by construction; live-verified local read at adoption).
                              # Web API permitted for tests: read-only key by default; a
                              # write-capable key only for a test that needs it, never against
                              # the real library. No key is stored in this repo.
    "mdformat==1.0.0",
    "mdformat-gfm==1.0.0",
    "mdformat-frontmatter==2.1.2",
    "yamlfix==1.19.1",
    "pyproject-fmt==2.28.0",
    "pre-commit==4.6.2",
]
```

- [ ] **Step 2: Extend `.gitignore`** (repo root) with the lane's transient artifacts:

```
.mutate4py/
lcov.info
.coverage.*
.contexts.db
```

- [ ] **Step 3: Install and verify**

Run: `source .venv/bin/activate && pip install -e ".[dev]" -q && mutate4py --help >/dev/null && crap4py --help >/dev/null && drywall --help >/dev/null && mypy --version >/dev/null && python -c "import pytest_cov" && echo OK`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add pyproject.toml .gitignore
git commit -m "build: pin dev-quality lane tools (pytest-cov, mutate4py, crap4py, drywall, mypy)"
```

______________________________________________________________________

### Task 2: Ruff + mypy regression rules, mdformat, config validity

**Files:**

- Modify: `pyproject.toml` (`[tool.ruff.lint]` + `[tool.mypy]`), `knowledge_harness/` (lint + type fixes), test files (PLW1510, S108 classification)

**Interfaces:**

- Consumes: Task 1's installed dev extra.
- Produces: `ruff check knowledge_harness tests scripts` and `mypy knowledge_harness` both clean — Task 5's CI runs exactly these (the `scripts/` package exists from Task 4 onward; until then the path is simply absent and ruff skips it).

**Pre-measured violations at 2026-08-20 HEAD** (pre-Plan-C/T; as-built HEAD governs — C/T code may add hits, fix those in the same sweep): DTZ×4 (`datetime.date.today()` in `__main__.py`), PTH115×1 (`os.readlink`, `__main__.py:367`), RUF×6 (5 core + 1 tests), PLW1510×2 (tests call `subprocess.run` without explicit `check`), S108×2 (`"/tmp/escape"` in `tests/test_cli_live.py:322` and `tests/test_notes.py:23` — classify: if these are deliberate absolute-path-escape fixtures, per-line `noqa: S108` with that reason; otherwise `tmp_path`), S314×1 (`checks.py:683` — **resolved by admission, not noqa** (spec §8 dependency discipline; docs/2026-08-20-zero-dep-rethink.md): add `defusedxml==0.7.1` to `[project] dependencies` as core's first pinned runtime dependency — parsing externally-influenced XML is commodity-hard — lazy-imported inside the parsing function so gate-path startup is unchanged; replace the `ElementTree` parse with the `defusedxml.ElementTree` equivalent). Also PERF×3 (loop/comprehension rewrites as reported). Zero-hit adoptions (pure regression guards): ARG, FURB, ISC, PGH, the rest of the S family, the future-guard block ASYNC/EXE/FA/FLY/G/INT/LOG/N/PYI/RET/TC/YTT (structurally n/a today — no async, no logging, no stubs; the guard is already armed the day such code appears), and T20 outside `__main__.py`/`scripts/` (all 18 measured prints live in `__main__.py` — library modules get the stray-debug-print guard; a rogue print in `checks.py` would corrupt the CLI stdout contract).

**mypy, pre-measured (rung-1 config below, mypy 2.3.1): 13 genuine errors in 8 files** — the default-mode 10 plus 3 surfaced by `check_untyped_defs` — `frontmatter.py:137` var-annotated + `:141` assignment (`current_list` needs `list[...] | None` typing), `inbox.py:368` var-annotated `entries`, `zotero.py:182` return-value (`object` vs `dict` — narrow with `isinstance`), `checks.py:66` assignment (`str` into a `Path` variable — split the variable), `lints.py:187`/`:440` var-annotated, `lints.py:457` arg-type (`str | None` into `Outcome` — guard before the call), `identify.py:110` var-annotated `identifiers`, plus one index-category error and the rung-1 three, all as mypy reports them (rung-1 breakdown: var-annotated×7, assignment×2, return-value/index/arg-type×1 each; the pypdf import is handled by the override). `--strict` is 329 (316 annotation-presence) — a campaign yielding ~0 additional verified defects, deliberately NOT this task (author-ruled 2026-08-20); the ratchet path is recorded in the config comment.

**Ruling encoded (author-approved 2026-08-20): machine-generated timestamps and dates derive from an explicit timezone-aware UTC clock.** Verified events, `accessed` dates, and update-notice detection dates are bi-temporal records that live forever in git; a naive local clock is a defect class, not a style choice. DTZ enforces this from now on.

- [ ] **Step 1: Extend the ruff config** in `pyproject.toml` — replace the existing `extend-select` list and add the per-file ignore:

```toml
[tool.ruff.lint]
extend-select = [
    "A",
    "ARG",
    "ASYNC",
    "B",
    "C4",
    "C90",
    "DTZ",
    "EXE",
    "FA",
    "FLY",
    "FURB",
    "G",
    "I",
    "INT",
    "ISC",
    "LOG",
    "N",
    "PERF",
    "PGH",
    "PIE",
    "PLE",
    "PLW",
    "PT",
    "PTH",
    "PYI",
    "RET",
    "RUF",
    "S",
    "SIM",
    "T10",
    "T20",
    "TC",
    "UP",
    "W",
    "YTT",
]
ignore = [
    # Bandit idiom exclusions (recorded 2026-08-20): these fire on this repo's
    # own architecture, not on findings. Subprocess hygiene is still enforced
    # by S602/S604 (shell=True) which remain active inside "S".
    "S310",  # urlopen IS the four-state network layer, https-only
    "S603",  # fires on every list-form subprocess call (git plumbing is the design)
    "S607",  # "git" by name, resolved via PATH, is the intended invocation
]
# Deliberately NOT selected (recorded 2026-08-20 — do not "fix"):
#   PLR   — pylint-refactor thresholds: PLR0911's "too many returns" flags four-state
#           outcome mappers (multi-return IS the doctrine's shape); PLR2004 flags HTTP
#           codes; complexity rows are covered by C90 + the CRAP ceiling
# C90 IS selected (2026-08-20 reversal of the earlier skip): CRAP >= CC always, so the
# CRAP ceiling subsumes any CC cap at or above it — but BELOW the ceiling a CC cap
# catches complexity laundered by high coverage (coverage measures execution, not
# verification; mutation survivors live in covered lines). Backstop, not the risk gate.
#   BLE   — the four-state doctrine requires broad catch -> UNREACHABLE in probe
#           wrappers and fail-open hooks; this rule fights the architecture
#   ANN   — mypy owns typing: it checks annotations are TRUE, ANN only that they exist
#   D     — docstrings unenforced by decision: presence/format checks can't verify truth,
#           and the meaning layer lives in CONTEXT.md/spec; docstrings stay by convention
# Upgrade protocol (ruff pinned; upgrades are deliberate acts): newer ruff versions
# default-enable curated singles from BLE/D/TRY/PL — the skip list above — and
# extend-select cannot unselect defaults. On any ruff upgrade: diff the new version's
# defaults (ruff check --isolated --show-settings) against these skips and move any
# violated skip into `ignore`, or the recorded rulings silently stop being true.

[tool.ruff.lint.mccabe]
max-complexity = 32  # green at adoption (worst: _target_hash CC 31); Task 3 tightens to 28 [gate value is 30 everywhere; any residual '45' in this doc is stale authoring prose]
                     # after the split. No pre-committed final target: the resting cap gets
                     # set from the post-deepening CC distribution (four-state outcome
                     # mappers legitimately run CC 17-22 — the doctrine is branchy; a
                     # convention number like 15 could force fragmenting cohesive mappers)

[tool.ruff.lint.per-file-ignores]
"tests/test_cli_live.py" = ["UP012"]
"tests/*" = ["RUF001", "RUF002", "RUF003", "S101"]  # unicode fixtures deliberate; assert IS pytest
"knowledge_harness/__main__.py" = ["T20"]  # print IS the CLI output contract (all 18 measured uses)
"scripts/*" = ["T20"]  # gate scripts report via stdout by design

[tool.mypy]
files = ["knowledge_harness"]
check_untyped_defs = true  # rung 1: untyped function bodies are checked (+3 real errors at adoption)
strict_equality = true     # truth flags — measured zero-cost at adoption
warn_unused_ignores = true
warn_redundant_casts = true
# Ratchet path (as touched code gets annotated): disallow_incomplete_defs ->
# disallow_untyped_defs. Full --strict deferred by decision (measured 2026-08-20:
# 316 of its 329 errors are annotation-presence, yielding ~0 additional verified
# defects; at JSON boundaries strict invites cast()-laundered "asserted, not
# verified" types). Revisit after the evidence shapes (CSL-JSON item, Zotero
# responses, frontmatter) are modeled as TypedDicts — then the remaining rungs
# are cheap and strict arrives as a fact, not a campaign.

[[tool.mypy.overrides]]
module = "pypdf.*"
ignore_missing_imports = true  # optional [pdf] extra; dev lane installs [dev] only
```

(RUF100 disappears because full `RUF` contains it; S101 in production code stays active — 3 core hits become explicit exceptions or fixes.)

- [ ] **Step 1b: Post-flip naming residue (parked from Plan L)** — rename the `CORE` constant/name to `ROOT` at its five sites (both hooks, `test_precommit`, `test_verify_cli`, this plan's `mutation_gate` sketch): the name describes a directory that no longer exists.

- [ ] **Step 2: Run to see the expected failures**

Run: `source .venv/bin/activate && ruff check knowledge_harness tests --no-cache; mypy knowledge_harness`
Expected: the pre-measured violations above (counts may differ at HEAD; every hit gets classified fix-vs-noqa-with-reason, nothing blanket-ignored).

- [ ] **Step 3: Fix**

Autofix first: `ruff check knowledge_harness tests --fix`. Then by hand:

- DTZ: every `datetime.date.today()` becomes the UTC clock, e.g. `__main__.py:219`:

```python
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
```

- PTH115: `os.readlink(...)` becomes `Path(...).readlink()`.

- PLW1510: add explicit `check=True` (or `check=False` with a reason) to the two test `subprocess.run` calls.

- RUF012/RUF013-class hits: annotate mutable class attributes / make `Optional` explicit as reported.

- S108: classify per the pre-measured note (noqa-with-reason if a deliberate escape fixture, else `tmp_path`).

- S314: the defusedxml admission per the pre-measured note — dependency added, lazy import at the parse site, no noqa. Verify gate-path startup unaffected: `python -c "import time,subprocess,sys; t=time.perf_counter(); subprocess.run([sys.executable,'-m','knowledge_harness','--help'],capture_output=True); print(time.perf_counter()-t)"` before and after — the delta must be noise.

- S101 in core (3 hits): replace production `assert` with explicit raises, or noqa-with-reason where it guards an internal invariant.

- PERF (3 hits): apply the reported rewrites.

- mypy's 13: annotate the seven `var-annotated` sites, narrow `zotero.py:182` with `isinstance`, split the `checks.py:66` variable, guard `lints.py:457`'s `None`, and fix the remaining index error as reported.

- [ ] **Step 3b: Markdown canonical form (mdformat)** — author-ruled 2026-08-21 after two rounds of push-back; the drift-protection argument governs: multi-agent authorship makes style drift the default, and a pinned formatter is the standing protection.

**Format policy (author-ruled 2026-08-21 across four push-backs; the governing principle: uniformity everywhere, zero remembered rules, each surface canonicalized by the right owner):**

- **mdformat owns all CommonMark repo markdown**: `README.md`, all of `docs/` (history surfaces included — verified: `--wrap keep` preserves content, fences byte-safe, no prose reflow; **the history rule's reading is amended: content and meaning are never rewritten; form was canonicalized once**, commit carried in `.git-blame-ignore-revs`), and `skills/`. `tests/` needs no exclusion — it contains zero `.md` files (verified; inline string fixtures are invisible to mdformat by construction).
- **The sole writer IS the formatter for vault-dialect surfaces** (`knowledge_harness/templates/vault/**` and everything the harness emits): measured 2026-08-21, mdformat escapes the dialect — wikilinks `[[x]]` → `\[[x]\]`, inline fields `[supports:: …]` escaped, `%%/hk-managed%%` indented — and `mdformat-obsidian` 0.3.2 does the same, so no off-the-shelf formatter speaks Obsidian dialect. Canonical form there is the render/scaffold contract's output, per the author's principle ("having the sole writer use the formatter eliminates the problem"): managed regions canonicalize by full re-render (witnessed by `managed-sha256`), ledgers by the entry grammar + append-only discipline. This is a dialect boundary in tool config (invocation path list), not a remembered rule.

Run: `mdformat --wrap keep README.md docs skills` (adjust to HEAD's tree; templates deliberately absent — dialect surface). Record the churn commit hash in a new `.git-blame-ignore-revs` file and note `git config blame.ignoreRevsFile .git-blame-ignore-revs` in README's dev section. After the churn: `grep -rn '\\\[\[' docs skills README.md` must return nothing (no wikilink escaping happened — the CommonMark set was truly dialect-free).

- [ ] **Step 3b-1: Canonical form for the remaining file types** (author-ruled 2026-08-21 — "that's for md files"; the one-form-owner matrix completes over every type in the repo, all candidates comment-preservation-tested live):

| Type                               | Owner                                                                                                                                                                 | Enforcement                                                                       |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Python                             | ruff format (pinned)                                                                                                                                                  | CI check (existing)                                                               |
| Markdown, CommonMark               | mdformat (pinned)                                                                                                                                                     | CI `--check`                                                                      |
| Markdown, vault dialect + `.base`  | the sole writer (render/scaffold)                                                                                                                                     | canonicality property tests                                                       |
| YAML (workflows, `templates/ci/`)  | yamlfix (pinned; verified: only doc-start normalization, comments preserved)                                                                                          | CI `yamlfix --check`                                                              |
| TOML (`pyproject.toml`)            | pyproject-fmt (pinned; verified: tool-section comments preserved, zero spurious churn; taplo rejected — collapses arrays, general tool where a targeted one suffices) | CI `pyproject-fmt --check`                                                        |
| JSON (manifests, `hooks.json`)     | stdlib `json.tool` canonical form                                                                                                                                     | asserted inside `test_config_validity.py` — formatter and check in one, zero deps |
| Shell (`templates/git/pre-commit`) | shfmt (CI action, pinned)                                                                                                                                             | CI diff mode                                                                      |

Apply the one-time churn: `yamlfix .github/workflows knowledge_harness/templates/ci && pyproject-fmt pyproject.toml && python -m json.tool --indent 2` over each JSON manifest (rewrite in place), then commit; the churn commit joins `.git-blame-ignore-revs`. `system/bibliography.json` is vault-side and BBT-owned — outside every repo formatter's jurisdiction by construction (staleness lint enforces).

- [ ] **Step 3b-1b: The orchestration seam** (rethink audit 2026-08-21, `docs/2026-08-21-lint-format-rethink.md` — closes R7 "one command locally == CI"). Create `.pre-commit-config.yaml` at repo root:

```yaml
# Dev-lane orchestration seam (docs/2026-08-21-lint-format-rethink.md): the ONE
# command for every form/lint check, locally and in CI:
#     source .venv/bin/activate && pre-commit run --all-files
# All hooks are repo-local system hooks over the pinned venv — no remote hook
# repos, no env building, no network at check time. The one-form-owner matrix
# lives here as config; quality metrics (CRAP/drywall/mutation) are a different
# axis and run as separate workflow steps.
# NAME COLLISION, deliberate: this is the repo's DEV-LANE pre-commit (style and
# correctness). The vault's pre-commit (knowledge_harness/templates/git/pre-commit)
# is a TRUST GATE owned by the harness — a different system; do not conflate.
repos:
  - repo: local
    hooks:
      - id: ruff-format
        name: "form: python (ruff format)"
        language: system
        entry: bash -c 'ruff format knowledge_harness tests scripts'
        pass_filenames: false
        always_run: true
      - id: ruff-check
        name: "lint: python (ruff)"
        language: system
        entry: bash -c 'ruff check knowledge_harness tests scripts'
        pass_filenames: false
        always_run: true
      - id: mypy
        name: "types: python (mypy rung-1)"
        language: system
        entry: bash -c 'mypy knowledge_harness'
        pass_filenames: false
        always_run: true
      - id: mdformat
        name: "form: markdown CommonMark (mdformat)"
        language: system
        entry: bash -c 'mdformat --wrap keep README.md docs skills'
        pass_filenames: false
        always_run: true
      - id: yamlfix
        name: "form: yaml (yamlfix)"
        language: system
        entry: bash -c 'yamlfix .github/workflows knowledge_harness/templates/ci'
        pass_filenames: false
        always_run: true
      - id: pyproject-fmt
        name: "form: toml (pyproject-fmt)"
        language: system
        entry: bash -c 'pyproject-fmt pyproject.toml'
        pass_filenames: false
        always_run: true
      - id: config-validity
        name: "lint: json canonical + skill frontmatter (suite)"
        language: system
        entry: bash -c 'python -m pytest tests/test_config_validity.py -q'
        pass_filenames: false
        always_run: true
      # Manual stage: binary tools R5 declines to require locally (ruff-repo
      # precedent for stage-tiering). CI runs them; local runs are optional.
      - id: shellcheck
        name: "lint: shell (shellcheck)"
        language: system
        entry: shellcheck knowledge_harness/templates/git/pre-commit
        pass_filenames: false
        always_run: true
        stages: [manual]
      - id: shfmt
        name: "form: shell (shfmt, diff mode)"
        language: system
        entry: shfmt -d knowledge_harness/templates/git/pre-commit
        pass_filenames: false
        always_run: true
        stages: [manual]
```

(Formatter hooks run in write mode; pre-commit's contract fails a hook whose files changed, so the same command is check-mode in CI with `--show-diff-on-failure`. If a hook needs adjustment against pre-commit 4.6.2's actual behavior at execution, adapt and record — the seam's contract is only: one command, all owners, no network.)

- [ ] **Step 3b-1c: IDE alignment — PRE-LANDED 2026-08-22** (`.vscode/settings.json` + `extensions.json` committed early because the prettier extension was live while the threat shield was only `.prettierignore`, now deleted as redundant; verify the files match this contract, adjust only if drifted):

```jsonc
// .vscode/settings.json — JSONC, a dialect surface owned by VS Code itself
// (outside the json.tool owner, same class as .base files).
{
  // One form-owner per type: the IDE must never fight the owners
  // (docs/2026-08-21-lint-format-rethink.md). Python alone formats on save,
  // via the same pinned ruff the seam runs.
  "editor.formatOnSave": false,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  },
  "prettier.enable": false,
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "files.insertFinalNewline": true
}
```

```json
{
  "recommendations": ["charliermarsh.ruff"]
}
```

- [ ] **Step 3b-2: Emitter canonicality property tests** — `tests/test_canonical_form.py`, making the sole-writer-is-the-formatter principle mechanical: (1) render idempotence — rendering the same item twice yields identical bytes, and re-rendering rendered output changes nothing; (2) every ledger/inbox line the emitters produce matches the entry-grammar regex exactly; (3) scaffold output from templates is byte-stable across two runs into fresh directories. These give vault surfaces lifetime form-certainty with zero rules — enforced by the owners, verified by the suite.

**Contract notes recorded in pyproject comment**: the mdformat pin is a render-contract component (canonical template form leaks into rendered vault notes — a formatter upgrade is judged like a render change, with re-import expectations); oxfmt rejected 2026-08-21 with the mismatch named (it reformats *inside* fenced code blocks — quoted material — the prettier-incident class; measured live: respacing YAML in a quoted workflow snippet; plus a Node toolchain in a Python dev lane).

**Vault-side note (one line in the AGENTS.md template, informative not normative)**: formatters are writers; the vault's machine surfaces (`log/`, `inbox/review-queue.md`, literature managed regions, `system/bibliography.json`) each have an owner and a byte contract, and the trust machinery rejects foreign writers mechanically — this line explains why the alarms fire, it is not itself the enforcement.

- [ ] **Step 3c: Config validity test** — `tests/test_config_validity.py`: parse every repo JSON (`hooks/hooks.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `knowledge_harness/templates/harness/machine.json.example`) with stdlib `json` and every TOML (`pyproject.toml`) with `tomllib`; assert each loads **and that every JSON file equals its `json.dumps(obj, indent=2, ensure_ascii=False) + newline` canonical form** (the failure message prints the `python -m json.tool` command that fixes it). A malformed `hooks.json` currently fails silently at plugin load — this makes it fail loudly in CI. **Identifier-governance parity (added 2026-08-22, replacing an AGENTS.md context rule with mechanical enforcement):** the same test parses `docs/terminology.md` §4.4's tables and asserts every member of the code's reason-code registry, check-id set, and doctor probe-id set at HEAD has a row — an ungoverned identifier fails the suite instead of waiting for an audit. **Record-immutability check (added 2026-08-22 — mechanizes AGENTS.md's history rule per the eliminate>mechanism>rule ladder):** a pre-commit-config hook diffing the branch against origin/main and failing on any modification, rename, or deletion under the record paths (`research/`, `analysis/`, `docs/adr/`, completed plans — the manifest is a path list in the hook entry itself); once green in CI, the AGENTS.md sentence becomes a candidate for retirement. **Same test, same class — skill frontmatter**: for every `skills/*/SKILL.md`, parse the frontmatter with the core's own `frontmatter.parse` (dogfooding the tokenizer on real files, zero new deps) and assert the plugin contract: `name` present and equal to the skill's directory name, `description` present and non-empty, any `disable-model-invocation` value boolean. A typo'd SKILL.md frontmatter is the `hooks.json` failure class — silent at plugin load. (Vault-dialect frontmatter needs nothing here: its parser IS the lint, its sole writer IS the formatter, and the canonicality tests enforce both.)

- [ ] **Step 4: Verify clean + suite green**

Run: `ruff check knowledge_harness tests --no-cache && mypy knowledge_harness && mdformat --check --wrap keep README.md docs skills && python -m pytest tests -q`
Expected: `All checks passed!`, `Success: no issues found`, mdformat silent, and all tests PASS (the DTZ fix must not break date-based assertions; if a test pinned a local-clock date, fix the test to the UTC clock — same ruling).

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add pyproject.toml knowledge_harness tests
git commit -m "lint: ruff full-S-minus-idiom + mypy default mode (DTZ/UTC ruling, 10 type fixes, recorded skips)"
```

______________________________________________________________________

### Task 3: CRAP/CC backlog burn-down

**Files:**

- Modify: `knowledge_harness/__main__.py` (`_target_hash` split), `tests/test_inbox.py` (+ any test file covering `inbox.load` paths), `pyproject.toml` (mccabe tighten)

**Interfaces:**

- Consumes: Task 2's config (C90 at 32, gates green).
- Produces: `crap4py knowledge_harness --lcov lcov.info --max-crap 30` exits 0; `ruff check knowledge_harness` clean at `max-complexity = 28`. Task 5's workflow gates at these values.

**Why these two functions (measured 2026-08-20; as-built HEAD governs — if Plan C/T added functions violating the gates, burn those down here too, same recipes):** CRAP ≥ CC always (`CC² × (1−cov)³ + CC`), so `--max-crap 30` forces exactly two outcomes — `_target_hash` (CC 31, 77.3% cov, CRAP 42.3) can never pass at any coverage and **must split**; `inbox.load` (CC 27, 72.7%, CRAP 41.8) passes at **≥84% branch coverage** and needs **tests, not surgery**.

- [ ] **Step 1: Branch-coverage tests for `inbox.load`** — read the coverage report's uncovered branches for it (`python -m pytest tests -q --cov=knowledge_harness --cov-branch --cov-report=term-missing 2>/dev/null | grep inbox`), write failing-then-passing tests for each uncovered branch (malformed entries, ack-scope edges, empty/absent file paths — whatever the report names). Target: `inbox.load` branch coverage ≥85%.
- [ ] **Step 2: Verify the CRAP drop** — regenerate lcov, run `crap4py knowledge_harness --lcov lcov.info --fragment inbox`; expected: `inbox.load` CRAP ≤ 30.
- [ ] **Step 3: Split `_target_hash`** — extract coherent legs (per its structure at HEAD: the per-kind target-resolution branches are the natural seams) into named helpers until `_target_hash` and every extracted helper have CC ≤ 28. Pure refactor: no behavior change, suite stays green with zero test edits (if a test must change, stop — that's a behavior change, escalate).
- [ ] **Step 4: Tighten the mccabe cap** — `max-complexity = 32` → `28` in `pyproject.toml`; update the comment.
- [ ] **Step 5: Verify all gates green** — `ruff check knowledge_harness tests --no-cache && python -m pytest tests -q --cov=knowledge_harness --cov-branch --cov-report=lcov:lcov.info && crap4py knowledge_harness --lcov lcov.info --max-crap 30`; expected: all pass.
- [ ] **Step 6: Commit** — `git add knowledge_harness tests pyproject.toml && git commit -m "refactor: split _target_hash (CC<=28), branch-test inbox.load — CRAP ceiling 30, CC cap 28"`

______________________________________________________________________

### Task 4: Mutation gate script + blanket baseline

**Files:**

- Create: `scripts/mutation_gate.py`, `tests/test_mutation_gate.py`, `mutation-baseline.txt`, `knowledge_harness/<module>.py.manifest.json` for every module

**Interfaces:**

- Consumes: Task 1's installed tools; Task 2's clean lint state (the gate script and its tests must satisfy the extended rule set); Task 3's burn-down (baseline manifests must hash the post-refactor tree).

- Produces: `python scripts/mutation_gate.py --lcov lcov.info` (gate mode, exit 0/1) and `python scripts/mutation_gate.py --update-baseline --lcov lcov.info` (rewrites `mutation-baseline.txt`); baseline line format `<relpath>::<func-id>::<mutation>`; committed sidecar manifests. Task 3's workflow calls the gate mode verbatim.

- [ ] **Step 0: Confirm Task 0 (post-D batch) is committed on this branch** — it carries the last planned pre-baseline churn; Plan R and the cuts are long merged. Do not build manifests with any Task 0 work pending.

**Design constraints the script encodes (verified live 2026-08-20):**

- mutate4py exits 0 even when mutants survive → pass/fail must come from parsing the `Survivors:` section.

- Survivor lines look like `  line 79 char == "-" -> char != "-" func/_norm_with_map`. Baseline keys **exclude the line number** (`file::func/_norm_with_map::char == "-" -> char != "-"`) so unrelated edits shifting lines don't churn the baseline.

- Policy: survivors matching a baseline key pass (pre-existing = backlog, never gate); any other survivor fails. Uncovered sites never fail the gate (coverage is crap4py's beat).

- Gate mode scopes to files changed vs a base ref (merge-base diff); no changed core files → exit 0.

- **git pathspecs resolve relative to the cwd.** The diff runs with `cwd=CORE` (the repository root), flag `--relative`, and pathspec `knowledge_harness/*.py`. A stale, `core/`-prefixed pathspec (`core/knowledge_harness/*.py` — the pre-flip nested layout) matches nothing and the gate passes forever — which is why `changed_modules` gets its own unit test against a scratch git repo (a dead gate and a working gate are otherwise indistinguishable on a quiet branch).

- Baseline keys collapse duplicate identical mutations within one function (the real selectors output has `1 -> 0` twice on line 79) — deliberate: an advisory lane prefers a stable baseline over distinguishing repeats of an already-recorded survivor.

- Tests import `from scripts.mutation_gate import …`, which resolves because every standardized invocation is `python -m pytest` from the repository root (cwd lands on `sys.path`). Bare `pytest` breaks the import — keep the invocation as written.

- [ ] **Step 0b: Kill the bare-pytest footgun** — add `pythonpath = ["."]` and `testpaths = ["tests"]` (parked from Plan L: post-flip, pytest's rootdir is the whole repo; pinning collection was deliberately excluded from L's zero-behavior-change branch) to `[tool.pytest.ini_options]` in `pyproject.toml`, so bare `pytest` and `python -m pytest` resolve `scripts.*` imports identically (config beats remembered convention; the entry-point audit 2026-08-21 flagged bare `pytest` as a caller-less entry point that silently breaks).

- [ ] **Step 1: Write the failing tests** — `tests/test_mutation_gate.py`:

```python
"""Unit tests for the no-new-survivors mutation gate (parsing + comparison only;
no subprocess — the mutate4py invocation itself is exercised by the baseline run)."""

from pathlib import Path

from scripts.mutation_gate import (
    baseline_keys,
    changed_modules,
    new_survivors,
    parse_survivors,
)

SAMPLE_OUTPUT = """\
Mutation run: knowledge_harness/selectors.py
Total mutation sites: 71
Covered mutation sites: 54
Uncovered mutation sites: 17
Mutation workers: 4

Mutation Report
===============
Killed: 35
Survived: 3
Uncovered: 17
Per-Mutant overhead: 0.33s

Survivors:
  line 79 char == "-" -> char != "-" func/_norm_with_map
  line 119 position < 0 -> position <= 0 func/find_context
  line 123 end < len(text) -> end <= len(text) func/find_context
"""


def test_parse_survivors_extracts_file_func_and_mutation():
    keys = parse_survivors("knowledge_harness/selectors.py", SAMPLE_OUTPUT)
    assert keys == {
        'knowledge_harness/selectors.py::func/_norm_with_map::char == "-" -> char != "-"',
        "knowledge_harness/selectors.py::func/find_context::position < 0 -> position <= 0",
        "knowledge_harness/selectors.py::func/find_context::end < len(text) -> end <= len(text)",
    }


def test_parse_survivors_empty_when_no_survivors_section():
    assert parse_survivors("knowledge_harness/paths.py", "Killed: 5\nSurvived: 0\n") == set()


def test_new_survivors_ignores_baselined_keys():
    baseline = {
        'knowledge_harness/selectors.py::func/_norm_with_map::char == "-" -> char != "-"',
    }
    found = parse_survivors("knowledge_harness/selectors.py", SAMPLE_OUTPUT)
    fresh = new_survivors(found, baseline)
    assert fresh == {
        "knowledge_harness/selectors.py::func/find_context::position < 0 -> position <= 0",
        "knowledge_harness/selectors.py::func/find_context::end < len(text) -> end <= len(text)",
    }


def test_baseline_round_trip(tmp_path: Path):
    path = tmp_path / "mutation-baseline.txt"
    keys = {"b::func/x::1 -> 0", "a::func/y::True -> False"}
    path.write_text("\n".join(sorted(keys)) + "\n", encoding="utf-8")
    assert baseline_keys(path) == keys


def test_baseline_missing_file_is_empty(tmp_path: Path):
    assert baseline_keys(tmp_path / "absent.txt") == set()


def test_changed_modules_lists_modified_core_files(tmp_path: Path):
    """The one function deciding whether the gate ever runs must be proven live:
    a wrong pathspec makes the diff silently empty and the gate passes forever."""
    import subprocess

    repo = tmp_path / "repo"
    (repo / "knowledge_harness").mkdir(parents=True)

    def git(*argv: str) -> None:
        subprocess.run(["git", *argv], cwd=repo, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.invalid")
    git("config", "user.name", "t")
    (repo / "knowledge_harness" / "x.py").write_text("A = 1\n", encoding="utf-8")
    (repo / "knowledge_harness" / "__init__.py").write_text("", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    git("checkout", "-q", "-b", "feature")
    (repo / "knowledge_harness" / "x.py").write_text("A = 2\n", encoding="utf-8")
    (repo / "knowledge_harness" / "__init__.py").write_text("B = 1\n", encoding="utf-8")
    git("commit", "-q", "-a", "-m", "change")

    assert changed_modules("main", cwd=repo) == ["knowledge_harness/x.py"]
```

- [ ] **Step 2: Run to verify failure**

Run: `source .venv/bin/activate && python -m pytest tests/test_mutation_gate.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts'`

- [ ] **Step 3: Write the script** — `scripts/__init__.py` (empty) and `scripts/mutation_gate.py`:

```python
"""No-new-survivors mutation gate over mutate4py.

Invoked explicitly as `python scripts/mutation_gate.py` — no shebang on purpose
(EXE001 fires on a shebang in a non-executable file, and nothing execs this directly).

Gate mode (default): mutation-test the knowledge_harness files changed since --base,
fail (exit 1) on any survivor whose key is absent from the committed baseline.
--update-baseline: blanket-run every knowledge_harness module (--mutate-all) and
rewrite the baseline file with every current survivor.

mutate4py exits 0 even when mutants survive, so pass/fail is parsed from the
"Survivors:" report section. Baseline keys exclude line numbers on purpose:
`<relpath>::<func-id>::<mutation>` stays stable across unrelated edits.
Always invokes mutate4py with --manifest-file (sidecar); the embedded manifest
mode writes into production source files and is never acceptable here.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

CORE = Path(__file__).resolve().parent.parent  # repo root
SURVIVOR_RE = re.compile(r"^\s+line \d+ (?P<mutation>.+) (?P<func>func/\S+)$")


def parse_survivors(relpath: str, output: str) -> set[str]:
    keys: set[str] = set()
    in_section = False
    for line in output.splitlines():
        if line.startswith("Survivors:"):
            in_section = True
            continue
        if in_section:
            match = SURVIVOR_RE.match(line)
            if match is None:
                if line.strip():
                    in_section = False
                continue
            keys.add(f"{relpath}::{match['func']}::{match['mutation']}")
    return keys


def new_survivors(found: set[str], baseline: set[str]) -> set[str]:
    return found - baseline


def baseline_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {line for line in path.read_text(encoding="utf-8").splitlines() if line}


def changed_modules(base: str, cwd: Path = CORE) -> list[str]:
    # --relative + a cwd-relative pathspec, both resolved from the repo root: a
    # stale core/-prefixed pathspec here matches nothing and kills the gate silently.
    diff = subprocess.run(
        ["git", "diff", "--name-only", "--relative", f"{base}...HEAD", "--", "knowledge_harness/*.py"],
        capture_output=True,
        text=True,
        check=True,
        cwd=cwd,
    ).stdout.split()
    return sorted(
        p
        for p in diff
        if p.endswith(".py") and not p.endswith("__init__.py") and (cwd / p).exists()
    )


def _all_modules() -> list[str]:
    return sorted(
        f"knowledge_harness/{p.name}"
        for p in (CORE / "knowledge_harness").glob("*.py")
        if p.name != "__init__.py"
    )


def _run_mutate(relpath: str, lcov: str, extra: list[str], max_workers: int) -> str:
    cmd = [
        sys.executable, "-m", "mutate4py", relpath,
        "--lcov", lcov, "--manifest-file", "--max-workers", str(max_workers),
        *extra,
    ]
    # check=False deliberate: mutate4py exits 0 even with survivors; stdout is the signal
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=CORE, check=False)
    sys.stderr.write(proc.stderr)
    return proc.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lcov", required=True, help="pre-generated branch-coverage LCOV")
    parser.add_argument("--base", default="origin/main", help="gate mode: diff base ref")
    parser.add_argument("--baseline", default=str(CORE / "mutation-baseline.txt"))
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--test-contexts", default=None, help="optional contexts db for narrowing")
    args = parser.parse_args()

    extra = ["--test-contexts", args.test_contexts] if args.test_contexts else []
    baseline_path = Path(args.baseline)

    if args.update_baseline:
        keys: set[str] = set()
        for module in _all_modules():
            print(f"[baseline] {module}", flush=True)
            out = _run_mutate(module, args.lcov, [*extra, "--mutate-all"], args.max_workers)
            keys |= parse_survivors(module, out)
        baseline_path.write_text("\n".join(sorted(keys)) + "\n", encoding="utf-8")
        print(f"[baseline] {len(keys)} survivors written to {baseline_path}")
        return 0

    modules = changed_modules(args.base)
    if not modules:
        print("[gate] no changed knowledge_harness modules; pass")
        return 0
    baseline = baseline_keys(baseline_path)
    fresh: set[str] = set()
    for module in modules:
        print(f"[gate] {module}", flush=True)
        out = _run_mutate(module, args.lcov, extra, args.max_workers)
        print(out)
        fresh |= new_survivors(parse_survivors(module, out), baseline)
    if fresh:
        print(f"[gate] FAIL — {len(fresh)} new survivor(s):")
        for key in sorted(fresh):
            print(f"  {key}")
        return 1
    print("[gate] pass — no new survivors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run to verify green**

Run: `python -m pytest tests/test_mutation_gate.py -q`
Expected: 6 PASS. Then full suite: `python -m pytest tests -q` — all PASS (452+ at HEAD).

- [ ] **Step 5: Build the contexts DB** (one-time; **measured 2026-08-22: ~9–10 min at 1454 tests** — 9m00s and 9m36s over two builds, ~0.37 s per isolated session, mostly thanks to the settle_seconds=0 fix. Supersedes both prior figures: the original ~10–15 min was measured at 452 tests, and the same-day ~35–50 min re-estimate assumed 1.5–2 s per session — wrong in the other direction; no mutation run)

Run: `python -m mutate4py --build-test-contexts .contexts.db --pytest-args 'tests -q -p no:cacheprovider'`
Expected: `.contexts.db` written (gitignored). **Fallback amended 2026-08-22: if the build degrades or errors, STOP and report — do not proceed to a no-contexts blanket.** Full-suite-per-mutant is no longer the plan's "acceptable one-time ~2.5 h": serial suite is now 78 s, so ~1,250 sites at 4 workers is ~7 h. The contexts DB is load-bearing; a failed build is a finding to hand back, not a degraded mode to absorb silently.

- [ ] **Step 6: Blanket baseline run** (~10–15 min with contexts — measured against the 452-test suite; expect longer at 1454 tests and record the actual wall-clock in the task report)

```bash
python -m pytest tests -q --cov=knowledge_harness --cov-branch --cov-report=lcov:lcov.info
python scripts/mutation_gate.py --update-baseline --lcov lcov.info --test-contexts .contexts.db
```

Expected: `mutation-baseline.txt` written (expect roughly 150–250 keys); one `<module>.py.manifest.json` sidecar beside every module. Spot-check: `test -f knowledge_harness/selectors.py.manifest.json` and `git diff --stat knowledge_harness/*.py` shows **zero** source-file modifications (sidecar mode holds).

- [ ] **Step 7: Verify the differential is quiet, then commit**

Run: `python scripts/mutation_gate.py --lcov lcov.info --base HEAD` — Expected: `no changed knowledge_harness modules; pass` (exit 0).

```bash
cd "$(git rev-parse --show-toplevel)"
git add scripts tests/test_mutation_gate.py mutation-baseline.txt knowledge_harness/*.manifest.json
git commit -m "feat: mutation gate script + blanket baseline (sidecar manifests, no-new-survivors policy)"
```

______________________________________________________________________

### Task 5: Advisory quality workflow (ruff + crap4py ceiling + drywall + mutation gate)

**Files:**

- Create: `.github/workflows/quality.yml`

**Interfaces:**

- Consumes: Task 1's dev extra; Task 2's ruff+mypy rule set; Task 3's burn-down (gate 30 is only green after it); Task 4's `scripts/mutation_gate.py`, committed manifests and baseline.
- Produces: one advisory workflow, `quality`, on pull requests and manual dispatch.

**Thresholds:** `crap4py --max-crap 30` — the conventional CRAP line, green after Task 3's burn-down (CRAP ≥ CC, so 30 also enforces CC ≤ 30; the ruff C90 cap at 28 backstops below it). drywall default threshold 0.82 — currently zero duplicates. crap4py exit behavior verified live 2026-08-20: exceeds → exit 1.

**Trigger reality:** this repo's practice to date is local merge + push to main — no PRs. The `push: branches: [main]` trigger exists so tests, the CRAP ceiling, and drywall run on every landing; on a push event the mutation gate no-ops by construction (`origin/main...HEAD` is empty after push) and earns its keep only on `pull_request` and `workflow_dispatch` runs. This is deliberate, not a bug — do not "fix" the gate to run on push.

- [ ] **Step 1: Write the workflow** — `.github/workflows/quality.yml`:

```yaml
name: quality

on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  quality:
    name: dev-quality lane (advisory)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # mutation gate diffs against the merge base
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install
        run: pip install -e ".[dev]"
      - name: Form + lint (the one command — same as local)
        run: pre-commit run --all-files --show-diff-on-failure
      - name: Residual binary hooks (manual stage)
        run: pre-commit run --all-files --hook-stage manual
      - name: Workflow lint (actionlint)
        uses: raven-actions/actionlint@v2
      - name: Shell lint (shellcheck)
        run: shellcheck knowledge_harness/templates/git/pre-commit
      - name: Tests + branch coverage
        run: python -m pytest tests -q --cov=knowledge_harness --cov-branch --cov-report=lcov:lcov.info
      - name: CRAP ceiling (crap4py)
        run: crap4py knowledge_harness --lcov lcov.info --max-crap 30
      - name: Duplicate gate (drywall)
        run: drywall knowledge_harness
      - name: Mutation gate (no new survivors)
        run: python scripts/mutation_gate.py --lcov lcov.info --base "origin/${{ github.base_ref || 'main' }}"
```

- [ ] **Step 2: Verify each gate command locally** (worktree stand-in for CI)

```bash
source .venv/bin/activate
ruff check knowledge_harness tests scripts && echo LINT-OK
mypy knowledge_harness && echo TYPE-OK
python -m pytest tests -q --cov=knowledge_harness --cov-branch --cov-report=lcov:lcov.info
crap4py knowledge_harness --lcov lcov.info --max-crap 30 && echo CRAP-OK
drywall knowledge_harness && echo DRY-OK
python scripts/mutation_gate.py --lcov lcov.info --base origin/main && echo MUT-OK
```

Expected: `LINT-OK`, `TYPE-OK`, `CRAP-OK`, `DRY-OK`, `MUT-OK`. Also verify locally: `pre-commit run --all-files` clean (the one command — supersedes per-tool invocations); `shellcheck knowledge_harness/templates/git/pre-commit` clean (actionlint runs CI-side; if its action name/version differs at execution, use the current official actionlint action and record it). (The mutation gate re-tests this branch's changed core files — the gate script itself lives outside `knowledge_harness`, so expect a small or empty module list.)

- [ ] **Step 3: Negative check of the CRAP gate** (proves the gate can fail)

Run: `crap4py knowledge_harness --lcov lcov.info --max-crap 15; echo "exit=$?"`
Expected: `exit=1` (several functions sit between 15 and 30 post-burn-down). Do not commit any change from this step.

- [ ] **Step 4: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add .github/workflows/quality.yml
git commit -m "ci: advisory dev-quality workflow (crap ceiling 45, drywall, mutation no-new-survivors)"
```

______________________________________________________________________

### Task 6: Merge

- [ ] **Step 1: Full acceptance in the worktree** — `python -m pytest tests -q` green; the gate commands from Task 5 Step 2 all pass; `git status` clean; `git diff main --stat` shows only this plan's files plus manifests.
- [ ] **Step 2: Merge to main** per `superpowers:finishing-a-development-branch` (merge locally, push, remove worktree, prune).
- [ ] **Step 3: Post-merge note** — append one line to the "Actionable backlog surfaced" section of `research/code-quality-tools-gabadi.md`: baseline landed, survivor count, and the ratchet reminder (lower `--max-crap` as items 2–3 burn down). Commit as `docs: record quality-lane baseline landing`.

______________________________________________________________________

## Self-review notes

- **Spec coverage**: this plan implements the deferred-register entry "mutation-testing baseline (post-Plan-T, parallelizable with Plan D)" in full — contexts DB, blanket, sidecar manifests, no-new-survivors CI, plus the recorded crap4py/drywall adoption order. Nothing else in the register is touched.
- **Exit-code truths encoded**: mutate4py exit 0 with survivors (hence the parser), crap4py exit 1 over ceiling (verified), drywall exit 1 on duplicates / 2 on bad args.
- **Type consistency**: gate entry points `parse_survivors(relpath, output)`, `new_survivors(found, baseline)`, `baseline_keys(path)`, `changed_modules(base, cwd)` match between Task 4's tests and script; Task 5 calls the CLI exactly as Task 4 produces it; the gate script carries explicit `check=False` so Task 2's PLW1510 adoption stays clean.
- **AST-churn sequencing**: Tasks 2 (lint/type fixes) and 3 (burn-down refactor) both run before Task 4's blanket baseline on purpose — all pre-baseline churn lands first, so manifests hash the settled tree.
- **Known risk left open deliberately**: if `--build-test-contexts` proves unreliable (its own help warns shared-session DBs degrade to the full test set), the blanket falls back to full-suite-per-mutant — **re-ruled 2026-08-22: no longer an acceptable silent fallback (~7 h at the 1454-test suite, not the 2.5 h this line assumed); Step 5 now stops and reports instead**. The CI gate path still never needs the contexts DB because diffs keep mutant counts small.
