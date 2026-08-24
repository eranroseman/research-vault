# Task 17b review — `a2d7942..f3f5a7f`

Reviewer: independent verification pass. Every claim below was re-run, not read.

## Verdicts

**(A) SPEC COMPLIANCE — PASS with one unmet clause.**
Steps 1, 2b and 3 are met with the brief's exact values. Step 2 is met in its
mechanism (four keys + `generated` self-guard, machine-actor class test) but
leaves one clause unimplemented: "Scope stated in the lint's finding text."
The shipped reason string states the rule, never the boundary, and the
forging-is-out-of-scope boundary appears nowhere in shipped code or docs —
only in the implementer's report file.

**(B) CODE QUALITY — GOOD.**
`_bump_generated` is genuinely fail-closed; the byte-preservation contract its
docstring claims holds under every probe including CRLF. The defects are
duplication (three spellings of one timestamp, a second spelling of the
frontmatter wire format), one predicate that is weaker than the codebase's own
existing validator, an inaccurate absence claim in the report, and comment
hygiene against an empty commit body.

## Method

Scratch trees built with `git archive <sha> | tar -x -C /tmp/…` (no `.git`, so
no shared-git-state exposure). Import-path canary run in each tree before any
measurement: `knowledge_harness.__file__` resolved to the scratch tree, not the
worktree, in every variant.

| tree | contents |
|---|---|
| `/tmp/hk-head` | `f3f5a7f` as shipped |
| `/tmp/hk-base` | `a2d7942` |
| `/tmp/hk-mixed` | head + `lints.py` reverted to base |
| `/tmp/hk-mixed2` | head + `archive.py` reverted to base |

Independent full-suite run in `/tmp/hk-head`: **1577 passed, 7 skipped** —
matches the report and the stated +8 over the 1569 baseline. `ruff check`,
`ruff format --check` and `mypy` clean on the touched files (re-run, not
accepted).

## 1. Per-key discrimination matrix (re-run, not read)

`tests/test_lints.py::test_hand_edited_machine_owned_frontmatter_key_is_drift`,
run in `/tmp/hk-mixed` (new test + **base** `lints.py`). Full outcome list
captured per parameter, so double coverage is visible rather than inferred.

| key | outcome list at BASE | discriminates? | double coverage at base |
|---|---|---|---|
| `archive-url` | `[]` | YES | none — new check is sole coverage |
| `managed-sha256` | `['schema-violation — stale managed-sha256']` | **YES** | UNMATCHED already present via `notes.validate_managed_witness` |
| `fixity-sha256` | `[]` | YES | none |
| `generated` | `[]` | YES | none |
| `citekey` | `[]` | YES | none |

All five FAIL at base and PASS at head. **The `managed-sha256` hazard is real
but the shipped test survives it**: at base the note is already UNMATCHED, so a
test asserting mere UNMATCHED-ness would pass at base and prove nothing. The
shipped test asserts the exact reason string
(`drift — managed-sha256 changed without writer attestation`), which is absent
at base — so it discriminates. The implementer's table is accurate.

Worth recording as an observation, not a defect: for `managed-sha256` the new
check adds a distinct *reason* but no new *detection* — that key was already
caught. The other four keys gain detection that did not exist.

Adjacent tests, same run:

- `tests/test_archive.py::test_a_bare_archive_url_hand_edit_fails_the_closing_guard`
  — FAILS at base (`['schema-violation — missing managed-sha256']`), passes at
  head. Discriminates.
- `test_screening_status_hand_edit_is_not_evidence_layer_drift` — passes at base
  and head. Correct for a negative control; it guards against future
  over-broad expansion of `_MACHINE_OWNED_FRONTMATTER_KEYS`, which is a real
  regression it can catch.

**Step 2b is load-bearing, not tidying.** In `/tmp/hk-mixed2` (head + base
`archive.py`), `test_a_legitimate_archive_run_passes_the_closing_guard` FAILS
on `assert not any(item.reason.startswith("drift"))`. Without the
`_bump_generated` wiring, every legitimate `archive-source` run would be
flagged as drift.

## 2. The clock and the wire format

`knowledge_harness/archive.py:139-141` is a byte-identical re-spelling of
`knowledge_harness/__main__.py:267-268`:

```python
now = datetime.datetime.now(datetime.UTC).replace(microsecond=0)
… now.isoformat().replace("+00:00", "Z")
```

A third spelling lives at `knowledge_harness/notes.py:215`
(`generated_at = f"{accessed}T00:00:00Z"`, date resolution) as `render_note`'s
default.

**Severity: Minor** — and the reasoning matters, because the obvious worry does
not materialise. The new lint compares `generated` for *inequality* and then
tests `by` for the machine-actor prefix; it never inspects `at`'s format. Two
writers disagreeing on format would therefore still produce a legal
attestation. The real exposure is `notes._valid_generated`
(`knowledge_harness/notes.py:195-209`), which requires `at.endswith("Z")` and
`fromisoformat`-parseability: a writer that drifts off that spelling makes
`render_note`'s `projection_changed` permanently true, re-bumping `generated`
on every render and destroying byte-identical-rerender preservation. That risk
predates this task; the diff adds a third independent place for it to start.
Recommend one shared helper.

Second duplication, same family: `archive.py:168-172` hand-rolls
`f"generated: {{{inner}}}"`, re-implementing `frontmatter.serialize`'s
inline-dict branch (`frontmatter.py:75-82`). Verified byte-equal today
(probe 8: both emit
`generated: {by: "knowledge_harness/0.1.0", at: "2026-08-24T00:00:00Z"}`), but
it is a second spelling of the same wire format with nothing holding them
together. **Minor.**

The report's "`render_note`'s only production caller is `__main__.py:270`"
absence claim was re-verified with a broader grep than the report's — including
`from .notes import` aliasing, which only imports `note_path`, `MANAGED_OPEN`,
`MANAGED_CLOSE`. Claim holds.

## 3. `_bump_generated`'s single-line assumption — empirical results

Direct probes against `/tmp/hk-head`'s package:

| case | result |
|---|---|
| no `generated` key (insert path) | OK; exactly one line added, **zero removed**; managed region, witness, human key byte-identical |
| list-style `generated:` + `  - {…}` | `ArchiveError: generated write broke the frontmatter: list item outside list` |
| nested-map `generated:` + indented `by`/`at` | `ArchiveError: … nested maps unsupported (flat schema, spec §5)` |
| CRLF throughout, no `generated` | OK; `\r\n` preserved on the inserted line and everywhere else |
| CRLF with existing `generated` | OK; `\r\n` preserved on the replaced line |
| two `generated:` lines | `ArchiveError: note carries 2 generated fields, need one` |
| no frontmatter | `ArchiveError: literature note has no frontmatter` |
| unterminated frontmatter | `ArchiveError: literature note frontmatter is unterminated` |
| `generated-by:` lookalike key | correctly ignored; new `generated` inserted, lookalike untouched |

**The byte-preservation contract the docstring claims holds.** The parse-back
round-trip guard (`archive.py:184-189`) turns every abnormal serialization into
a fail-closed `ArchiveError` rather than a mangled note. No corruption path
found.

The "some other key's *value* contains a line starting with `generated:`" case
is **unreachable**, and I verified the premise against the parser rather than
asserting it: `frontmatter.parse` (`frontmatter.py:143-165`) is strictly
one-line-per-key — non-`  - ` indented lines raise, and a line that reads
`generated: …` *is* a `generated` key to the parser. Probe 4 confirms: a value
written across two lines parses as two separate keys. The line scan and the
parser therefore cannot disagree.

## 4. The predicate's edge cases (`lints._frontmatter_attestation_outcomes`)

Called directly with synthetic dicts — no git needed.

| case | result | assessment |
|---|---|---|
| `generated` absent → present (machine), `archive-url` added | legal | correct — this is `archive.py`'s own insert path |
| `generated` absent → present (machine), nothing else | legal | correct |
| `generated` present → absent, `archive-url` edited | drift on **both** | correct — deleting the attestation is caught |
| `generated` present → absent, nothing else | drift on `generated` | correct |
| **machine `by` + garbage `at` (`"banana"`)** | **LEGAL** | see finding 1 |
| **machine `by`, `at` key removed entirely** | **LEGAL** | see finding 1 |
| legit `generated` bump + unrelated `citekey` hand-edit riding along | **LEGAL** | spec-compliant false negative; see finding 5 |
| `generated` unchanged (machine) + `archive-url` edited | drift | correct |
| `generated` → `human:eran` + `archive-url` edited | drift on both | correct, matches brief |
| `__version__` bump only (`0.1.0`→`0.2.0`) | legal | correct — class test works as the comment claims |
| `generated` non-dict → different non-dict + `archive-url` edited | drift on `archive-url` only | `generated` change invisible; see finding 8 |
| `generated` dict → non-dict + `archive-url` edited | drift on both | correct |
| `by = "knowledge_harness/evil"` | legal | stated boundary (class test), brief-sanctioned |
| base frontmatter unparseable | no finding, silently skipped | see finding 9 |
| all four keys edited, no attestation | four distinct drift reasons, sorted | correct |

No divergence found between code and brief on the cases the brief names. The
two divergences from *intent* are findings 1 and 5.

## 5. The disclosed scope deviation (`test_verify_cli.py`)

**Git safety: confirmed clean.** `net_vault` (`tests/conftest.py:142`) derives
from `fixture_vault` → `tmp_vault` (`tests/conftest.py:25-29`), which is
`tmp_path` with its own `git init -q`. Every new `git add -A` / `git commit`
in the diff passes `cwd=net_vault` or `cwd=fixture_vault`. No path reaches the
real repository.

**The change preserves what the test was testing.** The subject of
`test_no_attachment_acknowledged_warning_stays_suppressed_across_effects` is
warn-notice suppression on a note with no attachment hash. After the commit,
the worktree note still lacks `fixity-sha256` when `verify_state` runs — only
HEAD changed. Every suppression assertion (`warning_effective is False`,
`counts` equality, no open entry, two `update-notice` events, `code == 0`,
warning absent from output) exercises the same path. The commit was necessary,
not cosmetic: without it the new guard reports drift (reproduced directly) and,
per the implementer's pre-fix run, `code == 0` fails — the drift half I re-ran,
the exit-code half rests on their account.
Verdict: preserved, not weakened.

**But the report's accompanying absence claim is false** — see finding 2.

## 6. Duplicate-key evasion (report concern 2) — VERIFIED

`frontmatter._mapping_from_items` (`frontmatter.py:27-30`) builds
`dict(items)`, so `.get()` returns the last copy while `source_items` retains
order. Probe:

- base `archive-url: "https://a/1"`; candidate carries
  `archive-url: "https://EVIL/9"` then `archive-url: "https://a/1"` →
  `.get()` returns `https://a/1` → **NO FINDING**.
- Same for a duplicated `citekey`.

The claim is correct. Only `managed-sha256` has an independent duplicate guard
(`notes.validate_managed_witness` iterates `_mapping_items`, not `.get()`, and
emits `schema-violation — duplicate managed-sha256`); `archive-url`,
`fixity-sha256` and `citekey` have none.

Deferral is correct — the brief scopes Step 2 to a value comparison over five
named keys, and closing this needs a `_mapping_items`-based comparison across
all four. But per AGENTS.md this repo tracks work in GitHub Issues; it should
be filed, not left as a paragraph in a report file that nothing reads again.

## Findings

1. **Important** — `knowledge_harness/lints.py:652-654`: `_machine_attested`
   tests only `by`, never `at`. `{by: "knowledge_harness/0.1.0", at: "banana"}`
   — and even `{by: …}` with no `at` at all — legalizes edits to all four
   machine-owned keys (probes c, c2). `notes._valid_generated`
   (`knowledge_harness/notes.py:195-209`) already validates that shape
   (exactly `{by, at}`, non-empty `by`, `fromisoformat`-parseable, `Z`-suffixed)
   and is not reused. Spec-compliant, since the brief names only `by` — but a
   one-line strengthening that closes a whole class of half-forged attestation.

2. **Important** — `.superpowers/sdd/2026-08-22-post-q-batch/task-17b-report.md`
   claims "the other four `fixity-sha256`-editing call sites in
   `test_verify_cli.py` all call `_target_hash` directly and never exercise
   `lint_evidence_layer`." False.
   `tests/test_verify_cli.py:1505` and `tests/test_verify_cli.py:1541` both
   hand-edit `fixity-sha256` out of `smith2020.md` **uncommitted** and then call
   `verify_state`, which reaches `lint_evidence_layer` at
   `knowledge_harness/verify.py:1014`. Reproduced directly: that setup now
   yields `['drift — fixity-sha256 changed without writer attestation']`. The
   tests still pass because they assert on hashes and inbox entries, not on the
   report — so the suite is silently carrying unasserted drift findings. Not a
   code defect; a wrong verification claim that a future assertion on
   `report["counts"]` will turn into a surprise failure.

3. **Important** — `knowledge_harness/lints.py:670-690`: Step 2's clause
   "Scope stated in the lint's finding text" is unmet. The reason string is
   `drift — {key} changed without writer attestation`, which states the rule
   but not the boundary. The forging-is-recorded-bypass boundary
   (spec §2's stated-boundary idiom, `docs/superpowers/specs/2026-08-16-foundation-spec.md:19`)
   is stated in no shipped artifact — not the reason string, not the module
   comment at `lints.py:618-623`, not the docstring at `lints.py:658-663`, not
   an ADR. It exists only in the report's concern 4. The reason-string
   convention here (`class — detail`) argues against a sentence in the string;
   the docstring or an ADR would satisfy the intent. Either way the boundary
   must land somewhere durable.

4. **Minor** — `knowledge_harness/archive.py:139-141` duplicates
   `knowledge_harness/__main__.py:267-268` byte for byte; `notes.py:215` is a
   third spelling. The lint's equality test makes format skew *harmless to the
   legality decision* (only inequality plus `by` matter), so the feared
   consequence does not materialise — but `notes._valid_generated`'s `Z`
   requirement turns any future divergence into permanent re-render churn.
   Extract one helper.

5. **Minor** — `knowledge_harness/lints.py:673-681`: attestation piggy-backing.
   One legitimate `generated` bump legalizes *every* machine-key change in the
   same diff, so an unrelated `citekey` hand-edit riding along with a real
   `archive-source` run passes silently (probe d). Inherent to the brief's own
   "iff" formulation and therefore spec-compliant — but the report's concern 4
   discloses only *forged* attestation, not *borrowed* attestation. Should be
   disclosed as a boundary alongside it.

6. **Minor** — `knowledge_harness/archive.py:168-172` re-implements
   `frontmatter.serialize`'s inline-dict emitter (`frontmatter.py:75-82`).
   Verified byte-equal today; nothing keeps them equal tomorrow.

7. **Minor** — `knowledge_harness/lints.py:657`:
   `_frontmatter_attestation_outcomes(raw_path, base_data, candidate_data)`
   carries no annotations, while every neighbour in the module is annotated
   (`_managed_bytes`, `_frontmatter`, `_generated`, `_machine_attested`).

8. **Minor** — `knowledge_harness/lints.py:647-649`: `_generated` coerces any
   non-dict `generated` to `None`, so a change *between* two malformed non-dict
   `generated` values is invisible (probe h) while dict→non-dict is caught.
   Only reachable on an already-broken note; no lint validates `generated`'s
   shape anywhere.

9. **Minor** — `knowledge_harness/lints.py:667-668`: if the *base* note's
   frontmatter is unparseable or non-UTF-8, the entire per-key check is skipped
   silently. The candidate side is covered by `validate_managed_witness`'s
   `schema-violation — malformed managed boundary`; the base side has no
   compensating outcome.

10. **Minor** — `knowledge_harness/lints.py:632-644` re-parses every surviving
    candidate note's frontmatter, which `notes.validate_managed_witness` already
    parsed in the same function's first loop (`lints.py:702`). Two full parses
    per note per run.

11. **Minor (comment hygiene)** — history and provenance in comments, against
    this repo's rule that they belong in the commit body:
    `knowledge_harness/lints.py:623` ("task 17b"),
    `knowledge_harness/lints.py:660` ("Legality rule (ruled 2026-08-24)"),
    `knowledge_harness/archive.py:150` ("task 17b step 2b"),
    `tests/test_archive.py:115`, `tests/test_archive.py:518`,
    `tests/test_archive.py:543`, `tests/test_lints.py:829`,
    `tests/test_verify_cli.py:1047`. Compounding it: **`f3f5a7f`'s commit body
    is empty** — the subject line is the entire message — so the provenance had
    nowhere else to go. The `docs/terminology.md` citation at `lints.py:627-630`
    is the one comment that earns its place: it states an external constraint
    the code cannot show.

12. **Minor (test hygiene)** —
    `tests/test_archive.py:542` `test_a_bare_archive_url_hand_edit_fails_the_closing_guard`
    duplicates the `archive-url` parameter of
    `test_hand_edited_machine_owned_frontmatter_key_is_drift`. It does
    discriminate (verified failing in `/tmp/hk-mixed`), so it is not vacuous —
    but the report itself notes it was "green throughout" Step 2b, i.e. it was
    added for illustration rather than coverage. No test found that asserts
    nothing meaningful; no test name found that overclaims its body.

13. **Minor (process)** — report concern 2 (duplicate-key evasion) is verified
    and correctly deferred, but AGENTS.md routes deferred work to GitHub Issues.
    Concerns 1 (other `MANAGED_FIELDS` unguarded) and 3 (renamed files skip the
    per-key check) are in the same position.

## Confirmed correct (re-run, worth recording)

- Commit subject is byte-identical to the brief's Step 3 string.
- `_bump_generated` fails closed on every abnormal input probed; the
  byte-preservation contract holds, CRLF included.
- All five parametrized keys discriminate against base production code.
- Step 2b is load-bearing, proven by reverting `archive.py` alone.
- Suite independently reproduced at 1577 passed / 7 skipped.
- New `git` calls in tests operate only on pytest `tmp_path` vaults.
- `render_note`'s single production caller always passes an explicit
  second-resolution `generated_at`, so the date-resolution default at
  `notes.py:215` cannot mask a content change in production.

## ⚠️ Cannot verify from diff

None. Every claim in scope was reproducible from the shipped tree.
