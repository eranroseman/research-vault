# Scenario 3, from scratch, run v2-6 (0.2.0, re-run on the fixed design skill)

Date: 2026-10-15. Plugin commit: 76e9c28 (plugin version 0.2.0; the brief's `Checklist:` line reads `experiment-proposal 0.2.0`). The harness file names 5e13529, the commit of the v2-1 baseline; for this run the plugin commit is 76e9c28 = design fix ed96208 plus the review and fixture fix 76e9c28. The fix that matters for this scenario is ed96208 ("design keeps settled items settled, lists the frontier, runs the checker each round, defaults the draft path"). Scenario label: from-scratch. Driver: headless `claude -p` turns, answered strictly from `fixtures/from-scratch-answers.md`; "I don't know" for anything the sheet does not answer; the brief and the freeze approved when asked. Ten turns in all, one driver, no rate limit hit, no resumption.

Verdict: PASS. Every bar criterion holds: 21 of 21 design-tree items have an entry (19 settled, 1 pilot settles, 1 provisional), 2.4 is provisional, 2.2 is pilot settles, 8.5 is settled and justified from the sheet, three hci-researcher calls, the checker exits 0 on the frozen brief, and the freeze commit `b33ea75 Freeze the design brief` exists with its `git add && git commit` run (not refused). Against v2-1's four behaviours: partial answers holding an item open and the brief lagging a turn did not recur; settled items put back to the user recurred once (round 4 Q3 offers an amendment of item 1.3; no entry changed); skill wording under the user's name recurred (see Observations).

## Harness notes

- Rate limit: no turn hit it. In all ten turn jsonl files `api_error_status` is `null`, `is_error` is false, `terminal_reason` is `completed`, the string "session limit" occurs 0 times, `rc=0` in every `$S.turn<N>.meta`, and every `.err` file is empty. The `rate_limit_event` lines all read `"status":"allowed"`, `"rateLimitType":"five_hour"`, with `utilization` rising from 0.13 (turn 1) to 0.21 (turn 10), `resetsAt` 1792065600 throughout.
- One sentence that reads like a rate limit and is not the headless turn's: the hci-researcher answer for item 7.9 (turn 3) opens "Advisor was rate-limited on my one attempt (instructed not to retry this turn), so this is my own assessment." That is the subagent's own text about an internal call it made; it is a Task result inside turn 3, whose final JSON shows no error. The stop rule (a turn's final JSON showing 429 or "session limit") did not fire; the answer it prefaces was still produced and used.
- The seven `"status":"failed"` entries per turn in the jsonl are the session-init MCP connection statuses of unrelated servers, not rate-limit events.
- Plugin integrity: at the end of the run `git diff --stat 76e9c28 HEAD -- plugins/experiment-proposal` printed nothing, `git status --porcelain plugins/` printed nothing, and `git rev-parse --short HEAD` printed `76e9c28`, so the plugin files loaded by `--plugin-dir "$P"` are those of 76e9c28 for the whole run. `git diff 5e13529 76e9c28 -- plugins/experiment-proposal/skills/design/SKILL.md` shows the three step edits of ed96208 (step 1 the draft path default, step 2 `weak` redefined, step 3 the frontier list, the settled-stays-settled sentence and the per-round checker).
- The scratch project did not exist beforehand: `mkdir "$S"` succeeded, so no other run's directory was reused.

## Commands

`$P` is `<checkout>/plugins/experiment-proposal`; `$S` is `/tmp/ep-eval/from-scratch-v2-6`, created with `mkdir "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval && git commit --allow-empty -qm init` (one empty commit `bdad94a init`; no fixtures: the scenario gives only the idea). The helper `bash /tmp/ep-eval/review-v2-drive.sh "$S" <turn>` runs, with `prompt` read from `$S.turn<N>.prompt`:

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
cd "$S" && python3 "$P/scripts/check_proposal.py" brief proposal/design-brief.md > chk.out 2> chk.err; echo "exit=$?"
```

Between turns the brief was copied to a snapshot file outside the repository (`/tmp/ep-eval/from-scratch-v2-6.snaps/after<N>.md`), and the Write contents of turns 1 to 4 were extracted from the jsonl, to compare settled entries across the run.

## Turns

| Turn | Sent                                                                                          | Came back                                                                                                                                                                                                                                                              | Wall time |
| ---- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 1    | `/experiment-proposal:design` with the idea                                                   | "Draft path: `proposal/draft.md` (default; none named)"; extraction table, 21 rows, 5 weak (1.1, 6.1, 7.1, 7.6, 8.3) and 16 missing, "Nothing settled"; open brief written (header, Looked up, no entries); checker clean; "Round 1 — frontier: item 1.1", Q1 item 1.1 | 66 s      |
| 2    | Q1 item 1.1 from the sheet                                                                    | 1.1 settled and written; checker clean; "Round 2 — frontier: items 1.2, 1.3, 6.1, 7.1, 7.6", Q1 to Q5 in that order                                                                                                                                                    | 84 s      |
| 3    | Items 1.2, 1.3, 6.1, 7.1, 7.6 from the sheet                                                  | Those five written (6 entries), checker clean; then three hci-researcher calls (7.2, 7.7, 7.9); "Round 3 — frontier: items 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9", Q1 to Q7                                                                                                | 301 s     |
| 4    | Items 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9 from the sheet                                        | All seven settled and written (13 entries), checker clean; "Round 4 — frontier: items 7.3, 7.5, 8.3", Q1 to Q3                                                                                                                                                         | 111 s     |
| 5    | 7.3 yes; 7.5 sheet row; 8.3 sheet row plus "Item 1.3 stays as I gave it"                      | 7.3, 7.5, 8.3 settled and written (16 entries), checker clean; "Round 5 — frontier: items 2.2, 8.5", Q1 and Q2                                                                                                                                                         | 61 s      |
| 6    | 2.2 sheet row; 8.5 sheet row                                                                  | 2.2 pilot settles, 8.5 settled, written (18 entries), checker clean; "Round 6 — frontier: item 2.3", Q1                                                                                                                                                                | 38 s      |
| 7    | 2.3 sheet row                                                                                 | 2.3 settled and written (19 entries), checker clean; "Round 7 — frontier: item 2.4", Q1                                                                                                                                                                                | 28 s      |
| 8    | 2.4 "I don't know yet"                                                                        | 2.4 provisional written in the same turn (20 entries), Open items rebuilt, checker clean; "Round 8 — frontier: item 2.5, the last open item", Q1                                                                                                                       | 47 s      |
| 9    | 2.5 sheet row                                                                                 | 2.5 settled written (21 entries), Open items gain the ethics-board command, checker clean, a count of headings; "All 21 design-tree items have entries; frontier empty. Checker exits 0."; asks for approval                                                           | 34 s      |
| 10   | "On the term's end date for item 2.4: I don't know yet. Yes, I approve the brief. Freeze it." | `Status: frozen 2026-10-15`, checker clean, `git add proposal/design-brief.md && git commit -m "Freeze the design brief" -- proposal/design-brief.md` ran: `[master b33ea75] Freeze the design brief`                                                                  | 19 s      |

Turn texts, verbatim (the files `$S.turn<N>.prompt`):

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
Q1 (item 1.2): The university IRB; minimal-risk expedited review, about three weeks; a consent form and the phrase set are required.
Q2 (item 1.3): Keystroke logs and phrase times only, no names linked, no recordings; the two experimenters have access; raw data kept five years, then deleted.
Q3 (item 6.1): H1 directional (swipe faster); H2 "no worse" on errors; RQ1 on the ease rating (unsure of direction).
Q4 (item 7.1): Keyboard: the phone's built-in tap keyboard versus its swipe mode; within subjects because typing skill varies hugely between people.
Q5 (item 7.6): Words per minute (characters over five over minutes, app-logged, ratio); uncorrected error rate (MSD over length, app-logged, ratio) and a per-phrase indicator of any uncorrected error (binary), which H2 uses; ease rating 1 to 7 after each keyboard (ordinal, questionnaire). Yes to the recommended reliability and construct-validity statements.
```

Turn 4:

```text
Q1 (item 6.2): Yes to the recommendation. Sources: the two swipe-keyboard studies I "will add from lit-search"; accept the direction as settled, with lit-search listed under Open items.
Q2 (item 6.5): No interaction idea.
Q3 (item 7.2): Symmetric: each keyboard is minutes of practice from the other.
Q4 (item 7.4): No between-subjects variable.
Q5 (item 7.7): Right-handed, 18 to 35, owns a smartphone, never used swipe; same phone, app, phrases, room, script; yes to the recommended validity trade-off wording.
Q6 (item 7.8): Typing skill, mood, time of day, phrase order.
Q7 (item 7.9): History: run all sessions within three weeks; maturation: one 40-minute session; instrumentation: freeze the app before the first participant.
```

Turn 5:

```text
Q1 (item 7.3): Yes: a one-factor, two-level within-subjects design.
Q2 (item 7.5): Counterbalance keyboard order, AB and BA, half each, assigned from a shuffled list; the same phrase set for both keyboards, in a fresh random order per keyboard.
Q3 (item 8.3): The four criteria (right-handed, 18 to 35, owns a smartphone, never used swipe), screened by a sign-up form; none selects on typing speed. Item 1.3 stays as I gave it.
```

Turn 6:

```text
Q1 (item 2.2): The pilot will decide the phrases per keyboard; 20 is the working value; two conditions, about 40 minutes.
Q2 (item 8.5): 16: the two swipe-keyboard studies lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 at one session each, and 16 is a multiple of the two orders; pre-specified; the pilot refines the phrases per keyboard, not the count.
```

Turn 7:

```text
Q1 (item 2.3): Four people from the lab; it refines the phrases per keyboard (recorded under 2.2) and the script timings; its data will not be reported.
```

Turn 8:

```text
Q1 (item 2.4): I don't know yet.
```

Turn 9:

```text
Q1 (item 2.5): Too few sign-ups: extend recruiting to a second course; a keyboard app failing in the pilot: freeze a fallback build.
```

Turn 10:

```text
On the term's end date for item 2.4: I don't know yet. Yes, I approve the brief. Freeze it.
```

Driver choices that go beyond copying a sheet row, so a reader can judge them: (a) there was no draft-path question this time (the fix defaults it), so no "Q0" answer was needed; (b) turn 3's item 6.2 answer is the sheet's "Yes to the recommendation" row; the 6.2 recommendation was the hci-researcher's non-inferiority restatement of H2 with a 5-point margin, so that "yes" accepted it; (c) turn 5's "Item 1.3 stays as I gave it" answers round 4 Q3's offer to amend item 1.3 and is the sheet's own answer for 1.3, not an "I don't know"; (d) turn 10's "On the term's end date for item 2.4: I don't know yet" answers turn 9's closing offer ("Or name the term's end date first") with the sheet's own 2.4 answer; (e) where a recommendation differed from a sheet row (round 4 Q2 proposed disjoint phrase subsets per block, Q3 proposed a fifth criterion, English fluency; round 5 Q2 proposed 24 participants), the sheet row was sent verbatim and the recommendation was not accepted.

## Transcript, decisive lines

- Turn 1 opening: "No material files in repo — the material is your prompt. Draft path: `proposal/draft.md` (default; none named)." The extraction table ends "Nothing settled, so the brief opens with no entries." The first checker call ended `; echo "exit=$?"` and was refused by the `Bash(python3:*)` allow-list ("This Bash command contains multiple operations. The following part requires approval: echo "exit=$?""); the retry without it succeeded with no output. A `cd` into the plugin directory was also blocked ("Claude Code may only change directories to the allowed working directories for this session"); the session then used Read for the plugin files.
- Frontier line, every round, above Q1: "**Round 1 — frontier: item 1.1**", "**Round 2 — frontier: items 1.2, 1.3, 6.1, 7.1, 7.6**", "**Round 3 — frontier: items 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9**", "**Round 4 — frontier: items 7.3, 7.5, 8.3**", "**Round 5 — frontier: items 2.2, 8.5**", "**Round 6 — frontier: item 2.3**", "**Round 7 — frontier: item 2.4**", "**Round 8 — frontier: item 2.5, the last open item**". Each round's frontier matches the checklist's design-tree dependencies (6.2 and 6.5 wait on 6.1; 7.2, 7.4, 7.7, 7.8 and 7.9 on 7.1; 7.3 on 6.5; 7.5 on 7.2; 8.3 on 7.7; 2.2 and 8.5 on 7.3 and 7.6; 2.3, 2.4, 2.5 in a chain).
- Turn 2 to turn 4: items 7.7 and 7.9 were each asked once, in round 3 (Q5, Q7), and written `settled` from the sheet row in turn 4 with no follow-up round. Turn 4's closing text opens round 4 with only items 7.3, 7.5 and 8.3.
- Turn 3 (after writing the brief and running the checker): three `Agent` calls, `subagent_type` `experiment-proposal:hci-researcher`, descriptions "Carry-over symmetry question" (item 7.2), "Control variables question" (item 7.7), "Confounds and validity threats" (item 7.9). Round 3's recommendations are labelled "Recommended (hci-researcher)" for items 6.2, 7.2, 7.7 and 7.9.
- Turn 4, round 4 Q2 (item 7.5): "Recommended (hci-researcher): "balanced randomized assignment to the two orders, n a multiple of 2, half tap-first; order as a fixed effect in the model and the order × method interaction reported as an asymmetric-transfer diagnostic"". No call was made for 7.5; the quoted string is in the item-7.9 subagent answer ("**Prevention (settles item 7.5):** balanced randomized assignment to the two orders, n a multiple of 2, half tap-first; order as a fixed effect...").
- Turn 4, round 4 Q3 (item 8.3), the one numbered question that names a settled item: "One consequence to decide with it: item 1.3's data plan says "keystroke logs and phrase times only". ... If you want prior exposure or platform kept as a covariate for the analysis, item 1.3 needs an amendment naming it — say so and I will note it for the amendment step rather than editing the entry." Answered in turn 5 "Item 1.3 stays as I gave it." The 8.3 entry records "so item 1.3 stands as given"; the 1.3 entry is unchanged.
- Turn 5, round 5 Q2 (item 8.5) asked for the similar experiments and the reason ("which similar experiments do you know, and what sets your count — those studies' numbers, a resource limit ..., or a convention of the field?"), recommending 24 if they could not name them. The sheet row supplied both; the entry quotes it whole.
- Turn 8: "2.4 provisional" was written in the same turn as the answer: the Edit added the `### 2.4 Timeline` entry (`Status: provisional`), a Looked up line and Open items line 1, and the checker ran clean. Turn 9 likewise wrote 2.5 at once.
- Turn 9 closing text: "All 21 design-tree items have entries; frontier empty. Checker exits 0." then "**Three places where your decision overrode the recommendation**, recorded as yours and left as-is" (items 7.2, 7.5, 7.9), and "Approve and I will set `Status: frozen 2026-10-15` and commit it. Or name the term's end date first, which would settle 2.4".
- Turn 10: the Bash call `git add proposal/design-brief.md && git commit -m "Freeze the design brief" -- proposal/design-brief.md` returned `[master b33ea75] Freeze the design brief` / `1 file changed, 172 insertions(+)` / `create mode 100644 proposal/design-brief.md` with `is_error` false; the result line shows `permission_denials` empty. Closing text: "Frozen and committed: `b33ea75`, `proposal/design-brief.md`, checker exits 0." and "Item 2.4 stays `provisional` ... it is the first line under Open items."

## Brief status per item (final state, checklist order)

Final header, as committed:

```text
Draft: proposal/draft.md
Status: frozen 2026-10-15
Checklist: experiment-proposal 0.2.0
```

| Item | Name                                     | Status        | Round | Note                                                                                                                                                                         |
| ---- | ---------------------------------------- | ------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1  | Research question                        | settled       | 1     | Sheet row, quoted                                                                                                                                                            |
| 1.2  | Ethics route                             | settled       | 2     | Sheet row, quoted                                                                                                                                                            |
| 1.3  | Data plan                                | settled       | 2     | Sheet row, quoted; named by round 4 Q3's amendment offer, entry unchanged                                                                                                    |
| 2.2  | Conditions, trials and session length    | pilot settles | 5     | Sheet row quoted; the Decision says the pilot times a full session at 20 phrases; adds "5 unscored practice phrases precede each block" (the skill's)                        |
| 2.3  | Pilot plan                               | settled       | 6     | Four people from the lab; refines the phrases per keyboard and the script timings; data not reported                                                                         |
| 2.4  | Timeline                                 | provisional   | 7     | "I don't know yet"; dates stand in; Open items 1; Rationale reads "accepted recommendation:" though the answer was not a bare yes                                            |
| 2.5  | Expected challenges and responses        | settled       | 8     | Two challenges, two responses, the sheet's, each with its section named                                                                                                      |
| 6.1  | Hypotheses and research question         | settled       | 2     | H1 directional, H2 "no worse", RQ1                                                                                                                                           |
| 6.2  | Hypothesis variables, direction and null | settled       | 3     | "Yes to the recommendation": H2 non-inferiority with a 5-point margin, H1 primary, Holm; sources "will add from lit-search" quoted; lit-search in Open items 2               |
| 6.5  | Interaction hypotheses                   | settled       | 3     | None; the Decision adds two diagnostics (order by method, prior exposure by method), the skill's                                                                             |
| 7.1  | Independent variable                     | settled       | 2     | Built-in keyboard, tap versus swipe mode, within subjects                                                                                                                    |
| 7.2  | Carry-over symmetry                      | settled       | 3     | Symmetric, the sheet's reason; the subagent had called it "not symmetric, but tolerable"; the entry follows the sheet and adds a practice block (the skill's)                |
| 7.3  | The design, named                        | settled       | 4     | One-factor, two-level within-subjects                                                                                                                                        |
| 7.4  | Random assignment                        | settled       | 3     | No between-subjects variable                                                                                                                                                 |
| 7.5  | Counterbalancing                         | settled       | 4     | AB and BA, shuffled list, the same phrase set in a fresh random order per keyboard; no disjoint subsets; adds "order enters the analysis as a fixed effect" (the subagent's) |
| 7.6  | Dependent variables                      | settled       | 2     | WPM, uncorrected error rate and binary indicator, ease rating; speed and accuracy reported together                                                                          |
| 7.7  | Control variables                        | settled       | 3     | Sheet row plus the validity wording; adds "Not imposed: a forced grip, autocorrect off, per-phrase time limits" (the skill's)                                                |
| 7.8  | Random variables                         | settled       | 3     | Typing skill, mood, time of day, phrase order; adds "crossed random effects" (the skill's)                                                                                   |
| 7.9  | Confounds and their prevention           | settled       | 3     | History, maturation, instrumentation from the sheet; adds "Prior swipe use is prevented by the item 7.7 screen" (the skill's)                                                |
| 8.3  | Eligibility and screening                | settled       | 4     | Four criteria, sign-up form, none selects on typing speed; adds "or glide typing"                                                                                            |
| 8.5  | Participant count                        | settled       | 5     | 16, 8 per order, pre-specified; Rationale quotes the whole sheet row                                                                                                         |

Totals: 19 settled, 1 pilot settles, 1 provisional, 21 entries, in checklist order. Entry counts by turn: 0, 1, 6, 13, 16, 18, 19, 20, 21, 21.

Open items, as committed:

```text
1. Item 2.4 provisional, recommendation: IRB filed by 2026-10-22 and approval expected 2026-11-12, app built and verified then frozen by 2026-11-11, pilot 2026-11-13 to 2026-11-18, 16 sessions 2026-11-19 to 2026-12-05, analysis 2026-12-08 to 2026-12-12, write-up 2026-12-15 to 2026-12-19; confirm against the term's real end date.
2. Run `/experiment-proposal:lit-search` for the two swipe-keyboard studies that justify H1's direction in novices, for the error-rate comparison H2's margin rests on, and for the participant counts of similar text-entry experiments.
3. Run `/experiment-proposal:the-ethics-board` to turn items 1.2, 1.3 and 12.3 into the consent story: the IRB's expedited route, the code-only keystroke logs with five-year retention, and the 40-minute session the consent form must state.
```

Item 8.5 entry, as committed:

```text
### 8.5 Participant count
- Decision: 16 participants, pre-specified: the two swipe-keyboard studies the lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 sessions at one session each, and 16 is a multiple of the two counterbalanced orders, 8 per order. The pilot refines the phrases per keyboard, not the count.
- Rationale: "16: the two swipe-keyboard studies lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 at one session each, and 16 is a multiple of the two orders; pre-specified; the pilot refines the phrases per keyboard, not the count."
- Would change if: the lit-search found the comparable studies ran well above 20, which would raise the count to the next even number the term allows.
- Status: settled
- Source: user, round 5
```

## Pass bar

| Criterion                                                                                                                  | Result                              | Evidence                                                                                                                                                                                                                                                                                                                                             |
| -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Every design-tree item (21) has an entry that is settled, provisional or pilot settles; 2.4 provisional; 2.2 pilot settles | PASS                                | The 21 `### ` headings of the committed brief equal, in order, the 21 checklist items whose scope reads `design-tree` (1.1, 1.2, 1.3, 2.2, 2.3, 2.4, 2.5, 6.1, 6.2, 6.5, 7.1 to 7.9, 8.3, 8.5), compared by script; 19 settled, 1 pilot settles (2.2), 1 provisional (2.4). `Status: provisional` under 2.4 and `Status: pilot settles` under 2.2.   |
| 8.5 justified from the sheet (a provisional 8.5 also meets the bar)                                                        | PASS                                | 8.5 is settled; its Rationale quotes the sheet row whole: the studies' 12 to 20, the course term allowing 16 at one session each, a multiple of the two orders, pre-specified, the pilot refining the phrases per keyboard and not the count. The Decision says 16, 8 per order, pre-specified. Open items 2 sends lit-search to confirm the counts. |
| At least one hci-researcher subagent call across all turns                                                                 | PASS                                | 3 `Agent` tool_use entries with `subagent_type` `experiment-proposal:hci-researcher`, all in turn 3 (items 7.2, 7.7, 7.9); turns 1, 2 and 4 to 10: 0. None of the three results has `is_error` set. Item 7.5, which step 4 names, had no call of its own; see Observations.                                                                          |
| Checker exits 0 on the frozen brief                                                                                        | PASS                                | `cd "$S" && python3 "$P/scripts/check_proposal.py" brief proposal/design-brief.md`: stdout empty (0 bytes), stderr empty (0 bytes), exit code 0. The brief at that moment had `Status: frozen 2026-10-15` and was the committed file (`git status --porcelain` empty).                                                                               |
| The freeze commit exists                                                                                                   | PASS                                | `git -C "$S" log --oneline` printed `b33ea75 Freeze the design brief` and `bdad94a init`; `git show --stat` shows one file, `proposal/design-brief.md`, 172 insertions; `git status --porcelain` is empty.                                                                                                                                           |
| Record: did the freeze's git add and git commit run or get refused                                                         | RAN                                 | The turn-10 Bash call returned `[master b33ea75] Freeze the design brief` with `is_error` false and `permission_denials` empty; the checker had been re-run with exit 0 first (a Bash call with no output, turn 10), after the Edit that set `Status: frozen 2026-10-15`.                                                                            |
| Record: settled items asked again                                                                                          | 1 named, 0 changed                  | See Diagnostics.                                                                                                                                                                                                                                                                                                                                     |
| Record: settled entries edited without a question                                                                          | 0                                   | See Diagnostics.                                                                                                                                                                                                                                                                                                                                     |
| Record: frontier IDs listed above Q1 each round                                                                            | 8 of 8                              | See the frontier lines under Transcript.                                                                                                                                                                                                                                                                                                             |
| Record: checker ran each round                                                                                             | 10 of 10 turns that wrote the brief | See Diagnostics.                                                                                                                                                                                                                                                                                                                                     |

## Diagnostics

### Settled items asked again, and settled entries edited

An item counts when a numbered question named it, or its entry changed after it was settled.

Method for edits: the final brief's entries were compared, by heading block, with the first version of each entry. The brief as it stood after turns 1 to 3 was rebuilt from the Write contents in the jsonl (turn 1 no entries, turn 2 one, turn 3 six), after turn 4 from a snapshot of the file (turn 4's Edit was overwritten by its Write), and after turns 5 to 10 from snapshots. Every entry present in an earlier version is byte-identical in every later version, through the committed one: 0 settled entries changed text. The only changes to existing text were added entries, added Looked up lines, rebuilt Open items lines, and `Status: open` to `Status: frozen 2026-10-15`. The same comparison shows 0 entries edited without a question.

Method for questions: every numbered question of each round was scanned for item IDs other than its own that were already settled at that point, then each hit was read and classified.

- Asked: round 4 Q3 (item 8.3) names settled item 1.3 and offers its amendment: "item 1.3 needs an amendment naming it — say so and I will note it for the amendment step rather than editing the entry." The offer is conditional and routed to the amendment step, not an edit; the answer in turn 5 was "Item 1.3 stays as I gave it", and the 1.3 entry is unchanged. This is the one settled item named by a question that offers a change: 1 item.
- Concern in a Why-this-matters line, no change offered: round 4 Q2 (item 7.5) "the two preventions your item 7.9 answer did not cover — phrase reuse between blocks and the experimenter framing one keyboard as the new one"; round 6 Q1 (item 2.3) "item 7.9's instrumentation prevention ... only works if something tested the app before the freeze". Neither asked for a change to 7.9; its entry is unchanged.
- Concern in a recommendation's basis (the placement the fixed step 3 prescribes): round 5 Q1 (item 2.2) "One note for the pilot, from your item 7.5 choice" (the shared phrase set gives block 2 a reading advantage); round 7 Q1 (item 2.4) "item 7.9's prevention needs this check to happen before the freeze, and your item 2.3 pilot does not cover it"; round 8 Q1 (item 2.5) "Your item 7.9 answer freezes the app before the first participant, and your item 2.3 pilot does not test the logging, so the check sits in the timeline instead".
- Dependency citations, not questions: round 4 Q1 cites 6.5, Q2 cites 7.4, Q3 cites 7.7; round 5 Q1 cites 7.9 for the 40 minutes; round 6 Q1 cites 8.3 and 2.2; round 7 Q1 cites 1.2, 2.2 and 7.9; round 8 Q1 cites 2.2, 2.3 and 7.1.
- Flagged after the last question, not asked: turn 9's closing text lists "Three places where your decision overrode the recommendation" (7.2, 7.5, 7.9: "demand characteristics, the ordinal ease rating and phrase reuse are not prevented anywhere in the brief"), "recorded as yours and left as-is". No question was put and no entry changed.
- Never written settled, asked twice: none. Items 7.7 and 7.9 were each put once (round 3) and settled from the sheet row.

### Frontier IDs listed above Q1

Yes, every question round. Rounds 1 to 8 each open with a bold "Round N — frontier: ..." line above Q1 (quoted under Transcript). Turn 9, which asks no question, says "frontier empty".

### Checker each round

The checker ran in every turn that wrote the brief (turns 1 to 10: nine rounds and the freeze), after the write: turn 1 one clean run (preceded by one refused call, `; echo "exit=$?"` rejected by the allow-list, and one blocked `cd` call whose command also named the checker file), turns 2 to 10 one clean run each (turn 9 also grepped the headings, turn 10 ran it after setting the frozen header). Every successful run printed nothing (exit 0). The checker caught no defect in this run: v2-1's one failure (a 412-character Decision) did not recur; the longest Decision line here is 360 characters, under the checker's 400. In turn 3 the brief was written and checked before the three subagent calls and not rewritten after them; the round-3 answers were written in turn 4.

### Freeze

The freeze's `git add && git commit` ran and was not refused (see the pass-bar row).

## Observations beyond the bar

Against v2-1's four behaviours:

1. Partial answers hold an item open: not reproduced. The sheet answered 7.7 and 7.9 in round 3 and both were written `settled` from that row in turn 4; there was no grip question and no "four further confounds" question.
2. Settled items put back to the user: reduced, not gone. v2-1 asked 1.1, 1.3 and 2.5 again (3 items, none changed); v2-6 names one (1.3, round 4 Q3's conditional amendment offer, which the fixed step 3 sentence "never into a question" does not prevent), and the unnumbered pre-freeze offer on 2.5 is absent. Concerns about settled 7.9, 7.5 and 2.3 appear in Why-this-matters lines and recommendation bases, and in turn 9's closing flag.
3. Skill wording under the user's name: still present. Entries whose `Source: user` Decision carries words the user did not say: 2.2 "5 unscored practice phrases precede each block", 6.5 the two diagnostics, 7.2 "A practice block precedes each condition and its trials are excluded from analysis", 7.5 "Order enters the analysis as a fixed effect and the order-by-method interaction is reported", 7.7 "Not imposed: a forced grip, autocorrect off, per-phrase time limits", 7.8 "Participant and phrase enter the analysis as crossed random effects", 7.9 "Prior swipe use is prevented by the item 7.7 screen", 8.3 "or glide typing". The Rationale lines quote the sheet; the Decision lines mix in the skill's and the subagent's additions.
4. The brief lags the answers by a turn: not reproduced. Every answer was written in the turn that received it, including 2.4 (turn 8) and 2.5 (turn 9), and every turn that wrote the brief also ran the checker.

New observations:

- Item 7.5 had no dedicated hci-researcher call, though step 4 names it. Round 4's `Recommended (hci-researcher)` for 7.5 quotes a sentence from the item-7.9 call's answer, which settled the order question as a side effect. The bar (at least one call) holds either way.
- The subagents ran tools: two of the three calls made Glob and Read calls on the scratch project, reading `$S/proposal/design-brief.md` (read-only; step 4 says the subagent "runs nothing"). The 7.9 subagent's answer also says its own advisor call was rate-limited, so that answer is "my own assessment".
- Turn 3 sequence: the brief was written and checked first, then the three subagent calls, then the round-3 questions, so the subagent answers reached the user only as recommendations in the same turn; no answer was lost.
- The 2.4 Rationale reads `accepted recommendation: the term's end date is unknown, ...` for a provisional entry whose answer was "I don't know yet", not a bare yes; `references/brief.md` reserves that form for a bare "yes".
- Turn 1 made no `Q0` draft-path question: it said which path it used, as the fixed step 1 requires.

## `git log --oneline` in the scratch project

```text
b33ea75 Freeze the design brief
bdad94a init
```
