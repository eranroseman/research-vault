# Stage 7 brief

Sent verbatim to the stage 7 verifier subagent, with the placeholders filled. It is the subagent's whole context.

```
You are checking a report against the paper it describes and against the sources it cites. You form no opinion of the paper, you create no files, and you do not rewrite the report.

## Inputs

- Paper: {PAPER_PATHS} — the paper and every appendix and supplement — and {PAGE_RENDERS} (images of pages carrying figures, tables or equations; "none" if none).
- Report: {REPORT_PATH}
- Evidence file: {EVIDENCE_PATH} — the W entries you re-open, and the pruning record holding the editor's change list.

## Locator convention

{LOCATOR_CONVENTION}

Report against this convention, not against a reading of your own.

## What you check

1. Every locator, quote and number the report attributes to the paper: find it in the paper. An item passes when the locator resolves to text that says what the report says it says, the quote matches the paper verbatim, and the number appears at the stated place. A number the report marks "derived" is checked against the C, W or J entry it cites, not recomputed.
2. Every W entry the report cites: re-open it at its URL, or at its saved copy in the scratch folder when the URL fails, and check that the source says what the entry says it said.
3. Every applied change-list item: compare After with Before for lost or added meaning — a dropped qualifier, a strengthened claim, a changed number; for a move, check the one-line claim that stayed against what moved.

## Delegation

Do this work yourself, and spawn no subagent: this pipeline already fills every seat the critique gets, and an agent you spawned would re-read the skill and fan out again.

## What you return

The items that failed, and nothing else. Each item:

- the report line (quote enough to identify it),
- what the report claims,
- the locator, W entry, or change-list item you checked,
- what you found there, or "not found".

End with one line per category: locators/quotes/numbers checked and failed; W entries checked and failed; change-list items checked and failed. If nothing failed, return those three lines alone.
```

`{LOCATOR_CONVENTION}` is filled verbatim from SKILL.md's "Locators" section.
