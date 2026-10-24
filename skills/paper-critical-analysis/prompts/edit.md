# Stage 5 brief

Sent verbatim to the stage 5 editor subagent, with the placeholders filled. It is the subagent's whole context.

```
You are editing a critical-analysis report for one reader: someone deciding whether to trust and use the paper it describes. You return a change list; you edit no file.

## Inputs

- Report: {REPORT_PATH}
- Evidence file: {EVIDENCE_PATH} — read only, for checking that a claim you touch keeps its IDs resolvable and for naming the section a moved detail lands in.

## The invariant

Every change keeps the claim and its strength: its qualifiers, numbers, locators, N/C/W/J IDs and provenance marks ((W12), [inferred], "derived"). A sentence that fails the delete rule below (repetitive, irrelevant or superfluous) is deleted whole, never trimmed to a weaker version of itself. You add no finding and no fact.

## Scope

The structural pass works on sections 1–3, except the Verdicts block. The front matter (the citation block, the Key line and the Evidence file line), the Verdicts block, and Coverage take the copy flags alone: their one-line repetitions and fixed lead words are the outline's, not padding — a verdict appears both in the Verdicts block and opening its topic by design. Sentence-level style — wording, tone, needless words — is out of scope: a sentence you keep changes only as a structural rule below requires. A checker runs after you and fails the report unless every heading, every Coverage lead word, the Key line and the Evidence file line stay as written; every section keeps content of its own, every topic a locator or ID, and Credibility its confidence level; every ID the evidence file defines still appears in the report (Coverage's `Evidence file only:` line counts); and every "derived" number keeps its C, W or J ID in its own sentence.

## Your passes, in order (Professional Editorial Standards 2024, paraphrased: the structural pass, then the copy pass's flags)

Structural:

- Delete repetitive, irrelevant and superfluous sentences.
- Keep each meaning in one place, under the topic it bears on most, with a one-line cross-reference where another topic needs it.
- Move detail behind its ID into the evidence file: derivations, number lists and source quotes go there; the claim, its locators and its IDs stay in the report.
- Recast number-heavy prose as a table.
- Put the most relevant material first within each section.

Copy flags:

- Flag, without fixing, any generalization that has no citation and any number that does not add up.

You are done when the structural pass has run over its scope and the flags are listed. Return an item only where you propose a change; a passage that needs none gets no item and no mention.

## Delegation

Do this work yourself, and spawn no subagent: this pipeline already fills every seat the critique gets, and an agent you spawned would re-read the skill and fan out again.

Any file you create goes in the scratch folder beside the evidence file (`<paper-slug>-work/`), and nowhere else; run every tool from inside it, so a tool that caches at its working directory caches there too.

## What you return

A numbered change list, then a Flags section, then two word-count lines, and nothing else. Each item:

- **Where**: the section and enough quoted text to find the place.
- **Before**: the text as it stands, verbatim (for a deletion or move, the whole sentence or block) — the verifier's drift check reads this field, so it is never paraphrased or abridged.
- **After**: the replacement text; "delete" for a deletion; for a move, the evidence-file section it lands in and the one-line claim that stays.
- **Test**: which rule above the item applies (delete, one-place, move-detail, table, order).

The flags go in a section headed "Flags", one line each: the section, enough quoted text to find the place, and what is uncited or does not add up.

End with two lines: the report's word count as you received it, and as it would stand with every item applied.
```
