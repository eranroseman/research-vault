### Task 1: Rename `project` → `project-flow` (item 1)

Disposition: historical (2026-09-06)

Ruled 2026-08-22: class-4 collision with CONTEXT.md's *Project* dissolved by the glossary's other governed noun, *Project flow*. Entry family becomes uniformly two-part.

**Files:** Move: `skills/project/` → `skills/project-flow/`. Modify: `docs/terminology.md` §4.3 skills row; routing tables in `skills/find-sources/SKILL.md` and `skills/import-source/SKILL.md`; the skill's content test in `tests/`.

- [ ] **Step 1:** `git mv skills/project skills/project-flow`; update `name:` in its SKILL.md frontmatter to `project-flow`.
- [ ] **Step 2:** Update terminology §4.3's skills row and both routing tables (grep `skills/ -rn "\`project\`"` and judge each hit — routing rows change; prose about "a project" (the noun) does not).
- [ ] **Step 3:** Update the content test that names the skill (locate via `grep -rn "project" tests/test_skill_contracts.py tests/test_skill_files.py`); run it: PASS.
- [ ] **Step 4:** Judged grep for retired references: `grep -rn "skills/project/\|Skill(project)\|\`project\` skill" --include="*.md" .` — every hit either updated or judged non-referential (record the judgment list in the commit body).
- [ ] **Step 5:** Full offline suite. Commit `refactor: rename project skill to project-flow`.

