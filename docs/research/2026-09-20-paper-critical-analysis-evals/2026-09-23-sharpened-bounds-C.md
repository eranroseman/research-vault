# Critical analysis: Abbonato (2026), "CheckIfExist: Detecting Citation Hallucinations in the Era of AI-Generated Content"

|                    |                                                                                                                 |
| ------------------ | --------------------------------------------------------------------------------------------------------------- |
| **Title**          | CheckIfExist: Detecting Citation Hallucinations in the Era of AI-Generated Content                              |
| **Authors**        | Diletta Abbonato (sole author, corresponding), Department of Culture, Politics and Society, University of Turin |
| **Venue / Status** | arXiv preprint, arXiv:2602.15871v1 [cs.CL]; no journal or conference named                                      |
| **Year**           | 2026                                                                                                            |
| **Domain**         | Computational linguistics (cs.CL) / scientometrics / research-support tooling                                   |
| **Paper Type**     | Systems (tool) paper                                                                                            |
| **Length**         | 9 pages, no appendix or supplement                                                                              |

Written for a reader deciding whether to trust and use this paper. Referee concerns — publishability, questions to the author, revision requests — are out of scope. **Web access was not available for this run**, so every web-dependent slot reads "not checked: no web access" and is listed under "What this report did not check". Locations follow one convention: the section, then the paragraph counted from the start of that section (page added where the section spans pages), or the algorithm line, figure, table, or equation number.

## 1. Context

**Title.** "CheckIfExist: Detecting Citation Hallucinations in the Era of AI-Generated Content" — short, and the tool name plus subtitle tells a reader what to expect: software that checks whether a cited work exists. The subtitle's second half ("in the Era of AI-Generated Content") is framing rather than content. A reader taking "Detecting" at face value will expect a measured detection rate; what the paper delivers is the design of a detector.

**Authors and affiliations.** One author, Diletta Abbonato, marked corresponding (diletta.abbonato@unito.it), at the Department of Culture, Politics and Society, University of Turin. Single-author, single-institution, single-department, so author order carries no information. The department is a social-sciences department, while the paper is filed under cs.CL and describes a React/TypeScript application — a combination that reads as scientometrics done from a social-science base rather than an NLP-group product. No prior work by the author is cited (0 of 23 references include the author; derived from the reference list, pages 8–9). How well known the institution or the author is in this area, and what they have done before, is **not checked: no web access**.

**Venue.** arXiv preprint, arXiv:2602.15871v1 [cs.CL], page 1 margin. No journal or conference is named, and there is no submission or acceptance statement. On the Source types scale this is the weakest rung: an electronic preprint with no mandatory quality control, so nothing in the paper has been through peer review, and every claim in it rests on the text itself. That matters more than usual here, because the paper's own motivating example is fabricated citations surviving three or more reviewers at NeurIPS (Sec 1 para 3, p2) — a preprint has not had even that filter. The predatory-venue check does not apply to arXiv. One oddity, recorded as read: the identifier prefix 2602 encodes February 2026 while the stamp on the same line reads 27 Jan 2026; page 1 was not rendered to an image, so this rests on the text extraction alone (see "What this report did not check").

**Motivation.** Strong and well-organized, and the best part of the paper. Section 1 paras 2–3 and Section 2 paras 1–3 build the case in three moves: citations are the verification substrate of science (Garfield, 1972; Merton, 1973); that substrate already carries a 25–54% reference-error rate (Sec 2 para 1, p2); and LLM fabrication is a categorically different generator of error — "systematic fabrications emerging from statistical regularities in language generation rather than from engagement with actual sources" (Sec 2 para 2, pp2–3) — with documented rates of 6% to over 30% (Sec 2 para 2, p3, citing Agrawal et al., 2024). Section 2 para 3 adds an economic frame: generation cost has collapsed to near zero while verification cost has not, a cost asymmetry the paper calls "a classic market failure". The contribution is stated plainly in Sec 1 para 1 and again in Sec 1 para 5. What the paper does not do is give an overview of the rest of itself: there is no roadmap paragraph anywhere, so a reader reaches Section 3 without being told that no evaluation is coming.

**Related work.** There is no Related Work section. Prior work is handled in two places: Sec 1 para 4 (p2), which covers reference managers and bibliographic databases and one sentence on commercial hallucination-detection services; and Sec 4.1 (p7), which is a feature table against four reference managers. The treatment synthesizes rather than lists in Sections 1–2 — the citation-error, citation-propagation and LLM-hallucination literatures are woven into an argument, not enumerated — but the gap it identifies ("these systems are fundamentally designed for organization rather than validation", Sec 1 para 4) is identified against the wrong comparison set. The nearest prior art is automated bibliography checking, and the paper cites a paper of exactly that kind — Dunford et al. (2024), "Using automated analysis of the bibliography to detect potential research integrity issues" — twice (Sec 1 para 3; Sec 2 para 2), both times for the difficulty of manual detection, never as a prior automated approach to compare against (N32). Balance of recent and foundational sources is good: 12 of 23 references are 2023 or later and 7 predate 2010 (derived from the reference list, pages 8–9).

- *Tree backward*: following the reference list to what the paper is built on gives Garfield (1972), Merton (1973), MacRoberts and MacRoberts (1996) for the scientometric frame; Hendricks et al. (2020), Ammar et al. (2018), Priem et al. (2022) for the three databases queried — each the database's own descriptor paper, which is the right primary source for a coverage claim; and Ji et al. (2023), Alkaissi and McFarlane (2023), Agrawal et al. (2024) for hallucination. These are the obvious rather than idiosyncratic choices for each of those three roles. That they are the field's *recognized* foundational references is recall on my part, not a check against a citation index, and is quarantined under "What this report did not check".
- *Tree forward*: **not checked: no web access.**

**References check.** 23 references (pages 8–9). By type, counted from the entries: 18 journal articles, 2 conference proceedings (Agrawal et al., 2024; Ammar et al., 2018), 1 book (Merton, 1973), 1 arXiv preprint (Priem et al., 2022), and 1 press article (Goldman, 2026, Fortune) — 23 total (derived). Span 1972–2026, 54 years (derived). The preprint is labeled as such ("arXiv preprint arXiv:2205.01833"); reviews are not labeled by the reference list, and are identifiable only from their own titles — Ji et al. (2023) "Survey of hallucination…", Wager and Middleton (2008) "…A systematic review", Taşkın (2025) "…An Annual Review of Information Science and Technology (ARIST) paper". Self-citations: 0 of 23 (derived). Same-institution citations: **not checked: no web access**. Primary sources are used where it matters most — the three database papers, and Garfield and Merton in the original rather than through a secondary summary. The two paper locations at which a cited source's own title does not reach the claim attached to it carry appendix entries C12, C13 and C14, and the load-bearing motivating statistic rests on a press article rather than the report that press article describes (N26). Whether the 23 references exist, and whether their metadata, volumes, page ranges and DOIs are correct, is **not checked: no web access** — one internal signal is in the appendix as C15. Whether I recognize any of these papers is recall, quarantined under "What this report did not check".

## 2. Summary

**Problem.** The paper sets out to close one specific gap: a researcher who has a bibliographic reference in hand — typed by a person, imported from a PDF, or produced by a language model — has no fast, free way to learn whether the cited work exists. Sec 1 para 4 (p2) names the two existing routes and why each fails for this purpose: reference managers (Zotero, Mendeley, EndNote, JabRef) "store the provided metadata without verifying its authenticity", so "a hallucinated reference with a fabricated DOI, non-existent journal, or invented author will be catalogued alongside legitimate citations without any indication of its spurious nature"; and bibliographic databases (Web of Science, Scopus, Google Scholar) can verify a reference but only through "manual querying of each citation—a process that scales poorly and interrupts the writing workflow". A third route, commercial hallucination detection, is said to sit behind restrictive freemium limits or subscriptions. The objective, stated in Sec 1 para 5 (p2), is "instant verification of reference authenticity through real-time queries to multiple scholarly databases… returning validation results within seconds". There are no research questions and no hypotheses; this is an engineering objective, and the paper is explicit about that framing.

**Method.** No family from the Method menu fits: there is no experiment, correlational observation, survey, archival study, or qualitative design, because there is no study. On the calibration table this is a **Systems** paper — a tool description — and it should be read against that row's bar: architecture decisions, scalability evidence, real-world deployment, engineering contributions. The paper has no evaluation, so there is no evaluation family to name either (N1); the Summary slots from `references/experiment-design.md` and `references/qualitative-methods.md` therefore have nothing to summarize, and what follows is the method in the only sense the paper offers it — the process the software follows.

The system is "a web-based application using React with TypeScript" in four modules: input preprocessing for LaTeX command filtering, BibTeX parsing, a multi-source search service, and a presentation layer (Sec 3 para 1, p3). The verification procedure, from Algorithm 1 (p4) and Figure 1 (p5):

1. Filter LaTeX commands from the query (Algorithm 1 line 1; Sec 3 para 3, pp3–4, naming `\vspace`, `\hspace`, `\textit` and custom macros).
2. Query CrossRef for the top 3 candidates (Algorithm 1 line 2); if CrossRef returns nothing, take candidates from Semantic Scholar instead (lines 3–5).
3. Pick a best candidate and score it, then detect issues (lines 6–7).
4. If that score is below 70 or any issue was found, run the fallback: query Semantic Scholar and OpenAlex, extract each source's author set, intersect the three sets into `confirmedAuthors`, and take the rest of the union as `suspectAuthors` (lines 8–19). Two or more confirmed authors adds 10 to the score and merges metadata across the three sources into a corrected record (lines 21–24); a non-empty `suspectAuthors` adds a "Potential fabricated authors" issue (lines 26–28).
5. Compute the final confidence from score and issues, generate APA and BibTeX outputs, and return `{exists : bestScore > 50, confidence, issues, apa, bibtex, sources}` (lines 30–32).

Matching is Levenshtein-based: `similarity(a, b) = 1 − lev(a, b)/max(|a|, |b|)` (Eq. 1, p6), over strings normalized by lowercasing and removing non-alphanumeric characters (Sec 3 para 6, p6). Author matching extracts family names from the primary source's metadata, checks each for presence in the query string, takes author similarity as "the proportion of matched authors", and flags as potentially fabricated any "capitalized tokens in the query that match neither title words, journal name, year, nor any real author family name" (Sec 3 para 7, p6). Confidence has two stated forms: `confidence = S_title − 0.5 × (100 − S_author)` when title similarity exceeds 80% but author similarity falls below 90% (Eq. 2, p6), and the four-field average `(S_title + S_author + S_journal + S_year)/4 + β_ms` with `β_ms ∈ [0, 10]` "for structured input with high matching across all fields" (Eq. 3, p6). Penalties: title mismatch −20, author mismatch −20, journal discrepancy −10 to −20, each detected fake author −10 to −20 (Sec 3 para 8, p6). Footnote 2 (p6) says the thresholds and penalties "were empirically calibrated to optimize discrimination between valid references and known hallucinations, with author-related discrepancies weighted more heavily given their stronger diagnostic signal for detecting AI-generated fabrications".

What this choice of method implies about what the results can show is simple and worth stating plainly: a design description can show that a mechanism is coherent and implementable. It cannot show that the mechanism works, how often it is right, or how it fails — those need a labeled set and a measurement, and the paper has neither.

**Results.** There are no results to summarize in the usual sense. The paper reports no data, no descriptive statistics, no tables of measurements, no charts of outcomes, and no inferential statistics; `references/quantitative-results.md`'s reading-the-numbers and analysis–design-alignment checks have nothing to apply to. What the paper presents in the results position is functional description and one comparison table.

The functional description (Sec 4, pp6–7) covers: a unified input area with a mode switch; a quick-check mode accepting free-form citation text "in any standard format (APA, MLA, Chicago, etc.) or informal reference descriptions", returning "results within seconds of query submission"; a batch mode accepting BibTeX entries or newline-separated citation lists, processing "entries sequentially with rate limiting (800ms intervals) to comply with API usage policies", with a progressive results view; and, per verified reference, APA 7 citations and valid BibTeX records with generated citation keys, derived "from authoritative metadata retrieved from the scholarly databases rather than potentially erroneous input", plus file-download and clipboard-copy export of all corrected entries.

The comparison (Table 1, p7) is a 13-row feature matrix over CheckIfExist, Zotero, Mendeley, EndNote and JabRef, marking each cell ✓ or –. CheckIfExist carries ✓ on all six validation-specific rows (Immediate validation, Hallucination detection, Fake author detection, Batch verification, Multi-source validation, Corrected BibTeX output), where all four managers carry –, and – on three organization rows (Reference organization, Word processor integration, Cloud synchronization) where all four carry ✓ except JabRef on synchronization. The table's source is not given (N24). Sec 4.1 para 2 (p7) reads the table as showing that "the proposed system occupies a complementary position within the reference management ecosystem": it "does not seek to replace comprehensive tools like Zotero but rather provides a specialized verification capability that these tools lack", with a stated workflow of exporting a Zotero library as BibTeX, validating it, and reimporting corrected records.

**Discussion.** The paper has no Discussion section; interpretation lives in Section 5 Conclusions (pp7–8). Section 5 para 1 lists five use cases — authors validating reference lists before submission, researchers checking LLM-suggested citations, reviewers auditing manuscripts under review ("identifying potential fabrications warranting author clarification"), publishers integrating validation into submission pipelines "with the multi-source validation providing higher confidence than single-database checks", and bibliometricians filtering spurious references from datasets. Section 5 para 2 restates the contribution: a "practical, open-source solution for immediate bibliographic reference validation through multi-source verification", complementing rather than replacing existing managers, "filling a specific gap in the scholarly toolkit", and closes on freely accessible tools supporting human judgment as AI writing assistants spread. The author offers no explanation of why any result came out as it did, because there are no results to explain, and the advance in knowledge is claimed as a tooling advance rather than a finding.

The conclusion summarizes the motivation, the architecture and the claimed value, but not methods or results in the sense the outline asks about — there being none of the latter. Three things the outline expects are absent outright: **no stated limitation of any kind** (N30), **no future work** (N31), and **no acknowledgements, funding, or conflict-of-interest statement** anywhere from the Abstract through Availability (N27, N28, N29). The only post-conclusion material is a two-line Availability statement: MIT License, at `https://zabbonat.github.io/References-Validation/` (p8).

## 3. Discussion

### Importance

The problem is real, sharply motivated, and worth tooling, but the contribution the paper actually delivers is a described artifact rather than a demonstrated detector, and the title's promise ("Detecting Citation Hallucinations") outruns what the paper establishes about it.

**Point 1 — Not reported.**

- **Location**: Title; Abstract; Sec 5 para 2 (p8).
- **Observation**: The title claims hallucination detection and the Abstract claims the tool delivers "instant feedback on reference authenticity"; no detection outcome of any kind — accuracy, precision, recall, false-positive rate — appears anywhere in the paper.
- **Evidence or criterion**: N1.
- **Why it matters**: A reader who cites this paper as evidence that automated hallucination detection works would be citing a design document. The stated question (Sec 1 para 1, "real-time validation") is answered by a description; the title's question is not answered at all.

**Point 2 — Not reported.**

- **Location**: Sec 1 para 3 (p2); Sec 5 para 1 (pp7–8).
- **Observation**: The paper's entire motivation is a concrete, enumerated corpus of hallucinated citations ("more than 100 AI-hallucinated citations across at least 53 papers" at NeurIPS 2025; "50 hallucinated citations" at ICLR), and it is used as the reason reviewers need the tool — yet the tool is never run on any of them.
- **Evidence or criterion**: N44; N1.
- **Why it matters**: The cheapest possible validation of the claimed contribution was in the author's hands and was skipped, which leaves the gap between "a problem exists" and "this tool addresses it" entirely unbridged.

**Point 3 — Not reported.**

- **Location**: Sec 1 para 3 (p2); References p9 (Goldman, 2026, *Fortune*).
- **Observation**: All four headline motivating figures ("over 4,000 research papers", "more than 100 AI-hallucinated citations across at least 53 papers", "50 hallucinated citations" at ICLR, "an acceptance rate of 24.52% from over 21,500 submissions") trace to a single trade-press article whose own listed title says "new report claims"; the report itself is never cited.
- **Evidence or criterion**: N26.
- **Why it matters**: In a paper whose subject is verifiable citation, the load-bearing empirical premise is not verifiable from the paper — the reader must trust a secondary press summary of an uncited primary source.

**Point 4 — Not reported.**

- **Location**: Sec 2 para 3 (p3).
- **Observation**: The paper's sharpest idea — the cost asymmetry between near-zero-cost fabrication and substantial verification cost, framed as "a classic market failure" with negative externalities distributed "across the entire scholarly community" — is developed only in prose and carries no quantity, no model, and no measurement.
- **Evidence or criterion**: Sec 2 para 3 (p3); N1.
- **Why it matters**: This is the part of the paper most likely to be worth citing, and it is the part offered with the least support; a reader cannot use the framing to estimate how much verification effort the tool would actually displace.

### Credibility

Treat this as a low-credibility evidentiary document and a moderate-credibility engineering sketch: nothing about the tool's behavior can be checked from the paper, the method is specified three times in three mutually inconsistent ways, and the one empirical procedure the paper asserts was performed is nowhere reported.

**Point 1 — Not reported.**

- **Location**: Sec 3 para 2, last sentence (p3); Sec 5 para 1 (pp7–8).
- **Observation**: There is no Evaluation section and no reported measurement of any kind. The claim that the cascade "achieves higher recall than any single-source approach while maintaining precision through multi-source confirmation" and the claim of "higher confidence than single-database checks" are asserted immediately after narrative about coverage gaps.
- **Evidence or criterion**: N1; `experiment-design.md` reporting red flags ("missing methodological details", "results don't match methods"); `quantitative-results.md` order of assessment, which cannot be entered at step one because the target quantity is never defined.
- **Why it matters**: "higher recall" and "maintaining precision" are quantitative claims about a classifier. With no labeled set, no per-source figures, and no cascade figures, the conclusions cannot be correct or incorrect — they are untested, and the paper presents them in the grammar of findings.

**Point 2 — Integrity concern, stated neutrally.**

- **Location**: footnote 2 (p6); Sec 3 para 8 (p6).
- **Observation**: The footnote states that "Threshold and penalty values were empirically calibrated to optimize discrimination between valid references and known hallucinations, with author-related discrepancies weighted more heavily given their stronger diagnostic signal for detecting AI-generated fabrications." No calibration set, provenance of the "known hallucinations", procedure, objective function, or resulting discrimination appears anywhere in the paper. The same footnote's claim of heavier author weighting is not borne out by the penalty list in the paragraph it annotates, where title mismatches and author mismatches are both −20.
- **Evidence or criterion**: N2; C11.
- **Why it matters**: The footnote asserts that an empirical procedure was carried out and reports none of it, and the one checkable detail inside it does not hold. A plausible benign explanation is informal hand-tuning during development, described loosely and compressed into a footnote in a short tool paper. This is recorded as a discrepancy between an asserted procedure and the paper's contents, with the uncertainty stated — not as a finding about the author.

**Point 3 — Demonstrated inconsistency.**

- **Location**: Sec 3 para 2 (p3) vs Algorithm 1 lines 18–19 and 26–27 (p4).
- **Observation**: The text says multi-source lookup exists because "no individual scholarly database achieves complete coverage of the academic literature". The pseudocode defines `confirmedAuthors` as the *intersection* of all three sources' author sets and flags every author outside that intersection as potentially fabricated. A genuine reference absent from any one of the three indexes therefore has an empty intersection, and all of its real authors receive a "Potential fabricated authors" issue.
- **Evidence or criterion**: C3; C4.
- **Why it matters**: The single mechanism the paper advertises as its detection contribution converts the coverage gap the design is supposed to absorb into a fabrication accusation. This is the most consequential defect in the paper, and it is visible in the pseudocode without any experiment.

**Point 4 — Potential design problem (construct validity).**

- **Location**: Sec 1 para 3 (p2); Eq. 1 (p6); Sec 3 para 6 (p6); Figure 1 node "Title Similarity (Levenshtein)" (p5).

- **Observation**: The paper names the hard case itself: hallucinations that are "subtle alterations of real papers, such as expanding author initials into guessed first names or paraphrasing titles". The tool's title measure is normalized character-level Levenshtein similarity (Eq. 1) over strings lowercased with non-alphanumerics removed. Expanding author initials does not touch the title, so title similarity is unaffected. Recomputed from Eq. 1 on titles taken from the paper's own reference list (**derived**; normalization as stated in Sec 3 para 6):

  | Edit                                             | From → to                                                                                                         | Eq. 1      |
  | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- | ---------- |
  | one letter, long title                           | "Survey of hallucination in natural language generation" → "Survey of hallucinations in…"                         | 97.96%     |
  | article added + pluralized                       | → "A survey of hallucinations in natural language generation"                                                     | 96.00%     |
  | preposition swapped                              | "Problems of citation analysis" → "Problems in citation analysis"                                                 | 92.31%     |
  | **one content word swapped, changing the claim** | "Accuracy of references in five leading medical journals" → "…three leading medical journals"                     | **91.84%** |
  | same one-word swap, short title                  | "Read before you cite!" → "Read before you write!"                                                                | 88.89%     |
  | genuine paraphrase, long title                   | "Accuracy of references in five leading medical journals" → "Reference accuracy in five leading medical journals" | 64.58%     |
  | genuine paraphrase, short title                  | "Read before you cite!" → "Read before citing"                                                                    | 64.71%     |
  | **benign appended subtitle**                     | "Problems of citation analysis" → "…in the social sciences"                                                       | **57.78%** |
  | **title truncated at half**                      | "Construction of the literature graph in Semantic Scholar" → "Construction of the literature"                     | **55.10%** |

- **Evidence or criterion**: Eq. 1 (p6); Sec 3 para 6 (p6); Sec 1 para 3 (p2); N34; derived.

- **Why it matters**: The metric scores a title that has been altered into a *different claim* at 91.84% while scoring a genuine reference with a subtitle appended at 57.78% and a truncated genuine title at 55.10% — below the values that light-touch fabrications receive. It is blind by construction to the initials-expansion case the paper singles out, and the same edit costs more in a short title (88.89%) than in a long one (97.96%), so sensitivity depends on title length, which the paper never discusses. The construct the tool measures — "does a sufficiently similar record exist in an index?" — is not the construct the title claims — "is this citation a hallucination?" — and the two diverge in exactly the direction that matters.

**Point 5 — Potential design problem (base rate neglect).**

- **Location**: Sec 1 para 3 (p2); Sec 5 para 1 (pp7–8).
- **Observation**: The paper proposes reviewer and publisher screening while reporting no false-positive rate. **Derived**, using only figures the paper gives — 4,000 NeurIPS 2025 papers, more than 100 hallucinated citations (Sec 1 para 3), and 23 references as a bibliography size, this paper's own (References, pp8–9): 4,000 × 23 = 92,000 references, of which >100 are hallucinated, a prevalence of 0.109%. At perfect sensitivity, a 1% false-positive rate yields 919 false flags against 100 true ones (precision 9.8%, 9.2 false flags per true one); at 5% it yields 4,595 false flags (precision 2.1%, 46.0 false per true).
- **Evidence or criterion**: Sec 1 para 3 (p2); References pp8–9; N1; `quantitative-results.md`, "base rate neglect"; derived.
- **Why it matters**: At the prevalence the paper itself establishes, the tool's usefulness as a screen is governed almost entirely by the false-positive rate it never reports. A reader cannot tell whether the output is a useful filter or mostly noise, and the reviewer and publisher use cases are the ones most sensitive to this.

**Point 6 — Potential design problem, walked on the paper's own bibliography.**

- **Location**: Sec 3 para 7 (p6); Sec 3 para 8 (p6); References p9 (Merton, 1973 entry).
- **Observation**: The stated fabricated-author rule flags "capitalized tokens in the query that match neither title words, journal name, year, nor any real author family name". **Derived**, applying that rule verbatim to the paper's own entry "Merton, R. K. (1973). The Sociology of Science: Theoretical and Empirical Investigations. University of Chicago Press.": *Merton* matches an author family name and the title words match the title, leaving *R*, *K*, *University*, *Chicago*, *Press* — five "potential fabricated authors" on a genuine, canonical monograph, carrying −50 to −100 at the stated −10 to −20 each.
- **Evidence or criterion**: Sec 3 para 7 (p6); Sec 3 para 8 (p6); References p9; C10; derived.
- **Why it matters**: Author initials, publishers, and conference-name words are ordinary parts of a citation string, so the detector's false-positive mode is structural rather than incidental — and it is demonstrable on the paper's own reference list without running the tool.

**Point 7 — Demonstrated inconsistency.**

- **Location**: Algorithm 1 lines 30–32 (p4); Figure 1 (p5); Sec 3 para 8 (p6).
- **Observation**: Line 30 computes `confidence` from `bestScore` and `issues`, but line 32 returns `exists : bestScore > 50` — the pre-penalty score, so every penalty the paper describes is irrelevant to the existence verdict. Three thresholds (50 for existence, 70 for fallback, 80 for "Verified") appear across the pseudocode and the figure and are never reconciled in the text, which mentions none of 50, "Verified", or "Partial Match". Line 23 assigns `correctedMetadata` only inside the `|confirmedAuthors| ≥ 2` branch of the fallback branch, while line 31 calls `GENERATEOUTPUTS(correctedMetadata)` unconditionally. The prose, the pseudocode, and the flowchart further disagree on the fallback trigger, the cascade structure, the author-mismatch path, and the empty-CrossRef path.
- **Evidence or criterion**: C1; C2; C6; C7; C8; C9; N17.
- **Why it matters**: The headline output — whether a reference exists — is produced by an unspecified function (`EVALUATECANDIDATES`, N5) of an unspecified score, bypassing the penalty machinery that occupies most of Section 3. Nine separate conflicts between prose, pseudocode, and figure mean no single reading of the method can be checked against the deployed tool.

**Point 8 — Demonstrated inconsistency (citation support, in a paper about citation integrity).**

- **Location**: Sec 1 para 4 (p2); Sec 2 para 1 (p2); References pp8–9.
- **Observation**: Kratochvíl (2017) is cited for the functionality of "Zotero, Mendeley, EndNote, and JabRef" though its own listed title covers "EndNote, Mendeley, RefWorks and Zotero" — not JabRef. Zhu et al. (2025) is cited for commercial services' "restrictive freemium models" though its listed title is "Evaluating the potential risks of employing large language models in peer review". The "error rates ranging from 25% to 54%" are attributed to "studies examining citation accuracy across disciplines" while both cited titles are confined to medicine. Two 2025 entries in the same journal carry volumes 76(6) and 77(1).
- **Evidence or criterion**: C12; C13; C14; C15.
- **Why it matters**: Three citation-support problems and one internal reference-list conflict in a 23-item bibliography suggest the tool was not applied to its own paper, or would not have caught these classes — which are precisely the "subtle alteration" failures the paper says matter most. It also weakens the two comparative premises that the Novelty verdict rests on.

**Point 9 — cross-reference.** Source independence (the +10 multi-source bonus treating CrossRef, Semantic Scholar and OpenAlex as independent corroboration, where Sec 3 para 2 says OpenAlex aggregates CrossRef) bears most on the Assumptions verdict and is recorded there as **A2**.

### Novelty

The engineering combination is sensible and mildly clever in exactly one place — using cross-source author agreement as a fabrication signal — while the rest is an obvious assembly of public APIs and a standard string metric, and the paper's "fills this gap" claim is unsupported rather than false because no prior art was searched.

**Point 1 — Not reported.**

- **Location**: Sec 1 para 4 (p2); Sec 4.1 (p7).
- **Observation**: There is no Related Work section and no search of prior academic or open-source automated citation-existence checkers. Dunford et al. (2024), whose listed title is "Using automated analysis of the bibliography to detect potential research integrity issues", is cited twice (Sec 1 para 3; Sec 2 para 2) for the difficulty of manual detection and for "chimeric" hallucinations, never discussed as a prior automated approach.
- **Evidence or criterion**: N32.
- **Why it matters**: The Abstract's claim that "The proposed tool fills this gap" is a novelty claim broader than the cited literature supports; the paper cites, without engaging, the one reference in its own list whose title describes the same activity.

**Point 2 — Not reported.**

- **Location**: Abstract; Sec 1 para 4 (p2); Sec 4.1 para 2 (p7).
- **Observation**: The competitor category the paper positions against — "Commercial hallucination detection services" — is never named, priced, or dated, and is absent from Table 1.
- **Evidence or criterion**: N23.
- **Why it matters**: Without a single named competitor, a reader cannot determine what is new here relative to the actual competing category, nor check the differentiator ("unlimited free verification") that the paper leans on.

**Point 3 — Potential design problem (comparator selection).**

- **Location**: Table 1 (p7); Sec 4.1 para 2 (p7); Sec 1 para 4 (p2).
- **Observation**: The comparison set is four reference *managers* (Zotero, Mendeley, EndNote, JabRef), which the paper states are "fundamentally designed for organization rather than validation". The six validation rows — immediate validation, hallucination detection, fake author detection, batch verification, multi-source validation, corrected BibTeX output — are therefore checkmarked for CheckIfExist and dashed for all four by construction. The rows are never defined as distinct features, and no versions or audit dates are given.
- **Evidence or criterion**: Table 1 (p7); N33; N24; N25.
- **Why it matters**: A comparison against a category the paper says does not attempt the task cannot establish novelty; it establishes category membership. The feature table reads as a differentiation exercise rather than evidence.

**Point 4 — Demonstrated inconsistency.**

- **Location**: Abstract; Sec 3 para 6 (p6).
- **Observation**: The Abstract describes plural "string similarity algorithms" computing "multi-dimensional match confidence scores"; one algorithm is described — normalized Levenshtein distance.
- **Evidence or criterion**: C17; N42.
- **Why it matters**: The only technical novelty a reader could weigh in the matching layer is overstated in the Abstract relative to Section 3, and the Abstract is what most readers will use to judge whether this is new work.

**Point 5 — Potential design problem (the novel part is the least specified part).**

- **Location**: Sec 3 para 7 (p6); Algorithm 1 lines 18–19 (p4).
- **Observation**: Cross-source author intersection is the paper's one non-obvious mechanism, and it is the mechanism whose specification conflicts with its prose description and inverts its stated purpose.
- **Evidence or criterion**: C3; C4; N10.
- **Why it matters**: There is new information to be learned from this paper — the idea is worth stealing — but a reader cannot reimplement the idea from the paper, so the novelty is directional rather than transferable.

### Applicability

The use case is immediate, the artifact is free, MIT-licensed, and installation-free, so it is worth trying on your own bibliography — but the paper gives you nothing with which to predict how it will behave, and three of the five use cases it proposes require an interface it does not describe.

**Point 1 — Not reported.**

- **Location**: Sec 4 (pp6–7); Sec 3 (pp3–6).
- **Observation**: No worked example, no sample input or output, no screenshot, no trace of a hallucinated reference or a genuine one through the pipeline.
- **Evidence or criterion**: N36.
- **Why it matters**: For a tool paper, the worked example is the applicability evidence. Without it, a practitioner cannot tell what "Partial Match" looks like in practice or how much interpretive work the output leaves them.

**Point 2 — Not reported.**

- **Location**: Availability (p8); footnote 1 (p1); Sec 3 para 1 (p3).
- **Observation**: Only a GitHub Pages URL is given. No software version, release date, source-repository location, dependency list (Levenshtein implementation, BibTeX parser, APA 7 formatter), or tests.
- **Evidence or criterion**: N22.
- **Why it matters**: A reader cannot cite a version, reproduce a result, or audit the matching code against the paper's description — and since behavior depends on three third-party APIs, the tool's output is not stable over time, which makes an unversioned artifact hard to use in any documented workflow.

**Point 3 — Potential design problem.**

- **Location**: Sec 5 para 1 (pp7–8) vs Sec 3 para 1 (p3) and Sec 4 para 2 (p7).
- **Observation**: Three of the five proposed use cases — publisher submission pipelines, large-scale bibliometric filtering, and reviewer auditing at volume — need programmatic access. The described artifact is a browser "web-based application using React with TypeScript" processing entries sequentially at 800 ms intervals, with no API, CLI, batch backend, or concurrency described.
- **Evidence or criterion**: Sec 5 para 1 (pp7–8); Sec 3 para 1 (p3); Sec 4 para 2 (p7); N20; N15.
- **Why it matters**: The use cases with the highest stated value are the ones the described interface cannot serve, and the paper does not flag the mismatch. The wall-clock consequences are in Scalability Points 2 and 3.

**Point 4 — Not reported.**

- **Location**: Figure 1 (p5); Algorithm 1 line 32 (p4); Sec 4 (pp6–7).
- **Observation**: The user-facing states "Verified", "Partial Match", "Corrected Citation", and the "Mismatch" path appear only in Figure 1 and are never described in the text; the text never mentions the existence threshold of 50. What a user sees for a reference with `exists = true` and a score of, say, 65 is not stated.
- **Evidence or criterion**: N39; N17; C6.
- **Why it matters**: A practitioner cannot write a decision rule ("act on these, ignore those") over output categories whose meaning the paper never defines — which is the minimum needed to fold the tool into an editorial or review workflow.

**Point 5 — Not reported.**

- **Location**: Sec 3 para 2 (p3); Sec 4 para 3 (p7).
- **Observation**: The paper states that CrossRef "may lack coverage of preprints, regional journals, or older publications", and never says what the tool outputs for such works, or for books, theses, and reports — whether they are reported as non-existent. **Derived**: 3 of the paper's own 23 references (13.0%) are of exactly these classes — a 1973 monograph (Merton), a 2022 arXiv preprint (Priem et al.), and a 2026 news article (Goldman).
- **Evidence or criterion**: N16; Sec 3 para 2 (p3); References pp8–9; derived.
- **Why it matters**: In the humanities and social sciences — the author's own faculty is Culture, Politics and Society — monographs and grey literature are a large fraction of any bibliography, so the false-"non-existent" rate is the decisive applicability number and is neither reported nor bounded.

**Point 6 — Not reported.**

- **Location**: Sec 4 para 2 (p7).
- **Observation**: The 800 ms rate limit is said to be applied "to comply with API usage policies", but the policies are not named, and API keys, the CrossRef polite pool, Semantic Scholar rate limits, and behavior on API error or timeout are not addressed.
- **Evidence or criterion**: N15.
- **Why it matters**: If a transient API failure is indistinguishable in the output from a genuine non-match, a batch audit silently converts outages into fabrication flags — a failure mode a user must know about before trusting a bibliography report.

### Generalizability

Empirically not assessable — with no evaluation there is no result to generalize; what *can* be assessed is the reach the paper claims for its design, and that reach exceeds what its own statements about database coverage and name handling support.

**Point 1 — Not reported.**

- **Location**: Sec 3 (pp3–6); Sec 4 (pp6–7); Sec 5 (pp7–8).
- **Observation**: There is no result, no sample of references, and no setting in which the tool was exercised, so the external-validity questions in `experiment-design.md` — representativeness of the sample, inclusion criteria, consistency across subgroups — have no object anywhere in the paper.
- **Evidence or criterion**: N1; `experiment-design.md`, external validity.
- **Why it matters**: A reader cannot transfer performance to their discipline, because no performance was established in any discipline. This is the sense in which the dimension is inapplicable; the remaining points concern claimed reach rather than measured reach.

**Point 2 — Potential design problem.**

- **Location**: Sec 3 para 2 (p3) vs Sec 5 para 1 (pp7–8).
- **Observation**: The paper documents its own coverage asymmetries — CrossRef "may lack coverage of preprints, regional journals, or older publications"; Semantic Scholar "provides strong coverage of computer science and biomedical literature"; OpenAlex "offers the broadest coverage… though metadata quality varies" — then proposes the tool for authors, reviewers, publishers, and bibliometricians without discipline restriction.
- **Evidence or criterion**: Sec 3 para 2 (p3); Sec 5 para 1 (pp7–8); N16.
- **Why it matters**: By the paper's own account, performance must vary by field, era, language, and document type. The claimed reach is uniform where the design is explicitly non-uniform, and no subgroup breakdown is offered even in principle.

**Point 3 — Potential design problem.**

- **Location**: Sec 3 para 6 (p6); Sec 3 para 7 (p6).
- **Observation**: Author matching rests on family-name extraction and containment checking, after a normalization step that converts to lowercase and removes all non-alphanumeric characters. Handling of "et al.", initials, diacritics, hyphenated and multi-part family names, and non-Western name order is unspecified. **Derived** from the paper's own reference list: 6 of the cited surnames carry non-ASCII letters (Céspedes, Kratochvíl, Larivière, Rodríguez-Bravo, Świgoń, Taşkın), 2 are hyphenated compounds (Rodríguez-Bravo, Sainte-Marie), and 1 is an unhyphenated two-part family name (Izzo Hunter) — every one of which the stated normalization alters or splits.
- **Evidence or criterion**: N10; Sec 3 para 6 (p6); References pp8–9; derived.
- **Why it matters**: The containment test degrades most for exactly the literature OpenAlex is included to cover better (open-access and "non-English publications", Sec 3 para 2), so the false-fabrication rate is likely to fall unevenly on non-Anglophone authors — a generalizability failure with an equity edge.

**Point 4 — Not reported.**

- **Location**: footnote 2 (p6); Sec 3 para 8 (p6).
- **Observation**: The thresholds 50/70/80, the penalties, and the weights were "empirically calibrated" against an unspecified set of "valid references and known hallucinations".
- **Evidence or criterion**: N2; N13.
- **Why it matters**: Thresholds tuned on an undescribed corpus transfer unpredictably; without knowing the calibration set's discipline, era, and hallucination provenance — which model, which prompting strategy — a reader cannot judge whether the cut-points hold for their own inputs.

**Point 5 — Demonstrated inconsistency.**

- **Location**: Sec 4 para 1 (p6) and Sec 4 para 3 (p7) vs Table 1 (p7).
- **Observation**: Input generalizes across citation styles — "free-form citation text in any standard format (APA, MLA, Chicago, etc.)" — but output is APA 7 and BibTeX only; Table 1 nonetheless awards CheckIfExist "Bibliography formatting ✓" alongside the four managers.
- **Evidence or criterion**: N25; Table 1 (p7); Sec 4 para 3 (p7).
- **Why it matters**: A user in an MLA or Chicago discipline can validate but cannot obtain a usable corrected citation, which narrows the practical reach in a way the feature table conceals.

### Scalability

Single-reference and single-bibliography use scale comfortably by the paper's own rate figure, but the two largest scales the paper claims — publisher submission pipelines and large-scale bibliometric filtering — are contradicted by that same figure, and computational cost is not discussed anywhere.

The paper gives exactly one timing figure: batch mode "processes entries sequentially with rate limiting (800ms intervals)" (Sec 4 para 2, p7). Every rate below is **derived** from it, and from the two corpus sizes the paper states (Sec 1 para 3, p2) and the size of the paper's own bibliography (References, pp8–9, 23 entries). **Derived base rate**: 1 / 0.8 s = 1.25 references/s = 75/min = 4,500/h, single-threaded, one client.

**Point 1 — Supported scale.**

- **Location**: Abstract; Sec 4 para 2 (pp6–7).
- **Observation**: Claim: "batch processing of BibTeX entries" for "comprehensive bibliography audits". **Derived**: this paper's own 23-entry bibliography takes 18 s; a 50-entry article bibliography 40 s; a 200-entry review bibliography 160 s (2.7 min) — rate-limit floor, before network latency.
- **Evidence or criterion**: Sec 4 para 2 (p7); References pp8–9; derived.
- **Why it matters**: This scale holds, and a reader can act on it: a normal bibliography audit is a coffee-break operation, and the largest realistic single bibliography is under three minutes of enforced delay.

**Point 2 — Potential design problem (unsupported claimed scale).**

- **Location**: Sec 5 para 1 (pp7–8), "Publishers can integrate reference validation into submission pipelines".
- **Observation**: **Derived** from the largest submission figure the paper gives (NeurIPS 2025, "over 21,500 submissions", Sec 1 para 3) at 23 references each: 494,500 references = 395,600 s = 109.9 h = 4.6 days of continuous single-threaded wall time. The paper describes no server, no parallelism, no API keys, and no caching.
- **Evidence or criterion**: Sec 5 para 1 (pp7–8); Sec 1 para 3 (p2); Sec 4 para 2 (p7); N20; N15; derived.
- **Why it matters**: One conference-scale submission round consumes four and a half days at the paper's own rate. The claim is feasible only with an architecture the paper does not describe, so as stated it is unsupported.

**Point 3 — Potential design problem (unsupported claimed scale).**

- **Location**: Sec 5 para 1 (pp7–8), "Researchers conducting large-scale bibliometric analyses can filter potentially spurious references from datasets".
- **Observation**: The paper attaches no magnitude to "large-scale", so there is no stated figure to check this claim against — it reads as unsupported on that ground alone. **Derived** against the largest corpus the paper does name, its own motivating one (4,000 NeurIPS 2025 accepted papers, Sec 1 para 3, at 23 references each): 92,000 references = 73,600 s = 20.4 h.
- **Evidence or criterion**: Sec 5 para 1 (pp7–8); Sec 1 para 3 (p2); Sec 4 para 2 (p7); derived.
- **Why it matters**: Bibliometric datasets are routinely far larger than the paper's own motivating corpus, and that corpus alone is already 20 hours of sequential throughput. The same computation is the plainest available explanation for why the motivating corpus was never processed (Importance Point 2), and the paper does not state it.

**Point 4 — Not reported.**

- **Location**: Abstract; Sec 1 para 5 (p2); Sec 4 para 1 (p6) — "within seconds".
- **Observation**: No latency is measured anywhere, and the paper's only timing figure is the 800 ms interval *between batch entries* (Sec 4 para 2), which says nothing about per-reference latency in quick-check mode. What the paper does specify is the number of sequential network round trips: three on the fallback path (Algorithm 1 lines 2, 10, 11), and four when CrossRef returns nothing, since line 4 queries Semantic Scholar and line 10 then queries it again (C9). No per-call latency figure is given for any of them.
- **Evidence or criterion**: Sec 4 para 1 (p6); Algorithm 1 lines 2, 4, 10, 11 (p4); C9; N1.
- **Why it matters**: "Within seconds" is a claim about three to four sequential third-party API round trips whose latency the paper never states, on the path taken for every reference scoring below 70 *or* raising any issue — that is, exactly the interesting cases. With no figure to check it against, the claim is unsupported, and a reader cannot distinguish "instant" from "several seconds per suspicious reference".

**Point 5 — Not reported.**

- **Location**: Sec 3 (pp3–6); Sec 4 (pp6–7).
- **Observation**: No computational cost of any kind is discussed: no CPU or memory figures, no caching or deduplication, no parallelism, no API quota accounting, and no statement of where the bottleneck lies. **Derived**: Levenshtein is O(|a|·|b|) over at most three candidate titles per reference (Algorithm 1 line 2, `rows = 3`), so local compute is negligible beside three network round trips — the system is entirely I/O bound.
- **Evidence or criterion**: Sec 3 para 6 (p6); Algorithm 1 line 2 (p4); derived.
- **Why it matters**: Because the paper never identifies the bottleneck, a reader cannot see that the only lever for scale is API concurrency and quota — which is precisely the lever the paper's "unlimited free" positioning cannot pull.

**Point 6 — Demonstrated inconsistency.**

- **Location**: Table 1 row "Unlimited free usage" (p7) vs Sec 4 para 2 (p7); Sec 1 para 4 (p2).
- **Observation**: The paper criticizes competitors whose free tiers "may limit users to a small number of verifications per day or month", claims "Unlimited free usage ✓" for itself in Table 1, and states in the same section that its own batch mode rate-limits to 800 ms intervals "to comply with API usage policies" that it does not name.
- **Evidence or criterion**: Table 1 (p7); Sec 4 para 2 (p7); Sec 1 para 4 (p2); N15.
- **Why it matters**: The tool's throughput ceiling is set by three third parties the author does not control, and the tool already throttles itself to respect them. "Unlimited" is true of the author's own pricing and not of the system's capacity — a distinction that decides whether any of the high-volume use cases is real.

### Assumptions

The method rests on at least nine premises, none of which the paper states as an assumption — including the load-bearing ones, source independence, existence-equals-indexed, and capitalization surviving normalization — and at least three of them are false as written against the paper's own text.

Walked step by step through Algorithm 1, Figure 1, and Equations 1–3.

**A1 — Existence equals presence in one of three indexes. Not stated as an assumption. Potential design problem.**

- **Location**: Algorithm 1 line 32 (p4), `exists : bestScore > 50`.
- **Observation**: The verdict a user reads as "this reference exists" is a fuzzy-match score against three metadata indexes. Sec 3 para 2 acknowledges coverage gaps but never says the verdict is conditional on them, and the paper never states what is output for uncovered document types.
- **Evidence or criterion**: N16; Sec 3 para 2 (p3).
- **Why it matters**: Every genuine book, thesis, report, regional-journal article, or pre-DOI work absent from all three indexes is reported to the user in the vocabulary of fabrication. The premise fails for a large, identifiable, and disciplinarily concentrated slice of the literature.

**A2 — The three sources are independent. Not stated; contradicted by the paper. Potential design problem.**

- **Location**: Algorithm 1 lines 18, 21–22 (p4); Eq. 3 (p6), β_ms.
- **Observation**: The confirmation bonus and the "multi-source confirmation" language treat agreement across sources as independent corroboration; Sec 3 para 2 states that OpenAlex aggregates data "from CrossRef, PubMed, ORCID, arXiv, and other repositories".
- **Evidence or criterion**: Sec 3 para 2 (p3); Algorithm 1 lines 18, 21–22 (p4).
- **Why it matters**: Corroboration among nested sources is worth less than the +10 bonus implies, so CrossRef–OpenAlex agreement is partly tautological; metadata errors and fabricated authors that propagated from CrossRef into an aggregator are confirmed rather than detected, and the failure mode is silent and systematic.

**A3 — A genuine reference appears in *all three* sources. Not stated; contradicted by the paper's own rationale. Demonstrated inconsistency.**

- **Location**: Algorithm 1 line 18 (p4), the triple intersection; lines 19, 26–27 (p4).
- **Observation**: Only the triple intersection can produce `confirmedAuthors`; every author outside it becomes a `suspectAuthor` and raises a "Potential fabricated authors" issue. This is the premise the paper most explicitly denies in prose while depending on it in code.
- **Evidence or criterion**: C3; C4.
- **Why it matters**: Naming it as a premise is what shows the defect is structural rather than a coding slip — the design cannot both absorb coverage gaps and require triple agreement. The consequence for a reader's trust in the method is recorded as **Credibility Point 3**.

**A4 — Works have at least two authors. Not stated. Potential design problem.**

- **Location**: Algorithm 1 line 21 (p4), `if |confirmedAuthors| ≥ 2`.
- **Observation**: A single-author work can never satisfy this test, so neither the +10 bonus nor `MERGEMETADATA` (line 23) is reachable for it — and by C7 the unconditional `GENERATEOUTPUTS(correctedMetadata)` on line 31 then receives an unassigned variable. **Derived** from the paper's own 23-entry reference list: 6 entries (26.1%) are single-author and 13 (56.5%) have two or fewer authors, for which the test is unreachable or fragile. The paper itself is single-authored.
- **Evidence or criterion**: N40; C7; References pp8–9; derived.
- **Why it matters**: A quarter of a typical bibliography gets no multi-source corroboration and no corrected metadata by construction, and the paper never mentions the case.

**A5 — Capitalized tokens survive to the fabricated-author test. Not stated; contradicted. Demonstrated inconsistency.**

- **Location**: Sec 3 para 7 (p6) vs Sec 3 para 6 (p6).
- **Observation**: Fabricated authors are detected as "capitalized tokens in the query"; the preceding paragraph states that "strings undergo normalization through conversion to lowercase and removal of non-alphanumeric characters" prior to comparison. The paper never says the detector runs on the un-normalized query.
- **Evidence or criterion**: C10.
- **Why it matters**: As written, the flagship fabricated-author detector operates on a string in which no capitalized token exists, so a reader cannot tell whether the mechanism runs at all — and the Merton walkthrough at Credibility Point 6 shows what it does when it does run.

**A6 — Character-edit distance on normalized titles tracks bibliographic identity. Not stated. Potential design problem.**

- **Location**: Eq. 1 (p6); Figure 1 node "Title Similarity (Levenshtein)" (p5).
- **Observation**: Eq. 1 is the paper's only stated identity measure for titles, and the paper offers no argument that character-edit distance tracks bibliographic identity, no threshold justification for it beyond footnote 2, and no discussion of its dependence on title length (N34).
- **Evidence or criterion**: Eq. 1 (p6); N34.
- **Why it matters**: The premise is the one on which every verdict ultimately rests, and it is never argued for. The recomputed values showing where it fails — tolerant of claim-changing edits, intolerant of benign length variation — are at **Credibility Point 4**.

**A7 — CrossRef's relevance ranking puts the true match in the top 3. Not stated. Potential design problem.**

- **Location**: Algorithm 1 line 2 (p4), `rows = 3`; Figure 1 node "Retrieve Top 3 Candidates" (p5).
- **Observation**: Recall is capped by a third party's ranking at k = 3, with no stated ranking criterion and no minimum-relevance floor. For a wholly fabricated query, CrossRef still returns three real works, which are then scored.
- **Evidence or criterion**: N35; N4; N41.
- **Why it matters**: The scorer is never handed an empty candidate set for a fabricated reference, so the system's ability to say "this does not exist" depends entirely on the unspecified score falling below 50 against three real papers — the case that matters most is the one the paper never traces.

**A8 — Journal and year similarities exist and are populated. Not stated. Potential design problem.**

- **Location**: Eq. 3 (p6).
- **Observation**: Neither S_journal nor S_year is defined. **Derived** from Eq. 3 as written, with β_ms ∈ \[0, 10\]: a perfect title and author match with journal and year absent from the input scores (100+100+0+0)/4 = 50, so 50 to 60 — below the 70 fallback trigger and at or barely above the 50 mark; a book with exact title, authors, and year but no journal scores (100+100+0+100)/4 = 75, so 75 to 85, clearing Figure 1's ">80%" Verified gate only if the multi-source bonus exceeds 5.
- **Evidence or criterion**: N11; Eq. 3 (p6); Figure 1 (p5); derived.
- **Why it matters**: Averaging four field similarities silently penalizes every reference type or input format that lacks a journal or a year, so correct references from books, preprints, and informal free-text queries are pushed toward "Partial Match" by the arithmetic rather than by any evidence of a problem.

**A9 — Exactly one scoring formula applies per case. Not stated. Potential design problem.**

- **Location**: Sec 3 para 8 (p6), the Eq. 2 and Eq. 3 conditions.
- **Observation**: Eq. 2 applies "When title similarity exceeds 80% but author similarity falls below 90%"; Eq. 3 applies "For structured input with high matching across all fields"; every other case has no stated formula. **Derived** discontinuity at the boundary, at β_ms = 0: at S_title = 95 and S_author = 89, Eq. 2 gives 95 − 0.5 × (100 − 89) = 89.5; raising author similarity to 90 removes Eq. 2, and Eq. 3 gives (95+90+100+100)/4 = 96.25 if journal and year are perfect but (95+90+0+0)/4 = 46.25 if they are absent — a one-point improvement in author similarity can drop the score by 43.25. **Derived** at the other extreme: Eq. 2 with a perfect title and zero author match returns 100 − 0.5 × 100 = 50, exactly the existence boundary.
- **Evidence or criterion**: N12; N13; N14; C5; Eq. 2 (p6); Eq. 3 (p6); derived.
- **Why it matters**: The scoring surface is undefined over much of its domain and discontinuous at the boundary between its two defined regions, so identical evidence can produce opposite verdicts depending on which branch is taken — and the branch rule is not in the paper.

**A10 — Statistical-test assumptions: inapplicable.**

- **Location**: Sec 3 (pp3–6); Sec 4 (pp6–7); Sec 5 (pp7–8).
- **Observation**: No statistical test, model, or inferential procedure is performed anywhere in the paper, so the parametric-assumption and diagnostic checks in `quantitative-results.md` have no object; likewise the counterfactual, design checks, and variable definitions in `experiment-design.md`, there being no comparison and no measured outcome.
- **Evidence or criterion**: N1; `quantitative-results.md`, assumption diagnostics; `experiment-design.md`, the counterfactual.
- **Why it matters**: Naming this as inapplicable rather than as passing matters: the absence of tests is not a clean bill of health, it is the absence of the evidence those tests would have produced.

### Readability

The prose is fluent, well-organized, and easy to follow sentence by sentence, but the method is specified three times in three mutually inconsistent registers and several symbols are never defined, so the paper reads easily and specifies poorly.

**Point 1 — cross-reference.** That the prose, the pseudocode, and Figure 1 cannot be resolved to a single method (C1, C2, C6, C8, C9) is the central obstacle to reading Section 3, and it bears most on whether the method can be trusted at all; it is recorded as **Credibility Point 7**.

**Point 2 — Not reported.**

- **Location**: Eq. 3 (p6); Sec 3 para 8 (p6); Algorithm 1 lines 6, 7, 23, 30 (p4).
- **Observation**: S_journal and S_year are never defined; the rule producing intermediate β_ms values is never given; "high matching across all fields" is never quantified; and `EVALUATECANDIDATES`, `DETECTISSUES`, `MERGEMETADATA`, and `COMPUTEFINALSCORE` are named without definition.
- **Evidence or criterion**: N5; N6; N7; N8; N11; N13; N14.
- **Why it matters**: Equations that contain undefined symbols are decoration; a reader cannot compute a single score by hand from the paper, which is the minimum a formal presentation should permit.

**Point 3 — Not reported.**

- **Location**: Algorithm 1, Require line and line 32 (p4).
- **Observation**: The "optional expected metadata E" in the Require line is never used in lines 1–32; the `sources` field of the return value is never defined.
- **Evidence or criterion**: N18; N19.
- **Why it matters**: A dead parameter and an undefined return field in a 32-line algorithm suggest the pseudocode was not read against itself, which lowers a reader's confidence that it reflects the deployed code.

**Point 4 — Potential design problem (register).**

- **Location**: Sec 2 paras 1–3 (pp2–3).
- **Observation**: The Background section reaches for "path-dependent vulnerabilities", "sophisticated verisimilitude", "negative externalities throughout the knowledge network", "a classic market failure", "fundamentally altered the calculus", "citation mutation", and "categorically different phenomenon" — two pages of economics-and-sociology register in a nine-page tool paper whose technical content is three API calls and an edit distance.
- **Evidence or criterion**: Sec 2 paras 1–3 (pp2–3).
- **Why it matters**: The prose is more elevated than the contribution, which sets an expectation the System Architecture section then disappoints; the tone is scholarly but not always precise, since several of these phrases carry no referent in the paper — there is no path-dependence model and no market-failure analysis.

**Point 5 — Not reported (structure).**

- **Location**: Sec 5 para 1 (pp7–8).
- **Observation**: There is no Related Work, Evaluation, Limitations, or Future Work section, and the use-case discussion — normally a Discussion or Applications section — is the first paragraph of "Conclusions".
- **Evidence or criterion**: N30; N31; N32.
- **Why it matters**: A reader looking for what the tool cannot do has no place to look, and the organization means the paper's strongest forward-looking claims — publishers, bibliometricians — appear where a reader expects a summary of established results rather than proposals.

**Point 6 — Demonstrated inconsistency (minor).**

- **Location**: Sec 1 para 4 (p2) vs Sec 3 para 2 (p3).
- **Observation**: "DOI" is used on page 2 and "Digital Object Identifier system" appears on page 3 without the acronym ever being attached to the expansion.
- **Evidence or criterion**: C16.
- **Why it matters**: Trivial for this audience, but it is one of several signs that the manuscript was not read end to end for internal consistency — the same class of oversight as the dead parameter and the three-way method conflict.

**Point 7 — Potential design problem (cultural neutrality).**

- **Location**: Sec 3 paras 6–7 (p6).
- **Observation**: The tone is culturally neutral and contains nothing exclusionary; the non-neutrality is in the substance rather than the writing — the name-handling scheme presumes a Western given-name/family-name split and an alphabet without diacritics or compound family names.
- **Evidence or criterion**: N10; Sec 3 para 6 (p6).
- **Why it matters**: A reader assessing whether the paper is culturally neutral should separate the prose, which is, from the method, which is not; and the paper's own discussion of OpenAlex's "non-English publications" coverage makes the omission more visible, not less.

### Ethics

The tool is a good idea pointed at a genuine harm, but the paper shows no awareness of the harm its own output can cause — a "Potential fabricated authors" flag attached to a named living researcher, with no measured false-positive rate — and it carries no limitations, privacy, funding, or conflict-of-interest statement. Human-participant ethics is inapplicable: no people took part and no data was collected from anyone, so the consent, IRB, compensation, deception, and demand-characteristics questions in `references/participants.md` have no object.

**Point 1 — Not reported.**

- **Location**: Sec 5 paras 1–2 (pp7–8).
- **Observation**: There is no limitations section and no acknowledgement of a negative consequence. The two harms the design most obviously produces — a false "non-existent" verdict on a genuine work and a false "fabricated author" flag on a real person — are never named, even though the paper describes both mechanisms that produce them.
- **Evidence or criterion**: N30; `research-integrity.md`, negative-consequence and dual-use awareness.
- **Why it matters**: A verification tool's errors are accusations. A paper that proposes reviewer and publisher screening without discussing its own false-positive behavior leaves its users unprepared for the only outcome that can damage a third party.

**Point 2 — Potential design problem with ethical consequence.**

- **Location**: Algorithm 1 line 27 (p4); Sec 5 para 1 (pp7–8).
- **Observation**: The output is a literal accusation string — `issues ← issues ∪ {"Potential fabricated authors: " + suspectAuthors}` — attached to the names in the user's citation, and the proposed users are reviewers and publishers. C3 and C4 show the rule flags the real authors of any genuine reference missing from even one of the three indexes; the false-positive volume implied by the paper's own figures is at Credibility Point 5, and the Merton (1973) walkthrough is at Credibility Point 6.
- **Evidence or criterion**: C3; C4; Algorithm 1 line 27 (p4); Sec 5 para 1 (pp7–8); N1.
- **Why it matters**: The paper closes by saying the tool should "support human judgment in maintaining citation integrity", but an accusatory label with an unmeasured and structurally high false-positive rate, delivered to reviewers and editors who hold power over the accused, substitutes for judgment rather than supporting it. The most likely real-world harm of this tool is a fabrication allegation against an author whose book or non-English article simply is not in CrossRef.

**Point 3 — Not reported.**

- **Location**: Sec 3 para 1 (p3); Sec 5 para 1 (pp7–8); Availability (p8).
- **Observation**: The intended input is the bibliography of an unpublished manuscript or a manuscript under review. The paper does not say whether queries are issued from the user's browser or a server, whether input is logged or retained, or what is disclosed to third parties — while by construction every reference is transmitted to CrossRef, Semantic Scholar, and OpenAlex.
- **Evidence or criterion**: N20; N21; `participants.md`, privacy and the data plan, applied to the tool's users rather than to study participants.
- **Why it matters**: Pasting a bibliography into the tool discloses the reading list of an unpublished paper, and a reviewer pasting a manuscript's references discloses material under confidential review. Neither user can assess that exposure from the paper, and the disclosure is not optional to the design.

**Point 4 — Not reported.**

- **Location**: Abstract through Availability (pp1–8).
- **Observation**: There is no funding statement, no conflict-of-interest declaration, no acknowledgements, no author-contribution statement, and no statement of any relationship to the databases queried or the tools compared — while the paper makes adverse commercial claims about unnamed competing services.
- **Evidence or criterion**: N23; N27; N28; N29; `research-integrity.md`, "Two red flags: no conflicts-of-interest statement at all".
- **Why it matters**: The named red flag is present. A plausible benign explanation is a single-author, unfunded academic tool released under MIT, where there may be nothing to declare — but the paper's own comparative positioning against unnamed paid competitors is exactly the situation a disclosure line is meant to settle, and its absence leaves the reader to assume rather than to check.

**Point 5 — Not reported (a qualification on an otherwise favourable reading).**

- **Location**: Availability (p8); Sec 5 para 2 (p8); Sec 1 para 4 (p2).
- **Observation**: The tool is MIT-licensed, free, publicly hosted, and framed as complementing rather than replacing existing infrastructure and as supporting human judgment — a defensible and equity-conscious direction, explicitly motivated by researchers "in resource-constrained environments". The qualification: "support human judgment" is in tension with a binary `exists` verdict and with intermediate labels ("Partial Match", "Corrected Citation") that the paper never explains.
- **Evidence or criterion**: Availability (p8); Sec 5 para 2 (p8); Sec 1 para 4 (p2); N39; N17; C6.
- **Why it matters**: The ethical framing is the right one and the licensing follows it, so on intent this dimension is favourable. But a user can only exercise judgment over an output whose categories they understand, and those categories are undefined in the paper — so the safeguard the conclusion relies on is not actually delivered by the described interface.

## What this report did not check

- **Web-dependent slots skipped (no web access for this run).** Author background and prior work in the area; the tree-forward comprehensiveness check (whether more recent work citing the paper's own key references is conspicuously missing); the count of references sharing the author's institution; whether the 23 references exist and whether their metadata, volume and issue numbers, page ranges, DOIs and links are correct; whether each cited paper supports the claim attached to it beyond what its listed title shows; the identity, free-tier limits and prices of the "commercial hallucination detection services" the paper critiques (N23); the accuracy of Table 1's feature grid against current versions of Zotero, Mendeley, EndNote and JabRef (N24); whether the report behind the NeurIPS and ICLR figures says what the Fortune article is cited for (N26); and whether Nicholas et al. (2025) reports the fabricated-author frequency it is cited for (N38).
- **The deployed tool itself was not exercised.** `https://zabbonat.github.io/References-Validation/` was not visited, the source repository was not inspected, and the MIT License was not confirmed (N22, Claim 9 of the stage 1 extraction). Every statement in this report about the tool's behaviour is a statement about Algorithm 1, Figure 1, and Sections 3–4 — the described design, not the running software. A reader should assume nothing here about whether the deployment matches the description.
- **Parts of the paper not read or not readable.** None: all 9 pages were read, and there are no appendices, supplements, or data availability materials to read. Page 4 (Algorithm 1) and page 5 (Figure 1) were additionally read as page images; pages 1–3 and 6–9 were read as extracted text only, so the page-1 margin string (`arXiv:2602.15871v1 [cs.CL] 27 Jan 2026`) and Table 1's ✓/– glyphs on page 7 rest on the text extraction rather than on a rendered page.
- **Proofs or analyses not followed in detail.** None to follow: the paper contains no proof, no derivation, and no statistical analysis. Equations 1–3 were read as definitions and checked for internal consistency against Algorithm 1; Eq. 1 was not re-derived, and no numeric example was traced through Eq. 2 or Eq. 3 because the paper supplies no example input (N36).
- **Statements in this report resting on recall rather than on the paper.** Two, both in the Context section and neither used as a finding anywhere in the Discussion: (a) that Garfield (1972), Merton (1973) and MacRoberts and MacRoberts (1996) are the field's recognized foundational references for the scientometric frame, and that Hendricks et al. (2020), Ammar et al. (2018) and Priem et al. (2022) are the standard descriptor papers for CrossRef, Semantic Scholar and OpenAlex — recall, not verified against a citation index; (b) that the arXiv identifier prefix `2602` encodes February 2026 while the stamp on the same line reads 27 Jan 2026 — the encoding convention is recall, and the string itself was read from the text extraction rather than from a render of page 1. Neither is presented as a finding, and neither moves any verdict.

## Appendix: not-stated list, inconsistency list, verifier list

### Stage 3 return accounting

- **Points returned by the stage 3 subagent**: 58 (Importance 4, Credibility 10, Novelty 5, Applicability 6, Generalizability 5, Scalability 6, Assumptions 10, Readability 7, Ethics 5).
- **Points dropped for missing evidence**: 1. Credibility Point 10 (the paper is an un-reviewed arXiv preprint, and the arXiv identifier's month block 2602 does not match the printed date of 27 Jan 2026) cited only "page 1 margin" and the stage 1 Venue/Status row. The page-1 margin stamp is not a Location under this report's convention — it is not a section paragraph, algorithm line, figure, table, or equation — and the stage 1 extraction is not an N- or C- entry. The venue's lack of peer review is carried by the Context "Venue" slot; the identifier/date observation is quarantined under "What this report did not check".
- **Duplicate groups stage 4 collapsed**: 4.
  1. Triple-intersection premise vs. the paper's coverage rationale (C3, C4) — kept at Credibility Point 3, cross-referenced from Assumptions A3.
  2. Source independence and the +10 multi-source bonus (Sec 3 para 2; Algorithm 1 lines 18, 21–22) — kept at Assumptions A2, cross-referenced from Credibility Point 9.
  3. Eq. 1's behaviour on altered and benign titles (Eq. 1; Sec 3 para 6) — kept at Credibility Point 4, cross-referenced from Assumptions A6.
  4. The three-way prose/pseudocode/figure method conflict (C1, C2, C6, C8, C9) — kept at Credibility Point 7, cross-referenced from Readability Point 1.
- **Other stage 4 removals**: the subagent's front-matter paper-type line and its closing "One-line summary for the caller", neither of which is a slot in this report; the duplicated base-rate arithmetic inside Ethics Point 2, replaced by a cross-reference to Credibility Point 5.
- **Derived numbers recomputed at stage 4**: the Eq. 1 similarity table (Credibility Point 4) was recomputed from scratch on titles pinned to the paper's own reference list, replacing four unpinned figures; the base-rate calculation (Credibility Point 5, cross-referenced from Ethics Point 2) was recomputed on 23 references per paper, the paper's own bibliography size, in place of an externally assumed 40; the Scalability rates were recomputed on the paper's own corpus figures (4,000 accepted papers; 21,500 submissions) in place of an externally assumed 1,000-submission journal-year, and the fallback-path rate that treated the 800 ms figure as a per-API-call interval was withdrawn, since Sec 4 para 2 states it as an interval between batch *entries*; Scalability Point 4's "≥2.4 s of enforced delay" was withdrawn for the same reason and replaced with the round-trip count the paper does specify; Eq. 3's worked values in Assumptions A8 and A9 were restated as ranges over β_ms ∈ [0, 10]; the coverage-gap document-type count in Applicability Point 5 was corrected from 2 of 23 to 3 of 23; and the name-form counts in Generalizability Point 3 were corrected from "diacritics in four and a hyphenated compound in one" to 6 non-ASCII surnames, 2 hyphenated compounds, and 1 unhyphenated two-part family name. The Merton walkthrough (Credibility Point 6) and the author-count figures (Assumptions A4) were recomputed and confirmed unchanged.

### Not-stated list

N1. Any evaluation of the tool — precision, recall, accuracy, false-positive or false-negative rate on genuine versus hallucinated references. Not given anywhere; the recall/precision claim (Sec 3 para 2, last sentence) and the "higher confidence" claim (Sec 5 para 1, p8) have no reported measurement. There is no Evaluation section.

N2. The calibration behind footnote 2 (p6): the dataset of "valid references and known hallucinations" (size, provenance, how hallucinations were obtained or labeled), the calibration procedure, the objective optimized, and the resulting discrimination. Only the sentence in footnote 2 exists.

N3. The set of LaTeX commands removed by FILTERLATEXCOMMANDS (Algorithm 1 line 1 "etc."; Sec 3 para 3 "such as \\vspace, \\hspace, \\textit, or custom macros") and how custom macros are recognized.

N4. How the search query is constructed (Figure 1 node "Construct Search Query"): which CrossRef endpoint and query fields are used, and how free-text input versus extracted BibTeX fields are mapped to them (Algorithm 1 line 2 gives only CROSSREFQUERY(q, rows = 3)).

N5. EVALUATECANDIDATES (Algorithm 1 line 6): how the best of the three candidates is chosen, whether the score used for selection is the composite confidence of Eq. 2/3 or title similarity alone, and how ties are broken.

N6. DETECTISSUES (Algorithm 1 line 7): the full list of issue types and their definitions. Sec 3 para 8 (p6) names four penalized issues (title mismatch, author mismatch, journal discrepancy, fake author) without defining the condition for each (e.g., what similarity value constitutes a "title mismatch").

N7. COMPUTEFINALSCORE (Algorithm 1 line 30): how bestScore and issues combine; the rule selecting a value inside the ranges "−10 to −20" for journal discrepancies and per fake author (Sec 3 para 8, p6).

N8. MERGEMETADATA (Algorithm 1 line 23): which source wins when CrossRef, Semantic Scholar, and OpenAlex disagree on a field (year, venue, author order, title).

N9. SEMANTICSCHOLARQUERY and OPENALEXQUERY (Algorithm 1 lines 4, 10, 11): endpoints, number of results retrieved, whether one or several candidates are compared, and whether the fallback sources are themselves scored by Eq. 1–3.

N10. Author similarity S_author beyond "the proportion of matched authors" (Sec 3 para 7, p6): the denominator (authors in the query or authors in the database record); handling of "et al.", initials, diacritics, hyphenated or multi-part family names, and name order in non-Western conventions; whether family names undergo the same normalization as titles (Sec 3 para 6 removes non-alphanumeric characters, which alters hyphenated names).

N11. S_journal and S_year (Eq. 3): neither is defined. Sec 3 para 6 defines only the title similarity (Eq. 1). How a numeric year yields a similarity (exact match, tolerance) is not stated.

N12. The rule for which scoring formula applies: Eq. 2 applies "When title similarity exceeds 80% but author similarity falls below 90%" (Sec 3 para 8, p6); Eq. 3 applies "For structured input with high matching across all fields". The formula for every other case (title similarity at or below 80%; free-text input with high matching; structured input with title > 80% and author ≥ 90%) is not given.

N13. The threshold behind "high matching across all fields" (Eq. 3 condition, Sec 3 para 8, p6).

N14. The rule producing intermediate values of β_ms ∈ [0, 10] (Eq. 3). Algorithm 1 line 22 adds exactly 10.

N15. The API usage policies that the 800 ms interval complies with (Sec 4 para 2, p7); whether API keys, a CrossRef "polite pool" contact, or Semantic Scholar rate limits are handled; what happens on an API error or timeout.

N16. What the tool outputs for reference types that the paper itself says CrossRef may lack (Sec 3 para 2, p3: preprints, regional journals, older publications) and for books, theses, and reports — whether these are reported as non-existent.

N17. The meaning of the three thresholds and their relation to one another: exists is bestScore > 50 (Algorithm 1 line 32); fallback triggers below 70 (Algorithm 1 line 8; Figure 1); "Verified" requires > 80% (Figure 1). The text (Sec 3 para 8; Sec 4) never mentions 50 or the Verified/Partial Match labels, and does not say what a user sees for a reference with exists = true but score ≤ 80.

N18. The role of "optional expected metadata E" (Algorithm 1, Require line): E is never used in lines 1–32.

N19. The "sources" field of the return value (Algorithm 1 line 32): never defined.

N20. Where the code runs: the paper says "web-based application using React with TypeScript" (Sec 3 para 1) and the URL is a GitHub Pages site (footnote 1; Availability), but does not say whether database queries are issued from the user's browser or from a server, or whether any user input is stored or sent to a third party.

N21. Privacy and data handling of submitted references (unpublished manuscripts' bibliographies are the intended input, Sec 5 para 1). Not mentioned.

N22. Software version, release date, source-repository location (only the GitHub Pages URL is given), dependencies (Levenshtein implementation, BibTeX parser, APA 7 formatter), tests, and how to reproduce the deployment.

N23. The identity of the "commercial hallucination detection services" (Abstract; Sec 1 para 4, p2; Sec 4.1 para 2, p7), their free-tier limits, and their prices. None is named; Table 1 does not include them.

N24. How Table 1 (p7) was compiled: versions and dates of Zotero, Mendeley, EndNote, and JabRef examined; the criterion for "Unlimited free usage" (Mendeley ✓, EndNote –) and for "Open source"; whether the entries were checked against vendor documentation.

N25. The scope of Table 1's "Bibliography formatting ✓" for CheckIfExist, given that the tool's stated output formats are APA 7 and BibTeX only (Sec 4 para 3, p7).

N26. The primary source for the NeurIPS 2025 and ICLR figures (Sec 1 para 3, p2: "over 4,000 research papers", "more than 100 AI-hallucinated citations across at least 53 papers", "50 hallucinated citations" at ICLR, "acceptance rate of 24.52% from over 21,500 submissions"). The only citation is Goldman (2026), a Fortune press article whose own title says "new report claims"; the report is not cited.

N27. Funding, conflicts of interest, and acknowledgements. No statement anywhere (checked: Abstract through Availability).

N28. Author contribution or role statement. Single author; none given.

N29. Any relationship between the author and the databases queried or the tools compared. Not stated.

N30. A limitations section or any stated limitation of the tool (false positives on genuine references absent from the databases; false negatives on hallucinations that closely alter real papers, a form the paper itself describes in Sec 1 para 3, p2). None; Sec 5 states none.

N31. Future work. None stated.

N32. Prior academic or open-source tools for automated citation-existence checking. The related-work discussion (Sec 1 para 4; Sec 4.1) covers reference managers and unnamed commercial services only; Dunford et al. (2024), whose title is "Using automated analysis of the bibliography to detect potential research integrity issues", is cited (Sec 1 para 3; Sec 2 para 2) for the difficulty of manual detection and "chimeric" forms, not discussed as a prior automated approach.

N33. Definitions distinguishing Table 1's rows "Immediate validation", "Hallucination detection", "Fake author detection", and "Multi-source validation" as separate features.

N34. Title-matching details: whether whole titles or truncated strings are compared, handling of subtitles, and behavior of Eq. 1 for very short titles.

N35. The ranking behind "Retrieve Top 3 Candidates" (Figure 1) — presumably the database's relevance order; not stated.

N36. A worked example of a hallucinated reference passing through the pipeline, or of a genuine one; the paper gives no example input, output, or screenshot.

N37. The date of the coverage figures "over 140 million scholarly works" (CrossRef, citing Hendricks et al., 2020) and "over 200 million academic papers" (Semantic Scholar, citing Ammar et al., 2018) in Sec 3 para 2, p3 — whether the figures are from the cited papers or from another source is not stated.

N38. Whether Nicholas et al. (2025), cited in Sec 3 para 7 (p6) for LLM hallucinations "frequently" inserting non-existent author names, reports such a frequency. Its listed title is "Early career researchers open-up on citations in respect to reputation, trust, ethics, AI and much more"; not checked (no web access).

N39. What "Partial Match" and "Corrected Citation" mean to the user (Figure 1) — the text never describes these states or the "Mismatch" path.

N40. How single-author works are handled by the multi-source bonus rule |confirmedAuthors| ≥ 2 (Algorithm 1 line 21), which a single-author record can never satisfy.

N41. Handling of the case in which CrossRef returns candidates whose best score is below 50 and the fallback sources return nothing — the output path for a wholly fabricated reference is not walked through.

N42. Which "string similarity algorithms" (Abstract, plural) are used other than Levenshtein distance (Sec 3 para 6, the only one described).

N43. Whether the "author mismatch" penalty (−20) and Eq. 2's reduction for author similarity below 90% are applied together, and what condition defines an "author mismatch" issue (Sec 3 para 8, p6).

N44. Whether the queries were exercised on the NeurIPS/ICLR hallucinated citations that motivate the paper (Sec 1 para 3; Sec 5 para 1). Not stated.

### Inconsistency list

C1. Fallback trigger at exactly 70. Algorithm 1 line 8 triggers fallback when "bestScore < 70 or |issues| > 0"; Figure 1's decision node reads "Score > 70%?" with "No/Issues" leading to fallback. A score of exactly 70 does not trigger fallback in Algorithm 1 but does in Figure 1.

C2. Cascade versus unconditional dual query. Sec 3 para 2 (p3) describes Semantic Scholar as "a fallback source" and says "OpenAlex completes the validation cascade"; Algorithm 1 lines 10–11 query both Semantic Scholar and OpenAlex unconditionally once fallback triggers, with no cascade between them. Figure 1 draws them in sequence (Semantic Scholar API → OpenAlex API) with no decision node between.

C3. Stated purpose of multi-source lookup versus the intersection rule. Sec 3 para 2 (p3) says the multi-source approach "addresses a fundamental limitation of single-database validation: no individual scholarly database achieves complete coverage" and yields "higher recall than any single-source approach". Algorithm 1 lines 18–19 define confirmedAuthors as the intersection of the three sources' author sets and suspectAuthors as every author outside that intersection; lines 26–27 then add a "Potential fabricated authors" issue whenever suspectAuthors is non-empty. Under these lines, a genuine reference missing from any one of the three databases has an empty intersection, so all of its authors are flagged as potentially fabricated — the coverage gap the text says the design overcomes is, in the pseudocode, converted into a fabrication flag.

C4. Which authors are cross-validated. Sec 3 para 7 (p6) says authors "appearing in only one source or in the query but not in any database are flagged as potentially fabricated"; Algorithm 1 line 19 computes suspectAuthors from the three database author sets only (query authors are not in the expression) and flags any author absent from even one source, not only those "appearing in only one source".

C5. Multi-source bonus: fixed or ranged. Algorithm 1 line 22 adds exactly 10 when |confirmedAuthors| ≥ 2; Eq. 3 and Sec 3 para 8 (p6) define β_ms ∈ [0, 10] as "the bonus awarded when author information is validated across multiple databases".

C6. Which score decides existence. Algorithm 1 line 30 computes confidence from bestScore and issues, but line 32 returns exists : bestScore > 50 — the pre-penalty score. Figure 1 places the "Score > 80%?" (Verified) decision after "Compute Confidence Score", and Sec 3 para 8 (p6) says penalties adjust "the composite confidence score". Three thresholds (50, 70, 80) appear across Algorithm 1 and Figure 1 with no reconciliation in the text (see N17).

C7. correctedMetadata used when it may be unassigned. Algorithm 1 line 23 assigns correctedMetadata only inside the branch |confirmedAuthors| ≥ 2 (itself inside the fallback branch of line 8); line 31 calls GENERATEOUTPUTS(correctedMetadata) unconditionally. When fallback does not trigger, or fewer than two authors are confirmed, the pseudocode generates outputs from an unassigned variable.

C8. Corrected citation on mismatch versus on confirmation. Figure 1's "Cross-validate Authors" node sends its "Mismatch" edge to "Corrected Citation", and "Partial Match" also flows to "Corrected Citation"; Algorithm 1 line 23 produces correctedMetadata only when authors are confirmed across sources (|confirmedAuthors| ≥ 2), and Sec 3 para 7 (p6) says mismatched authors are "flagged as potentially fabricated", not corrected.

C9. Source labeling when CrossRef returns nothing. Algorithm 1 line 4 fills candidates from Semantic Scholar when CrossRef is empty; line 14 then labels the authors of bestMatch as crossRefAuthors, and line 10 queries Semantic Scholar a second time. Figure 1 has no branch for an empty CrossRef result at all ("Retrieve Top 3 Candidates" flows straight to scoring).

C10. Lowercasing versus capitalized-token detection. Sec 3 para 6 (p6): "Prior to comparison, strings undergo normalization through conversion to lowercase and removal of non-alphanumeric characters." Sec 3 para 7 (p6): fabricated authors are detected as "capitalized tokens in the query". After the stated normalization no capitalized tokens remain; the paper does not say the detection runs on the un-normalized query.

C11. Footnote 2 (p6) states "author-related discrepancies weighted more heavily"; the penalty list in Sec 3 para 8 (p6) gives title mismatches −20 and author mismatches −20 — equal weights (the per-author fake-author penalty of −10 to −20 is the only author-specific extra).

C12. Sec 1 para 4 (p2) supports "Reference managers such as Zotero, Mendeley, EndNote, and JabRef provide comprehensive functionality..." with Kratochvíl (2017), whose title in the reference list (p9) is "Comparison of the accuracy of bibliographical references generated for medical citation styles by EndNote, Mendeley, RefWorks and Zotero" — JabRef is absent from the cited title.

C13. Sec 1 para 4 (p2) supports the claim about commercial hallucination-detection services' "restrictive freemium models" with Zhu et al. (2025), whose title in the reference list (p9) is "Evaluating the potential risks of employing large language models in peer review" — the cited title does not indicate coverage of commercial services or pricing.

C14. Sec 2 para 1 (p2) states "Studies examining citation accuracy across disciplines have documented error rates ranging from 25% to 54%" citing Siebers and Holt (2000), whose title is "Accuracy of references in five leading medical journals", and Wager and Middleton (2008), "Effects of technical editing in biomedical journals: A systematic review" — both titles are confined to medicine, while the claim is "across disciplines".

C15. Two 2025 entries in the same journal carry different volume numbers: Céspedes et al. (2025), Journal of the Association for Information Science and Technology, 76(6); Taşkın (2025), same journal, 77(1) (References, p8–9). The conflict presumes one volume per year; the paper does not say otherwise, and whether either entry is correct is a web check (not checked).

C16. The acronym DOI is used in Sec 1 para 4 (p2, "a fabricated DOI") before "Digital Object Identifier system" appears in Sec 3 para 2 (p3), and the acronym is never attached to the expansion.

C17. Abstract: the tool computes "multi-dimensional match confidence scores" with "string similarity algorithms" (plural); Sec 3 para 6 (p6) describes one algorithm (Levenshtein distance). See N42.

Citation existence and metadata correctness for all 23 references: not checked (no web access).

### Verifier list (stage 5)

The verifier checked 310 items — every **Location** field in the body and in the two lists above, every quoted passage, and every number attributed to the paper — against the paper text and the page-4 and page-5 renders. 3 failed. Dispositions:

1. **Summary → Results**, on Table 1's reading. Report claimed the paper's wording was "in a complementary position within the reference management ecosystem"; the paper (Sec 4.1 para 2, p7) reads "the proposed system **occupies** a complementary position within the reference management ecosystem". **Corrected** — the quotation now runs from "the proposed system occupies".
2. **Credibility Point 1, "Why it matters"**. Report placed "maintained precision" in quotation marks; the paper (Sec 3 para 2, last sentence, p3) reads "while **maintaining** precision through multi-source confirmation". **Corrected** to the paper's inflection; "higher recall" passed as written.
3. **Assumptions verdict sentence**. Report said "the paper states one of them fully, gestures at a second"; the verifier found no support for either count — all nine premise entries A1–A9 are labelled "Not stated", and no paper location is offered for a stated premise. **Corrected**: the verdict now reads that the paper states none of the nine as an assumption. The same sentence's "at least three of those false as written" was confirmed (A2, A3, A5) and stands.

Two items the verifier passed but marked as close to the line were corrected anyway, for consistency with the Location convention and to remove a count ambiguity: Scalability Point 1's Location is now "Sec 4 para 2 (pp6–7)", the phrase "comprehensive bibliography audits" sitting on p6 of a paragraph that spans pp6–7; and the Context "References check" sentence now reads "the two paper locations … carry appendix entries C12, C13 and C14", which no longer reads as a count of entries.

The verifier recorded that all 32 Algorithm 1 line references and every Figure 1 node name and edge label used in this report resolve as stated against the page renders, and that apparent quote mismatches elsewhere were artefacts of line-break hyphenation in the text extraction, matching the paper verbatim once de-hyphenated. Numbers labelled "derived" were outside its scope by the brief; those were recomputed at stage 4 and are itemised under "Stage 3 return accounting" above.
