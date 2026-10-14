# handoff grill, run 4

Date: 2026-10-14. Plugin commit: `510579b` (the plugin tree at the worktree head `06a1eec` is identical: `git diff --stat 510579b HEAD -- plugins/experiment-proposal` is empty). Scenario 6 (hand-off), research-grill PRESENT. This is a fresh scenario 5 project, not the continuation of a review record; the 12 defects are not scored. This commit changed how review detects research-grill: it reads `~/.claude/plugins/installed_plugins.json` with the Read tool and looks for a key beginning `oss@`, and asks the user when the file cannot be read.

## State before the phase

`claude plugin list` (the oss entry), taken before the runs:

```text
  ❯ oss@open-science-skills
    Version: 2.35.1
    Scope: user
    Status: ✔ enabled
```

`~/.claude/plugins/installed_plugins.json` holds the key `oss@open-science-skills`.

## Commands

Setup (scratch project outside the repository, the scenario 5 fixtures committed):

```bash
tmp=$(mktemp -d) && cd "$tmp" && git init -q && git commit --allow-empty -qm init && mkdir proposal
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.brief.md proposal/design-brief.md
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.md proposal/draft.md
git add -A && git commit -qm fixtures
P=<checkout>/plugins/experiment-proposal
```

Turn 1 (prompt before `--allowedTools`; stdin from `/dev/null`):

```bash
claude -p "/experiment-proposal:review" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

Turn 2:

```bash
claude -p --continue "Confirm 3.1, 5.2 and 13.4; 11.10 and 13.1 not done." --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

Both turns exited 0. Turn 2 is the last turn; no further turn was run. Review did not ask whether research-grill is installed (its fallback question), so no answer was given. The defend command was not run. The three runs of this phase executed in parallel in three scratch projects.

## Turn 1, stdout from the batch question onward

```text
**Which fixes should I apply? Give their numbers.** Fixes 2, 8, 9 and 20 are decisions, not paste-ins. Fix 9 is the one that cascades. Failures you will not fix: say so and give a reason, I record a waiver.

Run `/oss:research-grill defend proposal/draft.md`.

Seed objections:

- Could someone run a session from the Method alone?
- Delta (item 13.6, passed narrowly): the third contribution, "a reusable target-selection task program and its logs", reads as a feature, and the "current devices" delta cites no current comparison.
- Necessity (item 13.9, passed narrowly): the index-of-difficulty formula serves no hypothesis or analysis in the draft.
- Executability (item 13.11, passed narrowly): the apparatus is "each a named make and model" with neither named.
```

## Turn 2, the FINAL message of the session (full stdout, verbatim)

```text
Recorded in `proposal/review.md`.

- 3.1, 5.2, 13.4: pass, confirmed by the user, 2026-10-14.
- 11.10: fail, dry run not done; `proposal/power.R` absent from `proposal/`. fix 23 (decide: run it, or waive).
- 13.1: fail, seven-reader-question review not done. fix 24 (decide: do it, or waive).
- 13.5 now lists 25 failing items (11.10 added).

Summary now: 79 checked. Pass 51. Fail 28. Not checked 2. Fixes 24. Waivers 0.

**Which fixes should I apply? Give their numbers.** Fixes 2, 8, 9, 20, 23, 24 are decisions. Fix 9 (device between vs within) cascades. Any failure you will not fix: give a reason, I record a waiver.

Run `/oss:research-grill defend proposal/draft.md`.

Seed objections:

- Could someone run a session from the Method alone?
- Delta (item 13.6, passed narrowly): the third contribution, "a reusable target-selection task program and its logs", reads as a feature, and the "current devices" delta cites no current comparison.
- Necessity (item 13.9, passed narrowly): the index-of-difficulty formula serves no hypothesis or analysis in the draft.
- Executability (item 13.11, passed narrowly): the apparatus is "each a named make and model" with neither named.
```

## The Hand-off section of proposal/review.md after turn 2

```text
## Hand-off

Run `/oss:research-grill defend proposal/draft.md`.

Seed objections:

- Could someone run a session from the Method alone?
- Delta (item 13.6, passed narrowly): the third contribution, "a reusable target-selection task program and its logs", reads as a feature, and the "current devices" delta cites no current comparison.
- Necessity (item 13.9, passed narrowly): the index-of-difficulty formula serves no hypothesis or analysis in the draft.
- Executability (item 13.11, passed narrowly): the apparatus is "each a named make and model" with neither named.
```

## How review detected the install state

Taken from the session transcript (the session log of the scratch project). Review read the file with the **Read** tool:

```text
Read: ~/.claude/plugins/installed_plugins.json
  -> read succeeded (no error); it holds the key `oss@open-science-skills`
```

A Bash call (`ls` and `git status` of the scratch project) came after the Read and is unrelated to detection. Review did not ask the user whether research-grill is installed. The state it printed matches the real state.

## Criteria

| Criterion                                                       | Result | Evidence                                                                                                                                                      |
| --------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exact command `/oss:research-grill defend proposal/draft.md`    | pass   | "Run `/oss:research-grill defend proposal/draft.md`." in the final message and in review.md; the command inside the code span is exact                        |
| No install commands                                             | pass   | neither the final message nor review.md has "not installed" or the two install commands                                                                       |
| Seed list: each waiver                                          | pass   | no waivers in this run (summary line says "Waivers 0"); none listed                                                                                           |
| Seed list: "could someone run a session from the Method alone?" | pass   | first seed objection                                                                                                                                          |
| Seed list: each narrow pass with its doubt                      | pass   | 13.6, 13.9 and 13.11, each with a doubt; review.md has exactly these three rows as `pass narrowly` (13.7 is a `fail` in this run, so it is not a narrow pass) |
| Final message ends with the hand-off text itself                | pass   | turn 2 stdout ends on the last seed objection; the command and the full seed list are printed                                                                 |
| review.md Hand-off matches the final message                    | pass   | same command and seed list                                                                                                                                    |
| Detection                                                       | pass   | Read of `installed_plugins.json`, succeeded, key `oss@` present                                                                                               |

## Verdict

Run 4 of the scenario 6 hand-off with research-grill present: **PASS**. Review read `installed_plugins.json` with the Read tool, printed the exact defend command with no install commands, and the final message ends with the seed list.
