# Scenario 5 (review on the proposal with 12 planted defects) at 0.2.0, run v2-4

Date: 2026-10-15
Plugin commit: 76e9c28 (`experiment-proposal` 0.2.0), which is also the fixture commit. The fix that matters for this scenario is 76e9c28 itself: the review skill now waits for the user's template values (step 2) and the attested answers (step 3) before running the draft checker or writing review.md, re-reads `~/.claude/plugins/installed_plugins.json` each time it prints the hand-off, and the shape names a resolved finding `- pass (fix N applied): ...`; the draft fixture now gives the demographic questionnaire (Appendix D) right after the consent form. (ed96208, the design fix, does not touch the review skill.) The worktree's HEAD at scoring time is e7dfcb1, a plans-document commit; `git diff --stat 76e9c28 HEAD -- plugins/experiment-proposal docs/research/2026-10-13-experiment-proposal-evals/fixtures` prints nothing, and `git status --porcelain -- plugins/` printed nothing before turn 1 and after the last stop.
Fixtures: `fixtures/proposal-with-defects.md` copied in as `proposal/draft.md`, `fixtures/proposal-with-defects.brief.md` as `proposal/design-brief.md`; key `fixtures/proposal-with-defects.key.md`. Both scratch copies are byte-identical to the fixtures (`diff` of each against its fixture printed nothing before the `fixtures` commit).
Model: `--model opus`, which the stream's init event and every assistant event report as `claude-opus-5`. The init event lists the plugins `experiment-proposal` (path `$P`, version 0.2.0, source `experiment-proposal@inline`; one agent, `experiment-proposal:hci-researcher`) and `oss` (research-grill present). Turn 1's Reads of `references/checklist.md`, `references/review.md` and `.claude-plugin/plugin.json` resolved under `$P`, and the review's header reads `Checklist: experiment-proposal 0.2.0`.
No turn opened the key or any `docs/research` file (a grep of the three streams for `key.md` and `docs/research` finds nothing), and no turn called the `Agent` tool.

## Commands

Setup (the scratch directory did not exist before this run):

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/review-v2-4
mkdir -p "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval && mkdir proposal
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.brief.md "$S/proposal/design-brief.md"
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.md "$S/proposal/draft.md"
cd "$S" && git add -A && git commit -qm fixtures    # 9c79c68
```

The three stop copies were made from `$S` at the `fixtures` commit, before turn 1, with one planted change each in the working tree:

```bash
cp -r "$S" "$S-nobrief" && rm "$S-nobrief/proposal/design-brief.md"     # git status: " D proposal/design-brief.md"
cp -r "$S" "$S-nodraft" && rm "$S-nodraft/proposal/draft.md"            # git status: " D proposal/draft.md"
cp -r "$S" "$S-open" && sed -i 's/^Status: frozen 2026-10-10$/Status: open/' "$S-open/proposal/design-brief.md"
# "$S-open": git diff -U0 shows only line 4, "Status: frozen 2026-10-10" -> "Status: open"
```

Each turn ran through the helper `review-v2-drive.sh "$S" N`, which reads the prompt from `$S.turnN.prompt` and runs, for turn 1:

```bash
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null
```

and for later turns the same command with `--continue` before `--model`. Prompts and exits (`$S.turnN.meta`; agent turns from the result event):

| Turn | Prompt                                                                                                                                                                                 | Exit, wall time        |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| 1    | `/experiment-proposal:review`                                                                                                                                                          | rc=0, 138 s (6 turns)  |
| 2    | "Template values: accept the course's defaults, with the citation style "author-year, as the draft uses" and the supervisor "the course instructor". Confirm 3.1, 5.2, 13.1 and 13.4." | rc=0, 450 s (17 turns) |
| 3    | "Apply fixes 6 and 9."                                                                                                                                                                 | rc=0, 66 s (12 turns)  |

No turn's result event carries `api_error_status` (each reads `"subtype": "success"`, `"is_error": false`).

Commits in `$S` between turns:

```bash
cd "$S" && git add -A && git commit -qm first-pass    # after turn 2: a492e5b
cd "$S" && git add -A && git commit -qm after-fixes   # after turn 3: adf86fc
```

The stops ran with the turn 1 command, `S` replaced by the copy (`review-v2-drive.sh "$S-nobrief" 1`, and so on), one after the other.

Scoring commands (temporary files in a scratch directory outside the repository):

```bash
T=/tmp/ep-eval-score-v2-4
git -C "$S" show a492e5b:proposal/review.md > "$T/first-pass-review.md"     # commit "first-pass"
git -C "$S" show adf86fc:proposal/review.md > "$T/after-fixes-review.md"    # commit "after-fixes"
python3 "$P/scripts/check_proposal.py" review "$T/first-pass-review.md"; echo "exit=$?"
python3 "$P/scripts/check_proposal.py" review "$T/after-fixes-review.md"; echo "exit=$?"
git -C "$S" show 9c79c68:proposal/draft.md > "$T/fixture-draft.md"
python3 "$P/scripts/check_proposal.py" draft "$T/fixture-draft.md" --words 2000-4000 --references 15-20 --supervisor "the course instructor"; echo "exit=$?"
git -C "$S" diff -U0 a492e5b adf86fc
git -C "$S" diff --word-diff=plain -U0 a492e5b adf86fc -- proposal/draft.md
```

## The waits

Turn 1 waited. Its tool calls were five Reads and nothing else: the brief, `references/checklist.md`, `references/review.md`, `.claude-plugin/plugin.json`, the draft. No Bash call, so no draft checker run; no Write or Edit, so no review.md (after turn 1, `$S/proposal` held only `design-brief.md` and `draft.md`, and `git status --porcelain` printed nothing). It asked for the supervisor's name instead of making one up (v2-1's turn 1 had tried to run the checker with an invented name). Both questions came in the one message, and one answer covered both. The final message, in full:

```text
Draft and brief read. One big thing surfaced already: brief has **device between subjects**; draft makes it **within**. That reshapes Design, Procedure, Participants, and the consent form. Flagging now so you can decide before picking fixes.

Need your values before I run the mechanics checker:

**1. Template mechanics** (course defaults shown — reply "defaults" to take all):
- Sections in order: Introduction, Literature review, Research questions or Hypotheses, Participants, Materials, Procedure, Design, Appendix
- Body words: 2,000–4,000, excluding references and appendices
- References: 15–20
- Citation style: the template's; ACM reference format for CHI
- Supervising instructor's name: **?** (no default — need it)

Note: draft's reference list is author–date, not ACM numbered. Confirm the style you actually submit in; ACM would fail every entry.

**2. Attested items** (need an answer each):
- **5.2** Snowballing from a recent key article stopped turning up new relevant work? Brief's Open items still says "Run `/experiment-proposal:lit-search` for a current-device comparison to cite under H1" — so did it actually stop?
- **13.1** Proposal reviewed against the seven reader questions (importance, credibility, ethics, novelty, external validity, assumptions, readability) and revised where short?
- **13.4** Can you give the reason for every Design choice? (brief rationales are the record)
```

Item 3.1 was asked as the template question only, not again in the attested batch; turn 2's answer confirmed 3.1 with the other three. The opening paragraph reports the within-or-between departure from reading alone, before any value was given; nothing was written or run on it.

## The draft checker, with the user's values

Turn 2, the first call after the answer (the absolute plugin path written as `$P`):

```bash
python3 "$P/scripts/check_proposal.py" draft proposal/draft.md --words 2000-4000 --references 15-20 --supervisor "the course instructor"; echo "EXIT=$?"
```

The permission guard refused it for the compound `echo` ("This Bash command contains multiple operations. The following part requires approval: echo "EXIT=$?""), the same refusal as in v2-1. The skill then read `~/.claude/plugins/installed_plugins.json` and ran the same command without the `echo`: every value is the one the user gave, and no `--sections` because the default list was accepted. Output, exit 1:

```text
proposal/draft.md:67: references: 14 entries; the template asks for 15 to 20
proposal/draft.md:3: introduction: no bullet list of contributions
proposal/draft.md:1: appendix: no consent sentence saying the study is under the supervision of the instructor
```

Turn 3 ran the same command again after the two edits and got the same three lines. A scoring re-run of the command on the fixture copy (`$T/fixture-draft.md`) also printed those three lines, exit 1. No sections line and no word-count line; the review records "the section list and the body word count hold" (row 13.5). The mechanics report D8, D3 and D9, nothing else: pass.

## Scoring against the key (first pass: review.md at commit a492e5b, after turn 2)

First-pass Summary line: `Items checked: 65. Pass: 52. Fail: 13. Not checked (defend-stage): 2. Consistency and brief findings: 12. Fixes proposed: 13. Waivers: 0.` Every count recomputes from the rows: 67 rows (61 under Items, 6 under Substance tests), 65 not `not checked`; 47 Items rows plus 5 substance rows read `pass` or `pass narrowly` (52); 12 plus 1 read `fail` (13); 2 `- fail` lines under Cross-section consistency and 10 under Brief against draft (12); highest fix number 13. The seven sections are in the shape's order.

### D1 to D12

| Defect | Item or section                    | The row's reason (quoted)                                                                                                                                                                                                                                                                                                                          | Verdict |
| ------ | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| D1     | 1.3                                | fail: "the data plan gives the screening reason and names the author as the only person with access, but never says how long the raw data are kept." (fix 1)                                                                                                                                                                                       | caught  |
| D2     | 6.2                                | fail: "H2 names its variables and direction but cites no source for that direction, while H1 and H3 do." (fix 4)                                                                                                                                                                                                                                   | caught  |
| D3     | 4.3 (and the draft checker)        | fail: "the contributions run inline as (a), (b) and (c) rather than as a bullet list; the checker reports "introduction: no bullet list of contributions"." (fix 2)                                                                                                                                                                                | caught  |
| D4     | 7.5                                | fail: "the device order is counterbalanced, but neither Design nor Procedure states the order of the nine distance-and-size combinations within a device." (fix 6)                                                                                                                                                                                 | caught  |
| D5     | 7.6                                | fail: "error rate carries a construct statement, "it measures selection accuracy, the complement of the speed measure", but movement time has only a reliability statement and no construct-validity statement." (fix 7)                                                                                                                           | caught  |
| D6     | 8.2                                | fail: "the recruitment method is stated, but nothing says how candidates can decline without consequence, which matters where the author recruits from their own course section." (fix 8)                                                                                                                                                          | caught  |
| D7     | 10.5                               | fail: "nothing says what happens if the experimenter falls ill or the equipment breaks down." (fix 9)                                                                                                                                                                                                                                              | caught  |
| D8     | 5.1 (and the draft checker)        | fail: "the review cites motivating, justifying and similar work, but the list holds 14 entries against the template's 15 to 20." (fix 3, a decide naming `/experiment-proposal:lit-search`); checker "references: 14 entries; the template asks for 15 to 20"                                                                                      | caught  |
| D9     | 12.3 (and the draft checker)       | fail: "the consent form states 20 minutes against the 35-minute estimate, names no supervising instructor, gives no retention period, ..." (fix 10, whose consent text adds "under the supervision of the course instructor"); checker "appendix: no consent sentence saying the study is under the supervision of the instructor"                 | caught  |
| D10    | 12.5                               | fail: "the script has no point at which participants can ask questions." (fix 11)                                                                                                                                                                                                                                                                  | caught  |
| D11    | 12.3 and Cross-section consistency | 12.3: "the consent form states 20 minutes against the 35-minute estimate"; Cross-section: "fail: the session duration differs: 35 minutes in Procedure ("The durations sum to the session estimate of 35 minutes.") and in Appendix A ("a 35-minute study of pointing devices"), but "it takes about 20 minutes" in Appendix B, the consent form." | caught  |
| D12    | Brief against draft, entry 7.1     | "fail: item 7.1, device. The brief: "device between subjects; distance and size within subjects, 128/256/512 pixels and 16/32/64 pixels." The draft, Design para 1: "Device: the mouse or the trackball named in Materials, within subjects". The distances and sizes match. fix 5."                                                               | caught  |

Caught 12 of 12, passed 0. Row 12.3 reports both of its reasons (D9 and D11) and counts for both, as the key allows. D12 is scored on the Brief against draft section alone; the 7.1 row reads `pass narrowly`, its doubt naming the brief's between-subjects decision, which the key does not consult.

The Brief against draft section's other `- fail` lines are 7.2, 7.3, 7.4 and 8.5 ("The brief: "24 (12 per device)"") from the between-subjects brief, 7.5 (D4 seen from the brief), and 1.3, 6.2 and 7.6 (restating D1, D2 and D5): all expected by the key, none an over-failure. It also fails 7.9 ("The brief: "history (same weeks, similar times)"" against the within-session prevention, "a prevention that depends on the within-subjects design"), the same between-or-within departure seen from the history remedy; 7.9's row under Items is a control and reads `pass narrowly`, so the line is not scored. Findings beyond the key that are not control rows: row 7.2 fails (the carry-over is called symmetric against the brief's asymmetric; the decide, fix 5, names `/experiment-proposal:design`), substance test 13.9 fails (Accot and Zhai (1997) "cited then declared irrelevant"; fix 13), and Cross-section consistency adds "the incentive differs: "Participants who complete the session will receive course credit." (Participants, para 2) against "there is no payment" (Appendix B)", a real tension in the fixture that row 12.3 also names. None counts either way.

### Controls

The 38 controls (1.1, 1.2, 2.2 to 2.5, 3.2, 3.3, 4.1, 4.2, 4.4, 4.5, 5.3, 6.1, 6.3, 6.5, 6.6, 7.7, 7.8, 7.9, 8.1, 8.3, 8.4, 8.5, 8.8, 8.9, 9.1 to 9.4, 10.1 to 10.4, 12.1, 12.2, 12.4, 12.6): all 38 pass, 35 as `pass` and 3 as `pass narrowly` (3.3: the combination order is not stated, item 7.5; 7.9: the history prevention holds only under the within-subjects design; 10.3: the program and the display are not named at a phase). 0 over-failures.

Control 10.2, with the questionnaire now between consent and instructions, passes; the row, verbatim:

```text
- **10.2** pass: "welcome (2 minutes); the consent form (Appendix B), read and signed (5 minutes); the demographic questionnaire (Appendix D), which screens for the profile and excuses anyone outside it (2 minutes); scripted instructions, read from the script (Appendix C) in a neutral tone (3 minutes)" (Procedure, para 1; the seven durations sum to the 35-minute estimate)
```

It quotes the order as the draft gives it and says nothing about the checklist's parenthetical order (questionnaires after tasks); it does not treat the early questionnaire as a defect. Control 8.3, v2-1's over-failure on the pre-76e9c28 ordering (screening after the second device), now passes: "screened by a short form (Appendix D) for handedness and age. No eligibility criterion selects people for an extreme score on pointing performance." (Participants, para 1); see the quotes section for what this quote leaves out.

### Quotes on draft-checked passes

48 draft-checked rows pass or pass narrowly (43 under Items, five substance tests); the four attested passes (3.1, 5.2, 13.1, 13.4) read `confirmed by the user, 2026-10-15`. Every one of the 48 carries a quoted passage followed by its location in parentheses. Checked mechanically against the draft (whitespace normalised, mdformat's escaped underscores unescaped): 47 quotes occur in the draft as one contiguous passage, none is longer than two sentences, and 12.6's `"Age: ____ Handedness: ____"` matches with the underscores unescaped, which the key accepts. Exceptions and borderlines:

- 8.3 quotes "screened by a short form (Appendix D) for handedness and age. No eligibility criterion selects people for an extreme score on pointing performance." The two sentences are each verbatim but not adjacent: the draft has "They are a convenience sample, so the results describe right-handed young adults only cautiously." between them, and the quote marks no omission. Turn 2's Write had the contiguous pair (the screening clause and the convenience-sample sentence); an Edit later in the same turn swapped the second sentence for the eligibility one. The quote has a location and the words are the draft's, so the key's "quotes a passage with its location" holds; SKILL step 3's "verbatim" does not hold for the passage as a unit. This is a sharper departure than v2-1's 8.9 (a period for a semicolon).
- 3.2 quotes the heading "## Research questions or Hypotheses" (heading 3, between Literature review and Participants), a heading line as the passage, as in v2-1.

### 13.2 and 13.3

Both rows read `not checked: defend-stage`.

### The checker on the first pass

```text
$ python3 "$P/scripts/check_proposal.py" review "$T/first-pass-review.md"; echo "exit=$?"
exit=0
```

Inside turn 2 the skill's first checker run reported one line, `proposal/review.md:28: fix 13 appears before fix 4; fixes are numbered in order of appearance` (row 5.1 named fix 13 in its decide); it reworded the row and the next run printed nothing. It then made six wording edits (fix 5's appendix list, the 8.3 quote, fix 8's text, fix 10's brackets) and ran the checker a third time, with no output.

## Fix-picking check

D4 is row 7.5, fix 6; D7 is row 10.5, fix 9, in the first-pass file. Turn 3's prompt was "Apply fixes 6 and 9.": the right two numbers.

The draft, `git -C "$S" diff -U0 a492e5b adf86fc -- proposal/draft.md`: two hunks, `@@ -49 +49 @@` (Procedure, para 2) and `@@ -53 +53 @@` (Design, para 1); at the default three lines of context git shows them as one hunk, `@@ -46,11 +46,11 @@`, as in v2-1, which is why the key now counts at `-U0`. `--word-diff=plain -U0` shows two insertions and no deletions, and a character-level comparison confirms each changed line is the old line with one sentence inserted and nothing removed:

```text
{+If the experimenter falls ill or the equipment fails, the affected session will be rescheduled within the data-collection weeks; a spare mouse and trackball of the same models will be kept in room 204, and a replacement unit will be re-checked against the log before the next session.+}
{+nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software with equal counts per combination. The+}
```

(The second is the sentence "The nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software with equal counts per combination." inserted after "H3's interaction has its variables crossed."; word-diff aligns the following "The" differently.) Each insertion is its fix's quoted text, word for word, at the place the fix names: fix 9, "add to Procedure", at the end of Procedure para 2; fix 6, "add to Design, para 1".

`proposal/review.md`, `git -C "$S" diff -U0 a492e5b adf86fc -- proposal/review.md`: six changed lines; Waivers and Hand-off are unchanged.

| Line | What changed                                                                 | Allowed by the key                     |
| ---- | ---------------------------------------------------------------------------- | -------------------------------------- |
| 18   | row 3.3, `pass narrowly` to `pass (fix 6 applied)`                           | no (see below)                         |
| 41   | row 7.5, fail to `pass (fix 6 applied)`                                      | yes, the 7.5 row                       |
| 61   | row 10.5, fail to `pass (fix 9 applied)`                                     | yes, the 10.5 row                      |
| 73   | row 13.5, "eleven items" to "nine items", remaining fixes listed, still fail | yes, the 13.5 row                      |
| 87   | Brief against draft entry 7.5, `- fail:` to `- pass (fix 6 applied):`        | yes, a Brief finding the fixes touched |
| 105  | Summary                                                                      | yes, the Summary                       |

The re-checked rows:

```text
- **7.5** pass (fix 6 applied): "The nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software with equal counts per combination." (Design, para 1)
- **10.5** pass (fix 9 applied): "If the experimenter falls ill or the equipment fails, the affected session will be rescheduled within the data-collection weeks; a spare mouse and trackball of the same models will be kept in room 204, and a replacement unit will be re-checked against the log before the next session." (Procedure, para 2)
- pass (fix 6 applied): item 7.5, counterbalancing. The brief: "the nine distance-and-size combinations in a random order per participant, drawn by the software with equal counts per combination." The draft, Design para 1, now states the same: "The nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software with equal counts per combination."
```

Both rows read `<result> (fix N applied)` and quote the new passage, verbatim in the after-fixes draft. The Brief line uses the shape 76e9c28 added, `- pass (fix N applied): ...`.

Row 3.3 is outside the key's list. Before and after:

```text
- **3.3** pass narrowly: "a statistically significant advantage for the mouse supports it" (Research questions or Hypotheses, para 2); the doubt: the Method is not fully replicable from its own text, because neither Design nor Procedure states the order in which the nine distance-and-size combinations are presented (item 7.5).
- **3.3** pass (fix 6 applied): "a statistically significant advantage for the mouse supports it" (Research questions or Hypotheses, para 2); with the combination order now stated in Design, each Method section is replicable from its own text.
```

This misses the key's literal "every other row is byte-identical". It is the re-check SKILL step 6 asks for ("Re-check the items they touch"), and the README's scenario 5 row asks for the same ("picked fixes applied alone with the affected rows re-checked"): 3.3's doubt named item 7.5's missing order, which fix 6 supplies. The result class stays a pass (a narrow pass counts as a pass), the quote is unchanged, and no count moves on its account (Pass 52 to 54 is 7.5 and 10.5 alone). The key's allowed list names the 7.5, 10.5 and 13.5 rows and the touched Cross-section or Brief findings, but no Items row whose narrow-pass doubt a fix settles; that is a gap in the key, reported to the controller. Scored on what the check guards (the picked fixes applied alone, no unrelated row altered), the fix-picking check passes, with this miss of the literal clause recorded.

Key correction: the key as written at 76e9c28 would have failed this run on row 3.3; the plan's author corrected the key's fix-picking sentence to match review step 6 ("Re-check the items they touch"), plan commit 2ff28f5, key commit ea99fd2, so the fix-picking check passes.

Summary after the fixes: `Items checked: 65. Pass: 54. Fail: 11. Not checked (defend-stage): 2. Consistency and brief findings: 11. Fixes proposed: 13. Waivers: 0.`, every count recomputed from the rows (fixes 6 and 9 stay counted, so the highest fix number is still 13). Turn 3 ran the checker on its own rewrite ("(Bash completed with no output)"). Scoring re-run:

```text
$ python3 "$P/scripts/check_proposal.py" review "$T/after-fixes-review.md"; echo "exit=$?"
exit=0
```

## Missing-input and not-frozen stops

No stop project holds a `proposal/review.md` afterwards, and `git status --porcelain` in each shows only its planted change: nothing was written. No result event carries `api_error_status`.

Brief deleted (`$S-nobrief`, rc=0, 9 s, 2 turns), final message:

```text
No design brief at proposal/design-brief.md; run /experiment-proposal:design first.

Draft exist at `proposal/draft.md`, but review need frozen brief as evidence baseline. Nothing written.
```

Stops, names the brief and `/experiment-proposal:design`: pass.

Draft deleted (`$S-nodraft`, rc=0, 15 s, 4 turns), final message (the scratch path written as `$S-nodraft`):

```text
Stop. No draft to review.

Brief at `proposal/design-brief.md` present and frozen 2026-10-10. Its `Draft:` line points to `proposal/draft.md` — that file does not exist. Tried:

- `$S-nodraft/proposal/draft.md` — missing

No other draft file in repo either. Write the draft at that path (or name a different path when you re-run `/experiment-proposal:review`), then review runs.
```

Stops and names `proposal/draft.md` (and the brief's `Draft:` line it came from): pass.

Brief `Status: open` (`$S-open`, rc=0, 36 s, 5 turns), final message:

```text
Brief not frozen. Stop.

`proposal/design-brief.md` line 4 reads `Status: open`, not `frozen YYYY-MM-DD`. Review needs frozen brief — Brief-against-draft and item 13.4 both read it as fixed record.

Run `/experiment-proposal:design` to finish it.

Still open likely because of brief's one Open item: run `/experiment-proposal:lit-search` for current-device comparison to cite under H1.

Nothing written, draft untouched.
```

Stops and says the brief is not frozen: pass.

## Hand-off (research-grill present)

Detection: `~/.claude/plugins/installed_plugins.json` has the key `"oss@open-science-skills"` (its line 145). Turn 2 read the whole file with the Read tool before writing review.md ("research-grill installed (`oss@`)."); turn 3 read it again (offset 144, limit 10, which shows the `oss@` key) after its last checker run and immediately before printing the hand-off: the per-print re-read that 76e9c28 added held. Turn 1 printed no hand-off and did not read the file.

Turn 3, the last pass message, ends with the hand-off in full, in a `text` fence, the last thing in the message, and identical to the file's Hand-off section (unchanged by the fixes):

```text
/oss:research-grill defend proposal/draft.md
Seed list: no waivers; could someone run a session from the Method alone?; no substance test passed narrowly.
```

The installed form: the exact defend command and the seed list. There are no waivers and no substance test passed narrowly (the narrow passes are items 7.1, 7.9 and 10.3, and before the fix 3.3, none a substance test), so the seed list holds the fixed question with the words "no waivers" and "no substance test passed narrowly" standing where the shape puts `<each waiver>` and `<each substance test passed narrowly>`.

Turn 2, which wrote review.md and ended the first pass, did not end with the hand-off: its final message ends with the paragraph "Fix 5 gates fixes 6, 7, 9 and 10 — they are written in the within-design's terms; going between means a second pass over those rows." and then the line "Which fixes should I apply? Give their numbers.", and nowhere mentions research-grill. SKILL step 7 says "End every message that ends a pass with the hand-off text itself, in full"; v2-1's turn 2 did. The hand-off was in the file, but not in the message: a step 7 miss on the first-pass message, outside scenario 5's bar (it is scenario 6's criterion).

## Harness events

- No turn hit the rate limit.
- Turn 2 had two permission denials: the draft checker with the compound `echo "EXIT=$?"` (re-run without it, see above), and a `cd` into `$P/scripts` with a piped `grep` (the skill read `check_proposal.py` with Read instead). The `$S-open` stop had one: a compound `ls` and `cat` of `$P/.claude-plugin/plugin.json`. None changed an outcome.

## Pass bar

| Criterion                                                   | Result | Evidence                                                                                                                                           |
| ----------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| At least 11 of 12 caught, 0 passed                          | pass   | 12 of 12 caught, 0 passed                                                                                                                          |
| At most two over-failures                                   | pass   | 0 of 38 controls fail; 10.2 passes with the questionnaire after consent; 8.3 passes                                                                |
| Draft checker reports D3, D8, D9 and nothing else           | pass   | three lines in turns 2 and 3, run with the user's values: references, bullet list, supervision sentence                                            |
| Every draft-checked pass quotes a passage with its location | pass   | 48 of 48; 8.3 joins two non-adjacent sentences with no omission mark; 3.2 quotes a heading                                                         |
| 13.2 and 13.3 read not checked                              | pass   | both `not checked: defend-stage`                                                                                                                   |
| Checker exits 0 on review.md                                | pass   | first pass exit 0; after fixes exit 0                                                                                                              |
| Picked fixes applied alone, affected rows re-checked        | pass   | fixes 6 and 9 (D4, D7); two insertions, two hunks at `-U0`; 7.5 and 10.5 read `pass (fix N applied)`; row 3.3 also changed, outside the key's list |
| Missing-input and not-frozen stops                          | pass   | brief: names it and `/experiment-proposal:design`; draft: names `proposal/draft.md`; open: "Brief not frozen. Stop."                               |

Also recorded, as the brief for this run asks:

| Check                                             | Result | Evidence                                                                                       |
| ------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------- |
| Turn 1 waited: no review.md, no draft checker run | yes    | five Reads, no Bash, no Write; asked for the supervisor's name                                 |
| Draft checker run with the user's values          | yes    | `--words 2000-4000 --references 15-20 --supervisor "the course instructor"`, after the answer  |
| Hand-off ends the last pass message in full       | yes    | turn 3 ends with the installed hand-off in a `text` fence, identical to the file; file re-read |
| Hand-off ends the first-pass message              | no     | turn 2 ends with "Which fixes should I apply? Give their numbers."                             |

## Verdict

Run v2-4 of scenario 5 at 76e9c28: pass. Outside the bar: row 3.3 was re-checked and changed by fix 6, against the key's literal byte-identical clause (a gap in the key's allowed list); the 8.3 quote is not one contiguous passage; turn 2's first-pass message did not end with the hand-off.
