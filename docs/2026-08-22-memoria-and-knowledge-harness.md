# Memoria and knowledge-harness: two answers to one thesis

Analysis note, 2026-08-22.

## Why this exists

`docs/2026-08-22-product-comparison-verified.md` compares this harness against 35 external
products and asks, in §17, whether it has a place or whether we should adopt an existing
alternative. It never mentions **Memoria** — `eranroseman/memoria-vault`, the same author's other
implementation of the same thesis, sitting at `~/memoria-vault`.

That omission matters more than any row in the comparison. Memoria is not a competitor in the
market sense; it is the alternative the positioning question was actually about.

## Method and read depth

Memoria was read on 2026-08-22 at `~/memoria-vault`, at commit `5395a87d`. **Read:** `README.md`,
`docs/overview.md`, the guarantees table in `docs/README.md`, `docs/superpowers/specs/
2026-07-12-beta.1-consolidation.md`, and these implementation files —
`runtime/evidence.py`, `runtime/span_refs.py`, `runtime/decision_rules.py`,
`runtime/sweeps/retraction/retraction.py`, `runtime/sweeps/linter/detectors.py` (declaration list),
and the `verify_project_draft` path in `runtime/knowledge.py`. **Not read:** the other ~90 modules,
the test suite, the TypeScript adapter, the docs site.

Line counts, module names and finding vocabularies below are exact. Behavioural claims are drawn
from docstrings and the specific functions named, and are marked where they are inferences.

**Three of this note's earlier drafts asserted absences that turned out to be wrong** — no quote
verification, a general number-faithfulness lint, grounded synthesis unimplemented. Each was a
negative from a probe that had not been validated against a known positive, which is the same
failure the comparison document records twice in §1 and §19.3. The corrected versions are below,
and they are narrower than either the wrong claim or its opposite.

## What each is, measured

| | knowledge-harness | Memoria |
|---|---|---|
| First commit | 2026-08-16 | 2026-05-27 |
| Commits | 371 | 1,441 |
| Core | 26 modules, 9,716 lines | 99 modules, 46,331 lines |
| Tests | 1,330 collected | 180 files, 90,100 lines |
| Status | v0.1.0, unpublished | v0.1-alpha, public repo, published docs site, installers |
| Distribution | Claude Code plugin | CLI + installer (bash / PowerShell), Obsidian adapter in TypeScript |
| Platforms | WSL / Linux | Windows 10/11, Ubuntu/Debian, WSL2; macOS explicitly unsupported |
| Dependencies | standard library only, `pypdf` behind an extra | Python 3.12+, `yaml`, provider keys per flow, Node 22 for the adapter |
| State | the vault is the state; git only | Markdown plus SQLite plus an append-only journal under `.memoria/` |

Memoria is roughly five times the code, three months older, and shipped in a way this project is
not.

## The shared thesis

Memoria's README: *"a local research engine for one researcher: it turns what you read into checked
notes, linked arguments, and drafts whose every citation must resolve against a real source before
export"*, under the banner *"The AI does the bookkeeping. You keep the judgment."* Its control rule:
*"Operations propose; the PI disposes."*

Ours: *"every claim traceable to a real source, zero fabricated citations"*, and the foundation
spec's *"admission is a human act."*

The agreement runs past the pitch and into doctrine:

| Doctrine | knowledge-harness | Memoria |
|---|---|---|
| The machine writes, the human decides | CLI verbs write; skills compose and explain | "Operations propose; the PI disposes" |
| One write path | every durable write is a CLI verb | "every machine write lands through a single journaled write path" |
| Append-only record | `log/`, `inbox/review-queue.md`, drift-linted | append-only journal under `.memoria/` |
| Never claim unbuilt behaviour | four-state results; a skill may not say a check ran | "the docs never claim un-built behavior — anything not shipped is marked *planned*" |
| Plain files that outlive the tool | ADR 0001, OKF-conformant markdown | "plain Markdown you can read with `cat`… the whole vault travels as a folder copy" |
| Surfacing what waits on you | review-inbox drain with count and oldest age | attention cards |

## Convergences reached independently

Three are close enough to be worth naming, because they were arrived at separately.

**OKF conformance, with the same rule.** Memoria's beta.1 spec, item K1: `okf-conformance` —
*"every non-reserved `.md` has parseable frontmatter + non-empty `type`"*. That is verbatim the rule
our ADR 0001 states.

**The bibliography as a regenerated projection.** Memoria classes `bibliography.bib` as a *data
projection* — "regenerated always, never PI-edited" — against *view preferences* which are seeded
once and then owned by the human. Our spec §4 rules the BibLaTeX file into exactly that class, and
calls it "the `log.md` artifact class".

**A generated vault `AGENTS.md`.** Memoria: "a thin, engine-generated `AGENTS.md` at the vault root
(read-contract projection… never PI-edited)". Ours ships one from `setup-vault`.

## The evidence model, compared

This is where the two designs genuinely differ, and neither is simply ahead.

**Memoria** binds evidence to drafts through `%%ev: …%%` markers carrying an evidence-set id
(`ev-` plus eight hex). An evidence item is one of two kinds:

- a **source span**, `work_id#^pNNNN` — a work plus a page anchor, resolved against a `passages`
  table whose `passage_id` is a content hash;
- **code grounds**, `code-grounds:<run_id>:<artifact_id>:sha256:<64>` — a claim grounded in the
  hashed output of a code run.

`resolve_span_ref` refuses unless the source's `check_status` is `"checked"`, and
`read_barrier.py` is a "checked-file consumption guard" over hashes. Admission is enforced at
resolution, by machine.

**Ours** binds a claim to a source through a claim line — evidence-boundary tag, `[@citekey,
locator]`, `^c-XXXXXXXX` anchor — with `citekey#^claim-id` as the global address, `supports` and
`disputes` stance links between claim addresses, and quote text compared against the literature
note's managed region under NFKC-plus-whitespace normalisation with prefix/suffix selectors.

The differences that follow:

- **Direction.** Theirs points at a page in the source. Ours points at a claim we extracted from
  the source. Theirs is more direct and coarser; ours is finer and mediated by our own extraction.
- **Drift versus correspondence.** `evidence-text-drift` compares `current_block_hash` against
  `stored_block_hash` — it detects that bound text *changed since binding*. Our quote check asks a
  different question: whether the quote *corresponds to the source at all*. Both are real
  guarantees; neither subsumes the other.
- **Code grounds have no counterpart anywhere.** Not in Memoria's competitors and not in the 35
  products surveyed in the comparison. For a harness that will eventually carry analysis as well as
  literature, grounding a claim in a hashed run output is the obvious missing half of citation.

## Where Memoria is ahead

Six of these are gaps the comparison document lists as ours against the external field. Memoria
ships them.

| Gap in the comparison | Memoria |
|---|---|
| §11.1 per-finding severity | `SEVERITY_RANK` in the linter; verification findings carry `severity: high\|medium` |
| §11.1 contradiction machinery beyond flagging | `propagation.py`, 651 lines — typed-consequence propagation over the grounding closure and derivation DAG; a claim can lose its grounds through a `supports` edge or a cited source's standing |
| §11.1 machine-side admission screening | the `check_status == "checked"` gate plus `read_barrier.py` |
| §11.2 untrusted-source hardening | `content_security.py`, 514 lines, "content-layer defenses for untrusted Markdown" |
| §11.2 structural lints | `broken_wikilinks`, `orphan_working_files`, `stale_fleeting`, `frontmatter_schema_check`, `frontmatter_link_check` |
| §11.6 evaluation surface | `runtime/eval/eval_score.py` — "deterministic vault-eval scorer: diagnostic, never gating… zero-LLM, report-only" |

Its **retraction sweep is better than ours**: three sources, most-authoritative first — the
Retraction Watch CSV loaded locally and indexed by `OriginalPaperDOI` ("complete, offline,
deterministic"), the Crossref API using both `message.update-to[]` *and*
`message.relation.is-retracted-by`, and **Open Retractions** as an independent cross-check. We use
the RW CSV, Crossref `updated-by`, and OpenAlex `is_retracted`; we use neither
`relation.is-retracted-by` nor an independent third source.

Its **check vocabulary is wider**: twenty finding kinds including `no-support`, `no-refutation`,
`refutation`, `conflict`, `fragility`, `thin-argument`. **`no-refutation` flags a claim for which
no counter-evidence was considered.** Our `disputed-claim` check fires only when disputes already
exist; flagging their absence is analysis-of-competing-hypotheses discipline we do not implement.

### The single best idea in either project

`decision_rules.py`: *"pre-registration as data, not memory. Every beta.1 blocker is written down
**before** its evidence arrives — what gets measured, over what window, which number decides it,
and what the decision then is. A rule the PI can read today cannot be quietly re-derived once the
numbers are in."*

Seventeen rules, each carrying `id / blocker / metric / window / threshold / recommendation /
check / status`. Four are `auto`, backed by named constants; thirteen are `manual` reminders that
no predicate can fire. Assessment is pure and separate from application — `assess_decision_rules`
reports what *would* fire; only a PI-protected operation mints a notice. *"A rule recommends; it
never acts."*

Two of the seventeen instrument exactly the risk the comparison's §8.5 identifies as decisive for
us:

- `evidence-review-sizing` — fires at "at least 10 recorded evidence-review events with a decision
  on fewer than half of them", recommending *"batch and filter until review fits a session; **if
  skipped, simplify the gate**"*.
- `attention-loudness` — *"any routine push means the policy is wrong."*

Our `fuzzy-quote` threshold of 0.90 and our `--cap 30` are bare constants. No metric, no window, no
recorded decision, and nothing that would tell us the gate had stopped being used.

## Where knowledge-harness is ahead

Three things, and the list is short.

- **Zotero and Better BibTeX as the citekey spine.** Memoria's plan for Zotero is
  `zotero-bulk-import` — *"generic BibTeX/CSL; admit to catalog, none to knowledge"* — an import
  adapter. Our citekey joins filenames, prose citations, the bibliography export and every check.
  This is the one architectural axis where the two projects genuinely diverge.
- ~~Quote correspondence against source text.~~ **Withdrawn 2026-08-22.** Memoria's capability
  layer ships `integrity-claim-quote-check` ("check whether a claim's quoted evidence appears in
  its source") and `integrity-quote-anchor-check` ("check anchored note quotes against their source
  content"). The earlier reading rested on `evidence-text-drift`, which hash-pins bound text, and
  missed the operations layer entirely. What may remain ours is the stored W3C prefix/suffix
  selectors and the `fuzzy-quote` reason code — unverified against their implementation, so not
  claimed. **This is the fourth absence asserted about Memoria in this note's drafts that reading
  falsified**, and the pattern is the one §1 of the product comparison names: a negative from a
  probe aimed at the wrong layer.
- **Claim-to-claim stance links.** `supports` appears in Memoria's propagation walk as an edge
  type, so the concept exists; `citekey#^claim-id` addressing between claims does not appear in
  what was read.

Everything else on our side is matched or exceeded.

## What this means

Stated as options rather than a recommendation, because the choice is not a technical one.

1. **Two projects, one thesis, one author.** The comparison document's §17 concludes "build the
   trust core, adopt the breadth". Memoria *is* breadth — five times the code, public, installed,
   documented — built by the same person for the same reader. The adopt-versus-build rule the
   comparison lands on (§18.1: adopt by default; build only where the artifact decides a verdict)
   applied to this pair produces an uncomfortable answer, because Memoria decides verdicts too.

2. **The distinctness that survives is narrow and real.** A Zotero-anchored citekey spine and
   quote-correspondence checking are not small things for the academic-research arc specifically.
   They are also two features, not a product.

3. **The strongest case for continuing is the Claude Code surface.** Memoria is a CLI with an
   Obsidian adapter; knowledge-harness is a plugin whose gates are hooks — PostToolUse, Stop,
   pre-commit — armed by the harness rather than run by the operator. That is a genuinely different
   integration, and it is the thing §12 of the comparison identifies as unmatched anywhere.

4. **The cheapest next step is neither.** Both projects have unmeasured false-positive rates, and
   the comparison's §8.5 establishes that this is the number deciding whether either is deployable.
   Memoria at least has pre-registered rules that would notice; we have constants.

## Limits

Ninety of Memoria's ninety-nine modules were not read, nor any of its 90,100 test lines. Its
capability claims here come from docstrings, the specific functions named, and its own
documentation — the same standard the comparison document applies to external products, and the
same limit. No behaviour of either project was measured. The "where each is ahead" lists are
therefore claims about what each *implements*, not about what either *achieves*.
