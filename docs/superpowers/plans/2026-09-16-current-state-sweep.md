# Current-state sweep at the close of lane 1 — the list

**Goal:** after Part B of the ingest redesign merges, nothing in the repository contradicts the implementation, and nothing describes a subject that no longer exists in any form. Records of what happened stay: a dated, true account is not a defect.

**Criterion (the operator's, 2026-09-16, narrowed the same day):** delete or update a file only if it asserts, as current, something the tree contradicts, or if its whole subject is gone. Being historical is not by itself a reason. Where a small edit removes the only contradiction, the edit is the action; where the contradiction runs through a document, the document is rewritten in place.

**Method:** two read-only surveys over main at b7a2573 — every record file under `docs/` and `.out-of-scope/` (104 files) classified, then re-classified under the narrowed criterion; every current-state surface (README, CONTEXT, AGENTS, ATTRIBUTION, `docs/agents`, `docs/adr`, terminology, testing, the skills, the templates, the plugin manifests, config comments, module docstrings) read for retired names, dangling paths and false statements. Every path and line below was verified against the tree on 2026-09-16; line numbers move with Part B's merge.

**Order:** after Part B merges. Pointers are repaired before the three files they point at are deleted.

**Executed 2026-09-16** (main through `aa75c42`): A, B, C2, C3 and E as listed, with the operator's amendments recorded under D; C1 became the retirement of the foundation specification itself. Section E's three mechanisms are `tests/test_current_state.py`.

______________________________________________________________________

## A. Delete — subject gone

Three files. Each documents a mechanism that no longer exists in any form.

1. `docs/superpowers/plans/2026-09-05-status-marking-pass.md` — the plan for the `Disposition:` marker system, deleted at `64b8c0b` with `docs/document-dispositions.tsv`. Its own header reads `Disposition: current (%(date)s)`, an unexpanded placeholder asserting currency for a system that is gone. Citers (historical, links go dangling): `docs/2026-08-31-proposed-adr-and-context-changes.md`, `docs/research/harness-audits/2026-08-30-installed-asset-disposition-survey.md` — see D2.
2. `docs/superpowers/specs/2026-08-16-foundation-spec-mutate4py-defects-evidence.md` — defect evidence for mutate4py, retired at `5e1e105`; the exclusion list it documents is closed and every module is baselined over mutmut. Before it goes: D1 (#67 holds its drafts). Citers to repoint: `2026-08-16-foundation-spec.md:171` (rewritten in C1 anyway), `2026-09-13-plan-w-quality-tail-results.md` ("Upstream reports queued"), issue #67.
3. `docs/superpowers/specs/2026-09-06-import-redesign-part-a-mutation-survivors.md` — a mutate4py run pinned to one sha; the survivor set was re-measured over mutmut into `mutation-baseline.txt`. Citer to repoint: `2026-09-06-import-redesign-part-a-results.md`.

Everything else surveyed stays: 95 files are true records (dated, framed as such), and their `Disposition: historical (2026-09-06)` headers are true statements.

______________________________________________________________________

## B. Update — a contradiction a small edit removes

### B1. Record files (three headers, two sentences, one URL)

- `docs/superpowers/plans/2026-09-13-plan-w-quality-tail.md:3` `Disposition: pending-issue: 42` — #42 is closed; drop the line.
- `docs/superpowers/specs/2026-08-16-foundation-spec.md:3` `Disposition: pending-map` — the map (#1) closed 2026-08-16; drop the line (the rest of the spec is C1).
- `docs/research/validation-slice/2026-08-22-case-study-question-bank.md:3` "research-vault runs end-to-end (find → admit → import → synthesize → verify → publish)" — present tense, and the tree runs capture → compile → verify → publish; add the file's missing `Disposition: historical` line or reword the sentence.
- `.out-of-scope/reason-code-callsite-ast-scan.md:28` links `eranroseman/knowledge-harness/issues/26` — the repository is `research-vault`; fix the URL.
- The `[should-be-scoping-review]` flag on 30 `historical` headers: a recommendation decision 15 of the assembly spec superseded, on headers that are otherwise true. Leave, or strip in one pass — D3.

### B2. Current-state surfaces — retired names, dangling paths, false statements

Only rows where the text asserts something the tree contradicts. True dated narration (a "Closed 2026-…" sentence, a measurement with method and date, a rationale) is not listed.

**Dangling paths (a reader hits a missing file today)**

- `README.md:117` links `docs/research/harness-audits/dev-harness-analysis.md`, deleted at `1f64d06`.
- `AGENTS.md:16–18` names `config/public-marketplace.json` (no `config/` directory) and says a contributor checkout "has no marketplace catalog" while `.claude-plugin/marketplace.json` is tracked; state the actual release mechanism.
- `skills/synthesis-conventions/SKILL.md:26` routes through `system/templates/synthesis.md` (does not exist) — Part B Task 3 rewrote this skill; confirm after merge.
- `pyproject.toml:37–39` instructs a check of `%%rv-managed%%` markers in `system/templates/literature.md`: the markers are retired and the file does not exist.
- `docs/superpowers/specs/2026-09-05-assembly-design.md:80, :606` treat `docs/document-dispositions.tsv` as a live artifact (C2).

**Retired names presented as current**

- `README.md:3` "question → literature → synthesis → draft → submit" (the stage is compile into `wiki/`); `:15` "Admission is a human act" (selection, before capture; admission is retired in CONTEXT.md); `:72` "not a synthesis"; `:76` `disputes` stance links described as live (frozen per CONTEXT.md:76); `:29` claim links `[[citation-key#^claim-id]]` described as live (frozen). `:19` "claims are written in project drafts — never in the machine-written literature note" contradicts `skills/evidence-conventions/SKILL.md:111` "the single verified quote lives once, in the literature note" — one of the two is current; settle which (Part B Task 3 touched the skill).
- `CONTEXT.md:24` "never an admission path" — retired term.
- `AGENTS.md:12` `litrature/` — the directory is `literatures/`.
- `docs/agents/terminology.md:69` the literature-screening-states row points at a CONTEXT.md section that no longer defines them; `:78` `fixity-sha256` (retired; `managed-sha256` is the witness); `:136` `synthesis-conventions` as a governed skill name — whatever Part B Task 3 ships; `:194–196` the stale-name list (`knowledge-harness`, `.harness/`, `HARNESS_*`, `hk-`) describes an "unfinished rename" that is finished.
- `docs/agents/testing.md:30` "admission is a human act".
- `docs/agents/triage-labels.md:5` a "mattpocock/skills" column and `:15` unedited template boilerplate. (`/grill-with-docs`, `/improve-codebase-architecture`, `/triage` and `/wayfinder` are user-invoked skills that exist; the survey could not see them. Not findings.)
- `docs/adr/0001:64, :66` `citekey` for the field the tree calls `citationKey`; `:34` records a "second exemption" — true, but check it against `research_vault/structure.py:37` (which cites "ADR 0001, second exemption") when editing.
- `ATTRIBUTION.md:74` "currently misconfigured destructively on the author's machine — decomposition §15.16": a machine-specific fact with no date or method, and no document named "decomposition"; `:14, :22, :40, :61–64, :72` lane numbers and spec pointers a reader cannot follow — point at the assembly spec by file name or drop.
- Skills: `capture-source:40` "a later lane's work"; `evidence-conventions:82` "Admission is a human act"; `factcheck-draft:36, :39, :42, :56` "managed region" (the region is retired; the whole note body is capture's); `find-sources:9, :114` admission; `project-flow:9, :54–56` synthesis stage and "synthesis claims"; `setup-vault:48–65` the `citekey:` migration section (a pre-release spelling; the design is greenfield — check `notes.rename_frontmatter_key` for other callers) and `:65` "the retired fixity-sha256 witness".
- `research_vault/templates/vault/AGENTS.md:9` "admitted through Zotero"; `:11` "two model-invocable skills … synthesis-conventions" — whatever Part B Task 3 ships (`tests/test_templates.py:125–135` pins the sentence byte-for-byte).
- `.claude-plugin/plugin.json:3`, `marketplace.json:10` "per-claim provenance" — the per-claim machinery is frozen; name the live gates.
- `research_vault/quotes.py:1` "managed literature-note quote claims"; `research_vault/claims.py:1` "§5 claim lines" — the parser is live, nothing writes them; say so.
- `tests/test_frontmatter.py:109` mentions `archive.py`, which does not exist.

**False counts and statements**

- `.github/workflows/quality.yml:110` "all 34 modules"; `mutation-baseline.txt:1` "every research_vault module measured" — `__init__.py` and `claims.py` have no rows: either they measured clean (say "every module with a survivor") or they are unmeasured (measure them).
- `.github/workflows/quality.yml:87–101` the CRAP deferral names `archive.py` and `check_metadata`, neither in the tree — Part B Task 4 replaced the block on the branch; confirm after merge.
- `docs/agents/domain.md:66–67` "ADRs carry no history" — a rule ADR 0001 breaks at `:17–19`/`:86–87` (the same amendment story twice) and `:82–85` (the ADR narrating its own revision). Either the rule or the ADR changes; the user's criterion favours leaving true narration, so the rule is the thing to soften ("no change logs") or the two duplicated paragraphs collapse to one.

______________________________________________________________________

## C. Update — the three active specs (contradictions that run through the document)

Each spec stays; its dated amendments and superseding rows are true records and stay too. What changes is every sentence that asserts, as current, something the tree contradicts.

### C1. `2026-08-16-foundation-spec.md`

- `:5` "the project's current contract" while `:8, :18, :23, :85, :104` name `knowledge-harness`, `:31, :43, :99` the `synthesis/` root, `:42` the managed/free region and `citekey`, `:76` `screening-state` — retired; each becomes the current name or a dated past-tense sentence.
- §4 (Zotero bridge) is superseded by the ingest spec (`2026-09-06-import-redesign-design.md:5` says so; §4 does not) — one line at §4's head naming the successor.
- `:166` ("closed 2026-09-14: all 34 modules baselined") against `:171` (still schedules the six-module exclusion list and a mutate4py re-baseline) — `:171` becomes past tense or goes.
- `:184` the Research footer points at the folders that stay; no change unless A's three files are named there.

### C2. `2026-09-05-assembly-design.md`

- `:32, :415, :427` "ADRs 0004 and 0005 carry `Status: suspended`" — deleted at `b3ed645`; `docs/adr/` holds 0001–0003.
- `:80, :606` `docs/document-dispositions.tsv` "a reviewed artifact" — deleted at `64b8c0b`; `:78` (decision 15) against `:80` ("the artifact is untouched") — one sentence: the artifact is gone.
- §10 (`:415–:444`) specifies the `Disposition:` marker grammar, its `pending-issue:` value and its linter — the system is deleted; the section becomes one dated sentence recording that it ran and was removed, or goes.
- §15 items that are closed but still listed as open items (01, 06, 14) — strike or mark closed; the rest stay as written.

### C3. `2026-09-06-import-redesign-design.md`

- `:7` "ADR 0001, 0002 and 0003 carry `Status: accepted` with `Disposition: current`" — no ADR carries the marker; drop the clause.
- Nothing else contradicts the tree: `:74` (a collision that "dissolved") and `:527` ("Moved by Plan W") are true dated records and stay.

______________________________________________________________________

## D. Decisions for the operator

Decided 2026-09-16: 1 — #67 closed wontfix, the mutate4py file goes; 2 — moot, no record links the plan (the survey's claim was wrong; `grep -rn status-marking-pass docs` finds only the plan itself); 3 — leave the flag; 4 — the skill wins, README:19 reworded; 5 — per ticket: #41, #44, #45, #71 closed as dissolved or answered, #18, #30, #46 kept. Also decided: the vault directory is `literature/` (#142).

1. **#67 and the mutate4py drafts** — A2 deletes the file holding four of the queued upstream reports. File them, move the drafts to the issue, or close #67 as "will not file" first. (The mutmut drafts stay: `docs/research/2026-08-23-mutmut-defect-reports.md` is about the current tool and two live shims cite it.)
2. **Dangling links inside historical records** — two 2026-08 records link the deleted status-marking plan; after A, the links 404. Accept it in dated records, or repair the two links (a one-line edit each).
3. **The `[should-be-scoping-review]` flag** on 30 `historical` headers — a retired recommendation on otherwise-true headers. Leave as is, or strip in one pass.
4. **README's claim section versus `evidence-conventions:111`** — which statement is current: claims live in drafts only (README:19), or a verified quote lives once in the literature note (the skill)? One wins; the other is edited.
5. **The pre-redesign programme tickets** (#41, #44, #45, #46, #18, #30, #71) — no longer closable on "inputs deleted"; their records stay. Close only those whose question the ingest redesign answered or dissolved, one comment each; #45 natively blocks #32.

______________________________________________________________________

## E. Mechanisms that keep it this way

1. **No dangling repository path** — a test that extracts `docs/…`, `research_vault/…`, `skills/…`, `tests/…`, `.github/…`, `system/…`, `config/…` path literals from tracked `*.md`, `*.py`, `*.toml` and `*.json` under the current-state surfaces and asserts each exists. Today it catches README:117, AGENTS.md:17, synthesis-conventions:26, pyproject.toml:39, assembly-design:80/:606. Historical records under `docs/research/**` and `docs/product-landscape/**` are out of its scope (their links are dated); the specs are in it.
2. **No retired vocabulary on current-state surfaces** — `tests/test_skill_contracts.py` already scans skills for check-id spellings; the same shape with a deny-list (`synthesis/`, `admission`, `citekey:`, `fixity-sha256`, `knowledge-harness`, `.harness`, `HARNESS_`, `managed region` as prose) over README, CONTEXT, AGENTS, `docs/agents`, `docs/adr`, terminology, testing, the skills, the vault templates and the plugin manifests. Exact identifiers that legitimately survive (`managed-region` as a target kind, `not-admitted` as a reason code) are excepted by spelling.
3. **`Disposition:` values are `historical` or `superseded-by` only** — the `pending-*` and `current` values named a workflow that is gone; a one-line assertion over tracked Markdown keeps a false pending marker from reappearing.

______________________________________________________________________

## F. Issues at lane 1's close

- Closed on Part B's merge: #21 (Task 2b); #113 if the upstream post is made in Task 6, else it stays `ready-for-human`.
- The `pre-lane-2` milestone holds the follow-ups; nothing else closes on the strength of this sweep (D5 decides the programme tickets one by one).
