# Review: gabadi's three code-quality tools (pypi.org/user/gabadi)

Date: 2026-08-20. All three installed into `core/.venv` and run live against `harness_core` at HEAD (452 passed, 5 skipped; branch-coverage LCOV from `pytest --cov --cov-branch --cov-report=lcov:lcov.info`). Common profile: single maintainer (gabadi), MIT, v0.1.x (releases Jun–Aug 2026), Sigstore/trusted-publishing attestations, ports/extensions of unclebob (Robert C. Martin) tool lineages.

## crap4py 0.1.1 — CRAP score per function

Formula `CC² × (1 − coverage)³ + CC`; conventional risk threshold 30. Inputs: source + branch-level LCOV. Python ≥3.10, stdlib AST. `--max-crap` gives a CI gate; auto-excludes tests and `.gitignore` paths.

**Live result (231 functions):** two over threshold — `_target_hash` (`__main__.py`, CC 31, 77.3% cov, CRAP 42.3) and `inbox.load` (CC 27, 72.7%, 41.8). Next band: `check_metadata` 27.1, `_arxiv_version_outcome` 25.9, `_scope_acknowledged` 23.0 (CC 23 at 100% coverage — complexity-driven). Matches intuition about the codebase's gnarliest spots; the CC-at-full-coverage cases are refactor candidates, the low-coverage cases are test-gap candidates.

**Verdict: adopt first.** Cheapest of the three, ran correctly first try, output immediately actionable as a triage list. Advisory lane, not publish-gate.

## drywall 0.1.3 — polyglot AST-subtree DRY analyzer

Rust binary shipped via pip (also cargo/npm); Jaccard similarity over normalized AST fingerprints, default threshold 0.82; exit 0/1/2 for CI. Rust/JS/TS/Python.

**Live result:** zero duplicate pairs in `harness_core` at default threshold; instant runtime.

**Verdict: adopt as cheap silent gate.** No current findings (codebase small and DRY), so value is preventive — exit-code gate in CI costs nothing and catches copy-paste drift later.

## mutate4py 0.1.4 — mutation testing with embedded manifest

Discovers mutation sites, applies each, runs pytest, reports killed/survived/uncovered. Python ≥3.11 (we run 3.12), zero runtime deps, pytest-only. Differential reruns via a structural manifest hashed with `ast.unparse()` (formatting-immune).

**Sharp edges found live:**

- **Default = full suite per mutant.** `selectors.py` alone has 71 sites; 71 × ~37 s suite ≈ 45 min per small file — two runs timed out at 550 s. Narrowed with `--pytest-args 'tests/test_selectors.py'`: the whole file ran in **12 s**. `--test-contexts` (coverage context DB) automates narrowing; non-negotiable at our suite size.
- **Manifest is written INTO the production source file** (JSON footer appended to `selectors.py` and `claims.py`; reverted). For this repo that's a foreign machine-written region in `harness_core` — use `--manifest-file` (sidecar `<file>.manifest.json>`) always. Also creates a `.mutate4py/` work dir (gitignore it).

**Live result (selectors.py, forced full run): 35 killed, 19 survived, 17 uncovered of 71.** Survivors cluster exactly where it hurts: `_norm_with_map` line 79 (hyphen-join boundary — `index + 1 < len` vs `<=`, `char == "-"` vs `!=` all survive), `find_context` lines 119/123 (context-window clamps `position < 0` vs `<= 0`, `end < len(text)` vs `<=`), `_order_canonical_run` line 63 (combining-mark ordering). These are untested boundaries in the **fuzzy-quote matcher — the trust-critical path**. Real test gaps found in one 12-second run; this is the strongest result of the three.

**Verdict: adopt targeted, not blanket.** Run in sidecar-manifest mode with test narrowing on the trust-critical modules (`selectors.py`, `quotes.py`, `checks.py`, `frontmatter.py`, `claims.py`); blanket runs are cost-prohibitive without contexts.

## Placement in this harness

All three belong in the **dev-quality lane** (advisory CI / pre-merge), never in the vault's publish-gate closing sets — they measure the harness's code, not the vault's claims. Adoption order: crap4py → mutate4py (targeted) → drywall. Risk to price in: v0.1.x single-maintainer tools; pin versions, treat as removable.

## Baseline-then-differential plan (author-ruled 2026-08-20)

Blanket baseline once, then per-diff differential — the manifest's designed workflow. Trigger: **post-Plan-T, parallelizable with Plan D** (author-refined 2026-08-20). The hard constraint is the terminology wave — renames change `ast.unparse()` hashes and invalidate a pre-wave baseline wholesale. Only wholesale-rename waves force re-baseline; incremental edits are what differential mode absorbs, so running beside Plan D (mostly markdown — skills + glossary) costs at most a differential top-up on merged core-Python changes, and delivers the survivors backlog while D is in flight. Measured scan: ~1,250 sites across `harness_core` (`__main__.py` 216, `inbox.py` 124, `lints.py` 102, `events.py` 101, plus `checks.py`/`bibliography.py`); ~10–15 min blanket with test-contexts narrowing at 4 workers vs ~2.5 h without. Mechanics: `--build-test-contexts` once → blanket with `--test-contexts` and `--manifest-file` (sidecar; embedded mode is a repo-hygiene violation) → commit sidecars so differential persists across clones/CI → gitignore `.mutate4py/` → gate policy "no new survivors" on diffs; pre-existing survivors are backlog, never gate.

## Actionable backlog surfaced

1. Kill the 19 selectors.py survivors — boundary tests for hyphen-join, context-window clamps, combining-mark ordering.
2. `_target_hash` and `inbox.load`: raise branch coverage or split (CRAP > 30).
3. `_scope_acknowledged` (CC 23, 100% cov): complexity-only — refactor candidate, no test gap.

Raw outputs: mutation reports in `/tmp/mut*.out` at run time (not preserved); CRAP table regenerable with the commands above.
