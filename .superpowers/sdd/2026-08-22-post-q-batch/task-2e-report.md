# Task 2e report: form-gate coherence

## 1. Step 2, re-proven from scratch (not taken on the controller's word)

Extracted a clean copy of the tree via `git archive HEAD | tar -x` (never `cp
-r`, per the environment constraint) and ran the pinned mdformat
(`--number --wrap keep --check`) over each of the 10 markdown files under
`knowledge_harness/templates/vault/` individually:

| file | mdformat --check |
|---|---|
| `AGENTS.md` | **changes** — 1 blank line added after frontmatter close |
| `inbox/review-queue.md` | no change |
| `index.md` | **changes** — every wikilink and Base embed escaped |
| `log.md` | no change |
| `synthesis/index.md` | no change |
| `system/glossary.md` | **changes** — 1 blank line added after frontmatter close |
| `system/templates/daily.md` | **changes** — 1 blank line added after frontmatter close |
| `system/templates/literature.md` | **changes** — 3 blank lines added around `%%hk-managed%%`/`%%/hk-managed%%` |
| `system/templates/project.md` | no change |
| `system/templates/synthesis.md` | no change |

Five change, confirming the brief's number. `index.md`'s diff, applied and
inspected then discarded:

```
-- [[literatures/]] — evidence layer: citekey-keyed literature notes
+- \[[literatures/]\] — evidence layer: citekey-keyed literature notes
...
-![[system/bases/trust-tier.base]]
+!\[[system/bases/trust-tier.base]\]
```

All six folder wikilinks and both Base embeds escaped — exactly the brief's
claim, confirmed on this run rather than assumed. The 11-vs-10 file count in
the brief's own Step 2 text does not match what is on disk: `find
knowledge_harness/templates/vault -name '*.md'` returns 10, not 11. This is
a brief erratum, not a defect in the tree — the "five change" figure it
depends on is independently verified correct either way. Flagged in
Concerns rather than silently corrected in the brief.

## 2. Step 2 implementation: gate four, exclude one, by ownership not by name

`.pre-commit-config.yaml`'s mdformat hook gained five explicit vault paths
(`vault/AGENTS.md`, `vault/inbox`, `vault/log.md`, `vault/synthesis`,
`vault/system`) rather than the whole `knowledge_harness/templates/vault`
directory — mdformat 1.0.0 has no `--exclude`/ignore-file mechanism (checked
`mdformat --help`; only positional `paths`), so excluding one file inside an
otherwise-gated tree requires naming the rest individually. `vault/index.md`
is the only markdown file anywhere under the vault carrying `[[` (checked
`grep -rl '\[\['`), so it is the only one that needed excluding.

The comment above the hook states the criterion verbatim, per the author's
2026-08-24 ruling: *"Vault-dialect templates (wikilinks, managed-region
markers, Base embeds) belong to their sole writer, not the CommonMark
owner"* — framed as an ownership boundary, not a filename exception, so a
future dialect-bearing template excludes itself by the same rule.

Applied mdformat to the four safe files in the real tree; the diff matched
the dry run exactly (verified via `git diff`, not assumed from the
scratch-tree run). Re-ran `mdformat --check` over the hook's full exact
path list afterward: exit 0, zero files needing changes — the gated set is
canonical.

## 3. Pins moved with the bytes, same commit

`tests/test_templates.py`'s `test_markdown_templates_match_canonical_content`
carries whole-file byte-exact expected strings for `AGENTS.md`,
`system/glossary.md`, `system/templates/daily.md`, and
`system/templates/literature.md`. Updated all four to include the new blank
line(s) mdformat added. Verified byte-exact, not just "tests pass": executed
the test function directly against the real files via `importlib`, then
confirmed with `pytest tests/test_templates.py -q` (8 passed).

`tests/test_config_validity.py`'s `_MDFORMAT_ROOTS` — the constant a
comment already claimed mirrors `.pre-commit-config.yaml`'s mdformat hook,
with nothing checking that claim (the 2026-08-24 audit's own finding) —
gained the same five vault paths. This is what accounts for 9 of the test
count delta: the table-truncation sweep (`_mdformat_owned_markdown()`)
picked up the 9 newly-gated vault markdown files (`AGENTS.md`,
`review-queue.md`, `log.md`, `synthesis/index.md`, plus 5 under `system/`).

## 4. Judgment call: added the mirror-accuracy assertion

The brief left "whether to also add an assertion that the constant matches
the hook's actual path list" as a judgment call, naming it as squarely this
task's subject without mandating it. **Decision: added it**
(`test_mdformat_roots_mirror_the_hook_the_seam_actually_runs`), because
leaving it unasserted after this task is exactly the defect class the task
exists to close — a comment claiming a mirror, unchecked, is what let
`_MDFORMAT_ROOTS` under-cover the vault files in the first place. The test
parses `.pre-commit-config.yaml`'s actual `entry: bash -c '...'` string via
regex, tokenizes it, strips the two known mdformat flags (`--number`,
`--wrap keep`), and asserts the remaining tokens as a set equal
`_MDFORMAT_ROOTS`. It does not depend on mdformat's private `_cli` module
(considered and rejected — leading-underscore internals, not a public API,
and a heavier dependency than the small hand-rolled flag-skip it replaces).

## 5. Step 1: vendor exclusion — comment added; the queue note already existed

`skills/find-sources/scripts/*.py` was already outside ruff's path list
(`knowledge_harness tests scripts hooks` never names `skills`) — confirmed
by reading `.pre-commit-config.yaml` directly, not inferred. Added one
comment above `ruff-format`/`ruff-check` stating the exclusion and its
reason (frozen vendored fork, re-vendor to update).

The brief's second Step 1 deliverable — "the real finding there
(`jats_to_text.py:291` passing `Element | None` into `collect_sections`)
goes to the vendor channel: a ready-to-file upstream note in the K-Dense
report queue" — was checked before writing anything new, per the
advisor-flagged risk of duplicating an existing note. Confirmed both parts
of the claim:

- **The finding is real.** `skills/find-sources/scripts/jats_to_text.py:134`
  types `collect_sections(body: ET.Element)`. `body = article.find("body")`
  (line 263) returns `Element | None`. The `if body is None:` guard above
  it calls `fail(...)` (from `_common.py:223`), typed `-> None`, not
  `NoReturn`, even though it always raises `SystemExit` — so a type checker
  cannot narrow `body` past that guard, and `collect_sections(body)` at
  line 290/291 is a genuine (if currently unenforced) type mismatch.
- **The queue note already exists**, filed by a prior commit already an
  ancestor of this branch's `HEAD`: `git merge-base --is-ancestor ebea360
  HEAD` confirms it. `skills/find-sources/SKILL.md:23` reads "...kept
  frozen per the vendor rule, noted in the K-Dense upstream queue beside
  the jats arg-type finding," and `ebea360`'s own commit message states
  "The K-Dense upstream queue now carries two findings — this one and the
  jats_to_text.py:291 arg-type defect — both landing at the next
  re-vendor."

No new note was filed; filing a second one would have duplicated an
existing record. Nothing under `skills/find-sources/scripts/` or
`skills/find-sources/references/` was touched, per the global constraint.

## 6. Step 3: header sentence corrected

"The ONE command for every form/lint check, locally and in CI" →
"...when typed, and in CI", with one added line naming the replacement
practice: run the form owner directly on touched files before committing —
`pre-commit run` also stashes and is not the safe form in a shared
checkout. No test in the suite asserts the header's exact text (checked via
grep before editing), so this was a free edit.

## 7. Step 4: four small truths

- **yamlfix self-exclusion documented.** Ran yamlfix over a scratch copy of
  `.pre-commit-config.yaml` (git-archived, not `cp -r`) to get real
  evidence rather than assert from memory: it rewrites every double-quoted
  `name:` string to single-quoted, inserts a `---` document marker, and
  rewraps the long hand-wrapped entries (`mdformat`'s and
  `pyproject-fmt`'s) differently — confirming the "readability of the
  hand-wrapped entries" reason the brief gives. One comment added above
  the `yamlfix` hook.
- **Dead `analysis` pathspec dropped**, both from the `git diff` argument
  list and from the hook's own `name:` field (`"records: append-only under
  research/analysis/adr"` → `"records: append-only under research/adr"`).
  Confirmed `analysis/` does not exist anywhere in the tree (`ls analysis`
  → No such file or directory) before removing it, and confirmed no test
  hardcodes either string (grepped `tests/*.py` and `.pre-commit-config.yaml`
  for "analysis" — only unrelated hits in `test_project_flow_skill.py`
  prose and one unrelated `test_config_validity.py` comment about
  `research/`/`analysis/` JSON, addressed in Concerns, not fixed here —
  see below). The `name:` field was in scope by extension: leaving it
  saying "analysis" after removing it from the actual check would recreate
  the exact defect this task exists to close.
- **Hook now fails loud on a `git diff` error.** Proved the *before* state
  first, against the exact command pre-commit would run — extracted via
  `yaml.safe_load` + `shlex.split` from the real file, not hand-typed (a
  hand-typed reproduction earlier in this task silently broke across
  newlines and gave a false read; caught and discarded before it was used
  as evidence). Built a `git` shim in `/tmp/fake-git-bin` that fails only
  on `diff` (exit 128, stderr message) and passes everything else through
  to the real `/usr/bin/git`. With `PATH` prefixed by the shim:
  - **Before the fix:** the shim's `fatal:` message printed, and the hook
    still exited 0 — `touched=$(git diff ...)` only captures stdout (empty,
    since the failure went to stderr), and nothing checked the substituted
    command's own exit status, so `[ -z "$touched" ]` was true and the
    error was swallowed.
  - **After the fix** (`touched=$(...) || { echo ...; exit 1; }`): same
    induced failure now exits 1, with an explicit message
    ("git diff failed while checking record immutability").
  - **Sanity check, real git, both before and after:** exit 0, nothing to
    report (this branch carries no modification/rename/deletion under
    `research`/`docs/adr` relative to `origin/main`).
  Re-ran all four of the above against the *shipped* `.pre-commit-config.yaml`
  after editing it (not just the draft), per the requirement to prove the
  fix against the artifact that actually ships.
- **mdformat upgrade-protocol comment added** on its pin in `pyproject.toml`
  (next to `"mdformat==1.0.0"`, below the existing RENDER-CONTRACT comment),
  matching ruff's protocol comment in shape. Content: a canonical-form-
  changing mdformat upgrade would rewrite files under `docs/adr` — one of
  record-immutability's two append-only roots (`research`, `docs/adr`) —
  so it cannot land through the normal commit-time gate; it lands as its
  own churn commit through the bypass channel (`git commit --no-verify`),
  with the commit message itself as the record (the blame-ignore-revs
  provenance — measured useless, deleted 2026-08-24 — was kept out of the
  comment itself and put in the Step 1/3/4 commit's body instead, per
  comment hygiene: a comment states a constraint, not history). The
  comment names all three `%%`-bearing vault templates — `AGENTS.md`,
  `system/glossary.md`, `system/templates/literature.md` — not just
  `literature.md`, correcting the brief's narrower framing. Verified all
  three carry `%%` (`grep -rln '%%' knowledge_harness/templates/vault/`)
  and that mdformat leaves the marker text itself untouched today (only
  adding blank lines around it — see Step 2's diffs above), before writing
  the claim.

## 8. Suite and gate evidence

- Full offline suite after Step 2's commit: **1714 passed, 7 skipped**
  (baseline 1704/7 + 9 new table-truncation parametrizations over the
  newly-gated vault files + 1 new mirror test — computed in advance,
  matched exactly).
- Full offline suite after Steps 1/3/4 (comment/config-only, no new test
  surface): **1714 passed, 7 skipped**, unchanged.
- `ruff check knowledge_harness tests scripts hooks`: all checks passed.
- `ruff format --check knowledge_harness tests scripts hooks`: 75 files
  already formatted.
- `mypy knowledge_harness`: no issues, 27 source files.
- `pyproject-fmt --keep-full-version --no-generate-python-version-classifiers
  --table-format long pyproject.toml`: no change (comments sit correctly
  above the settings they rule, both the pre-existing ones and the new
  upgrade-protocol comment).
- `echo '{}' | python hooks/stop_publish_gate.py`: exit 0.
- `pre-commit run --all-files`: all 8 non-manual hooks passed (ruff-format,
  ruff-check, mypy, mdformat, yamlfix, pyproject-fmt, config-validity,
  record-immutability). Zero files modified by the run.

### Fact #5 compliance (stash-safety, shared checkout)

`.superpowers/sdd/2026-08-22-post-q-batch/progress.md` (the controller's
file, not mine — explicitly excluded from every commit here) was
uncommitted and unstaged for the entire task, which would have made
`git status --porcelain` non-empty for the whole session. Rather than let
`pre-commit run --all-files` stash it (onto a stash stack shared across
every worktree of this repo — the exact hazard fact #5 names), I:

1. Recorded its checksum (`sha256sum`) and a copy in `/tmp` before touching
   anything.
2. `git checkout --` it, bringing the tree to a genuinely clean
   `git status --porcelain` (confirmed empty) — the literal condition fact
   #5 requires, achieved without invoking `git stash` at all (a manual
   stash would recreate the exact shared-stack hazard it warns about).
3. Ran `pre-commit run --all-files` on the clean tree (green, see above)
   and confirmed `git status --porcelain` and `git stash list` were both
   still empty immediately after — no stash was created or left behind.
4. Before restoring, ran `git diff --quiet` against the checked-out file to
   confirm nothing else had written to it during the run (nothing had —
   this worktree is not shared with a concurrently-running session in this
   task).
5. Copied the parked file back and verified the checksum matched exactly,
   and that `git diff --stat` showed the identical 49-line insertion
   present at the start of the task. Not committed, per the explicit
   constraint.

## 9. Commits

- `5c640d5` — `fix: mdformat gates knowledge_harness/templates/vault
  (render-contract event)` — Step 2 alone: hook path list + dialect-
  ownership comment, the four canonicalized template files, the
  `test_templates.py` pins, and the `_MDFORMAT_ROOTS` mirror + new mirror
  test.
- `212d135` — `fix: form gates match their own claims — explicit vendor
  exclusion, templates canonicalized, hook truths` (brief's exact message)
  — Steps 1, 3, 4: the ruff vendor-exclusion comment, the corrected header,
  the yamlfix self-exclusion comment, the record-immutability fixes (dead
  pathspec dropped, fail-loud on git errors), and the mdformat
  upgrade-protocol comment.
- This report, added with `git add -f` (it lives under `.superpowers/`,
  root-`.gitignore`'d by policy, with a nested `.superpowers/sdd/.gitignore`
  containing `*` as the SDD tooling's own re-created implementation detail
  — both are the versioned decision to ignore future `.superpowers/`
  content, not something this report's presence should fight; `-f` is the
  documented way past a deliberately-ignored path, consistent with how the
  ~60 already-tracked files under this same directory are grandfathered).

## 10. Concerns

- **Brief erratum: "11 template files."** `find
  knowledge_harness/templates/vault -name '*.md'` returns 10, not 11, both
  before and after this task's changes (verified via `git archive`
  scratch trees at two points in the task). The "five change" figure the
  brief's Step 2 depends on is independently correct regardless of this
  count. → controller, for the plan record.
- **`test_config_validity.py:32`** carries a comment — "`research/` and
  `analysis/` JSON are immutable records (AGENTS.md history rule)" —
  citing an `analysis/` directory that does not exist in this tree, the
  same defect class as the record-immutability hook's dead pathspec this
  task fixed. Left untouched: it is a different location
  (`JSON_MANIFESTS`'s scope rationale, not the record-immutability hook)
  and not named in this task's brief. → controller / candidate
  `needs-triage` GitHub issue.
- **mdformat's `skills` root already formats
  `skills/find-sources/references/*.md`** (11 vendored reference files),
  the same vendor-drift class Step 1 makes explicit for the Python side.
  Out of this task's stated boundary ("Step 1 makes the exclusion
  explicit; it does not fix the fork") — the brief scopes Step 1 to ruff
  only. → controller triage, in case the same explicit-exclusion treatment
  is wanted for mdformat's path list too.
- **The loose-prefix-assertion pattern** this plan has repeatedly flagged
  (seven prior instances, once inside the commit that fixed it) has its
  home at GitHub issue #22, not here — no new instance of it was found in
  this task's own work (every assertion added or changed in this task
  either checks an exact set/string or is proven against induced failure,
  per the brief's own standard); noted per the "silence is not a
  disposition" instruction, not because a new instance was found.

## 11. Fix round 1 — dynamic exclusion, vendored markdown absorbed, comment truths corrected

The coordinator's round-1 review: **spec PASS with one material deviation
(HIGH 1), quality PASS with findings (HIGH 2, four MEDIUM, two LOW).**
Upheld without change: the four canonicalized templates (whitespace-only,
ignore-all-space diff empty), `index.md` unescaped and byte-pinned, every
pin moved with its bytes, the swallowed-error fix (both directions), and
the round-1 mirror test (discriminated both ways against the real config).
Addressed below, in the coordinator's order. Commit `17e3ad4`.

### 11.1 HIGH 1 — the "excludes itself by rule" claim made true, not softer

The round-1 comment claimed the vault exclusion pattern would protect
future dialect-bearing templates "by the same rule, not by incident." It
did not: `vault/system` was one of five *directories* in the static
`entry:` path list, so mdformat would sweep in and silently corrupt
(escape wikilinks in) any new `vault/system/newnote.md` — exit 0, no
warning. The opposite drift also existed: a new `vault/rootnote.md`,
outside all five named subpaths, would be silently ungated entirely.
Demonstrated, not asserted — the coordinator constructed both cases before
reporting them.

**Strengthened reality, per the repo's claim-vs-reality doctrine applied
to comments** (weaken the claim or strengthen reality, never soften into
ambiguity — chose to strengthen). The hook's `entry:` now runs:

```
find knowledge_harness/templates/vault -name "*.md" -not -path \
  "knowledge_harness/templates/vault/index.md"
```

Verified the `-not -path` form excludes *only* the top-level `index.md`
and not the nested `synthesis/index.md` (find's `-path` requires an exact
full-string match with no wildcard, so
`knowledge_harness/templates/vault/index.md` cannot also match
`knowledge_harness/templates/vault/synthesis/index.md`): ran both
`find ... -name '*.md'` (10 files) and the same with `-not -path` added (9
files, `synthesis/index.md` present, top-level `index.md` absent).

This closes the "silently ungated" drift completely — every file anywhere
under the vault, present or future, is now in scope unless it is literally
`vault/index.md`. It does **not** provide content-based dialect detection:
a new wikilink-bearing file dropped in elsewhere in the vault is still not
automatically protected. The rewritten comment says this explicitly rather
than implying otherwise — "Both exclusions below are PATH exclusions, not
content detection... name it here explicitly when that happens, the same
way these two are named."

**Correction to my own prior claim, verified before writing anything:** I
stated in round 0 that mdformat 1.0.0 has no `--exclude` mechanism, based
on `mdformat --help`. That was checking the wrong source. Read
`mdformat/_cli.py` directly: the `--exclude` flag exists but `_cli.py`
only calls `parser.add_argument("--exclude", ...)` when
`sys.version_info >= (3, 13)`; the exclusion-application logic
(`is_excluded()`) is likewise gated. Confirmed empirically on this venv
(Python 3.12.3, `python3 --version`):

```
$ .venv/bin/mdformat --exclude "*.md" --check README.md
mdformat: error: unrecognized arguments: --exclude README.md
```

A `.mdformat.toml` `exclude` key produces an explicit error on <3.13
("'exclude' patterns are only available on Python 3.13+"), not silent
inertness. So the `find`-based shape is a **workaround with a known
expiry**, not a permanent tool limit, and the hook's comment records that:
collapse both `find` substitutions to `--exclude` once the floor moves to
3.13+.

### 11.2 HIGH 2 — skills/find-sources/references absorbed into the exclusion

Verified before acting, not taken on the ruling alone: `git show --stat
ce0f1e3` confirms a 2026-08-22 commit (`ce0f1e3`, an ancestor of this
branch's starting point, so not something this task or a concurrent
session did) titled "style: one-time canonical-form churn (mdformat over
docs+skills, ruff format)" — mdformat over `docs/`, `skills/` was already
part of the repo's history before this task began. `gh issue view 24`
confirms the routed restoration ticket is real, OPEN, and states the exact
same finding: eight files inside `skills/find-sources/references/`
(`arxiv.md`, `biorxiv.md`, `core.md`, `crossref.md`, `europepmc.md`,
`medrxiv.md`, `openalex.md`) plus `SKILL.md` were reformatted by that
commit, and `mdformat --check` on the directory exits 0 today — the fork
sits in this repo's canonical form, not upstream's, and the "skills" root
in mdformat's path list was actively keeping it that way.

Ruling accepted: this absorbs into 2e, same reasoning as Step 1's ruff
vendor-exclusion one file type over — not scope creep, a correction. The
hook now excludes `skills/find-sources/references` the same `find -not
-path` way as `vault/index.md`:

```
$(find skills -name "*.md" -not -path "skills/find-sources/references/*")
```

Verified: `find skills -name '*.md'` returns 23; with the exclusion, 12
(the same 12 own-skill `SKILL.md` and `import-source/references/*.md`
files, none from the vendored fork).

**Stated plainly, per the coordinator's explicit instruction: this does
NOT undo `ce0f1e3`'s churn.** The eight reformatted files (plus SKILL.md,
which is not part of the frozen fork and was intentionally left gated)
remain in their reformatted, non-upstream state. Excluding the directory
from mdformat only stops the gate from *keeping* it that way on future
runs; restoring the actual upstream bytes requires a re-vendor, which is
GitHub issue #24's job, not this task's.

### 11.3 MEDIUM — comment truths

- **`.pre-commit-config.yaml`'s self-contradictory "named individually
  below, by omission"** (index.md was not named at all under the old
  static list) is resolved by 11.1's redesign: the comment now describes
  the actual `find`-based mechanism instead of a roster that never
  existed for index.md specifically.
- **`_MDFORMAT_ROOTS`'s "five siblings named individually"** was the same
  HIGH-1-class defect one file over — three of the five were directories
  that silently absorb future files. Redesigned to mirror the hook's
  actual shape: `_MDFORMAT_ROOTS` is now six directory/file roots
  (`README.md`, `AGENTS.md`, `CONTEXT.md`, `docs`, `skills`,
  `knowledge_harness/templates/vault`), with two new tuples,
  `_MDFORMAT_EXCLUDED_FILES` and `_MDFORMAT_EXCLUDED_DIRS`, that
  `_mdformat_owned_markdown()` applies when walking each directory root.
- **`test_canonical_form.py`'s module docstring**, which this task's own
  Step 2 commit made stale ("no formatter speaks it" for vault-dialect
  markdown, when nine of ten static templates are now mdformat-owned).
  Verified the remaining claim empirically before narrowing the docstring
  to it, rather than trusting the original wording: rendered a real
  literature note via `notes.render_note` (with one annotation, so the
  managed region contains an actual list item) and ran the pinned mdformat
  over it. Result: the closing `%%/hk-managed%%` marker gets indented two
  spaces into the preceding list item's CommonMark continuation, and the
  list item's own internal double space (`(paraphrase)  [@smith2020]`)
  collapses to one — both real, content-level changes, distinct from the
  static templates' blank-line-only churn. The docstring now scopes the
  "sole writer" claim to RENDERED content (literature notes with real
  managed-region content) and the one static template that still carries
  real dialect markup (`vault/index.md`), and states which nine templates
  mdformat now owns and why they're safe (placeholder content, no list
  markup or wikilinks to mangle).
- **`tests/test_config_validity.py:32`'s dead `analysis/` reference**
  (round 1's own Concern 2, left unfixed pending this instruction): one
  line, "and `analysis/`" dropped from the JSON_MANIFESTS scope comment.

### 11.4 The mirror test, redesigned around the new mechanism (not patched)

Text-tokenizing a static path list no longer describes what the hook
does — it now runs shell `find` expressions. Rather than parse the new
shell syntax as more text (which would just move the "does the parse
match reality" risk rather than close it), the test now **executes the
hook's own logic**:

1. Parses `.pre-commit-config.yaml` via `yaml.safe_load` — the same
   library `pre-commit==4.6.2` (a hard pin) uses internally to read this
   exact file, not a from-scratch approximation of YAML folding.
2. Looks up the `mdformat` hook by `id`, `shlex.split`s its `entry`.
3. Swaps the fixed `mdformat --number --wrap keep ` prefix for
   `printf "%s\n" ` and runs the resulting string via `bash -c`, cwd the
   repo root — this actually invokes the real `find ... -not -path`
   clauses against the live filesystem.
4. Compares the resolved file set against `_mdformat_owned_markdown()`'s
   independent reimplementation (walk each root, apply the two exclusion
   tuples).

This is strictly stronger than parsing hook text: it cannot be fooled by a
`find` pattern that *parses* correctly but *resolves* to the wrong files.

**Mutation-tested, both directions, plus the new skills exclusion** (the
coordinator credited round 1's version for discriminating both ways; this
redesign is re-verified to keep that property):

1. Hook-only mutation (`vault/index.md` → `vault/WRONG.md` in
   `.pre-commit-config.yaml`): **red** — `hook only: [index.md]`.
2. Mirror-only mutation (`_MDFORMAT_EXCLUDED_FILES` → a wrong path):
   **red** — `mirror only: [index.md]`.
3. Mirror-only mutation (`_MDFORMAT_EXCLUDED_DIRS` → a wrong path):
   **red** — the 11 references files show up as `mirror only`.

All three restored to the original text and re-verified green
individually.

**Two defects in my own first draft of this rewrite, caught by running the
test rather than by inspection, corrected before this commit:**

- The initial regex, `re.search(r"entry: bash -c '(.*)'", entry,
  re.DOTALL)`, is greedy: against the raw sliced YAML text it matched past
  the intended closing quote, through the rest of the hook block and into
  the *next* hook's comment. Symptom: the captured "inner" script
  contained `pass_filenames: false`, `always_run: true`, and the next
  hook's comment lines as literal text.
- Separately, extracting the entry from raw config text (rather than
  through `yaml.safe_load`) preserved the literal newlines YAML's
  block-folded scalar uses for line wrapping. Fed to `bash -c`, an
  unquoted newline mid-command terminates the statement — the second
  physical line's first token (`CONTEXT.md`) then ran as its own command
  and failed with "command not found" (exit 127).

Both are gone in the shipped version: it parses through PyYAML from the
start (which correctly folds the multi-line scalar into one shell-safe
line, exactly as pre-commit itself would run it) and never touches raw
multi-line config text.

### 11.5 LOW — judged, both fixed (cheap)

- **The raw-text `config.index("- id: ", start + 1)` slice**, which would
  raise an unhandled `ValueError` (not a clean test failure) if `mdformat`
  ever became the config's last hook: gone entirely in 11.4's redesign —
  `yaml.safe_load` plus a dict lookup by `id` has no ordering dependency
  at all. The identical pattern still exists in the pre-existing, untouched
  `test_pyproject_fmt_flags_match_the_hook_the_seam_actually_runs` (line
  ~354) — out of this task's scope, not touched; see Concerns.
- **`pyproject.toml`'s 12-line upgrade-protocol comment ending in
  rationale** ("...would corrupt two of these three files if only one
  were watched") rather than a constraint. Restructured to lead with the
  imperative (an upgrade "must land as its own churn commit... never
  through the normal commit-time gate") and end on one too ("block the
  upgrade if any version starts escaping `%%` sequences").

### 11.6 Gates, this round

- Full suite: **1703 passed, 7 skipped** — down from 1714 by exactly 11,
  computed in advance (the 11 `skills/find-sources/references/*.md` files
  dropped out of the mdformat table-truncation sweep once excluded) and
  matched exactly on the run.
- `ruff check knowledge_harness tests scripts hooks`: all checks passed.
- `ruff format --check knowledge_harness tests scripts hooks`: 75 files
  already formatted.
- `mypy knowledge_harness`: no issues, 27 source files.
- `mdformat --number --wrap keep --check` over the hook's actual resolved
  file set (extracted and run the identical way the mirror test does):
  exit 0.
- `pyproject-fmt --keep-full-version --no-generate-python-version-classifiers
  --table-format long pyproject.toml`: no change.
- `yamlfix --check .github/workflows knowledge_harness/templates/ci`: 0
  fixed.
- `record-immutability` hook's exact command, re-run against real git
  (not re-touched this round, upheld by the coordinator): exit 0.
- `echo '{}' | python hooks/stop_publish_gate.py`: exit 0.

**`pre-commit run --all-files` was NOT run this round.** The working tree
carries `.superpowers/sdd/2026-08-22-post-q-batch/progress.md`, the
coordinator's uncommitted file, for the entire duration of this task. Per
the new repo policy landed on `origin/main` mid-task (`3d6ad73`, "AGENTS.md:
shared-checkout etiquette — never touch another session's uncommitted
files"), no session may `git checkout --`, `git stash`, or otherwise
revert/restore another session's uncommitted file to force a clean tree
for that gate — even with the checksummed-copy-and-exact-restore procedure
used safely in round 0. Verified this is current, not stale advice: `git
branch --all --contains 3d6ad73` shows it on `main`/`origin/main`;
confirmed via `git show 3d6ad73` that the AGENTS.md line change is real and
states the rule verbatim. Reporting the precondition as unmeetable, per
the instruction, rather than working around it: every constituent gate the
`pre-commit` hooks would run was instead verified individually above,
each using the hook's own exact command extracted from the real,
committed `.pre-commit-config.yaml` (not a hand-typed approximation).

### 11.7 Concerns, round 1

- **The same `config.index(..., start + 1)` ValueError-fragility pattern**
  (11.5) also exists, untouched, in the pre-existing
  `test_pyproject_fmt_flags_match_the_hook_the_seam_actually_runs`
  (`tests/test_config_validity.py`, ~line 354) — a different test than the
  one this round's LOW item named, not fixed here since it was not in
  scope. → controller, candidate one-line fix if wanted.
- **Restoring `skills/find-sources/references`'s upstream bytes** is
  explicitly NOT done by this round's exclusion (11.2) — the fork still
  carries `ce0f1e3`'s churn. → GitHub issue #24 (verified OPEN), as ruled.
- All four Concerns from §10 (round 0) stand unchanged; none were
  addressed or superseded by this round's findings.
