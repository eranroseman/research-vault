# The review

`proposal/review.md` is `review`'s record of one pass over the draft. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_proposal.py" review proposal/review.md` (on a host that leaves the variable unexpanded, `../scripts/check_proposal.py` relative to this file) checks the shape below, except the wording of each value, and prints one line per defect; the wording rules are yours to keep.

## Header

Four lines before the first section:

```text
Brief: proposal/design-brief.md (frozen 2026-10-20)
Draft: proposal/draft.md (from the brief)
Date: 2026-10-27
Checklist: experiment-proposal 0.2.0
```

`Draft:` says `(from the brief)` or `(named by the user)`.

## Sections

`## Items`, `## Cross-section consistency`, `## Brief against draft`, `## Substance tests`, `## Summary`, `## Waivers`, `## Hand-off`, in that order, no others.

## Rows

Under Items, one row per checklist item except the six substance tests, in checklist order; under Substance tests, one row each for items 13.6 to 13.11. A row is `- **<ID>** <result>`, then `(fix N applied)` after a re-check, then `:` and the evidence:

```markdown
- **1.1** pass: "Is target selection faster with a mouse or a trackball?" (Introduction, para 1)
- **3.1** pass: confirmed by the user, 2026-10-27
- **7.5** fail: the order of the nine combinations is not stated. fix 1: add to Design, "The nine combinations will be presented in a random order per participant, drawn by the study software."
- **9.3** fail (waived): no logging statement; waived, see Waivers.
- **13.2** not checked: defend-stage
- **13.7** pass narrowly: "H3 predicts a larger advantage for small targets" (Hypotheses); the doubt: any non-zero interaction would read as support.
```

The result is one of `pass`, `pass narrowly`, `fail`, `fail (waived)`, `not checked`. A pass or a narrow pass on a draft-checked item carries a quoted passage, verbatim and at most two sentences, followed by its location in parentheses (the section heading and, where the draft has them, the page or paragraph); no quote, no pass. A pass on an attested item carries `confirmed by the user, <date>`. Only items 13.2 and 13.3 read `not checked`, and they always do. A failure says in one sentence what is missing, then its fix.

A fix is `fix N:` followed by replacement text quoted and ready to paste in the draft's tense and voice, or `decide:` and the decision the user must make, naming `/experiment-proposal:design` when the brief must change. Fixes are numbered 1, 2, 3 in order of first appearance across the whole file; `(fix N applied)` repeats a number.

## Cross-section consistency and Brief against draft

One line per finding, `- fail: <what differs, both values, both locations>. fix N: ...`, or `- pass: ...` when there is none. The brief's current decision for an item is its entry, overridden by the latest amendment naming it.

## Summary

One line, every count recomputed from the file:

```text
Items checked: 65. Pass: 63. Fail: 2. Not checked (defend-stage): 2. Consistency and brief findings: 1. Fixes proposed: 3. Waivers: 0.
```

Items checked counts every row under Items and Substance tests that is not `not checked`; Pass counts `pass` and `pass narrowly`; Fail counts `fail` and `fail (waived)`; Not checked is the two defend-stage rows; Consistency and brief findings counts the `- fail` lines of the two sections; Fixes proposed is the highest fix number; Waivers counts the entries under Waivers.

## Waivers

`- <ID> waived, reason: "<the user's words>" (<date>)` per waiver, or `- none`.

## Hand-off

The closing text, printed in full at the end of every message that ends a pass and copied here. With research-grill installed (the file `~/.claude/plugins/installed_plugins.json`, read with the Read tool, has a key beginning `oss@`; ask the user when it cannot be read, never assume absence):

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
