# Task 16 review - ded3cdf..0b8ec6c

## Spec Compliance

**Verdict: issues.**

Steps 1 through 5 of the brief all landed, verbatim where the brief was literal: the two RED tests
carry the brief's exact names, fixtures and assertions; the floor is the brief's Step 3 predicate
adapted to a single hoisted `applicable` variable and a flag set inside the existing `parse_claims`
loop; the spec sentence is the brief's Step 4 text, word for word, inside §5's Event-integrity
paragraph in the same commit; the commit subject is the brief's Step 5 subject.

The unmet requirement is the brief's title clause. Task 16 is titled — in the brief
(`task-16-brief.md:1`) and identically in the plan
(`docs/superpowers/plans/2026-08-22-post-q-batch.md:331`) — as *"also closes issue #17 — human-reviewed
tier unreachable — read the issue and cover it in this task's tests; reference #17 in the commit."*
Three obligations; the commit delivers only the third. The issue is not closed, and no new test covers
it.

Issues:

- `docs/superpowers/plans/2026-08-22-post-q-batch.md:331` — the plan records task 16 as closing issue
  #17, but #17 is still OPEN and its precondition is untouched: no shipped surface mints a
  `human:`-attributed verified event (`research_vault/verify.py:797` and
  `research_vault/publish.py:368` are the only production `record_pass` call sites and neither
  passes `by=`). I confirmed by grep that no other task in the plan owns that surface — #17 appears
  exactly once in the plan, at line 331.
- `tests/test_events.py:164` — the brief's "cover it in this task's tests" clause produced no
  coverage. The floor changed the human-reviewed derivation as well as the machine one, and nothing
  pins the change.

### Cannot verify from diff

Resolved during synthesis (recorded so the controller does not re-run them):

- **RED evidence.** Reproduced against a scratch export of `ded3cdf`: the url-only fixture and
  `trust_tier("just some text\n")` both return `machine-confirmed` at BASE and `unverified` at HEAD.
  The report's RED block is accurate.
- **Full suite.** Reproduced against a clean scratch export of `0b8ec6c`: `1561 passed, 7 skipped in
  75.23s`, matching the report's counts exactly. The output carried no warnings summary, so the
  pristine-output constraint holds.
- **Commit body.** `git log -1 --format=%B 0b8ec6c` carries the consequence sweep (naming the three
  test files and stating that no test pinned the vacuous tier, which is Step 5's per-test obligation
  discharged honestly on an empty set), and references #17 in non-closing prose — no closing keyword,
  so merging will not auto-close the issue.
- **Issue #17.** `gh issue view 17` reports state OPEN, title "The human-reviewed trust tier cannot be
  minted by any shipped surface". Its own body calls the two defects "distinct" and merely "best fixed
  in the same pass", which supports the implementer's scope call.
- **Form checks, partially.** Run read-only against a scratch export: `ruff format --check` (74 files
  already formatted), `ruff check` (all checks passed), `mypy research_vault` (no issues, 27 files),
  and `mdformat --check --number --wrap keep` on the amended spec file. Four of the eight hooks, chosen
  as the ones this diff can affect.

Residual, for the controller:

- **Full form gate.** Run `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` once in a
  sanctioned checkout to confirm the report's "form gate 8/8". The four hooks I did not run (yamlfix,
  pyproject-fmt, config-validity, and the remaining suite hook) act on yaml, toml, json and skill
  frontmatter, none of which this diff touches; this is bookkeeping, not a risk.
- **Plan-owner ratification of the #17 bookkeeping.** Keep GitHub issue #17 open, and decide between
  retitling task 16 so it no longer claims closure and scheduling the CLI-minting surface as its own
  task. No plan task owns that surface today, so the decision cannot be deferred to a later task by
  default.

## Strengths

- The floor is OR-shaped exactly as the brief required. `if not applicable and not has_managed_quotes`
  (`research_vault/events.py:280`) is NOT(applicable OR managed quotes), so a citekey-only note with
  a matched managed-quote check still reaches `machine-confirmed` — I reproduced that on the real tree
  — and every note with a doi or pmid whose checks pass is untouched.
- The reuse requirement is over-satisfied. `has_managed_quotes = True` is set inside the pre-existing
  `parse_claims` loop (`events.py:268`), so no second parse was added, and `_applicable_note_checks(data)`
  is hoisted into one `applicable` binding used by the subset test, the failure-row loop and the floor —
  one call where BASE made two. The hoist is behaviour-preserving: the helper is a pure function of
  `data` and `applicable` is only read.
- The flag's placement is the correct one. It is set immediately after the continue-guard and before the
  `checks.isdisjoint(quote_checks)` test, so a note with quote claims counts as checkable whether or not
  its quote checks have matched yet — the floor cannot mask the quote loop's own invalidation.
- The rename of `applicable_failures` to `applicable` retires a misleading name: the set never held
  failures, it was the applicable-check set the failure loop consults.
- The spec sentence sits between the requirement clause and the writer clause, so §5 now reads
  requirement, then floor, then writer, rather than appending the new rule as an orphan. The scope fence
  held: one line changed, and the "Invariants" never-delete paragraph reserved for a sibling task is
  untouched.
- The consequence sweep in the report is real and independently confirmable: every `machine-confirmed`
  and `human-reviewed` assertion in the repo rides a doi or pmid fixture, so Step 5's "fix any test that
  pinned the vacuous tier" genuinely had no work.
- The out-of-scope half of #17 was disclosed with its evidence in both the report and the commit body,
  and the commit deliberately avoids a closing keyword. That is the honest way to reference an issue a
  change does not close, and this diff makes #17's neighbourhood strictly better: derivation now demands
  real evidence beneath a human event.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

**1. `research_vault/events.py:280` — the floor's `has_managed_quotes` clause is unpinned; a mutant
that deletes it survives the entire suite. Status: CONFIRMED.**

The floor is a two-clause predicate but only the first clause is tested. No test anywhere exercises a
note with an empty applicable-check set that still reaches `machine-confirmed` through a matched
managed-quote check.

Why it matters: rewriting the guard as `if not applicable:` silently regresses every identifier-less
note carrying verified managed quote claims to permanently `unverified`, and nothing catches it. I
reproduced both halves — on the real tree, a citekey-only note with a matched
`quote:noid2020#^c-11111111:managed-region` event yields `machine-confirmed`; with the clause deleted
in a scratch copy it yields `unverified`, and that mutated copy still passes `tests/test_events.py`,
`tests/test_trust_tier_cli.py`, `tests/test_notes.py` and `tests/test_quotes.py` (124 passed). The
quality lens reported the same mutant surviving the full 1561-test suite. The state is production-
reachable: `verify.py`'s `_projection_identity` mints `quote:<link>:<target>` events for any note with
quote outcomes, with no doi or pmid involved.

One correction to the lens's rationale, which does not weaken the finding. The claim that the repo's
mutation gate "would immediately trip" on this clause is wrong: `research_vault/events.py` is one of
the six modules listed in `mutation-exclusions.txt` and is explicitly not represented in
`mutation-baseline.txt`. Mutation testing will never see this clause. That makes the missing test more
valuable, not less — the gate is not a fallback here.

How to fix: promote the report's own self-review #3 heredoc into `tests/test_events.py` — a citekey-only
note (no doi, no pmid) with a managed quote claim `^c-11111111`, asserting `unverified` before
`record_pass("quote:<citekey>#^c-11111111:managed-region", Result.MATCHED)` and `machine-confirmed`
after. The implementer ran exactly this by hand and left it out of the suite.

**2. `tests/test_events.py:164` — the floor also narrows `human-reviewed`, and nothing pins that
behaviour change. Status: CONTESTED (stood verification; independently reproduced during synthesis).**

The floor at `events.py:280` runs before the `human:` check at `events.py:287`, so a note with a valid
`human:` verified event, an empty applicable set and no managed quote claims derived `human-reviewed` at
BASE and derives `unverified` at HEAD. I reproduced the flip directly: the brief's url-only fixture plus
`record_pass(text, "doi", Result.MATCHED, by="human:eran")` returns `human-reviewed` on a scratch export
of `ded3cdf` and `unverified` on `0b8ec6c`.

Why it matters: this is a real behaviour change shipped by this commit with no test. The three tests the
report cites as covering the human path all miss the case — `test_human_event_alone_is_not_human_reviewed`
(`tests/test_events.py:175`) uses BASE, whose `doi` makes the applicable set non-empty and whose unchecked
quote claim drives a different `unverified` path; `tests/test_trust_tier_cli.py` uses PMID_ONLY with its
applicable check passed; the two new tests carry no events at all. The new spec sentence mandates the
narrowing with no carve-out for human events, so the missing test would pin spec-required behaviour. It is
also the only discharge of the brief's "cover #17 in this task's tests" clause that stays inside this
commit's single-function delta.

How to fix: add one derivation-side test beside the two new ones — take the brief's url-only fixture, apply
`events.record_pass(text, "doi", Result.MATCHED, by="human:eran", at="2026-08-16")`, assert
`events.trust_tier(text) == "unverified"`. `record_pass` does not validate check names against the note's
identifiers (see `tests/test_events.py:213`, which records `quote:...:unsupported-target`), so this needs no
new CLI surface. The production-minting half of #17 stays out of scope.

**3. `docs/superpowers/plans/2026-08-22-post-q-batch.md:331` — the plan records task 16 as closing issue
#17, which it does not. Status: CONTESTED, plan-mandated.**

Why it matters: #17 is OPEN, and its precondition remains unproducible — `human:` reaches production only
through `inbox.py`'s acknowledgment path, and neither `record_pass` call site
(`research_vault/verify.py:797`, `research_vault/publish.py:368`) passes `by=`. Leaving the plan line
as written records a closure that did not happen, and my grep shows #17 is named exactly once in the whole
plan, so no later task inherits the work by default. The three items the report cites as "coverage" for #17
all pre-date this commit, so no new evidence about #17 was produced either.

How to fix: this is bookkeeping, not code, and it needs a human. The implementer's refusal to close #17 was
correct and openly disclosed — minting a human-attributed verified event needs a new CLI verb, outside this
commit's single-function delta, the brief's Steps 1 to 5, and the parent task's surfaces list, which names
`events.py` alone. Keep GitHub issue #17 open, retitle task 16 so it no longer claims closure, and schedule
the CLI-surface work as its own task.

### Minor (Nice to Have)

None.

## Refuted During Verification

None. All three findings raised by the lenses survived adversarial verification, and all three are carried
forward above. Nothing was dropped.

## Assessment

**Task quality: Needs fixes.**

The fix itself is correct, minimal, and better than the brief asked for — the floor is OR-shaped in both
directions, the hoist nets a call reduction rather than an addition, and the spec sentence landed verbatim
in the same commit. What blocks approval is coverage and bookkeeping, not behaviour: two branches this
commit created or changed ship with no test that pins them (one of them in a module mutation testing cannot
measure), and the plan still claims a closure of issue #17 that the commit correctly declined to make.
