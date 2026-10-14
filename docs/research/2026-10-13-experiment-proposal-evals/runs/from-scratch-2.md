# Scenario 3, from scratch, run 2

Date: 2026-10-14. Plugin commit: 6bb6ed7. Scenario label: from-scratch. Driver: headless `claude -p` turns, answered strictly from `fixtures/from-scratch-answers.md` (the plan calls this scenario interactive; the author delegated it). R 4.3.3 with lme4, lmerTest, ordinal and simr was installed; no shim. A first attempt against an earlier plugin text was voided before any answer to round 1; this record is the restart.

Verdict: FAIL on the rating bar. Everything else in the bar is met: all items settled, the count is computed and recorded (40 participants), the hci-researcher was consulted, the freeze commit exists. The rating (and the error model) were excluded from `proposal/power.R`, so the output has no `rating` row.

## Turns

| Turn | Command (flags as in turn 1 on every turn)                                                                                                                           | Wall time |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 1    | `timeout 5400 claude -p "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"`            | 129 s     |
| 2    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 43 s      |
| 3    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 155 s     |
| 4    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 160 s     |
| 5    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 49 s      |
| 6    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 128 s     |
| 7    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 39 s      |
| 8    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 33 s      |
| 9    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 190 s     |
| 10   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 56 s      |
| 11   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 21 s      |
| 12   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 27 s      |
| 13   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 811 s     |
| 14   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 16 s      |

Turn texts, verbatim (the driver sent the same flags every turn; `$P` is `<checkout>/plugins/experiment-proposal`, run from `<scratch>`):

Turn 1:

```text
/experiment-proposal:design Novice smartphone users entering text: does a swipe keyboard beat tap typing? Within subjects, two keyboards, phrases from a standard set, speed and errors logged, plus a 1 to 7 ease rating after each keyboard.
```

Turn 2:

```text
Q1 (item 1.1): "Does entering phrases with a swipe keyboard, compared with a tap keyboard, change words per minute for novice smartphone users?" Levels: tap, swipe. Draft path: yes, accept the default proposal/draft.md.
```

Turn 3:

```text
Answers for round 2, by item (the Q numbers follow your item order 1.2, 1.3, 6.1, 7.1, 7.6):
Item 1.2 (Q1): The university IRB; minimal-risk expedited review, about three weeks; a consent form and the phrase set are required.
Item 1.3 (Q2): Keystroke logs and phrase times only, no names linked, no recordings; the two experimenters have access; raw data kept five years, then deleted.
Item 6.1 (Q3): H1 directional (swipe faster); H2 "no worse" on errors; RQ1 on the ease rating (I am unsure of the direction).
Item 7.1 (Q4): Keyboard: the phone's built-in tap keyboard versus its swipe mode; within subjects because typing skill varies hugely between people.
Item 7.6 (Q5): Words per minute (characters over five over minutes, app-logged, ratio); uncorrected error rate (MSD over length, app-logged, ratio) and a per-phrase indicator of any uncorrected error (binary), which H2 and item 11.4 use; ease rating 1 to 7 after each keyboard (ordinal, questionnaire). Yes to the recommended reliability and construct-validity statements.
```

Turn 4:

```text
Answers for round 3, by item (Q order is 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9, 11.2):
Item 6.2 (Q1): Yes to the recommendation. Sources: the two swipe-keyboard studies I "will add from lit-search"; accept the direction as settled, with lit-search listed under Open items.
Item 6.5 (Q2): No interaction idea.
Item 7.2 (Q3): Symmetric: each keyboard is minutes of practice from the other.
Item 7.4 (Q4): No between-subjects variable.
Item 7.7 (Q5): Right-handed, 18 to 35, owns a smartphone, never used swipe; same phone, app, phrases, room, script; yes to the recommended validity trade-off wording.
Item 7.8 (Q6): Typing skill, mood, time of day, phrase order.
Item 7.9 (Q7): History: run all sessions within three weeks; maturation: one 40-minute session; instrumentation: freeze the app before the first participant.
Item 11.2 (Q8): Trials (phrases) are the unit; no aggregation.
```

Turn 5:

```text
Answers for round 4, by item (Q order is 6.6, 7.3, 7.5, 8.3, 11.4, 11.8). I am giving my own values where yours differ.
Item 6.6 (Q1): H1: 3 words per minute. H2: an equivalence bound of 2 percentage points in the proportion of phrases with an uncorrected error, converted to log-odds at the baseline rate, tested with TOST. RQ1: 0.5 on the latent scale. (Not your 0.05 or odds ratio 1.5 bound, and not 1.0 for RQ1.)
Item 7.3 (Q2): Yes: a one-factor, two-level within-subjects design.
Item 7.5 (Q3): Counterbalance keyboard order, AB and BA, half each, assigned from a shuffled list; the same phrase set for both keyboards, in a fresh random order per keyboard. No order term in the confirmatory models, since order is counterbalanced (an order term only in a sensitivity check). I do not want disjoint phrase subsets per keyboard.
Item 8.3 (Q4): The four criteria (right-handed, 18 to 35, owns a smartphone, never used swipe), screened by a sign-up form; none selects on typing speed. No other criterion.
Item 11.4 (Q5): lmer for words per minute; glmer binomial for a per-phrase error indicator; clmm for the rating.
Item 11.8 (Q6): Exclude failed sessions and participants who turn out ineligible; trim phrases with a time under 1 second or over 60 seconds; report every exclusion.

On your flag about item 6.2 (run 2 only): keep H1 as is, swipe faster, directional. The decision stands.
```

Turn 6:

```text
Answers for round 5, by item (Q order is 2.2, 6.7, 11.5):
Item 2.2 (Q1): The pilot will decide the phrases per keyboard; 20 is the working value; two conditions, about 40 minutes.
Item 6.7 (Q2): Support if the 95% interval excludes zero in the predicted direction and the point estimate is at least the SESOI; falsify if it excludes the SESOI; otherwise inconclusive.
Item 11.5 (Q3): Keyboard as the only fixed effect in the confirmatory models, sum-coded (tap -0.5, swipe +0.5), not treatment-coded; H1 and H2 map to the keyboard coefficient; no order term, since order is counterbalanced (an order term only in a sensitivity check).
```

Turn 7:

```text
Answers for round 6, by item:
Item 2.3: Four people from the lab; it refines the phrases per keyboard (recorded under 2.2) and the script timings; its data will not be reported.
Item 11.6: Yes to the hci-researcher's recommendation as you state it (the random-effects structure and drop order you give).
Item 6.7 clarification: Yes, accept your reading for H2 (TOST at the item 6.6 bound; the nearest sheet row is 6.6, H2 by TOST). The rule I gave was for H1. For RQ1 the rule I gave applies, read in either direction.
```

Turn 8:

```text
Answers for round 7, by item:
Item 2.4 (Q1): I don't know yet.
Item 11.7 (Q2): Satterthwaite through lmerTest for lmer; Wald z for glmer and clmm; standardized coefficients and odds ratios as effect sizes.
```

Turn 9:

```text
Answers for round 8, by item:
Item 2.5 (Q1): Too few sign-ups: extend recruiting to a second course; a keyboard app failing in the pilot: freeze a fallback build. (These two only.)
Item 11.9 (Q2): Alpha 0.05; every p value reported with its effect size; two confirmatory hypotheses, Holm-adjusted. (I am not accepting "no multiplicity correction"; H1 and H2 are the two confirmatory hypotheses and are Holm-adjusted.)
```

Turn 10:

```text
Yes to every question, P1 to P10, accepting each recommendation as you worded it (for P1, option b).
```

Turn 11:

```text
Yes, run proposal/power.R as shown, including the plan you listed.
```

Turn 12:

```text
Is the power run finished? Continue.
```

Turn 13:

```text
Is the power run finished? Continue.
```

Turn 14:

```text
Approve the brief. Yes, freeze it.
```

Rounds: 8 design rounds, then the P batch (P1 to P10, answered in turn 10), the filled block (turn 11, OK to run), two "Is the power run finished? Continue." turns (12 and 13), and the approval and freeze turn (14). 14 turns in all. Consistency questions answered from the sheet: in turn 4's reply the session flagged that every first-session study it knew showed swipe slower and offered to restate H1; the driver answered "keep H1 as is, swipe faster, directional. The decision stands" (sheet row 6.1). In turn 6 the session asked whether H2 and RQ1 follow the TOST and 0.5 reading; the driver answered yes, citing the sheet's row 6.6.

## Transcript, decisive lines

- Turn 1: "R check passed (lme4, lmerTest, ordinal, simr all present)."
- hci-researcher: five Agent calls (7.7, 7.9, 6.6, 7.5, 11.6) and one SendMessage follow-up to the same subagent (the WPM slope SD). Turn 3: "Consulted hci-researcher on items 7.7 and 7.9." Turn 4: "Consulted hci-researcher on items 6.6 and 7.5."
- Turn 8 (round 7 recorded): "item 2.4 provisional, listed under Open items."
- Turn 9, the P batch, opened with three flags. "**P1.** H2 handling. Options: (a) amend item 6.6 to a wider bound ... (b) keep the 2-point bound, exclude the error model from the run, and record H2 as not powered ... (c) keep the model in the run ... Recommended: (b)." "**P2.** Rating model: exclude from `power.R` and record the analytic estimate (about 209 for 0.80 ...) ... Accept? Recommended: yes." Turn 10: "Yes to every question, P1 to P10, accepting each recommendation as you worded it (for P1, option b)." So the error and rating models were excluded by the sheet's answers.
- Turn 10: "`proposal/power.R` written (the copy command was blocked by the permission system; I wrote the template content from my earlier read, generic part unchanged)." Later the session verified "generic tail identical: TRUE / header identical: TRUE" against the template.
- Turn 11, how it ran R: three `Rscript` calls with `run_in_background: true` (the 3 WPM search, and in-memory variants at 2 and 4 WPM for item 8.7), 16:20:31 to 16:20:40 UTC. The turn ended after 21 s: "Three searches running in background ... Waiting for them to finish". Harness at the start of turn 12: `<status>stopped</status>` for all three ("didn't finish before the previous session ended"); the three output files were empty.
- Turn 12: the session found them empty, relaunched all three in the background (16:21:43 to 16:21:47 UTC), turn ended after 27 s ("Restarted all three searches ... in the background"). Stopped again at the start of turn 13.
- Turn 13 (811 s): a `| tee` form was refused as a compound command; the session then ran the three searches as foreground Bash calls with `timeout: 600000`. They completed one after another: 3 WPM 16:24:33 to 16:26:23 UTC (1.8 min), 2 WPM to 16:28:22 (2.0 min), 4 WPM to 16:30:17 (1.9 min). It set `n_sims = 1000` and `n_grid = c(40, 48)` (the chosen count and the next grid value) and ran `Rscript proposal/power.R` in the foreground, 16:30:25 to 16:34:07 UTC (3.7 min). No grid shrink beyond the skill's own step 5. Each run was the wpm model only, so each is much faster than the three-model run would be.
- Turn 13 end: "Participant count: 40 (20 per order). Governing run, 1000 simulations, alpha 0.025, 3 WPM effect, 20 phrases per keyboard: power 0.88 at 40. The 200-simulation search gave 0.79 at 32, just under target, so 40 is the mechanical choice and slightly conservative. Sensitivity (item 8.7): at 2 WPM no grid value reaches 0.80; at 4 WPM, 24 suffices." "H2 is not powered ... RQ1 is exploratory; power near 0.2 at 40 for a 0.5 latent-logit effect." It asked "Freeze it?"
- Turn 14: "Brief frozen. Commit 6876ef6, "Freeze the design brief", holds `proposal/design-brief.md` (Status: frozen 2026-10-14) and `proposal/power.R`."

## Power output

200-simulation searches (full grid, wpm only) and the 1000-simulation governing run, as printed by `Rscript proposal/power.R`:

200-simulation search, H1 = 3 WPM (wall about 1.8 min):

```text
## Power curve (200 simulations per point, alpha = 0.025, seed 20261013)
| Measure | n | Power | 95% CI |
| --- | --- | --- | --- |
| wpm | 12 | 0.28 | 0.22 to 0.35 |
| wpm | 16 | 0.43 | 0.36 to 0.50 |
| wpm | 20 | 0.56 | 0.49 to 0.63 |
| wpm | 24 | 0.64 | 0.57 to 0.71 |
| wpm | 32 | 0.79 | 0.73 to 0.84 |
| wpm | 40 | 0.87 | 0.82 to 0.91 |
| wpm | 48 | 0.92 | 0.87 to 0.95 |
Primary measure: wpm
Participant count: 40 (the smallest grid value with power >= 0.80 for wpm)
```

200-simulation range run, H1 = 2 WPM (wall about 2.0 min):

```text
## Power curve (200 simulations per point, alpha = 0.025, seed 20261013)
| Measure | n | Power | 95% CI |
| --- | --- | --- | --- |
| wpm | 12 | 0.10 | 0.06 to 0.15 |
| wpm | 16 | 0.20 | 0.14 to 0.26 |
| wpm | 20 | 0.25 | 0.19 to 0.32 |
| wpm | 24 | 0.30 | 0.24 to 0.37 |
| wpm | 32 | 0.41 | 0.35 to 0.49 |
| wpm | 40 | 0.51 | 0.44 to 0.58 |
| wpm | 48 | 0.60 | 0.53 to 0.67 |
Primary measure: wpm
No participant count in the grid reaches power 0.80 for the primary measure; extend n_grid or revisit the effect size, with a reason.
```

200-simulation range run, H1 = 4 WPM (wall about 1.9 min):

```text
## Power curve (200 simulations per point, alpha = 0.025, seed 20261013)
| Measure | n | Power | 95% CI |
| --- | --- | --- | --- |
| wpm | 12 | 0.54 | 0.46 to 0.61 |
| wpm | 16 | 0.70 | 0.63 to 0.76 |
| wpm | 20 | 0.78 | 0.72 to 0.84 |
| wpm | 24 | 0.90 | 0.84 to 0.93 |
| wpm | 32 | 0.96 | 0.93 to 0.99 |
| wpm | 40 | 0.99 | 0.97 to 1.00 |
| wpm | 48 | 1.00 | 0.98 to 1.00 |
Primary measure: wpm
Participant count: 24 (the smallest grid value with power >= 0.80 for wpm)
```

1000-simulation governing run, n_grid = 40 and 48, H1 = 3 WPM (wall about 3.7 min):

```text
## Power curve (1000 simulations per point, alpha = 0.025, seed 20261013)
| Measure | n | Power | 95% CI |
| --- | --- | --- | --- |
| wpm | 40 | 0.88 | 0.86 to 0.90 |
| wpm | 48 | 0.94 | 0.92 to 0.95 |
Primary measure: wpm
Participant count: 40 (the smallest grid value with power >= 0.80 for wpm)
```

There is no `rating` row (and no error row): `proposal/power.R` has the `wpm` model only.

## Pass bar

| Criterion                                                    | Result | Evidence                                                                                                                                              |
| ------------------------------------------------------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Every design-tree item settled, provisional or pilot settles | PASS   | 32 entries: 29 `settled` plus 8.5, 8.6, 8.7 `settled`, 2.2 `pilot settles`, 2.4 `provisional`; `Status: frozen 2026-10-14`.                           |
| 2.4 provisional, 2.2 pilot settles                           | PASS   | \`2.4 Timeline                                                                                                                                        |
| Mixed-model plan complete (11.2, 11.4 to 11.9)               | PASS   | All `settled`.                                                                                                                                        |
| Power computed, `proposal/power.R` run, count recorded       | PASS   | Count 40 from the 1000-simulation run; 8.5 entry `Source: proposal/power.R, run 2026-10-14`.                                                          |
| Rating's power through the clmm loop, a `rating` row         | FAIL   | No `rating` row: P2 (exclude the rating model) was accepted by the sheet's "yes to every P question". The error model was excluded too (P1 option b). |
| hci-researcher consulted at least once                       | PASS   | Five Agent calls and a follow-up message.                                                                                                             |
| Freeze commit exists                                         | PASS   | `6876ef6 Freeze the design brief`.                                                                                                                    |

## Verdict

FAIL on the rating row only. Observations: background `Rscript` was stopped at session end twice (turns 11 and 12); the session fell back to foreground runs with a 600000 ms timeout, which worked because the wpm-only runs are short. A run with the clmm loop would not fit that timeout. The error/rating exclusions come from the session's reading of the template (one trial count for every model; the rating is one per participant per keyboard), proposed in P1 and P2 and accepted by the driver's blanket "yes".

## Brief (final state in the scratch project)

```text
--- HEADER
# Design brief: Swipe versus tap keyboard for novice smartphone text entry

Draft: proposal/draft.md
Status: frozen 2026-10-14
Checklist: experiment-proposal 0.1.0
--- STATUSES
1.1 The question | settled
1.2 Ethics route | settled
1.3 Data plan | settled
2.2 Conditions, trials and session | pilot settles
2.3 Pilot plan | settled
2.4 Timeline | provisional
2.5 Expected challenges | settled
6.1 Hypotheses and research questions | settled
6.2 Hypotheses with variables, direction and null | settled
6.5 Interaction hypotheses | settled
6.6 Smallest effect size of interest | settled
6.7 Decision rules | settled
7.1 Independent variables | settled
7.2 Carry-over | settled
7.3 Overall design | settled
7.4 Random assignment | settled
7.5 Counterbalancing | settled
7.6 Dependent variables | settled
7.7 Control variables | settled
7.8 Random variables | settled
7.9 Confounds | settled
8.3 Eligibility | settled
8.5 Participant count | settled
8.6 Effect size assumed | settled
8.7 Sensitivity range | settled
11.2 Unit of analysis | settled
11.4 Model family per dependent variable | settled
11.5 Fixed effects and contrast coding | settled
11.6 Random-effects structure and simplification order | settled
11.7 Inference method and effect-size reporting | settled
11.8 Exclusions and trimming | settled
11.9 Significance level, reporting and multiplicity | settled
--- Looked up
- R prerequisite check (lme4, lmerTest, ordinal, simr): passed (Rscript, 2026-10-14)
- Git repository root: <scratch> (git rev-parse, 2026-10-14)
- Standard phrase set: MacKenzie and Soukoreff (2003), "Phrase sets for evaluating text entry techniques", CHI EA; 500 English phrases, no punctuation, lowercase (from memory, 2026-10-14)
- Words per minute: (transcribed characters minus 1) / 5 / minutes from first to last keystroke; a word is 5 characters (MacKenzie, 2002; from memory, 2026-10-14)
- Error metrics: minimum string distance (MSD) error rate between presented and transcribed phrase, and total error rate splitting corrected and uncorrected errors (Soukoreff and MacKenzie, 2001, 2003; from memory, 2026-10-14)
- Single Ease Question (SEQ): standard one-item 7-point ease rating, "Overall, how difficult or easy was the task to complete?" (Sauro and Dumas, 2009; from memory, 2026-10-14)
- Prior first-session swipe vs tap evidence (hci-researcher, memory estimates, verify via lit-search, 2026-10-14): Reyal, Zhai and Kristensson (CHI 2015), touch about 33 to 35 WPM, gesture initially about 28 to 30 WPM in the lab with higher uncorrected errors; Kristensson and Zhai (UIST 2004, SHARK2), novices started mid-teens WPM; Palin et al. (MobileHCI 2019), 37,000 volunteers, mean about 36 WPM, SD about 13, uncorrected error rate 2 to 3 percent. Every first-session comparison known shows swipe slower than tap for people who already tap.
- Power simulation baselines (hci-researcher, memory estimates, 2026-10-14): tap WPM mean 33, between-participant SD 8, per-phrase residual SD 6; per-phrase P(any uncorrected error) under tap 0.30 (logit -0.85), participant intercept SD 0.9 logit; ease rating thresholds -4.0, -2.8, -1.6, -0.4, 0.9, 2.4, participant SD 1.5 logit; phrase length about 28.6 characters.
- By-participant keyboard slope SD for the WPM model: about 5 WPM, plausible range 4 to 7, slope-intercept correlation near zero (hci-researcher, memory estimate, 2026-10-14)
- Two-condition crossover parameterization (hci-researcher, 2026-10-14): Keyboard is determined by Order x Period, so fit Keyboard + Period + Order; Keyboard x Order is aliased with Period.
- H2 bound conversion: 2 percentage points at tap baseline 0.30 gives 0.32; logit(0.30) = -0.847, logit(0.32) = -0.754, difference 0.0935 logit, odds ratio 1.10 (computed, 2026-10-14)
- Analytic H2 TOST requirement (computed, 2026-10-14): with 20 phrases per condition at tap baseline 0.30, the per-participant paired logit difference has SD about 0.69; 80 percent TOST power at one-sided alpha 0.05 with true effect 0 needs about 337 participants at the 2-percentage-point bound (0.0935 logit) and about 18 at an odds-ratio 1.5 bound (0.405 logit)
- Analytic RQ1 estimate (computed, 2026-10-14): a 0.5 latent-logit effect against a paired latent difference SD of about 2.56 is d about 0.20; 80 percent power needs about 209 participants; at 24 participants power is about 0.15, at 40 roughly 0.2
- Session arithmetic (estimate, 2026-10-14): welcome and consent 5 min; instructions 3 min; per keyboard: 5 practice phrases about 1.5 min, 20 scored phrases at about 9 s (tap) to 15 s (swipe, novice) per phrase including reading, so 3 to 5 min, then the ease rating 1 min; break between keyboards 2 min; debriefing 3 min. Total about 28 to 32 min, within a 40-minute slot.
--- Open items
1. Provisional power parameters (item 8.6): tap intercept 33 WPM, participant intercept SD 8, participant keyboard slope SD 5, residual SD 6 per phrase (hci-researcher memory estimates, not confirmed; the pilot or lit-search replaces them and the count is rerun)
2. Item 2.4 provisional, recommendation: IRB now, approval about 3 weeks, pilot the week after, collection 3 weeks, analysis 2 weeks, write-up 2 weeks; about 11 weeks. The user has not set a deadline.
3. Run `/experiment-proposal:lit-search` for the two swipe-keyboard studies that source H1's direction (swipe faster for novices) and for a published tap-condition error baseline to fix the H2 log-odds bound; also to verify the first-session evidence under Looked up that points the other way.
4. Run `/experiment-proposal:the-ethics-board` with the consent story and data path from items 1.2, 1.3 and 12.3.
--- Amendments
(absent)
--- 8.5
### 8.5 Participant count
- Decision: 40 participants (20 per keyboard order). Governing run: 1000 simulations, alpha 0.025, seed 20261013, 20 phrases per keyboard, H1 effect 3 WPM: power 0.88 (95 percent CI 0.86 to 0.90) at n = 40; 0.94 (0.92 to 0.95) at n = 48. Search (200 simulations, same settings, full grid): n = 12, 0.28; 16, 0.43; 20, 0.56; 24, 0.64; 32, 0.79; 40, 0.87; 48, 0.92. The count is the smallest grid value meeting 0.80 for the primary measure. The pilot refines the trials per condition (item 2.2) and the residual and slope SDs; the count is rerun if the pilot's values differ. H2 is not powered at this count: at the 2-percentage-point equivalence bound the analytic TOST estimate needs about 337 participants (Looked up); H2 is preregistered with that limitation stated. RQ1 is exploratory: at 40 participants a 0.5 latent-logit effect has power of roughly 0.2 by the analytic paired estimate. Simplifications for the power run: only the WPM model simulated; by-phrase random terms (item 11.6) dropped; treatment coding with tap as reference, which gives the same swipe-minus-tap coefficient as the sum coding of item 11.5.
- Rationale: accepted recommendation: section 6 of the design skill; target power 0.80, alpha 0.025 (worst-case Holm, item 11.9), parameters P1 to P10 accepted as worded, with P1 option (b): "Yes to every question, P1 to P10, accepting each recommendation as you worded it (for P1, option b)."
- Would change if: the pilot's residual SD, slope SD or trials per condition differ from the assumed 6, 5 and 20; or item 6.6's H2 bound is amended, which would let H2 be powered.
- Status: settled
- Source: proposal/power.R, run 2026-10-14
```

## `proposal/power.R` PARAMETERS block (final state)

```r
params <- list(
  seed = 20261013,
  n_sims = 1000,           # governing run; the 200-simulation search used c(12, 16, 20, 24, 32, 40, 48)
  alpha = 0.025,           # worst-case Holm threshold for H1 among two confirmatory tests (item 11.9)
  target_power = 0.80,
  # Participant counts to try. Keep every value a multiple of the number of
  # between-subjects groups and of the number of counterbalanced orders.
  n_grid = c(40, 48),      # the count chosen by the search and the next grid value
  trials_per_condition = 20,   # item 2.2 working value; the pilot refines it
  # Within-subjects factors (every participant sees every level) and
  # between-subjects factors (equal groups, assigned round-robin): name = levels.
  within = list(keyboard = c("tap", "swipe")),
  between = list(),
  # One entry per dependent variable. The FIRST entry is the primary measure and
  # sets the participant count; every other model's power is reported at that count.
  #   dv       the measure's name
  #   family   "lmer" (continuous), "glmer" (trial-level 0/1), "clmm" (ordinal rating)
  #   formula  fixed effects as in the brief + one random-effects term by participant;
  #            the clmm loop supports a random intercept only, (1 | participant)
  #   test     the coefficient the hypothesis rests on, named as R's model matrix
  #            names it (factor name followed by the level, e.g. devicetrackball)
  #   fixef    every fixed-effect coefficient, named, on the model's scale:
  #            lmer in the measure's units; glmer on the logit scale; clmm on the
  #            latent logit scale and WITHOUT an intercept (thresholds replace it)
  #   sd_participant   SDs of the random-effect terms, in the order the formula
  #            lists them (intercept first, then each slope)
  #   sigma    residual SD (lmer only)
  #   thresholds   the K-1 cut points of a K-category rating (clmm only)
  #
  # Only the primary measure is simulated. The error model (H2, equivalence by
  # TOST at a 2-percentage-point bound) and the ease rating (RQ1, one rating per
  # participant per keyboard) are excluded: the template tests a coefficient
  # against zero and simulates trials_per_condition observations per cell, so
  # neither would represent its hypothesis. Analytic estimates for both are
  # recorded in the design brief (items 8.5 and 8.7).
  # Random effects: the brief's by-phrase terms (item 11.6) are dropped here
  # because the template supports one by-participant term.
  # Coding: treatment contrast with tap as reference; keyboardswipe is swipe minus
  # tap, the same quantity as the brief's sum-coded coefficient (item 11.5).
  models = list(
    list(
      dv = "wpm",
      family = "lmer",
      formula = y ~ keyboard + (1 + keyboard | participant),
      test = "keyboardswipe",
      fixef = c("(Intercept)" = 33, "keyboardswipe" = 3),   # 3 WPM = SESOI (item 6.6)
      sd_participant = c(8, 5),                             # intercept SD, slope SD
      sigma = 6
    )
  )
)

## ---- END OF PARAMETERS ----
```

## `git log --oneline` in the scratch project

```text
6876ef6 Freeze the design brief
63c8743 init
```
