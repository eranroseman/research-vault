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
