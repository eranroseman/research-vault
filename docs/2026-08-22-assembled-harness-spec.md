# An assembled harness: the same thesis from third-party parts

Design exploration, 2026-08-22. **Not approved, not planned, nothing built from it.** It answers
one question: could the thing knowledge-harness and Memoria are both building be assembled from
components that already exist, rather than written?

Every component named below was inspected during the 2026-08-22 product survey. Licences are as
verified then, and marked **[F]** where a file was opened and **[M]** where the row rests on
repository metadata and the project's own description.

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
| Retraction, three sources | Memoria's sweep design | MIT **[F]** | Retraction Watch CSV (Crossref-owned, freely distributed, loaded locally and indexed by `OriginalPaperDOI`) → Crossref `update-to[]` **and** `relation.is-retracted-by` → Open Retractions as an independent cross-check. The best design of the three surveyed |
| Retraction dataset | gitlab.com/crossref/retraction-watch-data | CC **[M]** | the offline, deterministic leg |
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
- Pre-register the thresholds. Memoria's `decision_rules.py` is the model: `id / blocker / metric /
  window / threshold / recommendation / check / status`, written before the evidence arrives, with
  assessment pure and application human-gated. Two of its seventeen rules instrument gate
  abandonment directly — *"if skipped, simplify the gate"*, *"any routine push means the policy is
  wrong"*.

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
        citation-checker check_claim_fidelity  + Open Retractions

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
