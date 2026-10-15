# Scenario 3, from scratch, run v2-4 (0.2.0, fixed design skill)

Date: 2026-10-15. Plugin commit: 76e9c28 (plugin version 0.2.0; the brief's `Checklist:` line reads `experiment-proposal 0.2.0`). The fix commit that matters for this scenario is ed96208, the design fix: `design` keeps settled items settled, lists the frontier above Q1, runs the checker each round and defaults the draft path (76e9c28 is the review and fixture fix on top of it). Scenario label: from-scratch. Driver: headless `claude -p` turns, answered strictly from `fixtures/from-scratch-answers.md`; "I don't know" for anything the sheet does not answer (nothing needed it except item 2.4); the brief and the freeze approved when asked. Ten turns in all, one driver, no interruption.

Verdict: PASS. Every bar criterion holds: 21 of 21 design-tree items have an entry (19 settled, 1 pilot settles, 1 provisional), 2.4 is provisional, 2.2 is pilot settles, 8.5 is settled and justified from the sheet, eight hci-researcher calls, the checker exits 0 on the frozen brief (stdout and stderr empty), and the freeze commit `cad4cfc Freeze the design brief` exists, its `git add && git commit` run and not refused. Diagnostics: no settled item was asked again and no settled entry was edited after the user saw it; the frontier's IDs were listed above Q1 in all eight rounds; the checker ran in nine of the ten turns (not in turn 2); one unnumbered offer to reopen item 2.3 stands in the closing message (see Diagnostics).

## Harness

- No rate limit: every turn's final JSON has `is_error` false, `api_error_status` null, `subtype` success, `terminal_reason` completed, and every `rate_limit_event` reads `allowed`; no jsonl contains "session limit". `$S.turn<N>.err` is empty for all ten turns; `rc=0` in every `$S.turn<N>.meta`.
- Scratch project: `$S` is `/tmp/ep-eval/from-scratch-v2-4`, fresh (the directory did not exist before), `git init -q`, `git config user.email eval@example.invalid`, `git config user.name eval`, `git commit --allow-empty -qm init` (`7ab551e`), no fixtures and no `proposal/` directory (the scenario gives only the idea). `$P` is `<checkout>/plugins/experiment-proposal`.
- Prompts are the files `$S.turn<N>.prompt`; the helper `/tmp/ep-eval/review-v2-drive.sh "$S" <turn>` ran them with the harness flags, `--continue` from turn 2.

## Commands

Turn 1, as the helper runs it:

```text
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null
```

Turns 2 to 10 (the same with `--continue` before the model flag):

```text
cd "$S" && timeout 1800 claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn$t.jsonl" 2> "$S.turn$t.err" < /dev/null
```

After the run, the checker from the scratch project, stdout, stderr and exit code captured separately:

```text
cd "$S" && python3 "$P/scripts/check_proposal.py" brief proposal/design-brief.md > chk.out 2> chk.err; echo "exit=$?"
```

## Turns

| Turn | Sent                                                                                          | Came back                                                                                                                                                                                                                                                                                                              | Wall time |
| ---- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 1    | `/experiment-proposal:design` with the idea                                                   | Extraction table (21 items: 7 weak, 14 missing, none settled); draft path defaulted to `proposal/draft.md` and said so, no question about it; open brief written (header, two Looked up lines, one Open item); checker run (first call refused by the allow-list, second clean); "Frontier: item 1.1." and Q1 item 1.1 | 78 s      |
| 2    | Q1 item 1.1 from the sheet                                                                    | 1.1 settled; two hci-researcher calls (7.1, 7.6); no checker run; round 2 = Q1 to Q5: items 1.2, 1.3, 6.1, 7.1, 7.6, frontier line above Q1                                                                                                                                                                            | 106 s     |
| 3    | Items 1.2, 1.3, 6.1, 7.1, 7.6 from the sheet                                                  | Those five settled; three hci-researcher calls (7.2, 7.7, 7.9); checker failed once (7.6 Decision 411 characters), fixed, clean; round 3 = Q1 to Q7: items 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9                                                                                                                           | 282 s     |
| 4    | Items 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9 from the sheet                                        | All seven settled in this one pass (7.7 and 7.9 included); one hci-researcher call (7.5); checker failed once (entries not in checklist order), fixed, clean; round 4 = Q1 to Q3: items 7.3, 7.5, 8.3                                                                                                                  | 211 s     |
| 5    | Items 7.3, 7.5, 8.3 from the sheet                                                            | Those three settled; two hci-researcher calls (2.2, 8.5); checker failed once (entries not in checklist order), fixed, clean; round 5 = Q1 to Q2: items 2.2, 8.5                                                                                                                                                       | 197 s     |
| 6    | Items 2.2, 8.5 from the sheet                                                                 | 2.2 pilot settles, 8.5 settled; checker clean; round 6 = Q1 item 2.3                                                                                                                                                                                                                                                   | 50 s      |
| 7    | Item 2.3 from the sheet                                                                       | 2.3 settled; checker clean; round 7 = Q1 item 2.4                                                                                                                                                                                                                                                                      | 30 s      |
| 8    | Item 2.4 "I don't know yet."                                                                  | 2.4 provisional written in the same turn, Open items rebuilt (2.4 first); checker clean; round 8 = Q1 item 2.5                                                                                                                                                                                                         | 40 s      |
| 9    | Item 2.5 from the sheet                                                                       | 2.5 settled; checker clean; entry count 21; frontier empty; tally 19 settled, 1 pilot settles, 1 provisional; asks for approval and the freeze, with one unnumbered offer to reopen item 2.3                                                                                                                           | 119 s     |
| 10   | "On the offer about item 2.3: it stays as I gave it ... Yes, I approve the brief. Freeze it." | `Status: frozen 2026-10-15`, checker clean, `git add proposal/design-brief.md && git commit -m "Freeze the design brief" -- proposal/design-brief.md` ran: `[master cad4cfc] Freeze the design brief`                                                                                                                  | 23 s      |

Total wall time 1136 s. Turn texts, verbatim (the files `$S.turn<N>.prompt`):

Turn 1:

```text
/experiment-proposal:design Novice smartphone users entering text: does a swipe keyboard beat tap typing? Within subjects, two keyboards, phrases from a standard set, speed and errors logged, plus a 1 to 7 ease rating after each keyboard.
```

Turn 2:

```text
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

Turn 4:

```text
Item 6.2 (Q1): Yes to the recommendation. Sources: the two swipe-keyboard studies I "will add from lit-search"; accept the direction as settled, with lit-search listed under Open items.
Item 6.5 (Q2): No interaction idea.
Item 7.2 (Q3): Symmetric: each keyboard is minutes of practice from the other.
Item 7.4 (Q4): No between-subjects variable.
Item 7.7 (Q5): Right-handed, 18 to 35, owns a smartphone, never used swipe; same phone, app, phrases, room, script; yes to the recommended validity trade-off wording.
Item 7.8 (Q6): Typing skill, mood, time of day, phrase order.
Item 7.9 (Q7): History: run all sessions within three weeks; maturation: one 40-minute session; instrumentation: freeze the app before the first participant.
```

Turn 5:

```text
Item 7.3 (Q1): Yes: a one-factor, two-level within-subjects design.
Item 7.5 (Q2): Counterbalance keyboard order, AB and BA, half each, assigned from a shuffled list; the same phrase set for both keyboards, in a fresh random order per keyboard.
Item 8.3 (Q3): The four criteria (right-handed, 18 to 35, owns a smartphone, never used swipe), screened by a sign-up form; none selects on typing speed.
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
On the offer about item 2.3: it stays as I gave it, four people from the lab. Yes, I approve the brief. Freeze it.
```

Two answers went beyond a bare sheet row. The turn-4 answer to item 6.2 ("Yes to the recommendation") accepted the non-inferiority margins the skill proposed for H2 (2 points on the uncorrected error rate, 5 points on the share of phrases with an uncorrected error), because the sheet says "Yes to the recommendation" there. In turn 10 the reply to the unnumbered offer on item 2.3 restates the sheet's 2.3 row ("four people from the lab") and does not use "I don't know", because the sheet answers 2.3.

## Transcript, decisive lines

- Turn 1: "Repo exists. No material in project — only task text from command args. Draft path: `proposal/draft.md` (default, none named)." The extraction table marked all 21 design-tree items weak or missing; its closing line: "Nothing settled, so the brief starts with no entries." Then: "Checker exits 0. Brief written at `proposal/design-brief.md`, status open." / "## Round 1" / "Frontier: item 1.1." / "**Q1. Item 1.1 — the research question.**"
- Round headers, each directly above Q1: "Frontier: items 1.2, 1.3, 6.1, 7.1, 7.6." (turn 2); "Frontier: items 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9." (turn 3); "Frontier: items 7.3, 7.5, 8.3." (turn 4); "Frontier: items 2.2, 8.5." (turn 5); "Frontier: item 2.3." (turn 6); "Frontier: item 2.4." (turn 7); "Frontier: item 2.5 — the last design-tree item." (turn 8).
- Turn 4, the pass that settled the two items the baseline run held open: items 7.7 and 7.9 were written `settled` from the sheet rows, with no follow-up question on grip or on further confounds (both appear in the recommendations the skill showed in turn 3, and neither was asked again).
- Turn 8: "Checker exits 0. Item 2.4 recorded provisional and listed under Open items." (the 2.4 entry and the Open items were written in the same turn as the answer.)
- Turn 9: "The frontier is empty. `proposal/design-brief.md` holds all 21 design-tree items, and the checker exits 0." / "**Status tally:** 19 settled, 1 `pilot settles` (item 2.2, phrases per keyboard, working value 20), 1 `provisional` (item 2.4, the timeline, waiting on the course deadline)." / the unnumbered offer: "Both entries stand as you decided them; if you want the pilot run with screened novices instead, say so now and I will record 2.3 that way rather than amend it later." / "Approve the freeze? On your yes I set `Status: frozen 2026-10-15`, re-run the checker, and commit the brief."
- Turn 10: the Bash call `git add proposal/design-brief.md && git commit -m "Freeze the design brief" -- proposal/design-brief.md` returned, with `is_error` false: "[master cad4cfc] Freeze the design brief" / "1 file changed, 176 insertions(+)" / "create mode 100644 proposal/design-brief.md". Final text: "Frozen and committed: `cad4cfc` "Freeze the design brief". Checker exits 0 on the frozen brief ..."

## Brief status per item (final state, checklist order)

Final header, as committed:

```text
Draft: proposal/draft.md
Status: frozen 2026-10-15
Checklist: experiment-proposal 0.2.0
```

"Asked in" is the round whose questions carried the item (round N is the closing text of turn N, answered in turn N+1; the entry's Source line reads `user, round N`). "Rationale" says whether the entry quotes the user's words or reads `accepted recommendation`. "Looked up by" names the hci-researcher call made for the item (its answer was quoted as the recommendation's basis).

| Item | Entry title                                     | Status        | Asked in | Rationale                                                                         | hci-researcher call before the question |
| ---- | ----------------------------------------------- | ------------- | -------- | --------------------------------------------------------------------------------- | --------------------------------------- |
| 1.1  | Research question                               | settled       | round 1  | the sheet's sentence, quoted                                                      | none                                    |
| 1.2  | Ethics route                                    | settled       | round 2  | the sheet row, quoted                                                             | none                                    |
| 1.3  | Data plan                                       | settled       | round 2  | the sheet row, quoted                                                             | none                                    |
| 2.2  | Conditions, trials and session estimate         | pilot settles | round 5  | the sheet row, quoted                                                             | turn 5, trial count and session         |
| 2.3  | Pilot plan                                      | settled       | round 6  | the sheet row, quoted                                                             | none                                    |
| 2.4  | Timeline                                        | provisional   | round 7  | "I don't know yet", the recommended dates stand in; listed first under Open items | none                                    |
| 2.5  | Expected challenges and responses               | settled       | round 8  | the sheet row, quoted                                                             | none                                    |
| 6.1  | Hypotheses and research question                | settled       | round 2  | the sheet row, quoted                                                             | none                                    |
| 6.2  | Hypothesis variables, direction and testability | settled       | round 3  | `accepted recommendation` (the H2 margins), plus the sheet's source words quoted  | none                                    |
| 6.5  | Interaction hypotheses                          | settled       | round 3  | "No interaction idea."                                                            | none                                    |
| 7.1  | Independent variable and its levels             | settled       | round 2  | the sheet row, quoted                                                             | turn 2                                  |
| 7.2  | Carry-over symmetry                             | settled       | round 3  | the sheet row, quoted                                                             | turn 3                                  |
| 7.3  | The design named                                | settled       | round 4  | "Yes: a one-factor, two-level within-subjects design."                            | none                                    |
| 7.4  | Random assignment                               | settled       | round 3  | "No between-subjects variable."                                                   | none                                    |
| 7.5  | Counterbalancing                                | settled       | round 4  | the sheet row, quoted (the skill's four-cell pool crossing was not adopted)       | turn 4                                  |
| 7.6  | Dependent variables                             | settled       | round 2  | the sheet row, quoted; reliability and validity statements under Looked up        | turn 2                                  |
| 7.7  | Control variables                               | settled       | round 3  | the sheet row, quoted                                                             | turn 3                                  |
| 7.8  | Random variables                                | settled       | round 3  | the sheet row, quoted                                                             | none                                    |
| 7.9  | Confounds and their prevention                  | settled       | round 3  | the sheet row, quoted                                                             | turn 3                                  |
| 8.3  | Eligibility and screening                       | settled       | round 4  | the sheet row, quoted                                                             | none                                    |
| 8.5  | Participant count                               | settled       | round 5  | the sheet row, quoted whole                                                       | turn 5, typical counts                  |

Totals: 21 entries (`grep -c '^### '` on the frozen brief prints 21; the 21 headings are exactly the checklist's design-tree items), 19 settled, 1 pilot settles (2.2), 1 provisional (2.4). Every Decision line is at most 367 characters (the checker's limit is 400). Looked up holds 15 lines, 12 of them citing the hci-researcher. Open items: 1 is item 2.4 provisional with its recommendation, 2 is `/experiment-proposal:lit-search` (H1's direction under item 6.2 and the counts item 8.5 cites), 3 is `/experiment-proposal:the-ethics-board` (items 1.2 and 1.3 into the consent story item 12.3 needs).

### 2.2 and 2.4 and 8.5, as committed

```text
### 2.2 Conditions, trials and session estimate
- Decision: Two conditions, tap and swipe, one block each. Phrases per keyboard: the pilot decides, working value 20; it times both scored blocks with novices and sets the count to the largest that keeps the session, welcome to debriefing, inside about 40 minutes. Session estimate: about 40 minutes.
- Rationale: "The pilot will decide the phrases per keyboard; 20 is the working value; two conditions, about 40 minutes."
- Status: pilot settles
- Source: user, round 5

### 2.4 Timeline
- Rationale: "I don't know yet" — the course deadline is unknown, so the recommendation stands in: the dates chain the three-week IRB review (item 1.2) and the three-week collection window (item 7.9) forward from 2026-10-15.
- Status: provisional
- Source: user, round 7

### 8.5 Participant count
- Decision: 16 analyzable participants, 8 per keyboard order, pre-specified; an excluded participant is replaced within the same order; pilot participants do not count toward the 16.
- Rationale: "16: the two swipe-keyboard studies lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 at one session each, and 16 is a multiple of the two orders; pre-specified; the pilot refines the phrases per keyboard, not the count."
- Status: settled
- Source: user, round 5
```

## Pass bar

| Criterion                                                                                                                  | Result | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| -------------------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Every design-tree item (21) has an entry that is settled, provisional or pilot settles; 2.4 provisional; 2.2 pilot settles | PASS   | 21 entries, in checklist order, no `weak` or `missing` in the brief; `grep '^- Status'` counts 19 `settled`, 1 `pilot settles`, 1 `provisional`. `Status: provisional` sits under 2.4 and `Status: pilot settles` under 2.2.                                                                                                                                                                                                                                                                                                   |
| 8.5 justified from the sheet (a provisional 8.5 also meets the bar)                                                        | PASS   | 8.5 is settled; its Rationale quotes the sheet row whole: the two studies' 12 to 20 in within-subjects comparisons, the course term allowing 16 at one session each, 16 a multiple of the two orders, pre-specified, the pilot refining the phrases per keyboard and not the count. The Decision line says 16, 8 per order, pre-specified. Open items 2 sends lit-search to find the comparable studies' counts.                                                                                                               |
| At least one hci-researcher subagent call across all turns                                                                 | PASS   | 8 `Agent` tool_use entries whose input names `experiment-proposal:hci-researcher` (the `subagent_type`): turn 2, "Within-subjects reason for item 7.1" and "Dependent variables for item 7.6"; turn 3, "Carry-over symmetry for item 7.2", "Control variables for item 7.7", "Confounds for item 7.9"; turn 4, "Counterbalancing for item 7.5"; turn 5, "Trial count and session for item 2.2", "Typical participant counts for item 8.5". Turns 1 and 6 to 10: none. All eight tool results came back with text and no error. |
| Checker exits 0 on the frozen brief                                                                                        | PASS   | `cd "$S" && python3 "$P/scripts/check_proposal.py" brief proposal/design-brief.md > chk.out 2> chk.err; echo "exit=$?"` printed `exit=0`; stdout empty (0 bytes), stderr empty (0 bytes). The brief at that moment had `Status: frozen 2026-10-15`.                                                                                                                                                                                                                                                                            |
| The freeze commit exists                                                                                                   | PASS   | `git -C "$S" log --oneline` printed `cad4cfc Freeze the design brief` and `7ab551e init`; `git show --stat HEAD` shows one file, `proposal/design-brief.md`, 176 insertions, author `eval <eval@example.invalid>`; `git status --porcelain` is empty.                                                                                                                                                                                                                                                                          |

## Diagnostics (not the bar)

### Settled items asked again, and settled entries edited

Method: every `Write` and `Edit` call on `proposal/design-brief.md` across the ten jsonl files was replayed in order (25 calls; the replay equals the committed file entry for entry), and each entry's text compared after every call; the brief was also snapshotted after turns 3 to 10 (`$S.brief.after3` to `$S.brief.after10`) and compared entry by entry. Each round's closing text was split into its numbered questions and the item IDs in each were compared with the entries already written.

- Entries changed after being written, in a later turn: none. 20 of the 21 entries were written once and never touched again; the Status line of the header changed from `open` to `frozen 2026-10-15` in turn 10 and nothing else changed in the final turn.
- One entry changed within the turn that wrote it: item 7.6's Decision line was rewritten twice in turn 3 (a wording addition on the reliability statement, then a shortening after the checker reported `entry 7.6: Decision line is 411 characters; at most 400`). Both rewrites precede the user's seeing the entry, so it does not count as an edit of a settled entry; it is the checker catching a shape defect.
- Entries moved, not rewritten: the checker reported `entries are not in checklist order` in turns 4 and 5; the skill reordered the entries in the same turn (the replay shows no text change).
- Numbered questions whose target was a settled item: 0 of 21 (1 + 5 + 7 + 3 + 2 + 1 + 1 + 1 questions over the eight rounds, each design-tree item put once). Every question's target was in the frontier line above it, and the frontier lines list exactly the targets.
- Numbered questions that name a settled item's ID as context or inside a recommendation's basis (the item itself was not put to the user): round 4 Q1 (item 7.3) names 6.5 ("because item 6.5 settled with no interaction hypothesis"); round 4 Q3 (item 8.3) names 7.7 ("Your settled item 7.7 already names four") and 1.3; round 5 Q1 (item 2.2) names 7.9 ("the 40 minutes you settled on in item 7.9"), 7.6 and 7.5; round 6 Q1 (item 2.3) names 2.2 and 7.5; round 7 Q1 (item 2.4) names 1.2, 7.9 and 2.2; round 8 Q1 (item 2.5) names 8.3, 1.2, 2.3 ("Your settled item 2.3 does not have the pilot measuring the error rate"), 2.2 and 7.9. None offers an amendment or asks for a new decision on the named item. Borderline: round 5 Q2 (item 8.5) says "One thing to decide with your eyes open, because it bears on your settled H2" and offers a statement about H2's margin to put in the proposal; the sheet row was given, the 8.5 entry did not carry the statement, and the fact is a Looked up line ("Non-inferiority at 16 participants ...").
- Unnumbered offer on a settled item: turn 9's closing text offers to record item 2.3 with screened novices "rather than amend it later". It is outside the numbered questions and changed nothing; the turn-10 reply said 2.3 stays. Counts, by reading. (a) Settled items put to the user for a new decision or offered for amendment, the reading the baseline record v2-1 used: 0 in numbered questions; 1 if the unnumbered offer counts (item 2.3). (b) Entries changed after the user saw them: 0. (c) Under the literal reading of the definition, a numbered question "names" a settled item whenever its ID appears in the question: 10 distinct settled items (6.5, 7.7, 1.3, 7.9, 7.6, 7.5, 2.2, 1.2, 8.3, 2.3) were named by ID across 6 questions (round 4 Q1 and Q3, and round 5, 6, 7 and 8 Q1), 16 mentions in all, every one as basis or context as listed above, plus one mention of "your settled H2" without an ID (round 5 Q2); the orchestrator picks the reading. Baseline v2-1 for comparison, reading (a): 3 asked (items 1.1, 1.3, 2.5), 0 changed.

### Frontier IDs above Q1

Listed in 8 of 8 rounds, on a line "Frontier: item(s) ..." directly above Q1, and each list equals the set of that round's question targets (see the Transcript lines). The frontier follows the dependencies: 6.2 waited for 6.1; 7.3 waited for 6.5 and 7.5 for 7.2 (both settled in the round-3 answers); 8.3 waited for 7.7; 2.2 and 8.5 waited for 7.3 (8.5 also for 7.6); 2.3 waited for 2.2, which was `pilot settles`; 2.4 for 2.3; 2.5 for 2.4 (provisional).

### Checker each round

| Turn | Checker runs | Result                                                                                                                                  |
| ---- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | 2            | First call refused by the allow-list (it ended `; echo "exit $?"`: "This Bash command contains multiple operations"); second call clean |
| 2    | 0            | The brief was edited (item 1.1 entry added) and the checker was not run                                                                 |
| 3    | 2            | First: `Exit code 1`, `proposal/design-brief.md:43: entry 7.6: Decision line is 411 characters; at most 400`; fixed, second clean       |
| 4    | 2            | First: `Exit code 1`, `proposal/design-brief.md:5: entries are not in checklist order`; fixed, second clean                             |
| 5    | 2            | First: the same line-5 order defect; fixed, second clean                                                                                |
| 6    | 1            | Clean                                                                                                                                   |
| 7    | 1            | Clean                                                                                                                                   |
| 8    | 1            | Clean                                                                                                                                   |
| 9    | 1            | Clean (plus a `grep -c '^### '` count of 21)                                                                                            |
| 10   | 1            | Clean, after the Status edit and before the commit                                                                                      |

The checker ran after the brief was rewritten in 9 of 10 turns; turn 2 is the exception, and no defect hid behind it (the next run, in turn 3, failed only on an entry written in turn 3).

### The freeze

Ran, not refused. Turn 10 order: Edit (`Status: frozen 2026-10-15`), checker (no output), then `git add proposal/design-brief.md && git commit -m "Freeze the design brief" -- proposal/design-brief.md`, which returned `[master cad4cfc] Freeze the design brief`. `permission_denials` is empty in turn 10. The commit used the scratch project's own `eval <eval@example.invalid>` identity.

## Observations beyond the bar

1. The checker was not run in turn 2, a partial miss of the fix under test. Fix commit ed96208 is titled "runs the checker each round" and `SKILL.md` step 3 says "Rewrite the brief after every round and run the checker on it"; turn 2 rewrote the brief (the item 1.1 entry, one `Edit`) and made no checker call. The checker ran in turn 1 and in turns 3 to 10, and the one skipped round hid no defect, but the skill did not run it every round.
2. One unnumbered offer to reopen a settled item survived the fix. Turn 9's closing text noted that item 2.2 has the pilot time the blocks with novices while item 2.3 draws the four pilot participants from the lab, and offered to record 2.3 with screened novices. The observation is accurate (2.3 as the user gave it conflicts with the "with novices" wording in the 2.2 entry), but the offer sits where the skill's rule on settled items says a concern goes into a recommendation's basis, not into a question or an offer. It cost one clause in the freeze reply and changed no entry.
3. The skill's wording enters entries under the user's name. The 2.2 Decision's "it times both scored blocks with novices and sets the count to the largest that keeps the session ... inside about 40 minutes" is the skill's gloss on the sheet's "the pilot will decide the phrases per keyboard"; the "with novices" clause is what conflicts with 2.3 (observation 1). The 8.5 Decision adds "an excluded participant is replaced within the same order; pilot participants do not count toward the 16", which came from the hci-researcher, under `Source: user, round 5`. The Rationale lines in both entries do quote the sheet exactly.
4. The checker is doing real work: three of the run's ten turns hit a failure (a 411-character Decision, and entries out of checklist order twice), each fixed in the turn.
5. Harness recoveries in turn 1 (as in v2-1): `cat` of the plugin's `plugin.json` was refused ("may only concatenate files from the allowed working directories"), and the skill used `Read` instead; the checker call with `; echo "exit $?"` was refused by the `Bash(python3:*)` allow-list and retried without it. Neither recurred.
6. Against the baseline run v2-1 (`runs/from-scratch-v2-1.md`, plugin commit 5e13529): items 7.7 and 7.9 were settled in the first pass (v2-1 held them open, asked grip and four further confounds, and ended both `provisional`); no draft-path question (v2-1 asked Q0); no numbered question offered to amend a settled item (v2-1: three); the 2.4 entry was written in the turn that answered it (v2-1: a turn late); the run took 10 turns, not 11, with 19 settled and 1 provisional instead of 17 settled and 3 provisional. This is one run of the three that scenario 3 needs; its bar holds only if all three meet it.

## `git log --oneline` in the scratch project

```text
cad4cfc Freeze the design brief
7ab551e init
```
