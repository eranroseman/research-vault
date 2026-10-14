# handoff rerun scenario, run 1

Date: 2026-10-14. Plugin commit: `6bb6ed7` (the plan aligned review's text at this commit). Scenario 6 (hand-off with research-grill absent), rerun after the first records (`runs/handoff-1.md` to `runs/handoff-3.md`) flagged that review's closing stdout only pointed to review.md. This run is a fresh scenario 5 project: it is not the continuation of a review record, and the 12 defects are not scored.

research-grill is not installed on this machine: no key beginning `oss@` in `~/.claude/plugins/installed_plugins.json` (`grep -o '"oss@[^"]*"'` printed nothing), and no `oss:research-grill` skill is offered to the sessions. It was not installed for this run.

## Commands

Setup (scratch project outside the repository):

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

Turn 2, the attested batch:

```bash
claude -p --continue "Confirm 3.1, 5.2 and 13.4; 11.10 and 13.1 not done." --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

Both turns exited 0. The session's last turn is turn 2; no further turn was run.

## Turn 1, stdout from the batch question onward

````text
Which fixes should I apply? Give their numbers.

research-grill is not installed.

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Once installed, run:

```text
/oss:research-grill defend proposal/draft.md
```

Seed objections:

- could someone run a session from the Method alone?
- 13.7 Falsifiability, passed narrowly: under the draft's rule a null result is only "not supported", so no outcome falsifies a hypothesis.
- 13.9 Necessity, passed narrowly: the index of difficulty is defined but no hypothesis or analysis uses it.
- 13.11 Executability, passed narrowly: the mouse and trackball have no make or model named.
````

## Turn 2, the FINAL message of the session (full stdout, verbatim)

````text
Recorded in `proposal/review.md`: 3.1, 5.2, 13.4 pass, confirmed 2026-10-14. 11.10 and 13.1 fail with your answer. 13.5 now lists 11.10 too. Summary: pass 54, fail 25.

11.10 and 13.1 are process items, no draft fix. Options: do them later and re-run review, or waive each with a reason. Say which.

Which fixes should I apply? Give their numbers.

research-grill is not installed.

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Once installed, run:

```text
/oss:research-grill defend proposal/draft.md
```

Seed objections:

- could someone run a session from the Method alone?
- 13.7 Falsifiability, passed narrowly: under the draft's rule a null result is only "not supported", so no outcome falsifies a hypothesis.
- 13.9 Necessity, passed narrowly: the index of difficulty is defined but no hypothesis or analysis uses it.
- 13.11 Executability, passed narrowly: the mouse and trackball have no make or model named.
````

## The Hand-off section of proposal/review.md after turn 2

````text
## Hand-off

research-grill is not installed.

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Once installed, run:

```text
/oss:research-grill defend proposal/draft.md
```

Seed objections:

- could someone run a session from the Method alone?
- 13.7 Falsifiability, passed narrowly: under the draft's rule a null result is only "not supported", so no outcome falsifies a hypothesis.
- 13.9 Necessity, passed narrowly: the index of difficulty is defined but no hypothesis or analysis uses it.
- 13.11 Executability, passed narrowly: the mouse and trackball have no make or model named.
````

## Criteria

| Criterion                                                                                                                | Result | Evidence                                                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Final message ends with the hand-off text itself, not a pointer to review.md                                             | pass   | the last block of turn 2's stdout is the hand-off, and the message ends on the last seed objection; turn 1's stdout also ends on the hand-off                            |
| Says "research-grill is not installed"                                                                                   | pass   | first line of the hand-off in the final message and in review.md                                                                                                         |
| Gives both install commands                                                                                              | pass   | `claude plugin marketplace add scdenney/open-science-skills` and `claude plugin install oss@open-science-skills` in a fenced block in the final message and in review.md |
| Gives the defend command for later use                                                                                   | pass   | `/oss:research-grill defend proposal/draft.md` after the install block                                                                                                   |
| Install commands come before the defend command                                                                          | pass   | order in the final message and in review.md: statement, install block, defend command, seed list                                                                         |
| Gives the seed list (each waiver; "could someone run a session from the Method alone?"; each narrow pass with its doubt) | pass   | Narrow passes in the seed list: 13.7, 13.9, 13.11, each with its doubt; the review.md rows for those three read `pass narrowly`. No waivers, so none listed.             |
| review.md's Hand-off section matches the final message                                                                   | pass   | the section holds the same statement, commands and seed list (compare the two quoted blocks above)                                                                       |
| Defect count visible (not scored)                                                                                        | note   | not scored; see the quoted turn lines for the counts the session printed                                                                                                 |

## Verdict

Run 1 of the scenario 6 rerun: pass on the tightened bar. The closing stdout of the last turn prints the hand-off itself in the required order, and review.md's Hand-off section matches. The gap flagged in `runs/handoff-1.md` is closed in this run.
