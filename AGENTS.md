# research-vault

Commit with explicit pathspec (`git commit -- <files>`); parallel sessions share this checkout — never revert or restore another session's uncommitted files, report the precondition as unmeetable instead. (Index-only changes like `git rm --cached` can't ride a pathspec commit — verify a clean `git status --porcelain`, then commit through the index.)

Testing and Zotero probing — including the live legs that offline runs silently skip: `docs/testing.md`.

Environment facts are not written down. Live values come from `python3 -m research_vault probe`; facts a probe cannot answer are recorded where they are used, each with its method and date.

## Agent skills

### Git

Merge back to main locally and push main to origin in the same motion. Fetch before claiming something is absent from the remote.

### Issue tracker

GitHub Issues (`gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five canonical labels (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: root `CONTEXT.md` + `docs/adr/`. See `docs/agents/domain.md`.

### Design discipline

Eliminate the problem > add a mechanism > add a rule; prose is the last resort.

Climb from the top and stop at the first rung that holds. A rule nobody can enforce is the weakest thing you can ship, and it goes stale silently. When prose really is the last resort, **say which higher rungs you tried and why they were unavailable** — an unexplained rule is indistinguishable from a lazy one, and the next reader cannot tell whether to re-attempt the climb.

### Task reports

The SDD skill never commits its `.superpowers/sdd/` reports, and its Finish step
deletes the workspace — a report is not a durable home. Reports name a
destination per Concern at write time; a plan's workspace closes only after
every Concern's disposition has landed in that home — an issue, a spec entry, or
a recorded decline.
