### Task 16: No vacuous machine-confirmed tier (audit defect 3 + spec §86 gap; also closes [issue #17](https://github.com/eranroseman/knowledge-harness/issues/17) — human-reviewed tier unreachable — read the issue and cover it in this task's tests; reference #17 in the commit)

**The reason, for the test name and the docstring:** an empty applicable-check set satisfies "every applicable check passed" vacuously, and vacuous truth is not evidence. A machine tier needs at least one check that ran and passed — otherwise a note with no identifiers, no quotes, and no verified events derives the top tier, which is what it does at HEAD.

**Files:**

- Modify: `research_vault/events.py` (`trust_tier`, ~line 240)

- Modify: `docs/superpowers/specs/2026-08-16-foundation-spec.md` (§5 Event-integrity paragraph)

- Test: `tests/test_events.py`

- [ ] **Step 1: Failing test**

```python
def test_no_identifier_no_claims_note_is_unverified():
    text = "---\ntype: literature\ncitekey: url2024only\nurl: https://example.org\n---\nbody\n"
    assert events.trust_tier(text) == "unverified"

def test_frontmatterless_text_is_unverified():
    assert events.trust_tier("just some text\n") == "unverified"
```

- [ ] **Step 2: Run** — Expected: FAIL, both return `"machine-confirmed"` today (empty applicable set, subset test vacuously true, no quote claims to block it).

- [ ] **Step 3: Implement** — machine-confirmed requires evidence, not absence of counter-evidence. After the existing `machine_confirmed` computation, add the checkability floor:

```python
has_applicable = bool(_applicable_note_checks(data))
has_managed_quotes = any(
    claim.tag == "quote" and claim.in_managed and claim.claim_id
    for claim in claims_mod.parse_claims(note_text)
)
if not has_applicable and not has_managed_quotes:
    machine_confirmed = False
```

(Reuse the existing `parse_claims` iteration rather than iterating twice if straightforward — a flag set inside the current loop plus the `has_applicable` check is equivalent.)

- [ ] **Step 4: Spec amendment, same commit** — §5's event-integrity paragraph gains one sentence: *"An item with no applicable note-level checks and no managed quote claims derives `unverified` — the machine tiers require at least one deterministic check to have run and matched, never vacuous satisfaction (closed 2026-08-22, audit defect 3)."*

- [ ] **Step 5: Full suite; fix any test that pinned the vacuous tier (say so per-test in the commit body). Commit** `fix: trust tier requires evidence — no vacuous machine-confirmed`

