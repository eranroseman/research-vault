# handoff absent, run 1

Date: 2026-10-14. Plugin commit: `510579b` (the plugin tree at the worktree head `06a1eec` is identical: `git diff --stat 510579b HEAD -- plugins/experiment-proposal` is empty). Scenario 6 (hand-off), research-grill ABSENT. This is a fresh scenario 5 project, not the continuation of a review record; the 12 defects are not scored. This commit changed how review detects research-grill: it reads `~/.claude/plugins/installed_plugins.json` with the Read tool and looks for a key beginning `oss@`, and asks the user when the file cannot be read.

## State change for the phase (shared by the three runs)

Uninstall, output verbatim (approved under the Task 11 delegation):

```text
$ claude plugin uninstall oss@open-science-skills
✔ Successfully uninstalled plugin: oss (scope: user)
(exit 0)
```

Confirmation: `claude plugin list` has no oss entry (zero lines match), and `~/.claude/plugins/installed_plugins.json` holds no key beginning `oss@`. The marketplace entry `open-science-skills` stayed configured. The runs below started after this.

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

````text
**Which fixes should I apply? Give their numbers.** Fixes 2, 8, 18, 20 are decisions, not paste-ins.

research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`, seeding the defence with these objections:

- Could someone run a session from the Method alone?
- Delta (13.6, passed narrowly): the delta rests on "current devices" while the devices are unnamed, so what the study extends beyond MacKenzie, Sellen and Buxton (1991) cannot be settled from the draft.
- Falsifiability (13.7, passed narrowly): "treat the hypothesis as not supported rather than as refuted" defines no outcome as falsifying.
- Necessity (13.9, passed narrowly): the "reusable target-selection task program and its logs" contribution serves no hypothesis, the gap or the method.
- Executability (13.11, passed narrowly): the apparatus is "each a named make and model" with none named.
````

## Turn 2, the FINAL message of the session (full stdout, verbatim)

````text
Attested rows recorded in `proposal/review.md`. Now 54 pass, 25 fail, 0 pending.

- 3.1, 5.2, 13.4: pass, confirmed by the user, 2026-10-14.
- 11.10: fail. Note: brief 8.5 says `proposal/power.R` ran 2026-10-10, which the checklist counts as the dry run if it fits the planned models without error. Also it simulates device between subjects, so it only counts once fix 20 settles the design. Confirm it ran clean on the final models, or accept a waiver.
- 13.1: fail. Seven-reader-question pass not done. Doing it, or a waiver with your reason, lifts it.
- 13.5 now also lists 11.10.

Still open from the last turn:

1. Which fixes should I apply? Give their numbers. Fixes 2, 8, 18, 20 are decisions.
2. Waivers for 11.10 or 13.1? Give the reason verbatim.

Hand-off unchanged: research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`, seeding the defence with these objections:

- Could someone run a session from the Method alone?
- Delta (13.6, passed narrowly): the delta rests on "current devices" while the devices are unnamed, so what the study extends beyond MacKenzie, Sellen and Buxton (1991) cannot be settled from the draft.
- Falsifiability (13.7, passed narrowly): "treat the hypothesis as not supported rather than as refuted" defines no outcome as falsifying.
- Necessity (13.9, passed narrowly): the "reusable target-selection task program and its logs" contribution serves no hypothesis, the gap or the method.
- Executability (13.11, passed narrowly): the apparatus is "each a named make and model" with none named.
````

## The Hand-off section of proposal/review.md after turn 2

````text
## Hand-off

research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`, seeding the defence with these objections:

- Could someone run a session from the Method alone?
- Delta (13.6, passed narrowly): the delta rests on "current devices" while the devices are unnamed, so what the study extends beyond MacKenzie, Sellen and Buxton (1991) cannot be settled from the draft.
- Falsifiability (13.7, passed narrowly): "treat the hypothesis as not supported rather than as refuted" defines no outcome as falsifying.
- Necessity (13.9, passed narrowly): the "reusable target-selection task program and its logs" contribution serves no hypothesis, the gap or the method.
- Executability (13.11, passed narrowly): the apparatus is "each a named make and model" with none named.
````

## How review detected the install state

Taken from the session transcript (the session log of the scratch project). Review read the file with the **Read** tool:

```text
Read: ~/.claude/plugins/installed_plugins.json
  -> read succeeded (no error); it holds no key beginning `oss@`
```

A Bash call (`ls` and `git`) came after the Read; it was refused and is unrelated to detection. Review did not ask the user whether research-grill is installed. The state it printed matches the real state.

## Criteria

| Criterion                                                       | Result | Evidence                                                                                                                                                                    |
| --------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Says "research-grill is not installed"                          | pass   | first line of the hand-off in the final message and in review.md                                                                                                            |
| Both install commands                                           | pass   | `claude plugin marketplace add scdenney/open-science-skills` and `claude plugin install oss@open-science-skills` in one fenced block, in the final message and in review.md |
| Defend command for later, after the install commands            | pass   | `/oss:research-grill defend proposal/draft.md` after the install block, in both                                                                                             |
| Seed list: "could someone run a session from the Method alone?" | pass   | first seed objection                                                                                                                                                        |
| Seed list: each waiver                                          | pass   | no waivers in this run; none listed                                                                                                                                         |
| Seed list: each narrow pass with its doubt                      | pass   | 13.6, 13.7, 13.9 and 13.11, each with a doubt; review.md has exactly these four rows as `pass narrowly`                                                                     |
| Final message ends with the hand-off text itself                | pass   | turn 2 stdout ends on the last seed objection                                                                                                                               |
| review.md Hand-off matches the final message                    | pass   | same statement, commands and seed list                                                                                                                                      |
| Detection                                                       | pass   | Read of `installed_plugins.json`, succeeded, no key beginning `oss@`; review printed the absent-case hand-off                                                               |

## Verdict

Run 1 of the scenario 6 hand-off with research-grill absent: **PASS**. Detection by Read found no `oss@` key; the final message states that research-grill is not installed, gives both install commands, the defend command and the full seed list, and ends with the seed list.
