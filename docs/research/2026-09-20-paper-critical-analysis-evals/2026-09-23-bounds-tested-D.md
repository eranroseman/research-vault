# Critical analysis: CheckIfExist: Detecting Citation Hallucinations in the Era of AI-Generated Content

Paper: Diletta Abbonato, arXiv:2602.15871v1 [cs.CL], 27 Jan 2026, 9 pages. Analysed from a PyMuPDF text extraction plus page renders of Algorithm 1 (p4) and Figure 1 (p5). **Web access: not allowed for this run**, so every slot that depends on it reads "not checked: no web access".

## 1. Context

- **Title**: "CheckIfExist: Detecting Citation Hallucinations in the Era of AI-Generated Content" (title). Short, ten words, and it names the artefact and the problem, so a reader knows to expect a citation-checking tool aimed at LLM fabrications. It does not signal the paper type: "Detecting" reads as a capability that was measured, whereas the paper is a software description with no evaluation (Stage 1 Paper Type; N1).

- **Authors and affiliations**: one author, Diletta Abbonato (author block), corresponding at diletta.abbonato@unito.it (footnote on p1), Department of Culture, Politics and Society, University of Turin (affiliation). A single author means author order carries no information and there is no division of labour to read; one institution, one department — a social-science department, not a computer-science one, for a paper submitted to cs.CL. The paper states no contribution statement, no funding, no acknowledgements and no conflicts (N27, N28). The author's field and prior work: **not checked: no web access**; the reference list contains no entry naming this author, so the paper shows zero self-citations (References, pp8–9, derived: 0 of 23).

- **Venue**: arXiv preprint, stamped arXiv:2602.15871v1 [cs.CL] 27 Jan 2026 (identifier stamp, p1). No journal, conference or workshop is named anywhere. On the source-type scale this is the bottom rung — an electronic preprint with no mandatory quality control — so nothing in the paper has been through peer review, and every claim in it has to stand on the text itself. The predatory-venue check does not apply: arXiv is a moderated preprint server, not a reviewing venue. Because the paper's own motivating example is hallucinated citations surviving three or more NeurIPS reviewers (Sec 1 para 3, p2), the absence of review here is worth holding in mind while reading.

- **Motivation**: the paper motivates the problem at length and well. Sections 1 and 2 argue that citations are the verification substrate of science (Sec 1 para 2; Sec 2 para 1), that pre-LLM citation error rates already ran 25–54% (Sec 2 para 1), that LLM hallucination is categorically different from transcription error because it is systematic rather than random (Sec 2 para 2, pp2–3), that measured hallucination rates run 6% to over 30% (Sec 2 para 2, p3), and that the cost asymmetry between generating and verifying a citation is a market failure (Sec 2 para 3, p3). The headline motivating fact — over 100 AI-hallucinated citations across at least 53 of over 4,000 NeurIPS 2025 papers, plus 50 at ICLR (Sec 1 para 3, p2) — rests on a single Fortune press article whose own title says "new report claims" (Goldman, 2026; N26). The contribution is stated plainly (Sec 1 para 1; Sec 1 para 5, p2). There is **no overview of the rest of the paper**: no roadmap paragraph anywhere in Section 1.

- **Related work**: there is no Related Work section. Prior work is handled in two places — Sec 1 para 4 (p2), on reference managers, bibliographic databases and commercial detection services, and Sec 4.1 (p7), a feature table against four reference managers. Both synthesise rather than list: the argument that managers are built for organisation rather than validation, and that a hallucinated reference is therefore catalogued alongside a real one, is made as a connected case, not as a citation parade. The gap is identified in one sentence (Sec 1 para 5, p2) and it is a real gap in the tools it names. But the survey stops at reference managers and unnamed commercial services: no prior academic or open-source citation-existence checker is discussed (N32), even though Dunford et al. (2024) — cited twice, for manual-detection difficulty and for "chimeric" fabrications (Sec 1 para 3; Sec 2 para 2) — is titled "Using automated analysis of the bibliography to detect potential research integrity issues" and is plainly an earlier automated approach.
  - *Tree backward*: the reference list reaches the field's recognised foundations for the citation-as-verification argument — Garfield (1972), Merton (1973), MacRoberts and MacRoberts (1996), Simkin and Roychowdhury (2003) — and the standard infrastructure papers for all three databases queried (Hendricks et al., 2020 for CrossRef; Ammar et al., 2018 for Semantic Scholar; Priem et al., 2022 for OpenAlex). Nothing idiosyncratic. For the hallucination side it reaches Ji et al. (2023), Alkaissi and McFarlane (2023), Athaluri et al. (2023) and Agrawal et al. (2024). The judgement that these are the recognised foundational works is **recall, not a check against the paper** (quarantined under "What this report did not check"). The balance of recent to foundational is good: 1972–2026.
  - *Tree forward*: **not checked: no web access.** No citation index was consulted, so whether more recent work citing the paper's key references is conspicuously missing is unknown.

- **References check**: 23 entries (References, pp8–9). By kind, derived from the entries themselves: 18 journal articles, 2 conference proceedings (Agrawal et al., 2024; Ammar et al., 2018), 1 book (Merton, 1973), 1 arXiv preprint (Priem et al., 2022), 1 press article (Goldman, 2026, Fortune). Span 1972 (Garfield) to 2026 (Goldman) — 54 years, derived; 12 of 23 are from 2023 or later, derived, so the list leans recent without dropping the foundations. Labelling of reviews and preprints is mostly done by the titles rather than by the author: Priem et al. (2022) is marked "arXiv preprint"; Ji et al. (2023) announces itself as a "Survey" in a survey journal; Wager and Middleton (2008) says "A systematic review"; Taşkın (2025) says "An Annual Review of Information Science and Technology (ARIST) paper". The Fortune piece is identified only by outlet, with no URL, date or note that it is journalism rather than research. Self-citations: 0 of 23, derived. Same-institution citations: **not checked: no web access**. Citation metadata, DOIs and links: **not checked: no web access**; one internal conflict is visible without the web — two 2025 papers in the same journal are given different volumes, JASIST 76(6) and JASIST 77(1) (C15). Primary sources are used for the infrastructure and foundational claims but not for the paper's headline statistic, where a press article stands in for the report it describes (N26). Whether cited papers support the claims attached to them cannot be settled without reading them, but three claim-to-title mismatches are visible from the reference list alone: a claim about four reference managers including JabRef cited to a paper whose title covers EndNote, Mendeley, RefWorks and Zotero (C12); a claim about commercial detection services' pricing cited to a paper titled "Evaluating the potential risks of employing large language models in peer review" (C13); and a claim about citation accuracy "across disciplines" cited to two medical-journal studies (C14). Recognition of individual cited papers is **recall by construction** and is listed under "What this report did not check".

## 2. Summary

- **Problem**: the paper sets out to close one specific gap. Citations underpin verification in science, LLMs now fabricate them at measured rates of 6% to over 30% (Sec 2 para 2, p3), and the fabrications have reached accepted papers at NeurIPS and ICLR (Sec 1 para 3, p2; Abstract). Existing reference managers organise citations but do not validate their authenticity (Abstract; Sec 1 para 4, p2), bibliographic databases require manual per-citation querying that "scales poorly and interrupts the writing workflow" (Sec 1 para 4, p2), and commercial hallucination detectors sit behind restrictive freemium tiers (Abstract; Sec 1 para 4, p2). The objective is therefore a free, immediate, open-source verifier of whether a reference exists (Sec 1 para 1; Sec 1 para 5, p2). No research question, hypothesis or success criterion is stated as such, and no evaluation is proposed: the objective is to build the tool, not to measure it (N1).

- **Method**: **no family from the method menu fits.** There is no experiment, no correlational or archival analysis, no survey and no qualitative design; nothing is measured, so there is no unit of inference and no statistical analysis. By the menu's calibration table this is a **systems / tool paper**, to be held to architecture decisions, scalability evidence, real-world deployment and engineering contribution rather than to baselines or significance testing. It **has no evaluation**, so there is no evaluation family to name either — the Summary's evaluation slot is not assessable from the paper (N1). What the paper reports instead is a design. The tool is a React/TypeScript web application in four modules — LaTeX-command input preprocessing, BibTeX parsing, a multi-source search service, and a presentation/export layer (Sec 3 para 1, p3). Its process, as Algorithm 1 (p4) and Figure 1 (p5) give it: strip LaTeX commands (line 1); query CrossRef for the top 3 candidates (line 2), falling back to Semantic Scholar if CrossRef returns nothing (lines 3–5); score the candidates and pick the best (line 6); detect issues (line 7); if the best score is below 70 or any issue was found (line 8), query Semantic Scholar and OpenAlex (lines 10–11), intersect the three sources' author sets into confirmedAuthors and treat the rest as suspectAuthors (lines 18–19), add a flat +10 bonus and merge metadata when at least two authors are confirmed (lines 21–23), and raise a "Potential fabricated authors" issue if any author is outside the intersection (lines 26–27); compute a final confidence from score and issues (line 30); and return exists as bestScore > 50, with the confidence, issues, APA string, BibTeX record and sources (line 32). Title similarity is normalised Levenshtein, 1 − lev(a,b)/max(|a|,|b|), over strings lowercased with non-alphanumerics stripped (Eq. 1, p6). Author matching extracts family names from the primary source, checks containment in the query string, scores the proportion matched, and flags capitalised query tokens matching no title word, journal, year or real author family name as possible fabrications (Sec 3 para 7, p6). Confidence is Stitle − 0.5 × (100 − Sauthor) when title similarity exceeds 80% and author similarity is below 90% (Eq. 2, p6), or the mean of title, author, journal and year similarities plus a bonus βms ∈ [0, 10] for structured input with high matching across all fields (Eq. 3, p6), with penalties of −20 for a title mismatch, −20 for an author mismatch, −10 to −20 for a journal discrepancy and −10 to −20 per detected fake author (Sec 3 para 8, p6). Thresholds and penalties are said to have been "empirically calibrated" (footnote 2, p6), with no calibration set, procedure or outcome given (N2). What this choice of method implies for what the results can show is simple and severe: a design description can establish that a mechanism was specified, and nothing about how well it works. Every performance property — recall, precision, fabricated-author detection, latency — is asserted rather than shown (Claims 2, 3, 7, 8; N1).

- **Results**: **there are none.** The paper reports no data, no descriptive statistics, no tables of measurements, no charts of results, and no inferential statistics; the quantitative-results background file therefore has nothing in the paper to act on, and no assessment of analysis–design alignment, multiplicity, missingness or assumption diagnostics is possible (N1). The only table, Table 1 (p7), is a thirteen-row functional feature matrix of CheckIfExist against Zotero, Mendeley, EndNote and JabRef, marked with ticks and dashes and carrying no source, date or version for any entry (N24); by it, CheckIfExist alone has immediate validation, hallucination detection, fake author detection, batch verification, multi-source validation and corrected BibTeX output, and lacks reference organisation, word-processor integration and cloud synchronisation. The only figure, Figure 1 (p5), is the workflow diagram, not a result. The numbers the paper does carry — 140 million CrossRef works, 200 million Semantic Scholar papers (Sec 3 para 2, p3), 800 ms batch interval (Sec 4 para 2, p7), and the thresholds 50/70/80 and penalties in Algorithm 1 and Sec 3 para 8 — are stated properties of databases, of the implementation, and of the scoring rules, not outcomes of any procedure the paper ran.

- **Discussion**: the paper has **no Discussion section**; Section 5, "Conclusions", carries its place. The authors interpret the work by enumerating five deployment use cases (Sec 5 para 1, pp7–8): authors validating reference lists before submission; researchers checking LLM-suggested citations before use; reviewers auditing manuscripts for fabrications warranting author clarification; publishers integrating validation into submission pipelines, "with the multi-source validation providing higher confidence than single-database checks"; and bibliometricians filtering spurious references from datasets. The claimed advance is that the tool "enables researchers to validate citations at the speed of modern content production" and fills "a specific gap in the scholarly toolkit" while complementing rather than replacing existing managers (Sec 5 para 2, p8; Sec 4.1 para 2, p7). Practical value is the paper's strongest suit and is stated concretely: MIT licence and a working URL (Availability, p8), unlimited free verification (Sec 4.1 para 2, p7; Table 1 row "Unlimited free usage", p7), and APA 7 and BibTeX output derived from "authoritative metadata retrieved from the scholarly databases rather than potentially erroneous input" (Sec 4 para 3, p7). Because no result is reported, there is no account of why the authors got the results they did — the question does not arise. The conclusion reiterates the problem, the architecture and the significance, but summarises no method beyond the architecture and no results at all. There is **no limitations statement of any kind** (N30) — not on genuine references absent from all three databases, nor on hallucinations that subtly alter real papers, a failure mode the paper itself describes in Sec 1 para 3 (p2). There is **no future work** (N31), **no acknowledgements** and **no funding or conflict-of-interest statement** (N27).

## 3. Discussion

### Importance
The problem is real and timely, but the contribution is a described design for an unevaluated tool, so its significance rests on plausibility rather than any demonstrated detection ability.

- **Location**: Title; Abstract; Section 1 para 1 (p1).
  **Observation**: The title and abstract promise *detection of citation hallucinations*; what the paper delivers is an existence-and-metadata check against three databases, with detection performance never measured.
  **Evidence or criterion**: N1 (no precision, recall, false-positive or false-negative rate anywhere; no Evaluation section); Claim 1 and Claim 3 of the stage 1 extraction.
  **Why it matters**: A reader deciding whether to trust the tool for its headline purpose has nothing to weigh but the design description, so the size of the contribution cannot be distinguished from the size of the claim. *(Not reported.)*

- **Location**: Section 1 para 3 (p2) versus Section 3 para 6 (p6, Eq. 1).
  **Observation**: The paper's own taxonomy of hallucinations includes "subtle alterations of real papers, such as expanding author initials into guessed first names or paraphrasing titles" — and the matcher it then specifies is normalized Levenshtein title similarity with an 80% band, which is designed to treat paraphrases as matches.
  **Evidence or criterion**: Section 1 para 3 (p2); Eq. 1 and Section 3 para 8 (p6).
  **Why it matters**: The class of fabrication the paper uses to establish urgency is the class its central similarity measure is structurally least able to separate, so the motivation and the mechanism are pulling against each other. In fairness, the fabricated-author rule (Section 3 para 7, p6) does target the "guessed first names" case; the title-paraphrase case has no corresponding mechanism. *(Potential design or analysis problem.)*

- **Location**: Section 1 para 3 (p2); the underlying claim, without the figures, in Abstract and Section 5 para 1 (p8).
  **Observation**: The urgency figures that carry the paper — "over 4,000 research papers", "more than 100 AI-hallucinated citations across at least 53 papers", "50 hallucinated citations" at ICLR, "24.52% from over 21,500 submissions" — trace to a single source, Goldman (2026), a *Fortune* article whose own reference-list title ends "new report claims". The report itself is never cited.
  **Evidence or criterion**: N26; References p9, Goldman (2026).
  **Why it matters**: The entire importance case is second-hand press reporting of an uncited document, so a reader cannot check the numbers that justify the tool. *(Not reported.)*

- **Location**: Section 2 para 1 (p2); Section 2 para 3 (p3).
  **Observation**: The Background frames the problem well — cost asymmetry between generating and verifying citations, "citation mutation" propagation, laundering of fabricated references into indexed literature. This is the paper's strongest intellectual content and it is genuinely useful framing.
  **Evidence or criterion**: Section 2 para 1 and para 3; Strzelecki (2024) as cited in Section 2 para 3.
  **Why it matters**: A reader can take the problem framing away from this paper even if the tool claims are set aside — worth saying explicitly, since the framing and the artifact stand or fall separately here.

---

### Credibility
Treat every performance claim as unverified: the paper reports no evaluation at all, and its pseudocode, figure, and prose disagree about the rules that would decide any outcome.

The qualitative trustworthiness checks and the demand-characteristics check are inapplicable (no qualitative study, no participants). The statistical-test checks of `references/quantitative-results.md` are inapplicable in that no test is run — but its **order of assessment** stops at the first step: the target quantity ("what counts as a correct detection") is never defined, so nothing downstream can be assessed.

- **Location**: Section 3 para 2, last sentence (p3); Section 5 para 1 (p8).
  **Observation**: The paper states that the cascade "achieves higher recall than any single-source approach while maintaining precision through multi-source confirmation", and that multi-source validation provides "higher confidence than single-database checks". No recall, precision, or confidence figure for any configuration appears in the paper.
  **Evidence or criterion**: N1; Claims 2 and 8 of the stage 1 extraction; the claim–evidence mismatch category "directionally correct claims that overstate magnitude or precision" in `references/quantitative-results.md`.
  **Why it matters**: These are quantitative comparative claims stated as findings, and a reader has no way to tell whether the cascade helps, hurts, or does nothing. *(Potential design or analysis problem — claim–evidence mismatch.)*

- **Location**: Footnote 2 (p6).
  **Observation**: The thresholds and penalties are said to have been "empirically calibrated to optimize discrimination between valid references and known hallucinations", with author discrepancies weighted more heavily for their "stronger diagnostic signal". No calibration set, size, provenance, labeling procedure, objective, or resulting discrimination is given.
  **Evidence or criterion**: N2; Claim 4 of the stage 1 extraction; the reporting red flags "missing methodological details" and "results don't match methods" in `references/experiment-design.md`.
  **Why it matters**: The specific numbers 50, 70, 80, −20, −10 and +10 are the whole decision procedure, and their justification is an unsupported assertion, so a reader cannot judge whether they transfer to their own bibliography. This is a reporting gap, not evidence of any impropriety. *(Not reported.)*

- **Location**: Abstract; Section 5 para 1 (p8), versus Algorithm 1 lines 2–11.
  **Observation**: "Multi-source validation against CrossRef, Semantic Scholar, and OpenAlex" is presented as how the system works. In Algorithm 1, Semantic Scholar and OpenAlex are queried only inside the `bestScore < 70 or |issues| > 0` branch (line 8), so a reference that passes the CrossRef check is validated by exactly one source.
  **Evidence or criterion**: Algorithm 1 lines 2, 8, 10, 11; Abstract; Section 5 para 1.
  **Why it matters**: The headline architectural claim describes the failure path only. On the nominal success path the tool is a single-database checker, which is the design the paper argues against in Section 3 para 2. *(Demonstrated inconsistency.)*

- **Location**: Algorithm 1 lines 8, 22, 32; Figure 1 nodes "Score > 70%?" and "Score > 80%?".
  **Observation**: The +10 multi-source bonus (line 22) is reachable only from the fallback branch, and existence is returned on the pre-penalty `bestScore` (line 32) rather than on the `confidence` that line 30 computes from the score and the issues. Derived: a reference scoring 69 that triggers fallback and confirms two authors reaches 79, outranking a reference that scored 72 from CrossRef alone and never had a chance at the bonus. A reference carrying a detected issue can still return `exists = true` on a bestScore above 50 while the confidence the user sees has been penalised.
  **Evidence or criterion**: Algorithm 1 lines 8, 22, 30, 32; Figure 1; C6.
  **Why it matters**: `bestScore` is not comparable across paths and is non-monotone in evidence quality — a worse initial match that happens to route through the fallback can outscore a better one — and the boolean a caller reads is computed on a different quantity from the number shown to the user, so neither can be read as a ranking. *(Potential design or analysis problem.)*

- **Location**: Algorithm 1 lines 18–19, 26–27, versus Section 3 para 2 (p3).
  **Observation**: `confirmedAuthors` is the three-way intersection and `suspectAuthors` is everything outside it, which raises a "Potential fabricated authors" issue. A genuine work absent from any one of the three databases has an empty intersection, so all of its authors are flagged.
  **Evidence or criterion**: C3; Algorithm 1 lines 18, 19, 26, 27; Section 3 para 2.
  **Why it matters**: The coverage gap the text says the multi-source design overcomes is, in the pseudocode, converted into a fabrication accusation — the single most consequential failure mode of the tool, pointing in exactly the direction that harms an honest author. *(Demonstrated inconsistency.)*

- **Location**: Algorithm 1 line 23 versus line 31.
  **Observation**: `correctedMetadata` is assigned only inside the `|confirmedAuthors| ≥ 2` branch, itself inside the fallback branch, yet line 31 calls `GENERATEOUTPUTS(correctedMetadata)` unconditionally. Every reference that passes the CrossRef check therefore generates its APA and BibTeX output from an unassigned variable.
  **Evidence or criterion**: C7; Algorithm 1 lines 8, 21, 23, 31.
  **Why it matters**: The pseudocode is the paper's only specification of the artifact, and on its most common path it produces no defined output — so the reader cannot use Algorithm 1 to reason about, or reimplement, what the tool returns. *(Demonstrated inconsistency.)*

- **Location**: Section 3 para 6 (p6, Eq. 1) versus Section 3 para 8 (p6, Eq. 2) and Algorithm 1 line 8.
  **Observation**: Eq. 1 defines `similarity(a,b) = 1 − lev(a,b)/max(|a|,|b|)`, which lies in [0, 1]. Eq. 2 computes `S_title − 0.5 × (100 − S_author)` and the thresholds are 50, 70, 80 with penalties of −20 and −10, all on a 0–100 scale. No rescaling step is stated anywhere.
  **Evidence or criterion**: Eq. 1; Eq. 2; Section 3 para 8; Algorithm 1 line 8.
  **Why it matters**: The only formally defined similarity is on the wrong scale for every formula and threshold that consumes it, so the scoring system as printed does not compute. *(Demonstrated inconsistency.)*

- **Location**: Section 3 para 6 (p6) versus Section 3 para 7 (p6).
  **Observation**: Strings are normalized by "conversion to lowercase and removal of non-alphanumeric characters" before comparison; fabricated authors are then detected as "capitalized tokens in the query". After the stated normalization no capitalized token exists.
  **Evidence or criterion**: C10; Section 3 para 6; Section 3 para 7.
  **Why it matters**: The fabricated-author detector — the paper's distinctive hallucination-detection mechanism — is specified as operating on a string form the preceding paragraph says has been destroyed. *(Demonstrated inconsistency.)*

### Novelty
The design is a competent assembly of three public APIs and Levenshtein matching, and its novelty claim survives mainly because the closest prior work is left out of the comparison.

- **Location**: Section 1 para 4 (p2); Section 4.1 para 1 and Table 1 (p7).
  **Observation**: The gap is established against reference *managers* (Zotero, Mendeley, EndNote, JabRef) — tools that never claimed to validate authenticity — and Table 1's uniqueness rows ("Hallucination detection", "Fake author detection", "Multi-source validation") are checked only against that set.
  **Evidence or criterion**: Table 1; N23 (the commercial hallucination-detection services the paper itself says exist are named nowhere and appear in no column); Claim 5 of the stage 1 extraction.
  **Why it matters**: A novelty claim demonstrated against a comparator set chosen to exclude the actual competitors is not demonstrated, and Section 4.1 para 2's "as the comparison demonstrates" overstates what Table 1 can show. *(Potential design or analysis problem — comparator selection.)*

- **Location**: Section 1 para 3 (p2) and Section 2 para 2 (p3), versus N32.
  **Observation**: Dunford et al. (2024), titled "Using automated analysis of the bibliography to detect potential research integrity issues", is cited twice — for the difficulty of manual detection and for "chimeric" fabrications — but never discussed as a prior automated approach to the paper's own task.
  **Evidence or criterion**: N32; References p9, Dunford et al. (2024); Section 1 para 3; Section 2 para 2.
  **Why it matters**: The paper's own bibliography contains work whose title describes the task it claims is unaddressed, and no positioning against it is offered, so the reader cannot tell what is new. *(Not reported.)*

- **Location**: Section 3 para 6 (p6, Eq. 1); Section 3 para 7 (p6).
  **Observation**: The components are standard: normalized Levenshtein on lowercased alphanumeric titles, family-name containment, and an unweighted mean of four field similarities. The one non-obvious idea is the cross-source author intersection as a fabrication signal (Algorithm 1 lines 18–19).
  **Evidence or criterion**: Eq. 1, Eq. 3, Algorithm 1 lines 18–19; N42 (the abstract's plural "string similarity algorithms" corresponds to one described algorithm, C17).
  **Why it matters**: The cross-source intersection is the paper's genuine idea and is worth a reader's attention, but it is also the mechanism that C3 shows misfires on coverage gaps and that N1 shows was never measured — so the one novel element is the one with no evidence behind it. *(Not reported.)*

- **Location**: Section 3 para 3 (p3–4); Algorithm 1 line 1.
  **Observation**: Automatic LaTeX-command filtering on pasted references is a small, practical, and plausibly new convenience in this niche.
  **Evidence or criterion**: Section 3 para 3; Algorithm 1 line 1; N3 (the command set and custom-macro handling are unspecified).
  **Why it matters**: This is real incremental value for LaTeX users, and naming it separately keeps the novelty judgment honest — the contribution is not zero, it is small and workflow-level.

---

### Applicability
A free, MIT-licensed, URL-accessible web tool is immediately usable, but the paper gives a reader no error rate, no example, and no version, so adoption is a leap of faith.

- **Location**: Availability (p8); footnote 1 (p1); Table 1 rows "Open source" and "Unlimited free usage" (p7).
  **Observation**: The tool is stated to be MIT-licensed, unlimited, and live at a given URL, which is the paper's clearest practical strength.
  **Evidence or criterion**: Claim 9 of the stage 1 extraction; Availability; footnote 1.
  **Why it matters**: Low-friction access and a permissive license genuinely lower the barrier for individual researchers, and the BibTeX round-trip described in Section 4.1 para 2 (p7) fits an existing Zotero-to-LaTeX workflow without new infrastructure.

- **Location**: Section 4 (pp6–7); Section 3 (pp3–6).
  **Observation**: The paper contains no example input, no example output, no screenshot, and no walked-through case — genuine or fabricated.
  **Evidence or criterion**: N36; N41 (the output path for a wholly fabricated reference is never traced).
  **Why it matters**: A reader cannot see what a flag looks like, how a fabrication is reported, or how to interpret a "Partial Match", so they cannot plan how to act on the tool's output. *(Not reported.)*

- **Cross-reference**: the highest-stakes applicability problem — reviewers and publishers advised to act on an unquantified fabrication flag (Section 5 para 1, pp7–8) — is carried under **Ethics**, the dimension whose verdict it moves most.

- **Location**: Section 3 para 1 (p3); Availability (p8).
  **Observation**: No software version, release date, source-repository location (only the GitHub Pages site), dependency list, or test suite is given, and Section 3 para 1 names only "React with TypeScript".
  **Evidence or criterion**: N22.
  **Why it matters**: A reader cannot cite a version, reproduce a result, audit the Levenshtein or APA-formatting implementations, or tell whether the live site still matches the paper. *(Not reported.)*

- **Location**: Section 4 para 2 (p6–7); Section 3 para 1 (p3).
  **Observation**: Behavior on API error, timeout, or rate-limit rejection is never described, and whether requests originate in the browser or from a server is not stated.
  **Evidence or criterion**: N15; N20.
  **Why it matters**: For batch auditing of a long bibliography, a transient API failure and a genuine non-existence are operationally indistinguishable unless the tool distinguishes them, and the paper does not say it does. *(Not reported.)*

---

### Generalizability
Reach beyond DOI-registered English-language journal articles is asserted rather than shown, and the paper's own coverage caveats predict the failures.

- **Location**: Section 3 para 2 (p3).
  **Observation**: The paper itself states that CrossRef "may lack coverage of preprints, regional journals, or older publications" and that OpenAlex "metadata quality varies", then never says what the tool outputs for such works, or for books, theses, and reports.
  **Evidence or criterion**: N16; Section 3 para 2; C3.
  **Why it matters**: Whole reference genres fall outside the validated region, and by C3 they are pushed toward a fabrication flag rather than an "unknown" verdict, so the tool's verdict is least trustworthy exactly where a user cannot tell. *(Potential design or analysis problem.)*

- **Location**: References, pp8–9.
  **Observation**: Derived — of the paper's own 23 reference entries, 3 (13%) belong to genres the paper names as coverage risks: Merton (1973), a University of Chicago Press monograph; Priem et al. (2022), an arXiv preprint; Goldman (2026), a *Fortune* news article.
  **Evidence or criterion**: References pp8–9 (counted); Section 3 para 2 (p3, the coverage caveats); N16.
  **Why it matters**: The paper's own bibliography is a ready test set on which roughly one entry in eight sits in the unvalidated region, and the paper never runs it. *(Potential design or analysis problem.)*

- **Location**: Section 3 para 7 (p6).
  **Observation**: Author matching works by extracting family names and checking their presence in the query string, with fabricated authors detected as capitalized tokens; handling of initials, "et al.", diacritics, hyphenated or multi-part family names, and non-Western name order is not specified, and Section 3 para 6's removal of non-alphanumeric characters alters hyphenated names.
  **Evidence or criterion**: N10; Section 3 para 6 (p6).
  **Why it matters**: The design embeds Western, English-capitalized name conventions, so a reader working with Spanish, Chinese, Vietnamese, or transliterated Turkish or Arabic names cannot assume the reported behavior holds — and the paper's own reference list contains Taşkın, Céspedes, Kratochvíl, and Świgoń. *(Not reported.)*

- **Cross-reference**: the calibration population behind the 50/70/80 thresholds is undefined (footnote 2, p6; N2), which is why external validity cannot be assessed at all here; the point is carried under **Credibility**.

- **Location**: Section 3 para 2 (p3).
  **Observation**: Semantic Scholar is described as providing "strong coverage of computer science and biomedical literature"; the tool is presented as discipline-general.
  **Evidence or criterion**: Section 3 para 2; N1.
  **Why it matters**: Two of the three sources have stated disciplinary or genre skews, and no per-discipline result exists, so the "multi-source confirmation" argument is strongest in CS and biomedicine and weakest where the coverage gaps concentrate. *(Not reported.)*

---

### Scalability
Single-reference use is comfortable at the stated pacing, but the publisher-pipeline and bibliometric-dataset scales the paper claims have no in-paper figure that supports them.

- **Location**: Section 4 para 2 (p7).
  **Observation**: The only throughput figure in the paper is sequential batch processing with "rate limiting (800ms intervals)". Derived from that figure: 1.25 references/second, 75/minute, and 86,400 / 0.8 = **108,000 references per day** on one sequential stream. A 50-entry bibliography costs 50 × 0.8 = **40 s** of pacing delay before any API latency.
  **Evidence or criterion**: Section 4 para 2 (p7) — the 800 ms figure; derived.
  **Why it matters**: Individual and per-manuscript use is clearly fine, and stating the rate lets a reader size their own job. This is the only scale the paper's own numbers support.

- **Location**: Section 5 para 1 (pp7–8).
  **Observation**: The paper claims "Publishers can integrate reference validation into submission pipelines" and that bibliometricians "conducting large-scale bibliometric analyses can filter potentially spurious references from datasets". Derived, using the paper's own NeurIPS figure of "over 4,000 research papers" (Section 1 para 3, p2) and, since the paper states no references-per-paper multiplier, taking 23 references/paper from the length of its own reference list (References, pp8–9): 4,000 × 23 = 92,000 references; × 0.8 s = 73,600 s = **20.4 hours** of pacing delay for one conference's proceedings on a single stream. A one-million-reference bibliometric dataset: 1,000,000 × 0.8 s = **9.3 days**.
  **Evidence or criterion**: Section 4 para 2 (800 ms); Section 1 para 3 (4,000 papers); References pp8–9 (23 entries, used as the multiplier); derived.
  **Why it matters**: Recomputed against the 108,000 references/day ceiling derived above, one conference's proceedings consumes about 0.85 of a day and the million-reference dataset about nine days on a single stream, and no parallelism, server-side batching, or caching is described — so the publisher-pipeline and dataset-filtering claims read as unsupported. *(Potential design or analysis problem.)*

- **Location**: Algorithm 1 lines 2, 4, 10, 11.
  **Observation**: The fallback branch issues two extra API calls per reference (lines 10–11), and when CrossRef returns nothing Semantic Scholar is queried twice (lines 4 and 10). Derived: with fallback triggered on every reference, the paper's own 23-entry bibliography issues 23 × 3 = **69 API requests**, and the outbound request rate becomes 3 / 0.8 = **3.75 requests/second** even though pacing is described per entry, not per call.
  **Evidence or criterion**: Algorithm 1 lines 2, 4, 10, 11; Section 4 para 2 (800 ms per entry); C9 (duplicate Semantic Scholar query); derived.
  **Why it matters**: The compliance claim in Section 4 para 2 is about entry pacing while the load on the APIs is up to 3–4× that, and N15 records that no actual policy limit is quoted anywhere — so a reader cannot tell whether batch mode stays within any provider's terms. *(Potential design or analysis problem.)*

- **Location**: Section 3 para 1 (p3); Availability (p8).
  **Observation**: The application is browser-based and served from GitHub Pages, and the paper never says whether queries are issued from the browser or a server, nor whether any result is cached.
  **Evidence or criterion**: N20; N22.
  **Why it matters**: If execution is client-side, throughput is per-user-browser and cannot be pooled, and bibliometric datasets — which contain the same references thousands of times — would be re-queried without a cache, making the large-scale claim worse than the derived figures suggest. *(Not reported.)*

- **Location**: Algorithm 1 line 2.
  **Observation**: Only three CrossRef candidates are retrieved per query (`rows = 3`), and Figure 1's "Retrieve Top 3 Candidates" matches.
  **Evidence or criterion**: Algorithm 1 line 2; N35 (the ranking producing the top 3 is not stated).
  **Why it matters**: The per-query cost is deliberately held constant, which is good for scale, but it means recall is bounded by CrossRef's relevance ranking placing the correct record in its first three hits — a fixed ceiling that no amount of scale relieves. *(Potential design or analysis problem.)*

---

### Assumptions
The method rests on at least a dozen premises about database coverage, name forms, and score scales that the paper does not state, and its own text contradicts several of them.

- **Location**: Algorithm 1 line 3 (`if candidates = ∅`).
  **Observation**: The empty-result branch presumes that a non-existent reference yields no CrossRef candidates, while line 8's score threshold presumes non-empty candidates with low scores. A relevance-ranked text search over 140 million records (Section 3 para 2, p3) will normally return three nearest neighbours for any non-empty query.
  **Evidence or criterion**: Algorithm 1 lines 2, 3, 8; N41.
  **Why it matters**: Which branch actually fires for a fabricated reference determines the tool's core behavior, and the paper specifies two mutually exclusive stories without saying which holds. The paper does not state this assumption. *(Potential design or analysis problem.)*

- **Location**: Algorithm 1 line 32 (`exists : bestScore > 50`).
  **Observation**: Existence is decided by similarity to a retrieved record, which assumes that absence from all three databases implies non-existence and that presence implies the citation is genuine as used.
  **Evidence or criterion**: Algorithm 1 line 32; Section 3 para 2 (p3, the stated coverage gaps); N16.
  **Why it matters**: Both directions fail in ways the paper's own Section 3 para 2 predicts — an uncovered monograph reads as non-existent, and a retracted, predatory, or merely different-but-similar record reads as verification. Neither assumption is stated. *(Potential design or analysis problem.)*

- **Location**: Section 3 para 6 (p6, Eq. 1).
  **Observation**: Using normalized Levenshtein distance on titles assumes edit distance is monotone in "same work" and that compared titles are of comparable length; behavior on very short titles and on subtitles is unspecified.
  **Evidence or criterion**: N34; Eq. 1; Section 1 para 3 (p2, hallucinations that paraphrase titles).
  **Why it matters**: A short title makes each edit costly and a paraphrase makes many edits cheap relative to length, so the measure is most permissive precisely where the paper's threat model needs it strictest. The paper does not state the assumption. *(Potential design or analysis problem.)*

- **Location**: Section 3 para 7 (p6, family-name containment).
  **Observation**: Author matching assumes family names appear verbatim in the query string and that containment implies authorship agreement. The check is one-directional: a query listing many names contains any subset of a record's names.
  **Evidence or criterion**: N10; Section 3 para 7; Eq. 3 (S_author enters the score).
  **Why it matters**: Extra fabricated names in a query cannot lower the containment proportion, so the author-similarity component is blind to insertion — the exact hallucination mode Section 3 para 7 says the design detects. Not stated. *(Potential design or analysis problem.)*

- **Location**: Section 3 para 7 (p6, "capitalized tokens in the query that match neither title words, journal name, year, nor any real author family name").
  **Observation**: The fabricated-author rule assumes the listed exclusions exhaust the capitalized non-author tokens in a citation string. Publisher names, cities, editor names, series titles, conference names, and "In Proceedings of" are not excluded.
  **Evidence or criterion**: Section 3 para 7; C10; References p9, Merton (1973) ("University of Chicago Press").
  **Why it matters**: Applied to the paper's own Merton entry, "University", "Chicago", and "Press" are capitalized tokens matching no excluded category, so each would be reported as a potential fabricated author and penalized. The exhaustiveness assumption is not stated. *(Potential design or analysis problem.)*

- **Location**: Algorithm 1 line 18 (three-way intersection).
  **Observation**: Intersecting author sets assumes all three sources index the work *and* record author names in comparable string form — CrossRef stores given and family names separately, while the other two commonly return full-name strings.
  **Evidence or criterion**: Algorithm 1 lines 14–18; N8 (field-conflict resolution unspecified); N10.
  **Why it matters**: If normalization across sources is imperfect, the intersection empties and, by C3, every author is flagged — turning a string-format mismatch into a fabrication report. Not stated. *(Potential design or analysis problem.)*

- **Location**: Algorithm 1 line 21 (`|confirmedAuthors| ≥ 2`).
  **Observation**: The multi-source bonus requires at least two confirmed authors, which a single-author work can never satisfy. Derived: 6 of the paper's own 23 reference entries (26%) are single-author — Garfield (1972), Goldman (2026), Kratochvíl (2017), Merton (1973), Strzelecki (2024), Taşkın (2025).
  **Evidence or criterion**: N40; Algorithm 1 line 21; References pp8–9 (counted); derived.
  **Why it matters**: A quarter of this paper's own bibliography — and the paper is itself single-authored — is systematically denied the confirmation bonus and so is systematically scored lower, an assumption about authorship cardinality that the paper never states. *(Potential design or analysis problem.)*

- **Location**: Section 3 para 8 (p6, Eq. 3).
  **Observation**: Eq. 3 assumes title, author, journal, and year similarities are on a common scale and equally informative, since it takes their unweighted mean. S_journal and S_year are never defined, and Eq. 2's −0.5 coefficient is given without justification.
  **Evidence or criterion**: N11; N13; Eq. 2; Eq. 3; footnote 2 (p6, which claims author discrepancies are weighted more heavily — contradicted by the equal weights, C11).
  **Why it matters**: Equal weighting contradicts the paper's own stated rationale for the weights, and two of the four components have no definition, so the composite cannot be computed or audited. *(Demonstrated inconsistency.)*

- **Location**: Section 3 para 8 (p6, the Eq. 2 and Eq. 3 conditions).
  **Observation**: Eq. 2 applies when "title similarity exceeds 80% but author similarity falls below 90%"; Eq. 3 applies "For structured input with high matching across all fields". Derived: for structured input with S_title = 81, S_author = 89, S_journal = S_year = 100, both conditions hold, and Eq. 2 gives 81 − 0.5 × 11 = **75.5** while Eq. 3 gives (81 + 89 + 100 + 100)/4 = **92.5**, up to **102.5** with the bonus — a 27-point spread straddling Figure 1's 80% Verified gate. Derived further: Eq. 3's maximum is 100 + 10 = **110**, above the 100% scale Figure 1 reports.
  **Evidence or criterion**: N12; N13; Eq. 2; Eq. 3; Figure 1 ("Score > 80%?"); derived.
  **Why it matters**: The assumption that the two formulas' domains are disjoint and bounded is false on both counts, and no precedence rule is given, so the same input can be Verified or a Partial Match depending on an unstated choice. *(Demonstrated inconsistency.)*

- **Location**: Algorithm 1, Require line ("optional expected metadata E").
  **Observation**: The procedure declares an input E that no subsequent line uses.
  **Evidence or criterion**: N18; Algorithm 1 lines 1–32.
  **Why it matters**: The interface assumes a caller-supplied expectation that the specification never consumes, so a reader cannot tell whether comparison against user-declared metadata is part of the method. *(Demonstrated inconsistency.)*

- **Location**: Section 4 para 2 (p7, "800ms intervals to comply with API usage policies").
  **Observation**: The method assumes unauthenticated, key-free, quota-free access to all three APIs at that pacing, with no mention of API keys, a CrossRef polite-pool contact, or per-source limits.
  **Evidence or criterion**: N15.
  **Why it matters**: The tool's central promise of unlimited free verification rests entirely on this assumption about third-party terms, and it is stated only as an unsourced claim of compliance. *(Not reported.)*

The statistical-test assumptions in `references/quantitative-results.md` are inapplicable — no test is performed. The counterfactual and variable-definition checks in `references/experiment-design.md` are inapplicable in the causal sense, but the construct-validity requirement bites: the key construct, "reference exists / is hallucinated", is operationalized only as `bestScore > 50` (Algorithm 1 line 32) against undefined component measures, which is not an operationalization another party could repeat.

---

### Readability
Clearly written and easy to follow as prose, but the notation is incomplete and the scoring rules cannot be reconstructed from what the paper defines. *(Readability moves no other verdict here.)*

- **Location**: Section 1 (pp1–2); Section 2 (pp2–3).
  **Observation**: The Introduction and Background are well-organized, flow logically from the function of citations to the economics of cheap fabrication, and use no unnecessary jargon.
  **Evidence or criterion**: Section 1 paras 1–5; Section 2 paras 1–3.
  **Why it matters**: A reader reaches the system description with the problem clearly in hand, which is the paper's genuine writing strength.

- **Location**: Section 3 para 8 (p6, Eq. 3); Section 3 para 6 (p6).
  **Observation**: S_journal and S_year appear in Eq. 3 with no definition, only S_title is defined (Eq. 1), and β_ms is described as a range while Algorithm 1 line 22 adds a constant.
  **Evidence or criterion**: N11; N14; C5.
  **Why it matters**: Three of the four terms in the paper's central formula are undefined or ambiguously defined, so the scoring section cannot be read as a specification even by a careful reader. *(Not reported.)*

- **Location**: Figure 1 (p5); Section 3 para 8 (p6); Section 4 (pp6–7).
  **Observation**: The user-facing states "Verified", "Partial Match", "Corrected Citation", and the "Mismatch" edge appear only in Figure 1 and are never described in the text, and the 50 threshold appears only in Algorithm 1.
  **Evidence or criterion**: N17; N39; C6.
  **Why it matters**: Figure and text describe non-overlapping parts of the same output vocabulary, so the reader must reverse-engineer what the tool tells a user. *(Not reported.)*

- **Location**: Figure 1 (p5) versus Algorithm 1 line 32.
  **Observation**: Every path in Figure 1 terminates in "Generate APA + BibTeX" — there is no terminal state corresponding to `exists = false`, even though Algorithm 1 line 32 returns existence as a boolean.
  **Evidence or criterion**: Figure 1; Algorithm 1 line 32; N41.
  **Why it matters**: The figure of a hallucination-detection pipeline has no "not found" outcome drawn on it, which is the one outcome the title is about. *(Demonstrated inconsistency.)*

- **Location**: Section 2 para 3 (p3); Section 2 para 2 (pp2–3); Section 2 para 1 (p2); Abstract.
  **Observation**: Register is inflated relative to a tool paper: "unprecedented challenges", "a classic market failure", "negative externalities", "path-dependent vulnerabilities", "sophisticated verisimilitude", "chimeric", "laundering fabricated references". The Conclusions section opens with a use-case list rather than conclusions.
  **Evidence or criterion**: Abstract; Section 2 paras 1, 2 and 3; Section 5 para 1; stage 1 extraction (no Evaluation, Limitations, Discussion, or Future Work section exists).
  **Why it matters**: Economics and epistemology vocabulary carries rhetorical weight the evidence base does not, and the absence of Evaluation and Limitations sections means the structure never reaches the place a reader looks for caveats. *(Potential design or analysis problem — reporting structure.)*

- **Location**: Section 1 para 4 (p2); Section 3 para 2 (p3); Table 1 (p7).
  **Observation**: "DOI" is used on p2 before "Digital Object Identifier" appears on p3, and the acronym is never attached to the expansion. Table 1 marks "Bibliography formatting ✓" for a tool whose only stated outputs are APA 7 and BibTeX, and gives no definitions distinguishing its rows "Immediate validation", "Hallucination detection", "Fake author detection", and "Multi-source validation".
  **Evidence or criterion**: C16; N25; N33.
  **Why it matters**: The comparison table, which carries the paper's positioning argument, uses four feature labels a reader cannot tell apart. *(Not reported.)*

---

### Ethics
No human subjects are involved, yet the paper recommends accusatory uses to reviewers and publishers with no measured error rate, no limitations section, and no disclosure statement of any kind.

The questions in `references/participants.md` are inapplicable: no people took part, so consent, IRB, compensation, deception, and debriefing do not arise.

- **Location**: Section 5 para 1 (pp7–8).
  **Observation**: The paper advises reviewers to identify "potential fabrications warranting author clarification" and publishers to run submissions through the tool, while the mechanism producing that flag (Algorithm 1 lines 26–27) fires whenever any author falls outside the three-way intersection.
  **Evidence or criterion**: C3; N1; N30 (no limitation is stated anywhere).
  **Why it matters**: An unquantified false-positive rate on a mechanism that outputs "Potential fabricated authors" is being recommended into peer review and editorial screening, where a false flag can attach an accusation of fabrication to an honest author with a monograph or a regional-journal citation. The paper shows no awareness of this consequence. *(Potential design or analysis problem.)*

- **Location**: Section 5 para 1 (pp7–8); Section 3 para 1 (p3).
  **Observation**: The intended inputs include bibliographies of unsubmitted manuscripts and of manuscripts under confidential review, and the paper states nothing about where queries are issued from, whether input is stored, or whether anything is sent to a third party.
  **Evidence or criterion**: N20; N21; Section 5 para 1.
  **Why it matters**: Using the tool as advised transmits the reference list of a confidential manuscript to three external APIs, and a reviewer bound by peer-review confidentiality is given no information with which to judge whether that is acceptable. The privacy and data-handling questions in `references/participants.md` apply to the data, not to participants, and are unanswered. *(Not reported.)*

- **Location**: Front matter (author block, p1); end matter (Availability, p8).
  **Observation**: There is no funding statement, no conflict-of-interest statement, no acknowledgements, and no statement of any relationship between the author and the databases queried or the tools compared in Table 1.
  **Evidence or criterion**: N27; N29; the red flag "no conflicts-of-interest statement at all" in `references/research-integrity.md`.
  **Why it matters**: The paper makes competitive claims against four named commercial and open-source products and against unnamed paid services, and a reader has no basis for assessing independence. Described neutrally: the statements are absent, which is a disclosure gap and not by itself evidence of any undisclosed interest. *(Integrity concern.)*

- **Location**: Abstract; Section 1 para 4 (p2); Section 4.1 para 2 (p7).
  **Observation**: Competitors are characterized as imposing "restrictive usage limits" and "substantial subscription fees" without any of them being named, dated, or priced, and the supporting citation, Zhu et al. (2025), is titled "Evaluating the potential risks of employing large language models in peer review".
  **Evidence or criterion**: N23; C13; Claim 6 of the stage 1 extraction.
  **Why it matters**: Unnamed competitors cannot answer a characterization of their pricing, and the one citation offered does not, by its own title, cover commercial services or prices — so the fairness claim that differentiates this tool rests on an unverifiable comparison. *(Potential design or analysis problem.)*

- **Location**: Section 5 para 2 (p8).
  **Observation**: The Conclusions close on the tool supporting "human judgment in maintaining citation integrity", which is the right framing, but no limitation, failure mode, or caution accompanies it anywhere in the paper.
  **Evidence or criterion**: N30; N31; Section 5 para 2.
  **Why it matters**: The paper gestures at the tool being advisory while giving a user nothing to be sceptical with, so in practice a "Verified" or "Potential fabricated authors" label arrives with the authority of an unqualified verdict. *(Not reported.)*

- **Location**: Section 1 para 3 (p2); Section 5 para 1 (pp7–8).
  **Observation**: The NeurIPS and ICLR hallucinated citations that motivate the paper are never run through the tool.
  **Evidence or criterion**: N44; N1; Claim 3 of the stage 1 extraction.
  **Why it matters**: A named, public, already-identified set of hallucinated citations is available as a test set and is used only rhetorically — the cheapest available check on whether the tool does what the title says was not performed or not reported. *(Not reported.)*

### What this report did not check

- **Web-dependent slots skipped**: web access was not allowed for this run. Not checked, all for that reason: the author's field and prior work; tree-forward (whether more recent work citing the paper's key references is conspicuously missing); the count of references from the authors' own institution; citation metadata, DOIs and link correctness for all 23 references, including whether every cited work exists; whether each cited paper supports the claim attached to it beyond what its title in the reference list shows; the identity, free-tier limits and prices of the "commercial hallucination detection services" the paper critiques (N23); the current feature sets and versions of Zotero, Mendeley, EndNote and JabRef behind Table 1 (N24); whether Nicholas et al. (2025) reports the fabricated-author frequency it is cited for (N38); whether either JASIST volume number in C15 is the correct one; and whether the deployed tool, its repository, its MIT licence file and its "within seconds" behaviour are as stated (Claims 1, 7, 9).
- **Parts of the paper not read or not readable**: none — all 9 pages were read, and the two pages carrying Algorithm 1 (p4) and Figure 1 (p5) were also read as page images. The paper has no appendix, no supplement and no data availability statement. The source code was **not inspected**: the paper gives only a GitHub Pages URL (footnote 1, p1; Availability, p8), reaching it needs web access, and no repository, version or release date is stated (N20, N22). Every statement here about the tool's behaviour is a statement about the paper's description of it, never about the running software.
- **Proofs or analyses not followed in detail**: the paper contains no proof and no statistical analysis, so none was skipped. Algorithm 1's 32 lines, Figure 1's control flow and Equations 1–3 were traced by hand against the prose, which is where the inconsistencies C1–C11 come from; that trace is a reading of the pseudocode as written, not an execution of the implementation, so a discrepancy found in Algorithm 1 may or may not be present in the deployed code.
- **Statements resting on recall rather than on the paper**: two, quarantined here rather than presented as findings. First, the Context "tree backward" judgement that Garfield (1972), Merton (1973), MacRoberts and MacRoberts (1996), Simkin and Roychowdhury (2003), Hendricks et al. (2020), Ammar et al. (2018) and Priem et al. (2022) are the field's recognised foundational and infrastructure references, and that the list contains nothing idiosyncratic, is recall by construction and was not verified against any index. Second, the References-check observation that some cited papers are familiar is likewise recall. Third, a stage 3 finding that the identifier stamp's "arXiv:2602.15871v1 ... 27 Jan 2026" (p1) is internally inconsistent — 2602 reading as February 2026 against a January date — rests on recall of arXiv's YYMM identifier convention, which the paper nowhere states; it is quarantined here and was removed from the Discussion rather than presented as a finding. None of the three carries any point in the Discussion.


### Appendix: not-stated list, inconsistency list, verifier list

#### Not-stated list

N1. Any evaluation of the tool — precision, recall, accuracy, false-positive or false-negative rate on genuine versus hallucinated references. Not given anywhere; the recall/precision claim (Sec 3 para 2, last sentence) and the "higher confidence" claim (Sec 5 para 1, p8) have no reported measurement. There is no Evaluation section.

N2. The calibration behind footnote 2 (p6): the dataset of "valid references and known hallucinations" (size, provenance, how hallucinations were obtained or labeled), the calibration procedure, the objective optimized, and the resulting discrimination. Only the sentence in footnote 2 exists.

N3. The set of LaTeX commands removed by FILTERLATEXCOMMANDS (Algorithm 1 line 1 "etc."; Sec 3 para 3 "such as \vspace, \hspace, \textit, or custom macros") and how custom macros are recognized.

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

#### Inconsistency list

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

#### Stage 3 return accounting

- Points returned by the stage 3 subagent: **57** (Importance 4, Credibility 11, Novelty 4, Applicability 5, Generalizability 5, Scalability 5, Assumptions 11, Readability 6, Ethics 6).
- Points dropped on return for want of evidence: **1**. The Credibility point on the venue being an unreviewed preprint carried, as its whole Evidence field, "Stage 1 extraction, Venue / Status row" — not a Location in the paper, not a numbered N- or C- entry, and not a numbered stage 1 claim. The fact itself is reported in the Context "Venue" slot.
- Downgraded at assembly: **1**. The Credibility point on the identifier stamp's 2602 / 27 Jan 2026 mismatch depends on recall of arXiv's YYMM convention, which the paper does not state; it was moved to "What this report did not check" rather than presented as a finding.
- Removed by stage 4: **3** of the 55 assembled. Two duplicate groups collapsed — the reviewer/publisher advice at Section 5 para 1 (pp7-8), held under Ethics with a cross-reference left under Applicability; and footnote 2's unreported calibration, held under Credibility with a cross-reference left under Generalizability. One hedge removed for repeating a "did not check" entry — the reference-list volume-year point, whose adjudication needs the external check already listed there; the observable pattern survives as C15.
- Points in the delivered Discussion: **52**.

#### Stage 5 verifier list, with dispositions

The verifier checked 278 items (every Location field in the body and the appendix lists, every quoted passage, every number attributed to the paper) and failed 7. All 7 were corrected in place; none was removed and none was moved to "What this report did not check".

1. **Readability, register point** — the Location listed Abstract, Section 2 para 1 and Section 2 para 3, but "sophisticated verisimilitude" and "chimeric" are in Section 2 para 2 (pp2–3). *Corrected*: Section 2 para 2 added to the Location and to the Evidence field.
2. **Importance, urgency-figures point** — the Location said the figures are "repeated in Abstract and Section 5 para 1"; both places repeat the claim without any number. *Corrected*: the Location now reads that the underlying claim, without the figures, appears at those two places.
3. **Credibility, score-comparability point** — the point said existence *and the Verified label* are decided on `bestScore`; Figure 1 puts its "Score > 80%?" gate downstream of "Compute Confidence Score", so Verified is decided on the computed confidence, and Algorithm 1 line 32 contains no Verified label. *Corrected*: the point now rests only on what the two locations support — existence returned on the pre-penalty `bestScore` while the user-facing confidence is penalised — and the derived 78 → 88 "clears the Verified gate" example was withdrawn. The 69 → 79 versus 72 non-monotonicity, which rests on lines 22 and 32 alone, was recomputed and stands.
4. **Readability, acronym point** — "two pages later" for the DOI expansion; the gap is p2 to p3, one page. *Corrected* to "on p2 before ... appears on p3".
5. **Novelty, standard-components point** — Eq. 3 described as a "weighted mean"; it is the unweighted mean of four similarities plus β_ms. *Corrected* to "an unweighted mean of four field similarities", which is also what the Assumptions point and C11 rely on.
6. **Applicability, access point** — the Zotero-export-validate-reimport round trip attributed to Section 4.1 para 1, which is the single sentence introducing Table 1. *Corrected* to Section 4.1 para 2 (p7).
7. **Summary, Discussion slot** — "unlimited free use" attributed to Sec 4 para 3 and Availability; it appears at Section 4.1 para 2 and in Table 1's "Unlimited free usage" row. *Corrected*: each of the three practical-value facts now carries its own Location, and the APA/BibTeX provenance is quoted from Sec 4 para 3 verbatim.
