# handoff grill, run 6

Date: 2026-10-14. Plugin commit: `510579b` (the plugin tree at the worktree head `06a1eec` is identical: `git diff --stat 510579b HEAD -- plugins/experiment-proposal` is empty). Scenario 6 (hand-off), research-grill PRESENT. This is a fresh scenario 5 project, not the continuation of a review record; the 12 defects are not scored. This commit changed how review detects research-grill: it reads `~/.claude/plugins/installed_plugins.json` with the Read tool and looks for a key beginning `oss@`, and asks the user when the file cannot be read.

## State before the phase

`claude plugin list` (the oss entry), taken before the runs:

```text
  ❯ oss@open-science-skills
    Version: 2.35.1
    Scope: user
    Status: ✔ enabled
```

`~/.claude/plugins/installed_plugins.json` holds the key `oss@open-science-skills`.

## Commands

Setup (scratch project outside the repository, the scenario 5 fixtures committed):

```bash
tmp=$(mktemp -d) && cd "$tmp" && git init -q && git commit --allow-empty -qm init && mkdir proposal
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.brief.md proposal/design-brief.md
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.md proposal/draft.md
git add -A && git commit -qm fixtures
P=<checkout>/plugins/experiment-proposal
```

Turn 1 (prompt before `--allowedTools`; stdin from `/dev/null`):

```bash
claude -p "/experiment-proposal:review" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

Turn 2:

```bash
claude -p --continue "Confirm 3.1, 5.2 and 13.4; 11.10 and 13.1 not done." --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

Both turns exited 0. Turn 2 is the last turn; no further turn was run. Review did not ask whether research-grill is installed (its fallback question), so no answer was given. The defend command was not run. The three runs of this phase executed in parallel in three scratch projects.

## Turn 1, stdout from the batch question onward

````text
2. Which fixes should I apply? Give their numbers (1 to 24). Fix 2, 5, 21, 23 are `decide:` fixes; state the decision with the number. Any failure you will not fix: give a waiver reason.

**Hand-off** (also in file). research-grill installed. Not yet ready: run once every item passes or is waived:

```text
/oss:research-grill defend proposal/draft.md
```

Seed objections:
- Could someone run a session from the Method alone?
- Falsifiability (13.7, narrow): under draft's rule no result ever refutes a hypothesis; null is only "not supported".
- Necessity (13.9, narrow): Fitts's law index of difficulty stated in Literature review, never used in Design or Planned analysis.
- Waivers: none recorded.
````

## Turn 2, the FINAL message of the session (full stdout, verbatim)

````text
Recorded. 3.1, 5.2, 13.4 pass (confirmed 2026-10-14). 11.10 and 13.1 fail with your "not done". Summary now: pass 49, fail 30, defend-stage 2.

11.10 and 13.1 are process items, no draft text fixes them. 11.10 clears when `proposal/power.R` runs end to end without error. 13.1 clears when you review draft against seven reader questions and revise. Say so when done and I update rows.

Still need: which fixes should I apply? Give numbers 1 to 24. For `decide:` fixes (2, 5, 21, 23) state the decision with the number. Any failure you will not fix: give waiver reason.

Hand-off unchanged, in file. research-grill installed. Run once every item passes or is waived:

```text
/oss:research-grill defend proposal/draft.md
```

Seed objections:
- Could someone run a session from the Method alone?
- Falsifiability (13.7, narrow): under draft's rule no result ever refutes a hypothesis; null is only "not supported".
- Necessity (13.9, narrow): Fitts's law index of difficulty stated in Literature review, never used in Design or Planned analysis.
- Waivers: none recorded.
````

## The Hand-off section of proposal/review.md after turn 2

```text
## Hand-off

Not yet ready for the defend stage: 30 items fail, among them 11.10 (power.R not yet dry-run) and 13.1 (seven reader questions not yet applied). Once every item passes or is waived, run:

/oss:research-grill defend proposal/draft.md

Seed list of objections:

- Could someone run a session from the Method alone?
- Falsifiability (item 13.7, passed narrowly): under the draft's decision rule no result ever refutes a hypothesis; a null is only "not supported".
- Necessity (item 13.9, passed narrowly): the Fitts's law index of difficulty is stated in the Literature review but never used in the Design or the Planned analysis.
- Waivers: none recorded.
```

## How review detected the install state

Taken from the session transcript (the session log of the scratch project). Review read the file with the **Read** tool:

```text
Read: ~/.claude/plugins/installed_plugins.json
  -> read succeeded (no error); it holds the key `oss@open-science-skills`
```

A Bash call (`ls` and `git`) came after the Read; it was refused and is unrelated to detection. Review did not ask the user whether research-grill is installed. The state it printed matches the real state.

## Criteria

| Criterion                                                       | Result           | Evidence                                                                                                                                                                                                                                                                                                                                                                        |
| --------------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exact command `/oss:research-grill defend proposal/draft.md`    | pass             | present in a code block in the final message and as a line in review.md. Added wording (flagged, not a miss against this bar): both place a gate before it, "Run once every item passes or is waived:" in the final message and "Not yet ready for the defend stage: 30 items fail ... Once every item passes or is waived, run:" in review.md. The skill text has no such gate |
| No install commands                                             | pass             | none; the final message says "research-grill installed."                                                                                                                                                                                                                                                                                                                        |
| Seed list: each waiver                                          | pass             | no waivers; the list closes with "Waivers: none recorded."                                                                                                                                                                                                                                                                                                                      |
| Seed list: "could someone run a session from the Method alone?" | pass             | first seed objection                                                                                                                                                                                                                                                                                                                                                            |
| Seed list: each narrow pass with its doubt                      | pass             | 13.7 and 13.9, each with a doubt. review.md has exactly these two as `pass narrowly`; 13.11 is a `fail` in this run, so it is not a narrow pass                                                                                                                                                                                                                                 |
| Final message ends with the hand-off text itself                | pass             | turn 2 stdout ends on the seed list                                                                                                                                                                                                                                                                                                                                             |
| review.md Hand-off matches the final message                    | pass with a note | same command and seed objections; the framing differs (review.md opens "Not yet ready ...", the final message opens "Hand-off unchanged, in file. research-grill installed.")                                                                                                                                                                                                   |
| Detection                                                       | pass             | Read of `installed_plugins.json`, succeeded, key `oss@` present                                                                                                                                                                                                                                                                                                                 |

## Verdict

Run 6 of the scenario 6 hand-off with research-grill present: **PASS** on the bar, with one flagged deviation: the hand-off tells the user to run the defend command only once every item passes or is waived, a gate the skill text does not contain. The exact command, no install commands, the seed list and the Read detection are all present.
