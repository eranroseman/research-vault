# Task 10 report: two-tier citekey check (audit item 17, spec §4)

## RED evidence

Command:

```
.venv/bin/python -m pytest tests/test_checks.py -k "test_cited_citekey" -q
```

Output (before the fix, tests already written against the unmodified
`check_citekeys`):

```
F..                                                                      [100%]
=================================== FAILURES ===================================
_________________ test_cited_citekey_requires_literature_note __________________

    outs = checks.check_citekeys(tmp_vault, note, {"smith2020": {}})

    assert len(outs) == 1
>   assert outs[0].result is Result.UNMATCHED
E   AssertionError: assert <Result.MATCHED: 'MATCHED'> is <Result.UNMATCHED: 'UNMATCHED'>
E    +  where <Result.MATCHED: 'MATCHED'> = Outcome(check='citekey', target='smith2020',
E       result=<Result.MATCHED: 'MATCHED'>, reason='matched', ...).result

1 failed, 2 passed, 119 deselected in 2.96s
```

This is the expected failure and only the expected failure. Contrary to the
outer task prompt's framing ("confirm the first two fail"), the brief's own
test shapes only fail one of the three: `test_cited_citekey_requires_literature_note`
is the sole RED case, because today's `check_citekeys` grants MATCHED on
bibliography membership alone (`smith2020` is in the passed-in
`bibliography_universe`, no `literatures/smith2020.md` exists, and the old
code never looked). `test_cited_citekey_with_note_passes` and
`test_cited_citekey_absent_everywhere` both describe *today's* behavior
("MATCHED as today" / "existing mismatch reason") and pass unmodified before
any implementation change — they are pins, not RED cases. Confirmed by the
run above: `1 failed, 2 passed`. The failure is on the assertion itself (a
value mismatch: MATCHED where UNMATCHED is expected), not a fixture/setup
error, confirming the test exercises today's defect rather than a broken
research-vault.

## GREEN evidence

Targeted:

```
.venv/bin/python -m pytest tests/test_checks.py -k "test_cited_citekey or citekey_check" -q
```

```
.......                                                                  [100%]
7 passed, 115 deselected in 0.20s
```

(3 new tests + 4 pre-existing `check_citekeys` tests, all green.)

Enforcement surfaces:

```
.venv/bin/python -m pytest tests/test_config_validity.py tests/test_skill_contracts.py -q
```

```
........................................................................ [ 38%]
........................................................................ [ 77%]
...........................................                              [100%]
187 passed in 5.90s
```

Full offline suite:

```
.venv/bin/python -m pytest tests -q
```

```
1575 passed, 7 skipped in 92.70s (0:01:32)
```

(Baseline at BASE was 1572 passed, 7 skipped; delta is exactly +3, the three
new tests. No test count regressed or was removed.)

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

8/8. (First run flagged `mdformat` because my hand-edited table rows weren't
column-padded; let it auto-fix, then reran clean — did not hand-align.)

## Citation case vs. note-identity case

`check_citekeys` (`research_vault/checks.py:131`) builds its `cited` set
purely from `claims.CITE_RE.finditer(note_text)` on the checked note's raw
body — there is no separate frontmatter-driven "note identity" branch
anywhere in the function; every row in the per-citekey loop is structurally
a citation.

The "note's own citekey row" the brief warns about is a *specific instance*
of that same citation loop, not a different code path: a literature note's
own managed body self-cites its own subject. `notes.render_claim`
(`research_vault/notes.py:302-310`) renders every claim as
`[@{citekey}, p. {page}]` where `citekey` is the item's own id
(`notes.render_note`, `research_vault/notes.py:217`,
`fm = {"citekey": item["id"], ...}`), and literature notes are always
written to `literatures/{citekey}.md` (`notes.note_path`,
`research_vault/notes.py:118-129`). The fixture vault demonstrates this
directly: `literatures/smith2020.md` contains `[@smith2020, p. 12]` and
`[@smith2020, p. 3]` in its own managed region
(`tests/conftest.py:52-58`). `verify.py:981-985` calls `file_outcomes` (and
therefore `check_citekeys`) over every file under `literatures/`,
`synthesis/`, and `projects/`, so this self-citation row really is checked
in production.

Given that, I did not special-case the self-citing row. The new tier-2
existence check is `(vault / "literatures" / f"{citekey}.md").is_file()`,
applied uniformly to every row in the loop. When `check_citekeys` runs on
`literatures/smith2020.md` itself, the self-citation row's citekey is
`smith2020`, and the path it checks — `literatures/smith2020.md` — is
exactly the file that was just `read_text()`-ed to build `cited` in the
first place. Existence there is a structural invariant, not a coincidence:
the note being checked cannot itself be absent, so the tier-2 branch is a
no-op for that row and the "note-vs-bibliography identity" case keeps its
old bibliography-membership-only semantics automatically, with no
if/branching needed to separate the two "cases." Confirmed live (not just
argued) — see Self-review below.

## Implementation

`research_vault/checks.py`, per-citekey loop:

```python
for citekey in cited:
    if citekey not in bibliography_universe:
        result = Result.UNMATCHED
        reason = "mismatch — citekey not in bibliography"
    elif not (vault / "literatures" / f"{citekey}.md").is_file():
        # Tier 2: bibliography membership alone is not citability — the
        # cited source needs an imported literature note to verify a
        # quote or paraphrase against.
        result = Result.UNMATCHED
        reason = "not-imported — cited citekey has no literature note"
    else:
        result = Result.MATCHED
        reason = "matched"
```

Path construction (`vault / "literatures" / f"{citekey}.md"`, `.is_file()`)
matches the existing convention for this exact lookup elsewhere in the
codebase (`research_vault/lints.py:491`, `research_vault/factcheck.py:73,90`)
rather than routing through `notes.note_path()`, which raises
`InvalidCitekeyError` for unsafe input — a check function should stay total,
and every citekey reaching this loop already passed `claims.CITE_RE`'s safe
charset (`[A-Za-z0-9_.:-]+`), so the exception path was never reachable
here.

I checked `research_vault/outcome.py` before writing any test: `Outcome`'s
`__post_init__` defers to `inbox.validate_reason` (imported locally to break
a cycle — `inbox` itself imports `outcome` for `Result`), so there is no
second, independent reason-code vocabulary anywhere else to update. One
registration site.

## Dialect surfaces the two enforcement tests flagged

Registered `not-imported` in `research_vault/inbox.py`'s `REASON_CODES`
first, then ran the full suite to let the two mechanically-enforced surfaces
name themselves rather than guessing:

- `tests/test_config_validity.py::test_every_reason_code_at_head_is_governed`
  (line 167 asserts `inbox.REASON_CODES - _backticked(governance_row)` is
  empty) failed: `not-imported` had no backticked entry in
  `docs/terminology.md` §4.4's "reason codes" row. Fixed by adding
  `` `not-imported` `` to the row's enumeration (alphabetically after
  `` `not-admitted` ``) and a "Task 10 adds `not-imported`: ..." provenance
  clause matching the row's existing per-task style, naming the distinction
  from `not-admitted` explicitly (in-Zotero-but-not-imported vs.
  never-admitted-to-Zotero).
- `tests/test_skill_contracts.py::test_evidence_conventions_accounts_for_every_reason_code`
  (line 487 asserts `tabled | exempt == inbox.REASON_CODES`) failed:
  `not-imported` was in neither the table nor the closing exemption
  sentence. Fixed by adding a new table row to
  `skills/evidence-conventions/SKILL.md`'s "Reason-code vocabulary" section,
  directly under `` `not-admitted` ``, stating the same distinction. I did
  **not** touch the closing sentence ("One registry code stays off this
  table: `matched` ...") or its "One" count word — `not-imported` reaches
  the review queue (it is a real UNMATCHED finding, unlike `matched`), so it
  belongs in the table, not the exemption set, and the exemption set stays
  `{matched}` exactly as before.

I did not add `not-imported` to the exemption list at any point — it was
never a candidate: unlike `matched`, a `not-imported` finding is a genuine
UNMATCHED result that files to the review queue, so exempting it would have
been asserting something false about the finding, not documenting a
registry fact.

Both enforcement tests, plus the full `test_config_validity.py` and
`test_skill_contracts.py` files, are green after these two edits (see GREEN
evidence above).

## Tests that pinned the old (defective) behavior

None found in the full-suite triage. After registering the reason code and
before touching either doc surface, the full suite (`1573 passed, 2 failed`)
showed exactly the two enforcement failures above and nothing else — no
other test anywhere in the suite asserted single-tier MATCHED for a
bibliography-present/note-absent citekey. `tests/test_checks.py`'s
pre-existing `check_citekeys` tests (`test_citekey_check_matches_and_...`,
`test_citekey_check_skips_a_note_with_no_citations`,
`test_citekey_check_scans_citations_in_non_claim_prose`,
`test_citekey_check_deduplicates_repeated_citations`,
`test_citekey_outcome_carries_claim_line_origins`) all use `fixture_vault`,
whose only cited-and-bibliography-present citekeys (`smith2020`,
`prose-only2024` is *not* in the bibliography) already have a real
`literatures/*.md` note (`smith2020.md`) or are absent from the bibliography
entirely (`fabricated2020`, `prose-only2024`) — none of them exercised the
bibliography-present-but-note-absent case the old code got wrong, so none
needed updating.

## Files changed

- `research_vault/checks.py` — `check_citekeys`'s per-citekey loop now
  branches three ways (bibliography-absent / bibliography-present-but-note-absent
  / both-present) instead of two; new `not-imported` UNMATCHED branch; inline
  comment states only the tier-2 constraint, not its provenance.
- `research_vault/inbox.py` — `REASON_CODES` gains `"not-imported"`,
  inserted alphabetically after `"not-admitted"`.
- `docs/terminology.md` — §4.4's "reason codes" row: `` `not-imported` ``
  added to the enumeration; a "Task 10 adds..." provenance clause appended
  in the row's existing style.
- `skills/evidence-conventions/SKILL.md` — new table row for `` `not-imported` ``
  in the "Reason-code vocabulary" section, directly under `not-admitted`.
- `tests/test_checks.py` — three new tests, verbatim from the brief's
  shapes: `test_cited_citekey_requires_literature_note` (RED case),
  `test_cited_citekey_with_note_passes`, `test_cited_citekey_absent_everywhere`
  (both pins of unchanged behavior, per the brief's own annotations).

## Self-review

- Note's own citekey row still behaves as before: confirmed live with a
  throwaway test using `fixture_vault` (written to
  `tests/test_self_review_scratch.py`, run, then deleted — not part of the
  commit). `checks.check_citekeys(fixture_vault, fixture_vault /
  "literatures" / "smith2020.md")` returns the `smith2020` row as
  `Result.MATCHED`, reason `"matched"` — unchanged from before this task.
  `literatures/gone2019.md` (a literature note with no self-citing claims in
  its managed body) still returns the single `SKIPPED` /
  `"no-identifier — note cites nothing"` outcome, also unchanged.
- Third brief test (`test_cited_citekey_absent_everywhere`) reports the
  existing mismatch reason, not the new one: confirmed — it asserts
  `outs[0].reason == "mismatch — citekey not in bibliography"` exactly, and
  passed both before and after the implementation change (it's a pin, per
  the RED evidence above), because the bibliography-absent branch is checked
  first and short-circuits before the new tier-2 branch is ever reached.
- Signature unchanged: `check_citekeys(vault_root, note_path,
  bibliography_universe=None)` — confirmed by inspection of the diff, no
  parameter added or removed.
- `not-imported` kept distinct from `not-admitted`, not merged or aliased:
  confirmed — two separate strings in `REASON_CODES`, two separate table
  rows/enumeration entries, each stating its own distinguishing condition
  (never-in-Zotero vs. in-bibliography-but-not-imported).

## Concerns

None. The change is scoped to one branch inside one loop, both
mechanically-enforced dialect surfaces are satisfied without touching the
`matched` exemption, no existing test pinned the defect, and the full suite
plus form gate are green.
