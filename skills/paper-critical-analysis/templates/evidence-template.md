# Evidence template

`scripts/check_report.py` reads its required headings from this file, so keep them as written and replace every `{{placeholder}}`. A ledger entry starts on its own line — `- N1:`, `- C1:`, `- W1:`, or `- J1:` — and detail may continue on indented lines beneath it; the checker reads IDs from exactly that first-line shape. A section whose stage has not run yet reads `pending: stage <n>`, never blank.

______________________________________________________________________

# Evidence: {{paper title}}

Report: {{report path}}.

## Identity

Filled at stage 1, from the full text, not from the request: title; authors; venue and year; DOI; version read; full text read from; matches the paper requested ({{yes | no}}, confirmed by {{how}}).

Paper type, also at stage 1: one of empirical, theoretical, survey, systems, position, replication, or negative results; a paper fitting none is recorded as the nearest, with the mismatch named.

Method family and background files, also at stage 1: the family from SKILL.md's method menu, or for a paper fitting none, the family of its evaluation if it has one; and every file SKILL.md's load table assigns, by path.

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

Every principal claim, numbered; after the claims, as plain lines, each key quote or number with its locator and each term you had to look up. A claim's shape:

```
Claim 1: [the claim, as the paper states it]
Evidence: [what the paper offers for it]
Needed: [what evidence would settle it]
```

## Not-stated list

Everything the report will need that the paper does not give. One entry per line: `- N1: <item>; needed by <claim or slot>`.

## Inconsistency list

Every place two locations in the paper conflict. One entry per line: `- C1: <both locators; both values>`. The reconciliation log follows as plain lines under this heading, one per number reconciled: the number, the locations it was checked against, and whether they agree or the C ID it raised.

## External-check list

One entry per outside check: `- W1: <claim checked>; <source>; <URL>; <saved copy>; <what the source said>`.

Each mandated check fills its slot below with the W IDs that discharged it or `not checked: <reason>`; the checker fails an unfilled slot:

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
