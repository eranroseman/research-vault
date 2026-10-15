# Scenario 5 (review) at 0.2.0, run v2-2

Date: 2026-10-15
Plugin commit: 5e13529 (`experiment-proposal` 0.2.0)
Fixtures: `fixtures/proposal-with-defects.md` copied in as `proposal/draft.md`, `fixtures/proposal-with-defects.brief.md` copied in as `proposal/design-brief.md` (both byte-identical to the fixtures at the scratch commit `fixtures`); key `fixtures/proposal-with-defects.key.md`.
Model: `--model opus`, which the stream reports as `claude-opus-5`.
Scratch project: `S=/tmp/ep-eval/review-v2-2`, outside the repository.

The headless turns ran under a driver that a rate limit killed before scoring. This record is scored afterwards from the saved artifacts (`$S.turnN.prompt`, `.jsonl`, `.meta`) and from the scratch repository's commits; no review turn was run for it. The commits are named by their subjects: `fixtures` is `818214a`, `first-pass` is `42cc12c` (after turn 2), `after-fixes` is `548db23` (after turn 3). Scoring reads `git -C "$S" show 42cc12c:proposal/review.md` and `git -C "$S" diff 42cc12c 548db23`, not the working tree.

## Commands

Setup (the scratch log shows commits `init`, then `fixtures` holding exactly the two files):

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/review-v2-2
mkdir -p "$S/proposal" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.brief.md "$S/proposal/design-brief.md"
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.md "$S/proposal/draft.md"
cd "$S" && git add -A && git commit -qm fixtures
```

Each turn ran through `/tmp/ep-eval/review-v2-drive.sh "$S" N`, which reads the prompt from `$S.turnN.prompt` and runs, for turn 1:

```bash
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null
```

and for later turns the same command with `--continue` after `-p`:

```bash
cd "$S" && timeout 1800 claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "Template mechanics: accept the course's defaults, with the citation style author-year, as the draft uses, and the supervisor the course instructor. Confirm 3.1, 5.2, 13.1 and 13.4." > "$S.turn2.jsonl" 2> "$S.turn2.err" < /dev/null
cd "$S" && git add -A && git commit -qm first-pass
cd "$S" && timeout 1800 claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "Apply fixes 4 and 7." > "$S.turn3.jsonl" 2> "$S.turn3.err" < /dev/null
cd "$S" && git add -A && git commit -qm after-fixes
cd "$S" && timeout 1800 claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "Print the hand-off again." > "$S.turn4.jsonl" 2> "$S.turn4.err" < /dev/null
```

Turn results (`.meta` and the stream's result event): turn 1 rc=0, 527 s, 25 turns; turn 2 rc=0, 58 s, 12 turns; turn 3 rc=0, 73 s, 10 turns; turn 4 rc=1, 5 s, `api_error_status` 429 (see Harness events). Turns 1 to 3 have `api_error_status` null.

The three stop runs, each one turn-1 command in its own project (`$S-nobrief`, `$S-nodraft`, `$S-open`), copies of `$S` at commit `fixtures` (same shas), with `proposal/design-brief.md` deleted, `proposal/draft.md` deleted, and the brief's line 4 changed to `Status: open` respectively:

```bash
cd "$S-nobrief" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review" > "$S-nobrief.turn1.jsonl" 2> "$S-nobrief.turn1.err" < /dev/null
```

(the same for `$S-nodraft` and `$S-open`).

Scorer's checks, run on files extracted outside the repository:

```bash
T=/tmp/ep-eval-score-v2-2
git -C "$S" show 42cc12c:proposal/review.md > "$T/first-pass.review.md"
git -C "$S" show 548db23:proposal/review.md > "$T/after-fixes.review.md"
git -C "$S" show 818214a:proposal/draft.md > "$T/fixtures.draft.md"
cd "$T" && python3 "$P/scripts/check_proposal.py" review first-pass.review.md; echo "exit=$?"
cd "$T" && python3 "$P/scripts/check_proposal.py" review after-fixes.review.md; echo "exit=$?"
cd "$T" && python3 "$P/scripts/check_proposal.py" draft fixtures.draft.md --words 2000-4000 --references 15-20 --supervisor "the course instructor"; echo "exit=$?"
git -C "$S" diff 42cc12c 548db23 -- proposal/draft.md
git -C "$S" diff -U0 42cc12c 548db23 -- proposal/draft.md proposal/review.md
```

## Transcript, decisive lines

Turn 1, the draft checker the skill ran (the same three lines again in turns 2 and 3, with `--supervisor "the course instructor"`):

```text
python3 "<checkout>/plugins/experiment-proposal/scripts/check_proposal.py" draft proposal/draft.md --words 2000-4000 --references 15-20 --supervisor "the supervising instructor"
Exit code 1
proposal/draft.md:67: references: 14 entries; the template asks for 15 to 20
proposal/draft.md:3: introduction: no bullet list of contributions
proposal/draft.md:1: appendix: no consent sentence saying the study is under the supervision of the instructor
```

Turn 1, the review checker on the skill's first write, then clean after the skill renumbered:

```text
proposal/review.md:20: fix 8 appears before fix 2; fixes are numbered in order of appearance
CLEAN
```

Turn 1, final message (opening lines; it ends with the hand-off below):

```text
Review written: `proposal/review.md`. Checker exits 0.
**Headline.** Draft contradicts frozen brief on the core design. Brief: device **between** subjects, 2×3×3 **mixed** factorial, 12 per device, asymmetric carry-over. Draft Design: device **within** subjects, "2 by 3 by 3 within-subjects factorial", "There is no between-subjects variable." ...
**Counts.** Items checked 65. Pass 49. Fail 16. Not checked 2. Consistency and brief findings 12. Fixes proposed 9. Waivers 0.
**Numbered fixes** (paste-ready text in the file): 1 data retention · 2 contributions as bullets · 3 H2 citations · 4 order of nine combinations · 5 construct validity for movement time · 6 declining without consequence · 7 illness/breakdown contingency · 8 consent form rewrite (20 min vs 35, no supervisor line, no retention, "no payment" vs course credit) · 9 question point in script.
**Question 2 — attested batch (3.1, 5.2, 13.1, 13.4).** Unconfirmed, so all four read `fail`. ...
**Question 3 — which fixes should I apply? Give their numbers.**
```

Turn 2, final message (opening lines):

```text
Four attested rows now pass; `proposal/review.md` rewritten, checker exits 0. Draft untouched.
- Summary: Items checked 65. Pass 53. Fail 12. Not checked 2. Findings 12. Fixes 9. Waivers 0.
Re-ran the draft checker with the confirmed supervisor: same three mechanics defects (references 14, contributions not bulleted, no supervision sentence) ...
**Which fixes should I apply? Give their numbers** (1–9).
```

Turn 3, final message (opening lines):

```text
Fixes 4 and 7 applied. Nothing else in the draft touched.
- 7.5 → `pass (fix 4 applied)`, quoting the new Design sentence.
- 10.5 → `pass (fix 7 applied)`; caveat recorded that the spare computer must carry the same 24-inch 1920 by 1080 display, or the pixel distances shift.
- Brief against draft, item 7.5 → `pass (fix 4 applied)`; the draft now states the brief's decision in its own terms.
- Summary: Items checked 65. Pass 55. Fail 10. Not checked 2. Findings 11. Fixes proposed 9. Waivers 0.
Review checker exits 0.
```

## First pass against the key (commit `42cc12c`)

Summary line: `Items checked: 65. Pass: 53. Fail: 12. Not checked (defend-stage): 2. Consistency and brief findings: 12. Fixes proposed: 9. Waivers: 0.` The counts agree with the rows: 67 rows (61 draft-checked, 4 attested, 2 defend-stage); 49 draft-checked passes (two of them `pass narrowly`, 13.8 and 13.9) plus the 4 attested confirmations; 12 fails (1.3, 4.3, 5.1, 6.2, 7.2, 7.5, 7.6, 8.2, 10.5, 12.3, 12.5, 13.5); 2 Cross-section and 10 Brief-against-draft `- fail` lines.

### D1 to D12

| Defect | Item or section                | First-pass report                                                                                                                                                                                                                            | Verdict |
| ------ | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| D1     | 1.3                            | fail: "the data plan gives no retention period for the raw logs and states the access limit only inside the consent form, not in the proposal body." (fix 1)                                                                                 | caught  |
| D2     | 6.2                            | fail: "H2 names its variables and direction but cites no source for that direction, though the brief gives two." (fix 3)                                                                                                                     | caught  |
| D3     | 4.3 (and the draft checker)    | fail: "the contributions run as prose labelled (a), (b) and (c) rather than as a bullet list." (fix 2); checker: "introduction: no bullet list of contributions"                                                                             | caught  |
| D4     | 7.5                            | fail: "the order of the two devices is counterbalanced, but the order of the nine distance-and-size combinations within a device is never stated." (fix 4)                                                                                   | caught  |
| D5     | 7.6                            | fail: "movement time is given a unit, a recording method, a scale and a reliability statement but no construct-validity statement" (fix 5)                                                                                                   | caught  |
| D6     | 8.2                            | fail: "the recruitment method is stated, but nothing says how a candidate in the author's own course section can decline without consequence." (fix 6)                                                                                       | caught  |
| D7     | 10.5                           | fail: "nothing says what happens if the experimenter falls ill or the equipment breaks down." (fix 7)                                                                                                                                        | caught  |
| D8     | 5.1 (and the draft checker)    | fail: "the reference list holds 14 entries against the template's 15 to 20" (decide); checker: "references: 14 entries; the template asks for 15 to 20"                                                                                      | caught  |
| D9     | 12.3 (and the draft checker)   | fail: "... and omits the supervision sentence, ..." (fix 8); checker: "appendix: no consent sentence saying the study is under the supervision of the instructor"                                                                            | caught  |
| D10    | 12.5                           | fail: "the script has no point at which participants can ask questions." (fix 9)                                                                                                                                                             | caught  |
| D11    | 12.3 and Cross-section         | 12.3 fail: "the consent form states about 20 minutes against the 35-minute session estimate"; Cross-section: "fail: the session duration is 35 minutes in Procedure ... but "it takes about 20 minutes" in Appendix B, the consent form."    | caught  |
| D12    | Brief against draft, entry 7.1 | "fail: item 7.1. The brief decides "device between subjects; distance and size within subjects"; the draft's Design says "Device: ... within subjects, because individual pointing skill varies far more than the device effect we expect"." | caught  |

Caught 12 of 12, passed 0. Row 12.3 reports both D9 and D11, which the key counts for both. D12 is scored on the Brief-against-draft section alone; the 7.1 row itself reads pass, as the key expects.

### The 38 controls

All 38 control rows read pass in the first pass; over-failures: 0.

| Item | Result | Quoted passage (opening words)                                                                                 | Location                                                   |
| ---- | ------ | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| 1.1  | pass   | "Does selecting targets with a mouse rather than a trackball change movement time?"                            | Introduction, para 1                                       |
| 1.2  | pass   | "The study will run under the department's standing approval for minimal-risk studies (Appendix E)."           | Participants, para 1                                       |
| 2.2  | pass   | "10 practice trials on the first device, then 5 trials of each of the nine ..."                                | Procedure, para 1                                          |
| 2.3  | pass   | "The pilot sample, three lab members, differs from the main sample ..."                                        | Participants, para 2                                       |
| 2.4  | pass   | "Pilot in week 3; data collection in weeks 4 to 7; ..."                                                        | Timeline                                                   |
| 2.5  | pass   | "if sign-ups fall short by week 5, recruiting extends to a second section"                                     | Participants, para 2                                       |
| 3.2  | pass   | "## Research questions or Hypotheses"                                                                          | heading 3 of 8, between Literature review and Participants |
| 3.3  | pass   | "a difference that is not statistically significant is reported with its estimate and interval ..."            | Research questions or Hypotheses, para 2                   |
| 4.1  | pass   | "We will compare movement time and error rate with a mouse and a trackball ..."                                | Introduction, para 1                                       |
| 4.2  | pass   | "Vendors make the case for each device on comfort and speed, ..."                                              | Introduction, para 2                                       |
| 4.4  | pass   | "Only a controlled experiment can show that the device, rather than the person or the task, ..."               | Introduction, para 2                                       |
| 4.5  | pass   | "The rest of this proposal reviews the literature, states the hypotheses, ..."                                 | Introduction, para 3                                       |
| 5.3  | pass   | "The gap this literature leaves is a comparison that crosses the two devices ..."                              | Literature review, final para                              |
| 6.1  | pass   | "H1: Mean movement time will be shorter with the mouse than with the trackball ..."                            | Research questions or Hypotheses, bullet 1                 |
| 6.3  | pass   | "Each hypothesis is scoped to the two devices and the nine distance-and-size combinations tested ..."          | Research questions or Hypotheses, para 2                   |
| 6.5  | pass   | "H3: The mouse's movement-time advantage will be larger for smaller targets, ..."                              | Research questions or Hypotheses, bullet 3                 |
| 6.6  | pass   | "For H1, a statistically significant advantage for the mouse supports it; ..."                                 | Research questions or Hypotheses, para 2                   |
| 7.7  | pass   | "Right-handed participants aged 18 to 22, determined by self-report on the screening form; ..."                | Design, Control variables                                  |
| 7.8  | pass   | "Individual skill, vision, mood, time of day, ..."                                                             | Design, Random variables                                   |
| 7.9  | pass   | "Maturation: a single short session. Instrumentation: ..."                                                     | Design, Confounds to watch for                             |
| 8.1  | pass   | "Twenty-four right-handed adults aged 18 to 22 will take part, ..."                                            | Participants, para 1                                       |
| 8.3  | pass   | "No eligibility criterion selects people for an extreme score on pointing performance."                        | Participants, para 1                                       |
| 8.4  | pass   | "They are a convenience sample, ..."                                                                           | Participants, para 1                                       |
| 8.5  | pass   | "The number follows similar device comparisons and a stated reason: ..."                                       | Participants, para 2                                       |
| 8.8  | pass   | "it is a multiple of the two counterbalanced device orders"                                                    | Participants, para 2                                       |
| 8.9  | pass   | "Four extras will be recruited for no-shows ..."                                                               | Participants, para 2                                       |
| 9.1  | pass   | "Participants will interact with a Logitech M510 mouse and a Kensington Orbit trackball, ..."                  | Materials, para 1                                          |
| 9.2  | pass   | "a program that presents targets at the three distances and three sizes and logs, ..."                         | Materials, para 1                                          |
| 9.3  | pass   | "The program will be written for the study and will log every trial automatically, ..."                        | Materials, para 2                                          |
| 9.4  | pass   | "The questionnaire is custom because the two items need no standard instrument; ..."                           | Materials, para 2                                          |
| 10.1 | pass   | "Each participant will be tested alone in room 204, the same room for every session."                          | Procedure, para 1                                          |
| 10.2 | pass   | "The phases, in order, with their estimated durations: ..."                                                    | Procedure, para 1                                          |
| 10.3 | pass   | "The mouse and the trackball will be used at the point in the session where the script introduces them; ..."   | Procedure, para 2                                          |
| 10.4 | pass   | "Every participant will hear the same instructions because the experimenter will read the verbatim script ..." | Procedure, para 2                                          |
| 12.1 | pass   | "The study falls under the department's standing approval for minimal-risk interaction studies ..."            | Appendix E                                                 |
| 12.2 | pass   | "recruited from the author's own course section by an announcement in class (Appendix A) and a sign-up sheet"  | Participants, para 1                                       |
| 12.4 | pass   | "Consent is recorded by your signature below."                                                                 | Appendix B                                                 |
| 12.6 | pass   | `"Age: \_\_\_\_ Handedness: \_\_\_\_"` (escaped underscores, which the key accepts)                            | Appendix D                                                 |

Rows that are neither a defect's home nor a control: 2.1 pass, 6.4 pass (vacuous, no research question), 7.1 pass, 7.3 pass, 7.4 pass, 7.2 fail and 13.5 fail. 7.2 fails because "the draft calls the device carry-over symmetric, while the brief records it as one-way habit transfer from daily mouse use", the D12 departure seen from the carry-over item; 13.5 is the roll-up of the failing items. Neither is a control, so neither counts against the bar.

Findings beyond the key, not counted as over-failures (the key's over-failure is a failing control row, and every control row passes); each is grounded in the fixture text:

- Brief against draft, "fail: item 7.9. The brief prevents history with "same weeks, similar times"; the draft prevents it instead with "both devices will be used by every participant within one session, ..."". The brief's 7.9 entry does read "history (same weeks, similar times)"; the difference follows from D12 like the 7.2, 7.3, 7.4 and 8.5 entries the key anticipates. Defensible.
- Cross-section consistency, "fail: the incentive differs: "Participants who complete the session will receive course credit." (Participants, para 2) against "there is no payment" (Appendix B), which leaves the credit undisclosed at consent." Both passages are in the draft. Defensible.
- Row 12.3 also names the credit, the retention period, who sees the results and the consequences of withdrawing, besides D9 and D11. Each is absent from the fixture's consent form.

Even counted as over-failures, the first two would make two, which the bar allows.

### Draft-checked passes quote a passage with a location

A script matched every `pass` and `pass narrowly` row in the first-pass file against the fixture draft: 49 draft-checked pass rows, each with a double-quoted passage followed by its location in parentheses, all 49 passages verbatim in the draft, none over two sentences. One borderline row: 6.4 puts prose before its quote, "the section states no research question, only H1 to H3, so the item is vacuous here: "H2: Error rate will be lower with the mouse than with the trackball." (Research questions or Hypotheses, bullet 2)"; the quote is verbatim and located, so it counts. The four attested rows (3.1, 5.2, 13.1, 13.4) read `pass: confirmed by the user, 2026-10-15`.

### 13.2 and 13.3

Both rows read `not checked: defend-stage`.

### The draft checker's mechanics

The draft checker reported exactly three lines, D8 (`references: 14 entries; the template asks for 15 to 20`), D3 (`introduction: no bullet list of contributions`) and D9 (`appendix: no consent sentence saying the study is under the supervision of the instructor`), and nothing else: no section-order or word-count line. The skill ran it in turns 1, 2 and 3 with the same three lines each time; the scorer's run on the fixture draft prints the same three lines, `exit=1`.

### Checker on the first-pass review.md

```text
$ python3 "$P/scripts/check_proposal.py" review first-pass.review.md; echo "exit=$?"
exit=0
```

No defect lines; exit 0.

## Fix-picking check

The fix numbers: in the first-pass file, row 7.5 (D4) carries "fix 4: add to Design, para 1, ..." and row 10.5 (D7) carries "fix 7: add to the end of Procedure, para 2, ...". Turn 3's prompt was "Apply fixes 4 and 7." Correct.

The draft diff `42cc12c..548db23`: two changed lines, each one fix. At zero context, exactly two hunks:

```text
@@ -49 +49 @@ Each participant will be tested alone in room 204, the same room for every sessi
@@ -53 +53 @@ Every participant will hear the same instructions because the experimenter will
```

Line 49 (Procedure, para 2) gains "If the experimenter falls ill or a device or the computer fails, the session will be rescheduled within the same week ..."; line 53 (Design, para 1) gains "The nine distance-and-size combinations will be presented in a random order for each participant, drawn by the study software with equal counts per combination." The default-context `git diff` prints them as one hunk (`@@ -46,11 +46,11 @@`) only because the two lines are four apart and their three-line contexts overlap; diffstat `proposal/draft.md | 4 ++--`. Nothing else in the draft changed. The first pass left the draft untouched: `fixtures..first-pass` changes only `proposal/review.md`.

The review.md diff changes five lines, all of them allowed by the key; every other row is byte-identical:

- line 37, row 7.5: now `- **7.5** pass (fix 4 applied): "The nine distance-and-size combinations will be presented in a random order for each participant, drawn by the study software with equal counts per combination." (Design, para 1), ...`
- line 57, row 10.5: now `- **10.5** pass (fix 7 applied): "If the experimenter falls ill or a device or the computer fails, ..." (Procedure, para 2); ...`
- line 68, row 13.5: 7.5 and 10.5 dropped from its list, and "apply fixes 1 to 9" became "apply fixes 1, 2, 3, 5, 6, 8 and 9"
- line 82, the Brief-against-draft 7.5 entry the fix touched: now "pass (fix 4 applied): item 7.5. ... the draft's Design now states it in those terms."
- line 100, Summary: `Items checked: 65. Pass: 55. Fail: 10. Not checked (defend-stage): 2. Consistency and brief findings: 11. Fixes proposed: 9. Waivers: 0.`

Both re-checked rows quote the after-fixes draft verbatim (the same script, run on `after-fixes.review.md` against the after-fixes draft). Waivers and Hand-off unchanged.

Checker on the after-fixes review.md:

```text
$ python3 "$P/scripts/check_proposal.py" review after-fixes.review.md; echo "exit=$?"
exit=0
```

## The three stops

All three exited rc=0 and wrote nothing: `git status --porcelain` in each project shows only the setup change (` D proposal/design-brief.md`, ` D proposal/draft.md`, ` M proposal/design-brief.md`), and no `proposal/review.md` exists.

Brief deleted (`$S-nobrief`, 18 s):

```text
No design brief at proposal/design-brief.md; run /experiment-proposal:design first.
```

Names the brief and `/experiment-proposal:design`. Pass.

Draft deleted (`$S-nodraft`, 48 s):

```text
No draft. Stop.
Brief found at `proposal/design-brief.md`, frozen 2026-10-10.
Draft missing: path tried `proposal/draft.md` (from brief's `Draft:` line), resolved `/tmp/ep-eval/review-v2-2-nodraft/proposal/draft.md` — not found. Only `design-brief.md` in that folder.
```

Names `proposal/draft.md`. Pass.

Brief `Status: open` (`$S-open`, 38 s):

```text
Brief not frozen. `proposal/design-brief.md:4` reads `Status: open`, not `frozen YYYY-MM-DD`.
Stopping here — no review written. Run `/experiment-proposal:design` to finish and freeze brief, then re-run review.
```

Says the brief is not frozen. Pass.

## Hand-off (research-grill installed)

Turn 1 read `~/.claude/plugins/installed_plugins.json` with the Read tool; it lists `oss@open-science-skills`, so the present case applies. Turns 2 and 3 (and turn 1) end their final message with this block, the last characters of each message being its closing fence:

```text
/oss:research-grill defend proposal/draft.md
Seed list: no waivers; could someone run a session from the Method alone?; item 13.8 passed narrowly, the doubt being that contribution (c), a reusable task program and its trial logs, would describe almost any pointing study unchanged; item 13.9 passed narrowly, the doubt being that the steering citation is declared irrelevant in its own sentence and the throughput discussion supports an analysis the proposal says it will not run.
```

The two lines are identical to the Hand-off section of review.md at both commits. The final message ends with the hand-off in full: yes, in turns 1, 2 and 3. Scenario 6's "print it again" turn is not scored here (see below).

## Harness events

- Turn 4 ("Print the hand-off again.") failed: `rc=1 secs=5`; the result event reads `"is_error": true, "api_error_status": 429, "result": "You've hit your session limit · resets 3:40am (America/Chicago)"`. The turn belongs to scenario 6 and is not scored in this record; turns 1 to 3 and the three stops ran clean.
- Turn 1: the skill's first draft-checker call appended `; echo "EXIT:$?"` and was denied ("This Bash command contains multiple operations. The following part requires approval: echo "EXIT:$?""), and a `sed -n 1,200p` of the plugin's `check_proposal.py` was blocked as outside the session's working directory; both appear as `permission_denials` in turn 1's result event. The skill reran the plain checker command and read the script with the Read tool. No effect on the review.
- The host's user-level caveman hook shows in one stop message's style ("`proposal/draft.md` exist, but review cannot run without frozen brief"); no effect on what was checked.
- The driver was killed by a rate limit before scoring; this record was scored afterwards from the saved artifacts.

## Pass bar

| Criterion                                                   | Result | Evidence                                                                                       |
| ----------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------- |
| At least 11 of 12 caught, 0 passed                          | pass   | 12 of 12 caught, 0 passed                                                                      |
| At most two over-failures                                   | pass   | 0 of 38 control rows fail                                                                      |
| Draft checker reports D3, D8 and D9 and nothing else        | pass   | exactly those three lines, in turns 1, 2 and 3 and in the scorer's run                         |
| Every draft-checked pass quotes a passage with its location | pass   | 49 of 49, all verbatim; 6.4 borderline (prose before the quote)                                |
| 13.2 and 13.3 read not checked                              | pass   | both `not checked: defend-stage`                                                               |
| Checker exits 0 on the first-pass review.md                 | pass   | exit=0, no output                                                                              |
| Picked fixes applied alone, affected rows re-checked        | pass   | fixes 4 and 7 are D4's and D7's; two draft hunks at zero context; five allowed review.md lines |
| Checker exits 0 on the after-fixes review.md                | pass   | exit=0, no output                                                                              |
| Missing-brief, missing-draft and not-frozen stops           | pass   | each stops, names the file or says not frozen, writes nothing                                  |
| Hand-off ends turn 2's and turn 3's final messages in full  | pass   | present-case block quoted above                                                                |

## Verdict

Run 2 of scenario 5 at 0.2.0: pass.

## Notes

- Before the attested batch, turn 1 wrote 3.1, 5.2, 13.1 and 13.4 as `fail` with a `decide:` (snapshot `$S.turn1.review.md`; Summary then `Pass: 49. Fail: 16.`). The shape has no pending result, so this conforms; turn 2 turned them into `pass: confirmed by the user, 2026-10-15` and recomputed 13.5 and the Summary.
- The review checker earned its place in turn 1: it caught the skill's own out-of-order fix reference ("fix 8 appears before fix 2") on the first write.
- Two lines in the sections the checker accepts fall outside the shape's wording, "One line per finding, `- fail: ...`, or `- pass: ...` when there is none": an unbulleted "No other mismatch: the participant count is 24 ..." line under Cross-section consistency, and, after the fixes, "- pass (fix 4 applied): item 7.5. ..." under Brief against draft. Neither touches the bar.
