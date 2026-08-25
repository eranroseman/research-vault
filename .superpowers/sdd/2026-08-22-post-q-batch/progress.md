# SDD ledger — plan: docs/superpowers/plans/2026-08-22-post-q-batch.md

Worktree: /home/eranr/New folder/.claude/worktrees/fix+pre-slice-batch
Branch: fix/pre-slice-batch
Merge base: 002cb25
Baseline suite: 1548 passed, 7 skipped (offline)
Venv: .venv (created in worktree, python 3.12.3, `pip install -e ".[dev]"`)

Pre-flight: author committing an unrelated 2026-08-23 re-ruling to
docs/superpowers/specs/2026-08-16-foundation-spec.md on main (§4/§10); this
branch touches §5/§6 of that file at Tasks 16/21 — different paragraphs, clean
3-way merge expected at Task 21.
Human-presence needs flagged up front: Task 13 Step 1 (consent for the
~/kh-vault commit), Task 21 Step 3 (live suite — Zotero running, real
HARNESS_MAILTO).

Task 1: implementer DONE (commit 8dbf87f, suite 1548 passed / 7 skipped = baseline).
Task 1: review dispatched (3-lens workflow + adversarial verify) over 002cb25..8dbf87f.

Plan amendment (author, 2026-08-23): Part 3 / Task 22 — rename
`skipped_digest` -> `skipped_sha256` in knowledge_harness/factcheck.py, its
tests, skills/factcheck-draft/SKILL.md, and the regenerated sidecar manifest.
Ruling + six steps drafted at
.superpowers/sdd/2026-08-22-post-q-batch/task-22-amendment.md; it is appended
to the plan file and committed as its own `docs:` commit AFTER Task 1's
completion line is written, so no controller edit can be swept into an
implementer's fix commit or pollute a scoped re-review range.
Execution order amended: ... 19, 20, 22, 21 (Task 21 merges and pushes, so
Task 22 must precede it to ride its acceptance).
NOTE: origin/main's copy of the plan lacks Task 22 until the merge — the
"read this plan from origin/main" global constraint is stale for Task 22.
Briefs are generated from the worktree copy, which is already the practice.
CORRECTED 2026-08-24 (independent SHA-walk): that sentence stopped being true at
Task 2b. From 2b onward, briefs for tasks the author added after this branch was
cut were extracted from ORIGIN/MAIN's plan copy (via `git show origin/main:...`
into /tmp, then `task-brief` with an explicit OUTFILE), because the branch's copy
did not contain those tasks at all. Tasks 2b, 2c, 2d and Task 22 were all
sourced that way. After the boundary merge at 3a6d0cd the branch copy is
authoritative again, so Task 14 onward is generated from it normally.
Verified while drafting: mutation-baseline.txt carries no `func/skipped_digest`
key (only _bucket, contested_adjacent_links, eligible_claims, select_claims,
module for factcheck.py) — the ruling's claim holds.

Task 1: review clean — spec compliant, quality Approved, 0 Critical/Important.
  Review file: .superpowers/sdd/2026-08-22-post-q-batch/task-1-review.md
  Cannot-verify #1 resolved by controller: re-ran the offline suite at 8dbf87f
    — 1548 passed, 7 skipped (= baseline); tests/test_project_flow_skill.py 10 passed.
  Cannot-verify #2 resolved from plan text: Task 21 Step 3 already mandates the
    live run (HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO, Zotero running).
    No plan edit owed; the wave-level obligation stands and is already scheduled.
Task 1: minor (deferred): test functions in tests/test_project_flow_skill.py keep
  the test_project_ prefix (10 defs from line 23) while file, directory and
  frontmatter say project-flow — node IDs re-create the class-4 collision the
  rename dissolves; sibling test_import_source_skill.py prefixes with the skill name.
Task 1: minor (deferred): no test pins the INBOUND routing references to the
  renamed skill (skills/find-sources/SKILL.md:104 and :17,
  skills/import-source/SKILL.md:173); a missed inbound row would still have left
  the suite green.
Task 1: minor (deferred): stale `project` skill references survive in
  docs/product-landscape/2026-08-22-adoption-plan.md:585, a SELF-DECLARED LIVING
  document — the write-once-records exemption does not cover it.
Task 1: complete (commits 002cb25..8dbf87f, review clean, 3 minors deferred)

Plan amendment APPLIED and committed: aef25c1 `docs: add Part 3 / Task 22 to the
pre-slice batch plan`. Verified after the edit: task-brief now extracts Task 21
cleanly (21 lines) and Task 22 at 57 lines (it trails the file's NOT-in-this-plan
and Self-Review sections, which is harmless context).
Task 2: BASE = aef25c1. Implementer dispatched (sonnet). Pointed at the C-7 card
(docs/2026-08-22-skills-layer-audit.md:261) and its adjudication (:340) as the
governing source for the seven entry names, NOT arithmetic over skills/; and at
the whole-file pin tests/test_templates.py:96.
Task 2: implementer DONE (commit 45aa45d, 2 files +24 lines; suite 1548/7 = baseline,
  8/8 pre-commit hooks). Implementer reports the C-7 card and ENTRY_SKILLS agreed
  exactly on the seven names, so no arbitration was needed — review is told to
  verify that agreement rather than accept it.
Task 2: review dispatched over aef25c1..45aa45d.
Task 2: review clean — spec compliant, quality Approved, 0 Critical/Important.
  Review file: .superpowers/sdd/2026-08-22-post-q-batch/task-2-review.md
  Cannot-verify #1 resolved by controller: offline suite re-run at 45aa45d —
    1548 passed, 7 skipped (= baseline), tree clean.
  Cannot-verify #2 resolved by controller: re-ran the form gate under the
    WORKTREE venv (PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run
    --all-files) — 8/8 hooks Passed, no files modified. This closes the second
    Minor finding rather than deferring it.
  Cannot-verify #3 needed no action (the synthesizer read the commit body itself).
Task 2: minor (deferred): nothing binds ENTRY_SKILLS to the vault AGENTS.md index
  in the reverse direction, so an eighth entry skill would go missing from the
  template silently; the `publish` row is additionally invisible to
  _BACKTICKED_KEBAB_TOKEN, which requires a hyphen. Reviewer marked it
  plan-mandated (option (a) is the shape the human ruled).
Task 2: complete (commits aef25c1..45aa45d, review clean, 1 minor deferred)

TOOLING FACT learned at Task 2, now carried in every dispatch: the sandbox
refuses `source .venv/bin/activate`. Implementers must use `.venv/bin/python -m
pytest` and `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files`.
Without the PATH prefix the `language: system` hooks resolve tools through the
ambient PATH, which points at the MAIN checkout's venv (/home/eranr/New
folder/.venv), not the worktree's.

Task 3: BASE = 45aa45d. Implementer dispatched (opus — the enumeration checker is
instrument design, not transcription). Four ambiguities resolved in the dispatch:
  (a) Step 2's sentence lives in skills/evidence-conventions/SKILL.md:89, NOT in
      verify-citations as the brief's Files line says — the brief defers to the
      C-2 card and the card names that file. Line drifted from :86 to :89.
  (b) Step 1 uses the brief's defer-to-CLI sentence, overriding both options the
      C-1 card offers.
  (c) Step 2's "pin with a test" is an ADD — no pin exists for that sentence today.
  (d) the emitted check-id set is BIGGER than inbox.CHECK_IDS (terminology.md:46-50
      names staleness, append-only, claim-immutability, published-drift,
      publish-gate); a checker built on CHECK_IDS alone is the wrong instrument.
Task 3: implementer DONE_WITH_CONCERNS (commit 12f29fe; suite 1560 passed / 7
  skipped — baseline 1548/7 plus 12 new tests; form gate 8/8). Flagged two
  deliberate deviations from the verbatim-copy constraint.
Task 3: PLAN CONFLICT escalated to the author and RULED. The C-2 card's repair
  sentence claims `manual` "belongs to a surface not shipped yet"; false at HEAD
  (hooks/stop_publish_gate.py ships, is wired in hooks.json, and writes
  `manual — publish-gate bypass: …` into the review queue via
  inbox.append_entry — I verified this before escalating).
  RULING (author, 2026-08-23): give `manual` its own row in the reason-code
  table; delete the "not shipped yet" sentence entirely, its trigger having
  fired ("gets its own glossary row when that surface lands" — the surface
  landed); closing sentence names only `matched`; sweep for the same stale claim
  elsewhere in the same commit.
  DOCTRINE RECORDED for the rest of this plan: verbatim governs decided
  substance; the tree governs facts. When a card's factual claim is falsified at
  HEAD, copying it verbatim would fabricate, and the no-fabrication doctrine
  outranks a copy instruction. Deviations go in the commit body.
Task 3: fix round 1/5 dispatched (resumed the original implementer with the
  ruling). NOTE: this round was triggered by the author's ruling, not by review
  findings — the review had not yet returned.
Task 3: review run wf_41e60ae8-2f8 FAILED — the synthesis agent exceeded the
  StructuredOutput retry cap after 15 of 16 agents had completed. Root cause:
  the synthesizer was handed the full lens JSON inline AND a deep return schema
  on top of writing the report file. Script hardened before re-run: payload
  compacted, return schema slimmed (why/howToFix now live only in the report
  file), and the synth call wrapped so a synthesis failure returns the raw
  verified findings instead of discarding the whole run. Review re-runs over the
  full range 45aa45d..<fix HEAD> once the fix round lands.

BRANCH RECONCILIATION required (author message, 2026-08-23). origin/main has
moved by three commits my branch does not have: 1db33d2 (AGENTS.md trim),
3cfb79b, 9749a05. The plan on origin/main now carries the AUTHOR's own
Part 3 / Task 22 AND a new Part 4 / Tasks 23-25 (mutmut adoption).
  => My aef25c1 (`docs: add Part 3 / Task 22`) is SUPERSEDED. I authored Task 22
     from the ruling text before the author committed their own version; two
     independent Part 3 sections must not both land. The author's text governs.
     Reconciliation: merge origin/main, keep origin/main's Part 3 + Part 4
     verbatim, drop MY Part 3 section and MY Self-Review bullet.
  => .superpowers/.../task-22-amendment.md is superseded; kept only as a record
     of what I drafted. Task 22's brief MUST be regenerated after the merge.
  SUBSTANTIVE DIFFERENCES in the author's Task 22 (mine would have misdirected
  the implementer):
    - Motivation REVISED: not a collision fix. The authored per-source account
      is now named `summary` (docs/2026-08-23-proposed-adrs.md §8), so nothing
      collides and nothing downstream waits. It is a precision fix only.
    - DROP-ON-FRICTION: "If the implementer hits any friction in Step 4, drop
      the task rather than spend the instrument-freeze window on it." My version
      had no such escape and would have burned the window.
    - Scope is NARROWER than mine: "renames one function, one dict key, and
      their references". My judged-grep step would have renamed
      tests/test_finding_cli.py's `digest-aaaa`/`digest-bbbb` fixtures and its
      docstring — OUT of scope under the author's text.
    - Sidecar regenerates through scripts/mutation_gate.py's own path, not the
      raw `python -m mutate4py` invocation I wrote.
    - Adds factcheck.py:39 (claim_text_hash's docstring) explicitly.
    - Commit subject differs: `refactor: rename skipped_digest to
      skipped_sha256 (one sense per term)`.
    - Ordering: "Run it anywhere in the batch" (mine forced it before Task 21).
  PART 4 IS OUT OF THIS BRANCH'S SCOPE: Tasks 23-25 run on main AFTER Task 21's
  merge, explicitly non-gating. This branch covers Tasks 1-22.
  MERGE HELD until Task 3's review run (wf_fbda4bc1-4fd) returns, so the tree
  does not move under the running reviewers.
  Author's bookkeeping note acknowledged: 3cfb79b's subject mislabels its
  content as "Part 3 mutmut" when it carries Task 22; 9749a05 says so in its own
  subject. Nothing to do — history is never rewritten (ADR 0002), and the
  correction already lives in the later commit's message.

NAMING RULING absorbed (author, 2026-08-23; committed at origin/main 59037cd,
plan Part 3 lines 465-483, above Task 22). The authored per-source account is a
`summary`. Binding on any implementer who touches that artifact; creates no work
in this plan — the churn list is owed by the FUTURE step that authors the
artifact (Plan D polish item 10, gated on the deferred /fulltext leg), not by
any task 1-22.
  Declines recorded so they are not re-proposed: digest (superseded same day),
  synopsis, précis, annotation, and bare `summary` for anything else
  vault-facing. Section heading is `## Summary`. Glossary entry deliberately
  does NOT land now; draft held at docs/2026-08-23-proposed-adrs.md §7(e).
  ONE operational consequence for THIS run: Task 9 modifies
  `knowledge_harness/inbox.py`'s `summary()`. The ruling classes `inbox.summary()`
  and `okf.py:1` as dev-facing (T7), never reaching vault prose — "rename or
  leave, implementer's discretion, not a blocker". Task 9's dispatch AND its
  review constraints must both carry this, so neither the implementer renames it
  thinking the ruling demands it, nor a reviewer flags the non-rename as a gap.
  Also never-rename, carried into any task touching find-sources:
  skills/find-sources/scripts/arxiv_atom.py:93 keeps its <summary> -> abstract
  translation exactly (ADR-level, slice finding 16).

origin/main is now SEVEN commits ahead of this branch's base: 1db33d2, 3cfb79b,
9749a05, 81cb762, b287d80, 59037cd, 176de94 — all documentation. 81cb762 is the
author's two-way-Zotero-sync spec re-ruling, the uncommitted change flagged at
pre-flight; it is committed as agreed, and it touches spec §4/§10 while Tasks
16/21 touch §5/§6, so the clean 3-way merge predicted at pre-flight still holds.

MERGE ANALYSIS (dry, via `git merge-tree --write-tree`; working tree untouched):
  Exactly ONE conflicted file: docs/superpowers/plans/2026-08-22-post-q-batch.md.
  docs/terminology.md auto-merges cleanly — origin/main touched line ~148 (the
  venue-sense wording) while Task 1 touched §4.3's skills row; different lines.
  Resolution is unambiguous: `aef25c1` is my ONLY commit touching the plan file,
  so take origin/main's plan file WHOLESALE (`git checkout origin/main -- <plan>`),
  which drops my Part 3 and my Self-Review bullet in one move.
  Reviewed every origin/main hunk against tasks already run or still to run:
    - Task 1's hunk is prose-only (the ruling's rationale now cites terminology
      §4.3 and records that CONTEXT.md's entry was cut 2026-08-23) plus two
      mdformat escaping fixes in Steps 2 and 4. NO implementation change —
      Task 1's landed work stands, no rework.
    - Tasks 14-21 hunks are mdformat blank-line normalization after "**Files:**".
      No requirement changed anywhere in Tasks 1-21.
    - The Self-Review bullet gains the Task 22 / Part 4 provenance note,
      including the author's own record of 3cfb79b's mislabel.
  Merge executes once Task 3's review returns; the tree stays still until then.

AUTHOR INSTRUCTION (2026-08-23): do NOT merge mid-plan. The origin/main merge
happens only when every task is done. Supersedes my earlier "merge once Task 3's
review returns".
  Consequences, all handled without merging:
  - `aef25c1` (my superseded Part 3 / Task 22) gets REVERTED on this branch once
    Task 3's review returns — subtractive only, pulls nothing from origin/main.
    Two contradicting Task 22 specs must not coexist in the tree, and the revert
    records in git history why the final merge resolves that file toward
    origin/main.
  - Task 22's brief is generated from `git show origin/main:docs/superpowers/
    plans/2026-08-22-post-q-batch.md` at run time, NOT from the branch copy.
  - The naming ruling (summary) binds implementers via this ledger and the
    dispatch prompts; it does not need to be in the branch's plan file to hold.
  - Part 4 (Tasks 23-25) remains out of scope for this branch by the author's own
    placement: it runs on main AFTER Task 21's merge.
  - The merge analysis above still stands and still applies at the end.

`aef25c1` REVERTED at 4a690cc (controller bookkeeping, not task work). Branch's
plan file no longer carries any Part 3; Task 22's brief comes from origin/main.

Task 3: review returned — spec ISSUES, quality NEEDS FIXES. Review file:
  .superpowers/sdd/2026-08-22-post-q-batch/task-3-review.md
  Cannot-verify #1 closed by controller: form gate on d44452e, 8/8 Passed, no
    files modified, tree clean.
  Cannot-verify #2 closed by controller: the reviewer asked whether the 2026-08-23
    `manual`-row ruling was actually issued as the commit body records. It was —
    the author issued it in this session and I relayed it verbatim.
Task 3: fix round 2/5 dispatched (round 1 was the author's ruling, not a review
  finding). Two open findings, coupled by the reviewer's own instruction:
  - Important CONFIRMED, tests/test_skill_contracts.py:184 — the sweep's "check
    id" phrase anchor reads only 4 of 46 backticked check-id mentions and
    extracts from ZERO of the five multi-id enumerations shipped today
    (import-source:46, publish:31, publish:37 x2, verify-citations:31). Numbers
    measured by the reviewer running the shipped functions over the real corpus.
    Step 3's mandated invariant does not ship while the test name, docstring,
    commit subject and report all claim it does. Suggested fix (probed: fires on
    exactly those five, zero false positives at HEAD): a co-occurrence anchor.
  - Minor CONFIRMED, :189 — _RUN_JOINER treats `|` as list punctuation, merging
    adjacent table cells into one run. Latent today, load-bearing once the
    anchor lands; the reviewer requires it fixed in the same change.
  FIX_BASE for the scoped re-review will be 4a690cc, not d44452e, so the
  unrelated revert commit stays out of the fix diff.
Task 3: minor (deferred): tests/test_skill_contracts.py:389 — `_COUNT_WORDS[len(exempt)]`
  raises an opaque KeyError instead of asserting for 0 or >5 exempt codes, and
  the leg pins the sentence's phrasing rather than its contract.
Task 3: minor (deferred): tests/test_skill_contracts.py:225 — the AST scan reads
  only positional first args and only ast.Assign module constants, so a future
  `Outcome(check="new-id", ...)` or annotated constant silently drops an id.
  Both blind spots verified latent at HEAD.
Task 3: minor (deferred): tests/test_skill_contracts.py:369 — the C-2 pin's
  docstring claims moving `manual` off the table fails the equality; it does not.
  The pin proves accounting, not placement. Concession lives only in the report
  while the docstring says the opposite.
Task 3: minor (deferred): tests/test_skill_contracts.py:339 — module docstring
  promises nothing is scoped to a particular skill, but the new reason-code pin
  hard-codes skills/evidence-conventions/SKILL.md.
Task 3: minor (deferred): skills/evidence-conventions/SKILL.md:88 — the `manual`
  row's closing clause "the only code in this table a person writes" is
  unmandated, unpinned prose; inbox.py:381-384 makes every ack a human-actored
  entry carrying some registry code. Reviewer corrected this DOWN from Important
  after verification refuted the actor half of the claim.
Task 3: REFUTED and dropped (recorded, not silently discarded):
  skills/verify-citations/SKILL.md:31 — the charge that a hand-maintained
  enumeration survived in the de-enumerated file. Also refuted: that switching
  to finditer would yield new ids (it yields zero at HEAD), and that
  publish/SKILL.md:37 is unpinned (tests/test_publish.py:806-856 pins it).
Task 3: fix round 2/5 landed — commit de1867d `fix: check-id sweep anchors on
  co-occurrence, not only on the phrase`. Implementer measured before/after over
  the real corpus: 4 tokens / 0 enumerations -> 20 tokens / all five
  (import-source:46, publish:31, publish:37 x2, verify-citations:31), zero false
  positives; co-occurrence threshold 2 because `quote` and `disputed-claim`
  collide with other vocabularies. `|` dropped from _RUN_JOINER in the same
  commit. Suite 1560/7 (no delta — one unit test replaced by one). Residual
  bound now stated in test name, both docstrings, commit body and report: a run
  with neither the phrase nor two surviving valid ids is not read, so a
  WHOLESALE rename of an entire enumeration slips past; partial drift does not.
Task 3: scoped re-review dispatched over 4a690cc..de1867d (sonnet). FIX_BASE is
  4a690cc rather than the reviewed head d44452e, so the controller's unrelated
  revert stays out of the fix diff.

CONTROLLER DEFECT found and fixed: the form gate was at 7/8 after my revert.
  Cause: the plan file was ALREADY mdformat-dirty at the merge base 002cb25 —
  proved by extracting the base blob and running mdformat against it directly.
  aef25c1 had silently included the whole-file normalization and masked it; the
  revert unmasked it. Normalized at a3db464; gate back to 8/8.
  HONESTY CORRECTION: my first version of that commit message claimed no
  non-whitespace line changed. False — mdformat escaped inside two inline code
  spans in Task 1's Steps 2 and 4 (an added backslash before a closing backtick,
  and `*.md` -> `\*.md`), exactly the mangling the implementer had warned about.
  The check behind my claim counted diff headers and missed them. Message
  amended to state the two mangled lines explicitly and why they are accepted:
  origin/main's copy already carries the identical artifacts from the author's
  own mdformat run, so this is where the file lands at the merge either way, and
  Task 1 is complete so nobody will re-run those two greps.
Task 3: fix round 2/5 re-review (2 addressed, 1 NEW open — commits 4a690cc..de1867d).
  Both original findings ADDRESSED, reproduced independently by the re-reviewer:
  it executed the shipped extractor over skills/*/SKILL.md (20 tokens, all five
  enumerations, zero false positives) and confirmed the _RUN_JOINER fix by
  patching `|` back in and watching the false positive return.
  NEW Important breakage introduced BY the fix diff — same defect class the task
  exists to eliminate, a claim exceeding the instrument: the residual-bound gloss
  ("a wholesale rename of every member would slip past; partial drift does not")
  is FALSE, falsified by a SHIPPED enumeration. skills/publish/SKILL.md:37 has a
  two-member run (`citekey`, `evidence-layer`) sitting BEFORE that line's
  "check id" phrase, so co-occurrence is the only thing reading it. Renaming
  EITHER single member drops surviving-valid to 1, below the threshold of 2, and
  the whole run — drifted token included — goes invisible. That is single-id
  partial drift slipping past today. The gloss was propagated identically to two
  docstrings, the commit body and the report.
Task 3: fix round 3/5 dispatched. Code stays (threshold 1 was already shown to
  false-positive on `quote`/`disputed-claim`); the CLAIMS change, in all four
  places. de1867d's body is corrected FORWARD by a new commit rather than
  rebased, since a3db464 sits on top of it.
Task 3: fix round 3/5 landed — commit 2150da9 `docs: correct the co-occurrence
  anchor's bound; pin it by test`. Forward correction on top of a3db464;
  de1867d NOT rewritten, and 2150da9's body quotes the false sentence explicitly.
  Implementer re-derived the bound from the return condition rather than
  restating its own prose: a run is read only if the prose introduces it OR at
  least two members are still valid ids — `named` counts SURVIVORS, not renames.
  Accurate bound: a phrase-less run goes dark once fewer than two members
  survive, so publish:37's two-member run is lost to a SINGLE rename.
  Went beyond the ask: the bound is now EXECUTABLE —
  test_the_documented_bound_on_the_co_occurrence_anchor_holds pins the
  publish:37 pair under each single rename, the survivor-count behaviour of a
  longer run, and the threshold itself (dropping _CO_OCCURRENCE_ANCHOR to 1
  breaks it). Both rejected alternatives recorded with counter-evidence.
  Suite 1561/7 (+1 = the bound pin); form gate 8/8.
  Standing concern from the implementer, for the final review: the hole is real
  and larger than first described; closing it needs a DIFFERENT ANCHOR, not a
  different threshold, and no attempt was made.
Task 3: round 3 scoped re-review dispatched over a3db464..2150da9 (FIX_BASE is
  a3db464, not de1867d, so the controller's mdformat chore stays out of the diff).
Task 3: fix round 3/5 re-review — ALL ADDRESSED, no new breakage (a3db464..2150da9).
  Re-reviewer derived the return condition from source independently before
  reading the implementer's prose and got the same rule; verified the new pin
  EMPIRICALLY by monkeypatching _CO_OCCURRENCE_ANCHOR to 1 in memory and
  confirming the pinned legs then return non-empty (so the pin discriminates in
  both directions); and reproduced both rejected alternatives' counter-evidence
  (threshold 1 flags evidence-conventions:22's paraphrase/inference/open-question;
  a line-scoped phrase anchor flags mark-published/mark-corrected on publish:37).
  Confirmed all four surfaces carry the corrected bound. Noted that the old false
  sentence survives verbatim in de1867d's body, in round-2's report section, in
  this ledger and in a prior diff artifact — all historical record under the
  forward-correction discipline, not live claims. Test name kept, judged accurate.
Task 3: complete (commits 45aa45d..2150da9, review clean after 3 fix rounds,
  6 minors deferred). Suite 1561 passed / 7 skipped; form gate 8/8.
  NOTE the branch range for Task 3 includes two controller commits that are not
  task work: 4a690cc (revert of the superseded Part 3) and a3db464 (mdformat).
Task 4: BASE = 2150da9. Implementer dispatched (opus — four audit items folded
  into one skill surface, with verbatim-copy fidelity at stake).

CONTENT-SOURCE RELOCATION (author, 2026-08-23; on origin/main only, NOT on this
branch since we do not merge mid-plan). Locate by filename:
  docs/2026-08-22-skills-layer-audit.md    -> research/validation-slice/2026-08-22-skills-layer-audit.md
  docs/2026-08-22-references-cross-read.md -> research/validation-slice/2026-08-22-references-cross-read.md
  docs/2026-08-22-no-fabrication-audit.md  -> research/validation-slice/2026-08-22-no-fabrication-audit.md
  docs/2026-08-22-slice-findings.md        -> research/validation-slice/2026-08-22-slice-findings.md
  (also research/rethink-audits/ for the 2026-08-16/20/21 rethink documents;
   docs/ now retains only proposed-adrs, environment, terminology, testing.)
  NOT MOVED, verified: docs/superpowers/specs/2026-08-16-foundation-spec.md and
  docs/superpowers/plans/* — so Tasks 13, 16 and 21 are unaffected.
  RULE for every remaining dispatch: READ from the old docs/ paths (that is where
  the files are on this branch), CITE the new research/validation-slice/ paths in
  anything that ships — skill prose, vendoring notes, commit bodies, reports.
  After the merge the docs/ copies are gone, so a shipped docs/ citation lands
  dead. Verified no test validates cited document paths, so citing a
  not-yet-present path breaks nothing on-branch.
  Task 4's implementer was corrected mid-flight with exactly this.
  Merge note: origin/main renames these files while this branch leaves them
  untouched, so rename detection should carry them across without conflict.
  Also: their new home under research/ makes them standing-as-written record
  (AGENTS.md) — annotate our own prose, never edit the audit documents.
Task 4: implementer DONE (commit 800c492; skills/find-sources/SKILL.md +
  tests/test_find_sources_vendor.py only; references/ and scripts/ untouched).
  Suite 1562/7 (+1 new pin); form gate 8/8.
  Verified rather than trusted, as instructed: REDACTED_PARAMS is 6
  (api_key, apikey, key, email, mailto, tool — _common.py:201) and 3 APIs
  document a query-string api_key (CORE, NCBI E-utilities, OpenAlex), plus
  Unpaywall's mandatory email. Both brief numbers hold; NEITHER ships — the
  prose says "several" and defers to redact_url, so the count cannot rot.
  DEVIATION under the standing doctrine, recorded in the commit body: six
  cross-read line references are stale at HEAD, and the annotations ship
  verified numbers instead — biorxiv 113->115, 170->172, 161-163->163-164,
  154-159->156-160; medrxiv 133->135; openalex 160-168->162-172.
  PRECEDENCE JUDGMENT to check: references/ left untouched because the triage's
  "one vendoring-note section" is the decided set and overrides individual
  findings phrased as "annotate biorxiv.md".
  Path correction applied: shipped citations use research/validation-slice/...
  Controller verified arxiv_atom.py:93 still translates <summary> -> abstract.
  Implementer's own standing concerns, carried for the final review: the
  category-separator annotation ships UNVERIFIED BY DESIGN (triage defers it to
  a live two-curl probe at slice time); both class-3 guards are prose, not
  mechanism; line refs into frozen vendored files need re-verifying at the next
  re-vendor and no test enforces it.
Task 4: review dispatched over 2150da9..800c492.

TASK 24b added (author, 2026-08-23; origin/main 62d8360) — comment-hygiene sweep
over knowledge_harness/*.py, scripts/*.py, tests/*.py. Comments and docstrings
only, zero behavior changes. Detect by grepping for `2026-`, `ruled`,
`Plan [A-Z]\b`, `Task [0-9]`, `previously`, `postmortem`, `superseded`,
`renamed from`; judge each hit against the doctrine that a comment states a
constraint the code cannot show, while provenance, history and correctness
arguments belong to git log. Vendored copyright/license/pinned-commit headers
stay. Judged keep-list in the commit body. Suite green IS the behavior guard —
any failure means the sweep touched behavior, so revert that hunk.
  SCOPE: Part 4, sequenced between Tasks 24 and 25, so it runs on main AFTER
  Task 21's merge. NOT this branch's work — same as Tasks 23-25.
  Sequencing rationale recorded: docstrings live in the AST, so sweeping after
  the baseline would invalidate it; this way the blanket hashes the cleaned tree
  once. Same shape as ruff-before-baseline in Plan Q.
  FORWARD CONSEQUENCE FOR THIS BRANCH, acted on rather than just noted: tests/
  is inside 24b's file scope, and this branch is actively ADDING the exact
  language 24b sweeps — Task 3's test docstrings cite C-2 and dated rulings,
  Task 4 ships vendoring-note provenance. From Task 5 onward, dispatches carry:
  write comments that state a CONSTRAINT; put provenance, dates, ruling
  citations and correctness arguments in the COMMIT BODY, not in the code.
  That is already this plan's habit for commit bodies, so it costs nothing and
  leaves 24b less to undo.
  NOT retro-editing Tasks 1-4's comments — 24b owns that judgment, and
  pre-empting it would be me grading work the author assigned to that task.
  Note for whoever runs 24b: Task 3's docstrings stating the co-occurrence
  anchor's BOUND are constraints the code cannot show and are additionally
  pinned by an executable test — they read like ruling prose but are
  load-bearing. The C-2 and date citations around them are the sweepable part.
Task 4: review returned — spec COMPLIANT, quality NEEDS FIXES. Review file:
  .superpowers/sdd/2026-08-22-post-q-batch/task-4-review.md
  Reviewer independently re-sampled the re-derived line refs (biorxiv
  12/40/115/156-160/163-164/172, medrxiv 12/53/135, europepmc 16-17, openalex
  162-172) — all land on the quoted text. Both guards' claims verified against
  CODE, not just the source doc (paginate.py:86 raises the un-redacted
  `HTTP {code} from {url}` while :345/:444 redact; DEFAULT_MAX_CALLS 50 at :52;
  APIS holds exactly five walkers at :264-302). references/-untouched precedence
  call judged CORRECT.
  Cannot-verify #3 closed by controller: suite re-run at 800c492 — 1562 passed,
    7 skipped, unchanged.
  Cannot-verify #1 and #2 are the triage's own deferred state, not omissions:
    the category-separator convention and the OpenAlex 403 half of the stderr
    guard both need the SLICE-TIME live probe. Tracked here so they do not
    stand as permanent hedges — fold the answers back into
    skills/find-sources/SKILL.md:16 and :27 when the probe runs.
  Cannot-verify #4 is a MERGE-TIME check: confirm
    research/validation-slice/2026-08-22-{references-cross-read,skills-layer-audit}.md
    exist at exactly those paths once origin/main merges.
Task 4: fix round 1/5 dispatched — Important CONFIRMED, record-only, shipped
  prose needs no change. The deviation ledger declares SIX line-number
  corrections but seven shipped; biorxiv.md 140-144 -> 142-145 is undeclared,
  and task-4-report.md:57 affirmatively files that range under "Correct as
  cited" — a citation the cross-read never made. Kept at Important over one
  lens's Minor because a commit body is immutable after merge and the entry is
  a false verification claim in a no-fabrication repo. 800c492 is the branch
  tip, so `git commit --amend` is clean. Implementer told to REBUILD the ledger
  from a fresh pass rather than add one row, having got the count wrong once.
  The shipped 142-145 is substantively BETTER than the cross-read's 140-144 —
  the paragraph runs 142-146.
Task 4: fix round 1/5 landed — 800c492 AMENDED into 8e7b136. Controller verified
  the tree is BYTE-IDENTICAL between the two (`git diff --stat 800c492 8e7b136`
  empty) and the working tree clean, so the fix is entirely commit body + report.
  Ledger RE-DERIVED rather than patched: the implementer enumerated all file:line
  tokens in the shipped section by grep (14), enumerated the cross-read's own
  citations by grep, and matched row by row — 7 changed, 7 unchanged, 14
  accounted for. The false "correct as cited" entry is gone.
  NEW claim volunteered during the fix: references/pubmed.md ships with no line
  where the source cites :10 — a DROPPED ref, not a changed one.
  SECOND-ORDER PASS, unprompted: the miscount made the implementer distrust its
  other restated citations, so it verified the nine it had taken from the C-3
  card or cross-read without checking (core.md:23, pubmed.md:21, openalex.md:21,
  unpaywall.md:20, crossref.md:20, _common.py:205-220, webapi.py:38-43,
  paginate.py:52, pmc.md:237). All hold; no prose change needed.
  Implementer's own added concern, worth carrying to the final review: three
  record slips now, ALL in facts it RESTATED from a source document rather than
  derived — so treat any "verified as cited" line in its reports as
  spot-checkable, not settled. That is a useful self-diagnosis of a failure mode,
  not an excuse; the re-review is told to re-derive rather than check arithmetic.
Task 4: fix round 1 re-review dispatched. NOTE: no tree diff exists by design, so
  the re-reviewer reads the commit body, the report and the full task diff
  instead of a fix-diff package, and is instructed to re-derive the 7/7/14 split
  independently rather than verify the implementer's own restatement.
Task 4: fix round 1 re-review — ALL ADDRESSED, no new problems. The re-reviewer
  RE-DERIVED the split independently rather than checking the implementer's
  arithmetic: 14 tokens in skills/find-sources/SKILL.md:13-27, matched against
  the cross-read's own citations = 7 changed / 7 unchanged, identical. Verified
  the false "Correct as cited" entry is gone from BOTH commit body and report;
  confirmed the volunteered pubmed.md dropped-ref claim; spot-checked 8 of the 9
  second-order items against the tree (all hold); and independently re-confirmed
  the tree is byte-identical between 800c492 and 8e7b136, so no prose or pin
  change hid under a "commit-message-only" fix.
Task 4: complete (commits 2150da9..8e7b136, review clean after 1 fix round,
  5 minors deferred). Suite 1562/7; form gate 8/8.
Task 4: minor (deferred): tests/test_find_sources_vendor.py:223 — the AST helper
  recognises only os.environ.get/os.getenv with a string-literal first arg, so
  os.environ["NAME"], a bare getenv after `from os import getenv`, or a
  non-literal key would be missed and the set-equality would still pass.
  Verified theoretical today: all three reads are literal os.environ.get.
Task 4: minor (deferred): skills/find-sources/SKILL.md:70 — Step 5 and guard 2
  both say to run a URL through redact_url, but scripts/_common.py is
  import-only (no __main__, no argparse), so the skill gives no way to execute
  the instruction it gives.
Task 4: SLICE-TIME items (not defects — the triage's own deferred state):
  fold the category-separator probe answer into skills/find-sources/SKILL.md:16,
  and the OpenAlex 403 confirmation into :27, when the live legs run.
Task 5: BASE = 8e7b136. Implementer dispatched (sonnet). Carried three things the
  brief omits but the C-6 card decides: (1) the card's State is "record, not a
  plain repair" and asks for a PROBE FIRST — add a template, run scaffold, see
  whether anything catches the divergence before the prose does; (2) the card
  supplies the deliverable sentence verbatim; (3) the card names exactly what is
  load-bearing — tests/test_skill_files.py:107-121 pins six paths against a real
  dishonesty, so the six stay and the other eight go.
Task 5: implementer DONE (commit 97afad5; skills/setup-vault/SKILL.md +
  tests/test_skill_files.py, 3 insertions / 3 deletions). Suite 1562/7 =
  baseline (no tests added — prose plus an existing pin); form gate 8/8.
  PROBE RUN as the C-6 card's State field requires: a scratch template plus the
  full suite produced FIVE code-layer failures catching the divergence while
  tests/test_skill_files.py — the SKILL.md prose pin — stayed SILENT. That is
  the card's question answered directly: the prose inventory was the stale-able
  duplicate, and the code layer already guards the fact. Scratch change reverted.
  Also corrected old-path citations in its report to research/validation-slice/.
Task 5: review dispatched over 8e7b136..97afad5. Reviewer told the real risk in
  a 3-line diff is not complexity but whether a one-line prose change quietly
  weakened an honesty pin that exists to prevent a specific lie — so it must
  confirm the six pinned paths are still asserted, that the pin still fails on a
  claimed-but-unprinted path, and that the pin edit was forced by the prose move
  rather than a weakening. Also told to re-derive the card's own factual claims
  (the file-by-file enumeration match; scaffold.py:241 `sorted(created)`), since
  card line numbers have rotted repeatedly in this plan.
Task 5: review clean — spec COMPLIANT, quality APPROVED, 0 Critical/Important.
  Review file: .superpowers/sdd/2026-08-22-post-q-batch/task-5-review.md
  Reviewer verified the card's decided sentence ships CHARACTER-FOR-CHARACTER
  from the card itself (SKILL.md:21 == audit :257), the six pinned paths are all
  still asserted with the docstring unchanged, a sibling pin's phrases survive
  verbatim, and BOTH of the card's factual citations re-derive true
  (scaffold.py:241 is `return sorted(created)`; templates/vault/ holds 13 files
  mapping 1:1 onto the old enumeration). It also confirmed no test, skill or doc
  still quotes the dropped enumeration.
  Cannot-verify #1 and #2 closed by controller at 97afad5: suite 1562 passed /
    7 skipped, form gate 8/8, tree clean.
  Cannot-verify #3 (the probe) REPRODUCED by controller rather than accepted —
    the implementer has a known slip pattern on restated-vs-derived facts, and
    the probe's conclusion is what justifies dropping the inventory. Added
    knowledge_harness/templates/vault/system/templates/zz-probe-scratch.md, ran
    the full suite: EXACTLY 5 failures — test_scaffold.py x4
    (creates_the_complete_okf_vault, commits_only_its_created_paths,
    cli_prints_the_created_paths, cli_requires_literal_rw_consent) and
    test_templates.py::test_all_canonical_template_paths_are_packaged — with
    tests/test_skill_files.py SILENT. Matches the implementer's report exactly.
    Scratch file removed; tree verified clean and the templates directory back
    to its four files.
  Cannot-verify #4 is the standing MERGE-TIME check (research/validation-slice/
    citations resolve once origin/main merges) — already tracked.
Task 5: minor (deferred): skills/setup-vault/SKILL.md:21 — the kept-six clause
  reads "Paths such as ...", which reopens a set the brief closed, and two of
  its entries (system/templates/, system/bases/) are directory prefixes scaffold
  never prints as created paths. The reviewer corrected one lens's mitigation:
  only the SUBSTRING pin pre-dates this change; standalone bare directories in a
  contract list are new in this diff. Held at Minor because the same sentence's
  "report that list verbatim" rule dominates in practice and
  tests/test_scaffold.py:21-38 EXPECTED_CREATED confirms scaffold emits only files.
Task 5: complete (commits 8e7b136..97afad5, review clean, 1 minor deferred)
Task 6: BASE = 97afad5. Implementer dispatched (sonnet). Two things resolved in
  the dispatch:
  (a) "find-sources' shape" = the POINTER TABLE's form only
      (skills/find-sources/SKILL.md:43-48, `| purpose | target | reference |`),
      NOT its vendoring discipline. find-sources' references/ are a vendored
      third-party fork with provenance headers and a never-hand-edit rule;
      import-source's will be OUR OWN prose moved out of our own file. Copying
      the vendoring semantics would assert a false origin for content we wrote.
  (b) CROSS-TASK HAZARD, measured not guessed: Task 3's check-id enumeration
      sweep and the shipped-`finding`-invocation scan both take their corpus
      from _skill_md_files(), which globs skills/*/SKILL.md ONLY and never reads
      references/. The sections being moved carry real check ids and reason
      codes in backticks — citekey, doi, staleness, web-archive,
      missing-archive, not-admitted, plus archive-url, verify, inbox,
      import-note. So this move may silently shrink the sweep's corpus: the
      exact "instrument claims coverage it does not have" class this plan has
      already fought twice. Implementer must take a BEFORE measurement (the
      extractor's output over import-source/SKILL.md), repeat it after, and
      report the delta with exact tokens. It must NOT silently accept a loss nor
      unilaterally redesign the sweep — the plan mandates the move; I route it.
      Controller pre-checked one half: §7-9 contains NO shipped `finding`
      invocations, so that scan loses nothing. The check-id sweep is open.
  Also carried: byte-preservation is a checkable claim (hash/diff the extracted
  bodies, state any heading adaptation); the two existing pins in
  tests/test_import_source_skill.py both read SKILL.md, so confirm neither
  asserts moving text and STOP if one does.
Task 6: implementer DONE (commit 8bc6294; SKILL.md 173 -> 123 lines, three new
  files under skills/import-source/references/ — refresh-mode.md, batch-mode.md,
  archive-at-import.md). Form gate 8/8.
  CROSS-TASK HAZARD RESOLVED, measured with the sweep's own extractor rather
  than guessed: the check-id sweep delta is EMPTY both before and after, so
  Task 3's instrument kept its full corpus and nothing left its reach.
  Suite 1565/7 vs baseline 1562/7. The +3 is attributed to a PRE-EXISTING
  parametrized instrument, test_markdown_table_rows_have_no_truncated_code_spans,
  which globs skills/**/*.md and auto-generates one case per new file — NOT three
  new hand-written tests. Review is told to verify that attribution.
  Implementer amended its own commit once before declaring done, to correct a
  false "three-column" claim in its body. Self-caught, and the table is genuinely
  three-column now (Need / Verb / Reference file).
  DISCLOSED CONCERN routed to review rather than silently fixed:
  references/batch-mode.md keeps the phrase "the same per-note contract as
  above", which used to point at the preceding section and now points at nothing.
  Left as bytes because editing it would violate byte-preservation, and the
  immediate colon-clause restates the substance inline. That is a real tension —
  byte-preservation versus a reference that no longer resolves — and the reviewer
  is asked to rule which should win and whether the same problem exists elsewhere
  in the three new files.
Task 6: review dispatched over 97afad5..8bc6294. Reviewer told to RE-RUN the
  before/after sweep measurement itself (an empty delta is a strong claim and
  cheap to check), verify byte-preservation against §7-9 at 97afad5, and confirm
  the new files carry NO vendoring language — asserting a false origin for prose
  we wrote would be a serious defect.
Task 6: review clean — spec COMPLIANT, quality APPROVED, 0 Critical/Important.
  Review file: .superpowers/sdd/2026-08-22-post-q-batch/task-6-review.md
  The cross-task hazard is genuinely closed: the reviewer independently re-ran
  the sweep's extractor at BASE and at HEAD and got byte-identical output, plus
  zero matches over the isolated §7-9 substring. Byte-preservation PROVED, not
  promised — three body sha256 values reproduced by two different methods, and
  crucially the check ran against the POST-GATE tree, which rules out a silent
  mdformat rewrite. No false provenance: the new files carry no vendoring
  header, no upstream commit, no never-hand-edit rule. The +3 test attribution
  verified statically (three new parametrizations of the pre-existing
  test_markdown_table_rows_have_no_truncated_code_spans, whose corpus globs
  skills/**/*.md).
  Cannot-verify #1 and #2 closed by controller at 8bc6294: suite 1565 passed /
    7 skipped, form gate 8/8, tree clean.
Task 6: minor (deferred): references/batch-mode.md:9 — "the same per-note
  contract as above" no longer resolves; the "above" was §7 and is now the
  sibling file refresh-mode.md. Marked plan-mandated: byte-preservation
  correctly forbade the one-word fix inside this task, and the orphan was
  disclosed rather than hidden.
Task 6: minor (deferred): skills/import-source/SKILL.md:96 — the freshly
  authored §7 lead-in carries no read-before-acting imperative, so the
  archive-at-import mandate now sits behind a pointer with nothing telling the
  reader to take it. Status CONTESTED. The reviewer lowered one lens's Important
  to Minor because the relocation itself is plan-mandated and the missing
  imperative sits outside the controller-pinned shape, but deliberately KEPT the
  CONTESTED status "so the record is not laundered" — good discipline, and the
  final review should see both sides.
Task 6: minor (deferred): skills/import-source/SKILL.md:100 — the three new
  pointers are unpinned; no test asserts the table's paths resolve. Not a
  regression: find-sources' eleven pointers are equally unpinned.
Task 6: complete (commits 97afad5..8bc6294, review clean, 3 minors deferred)

Task 7: BASE = 8bc6294. Implementer dispatched (sonnet). Controller pre-work,
  because a mechanical sweep here would do real damage:
  - LINE DRIFT: "not as a raw dump" is at skills/find-sources/SKILL.md:108, NOT
    the brief's :88 — Task 4 inserted a vendoring section above it.
    "not in raw run order" is at skills/verify-citations/SKILL.md:27 as stated.
  - TRAP 1, vendored files: skills/find-sources/references/*.md (ELEVEN files)
    each carry "Do not hand-edit this file; re-vendor from upstream to update
    it." That is the VENDORING rule, not the never-hand-write refrain, and those
    files are frozen. A naive sweep rewrites all eleven and breaks the
    frozen-fork discipline Task 4 just reinforced. Explicitly out of scope.
  - TRAP 2, pinned sites: tests/test_skill_files.py:36 ("Do not create
    directories or files by hand"), tests/test_project_flow_skill.py:149
    ("never prose written by hand"), and :140 ("the person consents; the CLI
    writes" — already the target token, so it is the model, not a candidate).
  - TRAP 3, a variant in a shipped TEMPLATE not a skill:
    tests/test_templates.py:100 pins "evidence notes exist only by projection,
    never by hand". The brief scopes to SKILL.md files, so leaving it is
    defensible, but the ruling must be stated, not silent.
  - MEANING PRESERVED is the hard part: skills/publish/SKILL.md:11's refrain
    carries an ENUMERATION of what may not be hand-written (a status, a
    `verified` event, a tag, an acknowledgment, a review-inbox entry). Collapsing
    the refrain must not delete the enumeration.
Task 7: implementer DONE_WITH_CONCERNS (commit eb54ab6; five SKILL.md files,
  7 insertions / 7 deletions). Suite 1565/7 = baseline exactly (pure prose
  sweep); form gate 8/8; the judged grep for both cut prohibitions returns
  nothing repo-wide.
  Controller verified before routing to review:
  - The audit ENUMERATES its five sites at docs/2026-08-22-skills-layer-audit.md:130
    — project:84, import-source:11, publish:11, verify-citations:9,
    find-sources:71 — and adjudicates at :362 "five spellings -> one inline token".
  - The audit's find-sources:71 maps to today's :91 (Task 4 inserted ~20 lines
    above), and :91 WAS correctly collapsed: "Never hand-write a line into
    search-log.md yourself" -> "The CLI writes every line into search-log.md".
    So the five named sites are the five that changed.
  - publish:11's ENUMERATION SURVIVED the collapse by moving into the subject:
    "Every mechanical act below — a status, a `verified` event, a tag, an
    acknowledgment, a review-inbox entry — is a CLI verb call...". Meaning
    preserved, which was the flagged risk.
  - Both prohibition cuts landed at the re-located lines.
  OPEN QUESTION routed to review rather than pre-decided: skills/find-sources/
  SKILL.md:74 is a SIXTH spelling ("appended through the CLI verb, never
  hand-written") in the SAME FILE, ~17 lines from a site that now reads "The CLI
  writes" — so the shipped file carries both spellings. The implementer left it
  because the audit enumerated five and this was not among them. Genuine tension:
  an enumeration is a decided set, but the audit's stated purpose at :130 is that
  ONE leading word carries the doctrine. Reviewer asked to rule and, if it should
  collapse, to label it plan-mandated — I will put it to the author rather than
  dispatch a fix contradicting the decided set.
  Implementer also noted its advisor calls failed (service overloaded), so it
  shipped without that second-opinion pass. Recorded, not held against it.
Task 7: review dispatched over 8bc6294..eb54ab6.
Task 7: review returned — spec COMPLIANT, quality NEEDS FIXES. Review file:
  .superpowers/sdd/2026-08-22-post-q-batch/task-7-review.md
  THE SIXTH-SPELLING QUESTION IS SETTLED — and my framing of it was wrong. I had
  routed it as a possible author call. The reviewer settled it EMPIRICALLY
  instead: `git show 82b23a9:skills/find-sources/SKILL.md` (the commit that added
  the audit) already carried BOTH clauses, at :54 and :71, and the audit cites
  :71. So the five-site set was decided WITH the sixth spelling already in the
  tree — not miscounted, not an oversight. No author call needed. Two lenses had
  filed it Important; both framings were refuted, and the fidelity lens's
  distinguishing claim (that :74 is the last surviving negation spelling) is
  false, since project-flow:84 and publish:11 ship the same trailing negation
  under the APPROVED collapse. Downgraded to Minor/CONTESTED, planMandated
  corrected to false.
  Cannot-verify closed by controller at eb54ab6: form gate 8/8, tree clean.
Task 7: fix round 1/5 dispatched. Two open findings:
  - Important CONFIRMED, task-7-report.md:201 — the Step 3 "judged grep" block
    prints "(no output — checked repo-wide)" for a command that exits 0 with
    THREE hits. I reproduced it: plan:78, audit:135, audit:159 — the last being
    the very Step 2 line the brief quotes, so it could never have been empty.
    Step 3's SUBSTANCE holds (skills/ is clean; all three hits are record
    documents that stand as written), so the defect is the false transcript in
    the durable record, not the sweep. THIRD finding of this exact class in this
    plan, all in facts RESTATED rather than derived — the pattern this
    implementer diagnosed about itself at the end of Task 4.
  - UPGRADED BY CONTROLLER from the reviewer's Minor: skills/project-flow/
    SKILL.md:84 is one of the FIVE SITES THE AUDIT ENUMERATED, and no collapse
    happened there — the edit is a punctuation join, 204 chars to 203, leaving
    "the CLI writes" AND "never prose written by hand" side by side. That is the
    duplication item 9 exists to remove, at a named site, so I am treating it as
    a missed requirement rather than a style nit and said so explicitly in the
    dispatch. The pin at tests/test_project_flow_skill.py:149 is not a reason to
    leave it — the plan's constraints allow moving the pin in the same commit.
    An argued refusal naming the specific loss is an acceptable answer.
  Also noted by the reviewer, recorded for the final review: the report's claim
  that the audit "praised project-flow as the closest to ideal" has NO SOURCE in
  the audit.
Task 7: fix round 1/5 landed — commit a2a5aad `fix: complete the leading-word
  collapse at project-flow:84` (2 files, 6 insertions / 2 deletions).
  project-flow:84 now reads "...the person consents; the CLI writes — every
  mechanical act in this skill (events, statuses, tags, holds, acknowledgments)
  is a CLI verb call." — the duplicate "never prose written by hand" is gone and
  the pin moved in the same commit. Report's judged-grep transcript corrected to
  real output with an explicit ruling. Suite 1565/7; form gate 8/8.
Task 7: fix round 1 re-review dispatched over eb54ab6..a2a5aad. Told to check a
  risk that is MINE as much as the implementer's: I asked for the collapse, and a
  collapse can DELETE a constraint rather than compress it. project-flow:84 no
  longer carries any explicit prohibition, resting the write-discipline entirely
  on inferring it from "the CLI writes" — whereas publish:11, collapsed under the
  same approval, KEPT a trailing "never by hand, not in a note, not in
  frontmatter, not anywhere". If project-flow now states LESS RULE than its
  peers, that is new breakage from my own fix instruction and must be reported as
  such. Also told to verify the pin was MOVED not WEAKENED — a pin asserting only
  `"the CLI writes" in text` would not discriminate, since that token appears
  elsewhere in the file.
Task 7: fix round 1 re-review — ALL ADDRESSED, no new breakage (eb54ab6..a2a5aad).
  Finding 1: the corrected transcript was re-run by the re-reviewer and matches
  line-for-line, and the required RULING is present too (skills/ clean; the three
  hits are record documents standing as written per AGENTS.md).
  Finding 2: collapse landed. MY "less rule" worry was CHECKED AGAINST THE CORPUS
  and does not hold: three of the four other named sites (import-source:13,
  verify-citations:9, find-sources:91) were ALREADY collapsed in round 1 to the
  same structure with NO negation trailer; only publish:11 keeps one, as a
  deliberate brief-flagged exception. project-flow's fixed line is structurally
  isomorphic to import-source's already-approved collapse, so it lands ON the
  majority pattern, not below it. My framing of publish as the baseline was wrong.
  Pin verified MOVED not weakened: it now asserts the full verbatim phrase
  "every mechanical act in this skill (events, statuses, tags, holds,
  acknowledgments) is a CLI verb call" alongside "the CLI writes", so it
  discriminates — a bare token check would not, since "the CLI writes" also
  appears in the Acknowledgments code-block sentence.
Task 7: complete (commits 8bc6294..a2a5aad, review clean after 1 fix round,
  3 minors deferred). Suite 1565/7; form gate 8/8.
Task 7: minor (deferred): skills/find-sources/SKILL.md:74 — a sixth spelling of
  the refrain survives ~17 lines above the collapsed :91, so the file states the
  doctrine twice. CONTESTED, planMandated FALSE: the audit's five-site set was
  drawn with this line already in the tree (proved via git show 82b23a9).
  Residual duplication is real and disclosed — an author call for a follow-up,
  not a spec miss.
Task 7: minor (deferred): publish:11 and import-source:13 stack three em dashes
  doing two different jobs. Style only; every enumerated noun and the
  location-scope clause survive.
Task 7: minor (deferred): the task-7 report claims the audit "praised
  project-flow as the closest to ideal" — NO SOURCE in the audit. Fourth
  restated-not-derived slip; recorded for the final review.

Task 8: BASE = a2a5aad. Implementer dispatched (opus — largest prose task,
  7-8 adoptions across 6 skill files). Controller pre-work:
  - THE DECIDED SET is the audit's :381 paragraph ("Small, doctrinally-consistent
    steals"). I enumerated it: exactly SEVEN adoptions, mapping onto the brief's
    list — routing guard (project-flow), compilation-value line
    (synthesis-conventions), partial-read honesty rule (import-source +
    factcheck-draft), "it validates declarations, not their truth"
    (factcheck-draft), the why-one-pass sentence (factcheck-draft), the
    disposition rationalization table (publish), setup-vault fails closed on
    ambiguous vault selection.
  - SEED ROWS for publish's table are named at :401 — "they said go ahead so the
    ack is covered" and "UNREACHABLE is basically fine", ported from
    finishing-a-development-branch.
  - BOUNDARY DRAWN EXPLICITLY: §7's numbered list 01-11 (~:408-:419) is the
    on-disk corpora addendum = the POST-SLICE POLISH PASS, which this plan's own
    "NOT in this plan" section defers. §7 item 11 is literally the skill-eval
    lane. Landing any of the eleven would be scope creep into a deferred set.
    ONLY the two seed rows come from §7.
  - ONE BRIEF ITEM HAS NO §6 SOURCE: "publish announces gate-armed at start" is
    not in the :381 paragraph. Implementer told to search the audit, use the
    decided phrasing if found, and otherwise AUTHOR it while stating plainly
    that it is plan-sourced not audit-sourced — never present authored prose as
    copied.
  - STEP 2 IS A REAL VERIFICATION, not a skippable no-op: confirm no §6 DEFERRED
    item landed (independence key on claims; machine intake gate; frontmatter
    metadata related_skills/envVars), naming each in the report.
  - Carried the four restated-not-derived slips as a warning: this task quotes
    the audit repeatedly, so quote it open, never from memory.
Task 8: implementer DONE_WITH_CONCERNS (commit c0d0854; 10 files, +95/-1 — six
  skill files plus four test files carrying five new pins). Suite 1570/7
  (baseline 1565/7, delta = exactly the five new pins); form gate 8/8.
  MY BOUNDARY QUESTION ANSWERED, and my framing corrected: adoption 8
  ("publish announces at start that the gate is armed") IS audit-sourced — it
  sits at :405 in a §7 subsection called "Batch enrichments (existing items, no
  new scope)" that I had missed, distinct from and above the deferred 01-11
  polish list. Controller verified :405 directly: it reads "publish announces at
  start that the gate is armed (one line — the most irreversible skill should
  say so)." No boundary breach, and nothing for the author to rule on.
  STEP 2 RAN and went WIDER than I specified: six §6 deferred items checked by
  name (plan-hash handshake, independence key on claims, machine intake gate,
  frontmatter metadata, freshness fields, repair-as-separate-operation gate) —
  I had named only three — plus a cross-check of §7's deferred items for the six
  files edited. None landed.
  TWO DISCLOSED CONCERNS routed to review rather than pre-decided:
  (1) Adoption 8 shipped as a RULING, not a transcription. The implementer says
      the gate is NOT armed at skill start (arm-publish arms it later), so the
      literal decided wording would assert a state false at HEAD; it shipped a
      flow-property reading ("runs through an armed gate") under the
      tree-governs-facts doctrine. Reviewer must VERIFY THE FACTUAL PREMISE
      first — if the gate IS armed at start the deviation is unjustified — and
      label the finding plan-mandated if the deviation is wrong, so it comes to
      the author rather than a fix dispatch.
  (2) The implementer pinned its RATIONALE for that ruling in a TEST DOCSTRING.
      That collides with the comment-hygiene doctrine now binding on new test
      code (a docstring states the constraint it enforces; correctness arguments
      belong in git log). Flagged to the reviewer explicitly.
  (3) Two adoptions ship UNPINNED — synthesis-conventions and factcheck-draft
      have no per-skill prose pin file in this repo, and creating two new ones
      was judged outside the brief. Reviewer asked whether that scope call is
      right and whether those two adoptions are therefore free to rot.
Task 8: review dispatched over a2a5aad..c0d0854.

Task 9 PRE-CHECK (controller, done while Task 8's review ran; read-only). The
plan says filter SKIPPED out of the COUNTING path. Located every surface:
  - knowledge_harness/inbox.py:701 `open_entries()` — builds the open list.
  - knowledge_harness/inbox.py:711 `summary()` — calls open_entries and returns
    {"unacknowledged": len(entries), "oldest": min(dates)}. BOTH keys need the
    filter; the plan's "oldest-age basis" is the `oldest` key here.
  - knowledge_harness/scaffold.py:293 `_inbox_probe()` — calls inbox.summary()
    and reads both keys, so it INHERITS the fix for free. No separate edit.
  - knowledge_harness/__main__.py:761 prints inbox.summary() (fixed by the same
    change); :763 uses open_entries() for the LISTING, which must keep showing
    SKIPPED entries — they stay RECORDED and visible per the plan.
  HAZARD, the reason this pre-check was worth doing: knowledge_harness/verify.py:850
  also calls `open_entries()`, but NOT to count — `_file_effects` builds an
  `open_keys` set over (check, target, target_kind, result, ...) for DEDUP and
  SUPPRESSION. If the SKIPPED filter is pushed down into `open_entries()` instead
  of staying in `summary()`, verify stops recognising existing SKIPPED findings
  as already-open and RE-FILES A DUPLICATE EVERY RUN — filling the queue with
  exactly the noise this task exists to reduce. The dispatch must forbid
  filtering inside open_entries().
  `Finding.result` is a plain `str` field (inbox.py:121), so the predicate
  compares strings, not enum members.
  Also carried into Task 9's dispatch AND its review constraints per the author's
  naming ruling: `inbox.summary()` is DEV-FACING (T7), "rename or leave,
  implementer's discretion, not a blocker" — so the implementer must not rename
  it thinking the summary ruling demands it, and no reviewer should flag the
  non-rename as a gap.
Task 8: review returned — spec ISSUES, quality NEEDS FIXES. Review file:
  .superpowers/sdd/2026-08-22-post-q-batch/task-8-review.md
  ADOPTION 8 RESOLVED IN THE IMPLEMENTER'S FAVOUR: the reviewer verified the
  factual premise against the tree — skills/publish/SKILL.md:61 confirms the gate
  is INERT at skill start — so the literal wording would have asserted a false
  state and the flow-property phrasing is right. Nothing plan-mandated, nothing
  for the author.
  All eight adoptions carry the audit's decided phrasings (checked against :381,
  :395, :401, :405). Step 2's deferred-item verification is real. The +5 delta is
  five genuine new test functions, no vacuous pin.
  Cannot-verify closed by controller at c0d0854: form gate 8/8, tree clean.
Task 8: fix round 1/5 dispatched. Two Important CONFIRMED:
  - tests/test_publish.py:795 (also :810, test_project_flow_skill.py:131,
    test_import_source_skill.py:41, test_skill_files.py:41) — all five new test
    docstrings open with audit provenance and the adoption-8 one argues its own
    correctness, against the comment-hygiene doctrine binding from Task 5 on.
    NOTE: one lens tried to REFUTE this by claiming the doctrine does not exist;
    the synthesizer OVERTURNED the refutation by locating the doctrine in THIS
    LEDGER (progress.md:411-429) and noting Task 3's docstrings are explicitly
    grandfathered there. The ledger did work I did not anticipate — it survived
    into a reviewer's reasoning and corrected a false refutation.
  - skills/factcheck-draft/SKILL.md:19/:42/:79 — three adoptions ship UNPINNED on
    a justification the tree FALSIFIES. The report and commit body claim no
    per-skill pin file exists; tests/test_finding_cli.py:409
    (test_factcheck_draft_skill_names_its_bounds_and_never_blocks) already reads
    FACTCHECK_DRAFT_SKILL and asserts a token tuple against it. Controller
    verified directly. Every token in that tuple occurs elsewhere in the file, so
    ALL THREE adopted paragraphs could be deleted today with the suite green.
    That is Step 3's "Pins" unmet and it is what flipped spec to issues. Fix is
    three appended tokens plus correcting the false claim (c0d0854 is the tip, so
    amend is clean).
  Coupled Minor folded into the same pass: tests/test_publish.py:798's docstring
  declares the line must not claim the gate is already armed, but all three
  asserts are POSITIVE presence checks — restoring the audit's literal wording
  keeps it green. Converting to `assert "the gate is armed" not in intro` fixes
  the hygiene finding AND makes the test enforce the ruling, in one move.
  synthesis-conventions stays unpinned (deferred Minor): no test reads that file,
  so pinning would need a new file — outside the brief's update discipline.
  PATTERN NAMED TO THE IMPLEMENTER: fifth finding in this plan of a claim the
  tree falsifies, all of them facts RESTATED from context rather than derived by
  looking. It checked whether a DEDICATED pin file existed; the question was
  whether ANY test reads the file.
Task 8: fix round 1/5 landed — c0d0854 AMENDED into e76805c (still one commit;
  the fix delta is 5 test files, +38/-20; skills/ untouched). Suite 1570/7
  unchanged (the three tokens went into an EXISTING test function, so no new
  test); form gate 8/8; tree clean.
  Finding 2 fixed and the false claim corrected in BOTH report and commit body.
  The implementer confirmed against the tree before fixing:
  test_finding_cli.py:17 defines FACTCHECK_DRAFT_SKILL and :409 has asserted
  against it since before this task.
  DISCRIMINATION EVIDENCE went beyond what I asked: I requested one site; it ran
  ALL NINE — each adoption deleted in a scratch copy, pins run, restored —
  8 CAUGHT, 1 MISSED. The single miss is synthesis-conventions, which was ruled
  to stay unpinned. skills/ diff empty afterwards.
  SELF-CAUGHT INCONCLUSIVE TEST, worth recording as the behaviour this plan has
  been pushing for: its first check of the negative assert was UNEXERCISED
  because a positive assert fired first. It noticed, re-ran with all positive
  phrases intact plus the false-state claim added, and confirmed only
  `assert "the gate is armed" not in intro` catches it.
  The three appended tokens carry a comment stating WHY they discriminate and why
  the tokens above them do not — a constraint the code cannot show, which is the
  correct side of the comment-hygiene line.
  Implementer's own diagnosis of the pattern: the error was the SCOPE OF ITS
  QUESTION — it searched for a dedicated pin FILE rather than for any test
  READING the file, and test_finding_cli.py pins three skills' prose under a name
  no filename-shaped search surfaces.
Task 8: fix round 1 re-review dispatched over c0d0854..e76805c.
Task 8: fix round 1 re-review — ALL ADDRESSED, no new breakage (c0d0854..e76805c).
  All three appended tokens verified INDEPENDENTLY to occur exactly once, at
  factcheck-draft/SKILL.md:19, :42, :79 — counts and locations match the
  implementer's claim exactly. The false claim is corrected in BOTH durable
  records (report Pins section, marked corrected; and e76805c's body, which
  explicitly says it corrects the first version of itself).
  All five docstrings now open with a constraint statement; a grep across the
  five files for `audit|adopted|§` hits only pre-existing unrelated module
  docstrings. The three-line comment above the appended tokens was judged
  CONSISTENT with the doctrine — it states why those tokens discriminate and the
  ones above them do not, which is a constraint the code cannot show.
  The negative assert is scoped to the same `intro = text[: text.index("## Orient")]`
  slice as the positive ones, so it genuinely fires.
Task 8: complete (commits a2a5aad..e76805c, review clean after 1 fix round,
  7 minors deferred). Suite 1570/7; form gate 8/8.
Task 8: minor (deferred): skills/synthesis-conventions/SKILL.md:18 — the
  compilation-value line ships UNPINNED because no test reads that file at all;
  pinning would need a new pin file, outside the brief's update discipline.
  §7 polish item 06 is queued to rewrite this prose anyway.
Task 8: minor (deferred): skills/publish/SKILL.md:138 — the refusal row omits the
  resolve/acknowledge clearing path that :61 and hooks/stop_publish_gate.py:535
  both carry. CONTESTED: nothing in the row is false, and publish.py:354-362
  routes the ack path back through mark-published, but the enumeration is
  narrower than :61's.
Task 8: minor (deferred): skills/publish/SKILL.md:137-139 — three table rows
  repeat their source paragraphs (:75, :61, :112) near-verbatim, so an edit to
  the canonical prose leaves the table asserting the old rule with the suite green.
Task 8: minor (deferred): skills/publish/SKILL.md:11 — the gate announcement
  omits the eight-block safety bound (hooks/stop_publish_gate.py:16
  MAX_ACTIVE_BLOCKS = 8, released at :506-507 with BOUND_MESSAGE) after which the
  session ends with the gate still armed; and "is acknowledged" grammatically
  attaches the ack to the publish attempt, whereas in this corpus an ack is
  always granted to a blocking finding. Two distinct defects, same line.
Task 8: minor (deferred): tests/test_publish.py:815 — the rationalization pin
  asserts against the whole file instead of slicing to the section first, unlike
  its three siblings, so a row moved out of the table still passes.

Task 9: BASE = e76805c. Implementer dispatched (sonnet). TDD task. The dispatch
  carries the full surface map from my pre-check, the dedup HAZARD spelled out
  (do not filter inside open_entries(), or verify.py:850's _file_effects stops
  suppressing and re-files a duplicate every run), the note that
  scaffold._inbox_probe inherits the fix for free so no second filter is owed,
  the fact that Finding.result is a plain str, and the author's naming ruling
  that inbox.summary() is dev-facing T7 — NOT to be renamed, and the reviewer
  will be told the same so a non-rename is not flagged as a gap.
  Also required: DEMONSTRATE the hazard did not land (show verify's dedup still
  sees SKIPPED), not merely assert it.
Task 9: implementer DONE (commit acd38b5; knowledge_harness/inbox.py,
  tests/test_inbox.py, tests/test_verify_cli.py — 3 files, +70/-2). Suite 1572/7
  (baseline 1570 + 2 new tests); form gate 8/8; tree clean.
  RED confirmed for the RIGHT REASON: unacknowledged 1 -> expected 0, and oldest
  '2026-08-01' -> expected None. GREEN after the fix.
  Filter landed exactly where the map said: inside summary(), as
  `entry.result != Result.SKIPPED.value`, applied to the list BOTH keys derive
  from. open_entries() deliberately untouched.
  HAZARD HANDLED BETTER THAN ASKED: I required a demonstration; the implementer
  made it a PERMANENT regression test —
  test_file_effects_does_not_refile_an_already_open_skipped_finding in
  tests/test_verify_cli.py — which passed both before and after, proving
  open_entries() was never filtered. That converts a one-off check into a guard
  against a future task re-introducing the hazard.
  BUT: a test that passes identically before and after is also the shape a
  VACUOUS test takes. The review is told to construct the counterfactual —
  filter open_entries() in a scratch copy and confirm the test goes RED. If it
  stays green under that mutation it guards nothing.
  Surface sweep: no other counting surface found. The implementer additionally
  grepped `inbox.load(` callers and checked __main__.py:360/371's
  `Result.SKIPPED: 0`, judging both unrelated (CLI exit-code and dedup logic,
  not inbox counting). No existing test pinned the old defect —
  test_summary_counts_and_age never used SKIPPED — so nothing needed fixing.
  summary()'s new docstring states WHY SKIPPED stays in open_entries (verify's
  dedup keys off that list) — a constraint the code cannot show, so the right
  side of the comment-hygiene line. Review is judging that call too.
Task 9: review dispatched over e76805c..acd38b5.

Task 10 PRE-CHECK (controller, read-only, done while Task 9's review ran).
  Surfaces located: knowledge_harness/checks.py:131 `check_citekeys` (the plan's
  ~131 is exact, no drift); knowledge_harness/inbox.py:25 `REASON_CODES`.
  THE DIALECT-SURFACE RULE IS NOW MECHANICALLY ENFORCED — and by an instrument
  THIS PLAN built two tasks ago. Adding `not-imported` to REASON_CODES alone
  turns the suite RED in two independent places:
    - tests/test_skill_contracts.py:487 (Task 3's C-2 pin) asserts
      `tabled | exempt == inbox.REASON_CODES` — full set equality — so
      skills/evidence-conventions/SKILL.md's table must gain a `not-imported`
      row or a named exemption.
    - tests/test_config_validity.py:167 asserts
      `inbox.REASON_CODES - _backticked(row)` is empty, so docs/terminology.md
      §4.4's reason-codes row must enumerate it too.
  So the plan's Step 4 ("register in the registry, terminology §4.4, and
  evidence-conventions' table — same commit") cannot be half-done: the two tests
  name exactly which surface was missed. Task 3's C-2 pin paid off immediately,
  on the very next code task that adds a code.
  Carry into the dispatch: this is a FEATURE, not an obstacle — do not "fix" a
  red suite by exempting the new code from the table; the exemption list is for
  codes that genuinely never reach the review queue (`matched`), and
  `not-imported` will reach it.
  Scope bound from the brief, worth restating: the note's OWN citekey row
  (note-vs-bibliography identity) keeps current semantics — the new rule is
  scoped to CITATIONS only. And `not-imported` is distinct from the existing
  `not-admitted`; the plan says so explicitly.
Task 9: review clean — spec COMPLIANT, quality APPROVED, 0 Critical/Important.
  Review file: .superpowers/sdd/2026-08-22-post-q-batch/task-9-review.md
  THE HAZARD GUARD IS NOT VACUOUS: the reviewer built the counterfactual I asked
  for and confirmed tests/test_verify_cli.py:1163-1183 goes RED under exactly the
  mutation (a filtered open_entries()). So the permanent test genuinely guards
  the dedup hazard against a future task re-introducing it.
  Reviewer independently confirmed summary() is the ONLY unacknowledged
  arithmetic in the package, and that the string compare is TOTAL: Finding.result
  is a str validated against Result.__members__, and Result is a str-enum whose
  member names equal their values.
  Also noted: the mixed-queue test dates the SKIPPED entry 2026-08-01 and the
  UNMATCHED one 2026-08-16, so a fix that excluded SKIPPED from the COUNT but not
  the AGE BASIS would fail on `oldest` — the test discriminates the half-fix.
  Reviewer re-ran the offline suite itself: 1572 passed / 7 skipped, no warnings.
  Cannot-verify closed by controller at acd38b5: form gate 8/8, tree clean.
Task 9: minor (deferred): tests/test_inbox.py:877, :890-892, :898-899 — three
  comments restate the assertion directly beneath them instead of stating a
  constraint the code cannot show.
Task 9: minor (deferred): tests/test_verify_cli.py:1163 — the dedup guard has no
  POSITIVE CONTROL showing _file_effects would file this outcome into an empty
  vault, so it cannot distinguish "dedup suppressed the filing" from "nothing
  would have been filed anyway".
Task 9: minor (deferred): tests/test_verify_cli.py:1181 — the guard's only
  assertion reads through inbox.open_entries(), the very function it protects,
  so its failure message points at the reader rather than at the duplicate row it
  exists to expose. Fix would be asserting against the unfiltered inbox.load().
  NOTE for the final review: these last two concern the guard I specifically
  asked for, and Part 2's Tasks 14-21 touch this same file family — a guard whose
  red message misleads will cost time there. Worth triaging up.
Task 9: complete (commits e76805c..acd38b5, review clean, 3 minors deferred)

Task 10: BASE = acd38b5. Implementer dispatched (sonnet). TDD task. Dispatch
  carries the verified surface list (no line drift — check_citekeys really is at
  checks.py:131), the citations-only scope bound, the not-imported vs
  not-admitted distinctness, and the key insight from the pre-check: the
  dialect-surface rule is now MECHANICALLY ENFORCED by
  tests/test_skill_contracts.py:487 and tests/test_config_validity.py:167, so the
  tests will name whichever surface is missed. Explicitly forbidden: greening a
  red suite by adding not-imported to the EXEMPTION list — that list is for codes
  that never reach the review queue, and this one will.
Task 10: implementer DONE (commit a808f09; 5 files, +58/-13 — checks.py,
  inbox.py, terminology.md, evidence-conventions/SKILL.md, tests/test_checks.py).
  Suite 1575/7 (baseline 1572 + 3 new tests); form gate 8/8; tree clean.
  RED shape correct: 1 failed as predicted, 2 pins passed — the brief's other two
  tests pin behaviour that already holds, so a 1-of-3 red IS the right shape.
  CONTROLLER VERIFIED before dispatching the review: all three dialect surfaces
  landed — inbox.py:32 (registry), terminology.md:141 (§4.4 row),
  evidence-conventions/SKILL.md:86 (table row) — and tests/test_skill_contracts.py
  is NOT in the diff, so the forbidden shortcut (adding not-imported to the
  EXEMPTION list to green a red suite) was not taken. The mechanically-enforced
  dialect rule worked exactly as the pre-check predicted.
Task 10: review dispatched over acd38b5..a808f09. Reviewer pointed at the
  highest-risk item: the SCOPE BOUND. checks.py is +20/-13 inside a per-citekey
  loop that handles BOTH the citation case and the note's own citekey row, and
  the brief forbids changing the latter. Also asked to explain terminology.md's
  10 changed lines for a one-code addition (table realignment vs something
  semantic in a neighbouring row).

TASK 2b ADDED (author, 2026-08-24; origin/main bd28399). Root index template
embeds the two Bases. IN SCOPE for this branch — Part 1, ordering independent.
Task 2 already passed, so this is its own commit:
`feat: vault index embeds the trust-tier and open-questions Bases`.
  Brief extracted from origin/main's plan copy (the branch's copy predates it, and
  we do not merge mid-plan) to
  .superpowers/sdd/2026-08-22-post-q-batch/task-2b-brief.md.
  CONTROLLER PRE-CHECK, all read-only:
  - knowledge_harness/templates/vault/index.md is 12 lines; the folder links are
    lines 7-12, so the embeds go under them.
  - The whole-file pin is tests/test_templates.py:79
    (`assert asset("vault/index.md").read_text() == (...)`) — a byte-equality
    pin, so it must move in the same commit or the suite goes red.
  - Both Base files exist at knowledge_harness/templates/vault/system/bases/.
    trust-tier.base: a table view named "Trust tier", filtered to
    `type == "literature"`. open-questions.base: a table view named "Open
    questions", filtered to `type == "synthesis"` with a formula
    `open_q: file.content.contains("(open-question)")`. The lead-ins compress
    FROM these — the brief says "don't invent".
  - system/bases/ is ALREADY one of the six pinned scaffold paths (Task 5's
    list), so nothing moves and the tree probe is untouched, exactly as the
    author's ruling states.
  HAZARD TO GUARD IN THE DISPATCH: the naming ruling's churn list names
  templates/vault/index.md:10 ("daily activity log (summary: [[log]])" -> reword
  to "rolled up"). That churn is owed by the FUTURE step that authors the summary
  artifact, NOT by this task. An implementer reading plan context while editing
  this exact file could easily over-reach into it. Tell it not to.
  Item 15 (Task 13, live-vault application at ~/kh-vault) now covers the updated
  index as well as the updated AGENTS.md — recorded so Task 13's dispatch carries
  both files.
  DISPATCH HELD until Task 10's review resolves: if that review returns findings,
  its fix round is an implementation dispatch, and the skill forbids two
  implementers running at once. File sets are disjoint, but concurrent commits
  race the index.
Task 10: review clean — spec COMPLIANT, quality APPROVED, 0 Critical/Important.
  Review file: .superpowers/sdd/2026-08-22-post-q-batch/task-10-review.md
  THE SCOPE BOUND HELD, and the reviewer established why from the code: branch
  ordering tests bibliography ABSENCE FIRST, so the pre-existing
  "mismatch — citekey not in bibliography" keeps priority and the new tier can
  never absorb it (checks.py:156-166, pinned by tests/test_checks.py:117). The
  change is one flat if/elif/else in doctrine order: not admitted -> not
  imported -> citable. All three tests drive the real check_citekeys against
  real files, no mocks, each asserting both Result and the exact reason string.
  The reviewer resolved two of its own lenses' cannot-verify items rather than
  passing them up: suite green at a808f09 (1575/7, tree clean) and the RED
  evidence is deterministic from the pre-change branch in the diff.
  Cannot-verify #1 closed by controller: form gate 8/8 at a808f09, tree clean —
    which also settles the report's note that mdformat auto-fixed table rows on
    a first run; the committed tree is gate-clean.
Task 10: minor (deferred): tests/test_checks.py:81 — the scope bound (a
  literature note's OWN citekey row keeps note-vs-bibliography semantics) ships
  with NO committed regression test. The implementer wrote one, ran it, deleted
  it. The reviewer verified empirically that nothing else pins it: the verify-CLI
  fixture sweeps use next(...) filters or an exit code that already tolerates
  UNMATCHED, and the two file_outcomes tests monkeypatch it away. Behaviour is
  correct today, so this is test durability, not a missed requirement — but it is
  the exact boundary I flagged as highest-risk, so it is worth triaging up at the
  final review.
Task 10: minor (deferred): knowledge_harness/checks.py:159 — the
  `vault/"literatures"/f"{citekey}.md"` layout convention is now inlined a FOURTH
  time (notes.py:129, lints.py:491, factcheck.py:73 and :90, checks.py:159) with
  no single owner. Design preference, not a defect.
Task 10: minor (deferred): the tracked mutation sidecars for checks.py and
  inbox.py are stale — source_sha256 no longer matches and recorded function line
  ranges have drifted. Hash-verified by the reviewer. See RULING B below.
Task 10: complete (commits acd38b5..a808f09, review clean, 3 minors deferred)

CONTROLLER RULING A — spec §6's citekey row. The reviewer flagged that
docs/superpowers/specs/2026-08-16-foundation-spec.md:96 still reads "Citekey
exists in bibliography", which now UNDER-DESCRIBES the shipped two-tier check.
The implementer was right not to touch it: the spec was outside Task 10's file
list. Routing it to TASK 21, which already amends §6 rows (Step 1 the metadata
row ~:98, Step 2 the update-notice row ~:99) — :96 is the adjacent row in the
same table, so that task is its natural home and the edit is one row's wording.
Recorded as a carried INPUT to Task 21, and surfaced to the author, since it is a
small scope addition to a task the plan already scoped.

CONTROLLER RULING B — mutation sidecar refresh is a BASELINE act, not a task act.
Task commits do NOT regenerate knowledge_harness/*.py.manifest.json. Grounds,
all checked rather than assumed: nothing reads `source_sha256`; no hook and no CI
step checks sidecar freshness; `__main__.py.manifest.json` was ALREADY STALE at
this branch's BASE, so "do not refresh per task" is the repo's existing practice
rather than a new indulgence; mutate4py rewrites the sidecar on its next run; and
Part 4's Task 25 retires the sidecars WHOLESALE when the mutmut baseline lands.
TASK 22 IS THE EXPLICIT EXCEPTION — its own author ruling mandates regenerating
the factcheck.py sidecar in the same commit, with a stale-commit fallback. No
other task in this plan owes a sidecar refresh.

TASK 2c ADDED (author, 2026-08-24; origin/main 17378d7). Vault AGENTS.md template
opens with a two-sentence integrity preamble, AHEAD of the routing index — the
oblivious-agent defense: routing serves agents who read on, the preamble protects
the ones who don't. IN SCOPE, Part 1, independent ordering, own commit
(`feat: vault AGENTS.md opens with the integrity preamble`) since Task 2 passed.
  Brief extracted from origin/main to .../task-2c-brief.md.
  CONTROLLER PRE-CHECK (read-only) — the template as it stands after Task 2:
  - It ALREADY names machine surfaces at line 24: "Machine surfaces (`log/`,
    `inbox/review-queue.md`, managed regions, `system/bibliography.json`) are
    owner-written: hand or tool edits are regenerated away or raise a finding."
    And line 6 names `literatures/` ("evidence notes exist only by projection,
    never by hand").
  - The brief's DRAFT sentence names `literatures/`, `log/`, root `log.md`,
    `inbox/review-queue.md` — which does NOT match line 24's list. It adds root
    `log.md` (a real vault surface — templates/vault/log.md ships) and omits
    managed regions and `system/bibliography.json`. The brief's instruction
    "adjust the surface list to what the template already names" is precisely
    about this gap, so the reconciliation is the judgment this task turns on.
  - REDUNDANCY RISK to surface rather than resolve unilaterally: a preamble at
    the top saying "these surfaces are machine-written, hand edits are caught"
    sits two paragraphs from line 24 saying nearly the same thing. Some
    compression is the POINT (the preamble exists for the agent that reads
    nothing else), but near-verbatim duplication is a defect. The brief
    authorises ADDING a preamble, not deleting line 24, so the implementer must
    make them non-redundant in emphasis or report the tension — not silently
    delete a line the brief did not scope.
  - The pin is the same whole-file byte-equality assert Task 2 updated
    (tests/test_templates.py:96 region), so it moves in the same commit.
  - The preamble's "the CLI writes" phrasing matches the leading-word token Task 7
    collapsed to — consistent, no conflict.
  DISPATCH HELD: Task 2b's implementer is live and edits tests/test_templates.py;
  Task 2c edits THE SAME FILE. Strictly serial.
  ITEM 15 ACCOUNTING CORRECTED: the consent-gated ~/kh-vault commit now carries
  TWO files with THREE changes — AGENTS.md (Task 2's routing index + Task 2c's
  preamble) and index.md (Task 2b's Base embeds). Task 13's dispatch must name
  all three.
Task 2b: implementer DONE (commit 660f752; 3 files, +16/-2 — index.md template
  plus TWO pins). Suite 1575/7 baseline-equal; form gate 8/8, run twice.
  CORRECTION TO MY OWN PRE-CHECK: I told the implementer the pin was
  tests/test_templates.py:79. There were TWO. The suite caught a second
  byte-equality pin on the identical string at tests/test_scaffold.py:81 (a
  scaffolded-output assertion), which the implementer updated in the same commit.
  Not a defect — the brief's surface list and my verification of it were both
  incomplete by one file, and the pin discipline caught what we missed. The
  review is told not to assume the list is complete even now.
  Controller verified: index.md:10 is UNCHANGED, so the naming-ruling churn that
  is owed by a future task was not pulled into this one.
Task 2b: review dispatched over a808f09..660f752.

TASK 24c ADDED (author, 2026-08-24; origin/main 11e6fb3). Suite hermeticity +
fixture speed. Part 4, so OUT OF THIS BRANCH'S SCOPE — Part 4 order is now
23 -> 24 -> 24b -> 24c -> 25, all running on main AFTER Task 21's merge.
Sequencing logic mirrors 24b's: the mutation gate re-executes covering test
slices per mutant, so every second cut multiplies by mutant count.
  Fix order is the MEASURED-VALUE order: dead_base fixture (the only fix reaching
  test_probe_unreachable's subprocess CLI) -> offline socket-block (the doctrine
  fix; docs/testing.md gains its one-line rule in the same commit) ->
  session-scoped template vault -> retention policy + worksteal.
  Acceptance is BEHAVIOURAL: offline green with sockets hard-blocked and ZERO
  connects to 23119; serial <= ~40 s; live suite still green with both flags.

  CONSEQUENCE FOR THIS BRANCH'S EVIDENCE — flagged to the author, not fixed here.
  24c's headline defect is that the offline suite is NOT hermetic: 97 connects to
  localhost:23119 in one offline run, from unmarked tests in test_verify_cli.py,
  test_okf.py and test_publish.py doing real BBT CSL exports. Offline green was
  machine-dependent — Zotero up means live calls, Zotero down means each connect
  eats a 5 s timeout.
  I PROBED THIS MACHINE: port 23119 is OPEN — Zotero is UP. So every "offline
  suite green" recorded in this ledger, mine and every implementer's, was run in
  the regime where those connects reached a live Zotero. The results are real
  (assertions ran, tests passed) but they are NOT hermetic, and a machine with
  Zotero down would produce a very different run.
  This does not invalidate any task: no task in Parts 1-2 changed those code
  paths, and the deltas we tracked (+2, +3, +5 tests) are all accounted for.
  But it DOES weaken Task 21 Step 3's acceptance, which reads "Full suite offline
  AND live" — until 24c lands, the offline leg is not cleanly distinguishable
  from a partial live run, and 24c is explicitly sequenced AFTER Task 21.
  Recorded so Task 21's acceptance is read with that caveat rather than as
  hermetic evidence.

PROSE-VS-MECHANISM AUDIT ROUTED IN (author, 2026-08-24; origin/main 1b25fad,
47795bc). Three additions, two in Part 1 and one in Part 2 — ALL IN SCOPE:
  TASK 2d (Part 1, independent ordering): scaffold ships .prettierignore,
    .markdownlintignore, .editorconfig covering literatures/, log/,
    inbox/review-queue.md, system/bibliography.json — formatters obey config,
    not paragraphs. The AGENTS.md formatter paragraph (which says of ITSELF "it
    is not what enforces them") shrinks to one line naming the ignore files.
    Step 2 scopes the "prefer the knowledge-harness skills" line to the TWO
    model-invocable guards (evidence-conventions, synthesis-conventions).
    HARD CONSTRAINT: do NOT flip any disable-model-invocation flag — the
    seven-skill human gating is deliberate design, not an oversight.
  TASK 9 ADDENDUM: summary() also emits oldest_age_days and aging: true past the
    Whittaker threshold. Rationale: the skill asks the agent to do date math
    against a clock it does not reliably have.
  TASK 17b (Part 2, after Task 17): the audit's biggest catch — literature
    frontmatter sits OUTSIDE %%hk-managed%%, so lint_evidence_layer's
    managed-slice diff never sees it, and "sole writer of archive-url" is
    enforced by NOTHING at commit. Extend the closing lint to diff the
    machine-owned key set (archive-url, managed-sha256, fixity-sha256,
    generated, citekey) against the base ref. BOUNDARY: status and free prose
    stay OUT — screening is human-writable by design. Failing test first,
    parametrized over the five keys plus the two must-still-pass cases.
    lints.py lint_evidence_layer ~line 618; tests/test_lints.py.
  EXPLICITLY NOT IN SCOPE (went to the post-slice polish ledger): the
    synthesis-shape lint, registry single-sourcing, four-state dedup,
    trust-tier --project. PreToolUse deny stays behind its evidence trigger in
    spec §10. Standing instruction: if I find myself mechanizing skill prose
    beyond these three tasks, that is the polish pass — stop and flag.

  TWO THINGS THE ADDENDUM NEEDS BEFORE IT CAN BE DISPATCHED:
  (a) THE WHITTAKER THRESHOLD DOES NOT EXIST IN THE TREE. I checked every
      occurrence. skills/project-flow/SKILL.md:25 defines the guard in
      deliberately CONTINUOUS, display-only terms: "When the oldest entry is
      old, lead with it... an aging queue earns more prominence the longer it
      goes untouched. This is display only; nothing here blocks on age." Spec §3
      and the rethink audit reference "Whittaker rot" without a number.
      So `aging: true` needs a boolean threshold that has never been decided.
      An implementer would have to INVENT one — exactly the class this plan has
      caught repeatedly. Raised with the author rather than defaulted.
  (b) "SAME COMMIT" IS NO LONGER POSSIBLE. Task 9's commit acd38b5 is buried
      under a808f09 (Task 10) and 660f752 (Task 2b). Amending it would mean
      rebasing two landed, reviewed commits. Per the precedent set at Task 3
      (de1867d corrected FORWARD rather than rebased under a3db464), the
      addendum lands as its own follow-up commit. The intent — one extra
      assertion in Task 9's existing tests — is preserved; only the commit
      boundary moves.
  RULING (author, 2026-08-24) on (a): EMIT `oldest_age_days` ONLY — DROP the
  `aging:` boolean entirely. Author's reasoning, recorded because it generalises:
  the guard is deliberately CONTINUOUS ("earns more prominence the longer it goes
  untouched"), and a boolean quantizes that design with a number nobody decided.
  The addendum's stated purpose was killing the agent's date math, and the number
  alone achieves that completely. The `aging:` flag was the author's own drafting
  embellishment, which smuggled an undecided threshold into a mechanism — "the
  correction-vs-decision error in miniature". Mechanism supplies the FACT (days);
  the skill's continuous-prominence judgment keeps deciding what counts as old,
  which is exactly the division of labour the prose-vs-mechanism audit drew.
  If a threshold is ever genuinely wanted, the slice's pre-registered
  inbox-review-sizing rule is where rot-pressure gets its first MEASURED number —
  a decided one, from data, not from a menu.
  So the addendum reduces to: summary() also emits `oldest_age_days`; one extra
  assertion in Task 9's existing tests; no new constant, no threshold, no boolean.
  Note the shape of this: the author's own draft contained the invented part, and
  the plan's own doctrine (do not ship a number nobody decided) is what removed
  it. Same doctrine that governs implementers governs the plan text.

REVISED QUEUE after all 2026-08-24 additions. Completed: 1, 2, 2b, 3, 4, 5, 6, 7,
8, 9, 10. Remaining in this branch: Part 1 — 2c, 2d, Task 9 addendum, 11, 12, 13;
Part 2 — 14, 15, 16, 17, 17b, 18, 19, 20, 21; then Task 22 (before 21 per its
ordering note, or anywhere — it is independent). Part 4 (23, 24, 24b, 24c, 25)
runs on main AFTER the merge and is NOT this branch's work.
  FILE-COLLISION NOTE for sequencing: 2c and 2d BOTH edit
  knowledge_harness/templates/vault/AGENTS.md, so they are strictly serial with
  each other; 2b (landed) and 2c both touch tests/test_templates.py. The Task 9
  addendum touches inbox.py + tests/test_inbox.py and collides with neither.
Task 2b: review — spec COMPLIANT, quality APPROVED, 0 Critical/Important.
  Review file: .superpowers/sdd/2026-08-22-post-q-batch/task-2b-review.md
  Reviewer verified both pins reconstruct the template's 588 bytes exactly by
  AST-PARSING the literals rather than trusting a green suite; confirmed line 10
  untouched; confirmed no .base file moved; closed two of its own three
  cannot-verify items (commit body provenance; its own pytest run 1575/7) and
  closed the form-gate one BY MECHANISM (ruff format --check clean on both test
  files; mdformat's hook path list provably excludes templates/ and tests/).
  Praised: the implementer found the second pin by RUNNING THE SUITE rather than
  trusting my "nothing to hunt for" surface list, and flagged the brief's
  incomplete enumeration back as a possible BATCH-WIDE pattern — other briefs
  pinning content duplicated between a template asset and a scaffold-output
  assertion may have the same gap. Worth carrying into 2c and 2d.
  Also praised: the trust-tier lead-in deliberately WITHHOLDS a tier-column claim
  the Base cannot support (trust_tier is runtime-computed in events.py; the Base
  has no formula and no tier column), choosing the weaker true sentence over the
  better-reading false one.
Task 2b: minor (deferred): the canonical index.md literal is duplicated verbatim
  in tests/test_scaffold.py:81-95 and tests/test_templates.py:79-93 and must be
  hand-edited in lockstep. Pre-existing structure this change extended; the cost
  MATERIALIZED here (first suite run failed on the second, unnamed pin). Reviewer
  notes the fix is to have test_scaffold assert scaffolded output == asset bytes,
  NOT to extract a shared constant, which would weaken both pins.
Task 2b: minor (deferred): nothing asserts the index.md -> system/bases/*.base
  embed targets actually RESOLVE in a scaffolded vault; the paths are pinned only
  as opaque text, so renaming a .base file while updating EXPECTED_CREATED and
  the asset list but not the index template leaves a dangling embed, suite green.
Task 2b: CONTROLLER ACTION on the render cannot-verify — fix round dispatched,
  framed as risk-elimination not a proven defect. The reviewer could not establish
  offline whether Obsidian promotes `![[x.base]]` to a BLOCK-level table embed
  when the lead-in sits directly above with no blank line (in CommonMark they are
  one paragraph). I cannot verify Obsidian's behaviour either and did not assert
  it — but the asymmetry decides it: a blank line costs nothing, and the failure
  it removes is TOTAL (an inline-rendered embed delivers none of the one-click
  dashboard value while still passing every byte-equality pin). New commit on top
  of 660f752, not an amend, since that commit is reviewed and its review recorded.
  ROUTED TO TASK 13 (live-vault application, where a real Obsidian exists): the
  other half — whether open-questions.base's `open_q` formula column is visible
  in the default table view, given the file declares formulas.open_q but no
  `order`/column list. Needs a .base change outside 2b's scope.

Task 2d PRE-CHECK (controller, read-only) — A DOTFILE PACKAGING TRAP:
  Task 2d ships three NEW scaffold files (.prettierignore, .markdownlintignore,
  .editorconfig). The repo ALREADY has a workaround for exactly this class:
  knowledge_harness/templates/vault/ ships `gitignore` WITHOUT the leading dot,
  and scaffold.py:67 renames it on write —
  `yield ".gitignore" if relative == "gitignore" else relative, source`.
  Package data is `knowledge_harness = ["templates/**/*"]` (pyproject.toml:64).
  So the established pattern is: ship the dotless name as the template asset, map
  it to the dotted name in scaffold.py's rename logic. Task 2d must follow it for
  all three files, or they may silently fail to package.
  ALSO: adding three scaffold files trips enumerated pins —
  tests/test_scaffold.py's EXPECTED_CREATED (currently 18 paths; TRACKABLE_CREATED
  derives from it, and these three would be trackable, hence committed by
  scaffold) and tests/test_templates.py:37
  test_all_canonical_template_paths_are_packaged. Both must move in the same
  commit. The SIX pinned scaffold paths (Task 5's contract) are a different list
  and are NOT affected.
Task 2b: fix round landed — commit 3d26a44 `fix: blank line before each Base
  embed so it renders as a block` (3 files, +6/-4: two blank lines in the
  template, both byte-equality pins moved in lockstep). Suite 1575/7
  baseline-equal; form gate 8/8, and the implementer MD5-VERIFIED that mdformat
  did not touch the file — which also answers the question I raised in the fix
  dispatch: this fix CAN survive the formatter, so the blank lines are stable.
  Controller confirmed the template now reads lead-in / blank / embed / blank for
  both Bases.
  Scoped re-review dispatched over 660f752..3d26a44. NOTE: this fix came from a
  controller-resolved cannot-verify rather than a review finding, but it still
  gets its scoped re-review — "the fix was small, skip the re-review" is on the
  skill's rationalization list, and a whitespace-only change to a byte-equality
  pin is exactly where an invisible error hides.
  Task 2c dispatch stays held until this returns: 2c edits tests/test_templates.py,
  which the re-reviewer is reading.
Task 2b: fix-round re-review — ADDRESSED, no new breakage. The re-reviewer did
  the byte-level reconstruction independently rather than inferring from a green
  suite: it rebuilt the expected literal from tests/test_templates.py:70-85 and
  matched the template exactly (590/590 bytes), AND called
  scaffold.scaffold_vault() LIVE into a temp dir to compare the scaffolded
  index.md against tests/test_scaffold.py:81-92's literal. Line 10 confirmed
  byte-identical against 660f752. No .base file in the diff; EXPECTED_CREATED
  untouched.
Task 2b: complete (commits a808f09..3d26a44, review clean after 1 controller-
  initiated fix round, 2 minors deferred)

USEFUL FACT ESTABLISHED, worth carrying for the rest of the plan: mdformat's
pre-commit hook uses a HARDCODED arg list — `mdformat --number --wrap keep
README.md AGENTS.md CONTEXT.md docs skills` with `pass_filenames: false`
(.pre-commit-config.yaml:57). So it structurally CANNOT reach
knowledge_harness/templates/ or tests/, regardless of what is staged. Verified
empirically too (md5 identical before and after running the hook against the
template). Consequences: template edits are never reformatted, so byte-equality
pins on templates are stable; and the repo-root AGENTS.md IS owned by mdformat
while the vault template AGENTS.md is NOT — two different files, easy to conflate.

Task 2c: BASE = 3d26a44. Implementer dispatched (sonnet). Dispatch carries:
  - the SURFACE-LIST RECONCILIATION as the substance of the task, with both
    lists quoted (template line 24's four surfaces vs the brief's draft, which
    adds root log.md and omits managed regions + system/bibliography.json), and
    an instruction to REPORT an inconsistency rather than paper over it.
  - the REDUNDANCY TENSION with line 24: differentiate in emphasis if possible,
    REPORT if one has to give, never delete a line the brief did not scope.
  - "do not trust any surface list, INCLUDING MINE" — the preceding task's brief
    named one pin and the suite found a second; the reviewer flagged it as a
    possibly batch-wide pattern (packaged-asset assertion vs scaffold-output
    assertion). Run the suite and let it enumerate the pins.
  - the mdformat scope fact above, including the root-AGENTS.md-vs-template
    confusion risk.
Task 2c: implementer DONE_WITH_CONCERNS (commit 514d12b; template +
  tests/test_templates.py). Suite 1575/7 baseline-equal; form gate 8/8. It ran
  the full suite rather than trusting any surface list and confirmed only ONE pin
  exists for this content — no task-2b-style second pin here.
Task 2c: CONCERN 2 ESCALATED AND RULED — the important one. The shipped preamble
  carried the author's drafted clause verbatim: "hand edits are warned in session
  and caught at commit". CONTROLLER VERIFIED against the code before escalating:
  knowledge_harness/verify.py:55 CLOSING_BY_SURFACE["commit"] is
  {"citekey", "evidence-layer"}, so only `literatures/` closes at commit; `log/`
  and `inbox/review-queue.md` raise NON-GATING findings with no session warning.
  The clause was FALSE for two of the three surfaces it named — a false
  enforcement claim in the single sentence aimed at the agent that reads nothing
  else.
  RULING (author, 2026-08-24): weaken the clause to what is true of ALL named
  surfaces; keep all three names. Decided replacement: "hand edits leave a
  trace" — true on all three via evidence-layer closure, append-only findings,
  and drift records. Reasoning recorded: a per-surface enforcement map spends the
  compression that makes a preamble work; narrowing to literatures/ would
  silently un-name two machine surfaces for exactly that reader; and fixing the
  ENFORCEMENT instead would relitigate spec §6's deliberate warn-tier design —
  "changing gate behavior as a side effect of fixing a sentence is the tail
  wagging the gate".
Task 2c: fix round 1/5 dispatched with the decided wording.
Task 2c: deferred finding for the final review (implementer's concern 1, out of
  scope and correctly left alone): the template's OWN line 24 machine-surfaces
  list omits root `log.md`, which knowledge_harness/okf.py shows is genuinely
  machine-written. A defect in a line this task does not scope.

### FOR THE BATCH'S LANDING REPORT (author asked this be logged where earned)

THE CATCH DISCIPLINE RAN IN THE HARDEST DIRECTION TWICE IN ONE RUN — against the
planner, not the implementers:
  1. Task 9 addendum: the drafted `aging: true` flag required a Whittaker
     threshold that exists NOWHERE in the tree. Shipping it would have made an
     invented number the tree's first Whittaker constant. Dropped; mechanism now
     emits `oldest_age_days` only, and the skill's continuous-prominence
     judgment keeps deciding what counts as old.
  2. Task 2c: the drafted preamble clause fabricated an ENFORCEMENT CLAIM — "warned
     in session and caught at commit" — inside the anti-fabrication preamble
     itself, false for two of its three surfaces. Caught by verification against
     CLOSING_BY_SURFACE.
  Both were the author's own drafting, both were caught by the same rule that has
  caught six implementer claims in this run, and in both cases the author ruled
  against their own draft. That symmetry — one doctrine binding planner and
  implementer alike, verified against the tree rather than argued — is the
  system's own evidence that it is a doctrine and not a review posture.
Task 2c: fix round 1 landed — 514d12b AMENDED into a5668d6 (still branch tip,
  nothing on top, so the amend is clean). The ruled clause shipped verbatim:
  "This is a knowledge-harness vault. `literatures/`, `log/`, and
  `inbox/review-queue.md` are machine-written — the CLI writes them; hand edits
  leave a trace." Suite 1575/7 baseline-equal; form gate 8/8.
  Controller verified the diff is PURELY ADDITIVE — 2 files, 5 insertions, ZERO
  deletions — so line 24 was not deleted or gutted, exactly as the brief required.
Task 2c: review dispatched over 3d26a44..a5668d6. NOTE this is the task's FIRST
  review: the concern was escalated and ruled BEFORE any review ran, so the
  review sees the post-ruling state. The reviewer is told not to re-litigate the
  ruling but IS told to verify the new claim is true — if "leave a trace" is
  itself false for any named surface, that is worse than the first false claim,
  because this is the anti-fabrication preamble.

TASK 17b PRE-CHECK (controller, read-only, done while Task 2c's review ran).
  GOOD NEWS — everything the task needs already exists, no signature change:
  - `lint_evidence_layer(base_snapshot, candidate_snapshot)` (lints.py:618)
    ALREADY takes BOTH snapshots, so base-ref access is there.
  - lints.py already imports `frontmatter` (line 13), so parsing is available.
  - `_literature_files(snapshot)` (:599) yields path -> FileImage for either side;
    `_managed_bytes(image)` (:609) extracts the managed slice and is already used
    for the rename-pairing logic.
  So the implementation is: for paths present in BOTH snapshots, parse frontmatter
  from each image, compare the five machine-owned keys, emit `evidence-layer`
  UNMATCHED/drift on a change.

  DESIGN GAP THE TASK TEXT LEAVES IMPLICIT — needs an author ruling BEFORE 17b is
  dispatched. The plan says "Import-note's own writes are the legal path (they go
  through the CLI, not a hand edit against base)." But at commit time a git
  base->candidate diff CANNOT distinguish a CLI write from a hand edit — both are
  just changed bytes. The natural reading of "diff the key set ALONGSIDE the
  managed slice" is: a machine-key change is legal when the managed slice ALSO
  changed (a genuine regeneration), and illegal when the key moved while the
  managed region stayed identical (a surgical hand edit).
  THAT RULE BREAKS ON THE HEADLINE KEY. `archive.py:72` `_write_archive_url`
  inserts or replaces the archive-url line INSIDE THE FRONTMATTER and does not
  touch the managed region. archive-source is the SOLE legitimate writer of
  archive-url (spec §7, archive.py:1). So a legitimate archive-source run produces
  EXACTLY the signature 17b wants to flag: frontmatter key changed, managed slice
  unchanged. The naive rule would flag the CLI's own sanctioned path — and
  archive-url is the key whose unenforced ownership IS the audit's stated gap.
  Options for the author, recorded now rather than rediscovered at dispatch:
   (a) require a corroborating record — an archive-url change is legal only if a
       matching web-archive event/finding exists in the same candidate snapshot;
   (b) have archive-source co-sign its write (e.g. touch `generated`), giving the
       lint a witness to key on;
   (c) exclude archive-url from the diffed set — but that guts the headline case;
   (d) accept it as a warn-tier finding a human acknowledges once per archive run.
  NOT blocking today: 17b sits in Part 2 after Task 17, roughly eight tasks out.
  Flagged to the author now because the context is fresh and it may change how
  17b is scoped.
  RULING (author, 2026-08-24; amended on origin/main at ea0774d) — WRITER
  ATTESTATION replaces managed-slice coupling as the legality primitive.
  The author EXTENDED my finding: the coupling heuristic leaks not only on
  archive-url's frontmatter-only write but ALSO on import-note's own keys — a new
  attachment with no annotations changes `fixity-sha256` while the managed slice
  stays byte-identical. Two independent leaks means slice-coupling was never the
  right primitive. (That the attachment case fell out of the same fix is the sign
  the new primitive is right.)
  THE RULE: a machine-owned key change is legal IFF `generated` changed in the
  same diff with `by` = the machine actor (AGENT_ACTOR). Every CLI writer already
  touches or can touch it — import-note writes `generated` with every projection;
  archive-source gains a `generated.{by,at}` bump (Step 2b), defensible because
  gaining a snapshot reference IS a meaningful content change and is orthogonal
  to byte-identical-rerender preservation.
  SCOPE HONESTY, to be stated in the lint's own finding text: this defends
  against ACCIDENTS and OBLIVIOUS AGENTS — an Obsidian property-panel tweak never
  touches `generated`. A hand edit that also forges the attestation is deliberate
  circumvention, which is recorded-bypass territory, not the accident class this
  lint exists for. Spec §2's own words apply: a stated boundary, not a compliance
  control.
  WHY THE OTHER ROUTES DIED (recorded so they are not re-proposed): route 4
  manufactures a rubber stamp — one identical ack per legitimate archive run, the
  exact factory §3 prohibits; route 3 abandons the audit's headline case; route 1
  couples the lint to a record archive-source does not reliably produce.
  Task 17b now has Steps 1, 2, 2b, 3, and its commit subject changed to
  `fix: closing guard covers machine-owned frontmatter keys via writer attestation`.

  ONE INTERNAL INCONSISTENCY IN THE AMENDED TEXT, flagged to the author:
  Step 1 parametrizes the failing test over FIVE keys including `generated`
  ("archive-url ... managed-sha256, fixity-sha256, `generated`, citekey"), but
  Step 2's guarded set is FOUR and deliberately excludes it
  ("`archive-url`, `managed-sha256`, `fixity-sha256`, `citekey`") because
  `generated` is now the WITNESS rather than a guarded key.
  Taken literally the two steps disagree, and putting `generated` in the guarded
  set would be CIRCULAR — a `generated` change would legalize itself.
  RECOMMENDED READING, pending confirmation: `generated` stays guarded but under
  its OWN predicate — a `generated` change whose `by` is not the machine actor is
  itself drift. That closes the circularity and keeps Step 1's parametrization
  honest, so all five keys remain covered with `generated` guarded differently
  from the other four.
  RESOLVED (author, 2026-08-24; origin/main 07e21f2): the two-predicate rule is
  adopted as recommended. `generated` stays guarded under its OWN predicate — a
  `generated` change whose `by` is not the machine actor is drift. No
  circularity (it cannot legalize itself), Step 1's five-key parametrization
  stands, and `generated` asserts the second predicate. The circularity argument
  is now inline in the plan text, so the executor eight tasks out reads the
  decision WITH its rationale and needs no dialog.
  Author's note on why this strengthens the scope line: a forger must now produce
  a WELL-FORMED MACHINE ATTESTATION, not merely touch the field — which is
  exactly where the accident/circumvention boundary was drawn.

TASK 11 PRE-CHECK (controller, read-only, done while Task 2c's review ran).
  DEFECT CONFIRMED EXACTLY AS THE PLAN DESCRIBES. notes.py:141 `_split_free`:
    :142-143  `existing is None` -> SEED_FREE          (correct: fresh seed)
    :144-150  scan for MANAGED_CLOSE -> verbatim tail  (correct: preserved)
    :151      fallthrough `return SEED_FREE`           <- THE DEFECT
  A non-empty `existing` with NO marker silently returns SEED_FREE, discarding
  the entire hand-written body — and render_note (:257) then writes that as
  success. The plan's fix replaces :151 with the RenderIntegrityError.
  PRECISE DETAIL THAT IS EASY TO MISS: the plan's case list is "None/EMPTY ->
  SEED_FREE". Today an empty string `""` reaches :151 via the loop-with-no-lines
  path and returns SEED_FREE by accident. After the fix, :151 RAISES — so the
  empty-string case must be caught EXPLICITLY in the first branch, or a fresh
  render with `existing=""` starts raising. The brief's third test
  (`test_fresh_note_still_seeds`, existing=None) would NOT catch that regression.
  TRAP THREE LINES AWAY: `SEED_FREE = "\n## Notes\n"` (notes.py:16) is the
  free-region seed heading. The 2026-08-23 naming ruling says the literature-note
  free-region heading reads `## Summary` — but that churn is owed by the FUTURE
  step that authors the summary artifact, NOT by Task 11. An implementer editing
  _split_free will have SEED_FREE on screen and the naming ruling in context.
  The dispatch must say: leave `## Notes` alone.
  SUPPORTING CONTEXT for Step 4 (spec §5 invariants): notes.py:154-156 already
  carries the comment "§5 never-delete applies to metadata too" beside
  MANAGED_FIELDS — the free-region sentence extends the same invariant, so the
  spec edit has an in-tree precedent to match in wording.
  SPEC-FILE NOTE: Task 11 Step 4 edits spec §5's invariants line and Task 16
  edits spec §5's event-integrity paragraph. Same file, different paragraphs —
  no conflict between them, and both are separate from the author's own §4/§10
  edits already on origin/main.
  Task 11 empty-string gap PINNED by the author in the plan text (origin/main
  1467d64): test_fresh_note_still_seeds now parametrizes existing=None AND
  existing="" with the reasoning inline. The `## Notes` guard stays a
  dispatch-level fence rather than a plan change — churn ownership is already
  recorded with the naming ruling, and the fence belongs at the moment of
  temptation.

TASK 12 PRE-CHECK (controller, read-only). Clean — no surprises, and the plan's
  supplied code is correct AS WRITTEN.
  DEFECT CONFIRMED at notes.py:260 `_assert_managed_body_parses`:
    expected = [claim_id(a) for a in annotations]
    parsed   = [claim.claim_id for claim in parse_claims(body) if claim.in_managed]
    if parsed != expected: raise
  `claim_id` (:280-282) is `"c-" + sha256(basis)[:8]` where
  `basis = annotation.get("key") or _norm(annotationText)`. So two KEYLESS
  annotations with identical text produce the SAME id. expected becomes
  ["c-xxxxxxxx", "c-xxxxxxxx"]; the rendered body carries two identical `^` anchors;
  parse_claims reads both, so parsed == expected and the equality check PASSES.
  Duplicate anchors ship — exactly the plan's diagnosis.
  VERIFIED THE ONE THING THAT COULD HAVE BROKEN THE PLAN'S FIX: `expected` is a
  list of STRINGS, so `len(set(expected)) != len(expected)` is safe — no
  unhashable-element risk. The fix works as supplied.
  PLACEMENT NOTE for the dispatch: put the uniqueness check BEFORE the
  `parsed != expected` comparison. Both orders catch the defect, but before gives
  the accurate diagnosis ("duplicate claim anchors") instead of letting a
  misleading equality pass first. Check `expected`, not `parsed`, as the plan
  says — that catches the collision at its source regardless of what rendered.
  No legitimate duplicate exists: identical keyless text IS a duplicate
  annotation, and duplicate explicit keys would be an upstream data error.
  Task 12 is the smallest remaining code task — no spec edit, no dialect
  surfaces, one assert plus one test.
Task 2c: review returned — spec ISSUES, quality NEEDS FIXES. Review file:
  .superpowers/sdd/2026-08-22-post-q-batch/task-2c-review.md
  LENS FAILURE, recorded for coverage honesty: the FIDELITY lens died on an API
  error (400 tools.10.model: claude-fable-5). This review ran on 2 of 3 lenses,
  so "no other findings" carries less weight than usual here.
  ONE CONFIRMED IMPORTANT, plan-mandated: "hand edits leave a trace" is FALSE for
  an IN-FORMAT APPEND to a log/ day file. Reproduced end to end in a scaffolded
  vault: no PostToolUse warning (hooks/posttooluse_lint.py:97,104 covers only
  literatures/ and CONCEPT_ROOTS); no append-only finding (lints.py:141 fires only
  when new bytes do NOT start with old — an append DOES, controller verified the
  line independently); no gate (append-only absent from
  CLOSING_BY_SURFACE["commit"]); then okf.py copies the fabricated line into root
  log.md. `verify --surface commit` exits 0, zero findings.
  Cannot-verify closed by controller at a5668d6: form gate 8/8, tree clean.
  RULING 1 (author, 2026-08-24) — DROP THE MECHANISM CLAIM, STATE THE BOUNDARY.
  Assert no mechanism, so nothing can be falsified. Decided sentence, now naming
  FOUR surfaces: "This is a knowledge-harness vault. `literatures/`, `log/`,
  `log.md`, and `inbox/review-queue.md` are machine-written — the CLI writes them;
  don't edit them by hand." Adding root log.md also resolves the Minor the
  implementer raised twice. Fix round 2 dispatched.

### RULING 2 — THE REPRODUCTION IS A GATE DEFECT, NOT PROSE DRIFT

  The author followed the reproduction one step further than the review did:
  an in-format append to inbox/review-queue.md that nothing detects can be a
  HAND-WRITTEN ACK LINE. Closures are bypassed IFF a matching human
  acknowledgment exists — so an oblivious agent that Writes an ack instead of
  invoking the `ack` verb has SILENTLY DEFEATED THE PUBLISH GATE. And okf.py
  launders appended log forgeries into root log.md, a machine surface.
  THE PRE-REGISTERED TRIGGER HAS FIRED. Spec §10's PreToolUse entry says revisit
  blocking "only on evidence that warnings fail" — and for these two surfaces
  warnings DO NOT EXIST to fail, which clears that bar rather than relitigating
  the warn-tier design. The author is explicit this is the trigger firing, not a
  reopening of 17b's ruling.
  THE DESIGN IS ALREADY SPECIFIED — prose-vs-mechanism audit finding 4:
  PreToolUse DENY on Edit/Write into the machine-surface path list. Fixed paths,
  no vault import, no fail-open inheritance, CLI unaffected because it writes
  through Python. Closes the AGENT-SIDE accident class at the source; the
  HUMAN side remains the stated boundary, honestly worded by Ruling 1's sentence.
  STATUS: no task exists for this yet. It was previously listed as explicitly OUT
  of scope ("PreToolUse deny stays behind its evidence trigger in spec §10").
  I am NOT self-authorizing a new task — plan additions have come from the author
  on origin/main every time. Flagged and awaiting either an amendment or an
  instruction to draft one.
Task 2c: fix round 2 landed — a5668d6 AMENDED into c8cac73 (still branch tip).
  Shipped sentence: "This is a knowledge-harness vault. `literatures/`, `log/`,
  `log.md`, and `inbox/review-queue.md` are machine-written — the CLI writes
  them; don't edit them by hand." Four surfaces, no mechanism asserted. Pin gained
  a constraint comment so a future editor cannot silently reintroduce a false
  enforcement claim. Suite 1575/7; form gate 8/8; tree clean.
Task 2c: fix round 2 re-review dispatched over a5668d6..c8cac73, built around ONE
  question: this preamble has now been wrong TWICE in the same clause, so the
  re-reviewer's whole job is to ask whether the SURVIVING sentence makes any
  falsifiable claim and whether it is true. The mechanism clause is gone, but one
  factual claim remains — "the CLI writes them", asserted of all FOUR surfaces —
  and it must be verified per surface against the code. A third false claim in
  the anti-fabrication paragraph is the finding that would matter most.
  Also asked: is `don't edit them by hand` an INSTRUCTION (fine — a stated
  boundary) or does it imply a consequence that does not exist (not fine)?
Task 2c: fix round 2 re-review — ALL ADDRESSED, no new breakage (a5668d6..c8cac73).
  The re-reviewer answered the one question that mattered: it verified "the CLI
  writes them" PER SURFACE against the code, not as a blanket claim —
  literatures/ via cmd_import_note -> _write_note_text (__main__.py:301); log/
  via publish._append_log (:399), with NO log/journal verb in the parser that
  would let a human write freeform lines; log.md via okf.regenerate_log (:38,
  whole-file write) called from three CLI-internal sites only;
  inbox/review-queue.md via inbox.append_entry/append_ack from the finding and
  ack verbs, verify.py and the stop hook. It also judged "don't edit them by
  hand" a bare imperative asserting no consequence — fine per the test I set.
  The pin's constraint comment was judged acceptable: present tense, names
  concrete re-verification targets (CLOSING_BY_SURFACE, lint_append_only's
  startswith predicate), no dates, no round-by-round narration.
  The 18-line test delta accounted for: a 13-line constraint comment plus a
  3-for-2 rewrap of the pinned sentence. Lines 24/26 byte-identical.
Task 2c: complete (commits 3d26a44..c8cac73, review clean after 2 fix rounds,
  3 minors deferred). Suite 1575/7; form gate 8/8.
Task 2c: minor (deferred): the template's line 26 "Machine surfaces (...) are
  owner-written" list still DIVERGES from line 6's new four-surface list — omits
  log.md and literatures/, adds managed regions and system/bibliography.json.
  Not a contradiction (nothing there claims log.md is human-editable), and
  deliberately left untouched; carried to the final review.
Task 2c: minor (deferred): line 6 and line 26 are two enumerations of machine
  surfaces with different membership and different consequence clauses, and
  nothing marks which is the abridged form.

Task 2d: BASE = c8cac73. Implementer dispatched (sonnet). Dispatch carries:
  - the DOTLESS PACKAGING PATTERN (ship `prettierignore` etc. without the dot,
    extend scaffold.py:67's rename mapping, as `gitignore` already does);
  - the enumerated pins that adding three scaffold files trips (EXPECTED_CREATED,
    TRACKABLE_CREATED's derivation, test_all_canonical_template_paths_are_packaged,
    the AGENTS.md byte pin) PLUS "do not trust that list, run the suite";
  - the two model-invocable guards, verified mechanically as the only two
    skills/*/SKILL.md files WITHOUT disable-model-invocation;
  - the HARD PROHIBITION against flipping any disable-model-invocation flag;
  - a DO-NOT-TOUCH fence around line 6 (three wordings, two author rulings) and
    line 26 (a known deferred finding);
  - an instruction to verify each ignore file's SYNTAX per tool rather than
    assuming gitignore semantics — wrong syntax means the file silently does
    nothing, which would reproduce the very defect this task fixes;
  - the self-review test that actually matters: would a formatter run in a
    scaffolded vault now skip the machine surfaces?

TASK 24d ADDED (author, 2026-08-24). Version currency: ruff 0.15.21 -> 0.16.4 by
the upgrade protocol recorded in pyproject itself; pyproject-fmt patch bump plus
the stale shellcheck comment in quality.yml; GitHub Actions v4/v5 -> v7.
Part 4 order is now 23 -> 24 -> 24b -> 24c -> 24d -> 25. OUT OF THIS BRANCH'S
SCOPE — Part 4 runs on main after Task 21's merge.
  Sequencing rationale, consistent with 24b and 24c: it sits BEFORE the baseline
  because a ruff bump AFTER Task 25 would invalidate a fresh baseline; before it,
  the change is free.
  Step 1 is the only non-mechanical piece: `extend-select` cannot UNSELECT
  defaults, so any single rule that 0.16 default-enables from the deliberately
  skipped families (BLE/D/TRY/PL) must move into `ignore` WITH its recorded
  rationale intact — otherwise the skip-list rulings silently stop being true.
  Three places move together: the dep pin, `required-version`, the pre-commit
  lane. Trivial autofixes land in the same commit; anything larger is REPORTED,
  not landed.
  Step 3 scope note worth carrying: the Actions bump covers
  .github/workflows/quality.yml AND BOTH vault CI templates
  (knowledge_harness/templates/ci/{verify,rw-batch}.yml), because those render
  into every user vault at scaffold — stale actions there ship to USERS, not just
  to this repo. Template pins move in the same commit.
  EXPLICITLY OUT OF SCOPE, decided: CI stays on Python 3.12 (everything is
  developed and verified on 3.12.3; revisit post-slice), and no venv-wide
  --upgrade rides this task — pins only.
  CONTROLLER CHECK DONE: the harness-core dist-info ghost the author fixed
  outside the plan is NOT present in this worktree's venv. `pip list` shows only
  `knowledge-harness 0.1.0` (editable, pointing at this worktree) and no
  harness_core* dist-info exists under site-packages. No uninstall needed here,
  so every suite result recorded in this ledger was produced against a clean venv.
  No collision with in-flight work: Task 2d touches templates/vault/, Task 24d
  touches templates/ci/ — different subtrees, and 24d is post-merge regardless.

CI AUDIT FOLDED INTO PART 4 (author, 2026-08-24; origin/main 1dd4e10). No new
tasks — 24d grew and Task 25 gained a step. ALL PART 4, out of this branch's
scope; recorded so nothing is rediscovered.
  24d STEP 2 CHANGED IN KIND: shellcheck is not a comment fix but the lane's ONE
  UNPINNED TOOL, riding the runner image. Concrete failure predicted in the plan
  text: when ubuntu-latest migrates to 26.04 it jumps to 0.11.x and the VAULT
  pre-commit template starts failing on a change nobody made. Install it by the
  shfmt pattern (pinned version + release URL + `sha256sum -c`) and DELETE the
  ships-in-the-image exception — so the "pinned exact, like every other tool"
  sentence becomes TRUE rather than scoped. Same shape as the preamble fixes:
  the sentence is not edited to match a weaker reality, the mechanism is fixed to
  make the sentence true.
  24d STEP 4 IS NEW — five folds in the same files:
   (a) ELIMINATE raven-actions/actionlint@v2 — the lane's one floating
       third-party tag executing arbitrary code in the job — via the
       pinned-binary-download pattern, digest-checked like shfmt. SHA-pinning is
       the FALLBACK only if the binary route fights the runner.
   (b) actionlint gains the TWO VAULT CI TEMPLATES as file arguments: they ship
       to every user vault and have NEVER BEEN LINTED.
   (c) shfmt's install gains its digest check; the verified hash is in the plan.
   (d) Concurrency group with cancel-in-progress ONLY for pull_request —
       cancelling a push-to-main run would abandon a landing mid-flight.
   (e) `persist-credentials: false` on checkout; the fetch-depth comment names
       BOTH consumers (the mutation gate and the record-immutability hook).
  TASK 25 STEP 1b: THE MUTATION GATE HAS NEVER ACTUALLY EXECUTED — push runs
  no-op by construction and this repo has zero PR runs, so every claim in the
  gate's comment block is REASONED, NOT OBSERVED. After the mutmut port and
  baseline land: `gh workflow run quality.yml --ref <branch-touching-core>`,
  observe one real end-to-end gate run, and set `timeout-minutes` FROM THAT
  MEASURED BOUND — do not invent the number first.
  UNCHANGED AND DELIBERATE, from the audit's verified-true list (recorded so a
  later reader does not "fix" them): `-n auto` stays ABSENT from CI pytest;
  `[pdf]` stays uninstalled; config-validity's double run STANDS; the base_ref
  fallback is correct on all three triggers.

### LANDING-REPORT META-FINDING, EXTENDED

  The no-invented-numbers / claims-must-be-observed doctrine has now caught the
  same defect class at THREE levels, not two:
   - IMPLEMENTER claims (six this run): a sweep claiming coverage it did not
     have; a grep transcript of a run that produced different output; a citation
     the source never made; a miscounted deviation ledger; a pin justification
     the tree falsified; a residual bound false against a shipped enumeration.
   - PLANNER claims (two): the invented Whittaker threshold, which would have
     become the tree's first such constant; and a fabricated enforcement clause
     inside the anti-fabrication preamble — twice, since the re-ruled wording was
     also false and was caught by reproduction in a scaffolded vault.
   - INFRASTRUCTURE claims (now): a CI gate whose entire comment block describes
     behaviour it has never exhibited, because it has never run — and a
     timeout-minutes value that Step 1b explicitly forbids inventing before it is
     measured.
  One rule, applied to code, to plan text, and to the machinery that checks both.

### DOCTRINE LINE — PIN VS NARROW (author, 2026-08-24)

  When a claim and reality disagree, MAKE HONEST WHICHEVER SIDE IS CHEAPER TO FIX.
   - The vault preamble WEAKENED ITS CLAIM: the asserted mechanism did not exist,
     and building it would have relitigated settled warn-tier design.
   - Shellcheck STRENGTHENS REALITY: the mechanism is one `sha256sum -c` away, so
     the sentence gets made true instead of scoped.
  Same test, opposite outcomes, both right. The failure mode is applying one
  direction reflexively — narrowing every claim produces honest documentation of
  a weak system, and strengthening every mechanism relitigates settled design to
  save a sentence.

  THE VERIFIED-TRUE LIST IS THE DOCTRINE'S QUIET COMPLEMENT: its value is measured
  as much by the four things a later reader will NOT "fix" (`-n auto` absent from
  CI pytest, `[pdf]` uninstalled, config-validity's double run, the base_ref
  fallback correct on all three triggers) as by the nine claims it caught. An
  audit that only ever finds defects teaches its readers to distrust everything;
  one that publishes what it checked and found sound teaches them where to stop.

TASK 13 PRE-CHECK (controller, read-only) — ITS PLAN TEXT IS STALE AGAINST THREE
LATER RULINGS. Task 13 on origin/main still reads: "update the live vault's
AGENTS.md ... — ONE FILE, separate repo". Since it was written, item 15 has
accumulated:
  1. AGENTS.md — routing index (Task 2) PLUS the integrity preamble (Task 2c).
     RULED: "Item 15's consent-gated ~/kh-vault commit now carries three files:
     AGENTS.md, index.md, and this preamble rides the first."
  2. index.md — the two Base embeds (Task 2b). RULED: "when the author consents
     to that vault commit, the updated index goes with the updated AGENTS.md."
  3. NOT RULED, my question: Task 2d adds THREE new scaffold files
     (.prettierignore, .markdownlintignore, .editorconfig). A live vault WITHOUT
     them is precisely the unprotected case they exist to fix — an editor that
     trims trailing whitespace on save corrupts the append-only queue's
     byte-preservation contract. So there is a real argument they belong in the
     same consent-gated commit. But that extends item 15 beyond what has been
     ruled, and 2d's final shape is still in flight (the `[*]` fix is running).
  4. ROUTED BY ME at Task 2b's review: verify in a REAL Obsidian whether
     open-questions.base's `open_q` formula column is actually visible in the
     default table view — the file declares `formulas.open_q` but no `order` or
     column list, so the shipped lead-in may describe something the reader cannot
     see. That needs a Bases-capable Obsidian, which ~/kh-vault has and this
     worktree does not. It also may require a change to a .base file, which is
     NOT currently in Task 13's scope.
  RAISE WITH THE AUTHOR once 2d lands and its file set is final: whether the
  consent-gated vault commit carries two files or five, and whether a .base fix
  falls inside item 15 or needs its own task. Not blocking — Task 13 is several
  tasks out — but the plan text should say what the commit actually carries
  before an implementer reads "one file" and stops there.
  RULED (author, 2026-08-24; origin/main ba10d33) — Task 13's scope is now a
  CLASS, NOT A COUNT: "update the live vault at ~/kh-vault to the CURRENT
  template set — every file the landed template tasks produced ... Enumerate the
  actual file list at dispatch from the landed tasks."
  This dissolves the moving-target problem: 2d can settle at whatever count it
  settles at, the dispatch reads the truth of that day, and nobody rules twice.
  ITEM 3 RULED — the ignore files ARE included. The argument closes itself: the
  live vault is the IN-USE vault, exactly where an editor's trim-on-save
  corrupting the append-only byte contract stops being hypothetical. Shipping
  protective config everywhere EXCEPT the one vault actively carrying the slice
  would be the inversion.
  ITEM 4 RULED — the open_q Bases check RIDES AFTER, never inside. It is
  author-side verification needing a Bases-capable Obsidian, performed AFTER the
  commit lands. If it turns out to need a .base edit, that is a RECORDED FINDING
  for a later task, never Task 13 scope creep. Fenced on both sides: after the
  commit, author-performed, findings-not-edits.
  The consent gate is UNCHANGED: one vault commit, asked first, never pushed to
  the vault remote without explicit consent.
  DISPATCH NOTE for Task 13: do not carry a hardcoded file list into the brief —
  derive it from the landed template tasks at dispatch time, per the class rule.

TASK 2e ADDED (author, 2026-08-24; origin/main 2b6f3bf). Form-gate coherence.
IN SCOPE — Part 1. Five steps; three carry decisions rather than mechanics.
  STEP 1 REVERSES THE AUDIT'S RECOMMENDATION. The audit said gate
  skills/find-sources/scripts/*.py; the author rules they stay UNGATED, BY the
  vendor rule — frozen K-Dense fork, re-vendor to update, so our formatters and
  autofixers would create VENDOR DRIFT. The deliverable is making the exclusion
  EXPLICIT: one comment at ruff's path list naming it and why.
  DO NOT "FIX" THE 12 FINDINGS IN THOSE FILES. The real one —
  jats_to_text.py:291 passing `Element | None` into `collect_sections` — goes to
  the K-Dense UPSTREAM REPORT QUEUE as ready-to-file, and lands at the next
  re-vendor, NEVER by hand.
  This is a THIRD direction on the pin-vs-narrow axis: not weakening the claim,
  not strengthening reality, but "the exception is correct — state it". The path
  list's implicit "we gate everything" becomes "we gate everything except the
  vendored fork, because touching it would drift the fork".
  STEP 2 IS A RENDER-CONTRACT EVENT, not a path-list edit. Adding
  knowledge_harness/templates/vault to mdformat canonicalizes 11 template files,
  FIVE of which change — and those ship VERBATIM into user vaults. Requirements:
  its OWN COMMIT; template pins in the same commit; and the commit body must
  state the downstream truth — existing vaults see MANAGED-REGION DIFFS on next
  refresh, which are legitimate `stale` outcomes, NOT defects.
  STEP 3: THE HOOK STAYS UNINSTALLED — ruled. pre-commit's stash/restore plus
  whole-tree `always_run` hooks is exactly the interference the pathspec rule
  guards against in a shared checkout. Deliverables: fix the header sentence to
  the truth ("when typed, and in CI"), and name the replacement practice — run
  the form owner DIRECTLY on touched files before committing.
  NOTE `pre-commit run --files` ALSO STASHES and is NOT the safe form.
  STEP 4 carries one item that must not be lost in the batch: the
  record-immutability hook SWALLOWS any `git diff` failure into an empty
  `touched` and PASSES VACUOUSLY. Make it fail loud, with explicit failure
  handling inside the `bash -c`. Also: document yamlfix's self-exclusion; drop
  the dead `analysis` pathspec; add an mdformat upgrade-protocol comment matching
  ruff's.
  SEQUENCING: independent within Part 1, BUT Step 2 rewrites template files that
  Tasks 2b, 2c and 2d just pinned byte-for-byte. It must run AFTER all three are
  final. 2d landed at c418cf7 with its review in flight, so 2e is queued behind
  that review.

  BEARS ON MY OWN PRACTICE: I have used
  `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` as the form
  gate throughout this run. Step 3's hazard is stash/restore interference in a
  SHARED checkout with unstaged work. Every one of my gate runs was paired with a
  `git status --porcelain` check and executed on a CLEAN tree, in a worktree no
  other session shares — so nothing was ever stashed and no result is suspect.
  Recording it rather than assuming it, since the hazard is real and my usage
  only looks safe once the pairing is stated.

  FOURTH LEVEL OF THE CLAIMS-MUST-BE-OBSERVED DOCTRINE, for the landing report:
  Step 4's record-immutability hook passes VACUOUSLY when `git diff` fails —
  a gate reporting success without having checked anything. The ledger now has
  the same defect class at four levels: implementer claims, planner claims,
  CI-infrastructure claims (Task 25's never-executed mutation gate), and now
  a git hook that green-lights on its own error path.

### DOCTRINE LINE, FINAL FORM — THE THREE DIRECTIONS (author, 2026-08-24)

  When a claim and reality disagree, there are exactly three moves, and the
  choice is made by WHICH SIDE IS RIGHT — never by reflex:
   1. WEAKEN THE CLAIM — when no mechanism is worth building.
      Instance: the vault integrity preamble. The asserted enforcement did not
      exist, and building it would have relitigated settled warn-tier design.
   2. STRENGTHEN REALITY — when the mechanism is cheap.
      Instance: shellcheck. One `sha256sum -c` away, so the sentence
      "pinned exact, like every other tool" gets made true rather than scoped.
   3. STATE THE EXCEPTION — when the deviation is correct.
      Instance: the vendored K-Dense fork. Ungating it is RIGHT (our formatters
      would drift the fork), so the fix is naming the exclusion and its reason,
      not eliminating it.
  Preamble, shellcheck, vendored fork: one instance each, all three in this plan.
  THE FAILURE MODE IS PICKING BY REFLEX INSTEAD OF BY WHICH SIDE IS RIGHT.
  Narrow everything and you produce honest documentation of a weak system.
  Strengthen everything and you relitigate settled design to save a sentence.
  Excuse everything and the exception list becomes the system.

  AND THE FIFTH LEVEL — THE AUDITOR'S OWN INSTRUMENT. The claims-must-be-observed
  rule was turned on the controller's own method mid-run: "my form-gate runs were
  safe" was EXAMINED rather than asserted (clean-tree porcelain check paired with
  every invocation, worktree shared with no other session, therefore no stash
  ever fired and no recorded result is suspect). A doctrine that never gets
  pointed at the instrument doing the auditing is a posture; this one was, before
  the fifth candidate could become a finding.

### LEDGER INTEGRITY AUDIT (controller, 2026-08-24) — the recovery map checked
### against git, programmatically rather than by eye

  The skill calls this ledger the recovery map and says the commits it names must
  exist in git even when context no longer remembers creating them. That claim
  had never been verified. It has now.
  RESULT: 20 commits on the branch since merge-base 002cb25. All 26 SHAs named in
  the ledger's 13 ranges RESOLVE — no phantom commits, no typos. 12 completion
  lines. 18 of 20 commits fall inside a claimed completion range.
  TWO COMMITS ARE UNCOVERED, and both are explainable:
   - `c418cf7` — Task 2d, landed and IN REVIEW. Expected; it gets its completion
     line when the review closes.
   - `aef25c1` — MY Part 3 / Task 22 amendment, a CONTROLLER commit no task
     claims, later reverted by 4a690cc (which IS covered, inside Task 3's range).
  ONE CHAIN DISCONTINUITY, at exactly that point: Task 1 completes at 8dbf87f,
  and Task 2's recorded range begins at aef25c1 rather than 8dbf87f. That is
  CORRECT — aef25c1 was the true BASE when Task 2 dispatched, because I committed
  the amendment between the two tasks — but a machine walking the chain sees a
  gap, and a post-compaction reader could reasonably ask why Task 2's base is not
  Task 1's head. Recording the answer here so that question resolves without
  re-deriving it: the branch carries THREE controller commits that no task
  claims — aef25c1 (Part 3 amendment, superseded), 4a690cc (its revert) and
  a3db464 (mdformat normalization). The latter two sit INSIDE Task 3's range and
  were flagged there at the time; aef25c1 sits between Task 1 and Task 2 and is
  the sole break in an otherwise contiguous chain from 002cb25 to c8cac73.
  METHOD NOTE, in keeping with the run's own doctrine: this was checked by
  resolving every SHA and walking the ranges in code, not by reading the log and
  judging it consistent. Eyeballing a chain is precisely the "reasoned, not
  observed" failure the plan has caught four times elsewhere.

TASK 2e STEP 2 PRE-CHECK — A DESTRUCTIVE DEFECT CAUGHT BEFORE DISPATCH.
  Step 2 reads "add knowledge_harness/templates/vault to mdformat's paths and
  canonicalize the 11 template files — five change". I dry-ran the change against
  every file rather than trusting that description. FIVE change, as the plan
  says, but they are not alike:
   - AGENTS.md, system/glossary.md, system/templates/daily.md,
     system/templates/literature.md — one to three BLANK LINES each. Pure
     canonicalization, harmless.
   - index.md — mdformat ESCAPES EVERY OBSIDIAN WIKILINK:
       `[[literatures/]]`                    -> `\[[literatures/]\]`
       `![[system/bases/trust-tier.base]]`   -> `!\[[system/bases/trust-tier.base]\]`
     mdformat is CommonMark; wikilinks are not, so it escapes the brackets. That
     would kill ALL SIX folder links and BOTH Base embeds Task 2b just landed —
     in a file that ships VERBATIM into every user vault. Executed as written,
     Step 2 would have shipped a broken index to every future vault.
  RULING (author, 2026-08-24) — THE CRITERION IS DIALECT OWNERSHIP, NOT A
  FILENAME LIST, and it comes from the one-form-owner matrix this lane was built
  on. Vault-dialect markdown belongs to its SOLE WRITER, not to mdformat, whose
  jurisdiction is CommonMark. Wikilinks are one dialect marker; %%hk-managed%%
  comments and Base embeds are others. index.md is excluded NOT because of its
  name but because it is a vault-dialect file that a CommonMark formatter by
  definition corrupts — "that's not an exception to the rule, it's a different
  owner". Author's note on why this framing matters: it survives the trio's third
  failure mode, because AN EXCEPTION LIST GROWS BY FILENAMES; AN OWNERSHIP
  BOUNDARY DOES NOT GROW AT ALL.
  DISPATCH DELIVERABLES: exclude index.md; canonicalize the other four (the
  dry-run proves them pure-CommonMark-safe today); and the path-list comment
  states the CRITERION — "vault-dialect templates (wikilinks, managed-region
  markers, Base embeds) belong to their sole writer, not the CommonMark owner" —
  so the next dialect-bearing template excludes itself BY RULE rather than by
  incident.
  RIDER, AND I AM CORRECTING ITS SCOPE: the author named literature.md as
  dialect-adjacent because it carries %% markers. I checked — THREE of the four
  canonicalized files do: literature.md, system/glossary.md AND AGENTS.md.
  Verified empirically that mdformat leaves the markers intact today
  (literature.md's `%%hk-managed%%` / `%%/hk-managed%%` survive the probe
  unchanged), so canonicalizing all four is safe now. But the mdformat
  upgrade-protocol comment Step 4 already adds must name ALL THREE, not just
  literature.md — an upgrade that starts touching `%%` sequences is exactly the
  drift that protocol exists to catch, and a protocol watching one of three files
  would miss it two times in three.

  SIXTH LEDGER LEVEL — THE PLAN'S REMEDY AUDITED, NOT JUST ITS CLAIMS.
  Every earlier level examined a CLAIM (implementer, planner, CI comment block,
  git hook, the controller's own instrument). This one examined a PROPOSED FIX:
  Step 2 shipped as "canonicalize the templates" and would have corrupted every
  folder link and both Base embeds in every future vault. It was caught because
  the change was RUN before the plan's description of it was trusted.

### THE THROUGH-LINE, for the landing report — one mechanism, thirteen instances

  Every catch in this run has the same shape, whatever level it sat at: THE
  ARTIFACT WAS DESCRIBED FROM MEMORY OR REASONING INSTEAD OF DERIVED FROM THE
  THING ITSELF. The remedy was always identical and always cheap: go look.
   - a sweep's coverage REASONED, never measured over the corpus (4 of 46)
   - a grep transcript RESTATED, never re-run (printed "(no output)"; three hits)
   - a citation RESTATED from context that the source never made
   - a deviation ledger RESTATED, never enumerated (six declared, seven shipped)
   - a pin justification SEARCHED FOR THE WRONG THING (a dedicated pin file,
     when the question was whether any test reads the file)
   - a residual bound DERIVED FROM ITS OWN PROSE, not from the return condition
   - a threshold INVENTED because no tree source existed to derive it from
   - an enforcement clause ASSERTED TWICE without checking CLOSING_BY_SURFACE
   - a CI gate's comment block REASONED about a gate that has never executed
   - a git hook REPORTING SUCCESS on its own unchecked error path
   - a recovery map I would have EYEBALLED rather than walked in code
   - a proposed remedy DESCRIBED ("canonicalize the templates") rather than run —
     it would have shipped a broken index into every future vault
   - a rider NAMED FROM THE DISCUSSION rather than grepped (one file of three)
  Author's own diagnosis of the last one is the cleanest statement of the whole
  pattern: "I named the file I'd seen discussed instead of grepping the set."
  It landed on implementers six times, on the planner four, on infrastructure
  twice, and on the controller once. No level was exempt, and the same one-line
  fix answered all of them.
  AUTHOR'S CLOSING FRAME (2026-08-24), the thesis in final form: the harness
  exists because knowledge work fabricates in exactly this way — describing
  sources from memory instead of deriving claims from the artifact — and the
  process building it committed the same error thirteen times at four levels
  before the discipline held. "GO LOOK" IS THE IRON LAW GENERALIZED PAST
  CITATIONS: no claim without its artifact, whether that artifact is a paper, a
  coverage report, a hook's error path, or a rider's file count. The system and
  its construction converged on one rule from opposite directions, which is about
  the strongest evidence a rule gets.

PYPROJECT/CONFIG AUDIT FOLDED IN (author, 2026-08-24; origin/main 4791a67).
Two dead facts already fixed on main outside the plan: the stale print count, and
the defusedxml boundary scope (its ruling-anchor marker re-pinned at c543e48).
  PART 4, OUT OF SCOPE — recorded so nothing is rediscovered:
  24c STEP 4b: `addopts = ["--strict-markers"]`, verified safe against the mark
    inventory. The consequence that earns it is FINDING-SHAPED: a typo'd
    `live_net` mark today runs SILENTLY and makes real external API calls during
    an offline run. Note the xdist ruling forbids `-n` in addopts, not addopts.
  24d STEP 4c, four items: (a) version single-sourced via `dynamic` reading
    `__version__` — eliminates the only untested copy; (b) pytest pins EXACT per
    lane doctrine while `pypdf>=4` keeps its FLOOR with a comment — a
    feature-detected user extra, where floors are the design, and the DISTINCTION
    is the point; (c) mypy gains `python_version = "3.11"` (ruff's "the two move
    together" comment becomes three) and its `files` grows to `scripts/` and
    `hooks/` — THE GATE LOGIC ITSELF IS TYPE-UNCHECKED TODAY; if the new surface
    yields non-trivial errors, REPORT rather than land; (d) `[project]` gains
    SPDX license + urls matching plugin.json, coupled with the setuptools>=77
    build-floor bump in the same commit.

  IN SCOPE — TASK 4 GAINS THE XML ANNOTATION. Task 4 is COMPLETE (8e7b136,
  review clean) and buried under many commits, so like the Task 9 addendum this
  lands as a FOLLOW-UP COMMIT, not a rebase. Decided text, to be added to the
  vendoring-note section verbatim:
    "`arxiv_atom.py`/`jats_to_text.py` parse network XML via stdlib ElementTree
     by upstream's choice — not XXE (no entity expansion); residual
     expansion-DoS rides the runtime's libexpat; kept frozen per the vendor rule,
     noted in the K-Dense upstream queue beside the jats arg-type finding."
  THIS IS THE THIRD DIRECTION AGAIN, third instance in the plan: the vendored
  scripts' stdlib ElementTree STAYS because the vendor rule is correct — so the
  deliverable is stating the exception with its MEASURED risk, not fixing the fork.
  THE K-DENSE UPSTREAM QUEUE NOW CARRIES TWO FINDINGS: the jats_to_text.py:291
  arg-type defect (from Task 2e Step 1) and this XML note. Both ready-to-file,
  both landing at the next re-vendor, ZERO hand edits to the fork — "two findings,
  one upstream conversation".

  TWO PENDING ADDENDA TO COMPLETED TASKS, both free-floating in the queue:
   - Task 9 addendum: summary() also emits `oldest_age_days` (no boolean, no
     threshold — ruled). Touches inbox.py + tests/test_inbox.py.
   - Task 4 addendum: the XML annotation above. Touches
     skills/find-sources/SKILL.md + its pin.
  They collide with each other not at all, and with nothing in flight. Plan: one
  dispatch, TWO commits — the plan's one-commit-per-task rule means two addenda
  to two different tasks get two commits, not one merged change.
  TWO FRAMINGS THE AUTHOR ASKED BE KEPT:
   - On the XML annotation's wording: a NARROW TRUE CLAIM OUTLIVES A BROAD SCARY
     ONE. "Not XXE; residual expansion-DoS rides libexpat" survives scrutiny where
     "we parse untrusted XML with ElementTree" would decay into folklore. This is
     the four-state ethos applied to RISK PROSE — the same reason UNREACHABLE is
     not UNMATCHED.
   - For 24d(c)'s runner: it is A DISCOVERY TASK WEARING A CONFIG-BUMP'S CLOTHES.
     The report-don't-land instruction exists because NOBODY HAS EVER LOOKED AT
     scripts/ AND hooks/ THROUGH MYPY'S EYES. Budget accordingly; a clean run
     would be the surprise, not the expectation.

BOTH ADDENDA DISPATCHED (one implementer, TWO commits) while Task 2d's review
runs. Safe to overlap: the review is READ-ONLY and reads templates/, scaffold.py,
test_templates.py and test_scaffold.py; the addenda touch inbox.py +
tests/test_inbox.py and skills/find-sources/SKILL.md + its pin. Disjoint, and no
other implementer is live.
  PRE-CHECK THAT SHAPED THE DISPATCH — A CALENDAR-ROT TRAP in addendum 1.
  `oldest_age_days` needs a clock. inbox.py:305 already establishes the
  convention (`datetime.datetime.now(datetime.UTC).date()`) and :172 parses with
  `date.fromisoformat`. But Task 9's existing tests use FIXED dates
  (2026-08-01, 2026-08-16), so an assertion like `oldest_age_days == 23` would
  pass today and FAIL TOMORROW — a test that rots on a calendar and would be
  blamed on something else weeks later. The dispatch names the trap and the
  cleanest escape: write the fixture at today-minus-N and assert N.
  Also asked to decide and STATE the `None` case (no unacknowledged entries).
  Also verified and carried: scaffold._inbox_probe computes NO age today, so it
  is deliberately NOT rewired here; and summary()'s SKIPPED filter already gives
  `oldest_age_days` the right basis for free — confirm, do not re-implement.
  Addendum 2 carries the decided XML text verbatim plus the reason its PRECISION
  is the point (narrow true claim over broad scary one), and a hard fence around
  skills/find-sources/scripts/ and references/ — the fork is frozen; the
  deliverable is the annotation, never a fix.
Task 2d: review returned — spec COMPLIANT, quality NEEDS FIXES. Review file:
  .superpowers/sdd/2026-08-22-post-q-batch/task-2d-review.md
  THE RISKIEST UNKNOWN WAS ANSWERED EMPIRICALLY: EditorConfig's `dir/**` DOES
  match files directly inside `dir` — verified against BOTH reference cores on
  the shipped file, with the four mandated surfaces matching and
  projects/notes.md, index.md, log.md matching nothing. The dotless packaging
  pattern was verified END TO END with a real WHEEL BUILD plus a live
  scaffold_vault() run: all three assets package and land renamed. And
  EXPECTED_CREATED is correct rather than merely green — test_scaffold.py:75
  compares against `sorted(created)` as an ORDERED list, so the three insertions
  sitting in true byte-sort position is pinned behaviour.
  ONE CONFIRMED IMPORTANT, plan-mandated: `projects/*/search-log.md` is protected
  by lints.py:_is_append_only_path but covered by NONE of the three ignore files.
  Controller verified the source directly — _is_append_only_path (lints.py:109)
  names THREE durable-append surfaces and its own docstring says so; the ignore
  files carry two of them. Consequence correctly scoped by the reviewer: append-
  only is NOT in CLOSING_BY_SURFACE, so a prettier run yields a NON-BLOCKING,
  recoverable drift finding, not a failed hook.
  RULING (author, 2026-08-24) — ADD IT AND ANCHOR EVERYTHING. Two independent
  reasons, each sufficient:
   1. THE SCOPE AUTHORITY IS `_is_append_only_path`, NOT THE BRIEF. The author's
      own words: "my brief's four-surface list was the planner describing from
      memory what lints.py already states precisely (the through-line's shape,
      again, mine again)." projects/ being user-owned does not exempt the one
      machine-written file inside it — search-log.md has a sole CLI writer and an
      append-only contract, and the slice's Phase 3 is about to write real search
      logs. A formatter trimming one mid-slice manufactures exactly the
      drift-finding noise the precision measurement does not need.
   2. THE ANCHORING DISAGREEMENT IS THREE FILES QUIETLY MEANING DIFFERENT THINGS.
      .editorconfig says root `log/`; the other two say "any directory named log
      at ANY DEPTH" — which would silently shield a user's projects/myproj/log/
      from formatting, or mis-scope a nested literatures/. One meaning, stated
      identically in all three; the anchored form is the correct one.
   RIDER: each ignore file gains a ONE-LINE POINTER naming
   lints.py:_is_append_only_path (plus the bibliography) as the SOURCE OF TRUTH.
   These are imperative path lists in three formats that cannot be made
   declarative, so the next-cheapest defence is every copy naming its master —
   the same move as 2e's exclusion-criterion comment. The list can still drift,
   but a reader checking it knows where the truth lives.
  FIX HELD, NOT DISPATCHED: c418cf7 is still branch tip, but the two-addenda
  implementer is LIVE and about to commit. Two implementers must never run
  concurrently — I flagged that hazard earlier in this run and am following it.
  2d's fix goes out the moment the addenda land, as a FOLLOW-UP COMMIT (not an
  amend, since the addenda commits will by then sit on top).
  FOLDING INTO THAT FIX (all cheap once the byte pin churns anyway):
   - the CONFIRMED commit-body errors in c418cf7: it cites the brief at a
     `docs/superpowers/sdd/...` path that EXISTS NOWHERE (controller re-verified
     via git ls-tree origin/main — only plans and specs live under
     docs/superpowers/), and calls igorshubovych/markdownlint-cli a FORK when it
     is the CANONICAL repo. The syntax claim it supports is correct, so no
     shipped file changes — but two false statements in a commit body is the
     14th instance of the through-line and the record must be corrected.
   - AGENTS.md:28 credits `.editorconfig` with keeping formatters OFF the
     surfaces, but EditorConfig has NO ignore primitive — it only disables two
     save-time behaviours. Wording imprecision rather than a false enforcement
     claim, and the reviewer says to fold it in if finding 1's fix is taken. It is.
   - the `root = true` rationale: the comment claims it stops ancestors diluting
     the overrides, but measurement shows closer-file precedence already
     guaranteed that. What root = true ACTUALLY blocks is ancestor-sourced
     charset/end_of_line. Keeping the line is right for a STRONGER reason than
     the comment gives — and this also resolves the implementer's disclosed
     unverified belief in its favour.
  DEFERRED (not folded — they need redesign, not a wording pass):
   - tests/test_templates.py:317's pin uses substring and aggregate assertions,
     so a commented-out or negated pattern, a deleted `root = true`, or lopsided
     property placement all keep it green.
   - the 20-line editorconfig header restates its unset-is-inert rationale
     near-verbatim at tests/test_templates.py:325-333; two copies will drift.
  DISPATCH REQUIREMENT for the held 2d fix, added after a controller check:
  THE ANCHORED PATTERNS MUST BE VERIFIED EMPIRICALLY, PER TOOL, BEFORE SHIPPING.
  `/literatures/` and `/log/` are the ruled form, but an anchor that a given tool
  does not honour matches NOTHING — which would silently convert partial
  protection into ZERO protection while every pin stays green. That is the same
  failure shape as 2e Step 2's wikilink escape: a change whose description sounds
  safe and whose effect is destructive, catchable only by running it.
  I could not run it myself: prettier and markdownlint-cli are not installed in
  this worktree, and npx-fetching them mid-run would be a network act against
  this repo's offline posture and outside anything the plan sanctions. The
  reviewer had them (it cites prettier 3.9.6 and markdownlint-cli 0.49.1), so the
  capability exists — it belongs to the implementer, whose job it is.
  The dispatch will require: for EACH of the three files, demonstrate that the
  anchored pattern actually excludes the intended paths AND that
  `projects/*/search-log.md` is genuinely covered — with the tool's own output,
  not by reading its documentation.
  Planner's share of the through-line count now stands at FIVE of fourteen.

BOTH ADDENDA LANDED: eff8d67 `feat: inbox summary emits oldest_age_days` and
  ebea360 `docs: find-sources vendoring note records the XML parsing boundary`.
  Suite 1576/7 baseline-equal after EACH commit; form gate 8/8 both times.
  Three disclosed concerns, all recorded rather than waved through:
   1. The age-math test carries a VANISHING-PROBABILITY UTC-midnight-straddle
      flake window — explicitly NOT calendar rot (the trap I flagged was
      avoided), left unhardened as a stated design choice. Review to judge.
   2. `oldest_age_days` has NO agent-facing consumer yet — correct per the brief,
      which scoped this to the emission plus one assertion. Worth carrying to the
      final review: a mechanism nothing reads is a mechanism nobody notices
      breaking.
   3. ADDENDUM 2'S THREE CLAUSES SHIPPED AS DECIDED TEXT, NOT INDEPENDENTLY
      RE-VERIFIED THIS SESSION. Honest disclosure, and precisely the shape this
      run keeps catching — so the review must verify them against the tree and
      the stdlib rather than accept them as decided. Specifically: "not XXE (no
      entity expansion)" and "residual expansion-DoS rides the runtime's
      libexpat" are technical claims about stdlib ElementTree, and there is a
      possible internal tension between the parenthetical "no entity expansion"
      and a residual EXPANSION-DoS. The natural reading is "no EXTERNAL entity
      expansion" (the XXE vector), which would make both clauses true and
      consistent — but that reading needs confirming, not assuming, because a
      false security claim is worse than a vague one.

Task 2d: fix round 2 DISPATCHED (implementer slot free now the addenda landed).
  Carries: the search-log addition; the anchoring with its PER-TOOL EMPIRICAL
  PROOF requirement; the source-of-truth pointer comments; and three record
  corrections (c418cf7's two false commit-body statements, corrected FORWARD
  since it is now buried; AGENTS.md's inaccurate credit to .editorconfig, which
  has no ignore primitive; and the root = true rationale, wrong reason for a
  right line). Two Minors explicitly deferred as redesign, so a byte-churning fix
  does not also quietly restructure assertions.
  Branch tip is ebea360, so the fix is a FOLLOW-UP COMMIT, not an amend.

HOLD CLEARANCE, RECORDED RETROACTIVELY (the author is right that it went
unrecorded at the moment it expired): Task 2d's fix was held ONLY because the
two-addenda implementer was live and two implementers must never run
concurrently. That reason expired when eff8d67 and ebea360 landed. I dispatched
the fix immediately on that clearance rather than waiting for instruction — so
the author's "dispatch it now" instruction describes work already in flight, not
work pending. Recording the clearance here so the sequence is legible from the
ledger alone: hold set at the 2d review's return, cleared by the addenda landing,
fix dispatched in the same turn as the clearance.
  ALREADY IN THAT DISPATCH: the search-log addition; the anchoring; the
  per-tool EMPIRICAL PROOF requirement as the acceptance bar; the source-of-truth
  pointer comments; and three record corrections including c418cf7's two false
  body statements corrected FORWARD.
  NOW ADDED by the author's ruling: the disproven `root = true` rationale must be
  fixed in BOTH places — the .editorconfig file AND its near-verbatim duplicate
  at tests/test_templates.py:325. I had deferred the duplication as "redesign,
  not a wording pass"; the author scopes it narrower and correctly — fixing a
  DISPROVEN RATIONALE in both copies is the wording pass, and leaving one copy
  stating a disproven reason would be the defect this run exists to catch.
  ALSO ADDED: two wires so `oldest_age_days` has a consumer — one line each in
  skills/project-flow/SKILL.md:25 and skills/setup-vault/SKILL.md:34, pins
  updated. Author's framing: "the fact shipped without the wire — my scope error,
  your fix." This closes the concern I raised at the addenda's landing, that a
  mechanism nothing reads is a mechanism nobody notices breaking.

MERGE SEQUENCING CORRECTION: the author instructs merging origin/main NOW at the
Part 1/Part 2 boundary. It CANNOT run while the 2d fix implementer is live —
merging moves the tree under a working agent, and its conflict sites (the plan
file, terminology §4.3/4.4) are files an implementer may be reading. The merge
goes immediately AFTER that fix lands, before anything from Part 2. Recording the
reason so the delay is not mistaken for drift.

### RECEIVED FINDINGS — independent review, 2026-08-24 (arrived from outside
### this ledger; recorded here as received, verbatim)

FINDING 6: "Checkbox contract dead. 133 unchecked / 3 checked at origin/main;
  the 3 are 8b's verify-only steps. 12 tasks done, zero boxes ticked. The plan's
  own claims-must-be-observed doctrine, unapplied to the plan."
  ACCEPTED WITHOUT QUALIFICATION. The plan opens by telling agentic workers the
  checkboxes are the tracking mechanism, twelve tasks completed, and I ticked
  nothing — I tracked in this ledger instead and never reconciled the two. That
  is the through-line's shape once more, and mine: the plan's own status surface
  described by a parallel record rather than derived from the artifact everyone
  else reads. ACTION: backfill the twelve completed tasks' boxes, tick henceforth.
  HELD until the 2d fix implementer lands — the plan file is also a merge conflict
  site, and editing it under a live agent is the hazard I have been enforcing.

FINDING 7: "Task 8b's verify never ran. Zero `Task 8b:` lines in progress.md.
  Content landed on main at d7fa91b; the owed verify is unscheduled."
  ACCEPTED. Task 8b is the dropped-ADR guard sentences, landed by the author
  session at d7fa91b and marked LANDED/VERIFY-ONLY in the plan — so it never
  entered my dispatch queue, and an owed verification with no owner is exactly
  how a task goes quietly unfinished.
  THE TWO-MINUTE VERIFY, scheduled into the next dispatch with its `Task 8b:`
  line: confirm skills/evidence-conventions/SKILL.md carries
   (a) the rewritten "The abstract said so." rationalization row, WITH the
       full-text-summary guard, and
   (b) the inline-provenance sentence at approximately line 16.
  BOTH PRESENT -> log the `Task 8b:` line, LAND NOTHING.
  EITHER ABSENT -> STOP AND REPORT. Do NOT re-add: the duplicate-row hazard is
  precisely why this task is verify-only.

### HANDOFF TO THE INDEPENDENT REVIEWER — a named target, not a hope

  The reviewer takes eff8d67 and ebea360; I dispatch nothing for them, and Part 2
  waits on eff8d67 clearing. One item must reach them EXPLICITLY, because a
  flagged-but-unrouted security claim is how findings die in transit:
  WHAT: commit ebea360 added an XML annotation to
  skills/find-sources/SKILL.md's vendoring-note section. Its implementer
  disclosed that the three clauses "shipped as DECIDED TEXT, NOT independently
  re-verified in this session".
  THE CLAIMS, verbatim: "`arxiv_atom.py`/`jats_to_text.py` parse network XML via
  stdlib ElementTree by upstream's choice — not XXE (no entity expansion);
  residual expansion-DoS rides the runtime's libexpat".
  THE SPECIFIC DOUBT: there is a possible internal tension between the
  parenthetical "no entity expansion" and a residual EXPANSION-DoS. The natural
  reading is "no EXTERNAL entity expansion" — the actual XXE vector — which would
  make both clauses true and mutually consistent. That reading needs CONFIRMING
  against stdlib ElementTree's real behaviour, not assuming.
  WHY IT MATTERS: this annotation's precision IS its purpose — it was written
  narrow on the explicit reasoning that a narrow true claim outlives a broad
  scary one. A false security claim is worse than a vague one, and this is the
  one paragraph in the file whose whole value is being exactly right.

### PROBE RESULT — the XML annotation's ambiguous clause, settled empirically
### (evidence FOR the independent reviewer; not a verdict on the commit, which
###  remains theirs)

  ATTRIBUTION, recorded at the author's own instruction: the ambiguous clause is
  the AUTHOR's. They drafted the annotation in the Task 4 fold, and
  "(no entity expansion)" was their compression of a distinction that does not
  survive compressing. They stated their prior explicitly as HYPOTHESIS, NOT
  VERDICT — "confirming from memory is the through-line sin" — and supplied two
  checkable sources rather than asking to be believed.
  I ran their probe design. Pure stdlib, offline, no network, no dependency;
  Python 3.12.3 in this worktree's venv. Reproducible in ~10 lines.
  RESULT 1 — INTERNAL entities ARE expanded. A 3-level document expanded 4
    characters to 36. That is exactly the billion-laughs class.
  RESULT 2 — EXTERNAL entities are NOT resolved. `<!ENTITY xxe SYSTEM
    "file:///etc/hostname">` raised `ParseError: undefined entity &xxe;`.
  THEREFORE, against the shipped text in ebea360:
   - "not XXE"                       -> TRUE. External entities are refused.
   - "(no entity expansion)"         -> FALSE AS WRITTEN. Internal entities are
                                        expanded, demonstrably.
   - "residual expansion-DoS rides
      the runtime's libexpat"        -> TRUE, and internal expansion is precisely
                                        the mechanism that makes it so.
  The author's predicted one-word fix is confirmed correct: "no EXTERNAL entity
  expansion". With that word, all three clauses become true and mutually
  consistent — the residual DoS is no longer in tension with the parenthetical,
  because internal expansion is what carries it.
  THE PLANNER'S COUNT GOES UP ONE, to six of fifteen, as the author said it
  should if the doubt confirmed.
  WHAT THIS COST vs WHAT IT WOULD HAVE COST: the doubt was routed instead of
  shipped, so the correction is one word in a comment. Had the disclosure not
  been made — "shipped as decided text, not independently re-verified" — a false
  security claim would have shipped into every user vault inside the one
  paragraph whose entire purpose is being exactly right.
  SOURCE FIXED BY THE AUTHOR (origin/main 750d4c7): the plan's Task 4 fold now
  reads "not XXE (no EXTERNAL entity expansion — internal entities DO expand,
  probe-verified 2026-08-24, which is exactly the class the next clause hedges)".
  The correction carries its probe citation INLINE, so the next reader of Task 4
  inherits the verified form rather than the compressed one. The shipped
  SKILL.md copy in ebea360 still carries the false clause and waits on the
  reviewer's verdict, then rides the follow-up commit family with this as its
  reference text.
  NOTE FOR THE MERGE: origin/main has moved f6b7788 -> 750d4c7, and f6b7788 is
  where Part 4 split out into Plan W — so the plan-file conflict at merge time is
  smaller than it was (Part 4's tasks left this document) but now also carries
  this annotation correction. Both are wanted.
  THE INCIDENT'S ONE-LINE RECORD, as the author framed it: a false security claim
  was ONE DISCLOSURE away from shipping into every user vault, inside the
  paragraph whose entire purpose is being exactly right — and the disclosure cost
  the implementer a sentence. That asymmetry is the argument for the disclosure
  discipline, priced in the currency that matters.
  AND THE METHOD NOTE THE AUTHOR ADDED, which generalizes past this incident:
  their prior was RIGHT and still needed the probe, because being right from
  memory does not retroactively license memory. The probe is not a tax on
  uncertainty; it is what makes a correct belief citable.

### BOUNDARY MERGE LANDED — 3a6d0cd, plus d6c5ccd and 32acfe2

  Merge resolved per file and recorded in the commit body. Plan file taken from
  origin/main wholesale. terminology.md needed BOTH sides: origin/main pruned the
  §4.3/§4.4 registers while this branch had renamed the project skill (Task 1)
  and registered `not-imported` (Task 10). Resolved to their pruned structure,
  then re-applied both additions. CRITICAL: origin/main still carried the
  PRE-RENAME `project`, so taking their side wholesale would have SILENTLY
  REVERTED TASK 1. Both re-applications are mechanically proved, not eyeballed —
  test_config_validity asserts every REASON_CODES member appears in §4.4, and
  test_skill_contracts asserts every cited skill name resolves to a shipped
  directory; a wrong resolution of either fails the suite.
  The one-word XML fix was applied during the merge as routed.
  d6c5ccd: Plan W arrived from origin/main FAILING this repo's own markdown gate
  by one blank line. Normalized rather than left red.
  32acfe2: checkbox backfill, finding 6 — 38 boxes across the twelve completed
  tasks; 41 checked total including 8b's three pre-existing. 72 remain rather
  than 95 because Part 4 split into Plan W after the finding was written.
  TICKING HENCEFORTH as each review closes, not in arrears.
  POST-MERGE STATE: suite 1554 passed / 7 skipped, form gate 8/8, tree clean.
  The count fell from 1576 because origin/main CONSOLIDATED per-template byte
  pins into one canonical-content test. Coverage is not lost — I verified
  directly that the consolidated pin still carries this branch's content: the
  index Base embeds WITH their block-rendering blank lines, and the AGENTS.md
  integrity preamble (split across string literals, which is why an
  exact-sentence grep found nothing).

### Task 8b: VERIFY RAN — both criteria PRESENT, nothing landed (finding 7 closed)

  (a) the rewritten "The abstract said so." row WITH the full-text guard —
      present at origin/main's skills/evidence-conventions/SKILL.md:97.
  (b) the inline-provenance sentence — present at :16 ("whatever is not on the
      line does not travel with it, so attribution held in frontmatter survives
      exactly one hop").
  METHOD NOTE, recorded because it nearly produced a false finding: my first pass
  grepped THIS BRANCH (which predates d7fa91b) and then grepped for the WORD
  "provenance" — a sentence that conveys provenance without using the word.
  Wrong tree, then wrong search term. Two wrong instruments in one check, caught
  only by looking again before reporting. A false "absent" here would have sent
  someone to re-add content that is already there — precisely the duplicate-row
  hazard that makes this task verify-only.

### BLOCKER SURFACED TO THE ORCHESTRATOR — the polish-ledger entry

  The record-immutability hook is `git diff --name-status --diff-filter=MRD
  origin/main...HEAD -- research analysis docs/adr`, failing on ANY hit. So any
  modify, rename or delete under research/ from a branch turns the gate red —
  AND AN APPEND IS STILL AN `M`. There is no append-shaped escape: those files
  are immutable from branches and editable only on main directly.
  So the instructed pointer entry in
  research/validation-slice/2026-08-22-skills-layer-audit.md CANNOT be written
  from here. Routed to the orchestrator as a RECORDS-CONTRACT question, not an
  implementation one — I did not choose among the options (author writes it on
  main / it waits for the merge / the hook gains an exception).
  CONTENT IS READY either way: the 33 deferred minors, plus the reviewer's three
  new ones — negative `oldest_age_days` reachable via future-dated findings
  (REPRODUCED at -26428), the docstring zero-case untested, and __main__.py:761's
  CLI JSON entirely unpinned (named individually so the polish pass sizes it as
  test-writing) — and the refuted pair (crash-on-bad-date, mixed-precision min)
  recorded as NEGATIVE KNOWLEDGE so nobody re-derives it.
  NOTE: the negative-age defect is in code that landed this session (eff8d67).
  It is routed to polish by the reviewer's own triage, not dismissed.

BLOCKER RESOLVED by the orchestrator: the polish-ledger entry lands ON MAIN,
through them — the established channel, and why the hook never fired on prior
appends. No hook exception (weakening record-immutability for convenience is the
wrong trade) and no waiting on the merge (findings rot in transit). Their note
kept with the entry: a living ledger inside the append-only zone is a CATEGORY
TENSION the hook just made visible; it resolves when the polish pass extracts the
list into its own plan, not by loosening the gate.
  I SENT AN ENUMERATION, NOT A POINTER, and flagged the change of shape for
  override. Reason: a pointer would DANGLE. The 33 live only in this git-ignored
  ledger, which the SDD skill instructs me to `rm -rf` when the final review
  clears — and the reviewer's own report cites the same path, inheriting the same
  dangling reference. Enumerating IS the preservation act, and one line each with
  file:line is the form a triage pass can size.
  COUNTS DERIVED, NOT RESTATED: my ledger greps to 33 across 12 tasks, matching
  the reviewer's independent count; plus 2 deferred from 2d's own review, plus
  their 3 new = 38 items sent.
  The three new ones are recorded with their weight: `oldest_age_days` goes
  NEGATIVE on future-dated findings (reproduced at -26428) in code that landed
  THIS SESSION (eff8d67); the docstring zero-case is untested; and
  __main__.py:761's CLI JSON is ENTIRELY UNPINNED — that last one named
  individually at the reviewer's instruction so the polish pass sizes it as
  test-writing rather than a one-liner.
  NEGATIVE KNOWLEDGE preserved so it is not re-derived: crash-on-bad-date and
  mixed-precision `min` were both investigated and REFUTED.
XML WORDING RULED: keep mine. The comment doctrine beats byte-alignment —
  provenance (probe-verified, the date) belongs in the commit body, which is
  where it is; the plan text carries the date because plans are decision records
  and skill comments are not. Sentence-case stands.
  ENTRY LANDED on main at 45c5e26 (verbatim, form-owner pass applied, pathspec
  commit, pushed). Shape correction approved and recorded in that commit body.

### SUPERSESSION NOTE — where the deferred-minor list actually lives

  The independent review's report
  (research/validation-slice/2026-08-24-post-q-batch-review.md) cites this file
  at its line 159, running `grep -c "minor (deferred)" progress.md` against
  `.superpowers/sdd/2026-08-22-post-q-batch/progress.md`. THAT PATH IS
  GIT-IGNORED SDD SCRATCH AND IS SCHEDULED FOR `rm -rf` when the final
  whole-branch review clears — so the citation dies with the workspace.
  THE DURABLE SUCCESSOR IS THE POLISH-LEDGER ENUMERATION at
  research/validation-slice/2026-08-22-skills-layer-audit.md's polish-pass
  section, landed on main at 45c5e26: all 38 items with file:line each
  (33 from this ledger + 2 from Task 2d's review + 3 from the independent
  review), plus the refuted pair recorded as negative knowledge.
  A post-rm-rf reader of the review's line 159 should go there. Recorded at the
  orchestrator's request, and it is the right ask — a citation whose target is
  scheduled for deletion is a dangling reference that has not dangled YET, which
  is the hardest kind to notice.

Task 2d: fix round 2 re-review — ALL ADDRESSED, no new breakage. The re-reviewer
  did not accept the anchoring proof, it REPRODUCED it: built its own fixture
  vault with real surfaces, nested same-named decoys and a control, ran the same
  cached prettier 3.9.6 and markdownlint-cli 0.49.1 (confirming both still at the
  cited npx paths), and got the same result — five real surfaces silently
  skipped, only the two decoys and the control flagged. It then REVERTED to the
  unanchored form and reproduced the bug exactly as claimed.
  It also went PAST the implementer's disclosure: rather than accept "prettier
  does not read those two properties", it read prettier's bundled resolver source
  (`editorConfigToPrettier()` in the inlined editorconfig-to-prettier.js) and
  confirmed CATEGORICALLY that it destructures only indent_style, indent_size,
  tab_width, max_line_length, quote_type and end_of_line — so
  insert_final_newline and trim_trailing_whitespace are provably never mapped.
  Verdict on the disclosure: accurate and if anything UNDERSTATED in the
  implementer's favour.
  Confirmed the root = true correction landed in BOTH places, and that the
  upstream test consolidation left no restatement of the disproven rationale.
  Confirmed c418cf7 is an untouched ancestor (git merge-base --is-ancestor), so
  the record correction is genuinely forward.
  OUT-OF-SCOPE OBSERVATION, correctly NOT raised as a finding: root `log.md` is
  named machine-written in the preamble but appears in no ignore file — because
  okf.regenerate_log() REWRITES IT WHOLESALE, making it a regenerated surface
  rather than a durable-append one, correctly outside _is_append_only_path under
  the author's own ruling that the function is the scope authority.
Task 2d: complete (commits c8cac73..89fe2fe, review clean after 2 fix rounds,
  2 minors deferred). Ticked at b1d5f17 — 3 boxes, at review close.

PART 1 IS COMPLETE except Tasks 11, 12, 13. Fourteen tasks done: 1, 2, 2b, 2c,
2d, 3, 4, 5, 6, 7, 8, 9, 10, plus the two addenda and Task 8b's verify.

Task 14: BASE = b1d5f17. PART 2 OPENS. Implementer dispatched (sonnet, TDD).
  PRE-CHECK FINDINGS CARRIED INTO THE DISPATCH:
   - checks.py:914 `_rw_date` (brief says ~910; minimal drift) is exactly the
     fromisoformat-only shape described.
   - checks.py:8 has `from datetime import date as _date` and NO `_datetime`
     alias — the brief anticipated this; confirmed absent.
   - verify.py:986's notice_lookup line is exact.
   - THE BRIEF POINTS AT THE WRONG FILE FOR STEP 4. It says "locate the existing
     summary emission in verify.py" — but verify.py HAS NO PRINT CALLS AT ALL.
     My own `grep -c "print("` returned 3, and all three were the substring
     inside `_notice_fingerprint(` — a false positive I caught only by printing
     the matched lines. (My instrument, wrong again; caught before it became a
     dispatch instruction.) The real emission is cmd_verify in __main__.py:405-421.
     So the task splits: DETECTION is knowable at verify.py:986 where the brief
     points, EMISSION can only happen in cmd_verify. The implementer must choose
     deliberately and say which — and the stdout test therefore belongs in
     tests/test_verify_cli.py, not the tests/test_verify.py the brief names.
   - HARD CONSTRAINT restated: the absence line is STDOUT ONLY, never a
     review-queue record — no reason code, no inbox entry. The brief cites the
     SKIPPED-counting lesson: an entry nobody needs to acknowledge manufactures
     rubber-stamp pressure.
   - The arming ruling is to be RECORDED in the commit body, not implemented as
     a default. No default-on; fetching the RW CSV stays a deliberate network
     and license act.

### BOUNDARY SHA-WALK RESPONSE (independent reviewer, ca0281d — 27/9)

  THE FIVE MISSING COMPLETION LINES. The walk is right: the recovery map's
  contract runs both ways, and five commits had no completion line. Written now.
  2e23c40 and 89fe2fe were absent from this file ENTIRELY (grep 0) — they landed
  while I was mid-merge and I never came back for them. Writing them:

Task 2d: complete (commits c8cac73..c418cf7, first pass) — formatter ignore
  files shipped with the scaffold via the dotless template pattern; AGENTS.md
  scope line corrected to the two model-invocable guards.
Task 9 addendum: complete (commit eff8d67) — inbox.summary() emits
  oldest_age_days. No boolean, no threshold: the withdrawn `aging:` flag would
  have made an invented number the tree's first Whittaker constant.
Task 4 addendum: complete (commit ebea360) — find-sources vendoring note records
  the XML parsing boundary. Its clause was later corrected to "no EXTERNAL
  entity expansion" after a stdlib probe; see the probe result above.
Task 2d: complete (commit 2e23c40, fix round 2 part 1) — search-log surface
  added to all three ignore files and the patterns anchored, with per-tool
  empirical proof and a positive control.
Task 2d: complete (commit 89fe2fe, fix round 2 part 2) — oldest_age_days wired
  into project-flow and setup-vault reporting, both pins moved in the same commit.

Task 8b: complete (verify-only, content landed on main at d7fa91b) — VERIFY RAN,
  BOTH CRITERIA PRESENT, NOTHING LANDED. (a) the rewritten "The abstract said
  so." row with the full-text guard, at evidence-conventions/SKILL.md:97; (b) the
  inline-provenance sentence at :16. Checked against origin/main because this
  branch predated d7fa91b. The walk is right that the verify ran and reported but
  this line never landed — the report existed only in my message to the author,
  which is exactly the gap the `Task 8b:` convention exists to close.

  CHECKBOX COUNT — BOTH NUMBERS RECONCILED, neither was simply right.
  My backfill commit said 72 unchecked; the walk says 71 at tip; I measure 69 at
  tip. All three are explained by ONE line: the plan's header at :3 is prose
  documenting the syntax ("Steps use checkbox (`- [ ]`) syntax for tracking") and
  is NOT a checkbox. Counting it inflates every total by one.
  VERIFIED NUMBERS, method stated: strict `grep -c -- "- [ ]"` counts the header
  literal; anchored `grep -cE "^\s*- \[ \]"` does not.
    - real checkboxes at 32acfe2 (the backfill commit): 71 unchecked  <- the
      walk's number, correct FOR THAT COMMIT
    - real checkboxes at tip b1d5f17: 68 unchecked, 44 checked  <- 2d's three
      boxes ticked since
  So my "72" over-counted by one, and the walk's "71" is right about the -1 but
  attributes it to tip rather than to the backfill commit. The 38-box backfill
  itself is exact and unaffected.

  VERIFIED AND CLOSED by the walk, recorded in the closed column:
   - the 38-box backfill: exact.
   - the XML clause confirmed at find-sources/SKILL.md:23 — Important discharged.
   - the Task 1 rename intact at terminology.md:125 — the wholesale-theirs hazard
     was real and the walk independently confirms it was avoided.
   - 2d's Important closed across all three ignore files, anchoring verified.
   - four commits structurally unclaimable and correctly so: the merge, the form
     pass, the backfill, and the explained controller amendment. No action.
  STAYS OPEN BY DESIGN: the .editorconfig glob-only residual. Carried to Part 2's
  boundary for a TOOL-RUN check — not closed on reasoning, which is the right
  call given no offline EditorConfig conformance tool exists on this machine.
  PLANNER COUNT -> 7. The author claims the Task 14 brief defect: "locate the
  emission in verify.py" named the file FROM MEMORY. The emission is cmd_verify
  at __main__.py:405-421. Same through-line shape, seventh planner instance.
  INSTRUMENT LESSON, recorded because it will recur: A GREP COUNT IS NOT A CALL
  COUNT. `grep -c "print("` in verify.py returned 3 and the file has ZERO print
  calls — all three hits were the substring inside `_notice_fingerprint(`. The
  count looked like evidence and was an artefact of the pattern. Printing the
  matched LINES, not trusting the count, is what caught it. This joins the
  wrong-instrument set: wrong tree (8b first pass), wrong search term (8b
  second pass, "provenance" for a sentence conveying it without the word), wrong
  pattern (this one), and the two exact-sentence greps that missed content split
  across string literals.
  SHAPE OF THE MISS, recorded as written: "recording the REASONING" does not
  discharge "recording the LINE" — a post-compaction reader greps. The Task 8b
  instance nested inside it is the purest small form: work done, evidence
  produced, record written only in a message to the author.
  .EDITORCONFIG RULING STANDS: proxy-verification through an adjacent tool's
  resolver reads as evidence and is not. Waits for a real conformance run at
  Part 2's boundary.
  Orchestrator: nothing further. PART 2 IS MINE.

Task 14: implementer DONE (commit a53a48b; __main__.py, checks.py,
  tests/test_checks.py, tests/test_verify_cli.py — 4 files, +70/-2). Suite
  1557/7 (baseline 1554 + 3 new tests); form gate 8/8; 3 tests RED-confirmed
  then GREEN.
  DESIGN DECISION, made deliberately and justified concretely rather than by
  preference: detection AND emission both live in cmd_verify, checking
  args.rw_csv directly; verify.py untouched. Stated reasons — verify.py has no
  print calls, cmd_verify already holds the same value, and routing through the
  report would WIDEN the outcomes/counts report contract that several tests
  monkeypatch as a LITERAL DICT. The review is told to verify that last claim
  specifically: it is a good reason if true and a rationalization if not.
  The stdout test went to tests/test_verify_cli.py as the dispatch resolved,
  not the tests/test_verify.py the brief's Files line names.
  DISCLOSED SUPPRESSION: the brief's own _rw_date snippet trips ruff DTZ007;
  resolved with a noqa at checks.py:935 on the grounds that a bare calendar
  date has no timezone to apply. Routed to review rather than accepted — a noqa
  is a CLAIM that a rule does not apply, and this run's doctrine says claims get
  checked. The review is asked whether the claim holds and whether the comment
  states the CONSTRAINT rather than merely asserting the exemption.
Task 14: review dispatched over b1d5f17..a53a48b. Hard constraint flagged as
  Critical-if-violated: the absence path must file NOTHING to the inbox — no
  reason code, no finding, no Outcome that could reach the queue. Also asked to
  confirm that 13/45/2023 0:00 still returns the INVALID sentinel: well-formed
  in SHAPE but an invalid date, and the case a loose implementation coerces.

Task 14: review returned — spec COMPLIANT, quality NEEDS FIXES.
  BOTH IMPLEMENTER JUDGMENT CALLS UPHELD AFTER VERIFICATION, not accepted:
   - the detection/emission reasoning is TRUE. The reviewer found the five
     hand-written two-key report literals in tests/test_verify_cli.py that a
     widened report contract would break, and confirmed publish.py discards the
     report entirely. Good reason, not rationalization.
   - the noqa DTZ007 is line-scoped with a reason, and correctly preferred over
     widening the project's deliberate DTZ lint configuration.
  Hard inbox constraint holds STRUCTURALLY: the emission is a bare print after
  verify_state returns, so it can never become an Outcome or a queue entry.
  13/45/2023 0:00 provably cannot be coerced without turning the test red.
  Cannot-verify closed by controller at a53a48b: suite 1557/7, form gate 8/8,
  tree clean.
  THE REVIEWER CORRECTED ITS OWN LENS: the spec lens claimed the commit body
  "already records it verbatim"; grepping a53a48b showed it does not. Recorded
  because a synthesis that overrules its own inputs on evidence is the behaviour
  the multi-lens shape exists for.

Task 14: fix round 1/5 dispatched. One Important, three Minors.
  IMPORTANT, CONFIRMED — A CROSS-TASK INTERACTION. The new stdout line
  "update-notice: RW leg not run (no --rw-csv)" violates verify's OWN DOCUMENTED
  OUTPUT GRAMMAR at skills/verify-citations/SKILL.md:25/27, which says results
  are "RESULT check target — reason" grouped by "the second token on each line".
  Under that grammar the line parses as RESULT="update-notice:" and check
  id="RW" — a PHANTOM CHECK ID on the skill's own documented flagless
  invocation.
  TWO REASONS IT IS NOT IMPLEMENTER DRIFT: the line text is the BRIEF'S OWN
  example string, and Task 3's de-enumeration (d44452e) REMOVED the explicit
  check-id list that would have rejected a phantom RW. That is the coverage
  bound Task 3 disclosed at the time — its sweep guards validity, not
  under-enumeration — arriving as a real consequence two Parts later.
  FIX IS ONE SENTENCE in the skill's output section. Explicitly FORBIDDEN:
  reshaping the line into "SKIPPED update-notice ...", which would dress a
  non-result as a four-state result and re-enter the failure the brief forbids.
  The line is honest; the grammar never anticipated a non-result line.
  MINOR: the fix is pinned only at the private-helper level — nothing exercises
  load_rw_csv or check_rw_batch with a production-format RetractionDate, so a
  future re-filter to ISO at the loader would leave the new unit test green.
  One-line fix in an adjacent fixture CSV.
  MINOR: the SKIPPED-counting rationale lives in the code comment and test
  docstring rather than the commit body.
  THE REVIEWER CHALLENGED WHETHER THAT CONSTRAINT IS BINDING, having failed to
  find it in the batch plan's Global Constraints, AGENTS.md or docs/. Fair
  challenge, and I LOCATED IT: docs/superpowers/plans/2026-08-24-plan-w-quality-tail.md:39
  — "a comment states a constraint the code cannot show; provenance, history and
  correctness arguments belong to git log." It was absent from where they looked
  because it MOVED TO PLAN W when Part 4 split out. The doctrine holds; the
  challenge was right to make.
  MINOR: `not args.rw_csv` re-derives the arming predicate verify.py:986 owns.
  Verified equivalent today and the alternatives verifiably worse, so a POINTER
  COMMENT rather than a restructure — the same source-of-truth move used in 2d
  for lists that cannot be made declarative.

Task 14: fix round 1 landed — a53a48b AMENDED into 079c287 (still the sole task
  commit; no rebase). 6 files, +10/-15. Suite 1557/7 and form gate 8/8, both
  unchanged after the four edits.
  All four applied: (1) verify-citations/SKILL.md now documents that verify may
  print a NON-RESULT status line that must not be parsed as
  "RESULT check target — reason" nor grouped by check id; (2) the
  test_rw_csv_matches_both_identifiers_and_blocking_beats_warning fixture now
  pins a production-format date through load_rw_csv/check_rw_batch rather than
  only through the private _rw_date unit test; (3) the SKIPPED-counting
  rationale moved from code comment and test docstring into the commit body;
  (4) a one-line pointer comment at verify.py:986 naming cmd_verify as the
  mirroring consumer of the falsy-rw_csv predicate.
  CONTROLLER SPOT-CHECK before dispatching the re-review: the rationale is now
  present in 079c287's body (2 hits) and ABSENT from __main__.py (0 hits) — both
  directions, since a rationale duplicated in both places would be the defect
  unfixed rather than moved.
  The implementer used 2/2/2024 0:00 rather than the reviewer's suggested
  1/2/2023 0:00 — equivalent in shape, and the re-review is asked to confirm it
  genuinely flows through the loader and would fail under an ISO re-filter.
Task 14: fix round 1 re-review dispatched over a53a48b..079c287. Two checks
  weighted highest: (a) does the SKILL.md sentence actually COUNTERMAND the
  grouping instruction at :25/:27, or does it merely mention the line — a
  sentence that notes the exception without overriding the rule does not close
  the misparse; and (b) the diff REMOVES lines from tests/test_verify_cli.py, so
  confirm nothing that pinned behaviour went out with the docstring prose,
  specifically the output.count(...) == 1 exactly-once assertion and the
  inbox.open_entries check that pins the hard no-inbox constraint.

Task 14: fix round 1 re-review — ALL ADDRESSED, no new breakage. Both weighted
  checks came back clean:
   - The SKILL.md sentence is placed BETWEEN the grammar sentence (:25) and the
     grouping instruction (now :29), so a top-to-bottom reader hits the carve-out
     BEFORE applying grouping — it countermands rather than merely mentions,
     which was the distinction that mattered. The shipped line was NOT reshaped:
     __main__.py:406 still emits the bare print, no fake four-state dressing.
   - The removed nine lines in tests/test_verify_cli.py were DOCSTRING ONLY.
     Both pinning assertions confirmed present and untouched: the
     output.count(...) == 1 exactly-once check and the inbox.open_entries check
     that pins the hard no-inbox constraint.
  The fixture date 2/2/2024 0:00 genuinely traverses load_rw_csv's drop path —
  the re-reviewer showed that an ISO-only re-filter at the loader would drop the
  row from the PMID index and fail the blocking-retraction assertion, which is
  exactly the coverage the private-helper test could not give.
  Rationale relocation verified in BOTH directions, and the surviving comments
  were judged to state constraints rather than narration: __main__.py:405 shrank
  to "Stdout line only — never a review-queue record"; checks.py:914-915 to the
  production-shape fact. The noqa comment was correctly judged a DISTINCT
  constraint (why the suppression is safe), not a re-introduction.
Task 14: complete (commits b1d5f17..079c287, review clean after 1 fix round,
  0 minors deferred). Ticked at b899883 — 5 boxes. Suite 1557/7; gate 8/8.

Task 15: BASE = b899883. Implementer dispatched (sonnet, TDD).
  PRE-CHECK, surfaces: reduce_update_notice_outcomes at checks.py:1018 (brief
  says ~1024) and the fallback tuple at :1057, currently exactly
  (Result.UNREACHABLE, Result.MATCHED, Result.SKIPPED) as the brief describes.
  THE BRIEF POINTS AT THE WRONG FILE AGAIN — second time in Part 2. Step 4 says
  to "read verify.py's minting condition"; verify.py does not hold it. The guard
  is events.py:97 — `if result is not Result.MATCHED: raise ValueError("only
  MATCHED mints verified events...")` — AND IT IS ALREADY PINNED at
  tests/test_events.py:139 via pytest.raises(match=...).
  So Step 4's "add a regression test if none pins it" resolves to: one exists.
  The dispatch reframes the work as establishing whether the invariant is
  STRUCTURALLY guaranteed — the guard sits at the minting function and refuses
  ANY non-MATCHED, so a reduced UNMATCHED cannot reach a mint however the
  reduction chose it — and asks for that argument traced against the real call
  path rather than assumed. A duplicate test re-asserting the same guard would
  be noise; if they find genuine extra coverage they must say what it catches
  that :139 does not.
  ALSO CARRIED: the consequence sweep is a finding-generator, not a chore — any
  test that pinned the old rounding ASSERTED THE DEFECT, and must be fixed with
  a per-test note in the commit body naming what it used to assert. Quietly
  adjusting an expected value would bury a finding.
  And the comment-hygiene doctrine now travels WITH ITS ADDRESS
  (plan-w-quality-tail.md:39), since a reviewer fairly challenged whether it was
  real and could not find it after Part 4 split out.

### TWO CONTROLLER ERRORS ON TASK 15 — recorded prominently, both mine

  ERROR 1 — I TOLD AN IMPLEMENTER THE BRIEF WAS WRONG WHEN THE BRIEF WAS RIGHT.
  My dispatch said "the brief points at the wrong file AGAIN — verify.py does not
  hold the minting condition", and directed the work to events.py:97 instead.
  THAT WAS FALSE. verify.py:797 holds the OPERATIVE gate: a ternary that calls
  `events.record_pass(text, check, Result.MATCHED, ...)` and never forwards a
  non-literal result. events.py:97's guard is DEFENSE IN DEPTH — real, already
  pinned at test_events.py:139, but a backstop rather than the protection.
  The brief's "read verify.py's minting condition" was accurate.
  HOW I GOT IT WRONG: I grepped verify.py for `verified|mint` and then filtered
  to `mint|append_event|record_event`. The call is `record_pass`. None of my
  terms matched it, I read the empty result as absence, and I asserted absence.
  FOURTH wrong-instrument instance in this stretch, and the first that cost
  someone else: wrong tree (8b), wrong search term (8b again), wrong pattern
  (grep -c "print(" counting substrings inside _notice_fingerprint), and now
  wrong search term again — with the added failure that I built a confident
  dispatch correction on top of it.
  THE IMPLEMENTER CAUGHT AND CORRECTED ME, and pinned the real gate separately.
  That is the loop working in the direction it is hardest to accept: the
  controller's "correction" was the defect, and the subagent said so.
  Note the asymmetry that made this dangerous — an absence claim from a grep is
  unfalsifiable by the same grep. "I searched and found nothing" needs a
  different instrument to check than the one that found nothing.

  ERROR 2 — I DISPATCHED TASK 15 WITHOUT GENERATING ITS BRIEF. The dispatch said
  "Read your task brief first" and named
  .superpowers/sdd/2026-08-22-post-q-batch/task-15-brief.md, which DID NOT EXIST.
  I went from pre-check straight to dispatch and skipped `task-brief` entirely.
  The implementer fell back to the plan's Task 15 section
  (docs/superpowers/plans/2026-08-22-post-q-batch.md:296-329), verified its
  content matched the dispatch verbatim, and disclosed the gap rather than
  silently proceeding — so no information was lost, by its diligence and not by
  my process.
  PROCESS FIX for every remaining task: generate the brief BEFORE writing the
  dispatch, and confirm the file exists. The skill's whole point in extracting
  briefs is that the task text reaches the implementer without passing through
  my paraphrase; pointing at a missing file silently reintroduces exactly the
  dependency the brief removes.

Task 15: implementer DONE (commit 3d65856). Suite 1559/7 (baseline 1557 + 2 new
  tests); form gate 8/8. RED->GREEN on
  test_reduce_preserves_nonblocking_unmatched_over_matched.
  CONSEQUENCE SWEEP: no test pinned the old rounding — so nothing had encoded
  the defect, which is worth recording as a negative result rather than silence.
  ADDED COVERAGE beyond the brief, and correctly targeted after correcting me:
  test_apply_state_transitions_routes_unmatched_update_notice_to_failure_not_a_mint
  pins verify.py:797's operative ternary, which nothing pinned before.

Task 15: review — spec COMPLIANT, quality APPROVED. Review file:
  .superpowers/sdd/2026-08-22-post-q-batch/task-15-review.md
  The reviewer REPLAYED THE RED in a scratch checkout against b899883 and got
  the exact assertion failure character-for-character — an assertion failure,
  not a constructor error, which was the specific doubt I raised.
  It also used MUTATION TESTS to upgrade both Minors from NOT-VERIFIED to
  CONFIRMED: replacing the ternary condition with True, and mutating the else
  branch to record_failure(..., Result.UNREACHABLE). That is the right way to
  establish a test's strength, and it is what turned two soft observations into
  evidenced findings.
  It verified the fix sits INSIDE the else branch so the blocking bucket is
  provably untouched, and that verify.py's warn loop in _file_effects sits
  OUTSIDE the non-MATCHED block, so an UNMATCHED reduction still files RW's
  correction notices — the warn_notices merge the brief's second assertion
  requires.
  The implementer's two adaptations of the brief's literal test constructor were
  judged justified and were disclosed: inbox.validate_reason would have raised on
  the brief's reason string, and production never sets extra["class"] on a
  non-blocking UNMATCHED.
  CONSEQUENCE SWEEP CONFIRMED EMPTY — no test pinned the old rounding. Recorded
  as a negative result rather than silence.
  Cannot-verify closed by controller: literal `pre-commit run --all-files` at
  HEAD, 8 Passed, tree clean. Also worth recording the reviewer's accounting,
  which explains a number I have been reporting all run: the gate is 8 of 10
  hook ids because shellcheck and shfmt are `stages: [manual]`.
Task 15: minor (deferred): tests/test_verify_cli.py:534 — the new routing test
  asserts only that a failed-verification row EXISTS for update-notice, never
  that the recorded result is UNMATCHED, so its name promises more than it
  checks. Proved by mutation: record_failure(..., Result.UNREACHABLE) still
  passes. Thematically central to this run — a test claiming more than it
  verifies — but Minor because :1493 already pins exact rows for that drift.
Task 15: minor (deferred): tests/test_verify_cli.py:516 — the commit body's
  coverage-novelty claim is broader than the real gap; :1493 already catches
  ternary drift. Documentation-only; the new test still earns its place for the
  update-notice check id, which no pre-existing test routes as a failure.
Task 15: complete (commits b899883..3d65856, review clean, 2 minors deferred).
  Ticked at ded3cdf — 5 boxes. Suite 1559/7; gate 8/8.

Task 16: BASE = ded3cdf. Implementer dispatched (sonnet, TDD). BRIEF GENERATED
  BEFORE THE DISPATCH THIS TIME — the Task 15 process fix, applied.
  PRE-CHECK: the defect is confirmed at events.py:255 —
  `machine_confirmed = _applicable_note_checks(data) <= checks` is a SUBSET TEST
  VACUOUSLY TRUE ON AN EMPTY SET.
  The brief's "reuse the existing parse_claims iteration" is directly
  actionable: claims_mod is imported at events.py:7 and a
  `for claim in claims_mod.parse_claims(note_text):` loop already exists at :267,
  so a flag set inside it avoids a third pass. Also flagged that
  _applicable_note_checks(data) is ALREADY called twice (:255, :258) — do not
  make it three.
  SPEC PARAGRAPH LOCATED, and the brief was right again: it is at
  docs/superpowers/specs/2026-08-16-foundation-spec.md:88, titled "Event
  integrity" — TWO WORDS, NO HYPHEN, which is why my hyphenated grep missed it.
  FIFTH wrong-instrument instance, but the FIRST one I caught before asserting
  absence: after the first grep returned nothing I searched by CONTENT instead
  of concluding, precisely because Task 15 had just taught me that an absence
  claim from a grep is unfalsifiable by the same grep. The lesson took one
  iteration to land.
  The paragraph's current closing claim is exactly what the defect exploits:
  "Machine-confirmed trust requires all applicable note-level checks and quote
  claims to match" — vacuously satisfiable when the applicable set is empty.
  Also carried: Task 11 edits a DIFFERENT §5 paragraph (the never-delete
  invariants line), so Task 16 must touch only Event integrity.

Task 16: implementer DONE_WITH_CONCERNS (commit 0b8ec6c). Suite 1561/7
  (baseline 1559 + 2 new tests); form gate 8/8. RED confirmed: BOTH new tests
  returned "machine-confirmed" pre-fix.
  THE DEFECT WAS THE SAME VACUITY WRITTEN TWICE, in two languages — events.py:255's
  subset test over an empty set, and the spec's "Machine-confirmed trust requires
  all applicable note-level checks and quote claims to match". Both were in
  scope and both are closed in the one commit.

### VERIFIED FINDING ROUTED TO THE ORCHESTRATOR — human-reviewed is unreachable

  The implementer disclosed it rather than absorbing it. I VERIFIED IT
  INDEPENDENTLY before routing:
  `events.record_pass` has exactly TWO production call sites — publish.py:368 and
  verify.py:797 — and NEITHER PASSES `by=`. Both call
  `record_pass(text, check, Result.MATCHED, at=...)`, so every shipped event
  takes the default machine actor.
  `trust_tier` requires a `human:` event to derive `human-reviewed`. NOTHING IN
  THE SHIPPED CODE CAN MINT ONE. The tier is well-defined, correctly derived, and
  STRUCTURALLY UNREACHABLE — a trust level the spec describes and the system
  cannot produce.
  NOT TASK 16's TO FIX: closing it needs a NEW PRODUCTION SURFACE that mints
  `human:` events, outside that task's step 1-5 delta and its verified-surfaces
  list. The implementer was right to flag rather than expand, and its sweep
  confirmed the DERIVATION half is correct — human-reviewed still requires the
  event and would be reachable given one — so the defect is precisely and only
  the missing minting path.
  Routed while the verification was fresh, on the same reasoning as the XML
  clause earlier: a finding held in a task report DIES WITH THE WORKSPACE. It is
  a trust-model gap rather than a code defect, so scoping it is the author's.
Task 16: review dispatched over ded3cdf..0b8ec6c. The reviewer is told the
  unreachability is VERIFIED and not to re-litigate it — only to judge whether
  excluding it was the right scope call, and whether anything in this diff makes
  the situation better or worse. It is also asked to confirm the floor is
  has_applicable OR has_managed_quotes rather than AND: a note with quote claims
  but no note-level checks is still checkable and must stay eligible, and a fix
  that made the tier unreachable in the OTHER direction would be the same defect
  mirrored.
  DISPOSITION (orchestrator): the finding is now on ISSUE #17, split — derivation
  half CLOSED and confirmed by Task 16, minting half re-scoped as the open
  remainder with both call sites and the ack-vs-event design tension named. It no
  longer depends on this workspace surviving.
  Their note on why the routing worked: independent verification BEFORE routing
  is what made the issue comment writable AS FACT RATHER THAN CLAIM. Worth
  keeping — the verification was not ceremony, it changed what could be written
  down and where.
  SCOPING GOES TO THE AUTHOR — it is a trust-model act: WHICH human act mints,
  through which verb, under the rubber-stamp rule. Orchestrator's recommendation
  heading there is DEFER-WITH-TRIGGER to the slice, on reasoning worth recording:
  AN UNREACHABLE TIER NEVER LIES — absence reads as "not yet", so nothing is
  fabricated while it stays unreachable. Phase 5's per-quote attestation path is
  where the natural minting act will reveal itself as friction, and scoping the
  verb before that evidence would be INVENTING THE DESIGN THE SLICE EXISTS TO
  SURFACE. Explicitly NOT added to Part 2 — new surface, and the plan was just
  un-bloated by the Plan W split.
  That reasoning is the no-invented-numbers doctrine applied to DESIGN rather
  than to constants: do not specify the verb before the evidence that shows what
  it should be.

Task 16: review returned — spec ISSUES, quality NEEDS FIXES. Review file:
  .superpowers/sdd/2026-08-22-post-q-batch/task-16-review.md
  THE FIX ITSELF WAS JUDGED CORRECT AND MINIMAL, and several things were
  verified in the implementer's favour: the floor is OR-shaped in BOTH
  directions (a citekey-only note with a matched managed-quote check still
  reaches machine-confirmed, reproduced); the _applicable_note_checks hoist is a
  NET CALL REDUCTION where BASE made two; has_managed_quotes genuinely reuses the
  existing parse_claims loop; the flag sits after the continue-guard and before
  the isdisjoint test so the floor cannot mask the quote loop's own
  invalidation; the spec sentence landed verbatim with the sibling task's
  Invariants paragraph untouched. The commit also deliberately used NON-CLOSING
  PROSE so merging would not auto-close an unfixed issue — the right instinct,
  and it worked.
  Cannot-verify closed by controller: form gate 8/8 at 0b8ec6c, tree clean.
  THREE IMPORTANT FINDINGS. Two went to a fix round; one is plan bookkeeping.
  (1) CONFIRMED — the floor's `has_managed_quotes` clause is PINNED BY NO TEST.
      Dropping it (leaving `if not applicable:`) regresses every identifier-less
      note with verified managed quote claims to permanently unverified, AND THE
      MUTANT PASSES THE ENTIRE SUITE. The reviewer reproduced it and ran the
      mutated copy against test_events/test_trust_tier_cli/test_notes/test_quotes
      — 124 passed.
      I VERIFIED THE AGGRAVATING FACT MYSELF: knowledge_harness/events.py is in
      mutation-exclusions.txt (line 37), so THE MUTATION GATE CANNOT CATCH THIS
      EITHER. A hand-written test is the only thing that can.
      This is the exclusion list's real cost made concrete: a module nothing
      mutates needs its guards pinned BY HAND, and nobody is reminded of that at
      the moment they write one.
  (2) CONTESTED — the floor ALSO narrows human-reviewed. A note with a `human:`
      event, empty applicable set and no managed quotes derived human-reviewed at
      BASE and derives unverified at HEAD. Reproduced against scratch exports of
      both commits; no test constructs a human event on an identifier-less note.
      NOT MERELY A COVERAGE WISH: the plan's own Task 16 title at :331 says
      "read the issue and cover it in this task's tests", so this clause is
      UNDISCHARGED. And it is testable despite the tier being unreachable —
      A TEST FIXTURE CAN WRITE A `human:` EVENT INTO FRONTMATTER DIRECTLY; only
      the MINTING surface is missing, not the derivation. Sent back with both
      directions to pin.
  (3) CONTESTED, plan-mandated — the plan at :331 says Task 16 "also closes"
      issue #17. It does not: the derivation half closed, the minting half is
      untouched. Verified by the reviewer via `gh issue view 17` (OPEN) and a
      plan-wide grep showing #17 is named ONLY at :331, so no later task
      inherits it by default. Controller confirmed the line text directly.
      ROUTED TO THE ORCHESTRATOR for a main-side plan-text correction, not fixed
      here: it is an authored claim about what a task delivers, same reasoning
      that sent the polish-ledger entry through them. Flagged that the retitle
      should also account for the "cover it in this task's tests" clause, which
      is being discharged now rather than dropped.
  BOTH LANDED (orchestrator, origin/main fab7bf1):
  (a) Task 16's title retitled to record the split TRUTHFULLY — derivation half
      closed AND pinned via fixture-written events (the "cover in tests" clause
      preserved as being-discharged rather than dropped), minting half explicitly
      OPEN with the slice-Phase-5 trigger named, and an instruction that the task
      MUST NOT auto-close #17. The implementer's careful non-closing prose is now
      A PLAN REQUIREMENT rather than a courtesy — the best possible fate for a
      good instinct: it stops depending on the next implementer having it.
  (b) mutation-exclusions.txt NOW STATES ITS OWN COST IN ITS HEADER: while a
      module is listed, new guard logic needs hand-pinned tests, the gate cannot
      catch an unpinned branch, and nothing reminds the author at write time —
      with the events.py mutant-survives-the-whole-suite case recorded as the
      evidence. That converts the file from a GAP-REGISTER into a gap-register
      THAT WARNS ITS READERS, which is the most it can do until Plan W's Task 25
      retires it.
      Worth keeping as a pattern: the finding was "nobody is reminded at write
      time", and the fix was to put the reminder where the reader already goes.
      Not a new mechanism — a note in the file that already had to be read.

Task 16: fix round 1 landed — 0b8ec6c AMENDED into 2c2af7c. TESTS ONLY:
  +52 lines in tests/test_events.py, three new tests, no production change.
  Suite 1564/7 (= the 1561 I confirmed + 3); form gate 8/8 after one
  ruff-format auto-fix, re-verified clean.
  THE DISCRIMINATION PROOFS WERE DONE BY MUTATION, which is exactly what the
  finding required — a test added to close a "nothing pins this" finding, that
  itself passes whether or not the guard exists, would be the finding UNFIXED
  WHILE APPEARING FIXED, and with events.py mutation-excluded nothing downstream
  would ever notice:
   - Mutant A (drop the has_managed_quotes clause): 2 failed / 1562 passed, and
     ONLY the two new OR-pin tests caught it.
   - Mutant B (remove the floor entirely): 3 failed, including an assertion
     reading 'human-reviewed' == 'unverified' — the exact regression flip
     finding 2 described, now pinned.
Task 16: fix round 1 re-review dispatched over 0b8ec6c..2c2af7c. Since the fix
  is ENTIRELY NEW TESTS, the re-reviewer is told the only question that matters
  is whether they discriminate, and to REPRODUCE both mutants in a scratch copy
  rather than read the reported counts — checking not just how many tests fail
  but WHICH, because a mutant caught only by a pre-existing test would mean the
  new one does no work. Also asked to confirm the human-reviewed pin covers BOTH
  directions (a human: event WITH applicable checks still derives human-reviewed,
  and the identifier-less no-quote case now derives unverified), since one-sided
  coverage leaves the flip half-pinned.

Task 16: fix round 1 re-review — ALL ADDRESSED, no new breakage. The re-reviewer
  BUILT BOTH MUTANTS ITSELF in /tmp/scratch_mutant rather than reading the
  reported counts, and checked WHICH tests fired rather than how many:
   - Mutant A (floor reverted to `if not applicable:`): 2 failed / 40 passed in
     test_events.py, and the two failures were EXACTLY the new OR-pins —
     test_identifier_less_note_with_matched_quote_is_machine_confirmed (:185) and
     ..._and_human_event_is_human_reviewed (:197). NO PRE-EXISTING TEST CAUGHT IT,
     which is the point: without these two the regression ships silently.
   - Mutant B (floor deleted): 3 failed, and the new
     test_identifier_less_note_with_human_event_and_no_quotes_is_unverified (:216)
     failed with exactly `assert 'human-reviewed' == 'unverified'`. It is the ONLY
     test exercising that flip; the other two Mutant-B failures never touch the
     human-reviewed path.
  Both directions of the human-reviewed pin confirmed covered: positive with
  applicable checks (pre-existing, :155-171), positive via the managed-quotes-only
  OR clause (new, :197), and the negative flip (new, :216).
  Production and spec verified BYTE-IDENTICAL between fix-base and head, so the
  round really was tests-only.
Task 16: minor (deferred): tests/test_events.py:217's docstring reads "no longer
  derives human-reviewed... the floor applies before the human-actor check runs"
  — history-flavoured ("no longer") and implementation-order phrasing that the
  comment-hygiene doctrine would send to the commit body. Judged a stylistic nit
  rather than a substantive violation: the brief itself mandated "the reason, for
  the test name and the docstring", the test body is purely behavioural (calls
  trust_tier, asserts a tier string, does not mirror the guard's boolean
  structure), and 2c2af7c's body separately carries the full provenance.
Task 16: complete (commits ded3cdf..2c2af7c, review clean after 1 fix round,
  1 minor deferred). Ticked at 1fd3f8a — 5 boxes. Suite 1564/7; gate 8/8.

Task 17: BASE = 1fd3f8a. Implementer dispatched (sonnet, TDD, two sides).
  Brief generated BEFORE the dispatch, per the standing process fix.
  PRE-CHECK FOUND THE BRIEF'S SNIPPET INCOMPLETE — the significant finding here.
  Side (b)'s guard is shown once, but `_citekey_hash` in verify.py has TWO
  STRUCTURALLY IDENTICAL ADOPTION SITES, both verified:
    verify.py:212 — inside the `candidate_snapshot is not None` branch
    verify.py:224 — inside the live-file `note.is_file()` branch
  Both read the same five lines and both `return first`. GUARDING ONLY ONE leaves
  the other path adopting "unresolved", AND A TEST EXERCISING A SINGLE BRANCH
  WOULD PASS EITHER WAY — the half-fix shape this plan keeps catching. The
  dispatch requires both covered, tests that reach BOTH branches named
  individually, and a discrimination demo showing that reverting each guard
  separately turns a test red.
  ALSO FLAGGED, an over-delete hazard: __main__.py:255 separately does
  `degradation_reasons.append("attachment unresolved")`. That is a DIFFERENT
  record and must SURVIVE — it is how the degradation stays visible once the
  placeholder digest stops being written. Deleting it would trade a fabricated
  digest for silence, which is the opposite of this task.
  Confirmed `re` is already imported in verify.py, so the brief's fullmatch guard
  needs no new import.

Task 17: implementer DONE (commit 213a826; 5 files, +80/-18). Suite 1566/7
  (baseline 1564 + 2 new tests); form gate 8/8.
  BOTH ADOPTION SITES GUARDED INLINE with re.fullmatch(r"[0-9a-f]{64}", first),
  and DISCRIMINATION DEMONSTRATED PER SITE: reverting each guard individually
  turns only its own test red. That was the specific thing the pre-check called
  for, because a single-branch test would have passed either way.
  Controller confirmed the over-delete hazard was avoided: "attachment
  unresolved" still occurs twice in __main__.py, so the degradation record
  survives alongside the deleted placeholder append.
  UNPLANNED CONSEQUENCE, disclosed rather than absorbed — and the highest-risk
  part of this diff: the new guard REJECTED A TEST FIXTURE'S FAKE DIGEST. The
  shared `net_vault` fixture in tests/conftest.py had been using "aa11" as digest
  shorthand, which is not 64-hex, so the guard refused it. The implementer
  migrated the fixture and its derived literals in test_verify_cli.py and
  test_cli_live.py to real 64-hex, and reports confirming via advisor and
  full-suite runs that the change was necessary and exactly scoped rather than a
  guard weakening.
  THIS IS WHY THE REVIEW MATTERS HERE: a SHARED fixture feeds many tests, so the
  migration's blast radius is wider than the task. The review is asked to judge
  whether any assertion that depended on the old value was weakened, whether any
  test now exercises a different path than before, and whether the remaining
  "aa11" occurrences elsewhere in tests/ are unrelated contexts (claim ids,
  citekeys) rather than digests the guard would now reject.
  ALSO FLAGGED: tests/test_cli_live.py changed, and it is ENV-GATED — it does
  NOT run in an offline suite, so nothing in any green run verifies those six
  lines. The review must judge them on inspection, because nothing else will
  catch them until the live legs run at Task 21.
  A nice property of this defect worth recording: the guard did not just fix
  production, it EXPOSED A LATENT FALSEHOOD IN THE TEST SUITE — fixtures had been
  asserting against a digest shape that production would never emit. Tightening a
  producer surfaced consumers that had been coasting on a looser contract.
Task 17: review dispatched over 1fd3f8a..213a826.

### TASK 17b PRE-CHECK, ROUND 2 (post-merge) — THE ATTESTATION RULE VERIFIED
### END TO END AGAINST THE MECHANISM

  Surfaces re-confirmed after the boundary merge: lint_evidence_layer still takes
  BOTH snapshots (lints.py:618), so no signature change is needed.
  THE RULE'S MECHANISM, traced rather than assumed:
   - notes.py:246 — render_note ALWAYS sets `generated = {"by": AGENT_ACTOR,
     "at": generated_at if projection_changed else prior_generated_at}`.
     So `by` is always the machine actor after any render; it is NOT the
     discriminating signal for a CLI write. `at` is.
   - notes.py:238 — `projection_changed` is true when
     `_managed_projection(prior) != _managed_projection(fm)`, among other terms.
   - notes.py:187-192 — `_managed_projection` covers every MANAGED_FIELDS member
     EXCEPT `generated` itself.
   - notes.py:157-169 — MANAGED_FIELDS CONTAINS `citekey`, `fixity-sha256` AND
     `managed-sha256` — three of the four guarded keys.
  THEREFORE the rule works, and here is why each case lands correctly:
   - import-note changes fixity-sha256 (the author's new-attachment-no-annotations
     case) -> projection_changed -> `at` bumps -> attestation present -> LEGAL.
     This is exactly the case that killed managed-slice coupling, and the
     attestation primitive handles it natively.
   - import-note changes managed-sha256 or citekey -> same path -> LEGAL.
   - A HAND EDIT to any guarded key does not touch `generated` at all -> no
     attestation -> FLAGGED. That is the whole defect, caught.
   - A byte-identical re-render changes no machine key either, so there is
     nothing to flag — the preservation semantics stay orthogonal, as the author
     said.
   - The SECOND predicate (a `generated` change whose `by` is not AGENT_ACTOR is
     itself drift) has teeth precisely because render_note ALWAYS writes
     AGENT_ACTOR: any other value is necessarily hand-written.
  AND THE ONE GAP IS EXACTLY WHAT STEP 2b EXISTS FOR: `archive-url` is NOT in
  MANAGED_FIELDS — notes.py:155-156's own comment lists it among the fields that
  "pass through unchanged". So archive-source's write does NOT bump `generated`,
  and WITHOUT Step 2b's bump every legitimate archive-source run would be flagged
  as drift. Step 2b is load-bearing, not tidying.
  This is a verified mechanism to hand the implementer rather than a rule to
  reverse-engineer — and it means the author's design survives contact with the
  code in every branch, which is worth recording as a positive result.

Task 17: review returned — spec ISSUES, quality NEEDS FIXES. Review file:
  .superpowers/sdd/2026-08-22-post-q-batch/task-17-review.md
  Cannot-verify closed by controller at 213a826: suite 1566/7, form gate 8/8.
  UPHELD AFTER INDEPENDENT CHECKING: side (a) is one deleted line with BOTH
  degradation channels intact; both adoption guards are non-redundant, with the
  per-site revert experiment REPRODUCED in an isolated copy and corroborated by
  per-test line coverage; and MIGRATING THE FIXTURE RATHER THAN LOOSENING THE
  GUARD was endorsed, because notes.sha256_file() always emits 64 lowercase hex
  so the regex can never reject a digest this codebase wrote.
  ONE FINDING REFUTED in the implementer's favour: a lens claimed the diff newly
  duplicated the adoption policy across two planes. `git show 1fd3f8a` shows the
  block was ALREADY duplicated verbatim; the diff swaps one predicate line per
  site. Pre-existing structure, not authored here.
  CONFIRMED IMPORTANT — THE HAZARD I FLAGGED, IN ITS SHARPEST FORM. The shared-
  fixture migration was PARTIAL: tests/test_verify_cli.py:399 still seeds
  target_hash="aa11" and :401 still calls append_ack(..., "aa11") — four chars —
  while the fixture they must match widened to "aa11" * 16. Controller confirmed
  both lines directly.
  So test_matching_outcome_still_mints_event_after_same_hash_ack NO LONGER
  ESTABLISHES THE SAME-HASH ACK ITS OWN NAME ENCODES. Two lenses proved it
  independently: is_acknowledged True at base / False at HEAD, and an injected
  MATCHED-suppression fault FAILS AT BASE AND PASSES AT HEAD — then fails again
  once 399/401 are migrated.
  That is the worst shape a test defect takes: the NAME still claims the
  behaviour, the TEST no longer exercises it, and THE SUITE REPORTS GREEN. It is
  the shared-fixture blast radius the dispatch warned about, landing one file
  away from where the implementer was looking. The other short literals (475,
  501, 703, 1269, 1682) were audited and are inert, so the fix is exactly two
  lines.
Task 17: fix round 1/5 dispatched — the Important plus three Minors chosen
  because each is a seam this task created or the decision it rests on:
   - Minor: both new tests seed "unresolved", so only the guard's HEX-NESS is
     pinned and the {64} LENGTH BOUND — the discriminator the whole task rests
     on — has NO test. Relaxing the regex to [0-9a-f]+ would keep the entire
     suite green while re-admitting a short constant as an ack anchor. Fix is a
     one-line parametrize over ["unresolved", "aa11"].
   - Minor: side (a) makes `fixity-sha256: []` a NEWLY REACHABLE production
     shape (the placeholder always filled the list before), and nothing pins that
     an empty list falls through to the managed-bytes hash. The seam where the
     two halves of the fixity pair meet, created by this task.
   - Minor: verify.py:243 and :400 docstrings still describe fixity adoption as
     UNCONDITIONAL, so a reader would conclude any declared value anchors an ack
     — precisely the defect this task closed.
Task 17: minor (deferred): the migrated 64-char digest is now spelled three ways
  — the conftest YAML literal, seven raw literals, and "aa11" * 16 in assertions
  — so a future fixture change must be mirrored by hand across long literals
  whose failure mode is a SILENT NO-OP. All nine verified exactly 64 chars today,
  so a drift hazard rather than a current defect.
Task 17: minor (deferred): mutation-baseline.txt:130 still lists a
  `_citekey_hash::isinstance(first, str) and first` survivor keyed to the exact
  expression this commit deleted from both sites. Inert for the gate
  (`found - baseline` can never produce that key again) — inventory drift,
  obsoleted in the good direction.
Task 17: fix round 1 landed — 7374ebd, FOLLOW-UP COMMIT not an amend, per the
  standing correct-forward rule (213a826 was reviewed, so it is a record).
  2 files, +61/-19; verify.py docstrings only, no production logic change in
  this round. Suite 1569/7 (= 1566 + 3 new parametrized cases); form gate 8/8.
Task 17: fix round 1 re-review dispatched over 213a826..7374ebd. The dispatch
  requires REPRODUCTION rather than reading, because every one of the four
  findings is about whether a test DISCRIMINATES — and a fix that adds a test
  which passes either way is the finding unfixed while appearing fixed:
   - finding 1: rebuild the injected MATCHED-suppression fault and report the
     actual pass/fail matrix, expecting FAILS AT HEAD / PASSES AT BASE.
   - finding 2: relax the regex to [0-9a-f]+ at HEAD and name which tests go red
     with which parameter id — plus the one-site converse, since relaxing both
     sites at once cannot distinguish a per-site pin from a single one.
   - finding 3: prove the string replacement is not a silent no-op, because a
     replacement whose target is absent leaves the fixture untouched and the
     test passes VACUOUSLY — the exact shape of "covered" that isn't.
Task 17: fix round 1 re-review — ALL FOUR FINDINGS ADDRESSED, no new defects.
  The re-reviewer RAN every experiment rather than reading the report:
   - Finding 1 matrix REPRODUCED EXACTLY AS PREDICTED: the injected MATCHED-
     suppression fault PASSES at base 213a826 (test blind) and FAILS at head
     7374ebd (`assert False`, no doi verified event minted). The test now
     establishes the same-hash ack its name encodes.
   - Finding 2: relaxing {64} to + at both sites fails EXACTLY the two [aa11]
     parameter ids and leaves [unresolved] green — so the length bound is what
     the new parameter pins, not hex-ness over again. The PER-SITE converse was
     also run: each test independently guards its own adoption site, which is
     the property the combined relaxation cannot show.
   - Finding 3: the parser turns a bare `fixity-sha256:` into a PRESENT key with
     value [], not an absent key, and the .replace() was confirmed to actually
     fire against the fixture text — so the test is not vacuous. IndexError
     injection confirmed it catches regressions on BOTH _citekey_hash branches;
     the implementer's own self-review had only shown the combined-fault case.
   - Finding 4: docstrings accurate across all five shapes (absent, empty,
     non-hex, short-hex, valid 64-hex).
  Controller re-ran the gates independently: suite 1569 passed / 7 skipped,
  stop_publish_gate exit 0. Worktree confirmed clean (status, cached diff,
  worktree diff, stash list all empty).
Task 17: CONTROLLER-VERIFIED, not taken on report — the remaining short "aa11"
  literals. The prior review called five of them "audited and inert", and an
  absence claim of that kind is exactly what burned this task once. So I checked
  the one that shares the DEFECT'S OWN SHAPE — test_verify_cli.py:1306
  `target_hash="aa11"` in test_warn_dedup_reconstructs_type_and_inbox_is_oldest_
  first — by MUTATING IT TO "aa11" * 16 in a scratch tree. The test passes either
  way, so the value is genuinely inert there and finding 1 has NO SECOND
  INSTANCE. Verified rather than trusted.
Task 17: complete (commits 1fd3f8a..7374ebd, review clean after 1 fix round,
  2 minors deferred). Ticked at a2d7942 — 5 boxes; 64 checked / 48 unchecked.
Task 17: minor (deferred, PRE-EXISTING — not created by this task, so not a fix
  round): test_warn_dedup_reconstructs_type_and_inbox_is_oldest_first names
  "warn dedup", but run_verify() passes no rw_csv, so per Task 15's own finding
  the update-notice leg NEVER RUNS and no competing update-notice entry can be
  minted. The `== 1` count therefore cannot fail on the fresh-mint dedup path.
  WHAT I DID NOT ESTABLISH, stated so the final review can settle it rather than
  inherit my guess: whether verify._file_effects' RE-FILE dedup of the already-
  open seeded entry is exercised — that path could still give the assertion
  teeth. Flagged as a question with its evidence, not as a proven defect.
Task 17: minor (deferred): docstring says "digest-shaped" without spelling out
  LOWERCASE-ONLY — an uppercase 64-hex digest fails the guard. Inert today
  because notes.sha256_file() only ever emits lowercase, so it is a reader
  hazard rather than a behaviour gap.

### STANDING DISPATCH RULE — SCRATCH COPIES OF THIS WORKTREE (mechanism, verified)
  The re-reviewer self-reported a contained incident that is a TRAP FOR EVERY
  FUTURE SUBAGENT, because fault-injection in a scratch copy is a method I keep
  demanding. Root cause, confirmed by me directly: this worktree's `.git` is a
  66-BYTE POINTER FILE reading
  `gitdir: /home/eranr/New folder/.git/worktrees/fix+pre-slice-batch`.
  `cp -r` copies that pointer VERBATIM, so git commands run inside the "copy"
  operate on the REAL worktree's gitdir — including its index. That is how
  `git checkout <sha> -- .` in a scratch tree transiently mis-staged the live
  worktree. Working-tree files were never touched; repaired with `git reset HEAD`
  and I independently confirmed the tree clean afterwards.
  ELIMINATE THE PROBLEM RATHER THAN ADD A RULE, per AGENTS.md's own ordering.
  The recipe, PROVEN not reasoned — I ran both halves:
      git archive <sha> | tar -x -C <scratch>
  produces a tree with NO .git AT ALL (`ls -la <scratch>/.git` -> No such file),
  so it CANNOT reach shared git state even in principle, and
  `python -m pytest tests/test_verify_cli.py` inside it returns 86 passed /
  1 skipped. Safe AND working — a recipe that is only safe would be useless.
  Every future dispatch that asks for scratch-copy experiments carries this
  recipe and the prohibition: never `cp -r` this worktree, and never run
  `git checkout` / `git reset` / `git stash` inside a copied tree.

Task 17b: BASE = a2d7942. Implementer dispatched (sonnet — multi-file, and the
  predicate is a judgment call). Brief generated and confirmed BEFORE the
  dispatch, per the standing process fix.
  THE PRE-CHECK FOUND THREE THINGS THE BRIEF COULD NOT KNOW, and one of them is
  a latent production defect the plan text would have shipped:
  (1) VERSION-DEPENDENT ACTOR — THE BIG ONE. The brief's rule is "`generated`
      changed with `by` = THE MACHINE ACTOR". Implemented literally as
      `by == AGENT_ACTOR`, that is a time bomb: AGENT_ACTOR is
      `f"knowledge_harness/{__version__}"` (__init__.py:8, today
      knowledge_harness/0.1.0), so THE FIRST VERSION BUMP FLAGS EVERY NOTE
      LEGITIMATELY ATTESTED BY THE PREVIOUS VERSION AS DRIFT — a false-drift
      storm across a whole vault, caused by an upgrade rather than by any edit.
      Resolved to a machine-actor CLASS test, and resolved from the tree's own
      idiom rather than my preference: `actor.startswith("human:")` is how this
      codebase tests actor class, at inbox.py:383,474,614,626,645 and
      events.py:287, and NO exact-actor equality test is used for class
      membership anywhere. The one `!= AGENT_ACTOR` (notes.py:240) is a
      RE-RENDER TRIGGER, where version sensitivity is the point — handed over
      with the contrast spelled out so it isn't copied by surface similarity.
  (2) A DISCRIMINATION HAZARD INSIDE STEP 1'S OWN PARAMETRIZATION.
      `managed-sha256` is the witness, and lint_evidence_layer's FIRST loop
      (lints.py:627-637) already runs validate_managed_witness, which returns
      UNMATCHED "schema-violation — stale managed-sha256" for any hand-edit to
      it. So that parameter yields UNMATCHED WITH OR WITHOUT THE NEW CHECK: a
      test asserting only the four-state result passes at base and at head, and
      the plan's own test design would have reported coverage it did not have.
      Dispatch requires the SPECIFIC reason string and PER-KEY discrimination,
      plus a check of whether any other key is double-covered too.
  (3) NO DIALECT REGISTRATION NEEDED — checked rather than assumed, because the
      reflex here is to open terminology.md. inbox.REASON_CODES governs the
      LEADING WORD only (_REASON at inbox.py:81 is `(?:<code>)(?:$|\s+\S.*)`),
      and `drift` is already registered, so `drift — <text>` is already legal.
      Told the implementer to report a concern rather than coin a new leading
      word, since that would be a governed-surface change outside this scope.
  STEP 2b RE-CONFIRMED LOAD-BEARING AT THE CODE, not from the earlier note:
  archive.set_archive_url (archive.py:71) is BYTE-SURGICAL and never routes
  through render_note, so it cannot bump `generated`; and archive-url is absent
  from MANAGED_FIELDS. Without Step 2b the new lint flags every legitimate
  archive-source run. Two safety facts handed over with it: managed_sha256
  covers only the managed slice, so a frontmatter-only `generated` bump does
  NOT stale the witness; and set_archive_url's parse-back-or-raise discipline
  (archive.py:106-115) is the pattern the bump should copy.
  ALSO CARRIED: the standing scratch-copy recipe, since this task's proof
  obligation is per-key revert experiments — exactly the method that corrupted
  the live index last time.
Task 17b: implementer DONE (commit f3f5a7f; 5 files, +313/-3). Suite 1577/7
  (= 1569 + 8 new); ruff and mypy clean; form gate exit 0.
  THE VERSION-BUMP TIME BOMB WAS AVOIDED: lints.py ships
  `_MACHINE_ACTOR_PREFIX = "knowledge_harness/"` with a startswith test, not
  `== AGENT_ACTOR`. That was the pre-check's central hand-over and it landed.
  CONTROLLER-VERIFIED BEFORE DISPATCHING THE REVIEW, because two of these are
  claims this run has been burned on before:
   - THE CITATION IS REAL. lints.py's new comment cites "docs/terminology.md's
     actor convention: process-written records carry knowledge_harness/<version>".
     I checked the document: terminology.md:44 says exactly that, in those words.
     Derived from the source, not from memory — recorded as a positive, since a
     fabricated citation is a defect this plan has already caught once.
   - THE SINGLE-LINE ASSUMPTION IS SAFE, AND SAFE BY THE DIALECT RATHER THAN BY
     LUCK. _bump_generated finds `generated` with startswith("generated:") and
     replaces ONE line, which would corrupt a block-style mapping and orphan its
     `by:`/`at:` lines. I probed it: frontmatter.serialize emits `generated`
     INLINE on one line, and block style is not merely unusual but UNPARSEABLE
     here — `FrontmatterError: nested maps unsupported (flat schema, spec §5)`.
     So the shape the writer assumes is the only shape a valid note can carry.
   - THE UNRELATED-TEST EDIT IS NOT A WEAKENING, on inspection: the two git
     commands run with cwd=net_vault (the temp fixture vault), not the real
     repo, and they COMMIT a mutation the test had left uncommitted so base and
     candidate agree. The test is about warning suppression; its setup had been
     manufacturing an unattested fixity-sha256 delta as a side effect.
  FLAGGED TO THE REVIEW AS A QUESTION, NOT A VERDICT (no pre-judging): the diff
  adds archive._generated_at(), which is a VERBATIM DUPLICATE of __main__.py:267-
  268's `now.isoformat().replace("+00:00", "Z")`. Two independent spellings of
  one wire format, in two modules that both write the same field — and the new
  lint compares `generated` values FOR EQUALITY, so a future divergence in
  format would be a correctness bug, not a style nit. Severity left to the
  reviewer.
Task 17b: review dispatched over a2d7942..f3f5a7f on the most capable model —
  this is the batch's highest-risk diff, since a guard that flags legitimate
  writes is worse than no guard. The review must produce a PER-KEY
  discrimination matrix and is told exactly where to expect a false pass
  (managed-sha256 is double-covered by validate_managed_witness), plus the
  predicate's edge cases: generated absent->present, present->absent, machine
  `by` with garbage `at`, and a legitimate bump with a hand-edit riding along in
  the same commit.
Task 17b: review returned — spec PASS WITH ONE UNMET CLAUSE, quality GOOD,
  3 Important / 13 Minor. Review file:
  .superpowers/sdd/2026-08-22-post-q-batch/task-17b-review.md
  PER-KEY MATRIX REPRODUCED, and it vindicates the pre-check's hazard call:
  reverting lints.py, archive-url / fixity-sha256 / generated / citekey all
  produce an EMPTY outcome list at base, while MANAGED-SHA256 ALREADY PRODUCES
  `schema-violation — stale managed-sha256` AT BASE. So that parameter
  discriminates ONLY because the shipped test asserts the exact new reason
  string rather than UNMATCHED-ness. Had the implementer asserted the four-state
  result — the obvious thing to assert — the key would have reported coverage it
  did not have. The hazard was real and the test survives it.
  Step 2b independently proven load-bearing: reverting archive.py ALONE reds the
  legitimate-run test. The pre-check's claim was not taken on trust.
  IMPORTANT 1 — the attestation accepts a MALFORMED `generated`: _machine_attested
  (lints.py:652) tests only `by`, so `{by: machine, at: "banana"}` — and even a
  `generated` carrying `by` with NO `at` — legalizes all four machine-owned keys.
  notes._valid_generated (notes.py:195) already encodes the required shape and
  sits unused.
  IMPORTANT 2 — THE IMPLEMENTER'S ABSENCE CLAIM WAS FALSE, and the very defect it
  fixed still ships twice: tests/test_verify_cli.py:1505 and :1541 strip
  fixity-sha256 in the working tree without committing, both call verify_state,
  and verify.py:1014 reaches the lint. CONTROLLER-CONFIRMED BOTH LEGS DIRECTLY —
  read the two test bodies and read verify.py:1014 — rather than take the
  reviewer's word, since this is the same claim shape that has already misfired
  twice this run. They pass only because nothing asserts the outcome list.
  IMPORTANT 3 — Step 2's "Scope stated in the lint's finding text" was unmet.
Task 17b: AUTHOR RULING (2026-08-24) on Important 3 — DOCSTRING ONLY, NO ADR,
  REASON STRING UNTOUCHED. I asked rather than picked, because the two readings
  were materially different work on a governed surface, and picking by reflex is
  the named failure mode. I read the precedent first: spec §2's stated-boundary
  language is the Preservation-boundary bullet (spec:19), ending "(Solo scope:
  this is a stated boundary, not a compliance control.)" — a documented
  limitation, not a control.
  THE AUTHOR RULED AGAINST THEIR OWN CLAUSE, planner defect #8: "the brief's
  'the lint's finding text' was my over-specification — planner wording error,
  correct it rather than obey it. Same class as the aging-threshold precedent."
  Reasons recorded because they generalise: an ADR fails the bar since A SCOPE
  LIMITATION IS A FACT, NOT A DECISION, and minting one dilutes "only ADRs are
  binding"; the reason string is noise because INBOX ROWS CARRY FINDINGS, NOT
  SCOPE PHILOSOPHY, and "every letter reduces compliance"; and adding spec
  surface merely to host the sentence INVERTS THE FIX-RUNG, since the lint lives
  in plan + code and has no spec entry at all.
  Plan amended at 47fc2d2 and the brief REGENERATED before the fix dispatch, so
  the implementer reads the corrected requirement rather than the retracted one.
Task 17b: fix round 1/5 dispatched — 3 Importants plus four Minors, each a seam
  this task created:
   - A: THREE SPELLINGS of one wire format — archive._generated_at byte-
     duplicates __main__.py:267-268, notes.py:215 is a third, and _bump_generated
     re-implements frontmatter.serialize's inline-dict emitter. Format contracts
     with more than one author. INTERLOCKED WITH IMPORTANT 1 and dispatched as
     such: if the attestation starts requiring a valid `at`, archive's emitted
     `at` must satisfy the SAME validator or Step 2b's legitimate run stops being
     attested. Implementer told to re-run the Step 2b test and say so.
   - B: _generated coerces a non-dict to None, so junk-to-DIFFERENT-junk compares
     equal-as-None and produces no finding — a hole in the guard this task exists
     to build.
   - C: an unparseable BASE frontmatter silently skips the whole per-key check;
     only the candidate side is covered by validate_managed_witness.
   - D: comment hygiene at seven sites AND `f3f5a7f`'s commit body is EMPTY —
     which is WHY the comments carry history: the doctrine's destination did not
     exist, so provenance had nowhere else to go.
  ON IMPORTANT 2 the dispatch asks for METHOD, not just the fix: enumerate every
  test that mutates a literature note in the working tree and reaches the lint,
  and SHOW how the tree was made to tell — because an absence claim from a grep
  is unfalsifiable by the same grep, which is exactly how this one got through.
Task 17b: minor (deferred): missing type annotations on
  _frontmatter_attestation_outcomes; the double frontmatter parse at lints.py:632
  and :702; the duplicated archive-url parametrization at test_archive.py:542.
Task 17b: minor (deferred): DUPLICATE-KEY EVASION, verified real by the reviewer
  against the parser — frontmatter .get() is last-key-wins, so a duplicated
  machine-owned key whose final copy matches base evades the value comparison
  entirely. Only managed-sha256 has an independent duplicate guard, via the
  witness check. Correctly out of this task's scope; belongs to whoever hardens
  the parser, and it is the one deferred item with real teeth.
Task 17b: CONTROLLER ACTION OWED — AGENTS.md routes deferred work to GitHub
  Issues, not to a report paragraph. The implementer's concerns 1/2/3 (unguarded
  MANAGED_FIELDS keys; duplicate-key evasion; renamed files skipping the per-key
  diagnostic) are mine to file, and I told the implementer so rather than let the
  routing rule go unowned.
Task 17b: FILING DECISION — batch, not now. Checked the tracker rather than
  assume it was empty: `gh issue list --state open` returns exactly two, #17
  ("The human-reviewed trust tier cannot be minted by any shipped surface") and
  #16 ("Duplicate claim anchors render silently when annotations are keyless",
  which is Task 12's defect). NEITHER duplicates 17b's three concerns, so the
  batch is safe to defer to the end of the plan — and deferring matches the
  author's own stated preference for batching ("two findings, one upstream
  conversation") rather than filing piecemeal mid-run. Read
  docs/agents/issue-tracker.md first so the filing follows the repo's documented
  `gh issue create` conventions rather than my habits.
  LOOSE END TO SETTLE AT THE FINAL REVIEW, flagged now so it is not lost: #17 is
  STILL OPEN even though Task 16 is complete. Task 16 fixed the VACUOUS
  machine-confirmed tier (the checkability floor in events.py); #17's title is
  about no shipped surface MINTING human-reviewed at all. Those may be different
  defects, and I have not established which — so the question is recorded, not
  answered. Whether #16 closes on Task 12 is the same question, one task later.
Task 17b: fix round 1 landed — 5ac70df, FOLLOW-UP not an amend; f3f5a7f and the
  interleaved docs commit 47fc2d2 both untouched. 8 files, +233/-54.
  Suite 1581/7 (= 1577 + 4 regression tests); ruff, mypy, form gate all clean.
  THE "SHOW YOUR METHOD" DEMAND PAID FOR ITSELF, and this is the round's real
  result. Told to establish the absence claim properly rather than re-grep, the
  implementer INSTRUMENTED _frontmatter_attestation_outcomes to RAISE on any
  outcome under an env-var gate and ran the whole suite. That surfaced 17
  failures — 7 intentional-positive-drift tests, and 10 parametrized cases
  across THREE real functions. So THE REVIEW'S OWN TWO-SITE ENUMERATION WAS
  ITSELF INCOMPLETE: a third site
  (test_ack_suppresses_effects_but_retains_raw_outcome_and_reopens_on_hash)
  hand-edits fixity-sha256's VALUE rather than removing it, which is why a
  pattern search keyed to the removal shape missed it — and why the reviewer,
  searching the same way, missed it too.
  THAT IS THE DOCTRINE PROVING ITSELF TWICE OVER: the grep found what the grep
  was shaped to find, at BOTH levels; only making the tree object could
  enumerate the real set. Worth carrying forward as the standard remedy for any
  "I checked, there are no others" claim in this plan.
  IMPLEMENTER SELF-REPORTED A FAILED FIRST ATTEMPT rather than shipping it: its
  first Minor-B test DID NOT DISCRIMINATE, and it rewrote it after checking
  against the reverted code. Recorded as a positive — that is the exact failure
  mode this plan keeps catching in others, caught by the author of the code.
  CONTROLLER-READ THE DIFF BEFORE DISPATCHING THE RE-REVIEW:
   - _machine_attested now routes through notes._valid_generated first, then
     checks the prefix. Verified NO AttributeError risk: _valid_generated
     (notes.py:200) requires `isinstance(actor, str) and actor`, so
     generated["by"].startswith() cannot be reached on a non-string.
   - THE INTERLOCK CLOSED IN THE RIGHT DIRECTION: _valid_generated already
     demanded a Z-suffixed ISO 8601 `at`, and archive now stamps through
     notes.generated_at_now — so what archive EMITS and what the attestation
     ACCEPTS are one spelling and cannot drift apart. That was the specific
     hazard the interlocked dispatch named.
   - serialize's `elif isinstance(value, dict)` branch was FOLDED INTO
     render_field's else path. Reads equivalent — dicts still reach the dict
     emitter, lists still short-circuit above — but this is frontmatter.py, the
     byte-preservation core, and a module the brief NEVER NAMED.
Task 17b: fix round 1 re-review dispatched over f3f5a7f..5ac70df, on the most
  capable model because the round REFACTORED A CORE SERIALIZER to close a
  duplication finding. The re-review is required to REPRODUCE the instrumentation
  audit itself — not read its counts — and to confirm the enumeration is now
  complete at 5ac70df, since a third site emerged precisely because two prior
  searches shared a blind spot. It must also DIFFERENTIALLY TEST
  frontmatter.serialize byte-for-byte across both commits over a wide input
  range, because "the suite is green" cannot show a serializer refactor is
  behaviour-preserving on inputs the suite never exercises.

### SDD WORKSPACE NOW TRACKED — 95a81b3 (author ruling, relayed by the orchestrator)
  Task reports must survive the worktree: their "Concerns (not fixed)" sections
  were the only record of deferred work, and they lived ONLY in git-ignored
  scratch that dies with the worktree. 17b's round-0 concerns were headed exactly
  there. 92 files, +20926, committed as-is with explicit pathspec, no content
  edits. From Task 18 on, each task's report ships in that task's own commit.
  PREMISE VERIFIED, AND NOT WHERE I FIRST LOOKED: `cat .git/info/exclude` returns
  nothing here because `.git` IS A POINTER FILE, not a directory — the same fact
  behind the scratch-copy trap. Resolved through the common dir the rule is real:
  git check-ignore -v gives `/home/eranr/New folder/.git/info/exclude:49`. So the
  `-f` was genuinely required rather than defensive.
  CHECKED BEFORE COMMITTING, because tracking ~90 new markdown files is exactly
  how a form gate breaks: mdformat's hook entry is an EXPLICIT PATH LIST
  (`README.md AGENTS.md CONTEXT.md docs skills`) and _MDFORMAT_ROOTS at
  tests/test_config_validity.py:427 MIRRORS IT EXACTLY. Neither covers
  `.superpowers/`, so nothing pulls these files into the gate.
  TWO CONSEQUENCES RAISED WITH THE ORCHESTRATOR RATHER THAN LEFT TO SURFACE:
   - TASK 2e IS "FORM-GATE COHERENCE" AND HAS NOT RUN YET. If its implementer
     writes the obvious check — every tracked .md is formatter-owned or
     explicitly excluded — it now finds ~90 tracked-but-unowned files THAT DID
     NOT EXIST WHEN 2e WAS SPECIFIED. A collision this ruling created; cheap in
     2e's brief, expensive discovered mid-task. Carried into 2e's dispatch.
   - THE SDD SKILL'S OWN END-STATE NOW CONTRADICTS THE RULING: its final step is
     "delete this plan's workspace", which would delete the very files this
     commit exists to preserve. Author ruling governs; THE WORKSPACE IS NOT
     DELETED AT THE END OF THIS PLAN. Flagged for wherever the standing rule
     lives, since the next SDD run meets the same contradiction with nobody in
     the loop.
  ONE ITEM LEFT WITH THE ORCHESTRATOR TO DECIDE: the commit includes ~450KB of
  review-<base>..<head>.diff packages that are BYTE-RECONSTRUCTIBLE from git.
  Committed because the instruction named the directory and narrowing a stated
  scope on my own judgment is the wrong default — offered a correct-forward
  removal commit if they would rather main carry only reports, reviews, briefs
  and ledger.

SDD workspace: review packages UNTRACKED at cf3b17c (ruled — byte-
  reconstructible artifacts do not earn repo history; reports, reviews, briefs
  and the ledger do). 31 files, -7105 from the index, ALL 31 STILL ON DISK for
  the rest of the run. Tracked count 92 -> 61. Corrected FORWARD; 95a81b3 stands.
  A REAL TRAP IN THIS REPO'S OWN CONVENTION, worth carrying beyond this plan.
  AGENTS.md mandates explicit-pathspec commits (`git commit -- <files>`) because
  parallel sessions share the checkout. But `git commit -- <pathspec>` COMMITS
  THE WORKING-TREE STATE of those paths and IGNORES THE INDEX — so the
  `git rm --cached` I had staged was SILENTLY DISCARDED. The files stayed
  tracked, and the commit message asserted they had been removed.
  A CACHE-ONLY REMOVAL CANNOT BE EXPRESSED IN THE PATHSPEC FORM AT ALL; it has
  to go through the index. So the convention and the operation are genuinely
  incompatible here, and the safe procedure is: confirm `git status --porcelain`
  is EMPTY first (proving no parallel session has anything staged or dirty),
  then stage and commit through the index.
  CAUGHT BY VERIFYING RATHER THAN BY READING THE EXIT CODE: the commit reported
  "1 file changed, 35 insertions(+)" for what should have been 31 deletions, and
  `git ls-files .superpowers/ | wc -l` still said 92. Message amended at 2393658
  to state what the commit actually did and why, following the a3db464
  precedent for a false claim in a commit message.
  THE THROUGH-LINE AGAIN, this time in my own work: the commit was described
  from intent instead of derived from the result.

### TASK 18 PRE-CHECK (done while the 17b re-review runs; read-only, no collision)
  THE PLAN ASKS THE IMPLEMENTER TO "LOCATE IT — DO NOT INVENT A SECOND
  NORMALIZER". I looked, so the answer ships with the brief instead of costing a
  round: THERE IS NO GENERAL URL NORMALIZER IN THIS PACKAGE, established from
  THREE ANGLES rather than one grep, because an absence claim from a single grep
  is unfalsifiable by that same grep:
   - no `def` in knowledge_harness takes two URLs to compare (enumerated every
     def whose name carries url/link);
   - EVERY `netloc` use is a single-URL membership or equality test against a
     CONSTANT — archive.py:68, checks.py:713, checks.py:729, webapi.py:64 — never
     a two-URL comparison;
   - the only casefold-on-host idiom is arXiv-specific (_arxiv_identity,
     _arxiv_base_identity).
  So the plan's stated FALLBACK governs: exact match after stripping a single
  trailing slash and lowercasing scheme+host only.
  A DISAGREEMENT THE PLAN'S OWN SNIPPET WOULD INTRODUCE, and the important find:
  ARCHIVE_HOSTS is frozenset({"web.archive.org", "archive.org"}) — TWO hosts —
  but the plan's _SNAPSHOT_RE hardcodes ONLY `web\.archive\.org`. A snapshot on
  archive.org passes is_archive_url TODAY and would fail the new shape check. The
  tightening is probably RIGHT (a real Wayback snapshot always lives on
  web.archive.org; archive.org is the availability API host), but it is a
  behaviour change the plan never states, and it leaves TWO OVERLAPPING
  VALIDATORS DISAGREEING about what a snapshot URL is — the same "two spellings
  of one contract" shape Task 17b just spent a fix round eliminating. The
  implementer must state which one governs rather than let them drift.
  ASYMMETRY WORTH STATING TOO: _closest_snapshot (archive.py:129) already routes
  the CONFIRMED snapshot through is_archive_url, so both paths check host
  membership — but only the SUPPLIED path gains shape + target-URL checking.
  Lower exposure (the availability API is queried with params={"url": url}, so it
  answers about that URL), but the asymmetry should be deliberate, not accidental.
Task 18/final-review: minor (deferred) — MODULE MANIFESTS ARE STALE, 10 OF 25.
  knowledge_harness/*.manifest.json carry a source_sha256 per module; I compared
  each against the file it names: __main__, archive, checks, events, frontmatter,
  inbox, lints, notes, scaffold and verify are all stale — precisely the modules
  this batch touched. NO PYTHON FILE READS THEM (grep for manifest.json across
  *.py returns nothing), so no gate catches the drift and none can: they are
  mutate4py's own cache. INERT TODAY, and Plan W replaces that tool with mutmut
  (Tasks 23-25, out of scope here), which is the disposition — but recorded with
  the measurement rather than left as a vague "probably fine".

Task 17b: fix round 1 re-review — SOME OPEN. Every round-1 item addressed and
  revert-red, but one NEW IMPORTANT, and two of round 1's own findings only
  HALF-CLOSED. Review file: task-17b-rereview-r1.md
  WHAT THE RE-REVIEW ESTABLISHED BY RUNNING RATHER THAN READING:
   - 14 malformed `generated` shapes probed; at f3f5a7f SEVEN of them attested
     and legalized an archive-url edit, at 5ac70df all are blocked. Revert-red
     2/2. _machine_attested has exactly two call sites, both behind
     _valid_generated, so the AttributeError I checked for is UNREACHABLE —
     probed with "junk"/[1,2]/None: raises at base, returns False at head.
   - THE INSTRUMENTATION AUDIT REPRODUCED EXACTLY: 17 failed at f3f5a7f (7
     intentional + 10 real across the three named functions), 11 at 5ac70df, all
     intentional. NO MISSED SITE, and no env-gate trace shipped.
   - serialize BYTE-IDENTICAL across a 52-input differential (including
     _DuplicateKeyMapping at top level, inner and in-list, and 13 control-char
     raise-parity cases) — same md5 on both trees. That is what makes the core
     refactor safe to keep, and a green suite could never have shown it.
   - Boundary verified three ways: docstring carries §2's form plus piggy-backing
     (probed: legit bump + unrelated citekey edit -> n=0), ZERO production reason
     strings changed, ZERO ADRs added.
  A METHOD FINDING WORTH KEEPING: an import-path canary caught an EDITABLE
  INSTALL resolving `knowledge_harness` to the PARENT repo instead of the scratch
  tree. Every scratch probe in this plan has been at risk of silently measuring
  the wrong code; from now on scratch dispatches carry `PYTHONPATH=.` and a canary.
Task 17b: IMPORTANT (N1) — THIS TASK DISARMED A PRE-EXISTING TEST, and the
  implementer had judged exactly this benign in its concern 3. Controller
  confirmed by reading the test: tests/test_lints.py:751-755 takes the FIRST
  UNMATCHED outcome and asserts only `reason.startswith("drift")`. The [edit]
  case refreshes the managed witness, so managed-sha256 changes with no
  `generated` bump and the NEW check emits a SECOND drift outcome carrying THE
  SAME TARGET. If the managed-region comparison broke, the attestation outcome
  now satisfies the assertion in its place.
  MUTATION PROOF on lints.py:779: 1 failed at a2d7942, 0 failed at BOTH f3f5a7f
  and 5ac70df. The test caught that regression before this task and does not now.
  AND THE REPO'S OWN MUTATION GATE IS BLIND TO IT — the `!=`->`==` operator mutant
  it generates is still killed (9 failures), so nothing downstream would ever
  report the loss. A loose assertion is how a guard gets disarmed without any
  test turning red; this is the second instance this plan has caught, after Task
  17's fixture migration.
Task 17b: fix round 2/5 dispatched — N1 plus three items that are NOT new minors
  but ROUND 1'S OWN FINDINGS LEFT HALF-CLOSED, which is why they re-enter the
  loop rather than the deferred list:
   - N2: Minor C half-closed. Base frontmatter unparseable AND candidate carrying
     an intact machine `generated` yields ZERO findings — same as pre-fix,
     because the changed side AUTO-ATTESTS. The test name and 5ac70df's commit
     body both say "fail-closed"; for this path it is not, so a commit body
     asserts something untrue. Correction goes in round 2's body, not an amend.
   - N3: Minor A half-closed. One "now" spelling remains, but the inline-dict
     emitter is STILL WRITTEN TWICE (frontmatter.py:73-77 and :88-92).
   - N4: notes._valid_generated is now the SOLE definition of `generated`'s shape
     — attestation, render trigger and archive's round-trip all bottom out in it
     — and it has NO DIRECT TEST; render_field and generated_at_now have zero
     test references; frontmatter.py is mutation-excluded, so nothing else would
     catch a regression either. The task made it load-bearing without covering it.
  Dispatch also carries the new report-in-task-commit rule and the explicit
  instruction NOT to re-add the review packages untracked at cf3b17c.

### TASK-REPORTS RULE REWORKED (author, relayed by the orchestrator) — THE SKILL
### OVERRIDE IS GONE, AND THAT IS THE BETTER SHAPE
  New form: a report NAMES A DESTINATION PER CONCERN AT WRITE TIME, and a plan's
  workspace closes only once every Concern's disposition has landed in its
  durable home. The SDD skill's Finish delete then runs AS WRITTEN, because by
  then it destroys only exhaust. That eliminates the contradiction I flagged
  rather than papering over it with an override — the mechanism moved up a rung,
  exactly as AGENTS.md orders the choices.
  FOR POST-Q, NOTHING CHANGES and one thing is explicitly ruled OUT: the
  committed workspace (95a81b3 + cf3b17c) STANDS — it was the rescue for concerns
  written BEFORE write-time destinations existed — and NO DELETION COMMIT is
  added at Finish. The workspace is already history; deleting it now would
  destroy the very record the rescue created.
  ACTED ON IMMEDIATELY rather than deferred to Task 18: sent an addendum to 17b's
  in-flight round-2 implementer requiring a destination per Concern, including
  re-stating destinations for the three carried from rounds 0 and 1 (unguarded
  MANAGED_FIELDS keys; duplicate-key evasion; renamed files skipping the per-key
  diagnostic — destination: controller files them as GitHub issues at plan
  close). Told it explicitly that AN HONEST DECLINE IS A DISPOSITION AND SILENCE
  IS NOT, so "no destination" cannot be the cheap answer.
  STANDING CHANGE TO EVERY REMAINING DISPATCH: reports ship in the task commit,
  and every Concern names its destination at write time.

Task 17b: BOTH FINDINGS ROUTED TO DURABLE HOMES, and I VERIFIED BOTH rather than
  record them on the relay — AGENTS.md's own "fetch before claiming something is
  absent from origin" cuts both ways:
   - `gh issue view 22` -> OPEN, "Sweep loose prefix assertions on outcome reason
     strings", labels enhancement + needs-triage. Candidate home named as Plan
     W's quality tail, WHICH KEEPS THIS BATCH'S FREEZE INTACT — the sweep is a
     real task and it is deliberately NOT this plan's. DESTINATION RULE FOR ME:
     when round 2 pins the exact reason strings, they go as a COMMENT ON #22, not
     as a new issue.
   - `git fetch` then `git show 3faab3c` -> real, and it is the CURRENT TIP of
     origin/main: "testing: wrong-tree import trap (PYTHONPATH=. + canary for
     scratch probes)", 4 lines into docs/testing.md. My dispatch-level fix
     stands; the doc is what makes it outlive this plan and this session.
  ORIGIN/MAIN HAS MOVED (3faab3c, and f9d95df's pathspec exception before it).
  NOT MERGING NOW — the standing ruling is merge at a Part boundary and Part 2 is
  not done. Recorded so the divergence is a known quantity rather than a surprise
  at Task 21.

Task 17b: fix round 2 landed — 1441e7f, follow-up not an amend. 6 files
  including task-17b-report.md, THE FIRST COMMIT UNDER THE NEW
  REPORT-IN-TASK-COMMIT RULE. progress.md deliberately EXCLUDED from its
  pathspec because the controller was editing it concurrently — the right call,
  and exactly why the explicit-pathspec convention exists in a shared checkout.
  No review-*.diff re-added. Suite 1605/7 (+24: 1 for N2, 17 in test_notes.py and
  6 in test_frontmatter.py for N4); ruff, mypy, form gate clean.
  ALL FOUR CONCERNS NOW CARRY DESTINATIONS, per the addendum — three routed to
  "controller files as GitHub issues at plan close", and the fourth is AN EXPLICIT
  DECLINE WITH A REASON (_valid_generated's keyset-equality clause judged
  behaviourally redundant with its own later type checks; kept for readability).
  That is the shape the new rule wanted: silence would not have been a
  disposition, and a decline is.
  IMPLEMENTER SELF-REPORTED A SECOND FAILED PROBE — its first N4 mutation "turned
  out not to be a real mutant" and was redone. Second time this task it has
  disclosed a method failure rather than shipping past it.
  CONTROLLER-READ THE PRODUCTION DIFF BEFORE DISPATCHING:
   - N3's extraction also removes a confusing `key` SHADOW in serialize's
     list-of-dicts comprehension. Harmless in Python 3 (comprehensions own their
     scope) but it made the duplicate genuinely hard to see as a duplicate.
   - N2's guard is `attested = base_data is not None and generated_changed and
     _machine_attested(...)`. AN ASYMMETRY IT LEAVES, which I am sending to the
     re-review AS A QUESTION rather than a verdict: the SECOND predicate, the
     `generated`-guards-itself block, did NOT get the base_data guard. So with an
     unparseable base and a machine-shaped candidate `generated`, the four keys
     now flag but `generated` ITSELF does not. My reading is that the four-key
     findings always fire first so no file passes silently — but that is a
     reading, and the re-review is asked to settle it empirically and give
     reasoning rather than a verdict.
Task 17b: fix round 2 re-review dispatched over cf3b17c..1441e7f (the round-2
  commit ALONE — the three intervening docs commits are excluded by choosing its
  parent as base, so the reviewer sees the fix and nothing else). Required to
  rebuild the lints.py:779 mutant and show it now goes RED; to confirm EVERY
  `change` parameter is pinned rather than only the one the finding named; to
  differentially test serialize AND render_field byte-for-byte across both
  commits INCLUDING exception parity, since frontmatter.py is mutation-excluded
  and nothing else guards it; and to prove each new N4 test discriminates by
  mutation, PER TEST rather than in aggregate.
  ALSO ASKED TO FALSIFY THE DECLINE: construct an input the keyset-equality
  clause rejects that the type checks would accept, or show none exists — because
  A WRONG REDUNDANCY CLAIM LEFT IN A REPORT BECOMES A FUTURE DELETION.
  AND CARRIES THE WRONG-TREE IMPORT CANARY as a hard precondition, per
  docs/testing.md on main.

Task 17b: fix round 2 re-review — N1-N4 ALL GENUINELY FIXED, four new Minors.
  Review file: task-17b-rereview-r2.md (608 lines).
  THE EVIDENCE, all reproduced rather than read:
   - N1 RE-ARMED: the reviewer's own `if False:` neuter on lints.py:787 SURVIVES
     at cf3b17c (0 failed / 1581 passed) and is KILLED at 1441e7f (1 failed) by
     test_managed_change...[edit]. All FOUR parametrize values pin
     expected_reason, and `next()` was replaced by a comprehension filtered on
     result AND target — so wrong-outcome substitution is closed structurally,
     not just for the one parameter the finding named.
   - N2 CLOSED: the exact case goes n=0 -> n=4. Reverting only `base_data is not
     None` reds the new test with `assert []`.
   - N3 BYTE-IDENTICAL over 251 evaluations per SHA — and crucially 107 RAISES
     IDENTICAL IN TYPE AND MESSAGE, which a same-output comparison alone would
     have missed.
   - N4 discriminates, 8 of 10 mutants killed cleanly; the implementer's
     "first probe wasn't a real mutant" self-report VERIFIED ACCURATE.
  THE N2 ASYMMETRY I FLAGGED — ANSWERED, AND MY READING WAS WRONG IN THE DETAIL.
  The asymmetry is CORRECT by design: the two predicates answer different
  questions ("is there evidence of a legitimate write in this diff?" is
  unanswerable with an unreadable base, so it fails closed; "is this value
  machine-shaped?" is answerable from the candidate alone, so guarding it would
  emit a false positive about a perfectly valid `generated` because a DIFFERENT
  line is malformed). But I claimed the four-key findings always catch it, and
  THEY DO NOT: base unparseable + machine `generated` + NONE of the four keys
  gives n=0 at both SHAs. The file still fails end to end — netted by
  notes.validate_managed_witness with `schema-violation — missing managed-sha256`,
  which runs unconditionally upstream. Since managed-sha256 IS one of the four
  keys, the split is exhaustive: present -> four-key rule flags, absent -> witness
  rule flags. Harmless, BUT BY A SIBLING CHECK, NOT THE RULE I NAMED. Recorded
  because "I reasoned it was covered" and "I measured what covers it" are
  different claims, and only the second one is worth anything.
Task 17b: fix round 3/5 dispatched — four items, three of them ACCURACY DEFECTS
  and one the task's recurring failure mode:
   - N6: THE N1 DEFECT CLASS REINTRODUCED IN THE COMMIT THAT FIXED N1.
     tests/test_lints.py:1082 filters on TARGET ONLY, no Result filter and no
     reason pinned, then asserts truthiness. CONTROLLER CONFIRMED BY READING IT:
     `schema-violation — missing managed-sha256`, `— malformed managed boundary`
     and `drift — managed literature region changed` ALL carry that same target,
     so the test stays green even if the attestation outcomes vanish entirely.
     Third instance in this task of one shape — an assertion loose enough to be
     satisfied by the wrong outcome.
   - N7: the concern-4 decline is TRUE AS SCOPED AND DANGEROUSLY WORDED. Dropping
     the keyset clause alone: 0 divergences over 15,901 inputs, suite green — a
     genuine equivalent mutant, so the implementer was right. Dropping
     `len(items) != 2` alone: 144 divergences, AND THAT MUTANT SURVIVES THE FULL
     SUITE. CONTROLLER VERIFIED THE DECISIVE CASE DIRECTLY: `generated: {by:
     "human:eran", by: "knowledge_harness/0.1.0", at: <valid>}` PARSES, keeps
     both `by` entries, `.get("by")` LAST-WINS RETURNS THE MACHINE ACTOR, and
     _valid_generated rejects it ONLY via the length check — the keyset check
     passes it. So the clause called redundant SHARES AN `if` WITH THE SOLE
     REJECTER OF DUPLICATE-KEY `generated` FORGERY, and a reader acting on
     "behaviourally redundant" deletes the line and opens that path. Round 3 must
     amend the concern to separate the two sub-clauses AND add a
     duplicate-by-last-wins rejection parameter, since the suite is blind to it.
   - N8: the report's and commit body's N1 mutation account names the WRONG
     MUTANT (the `==` flip, which round 1 had already calibrated as killed, not
     the `if False:` neuter actually run) and the WRONG BEFORE-NUMBER (that flip
     fails 3 of 4 params at cf3b17c, not 0). Correction goes in round 3's body
     per the a3db464 precedent, not an amend.
   - N5: test_render_field_matches_serialize... COMPARES render_field TO ITSELF,
     because serialize's non-list branch routes through render_field. Worth
     having as a call-site-agreement pin, but the report calls it "proving the
     one-spelling property", which it does not.
  Dispatch names issue #22 as N6's destination, with the pinned strings to be
  added there as a COMMENT rather than a new issue.

Task 17b: fix round 3 landed — ff6b2f3, follow-up not an amend. 4 files,
  +225/-24, and ZERO PRODUCTION LINES: tests and the report only, which is the
  right shape for a round whose four findings were all accuracy defects.
  Suite 1606/7 (+1: duplicate-by-last-wins); ruff, mypy, form gate clean.
  progress.md again excluded from the pathspec for the concurrent-edit reason.
  CONTROLLER-READ THE DIFF, and two choices are better than they had to be:
   - N7's _DUPLICATE_BY_LAST_WINS is built by ACTUALLY CALLING frontmatter.parse
     on a duplicate-`by` source line, NOT by hand-constructing a dict that
     imitates one. That matters: a hand-built fake would pin the predicate
     against a shape the parser might never produce, which is how a test comes to
     defend an unreachable case while the reachable one walks past. Parsing it
     proves reachability and the rejection in a single artifact.
   - N6's pinned set is a SET OF EXACT REASONS with a comment naming the three
     decoy reasons that share the target. The fix does not merely tighten the
     assertion, it records WHY tightening was necessary — which is what stops the
     next person loosening it back.
  N8 IS THE ONE WORTH KEEPING: the implementer had named and run the WRONG MUTANT
  and reported a wrong before-number, then re-ran the real one in isolated
  scratch trees at both SHAs and recorded the correction AS AN ERRATUM rather
  than silently rewriting the original text. Third disclosed method failure from
  this implementer in one task. A run where the implementer's self-reports are
  reliable is a different kind of run, and it is worth saying so explicitly.
Task 17b: fix round 3 re-review dispatched over 1441e7f..ff6b2f3, on a mid tier
  rather than the top one — the diff is small and touches no production code, and
  the skill's own guidance sizes re-reviews to the diff. Required to:
   - suppress _frontmatter_attestation_outcomes entirely and show the N6 test was
     GREEN at 1441e7f and RED at ff6b2f3, which is the only thing that proves the
     pin does work the loose version did not;
   - check the pinned set is neither over- NOR under-specified against the
     fixture's actual outcomes, since an over-specified set is its own defect;
   - answer why `archive-url` — one of the four machine-owned keys — is ABSENT
     from the pinned set, and whether that absence is correct or a gap;
   - falsify the amended concern in BOTH directions: dropping `len(items) != 2`
     must red the new parameter, and dropping the keyset clause must leave the
     suite green. An amendment that is only checked in the direction it now
     emphasises is half-checked.
   - judge the MODULE-IMPORT-TIME parse behind _DUPLICATE_BY_LAST_WINS, since a
     raise there would fail collection of the whole test module rather than one
     test.
  And told outright to assume THE RECURRING DEFECT CLASS CAN APPEAR IN THE FIX
  FOR IT — it has already appeared three times in this task, once inside the
  commit that fixed it.

Task 17b: fix round 3 re-review — ALL ADDRESSED. One new Minor, and it landed on
  ME. Review file: task-17b-rereview-r3.md
   - N5 rename verified: body BYTE-IDENTICAL by diff, only name and docstring
     changed, so the rename did not quietly weaken the test.
   - N6 pinned set verified COMPLETE AND CORRECT by debug print — exactly
     {citekey, fixity-sha256, managed-sha256}, all UNMATCHED, nothing else shares
     the target. Neither over- nor under-specified.
   - N7 falsified in BOTH directions, which is what the dispatch demanded:
     dropping only `len(items) != 2` REDS duplicate-by-last-wins (1 failed / 16
     passed); dropping only the keyset clause leaves the FULL SUITE GREEN. The
     amended concern's split is accurate both ways, not just the way it now
     emphasises.
   - N8 rebuilt: cf3b17c 0 failed / 1581 passed, 1441e7f 1 failed. Matches the
     corrected account exactly, and the erratum is APPENDED AFTER the untouched
     original wrong paragraph rather than replacing it.
   - archive-url's absence from the pinned set is CORRECT, not a gap: the fixture
     note never sets that key on either side, so None != None yields nothing.
   - The module-import-time parse is acceptable: a frontmatter.parse regression
     becomes a whole-module COLLECTION ERROR for test_notes.py — loud, and
     undegraded on coverage, only on diagnostic granularity.
Task 17b: THE NEW MINOR WAS MY ERROR, NOT THE IMPLEMENTER'S. The comment
  justifying the pinned set claimed a looser assertion would be satisfied
  "including one where the attestation check's own findings had vanished
  entirely". FALSE — AND THE FALSE CLAIM CAME FROM MY OWN ROUND-3 DISPATCH,
  pasted into the comment because I asserted it.
  I MEASURED IT BOTH WAYS in a canary-checked scratch tree at 1441e7f rather than
  take the reviewer's word about my own mistake:
   - full suppression (_frontmatter_attestation_outcomes returns []) -> the LOOSE
     assertion FAILS. This fixture corrupts the BASE and leaves the candidate
     PRISTINE, so no schema-violation or managed-region finding carries that
     target at all; zeroing the check empties the list and truthiness notices.
     My "decoys are always present" premise was reasoning about a DIFFERENT
     scenario than the one the fixture builds.
   - partial loss (only the citekey outcome dropped) -> the LOOSE assertion
     PASSES. THAT is the real reason to pin the set: a truthiness check survives
     losing any single reason because the remaining two keep it non-empty.
  Corrected at 18ba920, comment-only, with the commit message naming the error as
  mine and carrying both measurements. Did NOT spend a fifth round on a one-line
  comment whose falsehood I authored.
  THE THROUGH-LINE, THIRD TIME AGAINST MY OWN WORK: described from reasoning
  instead of derived from the thing itself. It is worth noting the shape it took
  here — I did not invent a fact, I generalised a TRUE fact about one scenario
  onto a fixture that does not build that scenario. That is the harder version to
  catch, because the claim is true somewhere.
Task 17b: complete (commits a2d7942..18ba920 — f3f5a7f, 5ac70df, 1441e7f,
  ff6b2f3, 18ba920 — review clean after 3 fix rounds, 3 minors deferred).
  Ticked at the plan commit below: 4 boxes; 68 checked / 44 unchecked.
  Suite 1606/7; form gate exit 0. Both re-verified by the controller.
  FOUR ROUNDS, AND THE TASK EARNED THEM: it began as "add a check", and the
  review loop turned up a version-bump time bomb (pre-check), an attestation that
  accepted malformed input, a partial absence claim that hid a third defect site,
  a disarmed pre-existing test, a commit body asserting fail-closed behaviour it
  did not have, a wrong mutation account, and a decline whose wording invited a
  deletion that would reopen a forgery path. NONE of those were the original
  defect; all of them were real.
Task 17b: minor (deferred): other MANAGED_FIELDS keys (type, aliases, doi, url,
  pmid, version, accessed) remain outside the guard — the brief scoped it to five
  keys. Destination: GitHub issue at plan close.
Task 17b: minor (deferred): DUPLICATE-KEY EVASION at the parser — .get() is
  last-wins, so a duplicated machine-owned key whose final copy matches base
  evades the value comparison. Only managed-sha256 has an independent duplicate
  guard. Destination: GitHub issue at plan close. This is the one with teeth.
Task 17b: minor (deferred): renamed files get the wholesale "note renamed" drift
  but skip the per-key attestation diagnostic. Destination: GitHub issue at plan
  close.

Task 18: BASE = c010d0f. Implementer DONE (commit f05103e; 3 files, +312/-0,
  including its report per the new tracking rule; progress.md correctly
  untouched). Suite 1611/7 (= 1606 + 5); ruff, mypy, form gate clean.
  THE PRE-CHECK'S TWO HAND-OVERS BOTH LANDED: no URL normalizer was invented
  beyond the stated fallback (_comparable_url lowercases scheme+host and strips
  ONE trailing slash, nothing more), and the host disagreement was decided
  deliberately rather than inherited.
  AND THE IMPLEMENTER REVERSED MY DISPATCH'S IMPLIED PREFERENCE ON EVIDENCE,
  WHICH IS THE RIGHT WAY TO BE OVERRULED. I had framed the two overlapping
  validators as the "two spellings of one contract" defect and invited merging
  them. It kept them LAYERED and justified it by measurement: _SNAPSHOT_RE ALONE
  WOULD ADMIT A SNAPSHOT STRING WITH A TRAILING NEWLINE, because Python's `$`
  MATCHES BEFORE A TRAILING `\n`, and is_archive_url's splitlines() check is what
  actually blocks it.
  CONTROLLER VERIFIED THAT DIRECTLY rather than accept it: the regex returns
  True on "...paper\n" and False on "...paper\nevil", and splitlines() sees the
  trailing-newline case. So the layering is load-bearing, not redundancy — and my
  "two validators disagreeing" framing was right about the DISAGREEMENT and wrong
  about the REMEDY. Merging them would have removed a guard.
  This matters beyond the task: a trailing newline in a value bound for
  frontmatter is exactly the second-line forgery that _emit_scalar exists to
  refuse, so the guard sits in a family with a known threat, not in isolation.
Task 18: review dispatched over c010d0f..f05103e on the most capable model. The
  target-match decision rests entirely on _comparable_url, so the review is told
  to probe it ADVERSARIALLY rather than read it — no path, query or fragment
  ending in `/` (does removesuffix strip from the QUERY instead of the path?),
  explicit default port, percent-encoding, UPPERCASE IN THE PATH (which must NOT
  be lowercased, since paths are case-sensitive), http-vs-https for one host,
  trailing `//`, empty string — and to flag anything TOO PERMISSIVE, since a
  loose normalizer silently re-opens the hole the task closes.
  Also required: a PER-TEST discrimination matrix, and one specific probe for
  this plan's recurring defect — archive_source has several UNMATCHED paths all
  reading `missing-archive — ...`, so the reviewer must make the targeted path
  emit a DIFFERENT `missing-archive —` reason and confirm the test still fails.
  Prefix-sharing is precisely how the previous four instances hid.
Task 18: minor (deferred, PRE-EXISTING): test_a_supplied_snapshot_off_the_
  archives_host_is_refused asserts only Result.UNMATCHED with no reason pinned.
  The implementer declined it as out of scope, which is right — but THIS DIFF ADDS
  TWO MORE `missing-archive —` UNMATCHED PATHS TO THE SAME FUNCTION, so the
  pre-existing looseness now has more ways to be satisfied by the wrong outcome
  than it did before. Recorded as a question for the review rather than asserted:
  is that test WEAKER than it was? Destination: GitHub issue #22, the loose-
  prefix-assertion sweep.

Task 18: review returned — spec PASS, quality PASS with 3 Important / 7 Minor.
  Review file: task-18-review.md
  SPEC CHECKED THE WAY IT SHOULD BE: both reason strings BYTE-COMPARED brief to
  source to tests, em dash (\xe2\x80\x94) included; the regex reproduced character
  for character; and the normalizer-absence claim RE-GREPPED WITH DIFFERENT TERMS
  than the report used — which is the only way a second search adds anything,
  since repeating the first one just reproduces its blind spot.
  THE RECURRING LOOSE-ASSERTION DEFECT DOES NOT APPEAR IN THE NEW TESTS, and that
  was PROVEN rather than asserted: R1 and R2 swapped each targeted path's reason
  for a DIFFERENT `missing-archive — ...` string and the tests still went red. So
  the new assertions are outcome-specific, not prefix-specific. Five clean
  discrimination mutants besides (M1-M5), each reddening exactly one test.
  IMPORTANT F2 — AND IT IS THE FIFTH INSTANCE OF THE CLASS, WITH A TWIST: THE
  IMPLEMENTER SHIPPED AN EVIDENCE-BACKED ARGUMENT FOR KEEPING A GUARD AND NO TEST
  FOR THE GUARD. Deleting `if not is_archive_url(snapshot):` from the supplied
  branch leaves the WHOLE OFFLINE SUITE GREEN. CONTROLLER REPRODUCED IT in a
  canary-checked archive tree: tests/test_archive.py goes 48 passed / 1 skipped
  with the gate deleted. So is_archive_url on that branch is detected by ZERO
  tests repo-wide, and the newline-smuggling case the layering argument RESTS ON
  is pinned only on the CONFIRMED path, never the supplied one.
  The diff also DISARMED test_a_supplied_snapshot_off_the_archives_host_is_refused
  (:315), which asserts only Result.UNMATCHED: the two NEW `missing-archive —`
  outcomes can now satisfy it in place of the host check. The implementer's
  concern 2 declined retrofitting that test as out of scope — RIGHT BEFORE THIS
  DIFF, WRONG AFTER IT, and the report misses that its own change is what moved
  the line. I had flagged this exact question to the review; the answer is yes,
  the test is weaker than it was.
  IMPORTANT F3 — commit body EMPTY AGAIN (second task running). The host-split
  decision, the layering reasoning and the deliberate asymmetry live only in the
  report. The repo's own hygiene doctrine routes that material to the commit
  body, so with no body it has nowhere to live and ends up in comments instead.
  IMPORTANT F1 / F8 — two statements the code now falsifies: ARCHIVE_HOSTS's
  comment "the only hosts a recorded snapshot may live on" and the module
  docstring's "records only what the availability API returns". Both were true
  before the supplied branch tightened.
  _COMPARABLE_URL IS MEASURABLY TOO PERMISSIVE — CONTROLLER PROBED IT DIRECTLY
  rather than take the table:
    'https://example.org/p?a=b/'  vs '.../p?a=b'  -> True   WRONG
    'https://example.org/p#frag/' vs '.../p#frag' -> True   WRONG
    'https://exa\tmple.org/p'     vs '.../p'      -> True   WRONG
    'https://example.org/PAPER'   vs '.../paper'  -> False  correct
  F4: removesuffix("/") runs on the RECOMPOSED url, so it strips the slash off a
  QUERY or FRAGMENT rather than the path.
  F5, and the sharper one: urlsplit SILENTLY STRIPS TAB CHARACTERS, so a snapshot
  whose `original` carries a tab compares EQUAL to the clean note URL, passes both
  gates, and then raises an UNCAUGHT FrontmatterError out of archive_source at
  render_field — breaking the four-state contract for a verb that must return an
  Outcome, never raise. A value that survives validation and explodes at write
  time is the wrong failure mode for durable vault content.
  A SECOND REASON FOR THE ORDERING, which the implementer had not stated and the
  review found: `web.arch\tive.org` PASSES is_archive_url (urlsplit strips the
  tab) but FAILS the regex — so control characters must be screened first. The
  host-then-shape order is load-bearing for a reason beyond the one given.
Task 18: fix round 1/5 dispatched — F1, F2, F3 (Important), F4, F5, and the
  cheap correctness items F6 (a capturing group never read), F7 (a test named
  bare_domain whose body supplies a full capture path) and F8. F9's unpinned
  boundary cases go in too, justified explicitly by F2's lesson: "behaves
  correctly and is untested" IS the state that lets a guard be deleted silently.
Task 18: minor (deferred): the confirmed-path residual — a payload whose
  closest.url points at a different site is still MATCHED and recorded verbatim.
  Deliberate and out of scope. Destination: GitHub issue at plan close.
Task 18: minor (deferred): archive.py.manifest.json not refreshed — already stale
  at c010d0f, and the tool that reads it is replaced in Plan W. Destination: the
  measured manifest-staleness note already in this ledger (10 of 25).

Task 18: fix round 1 landed — 2fbad42, follow-up not an amend. 3 files,
  +424/-24, report included, progress.md correctly excluded. Suite 1621/7 (+10);
  ruff, mypy, form gate clean. THE COMMIT BODY IS 112 LINES — F3 answered in the
  only way that counts, since a body is where this repo's doctrine sends the
  reasoning that would otherwise silt up in comments.
  CONTROLLER SETTLED THE ONE QUESTION THE FIX RAISED, BY MEASUREMENT, BEFORE
  DISPATCHING THE RE-REVIEW. The F5 guard is `"\t" in snapshot` — TAB ONLY — and
  I had handed the implementer exactly one example, a tab. An under-fix shaped to
  my example was the obvious risk. So I ENUMERATED every character that both
  PASSES is_archive_url AND is STRIPPED BY urlsplit:
      char    is_archive_url   urlsplit_strips   reaches the gap
      \t      True             True              TRUE
      \r      False            True              False
      \n      False            True              False
      \v \f \x1c \x1d \x1e \x85        neither, on both counts
      space   True             False             False
  TAB IS THE ONLY ONE. The guard is complete today, and it is complete for a
  reason worth stating: \r and \n ARE stripped by urlsplit, and the only thing
  stopping them is is_archive_url's splitlines() check upstream.
  WHICH MAKES THE REAL FINDING A COUPLING, NOT A GAP: the tab-only guard is
  correct ONLY WHILE is_archive_url keeps rejecting \r and \n. Loosen that
  upstream check and this one silently becomes incomplete. The guard's comment
  mentions only the tab/urlsplit interaction and not the dependency — and a
  constraint the code cannot show is exactly what a comment is for here. Sent to
  the re-review as a judgement call rather than a verdict.
  ALSO CONFIRMED BY READING THE DIFF: _comparable_url now strips the trailing
  slash from parts.path BEFORE recomposing, which is the right fix for F4 — the
  bug was that removesuffix ran on the recomposed string and so could strip a
  query's or fragment's slash instead of the path's.
Task 18: fix round 1 re-review dispatched over f05103e..2fbad42, mid tier — the
  subtle question is already answered and what remains is discrimination
  checking. Handed the reviewer my character enumeration explicitly SO IT DOES
  NOT REDO IT, and pointed it at the coupling question instead. Required to:
   - delete the is_archive_url gate at 2fbad42 and name WHICH tests go red,
     since F2 was precisely "no test detects this" and only a deletion proves it
     now does;
   - confirm the new newline test exercises the SUPPLIED path, not the confirmed
     path where that case was already covered — a regression test placed on the
     wrong branch would look like coverage and be none;
   - probe _comparable_url on a fragment ending in `/`, a path of exactly `/`,
     an empty path and a path ending `//`, not just the query case I named;
   - re-run the reason-swap probe on every NEW test, because five instances of
     the loose-assertion defect say the sixth is likelier than the base rate.

Task 18: fix round 1 re-review — ALL ADDRESSED. Two new Minors, both created by
  the round. Review file: task-18-rereview-r1.md
   - F2 PROVEN CLOSED THE ONLY WAY IT COULD BE: deleting the is_archive_url gate
     now reddens EXACTLY 2 tests, where before it reddened NONE. And the newline
     regression test was confirmed to exercise the SUPPLIED path — a test of the
     right case placed on the wrong branch would have looked like coverage and
     been none.
   - F4 verified in both directions: `.../p?a=b/` vs `.../p?a=b` now UNEQUAL,
     while `.../p/` vs `.../p` stays EQUAL. A fix that only moved the bug would
     have shown up here.
   - F5's crash reproduced end to end with the clause removed, and a clean
     Outcome with it restored.
   - F9: 4 of 4 targeted regex mutations reddened exactly their own test.
   - THE RECURRING DEFECT IS ABSENT, AND DEMONSTRATED ABSENT: a `\w+://` mutation
     made a test fail via a DIFFERENT `missing-archive — ...` reason, which is
     the discriminator. Sixth task in a row where this was checked by swapping
     the reason rather than by reading the assertion.
### THE WRONG-TREE IMPORT TRAP CAUGHT ME — the controller, who had put the
### warning in four consecutive dispatches
  I ran a probe as `python /tmp/probe.py` from this worktree. That puts /tmp on
  sys.path[0], NOT the worktree, so `knowledge_harness` resolved to the EDITABLE
  INSTALL AT THE PARENT REPO — /home/eranr/New folder/knowledge_harness/archive.py
  — and the probe measured code that does not contain Task 18 at all. PROVEN, not
  surmised: running the same import with cwd=/tmp prints the parent path.
  IT ONLY FAILED LOUDLY BY LUCK. `_comparable_url` does not exist in the parent
  tree, so it raised AttributeError. Had I probed a function that exists in BOTH
  trees, I would have received a plausible wrong answer and never known.
  AND I HAD ALREADY DONE EXACTLY THAT: the character enumeration behind the
  tab-only completeness claim ran the same way. It happens to stand — I checked
  `is_archive_url` BYTE-IDENTICAL between origin/main and this branch, and the
  probe used only that function plus stdlib urlsplit — and I RE-RAN IT IN-TREE
  with the canary asserted, same table. But the claim was right by accident of
  the code being unchanged, not by method, and those are different things.
  THE HABIT THAT CAUSED IT is worth naming because it was formed for a good
  reason: I put helper scripts in /tmp to avoid polluting a tracked tree. That
  reflex is correct about the tree and wrong about sys.path. Fix: run probes with
  the working directory INSIDE the tree under test and assert
  knowledge_harness.archive.__file__ before trusting any result. Wrote the probe
  into the worktree, ran it, deleted it, confirmed `git status` clean.
Task 18: fix round 2/5 dispatched — two items, both this round's own making:
   - the tab-only guard is COMPLETE TODAY but its completeness DEPENDS on
     is_archive_url continuing to reject \r and \n upstream; nothing anywhere
     says so, and loosening that check would silently under-cover this one. One
     line, naming the dependency.
   - F4's fix also flipped `.../p/?a=b` and `.../p/#frag` from UNEQUAL to EQUAL —
     consistent with the stated contract, so not a defect, but NEW BEHAVIOUR
     PINNED BY NOTHING. Pin them, and pin the two that must NOT flip beside them
     (`.../p?a=b/` stays UNEQUAL; `.../p//` stays UNEQUAL — one slash, not all).
  Both measured in-tree with the canary asserted, after the lesson above.

Task 18: fix round 2 landed — 3bd8f21. 3 files, +167/-0; ONE production line pair
  (a two-line comment) and 3 tests. Suite 1624/7.
Task 18: ROUND-2 RE-REVIEW DONE BY THE CONTROLLER, NOT DELEGATED — deliberate,
  and worth recording as a judgement rather than a shortcut. The round was one
  comment plus three pins, and both of its claims are settleable by two mutants,
  so an agent dispatch would have added latency without adding evidence. The
  standard still applied: REPRODUCED, in a canary-checked `git archive` tree,
  never `cp -r`, and never from a /tmp working directory after this morning's
  lesson.
   - Revert the F4 fix (path-only strip back to strip-on-recomposed): FOUR tests
     red, and they are exactly the right four — BOTH the widening pins
     (trailing_slash_before_the_query_or_fragment_still_matches, query-string and
     fragment) AND the must-not-match pins (trailing_slash_OUTSIDE_the_path, same
     two ids). A pin that only caught one direction would have left the other
     free to drift.
   - Swap removesuffix("/") for rstrip("/"): EXACTLY ONE test red,
     test_supplied_snapshot_with_two_trailing_path_slashes_does_not_match. That
     is the mutant that distinguishes "strip ONE slash" from "strip all", which
     is the actual contract, and nothing else in the file notices it.
  Both mutants isolate cleanly. Gates re-run in the real tree by me: 1624 passed
  / 7 skipped, form gate exit 0.
  THE COMMENT LANDED IN THE RIGHT SHAPE TOO: two lines naming the dependency
  ("checking only for a tab here depends on is_archive_url, above, having already
  rejected \r/\n via its splitlines() check"), with the full character
  enumeration and its consequence in the COMMIT BODY. Constraint in the comment,
  evidence in history — which is the repo's doctrine applied rather than quoted.
Task 18: complete (commits c010d0f..3bd8f21 — f05103e, 2fbad42, 3bd8f21 — review
  clean after 2 fix rounds, 3 minors deferred). Ticked below: 4 boxes;
  72 checked / 40 unchecked. Suite 1624/7; form gate exit 0.
  WHAT THE LOOP BOUGHT HERE, since "two rounds for one regex" deserves an
  accounting: the shipped task began as a shape check and a URL match, and the
  loop added a guard nothing tested (deleting is_archive_url left the ENTIRE
  suite green), a normalizer that matched URLs differing in their query string, a
  tab that passed every gate and then CRASHED the verb out of its own four-state
  contract, two comments the code had falsified, an empty commit body, and a
  disarmed pre-existing test. The original defect was real; none of those were it.
Task 18: minor (deferred): the confirmed-snapshot path still has no shape or
  target check — a payload whose closest.url points at a different site is
  recorded verbatim. Deliberate, scoped out. Destination: GitHub issue at plan
  close.
Task 18: minor (deferred): other pre-existing loose-prefix reason assertions
  remain in tests/test_archive.py. Destination: GitHub issue #22 (the sweep),
  which already exists — not a new entry.
Task 18: minor (deferred): archive.py.manifest.json still stale. Destination: the
  measured 10-of-25 manifest-staleness note in this ledger; Plan W replaces the
  tool that reads it.

### CORRECTION TO MY OWN REMAINING-TASK COUNT
  When asked which task I was on, I listed the remainder as 18, 19, 20, 21 plus
  Part 1's 11, 12, 13, 2e and Task 22. THAT OMITTED TASK 19b (PreToolUse deny on
  machine surfaces). I enumerated the plan's `### Task` headings afterwards
  rather than trusting the list again: the true remainder is 2e, 11, 12, 13, 19,
  19b, 20, 21, 22 — NINE tasks, not eight. Recorded because a controller's own
  task list is exactly the kind of artifact this run keeps catching people
  describing from memory instead of deriving.

Task 19: BASE = ccde1bc. Implementer dispatched (sonnet). Brief generated and
  READ before dispatch — which is how the next item was caught.
  THE EXTRACTOR OVER-CAPTURED: task-19-brief.md contains Task 19 AND ALL OF TASK
  19b. Handing that over unqualified invites an implementer to build a
  PreToolUse hook nobody asked this task for. The dispatch fences it explicitly:
  everything from the 19b heading on is a different task and not theirs.
  PRE-CHECK FOUND A HARD BLOCKER THE BRIEF DOES NOT MENTION, and it would have
  surfaced as a mid-implementation failure rather than a design input:
  inbox._validate_date (inbox.py:167-177) enforces
  `re.fullmatch(r"\d{4}-\d{2}-\d{2}")` and RAISES otherwise, and notice_date
  reaches it through _validate_optional_date at inbox.py:193. Measured in-tree,
  canary asserted:
      '2023'       -> RAISES: notice_date must be a YYYY-MM-DD calendar date
      '2023-06'    -> RAISES
      '2023-06-15' -> ok
  So THE MOMENT _notice_date_from_updated RETURNS AN HONEST "2023", FILING THAT
  FINDING RAISES. The brief's own Step 4 ("trace every consumer") names the
  activity that would have found this — after the fact. The file list grows to
  include inbox.py.
  AND THE OBVIOUS FIX IS THE WRONG ONE: _validate_date is SHARED with
  detection_date (inbox.py:194) and the `date` field, both of which must stay
  strict full dates. Loosening it would silently widen two fields the task has no
  business touching. The dispatch requires a SEPARATE partial-date validator
  scoped to notice_date, still rejecting 2023-13, 2023-06-31, 23 and 2023-6 —
  "a validator that accepts everything is not a validator".
  TWO MORE HAND-OVERS, both located rather than described:
   - the two comparison sites: _active_blocking_notices (checks.py:566-584),
     which does `reinstatement >= notice["notice_date"]` — note the `>=`, so a
     SAME-DAY reinstatement clears today and must keep doing so in the
     unambiguous case — and _effective_blocking (checks.py:586-598), whose max()
     key is `(notice_date is not None, notice_date or "", type)`.
   - inbox.py:263 embeds notice_date IN THE FINDING ID
     (`f"/{notice_class}/{notice_type}/{notice_date or 'unknown'}"`), so changing
     emitted precision CHANGES IDS for year-only notices and an entry keyed
     2023-01-01 will not dedup against a new one keyed 2023. The brief never
     names that consequence.
  ALSO TOLD IT TO VERIFY, NOT ACCEPT, the brief's claim that string ordering over
  ISO prefixes is "already consistent" for the max() key — "2023" sorts BEFORE
  "2023-01-01" and AFTER "2022-12-31", which is a defensible choice but a choice,
  and the brief states it as a law.
  Consumer list handed over (27 sites in inbox.py, 3 regions in checks.py) with
  the instruction to search a SECOND way rather than trust my grep, and to record
  the METHOD in the commit body, not just the conclusion.

Task 19: implementer DONE (commit 50538bb; 5 files, +484/-5, report included,
  progress.md correctly untouched). Suite 1646/7 (= 1624 + 22 new tests); ruff,
  mypy, form gate clean, and the implementer separately ran the 8-hook pre-commit
  set against the exact committed files.
  BOTH PRE-CHECK HAND-OVERS LANDED THE WAY THEY WERE MEANT TO:
   - The blocker was treated as a DESIGN INPUT rather than discovered as a
     failure: inbox.py gained a SEPARATE _validate_partial_date +
     _validate_optional_partial_date, wired ONLY at notice_date (inbox.py:224),
     while detection_date keeps _validate_optional_date on the next line. The
     shared strict validator was NOT loosened, which was the specific hazard.
   - The 19b fence held — no hook, no plugin config, no §10 edit.
  AND IT WENT PAST WHAT I HANDED OVER, on the part that mattered most. The
  ambiguity rule is factored into two named predicates rather than inlined:
  _dates_incomparable and _reinstatement_clears. The first documents a case I had
  NOT specified and the brief does not mention — TWO EQUAL PARTIAL STRINGS
  ("2023" vs "2023") are incomparable, because a string is its own prefix and a
  year-only reinstatement could fall before or after a year-only retraction. Two
  equal FULL dates stay comparable, so the `>=` same-day clear survives. That is
  the fail-safe boundary drawn in the right place, and drawn where I had left the
  spec silent.
  CONTROLLER-TRACED THE PREDICATE'S CASES BY HAND before dispatching the review,
  because a date comparison is exactly where a plausible-looking rule hides a
  wrong branch: 2023-06 vs 2023-07-15 CLEARS (July is unambiguously after June);
  2023-06 vs 2023-06-15 does NOT (prefix); 2023 vs 2024-01-01 CLEARS; 2022 vs
  2023 CLEARS; 2023-06-15 reinstated by a 2023-06 partial does NOT. Each is the
  answer the asymmetry demands. The review is asked to enumerate the full table
  rather than take my spot-check.
  DESTINATIONS ACTED ON, NOT MERELY NAMED — a step beyond the rule as written:
  the implementer FILED GitHub issue #23 for the max()-ordering finding it
  measured ("2023" < "2023-01-01" is True) and COMMENTED on existing #22 for a
  loose .startswith("2010-02") assertion it found in a live-network test. Noted
  as a deviation from my "name the destination" instruction in the direction of
  doing more, and it is the right direction.
  MY OWED FILING IS ALREADY DISCHARGED, verified rather than assumed: `gh issue
  list` now shows #19 (other MANAGED_FIELDS keys outside the guard), #20
  (attestation evadable via duplicate frontmatter keys) and #21 (renamed notes
  skip the per-key diagnostic) — exactly Task 17b's three concerns, which my
  ledger had recorded as "controller files at plan close". They exist; I no
  longer owe them.
Task 19: review dispatched over ccde1bc..50538bb on the most capable model. Told
  outright that the extractor over-captured, so 19b's absence is NOT unmet scope
  — a reviewer reading the brief cold would file that as a spec failure.
  Required: a FULL TRUTH TABLE over _dates_incomparable across every precision
  pairing AND BOTH ARGUMENT ORDERS, flagging any pair where the code clears but a
  human could not have known the order; proof that _validate_date did NOT widen
  for detection_date and date; rejection probes rather than acceptance probes on
  the new validator; and the reason-swap check for the recurring loose-assertion
  defect, on tests that must assert WHICH notices survive rather than that a list
  is non-empty.

Task 19: review returned — SPEC PASS and QUALITY PASS, one Medium, three Low/Info.
  Review file: task-19-review.md
  THE TRUTH TABLE CAME BACK CLEAN, and the reviewer went past enumeration to the
  reason: THE PREFIX TEST IS NOT A HEURISTIC. ISO-prefix intervals are
  NESTED-OR-DISJOINT, so `startswith` is an EXACT DECISION PROCEDURE for
  ambiguity rather than a good-enough approximation. Every precision pairing was
  run in BOTH argument orders and NO ROW CLEARS WHERE A HUMAN COULD NOT HAVE
  KNOWN THE ORDER. That is the property the task exists to guarantee, established
  rather than argued.
  THE IMPLEMENTER'S TWO DEVIATIONS FROM THE BRIEF WERE BOTH UPHELD AS
  IMPROVEMENTS: the None sentinel (so an explicit 0 month/day FAILS instead of
  silently becoming 1) and reading equal partials as ambiguous — without which
  the brief's own "or both are full dates" clause is DEAD CODE. Planner text
  improved on by the implementer, twice, with reasons.
  AND THE REPORT UNDER-CLAIMED, which is the rarer direction: four tests the
  implementer labelled "regression guards, not discriminators" each have a
  killer. All 22 have one. M12 — a mutant returning a NON-EMPTY BUT WRONG list —
  reds four of them, which is the exact probe for this plan's recurring defect
  and it comes back NEGATIVE: those assertions are exact-list, not non-emptiness.
  Row 21 needed M13 (widening _validate_date wholesale) to prove it pins the
  shared-validator hazard, AND IT IS THE ONLY TEST IN test_inbox + test_checks
  THAT CATCHES IT.
Task 19: MEDIUM F1 — THE NEW VALIDATOR LETS NON-ASCII DIGITS INTO A GOVERNED
  IDENTIFIER, and it is a regression this diff introduced. _PARTIAL_DATE uses
  `\d`, which is UNICODE-AWARE, and validation goes through date(int(...)) rather
  than fromisoformat — so the ASCII backstop the REPLACED _validate_date happened
  to have is gone. CONTROLLER REPRODUCED IN-TREE, canary asserted:
      '٢٠٢٣'       -> ACCEPTED as '٢٠٢٣'
      '２０２３'      -> ACCEPTED as '２０２３'
      '2023-٠٦'    -> ACCEPTED as '2023-٠٦'
      '2023-06-١٥' -> ACCEPTED as '2023-06-١٥'
  int() parses them and THE VALUE IS RETURNED VERBATIM, so it reaches finding_id
  (inbox.py:263) and ack fingerprints; load() re-validates through the same path,
  so a hand-written inbox line that PREVIOUSLY RAISED InboxError NOW PARSES.
  Unreachable from Crossref today — but "the current caller cannot produce it" is
  not the contract a validator on a durable governed identifier advertises. One
  token to fix (re.ASCII or [0-9]).
  THE SHAPE IS WORTH KEEPING SEPARATELY FROM THE INSTANCE: a safety property that
  was never stated, only INHERITED as a side effect of an implementation detail,
  vanished when that detail was legitimately replaced. Nothing was done wrong to
  the property, because nobody knew it was there. That is why the dispatch also
  asks for a search for OTHER `\d` patterns whose only ASCII backstop was a
  fromisoformat call no longer being made.
Task 19: fix round 1/5 dispatched — F1 plus two hygiene items: the
  _dates_incomparable docstring spends its length restating what startswith does
  while omitting the nested-or-disjoint property that actually justifies it, and
  provenance duplicated from the commit body into a comment and a test docstring.
Task 19: minor (deferred): mutation-baseline.txt:32-34 and both .manifest.json
  sidecars are stale after this diff. Task 24 Step 4 establishes the
  regenerate-or-record convention, Task 19's brief has no such step, and the lane
  is advisory. Destination: the measured manifest-staleness note in this ledger
  (10 of 25) plus Plan W's Task 24.
Task 19: info (no action): tests/test_inbox.py:204's `match="notice_date"` matches
  the FIELD NAME rather than the message, so it survives M10 — judged not a real
  gap by the reviewer, and I agree: the field name is what that test is about.

Task 19: fix round 1 landed — 7b28dd8. 5 files, +93/-17; suite 1650/7 (+4).
Task 19: ROUND-1 RE-REVIEW DONE BY THE CONTROLLER — the round was one regex flag
  and two docstrings, and its single substantive claim is settleable by one
  mutant, so a dispatch would have added latency and no evidence.
   - THE FIX WORKS, probed in-tree with the canary asserted: '٢٠٢٣', '２０２３',
     '2023-٠٦' and '2023-06-١٥' are ALL REJECTED now, while '2023', '2023-06' and
     '2023-06-15' still pass. Same four values that were accepted verbatim before.
   - THE PINS DISCRIMINATE AND ARE EXACTLY SCOPED: reverting `re.ASCII` in an
     archive scratch tree reds EXACTLY the four new
     test_notice_date_rejects_non_ascii_digits parameters and NOTHING ELSE —
     4 failed / 273 passed. A revert that had reddened extra tests would have
     meant the flag was doing more than the finding described.
   - The implementer searched a SECOND WAY for the same shape (grep for int()
     over regex groups, rather than re-grepping `\d`) and found no other
     validator with it — which is the right method, since re-running the search
     that found the first instance can only find the first instance.
   - The docstring now states the LOAD-BEARING FACT — ISO-precision strings
     denote nested-or-disjoint intervals, so the prefix test is EXACT rather than
     a heuristic — instead of narrating what startswith does. That sentence is
     the difference between a reader trusting the rule and re-deriving it.
  Gates re-run by me in the real tree: 1650 passed / 7 skipped, form gate exit 0.
Task 19: complete (commits ccde1bc..7b28dd8 — 50538bb, 7b28dd8 — review clean
  after 1 fix round, 2 minors deferred). Ticked below: 5 boxes; 77 checked /
  35 unchecked.
  THE TASK'S OWN RESULT, stated plainly because it is the point: a year-only
  Crossref retraction can no longer be cleared by a mid-year reinstatement, and
  where precision leaves the order genuinely unknown the alert now STANDS. The
  cost of that choice is an acknowledgement; the cost of the old behaviour was a
  silently un-retracted citation.
Task 19: minor (deferred): mutation-baseline.txt:32-34 and both .manifest.json
  sidecars stale after this diff. Destination: Plan W Task 24 Step 4, which
  establishes the regenerate-or-record convention; the lane is advisory today.
Task 19: minor (deferred, filed by the implementer): the max() newest-wins key
  sorts a year-only date BEFORE a full date in the same year — measured, not
  reasoned ("2023" < "2023-01-01" is True), at TWO call sites rather than the one
  the brief assumed. Not a safety hole, because clearing provably runs earlier in
  the pipeline (checks.py:889). Destination: GitHub issue #23, verified OPEN.
