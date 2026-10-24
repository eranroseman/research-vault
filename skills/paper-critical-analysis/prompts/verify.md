# Stage 7 brief

Sent verbatim to each of the three stage 7 verifier subagents, with the placeholders filled. It is the subagent's whole context.

```
You are checking a report against the paper it describes and against the sources it cites. Every check is match or fail; you leave the report as it stands and create no files.

Three checks are listed under "What you check". You run check {CHECK} alone; the other two run in parallel contexts of their own, and the Inputs below hold only what your check needs.

## Inputs

### Check 1 — locators, quotes and numbers

- Paper: {PAPER_PATHS} — the paper and every appendix and supplement — and {PAGE_RENDERS} (images of every page carrying a figure, table or equation; "none" if none).
- Report: {REPORT_PATH}

### Check 2 — W entries

- Evidence file: {EVIDENCE_PATH} — its External-check list holds the W entries, one per outside check, each naming the claim checked, the source, its URL, the saved copy and what the source said.
- Scratch folder: `<paper-slug>-work/`, beside the evidence file — the saved copies of fetched sources.
- The web, for re-opening each entry's URL.

### Check 3 — claim strength and edit drift

- Report: {REPORT_PATH}
- Draft: {DRAFT_PATH} — the report as it stood before the editor's changes.
- Evidence file: {EVIDENCE_PATH} — every N, C, W and J entry the report cites, and the Pruning record: the editor's change list with each item marked applied or rejected.

## Locator convention

{LOCATOR_CONVENTION}

Resolve every locator under this convention, by the paper's own numbering and names.

## What you check

1. Every locator, quote and number the report attributes to the paper: find it in the paper. An item passes when the locator resolves to text that says what the report says it says, the quote matches the paper verbatim, and the number appears at the stated place; read a number in a figure, table or equation off the page as an image (its render, or the PDF page itself when there are no renders). A `whole paper` locator passes when a search of the paper and its supplements finds the absent item nowhere. A number the report marks "derived" is check 3's, not yours: skip it.
2. Every W entry in the evidence file: re-open it at its URL, or at its saved copy in the scratch folder when the URL fails. It passes when the source says what the entry says it said.
3. Two checks of the report against the evidence file. Claim strength: every sentence citing an N, C, W or J entry says no more than the entry does — the same scope, the same hedges, the same time and tense, the same subject (the released code is not the deployment; "pointed out" is not "judged inadequate") — and a number marked "derived" matches the value its C, W or J entry computes. Edit drift: every change-list item the Pruning record marks applied — compare the report's text where it landed with Before, for lost or added meaning, reading the draft where Before needs its surroundings. A rewording passes when it keeps the claim, its strength, and every qualifier, number, locator, N/C/W/J ID and provenance mark ((W12), [inferred], "derived") Before carried; for a move, check the one-line claim that stayed against what moved.

## Delegation

Do this work yourself, and spawn no subagent: this pipeline already fills every seat the critique gets, and an agent you spawned would re-read the skill and fan out again.

## What you return

The items that failed, then your count line, and nothing else. Each failed item:

- the report line (quote enough to identify it),
- what the report claims,
- the locator, entry, or change-list item you checked,
- what you found there, or "not found".

End with one count line for your check: check 1, locators, quotes and numbers checked and failed; check 2, W entries checked and failed; check 3, claims checked and failed, then change-list items checked and failed. If nothing failed, return the count line alone.
```

`{CHECK}` is filled with `1`, `2` or `3`. The dispatcher fills that check's Inputs subsection and removes the other two subsections, so each verifier holds only its own inputs. `{DRAFT_PATH}` is the draft stage 4 saved, `critical-analysis-<paper-slug>.draft.md`. `{LOCATOR_CONVENTION}` is filled verbatim from SKILL.md's "Locators" section, in every dispatch.
