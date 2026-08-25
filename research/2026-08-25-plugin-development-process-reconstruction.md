# How this plugin was designed and built — process reconstruction from artifacts

Methods material, 2026-08-25. Every claim below is derived from repo artifacts — git history,
GitHub issues, tracked files — by an artifact walk (no memory-derived process facts; commits,
issues, and file:line cited throughout). Two consumers: the methods section if harness-as-paper
materializes, and the process template when workloads 2/3 (analysis/reports, PKM, long-form) are
built the same way.

## Scale

- **658 commits over 10 calendar days** (2026-08-16 → 2026-08-25; two zero-commit days), peaking
  at 129/day. Conventional-type distribution: **253 docs, 87 fix, 60 plan, 45 feat**, 23 chore,
  15 test, 15 spec, 15 research, 12 refactor, 11 ruling, 7 adr — documentation commits outnumber
  feature commits five to one, which is the docs-first culture measured, not asserted.
- 25 issues (#1–#15 the wayfinder foundation map and its tickets, all closed 08-16 era; #16–#25
  triage- and batch-born, open). 19 plan documents ever, 4 extant, 14 deleted after absorption
  (553ae6f). 62 research files. 4 accepted ADRs. Spec: 211 lines, ~7.5k words. Test suite: 24
  gated live tests at slice Phase 0 → 1,454 (08-22) → ~1,747 collected at HEAD.

## The arc, in nine phases

1. **Wayfinder mapping + prior-art sweep (08-16).** Issue #1 (`wayfinder:map`) with a
   decisions-so-far ledger; #2–#6 research tickets resolved by fan-out (fd64536); raw exploration
   banked under research/ including manually recovered + OCR'd primaries (3719086, 96742a2).
2. **Decision tickets → spec → adversarial verification (08-16).** #7–#14 grilling tickets became
   spec sections that cite them inline ("## 3. Vault structure ([#7])"); the spec shipped only
   after "two adversarial verification passes (44 findings resolved) and a seven-domain rethink
   audit (85 findings; three trust-boundary defects fixed)" — its own Status line (e04db28,
   de4ec5f, approved 5211ebf).
3. **Build plans A/B/C (08-16 → 08-21).** Bridge core ("12 findings fixed, live-probed"),
   verification engine ("30 verification findings fixed"), scaffold + enforcement ("23 findings
   fixed") — every plan carries its own counted adversarial pass, and execution is punctuated by
   `ruling:` commits and build-time spec corrections (bd71121).
4. **ADRs + terminology wave (08-20 → 08-21).** ADR 0001 iterated across seven commits before
   0002/0003 joined it (65697ed); the eight-tier terminology precedence stack ruled and executed
   as Plan T; CONTEXT.md created by a plan task, not ad hoc.
5. **Quality lane (08-20 → 08-23).** Plan Q: pinned tools, ruff+mypy, mdformat, the mutation
   gate script, advisory CI. docs/testing.md born here.
6. **Skills layer, Plan D (08-21 → 08-22).** Eight skills authored with "all 19 adversarial
   findings" folded before landing; nine skills at HEAD.
7. **Validation slice opens: audits + pre-registration (08-22 → 08-23).** Plan S authored with
   load-bearing falsified-when; Phases 0–1 same day (live export, 166-row seed ledger, question
   selected); the audit corpus lands as files (no-fabrication: "39 candidate findings, each
   adversarially verified by a fresh agent instructed to refute — 21 confirmed, 18 refuted");
   decision rules pre-registered before their evidence window opens; trust-core remediation
   absorbed into one combined pre-slice plan so a single merge unblocks Phases 2–6.
8. **Pre-slice batch (08-23 → 08-25; first batch commit 002cb25 is author-dated 08-23).** 26
   tasks, 58KB plan, controller/implementer/reviewer topology, per-task review + fix rounds —
   not an exception but the norm: **10 of 26 task-closes record at least one fix round** (six
   took one, two took two, two took three; peer-counted from the ledger). One boundary SHA-walk
   at the Part 1/2 boundary (ca0281d; the pre-merge walk did not run and the post-merge walk is
   owed), an independent plan review, a concern-disposition sweep, ADR 0004 accepted, issues
   #16–#25 filed. What was hard, from the execution seat: plan text drifting from the tree
   (stale line numbers, a brief naming a nonexistent test file, a two-day-stale brief, a
   falsified premise that was true for an unchecked field), claims outrunning evidence in both
   directions, and three seats coordinating without ever seeing the same artifact. The
   highest-leverage single activity: the controller pre-check — reading the code a brief points
   at before dispatch and handing over facts the brief cannot know (see the execution-seat
   ledger below). Plan W split out so the batch header's single-dispatch claim "becomes true
   again" (f6b7788).
9. **Present (08-25).** Batch complete 112/112, acceptance sweep clean, merged; method
   retrospective committed and visibly amended; slice Phases 2–6 unblocked, not yet run; Plan W
   pending.

## Method-inventions ledger

Each mechanism with its first-appearance artifact — the reusable part.

1. **Wayfinder decision-ticket mapping** — the map issue's one-line-per-closed-ticket ledger;
   spec sections cite their tickets (issue #1; spec §3–§9).
2. **Spec-as-amendable-contract** — "amendable in place with dated notes… the goal state is a
   spec fully absorbed into those artifacts"; entries name their nature (decided / corrected /
   deferred / measured — never "ruled"); absorption pass pre-registered with triggers (spec:3,
   :200).
3. **Adversarial verification with counted findings** — every major artifact ships with its
   pass's numbers in the commit or Status line (44+85 for the spec; 12/30/23/19 for plans A–D).
4. **The ADR bar** — "only ADRs carry constitutional weight (the domain-modeling three-test bar
   decides)"; enforced negatively too: three proposed ADRs scrapped, one landed "as sentences
   where they are read, not as ADRs" (5ad05a0, d7fa91b).
5. **Pre-registered decision rules + instrument freeze** — rules registered before evidence
   exists, registry closes when the window opens, "a rule recommends; it never acts"
   (slice-decision-rules.md); instruments merge before the slice runs (plan-s:8).
6. **Planted-error drills + falsified-when clauses** — the gate's own failure modes seeded
   deliberately (spec:149), and the foundation names what falsifies it, including "the author
   routes around the vault" (spec:151).
7. **Audits as read-only artifacts** — finder lanes + fresh refuting verifiers, results committed
   as files with confirmed/refuted counts, "report only — nothing applied"
   (research/validation-slice/).
8. **Research-note verdict/verification headers** — every evaluation note opens with its
   disposition so nobody re-runs it from scratch; verdicts name their instrument
   (product-landscape/README.md).
9. **Vendored-fork provenance** — pinned commit, license, per-file provenance headers,
   "corrections read beside frozen files, never edits to them," formatter exclusion; the one
   violation was caught and filed (#24) rather than absorbed (skills/find-sources/SKILL.md:11).
10. **Measurement-gap honesty in tooling** — mutation-exclusions.txt is "a record of a
    measurement gap" expected to shrink, not a suppression list; tool defects documented and
    queued upstream; replacement (mutmut) adopted only on a pre-registered pilot's data.
11. **Governed vocabulary with parity tests** — the reason-code registry enumerated in
    terminology.md with a test asserting doc/code parity (b209fbc).
12. **Four-state truth constitutionalized** — in code on day one, ADR 0002 four days later ("an
    outage is never an accusation; only a genuine pass mints a verification record").
13. **Terminology cost model** — rename churn priced at zero; eight-tier anchor-source
    precedence; "precedent is information, never constraint" (docs/terminology.md).
14. **Rulings as commits** — 11 `ruling:` + 60 `plan:` commits record in-flight decisions where
    the next reader looks: the history itself.
15. **Enforcement in-tree, lane-separated** — PreToolUse deny, PostToolUse lint (fail-open), Stop
    publish gate (armed, bounded); the dev-lane pre-commit explicitly "not to be conflated" with
    the vault's trust-gate pre-commit.
16. **Method retrospectives as artifacts** — "what the *method* produced, not what the tasks
    did," amended visibly when late instances arrived (2026-08-25 retrospective).

### From the execution seat (peer review by the batch implementer session, 2026-08-25)

Ten inventions the controller-side ledger missed, counted from the implementer's own record:

17. **Pre-check hand-over, with its inverse discipline** — the controller reads the code a brief
    points at before dispatch and hands over facts the brief cannot know (Task 17b's
    version-bump time bomb; Task 20's None-idiom trap; Task 11 shrunk to proving reachability;
    Task 2e's wikilink-escaping dry-run) — AND the implementer re-verifies rather than inherits:
    "a pre-check that becomes a fact the implementer inherits unexamined is just a longer game
    of telephone."
18. **Brief regeneration immediately before dispatch** — born from a two-day-stale-brief error;
    existence is not currency.
19. **Scratch-probe canary discipline** — `git archive | tar -x`, never `cp -r` (a worktree's
    `.git` pointer means a copy's git commands mutate the real index — happened); `PYTHONPATH=.`
    plus an asserted import path (a probe silently measured the parent repo — happened). In
    docs/testing.md.
20. **Discrimination proof as the unit of review evidence** — not "the test passes" but "revert
    the line, show it red," per test; sharper form: make the targeted path emit a
    different-but-plausible outcome and confirm the test still fails.
21. **The four-condition delegation rule** — same axis, decisive measurement, reversible,
    immediately visible; all four or ask.
22. **Destination-per-concern at write time** — an honest decline is a disposition; silence is
    not.
23. **Correct-forward over amend for reviewed commits** — including commit messages that made
    false claims (a3db464, 2393658 precedents).
24. **The seat holding the consent context performs the consented act** — Task 13's live-vault
    write stayed with the controller because a delegate would re-derive the safety context or
    act without it.
25. **Enumerate, don't count** — "four skips remain" leaves acceptance open; naming which two
    are a gate and which two a decision makes the finish line checkable in advance.
26. **Reproduce-don't-read for acceptance sweeps** — with the fence that "cannot reproduce
    because the scenario is unbuildable" is a different finding from "reproduced and the defect
    is gone."

## Plan lineage

A (bridge core) → B (verification) → C (scaffold/enforcement) → T (terminology) → Q (quality
lane) → R/L/rename (remediation, layout) → D (skills) → S (validation slice, extant) → post-Q
pre-slice batch (absorbed Plan V; complete, merged) → W (quality tail, pending). Fourteen dead
plans deleted after absorption — the plan corpus itself follows the absorb-outward model.

## What the artifacts cannot show (transcript-side, controller session 2026-08-25)

Five observations from inside the process that no artifact walk reaches — a different instrument,
so recorded separately from the cited sections above.

1. **The inventions share an economics the ledger doesn't name: they conserve the author's
   decision budget.** Pre-registration decides once, early, when deciding is cheap; the ADR bar
   makes constitutional decisions rare; verdict headers prevent re-deciding; correction-vs-
   decision stops mistakes from consuming decisions; the delegation conditions stop settled
   questions from being re-asked. The method scales agents freely — the binding resource is the
   single human every "word" passes through. Measured (transcript grep by message timestamp,
   short-form approval turns only — "word"/"yes"/"approved"/"okay"; a floor, since prose rulings
   and dialog picks don't match the pattern): 163 across the run, ~23 per active day, peaking at
   36 on 08-20. For workloads 2/3, that is the constraint to design around explicitly.
   Population caveat from the execution seat: during the batch, most decisions consumed the
   ORCHESTRATOR's relay, not the author's word — the author gated only consent and scope. The
   163 may measure a different population than "decisions the method consumed"; a
   scope-of-instrument question, stated rather than resolved.
2. **Catch latency vs catch quality — a two-seat disagreement, recorded unresolved.**
   Controller-seat observation: spec-era errors were caught by scheduled adversarial passes days
   later; by batch's end some were caught in the message that made them — catches moved toward
   point-of-writing. Execution-seat contest: the batch's final task still took three fix rounds
   and instrument-scope errors span the whole run including its last day; what improved was the
   INSTRUMENTS (discrimination proofs, canaries, enumeration, reproduce-don't-read), so "catch
   quality improved; catch latency is not visible from this seat." The falling-findings
   prediction carries the execution seat's counter-reason too: later tasks had more machinery
   available to violate.
3. **The method has n=1 on both axes** — one author, one model family, co-evolved with its own
   product. The slice validates the product; nothing tests the method's transferability.
   Workload 2's build is the natural replication run: template applied to a different domain,
   divergences recorded — the paper's external-validity evidence from already-scheduled work.
4. **The 5:1 docs:feat ratio's failure mode is doc drift**, the run's dominant drift class
   (spec-vs-code four-state episodes, comment-truth findings, thrice-revised rules). The late-run
   answers — parity tests, comments-state-only-what-code-cannot, absorb-outward, the four-state
   dedup candidate — converge on an unstated target worth naming: every doc is eventually either
   a contract with a parity test, a register with triggers, or deletable. The absorption pass can
   steer toward that endpoint instead of discovering it.
5. **The transcripts are the unpreserved lab notebook.** Records-tell-the-truth stops at the
   repo boundary: every ruling's reasoning lives in session transcripts — unversioned, uncited,
   decaying. Product claims cite file:line; the paper's process claims will need transcript
   citations, and no fixity or archive discipline exists for them. If harness-as-paper is live,
   transcript preservation is a decision with a clock on it (export key sessions into
   `research/raw/` or `sources/`; small cost, shrinking window). Partial counter-example that
   strengthens the point: the batch's SDD ledger (progress.md, committed at 95a81b3) IS a
   preserved partial transcript — rulings with derivations, errors included — and served as the
   recovery map across a context compaction. The one place preservation was done, it worked;
   it exists because a skill happened to prescribe it, not because preservation was decided.

## What repeats for the next workload

The arc compresses to a template: **map the fog as decision tickets → grill each into a spec
section that cites its ticket → verify adversarially with counted findings → constitutionalize
only what passes the ADR bar → build in planned batches with per-task review and rulings in
commits → pre-register the validation before its evidence exists → run the slice against
planted failures with a falsified-when you mean.** The inventions ledger is the checklist;
the scale numbers are the honest cost.
