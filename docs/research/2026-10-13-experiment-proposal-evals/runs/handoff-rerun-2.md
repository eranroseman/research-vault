# handoff rerun scenario, run 2

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
**Attested items (five, one batch):**
1. Item 3.1: Have you identified the template, length limit, citation style, section list, and whether appendices and references count toward the limit? If no template, confirm the typical sections were chosen.
2. Item 5.2: Has snowballing from at least one recent key article stopped turning up new relevant work? Note the brief's open item 1, the lit-search for a current-device comparison, is still open.
3. Item 11.10: Has the analysis script been dry-run end to end on simulated data? The brief cites `proposal/power.R` run on 2026-10-10, but that file is not in `proposal/`. Did it run, and where is it?
4. Item 13.1: Has the proposal been reviewed against the seven reader questions (importance, credibility, ethics, novelty, external validity, assumptions, readability) and revised where it fell short?
5. Item 13.4: Can the reason for every choice in the Design section be given? The brief's rationale entries are the record.

**Fixes:** Which fixes should I apply? Give their numbers.

Hand-off:

research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`.

Seed objections:

- Could someone run a session from the Method alone? The devices have no make or model, and the Procedure never names the program or display.
- Delta (13.6, narrow): is "a reusable target-selection task program and its logs" a contribution beyond the cited work, and do earlier comparisons give mixed results or consistently favour the mouse?
- Necessity (13.9, narrow): does the Fitts's-law formula serve any hypothesis or analysis?
- Executability (13.11, narrow): can the pilot settle the make and model without changing a hypothesis?
- Device between or within subjects: the frozen brief says between (asymmetric habit transfer), the draft says within; brief 2.2's 35-minute session assumes both devices per participant.
````

## Turn 2, the FINAL message of the session (full stdout, verbatim)

````text
Recorded in `proposal/review.md`. 3.1, 5.2, 13.4 now pass, confirmed 2026-10-14. 11.10 and 13.1 fail per your answer. 13.5 row and Summary updated: 51 pass, 28 fail, 0 pending.

11.10 and 13.1 have no draft fix. Options: run `proposal/power.R` on simulated data and do the seven-question review, then tell me, or ask for a waiver with your reason, which goes under Waivers.

Which fixes should I apply? Give their numbers.

Hand-off unchanged:

research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`.

Seed objections:

- Could someone run a session from the Method alone? The devices have no make or model, and the Procedure never names the program or display.
- Delta (13.6, narrow): is "a reusable target-selection task program and its logs" a contribution beyond the cited work, and do earlier comparisons give mixed results or consistently favour the mouse?
- Necessity (13.9, narrow): does the Fitts's-law formula serve any hypothesis or analysis?
- Executability (13.11, narrow): can the pilot settle the make and model without changing a hypothesis?
- Device between or within subjects: the frozen brief says between (asymmetric habit transfer), the draft says within; brief 2.2's 35-minute session assumes both devices per participant.
````

## The Hand-off section of proposal/review.md after turn 2

````text
## Hand-off

research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`.

Seed objections:

- Could someone run a session from the Method alone? The devices have no make or model, and the Procedure never names the program or display.
- Delta (13.6, narrow): is "a reusable target-selection task program and its logs" a contribution beyond the cited work, and do earlier comparisons give mixed results or consistently favour the mouse?
- Necessity (13.9, narrow): does the Fitts's-law formula serve any hypothesis or analysis?
- Executability (13.11, narrow): can the pilot settle the make and model without changing a hypothesis?
- Device between or within subjects: the frozen brief says between (asymmetric habit transfer), the draft says within; brief 2.2's 35-minute session assumes both devices per participant.
````

## Criteria

| Criterion                                                                                                                | Result | Evidence                                                                                                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Final message ends with the hand-off text itself, not a pointer to review.md                                             | pass   | the last block of turn 2's stdout is the hand-off, and the message ends on the last seed objection; turn 1's stdout also ends on the hand-off                                       |
| Says "research-grill is not installed"                                                                                   | pass   | first line of the hand-off in the final message and in review.md                                                                                                                    |
| Gives both install commands                                                                                              | pass   | `claude plugin marketplace add scdenney/open-science-skills` and `claude plugin install oss@open-science-skills` in a fenced block in the final message and in review.md            |
| Gives the defend command for later use                                                                                   | pass   | `/oss:research-grill defend proposal/draft.md` after the install block                                                                                                              |
| Install commands come before the defend command                                                                          | pass   | order in the final message and in review.md: statement, install block, defend command, seed list                                                                                    |
| Gives the seed list (each waiver; "could someone run a session from the Method alone?"; each narrow pass with its doubt) | pass   | Narrow passes in the seed list: 13.6, 13.9, 13.11 (13.7 failed in this run, so it is not a narrow pass), each with its doubt; the within/between disagreement is added. No waivers. |
| review.md's Hand-off section matches the final message                                                                   | pass   | the section holds the same statement, commands and seed list (compare the two quoted blocks above)                                                                                  |
| Defect count visible (not scored)                                                                                        | note   | not scored; see the quoted turn lines for the counts the session printed                                                                                                            |

## Verdict

Run 2 of the scenario 6 rerun: pass on the tightened bar. The closing stdout of the last turn prints the hand-off itself in the required order, and review.md's Hand-off section matches. The gap flagged in `runs/handoff-2.md` is closed in this run.
