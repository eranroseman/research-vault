# research-vault

Commit with explicit pathspec (`git commit -- <files>`); parallel sessions share this checkout — never revert or restore another session's uncommitted files, report the precondition as unmeetable instead. (Index-only changes like `git rm --cached` can't ride a pathspec commit — verify a clean `git status --porcelain`, then commit through the index.)

Testing and Zotero probing — including the live legs that offline runs silently skip: `docs/agents/testing.md`.

Environment facts are not written down. Live values come from `python3 -m research_vault probe`; facts a probe cannot answer are recorded where they are used, each with its method and date.

## Product and vault boundaries

This repository is the product source and is read as a repository: vault rules and conventions — `CONTEXT.md`'s layout, the skills' gates, the vault's pre-commit hook — govern a user vault, not this tree.

- A user vault is the directory containing `inbox/`, `wiki/`, `literatures/` and `.raw/`. Mutable state always belongs there.
- `research_vault/templates/vault` is the distributable seed. Root `wiki/`, `.raw/`, and
  `.vault-meta/` are contributor state and are excluded from public artifacts.
- Never derive a user vault from the plugin cache or `${CLAUDE_PLUGIN_ROOT}`.
- The repository is its own marketplace: `.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json` are tracked here. A public default branch is
  populated from a distribution-clean artifact, never by pushing
  contributor-vault state.

## Agent skills

### Git

Merge back to main locally and push main to origin in the same motion. Fetch before claiming something is absent from the remote.

### Issue tracker

GitHub Issues (`gh` CLI). A review finding a task will not fix is an issue, opened when deferred. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five canonical labels (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Naming

How a name is chosen, and the governed spellings not owned by CONTEXT.md or an ADR. See `docs/agents/terminology.md`.

### Sourcing

Components are chosen by a sourcing screen; the build bar is tiered. See `docs/agents/sourcing.md`.

### Domain docs

Single-context: root `CONTEXT.md` + `docs/adr/`. See `docs/agents/domain.md`.

### Out of scope

The `.out-of-scope/` directory in a repo stores persistent records of rejected feature requests. See `docs/agents/out-of-scope.md`.

### Design discipline

Eliminate the problem > add a mechanism > add a rule; prose is the last resort.

Climb from the top and stop at the first rung that holds. A rule nobody can enforce is the weakest thing you can ship, and it goes stale silently. When prose really is the last resort, **say which higher rungs you tried and why they were unavailable** — an unexplained rule is indistinguishable from a lazy one, and the next reader cannot tell whether to re-attempt the climb.
