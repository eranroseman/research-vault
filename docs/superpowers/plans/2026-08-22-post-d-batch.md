# Post-D Batch — Task

> The Plan D follow-up ledger (worktree deleted; this doc is the durable record) + the author-triaged prose/duplication audit. Single Codex pass, one branch, suite green offline AND live per task-group, merge + push in the same motion.

## F-4 RULING (2026-08-22): the information flow enters at admission, not at search

Spec §7's two-flow accounting is explicit: the information flow (find → human admits via Zotero → catalog → integrate) is continuous and project-independent. The shipped surface inverted that by gating entry on a project. Ruled:

- **`import-source` and everything downstream of admission runs standalone** — catalog, index, log, integrate-at-import need no project. A human may admit a source found by any means (a colleague's email, a footnote chase); the harness catalogs it regardless.
- **`find-sources` alone stays project-scoped** — its deliverable is the PRISMA-S trail, which is per-review by definition (the existing ruling stands unchanged).
- Fix whatever check enforces the project gate on the import path; regression test: `import-source` on a fresh vault with zero projects completes catalog/index/log.

## Fixes (from the shipped-state review)

1. **F-5**: `import-source` prose never says where to read the citekey after admission — one sentence (BBT column / citation key in Zotero's UI). First real import hits this.
2. **F-3**: same-day correction impossible — pass `--date` through to the disposition verbs; NEVER a tag suffix (breaks `PUBLISHED_TAG` parsing and F-2's newest-tag ordering; shape recorded by the executor, adopted).
3. `trust-tier` exits 1 where sibling verbs exit 2 — align to the exit-code contract.
4. Empty-directory disagreement between `_require_clean_project` and `_project_differs` — one definition of "clean", tested.
5. `search-log` silently discards cross-kind flags — reject loudly.

## Duplication + prose (audit accepted wholesale — house comment doctrine: postmortems are the author talking to the reviewer, noise once merged; git log holds them)

6. `_validate_optional_text` copied `searchlog.py` ← `inbox.py` → move into `appendlog.py` (the module that exists to stop this drift), import in both.
7. Docstring/comment shrinks as itemized in the audit: `appendlog.py` (module docstring 19→3, condition comment 8→1, fsync 8→1), `searchlog.py` (48→8, `_prepare_append` postmortem → one line), `factcheck.py` (42→~12 keeping copyright/license/pinned-commit — those are load-bearing; `_bucket` 10→0, its sibling docstring covers it), `__main__.py` (`record_finding` 30→~5 keeping the id-collision rationale), `lints.py` (9→2), `webapi.py` bool-docstring kept at 3 lines with the three pasted copies (archive ×2, verify ×1) deleted.
8. Code: `searchlog.py` regex-then-isoformat → isoformat round-trip alone (the round-trip already rejects everything the regex does; drop `re`); `factcheck.ClaimRef.to_dict` → `dataclasses.asdict` at call sites; `lints.py` append-only path test → one expression; the four `cmd_mark_*` → one `{verb: publish.fn}` dict + `cmd_disposition`; frozenset-of-one → inline `check != "factcheck"`.

## Deferred with homes (do NOT implement here)

- Architecture-pass inputs (append to the deepening pass's evidence list, not this batch): `paths.project_dir` extraction; `finding_id` collision guard in `verify._file_effects`; the third `_git` copy; `publish.py`'s private verify imports; `searchlog`'s unused parser + unwired `durable=`.
- Vendored fork (3,478 lines): "re-vendor, never hand-edit" policy makes pruning a policy change, not a cut — flagged as the largest lever if that policy ever reopens; excluded from this batch.
- Plan D checkboxes stay unticked: the merged history is the completion record (AGENTS.md history rule, executor's reading confirmed).
- The two `HARNESS_LIVE_AUTOEXPORT_VAULT` skips stay honest ("not run", never "passed") until the slice's human BBT step exists.

Acceptance: suite green offline and live; F-4's standalone-import regression test present; judged grep confirms no postmortem prose returned; one merge, pushed in the same motion.
