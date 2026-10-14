# Scenario 2 (material with gaps), run 2

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

| Item                     | Status  | Passage or gap                                                                                                                                                       |
| ------------------------ | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1 question             | settled | "Does entering text on a 40 mm smartwatch with a swipe keyboard change words per minute... because those are the two keyboards the watch ships with" (Question, l.5) |
| 1.2 ethics               | settled | "submitted under the department's standing protocol... committee has told us covers keyboard comparisons" (Ethics, l.9)                                              |
| 1.3 data plan            | weak    | reasons and access given; "Retention: to be decided" (Data, l.13)                                                                                                    |
| 2.2 trials, session      | missing | no trials per condition, no session estimate                                                                                                                         |
| 2.3 pilot                | settled | "three people from the lab, data not reported, because lab members are not the target population" (l.36)                                                             |
| 2.4 timeline             | missing | none                                                                                                                                                                 |
| 2.5 challenges           | missing | exam week named, no response                                                                                                                                         |
| 6.1 hypotheses/RQs       | settled | H1, H2, RQ1 "direction unclear" (l.29-31)                                                                                                                            |
| 6.2 hypothesis content   | weak    | H1 "sources to be added"; H2 has no cited basis                                                                                                                      |
| 6.5 interactions         | settled | "No interaction is expected: our field study gave no hint" (l.32)                                                                                                    |
| 6.6 smallest effect      | missing | none; H2 "no worse" needs equivalence bound                                                                                                                          |
| 6.7 decision rules       | missing | none                                                                                                                                                                 |
| 7.1 IV                   | settled | "within subjects, because individual typing skill varies enormously" (l.17)                                                                                          |
| 7.2 carry-over           | settled | "symmetric, each is a few minutes of practice away" (l.17)                                                                                                           |
| 7.3 design named         | weak    | implied one-factor within-subjects, never named                                                                                                                      |
| 7.4 random assignment    | settled | "no between-subjects variable, since every participant uses both" (l.21)                                                                                             |
| 7.5 counterbalancing     | missing | none                                                                                                                                                                 |
| 7.6 DVs                  | weak    | definitions, units, logging, scale given; no reliability or construct-validity statement                                                                             |
| 7.7 controls             | weak    | listed; no internal-vs-external validity weighing; eligibility mixed in                                                                                              |
| 7.8 random variables     | settled | "typing skill, mood, time of day... left to chance" (l.20)                                                                                                           |
| 7.9 confounds            | weak    | history only, no prevention; maturation, instrumentation absent                                                                                                      |
| 8.3 eligibility          | settled | screening form with reasons (l.36)                                                                                                                                   |
| 8.5/8.6/8.7 power        | BLOCKED | none in material; lme4 missing                                                                                                                                       |
| 11.2 unit of analysis    | missing | none                                                                                                                                                                 |
| 11.4 model family        | weak    | "mixed ANOVA" conflicts with checklist mixed models; also no between factor exists                                                                                   |
| 11.5 fixed effects       | missing | none                                                                                                                                                                 |
| 11.6 random effects      | missing | none                                                                                                                                                                 |
| 11.7 inference           | missing | none                                                                                                                                                                 |
| 11.8 exclusions          | missing | none                                                                                                                                                                 |
| 11.9 alpha, multiplicity | missing | none                                                                                                                                                                 |

Items in the printed table that the key does not list: none.

## First-round questions, with item IDs

- Q0.
- Q1. Item 1.3, raw data retention.
- Q2. Item 2.4, timeline.
- Q3. Item 6.2, hypothesis sourcing.
- Q4. Item 7.3, design name.
- Q5. Item 7.5, counterbalancing
- Q6. Item 7.6, dependent variables: reliability and construct validity.
- Q7. Item 7.7, control variables.
- Q8. Item 7.9, confounds.

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
- Q0 (the draft path, `proposal/draft.md`) is the skill's one-time ask, not a design-tree item. Q7 (item 7.7) proposed moving the eligibility criteria out of the controls and named 8.3 in its reason line; 8.3 itself was not a question.
