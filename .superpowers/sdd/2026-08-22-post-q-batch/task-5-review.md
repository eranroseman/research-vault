# Task 5 review - 8e7b136..97afad5

## Spec Compliance

**Verdict: compliant.**

Both of the brief's steps landed.

Step 1 asked for the 14-path inventory to be dropped, the six test-pinned paths
kept as an honesty rule rather than an inventory, and the whole thing said in one
sentence. `skills/setup-vault/SKILL.md:21` now drops all eight of the stale-able
entries (`.gitignore`, `.research-vault/machine.json`, `index.md`,
`literatures/.gitkeep`, `log.md`, `log/.gitkeep`, `projects/.gitkeep`,
`synthesis/index.md`) and keeps the six that `tests/test_skill_files.py:111-119`
pins, reframed as "the contract, not an inventory of everything scaffold can
create". The card's decided sentence ships verbatim: `docs/2026-08-22-skills-layer-audit.md:257`
reads "scaffold prints every path it created; report that list verbatim, and
never present a path it did not print as committed", and that exact string is in
the skill line, lowercase-joined after "Run it:" so the card's casing never had
to be altered.

Step 2 asked for the pins to move, the suite to run, and a commit subject of
`fix: setup-vault paths are a contract, not an inventory (C-6)`. The subject at
97afad5 is exact, it is one commit, and the two honesty-phrase assertions
(`tests/test_skill_files.py:120-121`) move in the same commit as the prose they
pin.

**Issues:** none that rise to a spec violation. The one open finding below is a
wording imprecision at `skills/setup-vault/SKILL.md:21` and it is
NOT-VERIFIED-MINOR, which is neither CONFIRMED nor CONTESTED; under the synthesis
rule a Minor finding at that status cannot flip the spec verdict. The substance
the brief asked for — one sentence, inventory gone, pinned six reframed as a
contract, scaffold's own output named as the full list — did ship. The residual
tension is only that the sentence says "Paths such as ..." where the brief's
phrasing was closed ("the pinned six are the contract").

### Cannot verify from diff

1. **Suite green offline at 97afad5 — 1562 passed / 7 skipped, unchanged from
   BASE.** No lens re-ran the suite (the review instruction forbade it). The
   arithmetic is right on its face: the diff adds and removes no test function
   and changes only two assertion substrings inside an existing test, so
   UNCHANGED is the correct prediction. Controller check: confirm the
   `1562 passed, 7 skipped` line from the implementer's run log or CI at
   97afad5, and confirm the output was warning-free.
2. **Form gate: `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run
   --all-files`, all 8 hooks Passed.** Not re-runnable from a read-only review
   without mutating the tree, since the hooks reformat. Controller check:
   confirm the 8-hook Passed output from the implementer's log at 97afad5.
3. **The card's mandated probe was actually executed as described** (scratch
   template added, full suite run, five code-layer failures, `tests/test_skill_files.py`
   silent). The blast radius was corroborated structurally from the test sources —
   `tests/test_scaffold.py:21-38` `EXPECTED_CREATED` is the hardcoded list four
   tests read, and `tests/test_templates.py::test_all_canonical_template_paths_are_packaged`
   is the fifth — but the run was not reproduced. Controller check, optional: copy
   a file into `research_vault/templates/vault/system/templates/`, run the
   suite, expect exactly those five failures and `tests/test_skill_files.py` to
   pass, then delete the scratch file.
4. **The `research/validation-slice/2026-08-22-skills-layer-audit.md` path cited
   in the commit body and the report does not resolve at HEAD.** The card lives
   at `docs/2026-08-22-skills-layer-audit.md` in this worktree; I confirmed the
   `research/validation-slice/` copy is absent. Per the controller's PATH RULE
   (recorded at `.superpowers/sdd/2026-08-22-post-q-batch/task-4-review.md:76`)
   these citations are deliberately ahead of this branch, so this is a merge-time
   check, not a defect. Controller check: at merge, confirm
   `research/validation-slice/2026-08-22-skills-layer-audit.md` exists at that
   exact path.

**Resolved during synthesis, recorded rather than passed through:** the quality
lens could not see the commit body and asked whether it carries the provenance
and the explicit no-deviation finding. I ran `git show --no-patch 97afad5`. The
body carries the probe procedure and its result, both re-derived factual
citations (`research_vault/scaffold.py:241` is `return sorted(created)`; the
old enumeration matched the 13 files under `research_vault/templates/vault/`),
the adjudication quote, and the statement that neither citation was stale so no
deviation was required. Nothing in the code, the skill text, or the test
docstring carries that provenance, which is where the standing doctrine wants it.
This item is closed; no controller action needed.

## Strengths

- **The card's decided sentence ships byte-for-byte, and from the card rather
  than the dispatch's copy.** I checked `skills/setup-vault/SKILL.md:21` against
  `docs/2026-08-22-skills-layer-audit.md:257` and the wording matches character
  for character, including the lowercase "scaffold". Attaching it to "Run it:"
  preserves the imperative to execute that the old text carried as "Run scaffold
  and report its exact printed created paths", instead of silently dropping it.
- **The honesty pin was not weakened, and no sibling pin broke.**
  `tests/test_skill_files.py:111-119` still asserts all six load-bearing paths and
  the docstring "Claiming unrelated work was committed must fail." is unchanged;
  deleting or softening the honesty clause still fails line 121. The other
  setup-vault pin, `test_setup_vault_uses_scaffold_with_separate_ci_consents`
  (`tests/test_skill_files.py:35-36`), requires "Do not create directories or
  files by hand" and "use `git add .`", and both survive verbatim in the rewritten
  first sentence.
- **The two real behavioural caveats survived the rewrite.** CI paths appearing
  only for their separately consented flags, and repair creating fewer paths than
  a fresh scaffold, are constraints rather than inventory, and both are still
  stated. Nothing load-bearing left with the eight dropped paths.
- **Both of the card's factual citations were re-derived rather than trusted, and
  both held.** `research_vault/scaffold.py:241` is `return sorted(created)`,
  and `research_vault/templates/vault/` holds 13 files that map 1:1 onto the
  vault-derived entries of the old enumeration (`gitignore` -> `.gitignore`). I
  also confirmed independently that no other test, skill, or doc still quotes the
  old enumeration or the old "Say only scaffold-created paths are committed"
  phrasing.
- **Tight blast radius.** Two files, three changed lines, no new abstractions, no
  drive-by edits, and the pin moves in the same commit as the prose it pins.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

None.

### Minor (Nice to Have)

**`skills/setup-vault/SKILL.md:21` — the kept-six clause hedges with "such as"
and lists two bare directories scaffold never prints.**
Status: NOT-VERIFIED-MINOR. Plan-mandated: no. Raised independently by the
quality and fidelity lenses; merged here.

*What is wrong.* The sentence reads "Paths such as `AGENTS.md`,
`inbox/review-queue.md`, `system/templates/`, `system/bases/`,
`system/glossary.md`, and `.git/hooks/pre-commit` are the contract, not an
inventory of everything scaffold can create". Two things: "such as" reopens a set
the brief closed ("the pinned six are the contract"), and two of the six entries
are directory prefixes that scaffold never emits as created paths.

*Why it matters.* The immediately preceding clause instructs the agent to "never
present a path it did not print as committed". An agent that reads the six as
guaranteed contract paths could report `system/templates/` or `system/bases/` as
committed, even though `tests/test_scaffold.py:21-38` `EXPECTED_CREATED` contains
no bare-directory entry — scaffold prints `system/templates/daily.md` and its
three siblings, and `system/bases/open-questions.base` and
`system/bases/trust-tier.base`. The old prose was more precise on exactly this
point: it named the two `.base` files individually and wrote "`system/templates/`
daily, literature, project, and synthesis templates". Impact is low because the
adjacent verbatim-reporting rule dominates in practice.

*How to fix.* Close the set and point at files, e.g. "`AGENTS.md`,
`inbox/review-queue.md`, `system/glossary.md`, `.git/hooks/pre-commit`, and the
files under `system/templates/` and `system/bases/` are the contract, not an
inventory ...". Any rewrite must keep (a) the card's decided sentence verbatim,
(b) all six substrings the pin loops over at `tests/test_skill_files.py:111-119`,
and (c) both phrase assertions at `tests/test_skill_files.py:120-121`.

*Severity note.* The fidelity lens excused the bare-directory spelling as
pre-dating this change and forced by the test pin. That is half right and I have
corrected it: the *substring* pin pre-dates the change, but the old text
satisfied it inside full file paths. Presenting `system/templates/` and
`system/bases/` as standalone entries in a list of contract paths is new in this
diff. Severity still stays Minor — the verbatim-reporting rule sits in the same
sentence and mitigates the misreading.

## Refuted During Verification

None; every finding either lens raised survived verification, and both lenses
raised the same one. Nothing was dropped.

## Assessment

**Task quality: Approved.**

The brief's two steps landed exactly, the card's decided sentence shipped
verbatim from the card itself, and no pin — neither the honesty pin nor its
sibling in the same file — was weakened by the rewrite. The single surviving
finding is a Minor wording imprecision in the kept-six clause, which is deferred
rather than blocking; four cannot-verify items (three implementer-reported run
results plus the PATH RULE merge check) are left for the controller.
