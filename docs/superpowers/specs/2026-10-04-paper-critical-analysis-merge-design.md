# Design: one paper-critical-analysis skill from two

Date: 2026-10-04. Status: approved in brainstorming, awaiting spec review. Branch: `paper-critical-analysis-merge`.

## Goal

Replace `skills/paper-critical-analysis/` and the now-retired `critical-analysis-report` skill with a single skill, `paper-critical-analysis`. It produces the report that `sources/How to Write a Critical Analysis of a Research Paper.md` asks a human to write: context, summary, and a discussion of importance, credibility, novelty, applicability, generalizability, scalability, assumptions, readability and ethics.

The guide was written for people, and its three reading passes exist to work around human memory. An agent fails differently, so the process here is built around the failures observed in agent runs, while the delivered result stays the guide's.

The skill balances depth against cost. It runs at one depth, with no fast or deep mode.

## Evidence behind the design

Both skills were run on Bloom (Jörke et al., CHI '26, arXiv:2510.05449v2, 33 pages with supplements, plus the authors' taxonomy and released repository). Each was run twice: once as shipped, once after minimal fixes. A 20-item answer key was written before any report existed.

| Run                         | Key score | Fresh input tokens | Wall time |
| --------------------------- | --------- | ------------------ | --------- |
| critical-analysis-report, 1 | 12        | 3.0M               | 55 min    |
| critical-analysis-report, 2 | 15        | 3.1M               | 49 min    |
| paper-critical-analysis, 1  | 17        | 19.7M              | 148 min   |
| paper-critical-analysis, 2  | 18        | 10.4M              | ~150 min  |

The design rests on six observations:

- The deepest findings came from exhaustive work:

  - reconciling every number across text, tables, figures and supplements;
  - reading the authors' released code and data.

  Examples: the headline H1 coefficient is the control arm's change, a table average is mis-scaled, and the usage claims contradict the released data. Neither skill asks for the code and data; runs did it on their own initiative, and one run that skipped it missed the top finding.

- Judgment in a fresh context, bound to citable evidence with recall set apart, was better calibrated than judgment in the context that did the reading.

- A word cap cut findings by convenience, not severity. A main-context tightening pass removed nothing (0 of 55 points).

- Paragraph-counted locators forced a custom paragraph index every run, and most verifier flags were locator or quote slips.

- Section fan-out on a 33-page paper duplicated the main context's own reading (3M tokens) for no finding the main context lacked.

- Each verifier checked only claims located in the paper. Both factual errors in one run sat in claims sourced outside it.

The run artifacts are local and git-ignored (`sources/bloom-skill-comparison/`, `sources/bloom-skill-comparison-run2/`); `comparison.md` there holds the full analysis.

## Decisions

| Question                | Decision                                                                                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Depth and cost          | One depth, balanced to the guide's intent. Target about 8M fresh tokens and about 2 hours on a paper the size of Bloom.                                                   |
| Scope in the repository | Replace both skills. Keep the name `paper-critical-analysis`, which the vault template already seeds into users' `AGENTS.md`.                                             |
| What the skill reads    | The paper, every available appendix and supplement, files the paper names as holding its content, the authors' released code and data, and 3–5 selected related works.    |
| Architecture            | Reader, judge, editor and verifier: one main context and three fresh-context subagents.                                                                                   |
| Report shape            | The guide's outline in prose. The audit trail lives in a separate evidence file.                                                                                          |
| Length                  | Write uncapped, then prune with a fresh-context editor. No word bound.                                                                                                    |
| Web access              | Required. The skill stops if the probe fails.                                                                                                                             |
| Locators                | Section, page, figure, table, equation, footnote or reference number; a named front-matter part; or `whole paper` for something absent throughout. No paragraph counting. |
| Fan-out                 | None. Very long papers are read in chunks, with notes written after each chunk.                                                                                           |

## Outputs

Each run writes into one output folder:

- `critical-analysis-<paper-slug>.md`, the report.
- `critical-analysis-<paper-slug>.evidence.md`, the evidence file.
- `critical-analysis-<paper-slug>.draft.md`, the report as it stood before editing.
- `<paper-slug>-work/`, a scratch folder holding fetched sources, page images, scripts and data downloaded for recomputation. Raw participant-level data is deleted from it at the end of the run.

### The report

It follows the guide's outline:

1. **Context:**
   - title and authors;
   - venue and its review rigor;
   - the authors' previous work;
   - motivation;
   - related work, with tree backward and tree forward;
   - reference counts.
2. **Summary:**
   - problem;
   - method, with its method family and what that family can and cannot show;
   - results;
   - the authors' discussion;
   - conclusion.
3. **Critical discussion:** the nine verdict sentences first, one line each; then the nine topics in prose, each opening with its verdict. Credibility closes with a confidence level and the evidence that would raise it.
4. **Coverage:**
   - not read;
   - not checked;
   - for the reader to double-check;
   - verification;
   - recalled knowledge, one line each;
   - findings left in the evidence file only, by ID.

Marks in the report:

- A locator means the paper says it.
- A W ID such as `(W12)` means a source outside the paper said it. The evidence file gives the source, its URL or saved copy, and what it said.
- `[inferred]` marks the writer's own reasoning.
- A computed number reads `derived` and cites the C, W or J entry that holds the computation. (J covers the judge's own computations, such as Scalability rates, which are neither in-paper conflicts nor outside sources.)
- Recalled knowledge appears only under Coverage.

### The evidence file

It is the audit trail, and each section is filled during the stage that produces it:

- identity: the version read and how it was confirmed;
- the conditions settled at stage 0, and the web probe's result;
- the stage log, so an interrupted run resumes from it;
- the section map;
- promises 1–5, quoted or located in the title, abstract, introduction or conclusion;
- claims, each with a `Needed:` line naming the evidence that would settle it;
- the not-stated list (N1…), the inconsistency list (C1…) with its reconciliation log, and the external-check list (W1…);
- the related works read, and the released-artifact checks, each as W entries;
- the judge's points under assigned IDs (J1…), and its Recalled lines;
- the pruning record: word counts before and after, and the editor's change list with each item applied or rejected;
- the verifier's list with each item's disposition;
- the participant data deleted at the end.

## Process

Each stage exists to counter an agent failure seen in the runs. Each ends on a completion bar that can be checked.

| Stage                          | Who               | Failure it counters                                                                                                                       |
| ------------------------------ | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 0. Settle conditions           | main              | Mid-run environment surprises: unrenderable PDFs, blocked or rate-limited services, interrupted sessions losing in-session results        |
| 1. Read into the evidence file | main              | Context used as working memory grows costly and lossy; figures are invisible as text                                                      |
| 2. Check exhaustively          | main              | Satisficing: depth varied by run, and the deepest findings came only from exhaustive reconciliation and artifact checks; model arithmetic |
| 3. Judge                       | fresh subagent    | Anchoring on the authors' framing; recall presented as evidence; poor calibration                                                         |
| 4. Write                       | main              | (assembly)                                                                                                                                |
| 5. Edit                        | fresh subagent    | Restatement and padding by default; an author reviewing its own text keeps everything                                                     |
| 6. Check                       | `check_report.py` | Rules held only in prose decay                                                                                                            |
| 7. Verify                      | fresh subagent    | Locator and quote slips, wrong outside claims, meaning drift introduced by editing                                                        |

### Stage 0: settle conditions

Settle every row before reading, and record each in the evidence file.

| Condition                           | What it changes                                                                                                                                                                                                                         |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| What counts as the paper            | The body, appendices and supplements, plus any supplied file the paper names as holding its content (for example a taxonomy in the repository it cites). Any other supplied file is an outside source, entering only through W entries. |
| The Read tool cannot render the PDF | Extract text with PyMuPDF, pypdf or pdftotext, and render every page carrying a figure, table or equation to an image. With no tool available, stop and ask for the text.                                                               |
| Web access                          | Probe by fetching one known-good record, such as the Crossref entry for a DOI the paper cites; retry once on a network error. If the probe fails or is refused, stop and report why.                                                    |
| Released code or data               | Load `references/released-artifacts.md`; stage 2 checks them.                                                                                                                                                                           |
| The paper runs past 100 pages       | Read in chunks and write the evidence file after each chunk.                                                                                                                                                                            |

Every fetched source is saved to the scratch folder as it arrives.

**Done when:** every row is settled and recorded, and the probe passed.

### Stage 1: read into the evidence file

Read everything stage 0 counted as the paper, once and in full. View every figure and table as an image.

Fill the evidence file as you go:

- identity and section map;
- promises 1–5;
- claims, each with its `Needed:` line;
- key quotes and numbers with their locators;
- terms you had to look up.

Classify the method family from the method menu in SKILL.md, and record which background files the load table assigns.

**Done when:** every page has been read once, the identity is confirmed against the request, and every principal claim carries a `Needed:` line.

### Stage 2: check exhaustively

- **N list:** every item the report will need that the paper does not give. Start from the `Needed:` lines, then walk the assigned background files.
- **C list:** every place two locations in the paper conflict. Reconcile every reported result in the abstract and text (statistic, count, percentage, effect size) against the tables, figures and supplements, and every percentage, sum and effect size against the numbers it rests on. Do arithmetic in code, and keep the reconciliation log in the evidence file.
- **W list:** one entry per outside check, each holding the claim checked, the source, its URL and saved copy, and what the source said. The checks are:
  - venue rigor and the authors' previous work;
  - reference counts, tree backward and tree forward;
  - 3–5 related works, read in full where openly available and as abstracts otherwise:
    - the work the paper builds on most;
    - the primary source behind its load-bearing outside claim;
    - its closest prior or concurrent work that it does not cite;
    - any other work the argument depends on;
  - every concept the paper uses without defining;
  - if code or data are released, the analysis code behind each headline number (every number in the abstract and conclusion), with those numbers recomputed from the released data.
  - When a citation index fails, fall back in order: OpenAlex, Crossref, OpenCitations, Semantic Scholar. Each failure becomes a W entry, and any count left incomplete is labelled partial.

**Done when:**

- every `Needed:` line is resolved to an entry or to evidence;
- every number is reconciled or entered in C;
- every Context question is answered or marked `not checked: <reason>`;
- every released artifact relevant to a headline number has been examined.

### Stage 3: judge

A fresh-context subagent receives `prompts/judge.md` with these filled in:

- the paper and its supplements;
- the page images;
- the evidence file;
- the locator convention;
- the background files assigned by the load table.

It returns, for each of the nine topics in order, a verdict sentence of about 30 words making a single claim, followed by its points. It closes with a Recalled section. Each point carries five fields:

- **Kind:** one of five kinds: not reported; potential design or analysis problem; demonstrated inconsistency; external contradiction; integrity concern.
- **Locator.**
- **Observation:** one sentence.
- **Evidence:** locators or N, C, W or claim IDs. A background criterion may ride alongside but never stands alone.
- **Why it matters:** one sentence.

The bar a paper is judged against depends on its type: empirical, theoretical, survey, systems, position, replication or negative results. Recalled knowledge goes only in the Recalled section.

The main context drops any point whose Evidence field cites nothing admissible, logs the count, and assigns J IDs.

**Done when:** all nine topics and the Recalled section are returned, and every point that is kept carries admissible evidence.

### Stage 4: write

Build Context and Summary from the evidence file. Write the critical discussion in prose, placing every J point under the topic it bears on most; points may merge into paragraphs as long as each keeps its locators and IDs. Then write Coverage. There is no length limit at this stage.

Save the result as the draft.

**Done when:** every J point is in the report, and every heading in the outline is filled.

### Stage 5: edit

A fresh-context subagent receives `prompts/edit.md`, the report and the evidence file, which it reads only.

It works for one reader: someone deciding whether to trust and use the paper. Its stages follow the Professional Editorial Standards 2024 (structural, stylistic, copy), paraphrased in the brief:

- **Structural:**
  - Delete repetitive, irrelevant and superfluous sentences.
  - Keep each meaning in one place, under the topic it bears on most, with a cross-reference where needed.
  - Move detail behind its ID into the evidence file. Derivations, number lists and source quotes go there; the claim stays in the report.
  - Recast number-heavy text as a table.
  - Put the most relevant material first.
- **Stylistic:**
  - Tighten passing sentences: omit needless words, prefer active and positive forms, use concrete language.
  - Remove AI-writing patterns: puffery, empty "-ing" phrases, promotional adjectives, stock vocabulary, scattered bold.
- **Copy:**
  - Make terms, numbers and abbreviations consistent.
  - Flag, without fixing, any generalization that has no citation and any number that does not add up.

The invariant is that every change keeps the claim and its strength, its qualifiers, numbers, locators, IDs and provenance marks. A sentence that fails the relevance or no-op test is deleted whole, never trimmed. The structural and stylistic passes work on the report's sections 1–3 only; the front matter, the Verdicts block and Coverage take the copy pass alone — their repetitions and fixed leads are the outline's, not the writer's.

The editor returns a change list instead of editing the file. Each item gives the text before and after, and the test applied. The main context applies or rejects each item and records why.

**Done when:** every change-list item is applied or rejected with a reason, and the before-and-after word counts are logged.

### Stage 6: check

Run `python3 skills/paper-critical-analysis/scripts/check_report.py <report>`. It reads the report and its evidence file and fails on any of:

- a missing outline heading;
- a section holding nothing but the template's own text;
- a leftover template placeholder;
- the template preamble left in place;
- a topic with no locator or ID;
- a Credibility section that states no confidence;
- a missing Coverage line;
- an unfilled Coverage line or mandated-check slot, or a slot citing an undefined ID;
- a `derived` number with no C, W or J ID in its sentence;
- a missing provenance key;
- a broken ledger: an N, C, W or J ID that appears neither in the report nor on Coverage's "evidence file only" line;
- a missing evidence file.

The template headings are the checker's single source of truth: the checker reads them from `templates/report-template.md`.

**Done when:** the checker reports no errors.

### Stage 7: verify

A fresh-context subagent receives `prompts/verify.md`, the paper and its supplements, the page images, the report, and the evidence file. It checks three things:

- every locator, quote and number the report attributes to the paper;
- every W entry the report cites, re-opened at its URL or saved copy;
- every applied change-list item, compared with its original for lost or added meaning.

It returns failures only, with the counts checked, and creates no files.

The main context fixes, drops or moves each item to Coverage, records the dispositions, and runs the checker again. It then deletes raw participant data from the scratch folder and lists what was deleted.

**Done when:** every verifier item has a disposition, the checker is clean, and the deletion is recorded.

## Components

```text
skills/paper-critical-analysis/
  SKILL.md                     stages 0-7 with completion bars; the conditions table;
                               the load table; the method menu; rules (provenance,
                               nothing silent, evidence, write scope); output paths
  templates/
    report-template.md         the guide's outline; read by check_report.py
    evidence-template.md       the evidence file's sections
  prompts/
    judge.md                   stage 3 brief
    edit.md                    stage 5 brief
    verify.md                  stage 7 brief
  references/
    sources-and-venues.md      source types, review rigor, predatory-venue check,
                               sourcing red flags (every paper)
    research-integrity.md      every paper
    quantitative-methods.md    the paper reports measured quantities or statistics
    qualitative-methods.md     the paper collects or analyses qualitative data
    participants.md            people took part
    released-artifacts.md      code or data are released
  scripts/
    check_report.py
```

Material is merged from both skills as follows:

- `quantitative-methods.md` absorbs critical-analysis-report's experiment-design and result-interpretation background.
- `participants.md` absorbs its fair-treatment background.
- `sources-and-venues.md` combines the two skills' source-type sections.
- The judge brief is paper-critical-analysis's, with locators simplified.
- The checker is critical-analysis-report's, extended, with its length bounds removed.

`released-artifacts.md` is new. It says:

- what to open: analysis code, notebooks, data dictionaries and data files;
- what never to open or fetch: credential, key, environment and config files. If a repository appears to expose one, record its path only, neutrally, under Ethics;
- how to handle data: download only what a recomputation needs, into the scratch folder; keep aggregates only; never quote individual rows; never attempt re-identification, and note the risk of it only as an observation;
- how to record each check as a W entry.

## Rules

- **Provenance:** the reader must be able to tell apart what the paper says, what an outside source says, and what the writer infers. The marks under Outputs carry this distinction.
- **Nothing silent:** write `none found; checked: <where>`, `not checked: <reason>` or `not applicable: <reason>` rather than leaving a gap.
- **Integrity:** concerns are neutral observations, given with their benign explanations; never accusations.
- **Write scope:** every file the run creates goes in the output folder, scratch work included.
- **Quotes:** short ones only; never reproduce passages.

## Migration

All on branch `paper-critical-analysis-merge`:

- Rewrite `skills/paper-critical-analysis/` to the layout above; the `critical-analysis-report` skill directory is removed.
- Tests:
  - Rewrite `tests/test_paper_critical_analysis_skill.py` for the new stages, briefs, load table and template–checker agreement.
  - Add `tests/test_check_report.py`, with a passing report-and-evidence pair and one failing fixture per rule.
  - Remove `critical-analysis-report` from `tests/test_skill_contracts.py`.
  - Repin the vault-template row in `tests/test_templates.py` if its wording changes.
- `README.md`: merge the two skill rows into one.
- `ATTRIBUTION.md`:
  - Keep the nine MIT notices for text carried over from paper-critical-analysis.
  - Credit critical-analysis-report's material.
  - Name the editor's sources: the Professional Editorial Standards 2024 (paraphrased, since the text is copyrighted), Strunk's *The Elements of Style* (public domain), and Wikipedia's "Signs of AI writing" (paraphrased).
- `docs/agents/terminology.md`: the governed list already names `paper-critical-analysis`. Nothing to change unless a reference to the retired skill turns up.
- `research_vault/templates/vault/AGENTS.md`: keep the row and update its description if needed.
- `docs/research/2026-09-20-paper-critical-analysis-evals/README.md`: append a section for the merged skill's runs, with no absolute home paths.
- Branch `critique-skills-tuning` holds the minimal fixes tested in run 2. It is superseded by this branch; delete it once this lands.

## Testing and evaluation

**Offline:** the full suite (`python -m pytest tests -q -n auto`), plus ruff and mdformat.

**Behavioural:** one run per paper, using the prompts from the comparison runs with only the skill path changed.

1. **Bloom**, with the same inputs and the same 20-item answer key. It passes if:
   - the score is at least 18;
   - it uses about 8.5M fresh tokens or fewer, and about 2 hours or less;
   - nothing is unsupported after verification, and no outside claim is wrong;
   - it writes no files outside the output folder;
   - it fetches no credential files;
   - raw participant data is deleted.
2. **CheckIfExist** (Abbonato 2026, arXiv:2602.15871), the 9-page systems paper used in the earlier evals. An answer key is built from the run E and F records before the run. This tests a paper with no participants and heavy web use.
3. **A human read** of one report: is it the guide's result, in prose a person would want to read?

With one run per paper, differences of a point or two are noise. A second Bloom run is made only if the first is borderline.

## Non-goals

- Fast and deep modes.
- Running without web access.
- Fan-out across sections.
- Score tables.
- Referee-style output: questions or revision requests addressed to the authors.
- Critiques that span several papers.
