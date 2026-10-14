# Scenario 1 baseline, run 3

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

> Brief written: `experiment-design-brief.md` (not committed, you said you'd commit).

> Session was non-interactive, so reasons are mine, written in your voice. Four assumptions flagged at top of file that change the study if wrong:

> **Status:** draft for commit. Every decision below is settled with a stated reason and the alternatives that were rejected. Edit the reason text if your own rationale differs; the decision structure stands either way.

> **Power rationale.** Primary test is a paired comparison of per-participant throughput. With alpha = 0.05 two-tailed, N = 24 gives approximately 0.80 power to detect a standardized paired difference (Cohen's dz) of 0.60, and above 0.95 power for dz = 0.80.

> - **Multiple comparisons:** H1 is the confirmatory test. H2 to H4 are labelled secondary and reported with uncorrected p-values and effect sizes; no family-wise correction is applied, and the report says so.

Tool calls, from the session log: Bash (`ls`, `git log`, `cat *.md`); Skill `design:user-research` (an ambient user-level plugin, not experiment-proposal); Bash heredoc to write the brief; one Bash `sed` edit of the brief. No check for `Rscript`, `R`, or any power tool; the brief only recommends G\*Power or the `pwr` R package for later.

## Scoring against the 32 design-tree items

Classes. **S**: the brief states a decision and a reason for it (no check on whether it matches the checklist's holds-when; off-policy decisions are marked). **D**: a decision is stated with no reason, or only part of the item. **N**: never raised. Because the prompt has no user turn, every S and D decision was decided without asking; under the fixture's rule (a decision invented without asking counts as unasked) **no item is settled** in the checklist's sense, and S and D together are the items decided without asking.

| Item | Subject                                  | Class | Evidence                                                                                                                               |
| ---- | ---------------------------------------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1  | Research question                        | S     | Section 1 Decision and Reason.                                                                                                         |
| 1.2  | Ethics route                             | S     | Section 12: ethics board approval before recruitment, Reason 'standard practice'; no requirements or review time.                      |
| 1.3  | Data plan                                | S     | Section 12: pseudonymous codes, consent forms stored separately; retention not set.                                                    |
| 2.2  | Conditions, trials, session estimate     | S     | Section 8: 324 scored trials per device, 60 minute budget, Reason.                                                                     |
| 2.3  | Pilot plan                               | D     | Section 13: pilot of 2 to 3 participants listed under open items; no reason.                                                           |
| 2.4  | Timeline                                 | N     | No timeline.                                                                                                                           |
| 2.5  | Challenges and responses                 | S     | Sections 5 and 6: over-recruit by 2 to 4; plateau cap of 8 with a 'no plateau' log. Partial.                                           |
| 6.1  | Hypotheses versus questions              | S     | Section 1.                                                                                                                             |
| 6.2  | Hypothesis variables, direction, sources | S     | Section 1: direction from 'the historical pattern that mice outperform trackballs'; no citation.                                       |
| 6.5  | Interaction hypotheses                   | N     | No interaction hypothesis.                                                                                                             |
| 6.6  | Smallest effect size of interest         | N     | No smallest effect size of interest.                                                                                                   |
| 6.7  | Decision rule per hypothesis             | N     | H1 confirmatory and H2 to H4 secondary; no support, falsify or inconclusive rule.                                                      |
| 7.1  | Independent variables, within or between | S     | Section 2 with Alternatives rejected.                                                                                                  |
| 7.2  | Carry-over                               | S     | Section 2 and 6.                                                                                                                       |
| 7.3  | Overall design named                     | S     | Section 2: within-subjects, device single factor, A x W crossed.                                                                       |
| 7.4  | Random assignment (between-subjects)     | S     | Section 2: 'Mixed design ... out of scope; the population is deliberately homogeneous'.                                                |
| 7.5  | Counterbalancing                         | S     | Section 2: pre-generated balanced schedule.                                                                                            |
| 7.6  | Dependent variables                      | S     | Section 4 with Reason; no reliability statement.                                                                                       |
| 7.7  | Control variables                        | S     | Section 7 with Reason.                                                                                                                 |
| 7.8  | Random variables listed                  | N     | Random variables not listed.                                                                                                           |
| 7.9  | Confounds                                | S     | Sections 6 and 7.                                                                                                                      |
| 8.3  | Eligibility criteria                     | S     | Section 5 Reason.                                                                                                                      |
| 8.5  | Participant count and power              | S     | Section 5: N = 24, power 0.80 for dz 0.60; 'Recompute with G\*Power or the pwr R package'.                                             |
| 8.6  | Effect-size sourcing                     | S     | Section 5: 'powered for a medium standardized effect'; a field benchmark not named as last resort. Off the checklist order.            |
| 8.7  | Sensitivity range                        | S     | Section 5: power at dz 0.60 and at 0.80.                                                                                               |
| 11.2 | Unit of analysis                         | S     | Section 11: throughput 'defined at the cell level, not trial level'; errors modelled per trial.                                        |
| 11.4 | Model per hypothesis                     | S     | Section 11: RM-ANOVA for throughput and MT, binomial GLMM for errors; alternatives-rejected line names the mixed model for throughput. |
| 11.5 | Fixed effects and coding                 | D     | GLMM fixed effects device and ID stated; no coding.                                                                                    |
| 11.6 | Random effects and simplification order  | D     | Random intercept per participant for the GLMM; no simplification order.                                                                |
| 11.7 | Inference method                         | D     | Greenhouse-Geisser, partial eta squared, dz with 95 percent CI; GLMM p-value method not stated.                                        |
| 11.8 | Exclusions and trimming                  | S     | Section 10 with Reason.                                                                                                                |
| 11.9 | Alpha and multiplicity                   | S     | Section 11: alpha 0.05; H2 to H4 uncorrected and labelled secondary, reason given.                                                     |

- Decided without asking, with a stated reason (S): 23 of 32 (1.1, 1.2, 1.3, 2.2, 2.5, 6.1, 6.2, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.9, 8.3, 8.5, 8.6, 8.7, 11.2, 11.4, 11.8, 11.9).
- Decided without asking, no reason or partial (D): 4 of 32 (2.3, 11.5, 11.6, 11.7).
- Never raised (N): 5 of 32 (2.4, 6.5, 6.6, 6.7, 7.8).
- Settled in the fixture's sense (decision, reason and asked): 0 of 32.

## The other checks

- R, power tool, SESOI, decision rule, simplification order, multiplicity: No R or power-tool check (the brief recommends G\*Power or `pwr` for later; it does not check they exist). SESOI not asked. No decision rule per hypothesis. Random intercept per participant for the GLMM, no simplification order. Multiplicity policy raised (H1 confirmatory, H2 to H4 secondary, no family-wise correction, with a reason).
- Brief file written: `experiment-design-brief.md` at the scratch root, 22229 bytes, untracked.
- Rationale in the user's words or invented: Yes, all of it, and this run says so: "reasons are mine, written in your voice". The brief itself still says every decision is "settled with a stated reason" and tells the user to edit the reasons if theirs differ.

## Against the fixture's expected line

Expected line: most of 6.6, 6.7, 8.6, 8.7, 11.6, 11.7, 11.9 never raised. Observed: never raised 6.6 and 6.7 only (2 of 7). 8.6 (as a medium-effect convention), 8.7 (two effect sizes), 11.9 (with a multiplicity policy) raised; 11.6 and 11.7 raised in part. Against the literal wording the expectation does NOT hold for this run. What holds: no R prerequisite check, no SESOI, no decision rule, no simplification order, decisions made without asking.

## Verdict

RED recorded; the scenario has no pass bar. The run asked nothing, wrote a complete-looking brief, and every reason in it is the model's. The unraised or partly raised items are the ones the plugin adds.
