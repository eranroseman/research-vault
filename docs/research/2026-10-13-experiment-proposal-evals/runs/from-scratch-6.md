# Scenario 3, from scratch, run 6 (re-run at plugin commit 3893203)

Date: 2026-10-14. Plugin commit: 3893203. Scenario label: from-scratch. Driver: headless `claude -p` turns answered strictly from `fixtures/from-scratch-answers.md` (the plan calls this scenario interactive; the author delegated it). No turn cap: turns were sent until the brief was frozen. R 4.3.3 with lme4, lmerTest, ordinal and simr was installed; no shim. The three runs ran at the same time on one machine, so R wall times include contention. Records `from-scratch-1.md` to `-3.md` are the earlier failed attempt at commit 6bb6ed7 and are not changed.

Verdict: PASS. Every bar is met: all items settled, 2.4 provisional, 2.2 pilot settles, the count (16) is computed and recorded, the output table has an `ease` row from the clmm loop, the hci-researcher was consulted (five Agent calls), and the freeze commit exists. The rating's power is low (0.09 at n = 16), recorded as a finding.

## Turns

| Turn | Command (flags as in turn 1 on every turn)                                                                                                                           | Wall time |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 1    | `timeout 5400 claude -p "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"`            | 104 s     |
| 2    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 41 s      |
| 3    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 119 s     |
| 4    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 148 s     |
| 5    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 57 s      |
| 6    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 135 s     |
| 7    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 29 s      |
| 8    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 28 s      |
| 9    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 43 s      |
| 10   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 193 s     |
| 11   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 1516 s    |
| 12   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 21 s      |

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
Item 6.7 (H2 part, or your note on H2): Yes, your equivalence (TOST) reading for H2 is right; the nearest sheet row is 6.6, H2 tested by TOST. H1 and RQ1 keep the rule I gave.
Item 2.3: Four people from the lab; it refines the phrases per keyboard (recorded under 2.2) and the script timings; its data will not be reported.
Item 11.6: Yes to the hci-researcher's recommendation as you state it (the random-effects structure and drop order you give).
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
Yes to every question, P1 to the last, accepting each recommendation as you worded it. Keep all three models (never drop the rating or the error model), and the rating has 1 observation per participant per condition.
```

Turn 11:

```text
Yes, run proposal/power.R.
```

Turn 12:

```text
Freeze as is: keep the 2 percentage point H2 bound (item 6.6 stands as I gave it). I approve the brief. OK to freeze.
```

Turns and rounds: 12 turns. Turn 1 asked round 1; turns 2 to 8 answered rounds 1 to 7; turn 9 answered round 8 and the session asked the power batch (P1 to P8); turn 10 answered it (block shown, 193 s); turn 11 said "Yes, run proposal/power.R." and the session ran both the 200-simulation search and the 1000-simulation confirmation inside that one turn (1516 s); turn 12 approved and froze. No "Is the power run finished? Continue." turn was needed.

Consistency questions raised and answered from the sheet: turn 4 reply, the note that item 7.9 held only the sheet's three preventions (answered by continuing; the sheet's row 7.9 stands); turn 6 reply, H2's decision rule re-asked as TOST (answered yes, row 6.6); turn 11 reply, "keep the 2-point bound or widen": "Freeze as is: keep the 2 percentage point H2 bound (item 6.6 stands as I gave it)" (row 6.6).

## Transcript, decisive lines

- Turn 1: R prerequisite check passed.
- hci-researcher: five Agent calls (7.7, 7.9, 6.6, 7.5, 11.6). Turn 3: "Both consults done." Turn 4 reply: "Item 7.9 holds only your three preventions. hci-researcher also flagged demand characteristics, novelty of swipe ... Those are not in the entry".
- Turn 9, the P batch: "**P3 (trials per condition).** 20 phrases per keyboard, from item 2.2's working value; 1 rating per keyboard for the ease model?" and "**P7 (ease model).** `clmm` ... one rating per keyboard?" Turn 10 answer: "Yes to every question, P1 to the last, accepting each recommendation as you worded it. Keep all three models (never drop the rating or the error model), and the rating has 1 observation per participant per condition."
- Turn 10: the `cp` of the template was refused; `proposal/power.R` was written with Write after reading the template. The ease model carries `trials = 1`. "Run time: 15 to 30 minutes at 200 simulations over the 8-value grid with three models ... and about as long again for the 1000-simulation confirmation."
- Turn 11, how R ran and how the session waited: a first form `Rscript proposal/power.R > proposal/power-200.log 2>&1; echo "exit=$?" >> ...` was refused as compound; the session ran `Rscript proposal/power.R` with `run_in_background: true` and then a blocking `TaskOutput` (`block: true`, `timeout: 600000`) in the same turn; the first call timed out after 10 minutes and a second blocking call returned when the run finished. The 1000-simulation confirmation (`n_grid = c(16, 20)`) was run the same way: blocking call, a second call after the 10-minute timeout. The turn never ended while R ran; no background run was killed at a turn's end.
- Wall times (start of the Bash call to the session reading the finished output, UTC; the actual finish is no later): 200-simulation search over the 8-value grid, 17:49:15 to 18:00:25, at most 11.2 min; 1000-simulation confirmation over n = 16 and 20, 18:00:33 to 18:11:34, at most 11.0 min.
- Turn 11 end: "Count: 16 participants, 8 per order." Table: wpm 0.84 and 0.94; any_error 0.04 and 0.05; ease 0.09 and 0.11 at n = 16 and 20. "RQ1 is also underpowered at 16 (0.09); not a hypothesis, no decision rule hangs on it, but reviewer may ask."
- Turn 12 end: "Brief frozen. Commit `03697c2`, "Freeze the design brief", holds `proposal/design-brief.md` (Status: frozen 2026-10-14) and `proposal/power.R`."

## Power output and the excluded-fit lines

200-simulation search over the full grid:

```text
ease: 35 of 200 clmm fits failed at n = 12 and were excluded
ease: 21 of 200 clmm fits failed at n = 16 and were excluded
ease: 19 of 200 clmm fits failed at n = 20 and were excluded
ease: 11 of 200 clmm fits failed at n = 24 and were excluded
ease: 15 of 200 clmm fits failed at n = 32 and were excluded
ease: 8 of 200 clmm fits failed at n = 40 and were excluded
ease: 5 of 200 clmm fits failed at n = 48 and were excluded
ease: 2 of 200 clmm fits failed at n = 64 and were excluded
## Power curve (200 simulations per point, alpha = 0.025, seed 20261013)
| Measure | n | Power | 95% CI |
| --- | --- | --- | --- |
| wpm | 12 | 0.70 | 0.64 to 0.77 |
| wpm | 16 | 0.88 | 0.82 to 0.92 |
| wpm | 20 | 0.95 | 0.91 to 0.98 |
| wpm | 24 | 0.98 | 0.95 to 0.99 |
| wpm | 32 | 1.00 | 0.98 to 1.00 |
| wpm | 40 | 1.00 | 0.98 to 1.00 |
| wpm | 48 | 1.00 | 0.98 to 1.00 |
| wpm | 64 | 1.00 | 0.98 to 1.00 |
| any_error | 12 | 0.04 | 0.02 to 0.08 |
| any_error | 16 | 0.04 | 0.02 to 0.08 |
| any_error | 20 | 0.06 | 0.03 to 0.10 |
| any_error | 24 | 0.04 | 0.02 to 0.08 |
| any_error | 32 | 0.05 | 0.02 to 0.09 |
| any_error | 40 | 0.07 | 0.04 to 0.11 |
| any_error | 48 | 0.06 | 0.03 to 0.10 |
| any_error | 64 | 0.07 | 0.04 to 0.12 |
| ease | 12 | 0.10 | 0.06 to 0.15 |
| ease | 16 | 0.09 | 0.05 to 0.14 |
| ease | 20 | 0.10 | 0.06 to 0.16 |
| ease | 24 | 0.14 | 0.09 to 0.20 |
| ease | 32 | 0.14 | 0.09 to 0.19 |
| ease | 40 | 0.14 | 0.09 to 0.19 |
| ease | 48 | 0.18 | 0.13 to 0.24 |
| ease | 64 | 0.26 | 0.20 to 0.33 |
Primary measure: wpm
Participant count: 16 (the smallest grid value with power >= 0.80 for wpm)
At n = 16, any_error: power 0.04 (0.02 to 0.08)
At n = 16, ease: power 0.09 (0.05 to 0.14)
```

1000-simulation confirmation, n_grid = 16 and 20:

```text
ease: 119 of 1000 clmm fits failed at n = 16 and were excluded
ease: 96 of 1000 clmm fits failed at n = 20 and were excluded
## Power curve (1000 simulations per point, alpha = 0.025, seed 20261013)
| Measure | n | Power | 95% CI |
| --- | --- | --- | --- |
| wpm | 16 | 0.84 | 0.81 to 0.86 |
| wpm | 20 | 0.94 | 0.92 to 0.95 |
| any_error | 16 | 0.04 | 0.03 to 0.06 |
| any_error | 20 | 0.05 | 0.03 to 0.06 |
| ease | 16 | 0.09 | 0.07 to 0.11 |
| ease | 20 | 0.11 | 0.09 to 0.13 |
Primary measure: wpm
Participant count: 16 (the smallest grid value with power >= 0.80 for wpm)
At n = 16, any_error: power 0.04 (0.03 to 0.06)
At n = 16, ease: power 0.09 (0.07 to 0.11)
```

Rating power is low: 0.09 at n = 16 and 0.11 at n = 20 in the 1000-simulation run (0.09 to 0.26 over the search grid). Failed clmm fits were excluded and counted: 35 of 200 at n = 12 down to 2 of 200 at n = 64 in the search; 119 of 1000 at n = 16 and 96 of 1000 at n = 20 in the confirmation, so about 12 percent and 10 percent of the rating fits were dropped there.

## Pass bar

| Criterion                                                    | Result | Evidence                                                                                                                      |
| ------------------------------------------------------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------- |
| Every design-tree item settled, provisional or pilot settles | PASS   | 31 entries: `settled` except 2.2 `pilot settles` and 2.4 `provisional`; 8.5, 8.6, 8.7 `settled`; `Status: frozen 2026-10-14`. |
| 2.4 provisional, 2.2 pilot settles                           | PASS   | Both statuses as above.                                                                                                       |
| Mixed-model plan complete (11.2, 11.4 to 11.9)               | PASS   | All `settled`.                                                                                                                |
| Power computed, `proposal/power.R` run, count recorded       | PASS   | Count 16 from the 1000-simulation run; 8.5 `Source: proposal/power.R, run 2026-10-14`.                                        |
| Rating's power through the clmm loop, a `rating` row         | PASS   | `ease` rows in both tables, with the excluded-fit lines.                                                                      |
| hci-researcher consulted at least once                       | PASS   | Five Agent calls.                                                                                                             |
| Freeze commit exists                                         | PASS   | `03697c2 Freeze the design brief`.                                                                                            |

## Verdict

PASS. Observations: (1) the session waited inside the turn with blocking `TaskOutput` calls; nothing was killed. (2) Item 8.7's entry reports the curve over participant counts at the assumed effects only ("No sensitivity run over alternative effect sizes was made"), not a range of effect sizes; the entry is `settled`. Section 6 step 5 says only that 8.7's entry "holds the range". (3) The H2 power is at alpha on the grid (0.07 at n = 64).

## Brief (final state in the scratch project; Looked up entries trimmed to the sections asked for)

```text
--- HEADER
# Design brief: swipe keyboard versus tap typing for novice smartphone users

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
6.2 Hypothesis details | settled
6.5 Interaction hypotheses | settled
6.6 Smallest effect size of interest | settled
6.7 Decision rules | settled
7.1 Independent variable | settled
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
8.7 Range reported | settled
11.2 Unit of analysis | settled
11.4 Model family | settled
11.5 Fixed effects and contrasts | settled
11.6 Random effects | settled
11.7 Inference method | settled
11.8 Exclusions and trimming | settled
11.9 Significance level and multiplicity | settled
--- Looked up
- Standard phrase set for text entry evaluation: MacKenzie, I. S. and Soukoreff, R. W. (2003), "Phrase sets for evaluating text entry techniques", CHI 2003 Extended Abstracts; 500 phrases, no punctuation, lowercase, mean 28.6 characters (recalled 2026-10-14; lit-search to confirm)
- Words per minute convention: (transcribed characters − 1) / 5 / minutes, time from first to last keystroke (MacKenzie, "A note on calculating text entry speed", 2002; recalled 2026-10-14)
- Error metric convention: minimum string distance error rate and keystrokes per character, Soukoreff and MacKenzie (2003), "Metrics for text entry research", CHI 2003 (recalled 2026-10-14)
- Direction evidence: Reyal, Zhai and Kristensson (2015), "Performance and user experience of touchscreen and gesture keyboards in a lab setting and in the wild", CHI 2015, reported gesture (swipe) typing comparable to or faster than tap typing with lower correction effort in the lab (recalled 2026-10-14; lit-search to confirm figures)

- R prerequisite check (lme4, lmerTest, ordinal, simr): passed (Rscript run in the project, 2026-10-14)
- Git repository: present at the project root (git rev-parse, 2026-10-14)

- hci-researcher consult, item 7.7 (controls) and item 7.9 (confounds): seven controls and eight confounds recommended; recorded in those entries' recommendations (2026-10-14)
- hci-researcher consult, item 6.6 (smallest effects of interest; web search unavailable to it, figures recalled): H1 +3 words per minute on a 20 to 25 WPM novice tap baseline (judgment; Reyal, Zhai and Kristensson 2015 found first-session gesture entry on par with or slightly below touch, gains only after practice); H2 non-inferiority bound +0.4 log-odds (odds ratio 1.5) on per-phrase any-error probability, baseline about 0.35 per phrase (1 − 0.985^28.6, from a 1 to 2% per-character uncorrected error rate); RQ1 0.8 on the latent logit scale (about 0.4 to 0.5 rating points mid-scale). Simulation inputs, all judgment: WPM participant SD 5, residual SD 4, participant by keyboard slope SD 3; errors random intercept SD 0.8 logit, slope SD 0.5; 7-point ease thresholds −3.5, −2.5, −1.5, −0.5, 0.7, 2.0 (2026-10-14)
- hci-researcher consult, item 7.5 (counterbalancing): two orders (tap then swipe, swipe then tap), crossed with two fixed phrase halves of matched mean length assigned to the keyboards, giving four cells; block randomisation in blocks of 4 from an allocation list generated once with R `sample()` and a recorded seed; participant count a multiple of 4 (2 without the phrase crossing); order as a fixed effect in the models (2026-10-14)

- H2 bound in log-odds: 2 percentage points at a 0.35 baseline is logit(0.37) − logit(0.35) = −0.532 − (−0.619) ≈ 0.087 log-odds (computed 2026-10-14)
- Session arithmetic: a 28.6-character phrase is about 5.7 words, about 17 s at 20 WPM, about 25 s with reading and the next-phrase tap; 20 phrases per keyboard ≈ 8 min, 5 practice phrases ≈ 2 min, so about 10 min per keyboard and 20 min of tasks; welcome and consent 5 min, instructions 3 min, break 2 min, two ratings 2 min, debriefing 3 min; total about 35 min (computed 2026-10-14)

- hci-researcher consult, item 11.6 (random effects): fix one seeded random draw of 20 phrases for all participants so phrase random effects are identifiable (a fresh draw per participant leaves about two observations per phrase); WPM and error models maximal `y ~ kb + (1 + kb | participant) + (1 + kb | phrase)`, drop order on singular fit or allFit disagreement: correlations, phrase slope, phrase intercept, participant slope, participant intercept never dropped; glmer with nAGQ = 1 and bobyqa; clmm `(1 | participant)` only, with a paired Wilcoxon signed-rank test as the non-convergence fallback; simplify only on isSingular or allFit disagreement, not a lone convergence warning (Barr 2013; Bates 2015; Matuschek 2017) (2026-10-14)

- Power batch, accepted by the user 2026-10-14: target power 0.80; alpha 0.025 (Holm worst case over the two confirmatory tests of item 11.9); 20 phrases per keyboard, 1 rating per keyboard; tap baseline 22 WPM (middle of the 20 to 25 novice range, hci-researcher); baseline per-phrase any-error rate 0.35; ease participant intercept SD 1.0 (template default, judgment); participant grid 12, 16, 20, 24, 32, 40, 48, 64 (multiples of the 2 orders)
--- Open items
1. Item 2.4 provisional, recommendation: ten weeks from IRB submission (3 review, 1 pilot, 3 collection, 1 analysis, 2 write-up); the user has not set a deadline
2. Run `/experiment-proposal:lit-search` for prior swipe-versus-tap text entry studies with novice users, to source the hypothesis direction (item 6.2), the first-session words per minute and error baselines and SDs (items 6.6 and 8.6), and the two swipe-keyboard studies item 6.2 cites
3. Run `/experiment-proposal:the-ethics-board` with the consent story and data path from items 1.2, 1.3 and 12.3
--- Amendments
(absent)
--- 8.5
### 8.5 Participant count
- Decision: 16 participants, 8 per keyboard order, the smallest grid value at which the primary measure (words per minute) reaches power 0.80 at alpha 0.025 for a 3 WPM effect. Governing run, 1000 simulations, 2026-10-14: WPM power 0.84 (95% CI 0.81 to 0.86) at n = 16, 0.94 (0.92 to 0.95) at n = 20. At n = 16 the other models: any_error 0.04 (0.03 to 0.06), ease 0.09 (0.07 to 0.11). Search run, 200 simulations over the full grid, 2026-10-14:

  | Measure | n | Power | 95% CI |
  | --- | --- | --- | --- |
  | wpm | 12 | 0.70 | 0.64 to 0.77 |
  | wpm | 16 | 0.88 | 0.82 to 0.92 |
  | wpm | 20 | 0.95 | 0.91 to 0.98 |
  | wpm | 24 | 0.98 | 0.95 to 0.99 |
  | wpm | 32 | 1.00 | 0.98 to 1.00 |
  | wpm | 40 | 1.00 | 0.98 to 1.00 |
  | wpm | 48 | 1.00 | 0.98 to 1.00 |
  | wpm | 64 | 1.00 | 0.98 to 1.00 |
  | any_error | 12 | 0.04 | 0.02 to 0.08 |
  | any_error | 16 | 0.04 | 0.02 to 0.08 |
  | any_error | 20 | 0.06 | 0.03 to 0.10 |
  | any_error | 24 | 0.04 | 0.02 to 0.08 |
  | any_error | 32 | 0.05 | 0.02 to 0.09 |
  | any_error | 40 | 0.07 | 0.04 to 0.11 |
  | any_error | 48 | 0.06 | 0.03 to 0.10 |
  | any_error | 64 | 0.07 | 0.04 to 0.12 |
  | ease | 12 | 0.10 | 0.06 to 0.15 |
  | ease | 16 | 0.09 | 0.05 to 0.14 |
  | ease | 20 | 0.10 | 0.06 to 0.16 |
  | ease | 24 | 0.14 | 0.09 to 0.20 |
  | ease | 32 | 0.14 | 0.09 to 0.19 |
  | ease | 40 | 0.14 | 0.09 to 0.19 |
  | ease | 48 | 0.18 | 0.13 to 0.24 |
  | ease | 64 | 0.26 | 0.20 to 0.33 |

  Assumed values: target power 0.80; alpha 0.025 (Holm worst case, item 11.9); 20 phrases per keyboard, 1 rating per keyboard; WPM intercept 22, effect 3, participant intercept SD 5, slope SD 3, residual SD 4; any_error baseline 0.35, simulated effect 0.087 log-odds (the H2 bound), participant intercept SD 0.8, slope SD 0.5; ease effect 0.5 latent, participant SD 1.0, thresholds −3.5, −2.5, −1.5, −0.5, 0.7, 2.0. Simplifications for the power run only: phrase random effects (item 11.6) dropped, one random term by participant; the error model tests a difference at the bound, a stand-in for TOST power at a true zero effect, slightly optimistic; treatment coding in place of item 11.5's sum coding, the same test for two levels; the clmm run used `(1 | participant)` as item 11.6 already specifies, with 119 of 1000 fits at n = 16 failing and excluded. Consequence: at n = 16, H2's equivalence test and RQ1 are far below 0.80; H2's 2-point bound is not reachable on this grid (power 0.07 at n = 64), so H2 is expected to come out inconclusive unless the bound is widened. The pilot refines the count only through the phrase count (item 2.2): if the pilot sets fewer than 20 phrases per keyboard, the run is repeated with that count before pre-registration.
- Rationale: accepted recommendation: smallest grid value with power at or above 0.80 for the primary measure (section 6 of the design skill); power parameters accepted by the user, "Yes to every question, P1 to the last, accepting each recommendation as you worded it. Keep all three models (never drop the rating or the error model), and the rating has 1 observation per participant per condition."
- Would change if: item 6.6 changed (a wider H2 bound, or a different SESOI), the pilot's SDs differed, or the user wanted H2 or RQ1 powered rather than the primary alone.
- Status: settled
- Source: proposal/power.R, run 2026-10-14
--- 8.6
### 8.6 Effect size assumed
- Decision: The smallest effect size of interest of item 6.6, first in the sourcing ranking: 3 WPM for H1, 0.087 log-odds (2 percentage points at a 0.35 baseline) for H2, 0.5 latent for RQ1. The SDs and baselines are the hci-researcher's judgment informed by Reyal, Zhai and Kristensson (2015) and gesture-keyboard lab studies, recalled, not re-verified; their imprecision is unquantified and the run is not corrected for it. No pilot or prior study of this exact measure and design was used; lit-search (Open items) should replace the recalled values with published first-session figures before pre-registration.
- Rationale: accepted recommendation: item 8.6's ranking puts the smallest effect of interest first; the user accepted the batch values as worded.
- Would change if: lit-search or the pilot gave different baselines or SDs.
- Status: settled
- Source: user, power batch; hci-researcher consult 2026-10-14
--- 8.7
### 8.7 Range reported
- Decision: The count is read off the search curve above, which varies the participant count from 12 to 64 at the assumed effects, not the effect size; the curve reports all three measures at every grid value. The committed count, 16, is read at the 3 WPM effect. No sensitivity run over alternative effect sizes was made; the curve shows that H1 is powered at 0.70 at n = 12 and 0.94 at n = 20, so a true effect somewhat below 3 WPM would be caught by the next grid value.
- Rationale: accepted recommendation: the template's power curve over the participant grid (section 6 of the design skill).
- Would change if: the user asked for a curve over effect sizes (for example 2, 3, 4 WPM) at n = 16.
- Status: settled
- Source: proposal/power.R, run 2026-10-14
```

## `proposal/power.R` PARAMETERS block (final state, the 1000-simulation governing configuration)

```r
params <- list(
  seed = 20261013,
  n_sims = 1000,           # simulations per participant count; use 1000 for the final run
  alpha = 0.025,           # Holm worst case over the two confirmatory tests (item 11.9)
  target_power = 0.80,
  # Participant counts to try. Keep every value a multiple of the number of
  # between-subjects groups and of the number of counterbalanced orders.
  # Search grid (200 simulations, run 2026-10-14): c(12, 16, 20, 24, 32, 40, 48, 64); the
  # 1000-simulation confirmation runs on the chosen count and the next grid value.
  n_grid = c(16, 20),   # multiples of 2 orders (item 7.5)
  trials_per_condition = 20,                     # phrases per keyboard, item 2.2 working value
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
  #   trials   observations per participant per condition for this model; defaults
  #            to trials_per_condition; 1 for a once-per-condition questionnaire rating
  #
  # Simplifications for the power run only (recorded in the design brief, items 8.5 to 8.7):
  #   the phrase random effects of item 11.6 are dropped (the template supports one
  #   random term, by participant); the error model simulates a true effect equal to
  #   the H2 equivalence bound and tests it as a difference, which approximates TOST
  #   power at a true zero effect; treatment coding stands in for the sum coding of
  #   item 11.5, the same test for a two-level factor.
  models = list(
    list(
      dv = "wpm",
      family = "lmer",
      formula = y ~ keyboard + (1 + keyboard | participant),
      test = "keyboardswipe",
      fixef = c("(Intercept)" = 22, "keyboardswipe" = 3),   # tap baseline 22 WPM; SESOI 3 WPM (item 6.6)
      sd_participant = c(5, 3),
      sigma = 4
    ),
    list(
      dv = "any_error",
      family = "glmer",
      formula = y ~ keyboard + (1 + keyboard | participant),
      test = "keyboardswipe",
      fixef = c("(Intercept)" = qlogis(0.35),
                "keyboardswipe" = qlogis(0.37) - qlogis(0.35)),   # 2-point bound at the 0.35 baseline, about 0.087 log-odds
      sd_participant = c(0.8, 0.5)
    ),
    list(
      dv = "ease",
      family = "clmm",
      formula = y ~ keyboard + (1 | participant),
      test = "keyboardswipe",
      fixef = c("keyboardswipe" = 0.5),   # SESOI 0.5 on the latent scale (item 6.6)
      sd_participant = c(1.0),
      thresholds = c(-3.5, -2.5, -1.5, -0.5, 0.7, 2.0),
      trials = 1
    )
  )
)

## ---- END OF PARAMETERS ----
```

## `git log --oneline` in the scratch project

```text
03697c2 Freeze the design brief
f3bab3c init
```
