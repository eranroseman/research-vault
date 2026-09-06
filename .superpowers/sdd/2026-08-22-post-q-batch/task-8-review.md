# Task 8 review - a2a5aad..c0d0854

Disposition: historical (2026-09-06)

## Spec Compliance

**Verdict: issues** (correcting the spec lens's "compliant" — reasoning below).

Step 1 landed in full. All eight adoptions ship, in the six files the brief names, and every
fragment the audit decided survives verbatim. I re-read the record document at
`docs/2026-08-22-skills-layer-audit.md` (it does resolve on-branch; the report's
`research/validation-slice/` path is the destination path, not the current one) and checked each
quoted phrase against `:381`, `:395`, `:401` and `:405`:

- "route the user's intent without silently broadening it" — `skills/project-flow/SKILL.md:76`,
  verbatim, inside the `## Routing` slice.
- The compilation-value line — `skills/synthesis-conventions/SKILL.md:18`, with "— the only
  threshold" deliberately left unreworded.
- "SKIPPED applied to reading" — `skills/import-source/SKILL.md:113` and
  `skills/factcheck-draft/SKILL.md:42`, verbatim in both.
- "validates declarations, not their truth" — `skills/factcheck-draft/SKILL.md:79`. The audit's
  "it validates" became "this pass validates", which supplies the pronoun's antecedent and leaves
  the brief's own quoted fragment intact.
- "role separation is not independent error processes" — `skills/factcheck-draft/SKILL.md:19`,
  verbatim, carrying `:395`'s deterministic-only-closure half as well. That extra clause is
  audit-mandated rather than scope creep: `:395` rules that the why-one-pass sentence "now says so
  in the skill instead of implying it", so shipping only the anti-panel half would have left the
  audit's claim about the skill untrue.
- Both `:401` seed rows — `skills/publish/SKILL.md:134-135`, as left-column cells, sentence-cased
  from the audit's lowercase quotation with the wording intact.
- Fail closed on an ambiguous vault — `skills/setup-vault/SKILL.md:15`.

**Adoption 8 (the controller's concern 1) resolves in the implementer's favour.** The factual
premise holds: `skills/publish/SKILL.md:61` states "Arming writes the state flag the Stop hook
checks; while it is absent the hook is inert", and `arm-publish` is not run until `:57`, so the
gate genuinely is not armed when the skill starts. The audit's literal wording ("publish announces
at start that the gate is armed") would have been a false mechanical claim at HEAD, and the
flow-property phrasing is the right call under tree-governs-facts. It is also audit-sourced rather
than plan-sourced: `:405` sits in §7's "Batch enrichments (existing items, no new scope)"
subsection, above the deferred 01-11 polish list, and is the same sentence that authorises the
table's seed rows. No finding, nothing plan-mandated, nothing for the author to rule on.

Step 2 is a real verification, not a claimed no-op. The six §6 deferred items the report names
match the audit's `:385`-`:390` bullets exactly, and none appears in the diff; the diff stat is 95
insertions / 1 deletion, that single deletion being factcheck-draft's budget sentence re-added
with the why-one-pass clause. Frontmatter appears only as context in every hunk.

Step 3's commit is exact: one commit, message `feat: ecosystem-steal prose adoptions (audit §6
adopted set)` verbatim from the brief, `skills/` and `tests/` only.

**The spec issue is Step 3's "Pins", under-met for `factcheck-draft`:**

- `skills/factcheck-draft/SKILL.md:19`, `:42`, `:79` — three of the eight adoptions ship with no
  pin, justified by a claim about the tree that does not hold: `tests/test_finding_cli.py:409`
  (`test_factcheck_draft_skill_names_its_bounds_and_never_blocks`) already reads that SKILL.md and
  asserts against its text, so no new file was needed. Detail under Important issue 2.

The spec lens rated this Minor on a tie-break it explicitly invited the controller to overrule:
"no pin file exists for these two skills to update". That premise is false for `factcheck-draft`
and true only for `synthesis-conventions`. With the excuse gone for the file carrying three of the
eight adoptions — including the two doctrine sentences the audit called "our four-state posture
said better than we say it" — the requirement is partially unmet rather than scoped out, so the
verdict moves to issues. The `synthesis-conventions` half of the scope call stands: nothing in
`tests/` reads that file, and creating a new pin file is defensibly the polish pass's call.

### Cannot verify from diff

- **The form gate.** `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` reporting
  8/8 with no file modified. This review is read-only and mdformat writes, so the hook run was not
  repeated here. Re-run it from the worktree root and confirm the run leaves the tree clean — the
  report says mdformat reflowed the new publish table on its first run, and a reflow-dirty tree
  would not show up in a read-only review.

Everything else the lenses flagged as unverifiable was resolved during this synthesis and needs no
controller action:

- **Suite.** Re-run here read-only (`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests -q
  -p no:cacheprovider`): **1570 passed, 7 skipped in 90.14s**, exit 0, no warnings in the output.
  Matches the report exactly.
- **Working tree.** `git status --porcelain` is empty at `c0d0854`, both before and after that run.
- **Commit body.** `git log -1 --format=%B c0d0854` carries the full adoption-to-source map, the
  adoption-8 deviation ruling, and the item-14 verification. The deviation reasoning is already in
  the commit body where it belongs — which is what makes the duplicate copy in the test docstring
  removable rather than load-bearing.
- **Verbatim fidelity to the audit.** Checked directly against
  `docs/2026-08-22-skills-layer-audit.md`, as listed above.

## Strengths

- **The adoptions are written into this corpus's vocabulary, not pasted from the survey.** The
  routing guard's examples are this repo's own verbs; the setup-vault line is the narrower,
  actionable rule that the existing "keep the person in control of destination" sentence never
  supplied.
- **The partial-read rule was deliberately kept clear of the deferred machine intake gate.** Both
  paragraphs say out loud that they carry no filing mechanics —
  `skills/factcheck-draft/SKILL.md:42` ("This governs what you report, not which verb you file")
  and `skills/import-source/SKILL.md:113` ("no verb watches your reading, which is precisely why
  the label has to come from you"). A reporting rule that could easily have implied a CLI contract
  that does not exist instead disclaims one. That is a real boundary held, not merely asserted.
- **The rationalization table refuses to become a second source of truth.** Six of its seven rows
  restate a rule that already exists elsewhere in the file — ack scoping at `:85`, "present
  exactly these three" at `:48`, the typed-`discard` rule at `:75`, re-publication at `:112`, the
  bypass at `:120`. For a genre whose whole risk is drifting into a second, wronger statement of
  the mechanics, that is the right discipline; the heading and header row also match
  `evidence-conventions`' existing table byte-for-byte, so it is the house form rather than the
  imported one.
- **Three of the five new pins slice to a section before asserting**
  (`tests/test_project_flow_skill.py:135`, `tests/test_skill_files.py:46`,
  `tests/test_publish.py:801`), so they pin placement and not merely presence. A guard that
  survives a reorganisation into the wrong section fails — the failure mode worth catching in a
  prose pin.
- **The +5 test delta is honestly accounted for.** Exactly five new test functions, and every
  asserted string is prose this same commit introduced; no new pin passes vacuously against
  pre-existing text.
- **The deviation was surfaced rather than smoothed over.** Adoption 8 shipped as a disclosed
  concern with its factual premise stated, and the premise checks out against the tree.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

**1. All five new test docstrings lead with audit provenance, and one argues its own correctness —
`tests/test_publish.py:795` (also `:810`, `tests/test_project_flow_skill.py:131`,
`tests/test_import_source_skill.py:41`, `tests/test_skill_files.py:41`). Status: CONFIRMED.**

*What is wrong.* Every docstring this task added opens with where the line came from: "Adopted per
audit §7's batch enrichments" (`test_publish.py:795`), "Audit §6 adopted a rationalization table
here, seeded by §7 with two rows ported from `finishing-a-development-branch`" (`:810`), "The
routing guard adopted from the ecosystem survey (audit §6's adopted set)"
(`test_project_flow_skill.py:131`), "The partial-read honesty rule (audit §6's adopted set)"
(`test_import_source_skill.py:41`), "Adopted from the ecosystem survey (audit §6's adopted set)"
(`test_skill_files.py:41`). The adoption-8 docstring goes further and defends the implementer's
phrasing ruling inside the pin: "…so it is pinned as a property of the flow."

*Why it matters.* The comment-hygiene discipline recorded at
`.superpowers/sdd/2026-08-22-post-q-batch/progress.md:411-429` (author, 2026-08-23, TASK 24b) is
binding on this branch's new test code from Task 5 onward: "write comments that state a
CONSTRAINT; put provenance, dates, ruling citations and correctness arguments in the COMMIT BODY,
not in the code." Task 8 is post-Task-5, `tests/` is inside 24b's file scope, and the stated point
of the forward instruction is to leave 24b less to undo. The controller pre-flagged the
`test_publish.py:795` instance to this review for exactly this reason. The citations also point at
audit section and line numbers that nothing checks, so they rot the moment the audit is
renumbered — and the commit body already carries every one of them, correctly.

*How to fix.* Cut the provenance openers from all five docstrings and the "so it is pinned as a
property of the flow" tail. Keep the sentences that state a constraint the asserts cannot show —
the false-state hazard at `test_publish.py:798` ("The line must not claim the gate is already
armed — `arm-publish` arms it later"), the section-placement requirement in
`test_project_flow_skill.py`, the no-verb-watches-your-reading point in
`test_import_source_skill.py`. Better still for the first of those, convert it into the assert it
describes (Minor issue 8).

**2. Three factcheck-draft adoptions ship unpinned on a scope excuse the tree does not support —
`skills/factcheck-draft/SKILL.md:42` (also `:19` and `:79`). Status: CONFIRMED.**

*What is wrong.* The report's Pins section says `synthesis-conventions` and `factcheck-draft` have
"**no per-skill prose pin file** in this repo today — `test_factcheck.py` pins CLI behaviour, and
nothing reads `skills/synthesis-conventions/SKILL.md`", and the commit body repeats it ("neither
has a per-skill prose pin file in this repo, and creating one is the polish pass's call"). For
`factcheck-draft` the operative half of that is wrong: `tests/test_finding_cli.py:17` binds
`FACTCHECK_DRAFT_SKILL` and `tests/test_finding_cli.py:409`
(`test_factcheck_draft_skill_names_its_bounds_and_never_blocks`) reads that SKILL.md and asserts a
token tuple against its text. No new file was needed — three appended tokens would have done it.
The file the report names, `test_factcheck.py`, is not where that pin lives.

*Why it matters.* Every token in the existing tuple (`tests/test_finding_cli.py:411-421`) also
occurs elsewhere in the skill — in the `factcheck` command block, the `--cap` sentence, the
four-state table, the `finding` examples — so all three adopted paragraphs can be reworded or
deleted with the suite fully green. No test anywhere in `tests/` asserts any of the three
sentences; only the import-source twin is pinned, at `tests/test_import_source_skill.py:46`. The
unpinned set includes the two doctrine sentences the audit singled out ("our four-state posture
said better than we say it") and the `:395`-mandated deterministic-only closure statement, and §7's
deferred polish item 08 is scheduled to rewrite this very file — so the rot vector is concrete and
near-term.

*How to fix.* Append the three distinctive tokens — "SKIPPED applied to reading", "validates
declarations, not their truth", "role separation is not independent error processes" — to the tuple
at `tests/test_finding_cli.py:411`, and correct the "no per-skill prose pin file" sentence in the
report. The commit body's copy of the claim is immutable; the report's is not.

### Minor (Nice to Have)

**3. `skills/synthesis-conventions/SKILL.md:18` — the compilation-value line ships with no pin at
all. Status: NOT-VERIFIED-MINOR (underlying fact spot-checked: nothing under `tests/` reads
`skills/synthesis-conventions/SKILL.md`).** Unlike issue 2, pinning this one does require a new
file, and the plan's stated discipline is an update rule ("whole-file test pins update in the SAME
commit as the prose they pin"), not a create rule — so the scope call is defensible. But §7's
polish item 06 is queued to rewrite this skill's threshold prose, and nothing would fail if the
adopted paragraph vanished. Roughly six lines in a new `tests/test_synthesis_conventions_skill.py`,
following the `tests/test_project_flow_skill.py` pattern, closes it. The controller may reasonably
fold this into the issue-2 fix.

**4. `skills/publish/SKILL.md:138` — the refusal row's list of exits omits the resolve/acknowledge
path. Status: CONTESTED (downgraded from Important; see Refuted During Verification).** The row
says the armed gate "clears when `mark-published` succeeds, or when the person asks to disarm —
never by failing", while `:61` of the same file says the hook holds "until the finding is resolved,
acknowledged, or the person abandons the attempt", and `hooks/stop_publish_gate.py:535` clears the
flag with no verb at all once the surface comes back green. Nothing in the row is false, and the
ack path normally routes back through `mark-published` succeeding
(`research_vault/publish.py:354-362`), so this is an incomplete enumeration rather than a
contradiction. Adding the third path — "when the blocker is fixed or acknowledged and the surface
comes back green" — makes the row agree with `:11` and `:61` at no cost.

**5. `skills/publish/SKILL.md:138` (also `:137` and `:139`) — three right-hand cells repeat their
source paragraph near-verbatim rather than summarising it. Status: NOT-VERIFIED-MINOR.** Row `:138`
repeats `:61`'s bolded "A refusal leaves the gate armed"; row `:139` repeats fifteen consecutive
words of `:112` ("would record a correction as a first publication in tags and events that are
never deleted"); row `:137` repeats `:75`'s "never infer the … word from context and never type it
on their behalf". Two copies of one rule with nothing tying them means an edit to the canonical
paragraph leaves the table asserting the old rule, and the new pin only checks the two seed rows,
so that drift passes green. The report says one row (the bypass) was reworded during drafting for
precisely this reason; the same treatment — consequence plus a pointer to the section that owns the
rule — applied to these three finishes the job. Distinct from issue 4, which is about the row's
content being incomplete rather than duplicated.

**6. `skills/publish/SKILL.md:11` — "holds the session until the attempt lands, is acknowledged, or
is disarmed" omits the hook's safety bound. Status: NOT-VERIFIED-MINOR (mechanism verified:
`hooks/stop_publish_gate.py:16` sets `MAX_ACTIVE_BLOCKS = 8`, and `:506-507` releases with
`BOUND_MESSAGE` after the eighth block, leaving the flag set).** The stated release conditions are
therefore not exhaustive: after the eighth block the session ends with the gate still armed. It
mirrors the pre-existing claim at `:61`, so this is a consistency issue rather than a regression,
but it is a new mechanical claim written one paragraph after the implementer invoked
tree-governs-facts to avoid this exact class. Either name the bound or drop the mechanism clause;
`test_publish_skill_announces_the_armed_gate_before_the_first_command` asserts only "Say this
before the first command", "runs through an armed gate" and the flag-setting clause, so tightening
it breaks no test.

**7. `skills/publish/SKILL.md:11` — "until the attempt lands, is acknowledged, or is disarmed"
grammatically attaches the acknowledgment to the attempt. Status: NOT-VERIFIED-MINOR.** In this
corpus an `ack` is granted to a blocking finding, never to a publish attempt
(`skills/publish/SKILL.md:79-85`; `:61` says "until the finding is resolved, acknowledged, or the
person abandons the attempt"). This is the first thing the person hears, and precision about who
acknowledges what is what the whole ack surface rests on. "…until the attempt lands, its blocking
finding is acknowledged, or the gate is disarmed" keeps the subject on the finding. Distinct from
issue 6, which is about the release conditions being incomplete rather than misattributed.

**8. `tests/test_publish.py:798` — the docstring declares an invariant no assert enforces. Status:
NOT-VERIFIED-MINOR.** "The line must not claim the gate is already armed — `arm-publish` arms it
later" is the entire reason for the deviation from the audit's decided wording, and all three
asserts are positive presence checks. A later editor who "restores the literal wording" by adding
"the gate is armed" to the intro keeps the test green, so the pin cannot defend the constraint it
says it exists to defend. Add `assert "the gate is armed" not in intro` and let the assert carry
the constraint. This interacts with issue 1: converting the sentence into an assert satisfies both.

**9. `tests/test_publish.py:815` — the rationalization pin asserts against the whole file instead
of the section. Status: NOT-VERIFIED-MINOR.** Its three siblings slice first
(`tests/test_publish.py:801`, `tests/test_project_flow_skill.py:135`,
`tests/test_skill_files.py:46`); this one proves only that the heading exists somewhere and the
strings exist somewhere. A row moved out of the table, or an emptied section whose sentences
survive as body prose, still passes — and these are the two rows the audit explicitly mandated, so
placement is the thing worth pinning. `table = text[text.index("## Rationalizations, answered") :]`
and then the four content asserts against the slice.

## Refuted During Verification

**Quality lens, Important at `skills/publish/SKILL.md:138` — "the row contradicts `:11`, `:61` and
the hook, and steers an agent toward disarm or the bypass after a refusal." Refuted as stated;
residual kept at Minor.** The verification held on the mechanics and it re-checks out: the row
asserts nothing false ("never by failing" is true, and both listed exits are true), and
`research_vault/publish.py:354-362` — with its comment that "a green decision here *is* spec
§6's 'green, or every blocking entry carries a standing ack'" — means the ack path routes back
through `mark-published` succeeding rather than around it. The one path genuinely not named is
`hooks/stop_publish_gate.py:535`'s verb-less cleanup on the next Stop, which is automatic
background behaviour rather than a choosable exit. A subset is not the contradiction the finding
called it, and the harm story is further weakened by the ack rule being the table's own first row.
The residual — an enumeration narrower than `:61`'s — survives as Minor issue 4.

**Fidelity lens, Important at `tests/test_publish.py:795` — its REFUTE of the docstring-hygiene
finding is itself overturned; the finding stands.** The fidelity verifier concluded that "no
comment-hygiene doctrine ruled 2026-08-23 exists", reading only
`docs/superpowers/plans/2026-08-20-plan-q-quality-lane.md:51` and citing
`tests/test_skill_contracts.py:459-472` (task 3, `d44452e`) as on-branch precedent for
provenance-bearing docstrings. Both legs fail against the primary source. The doctrine is recorded
at `.superpowers/sdd/2026-08-22-post-q-batch/progress.md:411-429`, dated 2026-08-23, and its
forward-consequence paragraph binds dispatches "from Task 5 onward"; the same block explicitly
grandfathers the counter-example ("NOT retro-editing Tasks 1-4's comments — 24b owns that
judgment") and even names Task 3's C-2 and date citations as "the sweepable part". The quality
lens's STANDS is the correct verification, and the progress.md text was re-read here to confirm it.
The finding is carried as CONFIRMED Important issue 1.

**Nothing else was dropped.** The spec lens's Minor at `tests/test_publish.py:794` and the fidelity
lens's Important at `tests/test_publish.py:795` describe the same defect as the quality lens's
finding and were merged into issue 1 at the higher severity. The spec lens's Minor covering four
unpinned adopted lines was split: its `factcheck-draft` half merged into issue 2 at Important, its
`synthesis-conventions` half kept as Minor issue 3 — the split both the spec and fidelity lenses
independently converged on.

## Assessment

**Task quality: Needs fixes.**

The prose work is the strong part — eight faithful adoptions, a genuinely reasoned deviation on
adoption 8, a real item-14 verification, and a rationalization table that stays subordinate to the
rules it restates. What needs fixing is small and mechanical: three of the eight adopted lines have
no pin although the pin file for that skill already exists and would take three appended tokens,
and all five new docstrings carry the provenance and correctness prose this branch's dispatches
have kept out of code since Task 5.
