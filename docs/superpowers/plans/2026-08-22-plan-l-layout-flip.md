# Plan L: Layout Flip (`core/` → repo root) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the Python package to repo root in the ruled post-R/pre-Q window (spec §10 release-gate entry, re-ruled 2026-08-21), so Plan Q's manifests, workflow, pre-commit config, and IDE settings all land once, on final paths.

**Architecture:** One mechanical wave: `core/*` contents rise one level (`harness_core/`, `tests/`, `pyproject.toml` at root), every consumer loses one path segment, Plan Q's authored text is swept to final paths in the same wave. No logic changes anywhere — pure moves plus path-string edits.

**Tech Stack:** git mv, Python ≥3.10, pytest.

**Authority:** spec §10 release-gate entry (the window ruling and its rationale). **As-built HEAD governs**; cited paths are anchors.

## Global Constraints

- Worktree via `superpowers:using-git-worktrees`, branch `build/layout-flip`. Merge + push in the same motion at the end.
- **Zero behavior change**: the suite must pass unmodified except for path/import mechanics; if any step forces a semantic question, stop and escalate as an SDD ruling.
- Records untouched (history rule): completed plans and records keep their `core/` path mentions — they describe the tree as it was.
- One commit per task; suite green at each.

## File Structure (after)

```
harness_core/          # was core/harness_core/ (templates ride inside, unchanged)
tests/                 # was core/tests/
pyproject.toml         # was core/pyproject.toml
.venv/                 # recreated at root (gitignored)
hooks/  skills/  .claude-plugin/  docs/  research/  analysis/  sources/   # unchanged
```

---

### Task 1: The move + import/config mechanics

**Files:**
- Move: `core/harness_core` → `harness_core`, `core/tests` → `tests`, `core/pyproject.toml` → `pyproject.toml`; delete the emptied `core/`.
- Modify: `.gitignore`, `hooks/posttooluse_lint.py`, `hooks/stop_publish_gate.py`, `tests/` path fixtures, `.vscode/settings.json`, `harness_core/__init__.py` docstring.

- [ ] **Step 1: git mv the three trees**, then fix `.gitignore`: every `core/`-prefixed line drops the prefix (`.venv/`, `*.egg-info/`, `.mutate4py/`, `lcov.info`, `.coverage*`, `.contexts.db` — per the lines present at HEAD).
- [ ] **Step 2: Hooks lose a segment** — the `parents[1] / "core"` sys.path injection becomes `parents[1]` in both hooks; grep confirms no other `"core"` path literal in `hooks/`.
- [ ] **Step 3: Test path fixtures** — `tests/test_hooks.py` and `tests/test_skill_files.py` compute repo root via `parents[N]`; each drops one level (their files are now one level shallower). Sweep `tests/` for `"core"` path literals (conftest, template paths) — judged, not blind: the word appears in prose senses.
- [ ] **Step 4: Config residue** — `.vscode/settings.json` interpreter path becomes `${workspaceFolder}/.venv/bin/python`; `harness_core/__init__.py` docstring's spec path stays valid (already `docs/superpowers/specs/...`).
- [ ] **Step 5: Recreate the venv at root** (`python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]" -q`), run `python -m pytest tests -q`.
Expected: 865 passed / 6 skipped, unchanged.
- [ ] **Step 6: Commit** — `git commit -m "refactor: layout flip — package to repo root (post-R/pre-Q window, spec §10)"`

---

### Task 2: Plan Q path sweep (authored text, free edit)

**Files:**
- Modify: `docs/superpowers/plans/2026-08-20-plan-q-quality-lane.md`

- [ ] **Step 1:** Sweep every `core/` path in Plan Q to final form: `cd core &&` prefixes drop; `core/pyproject.toml` → `pyproject.toml`; `core/harness_core` → `harness_core`; `core/tests` → `tests`; `core/scripts` → `scripts`; workflow `working-directory: core` lines drop; `.gitignore` snippet block loses prefixes; mdformat/pre-commit path lists lose `core/` segments; the `.pre-commit-config.yaml` block's `cd core &&` entries simplify. Judged sweep — `core` appears in prose senses ("the core's own parser") that stay.
- [ ] **Step 2:** Self-check: `grep -n "core/" docs/superpowers/plans/2026-08-20-plan-q-quality-lane.md` returns only prose senses and record citations; the venv bootstrap line in Global Constraints reads from root.
- [ ] **Step 3:** Commit — `git commit -m "plan: Plan Q swept to post-flip paths"`

---

### Task 3: Acceptance + merge

- [ ] **Step 1:** Full suite green from root; `ruff check harness_core tests` at its 4 pre-existing findings; boundary greps: no `parents[1] / "core"` anywhere, no `core/` in living configs (`ls core` fails).
- [ ] **Step 2:** Merge per `superpowers:finishing-a-development-branch`, push in the same motion, report the SHA.

## Self-Review (at authoring)

- Templates ride inside `harness_core/` — package-data config is path-relative to the package and needs no edit.
- Mutation manifests don't exist yet (that's the point of the window); nothing re-baselines.
- The spec's quality-lane sentence and register entries that cite `core/` are living text — Task 2's sweep covers Plan Q; a final judged grep over `docs/superpowers/specs/` for `core/` path literals belongs in Task 3 Step 1.
- `hooks/hooks.json` carries `${CLAUDE_PLUGIN_ROOT}` command strings — verify at HEAD whether any embeds `core/` (Task 1 Step 2's grep covers `hooks/` wholesale).
