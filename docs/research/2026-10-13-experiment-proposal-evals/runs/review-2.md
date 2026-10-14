# review scenario, run 2

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
claude -p --continue "Apply fixes 8 and 13." --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

Supplementary turn 4 (scenario 6, not part of the scenario 5 bar; after `git add -A && git commit -qm after-fixes`):

```bash
claude -p --continue "Print the hand-off again." --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

## Transcript, decisive lines

Turn 1 stdout, final lines. The skill had already written `proposal/review.md` with the five attested rows as `pending` and then asked the batch (the SKILL says to ask before writing the file; the file existed after turn 1 with the attested rows pending):

```text
Review written to `proposal/review.md`. Draft fails 25 of 79 items. Big picture: draft departs from frozen brief on core design.

**Main problems**

- **Device within subjects in draft; brief says between.** Cascades: carry-over claim, design name, random assignment, power analysis (brief's 24 = 12 per device, between), random effects. Fix 20: `decide:` amend brief via `/experiment-proposal:design`, or move draft back to between subjects.
- **Planned analysis uses t-test, Wilcoxon, RM-ANOVA.** No mixed model, no fixed/random effects, no inference method. Items 11.2, 11.4 to 11.7 fail. Fix 14 gives replacement paragraph from brief.
- **Exclusion rule conditional on condition performance** (trackball mean over 2000 ms). No trimming bounds. Fix 15.
- **No SESOI, no decision rule.** Draft says null = "not supported rather than refuted". Items 6.6, 6.7, 13.7 fail. Fixes 5, 6.
- **Consent form says 20 minutes; session is 35.** No retention period, no withdrawal consequence, no contact address. Fixes 17, 18.
- **Devices unnamed** ("each a named make and model" placeholder). Items 2.1, 7.1 fail; four substance tests pass narrowly on this doubt. Fix 2.
- Smaller: H2 uncited (fix 4), nine combinations not randomized (fix 8), no decline-without-consequence statement (fix 10), no illness or breakdown plan (fix 13), appendix refs missing (fix 16), script lacks question point (fix 19), Procedure in present tense (fix 3).

**Need from you**

1. Attested items, confirm yes or no for each:
   - 3.1: template, length limit, citation style, section list identified?
   - 5.2: snowballing stopped turning up new work? (brief still lists open lit-search for H1)
   - 11.10: `proposal/power.R` ran end to end without error?
   - 13.1: reviewed against seven reader questions and revised?
   - 13.4: reason for every Design choice can be given?
2. Which fixes should I apply? Give their numbers (1 to 21). Fix 20 decides direction for fixes 14 and 21; pick it first.

research-grill not installed. Install commands in review.md Hand-off section. Advisor was rate-limited this turn; review not advisor-checked.
```

Turn 2 stdout:

```text
Recorded. 3.1, 5.2, 13.4 pass, confirmed 2026-10-14. 11.10 and 13.1 fail with your words. Summary now: pass 52, fail 27.

11.10 and 13.1 have no draft fix. Options: run `proposal/power.R` end to end and do the seven-question review, then tell me; or waive each with a reason I record verbatim.

Which fixes should I apply? Give their numbers (1 to 21). Fix 20 first: it decides whether fix 14 and fix 21 keep device between subjects.
```

Turn 3 stdout:

```text
Fixes 8 and 13 applied to `proposal/draft.md`; nothing else touched.

**Changed**

- **Design:** added random order of nine combinations sentence. Item 7.5 now pass. Brief departure 7.5 resolved.
- **Procedure:** added illness and equipment-failure sentences. Item 10.5 now pass.
- **13.5** re-checked: still fail, 22 items of steps 1 to 12 remain.
- Cross-section consistency: unaffected. Hand-off: unchanged.

Summary now: pass 54, fail 25, fixes applied 2 of 21, waivers 0.

**Still open**

- 19 unapplied fixes. Fix 20 (device between vs within) still gates fixes 14 and 21.
- 11.10 (power.R dry run) and 13.1 (seven-question review): no draft fix; do them or waive with a reason.

More fix numbers, or waivers?
```

## Scoring against the key (first pass: review.md after turn 2, committed as `first-pass`)

Summary line of the first pass: `Items checked: 79. Pass: 52. Fail: 27. Not checked (defend-stage): 2. Consistency and brief findings: 19. Fixes proposed: 21. Waivers: 0.`

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

Items 1.1, 4.1 to 4.5, 5.1, 5.3, 6.3, 6.5, 7.7, 7.8, 7.9, 8.4, 8.8, 8.9, 9.1 to 9.4, 10.1 to 10.4, 11.1, 11.3, 11.9, 12.4 and 12.6 (29 items): 0 of the 29 control items failed. Over-failures: none (0 over-failures)

### Quotes on draft-checked passes

All draft-checked pass rows in the Items section carry a quotation-marked passage with its location (0 without a quote). The file also repeats the substance tests 13.6 to 13.11 in a second "Substance tests" section; there the narrow-pass rows 13.9, 13.10 and 13.11 give only the doubt and "see the row above", but their Items-section rows quote passages (13.9 the third contribution, 13.10 the H3 test sentence, 13.11 the Timeline sentence). Counted as quoted; the duplicated rows are an output-format deviation (the SKILL template lists 13.6 to 13.11 only under Substance tests). Every quoted string occurs verbatim in the draft except 4.3 (bullets joined with semicolons).

### 13.2 and 13.3

Both rows read `not checked: defend-stage`.

### Summary

`Items checked: 79. Pass: 52. Fail: 27. Not checked (defend-stage): 2. Consistency and brief findings: 19. Fixes proposed: 21. Waivers: 0.` (after the attested answers: 3.1, 5.2 and 13.4 confirmed 2026-10-14; 11.10 and 13.1 failed with the user's words).

Other observation: Turn 1 stdout ended with "Advisor was rate-limited this turn; review not advisor-checked." The session reached for an advisor tool the harness provides; the SKILL does not mention one.

## Fix-picking check

D4 is item 7.5 (fix 8); D7 is item 10.5 (fix 13). Turn 3 asked for fixes 8 and 13.

- `git diff` of `proposal/draft.md`: exactly two hunks. One adds the nine-combination order sentence in Design; one adds the illness and equipment-failure sentences at the end of Procedure. No other change.
- `git diff` of `proposal/review.md` changed only: the 7.5 row (now `pass (fix 8 applied)` with a new quote), the 10.5 row (`pass (fix 13 applied)` with a new quote), the 13.5 row (re-checked, still fail, list shorter by two), the 7.5 entry under Brief against draft (now resolved or consistent), and the Summary line. Every other row is byte-identical.
- Summary after the fixes: `Items checked: 79. Pass: 54. Fail: 25. Not checked (defend-stage): 2. Consistency and brief findings: 19 (1 resolved by fix 8). Fixes proposed: 21. Fixes applied: 2 (8, 13). Waivers: 0.`

## Missing-input checks

Done once, in review-1.md (copies of the run-1 project); the README clause "With the brief or the draft removed" is part of scenario 5 and is recorded there.

## Pass bar

| Criterion                                   | Result | Evidence                                                    |
| ------------------------------------------- | ------ | ----------------------------------------------------------- |
| At least 11 of 12 caught, 0 passed          | pass   | 12 of 12 caught, 0 passed                                   |
| Every draft-checked pass quotes evidence    | pass   | see the quotes paragraph                                    |
| At most two over-failures                   | pass   | 0 over-failure(s)                                           |
| Fix-picking check holds                     | pass   | two draft hunks; review.md changed only in the allowed rows |
| Missing-input checks stop and name the file | pass   | recorded in review-1.md                                     |
| 13.2 and 13.3 marked not checked            | pass   | both rows                                                   |

## Verdict

Run 2 of scenario 5: pass.
