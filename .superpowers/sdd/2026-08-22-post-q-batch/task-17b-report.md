# Task 17b report: Machine-owned frontmatter joins the closing guard

## Status

Complete. All three steps (failing test, legality rule, `archive-source`
attestation) implemented, full suite green, form gate silent/exit 0.

## Commit

`f3f5a7f` — `fix: closing guard covers machine-owned frontmatter keys via writer attestation`

Files: `research_vault/lints.py`, `research_vault/archive.py`,
`tests/test_lints.py`, `tests/test_archive.py`, `tests/test_verify_cli.py`
(5 files, +313/-3).

## Test summary

`python -m pytest -q`: **1577 passed, 7 skipped** (baseline 1569 passed / 7
skipped + 8 new tests). `ruff check` and `ruff format --check` clean on all
touched files; `mypy` clean on `lints.py`/`archive.py`. Form gate
(`echo '{}' | python hooks/stop_publish_gate.py`) silent, exit 0.

## What was implemented

- `lints.py`: `lint_evidence_layer`'s surviving-file loop (the one already
  comparing `_managed_bytes(old) != _managed_bytes(new)`) now also compares
  four machine-owned frontmatter keys — `archive-url`, `managed-sha256`,
  `fixity-sha256`, `citekey` — plus `generated` under its own predicate. A
  change to any of the four is legal iff `generated` also changed in the same
  diff with `by` a machine-actor-class string (`startswith("research_vault/")`,
  per docs/terminology.md's actor convention — a class test, not an
  exact-version match, so a `__version__` bump doesn't flag every prior note).
  `generated` itself is drift if it changes without its own new `by` being
  machine-class. Reason string: `drift — {key} changed without writer attestation`.
- `archive.py`: `_record` (the sole writer path for `archive-url`) now also
  bumps `generated` via a new `_bump_generated` — byte-surgical, insert-or-replace
  (mirrors `set_archive_url`'s structure but was kept as a separate function
  rather than refactored into a shared helper, to avoid destabilizing
  `set_archive_url`'s existing, well-tested behavior). This closes the gap
  fact #4 named: without it, every legitimate `archive-source` run would
  write `archive-url` with no attestation and get flagged as drift by the
  new lint.

## Per-key discrimination (Step 1, TDD)

Ran `tests/test_lints.py::test_hand_edited_machine_owned_frontmatter_key_is_drift`
(parametrized over the 5 keys) before implementing the lints.py change, then
after:

| key | pre-fix (RED) | post-fix (GREEN) |
|---|---|---|
| `archive-url` | assertion failed, no drift outcome at all | `drift — archive-url changed without writer attestation` present |
| `managed-sha256` | assertion failed; outcomes contained only `schema-violation — stale managed-sha256` (the pre-existing witness check) — the specific new drift reason was absent, proving this isn't the hazard-#5 false pass | `drift — managed-sha256 changed without writer attestation` present, alongside the still-present schema-violation outcome |
| `fixity-sha256` | assertion failed, no drift outcome | `drift — fixity-sha256 changed without writer attestation` present |
| `generated` | assertion failed, no drift outcome (edit was to `by`, forcing a non-machine value) | `drift — generated changed without writer attestation` present |
| `citekey` | assertion failed, no drift outcome | `drift — citekey changed without writer attestation` present |

Captured failure for `managed-sha256` (the hazard-#5 case, verbatim):
```
AssertionError: [Outcome(check='evidence-layer', target='path-bytes:literatures/smith2020.md',
result=UNMATCHED, reason='schema-violation — stale managed-sha256', ...)]
```
i.e. the pre-existing witness check's UNMATCHED was present both before and
after my change; only the *specific new reason string* discriminates, and the
test asserts that string, not overall UNMATCHED-ness.

`test_screening_status_hand_edit_is_not_evidence_layer_drift` (status is
human-writable by design) and the pre-existing
`test_free_region_only_edit_is_not_evidence_layer_change` both stay green
throughout — non-machine edits are unaffected.

## Step 2b, both directions

- `tests/test_archive.py::test_a_legitimate_archive_run_passes_the_closing_guard`:
  **RED before** the `archive.py` change (`archive_source` wrote `archive-url`
  with no `generated` bump → the new lints.py check flagged it as
  `drift — archive-url changed without writer attestation`, proving Step 2b is
  load-bearing, not tidying). **GREEN after** `_bump_generated` was wired into
  `_record`.
- `tests/test_archive.py::test_a_bare_archive_url_hand_edit_fails_the_closing_guard`:
  green throughout (already covered by the Step 1 lints.py change alone) —
  included to demonstrate the two archive-url paths, real write vs. hand-edit,
  land on opposite sides of the guard.

## Deviations from the brief's file list

- `tests/test_archive.py` was modified even though the brief's "Files:" line
  only named `tests/test_lints.py`. Step 2b's tests need `archive.py`'s
  existing network-mock seam (`_fake_network`, `net_vault`, `WEB_NOTE`), which
  lives in `test_archive.py`; duplicating that infrastructure in
  `test_lints.py` seemed worse than the file-list deviation. Also updated
  `test_recording_preserves_every_other_byte_of_the_note` in the same file:
  the byte-preservation assertion had to additionally strip the new
  `generated` line (located by prefix, not predicted, since the timestamp is
  `datetime.now()`).
- `tests/test_verify_cli.py::test_no_attachment_acknowledged_warning_stays_suppressed_across_effects`
  broke as collateral: its setup hand-edits `smith2020.md` on disk to remove
  `fixity-sha256` (simulating "note with no attachment hash") without
  committing, so `verify_state`'s base (HEAD) vs. candidate (worktree) now
  correctly disagree on that key and the new lint reports drift — an accurate
  finding, since the test's own setup is literally the kind of unattested
  hand-edit this task guards against, just used as unrelated scaffolding. Fixed
  by committing the fixture mutation (`git add -A` + commit, the same idiom
  already used elsewhere in that file, e.g.
  `test_deleted_claim_with_invalid_utf8_has_a_stable_target_hash`) so base and
  candidate agree and the unrelated warning-suppression assertion is
  unaffected. No other `verify_state`/`lint_evidence_layer`-driving test in
  the suite touched a machine-owned key without a commit; the other four
  `fixity-sha256`-editing call sites in `test_verify_cli.py` all call
  `_target_hash` directly and never exercise `lint_evidence_layer`.

## Checked and closed (not a concern)

`render_note`'s only production caller is `__main__.py:270`, which always
passes an explicit `generated_at` (second-resolution timestamp). So the
"omitted `generated_at` defaults to date resolution, making a same-day
re-render's `generated` byte-identical to the prior one and masking a real
content change as unattested" tail case does not occur in production;
`grep -rn "render_note(" research_vault/` confirms this is the only
non-test call site.

## Concerns (not fixed — out of scope per the brief)

1. **Other `MANAGED_FIELDS` stay outside the guard.** `type`, `aliases`,
   `doi`, `url`, `pmid`, `version`, `accessed` are all in
   `notes.MANAGED_FIELDS` and all sit outside `%%rv-managed%%`, but the brief's
   Step 1 parametrization named exactly five keys (`archive-url`,
   `managed-sha256`, `fixity-sha256`, `generated`, `citekey`), so I scoped
   `_MACHINE_OWNED_FRONTMATTER_KEYS` to match. A hand-edit to, say, `doi`
   alone (no other machine-key change) would still pass silently.
2. **Duplicate-key evasion.** `frontmatter.parse` is last-key-wins on a
   duplicated line (`_DuplicateKeyMapping` preserves order for serialization
   but `.get()` returns the last value). A duplicated machine-owned key whose
   *final* copy matches the base value would evade the value comparison in
   `_frontmatter_attestation_outcomes`. Only `managed-sha256` has an
   independent duplicate guard, via `notes.validate_managed_witness`'s
   "schema-violation — duplicate managed-sha256" check in the first loop; the
   other three keys have no such guard.
3. **Renamed files skip the new check.** The rename-pairing logic (lines
   ~639–664) removes paired old/new paths from the surviving-files
   intersection before my new check runs, so a rename that also hand-edits a
   machine-owned key gets the wholesale
   `drift — managed literature note renamed` outcome but not a per-key
   reason. Coverage isn't silently lost (the rename itself is always
   flagged), but the specific-key diagnostic is.
4. **Forged attestation is out of scope by design.** A hand-edit that also
   sets `generated.by` to a machine-class-shaped string (e.g. keeps
   `"research_vault/0.1.0"` unchanged, or forges it) passes the guard —
   this is the brief's own stated boundary (recorded-bypass class, spec §2's
   stated-boundary language): the lint catches accidents and oblivious
   agents, not deliberate circumvention.

## Round 1 (fix round, review feedback on f3f5a7f)

### Status

Complete. All IMPORTANT and MINOR items addressed except the four items the
reviewer explicitly deferred. Full suite green, form gate silent/exit 0,
ruff and mypy clean.

### Commit

`5ac70df` — `fix: round-1 review fixes for the machine-owned-frontmatter guard (task 17b)`
(new commit, `f3f5a7f` left untouched, no rebase — 8 files, +233/-54).

### Test summary

`python -m pytest -q`: **1581 passed, 7 skipped** (was 1577/7; +4 new
regression tests — two parametrized cases for Important 1, one each for
Minor B and Minor C). `ruff check`/`ruff format --check` clean, `mypy
research_vault/` clean, form gate silent/exit 0.

### IMPORTANT 1 — malformed `generated` no longer attests

`_machine_attested` now calls `notes._valid_generated(generated)` (shape:
exactly `{by, at}`, `at` a valid `Z`-suffixed ISO 8601 timestamp) before
checking `by`'s class prefix, instead of testing `by` alone. Added
`test_malformed_generated_does_not_attest_a_machine_owned_key_change`,
parametrized over `{by: "research_vault/0.1.0", at: "banana"}` and
`{by: "research_vault/0.1.0"}` (no `at`) — both RED against the prior
`by`-only predicate, both GREEN after.

**Interlock proof (not assumed):** re-ran
`test_a_legitimate_archive_run_passes_the_closing_guard` after tightening
the shape check — still PASSED, because `archive._bump_generated`'s emitted
`at` (via the new `notes.generated_at_now()`) already satisfies
`_valid_generated`'s shape (second-resolution, `Z`-suffixed, 2-item dict).

### IMPORTANT 2 — the absence claim, redone properly

Applied the same "commit the fixture mutation" treatment already used at
the round-0 site to the two sites the review named
(`test_no_fixity_target_hashes_are_candidate_bound_before_projection`,
`test_no_fixity_acknowledgment_is_decided_from_candidate_before_projection`).

Then established the absence claim by instrumentation, not grep: temporarily
added `if outcomes and os.environ.get("HK_AUDIT_ATTESTATION"): raise
RuntimeError(...)` at the end of `_frontmatter_attestation_outcomes`, ran
`HK_AUDIT_ATTESTATION=1 python -m pytest -q` (full suite), and read off every
failure — the raise makes any test that reaches this check with a non-empty
outcome list fail loudly, whether or not it asserts on outcomes.

Result: **17 failures**. Classified each:
- 7 are tests that *intentionally* assert for drift and so are audit
  artifacts, not bugs: this task's own 5 parametrized
  `test_hand_edited_machine_owned_frontmatter_key_is_drift` cases,
  `test_a_bare_archive_url_hand_edit_fails_the_closing_guard`, and a
  pre-existing `test_managed_change_always_yields_typed_evidence_finding_with_fresh_witness[edit]`
  (its managed-region edit also changes `managed-sha256`, which the new check
  correctly flags too — the test's own assertion only checks the reason
  starts with "drift", so it was never failing for real).
- 10 parametrized cases across 3 distinct test functions were real: the two
  the review named, plus one more the review did not name —
  `test_ack_suppresses_effects_but_retains_raw_outcome_and_reopens_on_hash`,
  which hand-edits `fixity-sha256`'s *value* (not a removal) at the very end
  of the test, uncommitted, then calls `run_verify`. Fixed the same way:
  commit the mutation before the `verify_state`/`run_verify` call.

Reverted the instrumentation, re-ran the same audit command: only the 7
intentional-positive tests failed. No further unasserted sites in the suite.

### IMPORTANT 3 — boundary statement moved to the docstring

`_frontmatter_attestation_outcomes`'s docstring now states the stated-boundary
form verbatim (catches accidents and oblivious agents; forging the
attestation is deliberate circumvention, recorded-bypass class; stated
boundary, not a compliance control) and folds in piggy-backing (one
legitimate `generated` bump legalizes any other machine-owned key riding
along unattested in the same diff — this was disclosed-nowhere before; my
own concern 4 only covered forging). No reason strings changed. No ADR
added. The commit body repeats the boundary statement.

### MINOR A — one spelling of the wire format

- Added `frontmatter.render_field(key, value)`; `serialize()` now calls it
  for the scalar/dict branches, and `archive.set_archive_url`/`_bump_generated`
  both use it instead of hand-rolling the inline-dict emitter.
- Added `notes.generated_at_now(now=None)`; `archive._generated_at` (deleted)
  and `__main__.cmd_import_note`'s inline two-line duplicate both now call
  it. `archive.py` no longer imports `datetime` at all.

### MINOR B — raw-value comparison for `generated`

`_generated()` (which coerced any non-dict to `None`) is gone; comparisons
now go through `_field(data, key)`, which returns the raw value regardless of
shape. Added `test_two_unequal_junk_generated_values_are_not_seen_as_unchanged`
(two different non-dict `generated` values, e.g. `"junk-one"` vs `"junk-two"`)
— RED against the old coercion (both collapsed to `None`, comparing equal),
GREEN after.

### MINOR C — unparseable base no longer skips the whole check

Removed the `if base_data is None or candidate_data is None: return []`
short-circuit; `_field()` returns `None` for an unparseable side per key, so
a real value on the other side now compares unequal instead of being
silently skipped. Added
`test_unparseable_base_frontmatter_does_not_skip_the_per_key_check` (base
frontmatter has an injected `nested maps unsupported` line, candidate is
valid) — RED against the old short-circuit, GREEN after.

All four new correctness tests were verified in both directions: I
temporarily reverted `_field`/`_machine_attested`/`_frontmatter_attestation_outcomes`
to the pre-round-1 implementation in place, ran the 4 new tests (3 failed,
confirming discrimination; the fourth needed one iteration — see below),
then restored the fix and reran (all 4 passed).

**One test needed a redesign to actually discriminate:** my first version of
the Minor B test also changed `citekey` in the same edit, so it passed even
against the buggy code — citekey's own diff is detected independently of the
`generated` coercion, so that assertion didn't isolate the bug. Rewrote it to
touch *only* `generated` (junk-one → junk-two) and assert the standalone
"generated changed" finding, which does isolate the coercion bug. Documented
here per the instruction to report what I did, not just what I concluded.

### MINOR D — comment hygiene, commit body

Moved every provenance/history/ruling-date comment in the touched files
(`"task 17b"`, `"(ruled 2026-08-24)"`, `"(author ruling 2026-08-24)"`,
`"round-1 fix"` references) out of source comments and docstrings; the
`5ac70df` commit body carries that history instead. Comments now state only
the constraint the code can't show. Left the pre-existing, unrelated
`# ``published/<project>-...`` (ruled 2026-08-22)` comment at `lints.py:25`
alone (predates this task, not in scope) and kept the `docs/terminology.md`
citation the reviewer said earns its place.

### Gates

`python -m pytest -q`: 1581 passed, 7 skipped. `ruff check
research_vault/ tests/`: clean. `ruff format --check`: clean (one
auto-reformat applied to `tests/test_lints.py`, re-verified after). `mypy
research_vault/`: clean (one fixup needed — `_machine_attested`'s
parameter was briefly annotated `object`, which mypy rejected at
`generated["by"]`; left unannotated, matching `notes._valid_generated`'s own
convention, since this project's mypy config only requires checking
untyped-def *bodies*, not annotating every signature). `echo '{}' | python
hooks/stop_publish_gate.py`: silent, exit 0.

### Deferred (per reviewer's explicit instruction — not touched)

Missing type annotations on `_frontmatter_attestation_outcomes`; the double
frontmatter parse at `lints.py` (candidate parsed once for the witness check,
once for the attestation check); the duplicated `archive-url` parametrization
in `tests/test_archive.py`; duplicate-key evasion (concern 2 from the
original report, confirmed real by the reviewer, routed to the issue tracker
by the reviewer directly).

### Concerns carried forward (unchanged from round 0, still not fixed)

1. Other `notes.MANAGED_FIELDS` keys (`type`, `aliases`, `doi`, `url`,
   `pmid`, `version`, `accessed`) remain outside the guard — the task's own
   parametrization scoped it to five keys.
2. Renamed files skip the per-key check (only the surviving-path loop runs
   it); the rename itself is always flagged wholesale, so coverage isn't
   silently lost, but the specific-key diagnostic is absent for a renamed
   file that also hand-edits a machine-owned key.

(Concerns 1, 2, and 3 from the round-0 report — other MANAGED_FIELDS,
duplicate-key evasion, and forged-attestation scope — are being routed to
the issue tracker by the reviewer per their message; not re-litigated here.)

## Round 2 (fix round, review feedback on 5ac70df)

### Status

Complete. All four items (N1-N4) addressed. Full suite green, form gate
silent/exit 0, ruff and mypy clean.

### Commit

(this round's commit — see final message to controller for the hash; forward
fix, `5ac70df` and everything before it left untouched, no rebase). Pathspec
includes this report file per the new process rule.

### Test summary

`python -m pytest -q`: **1605 passed, 7 skipped** (was 1581/7; +24 new tests
— 1 in `test_lints.py` for N2, 17 in `test_notes.py` and 6 in
`test_frontmatter.py` for N4). `ruff check`/`ruff format --check` clean,
`mypy research_vault/` clean, form gate silent/exit 0.

### N1 — the disarmed test, re-armed

`test_managed_change_always_yields_typed_evidence_finding_with_fresh_witness`
now collects every UNMATCHED finding for the expected target (not just the
first one `next()` finds) and asserts the *exact* expected reason for each
`change` parameter is among them, instead of asserting only that some
finding's reason starts with `"drift"`. The `edit` case now legitimately
carries two same-target findings (`"drift — managed literature region
changed"` from the pre-existing check, `"drift — managed-sha256 changed
without writer attestation"` from this task's own check, since the test's
witness refresh changes `managed-sha256` without a `generated` bump) — pinning
the exact reason means the second finding can no longer stand in for the
first if the managed-region comparison itself regresses.

**Mutation reproduced, matching the review's numbers:** flipped
`lints.py`'s `if old != new:` (the managed-region comparison) to `if old ==
new:`. Result: 1 failed (`[edit]`), 3 passed (`add`/`delete`/`rename`,
unaffected since they use different code paths). Reverted; all 4 pass again.

**ERRATUM (round 3): the paragraph above is wrong on two counts, and this
round's commit body states the correction — `5ac70df`'s test fix is not
being amended, only this record.** I named the wrong mutant, and the number
I attributed to it was wrong too:

- The reviewer's original finding (round 2's coordinator message) used a
  full neuter of the check — `if old != new:` replaced with `if False:` —
  not the `!=`→`==` operator flip I actually ran. That same message said the
  operator flip is caught elsewhere in the suite ("the `!=`→`==` operator
  mutant it generates is still killed (9 failures)"), which I did not
  register at the time.
- Verified in isolated scratch trees (`git archive <sha> | tar -x`,
  `PYTHONPATH=.`, import-path canary confirmed before each run): at
  `cf3b17c` (pre-N1-fix), the `if False:` neuter survives — **0 failed,
  1581 passed**, matching the review's original number exactly. At
  `1441e7f` (this task's N1 fix), the same neuter is killed — **1 failed
  (`[edit]`), 3 passed**. Separately, the `!=`→`==` flip I actually ran does
  **not** give "0 failed" at `cf3b17c` as I claimed — verified in the same
  scratch tree, it gives **3 failed / 1 passed** (`delete`/`edit`/`rename`
  fail; `add` passes), because it manufactures a false-positive "region
  changed" finding on `gone2019.md` (the fixture's other, untouched
  literature file) whose target sorts ahead of the expected one for those
  three parameters — a different failure mechanism entirely, unrelated to
  the masking phenomenon N1 is about.

Net: the fix itself (re-arming with pinned exact reasons, filtered by target)
is correct and independently re-verified by the reviewer against the mutant
that actually matters. Only my account of *which* mutation I ran, and what
its numbers were at the unfixed commit, was wrong.

### N2 — Minor C's other half: unparseable base no longer auto-attests

Root cause: `attested` was computed as `generated_changed and
_machine_attested(candidate_generated)` with no reference to whether the
*base* was even readable. When base is unparseable (`base_data is None`),
`_field(base_data, "generated")` returns `None`, so any real candidate value
made `generated_changed` true — and if that candidate `generated` happened to
be validly machine-shaped (the ordinary, unremarkable case), `attested` came
out `True` and legalized every other machine-owned key's change with it. Not
forgery (the boundary this check explicitly declines to catch) — just an
unreadable prior state being read as consent.

Fix: `attested` now requires `base_data is not None` outright. Added
`test_unparseable_base_frontmatter_does_not_auto_attest_via_a_valid_candidate`
(base malformed via an injected `nested maps unsupported` line, candidate is
the pristine, untouched, validly-attested note) — confirmed RED (`[]`, zero
findings) against the code as `5ac70df` left it, GREEN after this fix.
Findings on the fixed path: exactly 3 (`citekey`, `fixity-sha256`,
`managed-sha256` — well under the review's observed 5-per-file bound), no
`generated`-itself finding, since `generated`'s own shape genuinely is valid
machine-class — only its power to legalize *other* keys is what an unreadable
base must revoke. This is now honestly "fail-closed": the commit body doesn't
need correcting because the behavior now matches what `5ac70df`'s commit body
claimed.

### N3 — the inline-dict emitter, down to one spelling

`frontmatter.py` had two: `render_field`'s dict branch and `serialize`'s
list-of-dicts branch. Extracted `_render_inline_mapping(mapping) -> str`
(returns just the `{...}` — no leading `key: `), used by both. Verified
byte-identical output via `test_frontmatter.py`'s existing round-trip tests
plus two new direct ones (below).

### N4 — direct tests for the shape contract

Added, none of which existed before this round:
- `tests/test_notes.py`: `test_valid_generated_rejects_every_malformed_shape`
  (14 parametrized cases covering every branch of `notes._valid_generated`:
  non-dict, wrong item count, wrong key names, missing `by`/`at`, empty
  `by`, non-string `by`/`at`, unparseable `at`, `at` with a `+00:00` offset
  instead of `Z`, date-only `at`) and
  `test_valid_generated_accepts_the_one_true_shape`; two tests for
  `notes.generated_at_now` (output satisfies `_valid_generated`; explicit
  `now` truncates microseconds and renders `Z`).
- `tests/test_frontmatter.py`: four direct `render_field` tests (scalar, int
  scalar, one-level mapping, round-trip through `parse`) plus two more —
  one pinning that `serialize`'s own line matches a standalone `render_field`
  call for the same key/value, one pinning that `render_field`'s mapping
  output matches a list-item rendering of the same mapping. **Correction
  (round 3, N5): the first of those two does not "prove the one-spelling
  property"** as this report originally claimed — `serialize` calls
  `render_field` directly for a dict-valued key, so it pins call-site
  agreement on code that already shares one path, not independent agreement
  between two paths that could have diverged. Renamed to
  `test_serialize_delegates_to_render_field_for_a_dict_valued_key` and its
  docstring corrected to say so. The second test (list-item comparison) is
  unaffected by this correction — it compares two syntactically different
  renderings (a `key: {...}` field line and a `  - {...}` list line) of the
  same mapping, which is a real, checkable invariant regardless of shared
  implementation.

**Discrimination, checked by mutation, with one iteration recorded
honestly:** my first probe — dropping just the `{key...} != {"by", "at"}`
clause from `_valid_generated` — turned out not to be a real mutant at all:
every case in my parametrization that used wrong/missing keys still got
rejected downstream by the `isinstance(actor, str)` / `isinstance(at, str)`
checks, because `.get()` on a missing key returns `None`. No test failed
because there was nothing to discriminate — the two code paths are
behaviorally equivalent for every case I had. That distrust turned up a real
gap in the parametrization, not a false negative in the test: I hadn't
covered a dict with exactly two keys, *neither* of which is `by`/`at`. Added
`{"by": "research_vault/0.1.0", "when": "...Z"}` (id `wrong-key-names`) —
still didn't discriminate that specific clause (same reason: `.get("at")` is
`None` either way), but a *second*, genuinely behavior-changing mutation
(dropping the `at.endswith("Z")` requirement, keeping only the tzinfo check)
was caught cleanly by the `at-offset-not-z` case: 1 failed, 15 passed.
Reverted; all 16 pass again. Net effect: the keyset-equality clause in
`_valid_generated` is logically redundant with the subsequent type checks
for every input I could construct — recorded as a concern below rather than
"fixed," since removing it isn't in scope and it costs nothing to leave.
(Round 3 amendment below: the *other* half of that same `if` — `len(items)
!= 2` — is not redundant at all, and this paragraph's silence on that point
was itself the defect N7 named. See the amended concern 4.)

### Concerns — each with a destination

1. **Other `notes.MANAGED_FIELDS` keys stay outside the guard**
   (`type`, `aliases`, `doi`, `url`, `pmid`, `version`, `accessed`) — the
   task's own five-key parametrization scoped it this way. **Destination:**
   controller files as a GitHub issue at plan close (per the controller's
   standing instruction on this round's concerns).
2. **Duplicate-key evasion** — a duplicated machine-owned frontmatter key
   whose last copy matches base evades the value comparison (last-key-wins
   parsing); only `managed-sha256` has an independent duplicate guard via
   the witness check. **Destination:** controller files as a GitHub issue at
   plan close.
3. **Renamed files skip the per-key diagnostic** — the rename-pairing path
   never reaches the per-key loop, so a rename that also hand-edits a
   machine-owned key gets the wholesale "note renamed" finding but no
   per-key reason. **Destination:** controller files as a GitHub issue at
   plan close.
4. **AMENDED (round 3): `_valid_generated`'s guard clause is
   `len(items) != 2 or {key for key, _ in items} != {"by", "at"}` — its two
   sub-clauses are NOT equally redundant, and my original wording did not
   say so.** Only the second sub-clause (`{key...} != {"by", "at"}`) is
   redundant with the function's later `isinstance(actor, str)`/
   `isinstance(at, str)` checks — verified by brute force independently by
   the reviewer (15,901 inputs, 0 divergences from dropping it alone). The
   first sub-clause, `len(items) != 2`, is load-bearing and is the SOLE
   rejecter of a duplicate-`by` forgery: `generated: {by: "human:eran", by:
   "research_vault/0.1.0", at: "2026-08-24T00:00:00Z"}` parses to 3 items
   whose unique key set is still exactly `{by, at}` (so the keyset check
   alone would accept it), and `.get("by")` is last-value-wins, so it reads
   the machine actor and ignores that a forged decoy preceded it — only the
   item-count check catches this shape (reviewer-verified: dropping
   `len(items) != 2` alone gives 144 divergences and survives the full
   suite). **Destination:** declining to remove the keyset-equality
   sub-clause specifically (still redundant, still costs nothing to keep,
   still documents the two-key shape for a reader); the item-count
   sub-clause is NOT a candidate for removal at all. The blind spot — no
   test exercised the duplicate-`by` shape — is closed this round:
   `tests/test_notes.py`'s `test_valid_generated_rejects_every_malformed_shape`
   gained a `duplicate-by-last-wins` case built from an actual parsed
   `_DuplicateKeyMapping` (not a Python dict literal, which would silently
   collapse the duplicate key at parse time and never exercise the shape at
   all), verified to fail if `len(items) != 2` is dropped (1 failed, 16
   passed) and to pass at head.

## Round 3 (fix round, review feedback on 1441e7f)

### Status

Complete. N5, N6, N7, N8 all addressed. Full suite green, form gate
silent/exit 0, ruff and mypy clean.

### Commit

(this round's commit — see the coordinator reply for the hash; forward fix,
`1441e7f` and everything before it left untouched, no rebase). Pathspec
includes this report file; `progress.md` and `review-*.diff` excluded per
the coordinator's instruction.

### Test summary

`python -m pytest -q`: **1606 passed, 7 skipped** (was 1605/7; +1 —
`duplicate-by-last-wins` added to `_valid_generated`'s rejection
parametrization for N7). `ruff check`/`ruff format --check` clean, `mypy
research_vault/` clean, form gate silent/exit 0.

### N6 — the same defect class, reintroduced in the commit that fixed N1

`test_unparseable_base_frontmatter_does_not_auto_attest_via_a_valid_candidate`
filtered on `item.target` only, with no `Result` filter and no reason
pinned — exactly the loose-assertion shape N1 was about, in the very test
written to prove N2. Fixed: now collects the *set* of reasons for
`Result.UNMATCHED` findings on the target and asserts it equals exactly
`{"drift — citekey changed without writer attestation", "drift —
fixity-sha256 changed without writer attestation", "drift — managed-sha256
changed without writer attestation"}`.

**Proven by suppression, not assumed:** temporarily made
`_frontmatter_attestation_outcomes` return `[]` unconditionally (in place,
reverted immediately after) — the test failed with `assert set() == {...}`,
confirming it would have gone red had the four-key outcomes vanished
entirely, which is exactly what N6 asked to demonstrate. Reverted; test
passes again.

**Destination for the pattern itself:** the coordinator identified this as
the third instance of one shape (loose target-only or prefix-only
assertions masking a vanished finding) and stated it is tracked as
**GitHub issue #22**. Per the coordinator's instruction, this round does not
open a new issue for it; the three pinned reason strings above are the
comment payload for issue #22, not a new tracker entry.

### N7 — concern 4's decline was true as scoped, but worded so a future
reader could delete the wrong line

Amended concern 4 (see the amended entry above, in the round-2 section) to
state precisely which sub-clause of `_valid_generated`'s combined `if
len(items) != 2 or {key for key, _ in items} != {"by", "at"}:` is redundant
(the keyset-equality half — reviewer-confirmed 0 divergences across 15,901
brute-forced inputs) and which is load-bearing (the item-count half — sole
rejecter of a duplicate-`by` forgery, 144 divergences, and that mutant
survived the full suite before this round).

Added the `duplicate-by-last-wins` case to
`test_valid_generated_rejects_every_malformed_shape`, built by actually
parsing `'generated: {by: "human:eran", by: "research_vault/0.1.0", at:
"2026-08-24T00:00:00Z"}'` through `frontmatter.parse` (not a Python dict
literal — a literal with a repeated key silently collapses to the last value
at the language level and would never exercise the `_DuplicateKeyMapping`
shape this case needs). Verified: dropping `len(items) != 2` from
`_valid_generated` — leaving only the keyset check — makes this new case
fail (1 failed, 16 passed); reverted, all 16 pass.

### N8 — the N1 mutation account was wrong; corrected in place with an
erratum, not by rewriting history

See the `ERRATUM (round 3)` block inserted directly after the original N1
mutation paragraph in the round-2 section above for the full correction. In
short: I ran and reported the `!=`→`==` operator flip, but the review's
actual mutant was a full `if False:` neuter, and the operator flip's
before-number I cited (0 failed at the pre-fix commit) was also wrong — the
operator flip actually fails 3 of 4 parameters there, for an unrelated
reason (a false-positive finding on the fixture's other literature file).
Both numbers were re-verified empirically in isolated scratch trees
(`git archive <sha> | tar -x -C /tmp/<name>`, `PYTHONPATH=.`, import-path
canary confirmed before trusting each result) rather than asserted from
memory:
- `if False:` neuter at `cf3b17c`: 0 failed, 1581 passed (full suite) —
  matches the review's original number.
- `if False:` neuter at `1441e7f`: 1 failed (`[edit]`), 3 passed — matches
  "KILLED... (1 failed)".
- `!=`→`==` flip at `cf3b17c` (what I actually ran in round 2): 3 failed
  (`delete`/`edit`/`rename`), 1 passed (`add`) — not "0 failed" as I wrote.

The underlying fix (N1's re-arming) was never in question; only my account
of which mutant I ran and its numbers was wrong. This correction lives here
and in this round's commit body rather than as an amendment to `5ac70df` or
`1441e7f`, both reviewed records.

### N5 — an overclaiming test, renamed and corrected

See the `Correction (round 3, N5)` note inserted into the round-2 N4 section
above. `test_render_field_matches_serialize_for_the_same_key_and_value`
claimed to prove render_field/serialize "must never drift apart into two
different formats," but `serialize`'s non-list branch calls `render_field`
directly — there are not two independent formats to diverge, only one
call site to agree with itself. Renamed to
`test_serialize_delegates_to_render_field_for_a_dict_valued_key` with a
docstring stating exactly that: it pins call-site agreement, not
independent-path equivalence.

### Concerns — each with a destination (round 3 additions/amendments only;
see round 1/2 sections above for the full carried-forward list)

- Concern 4 (`_valid_generated`'s keyset-equality clause) — **amended, not
  new** — see the round-2 Concerns section for the corrected text
  distinguishing the redundant sub-clause from the load-bearing one.
  Destination unchanged: declining to remove the redundant sub-clause; the
  load-bearing sub-clause is not a removal candidate.
- The loose-target-only/prefix-only assertion pattern (N1, and now N6) —
  **destination: GitHub issue #22** (per the coordinator; not a new issue).
  The three exact reason strings N6 pinned are this round's contribution to
  that issue's comment thread, not a new tracker entry.
