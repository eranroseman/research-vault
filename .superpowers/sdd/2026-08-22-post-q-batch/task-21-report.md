# Task 21 report

**Status:** Steps 1, 2, and 4 complete, plus the Step 5 commit for this scope. Step 3
(acceptance sweep, live suites, merge-and-push) is explicitly out of scope for this
agent and was not run.

## Commits

One commit, subject `fix: close spec §6 missing-data gaps; trust-core remediation
acceptance` (commit hash reported in the agent's final response to the controller,
since a commit cannot record its own hash inside itself). Files:
`knowledge_harness/checks.py`, `tests/test_checks.py`,
`docs/superpowers/specs/2026-08-16-foundation-spec.md`,
`docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md`, and this report.

### Step 1 — metadata row (superseded by author ruling 2026-08-25)

The brief's original premise ("if `check_metadata` silently folds an absent field
into MATCHED, fix it") does not fire: absent/malformed local or remote fields already
return UNREACHABLE, never MATCHED. The controller's ruling replaces the instruction:
a missing **local** field (in practice, only `title` — `_metadata_authors(None)` and
`metadata_year(None)` both already treat an absent field as valid-empty, so title is
the only local field whose absence reaches the error branch) becomes whole-check
SKIPPED, reason naming the field; remote-side failures are unchanged (still
UNREACHABLE, genuine outages). Added an early return in `check_metadata`
(`knowledge_harness/checks.py`) right after the DOI-presence SKIPPED check, before
the network `registry_agency` lookup — SKIPPED is a property of the item, determined
offline, so it returns before any attempt. This also changes precedence in the
combined case (missing title + routing/network failure): previously UNREACHABLE,
now SKIPPED — the correct direction per the ruling (a fact that will never resolve
by retrying must not masquerade as a retriable outage). Reason string:
`"no-identifier — item has no title"`.

The appended spec sentence names `title` specifically ("An absent local `title` —
the one field the comparison cannot run without — is whole-check SKIPPED..."),
not "a compared field" generically — see the Concerns entry below on why the
broader claim would have been false.

**Reason-code discovery not in the controller brief:** every `Outcome.reason` is
validated at construction (`outcome.py:92` calls `inbox.validate_reason`) against a
closed, governed vocabulary (`inbox.REASON_CODES`, cross-checked by
`tests/test_config_validity.py` and `tests/test_skill_contracts.py` against
`docs/terminology.md` §4.4 and `skills/evidence-conventions/SKILL.md`). Minting a new
code (e.g. `no-title`) would have required governance edits well outside this task's
file scope. `skills/evidence-conventions/SKILL.md`'s existing `no-identifier` row
already reads generically — "The check's required field is absent (no DOI/PMID, no
citekey, no quote claims)" — and the codebase already reuses it for non-identifier
absences (e.g. quote check's `"no-identifier — note has no quote claims"`). Both new
reasons use the governed `no-identifier` code with free text naming the actual
absent field, matching that established pattern exactly — no registry change needed.

### Step 2 — update-notice row (settled by doctrine definition)

Confirmed the premise: `_datacite_version_outcome` and its arXiv twin
`_arxiv_version_outcome` both returned UNREACHABLE for a **missing local `version`**
field, before any network call — "nothing was attempted; the item simply lacks the
field," which is SKIPPED by the four-state doctrine, not UNREACHABLE (reserved for
attempted-and-failed). Fixed symmetrically: a new shared `_provider_skipped(target)`
helper returns SKIPPED `"no-identifier — item has no local version"`; both
`_datacite_version_outcome` and `_arxiv_version_outcome` call it when
`_nonempty_version(entry.get("version"))` is `None`. For arXiv, this required
splitting the original compound condition
(`local_version is None or re.fullmatch(...) is None`) into two: absence → SKIPPED,
present-but-malformed-format (e.g. `"2"` instead of `"v2"`) → unchanged UNREACHABLE
(`"outage — arXiv version status unavailable"`), since a malformed-but-present value
is not "the item lacks the field."

### Step 4 — Plan S sequencing gates marked satisfied

Both gates in `docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md` (lines 8
and 10) now carry a one-line, dated (2026-08-25) mark pointing at
`docs/superpowers/plans/2026-08-22-post-q-batch.md` (the pre-slice batch plan,
confirmed as this task's own containing plan). Worded as **complete and merging**,
not merged — the merge is the controller's action and had not happened at commit
time. The second gate's mark is written consistent with its own existing text (both
gates satisfied by the same merge), not restated differently.

## Test summary

Full offline suite: 1714 → 1717 passed, 7 skipped (net +3: four new tests added,
one obsolete parametrize row removed). `ruff check`, `ruff format --check`, and
`mypy knowledge_harness/` all clean; `echo '{}' | python hooks/stop_publish_gate.py`
exits 0.

New/changed tests in `tests/test_checks.py`:
- `test_metadata_skips_entries_whose_local_bibliography_has_no_title` — SKIPPED,
  exact reason, exact `extra`; asserts no network call is made (via an
  always-raising fake).
- `test_update_notice_datacite_skips_when_local_version_is_absent` — SKIPPED, exact
  reason; asserts `api.datacite.org` is never called.
- `test_update_notice_arxiv_skips_when_local_version_is_absent` — the arXiv twin;
  SKIPPED, exact reason; asserts no arXiv feed request is made.
- `test_update_notice_arxiv_malformed_local_version_stays_unreachable` — construction
  check: a present-but-badly-formatted local version (`"2"`, not `"v2"`) still
  returns UNREACHABLE with the original reason — proves the split didn't
  overreach.
- `test_update_notice_datacite_fails_closed_on_version_status` — the `"missing-local"`
  row (previously asserting UNREACHABLE) was removed from this parametrize; the two
  new dedicated tests replace it since its behavior and docstring intent ("fails
  closed") no longer describe that case.

Per-fix discriminator matrix (each hunk reverted individually, target test rerun,
confirmed RED for the stated reason, then restored and full suite reconfirmed
green):
| Fix | Reverted to | Test | Result when reverted |
|---|---|---|---|
| Metadata title-SKIPPED | (removed the early-return block) | `test_metadata_skips_entries_whose_local_bibliography_has_no_title` | AssertionError from the always-raising network fake — proves the check now reaches a network call it shouldn't |
| DataCite version-SKIPPED | `return _provider_unreachable(target, "DataCite")` | `test_update_notice_datacite_skips_when_local_version_is_absent` | `Result.UNREACHABLE` != `Result.SKIPPED` |
| arXiv version-SKIPPED | combined condition, single `_provider_unreachable(target, "arXiv")` | `test_update_notice_arxiv_skips_when_local_version_is_absent` | `Result.UNREACHABLE` != `Result.SKIPPED`; the sibling malformed-format test still passed unchanged, confirming the split discriminates correctly |

By construction, confirmed unchanged (existing tests, still green): a genuinely
unreachable remote (`test_update_notice_datacite_fails_closed_on_version_status`'s
remaining `missing-remote`/`ambiguous-remote` rows, the arXiv malformed/ambiguous
parametrize, `test_metadata_treats_malformed_crossref_shapes_as_unreachable`, etc. —
all still UNREACHABLE) and a present-and-matching field (all MATCHED tests
unaffected).

## Concerns

- **Controller's spec line numbers were off by two (destination: controller).**
  Fact #3 stated the gate table begins at `2026-08-16-foundation-spec.md:95`,
  metadata row `:98`, update-notice row `:99`, "verified against the tree, no
  drift." Re-reading the file directly: the table header is at `:96`, the Metadata
  match row at `:100`, the Update-notice row at `:101` (the Citekey and DOI rows
  occupy `:98`/`:99`). Row identity by content (the "Metadata match (Crossref...)"
  and "Update-notice check (Crossref `updated-by`...)" cell text) was unambiguous,
  so I edited the correct rows regardless — this is a line-number discrepancy only,
  not a wrong-row risk.
- **Per-field outcome-detail granularity — declined for now (destination: a
  per-field outcome-detail design, if one is ever triggered; no current trigger).**
  The draft instruction wanted "SKIPPED for that field, recorded in the outcome's
  detail" (per-field). `check_metadata` returns one whole-check `Outcome`; inventing
  per-field detail structure inside an instrument freeze is out of scope. The spec
  sentence and the implementation both describe whole-check SKIPPED instead.
- **`.superpowers/sdd/2026-08-22-post-q-batch/task-21-brief.md` was already modified
  in the worktree before I started, and is not my change (destination: controller).**
  Left out of this commit's pathspec entirely, per the global constraints.
- **Title-vs-outage precedence decision (destination: controller, recorded here and
  in the commit body).** Placing the title-absence check before the network
  `registry_agency` call means a combined case — local title absent AND registry
  routing/network unreachable — now returns SKIPPED instead of the pre-fix
  UNREACHABLE. No existing test pinned that combination; this is the
  doctrine-consistent direction (an item lacking a field it will never regain by
  retrying should not be gated as a retriable outage), and it removes rather than
  adds a false gate-hold, consistent with the ruling's own stated purpose.
- **Absent local author/year are pre-existing, unruled gaps this task does not fix
  (destination: controller).** Only `title` reaches SKIPPED. `_metadata_authors(None)`
  returns `[]` for an absent local `author`, so an absent local author against a
  populated registry record falls through to the family-name comparison and returns
  **UNMATCHED** "mismatch — author family names differ" — not SKIPPED, not an outage.
  `metadata_year(None)` returns `(True, None)` for an absent local `issued` date, so
  the year leg is silently not compared and the check can still return **MATCHED**
  if title and author agree — the literal "absent field folded into MATCHED" the
  ruling's language forbids, just for a different field than the one this task
  closes (`test_metadata_compares_year_only_when_both_records_have_one` already pins
  this as the current, unchanged, green behavior). Both predate this task and were
  not part of either ruling; the spec sentence was scoped to `title` precisely to
  avoid asserting something false of these two. Widening the fix to cover them is
  unruled scope, not attempted here.
  **SUPERSEDED by Fix Round 1 below — ruled, fixed, and closed.**

## Fix Round 1 (2026-08-25)

**What changed and why.** This concern (the one directly above) turned out to be
the most consequential finding in the round-1 report, not a footnote: it corrected
the coordinator's own earlier claim (relayed upstream) that Step 1's "silently
folds into MATCHED" premise had been fully falsified. It hadn't — `author` and
`issued` were never checked, only `title`. **New ruling (2026-08-25): absent-local
becomes whole-check SKIPPED for all three compared fields, symmetric, and — because
the same shared helpers (`_metadata_authors`, `metadata_year`) produce the identical
absent-vs-malformed conflation on the remote side — the fix also covers absent
remote `author`/`year`.** The one deliberately asymmetric cell: a **remote** record
missing `title` entirely stays UNREACHABLE ("outage — malformed registry metadata",
unchanged) — a registry response with no title at all is a malformed response, not
a legitimate data state, unlike a work genuinely having no author or no publication
year on record.

**Six-cell before/after** (local absent × remote absent, for each compared field):

| Field | Local absent — before | Local absent — after | Remote absent — before | Remote absent — after |
|---|---|---|---|---|
| title | SKIPPED (round 1) | SKIPPED (unchanged) | UNREACHABLE "outage — malformed registry metadata" | unchanged (deliberate — see above) |
| author | UNMATCHED "mismatch — author family names differ" | SKIPPED "no-identifier — item has no author" | UNMATCHED "mismatch — author family names differ" | SKIPPED "no-identifier — registry record has no author" |
| year | MATCHED "matched" (year leg silently skipped) | SKIPPED "no-identifier — item has no year" | MATCHED "matched" (year leg silently skipped) | SKIPPED "no-identifier — registry record has no year" |

Root cause, one line: `_metadata_authors(None)` returns `[]` and `metadata_year(None)`
returns `(True, None)` — both helpers already treat an absent value as
valid-but-empty for shape-validation purposes, so absence for `author`/`year` never
reached either side's "malformed" branch; it fell through into the ordinary
comparison, reading as a real (and sometimes false) verdict on data that was never
there to compare.

**Implementation.** All three local-absence checks (`title`, `author`, `issued`)
now return SKIPPED before the network `registry_agency` call — extending round 1's
title-only precedent (SKIPPED is a property of the item, determined offline) to all
three fields uniformly. The two new remote-absence checks (`author`, `issued`) sit
immediately after the remote response is confirmed to be a dict and before the
existing combined malformed-shape check, so a field that is present-but-malformed
still routes to the unchanged UNREACHABLE branch — only literal absence
(`entry.get(field) is None` / `remote.get(field) is None`) is newly SKIPPED.

**Spec sentence — written to the six cells, not to the coordinator's literal
wording.** The coordinator's suggested replacement text ("absent on either side, any
of the three compared fields ... is whole-check SKIPPED") contradicts the
coordinator's own asymmetry ruling one paragraph earlier (remote `title` stays
UNREACHABLE). Shipping it verbatim would have re-created the exact defect this round
exists to close: a spec sentence the implementation does not fully satisfy. The
landed sentence instead names all three local fields, both non-title remote fields,
and states the remote-title exception explicitly, in one sentence, without
reflowing the row:

> "An absent local `title`, `author`, or `year`, or an absent remote `author` or
> `year`, is whole-check SKIPPED, the reason naming the field, never folded into
> MATCHED — a remote record missing `title` entirely remains a malformed-response
> outage, not a legitimate absence (ruled 2026-08-25, audit gap closed)."

**Five existing tests were a partial fixture migration, corrected in place —** the
same pattern the coordinator named: a change lands on some call sites (the four new
SKIP branches) while pre-existing fixtures that happened to omit `author`/`issued`
kept exercising the *old*, now-wrong branch and staying green for the wrong reason.
Each was re-pinned to test only its original, single concern by adding the field
its payload was incidentally missing (the absent-field lane it accidentally
exercised now has its own dedicated test instead):
- `test_metadata_reports_author_family_and_given_initial_divergence` — both remote
  payloads were missing `issued`; added it so the test asserts author-mismatch
  detection, not year-absence.
- `test_metadata_compares_year_only_when_both_records_have_one` — its first half
  asserted MATCHED for a remote record with no `issued` (the exact bug). Split into
  `test_metadata_skips_when_registry_record_has_no_year` (now SKIPPED, exact reason)
  and `test_metadata_reports_year_divergence_when_both_records_have_one` (the
  genuine-mismatch half, unchanged in substance).
- `test_metadata_uses_csl_content_negotiation_for_non_crossref_agencies` — neither
  local nor remote had `issued`; added it to both so the test asserts
  content-negotiation routing, not year-absence.
- `test_metadata_treats_malformed_crossref_shapes_as_unreachable[remote4]` (the
  `{"author": [{}]}` malformed-author-shape row) — was missing `issued`; added it so
  the row still exercises malformed-author detection instead of tripping the new
  remote-year-absence SKIP first.
- `test_metadata_treats_malformed_csl_shape_as_unreachable` — neither side had
  `issued`; added it to both so the test still asserts malformed title/author-shape
  detection (content-negotiation path).

**New tests added:** `test_metadata_skips_entries_whose_local_bibliography_has_no_author`,
`test_metadata_skips_entries_whose_local_bibliography_has_no_year`,
`test_metadata_skips_when_registry_record_has_no_author`,
`test_metadata_skips_when_registry_record_has_no_year` (from the split above),
`test_metadata_reports_year_divergence_when_both_records_have_one` (from the split
above), and `test_metadata_treats_registry_record_with_no_title_as_unreachable` (the
construction proof that the remote-title asymmetry is unchanged). Every new/changed
assertion checks the exact reason string, not just the four-state result.

**Discriminator matrix, four new branches** (each hunk reverted individually,
target test rerun, confirmed RED for the stated reason, then restored):

| Branch reverted | Test | Result when reverted |
|---|---|---|
| Local `author`-absent check removed | `test_metadata_skips_entries_whose_local_bibliography_has_no_author` | Still SKIPPED, but reason became `"no-identifier — item has no year"` (fell through to the next check) — caught only because the test asserts the exact reason string, not just the four-state result |
| Local `issued`-absent check removed | `test_metadata_skips_entries_whose_local_bibliography_has_no_year` | `AssertionError` from the always-raising network fake — the check reached a network call it shouldn't have |
| Remote `author`-absent check removed | `test_metadata_skips_when_registry_record_has_no_author` | `Result.UNMATCHED` "mismatch — author family names differ" — the original bug, reproduced on demand |
| Remote `issued`-absent check removed | `test_metadata_skips_when_registry_record_has_no_year` | `Result.MATCHED` "matched" — the original "folded into MATCHED" bug, reproduced on demand |

Confirmed by construction, still unchanged: a present-and-matching field (all
MATCHED tests green), a present-and-differing field (title/author/year mismatch
tests all still UNMATCHED with their original reasons), a genuinely unreachable
registry (routing/network/status/malformed-shape tests all still UNREACHABLE), and
the remote-title-absent lane specifically (new dedicated test, UNREACHABLE
unchanged).

**Test arithmetic:** offline suite 1717 → 1722 passed, 7 skipped (net +5: four
dedicated new tests, plus +1 from splitting the one test whose first half pinned
the MATCHED bug). `ruff check .` / `ruff format --check .` run repo-wide this round
(not just on the changed files): 10 pre-existing errors and 5 reformat candidates,
all in unrelated `skills/find-sources/scripts/*` files untouched by this task —
confirmed absent from `git diff`/grep against `checks.py`/`test_checks.py`. `mypy
knowledge_harness/` clean. `stop_publish_gate.py` hook exits 0.

**New concern (destination: controller).** The fix scopes "absent" to literal
`is None` on the raw entry/remote dict value, matching the coordinator's own
six-cell measurement. That leaves the *present-but-empty* representations of the
same defect class untouched, one representation over: a local or remote
`"author": []` still reaches the comparison as an empty list (not `None`, so the
new SKIP guard doesn't fire) and can still produce a false UNMATCHED against a
populated other side; a local or remote `"issued": {}` or
`"issued": {"date-parts": []}` still parses to `(True, None)` and can still let the
year leg silently pass, letting the check reach MATCHED. Same root cause
(`_metadata_authors`/`metadata_year` treating "no meaningful value" as valid-empty
regardless of whether the key was omitted or explicitly emptied), one
representation the six-cell measurement didn't cover. Not fixed here — unruled, and
raising it now rather than leaving it for the next audit to rediscover.
**SUPERSEDED by Fix Round 2 below — measured, ruled, and closed.**

## Fix Round 2 (2026-08-25)

**What changed and why.** The coordinator measured the "New concern" above
directly (both lanes, both fields, canary asserted) and confirmed it in full: every
present-but-empty representation of `author`/`issued` still exhibited the original
bug — `author=[]` still UNMATCHED (both lanes), and `issued={}`,
`issued={"date-parts": []}`, `issued={"date-parts": [[]]}` all still MATCHED (both
lanes). `{"date-parts": []}` in particular is not an edge case — it is what
CSL/Crossref actually emit for a work with no recorded date, so **the common case
was the one still broken.** Ruled: this is the same defect one representation over,
not a smaller residual, and it lands in this task rather than being recorded for
the next audit to rediscover — the same principle already applied twice on this
axis (partial fixture migrations, partial field coverage) applies unchanged to
partial *representation* coverage.

**Scope, as ruled:**
- `author`: an empty list (`[]`, either side) is *no authors to compare*, not a
  contradiction — treated as absent, SKIPPED, same as the missing-key case.
- `issued`: `{}`, `{"date-parts": []}`, and `{"date-parts": [[]]}` (either side) all
  mean *no year present* — `metadata_year` already normalizes every one of these to
  `(True, None)`, so the honest reading is "well-formed, no value," i.e. absent, not
  "well-formed and comparably empty." Treated as absent, SKIPPED, same as the
  missing-key case.
- `title`: an empty/whitespace-only string — a genuine judgment call, reasoned
  below, decided as: **LOCAL blank title → SKIPPED (same as missing); REMOTE blank
  title → stays UNREACHABLE/malformed (same as missing).**

**Implementation.** A new `_is_blank(value)` helper (`value is None or
(isinstance(value, str) and not value.strip())`) replaces the raw `is None` check
for the local title guard. For `author`, the existing `_metadata_authors(...)` call
was already being computed early (round 1); the guard changed from checking the raw
dict value to checking the *parsed* result against `[]` — `_metadata_authors(None)`
and `_metadata_authors([])` both already produced `[]`, so this one change catches
both representations with no new parsing logic. Same move for `issued`:
`metadata_year(...)` was already computed early; the guard changed from raw
`is None` to `local_year_ok and local_year is None` — since `metadata_year` already
normalizes every "no real date" shape to `(True, None)`, this catches all three
empty representations (and any other shape `metadata_year` treats the same way) via
the one function it already delegates the normalization to, rather than
re-implementing shape-sniffing in `check_metadata` itself. The remote side mirrors
this exactly, plus one addition: the combined malformed-registry-metadata check
gained `not remote_title.strip()` (guarded by the preceding `not isinstance(...,
str)` short-circuit, so a non-string title never reaches `.strip()`) so a blank
remote title still routes to the unchanged UNREACHABLE bucket instead of falling
through to the mismatch comparison.

**The `title=""` judgment call, argued both ways, and the decision.** The
coordinator posed the sharpest form of the question directly: *is `""` a value the
registry could meaningfully disagree with?* A comparison against an empty-string
title *can* run — unlike an empty author list or an empty date, where there is
genuinely nothing to compare, an empty title string is still a string, and
`_metadata_text("")` is still a well-defined value the checker can byte-compare
against the registry's title. That is the strongest argument for leaving it
UNMATCHED: the comparison is not vacuous in the way the other two are.

It loses to a stronger argument about what the record would then *claim*. A real
bibliographic work always has some title — even a placeholder ("Untitled") is a
title. So a blank local title is not a genuine "this work has no title" state in
the way an anonymous work genuinely has no authors, or a forthcoming work genuinely
has no year yet; it is almost always a data-entry gap in the local record — the
same practical shape as the missing-key case round 1 already ruled SKIPPED for
exactly that reason ("a fact that will never resolve by retrying"). Reporting
"mismatch — title differs from registry" for it asserts a *contradiction* — that
the two records disagree about what the work is called — when the actual, honest
defect is that the local record does not have real title text yet. That assertion
would send a human investigating the wrong thing (compare the title strings) instead
of the right one (the local bibliography entry needs a title filled in). That is
the same "verification record claiming a comparison that never really happened"
defect class the whole of Fix Round 1 exists to close, one field over — so `""`
is treated identically to a missing key on the **local** side: SKIPPED, not
UNMATCHED.

The **remote** side is decided the opposite way, deliberately, preserving the
already-ruled local/remote title asymmetry (round 1: a registry record with no
title at all is a malformed response, not a legitimate data state, because real
registries essentially always populate title, unlike author/year which are
legitimately sometimes absent). The same reasoning applies to a *blank* remote
title exactly as it applied to a *missing* one: a Crossref/DataCite record
returning an empty title string is not a real, if unusual, bibliographic fact — it
is a sign the response itself is degraded. So remote `title=""` stays UNREACHABLE
("outage — malformed registry metadata"), symmetric with remote `title=None`, and
asymmetric with the local decision — both sides now treat blank exactly the way
they already treated missing.

**Spec sentence: left unchanged, per the coordinator's own scoping.** The
coordinator's instruction was to extend the §6 sentence only if the title decision
changed what it must *say* — otherwise leave it. It doesn't: the landed sentence
already reads "an absent local `title`... is whole-check SKIPPED... a remote record
missing `title` entirely remains a malformed-response outage." Treating a blank
string the same way a missing key is already treated is a widening of what counts
as *absent*, not a change to the claim the sentence makes about what happens once
something is absent. Left as-is.

**Boundary pins — the widening does not swallow malformed input as absent.** Two
new tests confirm the guard is on the parsed *value*, not merely presence:
`author: [{"family": ""}]` (a non-empty list with an invalid entry) still returns
UNREACHABLE "outage — malformed bibliography metadata" — `_metadata_authors` returns
`None` for it, not `[]`, so the new `== []` guard correctly does not fire.
`issued: {"date-parts": [["not-an-int"]]}` (a present, non-empty, wrong-typed year)
still returns the same UNREACHABLE reason — `metadata_year` returns
`(False, None)`, so the new `year_ok and year is None` guard correctly requires
`year_ok` to be `True` and does not fire on malformed-but-present data.

**New tests** (12 total): a 4-case parametrize for local empty representations
(`author-empty-list`, `issued-empty-dict`, `issued-empty-date-parts`,
`issued-empty-inner-list`), the registry-side twin (same 4 cases), a local
blank-title test, a remote blank-title test, and the two malformed-boundary pins
above. One pre-existing parametrize row in
`test_metadata_treats_malformed_crossref_shapes_as_unreachable` (the
malformed-`issued`-shape row) incidentally used `"author": []` and was updated to a
populated author list so it still exercises malformed-`issued` detection instead of
tripping the new author-absence SKIP first — the same "partial fixture migration"
pattern as fix round 1, one row this time.

**Discriminator matrix** (each of the six widened guards reverted to its round-1,
`is None`-only form individually, target test(s) rerun, confirmed RED for the
stated reason, then restored):

| Guard reverted | Test(s) | Result when reverted |
|---|---|---|
| Local title: `_is_blank` → `is None` | blank-title test | reached a network call it shouldn't have (always-raising fake) |
| Local author: `== []` → raw `is None` | `author-empty-list` (local) | same — reached a network call it shouldn't have |
| Local issued: `year_ok and year is None` → raw `is None` | all 3 local issued cases | same — reached a network call it shouldn't have; the `is None` case (unchanged elsewhere) stayed green throughout, confirming the revert isolated exactly the widening |
| Remote author: `== []` → raw `is None` | `author-empty-list` (remote) | `Result.UNMATCHED` "mismatch — author family names differ" — the original bug, reproduced on demand |
| Remote issued: `year_ok and year is None` → raw `is None` | all 3 remote issued cases | `Result.MATCHED` "matched" — the original bug, reproduced on demand |
| Remote title: dropped `not remote_title.strip()` | remote blank-title test | `Result.UNMATCHED` "mismatch — title differs from registry" — a false contradiction asserted over a blank field, reproduced on demand |

Each revert's sibling test (the `is None` case for the same field/side) stayed
green throughout every revert, confirming the discriminator isolates the new
widening rather than the whole guard.

Confirmed by construction, still unchanged: present-and-matching stays MATCHED,
present-and-*differing* stays UNMATCHED (title/author/year mismatch tests
untouched), a genuine outage stays UNREACHABLE, and `remote title` fully absent
(missing key) stays UNREACHABLE (its own dedicated test from round 1, unaffected).

**Test arithmetic:** offline suite 1722 → 1734 passed, 7 skipped (net +12: the
described new tests). `ruff check .` clean on changed files (same pre-existing,
unrelated findings elsewhere as prior rounds). `ruff format --check .` initially
flagged a line in `tests/test_checks.py` this round — fixed by running
`ruff format` on the file (one line collapsed to fit the line length; verified via
`git diff` that nothing else changed) — now clean, along with the same 5
pre-existing, unrelated reformat candidates in `skills/find-sources/scripts/*`.
`mypy knowledge_harness/` clean. `stop_publish_gate.py` hook exits 0.

No new concerns from this round — the residual this round closes was the only one
carried forward from round 1.
