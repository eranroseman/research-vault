# Task 6 report: import-source references split

BASE: 97afad5. Commit: 8bc6294 `refactor: import-source §7-9 to references with pointer table`
(amended once — see "Fix report" at the end).

## What moved and where

`skills/import-source/SKILL.md`'s three long mode sections moved unchanged into
`skills/import-source/references/`, one file per section, matching find-sources'
pointer-table shape (`skills/find-sources/SKILL.md:43-48`) but not its vendoring
semantics (this is our own prose moved out of our own file — no provenance
header, no upstream commit, no re-vendor language):

- `## 7. Refresh mode: fresh, stale, orphaned` → `references/refresh-mode.md`
- `## 8. Batch mode` → `references/batch-mode.md`
- `## 9. Archive at import (web sources)` → `references/archive-at-import.md`

`SKILL.md` §7 now reads `## 7. Extended modes` with a three-column pointer
table (Need / Verb / Reference file), matching find-sources' three-cell row
shape (Looking-for / Primary / Reference file):

```
| Need                                                 | Verb                 | Reference file                    |
| ----------------------------------------------------- | --------------------- | ----------------------------------- |
| Refresh an existing note — fresh, stale, or orphaned | `import-note`        | `references/refresh-mode.md`      |
| Backfill: refresh every literature note in the vault | `backfill-selectors` | `references/batch-mode.md`        |
| Archive a web source (`url`, no `doi`) at import     | `archive-source`     | `references/archive-at-import.md` |
```

Sections 1–6, "Four-state honesty", and "Routing" are untouched.

## Before/after check-id sweep measurement

Task 3's check-id enumeration sweep (`tests/test_skill_contracts.py`,
`_enumerated_check_ids` / `_known_check_ids`) and the shipped-`finding`-invocation
scan (`_shipped_finding_invocations`) both source their corpus from
`_skill_md_files()`, which globs `skills/*/SKILL.md` only and never reads
`references/`.

**Before** (ran `tsc._enumerated_check_ids()` over the pre-edit
`skills/import-source/SKILL.md`, imported directly from `tests/test_skill_contracts.py`):

```
line 46: 'doi'
line 46: 'metadata'
line 46: 'update-notice'
line 52: 'identifier-discovery'
```

Both lines (46, 52) are in §2 ("Identifier discovery before any SKIPPED
sticks"), which does not move.

**Isolated check**: extracted just the substring for §7–9 (source lines 94–153)
into a scratch file and ran the same extractor over it alone: **zero matches**.
None of the ten backticked tokens the brief flagged as present in §7–9 —
`citekey`, `doi`, `staleness`, `web-archive`, `missing-archive`, `not-admitted`,
`archive-url`, `verify`, `inbox`, `import-note` — meet the sweep's anchoring
rules there:

- No line in §7–9 contains the introducing phrase "check id"/"check ids".
- No backtick run in §7–9 has 2+ members that are already known ids per
  `_known_check_ids()` (the union of `inbox.CHECK_IDS`, `inbox.REPEATABLE_ACT_CHECKS`,
  and the AST-scanned `Outcome(...)` call sites). Checked individually:
  `doi`=True, `citekey`=True, `web-archive`=True, `staleness`=True, but
  `missing-archive`=False, `not-admitted`=False, `archive-url`=False,
  `verify`=False, `inbox`=False, `import-note`=False — none of these five are
  registered/emitted check ids at all (they are reason codes, CLI verb names,
  or field names, not check ids). The one place two *known* ids sit near each
  other, line 102's `` `citekey` / `not-admitted` ``, only has one survivor
  (`citekey`), below the co-occurrence threshold of 2 (`not-admitted` is a
  reason code, not a check id) — so that run was never recognized even before
  the move.

**After** (ran the same extractor over the post-edit `SKILL.md`):

```
line 46: 'doi'
line 46: 'metadata'
line 46: 'update-notice'
line 52: 'identifier-discovery'
```

**Identical to before.** Delta is empty. The pointer table's own cells hold at
most one known id per run (and `|` has not been a run joiner since `de1867d`),
so it creates no new recognized run either.

**Conclusion for the brief's routing question**: the move removes nothing from
the check-id sweep's coverage, because the sweep never recognized any
check-id enumeration inside §7–9 in the first place (the brief's ten flagged
tokens exist in the file's prose, but the sweep's anchoring rules — "check id"
phrase or 2+ known-id co-occurrence in one unbroken backtick run — never fired
on them even pre-move). No prose in `tests/test_skill_contracts.py` overstates
the sweep's corpus as a result of this change; nothing there needed correction.

**Finding-invocation scan**: brief's own pre-check reproduced —
`grep -n "python3 -m research_vault finding "` over the isolated §7–9
substring returns nothing (exit 1). Confirmed independently.

## Byte-preservation check and method

Extracted the pre-edit file via `git show HEAD:skills/import-source/SKILL.md`
(HEAD = 97afad5, before any edit) and sliced out each section's body by exact
line range (heading line and the separating blank line before the next `##`
excluded):

- §7 body: lines 96–106
- §8 body: lines 110–122
- §9 body: lines 126–152

Compared these against the corresponding new reference file with its heading
line and following blank line stripped (`tail -n +3`), first with `diff`
(empty for all three) and then with `sha256sum`:

```
7c05215a...  tmp_orig_body7.md   ==  7c05215a...  tmp_new_body7.md
0e4f06ae...  tmp_orig_body8.md   ==  0e4f06ae...  tmp_new_body8.md
966779884...  tmp_orig_body9.md  ==  966779884...  tmp_new_body9.md
```

All three hashes matched exactly — byte-identical. This check was done AFTER
running the form gate (mdformat), per the risk that the hook could silently
rewrite the new files: mdformat did modify `SKILL.md` (reformatted the new
pointer table's column widths — a table I authored, not moved content) but
left the three reference files byte-for-byte as written; confirmed by
re-reading them post-gate and by the hash comparison above, which was run
against the post-gate tree.

**Adaptation made** (the only edit to moved content): each heading was promoted
from `##` to `#` and had its "7."/"8."/"9." prefix dropped, since a standalone
reference file doesn't carry the parent document's sequence number. Title text
is otherwise verbatim:

- `## 7. Refresh mode: fresh, stale, orphaned` → `# Refresh mode: fresh, stale, orphaned`
- `## 8. Batch mode` → `# Batch mode`
- `## 9. Archive at import (web sources)` → `# Archive at import (web sources)`

No other edit touches moved body text.

## Cross-references

Grepped the whole file for `§` before moving: only `§2`, `§5`, `§6` are cited
(none of which move), and grepped the isolated §7–9 substring for `§`: zero
hits. So no numbered cross-reference needed repointing.

One softer, unnumbered cross-reference survives untouched by design:
`batch-mode.md`'s sentence "the same per-note contract as above" no longer has
an "above" once `refresh-mode.md` is a sibling file rather than the section
immediately preceding it in the same document. I did not edit this — doing so
would violate the byte-preservation requirement, which the brief treats as a
hard constraint (only heading adaptation is sanctioned). I judged it
non-blocking because the same sentence's colon-clause immediately restates the
substance inline ("each note comes back fresh, stale, or orphaned"), so a
reader of `batch-mode.md` alone loses no operative information — only the
literal word "above" is now slightly orphaned. Reported here per the brief's
own instruction to name any cross-reference that now points at a sibling
section in a different file, not treated as a defect requiring a fix.

For navigability, the pointer table's own wording (not part of any moved
content — authored fresh) restates the fresh/stale/orphaned vocabulary and the
word "Backfill" in its two relevant rows, so a reader can find refresh mode
from either the frontmatter description's words ("refresh, or backfill") or
the table row text, without needing to already know the reference file names.

## Existing pins (tests/test_import_source_skill.py)

Both tests read `SKILL.md` text and assert only:

- `test_import_source_says_it_needs_no_project`: `"No project is required"`,
  `"project-independent"`, `"zero projects"` — all in the file's line 11 area
  (unmoved intro prose).
- `test_import_source_says_where_to_read_the_citekey_after_admission`:
  `"Citation Key"`, `"Better BibTeX"` — both in line 13 (unmoved intro prose).

Neither string appears in §7–9. Confirmed by reading the moved sections; both
pins are unaffected and stayed green through the full suite run below. No
contradiction to resolve — the brief's "stop if one does" condition did not
trigger.

## What was tested

1. `.venv/bin/python -m pytest tests -q` before any edit (via `git stash -u`),
   to reconfirm the stated baseline: **1562 passed, 7 skipped**. Matches the
   brief's stated BASE exactly.
2. `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` after the
   move: 7/8 on first run (mdformat rewrote `SKILL.md`'s new table only); 8/8
   on the immediate re-run, tree otherwise clean.
3. `.venv/bin/python -m pytest tests -q` after the move and after the form
   gate: **1565 passed, 7 skipped**.

## The +3 delta, explained

1565 vs. the 1562 baseline is **not** related to the check-id sweep or the
finding-invocation scan (both are unchanged, as measured above). Diffing
`--collect-only` output before/after identified the exact three new test IDs:

```
tests/test_config_validity.py::test_markdown_table_rows_have_no_truncated_code_spans[archive-at-import.md]
tests/test_config_validity.py::test_markdown_table_rows_have_no_truncated_code_spans[batch-mode.md]
tests/test_config_validity.py::test_markdown_table_rows_have_no_truncated_code_spans[refresh-mode.md]
```

This is a *different*, pre-existing instrument (`_mdformat_owned_markdown()` in
`tests/test_config_validity.py`) that globs `skills/**/*.md` recursively rather
than `SKILL.md` only, so it automatically picked up the three new reference
files and parametrized over them. All three pass cleanly (no escaped-backtick
table-truncation signature) — a useful confirmation that the two tables moved
into `refresh-mode.md` and `archive-at-import.md` survived mdformat intact,
consistent with the byte-preservation check above. No test or scan lost
coverage; one unrelated instrument gained three parametrizations it was
already designed to run over anything under `skills/`.

## Files changed

- `skills/import-source/SKILL.md` (modified — §7 replaced with pointer table)
- `skills/import-source/references/refresh-mode.md` (new)
- `skills/import-source/references/batch-mode.md` (new)
- `skills/import-source/references/archive-at-import.md` (new)

## Self-review

1. **Is the pointer table genuinely navigable?** Yes — three rows, each naming
   the need in the reader's own words (refresh/fresh/stale/orphaned; backfill;
   archive a web source with `url`/no `doi`) alongside the `references/<file>.md`
   path. A reader arriving from the frontmatter description ("import, catalog,
   refresh, or backfill") lands on the matching row without prior knowledge of
   the file layout.
2. **Cross-references into a now-different file?** Covered above: no numbered
   (`§N`) cross-reference broke; one prose cross-reference ("as above" in
   batch-mode.md) is now structurally orphaned but not operatively broken, left
   as bytes per the byte-preservation constraint, and reported rather than
   silently accepted.
3. Confirmed no stray temp files were swept into the commit
   (`git status --short` clean before and after `git add`).

## Concerns

None blocking. One item carried forward for whoever routes cross-task
findings: the "as above" orphaned cross-reference in `batch-mode.md` (see
above) is intentionally left as-is; if a future pass wants it repointed, that
would be a body-text edit outside this task's byte-preservation mandate and
should be scoped as its own change.

## Fix report (self-caught before the reviewer round)

Before declaring done I called `advisor()`, which caught a real defect in the
first commit's body: it claimed a "three-column pointer table" while the
shipped table (`| Need | Reference file |`) was two columns — a false,
checkable claim in an about-to-be-immutable commit body, the exact class of
issue Task 4 was held to Important for in this same plan.

Fix applied: added a `Verb` middle column to the pointer table, naming the CLI
verb each mode uses (Refresh → `import-note`, Backfill → `backfill-selectors`,
Archive → `archive-source`), making the table genuinely three-column and
matching find-sources' row shape (purpose / target / reference file) literally
rather than by number alone.

Re-verification commands and results, in the order the advisor specified (form
gate first, since mdformat can rewrite the table; then the after-measurement;
then the full suite; then amend):

```
$ PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files
  form: markdown CommonMark (mdformat).....................................Failed  (rewrote column widths)
$ PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files   # re-run
  ...all 8 hooks Passed, no files modified
```

```
$ .venv/bin/python <script importing tests/test_skill_contracts.py, running
  tsc._enumerated_check_ids() over the edited SKILL.md>
AFTER (3-col table): enumerated (line, token) pairs in edited SKILL.md:
  line 46: 'doi'
  line 46: 'metadata'
  line 46: 'update-notice'
  line 52: 'identifier-discovery'
  'import-note' in known_check_ids: False
  'backfill-selectors' in known_check_ids: False
  'archive-source' in known_check_ids: False
```

Identical to both the original before- and after-measurements: the new `Verb`
column adds no new recognized run (each cell is a single backticked token, and
none of the three verbs is a registered or emitted check id, so the
co-occurrence anchor cannot fire even in principle).

```
$ .venv/bin/python -m pytest tests -q
1565 passed, 7 skipped in 95.72s
```

Same 1565/7 as before the table fix — no new `.md` files were added, so no new
parametrizations; the `test_markdown_table_rows_have_no_truncated_code_spans`
count is unaffected since it parametrizes over files, not table columns.

Then `git commit --amend -F <corrected message>` (branch tip, not yet pushed,
so amend is clean — no shared history rewritten). New SHA: `8bc6294`. Commit
body corrected to say "three-column" truthfully and to note the pointer
table's cells were separately checked against the sweep. This report's own
quoted SHA and table snippet were updated to match in the same pass.

`git status --short` clean; `git log --oneline -3` shows a single commit on
top of BASE 97afad5, as required.
