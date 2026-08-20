# Plan Q: Dev-Quality Lane (mutation baseline + advisory gates) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the dev-quality lane for the harness's own code: a one-time mutate4py blanket baseline with committed sidecar manifests, a "no new survivors" differential gate, a crap4py CRAP-score ceiling, and a drywall duplicate gate — wired into one advisory GitHub Actions workflow.

**Architecture:** Three tool adoptions (live-reviewed 2026-08-20, see `research/code-quality-tools-gabadi.md`) land as pinned dev dependencies; a small gate script turns mutate4py's exit-0-even-with-survivors output into a baseline-compared pass/fail; the blanket run commits per-module sidecar manifests so differential reruns persist across clones with zero CI state. Everything measures **harness code quality only** — nothing here touches the vault's publish-gate closing sets.

**Tech Stack:** Python ≥3.11 for the lane (repo core stays ≥3.10; the lane's CI job runs 3.12), pytest + pytest-cov (LCOV branch coverage), mutate4py 0.1.4, crap4py 0.1.1, drywall 0.1.3, GitHub Actions.

## Global Constraints

- **Sequencing gate: execute only after Plan T (terminology wave) is merged to main.** The wave renames identifiers; `ast.unparse()` manifest hashes change wholesale, and a pre-wave baseline is dead weight. **Parallelizable with Plan D** (author ruling 2026-08-20) — D is skills/markdown; any core-Python overlap costs one differential top-up after both merge.
- Worktree via `superpowers:using-git-worktrees`, branch `build/quality-lane`.
- **As-built HEAD governs**: the module list, folder names, and skill names in this plan reflect pre-wave state; use the post-wave names at HEAD wherever they differ, and record adaptations in the commit message.
- Every test Run begins `cd core && python3 -m venv .venv 2>/dev/null; source .venv/bin/activate && pip install -e ".[dev]" -q` (idempotent; PEP 668).
- Tool versions are **pinned exact** (single-maintainer v0.1.x tools — treat as removable; upgrades are deliberate acts).
- mutate4py always runs with `--manifest-file` (sidecar JSON). The embedded-in-source mode appends a footer to production files — never acceptable in this repo.
- The lane is **advisory**: the workflow fails visibly but is not a required check (no branch protection exists; do not add any).
- Live-measured costs to expect (2026-08-20, 4 workers): ~1,250 mutation sites repo-wide; blanket with test-contexts narrowing ~10–15 min; contexts DB build (one isolated coverage session per collected test, 452 tests) ~10–15 min, one-time; full suite 37 s.
- Commit messages conventional; one commit per task.

## File Structure

- Modify: `core/pyproject.toml` (dev extras), `.gitignore`
- Create: `core/scripts/mutation_gate.py` (gate + baseline updater), `core/tests/test_mutation_gate.py`, `core/mutation-baseline.txt` (committed survivor baseline), `core/harness_core/*.py.manifest.json` (one sidecar per module, committed), `.github/workflows/quality.yml`

---

### Task 1: Pinned dev dependencies and hygiene

**Files:**
- Modify: `core/pyproject.toml`, `.gitignore`

**Interfaces:**
- Produces: installable `dev` extra containing `pytest-cov==7.1.0`, `mutate4py==0.1.4`, `crap4py==0.1.1`, `drywall==0.1.3` (later tasks and CI install exactly this).

- [ ] **Step 1: Extend the dev extra** in `core/pyproject.toml`:

```toml
dev = [
    "pytest>=8",
    "ruff==0.15.21",
    "pytest-cov==7.1.0",
    "mutate4py==0.1.4",
    "crap4py==0.1.1",
    "drywall==0.1.3",
]
```

- [ ] **Step 2: Extend `.gitignore`** (repo root) with the lane's transient artifacts:

```
core/.mutate4py/
core/lcov.info
core/.coverage
core/.coverage.*
core/.contexts.db
```

- [ ] **Step 3: Install and verify**

Run: `cd core && source .venv/bin/activate && pip install -e ".[dev]" -q && mutate4py --help >/dev/null && crap4py --help >/dev/null && drywall --help >/dev/null && python -c "import pytest_cov" && echo OK`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core/pyproject.toml .gitignore
git commit -m "build: pin dev-quality lane tools (pytest-cov, mutate4py, crap4py, drywall)"
```

---

### Task 2: Mutation gate script + blanket baseline

**Files:**
- Create: `core/scripts/mutation_gate.py`, `core/tests/test_mutation_gate.py`, `core/mutation-baseline.txt`, `core/harness_core/<module>.py.manifest.json` for every module

**Interfaces:**
- Consumes: Task 1's installed tools.
- Produces: `python scripts/mutation_gate.py --lcov lcov.info` (gate mode, exit 0/1) and `python scripts/mutation_gate.py --update-baseline --lcov lcov.info` (rewrites `mutation-baseline.txt`); baseline line format `<relpath>::<func-id>::<mutation>`; committed sidecar manifests. Task 3's workflow calls the gate mode verbatim.

**Design constraints the script encodes (verified live 2026-08-20):**
- mutate4py exits 0 even when mutants survive → pass/fail must come from parsing the `Survivors:` section.
- Survivor lines look like `  line 79 char == "-" -> char != "-" func/_norm_with_map`. Baseline keys **exclude the line number** (`file::func/_norm_with_map::char == "-" -> char != "-"`) so unrelated edits shifting lines don't churn the baseline.
- Policy: survivors matching a baseline key pass (pre-existing = backlog, never gate); any other survivor fails. Uncovered sites never fail the gate (coverage is crap4py's beat).
- Gate mode scopes to files changed vs a base ref (merge-base diff); no changed core files → exit 0.

- [ ] **Step 1: Write the failing tests** — `core/tests/test_mutation_gate.py`:

```python
"""Unit tests for the no-new-survivors mutation gate (parsing + comparison only;
no subprocess — the mutate4py invocation itself is exercised by the baseline run)."""

from pathlib import Path

from scripts.mutation_gate import baseline_keys, new_survivors, parse_survivors

SAMPLE_OUTPUT = """\
Mutation run: harness_core/selectors.py
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
    keys = parse_survivors("harness_core/selectors.py", SAMPLE_OUTPUT)
    assert keys == {
        'harness_core/selectors.py::func/_norm_with_map::char == "-" -> char != "-"',
        "harness_core/selectors.py::func/find_context::position < 0 -> position <= 0",
        "harness_core/selectors.py::func/find_context::end < len(text) -> end <= len(text)",
    }


def test_parse_survivors_empty_when_no_survivors_section():
    assert parse_survivors("harness_core/paths.py", "Killed: 5\nSurvived: 0\n") == set()


def test_new_survivors_ignores_baselined_keys():
    baseline = {
        'harness_core/selectors.py::func/_norm_with_map::char == "-" -> char != "-"',
    }
    found = parse_survivors("harness_core/selectors.py", SAMPLE_OUTPUT)
    fresh = new_survivors(found, baseline)
    assert fresh == {
        "harness_core/selectors.py::func/find_context::position < 0 -> position <= 0",
        "harness_core/selectors.py::func/find_context::end < len(text) -> end <= len(text)",
    }


def test_baseline_round_trip(tmp_path: Path):
    path = tmp_path / "mutation-baseline.txt"
    keys = {"b::func/x::1 -> 0", "a::func/y::True -> False"}
    path.write_text("\n".join(sorted(keys)) + "\n", encoding="utf-8")
    assert baseline_keys(path) == keys


def test_baseline_missing_file_is_empty(tmp_path: Path):
    assert baseline_keys(tmp_path / "absent.txt") == set()
```

- [ ] **Step 2: Run to verify failure**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_mutation_gate.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts'`

- [ ] **Step 3: Write the script** — `core/scripts/__init__.py` (empty) and `core/scripts/mutation_gate.py`:

```python
#!/usr/bin/env python3
"""No-new-survivors mutation gate over mutate4py.

Gate mode (default): mutation-test the harness_core files changed since --base,
fail (exit 1) on any survivor whose key is absent from the committed baseline.
--update-baseline: blanket-run every harness_core module (--mutate-all) and
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

CORE = Path(__file__).resolve().parent.parent  # .../core
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


def _changed_modules(base: str) -> list[str]:
    diff = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD", "--", "core/harness_core/*.py"],
        capture_output=True,
        text=True,
        check=True,
        cwd=CORE,
    ).stdout.split()
    return sorted(
        p.removeprefix("core/")
        for p in diff
        if p.endswith(".py") and not p.endswith("__init__.py") and (CORE / p.removeprefix("core/")).exists()
    )


def _all_modules() -> list[str]:
    return sorted(
        f"harness_core/{p.name}"
        for p in (CORE / "harness_core").glob("*.py")
        if p.name != "__init__.py"
    )


def _run_mutate(relpath: str, lcov: str, extra: list[str], max_workers: int) -> str:
    cmd = [
        sys.executable, "-m", "mutate4py", relpath,
        "--lcov", lcov, "--manifest-file", "--max-workers", str(max_workers),
        *extra,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=CORE)
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

    modules = _changed_modules(args.base)
    if not modules:
        print("[gate] no changed harness_core modules; pass")
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
Expected: 5 PASS. Then full suite: `python -m pytest tests -q` — all PASS (452+ at HEAD).

- [ ] **Step 5: Build the contexts DB** (one-time, ~10–15 min; no mutation run)

Run: `python -m mutate4py --build-test-contexts .contexts.db --pytest-args 'tests -q -p no:cacheprovider'`
Expected: `.contexts.db` written (gitignored). If the build degrades or errors, proceed without it — blanket then runs full-suite-per-mutant (~2.5 h at 4 workers); note which path was taken in the task report.

- [ ] **Step 6: Blanket baseline run** (~10–15 min with contexts)

```bash
python -m pytest tests -q --cov=harness_core --cov-branch --cov-report=lcov:lcov.info
python scripts/mutation_gate.py --update-baseline --lcov lcov.info --test-contexts .contexts.db
```
Expected: `mutation-baseline.txt` written (expect roughly 150–250 keys); one `<module>.py.manifest.json` sidecar beside every module. Spot-check: `test -f harness_core/selectors.py.manifest.json` and `git diff --stat harness_core/*.py` shows **zero** source-file modifications (sidecar mode holds).

- [ ] **Step 7: Verify the differential is quiet, then commit**

Run: `python scripts/mutation_gate.py --lcov lcov.info --base HEAD` — Expected: `no changed harness_core modules; pass` (exit 0).

```bash
cd "$(git rev-parse --show-toplevel)"
git add core/scripts core/tests/test_mutation_gate.py core/mutation-baseline.txt core/harness_core/*.manifest.json
git commit -m "feat: mutation gate script + blanket baseline (sidecar manifests, no-new-survivors policy)"
```

---

### Task 3: Advisory quality workflow (crap4py ceiling + drywall + mutation gate)

**Files:**
- Create: `.github/workflows/quality.yml`

**Interfaces:**
- Consumes: Task 1's dev extra; Task 2's `scripts/mutation_gate.py`, committed manifests and baseline.
- Produces: one advisory workflow, `quality`, on pull requests and manual dispatch.

**Thresholds (live-measured 2026-08-20):** `crap4py --max-crap 45` — current worst is `_target_hash` at 42.3, so the lane starts green; ratchet the number down as the CRAP backlog (`research/code-quality-tools-gabadi.md`) burns down. drywall default threshold 0.82 — currently zero duplicates. crap4py exit behavior verified: exceeds → exit 1.

- [ ] **Step 1: Write the workflow** — `.github/workflows/quality.yml`:

```yaml
name: quality

on:
  pull_request:
  workflow_dispatch:

jobs:
  quality:
    name: dev-quality lane (advisory)
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: core
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # mutation gate diffs against the merge base
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install
        run: pip install -e ".[dev]"
      - name: Tests + branch coverage
        run: python -m pytest tests -q --cov=harness_core --cov-branch --cov-report=lcov:lcov.info
      - name: CRAP ceiling (crap4py)
        run: crap4py harness_core --lcov lcov.info --max-crap 45
      - name: Duplicate gate (drywall)
        run: drywall harness_core
      - name: Mutation gate (no new survivors)
        run: python scripts/mutation_gate.py --lcov lcov.info --base "origin/${{ github.base_ref || 'main' }}"
```

- [ ] **Step 2: Verify each gate command locally** (worktree stand-in for CI)

```bash
cd core && source .venv/bin/activate
python -m pytest tests -q --cov=harness_core --cov-branch --cov-report=lcov:lcov.info
crap4py harness_core --lcov lcov.info --max-crap 45 && echo CRAP-OK
drywall harness_core && echo DRY-OK
python scripts/mutation_gate.py --lcov lcov.info --base origin/main && echo MUT-OK
```
Expected: `CRAP-OK`, `DRY-OK`, `MUT-OK`. (The mutation gate re-tests this branch's changed core files — the gate script itself lives outside `harness_core`, so expect a small or empty module list.)

- [ ] **Step 3: Negative check of the CRAP gate** (proves the gate can fail)

Run: `crap4py harness_core --lcov lcov.info --max-crap 30; echo "exit=$?"`
Expected: `exit=1` (two known functions exceed 30). Do not commit any change from this step.

- [ ] **Step 4: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add .github/workflows/quality.yml
git commit -m "ci: advisory dev-quality workflow (crap ceiling 45, drywall, mutation no-new-survivors)"
```

---

### Task 4: Merge

- [ ] **Step 1: Full acceptance in the worktree** — `python -m pytest tests -q` green; the three gate commands from Task 3 Step 2 all pass; `git status` clean; `git diff main --stat` shows only this plan's files plus manifests.
- [ ] **Step 2: Merge to main** per `superpowers:finishing-a-development-branch` (merge locally, push, remove worktree, prune).
- [ ] **Step 3: Post-merge note** — append one line to the "Actionable backlog surfaced" section of `research/code-quality-tools-gabadi.md`: baseline landed, survivor count, and the ratchet reminder (lower `--max-crap` as items 2–3 burn down). Commit as `docs: record quality-lane baseline landing`.

---

## Self-review notes

- **Spec coverage**: this plan implements the deferred-register entry "mutation-testing baseline (post-Plan-T, parallelizable with Plan D)" in full — contexts DB, blanket, sidecar manifests, no-new-survivors CI, plus the recorded crap4py/drywall adoption order. Nothing else in the register is touched.
- **Exit-code truths encoded**: mutate4py exit 0 with survivors (hence the parser), crap4py exit 1 over ceiling (verified), drywall exit 1 on duplicates / 2 on bad args.
- **Type consistency**: gate entry points `parse_survivors(relpath, output)`, `new_survivors(found, baseline)`, `baseline_keys(path)` match between Task 2's tests and script; Task 3 calls the CLI exactly as Task 2 produces it.
- **Known risk left open deliberately**: if `--build-test-contexts` proves unreliable (its own help warns shared-session DBs degrade to the full test set), the blanket falls back to full-suite-per-mutant (~2.5 h) — acceptable one-time; the CI gate path never needs the contexts DB because diffs keep mutant counts small.
