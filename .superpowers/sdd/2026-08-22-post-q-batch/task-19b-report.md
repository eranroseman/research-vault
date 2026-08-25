# Task 19b report: PreToolUse deny guards machine surfaces

## Status

Complete. Steps 1–3 implemented and committed in one commit (Global
Constraints require the manifest pin and the hook to land together; the
brief's own Step 3 folds the spec edit and the suite/commit into the same
step).

## Commit

`feat: PreToolUse deny guards machine surfaces (trigger evidence: 2c reproduction)`

Files: `hooks/pretooluse_guard.py` (new), `hooks/hooks.json`,
`tests/test_hooks.py`,
`docs/superpowers/specs/2026-08-16-foundation-spec.md`,
`.superpowers/sdd/2026-08-22-post-q-batch/task-19b-report.md`.

## Test summary

Full suite: 1677 passed, 7 skipped (baseline 1650/7 + 27 new tests in
`test_hooks.py`). `ruff check .` and `ruff format --check .` show only the
five pre-existing vendored-fork findings under `skills/find-sources/scripts/`
(confirmed identical before and after my change via `git stash`; Task 2e
owns that explicit exclusion, not this task). `mypy knowledge_harness/`:
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
`MACHINE_SURFACE_FILES = {Path("inbox/review-queue.md"),
Path("system/bibliography.json")}` (exact match). No import of
`knowledge_harness` anywhere in the module, lazy or otherwise.

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

Every new production branch has at least one test that goes red when it is
removed or weakened; the one honest exception
(`test_pretooluse_denies_dotdot_traversal_into_machine_surface` against the
resolve-call mutation) is documented above rather than silently claimed as a
discriminator it isn't.

## Concerns

1. **Root `log.md` is not in the deny list.** Task 2c's vault AGENTS.md
   preamble and the `okf.py` laundering path both name root `log.md` as
   machine-written, but the brief's fixed path list is exactly four entries
   (`literatures/`, `log/`, `inbox/review-queue.md`,
   `system/bibliography.json`) and does not include it. Implemented the
   brief's list verbatim rather than unilaterally widening it. Destination:
   flagged here for the controller/next-task decision — not filed as a new
   GitHub issue or spec entry on my own authority, since the brief was
   explicit and I have no mandate to expand its scope.
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
