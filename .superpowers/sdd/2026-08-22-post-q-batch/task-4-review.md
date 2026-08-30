# Task 4 review - 2150da9..800c492

## Spec Compliance

**Verdict: compliant.**

All four brief steps landed, and each landed as the decided source documents
specify rather than as a paraphrase.

- Step 1 (C-3 + item 11 fold): `skills/find-sources/SKILL.md:70` ships the C-3
  card's decided replacement wording verbatim - "Several of these APIs take a
  credential in the query string, so the fetched URL *is* a credential" - with
  the four-of-six hand-redaction list deleted and `scripts/_common.py`'s
  `redact_url` named as the authority. The polite-pool contact is sourced from
  `.research-vault/machine.json`'s `mailto`, else `RV_MAILTO`, with the plain
  statement that the vendored scripts do not read it. The vendoring paragraph's
  "no-credential" claim is corrected in the same fold, which the brief's Step 1
  line does not name but the cross-read finding's own remedy does.
- Step 2 (C-5): one line, at `skills/find-sources/SKILL.md:11`.
- Step 3 (item 12): one `## Vendoring notes` section carrying six annotations
  and two class-3 guards, plus the three routing touches the brief names - the
  `scripts/paginate.py` row's "never a single-DOI lookup", the OpenAlex row's
  "(abstracts: `scripts/openalex_abstract.py`, not that file's snippet)", and
  the `OPENALEX_API_KEY` caution as guard 2.
- Step 4: the pin ships in the same commit, and the commit subject is the
  brief's mandated string verbatim.

Fidelity of the six annotations to the triage was checked bullet-by-bullet
against `docs/2026-08-22-references-cross-read.md:56`: the shipped bullets are
one-to-one with the triage's class-2 list (preprint-fallback contradiction,
category-separator conflict, stale paginate docstring counts, phantom NCBI/S2
keys, biorxiv reconciliation overstatement, openalex lossy inversion). No
seventh bullet, no dropped one, and each bullet's substance traces to its own
confirmed finding rather than to a fresh reading of an upstream file.

The brief's "+ its `references/` where the cross-read says so" resolves to
nowhere, deliberately, and that judgment is right. Six individual findings say
the remedy is an annotation on `biorxiv.md`/`medrxiv.md`/`openalex.md`, but the
triage - the decided set - says "one vendoring-note section", and the triage
governs. Three independent supports agree: the vendored files carry "Do not
hand-edit this file", `AGENTS.md` holds record documents as written, and an edit
would falsify `skills/find-sources/SKILL.md:11`'s own "unmodified except for a
provenance header on each" sentence in the very commit that cites it.

The one Important finding below is a record defect under the standing author
doctrine, not a missed, extra, or misunderstood brief requirement, so it does
not turn the spec verdict.

### Cannot verify from diff

- **Which bioRxiv/medRxiv `category` separator convention actually filters**
  (`skills/find-sources/SKILL.md:16`). The annotation ships the three-way
  conflict unresolved, which is the triage's own decided state - it defers to "a
  two-curl live probe at slice time" - and no live call was made in this commit,
  as required. Controller check: run the two-curl probe at slice time (the same
  bioRxiv query with and without `?category=`, in each of the underscore /
  URL-encoded / hyphenated forms) and fold the answer back into the bullet.
  Track it as a slice-time item so the annotation gets resolved rather than left
  standing as a permanent hedge.
- **The stderr guard's "OpenAlex answers an invalid key with 403 - precisely the
  case that prints"** (`skills/find-sources/SKILL.md:27`). The un-redacted-URL
  half is verified in code (`skills/find-sources/scripts/paginate.py:86`), and
  the 403 half traces to `references/openalex.md:181` via the cross-read, so
  only live behaviour remains unverified. Controller check: confirm against
  OpenAlex's documented auth-failure status on the same slice-time live leg as
  the category probe.
- **Suite green offline at task end (1561 -> 1562, +1 new pin) and the 8-hook
  form gate passing.** No lens re-ran the suite, per instruction. The reported
  delta is exactly the one new test visible in the diff
  (`test_the_skill_names_exactly_the_environment_variables_the_scripts_read`),
  so the arithmetic is accounted for. Controller check: confirm the run itself
  from the implementer's transcript, or one re-run of
  `.venv/bin/python -m pytest tests -q`.
- **The shipped `research/validation-slice/...` paths resolve** (commit body,
  report, and the test docstring at
  `tests/test_find_sources_vendor.py:236`). Per the controller's PATH RULE these
  are deliberately ahead of this branch. Controller check: at merge, confirm
  `research/validation-slice/2026-08-22-references-cross-read.md` and
  `...-skills-layer-audit.md` exist at those exact paths.

## Strengths

- **Every line reference into the frozen vendored files was re-derived against
  HEAD rather than copied from the cross-read.** Two lenses independently
  sampled all thirteen shipped refs and I re-sampled eight of them directly:
  `references/biorxiv.md` 12, 40, 115, 156-160, 163-164, 172,
  `references/medrxiv.md` 12, 53, 135, `references/europepmc.md` 16-17, and
  `references/openalex.md` 162-172 all land on the text the annotation quotes.
  Seven of the cross-read's own refs had rotted; shipping them unchecked would
  have pointed agents at blank lines and headings. Invoking the standing author
  doctrine here was correct on the merits.
- **The claims behind both guards check out against the code, not only against
  the source document.** `fetch()` raises `HTTP {error.code} from {url}`
  un-redacted (`skills/find-sources/scripts/paginate.py:86`) while the
  provenance list and `--dry-run` use `redact_url` (`:345`, `:444`);
  `DEFAULT_MAX_CALLS = 50` (`:52`) with `--max-calls` validated `>= 1` (`:435`),
  so the suggested `--max-calls 1` workaround is real; bioRxiv `delay=1.0`
  (`:267`) backs "a second apart"; `APIS` holds exactly five walkers
  (`:264-302`) with `--list-apis` at `:411`, backing the "six of the ten"
  correction. The OpenAlex inversion bullet matches
  `scripts/openalex_abstract.py`'s own docstring and its collision-keeping
  implementation.
- **The new pin is a real behavioural assertion, not a tautology.**
  `tests/test_find_sources_vendor.py:254` reads the scripts' AST and fails the
  moment a re-vendor adds, drops, or renames a recognised env read - precisely
  when the two new SKILL.md claims go stale. AST rather than substring is the
  right call: a grep would match `paginate.py`'s own dead docstring names at
  `:28-29` and pass for the wrong reason.
- **Both guards with a point of use are placed at that point.** The
  `scripts/paginate.py` script-table row and the OpenAlex routing row carry
  their caveats inline, so an agent reading the table hits them without reading
  the errata section.
- **Neither of the brief's two supplied numbers ships.** Both were re-derived
  (six `REDACTED_PARAMS`, three query-string-key APIs) and then deliberately
  left out: the prose says "several" and makes `redact_url` the authority, which
  is exactly the C-3 card's decided resolution and removes the rottable
  inventory the card objected to.
- **The self-review caught two genuine regressions before shipping.** The first
  draft's "authenticate by query string" would have reintroduced the quibble the
  C-3 card records and rejects, and the stderr guard's original "redact it by
  hand first" would have contradicted, in the same commit, the hand-list
  deletion in step 5. Both are visible as corrected in the shipped text.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

**`skills/find-sources/SKILL.md:21` - the deviation ledger is incomplete by one
entry, and the report affirmatively misfiles that entry as verified.**
Status: **CONFIRMED.**

*What is wrong.* A seventh line-reference deviation ships undeclared. The
annotation cites `references/biorxiv.md:142-145` for the version-vs-first-posting
warning, where the cross-read source cites `biorxiv.md:140-144`
(`docs/2026-08-22-references-cross-read.md:29`). Commit `800c492`'s body says the
cross-read's numbers are "off in six places at HEAD" and lists six; this range
appears in neither that list nor the body's "correct as cited" list. Worse,
`task-4-report.md:57` puts it under "Correct as cited: ... `biorxiv.md:142-145`"
- but the cross-read never cited 142-145, so a verification claim the implementer
made is itself false. I confirmed independently: `142-145` occurs nowhere in the
repository except the shipped SKILL.md line and the report, and the cross-read's
only citation for that content is 140-144.

*Why it matters.* The standing author doctrine is what authorised the six
declared changes to decided content, and it requires deviations to be recorded
in the commit body. The body's "six places" is false as written, so the audit
trail understates what was changed - and in a repository whose posture is record
fidelity and no-fabrication, a ledger that is incomplete by its own framework
cannot be trusted for the other six. The false "Correct as cited" line is the
sharper half: it asserts a verification that did not happen, in the same document
that invokes the no-fabrication doctrine to justify the deviations. The fix
window closes at merge, since a commit body is immutable once merged.

*How to fix.* Record-only; no prose change. The shipped number is substantively
the better one - the version-vs-first-posting paragraph runs
`references/biorxiv.md:142-146`, and the same +2 drift explains the six declared
corrections. Amend the commit body to list `biorxiv.md` 140-144 -> 142-145 as the
seventh deviation, and correct `task-4-report.md:57`'s "Correct as cited" list.

*Severity resolution.* The fidelity lens rated this Important and verification
STANDS'd every claim; the spec lens rated the same substance Minor. Important is
kept, per the dedup rule and because the remedy is unavailable after merge.

*Two further departures, folded here rather than raised separately.* The
category-separator bullet adds the workaround "compare it against the same query
unfiltered", which is in neither the finding nor the triage, and the C-5 line
adds "where a vendored file and this one disagree, this one governs" beyond audit
option (a)'s wording. Both are defensible editorial additions - neither is false,
and the second follows from the audit's own observation that the SKILL.md table
is what an agent reads first. They are worth a mention when the ledger is
amended, but they are not deviations of the kind the doctrine is about, and as
standalone findings they would dilute the confirmed core.

### Minor (Nice to Have)

**`tests/test_find_sources_vendor.py:223` - the AST pin recognises only one
access form, so its failure direction is a false pass.**
Status: NOT-VERIFIED-MINOR. Raised by all three lenses; one finding.

`_env_vars_read_by_the_vendored_scripts` collects only `os.environ.get(...)` /
`os.getenv(...)` calls with a string-literal first argument, yet the test it
feeds asserts the scripts read *exactly* three names. `os.environ["NAME"]`,
`os.environ.setdefault(...)`, a bare `getenv("NAME")` after
`from os import getenv`, and any non-literal key are all invisible to it, while
the helper docstring claims it collects "Every literal name the scripts pull out
of the environment". The pin exists to catch drift at the next re-vendor -
exactly the moment upstream could change access style - so a re-vendored
`paginate.py` reading a fourth variable by subscript would leave
`skills/find-sources/SKILL.md:11` ("no bundled credentials, though `paginate.py`
reads [three names]") and `:20` (the phantom-keys annotation) asserted-but-false
with a green suite. The one scenario the test guards is the one it can miss.

The false-negative window is theoretical today: all three reads in
`skills/find-sources/scripts/paginate.py` (`:207`, `:210`, `:240`) are literal
`os.environ.get`, so the shipped set is correct at HEAD - verified.

Fix: also walk `ast.Subscript` nodes whose value unparses to `os.environ`,
accept `ast.Name` funcs named `getenv`, and assert on a non-literal key rather
than skipping it. A cheap belt-and-braces alternative is to cross-check the AST
hit count against a raw-text occurrence count of `environ`/`getenv` across
`SCRIPTS.glob("*.py")` and assert they agree, so any unrecognised form fails
loudly. Two smaller things ride along: line 234's
`ast.unparse(target.value) if isinstance(target, ast.Attribute) else ""` is dead
- once `attr` has matched, `target` is necessarily an `ast.Attribute` - and the
SKILL.md half of the test only asserts `name in skill`
(`tests/test_find_sources_vendor.py:257`), so it cannot tell the corrected
sentence from an incidental mention.

**`skills/find-sources/SKILL.md:70` - the skill mandates running a URL through
`redact_url` but gives no way to run it.**
Status: NOT-VERIFIED-MINOR. Raised by the spec and quality lenses; one finding.

Step 5 says "run a URL through it rather than hand-redacting" and guard 2 at
`:27` says "Run any paginate stderr you intend to quote through `redact_url`
first", but `skills/find-sources/scripts/_common.py` is an import-only library -
confirmed: no `__main__` block, no `argparse`; `redact_url` is defined at `:205`
and imported only by `paginate.py`. Every other script the skill names comes with
an invocation. Here the reader is pointed at a function with no recipe, in the
same edit that removes the hand-redaction list it could otherwise have applied,
so the likely improvisation is pasting the raw URL - exactly the leak the
sentence exists to prevent.

Honest scope: deferring to `redact_url` as the authority is the C-3 card's
decided fix and the brief mandates it, the pointer does deliver the card's
remedy, and the gap is partly inherited (the old sentence also said "anything you
don't run through it" with no recipe). What is missing is only the clause that
makes it runnable. Fix: ship the one-line invocation beside the pointer
(`python3 -c 'import sys; sys.path.insert(0, "SKILL_DIR/scripts"); from _common
import redact_url; print(redact_url("URL"))'`), or point URL redaction at the
path that already prints a redacted URL (`paginate.py --dry-run`, and the
provenance list).

**`skills/find-sources/SKILL.md:29` - the vocabulary paragraph was absorbed into
the vendoring-notes section.**
Status: NOT-VERIFIED-MINOR.

The new `## Vendoring notes` H2 was inserted above the document's placeholder
paragraph, so "In every command below, `PATH` is the vault, `NAME` is the project
under `projects/`, and `SKILL_DIR` is this skill's own directory..." now reads as
the closing paragraph of an errata section rather than as front matter for the
whole skill. That paragraph defines the placeholders every command in the file
uses. An agent that skips the corrections section - they are corrections to read
beside `references/`, not workflow - loses the definition of `SKILL_DIR`, the one
it needs to resolve script paths. Fix: move the heading and its bullets below the
"In every command below..." paragraph. Both internal cross-references still hold -
the routing table stays "below" the notes and step 2 still reads them as
"above".

**`skills/find-sources/SKILL.md:15` - "line numbers hold until the next
re-vendor" is asserted with nothing pinning it, and the stated reason for not
pinning does not hold.**
Status: NOT-VERIFIED-MINOR.

The section makes that claim for fifteen line references into frozen vendored
files, and nothing in `tests/` pins any of them. Seven of the cross-read's own
references had already rotted before this commit - direct evidence of the failure
mode the prose claims immunity from. The report's reason for adding no pin, that
it "would need a copy of upstream to diff against, which the repo does not
vendor" (`task-4-report.md:97`), is not right: asserting that a quoted substring
appears at the cited line of the *in-tree* frozen file is self-contained and
would fail loudly at re-vendor, which is exactly when these notes must be
re-checked. Severity stays Minor because the files are genuinely frozen by their
"Do not hand-edit" headers and the existing provenance-header test, so drift
requires a deliberate re-vendor commit. Fix: a table-driven test in
`tests/test_find_sources_vendor.py` mapping each cited (file, line, expected
substring) triple and asserting the substring is present at that line.

**`skills/find-sources/SKILL.md:19` - "The counts in this file are the current
ones" has an ambiguous referent.**
Status: NOT-VERIFIED-MINOR.

The bullet's subject is `scripts/paginate.py:8` and the preceding clause
discusses that script's own registry, so "this file" can be read as paginate.py -
the file whose counts the bullet has just declared stale. The sentence's job is
to say SKILL.md governs and the vendored docstring does not, and the ambiguity
can invert that for an agent reading the bullet in isolation, which is the exact
reading mode this section is written for. The misreading is self-defeating on a
second pass, which is why this stays a nit. Fix: name the file - "The counts in
SKILL.md are the current ones", or "The counts above (11 references, 5 walkers)
are the current ones".

## Refuted During Verification

None. No lens finding was refuted, and nothing was dropped in synthesis. Three
deduplications were made and are recorded above rather than discarded: the AST-pin
weakness was raised by all three lenses at
`tests/test_find_sources_vendor.py:223`/`:225` and is carried once; the
`redact_url`-has-no-entry-point gap was raised by the spec lens at
`skills/find-sources/SKILL.md:58` and the quality lens at `:70` and is carried
once, anchored at `:70`; and the spec lens's two additional unledgered departures
are folded into the Important finding's discussion, where they are assessed as
defensible editorial additions rather than raised as separate defects.

One severity was corrected: the ledger finding was Important in the fidelity lens
and Minor in the spec lens, and Important is kept.

One cannot-verify item was resolved inside the review rather than passed to the
controller: the quality lens could not check fidelity of the six annotations to
the triage's itemized content, but the spec lens did check it bullet-by-bullet
and found it one-to-one.

## Assessment

**Task quality: Needs fixes.**

The shipped prose and the shipped test are sound - every line reference was
re-derived against the tree, every guard's mechanics were re-derived from
`paginate.py` rather than trusted, the `references/` precedence call is correct,
and the self-review caught two real regressions before reporting. The single
blocking item is record-only and needs no change to `skills/find-sources/SKILL.md`
or the test: amend the commit body's deviation ledger from six entries to seven,
and correct the report's false "Correct as cited" claim about
`references/biorxiv.md:142-145`. It blocks because a commit body cannot be
amended after merge, so deferring it means the audit trail stays wrong
permanently. The five Minor findings are deferrable.
