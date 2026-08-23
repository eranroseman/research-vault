# Product-landscape docs — review findings

Reviewed 2026-08-22 (author-directed). Method: five lanes (self-claims vs the tree, sourcing-discipline sample of 55 claims, assembled+memoria docs, adoption plan vs recorded doctrine, cross-doc consistency), 68 candidates, each adversarially verified by a fresh agent instructed to refute. **60 confirmed, 8 refuted.** Full per-agent evidence: workflow journal wf_ffc62986-0a8 (session record). Review only — nothing in the four docs was edited; disposition is the author's (and the writing session's).

## The eight clusters (read these, then the detail)

1. **The comparison scores intended behavior as actual — its biggest defect class.** The same-day no-fabrication audit is never incorporated: the RW retraction leg is listed as a working registry leg and a §12 differentiator (it is inert in production); free-prose survival is asserted as a safety invariant (import silently destroys the free region of marker-less notes); trust tiers "derived from verified events" (the machine-confirmed tier mints vacuously); pre-commit named a closed enforcement point (it fails open when the package is unimportable); the citability axis carries the stale tier-1 form (tier-2 ruled, and unenforced). A comparison whose own §3 says "our side was measured from source, so its numbers are exact" must either measure actual behavior or say it scored the design.
2. **The evidence rule is violated by its own bookkeeping.** Eleven repositories appear in BOTH §2 read-depth lists ("read at file level" AND "cloned, no file opened"); §7's method note says only zotero-mcp was file-read while seven §7 rows carry the file-read mark; medsci's script count is 52 in one place and 36 in two others; §8.5 says "four full texts" and "four abstracts, one results table" about the same reading.
3. **"Measured from source" numbers match no single tree.** The dependency claim (one pinned defusedxml) and test count (1,467) describe neither the main checkout (zero deps, 1,330 tests) nor the Plan-Q worktree (1,470) — and §13 says "stdlib only", contradicting §4 and §12 inside the same document.
4. **Stale against same-day rulings** (the docs were written after the commits): "we nowhere reason about false-positive rate" (spec §6 warn-tier precision doctrine + §9 measured output landed earlier that evening); the confidence-axis "indictment" (recorded as a deliberate, trigger-named deferral); the import seam analysis (predates findings 15/16's full-text digest step).
5. **Restructure fallout.** §17/§18 were moved out of the comparison into the adoption plan after the sibling docs were written: ~10 cross-references across the memoria note, assembled spec, and the adoption plan itself now dangle or point at the wrong document (the plan cites its own sections as "the comparison's §2.1/§2.9").
6. **The adoption plan contradicts recorded rulings and itself.** Urgent-mirror claims the arc cannot close without three adoptions (spec §7/§9 close it with the shipped nine); the fulltext row ignores §10's /fulltext ruling and finding 16; asta-skill is Tier-A'd despite the consumed-MCP rejection; gap-to-topic sits in two mutually exclusive tiers; two tallies contradict their own tables; §3.2's "paid once" reconciliation step is incompatible with the mirror's own no-hand-edits rule; the replace-now table overrides its own §0 post-Q freeze.
7. **Memoria facts wrong where load-bearing.** The dependency row omits pydantic-ai-slim[openai] and PyMuPDF (declared in Memoria's pyproject at the recorded commit) — and the assembled spec builds its cost comparison on that absence; the verdict re-asserts a quote-check distinctness claim the same document withdrew twenty lines earlier; Memoria's Open Retractions sweep is credited as a live cross-check the sibling doc verified unreachable the same day; the K1-vs-ADR-0001 rule comparison misstates ADR scope.
8. **README misrepresents its own set.** "Reached three times by different routes" — the memoria note explicitly refuses that conclusion; the "daily" cadence is inferred from a commit total, stated as fact; three of four size figures are stale.

**What survived cleanly:** the refuted set is small (8) and the core external survey — the roster, most product rows, the §8.5 literature figures themselves, the FPR argument (which the spec adopted), and the overall "build the trust core, adopt the breadth" direction — was not itself overturned. The defects are concentrated in self-description, bookkeeping consistency, and the adoption plan's internal wiring, not in the field survey.

## Confirmed findings — detail

### 2026-08-22-adoption-plan.md:683 — HIGH (adoption)

**Claim:** The urgent-mirror block claims the research arc cannot close without three third-party adoptions, contradicting spec §7's two-flow accounting (project flow "owned at minimal viability") and spec §9, whose validated-when closes the full arc with the shipped nine skills; the line-689 row's assertion that the two-session cold-resume criterion "assumes continuity machinery we do not have" is flatly wrong — spec §3's inbox drain, §7's project start/resume orientation and synthesis-conventions' orientation-first are that machinery, and §9's two-session minimum exists to test it.

**Evidence:** "**Urgent — the arc does not close without these.**" … "the criterion assumes continuity machinery we do not have"

**Verifier:** CONFIRMED on both prongs. (1) Line 689's "the criterion assumes continuity machinery we do not have" is refuted by the tree and by the doc itself: spec line 34 defines the inbox drain as "`project`'s resume orientation step" surfacing entries with count and age; spec line 119 makes `project` the "start/resume" entry point; spec line 126 gives synthesis-conventions "orientation-first (read `synthesis/index.md` + recent log before operating)"; and  …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:687 — HIGH (adoption)

**Claim:** The fulltext-retrieval row presents a batch OA PDF downloader as the deferred direct-PDF-text leg's "missing input", but spec §10 records that leg's primary text source as Zotero local API /fulltext ("core-extracted, zero new dependency", pypdf fallback) with slice finding 16 ruling the sanctioned interim route (read the attachment via its Zotero storage path; no reachable full text = honest "no full text available"), and spec §2's preservation boundary keeps PDFs in Zotero storage outside the git vault.

**Evidence:** "the deferred direct-PDF-text leg in spec §10 needs text to exist locally first. This is that leg's missing input"

**Verifier:** CONFIRMED. adoption-plan.md:687 says the deferred leg "needs text to exist locally first. This is that leg's missing input" and files the batch OA downloader as arc-blocking urgent. Spec line 153 (§10) records the leg's input design otherwise: "primary text source when built: Zotero local API `/fulltext` endpoints — core-extracted, zero new dependency — with pypdf as fallback", and "until this leg lands the sanctioned route is reading the attachm …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-assembled-harness-spec.md:276 — HIGH (assembled-memoria)

**Claim:** Same wrong fact as the memoria doc's dependency row, load-bearing here in the cost comparison ('a dependency surface neither existing project has'): Memoria's pyproject at commit 5395a87d also declares pydantic-ai-slim[openai]>=2.0 and PyMuPDF, plus optional sqlite-vec — one of the very packages this section counts as a new cost of the assembly.

**Evidence:** Memoria adds `yaml` and provider keys.

**Verifier:** CONFIRMED. Line 276 reads exactly "Memoria adds `yaml` and provider keys." Ground truth `git show 5395a87d:pyproject.toml` in ~/memoria-vault (the very commit the research doc pins at 2026-08-22-memoria-and-knowledge-harness.md:17, also current HEAD) declares dependencies = ["pydantic-ai-slim[openai]>=2.0", "PyMuPDF>=1.24,<2", "PyYAML>=6.0"] plus optional extras mcp>=2,<3 and sqlite-vec>=0.1.6 (vector). So two unconditional runtime deps (pydantic …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-memoria-and-knowledge-harness.md:204 — HIGH (assembled-memoria)

**Claim:** The verdict section re-asserts quote-correspondence checking as surviving distinctness against Memoria after the same document withdrew that exact claim ~20 lines earlier ('Withdrawn 2026-08-22... integrity-claim-quote-check... so not claimed'), a withdrawal the adoption plan (section 3.5, line 725) records as governing; the 'Where knowledge-harness is ahead' list also still opens 'Three things' while one of the three is struck through.

**Evidence:** The distinctness that survives is narrow and real. A Zotero-anchored citekey spine and quote-correspondence checking are not small things

**Verifier:** Confirmed internal contradiction. Lines 179-187 of the memoria doc withdraw quote-correspondence as a distinctness ("Withdrawn 2026-08-22... Memoria's capability layer ships integrity-claim-quote-check... so not claimed"), yet verdict item 2 (lines 204-206) re-asserts "a Zotero-anchored citekey spine and quote-correspondence checking" as the surviving distinctness — even counting them as "two features", pairing the spine with the withdrawn item i …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:77 — HIGH (sourcing)

**Claim:** Eleven repositories appear in BOTH §2 read-depth lists — "Read at file level" and "Cloned and listed, no file opened" — so the per-row read-depth marking the evidence rule requires is contradictory for a third of the roster.

**Evidence:** "**Cloned and listed, no file opened** — shape, licence and scale confirmed, mechanisms not:" lists 917Dhj/DeepPaperNote, delibae/claude-prism, huytieu/COG-second-brain, skyllwt/AutoSci, PiaoyangGuohai1/cli-anything-zotero, tfscharff/doi-mcp, introfini/ZotSeek, PouriaRouzrokh/LatteReview, htlin222/prisma-automation, Agents365-ai/asta-skill, rpatrik

**Verifier:** CONFIRMED. Exactly eleven repos appear in both §2 lists — DeepPaperNote, claude-prism, COG-second-brain, AutoSci, cli-anything-zotero, doi-mcp, ZotSeek, LatteReview, prisma-automation, asta-skill, hallmark — in "Read at file level (cloned, one or more files opened and quoted)" at lines 61-73 AND in "Cloned and listed, no file opened" at lines 77-82; the categories are definitionally exclusive. No correction elsewhere reconciles it: §14 corrects t …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:78 — HIGH (cross-doc)

**Claim:** Eleven repositories appear in both §2's "Read at file level" list (lines 61-75) and its "Cloned and listed, no file opened" list (lines 77-85) — 917Dhj/DeepPaperNote, delibae/claude-prism, huytieu/COG-second-brain, skyllwt/AutoSci, PiaoyangGuohai1, tfscharff/doi-mcp, introfini/ZotSeek, PouriaRouzrokh/LatteReview, htlin222/prisma-automation, Agents365-ai/asta-skill, rpatrik96/hallmark — so the document's own read-depth record, which §1 declares load-bearing, is self-contradictory; the second list's correction note concedes the file-level marking "was wrong" but the first list was never pruned.

**Evidence:** Line 78 "917Dhj/DeepPaperNote, delibae/claude-prism, huytieu/COG-second-brain," under "**Cloned and listed, no file opened**" — the same names sit at lines 69-73 under "**Read at file level** (cloned, one or more files opened and quoted)"

**Verifier:** Confirmed by mechanical extraction: exactly the 11 named repos appear both under "Read at file level (cloned, one or more files opened and quoted)" (lines 61-73) and "Cloned and listed, no file opened" (lines 78-81) of docs/product-landscape/2026-08-22-product-comparison-verified.md. The contradiction is bidirectional, so the correction note at lines 82-84 ("marked several of these as file-level reads; that was wrong") cannot repair the record —  …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:113 — HIGH (sourcing)

**Claim:** §4 states the shipped core carries one pinned runtime dependency (defusedxml, admitted 2026-08-20), but the tree this doc ships on has zero: the claim describes the unmerged Plan-Q worktree, not the project.

**Evidence:** "**one** pinned runtime dependency — `defusedxml`, admitted 2026-08-20" — but pyproject.toml at HEAD (eecff57) has `dependencies = []`, defusedxml is imported nowhere, and checks.py:6 is `import xml.etree.ElementTree`; defusedxml exists only in .claude/worktrees/build+quality-lane (branch build/quality-lane). Repeated at line 1883 ("admitted 2026-0

**Verifier:** CONFIRMED. Decisive: §4's own "9,716 lines" matches main at HEAD eecff57 exactly (worktree = 9,824), so the section was measured from main — yet main has pyproject.toml `dependencies = []` and checks.py:6 `import xml.etree.ElementTree`; defusedxml exists only in .claude/worktrees/build+quality-lane (pyproject.toml:22 `defusedxml==0.7.1`, checks.py:765-766 lazy import). Line 1883's "explicit contract-match test" is worktree-only (tests/test_config …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:128 — HIGH (self-claims)

**Claim:** The self-measurement table lists an "optional offline Retraction Watch CSV via --rw-csv" as a working registry leg, but the same-day no-fabrication audit confirmed the entire RW screening leg is inert in production and the doc never says so.

**Evidence:** "optional offline Retraction Watch CSV via `--rw-csv`" — audit defect 1 (checks.py:924): load_rw_csv drops every row whose RetractionDate is not ISO; the production CSV uses "M/D/YYYY 0:00", so 2,022 of 2,023 sampled rows are silently dropped and check_rw_batch on a genuinely retracted DOI returned None.

**Verifier:** CONFIRMED. The doc mentions Retraction Watch exactly twice, both unqualified positives: line 128 lists "optional offline Retraction Watch CSV via `--rw-csv`" among "Registries called" in a table framed by "Our own side was measured from source, so its numbers are exact" (line 107), and line 1868 promotes the "offline Retraction Watch CSV path" under §12 "What we have that the field does not," claiming an edge over paper-qa's retraction CSV. Grep  …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:1238 — HIGH (self-claims)

**Claim:** The import-source description asserts free prose survives every render, but the audit confirmed import-note silently destroys the entire free region of any existing note lacking the exact managed-region marker line.

**Evidence:** "renders `literatures/CITEKEY.md` from Zotero into a managed region, leaving free prose below untouched" — audit defect 5 (notes.py:151): a note without the exact %%/hk-managed%% marker "loses its whole body to the pristine seed on import/backfill, silently, printed as success"; the same defect undercuts line 1271's "the note is a render, not an LL

**Verifier:** CONFIRMED against the tree. Doc line 1238 states unqualified: import-note renders "into a managed region, leaving free prose below untouched"; line 1271 builds on it ("the note is a render, not an LLM write, so re-import is a mechanical no-op and drift is lintable"). Ground truth contradicts both: knowledge_harness/notes.py:141-151 (_split_free) matches only the three exact standalone spellings of the %%/hk-managed%% close marker (line 146) and o …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:1866 — HIGH (self-claims)

**Claim:** The §12 uniqueness entry presents update-notice handling with reinstatement inside a gate as a working differentiator, when three confirmed audit defects show it scores intended rather than actual behavior: the RW leg is inert, a genuine UNMATCHED version-mismatch is reduced to MATCHED and unblocks publish, and the reinstatement-clears ordering runs on fabricated Jan-1 date padding.

**Evidence:** "Blocking and warn classes, bi-temporal recording, DataCite version checks, arXiv withdrawal detection and an offline Retraction Watch CSV path, with a dated reinstatement clearing an earlier dated block" — vs audit defects 1 (checks.py:924 RW inert), 2 (checks.py:1024 UNMATCHED rounded to MATCHED, "mints a verified update-notice event and unblocks

**Verifier:** CONFIRMED. All three audit defects are real and independently verified in code: checks.py:904/:922-927 drops every non-ISO RetractionDate row (production RW CSV uses "M/D/YYYY 0:00" — audit reproduced 2,022/2,023 rows dropped, a genuinely retracted DOI returned None), so the "offline Retraction Watch CSV path" the entry lists is inert; checks.py:1024-1032 selects only (UNREACHABLE, MATCHED, SKIPPED), discarding a non-blocking version-mismatch UNM …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:1909 — HIGH (cross-doc)

**Claim:** The §13 axis table says the core's dependencies are "stdlib only", contradicting §4 line 113 and §12 ("exactly one pinned runtime dependency — defusedxml"), the memoria note line 45, and adoption plan lines 261 ("Our core imports nothing outside the standard library today") and 729 ("Zero-dependency core") — and the tree itself is undecidable from the docs: main's pyproject.toml has dependencies = [] with no defusedxml anywhere in knowledge_harness/, the admission living only on the unmerged quality-lane worktree (commit cced181: "the core is no longer zero-dependency"); the 1,467-test count in §4 likewise matches the worktree (1,470 today), not main (1,330 collected).

**Evidence:** "| Dependencies | stdlib only | Node/Python trees, Postgres, embeddings, model providers |" vs line 113 "**one** pinned runtime dependency — `defusedxml`, admitted 2026-08-20"

**Verifier:** CONFIRMED. Line 1909 reads exactly "| Dependencies | stdlib only | ..." with no hedge, while the same doc says "one pinned runtime dependency — defusedxml" at lines 113 and 1882–1886, and §14's corrections never touch it. The two-baseline mix is verified in the tree: main's pyproject.toml line 6 is "dependencies = []" with no defusedxml anywhere in knowledge_harness/, while the unmerged worktree .claude/worktrees/build+quality-lane pins defusedxm …[full verdict in workflow journal wf_ffc62986-0a8]

### README.md:33 — HIGH (cross-doc)

**Claim:** The README claims the "build the trust core, adopt the breadth" conclusion was "reached three times by different routes" including "from the observation that the closest comparable is in-house", but the Memoria note explicitly refuses to reach that conclusion — it presents options only and says the adopt-by-default rule applied to Memoria "produces an uncomfortable answer, because Memoria decides verdicts too".

**Evidence:** "reached three times by different routes" vs memoria note line 196: "Stated as options rather than a recommendation, because the choice is not a technical one."

**Verifier:** Confirmed. README.md:33-35 claims the conclusion was "reached three times by different routes," with route 3 "from the observation that the closest comparable is in-house" — which can only be the Memoria note (the assembled spec is explicitly route 2, "by a different route" via component audit at assembled-harness-spec:314-315 and it excludes Memoria at :11; the adoption plan reaches the conclusion by generalizing the find-sources adoption at :89 …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:125 — MEDIUM (adoption)

**Claim:** The claim that medsci has "a could-not-run exit we do not have" is wrong: the comparison's own §6.1 (the cited evidence) says medsci's sys.exit(2) is "the same separation our exit codes make between a failed check and a check that could not run", and the four-state Result (UNREACHABLE/SKIPPED) plus the CLI exit-code contract already carry that distinction; only the severity-tier half of the sentence is a real gap.

**Evidence:** "with a severity tier and a could-not-run exit we do not have"

**Verifier:** Confirmed. The bullet's own cited evidence contradicts the exit half of adoption-plan line 125: docs/product-landscape/2026-08-22-product-comparison-verified.md:228-230 says medsci's sys.exit(2)-for-could-not-run is "the same separation our exit codes make between a failed check and a check that could not run." The code agrees: knowledge_harness/__main__.py:345-347 documents the contract ("0 recorded or not applicable, 1 the archive is serving no …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:163 — MEDIUM (adoption)

**Claim:** References to "Section 18" (line 163), "Section 17.5" (line 197), "Section 17.2" (line 208) and "§1.B" (line 710) are dangling: the comparison's §17/§18 were merged into this document (the comparison now jumps §16 to §19), their content is now this document's §1 and §2, and no §1.B exists anywhere.

**Evidence:** "Section 18 works that instruction into a candidate-by-candidate list."

**Verifier:** CONFIRMED. (1) Comparison doc headings jump "## 16. Searched and not added" (line 2002) directly to "## 19. Re-running this comparison" (line 2031) — no §17/§18 exist; adoption-plan lines 5-7 state §17/§18 "lived at §17 and §18 of the product comparison" and were merged here (old §17 = this doc's §1 "The verdict", old §18 = §2 "What is adoptable, classified"). (2) Line 163 "Section 18 works that instruction into a candidate-by-candidate list" the …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:197 — MEDIUM (cross-doc)

**Claim:** The plan still cites the pre-merge section numbers of content it now contains: line 197 "Section 17.5 recommends vendoring rather than rebuilding", line 205 "Section 17.2's whole argument", and line 163 "Section 18 works that instruction into a candidate-by-candidate list" — no §17.x or §18 exists in any of the four docs; the referents are this plan's own §1.5, §1.2 and §2.

**Evidence:** "Section 17.5 recommends vendoring rather than rebuilding. This section names what to vendor."

**Verifier:** CONFIRMED. The comparison doc's headings jump from '## 16. Searched and not added' (line 2002) straight to '## 19. Re-running this comparison' (line 2031) — no §17 or §18 exists in any of the four docs; the plan's own intro (adoption-plan lines 5-7) says the §17/§18 content "lived" in the comparison and was merged into this plan. The three stale citations are at line 197 ("Section 17.5 recommends vendoring rather than rebuilding"), lines 162-163  …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:296 — MEDIUM (cross-doc)

**Claim:** Two in-document references are off by one section: line 296 "(§2.8 gives the mechanism)" for whole-skill mirroring points at §2.8 "Tier F — do not touch" (the mechanism is §2.9), and line 29 cites "(§3.6)" for "the richer status enum" although §3.6 (Core — port from Memoria) never mentions bibverify's ten-state enum, which is discussed at §2.1.

**Evidence:** "**Whole skills, mirrored into `skills/` rather than vendored into the core** (§2.8 gives the" — §2.8 is "### 2.8 Tier F — do not touch"

**Verifier:** Both mis-references confirmed in docs/product-landscape/2026-08-22-adoption-plan.md. (1) Line 296 "(§2.8 gives the mechanism)": §2.8 (line 394) is "Tier F — do not touch", a licence blocklist with no mechanism; the mirroring mechanism is §2.9 (line 408): "K-Dense demonstrates the mechanism... The mechanism is right and worth copying" — corroborated by the doc itself at lines 606 and 654, which both name §2.9 as the mirroring section. (2) Line 29  …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:304 — MEDIUM (adoption)

**Claim:** asta-skill is recommended in the Tier A whole-skill adoption table (and again in the §2.9 mirror table, line 434) although it exists solely to consume Ai2's Asta MCP server, which contradicts the recorded ruling in spec §7 that "consumed MCP servers stay rejected per #8" and Tier A's own "standard-library only, no coupling" definition; the row flags the MCP dependency but never the recorded rejection.

**Evidence:** "instruction pack over Ai2's Asta MCP for Semantic Scholar | adds an MCP dependency"

**Verifier:** CONFIRMED. Adoption plan line 304 puts asta-skill in the Tier A "adopt as-is" whole-skill table (whose intro asserts "All verified MIT and standard-library-only", and §2.2 says "the tier is the recommendation") and line 434 repeats it in §2.9; the only hedge is the caution cell "adds an MCP dependency". Ground truth: foundation spec §7 line 129, inside the "CLI, not MCP" bullet, records "consumed MCP servers stay rejected per #8" (ruling 2026-08- …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:305 — MEDIUM (cross-doc)

**Claim:** Tier A ("adopt as-is"; §2.2 states "the tier is the recommendation") lists PHY041's claude-skill-citation-checker (line 305) and htlin222's research-guardian (line 306) as mirror candidates, while §3.4 (line 666) says "Not mirrored" for exactly those two and its Refused list (lines 705-706) rejects them because they decide verdicts — contradictory recommendations for the same two skills, which by §2.3's own admission also fail Tier A's test 4 (they "duplicate capability we have rather than adding capability we lack").

**Evidence:** Tier A row "| `claude-skill-citation-checker` | PHY041 | ..." vs line 666: "**Not mirrored:** PHY041 `claude-skill-citation-checker` and htlin222 `research-guardian`. Both are MIT and both decide verdicts"

**Verifier:** Confirmed contradiction. §2.2 (lines 254-256) makes tiering prescriptive: "Failing any one moves it down a tier, and the tier is the recommendation" — so the Tier A rows for PHY041 claude-skill-citation-checker (line 305) and htlin222 research-guardian (line 306) are adopt-as-is recommendations, not mere eligibility. §3.4 line 666 says "Not mirrored: PHY041 `claude-skill-citation-checker` and htlin222 `research-guardian`. Both are MIT and both de …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:390 — MEDIUM (adoption)

**Claim:** Tier E states gap-to-topic "is listed here rather than in Tier A", but the Tier A whole-skills table at line 303 does list gap-to-topic (and §3.4 then mirrors it), so the document assigns the same skill to two mutually exclusive tiers.

**Evidence:** "It is listed here rather than in Tier A because a skill is prompt text bound to its own vocabulary"

**Verifier:** Confirmed contradiction. Line 303 (§2.3 Tier A whole-skills table) lists `gap-to-topic` ("brings its own `design_brief.md` handoff vocabulary"), yet lines 389-392 (§2.7 Tier E) assert "It is listed here rather than in Tier A because a skill is prompt text bound to its own vocabulary and downstream handoff". Three further passages side with Tier A: §2.9's mirror table (line 432), §2.11's "of the six, ... `gap-to-topic` adds a step upstream of `pro …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:523 — MEDIUM (cross-doc)

**Claim:** Four references attribute the plan's own sections to the product comparison, which has no such subsections: line 523 "the sorting rule is §2.1 of the product comparison" (the rule is this plan's §2.1; the comparison's §2 is 'Read depth'), lines 606 and 654 "§2.9 of the product comparison" / "The comparison's §2.9" (mirroring is this plan's §2.9), and line 791 "the same conclusion the product comparison reaches in §1.2" (the comparison's §1 is 'Method'; the verdict is this plan's §1.2).

**Evidence:** "The sorting rule is §2.1 of the product comparison —" — the comparison's §2 ("Read depth") has no subsections

**Verifier:** Confirmed on all four references. The comparison (docs/product-landscape/2026-08-22-product-comparison-verified.md) has no §1.2, §2.1 or §2.9: its §1 "Method and evidence rule" (lines 27-58) and §2 "Read depth" (lines 59-96) contain no subsections or inline numbered anchors, and its headings jump §16 (line 2002) to §19 (line 2031) because §17/§18 were merged into this plan (plan lines 5-10). The misattributed content lives verbatim in the plan it …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:565 — MEDIUM (adoption)

**Claim:** The count "only one of the nine passes all three unchanged" contradicts the table immediately below it, which marks two skills "Write it, unchanged" (evidence-conventions and publish), and the section's own summary at line 581 ("two written as they are, two written smaller").

**Evidence:** "Applied honestly, only one of the nine passes all three unchanged."

**Verifier:** Confirmed. Line 565 says "only one of the nine passes all three unchanged," but the table immediately below marks two skills "Write it, unchanged" (evidence-conventions at line 569, publish at line 570 — each row's reasoning explicitly clears all three tests), and the section summary at lines 579-580 counts "two written as they are, two written smaller, and five that... would be a CLI verb, a mirror, or a rule" (2+2+5=9). No correction exists els …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:570 — MEDIUM (cross-doc)

**Claim:** §3 (moved verbatim from assembled-harness-spec §9) retains that document's section numbering, which now resolves to the wrong sections of this plan: line 570 "§2.10 confirms every other enforcement surface needs an operator flag" (plan §2.10 is the _quote_match measurement; the enforcement-surfaces table is assembled spec §2.10), line 571 "medsci `lit-sync` (§2.4)" (plan §2.4 is Tier B with no lit-sync; assembled §2.4 is 'Projection into the vault'), line 521 "Sections 1 to 8 answer the question as asked" (this doc has §0–§3), line 729 "§5 shows what an assembly costs", and lines 732/741/749 "(§2.6)" (plan §2.6 is Tier D; the armed-gate/FPR risk is comparison §8.5.2 and the retraction field assembled §2.6).

**Evidence:** "§2.10 confirms every other enforcement surface needs an operator flag" — this plan's §2.10 is "`_quote_match`, measured"

**Verifier:** CONFIRMED on every cited instance. Plan §3 was moved from assembled-harness-spec §9 (the spec's §9, line 327, is now a stub: "Moved... now live in [the adoption plan] §3"). The mover renumbered internal §9.x refs to §3.x and re-qualified comparison refs (§18.1 -> "§2.1 of the product comparison", per git show be4d83f~1), but left bare references to the assembled spec's own sections, which now mis-resolve inside the plan: line 570 "§2.10" -> plan  …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:572 — MEDIUM (adoption)

**Claim:** The factcheck-draft row asserts "§3.7 adopts medsci check_claim_fidelity.py", but §3.7's replace-now table does not contain check_claim_fidelity — the document elsewhere classifies it Tier B fork-the-algorithm (§2.4) and a port target (§1.5 step 2) — so the cross-reference is broken.

**Evidence:** "§3.7 adopts medsci `check_claim_fidelity.py`, which answers the same question deterministically"

**Verifier:** Confirmed. §3.7's replace-now table (adoption-plan lines 758-765) lists _quote_match.py, obra/knowledge-graph, check_reference_duplication.py/check_citation_keys.py, HALLMARK, pandoc+CSL and check-reporting — no check_claim_fidelity.py. That script is instead a §1.5 step-2 port target (lines 146-149) and Tier B fork-the-algorithm (line 320, §2.4: "fork a function, not a file"). No external referent rescues the pointer: the product comparison has  …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:572 — MEDIUM (cross-doc)

**Claim:** The factcheck-draft verdict says "§3.7 adopts medsci `check_claim_fidelity.py`", but §3.7's replace-now table does not contain it — the script sits in Tier B (§2.4, "fork a function, not a file": 644 lines bound to medsci's layout), so the reference is wrong and "adopts" overstates the Tier B recommendation the same document makes.

**Evidence:** "§3.7 adopts medsci `check_claim_fidelity.py`, which answers the same question deterministically" — §3.7 lists only _quote_match, knowledge-graph, duplicate detection, HALLMARK, pandoc and check-reporting

**Verifier:** Confirmed. Line 572 says "§3.7 adopts medsci `check_claim_fidelity.py`", but the plan's own §3.7 replace-now table (lines 756-765) lists only _quote_match.py, obra/knowledge-graph, check_reference_duplication.py/check_citation_keys.py, HALLMARK, pandoc+CSL, and check-reporting — the script is absent, and the comparison doc has no §3.7 at all (its §3 "Limits", lines 97-108, has no subsections), so no alternate referent rescues the pointer. The doc …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:622 — MEDIUM (adoption)

**Claim:** The §3.2 ownership-inversion argument is internally invalid at this step: the claim that vocabulary reconciliation is "paid once at adoption rather than continuously" is incompatible with the mirror mechanism's own rule ("no hand-edits, re-vendor to update", lines 279 and 421) — every re-vendor re-imports upstream's evolved prose with, by the section's own premise, no test to catch the silent regression — and §3.4's derived claim that a mirrored skill is "cheaper to hold ... because prose has no tests to hold it still" (line 672) derives cheapness from exactly the property that makes upstream drift undetectable, while the same section's evidence that skill evals exist (gbrain routing-eval, superpowers conformance) undercuts the no-tests premise.

**Evidence:** "that cost is paid once at adoption rather than continuously"

**Verifier:** CONFIRMED on the paid-once/cheaper-to-hold contradiction. Line 622 ("that cost is paid once at adoption rather than continuously") and its §3.4 restatement (lines 673-674, "a one-time cost paid per skill"; line 679, "Nothing on either list below is rejected on maintenance grounds") are incompatible with the doc's own mirror mechanism (line 279 "no hand-edits, re-vendor to update"; line 421 same rule — confirmed in ground truth: every skills/find- …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:654 — MEDIUM (adoption)

**Claim:** Several section citations point at the wrong document: "The comparison's §2.9" (654) and "§2.9 of the product comparison" (606) and "§2.1 of the product comparison" (523) name subsections the comparison does not have (its §2 "Read depth" has none) — the mirroring mechanism and sorting rule are this document's own §2.9 and §2.1 — while "(§2.8 gives the mechanism)" (296) points at Tier F instead of §2.9, and the "(§2.6)" citations for the false-positive/gate-abandonment risk (731, 741) resolve to the assembled note's "Post-publication signals", not to the FPR material in comparison §8.5.2/§12.

**Evidence:** "The comparison's §2.9 establishes mirroring a whole skill"

**Verifier:** All five legs confirmed. Comparison's §2 "Read depth" (product-comparison-verified.md:59) has no subsections, so "§2.1/§2.9 of the product comparison" (plan lines 523, 606, 654) cannot resolve there; the cited content is the plan's own §2.1 (line 203, "Adopt by default; build only where the artifact decides a verdict") and §2.9 (line 408 "Mirroring a whole skill"; line 410 "A third adoption mode sits between vendoring a file and taking a dependen …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:697 — MEDIUM (adoption)

**Claim:** The deferred-mirror row labels dataset identity as comparison group "11.1", but the comparison covers version-dataset/generate-codebook and "a dataset a claim depends on has no identity" under §11.5 (Output — the submit end, line 1783); §11.1 is verification-and-evidence and contains no dataset item.

**Evidence:** "| medsci `version-dataset`, `generate-codebook` | 11.1 dataset identity — a dataset a claim depends on currently has none |"

**Verifier:** Confirmed. Adoption-plan line 697 tags the medsci version-dataset/generate-codebook row as group "11.1", but the comparison doc's §11.1 (lines 1552-1631, "Verification and evidence — gaps on our own axis") contains no dataset item; the dataset-identity gap lives under §11.5 "Output — the submit end" at lines 1783-1786 ("a dataset a claim depends on has no identity in our vault"), which the row paraphrases almost verbatim. Sibling rows in the same …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:756 — MEDIUM (adoption)

**Claim:** The section title and "Why now" column direct replacing measured code (the selectors.find_context contiguous find, duplicate detection) immediately, contradicting this document's own §0 which assigns exactly those items post-Q ("measured code should not change while it is being measured") and the instrument-freeze discipline recorded at slice finding 14; a reader landing on §3.7 alone would wire _quote_match mid-Q.

**Evidence:** "### 3.7 Core — replace with third-party now"

**Verifier:** CONFIRMED. "Now" is a defined term in this document, not loose prose: §0's sequencing table (lines 26-30) uses "now" and "post-Q" as literal When-column values, and line 29 files exactly the reviewer's two items — "`_quote_match` at the selector site, duplicate detection" — under post-Q with the reason "measured code should not change while it is being measured". §3.7 (line 756, "Core — replace with third-party now") applies the class-1 "now" lab …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:779 — MEDIUM (adoption)

**Claim:** §3.9's tally "Five survive as written" contradicts §3.2's own result (two written as they are, two written smaller, five demoted to a CLI verb, mirror, or rule), and it also names project and setup-vault as the "thinner" survivors where §3.2's thinner pair is import-source and factcheck-draft — a reader cannot tell which preserve list governs.

**Evidence:** "Five survive as written because each carries a property nothing else has."

**Verifier:** Confirmed internal contradiction, no correction elsewhere. §3.9 (docs/product-landscape/2026-08-22-adoption-plan.md:779-781) tallies "Five survive as written ... Two — project and setup-vault — are thinner". §3.2 explicitly denies both halves: line 581 "The preserve list is not five skills — it is two written as they are, two written smaller, and five that from scratch would be a CLI verb, a mirror, or a rule in someone else's file" (line 565 eve …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-assembled-harness-spec.md:57 — MEDIUM (assembled-memoria)

**Claim:** 'Inherit nothing' contradicts both this doc's own section 2.2 row ('Already vendored here as `find-sources`') and the foundation spec section 7, which records find-sources as a vendored K-Dense paper-lookup fork and verify-citations/factcheck-draft as forks of scientific-writing's audit scripts under an adopt-by-default dependency discipline.

**Evidence:** which was to build the capabilities and inherit nothing

**Verifier:** CONFIRMED. Line 57's "build the capabilities and inherit nothing" is contradicted three ways: (1) same doc line 75 — K-Dense paper-lookup "Already vendored here as `find-sources`"; (2) foundation spec §7 line 120 — find-sources is a "**Vendored** fork of K-Dense `paper-lookup` (MIT)" — and line 129 — "`verify-citations` and `factcheck-draft` fork scientific-writing's offline audit scripts ... as starting points" under an adopt-by-default dependen …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-assembled-harness-spec.md:190 — MEDIUM (assembled-memoria)

**Claim:** Section 3's build list omits the adapter/join layer that the doc's own section 1.A declares unavoidable code ('That is not a component; it is the product') and that section 4's diagram labels part of 'the built part' (adapters -> result contract -> policy -> surfaces), so a reader tallying build cost from section 3 undercounts by the doc's own audit.

**Evidence:** Three things, and only three.

**Verifier:** Confirmed internal contradiction. Line 190's "Three things, and only three" (3.1 result contract, 3.2 policy layer, 3.3 claim addressing) drops the join/adapter layer the doc itself declares unavoidable code: §1.A lines 21-22 ("That is not a component; it is the product"), §1's close at lines 55-56 (assembled shape = components "plus an adapter layer that normalises their results, plus the claim addressing"), corroborated by the §4 diagram at lin …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-assembled-harness-spec.md:315 — MEDIUM (assembled-memoria)

**Claim:** Broken cross-reference: the product comparison no longer has a section 17.2 (headers jump from '## 16' to '## 19' after the same-evening restructure); the 'build the trust core, adopt the breadth' conclusion now lives in the adoption plan section 1.2 — and this doc was edited after the split (23:25 commit) without the pointer being updated.

**Evidence:** the same conclusion the product comparison reaches in §17.2 by a different route

**Verifier:** Confirmed on every element. (1) product-comparison-verified.md has no §17: headers jump from '## 16' (line 2002) to '## 19' (line 2031). (2) Pre-split commit 4f3b3d8 shows '### 17.2 The build-versus-adopt binary is false...' containing 'build the trust core, adopt the breadth'; split commit be4d83f (23:19) moved it verbatim to adoption-plan.md §1.2 (lines 85-89), and the adoption plan's line 6 states §17/§18 'lived at' the comparison. (3) The spl …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-assembled-harness-spec.md:315 — MEDIUM (cross-doc)

**Claim:** §8's verdict cites "the same conclusion the product comparison reaches in §17.2", but §17 no longer exists in the comparison (moved to the adoption plan, where the conclusion sits at §1.2).

**Evidence:** "this is the same conclusion the product comparison reaches\nin §17.2 by a different route: build the trust core, adopt the breadth."

**Verifier:** Confirmed. The comparison doc's headings jump from §16 to §19 (grep "^#" shows no §17/§18; grep "§17" in it returns nothing), and its lines 14-15 say the positioning judgment that "once sat here as Part V now live[s] in the adoption plan". The adoption plan's preamble (lines 5-7) states §17/§18 of the comparison were merged into it, and the "build the trust core, adopt the breadth" conclusion now sits at adoption plan §1.2 (lines 85-89) — the pla …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-memoria-and-knowledge-harness.md:45 — MEDIUM (assembled-memoria)

**Claim:** The dependency row understates Memoria's runtime dependency surface: pyproject.toml at the recorded commit 5395a87d declares dependencies = ["pydantic-ai-slim[openai]>=2.0", "PyMuPDF>=1.24,<2", "PyYAML>=6.0"] — an LLM framework and a PDF library are omitted, and pyproject is not in the doc's declared read list, so the fact lacks the evidence-rule sourcing.

**Evidence:** Python 3.12+, `yaml`, provider keys per flow, Node 22 for the adapter

**Verifier:** Confirmed. `git show 5395a87d:pyproject.toml` in ~/memoria-vault gives dependencies = ["pydantic-ai-slim[openai]>=2.0", "PyMuPDF>=1.24,<2", "PyYAML>=6.0"], exactly as the reviewer quoted; doc line 45 lists only "Python 3.12+, `yaml`, provider keys per flow, Node 22 for the adapter", omitting the LLM framework and PyMuPDF while the sibling knowledge-harness cell counts pinned packages ("one pinned runtime dependency... `pypdf` behind an extra") —  …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-memoria-and-knowledge-harness.md:77 — MEDIUM (assembled-memoria)

**Claim:** Memoria's K1 rule ('every non-reserved .md') is not verbatim ADR 0001's rule, which scopes to machine-written files ('every machine-written .md carries parseable YAML frontmatter with a non-empty type') and explicitly keeps fleeting human-captured notes frontmatter-free — a scope difference K1's rule would violate, so the claimed exact convergence is wrong.

**Evidence:** That is verbatim the rule our ADR 0001 states.

**Verifier:** Confirmed. The doc (docs/product-landscape/2026-08-22-memoria-and-knowledge-harness.md:77-78) says K1's rule "is verbatim the rule our ADR 0001 states," but docs/adr/0001-vault-outlives-harness.md:7 states "every machine-written `.md` carries parseable YAML frontmatter with a non-empty `type`" — not "every non-reserved `.md`" — and the same line makes the scope difference explicit and load-bearing: "fleeting human-captured notes stay frontmatter- …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-memoria-and-knowledge-harness.md:138 — MEDIUM (assembled-memoria)

**Claim:** Credits Memoria's sweep with Open Retractions as a live 'independent cross-check' advantage, while the sibling assembled-harness spec (section 2.6), from the same 2026-08-22 survey, verified openretractions.com 'not usable' — unreachable (HTTP 000) with the probe validated against two 200-returning hosts, and its data described upstream as ~2020.

**Evidence:** **Open Retractions** as an independent cross-check

**Verifier:** CONFIRMED. The memoria doc (docs/product-landscape/2026-08-22-memoria-and-knowledge-harness.md:135-140) bolds "Its retraction sweep is better than ours" and credits "**Open Retractions** as an independent cross-check" (line 138), then frames our lack of "an independent third source" as a gap — with no reachability or staleness caveat anywhere in the doc (grep for 000/unreachable/not usable/stale/2020 finds nothing relevant). The same-evening sibl …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-memoria-and-knowledge-harness.md:138 — MEDIUM (cross-doc)

**Claim:** The note credits Memoria's retraction sweep for using "Open Retractions as an independent cross-check" and faults us for lacking "an independent third source", but the assembled-harness spec (line 124) verified openretractions.com the same day as "not usable" — unreachable (HTTP 000, probe validated against Crossref/GitLab 200s) with data described upstream as ~2020 — so one doc scores as an advantage a source its sibling rules out.

**Evidence:** "**Open Retractions** as an independent cross-check" vs assembled spec line 124: "**not usable.** Unreachable from this machine on 2026-08-22 (HTTP 000)"

**Verifier:** Confirmed. docs/product-landscape/2026-08-22-memoria-and-knowledge-harness.md L135-140 credits Memoria's sweep with "**Open Retractions** as an independent cross-check" and faults us: "we use neither `relation.is-retracted-by` nor an independent third source" — with no qualification anywhere in the file. The sibling spec, same day/same tree, docs/product-landscape/2026-08-22-assembled-harness-spec.md L124: "openretractions.com | — | **not usable. …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-memoria-and-knowledge-harness.md:139 — MEDIUM (assembled-memoria)

**Claim:** Presents our Retraction Watch CSV leg as live coverage, while the same-day no-fabrication audit (finding 1, checks.py:924, verifier-CONFIRMED against the production CSV) records 'The entire RW leg silently dead while verify reports as if coverage ran' — the doc never notes this.

**Evidence:** We use the RW CSV, Crossref `updated-by`, and OpenAlex `is_retracted`

**Verifier:** Stands, at medium not high. Doc line 138-139 states unqualified "We use the RW CSV, Crossref `updated-by`, and OpenAlex `is_retracted`" as our sweep's source inventory; ground truth (docs/2026-08-22-no-fabrication-audit.md:88-92, finding 1, verifier-CONFIRMED against the production CSV) shows the RW leg is inert — checks.py:898-906 parses RetractionDate fromisoformat-only, 922-927 silently drops _INVALID rows, and the production CSV's "M/D/YYYY 0 …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-memoria-and-knowledge-harness.md:139 — MEDIUM (cross-doc)

**Claim:** "We use the RW CSV, Crossref `updated-by`, and OpenAlex `is_retracted`" states Retraction Watch CSV use as operational fact, but the same-day audit (docs/2026-08-22-no-fabrication-audit.md, finding 1, CONFIRMED by independent reproduction) shows the RW leg is inert — load_rw_csv drops every production row because RetractionDate is "M/D/YYYY 0:00", not ISO — so the sweep comparison understates the gap against Memoria.

**Evidence:** "We use the RW CSV" vs audit line 11: "Retraction Watch screening is inert ... The entire RW leg silently dead while verify reports as if coverage ran."

**Verifier:** CONFIRMED. checks.py:898-906 (_rw_date returns _INVALID for non-ISO strings) plus load_rw_csv's skip at checks.py:922-927 verify the audit's finding 1: every production RW row ("M/D/YYYY 0:00" dates) is silently dropped, so the RW leg is inert. The doc's line 139 ("We use the RW CSV") states it as live coverage in a source-by-source tally with no correction anywhere in the file; the Limits hedge (lines 219-223, "claims about what each implements, …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-memoria-and-knowledge-harness.md:198 — MEDIUM (assembled-memoria)

**Claim:** Broken cross-references at lines 8, 198, and 201: the product comparison no longer contains a section 17 or 18.1 (its headers jump from '## 16' to '## 19' after the 2026-08-22 23:19 restructure) — the 'build the trust core, adopt the breadth' verdict now lives in the adoption plan section 1.2 and the adopt-by-default rule in adoption plan section 2.1 (line 203).

**Evidence:** The comparison document's §17 concludes "build the trust core, adopt the breadth"

**Verifier:** CONFIRMED. The comparison doc's headers jump from "## 16. Searched and not added" (line 2002) directly to "## 19. Re-running this comparison" (line 2031); grep for any ##/### 17.x or 18.x header returns nothing. Commit be4d83f (2026-08-22 23:19:39, "split the product-landscape notes by lifecycle") explicitly states it "Extracted §17 (positioning verdict) and §18 (vendoring tiers) from the comparison" into the adoption plan and rewrote "seven inbo …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-memoria-and-knowledge-harness.md:198 — MEDIUM (cross-doc)

**Claim:** The note cites the comparison's §17 twice (lines 8 and 198: "The comparison document's §17 concludes 'build the trust core, adopt the breadth'") and §18.1 (line 201), but those sections were moved out of the comparison — the verdict now lives at adoption plan §1.2 and the adopt-by-default rule at adoption plan §2.1; the comparison jumps from §16 to §19.

**Evidence:** "The comparison document's §17 concludes \"build the" and line 201 "(§18.1: adopt by default; build only where the artifact decides a verdict)"

**Verifier:** Confirmed on every particular. The comparison doc's headings jump from "## 16. Searched and not added" (line 2002) to "## 19. Re-running this comparison" (line 2031) with only "---" separators between — no §17 or §18 exists. The adoption plan's own preamble (lines 5-7) states the move outright: "the positioning verdict and the vendoring classification lived at §17 and §18 of [the product comparison]". The reviewer's relocation targets both verify …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:113 — MEDIUM (self-claims)

**Claim:** The "measured from source" deterministic-core row matches no single tree: the main checkout has 27 modules (not 26), declares zero runtime dependencies, and parses external XML with stdlib ElementTree — defusedxml==0.7.1 exists only in the unmerged build/quality-lane worktree — and the doc's own §13 row contradicts it.

**Evidence:** "26 Python modules, 9,716 lines; **one** pinned runtime dependency — `defusedxml`" — main tree: 27 files totalling 9,716 lines, pyproject.toml `dependencies = []`, checks.py:6 `import xml.etree.ElementTree`; worktree has defusedxml but 9,824 lines; §13 line 1909 says "Dependencies | stdlib only".

**Verifier:** CONFIRMED — no frame makes the whole row true. Main-tree frame: dependency clause false — pyproject.toml has `dependencies = []`, checks.py:6 is `import xml.etree.ElementTree`, and defusedxml==0.7.1 exists only in commit 3f72d7a (2026-08-22) on unmerged build/quality-lane. Author's own worktree frame (commit cced181: "I read main instead of the worktree"): counts false — worktree is 27 modules / 9,824 lines, not 9,716. Either frame: §13 line 1909 …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:114 — MEDIUM (self-claims)

**Claim:** The test count of 1,467 does not match the main tree, which collects 1,330 tests; ~1,470 collect only on the unmerged build/quality-lane worktree, contradicting §3's assertion that "our own side was measured from source, so its numbers are exact".

**Evidence:** "Tests | 1,467 collected" — `pytest --collect-only -q` on the main checkout: "1330 tests collected"; on .claude/worktrees/build+quality-lane: "1470 tests collected". The figure recurs at lines 890, 1108, 1566 and 1819.

**Verifier:** CONFIRMED by direct measurement: main checkout (eecff57) collects 1330 tests; the unmerged build/quality-lane worktree collects 1470; the doc's 1,467 matches neither and recurs at lines 114, 890, 1108, 1565, 1819. Git history shows commit cced181 (22:37 on 08-22) changed 1,330 to 1,467 by reading the worktree ("I read main instead of the worktree… the suite is 1,467 tests, not 1,330"), yet the doc nowhere discloses branch scoping (no worktree/qua …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:114 — MEDIUM (sourcing)

**Claim:** The test count 1,467, asserted five times and called "exact" by §3, matches neither the main tree (1,330 collected) nor the Plan-Q worktree (1,470 collected).

**Evidence:** "| Tests | 1,467 collected" — `pytest --collect-only -q` on main at HEAD collects 1,330 with zero errors (tests/ last changed 2026-08-22 10:54, before the doc); the build/quality-lane worktree collects 1,470. Repeated at lines 890 ("Our 1,467 tests prove..."), 1108, 1565 ("1,467 tests say so"), 1819, while §3 line 107 claims "Our own side was measu

**Verifier:** CONFIRMED. Measured directly: main@eecff57 collects 1,330 (`pytest --collect-only -q`; tests/ untouched since 2026-08-22 10:54, commit f047116), worktree@1308682 collects 1,470 — 1,467 matches neither. Provenance: the doc originally said 1,330 (correct for main); commit cced181 (23:37:59, msg: "the suite is 1,467 tests, not 1,330") flipped all five occurrences (114, 890, 1108, 1565, 1819) to the worktree's count at f61c14b (23:35:49), which I ver …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:125 — MEDIUM (self-claims)

**Claim:** Trust tiers are described as "derived from `verified` events", but the audit confirmed the machine-confirmed tier is minted vacuously for any note lacking a DOI/PMID with zero verified events ever recorded.

**Evidence:** "Trust tiers | unverified → machine-confirmed → human-reviewed, derived from `verified` events" — audit defect 3 (events.py:255): `_applicable_note_checks(data) <= checks` is vacuously True for an empty applicable set; "even a frontmatter-less file derives 'machine-confirmed'" (reproduced empirically).

**Verifier:** CONFIRMED. Doc line 125 reads exactly "Trust tiers | unverified → machine-confirmed → human-reviewed, derived from `verified` events". Ground truth contradicts the unqualified derivation claim: knowledge_harness/events.py:234-239 (_applicable_note_checks falls through to `return set()` for any note lacking doi/pmid), :255 (`machine_confirmed = _applicable_note_checks(data) <= checks` — set() <= checks is vacuously True), :282 (returns "machine-co …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:143 — MEDIUM (cross-doc)

**Claim:** The §5 roster row claims "16 in the main table" but the §6 table has 15 rows (research-hub, written up at §6.15, is absent from it), and claims 16 search finds "of which 6 were read at file level (marked ✓)" while §6.16 carries only 3 ✓ marks (Orchestra-Research, Astro-Han, trapoom555).

**Evidence:** "16 in the main table, all read at file level, plus 16 found by search of which 6 were read at file level (marked ✓)"

**Verifier:** Confirmed on both prongs. (1) The §6 main table (lines 154-168) has exactly 15 data rows; WenyuChiou/research-hub — written up at file level in §6.15 (line 577) and listed among file-level reads in §2 (line 73) — has no table row, making it the missing 16th, so "16 in the main table" is off by one. (2) The §6.16 table (lines 646-661) does have 16 rows, but only 3 carry ✓ (Orchestra-Research 646, Astro-Han 650, trapoom555 661); the 5 ◐ rows are de …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:220 — MEDIUM (sourcing)

**Claim:** The closest-competitor section gives medsci's self-review skill 52 scripts here and 36 scripts twice elsewhere, an unresolved contradiction under the 33-gate/43-gate verdict built on those counts.

**Evidence:** "Reading `self-review` (52 scripts) and `sync-submission` (21)" vs line 206 "`self-review` (36 scripts, 26 tests)" and line 2088 "medsci `self-review` (36 scripts)".

**Verifier:** CONFIRMED. The doc gives self-review 52 scripts at line 220 but 36 scripts at lines 206 ("36 scripts, 26 tests") and 2088 ("medsci `self-review` (36 scripts)"), with no reconciliation anywhere in the doc, the companion docs (adoption-plan line 183 also says 36), or git history (both figures were introduced in the same commit). Ground truth: Aperivue/medsci-skills pushed_at is 2026-08-19T06:04Z — before the doc was written — so the GitHub tree tod …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:665 — MEDIUM (sourcing)

**Claim:** §7's method note says only zotero-mcp was read at file level, yet seven §7 rows carry the ✓ "file opened" mark and §2 lists those same components as file-level reads.

**Evidence:** "Only 54yyyu/zotero-mcp was read at file level; the rest are metadata-level rows" — contradicted by ✓ marks on Hylouis233/bibverify (line 695), PHY041/claude-skill-citation-checker (696), htlin222/research-guardian-skill (700), Agents365-ai/asta-skill (741), PouriaRouzrokh/LatteReview (749), htlin222/prisma-automation (750), obra/knowledge-graph (7

**Verifier:** Confirmed. Line 665-666 states "Only 54yyyu/zotero-mcp was read at file level; the rest are metadata-level rows", but the ✓ legend (lines 640-642: "except where a file was opened, marked ✓") governs §7's tables, and all seven cited ✓ rows exist (lines 695, 696, 700, 741, 749, 750, 751). §2's "Read at file level" list (lines 61-73) independently names all seven components, and four of them (bibverify, citation-checker, research-guardian-skill, kno …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:666 — MEDIUM (cross-doc)

**Claim:** §7's intro asserts "Only 54yyyu/zotero-mcp was read at file level; the rest are metadata-level rows", yet §7's own tables mark bibverify, PHY041/claude-skill-citation-checker, htlin222/research-guardian, htlin222/prisma-automation, PouriaRouzrokh/LatteReview, obra/knowledge-graph and Agents365-ai/asta-skill with ✓ (file opened), and §2 lists bibverify as a file-level read whose error-path contract test the assembled spec quotes.

**Evidence:** "Only 54yyyu/zotero-mcp was read at file level; the rest are metadata-level rows" vs line 695 bibverify row ending "...we do not ✓"

**Verifier:** Confirmed. Lines 665-666 ("Only 54yyyu/zotero-mcp was read at file level; the rest are metadata-level rows") are contradicted by the doc itself: §2 lines 61-73 list bibverify, PHY041/claude-skill-citation-checker, htlin222/research-guardian-skill, htlin222/prisma-automation, PouriaRouzrokh/LatteReview, obra/knowledge-graph and Agents365-ai/asta-skill as "Read at file level (cloned, one or more files opened and quoted)"; §7's tables mark those sam …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:906 — MEDIUM (self-claims)

**Claim:** The clause that we "nowhere reason about" our false-positive rate is stale: spec §6's warn-tier precision doctrine and §9's measured inbox-precision output — both reasoning about exactly that rate — were added to the spec earlier the same day, before this doc was written ("never measured" remains true).

**Evidence:** "We have never measured, and nowhere reason about, our false-positive rate" — spec §6 (added 2026-08-22): "a warn-tier check class whose observed inbox precision collapses is itself a defect"; spec §9 (added 2026-08-22): "the slice also records per-check-class review-inbox precision ... as data".

**Verifier:** Confirmed. Doc lines 905-906 assert "We have never measured, and nowhere reason about, our false-positive rate", but the spec (foundation-spec.md) line 92 (§6) carries "Precision is a warn-tier obligation (added 2026-08-22): a warn-tier check class whose observed inbox precision collapses is itself a defect", and line 148 (§9) carries "Measured output (added 2026-08-22, ruling on the false-positive finding): the slice also records per-check-class …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:940 — MEDIUM (sourcing)

**Claim:** §8.5.1 claims all four papers were read as full texts, while §8.5.3 describes the same reading as "four abstracts, one results table" and §8.5.4 concedes sections went unread — the evidence depth behind §8.5's figures is stated inconsistently.

**Evidence:** "All four are in `sources/` and were read as full texts, not abstracts." vs line 1053 "it was also the cheapest: four abstracts, one results table, and a repository already cloned" and line 1061-1063 "The mechanism is not in the sections read." (The four PDFs do exist in sources/.)

**Verifier:** CONFIRMED — the contradiction is line 940 vs line 1053, and git history proves line 1053 is a stale leftover. Line 940 (§8.5.1) says "All four are in `sources/` and were read as full texts, not abstracts"; line 1053 (§8.5.3) describes the same reading as "four abstracts, one results table, and a repository already cloned." Commit 2f908ff (21:37, pre-download) wrote the section from abstracts — the sentence originally sat beside "Abstracts were en …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:1267 — MEDIUM (self-claims)

**Claim:** The import-source seam analysis — no untrusted-content rules needed because the input is a Zotero record, not fetched text — predates same-day slice findings 15/16, which ruled an LLM-authored digest from the source's full text into import-source, with the sanctioned route being the agent reading the attachment directly.

**Evidence:** "we need no capture adapters, no format conversion, no egress consent and no untrusted-content rules in this skill, because the input is a Zotero record rather than fetched text" — slice finding 15: "RULED: add an explicit ingest step to `import-source` ... the session agent authors a free-region digest"; finding 16: "the sanctioned route ... the a

**Verifier:** CONFIRMED. The doc states the pre-ruling boundary twice — lines 1266-1269 ("we need no ... untrusted-content rules in this skill, because the input is a Zotero record rather than fetched text") and lines 1647-1649 (§11.2 repeat) — and carries no correction anywhere (grep for untrusted/digest/ruling/amended/finding across the doc: only competitor passages at 298, 347-348, 1256 plus the two stale statements). Ground truth docs/2026-08-22-slice-find …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:1603 — MEDIUM (self-claims)

**Claim:** The likelihood-axis gap is presented as an unaddressed indictment ("It indicts our confidence field", line 843) without noting that the spec recorded the confidence-axis split the same day as a deliberate, trigger-named deferral.

**Evidence:** "A likelihood axis, and a closed vocabulary for it ... Our `[confidence:: …]` collapses both into one free field" — spec §10 (recorded 2026-08-22): "§5's `[confidence:: ...]` deliberately conflates two axes ICD 203 keeps apart ... split trigger = slice friction".

**Verifier:** Confirmed. Comparison doc lines 843-849 ("It indicts our confidence field … no separate likelihood axis at all") and 1603-1605 (§11.1 gap entry) present the conflation as an unanswered gap, with no mention of the spec ruling anywhere in the doc or sibling landscape docs (greps for "confidence-axis", "deliberately conflat", "slice friction" return nothing). Ground truth: foundation-spec §10 line 153 records "confidence-axis split (recorded 2026-08 …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:1897 — MEDIUM (self-claims)

**Claim:** The citability axis carries the stale tier-1 form — bibliography membership — where the spec (amended 2026-08-22, before this doc was written) rules tier-2 citability (the literature note must exist), and the audit confirmed tier-2 is unenforced so a never-imported citation publishes cleanly.

**Evidence:** "What is citable | only a human-admitted Zotero item" — spec §4: "a claim's citekey is citable only if its literature note exists (tier 2 ... ) Accidental cross-project citation fails loudly"; audit defect 4 (checks.py:151): "a never-imported citation reports MATCHED and publishes". The §12 entry at line 1871 repeats the tier-1 form.

**Verifier:** CONFIRMED. Doc line 1897 answers the "What is citable" axis with "only a human-admitted Zotero item" — the tier-1 form. Spec §4 (L45, commit 8df8c9c, 2026-08-22 16:04 -0500) rules two-tier citability hours BEFORE the doc's commits (22:50–23:37 same day): "a claim's citekey is citable only if its literature note exists (tier 2)" and explicitly "library-present ≠ citable-in-this-vault", so the doc names a superset of the citable set as the boundary …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:1902 — MEDIUM (self-claims)

**Claim:** Git pre-commit is named a harness-armed closed enforcement point without noting the audit-confirmed defect that the shipped hook exits 0 when the knowledge_harness package is unimportable — the common default-install case — while promising a CI replay that a default scaffold does not have.

**Evidence:** "Enforcement point | git pre-commit, PostToolUse warn, Stop gate — armed by the harness, not by an operator flag" — audit defect 16 (templates/git/pre-commit:12): "exits 0 when knowledge_harness is not importable while asserting 'CI will replay verification'; scaffold.py:192 defaults with_ci=False ... the promised compensating control is fabricated

**Verifier:** Defect stands. Ground truth confirms every element: templates/git/pre-commit:10-13 exits 0 when knowledge_harness is unimportable while printing "CI will replay verification", contrasting its own python3-missing branch (lines 6-9, exit 1); scaffold.py:192 defaults with_ci=False and copies verify.yml only when with_ci=True, so a default vault has no CI replay; pyproject.toml has no [project.scripts], supporting the audit's "reachable as the common …[full verdict in workflow journal wf_ffc62986-0a8]

### README.md:9 — MEDIUM (cross-doc)

**Claim:** The cadence column says the memoria note updates "when Memoria moves, which is daily", but the memoria note contains no cadence self-description and nowhere states that Memoria moves daily — the only supporting figure is a commit total (1,441 since 2026-05-27) from which "daily" is the README's own inference.

**Evidence:** "when Memoria moves, which is daily" — the memoria note self-describes only as "Analysis note, 2026-08-22"

**Verifier:** CONFIRMED. README.md:9 flatly asserts the memoria note updates "when Memoria moves, which is daily". The memoria note (docs/product-landscape/2026-08-22-memoria-and-knowledge-harness.md) self-describes only as "Analysis note, 2026-08-22" (line 3); grep for daily/cadence/"per day"/"every day" across the note returns zero hits, so it contains no cadence statement. Its only cadence-adjacent data is the table at lines 38-39: first commit 2026-05-27,  …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-adoption-plan.md:53 — LOW (adoption)

**Claim:** The description of the landed Task 2 suite says it asserts disable-model-invocation "is boolean", but tests/test_skill_contracts.py:107 asserts string equality (== "true") for entry skills and absence for guards — no boolean-type assertion exists.

**Evidence:** "asserts `name` matches its directory, `description` is non-empty, and `disable-model-invocation` is boolean"

**Verifier:** Confirmed. tests/test_skill_contracts.py:107 asserts data.get("disable-model-invocation") == "true" (string) for ENTRY_SKILLS and lines 111-114 assert the key is ABSENT for guard skills — no boolean-type assertion exists. It could not: the suite's own parser (knowledge_harness/frontmatter.py:88-94, _parse_scalar) returns only str/int, so `true` parses as the string "true" and a boolean assertion would fail every skill. The doc's other description …[full verdict in workflow journal wf_ffc62986-0a8]

### 2026-08-22-product-comparison-verified.md:220 — LOW (cross-doc)

**Claim:** §6.1 states medsci's self-review skill has "52 scripts" while the same section fourteen lines earlier says "36 scripts, 26 tests", and §19.4 (line 2088) and the adoption plan §1.7 both use 36 — an unresolved numeric contradiction in a surveyed fact.

**Evidence:** Line 220 "Reading `self-review` (52 scripts)" vs line 206 "`self-review` (36 scripts, 26 tests)"

**Verifier:** Confirmed against the surveyed tree itself (/tmp/medsci-audit/skills/self-review): `scripts/` holds 52 directory entries, but only 36 are Python scripts — the other 16 are `*_challenge` fixture directories (expected/fixture/problem.md/verify.sh, no .py), and `tests/` has 26 entries. So line 206 ("36 scripts, 26 tests"), §19.4 line 2088, and adoption-plan line 183 match ground truth, while line 220's "Reading `self-review` (52 scripts)" miscounts  …[full verdict in workflow journal wf_ffc62986-0a8]

### README.md:8 — LOW (sourcing)

**Claim:** Three of the four size figures in the README's table are stale against the shipped files.

**Evidence:** "| product-comparison-verified | ... | 2,092 |" (actual 2,095 lines), adoption-plan "741" (actual 792), assembled-harness-spec "312" (actual 330); memoria "223" is correct — the docs were edited after the README (README 23:19, comparison 23:38).

**Verifier:** Confirmed by wc -l: actual sizes are 2,095 (comparison), 792 (adoption-plan), 330 (assembled-harness-spec), 223 (memoria) vs README lines 8-11 which state 2,092 / 741 / 312 / 223 — three of four stale, memoria correct. Mtimes match the reviewer's mechanism (README 23:19, docs 23:37-23:38). No hedge or correction elsewhere in the README. Severity low: a stale line-count in an index table's Size column is minor bookkeeping drift, not a fact a reade …[full verdict in workflow journal wf_ffc62986-0a8]

### README.md:10 — LOW (cross-doc)

**Claim:** Three of the four Size figures in the README table do not match the files: adoption-plan is listed at 741 lines but is 792, assembled-harness-spec at 312 but is 330, product-comparison at 2,092 but is 2,095 (the docs were edited after the README was written; only memoria's 223 still matches).

**Evidence:** "| [adoption-plan](2026-08-22-adoption-plan.md) | ... | as we act on it | 741 |" — wc -l reports 792

**Verifier:** Confirmed. wc -l today: adoption-plan 792, assembled-harness-spec 330, product-comparison 2095, memoria 223 — README (lines 8-11) says 741/312/2,092/223, so three of four are stale and only memoria matches. Git proves the reviewer's causal story exactly: at be4d83f, the commit that wrote the README ("docs: split the product-landscape notes by lifecycle"), the files measured 741/312/2092/223 — matching the README to the line — and five later commi …[full verdict in workflow journal wf_ffc62986-0a8]

## Refuted (8)

Kept as negative knowledge in the workflow journal (wf_ffc62986-0a8) — claims the verifiers overturned after checking the tree; not re-listed here to keep this report actionable.

## Suggested disposition (author triages)

- Cluster 1 wants one systematic fix: a "measured vs designed" marker on every our-side row, plus a pointer to the no-fabrication audit — cheaper and more honest than re-verifying each row.
- Clusters 2, 3, 5, 8 are mechanical: reconcile the read-depth lists, pick one script count, re-run the two tree measurements on the tree the doc names, fix the ~10 dangling refs, refresh the README.
- Cluster 6's contradictions need the writing session's intent — tier assignments and tallies can't be reconciled mechanically.
- Cluster 7's Memoria dependency row should be corrected before anything cites the cost comparison.
