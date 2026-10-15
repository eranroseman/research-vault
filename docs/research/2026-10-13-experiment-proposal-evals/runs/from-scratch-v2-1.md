# Scenario 3, from scratch, run v2-1 (0.2.0 baseline)

Date: 2026-10-15. Plugin commit: 5e13529 (plugin version 0.2.0; the brief's `Checklist:` line reads `experiment-proposal 0.2.0`). Scenario label: from-scratch. Driver: headless `claude -p` turns, answered strictly from `fixtures/from-scratch-answers.md`; "I don't know" for anything the sheet does not answer; the brief and the freeze approved when asked. Eleven turns in all: turns 1 to 4 by a first driver, which a rate limit killed during turn 4; turns 5 to 11 by this executor (see Harness event).

Verdict: PASS. Every bar criterion holds: 21 of 21 design-tree items have an entry (17 settled, 1 pilot settles, 3 provisional), 2.4 is provisional, 2.2 is pilot settles, 8.5 is settled and justified from the sheet, five hci-researcher calls, the checker exits 0 on the frozen brief, and the freeze commit `88002d3 Freeze the design brief` exists with its `git add && git commit` run (not refused). Beyond the bar, the run shows four behaviours of the baseline skill worth fixing (see Observations).

## Harness event: the 429 in turn 4 and the resumption

- Turn 4 (round 3's answers) ended with `api_error_status` 429. The final line of its jsonl: `"result":"You've hit your session limit · resets 3:40am (America/Chicago)"`, `"is_error":true`, `"terminal_reason":"api_error"`; `rc=1 secs=99` in `$S.turn4.meta`. The `rate_limit_event` before it: `"status":"rejected"`, `"rateLimitType":"five_hour"`, `"utilization":1`. The first driver was killed here.
- What turn 4 had done before the 429, read from its jsonl: an interim text ("Three things to flag, then the entries and round 4"), one Write of `proposal/design-brief.md` (entries 6.2, 6.5, 7.2, 7.4, 7.8 added to the six from earlier rounds), and one checker run with no output. Only the closing message, the round-4 questions, was lost. Items 7.7 and 7.9 were not written, because the interim text left them open (see Observations).
- Inspection before resuming (read-only): `proposal/design-brief.md` held 11 entries, `Status: open`; `git -C "$S" log --oneline` showed only `97236fb init`; `git status --porcelain` showed `?? proposal/`.
- Resumption: `cp $S.turn4.prompt $S.turn5.prompt`, then `bash /tmp/ep-eval/review-v2-drive.sh /tmp/ep-eval/from-scratch-v2-1 5` (one attempt, no retry loop, as the task required). The turn-5 jsonl carries `SessionStart:resume` and the same `session_id` as turn 4 (`0c0c29be-77f6-4b0b-908a-bade18a1c773`), so `--continue` resumed the right session. Its `rate_limit_event` read `"status":"allowed"`, `"utilization":0.01`, a fresh five-hour window (`resetsAt` 2026-10-15T12:00Z, where the rejected event had 08:40Z, the 3:40am of the 429 message); the turn ran at 07:03Z (02:03 CDT), before that stated reset. `api_error_status` was null on turns 5 to 11; no later turn was rate limited.
- Turn 5 made no tool call and opened with "Checker clean; those five entries are recorded (6.2, 6.5, 7.2, 7.4, 7.8 settled)", then asked round 4. The re-sent answers were not re-recorded.
- Plugin integrity: `git diff --stat 5e13529 HEAD -- plugins/experiment-proposal` printed nothing and `git status --porcelain plugins/` printed nothing, so the plugin files loaded by `--plugin-dir "$P"` are those of 5e13529 (HEAD is two plan commits past it).

## Commands

`$P` is `<checkout>/plugins/experiment-proposal`; `$S` is `/tmp/ep-eval/from-scratch-v2-1`, created with `git init -q`, `git config user.email eval@example.invalid`, `git config user.name eval`, one empty-tree commit `init` (no fixtures: the scenario gives only the idea). The helper `/tmp/ep-eval/review-v2-drive.sh "$S" <turn>` runs, with `prompt` read from `$S.turn<N>.prompt`:

Turn 1:

```text
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null
```

Turns 2 to 11 (the same, with `--continue` before the model flag):

```text
cd "$S" && timeout 1800 claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn$t.jsonl" 2> "$S.turn$t.err" < /dev/null
```

After the run, the checker from the scratch project, stdout, stderr and exit code captured separately:

```text
cd "$S" && python3 "$P/scripts/check_proposal.py" brief proposal/design-brief.md > chk.out 2> chk.err; echo "exit=$?"
```

## Turns

| Turn | Sent                                                                                                                  | Came back                                                                                                                                                                                             | Wall time |
| ---- | --------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 1    | `/experiment-proposal:design` with the idea                                                                           | Extraction table (all 21 items weak or missing, nothing settled); open brief written (header, Looked up); checker clean; Q0 draft path, round 1 = Q1 item 1.1                                         | 95 s      |
| 2    | Q0 "I don't know"; Q1 item 1.1 from the sheet                                                                         | 1.1 settled; two hci-researcher calls (6.1, 7.6); round 2 = Q1 to Q5: items 1.2, 1.3, 6.1, 7.1, 7.6                                                                                                   | 120 s     |
| 3    | Items 1.2, 1.3, 6.1, 7.1, 7.6 from the sheet                                                                          | Those five settled; three hci-researcher calls (7.2, 7.7, 7.9); checker clean; round 3 = Q1 to Q7: items 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9                                                            | 256 s     |
| 4    | Items 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9 from the sheet                                                                | 429 session limit (rc=1). Before it: brief written with 6.2, 6.5, 7.2, 7.4, 7.8 settled, checker clean; closing message lost                                                                          | 99 s      |
| 5    | Turn 4's prompt re-sent unchanged (harness event)                                                                     | No tool call; "those five entries are recorded"; round 4 = Q1 item 7.3, Q2 item 7.5, Q3 item 7.7 (grip), Q4 item 7.9 (four confounds)                                                                 | 40 s      |
| 6    | 7.3 yes; 7.5 sheet row; 7.7 sheet row, grip "I don't know"; 7.9 sheet row, four further confounds "I don't know"      | 7.3, 7.5 settled; 7.7, 7.9 provisional; the checker caught a 412-character 7.9 Decision (exit 1), session shortened it, checker clean; round 5 = Q1 item 2.2, Q2 item 8.3, Q3 item 8.5                | 113 s     |
| 7    | 2.2 sheet row; 8.3 sheet row plus "Item 1.1 stays as I gave it"; 8.5 sheet row                                        | 2.2 pilot settles; 8.3, 8.5 settled; checker clean; round 6 = Q1 item 2.3                                                                                                                             | 70 s      |
| 8    | 2.3 sheet row plus "Item 1.3 stays as I gave it: no recordings"                                                       | 2.3 settled; checker clean; round 7 = Q1 item 2.4                                                                                                                                                     | 40 s      |
| 9    | 2.4 "I don't know yet"                                                                                                | No tool call and no brief change; "Item 2.4 goes in provisional"; round 8 = Q1 item 2.5                                                                                                               | 25 s      |
| 10   | 2.5 sheet row                                                                                                         | 2.4 provisional and 2.5 settled written; Open items rebuilt; checker clean; 21 of 21 entries; asks for approval and the freeze, with one unnumbered standing offer on item 2.5                        | 132 s     |
| 11   | "On the standing offer for item 2.5: I don't know; item 2.5 stays as I gave it. Yes, I approve the brief. Freeze it." | `Status: frozen 2026-10-15`, checker clean, `git add proposal/design-brief.md && git commit -m "Freeze the design brief" -- proposal/design-brief.md` ran: `[master 88002d3] Freeze the design brief` | 17 s      |

Turn texts, verbatim (the files `$S.turn<N>.prompt`):

Turn 1:

```text
/experiment-proposal:design Novice smartphone users entering text: does a swipe keyboard beat tap typing? Within subjects, two keyboards, phrases from a standard set, speed and errors logged, plus a 1 to 7 ease rating after each keyboard.
```

Turn 2:

```text
Q0 (draft path): I don't know.
Q1 (item 1.1): "Does entering phrases with a swipe keyboard, compared with a tap keyboard, change words per minute for novice smartphone users?" Levels: tap, swipe.
```

Turn 3:

```text
Item 1.2 (Q1): The university IRB; minimal-risk expedited review, about three weeks; a consent form and the phrase set are required.
Item 1.3 (Q2): Keystroke logs and phrase times only, no names linked, no recordings; the two experimenters have access; raw data kept five years, then deleted.
Item 6.1 (Q3): H1 directional (swipe faster); H2 "no worse" on errors; RQ1 on the ease rating (unsure of direction).
Item 7.1 (Q4): Keyboard: the phone's built-in tap keyboard versus its swipe mode; within subjects because typing skill varies hugely between people.
Item 7.6 (Q5): Words per minute (characters over five over minutes, app-logged, ratio); uncorrected error rate (MSD over length, app-logged, ratio) and a per-phrase indicator of any uncorrected error (binary), which H2 uses; ease rating 1 to 7 after each keyboard (ordinal, questionnaire). Yes to the recommended reliability and construct-validity statements.
```

Turns 4 and 5 (identical):

```text
Item 6.2 (Q1): Yes to the recommendation. Sources: the two swipe-keyboard studies I "will add from lit-search"; accept the direction as settled, with lit-search listed under Open items.
Item 6.5 (Q2): No interaction idea.
Item 7.2 (Q3): Symmetric: each keyboard is minutes of practice from the other.
Item 7.4 (Q4): No between-subjects variable.
Item 7.7 (Q5): Right-handed, 18 to 35, owns a smartphone, never used swipe; same phone, app, phrases, room, script; yes to the recommended validity trade-off wording.
Item 7.8 (Q6): Typing skill, mood, time of day, phrase order.
Item 7.9 (Q7): History: run all sessions within three weeks; maturation: one 40-minute session; instrumentation: freeze the app before the first participant.
```

Turn 6:

```text
Item 7.3 (Q1): Yes: a one-factor, two-level within-subjects design.
Item 7.5 (Q2): Counterbalance keyboard order, AB and BA, half each, assigned from a shuffled list; the same phrase set for both keyboards, in a fresh random order per keyboard.
Item 7.7 (Q3): Right-handed, 18 to 35, owns a smartphone, never used swipe; same phone, app, phrases, room, script; yes to the recommended validity trade-off wording. On grip: I don't know.
Item 7.9 (Q4): History: run all sessions within three weeks; maturation: one 40-minute session; instrumentation: freeze the app before the first participant. For the four further confounds you list: I don't know.
```

Turn 7:

```text
Item 2.2 (Q1): The pilot will decide the phrases per keyboard; 20 is the working value; two conditions, about 40 minutes.
Item 8.3 (Q2): The four criteria (right-handed, 18 to 35, owns a smartphone, never used swipe), screened by a sign-up form; none selects on typing speed. Item 1.1 stays as I gave it.
Item 8.5 (Q3): 16: the two swipe-keyboard studies lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 at one session each, and 16 is a multiple of the two orders; pre-specified; the pilot refines the phrases per keyboard, not the count.
```

Turn 8:

```text
Item 2.3 (Q1): Four people from the lab; it refines the phrases per keyboard (recorded under 2.2) and the script timings; its data will not be reported. Item 1.3 stays as I gave it: no recordings.
```

Turn 9:

```text
Item 2.4 (Q1): I don't know yet.
```

Turn 10:

```text
Item 2.5 (Q1): Too few sign-ups: extend recruiting to a second course; a keyboard app failing in the pilot: freeze a fallback build.
```

Turn 11:

```text
On the standing offer for item 2.5: I don't know; item 2.5 stays as I gave it. Yes, I approve the brief. Freeze it.
```

Driver choices that go beyond copying a sheet row, so a reader can judge them: (a) Q0, the draft path, is not on the sheet, so "I don't know" (the default `proposal/draft.md` stood); (b) the sheet's 7.5 row answers the skill's "4 orders or 2" (AB and BA, so 2) and contradicts its disjoint-subsets proposal, so the row was sent verbatim and the ABBA blocks, warm-up and subsets were not accepted; (c) grip (round 4 Q3) and the four extra confounds (Q4) are not on the sheet, so "I don't know"; (d) where a skill question proposed amending a settled item (1.1 in round 5, 1.3 in round 6), the answer was "stays as I gave it", the sheet's own answer for that item, not "I don't know"; (e) the turn-10 yes-or-no offer on 2.5 got "I don't know; item 2.5 stays as I gave it".

## Transcript, decisive lines

- Turn 1: "No material in the repo — empty git repo, no `proposal/`. ... Nothing settled: material states decisions but no reasons." Its first checker call ended `; echo "exit=$?"` and was refused by the `Bash(python3:*)` allow-list ("This Bash command contains multiple operations"); the session retried without it.
- Turn 2: two `Agent` calls, `subagent_type` `experiment-proposal:hci-researcher`, descriptions "Direction of effect, item 6.1" and "Dependent variables, item 7.6". Turn 3: three more, "Carry-over symmetry, item 7.2", "Control variables, item 7.7", "Confounds and threats, item 7.9". No result was an error. Five in all; turns 1 and 4 to 11 made none.
- Turn 4 (interim text, before the 429): "**Grip is still open.** ... Item 7.7 stays weak until you pick." and "**Item 7.9 has three of seven.** ... Nothing depends on 7.9, so it costs nothing to finish it in round 4."
- Turn 5, round 4 Q2: "Recommended, two parts. Order: two sequences ... Block scheme (hci-researcher ...): alternate short blocks ... A-B-B-A for tap-first ... the 500-phrase set partitioned into 'two disjoint random subsets'". The turn-6 entry for 7.5 followed the sheet instead: "Two orders, tap-first and swipe-first, half the participants each, assigned from a shuffled list prepared before recruitment; the same phrase set is used for both keyboards, in a fresh random order per keyboard. The sample is therefore a multiple of 2 (item 8.8)."
- Turn 6: "Checker clean, with items 7.7 and 7.9 recorded `provisional` and listed under Open items." The checker's one failure in the run: `proposal/design-brief.md:121: entry 7.9: Decision line is 412 characters; at most 400` (exit 1), fixed in the same turn.
- Turn 7, round 5 Q2 (item 8.3): "First, a mismatch to settle: item 1.1 says 'novice smartphone users', but your criteria ... select *experienced tappers who have never swiped* ... Recommended: keep the criteria and amend item 1.1's wording to 'smartphone users who have never used swipe typing'". Q3 (item 8.5) asked for the similar experiments and the reason; the sheet's row supplied both and the entry quotes it whole.
- Turn 8, round 6 Q1 (item 2.3): "One conflict to settle inside this question: the log verification wants a screen recording, and item 1.3 says 'no recordings'. ... choosing (i) amends item 1.3 to carve out the pilot recording."
- Turn 9: "Item 2.4 goes in `provisional` with those dates standing in and listed under Open items." (no tool call that turn; the 2.4 entry was written in turn 10).
- Turn 10: "The brief is complete: 21 of 21 design-tree items, checker exits 0 ... One standing offer, yes or no: add the time-shortfall response to item 2.5 ... Approve the brief and freeze it? On your yes I set `Status: frozen 2026-10-15`, re-run the checker, and commit `Freeze the design brief`."
- Turn 11: the Bash tool call `git add proposal/design-brief.md && git commit -m "Freeze the design brief" -- proposal/design-brief.md` returned `[master 88002d3] Freeze the design brief` / `1 file changed, 195 insertions(+)` / `create mode 100644 proposal/design-brief.md` with `is_error` false; the result line shows `permission_denials` empty. Closing text: "Frozen and committed: `88002d3 Freeze the design brief`, checker clean at exit 0, `Status: frozen 2026-10-15`, 21 of 21 design-tree items".

## Brief status per item (final state, checklist order)

Final header, as committed:

```text
Draft: proposal/draft.md
Status: frozen 2026-10-15
Checklist: experiment-proposal 0.2.0
```

| Item | Name                                            | Status        | Round | Note                                                                                                                                                                               |
| ---- | ----------------------------------------------- | ------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1  | Research question                               | settled       | 1     | Sheet row, quoted                                                                                                                                                                  |
| 1.2  | Ethics route                                    | settled       | 2     | Sheet row, quoted                                                                                                                                                                  |
| 1.3  | Data plan                                       | settled       | 2     | Sheet row, quoted; named again in round 6 Q1                                                                                                                                       |
| 2.2  | Conditions, trials and session estimate         | pilot settles | 5     | "The pilot will decide the phrases per keyboard; 20 is the working value; two conditions, about 40 minutes." Decision adds "plus 5 unscored warm-up" (the skill's, not the user's) |
| 2.3  | Pilot plan                                      | settled       | 6     | Four people from the lab; refines phrases per keyboard and script timings; data not reported                                                                                       |
| 2.4  | Timeline                                        | provisional   | 7     | "I don't know yet"; dates stand in; Open items 1; written in turn 10, one turn after the answer                                                                                    |
| 2.5  | Expected challenges                             | settled       | 8     | Two challenges, two responses, the sheet's                                                                                                                                         |
| 6.1  | Hypotheses and research question                | settled       | 2     | H1 directional, H2 "no worse", RQ1                                                                                                                                                 |
| 6.2  | Hypothesis variables, direction and testability | settled       | 3     | "Yes to the recommendation": H2 non-inferiority with a 5-point margin; sources "will add from lit-search" quoted; lit-search in Open items 4                                       |
| 6.5  | Interaction hypotheses                          | settled       | 3     | None                                                                                                                                                                               |
| 7.1  | Independent variable                            | settled       | 2     | Built-in keyboard in tap mode versus swipe mode, within subjects                                                                                                                   |
| 7.2  | Carry-over                                      | settled       | 3     | Symmetric; the skill flagged the reason as contradicted by the hci-researcher, the entry unchanged                                                                                 |
| 7.3  | Overall design                                  | settled       | 4     | One-factor, two-level within-subjects                                                                                                                                              |
| 7.4  | Random assignment                               | settled       | 3     | No between-subjects variable                                                                                                                                                       |
| 7.5  | Counterbalancing                                | settled       | 4     | AB and BA, shuffled list, same phrase set in fresh random order per keyboard; no disjoint subsets, no ABBA                                                                         |
| 7.6  | Dependent variables                             | settled       | 2     | WPM, uncorrected error rate and binary indicator, ease rating                                                                                                                      |
| 7.7  | Control variables                               | provisional   | 4     | Sheet row plus the recommended grip standardization standing in; Open items 2; asked in rounds 3 and 4                                                                             |
| 7.8  | Random variables                                | settled       | 3     | Typing skill, mood, time of day, phrase order                                                                                                                                      |
| 7.9  | Confounds                                       | provisional   | 4     | History, maturation, instrumentation freeze from the sheet; four further threats standing in from the recommendation; Open items 3; asked in rounds 3 and 4                        |
| 8.3  | Eligibility and screening                       | settled       | 5     | Four criteria, sign-up form, none selects on typing speed                                                                                                                          |
| 8.5  | Participant count                               | settled       | 5     | 16, 8 per order, pre-specified; Rationale quotes the whole sheet row                                                                                                               |

Totals: 17 settled, 1 pilot settles, 3 provisional, 21 entries. The entries are in checklist order (the 0.1.0 baseline brief was in the order the rounds settled them).

Open items, as committed:

```text
1. Item 2.4 provisional, recommendation: the dates above, anchored on an IRB submission by 2026-10-22 and approval about 2026-11-12, with the app and script built during the review window; confirm the course's final deadline and snap the phases to it, compressing the collection window before touching item 8.5's count
2. Item 7.7 provisional, recommendation: standardize one dominant thumb for both modes, checked at each block start, paying mildly unnatural tap for an independent variable that is the gesture alone, with that external-validity cost stated; the alternative is free grip with item 7.1 amended to "the gesture and the grip it induces"
3. Item 7.9 provisional, recommendation: add to history, maturation and the app freeze the four threats specific to this design — the MSD asymmetry against H2 (binary indicator primary, word-level error rate added, which would amend item 7.6, bias direction stated), the gesture timing artefact (...), novelty and demand on the ease item (...), and experimenter expectancy (verbatim script, automated scoring, experimenter blind or absent during blocks)
4. Run `/experiment-proposal:lit-search` for swipe versus tap text-entry speed in novice or non-expert users, to find the two sources H1's direction needs (item 6.2) or to show that the direction must be amended, and to confirm the 12-to-20 participant counts item 8.5's justification rests on
5. Run `/experiment-proposal:the-ethics-board` for the consent story: items 1.2 (university IRB, expedited, about three weeks), 1.3 (keystroke logs and phrase times only, no names linked, no recordings, two experimenters, five years) and the 40-minute session estimate from item 2.2
```

(Item 3 is abridged here with `(...)`; the brief carries the full text. Every provisional item is listed first and the two commands last, as `references/brief.md` requires.)

Item 8.5 entry, as committed:

```text
### 8.5 Participant count
- Decision: 16 participants, 8 per order, pre-specified; the pilot refines the phrases per keyboard, not the count.
- Rationale: "16: the two swipe-keyboard studies lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 at one session each, and 16 is a multiple of the two orders; pre-specified; the pilot refines the phrases per keyboard, not the count."
- Would change if: lit-search found the comparable studies used materially more than 20 participants, which would leave 16 hard to defend.
- Status: settled
- Source: user, round 5
```

## Pass bar

| Criterion                                                                                                                  | Result             | Evidence                                                                                                                                                                                                                                                                                                                                                                                          |
| -------------------------------------------------------------------------------------------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Every design-tree item (21) has an entry that is settled, provisional or pilot settles; 2.4 provisional; 2.2 pilot settles | PASS               | `grep -c '^### '` on the brief printed 21; the 21 headings are exactly the checklist's design-tree items; 17 settled, 1 pilot settles (2.2), 3 provisional (2.4, 7.7, 7.9). The two named statuses hold: `Status: provisional` under 2.4 and `Status: pilot settles` under 2.2. Two extra provisional items (7.7, 7.9) are within the bar.                                                        |
| 8.5 justified from the sheet (a provisional 8.5 also meets the bar)                                                        | PASS               | 8.5 is settled; its Rationale quotes the sheet row whole: the studies' 12 to 20, the course term allowing 16 at one session each, a multiple of the two orders, pre-specified, the pilot refining the phrases per keyboard and not the count. The Decision line says 16, 8 per order, pre-specified. Open items 4 sends lit-search to confirm the 12-to-20 counts.                                |
| At least one hci-researcher subagent call across all turns                                                                 | PASS               | 5 `Agent` tool_use entries with `subagent_type` `experiment-proposal:hci-researcher` (turn 2: items 6.1 and 7.6; turn 3: items 7.2, 7.7 and 7.9); turns 1, 4 to 11: 0. Counted in every turn's jsonl; none of the five tool results was an error.                                                                                                                                                 |
| Checker exits 0 on the frozen brief                                                                                        | PASS               | `cd "$S" && python3 "$P/scripts/check_proposal.py" brief proposal/design-brief.md`: stdout empty (0 bytes), stderr empty (0 bytes), exit code 0. The brief at that moment had `Status: frozen 2026-10-15`.                                                                                                                                                                                        |
| The freeze commit exists                                                                                                   | PASS               | `git -C "$S" log --oneline` printed `88002d3 Freeze the design brief` and `97236fb init`; `git show --stat` shows one file, `proposal/design-brief.md`, 195 insertions; `git status --porcelain` is empty.                                                                                                                                                                                        |
| Record: did the freeze's git add and git commit run or get refused                                                         | RAN                | The turn-11 Bash call returned `[master 88002d3] Freeze the design brief` with `is_error` false and `permission_denials` empty; the checker had been re-run with exit 0 first (a Bash call with no output, turn 11). The commit used the scratch project's own `eval <eval@example.invalid>` identity, which the session confirmed in turn 10 with `git config user.name; git config user.email`. |
| Record: settled items asked again                                                                                          | 3 asked, 0 changed | See the next section.                                                                                                                                                                                                                                                                                                                                                                             |

## Settled items asked again

An item counts when a numbered question named it, or its entry changed after it was settled. No settled entry changed text after it was written: the final brief's settled entries were compared with the brief as it stood after each of turns 2 to 4 (rebuilt by replaying the Write and Edit calls in the jsonl) and after each of turns 5 to 11 (snapshots of the file); the only changes to existing text were in the Open items lines of the provisional items 7.7, 7.9 and 2.4 and one added Looked up line, and the final `Status: open` to `Status: frozen 2026-10-15`.

- Item 1.1 (settled in round 1): named in round 5's Q2 (the question is item 8.3): "First, a mismatch to settle: item 1.1 says 'novice smartphone users' ... amend item 1.1's wording". Answered in turn 7 "Item 1.1 stays as I gave it". The 1.1 entry is unchanged.
- Item 1.3 (settled in round 2): named in round 6's Q1 (the question is item 2.3): "the log verification wants a screen recording, and item 1.3 says 'no recordings' ... choosing (i) amends item 1.3". Answered in turn 8 "Item 1.3 stays as I gave it: no recordings". The 1.3 entry is unchanged; the 2.3 entry records the replay check instead of a recording.
- Item 2.5 (settled in round 8): named by an unnumbered yes-or-no offer in turn 10, "add the time-shortfall response to item 2.5 ... before freezing". Answered in turn 11 "I don't know; item 2.5 stays as I gave it". The 2.5 entry is unchanged.
- Flagged, not asked: item 7.2 (settled in round 3) was marked in turn 4's interim text as resting on a premise "the literature contradicts"; no question was put and the entry is unchanged.
- Never written settled, asked twice: items 7.7 and 7.9 were each put in round 3 (Q5, Q7) and again in round 4 (Q3, Q4), and ended provisional.

## Observations beyond the bar (possible plugin defects)

1. Partial answers hold an item open. The sheet answered 7.7 and 7.9 in round 3 (turn 4's prompt), but the skill kept both weak ("Item 7.7 stays weak until you pick") and in round 4 asked a grip question and a four-confound question the sheet cannot answer. With "I don't know" they ended `provisional`, 7.7 and 7.9 both listing recommendations the user never accepted as the decision. `SKILL.md` step 2 defines `weak` as "a decision without a reason, a reason that does not fit this experiment, or a conflict with another item" and step 3 as "'I don't know' makes the item `provisional` with the recommendation standing in"; neither says what to do with an answer that is part-complete.
2. Settled entries are put back to the user. Round 5's Q2 offered to amend 1.1, round 6's Q1 offered to amend 1.3, and turn 10 offered to add a response to 2.5. `SKILL.md` step 3 says "The frontier is every weak or missing item", and only step 1 (resume) says "every entry keeps its status"; no line says a settled item is not asked again before the freeze, and step 7 allows no later edit ("A frozen entry is never edited").
3. Skill wording enters an entry under the user's name. The 2.2 Decision reads "working value 20 scored plus 5 unscored warm-up" with `Source: user, round 5`; the user's words were "20 is the working value" and the warm-up is the hci-researcher's. `references/brief.md` says the Rationale "quotes the user's words" and the Source is `user, round N`. (7.5 did not have this problem: the entry follows the sheet and drops the disjoint subsets.)
4. The brief lags the answers by a turn. `SKILL.md` step 3: "Rewrite the brief after every round." Turn 9 answered 2.4 and replied "Item 2.4 goes in `provisional`" with no tool call and no change to the file; the entry was written in turn 10. A session that died there would lose the answer, as turn 4's closing message was lost.
5. Minor: turn 1's first checker call appended `; echo "exit=$?"` and was refused by the allow-list `Bash(python3:*)`; the retry succeeded. The checker caught a real defect in turn 6 (a 412-character Decision), the one check failure of the run.

## `git log --oneline` in the scratch project

```text
88002d3 Freeze the design brief
97236fb init
```
