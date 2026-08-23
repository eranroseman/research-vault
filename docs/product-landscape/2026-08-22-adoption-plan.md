# Adoption plan

Decision note, 2026-08-22. Updated as we act on it, unlike its two sources.

This is the actionable half of the 2026-08-22 pass. It was previously split across two documents —
the positioning verdict and the vendoring classification lived at §17 and §18 of
[the product comparison](2026-08-22-product-comparison-verified.md), and the per-file actions at §9
of [the assembled-harness note](2026-08-22-assembled-harness-spec.md). Both restated the same
adoption targets, and the same fact had already needed correcting twice in both places. Merging
them removes the drift by construction rather than by discipline.

The evidence behind every claim here lives in the comparison; this note cites it and does not
repeat it. **Section 0 states what is executable when** — the pre-baseline window has closed, one class of
change can proceed regardless, and one waits for the validation slice. Three parts after that: **why the product has a place** and on what condition, **what is
adoptable** and at what tier, and **what changes in this tree** and in what order.

---

## 0. Sequencing — the pre-baseline window has closed

This section has been wrong twice, in opposite directions, and both errors came from reading the
wrong tree. The corrected state, read from the worktree on 2026-08-22:

**Plan Q is deep in flight**, not unstarted. It runs on `build/quality-lane` at
`.claude/worktrees/build+quality-lane`, **18 commits above its merge base**, with Tasks 0–3
complete and Task 4 — the mutation gate — in progress at `f61c14b`. The plan document on `main`
shows 0 of 38 boxes ticked because execution lives on the branch; a checkbox count on `main` says
nothing.

**Task 0 was the window, and it is closed.** Plan Q's Task 0 is defined as "the last planned
pre-baseline churn", and Task 4's Step 0 refuses to build manifests with Task 0 work pending. Task
0 shipped at `2f5de3c`. So the slot that existed for disruptive pre-baseline changes has been used
and closed by design, and the ledger shows the plan being held to that line repeatedly — nine
deferred minors in Task 2 alone, each named rather than absorbed.

Adding vendored modules to `knowledge_harness/` now would therefore (a) reopen a batch declared
closed, (b) perturb the in-flight CRAP and coverage measurements that Task 3's controller
explicitly guarded, and (c) put unmeasured code into the baseline that exists to measure the
codebase.

### 0.1 What that leaves, by class

| Class | When | Why |
|---|---|---|
| **Gaps where we have nothing** — retrieval, full-text acquisition, a drafting skill, reporting checklists, submission integrity, session continuity | **now, independent of Plan Q** | none of these lands in `knowledge_harness/`; they are skills, mirrors and external tools. They perturb no measurement, and there is no "is ours better" to test because there is no ours |
| **Replacements of code we own** — `_quote_match` at the selector site, duplicate detection | **after Plan Q merges** | the Task 0 slot is closed and Task 4 is imminent. This is the conclusion an earlier draft reached for the wrong reason and a later draft overturned on a false reading |
| **The tested path** — the result contract, the closing sets, the claim addressing | **after the validation slice** | the only place "is ours better" is a real question, and the only place Plan S answers it |

The rule that survives all three revisions: **do not change the gate before the thing that tests
the gate runs, and do not change measured code while it is being measured.** The first is about
Plan S, the second about Plan Q, and neither is an argument for delaying the first row.

### 0.2 What Plan Q is already producing for this plan

Two of its outputs land directly on questions raised here.

**The mutation baseline is §3.2's missing measurement.** §3.2 argues a code fork is cheap to hold
because tests keep it still. Task 4's "no new survivors" gate is exactly the instrument that makes
that true or false per module, and its CRAP table names complexity surviving at full coverage. If
survivors cluster where a fork would land, the code half of the asymmetry weakens. The skills half
is unaffected — nothing measures prose either way, which is the argument.

**Skill-frontmatter validation already shipped.** Task 2's config-validity suite parses every
`skills/*/SKILL.md` with the core's own `frontmatter.parse` and asserts `name` equals the directory
name, `description` is non-empty, and any `disable-model-invocation` is boolean. That is the
structure half of the §11.6 routing gap, closed. The firing half — does the right skill activate
for a real phrasing — remains open, and that suite is its natural home.

### 0.3 One carve-out

`message.relation.is-retracted-by` (§3.6, item 5) is a single additive Crossref field. No rename,
no new module, no behaviour change to anything Plan Q measures or Plan S tests. It is the only item
here that could ride any window, and even it is better folded into a plan than landed loose.

---

## 1. The verdict

**Epistemic status.** Parts I–IV are evidence: every claim traces to a file, a spec or an API
response read on 2026-08-22. This section is *judgment* built on that evidence, and it is not the
same kind of statement. It rests on a capability read of roughly 35 repositories — not on market
research. There is no demand data here, no user evidence, and star counts are a distribution proxy
and a poor one in an ecosystem where an agent framework carries 234,000 stars. Every factual claim
below cites the section that verified it; the inferences are mine.

### 1.1 Verdict

Yes, but not in the category the README names. As "a Claude Code harness for knowledge work —
academic research first", the field is crowded and better resourced: Imbad0202 at 43,339 stars with
394 scripts, K-Dense at 34,130 with 163 skills, pedrohcgs with 52, medsci with 59. We ship nine.

As **the gate layer** — the thing that decides whether work may proceed — the position is real,
and on the evidence in Part III nobody occupies it.

**Whether it is habitable is a separate question, and §8.5 opens it.** Part III establishes that no
competitor gates a draft on per-claim evidence by default. The literature establishes that a
default-armed gate survives contact with users only if its false-positive rate is low enough that
they leave it armed, and that at the base rates measured for our corpora the best rule-based
verifier benchmarked yields one true finding per 27 flags on arXiv and one per 50 on bioRxiv. An
unoccupied position and a viable one are not the same claim. This verdict asserts the first; the
second is unmeasured, and §1.5 step 3 is what would settle it.

### 1.2 The build-versus-adopt binary is false, and this repository already resolved it once

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

### 1.3 The differentiator, stated precisely enough to defend

Not "we verify citations". Three other products run registry-backed deterministic verification —
Imbad0202's `verification_gate`, medsci's `verify-refs`, pedrohcgs' `validate-bib --semantic`
(§10.6) — above a Tier-2 shelf of bibverify, doi-mcp and citation-checker (§7).

The verified position is narrower and holds: **the only product whose verification result closes a
commit and a session-Stop surface**, combined with admission as the only path to citability and
`citekey#^claim-id` addressing with typed stance links. Two adjacent claims must stay qualified as
they are in §12: the citekey join is a difference of degree from medsci's `lit-sync`, not of kind;
and four-state honesty is convergence with Imbad0202, not a differentiator.

### 1.4 Why "adopt an alternative" is unavailable for the distinctive part

Three credible candidates, failing on different axes. The first draft of this section said
adoption was simply unavailable for the gating thesis; the full surveys of medsci-skills and
research-hub (§6.1, §6.15) show that was too strong, and the accurate statement is narrower.

- **Imbad0202/academic-research-skills** has the strongest verification machinery in the
  comparison (§6.2) and is **CC-BY-NC-4.0** (§15). It can be studied and re-derived; its files
  cannot be copied. It also has no vault and no citekey spine.
- **Aperivue/medsci-skills** matches our substrate exactly and is MIT (§6.1). It gates
  extensively — 33 scripts halt on major findings under `--strict`, 43 call themselves gates — with
  a severity tier and a could-not-run exit we do not have. Two things still separate it. Every one
  of those gates is a **command a person chose to run with a flag a person chose to pass**: the
  repository ships no `plugin.json` and no hooks, so nothing is armed by the harness. And it is
  **domain-locked**: 21 of 59 skills are medical-specific, and it describes itself as
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

### 1.5 What follows

1. **Narrow to the gate.** Keep the core, `verify-citations`, `publish`, `evidence-conventions` and
   `import-source`. Stop treating drafting, rendering and submission packaging as roadmap — those
   belong to medsci and pedrohcgs, who are years ahead on them (§11).
2. **Port two MIT scripts that are gate-layer, not breadth-layer.** medsci's
   `check_claim_fidelity.py` and `_quote_match.py` (§6.1). §10.7 already concedes `factcheck-draft`
   is where we are most clearly behind; these close that gap and *strengthen* the narrow position
   rather than widening scope.
3. **Run HALLMARK against the deterministic suite** (§8.4, §8.5). This has moved from a nice-to-have
   to the step the rest depends on. 2,526 entries, 14 hallucination types, six diagnostic sub-tests
   per entry — four of which map onto checks we already run — and a baseline registry with a
   documented dispatch interface, so registering ours is a supported operation rather than a fork.
   Report **FPR and MCC first**, not detection rate: HALLMARK's central finding is that FPR decides
   deployability, MCC is prevalence-invariant, and a recall figure quoted alone is the number its
   three failure modes exist to warn about. Then extrapolate against Zhao et al.'s measured
   prevalences — 0.39% arXiv, 0.27% PMC, 0.21% bioRxiv — rather than the benchmark's 2%, because
   those are the corpora a knowledge-harness vault is actually built from (§8.5.1).
   Split the report by leg: the closed-universe checks and the open-registry ones are different
   instruments and §8.5.2 predicts they will score differently.
4. **Vendor rather than rebuild** anything breadth-shaped, following the `find-sources` pattern —
   pinned SHA, header-only provenance additions, re-vendor to update. Section 18 works that
   instruction into a candidate-by-candidate list.

### 1.6 Two facts that bear on timing

**Being wrong is cheap.** ADR 0001 makes the vault tool-independent: plain markdown and YAML in
git, structurally conformant to OKF (§4, §8.3). A later pivot to medsci does not strand the
researcher's data. That asymmetry favours continuing.

**The window is not open indefinitely.** medsci-skills was pushed three days before this
comparison and already carries Zotero, an Obsidian vault, citekey provenance and registry
verification (§6.1). It is converging on our substrate from the audit side. If it adds a closing
gate, the distinctive position narrows to nothing. That argues for speed on the gate, not for
abandoning it.

### 1.7 What would change this verdict

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

## 2. What is adoptable, classified

Section 17.5 recommends vendoring rather than rebuilding. This section names what to vendor.
Every candidate below was checked on 2026-08-22 for licence, import surface and coupling; line
counts and import lists come from the files themselves.

### 2.1 The rule the tiers express

**Adopt by default; build only where the artifact decides a verdict.**

The default is adoption because the evidence says so. `find-sources` is already an adoption and it
works. Tier A is roughly 1,600 lines of standard-library Python filling five gaps we would
otherwise write. Tier C's 49 reporting checklists arrive with a licence audit someone else did
properly. Section 17.2's whole argument is that our differentiators are enforcement-layer and our
gaps are breadth-layer, and breadth is what other people have already built.

The exception is narrow and it is not about quality. K-Dense's `citation-management` skill is MIT,
stdlib-adjacent, well organised, and does exactly the DOI-existence work we do. Its
`validate_citations.py` returns `Tuple[bool, Optional[Dict]]`, and on a network failure:

```python
        except requests.exceptions.RequestException:
            return True, None
```

with the comment above it reading "Any other status is a transport problem on our side, not
evidence that the DOI is bad." The reasoning is defensible; the outcome is not. A boolean has
nowhere to put *could not run*, so the outage collapses into a pass.

The precise defect is worth naming, because a two-state result is not automatically wrong.
research-hub's `verify.py` returns `ok: bool` too and is rescued a layer up, where
`authenticity.py` classifies the reason string through `is_transient_reason()` and refuses to read
a transient failure as fabrication. K-Dense has no such layer: the boolean is the answer the caller
gets.

**And K-Dense is not representative — auditing the others on 2026-08-22 showed that.** bibverify
returns `QueryStatus.NETWORK_ERROR` from a ten-state enum, with a contract test asserting it;
`harcx` and `bibtex-updater` return a bool plus a reason and fail toward *not verified*;
CiteVerifier carries `timeout`, `error` and `unknown` verdicts. Four of five handle an outage
honestly. K-Dense is the only one that fails toward **clean**, which is the one direction that
cannot be recovered by a careful caller.

That sharpens the rule rather than weakening it. The test is not "will this tool express an
outage" — most will. It is **which way it fails when it does not know**, and that is a property you
only learn by reading the error path, not the README. It also means our own four-state is not
automatically the best available: bibverify distinguishes rate-limit from auth from network from
parse from provider failure, where our `UNREACHABLE` collapses all five.

So the test for "must build" is not *is this good code* but *does this decide a verdict*. It is
the same line the dependency question resolved to (test 2 below): a dependency is cheap where it
cannot corrupt a verdict and degrades cleanly, expensive in the trust path however well maintained
it is. One line, two questions.

In practice that puts the boundary here: `verify`, the checks, the four-state result, the closing
sets, the reason-code registry and the publish gate are ours to write. Search, capture, rendering,
retrieval, submission packaging, reporting checklists and format breadth are other people's to
write and ours to carry.

### 2.2 The four tests

A candidate is **adopt-as-is** only if it passes all four. Failing any one moves it down a tier,
and the tier is the recommendation.

1. **Licence.** Permissive, and verified in the artifact rather than assumed from the repository.
   K-Dense is MIT at repository level with four proprietary Anthropic skills inside it (§6.12);
   medsci's checklists carry per-file licences that differ from the repository's (§2.5).
2. **Dependency cost, weighed — not a veto.** Our core imports nothing outside the standard
   library today, and that is worth keeping. But it is a guideline, not a rule, and we already
   own the mechanism for breaking it cleanly: `pyproject.toml` carries `pdf = ["pypdf>=4"]` as an
   optional extra, and `selectors.pdf_text` returns `None` on any failure, so the feature degrades
   and the core does not. A dependency behind an extra costs the *feature* a dependency, not the
   core its property.

   So weigh rather than filter. Against a candidate: how many transitive packages, how well
   maintained, does it sit in the trust path, does it degrade cleanly when absent, and would we be
   reimplementing it worse. For it: what capability arrives, and how much of our own code stops
   existing. `python-docx` for field-code injection is one well-kept package buying a capability
   we have none of; `httpx` plus `anyio` plus `pydantic` plus `rich` to read one CSV is not.
3. **Substrate fit.** A file coupled to another project's layout — its registries, its vault
   resolver, its manifest format — is a rewrite, not an adoption.
4. **It fills a gap this document lists.** Otherwise it is scope creep with a provenance header.

### 2.3 Tier A — adopt as-is

Permissive, standard-library only, no coupling beyond a same-directory sibling. Vendor exactly as
`find-sources` was: pinned SHA, comment header, no hand-edits, re-vendor to update.

| Candidate | Lines | Imports | Fills | Note |
|---|---|---|---|---|
| medsci `verify-refs/scripts/_quote_match.py` | 172 | `re`, `unicodedata` | token-ordered quote matching where ours ends in a contiguous find (§6.1) | measured and pinned in §2.10; vendored and dropped pending a wiring decision |
| medsci `manage-refs/scripts/check_citation_keys.py` | 147 | `argparse`, `re`, `sys` | pandoc `[@key]` undefined/unused detection; complements our bibliography-joined `citekey` check | |
| medsci `manage-refs/scripts/check_reference_duplication.py` | 245 | `+ json`, `zipfile` | duplicate-entry detection, listed as absent from our `citekey` check (§10.6) | |
| medsci `sync-submission/scripts/cross_document_n_check.py` | 486 | `argparse`, `json`, `re`, `sys` | the same participant count asserted across every document — a cross-artifact consistency class we have none of (§11) | |
| medsci `version-dataset/scripts/*` | small | `hashlib`, `json`, `argparse`, `pathlib` | deterministic content-hash manifest for a dataset (§11, research-data reproducibility) | closest fit to our existing `fixity-sha256` thinking |
| medsci `search-lit/scripts/check_doi_record_match.py` | 276 | `urllib`, `csv`, `difflib.SequenceMatcher` | DOI-to-record matching with fuzzy title comparison; overlaps our `metadata` check and may sharpen its tolerance | stdlib networking, same posture as our `webapi.py` |
| medsci `sync-submission/scripts/check_wordcount_cap.py` | 238 | `+ _yaml_frontmatter` (same dir) | word-count ceilings at submission | vendor the sibling too, as medsci itself does |

`check_xref.py` (740 lines, stdlib) is the largest of these and does manuscript-to-DOCX
cross-reference QC. It passes all four tests but only becomes useful once we render a DOCX, so it
belongs behind the rendering decision rather than in front of it.

**Whole skills, mirrored into `skills/` rather than vendored into the core** (§2.8 gives the
mechanism). All verified MIT and standard-library-only:

| Skill | Repo | Python | Fills | Caution |
|---|---|---|---|---|
| `cnki-skills` | cookjohn | 1 file, stdlib (`urllib`, `hashlib`, `io`, `json`, `re`) | 10 skills over CNKI — search, journal browse, PDF download, export to Zotero. A Chinese-language corpus our vendored `find-sources` cannot reach at all | none; this is pure additional coverage |
| `gs-skills` | cookjohn | 1 file, same deps | 6 skills over Google Scholar | Scholar has no official API; expect fragility |
| `gap-to-topic` | WenyuChiou/research-hub | — | the three-gate go/no-go dossier, upstream of `project` (§6.13) | brings its own `design_brief.md` handoff vocabulary |
| `asta-skill` | Agents365-ai | — | instruction pack over Ai2's Asta MCP for Semantic Scholar | adds an MCP dependency |
| `claude-skill-citation-checker` | PHY041 | 1,180 lines incl. tests, stdlib + `urllib` | `.bib` against CrossRef, Semantic Scholar and OpenAlex | **overlaps our `doi` and `metadata` legs** — a second implementation of work we already do, from the `.bib` side rather than the citekey side |
| `research-guardian` | htlin222 | `runner.py` 717 lines, stdlib | multi-gate audit of hypotheses, citations, experiments, results and logic fallacies, with a JSON schema and seven reference files | **overlaps `factcheck-draft`** — LLM-judgment gates, not deterministic checks |

The last two are the ones the licence correction unlocked, and both duplicate capability we have
rather than adding capability we lack. That is the honest shape of this change: correcting seven
licences widened what we *may* adopt considerably more than it widened what we *should*.

### 2.4 Tier B — fork a function, not a file

Permissive and stdlib, but coupled to the donor's data shapes. Take the algorithm, write our own
seam, credit in a header comment.

| Candidate | What to take | Why not as-is |
|---|---|---|
| claude-obsidian `claude_obsidian/ledgers.py::_independent_group_count` | union-find collapsing sources that share an origin, content hash or declared independence key, so they cannot corroborate each other (§6.4) | operates on the donor's ledger record shape; the algorithm is about thirty lines and the value is entirely in the idea |
| medsci `verify-refs/scripts/check_claim_fidelity.py` | the graded-by-checkability probe design: quoted text is decidable, attribution is not, so only the extreme case fires (§10.7) | 644 lines whose CLI takes `--manuscript --fulltext-dir --bib --refmap` — bound to their layout |
| claude-obsidian `scripts/bm25-index.py` | a pure-stdlib BM25 index in 851 lines, with an honest documented no-op when the optional reranker is absent | imports `claude_obsidian.paths` and `claude_obsidian.transaction`; the retrieval decision is not made anyway (§11) |
| swarmvault `packages/engine/src/watch.ts` | the shrink-ratio circuit breaker: refuse a refresh that drops nodes or edges by more than 25% (§6.7) | TypeScript; the mechanism is a comparison and a threshold, perhaps twenty lines in Python |
| research-hub `authenticity.py` | the layered gate shape, and specifically the transient-versus-permanent split that admits under a recheck marker rather than blocking (§6.15) | the `requests` import is not the obstacle — our `webapi.py` already does the same work over `urllib` — but it also imports five project modules (`dedup`, `locks`, `search.crossref`, `security`, `utils.doi`), and those are the rewrite |

### 2.5 Tier C — adopt as data

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
- **rpatrik96/hallmark** — MIT, 2,526 labelled entries (826 valid, 1,246 hallucinated, plus a
  454-entry held-out split), 14 hallucination types, 3 difficulty tiers, a baseline registry of
  19+ variants. Use as an evaluation fixture; vendor no code. This is step 3 of
  §1.5 and the cheapest credibility move available.

### 2.6 Tier D — depend, do not vendor

Real tools doing real work, too large or too external to carry.

| Tool | Licence | Role |
|---|---|---|
| microsoft/markitdown | MIT, 175,520 stars | the format-breadth answer if `import-source` ever ingests beyond Zotero; SamurAIGPT already routes through it (§6.10) |
| pandoc + CSL | GPL, external binary | rendering and citation formatting; medsci `manage-refs` and pedrohcgs `compile-latex` both shell out to it rather than reimplementing |
| Hylouis233/bibverify | MIT | a second opinion on a `.bib`, with `rank_lookup_sources` explaining resolver choice — but it duplicates our DOI and metadata legs, so only worth it if that explanation is wanted (§7) |
| htlin222/prisma-automation | MIT, 8 stars | PRISMA flow-diagram generation, the one piece of systematic-review apparatus that is a discrete artifact rather than a workflow |
| kepano `defuddle` | MIT | already provisioned by `setup-vault`; the web-capture answer if one is needed |
| obra/knowledge-graph | MIT (README) | vault-as-knowledge-graph over SQLite with sqlite-vec and FTS5, local embeddings, Louvain communities, betweenness and PageRank, exposed as a CLI and an MCP server with a `prove-claim` skill. Node and TypeScript, so a dependency rather than a vendor target — but the single closest answer to our largest gap (§11, retrieval and graph) |
| introfini/ZotSeek | MIT (README + `package.json`) | a Zotero plugin in JavaScript giving local semantic search over the library with a built-in MCP server. Runs inside Zotero, so it is a companion to provision like kepano rather than anything to carry |
| TonybotNi/ZotLink | MIT (`setup.py`) | saves preprints into Zotero with metadata and PDFs. Imports `bs4`, `playwright`, `requests`, `mcp`, `pydantic`, `dotenv` and `fake_useragent` — the last of those is a posture we would not want anywhere near the evidence path, so: dependency at arm's length, or not at all |

### 2.7 Tier E — pattern only, and why

Worth reading, not worth carrying. Each fails a specific test.

- **Imbad0202, everything** — CC-BY-NC-4.0. The integrity-signal contract, the injection probes,
  the judge-prompt-version pin and the uncited-assertion detector are all re-derivable and none is
  copyable (§6.2, §15).
- **paper-qa `journal_quality.py`** — 216 lines importing `anyio`, `httpx`, `httpx_aiohttp`,
  `pydantic`, `rich`, plus `paperqa.types` and `.client_models`. Weighed rather than vetoed: five
  runtime packages is a poor trade for one signal, and the internal coupling means we would be
  rewriting it anyway. The venue-quality gap is real, but the route to it is the underlying
  journal-quality data, not this wrapper around it.
- **medsci `manage-refs` rendering scripts** — import `python-docx`, and vendor their own
  `_vendor_citation_writer` beside it. This is the candidate where the trade-off most plausibly
  favours taking the dependency: one well-maintained package, behind a `docx` extra alongside our
  existing `pdf` one, buying native Zotero CWYW field-code injection and journal-CSL rendering that
  we have no version of. It sits outside the trust path — it writes a submission artifact, it does
  not decide anything — which is what makes the dependency cheap. The counter-argument is that
  pandoc already renders DOCX and medsci shells out to it for exactly that; `python-docx` earns its
  place only for the field codes pandoc cannot write. Decide it with the rendering decision, not
  before.
- **hermes `grounded-citations`** — MIT, and the closest peer to our quote gate, but its ledger
  exists because web sources have no stable identifier. Our citekey universe already is that
  ledger (§6.6).
- **gbrain, swarmvault, llmwiki** — Postgres, a Node toolchain and a compiled-artifact ownership
  model respectively. Patterns transfer; code does not.
- **WenyuChiou `gap-to-topic`** — MIT and only 219 lines of SKILL.md plus references, evals and
  scripts, so it is nearly adoptable. It is listed here rather than in Tier A because a skill is
  prompt text bound to its own vocabulary and downstream handoff (`design_brief.md` frontmatter
  carrying `source` and `gap_verdict`); adopting it means adopting that flow (§6.13).

### 2.8 Tier F — do not touch

- **anthropics/skills `docx`, `pdf`, `pptx`, `xlsx`** — verified proprietary in the K-Dense mirror:
  `skills/docx/LICENSE.txt` opens "© 2025 Anthropic, PBC. All rights reserved." Check
  `THIRD_PARTY_NOTICES.md` before assuming anything about the originals (§6.12, §15).
- **jason-effi-lab/karpathy-llm-wiki-vault** — the only repository in the roster with no licence
  in any form, which is all rights reserved rather than public domain (§15). Read it on GitHub;
  carry nothing.

Everything else once listed here was a detection failure, not a licence failure (§15).
- **sdyckjq-lab/llm-wiki-skill's `workbench/.claude/skills/{docx,pdf,pptx,xlsx}/`** — the
  repository is MIT, that subtree is not (§15). The trap is the same one K-Dense sets, and it is
  why test 1 in §2.2 says *verified in the artifact*.

### 2.9 Mirroring a whole skill

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

This mode sidesteps §2.2's third test, because a skill is self-contained by design — it brings its
own prompt, scripts and reference files rather than reaching into a host layout. That widens the
candidate set considerably now that the licences are established:

| Skill | Repo | Licence | Fills |
|---|---|---|---|
| `claude-skill-citation-checker` | PHY041 | MIT (README) | `.bib` against CrossRef, Semantic Scholar and OpenAlex — a second opinion beside our own DOI and metadata legs |
| `research-guardian` | htlin222 | MIT (README) | multi-gate audit of hypotheses, citations, experiments, results and logic fallacies |
| `gap-to-topic` | WenyuChiou/research-hub | MIT | the three-gate go/no-go dossier, the one thing upstream of `project` (§6.13) |
| `cnki-skills`, `gs-skills` | cookjohn | MIT | CNKI and Google Scholar coverage our vendored `find-sources` lacks entirely |
| `asta-skill` | Agents365-ai | MIT | Ai2's Asta MCP over Semantic Scholar, as an instruction pack |
| medsci `verify-refs`, `manage-refs`, `check-reporting` | Aperivue | MIT (per-file for checklists, §2.4) | reference audit, rendering and 49 reporting guidelines as whole units rather than script by script |

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

### 2.10 `_quote_match`, measured — and where it would actually go

This candidate was vendored and removed during the same session, so the measurement survives only
here. Both parts are worth keeping: the behaviour, and the integration target, which is not the one
an obvious reading suggests.

**Measured.** Run standalone against a quote and three damaged haystacks, with our own contiguous
find for comparison:

| Artifact class | `match_quality` grade | matched / total | inserted | coverage | our contiguous find |
|---|---|---|---|---|---|
| line number mid-sentence | `PARTIAL` | 7 / 8 | 3 | 0.875 | **miss** |
| two-column bleed | `INTERLEAVED` | 8 / 8 | 1 | 1.0 | **miss** |
| hyphenation across a line break | `EXACT` | 8 / 8 | 0 | 1.0 | match |
| unrelated text | `ABSENT` | — | — | — | miss |

The third row is the one our `selectors._norm_with_map` already repairs. The first two are what a
contiguous find cannot see. The fourth is the row that matters most, and it is why the grade
vocabulary is worth more than the matcher.

**Where it goes, and where it does not.** The obvious target is `quotes.check_quote`, and that is
wrong: both sides of that comparison are vault strings — the claim's quote text against the
literature note's managed region — so PDF extraction artifacts cannot arise there.

Extraction noise enters at `__main__.py:257-263`, where `selectors.pdf_text` extracts an
attachment and `attach_contexts` locates each annotation to capture its prefix and suffix. When
`find_context`'s contiguous find misses, the annotation silently loses its W3C selectors and the
import reports one undifferentiated reason: `"some annotation quotes were not found in extracted
text"`.

Graded, that single reason splits into two facts we currently cannot tell apart:

- `INTERLEAVED` or `PARTIAL` — extraction noise. The annotation is sound; `pypdf` interleaved a
  line number or bled a column. Degradation, retry later.
- `ABSENT` — the annotation text is **not in the PDF we hashed**. That is an integrity condition,
  not a formatting one: either the attachment on disk is not the one that was annotated, or the
  "quote" was typed as a comment rather than selected from the page. We carry `fixity-sha256` on
  the file and nothing that checks its annotations correspond to it.

The second is fabrication-shaped and today invisible. That is the argument for the port, and it
sits on the evidence layer rather than in the quote check — which also means it changes what an
import reports, so it deserves the same care as any change to a verification surface.

### 2.11 What this changes about sequencing

Tier A now has two halves. The **files** are roughly 1,600 lines of standard-library Python under
one MIT licence from one donor, filling five listed gaps — the cheapest breadth we will ever
acquire, at one re-vendor obligation each. The **skills** are broader but thinner: of the six,
`cnki-skills` and `gs-skills` add corpora we genuinely cannot reach, `gap-to-topic` adds a step
upstream of `project`, and the remaining two duplicate `verify-citations` and `factcheck-draft`.

Tier C's reporting checklists remain the largest single capability gain, and the one whose licence
question someone else has already answered carefully.

The sequencing implication for §1.5 is that vendoring is not step 4. It is the step that makes
steps 1 and 2 affordable, because every file in Tier A is breadth we then do not have to build
while narrowing to the gate.

---

---

## 3. What changes in this tree

Sections 1 to 8 answer the question as asked — could this be assembled from scratch. This section
answers the question that follows from it: **given the harness that already exists, what stays,
what is ported, and what is replaced now.** The sorting rule is §2.1 of the product comparison —
*adopt by default; build only where the artifact decides a verdict* — and it is what makes these
three lists non-arbitrary.

### 3.1 Why skills come first

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

### 3.2 Skills — what would we write today?

The wrong question is *which of our skills are distinctive*. Distinctiveness is a fact about the
market, not an argument for existing, and answering it would just relabel the current nine as
justified. The question this document is actually about is **which of them would we write if we
were assembling the harness now**, knowing what §2 makes available. Three tests, all of which must
pass:

1. Does the job need doing at all?
2. Does nothing in §2 already do it?
3. Is a *skill* the right shape — as against a lint, a CLI verb, or a schema?

Applied honestly, only one of the nine passes all three unchanged.

| Skill | Verdict | Reasoning |
|---|---|---|
| `evidence-conventions` | **Write it, unchanged** | The job is needed and nothing in §2 does it — no component tags epistemic status per line. Test 3 is the interesting one: most of what it says is enforced mechanically by lints and checks, so why is it prose? Because it steers authoring *before* any lint runs. A claim that never gets written wrong costs nothing to fix. That is a skill's job and not a linter's |
| `publish` | **Write it, unchanged** | Nothing in §2 gates a session; §2.10 confirms every other enforcement surface needs an operator flag. The disposition menu, typed-`discard` consent and the correction lifecycle are judgment scaffolding, which is skill-shaped by definition |
| `import-source` | **Write it thinner** | The projection half is medsci `lit-sync` (§2.4). What remains ours is the admission boundary, the render-first no-op and the three surgical per-claim holds. Those are perhaps a third of the current skill; the rest is orchestration we would not write from scratch if `lit-sync` were mirrored |
| `factcheck-draft` | **Write it much thinner** | §3.7 adopts medsci `check_claim_fidelity.py`, which answers the same question deterministically. What survives is the part code cannot do — adjudicating a paraphrase's direction, magnitude and certainty — plus the budget-cap honesty, which is a contract of about twenty lines rather than a skill |
| `verify-citations` | **Probably not a skill** | It "ships no mechanics of its own" by its own text: it runs a verb and reports grouped by check id. That is a CLI output format and a reporting rule. Its one genuinely skill-shaped property is the refusal to act as the gate when asked — worth keeping as a rule, not obviously worth a skill file |
| `find-sources` | **Already not ours** | A vendored fork of `paper-lookup` plus a search log and an admission boundary. From scratch we would mirror the upstream and write the log as a CLI verb |
| `synthesis-conventions` | **Write it, but import the rules** | The 2+-source threshold is right and matches hermes independently. Everything else it lacks — page splitting, archival, backlink checks, index scaling — hermes already specifies (§3.4). From scratch this is mostly a mirror with our thresholds substituted |
| `project` | **Would not write it as it stands** | Orientation, inbox drain, trust tiers, four-element framing and gap analysis in one skill. WenyuChiou `gap-to-topic` does the framing gate better, the pedrohcgs cluster does continuity better, and the inbox drain is a CLI report. It survives on scope, not merit |
| `setup-vault` | **Would not write most of it** | Scaffolding is a CLI verb; companion provisioning is an installer concern; the Zotero wizard steps are the only genuinely skill-shaped part, because they are the bit a machine must refuse to do |

**What this changes.** The preserve list is not five skills — it is **two written as they are, two
written smaller, and five that from scratch would be a CLI verb, a mirror, or a rule in someone
else's file.** That is a sharper result than "these are distinctive", and it points the same way as
§3.9: the surface shrinks toward the gate and the doctrine, and most of the rest is orchestration
that only exists because we wrote the capabilities ourselves.

#### The asymmetry that decides this, and it runs the other way from code

An earlier draft closed here with a caution: a mirror carries a re-vendor obligation and an
upstream that can move, so trading authorship for a dependency is only conditionally good. **For
skills that is backwards**, and the reason is worth stating because it reorders everything above.

A skill is prose that steers a model. It has no type checker, no unit test that catches a
regression, and no compiler to tell you the edit you just made changed behaviour three paragraphs
away. Testing one means running a model and judging the result; updating one means editing prose
whose failure mode is silent and probabilistic. Code has none of those problems: a fork you
maintain has tests, types and deterministic behaviour, and a regression announces itself.

So the ownership calculus inverts by artifact:

| | Prefer to own | Prefer to adopt |
|---|---|---|
| **Code** | where it decides a verdict (§3.8) — a fork is cheap to maintain because tests hold it still | everywhere else |
| **Skills** | only where nothing exists, or where the vocabulary cannot be reconciled | **everywhere it exists** — authoring and maintaining prose is the expensive half of this product |

Two things follow.

**The mirror is the preferred mode for skills, not a fallback.** §2.9 of the product comparison
treats mirroring as a third adoption mode between vendoring a file and taking a dependency. For
skills specifically it should be the default, and writing one should need a reason.

**A mirror often brings its testing with it**, which is the part hardest to author. medsci ships
`_challenge` fixture directories beside its checks; gbrain ships a `routing-eval.jsonl` next to 41
of its 71 skills; superpowers runs per-agent conformance suites across eight agents. Our own
`test_skill_contracts.py` tests that frontmatter parses and names match directories — structure,
not firing (the comparison's §11.6). Mirroring a well-tested skill acquires an answer to a problem we have not
solved.

**The bound on all of this is vocabulary, not licence.** A mirrored skill arrives speaking its own
terms: `gap-to-topic` hands off through a `design_brief.md` with `source` and `gap_verdict`
frontmatter; hermes' rules assume a `SCHEMA.md`. Prose that contradicts the surrounding doctrine is
worse than no prose, because the model follows whichever it read last. So the real cost of a
mirrored skill is not the re-vendor obligation — it is reconciling its vocabulary with ours, and
that cost is paid once at adoption rather than continuously.

Re-read §3.2's table with that ordering and the five demotions stop being losses. Five skills we
would not write from scratch is five prose-maintenance burdens someone else is carrying, and the
two we would still write are the two where no upstream can carry the doctrine for us.

### 3.3 Skills — port from Memoria

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
   the the comparison's §11.2 gap as a shipped capability.
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

### 3.4 Skills — mirror from third parties

The comparison's §2.9 establishes mirroring a whole skill — copy the directory verbatim, carry its
licence beside it, add the provenance header, rename only into our namespace. All verified MIT.

| Mirror | Fills |
|---|---|
| cookjohn `cnki-skills`, `gs-skills` | CNKI and Google Scholar coverage `find-sources` cannot reach at all |
| WenyuChiou `gap-to-topic` | The three-gate go/no-go dossier — the step upstream of `project`, which frames a question and never asks whether it should be asked |
| medsci `check-reporting` | 49 reporting guidelines, verified-permissive rows only |
| medsci `manage-refs` | Rendering, marker conversion and Zotero CWYW field codes — the writing half of reference handling we have none of |
| hermes `llm-wiki` rules | Page-splitting and archival thresholds, backlink checks, index-scaling and log rotation — `synthesis-conventions` has the 2+-source threshold and none of the scale rules |
| claude-obsidian `wiki-retrieve`, `wiki-query` | A retrieval surface, if obra/knowledge-graph is not taken as the dependency instead (§3.7) |

**Not mirrored:** PHY041 `claude-skill-citation-checker` and htlin222 `research-guardian`. Both are
MIT and both decide verdicts — the §3.8 line.

#### The urgency test

Mirroring everything available would take the skill surface from nine to roughly twenty-eight. The
constraint is not maintenance cost — §3.2 establishes that a mirrored skill is *cheaper* to hold
than an authored one, because prose has no tests to hold it still. The constraint is **coherence**:
each mirror arrives speaking its own vocabulary, and reconciling it is a one-time cost paid per
skill, so adopting twenty at once buys twenty reconciliations before anything works together.

That makes this a sequencing question rather than a whether question. The test: **adopt first where
the gap blocks the arc; adopt later where it only widens it.** Nothing on either list below is
rejected on maintenance grounds.

The stated arc is question → literature → synthesis → draft → submit. Three gaps block it.

**Urgent — the arc does not close without these.**

| Mirror | Licence | Why it blocks |
|---|---|---|
| medsci `fulltext-retrieval` | MIT **[F]** | "Batch download open-access PDFs by DOI using legitimate OA APIs (Unpaywall, PMC, OpenAlex, Crossref). Optional PDF→Markdown conversion." We find sources and project metadata and **never fetch the text**. The Iron Law asks a quote to be verifiable against a source; the deferred direct-PDF-text leg in spec §10 needs text to exist locally first. This is that leg's missing input |
| K-Dense `scientific-writing` | MIT **[F]** | We have **no drafting skill**. `project` frames, `evidence-conventions` governs, `publish` gates, and nothing helps write. This one carries evidence provenance, reporting-guideline coverage and authorship accountability, and its audit scripts are stdlib with `claim_text_sha256` — the discipline already matches ours |
| pedrohcgs `checkpoint`, `compress-session`, `context-status`, `promote-memory` | MIT **[F]** | Four small skills, one cluster: a structured state snapshot before stopping, conversation distilled into decisions and open questions with file pointers. Spec §9's validation slice requires "minimum two sessions (forces one real cold resume)" — the criterion assumes continuity machinery we do not have |

**Deferred — real gaps, but breadth.**

| Mirror | Fills (§11 group) |
|---|---|
| gbrain `maintain` + `cron-scheduler` | 11.4 maintenance lane; our spec calls this "doctor mode + refresh mode", which is two verbs and no lane |
| claude-obsidian `wiki-fold` | 11.2 log and index scale — bounded extractive rollup, dry-run default. We have no rotation at any size |
| medsci `version-dataset`, `generate-codebook` | 11.1 dataset identity — a dataset a claim depends on currently has none |
| medsci `ma-scout`, `meta-analysis`, htlin222 `prisma-automation` | 11.5 systematic-review apparatus beyond screening states and a PRISMA-S log |
| medsci `find-journal` | 11.5 venue selection — two-pass matching against a curated profile library |
| pedrohcgs `replication-package`, `audit-reproducibility`, `submission-disclosures` | 11.5 the submission-integrity surface |
| claude-obsidian `wiki-mode` | 11.4 filing methodology — only if vault-shape choice is wanted; ours is deliberately fixed |

**Refused, and this list matters more than the two above.**

- **Anything that decides a verdict** (§3.8): pedrohcgs `validate-bib` and `verify-claims`, PHY041's
  checker, htlin222 `research-guardian`, gbrain `fact-check` and `citation-fixer`. All MIT, all
  tempting.
- **Anything duplicating what we have**: medsci `search-lit` (we vendor `paper-lookup`), gbrain
  `brain-ingest-gate` (our admission boundary is stricter), K-Dense `citation-management` — whose
  outage handling is §1.B's counterexample.
- **Anything domain-locked**: medsci's 21 medical-specific skills, unless the vault is medical.

**Skill-set governance**, from mattpocock/skills and obra/superpowers rather than from any research
tool: a `skills` array in `plugin.json` (ours has none), bucket promotion for skills being trialled
or retired, a Codex-side invocation policy to match our `disable-model-invocation`, a docs page per
promoted skill, and per-agent conformance tests. superpowers runs those across eight agents; we run
none, while authoring in a portable format precisely so other agents can use them.

### 3.5 Core — preserve

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
low enough that a person leaves the gate armed (§2.6). Unmeasured, they are a bet.

### 3.6 Core — port from Memoria

In-house, so this is porting rather than importing. Ranked by value.

1. **`decision_rules.py`.** Pre-registered rules — `metric / window / threshold / recommendation` —
   with assessment pure and application human-gated. Answers our unevidenced `0.90` fuzzy threshold
   and `--cap 30` directly, and its `evidence-review-sizing` rule instruments gate abandonment,
   which §2.6 names as the deciding risk. The highest-value item in this document.
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

### 3.7 Core — replace with third-party now

| Replace | With | Why now |
|---|---|---|
| The contiguous find in `selectors.find_context` | medsci `_quote_match.py` | Measured: our find misses line-number and column-bleed cases it grades PARTIAL and INTERLEAVED. Wire at `__main__.py:257-263`, not at `check_quote` — both sides of that comparison are vault text |
| Nothing — we have no retrieval | obra/knowledge-graph | Our largest single gap, MIT, SQLite + FTS5 + MCP. Do not build one |
| Duplicate detection we lack | medsci `check_reference_duplication.py`, `check_citation_keys.py` | stdlib, small, complement rather than replace our `citekey` check |
| Building an evaluation harness | HALLMARK as a fixture | Its six sub-tests already map onto four of our checks; registering a baseline is a supported operation |
| Any future renderer | pandoc + CSL | Both medsci and pedrohcgs shell out rather than reimplement |
| Building reporting-guideline support | medsci `check-reporting` | 49 checklists, verified-permissive rows only, plus its `LICENSES.md` discipline |

### 3.8 What is deliberately not replaced

`verify.py` and `checks.py` stay ours. bibverify, `harcx`, `bibtex-updater` and CiteVerifier are
all MIT and all tempting, and every one of them decides a verdict — which is exactly where §2.1
says adoption stops. K-Dense's `validate_citations.py` returning `True` on a network failure is the
concrete cost of getting that boundary wrong.

### 3.9 Net effect

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

Both halves are the same conclusion the product comparison reaches in §1.2 — build the trust core,
adopt the breadth — now with named files and named skills on both sides of the line.
