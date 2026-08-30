# Task 19 report: partial notice dates keep their precision

## Status

Complete. Task 19 Steps 1–5 implemented and committed. Task 19b (PreToolUse
deny) is explicitly out of scope for this report and was not touched — no
hook created, no plugin hooks config touched, §10 deferred entry untouched.

## Commit

`fix: partial Crossref dates keep precision; ambiguous reinstatement never clears`

Files: `research_vault/checks.py`, `research_vault/inbox.py`,
`tests/test_checks.py`, `tests/test_inbox.py`,
`.superpowers/sdd/2026-08-22-post-q-batch/task-19-report.md`.

## Test summary

Full suite: 1646 passed, 7 skipped (baseline 1624/7 + 22 new tests: 9 in
`test_checks.py`, 13 in `test_inbox.py`). `ruff check` clean, `ruff format
--check` clean, `mypy research_vault/` clean (27 files), `echo '{}' |
python hooks/stop_publish_gate.py` silent, exit 0.

## What changed

**`checks._notice_date_from_updated`**: now returns Crossref's own precision
(`YYYY`, `YYYY-MM`, or `YYYY-MM-DD`) instead of padding a partial date to
January 1st. Range validation still runs at full precision (a missing
month/day defaults to 1 *for validation only*, using a `None` sentinel rather
than `month or 1` — an *explicit* 0 is not "absent" and must still fail; see
discriminating test below).

**`checks._active_blocking_notices`**: the reinstatement-clears comparison
is no longer a bare string `>=`. New helpers:
- `_dates_incomparable(a, b)`: two full (`YYYY-MM-DD`, 10-char) dates are
  always comparable, including when equal (a same-day match is decisive).
  Otherwise, ambiguous whenever the shorter string is a prefix of the longer
  — which includes two *equal* partial strings, since a string is always
  its own prefix. That last part is a deliberate reading, not a literal
  transcription of the brief's "neither is a strict prefix of the other":
  two year-only dates that read identically (`"2023"` vs `"2023"`) give zero
  evidence about which day within 2023 came first, so they must be treated
  as ambiguous too, not as a decisive tie. Under the literal "strict prefix"
  reading, the brief's alternate clause ("or both are full dates") would be
  redundant, since equal full dates already pass the "not a strict prefix"
  test on their own — that clause only does work if the prefix test is meant
  to catch equality as well, and full dates are separately re-admitted by it.
- `_reinstatement_clears(reinstatement_date, notice_date)`: returns
  `False` when incomparable, otherwise the original `reinstatement_date >=
  notice_date`.

**`inbox.py`**: new `_validate_partial_date`/`_validate_optional_partial_date`,
accepting `YYYY`, `YYYY-MM`, `YYYY-MM-DD` with real calendar-range validation
(rejects `2023-13`, `2023-06-31`, `2023-00`, `23`, `2023-6`, wrong separators,
trailing whitespace). Wired into `_validate_notice_fingerprint` for
`notice_date` only. `_validate_date`/`_validate_optional_date` and
`detection_date` are untouched and still require a full calendar date —
pinned by `test_detection_date_still_requires_full_precision`.

## Per-test discrimination matrix

Each row: production line reverted, ran the named test(s), confirmed red,
then restored (verified `diff` against a pre-edit backup was empty and the
full suite green again before moving to the next probe).

| Test | Line reverted | Result |
|---|---|---|
| `test_partial_date_parts_keep_precision` | `_notice_date_from_updated` restored to original padding (`[*parts,1,1][:3]` + `.isoformat()`) | RED (returns `"2023-01-01"` not `"2023"`) |
| `test_update_notice_year_only_retraction_survives_same_year_reinstatement` | same revert | RED (`MATCHED` not `UNMATCHED` — reproduces the brief's Step 2 claim exactly) |
| `test_partial_date_parts_still_reject_an_explicit_zero_month_or_day` | `month if month is not None else 1` → `month or 1` (the brief's literal suggestion) | RED (`{"date-parts": [[2023, 0]]}` returns `"2023-00"` instead of `_INVALID` — confirms the None-sentinel deviation from the brief's literal text is load-bearing) |
| `test_ambiguous_reinstatement_does_not_clear`, `test_equal_partial_dates_do_not_clear`, end-to-end test above | `_reinstatement_clears` call replaced with bare `reinstatement >= notice["notice_date"]` | RED on all three |
| `test_ambiguous_reinstatement_does_not_clear_reversed_precision`, `test_unambiguous_full_date_reinstatement_still_clears`, `test_same_day_full_date_reinstatement_still_clears`, `test_differing_precision_reinstatement_still_clears_when_not_a_prefix` | same revert | stayed GREEN — these already held under the old code (string comparison happened to give the right answer for these shapes); they are regression guards, not discriminators of *this* line, and are documented as such |
| `test_same_day_full_date_reinstatement_still_clears` | `>=` → `>` in `_reinstatement_clears` | RED (pins the `>=` boundary explicitly, as required) |
| `test_equal_partial_dates_do_not_clear` | `_dates_incomparable`'s prefix check changed to exclude equality (`shorter != longer and longer.startswith(shorter)`) | RED — confirms the equal-partial-dates interpretation above is actually exercised, not just asserted |
| `test_notice_date_accepts_crossrefs_own_precision[2023]`, `[2023-06]`, `test_partial_notice_date_finding_is_fully_acknowledgeable` | `_validate_optional_partial_date` swapped back to `_validate_optional_date` in `_validate_notice_fingerprint` | RED (raises `notice_date must be a YYYY-MM-DD calendar date`) |
| `test_detection_date_still_requires_full_precision` | same revert | RED for a related reason — the `pytest.raises(match="detection_date")` no longer matches because `notice_date`'s validator now raises first with "notice_date" in the message; still confirms sensitivity to this line |
| `test_notice_date_rejects_malformed_or_out_of_range_partial_dates` (all 8 parametrized cases) | `_validate_partial_date` reduced to `return _validate_text(name, value)` (accepts anything) | RED on all 8 — confirms it is a real validator, not a pass-through |

Every new production branch has at least one test that goes red when it is
removed or weakened.

## Consumers traced (Step 4)

Two independent methods, as asked:

1. **Grep**, matching and extending the controller's list: `notice_date` in
   `inbox.py` (validation, `finding_id`, `append_entry`, `append_ack`, `load`,
   `is_acknowledged`, `summary`) and `checks.py` (`_crossref_notices`,
   `_active_blocking_notices`, `_effective_blocking`,
   `reduce_update_notice_outcomes`, `_blocking_outcome`, `check_rw_batch`).
2. **Traced the actual call path** in `verify.py` independently of grep
   (`_notice_fingerprint`, `_effective`, `_warning_effectiveness`,
   `_file_effects`) to confirm `outcome.extra["notice_date"]` really does
   flow straight into `inbox.append_entry(notice_date=...)` and
   `inbox.is_acknowledged(..., notice_date)` — this is the load-bearing path
   the controller's blocker warning was about, confirmed by reading the
   production code rather than trusting the grep. Also confirmed by running
   the test suite before implementing inbox.py's fix: with only checks.py
   changed, no test failed yet (no test fixture exercises year-only
   `updated` dates), but manual tracing showed `append_entry`/`append_ack`
   would raise on the first live `notice_date="2023"` — added
   `test_partial_notice_date_finding_is_fully_acknowledgeable` as the
   end-to-end proof that the whole append→load→ack→is_acknowledged path
   works with a partial date, per the advisor review's explicit call-out
   that a standing-but-unacknowledgeable alert would be worse than the bug
   being fixed.

`check_rw_batch`'s dates (Retraction Watch CSV via `_rw_date`) are always
full ISO dates or `None` — unaffected by this change, confirmed by reading
`_rw_date` and by grep across `tests/` for any RW fixture with partial
precision (none found).

## §2: max() key ordering — measured, not accepted

Ran the one-liner directly:
```
>>> "2023" < "2023-01-01"
True
>>> "2023" > "2022-12-31"
True
```
Different years compare correctly (second case). Same year, differing
precision does not: a year-only date always sorts as "earlier" than any full
date in the same year, even if the year-only notice actually happened later
in the year (e.g. December). This affects **two** call sites, not just the
one named in the brief:
- `_effective_blocking` (checks.py, key `(notice_date is not None, notice_date
  or "", type)`)
- `reduce_update_notice_outcomes` (checks.py, same key shape, live vs RW leg
  reduction)

Not fixed — it's a reporting-identity choice, not a safety hole: clearing
already happened in `_active_blocking_notices` before either `max()` runs, so
a surviving blocker still blocks regardless of which candidate `max()`
picks as "the" effective one. Filed as
[GitHub issue #23](https://github.com/eranroseman/knowledge-harness/issues/23)
covering both sites.

## §3: finding_id dedup consequence

`inbox.finding_id` embeds `notice_date` verbatim
(`.../{notice_class}/{notice_type}/{notice_date or 'unknown'}`). Changing
emitted precision means a pre-existing open row keyed `.../2023-01-01` will
not dedup against a newly-filed `.../2023` row for the same year-only
notice — this produces exactly one duplicate filing per year-only blocking
notice at the first post-upgrade verify run, each needing its own
acknowledgment. Disposition: **recorded accept**. The old padded rows are
artifacts of the defect being fixed (they claim a precision Crossref never
actually reported), so the one-time duplicate is a correct byproduct of
correcting bad data, not a bug to route around.

## Loose prefix assertion — issue #22

`tests/test_verify_cli.py:1861` (`test_live_drill_wakefield_and_fabricated`,
a live-network test, skipped offline) asserts
`outcome.extra["notice_date"].startswith("2010-02")` — a loose prefix
assertion on the exact field this task touches. It stays green under this
change (live Crossref/RW full dates are unaffected), so left as-is, but
noted as a new instance on
[GitHub issue #22](https://github.com/eranroseman/knowledge-harness/issues/22)
via `gh issue comment`.

## Step 5: tests that pinned padded dates

None found. Two independent checks: (1) grepped `tests/` for any `"updated":
{"date-parts": ...}` fixture with fewer than 3 elements — only the two
already-malformed/empty cases existed (`[]`, `[[]]`), neither of which
produces a padded date; (2) the pre-implementation full-suite run (1624/7,
matching the stated baseline exactly) was the empirical oracle — after
implementing both production changes, the full suite is still 1646 passed
(1624 + 22 new), so nothing existing needed fixing.

## Concerns

1. **Max() precision-ordering choice** (checks.py `_effective_blocking` and
   `reduce_update_notice_outcomes`) — destination: GitHub issue #23 (filed).
2. **Loose prefix assertion** at `tests/test_verify_cli.py:1861` — destination:
   GitHub issue #22 (commented, existing issue covers this pattern).
3. **finding_id dedup one-time duplicate** for year-only notices upgrading
   from padded to honest precision — destination: recorded accept, reasoned
   above (not a bug; a one-time consequence of correcting bad data).

## Fix round 1 (response to review of commit 50538bb)

Both verdicts on the round-1 review were PASS (spec and quality); three
quality findings addressed here without amending 50538bb.

**F1 (Medium) — `inbox.py`'s `_PARTIAL_DATE` accepted non-ASCII digits.**
`\d` is Unicode-aware, and unlike the sibling `_validate_date` (backstopped
by `datetime.date.fromisoformat`, which rejects non-ASCII digits), the new
`_validate_partial_date` converts matched groups with plain `int()`, which
happily parses them too. Reproduced before the fix: `'٢٠٢٣'`, `'２０２３'`,
`'2023-٠٦'`, and `'2023-06-١٥'` were all accepted and returned verbatim,
which would have landed in `finding_id` and ack fingerprints, and would have
let a hand-written inbox line that previously raised `InboxError` parse
silently on `load()`. Fixed with one `re.ASCII` flag on `_PARTIAL_DATE`.
Pinned by `test_notice_date_rejects_non_ascii_digits` (4 parametrized
cases, ids `arabic-indic-year`, `fullwidth-digit-year`, `arabic-indic-month`,
`arabic-indic-day`); reverting the `re.ASCII` flag was confirmed to turn
all four red (`DID NOT RAISE ValueError`), then the fix was restored and
`diff`-verified clean before moving on.

Searched a second way (not just re-finding the `\d` occurrence): grepped
`inbox.py` for every `int(...)` call over a regex-captured group. Only
`_validate_partial_date`'s three (`year`, `month`, `day`) exist; `_validate_date`
at line 169 also matches `\d` but is backstopped by `fromisoformat`
(confirmed it raises on the same four inputs), and `_REASON` (line 81) is
built from `REASON_CODES`, not `\d`, so it was never in scope. No other
instance of the "regex `\d` feeding straight into `int()` with no ASCII
backstop" shape exists in `inbox.py`.

**F2 (Low) — `_dates_incomparable` docstring restated what `startswith`
does instead of stating the load-bearing fact.** Rewritten to state the
property the review named: ISO date-precision strings denote
nested-or-disjoint intervals, so a prefix test is an exact decision
procedure, not a heuristic — worked examples dropped.

**F3 (Low) — provenance/history duplicated from the commit body into a
comment and a test docstring.** Trimmed `_validate_partial_date`'s
docstring (dropped "rather than pad it to a full date") and
`test_update_notice_year_only_retraction_survives_same_year_reinstatement`'s
docstring (dropped the "Before this fix..." sentence) to state only the
current constraint/behavior.

Full suite: 1650 passed, 7 skipped (1646 + 4 new). `ruff check`, `ruff
format --check`, and `mypy research_vault/` all clean on the four
touched files; `stop_publish_gate.py` silent, exit 0.

Deferred per coordinator instruction, not fixed here: `mutation-baseline.txt`
and the two `.manifest.json` sidecars are stale after this diff — Task 24
Step 4 owns the regenerate-or-record convention and this task's brief has
no such step.
