# Task 12 report: Duplicate-anchor render assert (item 19, claim-anchor audit)

Disposition: historical (2026-09-06)

## Status

Complete. Both failing tests (Step 1 identical-text, Step 1b keyless-empty-text)
written and confirmed red for the right reason before implementing; the
one-line uniqueness check from the brief implemented verbatim, placed before
the `parsed != expected` comparison; full suite green; every new test proven
to discriminate against each of the other two `RenderIntegrityError` sites,
not just against "no exception."

## Commit

`fix: render refuses duplicate claim anchors`

Files: `research_vault/notes.py`, `tests/test_notes.py`,
`tests/test_cli_live.py` (3 files, +80/-6). Report file included in the same
commit per instruction; `.superpowers/sdd/2026-08-22-post-q-batch/progress.md`
excluded (controller-owned).

Refs [#16](https://github.com/eranroseman/knowledge-harness/issues/16).

## Test summary

`python -m pytest -q`: **1714 passed, 7 skipped** (baseline 1709 passed / 7
skipped + 5 new tests in `test_notes.py`). `ruff check` / `ruff format --check`
/ `mypy research_vault/` clean on every file this task touched. Form gate
(`echo '{}' | python hooks/stop_publish_gate.py`) silent, exit 0.

## What was implemented

`research_vault/notes.py::_assert_managed_body_parses` (notes.py:272-286)
now computes `expected` and immediately checks `len(set(expected)) !=
len(expected)` before computing `parsed` or reaching the `parsed != expected`
comparison:

```python
expected = [claim_id(annotation) for annotation in annotations]
if len(set(expected)) != len(expected):
    raise RenderIntegrityError(f"duplicate claim anchors in render: {expected!r}")
parsed = [...]
if parsed != expected:
    raise RenderIntegrityError(...)
```

This is the brief's Step 3 code exactly, placed ahead of the parse-back
comparison (controller fact 3) so a duplicate is reported as a duplicate,
not misdiagnosed as a parse mismatch — with both conditions able to be true
simultaneously for duplicated input, only the first now fires.

`expected` is a `list[str]` (`claim_id` always returns `"c-" + hex8`), so
`set(expected)` never touches an unhashable element (controller fact 2).

## Verified before implementing (brief's "verify, don't trust the parenthetical")

Ran both new scenarios against the pre-fix code by hand:
- Two annotations with `key=None` and identical `annotationText`: render
  **succeeded silently**, both claims got `^c-9275856d`.
- Two `key=None` annotations with `annotationText=""` and different
  comments: render **succeeded silently**, both claims got `^c-e3b0c442`
  (confirmed `sha256(b"").hexdigest()[:8] == "e3b0c442"`).

Both confirm the brief's claim: `parsed != expected` is `False` when both
lists carry the identical duplicate, so no exception fires at all — not a
wrong-message failure, a **no-exception** failure.

## Per-test discrimination matrix

| Test | Pre-fix (today's blind check) | Fix present but message forced to site 1's text | Fix present but message forced to site 2's text | Real fix (green) |
|---|---|---|---|---|
| `test_duplicate_anchors_refuse_render` | `Failed: DID NOT RAISE RenderIntegrityError` | `AssertionError`: got `existing note has no managed-close marker …`, anchored regex expected `duplicate claim anchors in render: [...]` | `AssertionError`: got `managed body parsed to [...], expected [...]`, anchored regex rejects it | passes |
| `test_duplicate_keyless_empty_text_anchors_refuse_render` | `Failed: DID NOT RAISE RenderIntegrityError` | same as above, rejected | same as above, rejected | passes |

Procedure: removed the uniqueness check entirely (row 1, confirms Step 2's
"Run — Expected: FAIL" against the *right* cause, not a stand-in bug);
restored it but swapped its message for the marker-less-fallthrough site's
exact string (row 2); swapped again for the `managed body parsed to …`
site's format (row 3); restored the brief's exact code (row 4). Each
intermediate state was run through `pytest -k "duplicate_anchors or
duplicate_keyless" -v` and produced the exact failures tabulated above — a
bare `pytest.raises(notes.RenderIntegrityError)` would have incorrectly
passed in rows 2 and 3; the anchored `match=` regex (built from
`re.escape(f"duplicate claim anchors in render: {[cid, cid]!r}")`, anchored
`^...$`) correctly failed both. This is the same substitution technique
Task 11's review required (controller fact 5).

## No-false-positive construction (not reasoning)

Two additional tests, run against the real fix, both green:
- `test_distinct_keyed_annotations_still_render`: `QUOTE_ANN` (key
  `ANNKEY01`) and `COMMENT_ANN` (key `ANNKEY02`) in one `render_note` call —
  distinct anchors, no exception, both anchors present in the output.
- `test_distinct_keyless_annotations_still_render`: two `key=None`
  annotations with genuinely different `annotationText` — distinct anchors,
  no exception, both present in the output.

A third test, `test_parse_mismatch_still_raises_when_anchors_are_unique`,
proves the new check does not shadow the pre-existing `parsed != expected`
guard: it monkeypatches `claims.parse_claims` to corrupt one parsed claim_id
while rendering a single (non-duplicated) annotation, and confirms the
original `managed body parsed to [...], expected [...]` message still fires.
This raise site had **zero direct test coverage before this task** — none of
the 1709 baseline tests exercised it — so this is new coverage, not a
regression guard.

## Unplanned but necessary: two `tests/test_cli_live.py` fixtures fixed

Running the full suite with the fix in place turned up two failures outside
the brief's file list:
`test_import_note_applies_extracted_text_only_to_its_attachment` and
`test_import_note_reports_unresolved_attachment_in_mixed_extraction`. Both
build a note from two `_raw_quote(...)` results with different
`annotationText` but the shared helper hardcoded `"key": "ANNKEY01"` for
every call. `claim_id` prefers `key` over text (`key or _norm(text)`), so
both annotations collided on the identical anchor — a second, real instance
of exactly the defect this task closes, previously masked by the same
`parsed != expected` blindness and now (correctly) caught.

This was a latent bug in the test fixtures, not a synthetic edge case: real
Zotero/Better BibTeX annotation keys are unique per annotation, so two
different highlights never legitimately share one. Fixed by giving
`_raw_quote` an optional `key` parameter (default `"ANNKEY01"`, preserving
every other call site's existing behaviour — checked: only these two tests
ever combine two `_raw_quote()` results in one render) and passing distinct
keys (`ANNKEY01`/`ANNKEY02`) at the two colliding call sites. The advisor
tool was unavailable when I reached this decision point ("temporarily
overloaded"); I proceeded on the reasoning above — eliminate the actual
problem (a fixture that fakes colliding identity) rather than weaken the new
invariant to tolerate it — and flag it here for the controller to confirm or
override.

## Issue #16

Believed **fully closed** by this commit. The issue's title, reproduction,
and proposed fix are all satisfied verbatim: both reproduction cases in the
issue body (`a`/`b` identical-text keyless collision, `c`/`d` empty-text
keyless collision) now raise `RenderIntegrityError` before the note reaches
disk, via the exact code the issue proposed. The check is not scoped to
keyless annotations specifically — it flags any claim_id collision, keyed or
keyless — which is what caught the `test_cli_live.py` fixture bug (a *keyed*
collision) as a bonus, going beyond the issue's literal title. Not closed by
me per instruction; left for the controller.

## Concerns (each with a destination)

- **Pre-existing, unrelated lint failures elsewhere in the tree.**
  `ruff check .` (10 errors) and `ruff format --check .` (5 files) fail on
  `skills/find-sources/scripts/*.py` — files this task never touched (not in
  `git status --porcelain` for this branch's diff). All three files this
  task modified pass `ruff check` / `ruff format --check` clean when scoped
  directly. Destination: controller — out of scope for this commit, left
  unfixed, same finding Task 11 reported.
- **`pre-commit run --all-files` was not run**, per the explicit instruction
  not to (shared stash stack). Destination: controller — if a gate needs it,
  the controller runs it.
- **Advisor tool was unavailable** at the one point I most wanted a second
  opinion (whether to fix the `test_cli_live.py` fixtures or treat them as
  out of scope). Proceeded on my own judgment, documented above under
  "Unplanned but necessary." Destination: controller — please confirm this
  was the right call; the alternative would have been leaving two tests red
  or weakening the new check, both worse.
- **No merge to `main` / push to origin performed.** Same disposition as
  Task 11's report: integration appears to be the controller's/batch's job.
  Destination: controller — confirm whether this task should merge
  individually or as part of batch integration.
