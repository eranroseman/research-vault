# Current-state sweep at the close of lane 1 — the list

**Goal:** after Part B of the ingest redesign merges, the repository describes the project as it is, not how it got here. Every file, section and sentence below is either deleted, rewritten to state a current fact, or kept because it is a current fact. Git history holds everything removed.

**Principle (the operator's, 2026-09-16):** historical records read out of context mislead. Eliminate the problem (delete the record) before adding a mechanism (a lint) before adding a rule (prose in AGENTS.md). ADR 0003 already licenses the deletions: "Repo artifacts — plans, docs, code — are outside this ADR: deleting them is normal hygiene."

**Method:** two read-only surveys on 2026-09-16 over main at 6ba5585 — one classifying every record file under `docs/` and `.out-of-scope/` (106 files), one auditing every current-state surface (README, CONTEXT, AGENTS, ATTRIBUTION, `docs/agents`, `docs/adr`, terminology, testing, the skills, the templates, the plugin manifests, config comments, module docstrings) for history-shaped content. Every path and line cited was verified against the tree. Part B's own deliverables (its plan, register, results file, tracer report) join section A when it merges.

**Order:** run after Part B merges (its plan, the ingest spec's §4.3 sentence, `skills/synthesis-conventions`, `templates/vault/AGENTS.md` and `quality.yml`'s CRAP block are all in flight on its branch). Sections B and C (rewrites) go before section A (deletions), because the deletions break the references the rewrites remove.

______________________________________________________________________

## A. Delete

Files whose content is a record of what happened. Each is either executed and merged, a run report, a proposal absorbed or overtaken, or a research note whose conclusion lives in an active spec or in code. Where a survivor still points at a file, the pointer is listed in B/C and is rewritten first.

### A1. Executed plans and their registers — `docs/superpowers/plans/`

- `2026-08-22-plan-s-validation-slice.md`, `2026-08-22-post-q-batch.md`, `2026-08-22-slice-decision-rules.md`, `2026-09-01-canonical-vault-glossary-projection.md`, `2026-09-02-okf-conformance.md`, `2026-09-05-status-marking-pass.md` (a plan for a marker system that was itself deleted on 2026-09-07), `2026-09-13-plan-w-quality-tail.md`, `2026-09-13-plan-w-quality-tail-deferred.md` (46 rows, every one dispositioned).
- `2026-09-07-ingest-redesign-a-capture.md` and `2026-09-07-ingest-redesign-a-deferred.md` — after Part B merges. Part B's plan binds to Part A's "Decisions this plan settles (01–25)" by number; those decisions that are still load-bearing must be in the ingest spec's decision register before the plan goes (C3). The register's nine process notes are lessons about running plans; if any is wanted it goes into `docs/agents/` as a rule, not as a numbered anecdote.
- `2026-09-07-ingest-redesign-b-compile.md`, `2026-09-07-ingest-redesign-b-deferred.md` — after the merge, on the same terms.
- This file, once executed.

### A2. Run reports and evidence — `docs/superpowers/specs/*-results.md`, `*-evidence.md`

Results files are run reports; evidence files are dated inputs whose conclusion the spec already states.

- Results: `2026-08-16-foundation-spec-pre-slice-batch-boundary-review-results.md`, `…-pre-slice-batch-method-results.md`, `…-pre-slice-batch-review-results.md`, `…-validation-slice-results.md`, `2026-09-06-import-redesign-part-a-results.md`, `2026-09-06-import-redesign-part-a-mutation-survivors.md` (a mutate4py run pinned to one sha; re-measured over mutmut into `mutation-baseline.txt`), `2026-09-13-plan-w-quality-tail-results.md`, and Part B's `…-part-b-results.md` when it lands.
- Evidence, absorbed: `2026-08-16-foundation-spec-adoptable-skills-audit-evidence.md`, `…-ideaverse-lite-structure-evidence.md`, `…-mutate4py-defects-evidence.md` (see D4 first), `…-pkm-vault-schemas-evidence.md`, `…-plugin-packaging-mechanics-evidence.md`, `…-provenance-schemas-evidence.md`, `…-skill-inventory-gap-analysis-evidence.md`, `2026-09-06-import-redesign-compile-layout-evidence.md` and `…-partial-adoption-evidence.md` (the ingest spec §4.2 already says they bind nothing).
- Evidence the operator decides on: D1–D3.
- `2026-09-01-canonical-vault-glossary-projection-design.md` — the design of an executed plan; the glossary lives in CONTEXT.md.

### A3. Research, prior art, audits, proposals — whole folders

- `docs/research/prior-art/` (15 files), `docs/research/rethink-audits/` (7), `docs/research/validation-slice/` (10), `docs/research/raw/` (16, including `wide-prior-art/`), `docs/research/harness-audits/` (2), `docs/product-landscape/` (10, README included), `docs/2026-08-28-proposed-adr-and-context-changes.md`, `docs/2026-08-31-proposed-adr-and-context-changes.md`.
- `docs/research/2026-08-25-plugin-development-process-reconstruction.md`, `2026-09-01-okf-conformance-audit.md`, `2026-09-01-pre-spec-competitive-analysis.md`, `2026-09-01-r27-completion.md`, `2026-09-01-requirements-artifact-prior-art.md`.
- Held back pending a decision: `2026-08-23-mutmut-defect-reports.md` (D4), `2026-09-04-import-sourcing.md` (D2), `2026-09-05-zotero-api-reading.md` (D3), `validation-slice/2026-08-22-case-study-question-bank.md` (D5).
- Before `rethink-audits/2026-08-21-lint-format-rethink.md` goes: `tests/test_canonical_form.py:3`, `tests/test_config_validity.py:13` and `.vscode/settings.json:1` cite it as the form-owner matrix's source. The matrix's current home is `README.md` ("one form owner per type") and `.pre-commit-config.yaml`; repoint the three docstrings there.

### A4. The `Disposition:` markers

64 files carry a `Disposition:` header in a vocabulary deleted on 2026-09-07. All but one are in A1–A3; the survivor is `docs/superpowers/specs/2026-08-16-foundation-spec.md:3` (`pending-map`), rewritten in C1. After the sweep the count is zero; E1 keeps it there.

### A5. Dead sections in current-state surfaces

- `README.md` "## Planning" (a closed wayfinder map, a plan directory that will not exist, and a link to `docs/research/harness-audits/dev-harness-analysis.md`, which was deleted at `ec77cb0`).
- `docs/agents/issue-tracker.md` "## Wayfinding operations" (no `/wayfinder` in this environment; the labels `wayfinder:*` in `.github/labels.yml` and on GitHub go with it).
- `docs/agents/domain.md:55–69` provenance preamble and quoted chat rulings under "This repo's ADR authoring rules" (keep the rules; delete the anecdotes).
- `docs/agents/sourcing.md` "## Why the bar exists" and "## The higher rung" (rationale and an unfiled-issue note; the rule stands alone).
- `docs/terminology.md:194–196` the stale-name list (`knowledge-harness`, `.harness/`, `HARNESS_*`, `hk-`): no test reads it; the names are gone.
- `docs/testing.md` "## Multi-seat venv parity" except its last sentence, and the dead-port measurement narrative at :48–50 (keep the rule "bind an ephemeral port").
- `skills/setup-vault/SKILL.md` "## Migrate an older vault" (`citekey:` → `citationKey` one-shot migration for a pre-release spelling; the design is greenfield). Check `notes.rename_frontmatter_key` for other callers before deleting its code.
- `.github/workflows/quality.yml` the CRAP deferral comment (Part B Task 4 replaces it on the branch; confirm after merge that no `archive.py` / `check_metadata` / `189 consecutive runs` text remains) and `:52–54` (a comment correcting an old commit subject).
- `pyproject.toml:37–39` (an instruction to check `%%rv-managed%%` markers in `system/templates/literature.md` — the markers are retired and the file does not exist) and `:131–139` (a ruff upgrade narrative; the current fact is "the skipped families sit in `ignore` as prefixes").

______________________________________________________________________

## B. Rewrite — current-state surfaces

Each row: what is there now → the current fact. Quotes are ≤120 characters; the audit's full tables are in this plan's commit history if needed.

### B1. `README.md`

- :3 "question → literature → synthesis → draft → submit" → the stage is compile into `wiki/`.
- :13–31 the claim-line section ("A claim line exists only after…", "Claims carry their own evidence", the claim-line grammar, `[[citation-key#^claim-id]]`, "Claims are deprecated, never deleted") → capture writes no claim lines and the checks that read them are frozen (CONTEXT.md:70). Rewrite the section around what the product does now: capture → `literatures/` + `fulltext/`; compile → `wiki/` through the adopted tool; verify's four-state checks; the review queue and acknowledgments. Keep "Four-state honesty" and the exit-code table.
- :15 "Admission is a human act" → selection is the person's decision, before capture (CONTEXT.md:36, :38).
- :66 the `human-reviewed` deferral with "spec §10.2" → either the one-line fact (no shipped surface mints the tier; #17) or nothing.
- :72 "a compilation, not a synthesis" → "not an arrangement" or drop the word.
- :76 `disputes` stance links → frozen; state only that `disputed-claim` is a reason code the linter can file.

### B2. `CONTEXT.md`

- :18 avoid-register rationale "(the layer moved under `wiki/`…)" → keep the avoid, drop the parenthetical.
- :24 "never an admission path" → "never a path by which a source becomes citable".
- :30 "There is no separate rename log." → delete (a negative about a retired artifact).
- :49 "citekey (… a field Better BibTeX no longer owns)" → "citekey (a Better BibTeX synonym)".
- :51 "A source's state after it was added" → "A source's state in the lifecycle linter's words".
- :70, :76 "frozen pending the workflow-component audit" → name the fact without the pending clause; the audit is defined only in the specs.
- :78 "The vault's former `authority` frontmatter field had no writer and is retired" → delete the sentence.
- :92 "Its pre-commit leg is held" → state the behaviour: the hook runs `verify --offline`; the lifecycle check reports UNREACHABLE offline and never blocks.

### B3. `AGENTS.md`, `ATTRIBUTION.md`

- AGENTS.md:12 `litrature/` → `literatures/`.
- AGENTS.md:16–18 `config/public-marketplace.json` "injected only inside the audited release artifact" → no `config/` directory exists and `.claude-plugin/marketplace.json` is tracked in this checkout; state the actual release mechanism or delete the paragraph.
- ATTRIBUTION.md:14–15 "the assembly spec's obligations index", :22 "lane 4's screening floors", :40 "screened in lane 2", :61–64 "lane 3 / lane 3a", :72 "ingest spec §3.8", :74 "currently misconfigured destructively on the author's machine — decomposition §15.16" → drop lane names and spec pointers; each entry says what was taken and what was not, nothing else. The :74 machine fact is undated and machine-specific: delete.

### B4. `docs/agents/*`, `docs/adr/0001`

- domain.md:11 `/grill-with-docs`, `/improve-codebase-architecture` → the skills that exist (`domain-modeling`, `grilling`).
- issue-tracker.md:26 `/triage` → delete the flag or name the mechanism that reads it.
- triage-labels.md:5 "Label in mattpocock/skills" column and :15 "Edit the right-hand column to match…" template boilerplate → the repo's own five labels, no upstream column.
- out-of-scope.md:51–53 fictional issue numbers in the example → keep as an example but mark it as one, or use placeholders.
- ADR 0001 violates domain.md:66 ("ADRs carry no history"): :14 "which was growing an ecosystem … at adoption", :17–19 and :86–87 (the same "amended in place" story twice), :21–22 "because the paraphrase is what drifted", :34 "A second exemption is recorded, 2026-09-07", :39–46 the rejected one-line patch and its 49-files-in-90-days measurement, :50–51 "The doctor's structure probes are gone", :82–85 the ADR narrating its own revision, :64/:66 `citekey` → state each decision once, present tense, without dates or the story of its revision; `citationKey`.

### B5. `docs/terminology.md`, `docs/testing.md`

- terminology.md:24 "including dated reports, transcripts, and plans" → the surfaces that will exist.
- :67 "Superseded 2026-09-07 by … which mints the second identity…" → the current cost only.
- :69 the screening-states row → delete (CONTEXT.md no longer defines them).
- :73, :102–104, :145–148, :163–164 pointers into `docs/superpowers/specs/…` and "was specified by the foundation specification, which the assembly design §2 demotes" → point at CONTEXT.md and the surviving spec by name; drop the demotion narrative.
- :76 "recorded pending an ADR 0002 reconciliation" → resolve or delete the note.
- :78 `fixity-sha256` → `managed-sha256`.
- :127 "`compile` is Part B's fourth" → "`compile` is the fourth, performed by the adopted tool".
- :136 `synthesis-conventions` in the governed skill names → whatever Part B Task 3 names the skill.
- :144–145 `managed-region` → keep as a check target-kind identifier (it is live in `quotes.py`, `events.py`); never as prose.
- testing.md:18 "the operator's", "(measured 2026-09-14: a mutant … died on the developer's machine and lived on the runner)" → "the person's"; drop the mutant story (the rule is the sentence before it).
- :20 "the wave", :30 "admission is a human act", :33 "one went stale for three weeks…", :45 "read the specs" → phase-free wording; "accepting a source is the person's act"; delete the anecdote; name where facts live (AGENTS.md: where they are used).
- :52 "(measured: ~1ms fail vs 5029ms for port 1)" → date it or delete it.

### B6. Skills (after Part B Task 3, which rewrites `synthesis-conventions`, `capture-source`, `setup-vault`, `evidence-conventions`)

- capture-source:40 "a later lane's work" → "out of scope for capture".
- evidence-conventions:14 "(§5)", :82 "(spec §7)", :93 "(spec §2)", :95 "(spec §7)" → drop the section pointers or name the spec; :82 "Admission is a human act" → selection; :111 "the single verified quote lives once, in the literature note" → reconcile with the fact that capture writes no claim lines (which of the two statements is current is Part B Task 3's to settle; whichever survives, README must agree).
- factcheck-draft:9, :32, :46 spec pointers → ADR 0002 / the implementation; :36, :39, :42, :56 "managed region" → "the note body".
- find-sources:9, :114 admission → selection; :15 undated "checked against this tree" → date it; :19–20, :23 upstream-generation narration and the K-Dense queue note → the current fact ("this fork vendors 11 reference files and 5 walkers; two environment variables nothing reads").
- project-flow:9, :54–56 synthesis → compile / `wiki/` pages; :48 "§7" → OKF §7.
- verify-citations:9 "the deterministic suite of §6" → name the checks.
- setup-vault:65 "the retired fixity-sha256 witness" → `managed-sha256` (with A5's migration section gone).

### B7. Templates, manifests, config comments, docstrings

- `research_vault/templates/vault/AGENTS.md:9` "admitted through Zotero" → "accepted into Zotero"; :11 "two model-invocable skills … `synthesis-conventions`" → whatever Part B Task 3 ships (`tests/test_templates.py:125–135` pins this sentence byte-for-byte; edit both).
- `research_vault/templates/git/pre-commit:4–5` "The lifecycle leg is held … ingest spec invariant 5" → the behaviour, no status word, no spec pointer.
- `.claude-plugin/plugin.json:3` and `marketplace.json:10` "per-claim provenance" → the live gates (capture provenance, four-state checks).
- `pyproject.toml:12–13, :25` "its lane", "dev-lane tool" → "the dev tooling"; :40, :79 "pending #70" → the reason, not the issue number.
- `quality.yml:110` "all 34 modules" → no count, or the count the gate prints; `mutation-baseline.txt:1` "every research_vault module measured" → `__init__.py` and `claims.py` have no rows; say "every module with a survivor" or confirm they measured clean.
- Module docstrings (26 of 35 modules): references of the form "spec §6", "ingest spec §3.3", "decision 08", "open point 12", "decomposition decision 17", "audit §1" → keep a pointer only where it names a surviving document by file and section; drop decision and open-point numbers (they belong to the spec's own register). `research_vault/__init__.py:1` is the one shipped path into `docs/superpowers/` — repoint at the surviving spec or drop. `verify.py:3–4` "Extracted from `__main__`" → "the public seam hooks and tests consume". `quotes.py:1` "managed literature-note quote claims" → the check's current subject.
- `tests/test_frontmatter.py:109` mentions `archive.py`, which does not exist.

______________________________________________________________________

## C. Rewrite — the specs

The three active specs are the largest source of history in the tree, by design: `2026-09-05-assembly-design.md:5` rules that "a decision reversed on a later day is recorded as a later decision naming what it supersedes, never as a rewrite of the earlier one." That rule is the opposite of the operator's principle and is retired by this sweep; each spec is rewritten to state its current decisions once, present tense, with dated measurements kept only where AGENTS.md's environment-fact rule wants them (method and date, where used).

### C1. `2026-08-16-foundation-spec.md`

- :3 `Disposition: pending-map`, :7 "Status: APPROVED … 2026-08-16" → one status line or none.
- §4 (Zotero bridge) → delete; the ingest spec supersedes it wholesale (its own :5 says so; §4 was never edited to say so).
- :166 vs :171 — the mutation gate is "closed 2026-09-14" five lines above text that still schedules the six-module exclusion list and a mutate4py re-baseline → one current paragraph: mutmut behind `scripts/mutation_gate.py`, the baseline file, the CI budget.
- `knowledge-harness` URLs (:8, :18, :23, :85, :104), the `synthesis/` root (:31, :43, :99), the managed/free region (:42), `screening-state` (:76), `citekey` (:42), the "Superseded 2026-08-30" bullet (:104), the Research footer (:184) pointing at deleted folders → current names or deletion.
- :55 and the ingest spec :493 define "the workflow-component audit" that CONTEXT.md:70/:76 and several checks are "frozen pending" → either schedule it (an issue) or state the frozen checks' status without a pending clause.

### C2. `2026-09-05-assembly-design.md`

- :3 "amended 2026-09-06 and 2026-09-07", :5 the never-rewrite rule → retire.
- :32, :415, :427 ADRs 0004/0005 "carry `Status: suspended`" → they were deleted; :80, :606 `docs/document-dispositions.tsv` "a reviewed artifact" → deleted at `7ec2c95`; §10 (:415–:444) specifies the `Disposition:` marker system → delete the section.
- :297, :305, :458 state lines and "Executed 2026-09-14" narration; §7.1.1 → lane 1 is done: one sentence, and the lane table shows lane 1 closed with what it shipped.
- :78 decision 15 supersedes `should-be-scoping-review` while :80 says the artifact carrying it is untouched → the artifact is gone; one sentence.
- §11 measured inputs "dated 2026-09-05, before lane 1" and the sidecar counts → re-measure at the audit (#43) or delete the numbers.
- §15 "Open items carried forward" → strike closed items outright (01, 06, 14, 20's red-run count, 23's narration); keep open ones as open items without their closure stories.
- Every "(decision NN)" back-reference is fine as long as decisions are numbered once and never "superseded by row".

### C3. `2026-09-06-import-redesign-design.md`

- :3, :5, :7 draft lineage ("amended from the 2026-09-04 draft", "nothing there was decided", "ADR 0004 and 0005 were deleted on 2026-09-07") → delete; the spec is the spec.
- :74 the term collision that "dissolved on 2026-09-07" → delete.
- §8 open points with strike-through and "Closed 2026-09-07" / "Built in Part A Task 18" → closed points disappear; open ones stay as open points.
- §9 fact register: keep, it is the one place dated measurements belong (method and date per fact); the csljson row keeps its 500 and its two 200s as dated facts, decision 13 stated once.
- :503 §6's frozen-checks paragraph and its 2026-09-16 amendment → one current statement of what each frozen check does now and who owns its retirement.
- :527 "Moved by Plan W" block → fold into §7 as the current testing facts (hermetic suite, the gate), no "moved by".
- Part A's "Decisions this plan settles (01–25)" and Part B's decisions → the ones still load-bearing move into this spec's decision list before the plans are deleted (A1); the code's "decision 08 / 13 / 28" docstrings then resolve here or are dropped (B7).
- Evidence siblings: see D1–D2.

______________________________________________________________________

## D. Decisions for the operator

1. **`2026-09-06-import-redesign-terminology-evidence.md`** — the ingest spec :28 and :74 make it the per-term traceability record behind CONTEXT.md's glossary. Keep as the one evidence file the glossary cites (header: "evidence for CONTEXT.md's glossary; binds nothing"), or fold each term's one-line source into the glossary itself and delete.
2. **`docs/research/2026-09-04-import-sourcing.md`** (5,843 lines) — the ingest spec §4.2/§4.3 draw candidate descriptions from it; the assembly spec :469 flags that it reproduces verbatim text from unlicensed repositories and carries absolute local paths. Recommended: delete after Part B merges; the spec's own §4.2–4.3 already carry the descriptions it needs. `2026-09-05-assembly-design-sourcing-screen-evidence.md` is the same shape for the assembly spec (cited at :78, :80, :606 as the exemplar screen): keep it as the one exemplar, or fold the exemplar into `docs/agents/sourcing.md`.
3. **`docs/research/2026-09-05-zotero-api-reading.md`** (4,501 lines, records 1–451) — the measured Zotero facts the ingest spec §9 and the assembly spec :522 cite by record number, and Part B's live legs cite by record. Recommended: after Part B merges, move each fact the code or a spec depends on into §9 with its method and date, then delete the reading; a record number is not an address a reader can follow once the file is gone.
4. **Upstream reports (#67)** — the drafts live in `docs/research/2026-08-23-mutmut-defect-reports.md` (two live shims cite it as their reason) and `2026-08-16-foundation-spec-mutate4py-defects-evidence.md`. File them, or close #67 as "will not file", before deleting the drafts. The shims' docstrings then state the defect in one sentence each instead of pointing at a file.
5. **`validation-slice/2026-08-22-case-study-question-bank.md`** — a queue of case-study questions, keyed to the retired find → admit → import → synthesize pipeline. Delete, or open one issue holding the questions still wanted.
6. **`skills/synthesis-conventions`** — Part B Task 3 rewrites it for the compiled layer. Whether the skill survives under that name or becomes `wiki/`'s conventions is Task 3's; terminology.md:136 and `templates/vault/AGENTS.md:11` follow.
7. **The specs' rewrite (section C)** is the one large job here: three documents, ~1,400 lines, rewritten as current decisions. It can be one plan, dispatched after A and B, with each spec's decision register as the deliverable and this file's C1–C3 as its brief.

______________________________________________________________________

## E. Mechanisms that keep it current (so the sweep does not recur as prose)

1. **No `Disposition:` line in tracked Markdown** — one assertion in `tests/test_config_validity.py` over `git ls-files '*.md'`. Today: 64 files would fail; after A, zero.
2. **No dangling repository path in tracked Markdown and in docstrings** — a test that extracts `docs/…`, `research_vault/…`, `skills/…`, `tests/…`, `.github/…` path literals from tracked `*.md` and `research_vault/*.py` and asserts each exists. Today it would catch `docs/research/harness-audits/dev-harness-analysis.md` (README), `config/public-marketplace.json` (AGENTS.md), `system/templates/synthesis.md` (synthesis-conventions), `system/templates/literature.md` (pyproject.toml), `docs/document-dispositions.tsv` (assembly spec), and every pointer into a folder section A deletes.
3. **No retired vocabulary in current-state surfaces** — `tests/test_skill_contracts.py` already scans skills for check ids; extend the same scan with a small deny-list (`synthesis/`, `admission`, `citekey:`, `fixity-sha256`, `knowledge-harness`, `managed region` as prose, `.harness`, `HARNESS_`) over README, CONTEXT, AGENTS, `docs/agents`, `docs/adr`, terminology, testing, the skills and the vault templates. The identifiers that legitimately survive (`managed-region` as a target kind, `not-admitted` as a reason code) are exact strings the scan can except by spelling.
4. **Plans and registers are deleted by their own Finish step** — Part B's Task 6 is the last plan written under the old convention; the SDD Finish convention in `AGENTS.md` ("Task reports") gains one clause: a merged plan's file and its register are deleted in the merge's next commit once every row has a home. The results file convention (a run report beside the spec) is retired with them: what a run changed is in the spec; what it measured is in §9-style fact registers with method and date.

______________________________________________________________________

## F. Issues to close at lane 1's close (the tracker mirrors the tree)

Closed when Part B merges, on the merge: #21 (fixed by Task 2b), #113 if the upstream post is made (else it stays `ready-for-human`).

Closed as obsolete by this sweep — their inputs are the records section A deletes, and their programme (the validation slice and its post-slice queue) ended when the ingest redesign replaced it:

- #41 (run the revised Plan S validation slice), #44 (choose the next post-slice architecture deepening), #45 (disposition the complete post-slice improvement queue; it natively blocks #32 — remove the edge or close), #71 (pre-slice formatter/linter audit; the form-owner matrix and Plan W's version currency answered it), #18 (post-slice adoptions from the History Notes comparison — its source document is deleted), #30 (act on the process-reconstruction note — deleted).
- #67 closes or proceeds per D4.

Kept, with their milestone as assigned: everything in `pre-lane-2`; #17, #23, #27, #49, #50, #52, #65, #94 (foundation enhancements, still true of the tree); #46, #38 (M2 — Reports); #117, #119 (the search and scoping-review specs); #103, #104, #115 (upstream filings).

Labels: delete the five `wayfinder:*` labels from `.github/labels.yml` and GitHub with A5's section.
