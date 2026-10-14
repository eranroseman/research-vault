# review scenario, run 3

Date: 2026-10-14. Plugin commit: `16f7bb6`. Scenario 5 (`review` on the proposal with 12 planted defects). Fixtures: `fixtures/proposal-with-defects.md`, `.brief.md`, `.key.md`. Scratch project: `<scratch>`, outside the repository.

## Commands

Setup:

```bash
tmp=$(mktemp -d) && cd "$tmp" && git init -q && git commit --allow-empty -qm init && mkdir proposal
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.brief.md proposal/design-brief.md
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.md proposal/draft.md
git add -A && git commit -qm fixtures
P=<checkout>/plugins/experiment-proposal
```

Turn 1 (prompt before `--allowedTools`):

```bash
claude -p "/experiment-proposal:review" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

Turn 2, the attested batch. A first attempt put the prompt after `--allowedTools "Read,Write,Edit"` (with stdin from `/dev/null`) and failed at once with `Error: No deferred tool marker found in the resumed session ... Provide a prompt to continue the conversation.` (the prompt was swallowed by `--allowedTools`; nothing ran). Rerun with the prompt before the flag:

```bash
claude -p --continue "Confirm 3.1, 5.2 and 13.4; 11.10 and 13.1 not done." --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
git add -A && git commit -qm first-pass
```

Turn 3, the fix-picking check:

```bash
claude -p --continue "Apply fixes 8 and 14." --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

Supplementary turn 4 (scenario 6, not part of the scenario 5 bar; after `git add -A && git commit -qm after-fixes`):

```bash
claude -p --continue "Print the hand-off again." --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

## Transcript, decisive lines

Turn 1 stdout, final lines. The skill had already written `proposal/review.md` with the five attested rows as `pending` and then asked the batch (the SKILL says to ask before writing the file; the file existed after turn 1 with the attested rows pending):

```text
Review written to `proposal/review.md`. Not done: 5 attested items and fix selection need you.

**Result:** 79 items checked. 48 pass, 26 fail, 5 pending your confirmation, 2 defend-stage not checked. 1 consistency mismatch, 18 brief departures. 22 fixes proposed. No waivers.

**Big problems:**
- Draft puts device within subjects; brief froze it between (7.1 to 7.4, 7.9, 8.5). Fix 21 is a decide: amend brief via `/experiment-proposal:design`, or rewrite draft to between.
- Planned analysis uses paired t-test, Wilcoxon, ANOVA, participant means. Brief froze lmer/glmer on trials. Items 11.2, 11.4 to 11.7 fail. Fix 15 pastes brief's analysis; assumes device between.
- Exclusion rule conditional on trackball performance, no trimming bounds (11.8, fix 16).
- No SESOI (6.6), decision rule falsifies nothing (6.7, 13.7), H2 uncited (6.2).
- Consent form says 20 minutes, session is 35; no retention period, no decline consequences, no contact address (12.3, 1.3).
- Devices unnamed, "each a named make and model" placeholder (2.1, 7.1, 3.3).
- Smaller: 7.2, 7.5, 7.6, 8.2, 8.5, 8.6, 10.3, 10.5, 12.2, 12.5.

**Attested items, confirm each (yes, or what to record):**
1. 3.1: template, length limit, citation style, section list identified; appendices and references count toward limit?
2. 5.2: snowballing stopped turning up new work? Brief's Open item 1 says lit-search not yet run.
3. 11.10: analysis script dry-run end to end on simulated data? Brief says power.R ran 2026-10-10.
4. 13.1: draft reviewed against seven reader questions and revised?
5. 13.4: reason for every Design choice can be given? Draft's device-within departs from brief rationale.

**Which fixes should I apply? Give their numbers.** Fixes 2, 19, 21 are decide fixes; give decision text too.

One note outside review scope: brief states SESOI in ms, but its model runs on log movement time. Scale mismatch. Fair grill objection; a brief amendment, not mine to make.

research-grill not installed. Install commands and seed objections are in the Hand-off section of review.md.
```

Turn 2 stdout:

```text
Recorded. 3.1, 5.2, 13.4 pass, confirmed 2026-10-14. 11.10 and 13.1 fail with your words. 13.5 now also lists 11.10. Summary: pass 51, fail 28.

11.10 and 13.1 have no draft fix: 11.10 needs the dry run of the analysis script on simulated data, 13.1 the seven-reader-question pass. Do them later and re-run review, or waive each with a reason I record verbatim.

Still need from you:

1. Which fixes should I apply? Give their numbers (1 to 22).
2. For decide fixes you pick, the decision: fix 2 device make and model; fix 19 contact addresses; fix 21 device between (rewrite draft) or within (amend brief via `/experiment-proposal:design`).
3. Waiver or not for 11.10 and 13.1, with reason if waived.
```

Turn 3 stdout:

```text
Applied fixes 8 and 14 to draft.md. Re-checked.

- **7.5** now pass: random order of nine combinations added to Design, para 1. Brief departure 7.5 resolved.
- **10.5** now pass: illness and equipment contingency added to end of Procedure.
- **13.5** still fails; list shrinks by two.
- Summary: pass 53, fail 26, brief and consistency findings 18, fixes applied 2 of 22.

Nothing else touched. Cross-section consistency unchanged.

Still open, 26 fails. Review not done until each passes or carries a waiver. Next from you:

1. More fix numbers to apply (1 to 7, 9 to 13, 15 to 22), or none.
2. Decisions for fixes 2, 19, 21 if picked.
3. Waiver with reason for any fail you will not fix, including 11.10 and 13.1.
```

## Scoring against the key (first pass: review.md after turn 2, committed as `first-pass`)

Summary line of the first pass: `Items checked: 79. Pass: 51. Fail: 28. Not checked (defend-stage): 2. Consistency and brief findings: 19. Fixes proposed: 22. Waivers: 0.`

### D1 to D12

| Defect | Item or section     | Result                                                                              | Verdict |
| ------ | ------------------- | ----------------------------------------------------------------------------------- | ------- |
| D1     | 1.3                 | fail                                                                                | caught  |
| D2     | 6.2                 | fail                                                                                | caught  |
| D3     | 6.6                 | fail (and Brief against draft entry 6.6)                                            | caught  |
| D4     | 7.5                 | fail                                                                                | caught  |
| D5     | 7.6                 | fail                                                                                | caught  |
| D6     | 8.2                 | fail                                                                                | caught  |
| D7     | 10.5                | fail                                                                                | caught  |
| D8     | 11.4                | fail (11.5 to 11.7 also fail)                                                       | caught  |
| D9     | 11.8                | fail                                                                                | caught  |
| D10    | 12.5                | fail                                                                                | caught  |
| D11    | 12.3                | fail (and Cross-section consistency: 35 vs "about 20 minutes")                      | caught  |
| D12    | Brief against draft | 7.1 departure reported (brief "device between subjects" vs draft "within subjects") | caught  |

Caught 12 of 12, passed 0. (D12 scored by the Brief-against-draft section alone, as the key says.)

### Controls

Items 1.1, 4.1 to 4.5, 5.1, 5.3, 6.3, 6.5, 7.7, 7.8, 7.9, 8.4, 8.8, 8.9, 9.1 to 9.4, 10.1 to 10.4, 11.1, 11.3, 11.9, 12.4 and 12.6 (29 items): 28 of the 29 control items passed; 10.3 failed. Over-failures: 1 over-failure: 10.3 fail ("the target-selection program and the display are never named at the point of use in the Procedure"; the procedure names the devices, the practice trials, the script and the questionnaire, so the row should pass). Within the limit of two.

### Quotes on draft-checked passes

48 draft-checked pass rows, all carry a quotation-marked passage with its location (0 without a quote). Every quoted string occurs verbatim in the draft except 4.3 (bullets joined with semicolons).

### 13.2 and 13.3

Both rows read `not checked: defend-stage`.

### Summary

`Items checked: 79. Pass: 51. Fail: 28. Not checked (defend-stage): 2. Consistency and brief findings: 19. Fixes proposed: 22. Waivers: 0.` (after the attested answers: 3.1, 5.2 and 13.4 confirmed 2026-10-14; 11.10 and 13.1 failed with the user's words).

## Fix-picking check

D4 is item 7.5 (fix 8); D7 is item 10.5 (fix 14). Turn 3 asked for fixes 8 and 14.

- `git diff` of `proposal/draft.md`: exactly two hunks. One adds the nine-combination order sentence in Design; one adds the illness and equipment-failure sentences at the end of Procedure. No other change.
- `git diff` of `proposal/review.md` changed only: the 7.5 row (now `pass (fix 8 applied)` with a new quote), the 10.5 row (`pass (fix 14 applied)` with a new quote), the 13.5 row (re-checked, still fail, list shorter by two), the 7.5 entry under Brief against draft (now resolved or consistent), and the Summary line. Every other row is byte-identical.
- Summary after the fixes: `Items checked: 79. Pass: 53. Fail: 26. Not checked (defend-stage): 2. Consistency and brief findings: 18 (one brief departure, 7.5, resolved by fix 8). Fixes proposed: 22. Fixes applied: 2 (8, 14). Waivers: 0.`

## Missing-input checks

Done once, in review-1.md (copies of the run-1 project); the README clause "With the brief or the draft removed" is part of scenario 5 and is recorded there.

## Pass bar

| Criterion                                   | Result | Evidence                                                    |
| ------------------------------------------- | ------ | ----------------------------------------------------------- |
| At least 11 of 12 caught, 0 passed          | pass   | 12 of 12 caught, 0 passed                                   |
| Every draft-checked pass quotes evidence    | pass   | see the quotes paragraph                                    |
| At most two over-failures                   | pass   | 1 over-failure(s)                                           |
| Fix-picking check holds                     | pass   | two draft hunks; review.md changed only in the allowed rows |
| Missing-input checks stop and name the file | pass   | recorded in review-1.md                                     |
| 13.2 and 13.3 marked not checked            | pass   | both rows                                                   |

## Verdict

Run 3 of scenario 5: pass.
