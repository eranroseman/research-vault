# Pre-Slice Batch — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The single dispatch between Plan Q's merge and slice Phase 2 — instrument freeze for §9: the `project`→`project-flow` rename, the routing index, nine skill-prose corrections from the audits, and four code fixes (SKIPPED counting, tier-2 citekeys, free-region refusal, duplicate-anchor assert).

**Architecture:** One branch, tasks ordered as numbered — the rename precedes the index so the seven entry names are written once, correctly. Skill-prose tasks are edit + test-pin + judged-grep cycles; code tasks are TDD. (The polish pass + four-state dedup stay in their own POST-slice plan: they exist to be informed by slice usage.)

**Tech Stack:** Existing pinned toolchain; no new dependencies.

## Global Constraints

- Read this plan from origin/main at each task start (`git show origin/main:docs/superpowers/plans/2026-08-22-post-q-batch.md`).
- Worktree via `superpowers:using-git-worktrees`, branch `fix/pre-slice-batch`.
- Every test Run begins `source .venv/bin/activate` (`pip install -e ".[dev]" -q` if imports fail).
- Whole-file test pins (`tests/test_skill_files.py`-style) update in the SAME commit as the prose they pin.
- Content sources referenced by task: `docs/2026-08-22-skills-layer-audit.md` (the C-findings and ecosystem steals), `docs/2026-08-22-references-cross-read.md` (items 11–12's itemized annotations). Copy their itemized content verbatim — the triage there is the decided set.
- Suite green offline at each task's end. Commit messages conventional; one commit per task.

______________________________________________________________________

### Task 1: Rename `project` → `project-flow` (item 1)

Ruled 2026-08-22: class-4 collision with CONTEXT.md's *Project* dissolved by the glossary's other governed noun, *Project flow*. Entry family becomes uniformly two-part.

**Files:** Move: `skills/project/` → `skills/project-flow/`. Modify: `docs/terminology.md` §4.3 skills row; routing tables in `skills/find-sources/SKILL.md` and `skills/import-source/SKILL.md`; the skill's content test in `tests/`.

- [ ] **Step 1:** `git mv skills/project skills/project-flow`; update `name:` in its SKILL.md frontmatter to `project-flow`.
- [ ] **Step 2:** Update terminology §4.3's skills row and both routing tables (grep `skills/ -rn "\`project\`"\` and judge each hit — routing rows change; prose about "a project" (the noun) does not).
- [ ] **Step 3:** Update the content test that names the skill (locate via `grep -rn "project" tests/test_skill_contracts.py tests/test_skill_files.py`); run it: PASS.
- [ ] **Step 4:** Judged grep for retired references: `grep -rn "skills/project/\|Skill(project)\|\`project\` skill" --include="\*.md" .\` — every hit either updated or judged non-referential (record the judgment list in the commit body).
- [ ] **Step 5:** Full offline suite. Commit `refactor: rename project skill to project-flow`.

### Task 2: C-7 routing index into the vault AGENTS.md template (item 2)

**Files:** Modify: `knowledge_harness/templates/vault/AGENTS.md`; its whole-file test pin.

- [ ] **Step 1:** Add the index: the seven entry names (post-rename) + one clause each — source each clause from the skill's own description line (compress, don't invent). `tests/test_skill_contracts.py:153`'s self-validation must pass (every cited name exists as a shipped skill).
- [ ] **Step 2:** Update the template's whole-file pin in the same commit; full suite; commit `feat: vault AGENTS.md routing index (C-7)`.

### Task 3: verify-citations de-enumeration + the enumeration checker (items 3–4)

**Files:** Modify: `skills/verify-citations/SKILL.md`; `tests/test_skill_contracts.py`.

- [ ] **Step 1 (C-1):** Replace the check-id enumeration with the canonical obsidian-cli form — the replacement sentence: *"Run the CLI; its output is always up to date."* Teach the four states, not the fourteen ids (the four-state table stays; the id list goes).
- [ ] **Step 2 (C-2):** Correct the registry-scope sentence: TWO registry codes are out of scope, not one (the audit's C-2 card names them — copy from it), and pin with a test.
- [ ] **Step 3 (the enumeration checker):** Generalize the `test_skill_contracts.py:133` instrument: every check id any SKILL.md enumerates must be one `verify` can emit. Write it as a parametrized sweep over `skills/*/SKILL.md` extracting backtick-quoted check ids against the CLI's emitted set (source the canonical set from `knowledge_harness` code, not a hand list).
- [ ] **Step 4:** Full suite; commit `fix: verify-citations defers to CLI output; enumeration checker guards all skills`.

### Task 4: find-sources corrections + cross-read wiring (items 5, 7, 11, 12)

**Files:** Modify: `skills/find-sources/SKILL.md` (+ its `references/` where the cross-read says so); test pins.

- [ ] **Step 1 (C-3 + item 11 fold):** Credential counts align to `redact_url` — the SKILL.md says "several" and defers to `redact_url` as the authority (3 query-string-auth APIs; 6 redacted params live in code, not prose). Mailto: SKILL.md states it is sourced from harness config and that vendored scripts don't read it.
- [ ] **Step 2 (C-5):** One vendoring-note line: upstream prose describes upstream's corpus.
- [ ] **Step 3 (item 12):** One vendoring-note section carrying the six upstream-fact annotations — copy verbatim from the cross-read report's triage (docs/2026-08-22-references-cross-read.md). Add the routing guards: no single-DOI lookups via paginate; the openalex row points at `openalex_abstract.py`; `OPENALEX_API_KEY` env caution.
- [ ] **Step 4:** Pins updated same commit; full suite; commit `fix: find-sources credential/vendoring corrections + cross-read wiring`.

### Task 5: setup-vault C-6 (item 6)

**Files:** Modify: `skills/setup-vault/SKILL.md`; test pins.

- [ ] **Step 1:** Drop the 14-path inventory; keep the six test-pinned paths as an honesty rule, not an inventory (one sentence: the pinned six are the contract; the CLI's scaffold output is the full list).
- [ ] **Step 2:** Pins updated; suite; commit `fix: setup-vault paths are a contract, not an inventory (C-6)`.

### Task 6: import-source references split (item 8)

**Files:** Create: `skills/import-source/references/` (content moved from SKILL.md §7–9). Modify: `skills/import-source/SKILL.md` (pointer table, find-sources shape).

- [ ] **Step 1:** Move §7 (refresh), §8 (batch), §9 (archive) content unchanged into `references/` files; SKILL.md gets the pointer table in find-sources' shape. Content byte-preserved; tests unmoved and green.
- [ ] **Step 2:** Suite; commit `refactor: import-source §7-9 to references with pointer table`.

### Task 7: Prose sweeps — leading word + prohibition cuts (items 9–10)

**Files:** Modify: the SKILL.md files the greps hit; pins.

- [ ] **Step 1 (item 9):** The never-hand-write refrain's five spellings collapse to the single inline token *the CLI writes* (grep for the variants — "never hand-write", "never write by hand", etc. — one token per site, meaning preserved).
- [ ] **Step 2 (item 10):** Delete two prohibitions whose recipes are already present: "not as a raw dump" (find-sources:88), "not in raw run order" (verify-citations:27).
- [ ] **Step 3:** Judged grep confirms no returned prohibitions; pins; suite; commit `style: leading-word collapse + prohibition cuts`.

### Task 8: Ecosystem steals (items 13–14)

**Files:** Modify: `skills/project-flow/SKILL.md`, `skills/synthesis-conventions/SKILL.md`, `skills/import-source/SKILL.md`, `skills/factcheck-draft/SKILL.md`, `skills/publish/SKILL.md`, `skills/setup-vault/SKILL.md`; pins.

- [ ] **Step 1:** Land the adopted set, each sourced from the audit §6/§7 adjudication (copy the decided phrasings): routing guard line in project-flow; compilation-value line in synthesis-conventions; partial-read honesty rule (import-source + factcheck-draft); "validates declarations, not their truth" + the why-one-pass sentence in factcheck-draft; disposition rationalization table in publish (seed rows ported from finishing-a-development-branch per audit §7); publish announces gate-armed at start; setup-vault fails closed on ambiguous vault selection.
- [ ] **Step 2:** Item 14 is a no-op by design: all §6 deferred items carry their triggers in the audit doc — verify none landed here.
- [ ] **Step 3:** Pins; suite; commit `feat: ecosystem-steal prose adoptions (audit §6 adopted set)`.

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

### Task 10: Two-tier citekey check (item 17, spec §4 as ruled 2026-08-22)

**Files:** Modify: `knowledge_harness/checks.py` (`check_citekeys`, ~line 131); `knowledge_harness/inbox.py` (REASON_CODES) or wherever the registry lives; `docs/terminology.md` §4.4 (new row); `skills/evidence-conventions/SKILL.md` reason-code table. Test: `tests/test_checks.py`.

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

### Task 11: Free-region destruction fix (item 18, audit defect 5)

**Files:** Modify: `knowledge_harness/notes.py` (`_split_free`, ~line 141; `render_note`), `knowledge_harness/__main__.py` (`cmd_import_note` catch + review record). Test: `tests/test_notes.py`, `tests/test_import_note.py`.

- [ ] **Step 1: Failing tests**

```python
def test_existing_note_without_marker_refuses_render():
    existing = "---\ntype: literature\n---\nhand-written prose, no marker\n"
    with pytest.raises(notes.RenderIntegrityError):
        notes.render_note(ITEM, ..., existing=existing)

def test_import_refusal_files_review_record_and_exits_1(tmp_vault, ...):
    # cmd_import_note over a marker-less existing note → exit 1, file untouched
    # byte-for-byte, a render/UNMATCHED/schema-violation review record filed
    # (the uniform-wiring contract — same writer the finding verb uses).

def test_fresh_note_still_seeds():  # existing=None → SEED_FREE as today
```

- [ ] **Step 2: Run — Expected: FAIL** (marker-less body silently replaced by `SEED_FREE` today, printed as success).
- [ ] **Step 3: Implement:** `_split_free` distinguishes three cases — `existing` None/empty → `SEED_FREE` (fresh seed); marker found → preserved tail (unchanged); non-empty without marker → raise `RenderIntegrityError("existing note has no managed-close marker — refusing to overwrite the body")`. `cmd_import_note` already routes render rejections to exit 1 + the review record (verify against the import-note skill §1 table: check `render`, UNMATCHED, `schema-violation`); confirm the record actually files, don't assume.
- [ ] **Step 4:** Never-delete (§5) now covers the free region — add the sentence to the spec §5 invariants line in the same commit.
- [ ] **Step 5:** Full suite (the byte-exact free-region preservation test stays green); commit `fix: refuse import over a marker-less note — never reseed the free region`.

### Task 12: Duplicate-anchor render assert (item 19, claim-anchor audit)

**Files:** Modify: `knowledge_harness/notes.py` (`_assert_managed_body_parses`, ~line 260). Test: `tests/test_notes.py`.

- [ ] **Step 1: Failing test** — two identical keyless annotation texts (ids derive from quote hash, truncate to 8 hex) render duplicate `^id` anchors undetected today:

```python
def test_duplicate_anchors_refuse_render():
    annotations = [KEYLESS_ANNOTATION, dict(KEYLESS_ANNOTATION)]  # identical text
    with pytest.raises(notes.RenderIntegrityError):
        notes.render_note(ITEM_WITH(annotations), ...)
```

- [ ] **Step 2: Run — Expected: FAIL** (`parsed != expected` passes when both lists carry the same duplicates).
- [ ] **Step 3: Implement** — one uniqueness line in `_assert_managed_body_parses`:

```python
if len(set(expected)) != len(expected):
    raise RenderIntegrityError(f"duplicate claim anchors in render: {expected!r}")
```

- [ ] **Step 4:** Full suite; commit `fix: render refuses duplicate claim anchors`.

### Task 13: Live-vault index application + acceptance (item 15)

- [ ] **Step 1 (consent-gated):** After Task 2's template landed, update the live vault's AGENTS.md at `~/kh-vault` to the new template content — one file, separate repo; **the vault commit happens only with the author's explicit consent** (ask; do not push to the vault remote without it).
- [ ] **Step 2 (Part 1 checkpoint):** Full suite green offline; `test_skill_contracts` green over the renamed set; judged greps re-run (retired `project` skill references; no returned prohibitions). Do NOT merge yet — Part 2 continues on the same branch; final acceptance and the merge live at Task 21.

______________________________________________________________________

______________________________________________________________________

## Part 2: Trust-core remediation (Plan V, absorbed 2026-08-22)

Closes the no-fabrication audit's remaining trust-core defects (docs/2026-08-22-no-fabrication-audit.md defects 1-3 and 6-8, the RW arming ruling, the additive `relation` read) so slice Phases 4-6 and the gate drill run against remediated gates. Doctrine: missing input is SKIPPED or legible absence, never silence, never a synthesized value; UNMATCHED is never reduced away; trust tiers require evidence, not vacuity. No new dependencies (python-dateutil rejected under §8: the RW CSV's formats are enumerable, so a `strptime` list is the contract match). Part 1's Tasks 10-11 already carry audit defects 4-5.

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

### Task 15: Reduction must not round UNMATCHED to MATCHED (audit defect 2)

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

### Task 16: No vacuous machine-confirmed tier (audit defect 3 + spec §86 gap)

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

### Task 17: The "unresolved" placeholder never anchors acknowledgments (audit defects, fixity pair)

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

### Task 18: Supplied snapshots must be snapshots of THIS url (audit defect, archive)

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

- [ ] **Step 4: Full suite (the live archive legs are env-gated — run them at Task 21). Commit** `fix: supplied archive snapshots verified by shape and target URL`

### Task 19: Partial notice dates keep their precision (audit defect 6)

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

### Task 20: Additive `relation.is-retracted-by` read (queued 2026-08-22)

**Files:**

- Modify: `knowledge_harness/checks.py` (`_crossref_notices`, ~line 533)

- Test: `tests/test_checks.py`

- [ ] **Step 1: Failing test** — a Crossref message fixture with NO `updated-by` but `"relation": {"is-retracted-by": [{"id": "10.1/notice", "id-type": "doi"}]}` yields one blocking notice (type `retraction`, `notice_date` None, the relation id recorded).

- [ ] **Step 2: Run — Expected: FAIL** (only `updated-by` is read today).

- [ ] **Step 3: Implement** — after the `updated-by` loop, read `message.get("relation", {}).get("is-retracted-by", [])`; each well-formed entry appends a blocking record `{"type": "retraction", "notice_date": None, "source": "relation", ...}` **unless** an `updated-by` retraction for the same work already exists (no double-count). Malformed relation entries are ignored (the field is additive — it may only add signal, never change an existing verdict). Add the no-double-count test.

- [ ] **Step 4: Full suite. Commit** `feat: read Crossref relation.is-retracted-by as an additive retraction signal`

### Task 21: Spec gap closures + acceptance

**Files:**

- Modify: `docs/superpowers/specs/2026-08-16-foundation-spec.md` (§6 gate rows: metadata, update-notice)

- Modify: `docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md` (second sequencing gate: mark satisfied)

- [ ] **Step 1: Metadata row (§6, ~line 98)** — append: *"A compared field absent on either side is SKIPPED for that field, recorded in the outcome's detail — never folded into MATCHED (closed 2026-08-22, audit gap)."* Then verify the implementation agrees (read `check_metadata`'s absent-field handling; if it silently folds, fix it with a failing-test-first micro-cycle inside this task and note it).

- [ ] **Step 2: Update-notice row (§6, ~line 99)** — append the missing-local-version rule by the four-state definitions: *"an item lacking a local `version` field is SKIPPED for the version leg (the item lacks the field the check needs) — never UNREACHABLE, which is reserved for attempted-and-failed"* — then reconcile the implementation (`_datacite_version_outcome` / arXiv twin report UNREACHABLE "outage — version status unavailable" for a missing local field today; both audit lanes disputed this — settle it by the doctrine definition, failing test first, and record the resolution in the commit body).

- [ ] **Step 3: Acceptance sweep** — re-run the audit's confirmed reproductions for every defect this plan claims (defects 1, 2, 3, 6, the fixity pair, the archive branch): each must now be unreproducible. Full suite offline AND live (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>`, Zotero running). 8/8 hooks.

- [ ] **Step 4: Mark BOTH Plan S sequencing gates satisfied** (one line each, dated, pointing at this plan) — Phases 2–6 and the drill unblock together.

- [ ] **Step 5: Commit** `fix: close spec §6 missing-data gaps; trust-core remediation acceptance` — then merge to main and push in the same motion.

______________________________________________________________________

## NOT in this plan

Four-state dedup (migrate 3–4 — RED-gated) · anything the in-flight references cross-read confirms beyond items 11–12's decided set (triaged separately when it reports) · the skills polish pass + skill-eval lane (POST-slice, informed by usage).

Plan V (docs/superpowers/plans/2026-08-22-plan-v-trust-core-remediation.md) was absorbed here as Part 2 on 2026-08-22 — the two plans were forced serial by shared `checks.py` test surfaces, and Phase 3's imports run the very checks Part 2 remediates, so one combined merge unblocks slice Phases 2–6 and the drill together. That file remains as a tombstone pointer.

## Self-Review (at authoring)

- **Item coverage**: all 19 numbered items of the ruled list map to Tasks 1–13 (items 3+4→T3; 5+7+11+12→T4; 9+10→T7; 13+14→T8; 15→T13); audit defects map 4→T10, 5→T11, 1→T14, 2→T15, 3→T16, fixity pair→T17, archive→T18, 6→T19, relation→T20, spec gaps 86/98/99→T16/T21. Nothing dropped; item 14 is an explicit no-op verification.
- **Placeholder scan**: code tasks (9–12, 14–21) carry failing-test shapes with located scaffolding sources and exact implementation deltas; prose tasks name their content source docs (audit adjudication, cross-read triage) where the decided text is itemized — copy-verbatim instructions, not TBDs.
- **Order dependencies**: T1 (rename) before T2 (index) before T13 (live vault gets the final template). T10's reason-code registration is same-commit with its check (dialect-surface rule). Part 2 runs after Part 1 (shared `checks.py`/inbox test surfaces — T10 and T14–15 touch the same file family). Acceptance consolidates at T21: full suite offline AND live, the audit's reproductions unreproducible, BOTH Plan S sequencing gates marked satisfied.
- **Line numbers** read at 8e98a02/dd4e9f9; re-locate by content if drifted.
