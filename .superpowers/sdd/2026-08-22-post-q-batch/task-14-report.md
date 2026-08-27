# Task 14 report: RW date parsing + arming honesty

Commit: `079c287` — `fix: RW date parsing accepts production formats; unarmed RW leg says so` (amended from `a53a48b` after fix round 1; no rebase, branch tip only)

## Surfaces (as verified before touching anything)

- `knowledge_harness/checks.py:914` — `_rw_date`, exact `fromisoformat`-only body the brief describes.
- `knowledge_harness/checks.py:8` — `from datetime import date as _date`; no `_datetime` alias existed. Added one.
- `knowledge_harness/verify.py:986` — `notice_lookup = checks.load_rw_csv(rw_csv) if rw_csv else None`. Exact match, unmodified in the end (see decision below).
- `knowledge_harness/__main__.py:377-422` — `cmd_verify`, the only place `verify` prints anything. Confirmed `verify.py` has zero `print` calls (the 3 `grep -c "print("` hits are the substring inside `_notice_fingerprint(`).

## Step 1/2 — RED evidence (date parsing)

Test added to `tests/test_checks.py` (brief's Step 1, verbatim):

```python
def test_rw_date_accepts_production_formats():
    assert checks._rw_date("1/2/2023 0:00") == "2023-01-02"
    assert checks._rw_date("12/31/2019") == "2019-12-31"
    assert checks._rw_date("2023-01-02") == "2023-01-02"
    assert checks._rw_date("not a date") is checks._INVALID
    assert checks._rw_date("13/45/2023 0:00") is checks._INVALID
```

Command: `.venv/bin/python -m pytest tests/test_checks.py::test_rw_date_accepts_production_formats -v`

```
>       assert checks._rw_date("1/2/2023 0:00") == "2023-01-02"
E       AssertionError: assert <object object at 0x7400f6321b20> == '2023-01-02'
E        +  where <object object at 0x7400f6321b20> = <function _rw_date at 0x7400f4b67920>('1/2/2023 0:00')
FAILED tests/test_checks.py::test_rw_date_accepts_production_formats - Assert...
1 failed in 0.25s
```

Failed exactly as predicted: `_rw_date("1/2/2023 0:00")` returned the `_INVALID` sentinel object, not from a fixture error — `date.fromisoformat` rejects the slash-separated string and the old body has no fallback.

## Step 3 — implementation (date parsing)

`knowledge_harness/checks.py`: added `from datetime import datetime as _datetime` beside `_date`; replaced the ISO-only body with the brief's enumerated-format loop (`_RW_DATE_FORMATS = ("%m/%d/%Y %H:%M", "%m/%d/%Y")`), tried only after `fromisoformat` fails, falling through to `_INVALID` when nothing matches. One deviation from the brief's literal snippet: `datetime.strptime(...).date().isoformat()` trips ruff's `DTZ007` (naive datetime from `strptime` without `%z`); added `# noqa: DTZ007` with a one-line comment — these are bare calendar dates, no timezone semantics apply, and the project has `DTZ` enabled deliberately (`pyproject.toml`).

## Step 4 — RED evidence (arming honesty)

The brief's Files line named `tests/test_verify.py`; that file does not exist in this repo (confirmed via `ls tests/`). Stdout-capture assertions for `verify` already live in `tests/test_verify_cli.py` (e.g. `test_real_verify_cli_reports_invalid_bibliography_without_traceback`), so both new CLI tests went there instead.

Tests added:

```python
def test_real_verify_cli_states_rw_leg_absence_without_rw_csv(net_vault, capsys):
    code = main(["verify", "--vault", str(net_vault), "--offline"])
    output = capsys.readouterr().out
    assert code == 0
    assert output.count("update-notice: RW leg not run (no --rw-csv)") == 1
    assert not [e for e in inbox.open_entries(net_vault) if e.check == "update-notice"]


def test_real_verify_cli_omits_rw_leg_absence_line_when_rw_csv_supplied(net_vault, capsys, tmp_path):
    rw_csv = tmp_path / "rw.csv"
    rw_csv.write_text("OriginalPaperDOI,OriginalPaperPubMedID,RetractionDate,RetractionNature\n")
    code = main(["verify", "--vault", str(net_vault), "--offline", "--rw-csv", str(rw_csv)])
    output = capsys.readouterr().out
    assert code == 0
    assert "RW leg not run" not in output
```

Command: `.venv/bin/python -m pytest tests/test_verify_cli.py::test_real_verify_cli_states_rw_leg_absence_without_rw_csv tests/test_verify_cli.py::test_real_verify_cli_omits_rw_leg_absence_line_when_rw_csv_supplied -v`

```
tests/test_verify_cli.py::test_real_verify_cli_states_rw_leg_absence_without_rw_csv FAILED
tests/test_verify_cli.py::test_real_verify_cli_omits_rw_leg_absence_line_when_rw_csv_supplied PASSED

>       assert output.count("update-notice: RW leg not run (no --rw-csv)") == 1
E       assert 0 == 1
1 failed, 1 passed in 3.44s
```

Failed exactly as predicted: the unarmed run printed the absence line zero times — today's `cmd_verify` says nothing when `--rw-csv` is omitted. (The "supplied" test passed trivially pre-implementation since there was nothing to assert against yet; it became a real regression guard once the emission existed.)

## Detection/emission decision

**Chosen: `cmd_verify` checks its own argument (`args.rw_csv`).** Reasoning:

1. Emission can only happen in `cmd_verify` — `verify.py` has no `print` calls at all, confirmed by grep.
2. `cmd_verify` already receives the identical `rw_csv` value that flows into `verify_state(..., rw_csv=args.rw_csv, ...)` and on into `_plan_state`'s `checks.load_rw_csv(rw_csv) if rw_csv else None`. There is no additional information `verify.py` could compute that `cmd_verify` doesn't already have — detection needs no plumbing.
3. Widening the report contract (`{"outcomes": raw, "counts": counts}`) to carry a new key would have touched every place that pattern-matches that exact two-key dict literal. `tests/test_verify_cli.py` has several `monkeypatch.setattr("knowledge_harness.__main__.verify_state", lambda *_: ({"outcomes": [...], "counts": {...}}, ...))` fixtures (lines ~427, 453, 632, 1095, 1560) that construct this dict by hand; adding a field would force touching all of them for a decision the CLI can make on its own. `knowledge_harness/publish.py` also calls `verify_state` and discards the report entirely (`_report, effective, ...`), so a report-side change would add surface with no consumer there.
4. Keeping the check purely inside `cmd_verify`'s `print` block means the absence line is architecturally incapable of touching the `Outcome`/`effective`/`hashes`/inbox pipeline — it is a bare `print`, never a `checks.Outcome`, so it structurally cannot be filed, counted, or acknowledged.

`verify.py` was not modified.

## Hard constraint — confirmed empirically, not just by construction

`test_real_verify_cli_states_rw_leg_absence_without_rw_csv` asserts `not [e for e in inbox.open_entries(net_vault) if e.check == "update-notice"]` in the same run that prints the absence line — passing, confirming the line files nothing into the inbox. No new reason code was added anywhere.

## GREEN evidence

```
.venv/bin/python -m pytest tests/test_checks.py::test_rw_date_accepts_production_formats \
  tests/test_verify_cli.py::test_real_verify_cli_states_rw_leg_absence_without_rw_csv \
  tests/test_verify_cli.py::test_real_verify_cli_omits_rw_leg_absence_line_when_rw_csv_supplied -v
...
3 passed in 0.32s
```

Full pre-existing suites in both touched files: `.venv/bin/python -m pytest tests/test_checks.py tests/test_verify_cli.py -q` → `203 passed, 1 skipped` — no existing test pinned the old ISO-only or silent-skip behaviour.

Form gate: `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` → 8/8 passed (ruff-check required the `# noqa: DTZ007` above; passed after adding it).

Full offline suite: `.venv/bin/python -m pytest tests -q` → `1557 passed, 7 skipped` (baseline 1554/7 + 3 new tests, zero regressions).

## Arming ruling (recorded, not new work)

Verified `knowledge_harness/templates/ci/rw-batch.yml` line 34 before recording this: it already invokes `python -m knowledge_harness verify --vault . --offline --surface audit --git-candidate worktree --rw-csv "$RUNNER_TEMP/rw.csv" ...` — the scheduled CI lane runs the RW leg explicitly armed. The drill runs it explicitly armed too (Plan S amendment already recorded elsewhere). Local `verify` invocations without `--rw-csv` now state the absence via the new stdout line instead of running silent. No default-on: fetching the RW CSV remains a deliberate network-and-license act, never automatic. This ruling required no code change beyond the absence line itself — recorded here and in the commit body per the brief.

## Self-review

- ISO still parses: `checks._rw_date("2023-01-02") == "2023-01-02"` — passing.
- Genuinely malformed dates still return `_INVALID`, including the well-formed-shape-but-invalid-date case `"13/45/2023 0:00"` (month 13) — passing; `strptime` raises `ValueError` for the out-of-range month, falling through the loop to `_INVALID`.
- Absence line appears exactly once when `--rw-csv` is omitted, and not at all when it is supplied — both pinned by dedicated tests.

## Concerns

None blocking. One judgment call worth flagging: the brief's own snippet for `_rw_date` didn't anticipate the `DTZ007` lint (enabled deliberately in this repo's ruff config); resolved with a `# noqa: DTZ007` plus a comment stating why (bare calendar date, no tzinfo applies) rather than restructuring the parse to avoid `datetime.strptime` entirely, since the brief's format-loop shape was otherwise exactly right and worth preserving.

## Fix round 1

Review came back spec-compliant; both judgment calls (detection/emission split, `# noqa: DTZ007`) were checked, not just accepted, and upheld. One Important, three Minor findings, all addressed in the same commit (amended: `a53a48b` → `079c287`, no rebase, nothing on top of the branch tip either way).

**Finding 1 (Important) — verify's output grammar didn't anticipate a non-result line.** `skills/verify-citations/SKILL.md` documented `verify`'s output as strictly `RESULT check target — reason`, grouped by "the second token on each line." Under that literal grammar the absence line `update-notice: RW leg not run (no --rw-csv)` parses as RESULT=`update-notice:`, check-id=`RW` — a phantom check id an agent following the skill would report as a bogus result. Fixed with one added paragraph in the skill's "Report the four states honestly" section naming this exact line as an example of a non-result status line that must not be parsed as `RESULT check target — reason` and must not be folded into the grouped-by-check-id presentation. Did not reshape the line into a four-state result (e.g. `SKIPPED update-notice …`) — that was explicitly the wrong fix per the coordinator's message, since it would dress a non-result as a result and re-enter the failure the brief forbids.

**Finding 2 (Minor) — the fix was pinned only at the private-helper level.** `test_rw_csv_matches_both_identifiers_and_blocking_beats_warning` fed only ISO-shaped `RetractionDate` values through `load_rw_csv`/`check_rw_batch`, so a future regression that re-filtered rows to ISO-only inside `load_rw_csv` itself would have left `test_rw_date_accepts_production_formats` green. Fixed: changed the blocking row's `RetractionDate` from `2024-02-02` to `2/2/2024 0:00` (production format). `_rw_date` parses it to the identical `"2024-02-02"` already asserted, so no other assertion in that test moved — confirmed by running the test in isolation before and after.

**Finding 3 (Minor) — rationale was in comments/docstring instead of the commit body.** The SKIPPED-counting argument ("a queue entry nobody has to acknowledge would manufacture rubber-stamp pressure") lived in the `cmd_verify` code comment and was repeated in the new test's docstring — both narration/rationale, not constraints the code can't show, per this batch's comment doctrine (`docs/superpowers/plans/2026-08-24-plan-w-quality-tail.md:39`, confirmed present and binding — it moved out of the batch plan's Global Constraints into Plan W when Part 4 split out). Trimmed the `cmd_verify` comment to state only "Stdout line only — never a review-queue record," trimmed the `_RW_DATE_FORMATS` comment in `checks.py` to state only the production-shape fact (not narrate the try-ISO-then-loop control flow the code already shows), and trimmed the test docstring to a one-line description of what it pins. The full SKIPPED-counting rationale now lives in the amended commit body instead — confirmed by grep: `git log -1 --format=%B | grep -i "rubber\|SKIPPED-count\|acknowledg"` now returns three matches, where it previously returned none.

**Finding 4 (Minor) — pointer comment, not a restructure.** Added a two-line comment directly above `notice_lookup = checks.load_rw_csv(rw_csv) if rw_csv else None` at `verify.py:986` naming `cmd_verify` as the consumer that mirrors this same falsy-`rw_csv` predicate. Did not extract a shared predicate function or otherwise restructure — the reviewer verified the duplication is real but the alternatives are worse for a one-line check on each side, so this is a pointer only.

**Re-verification after all four fixes:**
- `.venv/bin/python -m pytest tests/test_checks.py tests/test_verify_cli.py -q` → `203 passed, 1 skipped`
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` → 8/8 passed
- `.venv/bin/python -m pytest tests -q` → `1557 passed, 7 skipped` (unchanged from before the fix round — no regressions introduced by the four fixes)

No new concerns from the fix round.
