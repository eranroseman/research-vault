# Task 20 report — additive `relation.is-retracted-by` read

Disposition: historical (2026-09-06)

Status: **complete**, fix round 1 of 5 addressed. Commits:
`39bf192` (`feat: read Crossref relation.is-retracted-by as an additive
retraction signal`) plus a follow-up fix-forward commit for this round
(see `git log` on this branch; `39bf192` was not amended, per
instruction).

## Fix round 1 — coordinator findings and disposition

Both verdicts (spec, quality) were **PASS**. Four items landed, all
fix-forward, no amend of `39bf192`:

1. **MAJOR — a `break` after the first relation append left all 147
   tests green**, because nothing exercised more than one well-formed
   relation entry. Added
   `test_crossref_notices_relation_multiple_entries_each_append_their_own_notice`
   (two entries, distinct ids, no `updated-by` at all → two blocking
   notices, asserted by their exact ids). Reproduced the coordinator's
   canary myself: injected the same `break` after the append, ran the
   full relation-test set — exactly this one new test went red (16
   others stayed green), then restored byte-identical (`diff` confirmed).
   See matrix row 7.
2. **MEDIUM — the report's "guard redundancy" claim was a wrong
   diagnosis, corrected below** (see the rewritten Row 5 detail). The
   list-normalization guard (`isinstance(retracted_by, list)`) is
   load-bearing, not redundant: removing it alone raises an uncaught
   `TypeError` for any non-iterable `is-retracted-by` value (`7`, `None`,
   `True`), before the entry/id guard is ever reached to filter anything.
   My original 9-case parametrize set's only two non-list shapes (`{}`
   and `"bad"`) happened to both be iterable, which is why removing that
   guard alone didn't turn them red — an artifact of the test set, not
   evidence the guard was unnecessary. Reproduced the coordinator's own
   probe and got identical output (see below). **The fix was a test
   case, not a guard deletion** — no production guard was removed.
3. **MEDIUM — two parametrize cases added**: `{"is-retracted-by": 7}`
   (non-iterable — isolates the list guard on its own, the gap the
   original 9 lacked) and `{"has-preprint": [...]}` (`relation` present,
   `is-retracted-by` key absent — the commonest real Crossref shape,
   previously untested). Both pass; both leave the `updated-by`
   withdrawal verdict intact, as required.
4. **MINOR — trimmed the dedup comment** at (then) `checks.py:579-581`
   from three lines (one of which restated the code line beneath it) to
   the single why-clause: "A withdrawal and a retraction are distinct
   signals, so the weaker must not mask the stronger."

Upheld with no action (per coordinator): `already_retracted` computed
before the loop; ruling (a) verified six ways; ruling (b)'s docstring
sentence and its placement on `_crossref_notices`; no `source`/`id`
leakage anywhere in the module. Recorded with no action: a dated
withdrawal plus a relation retraction reports `"retracted — withdrawal"`
with the relation retraction never surfacing in `extra` — the block
itself is never lost, which is the additive promise working as
intended, not a defect.

## What changed

`research_vault/checks.py:_crossref_notices` (~line 546) now reads
`message.get("relation", {}).get("is-retracted-by", [])` after the
existing `updated-by` loop. Each well-formed entry
(`isinstance(entry, dict) and isinstance(entry.get("id"), str) and
entry["id"]` — the same guard shape `_notice_target` already uses,
`checks.py:505-508`) appends `{"type": "retraction", "notice_date": None,
"source": "relation", "id": entry["id"]}` to `blocking`, **unless** an
`updated-by` notice of type `"retraction"` is already present (dedup is
same-type only — a `withdrawal` does not suppress a relation retraction).

Deliberate asymmetry from the controller's fact 1: the pre-existing
`updated-by` loop bails the *whole function* (`return None`) on any
malformed entry — that's the file's established fail-closed idiom, and it
is intentionally **not** repeated here. A malformed relation entry (bad
`relation` shape, bad `is-retracted-by` shape, non-dict entry, missing/
non-string/empty `id`) is skipped, never a reason to discard an
`updated-by` verdict already established. Additive means "may only add
signal, never take it away" — returning `None` from a bad relation entry
would do the opposite of that.

No changes to `_effective_blocking` or `_active_blocking_notices`: the
additive promise ("a relation notice never outranks a dated `updated-by`
notice") is already enforced by `_effective_blocking`'s `max()` key, since
`notice_date=None` sorts lowest. The undated-permanence behavior ("an
undated notice is never auto-cleared by a reinstatement") already exists
in `_active_blocking_notices` for *any* undated notice, relation-sourced or
not — this task only states that fact for relation notices specifically,
in `_crossref_notices`'s docstring, and pins it with a test (see matrix
below).

No change to `_blocking_outcome`: it builds `extra` explicitly from
`notice["type"]` and `notice["notice_date"]` only, so the new `"source"`
and `"id"` keys on the notice dict never reach the `Outcome` or the inbox.
Verified by an end-to-end test (row 6 below) that asserts the exact
`extra` dict for a relation-only retraction contains no `source`/`id` key.

### Docstring placement (recorded decision, not asked)

The brief's fact 3(b) says the required sentence goes in "the check's
docstring" without naming a function. I placed it in
`_crossref_notices`'s docstring rather than `check_update_notice`'s: the
brief's Files section scopes this task to `_crossref_notices`
specifically, and that is the function that manufactures the undated
relation notices — the most direct place to state the constraint their
existence creates. `check_update_notice`'s own docstring is unchanged.

## Per-test discrimination matrix

TDD Step 1/2: `test_crossref_notices_reads_relation_is_retracted_by_with_no_updated_by`
was written and run *before* any production change. It failed for the
right reason — `blocking == []` (not an exception, not `None`) — because
before this task only `updated-by` was read; the `relation` key was never
consulted. Confirmed by running the test against the pre-implementation
code.

For every test below, "red under" was verified by making the named
production edit, running the specific test, observing the failure, then
restoring the original line (confirmed byte-identical via `diff` against
a saved copy) and re-running the full relation-test set green before
moving on.

| # | Test | Targets | Red under | Failure observed |
|---|------|---------|-----------|-------------------|
| 1 | `test_crossref_notices_reads_relation_is_retracted_by_with_no_updated_by` | the entire relation-reading addition | reverting to pre-task code (Step 2) | `blocking == []` instead of the one relation notice |
| 2 | `test_crossref_notices_relation_retraction_does_not_double_count_updated_by_retraction` | the `if not already_retracted:` guard | guard replaced with `if True:` | `blocking` has 2 items (dup) instead of 1 |
| 3 | `test_crossref_notices_relation_retraction_adds_alongside_updated_by_withdrawal` | same-type-only scope of `already_retracted` (ruling a) | `already_retracted = bool(blocking)` (any-type) | relation retraction missing from `blocking` — only the withdrawal survives |
| 4 | `test_active_blocking_notices_undated_relation_retraction_survives_reinstatement` | the `notice["notice_date"] is None or` clause in `_active_blocking_notices` (ruling b) | clause replaced with `False or` | `TypeError: object of type 'NoneType' has no len()` inside `_dates_incomparable` — the guard is load-bearing, not incidental |
| 5 | `test_crossref_notices_ignores_malformed_relation_entries_without_erasing_updated_by` (11 parametrized cases, round 1 added 2) | three guards: `isinstance(relation, dict)`, `isinstance(retracted_by, list)`, entry/id validity | see below | see below |
| 6 | `test_update_notice_relation_only_retraction_blocks_without_leaking_internal_keys` | `_blocking_outcome`'s explicit `extra` construction (fact 5) | added `"source": notice.get("source")` to `extra` | assertion fails: extra dict has an unexpected `source` key |
| 7 | `test_crossref_notices_relation_multiple_entries_each_append_their_own_notice` (round 1) | the append actually running to completion over every entry, not just the first | `break` injected immediately after the `blocking.append(...)` call inside the loop | `blocking` has 1 item (`10.1/first` only) instead of 2 — `10.1/second` missing. Reproduced the coordinator's own canary: with the `break` in place, the other 16 relation tests stayed green and only this one went red |

Row 5 detail, **corrected in round 1** — the original diagnosis here was
wrong and has been replaced. The 11 parametrized cases (9 original + 2
added in round 1) are: `[]`, `"bad"`, `7` (non-dict `relation`);
`{"is-retracted-by": {}}`, `{"is-retracted-by": "bad"}`,
`{"is-retracted-by": 7}` (non-list `is-retracted-by`, the `7` case added
in round 1); `{"is-retracted-by": ["not-a-dict"]}` (non-dict entry);
`{"is-retracted-by": [{"id-type": "doi"}]}` (missing `id`),
`{"id": 7, ...}` (non-string `id`), `{"id": "", ...}` (empty `id`); and
`{"has-preprint": [...]}` (added in round 1 — `relation` present,
`is-retracted-by` key absent, the commonest real Crossref shape).

- **Drop the `isinstance(relation, dict)` guard**: the three non-dict
  `relation` cases (`[]`, `"bad"`, `7`) go red — a non-dict can't be
  `.get()`-ed. The rest stay green.
- **Drop the entry/id validity guard**: the non-dict-entry, missing-id,
  non-string-id, and empty-id cases go red (`TypeError` or a spurious
  notice with a wrong/missing/empty id polluting `blocking`). The rest
  stay green.
- **Drop the `isinstance(retracted_by, list)` guard** — *original claim
  under this revert was wrong; corrected here.* I reported that only the
  non-dict-`relation` cases went red and called `{}`/`"bad"` staying
  green "guard redundancy." That was the wrong diagnosis. Reproducing
  the coordinator's own isolated probe (list guard removed, everything
  else intact, called directly against
  `{"message": {"relation": {"is-retracted-by": <value>}}}`) gives:
  `7 -> TypeError: 'int' object is not iterable`,
  `None -> TypeError: 'NoneType' object is not iterable`,
  `True -> TypeError: 'bool' object is not iterable`,
  `"bad" -> ([], [])`, `{} -> ([], [])`. Iteration raises **before** the
  entry/id guard is ever reached for any non-iterable value — the entry
  guard cannot cover that failure mode at all, so it does not make the
  list guard redundant. The reason my original two non-list cases
  (`{}`, `"bad"`) didn't go red under this single-guard revert is that
  both happen to be *iterable* (an empty dict iterates to nothing; a
  string iterates to characters, which the entry guard then filters) —
  an artifact of which two shapes I picked, not evidence the guard does
  no work. Round 1's new `{"is-retracted-by": 7}` case closes exactly
  this gap: it is non-list *and* non-iterable, so it isolates the list
  guard and goes red under this revert on its own. What removing the
  guard would have cost in production: a malformed `is-retracted-by`
  shaped as an int/`None`/bool would raise an **uncaught `TypeError` out
  of `_crossref_notices`**, propagating past `check_update_notice` (which
  only catches `webapi.ApiError`) — worse than either fail-open (silently
  MATCHED) or fail-closed (UNREACHABLE), because it is neither; it would
  crash whatever called the check instead of returning any Outcome at
  all. The guard was not touched.

## Full-suite verification

Round 0 (initial landing, commit `39bf192`):
- `python -m pytest -q`: **1701 passed, 7 skipped** (baseline 1687 passed
  / 7 skipped + 14 new tests = 1701; exact match).
- `ruff check research_vault/checks.py tests/test_checks.py`: clean.
  `ruff check .` (whole repo) reports 10 pre-existing errors, all in
  `skills/find-sources/scripts/paginate.py` — confirmed pre-existing by
  `git stash && ruff check . | tail && git stash pop` (identical 10 errors
  with this diff stashed out). Untouched; out of this task's scope.
- `ruff format --check` on the two changed files: clean after running
  `ruff format` once (two lines needed wrapping — a `retracted_by = (...)`
  assignment and one over-long test dict key — no semantic change).
- `mypy research_vault/`: `Success: no issues found in 27 source files`.
- `echo '{}' | python hooks/stop_publish_gate.py`: silent, exit 0.

Round 1 (this fix-forward commit, 3 new tests: 1 multi-entry + 2
parametrize cases):
- `python -m pytest -q`: **1704 passed, 7 skipped** (1701 + 3; exact
  match).
- `ruff check research_vault/checks.py tests/test_checks.py`: clean.
  `ruff check .` still reports the same 10 pre-existing errors in
  `skills/find-sources/scripts/paginate.py` — unchanged, confirmed no new
  errors introduced.
- `ruff format --check` on the two changed files: clean.
- `mypy research_vault/`: `Success: no issues found in 27 source files`.
- `echo '{}' | python hooks/stop_publish_gate.py`: silent, exit 0.

## Concerns (each with a destination)

1. **`mutation-baseline.txt` and `research_vault/checks.py.manifest.json`
   are now stale.** Same situation commit `7b28dd8` recorded for its own
   `checks.py` diff: "Task 24 Step 4 owns the regenerate-or-record
   convention and this task's brief has no such step." Deferred here on
   the same precedent — not regenerated, not touched.
2. **Pre-existing `ruff check` failures in
   `skills/find-sources/scripts/paginate.py`** (10 errors: unused `noqa`,
   `B904`, `FURB188`, an import-from-`collections.abc` suggestion, etc.).
   Confirmed pre-existing (present with this diff stashed out) and outside
   `research_vault/`. Explicit recorded decline: out of this task's
   scope, not fixed here. No GitHub issue filed — flagging in this report
   is the disposition; escalate separately if it should block something.
3. **Loose-prefix-assertion pattern**: not reintroduced by this diff (all
   new assertions in the matrix above are exact-equality on full notice
   dicts, not prefix/non-empty checks) — no new instance to file. Existing
   instances remain tracked on GitHub issue #22, unchanged by this task.

## Test summary (one line, for the caller)

1704 passed, 7 skipped (baseline 1687 + 17 relation-retraction tests, 14 round-0 + 3 round-1); ruff/ruff-format/mypy/stop_publish_gate all clean.
