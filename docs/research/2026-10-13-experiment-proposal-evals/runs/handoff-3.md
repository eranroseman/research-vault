# handoff scenario, run 3

Date: 2026-10-14. Plugin commit: `16f7bb6`. Scenario 6 (hand-off with research-grill absent). The run is the end of review run 3 (`runs/review-3.md`, same project, same commands); the missing-input checks are recorded in `runs/review-1.md`.

research-grill is not installed on this machine: `~/.claude/plugins/installed_plugins.json` holds no key beginning `oss@` (grep count 0), so the "absent" branch is testable.

## What the end of the run printed

End of turn 1 (stdout, the line about the hand-off):

```text
research-grill not installed. Install commands and seed objections are in the Hand-off section of review.md.
```

End of turn 3 (stdout, after the fixes):

```text
(no line mentions research-grill or the hand-off; the turn ended on the open-items question)
```

The turn 1 and turn 3 stdout name the missing install and point to the file; neither carries the two commands or the seed list.

## The Hand-off section of proposal/review.md (first pass, committed)

````text
research-grill is not installed.

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
````

Then run `/oss:research-grill defend proposal/draft.md` with these seed objections:

- could someone run a session from the Method alone?
- 13.6 Delta, passed narrowly: the third contribution reads as a feature, and "current devices" is claimed while no device is named.
- 13.9 Necessity, passed narrowly: the index-of-difficulty formula serves no hypothesis or model.
- 13.11 Executability, passed narrowly: the apparatus is unnamed, so the first step is a choice the draft leaves open.

````

## Supplementary turn: "Print the hand-off again."

```text
Hand-off, as in review.md (unchanged; no waivers yet, narrow passes unchanged):

research-grill is not installed.

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
````

Then run `/oss:research-grill defend proposal/draft.md` with these seed objections:

- could someone run a session from the Method alone?
- 13.6 Delta, passed narrowly: the third contribution reads as a feature, and "current devices" is claimed while no device is named.
- 13.9 Necessity, passed narrowly: the index-of-difficulty formula serves no hypothesis or model.
- 13.11 Executability, passed narrowly: the apparatus is unnamed, so the first step is a choice the draft leaves open.

Note: review not done. 26 items still fail, none waived. Defend stage normally follows a clean review.

```

## Criteria

| Criterion | Result | Evidence |
| --- | --- | --- |
| Says research-grill is not installed | pass | first line of the Hand-off section and of the reprint |
| Gives both install commands | pass | `claude plugin marketplace add scdenney/open-science-skills` and `claude plugin install oss@open-science-skills` in the Hand-off section and the reprint |
| Gives the seed list (each waiver; "could someone run a session from the Method alone?"; each narrow pass with its doubt) | pass | three narrow passes (13.6, 13.9, 13.11) with doubts and the Method-alone question |
| The hand-off is printed at the end of the run (SKILL: "End by printing the hand-off, also into the file's Hand-off section") | miss, minor | the end-of-run stdout names the missing install and refers to the file; the full text printed only when asked again |
| Install commands "in place of the defend command" | minor deviation | the section prints the install commands and then also the line "then run `/oss:research-grill defend proposal/draft.md`" |

## Verdict

Run 3 of scenario 6: pass on the README bar (a clear install message with both commands and the seed list is in the file's Hand-off section and is printed on request), with one flagged gap: the run's own closing stdout does not print the hand-off. Controller to decide whether the gap needs a fix.
```
