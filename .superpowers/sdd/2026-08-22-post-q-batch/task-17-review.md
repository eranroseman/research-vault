# Task 17 review - 1fd3f8a..213a826

Disposition: historical (2026-09-06)

## Spec Compliance

Verdict: **issues** — one issue, and it is collateral to the fixture migration rather than a
deviation from any enumerated step.

Every step of the brief's Task 17 is verified met:

- Step 1/2 (failing tests, both sides): both sides have a test that pinned the defect. Side (a)
  reused the existing pinning test by flipping its assertion; side (b) added two new tests, one per
  adoption branch.
- Step 3 (side a): `hashes.append("unresolved")` is deleted at `research_vault/__main__.py:233`
  and nothing else in the except block moved. The stderr warning survives immediately above it, and
  the independent `degradation_reasons.append("attachment unresolved")` record at
  `research_vault/__main__.py:254` is untouched — it is driven by `local_path is None`, which the
  deleted line never influenced.
- Step 4 (side b): the brief's regex is present verbatim at both adoption sites,
  `research_vault/verify.py:213` (candidate-snapshot plane) and `research_vault/verify.py:225`
  (live-file plane). `re` was already imported at `research_vault/verify.py:11`. A repo-wide grep
  for `fixity` confirms these are the only two adoption sites in production code.
- Step 5 (commit): ONE commit, subject verbatim from the brief, and a body carrying the per-test
  notes the plan required for all three tests that had pinned the defect.

The issue:

- `tests/test_verify_cli.py:399` — the shared-fixture migration was partial, leaving
  `test_matching_outcome_still_mints_event_after_same_hash_ack` without the same-hash acknowledgment
  its name encodes. Detail under Important below.

### Cannot verify from diff

1. **The RED runs themselves, both sides.** These are pre-commit states no read-only pass can
   re-execute. The reported failure strings do match the mandated reasons
   (`AssertionError: assert ['unresolved'] == []` for side (a);
   `AssertionError: assert 'unresolved' != 'unresolved'` for side (b)), and both are structurally
   forced by the source deltas. For hard proof: in a scratch worktree at 1fd3f8a, apply only the five
   test bodies (the three flipped tests in `tests/test_cli_live.py` plus the two new tests in
   `tests/test_verify_cli.py`), then revert each of the three source deltas
   (`__main__.py:233` append, `verify.py:213`, `verify.py:225`) and confirm each named test fails
   with the message above.
2. **Full offline suite green at 1566 passed / 7 skipped, and the form gate at 8/8.** Two lenses
   verified the +2 accounting structurally — exactly two new `def test_` lines, zero deletions,
   neither parametrized — and ran the two new tests (both pass). Re-run
   `.venv/bin/python -m pytest` and `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files`
   on a clean checkout for a fresh green. Note that the fix for the Important finding touches only
   test literals.
3. **Task 17b (machine-owned frontmatter joins the closing guard, `lints.py`).** Not implemented in
   this diff, which matches the controller's scoping to "Task 17" specifically. Confirm 17b is
   tracked as its own task so the brief's second half is not dropped.
4. **The CI mutation gate on the two changed modules.** Analysis says the new guard's mutants die to
   the new tests (the `and`->`or` mutant returns `"unresolved"` and fails both; a regex-literal
   mutant breaks the adoption assertion at `tests/test_verify_cli.py:243`), but that is reasoning,
   not a run. Watch `quality.yml` or run `python scripts/mutation_gate.py --base 1fd3f8a`, and decide
   whether `mutation-baseline.txt:130` is dropped here or at the next blanket refresh.

Resolved, so not passed through: the per-site discrimination claim (reverting either guard in
isolation turns only that site's test red) was raised as unverifiable by one lens and then settled
empirically by another, which reproduced it in an isolated copy — reverting only
`research_vault/verify.py:213` turns only `test_ack_hash_rejects_placeholder_fixity_candidate_snapshot`
red, reverting only `research_vault/verify.py:225` turns only `..._live_file` red. A third lens
corroborated it independently by line coverage: the live-file test executes
`research_vault/verify.py:216-227` and never 205-215; the snapshot test executes 197-215 and never
216-227. The controller does not need to re-run this.

## Strengths

- **Side (a) is exactly one deleted line.** `research_vault/__main__.py:233` loses only the
  placeholder append. Degradation stays visible on two independent channels — the stderr warning and
  the `degradation_reasons` record — without a fabricated digest, and no arity coupling between
  `hashes` and the attachment list was broken.
- **Both adoption sites are guarded, and neither guard is redundant.** The per-site discrimination
  experiment reproduces exactly, so each new test reaches the plane it is named for. Routing is
  structurally forced: `_claim_anchor_hash` passes `candidate_snapshot=` straight through to
  `_citekey_hash` (`research_vault/verify.py:250-252`), and the two tests differ only in that
  keyword argument.
- **The fixture was migrated rather than the guard loosened, and that was the right call.**
  `_attachment_hash` returns `notes.sha256_file()` = `hashlib.sha256(...).hexdigest()`, always 64
  lowercase hex, so `re.fullmatch(r"[0-9a-f]{64}", first)` can never reject a digest this codebase
  wrote. A looser any-length-hex check would have re-admitted a hand-written `"aa11"` as an ack
  anchor — the exact class of constant-anchoring this task closes.
- **The new tests pin the route, not the negation.** They assert
  `result == hashlib.sha256(_note_bytes(...)).hexdigest()[:16]`, not merely
  `result != "unresolved"`, so they pin the specific fallback inside `_citekey_hash` rather than a
  condition that downstream fallbacks in `_claim_anchor_hash` would also satisfy.
- **Fallback semantics hold across all four shapes.** A real 64-hex digest is still adopted; an empty
  list fails the truthiness test; an absent key yields None and fails the isinstance test; a legacy
  `"unresolved"` now fails the regex. All three reject paths fall through to the managed-bytes hash.
- **The +2 test accounting is genuine, not a net.** Exactly two `def test_` lines added, zero
  deleted, neither parametrized; the `test_cli_live.py` changes are in-place edits to existing tests.
- **Provenance lives in the commit body.** Per-test notes for all three tests that pinned the defect,
  the two-site guard rationale, and the fixture-migration rationale. The only added prose in code is
  two test docstrings naming which branch each test reaches — a constraint the code cannot show.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

**`tests/test_verify_cli.py:399` — the fixture migration silently disarmed
`test_matching_outcome_still_mints_event_after_same_hash_ack`.** Status: **CONFIRMED** (independently
by two lenses, each with its own empirical probe).

What is wrong: the test still seeds `target_hash="aa11"` (line 399) and
`inbox.append_ack(net_vault, entry.id, "manual — checked", "human:test", "aa11")` (line 401), but the
fixity value they have to match widened to 64 hex characters at `tests/conftest.py:46`. The live hash
for a `doi`/`smith2020` outcome is now `"aa11" * 16` — pinned in-file at `tests/test_verify_cli.py:251`
— so the seeded acknowledgment no longer matches and the test no longer sets up the same-hash ack its
name encodes.

Why it matters: the test exists to prove that a MATCHED outcome still mints an event *despite* an
active same-hash acknowledgment. `inbox.is_acknowledged` substitutes the current hash into the entry
and matches acks by hash (`research_vault/inbox.py:692-699`), so with `"aa11" != "aa11" * 16` the
ack is inert and the regression guard is disarmed. The test passes either way, so suite greenness
gives no warning — which is precisely why the implementer's detection method (migrate until the suite
is green) was structurally blind to it. Two independent demonstrations confirm the lost detection: a
probe replicating the setup gives `is_acknowledged == True` at 1fd3f8a and `False` at 213a826; and
under an injected fault that lets an acknowledgment suppress event minting for a MATCHED outcome
(dropping the `outcome.result is Result.MATCHED or` short-circuit at `research_vault/verify.py:757-758`
and feeding `effective` at `research_vault/verify.py:1033`), this test FAILS at base and PASSES at
HEAD. The whole file passes 83/83 under that fault as written, and fails only once lines 399/401 are
migrated. This also falsifies the report's claims that the migration is "exactly as wide as it needs
to be" and that "no test's assertion intent changed, only the literal shape".

How to fix: widen both literals to match the fixture — `target_hash="aa11" * 16` at line 399 and
`inbox.append_ack(net_vault, entry.id, "manual — checked", "human:test", "aa11" * 16)` at line 401 —
matching the treatment already applied to the sibling test at lines 522/526. Verified in an isolated
copy: with that edit the test is green on unmutated HEAD and red again under the injected fault, i.e.
detection is restored.

Scope of the fix, so the controller does not have to re-audit: this synthesis checked every remaining
short `"aa11"` literal in the file. Lines 475, 501, 703 and 1682 are fake `{id(x): "aa11"}` hash maps
fed to a monkeypatched `verify_state` that never re-derives a hash from the note. Line 1269
(`test_warn_dedup_reconstructs_type_and_inbox_is_oldest_first`) seeds an inbox entry whose hash could
in principle enter a dedup key at `research_vault/verify.py:855-870`, but that arm cannot fire in
this test: it runs `run_verify(..., network=False)`, and `_offline_network_outcomes`
(`research_vault/verify.py:687-703`) emits only "outage — network disabled" outcomes with no
`warn_notices`, so no warn entry is minted and the literal is inert scaffolding. The fix is exactly
the two literals at 399 and 401.

### Minor (Nice to Have)

All five below are recorded as NOT-VERIFIED-MINOR: their substance was read directly off the code but
none was put through the adversarial verification pass, and none blocks.

**`tests/test_verify_cli.py:276` — the `{64}` length bound has no test.** Both new tests seed the
fixity value with `"unresolved"`, so only the hex-ness of the guard is pinned. Relaxing the regex to
`[0-9a-f]+` would keep the entire suite green while re-admitting a short hand-written constant like
`"aa11"` as an ack anchor — the looser check the report says was deliberately rejected. The length
bound is the discriminator this task's central decision rests on. Fix: parametrize the seeded fixity
value over `["unresolved", "aa11"]` in both new tests; the pre-migration fixture value is exactly the
malformed-but-hex shape that must fall through.

**`tests/test_verify_cli.py:262` — the newly reachable `fixity-sha256: []` shape is unpinned.** Side
(a) makes an empty list the honest output of an all-attachments-failed import, and every such note
will carry it going forward, but existing coverage spans only the absent key (`test_no_fixity_*`,
`gone2019.md`) and the legacy `["unresolved"]` string (the two new tests). The two halves of the
fixity pair meet at `[]` and the joint contract has no test. A manual probe confirms the fallback does
hold (`result == sha256(_note_bytes(...))[:16] == 53cae778a39982ca`), so this is a coverage gap, not a
defect. Fix: one small test beside the two new ones rewriting smith2020's fixity block to
`fixity-sha256: []` and asserting `_target_hash` equals the `_note_bytes` fallback.

**`research_vault/verify.py:243` — docstrings one level up still describe adoption as
unconditional.** `_claim_anchor_hash` says "The citekey's own recorded fixity wins where the note
declares one" (line 243) and `_identifier_anchor_hash` says "recorded fixity first"
(`research_vault/verify.py:400`). Adoption is now shape-conditional: a note declaring a malformed
`fixity-sha256` falls back to the managed-bytes hash. A reader of these docstrings would conclude that
any declared value anchors the ack — the defect this task closed. Fix: say the recorded fixity wins
where the note declares a well-formed digest.

**`tests/test_verify_cli.py:213` — the migrated digest is now spelled three ways.** The expanded
64-character literal appears in the conftest YAML (`tests/conftest.py:46`), again as a raw literal in
seven `.replace(...)` and note-text sites (`tests/test_verify_cli.py:213`, 267, 285, 819, 1004, 1467,
1503), and as `"aa11" * 16` in the assertions (`tests/test_verify_cli.py:243`, 250, 251, 522, 526,
1401). All nine widened literals were checked programmatically and every one is exactly 64 characters,
so this is not a current defect. The hazard is drift: `str.replace` fails silently as a no-op, so a
missed literal after a future fixture change would leave a test like
`test_no_fixity_target_hashes_are_candidate_bound_before_projection` keeping its name while exercising
the with-fixity path, and a 64-character literal is much harder to eyeball than the 4-character one it
replaced. Fix: export `FIXITY_DIGEST = "aa11" * 16` (and its `bb22` counterpart) from
`tests/conftest.py`, interpolate it into the fixture note text, and reference it from both the
mutation literals and the assertions. (This item merges two lenses' reports of the same hazard, the
second anchored at `tests/test_verify_cli.py:819`.)

**`mutation-baseline.txt:130` — a stale survivor entry.** The committed baseline still carries
`research_vault/verify.py::func/_citekey_hash::isinstance(first, str) and first -> isinstance(first, str) or first`,
keyed to the exact source expression this commit deleted from both adoption sites. It is inert for the
gate — `scripts/mutation_gate.py` computes `found - baseline`, and no run can now produce that key —
so it causes neither a false pass nor a false failure. It is inventory drift in a tracked, regenerable
file, and it is obsoleted in the good direction, since the new guard's `and`->`or` mutant is killed by
the two new tests. Fix: drop the line here, or flag it for the next blanket `--update-baseline` run.

## Refuted During Verification

**`research_vault/verify.py:213` — "the adoption guard is now a verbatim six-line block duplicated
across both planes, and this change chose to state the adoption policy twice" (raised Important).**
REFUTED. The finding's load-bearing claim is that the duplication is new; it is not.
`git show 1fd3f8a:research_vault/verify.py` shows the adoption block, including the predicate
`if isinstance(first, str) and first: return first`, already present verbatim at both sites before
this change. I re-ran that check during synthesis and confirmed it directly. The diff swaps exactly
one predicate line per site (`verify.py`: 4 lines changed, 2 deleted / 2 added), which is the minimal
in-place edit of pre-existing structure. The predicted failure — the snapshot plane and the worktree
plane disagreeing about what may anchor an ack after a future shape change — is a pre-existing
property of the function that this commit neither created nor worsened. Extracting a helper may still
be worth doing on its own merits, but it is not a defect of this diff and it does not block.

## Assessment

Task quality: **Needs fixes**.

The two-sided fix itself is clean, minimal and correct — both adoption sites carry the brief's regex
verbatim, the placeholder append is gone without collateral damage to either degradation channel, and
the decision to migrate the fixture rather than weaken the guard is the right one and is defended in
the commit body. The single blocking item is collateral: the fixture migration was one test short, and
because that test passes under both hash values, the gap is invisible to the suite — two literals at
`tests/test_verify_cli.py:399` and `:401` restore a regression guard that is currently disarmed.
