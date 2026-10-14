# handoff scenario, run 2

Date: 2026-10-14. Plugin commit: `16f7bb6`. Scenario 6 (hand-off with research-grill absent). The run is the end of review run 2 (`runs/review-2.md`, same project, same commands); the missing-input checks are recorded in `runs/review-1.md`.

research-grill is not installed on this machine: `~/.claude/plugins/installed_plugins.json` holds no key beginning `oss@` (grep count 0), so the "absent" branch is testable.

## What the end of the run printed

End of turn 1 (stdout, the line about the hand-off):

```text
research-grill not installed. Install commands in review.md Hand-off section. Advisor was rate-limited this turn; review not advisor-checked.
```

End of turn 3 (stdout, after the fixes):

```text
- Cross-section consistency: unaffected. Hand-off: unchanged.
```

The turn 1 and turn 3 stdout name the missing install and point to the file; neither carries the two commands or the seed list.

## The Hand-off section of proposal/review.md (first pass, committed)

````text
research-grill is not installed. To install it:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
````

Then run the defend stage on proposal/draft.md with these seed objections:

- Could someone run a session from the Method alone?
- Delta (passed narrowly): the delta rests on "current devices", yet the devices are unnamed.
- Necessity (passed narrowly): the third contribution, a reusable program, serves no hypothesis, the gap or the method.
- Method fit (passed narrowly): the hypotheses are addressed with tests that step 11 replaces.
- Executability (passed narrowly): the apparatus has no make or model, so the first purchase or booking is unclear.
- Waivers: none yet.

````

## Supplementary turn: "Print the hand-off again."

```text
research-grill is not installed. To install it:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
````

Then run the defend stage on `proposal/draft.md` with these seed objections:

- Could someone run a session from the Method alone?
- Delta (passed narrowly): the delta rests on "current devices", yet the devices are unnamed.
- Necessity (passed narrowly): the third contribution, a reusable program, serves no hypothesis, the gap or the method.
- Method fit (passed narrowly): the hypotheses are addressed with tests that step 11 replaces.
- Executability (passed narrowly): the apparatus has no make or model, so the first purchase or booking is unclear.
- Waivers: none yet.

Same text sits in the Hand-off section of `proposal/review.md`. Note: 25 items still fail, so defend stage is premature until fixes or waivers land.

```

## Criteria

| Criterion | Result | Evidence |
| --- | --- | --- |
| Says research-grill is not installed | pass | first line of the Hand-off section and of the reprint |
| Gives both install commands | pass | `claude plugin marketplace add scdenney/open-science-skills` and `claude plugin install oss@open-science-skills` in the Hand-off section and the reprint |
| Gives the seed list (each waiver; "could someone run a session from the Method alone?"; each narrow pass with its doubt) | pass | four narrow passes (Delta, Necessity, Method fit, Executability), the Method-alone question, "Waivers: none yet" |
| The hand-off is printed at the end of the run (SKILL: "End by printing the hand-off, also into the file's Hand-off section") | miss, minor | the end-of-run stdout names the missing install and refers to the file; the full text printed only when asked again |
| Install commands "in place of the defend command" | pass | the section gives the install commands and "Then run the defend stage on proposal/draft.md", without the slash command |

## Verdict

Run 2 of scenario 6: pass on the README bar (a clear install message with both commands and the seed list is in the file's Hand-off section and is printed on request), with one flagged gap: the run's own closing stdout does not print the hand-off. Controller to decide whether the gap needs a fix.
```
