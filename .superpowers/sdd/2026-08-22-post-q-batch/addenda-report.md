# Addenda report — Task 9 addendum + Task 4 addendum

Two independent, disjoint-file addenda to already-landed, reviewed tasks.
Per branch precedent (Task 3: de1867d corrected forward rather than
rebasing under a3db464), neither original commit (acd38b5, 8e7b136) was
touched — each addendum lands as its own fresh commit.

Base at start: `c418cf7`. Baseline suite run before any change: **1576
passed, 7 skipped** (matches the brief's stated baseline).

## Addendum 1 — `summary()` also emits `oldest_age_days`

Commit: `eff8d67` — `feat: inbox summary emits oldest_age_days`
Files: `knowledge_harness/inbox.py`, `tests/test_inbox.py`

### What was implemented

`inbox.summary()` (`knowledge_harness/inbox.py:712`) now returns a third
key, derived from the *same* SKIPPED-filtered `entries` list `oldest` is
already computed from — confirmed by reading, not re-implemented:

```python
entries = [
    entry for entry in open_entries(vault) if entry.result != Result.SKIPPED.value
]
oldest = min((entry.date for entry in entries if entry.date), default=None)
oldest_age_days = (
    None
    if oldest is None
    else (
        datetime.datetime.now(datetime.UTC).date()
        - datetime.date.fromisoformat(oldest)
    ).days
)
return {
    "unacknowledged": len(entries),
    "oldest": oldest,
    "oldest_age_days": oldest_age_days,
}
```

No new constant, no `aging:` boolean, no threshold — per the withdrawn-draft
ruling recorded in `progress.md` (~line 1319): the guard in
`skills/project-flow/SKILL.md` is deliberately continuous ("an aging queue
earns more prominence the longer it goes untouched"; "nothing here blocks
on age"), and no Whittaker threshold exists anywhere in the tree to quantize
it into a boolean. The mechanism supplies the day count; the skill's own
judgment keeps deciding what counts as old.

### Clock choice

`datetime.datetime.now(datetime.UTC).date()` — the exact convention already
established at `inbox.py:305` (used by `append_entry`'s default `date`).
Parsing uses `datetime.date.fromisoformat`, matching `_validate_date`'s own
parse at `inbox.py:172`. Using the same clock/parse pair the rest of the
module already uses means `oldest_age_days` and `oldest` can never disagree
about what day it is.

### The `None` case

`oldest_age_days` is `None` exactly when `oldest` is `None` — i.e., nothing
unacknowledged, so there is no age basis to report. This mirrors `oldest`
itself rather than inventing a sentinel like `-1` or `0`, and keeps the two
fields' "nothing to report" states aligned. A freshly filed entry (dated
today) correctly reports `0`, not `None` — the docstring states this
explicitly to head off conflating "no entry" with "an entry aged zero days."

### Why the test cannot rot on a calendar (and the one thing it still can)

Task 9's own test is `test_skipped_entries_not_counted_unacknowledged`
(confirmed via `git log -S` that it was introduced only in acd38b5, Task
9's landed commit — `test_summary_counts_and_age`, which also asserts
`summary()`, predates Task 9 by many commits, back to 815fead). Per the
brief, this is the one test that gets a new, deliberate assertion:

- The UNMATCHED fixture's date is computed as `today − 3 days` at test run
  time (`unmatched_age_days = 3`), not hardcoded to a fixed calendar string.
  The assertion is `"oldest_age_days": unmatched_age_days` — i.e. `3`, a
  fixed integer that never changes, because the *fixture* moves with
  "today" instead of the assertion trying to track "today" after the fact.
  Rerunning this test in a year still files the entry 3 days before
  whatever "today" is then, and still asserts `3`. This is the "cleanest
  fix" the brief names, chosen deliberately over asserting
  `oldest_age_days == (today - fixed_date).days` inline, which would work
  but would make the test's oracle a copy of production's own formula.
- The companion SKIPPED entry stays at its original fixed literal
  (`2026-08-01`, from the already-landed Task 9 commit) precisely because
  it is *excluded* from the age basis and its exact age never matters —
  only that it does not contribute at all. That is itself meaningful:
  today (2026-08-24) that SKIPPED date is already 23 days old and only
  grows; if the SKIPPED-filter in `summary()` ever regressed and let it
  back into the age basis, `oldest_age_days` would jump to ≥23 and keep
  climbing — it could never coincide with the fixed, independent `3` the
  test asserts. So the test remains a real regression check, not a
  tautology, indefinitely.
- **What this does *not* rule out**: a UTC-midnight straddle between the
  test reading "today" to build the fixture and `summary()` reading the
  clock again microseconds later during the assertion. That is a
  vanishing-probability *flake*, not calendar rot — the two are different
  failure classes. I did not add extra hardening against it (e.g.
  re-reading the clock after the call and widening the assertion to a
  range) because the window is a fraction of a second across a boundary
  that occurs once every 86,400 seconds; documenting it here rather than
  adding speculative machinery seemed the right trade.

The first assertion in the same test (queue holding only the SKIPPED entry)
now asserts `{"unacknowledged": 0, "oldest": None, "oldest_age_days":
None}` — the None-case coverage.

### Other pins the suite revealed

The brief warned not to trust any surface list. Grepping `summary(` in
`tests/` (not a curated list — a plain `grep -n "summary(" tests/*.py`,
then mapped each hit to its enclosing test function) found seven
exact-dict-equality assertions across five test functions in
`tests/test_inbox.py`. I did not run the file red before editing it: dict
equality in Python fails whenever either side has a key the other lacks,
so a new third key on `summary()`'s return value breaking every unqualified
`== {...}` comparison against it is a certainty from the language's own
semantics, not something that needed a RED run to establish. What I did
verify empirically is the enumeration itself — after editing all seven
sites, the full suite (`.venv/bin/python -m pytest tests -q`) came back at
the same 1576/7 as baseline; had I missed an eighth site, that run would
have failed instead, which is the check that actually matters here. Two of
the seven sites are Task 9's own test (covered above); the other five
sites, spread across four unrelated, older test functions, needed
mechanical updates just to keep comparing equal, since they are not
testing the age math themselves:

- `test_changed_hash_recurrence_stays_open_in_summary_and_open_entries`
  (one site, `oldest = "2026-08-16"`)
- `test_update_notice_ack_closes_only_its_exact_notice_fingerprint` (two
  sites, both `oldest = "2026-08-01"`)
- `test_a_legacy_update_notice_is_closed_only_by_an_ack_naming_it` (one
  site, `oldest = "2026-08-17"`)
- `test_summary_counts_and_age` (one site, `oldest = "2026-08-01"`;
  predates Task 9 — introduced in 815fead, not acd38b5)

For these, I added a small test-local helper, `_age_days(date_str)`, that
mirrors production's exact clock/parse formula and is used only where the
test's real point is something else (dedup, notice fingerprints, ack
scoping) and the dict-equality comparison is otherwise incidental. Using
the same formula here is a deliberate, narrower trade-off than in Task 9's
dedicated test: these five sites aren't validating the age computation
itself, they just need to keep comparing equal, so mirroring the formula
is pragmatic rather than tautological in a way that matters — the one test
that actually needs to catch an age-math regression (Task 9's) uses the
independent fixed-N construction instead.

No other file needed changes: `knowledge_harness/scaffold.py`'s
`_inbox_probe` and `knowledge_harness/__main__.py`'s `cmd_inbox` both read
`summary()` but only pull `"unacknowledged"`/`"oldest"` by key (no exact
dict-equality), and no test outside `test_inbox.py` compares the full
`summary()` dict (confirmed by grep for `"oldest"` across `tests/` and
`knowledge_harness/`).

### Explicitly not done

- `_inbox_probe` in `scaffold.py` was not rewired to surface
  `oldest_age_days` — it computes no age today and the brief rules this out
  of scope.
- `inbox.summary()` was not renamed — a prior naming ruling classes it
  dev-facing ("rename or leave, not a blocker").

## Addendum 2 — the XML annotation in find-sources' vendoring note

Commit: `ebea360` — `docs: find-sources vendoring note records the XML parsing boundary`
File: `skills/find-sources/SKILL.md`

### What was implemented

One new bullet appended to the "Vendoring notes: where the vendored files
are wrong" section's first list (the six upstream-fact annotations from
Task 4, i.e. the triage's "Class 2" items), placed as the seventh and
last, immediately before the "Two upstream defects have no correction to
read, only a guard..." lead-in for the two class-3 guards. It joins the
annotations list rather than the guards list because, like its six
siblings, it states a fact about the vendored code for the reader to hold
alongside the frozen files — it does not tell the agent to do or avoid
doing anything operationally, which is what distinguishes the two guard
bullets.

Shipped text (diff):

```diff
 - **`references/openalex.md:162-172` teaches the abstract inversion `scripts/openalex_abstract.py` exists to prevent, and never mentions the script.** Its snippet builds `{position: word}`, which silently drops every duplicate position — and real payloads contain them. Reconstruct abstracts with the script, never with that snippet.
+- **`arxiv_atom.py`/`jats_to_text.py` parse network XML via stdlib ElementTree by upstream's choice.** Not XXE (no entity expansion); residual expansion-DoS rides the runtime's libexpat; kept frozen per the vendor rule, noted in the K-Dense upstream queue beside the jats arg-type finding.

 Two upstream defects have no correction to read, only a guard to follow until a re-vendor fixes them:
```

### Fit to sibling style

Every sibling bullet in this list opens with a **bold factual lead
sentence** (subject, claim, period) naming the file(s) in question, then
continues in plain prose. E.g. the immediately preceding sibling:

> - **`references/openalex.md:162-172` teaches the abstract inversion
>   `scripts/openalex_abstract.py` exists to prevent, and never mentions
>   the script.** Its snippet builds `{position: word}`, which silently
>   drops every duplicate position...

The decided addendum text was one dash-joined sentence
("...by upstream's choice — not XXE...; ...; kept frozen..."). I split it
at the natural boundary into a bold lead ("...parse network XML via
stdlib ElementTree by upstream's choice.") followed by the three
semicolon-joined clauses verbatim as the explanation, capitalizing only
the first word ("Not XXE...") to start the new sentence. All three clauses
— "not XXE (no entity expansion)", "residual expansion-DoS rides the
runtime's libexpat", and "kept frozen per the vendor rule, noted in the
K-Dense upstream queue beside the jats arg-type finding" — ship intact and
unweakened; nothing was generalized into a broader warning.

### Pins

No test pin required updating. The only test in the tree that reads
`skills/find-sources/SKILL.md`'s content,
`test_the_skill_names_exactly_the_environment_variables_the_scripts_read`
(`tests/test_find_sources_vendor.py`), pins environment-variable names by
walking the AST of `scripts/*.py` and checking `SKILL.md` names each one;
this annotation introduces no new environment variable, so that pin is
untouched. No other test counts bullets in this section or otherwise pins
the vendoring-note section's exact prose or length (confirmed by grep
across `tests/` for section-specific counts/strings — none found).
`skills/find-sources/scripts/` and `skills/find-sources/references/` were
not touched, per the vendor rule.

## Test results

- Baseline (before any change, at `c418cf7`):
  `.venv/bin/python -m pytest tests -q` → **1576 passed, 7 skipped**.
- After Addendum 1 (`eff8d67`): full suite **1576 passed, 7 skipped**
  (unchanged — no test functions added or removed, only assertions
  extended); form gate **8/8** (ruff-format reflowed the two touched files
  once — long lines it wrapped — and that reflow is included in the
  commit).
- After Addendum 2 (`ebea360`): full suite **1576 passed, 7 skipped**; form
  gate **8/8**, no reformatting needed.
- Final state (both commits applied): full suite **1576 passed, 7
  skipped**; form gate **8/8**.

## Concerns

1. Addendum 1's dedicated age-math test has a vanishing-probability
   UTC-midnight-straddle flake window between building the fixture date and
   `summary()` reading the clock again during the assertion (see above,
   under "why the test cannot rot"). This is not calendar rot and was not
   hardened against; flagging it rather than silently accepting it.
2. `oldest_age_days` is not surfaced anywhere agent-facing yet (`_inbox_probe`,
   `project-flow`'s SKILL.md) — deliberately out of scope per the brief, but
   it means the addendum's stated purpose (killing the agent's date math) is
   only half-realized until a later task wires a consumer to read the new
   key. Flagging so it isn't lost; not a defect of this addendum.
3. None of Addendum 2's three clauses were independently re-verified against
   the vendored scripts in this session (e.g., re-confirming `arxiv_atom.py`
   and `jats_to_text.py` really only use stdlib `ElementTree` with no
   custom entity handling) — the text was decided and ruled 2026-08-24 per
   the brief, and the instruction was to ship it as decided content, not
   re-derive it. Noting the provenance is the ruling, not my own check, in
   case that distinction matters later.
