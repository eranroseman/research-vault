# Task 5 report: setup-vault C-6 (audit item 6)

Disposition: historical (2026-09-06)

Source card: `research/validation-slice/2026-08-22-skills-layer-audit.md:247-259` (read at its pre-move on-branch location, C-6; adjudication at line ~325-330).

## Probe (run first, per the card's State field)

The card's State says this is `ready-for-agent` — *record*, not a plain repair — and directs: "add a template, run `scaffold`, and see whether anything catches the divergence before this prose does."

Procedure:
1. `cp research_vault/templates/vault/system/templates/daily.md research_vault/templates/vault/system/templates/probe-scratch.md` (a scratch template, simulating a new template landing).
2. Ran the full offline suite: `.venv/bin/python -m pytest tests -q`.
3. Observed: **5 failures**, all in the code layer, none in the SKILL.md prose layer:
   - `tests/test_scaffold.py::test_scaffold_creates_the_complete_okf_vault_and_returns_paths` — hardcoded `EXPECTED_CREATED` list diverged from `scaffold_vault()`'s actual return.
   - `tests/test_scaffold.py::test_scaffold_commits_only_its_created_paths_and_preserves_user_index`
   - `tests/test_scaffold.py::test_scaffold_cli_prints_the_created_paths` — CLI stdout now includes `system/templates/probe-scratch.md`, diverging from the same hardcoded list.
   - `tests/test_scaffold.py::test_scaffold_cli_requires_literal_rw_consent_and_installs_only_rw_workflow`
   - `tests/test_templates.py::test_all_canonical_template_paths_are_packaged` — packaged-template inventory test caught the new file too.
   - Result line: `5 failed, 1557 passed, 7 skipped`.
   - `tests/test_skill_files.py` (the SKILL.md prose pin) **did not fail** — it only checks for six specific path substrings plus two honesty-rule phrases, none of which reference the new template.
4. Reverted: `rm research_vault/templates/vault/system/templates/probe-scratch.md`. Confirmed clean tree (`git status --porcelain` empty) and suite back to baseline: `1562 passed, 7 skipped`.

**Finding:** the probe confirms the card's diagnosis exactly. A new template landing is loudly caught at the code layer (`test_scaffold.py`'s own hardcoded `EXPECTED_CREATED`, and `test_templates.py`'s packaged-path inventory) — but nothing ties those code-layer tests to the SKILL.md prose's separate 14-path enumeration. The prose inventory could go stale silently forever without failing a single test. That is precisely the duplication the card diagnoses: two sources of truth for one fact, and only one of them (the code layer) is actually defended by a test that would notice drift.

## What I implemented

Per the brief's Step 1 and the card's adjudicated ruling ("C-6 | Drop the inventory. The 14-path list duplicates what the command prints; 'report its exact printed created paths' was already the right instruction standing alone" — Deliverable: *repair*):

Replaced `skills/setup-vault/SKILL.md`'s scaffold paragraph. Old text enumerated 14 individual paths plus "system/templates/ daily, literature, project, and synthesis templates" (18 total paths) by hand. New text:

> Do not create directories or files by hand, substitute custom CI, use `git add .`, or make an unrelated commit. Run it: scaffold prints every path it created; report that list verbatim, and never present a path it did not print as committed. Paths such as `AGENTS.md`, `inbox/review-queue.md`, `system/templates/`, `system/bases/`, `system/glossary.md`, and `.git/hooks/pre-commit` are the contract, not an inventory of everything scaffold can create; CI paths appear only for their separately consented flags, and repairing an existing vault may create fewer paths than a fresh one.

The card's decided deliverable sentence, confirmed verbatim from the card itself (`research/validation-slice/2026-08-22-skills-layer-audit.md:257`, not clipped from the dispatch):

> "scaffold prints every path it created; report that list verbatim, and never present a path it did not print as committed"

Shipped exactly, joined by a colon after "Run it" so the imperative-to-execute instruction (previously "Run scaffold and report its exact printed created paths") is preserved rather than silently dropped. I capitalized nothing mid-quote — "scaffold" stays lowercase as in the card, attached to "Run it:" so it never opens a sentence.

The six test-pinned paths (`AGENTS.md`, `inbox/review-queue.md`, `system/templates/`, `system/bases/`, `system/glossary.md`, `.git/hooks/pre-commit`) are kept, reframed explicitly as "the contract, not an inventory of everything scaffold can create" — matching the brief's "one sentence: the pinned six are the contract; the CLI's scaffold output is the full list." The other eight paths from the old enumeration (`.gitignore`, `.research-vault/machine.json`, `index.md`, `literatures/.gitkeep`, `log.md`, `log/.gitkeep`, `projects/.gitkeep`, `synthesis/index.md`) are dropped — they were the stale-able inventory, not load-bearing.

Kept: the CI-conditional-paths caveat and the "may create fewer paths when repairing" caveat — these are behavioral notes about scaffold's output, not part of the enumerated inventory, and dropping them wasn't asked for.

## Factual claims checked against the tree (per the verbatim-governs-substance-but-tree-governs-facts doctrine)

1. **"the enumeration matches `research_vault/templates/vault/` exactly, verified file by file"** — checked via `find research_vault/templates/vault -type f`. Result: 13 files (`AGENTS.md`, `gitignore`, `inbox/review-queue.md`, `index.md`, `log.md`, `synthesis/index.md`, `system/bases/open-questions.base`, `system/bases/trust-tier.base`, `system/glossary.md`, `system/templates/{daily,literature,project,synthesis}.md`). These map 1:1 onto the vault-template-derived entries in the old SKILL.md enumeration (with `gitignore` → `.gitignore`). **Confirmed accurate** — no deviation needed.
2. **"`scaffold.py:241` returning `sorted(created)`"** — read `research_vault/scaffold.py`; line 241 is exactly `return sorted(created)`, the last line of `scaffold_vault()`. **Confirmed accurate** — no deviation needed.
3. **`tests/test_skill_files.py:107-121`** (the pin brief cites) — read the file; lines 107-121 are exactly `test_setup_vault_reports_only_scaffold_created_commit_paths`, already scoped to the six paths plus two honesty-phrase assertions (no separate 8-item block existed in this test — the test was already narrow; only the two honesty-phrase substrings needed updating to match the new sentence's wording).

No factual claim in the card was found stale; no deviation from the card's cited facts was required. The adjudication table (`research/validation-slice/2026-08-22-skills-layer-audit.md`, §5, which "supersedes the per-card State fields") independently confirms the same ruling for C-6: "Drop the inventory... 'report its exact printed created paths' was already the right instruction standing alone" — consistent with what I shipped.

## Tests

- Targeted: `.venv/bin/python -m pytest tests/test_skill_files.py tests/test_skill_contracts.py -q` → `62 passed`.
- Form gate: `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` → all 8 hooks Passed.
- Full offline suite: `.venv/bin/python -m pytest tests -q` → `1562 passed, 7 skipped` (matches the documented baseline exactly).

## Files changed

- `skills/setup-vault/SKILL.md` — scaffold paragraph rewritten (inventory dropped, honesty rule kept and reworded to the card's decided sentence).
- `tests/test_skill_files.py` — `test_setup_vault_reports_only_scaffold_created_commit_paths`'s two honesty-phrase assertions updated to match the new wording (`"report that list verbatim"`, `"never present a path it did not print as committed"`); the six path assertions and the docstring are unchanged.

## Self-review

- Do the six pinned paths still appear as true statements in the shipped text? Yes — all six (`AGENTS.md`, `inbox/review-queue.md`, `system/templates/`, `system/bases/`, `system/glossary.md`, `.git/hooks/pre-commit`) are named as scaffold-owned contract paths, and all six are real paths scaffold creates (verified against `scaffold.py` and the templates tree).
- Would the pin still fail if someone claimed an unprinted path was committed? Yes — the test asserts the literal phrase "never present a path it did not print as committed" is present in the skill text; deleting or weakening that clause fails the test, and the six path names must also still appear.
- Checked `test_setup_vault_uses_scaffold_with_separate_ci_consents` (a different test in the same file) doesn't collide: it separately pins `"Do not create directories or files by hand"` and `` "use `git add .`" ``, both preserved verbatim in the rewritten paragraph's first sentence.
- No other test, skill file, or doc in the repo quotes the old 18-path enumeration or the old "Say only scaffold-created paths are committed" phrasing (checked via grep across `tests/`, `skills/`, `docs/`).

## Concerns

None. The probe, the card's adjudicated ruling, and the shipped diff all agree, and both of the card's factual citations held up against the tree with no deviation needed.
