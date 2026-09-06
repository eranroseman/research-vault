# Post-Q batch — independent review of the plan and its SDD ledger

Disposition: historical (2026-09-06)

Independent reviewer, read-only pass, 2026-08-24. Reviewed: the plan at `origin/main` `ddc43a1` and the SDD ledger on `fix/pre-slice-batch` at tip `ebea360` — **22 commits ahead of `origin/main`, 74 behind**, merge-base `002cb25`. Method: programmatic claim-checking rather than reading and judging — `git rev-list --count` for divergence, `git merge-tree` for conflict prediction, a grep-derived state spine over the 159 KB ledger, artifact counts by `ls | wc -l`, and source reads at named line numbers. Nothing in the repository or the worktree was modified during the pass. Commissioned after the pass: this record, a review of the two unreviewed addenda, and a re-run of the ledger's SHA-walk after the boundary merge.

Artifacts read: `.claude/worktrees/fix+pre-slice-batch/.superpowers/sdd/2026-08-22-post-q-batch/`
— progress.md at 159 KB, 15 briefs, 13 report/review pairs, 21 review diffs.

This is a review of the plan and its execution record — state, drift, open items, risk.
It is not a re-review of the branch's code; every landed task already carries a
three-lens adversarial review in that directory.

## 1. State

Complete with a clean review (12 completion lines): Tasks 1, 2, 2b, 2c, 3, 4, 5, 6, 7, 8, 9, 10.

Not complete:

| Item                            | State                                                                                                                                                                                                                                                     |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Task 8b                         | Verify-only. Its content landed on main at `d7fa91b`, but the plan still owes an executor "verify both are present and land nothing." `grep -n "^Task 8b:" progress.md` returns **nothing** — the verify never ran in this dispatch and is not scheduled. |
| Task 2d                         | Landed `c418cf7`. Review returned spec COMPLIANT / quality NEEDS FIXES with one confirmed Important. Fix ruled, scoped, and **held — never dispatched**.                                                                                                  |
| addendum (Task 9)               | `eff8d67` `feat: inbox summary emits oldest_age_days` — landed 12:30, after the ledger's last write at 12:27. Unrecorded, unreviewed.                                                                                                                     |
| addendum (Task 4)               | `ebea360` `docs: find-sources vendoring note records the XML parsing boundary` — landed 12:32. Unrecorded, unreviewed.                                                                                                                                    |
| Task 2e                         | Added 2026-08-24, queued behind 2d's review. Its Step 2 pre-check caught a destructive defect before dispatch.                                                                                                                                            |
| Tasks 11–13                     | Part 1 remainder, not started.                                                                                                                                                                                                                            |
| Tasks 14–21, 17b, 19b           | Part 2 (trust-core remediation), not started.                                                                                                                                                                                                             |
| Task 22                         | Part 3, not started.                                                                                                                                                                                                                                      |
| Tasks 23, 24, 24b, 24c, 24d, 25 | Part 4 (mutmut adoption), not started; runs post-merge on main.                                                                                                                                                                                           |

Branch: 22 commits ahead of `origin/main`, **74 behind** (`git rev-list --count`), merge-base `002cb25`.
Working tree clean. Latest commits at 12:32; ledger last written 12:27 — a controller
session may still be live in this shared checkout.

## 2. Findings — execution

### 2.1 Task 2d's confirmed Important is open at branch tip, with two unreviewed commits on top

At `ebea360`, the three shipped templates cover four surfaces:

```
literatures/
log/
inbox/review-queue.md
system/bibliography.json
```

`research_vault/lints.py:109` `_is_append_only_path` names three durable-append
surfaces, and its own docstring says so. The third — `projects/*/search-log.md` — is
covered by none of the three files. The ruled fix (add search-log; anchor to
`/literatures/` and `/log/`; one-line pointer at the source of truth in each file) is
unshipped. `.editorconfig` still uses `[literatures/**]` / `[log/**]`, the unanchored
any-depth form the ruling rejected.

The hold reason recorded in the ledger — "the two-addenda implementer is LIVE" — expired
at 12:32. Nothing records that the block cleared, because the ledger's last write predates
both addenda commits.

**Precision note on the ruled fix.** The pointer is specified as naming
`_is_append_only_path` (plus the bibliography) as the source of truth. But the set the
ignore files protect is *machine-owned surfaces*, not *append-only surfaces*:
`literatures/` and `system/bibliography.json` are owned by other mechanisms and are not in
`_is_append_only_path`. A pointer naming one authority for a four-item list drawn from two
authorities reproduces the imprecision it is meant to fix. The ruling already says "plus the
bibliography", so the one genuinely unattributed entry is `literatures/`. Name its owner too,
or word the pointer as "machine-owned" rather than "append-only".

### 2.2 `eff8d67` is the only code commit on this branch never reviewed

`research_vault/inbox.py` +18, `tests/test_inbox.py` +57. It changes the shape of
`inbox.summary()`, which `__main__.py:761` serialises straight to CLI JSON. That is a public
output contract on a branch whose whole method is three-lens review of every code change.
`ebea360` is one prose line and low-risk by comparison, but is equally uncovered.

The ledger's own programmatic integrity audit ran at 20 commits with 2 explained-uncovered.
It is now 22 commits with 4 uncovered, and no `review-c418cf7..ebea360.diff` exists.

### 2.3 `eff8d67` lands the fact but leaves its consuming surface unwired

The commit's stated rationale is that project-flow's inbox guard asks the agent to judge
staleness without a reliable clock. `skills/project-flow/SKILL.md:25` still reads "Report
the unacknowledged count and the oldest entry's date" — it does not name `oldest_age_days`.
`skills/setup-vault/SKILL.md:34` already asks for "the inbox count and oldest age", so the
new key has a consumer that cannot know it exists. The mechanism shipped; the prose that
motivated it did not move.

(The commit's withdrawal of `aging: true` checks out: project-flow:25 names the Whittaker
inbox-rot guard but states it in continuous terms with no numeric threshold. The plan's
Task 9 addendum text asserting a "Whittaker threshold" is the thing that was wrong.)

### 2.4 `c418cf7`'s commit body carries two confirmed false statements

A brief cited at a `docs/superpowers/sdd/...` path that exists nowhere, and
igorshubovych/markdownlint-cli called a fork when it is the canonical repo. Recorded in the
ledger as the 14th instance of the run's through-line, scheduled for correction in the held
fix, still uncorrected. With `.git-blame-ignore-revs` deleted on the grounds that the commit
message *is* the record, this is not cosmetic.

### 2.5 The `.editorconfig` template ships a rationale the ledger disproved

The 20-line header claims `root = true` means "no ancestor .editorconfig is read, so these
overrides cannot be diluted by one". Measurement showed closer-file precedence already
guaranteed that; what `root = true` actually blocks is ancestor-sourced charset/end_of_line
— which the same comment separately, and correctly, describes. Keeping the line is right for
a better reason than the one given. The rationale is near-duplicated at
`tests/test_templates.py:325-333`, so it is two copies of the weak argument.

## 3. Findings — the plan

### 3.1 The plan no longer matches its own stated goal

The header calls it "the single dispatch between Plan Q's merge and slice Phase 2 —
instrument freeze for §9": a rename, a routing index, nine prose corrections, four code
fixes. That is 13 tasks. The plan now carries **35**, across four parts, including a full
mutation-testing tool migration, CI supply-chain hardening, dependency version currency, a
suite-hermeticity rework, and a comment-hygiene sweep.

Part 4 (23, 24, 24b, 24c, 24d, 25) is a separate project by the plan's own account: it is
marked non-gating, it runs *after* Task 21's merge, and it executes on main rather than this
branch. It shares nothing with the pre-slice batch except a temporal boundary. Recommend
splitting it into its own plan file. Keeping it here makes the plan that gates the slice
look four times larger than the work that actually gates the slice.

### 3.2 The checkbox contract is dead

The plan header states steps use `- [ ]` for tracking. At `origin/main`: 133 unchecked,
3 checked — and all three checked boxes belong to Task 8b's verify-only steps. Twelve tasks
are complete and not one step box is ticked. Tracking lives entirely in progress.md.

This is the plan's own claims-must-be-observed doctrine, unapplied to the plan. Fix it in
the direction that is true: state that the SDD ledger is the tracker and the boxes are
authoring structure, or maintain them. Do not leave a header asserting a mechanism nobody uses.

### 3.3 The branch is 74 commits behind main and already conflicts

`git merge-tree origin/main fix/pre-slice-batch` reports content conflicts in two files:

- `docs/superpowers/plans/2026-08-22-post-q-batch.md`
- `docs/terminology.md`

Terminology is the substantive one: main changed +60/-62 lines while the branch changed
+12/-12, and the branch's edits are in §4.3 (Task 1's skills row) and §4.4 (Task 10's
`not-imported` row). Main has also done a `research/` reorg that moved every audit doc out of
flat `docs/`, deleted `.git-blame-ignore-revs`, and reworked pyproject and CI.

Task 21 lists "merge and push" as a step with no integration budget. Part 2 is eight more
code tasks touching `checks.py`, `inbox.py`, `notes.py` — the same file family main has been
editing. **Recommend merging main into the branch now, at the Part 1 / Part 2 boundary,**
rather than discovering a two-file conflict plus a doc reorg at the end of thirty commits.

### 3.4 The worktree's plan copy is stale, and the ledger says to use it

The worktree copy lacks Tasks 2b, 2c, 2d, 2e, 8b, the Task 9 addendum, the Task 4 XML step,
and the corrected content-source paths — all of which have been executed. The global
constraint says read the plan from `origin/main`, and the controller does. But the ledger
head still records "Briefs are generated from the worktree copy, which is already the
practice." That sentence was true for Task 22 and is now false and hazardous. Correct it in
the ledger; a post-compaction reader following it would brief off a plan missing five tasks.

### 3.5 Thirty-three deferred minors are routed nowhere

`grep -c "minor (deferred)" progress.md` → 33, across 12 tasks, plus 2 more from 2d's review,
plus the Task 4 SLICE-TIME items and two routings to a "post-slice polish ledger".

The polish ledger does exist — as the *Skills polish pass* section of
`docs/research/validation-slice/2026-08-22-skills-layer-audit.md` on `origin/main`, carrying 17
numbered items. But every one of those came from the audits, not from this run: not one of
the 33 deferrals has been written into it. (The branch cannot see that file at all — it still
carries the pre-reorg flat `docs/2026-08-22-skills-layer-audit.md`.)

AGENTS.md names GitHub Issues as the tracker; `gh issue list --state all` shows only #16 and
#17 open, both plan-referenced defects rather than deferrals.

So the destination is not missing — the routing is. Every one of the 33 currently dies with
progress.md. Append them to the polish-pass section, file them, or rule them written off,
before the ledger is archived.

## 4. Risk ahead

1. **Task 2e Step 2 remains the sharpest hazard, and its pre-check earned its keep.** Dry-running
   mdformat over the templates found it escapes Obsidian wikilinks, which would have shipped a
   broken `index.md` — six folder links and both Base embeds dead — into every future vault,
   with all pins green. The dialect-ownership ruling that replaced the filename exception is the
   right shape.
2. **The same failure shape now sits in 2d's held fix.** An anchored pattern a tool does not
   honour matches nothing, silently converting partial protection into zero while every pin
   stays green. The dispatch requirement — demonstrate coverage per tool with the tool's own
   output, not its documentation — must survive into the actual brief.
3. **Suite green is machine-dependent until Task 24c.** 97 connects to localhost:23119 in an
   "offline" run; Zotero up means live calls, Zotero down means 5 s timeouts. Every
   "1548 passed = baseline" line in this ledger was recorded under that condition. 24c sits at
   the far end of Part 4, *after* the merge that unblocks the slice. Consider pulling 24c Step 2
   (socket block) forward to the Part 1/Part 2 boundary — it is the cheapest way to make every
   subsequent green mean something.
4. **Two human-presence gates**, both correctly flagged in the ledger head: Task 13's consent for
   the `~/kh-vault` commit, and Task 21 Step 3's live suite (Zotero running, real
   `RV_MAILTO`). Task 13's file set is now larger than when written; the class rule handles it.
5. **Task 25 Step 1b** correctly records that the mutation gate has never actually executed —
   push runs no-op by construction and the repo has zero PR runs. Every claim in the gate's
   comment block is reasoned, not observed.

## 5. What is working

The ledger is the strongest artifact here. Three things in particular:

- **Escalation instead of silent resolution.** Task 3's plan conflict, Task 2c's preamble
  concern, and 2d's ignore-file scope all went to a ruling with the reasoning recorded, rather
  than being absorbed by an implementer.
- **Claims checked rather than accepted.** The programmatic SHA-walk of the ledger's own
  recovery map; the EditorConfig `dir/**` semantics verified against two reference cores; the
  dotless packaging pattern verified with a real wheel build and a live `scaffold_vault()`;
  the mdformat dry-run. Each of these caught something eyeballing would not have.
- **The doctrine turned on the instrument.** "My form-gate runs were safe" was examined, not
  asserted — paired porcelain checks, unshared worktree, therefore no stash ever fired.

## 6. Recommended order

1. Update the ledger for `eff8d67` and `ebea360`, and record that 2d's hold cleared.
2. Review the two addenda — `eff8d67` at minimum, as an unreviewed public output-shape change.
3. Dispatch 2d's held fix with the per-tool empirical verification requirement intact, folding
   in the commit-body corrections, the AGENTS.md `.editorconfig` wording, and the `root = true`
   rationale. Resolve the append-only-vs-machine-owned imprecision in the pointer first.
4. Wire `oldest_age_days` into project-flow's prose, or record why not.
5. Merge `origin/main` into the branch. Resolve `docs/terminology.md` deliberately. Two
   constraints: coordinate first with the possibly-live controller session (commits at 12:32
   against a ledger last written at 12:27), and do not land the merge between a held fix and
   its scoped re-review — it would pollute the FIX_BASE diff range.
6. Then Task 2e (it must run after 2b/2c/2d are final), then Tasks 11–13.
7. Split Part 4 into its own plan file; correct the checkbox claim in the header.
8. Route the 33 deferred minors into the polish-pass section or into issues.
9. Schedule Task 8b's verify, or record that it is satisfied by `d7fa91b` and needs no executor.

## 7. Status at commit time

Recorded so this pass reads honestly against a tree that moved while it was being written; the findings above stand as observed at `ebea360`/`ddc43a1`.

- **§3.1 acted on.** `f6b7788` `docs: split Part 4 into Plan W (quality tail)` moved Tasks 23–25, 24b, 24c and 24d into `docs/superpowers/plans/2026-08-24-plan-w-quality-tail.md`. The batch drops from 35 tasks to 29, and the header's single-dispatch claim is true again.
- **§3.2 stands.** The header still asserts `- [ ]` tracking; the plan is 109 unchecked / 3 checked, and all three checked boxes are Task 8b's verify-only steps.
- **A second finding of §2.2's class surfaced while this record was being written.** `750d4c7`
  corrects the plan's Task 4 XML annotation — "no entity expansion" becomes "no EXTERNAL entity
  expansion — internal entities DO expand, probe-verified" (recorded there as planner defect
  6/15). `ebea360` had already copied the uncorrected wording into
  `skills/find-sources/SKILL.md:23`, so the branch ships a false security claim whose first
  half denies the risk its second half names. Raised as Important 1 in the addenda review; it
  must land before Task 21's merge. It is also the concrete cost of §2.2: a reviewed commit
  would have been read against the plan and the claim probed.
- All other findings unchanged at `750d4c7`.
