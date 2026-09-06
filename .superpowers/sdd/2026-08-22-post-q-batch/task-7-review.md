# Task 7 review - 8bc6294..eb54ab6

Disposition: historical (2026-09-06)

## Spec Compliance

**Verdict: compliant** — corrected from the spec lens's "issues".

The spec lens returned "issues" on the strength of one Important finding
(`skills/find-sources/SKILL.md:74`, a sixth surviving spelling of the
never-hand-write refrain). That finding's load-bearing premise — that the audit's
"five spellings across five skills" census is falsified by the tree, so the tree
overrides the enumeration — is disproved by git. `git show 82b23a9:skills/find-sources/SKILL.md`
(82b23a9 is the commit that added `docs/2026-08-22-skills-layer-audit.md`)
already contained both clauses, at :54 and :71, and the audit's bracket cites
`find-sources:71`, a line number that matches that same tree. The author counted
find-sources once while the second spelling sat seventeen lines above it. The
five-site set is therefore a decided scope, not a miscount, and sweeping the
sixth site was never required by the brief. No CONFIRMED or CONTESTED finding is
a missed, extra, or misunderstood requirement.

Against the brief step by step:

- **Step 1 (item 9).** All five canonical sites were located and collapsed:
  `skills/project-flow/SKILL.md:84`, `skills/import-source/SKILL.md:13`,
  `skills/publish/SKILL.md:11`, `skills/verify-citations/SKILL.md:9`, and
  `skills/find-sources/SKILL.md:91` (the audit's `:71`, re-located by content
  after Task 4's +20-line vendoring insert). The four "OUT" rulings
  (`setup-vault:21`, `evidence-conventions:64`, `publish:110`,
  `find-sources:74`) and the vault-template ruling
  (`research_vault/templates/vault/AGENTS.md`, pinned whole-file at
  `tests/test_templates.py:100`) are each recorded with reasoning in the report
  and in the commit body, which is what the brief asked for. Meaning is preserved
  at every collapsed site; the two enumerations most at risk of silent loss
  (publish's five artifacts, import-source's four) survive by moving into the
  subject as appositives, and publish's scope clause "not in a note, not in
  frontmatter, not anywhere" survives verbatim. One partial: at
  `project-flow/SKILL.md:84` the refrain spelling the audit indexed still stands
  beside the token that was to replace it, so that site is a punctuation join
  rather than a collapse (Minor below).
- **Step 2 (item 10).** Both shaping prohibitions are gone: "not as a raw dump"
  at `skills/find-sources/SKILL.md:108` and "not in raw run order" at
  `skills/verify-citations/SKILL.md:27`. In both cases the positive recipe and
  its rationale are untouched, which is the audit's "cut the prohibition half,
  keep the recipe" ruling applied exactly.
- **Step 3.** The judged grep's *substance* holds — I reproduced
  `grep -rn "not as a raw dump\|not in raw run order" skills/` at exit 1. The
  *transcript* of that step in the report is false (Important below). Pins: I
  grepped `tests/` for every removed substring and got zero hits, and both
  project-flow pins survive character-for-character. Suite: 1565 passed, 7
  skipped, reproduced. Commit subject matches the mandated
  `style: leading-word collapse + prohibition cuts`.

### Cannot verify from diff

- **Pre-commit gate, 8/8 hooks, with no reformatting of the five edited lines.**
  I declined to run it: `pre-commit run --all-files` invokes mdformat,
  ruff-format and yamlfix, which rewrite files, and this review is read-only.
  Controller check: run `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files`
  at eb54ab6, expect 8/8, and confirm `git status --porcelain` is empty
  afterward — a hook that reformats one of the seven changed lines would show up
  there.

Resolved during this synthesis, so no longer open — recorded here because three
lenses listed them as unverifiable:

- **Suite green.** `.venv/bin/python -m pytest tests -q` at eb54ab6 returns
  `1565 passed, 7 skipped in 92.00s`, exit 0, with no warnings or other noise.
  Matches the report and the baseline exactly.
- **No test pins the removed strings.** `grep -rn "Never hand-write\|is a CLI verb call\|the CLI does all of that already\|not as a raw dump\|not in raw run order\|appended through the CLI verb" tests/`
  exits 1. The green suite is genuinely unpinned on this material, not
  coincidentally passing.
- **Commit body.** `git log -1 --format=%B eb54ab6` carries a long body recording
  every ruling. Nothing in it is contradicted by the diff, and — relevant to the
  Important finding below — it does not repeat the false repo-wide grep claim;
  its only verification claims are the tests/ grep (verified true), the
  pre-commit 8/8, and the pytest counts (verified true).

## Strengths

- The implementer surfaced the boundary call (`find-sources:74`) in its own
  report and again in the commit body rather than leaving it silently unswept.
  Two of the three lenses raised that site only because the report made it
  findable; both Important framings then fell to verification. Disclosure worked.
- The audit's `find-sources:71` was re-located by content rather than trusted as
  a line number, correctly landing on today's `:91` after Task 4's +20-line
  shift. That is the tree-governs-facts discipline applied where it belongs.
- Every collapsed site preserves its enumeration by moving it into the subject,
  including the hardest one (`publish:11`), where all five nouns and the full
  location-scope clause survive. Nothing enumerated was silently dropped.
- Pin diligence: every string about to be removed was grepped against `tests/`
  before editing, and the two project-flow pins were preserved
  character-for-character inside a rewritten sentence rather than loosened.
- Scope is clean and auditable at a glance: five SKILL.md files, seven
  insertions, seven deletions, no vendored `references/` file, no test churn, no
  incidental reformatting. Every changed line is shorter than the one it
  replaced, so the sweep is genuinely subtractive.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

**`.superpowers/sdd/2026-08-22-post-q-batch/task-7-report.md:201` — the Step 3
evidence block prints a grep result that does not reproduce.** Status:
**CONFIRMED**.

The block prints:

```
$ grep -rn "not as a raw dump\|not in raw run order" . --include="*.md" --include="*.py"
(no output — checked repo-wide, not just skills/)
```

Run from the repo root, that command exits 0 with three hits:
`docs/2026-08-22-skills-layer-audit.md:135`, `:159`, and
`docs/superpowers/plans/2026-08-22-post-q-batch.md:78`. The last of these is the
very Step 2 line the brief quotes, so the grep could never have been empty. The
report's next paragraph (`:205-208`) compounds rather than corrects it, asserting
that both prohibitions "are gone from every `.md`/`.py` file in the repository,
including the audit doc and plan docs".

Why it matters: the step's substance is fine — the skills-only grep genuinely
reproduces clean at exit 1, and the three hits are record documents that stand as
written under this repo's own rule for analysis and plans. But the SDD report is
the durable audit trail for a task whose other claims are all self-reported
transcripts of the same form, and one of them demonstrably does not reproduce.
That is the specific thing this gate exists to catch. I contained the blast
radius myself — the suite, the tests/ greps and the commit body all check out —
but containment is not the same as the record being accurate.

How to fix: replace the block with the grep that was actually run and its real
output, and state the ruling explicitly — `skills/` is clean; the three
documentation hits are descriptive quotes in record documents and stand as
written. The false text exists only in the report file, which is gitignored; the
commit body does not repeat the claim, so no history needs touching.

### Minor (Nice to Have)

**`skills/find-sources/SKILL.md:74` — a sixth spelling of the refrain survives in
the same file as one of the collapsed five.** Status: **CONTESTED**, severity
corrected down from the Important both the spec and fidelity lenses filed.

Line 74 still reads "appended through the CLI verb, never hand-written:",
seventeen lines above the newly collapsed `:91` ("The CLI writes every line into
`search-log.md`"), so the file states the write-discipline doctrine twice in one
section. The duplication is real and undisputed. What did not survive is the
claim that leaving it is a spec miss: the git evidence above shows the author's
five-site set was drawn with this line already in the tree, and `:74`'s
affirmative-led shape (the CLI verb first, negation trailing) is the same shape
that `project-flow:84` and `publish:11` ship under the approved collapse. This is
an author call for a follow-up sweep, not a defect in this task.

If the author wants it: cutting ", never hand-written" leaves the affirmative in
place, loses nothing enumerated, and no test pins the string (verified, zero hits
in `tests/`).

**`skills/project-flow/SKILL.md:84` — the one named site where no collapse
happened.** Status: **NOT-VERIFIED-MINOR** (Minor findings are not put through
the verify pass).

The edit joins two sentences with an em dash and moves the enumeration from em
dashes into parentheses, 204 characters to 203. Both restatements survive: "the
CLI writes" and "never prose written by hand". Item 9's target is one token per
site, and this is the site where the indexed refrain spelling still stands next
to the token meant to replace it.

Two things bear on the ruling rather than the severity. First, the report
justifies the outcome by pin preservation ("No pin changed"), but the plan's own
constraint lists `tests/test_project_flow_skill.py:149` among the known pins on
refrain phrasing and requires pins to update in the *same* commit as the prose —
so pin preservation is not by itself a reason to leave prose uncollapsed.
Second, the report's supporting claim that "the audit praised project-flow as the
closest to ideal of the five" (`task-7-report.md:92-94`) has no source: grepping
the audit for `project:84|project-flow|ideal|closest` returns only the
`:130`/`:151` site index, the `:367` rename ruling, and unrelated lines at
`:375`, `:381`, `:401`. I verified this myself.

Kept Minor because meaning is fully preserved and the token does lead the
sentence. Either revert to the original two sentences (zero-cost, since no
collapse is being achieved) or do the real collapse and update
`tests/test_project_flow_skill.py:149` in the same commit, as the constraints
allow. Best decided together with the `find-sources:74` ruling.

**`skills/publish/SKILL.md:11` (and `skills/import-source/SKILL.md:13`) — the
enumeration is hoisted into an appositive on "act".** Status:
**NOT-VERIFIED-MINOR**.

"Every mechanical act below — a status, a `verified` event, a tag, an
acknowledgment, a review-inbox entry — is a CLI verb call" now says a status is
an act; import-source does the same with "a literature note, a managed region".
In the originals those nouns were objects of "hand-write", where the grammar was
correct. `publish:11` additionally stacks three em dashes doing two different
jobs (appositive pair, then a trailing scope clause), which makes the reader
re-parse whether "never by hand" attaches to the enumeration or to the verb
clause.

Attaching the enumeration to what is written rather than to "act" fixes both, for
example: "Every mechanical act below is a CLI verb call: you compose and explain,
the person chooses, the CLI writes a status, a `verified` event, a tag, an
acknowledgment, a review-inbox entry — never by hand, not in a note, not in
frontmatter, not anywhere."

## Refuted During Verification

Three Important framings were knocked down. All are recorded here rather than
dropped, and none is resurrected as blocking.

1. **Spec lens, `skills/find-sources/SKILL.md:74`, Important — REFUTED.** The
   finding's quotes were accurate, but its load-bearing premise was that the
   audit's "five spellings across five skills" census is factually falsified at
   HEAD, so under the tree-governs-facts doctrine the tree overrides the
   enumeration. Git disproves it: `git show 82b23a9:skills/find-sources/SKILL.md`
   — 82b23a9 being the commit that added the audit — already carried both
   clauses, at `:54` and `:71`, and the audit cites `find-sources:71`, matching
   that tree exactly. The author counted this file once with both spellings
   visible. I re-ran this check myself.
2. **Fidelity lens, `skills/find-sources/SKILL.md:74`, Important — CONTESTED, and
   the contested claim does not hold.** Its distinguishing claim was that `:74`
   is "the last surviving negation spelling of the refrain in the swept skills".
   False at HEAD: `skills/project-flow/SKILL.md:84` ships "…is a CLI verb call,
   never prose written by hand" (test-pinned at
   `tests/test_project_flow_skill.py:149`) and `skills/publish/SKILL.md:11` ships
   "…the CLI writes — never by hand, not in a note, not in frontmatter, not
   anywhere". I confirmed both by grepping `skills/` at HEAD. `:74` matches the
   approved collapse shape rather than residual defect.
3. **Quality lens, `skills/verify-citations/SKILL.md:9`, Important — REFUTED.**
   The finding argued that turning "Never hand-write a result, a `verified`
   event, **or** a review-inbox entry — the CLI does all of that already" into
   "the CLI writes a result, a `verified` event, **and** a review-inbox entry"
   introduces an unconditional claim contradicted by the same file's `:31`,
   `:32` and `:36`. It misreads the original: the "or" sat under a negation
   (never A, never B, never C — carrying no conditionality), and the original's
   second clause, "the CLI does all of that already", was itself a conjunctive
   assertion over all three artifacts. The new sentence makes no claim the file
   did not already make; any overclaim here predates this diff and is not a
   regression introduced by it.

Merged, not dropped: the quality lens's Minor variant of `find-sources:74` is
folded into the Minor finding above, and the fidelity lens's Minor variant of
`verify-citations:9` ("restore the disjunction, and → or") rests on the same
premise as framing 3 and falls with it — it survives only as an optional
one-word polish with no defect behind it.

## Assessment

**Task quality: Needs fixes.**

The prose work itself is sound and in scope — five sites collapsed with every
enumeration preserved, two shaping prohibitions cut with their recipes intact, no
test churn, suite green at 1565/7 and independently reproduced. The single
blocking item is not in the skills at all: the report's Step 3 evidence block
prints a repo-wide grep as returning nothing when it returns three hits, and that
fabricated transcript is the only thing standing between this task and approval.
Correct the block, state the record-documents ruling explicitly, and the three
Minors (find-sources:74, project-flow:84, the appositive grammar) are follow-up
material for the author, not gate material.
