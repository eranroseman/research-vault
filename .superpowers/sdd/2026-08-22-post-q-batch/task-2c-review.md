# Task 2c review - 3d26a44..a5668d6

## Spec Compliance

**Verdict: issues.**

Step 1 landed structurally as written. The template opens with a two-sentence
integrity preamble at `knowledge_harness/templates/vault/AGENTS.md:6`, placed as
the first paragraph after the `# Vault agents guide` heading and ahead of the
routing index at lines 12-22. It restates none of the seven skills,
`synthesis/index.md`, or `evidence-conventions`, so the brief's "don't restate
the routing index" constraint holds. The surface list was adjusted, per the
brief's rider, to the three surfaces the template's own prose already names.

Step 2's mandated commit message landed exactly:
`feat: vault AGENTS.md opens with the integrity preamble` (commit a5668d6).

The compliance gap is in substance, not structure. Step 1's purpose is an
accurate defense for the agent that reads nothing else, and the shipped
enforcement clause — "hand edits leave a trace" — is false for the most natural
hand edit to one of the three surfaces the same sentence names. The locus
matters: this wording is the plan author's ruled replacement for the brief's
original clause, applied verbatim by the implementer after it independently
flagged the original as false and escalated rather than shipping it silently.
The deviation is in the ruled wording, not in implementer execution, so the fix
is an author decision.

### Cannot verify from diff

- **Brief Step 2's rider: "Item 15's live-vault application now carries this
  too."** Nothing in this diff touches item 15. When item 15 lands, check that
  the live-vault AGENTS.md application reproduces the preamble bytes verbatim
  from `knowledge_harness/templates/vault/AGENTS.md:6` — including whatever
  final wording the enforcement clause settles on after the Important finding
  below is ruled.
- **The 8-hook pre-commit form gate at a5668d6.** Report-claimed only. This
  review is read-only and `pre-commit run --all-files` can rewrite files, so it
  was not run here. Confirm from the implementer's captured output, or re-run in
  a disposable checkout rather than this worktree.

Two items the lenses could not resolve were resolved during synthesis and are
recorded here rather than passed to the controller:

- **Suite green at a5668d6.** Verified directly:
  `.venv/bin/python -m pytest tests -q` at HEAD a5668d6 gives
  `1575 passed, 7 skipped` with no warnings summary, and `git status --short` is
  clean afterward. `tests/test_templates.py` alone gives `7 passed`. This matches
  the stated baseline exactly.
- **Amend fidelity, 514d12b -> a5668d6.** Verified directly: `git diff 514d12b
  a5668d6` shows exactly two hunks, one per file, each changing only
  `hand edits are warned in session and caught at commit` to
  `hand edits leave a trace`. Nothing else moved in the amend.

## Strengths

- The preamble sits where the brief said it must: first paragraph after the H1,
  two sentences, before the routing index, restating no other section of the
  document.
- The diff is purely additive and independently confirmed: a single hunk
  `@@ -1,15 +1,17 @@` with no `-` lines, stat 5 insertions / 0 deletions. Line
  24 (managed regions) and line 26 (machine surfaces) are byte-identical to base.
  Nothing was deleted or gutted.
- `tests/test_templates.py:100-105` — the pin is a whole-file byte-equality
  assertion, so it genuinely verifies the "opens with" ordering requirement. A
  presence-only check would have passed on a preamble appended at the bottom;
  this one would not.
- The pin was updated in the same commit as the content it pins, and the added
  string concatenation reproduces template line 6 byte-for-byte including the
  U+2014 em dash.
- The pin was found by running the suite rather than trusting the brief's list,
  matching the batch's task-2b lesson: the implementer edited the template
  alone, ran the full suite, confirmed exactly one failure, then grepped for a
  task-2b-style second pin before concluding there was none.
- Every surface the preamble names is genuinely machine-written. `literatures/`
  is projected and warned at `hooks/posttooluse_lint.py:97`; `log/` and
  `inbox/review-queue.md` have the CLI as sole writer and are protected by
  `lint_append_only` at `knowledge_harness/lints.py:109-152`. "The CLI writes
  them" is exactly right for `inbox/review-queue.md`, where human acknowledgment
  entries are a supported workflow but only through the CLI verb.
- "Machine-written" is established repo vocabulary rather than a coinage — it is
  the term used in `docs/adr/0001-vault-outlives-harness.md:7` and
  `docs/terminology.md:43` — so line 6 does not open a vocabulary split against
  line 26's "owner-written".
- The implementer executed the author's ruling faithfully and verbatim, having
  first flagged the original clause as false and escalated it rather than
  shipping it silently.

One strength claimed by the quality lens was dropped in synthesis: that
"leave a trace" is the strongest claim holding across all three named surfaces.
The spec lens's CONFIRMED finding below refutes it.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

**`knowledge_harness/templates/vault/AGENTS.md:6` — the enforcement clause
"hand edits leave a trace" is false for in-format hand appends to `log/`.**
Status: CONFIRMED. Plan-mandated wording.

*What is wrong.* An agent that hand-appends a well-formed line to a `log/` day
file produces no session warning, no verify finding, and no record anywhere in
the harness. The claim the preamble makes about that surface does not hold.

*Why it matters.* This is the anti-fabrication preamble, written for the agent
that reads nothing else, and the author's ruling existed precisely to replace a
claim false for two of three surfaces with one true of all three. Verified
against code, not prose:

- `hooks/posttooluse_lint.py:97,104` warns only for paths under `literatures/`
  and for `CONCEPT_ROOTS = {"synthesis", "projects"}` — never for `log/` or
  `inbox/review-queue.md`.
- `knowledge_harness/lints.py:141-142` fires `append-only` only when
  `not new_bytes.startswith(old_bytes)`, so a pure append passes silently.
- `append-only` is absent from `CLOSING_BY_SURFACE["commit"]`
  (`knowledge_harness/verify.py:53-58`, which is
  `frozenset({"citekey", "evidence-layer"})`), so nothing gates.
- `knowledge_harness/okf.py:8-16,35` then copies the hand-appended line into
  root `log.md` on the next regeneration — a fabricated log entry laundered into
  a machine artifact with zero trace.

The spec lens reproduced this end to end in a scaffolded vault: an in-format
append to `log/2026-08-24.md` gave `verify --offline --surface commit` exit 0
with zero findings and no `inbox/review-queue.md` entry, after which
`okf.regenerate_log` copied the fabricated line verbatim into root `log.md`. All
four code anchors were re-read independently during synthesis and check out. The
author's three cited truth-makers — evidence-layer closure, append-only
findings, drift records — each miss this case. The only remaining "trace" is git
history itself, which is equally true of every free-prose file in the vault and
so carries no discriminating force.

*Scope, precisely.* Fully true for `literatures/` (warned in session and blocks
at commit). True for destructive edits on all three surfaces. False for
in-format appends to `log/`, and secondarily for a schema-conforming hand append
to `inbox/review-queue.md` (`knowledge_harness/inbox.py:455-530` raises
`InboxError` only on malformed lines).

*How to fix.* Author decision, not the implementer's. Either narrow the clause
to the behavior that holds universally — for example naming the destructive case
("hand edits that rewrite them are recorded") — or scope the enforcement claim
to `literatures/` and let the surface list stand bare. Whatever wording lands
must be re-verified against `_is_append_only_path` semantics rather than against
the template's own prose. Rule this together with the root `log.md` question in
the first Minor finding below: any wording that later covers root `log.md` needs
"regenerated away" rather than "leaves a trace", since hand edits there vanish
silently on the next regeneration. The two fixes belong in one pass.

### Minor (Nice to Have)

**`knowledge_harness/templates/vault/AGENTS.md:6` — the preamble omits root
`log.md`.** Status: NOT-VERIFIED-MINOR (corroborated in synthesis by reading
`knowledge_harness/okf.py:38`). Not plan-mandated.

The brief's draft listed root `log.md`; the implementer dropped it because the
template names it nowhere else, which is the literal reading of "adjust the
surface list to what the template already names". But root `log.md` has a single
writer that rewrites the file wholesale (`knowledge_harness/okf.py:38`,
`(vault / "log.md").write_text(text)`), so an agent that hand-edits it loses the
edit silently on the next regeneration. A surface with that failure mode appears
in neither line 6 nor line 26, so the oblivious-agent defense has no coverage for
it at all. The absence pre-dates this change and the coordinator deferred the
question to final review, so this is that surfacing rather than a regression.
Fix: have the plan author rule on whether root `log.md` belongs in the surface
list. Do not simply append it to the current sentence — "hand edits leave a
trace" is false for it, so adding it unchecked would ship a second false claim.

**`knowledge_harness/templates/vault/AGENTS.md:6` — a second, divergent
enumeration of machine surfaces.** Status: NOT-VERIFIED-MINOR. Plan-mandated
(the overlap is directed by the brief; the divergence is not).

Line 6 enumerates {`literatures/`, `log/`, `inbox/review-queue.md`}; line 26
enumerates {`log/`, `inbox/review-queue.md`, managed regions,
`system/bibliography.json`}. Neither list contains the other. The document
previously partitioned these cleanly — line 8 owned `literatures/` under the
projection rule, line 26 owned "Machine surfaces" — and now a 30-line file
carries two competing lists of the same concept with two different consequence
clauses ("leave a trace" versus "regenerated away or raise a finding"). Neither
is marked as the short form, so a later editor updating one has no signal the
other exists. Fix: mark line 6 explicitly as the abridged form (for example
"machine-written surfaces include ...") so line 26 reads as the complete
enumeration, or reconcile the lists so one is a strict subset of the other.

**`tests/test_templates.py:105` — the pin's explanatory comment does not cover
the new clause.** Status: NOT-VERIFIED-MINOR. Not plan-mandated.

The comment block at lines 94-99 exists precisely to stop a future editor from
"tightening" template prose into a claim the enforcement code does not back, but
its parenthetical ("append-only covers log/ and inbox/review-queue.md but is in
no CLOSING_BY_SURFACE set, so 'fail the gate' was false") explains line 26's
wording, not line 6's. An editor who reads the preamble and strengthens it back
to "caught at commit" would reintroduce exactly the false claim the comment was
written to prevent, and nothing in the file would stop them. Fix: extend the
comment to state the constraint governing the preamble clause. State the
constraint only — the dated provenance of the ruling belongs in the commit body,
where the report says it already is. This fix should be folded into whatever
rewording resolves the Important finding, since the constraint to record depends
on the clause that lands.

## Refuted During Verification

None. No finding from either lens was refuted. The one Important finding was
independently reproduced against a scaffolded vault by the spec lens and its
code anchors re-read during synthesis; the three Minor findings were carried at
their lens status, and all three were corroborated by direct reads of
`knowledge_harness/okf.py`, the template, and `tests/test_templates.py` during
synthesis.

## Assessment

**Task quality: Needs fixes.**

The mechanical execution is clean — additive diff, correct placement, pin
updated in the same commit and byte-exact, suite verified green at a5668d6
(1575 passed, 7 skipped), and the enforcement code read rather than assumed
before the surface list was chosen. What blocks is one sentence: the ruled
clause "hand edits leave a trace" is false for in-format appends to `log/`, the
exact path by which a fabricated entry gets laundered into root `log.md`. The
fix is small — the plan author re-rules one clause and the pin follows — and it
should be ruled in the same pass as the root `log.md` omission.
