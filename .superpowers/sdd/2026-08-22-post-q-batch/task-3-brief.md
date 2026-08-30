### Task 3: verify-citations de-enumeration + the enumeration checker (items 3–4)

**Files:** Modify: `skills/verify-citations/SKILL.md`; `tests/test_skill_contracts.py`.

- [ ] **Step 1 (C-1):** Replace the check-id enumeration with the canonical obsidian-cli form — the replacement sentence: *"Run the CLI; its output is always up to date."* Teach the four states, not the fourteen ids (the four-state table stays; the id list goes).
- [ ] **Step 2 (C-2):** Correct the registry-scope sentence: TWO registry codes are out of scope, not one (the audit's C-2 card names them — copy from it), and pin with a test.
- [ ] **Step 3 (the enumeration checker):** Generalize the `test_skill_contracts.py:133` instrument: every check id any SKILL.md enumerates must be one `verify` can emit. Write it as a parametrized sweep over `skills/*/SKILL.md` extracting backtick-quoted check ids against the CLI's emitted set (source the canonical set from `research_vault` code, not a hand list).
- [ ] **Step 4:** Full suite; commit `fix: verify-citations defers to CLI output; enumeration checker guards all skills`.

