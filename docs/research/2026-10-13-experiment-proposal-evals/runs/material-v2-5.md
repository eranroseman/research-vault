# Scenario 2 (material with gaps) at 0.2.0, run v2-5

Date: 2026-10-15
Plugin commit: 76e9c28 (`experiment-proposal` 0.2.0; the harness file names 5e13529, which this re-run replaces). The fix that matters for this scenario is ed96208 (design keeps settled items settled, lists the frontier, runs the checker each round, defaults the draft path); 76e9c28 is the review and fixture fix on top of it. Before the run, `git status --porcelain plugins/` in `<checkout>` was empty and HEAD was 76e9c28.
Fixture: `fixtures/material-with-gaps.md`, copied in as `material.md`; key `fixtures/material-with-gaps.key.md` (21 rows).
Model: `--model opus`, which the init event of the stream reports as `claude-opus-5`.
This run re-tests the failure of `runs/material-v2-2.md`: item 7.2, keyed settled, was printed weak against item 8.3 and asked as Q4.

## Commands (one turn, no answers given)

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/material-v2-5
mkdir -p "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/material-with-gaps.md "$S/material.md"
cd "$S" && git add -A && git commit -qm fixtures
printf '%s' "/experiment-proposal:design material.md" > "$S.turn1.prompt"
bash /tmp/ep-eval/review-v2-drive.sh "$S" 1
```

The helper runs, with the prompt read from `$S.turn1.prompt`:

```bash
cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "<prompt>" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null
```

The raw stream-json output is kept outside the repository as `$S.turn1.jsonl`. The process exited 0 after 265 s (`$S.turn1.meta`: `rc=0 secs=265`). The stream holds two result events, both `success` with no `api_error_status`: the first (15 turns, 150 s) ends "Waiting on the control-variables consult; I'll post round 1 when it lands." and the second (a resumed segment after the last background consult returned, 82 s) carries round 1. No `--continue` turn was needed and no round was answered. No 429 and no "session limit" appears anywhere in the stream (every `rate_limit_event` reads `allowed`).

Environment: the user-level plugins ran their SessionStart hooks in the scratch session (the init event lists them), including a global caveman hook ("CAVEMAN MODE ACTIVE"). It had no visible effect on the table or the questions.

## Decisive transcript lines

```text
Repo present at `/tmp/ep-eval/material-v2-5`; no `proposal/` yet. Checklist, brief shape (v0.2.0), and material in hand. Draft path: `proposal/draft.md` (not named by user).
...
Brief written, open; checker exits 0. Extraction table, 21 design-tree items in checklist order:
... 7.2 carry-over symmetry | weak | "carry-over ... is symmetric, each is a few minutes of practice away" contradicts screening for participants who "have never used a swipe keyboard on a watch" (## Variables)
... 7.3 design named | missing | Design never named as a factorial
... 7.5 counterbalancing | missing | No order scheme
Nine settled, written as entries. Round 1 frontier: **1.3, 2.4, 6.2, 7.2, 7.3, 7.6, 7.7, 7.9** (2.2, 2.5, 7.5, 8.5 blocked on 7.3, 2.4, 7.2 and 7.3/7.6).
...
Waiting on the control-variables consult; I'll post round 1 when it lands.      (first result event)
Control-variables consult landed. Round 1 frontier: **1.3, 2.4, 6.2, 7.2, 7.3, 7.6, 7.7, 7.9**.     (second result event, directly above Q1)
**Q4 — item 7.2, carry-over between the keyboards.** The material calls carry-over symmetric, "each is a few minutes of practice away from the other", but item 8.3 screens for people who have never used a swipe keyboard on a watch while every smartphone owner arrives practised at tap. Keep keyboard within subjects with a stated practice regime that equalizes the *opportunity* to practice?
Why this matters: this is asymmetric transfer, not plain carry-over. ... a reviewer will read the symmetry sentence as contradicted by your own screening.
Recommended (hci-researcher): "The symmetry claim as written is not defensible — prior exposure is grossly asymmetric ..."
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
| 7.3  | missing | missing    | Q5                       | match    |
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

Round 1 asked item IDs 1.3, 2.4, 6.2, 7.2, 7.3, 7.6, 7.7, 7.9 (Q1 to Q8, in checklist order). The skill named the rows it held back: "2.2, 2.5, 7.5, 8.5 blocked on 7.3, 2.4, 7.2 and 7.3/7.6".

- Q1, item 1.3, how long the raw data are kept.
- Q2, item 2.4, the timeline (asks for the deadline).
- Q3, item 6.2, H2's form and H1's citations.
- Q4, item 7.2, carry-over. KEYED SETTLED.
- Q5, item 7.3, naming the design.
- Q6, item 7.6, reliability and construct validity; recommends the System Usability Scale in place of the single 7-point item.
- Q7, item 7.7, the control variables; `Recommended (hci-researcher)`.
- Q8, item 7.9, the confounds; `Recommended (hci-researcher)`.

## Other behaviour

- Frontier IDs above Q1: yes, one line, "Round 1 frontier: 1.3, 2.4, 6.2, 7.2, 7.3, 7.6, 7.7, 7.9", directly above Q1 (it also appears after the table in the first segment). Every frontier item is asked: 8 IDs, 8 questions, one per ID, in checklist order. The frontier includes 7.2 only because 7.2 was printed weak.
- Draft path: stated, "Draft path: `proposal/draft.md` (not named by user)" before the table, and as the brief's first line `Draft: proposal/draft.md`. It was not asked as a question.
- The open brief: written to `proposal/design-brief.md` with `Status: open`, `Checklist: experiment-proposal 0.2.0`, 9 entries (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.4, 7.8, 8.3; 7.2 is not an entry), every entry `Status: settled`, and the two commands under Open items. The checker (`check_proposal.py brief proposal/design-brief.md`) was run on it by the skill: the first call, with `; echo "exit=$?"` appended, was refused by the harness ("The following part requires approval: echo"); the re-run without the echo completed with no output. The driver re-ran the checker after the session: exit 0. Nothing was committed (`git status --porcelain` in the scratch project shows only `proposal/`), which is right for an open brief. Only the one round-1 state exists, so there was no per-round rewrite to check.
- Reads: the checklist, the material, `references/brief.md` and `.claude-plugin/plugin.json` (all plugin files except the material), plus one Bash `git rev-parse --show-toplevel && ls -la && ls -la proposal`. Neither the key nor any `docs/research` file was opened (a grep of the stream for `key.md`, `material-with-gaps`, `docs/research` and `fixtures` finds nothing).
- `hci-researcher`: three calls to `experiment-proposal:hci-researcher`, for items 7.2, 7.7 and 7.9, one question per call, all with `run_in_background: true` and issued together; the answers were quoted as `Recommended (hci-researcher)` in Q4, Q7 and Q8. Step 4 names 7.5 for delegation; 7.5 was blocked behind the weak 7.2, so it got no call and no question.
- Permission refusals the skill recovered from (harness side, not counted against the plugin): a Bash `cat` of the plugin's `plugin.json` ("may only concatenate files from the allowed working directories"), recovered by a Read; and the checker call with the trailing echo, re-run without it.

## Pass-bar criteria

- Every row keyed weak or missing appears in the extraction as weak or missing: pass. All 11 keyed rows (1.3, 2.2, 2.4, 2.5, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9, 8.5) printed weak or missing (7.3 printed `missing` here; `weak` in run v2-2).

- No row keyed settled is asked in round 1: FAIL. Item 7.2 is keyed settled; the extraction printed it `weak` (the material's symmetric-carry-over sentence "contradicts" the screening of swipe-naive smartphone owners) and Q4 asks it. The other nine settled rows (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.4, 7.8, 8.3) were printed settled and not asked.

- Frontier IDs listed above Q1 and every frontier item asked: pass (8 of 8). The list is the corrected-skill behaviour; it carries the 7.2 error through.

- Draft path stated: pass (`proposal/draft.md`).

- Open brief written and the checker run on it: pass (9 entries; checker exit 0, by the skill and again by the driver).

## Verdict

FAIL on the second bar clause (item 7.2, keyed settled, was printed weak and asked as Q4), the same miss as `runs/material-v2-2.md`. The first clause holds; 20 of 21 key rows match. The design fix ed96208 did not stop the reopening of 7.2 in this run.

## Notes

- The run took the route step 2 now words as "a decision the material contradicts elsewhere": it read the material's own statement that carry-over is symmetric as contradicted by the material's screening (item 8.3), an inference across two sections, not a sentence that contradicts another sentence. The key accepts the material's argument for 7.2, and the run's own brief entry for 7.1 already records the same concern ("Would change if: carry-over between the keyboards proved asymmetric") without reopening 7.1. The step 3 sentence "A settled item stays settled: a concern about it goes in the basis of a recommendation that bears on it" never engaged, because the run classified 7.2 as weak in step 2 first, so the guard sits after the status call that failed. Whether the wording of `weak` needs another change, or the key and the subagent's view (a phone-practised tap keyboard against a novel swipe one is an asymmetric-transfer threat) should be reconciled, is the author's call; the record scores against the key as written.
- Consequences inside the run: the brief has 9 entries instead of 10; 7.5 was deferred to round 2 because it depends on 7.2; the hci-researcher was consulted on 7.2 instead of 7.5.
- Judgment call on "asked again", not decisive since 7.2 already fails: Q7 contains a paragraph naming items 8.3 and 7.8 ("Two of its suggestions touch already-settled items, so I am not putting them in this question ... Those entries stay as they are; say the word and I record either as an amendment once the brief is frozen"). No numbered question is about 8.3 or 7.8 and their entries are unchanged, so they are scored as not asked. The paragraph sits in the question's body rather than in a recommendation's basis, where step 3 puts a concern about a settled item.
- Q3 recommends demoting H2 to a research question (RQ2), which would change the settled content of 6.1 if accepted; the question's item is 6.2 and the 6.1 entry is unchanged this turn (as in v2-2 and v2-1).
- Process quirk: because the three consults ran in the background, the first result event ended before round 1 existed; a driver that read only the first result event would have seen no questions. The process stayed alive and the second segment delivered round 1 in the same invocation.
- Only the first turn ran; no round was answered.
- Scenario 2's bar needs all runs to meet it; with this run failing, the scenario does not hold at 76e9c28 on this run.
