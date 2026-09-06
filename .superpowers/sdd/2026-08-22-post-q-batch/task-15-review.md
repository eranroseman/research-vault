# Task 15 review - b899883..3d65856

Disposition: historical (2026-09-06)

## Spec Compliance

Verdict: **compliant**. No missed, extra, or misunderstood requirement.

Every brief step landed:

- Step 1/2 (failing test): `tests/test_checks.py:1461` adds
  `test_reduce_preserves_nonblocking_unmatched_over_matched` with the brief's exact
  assertion pair, including its trailing comments. The brief explicitly licensed
  adjusting the constructor call shape, and the two adjustments the implementer made
  are forced rather than cosmetic. `Outcome.__post_init__`
  (`research_vault/outcome.py:91`) routes every reason through
  `inbox.validate_reason`, whose `_REASON` regex (`research_vault/inbox.py:81-83`)
  demands a `REASON_CODES` prefix, so the brief's literal `"version mismatch"` would
  have raised `ValueError` before the reducer ran; `"mismatch — version differs"` is
  the shape `_version_mismatch` really emits (`research_vault/checks.py:653-660`).
  The brief's `extra={"class": "warn"}` was dropped because production non-blocking
  UNMATCHED outcomes never set a `class` key at all - only the blocking bucket reads
  it, and only for `== "blocking"`.
- Step 3 (implement): `research_vault/checks.py:1057-1063` is the brief's tuple
  verbatim, `(Result.UNREACHABLE, Result.UNMATCHED, Result.MATCHED, Result.SKIPPED)`,
  ruff-expanded across lines. It is the only production-code change in the diff, and
  it sits in the `else` branch, so the blocking bucket at `checks.py:1038-1050` is
  provably untouched.
- Step 4 (sweep + minting path): the per-test sweep result is stated affirmatively in
  the commit body ("no existing test pinned the old rounding"), with all four
  pre-existing `reduce_update_notice_outcomes` call sites named and dispositioned. The
  minting-path trace is present and correct, and it correctly corrects the task's own
  framing: `events.record_pass` has exactly two call sites repo-wide
  (`research_vault/verify.py:797`, `research_vault/publish.py:368`), both passing
  the literal `Result.MATCHED`, so the callee's guard is unreachable from this path and
  the ternary's condition is what actually stops the mint.
- Step 5 (commit): one commit, `3d65856`, subject exactly
  `fix: update-notice reduction preserves non-blocking UNMATCHED`.

One bookkeeping note so the controller's ledger does not flag a phantom discrepancy:
the implementer's report opens by saying `task-15-brief.md` did not exist and that the
task text was read from `docs/superpowers/plans/2026-08-22-post-q-batch.md:296-329`. The
brief artifact exists now and its content matches what the implementer worked from
step for step, so there is no compliance gap - only an artifact that was created after
the fact.

### Cannot verify from diff

Nearly all of the lenses' cannot-verify items were resolved during this synthesis by
direct execution. Recorded here as **closed**, so the controller does not chase them:

- **Suite green with the claimed accounting** - RESOLVED. Ran
  `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests -q -n auto -p no:cacheprovider`
  at HEAD: `1559 passed, 7 skipped`, matching the report exactly. The diff adds exactly
  two unparametrized test functions and touches no pre-existing assertion, so the +2
  from the 1557/7 baseline is fully accounted for.
- **Pristine output / no new warnings** - RESOLVED. The run emitted no warnings summary.
- **RED observed rather than reconstructed** - RESOLVED empirically. Extracted `b899883`
  into a scratch directory, dropped HEAD's `tests/test_checks.py` into it, and ran the
  new test against the pre-fix tuple. It failed with
  `AssertionError: assert <Result.MATCHED: 'MATCHED'> is <Result.UNMATCHED: 'UNMATCHED'>`
  - character for character the failure the report quotes, and an assertion failure
  rather than a constructor error.
- **Commit body carries the provenance argument** - RESOLVED. `git log -1 --format=%B`
  shows the UNREACHABLE-still-outranks-UNMATCHED rationale, the affirmative sweep
  result, the RED evidence with the test-literal justifications, and the full minting
  trace. `checks.py` gained no provenance comment; the two test docstrings state
  contracts, not history.
- **Form gate 8/8** - RESOLVED component-wise. `ruff format --check` and `ruff check`
  pass on all three changed files; `mypy research_vault` reports
  `Success: no issues found in 27 source files`; `config-validity` runs
  `tests/test_config_validity.py`, which passed inside the full suite;
  mdformat / yamlfix / pyproject-fmt match no file type in this diff; shellcheck and
  shfmt are `stages: [manual]`, which is precisely why the gate counts 8 and not the
  10 hook ids in `.pre-commit-config.yaml`.

The single genuine residual:

- **A literal `pre-commit run --all-files` invocation.** Its writer hooks mutate the
  tree, which this read-only review may not do. Every component of the gate is verified
  green above and the accounting matches the implementer's 8/8 claim, so this is a
  record-keeping item, not a risk. Controller check: run
  `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` once at gate close
  if a literal 8/8 transcript is required.

The working tree was clean before and after this review; `git status --porcelain` is
empty and HEAD is still `3d65856`.

## Strengths

- **The fix is one semantic token in the right place.** `checks.py:1057-1063` inserts
  `Result.UNMATCHED` into the non-blocking fallback tuple and nothing else - no helper,
  no flag, no restructuring of a function that did not need it. The blocking bucket is
  decided before the tuple is ever consulted, so the blast radius is confined to the
  one case the defect covered.
- **The RED is real and is the right RED.** Replayed empirically against `b899883`
  (see above): the pre-fix tuple `(UNREACHABLE, MATCHED, SKIPPED)` never listed
  UNMATCHED at all, so with `live=` non-blocking UNMATCHED and `rw=` MATCHED the
  generator's first hit is the RW leg. The reported failure is the predicted defect
  failure, not a constructor error.
- **The test-literal adaptations are justified against real code, and disclosed.** The
  reason string mirrors what `_version_mismatch` actually emits and the `extra` shape
  mirrors what the real live leg produces; the brief's draft would have died in reason
  validation and invented a field the codebase never sets. Both adjustments are argued
  in the commit body rather than made silently.
- **The reducer test pins the contract on both axes that matter** - the surviving
  `result`, and that RW's `warn_notices` still merge into the winner - using real
  `Outcome`s and the real reducer, no mocks. The second assertion is non-vacuous: the
  live leg's `warn_notices` list is empty, so a truthy merged list can only have come
  from RW.
- **Blast radius was checked downstream, not just locally.** An UNMATCHED reduced
  outcome still files its RW warns: the warn loop in `verify.py`'s `_file_effects` sits
  outside the `if outcome.result is not Result.MATCHED` block, so flipping the chosen
  result does not silently drop the correction notice.
- **The new `_apply_state_transitions` test discriminates.** Mutation-tested during this
  review: replacing the ternary's condition with `True` (so `record_pass` always fires
  with the literal MATCHED) fails both of its assertions. The implementer also states
  plainly that this test is green before and after the fix, so it is not passed off as
  red/green evidence for today's defect.
- **Commit-body doctrine is respected.** The sweep result, the minting trace, the
  controller-framing correction, and the test-literal adjustments all live in the body
  of `3d65856`; the production diff carries no comment.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

None.

### Minor (Nice to Have)

**1. `tests/test_verify_cli.py:534` - the routing test never pins the recorded result
value.** Status: **CONFIRMED** (upgraded from NOT-VERIFIED-MINOR by mutation testing
during this synthesis).

The assertion is
`assert any(row["check"] == "update-notice" for row in events.current_failures(source))`
- it checks that *a* failure row for the check exists, but not what result it records.
`events.record_failure` writes `{"check": ..., "result": result.value}`
(`research_vault/events.py:146`), so a drift at the `verify.py:797` ternary that
forwarded a wrong non-MATCHED result would still satisfy this test, even though the
test's name and docstring claim it pins UNMATCHED routing.

Why it matters: verified empirically. Rewriting the else branch to
`events.record_failure(text, check, Result.UNREACHABLE)` and running the new test
against that mutant gives `1 passed`. The test's name promises more than it delivers.
The same file's own precedent at `tests/test_verify_cli.py:1514` pins the full row, so
the weaker assertion is also inconsistent with local style.

Severity stays Minor for two reasons: this exact drift is already caught elsewhere -
`test_current_failure_projection_keeps_exact_recovery_behavior` asserts the exact rows
`[{"check": "doi", "result": "UNMATCHED"}, {"check": "metadata", "result": "UNREACHABLE"}]`
- and the gap is in test strength, not in shipped behaviour.

How to fix: assert the row content rather than the check id, e.g.
`assert events.current_failures(source) == [{"check": "update-notice", "result": "UNMATCHED"}]`,
matching the shape already used at `tests/test_verify_cli.py:1514`.

**2. `tests/test_verify_cli.py:516` - the commit body's coverage-novelty claim is
broader than the actual gap.** Status: **CONFIRMED** (upgraded from NOT-VERIFIED-MINOR
by mutation testing during this synthesis).

The report and commit body survey existing coverage only as far as
`tests/test_events.py:139` and conclude that the `verify.py:797` ternary was unpinned.
Every literal sentence is true when scoped to `test_events.py`, but a reader is left
believing the ternary had no caller-side coverage at all. It did:
`tests/test_verify_cli.py:1493`
(`test_current_failure_projection_keeps_exact_recovery_behavior`) drives verify
end-to-end with an UNMATCHED doi and an UNREACHABLE metadata outcome and asserts the
exact `current_failures` rows plus `trust_tier == "unverified"`.

Why it matters: verified empirically. Under the mutation that replaces the ternary
condition with `True`, both `:1493` and the new test fail. So `:1493` already guards
the drift the commit body presents as newly covered. The new test is still worth
keeping - the brief's Step 4 asked specifically about the update-notice mint, and
`:1493` only ever seeds update-notice as a pass, so no pre-existing test routes a
*failing* update-notice through this ternary - but the coverage argument as written
overstates the gap.

How to fix: no code change needed. If the commit body is ever amended, name
`tests/test_verify_cli.py:1493` as the pre-existing ternary coverage and scope the
novelty claim to the update-notice check id, which is the gap the brief actually named.

## Refuted During Verification

None. Both lens findings survived adversarial verification and were upgraded from
NOT-VERIFIED-MINOR to CONFIRMED by the mutation tests run during this synthesis. No
finding was dropped.

## Assessment

Task quality: **Approved**.

The brief's Step 3 landed verbatim, the RED was reproduced character for character
against the base commit, the consequence sweep and the minting-path trace are both
sound (and the trace correctly corrects the task's own framing), and the full offline
suite is green at 1559 passed / 7 skipped with pristine output. The two surviving
findings are Minor and both concern test strength and commit-body precision around the
supplementary routing test, not the shipped fix; neither blocks.
