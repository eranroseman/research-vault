# Ingest redesign, Part A (capture) — results

- **Date:** 2026-09-13
- **Method:** `docs/superpowers/plans/2026-09-06-ingest-redesign-a-capture.md` (twenty tasks) run under `superpowers:subagent-driven-development` across two controller sessions, with a fresh implementer and a two-stage review per task, a whole-branch review over the final diff with one fix wave and a scoped re-review, and one attended live leg on the test instance. The plan's printed code was folded to the committed tree after each task closed, so the plan on `main` is what runs.
- **Spec:** 2026-09-06-import-redesign-design.md
- **Binds:** nothing — this records what the execution produced and measured; the spec is the current state, the plan the authority for what was built.

## What landed

Merge commit `f2d3921` on `main`, `--no-ff`, pushed 2026-09-13: 137 commits, 118 files, +10,675 / −10,526. Tasks 1–15 ran under the first controller session (through `9cdbe91`, Task 15's close); Tasks 16–20 under the second (16 `ab3604a..c25d3e8`, 17 `bb53a2b..b3c492c`, 18 `e22f1b2..ec136c2`, 19 `ea76fad..314196f`, the post-review fix wave `a6b4b86..3fd6087`).

Retired: the web archive, the Better BibTeX auto-export contract, verify's DOI and metadata checks, screening state, the managed region, `import-note` and the `import-source` skill. Renamed: `citekey` → `citationKey`; the synthesis layer moved under `wiki/`. Built: the Zotero client for the local API, the `fulltext/` text layer, the machine-written literature note with its provenance tuple, the lifecycle linter (one code path at capture and verify, pre-commit held), the `capture` verb, plan-and-apply propagation with its applied-plan record, the captured-set lint at the capture→compile seam, doctor as setup's linter with thirteen probes, the `add` verb, open points 07, 08 and 09 with `--as-of`, and the `capture-source` and `setup-vault` skills.

## Verification, measured

| Command                                       | Result at `9cbe559`                                                                                                                                                                                                                                                                                                                                                                       |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| offline suite (`-n auto`, swept tree)         | 1717 passed, 4 skipped, 0 xfailed                                                                                                                                                                                                                                                                                                                                                         |
| `ruff format --check`, `ruff check`, `mypy`   | clean                                                                                                                                                                                                                                                                                                                                                                                     |
| `crap4py --max-crap 30`                       | exit 0 after the fix wave (before it: `cmd_add` 72.0, `_worktree_path_hash` 50.7, `_snapshot_path_hash` 31.3, `capture` 31.1 — three extractions and five tests)                                                                                                                                                                                                                          |
| read-only live legs (`RV_LIVE=1`)             | 13 passed, 1 skipped (`RV_LIVE_NET`)                                                                                                                                                                                                                                                                                                                                                      |
| doctor, live, both instances                  | `write-guard` MATCHED (the wrong server id answered 412); `translator-formats` UNMATCHED on 10.0.1 and 10.0.2 — `format=csljson` answers 200, against the spec's 500 of 2026-09-04                                                                                                                                                                                                        |
| mutation gate (mutate4py, serial)             | not read as a verdict: eight new modules have no baseline rows, so every survivor is "new" by construction; 20 of 23 changed modules measurable; `events.py`, `frontmatter.py`, `gitstate.py` unmeasured; the per-module survivor lists are Plan W Task 25's triage input (`docs/superpowers/specs/2026-09-06-import-redesign-part-a-mutation-survivors.md`, run continuing at `9bd1f1c`) |
| `git status --porcelain` in the main checkout | empty before and after the merge                                                                                                                                                                                                                                                                                                                                                          |

**The attended propagate leg** (test instance `Tdoqsn2J4q4h`, Zotero 10.0.2, Better BibTeX 9.0.64; one Always-Allow click by the operator): item `ALKT2NF7` re-keyed by `PATCH /api/users/0/items/ALKT2NF7` on the native `citationKey` field with `If-Unmodified-Since-Version: 1708` → 204, `Last-Modified-Version: 1714`, BBT agreeing within about two seconds, `extra` untouched — the legacy Extra line was never needed; the lifecycle linter reported `re-keyed` through `capture`'s refusal; `propagate` planned and applied (note renamed, `projects/leg.md` rewritten, recapture NOOP, a fresh plan found nothing); restore PATCH → 204; production received one read-only probe. Research records 449–451 in `docs/research/2026-09-05-zotero-api-reading.md`. No write-capable leg exists in the suite: `add`, `authorize` and `create_items` are offline-tested against recorded wire shapes.

**Invariant 5**, measured again: `main` has no branch protection, no rulesets, and this checkout has no pre-commit hook — issue #130.

## Review

Whole-branch review (`fable`, over the 1.4 MB diff `9d10db3..09f2eb8`): **with fixes**, no Critical; seven Important, ten Minor, four CRAP regressions, a row-by-row triage of every open deferred finding. The one design-level finding: a refresh of a re-keyed item wrote a second note beside the old and dead-ended propagation — capture now refuses while the old note exists. All Important items, the CRAP four, three Minors and seventeen deferred rows landed in one fix wave; the scoped re-review returned clean.

Per-task: every task passed spec compliance on first or second review; quality took one to three fix rounds (Task 18 three, Tasks 14, 16, 17 and 19 two, Tasks 11–13 and 15 one to three). Sixty-one deferred findings were recorded during execution; every one ends fixed with its commit named, declined with its reason, or open in issue #129 (fourteen rows plus the review's extras). Nine process notes stand in `docs/superpowers/plans/2026-09-06-ingest-redesign-a-deferred.md`.

## What moved in the spec because of this run

Open points 07, 08 and 09 closed; the re-keyed refusal; the captured-set lint reporting an unreadable note; the native citation-key PATCH measurement; the csljson route's 200 recorded beside the 500 (decision 13 stands; Part B re-measures); the greenfield consequence stated to the operator; invariant 5 tracked as #130. The assembly spec gained §7.1.1: Plan W (#42) runs between this part and Part B.

## What remains

- Issue #129: the deferred findings the review ruled real but not merge-blocking, with the leg's two behaviour findings as a comment.
- Issue #130: the write-side gate.
- Plan W on `main`, then Part B (`2026-09-06-ingest-redesign-b-compile.md`) from a post-Plan-W `main`; Part B needs the operator present for its tracers (Obsidian open) and possibly one consent click on the test instance.
- The mutate4py run in `/tmp/rv-gate`, finishing as data; `git worktree remove --force /tmp/rv-gate` when it ends.
