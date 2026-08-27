# Task 2 report — C-7 routing index in the vault AGENTS.md template

## What I implemented

Added an index table to `knowledge_harness/templates/vault/AGENTS.md`, right after the
existing "Prefer the knowledge-harness skills..." sentence and before the managed-region
paragraph. The table lists the seven post-rename entry skills, each with a one-clause
description, plus a one-line intro explaining why the index exists (all seven ship
`disable-model-invocation: true`, so an agent cannot reach them on its own — this is the
exact contradiction the audit's C-7 card names).

Updated the whole-file pin at `tests/test_templates.py:96` (`test_markdown_templates_match_canonical_content`)
in the same commit, since it asserts `asset("vault/AGENTS.md").read_text()` byte-for-byte.

## Source of the entry list

Per the brief: do not derive the list by arithmetic over `skills/`. Cross-checked two sources:

- **`docs/2026-08-22-skills-layer-audit.md:340`** (C-7 adjudication): ruled option (a), "the
  seven names in the vault AGENTS.md template." The card text does not spell the names inline,
  but its contradiction paragraph (`docs/2026-08-22-skills-layer-audit.md:261`) says "Seven of
  nine skills ship `disable-model-invocation: true`" — i.e., the seven are `skills/` minus the
  two guard/reference skills (`evidence-conventions`, `synthesis-conventions`, both model-invoked,
  neither carrying `disable-model-invocation`).
- **`tests/test_skill_contracts.py:29-38`** (`ENTRY_SKILLS`): `setup-vault`, `publish`,
  `verify-citations`, `factcheck-draft`, `project-flow`, `import-source`, `find-sources`.

I confirmed these agree: `skills/` currently ships exactly nine directories (`evidence-conventions`,
`factcheck-draft`, `find-sources`, `import-source`, `project-flow`, `publish`, `setup-vault`,
`synthesis-conventions`, `verify-citations`); subtracting the two guard skills leaves precisely
the seven in `ENTRY_SKILLS`. **No disagreement to report** — both sources converge on the same
seven, and `project-flow` (not `project`) is used throughout, consistent with Task 1's rename.

## The seven names and where each clause came from

Each compressed clause was sourced from the skill's own `description:` frontmatter line
(`head -n 4 skills/<name>/SKILL.md`), compressing rather than inventing new content.

| Skill | Source `description:` line | My compressed clause |
| --- | --- | --- |
| `setup-vault` | "Use when a person asks to create, repair, or provision a knowledge-harness vault" | create, repair, or provision a vault |
| `project-flow` | "Use when a person starts a new knowledge-harness research project, resumes an existing one, or asks to frame a research question" | start or resume a research project |
| `find-sources` | "Use when a person asks to find, search, or look up literature, papers, citations, DOIs, PMIDs, arXiv IDs, or open-access sources for a knowledge-harness project, before anything is admitted into Zotero" | find literature before it is admitted to Zotero |
| `import-source` | "Use when a person asks to import, catalog, refresh, or backfill a source they have admitted to Zotero in a knowledge-harness vault" | import, catalog, refresh, or backfill an admitted source |
| `verify-citations` | "Use when a person asks to verify citations, run the citation checks, or check whether a vault's evidence is trustworthy" | verify citations and run the citation checks |
| `factcheck-draft` | "Use when a person asks to factcheck a draft, sanity-check claims against their sources, or run factored verification before review" | factcheck a draft against its sources before review |
| `publish` | "Use when a person asks to publish, park, correct, or withdraw a knowledge-harness project" | publish, park, correct, or withdraw a project |

Ordering in the table: `setup-vault` first (the one-time, out-of-band vault-creation step),
then `project-flow` (the orchestrating entry point for the research flow), then the four
skills `project-flow`'s own Routing table (`skills/project-flow/SKILL.md:64-74`) routes to, in
that same order (`find-sources`, `import-source`, `verify-citations`, `factcheck-draft`,
`publish`) — matching the existing routing-table convention the audit calls out approvingly.

## What I tested

Ran from the worktree root, `.venv/bin/python` directly (the sandbox in this session blocks
`source`-based commands as unverifiable worktree operations, so I invoked the venv's python
binary directly instead of `source .venv/bin/activate`; this is equivalent — same venv, same
interpreter).

1. Targeted tests:
   ```
   .venv/bin/python -m pytest tests/test_templates.py tests/test_skill_contracts.py -q
   ```
   Result: `47 passed in 0.23s` — includes the updated whole-file pin
   (`test_markdown_templates_match_canonical_content`) and the skill-contracts
   self-validation (`test_every_skill_name_a_shipped_template_cites_has_a_skill_directory`,
   `test_every_entry_skill_named_here_is_actually_shipped`).

2. Pre-commit, all hooks:
   ```
   .venv/bin/python -m pre_commit run --all-files
   ```
   Result: all 8 hooks passed, including `form: markdown CommonMark (mdformat)` — confirmed
   via `.pre-commit-config.yaml` that mdformat's owned path list (`README.md AGENTS.md
   CONTEXT.md docs skills`) does **not** include `knowledge_harness/templates/`, so this
   template file is not mdformat-owned and my hand-authored table formatting is not at risk
   of being silently rewritten later.

3. Full offline suite:
   ```
   .venv/bin/python -m pytest tests -q
   ```
   Result: `1548 passed, 7 skipped in 199.40s (0:03:19)` — matches the stated BASE-commit
   baseline exactly (1548 passed, 7 skipped). No new test items were added (only pinned
   bytes changed), so the count matching is the expected outcome, not a coincidence.

4. Confirmed `.superpowers/` is untracked (`git status --short .superpowers/` returns
   nothing, `git ls-files | grep -c '^.superpowers/'` returns 0), and Task 1's commit
   (`8dbf87f`) carried no report file either — so this report is not staged into the commit.

## Files changed

- `knowledge_harness/templates/vault/AGENTS.md` — added the seven-row index table and its
  one-sentence intro.
- `tests/test_templates.py` — updated the whole-file pin
  (`test_markdown_templates_match_canonical_content`) to match, in the same commit.

## Self-review

- Every cited name (`setup-vault`, `project-flow`, `find-sources`, `import-source`,
  `verify-citations`, `factcheck-draft`, `publish`, plus the pre-existing
  `evidence-conventions`) exists as a `skills/<name>/` directory — verified with the same
  backticked-kebab-token regex `test_skill_contracts.py` uses, run standalone against the
  edited file, before running the suite.
- Every clause traces to that skill's own `description:` line (table above); nothing invented.
- The whole-file pin was updated in the same edit pass and the same commit as the template
  change.
- No scope creep: did not touch any `skills/*/SKILL.md` file, did not touch `project-flow`'s
  own Routing table, did not touch any other template file.
- Table alignment: hand-aligned with a short Python script rather than trusting an automatic
  formatter, since this file is outside mdformat's owned paths and there is no pin-independent
  formatter to lean on.

## Concerns

None. The C-7 card and `ENTRY_SKILLS` agreed exactly on the seven names; no arbitration was
needed.
