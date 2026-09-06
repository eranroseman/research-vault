# Task 2 review - aef25c1..45aa45d

Disposition: historical (2026-09-06)

## Spec Compliance

**Verdict: compliant.**

Both brief steps landed as written, and I re-derived the load-bearing facts rather
than taking the implementer's report on trust.

Step 1 asked for the seven post-rename entry names with one clause each, each clause
sourced from that skill's own `description:` line, with
`tests/test_skill_contracts.py`'s citation self-validation still passing.
`research_vault/templates/vault/AGENTS.md:12-20` carries exactly seven rows. The
set is corroborated four ways, each checked independently of the report: the C-7
adjudication rules option (a), "the seven names in the vault `AGENTS.md` template"
(`docs/2026-08-22-skills-layer-audit.md:340`); `skills/` ships nine directories and
exactly seven carry `disable-model-invocation: true`, the two omissions being the
guard skills `evidence-conventions` and `synthesis-conventions`; `ENTRY_SKILLS`
(`tests/test_skill_contracts.py:31-39`) is set-equal to the table; and
`docs/terminology.md:127` lists the ruled names. I read all nine `description:` lines
from the frontmatter and compared them to the seven clauses. Every clause is a strict
compression of its own skill's description — the only material dropped is tail
alternatives, such as `project-flow`'s "or asks to frame a research question" and
`factcheck-draft`'s "sanity-check claims against their sources". Nothing is invented.
The names are the post-rename ones: `project-flow`, with no `skills/project/` left in
the tree.

Step 2 asked for the whole-file pin updated in the same commit, a full suite, and an
exact commit subject. `tests/test_templates.py:96` is the only content pin over this
asset, its added block reproduces the template byte-for-byte including the trailing
blank line, and it lands in the same single commit `45aa45d`, whose subject is the
brief's string verbatim. I ran
`.venv/bin/python -m pytest tests/test_templates.py tests/test_skill_contracts.py -q`
myself: 47 passed, matching the report.

Scope is exactly the brief's two files. No `skills/*/SKILL.md`, no other template, no
other test, and no `.superpowers/` artifact entered the commit.

### Cannot verify from diff

- **Full offline suite green at task end (1548 passed, 7 skipped).** Re-run
  `source .venv/bin/activate && python -m pytest tests -q` at the gate. The
  implementer reported the expected counts; I ran only the two targeted files, which
  passed.
- **`pre-commit run --all-files` clean, under the mandated activation.** Re-run
  `source .venv/bin/activate && pre-commit run --all-files` from the worktree root.
  Expect 8 hooks: I read `.pre-commit-config.yaml` and confirmed it defines ten hooks
  of which `shellcheck` and `shfmt` are `stages: [manual]`, so eight is the correct
  count for `--all-files` and the report's "8 hooks" is not a discrepancy. The reason
  this leg is worth redoing is the Minor finding below, not doubt about the result.
- **Resolved during synthesis, no controller action needed:** the fidelity lens could
  not read the commit body. I ran `git show -s --format=%B 45aa45d`. The body
  describes the seven-row index, the post-rename name, the `ENTRY_SKILLS`
  cross-check, the pin update, and the C-7 reference. It claims nothing false.

## Strengths

- The seven clauses are genuinely sourced. All three lenses and this synthesis
  checked them against the real frontmatter rather than the report's table, and none
  is invented or drifted from its description line.
- The framing sentence at `research_vault/templates/vault/AGENTS.md:10` states a
  fact that is both true and mechanically defended: exactly the seven listed skills
  carry `disable-model-invocation: true`, and
  `test_invocation_flags_match_the_ruled_control_model`
  (`tests/test_skill_contracts.py:108`) goes red if any of them loses the flag or any
  guard skill gains one. The prose cannot rot without a test failing.
- Ordering is a convention, not an accident: `setup-vault`, then `project-flow`, then
  the five skills in the same order as `project-flow`'s own routing table
  (`skills/project-flow/SKILL.md:66-74`), so the two routing surfaces read as one.
- The table is byte-aligned to mdformat-canonical widths (every row 81 bytes, no
  trailing whitespace) even though `research_vault/templates/` sits outside
  mdformat's owned path list, so a future ownership change would not silently rewrite
  the file out from under the whole-file pin.
- The pin landed in the same commit as the content it pins, with the mandated
  conventional subject and an honest body.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

None. The fidelity lens filed its coverage finding as Important; verification
downgraded it, and it appears under Minor below with the reasoning recorded.

### Minor (Nice to Have)

**1. The index is not mechanically bound to `ENTRY_SKILLS` in either direction —
`research_vault/templates/vault/AGENTS.md:10`** (status: CONFIRMED; severity
corrected from Important to Minor)

*What is wrong.* Nothing asserts that every entry skill appears in the vault
template. `ENTRY_SKILLS` (`tests/test_skill_contracts.py:31`) is read at only two
places — `:73`, which checks `ENTRY_SKILLS` against shipped directories, and `:106`,
the per-skill invocation-flag check. `test_every_skill_name_a_shipped_template_cites_has_a_skill_directory`
(`tests/test_skill_contracts.py:155`) checks the other direction, cited names against
shipped directories. No test closes the loop. The forward guard also has a hole of
its own: `_BACKTICKED_KEBAB_TOKEN` (`tests/test_skill_contracts.py:47`) requires at
least one hyphen, so the new `publish` row
(`research_vault/templates/vault/AGENTS.md:20`) — the first single-word skill
citation in any shipped template — is invisible to it, leaving that one row unguarded
in both directions.

*Why it matters.* When an eighth entry skill ships, the table and the hard-coded
"These seven" go stale silently; the whole-file equality pin
(`tests/test_templates.py:96`) pins whatever the template happens to say, so an
omission never reaches it. In the other direction, if `skills/publish/` is renamed,
`test_every_entry_skill_named_here_is_actually_shipped` forces the `ENTRY_SKILLS`
update but nothing forces the template row, and the citation guard stays green over a
stale name shipped into every vault. Task 1 of this same batch renamed `project` to
`project-flow`, so renames are live here, not hypothetical. This is the one drift
vector for the surface C-7 exists to keep accurate, and the module already builds
exactly this kind of self-validating converse check elsewhere.

*How to fix.* One reverse assertion beside
`test_every_skill_name_a_shipped_template_cites_has_a_skill_directory`: read
`TEMPLATES_DIR / "vault" / "AGENTS.md"` and assert every name in `ENTRY_SKILLS`
appears in it. A plain substring or row check rather than the regex covers the
`publish` leg too. It passes as written today and fails the moment a new entry skill
lands without an index row, which is also the moment the "seven" in the prose needs
rewording.

*Verification and severity.* Confirmed twice; the substance is not in doubt. Both
verifiers judged Important inflated, and two of the three lenses had independently
filed the same substance as Minor, so it is recorded as Minor here. The brief
required only that the forward guard pass and the pin update — both done — and
`tests/test_skill_contracts.py` was not on the brief's file list; the fidelity lens
itself wrote that this is "not grounds to distrust the diff". The landed index is
correct and complete today. One caveat carried from verification: the charge that the
C-7 adjudication's "already guards the names mechanically" was "only half-true"
overreaches — the audit claimed forward validation of the names the template *cites*
(`docs/2026-08-22-skills-layer-audit.md:86`, `:227`, `:271` state the guard's exact
scope, including that it "proves only that a directory of that name exists"), which
is accurate as stated. The `publish` hyphen gap is a pre-existing limitation of that
regex, not something the ruling mandated; the reverse-direction gap is the shape the
human ruled, which is why this is flagged as plan-mandated and belongs in the ledger
rather than in a rejection.

*Merge provenance.* This finding consolidates three lens findings that one added
assertion closes: fidelity's finding at
`research_vault/templates/vault/AGENTS.md:14` (Important, CONFIRMED — the missing
converse check), quality's finding at line 10 (Minor — the same converse check, with
the "These seven" prose exposure), and spec's finding at line 20 (Minor — the
`publish` hyphen-regex leg). None was dropped.

**2. The pre-commit gate did not run under the mandated venv activation —
`.superpowers/sdd/2026-08-22-post-q-batch/task-2-report.md:57`** (status:
NOT-VERIFIED-MINOR)

*What is wrong.* The global constraint is that every test run begins
`source .venv/bin/activate`. The implementer disclosed that its sandbox refused
`source`-based commands and substituted `.venv/bin/python -m pytest` and
`.venv/bin/python -m pre_commit`, calling the substitution "equivalent — same venv,
same interpreter". That holds for pytest, but not for pre-commit.

*Why it matters.* I read `.pre-commit-config.yaml`: all eight default-stage hooks are
`language: system` with bare tool entries (`bash -c 'ruff format ...'`, `mypy`,
`bash -c 'mdformat ...'`, `yamlfix`, `pyproject-fmt`, and so on), so each tool
resolves through the ambient PATH, and `-m pre_commit` does not put the worktree's
`.venv/bin` on it. The config's own header names
`source .venv/bin/activate && pre-commit run --all-files` as the one command for
exactly this reason. The fidelity lens found the ambient PATH resolves these tools to
the main checkout's venv, then compared versions across both venvs and found them
identical (ruff 0.15.21, mdformat 1.0.0 with mdformat-gfm 1.0.0 and
mdformat_frontmatter 2.1.2), so the reported 8-hook pass stands. Impact here is
further limited because `research_vault/templates/` is outside mdformat's owned
paths, so the new table was never a formatter target.

*How to fix.* Re-run `source .venv/bin/activate && pre-commit run --all-files` from
the worktree root to close the gate as specified. Nothing in the diff needs to
change. This is constraint hygiene, not doubt about the result, and it does not move
either verdict.

## Refuted During Verification

None. No finding from any lens was refuted; both surviving findings are recorded
above, one with its severity corrected downward and its original label noted.

## Assessment

**Task quality: Approved.**

The mandated content landed exactly as ruled — seven correct names, seven faithfully
compressed clauses, a true and test-defended framing sentence, the pin updated in the
same commit, and the exact commit subject — and every claim in the implementer's
report survived independent checking. What remains is one deferred test-coverage
wish, one added assertion wide, plus a gate re-run under the literal venv-activation
constraint; neither blocks the merge.
