# Evidence template

The evidence file is the report's audit trail; each section is filled during the stage that produces it, so an interrupted run resumes from the stage log. `scripts/check_report.py` reads its required headings from this file. A ledger entry starts on its own line — `- N1:`, `- C1:`, `- W1:`, or `- J1:` — and detail may continue on indented lines beneath it; the checker reads IDs from exactly that first-line shape, and every ID defined here must appear in the report or on Coverage's "Evidence file only" line. A section whose stage has not run yet reads `pending: stage <n>`, never blank.

______________________________________________________________________

# Evidence: {{paper title}}

Report: {{report path}}.

## Identity

Filled at stage 1, from the full text, not from the request: title; authors; venue and year; DOI; version read; full text read from; matches the paper requested ({{yes | no}}, confirmed by {{how}}).

Paper type, also at stage 1: one of empirical, theoretical, survey, systems, position, replication, or negative results; a paper fitting none is recorded as the nearest, with the mismatch named.

## Conditions

Filled at stage 0: one line per row of SKILL.md's conditions table, each with how it was settled; the web probe's request, response, and verdict.

## Stage log

One line per stage as its completion bar is met: `stage <n>: met — <date, time>`. An interrupted run resumes after the last line.

## Section map

The page or heading of each part: title, abstract, introduction, related work, hypotheses or research questions, methods, results, discussion, conclusion, references, appendices, supplements. Parts missing or merged, named.

## Promises

Five numbered lines, each quoted from or located in the title, abstract, introduction, or conclusion:

1. Problem:
2. Why it matters:
3. Approach:
4. Contribution claimed:
5. What would make it trustworthy:

## Claims

Every principal claim, numbered:

```
Claim 1: [the claim, as the paper states it]
Evidence: [what the paper offers for it]
Needed: [what evidence would settle it]
```

## Not-stated list

Everything the report will need that the paper does not give. One entry per line: `- N1: <item>; needed by <claim or slot>`.

## Inconsistency list

Every place two locations in the paper conflict. One entry per line: `- C1: <both locators; both values>`. The reconciliation log follows as plain lines under this heading: every reported result in the abstract and text reconciled against the tables, figures and supplements, every percentage, sum and effect size against the numbers it rests on, arithmetic done in code.

## External-check list

One entry per outside check: `- W1: <claim checked>; <source>; <URL or saved copy>; <what the source said>`. The related works read and the released-artifact checks are W entries too.

The mandated checks each hold a fixed slot, filled with the W IDs that discharged it or `not checked: <reason>` — the checker reports an unfilled slot, so a skipped check is a visible hole rather than a silent one:

- Venue rigor:
- Authors' previous work:
- Reference counts:
- Tree backward:
- Tree forward:
- Related works read:
- Undefined concepts:
- Headline recomputations:

## Judge points

Filled at stage 3's return: the kept points under assigned IDs, `- J1: <Kind; Locator; Observation; Evidence; Why it matters>`, then the judge's Recalled lines, then the count of points dropped as inadmissible.

## Pruning record

Filled at stage 5: word counts before and after, then the editor's change list with each item applied or rejected and why.

## Verifier list

Filled at stage 7: each verifier item with its disposition (fixed, dropped, or moved to Coverage), then the counts checked.

## Deletions

Filled at the end of stage 7: every raw participant-level file deleted from the scratch folder, by path.
