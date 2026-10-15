# Scenario 2 (material with gaps) at 0.2.0, run v2-1

Date: 2026-10-15
Plugin commit: 5e13529 (`experiment-proposal` 0.2.0)
Fixture: `fixtures/material-with-gaps.md`, copied in as `material.md`; key `fixtures/material-with-gaps.key.md` (21 rows).
Model: `--model opus`, which the init event of the stream reports as `claude-opus-5`.

## Command (one turn, no answers given)

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/material-v2-1
mkdir -p "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/material-with-gaps.md "$S/material.md"
cd "$S" && git add -A && git commit -qm fixtures
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:design material.md" > "$S.turn1.jsonl"
```

The raw stream-json output is kept outside the repository as `$S.turn1.jsonl`. The run exited 0 after 14 turns in 300 s. The skill did not stop to ask for the draft path (see the notes), so no `--continue` turn was needed: the extraction table and round 1 both came in turn 1, and no round was answered.

Environment: the user-level plugins ran their SessionStart hooks in the scratch session (the init event lists them), including a global caveman hook ("CAVEMAN MODE ACTIVE"). It had no visible effect on the table or the questions.

## Decisive transcript lines

```text
Brief written, checker clean. Draft path: assuming `proposal/draft.md` — say otherwise and I change the header.
## Extraction: 21 design-tree items
... 7.2 carry-over | settled | "carry-over between the keyboards is symmetric, each is a few minutes of practice away" (## Variables)
... 7.3 design named | weak | Pieces present, design never named; no statement that preference measures are within subjects
... 7.5 counterbalancing | missing | Order of the two keyboards never mentioned
Blocked to round 2: 2.2 and 8.5 (need 7.3), 2.5 (needs 2.4).
**Q4 — item 7.3, name the overall design.**
**Q5 — item 7.5, counterbalancing (the order participants meet the two keyboards).**
```

## Per-row comparison with the key

| Item | Key     | Extraction | Asked in round 1?       | Match |
| ---- | ------- | ---------- | ----------------------- | ----- |
| 1.1  | settled | settled    | no                      | match |
| 1.2  | settled | settled    | no                      | match |
| 1.3  | weak    | weak       | Q1                      | match |
| 2.2  | missing | missing    | no (blocked on 7.3)     | match |
| 2.3  | settled | settled    | no                      | match |
| 2.4  | missing | missing    | Q2                      | match |
| 2.5  | missing | missing    | no (blocked on 2.4)     | match |
| 6.1  | settled | settled    | no                      | match |
| 6.2  | weak    | weak       | Q3                      | match |
| 6.5  | settled | settled    | no                      | match |
| 7.1  | settled | settled    | no                      | match |
| 7.2  | settled | settled    | no                      | match |
| 7.3  | missing | weak       | Q4                      | match |
| 7.4  | settled | settled    | no                      | match |
| 7.5  | missing | missing    | Q5                      | match |
| 7.6  | weak    | weak       | no (omitted, see notes) | match |
| 7.7  | weak    | weak       | Q6                      | match |
| 7.8  | settled | settled    | no                      | match |
| 7.9  | weak    | weak       | Q7                      | match |
| 8.3  | settled | settled    | no                      | match |
| 8.5  | missing | missing    | no (blocked on 7.3)     | match |

Items in the printed table that the key does not list: none (21 rows printed, the 21 key rows).

## Round 1, as asked

Round 1 asked item IDs 1.3, 2.4, 6.2, 7.3, 7.5, 7.7, 7.9 (Q1 to Q7, in checklist order). Each question carries the item, a `Why this matters:` line and a `Recommended:` line. The skill listed the rows it deferred: "Blocked to round 2: 2.2 and 8.5 (need 7.3), 2.5 (needs 2.4)."

- Q1, item 1.3, how long the raw data are kept.
- Q2, item 2.4, the timeline.
- Q3, item 6.2, H2 is not testable as written (recommends demoting it to RQ2).
- Q4, item 7.3, name the overall design.
- Q5, item 7.5, counterbalancing; `Recommended (hci-researcher)`.
- Q6, item 7.7, the controls, weighed; `Recommended (hci-researcher)`.
- Q7, item 7.9, the confounds; `Recommended (hci-researcher)`.

## Other behaviour

- The open brief: written to `proposal/design-brief.md` with `Status: open`, `Checklist: experiment-proposal 0.2.0`, 10 entries (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3), every entry `Status: settled`. The checker (`check_proposal.py brief`) exits 0 on it (re-run by the driver after the session). Nothing was committed, which is right for an open brief.
- Reads: the checklist, the material, `references/brief.md`, `.claude-plugin/plugin.json` and `scripts/check_proposal.py` (all plugin files), plus one `ls -la` of the project root (git root and listing). The scratch project holds only `material.md`, so nothing else in the project could have been read. Neither the key nor any `docs/research` file was opened (a grep of the stream for `key.md`, `material-with-gaps` and `docs/research` finds nothing).
- `hci-researcher`: three calls to `experiment-proposal:hci-researcher`, for items 7.5, 7.7 and 7.9, one question per call. Each call carried one question with the material's relevant passages and its answer was quoted as `Recommended (hci-researcher)`.
- Permission refusals the skill recovered from (harness side, not counted against the plugin): a Bash `cd <plugin> && cat plugin.json && git -C ...` ("This command changes directory before running a version-control command"), recovered by a Read of plugin.json; and `python3 ... check_proposal.py ... ; echo "exit=$?"` ("The following part requires approval: echo"), re-run without the echo (exit 0, no output).

## Pass-bar criteria

- Every row keyed weak or missing appears in the extraction as weak or missing: pass. 11 rows keyed weak or missing (1.3, 2.2, 2.4, 2.5, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9, 8.5); all 11 printed as weak or missing (7.3 printed weak where the key says missing, which the key makes interchangeable).

- No row keyed settled is asked in round 1: pass. The 10 settled rows (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3) were each printed settled and none is the item of a numbered question; the items asked were 1.3, 2.4, 6.2, 7.3, 7.5, 7.7, 7.9. See the notes for two recommendations that touch settled items.

## Verdict

PASS (both bar clauses hold; 21 of 21 key rows match).

## Notes

- Item 7.6 (weak, depends only on 1.1, which is settled) was in the frontier but is neither asked in round 1 nor named as blocked. Step 3 says "Ask the whole frontier in one round". It is printed weak in the table, so the bar holds; the omission is a completeness gap in the round, not a bar miss.
- Q6 folds a change to settled item 8.3 into the 7.7 recommendation: "(this changes your settled item 8.3, so say if you would rather keep the screen)". Q7 closes with "Note on Q7: the subagent's wording would 'drop the symmetric-carry-over claim'. I read that as testing the assumption rather than overturning your settled item 7.2". No numbered question names 8.3 or 7.2 as its item, so neither counts as asked under the item-ID reading used in the 0.1.0 records; flagged because a stricter reading would count Q6.
- Q3 recommends demoting H2 to RQ2, which would change the settled content of 6.1; the question's item is 6.2.
- Draft path: not asked as a question; the first line says "assuming `proposal/draft.md` — say otherwise and I change the header". Step 1 reads "Ask once for the draft's planned path (`proposal/draft.md` unless they say otherwise)".
- Only the first turn ran; no round was answered.
