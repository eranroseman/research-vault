# Scenario 5 (review on the proposal with 12 planted defects) at 0.2.0, run v2-1

Date: 2026-10-15
Plugin commit: 5e13529 (`experiment-proposal` 0.2.0). The plugin tree is unchanged between 5e13529 and the worktree's HEAD at scoring time (`git diff --stat 5e13529 HEAD -- plugins/experiment-proposal` prints nothing).
Fixtures: `fixtures/proposal-with-defects.md` copied in as `proposal/draft.md`, `fixtures/proposal-with-defects.brief.md` as `proposal/design-brief.md`; key `fixtures/proposal-with-defects.key.md`. Both scratch copies are byte-identical to the fixtures (`git -C "$S" show 818214a:<file>` diffed against each fixture prints nothing).
Model: `--model opus`, which the init event of the stream reports as `claude-opus-5`. The init event lists the plugins `experiment-proposal` (one agent, `experiment-proposal:hci-researcher`) and `oss` (research-grill present); the 0.2.0 copy is the one that ran, since turn 1's Reads of `references/checklist.md`, `references/review.md` and `.claude-plugin/plugin.json` resolved under `$P`, and the review's header reads `Checklist: experiment-proposal 0.2.0`.
Scoring: the driver ran turns 1 to 4 and the three stops, then was killed by a rate limit before scoring. This record is scored from the saved artifacts (the stream-json of each turn, the scratch project's commits); no turn was run during scoring.

## Commands

Setup (as the scratch repository's history shows it: an empty `init` commit, then `fixtures` with the two files):

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/review-v2-1
mkdir -p "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval && git commit --allow-empty -qm init && mkdir proposal
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.brief.md "$S/proposal/design-brief.md"
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.md "$S/proposal/draft.md"
cd "$S" && git add -A && git commit -qm fixtures
```

Each turn ran through the driver's helper `review-v2-drive.sh "$S" N`, which reads the prompt from `$S.turnN.prompt` and runs, for turn 1:

```bash
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null
```

and for later turns the same command with `--continue` before `--model`. Prompts and exits (`$S.turnN.meta`):

| Turn | Prompt                                                                                                                                                                                 | Exit, wall time                        |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| 1    | `/experiment-proposal:review`                                                                                                                                                          | rc=0, 595 s (24 turns)                 |
| 2    | "Template mechanics: accept the course's defaults, with the citation style author-year, as the draft uses, and the supervisor the course instructor. Confirm 3.1, 5.2, 13.1 and 13.4." | rc=0, 58 s (10 turns)                  |
| 3    | "Apply fixes 4 and 8."                                                                                                                                                                 | rc=0, 66 s (10 turns)                  |
| 4    | "Print the hand-off again."                                                                                                                                                            | rc=1, 5 s: 429, not scored (see below) |

Commits in `$S` between turns:

```bash
cd "$S" && git add -A && git commit -qm first-pass    # after turn 2: 53984d7
cd "$S" && git add -A && git commit -qm after-fixes   # after turn 3: 6663833
```

The three stops, each in a copy of the project at its `fixtures` commit (HEAD 818214a in each copy) with one planted change in the working tree, run with the turn 1 command and `S` replaced by the copy:

```bash
# "$S-nobrief": git status shows " D proposal/design-brief.md"
# "$S-nodraft": git status shows " D proposal/draft.md"
# "$S-open":    git status shows " M proposal/design-brief.md"; the diff is line 4, "Status: frozen 2026-10-10" -> "Status: open"
cd "$S-nobrief" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review" > "$S-nobrief.turn1.jsonl" 2> "$S-nobrief.turn1.err" < /dev/null
```

Scoring commands (temporary files outside the repository):

```bash
T=$(mktemp -d)
git -C "$S" show 53984d7:proposal/review.md > "$T/first-pass-review.md"     # commit "first-pass"
git -C "$S" show 6663833:proposal/review.md > "$T/after-fixes-review.md"    # commit "after-fixes"
python3 "$P/scripts/check_proposal.py" review "$T/first-pass-review.md"; echo "exit=$?"
python3 "$P/scripts/check_proposal.py" review "$T/after-fixes-review.md"; echo "exit=$?"
git -C "$S" diff 53984d7 6663833
git -C "$S" diff -U0 53984d7 6663833
git -C "$S" diff --word-diff=plain -U0 53984d7 6663833 -- proposal/draft.md
```

## Decisive transcript lines

Turn 1, the draft checker (the first attempt, with a supervisor name, was refused by the permission guard; see Harness events):

```text
proposal/draft.md:67: references: 14 entries; the template asks for 15 to 20
proposal/draft.md:3: introduction: no bullet list of contributions
proposal/draft.md:1: appendix: no consent sentence saying the study is under the supervision of the instructor
```

Turn 1, final message, opening and the batch:

```text
`proposal/review.md` written, checker clean. 65 items checked: 48 pass (2 narrowly), 17 fail, 2 defend-stage. 10 paste-ready fixes, 7 decides, 9 consistency-and-brief findings, 0 waivers.

**Headline:** draft runs **device within subjects** with symmetric carry-over; brief entries 7.1–7.4 settle it as **between subjects**, asymmetric. Four brief departures hang off that one decision, and it also re-opens brief 2.2 (35 minutes, 90 trials) and 8.5 (twelve per device) — both only hold within subjects.
...
1. Confirm the template's values and the attested items in one go — items 3.1, 5.2, 13.1 and 13.4 all fail now for want of your word. Defaults offered: sections Introduction, Literature review, Research questions or Hypotheses, Participants, Materials, Procedure, Design, Appendix; body 2,000–4,000 words excluding references and appendices; 15–20 references; the template's citation style (ACM reference format for CHI); and the supervising instructor's name. ...

2. Which fixes should I apply? Give their numbers. Fixes 1–10 are paste-ready; the decides are yours, and fix 9 needs the instructor's name plus a call on the delete-on-withdrawal promise, which no source states.
```

Turn 2 re-ran the draft checker with the confirmed section list (`--words 2000-4000 --references 15-20 --sections "Introduction, Literature review, Research questions or Hypotheses, Participants, Materials, Procedure, Design, Appendix"`), exit 1, the same three lines and no others. Its final message:

```text
Four attested items recorded as confirmed; review rewritten and the checker exits 0.

Changed rows: **3.1** pass (course defaults, author-year style, course instructor as supervisor), **5.2** pass, **13.1** pass, **13.4** pass. **3.3** keeps its pass, now on the confirmed author-year style rather than pending it. **13.5** still fails, now on twelve items of steps 1 to 12 rather than fourteen.

Summary: Items checked: 65. Pass: 52. Fail: 13. Not checked (defend-stage): 2. Consistency and brief findings: 9. Fixes proposed: 10. Waivers: 0.

One gap your answer leaves open: "the course instructor" is a role, not a name. ...
```

Turn 3, final message (before the hand-off):

```text
Fixes 4 and 8 applied to `proposal/draft.md`, nothing else touched. Checker exits 0 on the rewritten review.

- **Design, para 1** gained the combination-order sentence. Row **7.5** now reads `pass (fix 4 applied)`, quoting it.
- **Procedure, para 2** gained the illness-and-breakdown sentence. Row **10.5** now reads `pass (fix 8 applied)`, quoting it.
- Brief against draft: the 7.5 departure is now a pass — the brief's wording stands in the draft word for word. Findings drop from 9 to 8.
- **13.5** still fails, now on ten items of steps 1 to 12 rather than twelve.
```

No turn opened the key or any `docs/research` file (a grep of the three streams for `key.md` and `docs/research` finds nothing), and no turn called the `Agent` tool.

## Scoring against the key (first pass: review.md at commit 53984d7, after turn 2)

First-pass Summary line: `Items checked: 65. Pass: 52. Fail: 13. Not checked (defend-stage): 2. Consistency and brief findings: 9. Fixes proposed: 10. Waivers: 0.` Every count recomputes from the rows (65 rows not `not checked`, 52 `pass` or `pass narrowly`, 13 `fail`, 9 `- fail` lines across Cross-section and Brief against draft, highest fix number 10). The file has 67 rows, one per checklist item, and the seven sections in the shape's order.

### D1 to D12

| Defect | Item or section                    | The row's reason (quoted)                                                                                                                                                                                                                           | Verdict |
| ------ | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| D1     | 1.3                                | fail: "the data plan gives no retention period for the raw logs, which the brief sets at five years." (fix 1)                                                                                                                                       | caught  |
| D2     | 6.2                                | fail: "H2 names its variables and direction but cites no source for that direction" (fix 3)                                                                                                                                                         | caught  |
| D3     | 4.3 (and the draft checker)        | fail: "the three contributions run as prose inside one sentence, not as a bullet list." (fix 2); checker "introduction: no bullet list of contributions"                                                                                            | caught  |
| D4     | 7.5                                | fail: "the order of the nine distance-and-size combinations within a device is never stated, though the brief settles it." (fix 4)                                                                                                                  | caught  |
| D5     | 7.6                                | fail: "movement time carries no construct-validity statement and error rate no reliability statement." (fix 5)                                                                                                                                      | caught  |
| D6     | 8.2                                | fail: "the recruitment method is stated, but nothing says how a student in the author's own section can decline without consequence." (fix 6)                                                                                                       | caught  |
| D7     | 10.5                               | fail: "nothing says what happens if the experimenter falls ill or the equipment breaks down." (fix 8)                                                                                                                                               | caught  |
| D8     | 5.1 (and the draft checker)        | fail: "the reference list holds 14 entries against the template's 15 to 20." (decide: lit-search); checker "references: 14 entries; the template asks for 15 to 20"                                                                                 | caught  |
| D9     | 12.3 (and the draft checker)       | fail: "the consent form omits the supervisor, the purpose, the right to decline, ..." (fix 9); checker "appendix: no consent sentence saying the study is under the supervision of the instructor"                                                  | caught  |
| D10    | 12.5                               | fail: "the script has no point where participants can ask questions." (fix 10)                                                                                                                                                                      | caught  |
| D11    | 12.3 and Cross-section consistency | 12.3: "states the duration as about 20 minutes against the 35-minute session estimate"; Cross-section: "fail: the session duration differs, "about 20 minutes" in Appendix B against "the session estimate of 35 minutes" in Procedure paragraph 1" | caught  |
| D12    | Brief against draft, entry 7.1     | "fail: entry 7.1 puts device between subjects; Design paragraph 1 reads "Device: the mouse or the trackball named in Materials, within subjects". See the decide at item 7.2."                                                                      | caught  |

Caught 12 of 12, passed 0. Row 12.3 reports both of its reasons (D9 and D11) and counts for both, as the key allows. D12 is scored on the Brief against draft section alone; the 7.1 row reads pass, which the key does not consult.

The Brief against draft section's other lines are departures the key expects and does not count as over-failing: entries 1.3, 6.2 and 7.6 (restating D1, D2, D5), 7.2, 7.3 and 7.4 (the between-subjects brief), and 7.5 (D4 seen from the brief). It does not give 8.5's "12 per device" a line of its own; the 7.2 row's decide names it ("entry 8.5's twelve per device only hold if each participant meets both devices"). Row 7.2 fails ("the draft calls the device carry-over symmetric and puts device within subjects, against the brief's settled finding"); it is neither a control nor a defect home, so it counts neither way.

### Controls

The 38 controls (1.1, 1.2, 2.2 to 2.5, 3.2, 3.3, 4.1, 4.2, 4.4, 4.5, 5.3, 6.1, 6.3, 6.5, 6.6, 7.7, 7.8, 7.9, 8.1, 8.3, 8.4, 8.5, 8.8, 8.9, 9.1 to 9.4, 10.1 to 10.4, 12.1, 12.2, 12.4, 12.6): 37 pass, 1 over-failure.

- **8.3**, over-failed. The row's reason: "the criteria are listed, but the form named as the screen, Appendix D, is administered after the second device in Procedure, so eligibility is never screened before the session." (fix 7). The draft does say "screened by a short form (Appendix D) for handedness and age" (Participants, para 1) and gives "the demographic questionnaire (Appendix D) (2 minutes)" after the second device (Procedure, para 1), so the row describes a real, unplanted tension in the fixture; the key lists 8.3 as a control, so it counts as an over-failure.

1 over-failure; the bar allows two.

### The draft checker's mechanics

Turn 1 (`--words 2000-4000 --references 15-20`) and turn 2 (the same plus the confirmed `--sections` list) each printed exactly three lines, exit 1: references (D8), the contribution bullet list (D3), the supervision sentence (D9). No sections line and no word-count line; the review records the body as "2,449 words, inside the bounds" (row 13.5). Mechanics report D3, D8 and D9 and nothing else: pass. (A scoring re-run of the same turn 2 command on the fixture copy printed the same three lines, exit 1.)

### Quotes on draft-checked passes

48 draft-checked rows pass or pass narrowly (42 under Items, the six substance tests); the four attested passes (3.1, 5.2, 13.1, 13.4) read `confirmed by the user, 2026-10-15`. Every one of the 48 carries a quoted passage followed by its location in parentheses. Checked mechanically against the draft: 47 quotes occur verbatim (12.6's `"Age: ____ Handedness: ____"` matches with the draft's escaped underscores unescaped, which the key accepts), and none is longer than two sentences. Borderline, as the 0.1.0 record flagged its 3.2:

- 8.9 quotes "Four extras will be recruited for no-shows and for participants who turn out not to fit the profile." (Participants, para 2); the draft has a semicolon where the quote's period stands, the words are verbatim.
- 3.2 and 6.4 quote the heading "## Research questions or Hypotheses" (heading, line 25), and 12.1 quotes "## Appendix E: ethics review" (heading, line 100), a heading line as the passage.

### 13.2 and 13.3

Both rows read `not checked: defend-stage`.

### The checker on the first pass

```text
$ python3 "$P/scripts/check_proposal.py" review "$T/first-pass-review.md"; echo "exit=$?"
exit=0
```

## Fix-picking check

D4 is row 7.5, fix 4; D7 is row 10.5, fix 8, in the first-pass file. Turn 3's prompt was "Apply fixes 4 and 8.": the right two numbers.

The draft, `git -C "$S" diff 53984d7 6663833 -- proposal/draft.md`: at git's default three lines of context it shows one hunk, `@@ -46,11 +46,11 @@`, because the two changed lines (49, the last Procedure paragraph, and 53, Design paragraph 1) are separated only by a blank line, `## Design` and a blank line. With `-U0` it shows exactly two hunks, `@@ -49 +49 @@` and `@@ -53 +53 @@`, and `--word-diff` shows exactly two insertions and no deletions:

```text
{+If the experimenter falls ill, the sessions are rescheduled within the data-collection weeks and the same experimenter runs them; if the computer or either device fails, the session stops, the participant is thanked and offered a new slot, and the trials already logged are discarded so that no participant contributes a part session.+}
{+The nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software, with equal numbers of trials per combination.+}
```

Each insertion is its fix's quoted text, word for word, at the place the fix names. The key's "exactly two hunks in `git diff`" is met at `-U0`, not at the default context; in this fixture any edit to Procedure (lines 47 to 49) and to Design paragraph 1 (line 53) falls within one default hunk, so the literal wording cannot be met by any correct pair of these fixes. Scored on what it checks, the two picked fixes applied alone: pass.

`proposal/review.md`, `git -C "$S" diff -U0 53984d7 6663833 -- proposal/review.md`: five changed lines, all on the key's allowed list; every other line is byte-identical, and Waivers and Hand-off are unchanged.

| Line | What changed                                        | Allowed by the key                     |
| ---- | --------------------------------------------------- | -------------------------------------- |
| 37   | row 7.5, fail to `pass (fix 4 applied)`             | yes, the 7.5 row                       |
| 57   | row 10.5, fail to `pass (fix 8 applied)`            | yes, the 10.5 row                      |
| 68   | row 13.5, "twelve items" to "ten items", still fail | yes, the 13.5 row                      |
| 84   | Brief against draft entry 7.5, fail to pass         | yes, a Brief finding the fixes touched |
| 98   | Summary                                             | yes, the Summary                       |

The re-checked rows:

```text
- **7.5** pass (fix 4 applied): "The nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software, with equal numbers of trials per combination." (Design, para 1); the device order stays counterbalanced from a shuffled list.
- **10.5** pass (fix 8 applied): "If the experimenter falls ill, the sessions are rescheduled within the data-collection weeks and the same experimenter runs them; if the computer or either device fails, the session stops, the participant is thanked and offered a new slot, and the trials already logged are discarded so that no participant contributes a part session." (Procedure, para 2)
- pass (fix 4 applied): entry 7.5's random order per participant with equal counts, drawn by the software, now stands in Design paragraph 1 word for word.
```

Summary after the fixes: `Items checked: 65. Pass: 54. Fail: 11. Not checked (defend-stage): 2. Consistency and brief findings: 8. Fixes proposed: 10. Waivers: 0.`, every count recomputed from the rows (fix 4 and fix 8 stay counted, so the highest fix number is still 10). Turn 3 ran the checker on its own rewrite ("(Bash completed with no output)"). Scoring re-run:

```text
$ python3 "$P/scripts/check_proposal.py" review "$T/after-fixes-review.md"; echo "exit=$?"
exit=0
```

## Missing-input and not-frozen stops

No stop project holds a `proposal/review.md` afterwards, and `git status --porcelain` in each shows only its planted change: nothing was written.

Brief deleted (`$S-nobrief`, rc=0, 18 s), final message:

```text
No design brief at proposal/design-brief.md; run /experiment-proposal:design first.

Draft exists at `proposal/draft.md`, but review needs frozen brief as evidence base. Nothing written.
```

Stops, names the brief and `/experiment-proposal:design`: pass.

Draft deleted (`$S-nodraft`, rc=0, 37 s), final message (the scratch path written as `$S-nodraft`):

```text
Stopped at step 1. No draft to review.

**Draft missing.** Path tried: `$S-nodraft/proposal/draft.md` — from the brief's `Draft:` line (`proposal/design-brief.md:3`). No other markdown in repo.
...
No `proposal/review.md` written. Nothing checked.
```

Stops and names `proposal/draft.md` (and the brief line it came from): pass.

Brief `Status: open` (`$S-open`, rc=0, 29 s), final message:

```text
**Review stop — brief not frozen.**

`proposal/design-brief.md` line 4 reads `Status: open`, not `Status: frozen YYYY-MM-DD`. Review needs frozen brief as fixed reference; otherwise rows checked against brief that still move.

Run `/experiment-proposal:design` to finish it.
...
Nothing written. No `proposal/review.md`, no draft edits.
```

Stops and says the brief is not frozen: pass.

## Hand-off (research-grill present)

Detection: turn 1 read `~/.claude/plugins/installed_plugins.json` with the Read tool; the file has the key `"oss@open-science-skills"` (its line 135). The hand-off is the installed form. Turn 2's and turn 3's final messages each end with it, in full, and it is identical to the file's Hand-off section (unchanged by the fixes); turn 1's final message ends with it too:

```text
/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?; item 13.6 passed narrowly, the doubt being that contribution (c) is an artefact rather than something learned, so the whole delta rests on (a) and (b); item 13.9 passed narrowly, the doubt being that Accot and Zhai (1997) is raised only to be set aside, so removing it would not weaken the argument.
```

The seed list holds the fixed question and the two narrow passes with their doubts; there are no waivers. Exact command and seed list, the final message ends with the hand-off in full: pass.

## Harness events

- Turn 4 ("Print the hand-off again.") hit the account's session limit and is not scored. `$S.turn4.meta`: `rc=1 secs=5`. Fields of its result event: `"type": "result"`, `"subtype": "success"`, `"is_error": true`, `"api_error_status": 429`, `"num_turns": 1`, `"duration_ms": 844`, and the result line `You've hit your session limit · resets 3:40am (America/Chicago)`. The `after-fixes` commit predates it, and nothing in this record depends on it.
- Turn 1 had five permission denials. The first is the draft checker run with `--supervisor "Dr. Alice Kim"; echo "EXIT=$?"`, refused for the compound `echo` ("This Bash command contains multiple operations. The following part requires approval: echo "EXIT=$?""). "Dr. Alice Kim" occurs in neither fixture nor anywhere in the plugin: the skill made up the supervisor's name before asking for it, and only the permission guard kept it out of the checker run. The skill then ran the checker without `--supervisor`. The other four were a `cd` and a `grep` into the plugin directory (outside `$S`), a `python3 -c` word count refused for "Newline followed by # inside a quoted argument", and a compound `grep`; none changed the outcome (the skill read `check_proposal.py` with Read instead).

## Notes, outside the bar

- Order: turn 1 wrote the whole review, with 3.1, 5.2, 13.1 and 13.4 as `fail` ("not confirmed") and the mechanics checked against the course defaults, before asking step 2's template question and the attested batch together at the end. SKILL step 2 asks first. The turn 2 answer turned the four rows to `pass: confirmed by the user, 2026-10-15` and touched only 3.1, 3.3, 5.2, 13.1, 13.4, 13.5 and the Summary (diff of `$S.turn1.review.md` against the first pass).
- Cross-section consistency carries two `- pass:` lines beside its one `- fail:` line, and after the fixes Brief against draft carries a `- pass (fix 4 applied):` line among seven `- fail:` lines; the shape gives `- pass: ...` "when there is none". The checker accepts both.

## Pass bar

| Criterion                                                     | Result | Evidence                                                                                                      |
| ------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------- |
| At least 11 of 12 caught, 0 passed                            | pass   | 12 of 12 caught, 0 passed                                                                                     |
| At most two over-failures                                     | pass   | 1 (8.3, the screening form is administered after the task)                                                    |
| Draft checker reports D3, D8, D9 and nothing else             | pass   | three lines in turns 1 and 2: references, bullet list, supervision sentence                                   |
| Every draft-checked pass quotes a passage with its location   | pass   | 48 of 48; borderline 8.9 (period for a semicolon) and the heading quotes at 3.2, 6.4, 12.1                    |
| 13.2 and 13.3 read not checked                                | pass   | both `not checked: defend-stage`                                                                              |
| Checker exits 0 on review.md                                  | pass   | first pass exit 0; after fixes exit 0                                                                         |
| Picked fixes applied alone, affected rows re-checked          | pass   | fixes 4 and 8 (D4, D7); two insertions (one default hunk, two at `-U0`); five allowed review.md lines         |
| Missing-input and not-frozen stops                            | pass   | brief: names it and `/experiment-proposal:design`; draft: names `proposal/draft.md`; open: "brief not frozen" |
| Hand-off (research-grill present), final message ends with it | pass   | exact defend command and seed list at the end of turns 2 and 3                                                |

## Verdict

Run v2-1 of scenario 5: pass. Turn 4's 429 is a harness event outside the bar.
