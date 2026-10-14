# Scenario 2 (material with gaps), run 3

Date: 2026-10-14
Plugin commit: bf89d54
Fixture: `fixtures/material-with-gaps.md` as of commit bf89d54 (6.5 carries its reason: "No interaction is expected: our field study gave no hint that the keyboard's effect depends on who types or what they type."), key `fixtures/material-with-gaps.key.md`.

## Command (one turn, no answers given)

```bash
cd <scratch>   # fresh mktemp -d project: git init, empty init commit, mkdir proposal, material.md copied from fixtures/material-with-gaps.md, committed as "fixtures"
claude -p --plugin-dir <checkout>/plugins/experiment-proposal --permission-mode acceptEdits "/experiment-proposal:design material.md" --allowedTools "Read,Write,Edit,Agent,Bash(Rscript:*),Bash(git:*)"
```

Environment at run time: `Rscript` was on `PATH` with the four R packages not yet installed (the skill reported `missing R package: lme4`), so the prerequisite check failed and the power group came out BLOCKED, which the key accepts. See the report's deviations.

## Extraction table, as the skill printed it

| Item                     | Status  | Passage or gap                                                                                                                                                                                 |
| ------------------------ | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1 question             | settled | "Does entering text on a 40 mm smartwatch with a swipe keyboard change words per minute compared with a tap keyboard? ... because those are the two keyboards the watch ships with" (Question) |
| 1.2 ethics               | settled | "submitted under the department's standing protocol ... two-week turnaround ... covers keyboard comparisons with adults" (Ethics)                                                              |
| 1.3 data plan            | weak    | kinds, access ("Only the two experimenters") stated; "Retention: to be decided" (Data)                                                                                                         |
| 2.2 trials, session      | missing | no phrase count, no session estimate                                                                                                                                                           |
| 2.3 pilot                | settled | "three people from the lab, data not reported, because lab members are not the target population ... will refine the phrase count" (Participants)                                              |
| 2.4 timeline             | missing | none                                                                                                                                                                                           |
| 2.5 challenges           | missing | none                                                                                                                                                                                           |
| 6.1 hypotheses           | settled | H1, H2, "RQ1 ... (direction unclear)" (Hypotheses)                                                                                                                                             |
| 6.2 hypothesis form      | weak    | direction and variables named; "sources to be added"                                                                                                                                           |
| 6.5 interactions         | settled | "No interaction is expected: our field study gave no hint" (Hypotheses)                                                                                                                        |
| 6.6 smallest effect      | missing | none; H2 "no worse" needs equivalence bound                                                                                                                                                    |
| 6.7 decision rules       | missing | none                                                                                                                                                                                           |
| 7.1 IV                   | settled | "keyboard, tap or swipe, within subjects, because individual typing skill varies enormously" (Variables)                                                                                       |
| 7.2 carry-over           | settled | "carry-over between the keyboards is symmetric, each is a few minutes of practice away" (Variables)                                                                                            |
| 7.3 design named         | weak    | implied one-factor within; never named                                                                                                                                                         |
| 7.4 random assignment    | settled | "There is no between-subjects variable, since every participant uses both keyboards." (Variables)                                                                                              |
| 7.5 counterbalancing     | missing | none                                                                                                                                                                                           |
| 7.6 DVs                  | weak    | definitions, units, logging, speed+accuracy pairing present; no reliability or construct-validity statement                                                                                    |
| 7.7 controls             | weak    | listed; screening reasons given; no internal-vs-external validity weighing; phrase set, autocorrect, wrist, posture unset                                                                      |
| 7.8 random vars          | settled | "typing skill, mood, time of day, which vary by chance" (Variables)                                                                                                                            |
| 7.9 confounds            | weak    | "History might matter if some sessions run during exam week." No prevention; maturation, instrumentation absent                                                                                |
| 8.3 eligibility          | settled | "screened by a short form for handedness, age, phone ownership and no prior watch swipe use, because..." (Participants)                                                                        |
| 8.5–8.7 power            | BLOCKED | no count, no effect size; lme4 missing                                                                                                                                                         |
| 11.2 unit of analysis    | missing | none                                                                                                                                                                                           |
| 11.4 model family        | weak    | "A mixed ANOVA" conflicts with checklist (mixed-effects models); no between factor so "mixed" wrong anyway; rating unanalysed                                                                  |
| 11.5 fixed effects       | missing | none                                                                                                                                                                                           |
| 11.6 random effects      | missing | none                                                                                                                                                                                           |
| 11.7 inference           | missing | none                                                                                                                                                                                           |
| 11.8 exclusions          | missing | none                                                                                                                                                                                           |
| 11.9 alpha, multiplicity | missing | none                                                                                                                                                                                           |

Items in the printed table that the key does not list: none.

## First-round questions, with item IDs

- Q1, item 1.3, data retention.
- Q2, item 2.4, timeline.
- Q3, item 6.2, hypothesis sources.
- Q4, item 7.3, design name.
- Q5, item 7.5, counterbalancing
- Q6, item 7.6, dependent variables.
- Q7, item 7.7, control variables.
- Q8, item 7.9, confounds.

Item IDs asked in round 1: 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9. The power group (8.5, 8.6, 8.7) is asked in no round.

## Per-row comparison with the key

| Item | Expected | Got                         | Result |
| ---- | -------- | --------------------------- | ------ |
| 1.1  | settled  | settled                     | match  |
| 1.2  | settled  | settled                     | match  |
| 1.3  | weak     | weak                        | match  |
| 2.2  | missing  | missing                     | match  |
| 2.3  | settled  | settled                     | match  |
| 2.4  | missing  | missing                     | match  |
| 2.5  | missing  | missing                     | match  |
| 6.1  | settled  | settled                     | match  |
| 6.2  | weak     | weak                        | match  |
| 6.5  | settled  | settled                     | match  |
| 6.6  | missing  | missing                     | match  |
| 6.7  | missing  | missing                     | match  |
| 7.1  | settled  | settled                     | match  |
| 7.2  | settled  | settled                     | match  |
| 7.3  | missing  | weak                        | match  |
| 7.4  | settled  | settled                     | match  |
| 7.5  | missing  | missing                     | match  |
| 7.6  | weak     | weak                        | match  |
| 7.7  | weak     | weak                        | match  |
| 7.8  | settled  | settled                     | match  |
| 7.9  | weak     | weak                        | match  |
| 8.3  | settled  | settled                     | match  |
| 8.5  | missing  | BLOCKED (group row 8.5-8.7) | match  |
| 8.6  | missing  | BLOCKED (group row 8.5-8.7) | match  |
| 8.7  | missing  | BLOCKED (group row 8.5-8.7) | match  |
| 11.2 | missing  | missing                     | match  |
| 11.4 | weak     | weak                        | match  |
| 11.5 | missing  | missing                     | match  |
| 11.6 | missing  | missing                     | match  |
| 11.7 | missing  | missing                     | match  |
| 11.8 | missing  | missing                     | match  |
| 11.9 | missing  | missing                     | match  |

## Pass-bar criteria

- Every row keyed weak or missing appears as weak or missing (the power group as one row marked missing or BLOCKED): pass.
- No row keyed settled is asked in the first round: pass. Settled rows quoted from the material in the table: 1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3.
- One power-group row satisfies 8.5 to 8.7: pass (printed as `BLOCKED`).

## Verdict

PASS (32 of 32 key rows match).

## Notes

- Item 7.3 is keyed missing; the skill printed it weak ("implied one-factor within-subjects, never named" or equivalent). The key makes the two interchangeable, so it counts as a match.
- Only the first turn ran; no round was answered.
- The draft path was printed as a sentence at the start of round 1, not as a numbered question.
