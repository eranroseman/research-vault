# Task 9 report: SKIPPED entries excluded from unacknowledged counts

## RED evidence

Command:

```
.venv/bin/python -m pytest tests/test_inbox.py -k test_skipped_entries_not_counted_unacknowledged -q
```

Output (before the fix):

```
F                                                                        [100%]
=================================== FAILURES ===================================
_______________ test_skipped_entries_not_counted_unacknowledged ________________
...
>       assert inbox.summary(fixture_vault) == {"unacknowledged": 0, "oldest": None}
E       AssertionError: assert {'unacknowled... '2026-08-01'} == {'unacknowled...oldest': None}
E
E         Differing items:
E         {'oldest': '2026-08-01'} != {'oldest': None}
E         {'unacknowledged': 1} != {'unacknowledged': 0}
1 failed, 259 deselected in 0.23s
```

This is the expected failure: a queue holding only one SKIPPED entry (dated
2026-08-01) is counted today as 1 unacknowledged with `oldest` = that entry's
date, when it should count as 0/None. The failure is on the assertion itself
(a value mismatch), not a fixture/setup error — confirming the test exercises
today's defect, not a broken harness.

The companion dedup-hazard test
(`tests/test_verify_cli.py::test_file_effects_does_not_refile_an_already_open_skipped_finding`)
was run *before* any implementation change and **passed** — establishing the
pre-fix baseline that `_file_effects` does not duplicate-file a SKIPPED entry,
so any regression introduced by the fix would show up as a new failure there.

## GREEN evidence

Command:

```
.venv/bin/python -m pytest tests/test_inbox.py tests/test_verify_cli.py -q
```

Output (after the fix):

```
........................................................................ [ 21%]
........................................................................ [ 42%]
........................................................................ [ 63%]
........................................................................ [ 84%]
..........................................s........                      [100%]
338 passed, 1 skipped in 37.46s
```

Full offline suite:

```
.venv/bin/python -m pytest tests -q
```

```
1572 passed, 7 skipped in 90.97s (0:01:30)
```

(Baseline at BASE commit was 1570 passed, 7 skipped; the delta of +2 is
exactly the two new tests added — `test_skipped_entries_not_counted_unacknowledged`
and `test_file_effects_does_not_refile_an_already_open_skipped_finding`. No
test count regressed or was removed.)

Form gate:

```
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files
```

```
form: python (ruff format)...............................................Passed
lint: python (ruff)......................................................Passed
types: python (mypy rung-1)..............................................Passed
form: markdown CommonMark (mdformat).....................................Passed
form: yaml (yamlfix).....................................................Passed
form: toml (pyproject-fmt)...............................................Passed
lint: json canonical + skill frontmatter (suite).........................Passed
records: append-only under research/analysis/adr.........................Passed
```

8/8.

## Surface map — verified against the actual code

Grepped every consumer of `inbox.summary(` and `inbox.open_entries(` in
`knowledge_harness/`:

```
knowledge_harness/verify.py:850:    for entry in inbox.open_entries(vault_root):
knowledge_harness/inbox.py:701:def open_entries(vault) -> list[Finding]:
knowledge_harness/inbox.py:713:    entries = [entry for entry in open_entries(vault) ...]   (was: entries = open_entries(vault))
knowledge_harness/__main__.py:761:    print(json.dumps(inbox.summary(args.vault), sort_keys=True))
knowledge_harness/__main__.py:763:        inbox.open_entries(args.vault), key=lambda item: (item.date, item.id)
knowledge_harness/scaffold.py:295:        status = inbox.summary(vault)
```

This matches the brief's map exactly — no other counting surface exists.
Confirmed:

- `inbox.py:711 summary()` — the one place I edited.
- `scaffold.py:293 _inbox_probe()` — calls `inbox.summary()`, inherits the
  fix; verified live (see self-review below), did not touch this file.
- `__main__.py:761` (`cmd_inbox`'s printed summary) — inherits the fix by
  calling `inbox.summary()`. `__main__.py:763` (`cmd_inbox`'s listing) calls
  `open_entries()` directly, which still returns SKIPPED rows — listing
  behavior preserved, confirmed live.
- `verify.py:850 _file_effects`'s dedup — calls `open_entries()`, **not**
  touched. This is the hazard surface; see below.

No discrepancy from the map I was given. I did not find any additional
counting surface it missed.

## Dedup-hazard demonstration

`knowledge_harness/verify.py:850`'s `_file_effects` builds `open_keys` from
`inbox.open_entries(vault_root)` (unfiltered) to decide whether an outcome is
already filed, and skips filing if so. Because the fix lives in `summary()`
and does not touch `open_entries()`, this key set still includes SKIPPED
entries.

Demonstrated with a new permanent regression test,
`tests/test_verify_cli.py::test_file_effects_does_not_refile_an_already_open_skipped_finding`:
it pre-files one SKIPPED finding via `inbox.append_entry`, builds a matching
`Outcome` with the same `(check, target, target_kind, result, target_hash,
notice_class, notice_type, notice_date)` key, calls `verify._file_effects`
directly with that single outcome, and asserts `inbox.open_entries(tmp_vault)`
still contains exactly the one original entry (same `id`) — i.e. no
duplicate was filed. This test passed both before and after the
implementation change (confirming the hazard never landed) and continues to
pass in the full suite.

## Tests that pinned the old (defective) behavior

None found. `tests/test_inbox.py::test_summary_counts_and_age` (the existing
`summary()` test) uses only `UNMATCHED`/`UNREACHABLE` entries — it never
exercised SKIPPED, so it did not assert the defect and needed no change.
Grepped every test file for `SKIPPED` combined with `summary`/`unacknowledged`
usage; no other test in the suite pinned SKIPPED-counts-as-unacknowledged.

## Files changed

- `knowledge_harness/inbox.py` — `summary()` now filters
  `entry.result != Result.SKIPPED.value` before computing `unacknowledged`
  count and `oldest`. `open_entries()` untouched (deliberately — see hazard
  above). Docstring states only the mechanical constraint (SKIPPED stays in
  `open_entries()` because verify's dedup keys off it); the "why exclude it
  from counting" rationale (rubber-stamp pressure) went to the commit body
  instead, per the comments-state-constraints/provenance-in-commit-body rule.
- `tests/test_inbox.py` — new
  `test_skipped_entries_not_counted_unacknowledged` (RED/GREEN test from the
  brief; SKIPPED-only queue → 0/None; mixed queue → count/oldest derive from
  the non-SKIPPED entry only; SKIPPED stays visible via `open_entries`).
- `tests/test_verify_cli.py` — new
  `test_file_effects_does_not_refile_an_already_open_skipped_finding` (dedup
  hazard demonstration) plus the corresponding `_file_effects` import.

`inbox.summary()` was **not renamed** — per the author's naming ruling, it is
dev-facing (T7), never reaches vault prose, and rename is implementer's
discretion / not owed for this task. Left as-is.

## Self-review

- SKIPPED entries still visible in listings: confirmed live —
  `inbox.open_entries(vault)` for a SKIPPED-only vault returns 1 entry with
  `result == 'SKIPPED'`; `cmd_inbox`'s printed listing (`__main__.py:763`)
  iterates that same unfiltered list, so it still prints SKIPPED rows.
- Doctor's inbox probe reports the right count: confirmed live —
  `_inbox_probe` on a SKIPPED-only vault returns
  `Probe(check='inbox', result=MATCHED, reason='0 unacknowledged findings')`;
  on a mixed vault (1 SKIPPED + 1 UNMATCHED) it returns
  `Probe(check='inbox', result=UNMATCHED, reason='1 unacknowledged findings; oldest 2026-08-16')`
  — the SKIPPED entry's earlier date does not leak into `oldest`.
- No other counting surface missed — grep confirms `verify.py`, `scaffold.py`,
  `__main__.py`, `inbox.py` are the only 4 files that call `summary(` or
  `open_entries(`, matching the brief's map exactly.

## Concerns

None. The change is a single filtering expression in one function, the
hazard the brief flagged was verified not to have landed (with a permanent
regression test guarding it), and the full suite plus form gate are green.
