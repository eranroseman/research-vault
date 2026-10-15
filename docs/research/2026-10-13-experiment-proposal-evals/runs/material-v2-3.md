# Scenario 2 (material with gaps) at 0.2.0, run v2-3

Date: 2026-10-15
Plugin commit: 5e13529 (`experiment-proposal` 0.2.0)
Fixture: `fixtures/material-with-gaps.md`, copied in as `material.md`; key `fixtures/material-with-gaps.key.md` (21 rows).
Model: `--model opus`, which the init event of the stream reports as `claude-opus-5`.

## Command (one turn, no answers given)

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/material-v2-3
mkdir -p "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/material-with-gaps.md "$S/material.md"
cd "$S" && git add -A && git commit -qm fixtures
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:design material.md" > "$S.turn1.jsonl"
```

The raw stream-json output is kept outside the repository as `$S.turn1.jsonl`. The run exited 0 after 15 turns in 279 s. The skill did not stop to ask for the draft path (see the notes), so no `--continue` turn was needed: the extraction table and round 1 both came in turn 1, and no round was answered.

Environment: the user-level plugins ran their SessionStart hooks in the scratch session (the init event lists them), including a global caveman hook ("CAVEMAN MODE ACTIVE"). It had no visible effect on the table or the questions.

## Decisive transcript lines

```text
Repo found. Brief written open at `proposal/design-brief.md`, checker exits 0.
**Draft path:** assumed `proposal/draft.md` (in the brief's header). Say otherwise and I change it.
## Extraction: design-tree items
... 7.2 carry-over | settled | "carry-over between the keyboards is symmetric, each is a few minutes of practice away" (## Variables)
... 7.3 design named | missing | The design is never named (for example 2-level within-subjects)
... 7.5 counterbalancing | missing | Order of the two keyboards is not addressed
Settled items are already entries in the brief. Blocked this round: 2.2 and 8.5 (wait on 7.3), 2.5 (waits on 2.4).
## Round 1 — eight questions
**Q4 — item 7.3, naming the design.**
**Q5 — item 7.5, counterbalancing (balancing the order of the two keyboards so order cannot masquerade as an effect).**
```

## Per-row comparison with the key

| Item | Key     | Extraction | Asked in round 1?   | Match |
| ---- | ------- | ---------- | ------------------- | ----- |
| 1.1  | settled | settled    | no                  | match |
| 1.2  | settled | settled    | no                  | match |
| 1.3  | weak    | weak       | Q1                  | match |
| 2.2  | missing | missing    | no (blocked on 7.3) | match |
| 2.3  | settled | settled    | no                  | match |
| 2.4  | missing | missing    | Q2                  | match |
| 2.5  | missing | missing    | no (blocked on 2.4) | match |
| 6.1  | settled | settled    | no                  | match |
| 6.2  | weak    | weak       | Q3                  | match |
| 6.5  | settled | settled    | no                  | match |
| 7.1  | settled | settled    | no                  | match |
| 7.2  | settled | settled    | no                  | match |
| 7.3  | missing | missing    | Q4                  | match |
| 7.4  | settled | settled    | no                  | match |
| 7.5  | missing | missing    | Q5                  | match |
| 7.6  | weak    | weak       | Q6                  | match |
| 7.7  | weak    | weak       | Q7                  | match |
| 7.8  | settled | settled    | no                  | match |
| 7.9  | weak    | weak       | Q8                  | match |
| 8.3  | settled | settled    | no                  | match |
| 8.5  | missing | missing    | no (blocked on 7.3) | match |

Items in the printed table that the key does not list: none (21 rows printed, the 21 key rows).

## Round 1, as asked

Round 1 asked item IDs 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9 (Q1 to Q8, in checklist order). The skill listed the rows it deferred: "Blocked this round: 2.2 and 8.5 (wait on 7.3), 2.5 (waits on 2.4)."

- Q1, item 1.3, how long the raw data are kept.
- Q2, item 2.4, the timeline.
- Q3, item 6.2, the hypotheses' sources and H2's form.
- Q4, item 7.3, naming the design.
- Q5, item 7.5, counterbalancing; `Recommended (hci-researcher)`.
- Q6, item 7.6, reliability, construct validity and the ease rating; `Recommended (hci-researcher)`.
- Q7, item 7.7, the control variables; `Recommended (hci-researcher)`.
- Q8, item 7.9, confounds; `Recommended (hci-researcher)`.

## Other behaviour

- The open brief: written to `proposal/design-brief.md` with `Status: open`, `Checklist: experiment-proposal 0.2.0`, 10 entries (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3), every entry `Status: settled`. The checker (`check_proposal.py brief`) exits 0 on it (re-run by the driver after the session). Nothing was committed, which is right for an open brief.
- Reads: the checklist, the material, `references/brief.md`, `.claude-plugin/plugin.json` and `scripts/check_proposal.py` (all plugin files), plus one `ls -la` of the project root (the material was re-read four more times, between and after the four subagent calls). The scratch project holds only `material.md`, so nothing else in the project could have been read. Neither the key nor any `docs/research` file was opened (a grep of the stream for `key.md`, `material-with-gaps` and `docs/research` finds nothing).
- `hci-researcher`: four calls to `experiment-proposal:hci-researcher`, for items 7.5, 7.7, 7.9 and 7.6, one question per call (the 7.6 call came after the brief had been written). Each call carried one question with the material's relevant passages and its answer was quoted as `Recommended (hci-researcher)`.
- Permission refusals the skill recovered from (harness side, not counted against the plugin): a Bash `cd <plugin> && cat plugin.json` ("cd ... was blocked ... may only change directories to the allowed working directories"), recovered by a Read of plugin.json; and `python3 ... check_proposal.py ... ; echo "exit=$?"` ("The following part requires approval: echo"), re-run without the echo (exit 0, no output).

## Pass-bar criteria

- Every row keyed weak or missing appears in the extraction as weak or missing: pass. All 11 keyed rows (1.3, 2.2, 2.4, 2.5, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9, 8.5) printed with the key's own status.

- No row keyed settled is asked in round 1: pass. The 10 settled rows (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3) were each printed settled and none is the item of a numbered question; the items asked were 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9. See the notes for a recommendation that touches settled 8.3.

## Verdict

PASS (both bar clauses hold; 21 of 21 key rows match).

## Notes

- Q7 (item 7.7) folds a change to settled item 8.3 into its recommendation: "Accepting this also changes the item 8.3 entry", and the subagent text relaxes right-handedness and the no-prior-swipe criterion. No numbered question names 8.3 as its item, so it does not count as asked under the item-ID reading used in the 0.1.0 records; flagged because a stricter reading would count Q7.
- Q3 offers to restate H2 as RQ2 or as a non-inferiority claim with a margin, touching the settled content of 6.1; the question's item is 6.2.
- Q6 recommends the SUS as the primary RQ1 measure, from the subagent; a recommendation, not a decision.
- Draft path: not asked as a question; "**Draft path:** assumed `proposal/draft.md` (in the brief's header). Say otherwise and I change it."
- Only the first turn ran; no round was answered.
