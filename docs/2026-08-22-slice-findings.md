# Validation slice — findings log

Plan: docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md. Vault: ~/kh-vault → github.com/eranroseman/kv-vault. Friction is the product: every entry names what the harness did short of its prose.

## Phase 0

1. **scaffold inherits the system default branch** — created `master`; the first push to a `main`-expecting remote failed (`src refspec main does not match any`) and needed a hand rename. Fix class: scaffold sets `--initial-branch=main` (or documents the assumption). → setup-vault fix, post-Q batch candidate.
2. `doctor`'s autoexport guidance printed the exact Windows-side target via wslpath translation — the human step is copy-pasteable from the probe output. (Positive finding; the repair-guidance design working.)
3. `machine-config` probe accepted the minimal `.harness/machine.json` (mailto + empty path_map) on first try.

## Phase 0 — CLOSED (2026-08-22)

4. **Key regeneration executed pre-export** (author-ruled window): formula `authEtal2.lower + year | shorttitle.lower + year`; periods survive BBT sanitization (`abbasian.etal2024` verified); disambiguation postfixes working. 1,407 items exported (2.2 MB sorted CSL JSON).
5. **Formula finding — SUPERSEDED same day by the author's push-back**: the fallback failure was mechanically fixable, and my admission-side "fix" was a rule where a mechanism existed. Root cause (documented, mis-searched twice): patterns never fail on emptiness — only explicit filters fail them; `.len` is the guard ("if the length of the output does not match, skip to the next pattern"). A data-patch script (org-as-creator for 60 repo items) was applied, then UNDONE at the author's direction (fixes existing items, not future ones; also surfaced a Zotero API asymmetry — setCreators accepts `name`, getCreators returns `lastName`). Final formula: `authEtal2.lower.len + year | shorttitle.lower + year` — verified: 0 bare-year keys in 1,407; `.etal`/two-author period keys intact. Residue: 2 metadata-dirt keys fixed per-item by the author (a social-handle creator; one 122-char institutional name → the one legitimate manual pin).
6. **autoexport MATCHED, staleness MATCHED** on first doctor run after the human step; the on-demand comparison export byte-matches. The wizard-form walkthrough prose was sufficient — no missteps.
7. **24 `HARNESS_LIVE_AUTOEXPORT_VAULT`-gated tests pass** on first run (the gated family was larger than the 2 headline skips).

## Open items

- `backup` warn: author's one-line Zotero storage backup statement still owed.
- memoria citekey sweep (author's other system) after the regeneration — author-owned, priced at ruling time.

## Original Phase 0 open items (retained as written)

- Human BBT step (target in doctor output above) → flips `autoexport` + `staleness`, unlocks the two `HARNESS_LIVE_AUTOEXPORT_VAULT` tests.
- `backup` warn: needs the author's one-line statement of the Zotero storage backup story (sync? disk image?) — recorded wherever doctor reads it.

## Phase 1

8. **Doctrine finding — the rubber-stamp rule (ruled into spec §3)**: the seed corpus's 170-URL admission exposed a gate-design gap: per-item human confirmation over a pre-curated list is ceremony that trains click-through (Shipman/Marshall's forced-formality failure, generalized). Ruled: human gates only where judgment differs per instance; bulk admission of a reviewed list = one recorded approval + Zotero's consented local-write dialog + provenance record. The slice caught exactly the class of question §9 exists to surface.

9. **Seed admission executed (2026-08-22)**: author approved the worklist (sha256:583cee263a374186) as the admission decision per the rubber-stamp rule. Route: local-API write BLOCKED by the §2 version gate (Zotero 9 lacks Zotero-Server-ID; pyzotero failed cleanly — feature-detection doctrine fired as designed); CSL JSON import REJECTED (not a Zotero import format — recorded); **RIS import succeeded**: 166 items into collection "knowledge harness" (3 DOI-grade articles, 48 repos with org creators, 115 webpages; 14 title-fetch gaps recorded). Post-import: 1,575 in bibliography, 0 bare-year keys — the .len formula held on live author-less imports. Author's Linter plugin served as the post-batch review (2 title-level dupes caught that URL-dedupe missed; 3 preprint type fixes; ~110 creator warnings deferred to enrichment-on-citation).

10. **Batch classifier defect (author's review caught it)**: the repo regex typed 17 GitHub deep-path URLs (`/issues/`, `/blob/`, `/discussions/`, `/tree/`, `/releases/`) as computerProgram with org creators — they are forum posts and web pages. Hand-fixed per item by the author (real per-item judgment — the gate rule's legitimate form). Lesson for any future batch admission tooling: repo-classification must exclude deep paths; only `github.com/<org>/<repo>` roots are software.

11. **Doctrine finding — library-as-search-space (author push-back, ruled 2026-08-22)**: "membership is free" was wrong the same way pre-purge AGENTS.md was wrong — the cost is retrieval, not storage. The Zotero library is a first-class discovery surface (gap analysis, find-sources inLibrary checks, registry-first dedup all search it); noise there pollutes judgment in every future project. RULED: the library holds what a scholar's search should surface; the seed's tool-docs/forum/repo class stays OUT (the author's bulk deletion stands). **Seed migration moves to just-in-time admission**: a migrating record's citations batch-admit at migration time, scoped to that note, from the classification ledger via the reusable RIS pipeline. Admission happens when something becomes citable-in-practice — never before. (The batch pipeline built this session is what made this ruling cheap.)

13. **Phase 2 pre-staged (2026-08-22)**: validation question selected — re-ask `trust-gates-prior-art` under the harness (baseline: research/trust-gates-prior-art.md). Backup warn closed: `zotero_backup` = Zotero sync, doctor fully green (zero UNMATCHED). Author emptying trash on the pruned 166 (ledger preserves provenance); memoria sweep and upstream filings acknowledged on the author's schedule.

12. **Ruling 11 amended same day (author push-back, second round)**: just-in-time admission from the ledger would copy the workshop's sourcing practice forward — citations fit for engineering-genre research (maintainer threads as primary evidence on tool behavior) entering scholarly trust machinery unre-judged. AMENDED: the ledger is a CANDIDATE list, not a manifest. Migration re-authors each record under evidence-conventions; every claim faces vault-grade sourcing judgment (upgrade the source / re-tag honestly with boundary + confidence / demote to open-question / drop); admission happens only for citations that survive. Meta-finding, recorded deliberately: the harness's own founding research would not pass the harness's gates unmodified — the falsifiability standard functioning, first bite at migration.
