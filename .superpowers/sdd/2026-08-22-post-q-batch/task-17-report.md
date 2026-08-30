# Task 17 report: the "unresolved" placeholder never anchors acknowledgments

Commit: `213a826 fix: unresolved attachments omit fixity entries; ack scope never anchors to a placeholder`

## Side (a) — `__main__.py` stops writing the placeholder

**RED.** Flipped the existing pinning test (it asserted the defect, not a
regression guard):

```
tests/test_cli_live.py::test_import_note_unresolved_attachment_and_normalized_annotation
```

Before: `assert data["fixity-sha256"] == ["unresolved"]`.
After: `assert data["fixity-sha256"] == []`.

Ran it against the unfixed source — failed for the predicted reason on all
four parametrized attachment shapes:

```
AssertionError: assert ['unresolved'] == []
```

**Implementation.** Deleted `hashes.append("unresolved")` at
`research_vault/__main__.py:234`, keeping the `print(f"warning: attachment
unresolved: {error}", ...)` line immediately above it, and leaving
`degradation_reasons.append("attachment unresolved")` (a separate record,
~line 254) untouched.

**GREEN.** All four parametrizations pass; the stderr-warning assertion
(pinned elsewhere) stays green.

**Two more tests turned out to pin the same defect indirectly** — they seeded
a "prior note" fixture with `notes.render_note(..., ["unresolved"], ...)` to
make a fresh `cmd_import_note` call a no-op (byte-identical re-render):

- `tests/test_cli_live.py::test_import_note_identical_projection_is_noop`
- `tests/test_cli_live.py::test_import_note_preserves_prior_selectors_when_contexts_degrade`

Both used an attachment with `path: None` (permanently unresolved), so after
side (a)'s fix a fresh render now produces `fixity-sha256: []`, not
`["unresolved"]` — the seeded "prior" note no longer matched, breaking the
no-op assertion. Fixed by seeding `[]` instead of `["unresolved"]`, matching
the new honest output.

## Side (b) — `verify.py` stops adopting the placeholder, both branches

`_citekey_hash` has two structurally identical adoption sites:

- `verify.py:212` (originally) — `candidate_snapshot is not None` branch
- `verify.py:224` (originally) — live-file (`note.is_file()`) branch, reached
  when `candidate_snapshot` defaults to `None`

**RED — two new tests, one per branch:**

```
tests/test_verify_cli.py::test_ack_hash_rejects_placeholder_fixity_live_file
tests/test_verify_cli.py::test_ack_hash_rejects_placeholder_fixity_candidate_snapshot
```

- `..._live_file` calls `_target_hash(net_vault, claim_outcome)` with no
  `candidate_snapshot` kwarg — reaches `_citekey_hash`'s `candidate_snapshot
  is None` branch (`note.is_file()`).
- `..._candidate_snapshot` builds `gitstate.snapshot_worktree(net_vault)` and
  passes it explicitly as `candidate_snapshot=` — reaches the
  `candidate_snapshot is not None` branch.

Both seed `smith2020.md`'s `fixity-sha256` with `["unresolved"]` and assert
the resulting hash is not `"unresolved"` and equals the managed-bytes
fallback (`hashlib.sha256(_note_bytes(...)).hexdigest()[:16]`).

Ran against the unfixed source — both failed identically:

```
AssertionError: assert 'unresolved' != 'unresolved'
```

**Implementation — guarded inline at both sites, not factored.** Changed
`if isinstance(first, str) and first:` to
`if isinstance(first, str) and re.fullmatch(r"[0-9a-f]{64}", first):` at both
`verify.py:213` and `verify.py:225`. `re` was already imported. Chose to
guard twice rather than factor into a helper: the two call sites already
differ in how `raw`/`data` is obtained (snapshot image vs. live file read),
so factoring would only extract the four-line adoption check itself — a
small win in line count that costs the 1:1 mapping between "site" and
"discrimination test" the task explicitly asked for. Inline keeps the
revert-one-site experiment (below) a single-line edit per site.

**GREEN.** Both new tests pass.

**Discrimination demonstration.** Reverted each site's guard individually
(temporarily, not committed) and reran both tests:

- Reverting only the snapshot-branch guard (line 213) → only
  `test_ack_hash_rejects_placeholder_fixity_candidate_snapshot` goes red
  (`assert 'unresolved' != 'unresolved'`); the live-file test stays green.
- Restored, then reverted only the live-file-branch guard (line 225) → only
  `test_ack_hash_rejects_placeholder_fixity_live_file` goes red; the
  snapshot test stays green.

Confirms each test reaches exactly the site it's named for, and neither
guard is redundant with the other.

## Fixture fallout (the real complication)

`notes.sha256_file()` (the only production writer of `fixity-sha256`) always
emits a full 64-hex-character digest. The shared `net_vault`/`fixture_vault`
test fixture (`tests/conftest.py`) used `"aa11"` as shorthand for "a real
hash" — 4 characters, valid hex, but not a digest shape production could ever
produce. Applying the brief's literal digest-shape regex
(`[0-9a-f]{64}`) correctly rejects `"aa11"` as malformed, which broke every
test that expected `_citekey_hash`/`_target_hash` to adopt it verbatim.

Consulted the advisor before proceeding past this discovery; the guidance
(implement the brief's exact regex, migrate the fixture rather than
weaken the guard, since a looser "any-length hex" check would still let a
hand-edited `"aa"` anchor an ack — exactly the class of constant-anchoring
this task closes) matched the shape-vs-security tradeoff I'd found, so I
followed it.

Migrated `"aa11"` → `"aa11" * 16` (64 hex chars) and `"bb22"` → `"bb22" * 16`
everywhere the value is read back through `_citekey_hash` (i.e. derived from
`smith2020.md`'s live/candidate content): `tests/conftest.py:46`, and in
`tests/test_verify_cli.py`: the note-mutation `.replace(...)` calls that
change or strip smith2020's fixity value, and the assertions that compare a
computed hash against the literal. Confirmed via a full run of
`tests/test_verify_cli.py` + `tests/test_cli_live.py` before and after each
batch of edits — six tests failed after the conftest fixture change alone,
all six traced to fixity-derived hash comparisons, none needed weakening the
guard. Six tests fixed:

- `test_ack_suppresses_effects_but_retains_raw_outcome_and_reopens_on_hash`
  (note-content mutation from `aa11`→`bb22`)
- `test_target_hash_routes_safe_file_claim_citekey_and_staleness` (three
  `== "aa11"` assertions)
- `test_acknowledged_matched_warn_mints_event_without_refiling_or_printing`
  (ack literal had to match the live-computed hash to suppress refiling)
- `test_correction_ack_does_not_suppress_same_hash_blocking_retraction`
  (`blocker.target_hash == warning.target_hash == "aa11"`)
- the two new side-(b) tests themselves, whose own `.replace('  - "aa11"',
  ...)` calls no longer matched the widened fixture text

Left every other `"aa11"` literal in `test_verify_cli.py` unchanged — these
are independent inbox/ack scaffolding (`target_hash="aa11"` passed directly
to `inbox.append_entry`/`append_ack`, or fake `{id(x): "aa11"}` hash maps
fed to code that never re-derives the hash from the note) that never round
trips through `_citekey_hash`. The full suite run confirms none of them
depend on the fixture's shape.

## Verification

- Full offline suite: `1566 passed, 7 skipped` (baseline 1564 passed + 2 new
  tests = 1566; skip count unchanged).
- Form gate: 8/8 (`ruff format` reformatted one file on the first pass —
  line-wrapped the 64-char literals — then 8/8 clean on rerun).
- Single commit, conventional format, working tree clean afterward.

## Self-review

- **Real digests still adopt the first one?** Yes — the regex matches any
  64-lowercase-hex string, exactly `notes.sha256_file()`'s output shape.
  Confirmed by every passing test still asserting adoption of the (now
  64-char) `"aa11"`/`"bb22"` fixture values.
- **Empty or absent `fixity-sha256` still falls through to the managed-bytes
  hash?** Yes — `gone2019.md` (no `fixity-sha256` key at all) and the
  several `test_no_fixity_*` / `test_no_attachment_hash_*` tests that strip
  the key entirely all pass unchanged.
- **Degradation reason still records when an attachment fails?** Yes —
  `degradation_reasons.append("attachment unresolved")` at `__main__.py`
  (~line 254) was not touched, and
  `test_import_note_reports_unresolved_attachment_in_mixed_extraction`
  (stderr assertion) passes unchanged.

## Concerns

None blocking. One judgment call worth flagging: the fixture migration
(`"aa11"` → 64 chars) touches more lines than the two source-file deltas the
brief anticipated. I verified empirically (full-suite run, twice, before
committing) that the migration is exactly as wide as it needs to be — no
broader than the set of tests that actually read `_citekey_hash`'s output —
and that no test's *assertion intent* changed, only the literal shape of the
placeholder hash value it depends on.

Task 17b (frontmatter joins the closing guard, `lints.py`) is a separate
brief section and was not in scope for this task per the parent instructions
naming "Task 17" specifically; not started.

## Fix round 1 (review response)

Commit: `7374ebd fix: Task 17 review round 1 — migrate a stale ack-hash literal, pin the digest-length bound, cover the empty-fixity fallthrough`
(follow-up on top of `213a826`, nothing amended, nothing rebased).

### Finding 1 (confirmed, important) — stale short literal disarmed a test

`tests/test_verify_cli.py::test_matching_outcome_still_mints_event_after_same_hash_ack`
still seeded `target_hash="aa11"` (4 chars) and acked with `"aa11"` while
the `net_vault` fixture's real fixity had already widened to `"aa11" * 16`
in the prior commit. Fixed both literals to `"aa11" * 16`.

**Verification, reproducing the coordinator's method exactly:** temporarily
injected a "MATCHED-suppression" fault — removed the unconditional
`outcome.result is Result.MATCHED or` clause from `_effective`, and changed
`_apply_state_transitions(vault, authoritative, ...)` to
`_apply_state_transitions(vault, effective, ...)` in `verify_state` — so a
MATCHED outcome whose prior UNMATCHED entry is (same-hash) acknowledged no
longer mints its verified event.

- With the migrated (64-char) literals + fault: test FAILS
  (`assert False` — no `doi` verified event minted). Confirms the migrated
  test now catches the fault.
- Reverted only the two literals back to the 4-char `"aa11"` (fault still
  injected): test PASSES. Confirms the pre-fix state was blind — the hash
  mismatch made `is_acknowledged` False, which coincidentally exempted the
  outcome from the fault's suppression, masking the regression entirely.
- Restored `verify.py` to clean (`git diff` empty) and re-applied the
  literal migration before committing. The fault was never committed.

### Finding 2 (minor) — length bound now pinned

Parametrized both `test_ack_hash_rejects_placeholder_fixity_live_file` and
`test_ack_hash_rejects_placeholder_fixity_candidate_snapshot` over
`["unresolved", "aa11"]`. `"unresolved"` fails the guard's character class;
`"aa11"` is valid hex but fails the `{64}` length bound — so together they
pin both halves of the digest-shape check, not just hex-ness.

**Verification:** relaxed the guard regex to `[0-9a-f]+` (both sites,
temporarily) and reran — the `"aa11"` parametrization went red on both
tests (`assert 'aa11' != 'aa11'` fails, since the relaxed regex now adopts
the short hex string) while `"unresolved"` stayed green. Restored the
strict `{64}` regex (`git diff` on `verify.py` empty at that point) before
moving to the next finding.

### Finding 3 (minor) — empty-list fallthrough now covered

Added `test_ack_hash_falls_through_when_fixity_is_empty_list`, which sets
`smith2020.md`'s frontmatter to `fixity-sha256:` with no list items
(parses to `[]` — the exact shape side (a) now produces when every
attachment fails to resolve) and asserts both `_citekey_hash` branches
(no `candidate_snapshot`, and an explicit `gitstate.snapshot_worktree`
snapshot) fall through to the managed-bytes hash.

**Verification:** temporarily dropped the `and attachment_hashes`
truthiness check at both adoption sites (`if isinstance(attachment_hashes,
list):` alone) — the test failed with `IndexError: list index out of
range` on the live-file branch, correctly proving the test would catch a
regression that tried to index into an empty list instead of falling
through. Reverted (`git diff` empty) before committing.

### Finding 4 (minor) — docstrings corrected

`_claim_anchor_hash` and `_identifier_hash` docstrings described fixity
adoption as unconditional ("wins where the note declares one" / "recorded
fixity first"). Reworded both to state the actual constraint: a note's
fixity only wins when it is validly digest-shaped; an absent, empty, or
malformed value is treated as though nothing were declared. No
provenance/history language added, per the doctrine at
`docs/superpowers/plans/2026-08-24-plan-w-quality-tail.md:39`.

### Verification after all four fixes

- `.venv/bin/python -m pytest tests -q` → `1569 passed, 7 skipped`
  (1566 at `213a826` + 3 new parametrizations/tests: +1 param each on the
  two placeholder tests, +1 new empty-list test).
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` → 8/8
  (ruff-format reformatted one file on first pass, clean on rerun).
- Working tree clean after commit; no amend, no rebase — `7374ebd` sits on
  top of `213a826`.

### Deferred items (not addressed, per coordinator instruction)

- Three-way spelling of the 64-char digest literal (drift hazard) — noted
  as recorded/deferred by the coordinator, not touched.
- `mutation-baseline.txt:130` stale survivor key — noted as inert/deferred
  by the coordinator, not touched.
