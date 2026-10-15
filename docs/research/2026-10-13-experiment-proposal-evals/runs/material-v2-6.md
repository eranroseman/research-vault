# Scenario 2 (material with gaps) at 0.2.0, run v2-6 (design fix re-run)

Date: 2026-10-15
Plugin commit: 76e9c28 (`experiment-proposal` 0.2.0). The fix commit that matters for this scenario is ed96208 (design: a settled item stays settled, the frontier is listed above Q1, the checker runs each round, the draft path defaults to `proposal/draft.md`); 76e9c28 is the review and fixture fix on top of it. The harness file names 5e13529, the commit of runs v2-1 to v2-3.
Fixture: `fixtures/material-with-gaps.md`, copied in as `material.md`; key `fixtures/material-with-gaps.key.md` (21 rows).
Model: `--model opus`, which the init event of the stream reports as `claude-opus-5`.
What this run tests: run v2-2 at 5e13529 failed the second bar clause, because the extraction printed item 7.2 (carry-over, keyed settled) as `weak` and asked it as Q4. Step 2 now defines `weak` without the "conflict with another item" clause, and step 3 says "A settled item stays settled: a concern about it goes in the basis of a recommendation that bears on it, never into a question or a change to its entry."

## Command (one turn, no answers given)

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/material-v2-6
mkdir "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/material-with-gaps.md "$S/material.md"
cd "$S" && git add -A && git commit -qm fixtures
printf '%s' '/experiment-proposal:design material.md' > "$S.turn1.prompt"
bash /tmp/ep-eval/review-v2-drive.sh "$S" 1
```

The helper runs, in turn 1, exactly the harness command:

```bash
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null
```

The scratch directory did not exist before the run. The raw stream-json output is kept outside the repository as `$S.turn1.jsonl`. The run exited 0 (`rc=0 secs=322`; the final JSON reports `subtype` `success`, `is_error` false, `api_error_status` null, 13 turns, `terminal_reason` `completed`). The skill did not stop to ask for the draft path, so no `--continue` turn was needed: the extraction table and round 1 both came in turn 1, and no round was answered.

Rate limit: no 429 and no "session limit" in the final JSON (`api_error_status` null; the string "session limit" appears nowhere in the stream). Two of the three `hci-researcher` replies open with "Advisor is rate-limited; answering from knowledge" (the subagent's own advisor tool, not the headless turn); they answered from knowledge as instructed, and the turn itself completed.

Environment: the user-level plugins ran their SessionStart hooks in the scratch session (the init event lists 20 plugins), including a global caveman hook ("CAVEMAN MODE ACTIVE"). It had no visible effect on the table or the questions.

## Decisive transcript lines

The extraction table came in an earlier text block of turn 1 (before the brief was written); the final message of the turn holds round 1.

```text
Repo at `/tmp/ep-eval/material-v2-6`. Draft path: `proposal/draft.md` (user named none).
## Extraction: every design-tree item
... 7.2 carry-over | settled | "carry-over between the keyboards is symmetric, each is a few minutes of practice away from the other" (## Variables)
... 7.3 design named | missing | No design name, no statement that the two levels are crossed with nothing
... 7.5 counterbalancing | missing | Order of the two keyboards never mentioned
Writing the open brief now.
Brief written; checker exits 0.
**Round 1 frontier: items 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9.**
**Q4 — item 7.3, what is the design called?**
**Q5 — item 7.5, how is the order of the two keyboards counterbalanced?**
The subagent attaches a caveat that bears on your settled item 7.2: ... Its fix, which I recommend you adopt as part of this item rather than reopening 7.2: an identical unrecorded practice block before each keyboard ...
Answer Q1–Q8 in any order; a "yes" takes the recommendation as written. Blocked behind these: items 2.2 and 8.5 (need 7.3), 2.5 (needs 2.4).
```

(The table lines are abbreviated here; the full 21-row table is in the stream and summarised below.)

## Per-row comparison with the key

| Item | Key     | Extraction | Asked in round 1?                                                             | Match |
| ---- | ------- | ---------- | ----------------------------------------------------------------------------- | ----- |
| 1.1  | settled | settled    | no                                                                            | match |
| 1.2  | settled | settled    | no                                                                            | match |
| 1.3  | weak    | weak       | Q1                                                                            | match |
| 2.2  | missing | missing    | no (blocked on 7.3)                                                           | match |
| 2.3  | settled | settled    | no                                                                            | match |
| 2.4  | missing | missing    | Q2                                                                            | match |
| 2.5  | missing | missing    | no (blocked on 2.4)                                                           | match |
| 6.1  | settled | settled    | no                                                                            | match |
| 6.2  | weak    | weak       | Q3                                                                            | match |
| 6.5  | settled | settled    | no                                                                            | match |
| 7.1  | settled | settled    | no                                                                            | match |
| 7.2  | settled | settled    | no (no numbered question; named in Q5's recommendation text, entry unchanged) | match |
| 7.3  | missing | missing    | Q4                                                                            | match |
| 7.4  | settled | settled    | no                                                                            | match |
| 7.5  | missing | missing    | Q5                                                                            | match |
| 7.6  | weak    | weak       | Q6                                                                            | match |
| 7.7  | weak    | weak       | Q7                                                                            | match |
| 7.8  | settled | settled    | no                                                                            | match |
| 7.9  | weak    | weak       | Q8                                                                            | match |
| 8.3  | settled | settled    | no                                                                            | match |
| 8.5  | missing | missing    | no (blocked on 7.3 and 7.6)                                                   | match |

Items in the printed table that the key does not list: none (21 rows printed, the 21 key rows). 21 of 21 rows match.

## Round 1, as asked

The frontier line above Q1 lists 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9. Recomputed from the checklist's `depends on` fields with the extraction's statuses, that set is correct: each listed item's design-tree dependencies are settled (1.3 on 1.1; 2.4 on 2.3; 6.2 on 6.1; 7.3 on 7.1 and 6.5; 7.5 on 7.2; 7.6 on 1.1; 7.7 on 7.1; 7.9 on 7.1), and each unlisted weak or missing item has an unsettled dependency (2.2 on 7.3; 2.5 on 2.4; 8.5 on 7.3 and 7.6). Q1 to Q8 ask exactly those eight items, in checklist order, one each:

- Q1, item 1.3, retention of the raw data.
- Q2, item 2.4, the timeline.
- Q3, item 6.2, the sources behind H1's and H2's directions.
- Q4, item 7.3, the design's name.
- Q5, item 7.5, counterbalancing; `Recommended (hci-researcher)`.
- Q6, item 7.6, reliability and construct validity of the dependent variables.
- Q7, item 7.7, the control variables; `Recommended (hci-researcher)`.
- Q8, item 7.9, the confounds; `Recommended (hci-researcher)`.

Every question carries the question, a `Why this matters:` line and a `Recommended:` line with its basis.

Where settled items appear in round 1 (none is a numbered question):

- Q5 (item 7.5): the recommendation relays the subagent's caveat that screening for "never used a swipe keyboard on a watch" makes transfer asymmetric, and proposes an identical unrecorded practice block before each keyboard and a keyboard by order diagnostic, "rather than reopening 7.2". Item 7.2 is named in the recommendation text, not in the question or a `Basis:` line.
- Q8 (item 7.9): one recommendation bullet, "Order and asymmetric transfer", calls the symmetric-carry-over claim "the design's single most load-bearing assumption"; item 7.2 is not named by ID.
- Q3 mentions that H2 could flip direction after the literature search (item 6.1's content, in the recommendation); Q4's basis names the settled 7.1 and 6.5 entries; Q7's `Why this matters:` line names item 8.3 as depending on 7.7, and its recommendation proposes changes to how handedness and prior swipe use are screened (criteria that item 8.3 lists).
- No settled item is in the frontier, none has a number of its own, and every settled entry in the brief is unchanged (see below).

## Other behaviour

- The open brief: written to `proposal/design-brief.md` with `Draft: proposal/draft.md`, `Status: open`, `Checklist: experiment-proposal 0.2.0`, 10 entries (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3), every entry `Status: settled`, each with a quoted rationale and source from the material; 6 Looked up lines; 1 Open item (run `/experiment-proposal:lit-search` for H1's and H2's sources). The 7.2 entry keeps the material's decision and rationale ("each is a few minutes of practice away from the other"). The skill ran the checker on it (`check_proposal.py brief proposal/design-brief.md`, no output, and the turn's last message says "checker exits 0"); the driver re-ran it after the session: exit 0, no output. Nothing was committed in the scratch project (`git log` shows only `fixtures`), which is right for an open brief.
- The draft path: stated twice in turn 1 as assistant text ("Draft path: `proposal/draft.md` (none named by user)", then "Draft path: `proposal/draft.md` (user named none)") and written in the brief's `Draft:` line. It is not repeated in the turn's final message.
- Reads: the checklist, the material, `references/brief.md` and `.claude-plugin/plugin.json` (all plugin files except the material), plus one Bash call `git rev-parse --show-toplevel; ls -la; ls -la proposal` (exit 2 only because `proposal/` did not exist yet). The scratch project holds only `material.md`. Neither the key nor any `docs/research` file was opened (a grep of the stream for `key.md`, `material-with-gaps` and `docs/research` finds nothing).
- `hci-researcher`: three calls to `experiment-proposal:hci-researcher`, for items 7.5, 7.7 and 7.9, one question per call, issued during extraction (before the table was printed). The 7.5 call listed the settled decisions with their quotes and asked in part (b) "whether the researcher's symmetric-carry-over claim is safe given that participants are screened to have NEVER used a swipe keyboard on a watch"; its answer is what surfaced in Q5. The answers were quoted as `Recommended (hci-researcher)`.
- Permission refusal the skill recovered from (harness side, not counted against the plugin): a Bash `cd <plugin> && cat .claude-plugin/plugin.json | head -20` ("contains multiple operations ... requires approval"), recovered by a Read of `plugin.json`. The final JSON lists this one `permission_denials` entry.
- Blocked line: the last message says "items 2.2 and 8.5 (need 7.3), 2.5 (needs 2.4)"; item 8.5 also needs 7.6, which is in the same frontier, so the line is incomplete but the sets are right.
- Only the first turn ran; no round was answered.

## Pass-bar criteria

- Every row keyed weak or missing appears in the extraction as weak or missing: pass. All 11 keyed rows (1.3, 2.2, 2.4, 2.5, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9, 8.5) printed weak or missing (1.3, 6.2, 7.6, 7.7, 7.9 weak; 2.2, 2.4, 2.5, 7.3, 7.5, 8.5 missing).

- No row keyed settled is asked again, where "asked again" means a numbered question names it or its entry changes (a mention in a recommendation's basis is not asking): pass. The 10 keyed-settled rows (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3) were printed settled, none is in the frontier line, none has a question of its own, and all 10 brief entries are unchanged and `settled`. Item 7.2, the row v2-2 failed, is printed settled and its entry is intact. Borderline point for the reader: Q5's recommendation names item 7.2 and its practice-block advice bears on the settled carry-over claim. It is a recommendation for item 7.5 that says it is adopted "rather than reopening 7.2", so under the bar as written it is a mention in a recommendation, not asking; on a stricter reading of "a numbered question names it" it would count against the run.

- Also recorded. Frontier item IDs listed above Q1: yes (`Round 1 frontier: items 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9.`). Every frontier item asked: yes (8 items, Q1 to Q8). Draft path stated: yes, in the turn (twice) and in the brief header, but not in the final message. Open brief written: yes. Checker run on it: yes, by the skill (exit 0) and again by the driver (exit 0).

## Verdict

PASS. All 11 keyed weak or missing rows print weak or missing, and no keyed-settled row is asked; 21 of 21 key rows match, and the failure of v2-2 (item 7.2 printed `weak` and asked as Q4) does not recur: item 7.2 is printed settled, is not in the frontier and has no question, and the concern about it moved into the recommendation to Q5 as step 3 now directs.

## Notes

- This run alone does not decide the scenario: the bar needs every run of the re-run set to meet it.
- The earlier miss traced to step 2's old definition of `weak` (a conflict with another item). This run's subagent consult still probed 7.2 (the 7.5 prompt asked part (b) about the symmetric-carry-over claim) and the answer reached the user inside Q5's recommendation. The skill's rule allows that; whether a recommendation this long about a settled item should count as "bearing on" it is the author's call.
- Q3 again recommends keeping both directions and notes H2 could flip, without demoting H2 to a research question (v2-2 and run 1 demoted it); the question's item is 6.2.
- The extraction table is in an assistant text block of the turn, not in the turn's last message; a reader of only the last message sees round 1 and the brief status, not the table.
