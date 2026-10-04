# Report template

Keep the headings, their order, and their numbering — `scripts/check_report.py` reads its required headings from this file. Each line under a `##` or `###` heading is guidance on what that section holds, its subsections included: answer each bullet's question in prose in the bullet's place; a Coverage bullet keeps its lead (`- Not read:` and the rest) and is filled after the colon. Replace every `{{placeholder}}`, and keep the `Key:` line verbatim — the checker requires it. Reserve the word "derived" for a computed number, in a sentence citing the C, W or J entry that holds its computation: the checker flags every sentence holding the word without such an ID, so write "drawn from" or "based on" where the sense is not a computation. A section whose stage has not run yet reads `pending: stage <n>`, never blank.

______________________________________________________________________

# Critical analysis: {{paper title}}

{{Authors (year). Title. Venue, pages or DOI.}} Version read: {{preprint and number, or published}}. Report written {{date}}.

Key: a locator cites the paper; (W12) cites a source outside the paper through the evidence file; [inferred] marks the writer's own reasoning; a number marked "derived" cites the C, W or J entry holding its computation; recalled knowledge appears only under Coverage.

## 1. Context

### 1.1 Title and authors

- Title: short and to the point? Tells you what to expect?
- Authors: how many, and what does the order say? Affiliations: one institution or many, which departments, well known? Their field?

### 1.2 Publication venue

- Which kind of venue (`references/sources-and-venues.md`), and what does that imply about review rigor? If unfamiliar, the predatory-venue check from the same file (cite the W entry).

### 1.3 The authors' previous work

- What have they done before in this area (cite the W entry)?

### 1.4 Motivation

- Why is the problem important? Does the paper motivate the research, state the contribution, and preview the rest?

### 1.5 Related work and references

- Does the paper cover relevant prior work, synthesize it rather than list it, and establish the gap it fills?
- Tree backward: are the works it builds on the field's recognized foundations, or idiosyncratic picks? Tree forward: is recent work citing a key reference conspicuously absent here (cite the W entries)?
- The 3–5 related works read for this report, one line each (cite the W entries).
- Reference counts: total; with at least one of the authors; from the authors' institution; span of years; kinds of sources. A count a citation index could not complete is labelled partial.

## 2. Summary

The abstract's content at greater length, in the paper's own order.

### 2.1 Problem

- The research questions, hypotheses, objectives, or goals; what the authors set out to do.

### 2.2 Method

- What did the authors do? Which method family (SKILL.md's method menu), and what can results from that family show and not show?
- Report what the family's file lists under "What the Summary reports" (`references/quantitative-methods.md` or `references/qualitative-methods.md`); for a paper in neither family, the methods, techniques, or process followed.

### 2.3 Results

- Big picture first, then details; how the data was analyzed; descriptive then inferential statistics.

### 2.4 Discussion

- The authors' interpretation, implications, practical value, stated limitations, and future work — as they present them.

### 2.5 Conclusion

- Does it summarize methods, results, and discussion, and restate the significance? Acknowledgements and funding?

## 3. Critical discussion

Each of the nine topics after Verdicts opens with its verdict sentence, then its points in prose.

### Verdicts

The nine verdict sentences, one line each, in the order below.

### Importance

### Credibility

Closes with a line `Confidence: <high | medium | low>` and the evidence that would raise it.

### Novelty

### Applicability

### Generalizability

### Scalability

### Assumptions

### Readability

### Ethics

## 4. Coverage

- Not read: parts of the paper, supplements, or artifacts not read, and why.
- Not checked: checks that could not run, each with its reason.
- For the reader to double-check: claims resting on inference or an unconfirmed source.
- Verification: the verifier's counts checked and failed, and the checker's final result.
- Recalled: the judge's recalled knowledge, one line each.
- Evidence file only: every N, C, W and J ID the body above does not cite.
