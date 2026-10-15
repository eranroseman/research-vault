# Design brief: mouse versus trackball target selection

Draft: proposal/draft.md
Status: frozen 2026-10-10
Checklist: experiment-proposal 0.2.0

## Decisions

### 1.1 The question

- Decision: Does selecting targets with a mouse rather than a trackball change movement time? Levels: mouse, trackball.
- Rationale: "That's the one comparison the lab keeps arguing about."
- Would change if: the lab switched to touchpads.
- Status: settled
- Source: user, round 1

### 1.2 The ethics route

- Decision: the department's standing approval for minimal-risk interaction studies, protocol CS-HCI-2026-01.
- Rationale: "It covers device comparisons with adults; the office confirmed."
- Would change if: minors or recordings were added.
- Status: settled
- Source: user, round 1

### 1.3 The data plan

- Decision: no names linked to logs, no recordings; age and handedness collected only to screen; the author has access; raw logs kept five years.
- Rationale: "Nothing identifiable is needed for timing data."
- Would change if: the committee set a different period.
- Status: settled
- Source: user, round 1

### 2.2 The session estimate

- Decision: 2 devices by 9 combinations by 5 trials plus practice; 35 minutes.
- Rationale: "Under 40 minutes keeps people from tiring."
- Would change if: the pilot showed fatigue.
- Status: settled
- Source: user, round 2

### 2.3 The pilot

- Decision: three lab members; refines the trial count per combination; data not reported.
- Rationale: "Lab members are not the population."
- Would change if: the pilot ran exactly as proposed.
- Status: settled
- Source: user, round 2

### 2.4 The timeline

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

- Decision: H1 and H2 directional; H3 an interaction; no research questions.
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

### 6.5 Interactions

- Decision: H3: device by target size.
- Rationale: "Small targets are where trackballs struggle."
- Would change if: the pilot showed no size effect.
- Status: settled
- Source: user, round 2

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

### 7.3 The design

- Decision: 2 by 3 by 3 mixed factorial, device between, distance and size within.
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

- Decision: movement time in ms, software-timed, ratio, reliable and construct-valid as a measure of selection speed; error rate as the proportion of misses, ratio; reported together.
- Rationale: "Speed without accuracy is meaningless."
- Would change if: throughput were added.
- Status: settled
- Source: user, round 2

### 7.7 Controls

- Decision: right-handed, 18 to 22; same display, software, pointer settings, room, script.
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

- Decision: history (same weeks, similar times); maturation (one short session); instrumentation (frozen software and settings); experimenter (one for all).
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

### 8.5 The participant count

- Decision: 24 (12 per device), following MacKenzie, Sellen and Buxton (1991, twelve within subjects) and Douglas, Kirkpatrick and MacKenzie (1999, twelve per device); the course term allows 24 at one session each; pre-specified; the pilot refines the trial count, not the count.
- Rationale: "Twice the nearest study, and what the term allows."
- Would change if: the term allowed more sessions.
- Status: settled
- Source: user, round 3

## Looked up

- Fitts's law index of difficulty: log2(A/W + 1) (MacKenzie, 1992), 2026-10-10

## Open items

1. Run `/experiment-proposal:lit-search` for a current-device comparison to cite under H1
