# Task 9 review - e76805c..acd38b5

Disposition: historical (2026-09-06)

## Spec Compliance

**Verdict: compliant.**

The brief asked for one thing: SKIPPED review-queue results stay recorded and stay
visible in listings, but stop contributing to the unacknowledged count and the
oldest-age basis on every drain surface. The change delivers exactly that, in one
comprehension inside `summary()` (`research_vault/inbox.py:718-720`), with both
returned keys derived from the same filtered list.

The brief's "every drain surface" clause is satisfied by construction rather than by
edits elsewhere, and I confirmed the surface map independently. A repo-wide grep for
callers of `summary(` and `open_entries(` in `research_vault/` returns exactly:
`__main__.py:761` (the `inbox` verb's printed JSON summary), `__main__.py:763` (the
listing, which reads `open_entries()` and therefore still shows SKIPPED rows),
`scaffold.py:295` (the doctor inbox probe, which reads `status["unacknowledged"]` and
`status["oldest"]` at `scaffold.py:298-304`), and `verify.py:850` (`_file_effects`'s
dedup key set, deliberately untouched). There is no other unacknowledged arithmetic in
the package, and `inbox.py:723` is the only age-basis computation.

The filter is total, not a spelling gamble. `Finding.result` is a plain `str`
(`inbox.py:121`); `load()` rejects any row whose `result` is not in `Result.__members__`
(`inbox.py:542`); and `Result` (`outcome.py:16-20`) is a str-valued enum whose member
names equal their values, so `entry.result != Result.SKIPPED.value` cannot miss a
variant.

Commit hygiene matches the brief: one commit, subject verbatim
(`fix: SKIPPED findings recorded but never counted unacknowledged`).

No spec issues found.

### Cannot verify from diff

Three of the four items the lenses raised I resolved directly; one remains for the
controller.

**Still open — the pre-commit form gate at 8/8.** The report claims
`PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` passes all eight
hooks. I did not run it: the formatter hooks rewrite files, and this review is
read-only. The controller should run it and confirm the eight hook lines.

**Resolved — offline suite green and output pristine.** I ran
`.venv/bin/python -m pytest tests -q -p no:cacheprovider` against the reviewed tree:
`1572 passed, 7 skipped in 90.45s`, matching the report exactly, with no
`warnings summary` block in the output. `git status --porcelain` was clean before and
after the run.

**Resolved — the rubber-stamp rationale lives in the commit body.**
`git show -s --format=%B acd38b5` carries it: "counting it toward 'unacknowledged'
manufactures rubber-stamp pressure on whoever drains the queue", together with the
surface map, the `open_entries()` hazard and why it stays unfiltered, the
"no existing test pinned the old behaviour" note, RED/GREEN commands with counts, and
the non-rename ruling. This is the house comment doctrine applied correctly
(plan Q, `docs/superpowers/plans/2026-08-20-plan-q-quality-lane.md:51`): the shipped
docstring states only the mechanical constraint, and the argument sits in git log.

**Resolved — the orientation skills read the count, not the rows.**
`skills/project-flow/SKILL.md:25` and `skills/publish/SKILL.md:25` both say "report the
unacknowledged count and the oldest entry's date" immediately after invoking
`python3 -m research_vault inbox --vault PATH`, whose first printed line is
`json.dumps(inbox.summary(...))` with keys `unacknowledged` and `oldest`
(`__main__.py:761`). The naming maps one-to-one, and `project-flow/SKILL.md:27`
explicitly teaches that SKIPPED findings appear in that queue's listing, so the
listing-shows-SKIPPED / count-excludes-SKIPPED split is the taught behaviour rather
than a contradiction. The publish gate's separate blocking-class count is unaffected
either way: it keys off reason code `retracted`, and SKIPPED rows carry
`no-identifier`.

**Moot — the hazard test's pre-fix baseline.** The report claims the dedup test passed
before the implementation change. That history is not in the diff, but the fidelity
lens established something stronger: with `inbox.open_entries` monkeypatched to drop
SKIPPED, the test goes red, and a standalone reproduction showed the red is backed by a
genuinely duplicated row (1 row unmutated, 2 rows mutated). The guard discriminates,
which is what the baseline claim was evidence for.

## Strengths

The hazard the brief named is guarded rather than merely avoided. Filtering SKIPPED out
of `open_entries()` instead of `summary()` would have poisoned `_file_effects`'s dedup
key set (`verify.py:850-862`) and re-filed a duplicate finding on every verify run into
an append-only queue. The implementer put the filter in `summary()`, stated that
constraint in the docstring where a future simplifier will meet it
(`inbox.py:713-716`), and pinned it with a permanent regression test
(`tests/test_verify_cli.py:1163-1183`) that verification proved goes red under exactly
that mutation.

The RED phase is real. The reported failure is a value mismatch on the committed test's
first assertion (`{'unacknowledged': 1, 'oldest': '2026-08-01'}` against
`{'unacknowledged': 0, 'oldest': None}`) — the shape of the defect itself, not a
fixture or collection error.

The mixed-queue case is built to catch a half-fix. The SKIPPED entry is dated
2026-08-01 and the UNMATCHED entry 2026-08-16, so an implementation that excluded
SKIPPED from the count but left it in the age basis would fail on `oldest`.

The change is minimal and correctly placed: one comprehension, no new function, flag, or
parameter, and every counting consumer inherits it without an edit to `scaffold.py` or
`__main__.py`. The report's surface map matched independent greps exactly — nothing
missed, nothing fabricated.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

None.

### Minor (Nice to Have)

**1. `tests/test_inbox.py:890` — comments restate the assertions beneath them.**
Three of the new test's comments narrate what the following assert already says:
"Mixed queue: the SKIPPED entry still contributes neither to the count nor to the
oldest-age basis, so both derive from the UNMATCHED entry alone" (890-892),
"SKIPPED entries stay in the audit trail and in full listings — only the counting
surface excludes them" (898-899), and the opening clause of 877. The house doctrine
(plan Q line 51) is that a comment earns its place by carrying what the code cannot
show; restatements rot when the assertions change and cost reading time for no
information. Fix: keep the two clauses that carry non-obvious facts — the contract
semantics ("SKIPPED means 'does not apply', not 'needs a human decision'") and the
fixture constraint that the SKIPPED entry is deliberately dated earlier than the
UNMATCHED one, which is what makes the `oldest` assertion discriminating — and drop the
rest. *Status: NOT-VERIFIED-MINOR.* Raised independently by the quality and fidelity
lenses at the same line; merged here, keeping the broader statement.

**2. `tests/test_verify_cli.py:1163` — the dedup guard has no positive control.**
The test asserts only that no duplicate was filed; nothing shows that `_file_effects`
would have filed this outcome into an empty vault at all, so it cannot distinguish
"dedup suppressed the filing" from "nothing would have been filed anyway". It
discriminates today, because SKIPPED passes the `if outcome.result is not Result.MATCHED`
gate at `verify.py:864` and a key mismatch would append a second row — but a future
refactor that stops filing SKIPPED outcomes entirely would vacate the guard while
leaving it green. Fix: call `_file_effects` with the same outcome against a vault with
no pre-filed entry and assert exactly one entry lands. *Status: NOT-VERIFIED-MINOR.*
Kept separate from issue 3: a load-based assertion does not close this hole, since a
stop-filing-SKIPPED refactor leaves the single pre-filed row in place either way.

**3. `tests/test_verify_cli.py:1181` — the guard asserts through the function it
guards.** The only assertion reads `inbox.open_entries()`, the very call whose behaviour
the test protects, so under the mutation it exists to catch it fails with
`[] == ['metadata/...']` rather than exposing the duplicate row. The test still goes red
(verified), but the failure message points at the reader instead of the consequence, so
a maintainer meeting that red will diagnose "open_entries changed" rather than "verify
re-filed a duplicate on every run" — the fact the test's own docstring promises to
demonstrate. Fix: assert against the unfiltered `inbox.load(tmp_vault)` instead of, or
in addition to, `open_entries`. *Status: NOT-VERIFIED-MINOR.*

## Refuted During Verification

No finding was refuted. All three lens findings survived adversarial verification, and
no lens raised a Critical or Important finding to be knocked down. Nothing was dropped
from the ledger.

One observation was deliberately *not* promoted to a finding: the `inbox` verb now
prints a summary that excludes SKIPPED above a listing that includes it, so a queue of
three rows can print `"unacknowledged": 1`. That is the ruled behaviour
(`docs/2026-08-22-slice-findings.md:38`: recording SKIPPED is fine, counting it is the
defect), and `skills/project-flow/SKILL.md:27` already teaches the reader that SKIPPED
findings appear in the queue.

## Assessment

**Task quality: Approved.**

The one-line fix is correct, total, and placed where it does not break verify's dedup —
the single real hazard in this change — and the guard against that hazard was proven to
discriminate rather than merely to pass. The three surviving findings are Minor test-
hygiene items in the new tests; none blocks, and the only open verification item is the
pre-commit form gate, which the controller can close in one command.
