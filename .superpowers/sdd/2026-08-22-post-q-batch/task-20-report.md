# Task 20 report — additive `relation.is-retracted-by` read

Status: **complete**. Commit: `feat: read Crossref relation.is-retracted-by as an additive retraction signal` (see `git log -1` on this branch after landing).

## What changed

`knowledge_harness/checks.py:_crossref_notices` (~line 546) now reads
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
a saved copy) and re-running the full 14-test set green before moving on.

| # | Test | Targets | Red under | Failure observed |
|---|------|---------|-----------|-------------------|
| 1 | `test_crossref_notices_reads_relation_is_retracted_by_with_no_updated_by` | the entire relation-reading addition | reverting to pre-task code (Step 2) | `blocking == []` instead of the one relation notice |
| 2 | `test_crossref_notices_relation_retraction_does_not_double_count_updated_by_retraction` | the `if not already_retracted:` guard | guard replaced with `if True:` | `blocking` has 2 items (dup) instead of 1 |
| 3 | `test_crossref_notices_relation_retraction_adds_alongside_updated_by_withdrawal` | same-type-only scope of `already_retracted` (ruling a) | `already_retracted = bool(blocking)` (any-type) | relation retraction missing from `blocking` — only the withdrawal survives |
| 4 | `test_active_blocking_notices_undated_relation_retraction_survives_reinstatement` | the `notice["notice_date"] is None or` clause in `_active_blocking_notices` (ruling b) | clause replaced with `False or` | `TypeError: object of type 'NoneType' has no len()` inside `_dates_incomparable` — the guard is load-bearing, not incidental |
| 5 | `test_crossref_notices_ignores_malformed_relation_entries_without_erasing_updated_by` (9 parametrized cases) | three guards: `isinstance(relation, dict)`, `isinstance(retracted_by, list)`, entry/id validity | see below | see below |
| 6 | `test_update_notice_relation_only_retraction_blocks_without_leaking_internal_keys` | `_blocking_outcome`'s explicit `extra` construction (fact 5) | added `"source": notice.get("source")` to `extra` | assertion fails: extra dict has an unexpected `source` key |

Row 5 detail — the 9 parametrized cases are `[]`, `"bad"`, `7`
(non-dict `relation`), `{"is-retracted-by": {}}`,
`{"is-retracted-by": "bad"}` (non-list `is-retracted-by`),
`{"is-retracted-by": ["not-a-dict"]}` (non-dict entry),
`{"is-retracted-by": [{"id-type": "doi"}]}` (missing `id`),
`{"id": 7, ...}` (non-string `id`), `{"id": "", ...}` (empty `id`).
Three separate reverts were run against this parametrized set:

- **Drop the `isinstance(relation, dict)` guard** (call `relation.get(...)`
  unconditionally): cases 0–2 (`[]`, `"bad"`, `7`) go red —
  `AttributeError`/similar, since a non-dict `relation` can't be
  `.get()`-ed. Cases 3–8 stay green.
- **Drop the entry/id validity guard** (`isinstance(entry, dict) and
  isinstance(entry.get("id"), str) and entry["id"]`): cases 5–8 go red
  (case 5 raises `TypeError: string indices must be integers`; 6–8 add a
  spurious notice with a wrong/missing/empty id, so `blocking` no longer
  equals `[{"type": "withdrawal", ...}]`). Cases 0–4 stay green.
- **Drop the `isinstance(retracted_by, list)` guard**: only cases 0–2 go
  red (`retracted_by` is `None` when `relation` itself isn't a dict, and
  `for entry in None` raises `TypeError`). Cases 3–4 stay **green** even
  with this guard removed — not a gap in the test, but guard redundancy:
  case 3's `{}` iterates to zero entries either way, and case 4's `"bad"`
  string iterates to characters that the still-present entry/id guard
  rejects. So case 3 has no single-guard red condition (both guards must
  be absent simultaneously, which was not additionally tested), and case
  4's red condition is the conjunction of the list-guard and entry-guard
  removals, not the list-guard alone. Recorded here rather than glossed
  over, per the brief's instruction against assertions "satisfied by a
  different outcome" — this is the reverse case: a passing test whose
  red-condition is narrower than "any one guard removed."

## Full-suite verification

- `python -m pytest -q`: **1701 passed, 7 skipped** (baseline 1687 passed
  / 7 skipped + 14 new tests = 1701; exact match).
- `ruff check knowledge_harness/checks.py tests/test_checks.py`: clean.
  `ruff check .` (whole repo) reports 10 pre-existing errors, all in
  `skills/find-sources/scripts/paginate.py` — confirmed pre-existing by
  `git stash && ruff check . | tail && git stash pop` (identical 10 errors
  with this diff stashed out). Untouched; out of this task's scope.
- `ruff format --check` on the two changed files: clean after running
  `ruff format` once (two lines needed wrapping — a `retracted_by = (...)`
  assignment and one over-long test dict key — no semantic change).
- `mypy knowledge_harness/`: `Success: no issues found in 27 source files`.
- `echo '{}' | python hooks/stop_publish_gate.py`: silent, exit 0.

## Concerns (each with a destination)

1. **`mutation-baseline.txt` and `knowledge_harness/checks.py.manifest.json`
   are now stale.** Same situation commit `7b28dd8` recorded for its own
   `checks.py` diff: "Task 24 Step 4 owns the regenerate-or-record
   convention and this task's brief has no such step." Deferred here on
   the same precedent — not regenerated, not touched.
2. **Pre-existing `ruff check` failures in
   `skills/find-sources/scripts/paginate.py`** (10 errors: unused `noqa`,
   `B904`, `FURB188`, an import-from-`collections.abc` suggestion, etc.).
   Confirmed pre-existing (present with this diff stashed out) and outside
   `knowledge_harness/`. Explicit recorded decline: out of this task's
   scope, not fixed here. No GitHub issue filed — flagging in this report
   is the disposition; escalate separately if it should block something.
3. **Loose-prefix-assertion pattern**: not reintroduced by this diff (all
   new assertions in the matrix above are exact-equality on full notice
   dicts, not prefix/non-empty checks) — no new instance to file. Existing
   instances remain tracked on GitHub issue #22, unchanged by this task.

## Test summary (one line, for the caller)

1701 passed, 7 skipped (baseline 1687 + 14 new relation-retraction tests); ruff/ruff-format/mypy/stop_publish_gate all clean.
