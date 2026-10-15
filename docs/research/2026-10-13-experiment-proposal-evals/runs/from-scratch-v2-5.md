# Scenario 3, from scratch, run v2-5 (0.2.0, design fix ed96208)

Date: 2026-10-15. Plugin commit: 76e9c28 (plugin version 0.2.0; the brief's `Checklist:` line reads `experiment-proposal 0.2.0`). The harness file names 5e13529; for this run the plugin commit is 76e9c28, which carries the design fix ed96208 (the one that matters for this scenario: a settled item stays settled, the frontier is listed above Q1, the checker runs each round, the draft path defaults) and the review and fixture fix 76e9c28. Scenario label: from-scratch. Driver: headless `claude -p` turns through `/tmp/ep-eval/review-v2-drive.sh`, answered strictly from `fixtures/from-scratch-answers.md`; "I don't know" for anything the sheet does not answer; the brief and the freeze approved when asked. Ten turns, one session (`session_id` d055e83a-e628-41c8-92c5-d5e8013590c7 on every turn's init event), model `--model opus` (the init event reports `claude-opus-5`, Claude Code 2.1.273).

Verdict: PASS. Every bar criterion holds: 21 of 21 design-tree items have an entry (17 settled, 1 pilot settles, 3 provisional), 2.4 is provisional, 2.2 is pilot settles, 8.5 is settled and justified from the sheet, six hci-researcher calls (none an error), the checker exits 0 on the frozen brief with empty stdout and stderr, and the freeze commit `9c93370 Freeze the design brief` exists with its `git add && git commit` run (not refused). No turn was rate limited. Diagnostics: no numbered question asked a settled item's decision again and no settled entry changed after it was written (v2-1: three asked); one unnumbered pre-approval offer on settled item 2.5 and one note on settled item 7.4 remain; items 7.7 and 7.9 were asked once each and ended provisional because of sub-questions the sheet does not answer.

## Rate limit

No turn hit a limit. For every turn the final `result` event has `api_error_status` null, `is_error` false, `terminal_reason` `completed`, and every `rate_limit_event` reads `"status":"allowed"`; `rc=0` in each `.meta`. Wall time per turn: 83, 204, 234, 241, 69, 51, 36, 47, 142 and 22 seconds (1129 s in all).

## Plugin integrity

`git diff --name-only 76e9c28 HEAD -- plugins/` printed nothing and `git status --porcelain plugins/` printed nothing, both at the end of the run. HEAD moved from 76e9c28 to d692e49 while the run went on (two documentation commits at 02:49 and 02:50 local, `e7dfcb1` and `d692e49`, touching only `docs/research/2026-10-13-experiment-proposal-evals/fixtures/material-with-gaps.md` and `docs/superpowers/plans/2026-10-14-experiment-proposal-v2.md`), so the plugin files loaded by `--plugin-dir "$P"` are those of 76e9c28. The init event of turn 1 lists the plugin as `experiment-proposal@inline`, version 0.2.0, from the `$P` path, and the agent `experiment-proposal:hci-researcher`.

## Commands

`$P` is `<checkout>/plugins/experiment-proposal`; `$S` is `/tmp/ep-eval/from-scratch-v2-5`, created fresh (the directory did not exist) with:

```text
mkdir "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval && git commit --allow-empty -qm init
```

No fixtures and no `proposal/` directory: the scenario gives only the idea. The helper `bash /tmp/ep-eval/review-v2-drive.sh "$S" <turn>` runs, with the prompt read from `$S.turn<N>.prompt`:

Turn 1:

```text
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null
```

Turns 2 to 10 (the same, with `--continue` before the model flag):

```text
cd "$S" && timeout 1800 claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn$t.jsonl" 2> "$S.turn$t.err" < /dev/null
```

After the run, the checker from the scratch project, stdout, stderr and exit code captured separately:

```text
cd "$S" && python3 "$P/scripts/check_proposal.py" brief proposal/design-brief.md > /tmp/ep-eval/v2-5.chk.out 2> /tmp/ep-eval/v2-5.chk.err; echo "exit=$?"
```

## Turns

Round N is the set of numbered questions at the end of turn N's reply; its answers are turn N+1's prompt.

| Turn | Sent                                                                                                 | Came back                                                                                                                                                                                                                                                  | Wall time |
| ---- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 1    | `/experiment-proposal:design` with the idea                                                          | Extraction table (0 settled, 6 weak, 15 missing); draft path defaulted to `proposal/draft.md` with no question; open brief written; checker clean (first call refused, retried); "Frontier: item 1.1"; round 1 = Q1 item 1.1                               | 83 s      |
| 2    | Item 1.1 from the sheet                                                                              | 1.1 settled and written; checker clean; two hci-researcher calls (7.1, 7.6); "Frontier: items 1.2, 1.3, 6.1, 7.1, 7.6"; round 2 = Q1 to Q5                                                                                                                 | 204 s     |
| 3    | Items 1.2, 1.3, 6.1, 7.1, 7.6 from the sheet                                                         | Those five settled (brief rewritten whole); checker clean; three hci-researcher calls (7.7, 7.9, 6.2); "Frontier: items 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9"; round 3 = Q1 to Q7, with an autocorrect fork inside Q5 and a deletions-per-word call inside Q7 | 234 s     |
| 4    | Items 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9 from the sheet; "I don't know" on the two sub-forks          | One hci-researcher call (7.5); 6.2, 6.5, 7.2, 7.4, 7.8 settled, 7.7 and 7.9 provisional, all written this turn; checker exit 1 (a 404-character 7.9 Decision), fixed, clean; "Frontier: items 7.3, 7.5, 8.3"; round 4 = Q1 to Q3                           | 241 s     |
| 5    | Items 7.3, 7.5, 8.3 from the sheet                                                                   | Those three settled; checker clean; "Frontier: items 2.2 and 8.5"; round 5 = Q1, Q2                                                                                                                                                                        | 69 s      |
| 6    | Items 2.2 and 8.5 from the sheet                                                                     | 2.2 pilot settles, 8.5 settled; checker clean; "Frontier: item 2.3"; round 6 = Q1                                                                                                                                                                          | 51 s      |
| 7    | Item 2.3 from the sheet                                                                              | 2.3 settled; checker clean; "Frontier: item 2.4"; round 7 = Q1                                                                                                                                                                                             | 36 s      |
| 8    | Item 2.4 "I don't know yet"                                                                          | 2.4 provisional, written this turn; Open items rebuilt; checker clean; "Frontier: item 2.5"; round 8 = Q1                                                                                                                                                  | 47 s      |
| 9    | Item 2.5 from the sheet                                                                              | 2.5 settled; Open items rebuilt; checker clean twice; git identity confirmed; 21 of 21 entries; four notes (one an offer on settled 2.5, one on settled 7.4) and "Approve the brief for freezing?"                                                         | 142 s     |
| 10   | "On the running-short-of-time response for item 2.5: I don't know ... Yes, I approve ... Freeze it." | `Status: frozen 2026-10-15`, checker exit 0 (no output), `git add proposal/design-brief.md && git commit -m "Freeze the design brief" -- proposal/design-brief.md` ran: `[master 9c93370] Freeze the design brief`                                         | 22 s      |

Turn texts, verbatim (the files `$S.turn<N>.prompt`):

Turn 1:

```text
/experiment-proposal:design Novice smartphone users entering text: does a swipe keyboard beat tap typing? Within subjects, two keyboards, phrases from a standard set, speed and errors logged, plus a 1 to 7 ease rating after each keyboard.
```

Turn 2:

```text
Item 1.1 (Q1): "Does entering phrases with a swipe keyboard, compared with a tap keyboard, change words per minute for novice smartphone users?" Levels: tap, swipe.
```

Turn 3:

```text
Item 1.2 (Q1): The university IRB; minimal-risk expedited review, about three weeks; a consent form and the phrase set are required.
Item 1.3 (Q2): Keystroke logs and phrase times only, no names linked, no recordings; the two experimenters have access; raw data kept five years, then deleted.
Item 6.1 (Q3): H1 directional (swipe faster); H2 "no worse" on errors; RQ1 on the ease rating (unsure of direction).
Item 7.1 (Q4): Keyboard: the phone's built-in tap keyboard versus its swipe mode; within subjects because typing skill varies hugely between people.
Item 7.6 (Q5): Words per minute (characters over five over minutes, app-logged, ratio); uncorrected error rate (MSD over length, app-logged, ratio) and a per-phrase indicator of any uncorrected error (binary), which H2 uses; ease rating 1 to 7 after each keyboard (ordinal, questionnaire). Yes to the recommended reliability and construct-validity statements.
```

Turn 4:

```text
Item 6.2 (Q1): Yes to the recommendation. Sources: the two swipe-keyboard studies I "will add from lit-search"; accept the direction as settled, with lit-search listed under Open items.
Item 6.5 (Q2): No interaction idea.
Item 7.2 (Q3): Symmetric: each keyboard is minutes of practice from the other.
Item 7.4 (Q4): No between-subjects variable.
Item 7.7 (Q5): Right-handed, 18 to 35, owns a smartphone, never used swipe; same phone, app, phrases, room, script; yes to the recommended validity trade-off wording. On the autocorrect fork, (a) or (b): I don't know.
Item 7.8 (Q6): Typing skill, mood, time of day, phrase order.
Item 7.9 (Q7): History: run all sessions within three weeks; maturation: one 40-minute session; instrumentation: freeze the app before the first participant. On the deletions-per-word call: I don't know.
```

Turn 5:

```text
Item 7.3 (Q1): Yes: a one-factor, two-level within-subjects design.
Item 7.5 (Q2): Counterbalance keyboard order, AB and BA, half each, assigned from a shuffled list; the same phrase set for both keyboards, in a fresh random order per keyboard.
Item 8.3 (Q3): The four criteria above (right-handed, 18 to 35, owns a smartphone, never used swipe), screened by a sign-up form; none selects on typing speed.
```

Turn 6:

```text
Item 2.2 (Q1): The pilot will decide the phrases per keyboard; 20 is the working value; two conditions, about 40 minutes.
Item 8.5 (Q2): 16: the two swipe-keyboard studies lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 at one session each, and 16 is a multiple of the two orders; pre-specified; the pilot refines the phrases per keyboard, not the count.
```

Turn 7:

```text
Item 2.3 (Q1): Four people from the lab; it refines the phrases per keyboard (recorded under 2.2) and the script timings; its data will not be reported.
```

Turn 8:

```text
Item 2.4 (Q1): I don't know yet.
```

Turn 9:

```text
Item 2.5 (Q1): Too few sign-ups: extend recruiting to a second course; a keyboard app failing in the pilot: freeze a fallback build.
```

Turn 10:

```text
On the running-short-of-time response for item 2.5: I don't know; item 2.5 stays as I gave it. Yes, I approve the brief. Freeze it.
```

Driver choices that go beyond copying a sheet row, so a reader can judge them: (a) no Q0: the skill defaulted the draft path itself, so no answer was needed; (b) the autocorrect fork inside round 3's Q5 (item 7.7) and the deletions-per-word call inside Q7 (item 7.9) are not on the sheet, so "I don't know", the sheet's rows for 7.7 and 7.9 sent as given; (c) the sheet's 7.5 row sent verbatim, so the skill's permuted-block assignment and disjoint-phrase scheme were not accepted; (d) 8.3: the sheet row, with the four criteria named from the 7.7 row because "above" points to an earlier message; the fifth criterion in the skill's table (types in English on a QWERTY layout) is not on the sheet and was not named; (e) 8.5: the sheet row answers parts (a) and (b) together, so the skill's 24 plus 2 extras was not accepted; (f) 2.2, 2.3, 2.4 and 2.5 got their sheet rows (2.4 "I don't know yet"), not the skill's session breakdown, three pilot participants, dated timeline or seven challenges; (g) 6.2 and 7.3 got the sheet's "Yes"; (h) turn 10's offer on 2.5 got "I don't know; item 2.5 stays as I gave it", as v2-1's did, followed by the approval and the freeze words.

## Transcript, decisive lines

- Turn 1: "No `proposal/` yet — repo exists, so freeze by commit is possible. Draft path: `proposal/draft.md` (none named)." Then the extraction table (6 weak, 15 missing, nothing settled), an open brief written, and "Brief written, checker exits 0." followed by "Frontier: item 1.1. Every other design-tree item depends on it (directly, or through items 7.1, 7.3, 6.1)." above "Q1 — item 1.1". Two permission denials, neither blocking: `cat` of the plugin's `plugin.json` ("may only concatenate files from the allowed working directories"; the session used Read instead) and the first checker call, which ended `; echo "exit=$?"` ("This Bash command contains multiple operations"; the retry without it ran).
- Turn 2: four tool calls before the questions: the Edit that wrote 1.1, the checker, then two `Agent` calls with `subagent_type` `experiment-proposal:hci-researcher`, descriptions "IV operationalization judgment" (item 7.1) and "DV operationalization judgment" (item 7.6). Round 2 opens "Frontier: items 1.2, 1.3, 6.1, 7.1, 7.6." and gives Q1 to Q5 in checklist order, each with the question, `Why this matters:` and `Recommended:` (Q4 and Q5 `Recommended (hci-researcher):`).
- Turn 3: the three Agent calls are "Control variables judgment" (7.7), "Confounds and validity threats" (7.9) and "Non-inferiority hypothesis judgment" (6.2). Q5 (item 7.7) carries a fork: "**One fork inside Q5, your call.** ... (a) **Autocorrect off in tap, swipe's decoder on** ... (b) **Autocorrect on in both**"; Q7 (item 7.9) ends "You have two ways to take it ... Which?".
- Turn 4, opening: "Round 3 recorded: items 6.2, 6.5, 7.2, 7.4, 7.8 `settled`; items 7.7 and 7.9 `provisional`, each with the recommendation standing in and listed under Open items — 7.7's autocorrect fork and 7.9's deletions-per-word call are the two you left open." The checker's one failure of the run: `proposal/design-brief.md:105: entry 7.9: Decision line is 404 characters; at most 400` (exit 1), fixed by one Edit in the same turn, the next checker call clean.
- Turn 5, round 4 Q2 (item 7.5): the hci-researcher's recommendation is a permuted-block list and "one disjoint sample drawn without replacement from the full MacKenzie–Soukoreff pool". The turn-6 entry follows the sheet's row for the order and the phrase set (see Possible plugin defects, item 2, for what it adds).
- Turn 6: "Item 2.2 recorded as `pilot settles`, item 8.5 `settled` at 16." Round 6 asks only item 2.3: "Frontier: item 2.3."
- Turn 8: "Item 2.4 is `provisional`, listed under Open items with the deadline as the missing fact." The 2.4 entry was written in this turn, the same turn as the answer.
- Turn 9: "Brief complete: all 21 design-tree items have entries, checker exits 0. Git identity resolves (`eval <eval@example.invalid>`), repo has one commit, so the freeze can commit." Then 17 `settled`, 1 `pilot settles`, 3 `provisional`, and four notes (see Diagnostics).
- Turn 10: the Bash call `git add proposal/design-brief.md && git commit -m "Freeze the design brief" -- proposal/design-brief.md` returned `[master 9c93370] Freeze the design brief` / `1 file changed, 195 insertions(+)` / `create mode 100644 proposal/design-brief.md` with `is_error` false; the result line's `permission_denials` is empty. The checker call before it (after `Status: open` became `Status: frozen 2026-10-15`) returned no output. Closing text: "Frozen and committed: `9c93370 Freeze the design brief`, checker exit 0."

## Brief status per item (final state, checklist order)

Final header, as committed:

```text
Draft: proposal/draft.md
Status: frozen 2026-10-15
Checklist: experiment-proposal 0.2.0
```

| Item | Name                               | Status        | Asked in round | Written in turn | Note                                                                                                                                                                  |
| ---- | ---------------------------------- | ------------- | -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1  | Research question                  | settled       | 1              | 2               | Sheet row, quoted                                                                                                                                                     |
| 1.2  | Ethics route                       | settled       | 2              | 3               | Sheet row, quoted                                                                                                                                                     |
| 1.3  | Data plan                          | settled       | 2              | 3               | Sheet row, quoted                                                                                                                                                     |
| 2.2  | Conditions, trials, session length | pilot settles | 5              | 6               | "The pilot will decide the phrases per keyboard; 20 is the working value; two conditions, about 40 minutes."; the Decision adds the skill's warm-up phrases and break |
| 2.3  | Pilot plan                         | settled       | 6              | 7               | Four people from the lab; phrases per keyboard and script timings; data not reported                                                                                  |
| 2.4  | Timeline                           | provisional   | 7              | 8               | "I don't know yet."; the recommendation's dates stand in; Open items 1                                                                                                |
| 2.5  | Expected challenges                | settled       | 8              | 9               | The sheet's two challenges and responses; running short of time is not covered                                                                                        |
| 6.1  | Hypotheses and research questions  | settled       | 2              | 3               | H1 directional, H2 "no worse", RQ1 on the ease rating                                                                                                                 |
| 6.2  | Hypothesis statements              | settled       | 3              | 4               | "Yes to the recommendation": H2 non-inferiority with a 5-point margin; sources "will add from lit-search" quoted; lit-search in Open items 4                          |
| 6.5  | Interaction hypotheses             | settled       | 3              | 4               | None                                                                                                                                                                  |
| 7.1  | Independent variable               | settled       | 2              | 3               | Built-in keyboard, tap mode versus swipe mode, within subjects                                                                                                        |
| 7.2  | Carry-over                         | settled       | 3              | 4               | Symmetric; the Decision adds a pre-specified order check and a first-block fallback                                                                                   |
| 7.3  | Overall design                     | settled       | 4              | 5               | One-factor, two-level within-subjects                                                                                                                                 |
| 7.4  | Random assignment                  | settled       | 3              | 4               | "No between-subjects variable."; the Decision adds the skill's seeded permuted-block list (see Possible plugin defects, item 2)                                       |
| 7.5  | Counterbalancing                   | settled       | 4              | 5               | AB and BA, shuffled list, same phrase set in fresh random order per keyboard; no disjoint subsets, no block scheme                                                    |
| 7.6  | Dependent variables                | settled       | 2              | 3               | WPM, uncorrected error rate, binary any-error indicator, ease rating                                                                                                  |
| 7.7  | Control variables                  | provisional   | 3              | 4               | Sheet row plus recommendation (a) standing in for the autocorrect fork the sheet does not answer; Open items 2                                                        |
| 7.8  | Random variables                   | settled       | 3              | 4               | Typing skill, mood, time of day, phrase order                                                                                                                         |
| 7.9  | Confounds and their prevention     | provisional   | 3              | 4               | History, maturation, instrumentation from the sheet; the hci-researcher's further threats and deletions-per-word standing in; Open items 3                            |
| 8.3  | Eligibility and screening          | settled       | 4              | 5               | Four criteria, sign-up form, none selects on typing speed                                                                                                             |
| 8.5  | Participant count                  | settled       | 5              | 6               | 16, eight per order, pre-specified; Rationale quotes the whole sheet row                                                                                              |

Totals: 17 settled, 1 pilot settles, 3 provisional, 21 entries; the entries are in checklist order.

Open items, as committed (abridged where marked; the brief carries the full text):

```text
1. Item 2.4 provisional, recommendation: the phase order in its entry, anchored to a mid-December report deadline; supply the real deadline and the dates shift as a block, since the IRB's three weeks and the three-week collection window stack to six weeks of calendar before analysis.
2. Item 7.7 provisional, recommendation: autocorrect off in the tap condition while the swipe condition keeps its word decoder, which cannot be disabled, with the suggestion strip hidden in both, and the resulting comparison of bundled interfaces stated as a scope limit on H1 and H2.
3. Item 7.9 provisional, recommendation: log deletions per word as a safeguard field alongside the settled accuracy measures, so that a speed gain bought by accepting recogniser substitutions is visible; the remaining threats and preventions are hci-researcher's list.
4. Run `/experiment-proposal:lit-search` for the source that justifies H1's direction (...), for the two within-subjects swipe-keyboard studies whose counts of 12 to 20 justify item 8.5, for the standard phrase set's citable count and mean phrase length, and for the words-per-minute and minimum-string-distance definitions.
5. Run `/experiment-proposal:the-ethics-board` to turn items 1.2, 1.3 and 2.2 into the consent story item 12.3 needs: (...)
```

Every provisional item is listed first and the two commands last, as `references/brief.md` requires.

Item 8.5 entry, as committed:

```text
### 8.5 Participant count

- Decision: 16 participants, eight per order, pre-specified. The pilot refines the phrases per keyboard, not the count.
- Rationale: "16: the two swipe-keyboard studies lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 at one session each, and 16 is a multiple of the two orders; pre-specified; the pilot refines the phrases per keyboard, not the count."
- Would change if: the literature search found the cited studies ran larger samples, or the pilot's paired standard deviation on the binary error difference showed 16 could not support H2's five-point margin, in which case item 6.2's pre-specified fallback to a plain difference hypothesis applies rather than a larger sample.
- Status: settled
- Source: user, round 5
```

## Pass bar

| Criterion                                                                                                                  | Result | Evidence                                                                                                                                                                                                                                                                                                                                                                                                |
| -------------------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Every design-tree item (21) has an entry that is settled, provisional or pilot settles; 2.4 provisional; 2.2 pilot settles | PASS   | `grep -c '^### '` on the frozen brief printed 21. The 21 heading IDs (1.1 1.2 1.3 2.2 2.3 2.4 2.5 6.1 6.2 6.5 7.1 7.2 7.3 7.4 7.5 7.6 7.7 7.8 7.9 8.3 8.5) equal the IDs of the checklist lines whose scope reads `design-tree`, compared by script. Statuses: 17 settled, 1 pilot settles (2.2), 3 provisional (2.4, 7.7, 7.9). `Status: provisional` under 2.4 and `Status: pilot settles` under 2.2. |
| 8.5 justified from the sheet (a provisional 8.5 also meets the bar)                                                        | PASS   | 8.5 is settled; its Rationale quotes the sheet row whole: the studies' 12 to 20, the course term allowing 16 at one session each, a multiple of the two orders, pre-specified, the pilot refining the phrases per keyboard and not the count. The Decision line says 16, eight per order, pre-specified. Open items 4 sends lit-search to the two studies whose counts justify it.                      |
| At least one hci-researcher subagent call across all turns                                                                 | PASS   | Six `Agent` tool_use entries with `subagent_type` `experiment-proposal:hci-researcher`: turn 2 (items 7.1 and 7.6), turn 3 (items 7.7, 7.9 and 6.2), turn 4 (item 7.5). Turns 1 and 5 to 10: none. Counted in every turn's jsonl; none of the six tool results has `is_error` true. The SKILL names 7.5, 7.7 and 7.9 for delegation; all three were delegated.                                          |
| Checker exits 0 on the frozen brief                                                                                        | PASS   | `cd "$S" && python3 "$P/scripts/check_proposal.py" brief proposal/design-brief.md`: stdout empty (0 bytes), stderr empty (0 bytes), exit code 0. The brief at that moment had `Status: frozen 2026-10-15`.                                                                                                                                                                                              |
| The freeze commit exists                                                                                                   | PASS   | `git -C "$S" log --oneline` printed `9c93370 Freeze the design brief` and `7bbd6a0 init`; `git show --stat` shows one file, `proposal/design-brief.md`, 195 insertions; `git status --porcelain` is empty.                                                                                                                                                                                              |
| Record: did the freeze's git add and git commit run or get refused                                                         | RAN    | The turn-10 Bash call returned `[master 9c93370] Freeze the design brief` with `is_error` false and `permission_denials` empty; the checker had been re-run first with no output. The commit used the scratch project's own `eval` identity, which the session confirmed in turn 9 (`git config user.name` printed `eval`, `git config user.email` printed `eval@example.invalid`).                     |

## Diagnostics

### Frontier listed above Q1

Yes, in every round that asks questions (1 to 8). The line `Frontier: ...` stands before `**Q1`, by character position in each turn's final text, and its IDs are exactly the items whose design-tree dependencies were settled, pilot settles or provisional at that moment: round 1 item 1.1; round 2 items 1.2, 1.3, 6.1, 7.1, 7.6; round 3 items 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9; round 4 items 7.3, 7.5, 8.3 (7.7 provisional counts as satisfied, so 8.3 was asked); round 5 items 2.2 and 8.5; round 6 item 2.3; round 7 item 2.4; round 8 item 2.5. Turn 9 asks no round.

### Checker each round

Yes. Turns 1 to 10 each ran the checker after the turn's brief writes (turn 1 Write, turn 2 Edit, turn 3 Write, turns 4 to 9 Edits, turn 10 the status Edit). Results: turn 1 first call refused for `; echo "exit=$?"`, retry clean; turns 2, 3, 5, 6, 7, 8 clean; turn 4 exit 1 on a 404-character 7.9 Decision, fixed, clean; turn 9 twice, clean; turn 10 clean on the frozen brief.

### Freeze

`git add && git commit` ran, not refused (see the criteria table).

### Settled items asked again

Counted in three tiers, because "a numbered question names it" would otherwise count every basis line.

Tier 1, a numbered question or an offer that proposes deciding or changing a settled item. No numbered question does. The borderline cases, quoted:

- Round 3 Q7 (item 7.9), settled 7.6: "That last point bears on your settled item 7.6, which I am not reopening. You have two ways to take it, and either is consistent with 7.6 as settled: add deletions-per-word to the logged fields ... under this item ..., or decline it ... Which?" The choice is scoped to 7.9; the 7.6 entry is unchanged in every later snapshot.
- Round 3 Q1 (item 6.2), settled 6.1 (named by H2, not by ID): "The alternative, if you want 5pp off your plate: demote H2 to 'uncorrected error rate will differ between keyboards', non-directional." Answered with the sheet's "Yes to the recommendation"; the 6.1 entry is unchanged.
- Round 4 Q3 (item 8.3), settled 1.1: "One wording point this raises, which I am not reopening since item 1.1 is settled: ... The fix lives here, not in 1.1." The 1.1 entry is unchanged and the 8.3 entry carries no redefinition of "novice".
- Unnumbered, turn 9, before the approval, three notes that touch settled entries: (1) settled 2.5: "Item 2.5 has two challenges, not three. ... Give me the response now and I record it before freezing; otherwise it is an amendment later." (the same family as v2-1's turn-10 offer); answered in turn 10 "I don't know; item 2.5 stays as I gave it", entry unchanged. (2) settled 1.1 and 8.3: "'Novice' means two different things across items 1.1 and 8.3 ... A drafting note, since item 1.1 is settled", repeated in turn 10's closing; no answer needed. (3) settled 7.4: "Item 7.4's entry carries procedure you never affirmed. You said 'No between-subjects variable'; the entry adds the seeded-RNG permuted-block list from my recommendation ... if you want the draft to read as your words, it should use your item 7.5 phrasing, 'assigned from a shuffled list'." Turn 10 answered with the blanket approval only; the entry was frozen as written.

Tier 2, basis-only mentions of a settled item in a numbered question (the permitted place for a concern; found by searching each question block for "item N.N", so a mention written otherwise is not counted): round 2 Q5 (7.6) names 1.1; round 3 Q3 (7.2) names 7.1, Q5 (7.7) names 7.1; round 4 Q1 (7.3) names 6.5, Q2 (7.5) names 7.9; round 5 Q1 (2.2) names 7.5, Q2 (8.5) names 6.2 and 7.9; round 6 Q1 (2.3) names 2.2, 6.2, 7.9, 8.3; round 7 Q1 (2.4) names 1.2, 7.9, 8.3; round 8 Q1 (2.5) names 2.2, 2.3, 6.2, 7.9. None asks the user to decide the named item again. (The tier-1 cases above also fall under this search: 7.6 in round 3 Q7, 1.1 and 7.7 in round 4 Q3.)

Tier 3, settled entries edited without a question: none. Method: the brief as it stood after turns 1 and 2 was rebuilt by replaying the Write and Edit calls in the jsonl; the brief was copied after each of turns 3 to 10; every `###` entry was compared with its text in the previous snapshot. No entry changed after the turn in which it first appeared. The only entry edited inside its first turn is 7.9 (turn 4, the checker's 404-character defect; "asymmetric-transfer test" became "transfer test"). The other changes to existing text are Open items lines, Looked up lines and the final `Status: open` to `Status: frozen 2026-10-15`.

Also not asked twice: items 7.7 and 7.9 were each put once (round 3 Q5 and Q7) and recorded provisional in the next turn; v2-1 put each twice.

## Observations beyond the bar

What ed96208 changed against the v2-1 baseline, from this run: (1) no Q0, because the draft path defaults and is said once; (2) the frontier is listed above Q1 every round and matches the dependencies; (3) the checker runs after every brief rewrite, and it caught a real defect in turn 4; (4) every answer is written to the brief in the turn it is given (v2-1: 2.4 was acknowledged in turn 9 and written in turn 10); (5) no numbered question reopens a settled item (v2-1: three); (6) items 7.7 and 7.9 are asked once (v2-1: twice). Still present: the unnumbered pre-approval offer on settled 2.5.

Possible plugin defects still visible:

1. Sub-questions inside a numbered question hold a sheet-answered item open. Round 3's Q5 (item 7.7) added an autocorrect fork and Q7 (item 7.9) a deletions-per-word call that the sheet does not answer; "I don't know" on the fork made 7.7 and 7.9 provisional with the skill's recommendation standing in as the decision (7.7: "Autocorrect unresolved: option (a) stands in"), though the sheet answered both items. Within the bar, and one question each rather than two rounds, but the cause is the same as v2-1's observation 1: nothing says what a part-complete answer does.
2. Skill wording enters entries under `Source: user`. 7.4: the Decision adds "a seeded random-number generator in permuted blocks of two, the list frozen with the app build before the first participant", and the Rationale reads `Assignment procedure: accepted recommendation: ...`, though the user's answer was "No between-subjects variable." with no yes; the skill flagged this itself in turn 9 and froze it unchanged. 2.2: the Decision adds "five unscored warm-up phrases per keyboard, both ease ratings, a break and the debrief" where the user said "20 is the working value; two conditions, about 40 minutes". 7.5: "One scored block per keyboard, so the participant count is a multiple of two". 7.2: "if transfer proves asymmetric, the first-block between-subjects contrast becomes the headline and the within-subjects estimate is labelled contaminated". 7.9: airplane mode, version strings and a timing rule beyond the user's three. `references/brief.md` has the Rationale quote the user's words and the Source read `user, round N`.
3. A settled item is still put back to the user in the closing pre-approval message (2.5's missing time-shortfall response; 7.4's wording), unnumbered, so the "never into a question" rule does not reach it.
4. The sheet's 2.5 row names two challenges while the checklist's example list includes running short of time; the skill said so before the freeze and the entry was frozen without it (a later `review` is likely to fail 2.5 on it).
5. Turn 1: the checker call with `; echo "exit=$?"` was refused by the `Bash(python3:*)` allow-list, as in v2-1; the retry succeeded.

## `git log --oneline` in the scratch project

```text
9c93370 Freeze the design brief
7bbd6a0 init
```
