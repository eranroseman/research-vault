# Design brief: mouse versus trackball target selection

Draft: proposal/draft.md
Status: frozen 2026-10-10
Checklist: experiment-proposal 0.1.0

## Decisions

### 1.1 The question

- Decision: Does selecting targets with a mouse rather than a trackball change movement time? Levels: mouse, trackball.
- Rationale: "That's the one comparison the lab keeps arguing about."
- Would change if: the lab switched to touchpads.
- Status: settled
- Source: user, round 1

### 1.2 Ethics route

- Decision: the department's standing approval for minimal-risk interaction studies, protocol CS-HCI-2026-01.
- Rationale: "It covers device comparisons with adults; the office confirmed."
- Would change if: minors or recordings were added.
- Status: settled
- Source: user, round 1

### 1.3 Data plan

- Decision: no names linked to logs, no recordings; the two experimenters have access; raw logs kept five years.
- Rationale: "Nothing identifiable is needed for timing data."
- Would change if: the committee set a different period.
- Status: settled
- Source: user, round 1

### 2.2 Session estimate

- Decision: 2 devices by 9 combinations by 5 trials plus practice; 35 minutes.
- Rationale: "Under 40 minutes keeps people from tiring."
- Would change if: the pilot showed fatigue.
- Status: settled
- Source: user, round 2

### 2.3 Pilot

- Decision: three lab members; refines the trial count; data not reported.
- Rationale: "Lab members are not the population."
- Would change if: the pilot ran exactly as proposed.
- Status: settled
- Source: user, round 2

### 2.4 Timeline

- Decision: pilot week 3, data weeks 4 to 7, analysis weeks 8 to 9, write-up weeks 10 to 12.
- Rationale: "That's the term."
- Would change if: the IRB answer slipped.
- Status: settled
- Source: user, round 2

### 2.5 Expected challenges

- Decision: short sign-ups: extend to a second section by week 5.
- Rationale: "Happened last year."
- Would change if: recruiting opened to the whole department.
- Status: settled
- Source: user, round 2

### 6.1 Hypotheses

- Decision: H1 and H2 directional; H3 an interaction.
- Rationale: "The literature gives directions for time and errors."
- Would change if: the literature were mixed on errors.
- Status: settled
- Source: user, round 2

### 6.2 Directions and sources

- Decision: H1 and H3 from MacKenzie, Sellen and Buxton (1991) and Epps (1986); H2 from the same sources.
- Rationale: "Both report fewer errors with the mouse."
- Would change if: a newer comparison contradicted them.
- Status: settled
- Source: user, round 2

### 6.5 Interaction

- Decision: H3: device by target size.
- Rationale: "Small targets are where trackballs struggle."
- Would change if: pilot showed no size effect.
- Status: settled
- Source: user, round 2

### 6.6 Smallest effect size of interest

- Decision: 100 ms for H1; 2 percentage points for H2; 50 ms per size step for H3.
- Rationale: "Below 100 ms nobody would switch devices."
- Would change if: a usability threshold from the literature replaced it.
- Status: settled
- Source: user, round 3

### 6.7 Decision rule

- Decision: support when the interval excludes zero in the predicted direction and the estimate reaches the SESOI; falsify when the interval excludes the SESOI; otherwise inconclusive.
- Rationale: "Then a null is a null."
- Would change if: a Bayesian analysis were adopted.
- Status: settled
- Source: user, round 3

### 7.1 Independent variables

- Decision: device between subjects; distance and size within subjects, 128/256/512 pixels and 16/32/64 pixels.
- Rationale: "Daily mouse users bring habits a few minutes on a trackball won't erase, so the carry-over is asymmetric; between subjects avoids it."
- Would change if: participants had no daily device.
- Status: settled
- Source: user, round 2

### 7.2 Carry-over

- Decision: distance and size carry-over symmetric; device asymmetric, hence between.
- Rationale: "Habit transfer is one-way."
- Would change if: a wash-out period were feasible.
- Status: settled
- Source: user, round 2

### 7.3 Overall design

- Decision: 2 × 3 × 3 mixed factorial, device between, distance and size within.
- Rationale: "H3 needs device crossed with size."
- Would change if: device went within.
- Status: settled
- Source: user, round 2

### 7.4 Random assignment

- Decision: device from a shuffled list keeping the groups equal.
- Rationale: "A shuffled list is a random source we can archive."
- Would change if: device went within.
- Status: settled
- Source: user, round 2

### 7.5 Counterbalancing

- Decision: the nine distance-and-size combinations in a random order per participant, drawn by the software with equal counts per combination.
- Rationale: "Nine conditions is too many for a Latin square we'd analyse."
- Would change if: an order effect appeared in the pilot.
- Status: settled
- Source: hci-researcher

### 7.6 Dependent variables

- Decision: movement time in ms, software-timed, ratio; error rate as the proportion of misses, ratio; reported together.
- Rationale: "Speed without accuracy is meaningless."
- Would change if: throughput were added.
- Status: settled
- Source: user, round 2

### 7.7 Controls

- Decision: right-handed, 18 to 22; same display, software, room, script.
- Rationale: "Handedness and age keep the sample uniform at the cost of generality."
- Would change if: the study aimed at older adults.
- Status: settled
- Source: user, round 2

### 7.8 Random variables

- Decision: skill, vision, mood, time of day.
- Rationale: "Whatever varies by chance."
- Would change if: time of day were blocked.
- Status: settled
- Source: user, round 2

### 7.9 Confounds

- Decision: history (same weeks, similar times); maturation (one short session); instrumentation (frozen software); experimenter (one for all).
- Rationale: "Each has a cheap prevention."
- Would change if: two experimenters were needed.
- Status: settled
- Source: hci-researcher

### 8.3 Eligibility

- Decision: right-handed, 18 to 22, screened by form; no selection on pointing speed.
- Rationale: "No extreme-score selection."
- Would change if: the committee required more.
- Status: settled
- Source: user, round 3

### 8.5 Participant count

- Decision: 24 (12 per device), from proposal/power.R run on 2026-10-10: lmer on movement time, 120 ms device effect, power 0.82 at 24; error-rate glmer power 0.61 at 24.
- Rationale: "80% on the primary measure; errors are secondary."
- Would change if: the pilot revised the effect size.
- Status: settled
- Source: proposal/power.R
- Curve: n 16: 0.58; n 20: 0.71; n 24: 0.82; n 32: 0.93; n 40: 0.97

### 8.6 Effect-size source

- Decision: MacKenzie, Sellen and Buxton (1991), a prior study of the same measure; the SESOI (100 ms) is close to it.
- Rationale: "A published estimate beats a guess."
- Would change if: the pilot gave a stable estimate.
- Status: settled
- Source: user, round 3

### 8.7 Sensitivity range

- Decision: 90 to 150 ms reported as a range, 36 to 16 participants.
- Rationale: "One number hides the uncertainty."
- Would change if: never.
- Status: settled
- Source: proposal/power.R

### 11.2 Unit of analysis

- Decision: trials; no aggregation.
- Rationale: "Mixed models use every trial."
- Would change if: trial-level logs failed.
- Status: settled
- Source: user, round 3

### 11.4 Model family

- Decision: lmer on log movement time; glmer binomial on trial-level miss.
- Rationale: "Times are skewed; misses are binary."
- Would change if: residuals disagreed.
- Status: settled
- Source: hci-researcher

### 11.5 Fixed effects and contrasts

- Decision: device, distance, size and device by size, sum-coded; H1 the device coefficient, H2 the same in the glmer, H3 the device-by-size contrast.
- Rationale: "One coefficient per hypothesis."
- Would change if: distance by size mattered.
- Status: settled
- Source: user, round 3

### 11.6 Random effects

- Decision: random intercept, and slopes for distance and size, by participant; drop correlations, then the size slope, then the distance slope, on non-convergence.
- Rationale: "Within-subject factors get slopes; the order is fixed now so it isn't data-driven."
- Would change if: never.
- Status: settled
- Source: hci-researcher

### 11.7 Inference

- Decision: Satterthwaite through lmerTest; Wald z for the glmer; standardized coefficients and odds ratios.
- Rationale: "Standard and reproducible."
- Would change if: never.
- Status: settled
- Source: user, round 3

### 11.8 Exclusions and trimming

- Decision: failed sessions and ineligible participants excluded; trials under 150 ms or over 5000 ms trimmed; every exclusion reported.
- Rationale: "Nothing conditional on how someone did in a condition."
- Would change if: never.
- Status: settled
- Source: user, round 3

### 11.9 Significance and multiplicity

- Decision: alpha .05; every p value with its effect size; three hypotheses Holm-adjusted.
- Rationale: "Three tests, one family."
- Would change if: never.
- Status: settled
- Source: user, round 3

## Looked up

- Fitts's law index of difficulty: log2(A/W + 1) (MacKenzie, 1992), 2026-10-10

## Open items

1. Run `/experiment-proposal:lit-search` for a current-device comparison to cite under H1
