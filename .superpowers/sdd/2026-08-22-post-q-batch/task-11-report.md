# Task 11 report: Free-region destruction fix (item 18, audit defect 5)

## Status

Complete. All 4 steps (failing tests, implementation, spec edit, full suite)
done; full suite green; every new behaviour shown to discriminate (red under
the targeted mutation, green after).

## Commit

`1501d9c` — `fix: refuse import over a marker-less note — never reseed the free region`

Files: `knowledge_harness/notes.py`, `tests/test_notes.py`,
`tests/test_cli_live.py`, `docs/superpowers/specs/2026-08-16-foundation-spec.md`
(4 files, +61/-3).

## Test summary

`python -m pytest -q`: **1709 passed, 7 skipped** (baseline 1705 passed / 7
skipped + 4 new tests). `ruff check` / `ruff format --check` / `mypy
knowledge_harness/` clean on every touched file. Form gate
(`echo '{}' | python hooks/stop_publish_gate.py`) silent, exit 0.

## What was implemented

- `knowledge_harness/notes.py::_split_free`: the guard changed from
  `if existing is None` to `if not existing`, so both `None` and `""` still
  seed `SEED_FREE` in one explicit first branch (the controller's fact 4 —
  a zero-byte file on disk is the real-world source of the empty-string
  case). The prior bare `return SEED_FREE` fallthrough — reached whenever no
  line matched the exact standalone `%%/hk-managed%%` close marker — now
  raises `RenderIntegrityError("existing note has no managed-close marker —
  refusing to overwrite the body")` instead. No other line in `_split_free`
  or its one caller (`render_note`, `notes.py:269`) changed.
- `docs/superpowers/specs/2026-08-16-foundation-spec.md:90`: the §5
  Invariants sentence now states never-delete also covers the free region,
  surgically inserted into the existing single-line paragraph without
  reflowing surrounding text.
- No change to `knowledge_harness/__main__.py`: its
  `except (notes.RenderIntegrityError, notes.InvalidCitekeyError,
  frontmatter.FrontmatterError)` in `cmd_import_note` (lines 278-296)
  already routes any `RenderIntegrityError` — including this new one — to
  `render rejected for <citekey>: <error>` on stderr, a `render` /
  `UNMATCHED` / `schema-violation` hold via `_hold`, and exit 1. This was
  verified to actually fire (see the integration test below), not assumed
  from reading the code.

## Verified before implementing (brief's "verify, don't trust the parenthetical")

Ran the new unit test (`test_existing_note_without_marker_refuses_render`)
and the new CLI-level test against the pre-fix code: the unit test failed
with `Failed: DID NOT RAISE RenderIntegrityError`, and the CLI test failed
with `assert 0 == 1` — i.e. a marker-less existing note was silently
re-seeded and `cmd_import_note` returned 0 (success), confirming the brief's
"silently replaced by `SEED_FREE` today, printed as success" claim against
the actual tree rather than trusting the text.

## Per-test discrimination matrix

| Test | Behaviour targeted | Pre-fix (red) | Post-fix (green) | Discriminating mutation |
|---|---|---|---|---|
| `test_notes.py::test_existing_note_without_marker_refuses_render` | new raise on marker-less fallthrough | `Failed: DID NOT RAISE RenderIntegrityError` | passes; message matched with an anchored `^...$` regex so it cannot be satisfied by the *other* `RenderIntegrityError` site (`notes.py:281`, managed-body parse mismatch) | Reverting the whole fix (`git stash push -- knowledge_harness/notes.py`) → red. Confirmed. |
| `test_notes.py::test_fresh_note_still_seeds[none]` | `existing=None` still seeds, no raise | already green pre-fix (pre-existing behaviour, unchanged) | green | No single-line mutation of this change makes it fail — `None` was always caught by the original `is None` branch and still is under `not existing`. This is a regression guard, not new-behaviour discrimination; reported honestly rather than left blank. |
| `test_notes.py::test_fresh_note_still_seeds[empty-string]` | `existing=""` still seeds, no raise | already green pre-fix (the accidental fallthrough the brief's fact 4 warns about — `"".splitlines()` → `[]` → bare `return SEED_FREE`) | green | Intermediate mutation targeting exactly fact 4's hazard: guard reverted to `if existing is None` while the fallthrough raise was kept. Under that state `[empty-string]` goes **red** (`RenderIntegrityError` raised for `existing=""`) while `[none]` stays green — proving the `not existing` guard (not just the raise) is load-bearing. Restored; suite reconfirmed green. |
| `test_cli_live.py::test_import_note_marker_less_existing_note_refuses_and_files_hold` | end-to-end wiring: a **real** marker-less note on disk (not a monkeypatched `render_note`) reaches `cmd_import_note`'s existing catch/hold path | `assert 0 == 1` (silent success, file "imported") | passes: exit 1, destination file byte-identical before/after, stderr matches the exact `render rejected for smith2020: existing note has no managed-close marker — refusing to overwrite the body` line, and the filed hold asserts `check == "render"`, `target == "smith2020"`, `result == "UNMATCHED"`, and `reason ==` the full `schema-violation — <message>` string (equality, not `startswith`, so it can't pass on a different schema-violation hold) | Reverting the whole fix → red (`assert 0 == 1`). Confirmed. This is the only new test in the suite that exercises the real renderer un-mocked through the CLI; every existing `RenderIntegrityError`-in-`cmd_import_note` test monkeypatches `notes.render_note` directly and so never proved the new raise itself reaches the handler. |
| `test_notes.py::test_free_region_byte_exact` (pre-existing, named in brief's Step 5) | byte-exact free-region preservation when a marker *is* present | green before this change | still green, unmodified | N/A — pre-existing regression guard, confirmed still passing, not touched. |

## Blast-radius check (second verification, not the same grep twice)

`grep -rn "_split_free" . --exclude-dir=.git` (unscoped by extension, unlike
the controller's `knowledge_harness/`+`tests/`-scoped grep) finds exactly one
caller: `render_note` at `notes.py:269`. The only other hits are prose
(planning docs, product-landscape research notes) and
`notes.py.manifest.json`'s mutation-manifest sidecar entry — no second
functional caller.

`grep -rn "render_note(" knowledge_harness/` finds exactly one production
caller: `knowledge_harness/__main__.py:270`, inside `cmd_import_note` — the
only place a marker-less note now inherits the new raise. `backfill_selectors`
and `verify` (the other two commands that read note bytes from disk) do not
call `render_note`, so they are unaffected by this change.

## Deviation from the brief's file list

The brief lists `tests/test_import_note.py` as a target test file; that file
does not exist in this tree. The existing render-rejection/hold tests for
`cmd_import_note` live in `tests/test_cli_live.py` (see
`test_import_note_render_rejection_files_a_hold` and its neighbours,
`tests/test_cli_live.py:1350-1505`), so the new end-to-end wiring test was
added there, colocated with the tests it extends, rather than creating a new
file. Flagging this for the controller's awareness rather than silently
resolving the naming mismatch.

## Concerns (each with a destination)

- **Pre-existing, unrelated lint failures elsewhere in the tree.**
  `ruff check .` (10 errors) and `ruff format --check .` (5 files) fail on
  `skills/find-sources/scripts/*.py` — files this task never touched (not in
  `git status --porcelain` for this branch's diff). All four files this task
  modified (`knowledge_harness/notes.py`, `tests/test_notes.py`,
  `tests/test_cli_live.py`, plus the spec markdown, which `ruff` doesn't
  format without preview mode) pass `ruff check` / `ruff format --check`
  clean when scoped directly. Destination: controller — out of scope for a
  surgical commit on this task, left unfixed.
- **`pre-commit run --all-files` was not run**, per the explicit
  instruction not to (it stashes unstaged changes onto a shared stash stack,
  and the controller's `progress.md` is routinely dirty). Destination:
  controller — if a gate needs it, the controller runs it.
- **No merge to `main` / push to origin performed.** AGENTS.md's global
  instruction to "merge back to main locally and push main to origin in the
  same motion" was not applied here; this worktree branch
  (`fix/pre-slice-batch`) already carries several other tasks' commits ahead
  of it, and integration appeared to be the controller's/batch's job rather
  than this single task's. Destination: controller — confirm whether this
  task should have merged, or whether batch integration happens once at the
  end.
