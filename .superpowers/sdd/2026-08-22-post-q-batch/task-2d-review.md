# Task 2d review - c8cac73..c418cf7

## Spec Compliance

**Verdict: compliant.**

Every step of the brief landed, and the three lenses verified the load-bearing
claims against the real tools rather than against documentation:

- **Step 1** — the vault now ships `.prettierignore`, `.markdownlintignore` and
  `.editorconfig` covering the four surfaces the brief names (`literatures/`,
  `log/`, `inbox/review-queue.md`, `system/bibliography.json`). Two lenses
  independently staged the shipped templates into a fake vault and confirmed
  prettier 3.9.6 reports `ignored:true` for all four (including nested
  `log/2026/deep.md`), markdownlint-cli 0.49.1 auto-reads `.markdownlintignore`
  and lints only the uncovered files, and both reference EditorConfig cores
  (editorconfig-core-py 0.17.1 and the npm core that VS Code uses) return
  `insert_final_newline=false` / `trim_trailing_whitespace=false` for files
  directly inside `literatures/` and `log/`. The AGENTS.md formatter paragraph
  shrank to the one line the brief asked for
  (`research_vault/templates/vault/AGENTS.md:28`).
- **Step 2** — `grep -L disable-model-invocation skills/*/SKILL.md` returns
  exactly `evidence-conventions` and `synthesis-conventions` out of nine skills,
  so "the two model-invocable research-vault skills" at
  `research_vault/templates/vault/AGENTS.md:10` is literally true, and the
  seven rows in the table below it are exactly the gated set. `skills/` does not
  appear in the changed-file list at all, so the "do not flip any
  `disable-model-invocation` flag" prohibition is intact.
- **Step 3** — pins moved in the same commit as the prose they pin
  (`tests/test_templates.py` byte-equality string and `EXPECTED_PATHS`,
  `tests/test_scaffold.py` `EXPECTED_CREATED`), one commit, exact required
  subject.

The one Important finding below is a **gap in the brief's own four-surface
scope**, not a deviation from it: the brief enumerates exactly the four surfaces
that shipped, so the implementer complied. It is marked `planMandated` for that
reason, and it is why this verdict stays `compliant` while the quality verdict
does not.

### Cannot verify from diff

None. All three lenses returned empty `cannotVerify` lists, and each anchored
its central claims empirically.

## Strengths

- The riskiest unknown in the task — does EditorConfig's `dir/**` match files
  *directly inside* `dir`, or only in subdirectories? — was answered yes against
  both reference cores, on the shipped file, with the four mandated surfaces
  matching and `projects/notes.md`, `index.md` and `log.md` correctly matching
  nothing. No over-match, no under-match.
- The `false`-not-`unset` judgment is right and spec-backed. The spec's own gloss
  on `unset` is "(and use editor defaults)", which is precisely the threat, so
  `false` as an active override is the correct primitive. This distinction is
  subtle and easy to get wrong.
- Dropping `charset`/`end_of_line` rather than keeping them as inert `unset`
  lines is correct, and the residual gap the header comment declares is honestly
  scoped rather than overstated.
- The dotless packaging pattern is correct and complete.
  `_DOTLESS_TEMPLATE_RENAMES` (`research_vault/scaffold.py:64`) extends the
  existing single-file rename without changing its semantics, keeps the
  fallthrough explicit via `.get(relative, relative)`, and states the packaging
  constraint that forces dotless naming instead of narrating mechanics. A real
  wheel build and a live `scaffold_vault()` run confirmed all three assets
  package and land renamed.
- `EXPECTED_CREATED` is genuinely correct rather than merely green:
  `tests/test_scaffold.py:75` compares against `sorted(created)` as an ordered
  list, and the three insertions sit in true byte-sort position. The three files
  therefore fall into `TRACKABLE_CREATED` and are committed by the scaffolded
  vault's own first commit — pinned behaviour, not an accident.
- `assert "[*]" not in editorconfig.splitlines()`
  (`tests/test_templates.py:336`) is line-exact, so it cannot be satisfied by
  prose or a substring. It correctly pins the author's round-1 ruling that the
  file makes no claim about files it does not own.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

#### 1. `projects/*/search-log.md` is lint-protected but uncovered by all three ignore files

`research_vault/templates/vault/prettierignore:6` (identically
`markdownlintignore:6`, `editorconfig:37`, claim at `AGENTS.md:28`) —
**status: CONFIRMED, plan-mandated.**

**What is wrong.** `research_vault/lints.py:110-116` (`_is_append_only_path`,
docstring: "The three durable-append surfaces this lint protects") protects
`inbox/review-queue.md`, `log/`, **and** `projects/*/search-log.md`. The three
shipped ignore files cover the first two and omit the third, while
`AGENTS.md:28` now says the three files "keep them off the machine surfaces".

**Why it matters.** `search-log.md` is CLI-written by construction
(`research_vault/__main__.py:689`: "`find-sources` never hand-writes
`projects/<name>/search-log.md` — every line, of either kind, is this verb") and
prefix-enforced (`research_vault/lints.py:143`, `not
new_bytes.startswith(old_bytes)` → "drift — append-only file rewrote history").
Both the quality and fidelity lenses reproduced the failure end to end: with the
scaffold-installed `.prettierignore`/`.editorconfig` in place, prettier 3.9.6
run from the vault root rewrites a realistic `projects/alpha/search-log.md`
(a blank line inserted after the frontmatter), and `lint_append_only` — wired
unconditionally into every verify run at `research_vault/verify.py:1008` —
raises the drift outcome. This is the exact scenario the shrunken AGENTS.md line
tells the reader is now handled.

**Blast radius, stated precisely** (both lens verifications were partly right,
and neither said this outright): the `append-only` check is **not** in
`CLOSING_BY_SURFACE` for either the `commit` or the `publish` surface
(`research_vault/verify.py:53-59`, which closes on `citekey` and
`evidence-layer` only), so the drift outcome surfaces as a finding in the verify
report rather than failing the pre-commit hook. The PRISMA-S records still parse
(`searchlog.load()` skips blank lines), the pristine bytes remain at the lint's
own git base, and the finding clears once the reformatted file is committed. So
this is a recoverable false-positive drift finding plus a foreign writer's edit
to a provenance file, not permanent corruption. That is what keeps it Important
rather than Critical — and the recoverability does not make it Minor, because
Minor means deferred, and deferring means shipping an enforcement artifact with
a hole in exactly the file class it enforces.

**Two softeners worth recording, neither of which retires the finding.** First,
`AGENTS.md:28`'s "the machine surfaces" is anaphoric: the nearest antecedent is
line 26's list (`log/`, `inbox/review-queue.md`, managed regions,
`system/bibliography.json`), which does not name `search-log.md`, so the
sentence is arguably true as written rather than a third false enforcement
claim. Second, the brief scoped the ignore files to exactly four surfaces, so
this is a scope question for the author, not an implementer error.

**Closing out the `log.md` sub-claim (fidelity lens): not a defect.** `log.md`
is named machine-written at `AGENTS.md:6` and is also uncovered, but it does not
appear in `_is_append_only_path` and I found no other lint keyed to it, and
`research_vault/okf.py:37-38` rewrites it wholesale with `write_text`. A
formatter touch is therefore overwritten on the next regeneration and alarms on
nothing. It is also entangled with the known-deferred line-6 / line-26
divergence. No action.

**How to fix.** Either (a) add `projects/*/search-log.md` to `prettierignore`
and `markdownlintignore` and a `[projects/**/search-log.md]` section carrying
the two `= false` properties to `editorconfig` — both syntaxes express this
exactly, verified — extending `_MACHINE_SURFACES` in
`tests/test_templates.py:309` in the same commit so the
`len(_MACHINE_SURFACES) * 2` count assertion self-adjusts; or (b) narrow the
`AGENTS.md:28` sentence to name the surfaces actually covered. Option (a) makes
the sentence true rather than smaller and is four lines of config. Because the
four-surface list came from the brief, this needs an author scope ruling before
it is applied.

**One bound on the claim worth carrying forward regardless** (measured by the
fidelity lens, not itself a defect in this diff): prettier's and markdownlint's
ignore files are cwd-scoped, not hierarchical like `.gitignore`. Running either
tool from a *parent* of the vault reformats every machine surface. Nothing in
this task can fix that; it is a property of the tools.

### Minor (Nice to Have)

#### 2. `literatures/` and `log/` are unanchored, so the three files disagree about scope

`research_vault/templates/vault/prettierignore:3-4` (identically
`markdownlintignore:3-4`) — **status: NOT-VERIFIED-MINOR.**

Both entries are unanchored gitignore patterns, so they exclude any directory
with those names at any depth, not just the two vault-root machine surfaces.
Demonstrated with the shipped files: prettier 3.9.6 reports `{"ignored":true}`
for `projects/thesis/log/notes.md` and markdownlint-cli 0.49.1 skips it, while
`.editorconfig`'s `[log/**]` — which contains a `/` and is therefore anchored to
the `.editorconfig` file's directory — correctly applies nothing to it. The
three files thus cover different sets, and a user's own project log notes go
silently unformatted. This is the same principle the author invoked in round 1
when ruling `[*]` out of `.editorconfig`: research-vault does not impose on files
it does not own. Fix: write `/literatures/` and `/log/` in both ignore files.
`inbox/review-queue.md` and `system/bibliography.json` already contain a `/` and
are anchored.

#### 3. `test_formatter_ignores_cover_every_machine_surface` can pass on a broken file

`tests/test_templates.py:317-343` — **status: NOT-VERIFIED-MINOR.** All three
lenses raised this; merged here with the union of their sub-points.

This test is the only guard on the three files' content — the whole-file
byte-equality pins do not cover them — and it exists because the brief's own
risk framing is that wrong syntax makes the files silently do nothing. Four ways
it can be green on a broken file:

- **Substring surface check** (`assert surface in text`, line 323): `#
  literatures/` and `!literatures/` both pass, and the second one *un*-ignores
  the directory.
- **`assert "root = true" in editorconfig`** (line 335) is satisfied by the
  header comment alone — `root = true` appears as prose at `editorconfig:10` and
  `:16` — so deleting the real directive at `editorconfig:21` leaves the test
  green.
- **Aggregate `count("= false") == len(_MACHINE_SURFACES) * 2`** (line 343):
  duplicating both properties inside `[literatures/**]` while leaving
  `[system/bibliography.json]` empty passes every assertion in the test.
- **Negative assertions scan the comment block too** (`"= unset"`, `"charset ="`,
  `"end_of_line ="`, lines 340-342): a future header comment that quotes
  `charset = utf-8` as an example fails the test with no behaviour change. Note
  the interaction with findings 5 and 6 — any reword of that header risks
  tripping these, which is itself an argument for the fix.

Fix: assert on line-exact, non-comment content throughout, the way line 336
already does correctly for `[*]`. Build `patterns = [ln.strip() for ln in
text.splitlines() if ln.strip() and not ln.startswith("#")]` and assert
`set(_MACHINE_SURFACES) <= set(patterns)`; assert `"root = true" in
editorconfig.splitlines()`; and assert per-section that both properties follow
each of the four section headers instead of counting file-wide.

#### 4. `AGENTS.md:28` credits `.editorconfig` with an ignore capability it does not have

`research_vault/templates/vault/AGENTS.md:28` — **status:
NOT-VERIFIED-MINOR.**

The one-liner says all three files "keep them off the machine surfaces", but
EditorConfig has no ignore or exclude primitive at all: it only turns off two
save-time behaviours, and the file's own header declares a residual
charset/end_of_line gap. The claim is materially true rather than false — the
two ignore files verifiably make prettier and markdownlint skip the four
surfaces, and the two `false` overrides block exactly the mutations that break
the byte contracts — so this is wording imprecision, not a third false
enforcement claim. It earns a mention only because this template has already
shipped two false enforcement claims. Weigh the cost before acting: any reword
churns the whole-file byte-equality pin that took two author rulings to
stabilise. If finding 1 is fixed with option (a) or (b), that reword touches the
same pinned sentence and both can be settled in one pin churn. A candidate
phrasing: "`.prettierignore` and `.markdownlintignore` keep them off the machine
surfaces; `.editorconfig` stops editors trimming or newline-padding them."

#### 5. The `.editorconfig` header narrative is duplicated in the test comment

`research_vault/templates/vault/editorconfig:1-20` and
`tests/test_templates.py:325-333` — **status: NOT-VERIFIED-MINOR.**

Twenty lines of header comment precede twelve lines of config, and the
`unset`-is-inert rationale is restated near-verbatim in the test comment. Two
copies of the same rejected-alternative argument will drift independently: the
next change to either file leaves the other asserting stale reasoning. The
load-bearing constraints (`false` beats a user's global editor setting;
charset/end_of_line have no boolean off) survive in a few lines; the narrative
about `unset` having been considered and dropped is review history and belongs
in the commit body, which already carries it. Fix: keep the two constraint
sentences in the header, shorten the test comment to point at the config file.

#### 6. The `root = true` rationale states a mechanism the measurement contradicts

`research_vault/templates/vault/editorconfig:10-12` — **status:
NOT-VERIFIED-MINOR.**

The header says `root = true` means "these overrides cannot be diluted by
[an ancestor]". Measured with editorconfig-core-py 0.17.1 against this exact
file nested under an ancestor `.editorconfig` carrying `[*]
insert_final_newline = true / trim_trailing_whitespace = true / charset =
utf-16le`: **with** `root = true` the result for `vault/literatures/x.md` is the
two `false` values; **without** it, the same two `false` values plus `charset:
utf-16le`. So the two overrides were never dilutable — closer-file precedence
already guarantees that, which incidentally resolves the implementer's disclosed
"unverified belief" (report §9) in its favour. What `root = true` actually
blocks is ancestor-sourced properties this file does not set, i.e. exactly the
charset/end_of_line residual gap the comment declares eight lines later. Keeping
the line is right, for a stronger reason than the comment gives. Fix, if the
header is touched for finding 5 anyway: "`root = true` stops the ancestor
search, so an `.editorconfig` above the vault cannot inject charset/end_of_line
onto these four surfaces; the `false` overrides above would win on closeness
regardless."

#### 7. Two provenance statements in the commit body are inaccurate

Commit `c418cf7` message body (no source line; anchored at
`research_vault/templates/vault/markdownlintignore`) — **status: CONFIRMED.**

The body cites the brief as
`docs/superpowers/sdd/2026-08-22-post-q-batch/task-2d-brief.md`, a path that
exists neither in the worktree nor on `origin/main`. I re-verified this myself:
`git ls-tree --name-only origin/main -- docs/superpowers/` returns only `plans`
and `specs`. The real artifacts are
`docs/superpowers/plans/2026-08-22-post-q-batch.md` (tracked) and
`.superpowers/sdd/2026-08-22-post-q-batch/task-2d-brief.md` (local, gitignored)
— and the same body cites the report correctly with the `.superpowers/` prefix.
Separately, the body calls `igorshubovych/markdownlint-cli` a "maintained fork;
DavidAnson's README 404'd", which inverts the relationship:
`igorshubovych/markdownlint-cli` *is* the canonical markdownlint-cli, while
DavidAnson maintains `markdownlint` (the library) and `markdownlint-cli2`, and
no `DavidAnson/markdownlint-cli` exists — which is why the URL 404'd. The
substantive claim the citation supports is nonetheless correct and was confirmed
against markdownlint-cli 0.49.1 directly, so nothing about the shipped file
changes. Because the global constraint puts provenance in the commit body, that
body is the durable record and a pointer resolving nowhere sends the next reader
hunting. Not worth an amend on its own; fold it in if anything else on this
branch forces a reword.

## Refuted During Verification

None. All ten raw lens findings survived adversarial verification; the seven
above are those ten after cross-lens deduplication (the `search-log.md` gap was
raised by two lenses, and the weak-test-assertion finding by all three). One
sub-claim inside finding 1 — that root `log.md` is a comparable uncovered
surface — is closed above as a non-defect, with the evidence recorded there so
it is not re-derived later.

Two severity notes, since verification pulled in opposite directions on the same
finding. The quality lens's verifier called finding 1's severity inflated
because the consequence claim ("permanently corrupted PRISMA-S provenance")
collapses under test; the fidelity lens's verifier called it confirmed
end-to-end because the lint demonstrably fires. Both are right about what they
measured. The finding stays Important on the artifact-integrity argument — an
enforcement file with a hole in the class of file it enforces — with the
consequence restated accurately (a non-blocking, recoverable drift finding)
rather than inherited from either lens.

## Assessment

**Task quality: Needs fixes.**

The work is careful and unusually well evidenced — every syntax assumption was
checked against the real tool rather than its documentation, the round-1 `[*]`
ruling was applied with its reasoning rebuilt rather than carried over, and the
pins moved with the prose they pin. One Important gap blocks: the shipped ignore
files cover four surfaces while the trust machinery alarms on five, so the
enforcement this task exists to deliver has a hole in `projects/*/search-log.md`
— a four-line fix, but a plan-scope question that needs the author's ruling
because the brief named exactly the four surfaces that shipped.
