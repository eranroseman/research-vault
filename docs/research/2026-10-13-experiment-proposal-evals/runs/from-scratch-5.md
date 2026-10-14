# Scenario 3, from scratch, run 5 (re-run at plugin commit 3893203)

Date: 2026-10-14. Plugin commit: 3893203. Scenario label: from-scratch. Driver: headless `claude -p` turns answered strictly from `fixtures/from-scratch-answers.md` (the plan calls this scenario interactive; the author delegated it). No turn cap: turns were sent until the brief was frozen. R 4.3.3 with lme4, lmerTest, ordinal and simr was installed; no shim. The three runs ran at the same time on one machine, so R wall times include contention. Records `from-scratch-1.md` to `-3.md` are the earlier failed attempt at commit 6bb6ed7 and are not changed.

Verdict: PASS. Every bar is met: all items settled, 2.4 provisional, 2.2 pilot settles, the count (16) is computed and recorded, the output table has an `ease` row from the clmm loop, the hci-researcher was consulted (five Agent calls), and the freeze commit exists. The rating's power is low (0.10 at n = 16), recorded as a finding.

## Turns

| Turn | Command (flags as in turn 1 on every turn)                                                                                                                           | Wall time |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 1    | `timeout 5400 claude -p "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"`            | 150 s     |
| 2    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 61 s      |
| 3    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 139 s     |
| 4    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 249 s     |
| 5    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 80 s      |
| 6    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 169 s     |
| 7    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 46 s      |
| 8    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 49 s      |
| 9    | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 104 s     |
| 10   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 89 s      |
| 11   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 1411 s    |
| 12   | `timeout 5400 claude -p --continue "<turn text>" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"` | 28 s      |

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

Turns and rounds: 12 turns. Turn 1 asked round 1; turns 2 to 8 answered rounds 1 to 7; turn 9 answered round 8 and the session asked the power batch (P1 to P7, including a P7 on template simplifications); turn 10 answered it (block shown); turn 11 said "Yes, run proposal/power.R." and the session ran both the 200-simulation search and the 1000-simulation confirmation inside that one turn (1411 s); turn 12 approved and froze. No "Is the power run finished? Continue." turn was needed.

Consistency questions raised and answered from the sheet: turn 3 reply, whether 7.2 should be `pilot settles` (answered symmetric, row 7.2; the session kept `settled`); turn 4 reply, none beyond the H2 bound flag; turn 6 reply, H2's decision rule re-asked as TOST (answered yes, row 6.6); turn 11 reply, "freeze as is or amend item 6.6 now": "Freeze as is: keep the 2 percentage point H2 bound (item 6.6 stands as I gave it)" (row 6.6).

## Transcript, decisive lines

- Turn 1: R prerequisite check passed.
- hci-researcher: five Agent calls (7.7, 7.9, 6.6, 7.5, 11.6). Turn 3: "Two consultations with the HCI researcher done (items 7.7 and 7.9)."
- Turn 9, the P batch: "**P5 (RQ1 values, clmm).** Shall the rating model assume: keyboard effect 0.5 on the latent scale, participant intercept SD 1.5 logits, thresholds ..., one rating per participant per keyboard? ... With two ratings per participant this model is weakly identified; its power at the chosen count is reported, not used to set it." Turn 10 answer: "Yes to every question, P1 to the last, accepting each recommendation as you worded it. Keep all three models (never drop the rating or the error model), and the rating has 1 observation per participant per condition."
- Turn 10: the `cp` of the template was refused ("a sensitive file"); the session wrote `proposal/power.R` with Write after reading the template. The ease model carries `trials = 1`. "Run time: 10 to 20 minutes at 200 simulations over the full grid with three models (measured 2026-10-14), and about as long again for the 1000-simulation confirmation at the chosen count."
- Turn 11, how R ran and how the session waited: `Rscript proposal/power.R > proposal/power-run-200.log 2>&1` with `run_in_background: true`. A first wait loop (`for i in $(seq 1 570); do if grep ...; then break; fi; sleep 1; done`) was refused as a compound command; the session then loaded the Monitor tool and ran `tail -f` on the log filtered by `grep` for the result lines ("power.R 200-sim run: result or error lines"). The monitor delivered the excluded-fit lines as events at 17:56 to 17:57 UTC and the session read the log at 17:57:11. It set `n_sims = 1000`, `n_grid = c(16, 20)` and started the confirmation the same way (log in a scratch folder inside the project), armed a second Monitor, re-armed it once after the first event batch, read the log at 18:09:34 and stopped the monitor with TaskStop. The turn never ended while R ran; no background run was killed at a turn's end. At the start of turn 12 the harness reported the two leftover monitor tasks as `stopped`; they had already finished their work.
- Wall times (start of the Bash call to the session reading the finished log, UTC; the actual finish is no later): 200-simulation search over the 6-value grid, 17:49:16 to 17:57:11, at most 7.9 min; 1000-simulation confirmation over n = 16 and 20, 17:57:41 to 18:09:34, at most 11.9 min.
- Turn 11 end: "Participant count: **16** (8 per order)." Table: wpm 0.81 and 0.91; error 0.05 and 0.04; ease 0.10 and 0.10 at n = 16 and 20 (1000 simulations). "**One decision before the freeze: H2.** ... Freeze as is ... or Amend item 6.6 now".
- Turn 12 end: "`proposal/design-brief.md` now reads `Status: frozen 2026-10-14`, committed as `912126e` with `proposal/power.R`."

## Power output and the excluded-fit lines

200-simulation search over the full grid:

```text
ease: 19 of 200 clmm fits failed at n = 12 and were excluded
ease: 13 of 200 clmm fits failed at n = 16 and were excluded
ease: 4 of 200 clmm fits failed at n = 20 and were excluded
ease: 5 of 200 clmm fits failed at n = 24 and were excluded
ease: 4 of 200 clmm fits failed at n = 32 and were excluded
## Power curve (200 simulations per point, alpha = 0.025, seed 20261013)
| Measure | n | Power | 95% CI |
| --- | --- | --- | --- |
| wpm | 12 | 0.64 | 0.56 to 0.70 |
| wpm | 16 | 0.80 | 0.74 to 0.85 |
| wpm | 20 | 0.90 | 0.85 to 0.94 |
| wpm | 24 | 0.95 | 0.92 to 0.98 |
| wpm | 32 | 1.00 | 0.98 to 1.00 |
| wpm | 40 | 1.00 | 0.98 to 1.00 |
| error | 12 | 0.03 | 0.01 to 0.06 |
| error | 16 | 0.03 | 0.01 to 0.06 |
| error | 20 | 0.04 | 0.01 to 0.07 |
| error | 24 | 0.07 | 0.04 to 0.11 |
| error | 32 | 0.09 | 0.05 to 0.14 |
| error | 40 | 0.09 | 0.05 to 0.13 |
| ease | 12 | 0.10 | 0.06 to 0.16 |
| ease | 16 | 0.11 | 0.07 to 0.16 |
| ease | 20 | 0.15 | 0.10 to 0.21 |
| ease | 24 | 0.11 | 0.07 to 0.16 |
| ease | 32 | 0.16 | 0.11 to 0.22 |
| ease | 40 | 0.18 | 0.13 to 0.24 |
Primary measure: wpm
Participant count: 16 (the smallest grid value with power >= 0.80 for wpm)
At n = 16, error: power 0.03 (0.01 to 0.06)
At n = 16, ease: power 0.11 (0.07 to 0.16)
```

1000-simulation confirmation, n_grid = 16 and 20:

```text
ease: 44 of 1000 clmm fits failed at n = 16 and were excluded
ease: 30 of 1000 clmm fits failed at n = 20 and were excluded
## Power curve (1000 simulations per point, alpha = 0.025, seed 20261013)
| Measure | n | Power | 95% CI |
| --- | --- | --- | --- |
| wpm | 16 | 0.81 | 0.78 to 0.83 |
| wpm | 20 | 0.91 | 0.89 to 0.93 |
| error | 16 | 0.05 | 0.04 to 0.07 |
| error | 20 | 0.04 | 0.03 to 0.06 |
| ease | 16 | 0.10 | 0.08 to 0.12 |
| ease | 20 | 0.10 | 0.08 to 0.12 |
Primary measure: wpm
Participant count: 16 (the smallest grid value with power >= 0.80 for wpm)
At n = 16, error: power 0.05 (0.04 to 0.07)
At n = 16, ease: power 0.10 (0.08 to 0.12)
```

Rating power is low: 0.10 at n = 16 and at n = 20 in the 1000-simulation run (0.10 to 0.18 over the search grid). Failed clmm fits were excluded and counted: 19 of 200 at n = 12 down to 4 of 200 at n = 32 in the search; 44 of 1000 at n = 16 and 30 of 1000 at n = 20 in the confirmation.

## Pass bar

| Criterion                                                    | Result | Evidence                                                                                                                      |
| ------------------------------------------------------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------- |
| Every design-tree item settled, provisional or pilot settles | PASS   | 31 entries: `settled` except 2.2 `pilot settles` and 2.4 `provisional`; 8.5, 8.6, 8.7 `settled`; `Status: frozen 2026-10-14`. |
| 2.4 provisional, 2.2 pilot settles                           | PASS   | Both statuses as above.                                                                                                       |
| Mixed-model plan complete (11.2, 11.4 to 11.9)               | PASS   | All `settled`.                                                                                                                |
| Power computed, `proposal/power.R` run, count recorded       | PASS   | Count 16 from the 1000-simulation run; 8.5 `Source: proposal/power.R, run 2026-10-14`.                                        |
| Rating's power through the clmm loop, a `rating` row         | PASS   | `ease` rows in both tables, with the excluded-fit lines.                                                                      |
| hci-researcher consulted at least once                       | PASS   | Five Agent calls.                                                                                                             |
| Freeze commit exists                                         | PASS   | `912126e Freeze the design brief`.                                                                                            |

## Verdict

PASS. Observations: (1) the session waited inside the turn with Monitor; nothing was killed. (2) Item 8.7's entry gives the range across effect sizes by a normal-approximation scaling of the 3 WPM curve (2 WPM about 36, 4 WPM about 10) and says so; no simulation at other effect sizes was run. Section 6 step 5 does not say whether 8.7's range must be simulated. (3) The brief's 2.2 status line carries a parenthesis describing what the pilot measures; the status word is `pilot settles`.

## Brief (final state in the scratch project; Looked up entries trimmed to the sections asked for)

```text
--- HEADER
# Design brief: Swipe versus tap text entry for novice smartphone users

Draft: proposal/draft.md
Status: frozen 2026-10-14
Checklist: experiment-proposal 0.1.0
--- STATUSES
1.1 The question | settled
1.2 Ethics route | settled
1.3 Data plan | settled
2.2 Conditions, trials and session | pilot settles (the pilot measures per-phrase entry time per keyboard and total session time, and fixes the phrase count that keeps the session within 40 minutes)
2.3 Pilot plan | settled
2.4 Timeline | provisional
2.5 Expected challenges | settled
6.1 Hypotheses and research questions | settled
6.2 Hypothesis form and sources | settled
6.5 Interaction hypotheses | settled
6.6 Smallest effect size of interest | settled
6.7 Decision rules | settled
7.1 Independent variable | settled
7.2 Carry-over | settled
7.3 Design named | settled
7.4 Random assignment | settled
7.5 Counterbalancing | settled
7.6 Dependent variables | settled
7.7 Control variables | settled
7.8 Random variables | settled
7.9 Confounds | settled
8.3 Eligibility and screening | settled
8.5 Participant count | settled
8.6 Effect size assumed by the power analysis | settled
8.7 Sensitivity range | settled
11.2 Unit of analysis | settled
11.4 Model families | settled
11.5 Fixed effects and contrasts | settled
11.6 Random effects and simplification order | settled
11.7 Inference method | settled
11.8 Exclusions and trimming | settled
11.9 Significance level and multiplicity | settled
--- Looked up
- Words per minute (WPM), the standard text-entry speed measure: WPM = ((transcribed characters − 1) / seconds) × 60 / 5, five characters per word including spaces (MacKenzie, "A note on calculating text entry speed", 2002; Arif and Stuerzlinger, "Analysis of text entry performance metrics", IEEE TIC-STH 2009; recalled 2026-10-14)
- Standard text-entry error metrics: minimum string distance (MSD) uncorrected error rate, and total error rate = corrected + uncorrected, from the input stream (Soukoreff and MacKenzie, "Metrics for text entry research: an evaluation of MSD and KSPC, and a new unified error metric", CHI 2003; recalled 2026-10-14)
- The standard phrase set: 500 short English phrases, no punctuation, lowercase, mean length about 28 characters (MacKenzie and Soukoreff, "Phrase sets for evaluating text entry techniques", CHI Extended Abstracts 2003; recalled 2026-10-14)
- Session arithmetic: a 25-character phrase is 5 words; at an assumed novice tap speed of 28 WPM one phrase takes about 11 s, so 25 phrases (5 practice, 20 scored) take about 5 to 6 min; assumed novice swipe at roughly half that speed gives about 9 min; total with consent, instructions, ratings, a break and debriefing about 30 min (computed 2026-10-14)
- Sum coding at ±0.5 leaves the keyboard coefficient equal to the full swipe-minus-tap difference, so the item 6.6 thresholds apply unchanged; ±1 coding would halve it (2026-10-14)
- Log-odds width of a 2 percentage point bound at a baseline error proportion of 0.25: qlogis(0.27) − qlogis(0.25) = 0.104 (computed in R, 2026-10-14)
- Effect-size scaling for item 8.7: with the standard error of the keyboard coefficient falling as 1/√n, the participant count for an effect d scales as n(3 WPM) × (3/d)²: 16 × (3/2)² = 36 for 2 WPM; 16 × (3/4)² = 9, rounded to 10, for 4 WPM (normal approximation, computed 2026-10-14)
- Holm adjustment across two confirmatory tests: the smaller p value is compared with 0.05/2 = 0.025, the larger with 0.05; the power run uses 0.025 as the conservative level for the primary measure (2026-10-14)
- Effect-size and baseline assumptions for the power run, from the hci-researcher consultation (2026-10-14; the subagent could not search the web, so cited values are recalled and marked for verification by lit-search): WPM, swipe minus tap, smallest effect of interest 3 WPM (judgment, about 10% of a novice baseline; Reyal, Zhai and Kristensson CHI 2015 report lab gesture-versus-touch differences of about this size, recalled); novice tap intercept 28 WPM (judgment; Palin et al. MobileHCI 2019 mean 36 WPM for experienced users, recalled); between-participant SD 7 WPM, per-phrase residual SD 5 WPM, participant keyboard-slope SD 3 WPM (judgment). Errors: the subagent recommended a non-inferiority bound of log-odds +0.41 (odds ratio 1.5; judgment, below the OR 1.68 that Chen, Cohen and Chen 2010 equate to d = 0.2, recalled), which the user replaced with a 2 percentage point bound at item 6.6; tap baseline probability of a phrase with any uncorrected error 0.25 (judgment, derived from Palin et al.'s roughly 2.3% character error rate, recalled); participant intercept SD 0.8 logits (judgment); participant keyboard-slope SD 0.3 logits (design skill's judgment, not the subagent's). Ease rating: thresholds −4.0, −3.0, −2.0, −1.0, 0.5, 2.0 logits; the subagent recommended a smallest effect of beta = 1.0, which the user replaced with 0.5 at item 6.6; participant intercept SD 1.5 logits (all judgment)
- Counterbalancing options for two within-subjects levels, from the hci-researcher consultation (2026-10-14): two orders (AB, BA), multiple of 2; ABBA with mirror BAAB, multiple of 2 but four block switches; order crossed with phrase-subset assignment, 4 cells, multiple of 4, no extra session time
- R prerequisites (lme4, lmerTest, ordinal, simr): all present, check passed (Rscript requireNamespace check, 2026-10-14)
- Project is a git repository at <scratch>, so the brief can be frozen by commit (git rev-parse, 2026-10-14)
--- Open items
1. Item 2.4 provisional, recommendation: ten-week timeline (IRB three weeks, pilot one week, collection three weeks, analysis one week, write-up two weeks); the author has not set dates
2. Provisional power parameters (recommendations accepted for the run, not confirmed by a pilot or prior study; the pilot, item 2.3, refines them): tap intercept 28 WPM, participant intercept SD 7 WPM, participant keyboard-slope SD 3 WPM, per-phrase residual SD 5 WPM; tap baseline error probability 0.25, participant intercept SD 0.8 logits, slope SD 0.3 logits; ease thresholds −4.0, −3.0, −2.0, −1.0, 0.5, 2.0 and participant intercept SD 1.5 logits
3. Run `/experiment-proposal:lit-search` for prior swipe-versus-tap text-entry studies with novice or older users, to source the hypothesis direction (item 6.2), the effect size (items 6.6 and 8.6) and the recalled citations under Looked up
4. Run `/experiment-proposal:the-ethics-board` with the consent story and data path from items 1.2, 1.3 and 12.3
--- Amendments
(absent)
--- 8.5
### 8.5 Participant count
- Decision: 16 participants (8 per keyboard order), the smallest grid value at which the primary measure, words per minute, reaches power 0.80 for a 3 WPM effect at alpha 0.025 (the Holm-adjusted level, item 11.9). Governing run: 1000 simulations at n = 16 and 20, power 0.81 (95% CI 0.78 to 0.83) at 16 and 0.91 (0.89 to 0.93) at 20. At n = 16 the other models' power: error (H2, glmer) 0.05 (0.04 to 0.07); ease (RQ1, clmm) 0.10 (0.08 to 0.12). The pilot (item 2.3) refines the residual and slope SDs; if the pilot's values raise the count, the next grid value is 20. Power-run simplifications (noted in proposal/power.R): random effects by participant only, the by-phrase terms of item 11.6 omitted; treatment coding of keyboard, whose coefficient equals the sum-coded swipe-minus-tap difference; the glmer entry reports the power to detect a difference equal to the H2 bound (0.104 logits) against zero, as the stand-in for TOST power, since the template does not simulate a TOST; the clmm entry uses `(1 | participant)`, which matches item 11.6. The H2 result means the 2 percentage point equivalence bound cannot be reached at any grid value (power 0.03 to 0.09 across 12 to 40 at 200 simulations); H2 is kept as pre-registered, and the proposal must say the study is not powered for it (see the Open items entry).
- Rationale: accepted recommendation for every power parameter: "Yes to every question, P1 to the last, accepting each recommendation as you worded it. Keep all three models (never drop the rating or the error model), and the rating has 1 observation per participant per condition."
- Would change if: the pilot's per-phrase residual SD or keyboard-slope SD exceeds the assumed 5 and 3 WPM, or the phrase count per keyboard drops below 20.
- Status: settled
- Source: proposal/power.R, run 2026-10-14
--- 8.6
### 8.6 Effect size assumed by the power analysis
- Decision: The primary measure's effect size is the smallest effect size of interest from item 6.6, 3 WPM swipe minus tap, the first rung of the sourcing ranking. The baseline and variance values (tap intercept 28 WPM, participant intercept SD 7, keyboard-slope SD 3, residual SD 5) are the HCI researcher's judgment (Looked up), not a pilot or prior study, and are recorded as provisional parameters under Open items. H2's effect size is the item 6.6 bound itself (0.104 logits at a 0.25 baseline) with the subagent's judgment baseline; RQ1's is 0.5 on the latent scale (item 6.6) with judgment thresholds and SD.
- Rationale: accepted recommendation: smallest effect size of interest first (checklist item 8.6); "Yes to every question, P1 to the last, accepting each recommendation as you worded it."
- Would change if: the literature search or the pilot supplies a measured effect or SD for the same measure and design, which outranks judgment values.
- Status: settled
- Source: proposal/power.R, run 2026-10-14; items 6.6 and the hci-researcher consultation
--- 8.7
### 8.7 Sensitivity range
- Decision: The 200-simulation search over the full grid (alpha 0.025, seed 20261013) gives the power curve the count is read from. Words per minute (3 WPM, SDs 7/3/5): n = 12, 0.64 (0.56 to 0.70); 16, 0.80 (0.74 to 0.85); 20, 0.90 (0.85 to 0.94); 24, 0.95 (0.92 to 0.98); 32, 1.00; 40, 1.00. Error (0.104 logits at baseline 0.25, SDs 0.8/0.3): 12, 0.03; 16, 0.03; 20, 0.04; 24, 0.07; 32, 0.09; 40, 0.09. Ease (0.5 latent, SD 1.5, one rating per keyboard): 12, 0.10; 16, 0.11; 20, 0.15; 24, 0.11; 32, 0.16; 40, 0.18. The committed count, 16, is read off this curve at the assumed 3 WPM effect and confirmed at 1000 simulations (item 8.5). Range across plausible effect sizes for the primary measure, derived by normal-approximation scaling from the simulated 3 WPM curve (standard error falls as 1 over the square root of n, so the count scales with the square of the effect ratio; Looked up), not by simulation: a 2 WPM effect needs about 36 participants, 3 WPM 16, 4 WPM about 10 (rounded up to a multiple of 2). A simulated range at 2 and 4 WPM can replace this by re-running proposal/power.R with those values.
- Rationale: accepted recommendation: the range is reported as the curve, never one number alone (checklist item 8.7).
- Would change if: proposal/power.R is re-run with pilot-refined SDs or a different effect size.
- Status: settled
- Source: proposal/power.R, run 2026-10-14
```

## `proposal/power.R` PARAMETERS block (final state, the 1000-simulation governing configuration)

```r
params <- list(
  seed = 20261013,
  n_sims = 1000,           # confirmation run; the 200-simulation search over c(12, 16, 20, 24, 32, 40) chose 16
  alpha = 0.025,           # Holm-adjusted level for the smaller of two confirmatory p values (item 11.9)
  target_power = 0.80,
  # Participant counts to try. Keep every value a multiple of the number of
  # between-subjects groups and of the number of counterbalanced orders.
  n_grid = c(16, 20),                   # chosen count and the next grid value; multiples of 2 orders (item 7.5)
  trials_per_condition = 20,            # working value, pilot settles (item 2.2)
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
  # Simplifications for this run (recorded in the brief, items 8.5 to 8.7):
  # - keyboard is treatment-coded here (tap reference); the coefficient
  #   keyboardswipe equals swipe minus tap, the same quantity the brief's
  #   sum coding (tap -0.5, swipe +0.5) estimates, so effect sizes transfer.
  # - random effects by participant only; the by-phrase terms of item 11.6
  #   are omitted (the template supports one random term), which is item
  #   11.6's own reduction steps 2 to 4.
  # - H2 is an equivalence test (TOST, item 6.6); the template tests the
  #   coefficient against zero, so the "error" entry reports the power to
  #   detect a difference equal to the bound (0.104 logits), the stand-in
  #   for TOST power at a true effect of zero.
  models = list(
    list(
      dv = "wpm",                                    # H1, primary measure
      family = "lmer",
      formula = y ~ keyboard + (1 + keyboard | participant),
      test = "keyboardswipe",
      fixef = c("(Intercept)" = 28, "keyboardswipe" = 3),   # 3 WPM = smallest effect of interest (item 6.6)
      sd_participant = c(7, 3),                      # intercept SD, keyboard-slope SD
      sigma = 5                                      # per-phrase residual SD
    ),
    list(
      dv = "error",                                  # H2, per-phrase any uncorrected error
      family = "glmer",
      formula = y ~ keyboard + (1 + keyboard | participant),
      test = "keyboardswipe",
      fixef = c("(Intercept)" = qlogis(0.25), "keyboardswipe" = 0.104),  # bound = 2 pp at baseline 0.25
      sd_participant = c(0.8, 0.3)
    ),
    list(
      dv = "ease",                                   # RQ1, 1 to 7 rating once per keyboard
      family = "clmm",
      formula = y ~ keyboard + (1 | participant),
      test = "keyboardswipe",
      fixef = c("keyboardswipe" = 0.5),              # 0.5 on the latent scale (item 6.6)
      sd_participant = c(1.5),
      thresholds = c(-4.0, -3.0, -2.0, -1.0, 0.5, 2.0),
      trials = 1
    )
  )
)

## ---- END OF PARAMETERS ----
```

## `git log --oneline` in the scratch project

```text
912126e Freeze the design brief
f3bab3c init
```
