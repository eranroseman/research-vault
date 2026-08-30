### Task 10: Two-tier citekey check (item 17, spec §4 as ruled 2026-08-22)

**Files:** Modify: `research_vault/checks.py` (`check_citekeys`, ~line 131); `research_vault/inbox.py` (REASON_CODES) or wherever the registry lives; `docs/terminology.md` §4.4 (new row); `skills/evidence-conventions/SKILL.md` reason-code table. Test: `tests/test_checks.py`.

**Interfaces:** `check_citekeys` signature unchanged; new reason code `not-imported`.

- [ ] **Step 1: Failing tests**

```python
def test_cited_citekey_requires_literature_note(tmp_vault):
    # citekey present in bibliography, literatures/<citekey>.md absent:
    outcome = ...  # run check_citekeys on a draft citing it
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith("not-imported")

def test_cited_citekey_with_note_passes(tmp_vault): ...      # MATCHED as today
def test_cited_citekey_absent_everywhere(tmp_vault): ...     # existing "mismatch — citekey not in bibliography"
```

- [ ] **Step 2: Run — Expected: FAIL** (bibliography membership alone MATCHES today).
- [ ] **Step 3: Implement:** in the per-citekey loop, bibliography-present + note-absent → `Result.UNMATCHED`, reason `"not-imported — cited citekey has no literature note"`. The note's OWN citekey row (note-vs-bibliography identity) keeps current semantics — scope the new rule to citations only.
- [ ] **Step 4:** Register `not-imported` (distinct from `not-admitted`) in the reason-code registry, terminology §4.4, and evidence-conventions' table — same commit (dialect-surface rule).
- [ ] **Step 5:** Full suite; commit `feat: tier-2 citability — cited citekeys require a literature note (not-imported)`.

