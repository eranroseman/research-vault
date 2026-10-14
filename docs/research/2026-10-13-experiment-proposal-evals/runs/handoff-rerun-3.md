# handoff rerun scenario, run 3

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
Which fixes should I apply? Give their numbers. Fix 2, fix 7, fix 19 are `decide:` fixes needing your input. Fix 18 includes fix 1's sentence; pick one.

Could not read `~/.claude/plugins/installed_plugins.json` (blocked outside working directory); relied on skill list, where `oss:research-grill` absent.

research-grill is not installed.

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Once installed, run: `/oss:research-grill defend proposal/draft.md`

Seed objections:

- Could someone run a session from the Method alone?
- 13.6 Delta, passed narrowly: the "current devices" delta rests on a claim the brief's open lit-search item has not yet checked.
- 13.7 Falsifiability, passed narrowly: under the draft's own rule a null result is "not supported rather than as refuted", so no null ever falsifies.
- 13.11 Executability, passed narrowly: the apparatus is unnamed and the within-versus-between design conflict leaves the session's shape open.
````

## Turn 2, the FINAL message of the session (full stdout, verbatim)

````text
Recorded. Rows 3.1, 5.2, 13.4 now `pass: confirmed by the user, 2026-10-14`. Rows 11.10 and 13.1 now fail with what you said. 13.5 list gains 11.10. Summary: 52 pass, 27 fail, 0 pending.

Two paths for 11.10 and 13.1: do them later and tell me, then rows flip to pass. Or waive now with a reason; row becomes `fail (waived)`, reason recorded verbatim under Waivers.

Still open, all three answerable in one reply:

1. **Fix numbers to apply.** Fix 2, fix 7, fix 19 need decisions (make and model; within versus between; contact address). Fix 18 contains fix 1; pick one.
2. **Fix 7 route.** Amend brief to within subjects via `/experiment-proposal:design`, or revert draft to between subjects (also needs design skill for brief 2.2 session estimate).
3. **11.10 and 13.1.** Waive with reason, or leave failing until done.

Hand-off unchanged, in file:

research-grill is not installed.

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Once installed, run: `/oss:research-grill defend proposal/draft.md`

Seed objections:

- Could someone run a session from the Method alone?
- 13.6 Delta, passed narrowly: the "current devices" delta rests on a claim the brief's open lit-search item has not yet checked.
- 13.7 Falsifiability, passed narrowly: under the draft's own rule a null result is "not supported rather than as refuted", so no null ever falsifies.
- 13.11 Executability, passed narrowly: the apparatus is unnamed and the within-versus-between design conflict leaves the session's shape open.
````

## The Hand-off section of proposal/review.md after turn 2

````text
## Hand-off

research-grill is not installed.

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Once installed, run: `/oss:research-grill defend proposal/draft.md`

Seed objections:

- Could someone run a session from the Method alone?
- 13.6 Delta, passed narrowly: the "current devices" delta rests on a claim the brief's open lit-search item has not yet checked.
- 13.7 Falsifiability, passed narrowly: under the draft's own rule a null result is "not supported rather than as refuted", so no null ever falsifies.
- 13.11 Executability, passed narrowly: the apparatus is unnamed and the within-versus-between design conflict leaves the session's shape open.
````

## Criteria

| Criterion                                                                                                                | Result | Evidence                                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------ | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Final message ends with the hand-off text itself, not a pointer to review.md                                             | pass   | the last block of turn 2's stdout is the hand-off, and the message ends on the last seed objection; turn 1's stdout also ends on the hand-off                                                                                                                                                                                    |
| Says "research-grill is not installed"                                                                                   | pass   | first line of the hand-off in the final message and in review.md                                                                                                                                                                                                                                                                 |
| Gives both install commands                                                                                              | pass   | `claude plugin marketplace add scdenney/open-science-skills` and `claude plugin install oss@open-science-skills` in a fenced block in the final message and in review.md                                                                                                                                                         |
| Gives the defend command for later use                                                                                   | pass   | `/oss:research-grill defend proposal/draft.md` after the install block                                                                                                                                                                                                                                                           |
| Install commands come before the defend command                                                                          | pass   | order in the final message and in review.md: statement, install block, defend command, seed list                                                                                                                                                                                                                                 |
| Gives the seed list (each waiver; "could someone run a session from the Method alone?"; each narrow pass with its doubt) | pass   | Narrow passes in the seed list: 13.6, 13.7, 13.11, each with its doubt. No waivers. Turn 1 also noted that it could not read `~/.claude/plugins/installed_plugins.json` (blocked outside the working directory) and decided from the skill list, where `oss:research-grill` is absent; the branch taken was still the right one. |
| review.md's Hand-off section matches the final message                                                                   | pass   | the section holds the same statement, commands and seed list (compare the two quoted blocks above)                                                                                                                                                                                                                               |
| Defect count visible (not scored)                                                                                        | note   | not scored; see the quoted turn lines for the counts the session printed                                                                                                                                                                                                                                                         |

## Verdict

Run 3 of the scenario 6 rerun: pass on the tightened bar. The closing stdout of the last turn prints the hand-off itself in the required order, and review.md's Hand-off section matches. The gap flagged in `runs/handoff-3.md` is closed in this run.
