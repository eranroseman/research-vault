# knowledge-harness

Meaning: `CONTEXT.md`. Naming: `docs/terminology.md`. Behavior: `docs/specs/2026-08-16-foundation-spec.md`. Decisions: `docs/adr/`. Plans: `docs/plans/` — as-built HEAD governs over plan text; deviations are recorded in commit messages.

**Git**: multiple writers (two clones, worktrees under `.worktrees/`). Whoever merges to main pushes in the same motion. Fetch before claiming something is absent from origin.

**History rule**: `research/`, `analysis/`, completed plans, and accepted ADRs are records — content and internal paths stand as written. Everything else edits freely.
