# Scenario 2 (material with gaps) at 0.2.0, run v2-9, on the fixed design skill and the clarified material fixture

Date: 2026-10-15
Plugin commit: 76e9c28 (`experiment-proposal` 0.2.0). The fix that matters for this scenario is ed96208 (design keeps settled items settled, lists the frontier, runs the checker each round, defaults the draft path); 76e9c28 is the review and fixture fix on top of it. The harness file names 5e13529, which is the commit of runs v2-1 to v2-3.
Fixture commit: d692e49 (the material's 7.2 carry-over sentence now gives a reason the Participants screen cannot contradict). Fixture: `fixtures/material-with-gaps.md`, copied in as `material.md`; key `fixtures/material-with-gaps.key.md` (21 rows).
Model: `--model opus`, which the init event of the stream reports as `claude-opus-5`.
What this wave tests: run v2-4 printed 7.2 `weak` by reading the Participants screen ("have never used a swipe keyboard on a watch") as a contradiction of the carry-over claim, and asked it as Q4. The fixture now carries a reason for the symmetry that the screen does not contradict.

## Commands (one turn, no answers given)

```bash
P=<checkout>/plugins/experiment-proposal
S=/tmp/ep-eval/material-v2-9
# the directory did not exist before this run
mkdir -p "$S" && cd "$S" && git init -q && git config user.email eval@example.invalid && git config user.name eval
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/material-with-gaps.md "$S/material.md"
cd "$S" && git add -A && git commit -qm fixtures
printf '%s' "/experiment-proposal:design material.md" > "$S.turn1.prompt"
bash /tmp/ep-eval/review-v2-drive.sh "$S" 1
```

The helper reads the prompt from `$S.turn1.prompt` and, for turn 1, runs exactly the harness command: `cd "$S" && timeout 1800 claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "$prompt" > "$S.turn1.jsonl" 2> "$S.turn1.err" < /dev/null`, with `P` the plugin path above. Its meta file reads `rc=0 secs=460`. The scratch repository's `HEAD` before the turn was one commit, `fixtures`.

The raw stream-json output is kept outside the repository as `$S.turn1.jsonl`. The stream holds three `result` events, all `subtype: success`, `is_error: false`, `api_error_status: null`: the first (20 turns, 306 s) is the extraction table; the second (1 turn) is one line, "7.7 consult landed. Waiting on the 7.9 (confounds) consult before posting round 1."; the third (1 turn, 85 s) is round 1. The three `hci-researcher` calls ran in the background, which is why the turn closes three times. All four `rate_limit_event` lines read `status: allowed` (five-hour utilization 0.26 to 0.29); "session limit" and 429 do not occur, so no harness-fail applies. The skill did not stop to ask for anything before the extraction, so no `--continue` turn was needed: the extraction table and round 1 both came in turn 1, and no round was answered.

Environment: the user-level plugins ran their SessionStart hooks in the scratch session (the init event lists them), including a global caveman hook. It had no visible effect on the table or the questions.

## Decisive transcript lines

The assistant message that shows the table (the first `result` event; it comes after the orientation reads, the three background `hci-researcher` launches, and the brief write):

```text
Extraction table. Material: `material.md`. Draft path: `proposal/draft.md` (default; not named in material). Repo present, brief written open at `proposal/design-brief.md`, checker exits 0.
| 7.2 Carry-over | settled | "symmetric, because both use the same letter layout … each keyboard gets a short practice block" (Variables) |
| 7.3 Overall design | missing | Design never named (no factorial notation) |
| 7.5 Counterbalancing | missing | No order scheme at all |
| 8.3 Eligibility | settled | "screened by a short form for handedness, age, phone ownership and no prior watch swipe use" + reasons (Participants) |
Round 1 frontier: **1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9**. (Blocked until these settle: 2.2 on 7.3; 2.5 on 2.4; 8.5 on 7.3 and 7.6.)
```

The final message (the third `result` event), which opens with the frontier and carries Q1 to Q8 but not the table:

```text
Three consults in. Round 1 frontier: **1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9**.
**Q1 — item 1.3, data plan (retention and the screener).**
**Q2 — item 2.4, timeline.**
**Q3 — item 6.2, H2's testability.**
**Q4 — item 7.3, naming the design.**
**Q5 — item 7.5, counterbalancing.**
**Q6 — item 7.6, dependent variables.**
**Q7 — item 7.7, control variables.**
**Q8 — item 7.9, confounds.**
```

The key row for 7.2: "settled | carry-over argued symmetric".

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

Items in the printed table that the key does not list: none (21 rows printed, the 21 key rows). 21 of 21 rows match.

Mentions of settled rows that are not questions about them (no numbered question names the item as its subject, and no entry changes):

- Item 1.2 in the basis of Q1's recommendation (the standing protocol's retention period "wins" if it names one) and in the basis of Q2's recommended schedule; item 2.3 in the basis of Q2's schedule (the pilot week).
- Item 6.5 in Q4's Why line and in Q4's recommendation basis, item 7.1 in the same basis, and item 7.4 in Q4's closing note ("item 7.4 stays as settled").
- Two mentions sit in a question body rather than in a recommendation's basis, and are recorded here because step 3 says a concern about a settled item goes in the basis of a recommendation that bears on it:
  - Q7, in a paragraph after its Recommended block: "Two things the consult flagged about criteria already settled under item 8.3, for your judgment rather than my question: within subjects the right-handed exclusion 'buys nothing the placement rule does not', and the prior-use screen is asymmetric ... Raise either and I treat it as a change you asked for; otherwise item 8.3 stands and 7.7 just records the external-validity cost." The question's subject is item 7.7, the paragraph disclaims being a question, and the 8.3 entry is unchanged in the brief, so it is not scored as asking. It does hand the user two reasons to reopen 8.3 inside a question, which is the nearest this run comes to the failure mode.
  - Q8, in the Why line: "item 7.2's symmetry argument covers letter locations only". It is a concern about settled 7.2 in a Why line, next to the maturation prevention Q8 recommends. It names no question about 7.2, proposes no change to 7.2, and 7.2's entry in the brief is unchanged, so it is not scored as asking.
- The skill's own `hci-researcher` prompts for 7.5 and 7.9 pose the swipe-naive versus tap-practiced asymmetry as a concern to address in a section of its own, separate from the list headed "Decisions already settled by the researcher (do not reopen)", which also lists the carry-over decision. The prompts, not the user, receive that concern.

## Round 1, as asked

The frontier line above Q1 lists item IDs 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9, and Q1 to Q8 ask exactly those eight, in checklist order. The frontier is computed correctly from the run's own statuses against the checklist's `depends on` lists: 2.2 depends on 7.3, 2.5 on 2.4, 8.5 on 7.3 and 7.6, each of which is weak or missing; 7.5 depends only on 7.2, which is settled, so it is on the frontier and was asked (in v2-4 it was blocked behind a downgraded 7.2). The skill listed the rows it deferred, with the dependency of each. Under the key's statuses the frontier is the same eight items.

- Q1, item 1.3, retention and the screener's data.
- Q2, item 2.4, the timeline.
- Q3, item 6.2, H2 restated with a non-inferiority margin; H1's missing sources are left to `lit-search`.
- Q4, item 7.3, the design's name (single-factor, two-level, within-subjects).
- Q5, item 7.5, four order codes (keyboard order crossed with two matched phrase halves); `Recommended (hci-researcher)`.
- Q6, item 7.6, the dependent variables' formula, reliability and validity statements, and a replacement rating instrument (SUS).
- Q7, item 7.7, the control variables, with the internal versus external validity cost of each; `Recommended (hci-researcher)`.
- Q8, item 7.9, the confound list with a prevention each; `Recommended (hci-researcher)`.

## Other behaviour

- The open brief: written to `proposal/design-brief.md` with `Draft: proposal/draft.md`, `Status: open`, `Checklist: experiment-proposal 0.2.0`, 10 entries (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3), every entry `Status: settled`, four Looked up lines and two Open items (both the `lit-search` command). The driver re-ran the checker after the session: `check_proposal.py brief proposal/design-brief.md` exits 0 with no output. In the session the checker ran three times: a call with `; echo "exit=$?"` appended was refused by the harness ("The following part requires approval: echo"); the re-run exited 1 with `proposal/design-brief.md:5: sections must be Decisions, Looked up, Open items, in that order`; after an Edit added the Looked up section it ran clean. Nothing was committed (`git status --porcelain` shows only `?? proposal/`, one commit `fixtures`), which is right for an open brief. No round was answered, so there was no later rewrite to check.
- The first write of the brief held 21 entries: the 10 settled ones plus 11 placeholders for the weak and missing items (`Decision: Open.`, `Rationale: pending`, `Status: provisional`, `Source: user, round 1`) and 11 "round 1 pending" Open-items lines. The user had said nothing, so those labels were false at the moment of writing. The skill stripped them with a script in the same turn, before the table was shown and before any checker pass, so the file the user saw and the checker passed holds only the 10 settled entries.
- The table and the draft path are in an intermediate assistant message (the first `result` event), not in the final `result` string. The final message starts at "Three consults in" and carries the frontier and Q1 to Q8 but neither the table nor the draft-path line. In the stream both are shown to the user; a caller that reads only the last `result` of the turn would see round 1 and not the table. A caller that reads the first `result` would see the table and not the questions. The same shape as v2-4, now across three result events.
- Reads: the checklist, the material (once by the skill; the three subagents read it again), `references/brief.md` and `.claude-plugin/plugin.json` (plugin files), plus one `ls -la` of the project root. A Bash `cat` of `plugin.json` was refused (allowed working directories) and recovered by a Read. Neither the key nor any `docs/research` file was opened (a grep of the stream for `key.md`, `material-with-gaps` and `docs/research` finds nothing).
- `hci-researcher`: three background calls to `experiment-proposal:hci-researcher`, for items 7.5, 7.7 and 7.9, one question per call; the skill named those items in its step 4. It did not consult the subagent for 7.6 and recommended there from its own Looked up lines, with the text-entry metric facts cited from knowledge and flagged for `lit-search`. Each consult answer was quoted as `Recommended (hci-researcher)` in Q5, Q7 and Q8, and partly in Q3 ("hci-researcher, item 7.9 consult").
- One subagent answer (the 7.5 consult) opens with the note that "the advisor tool was rate-limited on my one attempt, so this answer is unreviewed". That is the subagent reporting a nested tool of its own, not the headless turn's API: all three `result` events show `api_error_status: null` and every `rate_limit_event` says `allowed`. It is recorded here and is not a harness-fail.
- Permission denials the skill recovered from (harness side, not counted against the plugin): the Bash `cat` of `plugin.json`, two `WebSearch` calls for the text-entry metric definitions (the tool is not in `--allowedTools`; the skill cited the facts from knowledge, said so in the Looked up lines and the table message, and queued the check for `lit-search`), and the `echo` appended to the checker call.

## Pass-bar criteria

- Every row keyed weak or missing appears in the extraction as weak or missing: pass. All 11 keyed rows (1.3, 2.2, 2.4, 2.5, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9, 8.5) printed weak or missing.

- No row keyed settled is asked again in round 1: pass. All ten settled rows (1.1, 1.2, 2.3, 6.1, 6.5, 7.1, 7.2, 7.4, 7.8, 8.3) were printed settled, and no numbered question names one as its subject or changes its entry. Item 7.2, the failure of v2-2 and v2-4, printed `settled` with a quote and has an entry in the brief. The two question-body mentions (Q7 on 8.3, Q8 on 7.2) are listed above and are not scored as asking.

- The frontier's item IDs are listed above Q1, and every frontier item is asked: pass. The line "Round 1 frontier: 1.3, 2.4, 6.2, 7.3, 7.5, 7.6, 7.7, 7.9" sits above Q1 and Q1 to Q8 are those eight items, in checklist order.

- The draft path is stated: pass. "Draft path: `proposal/draft.md` (default; not named in material)" in the message that shows the table, and `Draft: proposal/draft.md` in the brief. It is not repeated in the final message (see Other behaviour).

- The open brief was written and the checker run on it: pass. Ten entries, `Status: open`; the checker exits 0 (in the session after one refused attempt and one exit 1, and re-run by the driver).

## Verdict

PASS. Both clauses of the bar hold: 21 of 21 rows match the key, and no settled row is asked. The four extra criteria all pass. Item 7.2 printed `weak` and was asked in v2-2, v2-4 and v2-5 (MISMATCH rows in their per-row tables) and printed `settled` in v2-1, v2-3, v2-6 and v2-7 (by their per-row tables), so this run's settled 7.2 is consistent with the clarified fixture having closed the route but does not by itself separate the fixture change from run-to-run variation.

## Notes

- The change under test is the fixture, not the skill: ed96208 and 76e9c28 are the same plugin commit as in v2-4, and the 7.2 row differs where the material's carry-over sentence now says the symmetry holds "because both use the same letter layout, so what one keyboard teaches (where the letters are) helps the other equally". The extraction quotes that clause and the practice block, and nothing in the Participants screen contradicts it. One run does not show the skill is robust to a material that does contradict itself; v2-4 shows it was not.
- The skill's concern about swipe-naive versus tap-practiced learning (the v2-4 route) still reached the user, through the basis and Why lines of Q7 and Q8 and through the subagent prompts, without changing 7.2's status or entry. That is what step 3's "a settled item stays settled" asks for, with the two question-body mentions above as the soft edge: Q7 invites the user to reopen 8.3 and Q8's Why line says 7.2's argument is partial. A stricter reading of step 3 would want both moved into recommendation bases; the key's definition of "asked again" does not count them.
- Q3 (item 6.2) recommends restating H2 with a 2-percentage-point non-inferiority margin, while the brief's 6.1 entry records H2 as "no worse"; the question's item is 6.2, so it is not scored as asking 6.1, the same shape as the v2-4 note.
- Q6 recommends replacing the bespoke 7-point ease item with SUS and rewriting the speed formula; this is under 7.6, which is weak in the key ("the rating has no operational definition").
- Item 7.3 printed `missing` (key: missing), as in v2-4.
- Only the first turn ran; no round was answered.
- Scenario 2's bar needs all three runs in a set to meet it; this run meets it at 76e9c28 with fixture d692e49.
