# Scenario 5 (review on the proposal with 12 planted defects) at 0.2.0, run v2-6

Date: 2026-10-15
Plugin commit: 76e9c28 (`experiment-proposal` 0.2.0), which is also the fixture commit. The fix that matters for this scenario is 76e9c28 itself: `review` now waits for the template values (step 2) and the attested answers (step 3) before running the draft checker or writing review.md, re-reads the plugins file at each hand-off, and the shape names a resolved finding (`- pass (fix N applied): ...`); the draft fixture now has the questionnaire (Appendix D) screen right after the consent form. The design fix ed96208 does not touch `review`: `git show --stat ed96208` lists only `plugins/experiment-proposal/skills/design/SKILL.md` and `tests/test_experiment_proposal_plugin.py`. The worktree's HEAD at scoring time is 76e9c28, and `git diff --stat 76e9c28 HEAD -- plugins/experiment-proposal docs/research/2026-10-13-experiment-proposal-evals/fixtures` and `git status --porcelain` on the same paths print nothing.
Fixtures: `fixtures/proposal-with-defects.md` copied in as `proposal/draft.md`, `fixtures/proposal-with-defects.brief.md` as `proposal/design-brief.md`; key `fixtures/proposal-with-defects.key.md`. Both scratch copies are byte-identical to the fixtures (`diff` of each fixture against `git -C "$S" show fbcaf6c:<file>` prints nothing).
Model: `--model opus`, which the init event of every stream reports as `claude-opus-5`. The init event lists the plugins `experiment-proposal` and `oss` (research-grill present); the 0.2.0 copy under `$P` is the one that ran, since turn 1's Reads of `references/checklist.md`, `references/review.md` and `.claude-plugin/plugin.json` resolved under `$P`, and the review's header reads `Checklist: experiment-proposal 0.2.0`.
Driver: this run was driven and scored in one session; every turn finished with `"is_error": false` and `"api_error_status": null`, so no rate limit was hit.

## Commands

Setup:

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/review-v2-6
mkdir "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval && mkdir proposal
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.brief.md proposal/design-brief.md
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.md proposal/draft.md
git add -A && git commit -qm fixtures    # fbcaf6c
```

The three stop copies were made straight after the `fixtures` commit, before turn 1, so each holds only that commit and one planted change:

```bash
for x in nobrief nodraft open; do cp -a "$S" "$S-$x"; done
cd "$S-nobrief" && rm proposal/design-brief.md                                          # git status: " D proposal/design-brief.md"
cd "$S-nodraft" && rm proposal/draft.md                                                 # git status: " D proposal/draft.md"
cd "$S-open" && sed -i '4s/^Status: frozen 2026-10-10$/Status: open/' proposal/design-brief.md   # git status: " M proposal/design-brief.md"
```

Each turn ran through the helper `bash /tmp/ep-eval/review-v2-drive.sh "$S" N`, which reads the prompt from `$S.turnN.prompt` and runs, for turn 1:

```bash
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null
```

and for later turns the same command with `--continue` before `--model`. Prompts and exits (`$S.turnN.meta`, and the result event's `num_turns`):

| Turn | Prompt                                                                                                                                                                                 | Exit, wall time        |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| 1    | `/experiment-proposal:review`                                                                                                                                                          | rc=0, 32 s (7 turns)   |
| 2    | "Template mechanics: accept the course's defaults, with the citation style author-year, as the draft uses, and the supervisor the course instructor. Confirm 3.1, 5.2, 13.1 and 13.4." | rc=0, 518 s (15 turns) |
| 3    | "Apply fixes 5 and 8."                                                                                                                                                                 | rc=0, 64 s (11 turns)  |

Turn 1 asked both batches in one message, so one answer (turn 2) carried both the template values and the attested confirmations. Commits in `$S` between turns:

```bash
cd "$S" && git add -A && git commit -qm first-pass    # after turn 2: b49897b
cd "$S" && git add -A && git commit -qm after-fixes   # after turn 3: bc8b28d
```

The three stops, each one turn with the turn 1 command and `S` replaced by the copy, run in parallel:

```bash
cd "$S-nobrief" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review" > "$S-nobrief.turn1.jsonl" 2> "$S-nobrief.turn1.err" < /dev/null
# likewise "$S-nodraft" and "$S-open"
```

Scoring commands (temporary files outside the repository):

```bash
T=/tmp/ep-eval/v2-6-score
git -C "$S" show b49897b:proposal/review.md > "$T/first-pass-review.md"     # commit "first-pass"
git -C "$S" show bc8b28d:proposal/review.md > "$T/after-fixes-review.md"    # commit "after-fixes"
python3 "$P/scripts/check_proposal.py" review "$T/first-pass-review.md"; echo "exit=$?"
python3 "$P/scripts/check_proposal.py" review "$T/after-fixes-review.md"; echo "exit=$?"
python3 "$P/scripts/check_proposal.py" draft "$T/draft-fixtures.md" --words 2000-4000 --references 15-20 --supervisor "the course instructor"; echo "exit=$?"
git -C "$S" diff b49897b bc8b28d -- proposal/draft.md
git -C "$S" diff -U0 b49897b bc8b28d
git -C "$S" diff --word-diff=plain -U0 b49897b bc8b28d -- proposal/draft.md
```

plus a scoring script (`$T/quotes.py`) that parses every row under Items and Substance tests, checks each quoted passage on a pass against the draft verbatim (with `\_` unescaped), counts its sentences, checks a parenthesised location follows it, and lists any of the 38 controls that does not pass; and a second one that recomputes the Summary counts from the rows.

## The waits (turn 1)

Turn 1 waited. Its tool calls were six Reads and nothing else: `references/checklist.md`, `references/review.md`, `proposal/design-brief.md`, `.claude-plugin/plugin.json`, `proposal/draft.md`, and `~/.claude/plugins/installed_plugins.json`. It made no Bash call, so it ran no draft checker, and it wrote nothing: after turn 1, `proposal/` held only the two fixtures and `git status --porcelain` was empty. Its final message asked step 2's question and step 3's batch together:

```text
Brief frozen 2026-10-10, draft read. Before checking, two batches of questions.

**Template mechanics (item 3.1)** — confirm or correct these course defaults:
- Sections, in order: Introduction, Literature review, Research questions or Hypotheses, Participants, Materials, Procedure, Design, Appendix
- Body words: 2,000–4,000, excluding references and appendices
- References: 15–20
- Citation style: template's (ACM reference format for CHI)
- Supervising instructor's name: **?** (no default — need it)

**Attested items** — answer each:
- **3.1**: values above correct?
- **5.2**: snowballing from a recent key article stopped turning up new relevant work?
- **13.1**: proposal reviewed against the seven reader questions (importance, credibility, ethics, novelty, external validity, assumptions, readability) and revised where short?
- **13.4**: can you give the reason for every Design-section choice?
```

It added a flag that the draft's device is within subjects against the brief's between subjects. It did not invent a supervisor name: a grep of the three main streams for `Dr. ` followed by a name finds nothing (run v2-1's turn 1 had tried `--supervisor "Dr. Alice Kim"`).

## The draft checker, with the user's values

The draft checker ran only in turn 2, after the answer, with the user's values: the course defaults for the bounds and the supervisor as the user gave it. The first attempt carried a trailing `; echo "EXIT:$?"` and the permission guard refused it ("This Bash command contains multiple operations. The following part requires approval: echo "EXIT:$?""). The skill then ran it bare:

```text
$ python3 "$P/scripts/check_proposal.py" draft proposal/draft.md --words 2000-4000 --references 15-20 --supervisor "the course instructor"
Exit code 1
proposal/draft.md:67: references: 14 entries; the template asks for 15 to 20
proposal/draft.md:3: introduction: no bullet list of contributions
proposal/draft.md:1: appendix: no consent sentence saying the study is under the supervision of the instructor
```

It passed no `--sections`, because the confirmed list is the default, as the skill says. `--supervisor` changes nothing here: the draft has no supervision sentence, so the checker's "no consent sentence" line fires before any name comparison (`check_proposal.py` lines 747 to 752). Turn 3 re-ran the same command on the fixed draft and got the same three lines (references now at line 69). A scoring re-run on the fixture copy printed the same three lines, exit 1.

## Decisive transcript lines

Turn 2, final message (the opening; the hand-off follows):

```text
Review written: `proposal/review.md`. Checker exits 0.

**Items checked: 65. Pass: 54. Fail: 11. Not checked (defend-stage): 2. Consistency and brief findings: 10. Fixes proposed: 12. Waivers: 0.**

Mechanics: sections and body word count pass. Three mechanics defects — 14 references (needs 15), contributions in prose not bullets, no supervision sentence in the consent form.
...
Which fixes should I apply? Give their numbers.
```

Turn 3, final message (before the hand-off):

```text
Fixes 5 and 8 applied to `proposal/draft.md`; nothing else in the draft touched.

- **Design, para 1** — added the nine-combination random order with equal counts.
- **Procedure** — added a third paragraph: reschedule rather than hand the session to a second experimenter, plus spare devices and a second computer.

One note on fix 8: I dropped the bracketed reminder rather than paste an editorial note into a submittable draft. The draft now asserts the spares exist — confirm that before week 4, or soften the sentence.

Re-checked: **7.5 pass (fix 5 applied)**, **10.5 pass (fix 8 applied)**, the brief's 7.5 departure now **pass (fix 5 applied)**. **13.5 still fails** — eight items of steps 1 to 12 remain (1.3, 4.3, 5.1, 6.2, 7.6, 8.2, 12.3, 12.5) and the three mechanics defects are unchanged: 14 references, contributions in prose, no supervision sentence. Body word count still in bounds; the draft checker reports the same three lines and nothing new.
```

No turn opened the key or any `docs/research` file (a grep of the three main streams for `key.md` and `docs/research` finds nothing), and no turn called the `Agent` tool.

## Scoring against the key (first pass: review.md at commit b49897b, after turn 2)

First-pass Summary line: `Items checked: 65. Pass: 54. Fail: 11. Not checked (defend-stage): 2. Consistency and brief findings: 10. Fixes proposed: 12. Waivers: 0.` Every count recomputes from the rows: 65 rows not `not checked`, 54 `pass` or `pass narrowly`, 11 `fail`, 10 `- fail` lines (2 under Cross-section consistency, 8 under Brief against draft), highest fix number 12. The file has 67 rows, one per checklist item, and the seven sections in the shape's order.

### D1 to D12

| Defect | Item or section                    | The row's reason (quoted)                                                                                                                                                                                                                                                                                                            | Verdict |
| ------ | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| D1     | 1.3                                | fail: "the data plan gives the minimization reason and the access list but never says how long the raw data are kept (the brief sets five years)." (fix 1)                                                                                                                                                                           | caught  |
| D2     | 6.2                                | fail: "H2 names its variables and direction but cites nothing, so the predicted direction for error rate is unjustified" (fix 4)                                                                                                                                                                                                     | caught  |
| D3     | 4.3 (and the draft checker)        | fail: "the three contributions are run together in a sentence, not listed as bullets" (fix 2); checker "introduction: no bullet list of contributions"                                                                                                                                                                               | caught  |
| D4     | 7.5                                | fail: "the device order is counterbalanced, but the order of the nine distance-and-size combinations within a device is never stated." (fix 5)                                                                                                                                                                                       | caught  |
| D5     | 7.6                                | fail: "movement time carries no construct-validity statement and error rate no reliability statement" (fix 6)                                                                                                                                                                                                                        | caught  |
| D6     | 8.2                                | fail: "the recruitment method is stated, but nothing says how a candidate can decline without consequence, which matters most here because recruiting runs through the author's own course section." (fix 7)                                                                                                                         | caught  |
| D7     | 10.5                               | fail: "nothing says what happens if the experimenter falls ill or the equipment breaks down." (fix 8)                                                                                                                                                                                                                                | caught  |
| D8     | 5.1 (and the draft checker)        | fail: "the reference list holds 14 entries and the template asks for 15 to 20." (fix 3, a decide naming `/experiment-proposal:lit-search`); checker "references: 14 entries; the template asks for 15 to 20"                                                                                                                         | caught  |
| D9     | 12.3 (and the draft checker)       | fail: "no supervision sentence (the checker reports "appendix: no consent sentence saying the study is under the supervision of the instructor")" (fix 9)                                                                                                                                                                            | caught  |
| D10    | 12.5                               | fail: "the script never gives participants a point at which they can ask questions." (fix 10)                                                                                                                                                                                                                                        | caught  |
| D11    | 12.3 and Cross-section consistency | 12.3: "a duration of about 20 minutes against the 35-minute estimate"; Cross-section: "fail: the session duration is 35 minutes in Procedure, para 1, in the pilot sentence of Participants, para 2 and in the Appendix A announcement, but "about 20 minutes" in the Appendix B consent form."                                      | caught  |
| D12    | Brief against draft, entry 7.1     | "fail: item 7.1. The brief has "device between subjects; distance and size within subjects", with the rationale that daily mouse users bring asymmetric habits; the draft has "Device: the mouse or the trackball named in Materials, within subjects, ..." (Design, para 1). fix 12: decide: run `/experiment-proposal:design` ..." | caught  |

Caught 12 of 12, passed 0. Row 12.3 reports both of its reasons (D9 and D11) and counts for both, as the key allows; it also lists the retention period, the consequence of withdrawing, a benefits statement and "there is no payment" against the course credit. D12 is scored on the Brief against draft section alone; the 7.1 row reads pass ("though the label for device departs from the brief (see Brief against draft)"), which the key does not consult.

The Brief against draft section holds eight `- fail` lines: 1.3, 6.2, 7.1, 7.2, 7.3, 7.4, 7.5 and 8.5 ("The brief's count is "24 (12 per device)""). Each is a departure the key expects (1.3 and 6.2 restating D1 and D2, 7.2 to 7.4 and 8.5 from the between-subjects brief, 7.5 as D4 seen from the brief); none counts as over-failing. It gives no line for 7.6 (the brief's "construct-valid" against the draft's silence), which the key says the section will report; D5 is caught at row 7.6, so nothing turns on it. Rows 7.2, 7.3 and 7.4 pass on the checklist alone; they are neither controls nor defect homes.

### Controls

The 38 controls (1.1, 1.2, 2.2 to 2.5, 3.2, 3.3, 4.1, 4.2, 4.4, 4.5, 5.3, 6.1, 6.3, 6.5, 6.6, 7.7, 7.8, 7.9, 8.1, 8.3, 8.4, 8.5, 8.8, 8.9, 9.1 to 9.4, 10.1 to 10.4, 12.1, 12.2, 12.4, 12.6): 38 pass, 0 over-failures (the scoring script lists no control without a pass).

The rows the moved questionnaire touches, as written:

```text
- **10.2** pass: "The durations sum to the session estimate of 35 minutes." (Procedure, para 1); the seven phases run in order with 5 trials per combination, and 2 + 5 + 2 + 3 + 10 + 10 + 3 is 35
- **10.3** pass: "The mouse and the trackball will be used at the point in the session where the script introduces them; the questionnaire will follow the consent form; the debriefing will close the session." (Procedure, para 2)
- **8.3** pass: "No eligibility criterion selects people for an extreme score on pointing performance." (Participants, para 1), with handedness and age screened by the form in Appendix D
- **12.2** pass: "the consent form (Appendix B), read and signed (5 minutes); the demographic questionnaire (Appendix D)" (Procedure, para 1); Participants refers to Appendices A, D and E and Procedure to B, C and D
```

Control 10.2 passes. The row reads "the seven phases run in order" and sums the durations in the draft's order (2 + 5 + 2 + 3 + 10 + 10 + 3, so the questionnaire's 2 minutes come third). It does not mention that the questionnaire now sits between consent and instructions, which departs from the checklist's example order (welcome, consent, instructions, tasks, questionnaires, debriefing). Control 8.3, run v2-1's one over-failure (the screen ran after the second device), now passes, so the fixture change removed it.

### The draft checker's mechanics

The draft checker reports D3, D8 and D9 and nothing else: pass. It printed exactly three lines, exit 1, in turn 2 and again in turn 3: references (D8), the contribution bullet list (D3) and the supervision sentence (D9). There was no sections line and no word-count line; row 13.5 reads "the section list and the body word count hold".

### Quotes on draft-checked passes

50 draft-checked rows pass or pass narrowly: 44 under Items and the six substance tests (13.9 is the one narrow pass). The four attested passes (3.1, 5.2, 13.1, 13.4) read `confirmed by the user, 2026-10-15`. Every one of the 50 carries a quoted passage followed by its location in parentheses. Checked mechanically against the draft, all 50 quotes occur verbatim and none is longer than two sentences. Borderline cases, in the form the earlier records flagged:

- 3.2 quotes the heading line "## Design" (heading 7), 6.4 quotes "Research questions or Hypotheses" (heading 3) and 3.3 quotes the title (title): a heading as the passage.
- Several passes quote a clause, not a whole sentence, for example 2.5 "if sign-ups fall short by week 5, recruiting extends to a second section" (Participants, para 2) and 8.9 without its closing semicolon. The words are verbatim in each case.

After the fixes there are 52 such rows, all verbatim against the fixed draft, including the two re-checked rows.

### 13.2 and 13.3

Both rows read `not checked: defend-stage`.

### The checker on the first pass

```text
$ python3 "$P/scripts/check_proposal.py" review "$T/first-pass-review.md"; echo "exit=$?"
exit=0
```

Turn 2 ran it twice on its own file, once after the Write and once after six Edits: "(Bash completed with no output)" both times.

## Fix-picking check

In the first-pass file, D4 is row 7.5 with fix 5, and D7 is row 10.5 with fix 8. Turn 3's prompt was "Apply fixes 5 and 8.", the right two numbers.

The draft, `git -C "$S" diff -U0 b49897b bc8b28d -- proposal/draft.md`: two hunks, `@@ -50,0 +51,2 @@` (a new paragraph and its blank line after Procedure paragraph 2) and `@@ -53 +55 @@` (Design paragraph 1). `--word-diff=plain -U0` shows exactly two insertions and no deletions:

```text
{+If the experimenter falls ill or the equipment fails, the affected session will be rescheduled within the data-collection weeks rather than run by a second experimenter, so that one experimenter still runs every session. A spare mouse and trackball of the same models will be kept in room 204, and the study software will be installed on a second computer of the same configuration.+}
... Together, a 2 by 3 by 3 within-subjects factorial design; H3's interaction has its variables crossed. The {+nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software with equal counts per combination. The+} distances and sizes ...
```

At git's default context the two edits fall in one hunk (`@@ -48,9 +48,11 @@`), as they did in run v2-1. The key's wording, "two insertions (`git diff -U0` shows two hunks)", is met. Fix 5 went in word for word at the place it names. Fix 8 differs in two ways, and turn 3's message disclosed both:

- It went in as a new Procedure paragraph 3. The fix said "add to Procedure, para 2".
- The skill left out the fix's closing bracketed note to the user, "[confirm both are available before week 4]".

Neither adds anything beyond the picked fixes. The two picked fixes were applied alone: pass.

`proposal/review.md`, `git -C "$S" diff -U0 b49897b bc8b28d -- proposal/review.md`: five hunks, all on the key's allowed list. Every other row and line is byte-identical. The Waivers and Hand-off sections are unchanged (`diff` of each section between the two files prints nothing).

| Line    | What changed                                                                                              | Allowed by the key                     |
| ------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| 45      | row 7.5, fail to `pass (fix 5 applied)`                                                                   | yes, the 7.5 row                       |
| 65      | row 10.5, fail to `pass (fix 8 applied)`                                                                  | yes, the 10.5 row                      |
| 76      | row 13.5, "ten items" to "eight items ... still fail", still fail                                         | yes, the 13.5 row                      |
| 94      | Brief against draft entry 7.5, `- fail:` to `- pass (fix 5 applied):`                                     | yes, a Brief finding the fixes touched |
| 108-110 | Summary line recomputed, plus a new note: "Fixes 5 and 8 applied to proposal/draft.md on 2026-10-15; ..." | yes, the Summary section               |

The re-checked rows:

```text
- **7.5** pass (fix 5 applied): "The nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software with equal counts per combination." (Design, para 1), beside the device order counterbalanced half and half from a shuffled list
- **10.5** pass (fix 8 applied): "If the experimenter falls ill or the equipment fails, the affected session will be rescheduled within the data-collection weeks rather than run by a second experimenter, so that one experimenter still runs every session." (Procedure, para 3), with spare devices and a second computer named in the sentence after
- pass (fix 5 applied): item 7.5. The brief draws the nine combinations in a random order per participant with equal counts, and Design, para 1 now states exactly that.
```

The Summary after the fixes reads `Items checked: 65. Pass: 56. Fail: 9. Not checked (defend-stage): 2. Consistency and brief findings: 9. Fixes proposed: 12. Waivers: 0.`, and every count recomputes from the rows. Fixes 5 and 8 stay counted, so the highest fix number is still 12. Turn 3 ran the review checker on its own rewrite ("(Bash completed with no output)"). The scoring re-run:

```text
$ python3 "$P/scripts/check_proposal.py" review "$T/after-fixes-review.md"; echo "exit=$?"
exit=0
```

## Missing-input and not-frozen stops

No stop project holds a `proposal/review.md` afterwards, and `git status --porcelain` in each shows only its planted change, so nothing was written. Every stop result event reads `"is_error": false` with no permission denials.

Brief deleted (`$S-nobrief`, rc=0, 17 s, 2 turns), final message:

```text
No design brief at proposal/design-brief.md; run /experiment-proposal:design first.

Draft exist (`proposal/draft.md`), but review need frozen brief as evidence base. Nothing written.
```

Stops, names the brief and `/experiment-proposal:design`: pass.

Draft deleted (`$S-nodraft`, rc=0, 18 s, 5 turns), final message (the scratch path written as `$S-nodraft`):

```text
Stop. No draft.

Brief present, `Status: frozen 2026-10-10` — fine. Draft missing at path brief names: `proposal/draft.md` (absolute: `$S-nodraft/proposal/draft.md`). No other markdown in repo besides brief.

Nothing written. Next step yours: write draft there, or name different path and re-run `/experiment-proposal:review`.
```

Stops and names `proposal/draft.md`: pass.

Brief `Status: open` (`$S-open`, rc=0, 30 s, 7 turns), final message (opening):

```text
Stopped at step 1. Brief exists but is not frozen.

`proposal/design-brief.md` line 4 reads:

Status: open

The review needs `Status: frozen YYYY-MM-DD`. **The brief is not frozen yet; `/experiment-proposal:design` finishes it.**

No review written, no draft touched.
```

Stops and says the brief is not frozen: pass. The message goes on to list the brief's open item and to flag the device within-versus-between departure for the design session. That is advice, and it wrote nothing.

## Hand-off (research-grill present)

Detection: research-grill is installed. `~/.claude/plugins/installed_plugins.json` has the key `"oss@open-science-skills"` at its line 145. The skill read the file with the Read tool in turn 1, read it again in turn 2 as the last tool call before printing the hand-off, and read it again in turn 3 as the last tool call (offset 144, limit 5, showing `"oss@open-science-skills": [`). That matches 76e9c28's "Read the file each time you print the hand-off".

Two messages end a pass: turn 2 (the review written) and turn 3 (the fixes applied). Each ends with the installed hand-off, in full, after a `---` rule. Each is byte-equal to the file's Hand-off section; a script checks that the result text ends with the section's text, and the section did not change between the two commits. The hand-off that ends the last pass message (turn 3):

```text
/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?; item 13.9 passed narrowly, the doubt being that Accot and Zhai (1997) is cited and then set aside as not applying to the discrete task, so removing it would not weaken the argument.
```

The seed list holds the fixed question and the one narrow pass with its doubt; there are no waivers. Exact command and seed list, and the final message ends with the hand-off in full: pass.

## Harness events

- Turn 2 had two permission denials. One was the draft checker with a trailing `; echo "EXIT:$?"`, refused as a compound command; the skill re-ran it bare with the same values. The other was a `cd` into the plugin's `scripts` directory with a `grep`; the skill read `check_proposal.py` with Read instead. Neither changed the outcome. Turns 1 and 3 and the three stops had none.
- No turn hit the session limit: every result event has `"api_error_status": null`.

## Notes, outside the bar

- review.md opens with a title line, "# Review: mouse versus trackball target selection", before the four header lines, and adds a free paragraph before `## Items`: "Template values confirmed by the user: the course defaults for the sections, 2,000 to 4,000 body words excluding references and appendices, 15 to 20 references, author-year citations as the draft uses, and the course instructor as the supervising instructor (no name given)." After the fixes, the Summary section carries a second paragraph beside its one line. The shape gives "Four lines before the first section" and a one-line Summary; the checker accepts all three.
- Fixes 7, 8 and 9 carry bracketed placeholders for values the user has not given ("[instructor's name]", "[author's name, email]", "[research office contact]", "[confirm both are available before week 4]", and a note on grading). The shape asks for replacement text "ready to paste". The turn 2 message names all three as needing the user's values first.
- Cross-section consistency adds an unplanted finding beside D11: "the incentive differs: "Participants who complete the session will receive course credit" (Participants, para 2) against "there is no payment" with no mention of credit (Appendix B)". It is not a control row, so it does not count as an over-failure.
- Fix 12, the decide for D12, names `/experiment-proposal:design`. The review notes that the brief contradicts itself: entry 2.2's "2 devices by 9 combinations by 5 trials; 35 minutes" only holds with device within subjects.

## Pass bar

| Criterion                                                     | Result | Evidence                                                                                                                  |
| ------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------- |
| At least 11 of 12 caught, 0 passed                            | pass   | 12 of 12 caught, 0 passed                                                                                                 |
| At most two over-failures                                     | pass   | 0 of 38 controls fail; 10.2 passes ("the seven phases run in order"); 8.3 passes                                          |
| Draft checker reports D3, D8, D9 and nothing else             | pass   | three lines in turns 2 and 3: references, bullet list, supervision sentence                                               |
| Every draft-checked pass quotes a passage with its location   | pass   | 50 of 50 verbatim with a location (52 of 52 after the fixes); heading quotes at 3.2, 3.3, 6.4                             |
| 13.2 and 13.3 read not checked                                | pass   | both `not checked: defend-stage`                                                                                          |
| Checker exits 0 on review.md                                  | pass   | first pass exit 0; after fixes exit 0                                                                                     |
| Picked fixes applied alone, affected rows re-checked          | pass   | fixes 5 and 8 (D4, D7); two insertions, two hunks at `-U0`; review.md changes only at 7.5, 10.5, 13.5, Brief 7.5, Summary |
| Missing-input and not-frozen stops                            | pass   | brief: the skill's sentence verbatim; draft: names `proposal/draft.md`; open: "The brief is not frozen yet"               |
| Turn 1 waited; the draft checker ran with the user's values   | pass   | turn 1: six Reads, no Bash, no review.md; turn 2: checker with `--supervisor "the course instructor"` after the answer    |
| Hand-off (research-grill present), final message ends with it | pass   | exact defend command and seed list at the end of turns 2 and 3, the plugins file re-read each time                        |

## Verdict

Run v2-6 of scenario 5 passes at 76e9c28. It caught 12 of 12 defects, passed none and over-failed no control. The draft checker reported D3, D8 and D9 and nothing else, and the review checker exits 0 on both files. The picked fixes went in alone. All three stops held. Turn 1 waited for the user's values before checking anything, and the hand-off ends the final message in full.
