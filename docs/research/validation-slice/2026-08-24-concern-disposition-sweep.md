# Unmerged-concern sweep — post-Q batch, pre-merge gate

Disposition: historical (2026-09-06)

Independent reviewer, read-only pass, 2026-08-24. Commissioned as a merge-gate item: before
`fix/pre-slice-batch` merges and its worktree is removed, every concern raised in a task report
must have a disposition somewhere tracked — an issue, a spec §10 entry, the polish ledger, or an
explicit recorded decline. The reports live under `.superpowers/`, which is gitignored via
`.git/info/exclude`; they do not survive worktree removal.

Scope: all 18 task reports under
`.claude/worktrees/fix+pre-slice-batch/.superpowers/sdd/2026-08-22-post-q-batch/`.
Method: extract every heading matching the concern class (`Concerns`, `Concerns carried forward`,
`Deferred`, `not fixed`, `open question`) — **31 sections across 18 files** — then check each
concern's current state against the tree at branch tip and against every durable destination
(GitHub Issues, `docs/superpowers/specs/2026-08-16-foundation-spec.md` §10, the polish-pass
section of `docs/research/validation-slice/2026-08-22-skills-layer-audit.md`, and the plan itself).
Every state below was checked at tip, not read from the report that raised it.

## Result

**12 concerns have no durable disposition.** Nine of the 31 sections say "None". Ten more are
disposed and verified so below. Nothing was filed or edited by this pass.

## Undisposed — needs a home before merge

### A. Real gaps in shipped guard code (4) — issue class

All four are Task 17b. The 17b report says concerns 1–3 are "being routed to the issue tracker by
the reviewer per their message"; the 17b review says "it should be filed, not left as a paragraph
in a report file that nothing reads again." Neither filed. Tracker holds only #16, #17, #18.

| #   | Concern                                                                                                                                                                                                                                                        | Verified state at tip                                                                                                |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| A1  | `notes.MANAGED_FIELDS` keys `type`, `aliases`, `doi`, `url`, `pmid`, `version`, `accessed` sit outside the closing guard — the Step 1 parametrization scoped `_MACHINE_OWNED_FRONTMATTER_KEYS` to five keys. A hand-edit to `doi` alone passes silently.       | Real.                                                                                                                |
| A2  | Duplicate-key evasion. `frontmatter.parse` is last-key-wins; a duplicated machine-owned key whose final copy matches the base value evades the value comparison. Only `managed-sha256` has an independent duplicate guard. Confirmed real by the 17b reviewer. | Real.                                                                                                                |
| A3  | Renamed files skip the per-key check — the rename is flagged wholesale, so coverage is not lost, but the specific-key diagnostic is absent.                                                                                                                    | Real, lesser.                                                                                                        |
| A4  | Forged attestation passes the guard when `generated.by` is machine-class-shaped.                                                                                                                                                                               | **Not a defect — a stated boundary.** The lint catches accidents and oblivious agents, not deliberate circumvention. |

A4 should not be filed as a bug. It is a design boundary whose only record is the brief and the
report, both untracked. Its home is a spec §10 stated-boundary entry — §10.2, *Identity, records,
and trust model*, in the same register as the human-attestation entry at line 168 (both citations
re-verified against `origin/main` `4a2a476`, after §10's restructure into six themed subsections).

### B. Conditional declines recorded only in untracked files (2)

Task 3 raised two instrument gaps and disposed of each as "worth a card if the class recurs".
That is a real decision, but the condition is recorded nowhere durable, so nothing will ever
notice the class recurring.

- **B1.** The reason-code pin proves accounting, not placement. Deriving which reason codes a
  shipped writer actually files — an AST scan of `inbox.append_entry` reason arguments across
  `research_vault/` and `hooks/` — "would have caught C-2 outright."
- **B2.** The check-id sweep guards membership, not completeness. A phrase-less run drops out of
  view once fewer than two of its members stay valid; for a two-member run that is a single
  rename. `skills/publish/SKILL.md:37` is that shape today. Both obvious alternative anchors are
  refuted by that same line.

### C. Polish-ledger material (4)

None are defects; all are shape and hygiene items in the register the polish pass already holds.

- **C1.** `skills/import-source/references/batch-mode.md:9` — the orphaned "as above"
  cross-reference, left deliberately under Task 6's byte-preservation mandate. Confirmed still
  present at tip.
- **C2.** `skills/publish/SKILL.md` is the corpus's longest skill at 140 lines (confirmed by
  `wc -l`), seven table rows against `evidence-conventions`' five.
- **C3.** Three-way spelling of the 64-char digest literal — a drift hazard the Task 17
  coordinator marked deferred.
- **C4.** `mutation-baseline.txt:130` stale survivor key — marked inert and deferred.

C3 and C4 are Part 2 items; the polish ledger's 38 entries were built from Part 1 only
(`grep -c` for "digest literal" and "survivor key" over the audit doc both return 0).

### D. Loose ends owned by a later phase (2)

Both from Task 4, both genuine, neither with a home outside the report.

- **D1.** The category-separator annotation ships a recorded three-way conflict without saying
  which form filters; the triage defers that to a live two-curl probe at slice time. A live loose
  end for the slice, not a defect.
- **D2.** Line references into the frozen vendored files are correct today and rot silently at
  re-vendor. Nothing in `tests/` enforces re-verification, and the report explains why it did not
  add one (it would need a vendored copy of upstream to diff against). This belongs on a
  re-vendor checklist; there is no such checklist.

## Disposed — verified, no action

| Source                  | Concern                                                                     | Disposition, verified at tip                                                                                                                                                                                                                                                                               |
| ----------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tasks 2, 5, 9, 10, 15   | "None"                                                                      | —                                                                                                                                                                                                                                                                                                          |
| Task 1                  | Live legs not run                                                           | Plan defers live verification to Task 21 Step 3. Disposed by plan text.                                                                                                                                                                                                                                    |
| Task 1                  | Two unplanned table realignments                                            | Verified scope-limited, suite green.                                                                                                                                                                                                                                                                       |
| Task 14                 | `DTZ007` `noqa` judgment call                                               | Recorded in a code comment at the site. Disposed in code.                                                                                                                                                                                                                                                  |
| Task 16                 | #17 referenced, not closed                                                  | Issue #17 open, plus a spec §10:168 entry. Disposed twice over.                                                                                                                                                                                                                                            |
| Task 17                 | Fixture migration width                                                     | Verified empirically before commit.                                                                                                                                                                                                                                                                        |
| Task 2b                 | `open_q` render question                                                    | Routed to Task 13 Step 1, which states it rides after the commit as author-side verification. Disposed by plan text.                                                                                                                                                                                       |
| Task 2c #1              | Surface list omits root `log.md`                                            | **Fixed.** Template preamble now reads "`literatures/`, `log/`, `log.md`, and `inbox/review-queue.md`".                                                                                                                                                                                                    |
| Task 2c #2              | "warned in session and caught at commit" is precise only for `literatures/` | **Fixed, and the model disposition of this whole sweep.** The false clause is gone — the preamble now says "don't edit them by hand" — *and* the reproduction became the trigger evidence in Task 19b's own header, cited there in full. A concern that changed a shipped file and created a planned task. |
| Task 2d                 | `[*]` section over-broad                                                    | **Moot.** No `[*]` section exists at tip.                                                                                                                                                                                                                                                                  |
| Task 2d                 | EditorConfig properties unverified end to end                               | Carried by this reviewer to the Part 2 boundary; recorded in `2026-08-24-boundary-sha-walk.md`.                                                                                                                                                                                                            |
| Task 3 #1, #2 (round 0) | `manual` clause deviation; table scope tension                              | Both closed in later fix rounds, recorded in the round reports.                                                                                                                                                                                                                                            |
| Task 8 #1, #2           | Unpinned skills; adoption 8 phrasing                                        | Both resolved in fix round 1.                                                                                                                                                                                                                                                                              |

## A note on attribution

The controller's relay states that this reviewer routed the three 17b round-0 concerns to the
issue tracker. That is a misattribution, and it matters here because this sweep exists to fix a
record-keeping failure. This session reviewed the plan and its ledger (`0ea7fc7`), the two
addenda `eff8d67`/`ebea360`, and re-ran the boundary SHA-walk (`ca0281d`). It did not review Task
17b. The routing was promised by the **17b task reviewer** — `task-17b-review.md:216-217`, "per
AGENTS.md this repo tracks work in GitHub Issues; it should be filed, not left as a paragraph in a
report file that nothing reads again" — and the implementer's report then recorded it as
"routed... by the reviewer per their message". No report or review in the directory names this
session.

The substance is unaffected: the four concerns are real, nobody filed them, and they die at
worktree removal. But "the reviewer said they'd file it" was itself the untracked promise that
failed, and a sweep built to catch that class should not begin by mis-assigning it.

## Recommendation

1. **File A1–A3** as issues before merge. Drafts are ready; filing is an outward-facing action on
   the author's account and is held pending the author's own word rather than a relay.
2. **A4 to spec §10** as a stated-boundary entry, not an issue.
3. **B1–B2** need their recurrence condition written somewhere that gets read — the polish
   ledger, or an issue labelled for triage. A condition recorded only in a file about to be
   deleted is not a disposition.
4. **C1–C4** append to the polish-pass section, which already holds 38 Part 1 entries.
5. **D1** rides the slice; **D2** needs a re-vendor checklist, which does not exist and should.
6. **Make the sweep structural, not a one-off.** Every one of these was promised inside a file
   that `.git/info/exclude` hides and worktree removal destroys. The cheap fix is a report
   template that requires a destination per concern at write time, rather than a sweep that has
   to reconstruct twelve dispositions from thirty-one sections at merge time.
