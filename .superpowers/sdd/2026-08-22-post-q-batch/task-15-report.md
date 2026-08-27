# Task 15 report — reduction must not round UNMATCHED to MATCHED

BASE = b8998833cf6ab1d112bff6b7be3e86e881ab692a (`docs: tick Task 14`).

## Brief file did not exist

`task-15-brief.md` was not present in `.superpowers/sdd/2026-08-22-post-q-batch/`
(confirmed: only tasks 1, 2, 2b-2d, 3-10, 14, 21, 22 have brief files there).
Task 15's text lives instead in the plan file itself, still uncommitted-brief:
`docs/superpowers/plans/2026-08-22-post-q-batch.md:296-329` ("Task 15: Reduction
must not round UNMATCHED to MATCHED (audit defect 2)"). I read the task from
there; its content matches the task description given to me verbatim (failing
test, fallback-tuple delta, sweep-and-mint-trace instruction), so no information
was missing — only the standalone brief artifact was absent.

## Surfaces (re-verified)

- `knowledge_harness/checks.py:1018` — `reduce_update_notice_outcomes`.
- `knowledge_harness/checks.py:1057` (pre-fix) — the fallback tuple:
  `for result in (Result.UNREACHABLE, Result.MATCHED, Result.SKIPPED)`.
  Notably this tuple never listed `Result.UNMATCHED` at all — a non-blocking
  UNMATCHED reached the tuple only via the trailing `outcomes[0]` default, and
  lost outright whenever a MATCHED outcome was present since MATCHED sits in
  the tuple.

## RED

Added `tests/test_checks.py::test_reduce_preserves_nonblocking_unmatched_over_matched`
(adjacent to the existing `reduce_update_notice_outcomes` tests). Constructor
call was adjusted from the brief's literal draft, per the task's explicit
permission to do so:

- `Outcome`'s real signature (`knowledge_harness/outcome.py:46`) is positional
  `(check, target, result, reason, extra=...)`, which the brief's call already
  matched shape-for-shape.
- The brief's `reason="version mismatch"` does NOT validate: `Outcome.__post_init__`
  routes every `reason` through `inbox.validate_reason`, which requires the
  string to *start* with one of `inbox.REASON_CODES` (`inbox.py:81-83`,
  `_REASON` regex). "version mismatch" starts with "version", not a code, and
  would raise `ValueError` at construction — before the reduction logic ever
  ran. I used `"mismatch — version differs"` instead, matching the exact
  string shape the real non-blocking-mismatch producer already emits
  (`checks.py:655-661`, `_version_mismatch`).
- Dropped the brief's `extra={"class": "warn", ...}` for the live outcome.
  Production non-blocking UNMATCHED outcomes (`_version_mismatch`) carry no
  `class` key in `extra` at all — the "class" key exists solely to mark the
  *blocking* bucket (`extra.get("class") == "blocking"`, checked before the
  fallback tuple). Adding `"class": "warn"` would not have changed behavior
  (only `== "blocking"` is tested) but would have implied a field the real
  code never sets, so I matched the extra shape a real live-leg version
  mismatch actually produces (just `{"warn_notices": [...]}`).

Run:

```
.venv/bin/python -m pytest tests/test_checks.py::test_reduce_preserves_nonblocking_unmatched_over_matched -v
```

Result: **FAILED**, for the predicted reason —

```
AssertionError: assert <Result.MATCHED: 'MATCHED'> is <Result.UNMATCHED: 'UNMATCHED'>
```

`chosen` was the RW `MATCHED` outcome, not a constructor error. Confirms the
defect: the ran-and-disagreed non-blocking UNMATCHED lost to MATCHED.

## Fix

One-line delta, exactly the brief's Step 3, at `checks.py:1057` (ruff-expanded
across lines):

```python
for result in (
    Result.UNREACHABLE,
    Result.UNMATCHED,
    Result.MATCHED,
    Result.SKIPPED,
)
```

## GREEN

Same test now passes. `tests/test_checks.py` full module: 124 passed.

## Consequence sweep

Full offline suite before → after: **1557 passed / 7 skipped → 1559 passed / 7
skipped** (the two new tests; baseline recorded in the brief as 1557/7).

**No existing test pinned the old rounding — swept and confirmed empirically
(none needed fixing).** I traced every existing call of
`reduce_update_notice_outcomes` in the suite (`tests/test_checks.py:1410,
1479, 1506, 1572`) before running anything:

- `test_reduce_update_notice_outcomes_applies_precedence_and_merges_warns` —
  its `matched` case pairs `live=SKIPPED` with `rw=MATCHED` (no UNMATCHED
  involved); its `unmatched` case pairs `outage=UNREACHABLE` with
  `blocking=UNMATCHED(class="blocking")`, which is decided by the `blocking`
  bucket, evaluated *before* the fallback tuple — untouched by this change.
- `test_reduce_update_notice_outcomes_fails_closed_on_target_mismatch` —
  target-mismatch short-circuit, never reaches the fallback tuple.
- `test_reduce_update_notice_outcomes_keeps_the_winner_identity` — RW leg is
  UNMATCHED-blocking; decided by the blocking bucket, not the tuple.
- `test_notice_reducer_rebuilds_through_typed_records_without_mutating_sources`
  — pairs MATCHED with UNREACHABLE; UNREACHABLE still ranks first both before
  and after (position 1 in both tuples), so the winner is unchanged.

None of the four exercises the one scenario the old tuple mishandled: a
non-blocking UNMATCHED competing against a MATCHED. The full-suite run
(1559/7, zero failures, zero modified pre-existing assertions) confirms this
empirically — the sweep found nothing to fix. Stating this affirmatively per
the task's instruction: **the sweep found no test asserting the defect.**

## Minting-path trace and conclusion

The task description's framing needed a correction, caught before writing
unneeded tests. The framing was: "`events.py:97`'s guard refuses any
non-MATCHED result, so a reduced UNMATCHED cannot reach a mint regardless of
how the reduction chose it." That is true only as a fallback — the guard is
not actually what stops it in the current call graph, and tracing the real
call path found a stronger, prior reason.

**Trace.** `record_pass` (`events.py:88`) is called from exactly two places in
the whole codebase:

- `verify.py:797`, inside `_apply_state_transitions` (the function a reduced
  update-notice outcome flows into via `verify_state`'s `raw`/`authoritative`
  list):

  ```python
  updated = (
      events.record_pass(text, check, Result.MATCHED, at=detection_date)
      if outcome.result is Result.MATCHED
      else events.record_failure(text, check, outcome.result)
  )
  ```

- `publish.py:368`, unconditionally, for the publish-status event (unrelated
  to update-notice).

At both sites the second positional argument passed to `record_pass` is the
**literal** `Result.MATCHED`, never `outcome.result` — and at `verify.py:797`
the call is additionally gated on `outcome.result is Result.MATCHED` in the
surrounding ternary; any other result takes the `record_failure` branch
instead. So a reduced UNMATCHED (or any non-MATCHED outcome) cannot reach
`record_pass` at all through this call site — not because the callee refuses
it, but because the caller never offers it. `events.py:97`'s own guard
(`if result is not Result.MATCHED: raise ValueError(...)`) is real
defense-in-depth, already pinned at `test_events.py:139`
(`test_record_pass_rejects_non_matched`), but it protects a path this specific
call site cannot exercise, since it never passes anything but the hardcoded
literal.

**Conclusion on coverage.** `test_events.py:139` pins `record_pass`'s own
internal guard — necessary, but it does not and cannot exercise the
`verify.py:797` ternary, because that ternary never forwards `outcome.result`
into `record_pass` in the first place. If the ternary's condition or branches
ever drifted (e.g. a future edit accidentally called `record_pass` on the
`else` branch, or dropped the `is Result.MATCHED` guard), `test_events.py:139`
would not catch it — it only ever calls `record_pass` directly with results
it chooses itself, never through `verify.py`'s routing. So this is coverage
`test_events.py:139` does not provide, and I added it:
`tests/test_verify_cli.py::test_apply_state_transitions_routes_unmatched_update_notice_to_failure_not_a_mint`,
which calls `verify._apply_state_transitions` directly with a non-blocking
UNMATCHED update-notice outcome and asserts the note ends up with a
`failed-verification` row and no `verified` event. This test passes both
before and after the one-line reduction fix (it pins the call-site routing,
which the reduction defect never touched) — it is coverage-adding, not a
red/green test for today's defect. Ran individually first (PASSED, confirming
the routing already holds), then as part of the full suite above.

## Files changed

- `knowledge_harness/checks.py` — the one-line fallback-tuple fix (`checks.py:1057`).
- `tests/test_checks.py` — added `test_reduce_preserves_nonblocking_unmatched_over_matched`.
- `tests/test_verify_cli.py` — added `_apply_state_transitions` to the
  imports from `knowledge_harness.verify`, and added
  `test_apply_state_transitions_routes_unmatched_update_notice_to_failure_not_a_mint`.

## Self-review

- **Blocking path unaffected?** Yes. The `blocking` bucket
  (`outcome.result is Result.UNMATCHED and outcome.extra.get("class") ==
  "blocking"`) is evaluated and returned *before* the fallback tuple is ever
  consulted; the one-line change only touches the `else` branch. Confirmed by
  the three blocking-scenario tests above still passing unmodified.
- **Does UNREACHABLE still outrank UNMATCHED, and should it?** Yes to both.
  `Result.UNREACHABLE` is still first in the tuple. It should be: an outage is
  a transient failure to observe, not a content disagreement, so coercing a
  live outage into a durable UNMATCHED marker would be as wrong as the defect
  this task fixes, just in the other direction. The target-mismatch
  short-circuit earlier in the same function already coerces to
  `Result.UNREACHABLE` for the identical fail-closed-on-outage reason, so this
  preserves existing doctrine rather than relitigating it. In practice the
  ordering between these two is close to moot either way: `check_rw_batch`
  never returns `UNREACHABLE` or a non-blocking `UNMATCHED` (`checks.py:977-1011`
  only returns `None`, a blocking `UNMATCHED`, or `MATCHED`), so both
  `UNREACHABLE` and non-blocking `UNMATCHED` can only originate from the live
  leg — they cannot co-occur in the fallback tuple in production. The tuple's
  ordering between them is preserved doctrine, not a live decision this task
  touches.
- **Does RW's `warn_notices` still merge into the reduced outcome?** Yes —
  `warnings = _merge_warn_notices(...)` runs unconditionally over all input
  outcomes' `warn_notices` regardless of which outcome is `chosen`, and is
  applied to the final record after selection. Pinned by the new test's
  second assertion (`reduced.extra.get("warn_notices")` truthy, sourced from
  RW's `extra` since the live leg's list was empty).

## Concerns

None outstanding. Suite green at 1559 passed / 7 skipped; form gate 8/8; one
commit.
