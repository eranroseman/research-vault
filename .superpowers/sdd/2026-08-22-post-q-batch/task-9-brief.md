### Task 9: SKIPPED entries excluded from unacknowledged counts (item 16, slice finding 14)

**Files:** Modify: `knowledge_harness/inbox.py` (`summary`, ~line 710, and every drain surface that counts). Test: `tests/test_inbox.py`.

- [ ] **Step 1: Failing test**

```python
def test_skipped_entries_not_counted_unacknowledged(tmp_vault):
    # queue holding ONLY SKIPPED-result entries (write via the finding writer)
    assert inbox.summary(tmp_vault)["unacknowledged"] == 0
    # mixed queue: one SKIPPED + one UNMATCHED → count == 1, oldest = the UNMATCHED's date
```

(Locate the `Finding` field carrying `result` in `inbox.py` and the writer tests' scaffolding — copy their fixture shape.)

- [ ] **Step 2: Run — Expected: FAIL** (SKIPPED counts today).
- [ ] **Step 3: Implement:** filter `result == SKIPPED` out of the *counting* path — in `summary()` and every drain surface's unacknowledged arithmetic (grep for `summary(` and `open_entries(` consumers; doctor's inbox probe included). Entries stay RECORDED (audit trail) and stay visible in full listings; only the unacknowledged count and oldest-age basis exclude them — does-not-apply needs no acknowledgment, and counting it manufactures rubber-stamp pressure.
- [ ] **Step 4:** Full suite; commit `fix: SKIPPED findings recorded but never counted unacknowledged`.

