# Task 10 review - acd38b5..a808f09

## Spec Compliance

**Verdict: compliant.**

Every step of the brief landed, and the values the brief fixed verbatim are verbatim in
the commit: the reason string `not-imported — cited citekey has no literature note`
(knowledge_harness/checks.py:164) with a true U+2014 em dash, the three test names as
written (tests/test_checks.py:81, :94, :108), the commit subject character-for-character,
and exactly one commit touching exactly the five files the brief named. The signature
constraint holds — `check_citekeys(vault_root, note_path, bibliography_universe=None)` is
unchanged at knowledge_harness/checks.py:131-133.

The implementation matches the ruling it cites. Spec §4
(docs/superpowers/specs/2026-08-16-foundation-spec.md:45) rules that "a claim's citekey is
citable only if its literature note exists (tier 2 — `literatures/` membership IS the
vault's citation universe)". knowledge_harness/checks.py:159 tests exactly that, on
citations only, leaving tier 1 (`citekey not in bibliography_universe`) as the first branch
so the pre-existing `mismatch — citekey not in bibliography` reason keeps priority.

The scope bound the brief calls out — the note's own citekey row keeps its current
semantics — is satisfied in behaviour. `cited` is built only from `claims.CITE_RE` over the
note body (knowledge_harness/checks.py:139), with no frontmatter or identity branch, and a
literature note's managed block carries its own citekey as a claim citation
(`- (quote) [@smith2020, p. 12]`, rendered by knowledge_harness/notes.py:310). The tier-2
probe for that row resolves to the very file `check_citekeys` just read, so it stays
MATCHED. What is missing is a committed test pinning it; see the Minor issue below.

The spec lens returned "issues"; that is corrected here to "compliant". Both of its
findings are Minor and neither is a missed, extra, or misunderstood requirement — its
verdict rested on cannot-verify pass-throughs, which are the controller's to resolve, not
compliance failures.

### Cannot verify from diff

Two of the four pass-throughs the lenses raised were resolved during synthesis and are
recorded here rather than sent on:

- **Suite green offline.** RESOLVED. `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest
  tests -q -p no:cacheprovider` at a808f09 with a clean tree: **1575 passed, 7 skipped** in
  72s, exit 0 — matching the report's claim and +3 from BASE. The working tree was clean
  before and after.
- **RED evidence (1 failed / 2 passed).** RESOLVED analytically; no scratch worktree was
  created, since that mutates `.git`. The pre-change branch is fully visible in the diff
  hunk: `result = Result.MATCHED if citekey in bibliography_universe else
  Result.UNMATCHED`. Under it, `test_cited_citekey_requires_literature_note`
  (bibliography-present, note-absent) yields MATCHED and fails its `Result.UNMATCHED`
  assertion, while `test_cited_citekey_with_note_passes` (MATCHED) and
  `test_cited_citekey_absent_everywhere` (UNMATCHED with the old mismatch reason) both
  pass. `tests/conftest.py` is untouched by the diff, so `tmp_vault` exists identically at
  acd38b5. Exactly one failure is deterministic.

Remaining for the controller:

- **Form gate 8/8.** Not run here on purpose: the implementer's report records that
  mdformat auto-fixed table rows on its first pass, so `pre-commit run --all-files` can
  write to the tree and this review is read-only. If confirmation is wanted, run
  `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` at a808f09 and check
  that the tree is clean afterwards.
- **Spec §6's check-table row.** Line 96 of the foundation spec still labels the check
  "Citekey exists in bibliography", which now under-describes the shipped two-tier check.
  It does not contradict §4's dated ruling (§4 is the newer and more specific statement),
  and the spec was outside the brief's file list, so the implementer was right not to touch
  it under AGENTS.md's "stand as written" rule. Rule whether §4 is taken to supersede the
  §6 row's wording or a follow-up task amends line 96.
- **Manifest-sidecar refresh policy.** Whether a feature commit is expected to regenerate
  `knowledge_harness/*.py.manifest.json`. Evidence gathered below narrows this to a policy
  call with near-zero mechanical stakes.

## Strengths

- **Branch ordering carries the third case for free.** `if citekey not in
  bibliography_universe` short-circuits to the pre-existing `mismatch` reason before the
  tier-2 branch is evaluated (knowledge_harness/checks.py:156-166), and
  tests/test_checks.py:117 pins that reason by equality, so the new tier can never absorb
  the old one.
- **The change is one branch, not a second pass.** Two coupled conditional expressions
  (where `reason` was re-derived from `result`) become a single three-way if/elif/else that
  sets result and reason together, reading in doctrine order: not admitted → not imported →
  citable.
- **`not-imported` is genuinely distinct from `not-admitted`,** not aliased or widened:
  separate `REASON_CODES` members (knowledge_harness/inbox.py:31-32), separate table rows
  (skills/evidence-conventions/SKILL.md:85-86), separate terminology enumeration entries,
  each stating its own distinguishing condition (never entered Zotero vs. entered the
  library but not yet run through `import-note`).
- **Tests drive the real function against real files** with no mocks, and each asserts both
  the `Result` and the exact reason string, so a reason-code typo or a silent reason change
  fails the suite.
- **The tier-2 probe stays total.** It reuses the codebase's flat literature-note path
  convention rather than routing through `notes.note_path`, which raises
  `InvalidCitekeyError` — a check function must not blow up on a hostile citekey in a
  draft.
- **The dialect surfaces were updated in the same commit,** and the mechanically enforced
  ones (tests/test_config_validity.py's backticked-enumeration parity,
  tests/test_skill_contracts.py's table/registry parity) name themselves rather than being
  guessed at.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

None.

### Minor (Nice to Have)

**1. The scope bound has no committed regression test — tests/test_checks.py:81**
*(status: CONFIRMED)*

What is wrong: the brief's highest-risk requirement — a literature note's own citekey row
keeps its pre-existing note-vs-bibliography semantics — ships unpinned. The implementer
wrote exactly that test, ran it, and deleted it rather than committing it
(`tests/test_self_review_scratch.py`, report lines 253-262).

Why it matters: the guarantee rests on an unstated structural invariant — a literature note
lives at exactly `literatures/<its own citekey>.md`, so a self-citation row's tier-2 probe
resolves to the file just read. Nothing in checks.py states that dependency, and nothing in
the suite pins it. Verified during this synthesis: no committed test asserts a MATCHED
`citekey` outcome for a note under `literatures/`; the fixture-vault end-to-end verify runs
(tests/test_verify_cli.py:1698, :1733, :1808) either assert an exit code that already
tolerates UNMATCHED findings or pick findings out with `next(...)` filters, and the two
tests that touch `verify.file_outcomes` (tests/test_verify_cli.py:1221, :1651) monkeypatch
it away. So a later change — nesting literature notes (verify.py:981 already `rglob`s
`literatures`, while lints.py:576 and verify.py:709 enumerate it with a flat
`glob("*.md")`), keying the lookup off frontmatter, or a rename cascade — would silently
flip a literature note's self-citation row from MATCHED to `not-imported`, the exact
semantic change the brief forbids, with a green suite.

How to fix: commit the throwaway. One test, zero new fixtures: call
`checks.check_citekeys(fixture_vault, fixture_vault / "literatures" / "smith2020.md")` and
assert the `smith2020` row is `Result.MATCHED` / `"matched"`, with a docstring naming the
invariant.

**2. Fourth inlined copy of the literature-note path — knowledge_harness/checks.py:159**
*(status: NOT-VERIFIED-MINOR — a design preference, not a defect; the call sites are
confirmed)*

What is wrong: `(vault / "literatures" / f"{citekey}.md")` now appears in four places —
`notes.note_path` (notes.py:129, guarded), `lints._note_status` (lints.py:491), `factcheck`
(factcheck.py:73 and :90), and here.

Why it matters: the vault-layout rule has no single owner, so a change to where literature
notes live has to find every copy. `notes.note_path` looks authoritative but is bypassed by
all three call sites that need a total function.

How to fix (opportunistic, not blocking): add a total `literature_path(vault_root, citekey)
-> Path` beside `note_path`, have `note_path` call it after its safety guard, and use it
here and at the existing sites.

**3. Sidecar manifests left stale — knowledge_harness/checks.py.manifest.json:5**
*(status: CONFIRMED as stale; impact verified near-nil)*

What is wrong: the tracked mutation sidecars for both changed modules were not regenerated.
Verified by hash: `checks.py.manifest.json` records `source_sha256` `05c0891c...` against an
actual `c5ae4757...`, and `inbox.py.manifest.json` records `74a03266...` against an actual
`208fe2ba...`. The recorded line ranges have also drifted (`func/check_citekeys` end_line
173, `func/_doi_path` line 176; actual `_doi_path` is now at line 180).

Why it matters — and why it is only Minor: these files are git-tracked, so a stale hash is
committed state. But the mechanical stakes are close to nil, and the spec lens's premise
that no in-repo tool produces them is wrong. They are written by mutate4py's
`--manifest-file` sidecar mode, driven by `scripts/mutation_gate.py` (see
docs/superpowers/plans/2026-08-20-plan-q-quality-lane.md:457, 748); the documented refresh
act is a blanket `--update-baseline` run over every module, not a per-task commit. Nothing
in the repo reads `source_sha256` (no reference outside the manifest files themselves), no
pre-commit hook and no step of `.github/workflows/quality.yml` checks manifest freshness,
mutate4py reconciles and rewrites the sidecar on its next run, and the gate's baseline keys
deliberately exclude line numbers so they stay stable across unrelated edits. Finally,
`__main__.py.manifest.json` was already stale at BASE — per-task refresh is demonstrably
not this project's practice.

How to fix: nothing in this commit. Either fold a sidecar refresh into the next
`--update-baseline` run, or have the controller rule explicitly that manifest refresh is a
baseline act rather than a task act, and record that where the mutation gate is documented.

## Refuted During Verification

None. No lens finding was refuted; all three findings above survived, and none was dropped.
The severity labels were left as filed (all Minor). Two cannot-verify items were resolved
during synthesis rather than passed on (suite green, RED evidence — see Spec Compliance
above), and the spec lens's claim that "nothing in-repo generates" the manifest sidecars was
corrected: `scripts/mutation_gate.py` does.

## Assessment

**Task quality: Approved.**

The change does exactly what the brief and spec §4's dated ruling call for, in one branch,
with the reason strings and test names verbatim and the suite green at 1575 passed / 7
skipped. The only substantive gap is a missing regression test for the scope bound the
brief itself flagged as highest-risk — a one-test, zero-fixture follow-up that the
implementer had already written and then discarded.
