# Task 3 review - 45aa45d..d44452e

## Spec Compliance

**Verdict: issues.**

Steps 1, 2 and 4 land. Step 3 ships an instrument that does not do what the step
mandates.

- `tests/test_skill_contracts.py:184` - Step 3 asks for "a parametrized sweep
  over `skills/*/SKILL.md` extracting backtick-quoted check ids against the
  CLI's emitted set", so that "every check id any SKILL.md enumerates" is
  checked. The shipped extractor is anchored on the phrase "check id"/"check
  ids" and reads only the backticked run that follows the first such phrase on a
  line. Measured against the shipped corpus, it reads 4 of the 46 backticked
  known-check-id mentions and extracts from **zero** of the five multi-id
  enumerations that exist today (`import-source:46`, `publish:31`, `publish:37`
  twice, `verify-citations:31`). The sweep is real and carefully built, but it
  guards single mentions, not enumerations, which is the class the step names.
  Detail in Issues / Important below.

Everything else in the brief is met:

- **Step 1 (C-1).** The mandated sentence stands verbatim and as its own
  sentence: "Run the CLI; its output is always up to date."
  (`skills/verify-citations/SKILL.md:9`). The four-state table stays; the suite
  inventory at line 9 and the grouping list at line 27 are gone. Line 31's
  "every other check id (...)" parenthetical was also removed - beyond the
  brief's cited lines, argued from section 5's ruling ("stops hand-listing check
  ids altogether") and recorded in the commit body.
- **Step 2 (C-2).** Implemented in `skills/evidence-conventions/SKILL.md`, which
  the brief's Files line does not name; the C-2 card names that file and the
  parent resolved the deviation. **Ruling-contingent deviation:** the brief says
  "TWO registry codes are out of scope, not one"; the shipped closing sentence
  exempts one (`matched`) and gives `manual` its own table row. The commit body
  records this as an author ruling dated 2026-08-23, with the falsified "not
  shipped yet" rationale refuted against `hooks/stop_publish_gate.py:120,135`,
  `hooks/hooks.json` and `tests/test_hooks.py:698`. The deviation is disclosed,
  argued and consistent with the tree; it is contingent on that ruling being
  real.
- **Step 2's "pin with a test".**
  `test_evidence_conventions_accounts_for_every_reason_code`
  (`tests/test_skill_contracts.py:358`) asserts set equality against the live
  `inbox.REASON_CODES` in both directions plus disjointness. Confirmed that no
  such pin existed at base.
- **Step 4.** One commit, subject character-for-character as briefed. Suite
  re-run on d44452e: 1560 passed, 7 skipped, matching the report. The commit
  subject's "guards all skills" is technically true (all nine skills are
  parametrized) but overclaims what is guarded, per the Important finding.

### Cannot verify from diff

- **The 8-hook pre-commit form gate passing with no rewrites.** Not run here:
  `pre-commit run --all-files` invokes formatters that rewrite files, and this
  review is read-only. Controller check: run
  `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` on d44452e
  and confirm 8/8 Passed with no file modifications.
- **The 2026-08-23 author ruling on `manual`.** The commit body *records* a
  ruling that `manual` gets a table row and that the closing sentence exempts
  only `matched`; the brief says two codes stay off the table. The record can be
  verified, the ruling itself cannot. Controller check: confirm the ruling was
  issued as described; if it was not, Step 2's shipped sentence is a
  single-sentence revert away from the brief's wording.

Resolved during this review, so no longer cannot-verify items:

- Commit body: the log for d44452e shows both deviations with their code
  citations and the doctrine sentence verbatim.
- Working tree: the porcelain status is empty, so the report's temporary drift
  demonstrations were all reverted.
- Suite: `.venv/bin/python -m pytest tests -q` on d44452e gives 1560 passed,
  7 skipped.
- No pre-existing pin covered the changed prose: searching `tests/` at 45aa45d
  for "grouped by check id", "deterministic suite", "One registry code" and
  "every other check id" returns only an unrelated comment at
  `tests/test_publish.py:816`.

## Strengths

- The canonical check-id set is genuinely derived from code, and the derivation
  survives independent check. The AST scan of every `Outcome(...)` construction
  site yields 14 ids - the audit's own count, reached by a different method -
  and the union universe is 20. The three non-literal call sites are wrappers
  whose every argument is a literal the scan already reads; there is no hand list
  anywhere.
- The instrument is guarded, not just used.
  `test_the_emitted_check_id_scan_finds_the_pipelines_own_ids` pins the four
  registry-absent pipeline ids so the scan cannot silently degrade into
  `inbox.CHECK_IDS`, and
  `test_the_check_id_extractor_reads_a_run_and_stops_at_prose` pins the
  extractor on a literal sample with a deliberate negative leg. Neither is a
  tautology.
- The C-2 pin is a real instrument: set equality against `inbox.REASON_CODES` in
  both directions plus disjointness, so registering a reason code with neither a
  row nor a named exemption fails the build. Its docstring records the
  2026-08-23 ruling with a code citation, so a future editor meets the reason in
  the test.
- The `manual` deviation is handled the right way round: the card's rationale is
  falsified at HEAD, the implementer proved it against three code citations,
  preserved the card's decided substance, and put the whole record in the commit
  body rather than only in the report.
- Assertion messages carry actionable evidence - `line {number}: {check!r}` in
  the sweep, sorted set differences in the reason-code pin - so a failure names
  the offending line and token.
- The stale-claim sweep in the fix round is honest, and its three left-alone
  rulings are each correct: two audit hits are historical quotes that AGENTS.md
  says stand as written, and `docs/terminology.md:141` never carried the claim.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

**`tests/test_skill_contracts.py:184` - the sweep's phrase anchor makes it read
almost nothing, and it guards none of the enumerations shipped today.**
Status: **CONFIRMED** (reproduced independently in this review).

*What is wrong.* `_CHECK_ID_PHRASE` anchors extraction on the literal phrase
"check id"/"check ids", and `_enumerated_check_ids` (:255) reads only the first
backticked run that comes **after** the first such phrase on a line. Running the
shipped functions over the shipped corpus:

```text
factcheck-draft [(46, 'factcheck')]
import-source   [(52, 'identifier-discovery')]
publish         [(37, 'publish'), (42, 'publish')]
everything else []
TOTAL tokens read: 4     (of 46 backticked known-check-id mentions)
```

The five multi-id enumerations in the tree - `import-source:46`
(`doi`/`metadata`/`update-notice`), `publish:31` (five ids), `publish:37` (two
runs), `verify-citations:31` (the surviving minting-four list) - contribute
nothing, because in each case the run sits before the phrase or in a different
clause. Two mechanisms produce this: tokens before the phrase are never read,
and only the first phrase per line is consulted (a line reading "The check id
`citekey` is one; a second clause names check id `doi` too." yields only
`citekey`).

*Why it matters.* Step 3 is the substance of the task, and its whole purpose is
catching rename and typo drift in prose that lists check ids. The lists are
exactly what the sweep cannot see. The report's section 3a demonstration passes
only because it drifted line 27, which happens to sit after the anchor phrase; a
typo in `publish:31`'s five-id run would ship green. The overclaim is the
durable part of the harm: the test name
(`test_every_check_id_a_skill_enumerates_is_one_the_code_files`), the docstring
("catches the drift at build time"), the commit subject ("enumeration checker
guards all skills") and report section 2 ("`verify-citations` now contributes
nothing - it no longer enumerates", which is false: line 31 still enumerates,
the extractor just cannot see it) all tell a future editor that this drift class
is guarded. Report section 4's division of labour rests on the same false
premise.

*How to fix.* Keep the phrase anchor - it is the only thing that catches single
mentions like `factcheck-draft:46` - and add a co-occurrence anchor: any
backticked run in which two or more tokens are known check ids is a check-id
enumeration, and every token in that run must be known. Probed against all nine
shipped SKILL.md files in this review: the rule fires on exactly the five
enumerations above and produces zero false positives at HEAD
(`evidence-conventions:22`'s `quote`/`paraphrase`/`inference`/`open-question`
run carries only one known id, so it stays below the threshold). **This must
land together with the `_RUN_JOINER` fix below** - the probe is clean at HEAD
only because current runs break at prose gaps; while `|` counts as list
punctuation, a table row with two known ids in one cell and any backticked token
in the next cell would false-positive. Optionally also iterate
`_CHECK_ID_PHRASE.finditer(line)` so a second clause on one line is read; that
is empirically a no-op at HEAD but removes the second mechanism. Fixing this
also absorbs the residual noted under Refuted, since `verify-citations:31` and
`publish:37` would then be swept directly.

*Merge and refutation record.* Two lenses raised this defect at different
anchors in the same function (`:184` and `:270`), and a third raised the
same-line mechanism at `:255`; they are one finding. Two sub-claims from the
merged versions did **not** survive verification and are not part of it:
`skills/publish/SKILL.md:37` is **not** unguarded -
`tests/test_publish.py:806-856` already derives the minting set from
`verify._projection_identity` and asserts each id is backticked in that row -
and switching the phrase search to `finditer` yields zero new ids over the
shipped corpus.

### Minor (Nice to Have)

**`tests/test_skill_contracts.py:189` - `_RUN_JOINER` treats `|` as list
punctuation, so backticked tokens in adjacent table cells merge into one run.**
Status: CONFIRMED by probe; severity Minor because no shipped line trips it
today. Probed here: a table row whose first cell says "check id" and whose later
cells hold unrelated backticked tokens yields every one of those tokens as a
claimed check id. SKILL.md files are table-heavy and the
sweep is parametrized over every skill, present and future, so a future row that
mentions "check id" in one cell and backticks anything else in a later cell
fails the build on correct prose. Fix: drop `|` (and probably `/`) from the
character class, or split table rows on `|` before extracting. This becomes
load-bearing the moment the co-occurrence anchor above lands.

**`tests/test_skill_contracts.py:389` - `word = _COUNT_WORDS[len(exempt)]`
raises KeyError instead of asserting.** Status: NOT-VERIFIED-MINOR (raised by
all three lenses; mechanically evident from the code). `_COUNT_WORDS` covers 1
through 5. A future editor who tables every registry code, or who rewrites the
closing sentence without a backticked code, leaves `exempt` empty; every other
leg still passes and the pin dies with an opaque `KeyError: 0` instead of the
message it was written to give. The leg also pins phrasing rather than contract:
"Only `matched` stays off this table" is the same claim with the same exemption
count, and fails the regex. Fix: `_COUNT_WORDS.get(len(exempt))` plus
an explicit assertion, or express the leg as "if the sentence names a count
word, it must match".

**`tests/test_skill_contracts.py:215,225` - the AST scan reads only positional
first arguments and only `ast.Assign` module constants.** Status:
NOT-VERIFIED-MINOR (both blind spots verified latent in this review: the package
has no keyword-only `Outcome(check=...)` call among its 74 sites and no
annotated module-level string constant). A future `Outcome(check="new-id", ...)`
or `CHECK: Final[str] = "..."` would silently drop an id from the universe, and
`test_the_emitted_check_id_scan_finds_the_pipelines_own_ids` only catches total
degradation. The resulting failure would be loud (correct prose flagged
unknown), which is why this is Minor. Fix: fall back to `node.keywords` when
`node.args` is empty, and accept `ast.AnnAssign` targets in the constants map.

**`tests/test_skill_contracts.py:369` - the C-2 pin's docstring claims placement
enforcement the test does not give.** Status: NOT-VERIFIED-MINOR. The docstring
says "Moving it back off the table fails the equality below", but deleting the
`manual` row *and* naming `manual` in the closing sentence passes every leg (set
equality still holds, disjointness still holds, and `_COUNT_WORDS[2]` matches a
reworded sentence). The implementer's own concern 2 concedes that the pin proves
accounting, not placement - but the concession lives only in the report, and the
docstring is what a future editor reads. Fix: reword to "deleting the row
without adding a matching exemption fails the equality below; placement is not
mechanically pinned."

**`tests/test_skill_contracts.py:339` - the module's stated single
responsibility is now false.** Status: NOT-VERIFIED-MINOR. The module docstring
(lines 1-8) promises it "asserts only what the control model and plugin
architecture require of *every* skill" and that "nothing here is scoped to" a
particular skill, yet `EVIDENCE_CONVENTIONS` hard-codes one skill file and the
reason-code pin asserts only about it; `tests/test_skill_files.py` already
exists for skill-specific content. Fix: move the reason-code pin and its helpers
to `tests/test_skill_files.py`, or amend the docstring. The generic check-id
sweep is correctly placed either way.

**`skills/evidence-conventions/SKILL.md:88` - "and the only code in this table a
person writes" is not a claim the tree supports cleanly.** Status:
**CONTESTED**, Minor. The verification round refuted this at Important on the
grounds that every other cited writer is agent-actored (`__main__.py:716` stamps
`AGENT_ACTOR` unless `--actor` is given), leaving `manual` as the only
human-actored reason code (`hooks/stop_publish_gate.py:137`,
`actor="human:publish-bypass"`). That argument is incomplete: `inbox.append_ack`
(`research_vault/inbox.py:381-384`) *requires* a `human:` actor and runs
`validate_reason`, so every acknowledgment is a human-actored queue entry whose
reason must start with a registry code - and the shipped skills tell the agent
to have the person supply that reason (`skills/publish/SKILL.md:80`,
`skills/project-flow/SKILL.md:81`). Codes other than `manual` therefore do reach
the queue with a human actor. The clause is also unmandated prose beyond the
ruling, and unpinned - the same prose-asserts-what-code-does class the task
exists to remove. It stays Minor and non-blocking: on the "who originates the
code" reading the clause is defensible, since an ack echoes the code of the
finding it accepts. Fix: drop the exclusivity clause and keep the evidential
half, or narrow it to "the only row whose finding is recorded with a human
actor".

## Refuted During Verification

- **`skills/verify-citations/SKILL.md:31` - "a hand-maintained check-id
  enumeration survives in the file the task de-enumerates, and the new sweep
  cannot read it" (raised Important). REFUTED.** The extractor claim is true -
  the run precedes the phrase, so the sweep reads nothing from that line - but
  no defect follows on the axis claimed. All four ids (`doi`, `metadata`,
  `update-notice`, `quote`) are in `_known_check_ids()`, so the sweep would pass
  unchanged if it read them; the claim itself is true, and the code fact behind
  it is hard-pinned at `tests/test_publish.py:843`
  (`_minting_check_ids() == {"doi","metadata","update-notice","quote"}`, derived
  from `verify._projection_identity`), so the minting set cannot change without
  failing the build. Keeping this scoped, true list while deleting the
  exhaustive ones is the correct call. The residual - that this particular row
  has no pin of its own, unlike `publish`'s - is absorbed by the Important
  finding's fix.
- **`skills/evidence-conventions/SKILL.md:88` at Important - "the only code in
  this table a person writes is false", with `find-sources:72` and the `ack`
  invocations as counterexamples. REFUTED at Important, carried at Minor.**
  `find-sources:72`'s `--reason "not-admitted — ..."` is an agent-run command
  (no `--actor`, so `AGENT_ACTOR`), and `not-admitted` is additionally
  machine-filed at `__main__.py:204`, which is what the row's "no check files
  it" excludes. The same answer disposes of the second lens's
  `factcheck-draft:49-51,61` and `import-source:75-77` counterexamples: those
  are agent-run `finding` invocations. The finding survives at Minor only on the
  `ack` path, recorded above.
- **`tests/test_skill_contracts.py:270` sub-claims - "`publish/SKILL.md:37` is
  unguarded" and "iterate the phrase with `finditer`". REFUTED (the parent
  finding survives; these two legs do not).** `tests/test_publish.py:806-856`
  already implements the suggested pin for `publish:37`, deriving the minting
  set from `_projection_identity` and asserting each id appears in that MATCHED
  row, and that line does contribute `publish` to the sweep. The `finditer`
  change is an empirical no-op over the shipped corpus - re-probed here, zero
  new distinct ids.

## Assessment

**Task quality: Needs fixes.**

Steps 1, 2 and 4 are done well, the deviations are disclosed and argued against
code, and the derived-from-code universe plus its two guard tests are better
engineering than the brief asked for. The one blocking problem is Step 3's
reach: the sweep reads 4 of 46 check-id mentions and guards none of the five
enumerations shipped today, while its name, docstring, commit subject and report
all claim otherwise - and a cheap fix (a co-occurrence anchor, landed with the
`_RUN_JOINER` correction) closes it with no false positives at HEAD.
