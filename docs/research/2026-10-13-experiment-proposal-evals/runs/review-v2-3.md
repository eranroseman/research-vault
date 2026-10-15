# Scenario 5 (review on the proposal with 12 planted defects) at 0.2.0, run v2-3

Date: 2026-10-15
Plugin commit: 5e13529 (`experiment-proposal` 0.2.0)
Fixtures: `fixtures/proposal-with-defects.md` (copied in as `proposal/draft.md`) and `fixtures/proposal-with-defects.brief.md` (as `proposal/design-brief.md`), byte-identical to the fixture files (`cmp` against the scratch project's `fixtures` commit); key `fixtures/proposal-with-defects.key.md`.
Model: `--model opus`, which the init event of turn 1 reports as `claude-opus-5` (Claude Code 2.1.273); the init event lists `experiment-proposal` 0.2.0 from the `--plugin-dir` path and `oss@open-science-skills` 2.35.1, and one agent, `experiment-proposal:hci-researcher`.

The headless turns ran under an earlier driver, which a rate limit killed before it scored them (see Harness event). This record scores from the saved artifacts: the stream-json output of each turn, kept outside the repository as `$S.turnN.jsonl` with `$S.turnN.meta`, and the scratch project's commits. No turn was run for this record.

## Commands

Setup, as the scratch project's history shows it (commits `init`, empty, and `fixtures`, author `eval <eval@example.invalid>`):

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/review-v2-3
mkdir -p "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval
cd "$S" && git commit --allow-empty -qm init && mkdir proposal
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.brief.md "$S/proposal/design-brief.md"
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.md "$S/proposal/draft.md"
cd "$S" && git add -A && git commit -qm fixtures
```

Each turn ran through the helper `review-v2-drive.sh "$S" N`, which reads the prompt from `$S.turnN.prompt` and runs, for turn 1:

```bash
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null
```

and for every later turn the same command with `--continue` after `-p`. The prompts, verbatim:

| Turn | Prompt                                                                                                                                                                                 | rc, seconds, turns |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| 1    | `/experiment-proposal:review`                                                                                                                                                          | 0, 539 s, 21       |
| 2    | `Template mechanics: accept the course's defaults, with the citation style author-year, as the draft uses, and the supervisor the course instructor. Confirm 3.1, 5.2, 13.1 and 13.4.` | 0, 75 s, 11        |
| 3    | `Apply fixes 8 and 11.`                                                                                                                                                                | 0, 77 s, 10        |
| 4    | `Print the hand-off again.`                                                                                                                                                            | 1, 5 s (429)       |

After turn 2: `cd "$S" && git add -A && git commit -qm first-pass` (commit `0bc277b`, only `proposal/review.md` added). After turn 3: `cd "$S" && git add -A && git commit -qm after-fixes` (commit `f00d734`). The draft is unchanged from `fixtures` to `first-pass`.

Scoring commands, run for this record outside the repository (`first-pass` and `after-fixes` are commit messages, not refs, so `git -C "$S" show first-pass:proposal/review.md` answers `fatal: invalid object name 'first-pass'`; the shas stand in):

```bash
git -C "$S" show 0bc277b:proposal/review.md > <tmp>/first.md
git -C "$S" show f00d734:proposal/review.md > <tmp>/after.md
python3 "$P/scripts/check_proposal.py" review <tmp>/first.md; echo "exit=$?"
python3 "$P/scripts/check_proposal.py" review <tmp>/after.md; echo "exit=$?"
git -C "$S" diff 0bc277b f00d734
git -C "$S" diff -U0 0bc277b f00d734 -- proposal/draft.md
git -C "$S" diff --word-diff=porcelain 0bc277b f00d734 -- proposal/draft.md
```

Environment: the user-level plugins ran their SessionStart hooks in the scratch sessions, including a global caveman hook (one `CAVEMAN` hit in `$S.turn1.jsonl`); the nobrief and open stop messages are in its clipped register. No effect on the bar.

## Transcript, decisive lines

Turn 1 read the checklist, the shape, the brief, `plugin.json`, the draft and `~/.claude/plugins/installed_plugins.json` (Read), ran the draft checker without `--supervisor`, wrote `proposal/review.md`, and ran the review checker to a clean exit. Its final message, excerpts:

```text
**Mechanics (item 3.1 ran on the course defaults).** `check_proposal.py draft` reported three lines: 14 references → item 5.1; no bullet list of contributions → item 4.3; no consent sentence naming the supervisor → item 12.3. Sections and body word count passed. Confirm or correct the template's values: [...] and the supervising instructor's name — the name is unknown to me, and both fix 2 and fix 12 need it.

**Attested items (3.1, 5.2, 13.1, 13.4), one batch.** Confirm or correct: [...]

Those four rows and item 13.5 are recorded `fail` pending your answer. Once you confirm, they re-check to `pass (fix N applied)` with `confirmed by the user, 2026-10-15`.

**Counts.** Items checked: 65. Pass: 48. Fail: 17. Not checked (defend-stage): 2. Consistency and brief findings: 11. Fixes proposed: 17. Waivers: 0.

**Biggest finding.** The draft puts device **within** subjects; brief entries 7.1–7.4, 7.9 and 8.5 put it **between**. [...] fix 7 is a `decide:` fix: amend the brief via `/experiment-proposal:design`, or restore device-between [...] the order of the nine distance-and-size combinations is stated nowhere (fix 8).

Which fixes should I apply? Give their numbers.
```

Turn 2 re-ran the draft checker with `--supervisor "the course instructor"`, edited rows 3.1, 3.3, 5.2, 12.3 (fix 12's placeholder now names the course instructor), 13.1, 13.4, 13.5 and the Summary, and ran the review checker (`CLEAN`). Final message, excerpts:

```text
Checker exits 0.

**What changed.** Item 3.1 → `pass (fix 2 applied)`, recording the course defaults, author-year citations and the course instructor as supervisor. Items 5.2, 13.1, 13.4 → `pass` with `confirmed by the user, 2026-10-15` (fixes 5, 14, 15). Item 3.3 → full `pass`: the author-year doubt is settled by your answer. [...]

Items checked: 65. Pass: 52. Fail: 13. Not checked (defend-stage): 2. Consistency and brief findings: 11. Fixes proposed: 17. Waivers: 0.

Remaining failures: 1.3, 4.3, 5.1, 6.2, 7.2, 7.5, 7.6, 8.2, 10.5, 12.3, 12.5, 13.5, 13.9.

Which fixes should I apply? Give their numbers.
```

Turn 3 made two Edit calls on `proposal/draft.md`, five on `proposal/review.md`, ran the review checker (`REVIEW_CLEAN`) and the draft checker (the same three lines, exit 1). Final message, excerpts:

```text
Fixes 8 and 11 applied to `proposal/draft.md`; nothing else in the draft was touched. The review checker exits 0.

- Design, para 1 gained the fix-8 sentence after the target-size levels: [...]
- Procedure, para 2 gained the fix-11 sentence after the debriefing clause. I put it in the draft's future tense ("will be rescheduled", "will be stopped") rather than the present tense the fix text used, and the row now quotes what the draft says.
- Item 7.5 → `pass (fix 8 applied)`. Item 10.5 → `pass (fix 11 applied)`.
- Brief against draft: entry 7.5's finding became a pass line, so findings drop from 11 to 10.
- Item 13.5 re-checked: still `fail`, now nine items of steps 1 to 12 failing, and fix 16 lists the fixes that remain. [...]

Items checked: 65. Pass: 54. Fail: 11. Not checked (defend-stage): 2. Consistency and brief findings: 10. Fixes proposed: 17. Waivers: 0.
```

## Scoring the first pass (review.md at commit `0bc277b`, "first-pass")

Summary line: `Items checked: 65. Pass: 52. Fail: 13. Not checked (defend-stage): 2. Consistency and brief findings: 11. Fixes proposed: 17. Waivers: 0.` Recomputed from the rows: 61 rows under Items and 6 under Substance tests, less the two `not checked`, is 65; 52 pass or pass narrowly (48 draft-checked, 4 attested); 13 fail (1.3, 4.3, 5.1, 6.2, 7.2, 7.5, 7.6, 8.2, 10.5, 12.3, 12.5, 13.5, 13.9); 1 Cross-section fail and 10 Brief-against-draft fails; highest fix number 17. The counts agree.

### D1 to D12

| Defect | Item or section                | The row as written (excerpt)                                                                                                                                                                                            | Verdict |
| ------ | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| D1     | 1.3                            | "fail: the data plan names no retention period for the raw logs, which brief entry 1.3 sets at five years. fix 1"                                                                                                       | caught  |
| D2     | 6.2                            | "fail: H2 names its variables and direction but cites nothing [...] fix 6"                                                                                                                                              | caught  |
| D3     | 4.3                            | "fail: the contributions run as prose, lettered (a) to (c) inside a paragraph, not as a bullet list. fix 3"                                                                                                             | caught  |
| D4     | 7.5                            | "fail: the order of the nine distance-and-size combinations is stated nowhere; only the device order is counterbalanced. fix 8"                                                                                         | caught  |
| D5     | 7.6                            | "fail: movement time carries no construct-validity statement and the error rate no reliability statement. fix 9"                                                                                                        | caught  |
| D6     | 8.2                            | "fail: the section names the recruitment method but never says how a candidate can decline without consequence [...] fix 10"                                                                                            | caught  |
| D7     | 10.5                           | "fail: nothing says what happens if the experimenter falls ill or the equipment breaks down. fix 11"                                                                                                                    | caught  |
| D8     | 5.1                            | "fail: the reference list holds 14 entries, below the 15 to 20 the template asks for. fix 4"                                                                                                                            | caught  |
| D9     | 12.3                           | "fail: the consent form omits the supervisor, [...] fix 12"                                                                                                                                                             | caught  |
| D10    | 12.5                           | "fail: the script has no point at which participants can ask questions. fix 13"                                                                                                                                         | caught  |
| D11    | 12.3 and Cross-section         | 12.3: "states 20 minutes against a 35-minute session"; Cross-section: "fail: the consent form says the session "takes about 20 minutes" (Appendix B), where Procedure, Participants and Appendix A all give 35 minutes" | caught  |
| D12    | Brief against draft, entry 7.1 | "fail: entry 7.1 puts device between subjects; the draft reads "Device: the mouse or the trackball named in Materials, within subjects" (Design, para 1). fix 7."                                                       | caught  |

Caught 12 of 12, passed 0. The 12.3 row reports D9 and D11 together, which the key counts for both. D12 is scored on the Brief-against-draft section alone; the 7.1 row (pass, "the within-subjects label departs from the brief, see Brief against draft") is not consulted.

The Brief-against-draft section also reports 7.2, 7.3, 7.4, 8.5 ("entry 8.5 reads 24, twelve per device"), 7.9 (history prevented by "same weeks, similar times"), 7.5, 7.6, 1.3 and 6.2. The key names all of these except 7.9 as expected departures that do not over-fail; 7.9 is the same between-versus-within departure seen from the brief's history remedy, and it is not a control row, so it is not scored.

### Controls

All 38 controls read pass; 0 over-failures.

- `pass` (36): 1.1, 1.2, 2.2, 2.3, 2.4, 2.5, 3.2, 4.1, 4.2, 4.4, 4.5, 5.3, 6.1, 6.3, 6.5, 6.6, 7.7, 7.8, 7.9, 8.1, 8.4, 8.5, 8.8, 8.9, 9.1, 9.2, 9.3, 9.4, 10.1, 10.2, 10.3, 10.4, 12.1, 12.2, 12.4, 12.6.
- `pass (fix 2 applied)` (1): 3.3, a pass narrowly in turn 1 ("the doubt: the entries are author-date, not the ACM reference format the course default names") lifted to a pass once item 3.1 recorded the author-year style; the label is discussed under Observations.
- `pass narrowly` (1): 8.3, "screened by a short form (Appendix D) for handedness and age" (Participants, para 1); "the doubt: Appendix D is also the post-session demographic questionnaire, which Procedure hands over after the second device, so when handedness and age are collected is unclear."

Rows that fail outside both the key's defects and its controls, so not scored: 7.2 (the draft's "symmetric" carry-over against brief entry 7.2's asymmetric one; it carries fix 7, the same `decide:` fix as the Brief-against-draft departures), 13.9 ("the Accot and Zhai sentence states its own irrelevance to the task studied", fix 17) and 13.5 (fails while steps 1 to 12 fail, as expected).

### The draft checker's mechanics

Turn 1, before the template values were confirmed:

```text
python3 "<checkout>/plugins/experiment-proposal/scripts/check_proposal.py" draft proposal/draft.md --words 2000-4000 --references 15-20
Exit code 1
proposal/draft.md:67: references: 14 entries; the template asks for 15 to 20
proposal/draft.md:3: introduction: no bullet list of contributions
proposal/draft.md:1: appendix: no consent sentence saying the study is under the supervision of the instructor
```

Turn 2, with the confirmed supervisor (`... --references 15-20 --supervisor "the course instructor"`): the same three lines, exit code 1. Turn 3 re-ran it after the fixes: the same three lines. The three lines are D8 (item 5.1), D3 (item 4.3) and D9 (item 12.3), and nothing else: no section-order line and no word-count line (turn 1: "Sections and body word count passed"). No `--sections` was passed, so the course's section list was used.

### Quotes on draft-checked passes

48 draft-checked rows read pass or pass narrowly; each was checked by a script against the fixture draft. Each quotes a passage in double quotes that occurs verbatim in the draft, followed by a location in parentheses (a section heading with a paragraph number where the draft has paragraphs, or the title, an appendix, Timeline). Two notes:

- 3.2 quotes a heading, `"## Design" (heading, after "## Procedure")`, then says the checker found every section in order; borderline, like 0.1.0's 3.2, counted as quoted.
- 12.6 quotes `"Age: ____ Handedness: ____" (Appendix D)`, the blanks as plain underscores where the draft has mdformat's escaped ones; the key counts both.

The four attested rows (3.1, 5.2, 13.1, 13.4) carry `confirmed by the user, 2026-10-15`.

### 13.2 and 13.3

Both rows read `not checked: defend-stage`.

### The review checker on the first pass

```text
$ python3 "$P/scripts/check_proposal.py" review <tmp>/first.md; echo "exit=$?"
exit=0
```

No output, exit 0.

## Fix-picking check

- Fix numbers: in the first-pass file, row 7.5 (D4) carries "fix 8: add to Design, "The nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software, with equal counts per combination."" and row 10.5 (D7) carries "fix 11: add to Procedure, "If the experimenter falls ill, [...]"". Turn 3's prompt was `Apply fixes 8 and 11.` Correct.

- Draft diff, `first-pass` (the draft unchanged since `fixtures`) to `after-fixes`: plain `git diff` shows a single hunk, `@@ -46,11 +46,11 @@`, because the two changed lines (49, Procedure para 2; 53, Design para 1) are four lines apart and their three-line contexts merge. `git diff -U0` shows exactly two hunks, `@@ -49 +49 @@` and `@@ -53 +53 @@`, and `--word-diff=porcelain` shows two added sentences and nothing removed:

  ```text
  +If the experimenter falls ill, the affected sessions will be rescheduled within the data-collection weeks; if the computer or either device fails, the session will be stopped, its partial data will be discarded, and it will be rerun from the start with a replacement of the same model.
  +The nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software, with equal counts per combination.
  ```

  Scored as holding: the key's "exactly two hunks" means two separate edits and nothing else, which this is; the single default hunk is an artefact of the fixture's Procedure sitting just above Design. The fix-11 sentence was put in the draft's future tense, which the shape's "ready to paste in the draft's tense and voice" asks of the fix text itself (the fix text was in the present).

- review.md diff: five changed lines (`-U0` hunks at 39, 59, 70, 86, 103):

  - 7.5: `- **7.5** pass (fix 8 applied): "The nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software, with equal counts per combination." (Design, para 1); the device order is counterbalanced in the sentence before it.`
  - 10.5: `- **10.5** pass (fix 11 applied): "If the experimenter falls ill, the affected sessions will be rescheduled within the data-collection weeks; [...]" (Procedure, para 2)`
  - 13.5: re-checked, still fail, "nine items of steps 1 to 12 fail", fix 16's list now "1, 3, 4, 6, 7, 9, 10, 12, 13 and 17".
  - Brief against draft, the 7.5 finding: `- pass (fix 8 applied): entry 7.5 orders the nine combinations at random per participant with equal counts, and Design now states exactly that.`
  - Summary: `Items checked: 65. Pass: 54. Fail: 11. Not checked (defend-stage): 2. Consistency and brief findings: 10. Fixes proposed: 17. Waivers: 0.` (recomputed: 52 + 2 pass, 13 − 2 fail, 11 − 1 findings; correct).

  All five are in the key's allowed set; every other row, the Cross-section section, Waivers and Hand-off are byte-identical. The two re-checked rows read `<result> (fix N applied)` and quote the new passage, which the script found verbatim in the after-fixes draft.

- The review checker on the after-fixes file:

  ```text
  $ python3 "$P/scripts/check_proposal.py" review <tmp>/after.md; echo "exit=$?"
  exit=0
  ```

## The three stops

Each in a copy of the project at the `fixtures` commit (HEAD `818214a`, no review.md), one turn with `/experiment-proposal:review`, the same flags; the copies are `$S-nobrief`, `$S-nodraft` and `$S-open`, with `$S-<name>.turn1.jsonl` beside them. The setup commands are not in the artifacts; the state is from `git status` in each copy. None wrote a file (`git status --porcelain` shows only the planted change).

- Brief deleted (` D proposal/design-brief.md`); rc 0, 20 s, 2 turns:

  ```text
  No design brief at proposal/design-brief.md; run /experiment-proposal:design first.

  Draft exist at `proposal/draft.md`, but review need frozen brief as evidence base. Nothing written.
  ```

  Stops, names the brief and `/experiment-proposal:design`. Pass.

- Draft deleted (` D proposal/draft.md`); rc 0, 21 s, 3 turns:

  ```text
  Brief present and frozen. Draft missing.

  Tried: `/tmp/ep-eval/review-v2-3-nodraft/proposal/draft.md` — not there. Only `design-brief.md` sits in `proposal/`.

  Review stops here. No draft, nothing to check against checklist.
  ```

  Stops and names the path it tried, and `proposal/draft.md` as "path the brief's `Draft:` line names". Pass.

- Brief's status changed (` M proposal/design-brief.md`, the diff only `-Status: frozen 2026-10-10` to `+Status: open`); rc 0, 52 s, 7 turns:

  ```text
  Brief not frozen. `proposal/design-brief.md` line 4 read `Status: open`, not `frozen YYYY-MM-DD`.

  Review needs frozen brief. Run `/experiment-proposal:design` to finish it — brief still carry one open item ("Run `/experiment-proposal:lit-search` for a current-device comparison to cite under H1").

  No `proposal/review.md` written.
  ```

  Stops and says the brief is not frozen. Pass. (It read the checklist, the shape, `plugin.json` and the draft before stopping; harmless, nothing written.)

## The hand-off (research-grill present)

Detection: turn 1 read `~/.claude/plugins/installed_plugins.json` with the Read tool; it holds the key `oss@open-science-skills`, and turn 1 said "research-grill is installed (`oss@open-science-skills`)."

Turn 2's and turn 3's final messages both end with this block, in full, as their last lines:

```text
/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?; item 13.8 passed narrowly, the doubt being that the third contribution, a reusable task program and its trial logs, would read the same for any pointing study.
```

Turn 1's final message ends with the same block. The exact defend command and the seed list are present; there are no waivers, so the seed list is the fixed question plus the one narrow substance pass (13.8 with its doubt), as the shape gives it. 8.3's narrow pass is not a substance test and rightly is not seeded. The review.md Hand-off section holds the same two lines in the first-pass and after-fixes files. The final message ends with the hand-off in full: yes, in all three turns.

## Harness event: turn 4

Turn 4 (`Print the hand-off again.`) exited rc 1 after 5 s. Its stream shows a `rate_limit_event` with `"status":"rejected"` and `"rateLimitType":"five_hour"`, and the result line:

```text
"is_error":true,"num_turns":1,"subtype":"success","api_error_status":429,"result":"You've hit your session limit · resets 3:40am (America/Chicago)"
```

Turn 4 is a supplementary hand-off turn, not part of scenario 5's bar, and is not scored here; the hand-off is scored from turns 2 and 3 above. Turns 1 to 3 and the three stops all have `api_error_status` null and `is_error` false.

## Observations

- Attested rows were written before the batch was answered. In a headless turn the skill cannot wait, so turn 1 wrote 3.1, 5.2, 13.1 and 13.4 as `fail` with `decide:` fixes (fixes 2, 5, 14 and 15), and turn 2 rewrote them as `pass (fix N applied): confirmed by the user, 2026-10-15`; 3.3 became `pass (fix 2 applied)` too. The shape says "A pass on an attested item carries `confirmed by the user, <date>`" and reserves `(fix N applied)` for a row re-checked after a fix; here nothing in the draft changed, four fix numbers are spent on confirmations, and `Fixes proposed: 17` counts them. The shape's result list ("one of `pass`, `pass narrowly`, `fail`, `fail (waived)`, `not checked`") has no pending state for an attested item awaiting its answer. No bar criterion turns on it.
- Step 2's order: the skill says to ask for the template's values and then run `check_proposal.py draft ... --supervisor "<name>"`; turn 1 ran the checker without `--supervisor` and asked in the same message. The supervision line was reported anyway, and turn 2 re-ran it with the name; the result is the same.
- A Brief-against-draft line after a fix reads `- pass (fix 8 applied): ...`, where the shape gives "`- fail: ...`, or `- pass: ...` when there is none"; the checker accepts it.
- 13.4 passes as confirmed while its own row says "the Design section's within-subjects device still has no matching rationale in the brief, which fix 7 settles". The key does not score 13.4.
- Fix 12's consent text keeps two placeholders, `[the author's email]` and `[the office's contact]`; the draft's consent form gives no address either ("at the address below"), so the fix cannot fill them.

## Pass bar

| Criterion                                                         | Result | Evidence                                                                                                |
| ----------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------- |
| At least 11 of 12 caught, 0 passed                                | pass   | 12 of 12 caught, 0 passed                                                                               |
| At most two over-failures among the 38 controls                   | pass   | 0 over-failures; 36 pass, 3.3 pass after item 3.1, 8.3 pass narrowly                                    |
| Draft checker reports D3, D8 and D9 and nothing else              | pass   | three lines: 14 references, no bullet list, no supervision sentence; same with `--supervisor`           |
| Every draft-checked pass quotes a passage with its location       | pass   | 48 of 48 rows, verbatim (3.2 quotes a heading; 12.6 underscores as the key allows)                      |
| 13.2 and 13.3 read not checked                                    | pass   | both `not checked: defend-stage`                                                                        |
| Checker exits 0 on the first-pass review.md                       | pass   | no output, exit 0                                                                                       |
| Fix-picking: fixes 8 and 11 are D4's and D7's                     | pass   | rows 7.5 and 10.5                                                                                       |
| Fix-picking: two draft edits only                                 | pass   | `-U0` gives two hunks; plain `git diff` merges them into one, four lines apart                          |
| Fix-picking: only allowed review.md lines change, rows re-checked | pass   | 7.5, 10.5, 13.5, the Brief 7.5 line, Summary; 7.5 and 10.5 read pass (fix N applied) with the new quote |
| Checker exits 0 on the after-fixes review.md                      | pass   | no output, exit 0                                                                                       |
| Missing-brief stop                                                | pass   | "No design brief at proposal/design-brief.md; run /experiment-proposal:design first."                   |
| Missing-draft stop                                                | pass   | names the path tried, `proposal/draft.md`                                                               |
| Not-frozen stop                                                   | pass   | "Brief not frozen. [...] `Status: open`, not `frozen YYYY-MM-DD`."                                      |

Hand-off, recorded for scenario 6 (present case): the exact command and the seed list, and turns 2 and 3 each end with the hand-off in full.

## Verdict

Run v2-3 of scenario 5: pass. Turn 4's 429 is a harness event outside the bar.
