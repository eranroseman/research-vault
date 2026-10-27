# ACM sample (sources/ACM, 190 PDFs): paper structure templates

Contents: **Part 0** writer's guide (decision step, length budgets, checklists, heading names, how to use the numbers), **Part A** general template for all papers, **Part B1** system papers (57), **Part B2** method papers (84). B1 and B2 are mutually exclusive; the 9 papers with both a System and a Method section are counted in B1.

Everything quantitative comes from the 190-paper sample (ACM HCI, ubiquitous computing and CSCW papers, 2023–2026). Items marked *editorial* are writing advice, not derived from the data.

# Part 0: Writer's guide

## 0.1 Pick the paper type

| If your paper's main contribution is... | Use | Typical evidence |
|---|---|---|
| A new system, tool, device or technique, with an evaluation | Part B1 (system) | Design goals, architecture, implementation, then an evaluation or a user study |
| Findings from a study: interviews, survey, experiment, field study, log analysis | Part B2 (method) | Participants, procedure, analysis, then results and discussion |
| A technical experiment or benchmark (ML, sensing) with datasets and baselines | Part B1 core, with an "Experiment" section (the sample's Evaluation/Study/Data cluster, 39% of papers) | Dataset, setup, metrics, results |
| Both a system and a study of it | Part B1, with the study as an embedded Method/Evaluation block | In the sample, 9 papers have both a System and a Method section |

If unsure, use Part A, which describes the whole sample.

## 0.2 Length budgets

Pick a target body length, in words, and read the row. Body words include the abstract and exclude title and authors, references, acknowledgments, captions and in-figure text. Each cell is **median (Q1–Q3)** of that slot's share of body words, applied to the target. The slot is the section including its subsections.

How to use it:
- The ranges are independent per slot, so they do not sum to the target. Decide which optional slots you include, then scale the medians proportionally so they sum to your target.
- Treat a slot inside Q1–Q3 as ordinary and outside it as a deliberate choice you can explain.
- The abstract is about 150 words whatever the length (Q1–Q3 140–163), and the conclusion stays short. Do not scale them.

### System papers (B1)

| Slot | Included in | 4,000 body words (about 8 pages) | 7,000 (about 14 pages) | 10,000 (about 20 pages) |
|---|---|---|---|---|
| Introduction | 95% | 380 (300–580) | 660 (530–1,010) | 950 (760–1,450) |
| Related Work | 82% | 490 (420–660) | 850 (740–1,160) | 1,220 (1,050–1,650) |
| Core: system sections plus evaluation | 100% | 2,260 (1,580–2,560) | 3,950 (2,760–4,490) | 5,650 (3,950–6,410) |
| Results, as a separate section | 28% | 930 (710–1,140) | 1,620 (1,250–1,990) | 2,320 (1,780–2,850) |
| Discussion | 61% | 630 (370–830) | 1,110 (650–1,460) | 1,580 (930–2,080) |
| Conclusion | 89% | 120 (60–280) | 220 (100–500) | 310 (150–710) |

Of the core, the system sections themselves have a median of 1,497 words (Q1–Q3 731–2,541); evaluation or study sections add 1,581 (1,030–2,852) in the 53% of papers that have them.

### Method papers (B2)

| Slot | Included in | 3,000 body words (about 5 pages) | 5,500 (about 10 pages) | 9,000 (about 16 pages) |
|---|---|---|---|---|
| Introduction | 100% | 300 (220–420) | 540 (410–780) | 890 (670–1,270) |
| Related Work | 77% | 380 (300–580) | 690 (540–1,060) | 1,120 (890–1,740) |
| Method | 100% | 810 (480–1,190) | 1,480 (890–2,180) | 2,420 (1,450–3,560) |
| Results | 80% | 850 (650–1,100) | 1,570 (1,190–2,010) | 2,560 (1,950–3,290) |
| Discussion | 70% | 570 (460–700) | 1,040 (850–1,280) | 1,700 (1,390–2,100) |
| Conclusion | 93% | 100 (55–300) | 180 (100–540) | 300 (160–890) |

The page estimates use the groups' median body words per page: about 500 for system papers (more figures) and about 570 for method papers.

### Figure, table and reference budgets

| Per target length | System papers | Method papers |
|---|---|---|
| Figures per 1,000 body words (median; Q1–Q3) | 1.2 (0.7–1.8) | 0.5 (0.2–1.2) |
| Tables per 1,000 body words | 0.25 (0.07–0.49) | 0.24 (0–0.54) |
| References per 1,000 body words | 8.3 (6.4–10.6) | 8.4 (6.6–10.7) |
| Words per figure caption (median) | 35 (15–61) | 27 (13–49) |
| Words per table caption (median) | 15 (9–34) | 13 (9–29) |
| Small-font text (cell, label, footnote words) as a share of body | 6.5% | 4.4% |

Worked example for a system paper of 7,000 body words: about 8 figures, 2 tables and 58 references. For a method paper of 5,500 body words: about 3 figures, 1 table and 46 references. The venue's page limit and reference style override these numbers.

## 0.3 Checklists

Use the prevalence to decide whether an item is expected or optional. Above about 70% means readers expect it; below about 30% means include it only if your paper needs it. The "what to put in it" lines are *editorial*.

### Every paper

| Slot | Expected? | What to put in it (*editorial*) |
|---|---|---|
| Abstract | 86% have a separate Abstract heading | Problem, approach, main result, contribution, in about 150 words |
| Introduction | 97% | Problem and context, gap, your contribution, a short outline. Median 680 words |
| Related Work | 74% | Group prior work by theme and say what each group lacks. Median 1,060 words |
| Core | 98% | See the type-specific lists below |
| Results (if separate) | 51% | Findings organised by research question or theme, with tables and figures |
| Discussion | 62% | Interpretation, implications, limitations, future work |
| Conclusion | 89%, often under a combined "Discussion and Conclusion" heading | Short: contribution restated, main takeaway. Median 144 words as its own section |
| Acknowledgments | 74% | Funding, contributors, short (median 46 words) |
| References | 100% | Median 54 entries, mean 63 |

### System papers: core checklist

| Item | In system papers | Notes |
|---|---|---|
| Design goals or requirements | 19% | Include if the design follows from a formative study or stated needs |
| System overview or architecture | 47% | Often with a figure; the most common named subsection |
| Implementation or interface | 39% | Technical detail others need to reproduce or extend |
| Evaluation, as study or technical experiment | 53% as a separate section | State what you evaluated and how |
| Embedded study details | participants 46%, procedure 56%, materials 37%, analysis 35% | Include them if the evaluation is a user study |
| Figure budget | 8 per paper (median) | About one per 815 body words |
| Limitations | 19% as a standalone section | Most papers fold them into Discussion |

### Method papers: core checklist

| Item | In method papers | Notes |
|---|---|---|
| Participants and recruitment | 50% | Number, selection, demographics |
| Study design and procedure | 44% | Tasks, conditions, protocol |
| Materials, apparatus, stimuli, datasets | 35% | |
| Measures, metrics, variables | 24% | |
| Data collection | 20% | Often merged into procedure |
| Data analysis | 55% | Almost always last in the Method section |
| Ethics, approvals, positionality | 21% | Often placed late in the section |
| Results as their own section | 80% | 4% keep results inside the core |

## 0.4 Heading names

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

## 0.5 Reading the numbers

- These are descriptive medians of one sample, not a quality bar. A paper outside Q1–Q3 can be fine.
- Q1–Q3 spans a lot, because the sample mixes 3-page extended abstracts and 48-page papers. Match your venue's page limit before using any budget.
- The sample is ACM HCI/ubicomp/CSCW. Do not apply it to other fields or to non-ACM templates.
- Section sizes were measured from headings, so a word count under a heading includes its subsections, and combined headings (such as "Introduction and Background") are counted under the first section.
- Reference counts depend on the numbered `[n]` list surviving text extraction; word counts are approximate to a few percent.

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

Order is the average relative position within the core, grouped into steps.

Study variant (Method-type): Method lead-in > Participants/recruitment > Study design and procedure (and materials) > Measures > Data analysis > Ethics/positionality.
System variant (System-type): Design goals > System overview/architecture > Implementation/interface > optional embedded study (participants, procedure, datasets) > Results sub-sections.

Core size, Q1 / median / Q3: all 1,180 / 2,237 / 4,260 words and 3 / 6 / 10 subsections; Method-type 991 / 1,647 / 2,860 words and 3 / 5 / 7 subsections; Eval/Study-type (72 papers) 1,623 / 2,873 / 5,611 words and 5 / 9 / 13 subsections; System-type 1,923 / 3,941 / 5,861 words and 5 / 9 / 13 subsections.

Top-level core arrangements: Method alone 49 papers; Method then custom 13; Custom then Eval/Study 6; three custom sections 6; System alone 5; custom alone 5; Eval/Study alone 5; System then Eval/Study 4; Eval/Study twice 4; Method then Eval/Study 4; System then custom 3.

Systems papers (58 with a top-level System/Design section) typically run Abstract > Introduction > Related Work > System > Evaluation > Discussion > Conclusion. The design section sits about 40% of the way through and holds about 24% of the non-reference words. Systems papers have more figures (mean 8.9, median 8) than the other papers (mean 4.9).

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

## 6. Limitations

- Section classes come from heading keywords; 13 papers have no heading recognised as plain "Introduction" (mostly "Introduction and Background" variants, counted in slot 2 here) and one paper with unnumbered headings parsed poorly.
- Papers without a bold Abstract heading have their abstract counted in front matter.
- Table and figure content cannot be told apart in PDF text, so "small-font text" covers cell text, figure labels and footnotes together.
- Core component percentages depend on a keyword classifier; 70% of papers also have unclassified paper-specific subsections.
- Word counts count tokens that start with a letter or digit; they are approximate to a few percent (the sum of parsed parts matched pdftotext totals within about 5% on a 12-paper check).
- Sample is one publisher's HCI-adjacent papers, not ACM as a whole.

Scripts: `/tmp/acm_work/` (`analyze.py`, `stats.py`, `corr.py`, `order.py`, `sysd.py`, `tmpl.py`, `q.py`, `core.py`, `ratios.py`).

---

# Part B1: System papers

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

## Core components

Percentages are of the 57 papers. Order is the average relative position in the core, 0 to 1.

| Order | Component | Papers | Words Q1 / median / Q3 |
|---|---|---|---|
| 0.25 | Data collection | 9% | 146 / 208 / 238 |
| 0.30 | Design goals/requirements | 19% | 273 / 452 / 708 |
| 0.35 | Lead text before the first subsection | 100% | 239 / 455 / 813 |
| 0.42 | **System overview/architecture** | 47% | 268 / 445 / 687 |
| 0.48 | **Implementation/interface** | 39% | 179 / 254 / 668 |
| 0.50 | Participants/recruitment (embedded study) | 46% | 152 / 204 / 337 |
| 0.54 | Materials/apparatus/stimuli/datasets | 37% | 120 / 218 / 454 |
| 0.60 | Procedure/protocol/study design | 56% | 455 / 685 / 1,187 |
| 0.67 | Data analysis | 35% | 160 / 278 / 429 |
| 0.68 | Evaluation/experiment setup | 18% | 166 / 324 / 446 |
| 0.68 | Measures/metrics/variables | 18% | 199 / 251 / 512 |
| 0.72 | Results sub-sections inside the core | 30% | 428 / 743 / 1,207 |
| – | Paper-specific subsections | 86% | 638 / 1,386 / 2,395 |

Typical flow: design goals, then overview/architecture, then implementation and interface, then (for about half) an embedded user study with participants, procedure and analysis, then results. The most common named subsections under the system section are Overview/Architecture (37 across the group), then study-procedure titles (24), Implementation/Interface (19) and datasets/materials (14). 114 subsections have paper-specific titles (component names and the like).

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

## Limitations

Same as the full template. The group is small (57), so quartiles for rare slots (Results 16, Method 9) are rough. Paper-specific subsection titles dominate the system section and are not classified.

# Part B2: Method papers

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

## Core components

Percentages are of the 84 papers. Order is the average relative position within the core, 0 to 1.

| Order | Component | Papers | Words Q1 / median / Q3 |
|---|---|---|---|
| 0.24 | Lead text before the first subsection | 100% | 53 / 195 / 380 |
| 0.43 | Data collection | 20% | 84 / 188 / 345 |
| 0.49 | **Participants/recruitment** | 50% | 159 / 208 / 314 |
| 0.51 | Materials/apparatus/stimuli/datasets | 35% | 223 / 358 / 565 |
| 0.54 | **Procedure/protocol/study design** (tasks, conditions, interviews) | 44% | 306 / 571 / 706 |
| 0.54 | Measures/metrics/variables | 24% | 138 / 294 / 536 |
| 0.66 | Ethics/positionality/approvals | 21% | 106 / 149 / 346 |
| 0.80 | **Data analysis** | 55% | 170 / 272 / 374 |
| – | Paper-specific subsections | 55% | 282 / 597 / 1,545 |

Rare in this group: design goals (8%), implementation (11%), system overview (20%, mostly study prototypes), results inside the core (4%).

Typical flow: Method lead-in, then participants and recruitment, then study design and procedure (with materials and measures), then data analysis, and an ethics or positionality note late. Counts of the most common named subsections under Method (across the group): study procedure/design 51, participants 50, data analysis 47, materials 26, measures 22, data collection 18, ethics 17; 66 titles are paper-specific.

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

## Limitations

Same as the full template. The group is a keyword-defined cut (any top-level Method heading), so it includes some technical experiment papers alongside human-subjects studies; the sample is the ACM files in `sources/ACM`, not ACM as a whole.
