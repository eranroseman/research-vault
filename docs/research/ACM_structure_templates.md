# ACM sample (sources/ACM, 190 PDFs): paper structure templates

Contents: **Part 0** writer's guide (pick the type, how to use the numbers, heading names), **Part S** one-page cheat sheet for system papers, **Part M** one-page cheat sheet for method papers, **Part A** general template for all papers (including words before Results and the citation distribution), **Part B1** system papers (57), **Part B2** method papers (84). B1 and B2 are mutually exclusive; the 9 papers with both a System and a Method section are counted in B1.

Everything quantitative comes from the 190-paper sample (ACM HCI, ubiquitous computing and CSCW papers, 2023–2026). Items marked *editorial* are writing advice, not derived from the data.

# Part 0: Writer's guide

## 0.1 Pick the paper type

| If your paper's main contribution is... | Use | Typical evidence |
|---|---|---|
| A new system, tool, device or technique, with an evaluation | Part S (system cheat sheet) | Design goals, architecture, implementation, then an evaluation or a user study |
| Findings from a study: interviews, survey, experiment, field study, log analysis | Part M (method cheat sheet) | Participants, procedure, analysis, then results and discussion |
| A technical experiment or benchmark (ML, sensing) with datasets and baselines | Part S, with an "Experiment" section (the sample's Evaluation/Study/Data cluster, 39% of papers) | Dataset, setup, metrics, results |
| Both a system and a study of it | Part S, with the study as an embedded Method/Evaluation block | In the sample, 9 papers have both a System and a Method section |

If unsure, use Part A, which describes the whole sample.

## 0.2 Using the numbers

- Each cheat sheet (Parts S and M) gives word budgets as **median (Q1–Q3)** of a slot's share of body words, applied to a target length. The slot includes its subsections. Body words include the abstract and exclude title and authors, references, acknowledgments, captions and in-figure text.
- The ranges are independent per slot, so they do not sum to the target. Decide which optional slots you include, then scale the medians so they sum to your target.
- A slot inside Q1–Q3 is ordinary; outside it is a choice you can explain. Medians are descriptive, not a quality bar.
- The abstract is about 150 words whatever the length (Q1–Q3 140–163) and the conclusion stays short. Do not scale them.
- Q1–Q3 spans a lot, because the sample mixes 3-page extended abstracts and 48-page papers. The venue's page limit and reference style override every number here.
- The sample is ACM HCI/ubicomp/CSCW; do not apply it to other fields. Section sizes were measured from headings, so combined headings (such as "Introduction and Background") are counted under the first section.

## 0.3 Heading names

The sample's most common top-level headings (all 190 papers, case-insensitive), so a conventional name is the safe choice:

| Role | Conventional names (papers) | Less common |
|---|---|---|
| Introduction | Introduction (177) | Introduction and Background (2–4) |
| Related Work | Related Work (102) | Background (21), Background and Related Work (9), Literature Review (2) |
| Method | Methods (29), Method (24), Methodology (23) | Study Design (4), Procedure |
| Results | Results (43), Findings (39) | Results and Discussion (3), Preliminary Results |
| Discussion | Discussion (about 100) | Discussion and Future Work (10), Discussion and Conclusion (11) |
| Conclusion | Conclusion (about 120), Conclusions (8) | Conclusion and Future Work (9) |

- Use a standard heading where a standard one fits: the papers that avoid them accumulate paper-specific core sections (54% of papers have at least one; 6 papers have three custom core sections in a row).
- Pick either two sections (Discussion, Conclusion) or one combined heading, not both. Papers rarely use both forms.
- ACM's acknowledgment spelling varies ("Acknowledgments" 129, "Acknowledgements" 9).

# Part S: Cheat sheet, system paper

For a new system, tool, device or technique with an evaluation (57 papers in the sample). Detail: Part B1.

**Abstract > Introduction > Related Work > SYSTEM > Evaluation (or Method + Results) > Discussion > Conclusion > Acknowledgments > References**

| Slot | Included in | 4,000 body words (about 8 pages) | 7,000 (about 14 pages) | 10,000 (about 20 pages) |
|---|---|---|---|---|
| Abstract | 74% | about 150 | about 150 | about 150 |
| Introduction | 95% | 380 (300–580) | 660 (530–1,010) | 950 (760–1,450) |
| Related Work | 82% | 490 (420–660) | 850 (740–1,160) | 1,220 (1,050–1,650) |
| Core: system sections plus evaluation | 100% | 2,260 (1,580–2,560) | 3,950 (2,760–4,490) | 5,650 (3,950–6,410) |
| Results, as a separate section | 28% | 930 (710–1,140) | 1,620 (1,250–1,990) | 2,320 (1,780–2,850) |
| Discussion | 61% | 630 (370–830) | 1,110 (650–1,460) | 1,580 (930–2,080) |
| Conclusion | 89% | 120 (60–280) | 220 (100–500) | 310 (150–710) |

Page estimates use the group's median of about 500 body words per page.

**Core checklist.** Percentages are of the 57 papers; words are medians per paper (Q1–Q3 in Part B1). Expected means above about 70%, optional below about 30%; the "what to put in it" lines are *editorial*.

| Item | Papers | Median words | What to put in it |
|---|---|---|---|
| Design goals or requirements | 19% | 452 | The needs or formative findings the design follows from |
| System overview/architecture | 47% | 445 | Components and how they fit, usually with a figure |
| Implementation/interface | 39% | 254 | What others need to reproduce or extend the system |
| Evaluation as a separate section | 53% | 1,581 | What you evaluated, how, against what |
| Embedded study: procedure, participants | 56%, 46% | 685, 204 | Include if the evaluation is a user study |
| Embedded study: materials, analysis, measures | 37%, 35%, 18% | 218, 278, 251 | |
| Results inside the core | 30% | 743 | Instead of a separate Results section |
| Limitations as their own section | 19% | 256 | Most papers fold them into Discussion |

**Figures, tables, references** (median, Q1–Q3 in brackets):

| Per 1,000 body words | System papers |
|---|---|
| Figures | 1.2 (0.7–1.8), one per about 815 words |
| Tables | 0.25 (0.07–0.49), one per about 3,150 words |
| References | 8.3 (6.4–10.6) |

Worked example, 7,000 body words: about 8 figures, 2 tables, 58 references. A figure caption runs 35 words (15–61), a table caption 15 (9–34); in-figure and in-table text adds about 6.5% of the body.

**Pitfalls the data shows.** 61% of system papers have a paper-specific section next to the system section: expected, not an error. 28% combine Discussion and Conclusion under one heading; do not use both a combined heading and separate ones. 18% skip Related Work. Systems papers are more visual than method papers, with more than twice the caption share.

**Where the text and citations go.** Results starts after a median of 5,154 body words (Q1–Q3 2,030–6,424; only 16 papers have a separate Results section). About 73% of citations fall in the first half of a paper and about 48% in the first fifth; plan most references for the Introduction and Related Work, with a smaller group (about 18%) in the Discussion and Conclusion. Details in Part A sections 6 and 7.

# Part M: Cheat sheet, method paper

For findings from a study: interviews, survey, experiment, field study, log analysis (84 papers in the sample). Detail: Part B2.

**Abstract > Introduction > Related Work > METHOD > RESULTS > Discussion > Conclusion > Acknowledgments > References**

This is the textbook sequence; 10 of the 84 papers follow it exactly and 5 more match it without Acknowledgments.

| Slot | Included in | 3,000 body words (about 5 pages) | 5,500 (about 10 pages) | 9,000 (about 16 pages) |
|---|---|---|---|---|
| Abstract | 93% | about 150 | about 150 | about 150 |
| Introduction | 100% | 300 (220–420) | 540 (410–780) | 890 (670–1,270) |
| Related Work | 77% | 380 (300–580) | 690 (540–1,060) | 1,120 (890–1,740) |
| Method | 100% | 810 (480–1,190) | 1,480 (890–2,180) | 2,420 (1,450–3,560) |
| Results | 80% | 850 (650–1,100) | 1,570 (1,190–2,010) | 2,560 (1,950–3,290) |
| Discussion | 70% | 570 (460–700) | 1,040 (850–1,280) | 1,700 (1,390–2,100) |
| Conclusion | 93% | 100 (55–300) | 180 (100–540) | 300 (160–890) |

Page estimates use the group's median of about 570 body words per page.

**Method checklist.** Percentages are of the 84 papers; words are medians per paper (Q1–Q3 in Part B2). The order below is the typical order inside the Method section; the "what to put in it" lines are *editorial*.

| # | Item | Papers | Median words | What to put in it |
|---|---|---|---|---|
| 1 | Participants and recruitment | 50% | 208 | Number, selection, demographics |
| 2 | Study design and procedure | 44% | 571 | Tasks, conditions, protocol |
| 3 | Materials, apparatus, stimuli, datasets | 35% | 358 | |
| 4 | Measures, metrics, variables | 24% | 294 | |
| 5 | Data collection | 20% | 188 | Often merged into the procedure |
| 6 | Data analysis | 55% | 272 | Almost always last in Method |
| 7 | Ethics, approvals, positionality | 21% | 149 | Often placed late in the section |
| – | Results as their own section | 80% | 1,810 | 4% keep results inside the core |

**Figures, tables, references** (median, Q1–Q3 in brackets):

| Per 1,000 body words | Method papers |
|---|---|
| Figures | 0.5 (0.2–1.2), one per about 1,010 words |
| Tables | 0.24 (0–0.54), one per about 3,350 words |
| References | 8.4 (6.6–10.7) |

Worked example, 5,500 body words: about 3 figures, 1 table, 46 references. A figure caption runs 27 words (13–49), a table caption 13 (9–29); in-figure and in-table text adds about 4.4% of the body. Tables are mostly demographics, themes and statistics.

**Pitfalls the data shows.** 38% of method papers add a paper-specific section; 35% combine Discussion and Conclusion under one heading (do not mix forms); 23% skip Related Work; 20% skip Results as a section. Method and Results travel together in the data (phi +0.51).

**Where the text and citations go.** Results starts after a median of 2,610 body words (Q1–Q3 1,963–5,201), about 49% of the way through. About 73% of citations fall in the first half of a paper and about 48% in the first fifth; plan most references for the Introduction and Related Work. Method and Results cite little (about 1.5 per 1,000 words), then citations rise again in the Discussion and Conclusion (about 18% of all). Details in Part A sections 6 and 7.

# Part A: General template

Derived from all 190 PDFs in `sources/ACM` (HCI / ubiquitous-computing / CSCW papers, 2023–2026; median 8 pages, mean 14, range 3–48). Method: `pdftohtml -xml`; headings detected from bold numbered lines; words counted per section with subsections rolled into their top-level section; captions and small-font text counted separately; sections after References (appendices) excluded from the template.

Quartiles are written Q1 / median / Q3. "Papers" is the number (and share) of the 190 papers that have the element.

## 1. Paper size

| Measure | Q1 / median / Q3 | Mean |
|---|---|---|
| Pages | 7 / 8 / 21 | 14 |
| Total words, including references | 5,340 / 7,416 / 15,051 | 10,320 |
| Words excluding references | 3,537 / 5,330 / 11,004 | 7,253 |
| Top-level sections (front-matter headings included) | 10 / 11 / 12 | 11 |
| Subsections | 7 / 12 / 19 | 14 |
| References | 34 / 54 / 84 | 63 |
| Body words per page | 466 / 536 / 615 | 537 |
| Total words per page | 714 / 791 / 879 | 782 |

## 2. Template (nine slots)

Order is almost always the same when a slot is present. 155 of 190 papers (82%) never go backwards between slots; 146 (77%) are in order and also have Introduction, a core, a Discussion or Conclusion, and References.

**Abstract > Introduction > Related Work/Background > CORE > Results/Findings > Discussion (with Limitations/Future Work) > Conclusion > Acknowledgments > References**

| # | Slot | Papers | Words Q1 / median / Q3 | Mean share of body words |
|---|---|---|---|---|
| 1 | Abstract (CCS concepts and keywords: 17 / 22 / 26 words) | 163 (86%) | 140 / 151 / 163 | 3% |
| 2 | Introduction | 184 (97%) | 510 / 678 / 879 | 12% |
| 3 | Related Work/Background | 140 (74%) | 620 / 1,062 / 1,467 | 11% |
| 4 | Core (Method, System/Design, Evaluation/Study, custom sections; summed) | 186 (98%) | 1,194 / 2,278 / 4,605 | 41% |
| 5 | Results/Findings | 96 (51%) | 1,075 / 1,726 / 2,878 | 14% |
| 6 | Discussion (with Limitations/Future Work) | 118 (62%) | 592 / 1,310 / 2,313 | 11% |
| 7 | Conclusion (includes combined "Discussion and Conclusion" headings) | 170 (89%) | 126 / 210 / 448 | 6% |
| 8 | Acknowledgments | 140 (74%) | 27 / 46 / 75 | 1% |
| 9 | References (words) | 190 (100%) | 1,136 / 1,830 / 3,138 | not counted |

Standalone headings, for reference (Q1 / median / Q3 words): Method 787 / 1,163 / 1,790 (93 papers); System/Design/Implementation 730 / 1,477 / 2,529 (58); Evaluation/Study/Data 753 / 1,254 / 2,356 (74); Discussion 727 / 1,440 / 2,406 (104); Combined Discussion+Conclusion variants 356 / 557 / 1,052 (60); Limitations/Future Work 166 / 232 / 347 (30); Conclusion 109 / 144 / 214 (130).

Required in practice: Introduction, a core, a Discussion or Conclusion, References. Everything else is optional. Only 12 papers (6%) match the full textbook sequence exactly (Abstract > Introduction > Related Work > Method > Results > Discussion > Conclusion > Acknowledgments > References), so the template is a set of slots, not one fixed list.

Strong order regularities (papers having both): Introduction before Related Work 120/120; Method before Results 71/71; Results before Discussion 66/66; Discussion before Conclusion 85/85; Conclusion before Acknowledgments 95/95; System/Design before Evaluation 27/31.

Co-occurrence: Method and Results/Findings go together (phi +0.51). Discussion and Conclusion appear as either two sections or one combined heading, not both (phi about −0.5). Method is negatively associated with Evaluation/Study (−0.44) and System/Design (−0.42), which are alternative names for the core.

## 3. Core slot (slot 4)

Split by paper type in Parts S and M; the table here is for the whole sample. Order is the average relative position within the core, grouped into steps.

The core is a lead-in followed by components in a loose order. Percentages are of the 186 papers with a core. M is the 93 Method-type papers, S the 57 System-type papers (the groups overlap).

| Order | Component | All | M | S | Words Q1 / median / Q3 |
|---|---|---|---|---|---|
| 0 | Lead text before the first subsection | 100% | 100% | 100% | 102 / 276 / 580 |
| 1 | Design goals, requirements, motivation | 13% | 10% | 19% | 272 / 461 / 832 |
| 1 | Data collection | 13% | 19% | 9% | 118 / 206 / 296 |
| 2 | System overview/architecture | 30% | 20% | 47% | 273 / 422 / 708 |
| 2 | Participants/recruitment | 42% | 49% | 46% | 156 / 213 / 360 |
| 3 | Implementation/interface | 21% | 12% | 39% | 166 / 243 / 445 |
| 3 | Materials/apparatus/stimuli/datasets | 33% | 34% | 37% | 162 / 254 / 523 |
| 4 | Procedure/protocol/study design | 48% | 47% | 56% | 331 / 581 / 903 |
| 4 | Measures/metrics/variables | 22% | 24% | 18% | 178 / 294 / 528 |
| 4 | Evaluation/experiment setup | 13% | 12% | 18% | 152 / 350 / 628 |
| 5 | Ethics/positionality/approvals | 14% | 22% | 11% | 106 / 146 / 359 |
| 5 | Data analysis | 41% | 54% | 35% | 160 / 276 / 414 |
| 6 | Results sub-sections inside the core | 17% | 4% | 30% | 326 / 536 / 782 |
| – | Other paper-specific subsections | 70% | 59% | 86% | 423 / 924 / 1,934 |

## 4. Ratios: references, captions, tables, figures

"Body words" means main-text words excluding references, acknowledgments, front matter (title/authors), captions and small-font text. It includes the abstract. One paper (Schnur et al.) has no usable body and is excluded, so n = 189. Reference counts are the highest numbered `[n]` entry in each paper's list.

| Ratio | Q1 / median / Q3 | Mean |
|---|---|---|
| Reference words / total words | 0.177 / 0.216 / 0.264 | 0.223 |
| Reference words / body words | 0.245 / 0.309 / 0.408 | 0.341 |
| Reference entries per 1,000 body words | 6.5 / 8.6 / 11.4 | 9.4 |
| Body words per reference entry | 88 / 117 / 154 | 163 |
| Words per reference entry | 32 / 35 / 39 | 45 |
| Figure-caption words / body words | 0.007 / 0.026 / 0.050 | 0.035 |
| Table-caption words / body words | 0 / 0.003 / 0.010 | 0.008 |
| Fig+table caption words / total words | 0.007 / 0.023 / 0.042 | 0.028 |
| Small-font text (table cells, figure labels, footnotes) / body words | 0.033 / 0.057 / 0.089 | 0.080 |
| (Captions + small-font text) / body words | 0.055 / 0.095 / 0.158 | 0.123 |
| Figures per 1,000 body words | 0.35 / 0.84 / 1.36 | 0.97 |
| Tables per 1,000 body words | 0 / 0.24 / 0.51 | 0.34 |
| Body words per figure (papers with figures, n=162) | 701 / 963 / 1,630 | 1,550 |
| Body words per table (papers with tables, n=135) | 1,600 / 3,150 / 4,550 | 3,570 |
| Figures per page | 0.19 / 0.44 / 0.67 | 0.48 |
| Tables per page | 0 / 0.14 / 0.28 | 0.17 |

Counts and caption lengths:

| Item | Papers with at least one | Per paper | Words per caption |
|---|---|---|---|
| Figures | 163 (86%) | mean 6, median 5, max 29 | mean 40, median 28, Q1–Q3 14–55, max 186 (1,157 captions) |
| Tables | 136 (72%) | mean 2, median 2, max 20 | mean 25, median 16, Q1–Q3 9–33, max 187 (435 captions) |
| Other (listings, algorithms) | 9 | rare | mean 18 (13 captions) |

Small-font text in total: 150 / 261 / 634 words per paper (mean 533, max 4,473).

Rules of thumb: references take about a fifth of all words and about 0.3 words per body word; there is about one figure per 1,000 body words (one per 960 at the median) and one table per 3,000; captions plus in-figure and in-table text add roughly 10% on top of the body.

## 5. References versus sections

Reference count tracks paper length (Spearman +0.83 with non-reference words). Section word counts correlating with reference count: Discussion +0.74, Related Work +0.63, Results +0.62, Method +0.62, Introduction +0.55. Papers with a Discussion average 76 references versus 47 without; with Related Work 71 versus 49. Appendix papers average 107 references, which is a length effect.

## 6. Words before Results

Body words from the abstract to the start of a top-level Results/Findings section, excluding the title block and keywords. 96 papers (51%) have such a section.

| Measure | Q1 / median / Q3 | Mean | Min–max |
|---|---|---|---|
| Words before Results | 1,913 / 2,618 / 5,238 | 3,673 | 941–8,561 |
| Share of the paper's body words | 42% / 49% / 59% | 51% | 21–78% |
| Words from Results to the end (before references) | 1,790 / 3,216 / 5,441 | 3,706 | 545–9,485 |

What fills the words before Results (median, Q1–Q3): Abstract 148 (128–157); Introduction 696 (500–888); Related Work 899 (346–1,330, Q1 is low because some papers have none); core 1,274 (834–2,749).

The distribution has two clusters. By words before Results (bin starts, papers): 0: 1; 1,000: 27; 2,000: 23; 3,000: 4; 4,000: 11; 5,000: 13; 6,000: 16; 8,000: 1. About 50 papers have 1,000–3,000 words before Results and about 40 have 4,000–8,000, matching short extended abstracts and full papers.

| Type | Papers with Results | Words before Results (Q1 / median / Q3) | Share of body (median) | Core (median) |
|---|---|---|---|---|
| Method | 67 of 84 | 1,963 / 2,610 / 5,201 | 49% | 1,255 |
| System | 16 of 57 | 2,030 / 5,154 / 6,424 | 53% | 3,357 |

The system row rests on 16 papers. For the 88 papers with no Results section, the words before the first Discussion, Conclusion or Limitations section have a median of 3,838 (Q1–Q3 2,815–8,242), about 83% of the body: the evaluation sits inside the core, so almost the whole paper comes before the discussion.

## 7. Citation distribution

In-text numbered citations (`[12]`, `[3, 7]`, `[4–6]`; lists and ranges expanded) from the Introduction to the References heading, all 190 papers. First half means the first 50% of body words.

| Measure (Q1 / median / Q3) | First half | Second half |
|---|---|---|
| Citations, each reference counted separately | 32 / 62 / 106 (mean 72, max 259) | 10 / 22 / 36 (mean 29) |
| Citation brackets (`[3, 7]` counts once) | 23 / 41 / 67 (mean 49) | – |
| Citations per 1,000 words | 13.2 / 18.2 / 23.2 | 3.5 / 6.0 / 10.9 |
| Distinct references cited | 25 / 46 / 68 (mean 48) | – |

- A median of 73% of a paper's citations (Q1–Q3 63–84%) fall in the first half; 168 of 190 papers have more citations in the first half than the second.
- A median of 82% of the references a paper cites (Q1–Q3 71–91%) are already cited by the end of the first half.

By tenth of the paper's words:

| Tenth | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th | 9th | 10th |
|---|---|---|---|---|---|---|---|---|---|---|
| Share of all citations | 24.9% | 22.8% | 12.5% | 6.7% | 4.8% | 3.6% | 3.3% | 3.8% | 9.6% | 8.0% |
| Median citations per 1,000 words | 28.3 | 27.7 | 15.1 | 6.5 | 3.3 | 1.5 | 1.5 | 2.0 | 10.3 | 9.3 |

The first fifth (Introduction and Related Work) holds 47.7% of all citations at about 28 per 1,000 words. Citations drop to about 1.5 per 1,000 words in the sixth and seventh tenths (Method and Results), then rise to about 10 per 1,000 words in the last fifth (Discussion and Conclusion), which holds 17.6%. Every paper has at least 4 citations in the first half.

## 8. Limitations

- Section classes come from heading keywords; 13 papers have no heading recognised as plain "Introduction" (mostly "Introduction and Background" variants, counted in slot 2 here) and one paper with unnumbered headings parsed poorly.
- Papers without a bold Abstract heading have their abstract counted in front matter.
- Table and figure content cannot be told apart in PDF text, so "small-font text" covers cell text, figure labels and footnotes together.
- Core component percentages depend on a keyword classifier; 70% of papers also have unclassified paper-specific subsections.
- Word counts count tokens that start with a letter or digit; they are approximate to a few percent (the sum of parsed parts matched pdftotext totals within about 5% on a 12-paper check).
- Only numbered `[n]` citations are counted, and the tenths in section 7 are by word position including figure and table text, so they only approximate where sections fall.
- Sample is one publisher's HCI-adjacent papers, not ACM as a whole.

Scripts: `/tmp/acm_work/` (`analyze.py`, `stats.py`, `corr.py`, `order.py`, `sysd.py`, `tmpl.py`, `q.py`, `core.py`, `ratios.py`, `before.py`, `cites.py`). The earlier files in `/tmp/acm_work/` were cleaned up before `cites.py` was written, so only `cites.py` and the text extraction were re-created; rerunning the others needs the XML extraction again.

---

# Part B1: System papers (reference detail)

The cheat sheet is Part S; core component statistics are in its checklist, and limitations are in Part A section 8.

Group: the 57 of 190 papers with a top-level System/Design/Implementation section before References. (An earlier summary said 58: that count included one paper with such a section after References.) 9 of them also have a top-level Method section; those 9 are counted here, not in the method group (Part B2).

Quartiles are Q1 / median / Q3. Method as in Part A; word counts are approximate.

## Size

| Measure | Q1 / median / Q3 |
|---|---|
| Pages | 7 / 17 / 24 |
| Body words (excl. references, acknowledgments, front matter, captions, small-font text) | 3,455 / 9,071 / 11,121 |
| Total words incl. references | 4,633 / 11,086 / 14,473 |
| References | 39 / 58 / 82 (mean 64) |
| Core words (system sections plus anything else in the core) | 1,923 / 3,941 / 5,861 |
| Core subsections | 5 / 9 / 13 |

## Template

**Abstract > Introduction > Related Work > SYSTEM > Evaluation (or Method + Results) > Discussion > Conclusion > Acknowledgments > References**

| Slot | Papers | Words Q1 / median / Q3 | Mean share of body |
|---|---|---|---|
| Abstract | 42 (74%) | 139 / 153 / 162 | 3% |
| Introduction | 54 (95%) | 555 / 736 / 886 | 11% |
| Related Work/Background | 47 (82%) | 723 / 1,105 / 1,442 | 11% |
| **Core** (System plus Evaluation/Method/custom, summed) | 57 (100%) | 1,923 / 3,941 / 5,945 | **52%** |
| Results/Findings | 16 (28%) | 1,036 / 1,894 / 3,068 | 6% |
| Discussion (with Limitations/Future Work) | 35 (61%) | 466 / 1,145 / 2,423 | 10% |
| Conclusion (incl. combined headings) | 51 (89%) | 112 / 166 / 381 | 5% |
| Acknowledgments | 44 (77%) | 26 / 48 / 86 | 1% |
| References | 57 (100%) | 39 / 58 / 82 entries | not counted |

Standalone headings, as the share of the 57 papers with each and word quartiles:

| Heading | Papers | Words Q1 / median / Q3 |
|---|---|---|
| System/Design/Implementation | 57 (100%) | 731 / 1,497 / 2,541 |
| Evaluation/Study/Data | 30 (53%) | 1,030 / 1,581 / 2,852 |
| Discussion | 26 (46%) | 1,034 / 1,718 / 2,537 |
| Combined Discussion+Conclusion | 16 (28%) | 449 / 818 / 1,476 |
| Results/Findings | 16 (28%) | 1,036 / 1,894 / 3,068 |
| Limitations/Future Work | 11 (19%) | 191 / 256 / 349 |
| Background (standalone) | 10 (18%) | 646 / 1,005 / 1,343 |
| Method | 9 (16%) | 523 / 1,039 / 1,640 |
| Paper-specific sections (summed) | 35 (61%) | 652 / 1,138 / 1,956 |

## Order

The system section follows Related Work (or the Introduction when there is no Related Work) at about 40% of the way through the paper. System before Evaluation held in 27 of 31 papers that have both. Recurring sequences, 2 papers each (nothing is more common):
- Abstract > Introduction > Related Work > System > Method > Results > Discussion > Conclusion > Acknowledgments
- Abstract > Introduction > Related Work > System > Evaluation > Discussion+Conclusion > Limitations > Conclusion > Acknowledgments
- Abstract > Introduction > System > Discussion+Conclusion > Acknowledgments (no Related Work, no evaluation)
- Abstract > Introduction > Related Work > System > Evaluation > Results > Discussion > Conclusion > Acknowledgments

Top-level core arrangements: System alone 5; System then Evaluation/Study 4; System then a custom section 3; System > System > Evaluation 3; System > System 2; System then Method 2.

## Figures, tables, references

| Measure | Q1 / median / Q3 | Mean |
|---|---|---|
| Figures per paper | 5 / 8 / 10 | 8.9 |
| Tables per paper | 1 / 2 / 4 | 2.5 |
| Papers with at least one figure / table | 56 (98%) / 43 (75%) | |
| Words per figure caption | 15 / 35 / 61 | 45 |
| Words per table caption | 9 / 15 / 34 | 25 |
| Reference words / body words | 0.228 / 0.282 / 0.395 | 0.316 |
| Reference words / total words | 0.169 / 0.203 / 0.252 | 0.209 |
| References per 1,000 body words | 6.4 / 8.3 / 10.6 | 8.8 |
| Figure-caption words / body words | 0.025 / 0.048 / 0.080 | 0.056 |
| Table-caption words / body words | 0.0004 / 0.004 / 0.011 | 0.008 |
| Small-font text (cells, labels, footnotes) / body words | 0.039 / 0.065 / 0.104 | 0.093 |
| Figures per 1,000 body words | 0.69 / 1.2 / 1.8 | 1.36 |
| Tables per 1,000 body words | 0.07 / 0.25 / 0.49 | 0.33 |
| Body words per figure | 558 / 815 / 1,380 | 1,030 |
| Body words per table | 1,700 / 3,150 / 4,520 | 3,680 |
| Figures per page | 0.39 / 0.57 / 0.82 | 0.64 |
| Tables per page | 0.04 / 0.13 / 0.28 | 0.16 |

System papers are visual: about one figure per 815 body words, against one per 1,010 in the method group, and roughly twice the figure-caption share.

# Part B2: Method papers (reference detail)

The cheat sheet is Part M; core component statistics are in its checklist, and limitations are in Part A section 8. This group is a keyword-defined cut (any top-level Method heading), so it includes some technical experiment papers alongside human-subjects studies.

Group: the 84 of 190 papers with a top-level Method/Methodology section before References and no top-level System/Design/Implementation section. (9 papers have both; they are in Part B1.) These are mostly empirical user studies: interviews, surveys, experiments.

Quartiles are Q1 / median / Q3. Word counts are approximate; method as in Part A.

## Size

| Measure | Q1 / median / Q3 |
|---|---|
| Pages | 7 / 8 / 20 |
| Body words (excl. references, acknowledgments, front matter, captions, small-font text) | 3,905 / 5,550 / 11,336 |
| Total words incl. references | 5,060 / 7,401 / 14,929 |
| References | 33 / 54 / 92 (mean 67) |
| Core words (Method plus any other core sections) | 931 / 1,456 / 2,957 |
| Core subsections | 3 / 4 / 7 |

## Template

**Abstract > Introduction > Related Work > METHOD > RESULTS > Discussion > Conclusion > Acknowledgments > References**

This is close to the textbook sequence, and it is the most common single sequence in the whole sample: 10 of these 84 papers follow it exactly, and 5 more match it without Acknowledgments.

| Slot | Papers | Words Q1 / median / Q3 | Mean share of body |
|---|---|---|---|
| Abstract | 78 (93%) | 141 / 151 / 162 | 3% |
| Introduction | 84 (100%) | 529 / 696 / 942 | 12% |
| Related Work/Background | 65 (77%) | 637 / 1,056 / 1,647 | 12% |
| **Core** (Method plus anything else in the core, summed) | 84 (100%) | 931 / 1,456 / 2,957 | **30%** |
| **Results/Findings** | 67 (80%) | 1,208 / 1,810 / 2,990 | **23%** |
| Discussion (with Limitations/Future Work) | 59 (70%) | 706 / 1,674 / 2,582 | 13% |
| Conclusion (incl. combined headings) | 78 (93%) | 138 / 231 / 490 | 7% |
| Acknowledgments | 58 (69%) | 28 / 44 / 72 | 1% |

Standalone headings (share of the 84 papers, word quartiles):

| Heading | Papers | Words Q1 / median / Q3 |
|---|---|---|
| Method/Methodology | 84 (100%) | 799 / 1,170 / 1,797 |
| Results/Findings | 67 (80%) | 1,208 / 1,810 / 2,990 |
| Related Work/Background (combined) | 58 (69%) | 602 / 971 / 1,367 |
| Discussion | 55 (65%) | 798 / 1,690 / 2,674 |
| Conclusion | 55 (65%) | 119 / 158 / 231 |
| Paper-specific sections (summed) | 32 (38%) | 337 / 840 / 2,247 |
| Combined Discussion+Conclusion | 29 (35%) | 372 / 554 / 1,048 |
| Limitations/Future Work | 16 (19%) | 164 / 221 / 372 |
| Evaluation/Study/Data | 14 (17%) | 633 / 1,074 / 1,368 |
| Background (standalone) | 12 (14%) | 969 / 1,183 / 1,901 |

## Order

Method before Results held in every paper that has both. Recurring sequences (papers):
- Abstract > Introduction > Related Work > Method > Results > Discussion > Conclusion > Acknowledgments (10)
- the same without Acknowledgments (5)
- Abstract > Introduction > Related Work > Method > Results > Discussion+Conclusion > Acknowledgments (4)
- with a Limitations/Future Work section before the Conclusion (3)
- Abstract > Introduction > Method > Results > Discussion+Conclusion, no Related Work (2)

Top-level core arrangements: Method alone 49; Method then a custom section 13; Method then Evaluation/Study 4; custom section then Method 3; Method then two custom sections 3.

## Figures, tables, references

| Measure | Q1 / median / Q3 | Mean |
|---|---|---|
| Figures per paper | 1 / 4 / 9 | |
| Tables per paper | 0 / 2 / 3 | |
| Papers with at least one figure / table | 66 (79%) / 61 (73%) | |
| Words per figure caption | 13 / 27 / 49 | 36 |
| Words per table caption | 9 / 13 / 29 | 23 |
| Reference words / body words | 0.233 / 0.307 / 0.376 | 0.315 |
| Reference words / total words | 0.179 / 0.217 / 0.259 | 0.218 |
| References per 1,000 body words | 6.6 / 8.4 / 10.7 | 8.8 |
| Figure-caption words / body words | 0.003 / 0.014 / 0.041 | 0.025 |
| Table-caption words / body words | 0 / 0.002 / 0.010 | 0.009 |
| Small-font text (cells, labels, footnotes) / body words | 0.030 / 0.044 / 0.069 | 0.065 |
| Figures per 1,000 body words | 0.19 / 0.52 / 1.2 | 0.75 |
| Tables per 1,000 body words | 0 / 0.24 / 0.54 | 0.37 |
| Body words per figure (papers with figures) | 746 / 1,010 / 2,600 | 2,060 |
| Body words per table (papers with tables) | 1,450 / 3,350 / 4,550 | 3,520 |
| Figures per page | 0.12 / 0.29 / 0.59 | 0.38 |
| Tables per page | 0 / 0.14 / 0.29 | 0.19 |

Method papers are text-heavy: about half the figure density of the system group, with tables at the same density. Counts of tables are driven by participant demographics, themes and statistics.
