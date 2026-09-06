# research-vault

Disposition: current (2026-09-06)

Commit with explicit pathspec (`git commit -- <files>`); parallel sessions share this checkout — never revert or restore another session's uncommitted files, report the precondition as unmeetable instead. (Index-only changes like `git rm --cached` can't ride a pathspec commit — verify a clean `git status --porcelain`, then commit through the index.)

Testing and Zotero probing — including the live legs that offline runs silently skip: `docs/testing.md`.

Environment facts are not written down. Live values come from `python3 -m research_vault probe`; facts a probe cannot answer are recorded where they are used, each with its method and date.

A new Markdown file needs a `Disposition:` line — one paragraph under its first heading, or at the top when it has none. Vocabulary: `current`, `pending-map`, `historical`, `pending-issue: <number>`, `superseded-by: <path>`, `sibling-project`, plus an optional ` [should-be-scoping-review]`. `tests/test_dispositions.py` enforces it and names the file that is missing one. Nothing under `skills/`, `research_vault/templates/` or `.out-of-scope/` is in scope — those ship to a consumer, and the marker is bookkeeping about this repository. `scripts/dispositions.py propose` writes a reviewable TSV; nothing writes a marker except `apply` from a TSV you have read.

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
