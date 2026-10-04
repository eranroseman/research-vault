---
name: paper-critical-analysis
description: Critical analysis of one research paper, for a reader deciding whether to trust and use it rather than an editor deciding whether to publish it; writes a report plus an evidence file.
disable-model-invocation: true
---

# Critiquing a paper

The report is the one the critical-analysis guide asks a human to write: context, summary, and a discussion of importance, credibility, novelty, applicability, generalizability, scalability, assumptions, readability and ethics. The process is built around the failures agents actually show — satisficing instead of exhaustive checking, anchoring on the authors' framing, recall presented as evidence, padding kept by its own author, locator slips — so it reads the paper once, into the evidence file, and spends its depth on checking. One depth, no fast or deep mode; on a 33-page paper expect about 8M fresh tokens and about 2 hours.

## Input and output

Input: one paper, named by the first argument. The optional second argument names the output folder; the default is `critical-analysis-<paper-slug>/` beside the paper, where `<paper-slug>` is the lowercased name the paper is known by (its system name, or the first distinctive title word). You need the full text: given only an abstract, citation, or DOI, obtain it first or stop and say so.

The run writes four things into the output folder:

- `critical-analysis-<paper-slug>.md` — the report, in `templates/report-template.md`'s outline.
- `critical-analysis-<paper-slug>.evidence.md` — the audit trail, in `templates/evidence-template.md`'s sections, each filled during the stage that produces it.
- `critical-analysis-<paper-slug>.draft.md` — the report as it stood before stage 5.
- `<paper-slug>-work/` — fetched sources, page images, scripts, and data downloaded for recomputation. Raw participant-level data is deleted from it at the end of the run.

Eight stages, 0–7, every one on every paper. Each ends on a completion bar, recorded in the evidence file's stage log as it is met.

## Rules

- **Provenance.** The reader must be able to tell apart what the paper says, what an outside source says, and what the writer infers. The `Key:` line in `templates/report-template.md`, which every report carries verbatim, states the marks.
- **Nothing silent.** Write `none found; checked: <where>`, `not checked: <reason>` or `not applicable: <reason>` rather than leaving a gap; a section whose stage has not run yet reads `pending: stage <n>`.
- **Integrity.** Concerns are neutral observations, given with their benign explanations; never accusations.
- **Write scope.** Every file the run creates, scratch work included, goes in the output folder.
- **Quotes.** Short ones only; never reproduce passages.

## Locators

A locator is a section, page, figure, table, equation, footnote or reference number, exactly as the paper numbers it: `Section 4.2`, `p. 7`, `Figure 3`, `Table 2`, `Equation 5`, `footnote 4`, `reference [23]`. A named part of the front matter — title, abstract, author block, keywords — is a locator too. `whole paper` marks something absent throughout. No paragraph counting.

## What the paper loads

Each row sets both the file stage 2 walks and the path stage 3's brief hands the judge, so a row that does not fire puts its file out of the judge's reach too.

| Condition                                                                                          | File                                 |
| -------------------------------------------------------------------------------------------------- | ------------------------------------ |
| Every paper                                                                                        | `references/sources-and-venues.md`   |
| Every paper                                                                                        | `references/research-integrity.md`   |
| The paper reports a quantity it measured, or a statistic it computed from data                     | `references/quantitative-methods.md` |
| The paper collects or analyses qualitative data — interviews, field notes, documents, cases, media | `references/qualitative-methods.md`  |
| People took part in the research                                                                   | `references/participants.md`         |
| The paper releases code or data                                                                    | `references/released-artifacts.md`   |

## Stage 0 — Settle conditions

If the output folder already holds an evidence file, the run is a resume: start at the first stage its stage log does not mark met. Otherwise create the output folder, the scratch folder, and the evidence file from `templates/evidence-template.md` (everything below its first thematic break) first. Then settle every row of the table below before reading, and record each under Conditions in the evidence file; a condition discovered mid-run costs a stage its work. Save every fetched source to the scratch folder as it arrives.

| Condition                           | What it changes                                                                                                                                                                                                                         |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| What counts as the paper            | The body, appendices and supplements, plus any supplied file the paper names as holding its content (for example a taxonomy in the repository it cites). Any other supplied file is an outside source, entering only through W entries. |
| The Read tool cannot render the PDF | Extract text with PyMuPDF, pypdf or pdftotext, and render every page carrying a figure, table or equation to an image in the scratch folder. With no tool available, stop and ask for the text.                                         |
| Web access                          | Probe by fetching one known-good record, such as the Crossref entry for a DOI the paper cites; retry once on a network error. If the probe fails or is refused, stop and report why — the skill does not run without the web.           |
| Released code or data               | Load `references/released-artifacts.md`; stage 2 checks them.                                                                                                                                                                           |
| The paper runs past 100 pages       | Read in chunks, writing the evidence file after each chunk.                                                                                                                                                                             |

**Done when:** every row is settled and recorded, and the probe passed.

## Stage 1 — Read into the evidence file

Read everything stage 0 counted as the paper, once and in full, viewing every figure and table as an image. The evidence file is the working memory — fill it as you go rather than holding the paper in context: identity (confirmed against the request; wrong paper: stop and say what you have) and section map; promises 1–5; every principal claim with its `Needed:` line; key quotes and numbers with their locators; terms you had to look up, which stage 2 settles as W entries. Under Identity, record the paper type, the method family (classified from the method menu below), and the paths of the background files the load table assigns.

**Done when:** every page has been read once and every figure and table viewed as an image; the identity is confirmed against the request; the section map and promises 1–5 are filled; every principal claim carries a `Needed:` line; and the paper type, method family and assigned background files are recorded.

## Stage 2 — Check exhaustively

The deepest findings come only from exhaustive reconciliation and artifact checks; depth here is the point, not a cost to manage. Do all arithmetic in code, reconciliations and recomputations alike.

- **N list:** every item the report will need that the paper does not give. Start from the `Needed:` lines, then walk the assigned background files.
- **C list:** every place two locations in the paper conflict. Reconcile every reported result in the abstract and text — statistic, count, percentage, effect size — against the tables, figures and supplements, and every percentage, sum and effect size against the numbers it rests on. Keep the reconciliation log in the evidence file.
- **W list:** one entry per outside check, in the entry shape the evidence file's External-check list gives. The checks:
  - venue rigor and the authors' previous work (`references/sources-and-venues.md`);
  - reference counts, tree backward and tree forward;
  - 3–5 related works, read in full where openly available and as abstracts otherwise: the work the paper builds on most; the primary source behind its load-bearing outside claim; its closest prior or concurrent work that it does not cite; any other work the argument depends on;
  - every concept the paper uses without defining;
  - if code or data are released, the analysis code behind each headline number — every number in the abstract and conclusion — with those numbers recomputed from the released data (`references/released-artifacts.md`).

When a citation index fails, fall back in order: OpenAlex, Crossref, OpenCitations, Semantic Scholar. Each failure becomes a W entry, and any count left incomplete is labelled partial. Record each mandated check above in its slot in the evidence file's External-check list.

**Done when:** every `Needed:` line is resolved to an entry or to evidence; every number is reconciled or entered in C; every question in section 1 (Context) of `templates/report-template.md` is answered or marked `not checked: <reason>`; every mandated-check slot is filled; every released artifact relevant to a headline number has been examined.

## Stage 3 — Judge

**Fresh context, required.** Run one subagent whose whole context is `prompts/judge.md` with its placeholders filled: the paper and its supplements, the page images, the evidence file, the Locators section above (verbatim), and the background file paths the load table assigns. Judgment in a fresh context, bound to citable evidence, is better calibrated than judgment in the context that read the paper.

It returns the nine subsections and a Recalled section. The nine, in order: Importance, Credibility, Novelty, Applicability, Generalizability, Scalability, Assumptions, Readability and Ethics. Screen the return: drop any point whose Evidence field cites nothing admissible (the brief defines admissible), log the dropped count, assign J IDs to the kept points, and record them with the Recalled lines under Judge points in the evidence file. The Recalled lines surface later as Coverage's `Recalled:` entries, never as findings.

**Done when:** all nine subsections and the Recalled section are returned, and every kept point carries admissible evidence under a J ID.

## Stage 4 — Write

Write the report in `templates/report-template.md`'s outline, starting from below its first thematic break. Build Context and Summary from the evidence file, going back to the paper only for a slot it does not cover. Write the critical discussion in prose: the Verdicts block first, then the nine topics, placing every J point, tagged with its J ID, under the topic it bears on most; points may merge into paragraphs as long as each keeps its locators and IDs. Then write Coverage, with `Verification: pending: stage 7`; every N, C, W or J ID the report's body does not cite goes on Coverage's `Evidence file only:` line — the checker closes that ledger. There is no length limit at this stage. Save the result as the report, and copy it to the draft path — the draft is what stage 5 is measured against.

**Done when:** every J point is in the report, every heading in `templates/report-template.md` is filled, and the draft is saved.

## Stage 5 — Edit

**Fresh context, required** — an author reviewing its own text keeps everything. Run one subagent whose whole context is `prompts/edit.md` with its placeholders filled: the report and the evidence file, which it reads only. It returns a change list; apply or reject each item yourself, recording every disposition with its reason, and the before-and-after word counts, under Pruning record in the evidence file. Its Flags section (uncited generalizations, numbers that do not add up) is yours to settle too: fix each flag or move it to Coverage's `For the reader to double-check:` line. Apply only items that hold the brief's invariant.

**Done when:** every change-list item is applied or rejected with a reason, every flag is fixed or on Coverage's `For the reader to double-check:` line, and the before-and-after word counts are logged.

## Stage 6 — Check

Run `python3 scripts/check_report.py <report>` — the path is relative to this skill's directory; the checker finds the evidence file beside the report. The templates are its single source of truth: it reads required headings from `templates/report-template.md` and `templates/evidence-template.md`, and each error it prints names the file and the rule broken. Fix the file each error names; the checker stays as it is. Settle each warning too: a bare `none found`, `not checked` or `not applicable` gets the where or why the Nothing silent rule asks for, and an unqualified "significant" reads "statistically significant" wherever it reports a test result.

**Done when:** the checker reports no errors, and every warning it prints is settled as above.

## Stage 7 — Verify

**Fresh context, required** — a verifier holding the reasoning behind a locator is no longer checking it. Run one subagent whose whole context is `prompts/verify.md` with its placeholders filled: the paper and its supplements, the page images, the report, the evidence file, and the Locators section above (verbatim). It runs the brief's checks and returns failures only, with the counts checked.

Fix, drop, or move each returned item to Coverage; record the dispositions under Verifier list in the evidence file; update Coverage's `Verification:` line with the counts; run the checker again. Then delete raw participant-level data from the scratch folder and record what was deleted under Deletions.

**Done when:** every verifier item has a disposition, the checker is clean, and the deletion is recorded.

## Method menu

- **Experimental method** (quantitative) — random assignment supports a causal claim; every other route to one is ranked in `references/quantitative-methods.md`.
- **Correlational observation** (quantitative) — shows association, not cause.
- **Surveys** (quantitative) — self-report only, no direct observation.
- **Archival research** (quantitative) — relationships between variables, not causes; the records may be unreliable. Meta-analyses and systematic reviews (most widely via PRISMA) are archival research over publications.
- **Qualitative designs** — inductive studies, ethnographies, naturalistic observation, case histories; the traditions, and what each should report, in `references/qualitative-methods.md`.

A paper fitting no family is classified by its paper type — empirical, theoretical, survey, systems, position, replication, or negative results — and the family of its evaluation, if it has one, is named.
