# Plan S: Validation Slice — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (this plan is largely author-in-the-loop research work, not fresh-subagent tasks). Steps use `- [ ]`.
> This plan validates the harness by USING it. It runs the shipped skills against a real corpus in a fresh vault — the falsification test of spec §9. It is not a build; almost nothing here is code.

**Goal:** One trip around the project flow (§9) over two corpora plus the synthetic gate drill, ending in an author judgment: is the brief defensible and did the vault carry the work without being routed around?

**Setup dependency:** the vault is a SEPARATE git repository (spec §2). **Sequencing (ruled 2026-08-22): Phases 2+ wait for the pre-slice batch to merge** — instrument freeze (the project-flow rename, defect fixes, and the vault index land first; running on a mid-rename skill set would pollute the resume test and re-find catalogued defects). Phases 0–1 ran parallel to Plan Q and are closed.

**Second sequencing gate (ruled 2026-08-22, after the no-fabrication audit — research/validation-slice/2026-08-22-no-fabrication-audit.md; CONSOLIDATED same day: the remediation was absorbed into the combined pre-slice plan as Part 2, so BOTH gates are satisfied by that single plan's merge — Phases 2–6 and the drill unblock together): Phases 4–6 and the synthetic gate drill wait for trust-core remediation** (audit defects 1–5 — inert RW leg, UNMATCHED→MATCHED reduction, vacuous machine-confirmed tier, unenforced tier-2 citability, free-region destruction — plus the "unresolved"-placeholder and archive-url fixes). Same logic as the instrument freeze: the verify/publish gates ARE the instrument for those phases. Running them un-remediated fails both ways — the retraction drills would fail with a catalogued cause (a false "falsified"), and validated-when could pass on fabricated trust tiers and un-caught cross-project citekeys (a false validation, which is worse). Phases 2–3 do NOT wait on remediation — framing, gap analysis, find-sources, and import don't run the defective gates — except the notes.py:151 free-region destruction fix, pulled into the pre-slice batch because authored digests live in exactly the region a marker-mangled refresh silently destroys.

**Authority:** spec §9 verbatim (phases, validated-when, falsified-when); the shipped skills are the instrument under test — where a skill's behavior diverges from what the slice needs, that is a FINDING about the skill, recorded, not worked around (routing around the vault is the §9 falsification condition).

## Global Constraints

- The vault lives at a path OUTSIDE this repo (e.g. `~/kh-vault`); it gets its own `git init` via `setup-vault`. Nothing from the slice is committed into the plugin repo except this plan and the findings log.
- **Findings are the product as much as the brief.** Every point of friction, every skill that under-delivers, every drill result → `research/validation-slice/2026-08-22-slice-findings.md` (in the plugin repo — it is a record about the harness). A slice that ships a brief but hides friction has failed its purpose.
- Minimum two sessions with a real cold resume between them (§9 — exercises orientation and inbox-drain for real).
- Live throughout: Zotero running, `HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>`.
- The author performs every admission (human act) and every disposition (human-chosen); the agent orchestrates.

## Phase 0 — Scaffold + the human BBT step (front-loaded, parallel to Plan Q)

- [ ] `python -m knowledge_harness scaffold ~/kh-vault` (or the `setup-vault` skill) → fresh vault tree, `git init`, templates, Bases, vault AGENTS.md, glossary seed.
- [ ] **Human step (BBT Preferences — the wizard-form guide, delivered as prose here; the polish pass will formalize it):**
  1. Zotero → Edit → Preferences → Better BibTeX → Automatic export.
  2. File → Export Library → format **Better CSL JSON**, check **Keep updated**, target `~/kh-vault/system/bibliography.json`.
  3. Confirm the export appears under BBT's auto-export list and the file exists.
- [ ] `python -m knowledge_harness doctor ~/kh-vault` → every probe reported; autoexport MATCHED (this is the step that unblocks the two `HARNESS_LIVE_AUTOEXPORT_VAULT`-gated tests — set that env var to `~/kh-vault` and confirm they now run, not skip).
- [ ] Record in findings: did scaffold + the human step match the prose? Every gap is a setup-vault finding.

## Phase 1 — Seed migration (AMENDED 2026-08-22 — just-in-time admission per the library-as-search-space ruling; see findings log 11)

Seed admission is no longer up-front: the library holds scholarly sources only. The classification ledger is a CANDIDATE list, not a manifest (findings 11–12): migration re-authors each record under evidence-conventions, every claim faces vault-grade sourcing judgment, and only surviving citations admit (RIS pipeline, scoped per note). The three `sources/` PDFs admit now (scholarly; the author kept them). Phase 1's zero-unresolved-links criterion is evaluated per migrated note.

### Original phase text (superseded)

- [ ] Admit this repo's research corpus into Zotero: the web sources under `research/` (~40 cited URLs), the `sources/` PDFs. **This is the corpus-to-vault migration the release gate names** — PDFs go to Zotero storage (§2 boundary), not the vault.
- [ ] `import-source` in batch mode over the admitted set → literature notes, index, log; live hold policy exercised on the one known live contradiction.
- [ ] Validated-when check: seed migration lands with **zero unresolved links**. Record every hold and its reason code.

## Phase 2–3 — Framing, gap analysis, acquisition

- [x] **Question selected (2026-08-22): `trust-gates-prior-art`** — the most decision-relevant workshop question, re-asked under the harness; `research/prior-art/trust-gates-prior-art.md` is the loose-process baseline. Then `project-flow` start: frame it — question / scope / source types / success criteria — knowing the original loose-process answer exists as the baseline; the deliverable is the rigorous re-answer plus the delta.
- [ ] Gap analysis vs the seeded synthesis layer + bibliography → gap list.
- [ ] **Pre-registered pilot (2026-08-24, window not yet open): sampling-consistency on digests.** A handful of Phase 3 digests generate at N=3 in isolated contexts; the claim-disagreement rate is recorded as data. Decides whether SelfCheckGPT-style consistency checking becomes standing (its 2–3× generation cost is unpriced until this base rate exists — adopting by default would invent the cost-benefit number).
- [ ] `find-sources` (project-scoped, PRISMA-S log) → candidates → **author admits 15–25 papers** into Zotero → `import-source` with integrate-at-import.

## Phase 4–6 — Draft, verify, publish

- [ ] Draft a 1,000–2,000-word evidence brief in `projects/` under the Iron Law (via evidence-conventions); ~10 synthesis pages touched.
- [ ] `verify-citations` + `factcheck-draft` → adjudicated findings; the recorded skipped set is real here.
- [ ] `publish` → the gate; author chooses the disposition.

## Synthetic gate drill (decoupled — a scratch project, not the research)

- [ ] Plant all seven, run the gate, confirm each is caught: fabricated citekey; mutated quote; unacknowledged retracted citation; simulated API outage (publish must WAIT, not pass); killed auto-export (staleness lint fires); a DOI-less retracted paper (identifier discovery + PMID matching catches it); a DataCite-DOI item (registry routing must not read it clean).
- [ ] **Leg attribution (amended 2026-08-22): every retraction plant records WHICH leg caught it, and the drill runs with the RW leg armed** (`--rw-csv` supplied, matching the CI lane it ships in — the flag has no default and nothing in the shipped local surface passes it, so an unarmed drill leaves the RW leg untested by the drill designed to test it). The DOI-less plant's trap: identifier discovery may find the DOI and hand the catch to Crossref — a real catch, but not the PMID/RW path the plant exists to exercise; expected attribution for that plant is the RW/PMID leg, and a Crossref-attributed catch means the RW leg still has no evidence. Under the remediated-gates rule, "caught, but by the wrong leg with the target leg unexercised" is recorded as exactly that, never rounded to a pass of the leg.
- [ ] **Corpus upgrade (amended 2026-08-22): plant from HALLMARK, not only by hand.** A stratified sample across its 14 hallucination types and three difficulty tiers replaces hand-picked citation-content plants (hand-chosen errors test gates against errors we already knew they'd catch); the seven original plants are RETAINED for what HALLMARK cannot cover (outage, killed auto-export, DataCite routing — infrastructure drills, not citation content). **Precision arm**: a sample of HALLMARK's 826 valid entries planted alongside, false flags counted — the drill gains true negatives, yielding the §9 measured inbox-precision/FPR number as a by-product, and directly instrumenting the falsified-when clause's other half (a high false-positive rate is what causes routing around the vault). Corpus, not code — safe under both freezes. Adaptation of entries into vault claim shape is drill-scratch-project work, sized at drill time.
- [ ] Any planted error surviving to publish = §9 falsification. Record each drill's result verbatim.

## Judgment

**Pre-registered decision rules (2026-08-22): docs/superpowers/plans/2026-08-22-slice-decision-rules.md** — the two self-assessment clauses below are evaluated through them (`routed-around-tagging` makes the falsification clause countable at occurrence; `inbox-review-sizing` measures the rubber-stamp precursor; `defensibility-floor` anchors the author's judgment to the mechanical criteria). The registry closed to amendment when Phase 2 started.

- [ ] **Validated-when (§9)**: 100% of brief claims resolve mechanically per their tag; `verified` events recorded + trust tier derivable in a Base; all five/seven drills caught; seed migration zero-unresolved; cold-resume worked; **the author judges the brief defensible.** **Criteria are evaluated against remediated gates (ruled 2026-08-22)** — the no-fabrication audit (research/validation-slice/2026-08-22-no-fabrication-audit.md) is the reference; a criterion passing through a gate the audit lists as defective is not a pass.
- [ ] **Falsified-when**: any planted error reaches publish, OR the author routed around the vault. Either falsifies the foundation — record it as such, do not soften it.
- [ ] Findings log committed to the plugin repo; the vault repo stands on its own.

## Pre-registered friction → adoption map (ruled 2026-08-22)

No third-party skill or module is adopted during the slice — the shipped nine are the instrument, and for two candidates earlier called urgent the gap IS the measurement: the two-session minimum exists to test the continuity machinery (inbox drain, project start/resume, orientation-first), and Phase 4's no-drafting-skill brief tests whether evidence-conventions + project-flow carry drafting. Adopting either mid-slice validates something else.

After the slice, adoption is friction-selected through the existing channel (findings → deepening pass), pre-registered here so interpretation is disciplined, not biased:

| Friction the slice would surface                                   | Candidate it selects                                              |
| ------------------------------------------------------------------ | ----------------------------------------------------------------- |
| Orientation breaking down across ~10 synthesis pages (Phases 2, 4) | claude-obsidian wiki-retrieve/wiki-query, or obra/knowledge-graph |
| Drafting friction in Phase 4                                       | K-Dense scientific-writing                                        |
| Cold resume genuinely failing at Phase 4→5                         | the pedrohcgs continuity cluster (now properly conditional)       |
| Log or index scale in a two-session run                            | claude-obsidian wiki-fold                                         |
| Search coverage gaps in Phase 3                                    | cookjohn cnki-skills, gs-skills                                   |
| Submission friction in Phase 6                                     | medsci sync-submission                                            |

No friction observed = no adoption; the map never becomes a shopping list. The same discipline covers the Memoria-item pool (2026-08-22): per-finding severity ← whether the run produces findings of visibly different weight; the no-refutation finding kind ← Phase 4's brief (where a claim with no counter-evidence considered would first appear); propagation's consequence walk ← whether ~10 synthesis pages generate cross-claim consequences; the capability contract and integrity/argument-quality ops ← post-slice by necessity (they change skill frontmatter, the system under test); code grounds ← parked until analysis work exists. The ledger discipline itself converged independently (the findings log's "friction is the product" IS Memoria's shape) — nothing to take there. **gap-to-topic is excluded from the map and decided on merits (ruled 2026-08-22): not adopted** — it gates whether a question is worth asking, the slice's question is already chosen, so no slice evidence can bear on it; and question-selection sits upstream of the harness boundary (the harness begins at framing a chosen question, spec §7). An upstream workflow choice, not a harness gap — this also resolves its two-tier contradiction in the adoption plan (review cluster 6).

## Self-Review (at authoring)

- This is the plan that can fail the whole foundation — its value is honest findings, not a clean run. The falsified-when clause is load-bearing; an executor who smooths over friction to reach a brief has inverted the plan.
- Parallel-to-Q is real: separate repo, no shared files. The only shared resource is live Zotero (both want it running) — not a conflict.
- The BBT step is the one thing only the human can do; it is Phase 0 so it never blocks a later phase.
- Slice findings feed the deepening pass (real friction is its evidence) and may reopen deferred-register items with their named triggers (independence key on same-lab duplication; plan-hash handshake on consent friction).
