# The review

`proposal/review.md` is `review`'s record of one pass over the draft; `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_proposal.py" review proposal/review.md` (`../scripts/check_proposal.py` from this file where the variable stays unexpanded) checks the shape below, one line per defect; the wording of each value is yours to keep.

## Header

Four lines before the first section, and an optional fifth:

```text
Brief: proposal/design-brief.md (frozen 2026-10-20)
Draft: proposal/draft.md (from the brief)
Date: 2026-10-27
Checklist: experiment-proposal 0.3.0
Checker: draft --words 2000-4000 --references 15-20 --supervisor "Dr. Example"
```

`Draft:` says `(from the brief)` or `(named by the user)`; `Date:` is rewritten every pass. `Checker:` is the `draft` option set the pass ran, `draft [--sections "..."] --words A-B --references A-B [--review-section "<heading>"] [--supervisor "<name>"]`, checked when present; the next pass reads item 3.1's values from it alone, the course defaults when there is none, as for every 0.2.0 review.

## Sections

`## Items`, `## Cross-section consistency`, `## Brief against draft`, `## Substance tests`, `## Summary`, `## Waivers`, `## Hand-off`, in that order, no others, except an optional `## Judged` after Items: the research questions and hypotheses this pass judged, quoted verbatim from the draft, one per line; the next pass says in its reply when the draft's changed, and the checker reads nothing from them.

## Rows

Under Items, one row per checklist item except the six substance tests, in checklist order; under Substance tests, one each for items 13.6 to 13.11. A row is `- **<ID>** <result>`, `(fix N applied)` after a re-check, then `:` and the evidence:

```markdown
- **1.1** pass: "Is target selection faster with a mouse or a trackball?" (Introduction, para 1)
- **5.2** not confirmed: earlier review.md read confirmed by the user, 2026-10-15
- **7.5** fail: the order of the nine combinations is not stated. fix 1: add to Design, "The nine combinations will be presented in a random order per participant."
- **8.9** fail: the extras count is the placeholder [NO-SHOW EXTRAS]. decide: how many extra bookings to allow.
- **13.2** not checked: defend-stage
```

The result is one of `pass`, `pass narrowly`, `fail`, `fail (waived)`, `not confirmed`, `not checked`. A pass or a narrow pass on a draft-checked item carries a quoted passage, verbatim and at most two sentences, then its location in parentheses (section heading and, where the draft has them, page or paragraph); no quote, no pass, and a placeholder quote (`[LIKE THIS]`, `TODO`, `TBD`) is no pass: the row is `fail` with a `decide:` fix naming what the author must supply, or `fail (waived)` with the reason. A pass on an attested item carries `confirmed by the user, <date>`; `not confirmed` is for the attested items only (3.1, 5.2, 13.1 and 13.4), written by an agent run with any earlier confirmation as text after the colon, counted under Fail until an interactive pass re-asks the item. Only items 13.2 and 13.3 read `not checked`. A failure says in one sentence what is missing, then its fix.

A fix is `fix N:` and quoted replacement text in the draft's tense and voice, or `decide:` and the decision the user must make, naming `/experiment-proposal:design` when the brief must change. Fixes are numbered 1, 2, 3 in order of first appearance; `(fix N applied)` repeats a number.

## Cross-section consistency and Brief against draft

One line per finding, `- fail: <what differs, both values, both locations>. fix N: ...`, or `- pass: ...` when there is none; a resolved finding reads `- pass (fix N applied): ...`. The checker's `draft <path> --numbers` report is the search, repeated numbers, amounts and percentages grouped by value with heading, line and context; the reviewer's lines are the findings. The brief's current decision for an item is its entry, or the latest amendment naming it.

## Summary

One line, each count recomputed from the rows:

```text
Items checked: 65. Pass: 63. Fail: 2. Not checked (defend-stage): 2. Consistency and brief findings: 1. Fixes proposed: 3. Waivers: 0.
```

Items checked: every row under Items and Substance tests not `not checked`; Pass: `pass` and `pass narrowly`; Fail: `fail`, `fail (waived)` and `not confirmed`; Not checked: the two defend-stage rows; Consistency and brief findings: the `- fail` lines of the two sections; Fixes proposed: the highest fix number; Waivers: the entries under Waivers.

## Waivers

`- <ID> waived, reason: "<the user's words>" (<date>)` per waiver, or `- none`.

## Carrying an earlier review forward

When `proposal/review.md` exists, the new pass reads it first: waivers kept with their dates; item 3.1's values from its `Checker:` line, else the course defaults, offered interactively, used as they are in an agent run; no attestation carried as a pass (an agent run keeps it as text inside a `not confirmed` row, an interactive pass re-asks it in the step 3 batch); every earlier `fail` on a draft-checked item re-checked (`pass` with a new quote, or still `fail`); fixes numbered from 1 again with no earlier `(fix N applied)` marker, which belongs to the pass that applied the fix.

## Hand-off

The closing text, printed in full at the end of every message that ends a pass and copied here. With research-grill installed (`~/.claude/plugins/installed_plugins.json`, read with the Read tool, has a key beginning `oss@`; ask the user when it cannot be read, never assume absence; an agent run takes the absent form below with its first line replaced by "research-grill install not checked."):

```text
/oss:research-grill defend proposal/draft.md
Seed list: <each waiver>; could someone run a session from the Method alone?; <each substance test passed narrowly, with its doubt>.
```

Without it:

```text
research-grill is not installed. Install it with:
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
Then run: /oss:research-grill defend proposal/draft.md
Seed list: <the same list>.
```
