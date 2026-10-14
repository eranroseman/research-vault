# review scenario, run 1

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
claude -p --continue "Apply fixes 7 and 13." --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

Supplementary turn 4 (scenario 6, not part of the scenario 5 bar; after `git add -A && git commit -qm after-fixes`):

```bash
claude -p --continue "Print the hand-off again." --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

## Transcript, decisive lines

Turn 1 stdout, final lines. The skill had already written `proposal/review.md` with the five attested rows as `pending` and then asked the batch (the SKILL says to ask before writing the file; the file existed after turn 1 with the attested rows pending):

```text
Review written to `proposal/review.md`. No draft edits yet.

**Result:** 79 items checked. Pass 51, fail 23, 5 attested items pending your answer, 2 defend-stage skipped. 20 consistency and brief findings. 21 fixes proposed, 0 waivers.

**Biggest problems:**
- Device is within subjects in draft; brief (7.1 to 7.4, 8.5) says between. Power analysis in brief assumes between, 12 per device. Draft's analysis cannot borrow that count. Brief's own 2.2 (both devices, 35 min) reads as within, so brief needs reconciling too. fix 21 / fix 10: decide, route via `/experiment-proposal:design`.
- Planned analysis uses paired t-test, Wilcoxon, RM-ANOVA on participant means. Items 11.2, 11.4 to 11.7 fail; brief says lmer on log time plus glmer on misses. fix 15 replaces paragraph.
- Exclusion rule "mean trackball time over 2000 ms" is condition-dependent; no 150/5000 ms trimming. fix 16.
- No SESOI (6.6, fix 5); decision rule never falsifies (6.7, fix 6).
- Consent says 20 minutes; session is 35. Missing retention period, withdrawal consequences, benefits. fix 1, fix 19.
- Make and model of devices are placeholders (2.1, 3.3, 13.11). fix 2: decide.
- Smaller: H2 uncited (fix 4), nine-combination order unstated (fix 7), no construct validity for movement time (fix 8), decline-without-consequence missing (fix 9), no illness/breakdown plan (fix 13), screening form not in appendix (fix 17), no appendix cross-references (fix 18), script lacks question point (fix 20), count not stated pre-specified (fix 11), effect-size ranking unstated (fix 12).

`proposal/power.R` cited by brief and draft but absent from `proposal/`.

research-grill not installed. Hand-off and install commands in review.md.

**Need from you, one batch:**

1. Item 3.1: template, length limit, citation style, section list identified? Do appendices and references count toward limit?
2. Item 5.2: snowballing stopped yielding new work? Brief's open item says lit-search for current-device comparison not run yet.
3. Item 11.10: analysis script dry-run on simulated data? Where is `proposal/power.R`?
4. Item 13.1: draft reviewed against seven reader questions and revised?
5. Item 13.4: reason for every Design choice on record? Device-within choice has no brief entry.
6. Which fixes should I apply? Give their numbers. Fixes 2, 10, 17, 21 are decisions, not paste-ins. For any failure you will not fix, give a waiver reason and I record it.
```

Turn 2 stdout:

```text
Recorded. review.md updated: 3.1, 5.2, 13.4 pass, confirmed 2026-10-14. 11.10 and 13.1 fail with your answer; 11.10 added to 13.5's list. Summary now pass 54, fail 25.

11.10 and 13.1 stay failed until done or waived. 11.10 needs `proposal/power.R` run without error on simulated data; file not in `proposal/` now. 13.1 is your own pass over the seven reader questions.

Which fixes should I apply? Give their numbers. Fixes 2, 10, 17, 21 are decisions. For any failure you will not fix, give a waiver reason.
```

Turn 3 stdout:

```text
Fixes 7 and 13 applied to `proposal/draft.md`. Draft changed in two places only:
- Design: random order of nine combinations per participant, equal counts, software-drawn.
- Procedure: experimenter illness and equipment failure plan, spare devices.

Re-checked: 7.5 pass, 10.5 pass, brief entry 7.5 now consistent. 13.5 still fails on 21 items. Summary: pass 56, fail 23, findings 19.

Still open: 21 failing items, 19 fixes unapplied (1 to 6, 8 to 12, 14 to 21). Decisions 2, 10, 17, 21 block the mixed-model and power fixes. 11.10 and 13.1 need your own work or waiver.

Next: more fix numbers, or waiver reasons. Hand-off in review.md stands: install research-grill, then `/oss:research-grill defend proposal/draft.md`.
```

## Scoring against the key (first pass: review.md after turn 2, committed as `first-pass`)

Summary line of the first pass: `Items checked: 79. Pass: 54. Fail: 25. Not checked (defend-stage): 2. Consistency and brief findings: 20. Fixes proposed: 21. Waivers: 0.`

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

51 draft-checked pass rows (items 1.1 to 12.6 and the substance tests). 50 carry a quotation-marked passage with its location. One row, 3.2, lists the section headings verbatim without quotation marks and cites "(section headings)" as the location; counted as quoted evidence, flagged as borderline. The pass rows were checked mechanically: every quoted string occurs verbatim in the draft (the one mismatch, 4.3, is the three contribution bullets joined with semicolons).

### 13.2 and 13.3

Both rows read `not checked: defend-stage`.

### Summary

`Items checked: 79. Pass: 54. Fail: 25. Not checked (defend-stage): 2. Consistency and brief findings: 20. Fixes proposed: 21. Waivers: 0.` (after the attested answers: 3.1, 5.2 and 13.4 confirmed 2026-10-14; 11.10 and 13.1 failed with the user's words).

## Fix-picking check

D4 is item 7.5 (fix 7); D7 is item 10.5 (fix 13). Turn 3 asked for fixes 7 and 13.

- `git diff` of `proposal/draft.md`: exactly two hunks. One adds the nine-combination order sentence in Design; one adds the illness and equipment-failure sentences at the end of Procedure. No other change.
- `git diff` of `proposal/review.md` changed only: the 7.5 row (now `pass (fix 7 applied)` with a new quote), the 10.5 row (`pass (fix 13 applied)` with a new quote), the 13.5 row (re-checked, still fail, list shorter by two), the 7.5 entry under Brief against draft (now resolved or consistent), and the Summary line and one seed line under Hand-off. Every other row is byte-identical.
- Summary after the fixes: `Items checked: 79. Pass: 56. Fail: 23. Not checked (defend-stage): 2. Consistency and brief findings: 19. Fixes proposed: 21. Fixes applied: 2 (7, 13). Waivers: 0.`

## Missing-input checks

Recorded here for all three runs (run once, in copies of this run-1 project; the copies still held the first-pass review.md):

Brief removed (`rm proposal/design-brief.md`), then `claude -p "/experiment-proposal:review" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"`:

```text
No design brief at proposal/design-brief.md; run /experiment-proposal:design first.
```

Stops, names the brief, says to run `/experiment-proposal:design` first. `proposal/review.md` unchanged. Pass.

Draft removed (`rm proposal/draft.md`, brief restored), same command:

```text
Draft missing. Brief frozen (2026-10-10), its `Draft:` line points to `proposal/draft.md`. No path named with the command. Tried `proposal/draft.md`; file not there. Stopping.
```

Stops and names `proposal/draft.md`. `proposal/review.md` unchanged. Pass.

## Pass bar

| Criterion                                   | Result                         | Evidence                                                    |
| ------------------------------------------- | ------------------------------ | ----------------------------------------------------------- |
| At least 11 of 12 caught, 0 passed          | pass                           | 12 of 12 caught, 0 passed                                   |
| Every draft-checked pass quotes evidence    | pass (one borderline row, 3.2) | see the quotes paragraph                                    |
| At most two over-failures                   | pass                           | 0 over-failure(s)                                           |
| Fix-picking check holds                     | pass                           | two draft hunks; review.md changed only in the allowed rows |
| Missing-input checks stop and name the file | pass                           | recorded in review-1.md                                     |
| 13.2 and 13.3 marked not checked            | pass                           | both rows                                                   |

## Verdict

Run 1 of scenario 5: pass.
