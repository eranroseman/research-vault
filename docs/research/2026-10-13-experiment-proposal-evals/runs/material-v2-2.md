# Scenario 2 (material with gaps) at 0.2.0, run v2-2

Date: 2026-10-15
Plugin commit: 5e13529 (`experiment-proposal` 0.2.0)
Fixture: `fixtures/material-with-gaps.md`, copied in as `material.md`; key `fixtures/material-with-gaps.key.md` (21 rows).
Model: `--model opus`, which the init event of the stream reports as `claude-opus-5`.

## Command (one turn, no answers given)

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/material-v2-2
mkdir -p "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/material-with-gaps.md "$S/material.md"
cd "$S" && git add -A && git commit -qm fixtures
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:design material.md" > "$S.turn1.jsonl"
```

The raw stream-json output is kept outside the repository as `$S.turn1.jsonl`. The run exited 0 after 15 turns in 467 s. The skill did not stop to ask for the draft path (see the notes), so no `--continue` turn was needed: the extraction table and round 1 both came in turn 1, and no round was answered.

Environment: the user-level plugins ran their SessionStart hooks in the scratch session (the init event lists them), including a global caveman hook ("CAVEMAN MODE ACTIVE"). It had no visible effect on the table or the questions.

## Decisive transcript lines

```text
Brief written and the checker passes (no output = exit 0). Draft path: I used `proposal/draft.md` — say so if you want a different one.
## Extraction against the design tree
... 7.2 symmetric carry-over | weak | "carry-over … is symmetric, each is a few minutes of practice away" conflicts with item 8.3, which screens swipe-naive participants who own smartphones: tap is practised, swipe is novel (## Variables)
... 7.3 design named | weak | no design name anywhere
... 7.5 counterbalancing | missing | order of the two keyboards is never mentioned
Nine settled entries are in the brief. Blocked until this round lands: 2.2 (on 7.3), 2.5 (on 2.4), 7.5 (on 7.2), 8.5 (on 7.3 and 7.6).
**Q4 — item 7.2, carry-over.** Your participants all type on phone tap keyboards and none has used watch swipe, so one condition is measured on a practised skill and the other on a new one. Do you add a practice block before each keyboard's measured trials ...
Why this matters: the carry-over is asymmetric as the design stands, which counterbalancing cannot remove; ...
Recommended (hci-researcher): keep keyboard within subjects and add practice to criterion. ...
```

The key row for 7.2: "settled | carry-over argued symmetric".

## Per-row comparison with the key

| Item | Key     | Extraction | Asked in round 1?        | Match    |
| ---- | ------- | ---------- | ------------------------ | -------- |
| 1.1  | settled | settled    | no                       | match    |
| 1.2  | settled | settled    | no                       | match    |
| 1.3  | weak    | weak       | Q1                       | match    |
| 2.2  | missing | missing    | no (blocked on 7.3)      | match    |
| 2.3  | settled | settled    | no                       | match    |
| 2.4  | missing | missing    | Q2                       | match    |
| 2.5  | missing | missing    | no (blocked on 2.4)      | match    |
| 6.1  | settled | settled    | no                       | match    |
| 6.2  | weak    | weak       | Q3                       | match    |
| 6.5  | settled | settled    | no                       | match    |
| 7.1  | settled | settled    | no                       | match    |
| 7.2  | settled | weak       | Q4                       | MISMATCH |
| 7.3  | missing | weak       | Q5                       | match    |
| 7.4  | settled | settled    | no                       | match    |
| 7.5  | missing | missing    | no (blocked on 7.2)      | match    |
| 7.6  | weak    | weak       | Q6                       | match    |
| 7.7  | weak    | weak       | Q7                       | match    |
| 7.8  | settled | settled    | no                       | match    |
| 7.9  | weak    | weak       | Q8                       | match    |
| 8.3  | settled | settled    | no                       | match    |
| 8.5  | missing | missing    | no (blocked on 7.3, 7.6) | match    |

Items in the printed table that the key does not list: none (21 rows printed, the 21 key rows).

## Round 1, as asked

Round 1 asked item IDs 1.3, 2.4, 6.2, 7.2, 7.3, 7.6, 7.7, 7.9 (Q1 to Q8, in checklist order). The skill listed the rows it deferred: "Blocked until this round lands: 2.2 (on 7.3), 2.5 (on 2.4), 7.5 (on 7.2), 8.5 (on 7.3 and 7.6)."

- Q1, item 1.3, the data plan.
- Q2, item 2.4, the timeline.
- Q3, item 6.2, H2's form.
- Q4, item 7.2, carry-over. KEYED SETTLED.
- Q5, item 7.3, the design's name.
- Q6, item 7.6, the dependent variables.
- Q7, item 7.7, the control variables; `Recommended (hci-researcher)`.
- Q8, item 7.9, the confounds; `Recommended (hci-researcher)`.

## Other behaviour

- The open brief: written to `proposal/design-brief.md` with `Status: open`, `Checklist: experiment-proposal 0.2.0`, 9 entries (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.4, 7.8, 8.3; 7.2 is not an entry), every entry `Status: settled`. The checker (`check_proposal.py brief`) exits 0 on it (re-run by the driver after the session). Nothing was committed, which is right for an open brief.
- Reads: the checklist, the material, `references/brief.md`, `.claude-plugin/plugin.json` and `scripts/check_proposal.py` (all plugin files), plus one `ls -la` of the project root and two `Glob **/*.md` calls on the project (listing, not reading; the material was re-read twice). The scratch project holds only `material.md`, so nothing else in the project could have been read. Neither the key nor any `docs/research` file was opened (a grep of the stream for `key.md`, `material-with-gaps` and `docs/research` finds nothing).
- `hci-researcher`: three calls to `experiment-proposal:hci-researcher`, for items 7.2, 7.7 and 7.9, one question per call. Step 4 names 7.5 for delegation; 7.5 was blocked behind the downgraded 7.2, so it got no call and no question. Each call carried one question with the material's relevant passages and its answer was quoted as `Recommended (hci-researcher)`.
- Permission refusals the skill recovered from (harness side, not counted against the plugin): a Bash `cd <plugin> && cat plugin.json` ("cd ... was blocked ... may only change directories to the allowed working directories"), recovered by a Read of plugin.json; and `python3 ... check_proposal.py ... ; echo "exit=$?"` ("The following part requires approval: echo"), re-run without the echo (exit 0, no output).

## Pass-bar criteria

- Every row keyed weak or missing appears in the extraction as weak or missing: pass. All 11 keyed rows (1.3, 2.2, 2.4, 2.5, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9, 8.5) printed weak or missing.

- No row keyed settled is asked in round 1: FAIL. Item 7.2 is keyed settled; the extraction printed it `weak` ("conflict with another item": item 8.3 screens swipe-naive participants, so tap is practised and swipe novel) and Q4 asks it. The other nine settled rows (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.4, 7.8, 8.3) were printed settled and not asked.

## Verdict

FAIL on the second bar clause (item 7.2, keyed settled, was printed weak and asked as Q4). The first clause holds; 20 of 21 key rows match.

## Notes

- The miss traces to step 2's definition of `weak`: "a decision without a reason, a reason that does not fit this experiment, or a conflict with another item". The run used the last clause to reopen 7.2 against 8.3. The material argues the carry-over as symmetric ("each is a few minutes of practice away from the other") and the key accepts that; the run's counter-argument (a phone-practised tap keyboard against a novel swipe one) is a real HCI concern: in runs 1 and 3 the subagent raised the same asymmetry as a novelty confound under 7.9, and in run 1 its wording would have dropped the symmetric-carry-over claim, which that run declined to treat as overturning 7.2. Whether this is a skill defect (the conflict clause is too permissive) or a key disagreement is the author's call; the record scores against the key as written.
- Consequences inside the run: the brief has 9 entries instead of 10; 7.5 was deferred to round 2 because it depends on 7.2; the hci-researcher was consulted on 7.2 instead of 7.5.
- Q3 recommends demoting H2 to RQ2 (as in run 1), touching the settled content of 6.1; the question's item is 6.2.
- Row 2.2 of the printed table cites its source as "(## nothing)", a stray heading label.
- Draft path: not asked as a question; "Draft path: I used `proposal/draft.md` — say so if you want a different one."
- Only the first turn ran; no round was answered.
- Scenario 2's bar needs all three runs to meet it; with this run failing, the scenario does not hold at 5e13529 on these three runs.
