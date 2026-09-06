# research-vault

Disposition: current (2026-09-06)

Merge back to main locally and push main to origin in the same motion. Fetch before claiming something is absent from origin.

Eliminate the problem > add a mechanism > add a rule; prose is the last resort.

Commit with explicit pathspec (`git commit -- <files>`); parallel sessions share this checkout — never revert or restore another session's uncommitted files, report the precondition as unmeetable instead. (Index-only changes like `git rm --cached` can't ride a pathspec commit — verify a clean `git status --porcelain`, then commit through the index.)

Testing and Zotero probing — including the live legs that offline runs silently skip: `docs/testing.md`.

Environment facts are not written down. Live values come from `python3 -m research_vault probe`; facts a probe cannot answer are recorded where they are used, each with its method and date.

A new Markdown file needs a `Disposition:` line — one paragraph under its first heading, or at the top when it has none. Vocabulary: `current`, `pending-map`, `historical`, `pending-issue: <number>`, `superseded-by: <path>`, `sibling-project`, plus an optional ` [should-be-scoping-review]`. `tests/test_dispositions.py` enforces it and names the file that is missing one. Nothing under `skills/`, `research_vault/templates/` or `.out-of-scope/` is in scope — those ship to a consumer, and the marker is bookkeeping about this repository. `scripts/dispositions.py propose` writes a reviewable TSV; nothing writes a marker except `apply` from a TSV you have read.

## Agent skills

### Issue tracker

GitHub Issues (`gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five canonical labels (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: root `CONTEXT.md` + `docs/adr/`. See `docs/agents/domain.md`.
