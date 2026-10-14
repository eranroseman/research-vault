# handoff grill, run 5

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
**Which fixes should I apply? Give their numbers.** Fixes 2, 18 (address part), 20 and 21 need your decision text. For any failure you will not fix, give a reason and I record a waiver.

Hand-off:

/oss:research-grill defend proposal/draft.md

Seed objections:

- Could someone run a session from the Method alone?
- Falsifiability (13.7, passed narrowly): under the draft's rule, no outcome refutes a hypothesis until the support, falsify or inconclusive rule is in the draft.
- Necessity (13.9, passed narrowly): the Fitts's law index of difficulty is defined but no hypothesis, design choice or analysis uses it.
- Executability (13.11, passed narrowly): the mouse and trackball are not named by make and model.
```

## Turn 2, the FINAL message of the session (full stdout, verbatim)

```text
Recorded. 3.1, 5.2, 13.4 pass, confirmed 2026-10-14. 11.10 and 13.1 fail; new decide fixes 23 (run the dry run of `proposal/power.R` on simulated data, then confirm) and 24 (review against the seven reader questions, then confirm). 13.5 now also cites 11.10.

Summary now: 79 checked, 54 pass, 25 fail, 2 defend-stage, 24 fixes, 0 waivers.

Which fixes should I apply? Give their numbers. Fixes 2, 18 (address), 20, 21, 23 and 24 need your decision or action. For any failure you will not fix, give a reason and I record a waiver.

Hand-off:

/oss:research-grill defend proposal/draft.md

Seed objections:

- Could someone run a session from the Method alone?
- Falsifiability (13.7, passed narrowly): under the draft's rule, no outcome refutes a hypothesis until the support, falsify or inconclusive rule is in the draft.
- Necessity (13.9, passed narrowly): the Fitts's law index of difficulty is defined but no hypothesis, design choice or analysis uses it.
- Executability (13.11, passed narrowly): the mouse and trackball are not named by make and model.
```

## The Hand-off section of proposal/review.md after turn 2

```text
## Hand-off

/oss:research-grill defend proposal/draft.md

Seed objections:

- Could someone run a session from the Method alone?
- Falsifiability (13.7, passed narrowly): under the draft's rule, no outcome refutes a hypothesis until the support, falsify or inconclusive rule is in the draft.
- Necessity (13.9, passed narrowly): the Fitts's law index of difficulty is defined but no hypothesis, design choice or analysis uses it.
- Executability (13.11, passed narrowly): the mouse and trackball are not named by make and model.
```

## How review detected the install state

Taken from the session transcript (the session log of the scratch project). Review read the file with the **Read** tool:

```text
Read: ~/.claude/plugins/installed_plugins.json
  -> read succeeded (no error); it holds the key `oss@open-science-skills`
```

A Bash call (`ls`) came after the Read and is unrelated to detection. Review did not ask the user whether research-grill is installed. The state it printed matches the real state.

## Criteria

| Criterion                                                       | Result | Evidence                                                                                                                                                               |
| --------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exact command `/oss:research-grill defend proposal/draft.md`    | pass   | "/oss:research-grill defend proposal/draft.md" on its own line under "Hand-off:" in the final message and in review.md (not wrapped in a code span; the text is exact) |
| No install commands                                             | pass   | none in the final message or review.md                                                                                                                                 |
| Seed list: each waiver                                          | pass   | no waivers in this run ("0 waivers"); none listed                                                                                                                      |
| Seed list: "could someone run a session from the Method alone?" | pass   | first seed objection                                                                                                                                                   |
| Seed list: each narrow pass with its doubt                      | pass   | 13.7, 13.9 and 13.11, each with a doubt; review.md has exactly these three rows as `pass narrowly`                                                                     |
| Final message ends with the hand-off text itself                | pass   | turn 2 stdout ends on the last seed objection                                                                                                                          |
| review.md Hand-off matches the final message                    | pass   | same command and seed list                                                                                                                                             |
| Detection                                                       | pass   | Read of `installed_plugins.json`, succeeded, key `oss@` present                                                                                                        |

## Verdict

Run 5 of the scenario 6 hand-off with research-grill present: **PASS**. Detection by Read, exact command, no install commands, the final message ends with the seed list.
