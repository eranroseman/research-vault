# Package Rename: `harness_core` → `knowledge_harness` — Task

> Single-task contract (Plan-L pattern: pure moves and path strings, zero behavior change). Ruled 2026-08-22: the package mirrors the distribution/plugin name (`knowledge-harness`) per the standard PyPI convention; "core" named a directory the layout flip deleted; and `AGENT_ACTOR` is written into vault verified-events forever — no vault exists yet, so the rename is free exactly now. Land before Plan Q executes. As-built HEAD governs.

**Worktree** via `superpowers:using-git-worktrees`, branch `build/package-rename`; merge + push in the same motion.

## Changes

1. `git mv harness_core knowledge_harness`.
2. **pyproject.toml**: `name = "knowledge-harness"`; `packages.find` include, package-data key, `[tool.mypy] files`, and the ruff per-file-ignores key (`"harness_core/__main__.py"`) all follow.
3. **Import/reference sweep** (mechanical, judged): `from harness_core`/`import harness_core` across `tests/` and `hooks/`; `patch("harness_core.…")` strings in tests; `python -m harness_core` invocations wherever they exist at HEAD (pre-commit template, CI templates — judged grep decides the actual set); the `__init__` docstring.
4. **`AGENT_ACTOR`** becomes `knowledge_harness/{version}` — update the events/actor test assertions with it (the durable-surface point of doing this now).
5. **Plan Q authored-text sweep** (free edit, L-Task-2 pattern): every `harness_core` path in `docs/superpowers/plans/2026-08-20-plan-q-quality-lane.md` — workflow steps, pre-commit hook entries, mdformat/crap4py/drywall/mutate4py invocations, the gate-script sketch. Self-check: `grep -n "harness_core"` there returns nothing.
6. Living docs referencing the package by path (`CONTEXT.md`? spec quality-lane lines? — judged grep over living surfaces only). Records keep the old name (history rule).
7. The vault-template task (`2026-08-22-vault-agents-template-revision.md`) reads its file path per HEAD — whichever of the two tasks lands second adapts, per as-built-HEAD-governs.

## Acceptance

- Rebuilt venv, `pip install -e ".[dev]"`, `python -m pytest tests -q`: exact baseline (865 passed / 6 skipped at authoring).
- `python -m knowledge_harness --help` exits 0; hooks re-verified under `python3 -I` (the Plan-L reviewer's check — the suite alone can't prove the sys.path injection).
- Judged greps: `harness_core` absent from living surfaces (code, configs, active plans); present only in records.
- One commit; merge + push in the same motion; report the SHA.
