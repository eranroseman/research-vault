# Critical analysis: *CheckIfExist: Detecting Citation Hallucinations in the Era of AI-Generated Content*

Paper analysed: Diletta Abbonato, arXiv:2602.15871v1 [cs.CL], 27 January 2026, 9 pages. Text extracted with PyMuPDF; Algorithm 1 (page 4) and Figure 1 (page 5) read from page renders. **This run had no web access**; every slot that depends on it is marked below and listed again under "What this report did not check".

## 1. Context

**Title.** Short and informative: the tool's name, the problem it targets, and the setting. It sets the expectation of a detector whose detection performance is characterised — "Detecting Citation Hallucinations" promises that hallucinated citations get detected, at some rate. The paper describes a tool that is designed to do this and reports no detection rate (N1), so the title promises more than the body delivers.

**Authors and affiliations.** One author, Diletta Abbonato, corresponding, at the Department of Culture, Politics and Society, University of Turin. Author order carries no information in a single-author paper, and the paper gives no contribution statement (N28) — for a sole author that is a formality rather than a gap. One institution, one department. The department is a social-science one while the paper is filed under cs.CL and is in substance a software description; nothing follows from that about quality, but a reader should not expect the software-engineering reporting conventions of a systems venue. Whether the affiliation is well known, and what the author has published before in citation integrity or scientometrics, are web checks: **not checked: no web access**.

**Venue.** arXiv preprint, [cs.CL], stamped 27 January 2026, version 1. No journal or conference is named and no submission status is stated. On the source-type scale this is the lowest-assurance category: a preprint carries no mandatory quality control, so nothing in the paper has been filtered by peer review, and the reader is doing the review. The predatory-venue check does not apply — there is no venue to check. Concretely, this means the paper's unevidenced performance claims (Claim 2, Claim 3, Claim 8 in the extraction) have not been challenged by anyone before reaching the reader.

**Motivation.** Well motivated, and this is the paper's strongest section. Section 1 paragraph 2 establishes why citation accuracy matters (Garfield, 1972; Merton, 1973; MacRoberts and MacRoberts, 1996); paragraph 3 gives the immediate trigger, hallucinated citations found in accepted NeurIPS 2025 papers and in ICLR submissions; Section 2 adds documented citation-error base rates of "25% to 54%", the distinction between transcription error and systematic fabrication (Ji et al., 2023), reported hallucination rates of "6% to over 30%" (Agrawal et al., 2024), and an economic argument that generation cost has collapsed while verification cost has not (Section 2 paragraph 3). The contribution is stated plainly (Section 1 paragraph 1; Section 1 paragraph 5). There is **no overview of the rest of the paper**: no roadmap paragraph closes Section 1, and no section previews another.

**Related work.** There is no Related Work section. Prior work is handled in two places: Section 1 paragraph 4, on reference managers and bibliographic databases, and Section 4.1, on reference managers again via Table 1. Both synthesise rather than list — paragraph 4 argues a position (these tools organise, they do not validate) instead of enumerating features — but the synthesis covers the wrong neighbours. The gap the paper claims is "automated citation-existence checking", and the works compared are reference managers, which were never meant to do that, plus "commercial hallucination detection services" that are never named (N23). Prior academic or open-source citation-checking tools are absent (N32), including Dunford et al. (2024), cited twice for the difficulty of manual detection while its own title is "Using automated analysis of the bibliography to detect potential research integrity issues" — an automated approach cited but not positioned as prior art. Against a stated gap, that omission matters more than a missing recent citation would.

- *Tree backward*: the reference list does reach the field's foundations for the citation-integrity half of the argument — Garfield (1972), Merton (1973), MacRoberts and MacRoberts (1996), Simkin and Roychowdhury (2003) — and the correct primary papers for the three databases (Hendricks et al., 2020; Ammar et al., 2018; Priem et al., 2022). The judgement that these are the recognised foundational references is **recall, not a check against the paper**, and is quarantined below. For the tool-building half there is no backward tree at all, because no prior tool is cited.
- *Tree forward*: requires a citation index. **Not checked: no web access.**

**References check.** 23 entries (References, pages 8-9), counted from the list. By source type: 18 journal articles, 2 conference proceedings (Agrawal et al., 2024; Ammar et al., 2018), 1 book (Merton, 1973), 1 arXiv preprint (Priem et al., 2022), 1 press article (Goldman, 2026, *Fortune*). Labelling is mostly adequate — the preprint is given as "arXiv preprint", and the review and survey entries announce themselves in their titles (Ji et al., 2023, "Survey of hallucination in natural language generation"; Wager and Middleton, 2008, "A systematic review"; Taşkın, 2025, "An Annual Review of Information Science and Technology (ARIST) paper") — with one exception: Goldman (2026) is a *Fortune* news article and is not marked as non-scholarly anywhere in the text or the list, while carrying the paper's most load-bearing empirical figures (N26). Span: 1972 to 2026, 54 years, with 12 of 23 entries from 2023 or later — a defensible balance of foundational and current. **Zero** references include the author; no self-citation. How many are from the author's own institution is a web check: **not checked: no web access**. Primary sources are used where the paper's own subject matter is concerned (the three database papers), but not for its motivating statistics: the NeurIPS 2025 and ICLR counts, the 4,000-paper denominator and the 24.52% acceptance rate all rest on a press article that its own title says reports what a "new report claims", and that underlying report is not cited (N26) — a secondary source standing in for an available primary one, in the paper's opening argument. Whether cited papers support the claims attached to them can only be checked here by comparing claim to cited title, and three comparisons fail: C12 (a four-manager claim cited to a study of four different managers, JabRef absent), C13 (commercial services' pricing cited to a paper on peer-review risks), C14 ("across disciplines" cited to two medicine-only studies). One internal metadata conflict is visible without the web: C15, two 2025 papers in the same journal given different volume numbers. Citation metadata, links, and the existence of each cited work are otherwise **not checked: no web access**. Papers recognised on sight: Garfield (1972), Merton (1973), Ji et al. (2023), Priem et al. (2022) — **recall**, quarantined below.

## 2. Summary

**Problem.** The paper states an objective, not a research question: there are no research questions, no hypotheses, and no success criteria anywhere. LLMs used in academic writing produce citations that look legitimate but refer to nothing (Section 1 paragraph 3), manual verification scales badly and interrupts writing, reference managers store metadata without checking it, and commercial checkers ration their free tiers (Section 1 paragraph 4). The objective is to close that gap with a free tool that verifies a reference against several scholarly databases "within seconds" (Section 1 paragraph 5).

**Method.** No family from the method menu applies: there is no experiment, no correlational or archival analysis, no survey, and no qualitative design, because no data of any kind is collected or analysed. By the calibration table this is a **systems (tool) paper**, and it should be held to architecture decisions, scalability evidence, deployment, and engineering contribution rather than to statistical significance. Its evaluation has **no method family either, because it has no evaluation** (N1): the only comparative element is Table 1, a functional feature matrix against Zotero, Mendeley, EndNote, and JabRef, whose compilation method, tool versions, and audit date are not given (N24).

What the paper does report is a design. The tool is a React/TypeScript web application in four modules — LaTeX-command filtering, BibTeX parsing, a multi-source search service, and a presentation layer (Section 3 paragraph 1). The pipeline (Algorithm 1; Figure 1) filters LaTeX commands, queries CrossRef for the top 3 candidates, scores them, and on a score below 70 or any detected issue falls back to Semantic Scholar and OpenAlex, intersects the three author lists, adds 10 to the score when at least 2 authors are confirmed, flags every author outside the intersection as potentially fabricated, computes a final confidence, and returns `exists` when the pre-penalty score exceeds 50 (Algorithm 1 lines 1-32). Title similarity is normalised Levenshtein on lowercased, alphanumeric-only strings (Equation 1); author similarity is the proportion of family names found in the query (Section 3 paragraph 7); two confidence formulas are given for two named conditions (Equations 2 and 3), with penalties of -20 for title or author mismatch and -10 to -20 for journal discrepancies and per fake author (Section 3 paragraph 8). Thresholds and penalties are said to be "empirically calibrated" (footnote 2, page 6) against "valid references and known hallucinations" whose dataset and procedure are not given (N2). Usage is a single text box with quick and batch modes, batch processing sequentially at 800 ms intervals, and APA-7 plus BibTeX output derived from retrieved metadata rather than from the input (Section 4 paragraphs 1-3).

**Results.** There are none to summarise. No dataset, no run, no counts, no timings, no descriptive statistics, no tables of measurements, no charts, and consequently no inferential statistics; there is no Results or Evaluation section (N1). The paper's quantitative content is entirely (a) numbers taken from cited literature and the press (Sections 1-2, plus the "over 140 million" and "over 200 million" coverage figures in Section 3 paragraph 2; N37) and (b) constants inside the design — 3 candidates, thresholds 50/70/80, penalties, an 800 ms interval, a +10 bonus. The performance claims that a reader would take away — "higher recall than any single-source approach while maintaining precision" (Section 3 paragraph 2), "particularly effective at detecting LLM hallucinations" (Section 3 paragraph 7), "higher confidence than single-database checks" (Section 5 paragraph 1), "within seconds" (Abstract; Section 4 paragraph 1) — rest on no reported measurement.

**Discussion.** Section 5 is titled Conclusions and does two things. First (paragraph 1) it lists five use cases: pre-submission author self-check, verification of LLM-suggested citations, reviewer audit, publisher submission pipelines, and filtering spurious references out of bibliometric datasets. Second (paragraph 2) it restates the contribution and the gap. The interpretation offered is that the tool "enables researchers to validate citations at the speed of modern content production", and that it complements rather than replaces reference managers — a positioning claim Section 4.1 paragraph 2 makes explicitly. There is **no limitations statement of any kind** (N30) and **no future work** (N31); the conclusion reiterates the motivation and the design but summarises no method or result, because there is no result. There is **no acknowledgements section, no funding statement, and no conflict-of-interest statement** (N27); the Availability section gives the MIT licence and a GitHub Pages URL and nothing else (N22).

## 3. Discussion

Every point carries **Location**, **Observation**, **Evidence or criterion**, **Why it matters**, and its type — *not reported*, *potential design or analysis problem*, *demonstrated inconsistency*, or *integrity concern*. These four do not substitute for one another: nothing below is an integrity concern in the misconduct sense.

### Importance

The problem is real and well motivated, and a free, instant existence-check for references is a genuinely useful thing to have, but the paper's contribution is a described design with no reported result of any kind, and the thing it actually builds — presence in three metadata indexes — is narrower than the "detecting citation hallucinations" it puts in its title.

- **Location**: Title; Abstract, sentence 3; Algorithm 1 line 32.
  **Observation**: The title and abstract frame the contribution as hallucination detection, while the operational output is `exists : bestScore > 50`, i.e. whether a sufficiently similar record was found in CrossRef, Semantic Scholar, or OpenAlex.
  **Evidence or criterion**: Algorithm 1 line 32; N16; N30.
  **Why it matters**: A reader deciding whether to trust a "does not exist" result needs to know that the construct measured is index coverage, not fabrication; the two diverge exactly for the classes Sec 3 para 2 (p3) does name as CrossRef gaps — "preprints, regional journals, or older publications" — and for the books, theses and reports the paper never mentions at all (N16).
  *Potential design problem (construct validity of the headline claim).*

- **Location**: Sec 1 para 3 (p2).
  **Observation**: The urgency argument — "over 4,000 research papers", "more than 100 AI-hallucinated citations across at least 53 papers", "50 hallucinated citations" at ICLR, "24.52% from over 21,500 submissions" — rests entirely on Goldman (2026), a *Fortune* news article.
  **Evidence or criterion**: N26; References (p9), where the Goldman entry's own title ends "new report claims".
  **Why it matters**: The paper's central motivating statistic is taken from a press account rather than the underlying report, so a reader cannot check the numbers or their denominators; this is the "press release before peer review" sourcing pattern applied to the motivation slot.
  *Not reported (primary source for the motivating statistics).*

- **Location**: Sec 1 para 3 (p2) and Sec 5 para 1 (p7–8) versus the paper as a whole.
  **Observation**: The NeurIPS/ICLR hallucinated citations that motivate the paper and reappear as a use case are never used as test input for the tool.
  **Evidence or criterion**: N44; N1.
  **Why it matters**: The cheapest possible demonstration — run the tool on the very fabrications the paper cites as proof of need — is available and absent, so the size of the contribution cannot be judged even roughly.
  *Not reported.*

- **Deployment and version evidence** (Availability, p8; footnote 1, p1; N22) — carried under Applicability, the dimension it bears on most. On a tool paper's own bar of architecture, scalability evidence, deployment and engineering contribution, only the architecture is supplied.

### Credibility

The design is described in enough detail to be criticized but nothing in the paper is measured, several of its performance claims are contradicted by its own pseudocode, and at least one control-flow path in Algorithm 1 would produce a confidently "corrected" citation for a reference that never existed — so a reader should treat every performance statement here as an unevaluated intention, discounting further for an unreviewed arXiv preprint (page 1 margin, arXiv:2602.15871v1).

- **Location**: Sec 3 para 2 (p3), last sentence; Sec 5 para 1 (p8).
  **Observation**: "The system achieves higher recall than any single-source approach while maintaining precision through multi-source confirmation" and "the multi-source validation providing higher confidence than single-database checks" are stated as results.
  **Evidence or criterion**: N1.
  **Why it matters**: Recall and precision are quantitative claims with no measurement, no test set, and no single-source baseline anywhere in the paper; this is a claim–evidence mismatch on the paper's principal technical assertion.
  *Potential analysis problem (claim–evidence mismatch).*

- **Location**: Algorithm 1 lines 6, 18, 21–23, 31; Figure 1 ("Cross-validate Authors" → "Mismatch" → "Corrected Citation").
  **Observation**: `bestMatch` is the best of three CrossRef candidates whatever its score; `confirmedAuthors` is then computed from that matched record's authors across the three sources, and if two or more agree the algorithm adds +10 and calls MERGEMETADATA, whose output is handed to GENERATEOUTPUTS. No threshold guards the correction path.
  **Evidence or criterion**: Algorithm 1 lines 6, 18, 21–23, 31; C8; Sec 1 para 3 (p2), which describes hallucinations that are "subtle alterations of real papers, such as expanding author initials into guessed first names or paraphrasing titles".
  **Why it matters**: For precisely the hallucination form the paper highlights, a fabricated query weakly matching the real paper will find that real paper well attested in all three sources, earn the multi-source bonus, and be returned as a corrected APA/BibTeX citation — the pipeline silently converts a fabrication into a confident citation of a different work rather than flagging it.
  *Potential design problem.*

- **Location**: Algorithm 1 lines 18–19, 26–27; Sec 3 para 2 (p3).
  **Observation**: `confirmedAuthors` is the three-way intersection and `suspectAuthors` is everything outside it, and any non-empty `suspectAuthors` appends "Potential fabricated authors".
  **Evidence or criterion**: C3; C4.
  **Why it matters**: A genuine reference absent from any one of the three databases has an empty intersection, so every one of its authors is flagged as potentially fabricated — the coverage gap that Sec 3 para 2 says multi-source lookup exists to overcome is, in the pseudocode, converted into a fabrication flag. The stated rationale and the implemented rule point in opposite directions.
  *Demonstrated inconsistency, with a design consequence.*

- **Location**: Footnote 2 (p6).
  **Observation**: "Threshold and penalty values were empirically calibrated to optimize discrimination between valid references and known hallucinations."
  **Evidence or criterion**: N2; C11.
  **Why it matters**: No calibration set, provenance, size, procedure, objective, or resulting discrimination is given, so the numbers 50/70/80, −20, −10 and +10 are unsupported; and the same footnote's claim that author discrepancies are "weighted more heavily" conflicts with Sec 3 para 8 (p6), where title and author mismatches both cost −20.
  *Not reported, plus a demonstrated inconsistency.*

- **Location**: Sec 3 para 7 (p6).
  **Observation**: Fabricated authors are detected as "capitalized tokens in the query that match neither title words, journal name, year, nor any real author family name".
  **Evidence or criterion**: Sec 3 para 7 (p6); N6.
  **Why it matters**: Ordinary citation strings carry many capitalized tokens outside those four fields — publishers, series and conference names, place names, "In", "Proceedings", "University", month names — so on the paper's own accepted input formats ("APA, MLA, Chicago", Sec 4 para 1) the signature feature is liable to emit fabrication flags for correctly cited real works, and no false-positive rate is reported (N1).
  *Potential design problem.*

- **Location**: Algorithm 1 lines 23 and 31.
  **Observation**: `correctedMetadata` is assigned only inside `if |confirmedAuthors| ≥ 2`, itself inside the fallback branch of line 8, yet line 31 calls GENERATEOUTPUTS(`correctedMetadata`) unconditionally.
  **Evidence or criterion**: C7.
  **Why it matters**: In the normal high-confidence path (no fallback), the specification generates the tool's advertised outputs from an unassigned variable, so the claim that outputs "derive from authoritative metadata retrieved from the scholarly databases" (Sec 4 para 3, p7) is not established by the algorithm as written.
  *Demonstrated inconsistency.*

- **Location**: Algorithm 1 lines 30 and 32; Figure 1 ("Compute Confidence Score" → "Score > 70%?" → "Score > 80%?").
  **Observation**: `confidence` is computed from `bestScore` and `issues`, but the existence decision returns the pre-penalty `bestScore > 50`; three thresholds (50, 70, 80) appear across Algorithm 1 and Figure 1 and none is mentioned in the text except the 80% and 90% conditions of Eq. 2.
  **Evidence or criterion**: C6; N17.
  **Why it matters**: A reference with detected issues and a heavily penalized confidence is still returned as existing, and a reader cannot reconcile what the interface shows with what the algorithm decides — the two numbers that matter most to a user are not tied together anywhere in the paper.
  *Demonstrated inconsistency.*

- **Location**: Sec 3 para 6 versus Sec 3 para 7 (both p6); Algorithm 1 line 8 versus Figure 1 ("Score > 70%?").
  **Observation**: Normalization converts strings to lowercase and strips non-alphanumeric characters, while fabricated-author detection looks for capitalized tokens in the query; and fallback triggers at `bestScore < 70` in the pseudocode but at "Score > 70%? / No" in the figure.
  **Evidence or criterion**: C10; C1.
  **Why it matters**: Two of the paper's three specifications of the same system (prose, pseudocode, figure) disagree on the input a detector consumes and on a decision boundary, so no single implementation is recoverable from the paper; C2, C5, C8 and C9 add four more such conflicts.
  *Demonstrated inconsistency.*

- **Location**: Table 1 (p7); Sec 4.1 para 2 (p7).
  **Observation**: The only comparative evidence in the paper is a 13-row feature table with no stated method, in which the author's own tool is one of the compared systems and receives every distinguishing checkmark.
  **Evidence or criterion**: N24; N33; N23.
  **Why it matters**: The gap claim ("fills this gap", Abstract) is carried by a self-authored comparison whose criteria are unstated and whose comparison set excludes the only systems claiming the same function, so the table cannot support the conclusion drawn from it.
  *Potential analysis problem.*

- **Location**: Sec 1 para 4 (p2); Sec 2 para 1 (p2); References (p9).
  **Observation**: Three claims carry citations whose listed titles do not cover them: reference managers "such as Zotero, Mendeley, EndNote, and JabRef" cited to Kratochvíl (2017), whose title covers EndNote, Mendeley, RefWorks and Zotero; commercial services' "restrictive freemium models" cited to Zhu et al. (2025), "Evaluating the potential risks of employing large language models in peer review"; error rates "across disciplines" cited to two medical-journal studies.
  **Evidence or criterion**: C12; C13; C14.
  **Why it matters**: In a paper whose subject is citation support, three of the load-bearing motivating claims rest on sources whose scope, as listed, is narrower than the claim.
  *Demonstrated inconsistency (claim against the paper's own reference list).*

- **Location**: References (p8–9).
  **Observation**: Céspedes et al. (2025) and Taşkın (2025) are both in the *Journal of the Association for Information Science and Technology* but in volumes 76(6) and 77(1); Strzelecki (2024) and Nicholas et al. (2025) are both in *Learned Publishing* volume 38.
  **Evidence or criterion**: C15; References (p9).
  **Why it matters**: Minor, and each has a benign explanation — volumes straddling calendar years, online-first issue assignment; noted only because the paper's subject is bibliographic metadata accuracy.
  *Demonstrated inconsistency (low severity).*

Inapplicable within this dimension: the analysis-bias checks (p-hacking, HARKing, multiplicity, missing-data handling) and the demand-characteristics check have no target — the paper reports no statistics and no human participants.

### Novelty

Assembling three existing metadata APIs behind normalized Levenshtein title matching and family-name containment is standard engineering; the one idea with a claim to novelty — treating cross-source author agreement as a fabrication signal — is asserted rather than positioned, since the paper reports no literature search and discusses no prior automated citation-verification work at all.

- **Location**: Sec 1 para 4 (p2); Sec 4.1 (p7).
  **Observation**: The related-work discussion covers four reference managers, three bibliographic search databases, and unnamed commercial services; there is no Related Work section and no academic or open-source prior art on automated citation-existence checking.
  **Evidence or criterion**: N32; N23.
  **Why it matters**: The novelty claim is wider than the cited literature supports, and the paper cites Dunford et al. (2024) — "Using automated analysis of the bibliography to detect potential research integrity issues" — only for the difficulty of manual detection and for "chimeric" fabrications, never as a prior automated approach to compare against.
  *Not reported (no search or prior-art positioning).*

- **Location**: Abstract, sentence 6; Sec 3 para 6 (p6).
  **Observation**: The abstract credits "string similarity algorithms" (plural) producing "multi-dimensional match confidence scores"; one algorithm is described, normalized Levenshtein distance (Eq. 1).
  **Evidence or criterion**: C17; N42.
  **Why it matters**: The methodological novelty on offer shrinks under inspection to one textbook edit-distance measure plus substring containment for names, which bears directly on whether a reader expects to learn anything transferable from the method.
  *Demonstrated inconsistency.*

- **Location**: Table 1 rows "Immediate validation", "Hallucination detection", "Fake author detection", "Multi-source validation" (p7).
  **Observation**: Four separate rows distinguish the tool from the comparators, and none is defined.
  **Evidence or criterion**: N33.
  **Why it matters**: Undefined feature rows make the novelty margin as wide as the author chooses to draw it; "hallucination detection" and "fake author detection" in particular appear to name the same mechanism twice.
  *Not reported.*

- **Location**: Sec 3 para 7 (p6), last sentence.
  **Observation**: "This multi-source confirmation is particularly effective at detecting LLM hallucinations" is supported by a citation about how often LLMs insert non-existent author names, not by any measurement of the mechanism.
  **Evidence or criterion**: N1; N38.
  **Why it matters**: The paper's one candidate novel contribution is claimed effective on the strength of a citation about the problem rather than evidence about the solution.
  *Potential analysis problem (claim–evidence mismatch).*

### Applicability

A free web tool that checks references against three indexes and hands back clean BibTeX is easy to try and plausibly useful for a quick sanity pass on a bibliography, but the paper gives a reader nothing to calibrate on — no accuracy figure, no example, no version, no error behavior — and the reviewer and publisher workflows it proposes are the ones that most need a false-positive rate.

- **Location**: Sec 3 (pages 3–6) and Sec 4 (pages 6–7), throughout.
  **Observation**: The paper contains no example input, no example output, no screenshot, and no trace of a single reference through the pipeline.
  **Evidence or criterion**: N36.
  **Why it matters**: A practitioner cannot see what a result looks like, what an "issue" string reads like, or how a borderline case is presented, which is the minimum needed to decide whether the tool fits a workflow.
  *Not reported.*

- **Location**: Sec 3 para 2 (p3); Sec 4 para 1 (p6).
  **Observation**: The paper lists preprints, regional journals and older publications as CrossRef gaps and accepts "any standard format (APA, MLA, Chicago, etc.) or informal reference descriptions", but never states what the tool returns for those inputs, or for books, theses, and reports.
  **Evidence or criterion**: N16; N4.
  **Why it matters**: Whether a humanities or regional-literature bibliography can be audited at all is undetermined, and a user has no way to distinguish "not indexed" from "not real" in the output.
  *Not reported.*

- **Location**: Sec 3 para 1 (p3); Availability (p8).
  **Observation**: The tool is described as a React/TypeScript web application served from a GitHub Pages URL, with no statement of whether queries are issued from the browser or a server, and no version, commit, repository, dependency list, or test description.
  **Evidence or criterion**: N20; N22.
  **Why it matters**: A reader cannot confirm that the deployed page matches the paper, cannot pin a version for reuse, and cannot tell where submitted references travel.
  *Not reported.*

- **Location**: Sec 4 para 3 (p7); Table 1 row "Bibliography formatting" (p7).
  **Observation**: Outputs are APA 7 citations and BibTeX records; Table 1 nevertheless awards the tool a general "Bibliography formatting" checkmark alongside the reference managers.
  **Evidence or criterion**: N25.
  **Why it matters**: A reader expecting the multi-style formatting the row implies (the comparators support many citation styles) would find two output formats.
  *Demonstrated inconsistency (low severity).*

- **Reviewer and publisher use of unmeasured fabrication flags** (Sec 5 para 1, p7–8; N1, C3) — carried under Ethics, the dimension it bears on most. Both proposed uses act on negative verdicts whose error rate is unmeasured.

### Generalizability

Nothing empirical is offered, so the reach of the approach can only be read off its design, and that design is bounded by three DOI- and metadata-centric indexes and by Latin-script, Western-order, single-token family names — limits visible in the paper's own reference list and never acknowledged.

- **Location**: Sec 3 para 6 and para 7 (p6); References (p8–9).
  **Observation**: Normalization strips non-alphanumeric characters and author matching relies on extracting family names and checking their presence in the query string; no handling of initials, "et al.", diacritics, hyphenated or multi-part family names, or non-Western name order is described.
  **Evidence or criterion**: N10.
  **Why it matters**: The paper's own bibliography contains Taşkın, Céspedes, Rodríguez-Bravo, Świgoń and Sainte-Marie — names that the stated normalization alters or splits — so the described method is likely to degrade on exactly the references the paper itself cites, and no test establishes otherwise.
  *Potential design problem.*

- **Location**: Algorithm 1 line 21.
  **Observation**: The multi-source confirmation bonus and the MERGEMETADATA correction both require `|confirmedAuthors| ≥ 2`.
  **Evidence or criterion**: N40; References (p9), which includes single-author works (Garfield 1972; Merton 1973; Strzelecki 2024; Taşkın 2025).
  **Why it matters**: A single-author work can never satisfy the condition, so it can never earn the bonus or the metadata correction; a whole class of genuine references is structurally disadvantaged by the scoring rule, unmentioned.
  *Potential design problem.*

- **Location**: Sec 3 para 2 (p3).
  **Observation**: The three sources are characterized by their own coverage skews — CrossRef strong on DOI-registered works, Semantic Scholar on computer science and biomedicine, OpenAlex broadest but with variable metadata quality.
  **Evidence or criterion**: Sec 3 para 2 (p3); N1.
  **Why it matters**: The paper correctly identifies that coverage is domain-dependent and then reports no result for any domain, so a reader in a field poorly covered by all three has no basis to expect the tool to work and — under C3 — reason to expect spurious fabrication flags.
  *Not reported.*

- **Location**: Sec 4 para 1 (p6).
  **Observation**: Quick check is said to accept free-form citation text "in any standard format (APA, MLA, Chicago, etc.) or informal reference descriptions".
  **Evidence or criterion**: N4; N36.
  **Why it matters**: Format-independence is the broadest generalization claim in the paper and rests on an unspecified query-construction step with no example and no test across formats.
  *Not reported.*

Inapplicable within this dimension: the external-validity machinery of sampling frames, representativeness, and subgroup consistency has no target — there is no sample of references, no test population, and no measurement (N1).

### Scalability

Downward the tool is fine — one reference, one round trip — but the described batch architecture is a sequential loop at 800 ms per entry, which is about 1.25 references per second (derived), and the conclusion's large-scale bibliometric use case is not reachable at that rate; no computational cost, latency, quota, or failure analysis is reported.

- **Location**: Sec 4 para 2 (p7); Sec 5 para 1 (p8).
  **Observation**: Batch mode "processes entries sequentially with rate limiting (800ms intervals)", while the conclusion proposes that "researchers conducting large-scale bibliometric analyses can filter potentially spurious references from datasets".
  **Evidence or criterion**: Sec 4 para 2 (p7); Sec 5 para 1 (p8).
  **Why it matters**: Derived from the stated interval: a 100-reference bibliography takes about 80 seconds, but a 100,000-reference dataset takes about 22 hours of uninterrupted browser-side querying — so the stated architecture does not support the stated use case, and the paper does not note the gap.
  *Potential design problem.*

- **Location**: Sec 4 para 2 (p7).
  **Observation**: The 800 ms interval is justified as complying "with API usage policies", with no policy named, no API key or contact mechanism described, and no statement of behavior on API error, timeout, or throttling.
  **Evidence or criterion**: N15.
  **Why it matters**: A reader cannot tell whether a batch run will complete, silently degrade, or be rate-limited mid-audit, and cannot distinguish an API failure from a "does not exist" verdict in the results.
  *Not reported.*

- **Location**: Algorithm 1 lines 2, 4, 10, 11.
  **Observation**: A single reference can issue up to four API calls, and when CrossRef returns nothing, Semantic Scholar is queried twice — once at line 4 and again at line 10.
  **Evidence or criterion**: C9.
  **Why it matters**: Per-reference cost is highest exactly on the hardest cases, and the duplicate call is pure waste; combined with the fixed 800 ms pacing this compounds the throughput problem above.
  *Demonstrated inconsistency, with a cost consequence.*

- **Location**: Sec 3 para 1 (p3); Table 1 row "Unlimited free usage" (p7); Sec 4.1 para 2 (p7).
  **Observation**: The tool claims unlimited free verification, while all query volume is served by three third-party APIs and the paper does not say whether requests originate in the user's browser or a server.
  **Evidence or criterion**: N20; N15.
  **Why it matters**: The sustainability of the "unlimited free" differentiator — the paper's stated advantage over commercial services — depends on quota economics the paper never addresses, so a reader cannot judge whether the property survives adoption.
  *Not reported.*

- **Location**: Abstract, last sentence; Sec 1 para 5 (p2); Sec 4 para 1 (p6).
  **Observation**: "Within seconds" is asserted three times.
  **Evidence or criterion**: N1.
  **Why it matters**: Latency is the tool's core user-facing promise and the one property that would have been trivial to measure; no number, distribution, or measurement condition is given.
  *Not reported.*

### Assumptions

The system rests on at least four strong assumptions — that indexed equals existent, that author-set agreement across three databases is a fabrication signal, that normalized edit distance on titles is comparable across title lengths, and that an additive point score is a calibrated percentage — and the paper states none of them as an assumption, tests none, and has no limitations section.

- **Location**: Algorithm 1 line 32; Sec 3 para 2 (p3).
  **Observation**: Existence is operationalized as a similarity score above 50 against records retrieved from three indexes, while the same section acknowledges that no individual database achieves complete coverage.
  **Evidence or criterion**: N16; N30.
  **Why it matters**: The identifying assumption of the whole tool — absence from three indexes implies non-existence — is the one the paper's own coverage discussion undercuts, and it is never written down where a user would see it. Same evidence as the first Importance point, which asks the different question of whether the contribution matches the title.
  *Potential design problem.*

- **Location**: Eq. 1 (p6); Sec 3 para 8 (p6).
  **Observation**: Similarity is `1 − lev/max(|a|,|b|)`, and a single global threshold of 80% is applied to title similarity.
  **Evidence or criterion**: N34.
  **Why it matters**: Derived from Eq. 1: one character edit costs 10 similarity points in a 10-character normalized title but 1 point in a 100-character one, so a fixed 80% cut is far stricter on short titles than long ones; the paper neither states this length dependence nor says whether whole titles, subtitles, or truncations are compared.
  *Potential design problem.*

- **Location**: Eq. 2 and Eq. 3 (p6).
  **Observation**: Eq. 2 is specified for "title similarity exceeds 80% but author similarity falls below 90%" and Eq. 3 for "structured input with high matching across all fields"; S_journal and S_year are never defined, and no formula is given for any other case.
  **Evidence or criterion**: N11; N12; N13.
  **Why it matters**: The scoring function is undefined over most of its input domain and two of its four inputs are undefined, so the thresholds cannot be applied, checked, or reimplemented by a reader — the composite confidence is not a reconstructable quantity.
  *Not reported.*

- **Location**: Algorithm 1 lines 22 and 32; Figure 1 ("Score > 70%?", "Score > 80%?").
  **Observation**: Penalties (−20, −10 to −20) and a bonus (+10) are added to a quantity derived from percentage similarities, and the result is displayed to users as a percentage threshold.
  **Evidence or criterion**: N2; N14; C5; C6.
  **Why it matters**: Derived from lines 22 and 32: a reference scoring 45 — below the existence cut — becomes 55 and is returned as existing once the fixed +10 bonus applies, so the existence verdict turns on an uncalibrated constant; and the same bonus is specified as a fixed 10 in the pseudocode but a range β_ms ∈ [0,10] in Eq. 3, with no rule for intermediate values.
  *Potential design problem, plus a demonstrated inconsistency.*

- **Location**: Algorithm 1, Require line.
  **Observation**: The procedure requires "optional expected metadata E", which never appears in lines 1–32.
  **Evidence or criterion**: N18.
  **Why it matters**: The algorithm's declared interface assumes an input it never consumes, which suggests the published pseudocode is not the implemented procedure — relevant to whether any of the above can be checked against the deployed tool (N22).
  *Demonstrated inconsistency.*

- **The assumption that all three sources hold, parse, and agree on a record** (Algorithm 1 lines 14–19; Sec 3 para 7, p6; N10) — never stated as an assumption; the contradiction between the stated rationale and the implemented intersection rule is carried under Credibility (C3, C4), the dimension it bears on most.

Inapplicable within this dimension: statistical-test assumptions, the counterfactual, and independent/dependent variable definitions have no target — the paper reports no statistical test and no experiment.

### Readability

The prose is fluent and the paper is easy to read end to end, but the technical core is the least clear part of it: three mutually inconsistent specifications of the same pipeline, undefined notation in the central equation, and user-facing states that only the figure mentions, wrapped in a register that occasionally outruns its evidence.

- **Location**: Eq. 3 (p6); Algorithm 1 line 32.
  **Observation**: S_journal and S_year appear in the composite score without definition; β_ms is given a range but no rule; the returned field `sources` is never described.
  **Evidence or criterion**: N11; N14; N19.
  **Why it matters**: The notation in the paper's only substantive equations is incomplete, so the equations read as decoration rather than specification.
  *Not reported.*

- **Location**: Figure 1 ("Verified", "Partial Match", "Corrected Citation", "Mismatch").
  **Observation**: Four user-facing states appear only in the figure; the body text never names or explains any of them, and never mentions the 50 or 80 thresholds that separate them.
  **Evidence or criterion**: N39; N17.
  **Why it matters**: The output vocabulary a user actually sees is undocumented in the text, so the reader learns the interface only by inference from a flowchart.
  *Not reported.*

- **Location**: Sec 2 para 1 (p2) and Sec 2 para 3 (p3).
  **Observation**: The motivation is elevated into economics — "negative externalities" and "path-dependent vulnerabilities" in para 1 (p2), "classic market failure" and "effectively laundering fabricated references" in para 3 (p3) — with no model, quantity, or estimate attached.
  **Evidence or criterion**: Sec 2 para 1 (p2); Sec 2 para 3 (p3).
  **Why it matters**: Technical terms used decoratively make the argument harder to evaluate than plainer prose would, and set a register the rest of the paper's evidence does not meet.
  *Not reported (the asserted mechanism carries no supporting analysis).*

- **Location**: Sec 5 heading and para 1 (p7–8); Sec 1 para 4 (p2).
  **Observation**: The "Conclusions" section opens with a list of prospective use cases rather than conclusions, and there is no Evaluation, Limitations, or Future Work section; "DOI" is used on p2 and "Digital Object Identifier" appears on p3 without the two ever being connected.
  **Evidence or criterion**: N30; N31; C16.
  **Why it matters**: The structure withholds the sections a reader looks for when deciding whether to trust a tool, and the reader must supply the acronym binding themselves.
  *Not reported, plus a demonstrated inconsistency (C16).*

- **The three mutually inconsistent specifications of the pipeline** (Sec 3 paras 5–8, pages 4–6; Algorithm 1; Figure 1; C1, C2, C5, C6, C8, C9) — carried under Credibility, the dimension it bears on most. One mental model of the tool is not recoverable from the paper.

Readability moves none of the other verdicts.

### Ethics

The purpose is pro-integrity and no human participants are involved, but the paper recommends that reviewers and publishers act on unmeasured fabrication flags, says nothing about what happens to the unpublished bibliographies users paste into a web page, states no limitation or negative consequence, and carries no funding or conflict-of-interest declaration.

- **Location**: Algorithm 1 lines 26–27; Sec 5 para 1 (p7–8).
  **Observation**: The tool emits the string "Potential fabricated authors: " plus the author names whenever the suspect set is non-empty, and the paper proposes that reviewers use such output to identify "potential fabrications warranting author clarification" and that publishers wire it into submission pipelines.
  **Evidence or criterion**: C3; C4; N1.
  **Why it matters**: Under the stated rule a genuine reference missing from one of three indexes produces a named fabrication flag, and no false-positive rate exists to bound how often that happens — the recommended workflow can put an unfounded fabrication allegation in front of an author or editor, a dignitary and professional harm the paper does not consider.
  *Potential design problem with an ethical consequence.*

- **Location**: Sec 5 para 1 (p7–8); Sec 3 para 1 (p3).
  **Observation**: The intended inputs include bibliographies of manuscripts prior to submission and of manuscripts under review; the paper does not say whether queries are issued from the user's browser or a server, whether input is retained, or what is disclosed to the three third-party APIs.
  **Evidence or criterion**: N20; N21.
  **Why it matters**: Reviewers pasting a confidential manuscript's reference list into a web tool are transmitting information about unpublished work to third parties, and the paper gives them no basis to judge that risk.
  *Not reported.*

- **Location**: Sec 5 (pages 7–8).
  **Observation**: The paper states no limitation, no failure mode, and no adverse consequence of the tool, and does not consider adversarial use — for example, an author iterating a fabricated reference until the tool reports "Verified".
  **Evidence or criterion**: N30; N31.
  **Why it matters**: A verification tool published without a stated error mode invites over-trust in its verdicts in both directions, and the paper offers no evidence that the author has considered either.
  *Not reported.*

- **Location**: Pages 1–8, checked from the Abstract through Availability.
  **Observation**: There is no funding statement, no conflict-of-interest declaration, no acknowledgements, and no statement of any relationship between the author and the databases queried or the tools compared in Table 1.
  **Evidence or criterion**: N27; N28; N29.
  **Why it matters**: "No conflicts-of-interest statement at all" is a standing red flag in the integrity checklist, and it is sharpened here by Table 1, where the author rates their own tool against four named commercial and open-source competitors with no disclosure of interest or method. No evidence of an actual conflict is present; the observation is the absence of the statement.
  *Not reported.*

## What this report did not check

- **Web-dependent slots skipped (no web access for this run)**: the author's background and prior work in this area; whether the affiliation is a well-known place; the tree-forward check for more recent work citing the paper's key references; how many references share the author's institution; whether each of the 23 cited works exists and whether its metadata, volume, issue, pages and links are correct; whether the contents of the cited works support the claims attached to them, so C12, C13 and C14 rest on comparing each claim to the cited *title* only; whether Nicholas et al. (2025) reports the author-fabrication frequency attributed to it (N38); the identity, free-tier limits and prices of the "commercial hallucination detection services" (N23); the volume numbers in C15; and the repository, licence file, version and running behaviour behind the tool's URL (N22, and the open-source/MIT claim).
- **Parts of the paper not read or not readable**: none. All 9 pages of the text extraction were read; Algorithm 1 (page 4) and Figure 1 (page 5) were read from page renders. The paper has no appendix, no supplement, and no code listing. The linked GitHub Pages application and its source were not opened.
- **Proofs or analyses not followed in detail**: the paper contains no proof and no statistical analysis. Equations 1–3 were read but not implemented or numerically tested; the arithmetic labelled "derived" under Scalability and Assumptions (throughput at 800 ms, the length dependence of Eq. 1, the +10 bonus crossing the 50 cut) follows from the paper's own stated constants and was not validated against a running implementation.
- **Statements resting on recall rather than on the paper**: that Garfield (1972), Merton (1973), MacRoberts and MacRoberts (1996) and Simkin and Roychowdhury (2003) are the recognised foundational references for citation analysis, and that Ji et al. (2023) and Priem et al. (2022) are recognised on sight (both used in Context, tree backward and References check); and that a systems venue's customary reporting conventions differ from this paper's. These are quarantined here and are not findings.

## Appendix: not-stated list, inconsistency list, verifier list

Location convention: section, then paragraph counted from the start of that section (page added when the section spans pages), or the algorithm line, figure, table, or equation number.

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

### Verifier list (stage 5), with dispositions

The stage 5 verifier checked 340 items — 45 body Location fields, 4 cross-reference bullets, 8 evidence-field paper locations, the 61 appendix entries N1–N44 and C1–C17, 182 quoted passages and about 40 paper-attributed numbers — against the paper text and the page-4 and page-5 renders. Three failed.

V1. **Importance, first point, "Why it matters"** — the report wrote that Sec 3 para 2 (p3) names "books, theses, regional and older publications" as CrossRef gaps. The paper names "preprints, regional journals, or older publications"; books and theses appear nowhere in the paper, and the report's own N16 keeps the two groups apart. **Disposition: corrected in place** — the sentence now quotes the paper's list and marks books, theses and reports as classes the paper never mentions.

V2. **Readability, third point** — the report located all four economics phrases at Sec 2 para 3 (p3). "classic market failure" and "effectively laundering fabricated references" are there; "negative externalities" and "path-dependent vulnerabilities" are in Sec 2 para 1 (p2). **Disposition: corrected in place** — the Location and Evidence fields now carry both paragraphs and the Observation attributes each pair to its own paragraph.

V3. **Summary, "Results"** — the report scoped the paper's literature-derived numbers to Sections 1–2, while the "over 140 million" (CrossRef) and "over 200 million" (Semantic Scholar) coverage figures sit in Sec 3 para 2 (p3). Incomplete rather than wrong; the report catalogues them at N37. **Disposition: corrected in place** — the sentence now includes those two figures and cites N37.

No item was removed, and none was moved to "What this report did not check".

### Stage 3 drop count

The stage 3 subagent returned 48 points across the nine dimensions (Importance 4, Credibility 11, Novelty 4, Applicability 5, Generalizability 4, Scalability 5, Assumptions 6, Readability 5, Ethics 4). Every point's Evidence field was a Location in the paper or a numbered N- or C- entry, and every N- and C- reference cited fell within the N1–N44 and C1–C17 lists above. **Points dropped for inadmissible evidence: 0.** Stage 4 then merged four points into one-line cross-references under the dimension each bears on most (deployment evidence into Applicability; reviewer/publisher use into Ethics; the author-set intersection assumption into Credibility; the three-way specification conflict into Credibility), removed one hedge that repeated an entry in "What this report did not check", and removed one sentence of format scaffolding.
