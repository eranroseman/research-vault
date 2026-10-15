# Scenario 2 (material with gaps) at 0.2.0, run v2-8, on the fixed design skill and the clarified material fixture

Date: 2026-10-15
Plugin commit: 76e9c28 (`experiment-proposal` 0.2.0). The fix that matters for this scenario is ed96208 (design keeps settled items settled, lists the frontier, runs the checker each round, defaults the draft path); 76e9c28 is the review and fixture fix on top of it. The harness file names 5e13529, which is the commit of runs v2-1 to v2-3; `git diff --quiet 76e9c28 HEAD -- plugins` held (no difference) after the run.
Fixture commit: d692e49 (the material's 7.2 carry-over sentence now gives a reason the Participants screen cannot contradict). Fixture: `fixtures/material-with-gaps.md`, copied in as `material.md` (`cmp` against the worktree file: identical); key `fixtures/material-with-gaps.key.md` (21 rows). Both files were unchanged between d692e49 and the end of the run (the one later fixture-directory commit, ea99fd2 at 03:06, touches `fixtures/proposal-with-defects.key.md` only).
Model: `--model opus`, which the init event of the stream reports as `claude-opus-5`.
What this wave tests: run v2-4 printed 7.2 `weak` by reading the Participants screen ("have never used a swipe keyboard on a watch") as a contradiction of the carry-over claim, and asked it as Q4. The material now says why carry-over is symmetric ("because both use the same letter layout, so what one keyboard teaches (where the letters are) helps the other equally"), a reason the screen does not contradict.

## Commands (one turn, no answers given)

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/material-v2-8
# the directory did not exist before this run
mkdir -p "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/material-with-gaps.md "$S/material.md"
cd "$S" && git add -A && git commit -qm fixtures
printf '%s' "/experiment-proposal:design material.md" > "$S.turn1.prompt"
bash /tmp/ep-eval/review-v2-drive.sh "$S" 1
```

The helper reads the prompt from `$S.turn1.prompt` and, for turn 1, runs exactly the harness command: `cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null`, with `P` the plugin path above. Its meta file reads `rc=0 secs=667`.

The raw stream-json output is kept outside the repository as `$S.turn1.jsonl`. The stream holds one `result` event: `subtype: success`, `is_error: false`, `api_error_status: null`, 15 turns, 664 s, three assistant text blocks (an opening line, the table message, and the final message, which is the `result` string). All four `rate_limit_event` lines read `status: allowed` (five-hour utilization 0.26 to 0.31); the four `429` hits in a grep of the stream are a UUID fragment, a source line number in a file the skill read, and a token count, and "session limit" and "rate-limited" do not occur. No harness-fail applies. The skill did not stop to ask for anything before the extraction, so no `--continue` turn was needed: the extraction table and round 1 both came in turn 1, and no round was answered.

Environment: the user-level plugins ran their SessionStart hooks in the scratch session (the init event lists them), including a global caveman hook. It had no visible effect on the table or the questions.

## Decisive transcript lines

The assistant message that shows the table (the second text block; it comes after the orientation reads, the three foreground `hci-researcher` calls and five listing and search calls (`Glob`, `Grep`, `ls`), and before the brief was written):

```text
Draft path: `proposal/draft.md` (you named none). Repo present, so the brief can freeze by commit.
## Extraction: the 21 design-tree items against `material.md`
| 7.2 carry-over | settled | "carry-over between the keyboards is symmetric, because both use the same letter layout … and each keyboard gets a short practice block" (## Variables) |
| 7.3 design named | **missing** | The design is never named (no "2 × … within-subjects") |
| 7.4 random assignment | settled | "There is no between-subjects variable, since every participant uses both keyboards." (## Variables) |
| 7.5 counterbalancing | **missing** | Order of the two keyboards is never mentioned |
| 8.3 eligibility | settled | "screened by a short form for handedness, age, phone ownership and no prior watch swipe use, because handedness and prior swipe use change typing speed…" (## Participants) |
Ten settled, six weak, five missing.
```

The tally line's counts are swapped: the table holds ten settled, five weak (1.3, 6.2, 7.6, 7.7, 7.9) and six missing (2.2, 2.4, 2.5, 7.3, 7.5, 8.5), which is the key's split. The rows themselves are right.

The final message (the turn's `result` string), which opens without the table or the draft path, as in v2-4:

```text
Brief written: `proposal/design-brief.md`, 10 settled entries, checker exits 0.
## Round 1
Frontier (every weak or missing item whose design-tree dependencies are all settled): **1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9**. Items 2.2, 2.5 and 8.5 wait on 7.3, 7.6 and 2.4.
**Q1. Item 1.3 (the data plan).** ... **Q2. Item 2.4 (the timeline).** ... **Q3. Item 6.2 (what each hypothesis has to contain).** ... **Q4. Item 7.3 (naming the design).** ... **Q5. Item 7.5 (the order the two keyboards are used in).** ... **Q6. Item 7.6 (the dependent variables).** ... **Q7. Item 7.7 (the control variables).** ... **Q8. Item 7.9 (confounds).** ...
Answer Q1 to Q8 in any form ... Round 2 then asks items 2.2, 2.5 and 8.5.
```

The failure this wave tests did not recur. 7.2 is printed `settled` with the material's own reason, the brief carries it as an entry, and no question is about it. The brief's 7.2 entry:

```text
- Decision: Carry-over between the two keyboards is treated as symmetric, and each keyboard gets a short practice block before its measured phrases; keyboard therefore stays within subjects.
- Rationale: "both use the same letter layout, so what one keyboard teaches (where the letters are) helps the other equally"
- Status: settled
```

## Per-row comparison with the key

| Item | Key     | Extraction | Asked in round 1?           | Match |
| ---- | ------- | ---------- | --------------------------- | ----- |
| 1.1  | settled | settled    | no                          | match |
| 1.2  | settled | settled    | no                          | match |
| 1.3  | weak    | weak       | Q1                          | match |
| 2.2  | missing | missing    | no (blocked on 7.3)         | match |
| 2.3  | settled | settled    | no                          | match |
| 2.4  | missing | missing    | Q2                          | match |
| 2.5  | missing | missing    | no (blocked on 2.4)         | match |
| 6.1  | settled | settled    | no                          | match |
| 6.2  | weak    | weak       | Q3                          | match |
| 6.5  | settled | settled    | no                          | match |
| 7.1  | settled | settled    | no                          | match |
| 7.2  | settled | settled    | no                          | match |
| 7.3  | missing | missing    | Q4                          | match |
| 7.4  | settled | settled    | no                          | match |
| 7.5  | missing | missing    | Q5                          | match |
| 7.6  | weak    | weak       | Q6                          | match |
| 7.7  | weak    | weak       | Q7                          | match |
| 7.8  | settled | settled    | no                          | match |
| 7.9  | weak    | weak       | Q8                          | match |
| 8.3  | settled | settled    | no                          | match |
| 8.5  | missing | missing    | no (blocked on 7.3 and 7.6) | match |

21 of 21 rows match. Items in the printed table that the key does not list: none (21 rows printed, the 21 key rows). One order slip: the table prints 7.6 before 7.5, where the checklist has 7.5 first (the questions are in checklist order).

## Round 1, as asked

The frontier line above Q1 lists the item IDs 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9, and Q1 to Q8 ask exactly those eight, in checklist order. The frontier is right from the checklist's own dependencies: 7.5 depends on 7.2 (settled), 7.3 on 7.1 and 6.5 (settled), 2.4 on 2.3 (settled); 2.2 depends on 7.3, 2.5 on 2.4, and 8.5 on 7.3 and 7.6, each missing or weak, so those three wait. The deferred sentence names the blockers (7.3, 7.6 and 2.4) together, not row by row.

- Q1, item 1.3, the retention period (a three-kinds recommendation).
- Q2, item 2.4, the timeline, anchored on the committee's two-week turnaround.
- Q3, item 6.2, H2 restated as a non-inferiority claim with a margin.
- Q4, item 7.3, naming the design "a 2 (keyboard: tap, swipe) within-subjects design, with order counterbalanced".
- Q5, item 7.5, counterbalancing over AB and BA; `Recommended (hci-researcher)`.
- Q6, item 7.6, a corrected words-per-minute formula and reliability and construct-validity sentences; the skill's own recommendation, no subagent label.
- Q7, item 7.7, the control variables; `Recommended (hci-researcher)`.
- Q8, item 7.9, the confounds; `Recommended (hci-researcher)`.

## Other behaviour

- The open brief: written to `proposal/design-brief.md` with `Draft: proposal/draft.md`, `Status: open`, `Checklist: experiment-proposal 0.2.0`, 10 entries (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3), every entry `Status: settled`, six Looked up lines and three Open items (two `lit-search` commands and the `the-ethics-board` command, last). The checker (`check_proposal.py brief proposal/design-brief.md`) was run in the session: the first attempt, with `; echo "exit=$?"` appended, was refused by the harness ("The following part requires approval: echo"), the re-run without the echo printed nothing. The driver re-ran the checker after the session: `exit=0`. Nothing was committed (`git status --porcelain` shows only `?? proposal/`, one commit `fixtures`), which is right for an open brief. The checker ran once, on the open brief; no round was answered, so there was no later rewrite to check.
- The table and the draft path are in an intermediate assistant message, not in the final `result` string. The final message starts at "Brief written" and carries the frontier and Q1 to Q8 but neither the table nor the draft-path line. In the stream both are shown to the user; a caller that reads only the final result of `claude -p` without `--output-format stream-json` would see round 1 and not the table. Same shape as v2-4.
- Reads: the checklist, the material (four times in all, once by the skill and three more times around the subagent calls), `references/brief.md`, `.claude-plugin/plugin.json` and `scripts/check_proposal.py` (plugin files), plus three `Glob **/*` calls, one `Grep` and one `ls -la` on the project (listing and search; the scratch project holds only `material.md`). A Bash `cat` of `plugin.json` joined with a `head` of the checker was refused (harness permission) and recovered by two Reads. Neither the key nor any `docs/research` file was opened (a grep of the stream for `key.md`, `material-with-gaps` and `docs/research` finds nothing).
- `hci-researcher`: three foreground calls to `experiment-proposal:hci-researcher`, for items 7.5, 7.7 and 7.9, one question per call. The prompts list the settled decisions as "do not relitigate them, answer within them". The 7.5 prompt nonetheless asks the subagent whether the swipe-naive, tap-experienced sample "undercut[s] the item 7.2 symmetric-carry-over claim", and the 7.9 prompt asks whether the expertise asymmetry is "a confound, a limitation to state, or something the design should change". Those are questions to the subagent about a settled item; no question to the user came of them (see the next section). No call went out for 7.6 or 7.3. The subagent answers were quoted as `Recommended (hci-researcher)`.
- Permission denials the skill recovered from (harness side, not counted against the plugin): the Bash `cat` and `head` of plugin files, and the `echo` appended to the checker call, both above.
- Time: 667 s for one turn; the model finished 7.5, 7.7 and 7.9 as three sequential foreground subagent calls.

## Settled items in question bodies

No numbered question names a settled row as its subject, and no settled row's entry changed (the brief was written once, before Q1 to Q8). Mentions of settled rows inside question bodies, none of which is scored as asking:

- Basis of a recommendation, naming the item: item 1.2 in Q1 and Q2, item 2.3 in Q2, items 7.1 and 6.5 in Q4.
- Q5 carries a paragraph after its recommendation: "One thing this recommendation carries that bears on entries already settled, and which I am not reopening". It relays the subagent's view that the swipe-naive sample transfers more from tap to swipe than the reverse, so order should be pre-registered as a factor (a concern about the premise of 7.2, without naming 7.2), and it names "the settled item 7.4 sentence that there is no between-subjects variable" as sitting awkwardly beside a counterbalanced order, proposing one clarifying sentence in the Design section. No entry changes.
- Q7 says "item 8.3 is settled, so I am not reopening it" and relays the subagent's advice to keep the right-handedness criterion and state it under limitations; the swipe-naivety criterion's external-validity cost is discussed in the weighing for item 7.7.
- Q8 relays the expertise asymmetry as "a confound, and a self-inflicted one ... eligibility creates it" and recommends practising "to a criterion on both keyboards rather than a fixed short block". That bears on the "short practice block" of 7.2's settled entry, but it appears under item 7.9 (and practice block length is a control under item 7.7) and does not edit the entry.
- Q3's alternative "demoting [H2] to RQ2 alongside the ease rating" would change how 6.1 classifies H2 if taken; the question's item is 6.2 and the brief's 6.1 entry is unchanged. The same shape as the v2-4 note on Q3.

Under step 3's rule ("a concern about it goes in the basis of a recommendation that bears on it, never into a question or a change to its entry"), the 7.4, 8.3 and 7.2-premise concerns sit in recommendations that bear on them, and each says so or leaves the entry alone. The pass bar's wording is "asked again": a numbered question names the item as its subject, or the entry changes. Neither happens.

## Pass-bar criteria

- Every row keyed weak or missing appears in the extraction as weak or missing: pass. All 11 keyed rows (1.3, 2.2, 2.4, 2.5, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9, 8.5) printed weak or missing.

- No row keyed settled is asked again in round 1: pass. The ten settled rows (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3) were printed settled, each has an entry in the open brief, and no numbered question is about any of them. 7.2, the row that failed in v2-2 and v2-4, printed settled and was not asked.

- The frontier's item IDs are listed above Q1, and every frontier item is asked: pass. "Frontier ...: 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9" sits above Q1 and Q1 to Q8 are those eight items. The frontier is the one the key's statuses give: 2.2, 2.5 and 8.5 wait on 7.3, 2.4 and 7.3 with 7.6, each a missing or weak design-tree dependency.

- The draft path is stated: pass. "Draft path: `proposal/draft.md` (you named none)" in the message that shows the table and `Draft: proposal/draft.md` in the brief. It is not repeated in the final message (see Other behaviour).

- The open brief was written and the checker run on it: pass. Ten entries, `Status: open`; the checker exits 0 (in the session after one refused attempt, and re-run by the driver).

- Any mention of a settled item inside a question body: recorded above (items 1.2, 2.3, 7.1, 6.5, 7.4, 8.3, and the premise of 7.2); none is a question about the item.

## Verdict

PASS. 21 of 21 key rows match, including 7.2 printed settled, which v2-4 printed weak. The four extra criteria all pass. This run alone meets the scenario's bar; the bar needs all three runs in a set to meet it, and this is one run.

## Notes

- The fixture change is what moved 7.2. The skill's step 2 text is the same as in v2-4, and in this run the 7.2 row quotes "both use the same letter layout" and the Participants screen is not read as a contradiction: with the symmetry argued from the layout, a swipe-naive screen contradicts nothing the material says. The skill still carried the concern about the screen forward, but as the Q5 and Q8 recommendation text and a subagent prompt, which step 3's rule allows, rather than as a changed row.
- The concern leaked into three places all the same: the 7.5 subagent prompt asks whether the asymmetry "undercut[s]" 7.2, Q5's recommendation relays the transfer-asymmetry view, and Q8 recommends replacing the "short practice block" with practice to criterion. If a later round accepts Q8, the 7.2 entry's practice-block clause becomes stale and would need an amendment. Whether that is acceptable is the author's call; the record scores against the key as written.
- Tally slip in the table message ("six weak, five missing" for five weak and six missing) and 7.6 printed before 7.5. Neither affects the scoring.
- Q3 recommends a 2-percentage-point margin for H2 with the caveat that it is "a starting point you should replace with a value from a comparable study"; Q1 recommends five years of retention for trial logs and says it is "a common funder and journal convention, not a fact I read in your material". Both are labelled as the skill's recommendation, not as looked-up facts.
- Q6 corrects the material's words-per-minute formula (presented-phrase length, no minus-one term) under item 7.6, which the key marks weak; the correction is also recorded in the brief's Looked up with a recalled-from-memory source note.
- Only the first turn ran; no round was answered.
