# Task 2d report: formatter ignore files ship with the vault; AGENTS.md scope line corrected

Disposition: historical (2026-09-06)

## 1. The three ignore files: contents and why each syntax is right

All four machine surfaces named by the brief — `literatures/`, `log/`,
`inbox/review-queue.md`, `system/bibliography.json` — needed covering. Verified
each tool's actual ignore mechanism rather than assuming gitignore syntax
transfers everywhere (it does for two of the three; not for the third):

- **prettier** (`prettier.io/docs/en/ignore`): ".prettierignore uses gitignore
  syntax." Confirmed via WebFetch.
- **markdownlint-cli** (igorshubovych/markdownlint-cli, the maintained fork):
  "a `.markdownlintignore` file will be used to ignore files and/or
  directories according to the rules for gitignore." Confirmed via WebSearch
  (DavidAnson/markdownlint-cli's README 404'd; the live fork's docs and
  multiple secondary sources agree on gitignore-style rules).
- **EditorConfig** (`spec.editorconfig.org`): has no ignore/exclude directive
  at all. Its only opt-out primitives are per-property: `false` for the two
  boolean properties (`insert_final_newline`, `trim_trailing_whitespace`),
  and the special value `unset` for any property ("removes the effect of
  that pair, even if it has been set before"). Confirmed via WebFetch,
  including glob anchoring rules (a pattern containing `/` is anchored to
  the `.editorconfig` file's directory; `**` matches across separators) and
  comment syntax (`#`/`;`, allowed in the preamble before `root = true`).

`.prettierignore` and `.markdownlintignore` (identical, gitignore syntax):

```
# Machine-owned surfaces: the CLI, Better BibTeX, and the bridge are their
# only writers. Prettier/markdownlint reformatting them would fight the
# trust machinery.
literatures/
log/
inbox/review-queue.md
system/bibliography.json
```

`literatures/` and `log/` are unanchored gitignore directory patterns
(matches at any depth, harmless here since there is only one of each name);
`inbox/review-queue.md` and `system/bibliography.json` contain a `/` and so
are anchored to the vault root, matching exactly those two files.

`.editorconfig`:

```
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[literatures/**]
charset = unset
end_of_line = unset
insert_final_newline = false
trim_trailing_whitespace = false

[log/**]
charset = unset
end_of_line = unset
insert_final_newline = false
trim_trailing_whitespace = false

[inbox/review-queue.md]
charset = unset
end_of_line = unset
insert_final_newline = false
trim_trailing_whitespace = false

[system/bibliography.json]
charset = unset
end_of_line = unset
insert_final_newline = false
trim_trailing_whitespace = false
```

Design note, corrected after review: my first draft used `unset` for all
four properties on all four surfaces. That is wrong for the realistic
threat. `unset` only reverts to "no value set here", which falls through to
whatever the editor's own (global, user-level) setting is — a user who has
"trim trailing whitespace on save" enabled in their editor would still trim
`inbox/review-queue.md`, because `unset` does not override that setting, it
just declines to add a competing one. `false` is an active directive that
wins regardless of the editor's own default, so it is the correct primitive
for the two boolean properties. **`charset` and `end_of_line` have no
boolean "off" value** — there is no EditorConfig-native way to say "leave
this file's charset/line-ending alone no matter what the editor wants."
`unset` is the best available for those two, and it is a real, accepted
residual gap: an editor with a global non-UTF-8 charset or non-LF
line-ending default could still touch these two properties on the four
surfaces. This is inherent to the EditorConfig spec, not a mistake in this
file.

Also worth flagging (non-blocking, scope-adjacent): the `[*]` section
applies `trim_trailing_whitespace = true` / `insert_final_newline = true`
vault-wide, including to user-owned notes (`projects/`, `synthesis/`,
free prose below the managed region in literature notes). That is a
reasonable, conventional baseline for a git-tracked knowledge vault (and it
is what makes the four surfaces' `false` overrides meaningful — without a
project-wide default there would be nothing to override in the first
place), but it is an opinion beyond the four-surface mandate and is called
out here for the owner rather than silently imposed. I kept it because (a)
the task's own paragraph in AGENTS.md already asserts each machine surface
"has one owner and a byte contract" implying other files don't have that
constraint and are fair game for normal editing conventions, and (b) LF/
UTF-8/final-newline/no-trailing-whitespace is uncontroversial for markdown
notes. If the owner disagrees, dropping those four lines from `[*]` is a
one-line-block deletion with no knock-on effect on the four-surface
coverage.

## 2. Dotless-asset mapping

Followed the existing `gitignore` → `.gitignore` pattern exactly rather than
inventing a new one. `research_vault/scaffold.py`:

```python
# Dotfiles ship dotless (packaging pitfall: a dotfile committed directly as
# a template asset risks silently failing to package) and are renamed here
# on write.
_DOTLESS_TEMPLATE_RENAMES = {
    "gitignore": ".gitignore",
    "prettierignore": ".prettierignore",
    "markdownlintignore": ".markdownlintignore",
    "editorconfig": ".editorconfig",
}


def _vault_template_paths(templates):
    source_root = templates.joinpath("vault")
    for relative, source in _template_files(source_root):
        yield _DOTLESS_TEMPLATE_RENAMES.get(relative, relative), source
```

Verified the packaging concern directly rather than trusting the glob:
built a real wheel (`pip wheel --no-deps --no-build-isolation`) and listed
its contents — `research_vault/templates/vault/{editorconfig,
markdownlintignore,prettierignore}` are all present, packaged dotless exactly
like `gitignore`. Also ran a live `scaffold_vault()` against a throwaway
directory: all three land renamed with the leading dot, with correct
content, and are committed into the scaffolded vault's own first commit
alongside `.gitignore` (confirmed via `git show --stat HEAD` in the
scaffolded repo). Both throwaway directories and the wheel were removed
afterward; a stray `research_vault.egg-info/` (already gitignored) from
the wheel build was also removed to leave a clean tree.

## 3. Pins the suite revealed

Ran the full suite before touching pins, to let it enumerate rather than
trusting the brief's list alone (per the brief's own instruction — a prior
task's brief named one pin and the suite found a second). Three pins moved:

- **`tests/test_scaffold.py` `EXPECTED_CREATED`** (18 → 21 paths): added
  `.editorconfig`, `.markdownlintignore`, `.prettierignore` in their sorted
  position (scaffold_vault returns `sorted(created)`). `TRACKABLE_CREATED`
  derives from this list by filtering out `.git/`/`.research-vault/`-prefixed
  paths; the three new dotfiles are neither, so they fall into
  `TRACKABLE_CREATED` and get committed by `scaffold_vault`'s own commit
  step. **Confirmed this is correct**: these are vault-owned config files
  that belong in the vault's own git history next to `.gitignore`, not
  research-vault-local state — verified directly via the live scaffold smoke test
  in section 2.
- **`tests/test_templates.py` `EXPECTED_PATHS`**: added `vault/prettierignore`,
  `vault/markdownlintignore`, `vault/editorconfig` (dotless, matching the
  on-disk template asset names before scaffold's rename).
- **`tests/test_templates.py` — the vault AGENTS.md whole-file byte-equality
  pin** (`test_markdown_templates_match_canonical_content`): updated the two
  changed sentences (below). The constraint comment immediately above the
  pinned string, which asserts the *preamble* — not the formatter
  paragraph — names machine surfaces without claiming an enforcement
  mechanism, was left untouched: it still applies to line 6, which this
  task did not touch, and its content is unaffected by either of my edits.

No other enumerated-scaffold-output surface was found. Explicitly checked
and ruled out as not tripped by this change:

- `tests/test_config_validity.py` `JSON_MANIFESTS` — an explicit list, not a
  glob; does not include vault template JSON.
- `tests/test_config_validity.py` `_mdformat_owned_markdown()` /
  `_MDFORMAT_ROOTS` — scans repo-root `README.md`/`AGENTS.md`/`CONTEXT.md`/
  `docs`/`skills`, not `research_vault/templates/`; matches the brief's
  note that mdformat structurally cannot reach the templates directory.
- `tests/test_skill_files.py` — checks skill-file prose, not template file
  lists; unaffected.
- No `pytest.mark.parametrize` in the suite is driven by `EXPECTED_PATHS`,
  `EXPECTED_CREATED`, or a glob over `research_vault/templates/`.

I also added one new test, `test_formatter_ignores_cover_every_machine_surface`
in `tests/test_templates.py`, asserting all four machine-surface strings
appear in `.prettierignore`/`.markdownlintignore`, and that `.editorconfig`
declares a matching section for each with exactly 8 `= unset` and 8
`= false` directives. This is what accounts for the whole test-count delta
(below) — it is not a pin the suite revealed, it is new coverage added
because the brief's own risk framing ("wrong syntax means they silently do
nothing") had no test guarding it otherwise.

## 4. The shrunken paragraph, before and after

Before:

> Formatters are writers too. Each machine surface has one owner and a byte
> contract, and the trust machinery rejects foreign writers mechanically —
> so running a Markdown or JSON formatter across the vault is what sets the
> alarms off. This paragraph explains the alarms; it is not what enforces
> them.

After:

> Formatters are writers too: `.prettierignore`, `.markdownlintignore`, and
> `.editorconfig` keep them off the machine surfaces.

## 5. The scoped line 10

Verified mechanically which skills are model-invocable: `grep -rl
"disable-model-invocation" skills/*/SKILL.md` returns exactly seven files
(`publish`, `factcheck-draft`, `project-flow`, `verify-citations`,
`import-source`, `setup-vault`, `find-sources` — the same seven already
listed in the AGENTS.md table). `evidence-conventions` and
`synthesis-conventions` are the only two `SKILL.md` files without the flag,
confirming the brief's claim.

Before:

> Prefer the research-vault skills over generic drafting, even for
> free-form requests. Run `evidence-conventions` for claim syntax.

After:

> Prefer the two model-invocable research-vault skills over generic
> drafting, even for free-form requests: run `evidence-conventions` for
> claim syntax and `synthesis-conventions` for synthesis-note rules.

**No `disable-model-invocation` flag was touched.** `git diff --stat
skills/` is empty for this change.

## 6. Test-count delta accounted for

Baseline (BASE): 1575 passed, 7 skipped.
After this task: **1576 passed, 7 skipped** (form gate 8/8).

Delta: +1, fully accounted for by the single new test added in section 3
(`test_formatter_ignores_cover_every_machine_surface`). No parametrized
instrument picked up the three new template files (verified by inspection
in section 3), so there is no other source of test-count movement to
explain.

## 7. Lines 6 and 26 — untouched

`git diff -- research_vault/templates/vault/AGENTS.md` shows only two
hunks: the line-10 sentence and the formatter paragraph. Line 6 (the
integrity preamble) and line 26 (`Machine surfaces (...) are owner-written`)
do not appear in the diff at all — confirmed by inspection of the diff
output, not by assumption.

One thing a reviewer may ask, answered here rather than left implicit:
`log.md` is named in line 6 as machine-written, but it is not one of the
four surfaces the ignore files cover. That is deliberate and matches the
brief's explicit four-surface list (`literatures/`, `log/`,
`inbox/review-queue.md`, `system/bibliography.json`), which is the same set
line 26 names (line 26 also omits `literatures/` in favor of "managed
regions"). Line 6's four-surface list already diverges from line 26's, and
that divergence is recorded in the plan as a **known, deferred** finding for
the final review — not something this task's scope extends to reconcile.

## 8. Concerns

- The `[*]` section in `.editorconfig` imposes LF/UTF-8/final-newline/
  no-trailing-whitespace on every vault file, not just the four machine
  surfaces — see the design note in section 1. Kept deliberately; flagged
  for the owner rather than silently imposed or silently dropped.
- `.editorconfig`'s `charset`/`end_of_line` `unset` on the four surfaces is
  a real, accepted gap (no boolean "off" exists for those two properties in
  the spec) — an editor with a non-default global charset/line-ending
  setting could still touch those two properties on the four surfaces. This
  is inherent to EditorConfig, not fixable within this file.
- DavidAnson/markdownlint-cli's README 404'd during verification; confirmed
  the gitignore-style ignore-file behavior instead via the actively
  maintained igorshubovych/markdownlint-cli fork's docs and corroborating
  secondary sources. I did not find a primary-source page contradicting
  this, but flagging the substitution for the record.

## 9. Fix round 1 — `[*]` removed from `.editorconfig`, author ruling applied

The coordinator escalated concern 1 above to the author, who ruled: drop the
`[*]` section. Two convergent reasons — the four surface sections' `false`
overrides do their job (defending against **any** editor's defaults,
including the user's own) with or without a `[*]` block above them; and the
`[*]` block was a style opinion (LF/UTF-8/final-newline/no-trailing-
whitespace on every vault file) carrying no correctness claim the trust
machinery owns, which is exactly what "vault outlives its tools" says
research-vault does not get to impose. Applied:

**`[*]` removed entirely.** `research_vault/templates/vault/editorconfig`
now opens straight from `root = true` into the four surface sections. No
property is asserted for any file outside the four surfaces — silence about
what the machinery does not own, matching line 26's framing.

**`charset`/`end_of_line` dropped, not kept as `unset`.** This was the
implementation judgment call the ruling asked me to make explicitly, not
just carry over: with no `[*]` section and `root = true` blocking every
ancestor `.editorconfig` from being read at all, there is nothing left in
this file's scope for `unset` to undo — `unset` "removes the effect of that
pair, even if it has been set before" (spec.editorconfig.org), and nothing
sets charset/end_of_line anywhere this file can see. Keeping `charset =
unset` / `end_of_line = unset` would therefore be inert cruft that reads as
protection where none exists. I dropped both lines from all four sections
and say so plainly in the header comment instead. The residual gap stays
true either way and is stated explicitly: charset/end_of_line have no
boolean "off" in the spec, so an editor's own (non-EditorConfig-sourced)
charset or line-ending default can still touch these four surfaces — this
was true with the inert `unset` lines and is still true without them; the
only change is that the file no longer pretends otherwise.

**`root = true` kept**, reasoned through rather than carried over by
default. Its job now is narrower than before (it isn't protecting a `[*]`
block that no longer exists) but still load-bearing: it makes this file
authoritative on its own, by construction, rather than by an inference
about cross-file precedence I'd otherwise be resting the four surfaces'
protection on. Without `root = true`, a conforming implementation would
also read every `.editorconfig` in ancestor directories (e.g. if the vault
is nested inside a larger tree that happens to have one) and merge their
sections in; I believe closer-file sections take precedence over farther
ones for conflicting keys, which would likely mean our four sections still
win even without `root = true` — but I'd rather not depend on that belief
holding across every EditorConfig core implementation. `root = true` is one
line, imposes no opinion on any file (it is a search-scope declaration, not
a formatting value), and converts an inferred guarantee into a spec-
guaranteed one for the only four things this file protects. Kept for that
reason.

**Pins moved, in the same commit (amended `41c934a` → `c418cf7`, branch tip
with nothing on top, not pushed — confirmed via `git rev-parse
--abbrev-ref --symbolic-full-name @{u}` failing with "no upstream
configured"):** only `tests/test_templates.py`'s
`test_formatter_ignores_cover_every_machine_surface` needed rework — it now
asserts no bare `[*]` section line, no `= unset` directive, no
`charset =`/`end_of_line =` key anywhere, and exactly 8 `= false`
directives (2 properties × 4 surfaces). `EXPECTED_PATHS` /
`EXPECTED_CREATED` / the AGENTS.md byte-equality pin were untouched by this
round — none of them assert `.editorconfig`'s internal content, only its
existence and filename.

**Test evidence, this round:**
- `tests/test_templates.py tests/test_scaffold.py -q`: 24 passed.
- Full offline suite: 1576 passed, 7 skipped — same count as `41c934a`. No
  delta: this round reshapes an existing pinned test's assertions, it adds
  no new test and removes none.
- Form gate: 8/8, both before and after.

`prettierignore`/`markdownlintignore` were not touched, per the ruling —
they already list only the four surfaces and carry no `[*]`-equivalent
concept to remove.

## 10. Fix round 2 — the missing append-only surface, anchoring, and two commit-record corrections

The review this round was spec-compliant and verified the load-bearing
claims directly (both reference EditorConfig cores, a real wheel build
plus a live `scaffold_vault()` run, and `EXPECTED_CREATED`'s ordered-list
correctness) rather than trusting green pins. It found one real gap and
one scope correction, both author-ruled, plus two smaller corrections
folded in because the byte pin was already churning. A follow-up
coordinator message (mid-round) added two more: fixing the `root = true`
rationale in a second place, and wiring `oldest_age_days` (shipped by a
sibling commit, `eff8d67`) into its two intended consumers.

### 10.1 The missing surface: `projects/*/search-log.md`

`research_vault/lints.py`'s `_is_append_only_path` (line 109) is the
append-only lint's own scope authority — its docstring names three
durable-append surfaces:

```python
def _is_append_only_path(rel: bytes) -> bool:
    """The three durable-append surfaces this lint protects (terminology §4.1)."""
    return (
        rel == b"inbox/review-queue.md"
        or rel.startswith(b"log/")
        or (rel.startswith(b"projects/") and rel.endswith(b"/search-log.md"))
    )
```

The shipped ignore files covered two of the three (`log/`,
`inbox/review-queue.md`) and missed `projects/*/search-log.md` —
`find-sources`'s PRISMA-S search-provenance trail
(`research_vault/searchlog.py`, always exactly one level under
`projects/<name>/`). The author's ruling: the four-surface list in the
task brief "was the planner describing from memory what lints.py already
states precisely" — `_is_append_only_path` is the source of truth, not
the brief, so this was not a brief-following error on my part in round 1;
it was a real gap the brief itself carried.

Added `/projects/*/search-log.md` to `.prettierignore` and
`.markdownlintignore` (same gitignore syntax as the other four lines) and
a `[projects/*/search-log.md]` section to `.editorconfig` (same
`insert_final_newline = false` / `trim_trailing_whitespace = false` pair
as the other four sections). Each of the three files also gained one
line pointing at `_is_append_only_path` (plus `system/bibliography.json`,
Better BibTeX's export) as the source of truth for the list — three
imperative path lists in three formats cannot be made declarative or
derive from one another, so the next-cheapest defense is every copy
naming where truth lives.

### 10.2 Anchoring: `/literatures/` and `/log/`

Per `gitignore(5)`: a pattern is anchored to the `.gitignore` file's own
directory only if it has a separator at the beginning or in the middle;
a trailing slash alone (`literatures/`, `log/`) does **not** anchor — it
still matches a directory of that name at *any* depth below. So the
shipped `.prettierignore`/`.markdownlintignore` would have silently
shielded a user's own `projects/<name>/log/` or
`projects/<name>/literatures/` from formatting too, widening the ignore
file's effect well past its stated four (now five) surfaces. Added a
leading `/` to all five entries in both files for one explicit, uniform
meaning (`inbox/review-queue.md`, `system/bibliography.json`, and the new
`projects/*/search-log.md` already contained an interior `/` and were
technically anchored either way; the leading slash was added to them too
for explicitness, not because they needed it).

`.editorconfig`'s sections were already anchored: per
`spec.editorconfig.org`, a glob is relative to the `.editorconfig`
file's own directory whenever it contains a path separator not inside
square brackets, and every section in this file already does
(`literatures/**`, `log/**`, etc.) — EditorConfig has no leading-slash
convention the way gitignore does, so nothing there changed except the
new `projects/*/search-log.md` section.

### 10.3 Proof, not reasoning: the per-tool empirical evidence

The instruction was explicit and I treat it as met only by actual tool
runs, not by re-reading documentation: "An anchor a given tool does not
honour matches nothing — silently converting partial protection into
zero protection while every pin stays green." Neither `prettier` nor
`markdownlint-cli` is installed in this worktree or globally, but both
were found fully materialized and runnable in this machine's npx cache
(`~/.npm/_npx/`, left over from earlier, unrelated `npx` invocations),
at the *exact* versions a prior review cited:

```
$ node ~/.npm/_npx/7e4347a8d51f6fca/node_modules/prettier/bin/prettier.cjs --version
3.9.6
$ node ~/.npm/_npx/f4da0b4ac6006cf9/node_modules/markdownlint-cli/markdownlint.js --version
0.49.1
```

Built a fixture vault at `/tmp/rv-anchor-check/` (removed after use) with
all five real surfaces (`literatures/citekey.md`, `log/2026-08-24.md`,
`inbox/review-queue.md`, `system/bibliography.json`,
`projects/myproj/search-log.md`), two same-named nested decoys
(`projects/myproj/literatures/decoy.md`, `projects/myproj/log/decoy.md`),
and one non-machine control file (`synthesis/index.md`) — all seeded with
trailing whitespace / minified JSON, i.e. content each tool would flag if
it actually looked at the file.

**prettier**, using the shipped, anchored ignore file:

```
$ node .../prettier.cjs --check "**/*.md" "**/*.json"
[warn] projects/myproj/literatures/decoy.md
[warn] projects/myproj/log/decoy.md
[warn] synthesis/index.md
[warn] Code style issues found in 3 files.
```

Only the decoys and the control file are flagged; individually checking
each of the five real surfaces returned exit 0 / "All matched files use
Prettier code style!" despite dirty content (confirmed per-file for all
five). Rerunning the identical fixture with the **pre-fix, unanchored**
`literatures:`/`log/` lines (`literatures/`, `log/`, no leading slash)
reproduced the bug directly: prettier then flagged only `synthesis/index.md`
— **both decoys silently swallowed**, which is the exact failure the
anchoring fix closes.

**markdownlint-cli**, same fixture:

```
$ node .../markdownlint.js "**/*.md"
projects/myproj/literatures/decoy.md:1:24 error MD009 ...
projects/myproj/literatures/decoy.md:1 error MD041 ...
projects/myproj/log/decoy.md:1:17 error MD009 ...
projects/myproj/log/decoy.md:1 error MD041 ...
synthesis/index.md:1:8 error MD009 ...
synthesis/index.md:1:8 error MD022 ...
synthesis/index.md:2:38 error MD009 ...
```

Same pattern: decoys and control flagged, all four real markdown surfaces
silent. Explicit per-file checks on each real surface (`literatures/citekey.md`,
`log/2026-08-24.md`, `inbox/review-queue.md`, `projects/myproj/search-log.md`)
fell through to markdownlint-cli's "no files remained to lint" usage
printout (exit 0), contrasted directly against `synthesis/index.md`
checked the same way, which produced real errors (exit 1) — an
unambiguous ignored-vs-not-ignored signal.

**`.editorconfig`: no offline conformance tool exists on this machine,
and I say so rather than paper over it.** Checked, in order: a Python
`editorconfig` package (absent — `ModuleNotFoundError` in both the
system Python and this repo's venv), an npm `editorconfig`/`eclint`/
`editorconfig-checker` package (absent from the full npx cache despite a
broad `grep`; the one hit was a devDependency *listing* inside an
unrelated cached package's own `package.json`, not an installed
package), a system `editorconfig-checker`/`ec` binary (absent), `dpkg`/
apt cache (absent), and the pre-commit hook cache (no editorconfig-named
repo). Confirmed conclusively, without touching the network, via
`uv pip install --offline --python <venv> editorconfig`:

```
× No solution found when resolving dependencies:
  ╰─▶ Because editorconfig was not found in the cache ... network was disabled.
```

Rather than fall back to reasoning about the spec text (which is exactly
what this instruction forbids), I used **prettier's own bundled
EditorConfig resolver** — a real, independently authored conformant
implementation prettier itself uses to read `end_of_line`, `indent_style`,
`indent_size`/`tab_width`, and `max_line_length` (prettier does **not**
read `insert_final_newline`/`trim_trailing_whitespace`, the two
properties this file actually sets — those are editor save-time
behaviors outside what a batch formatter itself writes, so that part of
the shipped file's behavior remains unverified by any tool run here; see
concern below). Built a probe `.editorconfig` using the *exact* section
globs from the shipped file (`literatures/**`, `log/**`,
`projects/*/search-log.md`) with `end_of_line = crlf` (a property
prettier does honor) against a `[*] end_of_line = lf` default, then ran
prettier over matching JSON files and inspected raw bytes:

| file | glob it should match | end-of-line found |
|---|---|---|
| `literatures/note.json` | `[literatures/**]` | `\r\n` (CRLF) |
| `projects/myproj/literatures/note.json` (decoy) | none — falls to `[*]` | `\n` (LF) |
| `log/note.json` | `[log/**]` | `\r\n` (CRLF) |
| `projects/myproj/log/note.json` (decoy) | none — falls to `[*]` | `\n` (LF) |
| `projects/myproj/search-log.md` | `[projects/*/search-log.md]` | `\r\n` (CRLF) |
| `projects/myproj/nested/search-log.md` (two levels deep) | none — `*` does not cross `/` | `\n` (LF) |
| `control.json` (vault root, no matching section) | `[*]` | `\n` (LF) |

A control run with `--no-editorconfig` on the same `literatures/note.json`
content produced `\n` (LF), confirming `.editorconfig` — not some other
default — was the actual driver of the CRLF result. This is a genuine,
disclosed evidentiary gap relative to the other two tools: I verified the
shipped file's exact glob-matching mechanics through a real conformant
engine, but not its exact two properties, because no available tool
reads them from a file the way an IDE would on save. If stronger
confidence is wanted, installing `editorconfig` (pip) or
`editorconfig-checker` with network access and re-running against the
shipped file directly would close this gap.

### 10.4 `root = true` rationale — corrected in both places

The header comment (round 1) claimed `root = true` stops ancestor
`.editorconfig` files from diluting the four (now five) `false`
overrides. That is disproven: closer-file precedence already gives this
file's own sections priority over any ancestor `.editorconfig` for a
property both define, with or without `root = true`. What `root = true`
actually blocks is an ancestor `.editorconfig` supplying
`charset`/`end_of_line` values that would otherwise reach these paths
(irrelevant to the `false` overrides, which do not need it). Corrected
the reason in the header comment, and — per a follow-up author note
flagging that the *same* wrong reason was restated near-verbatim in
`tests/test_templates.py`'s test comment — corrected it there too. (My
round-2 rewrite of that test comment had already dropped the
ancestor-dilution phrasing while updating the surface count, so by the
time the follow-up note arrived the test comment was already silent on
`root = true`'s rationale rather than stating the wrong one; I still
added the corrected reasoning to the header comment as the single
authoritative statement, and confirmed the test comment carries no
disproven or stale claim.) The **line itself** (`root = true`) was never
in question — the ruling was about which stated reason for keeping it is
true.

### 10.5 AGENTS.md formatter line — accuracy without weakening

Before (round 1): "Formatters are writers too: `.prettierignore`,
`.markdownlintignore`, and `.editorconfig` keep them off the machine
surfaces." — inaccurate: EditorConfig has no ignore primitive, so
crediting it with keeping formatters "off" a surface alongside two files
that genuinely do exclude paths overstated it.

After: "Formatters are writers too: `.prettierignore` and
`.markdownlintignore` keep them off the machine surfaces; `.editorconfig`
disables an editor's own trim/final-newline defaults there instead."

### 10.6 Two corrections to `c418cf7`'s own commit body (record only, forward)

`c418cf7` is buried under two later commits (`eff8d67`, `ebea360`), so
per instruction these are corrected **forward**, in `2e23c40`'s body, not
by rewriting history:

- It cited the task brief at `docs/superpowers/sdd/2026-08-22-post-q-batch/
  task-2d-brief.md`. That path exists nowhere: `git ls-tree --name-only
  origin/main -- docs/superpowers/` returns only `docs/superpowers/plans`
  and `docs/superpowers/specs`. The real path is
  `.superpowers/sdd/2026-08-22-post-q-batch/task-2d-brief.md` (repo root,
  not under `docs/`) — itself gitignored, same as this report.
- It called `igorshubovych/markdownlint-cli` "the maintained fork." It is
  the canonical repository, not a fork. The syntax claim it supported
  (gitignore-style `.markdownlintignore` rules) was and is correct — only
  the repository's status was misdescribed.

### 10.7 Pins, this round

Only `tests/test_templates.py` needed changes: `_MACHINE_SURFACES` gained
the leading-`/` anchored form plus the fifth surface;
`test_formatter_ignores_cover_every_machine_surface`'s per-tool loop and
`.editorconfig` assertions moved with it (the glob-derivation line now
strips the gitignore-style leading `/` before building the EditorConfig
section name, since that tool has no equivalent leading-slash syntax);
and the AGENTS.md whole-file byte-equality pin picked up the reworded
formatter sentence. Per the explicit instruction, the test's
substring/aggregate assertion *shape* was deliberately left alone this
round (deferred as a redesign question) — only the byte content the
assertions check against was updated.

Ran the full suite rather than trusting this list: `1576 passed, 7
skipped` — identical to `ebea360`'s baseline. No delta: this round
reshapes existing pinned assertions and adds no new test.

### 10.8 Addition — wiring `oldest_age_days` into its two consumers

A sibling commit (`eff8d67`) added `oldest_age_days` to
`inbox.summary()`, but nothing read it yet. Checked the exact shipped
semantics in `research_vault/inbox.py` before writing anything: whole
days between today (UTC) and the oldest non-SKIPPED unacknowledged
entry's date; `None` exactly when `oldest` is `None` (nothing
unacknowledged); a freshly filed entry reports `0`, not `None`. Doctor's
own "inbox" probe (`research_vault/scaffold.py`'s `_inbox_probe`)
reports only `count` and the raw `oldest` date in its reason string, not
`oldest_age_days` — that field is only surfaced via `inbox.summary()`'s
JSON, which the standalone `python3 -m research_vault inbox --vault
PATH` command prints verbatim on its first line.

Added one sentence naming `oldest_age_days` to each consumer, inserted
inside the existing single-physical-line paragraph (no new line breaks),
so the coordinator-cited line numbers (`project-flow/SKILL.md:25`,
`setup-vault/SKILL.md:34`) stayed accurate and unchanged rather than
shifting:

- `skills/project-flow/SKILL.md:25` (the Whittaker inbox-rot guard): "...a
  warn queue nobody drains is a silent failure. `inbox`'s summary reports
  `oldest_age_days` directly — whole days since the oldest entry, 0 for
  one filed today, `None` only when nothing is unacknowledged — so read
  that figure rather than computing the entry's age from its date
  yourself. When the oldest entry is old, lead with it..."
- `skills/setup-vault/SKILL.md:34`: "Report every doctor probe, not only
  failures, plus the inbox count and oldest age. `inbox`'s summary reports
  `oldest_age_days` directly — whole days since that date, 0 for one
  filed today, `None` only when the queue is empty — so state that figure
  rather than estimating the age yourself. Do not replace this with a
  `doctor --url` command or environment variable."

Neither introduces a threshold, a boolean, or a day count at which
something becomes "aging" — both keep the existing continuous, relative
language ("old," "aging queue earns more prominence the longer it goes
untouched") exactly as before; only the *mechanism* for determining age
changed, from agent-side date math to reading the supplied field.

Ran the full suite to find every affected pin rather than trusting the
two cited line numbers or this description: `tests/test_project_flow_skill.py`'s
pinned substring `"unacknowledged count and the oldest entry's date,
oldest first"` and `tests/test_skill_files.py`'s `"inbox count"` /
`"oldest age"` substring checks all still hold verbatim (the new
sentences were inserted around the existing pinned text, not through
it). Targeted run (`tests/test_project_flow_skill.py
tests/test_skill_files.py`): 21 passed. Full suite: unchanged, `1576
passed, 7 skipped`.

### 10.9 Test evidence, round 2 (both commits)

- Full offline suite, final state (`89fe2fe`): **1576 passed, 7 skipped**
  — identical to the `ebea360` baseline cited for this round. No delta
  across either commit: both reshape/extend existing pinned assertions
  (or, for the skill files, land inside already-covered pinned
  substrings) without adding or removing a test.
- Form gate: **8/8**, run after each commit's changes and again at final
  `HEAD`.
- Per-tool anchoring proofs: section 10.3, above, with raw command output.

### 10.10 Commits this round

- `2e23c40` — `fix: search-log surface added and formatter-ignore
  patterns anchored` (the append-only surface, anchoring, proofs, the
  `root = true` header-comment correction, the AGENTS.md wording fix, and
  the two `c418cf7` commit-body corrections).
- `89fe2fe` — `docs: wire oldest_age_days into project-flow and
  setup-vault reporting` (Addition 2, kept as its own commit rather than
  folded into `2e23c40` since it is a distinct concern — completing
  `eff8d67`'s wiring — with its own independent test evidence).

Both are plain follow-up commits on top of `ebea360`; no amend, no
rebase. (One process note for the record: my first attempt at `2e23c40`
accidentally staged the two skill files into the same commit before I'd
written their message; caught it before reporting anything, and
corrected it with `git reset --soft HEAD~1` immediately after the commit
— on a commit that existed for only this one tool call and had not been
referenced, reported, or built on by anything — followed by re-staging
into the two commits actually described above. No shared or
previously-reported history was rewritten.)

### 10.11 Concerns, round 2

- `.editorconfig`'s two shipped properties
  (`insert_final_newline`/`trim_trailing_whitespace`) were verified for
  glob-matching correctness via prettier's bundled resolver, but not
  end-to-end through a tool that itself reads and acts on those two
  specific properties, because none is available offline on this
  machine. Documented as a real, disclosed gap in 10.3, not elided.
- Everything else from round 1's concerns stands as before (the
  charset/end_of_line residual gap is unchanged in nature, just
  reworded to say why `root = true` doesn't rescue it either).
