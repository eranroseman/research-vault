# Pre-slice batch — boundary review, run after the merge

Independent reviewer, read-only pass, 2026-08-25, over `d9b3acf..4b9f427` on `main`.

**This review ran after the merge, not before it.** The batch was already fast-forwarded onto
`origin/main` when it was commissioned. Nothing here gated the merge, and nobody should describe
the batch as reviewed before merging on the strength of this document. The merge stands on the
evidence its own acceptance produced; this is a boundary review of a landed range. The controller
asked for the gap to be visible rather than closed quietly, which is the right call and is why
this paragraph is first.

The one SHA-walk on record before the merge is `ca0281d`, at the Part 1 / Part 2 boundary.

## Scope of the instrument

Stated up front, because this run's own retrospective (`2026-08-25-pre-slice-batch-method-retrospective.md`)
names unstated instrument scope as the spine of every substantive controller error in the batch,
and the rule does not exempt the reviewer.

- The walk enumerates `git rev-list --first-parent d9b3acf..4b9f427` minus merge commits: **91
  commits**. First-parent is the branch's own line; commits that entered through the three merge
  commits are main's, already reviewed on main, and are deliberately out of scope.
- Coverage means "falls inside some `Task N: complete (commits A..B)` range in the ledger". The
  metric **cannot distinguish a task closed in a different form from a task never closed** — see
  finding 1, which is exactly that case.
- SHA extraction is `\b[0-9a-f]{7,40}\b` over the ledger. That regex over-matches; see finding 4.
- The suite result below is offline with port 23119 listening, so the live legs ran. Not a
  hermetic result. Plan W's suite task is what makes it one.

## Reconciliation with the prior walk

Prior walk (`ca0281d`, at `32acfe2`): **27 commits / 9 uncovered.**
This walk (`4b9f427`): **91 commits / 26 uncovered.**

The nine reconcile exactly as predicted. Five gained completion lines — `c418cf7` (Task 2d),
`eff8d67` and `ebea360` (the two addenda), `2e23c40` (2d's fix round), `89fe2fe` (the
`oldest_age_days` wiring). The other four never could: `aef25c1` (the reverted Part 3 amendment),
`3a6d0cd` (the boundary merge), `d6c5ccd` (Plan W's form pass), `32acfe2` (the checkbox backfill).

Of the 26 uncovered now, **21 are structurally unclaimable** — eighteen `docs: tick Task N`
commits (written after the completion line they follow), plus those four, plus `4b9f427`'s
mdformat re-pad and `b5115ff`'s retrospective. Per-task ticking became practice mid-run, which
raises the unclaimable count without indicating anything wrong.

**Five are real task work outside any completion range**, and they all belong to two tasks.

## Findings

### 1. Tasks 13 and 21 never received a canonical completion line

Twenty-seven tasks carry `Task N: complete (commits A..B, review …)`. Tasks 13 and 21 do not.
Both are closed in substance — `c16195e` and `a5edc02` tick them, and Task 21 carries fourteen
progress lines covering three fix rounds, the acceptance sweep, and the full live run — but
neither closes in the form every other task used.

The consequence is that five work commits sit outside every claimed range: `1c7f682` (spec §6
missing-data close), `111ddbf`, `04896d7`, `f8915c2` (Task 21's three fix rounds), and `271f4af`
(Task 13's live-vault record).

This is a record-shape defect, not unfinished work. It matters because the ledger is the recovery
map: a reader walking it programmatically — which is the only way it has ever been walked — sees
the batch's two closing tasks as uncovered and cannot tell from the map alone whether that means
"closed differently" or "never closed". Task 21 in particular is the acceptance task, so its
closure is the one a future reader is most likely to want to confirm.

Cheapest durable fix: two completion lines in the ledger's own form. If Task 21's closure is
genuinely the merge itself and not a range, then the line should say that.

### 2. `88c6c09`'s commit message is false, and the record still carries it

    88c6c09 docs: untrack the SDD review packages, keep the reports
     .../sdd/2026-08-22-post-q-batch/progress.md | 35 ++++++++++++++++++++++
     1 file changed, 35 insertions(+)

It untracked nothing. The work landed later at `cf3b17c`, same message, 31 files and 7,105
deletions — verified, and `.superpowers/` on `main` now holds 71 files with zero `review-*.diff`,
so the end state is correct.

What is not correct is the record. `grep` for `88c6c09` over the ledger and over every commit body
in the merged range returns nothing: no correction anywhere. So `main` permanently carries two
commits with the same message, one of which did the work and one of which claimed it and did not.

This repo deleted `.git-blame-ignore-revs` on the reasoning that the commit message *is* the
record. Under that doctrine an uncorrected false message is not cosmetic. Raised before the merge;
recorded here because it merged.

It is also the retrospective's own spine wearing a different coat: a claim reported without
checking what the action actually covered. Worth noting where it landed — the commit that failed
to observe its own claim is part of the work that fixed reports which assert without observing.

### 3. Sweep categories B, C and D are still unrouted

Confirmed against `main` at the merge tip. The polish-pass section holds 20 numbered entries;
`grep -ci` over it returns 0 for "digest literal", "survivor key", "append_entry" and "re-vendor
checklist". So:

- **B1** (reason-code placement — the AST scan of `inbox.append_entry` reason arguments that
  "would have caught C-2 outright") and **B2** (the check-id sweep's phrase-less hole, with
  `skills/publish/SKILL.md:37` in that shape today) — recurrence conditions with no home.
- **C3** (three-way spelling of the 64-char digest literal) and **C4** (`mutation-baseline.txt:130`
  stale survivor key) — Part 2 items the ledger's Part 1 entries never covered.
- **D2** (vendored line references rot at re-vendor; nothing enforces re-verification) — needs a
  re-vendor checklist that still does not exist.

Deferring these to the batch close was agreed and remains safe: `5c0325e` is tracked, so the
record survives. The caveat from that agreement now has evidence behind it. With the SDD workspace
tracked, "preserved" and "routed" have come apart, and B is precisely the shape that gets lost in
the gap — a condition nobody queries, sitting in a file that survives. Preservation was never the
failure mode; unread preservation was.

### 4. Four ledger tokens do not resolve, and none is a phantom

Reported precisely because a bare count here would be a false alarm of exactly the class the
retrospective warns about. `1293295` and `ec5e9ef` are commits in the **live vault repository**
(`~/kh-vault`), recorded correctly by Task 13's live-vault application; `5eed40f` is that repo's
prior tip. They cannot resolve here and should not. `e3b0c442` is not a commit at all — it is
`sha256(b"")[:8]`, the empty-annotation anchor collision from issue #16.

Of this repository's SHAs, **127 of 127 resolve. No phantoms.** The four are my regex's
over-match, not the ledger's error, and the honest form of this line is the scope, not the count.

## Independently reproduced

| Claim | Result |
|---|---|
| Fast-forward `d9b3acf..4b9f427` | Confirmed: `d9b3acf` is an ancestor of `4b9f427`; `4b9f427` is an ancestor of `origin/main`. |
| Offline 1738 / 7 | **Reproduced exactly** — 1738 passed, 7 skipped, 76.3 s (port 23119 listening). |
| 112 / 0 boxes | **Exact.** 112 checked, 0 unchecked. |
| Review packages untracked | Confirmed at `cf3b17c`; 71 files under `.superpowers/`, zero diffs. |

The live run (1743 / 2) and the six reconstructed audit defects were not re-run here: the live
legs need a human-present environment, and re-reconstructing the defects would duplicate Task 21's
acceptance rather than check it.

## On the retrospective

Read as commissioned, at `3707586` — the amended six-row version, which arrived while this review
was being written. It is the strongest artifact the batch produced, and it earns that by
cataloguing its own author's errors with the instrument that caused each one named beside the
answer it distorted. Adding the last two rows as a dated amendment rather than absorbing them
silently is the right call, and the stated reason — "a note that quietly grows to match its
subject is doing the thing it warns against" — is the note holding itself to its own rule.

Three observations.

**The spine generalises further than it claims.** "The instrument defined the scope of the answer,
and the answer was reported without that scope" covers all six tabulated instances. It also covers
`88c6c09` in finding 2 above, and it covers my own regex in finding 4. A rule that keeps finding
instances after the document closes is the right rule.

**"A confident negative is the most expensive kind of wrong answer, because it retires the
instruction that would have found the rest"** is the most portable sentence in the document. It
survives outside this project entirely. `x or default` **is** a truncating pipe for empty
containers is the second most portable, and it is the only row that names a defect the reader can
grep for.

**One gap, narrowed but not closed by the amendment.** The note says scope-stating is the writer's
duty and that the catch rate came from readers who re-measured, then writes a rule only for the
writer's half. The amendment adds a genuine self-check rule for the sixth instance — a surprising
measurement is a reason to check the instrument — but that is still a writer-side rule; it fires
only when the answer happens to look implausible, which by the note's own account five of six did
not. The reader's half remains unwritten, and the six rows now make its content unusually legible:
five were caught by a second reader using a **different** instrument — `git check-ignore`, a read
of `_cli.py`, a look at `metadata_year`, a probe of the empty representations — and none by the
same instrument applied twice. That is the sentence worth adding:

> A re-measurement with the same instrument reproduces the same scope, and therefore the same
> blind spot. What catches an unstated scope is a reader who measures differently.

It is also the practical form of the standing arrangement this session is part of, so writing it
down costs a line and makes the arrangement's rationale legible to whoever inherits it.

## Standing role

Next boundary is Plan W's close. This document is a new file; `research/` stands as written.
