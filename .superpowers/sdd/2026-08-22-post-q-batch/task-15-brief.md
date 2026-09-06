### Task 15: Reduction must not round UNMATCHED to MATCHED (audit defect 2)

Disposition: historical (2026-09-06)

**Files:**

- Modify: `research_vault/checks.py` (`reduce_update_notice_outcomes`, ~line 1024)

- Test: `tests/test_checks.py`

- [ ] **Step 1: Failing test**

```python
def test_reduce_preserves_nonblocking_unmatched_over_matched():
    live = Outcome("update-notice", "10.1/x", Result.UNMATCHED,
                   "version mismatch", extra={"class": "warn", "warn_notices": []})
    rw = Outcome("update-notice", "10.1/x", Result.MATCHED,
                 "matched", extra={"warn_notices": [{"type": "correction"}]})
    reduced = checks.reduce_update_notice_outcomes(live, rw)
    assert reduced.result is Result.UNMATCHED   # ran-and-disagreed survives
    assert reduced.extra.get("warn_notices")    # RW's warns still merged
```

(Adjust constructor call shape to the real `Outcome` signature in the file — the assertion pair is the contract.)

- [ ] **Step 2: Run it** — Expected: FAIL (today the fallback priority is UNREACHABLE > MATCHED > SKIPPED, so the non-blocking UNMATCHED loses to MATCHED).

- [ ] **Step 3: Implement** — in the non-blocking `chosen` fallback, insert `Result.UNMATCHED` ahead of `Result.MATCHED`:

```python
for result in (Result.UNREACHABLE, Result.UNMATCHED, Result.MATCHED, Result.SKIPPED)
```

- [ ] **Step 4: Sweep the consequences.** Run the full offline suite; any test that pinned the old rounding is a test asserting the defect — fix the test, and say so in the commit body per-test. Then check the event-minting path: an UNMATCHED reduction must not mint a `verified` update-notice event (read `verify.py`'s minting condition and add a regression test if none pins it).

- [ ] **Step 5: Commit** `fix: update-notice reduction preserves non-blocking UNMATCHED`

