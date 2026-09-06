# Task 14 review - b1d5f17..a53a48b

Disposition: historical (2026-09-06)

## Spec Compliance

**Verdict: compliant.**

Every value the brief names landed verbatim. The Step 1 test body is copied exactly, all five assertions
(tests/test_checks.py:1370). `_RW_DATE_FORMATS = ("%m/%d/%Y %H:%M", "%m/%d/%Y")` matches the brief's snippet
(research_vault/checks.py:919), tried only after `date.fromisoformat`, falling through to `_INVALID`. The
`_rw_date(value) -> str | None | object` contract is unchanged: ISO string, `None` for empty and blank,
`_INVALID` for non-strings and unparseable text; the only import change is the `_datetime` alias the brief
called for. The absence string is the brief's own example, `update-notice: RW leg not run (no --rw-csv)`
(research_vault/__main__.py:409). The commit subject matches the brief character for character. One commit,
four files, no scope creep.

The brief's hard constraint - stdout line, not a review-queue record, no new reason code - holds structurally
and not merely by test. The emission is a bare `print` inside `cmd_verify`, executed after `verify_state` (and
its `_file_effects` inbox filing) has already returned, so it can never become an `Outcome`, a reason code, or
a queue entry. No `inbox.append_entry` appears anywhere in the diff. The paired CLI test also pins it
empirically, asserting `inbox.open_entries(net_vault)` carries no `update-notice` entry in the same run that
prints the line.

Two documented deviations, both justified and both recorded in the commit body: the brief's Files line named
`tests/test_verify.py`, which does not exist in this repo, so both CLI tests went to `tests/test_verify_cli.py`
where the existing stdout-capture assertions live; and the brief's snippet did not anticipate ruff's `DTZ007`,
resolved with a line-scoped `# noqa: DTZ007` carrying a one-line reason rather than by widening the project's
deliberate lint configuration.

The brief also pointed at `research_vault/verify.py:986` as the emission site. `verify.py` was not modified.
This is not a spec miss: `verify.py` has no `print` calls at all, so emission can only happen in `cmd_verify`,
which already receives the same `rw_csv` value. Detection parity is exact - `if not args.rw_csv` in
`cmd_verify` mirrors `notice_lookup = checks.load_rw_csv(rw_csv) if rw_csv else None` at verify.py:986,
including the empty-string falsy edge - so the printed claim is truthful for every invocation.

The one Important finding below is not a missed, extra, or misunderstood requirement. The colliding line text
is the brief's own example string, used verbatim; the defect is a downstream consumer document that nobody
updated. Plan-induced, not implementer drift.

### Cannot verify from diff

Two items remain open for the controller. Four others were resolved during synthesis and are recorded here so
they are not re-opened.

**Open:**

1. *Suite green offline at task end: 1557 passed / 7 skipped against the 1554/7 baseline, with no new warnings.*
   The +3 arithmetic matches the three test functions added in the diff, but the run itself is the
   implementer's, and the report does not quote the full output. Controller check: run
   `.venv/bin/python -m pytest tests -q` once at part end and confirm 1557/7 with a clean warnings summary.

2. *Form gate 8/8.* Not re-run here; the gate can touch the working tree and this review is read-only.
   Controller check: `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files`. One run confirms both
   formatting and that the `# noqa: DTZ007` is load-bearing - RUF100 is active, so an unnecessary suppression
   would fail the gate.

**Resolved during synthesis:**

3. *The Plan S amendment the commit body cites.* Confirmed present.
   `docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md:57` reads "Leg attribution (amended
   2026-08-22): every retraction plant records WHICH leg caught it, and the drill runs with the RW leg armed
   (`--rw-csv` supplied, matching the CI lane it ships in ...)". The commit body's claim is true.

4. *The commit body records the arming ruling.* Confirmed by reading `git log -1 --format=%B a53a48b`: CI lane
   (with `templates/ci/rw-batch.yml` line 34 quoted), armed drill, local absence line, and the explicit
   no-default-on reason - "fetching the RW CSV is a network and license act that stays deliberate, never
   automatic".

5. *Whether the TDD RED requirement for Step 4 is met.* Yes, by
   `test_real_verify_cli_states_rw_leg_absence_without_rw_csv` alone, which failed 0 == 1 before implementation.
   The companion `..._omits_..._when_rw_csv_supplied` test passed pre-implementation, as the report itself
   concedes; it is a negative-assertion regression guard that can only fail if the branch is inverted, not a
   second RED.

6. *The RED failure outputs themselves.* Inherently unreproducible post-fix without mutating this checkout,
   which the review is barred from. Accepted: the quoted output is self-consistent (a sentinel object returned
   from `_rw_date`, the absence line counted zero times) and matches the pre-change code visible in the diff's
   removed lines.

## Strengths

- The `_rw_date` rewrite (research_vault/checks.py:922-938) preserves the three-way contract exactly with no
  signature change: ISO is still tried first through the untouched `fromisoformat` path, the format loop
  `continue`s rather than swallowing, and the function falls through to `_INVALID` when nothing matches.
- The negative test cases include `13/45/2023 0:00` (tests/test_checks.py:1375-1376) - a string that matches the
  new format shape syntactically but names no real calendar date. The parser cannot be made permissive by
  loosening the format strings without turning the test red.
- `output.count("update-notice: RW leg not run (no --rw-csv)") == 1` (tests/test_verify_cli.py:1562) pins
  exactly-once rather than mere presence, and the adjacent `inbox.open_entries` assertion pins the task's hard
  constraint empirically in the same run that prints the line, instead of arguing it by construction.
- The emission sits after the exit-2 error return and before the outcome loop
  (research_vault/__main__.py:405-409), so a failed run stays silent about the leg and the final JSON counts
  line remains the last line of stdout.
- The `# noqa: DTZ007` is line-scoped with a one-line reason (a bare calendar date, no tzinfo applies) rather
  than a widening of the project's deliberate DTZ configuration.
- The detection/emission decision was made deliberately and its stated reason survives verification: five
  hand-written two-key report literals in tests/test_verify_cli.py would indeed have broken under a widened
  report contract, and `publish.py` discards the report entirely.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

**1. research_vault/__main__.py:409 - the new unconditional stdout line does not conform to `verify`'s
documented output grammar, and the one consumer that documents and positionally parses that grammar was not
updated. Status: CONFIRMED.**

*What is wrong.* `skills/verify-citations/SKILL.md:25` states that "`verify` prints one line per non-MATCHED
outcome - `RESULT check target - reason` - followed by a final JSON summary of counts by result", and line 27
instructs the agent to present the printed lines "grouped by check id as the CLI reports them (the second token
on each line)". The new line, `update-notice: RW leg not run (no --rw-csv)`, puts `update-notice:` in the
RESULT slot and `RW` in the check-id slot.

*Why it matters.* The collision lands on the skill's own default path. SKILL.md:16 documents
`python3 -m research_vault verify --vault PATH`, with no `--rw-csv`, so every documented invocation now
emits the line - first, ahead of the outcome lines and the JSON counts. An agent following the skill literally
would report a phantom check id `RW` carrying a bogus result state: a fabricated reporting surface in the exact
domain this task exists to make honest. The consumer's own guard against a phantom id was removed the day
before: d44452e ("verify-citations defers to CLI output") replaced the explicit enumeration at line 27 - "the
second token on each line - `citekey`, `doi`, `metadata`, ..." - with an open "as the CLI reports them", so
nothing in the skill now rejects an unknown second token. `tests/test_skill_contracts.py`'s sweep checks only
that check ids a SKILL.md *names* exist in code; it does not model CLI output grammar, so no test catches this.

*Blast radius, checked independently.* Exit-code consumers are unaffected.
`research_vault/templates/ci/verify.yml:48` also runs without `--rw-csv` and so will print the line, but it
branches purely on `$?` (0/1/3/other) and never parses stdout. `hooks/stop_publish_gate.py:88-90` imports
`verify_state` directly and never sees the CLI's stdout. The damage is confined to the documented
human-and-agent-facing grammar in the skill.

*How to fix.* Add one sentence to the output section of `skills/verify-citations/SKILL.md` describing the
RW-absence line as a preamble note rather than an outcome line, and telling the agent not to group or count it.
Do not reshape the line into `SKIPPED update-notice ...` - that re-enters the SKIPPED-counting failure the
brief explicitly forbids.

### Minor (Nice to Have)

**2. research_vault/__main__.py:406 - rationale and provenance live in code comments and a test docstring
rather than in the commit body. Status: NOT-VERIFIED-MINOR (substance confirmed by synthesis).**

Both the spec and quality lenses raised this independently; it is one defect and is merged here. The comment at
__main__.py:406-408 states the constraint in its first clause ("Stdout line only - never a review-queue
record") and then argues it ("A queue entry nobody has to acknowledge would manufacture rubber-stamp pressure
(the SKIPPED-counting lesson)"). The docstring of `test_real_verify_cli_states_rw_leg_absence_without_rw_csv`
(tests/test_verify_cli.py:1551-1557) repeats the same argument. The comment at checks.py:915-918 similarly
narrates what the loop does ("each is tried only after ISO fails") instead of stating only the fact the code
cannot state - that these are Retraction Watch's production export shapes.

Correction to the spec lens: it asserted the commit body "already records it verbatim", which is false. Grepping
the commit body of a53a48b for `rubber`, `SKIPPED-count`, and `acknowledg` returns nothing. The commit body
explains the detection/emission split and the structural inbox unreachability at length, but the
SKIPPED-counting rationale exists *only* in the comment and the test docstring - precisely the inversion the
constraint forbids. The quality lens's conditional therefore fired.

One caveat for the controller: the constraint as both lenses quote it - "Comments and docstrings state
constraints; provenance and rationale belong in the commit body" - is not locatable anywhere in the repo. It is
absent from the batch plan's Global Constraints (docs/superpowers/plans/2026-08-22-post-q-batch.md:14-21),
AGENTS.md, and docs/. It appears to come from the batch's process instructions rather than a checked-in
document. Confirm it is binding before acting; the finding stands or falls with it.

*How to fix.* Trim the __main__.py comment to its constraint clause, cut the argument from the test docstring,
reduce the checks.py comment to the production-shape fact, and move the SKIPPED-counting rationale into the
commit body where the constraint says it belongs (or accept it as a documented amendment).

**3. tests/test_checks.py:1370 - the remediated defect is pinned only at the private-helper level. Status:
NOT-VERIFIED-MINOR.**

Audit defect 1 was reported end to end: production rows silently dropped, `check_rw_batch` returning `None` on a
genuinely retracted DOI. The only guard added exercises `_rw_date` in isolation. The intermediary that actually
drops the rows - `checks.py:954-959`, the `notice_date is _INVALID` branch of `load_rw_csv`'s filter - is still
exercised solely with ISO dates, confirmed by reading the loader. A future change that re-filters rows to ISO at
the loader would leave the new unit test green.

*How to fix.* Change one date in the existing `test_rw_csv_matches_both_identifiers_and_blocking_beats_warning`
fixture CSV (tests/test_checks.py:1379, immediately below the new test) from ISO to `1/2/2023 0:00`. The parsed
value is ISO either way, so no other assertion in that test moves.

**4. research_vault/__main__.py:405 - `not args.rw_csv` re-derives the RW-leg arming predicate that
verify.py:986 owns. Status: NOT-VERIFIED-MINOR.**

The same fact is now encoded in two places. If the leg's arming ever gains a term in verify.py (offline, empty
index, a licence gate), the CLI line would keep asserting the old predicate and report the leg's state
incorrectly - the one thing this line exists to get right. Verified equivalent today: verify.py:986 builds
`notice_lookup` only `if rw_csv`, and `check_rw_batch` runs only when `notice_lookup is not None`. The
alternatives - widening the report contract - are verifiably worse, so this is a note to keep the two in step,
not a call to restructure.

*How to fix.* Leave the code as is; add a short comment at verify.py:986 pointing at __main__.py:405 so the pair
is found together when either changes.

## Refuted During Verification

None. Every finding raised by the three lenses survived adversarial verification, and the one Important finding
survived an independent spot-check during synthesis (SKILL.md:25 and :27 read directly, d44452e's removal of the
id enumeration confirmed, and both non-parsing consumers - the CI verify lane and the publish-gate hook -
checked and cleared). No finding was dropped.

The fidelity lens returned no findings at all; its six strengths are folded into the Strengths section above
where they were not already duplicated.

## Assessment

**Task quality: Needs fixes.**

The code is correct and the spec is met verbatim - the parser fix closes audit defect 1 at the helper level and
the arming line is architecturally incapable of reaching the review queue, which is the constraint that
mattered most. The single Should-Fix is a one-sentence update to `skills/verify-citations/SKILL.md`, whose
documented parsing rule now mis-classifies the new line as an outcome with a phantom check id `RW` on the
skill's own default invocation; the three Minor items are deferrable.
