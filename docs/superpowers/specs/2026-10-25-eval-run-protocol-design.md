# Design: closing-keyword guard, eval run protocol, and landing a branch

Date: 2026-10-25. Status: draft, awaiting review. Branch: `eval-run-protocol`. Size: small change; the short design.

## Intent

Three mechanisms from the retrospectives of the 2026-10-24 cost-tuning session, landed first because they protect the next acceptance run and the next branch. A commit message that says "close #N's item" closes issue N when main moves (three accidental or early closes among the seven closing-keyword commits in main's 1,803; #219 and #220 on 2026-10-24, #21 on an earlier branch). An eval run has no claim on its dispatch, its stray-file audit has been done by hand twice, and its agents have been labelled by guesswork once. AGENTS.md's merge recipe needs `git checkout main`, which fails in a worktree and moves every session's branch in the shared checkout, so two sessions improvised the ref-push form on the same day; its commit form `git commit -- <files>` invites `-m` after the `--`, which git reads as a pathspec (eight plan commands and one real commit tripped on it).

## Goals

- A closing keyword followed by an issue reference cannot reach `main` in a commit message; the check names the line and the rewording.
- One command, run after an eval run, reports each agent's role, model and tokens, and every file the run wrote outside its run root.
- A second dispatch against the same run root fails before it starts.
- One command lands a green branch on `main` from its worktree; AGENTS.md shows the commit, worktree and landing forms that work from a worktree.

## Non-goals

- A git commit-msg hook: #130 settled that this repository installs no dev git hooks. The guard runs through pre-commit's pre-commit stage, which CI's required "Form + lint" step executes.
- An opt-in to close an issue from a commit: `docs/agents/issue-tracker.md` closes issues with `gh issue close <n> --comment`, and that stays the only route.
- Setting a subagent's working directory at dispatch: the Agent tool has no such parameter. #243 keeps that as the preferred fix for when a harness offers it; the ledger here is #243's post-run check.
- The contract-mutation ratchet, the stale-text review rule and the lint-scope fix: later projects.

## Anti-goals

- A guard that passes silently when `origin/main` is absent (a shallow checkout) — it must fail loud.
- A ledger that skips an agent whose transcript shape it does not understand — it reports the agent as unparsed, with the path.
- A dispatch claim that a second session can take over by touching a file.
- A landing command that pushes when the branch's check is red, missing, or ran on a different sha.

## Constraints

- Commits by pathspec; fast-forward-only merges through the `quality` check. The quality job's checkout fetches one commit today; the guard needs history, so that job gains `fetch-depth: 0` (the mutation-gate job already has it).
- Transcripts live under `~/.claude/projects/<project-slug>/<session>/subagents/`, one `agent-<id>.jsonl` with an `agent-<id>.meta.json` beside it carrying `description`, `model`, `parentAgentId`, `agentType`. Token usage is `message.usage` on assistant records, as `mine_tokens.py` reads it today.
- `sources/` is git-ignored; the ledger reads a run root there and writes nothing into the repository.
- No home-directory literal in tracked files (`tests/test_current_state.py`).
- `main` accepts fast-forwards only, after the `quality` check; `gh` is authenticated on this machine. `scripts/` is already in ruff's and mypy's path lists, so both new scripts are linted and typed without a config change.

## Approaches

Guard placement: (A1) a pre-commit-stage script scanning `origin/main..HEAD` messages, run by CI's existing "Form + lint" step — chosen; bites in CI only, since shared-checkout users run form owners directly, and nothing reaches `main` unchecked. (A2) a separate CI step reading the same range — same coverage, a second mechanism beside pre-commit, breaking AGENTS.md's one-command promise. A commit-msg hook — ruled out by #130.

Ledger shape: (B1) one script, `run_ledger.py`, replacing `mine_tokens.py`: roles, tokens, stray files — chosen, one file to maintain and the concrete form of #243's gate. (B2) keep `mine_tokens.py` and add an audit script — same parsing, two argument sets.

Dispatch claim: `mkdir` is the one sensible way; `touch` cannot claim.

Landing a branch: (C1) `scripts/land.py <branch>`, one command that waits for green and fast-forwards `main` by ref push — chosen; the recipe was retyped by two sessions in one day, and a script cannot be misread. (C2) rewrite the prose recipe in AGENTS.md only — cheaper, but a recipe drifts and each reader re-derives the worktree-safe form. The commit-form and worktree-first lines stay prose: a git hook is out by #130, and no checker sees flag order or where a file was first written.

## Decided

- `scripts/closing_keywords.py`: fails (exit 1) on any commit message in `origin/main..HEAD` matching a closing keyword (`close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved`) followed by an issue reference — `#N`, `#N's`, a colon form, `owner/repo#N`; prints the commit, the line, and "write `see #N` or `#N's item`". Exits 2 with a message if `origin/main` does not resolve. Conventional-commit types (`fix(skills):`) do not match: no `#` follows them. Tests use the three real messages that caused closes (81cd392, 71dc2ea, dbe85ec) and a control set.
- `.pre-commit-config.yaml` gains the hook at the pre-commit stage; `quality.yml`'s quality job gains `fetch-depth: 0`.
- `docs/research/2026-09-20-paper-critical-analysis-evals/run_ledger.py` replaces `mine_tokens.py` (git mv, history kept). Given a runner transcript path it walks `parentAgentId` links to find its subagents, prints one row per agent — role from `meta.json`'s `description`, model, fresh in (input + cache-write), cache read, output — and a total. With `--run-root <dir> --since <stamp-path>` it also lists, per agent, every path a tool call wrote, changed into, or redirected to that is outside the run root, read from the transcript's tool-use records (Write and Edit file paths; Bash commands' `cd`, `-o`, `>` and `>>` targets). An agent whose records it cannot parse is listed as unparsed with its path, never dropped. Stdlib only.
- Dispatch claim: the run protocol says `mkdir <run-root>/dispatch.stamp` at dispatch, dispatch only when it succeeds; the directory's mtime serves `find -newer`. The 2026-10-24 plan's `touch` wording is superseded.
- The evals README gains a short "Run protocol" section: claim by `mkdir`; dispatch from the session whose user approved the spend, never on relayed approval; after the run, `run_ledger.py` for roles, tokens and stray files; roles are read from `meta.json`, never inferred from timing.
- Comment on #243 pointing at the ledger as its post-run check.
- `scripts/land.py <branch>`: `git fetch origin`; resolve the branch head on origin; find the `quality` run for exactly that sha (`gh run list --commit <sha> --workflow quality`), waiting while it is queued or in progress, exiting 1 with the run URL if it is red or absent after a bounded wait; then `git push origin <branch>:main`; then `git -C <shared checkout> pull --ff-only origin main`, reporting rather than failing if that pull is refused by another session's uncommitted work. A non-fast-forward push refusal prints the rebase instruction and exits 1. Stdlib plus `git` and `gh` subprocesses.
- AGENTS.md: the commit line becomes `git commit -m "<message>" -- <files>` with the reason (after `--`, every word is a pathspec); the Git section becomes: create the branch worktree before writing the first file, the shared checkout stays on `main`; push the branch; land it with `python scripts/land.py <branch>`; a branch behind `main` cannot fast-forward — rebase, push, land again; fetch before claiming something is absent from the remote.

## Drive-bys on the same branch

Two one-line edits to `docs/research/2026-09-20-paper-critical-analysis-evals/README.md`, outside the design but riding the branch: the 2026-10-24 A/B entry gains the like-for-like pair rating of the 2026-10-04 report (same prompt, fresh Opus rater, 2026-10-25: overall 8, verifiability 7, calibration 7, 17 trust-lowering items, against the new report's 8, 8, 7 and 12; return saved beside that run), and the 2026-10-04 Results paragraph's wrapped line "+ 51 checks on Bloom…" is rejoined so "283 + 32 + 51 checks" reads as one figure instead of a stray bullet.

## Left to the builder

The exact regex and its tests; the transcript tool-use record shape for Bash, Write and Edit (read one real transcript to pin it, and test against a fixture cut from one); whether `--since` reads the stamp's mtime or an ISO time; table formatting; how `land.py` is tested without a network (a fake `git` and `gh` on `PATH` in a subprocess test, or an injected runner), and its wait bound.
