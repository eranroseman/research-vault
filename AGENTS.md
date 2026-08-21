# knowledge-harness — repository facts and policy

Meaning: `CONTEXT.md`. Naming: `docs/terminology.md` (identifiers §4.4 — check ids, probe ids, reason codes are governed; additions need a reference row). Behavior: `docs/specs/2026-08-16-foundation-spec.md`. Decisions: `docs/adr/`. Execution: `docs/plans/` — Codex executes, the author session rules; when plan and reality disagree, as-built HEAD governs and the commit message records the deviation.

## Multi-writer git discipline

Two clones (`~/knowledge-harness`, `~/New folder`) plus worktrees under `.worktrees/` write this repo. **Whoever merges to main pushes in the same motion** — an unpushed main merge is invisible state other writers fork around (twice on 2026-08-21). Fetch before claiming something is absent from origin. Worktree branches rebase onto origin main before merging.

## Repository rules

- `core/` admits dependencies case-by-case by **contract match** (spec §8; owners recorded in `docs/2026-08-21-lint-format-rethink.md`); the gate path imports light.
- **History rule**: `research/`, `analysis/`, completed plans, and accepted ADRs are records — content stands as written, and their internal paths stand with them. Living surfaces edit freely. Date-prefix = record, bare name = living surface; dated records file flat in `docs/`.
- Vault templates (`core/harness_core/templates/vault/`) are dialect surfaces owned by the render/scaffold contract; template text changes carry their test assertions.
- **Root namespace is the plugin loader's.** A new root file needs a tool that requires that exact path, plus a line here saying which (`.pre-commit-config.yaml` arrives with Plan Q's implementation, not before).
- Quality lane (arrives with Plan Q): one command locally == CI — `pre-commit run --all-files` from the activated venv.
