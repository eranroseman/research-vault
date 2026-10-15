# Scenario 3 (design from scratch) at 0.2.0, run v2-2

Date: 2026-10-15
Plugin commit: 5e13529 (`experiment-proposal` 0.2.0)
Fixture: `fixtures/from-scratch-answers.md`; no material file. Scratch project `S=/tmp/ep-eval/from-scratch-v2-2` (a repository whose only commit is the empty `init`; `proposal/` did not exist, the session created it).
Model: `--model opus`, which the init event of every turn reports as `claude-opus-5`.

Verdict: PASS. All five bar criteria hold (21 of 21 design-tree items have an entry, 2.4 provisional, 2.2 pilot settles, 8.5 justified from the sheet; 4 `hci-researcher` calls; the checker exits 0 on the frozen brief; the freeze commit `c064037` exists). The freeze's `git add && git commit` ran and was not refused. No numbered question named an already settled item; two unnumbered flags did, and one of them changed an entry (7.9, settled to provisional).

## Harness event: rate-limit interruption and resumption

A first driver ran turns 1 to 4 of this run (judging by the one-line "no stdin data received in 3s" warning in the `.err` files of turns 2 to 4, through `/tmp/ep-eval/drive-v2.sh`, which has the same flags as below but no `< /dev/null`) and was killed by the account's session rate limit after turn 4. Turn 4 itself completed normally (rc 0, 114 s, a normal final text; its result event has `is_error` false and no `api_error_status`). The rate-limit events inside turns 1 to 4 were `allowed_warning` (five-hour window utilization 0.92 to 0.99 in the last events). This record's resumption ran turns 5 to 9 through `/tmp/ep-eval/review-v2-drive.sh` (same flags, `--continue`, stdin from `/dev/null`), reading turn 4's final text first and continuing from the question it had asked. In turns 5 to 9 every result event has `is_error` false, `api_error_status` null and `subtype` `success`; the rate-limit events read `allowed` at utilization 0.01 to 0.02; no turn showed a 429 or "session limit", and no turn was retried. The session itself was continuous (`--continue` resumed the project's most recent session in `$S`), so the interruption cost the run no state; the brief on disk after turn 4 was byte-identical to the replay of turns 1 to 4's Write and Edit calls.

## Commands

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/from-scratch-v2-2
# turn 1 (the prompt is read from "$S.turn1.prompt")
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn1.jsonl" 2> "$S.turn1.err"
# turns 2 to 9: the same command with --continue before the prompt, prompt read from "$S.turn<N>.prompt"
cd "$S" && timeout 1800 claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn<N>.jsonl" 2> "$S.turn<N>.err"
```

The raw stream-json output is kept outside the repository as `$S.turn<N>.jsonl`.

## Turns (one line each)

| Turn | By              | Wall  | Agent calls | What the skill did                                                                                                                                                                                                                                                       | What was sent                                                                                       |
| ---- | --------------- | ----- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| 1    | first driver    | 211 s | 0           | Read the checklist, `brief.md` and `plugin.json`; extracted 21 design-tree items (1.1 settled, the other 20 weak or missing); wrote the open brief, checker clean; assumed the draft path; asked round 1 (1.2, 1.3, 6.1, 7.1, 7.6)                                       | the idea line, `/experiment-proposal:design ...`                                                    |
| 2    | first driver    | 258 s | 3           | Recorded round 1 (5 entries); pushed back on H2 "no worse" as untestable; consulted `hci-researcher` for 7.2, 7.7, 7.9; asked round 2 (6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9)                                                                                                | sheet answers for 1.2, 1.3, 6.1, 7.1, 7.6                                                           |
| 3    | first driver    | 227 s | 1           | Recorded round 2 (7 entries); flagged that the 7.2 reason covers motor practice only and that 7.7 and 7.9 were narrower than recommended; consulted `hci-researcher` for 7.5; asked round 3 (7.3, 7.5, 8.3) plus an unnumbered flag on settled 7.9 (between-block reset) | sheet answers for 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9                                                 |
| 4    | first driver    | 114 s | 0           | Recorded round 3 (7.3, 7.5, 8.3); 7.9 became provisional; fixed two checker length and order complaints; asked round 4 (2.2, 8.5): "Dependency chain leaves two questions now, then items 2.3, 2.4, 2.5 one at a time"                                                   | sheet answers for 7.3, 7.5, 8.3, "Keep item 1.1 as I worded it", and "I don't know" to the 7.9 flag |
| 5    | this resumption | 46 s  | 0           | Wrote 2.2 (`pilot settles`) and 8.5 (`settled`); checker clean, 16 entries; asked round 5 (2.3)                                                                                                                                                                          | sheet answers for 2.2 and 8.5                                                                       |
| 6    | this resumption | 31 s  | 0           | Wrote 2.3 (`settled`); checker clean, 17 entries; asked round 6 (2.4) plus an unnumbered flag on settled 2.3 (lab members may have swiped)                                                                                                                               | sheet answer for 2.3                                                                                |
| 7    | this resumption | 44 s  | 0           | Wrote 2.4 (`provisional`) and Open item 1; "Item 2.3 stands as you worded it"; checker clean, 18 entries; asked round 7 (2.5)                                                                                                                                            | "I don't know yet" for 2.4; "stand" for the 2.3 flag                                                |
| 8    | this resumption | 41 s  | 0           | Wrote 2.5 (`settled`) and the-ethics-board Open item; checker clean; "Brief ready" with 21 entries; asked "Freeze it?"                                                                                                                                                   | sheet answer for 2.5                                                                                |
| 9    | this resumption | 17 s  | 0           | Set `Status: frozen 2026-10-15`, ran the checker (clean), ran `git add proposal/design-brief.md && git commit -m "Freeze the design brief" -- proposal/design-brief.md`: commit `c064037`                                                                                | approval of the brief and the freeze                                                                |

Total: 9 turns, 8 rounds of questions (round 1 to round 7, then the freeze question), 4 `hci-researcher` calls.

Turn texts, verbatim.

Turn 1:

```text
/experiment-proposal:design Novice smartphone users entering text: does a swipe keyboard beat tap typing? Within subjects, two keyboards, phrases from a standard set, speed and errors logged, plus a 1 to 7 ease rating after each keyboard.
```

Turn 2:

```text
Item 1.2 (Q1): The university IRB; minimal-risk expedited review, about three weeks; a consent form and the phrase set are required.
Item 1.3 (Q2): Keystroke logs and phrase times only, no names linked, no recordings; the two experimenters have access; raw data kept five years, then deleted.
Item 6.1 (Q3): H1 directional (swipe faster); H2 "no worse" on errors; RQ1 on the ease rating (unsure of direction).
Item 7.1 (Q4): Keyboard: the phone's built-in tap keyboard versus its swipe mode; within subjects because typing skill varies hugely between people.
Item 7.6 (Q5): Words per minute (characters over five over minutes, app-logged, ratio); uncorrected error rate (MSD over length, app-logged, ratio) and a per-phrase indicator of any uncorrected error (binary), which H2 uses; ease rating 1 to 7 after each keyboard (ordinal, questionnaire). Yes to the recommended reliability and construct-validity statements.
```

Turn 3:

```text
Item 6.2 (Q1): Yes to the recommendation. Sources: the two swipe-keyboard studies I "will add from lit-search"; accept the direction as settled, with lit-search listed under Open items.
Item 6.5 (Q2): No interaction idea.
Item 7.2 (Q3): Symmetric: each keyboard is minutes of practice from the other.
Item 7.4 (Q4): No between-subjects variable.
Item 7.7 (Q5): Right-handed, 18 to 35, owns a smartphone, never used swipe; same phone, app, phrases, room, script; yes to the recommended validity trade-off wording.
Item 7.8 (Q6): Typing skill, mood, time of day, phrase order.
Item 7.9 (Q7): History: run all sessions within three weeks; maturation: one 40-minute session; instrumentation: freeze the app before the first participant.
```

Turn 4:

```text
Item 7.3 (Q1): Yes: a one-factor, two-level within-subjects design.
Item 7.5 (Q2): Counterbalance keyboard order, AB and BA, half each, assigned from a shuffled list; the same phrase set for both keyboards, in a fresh random order per keyboard.
Item 8.3 (Q3): The four criteria (right-handed, 18 to 35, owns a smartphone, never used swipe), screened by a sign-up form; none selects on typing speed. Keep item 1.1 as I worded it.
Flag on item 7.9 (between-block reset): I don't know.
```

Turn 5:

```text
Item 2.2 (Q1): The pilot will decide the phrases per keyboard; 20 is the working value; two conditions, about 40 minutes.
Item 8.5 (Q2): 16: the two swipe-keyboard studies lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 at one session each, and 16 is a multiple of the two orders; pre-specified; the pilot refines the phrases per keyboard, not the count.
```

Turn 6:

```text
Item 2.3 (Q1): Four people from the lab; it refines the phrases per keyboard (recorded under 2.2) and the script timings; its data will not be reported.
```

Turn 7:

```text
Item 2.4 (Q1): I don't know yet.
Flag on item 2.3 (the pilot sample): stand; the pilot is four people from the lab, as I said.
```

Turn 8:

```text
Item 2.5 (Q1): Too few sign-ups: extend recruiting to a second course; a keyboard app failing in the pilot: freeze a fallback build.
```

Turn 9:

```text
Yes, I approve the brief. Freeze it now, with 2.4 still provisional.
```

How the sheet was applied where the skill's question went beyond it: the skill extracted 1.1 as settled from the command line and never asked it, so the sheet's 1.1 wording was never offered (the brief's 1.1 reads "change text-entry speed and error rate", the sheet's reads "change words per minute"). The 7.9 between-block-reset flag (turn 3) is not answered by the sheet's 7.9 row, so the answer was "I don't know". The 2.3 pilot-sample flag (turn 6) is answered by the sheet's 2.3 row (four people from the lab), so this resumption sent "stand", not "I don't know"; the two flags therefore got different answers for a stated reason. For 2.4's term-end question the sheet has no answer and "I don't know yet" covered it. For 2.5 the skill recommended seven challenges; only the sheet's two were sent.

## Decisive transcript lines

Turn 1 (extraction, draft path):

```text
Repo exists. No material files — only the command line. Extraction against the 21 design-tree items:
| 1.1 research question | settled | "does a swipe keyboard beat tap typing?" + "Novice smartphone users entering text" + ... (command arguments) |
Checker exits 0 on the open brief. Brief written: `proposal/design-brief.md`.
**Draft path:** header assumes `proposal/draft.md`. Say so if you want another.
## Round 1 — five questions
```

Turn 2 and 3 (subagent calls; the `description` fields of the Agent calls named `experiment-proposal:hci-researcher`):

```text
turn 2: "Carry-over symmetry question", "Control variables question", "Confounds and validity threats"
turn 3: "Counterbalancing scheme"
Q3. Item 7.2 ... Recommended (hci-researcher): "keep Keyboard within subjects; treat carry-over as mildly asymmetric and absorb it by design ..."
```

Turn 3 (the unnumbered flag on a settled item, and the answer that changed it):

```text
**Flag, item 7.9 — the one omission that counterbalancing cannot repair.** Not a frontier question; your 7.9 entry is settled. ... Want it added to the 7.9 entry? "Add it", "leave it", or "leave it and note it as a limitation" all work.
```

Turn 4 (the dependency chain):

```text
Checker clean, 14 entries. Dependency chain leaves two questions now, then items 2.3, 2.4, 2.5 one at a time (each depends on the one before).
```

Turn 5 (8.5 as written, 2.2 as written):

```text
### 2.2 Conditions, trials and session length
- Decision: Two conditions, one per keyboard. The pilot sets the number of phrases per keyboard by timing how long a block of phrases actually takes a novice ... 20 phrases per keyboard is the working value. The session runs about 40 minutes ...
- Status: pilot settles
### 8.5 Participant count
- Decision: 16 participants, 8 per order, pre-specified. The pilot refines the phrases per keyboard, not the count.
- Would change if: the studies the literature search returns used counts outside 12 to 20, which would undercut the stated reason.
- Status: settled
```

Turn 6 (the unnumbered flag on settled 2.3):

```text
**Flag, item 2.3 — the pilot sample.** Recorded as you decided it, but worth one sentence: lab members are likely to have used swipe typing ... Say "adjust" and I will amend the 2.3 entry, or "stand" and I will leave it.
```

Turn 7: `Checker clean, 18 entries. Item 2.3 stands as you worded it. One item left.`

Turn 8:

```text
Brief complete: all 21 design-tree items, 19 settled, 1 `pilot settles`, 2 `provisional`. Checker exits 0.
- **19 settled**, 1 **pilot settles** (2.2, phrases per keyboard), 2 **provisional** (2.4 timeline, awaiting your term end; 7.9 between-block dictionary reset).
**Freeze it?** On your yes I set `Status: frozen 2026-10-15`, re-run the checker, and commit `Freeze the design brief`. ...
```

Turn 9 (the freeze: Edit, checker, then the Bash call; no permission denial in the result event):

```text
Edit: "Status: open" -> "Status: frozen 2026-10-15"
Bash: python3 "<checkout>/plugins/experiment-proposal/scripts/check_proposal.py" brief proposal/design-brief.md   (no output)
Bash: git add proposal/design-brief.md && git commit -m "Freeze the design brief" -- proposal/design-brief.md
[master c064037] Freeze the design brief
 1 file changed, 168 insertions(+)
 create mode 100644 proposal/design-brief.md
Frozen and committed: `c064037`, `proposal/design-brief.md`, checker exits 0.
```

## Per-item status (the 21 design-tree items, in the frozen brief)

| Item | Name                                  | Final status  | Asked in (answered in turn)                         | Asked again or changed after settled                                                                      |
| ---- | ------------------------------------- | ------------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| 1.1  | Research question                     | settled       | not asked; extracted from the command line (turn 1) | not asked; 8.3's Q3 recommended rewording it, the user said keep, entry never changed                     |
| 1.2  | Ethics route                          | settled       | round 1, Q1 (turn 2)                                | no                                                                                                        |
| 1.3  | Data plan                             | settled       | round 1, Q2 (turn 2)                                | no                                                                                                        |
| 2.2  | Conditions, trials and session length | pilot settles | round 4, Q1 (turn 5)                                | no                                                                                                        |
| 2.3  | Pilot plan                            | settled       | round 5, Q1 (turn 6)                                | unnumbered flag in turn 6 ("adjust" or "stand"); answered "stand"; entry never changed                    |
| 2.4  | Timeline                              | provisional   | round 6, Q1 (turn 7)                                | no                                                                                                        |
| 2.5  | Expected challenges                   | settled       | round 7, Q1 (turn 8)                                | no                                                                                                        |
| 6.1  | Hypotheses and research questions     | settled       | round 1, Q3 (turn 2)                                | no                                                                                                        |
| 6.2  | Hypothesis variables, direction, null | settled       | round 2, Q1 (turn 3)                                | no                                                                                                        |
| 6.5  | Interaction hypotheses                | settled       | round 2, Q2 (turn 3)                                | no                                                                                                        |
| 7.1  | Independent variable                  | settled       | round 1, Q4 (turn 2)                                | no                                                                                                        |
| 7.2  | Carry-over symmetry                   | settled       | round 2, Q3 (turn 3)                                | commented on in turn 3 (strategy asymmetry), no question, entry never changed                             |
| 7.3  | Overall design                        | settled       | round 3, Q1 (turn 4)                                | no                                                                                                        |
| 7.4  | Random assignment                     | settled       | round 2, Q4 (turn 3)                                | no                                                                                                        |
| 7.5  | Counterbalancing                      | settled       | round 3, Q2 (turn 4)                                | no                                                                                                        |
| 7.6  | Dependent variables                   | settled       | round 1, Q5 (turn 2)                                | no                                                                                                        |
| 7.7  | Control variables                     | settled       | round 2, Q5 (turn 3)                                | commented on in turn 3 ("narrower than recommended"), no question, entry never changed                    |
| 7.8  | Random variables                      | settled       | round 2, Q6 (turn 3)                                | no                                                                                                        |
| 7.9  | Confounds                             | provisional   | round 2, Q7 (turn 3), recorded `settled` in turn 3  | unnumbered flag in turn 3 ("Add it", "leave it", ...); "I don't know" changed it to provisional in turn 4 |
| 8.3  | Eligibility and screening             | settled       | round 3, Q3 (turn 4)                                | no                                                                                                        |
| 8.5  | Participant count                     | settled       | round 4, Q2 (turn 5)                                | no                                                                                                        |

Counts: 18 settled, 1 pilot settles (2.2), 2 provisional (2.4, 7.9), 21 in all. (The skill's own closing summary in turn 8 says 19 settled, 1 pilot settles, 2 provisional, which adds to 22; the brief and the checker agree on 21 entries and 18 settled.)

Frozen brief, statuses (read from `proposal/design-brief.md` in the scratch project):

```text
Status: frozen 2026-10-15
Checklist: experiment-proposal 0.2.0
1.1 settled; 1.2 settled; 1.3 settled; 2.2 pilot settles; 2.3 settled; 2.4 provisional; 2.5 settled;
6.1 settled; 6.2 settled; 6.5 settled; 7.1 settled; 7.2 settled; 7.3 settled; 7.4 settled; 7.5 settled;
7.6 settled; 7.7 settled; 7.8 settled; 7.9 provisional; 8.3 settled; 8.5 settled
Open items: 1. Item 2.4 provisional; 2. Item 7.9 provisional; 3. Run lit-search (H1 direction, and the 12-to-20 counts under 8.5); 4. Run the-ethics-board
```

## Pass bar

| Criterion                                                                         | Result    | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| --------------------------------------------------------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Every design-tree item has an entry that is settled, provisional or pilot settles | PASS      | 21 of 21 entries (the checklist's 21 design-tree items: 1.1, 1.2, 1.3, 2.2, 2.3, 2.4, 2.5, 6.1, 6.2, 6.5, 7.1 to 7.9, 8.3, 8.5), statuses in the table above; none is `weak` or `missing`.                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 2.4 provisional, 2.2 pilot settles                                                | PASS      | `2.4 Timeline`, `Status: provisional` and Open item 1; `2.2 Conditions, trials and session length`, `Status: pilot settles`, the Decision says the pilot times a block of phrases and how many fit the session.                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Item 8.5 justified from the sheet (a provisional 8.5 meets the bar)               | PASS      | Status `settled`. Decision: "16 participants, 8 per order, pre-specified. The pilot refines the phrases per keyboard, not the count." Rationale quotes the sheet's reason whole: the two swipe-keyboard studies lit-search is to find used 12 to 20 in within-subjects comparisons, the course term allows 16 at one session each, and 16 is a multiple of the two orders. The studies are not yet in hand; the entry's "Would change if" and Open item 3 carry that.                                                                                                                                                            |
| At least one `hci-researcher` call across all turns                               | PASS      | 4 `Agent` tool_use entries whose input names `experiment-proposal:hci-researcher`: turn 2 (3: 7.2, 7.7, 7.9), turn 3 (1: 7.5); turns 1 and 4 to 9: 0. Counted from every turn's jsonl. Recommendations quote it as `Recommended (hci-researcher)`.                                                                                                                                                                                                                                                                                                                                                                               |
| `check_proposal.py brief proposal/design-brief.md` exits 0 on the frozen brief    | PASS      | Run by this record's driver after the freeze, from the scratch project: stdout empty, stderr empty, exit code 0. The committed file equals the working copy.                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| The freeze commit exists                                                          | PASS      | `git log --oneline` in the scratch project: `c064037 Freeze the design brief`, then `97236fb init`. The commit adds only `proposal/design-brief.md` (168 insertions); `git status --short` is empty afterwards.                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Recorded: did the freeze's `git add && git commit` run or get refused             | RAN       | The skill's exact command ran in turn 9 and returned `[master c064037] Freeze the design brief`; the turn's `permission_denials` is empty. (Turn 1's first checker call, `...; echo "exit=$?"`, was refused as a compound command with an `echo`; the skill re-ran it plain. That is a harness refusal, recovered, and not the freeze.)                                                                                                                                                                                                                                                                                          |
| Recorded: settled items asked again                                               | see below | No numbered question named a settled item: the 20 numbered questions of rounds 1 to 7 each name an item for the first time. Two unnumbered flags put a question on settled entries (7.9 in turn 3, 2.3 in turn 6); 7.9's entry changed afterwards (settled to provisional, turn 4, because the answer was "I don't know"), 2.3's did not. Round 3's Q3 (item 8.3) also recommended rewording settled 1.1; the answer was "Keep item 1.1 as I worded it" and 1.1 is unchanged. Turn 3's opening comments on 7.2, 7.7 and 7.9 and turn 8's note that 2.5 lists two challenges are statements, not questions, and changed no entry. |

Counting the 21 numbered questions: round 1 asked 1.2, 1.3, 6.1, 7.1, 7.6; round 2 asked 6.2, 6.5, 7.2, 7.4, 7.7, 7.8, 7.9; round 3 asked 7.3, 7.5, 8.3; round 4 asked 2.2, 8.5; round 5 asked 2.3; round 6 asked 2.4; round 7 asked 2.5. That is 20 items plus the unasked 1.1 (settled by extraction) = 21.

## Verdict

PASS: the five bar criteria hold at plugin commit 5e13529 on this run.

## Observations beyond the bar (possible plugin defects, not scored)

- Draft path (step 1, "Ask once for the draft's planned path"): the skill never asked it as a question; it wrote "header assumes `proposal/draft.md`. Say so if you want another." in turn 1, the same as in the material run `material-v2-1`.
- Unprompted flags on settled entries (turns 3 and 6) turned an answered item into a second question; the "I don't know" to the first one moved 7.9 from settled to provisional. Step 3 of the skill says to ask the frontier only and has no line on flags about settled items; step 8's "treat every entry as settled and ask only what the user wants to change" applies to a frozen brief only.
- 8.3's Q3 bundled a recommendation to change settled 1.1's wording ("update item 1.1's wording to match") into a question about 8.3.
- The 400-character limit on a Decision line forced rewrites: 7.6 in turn 2 (458 characters) and 7.9 in turn 4 (530, then 464, then 412 characters) before the checker was clean; the entry-order complaint in turn 4 ("entries are not in checklist order") was fixed by re-ordering the new entries.
- Items 2.2 to 2.5 form a dependency chain (each depends on the one before), so rounds 5, 6 and 7 each held one question and cost three turns; this follows the checklist's `depends on`.
- The skill's closing summary in turn 8 miscounts the statuses (19 + 1 + 2 = 22 for 21 entries); the brief itself is right.
- Turn 8 told the user that four responses implied by other decisions are not written under 2.5 (the pilot overrunning 40 minutes, the margin needing revision after the pilot, IRB delay, experimenter or equipment failure); the entry stayed at the two the sheet gave.

## The brief

The full brief is `proposal/design-brief.md` in `$S` (committed as `c064037`); it has the three header lines, 21 entries each with the five lines, a Looked up section of six facts (the standard phrase set, the words-per-minute convention, the error-rate convention, mean phrase length, the session arithmetic, and the counterbalancing derivation), and the four Open items above.
