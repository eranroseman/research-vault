# Scenario 2 (material with gaps) at 0.2.0, run v2-7, on the clarified material fixture

Date: 2026-10-15
Plugin commit: 76e9c28 (`experiment-proposal` 0.2.0). The design fix this scenario tests is ed96208 (design keeps settled items settled, lists the frontier, runs the checker each round, defaults the draft path); 76e9c28 is the review and fixture fix on top of it. The harness file names 5e13529, which is the commit of runs v2-1 to v2-3. `git diff --stat 76e9c28 HEAD -- plugins` is empty: the plugin tree was unchanged for this run.
Fixture commit: d692e49 (the material's 7.2 carry-over sentence now gives a reason the Participants screen cannot contradict: "so what one keyboard teaches (where the letters are) helps the other equally, and each keyboard gets a short practice block before its measured phrases"). `git status --porcelain` showed no change to plugin or fixture files before the run.
Fixture: `fixtures/material-with-gaps.md`, copied in as `material.md` (`cmp` against the committed fixture: identical); key `fixtures/material-with-gaps.key.md` (21 rows).
Model: `--model opus`, which the init event of the stream reports as `claude-opus-5`.

## Commands (one turn, no answers given)

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/material-v2-7
# the directory did not exist before this run
mkdir -p "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/material-with-gaps.md "$S/material.md"
cd "$S" && git add -A && git commit -qm fixtures
printf '%s' "/experiment-proposal:design material.md" > "$S.turn1.prompt"
bash /tmp/ep-eval/review-v2-drive.sh "$S" 1
# after the session, by the driver (the skill did not run it, see Other behaviour)
cd "$S" && python3 "$P/scripts/check_proposal.py" brief proposal/design-brief.md; echo "exit=$?"
```

The helper reads the prompt from `$S.turn1.prompt` and, for turn 1, runs exactly the harness command: `cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null`, with `P` the plugin path above. Its meta file reads `rc=0 secs=355`.

The raw stream-json output is kept outside the repository as `$S.turn1.jsonl`. The stream holds one `result` event: `subtype: success`, `is_error: false`, `api_error_status: null`, 12 turns, 352 s, 3 subagent calls. Both `rate_limit_event` lines read `status: allowed` (five-hour utilization 0.26 and 0.27). "session limit" does not occur anywhere in the stream; the two lines that contain "429" contain it only inside a uuid. No harness-fail applies (see Other behaviour for the one "advisor tool was rate-limited" string). The skill did not stop to ask for anything before the extraction, so no `--continue` turn was needed: the extraction table and round 1 both came in turn 1, and no round was answered.

Environment: the user-level plugins ran their SessionStart hooks in the scratch session (the init event lists them), including a global caveman hook. It had no visible effect on the table or the questions.

## Decisive transcript lines

The assistant message that shows the table (it comes after the orientation reads and the three `hci-researcher` calls, and before the brief was written). Its first line states the draft path:

```text
**Design-tree extraction** — 21 items, checklist order. Draft path: `proposal/draft.md` (default; no path named).
| 7.2 carry-over | settled | "carry-over ... is symmetric, because both use the same letter layout, so what one keyboard teaches ... helps the other equally" |
| 7.3 design named | missing | Design never named; no "2 × 1 within-subjects" statement |
| 7.5 counterbalancing | missing | Order of tap/swipe never counterbalanced or randomized |
```

The final message (the turn's `result` string) opens with the brief and the frontier, and carries neither the table nor the draft path:

```text
Open brief written: `proposal/design-brief.md` (9 settled entries). Round 1 below.
**Frontier (round 1):** items 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9.
```

The line that matters most for this wave: the subagent's 7.7 answer still called the Participants screen a contradiction of the carry-over claim ("it also makes experience asymmetric across conditions ... contradicting the "carry-over is symmetric" claim"), yet the skill printed 7.2 `settled`, kept it a brief entry, and carried the concern only in the basis of Q5's recommendation (the subagent's words on 7.5):

```text
Your screening (phone owners who have never swiped on a watch) "makes tap familiar and swipe novel, which undercuts the symmetric carry-over claim", so "enter order as a between-subjects factor, test keyboard×order, report it regardless".
```

The brief's 7.2 entry, unchanged by that concern:

```text
### 7.2 Carry-over
- Decision: Carry-over between the two keyboards is expected to be symmetric, so keyboard stays within subjects; each keyboard gets a short practice block before its measured phrases.
- Rationale: "both use the same letter layout, so what one keyboard teaches (where the letters are) helps the other equally"
- Status: settled
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

Items in the printed table that the key does not list: none (21 rows printed, the 21 key rows). 21 of 21 rows match; v2-4 matched 20 of 21 on 7.2.

## Round 1, as asked

The frontier line above Q1 lists item IDs 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9, and Q1 to Q8 ask exactly those eight, in checklist order. The skill closes the message with "After this round, items 2.2, 2.5 and 8.5 open up." The frontier is correct from the run's own statuses: 2.2 and 8.5 depend on 7.3, 2.5 on 2.4, each a missing item. Under the key's statuses the frontier is the same eight, because 7.2 is settled in both.

- Q1, item 1.3, the data plan (retention, screening form, ease ratings).
- Q2, item 2.4, the timeline.
- Q3, item 6.2, H2 restated as directional, or turned into RQ2; H1's sources go to `lit-search`.
- Q4, item 7.3, the design's name.
- Q5, item 7.5, counterbalancing; `Recommended (hci-researcher)`.
- Q6, item 7.6, reliability and construct validity of the measures; `Recommended (hci-researcher, on the measurement hole)`, quoting the 7.9 call's instrumentation answer.
- Q7, item 7.7, the controls; `Recommended (hci-researcher)`.
- Q8, item 7.9, the confounds; `Recommended (hci-researcher)`.

### Mentions of settled items inside the question bodies

No numbered question names a settled item as its subject, and no settled entry changed. The mentions, by ID and by content:

- By ID, in a basis: Q2 names items 1.2 and 2.3; Q4 names items 6.5 and 7.1.
- By ID, in a recommendation: Q7 says "item 8.3 is settled" and declines to change the screening ("I recommend saying so in the Design section rather than changing your screening"). Same shape as v2-4's borderline Q7; not scored as asking, since it proposes no change to 8.3.
- By content, without the ID, in a recommendation (the route step 3 prescribes): Q5 quotes the subagent that the screening "undercuts the symmetric carry-over claim" (7.2), and that "order as a between-subjects factor" be entered (touching 7.4's "no between-subjects variable"); Q7 repeats the asymmetry concern for the no-swipe screen (8.3); Q8 quotes "the material asserts symmetric carry-over but never states counterbalancing — assertion is not a control" (7.2) and proposes "practise both keyboards to a stated plateau criterion" (bearing on 7.2's "short practice block").
- Q3's RQ2 alternative would move H2 out of 6.1's hypothesis set. The question's item is 6.2, so it is not scored as asking 6.1; the same note as v2-4.

## Other behaviour

- The open brief: written to `proposal/design-brief.md` with `Draft: proposal/draft.md`, `Status: open`, `Checklist: experiment-proposal 0.2.0`, and 10 entries (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3), every entry `Status: settled`. The 10 entries are exactly the 10 settled rows of the key; 7.2 is an entry here (it was not in v2-4). The skill's message says "9 settled entries", a miscount: the file holds ten `###` headings. The brief also has six Looked up lines and two Open items (`lit-search` and `the-ethics-board`).
- The checker was not run by the skill. The stream holds no `check_proposal.py` call: the Bash calls are `git rev-parse --show-toplevel && ls -la && ls -la proposal`, one refused `cat`, and `mkdir -p`. SKILL.md step 3 asks for the checker after every round's rewrite and step 6 at the end; step 2 (which wrote this brief) does not name it, and no round was answered, so the skill ran it zero times where v2-4's skill ran it once. The driver ran it after the session: it printed nothing and exited 0. Nothing was committed (`git status --porcelain` shows only `?? proposal/`, one commit `fixtures`), which is right for an open brief.
- The table and the draft path are in an intermediate assistant message, not in the final `result` string, as in v2-4: a caller that reads only the final result of `claude -p` without `--output-format stream-json` would see round 1 and the frontier but not the table. The draft path is also in the brief's header line.
- Reads: the checklist, the material, `references/brief.md` and `.claude-plugin/plugin.json` (plugin files). Three more `Read` calls of `material.md` follow the three `Agent` calls; each subagent answer ends "Source read: .../material.md", so they are the subagents' own reads. A Bash `cat` of `plugin.json` was refused (allowed working directories) and recovered by a Read; it is the run's only permission denial. Neither the key nor any `docs/research` file was opened (a grep of the stream for `key.md`, `material-with-gaps` and `docs/research` finds nothing).
- `hci-researcher`: three foreground calls to `experiment-proposal:hci-researcher`, for items 7.5, 7.7 and 7.9, one question per call, all before the table. In v2-4 the 7.5 call was skipped because 7.2 had been downgraded; here it ran. Q6 (item 7.6) had no call of its own and quotes the 7.9 answer's instrumentation lines under `(hci-researcher, on the measurement hole)`; the reliability and construct-validity sentences in Q6 are the skill's own and are not attributed to the subagent.
- The 7.9 subagent's answer ends "(The advisor tool was rate-limited on my one call; this answer is unreviewed by it.)". That is the subagent reporting a nested tool of its own, not the headless turn's API: the turn's result shows `api_error_status: null` and both `rate_limit_event` lines say `allowed`. It is recorded here and is not a harness-fail.

## Pass-bar criteria

- Every row keyed weak or missing appears in the extraction as weak or missing: pass. All 11 keyed rows (1.3, 2.2, 2.4, 2.5, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9, 8.5) printed weak or missing.

- No row keyed settled is asked again in round 1: pass. All ten keyed settled rows (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3) printed `settled`; no numbered question has one as its subject, and the brief has an unchanged entry for each. Item 7.2, the row v2-2 and v2-4 failed, printed settled with the passage quoted.

- The frontier's item IDs are listed above Q1, and every frontier item is asked: pass. "Frontier (round 1): items 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9" sits above Q1, and Q1 to Q8 are those eight items.

- The draft path is stated: pass. "Draft path: `proposal/draft.md` (default; no path named)" in the message that shows the table, and `Draft: proposal/draft.md` in the brief. It is not repeated in the final message.

- The open brief was written and the checker run on it: written, pass; checker run, not by the skill. Ten entries, `Status: open`; the driver's post-session run exits 0 with no output. The in-session checker run is absent (see Other behaviour). This is not one of the two scenario-2 bar clauses, which concern the extraction and settled items asked again.

- Any mention of a settled item inside a question body: recorded above; none is a numbered question about the item and none changes an entry.

## Verdict

PASS on the scenario 2 bar: every keyed weak or missing row appeared as weak or missing, and no keyed settled row was asked again. 21 of 21 rows match the key. The four extra criteria on the frontier, the draft path, the brief and the settled mentions hold, except that the checker was not run inside the session (driver run after: exit 0), which does not touch the bar.

## Notes

- The fixture change does what it was written to do. With a reason the Participants screen cannot contradict, the skill's extraction read 7.2 as settled, where v2-4 printed it `weak` ("contradicted elsewhere by the screen"). The 0.2.0 text of SKILL.md steps 2 and 3 is the same in both runs, so the change in the 7.2 row follows the fixture sentence.
- The subagent still reads the screen against the carry-over claim: its 7.7 answer says "contradicting the "carry-over is symmetric" claim", and its 7.5 answer says the screening "undercuts the symmetric carry-over claim". The skill did not turn either into a question or an entry change; Q5's recommendation carries the 7.5 sentence as a basis. Step 3's rule "a concern about it goes in the basis of a recommendation that bears on it" is the rule at work here.
- Q8's recommendation of a plateau-criterion practice block and Q5's order-by-keyboard test would revise 7.2's "short practice block" if accepted in round 2. That would be the user's amendment through a recommendation under 7.9 or 7.5, not the skill reopening 7.2; it is the place a later round could change a settled entry, so it is flagged for the next wave.
- The "9 settled entries" count in the skill's message is stale or miscounted against the file's ten; the file is right and matches the key.
- Q3 (item 6.2) recommends restating H2 as a directional claim ("higher with swipe") or as RQ2, while the brief's 6.1 entry records H2 as a hypothesis whose direction is predictable. The question's item is 6.2, so it is not scored as asking 6.1.
- Only the first turn ran; no round was answered.
- Scenario 2's bar needs all three runs in a set to meet it; this run meets it at 76e9c28 on the clarified fixture (d692e49).
