### Task 17: The "unresolved" placeholder never anchors acknowledgments (audit defects, fixity pair)

Disposition: historical (2026-09-06)

**Files:**

- Modify: `research_vault/__main__.py` (attachment loop, ~line 234)

- Modify: `research_vault/verify.py` (`_citekey_hash` fixity adoption, ~line 209)

- Test: `tests/test_import_note.py` (or the file holding import-note frontmatter tests), `tests/test_verify.py`

- [ ] **Step 1: Failing tests, both sides**

```python
def test_unresolved_attachment_omitted_from_fixity(...):
    # import with one attachment whose path resolution raises PathError
    # (monkeypatch _attachment_hash to raise) → rendered frontmatter's
    # fixity-sha256 list does NOT contain "unresolved"; the stderr warning
    # remains (already pinned elsewhere — keep that pin green).

def test_ack_hash_rejects_placeholder_fixity(...):
    # a note whose fixity-sha256 is ["unresolved"] (legacy content) →
    # _citekey_hash falls back to the managed-bytes hash, never adopts
    # the placeholder string.
```

Write these as real tests against the existing fixtures in those files — the shapes above are the contracts; copy the neighboring tests' vault/monkeypatch scaffolding.

- [ ] **Step 2: Run — Expected: FAIL both.**

- [ ] **Step 3: Implement side (a)** — in `__main__.py`'s attachment loop, on the unresolved branch, keep the stderr warning and **do not append** to `hashes` (delete the `hashes.append("unresolved")` line). The field's semantics become: list of successfully hashed attachment digests; absence is honest.

- [ ] **Step 4: Implement side (b)** — in `verify.py`, guard adoption with a digest-shape check so legacy notes can't anchor acks to a constant:

```python
if isinstance(first, str) and re.fullmatch(r"[0-9a-f]{64}", first):
    return first
```

(The existing managed-bytes fallback below already handles the reject path.)

- [ ] **Step 5: Full suite. Commit** `fix: unresolved attachments omit fixity entries; ack scope never anchors to a placeholder`

### Task 17b: Machine-owned frontmatter joins the closing guard (prose-vs-mechanism audit 2026-08-24, bucket-1 finding 2 — the biggest gap: literature frontmatter sits OUTSIDE %%rv-managed%%, so `lint_evidence_layer`'s managed-slice diff never sees it)

**Files:** Modify: `research_vault/lints.py` (`lint_evidence_layer`, ~line 618). Test: `tests/test_lints.py`.

- [ ] **Step 1: Failing test** — a hand-edit to a literature note's `archive-url` (and parametrized: `managed-sha256`, `fixity-sha256`, `generated`, `citekey`) with the managed slice untouched currently passes `lint_evidence_layer`; after the fix it is UNMATCHED (`drift`), while edits to non-machine keys (`status`, free-region prose) still pass — screening is human-writable by design.
- [ ] **Step 2 (legality rule decided 2026-08-24, superseding the managed-slice coupling — which leaks on archive-url's frontmatter-only write AND on attachment-only fixity changes):** a machine-owned key change (`archive-url`, `managed-sha256`, `fixity-sha256`, `citekey`) is legal iff `generated` changed in the same diff with `by` = the machine actor — writer attestation, not slice coupling. `generated` itself stays guarded under its OWN predicate: a `generated` change whose `by` is not the machine actor is drift — no circularity (it can't legalize itself), and Step 1's five-key parametrization stands, with `generated` asserting the second predicate. Scope stated in the lint's finding text: this catches accidents and oblivious agents; forging the attestation is deliberate circumvention (recorded-bypass class, spec §2's stated-boundary language). Extend `lint_evidence_layer` accordingly.
- [ ] **Step 2b:** `archive-source` bumps `generated.{by,at}` on its write (gaining a snapshot IS a meaningful content change; orthogonal to byte-identical-rerender preservation). Test: a legitimate archive run passes the new lint; a bare hand-edit to `archive-url` fails it.
- [ ] **Step 3:** Full suite; commit `fix: closing guard covers machine-owned frontmatter keys via writer attestation`.

