# Scenario 3 (design from scratch) at 0.2.0, run v2-3

Date: 2026-10-15
Plugin commit: 5e13529 (`experiment-proposal` 0.2.0; `git diff 5e13529 -- plugins/experiment-proposal` is empty at the end of the run)
Fixture: `fixtures/from-scratch-answers.md`; no material file. Scratch project `S=/tmp/ep-eval/from-scratch-v2-3` (a repository whose only commit before the freeze is `init`; `proposal/` did not exist, the session created it).
Model: `--model opus`, which the init event of every turn reports as `claude-opus-5`.

Verdict: PASS. All bar criteria hold (21 of 21 design-tree items have an entry, 2.4 provisional, 2.2 pilot settles, 8.5 provisional and justified from the sheet; 6 `hci-researcher` calls, 5 answered and 1 killed by the 429; the checker exits 0 on the frozen brief; the freeze commit `6decbb3` exists). The freeze's `git add` and `git commit` ran, as two Bash calls, and were not refused. Three settled items were asked again (7.2, 8.5, 2.5) and each moved to provisional after the answer "I don't know" (the sheet does not answer those questions); five more settled entries changed without a question (1.3, 6.1, 7.6, 7.9, 2.3), and provisional 7.2's Decision was extended in turn 11.

## Harness event: rate-limit interruption and resumption

A first driver ran turns 1 to 4 and was killed by the account's session rate limit. Turn 4 itself failed mid-turn: `rc=1 secs=124` in its `.meta`, and its result event reads `is_error` true, `terminal_reason` `api_error`, `api_error_status` 429, `result` `You've hit your session limit · resets 3:40am (America/Chicago)`. The failing call was the `Agent` call to `experiment-proposal:hci-researcher` for item 7.5 ("Counterbalancing scheme"); its tool result was `Agent terminated early due to an API error: You've hit your session limit · resets 3:40am (America/Chicago) (error type rate_limit, HTTP 429 ...)`. Before the call the session had already written the brief for round 3 (`Write` of `proposal/design-brief.md`, 10 entries new or edited); at the start of this resumption `git log --oneline` in `$S` showed only `97236fb init` and `git status --porcelain` showed `?? proposal/`.

The resumption (this record's driver) inspected the brief and the tail of turn 4's jsonl, copied `$S.turn4.prompt` to `$S.turn5.prompt` (`cmp` reports them identical) and re-sent it as turn 5 at 02:03 local time, before the 3:40 reset the message names. Turn 5 and every later turn ran to completion: each result event has `is_error` false and `api_error_status` null, `subtype` `success`. No turn was retried and no turn showed a 429 or "session limit". Every turn, 1 to 12, has the same `session_id` (`--continue` resumed the project's one session), so the interruption cost the session no state. The brief on disk before turn 5 had the same size (14953 bytes) as a replay of turns 1 to 4's Write and Edit calls, the replay through turn 5 equals the disk file, and so does the replay through turn 12; the committed file equals the working copy.

One consequence of the 429 for the evidence: when turn 5 re-ran the round, it did not repeat the lost `hci-researcher` call. It said "The `hci-researcher` subagent hit a session rate limit on the counterbalancing question, so Q2 below is recommended from the checklist and the material instead" (the skill's step 4: "If the subagent is unavailable, say so once and recommend from the checklist and the material in its absence"), and no later turn asked the subagent about item 7.5.

## Commands

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/from-scratch-v2-3
# turn 1 (the prompt is read from "$S.turn1.prompt"); turns 1 to 4 by the first driver
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null
# turns 2 to 12: the same command with --continue before the prompt, prompt read from "$S.turn<N>.prompt"
cd "$S" && timeout 1800 claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn<N>.jsonl" 2> "$S.turn<N>.err" < /dev/null
# the helper that wrapped each turn: bash /tmp/ep-eval/review-v2-drive.sh "$S" <N>   (writes "$S.turn<N>.meta" with rc and seconds)
# the criterion check, run after the freeze
cd "$S" && python3 "$P/scripts/check_proposal.py" brief proposal/design-brief.md; echo "exit=$?"
```

The raw stream-json output is kept outside the repository as `$S.turn<N>.jsonl`. The brief after each turn was rebuilt from that turn's `Write` and `Edit` calls on `proposal/design-brief.md` (a replay, compared with the disk file at the end of the run) to find which entries changed in which turn.

## Turns (one line each)

| Turn | By              | Wall        | Agent calls     | What the skill did                                                                                                                                                                                                                                                                                                                                        | What was sent                                                                                              |
| ---- | --------------- | ----------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 1    | first driver    | 91 s        | 0               | Read the checklist, `brief.md`, `plugin.json` and the checker; extracted 21 design-tree items (none settled: 1.1 weak, the rest weak or missing); wrote the open brief with no entries, checker clean; assumed the draft path; asked round 1 (1.1). Two Bash calls were denied as compound commands and the skill recovered (a Read, a plain checker run) | the idea line, `/experiment-proposal:design ...`                                                           |
| 2    | first driver    | 199 s       | 2               | Recorded 1.1 settled; consulted `hci-researcher` for 7.1 and 7.6; asked round 2 (1.2, 1.3, 6.1, 7.1, 7.6); "Brief rewritten, checker clean. Item 1.1 unblocked five items."                                                                                                                                                                               | the sheet answer for 1.1                                                                                   |
| 3    | first driver    | 395 s       | 3               | Recorded round 2 (5 entries); consulted `hci-researcher` for 7.7, 7.9 and 7.2; asked round 3 (6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9); made 6.2's H2 a non-inferiority claim and recommended 7.2 as pilot settles ("Three of my sources disagree; Q3 is the crux"); no Bash call, the checker not run                                                          | the sheet answers for 1.2, 1.3, 6.1, 7.1, 7.6                                                              |
| 4    | first driver    | 124 s, rc 1 | 1 (failed, 429) | Wrote the brief for round 3 (6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9 new; 1.3, 6.1, 7.6 edited), said it would state the 7.2 risk once, then the `hci-researcher` call for 7.5 died with the 429; the turn ended with `You've hit your session limit`                                                                                                           | the sheet answers for 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9, plus "keep mine" for the words-per-minute formula |
| 5    | this resumption | 71 s        | 0               | Same prompt as turn 4. Ran the checker for the first time since round 1: 7.9 Decision 606, 477, 432, then 410 characters against the limit of 400, four edit and check cycles, then clean; said the subagent was unavailable for 7.5; asked round 4 (7.3, 7.5, 8.3)                                                                                       | turn 4's text, unchanged                                                                                   |
| 6    | this resumption | 112 s       | 0               | Recorded 7.3, 7.5, 8.3 settled; rewrote settled 7.9 (the "disjoint phrase subsets" prevention became "Phrase familiarity: one set both blocks"); "Brief clean: 16 of 21 items settled"; asked round 5 (2.2, 8.5)                                                                                                                                          | the sheet answers for 7.3, 7.5, 8.3                                                                        |
| 7    | this resumption | 53 s        | 0               | Recorded 2.2 pilot settles and 8.5 settled; checker clean, "18 of 21 settled"; asked round 6 (2.3) and, inside Q1, a three-way choice on the number of sessions that reopens settled 8.5                                                                                                                                                                  | the sheet answers for 2.2 and 8.5                                                                          |
| 8    | this resumption | 74 s        | 0               | Recorded 2.3 settled; 8.5 became provisional ("Whether the term's slots cover 20 sessions rather than 16 the user could not say"); "19 of 21 settled, item 8.5 provisional"; asked round 7 (2.4, and Q2 on settled 7.2)                                                                                                                                   | the sheet answer for 2.3, and "I don't know" on the three session counts                                   |
| 9    | this resumption | 71 s        | 0               | Recorded 2.4 provisional; 7.2 became provisional; asked round 8 (2.5, seven challenges, "Yes accepts all seven")                                                                                                                                                                                                                                          | "I don't know yet" for 2.4, "I don't know" for the 7.2 question                                            |
| 10   | this resumption | 41 s        | 0               | Recorded 2.5 settled from the two challenges the sheet gives; "All 21 design-tree items have a status: 17 settled, 1 pilot settles (item 2.2), 3 provisional (items 2.4, 7.2, 8.5)"; asked a "Last question" on 2.5 (running short of time) and offered the brief for approval ("Say freeze")                                                             | the sheet answer for 2.5                                                                                   |
| 11   | this resumption | 135 s       | 0               | Recorded 2.5 provisional; trimmed settled 2.3 (dropped a claim the user did not take), added the interim look to 7.2, a Looked up fact and Open items; "Rounds are done. Every design-tree item has a status, the checker exits 0"; summary 16 settled, 1 pilot settles, 4 provisional; "Say freeze"                                                      | "I don't know" on running short of time                                                                    |
| 12   | this resumption | 22 s        | 0               | Set `Status: frozen 2026-10-15`, ran the checker (no output), ran `git add proposal/design-brief.md`, then `git commit -m "Freeze the design brief" -- proposal/design-brief.md`: commit `6decbb3`                                                                                                                                                        | approval and the freeze                                                                                    |

Total: 12 turns (turn 4 interrupted and re-sent as turn 5), 8 rounds of numbered questions, one extra question on 2.5 and the approval question, 6 `hci-researcher` calls (5 answered).

Turn texts, verbatim. Turns 1 to 4 were sent by the first driver; turn 5 is turn 4 re-sent unchanged.

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
Words per minute formula: keep mine (characters over five over minutes), as in item 7.6.
```

Turn 5:

```text
Item 6.2 (Q1): Yes to the recommendation. Sources: the two swipe-keyboard studies I "will add from lit-search"; accept the direction as settled, with lit-search listed under Open items.
Item 6.5 (Q2): No interaction idea.
Item 7.2 (Q3): Symmetric: each keyboard is minutes of practice from the other.
Item 7.4 (Q4): No between-subjects variable.
Item 7.7 (Q5): Right-handed, 18 to 35, owns a smartphone, never used swipe; same phone, app, phrases, room, script; yes to the recommended validity trade-off wording.
Item 7.8 (Q6): Typing skill, mood, time of day, phrase order.
Item 7.9 (Q7): History: run all sessions within three weeks; maturation: one 40-minute session; instrumentation: freeze the app before the first participant.
Words per minute formula: keep mine (characters over five over minutes), as in item 7.6.
```

Turn 6:

```text
Item 7.3 (Q1): Yes: a one-factor, two-level within-subjects design.
Item 7.5 (Q2): Counterbalance keyboard order, AB and BA, half each, assigned from a shuffled list; the same phrase set for both keyboards, in a fresh random order per keyboard.
Item 8.3 (Q3): The four criteria above, screened by a sign-up form; none selects on typing speed.
```

Turn 7:

```text
Item 2.2 (Q1): The pilot will decide the phrases per keyboard; 20 is the working value; two conditions, about 40 minutes.
Item 8.5 (Q2): 16: the two swipe-keyboard studies lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 at one session each, and 16 is a multiple of the two orders; pre-specified; the pilot refines the phrases per keyboard, not the count.
```

Turn 8:

```text
Item 2.3 (Q1): Four people from the lab; it refines the phrases per keyboard (recorded under 2.2) and the script timings; its data will not be reported. On your choice among the three session counts: I don't know.
```

Turn 9:

```text
Item 2.4 (Q1): I don't know yet.
Item 7.2 (Q2): I don't know.
```

Turn 10:

```text
Item 2.5 (Q1): Too few sign-ups: extend recruiting to a second course; a keyboard app failing in the pilot: freeze a fallback build.
```

Turn 11:

```text
Item 2.5 (Q1, running short of time): I don't know.
```

Turn 12:

```text
I approve the brief as it stands. Freeze.
```

How the sheet was applied where the skill's question went beyond it. The skill's questions that the sheet does not answer got "I don't know": the three-way choice on the number of sessions in round 6 (turn 8), the 7.2 carry-over-check question in round 7 (turn 9), and the 2.5 "running short of time" question (turn 11). Where a sheet row answers part of a question, the sheet text was sent as it stands, and 2.3's row was not extended to say the pilot is outside the course term's slots (the row says "four people from the lab", nothing about slots). The sheet's 1.1 wording was sent in turn 2 (the skill had asked a different wording and "Yes accepts it"). The draft path was never answered: the skill assumed `proposal/draft.md` in turn 1 ("Say otherwise and I change it") and the brief's header reads `Draft: proposal/draft.md`.

## Decisive transcript lines

Turn 4 (the 429; the end of its jsonl):

```text
[TEXT] Recorded. Two readings I made explicit, correct me if wrong: ... On item 7.2 your decision stands and I have recorded it. ...
[TOOL] Agent {"subagent_type": "experiment-proposal:hci-researcher", "description": "Counterbalancing scheme", ...}
[RESULT] ERR  Agent terminated early due to an API error: You've hit your session limit · resets 3:40am (America/Chicago) (error type rate_limit, HTTP 429, ...)
[FINAL] You've hit your session limit · resets 3:40am (America/Chicago)
```

Turn 5 (resumption; checker on the brief the interrupted turn wrote, and the subagent note):

```text
proposal/design-brief.md:92: entry 7.9: Decision line is 606 characters; at most 400
proposal/design-brief.md:92: entry 7.9: Decision line is 477 characters; at most 400
proposal/design-brief.md:92: entry 7.9: Decision line is 432 characters; at most 400
proposal/design-brief.md:92: entry 7.9: Decision line is 410 characters; at most 400
(then no output)
Brief rewritten with all of round 3; checker exits 0. Thirteen of 21 items settled. The `hci-researcher` subagent hit a session rate limit on the counterbalancing question, so Q2 below is recommended from the checklist and the material instead — saying so once, as the skill requires.
```

Turn 7 (the question that reopens settled 8.5, with the sheet's own reasons as its premise):

```text
One conflict to settle with it: item 8.5's reason was that "the course term allows 16 at one session each". Four pilot sessions make 20 sessions, not 16. Say which you want —
- **4 pilot plus 16 main, 20 sessions**, ...
- **4 pilot plus 12 main**, ...
- **2 pilot plus 16 main**, ...
Recommended of the three: 4 pilot plus 16 main, and item 8.5's reason gets one added clause ... That rewrites item 8.5's rationale, which is allowed while the brief is open.
```

Turn 8 (settled 7.2 asked again; the result of "I don't know" is in turn 9):

```text
**Q2 — item 7.2, where the carry-over check now runs.** Item 7.2 is settled on your judgment that carry-over is symmetric, and its "Would change if" line pointed the check at the pilot. A lab pilot cannot do it.
```

Turn 9 (the 7.2 entry after "I don't know"):

```text
The user could not say where the symmetry check should run once the pilot became a lab pilot (item 2.3), so the recommendation stands in and the item is provisional: a pre-specified interim look at the first 8 main-sample participants.
- Status: provisional
```

Turn 10 (all 21 have a status; settled 2.5 asked again):

```text
All 21 design-tree items have a status: 17 settled, 1 pilot settles (item 2.2), 3 provisional (items 2.4, 7.2, 8.5). Checker exits 0. The frontier is empty but for one gap.
**Last question — item 2.5, running short of time.** You took two of the seven challenges. Of the three the checklist names by name, "running short of time" is still unanswered, and item 2.4's timeline is itself provisional, so this is the gap a reviewer will find.
```

Turn 11 (the closing summary and the disclosure of what was folded in):

```text
- **settled, 16**: 1.1 question · 1.2 IRB route · 1.3 data plan · 2.3 pilot · 6.1 hypotheses · 6.2 variables and nulls · 6.5 no interaction · 7.1 independent variable · 7.3 design · 7.4 assignment · 7.5 counterbalancing · 7.6 dependent variables · 7.7 controls · 7.8 random variables · 7.9 confounds · 8.3 eligibility
- **pilot settles, 1**: 2.2, phrases per keyboard — working value 20, ...
- **provisional, 4**: 2.4 timeline · 2.5 running short of time · 7.2 carry-over check · 8.5 participant count — each listed under Open items with the recommendation standing in
Three things I folded in that were my recommendations, not your words — all named in the rationales so `review` can see it: item 7.7's keyboard settings, item 7.9's six unnamed confound preventions, and the cut order under item 2.5.
```

Turn 12 (the freeze: Edit, checker, then two Bash calls; no permission denial in the result event):

```text
Edit: "Status: open" -> "Status: frozen 2026-10-15"
Bash: python3 "<checkout>/plugins/experiment-proposal/scripts/check_proposal.py" brief proposal/design-brief.md   (no output)
Bash: git add proposal/design-brief.md
Bash: git commit -m "Freeze the design brief" -- proposal/design-brief.md
[master 6decbb3] Freeze the design brief
 1 file changed, 171 insertions(+)
 create mode 100644 proposal/design-brief.md
Frozen and committed: `6decbb3 Freeze the design brief`. Checker exits 0 on the frozen brief.
```

Subagent calls (the `Agent` tool_use entries whose input names `experiment-proposal:hci-researcher`, counted in every turn's jsonl):

```text
turn 1: 0
turn 2: 2  "IV definition and within-subjects reason" (7.1), "Dependent variable definitions" (7.6)
turn 3: 3  "Control variables" (7.7), "Confounds and validity threats" (7.9), "Carry-over symmetry" (7.2)
turn 4: 1  "Counterbalancing scheme" (7.5) -- killed by the 429, no answer
turns 5 to 12: 0
total: 6 calls, 5 answered
```

## Per-item status (the 21 design-tree items, in the frozen brief)

The 21 are the checklist's items whose scope reads `design-tree`: 1.1, 1.2, 1.3, 2.2, 2.3, 2.4, 2.5, 6.1, 6.2, 6.5, 7.1 to 7.9, 8.3, 8.5. "Asked" is the turn whose final text put the question; "answered" is the next turn.

| Item | Name                                     | Final status  | Asked (answered in turn)                                                   | Asked again, or entry changed after it was settled                                                                                                         |
| ---- | ---------------------------------------- | ------------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1  | Research question                        | settled       | round 1, Q1, turn 1 (2)                                                    | no                                                                                                                                                         |
| 1.2  | Ethics route                             | settled       | round 2, Q1, turn 2 (3)                                                    | no                                                                                                                                                         |
| 1.3  | Data plan                                | settled       | round 2, Q2, turn 2 (3)                                                    | entry changed in turn 4 with no question (the screening answers of item 8.3 and a consent-forms sentence added to Decision, Rationale and Would change if) |
| 2.2  | Conditions, trials and session length    | pilot settles | round 5, Q1, turn 6 (7)                                                    | no                                                                                                                                                         |
| 2.3  | Pilot plan                               | settled       | round 6, Q1, turn 7 (8)                                                    | entry trimmed in turn 11 with no question (the claim that the pilot checks the logging app was removed)                                                    |
| 2.4  | Timeline                                 | provisional   | round 7, Q1, turn 8 (9)                                                    | no                                                                                                                                                         |
| 2.5  | Expected challenges and responses        | provisional   | round 8, Q1, turn 9 (10); asked again as "Last question" in turn 10 (11)   | asked again; settled in turn 10, provisional in turn 11 after "I don't know"                                                                               |
| 6.1  | Hypotheses and research questions        | settled       | round 2, Q3, turn 2 (3)                                                    | entry changed in turn 4 with no question (H2 labelled non-inferiority)                                                                                     |
| 6.2  | Hypothesis variables, direction and null | settled       | round 3, Q1, turn 3 (4, re-sent 5)                                         | no                                                                                                                                                         |
| 6.5  | Interaction hypotheses                   | settled       | round 3, Q2, turn 3 (4, re-sent 5)                                         | no                                                                                                                                                         |
| 7.1  | Independent variable                     | settled       | round 2, Q4, turn 2 (3)                                                    | no                                                                                                                                                         |
| 7.2  | Carry-over symmetry                      | provisional   | round 3, Q3, turn 3 (4, re-sent 5); asked again as round 7, Q2, turn 8 (9) | asked again; settled in turn 4, provisional in turn 9 after "I don't know", Decision line extended in turn 11                                              |
| 7.3  | Overall design                           | settled       | round 4, Q1, turn 5 (6)                                                    | no                                                                                                                                                         |
| 7.4  | Random assignment                        | settled       | round 3, Q4, turn 3 (4, re-sent 5)                                         | no                                                                                                                                                         |
| 7.5  | Counterbalancing                         | settled       | round 4, Q2, turn 5 (6)                                                    | no                                                                                                                                                         |
| 7.6  | Dependent variables                      | settled       | round 2, Q5, turn 2 (3)                                                    | entry changed in turn 4 with no question (the "keep mine" formula answer added to the Rationale)                                                           |
| 7.7  | Control variables                        | settled       | round 3, Q5, turn 3 (4, re-sent 5)                                         | no                                                                                                                                                         |
| 7.8  | Random variables                         | settled       | round 3, Q6, turn 3 (4, re-sent 5)                                         | no                                                                                                                                                         |
| 7.9  | Confounds and their prevention           | settled       | round 3, Q7, turn 3 (4, re-sent 5)                                         | entry shortened to fit 400 characters in turn 5 (four edits), then rewritten in turn 6 after 7.5's answer; no question                                     |
| 8.3  | Eligibility and screening                | settled       | round 4, Q3, turn 5 (6)                                                    | no                                                                                                                                                         |
| 8.5  | Participant count                        | provisional   | round 5, Q2, turn 6 (7); reopened inside round 6, Q1, turn 7 (8)           | asked again; settled in turn 7, provisional in turn 8 after "I don't know", Decision and Rationale rewritten (16 main plus 4 pilot, 20 sessions)           |

Counts: 16 settled (1.1, 1.2, 1.3, 2.3, 6.1, 6.2, 6.5, 7.1, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8.3), 1 pilot settles (2.2), 4 provisional (2.4, 2.5, 7.2, 8.5), 21 in all; the skill's closing summary in turn 11 gives the same counts.

Frozen brief, header and statuses (read from `proposal/design-brief.md` in the scratch project):

```text
Draft: proposal/draft.md
Status: frozen 2026-10-15
Checklist: experiment-proposal 0.2.0
1.1 settled; 1.2 settled; 1.3 settled; 2.2 pilot settles; 2.3 settled; 2.4 provisional; 2.5 provisional;
6.1 settled; 6.2 settled; 6.5 settled; 7.1 settled; 7.2 provisional; 7.3 settled; 7.4 settled; 7.5 settled;
7.6 settled; 7.7 settled; 7.8 settled; 7.9 settled; 8.3 settled; 8.5 provisional
Open items: 1. Item 2.4 provisional; 2. Item 2.5 provisional; 3. Item 7.2 provisional; 4. Item 8.5 provisional; 5. Run lit-search (H1's two citations, H2's 10-point margin, the 12-to-20 participant range under 8.5); 6. Run the-ethics-board
```

Item 2.2, as written:

```text
- Decision: Two conditions per participant, tap and swipe. Phrases per keyboard: 20 is the working value, plus 5 practice phrases excluded from analysis; the pilot sets the final number from the per-phrase time it measures and from how stable a participant's mean words per minute is as phrases are added. Session about 40 minutes, welcome to debriefing.
- Status: pilot settles
```

Item 8.5, as written:

```text
- Decision: 16 participants in the main sample, 8 per order, pre-specified before data collection, plus the 4 pilot participants of item 2.3, so 20 sessions in all. The pilot refines the phrases per keyboard (item 2.2), not the count.
- Rationale: "the two swipe-keyboard studies lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 at one session each, and 16 is a multiple of the two orders" — the count rests on a named resource limit, the term's session slots, inside the range of the comparable studies, and 16 satisfies item 8.8 as a multiple of the 2 counterbalanced orders. Whether the term's slots cover 20 sessions rather than 16 the user could not say, so the recommendation of 16 main plus 4 pilot stands in and the item is provisional.
- Status: provisional
```

## Pass bar

| Criterion                                                                         | Result    | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| --------------------------------------------------------------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Every design-tree item has an entry that is settled, provisional or pilot settles | PASS      | 21 of 21 entries (the checklist's 21 design-tree items), statuses in the table above: 16 settled, 1 pilot settles, 4 provisional; none is `weak` or `missing`; the checker (which reads the same entries) exits 0.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| 2.4 provisional, 2.2 pilot settles                                                | PASS      | `2.4 Timeline`, `Status: provisional` (answer "I don't know yet", the recommendation of ten weeks stands in, Open item 1); `2.2 Conditions, trials and session length`, `Status: pilot settles` (the pilot sets the phrases per keyboard, 20 the working value).                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Item 8.5 justified from the sheet (a provisional 8.5 meets the bar)               | PASS      | Status `provisional`. The Rationale quotes the sheet's reason whole: the two swipe-keyboard studies lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 at one session each, and 16 is a multiple of the two orders. The count is 16 in the main sample, pre-specified, with the pilot refining the phrases, not the count. The studies are not yet in hand; Open item 4 and Open item 5 (lit-search) carry that. The entry also adds the 4 pilot participants (20 sessions), which the sheet does not say.                                                                                                                                                     |
| At least one `hci-researcher` call across all turns                               | PASS      | 6 `Agent` tool_use entries whose input names `experiment-proposal:hci-researcher`: turn 2 (2: 7.1, 7.6), turn 3 (3: 7.7, 7.9, 7.2), turn 4 (1: 7.5, killed by the 429). 5 returned answers. Recommendations quote it as `Recommended (hci-researcher)`.                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `check_proposal.py brief proposal/design-brief.md` exits 0 on the frozen brief    | PASS      | Run by this record's driver after the freeze, from the scratch project (`cd "$S" && python3 "$P/scripts/check_proposal.py" brief proposal/design-brief.md`): stdout empty, stderr empty, exit code 0. The header reads `Status: frozen 2026-10-15`.                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| The freeze commit exists                                                          | PASS      | `git log --oneline` in the scratch project: `6decbb3 Freeze the design brief`, then `97236fb init`. The commit adds only `proposal/design-brief.md` (171 insertions); `git status --porcelain` is empty afterwards.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Recorded: did the freeze's `git add` and `git commit` run or get refused          | RAN       | The skill ran them as two Bash calls, `git add proposal/design-brief.md` and `git commit -m "Freeze the design brief" -- proposal/design-brief.md`, not as the single `&&` command the skill's step 7 spells; the commit returned `[master 6decbb3] Freeze the design brief` and turn 12's `permission_denials` is empty. Whether the `&&` form would have been refused is not shown by this run.                                                                                                                                                                                                                                                                                                         |
| Recorded: settled items asked again                                               | see below | Three settled items were asked again, one numbered: item 7.2 (round 7, Q2, turn 8), item 2.5 (the "Last question" of turn 10) and item 8.5 (the three-way session-count choice inside round 6, Q1, turn 7, which says it "rewrites item 8.5's rationale"). Each moved from settled to provisional after the sheet-faithful answer "I don't know" (turns 8, 9, 11). Entries changed after they were settled with no question: 1.3, 6.1 and 7.6 (turn 4, knock-on edits from the round 3 answers), 7.9 (turn 5, to fit the checker's 400 characters; turn 6, after 7.5's answer), and 2.3 (turn 11, a claim removed): five settled entries in all; provisional 7.2's Decision was also extended in turn 11. |

Questions asked in all: round 1 asked 1.1; round 2 asked 1.2, 1.3, 6.1, 7.1, 7.6; round 3 asked 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9; round 4 asked 7.3, 7.5, 8.3; round 5 asked 2.2, 8.5; round 6 asked 2.3 (and the 8.5 choice); round 7 asked 2.4 and 7.2 again; round 8 asked 2.5; the extra question asked 2.5 again. That is 21 items asked for the first time (1.1 included) and three asked again.

## Verdict

PASS: the bar criteria hold at plugin commit 5e13529 on this run, with the 429 interruption of turn 4 recorded above as a harness event and no 429 in any turn this resumption ran.

## Observations beyond the bar (possible plugin defects, not scored)

- Settled items are reopened. Step 3 asks "the frontier ... every weak or missing item" and step 1 says "every entry keeps its status", yet turn 7 reopened 8.5, turn 8 reopened 7.2 and turn 10 reopened 2.5, each from a check the skill made on its own. The 8.5 conflict rested on a premise the sheet does not give (that the four lab pilot participants draw on the course term's 16 slots; the sheet's 2.3 row says "four people from the lab"). The 7.2 question exists only because the skill judged that a lab pilot cannot run the carry-over check that 7.2's own "Would change if" line gave to the pilot. The skill has no line on when a settled entry may be asked again, and an answer of "I don't know" to such a question downgrades the entry (3 of the 4 provisional items here). A rule or a flag-and-ask-once pattern is missing; compare the unnumbered flags in `from-scratch-v2-2.md`, which had the same shape.
- Partial answers are recorded as decisions. Step 3 covers a bare "yes" and "I don't know", not a partial answer. For 7.9 the sheet names three confounds; the Decision line carries all nine, and the Rationale says "the six the user did not name carry the consulted preventions"; the skill's own closing line in turn 11 says "Three things I folded in that were my recommendations, not your words". The status stays `settled`.
- Item 2.5 over-reads the checklist. The checklist reads "such as too few sign-ups, a manipulation that fails in the pilot, or running short of time", examples; the skill treated the third as required ("Of the three the checklist names by name ... is still unanswered") after offering seven challenges and writing that "the user took these two of the seven challenges put to them", and the answer "I don't know" made 2.5 provisional.
- The checker runs only at step 6, so rounds 3 and 4 (turns 3 and 4) wrote 10 entries with no checker run, and the 400-character limit on 7.9's Decision was found in turn 5 and took four edit and check cycles (606, 477, 432, 410 characters). `references/brief.md` states the limit ("The Decision line is at most 400 characters").
- Item 7.5's recommendation was not the subagent's: the 429 killed the call, the skill said so once as step 4 requires, and no later turn went back to it after the limit lifted. Its fallback recommendation (disjoint phrase subsets per keyboard, sample a multiple of 4) contradicted the sheet's 7.5 row (the same phrase set for both keyboards), so 7.9 had to be rewritten in turn 6. This is a harness artifact of the 429, not a skill defect, but it explains the 7.9 churn.
- Draft path (step 1, "Ask once for the draft's planned path"): never asked as a question; "Draft path: assuming `proposal/draft.md`. Say otherwise and I change it." in turn 1, as in the other 0.2.0 from-scratch run.
- Turn 1 had two Bash calls denied by the allow-list as compound commands (`... && git log --oneline -3` and `...; echo "exit=$?"`); the skill recovered with a Read and a plain checker run. Step 7's `git add ... && git commit ...` was split into two calls by the session this time; it was not refused either way.
- Entry content beyond the sheet's words: 1.3's Rationale says "the signed consent forms are the only identifiable records and are stored apart from the logs", which neither the sheet nor the idea line says (it also adds the screening answers of 8.3 as the only other data kept). It is a derived fact written into a settled entry; no question asked for it.

## The brief

The full brief is `proposal/design-brief.md` in `$S` (committed as `6decbb3`); it has the three header lines, 21 entries each with the five lines, a Looked up section of seven facts (the standard phrase set, the words-per-minute convention and the user's variant, total error rate, the ISO 9241-411 rating items, the two-order counterbalancing arithmetic, the session arithmetic with its 20-words-per-minute assumption flagged, and what a non-inferiority claim requires), and the six Open items above.
