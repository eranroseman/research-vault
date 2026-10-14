# Scenario 1 baseline, run 2

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

> Brief written: `docs/design-brief.md` (untracked, ready for you to commit). Repo was empty, so I created `docs/` for it.

> **"My reasons" caveat.** You gave no reasons, so each rationale is my proposed default. Items needing your input (device models, display, compensation, final pixel sizes) marked **[confirm]** and collected in section 15.

> **Power table is hand-computed** via normal approximation (no scipy here). N = 24 gives roughly 0.90 power at d = 0.7. Confirm in G\*Power before preregistering. Flagged in file.

> **Multiple comparisons.** The four hypotheses are distinct questions, each tested once; no correction is applied across them. The twelve questionnaire items under H4 are corrected with Holm's procedure.

> Advisor review unavailable this turn (rate-limited). Not re-reviewed.

Tool calls, from the session log: Bash (`ls`, `git log`, `git show --stat HEAD`, `git ls-tree`); one Bash call importing `scipy` to compute paired-t power, which failed (`ModuleNotFoundError: No module named 'scipy'`); Bash heredoc to write the brief. No check for `Rscript` or `R`. The one power-tool attempt was a Python one, not a prerequisite check, and fell back to a hand calculation.

## Scoring against the 32 design-tree items

Classes. **S**: the brief states a decision and a reason for it (no check on whether it matches the checklist's holds-when; off-policy decisions are marked). **D**: a decision is stated with no reason, or only part of the item. **N**: never raised. Because the prompt has no user turn, every S and D decision was decided without asking; under the fixture's rule (a decision invented without asking counts as unasked) **no item is settled** in the checklist's sense, and S and D together are the items decided without asking.

| Item | Subject                                  | Class | Evidence                                                                                                                                             |
| ---- | ---------------------------------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1  | Research question                        | S     | Section 1 question, with a 'Why directional hypotheses' paragraph.                                                                                   |
| 1.2  | Ethics route                             | D     | Section 11: IRB approval before any pilot; no requirements, no review time, no reason.                                                               |
| 1.3  | Data plan                                | D     | Section 11: participant codes, key destroyed after payment reconciliation; no reason, no access list.                                                |
| 2.2  | Conditions, trials, session estimate     | S     | Sections 3 and 6: 810 clicks, step times, 'Why three blocks'.                                                                                        |
| 2.3  | Pilot plan                               | D     | Section 12: three pilot participants, not counted, purpose listed; no stated reason for the number.                                                  |
| 2.4  | Timeline                                 | N     | No timeline.                                                                                                                                         |
| 2.5  | Challenges and responses                 | S     | Section 4: recruit 28 to keep 24 after exclusions; Section 3: why not ABAB (no-show risk). Partial.                                                  |
| 6.1  | Hypotheses versus questions              | S     | Section 1.                                                                                                                                           |
| 6.2  | Hypothesis variables, direction, sources | S     | Section 1 cites Card et al. (1978) and ISO 9241-411 comparisons.                                                                                     |
| 6.5  | Interaction hypotheses                   | D     | Section 1: device x ID interaction named exploratory; no reason.                                                                                     |
| 6.6  | Smallest effect size of interest         | N     | No smallest effect size of interest.                                                                                                                 |
| 6.7  | Decision rule per hypothesis             | N     | No support, falsify or inconclusive rule.                                                                                                            |
| 7.1  | Independent variables, within or between | S     | Section 3, 'Why within-subjects'.                                                                                                                    |
| 7.2  | Carry-over                               | S     | Section 3 (ABAB discussion) and Section 10 familiarity asymmetry.                                                                                    |
| 7.3  | Overall design named                     | S     | Section 3: fully crossed within-subjects; 'lets every participant give a direct preference judgment'.                                                |
| 7.4  | Random assignment (between-subjects)     | N     | No statement about between-subjects variables; order assigned by participant-ID parity, not a random source.                                         |
| 7.5  | Counterbalancing                         | S     | Section 3, 'Why counterbalance rather than randomize'.                                                                                               |
| 7.6  | Dependent variables                      | S     | Section 7, 'Why throughput is primary'; speed paired with accuracy.                                                                                  |
| 7.7  | Control variables                        | S     | Section 5, 'Why disable acceleration'.                                                                                                               |
| 7.8  | Random variables listed                  | N     | Random variables not listed.                                                                                                                         |
| 7.9  | Confounds                                | S     | Section 10 threat table.                                                                                                                             |
| 8.3  | Eligibility criteria                     | S     | Section 4, 'Why restrict handedness and age'.                                                                                                        |
| 8.5  | Participant count and power              | S     | Section 4: N = 24 from a normal-approximation table; hand-computed, 'confirm in G\*Power'.                                                           |
| 8.6  | Effect-size sourcing                     | S     | Section 4: d around 0.8 from the literature, powered for 0.6 as margin. Off the checklist order.                                                     |
| 8.7  | Sensitivity range                        | S     | Section 4 table: power at N = 24 for d = 0.6, 0.7 and 0.8.                                                                                           |
| 11.2 | Unit of analysis                         | S     | Section 9: mixed models 'use every trial rather than aggregated means'; primary test on per-participant means.                                       |
| 11.4 | Model per hypothesis                     | S     | Section 9: linear mixed model for log movement time, mixed logistic model for errors, paired t-test for throughput, Wilcoxon for ratings (not clmm). |
| 11.5 | Fixed effects and coding                 | D     | Fixed effects listed (device, nominal ID, block, device x ID); no coding, no named coefficient per hypothesis.                                       |
| 11.6 | Random effects and simplification order  | D     | Random intercept per participant and slope for device; no simplification order.                                                                      |
| 11.7 | Inference method                         | D     | Reports coefficients with CIs and d_z; how p values or CIs are obtained is not stated.                                                               |
| 11.8 | Exclusions and trimming                  | S     | Section 8, 'Why fix these now'.                                                                                                                      |
| 11.9 | Alpha and multiplicity                   | S     | Section 9: alpha 0.05, no correction across four hypotheses (reason given), Holm on the twelve questionnaire items.                                  |

- Decided without asking, with a stated reason (S): 20 of 32 (1.1, 2.2, 2.5, 6.1, 6.2, 7.1, 7.2, 7.3, 7.5, 7.6, 7.7, 7.9, 8.3, 8.5, 8.6, 8.7, 11.2, 11.4, 11.8, 11.9).
- Decided without asking, no reason or partial (D): 7 of 32 (1.2, 1.3, 2.3, 6.5, 11.5, 11.6, 11.7).
- Never raised (N): 5 of 32 (2.4, 6.6, 6.7, 7.4, 7.8).
- Settled in the fixture's sense (decision, reason and asked): 0 of 32.

## The other checks

- R, power tool, SESOI, decision rule, simplification order, multiplicity: No R check; one failed scipy power attempt, then a hand-computed normal approximation with "confirm in G\*Power". SESOI not asked. No decision rule per hypothesis. Random-effects structure stated (intercept per participant, slope for device) with no simplification order. Multiplicity policy raised (no correction across the four hypotheses; Holm on the twelve questionnaire items).
- Brief file written: `docs/design-brief.md` (the run created `docs/`), untracked.
- Rationale in the user's words or invented: Yes, all of it, and this run says so: "You gave no reasons, so each rationale is my proposed default." It marks six values [confirm]. The brief's status line calls every decision "a proposed default with its rationale".

## Against the fixture's expected line

Expected line: most of 6.6, 6.7, 8.6, 8.7, 11.6, 11.7, 11.9 never raised. Observed: never raised 6.6 and 6.7 only (2 of 7). 8.6 and 8.7 raised (8.7 as a three-row power table), 11.9 raised with a multiplicity policy, 11.6 and 11.7 raised in part (no simplification order, no p-value method). Against the literal wording the expectation does NOT hold for this run: the run raised more of the list than predicted, and it was the only one to use mixed models. What holds: no R prerequisite check, no SESOI, no decision rule, no simplification order, decisions made without asking.

## Verdict

RED recorded; the scenario has no pass bar. The run asked nothing, wrote a complete-looking brief, and every reason in it is the model's. The unraised or partly raised items are the ones the plugin adds.
