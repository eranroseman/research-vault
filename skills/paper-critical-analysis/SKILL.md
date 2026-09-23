---
name: paper-critical-analysis
description: In-depth critical analysis of one research paper, written for a reader deciding whether to trust it rather than an editor deciding whether to publish it. Extract, list what the paper does not say, judge nine named dimensions in a fresh context, tighten, then verify every cited location against the paper.
disable-model-invocation: true
---

# Critiquing a paper

Thoroughness is the constraint here, token cost is not.

## Input and output

Input: one paper, read in full. Output: one markdown file in the outline under "The report", named for the paper and written beside the input unless told otherwise.

Six stages, every one of them on every paper: extract, list what the paper does not say, judge, assemble, tighten, verify. Create a todo per stage and close each as its artifact exists.

## What varies

Settle all of these before stage 1. Each changes what a later stage does, and a condition discovered mid-run costs a stage its work.

| Condition | What it changes |
|---|---|
| The Read tool cannot render the PDF | Extract the text with a local tool (pypdf, PyMuPDF, or pdftotext) and render the pages carrying figures or pseudocode to images. Stage 6's verifier is handed those renders. With no tool available, ask for the text. |
| The paper exceeds 30 pages, appendices and supplements included | Stage 1 runs one subagent per section, each returning the extraction fields for its section; stage 2 runs in the main context over the merged extraction. Settle the row above first: a fan-out discovered unrenderable mid-flight wastes every branch. |
| Web access — probe it, never ask | Fetch one known-good record, such as `https://api.crossref.org/works/<a DOI the paper cites>`. A fetch that returns the record turns on the four searches in the Context section, the author-background, tree-forward, same-institution-count and citation-existence checks, and looking up a concept the paper never defines. Report the probe either way. |
| The probe is refused or fails | Those four slots, and whether a citation exists, read "not checked: no web access", and the did-not-check section names the probe and what it returned. Retry once on a network error before concluding this; a refusal needs no retry. |
| The paper has an experiment, a measurement, or a statistical analysis | Stage 2 walks `references/experiment-design.md` and `references/quantitative-results.md`. |
| The paper is qualitative or mixed-methods | Stage 2 walks `references/qualitative-methods.md`. |
| People took part in the research | Stage 2 walks `references/participants.md`. |
| No method family fits the paper | Stage 2 walks every background file. |

Whatever the paper, stage 2 walks `references/research-integrity.md` and the source types and method menu at the end of this file.

## Stage 1 — Extract, in the authors' frame

Open the report file first, at the path above, carrying the headings under "The report" and nothing beneath them. Every later stage writes into it, and both briefs are handed its path.

Then record, as the paper presents it:

| Field | Description |
|-------|-------------|
| **Title** | Full paper title |
| **Authors** | Author list and affiliations |
| **Venue / Status** | Publication venue, preprint server, or submission status |
| **Year** | Publication or submission year |
| **Domain** | Research field and subfield |
| **Paper Type** | Empirical, theoretical, survey, position paper, systems paper, etc. |

A short neutral map: research question; population or system; design and unit; intervention, exposure, test, or model; comparator/reference; outcomes and timing; principal claims.

Every principal claim, explicitly:

```
Claim 1: [the claim, as the paper states it]
Evidence: [what the paper offers for it]
Needed: [what evidence would settle it]
```

Keep four things apart: what the paper claims; what its evidence demonstrates; what is plausible but untested; what a reader would expect the paper to claim but it never does.

This extraction is where the report's Context and Summary slots come from.

## Stage 2 — List what the paper does not say

Walk the background files the table above assigns — in full here, and again from the slots that name them.

Write two numbered lists, kept apart:

- **Not-stated list** (N1, N2, …): every item the report will need that the paper does not give — participants, selection, consent, variable definitions, test assumptions, denominators, calibration data, code, thresholds, and so on; a part of the paper that is absent or merged into another; a concept the report needs that the paper uses without defining. Start from stage 1's `Needed:` lines: a claim whose settling evidence the paper never supplies is an entry here.
- **Inconsistency list** (C1, C2, …): every place where two locations in the paper conflict. Check systematically: numbers across text, tables, and figures; p-values, confidence intervals, and effect sizes against each other; sample sizes throughout; percentages, averages, sums, and claimed improvements against the numbers they rest on; internal references; acronyms defined on first use; terminology; citation style. Each mismatch is one entry carrying both locations.

A **Location** is the section, then the paragraph counted from the start of that section (add the page when the section spans pages), or the algorithm line, figure, table, or equation number, or a named part of the front matter (title, author block, affiliation, abstract, keywords, identifier stamp, footnote n). Every list entry, and every point in the report, uses this convention.

Every quote, citation, statistic, and methodological detail in either list, and in the report, comes from the paper text; what the text does not say is a not-stated entry.

Write both lists into the report's appendix now, so stage 3's brief can point at them.

## Stage 3 — Judge, in the reader's frame

**Fresh context, required.** Run one subagent whose whole context is `prompts/judge.md` with its placeholders filled: the paper, the stage 1 extraction, the two stage 2 lists, the Location convention from stage 2, the background file paths, and the nine dimensions copied from the Discussion outline below. Not the conversation that wrote them. That brief is the judging contract. Edit it there, not here.

It returns the nine subsections, and they are the Discussion's only source of findings.

## Stage 4 — Assemble the report

Run this in the main context, in this order. Nothing here adds a finding, and nothing here removes one for length.

1. **Screen the return.** Drop every point whose Evidence field contains no Location, no N- or C- entry, and no numbered stage 1 claim; an unnumbered extraction field does not count, since the fact it carries has a Location of its own, and a background-file criterion may sit alongside one of those but never stands in for it. Move a point that rests on anything the paper does not state, however true, to "What this report did not check" rather than letting it stand as a finding. Discard anything returned that is not one of the nine subsections.
2. **Project stage 1 into Context and Summary.** The field table fills the Title, Authors and Venue slots; the neutral map and the claim blocks fill Problem, Method, Results and the authors' own Discussion. Go back to the paper only for a slot the extraction does not cover.
3. **Place the nine subsections** in the Discussion, in the outline's order, each keeping its verdict sentence.
4. **Write the tail.** "What this report did not check", then the appendix, with the verifier's list left empty for stage 6.

## Stage 5 — Tighten the assembled report

Run this once, in the main context, after assembly and before verification. Read every point in the Discussion and rule on it: kept, or removed for one of the reasons below. Recompute every number the report labels "derived" and correct it; stage 6 does not check those. Then remove:

- a free-standing Discussion sentence that restates the paper without carrying a judgment. The Context and Summary slots, and every point's Observation field, restate the paper by design; none of them is in scope here;
- a point whose Location and Observation repeat another point's, keeping the copy under the dimension it bears on most, never under one picked to keep a subsection from running empty, and leaving a one-line cross-reference in the other;
- a point with no Location;
- a hedge that repeats an entry in "What this report did not check".

Remove a failing point whole; a point shaved to a clause still carries its load. Then read the Discussion once against the test the judge worked under: a report that finds nothing wrong with a non-trivial paper is a failed report. If these removals have left one, the removals were wrong. Slots, verdict sentences, and appendix entries survive this stage; stage 6 still corrects one it flags.

## Stage 6 — Verify the report against the paper

After tightening and before delivery, run a second subagent whose whole context is `prompts/verify.md` with its placeholders filled: the paper, its page renders, and the report. That brief is the verification contract.

The main context removes or corrects each flagged item, or moves it to "What this report did not check". The verifier's list, with each item's disposition, goes in the appendix.

## The report

Three sections in this order, headings fixed, every slot filled or marked "not assessable from the paper" or "not checked". The report is written for a reader deciding whether to trust and use the paper; a referee's concerns — publishability, questions and revision requests to the authors — are out of scope.

### 1. Context

- **Title**: is it short and to the point? Do you know what to expect from it?
- **Authors and affiliations**: how many people were involved, and what does the order tell you? One or many institutions, which departments? Well-known places? What is their field, and what have they done before in the same area?
- **Venue**: which kind (see Source types below), and what that implies about how rigorously it was reviewed.
- **Motivation**: why is the problem important? Does the paper motivate the research, state the contribution, and give an overview of the rest of the paper?
- **Related work**: does it cover relevant prior work, synthesize it rather than list it, balance recent and foundational sources, and identify the gap accurately? Two comprehensiveness checks:
  - Tree backward: follow the paper's own reference list to the works it's built on — are those the field's recognized foundational references, or oddly idiosyncratic ones?
  - Tree forward: pick one of the paper's key cited references and check, via a citation index, whether more recent work citing that same reference is conspicuously missing — keeping in mind that research typically takes a few years to reach journal publication, so missing only the very latest work isn't necessarily a gap.
- **References check**: how many references? What kinds of sources (see Source types below), and are reviews and preprints labeled as such? What is the span, in years, of the papers cited? How many include at least one of the authors? How many are for work by people at the same institution as the authors? Are primary sources used where possible? Do cited papers support the claims attached to them? Are citation metadata and links correct? Do you recognize any of the papers? Recognition, here and in tree backward, is recall by construction: label it as recall in the slot and list it under "did not check".

With web access, search: `"[paper topic] state of the art [current year]"`, `"[key method name] comparison benchmark"`, `"[authors] previous work [topic]"`, `"[specific technique] limitations criticism"`. Read, or at least skim, the most relevant related work before stage 3.

### 2. Summary

At greater length than an abstract, in the paper's own order:

- **Problem**: research questions, hypotheses, objectives; what the authors set out to do.
- **Method**: which method family from the Method menu below, and what that choice implies about what the results can and can't show. If no family fits (a systems, tool, theory, or position paper), name the paper type from the menu's calibration table, and name the family of the paper's evaluation if it has one. For an experiment, the Summary slots in `references/experiment-design.md`; for a qualitative study, those in `references/qualitative-methods.md`; otherwise, the methods, techniques, or process followed.
- **Results**: big picture to details; how the data was analyzed; descriptive statistics, tables, charts, then inferential statistics (`references/quantitative-results.md`).
- **Discussion**: how the results should be interpreted, according to the authors, and why they think they got them; the implications of the research and how it advances knowledge in the field; practical value; the limitations they state; future research they discuss and what they plan next; whether the conclusion summarizes methods, results, discussion, and reiterates significance; whether there is an acknowledgement section for people who helped but did not make a significant contribution, plus funding.

### 3. Discussion

Nine subsections, in this order. Each subsection opens with its one-sentence verdict, then its points, each point carrying the four fields from the judge brief. The questions below are prompts, not a form: answer those that bear on the paper, in whatever order the evidence suggests.

- **Importance** — Is the problem being studied important? How significant is the contribution? What are the big ideas of this paper? Does the question match the claimed contribution? Judge the paper against its own question; a mismatch with some other question counts only when it undermines the stated contribution.
- **Credibility** — Do you trust the methods that were used? How likely is it that the conclusions are correct? Affiliation and seniority carry no weight; the venue's review rigor carries some, and every check below runs regardless. The checks: validity threats and reporting red flags in `references/experiment-design.md`; the assessment order, claim–evidence mismatches and analysis biases in `references/quantitative-results.md`; trustworthiness and the self-audit in `references/qualitative-methods.md` for a qualitative study; questionable practices in `references/research-integrity.md`; demand characteristics in `references/participants.md`.
- **Novelty** — Is there a use of novel approaches? Are these obvious? Are these clever? Is there new information to be learned from the paper? What is genuinely new vs. incremental improvement? A novelty claim broader than the search or the cited literature supports is a claim–evidence mismatch.
- **Applicability** — What are the practical applications of the work presented in the paper? Can you apply the information to your own projects? Do you think other researchers or practitioners may be able to apply the information?
- **Generalizability** — Do the results apply only to the situation presented in the paper, or to a wider set of circumstances? External validity questions in `references/experiment-design.md`; for a qualitative study, case selection and claimed reach in `references/qualitative-methods.md`.
- **Scalability** — Will the work presented scale well? Will it be relevant if applied at a larger or smaller scale? Are computational costs discussed? Every scale the paper claims is checked against a rate computed from the figures the paper gives, and the computation is shown and labeled "derived". Where the paper states no multiplier, take one from elsewhere in the paper, name what you took and from where; a claimed scale with no in-paper figure to build a rate from reads as unsupported, and says so.
- **Assumptions** — What assumptions do the authors make? Are these realistic? Are scope and assumptions explicit? Every premise the method depends on carries the Location of the step, line, equation, or condition that depends on it, and says whether the paper states it; walk the method's steps to find them rather than reading the premises off its prose. Statistical-test assumptions in `references/quantitative-results.md`; the counterfactual, design checks, and variable definitions in `references/experiment-design.md`.
- **Readability** — How difficult was it to understand? Were individual sentences and paragraphs well-written? Was the paper well-structured, did it flow well, was it logically organized? Was it culturally neutral? Did it use words you'd only find in the GRE verbal section? Are definitions and notation clear? Is the tone precise and scholarly? Readability moves no other verdict.
- **Ethics** — Is the work a good idea? Could it lead to potentially harmful outcomes? Are the authors aware of potentially negative consequences? The integrity questions in `references/research-integrity.md`; when people took part, the questions in `references/participants.md`.

### What this report did not check

Required, even when empty. One line each for: web-dependent slots skipped; parts of the paper not read or not readable (appendices, supplements, code); proofs or analyses not followed in detail; any statement in the report that rests on recall rather than the paper, quarantined here rather than presented as a finding.

### Appendix: not-stated list, inconsistency list, return accounting, verifier list

The two stage 2 lists, numbered, so the Discussion's evidence can cite N- and C- entries; the stage 4 return accounting (points returned, points dropped for missing evidence, duplicate groups stage 5 collapsed); the stage 6 verifier's list with each item's disposition. Those three and no further commentary.

## Source types

### By currency and review rigor

- Books — summarize research from the start of the field up to roughly 13 years before publication; useful for foundational grounding, but less rigorously peer-reviewed than journals
- Review articles and edited-book chapters — typically within 5-8 years of current research; still not always peer-reviewed as rigorously as journal articles
- Journal articles — the primary sources; the most current formal source; top journals accept as few as 10-20% of submissions after peer review
- Proceedings — peer-reviewed, but usually shorter and less rigorously reviewed than a journal article; timely
- Technical reports — more procedural detail than a journal article, but usually not peer-reviewed
- Electronic, preprint, or web sources — no mandatory quality control; check the author's credentials and corroborate before trusting

### Predatory venue check

If the venue is unfamiliar, check whether it is indexed (Scopus, Web of Science, PubMed, DOAJ) and a COPE member before weighing its review rigor. Think. Check. Submit. (thinkchecksubmit.org) is the field's checklist.

### Red flags in the paper's sourcing and context

- Cherry-picked citations
- A single study in isolation, with no replication
- Contradicts the preponderance of evidence
- Press release before peer review

## Method menu

### The menu

- **Experimental method** (quantitative) — random assignment supports a causal claim; every other route to one is ranked in `references/experiment-design.md`.
- **Correlational observation** (quantitative) — shows association, not cause.
- **Surveys** (quantitative) — self-report only, no direct observation.
- **Archival research** (quantitative) — relationships between variables, not causes; the records may be unreliable. Meta-analyses and systematic reviews (most widely via PRISMA) are archival research over publications.
- **Qualitative designs** — inductive studies, ethnographies, naturalistic observation, case histories; the traditions, and what each should report, in `references/qualitative-methods.md`.

### Sampling

- **Probability** (random, stratified, cluster, multistage) — needed for population inference.
- **Non-probability** (convenience, snowball, purposive, quota) — fine for exploratory or qualitative work; the results should not be generalized beyond the sample.
- The sampling frame and any selection bias should be documented.

### Calibrate to the paper type

| Paper Type | Focus Areas |
|------------|-------------|
| **Empirical** | Experimental design, baselines, statistical significance, ablations, reproducibility |
| **Theoretical** | Proof correctness, assumption reasonableness, tightness of bounds, connection to practice |
| **Survey** | Comprehensiveness, taxonomy quality, coverage of recent work, synthesis insights |
| **Systems** | Architecture decisions, scalability evidence, real-world deployment, engineering contributions |
| **Position** | Argument coherence, evidence for claims, impact potential, fairness of characterizations |

Hold each paper to its own type's bar: a method to its stated claim rather than to state-of-the-art gains; self-contained theory to its proofs rather than to experiments; a replication to fidelity rather than novelty; a negative-results paper to its design rather than its direction; statistical testing only where the design supports it.
