# Task 17 re-review: fix round 1 (`213a826..7374ebd`)

Disposition: historical (2026-09-06)

Scope: commit `7374ebd` only. `213a826` is accepted and not re-reviewed.

## Method note — scratch-copy incident and repair

The worktree's `.git` is a *pointer file* (`gitdir: /home/eranr/New
folder/.git/worktrees/fix+pre-slice-batch`), not a self-contained
repository. A `cp -r` of the worktree copies that pointer file verbatim, so
the copy still resolves to the **same external gitdir** — its index, HEAD
ref, and refs are shared with the real worktree, even though the working
tree files are independent copies.

While preparing a second scratch copy (`/tmp/khs_base`, materializing
`213a826`'s content for the Finding 1 base leg) I ran
`git checkout 213a826 -- .` inside it. That command updated the *shared*
index (staging `research_vault/verify.py` and `tests/test_verify_cli.py`
at their `213a826` blobs) without touching any working-tree files — but
because the index is shared, this showed up in the **real worktree** as
`git status` reporting `MM` on both files.

Verified before repairing: the real worktree's working-tree file contents
were untouched throughout (`git diff` — index vs. working tree — was
non-empty in the "looks like the fix was just reapplied" direction, i.e.
purely an index artifact; the actual bytes on disk still hashed identically
to `HEAD`). Repaired with `git reset HEAD -- research_vault/verify.py
tests/test_verify_cli.py` (updates the index to match `HEAD`, does not
touch the working tree). Confirmed clean afterward: `git status` →
"nothing to commit, working tree clean"; both `git diff` and
`git diff --cached` empty for the whole repo.

No real-worktree file was ever modified; only the shared index was
transiently mis-staged, and that has been fully restored. All further
experiments were run in `/tmp/khs` after severing its `.git` pointer
(`rm /tmp/khs/.git`), which turns any further stray git command in scratch
into a loud failure instead of a silent cross-contamination. `/tmp/khs_base`
was deleted. Restores of `research_vault/verify.py` inside `/tmp/khs`
were done from a plain file backup (`/tmp/verify.py.orig`, saved from the
untouched checkout) and checked byte-for-byte (`sha256sum`) against the
real worktree's file after each restore, not via git.

## Finding 1 — stale short literal disarmed a same-hash-ack test

**Claim:** `test_matching_outcome_still_mints_event_after_same_hash_ack` was
blind at `213a826` (seeded/acked with 4-char `"aa11"` while the fixture's
real fixity had widened to 64 chars) and is now armed at `7374ebd`
(literals migrated to `"aa11" * 16`).

**Fault injected** (reproducing the coordinator's/implementer's method), in
`research_vault/verify.py`:
1. `_effective()`: dropped the unconditional `outcome.result is
   Result.MATCHED or` clause, leaving only `not inbox.is_acknowledged(...)`
   — so a MATCHED outcome with a same-hash ack is now filtered *out* of
   `effective`.
2. `verify_state()`: changed `_apply_state_transitions(vault, authoritative,
   detection_date)` to `_apply_state_transitions(vault, effective,
   detection_date)` — so `_apply_state_transitions` (the function containing
   the `events.record_pass` / `events.record_failure` ternary at
   `verify.py:797`) now only sees outcomes that survived (1), starving it of
   the acknowledged-MATCHED outcome and suppressing its verified event.

**Result — empirical matrix:**

| Tree state | Test literals | Fault | Outcome |
|---|---|---|---|
| `7374ebd` (HEAD) | `"aa11" * 16` (64 chars) | injected | **FAIL** — `assert False`, no `doi` verified event minted |
| `213a826` (BASE) | `"aa11"` (4 chars) | injected | **PASS** — test is blind |

This is exactly the matrix the task predicted: at BASE the hash mismatch
made `is_acknowledged` `False` for reasons unrelated to the fault, which
coincidentally exempted the outcome from the fault's suppression and masked
the regression; at HEAD the migrated literal makes the ack genuinely
same-hash, so the fault's suppression is caught. **Finding 1 is fixed.**

## Finding 2 — digest-length bound now pinned

**Claim:** the fix parametrizes both placeholder tests over `["unresolved",
"aa11"]`, pinning both the character-class guard and the `{64}` length
bound.

**Experiment 1 — relax both sites.** Changed `re.fullmatch(r"[0-9a-f]{64}",
first)` to `re.fullmatch(r"[0-9a-f]+", first)` at both adoption sites
(`verify.py:213` and `:225`) and ran `tests/test_verify_cli.py`:

```
FAILED tests/test_verify_cli.py::test_ack_hash_rejects_placeholder_fixity_live_file[aa11]
FAILED tests/test_verify_cli.py::test_ack_hash_rejects_placeholder_fixity_candidate_snapshot[aa11]
2 failed, 84 passed, 1 skipped
```

Exactly the `[aa11]` parametrization fails on both tests; `[unresolved]`
stays green on both, confirming the hex-length bound (not the char class)
is what's being probed. Without the round's fix, this relaxation would have
been invisible — the pre-fix single-case tests only ever seeded
`"unresolved"`.

**Experiment 2 — converse, one site at a time.** Relaxed only line 213
(candidate_snapshot branch): only
`test_ack_hash_rejects_placeholder_fixity_candidate_snapshot[aa11]` failed,
`..._live_file` (all params) stayed green. Relaxed only line 225 (live-file
branch): only `..._live_file[aa11]` failed, `..._candidate_snapshot` stayed
green. Each test still reaches exactly its own site with no cross-coverage
gap. **Finding 2 is fixed**, and the per-site discrimination from Task 17's
original implementation still holds after parametrization.

## Finding 3 — empty-list fallthrough now covered

**Claim:** `test_ack_hash_falls_through_when_fixity_is_empty_list` exercises
a present-but-empty `fixity-sha256: []`, not an absent key, and covers both
`_citekey_hash` branches.

**Shape check.** The project's frontmatter parser
(`research_vault/frontmatter.py:134`) is a hand-rolled flat-schema
parser, not PyYAML: a key line with nothing after the colon explicitly sets
`current_list = []` (line 159-161), i.e. a bare `fixity-sha256:` line
parses to a **present key with value `[]`**, not `None` and not a missing
key. Verified directly:

```python
>>> frontmatter.parse('---\nfixity-sha256:\n---\nbody\n')[0]
{'fixity-sha256': []}
```

**Replacement actually fires.** Ran the test's exact `.replace(...)` call
against the real `net_vault` fixture text from `tests/conftest.py:39-51`
(the target string
`'fixity-sha256:\n  - "aa11...aa11"\n'` matches byte-for-byte) — confirmed
`replaced != original` and that the parsed post-replacement frontmatter has
`'fixity-sha256': []` with `'fixity-sha256' in data` true. Not a vacuous
no-op. (The task's own vacuous-pass concern is also structurally
foreclosed here regardless: a no-op replace would leave the valid 64-hex
digest in place, which the test's `== expected` — expected being the
managed-bytes fallback, not the digest — would then fail. The direct check
above just confirms the mechanism, not merely the outcome.)

**Both branches independently covered.** Faulted the guard by dropping the
`and attachment_hashes` truthiness check (`if isinstance(attachment_hashes,
list) and attachment_hashes:` → `if isinstance(attachment_hashes, list):`):

- Faulting **both** sites: `IndexError: list index out of range` at
  `verify.py:224` (the live-file branch, hit by the test's first
  assertion, which has no `candidate_snapshot`).
- Faulting **only** the candidate_snapshot site (line 211), live-file site
  clean: first assertion passes; second assertion (which passes
  `candidate_snapshot=`) raises `IndexError` at `verify.py:212`. Confirms
  the second assertion genuinely reaches and exercises the
  candidate_snapshot branch, not just re-triggering the first.
- Faulting **only** the live-file site (line 223), candidate_snapshot site
  clean: `IndexError` at `verify.py:224`, symmetric to the both-sites case.

**Finding 3 is fixed** — the test exercises the true `[]`-present shape and
independently pins both `_citekey_hash` branches, matching the report's
claim (which understated this by only demonstrating the combined-fault
case).

## Finding 4 — docstring accuracy

Read the reworded docstrings (`_claim_anchor_hash` at `verify.py:243-253`,
`_identifier_hash` at `verify.py:400-410`) against the actual guard
(`isinstance(first, str) and re.fullmatch(r"[0-9a-f]{64}", first)`) for all
five cases:

| Fixity shape | Guard behavior | Docstring says |
|---|---|---|
| absent key (`.get()` → `None`) | falls through | "no fixity" / "absent" → falls through — accurate |
| empty list | falls through | "an empty list" / "empty" → falls through — accurate |
| non-hex string (`"unresolved"`) | falls through | "doesn't look like a digest" / "not digest-shaped" — accurate |
| short/valid-hex but wrong length (`"aa11"`) | falls through | covered by the same "doesn't look like a digest" / "not digest-shaped" phrasing — accurate, though the length dimension isn't spelled out explicitly |
| valid 64-lowercase-hex | adopted | "a validly-shaped digest" / "digest-shaped" wins — accurate |

**Residual imprecision (new, cosmetic, non-blocking):** the regex is
`[0-9a-f]{64}` — lowercase only. A 64-character **uppercase**-hex string
(e.g. `"AA11" * 16`) fails the guard and falls through, but "validly-shaped
digest" / "digest-shaped" doesn't say case-sensitive, so a reader could
reasonably expect it to be adopted. Confirmed empirically
(`re.fullmatch(r"[0-9a-f]{64}", "AA11"*16)` → `False`,
`re.fullmatch(r"[0-9a-f]{64}", "aa11"*16)` → `True`). In practice this is
inert: the only production writer, `notes.sha256_file()` at
`research_vault/notes.py:333`
(`hashlib.sha256(...).hexdigest()`), always emits lowercase, so no real
digest can ever hit this gap. **Finding 4 is fixed**, with one cosmetic
wording gap not worth a further round.

## New-defect / scope judgment

- **`assert result != placeholder` weaker than the assertion it replaced?**
  No. It is immediately followed by `assert result == expected`, where
  `expected` is a concrete, freshly-computed managed-bytes hash
  (`hashlib.sha256(_note_bytes(source.read_bytes())).hexdigest()[:16]`,
  computed *after* the placeholder write, per parameter). `result ==
  expected` strictly implies `result != placeholder` for both parameter
  values (`expected` is a 16-hex-char truncated digest; neither
  `"unresolved"` nor `"aa11"` can equal it). The `!=` assertion is
  redundant-but-harmless, not a weakening.
- **Is `expected` computed correctly for both parametrized values?** Yes —
  it's recomputed from `source.read_bytes()` after each parameter's write,
  so it reflects the actual post-injection file bytes for `"unresolved"`
  and for `"aa11"` alike. Same for the new empty-list test (computed once,
  after the one `.replace()`, and reused for both branch assertions — valid
  since both branches read the same underlying uncommitted file bytes).
- **Scope creep.** The `verify.py` half of this round is docstring-only (two
  hunks, no logic change — the `re.fullmatch(...)` guard itself was
  untouched, having already landed in `213a826`). The `test_verify_cli.py`
  half touches exactly the three sites the four findings name: the two
  parametrized placeholder tests, the new empty-list test, and the
  `target_hash`/`append_ack` literal fix in
  `test_matching_outcome_still_mints_event_after_same_hash_ack`. No other
  test or production line changed. No scope creep.

## Full suite at HEAD (`7374ebd`)

```
.venv/bin/python -m pytest tests -q -n auto
1569 passed, 7 skipped
```

Matches the report's claimed counts (1566 at `213a826` + 3 new
parametrizations/tests). Re-ran after all scratch-copy fault injections
were reverted and file bytes reconfirmed identical to `HEAD` via
`sha256sum`, so this run reflects the true committed state.

## Verdict

**ALL FINDINGS ADDRESSED.** No new defects in the round's own changes; one
cosmetic (non-blocking) docstring imprecision noted under Finding 4
(uppercase-hex case-sensitivity not spelled out — inert in practice since
production only emits lowercase digests).
