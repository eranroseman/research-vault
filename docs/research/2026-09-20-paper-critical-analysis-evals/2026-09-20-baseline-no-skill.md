# Critical Analysis: *CheckIfExist: Detecting Citation Hallucinations in the Era of AI-Generated Content*

**Paper:** Diletta Abbonato (University of Turin), arXiv:2602.15871v1 [cs.CL], stamped 27 Jan 2026, 9 pages (about 6 pages of body text, 1 full-page figure, 2 pages of references).
**Artifact:** open-source (MIT) React/TypeScript web app hosted at `zabbonat.github.io/References-Validation/`, validating references against CrossRef, Semantic Scholar, and OpenAlex.
**Review basis:** full text of the PDF (text-extracted; no web access). Claims that could not be checked against the paper itself are quarantined in Appendix A rather than presented as findings.

______________________________________________________________________

## Verdict

This is a tool-description paper for a plausible and genuinely useful utility: a free, installation-free web page that checks whether a reference exists in three scholarly indexes and returns corrected APA/BibTeX. The problem it targets is real and well motivated. But the paper contains **no evaluation of any kind** — no test set, no precision/recall, no false-positive rate on legitimate-but-unindexed references, no comparison with the commercial or open tools it positions itself against — and the footnote asserting that thresholds were "empirically calibrated" (p. 6, fn. 2) is unsupported by any reported data. Read closely, the algorithm as published (Algorithm 1, p. 4; Eqs. 2–3, p. 6) has internal inconsistencies that would produce systematic false positives, most seriously flagging every author of a real paper as "potentially fabricated" whenever one of the three databases lacks the paper. As a research contribution it is not yet evaluable; as a software note it overclaims ("hallucination detection") relative to what it does (existence-and-metadata lookup). Recommendation: major revision — add an evaluation, fix or clarify the scoring logic, add identifier-first lookup, and narrow the claims.

______________________________________________________________________

## 1. What the paper does

- **Problem (pp. 1–3).** LLM-generated references are plausible but often non-existent or "chimeric." Reference managers (Zotero, Mendeley, EndNote, JabRef) organize but do not validate; commercial hallucination checkers are metered or paid.
- **System (pp. 3–6).** Four modules: LaTeX-command filter, BibTeX parser, multi-source search, presentation/export. A cascading lookup: CrossRef (top 3 candidates) → Semantic Scholar if empty → score the best candidate → if score < 70 or any issue is detected, query Semantic Scholar and OpenAlex, intersect author sets across the three sources, add a +10 bonus if ≥ 2 authors are confirmed, and flag the remaining authors as suspect. Title similarity is normalized Levenshtein (Eq. 1). Confidence is either `S_title − 0.5·(100 − S_author)` (Eq. 2, when title > 80 and author < 90) or the mean of title/author/journal/year similarity plus a multi-source bonus β ∈ [0, 10] (Eq. 3, "structured input with high matching"), with penalties of −20 (title/author mismatch), −10 to −20 (journal), and −10 to −20 per detected fake author. Output: `exists = bestScore > 50`, a confidence value, an issue list, and APA + BibTeX regenerated from database metadata.
- **Features (pp. 6–7).** Quick-check (free text in any style) and batch-check (BibTeX or newline list), 800 ms inter-request delay, download/copy of corrected BibTeX. Table 1 (p. 7) contrasts it with four reference managers.
- **Claims (pp. 3, 7–8).** Higher recall than any single source "while maintaining precision"; results "within seconds"; unlimited free use; suitable for authors, reviewers, publishers' submission pipelines, and bibliometric dataset cleaning.

## 2. Strengths

1. **Timely, real problem, well framed.** The motivation is concrete and the "cost asymmetry" argument (p. 3) — generation is nearly free, verification is expensive — is a fair statement of why automated checking matters.
2. **Sensible core design.** Cascading across three indexes with complementary coverage is the right instinct, and cross-source author agreement is a reasonable heuristic for the chimeric case (real title, invented authors) that single-field matching misses.
3. **Low barrier to use.** No install, no account, no quota, MIT license. For a reviewer wanting to spot-check ten references, this is the correct form factor.
4. **Practical touches.** Stripping `\textit`, `\vspace`, and similar commands from pasted LaTeX; accepting BibTeX directly; emitting corrected BibTeX with generated keys. These reflect actual usage friction.
5. **Honest positioning.** The paper says the tool complements rather than replaces reference managers, and the round-trip workflow (export BibTeX → validate → reimport) is clearly described.

## 3. Major weaknesses

### 3.1 No evaluation at all

The paper reports no experiment. There is no dataset of real and hallucinated references, no precision/recall/F1, no false-positive rate on legitimate references, no ablation of the multi-source cascade against CrossRef alone, no timing measurement beyond "within seconds," and no comparison to the commercial services or to the prior automated-bibliography work it cites (Dunford et al., 2024). Footnote 2 (p. 6) states that "threshold and penalty values were empirically calibrated to optimize discrimination between valid references and known hallucinations" — but nothing about the calibration set, its size, its source, the metric optimized, or the resulting numbers appears anywhere. The claim on p. 3 that the system "achieves higher recall than any single-source approach while maintaining precision" is likewise asserted, not shown. Every design choice in §3 is therefore unvalidated, including the ones critiqued below. This alone would block acceptance at a venue that expects a research contribution.

### 3.2 "Not found" is not "hallucinated"

The tool's binary output (`exists: bestScore > 50`) equates absence from three indexes with fabrication. Large classes of legitimate references are poorly or inconsistently indexed: books and book chapters, theses, technical reports, standards, legislation, working papers, datasets, software, workshop papers, older or non-English humanities and social-science publications, and press articles. The paper acknowledges coverage gaps (p. 3) but presents multi-source lookup as a solution without quantifying the residual gap. The author's own bibliography illustrates the problem — a Fortune news article (Goldman, 2026), a monograph (Merton, 1973), and an arXiv preprint (Priem et al., 2022) — and the paper never reports how the tool scores them. The consequence is not merely inaccuracy but skew: the use cases in §5 (reviewers flagging "potential fabrications," publishers gating submissions, bibliometric filtering) would disproportionately burden fields, languages, and regions whose venues lack DOIs. A tool that cannot distinguish "not indexed" from "does not exist" should not be described as detecting hallucinations.

### 3.3 Auto-correction can launder hallucinations into miscitations

The batch export "enables rapid replacement of uncorrected entries with validated BibTeX records" (§5), and outputs "derive from authoritative metadata … rather than potentially erroneous input" (p. 7). But the record the tool returns is *the nearest indexed paper*, not *the paper the author read*. An LLM-fabricated reference whose title is 80 % similar to a real paper will be scored as a partial match and "corrected" to that real paper; a user following the recommended workflow will then cite a work they have never seen. That converts a detectable fabrication into an undetectable one. The paper cites Simkin and Roychowdhury's "Read before you cite!" (p. 2) and then recommends a workflow that is in tension with it. At minimum, correction should be a suggestion with a diff, not a replacement, and the paper should say so.

### 3.4 Table 1 compares against the wrong things

Table 1 (p. 7) lists thirteen features against four reference managers, which the paper itself says are "fundamentally designed for organization rather than validation" (p. 2). Six of the rows are validation features that no reference manager claims; the table therefore proves what was stipulated. The natural comparators — the "commercial hallucination detection services" mentioned in the abstract, and the automated bibliography analysis of Dunford et al. (2024) — are never named, described, or compared. The single support cited for the freemium-pricing claim, Zhu et al. (2025), is by its title a paper about risks of LLMs in peer review, not a survey of verification products. There is, in effect, no related-work section: the paper's bibliography contains at least one direct predecessor (Dunford et al.) cited only as background, and a natural evaluation design (Agrawal et al., 2024, who generate references with LLMs and check whether they exist) cited only for a hallucination-rate statistic.

## 4. Algorithmic issues (readable from Algorithm 1, Figure 1, and Eqs. 1–3)

Each item below is checkable against the pseudocode on p. 4 or the text on p. 6. The implementation may differ from the paper; if so, the paper is the thing that needs fixing.

01. **All authors flagged when any one source lacks the paper.** Lines 18–19 compute `confirmed = CR ∩ SS ∩ OA` and `suspect = (CR ∪ SS ∪ OA) \ confirmed`. If any one source returns nothing (its author set is empty), the intersection is empty and *every* author from the other sources lands in `suspect`, triggering "Potential fabricated authors" (line 27) and −10 to −20 per author (p. 6). A five-author paper indexed in CrossRef and Semantic Scholar but not OpenAlex would take a −50 to −100 penalty for being real. This is the single most consequential defect in the published logic.
02. **Single-author papers can never earn the bonus.** Line 21 requires `|confirmed| ≥ 2` before adding +10 and before `correctedMetadata` is assigned. A solo-authored paper, however perfectly indexed everywhere, is structurally excluded.
03. **`exists` ignores the penalties.** Line 30 folds the issues into `confidence`; line 32 returns `exists: bestScore > 50` using the *unpenalized* score. A reference carrying several fake-author penalties can still be reported as existing while its confidence says otherwise.
04. **`correctedMetadata` is used unassigned.** It is set only inside the `if |confirmed| ≥ 2` branch (line 23) but consumed unconditionally at line 31. Pseudocode sloppiness, but it hides an unstated behaviour: what is exported when the branch does not fire?
05. **Semantic Scholar is queried twice and cross-validated against itself.** If CrossRef returns nothing, line 4 already makes `bestMatch` a Semantic Scholar result; line 10 queries Semantic Scholar again, and line 14 labels the `bestMatch` authors as "crossRefAuthors." Two of the three "independent" sources are then the same source.
06. **Three thresholds, no stated relationship.** Line 8 uses 70 to trigger fallback; Figure 1 (p. 5) uses "> 70 %" and then "> 80 %" to separate Verified from Partial Match; line 32 uses 50 for `exists`. What a user should conclude from a score of 60 (exists, not verified, not partial?) is undefined.
07. **The scoring function is only partially specified.** Eq. 2 applies when title > 80 and author < 90; Eq. 3 applies to "structured input with high matching across all fields." The remaining cases — free text with title ≤ 80, structured input with a weak field, title > 80 with author ≥ 90 — are not given a formula. β is "∈ [0, 10]" in the text but a fixed +10 at line 22.
08. **No identifier lookup.** The introduction (p. 2) names "a fabricated DOI" as a hallmark of hallucinated references, yet Algorithm 1 never resolves a DOI, arXiv ID, PMID, or ISBN. Direct identifier resolution is deterministic, cheap, and the strongest signal available; a cascade should start there, not with a fuzzy bibliographic query capped at three CrossRef candidates (line 2).
09. **The fake-author heuristic is not robust.** A fake author is "a capitalized token in the query that matches neither title words, journal name, year, nor any real author family name" (p. 6). Taking the paper's own reference list as input: "Learned", "Publishing", "University", "Chicago", "Press", "Annual", "Review", "Information", "Science", "Technology", "Proceedings", "Findings", "Association", "Computational", "Linguistics" are all capitalized tokens that must be matched exactly against the retrieved journal string or become −10 to −20 penalties each. No stop-list, venue normalization, or handling of publisher/city/series names is described.
10. **Levenshtein is a weak choice for titles.** Character-level edit distance normalized by length (Eq. 1) penalizes word reordering, dropped subtitles, and truncation heavily, and is O(|a|·|b|). Token-based measures (Jaccard, token-sort/token-set ratio) are the usual choice for bibliographic title matching and would be a one-line change; no justification for Levenshtein is offered.
11. **Free-text parsing is unexplained.** Quick-check accepts "APA, MLA, Chicago, etc." (p. 6) but no citation parser is mentioned. If the entire citation string is sent as one bibliographic query and then compared by Levenshtein against a candidate *title*, the similarity is structurally low; if fields are extracted first, the extractor is the most error-prone component and is undescribed.
12. **`MERGEMETADATA` is a black box.** When sources disagree on year, venue, or author order, which wins? The exported BibTeX depends on this and the paper does not say.

## 5. Practical and deployment concerns

- **Client-side architecture vs. API terms.** GitHub Pages serves static content and none of the four modules described on p. 3 is a backend, so the app appears to run entirely in the browser; if so, it cannot hold a secret API key and must use unauthenticated tiers of all three services. The paper does not state which tiers or limits apply, whether a `mailto`/user-agent is set for CrossRef's polite pool, or what happens when Semantic Scholar rate-limits the user. "Unlimited free usage" (Table 1) is a property of the upstream APIs' goodwill, not of the tool.
- **Batch throughput is not characterized.** At 800 ms per entry plus one to three round-trips each, a 300-entry thesis bibliography takes several minutes at best; the "within seconds" claim is made only for single references, but §5 sells batch audits.
- **Confidentiality for reviewers.** §5 recommends that reviewers audit manuscripts under review. Doing so transmits the reference list of a confidential submission to three third-party services. Many venues' reviewer agreements forbid this; the paper should at least note it.
- **Reproducibility.** Results depend on live, changing indexes; there is no versioned release, archived snapshot, test suite, or source-repository URL (only the deployed page), so a result obtained today cannot be reproduced later.
- **Publisher-pipeline claim.** §5 says publishers "can integrate reference validation into submission pipelines," but the described artifact is a browser UI with no API, CLI, or library entry point.

## 6. Presentation and scholarship

- **Motivation rests on press coverage.** The headline NeurIPS/ICLR figures (p. 2) are cited to a Fortune article (Goldman, 2026); the underlying report is not cited. For a paper about citation integrity, citing the primary source would have been the obvious move.
- **Claim–source mismatches visible from titles alone.** Nicholas et al. (2025), a survey of early-career researchers' attitudes, is the sole citation on the sentence "This multi-source confirmation is particularly effective at detecting LLM hallucinations, which frequently insert plausible-sounding but non-existent author names" (p. 6); even read as supporting only the closer clause, an attitude survey is a weak source for an empirical property of LLM output. Zhu et al. (2025), on risks of LLMs in peer review, is cited (p. 2) for freemium pricing of verification services. Neither title supports the claim it is attached to.
- **Non sequitur.** "Given that NeurIPS 2025 had an acceptance rate of 24.52 % from over 21,500 submissions, the presence of fabricated references in accepted papers represents a significant breach" (p. 2) — the acceptance rate has no bearing on whether fabricated references are a breach.
- **Table 1 self-scoring.** "Bibliography formatting ✓" for a tool that emits exactly one citation style (APA 7) plus BibTeX is generous; reference managers support hundreds of styles.
- **Proportion.** Roughly a page (§2) is devoted to a sociology-of-science and market-failure framing that, while well written, is disconnected from any design decision in §3. That space would have been better spent on an evaluation.
- **The paper's own references show internal inconsistencies** (see Appendix A for the specifics), which is an awkward look for a citation-accuracy paper and would presumably be surfaced by running the tool on its own bibliography — an experiment the paper could have reported.

## 7. Questions for the author

1. What dataset was used for the "empirical calibration" in footnote 2? How many valid and hallucinated references, from which fields, and what precision/recall resulted?
2. What does the tool report for the paper's own 23 references? For a monograph, a press article, and an arXiv preprint in particular?
3. How does the implementation handle the case where one of the three sources returns no result — does it really flag all authors as suspect, as Algorithm 1 lines 18–19 imply?
4. Why does `exists` use `bestScore` rather than the penalized `confidence`?
5. Why is there no DOI/arXiv/PMID/ISBN resolution step?
6. Which API tiers and rate limits does the deployed app operate under, and is a polite-pool identifier sent?
7. Is the corrected BibTeX presented as a replacement or as a diff for the user to approve?
8. Where is the source repository, and is there a versioned/archived release?

## 8. Recommendations

01. **Evaluate.** Build a benchmark of (a) real references stratified by type and field — including books, theses, non-English and DOI-less venues — and (b) LLM-generated references, e.g. following the Agrawal et al. (2024) protocol, labelled by ground-truth lookup. Report precision, recall, and false-positive rate per stratum, plus an ablation (CrossRef only vs. cascade) and a timing table. Run the tool on its own bibliography and report the result.
02. **Fix the logic.** Guard the intersection against missing sources (intersect only over sources that returned a candidate); drop the `≥ 2` author requirement or justify it; make `exists` a function of the penalized score; specify the scoring formula for every branch; reconcile the 50/70/80 thresholds into one documented scale.
03. **Add identifier-first lookup.** Resolve DOI, arXiv ID, PMID, and ISBN before any fuzzy query.
04. **Replace Levenshtein with a token-based title measure** and describe the free-text field extraction.
05. **Add a stop-list / venue normalization to the fake-author heuristic**, or replace the heuristic with comparison against parsed author fields only.
06. **Separate "not found" from "contradicted."** Report three outcomes — verified, contradicted (real title, wrong authors/venue), and not indexed — instead of a single `exists` bit, and say plainly that "not indexed" is not evidence of fabrication.
07. **Make correction opt-in and visible** (show a diff; never silently replace).
08. **Rewrite the comparison.** Name and compare the commercial and open tools; treat Dunford et al. (2024) as prior work.
09. **Document deployment facts.** API tiers, rate limits, privacy implications for confidential manuscripts, source repository, and an archived release.
10. **Narrow the title and claims** to what is demonstrated: existence and metadata verification against three indexes.

______________________________________________________________________

## Appendix A — Points from reviewer recall, not verifiable from the PDF (no web access)

These are stated as "appears inconsistent — verify," not as findings.

- **Wager and Middleton (p. 9)** is listed as *JAMA*, 287(21):2821–2824, **2008**. *JAMA* volume 287 corresponds to 2002; the systematic review with that title and page range appears to be the 2002 paper, with a separate 2008 Cochrane update by the same authors. Year and volume look inconsistent.
- **Strzelecki (p. 9)** is dated 2024 but placed in *Learned Publishing* 38(1); volume 38 appears to be the 2025 volume. **Taşkın (p. 9)** is dated 2025 but placed in *JASIST* 77(1), while **Céspedes et al.** (also 2025) is in volume 76(6); volume 77 would appear to be 2026. These are typical online-first vs. issue-date mismatches — precisely the kind of discrepancy the tool's journal/year matching (p. 6) would penalize.
- **JabRef and Zotero features.** Reviewer recollection is that JabRef ships an integrity checker and DOI/ISBN metadata lookup, and that Zotero can fetch metadata by DOI/PMID/ISBN. If correct, Table 1's blanket "–" for "Immediate validation" under those tools is an oversimplification; verify against current documentation.
- **Semantic Scholar unauthenticated rate limits** are, by recollection, low and shared; if so, batch runs from the browser would hit them quickly. Verify against current API terms.
