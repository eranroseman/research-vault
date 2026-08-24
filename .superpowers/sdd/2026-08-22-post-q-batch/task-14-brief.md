### Task 14: RW date parsing + arming honesty (audit defect 1 + the arming ruling)

**Files:**

- Modify: `knowledge_harness/checks.py` (`_rw_date`, ~line 910)
- Modify: `knowledge_harness/verify.py` (RW-leg absence line, near `notice_lookup = checks.load_rw_csv(rw_csv) if rw_csv else None`, ~line 986)
- Test: `tests/test_checks.py`, `tests/test_verify.py`

**Interfaces:** `_rw_date(value) -> str | None | object` contract unchanged (ISO string, `None` for empty, `_INVALID` sentinel). No signature changes anywhere.

- [ ] **Step 1: Failing test — production date formats parse**

```python
def test_rw_date_accepts_production_formats():
    assert checks._rw_date("1/2/2023 0:00") == "2023-01-02"
    assert checks._rw_date("12/31/2019") == "2019-12-31"
    assert checks._rw_date("2023-01-02") == "2023-01-02"  # ISO still accepted
    assert checks._rw_date("not a date") is checks._INVALID
    assert checks._rw_date("13/45/2023 0:00") is checks._INVALID
```

- [ ] **Step 2: Run** `pytest tests/test_checks.py::test_rw_date_accepts_production_formats -v` — Expected: FAIL (first two assertions return `_INVALID` today).

- [ ] **Step 3: Implement** — replace the `fromisoformat`-only body with an enumerated format loop:

```python
_RW_DATE_FORMATS = ("%m/%d/%Y %H:%M", "%m/%d/%Y")

def _rw_date(value) -> str | None | object:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if not isinstance(value, str):
        return _INVALID
    text = value.strip()
    try:
        return _date.fromisoformat(text).isoformat()
    except ValueError:
        pass
    for fmt in _RW_DATE_FORMATS:
        try:
            return _datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return _INVALID
```

(`_datetime` = `datetime.datetime`; add the import alias beside `_date` if absent.)

- [ ] **Step 4: Failing test — unarmed RW leg is legible, not silent.** The `verify` output summary must carry exactly one line when `--rw-csv` was not supplied, e.g. `update-notice: RW leg not run (no --rw-csv)`. Write the test against whatever summary surface `verify` already prints (locate the existing summary emission in `verify.py`; assert on captured stdout of a minimal vault run without `--rw-csv`). This is a stdout line, NOT a review-queue record — no new reason code, no inbox noise (the SKIPPED-counting lesson, slice finding 14).

- [ ] **Step 5: Implement the one-line emission. Run both tests + full offline suite. Commit** `fix: RW date parsing accepts production formats; unarmed RW leg says so`

**Arming ruling implemented by this task (record in the commit body):** the RW leg's home is the scheduled CI lane (`templates/ci/rw-batch.yml`, already passes `--rw-csv`) and the drill runs it explicitly armed (Plan S amendment already recorded); local `verify` without the flag now states the absence. No default-on: fetching the RW CSV is a network+license act that stays deliberate.

