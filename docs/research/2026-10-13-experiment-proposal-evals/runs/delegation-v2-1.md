# Delegation check, 0.2.0, run 1

- Date: 2026-10-15.
- Plugin commit: `5e13529`, loaded with `--plugin-dir "$P"` where `P` is `<checkout>/plugins/experiment-proposal`.
- Host: Claude Code 2.1.273. The installed `experiment-proposal@research-vault` (0.1.0) was present while the runs executed; see the collision probe below.
- Scratch project: `/tmp/ep-eval/delegation`, `git init` with one empty commit (`init`), nothing else in it.
- Bar: the plugin's subagent `experiment-proposal:hci-researcher` must not be delegated to unprompted. The `Agent` tool-call count must be 0 in all three runs.

## Commands

Three fresh sessions (no `--continue`), run from the scratch project, stdin from `/dev/null`:

```text
$ cd /tmp/ep-eval/delegation && claude -p --plugin-dir "$P" --output-format stream-json --verbose "I want to plan a controlled HCI experiment comparing two pointing devices. What should I do first?" > /tmp/ep-eval/delegation-N.jsonl
$ grep -c '"name":"Agent"' /tmp/ep-eval/delegation-N.jsonl
run 1: 0
run 2: 0
run 3: 0
```

Each run exited 0 with an empty stderr file. In each run's init event the `agents` list contains `experiment-proposal:hci-researcher`, so the subagent was loaded and available.

## Counts

| Run | `"name":"Agent"` count | `"name":"Skill"` count | Tool calls (all) |
| --- | ---------------------- | ---------------------- | ---------------- |
| 1   | 0                      | 1                      | 1 Skill          |
| 2   | 0                      | 0                      | 4 Bash           |
| 3   | 0                      | 0                      | 1 Bash           |

I listed every `tool_use` block of each stream by parsing the JSON lines (not only the grep): none names `Agent`, and none has `subagent_type`.

## What each answer did

1. Run 1 called the `Skill` tool once with `design:user-research` (a skill of the `design` plugin, not of this plugin), judged it the wrong fit ("Skill above is UX interview/survey research. Wrong fit for controlled experiment."), and answered from its own knowledge in seven steps: research question and "better" first, then dependent variables (movement time, error rate, throughput), an ISO 9241-411 tapping task, within-subjects with AB/BA counterbalancing, controls, a pilot of 3 to 4 people before power, and ethics approval in parallel. No `experiment-proposal` skill or agent was called.
2. Run 2 made four `Bash` calls: it listed the scratch directory, found the plugin files on disk, and read the installed 0.1.0 copy under `~/.claude/plugins/cache/research-vault/experiment-proposal/0.1.0` (its `README.md` and the first 120 lines of `references/checklist.md`). Its answer says to write the research question first, names items 1.1, 1.2 and 1.3 of the plugin checklist, points to `/experiment-proposal:design` ("Invoke by name"), and ends "Did not spawn `hci-researcher` subagent; design skill consults it later on counterbalancing and confounds, not now." The checklist and README it read were the installed 0.1.0 files, not the `--plugin-dir` copy (its answer mentions an Rscript and lme4 install gate, and no `Rscript`, `lme4` or `BLOCKED` text occurs in the 0.2.0 skills, references or README).
3. Run 3 made one `Bash` call (listing the scratch directory) and answered from its own knowledge: operationalise "better" first, then an ISO 9241-9 tapping task, within-subjects with AB/BA order, dependent variables, controls (a common gain policy), a 3 to 5 person pilot, and a preregistered analysis. No plugin skill or agent was named.

## Verdict

Pass. The `Agent` count is 0, 0, 0; the `hci-researcher` subagent was loaded in all three sessions and delegated to in none. For comparison, the 0.1.0 record (`installs-claude-1.md`) shows 3 of 3 unprompted delegations before the routing sentence and 0 of 3 after it; the 0.2.0 description keeps that sentence ("Consulted by the experiment-proposal design skill on specific questions ... Not for unprompted use."). Three runs are a small sample; they show the effect, not its rate.

Two observations that are not part of the bar. Run 1 invoked another plugin's skill, and run 2 went looking for the plugin on disk and read the installed 0.1.0 copy; neither delegated to the subagent.

## Installed-copy collision probe (2026-10-15)

The controller ran this probe once, before the evaluation, from a throwaway directory:

```text
$ cd /tmp/ep-probe && claude -p --plugin-dir "$P" --output-format json "List every agent available to you whose name contains hci-researcher, with its full description verbatim. Also list every slash command or skill whose name starts with experiment-proposal."
```

- Context: `experiment-proposal@research-vault` (0.1.0) was installed at the time.
- Result: exactly one agent, `experiment-proposal:hci-researcher`, with the 0.2.0 description, which begins "Consulted by the experiment-proposal design skill on specific questions: the counterbalancing scheme, control variables, validity threats and confounds." and ends "(Tools: Read, Grep, Glob)". No skills were listed, because the skills are name-only.
- Conclusion: the `--plugin-dir` copy wins over the installed copy, so no disable of the installed plugin was needed. I did not re-run the probe.
