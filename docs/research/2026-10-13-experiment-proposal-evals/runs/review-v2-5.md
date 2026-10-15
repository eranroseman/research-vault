# Scenario 5 (review on the proposal with 12 planted defects) at 0.2.0, run v2-5

Date: 2026-10-15
Plugin commit: 76e9c28 (`experiment-proposal` 0.2.0), which is also the fixture commit. The fix that matters for this scenario is 76e9c28: review step 2 waits for the user's template values and runs the draft checker only with them, step 3 waits for the attested answers before writing review.md, step 7 re-reads the plugins file each time it prints the hand-off, the shape names a resolved finding (`- pass (fix N applied): ...`), and the draft fixture screens with Appendix D right after the consent form. The design fix ed96208 does not touch `review`. The worktree's HEAD at scoring time is 76e9c28, and `git status --porcelain` shows no change under `plugins/` or the fixtures, so the plugin tree that ran is the commit's.
Fixtures: `fixtures/proposal-with-defects.md` copied in as `proposal/draft.md`, `fixtures/proposal-with-defects.brief.md` as `proposal/design-brief.md`; key `fixtures/proposal-with-defects.key.md`. Both copies are byte-identical to the fixtures (`cmp` before the first commit, and the draft at the `first-pass` commit still compares equal to the fixture).
Model: `--model opus`; the init event of every stream reports `claude-opus-5`, lists the plugins `experiment-proposal` and `oss` (research-grill present), and one agent `experiment-proposal:hci-researcher`. Turn 1's Reads of `references/checklist.md`, `references/review.md` and `.claude-plugin/plugin.json` resolved under `$P`, and the review's header reads `Checklist: experiment-proposal 0.2.0`.

## Commands

Setup (`S=/tmp/ep-eval/review-v2-5`, fresh; no directory of that name existed before the run):

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/review-v2-5
mkdir -p "$S/proposal" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.brief.md "$S/proposal/design-brief.md"
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.md "$S/proposal/draft.md"
cd "$S" && git add -A && git commit -qm fixtures    # eaa1345
```

Each turn ran through the helper `review-v2-drive.sh "$S" N`, which reads the prompt from `$S.turnN.prompt` and runs, for turn 1:

```bash
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null
```

and for later turns the same command with `--continue` before `--model`. Prompts and exits (`$S.turnN.meta`; agent turns from the result event):

| Turn | Prompt                                                                                                                                                                                 | Exit, wall time        |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| 1    | `/experiment-proposal:review`                                                                                                                                                          | rc=0, 29 s (6 turns)   |
| 2    | "Template mechanics: accept the course's defaults, with the citation style author-year, as the draft uses, and the supervisor the course instructor. Confirm 3.1, 5.2, 13.1 and 13.4." | rc=0, 302 s (12 turns) |
| 3    | "Apply fixes 6 and 9."                                                                                                                                                                 | rc=0, 63 s (10 turns)  |

No turn's result event carries an `api_error_status` (all `null`), and no `.err` file has content. No rate limit was hit.

Commits in `$S` between turns:

```bash
cd "$S" && git add -A && git commit -qm first-pass    # after turn 2: ec60df0
cd "$S" && git add -A && git commit -qm after-fixes   # after turn 3: bba36af
```

The three stops, each a fresh copy of the project at its `fixtures` commit with the later history pruned (`git log --oneline --all` in each prints only `eaa1345 fixtures`) and one planted change in the working tree, run with the turn 1 command and `S` replaced by the copy:

```bash
for x in nobrief nodraft open; do
  git clone -q "$S" "$S-$x" && cd "$S-$x" && git reset -q --hard eaa1345 && git remote remove origin
  git reflog expire --expire=now --all && git gc -q --prune=now
done
rm "$S-nobrief/proposal/design-brief.md"     # git status: " D proposal/design-brief.md"
rm "$S-nodraft/proposal/draft.md"            # git status: " D proposal/draft.md"
sed -i 's/^Status: frozen 2026-10-10$/Status: open/' "$S-open/proposal/design-brief.md"   # git status: " M proposal/design-brief.md"
cd "$S-nobrief" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review" > "$S-nobrief.turn1.jsonl" 2> "$S-nobrief.turn1.err" < /dev/null
```

Scoring commands (temporary files outside the repository):

```bash
T=/tmp/ep-eval/v2-5-score
git -C "$S" show ec60df0:proposal/review.md > "$T/first-pass-review.md"     # commit "first-pass"
git -C "$S" show bba36af:proposal/review.md > "$T/after-fixes-review.md"    # commit "after-fixes"
python3 "$P/scripts/check_proposal.py" review "$T/first-pass-review.md"; echo "exit=$?"
python3 "$P/scripts/check_proposal.py" review "$T/after-fixes-review.md"; echo "exit=$?"
git -C "$S" diff -U0 ec60df0 bba36af
git -C "$S" diff --word-diff=plain -U0 ec60df0 bba36af -- proposal/draft.md
```

## The waits

Turn 1 waited. Its five tool calls are Reads only: `$P/references/checklist.md`, `$P/references/review.md`, the brief, the draft, `$P/.claude-plugin/plugin.json`. No Bash call, no Write; after the turn `proposal/` holds only `design-brief.md` and `draft.md`, and `git status --porcelain` is empty. The draft checker did not run in turn 1, so it never ran with values the user had not given. Its final message asked both batches in one turn:

```text
Brief frozen, draft read. Two question batches before I write the review.

**1. Template mechanics (item 3.1).** Confirm or correct these, the course defaults:

- Sections, in order: Introduction, Literature review, Research questions or Hypotheses, Participants, Materials, Procedure, Design, Appendix
- Body words: 2,000–4,000, references and appendices excluded
- References: 15–20
- Citation style: the template's (ACM reference format for CHI)
- Supervising instructor's name: **unknown — give it**

Note: draft section order puts Design *after* Procedure, and has extra `## Timeline` and `## References` headings. Tell me if the template's order is the default list or the draft's.

**2. Attested items** — answer all three:

- **5.2** Snowballing from a recent key article stopped turning up new relevant work (lit-search stop rule)? ...
- **13.1** Proposal reviewed against the seven reader questions ... and revised where short?
- **13.4** Can you give the reason for every Design-section choice? (brief's rationale entries are the record)
```

Item 3.1 was asked once, in the template block; the one answer covered both blocks. Turn 2 then ran the draft checker with the user's values, `--words 2000-4000 --references 15-20 --supervisor "the course instructor"` (no `--sections`, since the confirmed list is the default). Its first attempt, the same command followed by `; echo "EXIT=$?"`, was refused by the permission guard for the compound `echo`; the bare command ran, exit 1:

```text
proposal/draft.md:67: references: 14 entries; the template asks for 15 to 20
proposal/draft.md:3: introduction: no bullet list of contributions
proposal/draft.md:1: appendix: no consent sentence saying the study is under the supervision of the instructor
```

After the first Write of review.md, turn 2 ran the draft checker once more with `--words 2500-2501` (bounds nobody gave), which printed `words: the body has 2456 words; the template asks for 2500 to 2501` and the same three lines; the skill used it to read the body word count and corrected row 13.5 from "2,443 words" to "2,456 words". Turn 3 repeated the probe after the fixes (`the body has 2536 words`). Neither probe's word line became a finding; the review records the body as within 2,000 to 4,000. See Defects outside the bar.

## Scoring against the key (first pass: review.md at commit ec60df0, after turn 2)

First-pass Summary line: `Items checked: 65. Pass: 52. Fail: 13. Not checked (defend-stage): 2. Consistency and brief findings: 11. Fixes proposed: 14. Waivers: 0.` Every count recomputes from the rows (67 rows, 65 not `not checked`, 52 `pass` or `pass narrowly`, 13 `fail`, 11 `- fail` lines across Cross-section and Brief against draft, highest fix number 14). The seven sections are present in the shape's order. Failing rows: 1.3, 4.3, 5.1, 6.2, 7.2, 7.5, 7.6, 8.2, 10.5, 12.3, 12.5, 13.5, 13.9.

Turn 2's final message, opening and close (its failure table elided):

```text
`proposal/review.md` written, checker clean.

**Counts:** 65 items checked, 52 pass, 13 fail, 2 not checked (defend-stage), 11 consistency/brief findings, 14 fixes, 0 waivers.
...
**Biggest finding: the brief says device is between subjects, the draft puts it within.** That cascades through brief entries 7.1, 7.2, 7.3, 7.4 and 8.5 ... Not a paste fix; fix 5 is a `decide:` naming `/experiment-proposal:design`. The draft is internally consistent under its own choice, so items 7.1, 7.3, 7.4 and 8.8 pass on the draft's text — the departure lives in the Brief section.
...
Which fixes should I apply? Give their numbers.

/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?
```

### D1 to D12

| Defect | Item or section                    | The row's reason (quoted)                                                                                                                                                                                                                                                                       | Verdict |
| ------ | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| D1     | 1.3                                | fail: "the retention period for the raw logs is stated nowhere in the draft, though the reason for each identifiable item and the single point of access are." (fix 1)                                                                                                                          | caught  |
| D2     | 6.2                                | fail: "H2 names its variables and direction but cites no Literature Review source for that direction, while H1 and H3 do." (fix 4)                                                                                                                                                              | caught  |
| D3     | 4.3 (and the draft checker)        | fail: "the three contributions are run together in a prose sentence, not listed as bullets." (fix 2); checker "introduction: no bullet list of contributions"                                                                                                                                   | caught  |
| D4     | 7.5                                | fail: "the order of the nine distance-and-size combinations within a device is never stated, only the order of the two devices." (fix 6)                                                                                                                                                        | caught  |
| D5     | 7.6                                | fail: "movement time carries no construct-validity statement and error rate carries no reliability statement, though both have units, recording methods and scales and will be reported together." (fix 7)                                                                                      | caught  |
| D6     | 8.2                                | fail: "the recruitment method is stated, but nothing says how a candidate can decline without consequence, and recruiting from the author's own course section is where that matters most." (fix 8)                                                                                             | caught  |
| D7     | 10.5                               | fail: "nothing says what happens if the experimenter falls ill or the equipment breaks down." (fix 9)                                                                                                                                                                                           | caught  |
| D8     | 5.1 (and the draft checker)        | fail: "the reference list holds 14 entries, below the template's 15 to 20, although motivating work, justifying work and similar studies are all cited." (fix 3, a decide: lit-search); checker "references: 14 entries; the template asks for 15 to 20"                                        | caught  |
| D9     | 12.3 (and the draft checker)       | fail: "... and it omits the supervision sentence, the retention period, the consequences of declining or withdrawing, the benefits, and the course credit named in Participants." (fix 10); checker "appendix: no consent sentence saying the study is under the supervision of the instructor" | caught  |
| D10    | 12.5                               | fail: "the script has no point at which participants can ask questions." (fix 11)                                                                                                                                                                                                               | caught  |
| D11    | 12.3 and Cross-section consistency | 12.3: "the consent form states 20 minutes against the 35-minute session estimate"; Cross-section: "fail: the session duration is 20 minutes in the consent form ("it takes about 20 minutes", Appendix B) and 35 minutes in the Procedure phase list and the recruiting announcement"           | caught  |
| D12    | Brief against draft, entry 7.1     | "fail: entry 7.1 puts device between subjects ("device between subjects; distance and size within subjects") and the draft puts it within ("Device: the mouse or the trackball named in Materials, within subjects", Design, para 1). fix 5 settles it."                                        | caught  |

Caught 12 of 12, passed 0. Row 12.3 reports both of its reasons (D9 and D11) and counts for both, as the key allows. D12 is scored on the Brief against draft section alone; the 7.1 row reads pass on the draft's text, which the key does not consult.

The Brief against draft section's other `- fail` lines are departures the key expects and does not count as over-failing: 7.2, 7.3, 7.4 and 8.5's "24 (12 per device)" (the between-subjects brief), 7.5 (D4 seen from the brief), and 1.3, 6.2 and 7.6 (restating D1, D2, D5). Its closing `- pass:` line names entries 1.1, 1.2, 2.2 to 2.5, 6.1, 6.5, 7.7, 7.8, 7.9 and 8.3 as stated in the draft as decided, so every brief entry is accounted for.

### Controls

The 38 controls (1.1, 1.2, 2.2 to 2.5, 3.2, 3.3, 4.1, 4.2, 4.4, 4.5, 5.3, 6.1, 6.3, 6.5, 6.6, 7.7, 7.8, 7.9, 8.1, 8.3, 8.4, 8.5, 8.8, 8.9, 9.1 to 9.4, 10.1 to 10.4, 12.1, 12.2, 12.4, 12.6): 38 pass, 0 over-failures. Two of the 38 are narrow passes, which the key does not count as failures:

- **2.4** pass narrowly: "Pilot in week 3; data collection in weeks 4 to 7; analysis in weeks 8 and 9; write-up in weeks 10 to 12." (Timeline); the doubt: "the four phases are dated but none names what it delivers."
- **10.3** pass narrowly: "The mouse and the trackball will be used at the point in the session where the script introduces them; the questionnaire will follow the consent form; the debriefing will close the session." (Procedure, para 2); the doubt: "the script in Appendix C never names either device, so the placement of the two devices is asserted rather than shown."

Control 10.2, with the questionnaire now between consent and instructions, passes. The row in full:

```text
- **10.2** pass: "welcome (2 minutes); the consent form (Appendix B), read and signed (5 minutes); the demographic questionnaire (Appendix D), which screens for the profile and excuses anyone outside it (2 minutes); scripted instructions, read from the script (Appendix C) in a neutral tone (3 minutes)" (Procedure, para 1); the seven phases are in order with 5 trials per combination and durations summing to 35 minutes.
```

It does not object to the questionnaire's place against the checklist's listed phase order. Control 8.3, the over-failure in v2-1 (when Appendix D was given after the second device), now passes: "No eligibility criterion selects people for an extreme score on pointing performance." (Participants, para 1); "handedness and age are screened by the form in Appendix D."

Rows that fail and are neither controls nor defect homes, counted neither way: 7.2 ("no carry-over statement is made for distance or target size, and the claim of symmetric device carry-over contradicts the brief's own finding that daily-device habit transfer is one-way", a decide naming `/experiment-proposal:design`), 13.5 (follows from the failures), and the substance test 13.9 ("the throughput strand of the literature review does not serve a hypothesis, the gap or the method, and the draft says so itself about one citation, which it introduces only to set aside", fix 14). Cross-section consistency carries one finding beyond D11, also not a control: "the incentive is course credit in Participants ("Participants who complete the session will receive course credit", para 2) and no payment in the consent form ("there is no payment", Appendix B), with no mention of credit there" (fix 13).

### The draft checker's mechanics

The run with the user's values (turn 2, `--words 2000-4000 --references 15-20 --supervisor "the course instructor"`) printed exactly three lines, exit 1: references (D8), the contribution bullet list (D3), the supervision sentence (D9). No sections line and no word-count line. A scoring re-run of the same arguments on the `first-pass` draft printed the same three lines, exit 1. Mechanics report D3, D8 and D9 and nothing else: pass.

### Quotes on draft-checked passes

48 draft-checked rows pass or pass narrowly (43 under Items, five substance tests: 13.6, 13.7, 13.8, 13.10, 13.11); the four attested passes (3.1, 5.2, 13.1, 13.4) read `confirmed by the user, 2026-10-15`. Checked mechanically against the draft: each of the 48 carries a quoted passage followed by its location in parentheses, all 48 quotes occur verbatim in the draft (12.6's `"Age: \_\_\_\_ Handedness: \_\_\_\_"` with mdformat's escaped underscores, as the draft has them), and none is longer than two sentences. Borderline: 3.2 quotes the heading line "## Design" (heading, after Procedure) as its passage. After the fixes there are 50 (7.5 and 10.5 added), all verbatim in the rewritten draft.

### 13.2 and 13.3

Both rows read `not checked: defend-stage`.

### The checker on the first pass

```text
$ python3 "$P/scripts/check_proposal.py" review "$T/first-pass-review.md"; echo "exit=$?"
exit=0
```

Turn 2 itself ran the review checker twice: the first run reported `proposal/review.md:24: fix 14 appears before fix 4; fixes are numbered in order of appearance` (5.1's decide mentioned fix 14 by number); the skill reworded that mention to "the cut item 13.9 asks for" and the second run printed nothing.

## Fix-picking check

D4 is row 7.5, fix 6; D7 is row 10.5, fix 9, both paste-ready, in the first-pass file. Turn 3's prompt was "Apply fixes 6 and 9.".

The draft, `git -C "$S" diff -U0 ec60df0 bba36af -- proposal/draft.md`: exactly two hunks, `@@ -50,0 +51,2 @@` (a new third Procedure paragraph and its blank line) and `@@ -53 +55 @@` (Design paragraph 1). At git's default context the two fall in one hunk. `--word-diff=plain -U0` shows exactly two insertions and no deletions:

```text
{+If the experimenter falls ill, sessions will be rescheduled within the data-collection weeks rather than run by a second experimenter. If the display, a device or the study program fails, the session will stop, the partial log will be discarded, and the participant will be invited back once the identical hardware and the frozen software are restored.+}
{+The nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software with equal counts per combination.+}
```

Each insertion is its fix's quoted text, word for word (checked by substring), at the place the fix names ("add to Procedure"; "add to Design, after the device sentence"). Two insertions, two hunks at `-U0`: pass.

`proposal/review.md`, `git -C "$S" diff -U0 ec60df0 bba36af -- proposal/review.md`: five changed lines, all on the key's allowed list; every other line is byte-identical, and Waivers and Hand-off are unchanged.

| Line | What changed                                                                 | Allowed by the key                     |
| ---- | ---------------------------------------------------------------------------- | -------------------------------------- |
| 37   | row 7.5, fail to `pass (fix 6 applied)`                                      | yes, the 7.5 row                       |
| 57   | row 10.5, fail to `pass (fix 9 applied)`                                     | yes, the 10.5 row                      |
| 68   | row 13.5, drops 7.5 and 10.5 from its list, 2,456 to 2,536 words, still fail | yes, the 13.5 row                      |
| 82   | Brief against draft entry 7.5, `- fail` to `- pass (fix 6 applied)`          | yes, a Brief finding the fixes touched |
| 100  | Summary                                                                      | yes, the Summary                       |

The re-checked rows and the resolved finding:

```text
- **7.5** pass (fix 6 applied): "The nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software with equal counts per combination." (Design, para 1)
- **10.5** pass (fix 9 applied): "If the experimenter falls ill, sessions will be rescheduled within the data-collection weeks rather than run by a second experimenter." (Procedure, para 3)
- pass (fix 6 applied): entry 7.5's random order per participant with equal counts now stands in Design, para 1, "The nine distance-and-size combinations will be presented in a random order per participant, drawn by the study software with equal counts per combination."
```

The resolved Brief finding uses the new shape `- pass (fix N applied): ...` from 76e9c28. Summary after the fixes: `Items checked: 65. Pass: 54. Fail: 11. Not checked (defend-stage): 2. Consistency and brief findings: 10. Fixes proposed: 14. Waivers: 0.`, every count recomputed from the rows (fixes 6 and 9 stay counted, so the highest fix number is still 14). Turn 3 ran the review checker on its rewrite (no output). Scoring re-run:

```text
$ python3 "$P/scripts/check_proposal.py" review "$T/after-fixes-review.md"; echo "exit=$?"
exit=0
```

Turn 3's final message, before the hand-off:

```text
Fixes 6 and 9 applied to `proposal/draft.md`; `proposal/review.md` rewritten; checker exits 0 on both files' shapes.

**What changed:**

- Design, para 1 gained the combination-order sentence — item 7.5 now `pass (fix 6 applied)`, and the Brief departure for entry 7.5 flipped to `pass (fix 6 applied)`.
- Procedure gained a third paragraph with the illness and equipment contingency — item 10.5 now `pass (fix 9 applied)`.
- Item 13.5 still fails, now on items 1.3, 4.3, 5.1, 6.2, 7.2, 7.6, 8.2, 12.3, 12.5 and 13.9; body is 2,536 words, still inside 2,000–4,000.
- Summary: 65 checked, **54 pass, 11 fail**, 2 not checked, **10** consistency and brief findings, 14 fixes proposed, 0 waivers.
```

## Missing-input and not-frozen stops

No stop project holds a `proposal/review.md` afterwards, and `git status --porcelain` in each shows only its planted change: nothing was written. No stop's result event carries an `api_error_status`.

Brief deleted (`$S-nobrief`, rc=0, 20 s, 4 turns), final message:

```text
No design brief at proposal/design-brief.md; run /experiment-proposal:design first.

Found `proposal/draft.md` (19 KB), but review needs frozen brief as evidence base — brief drives item 3.1 mechanics, the Brief-against-draft section, and every departure flag. No brief, no review. Nothing written.
```

Stops with the skill's sentence, naming the brief and `/experiment-proposal:design`: pass.

Draft deleted (`$S-nodraft`, rc=0, 16 s, 3 turns), final message (the scratch path written as `$S-nodraft`):

```text
No draft. Brief frozen 2026-10-10, points `Draft: proposal/draft.md` — that path does not exist. Only file in `proposal/` is `design-brief.md`.

Tried: `$S-nodraft/proposal/draft.md`

Review needs draft. Write draft at that path (or name another path) and re-run `/experiment-proposal:review`.
```

Stops and names `proposal/draft.md`: pass.

Brief `Status: open` (`$S-open`, rc=0, 33 s, 5 turns), final message:

```text
Brief not frozen. Stop.

`proposal/design-brief.md` line 4 reads `Status: open`, not `frozen YYYY-MM-DD`. Review needs frozen brief. Run `/experiment-proposal:design` to finish it.

Brief also lists one open item — run `/experiment-proposal:lit-search` for a current-device comparison to cite under H1 — likely what blocks freeze.

No `proposal/review.md` written.
```

Stops and says the brief is not frozen: pass.

## Hand-off (research-grill present)

`~/.claude/plugins/installed_plugins.json` has the key `"oss@open-science-skills"` (its line 145), so the installed form is the right one. Turn 2 read the file with the Read tool before writing review.md; turn 3 did not read it again before printing the hand-off (see Defects outside the bar). The hand-off that ends the last pass message (turn 3), quoted:

```text
/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?
```

It ends turn 3's final message in full: the result string's last characters are `...the 13.9 necessity cut.\n\n/oss:research-grill defend proposal/draft.md\nSeed list: could someone run a session from the Method alone?`, nothing after it. Turn 2's final message ends with the same two lines, and both equal the file's Hand-off section. The seed list holds only the fixed question, which is right for this review: there are no waivers and no substance test passed narrowly (the two narrow passes, 2.4 and 10.3, are checklist items, not substance tests). Exact command and seed list, the final message ends with the hand-off in full: pass.

## Defects outside the bar

- Step 7's 76e9c28 rule, "Read the file each time you print the hand-off; an earlier reading is stale", was not followed in turn 3: its nine tool calls are two Edits of the draft, five Edits of review.md and two checker runs, with no Read of `installed_plugins.json` before the hand-off it printed. The printed form is still correct because nothing was installed or removed between turns 2 and 3.
- Step 2 says to run the draft checker "only with the user's values". Turns 2 and 3 each also ran it with `--words 2500-2501`, bounds the user never gave, to read the body's word count off the error line. The mechanics in the review come from the user-values run, and neither probe's word line became a finding.
- Turn 2's first Write gave row 13.5 a body count of "2,443 words" before the probe corrected it to 2,456.

## Harness events

- Permission denials: turn 2 had two, the checker with `; echo "EXIT=$?"` (re-run bare) and a `grep ... | head -60` into `$P/scripts/check_proposal.py` (the skill read the file with Read instead); the brief-deleted stop had one, a `find ...; echo "exit:$?"` (re-run bare). None changed an outcome. Turns 1 and 3 and the other two stops had none.
- No turn called the `Agent` tool, and no turn's tool input mentions `key.md` or `docs/research`.

## Pass bar

| Criterion                                                      | Result | Evidence                                                                                                        |
| -------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------- |
| At least 11 of 12 caught, 0 passed                             | pass   | 12 of 12 caught, 0 passed                                                                                       |
| At most two over-failures                                      | pass   | 0; all 38 controls pass (2.4 and 10.3 narrowly); 10.2 and 8.3 pass with the questionnaire after consent         |
| Draft checker reports D3, D8, D9 and nothing else              | pass   | the user-values run printed three lines: references, bullet list, supervision sentence                          |
| Every draft-checked pass quotes a passage with its location    | pass   | 48 of 48 verbatim with a location, none over two sentences; borderline heading quote at 3.2                     |
| 13.2 and 13.3 read not checked                                 | pass   | both `not checked: defend-stage`                                                                                |
| Checker exits 0 on review.md                                   | pass   | first pass exit 0; after fixes exit 0                                                                           |
| Picked fixes applied alone, affected rows re-checked           | pass   | fixes 6 and 9 (D4, D7); two insertions, two hunks at `-U0`; five allowed review.md lines                        |
| Missing-input and not-frozen stops                             | pass   | brief: the skill's sentence; draft: names `proposal/draft.md`; open: "Brief not frozen. Stop."                  |
| Turn 1 waited for the template values and the attested answers | pass   | turn 1: Reads only, no review.md, no checker run; both batches asked in one message                             |
| Hand-off (research-grill present), final message ends with it  | pass   | exact defend command and seed list end turns 2 and 3; turn 3 did not re-read the plugins file (outside the bar) |

## Verdict

Run v2-5 of scenario 5 at 76e9c28: pass. 12 of 12 caught, 0 passed, 0 over-failures, the review checker exits 0 on both files, the two picked fixes applied alone, the three stops hold, and turn 1 waited. Outside the bar: turn 3 printed the hand-off without re-reading the plugins file, and the draft checker was twice run with probe word bounds to read the word count.
