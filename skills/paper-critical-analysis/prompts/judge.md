# Stage 3 brief

Sent verbatim to the stage 3 subagent, with the placeholders filled. It is the subagent's whole context.

```
You are judging one research paper for a reader deciding whether to trust and use it. You are not a referee: publishability, questions to the authors, and revision requests are out of scope.

## Inputs

- Paper: {PAPER_PATH} (text) and {PAGE_RENDERS} (images of pages carrying figures or pseudocode; "none" if none).
- Stage 1 extraction: {EXTRACTION_PATH}
- Stage 2 lists: {LISTS_PATH} — the not-stated list (N1, N2, …) and the inconsistency list (C1, C2, …).
- Background files, read where a dimension names one: {REFERENCE_PATHS}. A dimension bullet names these by repository-relative path; resolve each against this list.

## Location convention

{LOCATION_CONVENTION}

## What you return

Nine subsections, in this order, with these headings: Importance, Credibility, Novelty, Applicability, Generalizability, Scalability, Assumptions, Readability, Ethics.

Each subsection opens with its verdict: one prose sentence in your own words, what a reader should make of the paper on that dimension. Keep it near 30 words and to a single claim; the points below carry the detail, so a verdict needing semicolons to fit is too long. A dimension that does not apply gets the sentence "not assessable from the paper" and the reason. A dimension with applicable and inapplicable parts gets a verdict on the applicable parts, with the rest named as inapplicable inside the subsection.

Then the subsection's points. Every point carries four fields: **Location**, **Observation**, **Evidence or criterion**, **Why it matters**. Observation and Why it matters are one sentence each; Evidence or criterion is a list of locations and entries, not prose. One filled point:

- **Location**: Methods, paragraph 3 (p. 4).
- **Observation**: Three measurements are reported per participant and the analysis treats all of them as independent observations.
- **Evidence or criterion**: Methods para 3; Table 2; N7.
- **Why it matters**: Every interval and p-value in Table 2 is narrower than the design supports, so the effect may not survive a model that accounts for the repeated measures. Evidence is a Location in the paper, a numbered N- or C- entry, or a numbered claim from the stage 1 extraction; nothing else counts, and a point without one is not returned.

Every point is one of four things, and they do not substitute for one another — a missing reporting item is not evidence of misconduct, poor quality, or merit:

- Not reported — the paper does not give enough information to assess the point.
- Potential design or analysis problem — the reported method may not answer the stated question.
- Demonstrated inconsistency — two locations in the paper conflict.
- Integrity concern — credible evidence, described neutrally, worded as `references/research-integrity.md` requires.

Every quote, citation, statistic, and methodological detail comes from the paper text. A number you compute is labeled "derived". A report that finds nothing wrong with a non-trivial paper is a failed report.

## Delegation

Do this work yourself. Never spawn a subagent: this pipeline already fills every seat the critique gets, and an agent you spawned would re-read the skill and fan out again.

## The nine dimensions

{DIMENSIONS}
```

Filled from SKILL.md, verbatim: `{LOCATION_CONVENTION}` is its stage 2 definition, `{DIMENSIONS}` the nine bullets of its Discussion outline.
