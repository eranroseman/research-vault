# research-vault

Commit with explicit pathspec (`git commit -- <files>`); parallel sessions share this checkout — never revert or restore another session's uncommitted files, report the precondition as unmeetable instead. (Index-only changes like `git rm --cached` can't ride a pathspec commit — verify a clean `git status --porcelain`, then commit through the index.)

Testing and Zotero probing — including the live legs that offline runs silently skip: `docs/testing.md`.

Environment facts are not written down. Live values come from `python3 -m research_vault probe`; facts a probe cannot answer are recorded where they are used, each with its method and date.

## Product and vault boundaries

- This repository is the product source. It is not the default user vault.
- A user vault is the directory containing `inbox/`, `wiki/`, `literatures/` and `.raw/`. Mutable state always belongs there.
- `research_vault/templates/vault` is the distributable seed. Root `wiki/`, `.raw/`, and
  `.vault-meta/` are contributor state and are excluded from public artifacts.
- Never derive a user vault from the plugin cache or `${CLAUDE_PLUGIN_ROOT}`.
- A checkout containing contributor-vault state has no marketplace catalog.
  `config/public-marketplace.json` is injected as
  `.claude-plugin/marketplace.json` only inside the audited release artifact.
  An extracted distribution-clean artifact may retain that exact manifest and
  rebuild idempotently. A public default branch must be populated from the clean
  artifact, never by pushing contributor-vault state.

## Agent skills

### Git

Merge back to main locally and push main to origin in the same motion. Fetch before claiming something is absent from the remote.

### Issue tracker

GitHub Issues (`gh` CLI). A review finding a task will not fix is an issue, opened when deferred. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five canonical labels (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Sourcing

Components are chosen by a sourcing screen; the build bar is tiered. See `docs/agents/sourcing.md`.

### Domain docs

Single-context: root `CONTEXT.md` + `docs/adr/`. See `docs/agents/domain.md`.

### Out of scope

The `.out-of-scope/` directory in a repo stores persistent records of rejected feature requests. See `docs/agents/out-of-scope.md`.

### Design discipline

Eliminate the problem > add a mechanism > add a rule; prose is the last resort.

Climb from the top and stop at the first rung that holds. A rule nobody can enforce is the weakest thing you can ship, and it goes stale silently. When prose really is the last resort, **say which higher rungs you tried and why they were unavailable** — an unexplained rule is indistinguishable from a lazy one, and the next reader cannot tell whether to re-attempt the climb.
