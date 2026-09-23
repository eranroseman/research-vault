Report written to `/tmp/run-F/stage3-return.md` (70 points, nine dimensions). Full text follows.

# Stage 3 judgement: CheckIfExist (Abbonato, 2026, arXiv:2602.15871v1)

Paper type, from the extraction: **Systems**, the nearest of the seven. The extraction names the mismatch and it holds: the paper is a tool description with an architecture, a pipeline figure, pseudocode, three scoring equations and a feature grid, and it reports no deployment data, no scalability measurement and no evaluation. Each dimension below is judged against the systems bar of architecture decisions, scalability evidence, real-world deployment and engineering contribution, and against the paper's own stated claim rather than against gains it never claimed. The venue is a moderated preprint server with no peer review, so review rigor adds no weight here.

## Importance

The problem is real and timely, but the paper's contribution is an unevaluated tool whose output measures database absence rather than the hallucination the title promises.

- **Kind**: Potential design or analysis problem.

- **Location**: Title; Abstract; Section 1, paragraph 3 (p. 2); Algorithm 1, line 32.

- **Observation**: The title and abstract promise detection of citation hallucinations, and Algorithm 1 operationalises that as a database match score above 50, while the paper's own Section 1 describes hallucinations that are "subtle alterations of real papers" and would match the real record with high title similarity.

- **Evidence or criterion**: Title; Section 1, paragraph 3; Algorithm 1, line 32; N28; C11; Claim 1.

- **Why it matters**: A reader is told the tool detects hallucination when it detects non-match, so a chimeric or lightly altered fabrication can be returned as existing and an unindexed real work as non-existent.

- **Kind**: Not reported.

- **Location**: Abstract; Section 3, paragraph 2; Section 4.1, paragraph 2.

- **Observation**: The contribution is stated as immediate, multi-source, high-recall verification, and no part of the paper measures accuracy, precision, recall, error rate or latency for any reference.

- **Evidence or criterion**: N1; N3; Claim 1; Claim 4.

- **Why it matters**: On the systems bar the engineering contribution is the only leg the paper stands on, because deployment evidence and performance evidence are absent.

- **Kind**: Not reported.

- **Location**: Section 1, paragraph 3 (p. 2).

- **Observation**: The load-bearing motivating figure of "more than 100 AI-hallucinated citations across at least 53 papers" is given without the prevalence, without the analyst's identity, and without the primary source's own warning against automatic not-found classification.

- **Evidence or criterion**: Section 1, paragraph 3; W8; N25; Claim 9.

- **Why it matters**: W8's primary source reports roughly one to two percent of accepted papers, was produced by a commercial AI-detection vendor of the category the paper positions itself against, and recommends human confirmation, all of which changes how urgent and how automatable the problem looks.

- **Kind**: Demonstrated inconsistency.

- **Location**: Section 1, paragraph 3 (p. 2), sentences 2 and 5.

- **Observation**: The paragraph gives "over 4,000 research papers accepted and presented" and, three sentences later, an acceptance rate of 24.52 percent from over 21,500 submissions, which is about 5,272 accepted papers, derived, and treats the two figures as one population.

- **Evidence or criterion**: Section 1, paragraph 3; C12; W8.

- **Why it matters**: The reader cannot recover the denominator the paper's urgency argument rests on, and W8 shows the examined set was 4,841 of 5,290, not the accepted population.

- **Kind**: Not reported.

- **Location**: Section 1, paragraph 3 (p. 2).

- **Observation**: The ICLR figure of "50 hallucinated citations" carries no citation at all.

- **Evidence or criterion**: Section 1, paragraph 3; N24.

- **Why it matters**: Half of the paper's evidence that the problem reaches premier venues is untraceable.

- **Kind**: Not reported.

- **Location**: Section 2, paragraph 1 (p. 2).

- **Observation**: The "25% to 54%" error-rate range is attributed to two sources without saying which bound comes from which, what counts as an inaccuracy, or over what populations.

- **Evidence or criterion**: Section 2, paragraph 1; N23; W5.

- **Why it matters**: The background argument that citation error is already common cannot be checked, and one of the two cited sources is misreferenced, as W5 records.

## Credibility

Nothing in the paper tests the tool, and its pseudocode, equations, figure and prose contradict one another at load-bearing points, so no claim about accuracy or behaviour can be trusted as stated.

- **Kind**: Not reported.

- **Location**: Section 3, paragraph 2; footnote 2 (p. 6).

- **Observation**: The paper claims higher recall than any single source, maintained precision, and empirically calibrated thresholds, and reports no dataset, labelled set, objective, or result behind any of them.

- **Evidence or criterion**: N1; N2; Claim 4; Claim 6; quantitative-methods.md "Reporting red flags: missing methodological details".

- **Why it matters**: Every performance statement in the paper is an assertion, and the reader has no basis to prefer the cascade over a single CrossRef query.

- **Kind**: Integrity concern.

- **Location**: Footnote 2 (p. 6); Availability (p. 8).

- **Observation**: Footnote 2 states that thresholds "were empirically calibrated to optimize discrimination between valid references and known hallucinations", and the public repository contains a batch-analysis script over six named dataset folders but no data, no results and no test directory, so an evaluation was at least scaffolded and is not reported.

- **Evidence or criterion**: Footnote 2; W12; N2; research-integrity.md "a tried-and-dropped analysis left unmentioned".

- **Why it matters**: The discrepancy is observable and neutral; a benign reading is that the evaluation is ongoing or destined for a separate paper, but as it stands the calibration claim has no visible support and the reader cannot tell whether the calibration favoured the tool.

- **Kind**: Demonstrated inconsistency.

- **Location**: Algorithm 1, lines 8, 21, 23, 31.

- **Observation**: `correctedMetadata` is assigned only at line 23, inside two nested conditions, and is read unconditionally at line 31, so on the ordinary success path of a score of 70 or more with no issues the output generator has no input.

- **Evidence or criterion**: Algorithm 1, lines 8, 21, 23, 31; C1; Claim 7.

- **Why it matters**: The pseudocode as printed cannot produce the corrected APA and BibTeX that Claim 7 says derive from authoritative metadata on the most common path.

- **Kind**: Demonstrated inconsistency.

- **Location**: Eq. 1; Eq. 2; Eq. 3; Algorithm 1, lines 8 and 32; Figure 1.

- **Observation**: Eq. 1 defines similarity on the unit interval, while Eq. 2 subtracts from 100, Eq. 3 adds a bonus of up to 10, and every threshold in the algorithm and figure is on a 0 to 100 scale, with no conversion stated.

- **Evidence or criterion**: Eq. 1; Eq. 2; C4; N9.

- **Why it matters**: A reader implementing the equations as printed gets a confidence that is always negative under Eq. 2, derived, so the method is not reproducible from the paper.

- **Kind**: Demonstrated inconsistency.

- **Location**: Section 3, p. 6, paragraph 2; Algorithm 1, lines 18, 19, 26, 27.

- **Observation**: The prose defines fabricated authors as capitalised tokens in the query matching nothing real, and flags authors in only one source; the pseudocode builds the fabricated set from names the databases returned and flags any author absent from even one of the three sources.

- **Evidence or criterion**: Section 3, p. 6, paragraph 2; Algorithm 1, lines 18 to 19 and 26 to 27; C7; C8.

- **Why it matters**: The two definitions pick out different sets, and the pseudocode version flags a real author whenever one database records the name differently or omits it, which directly inflates the "fake author" penalty.

- **Kind**: Potential design or analysis problem.

- **Location**: Algorithm 1, lines 10 to 19.

- **Observation**: The fallback queries Semantic Scholar and OpenAlex and intersects their author lists with the CrossRef match without any step checking that the three results denote the same work.

- **Evidence or criterion**: Algorithm 1, lines 10 to 19; C8.

- **Why it matters**: If one source returns a different paper for the same free-text query, the intersection empties, no bonus is awarded, and every author of the real paper is reported as potentially fabricated.

- **Kind**: Potential design or analysis problem.

- **Location**: Algorithm 1, line 21.

- **Observation**: The bonus and the assignment of corrected metadata are gated on at least two confirmed authors, which can never be satisfied for a single-author reference, derived from the line as printed.

- **Evidence or criterion**: Algorithm 1, lines 21 to 24; C9; Section 3, p. 6, paragraph 2.

- **Why it matters**: Single-author works, including the paper under review, cannot receive multi-source confirmation or corrected output on the fallback path, and the prose describes cross-validation as unconditional once the fallback fires.

- **Kind**: Potential design or analysis problem.

- **Location**: Algorithm 1, lines 30 to 32; Figure 1.

- **Observation**: The existence verdict is `bestScore > 50` computed before `COMPUTEFINALSCORE` folds the detected issues in, and Figure 1 has no terminal state that reports non-existence at all.

- **Evidence or criterion**: Algorithm 1, lines 30 to 32; Figure 1; C11; N4; N27.

- **Why it matters**: A reference with a score of 51 and several flagged issues is returned as existing, and the figure's user-facing states are only "Verified" and "Partial Match", so the tool's most consequential output has no consistent semantics.

- **Kind**: Demonstrated inconsistency.

- **Location**: Abstract; Section 3, paragraph 2; Table 1, row "Multi-source validation"; Algorithm 1, lines 2 to 11.

- **Observation**: The abstract, Section 3 and Table 1 describe validation against three databases, while Algorithm 1 reaches the second and third sources only when CrossRef returns nothing or the score is below 70 or an issue is flagged.

- **Evidence or criterion**: Abstract; Algorithm 1, lines 2 to 11; C10.

- **Why it matters**: A reference that scores 70 or more on CrossRef alone is validated against one source, so "multi-source confirmation" is the exception rather than the design.

- **Kind**: Demonstrated inconsistency.

- **Location**: Figure 1 (p. 5); Algorithm 1, lines 3 to 5; Section 3, paragraph 4 (p. 4).

- **Observation**: Section 3 calls Figure 1 "the complete verification pipeline", and the figure has no branch for CrossRef returning no candidates, which Algorithm 1 handles at lines 3 to 5.

- **Evidence or criterion**: Figure 1; Algorithm 1, lines 3 to 5; C6; C5.

- **Why it matters**: The figure and pseudocode describe different control flows, and C5 shows the pseudocode itself queries Semantic Scholar twice on one path, so the reader cannot tell which artefact describes the shipped tool.

- **Kind**: Demonstrated inconsistency.

- **Location**: Algorithm 1, line 22; Eq. 3 and the sentence defining βms (Section 3, p. 6, paragraph 4).

- **Observation**: The multi-source bonus is a fixed plus 10 added to `bestScore` in the pseudocode and a value in the range 0 to 10 added to a four-field average in Eq. 3.

- **Evidence or criterion**: Algorithm 1, line 22; Eq. 3; C2; C3; N12.

- **Why it matters**: The bonus is added to different quantities by different rules in the two places, and neither place states how a value inside the range is chosen.

- **Kind**: Not reported.

- **Location**: Algorithm 1, lines 6, 7, 23, 30; Section 3, p. 6, paragraphs 3 to 4.

- **Observation**: `EVALUATECANDIDATES`, `DETECTISSUES`, `MERGEMETADATA` and `COMPUTEFINALSCORE` are never defined, the Eq. 2 versus Eq. 3 selection rule is unquantified, `Sjournal` and `Syear` are undefined, and the penalty ranges have no selection rule.

- **Evidence or criterion**: N4; N5; N6; N7; N8; N10; N11.

- **Why it matters**: Four of the eight named procedures and two of the four score components are black boxes, so the scoring method cannot be reimplemented or audited.

- **Kind**: Integrity concern.

- **Location**: References, entry "Wager, E. and Middleton, P. (2008)"; Section 2, paragraph 1 (p. 2).

- **Observation**: The entry gives the title and JAMA locator of a 2002 article with the year 2008, combining the locator of one work with the year of another by the same authors, as W5 verified against Crossref.

- **Evidence or criterion**: References, Wager and Middleton entry; Section 2, paragraph 1; W5; W15.

- **Why it matters**: The discrepancy is observable and a benign reading is conflation of two works by the same authors during drafting, but it sits in a paper whose subject is citation accuracy and it is the kind of error the paper's own tool exists to catch.

- **Kind**: Integrity concern.

- **Location**: Section 3, p. 6, paragraph 2; Section 1, paragraph 4 (p. 2).

- **Observation**: The sentence that multi-source confirmation is "particularly effective at detecting LLM hallucinations, which frequently insert plausible-sounding but non-existent author names" cites Nicholas et al. 2025, an interview study of 91 early-career researchers that W6 found reports nothing on fabricated author names, and the sentence on commercial services' free-tier limits cites Zhu et al. 2025, a study of LLM-generated peer reviews that W7 found says nothing about pricing.

- **Evidence or criterion**: Section 3, p. 6, paragraph 2; Section 1, paragraph 4; W6; W7; Claim 3; Claim 5.

- **Why it matters**: Two claims the tool's design and positioning depend on are attached to sources that do not support them; a benign reading is topic-level citing, but the effect is that the claims are unsupported.

- **Kind**: Integrity concern.

- **Location**: Section 3, paragraph 2 (p. 3).

- **Observation**: The coverage figures "over 140 million" for CrossRef and "over 200 million" for Semantic Scholar are cited to Hendricks et al. 2020 and Ammar et al. 2018, and W4 and W13 found the first source says 106 million and the second gives a 280 million node count across papers, authors and entities, not a paper count.

- **Evidence or criterion**: Section 3, paragraph 2; W4; W13; N29.

- **Why it matters**: The architecture rationale rests on coverage figures the cited sources do not give, and neither figure is dated; a benign reading is that the numbers were taken from the databases' current web pages and cited to the founding papers.

- **Kind**: Not reported.

- **Location**: Footnote 1 (p. 1); Availability (p. 8).

- **Observation**: The artifact is identified only by a live URL, with no version, commit, dependency list or archived snapshot, and W12 found the served artifact now queries five databases and carries features the paper never mentions.

- **Evidence or criterion**: Footnote 1; Availability; N19; W12; W3.

- **Why it matters**: The paper's Section 3 no longer describes what the URL serves, so the described architecture cannot be checked against the running system.

- **Kind**: Demonstrated inconsistency.

- **Location**: Identifier stamp (p. 1).

- **Observation**: The identifier's year-month component reads 2602, February 2026, while the stamped date is 27 January 2026.

- **Evidence or criterion**: Identifier stamp; C14.

- **Why it matters**: The cause is not stated in the paper, the weight is low, and it does not move the credibility verdict.

- **Kind**: Demonstrated inconsistency.

- **Location**: Identifier stamp (p. 1).

- **Observation**: Recall: arXiv assigns the identifier when the submission is processed, which can fall in the month after a submission held in moderation, so the stamp discrepancy is most likely the server's artefact rather than the paper's.

- **Evidence or criterion**: Identifier stamp; C14.

- **Why it matters**: A reader should not read the discrepancy as a sign of tampering with the front matter.

## Novelty

The three-source author intersection is a modest engineering idea, and the free batch matching and corrected-BibTeX output the paper presents as filling a gap already existed in tools the paper does not cite.

- **Kind**: Potential design or analysis problem.

- **Location**: Table 1, rows "Immediate validation", "Batch verification", "Multi-source validation", "Corrected BibTeX output", "Unlimited free usage"; Section 4.1, paragraph 2.

- **Observation**: The gap claim is made only against four reference managers, while W9 records that Crossref's Simple Text Query has offered free batch matching of up to 1,000 pasted references since 2006 and that betterbib and rebiber correct BibTeX against online sources and pre-date the paper.

- **Evidence or criterion**: Table 1; Section 4.1, paragraph 2; W9; N16; Claim 2.

- **Why it matters**: The novelty claim is broader than the cited literature supports, and the reader is not told that the paper's own CrossRef stage uses the same matching interface that Simple Text Query exposes.

- **Kind**: Potential design or analysis problem.

- **Location**: Section 1, paragraph 2 (p. 2); Section 2, paragraph 2 (p. 3).

- **Observation**: The paper cites Dunford et al. 2024 twice, for manual-detection difficulty and for the chimeric form, and W10 found that source also states that validation of references against trusted databases is already used to detect fake or chimeric AI-generated references and that tools exist across the workflow.

- **Evidence or criterion**: Section 1, paragraph 2; Section 2, paragraph 2; W10; Claim 2.

- **Why it matters**: The paper's own source contradicts the claim that the validation gap is unfilled, and the paper does not engage with it.

- **Kind**: Not reported.

- **Location**: Table 1; Section 4.1, paragraph 1.

- **Observation**: The comparator set contains no tool whose purpose is verification, no source, version or access date for any cell, and no criterion for a feature counting as present.

- **Evidence or criterion**: Table 1; N16; C13; Claim 2.

- **Why it matters**: A comparison against organisers only cannot establish that a verifier is new, and C13 shows the paper's own row assignments do not survive its own prose.

- **Kind**: Not reported.

- **Location**: Section 3, p. 6, paragraph 2; Algorithm 1, lines 14 to 19.

- **Observation**: The part that is arguably new, intersecting author lists across three databases and flagging the remainder as potentially fabricated, is described and never tested, and its supporting citation does not support it.

- **Evidence or criterion**: Section 3, p. 6, paragraph 2; Claim 5; W6; N1.

- **Why it matters**: The one idea a reader could take from the paper has no evidence that it discriminates fabricated authors from formatting differences between databases.

- **Kind**: Not reported.

- **Location**: Section 1, paragraph 4 (p. 2); Section 4.1, paragraph 2.

- **Observation**: W11's forward search from the paper's key hallucination citation found no earlier reference-existence tooling the paper missed, and the two closest works are contemporaneous or later, including a 2026 Scientometrics cross-database benchmark.

- **Evidence or criterion**: W11; Section 1, paragraph 4.

- **Why it matters**: The paper is not behind the literature on LLM hallucination itself; its omission is of the older matching tools in W9, and a reader picking it up now should also read the later benchmark W11 names.

## Applicability

The tool is live, free and open, and is usable as a first-pass screen, but its verdicts cannot be acted on without a human check and the paper no longer describes what the URL serves.

- **Kind**: Not reported.

- **Location**: Section 3, paragraphs 1 to 2 (p. 3); Availability (p. 8).

- **Observation**: W12 found the served artifact queries CrossRef, Semantic Scholar, OpenAlex, DBLP and arXiv, extracts references from PDF and DOCX, flags DOI mismatches and retractions, emits MLA and ISO 690, and exposes an MCP server, none of which appear in the paper.

- **Evidence or criterion**: Section 3, paragraphs 1 to 2; W12; W3; N19.

- **Why it matters**: A practitioner should read the repository README rather than Section 3 to learn what the tool does, and the paper cannot be cited as a description of the current system.

- **Kind**: Potential design or analysis problem.

- **Location**: Section 3, paragraph 2 (p. 3); Algorithm 1, line 32.

- **Observation**: The paper itself says CrossRef "may lack coverage of preprints, regional journals, or older publications" and never says what the tool reports for a work absent from all three databases, while line 32 returns `exists: false` for any low score.

- **Evidence or criterion**: Section 3, paragraph 2; Algorithm 1, line 32; N13; N14; W8.

- **Why it matters**: Books, theses, reports and regional-language journals will be marked non-existent, and W8's primary source warns that exactly this not-found rule has "a higher false positive rate" and needs human confirmation.

- **Kind**: Not reported.

- **Location**: Section 4.1, paragraph 2; Section 4, paragraph 2 (p. 7).

- **Observation**: "Unlimited free verification" is promised while the tool depends on three third-party APIs whose rate limits, quotas and terms are never stated, and an 800 ms interval is imposed "to comply with API usage policies" without naming one.

- **Evidence or criterion**: Section 4.1, paragraph 2; Section 4, paragraph 2; N15; W13; Claim 3.

- **Why it matters**: W13 recorded HTTP 429 from Semantic Scholar at low volume during the check, so the unlimited promise is upstream's to make, not the paper's.

- **Kind**: Potential design or analysis problem.

- **Location**: Section 4, paragraph 3 (p. 7); Algorithm 1, lines 23 and 31.

- **Observation**: The corrected BibTeX a user would reimport derives from `MERGEMETADATA`, which is undefined, and on the common path is never assigned at all.

- **Evidence or criterion**: Section 4, paragraph 3; Algorithm 1, lines 23 and 31; N7; C1; Claim 7.

- **Why it matters**: The reimport workflow Section 4.1 proposes depends on output whose field-precedence rule when sources disagree is unknown and whose existence on the success path the pseudocode does not guarantee.

- **Kind**: Not reported.

- **Location**: Section 3, paragraph 3 (p. 3); Algorithm 1, line 1.

- **Observation**: The LaTeX filter is described by three example commands and "custom macros", with no rule set and no behaviour stated for unlisted macros.

- **Evidence or criterion**: Section 3, paragraph 3; Algorithm 1, line 1; Claim 8; N22.

- **Why it matters**: The "paste directly from source files" workflow is the paper's main usability claim, and a user cannot predict which manuscripts it handles.

- **Kind**: Not reported.

- **Location**: Section 5, paragraph 1 (p. 7 to 8).

- **Observation**: Five use cases, including reviewer audit, publisher pipelines and bibliometric filtering, are introduced for the first time in the conclusions with no evidence that the tool has been used in any of them.

- **Evidence or criterion**: Section 5, paragraph 1; C17; N21; N31.

- **Why it matters**: The systems bar asks for real-world deployment evidence, and the paper offers proposed uses in its place.

## Generalizability

No result exists to generalize, and the design as described is bound to Latin-script, multi-author, journal-style references indexed in three databases whose coverage is stated without a date.

The results half of this dimension is inapplicable: the paper reports no result for any reference set, so external validity of findings cannot be assessed. The design half is assessed below.

- **Kind**: Potential design or analysis problem.

- **Location**: Eq. 3; Section 3, p. 6, paragraph 4.

- **Observation**: The structured-input score averages title, author, journal and year similarity, and the paper never says what happens when the query has no journal, which is the case for every conference paper, preprint, book and thesis.

- **Evidence or criterion**: Eq. 3; N10; N13.

- **Why it matters**: The formula as printed applies cleanly only to journal articles, which excludes the computer-science literature the NeurIPS motivation concerns.

- **Kind**: Not reported.

- **Location**: Section 3, p. 6, paragraph 2.

- **Observation**: Fabricated-author detection is defined over "capitalized tokens in the query", and family-name matching over containment in the query string, and the paper states no language or script scope for either.

- **Evidence or criterion**: Section 3, p. 6, paragraph 2; N13.

- **Why it matters**: The paper claims OpenAlex coverage of non-English publications as a design rationale and never says whether the matching rules work on them.

- **Kind**: Potential design or analysis problem.

- **Location**: Section 3, p. 6, paragraph 2.

- **Observation**: Recall: names in many scripts have no capital letters, names with lowercase particles such as "van" or "de" and mononyms do not fit the capitalised-token pattern, and family-name order differs across cultures, so the heuristic as stated would miss or misflag authors outside the Anglo-European naming convention.

- **Evidence or criterion**: Section 3, p. 6, paragraph 2.

- **Why it matters**: The fake-author penalty is the paper's chosen diagnostic signal for AI fabrication, and it would fire on real authors whose names do not fit the pattern.

- **Kind**: Not reported.

- **Location**: Section 3, paragraph 2 (p. 3); Availability (p. 8).

- **Observation**: The repository now carries DBLP and arXiv services that the paper does not mention, which W12 records.

- **Evidence or criterion**: W12; Section 3, paragraph 2.

- **Why it matters**: The addition is consistent with the author having found coverage gaps in the three-source design for computer-science references, the domain the motivation is drawn from, and the paper does not say so.

- **Kind**: Not reported.

- **Location**: Section 3, paragraph 2 (p. 3).

- **Observation**: The database coverage figures carry no date, and W4 found the live CrossRef total differs from the paper's figure by roughly 47 million works.

- **Evidence or criterion**: Section 3, paragraph 2; N29; W4.

- **Why it matters**: Coverage, and therefore the false-negative behaviour of the existence verdict, changes with time, and the reader cannot place the description in time.

- **Kind**: Potential design or analysis problem.

- **Location**: Eq. 2; Section 3, p. 6, paragraph 2.

- **Observation**: Author similarity is "the proportion of matched authors" without saying whether the denominator is the query's authors or the record's, so an "et al." query against a 19-author record could score about 5 on authors and, by Eq. 2, about 52.6 in confidence with a perfect title, derived.

- **Evidence or criterion**: Eq. 2; Section 3, p. 6, paragraph 2; Algorithm 1, line 32; Figure 1.

- **Why it matters**: Under one reading of the denominator, ordinary in-text citation formats for large-team papers land just above the existence threshold and below both the fallback and the "Verified" gates.

## Scalability

The only in-paper figure is the 800 ms batch interval, which supports about 4,500 references an hour under ideal conditions, and the large-scale bibliometric use the paper proposes has no supporting figure at all.

- **Kind**: Potential design or analysis problem.

- **Location**: Section 4, paragraph 2 (p. 7); Section 5, paragraph 1 (p. 8).

- **Observation**: The batch mode processes entries sequentially at 800 ms intervals, which is 1.25 references per second, 75 per minute and 4,500 per hour, derived; the paper states no references-per-paper multiplier, so taking its own reference list of 23 entries as the multiplier against the "over 4,000 papers" of Section 1 gives 92,000 references and about 20.4 hours of continuous browser time, derived.

- **Evidence or criterion**: Section 4, paragraph 2; Section 5, paragraph 1; Section 1, paragraph 3; References list count of 23; N31.

- **Why it matters**: The "large-scale bibliometric analyses" use case is unsupported by any figure in the paper, and the derived rate assumes no failures, no retries and no upstream throttling.

- **Kind**: Potential design or analysis problem.

- **Location**: Algorithm 1, lines 2, 4, 10, 11.

- **Observation**: The 800 ms interval is per entry, while one entry can issue up to four API calls across three services, and C5 shows Semantic Scholar is queried twice on the empty-candidate path, so the per-service call rate can reach 5 calls per second in the worst case, derived from 4 calls per 0.8 s.

- **Evidence or criterion**: Algorithm 1, lines 2, 4, 10, 11; C5; N15.

- **Why it matters**: The rate limit is placed at the wrong granularity to protect the upstream services it cites as its reason.

- **Kind**: Not reported.

- **Location**: Section 4, paragraph 2 (p. 7).

- **Observation**: No bibliography size the tool has been run on, no throughput measurement, no failure behaviour on a long batch and no concurrency or queueing statement appear anywhere.

- **Evidence or criterion**: N31; N15; W13.

- **Why it matters**: W13's HTTP 429 from Semantic Scholar shows the upstream limit binds at small volumes, and the paper gives no way to predict where a batch stops.

- **Kind**: Not reported.

- **Location**: Abstract; Section 1, paragraph 5 (p. 2); Section 4, paragraph 1 (p. 6).

- **Observation**: "Within seconds", "instant" and "real-time" appear repeatedly with no latency figure, percentile or network condition.

- **Evidence or criterion**: N3; Claim 1.

- **Why it matters**: The small-scale claim is as unmeasured as the large-scale one.

- **Kind**: Not reported.

- **Location**: Section 3, paragraph 1 (p. 3).

- **Observation**: The system is a browser application, and the paper never states whether API calls originate from the user's browser or from a server, so whose rate limit and whose IP a batch consumes is unknown.

- **Evidence or criterion**: Section 3, paragraph 1; N15; N31.

- **Why it matters**: The answer determines whether the 800 ms interval is a per-user or a global constraint, and whether the "unlimited" promise survives many simultaneous users.

## Assumptions

The method rests on unstated premises at nearly every line of Algorithm 1, most consequentially that database absence means non-existence and that three databases return the same work for one query.

Statistical-test assumptions, the counterfactual and design checks in the quantitative-methods file do not apply: the paper runs no test and makes no comparison.

- **Kind**: Not reported.

- **Location**: Algorithm 1, line 2.

- **Observation**: The CrossRef query retrieves three rows, which assumes the true record, if it exists, is among the top three bibliographic matches for a free-text query; the paper does not state this.

- **Evidence or criterion**: Algorithm 1, line 2; Figure 1 "Retrieve Top 3 Candidates"; N5.

- **Why it matters**: Any real work ranked fourth or lower is scored against a wrong candidate and may be returned as non-existent.

- **Kind**: Not reported.

- **Location**: Algorithm 1, line 3.

- **Observation**: The Semantic Scholar substitution at line 4 fires only when CrossRef returns an empty candidate set, and the paper states no expectation of how often a free-text query returns nothing; not stated.

- **Evidence or criterion**: Algorithm 1, lines 3 to 5; C6.

- **Why it matters**: Whether the first fallback ever runs depends on an upstream behaviour the paper does not describe.

- **Kind**: Potential design or analysis problem.

- **Location**: Algorithm 1, lines 3 to 5.

- **Observation**: Recall: a free-text bibliographic query to the CrossRef works endpoint returns ranked candidates for almost any non-empty string, so the empty-set branch would rarely fire.

- **Evidence or criterion**: Algorithm 1, lines 3 to 5.

- **Why it matters**: If that behaviour holds, the first fallback is effectively dead code and the score-based fallback at line 8 is the only real one.

- **Kind**: Not reported.

- **Location**: Algorithm 1, lines 10 to 18.

- **Observation**: The author intersection at line 18 assumes `ssResult` and `oaResult` denote the same work as `bestMatch`, and no line checks this; not stated.

- **Evidence or criterion**: Algorithm 1, lines 10 to 18; C8.

- **Why it matters**: The premise is the one the fabricated-author flag depends on, and its failure produces the worst false alarm the tool can raise.

- **Kind**: Not reported.

- **Location**: Algorithm 1, line 18; Section 3, p. 6, paragraph 1.

- **Observation**: Raw set intersection of author lists assumes identical author-string formatting across three databases, while the only normalisation the paper states applies to Levenshtein inputs; not stated for authors.

- **Evidence or criterion**: Algorithm 1, line 18; Section 3, p. 6, paragraph 1; C7.

- **Why it matters**: "J. Smith", "John Smith" and "Smith, J." would fail to intersect, moving real authors into the suspect set.

- **Kind**: Not reported.

- **Location**: Algorithm 1, line 21.

- **Observation**: The confirmation gate assumes multi-author works; not stated.

- **Evidence or criterion**: Algorithm 1, line 21; C9.

- **Why it matters**: Single-author references never receive the bonus or corrected metadata.

- **Kind**: Not reported.

- **Location**: Algorithm 1, line 32.

- **Observation**: `exists: bestScore > 50` assumes that a low match score in three databases means the work does not exist; the paper never states this and never defines "exists".

- **Evidence or criterion**: Algorithm 1, line 32; N13; N28; W8.

- **Why it matters**: This is the assumption the primary source in W8 explicitly warns against, and it is the one every downstream use case in Section 5 inherits.

- **Kind**: Not reported.

- **Location**: Eq. 1; Section 3, p. 6, paragraph 1.

- **Observation**: Title Levenshtein similarity is assumed to discriminate real from fabricated references, while Section 1, paragraph 3 describes hallucinations that paraphrase titles or alter real papers; the assumption is not stated.

- **Evidence or criterion**: Eq. 1; Section 3, p. 6, paragraph 1; Section 1, paragraph 3.

- **Why it matters**: A lightly altered real citation scores as its real counterpart, so the method's own motivating hallucination class passes the title check.

- **Kind**: Not reported.

- **Location**: Eq. 2; Eq. 3; Section 3, p. 6, paragraphs 3 to 4.

- **Observation**: Eq. 2 covers title similarity above 80 with author similarity below 90, Eq. 3 covers "high matching across all fields", and no formula is stated for the remaining cases or for the direction of the author proportion; not stated.

- **Evidence or criterion**: Eq. 2; Eq. 3; N8; N10.

- **Why it matters**: The confidence is undefined for a title match at or below 80 with matched authors, which is the natural case for a paraphrased title with real authors.

- **Kind**: Not reported.

- **Location**: Footnote 2 (p. 6).

- **Observation**: The thresholds of 50, 70 and 80 and the penalties are assumed to transfer from an unstated calibration set to a user's references; not stated.

- **Evidence or criterion**: Footnote 2; N2; W12.

- **Why it matters**: Without the set's provenance the reader cannot tell whether the thresholds were tuned on the kind of references they will submit.

- **Kind**: Not reported.

- **Location**: Algorithm 1, line 1; Section 3, paragraph 3 (p. 3).

- **Observation**: The filter assumes the LaTeX commands present in pasted text belong to a finite known set; not stated beyond three examples.

- **Evidence or criterion**: Algorithm 1, line 1; Claim 8; N22.

- **Why it matters**: An unfiltered macro becomes a capitalised token that the fabricated-author rule can flag.

## Readability

The prose is clear and well organised, but the formal parts do not agree with each other or with the text, key terms are never defined, and the tone is promotional in places.

- **Kind**: Demonstrated inconsistency.

- **Location**: Figure 1 (p. 5); Algorithm 1 (p. 4); Section 3, p. 6.

- **Observation**: Figure 1's "Score > 80%?" gate and its "Verified" and "Partial Match" states appear nowhere in the text or pseudocode, the pseudocode's threshold of 50 appears nowhere in the text, and the figure omits the pseudocode's empty-candidate branch.

- **Evidence or criterion**: Figure 1; Algorithm 1, lines 3 to 5 and 32; N26; N27; C6.

- **Why it matters**: A reader must reconcile three descriptions of one procedure, and none of them is marked as authoritative.

- **Kind**: Demonstrated inconsistency.

- **Location**: Abstract; Section 1, paragraph 5; Algorithm 1, line 32; Section 5, paragraph 1.

- **Observation**: The tool's output is called "authenticity", "match confidence", "verification", "exists" and "validity" in different places without distinguishing them.

- **Evidence or criterion**: C16; N28.

- **Why it matters**: The reader cannot tell whether the tool asserts that a work exists, that the citation is accurate, or that the citation is not AI-generated, which are three different claims.

- **Kind**: Not reported.

- **Location**: Abstract; Section 1, paragraph 4; Section 3, paragraph 2; Section 4, paragraph 1.

- **Observation**: APA, MLA and ORCID are never expanded, and DOI is used before its expansion.

- **Evidence or criterion**: C15.

- **Why it matters**: Minor, but the paper addresses readers across disciplines and the abbreviations are field-specific.

- **Kind**: Demonstrated inconsistency.

- **Location**: Section 4.1; Section 5, paragraph 1 (p. 7 to 8).

- **Observation**: The section headed "Conclusions" introduces five new use cases, and the paper has no evaluation, results, limitations or future-work section between the comparison table and the conclusions.

- **Evidence or criterion**: C17; N17; N18.

- **Why it matters**: The structure signals that a results section was expected and is absent, and new material in a conclusion cannot be checked against anything earlier.

- **Kind**: Not reported.

- **Location**: Abstract; Section 1, paragraph 3 (p. 2); Section 2, paragraph 2 (p. 3); Section 3, paragraph 3 (p. 3); Section 4, paragraph 3 (p. 7).

- **Observation**: The register runs to "insidious", "verisimilitude" and "negative externalities", and the tool description uses "seamless", "instant" and "Critically" where a measurement would normally stand.

- **Evidence or criterion**: Abstract; Section 1, paragraph 3; Section 2, paragraph 2; Section 3, paragraph 3; Section 4, paragraph 3.

- **Why it matters**: The vocabulary is manageable for a scholarly reader, but the promotional adjectives sit exactly where the paper has no evidence, which a reader should notice.

- **Kind**: Demonstrated inconsistency.

- **Location**: References list (p. 8 to 9).

- **Observation**: Three journal entries omit pages while the rest give them, the Goldman entry carries neither date nor URL, and no entry carries a DOI.

- **Evidence or criterion**: C18; W15.

- **Why it matters**: The reference list of a paper about machine-verifiable references is not itself machine-verifiable by the method the paper proposes.

- **Kind**: Not reported.

- **Location**: Section 3, paragraph 1 (p. 3).

- **Observation**: The four named modules are never mapped onto Figure 1's boxes or Algorithm 1's lines.

- **Evidence or criterion**: N32.

- **Why it matters**: The architecture paragraph and the pipeline artefacts cannot be read against each other.

Cultural neutrality is unremarkable; the paper is culturally neutral in its examples and framing.

## Ethics

The aim is sound, but the paper proposes automatic screening of other people's bibliographies with no false-positive figure, no stated limits, no privacy statement and no conflict-of-interest disclosure.

The participants file does not apply: no people took part in the research.

- **Kind**: Potential design or analysis problem.

- **Location**: Section 5, paragraph 1 (p. 7 to 8).

- **Observation**: The paper proposes that reviewers identify "potential fabrications warranting author clarification", that publishers integrate the tool into submission pipelines, and that bibliometricians "filter potentially spurious references", while the tool's false-positive rate is unmeasured and its primary source recommends human confirmation over automatic classification.

- **Evidence or criterion**: Section 5, paragraph 1; N14; N21; W8; N13.

- **Why it matters**: A real but unindexed reference could put an author under suspicion or drop a real citation from a dataset, and the paper shows no awareness of that harm.

- **Kind**: Not reported.

- **Location**: Front matter (p. 1); Availability (p. 8).

- **Observation**: There is no conflict-of-interest statement, no funding statement and no acknowledgements.

- **Evidence or criterion**: N20; research-integrity.md "no conflicts-of-interest statement at all" as a named red flag.

- **Why it matters**: The paper positions a free tool against commercial services without stating whether the author has any interest in either.

- **Kind**: Not reported.

- **Location**: Section 3, paragraph 1 (p. 3); Section 5, paragraph 1 (p. 8).

- **Observation**: Whether user-supplied reference text, which in the reviewer and publisher use cases belongs to unpublished manuscripts, is transmitted to three third-party APIs and what those parties retain is never addressed.

- **Evidence or criterion**: N30; Section 5, paragraph 1.

- **Why it matters**: A reviewer pasting a confidential manuscript's bibliography into the tool discloses it to external services, and the paper does not warn of this.

- **Kind**: Not reported.

- **Location**: Section 3, paragraph 3 (p. 3); Section 3, p. 6, paragraph 2.

- **Observation**: No threat model is stated for a deliberately crafted near-miss reference or for evading the LaTeX filter and the matcher.

- **Evidence or criterion**: N22.

- **Why it matters**: A tool proposed for gatekeeping should say what an adversary can do to it, and this one does not.

- **Kind**: Not reported.

- **Location**: Whole paper; Section 4.1, paragraph 2.

- **Observation**: No limitations statement appears anywhere, and the paper's own Section 3 acknowledges coverage gaps in each database without carrying that acknowledgement into a stated limit on the verdicts.

- **Evidence or criterion**: N17; Section 3, paragraph 2; N13.

- **Why it matters**: Awareness of negative consequences is the ethics question this dimension asks, and the paper contains no sentence that answers it.

- **Kind**: Integrity concern.

- **Location**: References list; Section 2, paragraph 1; Section 3, p. 6, paragraph 2; Section 1, paragraph 4.

- **Observation**: As a pattern summary of the Credibility points above, nine reference locators were checked and one is wrong, and four claims were checked against their cited source and none is supported, in a paper whose subject is citation accuracy.

- **Evidence or criterion**: W15; W5; W4; W6; W7; W13.

- **Why it matters**: The pattern is stated neutrally and a benign reading is topic-level citing, but a reader should verify any claim in the paper against its source before relying on it.
