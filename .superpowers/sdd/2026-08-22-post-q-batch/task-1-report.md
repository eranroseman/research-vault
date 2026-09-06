# Task 1 report: Rename `project` -> `project-flow`

Disposition: historical (2026-09-06)

## Status: DONE

## What I implemented

Exactly the brief's rename, plus every genuine skill self-reference the
required (and supplementary) greps turned up, per the judgment rule
("routing rows and skill references change; prose about 'a project' the
ordinary noun does not").

1. `git mv skills/project skills/project-flow`; `name:` frontmatter ->
   `project-flow`; the Routing section's self-reference
   ("`project` orchestrates" -> "`project-flow` orchestrates") at line 66.
2. Routing tables updated:
   - `skills/find-sources/SKILL.md`: the inline "route to `project`" at
     line 17, and the routing-table row at line 104.
   - `skills/import-source/SKILL.md`: the routing-table row at line 173.
     Reflowed that table's column widths after the edit (see below).
3. `docs/terminology.md` SS4.3: the "skills" row (line 127) and, on
   review, a second self-reference in the same section — line 125's
   "`project`'s resume-orientation step" (part of the "Plan D's verbs"
   row). Both are the same kind of hit (a skill self-reference inside the
   ruled SS4.3 table), so both changed. Reflowed that table's column
   widths after the edit (see below).
4. Content test renamed `tests/test_project_skill.py` ->
   `tests/test_project_flow_skill.py` (matches the repo's existing
   `test_<skill>_skill.py` convention, e.g. `test_import_source_skill.py`).
   Updated: module docstring (lines 1, 4), `SKILL` path constant (line
   15), and the frontmatter-name assertion (line 27,
   `text.startswith("---\nname: project-flow\n...")`). Left unchanged:
   test function names (`test_project_*` — they assert behavior, not the
   old skill name, so renaming is unnecessary churn) and line 34's "spec
   SS7's project row names these exactly" (the frozen spec's SS7 row is
   still literally named `project`; rewriting this to `project-flow`
   would misdescribe a frozen document).
5. `tests/test_skill_contracts.py`: `ENTRY_SKILLS` set entry `"project"`
   -> `"project-flow"` (line 36) and the adjacent comment token (line
   29). This one is not in the brief's literal file list, but it is
   *required*, not optional — `ENTRY_SKILLS` is checked against shipped
   directory names (`test_every_entry_skill_named_here_is_actually_shipped`)
   and against `disable-model-invocation` gating
   (`test_invocation_flags_match_the_ruled_control_model`); leaving the
   old name in the set breaks both once the directory is renamed.
6. `research_vault/__main__.py` (`cmd_trust_tier` docstring, line 450)
   and `tests/test_trust_tier_cli.py` (module docstring, line 5): both
   had a `` `project`'s resume-orientation step `` self-reference. Found
   via a repo-wide grep for the exact backtick-quoted skill name that
   went beyond the brief's literal grep list — the brief's Step 3 grep
   was scoped to `test_skill_contracts.py`/`test_skill_files.py` and
   wouldn't have caught these. A stale self-reference in *shipped
   production code* would be a worse miss than one in a doc, so I
   treated "run the greps you actually need to find every hit" as
   covering `research_vault/` and `tests/` generally, not just the
   two named test files.
7. Table realignment (cosmetic, no semantic change): editing a cell to a
   longer string broke GFM pipe-table column alignment in two tables
   (`docs/terminology.md` SS4.3's second table, and
   `skills/import-source/SKILL.md`'s routing table) — IDE diagnostics
   flagged both (`MD060/table-column-style`). Reflowed each table's
   column widths with a small script (recomputed max width per column,
   rebuilt the separator and padding) so every row's pipes line up again.
   Verified via `git diff --stat` that each reflow touched only the
   table block itself (7 lines each), nothing else in the file.

## Judgment list (every grep hit, ruled)

**`grep -rn '`project`' skills/`** (brief's Step 2, corrected argument
order) — 4 hits, all skill self-references, all changed:
`skills/project/SKILL.md:66`, `find-sources/SKILL.md:17` and `:104`,
`import-source/SKILL.md:173`.

**`grep -rn "skills/project/\|Skill(project)\|\`project\` skill"
--include="*.md" .`** (brief's Step 4) — 6 hits, all in dated
plan/audit/research docs that stand as written per this repo's AGENTS.md
("research/, analysis/, completed plans, and accepted ADRs stand as
written — content, internal paths, and file location"); none changed:
- `docs/superpowers/plans/2026-08-22-post-q-batch.md` (x3: the Files
  line, the Step 4 grep spec itself, and the Part 1 checkpoint line) —
  this is the batch plan document that generated my own task brief.
- `docs/superpowers/plans/2026-08-22-plan-d-skills.md:84` — completed
  plan, historical task heading ("Task 4: `project` skill").
- `docs/2026-08-22-no-fabrication-audit.md:146` — dated audit, quotes a
  verifier verdict against the pre-rename path.
- `docs/product-landscape/2026-08-22-product-comparison-verified.md:570`
  — product-landscape research doc.

**Supplementary greps run beyond the brief's literal list** (per my
task's explicit instruction to find every hit, and per the general
principle that a rename which "must land completely and correctly"
shouldn't stop at the brief's named files):

- `grep -rn 'skills/project\b' .` (path form, all files) — same 6
  historical hits as above, plus 2 more lines in the same file
  (`docs/superpowers/plans/2026-08-22-post-q-batch.md:26,28` in addition
  to `:31,183` already counted). No new live ones. All frozen, none
  changed.
- `` grep -rn '`project`' research_vault/ `` — 1 hit,
  `research_vault/__main__.py:450` (`cmd_trust_tier` docstring) — live
  source, changed (item 6 above).
- `tests/test_trust_tier_cli.py:5` docstring — live test file, skill
  self-reference, changed (item 6 above).
- `docs/terminology.md` SS4.3 full-section read (not just the named
  "skills row") — turned up line 125's second self-reference, changed
  (item 3 above).
- `ls .claude-plugin` and `grep -rn project .claude-plugin/*.json` —
  zero hits; no plugin-manifest reference to update.
- `grep -rn '`project`' . --exclude-dir=.git --exclude-dir=.venv
  --exclude-dir=__pycache__` (full-repo, run at self-review time as a
  final gate, since earlier sweeps were scoped per-directory rather than
  repo-wide) — 30 hits beyond what's already listed above, all frozen or
  irrelevant, none changed:
  - `docs/superpowers/specs/2026-08-16-foundation-spec.md` (x3, lines 34,
    119, 146) — the frozen foundation spec; its §7 row is still literally
    named `project` (the same reason `test_project_flow_skill.py:34`'s
    citation stays untouched).
  - `docs/superpowers/plans/2026-08-17-plan-c-scaffold-enforcement.md`
    (x2) and `docs/superpowers/plans/2026-08-22-vault-agents-template-revision.md`
    (x1) — completed plans, frozen.
  - `docs/2026-08-22-skills-layer-audit.md` (x9) — the dated audit that
    itself recommended this rename; frozen historical record.
  - `docs/product-landscape/2026-08-22-adoption-plan.md` (x7),
    `docs/product-landscape/2026-08-22-review-findings.md` (x1), and
    3 more lines in `docs/product-landscape/2026-08-22-product-comparison-verified.md`
    beyond the `:570` already listed — product-landscape research docs,
    frozen.
  - `research/raw/wide-prior-art/sensemaking-literature.json` — under
    `research/`, frozen per AGENTS.md regardless of content.
  - `research/plugin-packaging-mechanics.md:25` — a false positive: this
    `` `project` `` is the Claude Code plugin-install scope
    (`user`/`project`), unrelated to our skill; also under `research/`
    and frozen either way.
  - No hit in a root file (`README`, `CONTEXT.md`), `.github/`, or any
    script — the advisor's specific concern about an uncovered root
    reference did not materialize.

## What I tested

- `./.venv/bin/python -m pytest tests -q` (baseline, before any edit):
  **1548 passed, 7 skipped** in 90.43s.
- `./.venv/bin/python -m pytest tests/test_project_flow_skill.py -v`
  (Step 3's "run it: PASS" evidence, after rename+edits): **10 passed**
  in 0.04s.
- `./.venv/bin/python -m pytest tests/test_skill_contracts.py -v`
  (generic contract over the renamed set): **40 passed** in 0.07s —
  includes `test_frontmatter_parses_via_the_core_parser[project-flow]`,
  `test_name_matches_directory[project-flow]`,
  `test_description_is_nonempty[project-flow]`,
  `test_invocation_flags_match_the_ruled_control_model[project-flow]`,
  and `test_every_entry_skill_named_here_is_actually_shipped`, all green.
- `./.venv/bin/python -m pytest tests -q` (full offline suite, after all
  edits including the table reflows): **1548 passed, 7 skipped** in
  88.56s — identical to baseline.
- `./.venv/bin/python -m pytest tests -q` (re-run after the
  import-source table reflow, to make sure that cosmetic fix didn't
  regress anything): **1548 passed, 7 skipped** in 93.20s.

Note on the venv: this sandbox's worktree-isolation guard refuses
`source .venv/bin/activate && ...` (it can't verify a sourced script
stays inside the worktree). I used `./.venv/bin/python -m pytest ...`
directly instead — same venv, same interpreter, just invoked without
`source`. Flagging this so a reviewer doesn't wonder why the transcript
doesn't show the literal `source` command from the global constraints.

## Files changed

- `skills/project/SKILL.md` -> `skills/project-flow/SKILL.md` (renamed;
  frontmatter `name:` and one prose self-reference updated)
- `skills/find-sources/SKILL.md` (routing reference + routing-table row)
- `skills/import-source/SKILL.md` (routing-table row; table reflowed)
- `docs/terminology.md` (SS4.3 skills row + Plan D verbs row; second
  table reflowed)
- `tests/test_project_skill.py` -> `tests/test_project_flow_skill.py`
  (renamed; SKILL path, frontmatter assertion, docstrings updated)
- `tests/test_skill_contracts.py` (ENTRY_SKILLS entry + comment token)
- `tests/test_trust_tier_cli.py` (docstring self-reference)
- `research_vault/__main__.py` (`cmd_trust_tier` docstring
  self-reference)

## Self-review findings

- Completeness: every hit from the brief's two required greps, plus
  supplementary greps over `research_vault/`, the rest of
  `docs/terminology.md` SS4.3, and a path-form sweep, is accounted for
  and ruled above. No stray hits found on a final full-repo re-grep for
  `` `project` `` and `skills/project` other than the frozen docs and the
  one deliberately-preserved spec citation.
- YAGNI: did not touch `docs/superpowers/plans/`,
  `docs/product-landscape/`, `docs/superpowers/specs/`, or
  `docs/2026-08-22-*-audit.md` — all frozen per AGENTS.md. Did not rename
  test function names in `test_project_flow_skill.py` (they don't assert
  the old name; renaming them would be pure churn against "implement
  exactly what the brief specifies — no more").
- Names accurate: `skills/project-flow/SKILL.md` frontmatter `name:
  project-flow` matches its directory; `test_project_flow_skill.py`
  follows the repo's existing `test_<skill>_skill.py` convention.
- No stray changes: `git status` after staging shows exactly the 8 files
  listed above (2 renames + 6 modifications) — nothing else touched.
- Pristine test output: full suite is 1548 passed / 7 skipped, identical
  to the stated baseline, both before my first edit and after my last
  one.

## Concerns

None blocking. Two notes:

- The two table-realignment fixes were unplanned but necessary
  (IDE-flagged `MD060` warnings from cells growing 5 characters); each
  was verified via `git diff --stat` to touch only its own table block,
  and the full suite stayed green through both.
- `docs/testing.md` says "after renames or seam moves, run the live legs
  before claiming the wave complete." I did not run
  `RV_LIVE=1 RV_LIVE_NET=1 ...`. This is deliberate, not an
  oversight: every `.py` change in this task is a docstring or a test
  file (`research_vault/__main__.py`'s one-line docstring edit,
  `test_skill_contracts.py`'s `ENTRY_SKILLS` set,
  `test_trust_tier_cli.py`'s docstring) — no executable code path
  changed, so none of the 7 gated live legs can be affected by this
  commit. The batch plan's own Part 1 checkpoint (line 183) states the
  bar for this stage is "full suite green offline," with final
  acceptance and live verification deferred to Task 21.
