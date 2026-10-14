# handoff absent, run 2

Date: 2026-10-14. Plugin commit: `510579b` (the plugin tree at the worktree head `06a1eec` is identical: `git diff --stat 510579b HEAD -- plugins/experiment-proposal` is empty). Scenario 6 (hand-off), research-grill ABSENT. This is a fresh scenario 5 project, not the continuation of a review record; the 12 defects are not scored. This commit changed how review detects research-grill: it reads `~/.claude/plugins/installed_plugins.json` with the Read tool and looks for a key beginning `oss@`, and asks the user when the file cannot be read.

See `runs/handoff-absent-1.md` for the uninstall output and the confirmation; the state is unchanged for this run.

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
**Which fixes should I apply? Give their numbers.** Fixes 2, 19 and 21 are decisions, not paste text.

**Hand-off**

research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`.

Seed objections for the defend stage:

- Could someone run a session from the Method alone? The devices are placeholders ("each a named make and model"), and the Procedure never names the program or display.
- Delta (13.6, pass narrowly): which prior finding would the result confirm or refute, the 1991 size-dependent gap or the narrowing suggested by Casiez and Roussel (2011)? Is "a reusable target-selection task program" a contribution or a feature?
- Necessity (13.9, pass narrowly): the index-of-difficulty formula is stated but never used; what does it do for the argument?
- Method fit (13.10, pass narrowly): the power analysis assumed an lmer, the Planned analysis runs a paired t-test and a repeated-measures ANOVA; which method answers H1, and does 24 still give 80% power for it?
- Executability (13.11, pass narrowly): which mouse and which trackball, and does the choice of a current trackball bear on the "current devices" gap?
- Design (brief 7.1 vs draft): the brief says device between subjects because mouse habits transfer asymmetrically; the draft says within because skill variance swamps the device effect. Which argument wins, and what does it do to the session length and the per-group count?
- Scale (brief 6.6 vs 11.4): the smallest effect sizes of interest are in milliseconds, the model is on log movement time; on which scale is 100 ms judged?
- Data minimization: the screening form at sign-up and the demographic questionnaire after the tasks both collect age and handedness; why twice?
````

## Turn 2, the FINAL message of the session (full stdout, verbatim)

````text
Attested rows recorded in `proposal/review.md`.

- **3.1, 5.2, 13.4** pass: confirmed by the user, 2026-10-14.
- **11.10** fail: dry run of `proposal/power.R` not done. Passes once run without error and confirmed, or needs waiver.
- **13.1** fail: seven-reader-question review not done. Passes once done and confirmed, or needs waiver.

Summary now: 79 checked. Pass 50. Fail 29. Defend-stage 2. Fixes proposed 21. Waivers 0.

Draft still untouched. Two things needed from you:

1. **Which fixes should I apply? Give their numbers.** Fixes 2, 19 and 21 are decisions, not paste text. Fix 15 waits on fix 19.
2. **11.10 and 13.1:** run the dry run and the reader review and tell me, or give a reason to waive each.

Hand-off unchanged: research-grill is not installed.

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`. Seed list as in the file: Method-alone runnability; Delta, Necessity, Method fit, Executability doubts; device between vs within; SESOI scale vs log model; age and handedness collected twice.
````

## The Hand-off section of proposal/review.md after turn 2

````text
## Hand-off

research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`.

Seed objections for the defend stage:

- Could someone run a session from the Method alone? The devices are placeholders ("each a named make and model"), and the Procedure never names the program or display.
- Delta (13.6, pass narrowly): which prior finding would the result confirm or refute, the 1991 size-dependent gap or the narrowing suggested by Casiez and Roussel (2011)? Is "a reusable target-selection task program" a contribution or a feature?
- Necessity (13.9, pass narrowly): the index-of-difficulty formula is stated but never used; what does it do for the argument?
- Method fit (13.10, pass narrowly): the power analysis assumed an lmer, the Planned analysis runs a paired t-test and a repeated-measures ANOVA; which method answers H1, and does 24 still give 80% power for it?
- Executability (13.11, pass narrowly): which mouse and which trackball, and does the choice of a current trackball bear on the "current devices" gap?
- Design (brief 7.1 vs draft): the brief says device between subjects because mouse habits transfer asymmetrically; the draft says within because skill variance swamps the device effect. Which argument wins, and what does it do to the session length and the per-group count?
- Scale (brief 6.6 vs 11.4): the smallest effect sizes of interest are in milliseconds, the model is on log movement time; on which scale is 100 ms judged?
- Data minimization: the screening form at sign-up and the demographic questionnaire after the tasks both collect age and handedness; why twice?
````

## How review detected the install state

Taken from the session transcript (the session log of the scratch project). Review read the file with the **Read** tool:

```text
Read: ~/.claude/plugins/installed_plugins.json
  -> read succeeded (no error); it holds no key beginning `oss@`
```

A Bash call (`ls`) came before the Read; it is unrelated to detection. Review did not ask the user whether research-grill is installed. The state it printed matches the real state.

## Criteria

| Criterion                                                       | Result                                              | Evidence                                                                                                                                                                                                                                                                                                                                                      |
| --------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Says "research-grill is not installed"                          | pass                                                | first line of the hand-off in the final message and in review.md                                                                                                                                                                                                                                                                                              |
| Both install commands                                           | pass                                                | `claude plugin marketplace add scdenney/open-science-skills` and `claude plugin install oss@open-science-skills` in one fenced block, in the final message and in review.md                                                                                                                                                                                   |
| Defend command for later, after the install commands            | pass                                                | `/oss:research-grill defend proposal/draft.md` after the install block, in both                                                                                                                                                                                                                                                                               |
| Seed list: "could someone run a session from the Method alone?" | pass in review.md; abbreviated in the final message | first seed objection in review.md; the final message has only "Method-alone runnability"                                                                                                                                                                                                                                                                      |
| Seed list: each waiver                                          | pass                                                | no waivers in this run; none listed                                                                                                                                                                                                                                                                                                                           |
| Seed list: each narrow pass with its doubt                      | pass in review.md; no doubts in the final message   | 13.6, 13.9, 13.10 and 13.11 (four narrow-pass rows in review.md, each a `pass narrowly`) plus design, scale and data-minimisation objections, with doubts in review.md                                                                                                                                                                                        |
| Final message ends with the hand-off text itself                | FAIL                                                | the final message ends with the install block, the defend command, and then one compressed line: "Seed list as in the file: Method-alone runnability; Delta, Necessity, Method fit, Executability doubts; device between vs within; SESOI scale vs log model; age and handedness collected twice." The doubts are not printed and the list points to the file |
| review.md Hand-off matches the final message                    | fail                                                | the install and defend commands match; the seed list does not (see above)                                                                                                                                                                                                                                                                                     |
| Detection                                                       | pass                                                | Read of `installed_plugins.json`, succeeded, no key beginning `oss@`; review printed the absent-case hand-off                                                                                                                                                                                                                                                 |

## Verdict

Verdict: spec bar met (clear install message, both install commands, defend command, seed list in review.md and in turn 1's final message); the plan's stricter final-message clause not met in turn 2 (seed list cut to a pointer to the file). Across the six reruns the stricter clause holds 5 of 6.
