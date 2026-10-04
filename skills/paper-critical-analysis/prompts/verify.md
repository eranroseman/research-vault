# Stage 7 brief

Sent verbatim to the stage 7 verifier subagent, with the placeholders filled. It is the subagent's whole context.

```
You are checking a report against the paper it describes and against the sources it cites. Every check is match or fail; you leave the report as it stands and create no files.

## Inputs

- Paper: {PAPER_PATHS} — the paper and every appendix and supplement — and {PAGE_RENDERS} (images of pages carrying figures, tables or equations; "none" if none).
- Report: {REPORT_PATH}
- Evidence file: {EVIDENCE_PATH} — the C, W and J entries a "derived" number cites, the W entries you re-open, and the Pruning record: the editor's change list with each item marked applied or rejected.
- Scratch folder: `<paper-slug>-work/`, beside the evidence file — the saved copies of fetched sources.

## Locator convention

{LOCATOR_CONVENTION}

Resolve every locator under this convention, by the paper's own numbering and names.

## What you check

1. Every locator, quote and number the report attributes to the paper: find it in the paper. An item passes when the locator resolves to text that says what the report says it says, the quote matches the paper verbatim, and the number appears at the stated place; read a number in a figure, table or equation off the page as an image (its render, or the PDF page itself when there are no renders). A `whole paper` locator passes when a search of the paper and its supplements finds the absent item nowhere. A number the report marks "derived" is checked against the C, W or J entry it cites, not recomputed.
2. Every W entry the report cites: re-open it at its URL, or at its saved copy in the scratch folder when the URL fails. It passes when the source says what the entry says it said, and what the report attributes to the entry says no more than the entry does.
3. Every change-list item the Pruning record marks applied: compare the report's text where it landed with Before, for lost or added meaning. A rewording passes when it keeps the claim, its strength, and every qualifier, number, locator, N/C/W/J ID and provenance mark ((W12), [inferred], "derived") Before carried; for a move, check the one-line claim that stayed against what moved.

## Delegation

Do this work yourself, and spawn no subagent: this pipeline already fills every seat the critique gets, and an agent you spawned would re-read the skill and fan out again.

## What you return

The items that failed, then the three count lines below, and nothing else. Each failed item:

- the report line (quote enough to identify it),
- what the report claims,
- the locator, W entry, or change-list item you checked,
- what you found there, or "not found".

End with one line per category: locators/quotes/numbers checked and failed; W entries checked and failed; change-list items checked and failed. If nothing failed, return those three lines alone.
```

`{LOCATOR_CONVENTION}` is filled verbatim from SKILL.md's "Locators" section.
