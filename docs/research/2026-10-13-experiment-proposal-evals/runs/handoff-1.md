# handoff scenario, run 1

Date: 2026-10-14. Plugin commit: `16f7bb6`. Scenario 6 (hand-off with research-grill absent). The run is the end of review run 1 (`runs/review-1.md`, same project, same commands); the missing-input checks are recorded in `runs/review-1.md`.

research-grill is not installed on this machine: `~/.claude/plugins/installed_plugins.json` holds no key beginning `oss@` (grep count 0), so the "absent" branch is testable.

## What the end of the run printed

End of turn 1 (stdout, the line about the hand-off):

```text
research-grill not installed. Hand-off and install commands in review.md.
```

End of turn 3 (stdout, after the fixes):

```text
Next: more fix numbers, or waiver reasons. Hand-off in review.md stands: install research-grill, then `/oss:research-grill defend proposal/draft.md`.
```

The turn 1 and turn 3 stdout name the missing install and point to the file; neither carries the two commands or the seed list.

## The Hand-off section of proposal/review.md (first pass, committed)

````text
research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
````

then run `/oss:research-grill defend proposal/draft.md`.

Seed objections for the defend stage:

- Could someone run a session from the Method alone? (The devices are unnamed, and the order of the nine combinations is unstated.)
- 13.7 Falsifiability, passed narrowly: no result falsifies a hypothesis under the draft's rule; what result would make you abandon H1?
- 13.9 Necessity, passed narrowly: Fitts's law and the index of difficulty are cited but never used; why not model the index of difficulty, or drop the paragraph?
- 13.11 Executability, passed narrowly: which mouse and which trackball, and does the choice of a modern trackball change the expected 120 ms effect?
- Device within or between subjects: the brief and the draft disagree, and the power analysis follows the brief.

````

## Supplementary turn: "Print the hand-off again."

```text
research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
````

then run `/oss:research-grill defend proposal/draft.md`.

Seed objections for the defend stage:

- Could someone run a session from the Method alone? (The devices are still unnamed.)
- 13.7 Falsifiability, passed narrowly: no result falsifies a hypothesis under the draft's rule; what result would make you abandon H1?
- 13.9 Necessity, passed narrowly: Fitts's law and the index of difficulty are cited but never used; why not model the index of difficulty, or drop the paragraph?
- 13.11 Executability, passed narrowly: which mouse and which trackball, and does the choice of a modern trackball change the expected 120 ms effect?
- Device within or between subjects: the brief and the draft disagree, and the power analysis follows the brief.

Waivers: none recorded.

```

## Criteria

| Criterion | Result | Evidence |
| --- | --- | --- |
| Says research-grill is not installed | pass | first line of the Hand-off section and of the reprint |
| Gives both install commands | pass | `claude plugin marketplace add scdenney/open-science-skills` and `claude plugin install oss@open-science-skills` in the Hand-off section and the reprint |
| Gives the seed list (each waiver; "could someone run a session from the Method alone?"; each narrow pass with its doubt) | pass | three narrow passes (13.7, 13.9, 13.11) with doubts, the Method-alone question and the device within/between disagreement |
| The hand-off is printed at the end of the run (SKILL: "End by printing the hand-off, also into the file's Hand-off section") | miss, minor | the end-of-run stdout names the missing install and refers to the file; the full text printed only when asked again |
| Install commands "in place of the defend command" | minor deviation | the section prints the install commands and then also the line "then run `/oss:research-grill defend proposal/draft.md`" |

## Verdict

Run 1 of scenario 6: pass on the README bar (a clear install message with both commands and the seed list is in the file's Hand-off section and is printed on request), with one flagged gap: the run's own closing stdout does not print the hand-off. Controller to decide whether the gap needs a fix.
```
