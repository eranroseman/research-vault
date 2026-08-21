# knowledge-harness — repository facts and policy

Meaning layer: `CONTEXT.md` (glossary). Naming governance: `docs/terminology.md`. Behavior contract: `docs/specs/2026-08-16-foundation-spec.md`. Decisions: `docs/adr/`. Plans: `docs/plans/` (executed by Codex under subagent-driven development; the author session issues rulings — when a plan and reality disagree, as-built HEAD governs and the deviation is recorded in the commit message).

## Multi-writer git discipline

Two clones of this repo exist on this machine (`~/knowledge-harness`, `~/New folder`) plus per-plan worktrees under `.worktrees/`. The rule that prevents forked history: **whoever merges to main pushes immediately** — an unpushed main merge is invisible state every other writer forks around (it happened twice on 2026-08-21). Corollaries: fetch before claiming something is absent from origin; never rewrite pushed history; worktrees rebase onto origin main before their merge.

## Repository rules

- `core/` is stdlib-shaped by discipline, not dogma: dependencies are admitted case-by-case by contract match (spec §8; `docs/2026-08-21-lint-format-rethink.md` records the format/lint owners). Nothing heavy imports on the gate path.
- The history rule: living surfaces may be edited; `research/`, `analysis/`, completed plans, and accepted ADRs are records — content is never rewritten (form was canonicalized once; see `.git-blame-ignore-revs` when it lands).
- Vault templates (`core/harness_core/templates/vault/`) are dialect surfaces owned by the render/scaffold contract — no external formatter touches them; template text changes carry their test assertions.
- Check ids, probe ids, and reason codes are governed identifiers (`docs/terminology.md` §4.4); additions require a reference row.
- Quality lane (post-Plan-Q): one command locally == CI — `source core/.venv/bin/activate && pre-commit run --all-files`.
- Caller-less entry points are guarded by config/tests, never convention: `marketplace add` rests on validity-tested manifests; bare `pytest` from `core/` equals `python -m pytest` once Plan Q pins `pythonpath`; the one-command lane line above is explicitly post-Plan-Q until its implementation lands.
- **Root namespace belongs to the plugin loader.** Add root files only where a tool requires that exact path, and name each here: `LICENSE` (matches plugin.json's MIT declaration), `.gitignore`, `.git-blame-ignore-revs` (canonical-form churn commits), `.pre-commit-config.yaml` (lands WITH Plan Q's implementation, not before), `.vscode/` (IDE alignment, Plan Q). The plugin payload ships the whole repo pre-alpha; the split is a recorded release gate (spec §10).
