# Plan S: Validation Slice — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (this plan is largely author-in-the-loop research work, not fresh-subagent tasks). Steps use `- [ ]`.
> This plan validates the harness by USING it. It runs the shipped skills against a real corpus in a fresh vault — the falsification test of spec §9. It is not a build; almost nothing here is code.

**Goal:** One trip around the project flow (§9) over two corpora plus the synthetic gate drill, ending in an author judgment: is the brief defensible and did the vault carry the work without being routed around?

**Setup dependency:** the vault is a SEPARATE git repository (spec §2), so this plan touches no file the plugin repo's Plan Q owns — it runs in parallel. The one human-only step (BBT auto-export creation) is front-loaded so its latency overlaps Plan Q.

**Authority:** spec §9 verbatim (phases, validated-when, falsified-when); the shipped skills are the instrument under test — where a skill's behavior diverges from what the slice needs, that is a FINDING about the skill, recorded, not worked around (routing around the vault is the §9 falsification condition).

## Global Constraints

- The vault lives at a path OUTSIDE this repo (e.g. `~/kh-vault`); it gets its own `git init` via `setup-vault`. Nothing from the slice is committed into the plugin repo except this plan and the findings log.
- **Findings are the product as much as the brief.** Every point of friction, every skill that under-delivers, every drill result → `docs/2026-08-22-slice-findings.md` (in the plugin repo — it is a record about the harness). A slice that ships a brief but hides friction has failed its purpose.
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

## Phase 1 — Seed migration (the information flow at volume)

- [ ] Admit this repo's research corpus into Zotero: the web sources under `research/` (~40 cited URLs), the `sources/` PDFs. **This is the corpus-to-vault migration the release gate names** — PDFs go to Zotero storage (§2 boundary), not the vault.
- [ ] `import-source` in batch mode over the admitted set → literature notes, index, log; live hold policy exercised on the one known live contradiction.
- [ ] Validated-when check: seed migration lands with **zero unresolved links**. Record every hold and its reason code.

## Phase 2–3 — Framing, gap analysis, acquisition

- [ ] `project-flow` start: frame the validation question — *how much are retracted papers cited after retraction, and do retraction-notification tools measurably reduce it?* — stating question / scope / source types / success criteria.
- [ ] Gap analysis vs the seeded synthesis layer + bibliography → gap list.
- [ ] `find-sources` (project-scoped, PRISMA-S log) → candidates → **author admits 15–25 papers** into Zotero → `import-source` with integrate-at-import.

## Phase 4–6 — Draft, verify, publish

- [ ] Draft a 1,000–2,000-word evidence brief in `projects/` under the Iron Law (via evidence-conventions); ~10 synthesis pages touched.
- [ ] `verify-citations` + `factcheck-draft` → adjudicated findings; the recorded skipped set is real here.
- [ ] `publish` → the gate; author chooses the disposition.

## Synthetic gate drill (decoupled — a scratch project, not the research)

- [ ] Plant all seven, run the gate, confirm each is caught: fabricated citekey; mutated quote; unacknowledged retracted citation; simulated API outage (publish must WAIT, not pass); killed auto-export (staleness lint fires); a DOI-less retracted paper (identifier discovery + PMID matching catches it); a DataCite-DOI item (registry routing must not read it clean).
- [ ] Any planted error surviving to publish = §9 falsification. Record each drill's result verbatim.

## Judgment

- [ ] **Validated-when (§9)**: 100% of brief claims resolve mechanically per their tag; `verified` events recorded + trust tier derivable in a Base; all five/seven drills caught; seed migration zero-unresolved; cold-resume worked; **the author judges the brief defensible.**
- [ ] **Falsified-when**: any planted error reaches publish, OR the author routed around the vault. Either falsifies the foundation — record it as such, do not soften it.
- [ ] Findings log committed to the plugin repo; the vault repo stands on its own.

## Self-Review (at authoring)

- This is the plan that can fail the whole foundation — its value is honest findings, not a clean run. The falsified-when clause is load-bearing; an executor who smooths over friction to reach a brief has inverted the plan.
- Parallel-to-Q is real: separate repo, no shared files. The only shared resource is live Zotero (both want it running) — not a conflict.
- The BBT step is the one thing only the human can do; it is Phase 0 so it never blocks a later phase.
- Slice findings feed the deepening pass (real friction is its evidence) and may reopen deferred-register items with their named triggers (independence key on same-lab duplication; plan-hash handshake on consent friction).
