# Task 19b report: PreToolUse deny guards machine surfaces

## Status

Complete. Steps 1–3 implemented and committed, plus a fix round 1 responding
to coordinator review (root `log.md` added to the deny list per author
ruling, two coverage gaps closed, one dead branch removed, one overstated
report sentence corrected) — see the "Fix round 1" section below.

## Commits

1. `feat: PreToolUse deny guards machine surfaces (trigger evidence: 2c reproduction)`
   (`a2b829d`) — files: `hooks/pretooluse_guard.py` (new), `hooks/hooks.json`,
   `tests/test_hooks.py`, `docs/superpowers/specs/2026-08-16-foundation-spec.md`,
   `.superpowers/sdd/2026-08-22-post-q-batch/task-19b-report.md`.
2. `fix: Task 19b review round 1 — root log.md joins deny list, dead code
   removed, matrix overclaim corrected` — files: `hooks/pretooluse_guard.py`,
   `tests/test_hooks.py`,
   `.superpowers/sdd/2026-08-22-post-q-batch/task-19b-report.md`.

## Test summary

Full suite: 1682 passed, 7 skipped (baseline 1650/7 + 32 new tests in
`test_hooks.py`, up from 27 after fix round 1). `ruff check .` and
`ruff format --check .` show only the five pre-existing vendored-fork
findings under `skills/find-sources/scripts/` (confirmed identical before
and after my changes via `git stash`; Task 2e owns that explicit exclusion,
not this task). `mypy knowledge_harness/`:
clean, 27 files. `echo '{}' | python hooks/stop_publish_gate.py`: silent,
exit 0.

## Hook protocol — sources (per the controller's instruction to verify, not guess)

1. **PreToolUse deny JSON shape** — `hookSpecificOutput.hookEventName`,
   `.permissionDecision` (`"allow" | "deny" | "ask"`),
   `.permissionDecisionReason`. Source: the official Claude Code hooks
   reference, bundled by the `working-with-claude-code` skill at
   `~/.claude/skills/working-with-claude-code/references/hooks.md` (fetched
   from docs.claude.com), lines 432–458 ("`PreToolUse` Decision Control").
   The deprecated top-level `decision`/`reason` fields (`"approve"`/`"block"`)
   are explicitly not used.
2. **NotebookEdit's path key is `notebook_path`, not `file_path`.** The
   bundled docs and even a fresh `tools-reference.md` fetch were ambiguous
   here (the `claude-code-guide` subagent explicitly declined to guess).
   Resolved against the actual shipped SDK types: fetched
   `https://unpkg.com/@anthropic-ai/claude-agent-sdk/sdk-tools.d.ts` and
   quoted the `NotebookEditInput` interface verbatim — `notebook_path:
   string` (required, absolute). The same fetch confirmed `FileEditInput`/
   `FileWriteInput` both use `file_path`, matching the existing PostToolUse
   hook's assumption.

The hook checks both `file_path` and `notebook_path` keys unconditionally
(not gated per `tool_name`) — over-inclusive is the safe direction for a
guard, per review.

## Design decisions

**Vault anchor is the resolved write target, not `cwd`.** The brief's own
sketch (mirroring `posttooluse_lint.py`) would have found the vault from
`cwd` and then checked the target path against it. Advisor review caught
that this is an evasion route for a *deny* hook: `cd /tmp`, then `Edit` with
an absolute path into `<vault>/literatures/x.md` — no `.harness` above
`/tmp`, silent allow, hand-written ack lands. Fixed: `_vault_from_target`
walks up from the **resolved candidate path's own parent directory**,
reusing the existing pure-stdlib `.harness`-walk technique (`os.lstat` +
`stat.S_ISDIR`, symlink-rejecting) already proven in both
`posttooluse_lint.py` and `stop_publish_gate.py`, just re-anchored. `cwd` is
used **only** to absolutize an already-relative candidate path; a relative
candidate with no usable `cwd` is left unresolved (skipped), never silently
resolved against the hook process's own ambient working directory. Pinned by
`test_pretooluse_denies_absolute_target_regardless_of_unrelated_cwd` (the
critical leak-fix test — confirmed red under the old cwd-anchored design,
see matrix) and `test_pretooluse_allows_relative_target_when_cwd_is_missing`
(confirmed red if the code falls back to `os.getcwd()`, even though that
ambient directory happens to be a real vault in the test).

**Failure posture (Controller fact #1) — three tiers, explicitly, not a
single blanket `suppress(Exception)`:**

1. Unparsable top-level stdin → silent, exit 0. Claude Code always sends
   well-formed JSON for a matched tool call, so this cannot be attributed to
   a real invocation; every hook in this repo (including the fail-closed
   `stop_publish_gate.py`) treats this identically.
2. Parsed payload but structurally not applicable (wrong `tool_name`, no
   `tool_input` dict, no string path key, no vault found, path outside the
   vault) → silent allow, via explicit `isinstance`/membership checks — no
   exception is raised or swallowed on this path.
3. **Any exception past parsing** (a bug, an `OSError` from path
   resolution, a monkeypatched fault) → `main()`'s own
   `try: _handle(payload) except Exception: _deny(FAIL_CLOSED_REASON)`
   denies with a reason string distinct from the machine-surface message,
   so tests (and a human reading the JSON) can tell "denied because machine
   surface" apart from "denied because the guard broke." This is the
   opposite of `posttooluse_lint.py`'s `main()` shape — deliberately, since
   that shape means "allow" for a warning surface and would mean "silent
   permission" for a deny surface.

**Deny message is the brief's line verbatim**, including backticks and the
ellipsis character, asserted as an exact string in every deny test (not a
substring check): `"machine surface; the CLI writes this — use the matching
verb (`finding`, `ack`, `import-note`, …)"`.

**Fixed path list, no vault import**: `MACHINE_SURFACE_DIR_NAMES =
{"literatures", "log"}` (prefix match via `relative.parts[0]`) and
`MACHINE_SURFACE_FILES = {Path("log.md"), Path("inbox/review-queue.md"),
Path("system/bibliography.json")}` (exact match — root `log.md` added in
fix round 1, see below). No import of `knowledge_harness` anywhere in the
module, lazy or otherwise.

## §10 spec edit (Step 3)

Single-line, surgical replacement of the exact entry `PreToolUse blocking
for the citekey lint (revisit only on evidence that warnings fail,
staleness lint fixed first)` inside the giant §10 line — `git diff --stat`
confirms `1 insertion(+), 1 deletion(-)`, no reflow. New text: records the
trigger fired 2026-08-24, cites the 2c reproduction evidence verbatim
(in-format `log/`/`inbox/review-queue.md` appends pass the append-only
lint, draw no PostToolUse warning, get laundered by `okf.py` into root
`log.md`), records that blocking shipped for the machine-surface list via
`hooks/pretooluse_guard.py`, and explicitly keeps the citekey-lint
PreToolUse question (warn-vs-block for `[@citekey]` prose) separately
deferred under its original revisit criterion — this task did not touch
that question.

## Per-test discrimination matrix

Each row: production line mutated in `hooks/pretooluse_guard.py` (or an
entry removed from `hooks/hooks.json`), the named test(s) run, confirmed
red, then the file restored and `diff`-verified byte-identical to the
pre-mutation backup before moving to the next probe.

| Test | Mutation | Result |
|---|---|---|
| `test_pretooluse_denies_edit_into_every_machine_surface` (6 params: `literatures/clean.md`, `literatures/nested/note.md`, `log/2026-08-16.md`, `log/2026-01-01.md`, `inbox/review-queue.md`, `system/bibliography.json`) | `_is_machine_surface` → `return False` | RED, all 6 (silent allow instead of deny) |
| `test_pretooluse_allows_edit_outside_machine_surfaces` (3 params), `test_pretooluse_allows_notebookedit_outside_machine_surfaces` | `_is_machine_surface` → `return True` | RED, all 4 |
| `test_pretooluse_denies_write_creating_new_log_day_file` | tool-name set narrowed to `{"Edit", "NotebookEdit"}` (drop `"Write"`) | RED |
| `test_pretooluse_denies_notebookedit_into_literatures` | `TOOL_PATH_KEYS` narrowed to `("file_path",)` | RED |
| `test_pretooluse_resolves_relative_file_path_against_cwd` | `_resolve_candidate` returns `None` for any non-absolute candidate (cwd-absolutizing branch removed) | RED |
| `test_pretooluse_denies_symlink_that_resolves_into_machine_surface` | final `.resolve()` call dropped from `_resolve_candidate` (candidate returned unresolved) | RED |
| `test_pretooluse_denies_dotdot_traversal_into_machine_surface` | same "drop final `.resolve()`" mutation | **stayed GREEN** — not a discriminator of this line. The `os.lstat` walk in `_vault_from_target` resolves `..` at the syscall level regardless of whether `Path.resolve()` ran, and the specific fixture's lexical `..` happened to still line up correctly against the vault root string. Documented honestly as a regression guard for `..`-shaped input, not a discriminator; the symlink test above is the real discriminator for the resolve-call line (symlink following genuinely requires it — confirmed empirically). |
| `test_pretooluse_denies_absolute_target_regardless_of_unrelated_cwd`, `test_pretooluse_denies_absolute_target_when_cwd_is_missing` | vault lookup reverted to the old (flawed) `cwd`-anchored design: `vault = _vault_from_target(Path(cwd).resolve()) if cwd else None` | RED, both — reproduces the cwd-evasion leak the advisor caught, confirming the fix is load-bearing |
| `test_pretooluse_allows_relative_target_when_cwd_is_missing` | `_resolve_candidate` falls back to bare `Path(raw).resolve()` (uses the process's ambient `os.getcwd()`, which happens to be `fixture_vault` in the test harness) instead of returning `None` | RED — the relative `literatures/clean.md` then resolves against the real vault and denies, proving the correct code path does NOT trust ambient cwd |
| `test_pretooluse_is_silent_for_missing_tool_input` | `if not isinstance(tool_input, dict): return` guard removed | RED — `tool_input=None` reaches `_candidate_paths`, `AttributeError` propagates, fails closed (deny) instead of silent allow |
| `test_pretooluse_is_silent_for_non_string_file_path` | `isinstance(..., str)` filter removed from `_candidate_paths` | RED — `Path(1)` raises `TypeError`, fails closed instead of silent allow |
| `test_pretooluse_is_silent_for_unmatched_tool_names` (3 params: Bash, Read, Grep) | tool-name membership check removed entirely | RED, all 3 |
| `test_pretooluse_is_silent_for_malformed_input` | outer `try/except` around `json.load(sys.stdin)` removed | RED — uncaught `JSONDecodeError`, nonzero exit and stderr instead of silent exit 0 |
| `test_pretooluse_fails_closed_on_unexpected_exception` | outer `try: _handle(payload) except Exception: _deny(...)` removed from `main()` | RED — the monkeypatched `RuntimeError` propagates out of `hook.main()` uncaught instead of producing the fail-closed deny JSON |
| `test_pretooluse_allows_machine_surface_shaped_path_without_a_real_vault_marker` | `_vault_from_target` unconditionally returns `target.parent.parent` (no `.harness` check at all) | RED — a path merely shaped like `literatures/clean.md`, with no real vault anywhere, gets denied instead of allowed |
| `test_pretooluse_is_silent_outside_a_vault` | (same class of mutation as above) | Not independently re-run as a distinct discriminator — same underlying mechanism as the prior row; kept as a plain regression/sanity case (arbitrary path, no vault, no machine-surface-shaped name) |
| `test_stop_hooks_manifest_registers_posttooluse_and_stop_commands`, `test_stop_hook_manifest_commands_execute_from_plugin_path_with_spaces` | `"PreToolUse"` entry deleted from `hooks/hooks.json` | RED, both (`KeyError: 'PreToolUse'` for the second, dict-inequality for the first) |
| `test_pretooluse_denies_edit_into_every_machine_surface[relative4]` (`log.md`) | `Path("log.md")` removed from `MACHINE_SURFACE_FILES` | RED on exactly that one param; the other six stayed green (confirms the addition is isolated, not accidentally coupled to the existing entries) |
| `test_pretooluse_allows_edit_outside_machine_surfaces[relative4]` (`projects/brief/log.md`, the root-only boundary) | `_is_machine_surface` widened to `relative.name == "log.md"` (matches a `log.md` anywhere, not just at vault root) | RED |
| `test_pretooluse_allows_edit_outside_machine_surfaces[relative3]` (`projects/brief/search-log.md`) and `[relative4]` | `_is_machine_surface` widened to `relative.name.endswith("log.md")` | RED, both — `search-log.md` needs its own suffix-based mutation to discriminate (the exact-name mutation above doesn't touch it, correctly, since `search-log.md` ≠ `log.md`) |
| `test_pretooluse_is_silent_for_parseable_non_dict_payload` (fix round 1, Concern 5a) | `if not isinstance(payload, dict): return` guard removed from `_handle` | RED — `[].get(...)` raises `AttributeError`, fails closed instead of silent allow |
| `test_pretooluse_allows_relative_target_when_declared_cwd_is_itself_relative` (fix round 1, Concern 5b) | `not Path(cwd).is_absolute()` clause dropped from `_resolve_candidate` (kept only `cwd is None`) | RED — a relative `cwd` ("literatures") plus relative `file_path` ("clean.md") then resolves through `Path.resolve()`'s implicit `os.getcwd()` fallback, landing in the real vault at `fixture_vault/literatures/clean.md`, and denies instead of staying unresolved |

Every new production branch has at least one test that goes red when it is
removed or weakened, with one documented exception: mutating the same
`.resolve()` call it is meant to pin
(`test_pretooluse_denies_dotdot_traversal_into_machine_surface`) does not
turn it red, for the reason given in that row and in Concern 3 below. That
sentence in the original version of this report claimed the property held
for *every* branch without qualification — an overclaim caught on
self-review after the commit landed (Concern 5, fix round 1) and corrected
here rather than left standing.

## Concerns

1. ~~Root `log.md` is not in the deny list.~~ **RESOLVED in fix round 1**
   (author ruling 2026-08-24, brief regenerated, plan commit `3c73676`):
   `log.md` (root only) is now on `MACHINE_SURFACE_FILES`. See the fix-round
   section below.
2. **`research/prior-art/trust-gates-prior-art.md:47` claims a `permissionDecision`
   value of `defer`** (precedence `deny > defer > ask > allow`) that the
   current official docs (cited above) do not list — only `allow`/`deny`/`ask`
   exist there. I trusted the live docs over the frozen prior-art note, per
   the brief's own instruction to verify rather than guess. Destination:
   recorded decline to edit — `research/prior-art/` is a frozen research
   record of a point-in-time investigation, not a living spec; not
   corrected here, noted for awareness only.
3. **The dotdot-traversal test is a regression guard, not a discriminator**
   of the `.resolve()` call it was originally written to pin (see matrix
   above) — the `os.lstat`-based vault walk already resolves `..` at the
   syscall level independently of `Path.resolve()`. Left in place as a
   correctness pin (the behavior it asserts is still real and desired), just
   documented honestly rather than mis-labeled.
4. **Pre-existing `ruff check`/`ruff format` findings under
   `skills/find-sources/scripts/`** (10 check errors, 5 files needing
   format) are unrelated to this task — confirmed identical before and
   after my change via `git stash`. Destination: already tracked, Task 2e
   Step 1 of this same plan (`docs/superpowers/plans/2026-08-22-post-q-batch.md`)
   owns the explicit vendor-exclusion fix.
5. **The `log.md` ruling leaves a one-direction residue: `system/bibliography.json`
   has no matching preamble warning.** Task 2c's vault AGENTS.md preamble
   (`knowledge_harness/templates/vault/AGENTS.md:6`) reads: `` `literatures/`,
   `log/`, `log.md`, and `inbox/review-queue.md` are machine-written `` — it
   does not name `system/bibliography.json`, so an agent that reads only the
   preamble gets no advance warning before hitting that specific deny. The
   guard being stricter than the doc it's paired with is tolerable (the deny
   fires regardless, and the message names the legal route), but not
   silence-worthy. Not fixed here — re-pinning a whole-file template inside a
   task that did not scope that edit is exactly what this fix round's ruling
   on scope declined. Destination: preamble gains `system/bibliography.json`
   at the next legitimate template re-pin; a GitHub issue if no re-pin lands
   before batch close.

## Fix round 1 (response to coordinator review of commit `a2b829d`)

Three items, addressed without amending `a2b829d` — corrected forward with a
new commit per instruction.

**Item 1 — root `log.md` joins the deny list (author ruling 2026-08-24,
brief regenerated, plan corrected at `3c73676`).** Added `Path("log.md")` to
`MACHINE_SURFACE_FILES` (exact match, so it is root-only by construction —
a deeper `log.md` or `search-log.md` cannot match it). Extended the deny
parametrization with the `log.md` case and confirmed it discriminates: with
the entry removed, exactly that one param goes red and the other six stay
green (matrix above). Added two boundary cases to the allow
parametrization — `projects/brief/search-log.md` (`searchlog.py`'s actual
output path — not on the list) and `projects/brief/log.md` (a nested
`log.md`, testing the "root-only" boundary explicitly) — and confirmed each
discriminates against a plausible over-broad matcher (`relative.name ==
"log.md"` catches the nested case; `relative.name.endswith("log.md")` also
catches `search-log.md`), per the matrix above.

**Item 2 — Concern 5, applied exactly as pre-specified:**
- (a) `test_pretooluse_is_silent_for_parseable_non_dict_payload` feeds
  `json.dumps([])` and asserts silence, covering
  `if not isinstance(payload, dict): return`. Confirmed red with the guard
  removed (matrix above).
- (b) `test_pretooluse_allows_relative_target_when_declared_cwd_is_itself_relative`
  feeds a present-but-relative `cwd` (`"literatures"`) alongside a relative
  `file_path` (`"clean.md"`), covering `not Path(cwd).is_absolute()` in
  `_resolve_candidate`. Confirmed red with the clause dropped (matrix
  above) — the mutant falls through to `Path.resolve()`'s implicit
  `os.getcwd()` behavior and lands in the real vault.
- (c) Re-examined `except ValueError: continue` around
  `resolved.relative_to(vault)`. Confirmed unreachable by construction: in
  `_vault_from_target`, every candidate `vault` is drawn from
  `(target.parent, *target.parent.parents)` — `target` here is always the
  same object as `resolved` at the call site, so `vault` is always one of
  `resolved`'s own ancestors, and `relative_to` cannot raise on a genuine
  ancestor. Deleted the `try/except`, left a one-line comment stating the
  invariant (the constraint the code's shape alone doesn't show), and ran
  the full suite green with it gone — no test depended on the swallow.
- (d) The blanket "every branch" sentence in the discrimination-matrix
  section is corrected above to name the one documented exception rather
  than claim universality.

**Item 3 — the `log.md` ruling's rider, recorded as Concern 5** (the
`system/bibliography.json`/preamble asymmetry) — see Concerns above. No code
or template change made for it in this task, per the ruling's own scope
line.

Concerns 2, 3, and 4 from the original report stand unchanged, as directed.

**Gates, re-run after all of the above:** full suite 1682 passed, 7 skipped
(1650 baseline + 32 in `test_hooks.py`, up from 27). `ruff check .` and
`ruff format --check .`: same five pre-existing vendored-fork findings
under `skills/find-sources/scripts/`, nothing new. `mypy knowledge_harness/`:
clean, 27 files. `echo '{}' | python hooks/stop_publish_gate.py`: silent,
exit 0. `tests/test_hooks.py:445`'s `hooks.json` exact-equality pin re-run
unchanged (this round touched no manifest content) and still passes.
