# Design: closing-keyword guard and eval run protocol

Date: 2026-10-25. Status: draft, awaiting review. Branch: `eval-run-protocol`. Size: small change; the short design.

## Intent

Two mechanisms from the retrospective of the 2026-10-24 cost-tuning session, landed first because they protect the next acceptance run. A commit message that says "close #N's item" closes issue N when main moves (three accidental or early closes among the seven closing-keyword commits in main's 1,803; #219 and #220 on 2026-10-24, #21 on an earlier branch). An eval run has no claim on its dispatch, its stray-file audit has been done by hand twice, and its agents have been labelled by guesswork once.

## Goals

- A closing keyword followed by an issue reference cannot reach `main` in a commit message; the check names the line and the rewording.
- One command, run after an eval run, reports each agent's role, model and tokens, and every file the run wrote outside its run root.
- A second dispatch against the same run root fails before it starts.

## Non-goals

- A git commit-msg hook: #130 settled that this repository installs no dev git hooks. The guard runs through pre-commit's pre-commit stage, which CI's required "Form + lint" step executes.
- An opt-in to close an issue from a commit: `docs/agents/issue-tracker.md` closes issues with `gh issue close <n> --comment`, and that stays the only route.
- Setting a subagent's working directory at dispatch: the Agent tool has no such parameter. #243 keeps that as the preferred fix for when a harness offers it; the ledger here is #243's post-run check.
- The contract-mutation ratchet, the stale-text review rule and the lint-scope fix: later projects.

## Anti-goals

- A guard that passes silently when `origin/main` is absent (a shallow checkout) — it must fail loud.
- A ledger that skips an agent whose transcript shape it does not understand — it reports the agent as unparsed, with the path.
- A dispatch claim that a second session can take over by touching a file.

## Constraints

- Commits by pathspec; fast-forward-only merges through the `quality` check. The quality job's checkout fetches one commit today; the guard needs history, so that job gains `fetch-depth: 0` (the mutation-gate job already has it).
- Transcripts live under `~/.claude/projects/<project-slug>/<session>/subagents/`, one `agent-<id>.jsonl` with an `agent-<id>.meta.json` beside it carrying `description`, `model`, `parentAgentId`, `agentType`. Token usage is `message.usage` on assistant records, as `mine_tokens.py` reads it today.
- `sources/` is git-ignored; the ledger reads a run root there and writes nothing into the repository.
- No home-directory literal in tracked files (`tests/test_current_state.py`).

## Approaches

Guard placement: (A1) a pre-commit-stage script scanning `origin/main..HEAD` messages, run by CI's existing "Form + lint" step — chosen; bites in CI only, since shared-checkout users run form owners directly, and nothing reaches `main` unchecked. (A2) a separate CI step reading the same range — same coverage, a second mechanism beside pre-commit, breaking AGENTS.md's one-command promise. A commit-msg hook — ruled out by #130.

Ledger shape: (B1) one script, `run_ledger.py`, replacing `mine_tokens.py`: roles, tokens, stray files — chosen, one file to maintain and the concrete form of #243's gate. (B2) keep `mine_tokens.py` and add an audit script — same parsing, two argument sets.

Dispatch claim: `mkdir` is the one sensible way; `touch` cannot claim.

## Decided

- `scripts/closing_keywords.py`: fails (exit 1) on any commit message in `origin/main..HEAD` matching a closing keyword (`close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved`) followed by an issue reference — `#N`, `#N's`, a colon form, `owner/repo#N`; prints the commit, the line, and "write `see #N` or `#N's item`". Exits 2 with a message if `origin/main` does not resolve. Conventional-commit types (`fix(skills):`) do not match: no `#` follows them. Tests use the three real messages that caused closes (81cd392, 71dc2ea, dbe85ec) and a control set.
- `.pre-commit-config.yaml` gains the hook at the pre-commit stage; `quality.yml`'s quality job gains `fetch-depth: 0`.
- `docs/research/2026-09-20-paper-critical-analysis-evals/run_ledger.py` replaces `mine_tokens.py` (git mv, history kept). Given a runner transcript path it walks `parentAgentId` links to find its subagents, prints one row per agent — role from `meta.json`'s `description`, model, fresh in (input + cache-write), cache read, output — and a total. With `--run-root <dir> --since <stamp-path>` it also lists, per agent, every path a tool call wrote, changed into, or redirected to that is outside the run root, read from the transcript's tool-use records (Write and Edit file paths; Bash commands' `cd`, `-o`, `>` and `>>` targets). An agent whose records it cannot parse is listed as unparsed with its path, never dropped. Stdlib only.
- Dispatch claim: the run protocol says `mkdir <run-root>/dispatch.stamp` at dispatch, dispatch only when it succeeds; the directory's mtime serves `find -newer`. The 2026-10-24 plan's `touch` wording is superseded.
- The evals README gains a short "Run protocol" section: claim by `mkdir`; dispatch from the session whose user approved the spend, never on relayed approval; after the run, `run_ledger.py` for roles, tokens and stray files; roles are read from `meta.json`, never inferred from timing.
- Comment on #243 pointing at the ledger as its post-run check.

## Left to the builder

The exact regex and its tests; the transcript tool-use record shape for Bash, Write and Edit (read one real transcript to pin it, and test against a fixture cut from one); whether `--since` reads the stamp's mtime or an ISO time; table formatting.
