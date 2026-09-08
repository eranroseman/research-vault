# Part A deferred findings

Minor findings raised by the per-task reviews of `2026-09-07-ingest-redesign-a-capture.md` and
deliberately held out of their tasks' fix loops. None blocks a merge; all are cosmetic or
documentation-level.

Rows are appended by the controller in the same commit as the task that recorded them, so the
record is written at the moment the finding is deferred rather than assembled at the end.

**Task 20's whole-branch review dispositions every row.** Each ends **fixed**, naming the commit,
or **declined**, with the reason written into the row. Rows still open after that review become
one repository issue (`gh issue create --label ready-for-agent`) with the open rows as its body.
No issue is filed before then: `docs/agents/issue-tracker.md` asks that the tracker carry findings
no spec or plan will claim, and this plan claims all of these.

## Deferred minors

| #   | File                                           | Finding                                                                                                                                                                                                                                                                                                                                                                           | Task | Disposition |
| --- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | ----------- |
| 1   | `research_vault/bibliography.py.manifest.json` | Lists mutate4py entries for ten helpers deleted with the auto-export contract. Not a constraint violation: sidecar deletion is mandated only for a deleted module, and this module survives. The gate rewrites its own sidecar on its next run.                                                                                                                                   | 2    |             |
| 2   | `research_vault/lints.py.manifest.json`        | Lists `func/_note_status` and `func/lint_screening_state`, both deleted. Same class as row 1.                                                                                                                                                                                                                                                                                     | 4    |             |
| 3   | `research_vault/__main__.py.manifest.json`     | Lists entries for `cmd_archive_source`, `cmd_import_note` and other deleted commands. Same class as row 1.                                                                                                                                                                                                                                                                        | 1, 5 |             |
| 4   | `research_vault/verify.py.manifest.json`       | Lists entries for `_archive_outcomes` and other deleted functions. Same class as row 1.                                                                                                                                                                                                                                                                                           | 1    |             |
| 5   | `research_vault/notes.py:157`                  | The pass-through-fields comment still names `archive-url` as an example of a field the renderer carries through unchanged. Accurate for historical notes under ADR 0003, but nothing writes the field going forward.                                                                                                                                                              | 1    |             |
| 6   | `research_vault/lints.py` (`_origin`)          | The `fallback or RepoPath(rel)` truthy branch is unreachable: every surviving caller passes `""`. **Created by Task 4**, which deleted `lint_screening_state`, the only caller that passed a truthy fallback — not pre-existing. Collapsing the signature was judged scope creep at the time.                                                                                     | 4    |             |
| 7   | `tests/test_canonical_form.py:11-13`           | The docstring still says "The tenth, `vault/index.md`" after the deletion of `literature.md` left nine templates. The count was corrected in the first sentence and not the second.                                                                                                                                                                                               | 5    |             |
| 8   | `tests/test_notes.py:115`                      | `test_generated_metadata_is_substantive_canonical_content` builds `generated` as a bare string rather than the `{by:, at:}` mapping `notes._valid_generated` defines. Not a no-op, but a mapping-aware exemption would slip past it.                                                                                                                                              | 5    |             |
| 9   | `.github/workflows/quality.yml:52-56`          | The CRAP-ceiling comment still describes `_bump_generated` in `archive.py`, a module Task 1 deleted. Pre-dates Task 3, which was told to make only the change its brief named. **Part B Task 4 removes the whole block**, so this needs attention only if Part B slips.                                                                                                           | 3    |             |
| 10  | `research_vault/verify.py:558`                 | `_mutate_marker` skips `wiki/` via `path.relative_to(vault_root).parts[0] == "wiki"`. Correct today, and the brief's printed `startswith("wiki/")` would never have fired — but it silently assumes every caller passes an absolute `vault_root`. `decode_repo_path(relative).startswith(b"wiki/")` would not.                                                                    | 6    |             |
| 11  | `tests/` (coverage gap)                        | No test exercises `verify` or `structure.check_reserved` against the shape `scaffold_vault` actually produces: `tmp_vault` hand-creates `wiki/concepts`, while a freshly scaffolded vault has no `wiki/` until first compile. The dangling `[wiki/](wiki/)` link and "Read `wiki/index.md`" in that interval are plan-mandated and crash-free; the untested shape is the finding. | 6    |             |

## Do not fix

Decided non-actions. Recorded so a later reader who finds them does not mistake them for rot.

| Finding                                                                                                                                                                                | Why it stands                                                                                                                                                                                                        |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The check value `quote:<claim-link>:managed-region` survives in `research_vault/events.py:12,297`, `verify.py:711` and `quotes._extra`, naming a managed region that no longer exists. | It is a durable value already written into vault `verified` events. Renaming it would invalidate those records, which ADR 0003 forbids. A name that outlived its referent is the correct outcome here, not a defect. |
| `docs/terminology.md` §4.4's preamble example uses the same `quote:…:managed-region` spelling.                                                                                         | Same reason: the document describes values that exist in written records.                                                                                                                                            |

## Process notes

Lessons from running this plan under `superpowers:subagent-driven-development`. They are recorded
here because a committed file is the only home that survives the workspace deletion at Finish;
"not issue-shaped" is a reason not to file them, not a reason not to write them down.

1. **An interim fix must not be relayed to a running implementer as an instruction.** The
   controller passed a plan author's in-progress correction ("drop the rename log") to Task 6's
   implementer before the replacement text was settled, then had to retract it when the answer
   turned out to be "the applied propagation plans" rather than a deletion. It cost nothing only
   because the implementer had not reached that file yet, twice. The fix adopted mid-run: the
   author marks every message **settled** (in the plan on main at a named commit) or **pending**
   (a decision is coming), and a pending item is held, or sent only as "stop before this line",
   never as an instruction. Task 6's implementer independently rejected the bad message after
   finding it contradicted the repository — that verification is now a standing instruction in
   every dispatch.
2. **A verification grep run during a live implementation must read a committed ref, not the
   working tree.** Checking a hazard's call sites with `grep` over the worktree while Task 4's
   implementer was editing `lints.py` returned a line number belonging to neither the before nor
   the after state. `git show HEAD:<path>` is the only stable view while a subagent holds the
   tree.
3. **Diff from the merge base, never from the branch tip, to decide whether a merge is safe.**
   `git diff --stat <branch-tip> main` counts the branch's own commits as reversals and can report
   dozens of files where the real incoming set is three. `git diff --stat $(git merge-base HEAD main) main` is the question actually being asked.
