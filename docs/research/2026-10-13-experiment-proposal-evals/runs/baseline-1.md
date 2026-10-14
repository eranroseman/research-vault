# Scenario 1 baseline, run 1

- Date: 2026-10-14
- Plugin commit: none loaded. The worktree was at `16f7bb6`; the experiment-proposal plugin was not installed and not passed with `--plugin-dir`. Other user-level plugins (for example `design`, `caveman`) are loaded in every `claude` session on this machine and were not disabled.
- Scenario: 1 Baseline (the RED step, no pass bar)
- Claude Code 2.1.273. The three runs started together, each in its own scratch project.

## Command

Scratch project: `tmp=$(mktemp -d)`, then `git init -q && git commit --allow-empty -qm init && git commit --allow-empty -qm fixtures` (there are no fixtures to copy for this scenario). Run from inside it, outside the repository:

```bash
cd <scratch> && timeout 900 claude -p "I want to run a controlled experiment comparing a mouse and a trackball for selecting targets on a screen, with right-handed young adults. Help me settle every design decision this experiment needs, with my reasons, and write them into a design brief file I can commit."
```

Exit code 0. Standard error was empty. No `--permission-mode` or `--allowedTools` flag was given. The session wrote its file without any permission prompt, so there was nothing to record as blocked and no second `--permission-mode acceptEdits` run was needed.

## Transcript, decisive lines

> Brief written to `experiment-design-brief.md` at repo root. Left uncommitted so you commit under your name.

> Repo had no prior files (both commits empty), so nothing to match against.

> **Sample size reasoning.** Soukoreff and MacKenzie (2004) summarize mouse throughput around 3.7 to 4.9 bits/s and trackball throughput around 3.0 bits/s in ISO-style tasks, a gap of roughly 1 bit/s. **Assumption:** the within-subject standard deviation of the device difference is about 1.2 bits/s, giving a standardized paired effect size dz of roughly 0.8. A paired t-test at alpha 0.05 with power 0.80 then needs 15 participants. I round to 16

> - **Primary test:** two-way repeated-measures ANOVA on throughput with factors device (2) and A×W cell (6). The device main effect is the primary result. Alpha is 0.05. Greenhouse-Geisser correction is applied if sphericity is violated.

Tool calls, from the session log: Skill `design:user-research` (an ambient user-level plugin, not experiment-proposal); Bash (`ls`, `git show --stat HEAD`, `git ls-tree`); Bash heredoc to write the brief; one Bash edit of the brief. No check for `Rscript`, `R`, or any power tool; the power figure is a hand calculation in prose.

## Scoring against the 32 design-tree items

Classes. **S**: the brief states a decision and a reason for it (no check on whether it matches the checklist's holds-when; off-policy decisions are marked). **D**: a decision is stated with no reason, or only part of the item. **N**: never raised. Because the prompt has no user turn, every S and D decision was decided without asking; under the fixture's rule (a decision invented without asking counts as unasked) **no item is settled** in the checklist's sense, and S and D together are the items decided without asking.

| Item | Subject                                  | Class | Evidence                                                                                                                                                        |
| ---- | ---------------------------------------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1  | Research question                        | S     | Section 1 question and a Reason line on directionality.                                                                                                         |
| 1.2  | Ethics route                             | S     | Section 17: approval by "my institution's review board", reason "required by review boards"; no requirements or review time.                                    |
| 1.3  | Data plan                                | S     | Section 17: numeric ID, key in a separate encrypted file deleted after the study closes; no access list.                                                        |
| 2.2  | Conditions, trials, session estimate     | S     | Section 6 table: 576 scored trials per participant, 50 to 60 minutes.                                                                                           |
| 2.3  | Pilot plan                               | S     | Section 16: four participants, not in the main sample, go/no-go criteria, with a Reason line.                                                                   |
| 2.4  | Timeline                                 | N     | No timeline.                                                                                                                                                    |
| 2.5  | Challenges and responses                 | S     | Section 16 and 7: recompute n if pilot dz is below 0.6; up to two extra practice sequences. Partial.                                                            |
| 6.1  | Hypotheses versus questions              | S     | Section 1.                                                                                                                                                      |
| 6.2  | Hypothesis variables, direction, sources | S     | Section 1 cites MacKenzie, Sellen and Buxton (1991) and Soukoreff and MacKenzie (2004).                                                                         |
| 6.5  | Interaction hypotheses                   | N     | No interaction hypothesis.                                                                                                                                      |
| 6.6  | Smallest effect size of interest         | N     | No smallest effect size of interest.                                                                                                                            |
| 6.7  | Decision rule per hypothesis             | N     | No support, falsify or inconclusive rule.                                                                                                                       |
| 7.1  | Independent variables, within or between | S     | Sections 2 and 3, with Reason lines.                                                                                                                            |
| 7.2  | Carry-over                               | S     | Sections 7 and 18: learning asymmetry accepted, extra trackball practice.                                                                                       |
| 7.3  | Overall design named                     | S     | Section 3: within-subjects, all six cells on both devices; the design is described, not named as a factorial.                                                   |
| 7.4  | Random assignment (between-subjects)     | N     | No statement about between-subjects variables.                                                                                                                  |
| 7.5  | Counterbalancing                         | S     | Section 4: device order alternated by enrollment order, not a random source.                                                                                    |
| 7.6  | Dependent variables                      | S     | Section 8 table with a Reason; no reliability or construct-validity statement.                                                                                  |
| 7.7  | Control variables                        | S     | Sections 10, 11 and 12: pointer acceleration off, gain fixed, same room.                                                                                        |
| 7.8  | Random variables listed                  | N     | Random variables not listed.                                                                                                                                    |
| 7.9  | Confounds                                | S     | Section 18 threats with handling; fatigue and order covered.                                                                                                    |
| 8.3  | Eligibility criteria                     | S     | Section 9, with a Reason for the screens.                                                                                                                       |
| 8.5  | Participant count and power              | S     | Section 9: n = 16 from an assumed dz of 0.8, hand-computed.                                                                                                     |
| 8.6  | Effect-size sourcing                     | S     | Section 9: effect from the literature gap plus an assumed SD, flagged Assumption. Off the checklist order: no smallest effect size of interest, no imprecision. |
| 8.7  | Sensitivity range                        | N     | One number only; a pilot recompute is promised.                                                                                                                 |
| 11.2 | Unit of analysis                         | D     | Section 8: throughput computed per sequence, averaged per participant and device; no stated reason, unit is not the trial.                                      |
| 11.4 | Model per hypothesis                     | S     | Section 15: repeated-measures ANOVA, reason "standard test for this design". Off policy: not a mixed-effects model.                                             |
| 11.5 | Fixed effects and coding                 | D     | Device main effect named; no contrast coding.                                                                                                                   |
| 11.6 | Random effects and simplification order  | N     | No random-effects structure, no simplification order.                                                                                                           |
| 11.7 | Inference method                         | D     | Greenhouse-Geisser correction only; no effect-size reporting rule.                                                                                              |
| 11.8 | Exclusions and trimming                  | S     | Section 15: spatial and temporal outlier rules fixed in advance, with a Reason.                                                                                 |
| 11.9 | Alpha and multiplicity                   | D     | "Alpha is 0.05"; no multiplicity policy for the many secondary tests.                                                                                           |

- Decided without asking, with a stated reason (S): 20 of 32 (1.1, 1.2, 1.3, 2.2, 2.3, 2.5, 6.1, 6.2, 7.1, 7.2, 7.3, 7.5, 7.6, 7.7, 7.9, 8.3, 8.5, 8.6, 11.4, 11.8).
- Decided without asking, no reason or partial (D): 4 of 32 (11.2, 11.5, 11.7, 11.9).
- Never raised (N): 8 of 32 (2.4, 6.5, 6.6, 6.7, 7.4, 7.8, 8.7, 11.6).
- Settled in the fixture's sense (decision, reason and asked): 0 of 32.

## The other checks

- R, power tool, SESOI, decision rule, simplification order, multiplicity: No R or power-tool check. SESOI not asked (no question of any kind; the session ends with a summary). No decision rule per hypothesis. No random-effects simplification order (no random effects at all). No multiplicity policy: several secondary tests, no correction mentioned.
- Brief file written: `experiment-design-brief.md` at the scratch root, 17881 bytes, untracked.
- Rationale in the user's words or invented: Yes, all of it. There is no user turn, so every "Reason" is the model's. The final reply says "each with a stated reason" and does not say the reasons are invented. The brief speaks in the user's voice ("the reason I chose it", "This is the question I intend to answer") and carries an `Author:` line with the user's full name, which is not in the prompt (it came from ambient context). Only device models, monitor, compensation and the within-subject SD are flagged **Assumption**.

## Against the fixture's expected line

Expected line: most of 6.6, 6.7, 8.6, 8.7, 11.6, 11.7, 11.9 never raised. Observed: never raised 6.6, 6.7, 8.7, 11.6 (4 of 7); 8.6 raised off the checklist order, 11.7 and 11.9 raised in part (11.9 without a multiplicity policy). No prerequisite check: matches. Decisions made without asking: matches (all of them). The expectation holds for this run.

## Verdict

RED recorded; the scenario has no pass bar. The run asked nothing, wrote a complete-looking brief, and every reason in it is the model's. The unraised or partly raised items are the ones the plugin adds.
