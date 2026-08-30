# Addenda review — `eff8d67` and `ebea360`

Independent reviewer, 2026-08-24, commissioned by the author. Range `c418cf7..ebea360`: the
two follow-up commits to completed Tasks 9 and 4 that landed after the ledger's last write
(12:27) and so carry no dispatch, no completion line, and no review diff.

**Verdict: CLEARED for Part 2, with one Important that must land before the merge.**
1 Important, 4 Minor, 0 Critical. The Important is not an execution defect — `ebea360` copied
its source verbatim and the source was wrong; the author corrected it on main at `750d4c7`
while this review was being written, and the branch has not picked the correction up. Nothing
here blocks Part 2 starting; the Important blocks Task 21.

## Verification actually performed

Offline suite re-run in the worktree venv at tip `ebea360`: **1576 passed, 7 skipped in
76.6 s**. Consistent with the ledger's growth curve (1548 at Task 1, 1565 at Task 6).

**Condition disclosed, as the ledger's own convention requires:** port 23119 was LISTENING
during this run, so the live legs executed. This is the non-hermeticity Plan W's suite task
fixes. The green is real but is not a hermetic result — the same caveat attaches to every
"suite green" line recorded in this run, and it is stated here rather than assumed away.

Both commit bodies' testable claims were checked against the tree, not accepted:

| Claim | Verified |
|---|---|
| `ebea360`: "no test pin needed updating" | TRUE. `skills/find-sources/SKILL.md` carries no whole-file byte pin. Its tests are token assertions (`tests/test_searchlog_cli.py:522,541,547`) and an AST sweep (`tests/test_find_sources_vendor.py`), none of which a new prose bullet disturbs. Green suite confirms. |
| `eff8d67`: four unrelated dict-equality tests updated | TRUE. `tests/test_inbox.py:479, 575, 595, 883` all carry `oldest_age_days` via `_age_days()`. Green suite confirms. |
| `eff8d67`: the no-threshold ruling held | TRUE — see below. |
| `eff8d67`: `_inbox_probe` deliberately not rewired | TRUE. `scaffold.py:305-320` reads `unacknowledged` and `oldest` only. |

## The author's direct question: did the no-threshold ruling hold?

**Yes.** The implementation ships the number and nothing else. `research_vault/inbox.py:718-738`
introduces no module constant, no boolean, no comparison against any cutoff — one subtraction
guarded by a `None` check. `grep -rn "aging" research_vault/` returns nothing.

The withdrawal reasoning also survives scrutiny, which is the part worth recording. The commit
body claims no Whittaker *threshold* exists in the tree. `skills/project-flow/SKILL.md:25` does
name "the Whittaker inbox-rot guard" — but states it in deliberately continuous terms ("an aging
queue earns more prominence the longer it goes untouched", "nothing here blocks on age") with no
number anywhere. The claim is about a threshold, not about the name, and it is precise. An
implementer told to emit `aging: true` would have had to invent the cutoff — the plan's Task 9
addendum text asserting a "Whittaker threshold" is the thing that was wrong, and the
implementation correcting the plan rather than obeying it is the right call.

Test quality on the age math is above the run's average. `test_skipped_entries_not_counted_unacknowledged`
files the UNMATCHED fixture at today-minus-3 computed at run time and asserts the literal `3`,
so it neither rots on a calendar nor duplicates production's own formula; the SKIPPED fixture
stays at the fixed `2026-08-01` precisely so a regressed filter would push the basis to
"23-and-growing" and never sit at 3. The `_age_days()` helper is tautological by construction
and its docstring says so, confining it to assertions that are not about the age math. That is
the honest form.

## Findings

### Minor 1 — the fact is emitted and nothing reads it

`oldest_age_days` appears nowhere outside `inbox.py` and `tests/`. Three skill surfaces read
the verb, and none names it:

- `skills/project-flow/SKILL.md:25` — "Report the unacknowledged count and the oldest entry's
  **date**". This is the surface the commit's own rationale cites as the reason for the change.
- `skills/publish/SKILL.md:25` — same wording.
- `skills/import-source/references/batch-mode.md:12` — invokes the verb, reports per-note breakdown.

`skills/setup-vault/SKILL.md:34` already asks for "the inbox count and oldest age" — a consumer
that wants the field and cannot know it exists.

The mechanism landed; the prose that motivated it did not move. One clause in project-flow:25
closes it, or a recorded ruling that the agent should keep deriving age itself.

### Minor 2 — negative ages are reachable through a supported flag

`_validate_date` (`inbox.py:167`) enforces `YYYY-MM-DD` and calendar validity, nothing more, so a
future date is legal. `__main__.py:870` gives the `finding` verb a `--date` argument. Reproduced
end to end against a scratch vault at `ebea360`, not reasoned from the validator:

    $ python3 -m research_vault finding --vault "$V" doi a UNMATCHED mismatch --date 2099-01-01
    doi/kind-10:identifier;target-1:a/2099-01-01
    $ python3 -m research_vault inbox --vault "$V"
    {"oldest": "2099-01-01", "oldest_age_days": -26428, "unacknowledged": 1}

Display-only, nothing blocks on age, so the blast radius is a nonsensical number in a report.
But the docstring commits to the boundary in one direction ("a freshly filed entry reports `0`,
not `None`") and is silent in the other. Either clamp at 0, or state the negative case in the
docstring so the surface reading it knows what it can receive.

### Minor 3 — the docstring's `0` claim has no test

`inbox.py:722` states "a freshly filed entry reports `0`, not `None`". `grep "oldest_age_days\": 0"`
over `tests/` returns nothing. The claim is true — a same-day entry yields `0` — but it is the
one boundary the docstring calls out by name and the one the tests skip. On a branch whose whole
method is claims-must-be-observed, an untested asserted boundary is the house's own finding class.
One line in the existing test.

### Minor 4 — the CLI JSON contract is entirely unpinned (pre-existing, widened here)

`__main__.py:761` serialises `inbox.summary()` straight to stdout as `json.dumps(..., sort_keys=True)`.
No test in the suite invokes the `inbox` verb: the unit tests pin the *dict*, not the *stdout*.
So the CLI's output contract has never been pinned, and this commit changed it without one.

Flagged as pre-existing and widened, not introduced — the gap predates the addendum. But this
addendum is the first change to that surface since the gap was visible, and one subprocess test
asserting the emitted key set would convert an unowned contract into a pinned one. Worth doing
before Part 2 lands more surfaces on it.

## Refuted, recorded rather than dropped

Two hypotheses were pursued and closed against the source; recorded so neither is re-derived.

1. **"A malformed date crashes `summary()`."** REFUTED. `date.fromisoformat` on the new path can
   only see a value that already passed `_validate_date` at parse time (`inbox.py:541`), and a bad
   line raises `InboxError` before `summary()` is reached. `InboxError(ValueError)` (`inbox.py:112`)
   is inside `_inbox_probe`'s catch (`scaffold.py:307`), so the doctor probe reports UNREACHABLE
   rather than crashing. The hand-edit vector the plan's Task 19b describes cannot reach the new
   arithmetic.
2. **"`min()` over ISO strings breaks on mixed-precision dates."** REFUTED. Partial dates exist
   elsewhere in this system (Task 19 defends their precision), but `_validate_date` rejects
   anything that is not a full `YYYY-MM-DD` on both the write and the load path, so the strings
   `min()` compares are fixed-width and lexicographic order is calendar order.

### Important 1 — `ebea360` ships a technical claim that is now known to be false

`skills/find-sources/SKILL.md:23` reads:

> Not XXE (no entity expansion); residual expansion-DoS rides the runtime's libexpat

The plan's Task 4 Step 3 was corrected on main at `750d4c7` (2026-08-24, "planner defect 6/15"):

> not XXE (no EXTERNAL entity expansion — internal entities DO expand, probe-verified
> 2026-08-24, which is exactly the class the next clause hedges)

The two are not the same claim. "No entity expansion" is false of stdlib ElementTree — internal
entities do expand, which is precisely the mechanism the following clause's expansion-DoS
warning describes. As shipped, the bullet's first half denies the risk its second half names.

`ebea360` is not at fault: it copied the plan verbatim, which is what Task 4 Step 3 instructs,
and the correction landed 23 minutes after the commit (`ebea360` 12:32:13, `750d4c7` 12:55:36). But the branch now carries a false
security claim in prose that ships to users, and the plan it was copied from no longer says it.
**Update `skills/find-sources/SKILL.md:23` to the corrected wording before Task 21's merge.**

This is also a live instance of the run's own through-line — the plan asserting a technical fact
that had not been probed — caught here by the author's probe rather than by the review that
should have covered this commit. Had `ebea360` been reviewed on landing, the range would have
been read against the plan and the claim tested; it was not, because the commit fell outside
the ledger's coverage. That is the concrete cost of the two uncovered commits, not a
hypothetical one.

## `ebea360` otherwise

One prose bullet added to the vendoring-notes list in `skills/find-sources/SKILL.md`. Correct
by every other constraint the plan sets: verbatim against the plan's Task 4 Step 3 text as it
stood at commit time, nothing under
`skills/find-sources/scripts/` or `references/` touched, the vendor rule respected (annotate, do
not fix, do not swap in defusedxml), and the technical claim is the narrow true one — "not XXE
(no entity expansion)" is a real distinction, and naming expansion-DoS via the runtime's libexpat
as the residual is what survives scrutiny where a blanket "we parse untrusted XML" warning would
not — the shape of the annotation is right, and only the parenthetical is wrong. No further findings.

## Recommendation

Clear both for Part 2. Then, in order:

1. **Important 1 before Task 21** — carry `750d4c7`'s corrected XML wording into
   `skills/find-sources/SKILL.md:23`. It rides the boundary merge for free if the merge happens
   first; if it does not, it is a one-line commit of its own.
2. **Minors 1–3** fold into the Task 2d follow-up already queued — all three are one-line changes
   and that commit is churning adjacent surfaces anyway.
3. **Minor 4** routes to Part 2's start, where the CLI surfaces are being worked.
4. Write the two missing completion lines into progress.md so the ledger's coverage map returns
   to N/0.
