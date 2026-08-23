# An assembled harness: the same thesis from third-party parts

Design exploration, 2026-08-22. **Not approved, not planned, nothing built from it.** It answers
one question: could the thing knowledge-harness and Memoria are both building be assembled from
components that already exist, rather than written?

Every component named below was inspected during the 2026-08-22 product survey. Licences are as
verified then, and marked **[F]** where a file was opened and **[M]** where the row rests on
repository metadata and the project's own description.

**knowledge-harness and Memoria are excluded from the assembly.** Both are in-house, and using
either as a component would answer a different question than the one asked. Where a design of
theirs is the best available answer to a problem, it is named as **in-house prior art** and marked
as such — never counted as something the assembly gets for free.

## 1. The honest reading of the constraint

"Third-party modules only" cannot mean *no code written*. Three things resist sourcing, and naming
them first is what makes the rest of this spec worth reading.

**A. The join.** Any assembly of N tools needs the code that calls them, passes data between them,
and decides what their output means together. That is not a component; it is the product.

**B. The result contract.** Assembled verifiers do not agree on what an answer is.
`docs/2026-08-22-product-comparison-verified.md` §18.1 records the decisive case: K-Dense's
`validate_citations.py` returns `Tuple[bool, Optional[Dict]]` and, on a network failure, returns
`True` — an outage becomes a pass, because a boolean has nowhere to put *could not run*. Its
sibling `literature-review` makes the opposite error, returning invalid on an exception. Adopting
both without a normalising layer imports two contradictory falsehoods. research-hub solves this by
classifying reason strings one layer up (`is_transient_reason`); Imbad0202 by a versioned schema
separating attestation from observation; we by putting four states in the type. **An assembled
system must build one of those three, because no component ships it.**

**C. The addressing.** `citekey#^claim-id` with typed `supports`/`disputes` between claim addresses
has no donor among 35 surveyed products (§12). The nearest precedents are standards, not code:
micropublications' Support and Challenge graphs, Wikidata's per-statement references.

So the shape of an assembled harness is: **third-party components for every capability, plus an
adapter layer that normalises their results, plus the claim addressing.** Roughly the inverse of
what both existing projects did, which was to build the capabilities and inherit nothing.

## 2. Component assembly

### 2.1 Reference layer — the spine

| Capability | Component | Licence | Notes |
|---|---|---|---|
| Reference manager | Zotero | AGPL-3.0 (app) | the admission surface; a human act by construction |
| Citekey generation and stability | Better BibTeX | MIT **[M]** | deterministic keys, pinning, auto-export of Better CSL JSON |
| Programmatic access | 54yyyu/zotero-mcp | MIT **[F]** | 51 tools: citekey lookup, attachment paths, annotations, PDF pages, full text, duplicates, plus Scite tallies and retraction alerts with no API key |
| Alternative access | urschrei/pyzotero | NOASSERTION **[M]** | library client for scripting; check the licence declaration before shipping |
| Local semantic search over the library | introfini/ZotSeek | MIT (README + `package.json`) **[F]** | a Zotero plugin with a built-in MCP server; runs in-process, so a provisioned companion rather than a dependency |

### 2.2 Discovery

| Capability | Component | Licence | Notes |
|---|---|---|---|
| Multi-database literature search | K-Dense `paper-lookup` | MIT **[F]** | 11 databases, stdlib-only scripts, per-API hazard documentation, credential redaction. Already vendored here as `find-sources` |
| Chinese-language corpus | cookjohn `cnki-skills` | MIT (README) **[F]** | CNKI search, journal browse, PDF download, Zotero export — coverage `paper-lookup` lacks entirely |
| Google Scholar | cookjohn `gs-skills` | MIT (README) **[M]** | no official API; expect fragility |
| Semantic Scholar via Ai2 | Agents365-ai `asta-skill` | MIT **[F]** | instruction pack over the Asta MCP server |

### 2.3 Admission screening

| Capability | Component | Licence | Notes |
|---|---|---|---|
| Fail-closed candidate gate | WenyuChiou/research-hub `authenticity.py` | MIT **[F]** | layered: no-identifier → identifier resolution → Crossref corroboration + predatory-venue denylist → metadata integrity, with recoverable quarantine and a transient-versus-permanent split that admits under a recheck marker. Imports `requests` and five project modules, so this is a fork, not a drop-in |
| Question-worth gate | WenyuChiou `gap-to-topic` | MIT **[F]** | three-gate go/no-go dossier, handing the verdict back to the researcher |

### 2.4 Projection into the vault

| Capability | Component | Licence | Notes |
|---|---|---|---|
| `.bib` → Zotero + Obsidian literature notes | Aperivue medsci `lit-sync` | MIT **[F]** | the only component found that joins all three, with concept-note extraction at an accumulation threshold |
| PDFs → literature and concept notes | medsci `obsidian-paper-vault` | MIT **[F]** | enters the same folders from the opposite end, designed not to collide with `lit-sync` |
| Format breadth | microsoft/markitdown | MIT **[M]** | ~20 formats to Markdown; SamurAIGPT already routes through it |
| Web capture | kepano `defuddle` | MIT **[M]** | already provisioned by `setup-vault` |
| Vault format and operations | kepano/obsidian-skills | MIT **[M]** | Obsidian Flavored Markdown, Bases, Canvas, CLI |

### 2.5 Verification — the part that must be normalised

| Capability | Component | Licence | Result semantics to normalise |
|---|---|---|---|
| BibTeX verification | Hylouis233/bibverify | MIT **[F]** | CLI, Python API and MCP; `rank_lookup_sources` explains resolver choice, `explain_update_diff` diffs entries |
| `.bib` against three registries | PHY041 `claude-skill-citation-checker` | MIT (README) **[F]** | stdlib, CrossRef + Semantic Scholar + OpenAlex |
| BibTeX against Semantic Scholar and DBLP | `harcx` | MIT (PyPI 0.2.0) **[M]** | throttling caveat below |
| Preprint→published replacement and validation | `bibtex-updater` | MIT (PyPI 1.7.0) **[M]** | HALLMARK's co-designed rule-based reference |
| DBLP-first verification | NKU-AOSP-Lab/CiteVerifier | MIT **[M]** | from the GhostCite paper |
| Fabricated references from a PDF | gianlucasb/hallucinator | NOASSERTION **[M]** | the only PDF-side input in this class; licence unverified |
| Reference audit against PubMed and Crossref | medsci `verify-refs` | MIT **[F]** | audit-only by design, writes `qc/reference_audit.json` |
| Citation-key validation | medsci `check_citation_keys.py` | MIT **[F]** | 147 lines, stdlib; pandoc `[@key]` undefined and unused |
| Duplicate entries | medsci `check_reference_duplication.py` | MIT **[F]** | 245 lines, stdlib |
| Claim fidelity | medsci `check_claim_fidelity.py` | MIT **[F]** | graded probes: `CITED_QUOTE_ABSENT` major, `ATTRIBUTION_UNSUPPORTED` only when not one content word appears in the source |
| Quote matching under extraction noise | medsci `_quote_match.py` | MIT **[F]** | 172 lines, `re` + `unicodedata`; grades EXACT / INTERLEAVED / PARTIAL / ABSENT with coverage |

**Operational caution, verified:** HALLMARK omits `HaRC` and `verify-citations` from its published
results because "Semantic Scholar throttling collapses their effective coverage to <7% on
`dev_public`". Any assembly leaning on Semantic Scholar inherits that ceiling.

### 2.6 Post-publication signals

| Capability | Component | Licence | Notes |
|---|---|---|---|
| Retraction dataset, offline leg | gitlab.com/crossref/retraction-watch-data | CC **[M]** | Crossref-owned, freely distributed; loaded locally and indexed by `OriginalPaperDOI` — complete, deterministic, no network at check time. Reachable 2026-08-22 (HTTP 200) |
| Retraction, live delta | Crossref REST `works/{doi}` | free API **[F]** | `message.update-to[]` filtered to `type == "retraction"`, **plus `message.relation.is-retracted-by`** — the second field is one this project does not currently read. Reachable 2026-08-22 (HTTP 200) |
| Retraction, non-Crossref coverage | OpenAlex `is_retracted` | free API **[F]** | the cross-check for DataCite and arXiv-registered DOIs |
| Retraction, independent third source | openretractions.com | — | **not usable.** Unreachable from this machine on 2026-08-22 (HTTP 000) while Crossref and GitLab both returned 200 from the same host, so the probe was validated. Its data is described upstream as ~2020. Listed so a later pass does not rediscover it as an option |
| Retraction status resolution | Imbad0202 `retraction_status.py` | **CC-BY-NC-4.0** | models reinstatement as a clearing verdict; **study only, cannot be copied** |
| Citation stance tallies | Scite via zotero-mcp `tools/scite.py` | MIT wrapper **[F]** | supporting / contrasting / mentioning counts, no API key |
| Venue quality | — | — | **no adoptable component.** paper-qa's `journal_quality.py` needs `anyio`, `httpx`, `pydantic`, `rich` and paperqa internals; the route is the underlying data |

### 2.7 Retrieval and graph

| Capability | Component | Licence | Notes |
|---|---|---|---|
| Vault as a knowledge graph | obra/knowledge-graph | MIT (README) **[F]** | SQLite + sqlite-vec + FTS5, local 22 MB embedding model, Louvain communities, betweenness, PageRank, CLI **and MCP server**, plus a `prove-claim` skill |
| Vector index | asg017/sqlite-vec | Apache-2.0 **[M]** | the storage layer beneath it |
| Stdlib BM25 alternative | claude-obsidian `scripts/bm25-index.py` | MIT **[F]** | 851 lines, pure stdlib, honest no-op when the reranker is absent; coupled to its own vault resolver, so a fork |

### 2.8 Synthesis discipline

| Capability | Component | Licence | Notes |
|---|---|---|---|
| Wiki thresholds and lint rules | hermes-agent `llm-wiki` | MIT **[F]** | 2+-source page threshold, closed tag taxonomy, minimum outbound links with backlink check, an 11-check lint, ask-first at 10+ pages touched |
| Machine-owned citation ledger | hermes-agent `grounded-citations` | MIT **[F]** | the ledger owns `url → [n]` "so the model only ever emits small integers it was handed"; quotes rejected unless they literally appear in fetched text; `verify --evidence` fails a draft whose sources carry no evidence |
| Compilation-value gate and staged writes | AgriciDaniel/claude-obsidian | MIT **[F]** | `transaction inspect` → `apply --approved-plan-sha256`, SHA preconditions, exit 75 on conflict, `dir_fd`-confined writes, portable-alias collision guard |
| Independence counting | claude-obsidian `ledgers.py` | MIT **[F]** | union-find collapsing sources sharing origin, content hash or declared independence key; "high-risk acceptance requires two independent sources" |

### 2.9 Output and submission

| Capability | Component | Licence | Notes |
|---|---|---|---|
| Rendering and citation formatting | pandoc | **GPL-2.0** **[M]** | invoked as a binary, not linked; both medsci and pedrohcgs shell out to it rather than reimplementing |
| Citation styles | CSL styles repository | **licence not declared via the API** **[M]** | the project states CC BY-SA; verify before redistribution |
| Journal-CSL rendering, marker conversion, Zotero CWYW field codes | medsci `manage-refs` | MIT **[F]** | needs `python-docx`; the field codes are the part pandoc cannot write |
| Submission-integrity checks | medsci `sync-submission` | MIT **[F]** | ~30 scripts: blinding sweep, asset anonymisation, word-count cap, cross-document participant-count consistency, cover-letter drift, portal-field residue, preflight gate |
| Reporting-guideline compliance | medsci `check-reporting` | MIT scripts; **per-checklist licences vary** **[F]** | 49 guidelines with a `references/LICENSES.md` resolving each through Crossref and PMC. Vendor only the rows marked verified permissive |
| PRISMA flow diagram | htlin222/prisma-automation | MIT **[M]** | the one discrete artifact in the systematic-review class |
| Document renderers | anthropics/skills `docx`/`pdf`/`pptx`/`xlsx` | **proprietary** | their `LICENSE.txt` forbids retaining copies outside the Services, reproducing, deriving and distributing. Use through the marketplace install, never mirrored |

### 2.10 Enforcement surfaces

| Capability | Component | Licence | Notes |
|---|---|---|---|
| Session-boundary gates | Claude Code hooks | — | PostToolUse, PreToolUse, Stop; the only surface in this list that arms a gate without an operator flag |
| Commit-time gate | pre-commit framework | MIT **[M]** | bypassable by design (`--no-verify`); its own docs prescribe CI replay as the honest layer |
| CI gate conventions | lychee-action | Apache-2.0 **[F]** | `fail: default: true` on master, after retries, accept-lists, ignore files and caching existed first |
| Build-as-gate precedent | Manubot / rootstock | NOASSERTION **[F]** | `manubot-fail-on-errors: true` opt-in, with `manual-references*.*` as a data-shaped bypass rather than a flag |
| Severity tiering precedent | Vale | MIT **[F]** | `--minAlertLevel`; only the top tier fails a build |

### 2.11 Evaluation

| Capability | Component | Licence | Notes |
|---|---|---|---|
| Citation-hallucination benchmark | rpatrik96/hallmark | MIT **[F]** | 2,526 entries — 826 valid, 1,246 hallucinated, plus a 454-entry held-out split — 14 types, three tiers, six diagnostic sub-tests per entry, a baseline registry with a documented dispatch interface |
| Metrics | via HALLMARK | — | detection rate, **FPR**, F1, tier-weighted F1, detect@k, MCC, expected calibration error |
| Base rates for extrapolation | Zhao et al., arXiv:2605.07723 | paper | arXiv 0.39%, PMC 0.27%, bioRxiv 0.21%, SSRN 1.91% as of August 2025 |
| Citation-quality metrics design | llm-wiki-compiler `src/eval/` | MIT **[F]** | `deductionFor(result: LintResult)` scores health by deducting per lint finding, so the metric cannot drift from the linter; `selectDeterministicSample()` fixes the judge sample so a delta means the corpus changed |

### 2.12 Schema and portability

| Concern | Standard | Notes |
|---|---|---|
| Quote anchoring | W3C Web Annotation `TextQuoteSelector` | `exact` after normalisation, `prefix`/`suffix`; "the text MUST be normalized before recording" |
| Fuzzy-matching counterexample | Hypothes.is `match-quote.ts:99` | `maxErrors = min(256, quote.length / 2)` — a 50% error budget suited to highlighting, not to a gate |
| Deprecate-never-delete | Wikidata rank model | P2241 reason for deprecated rank, P248 stated in, P304 pages, P813 retrieved, P1683 quotation, P1065 archive URL |
| Claim with support and challenge | Micropublications, DOI 10.1186/2041-1480-5-28 | minimal form is a statement with its attribution; maximal is the complete supporting argument |
| Sourcing and uncertainty vocabulary | ODNI ICD 203 / 206 | separates likelihood (seven probability-anchored bands) from confidence; requires source descriptors and source summary statements |
| Portability | OKF, `GoogleCloudPlatform/knowledge-catalog` | Apache-2.0; both existing projects independently target its conformance rule |

## 3. What must still be built

Three things, and only three.

### 3.1 The result contract

A single vocabulary every adapter maps into. The three shipped designs are:

- **states in the type** — four-state `Result` (knowledge-harness);
- **states in a versioned schema** — Imbad0202's `bibliographic_integrity_signal`, which separates
  `deterministic_fact` from `heuristic_advisory` from `process_attestation`, keeps `check_status`
  independent of `finding`, and renders `not_checked`/`unknown`/`degraded` as NOT CLEAN;
- **a two-state result under a reason classifier** — research-hub's `ok: bool` plus
  `is_transient_reason()` at the policy layer.

The second is the strongest for an assembly, because heterogeneous tools produce heterogeneous
evidence classes and the schema is the only design that carries that distinction explicitly. Every
adapter must answer: did the check run, what did it find, and which class of claim is that.

**The forbidden outcome is the silent pass.** An adapter that cannot distinguish an outage from a
clean result must report unresolved, not clean.

### 3.2 The policy layer

Which check closes which surface, and at what severity. Three findings constrain it:

- HALLMARK: **false-positive rate, not recall, decides deployability.** At the base rates measured
  for arXiv, bioRxiv and PMC, the best rule-based verifier benchmarked yields one true finding per
  27 to 50 flags.
- Therefore close on **closed-universe checks** — does this citekey exist in the export, does this
  note exist — where a miss is a fact and the false-positive rate is near zero by construction; and
  **warn on open-registry lookups**, where it is not.
- Pre-register the thresholds as data. Two third-party components do part of this:
  llm-wiki-compiler's `.llmwiki/eval/thresholds.yaml` and its fail-closed
  `.llmwiki/config.json` review policy, where an unknown mode or a corrupt config aborts the
  compile rather than silently disabling the policy (MIT **[F]**); and the PRISMA protocol
  templates shipped by Imbad0202 and medsci `fill-protocol`, which carry the domain's own practice
  of registering a method before collecting the evidence.

  Neither pre-registers the *decision*, only the number. **In-house prior art:** Memoria's
  `decision_rules.py` does — `id / blocker / metric / window / threshold / recommendation / check /
  status`, seventeen rules written before their evidence arrives, assessment pure and application
  human-gated, with two rules instrumenting gate abandonment directly (*"if skipped, simplify the
  gate"*; *"any routine push means the policy is wrong"*). That shape has no third-party
  equivalent found, so an assembly either reimplements it or goes without.

### 3.3 The claim addressing

`citekey#^claim-id` with typed `supports`/`disputes`, or an equivalent. No component provides it.
The standards in §2.12 provide the model; the implementation is yours.

## 4. Architecture

```
Zotero + BBT ──auto-export──► bibliography.json        (citekey universe)
     │
     └── zotero-mcp / pyzotero ──► projection ──► vault/literatures/*.md
                                   (lit-sync shape)

vault/ (Obsidian conventions, OKF-conformant, git)
     ├── literatures/   projected, never free-written
     ├── synthesis/     hermes thresholds + lint rules
     └── projects/      drafts carrying claim addresses

              ┌──────────────── the built part ────────────────┐
              │  adapters → result contract → policy → surfaces │
              └────────────────────────────────────────────────┘
                     ▲              ▲              ▲
        bibverify ───┘   medsci checks ─┘   retraction sweep ─┘
        harcx            _quote_match       RW CSV + Crossref
        citation-checker check_claim_fidelity  + OpenAlex is_retracted

surfaces: PostToolUse warn · pre-commit · CI · Stop gate at publish
retrieval: obra/knowledge-graph (SQLite + sqlite-vec + FTS5, MCP)
output:    pandoc + CSL · medsci sync-submission · prisma-automation
eval:      HALLMARK, reported as FPR and MCC first
```

## 5. What the assembly buys, and what it costs

**Buys.** Roughly 1,600 lines of stdlib verification scripts, 49 reporting checklists, a retrieval
and graph layer with an MCP server, 11 literature databases, ~30 submission-integrity checks, a
three-source retraction sweep design, and a benchmark — none of it written here. It also buys
*other people's failure modes already found*: `_quote_match.py` exists because thirteen false
positives were traced to contiguous-string matching, and that knowledge arrives with the file.

**Costs.** A dependency surface neither existing project has. knowledge-harness is stdlib-only;
Memoria adds `yaml` and provider keys. This assembly adds Node (obra/knowledge-graph),
`sqlite-vec`, `python-docx`, pandoc as a binary, and several PyPI packages — each with its own
release cadence, and each a place where a result contract can silently drift.

It also costs **licence surface**: AGPL (Zotero), GPL-2.0 (pandoc, as a binary), Apache-2.0,
CC for the retraction dataset, undeclared for the CSL styles and two tools, proprietary for the
document renderers, and CC-BY-NC for the single best retraction resolver — which must be
re-derived rather than used.

## 6. Risks, most serious first

1. **Inherited result semantics.** §1.B is not hypothetical: one surveyed verifier reports an
   outage as a pass. Every adapter is a place that error can enter, and it enters silently.
2. **False-positive accumulation.** Assembling more verifiers raises recall and raises FPR, and
   HALLMARK measures agentic any-no-match flagging at ~5× the false-positive rate of a conservative
   rule-based reference — attributing the rise to the harness, not the model. An assembly is that
   harness by construction. Mitigation is §3.2's closed-universe/open-registry split, and it must
   be designed in, not added later.
3. **Semantic Scholar throttling**, which HALLMARK documents as collapsing two tools below 7%
   coverage.
4. **Version drift across a dozen upstreams**, against two projects that today depend on almost
   nothing.
5. **The vendoring obligation.** Every adopted file carries a re-vendor duty and a provenance
   header, and the K-Dense case proves per-file licences inside a permissive repository are real.

## 7. What would falsify this approach

- The result contract proving impossible to write honestly for some adapter — a tool whose output
  genuinely cannot distinguish outage from finding, and which is load-bearing.
- The assembled false-positive rate, measured on HALLMARK and extrapolated to a 0.2–0.4% base rate,
  landing worse than either existing project measured the same way. **Neither has been measured**,
  so this is the first experiment to run, and it applies equally to all three designs.
- The integration layer growing past the ~10,000 lines knowledge-harness already is, at which point
  the assembly has bought nothing and owes maintenance to a dozen upstreams.

## 8. Verdict

Assembly is viable for **breadth** — discovery, projection, retrieval, rendering, submission,
reporting guidelines, evaluation — and this is the same conclusion the product comparison reaches
in §17.2 by a different route: build the trust core, adopt the breadth.

It is not viable for the **trust core**. The result contract, the closure policy and the claim
addressing have no donor, and they are precisely the parts that decide whether the system tells the
truth. An assembled harness is therefore not a third alternative to knowledge-harness and Memoria.
It is what either becomes if it stops writing capabilities and starts writing adapters — which, on
the evidence in §2, would leave most of both codebases unwritten.

---

## 9. Applied to knowledge-harness

Sections 1 to 8 answer the question as asked — could this be assembled from scratch. This section
answers the question that follows from it: **given the harness that already exists, what stays,
what is ported, and what is replaced now.** The sorting rule is §18.1 of the product comparison —
*adopt by default; build only where the artifact decides a verdict* — and it is what makes these
three lists non-arbitrary.

### 9.1 Why skills come first

This is a Claude Code plugin. The nine `SKILL.md` files are what a person invokes; the Python core
is what they call into. Memoria's equivalent surface is **60 operation contracts** under
`product/capabilities/operations/`. On that axis the gap is wider than anywhere in the core, and
the shape of their contract is the single most portable thing in either project.

**Their frontmatter, ours.** A Memoria operation declares:

```yaml
operation_id: analyze-claims
prompt_version: analyze-claims.v1
allowed_tools: [trusted_writer]
allowed_paths: [catalog/, digests/, fulltexts/, notes/, hubs/, projects/]
allowed_network: []
untrusted_fields: [input]
io_schema: {input: selection_or_note, output: claim_analysis}
risk_class: medium
required_checks: [memoria-runtime]
posture: peer-reviewer
```

Ours declares `name`, `description`, and sometimes `disable-model-invocation`. Everything else —
which paths a skill may touch, whether it may reach the network, which of its inputs are untrusted,
what it returns, how risky it is — lives in prose that nothing enforces.

### 9.2 Skills — preserve

| Skill | Why it survives |
|---|---|
| `evidence-conventions` | The Iron Law, the four evidence-boundary tags as a required per-line vocabulary, and the rationalizations table. No comparable tags epistemic status per line (§1.C). This is the skill that carries the doctrine; everything else enforces it |
| `import-source` | Projects only an already-admitted item, and the note is a render rather than an LLM write. Every other ingest surface in the survey takes arbitrary documents. Its three surgical per-claim holds — contradiction, low confidence, schema violation — hold one claim, never the catalog |
| `publish` | The fixed disposition menu, typed-`discard` consent, the correction lifecycle where a tag is added and never deleted, and a bypass that is "recorded, not forgiven" |
| `factcheck-draft` | The only skill anywhere that records what it did **not** check: the `budget-cap` finding names every claim the cap excluded, so silence cannot read as clearance |
| `verify-citations` | Its refusal is the design. It reports grouped by check id and explicitly will not act as the gate even when asked whether one would pass. Thin-wrapper discipline is worth keeping when the thing wrapped decides verdicts |

`project` and `setup-vault` are not on this list. Both are thinner than their counterparts and
neither carries a property nothing else has.

### 9.3 Skills — port from Memoria

1. **The capability contract itself.** `allowed_paths`, `allowed_network`, `untrusted_fields`,
   `io_schema`, `risk_class`, `prompt_version` in skill frontmatter. This is the largest single
   design gap between the two projects, and it is declarative — a frontmatter schema plus a
   validator, not an engine. It also makes several of our prose rules mechanical: "never write
   `literatures/`" becomes an `allowed_paths` line a lint can check.
2. **The `integrity-*` operation family.** Eight of them: `integrity-claim-quote-check`,
   `integrity-quote-anchor-check`, `integrity-evidence-check`, `integrity-contradiction-check`,
   `integrity-link-target-check`, `integrity-provenance-checkpoint`,
   `integrity-prompt-injection-check`, `trace-integrity-scan`. Ours are CLI checks reported by one
   skill; theirs are addressable operations with their own contracts. The prompt-injection one is
   the §11.2 gap as a shipped capability.
3. **The argument-quality operations.** `red-team-argument` ("make the strongest grounded
   counter-case against an argument"), `check-falsifiability` ("check whether input claims are
   empirically falsifiable"), `surface-tensions`, `analyze-project-argument`. We have
   `disputed-claim` surfacing and nothing that attacks a draft on purpose.
4. **`prompt_version` as a checked field.** Imbad0202 pins its judge prompt version as an invariant
   (§2.5 lineage); Memoria versions every operation prompt. Our `factcheck` finding identity is the
   claim text hash alone, so changing how we prompt an adjudicator does not reopen prior findings.
5. **Operation granularity as an option, not a default.** Sixty small contracts versus nine
   workflows is a real trade: theirs is addressable and composable, ours is fewer things to learn.
   Worth taking deliberately rather than drifting into.

### 9.4 Skills — mirror from third parties

The comparison's §18.9 establishes mirroring a whole skill — copy the directory verbatim, carry its
licence beside it, add the provenance header, rename only into our namespace. All verified MIT.

| Mirror | Fills |
|---|---|
| cookjohn `cnki-skills`, `gs-skills` | CNKI and Google Scholar coverage `find-sources` cannot reach at all |
| WenyuChiou `gap-to-topic` | The three-gate go/no-go dossier — the step upstream of `project`, which frames a question and never asks whether it should be asked |
| medsci `check-reporting` | 49 reporting guidelines, verified-permissive rows only |
| medsci `manage-refs` | Rendering, marker conversion and Zotero CWYW field codes — the writing half of reference handling we have none of |
| hermes `llm-wiki` rules | Page-splitting and archival thresholds, backlink checks, index-scaling and log rotation — `synthesis-conventions` has the 2+-source threshold and none of the scale rules |
| claude-obsidian `wiki-retrieve`, `wiki-query` | A retrieval surface, if obra/knowledge-graph is not taken as the dependency instead (§9.7) |

**Not mirrored:** PHY041 `claude-skill-citation-checker` and htlin222 `research-guardian`. Both are
MIT and both decide verdicts — the §9.8 line.

**Skill-set governance**, from mattpocock/skills and obra/superpowers rather than from any research
tool: a `skills` array in `plugin.json` (ours has none), bucket promotion for skills being trialled
or retired, a Codex-side invocation policy to match our `disable-model-invocation`, a docs page per
promoted skill, and per-agent conformance tests. superpowers runs those across eight agents; we run
none, while authoring in a portable format precisely so other agents can use them.

### 9.5 Core — preserve

| What | Where | Why it survives |
|---|---|---|
| Zotero + Better BibTeX citekey spine | `zotero.py`, `bibliography.py` | Nothing among 35 products, and nothing in Memoria, joins a reference manager, a vault and every check on one key. Memoria's plan is `zotero-bulk-import` — "admit to catalog, none to knowledge" |
| `citekey#^claim-id` and typed stance links | `claims.py`, the claim-immutability lint | No donor found. The precedents are standards, not code (§2.12) |
| ~~Quote correspondence against source text~~ | `quotes.py`, `selectors.py` | **Claim withdrawn.** Memoria ships `integrity-claim-quote-check` — "check whether a claim's quoted evidence appears in its source" — and `integrity-quote-anchor-check`. An earlier draft read only its `evidence-text-drift` hash-pin and concluded it did not compare against source. It does. What remains ours is the W3C prefix/suffix selector storage and the `fuzzy-quote` reason code, and neither has been compared against their implementation |
| Four-state `Result` and the frozen registries | `outcome.py`, `inbox.py` | This *is* §3.1's result contract, already owned: 18 reason codes and 15 check ids enforced by the writer |
| Hook surfaces | `hooks/` | The one differentiator that survived three narrowings. Memoria is a CLI; every competitor needs an operator flag |
| Publication lifecycle | `publish.py`, the published-drift lint | Tags are never deleted and a correction adds one. Every other product stops when the artifact ships |
| Zero-dependency core | `knowledge_harness/` | Cheap to keep, expensive to regain — and §5 shows what an assembly costs here |

**This bucket is contingent.** Rows four to six are only assets while the false-positive rate is
low enough that a person leaves the gate armed (§6.2). Unmeasured, they are a bet.

### 9.6 Core — port from Memoria

In-house, so this is porting rather than importing. Ranked by value.

1. **`decision_rules.py`.** Pre-registered rules — `metric / window / threshold / recommendation` —
   with assessment pure and application human-gated. Answers our unevidenced `0.90` fuzzy threshold
   and `--cap 30` directly, and its `evidence-review-sizing` rule instruments gate abandonment,
   which §6.2 names as the deciding risk. The highest-value item in this document.
2. **Per-finding severity.** `_FINDING_FIELDS` carries none, so a trivial and a serious instance of
   the same check are identical to the gate.
3. **A `no-refutation` finding kind.** Flags a claim for which no counter-evidence was considered.
   Our `disputed-claim` fires only when disputes already exist — we detect contested claims and
   never uncontested ones that ought not to be.
4. **The consequence walk in `propagation.py`.** When a source falls, what loses its grounds. We
   have `disputes` edges and no closure over them.
5. **`message.relation.is-retracted-by`.** One Crossref field we do not read (§2.6). Smallest item
   here and nearly free.
6. **`read_barrier` / `check_status == "checked"`.** The machine half of admission. It does not
   replace the human act; it enforces it at consumption.
7. **Code grounds.** `code-grounds:<run>:<artifact>:sha256`. Nothing anywhere has it. Park until
   analysis work lands, then it is the other half of citation.

### 9.7 Core — replace with third-party now

| Replace | With | Why now |
|---|---|---|
| The contiguous find in `selectors.find_context` | medsci `_quote_match.py` | Measured: our find misses line-number and column-bleed cases it grades PARTIAL and INTERLEAVED. Wire at `__main__.py:257-263`, not at `check_quote` — both sides of that comparison are vault text |
| Nothing — we have no retrieval | obra/knowledge-graph | Our largest single gap, MIT, SQLite + FTS5 + MCP. Do not build one |
| Duplicate detection we lack | medsci `check_reference_duplication.py`, `check_citation_keys.py` | stdlib, small, complement rather than replace our `citekey` check |
| Building an evaluation harness | HALLMARK as a fixture | Its six sub-tests already map onto four of our checks; registering a baseline is a supported operation |
| Any future renderer | pandoc + CSL | Both medsci and pedrohcgs shell out rather than reimplement |
| Building reporting-guideline support | medsci `check-reporting` | 49 checklists, verified-permissive rows only, plus its `LICENSES.md` discipline |

### 9.8 What is deliberately not replaced

`verify.py` and `checks.py` stay ours. bibverify, `harcx`, `bibtex-updater` and CiteVerifier are
all MIT and all tempting, and every one of them decides a verdict — which is exactly where §18.1
says adoption stops. K-Dense's `validate_citations.py` returning `True` on a network failure is the
concrete cost of getting that boundary wrong.

### 9.9 Net effect

**The core** shrinks toward four things: the spine, the addressing, the result contract, and the
gate. Everything around them comes from somewhere else, and two of the four already exist here.

**The skills** shrink further, and change shape rather than only shrinking. Five survive as written
because each carries a property nothing else has. Two — `project` and `setup-vault` — are thinner
than their counterparts and survive by scope rather than by merit. Six more arrive by mirroring.
And the frontmatter contract every one of them declares stops being three fields of prose and
becomes a declaration a lint can check.

That second half is the larger change, and it is the one this section originally missed. The
comparison document spends four hundred lines on skill-by-skill analysis; the first draft of §9
spent none, and sorted `.py` modules as though the plugin were a library. It is not: the skills are
the product surface, the core is what they call into, and the gap against Memoria is wider at the
skill layer than anywhere in the Python.

Both halves are the same conclusion the product comparison reaches in §17.2 — build the trust core,
adopt the breadth — now with named files and named skills on both sides of the line.
