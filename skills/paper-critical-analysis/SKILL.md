---
name: paper-critical-analysis
description: In-depth critical analysis report of one research paper (context, summary, nine-dimension discussion), with a fresh-context judgment pass and a verifier pass.
disable-model-invocation: true
---

# Critiquing a paper

Thoroughness is the constraint here, token cost is not.

## Input and output

Input: one paper. Read the whole thing. **PDF**: use the Read tool with the `pages` parameter for large documents. If the Read tool cannot render the PDF, extract the text with a local tool (pypdf, PyMuPDF, or pdftotext) and render the pages that carry figures or pseudocode to images; if no tool is available, ask for the text.

Output: one markdown file in the outline under "The report", written beside the input unless told otherwise; the tightening pass in stage 4 controls its length, not a ceiling. Ask up front whether web access is allowed: three Context slots depend on it. In a non-interactive run, take the answer from the request; absent one, treat it as no. Without it, the report names what its absence cost.

## Stage 1 — Extract, in the authors' frame

A part that is absent or merged is itself a stage 2 entry.

No judgment yet. Record:

| Field | Description |
|-------|-------------|
| **Title** | Full paper title |
| **Authors** | Author list and affiliations |
| **Venue / Status** | Publication venue, preprint server, or submission status |
| **Year** | Publication or submission year |
| **Domain** | Research field and subfield |
| **Paper Type** | Empirical, theoretical, survey, position paper, systems paper, etc. |

Create a short neutral map: research question; population or system; design and unit; intervention, exposure, test, or model; comparator/reference; outcomes and timing; principal claims. Do not write an assessment. Identify what evidence would be needed to evaluate each claim.

List the paper's main claims explicitly:

```
Claim 1: [Specific claim about contribution or finding]
Evidence: [What evidence supports this claim in the paper]
```

Separate: what the paper explicitly claims; what the evidence demonstrates; what remains plausible but untested; what was expected of the paper but never claimed. Do not penalize a paper for failing to answer a different research question unless the mismatch undermines its stated contribution.

**Long papers.** If the paper exceeds 30 pages including appendices and supplements, this stage runs one subagent per section, each returning these fields for its section; stage 2 runs in the main context over the merged extraction.

## Stage 2 — List what the paper does not say

Walk the background files that apply, and write two numbered lists, kept apart:

- **Not-stated list** (N1, N2, …): every item the report will need that the paper does not give (participants, selection, consent, variable definitions, test assumptions, denominators, calibration data, code, thresholds, and so on).
- **Inconsistency list** (C1, C2, …): every place where two locations in the paper conflict.

Concepts the report needs that the paper uses without defining go on the not-stated list too; with web access, look them up before stage 3, and say in the report that you did.

Run the consistency checks here, systematically: numbers across text, tables, and figures; statistical consistency (do p-values, confidence intervals, and effect sizes align? are sample sizes consistent throughout?); calculations (verify percentages, averages, sums; check that reported improvements match the actual numbers); internal references; acronyms defined on first use; terminology consistency; citations (is citation style uniform? whether they exist is a web check: without web access, "not checked"). Each mismatch goes on the inconsistency list with both locations.

Ground every claim in the paper text. Do not invent quotes, citations, statistics, or methodological details that are not present. If something is unclear or missing from the text, say so explicitly — that itself is a reviewable issue.

The two lists go in the report's appendix.

Background files, walked here and reached again from the slots that name them:

- The source types and the method menu at the end of this file — every paper.
- `references/experiment-design.md` and `references/quantitative-results.md` — a paper with an experiment, a measurement, or a statistical analysis.
- `references/qualitative-methods.md` — a qualitative or mixed-methods paper.
- `references/research-integrity.md` — every paper.
- `references/participants.md` — a paper in which people took part.

When no method family fits, walk all six.

## Stage 3 — Judge, in the reader's frame

Only now. Each of the nine dimensions gets a verdict with evidence. The verdict is one sentence, no scale and no fixed labels: what a reader should make of the paper on that dimension. A dimension that does not apply gets the sentence "not assessable from the paper" and the reason. A dimension with applicable and inapplicable parts gets a verdict on the applicable parts, with the rest named as inapplicable inside the subsection.

Evidence for a verdict is a location in the paper or a numbered entry from the appendix lists (N- or C-). Nothing else counts. Each substantive point carries **Location**, **Observation**, **Evidence or criterion**, **Why it matters**. A Location is the section, then the paragraph counted from the start of that section (add the page when the section spans pages), or the algorithm line, figure, table, or equation number. Stage 2 entries use the same convention.

**Fresh context, required.** Run stage 3 in a subagent given only the paper, the stage 1 extraction, the two stage 2 lists, this stage's four-field rule, the Discussion outline below (the nine dimensions and the Principles; not the did-not-check section), and the paths of the background files its subsections name, not the conversation that wrote them. The subagent returns the nine subsections. The main context assembles the report and may downgrade or de-duplicate the subagent's findings; it may not invent a new blocker. A report that finds nothing wrong with a non-trivial paper is a failed report.

## Stage 4 — Tighten the assembled report

Once, in the main context, after the report is assembled and before it is verified. Read it top to bottom and remove:

- a sentence that restates the paper without filling a slot or carrying a judgment;
- a point whose Location and Observation repeat another point's, keeping the copy under the dimension it bears on most and leaving a one-line cross-reference in the other;
- a point with no Location;
- a hedge that repeats an entry in "What this report did not check".

Never remove a slot, a verdict sentence, or an appendix entry.

## Stage 5 — Verify the report against the paper

After tightening and before delivery, a second subagent receives only the paper (its text and any page renders used for figures or pseudocode) and the report. It checks every **Location** field in the body and in the appendix lists, every quoted passage, and every number the report attributes to the paper against the paper (a number the report derives is labeled "derived" in the report and is outside the verifier's scope), and returns a list of items it could not find or that read differently in the paper, each with the report line and the paper location it checked. It does not rewrite the report and it forms no opinion of the paper. The main context removes or corrects each flagged item, or moves it to "What this report did not check". The verifier's list, with each item's disposition, is appended to the report's appendix.

## The report

Three sections in this order, headings fixed, every slot filled or marked "not assessable from the paper" or "not checked". The report is written for a reader deciding whether to trust and use the paper, not for an editor deciding whether to publish it: no accept/reject verdict, no questions for the authors, no revision requests.

### 1. Context

- **Title**: is it short and to the point? Do you know what to expect from it?
- **Authors and affiliations**: how many people were involved, and what does the order tell you? One or many institutions, which departments? Well-known places? Keep in mind the authors could be students; evaluate the merits regardless of affiliation. What is their field, and what have they done before in the same area?
- **Venue**: conference, journal, workshop, technical report, or preprint (see Source types below), and what that implies about how rigorously it was reviewed.
- **Motivation**: why is the problem important? Does the paper motivate the research, state the contribution, and give an overview of the rest of the paper?
- **Related work**: does it cover related work, discuss relevant related research, and establish a gap? Two comprehensiveness checks:
  - Tree backward: follow the paper's own reference list to the works it's built on — are those the field's recognized foundational references, or oddly idiosyncratic ones?
  - Tree forward: pick one of the paper's key cited references and check, via a citation index, whether more recent work citing that same reference is conspicuously missing — keeping in mind that research typically takes a few years to reach journal publication, so missing only the very latest work isn't necessarily a gap.
- **References check**: how many references? What kinds of sources (see Source types below)? How many include at least one of the authors? How many are for work by people at the same institution as the authors? Do you recognize any of the papers? What is the span, in years, of the papers cited? Recognition, here and in tree backward, is recall by construction: label it as recall in the slot and list it under "did not check".

With web access, search: `"[paper topic] state of the art [current year]"`, `"[key method name] comparison benchmark"`, `"[authors] previous work [topic]"`, `"[specific technique] limitations criticism"`. Read, or at least skim, the most relevant related work before stage 3. Without web access, the author-background, tree-forward and same-institution-count slots read "not checked: no web access".

### 2. Summary

At greater length than an abstract, in the paper's own order:

- **Problem**: research questions, hypotheses, objectives; what the authors set out to do.
- **Method**: which method family from the Method menu below, and what that choice implies about what the results can and can't show. If no family fits (a systems, tool, theory, or position paper), name the paper type from the menu's calibration table, and name the family of the paper's evaluation if it has one. For an experiment, the Summary slots in `references/experiment-design.md`; for a qualitative study, those in `references/qualitative-methods.md`; otherwise, the methods, techniques, or process followed.
- **Results**: big picture to details; how the data was analyzed; descriptive statistics, tables, charts, then inferential statistics (`references/quantitative-results.md`).
- **Discussion**: how the results should be interpreted, according to the authors, and why they think they got them; the implications of the research and how it advances knowledge in the field; practical value; the limitations they state; future research they discuss and what they plan next; whether the conclusion summarizes methods, results, discussion, and reiterates significance; whether there is an acknowledgement section for people who helped but did not make a significant contribution, plus funding.

### 3. Discussion

Nine subsections, in this order. Each subsection opens with its one-sentence verdict, then its points, each point carrying the four fields from stage 3. The questions below are prompts, not a form: answer those that bear on the paper, in whatever order the evidence suggests.

- **Importance** — Is the problem being studied important? How significant is the contribution? What are the big ideas of this paper? Does the question match the claimed contribution?
- **Credibility** — Do you trust the methods that were used? How likely is it that the conclusions are correct? Don't let the authors' affiliation alone earn your trust. Weigh the venue's review rigor into how much you trust the paper, but a rigorous venue doesn't excuse skipping the other checks. The checks: validity threats and reporting red flags in `references/experiment-design.md`; the assessment order, claim–evidence mismatches and analysis biases in `references/quantitative-results.md`; validation of findings in `references/qualitative-methods.md` for a qualitative study; questionable practices in `references/research-integrity.md`; demand characteristics in `references/participants.md`.
- **Novelty** — Is there a use of novel approaches? Are these obvious? Are these clever? Is there new information to be learned from the paper? Is it incremental work, or something very different from what has been done? What is genuinely new vs. incremental improvement?
- **Applicability** — What are the practical applications of the work presented in the paper? Can you apply the information to your own projects? Do you think other researchers or practitioners may be able to apply the information?
- **Generalizability** — Do the results apply only to the situation presented in the paper, or to a wider set of circumstances? External validity questions in `references/experiment-design.md`; for a qualitative study, case selection and claimed reach in `references/qualitative-methods.md`.
- **Scalability** — Will the work presented scale well? Will it be relevant if applied at a larger or smaller scale? Are computational costs discussed?
- **Assumptions** — What assumptions do the authors make? Are these realistic? Are scope and assumptions explicit? Statistical-test assumptions in `references/quantitative-results.md`; design assumptions and variable definitions in `references/experiment-design.md`.
- **Readability** — How difficult was it to understand? Were individual sentences and paragraphs well-written? Was the paper well-structured, did it flow well, was it logically organized? Was it culturally neutral? Did it use words you'd only find in the GRE verbal section? Are definitions and notation clear? Is the tone precise and scholarly? Readability moves no other verdict.
- **Ethics** — Is the work a good idea? Could it lead to potentially harmful outcomes? Are the authors aware of potentially negative consequences? The integrity questions in `references/research-integrity.md`; when people took part, the questions in `references/participants.md`.

### What this report did not check

Required, even when empty. One line each for: web-dependent slots skipped; parts of the paper not read or not readable (appendices, supplements, code); proofs or analyses not followed in detail; any statement in the report that rests on recall rather than the paper, quarantined here rather than presented as a finding.

### Appendix: not-stated list, inconsistency list, verifier list

The two stage 2 lists, numbered, so the Discussion's evidence can cite N- and C- entries; then the stage 5 verifier's list with each item's disposition. Stage 1's extraction is not reproduced.

## Source types

### Source types, by currency and review rigor

- Books — summarize research from the start of the field up to roughly 13 years before publication; useful for foundational grounding, but less rigorously peer-reviewed than journals
- Review articles and edited-book chapters — typically within 5-8 years of current research; still not always peer-reviewed as rigorously as journal articles
- Journal articles — the primary sources; the most current formal source; top journals accept as few as 10-20% of submissions after peer review
- Proceedings — peer-reviewed, but usually shorter and less rigorously reviewed than a journal article; timely
- Technical reports — more procedural detail than a journal article, but usually not peer-reviewed
- Electronic, preprint, or web sources — no mandatory quality control; check the author's credentials and corroborate before trusting

### Predatory venue check

If the venue is unfamiliar, check whether it is indexed (Scopus, Web of Science, PubMed, DOAJ) and a COPE member before weighing its review rigor. Think. Check. Submit. (thinkchecksubmit.org) is the field's checklist.

### Citation questions

- Do cited papers support the claims attached to them?
- Are primary sources used where possible?
- Are reviews labeled as reviews?
- Are preprints labeled as preprints?
- Are citation metadata and links correct?

### Literature and context questions

- Is relevant prior work covered?
- Does the paper synthesize rather than merely list sources?
- Are gaps accurately identified?
- Are recent and foundational sources balanced?

### Red flags in the paper's sourcing and context

Reporting red flags:

- No conflicts of interest statement
- Cherry-picked citations

Context red flags:

- Industry funding without independence
- Single study in isolation
- Contradicts preponderance of evidence
- No replication
- Published in predatory journal
- Press release before peer review

Novelty claims that are broader than the search or cited literature supports are a claim–evidence mismatch.

## Method menu

### The menu

- **Experimental method** (quantitative)
- **Correlational observation** (quantitative) — Doesn't prove causality.
- **Surveys** (quantitative) — there's no direct observation, only self-report.
- **Archival research** (quantitative) — can show relationships between variables but not causes; the records may not be reliable. Meta-analyses and systematic reviews (most widely via PRISMA) are archival research over publications.
- **Qualitative designs** — inductive studies, ethnographies, naturalistic observation, case histories.

### Hierarchy of evidence for causal claims

1. RCT (random assignment)
2. Quasi-experiment (natural treatment + control, no random assignment) — diff-in-diff, regression discontinuity, interrupted time series.
3. Instrumental variable / propensity score — observational with strong assumptions.
4. Cross-sectional regression — control for confounders.

For each, the **counterfactual** should be articulated: what would have happened to the treated group absent treatment?

### Sampling

- **Probability** (random, stratified, cluster, multistage) — needed for population inference.
- **Non-probability** (convenience, snowball, purposive, quota) — fine for exploratory or qualitative work; the results should not be generalized beyond the sample.
- The sampling frame and any selection bias should be documented.

### Qualitative traditions

| Tradition | What it asks | Data | Analysis |
|-----------|--------------|------|----------|
| **Phenomenology / IPA** | What is the lived experience of X? | In-depth interviews | Detailed interpretive coding of meaning units |
| **Grounded theory** | What theory explains this process? | Interviews + observation | Open → axial → selective coding, constant comparison |
| **Ethnography** | What is going on in this culture/setting? | Participant observation, field notes | Thick description, cultural pattern analysis |
| **Narrative inquiry** | What stories do people tell? | Life histories, narrative interviews | Structural + thematic narrative analysis |
| **Case study (qual)** | How and why does X happen here? | Multiple sources within bounded case | Within-case + cross-case analysis |
| **Thematic analysis** | What themes recur in the data? | Any qualitative data | Inductive or deductive coding (Braun & Clarke) |
| **Discourse / content analysis** | How is X talked about / represented? | Texts, transcripts, media | Coding of language patterns or content categories |

### Calibrate to the paper type

| Paper Type | Focus Areas |
|------------|-------------|
| **Empirical** | Experimental design, baselines, statistical significance, ablations, reproducibility |
| **Theoretical** | Proof correctness, assumption reasonableness, tightness of bounds, connection to practice |
| **Survey** | Comprehensiveness, taxonomy quality, coverage of recent work, synthesis insights |
| **Systems** | Architecture decisions, scalability evidence, real-world deployment, engineering contributions |
| **Position** | Argument coherence, evidence for claims, impact potential, fairness of characterizations |

Do not require SOTA gains for every method, experiments for self-contained theory, novelty for a replication, positive results for a negative-results paper, or statistical testing unsupported by the design.

## Principles

- Do NOT dismiss work based on author reputation or affiliation. Evaluate the work on its own merits.
