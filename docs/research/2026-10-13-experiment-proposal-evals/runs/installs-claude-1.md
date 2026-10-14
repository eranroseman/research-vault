# Scenario 7, Claude Code install test, run 1

- Date: 2026-10-14.
- Plugin commit: `2222256` (branch `experiment-proposal-plugin` at install time). A later commit on the branch (`4bf2597`) changed only a plan document; nothing under `plugins/` changed.
- Host: Claude Code 2.1.273. Installed from the branch's checkout (`<checkout>`) by local path, not from git, and without `--plugin-dir`.
- Scratch projects: two fresh `mktemp -d` directories outside the repository (`<scratch>`; the first held the three name-only runs, the second the review and subagent runs), each `git init` with an empty commit and `proposal/`. The scenario 5 fixtures were committed in the second scratch project before the review run.

## Install

Before: `claude plugin marketplace list` showed ten marketplaces (`claude-code-plugins`, `ponytail`, `claude-plugins-official`, `caveman`, `obsidian-skills`, `jrjsmrtn-skills`, `openai-codex`, `eranroseman`, `agricidaniel-claude-obsidian`, `typesafe-ai`); none named `research-vault`, so nothing was removed first.

```text
$ claude plugin marketplace add "<checkout>"
Adding marketplace…✔ Successfully added marketplace: research-vault (declared in user settings)
$ claude plugin install experiment-proposal@research-vault
Installing plugin "experiment-proposal@research-vault"...✔ Successfully installed plugin: experiment-proposal@research-vault (scope: user)
$ claude plugin list
  ❯ experiment-proposal@research-vault
    Version: 0.1.0
    Scope: user
    Status: ✔ enabled
$ claude plugin details experiment-proposal@research-vault
  Skills (4)  design, lit-search, review, the-ethics-board
  Agents (1)  hci-researcher
  Hooks (0)
```

The session's init event lists the install at `plugins[].path` = the checkout's `plugins/experiment-proposal` folder, so for a local-path marketplace `${CLAUDE_PLUGIN_ROOT}` is the checkout itself. The from-git form (`claude plugin marketplace add https://github.com/eranroseman/research-vault.git#experiment-proposal-plugin`) was not tried: the branch is not pushed. Deferred to after Task 12's first push.

## Session checks

### Names

```text
$ claude -p --output-format text "Name exactly, one per line, every skill and every agent you have whose name starts with experiment-proposal. Do not run any of them."
experiment-proposal:hci-researcher
```

Only the agent came back. The four skills are name-only (`disable-model-invocation: true`), so the model's own skill list leaves them out. The session init event (`--output-format stream-json --verbose`), in all three name-only runs below, lists the four skills and the agent:

```text
slash_commands / skills: ... 'experiment-proposal:design', 'experiment-proposal:lit-search', 'experiment-proposal:review', 'experiment-proposal:the-ethics-board' ...
agents: ... 'experiment-proposal:hci-researcher' ...
```

The brief's expected output (all five names from the prompt) is therefore not met literally; the five namespaced names are all present in the session's registry.

### Name-only invocation, three runs

```text
$ claude -p --output-format stream-json --verbose "I want to plan a controlled HCI experiment comparing two pointing devices. What should I do first?" > name-only.jsonl
$ grep -c '"name":"Skill"' name-only.jsonl
run 1: 0
run 2: 1
run 3: 0
```

Run 2's one match: `{"name":"Skill","input":{"skill":"experiment-proposal:hci-researcher",...}}`, answered by `Unknown skill: experiment-proposal:hci-researcher`. It names the agent, not a skill; none of the four skills was invoked in any run. In all three runs the model then delegated to the agent unprompted (`Agent` tool call with `subagent_type` `experiment-proposal:hci-researcher`), as the spec's open risk anticipated.

### `/experiment-proposal:review`, no brief

```text
$ claude -p --output-format text "/experiment-proposal:review"
```

Four runs. First (in the first, cluttered scratch directory, stdin not redirected): `Skill reserved for direct user invocation. Run `/experiment-proposal:review` yourself in Claude Code CLI or web app.` Re-run in the second scratch project with `</dev/null`, three times (two text, one stream-json):

```text
No design brief at `proposal/design-brief.md`. Run `/experiment-proposal:design` first.
No design brief at proposal/design-brief.md; run /experiment-proposal:design first.
No design brief at `proposal/design-brief.md`; run `/experiment-proposal:design` first.
```

The stream-json run shows the skill body loaded ("Reading brief, draft, and checklist.") and then the stop message after the model found no brief. The first-run message is a flake I could not reproduce; recorded, not explained.

### `/experiment-proposal:review` with the scenario 5 fixtures

Fixtures copied in (`proposal-with-defects.brief.md` as `proposal/design-brief.md`, `proposal-with-defects.md` as `proposal/draft.md`) and committed in the scratch project.

```text
$ claude -p --output-format text --permission-mode acceptEdits --allowedTools "Read,Write,Edit" "/experiment-proposal:review"
Error: Input must be provided either through stdin or as a prompt argument when using --print
```

`--allowedTools` is variadic and swallowed the prompt. Closest form, once, prompt first and the flag last:

```text
$ claude -p --output-format text --permission-mode acceptEdits "/experiment-proposal:review" --allowedTools "Read,Write,Edit"
Before writing the review file, I need to confirm four attested items with you: ... 3.1 ... 5.2 ... 11.10 ... 13.1 ... 13.4
```

(The reply says "four" and lists five items; its wording is quoted as printed.) The skill asks the attested items in one batch before it writes (its own rule), so a headless single turn writes nothing. Second turn with `--continue`, a deviation from the brief: `"I cannot answer the attested items in this headless session. Mark all five attested items as unconfirmed, do not ask again, and write proposal/review.md now."` Result: `Review written at proposal/review.md.` with a question about the device factor (within versus between subjects) and 18 numbered fixes. No fix was applied (`git status --porcelain`: only `?? proposal/review.md`).

Decisive lines of `proposal/review.md`:

```text
Checklist: experiment-proposal 0.1.0
- **1.1** pass: "We will compare movement time and error rate with a mouse and a trackball when right-handed young adults select targets at three distances and three sizes on a desktop display." (Introduction, para 1)
- **11.10** unconfirmed: dry-run of analysis script on simulated data; user could not confirm in headless session.
```

The quoted sentence occurs verbatim in `proposal/draft.md` (1 match). Item IDs, their wording and the attested list (3.1, 5.2, 11.10, 13.1, 13.4) can come only from the checklist file, so `${CLAUDE_PLUGIN_ROOT}/references/checklist.md` resolved. (This is a local-path install; the from-git install is the same check, deferred.)

### Subagent

```text
$ claude -p "Ask the experiment-proposal:hci-researcher agent, in one sentence, which random-effects structure a two-level within-subjects pointing study needs, and quote its answer." --allowedTools "Agent"
Agent answer: "For a two-level within-subjects pointing study, use a random-effects structure with random intercepts for participants and random slopes for condition: `(1 + condition | participant)`, ..."
```

A stream-json repeat shows the call `{"name":"Agent","input":{"subagent_type":"experiment-proposal:hci-researcher",...}}` and the answer relayed as "Agent says: ...".

## Verdicts, pass-bar clauses

| Clause                        | Verdict                                                                                                                                                                                                                                   |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Namespaced names              | Pass on the registry (all four skills and the agent under `experiment-proposal:`); the literal prompt returns only the agent, because name-only skills are hidden from the model's list. Expected output as written in the brief not met. |
| Name-only invocation (3 runs) | Fail on the strict bar: counts 0, 1, 0. No plugin skill was invoked in any run; the one `Skill` call named the agent and failed. The agent was delegated to unprompted in 3 of 3 runs.                                                    |
| Subagent available            | Pass. `experiment-proposal:hci-researcher` is in the session registry and answered through the `Agent` tool.                                                                                                                              |
| Checklist path resolving      | Pass (local-path install): `review` read the checklist and its rows quote the draft (row 1.1) and cite checklist IDs.                                                                                                                     |

## Cleanup

```text
$ claude plugin uninstall experiment-proposal@research-vault
✔ Successfully uninstalled plugin: experiment-proposal (scope: user)
$ claude plugin marketplace remove research-vault
✔ Successfully removed marketplace: research-vault
```

Removed: the plugin and the `research-vault` marketplace, both added by this test. Left behind: Claude Code's own cache folder `~/.claude/plugins/cache/research-vault/` holding an orphan-marked copy (`.orphaned_at`), which Claude Code garbage-collects itself. Final `claude plugin marketplace list`: the same ten marketplaces as before the test, no `research-vault`; `claude plugin list` shows no `experiment-proposal`.
