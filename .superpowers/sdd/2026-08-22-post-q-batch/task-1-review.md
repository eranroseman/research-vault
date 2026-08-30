# Task 1 review - 002cb25..8dbf87f

## Spec Compliance

**Verdict: compliant.**

Every step of the brief landed, in one commit with the mandated subject.

- **Step 1** — `skills/project/` → `skills/project-flow/` shows in the diff as a 98%-similarity rename, with `name: project` → `name: project-flow` in the frontmatter. `ls skills/` confirms no leftover `skills/project/`, and the moved directory carries SKILL.md as its only file, so nothing was stranded behind the move.
- **Step 2** — `docs/terminology.md:127` (§4.3 skills row) and both routing tables (`skills/find-sources/SKILL.md:17` inline route and `:104` table row, `skills/import-source/SKILL.md:173` table row) are updated. The implementer also caught a second self-reference in the same ruled §4.3 section, the Plan D verbs row's `` `project` ``'s resume-orientation step at line 125 — a correct application of the brief's own judgment rule rather than scope creep.
- **Step 3** — the content test moved to `tests/test_project_flow_skill.py` with its `SKILL` path constant, frontmatter-name assertion and module docstring updated. The brief's grep also names `tests/test_skill_files.py`; that file is scoped entirely to `skills/setup-vault/SKILL.md` and contains no `project` reference, so it owed no edit — the requirement is satisfied vacuously rather than overlooked.
- **Step 4** — the judgment list is in the commit body, as the brief required, not merely in the report. `git log -1 --format=%B 8dbf87f` carries both required greps, every hit with its ruling and reason, the frozen-document rationale quoted from AGENTS.md, and the deliberately preserved frozen-spec citation.
- **Step 5** — the package contains exactly one commit, subject `refactor: rename project skill to project-flow`, verbatim.

Three edits fall outside the brief's declared file list and all three are required consequences of the rename rather than scope creep: `ENTRY_SKILLS` in `tests/test_skill_contracts.py:36` (without it, `test_every_entry_skill_named_here_is_actually_shipped` and `test_invocation_flags_match_the_ruled_control_model` fail the moment the directory moves), and the skill self-references in `research_vault/__main__.py:450` and `tests/test_trust_tier_cli.py:5`, which are stale skill names in shipped source that the brief's test-file-scoped grep would never have surfaced.

The two table reflows were checked for hidden semantic edits, the failure mode a padding-churn diff is good at concealing. Normalizing all 26 removed and 26 added lines (collapse whitespace, collapse separator dash runs, substitute the rename back) leaves a perfect one-to-one mapping with nothing on either side alone: the rename is the only semantic delta in the commit.

### Cannot verify from diff

- **Offline suite green at task end.** The report claims 1548 passed / 7 skipped at 8dbf87f, identical to baseline, and 10 passed for `tests/test_project_flow_skill.py` as Step 3's PASS evidence. No lens was permitted to re-run the suite, and the synthesis deliberately left it to the checkpoint rather than duplicating it. At the Part 1 checkpoint, run `python -m pytest tests -q` at 8dbf87f and confirm 1548 passed / 7 skipped with no new warnings, plus `python -m pytest tests/test_project_flow_skill.py -q` reporting 10 passed.
- **Live legs after a rename.** `docs/testing.md:13` states unconditionally that after renames or seam moves the live legs must run before the wave is claimed complete, and `RV_LIVE` / `RV_LIVE_NET` were deliberately not run here. The per-task reasoning holds: every `.py` delta in this commit is a docstring, a test docstring, or the `ENTRY_SKILLS` literal, no executable path changed, and no live-gated test reads the skill directory. The obligation is wave-level, and it has a written landing point — Task 21 Step 3 at `docs/superpowers/plans/2026-08-22-post-q-batch.md:447` already reads "Full suite offline AND live (`RV_LIVE=1 RV_LIVE_NET=1 RV_MAILTO=<real>`, Zotero running)". Confirm that step actually executes before the wave merges, so the deferral closes rather than evaporates.

Two notes so nothing is misattributed to this commit. First, `mdformat --check --number --wrap keep` reports `docs/superpowers/plans/2026-08-22-post-q-batch.md` as unformatted; that file is untouched by this diff and the pre-commit config records the plans directory as deliberately outside the record-immutability manifest, so the failure is pre-existing. Second, the report justifies the table reflows by citing an IDE `MD060/table-column-style` warning; `mdformat_tables` is not installed in this repo, so the repo's own gate is indifferent to table alignment. The outcome is harmless and matches the tree's de-facto aligned-pipe style, but the stated rationale names a linter this repo does not run.

## Strengths

The rename is mechanically complete across every reference form worth searching: backtick, path, `name:` frontmatter, `Skill()` and slash invocation, quoted string literal, test filename, and hand-maintained skill-name enumerations. Repo-wide greps for `` `project` `` over `skills/`, `research_vault/` and `tests/` return zero hits; `skills/project\b` returns five, all in dated plan and audit records. Manifests, CI workflows, hooks and `pyproject.toml` reference `skills` as a directory and never per-skill, so nothing was owed there.

Frozen-document discipline is correct and explicitly reasoned rather than asserted. The frozen foundation spec's §7 row at `docs/superpowers/specs/2026-08-16-foundation-spec.md:119` is still literally `| `project` | entry |`, so `tests/test_project_flow_skill.py:34`'s citation of it was left spelling `project` on purpose — rewriting it would have turned an accurate citation into a misdescription of a frozen document.

The `ENTRY_SKILLS` update is the single most valuable thing in the commit beyond the move itself: it is what keeps the `disable-model-invocation` control-model gate and the shipped-directory gate honest, and it closes the half-done-rename hazard the plan flags for Task 2 before Task 2 begins.

The judgment list lives in the commit body, hit by hit with its ruling and reason, rather than pointing at a report that does not outlive the session. That is the artifact the brief asked for.

Form gates were checked independently of the implementer's pytest-only evidence: `ruff format --check` and `ruff check` pass on all four changed Python files, and `mdformat --check --number --wrap keep` — the pre-commit hook's exact invocation — passes on every markdown file this commit touched, including both reflowed tables.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

None.

### Minor (Nice to Have)

**1. Test function names still carry the retired skill name — `tests/test_project_flow_skill.py:23`** (CONFIRMED)

All ten test functions in the renamed file keep the `test_project_*` prefix (lines 23, 32, 48, 63, 75, 87, 102, 115, 130, 143) while the file, the skill directory and the frontmatter all now say `project-flow`.

This matters because pytest node IDs are the identifiers humans and CI cite, and `test_project_documents_every_routing_target` now reads as a test about *Project* the ordinary CONTEXT.md noun — precisely the class-4 collision this rename exists to dissolve. It also diverges from the sibling convention: `tests/test_import_source_skill.py` prefixes with the skill name (`test_import_source_says_it_needs_no_project`). The implementer's rationale, that the functions assert behaviour rather than the old skill name, does not survive inspection — the functions do carry the skill's name in their prefix.

Fix: rename the ten functions to `test_project_flow_*`. Mechanical, no assertion changes.

**2. No test pins the inbound routing references to the renamed skill — `skills/find-sources/SKILL.md:104`** (CONFIRMED)

Nothing in the suite asserts that the routing rows at `skills/find-sources/SKILL.md:104` and `:17` or `skills/import-source/SKILL.md:173` name the current skill. `tests/test_import_source_skill.py` and `tests/test_find_sources_vendor.py` contain no routing assertion, and `tests/test_skill_contracts.py`'s citation guard scans `research_vault/templates/` only.

This matters because the half-done rename the plan names as the Task 2 hazard is currently guarded only by the implementer's grep discipline: had either inbound routing row been missed, the suite would still have reported 1548 passed. Only `tests/test_project_flow_skill.py:115` pins routing, and only outbound, from the renamed skill to its targets.

Fix: add one assertion per inbound router — in `tests/test_import_source_skill.py` and a find-sources content test, assert that the routing section contains `` `project-flow` ``. Note the guard did improve incidentally: `project-flow` is hyphenated, so the template-citation token regex now covers it where bare `project` was invisible.

**3. Stale skill references survive in a self-declared living document — `docs/product-landscape/2026-08-22-adoption-plan.md:585`** (CONFIRMED)

Seven references to the skill by its old name survive at lines 312, 442, 515, 585, 669, 697 and 789. The task report rules the whole product-landscape directory "product-landscape research docs, frozen"; that ruling appears in the report, not the commit body, because the brief's Step 4 grep provably does not reach this file — its pattern returns no hits here.

The freeze rationale does not hold for this particular file. AGENTS.md freezes `research/`, `analysis/`, completed plans and accepted ADRs; the pre-commit record-immutability manifest covers `research/`, `analysis/` and `docs/adr/`. Neither list covers `docs/product-landscape/`. The file's own line 3 opts out explicitly: "Decision note, 2026-08-22. Updated as we act on it, unlike its two sources." Lines 585, 697 and 789 name the skill as a shipped component in the actionable adoption tiers, so a reader is pointed at a directory that no longer exists. Blast radius is low — no test, routing table or downstream contract reads this file.

Fix: update the seven backticked references to `project-flow`. Leave `2026-08-22-product-comparison-verified.md` and `2026-08-22-review-findings.md` untouched — those are dated records of the past, which is the correct reason to leave them, distinct from the freeze list.

## Refuted During Verification

None. All three findings raised by the lenses survived verification, and all three were re-checked directly against the tree during synthesis.

One lens claim was corrected rather than carried forward. The fidelity lens reported that Task 21's step list "does not name a live-leg run", making the live-leg deferral point at a task that never performs it. The plan text refutes this: Task 21 Step 3 at `docs/superpowers/plans/2026-08-22-post-q-batch.md:447` reads "Full suite offline AND live (`RV_LIVE=1 RV_LIVE_NET=1 RV_MAILTO=<real>`, Zotero running)." The deferral has a written landing point; the open obligation is that the step is executed, not that it is missing. The cannot-verify item above carries the corrected pointer.

One lens cannot-verify item was resolved rather than passed through. The quality lens could not confirm from its package that the Step 4 judgment list reached the commit body. Reading `git log -1 --format=%B 8dbf87f` during synthesis confirms it did, in full.

## Assessment

**Task quality: Approved.**

The rename lands completely and correctly across every live surface, the two out-of-brief edits it reached for are required consequences rather than scope creep, and the reflowed tables were proven whitespace-only by a one-to-one normalized line mapping. The three surviving findings are all Minor and none is a missed requirement: two are naming and coverage polish inside the test layer, and the third is stale prose in a document the brief's greps never reached.
