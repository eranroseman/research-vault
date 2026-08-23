# Plan V: Trust-Core Remediation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the no-fabrication audit's remaining trust-core defects (docs/2026-08-22-no-fabrication-audit.md, defects 1–3 and 6–8 plus the RW arming question and the additive `relation` read) so slice Phases 4–6 and the gate drill run against remediated gates.

**Architecture:** Surgical fixes inside existing modules — no new modules, no new dependencies, no schema changes beyond one honest-absence rule. Every fix follows four-state doctrine: missing input is SKIPPED or legible absence, never silence, never a synthesized value; UNMATCHED is never reduced away; trust tiers require evidence, not vacuity.

**Tech Stack:** Existing pinned toolchain only. No new runtime dependencies — the one tempting one (python-dateutil for Task 1) is explicitly rejected under §8: the RW CSV's formats are a small enumerable set, so a `strptime` format list is the contract match and guess-anything coercion is the shape §8 already rejected in pydantic.

## Global Constraints

- **Sequencing: dispatch AFTER the pre-slice batch merges** (docs/superpowers/plans/2026-08-22-post-q-batch.md) — the batch carries audit defects 4 (item 17, tier-2 citekey) and 5 (item 18, free-region destruction); this plan carries the rest. Do not start both branches concurrently; they share `checks.py`/`inbox` test surfaces.
- This plan **gates slice Phases 4–6 and the synthetic drill** (Plan S, second sequencing gate). Its acceptance is the §9 "remediated gates" reference closing.
- Worktree via `superpowers:using-git-worktrees`, branch `fix/trust-core`.
- Read this plan from origin/main at each task start (`git show origin/main:docs/superpowers/plans/2026-08-22-plan-v-trust-core-remediation.md`) — it may be amended mid-flight.
- Every test Run begins `source .venv/bin/activate` (venv exists; `pip install -e ".[dev]" -q` if imports fail).
- Suite green offline at each task's end; live legs (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>`) at Task 8 acceptance.
- Line numbers below were read at 8e98a02; re-locate by content if drifted. Commit messages conventional; one commit per task.

______________________________________________________________________

### Task 1: RW date parsing + arming honesty (audit defect 1 + the arming ruling)

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

______________________________________________________________________

### Task 2: Reduction must not round UNMATCHED to MATCHED (audit defect 2)

**Files:**
- Modify: `knowledge_harness/checks.py` (`reduce_update_notice_outcomes`, ~line 1024)
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

______________________________________________________________________

### Task 3: No vacuous machine-confirmed tier (audit defect 3 + spec §86 gap)

**Files:**
- Modify: `knowledge_harness/events.py` (`trust_tier`, ~line 240)
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

______________________________________________________________________

### Task 4: The "unresolved" placeholder never anchors acknowledgments (audit defects, fixity pair)

**Files:**
- Modify: `knowledge_harness/__main__.py` (attachment loop, ~line 234)
- Modify: `knowledge_harness/verify.py` (`_citekey_hash` fixity adoption, ~line 209)
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

______________________________________________________________________

### Task 5: Supplied snapshots must be snapshots of THIS url (audit defect, archive)

**Files:**
- Modify: `knowledge_harness/archive.py` (supplied-snapshot branch, ~lines 166–185; `is_archive_url` or a new `_snapshot_original`)
- Test: `tests/test_archive.py`

- [ ] **Step 1: Failing tests**

```python
def test_supplied_snapshot_must_have_wayback_shape(...):
    # snapshot="https://web.archive.org/" (host-only, alive) → UNMATCHED
    # "missing-archive — supplied snapshot is not a Wayback snapshot URL"

def test_supplied_snapshot_must_match_note_url(...):
    # note url = "https://example.org/paper", snapshot =
    # "https://web.archive.org/web/20240101000000/https://other.site/page"
    # → UNMATCHED "missing-archive — supplied snapshot is for a different URL"
```

- [ ] **Step 2: Run — Expected: FAIL** (today `is_archive_url` + non-404 liveness suffices and both cases record MATCHED).

- [ ] **Step 3: Implement** — parse the supplied snapshot before any network call:

```python
_SNAPSHOT_RE = re.compile(
    r"^https?://web\.archive\.org/web/(\d{4,14})(?:[a-z_]+)?/(?P<original>https?://.+)$"
)
```

Shape fails → the first UNMATCHED. Shape passes → compare `original` against the note's `url` after the same normalization the codebase already uses for URL comparison (locate it — do not invent a second normalizer; if none exists, exact-match after stripping a single trailing slash and lowercasing scheme+host only). Mismatch → the second UNMATCHED. Then the existing liveness probe and `_record` proceed unchanged.

- [ ] **Step 4: Full suite (the live archive legs are env-gated — run them at Task 8). Commit** `fix: supplied archive snapshots verified by shape and target URL`

______________________________________________________________________

### Task 6: Partial notice dates keep their precision (audit defect 6)

**Files:**
- Modify: `knowledge_harness/checks.py` (`_notice_date_from_updated`, ~line 506; the reinstatement-clears comparison — locate by `notice_date` ordering use)
- Test: `tests/test_checks.py`

- [ ] **Step 1: Failing tests**

```python
def test_partial_date_parts_keep_precision():
    assert checks._notice_date_from_updated({"date-parts": [[2023]]}) == "2023"
    assert checks._notice_date_from_updated({"date-parts": [[2023, 6]]}) == "2023-06"
    assert checks._notice_date_from_updated({"date-parts": [[2023, 6, 15]]}) == "2023-06-15"

def test_ambiguous_reinstatement_does_not_clear():
    # retraction notice_date "2023" (year-only), reinstatement "2023-06-15":
    # the ordering is ambiguous at shared precision → the alert STANDS.
```

- [ ] **Step 2: Run — Expected: FAIL** (year-only pads to `2023-01-01` today, and the padded date lets the June reinstatement clear the alert).

- [ ] **Step 3: Implement** — `_notice_date_from_updated` returns the ISO-prefix string at the given precision (validate ranges via `_date(year, month or 1, day or 1)` but *emit* only the supplied parts). The reinstatement-clears comparison becomes conservative: it clears **only when** `retraction_date < reinstatement_date` is unambiguous — i.e., neither is a strict prefix of the other and plain string comparison decides, or both are full dates. A prefix-ambiguous pair keeps the alert standing (fail-safe: a standing alert costs an ack; a wrongly-cleared retraction costs the thesis).

- [ ] **Step 4: Trace every consumer of `notice_date`** (grep; the reduction's `max()` key, inbox record fields, ack fingerprints). String ordering over ISO prefixes is already consistent for the `max()` newest-wins key; inbox and fingerprints carry the honest partial string. Record each consumer checked in the commit body.

- [ ] **Step 5: Full suite; fix tests that pinned padded dates (note each). Commit** `fix: partial Crossref dates keep precision; ambiguous reinstatement never clears`

______________________________________________________________________

### Task 7: Additive `relation.is-retracted-by` read (queued 2026-08-22)

**Files:**
- Modify: `knowledge_harness/checks.py` (`_crossref_notices`, ~line 533)
- Test: `tests/test_checks.py`

- [ ] **Step 1: Failing test** — a Crossref message fixture with NO `updated-by` but `"relation": {"is-retracted-by": [{"id": "10.1/notice", "id-type": "doi"}]}` yields one blocking notice (type `retraction`, `notice_date` None, the relation id recorded).

- [ ] **Step 2: Run — Expected: FAIL** (only `updated-by` is read today).

- [ ] **Step 3: Implement** — after the `updated-by` loop, read `message.get("relation", {}).get("is-retracted-by", [])`; each well-formed entry appends a blocking record `{"type": "retraction", "notice_date": None, "source": "relation", ...}` **unless** an `updated-by` retraction for the same work already exists (no double-count). Malformed relation entries are ignored (the field is additive — it may only add signal, never change an existing verdict). Add the no-double-count test.

- [ ] **Step 4: Full suite. Commit** `feat: read Crossref relation.is-retracted-by as an additive retraction signal`

______________________________________________________________________

### Task 8: Spec gap closures + acceptance

**Files:**
- Modify: `docs/superpowers/specs/2026-08-16-foundation-spec.md` (§6 gate rows: metadata, update-notice)
- Modify: `docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md` (second sequencing gate: mark satisfied)

- [ ] **Step 1: Metadata row (§6, ~line 98)** — append: *"A compared field absent on either side is SKIPPED for that field, recorded in the outcome's detail — never folded into MATCHED (closed 2026-08-22, audit gap)."* Then verify the implementation agrees (read `check_metadata`'s absent-field handling; if it silently folds, fix it with a failing-test-first micro-cycle inside this task and note it).

- [ ] **Step 2: Update-notice row (§6, ~line 99)** — append the missing-local-version rule by the four-state definitions: *"an item lacking a local `version` field is SKIPPED for the version leg (the item lacks the field the check needs) — never UNREACHABLE, which is reserved for attempted-and-failed"* — then reconcile the implementation (`_datacite_version_outcome` / arXiv twin report UNREACHABLE "outage — version status unavailable" for a missing local field today; both audit lanes disputed this — settle it by the doctrine definition, failing test first, and record the resolution in the commit body).

- [ ] **Step 3: Acceptance sweep** — re-run the audit's confirmed reproductions for every defect this plan claims (defects 1, 2, 3, 6, the fixity pair, the archive branch): each must now be unreproducible. Full suite offline AND live (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>`, Zotero running). 8/8 hooks.

- [ ] **Step 4: Mark the Plan S second sequencing gate satisfied** (one line, dated, pointing at this plan) — Phases 4–6 and the drill unblock.

- [ ] **Step 5: Commit** `fix: close spec §6 missing-data gaps; trust-core remediation acceptance` — then merge to main and push in the same motion.

______________________________________________________________________

## Self-Review (at authoring)

- **Audit coverage**: defects 1 (T1), 2 (T2), 3 (T3), 6 (T6), fixity pair (T4), archive (T5), RW arming (T1), relation field (T7), spec gaps 86/98/99 (T3/T8). Defects 4 and 5 are batch items 17/18 by prior ruling — deliberately absent here. Medium-severity audit items 9–16 stay with their existing routings (batch, polish pass) — this plan is the Phases-4–6 gate only.
- **Placeholder scan**: Tasks 1–3 and 5–7 carry executable test/implementation code. Task 4's tests and Task 8's reconciliations are specified as contracts with located scaffolding sources rather than full listings — the executor copies adjacent fixtures; the assertions given are complete.
- **Known judgment calls made here, not deferred**: no-default for `--rw-csv` (deliberate network/license act); UNMATCHED outranks MATCHED in reduction fallback; zero-checkable notes are `unverified`; ambiguous partial-date comparisons fail safe (alert stands); relation read is additive-only. Each is recorded in its task so the executor implements a decision, not a question.
- **The one place this plan may find more work**: Task 8 Steps 1–2 verify spec-vs-implementation agreement and may surface a silent fold in `check_metadata` or the version-leg UNREACHABLE dispute — both are micro-cycles inside the task by design, not new tasks.
