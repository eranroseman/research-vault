# Paper structure templates from 190 ACM papers

Use when planning the structure, section lengths, figures, tables or references of an ACM HCI, ubiquitous-computing or CSCW paper. Source: the 190 PDFs in `sources/ACM` (2023–2026). *Editorial* marks advice the sample does not measure.

## 1. Procedure

Each step ends on its done-test.

1. **Pick the type** (section 2). Done when one cheat sheet is named.
2. **Set the target** in body words: venue page limit times the group's body words per page (about 500 for system papers, 570 for method papers). Done when you have one number.
3. **Choose the slots.** Include every slot the cheat sheet's "Included in" column puts at 70% or more; include a slot below 70% only when the paper has content for it. Done when every slot is marked in or out.
4. **Budget the words.** Read each included slot's median at the nearest target length in the cheat sheet, then scale the medians so they sum to your target. Fix the abstract at about 150 words (Q1–Q3 140–163) and keep the conclusion at the cheat sheet's figure. Done when the budgets sum to the target.
5. **Fill the core checklist** with the same rule: items at 70% or more go in; the rest go in only when the paper has content for them. Done when every item is marked in or out.
6. **Set the counts.** Multiply the cheat sheet's per-1,000-word rates for figures, tables and references by the target in thousands, and place references as 5.5 shows. Done when you have three counts.
7. **Check the draft.** Each slot falls inside its Q1–Q3 range, or you can state why not. Done when every outside slot has a stated reason.

Definitions used throughout:
- **Q1 / median / Q3** are the 25th, 50th and 75th percentiles; budgets are written median (Q1–Q3).
- **Body words** include the abstract and exclude title and authors, references, acknowledgments, captions and in-figure text.
- A **slot** is a top-level section with its subsections; the **core** is every Method, System, Evaluation and paper-specific section between Related Work and Results.
- Q1–Q3 is wide because the sample mixes 3-page extended abstracts with 48-page papers. The venue's page limit and reference style set the final numbers.

## 2. Pick the paper type

| If your paper's main contribution is... | Use | Typical evidence |
|---|---|---|
| A new system, tool, device or technique, with an evaluation | System cheat sheet (3) | Design goals, architecture, implementation, then an evaluation or a user study |
| Findings from a study: interviews, survey, experiment, field study, log analysis | Method cheat sheet (4) | Participants, procedure, analysis, then results and discussion |
| A technical experiment or benchmark (ML, sensing) with datasets and baselines | System cheat sheet (3), with an "Experiment" section (the sample's Evaluation/Study/Data cluster, 39% of papers) | Dataset, setup, metrics, results |
| Both a system and a study of it | System cheat sheet (3), with the study as an embedded Method/Evaluation block | 9 papers have both a System and a Method section |

**System** papers (57) have a top-level System/Design/Implementation section; **method** papers (84) have a top-level Method section and no System section. The 9 papers with both count as system. If unsure, use the whole-sample data in section 5.

## 3. Cheat sheet: system paper

For a new system, tool, device or technique with an evaluation (57 papers).

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

Pages assume about 500 body words per page, the group's median.

**Core checklist.** Percentages are of the 57 papers; words are medians per paper.

| Item | Papers | Median words | What to put in it (*editorial*) |
|---|---|---|---|
| Design goals or requirements | 19% | 452 | The needs or formative findings the design follows from |
| System overview/architecture | 47% | 445 | Components and how they fit, usually with a figure |
| Implementation/interface | 39% | 254 | What others need to reproduce or extend the system |
| Evaluation as a separate section | 53% | 1,581 | What you evaluated, how, against what |
| Embedded study: procedure, participants | 56%, 46% | 685, 204 | Include if the evaluation is a user study |
| Embedded study: materials, analysis, measures | 37%, 35%, 18% | 218, 278, 251 | |
| Results inside the core | 30% | 743 | Instead of a separate Results section |
| Limitations as their own section | 19% | 256 | Most papers fold them into Discussion |

**Figures, tables, references.** Per 1,000 body words, median (Q1–Q3): figures 1.2 (0.7–1.8), one per about 815 words; tables 0.25 (0.07–0.49), one per about 3,150 words; references 8.3 (6.4–10.6). Worked example, 7,000 body words: about 8 figures, 2 tables, 58 references. A figure caption runs 35 words (15–61) and a table caption 15 (9–34); in-figure and in-table text adds about 6.5% of the body. Figure captions take 4.8% of body words in system papers and 1.4% in method papers.

**Common variations.** 61% have a paper-specific section next to the system section. 28% combine Discussion and Conclusion under one heading (heading rule in 5.2). 18% skip Related Work.

**Where the text and citations go.** Results starts after a median of 5,154 body words (Q1–Q3 2,030–6,424; only 16 papers have a separate Results section). About 73% of citations fall in the first half of a paper and 48% in the first fifth. Place most references in the Introduction and Related Work, and a smaller group (about 18%) in the Discussion and Conclusion (5.5).

## 4. Cheat sheet: method paper

For findings from a study: interviews, survey, experiment, field study, log analysis (84 papers).

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

Pages assume about 570 body words per page, the group's median.

**Method checklist.** Percentages are of the 84 papers; words are medians per paper. Items follow the average order inside the Method section.

| Item | Papers | Median words | What to put in it (*editorial*) |
|---|---|---|---|
| Data collection | 20% | 188 | Often merged into the procedure |
| Participants and recruitment | 50% | 208 | Number, selection, demographics |
| Materials, apparatus, stimuli, datasets | 35% | 358 | |
| Study design and procedure | 44% | 571 | Tasks, conditions, protocol |
| Measures, metrics, variables | 24% | 294 | |
| Ethics, approvals, positionality | 21% | 149 | Often placed late in the section |
| Data analysis | 55% | 272 | Almost always last in Method |
| Results as their own section | 80% | 1,810 | 4% keep results inside the core |

**Figures, tables, references.** Per 1,000 body words, median (Q1–Q3): figures 0.5 (0.2–1.2), one per about 1,010 words; tables 0.24 (0–0.54), one per about 3,350 words; references 8.4 (6.6–10.7). Worked example, 5,500 body words: about 3 figures, 1 table, 46 references. A figure caption runs 27 words (13–49) and a table caption 13 (9–29); in-figure and in-table text adds about 4.4% of the body. Tables are mostly demographics, themes and statistics.

**Common variations.** 38% add a paper-specific section; 35% combine Discussion and Conclusion under one heading (heading rule in 5.2); 23% skip Related Work; 20% skip Results as a section. Method and Results appear together (phi +0.51).

**Where the text and citations go.** Results starts after a median of 2,610 body words (Q1–Q3 1,963–5,201), about 49% of the way through. About 73% of citations fall in the first half of a paper and 48% in the first fifth. Place most references in the Introduction and Related Work. Method and Results cite little (about 1.5 per 1,000 words); citations rise again in the Discussion and Conclusion, which hold about 18% (5.5).

## 5. Reference data for the whole sample

### 5.1 Paper size

| Measure (Q1 / median / Q3) | All (190) | System (57) | Method (84) |
|---|---|---|---|
| Pages | 7 / 8 / 21 | 7 / 17 / 24 | 7 / 8 / 20 |
| Body words | 3,460 / 5,290 / 10,900 | 3,455 / 9,071 / 11,121 | 3,905 / 5,550 / 11,336 |
| Total words including references | 5,340 / 7,416 / 15,051 | 4,633 / 11,086 / 14,473 | 5,060 / 7,401 / 14,929 |
| References | 34 / 54 / 84 | 39 / 58 / 82 | 33 / 54 / 92 |
| Body words per page (median) | 536 | 499 | 569 |
| Core words | 1,180 / 2,237 / 4,260 | 1,923 / 3,941 / 5,861 | 931 / 1,456 / 2,957 |
| Core subsections | 3 / 6 / 10 | 5 / 9 / 13 | 3 / 4 / 7 |

### 5.2 Sections, order and headings

**Required slots:** Introduction, a core, a Discussion or Conclusion, and References; every other slot is optional. Order varies enough that the template is a set of slots: only 12 papers (6%) match the textbook sequence exactly.

**Abstract > Introduction > Related Work/Background > CORE > Results/Findings > Discussion (with Limitations/Future Work) > Conclusion > Acknowledgments > References**

Words per slot, with the share of papers that have it:

| Slot | All: papers | All: words Q1 / median / Q3 | System: papers, median | Method: papers, median |
|---|---|---|---|---|
| Abstract (keywords and CCS add about 22 words) | 86% | 140 / 151 / 163 | 74%, 153 | 93%, 151 |
| Introduction | 97% | 510 / 678 / 879 | 95%, 736 | 100%, 696 |
| Related Work/Background | 74% | 620 / 1,062 / 1,467 | 82%, 1,105 | 77%, 1,056 |
| Core (Method, System, Evaluation, custom sections; summed) | 98% | 1,194 / 2,278 / 4,605 | 100%, 3,941 | 100%, 1,456 |
| Results/Findings | 51% | 1,075 / 1,726 / 2,878 | 28%, 1,894 | 80%, 1,810 |
| Discussion (with Limitations/Future Work) | 62% | 592 / 1,310 / 2,313 | 61%, 1,145 | 70%, 1,674 |
| Conclusion (incl. combined "Discussion and Conclusion") | 89% | 126 / 210 / 448 | 89%, 166 | 93%, 231 |
| Acknowledgments | 74% | 27 / 46 / 75 | 77%, 48 | 69%, 44 |

**Order.** In 155 of 190 papers (82%) no slot appears before an earlier one, and 146 (77%) also have the required slots. When a paper has both sections, the order is: Introduction before Related Work 120/120; Method before Results 71/71; Results before Discussion 66/66; Discussion before Conclusion 85/85; Conclusion before Acknowledgments 95/95; System before Evaluation 27/31. Limitations usually sit between Discussion and Conclusion. The system section starts about 40% of the way through the paper, after Related Work (or after the Introduction when there is no Related Work).

**Heading names.** Most common top-level headings (case-insensitive). A conventional name is the safe choice:

| Role | Conventional names (papers) | Less common |
|---|---|---|
| Introduction | Introduction (177) | Introduction and Background (2–4) |
| Related Work | Related Work (102) | Background (21), Background and Related Work (9), Literature Review (2) |
| Method | Methods (29), Method (24), Methodology (23) | Study Design (4), Procedure |
| Results | Results (43), Findings (39) | Results and Discussion (3), Preliminary Results |
| Discussion | Discussion (about 100) | Discussion and Future Work (10), Discussion and Conclusion (11) |
| Conclusion | Conclusion (about 120), Conclusions (8) | Conclusion and Future Work (9) |

Prefer the standard name in the table. Choose one form for the ending: separate Discussion and Conclusion sections, or one combined heading; papers use one or the other (phi about −0.5).

### 5.3 Figures, tables and references

Rates use body words; one paper with no usable body is excluded (n = 189). A paper's reference count is the highest numbered `[n]` entry in its list.

| Measure (Q1 / median / Q3) | All | System | Method |
|---|---|---|---|
| Figures per paper | 2 / 5 / 9 (mean 6, max 29) | 5 / 8 / 10 (mean 8.9) | 1 / 4 / 9 |
| Tables per paper | 0 / 2 / 3 (mean 2, max 20) | 1 / 2 / 4 (mean 2.5) | 0 / 2 / 3 |
| Words per figure caption | 14 / 28 / 55 | 15 / 35 / 61 | 13 / 27 / 49 |
| Words per table caption | 9 / 16 / 33 | 9 / 15 / 34 | 9 / 13 / 29 |
| Figures per 1,000 body words | 0.35 / 0.84 / 1.36 | 0.69 / 1.2 / 1.8 | 0.19 / 0.52 / 1.2 |
| Tables per 1,000 body words | 0 / 0.24 / 0.51 | 0.07 / 0.25 / 0.49 | 0 / 0.24 / 0.54 |
| Small-font text (cells, labels, footnotes) / body words | 0.033 / 0.057 / 0.089 | 0.039 / 0.065 / 0.104 | 0.030 / 0.044 / 0.069 |
| References per 1,000 body words | 6.5 / 8.6 / 11.4 | 6.4 / 8.3 / 10.6 | 6.6 / 8.4 / 10.7 |

Rules of thumb: the reference list takes about a fifth of all words (0.216), at about 35 words per entry. Captions plus in-figure and in-table text add roughly 10% to the body.

### 5.4 Words before Results

Body words from the abstract to the start of a top-level Results/Findings section; 96 papers (51%) have one.

| Measure | Q1 / median / Q3 | Mean | Min–max |
|---|---|---|---|
| Words before Results | 1,913 / 2,618 / 5,238 | 3,673 | 941–8,561 |
| Share of the paper's body words | 42% / 49% / 59% | 51% | 21–78% |
| Words from Results to the end (before references) | 1,790 / 3,216 / 5,441 | 3,706 | 545–9,485 |

The distribution has two clusters, matching short extended abstracts and full papers: about 50 papers have 1,000–3,000 words before Results and about 40 have 4,000–8,000.

| Type | Papers with Results | Words before Results (Q1 / median / Q3) | Share of body (median) | Core (median) |
|---|---|---|---|---|
| Method | 67 of 84 | 1,963 / 2,610 / 5,201 | 49% | 1,255 |
| System | 16 of 57 | 2,030 / 5,154 / 6,424 | 53% | 3,357 |

The system row rests on 16 papers. Of the 94 papers with no Results section, 88 have a Discussion, Conclusion or Limitations section. In those 88, a median of 3,838 words (Q1–Q3 2,815–8,242), about 83% of the body, comes before it, because the evaluation sits inside the core.

### 5.5 Citation distribution

Counts cover numbered in-text citations (`[12]`, `[3, 7]`, `[4–6]`; lists and ranges expanded) between the Introduction and the References heading, in all 190 papers. The first half is the first 50% of words.

| Measure (Q1 / median / Q3) | First half | Second half |
|---|---|---|
| Citations, each reference counted separately | 32 / 62 / 106 (mean 72, max 259) | 10 / 22 / 36 (mean 29) |
| Citations per 1,000 words | 13.2 / 18.2 / 23.2 | 3.5 / 6.0 / 10.9 |

- A median of 73% of a paper's citations (Q1–Q3 63–84%) fall in the first half; 168 of 190 papers cite more in the first half. Each paper has at least 4 there.

By tenth of the paper's words:

| Tenth | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th | 9th | 10th |
|---|---|---|---|---|---|---|---|---|---|---|
| Share of all citations | 24.9% | 22.8% | 12.5% | 6.7% | 4.8% | 3.6% | 3.3% | 3.8% | 9.6% | 8.0% |
| Median citations per 1,000 words | 28.3 | 27.7 | 15.1 | 6.5 | 3.3 | 1.5 | 1.5 | 2.0 | 10.3 | 9.3 |

The first fifth (Introduction and Related Work) holds 47.7% of all citations at about 28 per 1,000 words. Citations drop to about 1.5 per 1,000 words in the sixth and seventh tenths (Method and Results), then rise to about 10 per 1,000 words in the last fifth (Discussion and Conclusion), which holds 17.6%.

## 6. How the numbers were produced, and their limits

Extraction: `pdftohtml -xml` gave text and font data for each PDF; bold numbered lines marked headings; words were counted per section, with subsections rolled into their top-level section; captions and small-font text were counted separately; appendices after the References were left out. The analysis scripts were scratch files and are not kept in the repo.

- Section classes come from heading keywords; 13 papers have no heading recognised as plain "Introduction" (mostly "Introduction and Background" variants, counted under Introduction).
- Without a bold Abstract heading, a paper's abstract is counted in front matter.
- PDF text does not separate table cells from figure labels, so "small-font text" covers both plus footnotes.
- Core component percentages depend on a keyword classifier; 70% of papers also have unclassified paper-specific subsections. The system group is small (57), so rare slots there (Results 16 papers, Method 9) are rough.
- The method group is a keyword-defined cut and includes some technical experiment papers alongside human-subjects studies.
- Word counts are approximate to a few percent.
- Only numbered `[n]` citations count. The tenths in 5.5 follow word position, including figure and table text, so they approximate where sections fall.
- The sample is one publisher's HCI-adjacent papers; apply the numbers to ACM HCI, ubiquitous-computing and CSCW papers, not to other fields.
