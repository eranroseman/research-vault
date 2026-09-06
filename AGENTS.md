# research-vault

Disposition: current (2026-09-06)

Merge back to main locally and push main to origin in the same motion. Fetch before claiming something is absent from origin.

Eliminate the problem > add a mechanism > add a rule; prose is the last resort.

Commit with explicit pathspec (`git commit -- <files>`); parallel sessions share this checkout — never revert or restore another session's uncommitted files, report the precondition as unmeetable instead. (Index-only changes like `git rm --cached` can't ride a pathspec commit — verify a clean `git status --porcelain`, then commit through the index.)

Testing and Zotero probing — including the live legs that offline runs silently skip: `docs/testing.md`.

Environment facts are not written down. Live values come from `python3 -m research_vault probe`; facts a probe cannot answer are recorded where they are used, each with its method and date.

## Agent skills

### Issue tracker

GitHub Issues (`gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five canonical labels (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: root `CONTEXT.md` + `docs/adr/`. See `docs/agents/domain.md`.
