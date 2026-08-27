# Task 6 review - 97afad5..8bc6294

## Spec Compliance

**Verdict: compliant.**

Both of the brief's steps landed, and the one constraint that carried real risk —
byte preservation of the moved content — was verified rather than asserted, by
every lens independently.

Step 1 asked that §7 (refresh), §8 (batch) and §9 (archive) move unchanged into
`skills/import-source/references/`, that `SKILL.md` receive a pointer table in
find-sources' shape, and that tests stay put and green. All three files exist —
`skills/import-source/references/refresh-mode.md` (13 lines),
`references/batch-mode.md` (15), `references/archive-at-import.md` (29) — one
section per file, no content duplicated between `SKILL.md` and the references.
Two lenses re-derived the implementer's three body sha256 values from
`git show 97afad5:skills/import-source/SKILL.md` and got byte-for-byte matches;
a third reproduced the same result by extracting removed and added lines from the
diff and diffing them (36 identical non-blank lines, identical order). The
comparison was run against the post-gate tree, so it also proves mdformat did not
silently rewrite the moved prose.

The one edit to moved content is the heading adaptation —
`## 7. Refresh mode: fresh, stale, orphaned` → `# Refresh mode: fresh, stale, orphaned`,
and likewise for §8 and §9 — with the title text otherwise verbatim. A standalone
reference file cannot carry the parent document's sequence number, so this is the
"defensible IF stated" case, and it is stated in both the report
(task-6-report.md:128-137) and the commit body.

The pointer table at `skills/import-source/SKILL.md:98-102` does match
find-sources' shape as the controller scoped it: three columns ending in a plain
code-span reference path, the same form as `skills/find-sources/SKILL.md:41-52`.
The three rows are accurate against the files they point at, and all three verbs
(`import-note`, `backfill-selectors`, `archive-source`) exist in
`knowledge_harness/__main__.py`.

Step 2's commit subject is exact and there is one commit on top of BASE.

The check-id sweep question the brief raised is closed cleanly: an independent
run of Task 3's extractor (`tests/test_skill_contracts.py::_enumerated_check_ids`)
over BASE and HEAD returns byte-identical output, and an isolated run over the
§7-9 substring alone returns zero matches — the sweep never recognised a check-id
enumeration inside the moved text, so the move removed nothing from its coverage
and no test prose overstates the corpus. This is the "claimed coverage exceeds
actual coverage" class that bit earlier tasks in this plan, and it did not recur.

**Issues:** none rising to a spec violation. The three open findings below are all
Minor. The one at CONTESTED status (`SKILL.md:96`) is a quality gap in freshly
authored glue prose, not a missed, extra, or misunderstood requirement — the
sentence it is about is not mandated by the brief in either direction, and the
shape the brief did pin shipped correctly.

### Cannot verify from diff

1. **Suite green offline at 8bc6294 — 1565 passed / 7 skipped.** No lens re-ran
   the suite; the review instruction forbade it. The +3 delta against the 1562
   baseline was verified statically and holds: it is three new parametrizations of
   the pre-existing `test_markdown_table_rows_have_no_truncated_code_spans`, whose
   `_mdformat_owned_markdown()` corpus globs `skills/**/*.md` recursively and so
   picks up the three new reference files automatically. Controller check: one
   `.venv/bin/python -m pytest tests -q` at 8bc6294; expect `1565 passed, 7 skipped`
   and warning-free output.
2. **Form gate 8/8** (`PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files`).
   Not re-runnable from a read-only review, since the hooks reformat. Controller
   check: one `--all-files` run at 8bc6294; expect 8/8 with no files modified. Note
   that the mdformat half is already transitively verified — the sha256 comparison
   above ran against the committed, post-gate tree and matched the pre-edit blob
   exactly, so mdformat demonstrably left the moved content alone. The other seven
   hooks remain unverified report claims.

## Strengths

- **Byte preservation was verified, not asserted, and verified in the right order.**
  The implementer ran the hash comparison *after* the form gate, which is precisely
  where a silent rewrite would have landed. Three lenses reproduced the result
  independently by two different methods.
- **The one adaptation to moved content is disclosed in both the report and the
  commit body**, and is exactly the adaptation a standalone file requires. Title
  text is otherwise verbatim.
- **Every checkable claim in the commit body reproduced under independent
  measurement** — the sweep delta, the three body SHAs, the +3 attribution, the 8/8
  form gate. In a plan that has twice had to correct false commit-body claims, a
  body that survives verbatim re-derivation is the signal that matters.
- **The cross-task hazard the controller weighted highest is genuinely closed.**
  Independent runs of the Task 3 sweep extractor over BASE and HEAD return
  identical output, and the three new files score zero even if the corpus were
  widened.
- **No false provenance.** The new files carry no vendoring header, no upstream
  commit, no never-hand-edit rule; the commit body states explicitly that only
  find-sources' pointer-table *shape* was borrowed, not its vendoring semantics.
- **The self-caught amend was the right call and landed correctly.** The advisor
  caught the first commit's body claiming a "three-column pointer table" over a
  two-column table; the fix added the `Verb` column, was re-verified against the
  sweep *before* the amend, and the body is now true of the shipped table.
- **The orphaned "as above" was surfaced and reasoned about rather than quietly
  fixed or quietly ignored.** Leaving the bytes intact preserved the very guarantee
  the SHA comparison rests on, and the item was carried forward as a scoped
  follow-up in the report, the commit body, and the concerns section.
- **Clean decomposition.** One section per file, each named for what it is, no file
  left oversized, nothing duplicated across the split.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

None. One finding arrived from the quality lens labelled Important and is recorded
below at Minor with the correction reasoned out; see `SKILL.md:96`.

### Minor (Nice to Have)

**1. `skills/import-source/references/batch-mode.md:9` — "the same per-note
contract as above" no longer resolves.**
*Status: NOT-VERIFIED-MINOR. Plan-mandated: yes.*

All three lenses raised this at the same line and agreed on both substance and
severity. The "above" was §7 in the same document; it is now the sibling file
`references/refresh-mode.md`, so a standalone reader of `batch-mode.md` has no
referent.

Why it matters: a cross-reference that points at nothing is documentation rot the
move introduced, in prose an agent reads in order to act. It stays Minor because
the same sentence's colon clause restates the substance inline — "each note comes
back fresh, stale, or orphaned, and every failure files its own record" — so no
operative information is lost; only the literal word is orphaned.

Why it is plan-mandated: the brief's byte-preservation constraint is exactly what
forbids the one-word fix inside this task, and byte preservation should win here,
because it is the instrument the byte-identity verification depends on. Leaving the
bytes alone and disclosing the orphan was the correct conservative reading. A
disclosed one-word repoint would have been equally compliant and is the better end
state, but that makes this a recommended follow-up, not a defect that blocks.

How to fix: in a follow-up scoped as its own change, repoint the phrase — "with the
same per-note contract as `references/refresh-mode.md` describes" — and state the
one-word edit in that commit's body, exactly as the heading adaptation was stated
here. Note this is a moved-bytes edit, so it needs the disclosure; the fix at item
2 below does not.

The brief's "anywhere else?" check was run across all three new files (grep for
above/below/earlier/previous/section/§): the only other positional-looking hit is
`refresh-mode.md:8`'s "The free region below it survives", which is note-internal
rather than document-positional, and `archive-at-import.md:17`'s "the shared exit
codes", which is non-positional and immediately followed by a self-contained
four-state/exit table. Both are clean.

**2. `skills/import-source/SKILL.md:96` — the pointer table's lead-in ships without
a read-before-acting imperative, and frames all three modes as extensions of the
core flow.**
*Status: CONTESTED (stands; not refuted). Plan-mandated: no.
Severity corrected from Important — reasoning below.*

The freshly authored §7 intro reads "Three more modes extend the core flow above;
each is documented in full on its own so this file stays focused on the catalog →
integrate path." find-sources' equivalent paragraph carries an imperative that this
one does not (`skills/find-sources/SKILL.md:55`, "Read the relevant reference file
before calling"). The text now behind the archive pointer says "Run this for every
web source you catalog, in the same session" and "**It is the sole writer of that
field** — never hand-write, edit, or remove an `archive-url`". After this change,
`archive-source` appears in the whole of `skills/` only at `SKILL.md:102` and inside
`references/archive-at-import.md`; §1 (Catalog) never mentions archiving, and
`SKILL.md:13`'s own never-hand-write list does not name `archive-url`.

Why it matters: the archive mandate is the one obligation in this skill whose
omission is unrecoverable — "Rescue is impossible after the fact" — and it moved
from always-loaded prose to a pointer hop with nothing telling the reader to take
the hop.

Why Minor rather than Important. Severity attaches to what the implementer
authored, not to what the plan ordered, and the relocation itself is the plan's
decision: the audit adjudicated it APPROVED (`docs/2026-08-22-skills-layer-audit.md:85`
and `:361`), with the flip condition recorded explicitly ("refresh-dominant usage
returns them inline"). The prominence trade was accepted knowingly upstream, and
accepted adjudications stand as written. What the implementer owns is one sentence
of fresh prose plus one absent sentence, and:

- "extend the core flow" is not "optional"; the sentence explains why the content
  lives elsewhere rather than asserting that archiving sits outside the catalog
  path. The plain reading of the shipped sentence is not false.
- The imperative's absence is a quality gap, not a missed requirement: the
  controller pinned "find-sources' shape" to the pointer table's form, and
  find-sources' imperative sits outside that range.
- The mitigations are real. The row itself carries both the trigger (`url`, no
  `doi`) and the timing ("at import"), and the invocation commands for all three
  modes exist only in the reference files, so an agent cannot act on a mode without
  opening its file. The residual failure mode requires an agent to read a row that
  says "at import" and skip it anyway.
- Two of three lenses rated this Minor on the same evidence. The verification pass
  that returned STANDS confirmed the finding's citations, not its severity label.

The status stays CONTESTED — the substance was not refuted, and lowering the
severity is not licence to launder the status. Under the synthesis rules a Minor
finding at CONTESTED does not block.

How to fix: one sentence of fresh prose after the table, which touches no moved
bytes and so needs no byte-preservation disclosure — mirror find-sources'
imperative, e.g. "Read the reference file before running its verb; each carries
rules the table cannot — the archive verb is the sole writer of `archive-url`, and
an UNREACHABLE attempt is not a snapshot." If it lands in the same follow-up commit
as item 1, the body should disclose both, since only item 1 touches moved content.

**3. `skills/import-source/SKILL.md:100` — the three new `references/` pointers are
unpinned.**
*Status: NOT-VERIFIED-MINOR. Plan-mandated: no.*

No test asserts that the paths named in the pointer table resolve to files that
exist; a grep over `tests/*.py` for `references/` returns nothing.

Why it matters: renaming or deleting any of the three reference files leaves a
silently dead pointer in an entry skill and nothing in the suite catches it. This
is not a regression introduced here — find-sources' eleven pointers
(`skills/find-sources/SKILL.md:41-52`) are equally unpinned, so the change follows
the repo's established state. Coverage could be broader; nothing was made worse.

How to fix, if judged worth guarding: one generic test over `skills/*/SKILL.md` that
extracts every `references/...md` code span and asserts the file exists. It would
cover find-sources' eleven pointers in the same stroke.

## Refuted During Verification

No finding was refuted. All three lenses' findings survived adversarial
verification, and all three are carried forward above.

One label was corrected rather than dropped: the quality lens's `SKILL.md:96`
finding arrived at Important and is recorded at Minor, with the reasoning stated in
full under that entry and its CONTESTED status preserved. Nothing was discarded.

Findings that arrived from more than one lens were merged, not dropped:
`batch-mode.md:9` was raised by all three lenses (statement kept from the fidelity
lens, which also ran the brief's "anywhere else?" sweep), and the `SKILL.md` lead-in
finding was raised by the spec lens at :96, the quality lens at :96 and the fidelity
lens at :98 — one defect, one entry.

## Assessment

**Task quality: Approved.**

The move is exactly what the brief asked for, byte preservation was proved rather
than promised, and the two hazards this plan has been burned by before — false
commit-body claims and silently narrowed test coverage — were both measured and
closed. Three Minor findings remain, all deferrable: two one-sentence prose
follow-ups and one pre-existing coverage gap the change did not create.
