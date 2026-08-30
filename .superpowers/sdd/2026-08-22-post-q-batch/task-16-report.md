# Task 16 report: no vacuous machine-confirmed tier

## RED evidence

Added the brief's two tests to `tests/test_events.py` (after `test_trust_tier_progression`,
before `test_human_event_alone_is_not_human_reviewed`) and ran them in isolation before
touching `events.py`:

```
$ .venv/bin/python -m pytest tests/test_events.py -k "test_no_identifier_no_claims_note_is_unverified or test_frontmatterless_text_is_unverified" -q
FF
=================================== FAILURES ===================================
_______________ test_no_identifier_no_claims_note_is_unverified ________________
    assert events.trust_tier(text) == "unverified"
E   AssertionError: assert 'machine-confirmed' == 'unverified'
___________________ test_frontmatterless_text_is_unverified ____________________
    assert events.trust_tier("just some text\n") == "unverified"
E   AssertionError: assert 'machine-confirmed' == 'unverified'
2 failed, 37 deselected in 0.09s
```

Both failed for the predicted reason — the empty-applicable-set / frontmatterless note derives
`"machine-confirmed"` at HEAD, not a fixture or collection error.

## Implementation

`research_vault/events.py::trust_tier` — added the checkability floor after the existing
`machine_confirmed` computation (mirrors the brief's Step 3 exactly, adapted to the code as it
actually stands):

```python
checks = {str(event.get("check", "")) for event in events}
applicable = _applicable_note_checks(data)
machine_confirmed = applicable <= checks
...
has_managed_quotes = False
for claim in claims_mod.parse_claims(note_text):
    if claim.tag != "quote" or not claim.in_managed or not claim.claim_id:
        continue
    has_managed_quotes = True
    ...
if not applicable and not has_managed_quotes:
    # A subset test over an empty applicable set is vacuously true; require
    # at least one deterministic check to have run and matched instead.
    machine_confirmed = False
```

**Reused the existing `parse_claims` loop** (the one at the old `:267`, now unchanged in
position): `has_managed_quotes = True` is set inside that loop, immediately after the
continue-guard, for every claim that is a managed quote with a claim id — regardless of
whether its checks currently match. No second `parse_claims(note_text)` call was added.

**`_applicable_note_checks(data)` is now called exactly once** instead of twice. HEAD called it
at the old `:255` (`machine_confirmed = _applicable_note_checks(data) <= checks`) and again at
the old `:258` (`applicable_failures = _applicable_note_checks(data)`). I hoisted the result into
a single `applicable` variable, used for both the initial subset test and the failure-row loop
(replacing the misleadingly-named `applicable_failures`), and reused again for the new floor
check — a net *reduction* in calls, satisfying "do not make it three."

## GREEN evidence

```
$ .venv/bin/python -m pytest tests/test_events.py -q
.......................................                                  [100%]
39 passed in 0.08s

$ .venv/bin/python -m pytest tests -q
...
1561 passed, 7 skipped in 69.23s (0:01:09)
```

Baseline at BASE (ded3cdf) was 1559 passed, 7 skipped. 1561 = 1559 + the 2 new tests. Skip count
unchanged.

## Consequence sweep — every test that touches `trust_tier`

Ran `grep -n "trust_tier(" tests/*.py` and inspected every hit's fixture for whether the
applicable-check set is empty and whether it carries a managed quote claim:

- `tests/test_events.py` — all `machine-confirmed`/`human-reviewed` assertions use `BASE`
  (has `doi:` → applicable = `{doi, metadata, update-notice}`, plus a managed quote claim
  `^c-11111111`) or `PMID_ONLY` (has `pmid:` → applicable = `{update-notice}`). Neither fixture
  has an empty applicable set with no managed quotes.
- `tests/test_notes.py` — all `trust_tier` assertions expect `"unverified"` already (malformed /
  duplicate-header fixtures); unaffected by the floor regardless of applicable-set size.
- `tests/test_verify_cli.py:1350,1518,1535` — uses `net_vault`'s `smith2020.md` fixture (has
  `doi:`); the `machine-confirmed` assertion at `:1535` follows all three note-level checks plus
  the managed quote check passing. Not vacuous.
- `tests/test_trust_tier_cli.py` — uses `PMID_ONLY` (has `pmid:`, applicable =
  `{update-notice}`). Not vacuous.
- `tests/test_project_flow_skill.py:82`, `tests/test_templates.py:300` — string/doc assertions
  about the tier *names* appearing in prose, not `trust_tier()` calls; unaffected.

**No test in the suite pinned the vacuous tier.** Every existing `"machine-confirmed"` or
`"human-reviewed"` assertion in the repo was already backed by a real, non-empty applicable set
(a `doi` or `pmid` field) or a genuine managed quote claim with a matching passing check. The
defect existed in the *code path*, but nothing in the test suite exercised the vacuous case
before this task's two new tests — so Step 5's "fix any test that pinned the vacuous tier" had
no work to do; confirmed by full-suite green with zero test-file edits beyond the two additions.

## Spec amendment

`docs/superpowers/specs/2026-08-16-foundation-spec.md:88`, "Event integrity" paragraph — appended
the brief's sentence verbatim after the existing "Machine-confirmed trust requires..." sentence,
before "Deterministic gate surfaces alone write these events...":

> An item with no applicable note-level checks and no managed quote claims derives `unverified`
> — the machine tiers require at least one deterministic check to have run and matched, never
> vacuous satisfaction (closed 2026-08-22, audit defect 3).

Only this paragraph was touched; the "Invariants" (never-delete) paragraph two lines below,
reserved for another task in this plan, is untouched.

## Issue #17 scope note

`task-16-brief.md`'s title also claims this task "closes issue #17" (human-reviewed
unreachable in production — `verify.py:797` and `publish.py:368` never pass `by="human:..."` to
`record_pass`). I read the issue. Its own text says the two defects are "distinct" and merely
"best fixed in the same pass," and its fix would require a new CLI surface (a way for a human to
mint a `human:` verified event) — a change well outside the brief's Step 1-5 delta, the parent
task's "Surfaces, verified by me" list (which names only `events.py`), and the single commit
subject `fix: trust tier requires evidence — no vacuous machine-confirmed`. I did not add a CLI
verb. What this task does provide toward #17: confirmation, via the full sweep above and the
self-review below, that `human-reviewed` remains reachable through `trust_tier` given a real
`human:` event (unaffected by the floor) — i.e., the *derivation* logic issue #17 examined is
correct; only the production *minting* surface is missing, and that stays open. Referenced #17 in
the commit body as a scope note, not a closure claim.

## Self-review

1. **Does a note that genuinely passes its applicable checks still reach machine-confirmed?**
   Yes — `test_trust_tier_progression`, `test_pmid_only_requires_update_notice_coverage`,
   `test_source_text_quote_coverage_is_machine_confirmed`, and the `net_vault` CLI test all still
   assert `"machine-confirmed"` and pass unchanged.
2. **Does human-reviewed still require its `human:` event?** Yes —
   `test_human_event_alone_is_not_human_reviewed` (a `human:` event with no applicable checks
   passing) still asserts `"unverified"`, and `test_trust_tier_progression` still reaches
   `"human-reviewed"` only after a `human:` event on top of full machine evidence.
3. **Is a note with quote claims but no note-level checks still eligible — floor is
   `has_applicable OR has_managed_quotes`, not AND?** Verified manually (not a suite test, since
   the brief specifies only the two RED tests):
   ```
   $ .venv/bin/python - <<'EOF'
   from research_vault import Result, events
   text = ("---\ncitekey: \"noid2020\"\ntype: \"literature\"\n---\n"
           "%%rv-managed%%\n- (quote) [@noid2020, p. 1] ^c-11111111\n"
           "  > A quoted sentence.\n%%/rv-managed%%\n")
   print(events.trust_tier(text))                     # unverified — quote check hasn't run
   text2 = events.record_pass(text, "quote:noid2020#^c-11111111:managed-region",
                               Result.MATCHED, at="2026-08-16")
   print(events.trust_tier(text2))                     # machine-confirmed — no doi/pmid needed
   EOF
   unverified
   machine-confirmed
   ```
   Confirms a citekey-only note (no `doi`/`pmid`, so `applicable` is empty) with a managed quote
   claim reaches `machine-confirmed` once its quote check matches — the floor did not add an
   AND requirement on note-level identifiers.

## Concerns

- Issue #17 is referenced but not closed by this task (see scope note above); the GitHub issue
  should stay open pending a CLI-surface fix elsewhere in the plan.
- None regarding the vacuous-tier fix itself: RED confirmed, GREEN confirmed, full suite green,
  form gate 8/8, no test needed correction because none pinned the vacuous case.

## Fix round 1 (coordinator review)

Two findings, both the same shape — behaviour the fix changed that no test pinned, and
`research_vault/events.py` sits in `mutation-exclusions.txt`, so a test is the only backstop.
Both addressed by adding tests to `tests/test_events.py`, each verified by hand to discriminate
the specific mutant it targets.

**Finding 1 — `has_managed_quotes` unpinned.** Deleting that clause from the guard (leaving
`if not applicable:`) regresses every identifier-less note with a verified managed quote to
permanently `unverified`, and the mutant passed the whole suite. Added:

- `test_identifier_less_note_with_matched_quote_is_machine_confirmed` — a citekey-only note (no
  doi/pmid) with a matched managed-quote check reaches `machine-confirmed`.
- `test_identifier_less_note_with_matched_quote_and_human_event_is_human_reviewed` — same note
  plus a `human:` event reaches `human-reviewed`. Extends the OR-not-AND check to the human tier
  too, at the coordinator's "pin both directions if you can do it cleanly."

New fixture `NO_ID_QUOTE` (module level, alongside `BASE`/`PMID_ONLY`): citekey + a managed
`(quote)` claim, no `doi`/`pmid`.

**Finding 2 — the floor also narrows `human-reviewed`, and it's exactly what the brief's "cover
it in this task's tests" clause for #17 asked for.** A `human:` event on an identifier-less,
quote-less note derived `human-reviewed` at BASE (empty applicable set made
`machine_confirmed` vacuously True) and derives `unverified` now. No existing test constructed
that case (a test fixture can write a `human:` event via `record_pass` even though no CLI
surface mints one in production — the derivation is testable, only the minting is not). Added:

- `test_identifier_less_note_with_human_event_and_no_quotes_is_unverified` — a note with only a
  `citekey`, no `doi`/`pmid`, no quote claims, and one `human:` event now asserts `"unverified"`.

### Discrimination evidence (manual mutation testing)

`research_vault/events.py` was temporarily mutated, the targeted tests run, then the file was
restored from a pre-mutation backup (`cp` to `/tmp/events.py.orig` and back — no commit was made
with either mutant in place; `git diff` against the fix confirmed byte-identical restoration
after each round).

**Mutant A — drop the `has_managed_quotes` clause** (`if not applicable and not
has_managed_quotes:` → `if not applicable:`):

```
$ .venv/bin/python -m pytest tests/test_events.py -k "test_identifier_less_note_with_matched_quote_is_machine_confirmed or test_identifier_less_note_with_matched_quote_and_human_event_is_human_reviewed" -q
...
AssertionError: assert 'unverified' == 'machine-confirmed'
...
AssertionError: assert 'unverified' == 'human-reviewed'
2 failed, 40 deselected in 0.06s

$ .venv/bin/python -m pytest tests -q   # full suite under mutant A
2 failed, 1562 passed, 7 skipped in 73.53s
```

Both new tests go red; the other 1562 tests (including all pre-existing `trust_tier` tests)
stay green under this mutant — matching the coordinator's independent reproduction.

**Mutant B — remove the floor entirely** (delete the `if not applicable and not
has_managed_quotes: machine_confirmed = False` block, restoring HEAD's vacuous behaviour):

```
$ .venv/bin/python -m pytest tests/test_events.py -k "test_no_identifier_no_claims_note_is_unverified or test_frontmatterless_text_is_unverified or test_identifier_less_note_with_human_event_and_no_quotes_is_unverified" -q
...
AssertionError: assert 'machine-confirmed' == 'unverified'      # test_no_identifier_no_claims_note_is_unverified
...
AssertionError: assert 'machine-confirmed' == 'unverified'      # test_frontmatterless_text_is_unverified
...
AssertionError: assert 'human-reviewed' == 'unverified'         # test_identifier_less_note_with_human_event_and_no_quotes_is_unverified
3 failed, 39 deselected in 0.07s
```

The third failure is the exact flip the coordinator described: without the floor, the
human:-event-only note derives `human-reviewed` again, and the new test catches it.

### Re-verification after restoring the real fix

```
$ .venv/bin/python -m pytest tests/test_events.py -q
..........................................                               [100%]
42 passed in 0.10s

$ .venv/bin/python -m pytest tests -q
1564 passed, 7 skipped in 71.24s (0:01:11)

$ PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files
8/8 passed (ruff-format reformatted a quote-style/line-wrap nit in the new test on the first
pass; re-run was clean)
```

1564 = 1561 (prior round) + 3 new tests. Skip count unchanged (7).

### Commit

Amended the existing commit (`2c2af7c`, was `0b8ec6c` — branch tip had nothing stacked on top,
per the coordinator, so amend was safe and keeps "one commit for this task"). Commit body
expanded to name each of the five tests in `tests/test_events.py` and what each one pins,
including the mutant each discriminates and the mutation-exclusions.txt context for why tests are
the only backstop here.

### Not addressed (by design, per coordinator)

The plan-text claim that Task 16 "closes issue #17" is being corrected in the plan document
directly — not a code change, not mine to make.
