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

The structural and stylistic passes work on sections 1–3, except the Verdicts block. The front matter (the citation block and the Key line), the Verdicts block, and Coverage take the copy pass alone: their one-line repetitions and fixed lead words are the outline's, not padding — a verdict appears both in the Verdicts block and opening its topic by design. A checker runs after you and fails the report unless every heading, every Coverage lead word and the Key line stay as written; every section keeps content of its own, every topic a locator or ID, and Credibility its confidence level; every ID the evidence file defines still appears in the report (Coverage's `Evidence file only:` line counts); and every "derived" number keeps its C, W or J ID in its own sentence.

## Your passes, in order (Professional Editorial Standards 2024, paraphrased: structural, then stylistic, then copy)

Structural:

- Delete repetitive, irrelevant and superfluous sentences.
- Keep each meaning in one place, under the topic it bears on most, with a one-line cross-reference where another topic needs it.
- Move detail behind its ID into the evidence file: derivations, number lists and source quotes go there; the claim, its locators and its IDs stay in the report.
- Recast number-heavy prose as a table.
- Put the most relevant material first within each section.

Stylistic:

- Tighten each sentence you keep: omit needless words, prefer active and positive forms, use concrete language.
- Remove AI-writing patterns: puffery, empty "-ing" phrases, promotional adjectives, stock vocabulary, scattered bold.

Copy:

- Make terms, numbers and abbreviations consistent across the report.
- Flag, without fixing, any generalization that has no citation and any number that does not add up.

The passes are done when every rule has been applied to every passage in its pass's scope, and every place that fails a rule has a change-list item or a flag.

## Delegation

Do this work yourself, and spawn no subagent: this pipeline already fills every seat the critique gets, and an agent you spawned would re-read the skill and fan out again.

Any file you create goes in the scratch folder beside the evidence file (`<paper-slug>-work/`), and nowhere else.

## What you return

A numbered change list, then a Flags section, then two word-count lines, and nothing else. Each item:

- **Where**: the section and enough quoted text to find the place.
- **Before**: the text as it stands, verbatim (for a deletion or move, the whole sentence or block).
- **After**: the replacement text; "delete" for a deletion; for a move, the evidence-file section it lands in and the one-line claim that stays.
- **Test**: which rule above the item applies (delete, one-place, move-detail, table, order, tighten, AI-pattern, consistency).

The copy pass's flags go in a section headed "Flags", one line each: the section, enough quoted text to find the place, and what is uncited or does not add up.

End with two lines: the report's word count as you received it, and as it would stand with every item applied.
```
