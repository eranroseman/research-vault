# Product comparison: knowledge-harness vs comparable products

Comparison note, 2026-08-22.

## How to read this

Five parts. **Part I** states how the evidence was gathered and measures our own side, so every
later claim has a baseline. **Part II** is the field: every comparable product, tiered by whether
it could replace the harness, replace one component, or only inform its design. **Part III** is
the comparison proper — skill by skill, then what we lack, then what only we have, then the
differences as one table. **Part IV** is the record: corrections this pass forced on this
repository's earlier notes, and what was deliberately left out. **Part V** is a positioning
judgment built on all of it, ending in a candidate-by-candidate vendoring list. Parts I–IV are
evidence; Part V is inference, except section 18, whose licence and dependency facts were checked
in the artifacts.

---

# Part I — Frame

## 1. Method and evidence rule

The roster began with the products named in `research/prior-art-knowledge-work-harness.md` and
`research/llm-wiki-integration-prior-art.md` — **names and URLs only**. Four things extended it:
30 GitHub searches across academic skills, LLM-wiki implementations, citation verification, Zotero
bridges, systematic-review automation and second-brain harnesses; two skill frameworks the user
named; the external tooling and standards this repository's own `research/` and `analysis/` notes
cite; and the two repositories those notes left unread.

No mechanism claim, capability claim, star count, license or verdict was carried over from any
note in this repository on that note's authority. Every fact below was re-derived on 2026-08-22
from one of three sources:

- the GitHub REST API, for existence, stars, license and last push;
- a clone of the repository, read directly — where a mechanism is asserted, the file that
  implements or specifies it is named, and where a line number is given, it was read;
- the primary specification or API, for standards and property identifiers.

Our own side was read from this repository's source only: `knowledge_harness/`, `skills/`,
`tests/`, `hooks/`, `.claude-plugin/` and root files.

Where a claim could not be traced to something actually read, it was cut rather than softened.

## 2. Read depth

**Read at file level** (cloned, files opened): Imbad0202/academic-research-skills,
Aperivue/medsci-skills, garrytan/gbrain, AgriciDaniel/claude-obsidian,
atomicstrata/llm-wiki-compiler, swarmclawai/swarmvault, SamurAIGPT/llm-wiki-agent,
pedrohcgs/claude-code-my-workflow, NousResearch/hermes-agent (both `llm-wiki` and
`grounded-citations`), nvk/llm-wiki, Pratiyush/llm-wiki, K-Dense-AI/scientific-agent-skills (at
the pinned SHA `336c4f8`), kepano/obsidian-skills, 54yyyu/zotero-mcp, obra/superpowers,
mattpocock/skills, Karpathy's gist, Hylouis233/bibverify, PHY041/claude-skill-citation-checker,
tfscharff/doi-mcp, htlin222/research-guardian-skill, htlin222/prisma-automation,
917Dhj/DeepPaperNote, Astro-Han/karpathy-llm-wiki, trapoom555/claude-paperloom,
introfini/ZotSeek, skyllwt/AutoSci, delibae/claude-prism,
PiaoyangGuohai1/cli-anything-zotero, huytieu/COG-second-brain, obra/knowledge-graph,
rpatrik96/hallmark, Agents365-ai/asta-skill, PouriaRouzrokh/LatteReview,
kytmanov/obsidian-llm-wiki-local, WenyuChiou/research-hub,
Orchestra-Research/AI-Research-SKILLs (top-level listing only). medsci-skills and research-hub
were additionally surveyed skill-by-skill on 2026-08-22 (§6.1, §6.15).

**Read at module-layout level** (structure inspected, bodies not read): Future-House/paper-qa,
stanford-oval/storm, assafelovic/gpt-researcher.

**Metadata level only** (stars, license, push date and the project's own description): every
other row. Where such a row states a capability, that is the project's claim, not a verified
mechanism, and it is marked as such in place.

**Verified at primary source rather than in a repository**: the W3C Web Annotation Data Model
spec text, Wikidata property labels via the Wikidata API, the micropublications paper via
Crossref, the OKF specification repository, and `lychee-action`'s `action.yml` on master.

## 3. Limits

Elicit, scite and llmwikis.org have no inspectable repository and are listed without comparison.
No product was read exhaustively; reading was targeted at the axes in Part III. Capability lists
drawn from a product's own skill file or README describe what it claims to do, not measured
behaviour. Star counts are a distribution signal, not a quality signal. Three claims found in this
repository's notes were **not** re-verifiable in this pass and are therefore absent: pandoc's
undocumented missing-citekey rendering, Quarto's warning propagation, and JATS4R's severity
taxonomy. Our own side was measured from source, so its numbers are exact.

## 4. Our side, measured

| Dimension | Value |
|---|---|
| Deterministic core | 26 Python modules, 9,716 lines, zero runtime dependencies (`pypdf` is an optional `pdf` extra) |
| Tests | 1,330 collected; markers for `live` (running Zotero) and `live_net` (real APIs) |
| Skills | 9 — 7 user-invoked (`disable-model-invocation: true`), 2 model-invocable |
| Hooks | 2 — PostToolUse lint (warn-only, fail-open, never interrupts); Stop publish gate (armed, fail-closed, bounded at 8 blocks) |
| CLI verbs | 20 — `probe`, `import-note`, `archive-source`, `staleness`, `backfill-selectors`, `verify`, `factcheck`, `trust-tier`, `arm-publish`, `disarm-publish`, `mark-published`, `mark-parked`, `mark-corrected`, `mark-withdrawn`, `ack`, `finding`, `search-log`, `inbox`, `scaffold`, `doctor` |
| Deterministic checks | 10 — citekey, doi, metadata, quote, update-notice, evidence-layer, identifier-discovery, web-archive, screening-state, disputed-claim |
| Lints | 7 — append-only, claim-immutability, published-drift, screening-state, disputed-claim, web-archive, evidence-layer |
| Doctor probes | 10 — tree, machine-config, zotero, bbt, autoexport, staleness, remote, backup, inbox, okf |
| Result vocabulary | MATCHED / UNMATCHED / UNREACHABLE / SKIPPED |
| Closing sets | audit = none; commit = {citekey, evidence-layer}; publish = {citekey, evidence-layer, quote, update-notice, doi} |
| Reason-code registry | 18 codes, frozen in `inbox.REASON_CODES` |
| Check-id registry | 15 ids, frozen in `inbox.CHECK_IDS` |
| Trust tiers | unverified → machine-confirmed → human-reviewed, derived from `verified` events |
| Update-notice classes | blocking = retraction, partial_retraction, removal, withdrawal; warn = expression_of_concern, correction, corrigendum, erratum; a dated **reinstatement** clears an earlier dated block |
| Claim deprecation | required fields `status`, `deprecated-at`, `deprecated-by`, `reason` on the claim line (`lints._DEPRECATION_REQUIRED_FIELDS`); `superseded-by` optional; never deletion |
| Registries called | doi.org handle API, Crossref `/works`, OpenAlex `/works`, DataCite `/dois`, arXiv, NCBI eutils, Wayback save + availability; optional offline Retraction Watch CSV via `--rw-csv` |
| Zotero bridge | Better BibTeX JSON-RPC (`localhost:23119/better-bibtex/json-rpc`) plus the Zotero local web API (`/api/users/0/items/top?format=csljson`); 8-method client, read-only by design |
| Vault layout | `inbox/`, `literatures/`, `synthesis/`, `log/`, `projects/`, `system/templates/`, `system/bases/`, plus `index.md`, `log.md`, `AGENTS.md`, `.harness/` |
| Portability target | OKF (Open Knowledge Format), spec at `GoogleCloudPlatform/knowledge-catalog` `okf/SPEC.md`, tracked at v0.2; `index.md` declares `okf_version: "0.2"` and `scaffold._okf_probe` enforces conformance |
| Provenance unit | claim line = evidence-boundary tag + `[@citekey, locator]` + `^c-XXXXXXXX`; global address `citekey#^claim-id`; stance links `supports`/`disputes`; quote selectors (prefix/suffix); `fixity-sha256`, `managed-sha256` |
| Distribution | MIT, plugin v0.1.0, unpublished |

---

# Part II — The field

## 5. Roster at a glance

| Tier | What it means | Count |
|---|---|---|
| **1 — harness comparables** | owns an ingest→synthesis or research→manuscript lifecycle and could be run instead of this harness | 16 in the main table, all read at file level, plus 16 found by search of which 6 were read at file level (marked ✓) |
| **2 — component comparables** | replaces or overlaps exactly one layer of ours | 31 |
| **3 — informing prior art** | pipelines, gate tooling, standards and benchmarks that shape the design without competing | 21 |
| **4 — skill-framework baseline** | how a skill set is packaged, invoked, governed and tested | 2 |

## 6. Tier 1 — harness comparables

Stars, license and last push are as of 2026-08-22.

| Product | Stars | License | Last push | Substrate | Zotero | Registry checks | Enforcement | Provenance unit |
|---|---|---|---|---|---|---|---|---|
| Imbad0202/academic-research-skills | 43,339 | CC-BY-NC-4.0 | 2026-08-20 | files + YAML "passport" | reference adapter over a Better BibTeX JSON export | yes — Crossref/OpenAlex/Semantic Scholar/arXiv resolvers, `retraction_status.py`, `verification_cache` | PreToolUse write-scope guard (pass-through on failure), 14 CI workflows, 394 scripts | `<!--block:BNNNN-->` block IDs plus a hash manifest |
| garrytan/gbrain | 28,933 | MIT | 2026-08-22 | markdown pages over Postgres/pgvector | none | no — LLM and web verification | 24 pre-commit references, 7 CI workflows, 1,814 test files | `[Source: ...]` inline citation |
| AgriciDaniel/claude-obsidian | 11,137 | MIT | 2026-08-01 | Obsidian vault | none | no | `hooks.json`, deterministic read-only lint CLI, staged transactions | source and claim ledgers, `^`-block references |
| atomicstrata/llm-wiki-compiler | 1,952 | MIT | 2026-08-22 | compiled wiki owned by `.llmwiki/state.json` | none | Crossref connector (`src/connectors/impl/crossref.ts`) in the `autosci` profile | runtime write-path gates, fail-closed profile, review queue with reason codes | source file plus line-range citations |
| SamurAIGPT/llm-wiki-agent | 3,434 | MIT | 2026-08-17 | plain markdown wiki | none | no | post-ingest wikilink/index validation; `health.py` zero-LLM structural checks | source page with a `## Contradictions` section |
| pedrohcgs/claude-code-my-workflow | 1,520 | MIT | 2026-08-22 | LaTeX/Quarto + R repository | `.bib` only | `validate-bib --semantic` (structural plus Crossref DOI) | 7 hook scripts across PreToolUse/PostToolUse/Stop; Stop runs `log-reminder.py` | claim ledger, Chain-of-Verification in a forked context |
| NousResearch/hermes-agent | 234,366 | MIT | 2026-08-22 | plain markdown directory | none | no | prompt conventions in `llm-wiki`; **runtime ledger and `verify --evidence` in `grounded-citations`** | `^[raw/…]` paragraph markers; ledger-owned `[n]` for web sources |
| nvk/llm-wiki | 1,056 | MIT | 2026-08-22 | hub registry plus per-topic wikis | none | no | none | per-directory `_index.md`; raw immutable (AGENTS.md:115) |
| swarmclawai/swarmvault | 665 | MIT | 2026-06-30 | markdown + graph + SQLite FTS, Node CLI | none | no | approval bundles, review/candidate queues, 25% graph-shrink guard (`packages/engine/src/watch.ts:33`), git hooks | claim-pair records with `evidence_state` |
| Pratiyush/llm-wiki | 374 | MIT | 2026-06-18 | markdown wiki | none | no | 19 CI workflows, GitHub Action, Docker | frontmatter `confidence` (4-factor) and `lifecycle` (AGENTS.md:202-205) |
| **Aperivue/medsci-skills** | 264 | MIT | 2026-08-19 | **Obsidian vault + Zotero + `.bib`** | **`lit-sync` writes the library and the vault** | **`verify-refs` against PubMed/CrossRef; `verify_refs.py` also references OpenAlex and doi.org** | `verify-refs` audit-only; CLI preflight gates exit 1; no hooks | citekeys plus claim-fidelity probes |
| K-Dense-AI/scientific-agent-skills | 34,130 | MIT (per-skill `license:` varies) | 2026-08-19 | none — 163-skill library | `pyzotero` skill | no | none | `[claim:C001] [evidence:E001]` markers in `scientific-writing` |
| kepano/obsidian-skills | 47,059 | MIT | 2026-06-08 | Obsidian vault | none | no | none | none — vault format and operations only |
| anthropics/skills | 171,018 | none declared (plus `THIRD_PARTY_NOTICES.md`) | 2026-08-21 | none — 19 skill directories | none | no | none | none |
| WenyuChiou/ai-research-skills | 217 | MIT | 2026-08-02 | catalog for 16 skills in sibling repos | via `research-hub` / `zotero-skills` | no | none | `.paper` memory artifacts |

### 6.1 Aperivue/medsci-skills — the closest competitor found

59 skills for medical research. It is the only product in this comparison that matches our
substrate on both sides — Zotero *and* an Obsidian vault keyed by citekey — and two of its scripts
attack problems our design currently avoids rather than solves.

- **`lit-sync`** — syncs a `.bib` into the Zotero library *and* Obsidian literature notes, then
  extracts cross-cutting concept notes once enough literature accumulates. That is our
  `import-source` plus `synthesis-conventions` in one skill, with an accumulation threshold like
  our 2+-source rule. Ships `scripts/check_citekey_provenance.py`.
- **`obsidian-paper-vault`** — a two-layer vault (templated literature notes plus atomic concept
  notes) built from a folder of PDFs, explicitly co-owning the same folders as `lit-sync` from the
  opposite end. Its SKILL.md states the rules exist because their absence produced "a fabricated
  patient count, a broken PDF link, an empty Dataview table" in a vault of 100+ papers.
- **`verify-refs`** — audit-only verification, writing `qc/reference_audit.json` and explicitly not
  writing to `references/` or `refs.bib`. Same audit-not-gate posture as our default
  `verify --surface audit`.
- **`check_claim_fidelity.py`** — three probes ordered by checkability: `CITED_QUOTE_ABSENT`
  (major), `ATTRIBUTION_UNSUPPORTED` (fires only when not one content word of the attributed span
  appears in the source in any morphological form), and a third tier. This is our
  `factcheck-draft` question — does the source say what the sentence claims — implemented
  deterministically rather than as LLM adjudication.
- **`_quote_match.py`** — 172 lines, `re` and `unicodedata` only. Quote matching designed to
  survive a PDF extraction layer, documenting thirteen false positives that contiguous-string
  matching produces: two-column bleed, line numbers landing mid-sentence, superscript markers and
  hyphenation across line breaks. **Partial overlap with ours, and the residue is the interesting
  part.** Our `selectors._norm_with_map` already handles NFKC drift, soft hyphens, line-break
  dehyphenation and whitespace collapse — against extracted PDF text, at selector-production time
  (`__main__.py:257`). What it does not handle is *interleaved foreign tokens*, because
  `find_context` ends in a contiguous `normalized_text.find(...)`. medsci's `_ordered_run(needle,
  hay, allow_missing)` is a token-ordered subsequence match instead, which is precisely the class
  our contiguous find misses.
- **`manage-refs/check_citation_keys.py`** — pandoc `[@bibkey]` undefined/unused key check, the
  same job as our `citekey` check.

**Full survey, 2026-08-22.** 59 skills, roughly 180 scripts and 150 test files. The heaviest are
`self-review` (36 scripts, 26 tests), `sync-submission` (21/17), `make-figures` (13),
`present-paper` (11), `manage-refs` (9/9), `check-reporting` (6/7, covering 49 reporting
guidelines), `meta-analysis` (6/2), `peer-review` (6/3).

Two qualifications that matter for any adopt decision. First, **it is domain-locked**: 21 of the
59 skills are medical-specific — imaging preprocessing, radiomics, uncertainty imaging, MLLM
evaluation, model cards and validation, cohort-gap discovery, batch cohorts, cross-national
KNHANES/NHANES/CHNS studies, sample-size calculation, deidentification, ICMJE COI. Its own
marketplace description calls it "physician-built … submission-grade, not a generic skill
catalog". Second, **it ships no hooks**: `.claude-plugin/` contains only `marketplace.json`, with
no `plugin.json` and no `hooks/` anywhere in the tree, so nothing it does is enforced at a session
boundary. Its enforcement is CLI gates a person runs — `sync-submission/scripts/preflight_gate.py`
returns 1 on halt (:587) and `manage-refs/scripts/pre_submission_gate.sh` exits 1 (:154).

It is distributed as several plugins; `medsci-literature` bundles exactly the six skills that
overlap us — `fulltext-retrieval`, `lit-sync`, `manage-refs`, `obsidian-paper-vault`, `search-lit`,
`verify-refs`.

### 6.2 Imbad0202/academic-research-skills — the strongest trust machinery

Four mega-skills (`deep-research`, self-described as a 13-agent pipeline over 14 agent files;
`academic-paper`, 12 agents; `academic-paper-reviewer`, a 5-seat panel; `academic-pipeline`, the
orchestrator), 16 slash commands, 3 top-level agents, 394 Python scripts.

`scripts/verification_gate` composes Crossref, OpenAlex, Semantic Scholar and arXiv resolvers into
a per-citation outcome. `retraction_status.py` is a deterministic resolver over already-returned
metadata with a 30-day revalidation cache; it models reinstatement as a clearing verdict
(lines 114, 140-146). `ars_anchorize_draft.py` stamps `<!--block:BNNNN-->` markers and emits a
hash manifest, explicitly so an agent cannot hallucinate a hash. It carries an `evals/` directory
(gold, held-out, calibration, bakeoff), an `audits/` directory, and cross-model verification
against Codex.

**`shared/bibliographic_integrity_signals.md`** is the sharpest artifact in the whole comparison.
Schema authority `shared/contracts/passport/bibliographic_integrity_signal.schema.json`, versions
1.0 → 1.2. It defines an epistemic boundary between three classes that "must not be collapsed":

| `epistemic_class` | Required label | What it establishes |
|---|---|---|
| `deterministic_fact` | `RESOLVER-OR-LIST-OBSERVATION` | what a named resolver or list returned at a recorded time — not whether the work is genuine, retracted or sound |
| `heuristic_advisory` | `HEURISTIC-INDICATOR` | a rule or model matched; never a factual finding by itself |
| `process_attestation` | `CHECK-EXECUTION-ATTESTATION` | a check was reportedly run; not the result of that check |

`check_status` and `finding` are **independent**: `not_checked`, `unknown` and `degraded` all
require `finding: unresolved`, and the formatter must render any of them as
**NOT CLEAN — UNRESOLVED**. A legacy `retraction_check: true` migrates only to a checked execution
attestation with an unresolved finding — "it never becomes `not_detected`". Each rendered row
carries resolver name, version and hash plus checked/recorded/stale timestamps. `terminal_policy`
records eligibility and the policy owner but does not enact policy; "adding a signal never
silently promotes it to `HIGH-BLOCK`".

That is our four-state doctrine written as a versioned schema, and stricter in one respect: we
fold "the check ran" and "what it found" into a single `Result`, where they separate them.

Four further mechanisms, all present as scripts: `run_indirect_prompt_injection_probe.py`,
`run_indirect_prompt_injection_no_call.py`, `check_indirect_prompt_injection_no_call.py` and
`check_instruction_data_boundary.py` (the untrusted-source boundary is probed and tested, not
asserted in prose); `check_judge_prompt_version.py` (the judge prompt version is a checked
invariant); `uncited_assertion_detector.py` (mechanical detection of assertions carrying no
citation); and a `rejection_log.yaml` beside the literature-corpus passport, recording
non-admission with reasons — the same job as our `search-log --not-admitted` records.

Against us: broader in verification tooling, far broader in writing and reviewing, and it has an
evaluation apparatus we lack entirely. Narrower in substrate: no vault, no citekey join key, no
Obsidian conventions, and Zotero contact is one adapter reading an export rather than a live
bridge. CC-BY-NC-4.0 forecloses a fork.

### 6.3 garrytan/gbrain — the largest skill surface, no registry verification

71 skill directories, several overlapping ours by name: `academic-verify`, `fact-check`,
`citation-fixer`, `ingest`, `brain-ingest-gate`, `publish`, `maintain`, `concept-synthesis`,
`correction-pipeline`, `data-loss-gate`, `frontmatter-guard`, `schema-author`, `cron-scheduler`,
`minion-orchestrator`. 41 of the 71 ship a `routing-eval.jsonl`.

`brain-ingest-gate` is a pre-write dedup gate that resolves named entities registry-first ("a
vector score is a floor for prose, never a gate for named things") then runs a read-the-top-hit
decision tree. `fact-check` assigns a 6-level confidence status, checks "against live citable
sources (never training data)", and applies a data-derived-claims gate with two named rules —
**PRODUCER ≠ VERIFIER** (re-derive each claim via a different query path) and
**AFFILIATION ≠ AUTHORSHIP** (person→thing claims resolve through typed edges) — with **delivery
hard-blocked on unsupported claims**.

`docs/contradictions.md` specifies a Wilson 95% confidence interval on the headline rate (line
57), a per-finding severity rubric (line 74), temporal verdicts
`temporal_supersession | temporal_regression | temporal_evolution` (line 157), a
`resolution_command` field per finding (line 109), and a pinned "NEVER auto-applies" invariant on
supersession (line 169). `src/commands/dream.ts` is a 6-phase enrichment cycle with `--phase`
selection and `--dry-run` preview.

Verification is LLM- and web-driven: `academic-verify` routes through a Perplexity research skill,
and the only OpenAlex reference in the repository is prose inside `skills/academic-verify/SKILL.md`
(and its plugin mirror) — there is no registry client in code. Its state lives in Postgres and
pgvector, so nothing is adoptable as code for a git-diffable vault.

### 6.4 AgriciDaniel/claude-obsidian — the closest substrate match without a reference manager

15 skills over an Obsidian vault, with source and claim ledgers, a deterministic read-only lint
CLI, and a staged-transaction write path. `wiki-ingest` computes SHA-256 per payload against
`.raw/.manifest.json`, applies a compilation-value gate (a no-op is a legitimate outcome), budgets
existing-page reads at five per source, runs read-only parallel workers that may not write, and
lands a single `claude-obsidian.transaction.v1` bundle through `transaction inspect` →
`transaction apply --approved-plan-sha256`. It also ships `wiki-retrieve` (vault-local contextual
BM25 with optional Nomic reranking), `wiki-query`, `wiki-fold`, `wiki-mode`
(Generic/LYT/PARA/Zettelkasten filing), `autoresearch` and `think`.

Its ingest skill carries the strongest untrusted-source discipline found: source content is
declared untrusted data; embedded instructions, fake role messages, commands, egress requests,
destination changes and requests for secrets must be ignored; fetching any URL requires explicit
consent for destination domains and a request budget; processing stops when redirects leave the
approved scope; a canonical claim may not be built whose only locator is an outside-vault path;
`.raw/` payloads are `create`-mode only, so "a changed remote source receives a new immutable
capture or an honest ledger update, not an overwrite"; a partial read must be labelled partial
with the missing range recorded; and unsupported media extraction must be reported rather than
pretended.

Its deterministic core carries two mechanisms with no counterpart here. **`ledgers.py`** (1,351
lines): `stable_source_id()` at line 407 derives a content-addressed identity from origin kind,
canonicalised locator and content SHA-256; an `independence_key` field is validated per record
(line 737); and `_independent_group_count()` (line 797) collapses sources sharing an origin,
content hash or independence key so they cannot count as independent corroboration — used at line
1130 to enforce "**high-risk acceptance requires two independent sources**" (line 1135). That is a
deterministic answer to corroboration-by-repetition. **`agents/verifier.md`** is a fresh-context,
read-only verifier subagent (`model: sonnet`, `maxTurns: 35`, tools `Read, Grep, Glob, Bash`) that
"reports evidence-ranked findings without modifying Git or repository state".

It has no reference manager and no external-registry verification: its ledgers record what the LLM
asserted, not what a registry confirmed.

### 6.5 atomicstrata/llm-wiki-compiler — enforcement in the runtime, not the prompt

A Node CLI with 32 source subsystems including `compiler`, `connectors`, `eval`, `freshness`,
`linter`, `mcp`, `profile`, `review`, `sdk`, `trust`, `workflows`. Configurable Lifecycle Profiles
declare typed entities, relations, lifecycle states, transition evidence, trust gates, workflows,
artifacts and connectors, all enforced at the write path and failing closed on an invalid profile.
It ships an MCP server (`llmwiki serve`), a TypeScript SDK, a local viewer, a review policy with
reason codes, freshness repair (`refresh --stale`), OKF export and import, and Ed25519-signed
template distribution. Its `autosci` research profile ships a Crossref connector restricted to
`api.crossref.org`.

Its citation model is the closest external analogue to ours. `docs/concepts/citations.mdx`
documents paragraph-level `^[file.md]` and **claim-level line ranges** `^[file.md:42-58]`.
`llmwiki lint` classes a marker whose file is absent from `sources/` as an **error**, attributing
it explicitly to a deleted source or "when the LLM hallucinated a filename", and rejects malformed
ranges. `llmwiki eval` reports **citation precision** — the fraction of markers pointing at a file
that exists — and a **`claim_level_citation_rate`**: the fraction of citations pinning a line
range rather than a whole file, with a minimum settable in `.llmwiki/eval/thresholds.yaml`, plus
health score, per-page health distribution, wikilink-graph health, regression deltas and optional
judge-model citation support with a cache at `.llmwiki/eval/citation-cache.jsonl`.

It is the only comparable that enforces structure at the write path and the only one that
*measures* citation quality. Its wiki is a compiled artifact owned by `state.json`, so pages
co-authored outside a compile fall out of ownership tracking.

### 6.6 NousResearch/hermes-agent — disciplined prompt in one skill, runtime gate in its sibling

The `llm-wiki` skill is one 507-line SKILL.md: orientation-first every session (SCHEMA + index +
last 20–30 log entries); page thresholds (create at 2+ sources or centrality, add to existing
otherwise, never for passing mentions, split above ~200 lines, archive when superseded); a closed
tag taxonomy that must be extended before use; a minimum of two outbound wikilinks per page plus a
backlink check; `^[raw/…]` paragraph provenance on pages synthesizing 3+ sources; `confidence` and
`contested` frontmatter where a single-source page with no confidence field is itself a lint
signal; a four-step Update Policy for contradictions; raw-body `sha256` giving skip-if-identical
re-ingest and drift flagging; an 11-check lint including orphan detection, broken wikilinks, index
completeness, stale content, source drift, page size, tag audit and log rotation; a bulk-ingest
mode that identifies entities across all sources before one write pass; and an ask-first gate when
an ingest would touch 10+ existing pages. Its 2+-source threshold is identical to ours, and its
lint covers five classes we do not check.

Everything in that skill is a prompt convention with zero runtime enforcement — **but that is true
of the skill, not of the repository.** The sibling `skills/research/grounded-citations`
(232 lines) puts a script in charge: a **ledger owns the `url → [n]` mapping** "so the numbers and
URLs come from retrieval, never from memory — the model only ever emits small integers it was
handed" (SKILL.md:18-20); **verbatim quotes are rejected unless they literally appear in the
fetched page text** (:22-24); claims from model knowledge are flagged `[unverified]`; and
**`verify --evidence` fails any draft whose cited sources carry no evidence** (:24-25). Source ids
stay stable across search and extract rounds (:70). Same instinct as ours — the machine, never the
model, writes citations — applied to web sources rather than a bibliography, and the nearest peer
found to our quote gate.

### 6.7 swarmclawai/swarmvault — the largest operational surface of the wiki family

A Node CLI documenting init, quickstart, scan, clone, source add/reload/guide/session, ingest,
inbox import, watch, compile (with `--approve` and `--max-tokens`), review list/show/accept/reject,
candidate list/promote/archive, query, chat (persisted multi-turn), explore, context
build/list/show/delete, task ledgers, doctor with `--repair`, lint (advisory deep pass, optional
web evidence), graph subcommands (query, explain, path, callers with file:line evidence, blast,
cycles, cluster, tree, merge, validate, diff, serve, export to HTML/JSON/Obsidian/Canvas/Neo4j),
an MCP server, and `export ai` producing `llms.txt`, `llms-full.txt`, JSON-LD and per-page
siblings. `swarmvault next` is a read-only orientation command returning paths, checks and
recommended commands. Ingest covers PDF, the Word/Excel/PowerPoint families, RTF, ODF, EPUB,
CSV/TSV, Jupyter, BibTeX, Org, AsciiDoc, transcripts, Slack, email, calendar, audio, video,
YouTube and images, plus source code. It carries the only destructive-refresh circuit breaker
found — a 25% node/edge shrink guard. Agent installers exist for over 40 agent tools.

No reference manager, no registry verification, no per-claim citation address.

### 6.8 pedrohcgs/claude-code-my-workflow — the other academic harness

52 skills over a LaTeX/Quarto + R repository, with a clean split between structural bibliography
lint and claim-support judgment.

`validate-bib` runs structurally by default — missing entries, unused entries, malformed fields,
typo candidates, across `.tex`/`.qmd`/`.md` including both `@key` and `[@key]` pandoc forms — and
`--semantic` adds citation-drift detection (duplicate entries for the same paper), **DOI
verification via Crossref**, and citation-style consistency within each file, with reports at
`quality_reports/bib_audit_[structural|semantic].md`. `verify-claims` runs Chain-of-Verification
per Dhuliawala et al. 2023, spawning a `claim-verifier` agent **in a forked context so the
verifier never sees the draft**.

Also: `seven-pass-review`, `deep-audit`, `review-paper`, `respond-to-eval`, `proofread`,
`replication-package`, `audit-reproducibility`, `stata-replication`, `power-analysis`,
`data-management-plan`, `disclosure-check`, `submission-disclosures`, `grant-proposal`,
`teach-from-paper`, `syllabus`, `compile-latex`, `qa-quarto`, `slide-excellence`,
`capture-environment`, `checkpoint`, `compress-session`, `context-status`, `promote-memory`,
`triage-inbox`. Seven hook scripts; the Stop hook is `log-reminder.py`, not a verification gate.

### 6.9 nvk/llm-wiki — capture/compile split and a large operation set

`AGENTS.md` is 1,056 lines. A hub registry (`wikis.json`) over per-topic wikis, with operations for
Init, Ingest, Ingest Collection, Private Adapters, Personal Specialist Skills, Compile, Query,
Research, Thesis, Collect, Retract, Refresh, Inventory, Ideas, Portfolio, Dataset and Archive.
Compile is incremental with a topic-guide preflight, concept classification, confidence scores,
aliases and bidirectional link repair. Query has three depths and is forbidden from using training
data. Research launches 5, 8 or 10 parallel agents by depth. **Retract** is user-authoritative
control-plane behaviour that overrides raw immutability and append-only rules, dry-runs by
default, and deletes the raw source plus unsupported derived claims. **Refresh** re-fetches source
URLs, classifies change as cosmetic/additive/contradictory and never auto-recompiles. Inventory
tracks candidates, queues, open questions, tasks and watch items, and is explicitly not evidence
for factual questions. Reusable specialist methods live under `HUB/.skills/<name>/SKILL.md` with
`HUB/.skills/registry.json` holding **explicit per-active-topic allowlists and no global defaults**
(AGENTS.md:520-527).

### 6.10 SamurAIGPT/llm-wiki-agent — the faithful gist instantiation, with real gaps

`CLAUDE.md` specifies a 10-step ingest, a source-page template carrying a `## Contradictions`
section, query, lint, and a `health` workflow (`tools/health.py`, zero LLM calls: empty/stub files,
index sync, log coverage). Two mechanism facts verified in code rather than docs:
`tools/ingest.py` computes `sha256(source_content, truncate=16)` at line 199 and uses it only in
the `print` at line 202 — the hash is never compared, so re-ingest is not idempotent; and
`tools/_utils.py:114` documents `append_log` as *prepending* ("newest-first") while `CLAUDE.md`
documents append plus a `tail` recipe. Ours makes re-import a render-first no-op and treats the log
as an append-only surface with a drift lint.

### 6.11 Pratiyush/llm-wiki — maturity metadata and context economy

Frontmatter carries `confidence` as a 4-factor score (source count, quality, recency,
cross-refs), `lifecycle` in {draft, reviewed, verified, stale, archived} and `entity_type` in a
closed set; hard rules include raw immutability, no silent overwrites, mandatory `## Connections`
cross-linking, and "frontmatter is authoritative". Its context-economy machinery (AGENTS.md:13-20)
has no counterpart here: `log.md` auto-archives at 50 KB; `hot.md` holds the last 10 session
summaries as a global hot cache; `MEMORY.md` is cross-session facts under a 200-line cap,
auto-consolidated; `CRITICAL_FACTS.md` is capped at **under 120 tokens**; `SOUL.md` carries wiki
identity and voice. Six skills and 19 CI workflows.

### 6.12 K-Dense-AI/scientific-agent-skills — our upstream, and four more comparables

163 skills. `paper-lookup` is the direct upstream of our `find-sources`. Four others are
substantive comparables, verified at the pinned SHA `336c4f8`:

- **`scientific-writing`** — the closest external analogue to claim-first drafting. Nine stdlib
  scripts (`audit_claims.py`, `check_references.py`, `check_consistency.py`,
  `validate_manifest.py`, `validate_authorship.py`, `lint_manuscript.py`, `scaffold_manuscript.py`,
  `select_reporting_guidelines.py`, `_common.py`) over registry files, with inline markers
  `[claim:C001] [evidence:E001,E002]` (`references/evidence_workflow.md:39`) and a
  **`claim_text_sha256`** field validated against a SHA-256 regex (`audit_claims.py:28,99`) — a
  claim record stores a hash of normalised claim text, not the text. Our `factcheck` uses a claim
  `text_hash` as the finding's `--target-hash` for the same reason.
- **`peer-review`** — deterministic local-only CLIs including `audit_citations.py` (closed-universe
  citation audit against a local reference CSV, no network) and `validate_claim_evidence.py`, with
  `claim_evidence_matrix_template.csv` and `source_ledger.csv` as assets.
- **`paperclip`** — a hosted service whose doctrine is a locator convention: every document is
  line-numbered "and that is the point of the tool: you cite `#L45`" (SKILL.md:24), with citation
  URLs `https://paperclip.gxl.ai/citations/{papers|fda|trials}/<doc_id>#L<n>` (:309-312).
- **`liteparse`** (Apache-2.0 in frontmatter) — fully local PDF/Office/OCR parsing with per-token
  bounding boxes; a credible answer to the extraction leg our quote gate avoids.

Also `citation-management`, `pyzotero`, `literature-review`, `research-lookup`, `exa-search`,
`bgpt-paper-search`, `paperzilla`, `research-grants`. **Licence hazard, verified directly:**
`skills/docx/LICENSE.txt` opens "© 2025 Anthropic, PBC. All rights reserved." Four skills in this
MIT repository — docx, pdf, pptx, xlsx — ship proprietary LICENSE.txt files and must never be
copied on the strength of the repository licence.

### 6.13 WenyuChiou/ai-research-skills — a catalog, but not a thin one

Zero `SKILL.md` files in-repo. A 560-line `catalog/skills.yml` catalogues 16 skills across five
plugin families — `research-hub`, `zotero-skills`, `academic-writing-skills`, `codex-delegate`,
`gemini-delegate` — living in sibling repositories, each entry carrying `verified_on`,
`verification_status` and `verification_tier` (T1): a provenance convention for the catalog's own
claims. Notable entries: `research-hub` (a separate pip runtime, `research-hub-pipeline`, driving
Zotero + Obsidian + NotebookLM), `zotero-skills` (deep Zotero CRUD), `zotero-library-curator`
(duplicate-DOI and orphan-item audits, read-only), `paper-summarize` (writes findings into both
Obsidian markdown and Zotero child notes), `notebooklm-brief-verifier`,
`literature-triage-matrix`, `paper-memory-builder`, `research-design-helper`, and **`gap-to-topic`**
— a three-gate go/no-go dossier (is the gap open? is it a contribution? is it feasible?) that
"stops short of the verdict, handing the worth-it call back to the researcher and advisor", with
downstream candidate selection filtered to `verdict in {conditional-go, go}`.

It writes *into* Zotero where we hold the library human-owned and read-only — the sharpest
divergence in the pool on our own axis. And `gap-to-topic` gates whether a question is worth
asking, a step upstream of anything our `project` skill does. MIT, so adoptable.

### 6.14 kepano/obsidian-skills and anthropics/skills — dependencies, not competitors

kepano ships five skills covering vault format and operations (`obsidian-markdown`,
`obsidian-bases`, `json-canvas`, `obsidian-cli`, `defuddle`); our `setup-vault` lists it as the one
provisioned companion. anthropics/skills ships 19 skill directories, none for research or
citations; its document skills are the missing renderer at our submit end, and it carries a
separate `THIRD_PARTY_NOTICES.md`.

### 6.15 WenyuChiou/research-hub — the runtime behind the catalog, and a second MIT gate

52 stars, MIT, pushed 2026-07-21. "AI-operable research workspace for Zotero, Obsidian, and
NotebookLM. Use any two, or all three, through CLI, MCP, REST, and dashboard." Eleven skills —
`research-hub`, `research-hub-multi-ai`, `research-context-compressor`,
`research-project-orienter`, `research-design-helper`, `literature-triage-matrix`,
`paper-memory-builder`, `paper-summarize`, `notebooklm-brief-verifier`, `zotero-library-curator`,
`gap-to-topic` — over a substantial Python package (`src/research_hub/`) with per-surface CLI
modules for citations, clusters, maintenance, NotebookLM, papers, pipeline, search, summarize,
vault and Zotero.

**`src/research_hub/authenticity.py` (1,176 lines) is the finding.** Its docstring is
"Fail-closed authenticity gate for ingest candidates", and `verify_authenticity()` routes each
candidate through layered checks, quarantining rather than deleting what fails:

- **L0** — no resolvable identifier → quarantined.
- **L1** — identifier resolution, with a distinction we make too: a *transient* failure
  (anti-bot wall, rate limit, unreachable after retry) "is NOT fabrication evidence"; the paper
  falls through to later gates and, if they pass, is admitted carrying a DOI-recheck marker for a
  later run. Only definitive non-registration (HTTP 404/410) is a permanent L1 rejection.
- **L2** — Crossref corroboration, plus a predatory-venue denylist, "fail-closed, recoverable via
  quarantine".
- **L3** — metadata integrity.
- Optional fit check against cluster fit scores.

Quarantine is a first-class, recoverable state (`quarantine_paper`, `list_quarantine`,
`show_quarantine`, `restore_quarantine`), with resolve and Crossref-verify caches and a documented
poisoned-cache migration for stale fail-closed entries.

**Why this matters to our positioning.** It is MIT, and it gates fail-closed on registry evidence
— so "no forkable product gates" was too strong. The boundary differs: research-hub gates
*admission of a candidate into the corpus* on *per-paper* authenticity, upstream of where we sit.
We gate *a draft, a commit and a session* on *per-claim* evidence. Those are complementary rather
than competing, and its transient-versus-permanent rule is the same doctrine as our
UNREACHABLE-is-never-a-verdict, implemented independently.

It has no claim addressing, no stance links, no quote verification and no publication lifecycle.

### 6.16 Found by search, not yet read at file level

Sixteen further Tier-1-shaped products surfaced in the search pass. Rows describe the project's
own claim except where a file was opened, marked ✓.

| Product | Stars | License | Last push | Why it belongs |
|---|---|---|---|---|
| Orchestra-Research/AI-Research-SKILLs | 11,950 | MIT | 2026-06-16 | *Excluded on inspection* — top-level dirs are `01-model-architecture`, `03-fine-tuning`, `13-mlops`: ML engineering, not literature work ✓ |
| eugeniughelbur/obsidian-second-brain | 4,152 | MIT | 2026-08-21 | Persistent markdown memory in an Obsidian vault across 7 CLI agents |
| zLanqing/codex-claude-academic-skills | 3,097 | MIT | 2026-05-14 | Three academic skills covering reading → writing → scientific computing |
| sdyckjq-lab/llm-wiki-skill | 2,363 | MIT (README) | 2026-07-27 | Multi-platform Karpathy-wiki skill; bundles the four Anthropic document skills under their own proprietary LICENSE.txt |
| Astro-Han/karpathy-llm-wiki | 1,982 | MIT | 2026-07-23 | Agent-Skills LLM wiki built around raw sources, citations and linting; ships `scripts/check_evidence.py` ✓ |
| delibae/claude-prism | 1,751 | MIT | 2026-07-28 | Offline-first scientific writing workspace, LaTeX + Python + 100+ local skills ✓ |
| skyllwt/AutoSci | 1,642 | MIT | 2026-08-19 | Autonomous-science skill suite (paper-plan, experiment eval, rebuttal, refine), i18n ✓ |
| lucasastorian/llmwiki | 1,520 | Apache-2.0 | 2026-08-09 | Karpathy wiki driven through MCP against a Claude account |
| OpenRaiser/NanoResearch | 1,355 | MIT | 2026-05-26 | Autonomous research assistant |
| lishix520/academic-paper-skills | 1,200 | MIT | 2026-01-04 | Strategist/composer paper-writing framework with quality checkpoints |
| huytieu/COG-second-brain | 931 | MIT | 2026-08-18 | 33 skills, 10 agents, "V-model verification lifecycle where the worker never grades its own homework" ✓ |
| kytmanov/obsidian-llm-wiki-local | 810 | MIT | 2026-05-26 | Fully local Karpathy wiki (Ollama) writing an auto-linking Obsidian vault ✓ |
| jason-effi-lab/karpathy-llm-wiki-vault | 692 | none — all rights reserved | 2026-04-13 | Karpathy wiki as a vault; the only repository in this roster declaring no licence in any form |
| Ar9av/PaperOrchestra | 644 | NOASSERTION | 2026-08-09 | Skills implementation of Google's PaperOrchestra with benchmark and autoraters |
| 917Dhj/DeepPaperNote | 630 | MIT | 2026-08-22 | Deep-read one paper → Obsidian-style research notes; ships an `evals/` directory ✓ |
| trapoom555/claude-paperloom | 94 | Apache-2.0 | 2026-04-28 | Claude Code plugin: self-maintaining research knowledge graph over Obsidian; agents for metadata, finding extraction and finding linking; `init`/`ingest`/`lint`/`query` ✓ |

## 7. Tier 2 — component comparables

Each replaces or overlaps exactly one layer of ours. Only 54yyyu/zotero-mcp was read at file
level; the rest are metadata-level rows describing what each project is for.

**Zotero access** — the field is seven deep, not one:

| Component | Stars | License | Last push | Shape |
|---|---|---|---|---|
| 54yyyu/zotero-mcp | 4,751 | MIT | 2026-08-13 | **51 tools** against our 8-method client ✓ |
| introfini/ZotSeek | 189 | MIT (README) | 2026-08-21 | Zotero plugin: local semantic search with a built-in MCP server ✓ |
| kujenga/zotero-mcp | 161 | MIT | 2026-08-07 | Lightweight Python MCP server over the Zotero API |
| TonybotNi/ZotLink | 137 | MIT (README) | 2025-10-12 | MCP server that *saves* preprints into Zotero with metadata and PDFs |
| PiaoyangGuohai1/cli-anything-zotero | 128 | Apache-2.0 | 2026-07-28 | CLI server for Zotero 7/8/9, 70+ commands ✓ |
| xunhe730/ZotPilot | 70 | MIT | 2026-06-28 | MCP server plus agent skill |
| dougwyu/claude-zotero-skills | 34 | NOASSERTION | 2026-08-07 | Skills for Zotero access |

zotero-mcp's surface is the sharpest component-level contrast. Its 51 tools include
`zotero_search_by_citation_key`, `zotero_get_attachment_path`, `zotero_get_annotations`,
`zotero_create_annotation`, `zotero_update_annotation`, `zotero_read_pdf_pages`,
`zotero_get_pdf_outline`, `zotero_get_page_layout`, `zotero_get_item_fulltext`,
`zotero_semantic_search`, `zotero_find_duplicates`, `zotero_merge_duplicates`,
`zotero_find_related_papers`, `zotero_expand_from_paper`, `zotero_find_contradicting_evidence`,
`zotero_literature_review`, `zotero_synthesize_annotations`, `zotero_library_coverage`,
`zotero_export_bibliography`, `zotero_add_item`, `zotero_batch_update`, plus feed and
multi-library management. It also ships `tools/scite.py`, surfacing supporting / contrasting /
mentioning citation counts and retraction alerts from Scite's public endpoints with no API key.

**Citation verification** — the class most directly overlapping our `verify` verb:

| Component | Stars | License | Last push | What it does |
|---|---|---|---|---|
| Hylouis233/bibverify | 73 | MIT | 2026-08-22 | DOI-first BibTeX verification as CLI, Python API **and MCP server**: `doi_to_bibtex`, `rank_lookup_sources`, `explain_update_diff`, `verify_bib_file`. It reports *why* a lookup source was chosen; we do not ✓ |
| PHY041/claude-skill-citation-checker | 29 | MIT (README) | 2026-03-22 | Claude Code skill verifying `.bib` against CrossRef, Semantic Scholar and OpenAlex ✓ |
| tfscharff/doi-mcp | 15 | MIT | 2026-07-30 | MCP server verifying citations against 9 databases ✓ |
| DeepCitation/deepcitation | 13 | MIT | 2026-08-18 | Citation verification against hallucination |
| groundlens-dev/groundlens | 7 | Apache-2.0 | 2026-08-22 | Grounding and faithfulness checking of RAG answers against retrieved sources |
| htlin222/research-guardian-skill | 5 | MIT (README) | 2026-04-17 | Multi-gate audit of hypotheses, citations, experiments, results and logic fallacies ✓ |

**Vault and bibliography conventions**:

| Component | Stars | License | Maps to |
|---|---|---|---|
| retorquere/zotero-better-bibtex | 7,046 | MIT | upstream of our citekey universe (`system/bibliography.json`) |
| urschrei/pyzotero | 1,401 | NOASSERTION | alternative to our hand-rolled stdlib client |
| urschrei/zotero_search_skill | 12 | BlueOak-1.0.0 | precedent for a skill-not-MCP Zotero surface |
| aidenlx/zotlit | 1,000 | AGPL-3.0 | literature-note conventions (managed regions, citekey filenames) |
| community-archive/obsidian-zotero-integration | 1,756 | GPL-3.0 | persist-region convention origin |
| hans/obsidian-citation-plugin | 1,336 | MIT | `@citekey` note-title convention origin; last push 2024-06-13 |
| coddingtonbear/obsidian-local-rest-api | 2,832 | MIT | alternative to our direct-file vault access |
| yilewang/llm-for-zotero | 2,719 | AGPL-3.0 | inverse topology — the agent lives inside Zotero |

**Literature search** — comparables to `find-sources` beyond K-Dense `paper-lookup`:

| Component | Stars | License | Coverage |
|---|---|---|---|
| cookjohn/cnki-skills | 865 | MIT (README) | CNKI search, journal browse, PDF download, **export to Zotero** — a Chinese-language corpus our vendored skill does not cover |
| cookjohn/gs-skills | 489 | MIT | Google Scholar skills |
| Agents365-ai/paper-fetch | 184 | MIT | Paper retrieval skill |
| Agents365-ai/asta-skill | 182 | MIT | Instruction pack wrapping Ai2's Asta MCP server over Semantic Scholar ✓ |
| wp-a/nature-academic-search | 101 | MIT | Nature-family search |
| htlin222/openevidence-mcp | 70 | Apache-2.0 | OpenEvidence MCP |

**Systematic review, retrieval and graph**:

| Component | Stars | License | What it does |
|---|---|---|---|
| PouriaRouzrokh/LatteReview | 119 | NOASSERTION | Python package automating systematic literature review with multi-agent reviewers ✓ |
| htlin222/prisma-automation | 8 | MIT | Multi-database search, deduplication, screening and **PRISMA flow-diagram generation** ✓ |
| obra/knowledge-graph | 106 | MIT (README) | Query and traverse an Obsidian vault as a knowledge graph — semantic search, path finding, community detection, all local ✓ |
| YishenTu/claudian | 14,920 | MIT | Obsidian plugin embedding Claude Code/Codex inside the vault — the inverse integration topology |

## 8. Tier 3 — informing prior art

### 8.1 Answer pipelines

**Future-House/paper-qa** (9,078, Apache-2.0) ships a metadata client layer worth studying
directly: `clients/crossref.py`, `openalex.py`, `semantic_scholar.py`, `unpaywall.py`,
`retractions.py` (a `RetractionDataPostProcessor` over a bundled `client_data/retractions.csv`
with a `download_retracted_dataset` refresh path), and `journal_quality.py`. Its agent layer
exposes a `gather_evidence` tool (`agents/tools.py:218`).

**stanford-oval/storm** (31,108, MIT, last push 2025-09-30) is a `storm_wiki` engine plus a
`collaborative_storm` variant; idle for eleven months.

**assafelovic/gpt-researcher** (29,085, Apache-2.0) carries roughly 20 retriever backends
including `openalex`, `pubmed_central`, `semantic_scholar` and `arxiv`, and skills for
`researcher`, `curator`, `writer`, `deep_research`, `context_manager`, `browser`.

### 8.2 Citation gates that already exist as shipping tools

This class had no representation before this pass, and it is where our publish gate's design has
external precedent.

| Tool | Stars | License | Last push | Gate mechanism, verified |
|---|---|---|---|---|
| manubot/manubot + manubot/rootstock | 474 / 481 | NOASSERTION | 2026-08-02 / 2026-01-18 | Citation *by identifier* — `[@doi:…]`, `[@pubmed:…]`, `[@arxiv:…]` resolved to metadata at build time in CI, so the fabrication class becomes "identifier does not resolve" |
| errata-ai/vale | 5,992 | MIT | 2026-08-21 | Severity tiers with `--minAlertLevel` (`internal/core/config.go:17`); only the top tier fails a build |
| lycheeverse/lychee + lychee-action | 3,851 / 508 | Apache-2.0 | 2026-08-18 / 2026-07-09 | Link checking with retries, accept-lists, ignore files and caching; `action.yml` on master sets **`fail: default: true`** |
| pre-commit/pre-commit | 15,520 | MIT | 2026-08-17 | Commit-time gate bypassable by design (`--no-verify`, `SKIP=`), with CI replay as the honest layer |

**Manubot is the closest external precedent for our publish gate's shape**, and it differs in a
way worth stating: it dissolves the citekey-fabrication class rather than checking for it. Its
failure model is fail-open by default with a one-line strict opt-in —
`manubot-fail-on-errors: true` (`rootstock/USAGE.md:162`) — and its bypass is **data, not a flag**:
files matching `manual-references*.*` supply metadata for citations the resolvers cannot handle,
and "the metadata for unhandled citations … must be provided in a manual reference file … or an
error will occur" (`USAGE.md:207-216`). That is the same design as our acknowledgment: the
override is a record, not a switch that disables the check.

**lychee-action's `fail: true` default is a direction-of-travel signal**: the escape hatches came
first and the default flipped closed once they existed. Our publish gate is closed with a recorded
bypass and an 8-block liveness bound; the field arrived at the same shape from the opposite
direction. **Vale's exit-code split** between "linting errors were found" and "a runtime error
occurred" is the distinction we carry both in `Result` (UNMATCHED vs UNREACHABLE) and in CLI exit
codes (`1` vs `3`) — convergence, not a gap.

### 8.3 The standards our provenance model implements

**W3C Web Annotation Data Model** (Recommendation) — `TextQuoteSelector` carries `exact` ("a copy
of the text which is being selected, **after normalization**"), with `prefix` and `suffix` each
SHOULD-have-exactly-one, and the rule that "the text MUST be normalized before recording in the
Annotation" (spec text fetched and verified). Our stored selectors
(`<!-- hk-selector prefix="…" suffix="…" -->`) are that shape; no other product here stores
prefix/suffix anchors at all.

**Hypothes.is client** (721 stars) is the reference implementation of the opposite tolerance
policy, and the number matters because it is the one a gate must not inherit:
`src/annotator/anchoring/match-quote.ts:99` sets `const maxErrors = Math.min(256, quote.length / 2)`
— **up to half the quote may mismatch and still anchor**. That suits a highlighting UX, where a
misplaced anchor costs little. A trust gate inverts the cost: the expensive error is a false pass.
Our `fuzzy-quote` reason code exists so an approximate match becomes a finding, never a pass.

**Wikidata** is the mass-deployed instance of deprecate-never-delete. A statement carries
property + value + qualifiers + references and one of three ranks — preferred, normal,
**deprecated** — with a reason recorded. Property labels confirmed live through the Wikidata API:
**P2241** "reason for deprecated rank", **P248** "stated in", **P304** "page(s)", **P813**
"retrieved", **P1683** "quotation", **P1065** "archive URL". That maps onto our machinery almost
field for field, and our ADR 0003 is the rule Wikidata runs at roughly a billion statements.

**Micropublications** — Clark, Ciccarese & Goble, *Journal of Biomedical Semantics*, 2014 (title,
journal and year confirmed live via Crossref for DOI `10.1186/2041-1480-5-28`) — model a Claim
with a support graph and **challenge** relations, with direct quotations from source text as
first-class evidence nodes. Our `supports`/`disputes` stance links between claim addresses are
that model in Obsidian markdown. **Nanopublications** (nanopub.net, reachable) separate assertion,
provenance and publication-info graphs — a distinction we implement without naming: provenance
*of the claim* is `[@citekey, locator]` plus the evidence-boundary tag, provenance *of the record*
is `generated: {by, at}` frontmatter plus `verified` events.

**OKF** (Open Knowledge Format), spec at `GoogleCloudPlatform/knowledge-catalog` (8,816 stars,
Apache-2.0, `okf/SPEC.md`), is our declared portability target at v0.2 and llm-wiki-compiler's
bundle exchange format. The convergence is real; the asymmetry is that theirs is an exchange
format while ours is a conformance target, and neither can currently read the other's bundle.

### 8.4 Benchmarks

**rpatrik96/hallmark** (11 stars, MIT, pushed 2026-08-21) — "HALLMARK: Citation hallucination
detection benchmark for ML papers — 2,525 entries, 14 hallucination types, 3 difficulty tiers,
10 baselines including LLMs and verification tools". A labelled corpus with a taxonomy of
hallucination classes and published baselines is the instrument we lack: our 1,330 tests prove
the checks behave as specified, but nothing measures how many real fabrications they catch.

### 8.5 Closed products

**Elicit, scite, llmwikis.org** and **hesreallyhim/awesome-claude-code** have no inspectable
repository of comparable shape — listed for completeness, excluded from evidence-based comparison.

### 8.6 Karpathy's gist — the doctrine everything cites

75 lines, one revision. Three layers (raw, wiki, schema); per-source human-in-the-loop ingest
touching 10–15 pages; `index.md` as the routing device that makes embedding-based RAG unnecessary
at ~100 sources; append-only `log.md` with a grep-parseable `## [date] action | subject` prefix;
periodic lint for contradictions, stale claims, orphans, missing pages and data gaps; query
answers filed back into the wiki so exploration compounds. No code, no schema file, no citation
discipline.

## 9. Tier 4 — the skill-framework baseline

Neither obra/superpowers nor mattpocock/skills is a domain competitor: neither touches literature,
citations, Zotero or a research vault. They are comparable at the layer *below* the domain — how a
skill set is packaged, invoked, governed and tested — and both are in practice this repository's
process substrate rather than its rivals. `mattpocock/skills` ships the `research` skill whose
procedure produced this repo's `research/` notes, and the `wayfinder` method its README names as
where planning happens.

| | obra/superpowers | mattpocock/skills | knowledge-harness |
|---|---|---|---|
| Stars | 276,191 | 232,042 | unpublished |
| License | MIT | MIT | MIT |
| Last push | 2026-08-19 | 2026-08-21 | — |
| Version | plugin v6.3.0 | plugin, version synced by script | v0.1.0 |
| Skills | 14 | 36 across 5 buckets | 9 |
| User-invoked (`disable-model-invocation: true`) | **0 of 14** | **24 of 36** | **7 of 9** |
| Hooks | SessionStart (`startup\|clear\|compact`) | none in-repo | PostToolUse lint, Stop publish gate |
| Tests | 16 directories incl. per-agent suites | none in-repo | 1,330 Python tests |

**superpowers — invocation discipline by rule, and cross-agent conformance testing.** Not one of
its 14 skills sets `disable-model-invocation`; the discipline comes instead from
`using-superpowers`, whose text makes invocation mandatory ("If you think there is even a 1% chance
a skill might apply … you ABSOLUTELY MUST invoke the skill") and is injected by a SessionStart hook
on startup, clear and compact. That is the opposite of our posture. Its `tests/` tree carries
per-agent directories — `antigravity`, `claude-code`, `codex`, `devin`, `hermes`, `kimi`,
`opencode`, `pi` — plus `explicit-skill-requests`, `hooks`, `shell-lint`, `version-bump` and
`writing-skills`. **That is portability conformance testing, and we have none.** It also ships
`scripts/sync-to-codex-plugin.sh` and `package-codex-plugin.sh`, a maintained second-target build.

**mattpocock/skills — governance of the skill set as an artifact.** Its `AGENTS.md` specifies
machinery we lack: **bucket promotion** (`engineering/` and `productivity/` are promoted, and
promoted skills must appear in the top-level `README.md` and in `.claude-plugin/plugin.json`'s
`skills` array — **our `plugin.json` has no `skills` array at all**); a **two-way invocation
contract** (user-invoked skills carry `disable-model-invocation: true` *plus*
`policy.allow_implicit_invocation: false` in `agents/openai.yaml`, documented in
`.agents/invocation.md` — we set only the Claude-side flag); **a docs page per promoted skill**
with four fixed sections and a stable published URL; README and bucket-README sync as a stated
invariant plus `claude plugin validate . --strict` after manifest changes; ADRs under
`.agents/adr/`; and scripts for the skill set itself (`link-skills.sh`, `list-skills.sh`,
`sync-plugin-version.mjs`). Its `CONTEXT.md` is a domain glossary written as term → definition →
`_Avoid_:` alternatives — structurally identical to ours.

Neither framework has a deterministic core: superpowers' discipline is prompt text reinforced by a
session hook, mattpocock's is repository convention enforced by review. Our hooks act on computed
check results rather than injecting instructions.

---

# Part III — The comparison

## 10. Skill by skill

Nine subsections, one per skill. Each states what ours does, names the counterparts that were
read, and compares them on the seam that matters — usually *who is allowed to write*, and *what
happens when a check cannot run*. The summary table is for scanning; the detail is below it.

| Our skill | Closest counterpart | Verdict in one line |
|---|---|---|
| `setup-vault` | medsci `setup-medsci`, claude-obsidian `wiki` | only ours provisions a reference manager; theirs are richer at diagnosing and at vault-shape choice |
| `find-sources` | K-Dense `paper-lookup` (our upstream), medsci `search-lit` | we add a PRISMA-S log and an admission boundary; we lack parallel search and triage |
| `import-source` | **medsci `lit-sync`** | the only other skill joining `.bib`, Zotero and a vault — but it writes the library, and we do not |
| `evidence-conventions` | K-Dense `scientific-writing`, hermes `grounded-citations` | convergent on hash-not-text claim identity and machine-written citations; ours is the only per-line epistemic vocabulary |
| `synthesis-conventions` | hermes `llm-wiki` page thresholds | identical 2+-source rule, reached independently; theirs has scale rules we lack |
| `verify-citations` | Imbad0202 `verification_gate`, medsci `verify-refs` | three registry-backed gates exist; only ours closes a surface |
| `factcheck-draft` | **medsci `check_claim_fidelity.py`**, pedrohcgs `verify-claims` | ours is LLM where theirs is code; ours never blocks where two of theirs do; ours is the only one that records what it did *not* check |
| `project` | WenyuChiou `gap-to-topic`, medsci `manage-project` | ours frames a question; theirs gate whether it is worth asking, and track the project as an artifact |
| `publish` | medsci `sync-submission`, pedrohcgs `replication-package` | ours is the only verification boundary; theirs are whole submission-integrity surfaces |

### 10.1 `setup-vault`

**Ours.** Asks for a destination and separdid ate consent for read-only CI and a scheduled
write-capable workflow, then runs one `scaffold` command with only the consented flags and reports
its exact printed paths. Runs `doctor` after, reporting every probe rather than only failures.
Provisions companions with per-item consent: `kepano/obsidian-skills` is scriptable
(`claude plugin install`), while Better BibTeX and the whole-library auto-export are human-only
Zotero wizard steps the skill explains but never performs — "never say an auto-export exists until
doctor reports `autoexport` MATCHED".

**Counterparts read.**

- **medsci `setup-medsci`** — a *read-only diagnostic*: verifies Python, R, Node, Claude Code, Git,
  Zotero and configured MCP servers, prints a pass/fail table with links to the right setup doc,
  and installs nothing. "Intentionally read-only so that a doctor can run it safely without
  worrying about breaking their system."
- **claude-obsidian `wiki`** — orchestration plus setup, with a strict data/code separation
  ("treat the installed product as code and the selected user vault as data. Never use the
  plugin/product root as a vault"), vault resolution in a fixed order (`--vault`, env var, nearest
  `.claude-obsidian.json`, then an unambiguous initialized vault) that **fails closed when
  selection is missing or ambiguous**, dry-run-by-default setup commands, and no network egress in
  the baseline. Its `wiki-mode` sibling then offers four filing methodologies.
- **gbrain `setup`** — auto-provisions Supabase or PGLite, injects AGENTS.md, performs a first
  import. `mutating: true`.
- **swarmvault `init`/`quickstart`** — plus `install --agent` writing rules and MCP registration
  for 40+ agent tools.
- **llmwiki `profile init` / `template init`** — scaffolds a *validated typed profile*; an invalid
  profile fails closed.

**The seam.** Everyone scaffolds; the difference is what they refuse to do. Ours refuses to
perform the Zotero wizard steps and refuses to claim an auto-export exists before `doctor` says
so. claude-obsidian refuses to guess a vault. medsci refuses to install anything at all.

**Ahead:** ours is the only setup skill in the comparison that provisions a *reference manager* and
verifies it through a probe (`zotero`, `bbt`, `autoexport`). **Behind:** we have no vault-shape
choice (claude-obsidian's four methodologies), no typed-profile validation (llmwiki), no agent-rule
installation for other tools (swarmvault), and no runtime diagnostic beyond the vault — medsci
checks R, Node and MCP servers; our `doctor` checks the vault, Zotero and git.

### 10.2 `find-sources`

**Ours.** A vendored fork of K-Dense `paper-lookup` (verified: 16 files, header-only additions,
zero removals at pinned SHA `336c4f8`), covering 11 databases with per-API reference files and
stdlib scripts. On top of that it adds two things upstream lacks: every completed query
gets an append-only `search-log` line with the query **as run** and the literal hit count, and every
candidate a person declines gets a `--not-admitted` line with a reason code. It terminates at
admission — it never writes `literatures/`, never invents a citekey, and never decides admission.

**Counterparts read.**

- **K-Dense `paper-lookup`** (our upstream) — the strongest single retrieval artifact found:
  documented "these APIs fail with HTTP 200" hazard sections per database, count reconciliation
  that fails visibly, credential redaction because the fetched URL *is* the credential, and a
  mandated output format carrying endpoint, parameters and access date.
- **medsci `search-lit`** — PubMed, Semantic Scholar, bioRxiv/medRxiv, described as
  "anti-hallucination — every reference verified via API before inclusion", generating BibTeX and
  shipping `check_doi_record_match.py`. It verifies *at search time*, folding into one skill what
  we split between `find-sources` and `verify-citations`.
- **pedrohcgs `lit-review`** — search plus synthesis in one: thematic clustering, gap
  identification, a written review with BibTeX-ready citations, `--no-verify` to skip checking.
- **Imbad0202 `deep-research`** — a 13-agent pipeline with a `source_verification_agent`, PRISMA
  mode and a post-research monitoring agent.
- **nvk Research** — 5, 8 or 10 parallel agents by depth, with named perspectives.
- **cookjohn `cnki-skills` / `gs-skills`** — CNKI and Google Scholar, including export to Zotero.

**The seam.** Ours is the only one that treats *what was searched* as durable evidence in its own
right. medsci verifies references during search; we defer verification to a separate deterministic
pass and instead record the search itself. Both are defensible; ours produces a PRISMA-S trail a
methods reviewer can reconstruct, theirs produces cleaner references sooner.

**Ahead:** the append-only search log with query-as-run and zero-hit results treated as real
findings; the hard admission boundary; the honest reporting table that distinguishes "completed,
zero hits" from "could not complete". **Behind:** no parallel search agents, no triage matrix
(WenyuChiou `literature-triage-matrix`), no candidate queue, no Chinese-language corpus, no
screening ritual, and no monitoring agent for new literature after the search.

### 10.3 `import-source`

**Ours.** The projection step after a human admits an item to Zotero. `import-note` renders
`literatures/CITEKEY.md` from Zotero into a managed region, leaving free prose below untouched;
re-import is a render-first comparison so an unchanged projection prints `NOOP` and writes
nothing. The catalog "answers to no judgment of yours" — nothing downstream can hold it back. Then
identifier discovery, registry-first dedup against `synthesis/index.md`, integration into the
synthesis layer with stance links, and exactly three surgical per-claim holds (contradiction,
low/absent confidence, schema violation) each filed as a finding naming that one claim. Web
sources get a Wayback snapshot at import, because "rescue is impossible after the fact".

**Counterparts read.**

- **medsci `lit-sync`** — the only other skill joining a `.bib`, the Zotero library *and* Obsidian
  literature notes, then extracting concept notes at an accumulation threshold. It honours an
  existing vault layout rather than renaming folders, and defaults to English folders for a new
  vault. Its sibling `obsidian-paper-vault` enters the same folders from the PDF side, and the two
  are explicitly designed not to overwrite each other.
- **claude-obsidian `wiki-ingest`** — scope and budget agreed before processing; SHA-256 preflight
  against `.raw/.manifest.json`; a compilation-value gate where a no-op is legitimate; a five-page
  read budget; read-only parallel workers; one transaction per batch landed through
  `inspect` → `apply --approved-plan-sha256`; and the strongest untrusted-source rules in the
  comparison.
- **gbrain `ingest` + `brain-ingest-gate`** — "a bare cp/mv into the brain repo is a bug";
  registry-first entity resolution before any similarity score; a read-the-top-hit dedup tree.
- **hermes ingest** — orientation first, page thresholds, raw-body `sha256` skip-if-identical, an
  ask-first gate at 10+ pages touched.
- **SamurAIGPT** — a 10-step ingest whose hash is computed and never compared.
- **nvk** — ingest captures only; compilation is deferred to a separate verb.

**The seam.** Every other product ingests *arbitrary documents*; ours projects *an item someone
already accepted*. That single difference cascades: we need no capture adapters, no format
conversion, no egress consent and no untrusted-content rules in this skill, because the input is a
Zotero record rather than fetched text. It also means we cannot ingest anything a person has not
first put in Zotero — which is the point, and the cost.

**Ahead:** the note is a render, not an LLM write, so re-import is a mechanical no-op and drift is
lintable; holds are per-claim rather than per-source, so a contradiction never blocks a catalog;
the web-archive capture happens at import rather than being detected as missing later.
**Behind:** no staged transaction with an approval hash (claude-obsidian), no ingest budget agreed
up front, no dedup decision tree at entity level (gbrain), no guided one-source-at-a-time session
(swarmvault), no format breadth, and no untrusted-source hardening for the day extracted PDF text
reaches an adjudicator.

### 10.4 `evidence-conventions`

**Ours.** The Iron Law — "no claim enters a draft without a verified source first" — plus a
one-line claim grammar: evidence-boundary tag, text, `[@citekey, locator]`, optional fields, and a
`^c-XXXXXXXX` anchor derived from stable content (a Zotero annotation key, else a quote hash) so
re-rendering never breaks an existing link. Quotes ride as blockquotes below the claim line.
Synthesis claims add `[confidence::]` and stance links targeting another *claim link*, never a
bare note. Retirement is a transition record, never a deletion. `failed-verification` markers are
CLI-owned. An 18-code reason registry governs every durable finding. A rationalizations table
answers "I'll cite it later", "it's common knowledge", "the abstract said so".

**Counterparts read.**

- **K-Dense `scientific-writing`** — five registries with inline markers
  `[claim:C001] [evidence:E001,E002]`, and a `claim_text_sha256` field validated against a SHA-256
  regex (`audit_claims.py:28,99`): the record stores a hash of normalised claim text, not the text.
  Evidence counts only when `verification.get("source_opened") is True` (`audit_claims.py:67`), and
  "mark the source verified only after a named human completes the check"
  (`evidence_workflow.md:57`).
- **hermes `grounded-citations`** — a ledger owns the `url → [n]` map "so the model only ever emits
  small integers it was handed"; sources are registered *at retrieval time* ("registering later,
  from memory, is the failure mode this skill exists to prevent"); cite-while-drafting with at most
  3 ids per sentence, per sentence not in a dump; the Sources block is rendered mechanically from
  the ledger; own-knowledge claims get no citation and conflicting sources are presented as both
  readings.
- **claude-obsidian `provenance.md` + ledgers** — controlled vocabularies for authority, review
  state, claim assessment, evidence relation, confidence and risk; contradictory evidence
  preserved; "`unsupported` is the canonical no-data state"; high-risk acceptance needs two
  independent sources, counted by union-find.
- **Pratiyush** — `confidence` as a 4-factor score, `lifecycle` in a closed set, `entity_type`
  declared, "frontmatter is authoritative", "no silent overwrites".
- **hermes `llm-wiki` SCHEMA** — a closed tag taxonomy where a new tag must be added to the schema
  before use.

**The seam.** Three products and we agree that the machine, not the model, writes the citation
apparatus — theirs a ledger or a registry, ours the CLI. Two of us agree that a claim record
should store a *hash* of its text rather than the text. Where we differ is what the per-line tag
means: K-Dense's `[claim:]`/`[evidence:]` tags *linkage*, ours tags *epistemic status*
(quote / paraphrase / inference / open-question). Nobody else makes the reader's epistemic
commitment a required, lintable field.

**Ahead:** per-line evidence-boundary tags; a global claim address that works outside the draft;
deprecation as a transition record with required fields; a frozen reason-code registry.
**Behind:** no closed tag taxonomy; no declared entity-type vocabulary; no independence counting;
no "a named human opened the source" precondition on counting evidence; and no rule that
conflicting sources must both be presented, which hermes states explicitly.

### 10.5 `synthesis-conventions`

**Ours.** The synthesis layer asserts arrangement, not evidence, which is why it is freely
rewritable — what never moves is the evidence underneath, so every arranged claim keeps citing its
source claim link. Orientation before creating anything. A page earns existence at **two or more
sources on the same topic** — "the only threshold". At least two outgoing wikilinks or it is a
stub. Creating a note is not complete until it is registered in `synthesis/index.md`.

**Counterparts read.**

- **hermes `llm-wiki`** — "Create a page when an entity/concept appears in **2+ sources** OR is
  central to one source; add to existing when already covered; DON'T create for passing mentions;
  **split** above ~200 lines; **archive** when fully superseded." Plus at least two outbound
  wikilinks *and* a backlink check, mandatory index registration with a total-page count, index
  splitting above 50 entries per section and a `_meta/topic-map.md` above 200, and log rotation at
  500 entries.
- **claude-obsidian** — a compilation-value gate: create or expand only when the source adds
  durable synthesis, navigation, a decision or a reusable connection; "do not paraphrase merely to
  create pages", and a no-op is a legitimate outcome.
- **medsci `lit-sync`** — concept notes extracted only "when enough literature accumulates".
- **llmwiki** — phase 1 extracts the full concept universe across all changed sources before any
  write, then merges cross-source concepts into one page deterministically.
- **nvk Compile** — classifies each into concept (bounded idea), topic (broad theme) or reference
  (curated list), and repairs bidirectional links.

**The seam.** Our 2+-source threshold and hermes's are identical, arrived at independently. The
substantive difference is *what a synthesis claim points at*: ours points at a claim address
inside a literature note, theirs at a page or a source file. That is why our synthesis layer can
be rewritten freely — the evidence is not in it.

**Ahead:** stance links to claim addresses; the evidence/arrangement separation that makes
rewriting safe. **Behind:** no page-splitting threshold, no archival rule, no backlink check, no
index-scaling rule, no log rotation, no alias handling, no deterministic cross-source merge, and
no page-type classification.

### 10.6 `verify-citations`

**Ours.** A thin wrapper over the CLI's `verify` verb — ten checks, four-state results, closing
sets per surface. It ships no mechanics of its own: orientation, run the verb, report results
**grouped by check id**. It explicitly does not act as the gate even when asked whether a gate
would pass, and it never files a finding itself because `verify` already does. Only four check ids
mint a `verified` event on MATCHED, and the skill is forbidden from claiming otherwise.

**Counterparts read.**

- **Imbad0202 `verification_gate` + `/ars-citation-check`** — four resolvers in parallel
  (Crossref, OpenAlex, Semantic Scholar, arXiv), the same four status names as ours, a persistent
  SQLite cache whose `_TTL_DAYS = 90` is annotated in source as "a guess, deferred for empirical
  tuning" (`verification_cache.py:32,35`) and whose staleness flag is advisory-only, existing "so
  stale evidence is visible exactly where it is used" (:39-40); entries with
  `obtained_via == "manual"` skip all resolvers (`verification_gate/__init__.py:248`); and
  detection is always-on with blocking only under an opt-in strict `terminal_policies` value,
  enforced by formatter REFUSE rules (`formatter_agent.md:378,430-431`). Above it sits the integrity-signal contract separating
  `deterministic_fact` / `heuristic_advisory` / `process_attestation`, with `check_status`
  independent of `finding`.
- **medsci `verify-refs`** — audit-only against PubMed and CrossRef (its siblings
  `preflight_gate.py` and `pre_submission_gate.sh` do halt, but at submission, not here), writing
  `qc/reference_audit.json`, explicitly not writing to `references/` or `refs.bib`, with an
  `--offline` mode that extracts and classifies without API calls. Its companion `manage-refs`
  owns the *writing* half — citation-key validation, journal-CSL rendering, marker conversion,
  Zotero CWYW field-code injection — with 12 scripts including `check_citation_keys.py`,
  `check_reference_duplication.py`, `check_xref.py` and a `pre_submission_gate.sh`.
- **pedrohcgs `validate-bib`** — structural by default (missing, unused, malformed, typo
  candidates, across `@key` and `[@key]` forms); `--semantic` adds duplicate-entry drift detection,
  Crossref DOI verification and per-file style consistency; reports to `quality_reports/`.
- **bibverify** — DOI-first, and it explains *why* a lookup source was chosen
  (`rank_lookup_sources`) and diffs original against updated entries (`explain_update_diff`).
- **llmwiki `lint`** — validates every `^[file.md:42-58]` marker, classing a missing source file as
  an error attributed to hallucinated filenames, and `eval` scores citation precision and a
  `claim_level_citation_rate` against thresholds.

**The seam.** Three registry-backed deterministic gates exist — ours, Imbad0202's, medsci's — and
the split between them is what happens on a bad result. medsci's `verify-refs` is audit-only by
design, and the halting gates live downstream at submission rather than on this check. Imbad0202
detects universally and blocks only under opt-in strict policy. Ours closes a commit and a
session-Stop surface by default, and treats UNREACHABLE as holding the publish gate rather than
passing it.

**Ahead:** the only one whose result closes a surface; the only one checking quote text against a
stored selector; update-notice classes with reinstatement; a `disputed-claim` check that surfaces
counter-evidence against a claim being relied on.
**Behind:** no verification cache (Imbad0202's 90-day TTL, medsci's `--offline` mode); no
explanation of resolver choice (bibverify); no duplicate-entry detection (pedrohcgs, medsci
`check_reference_duplication.py`); no cross-reference QC between manuscript and rendered output
(medsci `check_xref.py`); no citation-coverage metric (llmwiki); and no separation of *a check ran*
from *what it found* (Imbad0202).

### 10.7 `factcheck-draft`

**Ours.** Factored verification at draft→review. Selection is deterministic — the CLI's `factcheck`
subcommand ranks inference and paraphrase claims lacking a `verified` event first, boosts
contested-adjacent claims, and puts quote claims last because the deterministic checker already
covers them; ties keep document order; anything past `--cap 30` lands in `skipped`. Per claim the
judgment differs by tag: quote fidelity means *fair use in context*, paraphrase means direction,
magnitude, population and certainty, inference means "is this genuinely an inference and a
reasonable step". MATCHED writes nothing, because LLM judgment never mints a `verified` event.
Everything else is a finding carrying the claim's `text_hash`, so an edit reopens it and an
unchanged retry does not duplicate it. The skipped set gets **one** finding naming everything the
cap left unchecked. It never blocks anything.

**Counterparts read.**

- **medsci `check_claim_fidelity.py`** — the same question answered in *code*, with three probes
  ordered by checkability: `CITED_QUOTE_ABSENT` (major — "the words are in that document or they
  are not", and this is where a quote-operator inversion lives, a manuscript quoting "only if"
  where the source said "so long as"), `ATTRIBUTION_UNSUPPORTED` (prompt-level, firing only when
  **not one content word** of the attributed span appears in the source in any morphological
  form), and a third tier. Its origin is recorded: a manuscript sentence read "the field has begun
  to offer the chair [41]"; the cited work uses "chair" zero times and "advocate" four. "Nothing in
  the toolkit could have" caught it.
- **pedrohcgs `verify-claims`** — Chain-of-Verification per Dhuliawala et al. 2023, spawning a
  `claim-verifier` agent **in a forked context that never sees the draft**, classifying claims
  supported / contradicted / unverifiable, **fail-closed by default** with an explicit
  `--no-fail-closed` downgrade.
- **gbrain `fact-check`** — 6-level confidence, checked "against live citable sources (never
  training data)", with PRODUCER ≠ VERIFIER (re-derive via a different query path) and
  AFFILIATION ≠ AUTHORSHIP, and **delivery hard-blocked** on unsupported claims.
- **hermes `grounded-citations`** — `sources.py verify <draft>` exits non-zero, failing any draft
  whose cited sources carry no evidence.
- **claude-obsidian `agents/verifier.md`** — a fresh-context, read-only verifier subagent.

**The seam.** This is the skill where we are most clearly *behind*, and the gap has three parts.
Theirs is deterministic where ours is LLM judgment (medsci). Theirs isolates the verifier's context
where ours runs in the drafting session (pedrohcgs, claude-obsidian). Theirs blocks delivery where
ours never blocks (gbrain, pedrohcgs, hermes).

**Ahead, and it is one thing but a real one:** ours is the only one that records what it did *not*
check. The `budget-cap` finding names every claim the cap excluded, so silence can never read as
clearance. Deterministic selection also means the drafting context cannot choose which of its own
claims get scrutinised.
**Behind:** no code-level fidelity probe; no context isolation; no re-derivation rule; no
delivery gate; and no quote-operator-inversion detection, which is a failure class we do not model
at all.

### 10.8 `project`

**Ours.** The entry point for the project flow. Orient every time — read `synthesis/index.md`,
recent `log/` entries, the project's own files — then drain the review inbox, reporting the
unacknowledged count and the *oldest* entry's date, leading with it when it has been sitting.
Surface the trust tier of every cited citekey. For a new project, elicit exactly four elements
inline — the question, scope bounds, expected source types, success criteria — and refuse to
proceed with any missing. For an existing one, gap analysis sorts the question into covered /
contested / missing, with contested surfacing the disputing claim links explicitly so
disconfirmation is never folded into "covered". It orchestrates and routes; it does none of the
work itself.

**Counterparts read.**

- **WenyuChiou `gap-to-topic`** — a three-gate go/no-go dossier: is the gap open? is it a
  contribution? is it feasible? It "stops short of the verdict, handing the worth-it call back to
  the researcher and advisor", and downstream skills filter to
  `verdict in {conditional-go, go}` — 1 candidate auto-fills the design brief, 2+ asks the user,
  0 halts with "nothing to frame". Provenance flows forward in frontmatter (`source`,
  `gap_verdict`).
- **medsci `manage-project`** — scaffold, status, sync-memory, checklist, timeline: project memory
  files, progress tracked across phases, pre-submission checklists and **backwards** submission
  timelines.
- **Imbad0202 `academic-pipeline`** — a 10-stage workflow where "each stage completion requires
  user confirmation before proceeding" (SKILL.md:28), with an opt-in
  `resume_from_passport=<hash>` for continuing in a fresh session from a recorded stage (:23).
- **pedrohcgs** — `research-ideation`, `interview-me`, `triage-inbox`, plus `checkpoint`,
  `compress-session`, `context-status` and `promote-memory` for session continuity.
- **nvk Thesis mode** — thesis-driven investigation as a distinct mode of Research.

**The seam.** Ours makes the *review queue* the thing you orient against; theirs make the
*project* the thing. Both matter, and only one of us does each. Our inbox drain with an
oldest-first rule is a guard against a warn queue nobody reads; nobody else has that. Their project
memory, checklists and backwards timelines are artifacts we do not produce.

**Ahead:** the review-inbox drain with age prominence; trust tiers surfaced per cited citekey;
gap analysis that forces contested evidence into the open rather than letting it read as covered.
**Behind:** no gate on whether the question is worth asking (WenyuChiou); no project memory,
checklist or timeline (medsci); no resumable hashed artifact (Imbad0202); no session compression or
checkpointing (pedrohcgs); no thesis mode.

### 10.9 `publish`

**Ours.** Explicitly invoked only. Drain the inbox first, counting blocking-class entries
separately, and say that count out loud before anyone chooses. Run the gate. Present exactly three
pre-publication dispositions — `mark-published`, `park`, `keep-draft` — and never pick. Arming is
separate from publishing: `arm-publish` writes the flag the Stop hook reads, and a refusal
**leaves the gate armed** so the session keeps being held. After publication only two dispositions
exist, `mark-corrected` and `mark-withdrawn`, and the original tag is never deleted — a correction
adds a tag. Deletion requires the person to type `discard`; "anything less — 'drop it', a
nodded-through summary — is not consent". The one bypass is `--bypass`, recorded in the inbox as
an open finding: "explain that it is recorded, not forgiven, before writing it".

**Counterparts read.**

- **medsci `sync-submission`** — treats `submission/{journal}/` as derived output and records
  whether it is current, stale or frozen, with roughly 30 scripts: `blind_sweep.py`,
  `check_asset_anonymization.py`, `check_credit_integrity.py`, `check_wordcount_cap.py`,
  `cross_document_n_check.py` (the same participant count across documents),
  `check_cross_artifact_stale.py`, `cover_letter_drift_check.py`, `check_portal_field_residue.py`,
  `figure_portal_readiness_check.py`, `preflight_gate.py`. Several ship a paired `_challenge`
  fixture directory.
- **pedrohcgs** — `replication-package`, `audit-reproducibility`, `submission-disclosures`,
  `disclosure-check`, `respond-to-eval`, `deploy`.
- **Imbad0202** — `/ars-full` finalize with `verify_submission_package.py`, `/ars-disclosure`,
  `/ars-rebuttal-audit`, and formatter REFUSE rules that gate output.
- **gbrain `publish`** — "share brain pages as beautiful password-protected HTML with zero LLM
  calls", `mutating: false`: sharing, not a boundary.
- **swarmvault `review`/`candidate`** — generic staged approval, not tied to a claim.

**The seam.** "Publish" means three different acts in this pool. For gbrain it is *sharing*. For
medsci, pedrohcgs and Imbad0202 it is *assembling a journal package*. For us it is *crossing a
verification boundary and recording a lifecycle*. Only ours is a gate; only theirs produce a
submittable artifact.

**Ahead:** the armed fail-closed Stop gate bounded at 8 blocks with a recorded, non-forgiving
bypass; a correction lifecycle where tags are additive and a published-drift lint watches them;
typed-consent deletion; the refusal to let a disposition be inferred from a nodded-through
summary. **Behind:** we produce no submission package at all — no anonymisation sweep, no
word-count cap, no cross-document consistency check, no cover-letter drift check, no disclosure
closeout, no replication package, no rendered output in any journal format.

## 11. What the field has that we lack

Grouped by capability class; each entry names where the capability was read.

**Retrieval and query.** We ship no query verb and no retrieval index; a person reads the vault
through Obsidian, and a skill orients by reading `synthesis/index.md` and `log/`. Everything else
here has one — BM25 (claude-obsidian, swarmvault), hybrid semantic (llmwiki), pgvector (gbrain),
index-mediated with explicit depths (hermes, nvk), plus obra/knowledge-graph standalone and
zotero-mcp's `zotero_semantic_search`. See §6 for each.

**Agent-facing service surfaces.** We expose a CLI only. Comparables: llmwiki `serve` (MCP
exposing ingest, compile, query, lint, read, status, eval, context-pack, OKF) plus a TypeScript
SDK; swarmvault `mcp`; research-hub exposes CLI, MCP, REST and a dashboard over the same core;
zotero-mcp with 51 tools; bibverify's MCP server.

**Evaluation, calibration and benchmarks.** We have 1,330 unit tests and no evaluation harness.
llmwiki scores citation coverage, precision and a claim-level citation rate against thresholds
(§6.5); Imbad0202 ships gold, held-out, calibration and bakeoff sets with a threshold gate (§6.2);
gbrain ships routing evals for 41 of 71 skills; DeepPaperNote ships `evals/`; and **HALLMARK**
(§8.4) is a labelled hallucination benchmark we could run against our suite tomorrow.

**Deterministic claim-fidelity checking, and token-ordered quote matching.** medsci answers "does
the source say what the sentence claims" in code rather than by LLM adjudication (§6.1, §10.7);
ours is LLM judgment. On quote matching the gap is narrower than it first appears: our
`selectors._norm_with_map` already normalises NFKC drift, soft hyphens, line-break hyphenation and
whitespace against extracted PDF text, but matches contiguously, so a line number or a superscript
landing mid-sentence still breaks it. medsci's token-ordered subsequence match does not.

**Staged transactions and approval binding.** Our writes land immediately; the review inbox records
after the fact. claude-obsidian binds an approval hash to a reviewed plan (§6.4), swarmvault stages
approval bundles and a candidate queue (§6.7), llmwiki holds pages in `candidates/` under a
fail-closed policy (§6.5).

**Independence counting.** claude-obsidian collapses sources sharing an origin, content hash or
declared independence key so they cannot corroborate each other (§6.4). Our `disputes` links record
disagreement; nothing counts independence.

**Fresh-context verification.** claude-obsidian and pedrohcgs both isolate the verifier from the
drafting context (§6.4, §6.8). Ours runs in-session and mitigates only by selecting claims
mechanically.

**Untrusted-source hardening in the ingest path.** claude-obsidian states the rules (§6.4);
Imbad0202 ships probes and boundary checks that test them (§6.2). Our `find-sources` carries the
rule for search responses; `import-source` carries none, because its input is a Zotero projection
rather than fetched text — a defensible boundary that stops holding the moment extracted PDF text
reaches an adjudicator.

**Destructive-change guards.** swarmvault's 25% shrink guard is the only circuit breaker of its
kind found (§6.7). We have prepublication rollback and append-only lints, but nothing that refuses
an aggregate loss.

**Structural lints we do not run.** Orphan pages, broken wikilinks, index completeness, page size,
tag-taxonomy conformance, stale content and log rotation: specified by hermes (an 11-check lint),
implemented by claude-obsidian's lint CLI, SamurAIGPT's `health.py`, llmwiki's `lint` and
swarmvault's `lint`. Our lints cover append-only surfaces, claim immutability, published drift,
screening state, disputed claims, web archives and the evidence layer — nothing about the link
graph between synthesis pages.

**Graph analysis.** swarmvault (§6.7), gbrain's zero-LLM typed-edge extraction on every page
write, llmwiki's wikilink-graph expansion, and obra/knowledge-graph. We build no graph and compute
no backlinks.

**Ingest breadth and capture.** We ingest exactly one thing: a Zotero item. swarmvault covers
roughly 30 document formats plus media and transcripts; SamurAIGPT ~20 via markitdown;
claude-obsidian capture adapters plus `defuddle`; nvk collections and private adapters; medsci a
folder of PDFs.

**Maintenance and scheduling.** gbrain's `dream` cycle (§6.3), swarmvault `watch` plus git hooks,
llmwiki `refresh --stale`, nvk `Refresh --due`, Pratiyush's GitHub Action. We ship a scheduled CI
template and `backfill-selectors`; no maintenance cycle, no staleness-driven repair loop.

**Source freshness against live URLs.** nvk `Refresh` re-fetches source URLs and classifies change
as cosmetic, additive or contradictory under a human gate; hermes re-hashes raw bodies; llmwiki
computes fresh/stale/orphaned/unverified from recorded hashes. Our `staleness` verb compares the
bibliography export with the Zotero library, and `web-archive` detects a missing or dead snapshot
— neither re-reads a live source for content change.

**Deletion of ingested material.** nvk `Retract` is user-authoritative, overrides raw immutability
and append-only rules, dry-runs by default, deletes the raw source and unsupported derived claims,
and verifies. We never delete: notes deprecate. That is deliberate, but we have no answer for a
source that must be expunged.

**Contradiction machinery beyond flagging.** gbrain measures and grades contradictions and emits
paste-ready resolutions it never applies (§6.3); swarmvault dashboards them; llmwiki holds
contradicted pages. We record `disputes` links and a `disputed-claim` check — no probe, no
severity, no temporal reasoning.

**Maturity and confidence vocabularies.** Pratiyush declares page lifecycle and a computed
confidence (§6.11); hermes makes a missing confidence field a lint signal (§6.6); llmwiki holds
low-confidence pages by default (§6.5). Our trust tier is derived from check results; our
`confidence` is a per-claim field on inference claims only.

**Question-worth gating.** WenyuChiou's `gap-to-topic` (§6.13). Our `project` frames a question
and never asks whether it should be asked.

**Filing methodology.** claude-obsidian `wiki-mode` supports Generic, LYT, PARA and Zettelkasten
and suggests destinations. Our vault layout is fixed.

**Multi-agent orchestration.** Imbad0202 runs 12- and 13-agent pipelines, a 5-seat review panel
and cross-model verification against Codex; pedrohcgs runs multi-agent review with a forked-context
verifier; nvk launches 5, 8 or 10 parallel research agents; claude-obsidian runs read-only parallel
workers under an orchestrator; gbrain has `minion-orchestrator`. Our skills are single-threaded.

**Writing, reviewing and submission.** Imbad0202: 11 writing modes, 6 paper types, 5 citation
formats, bilingual abstracts, LaTeX/DOCX/PDF output, rebuttal audit, AI-disclosure mode.
pedrohcgs: `compile-latex`, `qa-quarto`, `slide-excellence`, `proofread`, `review-paper`,
`seven-pass-review`, `respond-to-eval`, `grant-proposal`, `replication-package`,
`audit-reproducibility`, `data-management-plan`, `power-analysis`, `disclosure-check`,
`submission-disclosures`. medsci: `write-paper`, `revise`, `peer-review`, `render-pdf-doc`,
`present-paper`, `fill-icmje-coi`. anthropics/skills supplies the document renderers. We have no
drafting skill, no format conversion, no reviewer simulation, no rebuttal or disclosure support,
no replication packaging.

**Submission-integrity checks.** Distinct from drafting, and on our own axis — these are
deterministic checks, not writing features. medsci `sync-submission` treats `submission/{journal}/`
as derived output and records it as current, stale or frozen, with roughly 30 scripts including
`blind_sweep.py` and `check_asset_anonymization.py` (blinding), `check_wordcount_cap.py`,
`cross_document_n_check.py` (the same participant count asserted across every document),
`check_credit_integrity.py`, `cover_letter_drift_check.py`, `check_cross_artifact_stale.py`,
`check_portal_field_residue.py`, `figure_portal_readiness_check.py` and `preflight_gate.py`,
several with paired `_challenge` fixture directories. Imbad0202 adds `verify_submission_package.py`
and formatter REFUSE rules that withhold output under a stale policy evaluation. pedrohcgs adds
`audit-reproducibility` and `disclosure-check`. We have none of this: our publish gate checks the
citations and the lifecycle, and nothing checks the artifact that leaves the building.

**Reference rendering and cross-reference QC.** medsci splits its reference handling by direction —
`verify-refs` only reads, `manage-refs` writes — and the writing half carries machinery we have no
equivalent for: journal-CSL pandoc rendering, `[N]` ↔ `[@key]` marker conversion, native Zotero
CWYW field-code injection, `check_reference_duplication.py`, and `check_xref.py` for
manuscript ↔ DOCX cross-reference QC. Our split runs along the same principle — one owner writes —
but on a different seam, and we render nothing.

**Systematic-review apparatus.** Imbad0202 ships a PRISMA mode, protocol template,
systematic-review toolkit, risk-of-bias agent and meta-analysis agent; medsci ships
`meta-analysis`, `ma-scout` and `check-reporting`; htlin222/prisma-automation generates the flow
diagram; LatteReview automates screening with multi-agent reviewers. We have PRISMA-style
screening states and a PRISMA-S search log — no flow diagram, no risk-of-bias instrument, no
meta-analysis.

**Machine-side admission screening.** research-hub screens candidates before they enter the
corpus: identifier resolution, Crossref corroboration, a **predatory-venue denylist** and a
metadata-integrity layer, all fail-closed (§6.15). Our admission boundary is deliberately human,
but that means nothing mechanical stands between a person and admitting a paper from a predatory
venue — we run no venue check at any point.

**Quarantine as a recoverable state.** research-hub quarantines rather than rejecting, with
`list`/`show`/`restore` verbs, a transient-versus-permanent reason split, and a **recheck marker**
on papers admitted while a check was only transiently unavailable, so a later run re-verifies
them. Our nearest equivalent is a finding plus an acknowledgment; we have no "admitted pending
re-verification" state, and an UNREACHABLE result leaves no durable marker that says *come back to
this one*.

**Reporting-guideline compliance.** medsci `check-reporting` covers 49 guidelines with 6 scripts
and 7 tests, and `fill-protocol`, `fill-icmje-coi` and `write-protocol` sit beside it. We have no
notion of a reporting guideline at all.

**Research-data reproducibility.** medsci `version-dataset` builds a deterministic content-hash
manifest for a dataset and `generate-codebook` emits a citable data dictionary. We hash
attachments (`fixity-sha256`) and nothing else; a dataset a claim depends on has no identity in
our vault.

**Bibliometric and venue signals.** paper-qa ships `journal_quality.py`; zotero-mcp surfaces Scite
supporting/contrasting/mentioning tallies; OpenAlex `cited_by_count` is available to several. We
record no venue-quality or citation-count signal.

**Zotero write-back.** Our client is read-only by design. zotero-mcp writes — `zotero_add_item`,
`zotero_update_item`, `zotero_batch_update`, `zotero_attach_file`, `zotero_create_collection`,
`zotero_set_item_collections`, `zotero_manage_note`, `zotero_create_annotation`,
`zotero_update_annotation`, `zotero_delete_annotation`, `zotero_delete_item`,
`zotero_merge_duplicates` — as do WenyuChiou's `zotero-skills` and K-Dense's `pyzotero`, and
medsci's `lit-sync` writes literature into the library. A deliberate boundary for us, but a real
capability the field has.

**PDF and annotation reach.** zotero-mcp reads PDF pages, outlines and page layout, extracts and
synthesizes annotations and returns item full text; K-Dense `liteparse` parses locally with
per-token bounding boxes. We resolve attachment paths and normalize Better BibTeX annotations into
claims, with `pypdf` only as an optional extra.

**Duplicate detection over the reference library.** zotero-mcp `zotero_find_duplicates` and
`zotero_merge_duplicates`; WenyuChiou `zotero-library-curator`; gbrain's registry-first dedup gate.
Our dedup question is about synthesis topics, not Zotero items.

**Interchange and export.** llmwiki exports and imports OKF bundles and exports JSON, JSON-LD,
GraphML, Marp and `llms.txt`; swarmvault exports `llms.txt`, `llms-full.txt`, JSON-LD, manifests,
per-page siblings, Canvas and Neo4j. We conform to OKF structurally but export no bundle.

**Viewers and dashboards.** llmwiki `view`; swarmvault `graph serve` workbench plus dashboards for
recent sources, reading log, timeline, research map, contradictions and open questions; Pratiyush's
serve scripts. We ship two Obsidian Bases and rely on Obsidian.

**Session continuity and context economy.** swarmvault chat transcripts, context packs and task
ledgers; pedrohcgs `checkpoint`/`compress-session`/`promote-memory`; gbrain's zero-LLM
`context_pack` verb; Pratiyush's hot cache, capped memory files and log auto-archive (§6.11). We
have the log and the review inbox — no session artifact, no log rotation, and no token budget on
any orientation read.

**Skill-set governance and portability.** mattpocock's bucket promotion, `plugin.json` `skills`
array, two-sided invocation contract, per-skill docs pages and manifest validation; superpowers'
per-agent conformance test suites and second-target build scripts; nvk's `.skills/registry.json`
per-topic allowlists; llmwiki's Ed25519-signed template distribution; swarmvault's installers for
40+ agent tools. We ship a plugin manifest and a marketplace entry.


## 12. What we have that the field does not

Two entries carry qualifications, stated inline rather than deferred.

- **Registry-verified existence as a closing gate, not a report.** Imbad0202 and medsci also verify
  against live registries; only we make the result close a commit and a session-Stop surface.
  medsci's reference check is audit-only and its halting gates are CLI preflights at submission
  with no hook enforcement (§6.1); research-hub gates corpus admission, not the draft (§6.15);
  Imbad0202 blocks only under an opt-in strict policy.
- **Per-claim evidence-boundary tags.** `quote` / `paraphrase` / `inference` / `open-question` as a
  required, lintable per-line vocabulary. No comparable tags *epistemic status* per line; K-Dense
  `scientific-writing`'s `[claim:C001] [evidence:E001,E002]` markers are per-line but tag
  claim-to-evidence linkage, which is a different thing.
- **Block-addressed claim links with typed stance links.** `citekey#^claim-id` with
  `supports`/`disputes` targeting another claim address. The finest provenance found elsewhere is
  hermes's per-paragraph `^[raw/…]` marker, llmwiki's line-range citation and paperclip's `#L45`.
  *Qualification:* unmatched among products, but the model has standards precedent — the
  micropublication Claim-with-support-and-challenge graph, and Wikidata's per-statement references.
- **Byte-comparable quote verification with stored W3C-shaped selectors.** Quote text is checked
  against the managed region with prefix/suffix anchors and a `fuzzy-quote` reason code that makes
  an approximate match a finding rather than a pass. medsci matches quotes against extracted PDF
  text and hermes rejects quotes absent from a fetched page; nobody else stores selectors.
- **An armed, fail-closed Stop gate with an audited bypass.** Bounded at 8 blocks, with the bypass
  recorded as an open finding rather than forgiven. pedrohcgs is the only other product with a Stop
  hook, and it runs a log reminder.
- **A publication lifecycle with tags that are never deleted.** `mark-published` /
  `mark-corrected` / `mark-withdrawn` / `mark-parked`, with a published-drift lint watching the tag
  and a correction adding a tag rather than replacing one. Every other product stops when the
  artifact ships.
- **A frozen reason-code and check-id registry.** 18 reason codes and 15 check ids enforced by the
  writer, so every durable finding carries a controlled vocabulary. Comparables use free-text
  findings or per-tool codes.
- **Update-notice handling with reinstatement inside a gate.** Blocking and warn classes,
  bi-temporal recording, DataCite version checks, arXiv withdrawal detection and an offline
  Retraction Watch CSV path, with a dated reinstatement clearing an earlier dated block. paper-qa
  ships a retraction CSV and Imbad0202's `retraction_status.py` also models reinstatement as a
  clearing verdict; neither pairs it with a session-closing gate.
- **Admission as a *human* act, as an architectural rule.** Nothing becomes citable except by a
  person accepting it into Zotero; `find-sources` terminates at that boundary and logs declines
  with a reason code, and no machine path can substitute. *Qualification:* research-hub also gates
  citability — `verify_authenticity()` decides whether a candidate enters the corpus at all
  (§6.15) — so the differentiator is not that we gate citability and others do not. It is that
  ours is gated by a person and theirs by a resolver. Everyone else gates *writes*, not
  citability.
- **A citekey join key backed by a live reference manager.** Filenames, prose citations, the
  bibliography export and every check join on the Better BibTeX citekey. *Qualification:*
  medsci's `lit-sync` also joins a `.bib`, the Zotero library and an Obsidian vault, so this holds
  as a difference of degree — our checks all key off the citekey — not of kind.
- **Zero runtime dependencies.** The core is stdlib-only. Every comparable of similar scope pulls a
  Node or Python dependency tree, and several require Postgres, embeddings or a model provider.

**Not on this list, and formerly claimed:** four-state honesty. Imbad0202's
`bibliographic_integrity_signals.md` mandates the same doctrine as a versioned schema and goes
further by separating *a check ran* from *what it found*. That is convergence, not a
differentiator.

## 13. Differences, axis by axis

| Axis | Us | The field |
|---|---|---|
| What is citable | only a human-admitted Zotero item | anything dropped into `raw/` or `sources/` — except research-hub, which screens candidates through a fail-closed resolver gate |
| Who writes the evidence layer | the CLI renders it; the LLM may not touch it | the LLM writes source pages directly (all wiki-family products) |
| Provenance granularity | claim block address + locator + stance | page, paragraph, line-range or `#L45` at best |
| Verification | deterministic registry checks that close surfaces | registry checks as audit (Imbad0202, medsci), LLM adjudication, structural lint, or nothing |
| Failure vocabulary | four states, frozen reason codes, never a verdict on an outage | the same four states as a schema (Imbad0202); elsewhere pass/fail, free-text findings or console output |
| Enforcement point | git pre-commit, PostToolUse warn, Stop gate | prompt convention (hermes `llm-wiki`, SamurAIGPT, nvk, Pratiyush), script gate (hermes `grounded-citations`), write-path runtime (llmwiki), transaction approval (claude-obsidian), PreToolUse guard (Imbad0202), CI build (Manubot) |
| Retrieval | none — index and log orientation | BM25, embeddings, hybrid, or graph expansion |
| Breadth of ingest | one item type | tens of formats plus media and code |
| Breadth of output | none | LaTeX, DOCX, PDF, slides, dashboards, `llms.txt`, JSON-LD, Neo4j |
| Evaluation | unit tests | citation coverage/precision harnesses, gold sets, calibration, routing evals, a labelled hallucination benchmark |
| Deletion | never — records deprecate | nvk retracts; llmwiki `rm` removes a source and derived pages |
| Concurrency | single-threaded skills | agent panels, parallel workers, orchestrators |
| Dependencies | stdlib only | Node/Python trees, Postgres, embeddings, model providers |
| Cross-agent testing | none | superpowers runs per-agent conformance suites for 8 agents |
| Scale evidence | none published | gbrain frames a 150K-page brain as its target (README.md:14); several ship scale docs |
| Maturity | v0.1.0, unpublished | 217 – 234k stars across Tier 1, versioned releases, marketplaces (the 276k Tier-4 framework is not a competitor) |

---

# Part IV — Record

## 14. Corrections to this repository's earlier notes

All verified against the repositories on 2026-08-22.

**Facts the notes get wrong**

1. Imbad0202/academic-research-skills **does** integrate Zotero: `scripts/adapters/zotero.py`
   reads a Better BibTeX JSON export, alongside `folder_scan.py` and `obsidian.py`. The note
   records "no Zotero integration at all". Its CC-BY-NC-4.0 license is confirmed from `LICENSE`.
2. WenyuChiou/ai-research-skills contains **zero** `SKILL.md` files today; it is a catalog whose
   16 skills live in sibling repositories. The note's count of 16 is right; its claim that they
   are in-repo, and that the project is "small and unproven", is not — the catalog carries
   per-skill verification tiers, a NotebookLM brief verifier, deep Zotero CRUD, a library curator
   and a three-gate topic dossier.
3. **skyllwt/OmegaWiki** is recorded as nonexistent (GitHub API 404), and a citation of it is
   treated as evidence of marketing fabrication. Today `GET /repos/skyllwt/OmegaWiki` resolves —
   GitHub follows the rename and returns **skyllwt/AutoSci** (1,642 stars, MIT). The repository
   exists under a new name, so the dead-end entry should be revisited; the note's separate
   observation about one account posting across two repositories' issues is unaffected.
4. K-Dense-AI ships 163 skill directories (note: 161); anthropics/skills ships 19 (note: 17);
   garrytan/gbrain ships 71.
5. atomicstrata/llm-wiki-compiler exports and imports OKF — the same standard our ADR 0001 names
   as the survivability mechanism. Neither note records this.
6. Every star count in both notes is stale relative to 2026-08-22.

**Claims the notes make that this pass falsified in our own favour's opposite direction**

7. "hermes' gates are prompt conventions with zero runtime enforcement" is true of the `llm-wiki`
   skill and **false of the repository**: `grounded-citations` ships a ledger script and a
   `verify --evidence` gate that fails drafts whose cited sources carry no evidence.
8. Four-state honesty was recorded here as unmatched. Imbad0202's
   `bibliographic_integrity_signals.md` mandates it as a versioned schema and separates
   attestation from observation, which we do not.

**Claims the notes make that re-verification confirmed**

9. SamurAIGPT's ingest hash is computed and only printed (`tools/ingest.py:199,202`), and its
   `append_log` prepends while its own `CLAUDE.md` documents append (`tools/_utils.py:114`).
10. K-Dense's per-skill licensing is real and heterogeneous: `skills/docx/LICENSE.txt` opens
    "© 2025 Anthropic, PBC. All rights reserved." Four skills in that MIT repository are
    proprietary.
11. Six mechanisms the notes cite were re-verified at primary source and hold: Manubot's
    `manubot-fail-on-errors` opt-in and `manual-references*.*` bypass, Vale's `--minAlertLevel`
    flag (its three-tier taxonomy was *not* re-checked), lychee-action's `fail: true` default in
    `action.yml`, Hypothes.is's 50 % error budget, the W3C normalization requirement, and
    Wikidata's deprecated rank with P2241. The notes' own wording was not diffed against these
    findings — only the underlying facts were confirmed.

## 15. Licence and adoptability

Forkable as declared in-repo (all MIT): claude-obsidian, llm-wiki-compiler, gbrain, WenyuChiou,
pedrohcgs, hermes-agent, swarmvault, SamurAIGPT, nvk, Pratiyush, kepano, medsci-skills,
research-hub, superpowers, mattpocock/skills.

**Not forkable: Imbad0202/academic-research-skills** — `LICENSE` is Creative Commons
Attribution-NonCommercial 4.0, © 2026 Cheng-I Wu. Its ideas can be re-derived; its files cannot be
copied.

**Check per skill: K-Dense-AI/scientific-agent-skills** — MIT at repository level *and* a per-skill
`license:` field in SKILL.md frontmatter, verified MIT on `paper-lookup`, `citation-management`,
`pyzotero` and `literature-review`, `Apache-2.0` on `liteparse` — but docx, pdf, pptx and xlsx ship
proprietary Anthropic LICENSE.txt files.

**Check the notices: anthropics/skills** ships a separate `THIRD_PARTY_NOTICES.md`; do not assume
the repository licence covers the document skills.

**MIT, declared in the README rather than a LICENSE file**: obra/knowledge-graph,
sdyckjq-lab/llm-wiki-skill, introfini/ZotSeek (also `package.json`), TonybotNi/ZotLink (also
`setup.py`), PHY041/claude-skill-citation-checker, htlin222/research-guardian-skill,
cookjohn/cnki-skills. GitHub's licence detector reports `none` for all of these, and an earlier
draft of this document repeated that. A README heading is a licence grant; the detector's silence
is not evidence of its absence.

**No licence, anywhere**: jason-effi-lab/karpathy-llm-wiki-vault. No LICENSE file, no manifest
field, no README statement. That is **all rights reserved**, not public domain — copyright attaches
automatically and absent an explicit grant there is no permission to copy, modify or redistribute.
GitHub's Terms of Service permit viewing and forking on GitHub; they do not permit redistribution
inside an MIT-licensed plugin.

**MIT with a proprietary subtree**: sdyckjq-lab/llm-wiki-skill declares MIT (`package.json`,
`workbench/LICENSE`, © 2026 Kiro) and bundles the four Anthropic document skills at
`workbench/.claude/skills/{docx,pdf,pptx,xlsx}/LICENSE.txt`, each opening "© 2025 Anthropic, PBC.
All rights reserved." The repository licence does not reach them.

## 16. Searched and not added

Second-brain and note-taking harnesses with no evidence layer and no citation discipline
(agenticnotetaking/arscontexta 3,480; alchaincyf/obsidian-ai-orange-book 1,425;
coleam00/second-brain-skills 819) and a long tail of `llm-wiki` forks under 110 stars
(ekadetov/llm-wiki, praneybehl/llm-wiki-plugin, 6eanut/llm-wiki, olegiv/llm-wiki-go,
eugenelim/llm-wiki-kit) repeat mechanisms already represented by claude-obsidian, hermes and nvk.
Generic writing skills (academic humanizers, PPT generators) and single-database MCP wrappers
(four separate `openalex-mcp` repos, scholar-feed-mcp, scholar-sidekick-mcp, nasa-ads-mcp,
academic-tools-mcp) are components of a component. Sub-10-star systematic-review scaffolds were not
inspected. **Orchestra-Research/AI-Research-SKILLs** (11,950) was checked and excluded: its
top-level directories are `01-model-architecture`, `02-tokenization`, `03-fine-tuning`,
`04-mechanistic-interpretability`, `08-distributed-training`, `13-mlops`, `15-rag` — ML
engineering, not scholarly-literature work.

From this repository's own notes, the following were reviewed and not carried into the comparison:
vault-structure conventions (nickmilo/IMF-v3, cassioborgesmenezes/pkm-imf), Zotero-ecosystem
plugins already represented at component level (jlegewie/zotfile, MuiseDestiny/zotero-attanger,
daeh/zotero-markdb-connect, dvanoni/notero, zotero/zotero itself), and W3C PROV-O, ICD 206/203 and
CSL/JATS locator conventions — none is a harness comparable and none was re-verified here.

**Previously outstanding, now closed:** `WenyuChiou/research-hub` was read on 2026-08-22 and is
written up at §6.15; medsci-skills was surveyed skill-by-skill and its entry at §6.1 revised. The
remaining unread surface is the long tail of Tier-1 search finds marked without a ✓ in §6.16.

---

# Part V — Positioning judgment

## 17. Does this product have a place, or should we adopt an alternative?

**Epistemic status.** Parts I–IV are evidence: every claim traces to a file, a spec or an API
response read on 2026-08-22. This section is *judgment* built on that evidence, and it is not the
same kind of statement. It rests on a capability read of roughly 35 repositories — not on market
research. There is no demand data here, no user evidence, and star counts are a distribution proxy
and a poor one in an ecosystem where an agent framework carries 234,000 stars. Every factual claim
below cites the section that verified it; the inferences are mine.

### 17.1 Verdict

Yes, but not in the category the README names. As "a Claude Code harness for knowledge work —
academic research first", the field is crowded and better resourced: Imbad0202 at 43,339 stars with
394 scripts, K-Dense at 34,130 with 163 skills, pedrohcgs with 52, medsci with 59. We ship nine.

As **the gate layer** — the thing that decides whether work may proceed — the position is real,
and on the evidence in Part III nobody occupies it.

### 17.2 The build-versus-adopt binary is false, and this repository already resolved it once

`find-sources` is an adoption: K-Dense's `paper-lookup`, vendored at a pinned SHA with a
header-only diff and zero removals (§10.2). Generalise that and the answer follows —
**build the trust core, adopt the breadth.** The two lists in Part III split cleanly along that
line:

- §12, what only we have, is entirely enforcement-layer: gates that close a surface, admission as
  the sole path to citability, block-addressed claims with typed stance links, a frozen
  reason-code registry, a correction lifecycle whose tags are never deleted.
- §11, what we lack, is almost entirely breadth-layer: retrieval, drafting, rendering, submission
  packaging, MCP surfaces, evaluation harnesses, maintenance lanes — and nearly all of it exists
  under MIT (§15).

Building breadth means competing on the field's own ground with one author. Building the gate means
being the only one there.

### 17.3 The differentiator, stated precisely enough to defend

Not "we verify citations". Three other products run registry-backed deterministic verification —
Imbad0202's `verification_gate`, medsci's `verify-refs`, pedrohcgs' `validate-bib --semantic`
(§10.6) — above a Tier-2 shelf of bibverify, doi-mcp and citation-checker (§7).

The verified position is narrower and holds: **the only product whose verification result closes a
commit and a session-Stop surface**, combined with admission as the only path to citability and
`citekey#^claim-id` addressing with typed stance links. Two adjacent claims must stay qualified as
they are in §12: the citekey join is a difference of degree from medsci's `lit-sync`, not of kind;
and four-state honesty is convergence with Imbad0202, not a differentiator.

### 17.4 Why "adopt an alternative" is unavailable for the distinctive part

Three credible candidates, failing on different axes. The first draft of this section said
adoption was simply unavailable for the gating thesis; the full surveys of medsci-skills and
research-hub (§6.1, §6.15) show that was too strong, and the accurate statement is narrower.

- **Imbad0202/academic-research-skills** has the strongest verification machinery in the
  comparison (§6.2) and is **CC-BY-NC-4.0** (§15). It can be studied and re-derived; its files
  cannot be copied. It also has no vault and no citekey spine.
- **Aperivue/medsci-skills** matches our substrate exactly and is MIT (§6.1). Its `verify-refs` is
  audit-only by design, but the product does gate: `preflight_gate.py` returns 1 on halt and
  `pre_submission_gate.sh` exits 1. Two things still separate it. Those are **CLI gates a person
  runs**, not session enforcement — the repository ships no `plugin.json` and no hooks at all. And
  it is **domain-locked**: 21 of 59 skills are medical-specific, and it describes itself as
  "physician-built … not a generic skill catalog".
- **WenyuChiou/research-hub** is MIT and gates fail-closed on registry evidence, with a layered
  authenticity check and recoverable quarantine (§6.15). But it gates a *different boundary*:
  admission of a candidate paper into the corpus, on per-paper authenticity. It has no claim
  addressing, no quote verification and no publication lifecycle.

So the honest position is not "nobody gates". It is that **nobody gates a draft, a commit and a
session on per-claim evidence**. research-hub gates the corpus upstream of us and is complementary;
medsci gates the submission package downstream of us and is medical-only; Imbad0202 gates
comparably but cannot be adopted. That is a narrower crux than the first draft claimed, and it
still holds.

### 17.5 What follows

1. **Narrow to the gate.** Keep the core, `verify-citations`, `publish`, `evidence-conventions` and
   `import-source`. Stop treating drafting, rendering and submission packaging as roadmap — those
   belong to medsci and pedrohcgs, who are years ahead on them (§11).
2. **Port two MIT scripts that are gate-layer, not breadth-layer.** medsci's
   `check_claim_fidelity.py` and `_quote_match.py` (§6.1). §10.7 already concedes `factcheck-draft`
   is where we are most clearly behind; these close that gap and *strengthen* the narrow position
   rather than widening scope.
3. **Run HALLMARK against the deterministic suite** (§8.4): 2,525 labelled entries, 14 hallucination
   classes, 10 published baselines. A per-class catch rate is the one number no competitor
   publishes, and §11 records that we have no evaluation instrument at all.
4. **Vendor rather than rebuild** anything breadth-shaped, following the `find-sources` pattern —
   pinned SHA, header-only provenance additions, re-vendor to update. Section 18 works that
   instruction into a candidate-by-candidate list.

### 17.6 Two facts that bear on timing

**Being wrong is cheap.** ADR 0001 makes the vault tool-independent: plain markdown and YAML in
git, structurally conformant to OKF (§4, §8.3). A later pivot to medsci does not strand the
researcher's data. That asymmetry favours continuing.

**The window is not open indefinitely.** medsci-skills was pushed three days before this
comparison and already carries Zotero, an Obsidian vault, citekey provenance and registry
verification (§6.1). It is converging on our substrate from the audit side. If it adds a closing
gate, the distinctive position narrows to nothing. That argues for speed on the gate, not for
abandoning it.

### 17.7 What would change this verdict

- ~~Reading medsci-skills in full and finding it already gates.~~ **Surveyed** (§6.1) — all 59
  skill descriptions with script and test counts, the gate scripts, the hook surface and the
  plugin split; roughly ten skill bodies read in full. It gates at the submission-package boundary
  via CLI scripts, ships no hooks, and is medical-domain-locked. The verdict survives, narrowed.
  A line-by-line read of `self-review` (36 scripts) and `sync-submission` (21) remains undone.
- ~~`WenyuChiou/research-hub` turning out to verify.~~ **Done** (§6.15). It does — fail-closed, MIT,
  on registry evidence — but at corpus admission rather than at the draft. Complementary, not
  competing. The verdict survives, narrowed again.
- **A third product adding per-claim gating at the draft boundary.** That is now the specific thing
  to watch, and medsci is the likeliest source of it.
- **Deciding the goal is one researcher's working setup rather than a product.** Then the economics
  invert: adopt medsci, keep the gate as a thin plugin over it, and stop building nine skills to
  reach parity with fifty-nine.

---

## 18. Vendoring candidates, gap by gap

Section 17.5 recommends vendoring rather than rebuilding. This section names what to vendor.
Every candidate below was checked on 2026-08-22 for licence, import surface and coupling; line
counts and import lists come from the files themselves.

### 18.1 The four tests

A candidate is **adopt-as-is** only if it passes all four. Failing any one moves it down a tier,
and the tier is the recommendation.

1. **Licence.** Permissive, and verified in the artifact rather than assumed from the repository.
   K-Dense is MIT at repository level with four proprietary Anthropic skills inside it (§6.12);
   medsci's checklists carry per-file licences that differ from the repository's (§18.4).
2. **Self-containment against a zero-dependency core.** Our core imports nothing outside the
   standard library. A file importing `requests`, `httpx`, `pydantic` or `python-docx` cannot be
   vendored into it, however good it is.
3. **Substrate fit.** A file coupled to another project's layout — its registries, its vault
   resolver, its manifest format — is a rewrite, not an adoption.
4. **It fills a gap this document lists.** Otherwise it is scope creep with a provenance header.

### 18.2 Tier A — adopt as-is

Permissive, standard-library only, no coupling beyond a same-directory sibling. Vendor exactly as
`find-sources` was: pinned SHA, comment header, no hand-edits, re-vendor to update.

| Candidate | Lines | Imports | Fills | Note |
|---|---|---|---|---|
| medsci `verify-refs/scripts/_quote_match.py` | 172 | `re`, `unicodedata` | token-ordered quote matching where ours ends in a contiguous find (§6.1) | vendored and dropped this session pending a decision on wiring; the pin is recorded in the git history |
| medsci `manage-refs/scripts/check_citation_keys.py` | 147 | `argparse`, `re`, `sys` | pandoc `[@key]` undefined/unused detection; complements our bibliography-joined `citekey` check | |
| medsci `manage-refs/scripts/check_reference_duplication.py` | 245 | `+ json`, `zipfile` | duplicate-entry detection, listed as absent from our `citekey` check (§10.6) | |
| medsci `sync-submission/scripts/cross_document_n_check.py` | 486 | `argparse`, `json`, `re`, `sys` | the same participant count asserted across every document — a cross-artifact consistency class we have none of (§11) | |
| medsci `version-dataset/scripts/*` | small | `hashlib`, `json`, `argparse`, `pathlib` | deterministic content-hash manifest for a dataset (§11, research-data reproducibility) | closest fit to our existing `fixity-sha256` thinking |
| medsci `search-lit/scripts/check_doi_record_match.py` | 276 | `urllib`, `csv`, `difflib.SequenceMatcher` | DOI-to-record matching with fuzzy title comparison; overlaps our `metadata` check and may sharpen its tolerance | stdlib networking, same posture as our `webapi.py` |
| medsci `sync-submission/scripts/check_wordcount_cap.py` | 238 | `+ _yaml_frontmatter` (same dir) | word-count ceilings at submission | vendor the sibling too, as medsci itself does |

`check_xref.py` (740 lines, stdlib) is the largest of these and does manuscript-to-DOCX
cross-reference QC. It passes all four tests but only becomes useful once we render a DOCX, so it
belongs behind the rendering decision rather than in front of it.

### 18.3 Tier B — fork a function, not a file

Permissive and stdlib, but coupled to the donor's data shapes. Take the algorithm, write our own
seam, credit in a header comment.

| Candidate | What to take | Why not as-is |
|---|---|---|
| claude-obsidian `claude_obsidian/ledgers.py::_independent_group_count` | union-find collapsing sources that share an origin, content hash or declared independence key, so they cannot corroborate each other (§6.4) | operates on the donor's ledger record shape; the algorithm is about thirty lines and the value is entirely in the idea |
| medsci `verify-refs/scripts/check_claim_fidelity.py` | the graded-by-checkability probe design: quoted text is decidable, attribution is not, so only the extreme case fires (§10.7) | 644 lines whose CLI takes `--manuscript --fulltext-dir --bib --refmap` — bound to their layout |
| claude-obsidian `scripts/bm25-index.py` | a pure-stdlib BM25 index in 851 lines, with an honest documented no-op when the optional reranker is absent | imports `claude_obsidian.paths` and `claude_obsidian.transaction`; the retrieval decision is not made anyway (§11) |
| swarmvault `packages/engine/src/watch.ts` | the shrink-ratio circuit breaker: refuse a refresh that drops nodes or edges by more than 25% (§6.7) | TypeScript; the mechanism is a comparison and a threshold, perhaps twenty lines in Python |
| research-hub `authenticity.py` | the layered gate shape, and specifically the transient-versus-permanent split that admits under a recheck marker rather than blocking (§6.15) | imports `requests` and five project modules |

### 18.4 Tier C — adopt as data

Data outlives code and travels further. Each of these is a table or a corpus rather than a
program, and each carries its own licence question.

- **medsci `check-reporting/references/checklists/`** — 49 reporting-guideline checklists, with
  scripts that are pure stdlib (`argparse`, `csv`, `hashlib`, `json`, `re`, `sys`). The important
  artifact is `references/LICENSES.md`, which resolves each checklist's licence through the
  article's Crossref `license` field and the PMC `<license>` element, splits the table into
  *verified permissive* and the rest, and states the rule plainly: "an absent licence statement is
  **not** evidence of permissive licensing", noting that several publishers do not release these
  instruments under an open licence at all. **Vendor only the rows marked verified permissive, and
  vendor that discipline with them.** This is the best licence hygiene found in the survey.
- **research-hub `_PREDATORY_DOI_PREFIXES`** — a registrant-prefix denylist sourced from Cabell's
  and Beall's, cross-checked against Crossref member data, admitting only prefixes whose entire
  portfolio is predatory. Verified: it currently holds **two entries**, so the value is the
  mechanism and the inclusion rule, not the table. Ours would need its own curation, and the
  config-extension point research-hub provides is the right shape.
- **rpatrik96/hallmark** — MIT, 2,525 labelled entries, 14 hallucination classes, 3 difficulty
  tiers, 10 published baselines. Use as an evaluation fixture; vendor no code. This is step 3 of
  §17.5 and the cheapest credibility move available.

### 18.5 Tier D — depend, do not vendor

Real tools doing real work, too large or too external to carry.

| Tool | Licence | Role |
|---|---|---|
| microsoft/markitdown | MIT, 175,520 stars | the format-breadth answer if `import-source` ever ingests beyond Zotero; SamurAIGPT already routes through it (§6.10) |
| pandoc + CSL | GPL, external binary | rendering and citation formatting; medsci `manage-refs` and pedrohcgs `compile-latex` both shell out to it rather than reimplementing |
| Hylouis233/bibverify | MIT | a second opinion on a `.bib`, with `rank_lookup_sources` explaining resolver choice — but it duplicates our DOI and metadata legs, so only worth it if that explanation is wanted (§7) |
| htlin222/prisma-automation | MIT, 8 stars | PRISMA flow-diagram generation, the one piece of systematic-review apparatus that is a discrete artifact rather than a workflow |
| kepano `defuddle` | MIT | already provisioned by `setup-vault`; the web-capture answer if one is needed |
| obra/knowledge-graph | MIT (README) | vault-as-knowledge-graph over SQLite with sqlite-vec and FTS5, local embeddings, Louvain communities, betweenness and PageRank, exposed as a CLI and an MCP server with a `prove-claim` skill. Node and TypeScript, so a dependency rather than a vendor target — but the single closest answer to our largest gap (§11, retrieval and graph) |

### 18.6 Tier E — pattern only, and why

Worth reading, not worth carrying. Each fails a specific test.

- **Imbad0202, everything** — CC-BY-NC-4.0. The integrity-signal contract, the injection probes,
  the judge-prompt-version pin and the uncited-assertion detector are all re-derivable and none is
  copyable (§6.2, §15).
- **paper-qa `journal_quality.py`** — imports `anyio`, `httpx`, `httpx_aiohttp`, `pydantic`,
  `rich` and paperqa internals. The venue-quality gap is real; this file is not the route to it.
- **medsci `manage-refs` rendering scripts** — import `python-docx`; they also vendor their own
  `_vendor_citation_writer`, so the pattern is confirmed but the code is not portable to a
  zero-dependency core.
- **hermes `grounded-citations`** — MIT, and the closest peer to our quote gate, but its ledger
  exists because web sources have no stable identifier. Our citekey universe already is that
  ledger (§6.6).
- **gbrain, swarmvault, llmwiki** — Postgres, a Node toolchain and a compiled-artifact ownership
  model respectively. Patterns transfer; code does not.
- **WenyuChiou `gap-to-topic`** — MIT and only 219 lines of SKILL.md plus references, evals and
  scripts, so it is nearly adoptable. It is listed here rather than in Tier A because a skill is
  prompt text bound to its own vocabulary and downstream handoff (`design_brief.md` frontmatter
  carrying `source` and `gap_verdict`); adopting it means adopting that flow (§6.13).

### 18.7 Tier F — do not touch

- **anthropics/skills `docx`, `pdf`, `pptx`, `xlsx`** — verified proprietary in the K-Dense mirror:
  `skills/docx/LICENSE.txt` opens "© 2025 Anthropic, PBC. All rights reserved." Check
  `THIRD_PARTY_NOTICES.md` before assuming anything about the originals (§6.12, §15).
- **jason-effi-lab/karpathy-llm-wiki-vault** — no licence in any form, which is all rights
  reserved rather than public domain (§15). Read it on GitHub; carry nothing.
- **sdyckjq-lab/llm-wiki-skill's `workbench/.claude/skills/{docx,pdf,pptx,xlsx}/`** — the
  repository is MIT, that subtree is not (§15). The trap is the same one K-Dense sets, and it is
  why test 1 in §18.1 says *verified in the artifact*.

### 18.8 Mirroring a whole skill

A third adoption mode sits between vendoring a file and taking a dependency: **mirror the skill
directory verbatim, with its own licence file beside it.** K-Dense demonstrates the mechanism —
it carries Anthropic's `docx`, `pdf`, `pptx` and `xlsx` skills inside an MIT repository, each
keeping its own `LICENSE.txt` rather than being relicensed under the host's terms.

The mechanism is right and worth copying:

- Copy the upstream skill directory unchanged — `SKILL.md`, `scripts/`, `references/`, `evals/`.
- Carry the upstream `LICENSE` beside it, or add one naming the source and terms where upstream
  declared them in a README.
- Add the provenance header we already use: source repository, pinned SHA, upstream path, licence,
  and "do not hand-edit; re-vendor to update".
- Rename only into our namespace, exactly as `paper-lookup` became `find-sources` (§10.2).

This mode sidesteps §18.1's third test, because a skill is self-contained by design — it brings its
own prompt, scripts and reference files rather than reaching into a host layout. That widens the
candidate set considerably now that the licences are established:

| Skill | Repo | Licence | Fills |
|---|---|---|---|
| `claude-skill-citation-checker` | PHY041 | MIT (README) | `.bib` against CrossRef, Semantic Scholar and OpenAlex — a second opinion beside our own DOI and metadata legs |
| `research-guardian` | htlin222 | MIT (README) | multi-gate audit of hypotheses, citations, experiments, results and logic fallacies |
| `gap-to-topic` | WenyuChiou/research-hub | MIT | the three-gate go/no-go dossier, the one thing upstream of `project` (§6.13) |
| `cnki-skills`, `gs-skills` | cookjohn | MIT | CNKI and Google Scholar coverage our vendored `find-sources` lacks entirely |
| `asta-skill` | Agents365-ai | MIT | Ai2's Asta MCP over Semantic Scholar, as an instruction pack |
| medsci `verify-refs`, `manage-refs`, `check-reporting` | Aperivue | MIT (per-file for checklists, §18.4) | reference audit, rendering and 49 reporting guidelines as whole units rather than script by script |

**Where the pattern stops.** K-Dense and sdyckjq-lab both mirror Anthropic's `docx`, `pdf`, `pptx`
and `xlsx` skills. Their bundled `LICENSE.txt` addresses that directly, under the heading
ADDITIONAL RESTRICTIONS — users may not:

> - Extract these materials from the Services or retain copies of these materials outside the
>   Services
> - Reproduce or copy these materials, except for temporary copies created automatically during
>   authorized use of the Services
> - Create derivative works based on these materials
> - Distribute, sublicense, or transfer these materials to any third party

and closing: "The receipt, viewing, or possession of these materials does not convey or imply any
license or right beyond those expressly granted above."

So the mirroring *mechanism* is sound and worth copying, and the two repositories that demonstrate
it are, on those four directories, doing what their own bundled licence forbids. That is not a
close call and it is not our judgment call to make differently — it is the text. Mirror freely
under MIT and comparable terms; for these four, take the dependency through the Services instead
(anthropics/skills installs as a marketplace plugin), which is the route the licence contemplates.

### 18.9 What this changes about sequencing

Tier A is roughly 1,600 lines of standard-library Python under one MIT licence from one donor,
filling five gaps this document lists. That is the cheapest breadth we will ever acquire, and it
costs one re-vendor obligation per file. Tier C's reporting checklists are the largest single
capability gain and the one with the most careful licence question already answered for us.

The sequencing implication for §17.5 is that vendoring is not step 4. It is the step that makes
steps 1 and 2 affordable, because every file in Tier A is breadth we then do not have to build
while narrowing to the gate.
