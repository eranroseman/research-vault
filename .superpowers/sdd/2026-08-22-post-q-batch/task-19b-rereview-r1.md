# Task 19b re-review, round 1

Scope: `a2b829d..6a62cab` (review only `6a62cab`; `3c73676` is a plan-doc
amendment; `a2b829d` accepted, not re-reviewed). HEAD is ahead
(`a42c7a1`, post-merge) — checked out nothing, read-only throughout.

## Verdict: SOME OPEN

Items 1–3 are fully addressed and empirically confirmed. Item 4's own
correction — the report's replacement sentence for the "every branch has a
red test" overclaim — is itself still an overclaim: it names one documented
exception but a second, undocumented one exists (below). The defect this
item exists to fix (an overclaimed coverage sentence) is not fully fixed.

## Method

All discrimination checks were run as subprocess probes against
`hooks/pretooluse_guard.py` (stdlib-only, no `research_vault` import) —
mutated in a `git archive 6a62cab | tar -x` scratch tree at
`/tmp/task19b-scratch` (never `cp -r`, never `git` inside it), diffed
byte-identical back to the real worktree file after every restore, deleted
when done. This verifies *hook behavior* flips under each mutation (deny
becomes allow, or the reason string changes) and separately confirms the
test helpers (`_pretooluse_deny`, `_assert_pretooluse_allows`) assert exact
shape/equality/silence — so a behavior flip necessarily fails the assertion.
I did not run `pytest` against the mutants directly (the scratch tree can't
import `research_vault`); the chain from "behavior flips" to "test goes
red" is by inspection of the assertion helpers, not a directly observed red
run. Full suite was run once, unmutated, in the real worktree at current
HEAD (`a42c7a1`, post-merge) — see counts below. I did not check out or run
the suite at `6a62cab` itself.

## Item 1 — root `log.md` joins the deny list

CONFIRMED. `<vault>/log.md` → deny, reason string exactly
`"machine surface; the CLI writes this — use the matching verb (`finding`,
`ack`, `import-note`, …)"`. Removing `Path("log.md")` from
`MACHINE_SURFACE_FILES` flips that one case to silent allow, isolated (other
entries unaffected) — discriminates. Boundary: `projects/brief/search-log.md`
allowed, `projects/brief/log.md` (nested) allowed, `log/2026-01-01.md`
(directory) still denied — all four reproduced directly and all four are
pinned by parametrized tests (`test_pretooluse_denies_edit_into_every_machine_surface`,
`test_pretooluse_allows_edit_outside_machine_surfaces`).

## Item 2 — three self-reported matrix gaps

- (a) non-dict payload (`[]`) guard: silent with guard present; removing
  `if not isinstance(payload, dict): return` turns it into a fail-closed
  deny (`AttributeError` on `[].get(...)`) — discriminates.
- (b) relative `cwd` guard: silent (`cwd="literatures"`, `file_path="clean.md"`)
  with guard present; dropping `not Path(cwd).is_absolute()` (keeping only
  `cwd is None`) turns it into a deny (falls through to `Path.resolve()`'s
  ambient-cwd fallback and lands in the real vault) — discriminates.
- (c) deleted `except ValueError` around `resolved.relative_to(vault)`:
  independently re-derived and stress-tested. `_vault_from_target` draws
  `vault` from `target.parent`/`target.parent.parents` — pure lexical
  truncation of the *same* `resolved` object passed in at the call site.
  `Path.relative_to` on an ancestor produced this way cannot raise, by
  construction (ancestor's parts are always a literal prefix of the
  descendant's parts). Tried to falsify with `..`-laden paths, a symlink
  redirecting into the vault, and a broken/nonexistent final component —
  none reached the branch; `_vault_from_target` and `.relative_to` behaved
  consistently in every case. **Verdict: truly unreachable, deletion is
  correct**, not a defect.
- (d) matrix-overclaim correction: see Item 4 below — the correction itself
  is incomplete.

## Item 3 — failure posture

| Input | Observed behaviour |
|---|---|
| malformed JSON (`"not json"`) | silent, rc 0, empty stdout/stderr |
| empty stdin | silent, rc 0, empty stdout/stderr |
| missing `cwd`, relative `file_path` | silent (unresolvable, not anchored to ambient cwd) |
| missing `cwd`, absolute `file_path` in vault | deny, machine-surface reason (absolute doesn't need `cwd`) |
| missing `tool_input` | silent |
| non-string `file_path` | silent (filtered in `_candidate_paths`) |
| symlink loop (`ELOOP`) via `.resolve()` | **deny, `FAIL_CLOSED_REASON`** — a genuinely induced exception past parsing, confirms tier 3 empirically, not just by reading the code |

Judgment: the three-tier posture is right for a deny hook. Tier 1
(unparsable/empty stdin → silent allow) is technically fail-open for that
narrow input class, but it is a deliberate, justified call — Claude Code
cannot send malformed JSON for a matched tool call, so it's not attributable
to a real invocation, and it matches every other hook in the repo including
the fail-closed `stop_publish_gate.py`. Tier 3 (any exception past parsing)
is genuinely fail-closed, confirmed with a real exception (ELOOP), not a
theoretical claim. The decision is stated where a future editor will see it:
`main()`'s docstring spells out all three tiers and the rationale. The
residual assumption (well-formed JSON is guaranteed for matched tool calls)
is inherited, not re-justified here, but it is at least named.

## Item 4 — matrix overclaim correction, spot-checked

The corrected sentence: "every new production branch has at least one test
that goes red... with one documented exception" (the `.resolve()`/dotdot
case). Spot-checked two branches:

- tool-name membership check (`payload.get("tool_name") not in {...}`):
  removed it, fed `Bash`/`Read`/`Grep` at a machine-surface path — all three
  now deny instead of silent-allow. Matches the report's claim; discriminates
  as documented.
- `cwd = cwd if isinstance(cwd, str) else None`
  (`hooks/pretooluse_guard.py:101`): removed it, fed a non-string non-None
  `cwd` (`12345`) with a relative `file_path` — the mutant now fails closed
  (`FAIL_CLOSED_REASON`) instead of silently allowing. **No test in the
  suite feeds a non-string, non-None `cwd`** — every existing `cwd`-related
  test either omits `cwd` entirely or sets it to a real path string. The
  missing-`cwd` tests do not discriminate this line (with the filter
  removed, `cwd=None` still flows to `None` either way). This is a second,
  undocumented exception to the "every branch" claim — the very sentence
  `6a62cab` introduced to correct the prior overclaim
  (`task-19b-report.md`, "Per-test discrimination matrix" section) is itself
  still not fully accurate.

**Severity: minor.** The uncovered branch fails in the safe direction (deny,
not allow) — this is a coverage/claim gap, not a security leak. But it is a
finding squarely inside the scope of what Item 2(d)/Item 4 were supposed to
fix.

## Other checks

- **Loose-assertion sweep (the plan's recurring defect):** all deny-path
  tests assert exact reason-string equality (`== MACHINE_SURFACE_DENY_REASON`)
  via `_pretooluse_deny`, which itself asserts exact JSON shape
  (`set(output) == {"hookSpecificOutput"}`, `set(specific) == {...}`) before
  returning the reason. Mutated `DENY_REASON` itself to a different string
  while still denying for `log.md` — the hook still denies, but with a
  different reason, which would fail every test's exact-equality assertion.
  No instance of the loose-assertion defect found in `6a62cab`'s new tests.
- **Deny route line:** present and verbatim-correct, matches the brief's
  line exactly, backticks and ellipsis included.
- **`hooks.json` exact-equality pin:** intact — `test_stop_hooks_manifest_registers_posttooluse_and_stop_commands`
  still asserts the full manifest dict by `==`, not loosened. Passes.
- **Comment hygiene:** the two new/changed comments in
  `hooks/pretooluse_guard.py` (the `log.md` root-only note at the
  `MACHINE_SURFACE_FILES` definition, and the `relative_to` invariant note)
  both state constraints the code's shape alone doesn't show; neither
  carries provenance/history ("fix round 1", "author ruling") — that
  material correctly lives only in the commit message and report, not in
  source comments.
- **Test-name overclaim sweep:** none found; docstrings on the two new tests
  match their bodies precisely.

## Suite counts

Ran once, unmutated, from the real worktree at current HEAD (`a42c7a1`,
post-merge, not `6a62cab`): **1683 passed, 7 skipped** — matches the
caller's expected post-merge count. Did not re-run at `6a62cab` itself.
