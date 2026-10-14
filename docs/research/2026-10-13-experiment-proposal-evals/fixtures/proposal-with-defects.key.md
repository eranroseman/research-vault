# Scenario 5 key: the twelve planted defects

`review` runs with the brief and the draft copied to `proposal/design-brief.md` and `proposal/draft.md`. A defect is caught when the row or section the key names reports a failure that describes it; it is passed (the worst outcome) when that item is marked pass. Pass bar: at least 11 of 12 caught, 0 passed; every draft-checked pass in the file quotes a passage with its location.

| Defect | Where in the draft                                                                                                                                                          | Expected failing item or section                      |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| D1     | No retention period for the raw data anywhere; who has access appears only in the consent form, and no section gives the reason for the identifiable data (age, handedness) | item 1.3                                              |
| D2     | H2 states a direction and cites no source                                                                                                                                   | item 6.2                                              |
| D3     | No smallest effect size of interest anywhere (the brief has one; the draft dropped it)                                                                                      | item 6.6, and the Brief against draft section for 6.6 |
| D4     | The order of the nine distance-and-size combinations is never counterbalanced or randomized (only device order is)                                                          | item 7.5                                              |
| D5     | Movement time has a reliability statement but no construct-validity statement                                                                                               | item 7.6                                              |
| D6     | Recruitment from the author's own course section with no way to decline without consequence stated                                                                          | item 8.2                                              |
| D7     | Nothing on illness or equipment failure                                                                                                                                     | item 10.5                                             |
| D8     | A paired t-test, Wilcoxon and a repeated-measures ANOVA with a sphericity check; no mixed-effects model                                                                     | item 11.4 (and 11.5 to 11.7 may fail with it)         |
| D9     | Exclusion of participants whose trackball time exceeds 2000 ms depends on how they responded in a condition                                                                 | item 11.8                                             |
| D10    | The script has no point where participants can ask questions                                                                                                                | item 12.5                                             |
| D11    | The consent form says "about 20 minutes"; the session estimate is 35 minutes                                                                                                | item 12.3, and the Cross-section consistency section  |
| D12    | Device is within subjects in the draft; the frozen brief says between subjects (items 7.1, 7.2, 7.3, 7.4)                                                                   | the Brief against draft section, entry 7.1            |

Also expected to pass, as controls that the review does not over-fail: items 1.1, 4.1 to 4.5, 5.1, 5.3, 6.3, 6.5, 7.7, 7.8, 7.9, 8.4, 8.8, 8.9, 9.1 to 9.4, 10.1 to 10.4, 11.1, 11.3, 11.9, 12.4, 12.6. Items 13.2 and 13.3 must be marked not checked.

## The fix-picking check

After the first pass, answer "Apply fixes <the two numbers that correspond to D4 and D7>". Expected: only those two passages change in the draft (`git diff` in the scratch project shows two hunks), the rows for 7.5 and 10.5 are re-checked, and no other row or passage changes.

## The missing-input check

Run twice more in a copy of the project: once with `proposal/design-brief.md` deleted (expected: stops, names the brief and says to run `/experiment-proposal:design` first) and once with `proposal/draft.md` deleted (expected: stops and names `proposal/draft.md`).
