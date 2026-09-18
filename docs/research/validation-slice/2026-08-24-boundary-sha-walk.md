# Part 1 / Part 2 boundary — SHA-walk re-run

Disposition: historical (2026-09-06)

Independent reviewer, read-only pass, 2026-08-24. Re-run of the coverage walk commissioned at
`bd64dcb`, now that the boundary merge has landed. Measured at `fix/pre-slice-batch` tip
`8ed31c5`, against `origin/main` at `bd64dcb`. Baseline to beat: **22 commits / 4 uncovered**
at `1ed029c`. Method as before — resolve every SHA the ledger names, walk the claimed ranges in
code, diff the covered set against the branch-authored set. Nothing was modified.

## Result: 27 / 9 uncovered — not N/0, and the reason is nameable

Every SHA-like token in progress.md still resolves: **56 of 56, zero phantoms.** Twelve
completion lines, same as at `1ed029c` — none were added for the five commits that have landed
since. The uncovered set splits cleanly in two, and only one half is a gap.

**Structurally uncoverable by a task range (4) — expected, no action:**

| Commit    | Why                                                                                                                           |
| --------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `7abe69b` | Controller's Part 3 amendment, later reverted. Already explained in the ledger's own integrity audit as the sole chain break. |
| `f51990c` | The boundary merge itself. No task range can claim a merge commit.                                                            |
| `d5fa7d2` | `chore: mdformat Plan W` — form-owner pass.                                                                                   |
| `8ed31c5` | The checkbox backfill. Controller commit.                                                                                     |

**Task work awaiting a completion line (5) — the real gap:**

| Commit    | Owed                                                                             |
| --------- | -------------------------------------------------------------------------------- |
| `cc8f916` | Task 2d, landed, review returned NEEDS FIXES.                                    |
| `91dfa70` | Task 9 addendum. Reviewed and cleared 2026-08-24; line not yet written.          |
| `1ed029c` | Task 4 addendum. Same.                                                           |
| `efa6b77` | Task 2d's fix round. **Not mentioned in progress.md at all** (`grep` returns 0). |
| `76c3137` | The `oldest_age_days` wiring. **Not mentioned in progress.md at all.**           |

So the count rose from 4 to 9 because five more commits landed and the ledger did not follow
them. Two of the five are not merely unclaimed by a range — they are absent from the file. The
recovery map's own contract is that the commits it names must exist in git; the converse, that
commits in git must appear in the map, is where it is now short. Writing five completion lines
returns the figure to 27/4, which is N/0 for the coverable set.

## Verified against the tree

Every claim relayed at the boundary was checked, not accepted.

| Claim                                     | Verdict                                                                                                                                                                                                   |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Merge at `f51990c`, backfill at `8ed31c5` | Both resolve. Merge 13:10:43, backfill 13:12:11.                                                                                                                                                          |
| "38 boxes across the twelve tasks"        | **Exact.** `8ed31c5` flips 38 `- [ ]` to `- [x]`; 38 insertions / 38 deletions, one file.                                                                                                                 |
| "72 remain"                               | **71.** Off by one. Tip reads 71 unchecked / 41 checked (38 flipped + Task 8b's 3 pre-existing = 41). The §3.2 finding is closed either way.                                                              |
| XML clause corrected                      | **Closed.** `skills/find-sources/SKILL.md:23` now reads "no *external* entity expansion — internal entities do expand, which is the class the next clause hedges". The Important is discharged.           |
| Task 1's rename survived the merge        | **Confirmed.** `docs/terminology.md:125` carries `project-flow`; no bare `project` skill reference remains. The wholesale-theirs hazard was real and was avoided.                                         |
| Task 2d's confirmed Important closed      | **Confirmed.** All three ignore files now carry `/projects/*/search-log.md`, and prettier/markdownlint patterns are anchored (`/literatures/`, `/log/`). This was the headline finding of the first pass. |

**Residual, disclosed by the implementer and not independently re-run here:** `.editorconfig`
still uses `[literatures/**]` and `[log/**]` rather than an anchored form. EditorConfig matches
any section pattern containing a `/` against the path relative to the config file, so these are
already root-relative and the three files may well agree in meaning — but that is reasoning, not
measurement, and the first pass's whole point was that an unhonoured pattern matches nothing
while every pin stays green. Carried to the Part 2 boundary for a tool-run check.

## An anomaly worth not mis-blaming later

The offline suite is green at `8ed31c5` — **1554 passed, 7 skipped** (port 23119 LISTENING, so
live legs ran; not a hermetic result, per the standing caveat). That is **22 fewer collected
tests than the 1576 measured at `1ed029c`**, which reads at a glance like coverage lost across a
merge.

It is not. Test *definitions* are unchanged: 823 at `1ed029c`, 823 at `8ed31c5`. The drop is one
parametrized test resizing. `tests/test_config_validity.py:454` parametrizes
`test_markdown_table_rows_have_no_truncated_code_spans` over `_mdformat_owned_markdown()`, an
`rglob("*.md")` across `_MDFORMAT_ROOTS = ("README.md", "AGENTS.md", "CONTEXT.md", "docs", "skills")`. Across the merge:

```
docs/**/*.md      43 → 21    (−22)
skills/**/*.md    23 → 23
```

Main's `research/` reorg and its deletion of fourteen merged plan files moved 22 documents out
of the mdformat-owned tree. One case per file. 1576 − 22 = 1554, exactly. Nothing was lost.

Recorded because an unexplained 22-test drop across a merge is precisely the kind of thing that
sits unremarked and gets blamed on something unrelated weeks later.

## First-pass findings now closed

Measured at `origin/main` `6091521` and branch tip `8ed31c5`:

- **§2.1** (Task 2d's confirmed Important) — closed by `efa6b77`: search-log surface added to all
  three ignore files, prettier/markdownlint patterns anchored.
- **§2.3** (`oldest_age_days` emitted and unread) — closed by `76c3137`, which wires it into
  project-flow and setup-vault reporting.
- **§3.1** (scope creep) — closed by `6f39721`, Part 4 split into Plan W.
- **§3.2** (dead checkbox contract) — closed by `8ed31c5`, 38 boxes backfilled.
- **§3.5** (33 deferred minors routed nowhere) — closed by `6091521`: 38 items enumerated into the
  polish-pass section of `docs/research/validation-slice/2026-08-22-skills-layer-audit.md`. Verified
  count: 38 numbered entries, matching the 33 from the ledger plus 2 from 2d's review and 3 from
  the addenda review.
- **Addenda review Important 1** (false XML claim in shipped prose) — closed in the merge.

Still open: **§2.2** (the ledger's five missing completion lines, above), **§3.3**'s residual —
the merge is done but `docs/terminology.md` was the predicted conflict and its resolution is
worth a second read at the Part 2 boundary — and **§3.4** (the ledger head's "briefs come from the
worktree copy" sentence, false since Task 2b) and Task 8b's owed verify, neither of which any
commit has touched.

## Standing-role note

`research/` stands as written, so this is a new file rather than an edit to `bd64dcb`'s. The
next boundary is Part 2's end.
