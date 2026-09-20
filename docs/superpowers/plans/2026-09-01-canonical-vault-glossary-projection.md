# Canonical vault glossary projection — implementation plan

Disposition: historical (2026-09-06)

> **Execution:** use `superpowers:subagent-driven-development`. The work is one
> cohesive, reviewable change: its content, packaged asset, renderer, and
> preservation contract must land together.

**Goal:** Make `CONTEXT.md` the one canonical domain glossary and create each
new vault's `system/glossary.md` as a valid OKF `guide` whose body is exactly
that glossary. The generated file remains a normal, user-owned file.

**Design:** [canonical vault glossary projection design](../specs/2026-09-01-canonical-vault-glossary-projection-design.md)

**Constraints:**

- Keep `CONTEXT.md` a glossary: definitions and naming distinctions only.
  Put operating instructions in the vault `AGENTS.md`; do not record the
  separately pending project-lifecycle decision here.
- Read the canonical content via `importlib.resources`, not a path relative to
  the source checkout. The distributed package must carry the content.
- The repository source may use a symlink as package plumbing, but a scaffolded
  vault must receive a regular file and re-scaffolding must never overwrite it.
- Work only in this isolated worktree. Commit with explicit pathspecs.

## Task 1: Canonicalize and render the vault glossary

**Files:** Modify: `CONTEXT.md`, `research_vault/scaffold.py`,
`research_vault/templates/vault/AGENTS.md`, `tests/test_scaffold.py`,
`tests/test_templates.py`. Create: `research_vault/templates/context.md` as a
symlink to `../../CONTEXT.md`. Delete:
`research_vault/templates/vault/system/glossary.md`.

- [ ] **Step 1: Write the failing contracts before implementation.**

  - In `tests/test_templates.py`, replace the static
    `vault/system/glossary.md` inventory entry with `context.md`. Assert that
    the packaged `context.md` bytes equal the root `CONTEXT.md` bytes. Remove
    the several-hundred-line static glossary-content assertion; this test must
    make a second authored glossary impossible.
  - In `tests/test_scaffold.py`, after scaffolding, parse
    `system/glossary.md` and assert its frontmatter is exactly
    `{"type": "guide"}` and its parsed body equals the packaged canonical
    context source byte-for-byte. Assert the output is a regular file, not a
    symlink.
  - Extend the idempotence fixture to pre-create
    `system/glossary.md` with a human value. Assert it is absent from
    `created`, unchanged after the first scaffold, and unchanged after the
    second.
  - Add a preflight regression analogous to the existing staged-deletion test:
    a staged deletion of `system/glossary.md` must raise before scaffold writes
    it. This proves it remains an owned target even though it is not a vault
    template file.
  - Run
    `~/New folder/.venv/bin/python -m pytest tests/test_templates.py tests/test_scaffold.py -q`
    and confirm these expectations fail for the current implementation.

- [ ] **Step 2: Make `CONTEXT.md` the complete, concise domain glossary.**

  - Remove the repository-only reference to `docs/terminology.md` and any
    packaging, writer, or implementation detail. Retain only the title,
    sections, definitions, and useful naming distinctions.
  - Merge the template-only domain terms into their natural sections:
    `Synthesis note`, `System folder`, and `Venue`. Define `Machine surface`
    because the generated agents guide uses it, distinguishing the term from a
    particular writer or enforcement mechanism.
  - Retain the stronger existing definitions for `Analysis`, `Report`, and
    `Closing check`; keep the screening-state note-level/deprecated-claim
    distinction and the bibliography-export/citability distinction.
  - Define an `Update notice` in plain language, including its two dates
    (publication and detection), instead of the unexplained term
    “bi-temporally.” Do not add or choose project publication-state values.
  - Keep every definition short enough to serve as a shared vocabulary rather
    than a procedure; a reader who needs an operating rule should be directed
    by the relevant `AGENTS.md` instruction, not a duplicated glossary entry.

- [ ] **Step 3: Preserve the operational rule in the operating guide.**

  - Add one concise instruction to the vault template `AGENTS.md`: Better
    BibTeX is the sole writer of `system/bibliography.json`; users and other
    tools must not write it. Keep the existing machine-surface rule, now using
    the canonical term rather than redefining it.

- [ ] **Step 4: Replace the static template with a packaged projection.**

  - Create `research_vault/templates/context.md` as the exact source-tree
    symlink `../../CONTEXT.md`; verify `git ls-files -s` records mode `120000`.
    It lives outside `templates/vault`, so generic vault-template copying never
    emits it directly. Existing `"templates/**/*"` package data must include
    its dereferenced contents in a built distribution.
  - Remove `research_vault/templates/vault/system/glossary.md`.
  - In `research_vault/scaffold.py`, introduce explicit constants for
    `system/glossary.md` and its fixed
    `---\ntype: "guide"\n---\n\n` envelope. Add a narrow helper that, when the
    target is absent, reads `templates/context.md` through
    `importlib.resources`, opens the target with exclusive creation, writes the
    envelope followed by the unchanged body, and appends the glossary path to
    `created` exactly once.
  - Invoke that helper during scaffolding. Add the glossary path explicitly to
    `_owned_paths` and `_preflight_conflicts`; the former keeps symlink safety
    and the latter prevents a staged deletion from being silently recreated.
    Preserve the existing behavior for every other template and output path.

- [ ] **Step 5: Prove source, generated output, and distribution behavior.**

  - Re-run the focused tests from Step 1 until green, then run the complete
    suite with
    `~/New folder/.venv/bin/python -m pytest -q`.
  - Build a wheel into a fresh directory under `/tmp` without changing the
    worktree, inspect it, and prove it contains
    `research_vault/templates/context.md` as regular package data whose bytes
    equal `CONTEXT.md`. Use the project virtual environment and its available
    build frontend; if the `build` module is unavailable, use
    `pip wheel . --no-deps --no-build-isolation --wheel-dir <fresh-/tmp-dir>`.
  - Confirm `git status --short` contains only the files named in this task.
    Commit with an explicit pathspec, for example:
    `git commit -m "feat: generate vault glossary from canonical context" -- CONTEXT.md research_vault/scaffold.py research_vault/templates/context.md research_vault/templates/vault/AGENTS.md research_vault/templates/vault/system/glossary.md tests/test_scaffold.py tests/test_templates.py`.

## Review gates

1. **Task reviewer:** inspect the diff and tests for duplicate glossary
   authorship, resource-loading assumptions, source-symlink versus generated-
   file confusion, accidental overwrites, and a leaked lifecycle decision.
2. **Final reviewer:** inspect the full branch against this plan and the
   approved design; run the focused tests if evidence is incomplete.

## Acceptance criteria

- There is one authored set of domain definitions: `CONTEXT.md`.
- A fresh vault contains an OKF `guide` at `system/glossary.md`, with exactly
  the canonical body and no output symlink.
- Existing vault glossaries are untouched, including a staged deletion case.
- The canonical body is available from package resources after building a
  wheel.
- Tests and template inventory describe the new source of truth, and the full
  suite passes.
