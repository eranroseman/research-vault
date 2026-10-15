# Scenario 2 (material with gaps) at 0.2.0, run v2-4, on the fixed design skill

Date: 2026-10-15
Plugin commit: 76e9c28 (`experiment-proposal` 0.2.0). The fix that matters for this scenario is ed96208 (design keeps settled items settled, lists the frontier, runs the checker each round, defaults the draft path); 76e9c28 is the review and fixture fix on top of it. The harness file names 5e13529, which is the commit of runs v2-1 to v2-3.
Fixture: `fixtures/material-with-gaps.md`, copied in as `material.md`; key `fixtures/material-with-gaps.key.md` (21 rows).
Model: `--model opus`, which the init event of the stream reports as `claude-opus-5`.

## Commands (one turn, no answers given)

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/material-v2-4
# the directory did not exist before this run
mkdir -p "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/material-with-gaps.md "$S/material.md"
cd "$S" && git add -A && git commit -qm fixtures
printf '%s' "/experiment-proposal:design material.md" > "$S.turn1.prompt"
bash /tmp/ep-eval/review-v2-drive.sh "$S" 1
```

The helper reads the prompt from `$S.turn1.prompt` and, for turn 1, runs exactly the harness command: `cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null`, with `P` the plugin path above. Its meta file reads `rc=0 secs=446`.

The raw stream-json output is kept outside the repository as `$S.turn1.jsonl`. The turn ended `subtype: success`, `is_error: false`, `api_error_status: null`, 15 turns, 443 s, 4 subagent calls. All six `rate_limit_event` lines of the stream read `status: allowed` (five-hour utilization 0.13 to 0.17); "session limit" and 429 do not occur, so no harness-fail applies (see Other behaviour for the three "advisor was rate-limited" strings). The skill did not stop to ask for anything before the extraction, so no `--continue` turn was needed: the extraction table and round 1 both came in turn 1, and no round was answered.

Environment: the user-level plugins ran their SessionStart hooks in the scratch session (the init event lists them), including a global caveman hook. It had no visible effect on the table or the questions.

## Decisive transcript lines

The assistant message that shows the table (it comes after the orientation reads and the four `hci-researcher` calls, and before the brief was written):

```text
Repo present at `/tmp/ep-eval/material-v2-4`. Draft path: `proposal/draft.md` (you named none). No brief yet, so starting fresh.
## Extraction: design-tree items against `material.md`
| 7.2 carry-over symmetry | weak | "carry-over between the keyboards is symmetric, each is a few minutes of practice away from the other" — contradicted elsewhere by the screen "have never used a swipe keyboard on a watch" (## Variables), and no practice phase exists in the material |
| 7.3 overall design named | missing | Design never named; no factorial statement |
| 7.5 counterbalancing | missing | Order of the two keyboards never mentioned |
Writing the open brief with the nine settled entries.
```

The prompt the skill sent to the subagent for item 7.2, before the table was shown:

```text
Eligibility screen (item 8.3), settled: right-handed, aged 18-35, owns a smartphone, and HAS NEVER USED A SWIPE KEYBOARD ON A WATCH.
My concern, which is why I am asking you: the sample is screened to have never used a watch swipe keyboard, while tap keyboards on touchscreens are near-universal. So the swipe condition appears to carry first-exposure learning and novelty that the tap condition does not ...
```

The final message (the turn's `result` string), which opens without the table or the draft path:

```text
Checker exits clean on the open brief. Nine items settled from the material, twelve left.
## Round 1
Frontier: **1.3, 2.4, 6.2, 7.2, 7.3, 7.6, 7.7, 7.9**. (2.2, 2.5, 7.5 and 8.5 wait on 7.3, 2.4 and 7.2.)
**Q4 — item 7.2, whether carry-over really is symmetric.** May I keep keyboard within subjects but add per-keyboard familiarization immediately before each measured block ...
Why this matters: your eligibility screen (item 8.3) admits only people who have never used a watch swipe keyboard, while tap is near-universal, so swipe has far more learning headroom than tap. Unequal headroom makes the order effect in AB differ from BA, and counterbalancing cancels only symmetric carry-over. ...
Recommended (hci-researcher): "Within subjects plus per-keyboard practice to criterion plus counterbalancing plus an order-interaction check is the standard answer in this literature, not a compromise."
```

The key row for 7.2: "settled | carry-over argued symmetric".

## Per-row comparison with the key

| Item | Key     | Extraction | Asked in round 1?             | Match    |
| ---- | ------- | ---------- | ----------------------------- | -------- |
| 1.1  | settled | settled    | no                            | match    |
| 1.2  | settled | settled    | no                            | match    |
| 1.3  | weak    | weak       | Q1                            | match    |
| 2.2  | missing | missing    | no (blocked on 7.3)           | match    |
| 2.3  | settled | settled    | no                            | match    |
| 2.4  | missing | missing    | Q2                            | match    |
| 2.5  | missing | missing    | no (blocked on 2.4)           | match    |
| 6.1  | settled | settled    | no                            | match    |
| 6.2  | weak    | weak       | Q3                            | match    |
| 6.5  | settled | settled    | no                            | match    |
| 7.1  | settled | settled    | no                            | match    |
| 7.2  | settled | weak       | Q4                            | MISMATCH |
| 7.3  | missing | missing    | Q5                            | match    |
| 7.4  | settled | settled    | no                            | match    |
| 7.5  | missing | missing    | no (blocked on the 7.2 above) | match    |
| 7.6  | weak    | weak       | Q6                            | match    |
| 7.7  | weak    | weak       | Q7                            | match    |
| 7.8  | settled | settled    | no                            | match    |
| 7.9  | weak    | weak       | Q8                            | match    |
| 8.3  | settled | settled    | no                            | match    |
| 8.5  | missing | missing    | no (blocked on 7.3 and 7.6)   | match    |

Items in the printed table that the key does not list: none (21 rows printed, the 21 key rows).

Mentions of settled rows that are not questions about them (no numbered question is about the item, and no entry changes): item 1.2 and item 2.3 in the basis of Q2; item 6.5 in the basis of Q5; item 8.3 in the "Why this matters" of Q4; item 7.1's within-subjects label kept in Q4's recommendation. One is borderline: Q7's question text says "the eligibility screen kept as item 8.3 settled it", naming 8.3 only to keep it as it is; it is not a question about 8.3 and it proposes no change to 8.3, so it is not scored as asking. It does not change the verdict, which item 7.2 already decides.

## Round 1, as asked

The frontier line above Q1 lists item IDs 1.3, 2.4, 6.2, 7.2, 7.3, 7.6, 7.7, 7.9, and Q1 to Q8 ask exactly those eight, in checklist order. The skill listed the rows it deferred: "2.2, 2.5, 7.5 and 8.5 wait on 7.3, 2.4 and 7.2". That sentence names the first blocker of each; 8.5 also waits on 7.6, which is on the frontier.

- Q1, item 1.3, the retention period.
- Q2, item 2.4, the timeline.
- Q3, item 6.2, the sources behind H1, and H2 restated as a non-inferiority claim.
- Q4, item 7.2, carry-over. KEYED SETTLED.
- Q5, item 7.3, the design's name.
- Q6, item 7.6, the dependent variables' reliability and validity, with a renamed error measure and a replacement rating instrument.
- Q7, item 7.7, the control variables; `Recommended (hci-researcher)`.
- Q8, item 7.9, the confounds; `Recommended (hci-researcher)`.

## Other behaviour

- The open brief: written to `proposal/design-brief.md` with `Draft: proposal/draft.md`, `Status: open`, `Checklist: experiment-proposal 0.2.0`, 9 entries (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.4, 7.8, 8.3; 7.2 is not an entry), every entry `Status: settled`, three Looked up lines and one Open item (the `lit-search` command). The checker (`check_proposal.py brief proposal/design-brief.md`) was run in the session: the first attempt, with `; echo "exit=$?"` appended, was refused by the harness ("The following part requires approval: echo"), the re-run without the echo printed nothing. The driver re-ran the checker after the session: exit 0. Nothing was committed (`git status --porcelain` shows only `?? proposal/`, one commit `fixtures`), which is right for an open brief. The checker ran once, on the open brief; no round was answered, so there was no later rewrite to check.
- The table and the draft path are in an intermediate assistant message, not in the final `result` string. The final message starts at "Checker exits clean" and carries the frontier and Q1 to Q8 but neither the table nor the draft-path line. In the stream both are shown to the user; a caller that reads only the final result of `claude -p` without `--output-format stream-json` would see round 1 and not the table.
- Reads: the checklist, the material (read three times in all, once by the skill and twice more around the subagent calls), `references/brief.md` and `.claude-plugin/plugin.json` (plugin files), plus one `ls -la` of the project root, two `Glob **/*.md` calls and one `Grep` on the project (listing and search; the scratch project holds only `material.md`). A Bash `cat` of `plugin.json` was refused (allowed working directories) and recovered by a Read. Neither the key nor any `docs/research` file was opened (a grep of the stream for `key.md`, `material-with-gaps` and `docs/research` finds nothing).
- `hci-researcher`: four foreground calls to `experiment-proposal:hci-researcher`, for items 7.2, 7.7, 7.9 and 7.6, one question per call. Step 4 names 7.5 for delegation; 7.5 was blocked behind the downgraded 7.2, so it got no call and no question. The 7.2 call went out first and alone, and its prompt states the researcher's concern about the screen as "My concern". Each answer was quoted as `Recommended (hci-researcher)`, except Q6, whose recommendation is introduced as "Recommended (hci-researcher): the above".
- Three subagent answers open with a line that "the advisor was rate-limited, so this is from knowledge" (twice) or "Advisor is rate-limited (told not to retry this turn)". That is the subagent reporting a nested tool of its own, not the headless turn's API: the turn's result shows `api_error_status: null` and every `rate_limit_event` says `allowed`. It is recorded here and is not a harness-fail.
- Permission denials the skill recovered from (harness side, not counted against the plugin): the Bash `cat` of `plugin.json` and the `echo` appended to the checker call, both above.

## Pass-bar criteria

- Every row keyed weak or missing appears in the extraction as weak or missing: pass. All 11 keyed rows (1.3, 2.2, 2.4, 2.5, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9, 8.5) printed weak or missing.

- No row keyed settled is asked again in round 1: FAIL. Item 7.2 is keyed settled; the extraction printed it `weak` ("contradicted elsewhere by the screen ...") and Q4 is a numbered question about it. The other nine settled rows (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.4, 7.8, 8.3) were printed settled and no numbered question is about them.

- The frontier's item IDs are listed above Q1, and every frontier item is asked: pass. The line "Frontier: 1.3, 2.4, 6.2, 7.2, 7.3, 7.6, 7.7, 7.9" sits above Q1 and Q1 to Q8 are those eight items. The frontier is computed correctly from the run's own statuses (2.2, 2.5, 7.5 and 8.5 each have a weak or missing design-tree dependency). Under the key's statuses 7.2 would not be on it and 7.5 would be.

- The draft path is stated: pass. "Draft path: `proposal/draft.md` (you named none)" in the message that shows the table and `Draft: proposal/draft.md` in the brief. It is not repeated in the final message (see Other behaviour).

- The open brief was written and the checker run on it: pass. Nine entries, `Status: open`; the checker exits 0 (in the session after one refused attempt, and re-run by the driver).

## Verdict

FAIL on the second bar clause: item 7.2, keyed settled, was printed `weak` and asked as Q4. The first clause holds; 20 of 21 key rows match. The four extra criteria all pass. This is the same clause and the same item as run v2-2.

## Notes

- The fix under test did not close the route. ed96208 reworded step 2's third `weak` clause from "a conflict with another item" to "a decision the material contradicts elsewhere" and added step 3's "A settled item stays settled". The run's 7.2 row uses the reworded clause: it reads the material's own screening sentence ("have never used a swipe keyboard on a watch", in the same `## Variables` section) as contradicting the material's claim that carry-over is symmetric, and adds "no practice phase exists in the material". The "reason that does not fit this experiment" clause would also reach it. The key accepts the material's argument ("each is a few minutes of practice away from the other") as a settled reason.
- Step 3's "a settled item stays settled" never engages here: the downgrade happens at extraction, so by round 1 the item is a weak item on the frontier and the rule has nothing to protect. The sentence guards a settled item in rounds; the miss is in step 2's definition of `weak`, as in v2-2. Whether the skill is too permissive here or the key too lenient is the author's call; the record scores against the key as written.
- Consequences inside the run, identical to v2-2: the brief has 9 entries instead of 10; 7.5 was deferred because it depends on the downgraded 7.2 and was not asked; the subagent was consulted on 7.2 and not on 7.5.
- Q3 (item 6.2) recommends restating H2 as a non-inferiority claim, while the brief's 6.1 entry records H2 as a directional hypothesis. The question's item is 6.2, so it is not scored as asking 6.1; the same shape as the v2-2 note.
- Q6 recommends replacing the bespoke 7-point ease item with two standard instruments; this is under 7.6, which is weak in the key ("the rating has no operational definition").
- Run-specific difference from v2-2: item 7.3 was printed `missing` here (key: missing), where v2-2 printed `weak`.
- Only the first turn ran; no round was answered.
- Scenario 2's bar needs all three runs in a set to meet it; with this run failing, the scenario does not hold at 76e9c28 on this run.
