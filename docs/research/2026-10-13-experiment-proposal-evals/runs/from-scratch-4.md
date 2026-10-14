# Scenario 3, from scratch, run 4 (re-run at plugin commit 3893203)

Date: 2026-10-14. Plugin commit: 3893203. Scenario label: from-scratch. Driver: headless `claude -p` turns answered strictly from `fixtures/from-scratch-answers.md` (the plan calls this scenario interactive; the author delegated it). No turn cap: turns were sent until the brief was frozen. R 4.3.3 with lme4, lmerTest, ordinal and simr was installed; no shim. The three runs ran at the same time on one machine, so R wall times include contention. Records `from-scratch-1.md` to `-3.md` are the earlier failed attempt at commit 6bb6ed7 and are not changed.

Verdict: PASS. Every bar is met: all items settled, 2.4 provisional, 2.2 pilot settles, the count (40) is computed and recorded, the output table has an `ease_rating` row from the clmm loop, the hci-researcher was consulted (five Agent calls), and the freeze commit exists. The rating's power is low (0.14 at n = 40), recorded as a finding.

## Turns

| Turn | Command (flags as in turn 1 on every turn)                                                                                                                           | Wall time |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 1    | `timeout 5400 claude -p "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"`            | 99 s      |
| 2    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 34 s      |
| 3    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 167 s     |
| 4    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 153 s     |
| 5    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 71 s      |
| 6    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 133 s     |
| 7    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 29 s      |
| 8    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 27 s      |
| 9    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 145 s     |
| 10   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 73 s      |
| 11   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 1817 s    |
| 12   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 694 s     |

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
Your side question in item 7.7 (tap with autocorrect and suggestions on or off): I don't know.
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
Your flag on H1 (run 4 only): keep H1 directional, swipe faster (item 6.1 stands).
```

Turn 6:

```text
Answers for round 5, by item (Q order is 2.2, 6.7, 11.5):
Item 2.2 (Q1): The pilot will decide the phrases per keyboard; 20 is the working value; two conditions, about 40 minutes.
Item 6.7 (Q2): Support if the 95% interval excludes zero in the predicted direction and the point estimate is at least the SESOI; falsify if it excludes the SESOI; otherwise inconclusive.
Item 11.5 (Q3): Keyboard as the only fixed effect in the confirmatory models, sum-coded (tap -0.5, swipe +0.5), not treatment-coded; H1 and H2 map to the keyboard coefficient; no order term, since order is counterbalanced (an order term only in a sensitivity check).
Run 4 contradiction (items 7.6 and 11.4): choose (a). The sheet's item 11.4 names three models (lmer for words per minute, glmer for the per-phrase error indicator, clmm for the rating), so the continuous error rate is a descriptive measure and the per-phrase indicator is the error DV for H2.
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
Q1 (item 6.6): keep the 2 percentage point H2 bound; item 6.6 stands as I gave it (not 10 points). Q2 (item 8.7): yes, report the curve; yes to the sweep, with H2 at the 2 point bound. Q3: I approve the brief once the sweep is recorded; OK to freeze then.
```

Turns and rounds: 12 turns. Turn 1 asked round 1; turns 2 to 8 answered rounds 1 to 7; turn 9 answered round 8 and the session ran the power-batch (P1 to P6) in its reply; turn 10 answered the batch (the template was read and `proposal/power.R` written, block shown); turn 11 said "Yes, run proposal/power.R." and the session ran both the 200-simulation search and the 1000-simulation confirmation inside that one turn (1817 s); turn 12 answered the three questions raised at the end of turn 11, and the session ran the item 8.7 sweep and froze. No "Is the power run finished? Continue." turn was needed.

Consistency questions raised by the session and how they were answered from the sheet: turn 3 reply, tap autocorrect on or off (a side question inside item 7.7, not on the sheet): "I don't know" (recorded as a provisional item under Open items); turn 4 reply, whether H1 stays directional given the recalled Reyal et al. finding: "keep H1 directional, swipe faster" (item 6.1); turn 5 reply, the contradiction between item 7.6 (four dependent variables, including the continuous uncorrected error rate) and item 11.4 (three models): answered (a), the continuous rate descriptive, from the sheet's row 11.4 (lmer, glmer, clmm); turn 6 reply, its reading of H2's decision rule as TOST: yes, nearest row 6.6. Turn 11 reply, Q1 widen the H2 bound to 10 points: kept the 2 point bound (row 6.6); Q2 the effect-size sweep: yes (row 8.7, report the curve); Q3 approval: given once the sweep was recorded, with "OK to freeze then".

## Transcript, decisive lines

- Turn 1: "Prerequisites ..." check run with `Rscript -e 'for (p in c("lme4","lmerTest","ordinal","simr")) ...'`; passed.
- hci-researcher: five Agent calls (items 7.7, 7.9, 6.6, 7.5, 11.6). Turn 3: "Subagent answered on controls and confounds." Turn 4: "Subagents answered on effect sizes and counterbalancing."
- Turn 5, item 7.6 and 11.4: "**Contradiction, items 7.6 and 11.4.** Item 7.6 lists four dependent variables, including the continuous uncorrected error rate. Item 11.4 gives models for three. Power run rule: one model per dependent variable of 7.6, never fewer. One entry must change." It recorded 7.6 as amended so that the error rate is descriptive and three dependent variables are modelled.
- Turn 9, the P batch: "Settled already and not asked: trials per condition 20 (item 2.2 working value), rating once per keyboard, ...". "**P5, ease rating model values** (clmm) ... ceiling at 7 is the main threat to detecting a swipe effect." Turn 10 answer: "Yes to every question, P1 to the last, accepting each recommendation as you worded it. Keep all three models (never drop the rating or the error model), and the rating has 1 observation per participant per condition."
- Turn 10: the `cp` of the template was refused ("a sensitive file"); the session wrote `proposal/power.R` with Write after reading the template. The reply: "`proposal/power.R` written, template copy with only the PARAMETERS block filled." The ease model carries `trials = 1`. "Run takes 10 to 20 minutes at 200 simulations over the full grid with three models, then about as long again for the 1000-simulation confirmation".
- Turn 11, how R ran and how the session waited: `Rscript proposal/power.R > proposal/power-200.log 2>&1` with `run_in_background: true`, then a blocking `TaskOutput` call (`block: true`, `timeout: 600000`) inside the same turn; the log was read when the call returned. The 1000-simulation confirmation was started the same way (`n_sims = 1000`, `n_grid = c(40, 48)`); the first `TaskOutput` call timed out after 10 minutes and the session issued another blocking call, then read the log. The turn never ended while R ran; no background run was killed at a turn's end.
- Wall times (start of the Bash call to the session reading the finished log, UTC; the actual finish is no later): 200-simulation search over the 6-value grid, 17:49:12 to 17:58:45, at most 9.5 min; 1000-simulation confirmation over n = 40 and 48, 17:58:54 to 18:16:33, at most 17.6 min (the first blocking wait timed out at 18:09). The sweep in turn 12: three concurrent 200-simulation full-grid copies of the script, started 18:20:04 to 18:20:08, finished before the turn ended at about 18:31, at most about 11 min.
- Turn 11 end: "Count: 40 participants, 20 per order. Search curve over 16 to 64 is in item 8.7." Governing run 1000 simulations: wpm 0.88 at n = 40, 0.94 at 48; error indicator 0.07 and 0.08; ease rating 0.14 and 0.17.
- Turn 12 end: "Commit `af5f271` "Freeze the design brief" holds `proposal/design-brief.md` (Status: frozen 2026-10-14) and `proposal/power.R`. Working tree clean."

## Power output and the excluded-fit lines

The clmm loop's excluded-fit lines, which the script prints on stdout, are shown with each table.

200-simulation search over the full grid (read at 17:58:45 UTC):

```text
ease_rating: 30 of 200 clmm fits failed at n = 16 and were excluded
ease_rating: 13 of 200 clmm fits failed at n = 24 and were excluded
ease_rating: 15 of 200 clmm fits failed at n = 32 and were excluded
ease_rating: 10 of 200 clmm fits failed at n = 40 and were excluded
ease_rating: 5 of 200 clmm fits failed at n = 48 and were excluded
ease_rating: 2 of 200 clmm fits failed at n = 64 and were excluded
## Power curve (200 simulations per point, alpha = 0.025, seed 20261013)
| Measure | n | Power | 95% CI |
| --- | --- | --- | --- |
| words_per_minute | 16 | 0.41 | 0.34 to 0.48 |
| words_per_minute | 24 | 0.60 | 0.53 to 0.67 |
| words_per_minute | 32 | 0.77 | 0.70 to 0.82 |
| words_per_minute | 40 | 0.89 | 0.83 to 0.93 |
| words_per_minute | 48 | 0.92 | 0.87 to 0.95 |
| words_per_minute | 64 | 0.98 | 0.95 to 0.99 |
| uncorrected_error | 16 | 0.04 | 0.01 to 0.07 |
| uncorrected_error | 24 | 0.07 | 0.04 to 0.11 |
| uncorrected_error | 32 | 0.07 | 0.04 to 0.12 |
| uncorrected_error | 40 | 0.07 | 0.04 to 0.11 |
| uncorrected_error | 48 | 0.09 | 0.05 to 0.13 |
| uncorrected_error | 64 | 0.07 | 0.04 to 0.11 |
| ease_rating | 16 | 0.12 | 0.07 to 0.18 |
| ease_rating | 24 | 0.12 | 0.08 to 0.18 |
| ease_rating | 32 | 0.11 | 0.07 to 0.17 |
| ease_rating | 40 | 0.13 | 0.08 to 0.18 |
| ease_rating | 48 | 0.18 | 0.13 to 0.24 |
| ease_rating | 64 | 0.29 | 0.23 to 0.36 |
Primary measure: words_per_minute
Participant count: 40 (the smallest grid value with power >= 0.80 for words_per_minute)
At n = 40, uncorrected_error: power 0.07 (0.04 to 0.11)
At n = 40, ease_rating: power 0.13 (0.08 to 0.18)
```

1000-simulation confirmation, n_grid = 40 and 48 (read at 18:16:33 UTC):

```text
ease_rating: 36 of 1000 clmm fits failed at n = 40 and were excluded
ease_rating: 30 of 1000 clmm fits failed at n = 48 and were excluded
## Power curve (1000 simulations per point, alpha = 0.025, seed 20261013)
| Measure | n | Power | 95% CI |
| --- | --- | --- | --- |
| words_per_minute | 40 | 0.88 | 0.86 to 0.90 |
| words_per_minute | 48 | 0.94 | 0.92 to 0.95 |
| uncorrected_error | 40 | 0.07 | 0.06 to 0.09 |
| uncorrected_error | 48 | 0.08 | 0.07 to 0.10 |
| ease_rating | 40 | 0.14 | 0.12 to 0.17 |
| ease_rating | 48 | 0.17 | 0.14 to 0.19 |
Primary measure: words_per_minute
Participant count: 40 (the smallest grid value with power >= 0.80 for words_per_minute)
At n = 40, uncorrected_error: power 0.07 (0.06 to 0.09)
At n = 40, ease_rating: power 0.14 (0.12 to 0.17)
```

Rating power is low, as expected with one rating per participant per keyboard: 0.14 at n = 40 (1000 simulations), 0.12 to 0.29 over the 200-simulation grid. Clmm fits that failed were excluded and counted: 30 of 200 at n = 16 down to 2 of 200 at n = 64 in the search; 36 of 1000 at n = 40 and 30 of 1000 at n = 48 in the confirmation.

## Pass bar

| Criterion                                                    | Result | Evidence                                                                                                                          |
| ------------------------------------------------------------ | ------ | --------------------------------------------------------------------------------------------------------------------------------- |
| Every design-tree item settled, provisional or pilot settles | PASS   | 31 entries, all `settled` except 2.2 `pilot settles` and 2.4 `provisional`; 8.5, 8.6, 8.7 `settled`; `Status: frozen 2026-10-14`. |
| 2.4 provisional, 2.2 pilot settles                           | PASS   | \`2.4 Timeline                                                                                                                    |
| Mixed-model plan complete (11.2, 11.4 to 11.9)               | PASS   | All `settled`.                                                                                                                    |
| Power computed, `proposal/power.R` run, count recorded       | PASS   | Count 40 from the 1000-simulation run; 8.5 `Source: proposal/power.R, run 2026-10-14`.                                            |
| Rating's power through the clmm loop, a `rating` row         | PASS   | `ease_rating` rows in both tables (named `ease_rating`; the sheet calls the measure the rating), with the excluded-fit lines.     |
| hci-researcher consulted at least once                       | PASS   | Five Agent calls.                                                                                                                 |
| Freeze commit exists                                         | PASS   | `af5f271 Freeze the design brief`.                                                                                                |

## Verdict

PASS. Observations: (1) the new section 6 step 4 worked as written: the session waited inside the turn with a blocking `TaskOutput`, and nothing was killed. (2) The rating model stayed in the run with `trials = 1`; its power (0.14) is a finding, not a reason to drop it. (3) This run raised the 7.6 versus 11.4 count mismatch itself (four dependent variables, three models) and settled it before the power batch. (4) The H2 error model is a bound-sized-difference proxy; its power is at alpha across the grid and the baselines. (5) The session ran an item 8.7 sweep over effect sizes with three concurrent copies of the script (H1 at 2, 5, 8 WPM; RQ1 at 0.3, 0.5, 1.0; H2 baselines 0.20, 0.30, 0.45).

## Brief (final state in the scratch project; Looked up entries trimmed to the sections asked for)

```text
--- HEADER
# Design brief: Swipe versus tap keyboard for novice smartphone users

Draft: proposal/draft.md
Status: frozen 2026-10-14
Checklist: experiment-proposal 0.1.0
--- STATUSES
1.1 The question | settled
1.2 Ethics route | settled
1.3 Data plan | settled
2.2 Conditions, trials and session | pilot settles
2.3 Pilot | settled
2.4 Timeline | provisional
2.5 Expected challenges | settled
6.1 Hypotheses and research questions | settled
6.2 Hypothesis content | settled
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
8.7 Range across effect sizes | settled
11.2 Unit of analysis | settled
11.4 Model family | settled
11.5 Fixed effects and contrasts | settled
11.6 Random effects and simplification order | settled
11.7 Inference method | settled
11.8 Exclusions and trimming | settled
11.9 Significance level and multiplicity | settled
--- Looked up
- Text-entry speed and error metrics (words per minute, minimum string distance error rate, uncorrected and corrected errors): Soukoreff, R. W. and MacKenzie, I. S. (2003), "Metrics for text entry research: an evaluation of MSD and KSPC, and a new unified error metric", CHI 2003 (cited from memory, 2026-10-14)
- Standard phrase set: MacKenzie, I. S. and Soukoreff, R. W. (2003), "Phrase sets for evaluating text entry techniques", CHI 2003 Extended Abstracts, 500 phrases, mean length about 28.6 characters (cited from memory, 2026-10-14)
- Swipe versus tap, prior studies (hci-researcher, recalled, to be verified against the papers by lit-search, 2026-10-14): Reyal, Zhai and Kristensson (2015, CHI) report lab gesture-versus-touch differences of roughly 3 to 6 WPM across sessions, with gesture typing slower in early sessions and competitive only after practice; Palin, Saarelainen, Hassinen, Kristensson and Oulasvirta (2019, MobileHCI, about 37,000 users) report mean 36.2 WPM and uncorrected error rate about 2.3% per character
- H2 bound on the log-odds scale, 2 percentage points at the baseline per-phrase error proportion: 0.094 at a 0.30 baseline, 0.121 at 0.20, 0.081 at 0.45 (computed with R qlogis, 2026-10-14)
- Session arithmetic: one phrase of 28.6 characters at 30 WPM takes about 11 s to type; with reading and Enter about 20 s per phrase for a novice, slower on swipe; 20 measured phrases per keyboard is about 7 min per keyboard. Welcome and consent 5 min, instructions 3, per keyboard practice 5 phrases (2 min) plus measured block (7) plus rating (1), break 2, debriefing 3: total about 33 min, within the 40-minute session of item 7.9 (computed 2026-10-14)
- Power parameters accepted in the P batch (user, "Yes to every question", 2026-10-14): target power 0.80; alpha 0.025 (Holm's strictest step for two confirmatory hypotheses, item 11.9); grid 16, 24, 32, 40, 48, 64; lmer intercept 30 WPM, participant intercept SD 8, slope SD 5, residual SD 6 (hci-researcher, judgment anchored on Palin et al. 2019 and Reyal et al. 2015); glmer baseline 0.30, intercept SD 1.0 (hci-researcher), slope SD 0.5 (provisional), test coefficient 0.094 log-odds as the H2 TOST proxy; clmm intercept SD 1.0, thresholds −4.5, −3.5, −2.5, −1.5, 0.0, 1.5 (hci-researcher, judgment), 1 observation per participant per condition
- Counterbalancing for two conditions: complete counterbalancing, orders tap-then-swipe and swipe-then-tap; no Latin square needed (hci-researcher, 2026-10-14)
--- Open items
1. Item 7.7 provisional parameter, tap keyboard autocorrect and suggestions: recommendation "as shipped" (both on), since that is what novices meet in practice; user answered "I don't know"
2. H2 power: at the committed 2-percentage-point bound the TOST proxy has power 0.07 at n = 40 (0.03 to 0.11 across the grid and baselines 0.20 to 0.45); the user keeps the bound ("keep the 2 percentage point H2 bound; item 6.6 stands as I gave it"), so the proposal must state H2 as underpowered at this count
3. Provisional power parameter: participant keyboard-slope SD 0.5 log-odds in the error-indicator model (recommendation, my judgment, not from a source)
4. Item 2.4 provisional, recommendation: week 0 IRB submission; weeks 1 to 3 review; week 4 pilot; weeks 4 to 7 data collection; week 8 analysis; weeks 9 to 10 write-up; user answered "I don't know yet"
5. Run `/experiment-proposal:lit-search` for the hypothesis direction (swipe versus tap text entry speed and errors in novice users), to verify the Reyal, Zhai and Kristensson (2015) and Palin et al. (2019) figures under Looked up, and for the participant counts of similar experiments (item 8.5)
6. Run `/experiment-proposal:the-ethics-board` with the consent story and data path from items 1.2, 1.3 and 12.3
--- Amendments
(absent)
--- 8.5
### 8.5 Participant count
- Decision: 40 participants (20 per keyboard order), the smallest grid value at which the primary measure, words per minute, reaches power 0.80: power 0.88 (95% CI 0.86 to 0.90) at n = 40 in the governing run, 1000 simulations, alpha 0.025, seed 20261013. At n = 40 the other models: uncorrected-error indicator (H2 TOST proxy) power 0.07 (0.06 to 0.09); ease rating power 0.14 (0.12 to 0.17), with 36 of 1000 clmm fits failing and excluded. The search run, 200 simulations over the grid 16, 24, 32, 40, 48, 64, gave words-per-minute power 0.41, 0.60, 0.77, 0.89, 0.92, 0.98 and chose 40; the confirmation at 1000 simulations over 40 and 48 governs. Similar experiments: Reyal, Zhai and Kristensson (2015) ran a within-subjects gesture-versus-touch lab study (count to be confirmed by lit-search). The pilot refines the count only through the phrases per keyboard (item 2.2): a smaller phrase count raises the residual contribution and the power run is repeated at that value. Power-run simplifications, recorded in `proposal/power.R`: the crossed phrase terms of item 11.6 are dropped (the template supports one random term, by participant; the participant keyboard slope is kept); treatment coding with tap as reference replaces item 11.5's sum coding (same slope magnitude); the clmm uses `(1 | participant)`, which is also item 11.6's structure; H2's TOST is proxied by the power to detect a coefficient equal to the 2-point bound (0.094 log-odds at a 0.30 baseline), a conservative stand-in for TOST power under a true null. H2 at this count is therefore powered near alpha: the 2-point bound of item 6.6 is not reachable at any feasible count under these assumptions; see Open items. The run applied alpha 0.025 to all three models; RQ1 is reported unadjusted at 0.05 (item 11.9), so the rating's power at 0.05 would be somewhat higher than 0.14.
- Rationale: user accepted the run ("Yes, run proposal/power.R") and the batch ("Yes to every question, P1 to the last ... Keep all three models").
- Would change if: the pilot changed the phrases per keyboard, or item 6.6's H2 bound were widened with a reason, which would re-run `proposal/power.R`
- Status: settled
- Source: proposal/power.R, run 2026-10-14
--- 8.6
### 8.6 Effect size assumed
- Decision: H1, the primary measure: 3 words per minute, the smallest effect size of interest of item 6.6, first in the sourcing ranking; the hci-researcher anchored it as about 10% of a 30 WPM novice baseline, in the range of the 3 to 6 WPM gesture-versus-touch differences reported by Reyal, Zhai and Kristensson (2015) and consistent with Palin et al. (2019); the 10% threshold is judgment, so stated. H2: the 2-percentage-point bound of item 6.6 (0.094 log-odds at a 0.30 baseline), the smallest effect of interest, the user's judgment. RQ1: 0.5 latent-scale units, the smallest effect of interest, the user's judgment. Nuisance values (intercept 30, participant intercept SD 8, slope SD 5, residual SD 6 for WPM; baseline 0.30, intercept SD 1.0 for the error indicator; intercept SD 1.0 and thresholds −4.5, −3.5, −2.5, −1.5, 0.0, 1.5 for the rating) are the hci-researcher's judgment values, flagged as such, to be checked against the pilot; the error model's slope SD 0.5 is provisional (Open items).
- Rationale: "Yes to every question, P1 to the last, accepting each recommendation as you worded it."
- Would change if: lit-search or the pilot gave a sourced value for any of these
- Status: settled
- Source: items 6.6 and the P batch, 2026-10-14
--- 8.7
### 8.7 Range across effect sizes
- Decision: The search curve for words per minute at effect 3 WPM, 200 simulations, alpha 0.025: n 16 power 0.41 (0.34 to 0.48); 24, 0.60 (0.53 to 0.67); 32, 0.77 (0.70 to 0.82); 40, 0.89 (0.83 to 0.93); 48, 0.92 (0.87 to 0.95); 64, 0.98 (0.95 to 0.99). Governing run, 1000 simulations: 40, 0.88 (0.86 to 0.90); 48, 0.94 (0.92 to 0.95). Error indicator at the bound, 200 simulations: 0.04, 0.07, 0.07, 0.07, 0.09, 0.07 over the same grid; 1000 simulations: 0.07 at 40, 0.08 at 48. Ease rating at 0.5 latent, 200 simulations: 0.12, 0.12, 0.11, 0.13, 0.18, 0.29; 1000 simulations: 0.14 at 40, 0.17 at 48. The count is read off at 3 WPM. Sweep across plausible effect sizes (200 simulations each, alpha 0.025, grid 16, 24, 32, 40, 48, 64, run 2026-10-14 from temporary copies of `proposal/power.R` with only the effect sizes changed): H1 at 2 WPM, 0.18, 0.31, 0.42, 0.52, 0.56, 0.76 (no grid value reaches 0.80; about 64 to 80 would be needed); at 3 WPM, 0.41, 0.60, 0.77, 0.89, 0.92, 0.98 (count 40); at 5 WPM, 0.88, 0.98, 1.00, 1.00, 1.00, 1.00 (count 16); at 8 WPM, 1.00 at every grid value (count 16). RQ1 at 0.3 latent units, 0.07, 0.09, 0.05, 0.07, 0.09, 0.11; at 0.5, 0.12, 0.12, 0.11, 0.13, 0.18, 0.29; at 1.0, 0.22, 0.36, 0.41, 0.52, 0.62, 0.75. H2 at the 2-point bound with baseline 0.20 (0.121 log-odds), 0.03, 0.07, 0.09, 0.11, 0.11, 0.10; baseline 0.30 (0.094), 0.04, 0.07, 0.07, 0.07, 0.09, 0.07; baseline 0.45 (0.081), 0.05, 0.03, 0.04, 0.05, 0.05, 0.08. Reading: the committed count of 40 holds for H1 at 3 WPM or more and fails at 2 WPM; RQ1 is underpowered at 40 for any plausible effect below 1.0 latent units; H2 at the 2-point bound stays at alpha across the grid and every baseline. The user keeps the 2-point bound ("item 6.6 stands as I gave it").
- Rationale: accepted recommendation: the grid and the committed effect size of item 6.6.
- Would change if: the committed effect size changed
- Status: settled
- Source: proposal/power.R, runs 2026-10-14
```

## `proposal/power.R` PARAMETERS block (final state, the 1000-simulation governing configuration)

```r
params <- list(
  seed = 20261013,
  n_sims = 1000,           # simulations per participant count; use 1000 for the final run
  alpha = 0.025,           # Holm's strictest step for two confirmatory hypotheses (item 11.9)
  target_power = 0.80,
  # Participant counts to try. Keep every value a multiple of the number of
  # between-subjects groups and of the number of counterbalanced orders.
  n_grid = c(40, 48),      # search at 200 sims over c(16, 24, 32, 40, 48, 64) chose 40; curve in the brief, item 8.7
  trials_per_condition = 20,   # item 2.2 working value, pilot settles
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
  # Power-run simplifications (recorded in the brief, items 8.5 to 8.7): the
  # crossed phrase terms of item 11.6 are dropped (template supports one term by
  # participant); treatment coding replaces item 11.5's sum coding (same slope
  # magnitude); the H2 TOST is proxied by detecting a coefficient equal to the
  # 2-percentage-point bound (0.094 log-odds at a 0.30 baseline).
  models = list(
    list(
      dv = "words_per_minute",
      family = "lmer",
      formula = y ~ keyboard + (1 + keyboard | participant),
      test = "keyboardswipe",
      fixef = c("(Intercept)" = 30, "keyboardswipe" = 3),
      sd_participant = c(8, 5),
      sigma = 6
    ),
    list(
      dv = "uncorrected_error",
      family = "glmer",
      formula = y ~ keyboard + (1 + keyboard | participant),
      test = "keyboardswipe",
      fixef = c("(Intercept)" = qlogis(0.30), "keyboardswipe" = qlogis(0.32) - qlogis(0.30)),
      sd_participant = c(1.0, 0.5)
    ),
    list(
      dv = "ease_rating",
      family = "clmm",
      formula = y ~ keyboard + (1 | participant),
      test = "keyboardswipe",
      fixef = c("keyboardswipe" = 0.5),
      sd_participant = c(1.0),
      thresholds = c(-4.5, -3.5, -2.5, -1.5, 0.0, 1.5),
      trials = 1
    )
  )
)

## ---- END OF PARAMETERS ----
```

## `git log --oneline` in the scratch project

```text
af5f271 Freeze the design brief
f3bab3c init
```
