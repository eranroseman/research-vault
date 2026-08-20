# Plan C: Vault Scaffold + Enforcement Surfaces — Implementation Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` or `superpowers:executing-plans`; follow RED → GREEN in every task and commit only after the task's focused tests pass.

**Goal:** Ship a one-command OKF v0.2 vault scaffold, a doctor that verifies and repairs the Zotero/BBT substrate, and the pre-commit, CI, PostToolUse, and armed Stop enforcement surfaces defined by the foundation spec.

**Authority:** `docs/specs/2026-08-16-foundation-spec.md` and `docs/terminology.md` govern. As-built HEAD governs implementation details that this plan does not expressly change. Vendored Claude Code hook documentation governs hook input/output shapes.

**Stack:** Python 3.10+ stdlib, package resources, Git/GitHub Actions, and plugin `hooks/hooks.json`.

## Global contracts

- Final vault roots are `inbox`, `literatures`, `synthesis`, `log`, `projects`, `x/templates`, and `x/bases`.
- Root `index.md` has exactly `okf_version: "0.2"` frontmatter. Root `log.md` and every nested basename `index.md` or `log.md` have no frontmatter. Every other packaged concept Markdown file has parseable frontmatter and a non-empty `type`.
- `inbox/review-queue.md` begins with exactly `type: "review-inbox"`; daily notes use exactly `type: "daily"`. Inbox and daily-note bodies are append-only and never receive `generated` updates.
- Git path handling stays byte-preserving and NUL-delimited. No task may decode, newline-split, or lossy-normalize Git path output.
- Detection, verified pass events, current failure projection, markers, and inbox auditing are independent of enforcement surface. Surface sets decide blocking only.
- Synthetic `--offline` network outcomes may be printed in an explicit report but never change trust, events, markers, or inbox state. A genuinely attempted outage remains persisted as UNREACHABLE.
- `COMMIT_CLOSING = {"citekey", "evidence-layer"}`. `PUBLISH_CLOSING = {"citekey", "evidence-layer", "quote", "update-notice", "doi"}`. Exit 1 means a closing UNMATCHED; exit 3 means UNREACHABLE.
- BBT is the sole writer of `x/bibliography.json` after auto-export registration. The harness may stage and commit genuine BBT output; it never synthesizes or writes that export.
- The scaffold stages and commits only paths it created. It must not sweep unrelated staged, unstaged, or untracked work.
- `--with-ci` installs only read-only verification. `--with-rw-ci` is the distinct explicit consent for the scheduled write-capable workflow.
- Work in an isolated worktree. Run commands from `core/` unless stated otherwise.

## File structure

```text
core/harness_core/
├── templates/
│   ├── vault/
│   │   ├── index.md
│   │   ├── log.md
│   │   ├── AGENTS.md
│   │   ├── gitignore
│   │   ├── inbox/review-queue.md
│   │   ├── synthesis/index.md
│   │   └── x/
│   │       ├── templates/{literature,synthesis,project,daily}.md
│   │       └── bases/{open-questions,trust-tier}.base
│   ├── harness/machine.json.example
│   ├── git/pre-commit
│   └── ci/{verify.yml,rw-batch.yml}
├── scaffold.py
└── __main__.py
hooks/{hooks.json,posttooluse_lint.py,stop_publish_gate.py}
skills/setup-vault/SKILL.md
core/tests/{test_templates,test_scaffold,test_doctor,test_precommit,test_ci_templates,test_hooks,test_scaffold_live}.py
```

## Task 1: Package the OKF vault templates

Create the template tree and package it through `core/pyproject.toml`. The canonical Markdown content is:

```markdown
<!-- vault/index.md -->
---
okf_version: "0.2"
---
# Knowledge bundle

<!-- vault/log.md: reserved; no frontmatter -->
# Log

<!-- vault/AGENTS.md -->
---
type: "vault-guide"
---
# Vault agents guide

Evidence is admitted through Zotero and projected into `literatures/`. Read `synthesis/index.md` and recent `log/` entries before editing. Use the knowledge-harness `project`, `verify-citations`, and `publish` skills for delivery work. Review findings live in `inbox/review-queue.md`.

<!-- vault/inbox/review-queue.md -->
---
type: "review-inbox"
---

<!-- vault/synthesis/index.md: reserved; no frontmatter -->
# Synthesis index

<!-- vault/x/templates/literature.md -->
---
citekey: "{{CITEKEY}}"
type: "literature"
accessed: "{{TODAY}}"
fixity-sha256:
status: "unscreened"
generated: {by: "{{ACTOR}}", at: "{{NOW}}"}
---
%%hk-managed%%
# {{TITLE}}
%%/hk-managed%%

## Notes

<!-- vault/x/templates/synthesis.md -->
---
title: "{{TITLE}}"
type: "synthesis"
status: "draft"
generated: {by: "{{ACTOR}}", at: "{{NOW}}"}
---

<!-- vault/x/templates/project.md -->
---
title: "{{TITLE}}"
type: "project"
status: "draft"
generated: {by: "{{ACTOR}}", at: "{{NOW}}"}
---

<!-- vault/x/templates/daily.md -->
---
type: "daily"
---
<!-- log/YYYY-MM-DD.md; append-only -->
```

Package these remaining canonical assets exactly as shown:

```yaml
# vault/x/bases/open-questions.base
views:
  - type: table
    name: Open questions
filters:
  and:
    - 'type == "synthesis"'
formulas:
  open_q: 'file.content.contains("(open-question)")'
```

```yaml
# vault/x/bases/trust-tier.base
views:
  - type: table
    name: Trust tier
filters:
  and:
    - 'type == "literature"'
```

```gitignore
# vault/gitignore; scaffold copies this to .gitignore
.harness/
.obsidian/workspace*
```

```json
// harness/machine.json.example (this comment is not file content)
{
  "mailto": "you@example.edu",
  "path_map": {"D:\\Zotero\\": "/mnt/d/Zotero/"}
}
```

```sh
#!/bin/sh
# git/pre-commit
# knowledge-harness pre-commit: offline commit-closing checks.
# Bypass: git commit --no-verify. CI replays the same checks.
vault="$(git rev-parse --show-toplevel)" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "pre-commit: python3 unavailable; refusing an unverifiable commit." >&2
  exit 1
fi
if ! python3 -c "import harness_core" 2>/dev/null; then
  echo "pre-commit: harness_core is not importable; CI will replay verification." >&2
  exit 0
fi

python3 -m harness_core verify --vault "$vault" --offline --surface commit --git-base HEAD
code=$?
case "$code" in
  0) exit 0 ;;
  1)
    echo "pre-commit: commit-closing verification failed." >&2
    echo "Bypass with --no-verify; CI will replay these checks." >&2
    exit 1
    ;;
  3)
    echo "pre-commit: verification unreachable; leaving commit open for CI replay." >&2
    exit 0
    ;;
  *)
    echo "pre-commit: verifier exited unexpectedly with status $code." >&2
    exit "$code"
    ;;
esac
```

```yaml
# ci/verify.yml
name: verify
on: [push, pull_request]

permissions:
  contents: read

jobs:
  offline-verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install harness
        run: python -m pip install "harness-core @ git+https://github.com/eranroseman/knowledge-harness.git#subdirectory=core"
      - name: Resolve and fetch comparison base
        id: base
        shell: bash
        env:
          EVENT_NAME: ${{ github.event_name }}
          PR_BASE: ${{ github.event.pull_request.base.sha }}
          PUSH_BASE: ${{ github.event.before }}
        run: |
          set -euo pipefail
          zero=0000000000000000000000000000000000000000
          empty_tree="$(git hash-object -t tree /dev/null)"
          if [[ "$EVENT_NAME" == "pull_request" ]]; then
            base="$PR_BASE"
          elif [[ -n "$PUSH_BASE" && "$PUSH_BASE" != "$zero" ]]; then
            base="$PUSH_BASE"
          else
            base="$empty_tree"
          fi
          if [[ "$base" != "$empty_tree" ]]; then
            git fetch --no-tags origin "$base"
          fi
          printf 'sha=%s\n' "$base" >> "$GITHUB_OUTPUT"
      - name: Verify committed changes
        shell: bash
        run: |
          set +e
          python -m harness_core verify --vault . --offline --surface commit --git-base "${{ steps.base.outputs.sha }}"
          code=$?
          set -e
          case "$code" in
            0) exit 0 ;;
            1) exit 1 ;;
            3)
              echo "::warning::verification unreachable; no closing mismatch reported"
              exit 0
              ;;
            *)
              echo "::error::verifier exited unexpectedly with status $code"
              exit "$code"
              ;;
          esac
```

```yaml
# ci/rw-batch.yml
name: rw-batch
on:
  schedule:
    - cron: "17 3 * * *"
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  retraction-batch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install harness
        run: python -m pip install "harness-core @ git+https://github.com/eranroseman/knowledge-harness.git#subdirectory=core"
      - name: Download Retraction Watch CSV
        run: curl --fail --show-error --location --output "$RUNNER_TEMP/rw.csv" https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv
      - name: Run CSV-only audit
        shell: bash
        run: |
          set +e
          python -m harness_core verify --vault . --offline --rw-csv "$RUNNER_TEMP/rw.csv" --changed-paths-file "$RUNNER_TEMP/harness-changed-paths"
          code=$?
          set -e
          case "$code" in
            0|1) exit 0 ;;
            *)
              echo "::error::CSV audit exited unexpectedly with status $code"
              exit "$code"
              ;;
          esac
      - name: Commit exact verifier-owned outputs
        shell: bash
        run: |
          set -euo pipefail
          manifest="$RUNNER_TEMP/harness-changed-paths"
          if [[ ! -s "$manifest" ]]; then
            echo "No verifier-owned changes."
            exit 0
          fi
          git config user.name "harness-ci"
          git config user.email "actions@users.noreply.github.com"
          git --literal-pathspecs add --pathspec-from-file="$manifest" --pathspec-file-nul
          git --literal-pathspecs commit --only -m "chore: rw-batch findings" --pathspec-from-file="$manifest" --pathspec-file-nul
          git push
```

Task 1 is the single owner of these packaged bytes: it writes and packages them once. Tasks 3–4 implement the runtime interfaces that drive them and verify their behavior; they do not rewrite the templates unless a failing test exposes a defect and the correction receives explicit review.

RED tests in `test_templates.py` must enumerate every packaged path, including both Bases files and all five operational assets above. Parse every non-reserved Markdown file and assert non-empty `type`; assert root index frontmatter equals `{"okf_version": "0.2"}`; assert root log and all nested indexes have no frontmatter; assert the inbox header is exactly the required type; and assert the daily template uses exactly `type: "daily"`.

The same tests must parse both `.base` files enough to prove their exact type filters; parse `machine.json.example` as JSON and assert the `mailto` and `path_map` shapes; assert `gitignore` contains both canonical entries; run `sh -n` on `git/pre-commit`, assert its executable bit, and assert the exact verify command, exit-1 block, exit-3 open path, import-only fail-open path, `--no-verify`, and CI replay text. For each workflow, assert the event/permission boundary and the exact commands above. In particular, prove `verify.yml` fetches and passes an explicit base and handles 0/1/3/unexpected exits; prove `rw-batch.yml` uses the required curl flags, performs only the offline CSV leg, passes `--changed-paths-file`, handles an empty manifest, and uses literal NUL-safe `add` plus `commit --only` with no `|| true`.

Run: `python -m pytest tests/test_templates.py -v`.

Commit: `feat: package OKF vault templates`.

## Task 2: Implement the scaffold verb without sweeping user work

Create `scaffold.py` with:

```python
VAULT_DIRS = [
    "inbox", "literatures", "synthesis", "log", "projects",
    "x/templates", "x/bases",
]

def scaffold_vault(dest, with_ci=False, with_rw_ci=False) -> list[str]: ...
```

`scaffold_vault` copies only absent template paths, installs an executable pre-commit hook, creates `.harness/machine.json` only when absent, and initializes Git when necessary. `with_ci` copies only `verify.yml`; `with_rw_ci` copies `rw-batch.yml` and is never implied by `with_ci`.

When a commit is needed, resolve the exact created, trackable paths; stage only those paths with explicit `--` separation; and commit only those paths. Never use `git add -A`, a broad directory pathspec, or an unresolved glob. Preserve any unrelated index entries and all unrelated working-tree bytes.

Expose `scaffold --vault PATH [--with-ci] [--with-rw-ci]`. Its output is the list of paths created.

RED tests in `test_scaffold.py` must cover fresh output, all roots, root reserved files, typed concepts, idempotence, non-overwrite behavior, executable hook, empty-directory survival, independent CI flags, and a pre-existing repository with unrelated staged/unstaged/untracked changes. Assert the scaffold commit contains only created paths and the user's staged entry remains staged afterward.

Run: `python -m pytest tests/test_scaffold.py -v`.

Commit: `feat: add scoped OKF vault scaffold`.

## Task 3: Make doctor and import observe genuine BBT auto-export output

**Files:**

- Modify: `core/harness_core/scaffold.py`, `core/harness_core/bibliography.py`, and `core/harness_core/__main__.py`.
- Create: `core/tests/test_doctor.py`.
- Modify: `core/tests/test_bibliography.py` and `core/tests/test_cli_live.py`.

**Interfaces:**

- Replace Plan A's interim `bibliography.write_and_commit(vault_root, items)` writer with `bibliography.commit_autoexport(vault_root) -> bool`. The replacement accepts no export payload and never writes the target. When the target differs from HEAD, it stages only `x/bibliography.json` and commits with the exact target-only shape `git commit -q --no-verify --only -m "chore: bibliography export" -- x/bibliography.json`; it returns whether it committed.
- Add `AutoexportObservation = (result, detail, staleness, staleness_detail)`, where both result fields are `Result` values and both detail fields are strings. Add one shared `bibliography.observe_autoexport(vault_root, client, *, settle_seconds=60, poll_interval=1, monotonic=None, sleep=None) -> AutoexportObservation`; doctor and `import-note` both call it. The optional clock and sleeper are injection seams; `None` selects the real monotonic clock and sleeper. Reject `poll_interval <= 0` before polling.

Add `doctor(vault_root, client=None, network=True, settle_seconds=60, poll_interval=1) -> list[Probe]` and the CLI verb. `Probe = (name, Result, detail)`, with a string name, a `MATCHED | UNMATCHED | UNREACHABLE | SKIPPED` result, and a human-readable string detail. Return exactly these probes in this order and with these meanings:

1. `tree`: every required directory exists: `inbox`, `literatures`, `synthesis`, `log`, `projects`, `x/templates`, and `x/bases`. Repair missing pieces through the scoped scaffold, then report MATCHED only when this exact tree is complete.
2. `machine-config`: `.harness/machine.json` is readable and its `mailto` value is present and differs from the packaged `you@example.edu` placeholder.
3. `zotero`: `client.ready()` succeeds; MATCHED detail includes the reported versions, and inability to reach or decode the service is UNREACHABLE.
4. `bbt`: the ready response contains a non-empty `betterbibtex` version; absence is UNMATCHED, while a failed ready call is UNREACHABLE. If `client.ready()` fails, do not call `observe_autoexport`: report `bbt`, `autoexport`, and `staleness` as UNREACHABLE, with the exact downstream detail `zotero down`, then continue with `remote`, `backup`, and `inbox` so the returned list still contains all nine probes in order. When Zotero is ready but this required BBT version is absent, do not attempt downstream BBT operations: report `autoexport` and `staleness` as SKIPPED with a missing-BBT prerequisite detail; the hard `bbt` UNMATCHED still exits 1.
5. `autoexport`: the sole-writer observation flow below proves that the genuine `x/bibliography.json` target matches the on-demand comparison export by Plan A's exact sorted `(id, title)` fingerprint. A persistent mismatch, invalid target, or BBT JSON-RPC rejection is UNMATCHED; an I/O, transport, or malformed-response failure is UNREACHABLE. Preserve `ZoteroError.result` and put the raw error text in detail. Missing BBT is the prerequisite SKIPPED case defined above, not a synthetic outage.
6. `staleness`: the post-observation sorted-`(id, title)` target-versus-on-demand comparison result. This is diagnostic and warn-only, including when it is UNREACHABLE; it is SKIPPED when BBT is the known missing prerequisite.
7. `remote`: the vault Git repository has a remote; otherwise report UNMATCHED with `no remote — vault endures only on this disk (§2)`.
8. `backup`: machine config contains a non-empty `zotero_backup`; otherwise report UNMATCHED with `no stated Zotero storage backup (§2 boundary)`.
9. `inbox`: `inbox.summary(vault)` has zero unacknowledged findings; otherwise report UNMATCHED and include the count and oldest date in detail.

The hard-UNMATCHED set is exactly `{"tree", "machine-config", "bbt", "autoexport"}`. The hard-UNREACHABLE set is exactly `{"zotero", "bbt", "autoexport"}`. The warn-only set is exactly `{"staleness", "remote", "backup", "inbox"}`; neither UNMATCHED nor UNREACHABLE from those probes changes the exit status. Print all probe lines to stdout in probe order. Prefix every warn-only UNMATCHED or UNREACHABLE line with the literal `warn:`. Exit 1 if any hard probe is UNMATCHED; otherwise exit 3 if any hard probe is UNREACHABLE; otherwise exit 0. `doctor --base URL --vault PATH` and `--base URL doctor --vault PATH` must both route the same URL into `ZoteroClient`; keep the common-parent parser contract used by the existing verbs.

The foundation spec defines synthetic offline behavior for verification, not for doctor. Keep `network=True` in the historical doctor interface, but Task 3 must not invent `network=False` probe results, mutations, output, or RED expectations.

Replace the existing import path that calls `bibliography.write_and_commit(vault, client.export_csl(None))`. Doctor and `import-note` must call the same auto-export observer and receive the same MATCHED/UNMATCHED/UNREACHABLE classification and detail. Fetch and validate the whole-library on-demand export exactly once per observation, retain it in memory only as comparison evidence, and reuse its fingerprint through both settle windows and the final staleness result; do not race the target against a second fresh export. Compare the actual target and that evidence by their sorted `(id, title)` fingerprints, so serialization and byte-layout differences do not make the bibliography stale. No doctor or import path may pass the on-demand payload or its serialized bytes to a file writer, replace the target, or otherwise synthesize `x/bibliography.json`; BBT remains its sole writer.

The shared observer performs this exact sequence:

1. Capture the current target state, obtain and validate the whole-library on-demand comparison export once, and retain its sorted `(id, title)` fingerprint for every later comparison in this observation.
2. If the target is absent, non-regular, readable but malformed/invalid, or fingerprint-mismatched, poll for genuine BBT output for one settle window of at most `settle_seconds` using `poll_interval`. Target I/O or Unicode failures are UNREACHABLE rather than mismatch. At the deadline, perform one final read and comparison before declaring the first window persistently mismatched.
3. If the first window ends with a persistent absence or mismatch, call `register_autoexport(str(target))` exactly once. Never register before that first window, and never retry registration in the same observation.
4. Poll for one second settle window with the same bounds and the same retained evidence. At its deadline, perform one final target read and comparison before deciding failure.
5. Require the final actual target to be a regular, valid Better CSL JSON file whose sorted `(id, title)` fingerprint matches the retained on-demand evidence. A persistent absence, non-regular target, readable malformed/invalid file, or fingerprint mismatch is UNMATCHED; target I/O/Unicode failure or inability to reach/decode the authoritative service is UNREACHABLE. Return this same final comparison as the observation's `staleness` result instead of making a second export request.
6. If the validated BBT target differs from HEAD, call `commit_autoexport`. Commit the target's bytes exactly as BBT wrote them, without reserialization or normalization. Its exact target-only commit uses `--no-verify`; no unrelated staged, unstaged, or untracked path may enter that bookkeeping commit or change state.

`import-note` invokes that observer before any note write or NOOP output, because another Zotero admission can change the bibliography while the rendered note remains identical. MATCHED continues the existing note write/NOOP path. UNMATCHED prints the observer detail to stderr, returns 1, and writes no note or comparison bytes. UNREACHABLE does the same and returns 3. Doctor reports `result`/`detail` through `autoexport` and the cached final `staleness`/`staleness_detail` through `staleness`; it makes no second on-demand export.

RED coverage is mandatory and exact:

- `test_doctor.py`: test `cmd_doctor`'s output/exit matrix by stubbing `doctor` or injecting explicit `Probe` tuples: all-MATCHED exits 0; each hard UNMATCHED (`tree`, `machine-config`, `bbt`, `autoexport`) exits 1; each hard UNREACHABLE (`zotero`, `bbt`, `autoexport`) exits 3; every warn-only probe as UNMATCHED and UNREACHABLE stays exit 0 and prints `warn:`; if hard UNMATCHED and hard UNREACHABLE coexist, exit 1 wins. These CLI-routing cases do not add states to any probe producer.
- `test_doctor.py`: test producer classifications separately through the concrete conditions in the probe meanings. Assert tuple shape and exact nine-probe order. A failed `client.ready()` must not call `observe_autoexport` and must return, in order, `zotero`, `bbt`, `autoexport`, and `staleness` as UNREACHABLE; the latter three details are exactly `zotero down`, and the full list continues through `remote`, `backup`, and `inbox`. Missing BBT makes `bbt` UNMATCHED and makes `autoexport`/`staleness` prerequisite-SKIPPED without downstream calls; output arriving during the first settle window prevents registration; a persistent mismatch causes exactly one registration; output arriving during the second window passes; a post-registration absence, invalid target, or mismatch remains UNMATCHED; transport/read failures remain UNREACHABLE; raw BBT errors reach detail.
- `test_doctor.py`: monkeypatch the old bibliography writer to fail if called and prove the harness never writes the in-memory export bytes; prove only BBT-created target bytes are staged and committed, the commit uses `--no-verify`, its changed-path set contains only `x/bibliography.json`, and unrelated staged, unstaged, and untracked state is byte-for-byte unchanged.
- `test_doctor.py`: both legal `--base` positions construct `ZoteroClient` with the supplied URL.
- `test_bibliography.py`: deterministic fake clock/poller coverage for both settle windows, `poll_interval <= 0`, a target appearing on each final-deadline read, exactly one fresh-evidence fetch reused through both windows and final staleness, the exact sorted `(id, title)` comparator (including byte-different JSON that MATCHES), exact single-registration behavior, missing/non-regular/malformed versus I/O/Unicode classification, and byte-exact target-only commit behavior without real sleeping.
- `test_cli_live.py`: patch the shared observer, not a duplicate import-only implementation. Cover note NOOP while the observer still runs, delayed genuine BBT output, UNMATCHED timeout/mismatch returning 1, UNREACHABLE returning 3, no note write on either failure, and no call to the old bibliography writer or write of comparison bytes.
- `test_cli_live.py`: with unrelated staged, unstaged, and untracked files present, the bookkeeping commit contains only genuine `x/bibliography.json` bytes and preserves every unrelated index/worktree byte and status.

Run: `python -m pytest tests/test_doctor.py tests/test_bibliography.py tests/test_verify_cli.py tests/test_cli_live.py -m 'not live and not live_net' -v`.

Commit: `feat: add BBT-owned doctor and import flow`.

## Task 4: Implement verification witnesses, pre-commit, and CI authority split

Extend the deterministic core and templates in one TDD sequence.

### Managed-region witness

- `managed-sha256` hashes the exact bytes between and including the managed delimiters.
- Rendering updates it only when those exact bytes change.
- Current-file verification detects a stale or forged witness.
- Pre-commit compares current files with HEAD using byte-preserving Git reads.
- CI requires `--git-base REV`; the workflow fetches and passes an explicit base. Detection covers committed edits, deletions, and renames.
- Renames and unusual path bytes are carried through NUL-delimited byte APIs; regression tests include spaces, non-ASCII, and a delete/rename.

### State and surfaces

- Refactor collection from enforcement: collect once, project current failures/events/markers/inbox once, then apply the selected closing set.
- Run the same fixture through commit and publish surfaces and assert identical raw outcomes and mutations but different blocking decisions.
- For `--offline`, network-disabled outcomes may be present in JSON output, but compare the complete vault bytes before/after and assert no trust demotion, event, marker, or inbox write.
- A fake genuine network attempt that raises still persists UNREACHABLE.
- `--offline --rw-csv FILE` evaluates the CSV only; it does not invent a live registry leg.

### Exact verifier-owned output manifest

RW verification exposes `--changed-paths-file FILE`. After projecting verified/failure metadata, current markers, and inbox findings, the verifier writes a sorted, unique, NUL-delimited manifest of every repo-relative path whose bytes it changed. The exact allowed set is `inbox/review-queue.md` plus changed Markdown files under `literatures/`, `synthesis/`, and `projects/`; unchanged paths are absent. Reject absolute paths, `.`/`..` traversal, and any path outside that set. An allowed changed file missing from the manifest, or a manifest entry the verifier did not change, is an error.

Consumers stage and commit the complete manifest with literal NUL-safe path handling (`git --literal-pathspecs add --pathspec-from-file=FILE --pathspec-file-nul` and an exact-path `git commit --only` using the same manifest). They never use a broad pathspec, directory sweep, or `git add -A`. An empty manifest produces no commit. This interface must preserve unrelated staged, unstaged, and untracked changes.

### Workflow contracts

`verify.yml` is read-only. It fetches the explicit comparison base, runs offline commit verification, fails only on exit 1, and emits a GitHub warning while succeeding on exit 3.

`rw-batch.yml` exists only after `--with-rw-ci`. It uses `curl --fail --show-error --location`, fails loudly on installation/download/infrastructure errors, runs the CSV audit without a fabricated live leg, and stages/commits the verifier's exact complete changed-path manifest. This includes every changed verifier-owned note and `inbox/review-queue.md`, not merely the inbox. It never uses `|| true` around infrastructure or download steps.

The pre-commit hook runs `verify --offline --surface commit --git-base HEAD`, blocks exit 1, leaves exit 3 open, and documents `--no-verify` plus CI replay.

RED tests cover every bullet in `test_precommit.py`, `test_ci_templates.py`, `test_notes.py`, and `test_verify_cli.py`, including the root `log.md` versus `log/` path collision. A RW fixture must mutate verifier-owned metadata or markers in literature, synthesis, and project notes and append the inbox; assert that the manifest and commit contain all and only those outputs. Include unrelated staged, unstaged, and untracked changes, path names with spaces/non-ASCII, an empty run, a missing changed path, and an injected out-of-allowlist manifest entry.

Run: `python -m pytest tests/test_precommit.py tests/test_ci_templates.py tests/test_notes.py tests/test_verify_cli.py -v`.

Commit: `feat: add managed witness and CI verification surfaces`.

## Task 5: Add the PostToolUse warning hook

Create `hooks/posttooluse_lint.py` and register it later in Task 6. It reads the documented Edit/Write payload, locates the vault starting with `cwd` itself, and always exits 0. Internal errors are silent and fail open.

For any LLM Edit/Write whose resolved vault-relative path is under `literatures/`, emit an evidence-layer warning even when content checks are otherwise clean. For other concept paths, run the per-file offline checks and emit `hookSpecificOutput.additionalContext` only when findings exist. Synthetic offline network outcomes do not mutate the vault.

RED tests cover non-vault silence, clean non-evidence edits, every `literatures/` touch, malformed input, a checker exception, paths with spaces/non-ASCII, and the documented JSON shape.

Run: `python -m pytest tests/test_hooks.py -k posttooluse -v`.

Commit: `feat: add fail-open PostToolUse warnings`.

## Task 6: Add the armed Stop publish gate and hook manifest

Create `hooks/stop_publish_gate.py` and `hooks/hooks.json`. The flag contract is:

```json
{"project": "projects/brief", "vault": "/absolute/vault", "blocks": 0}
```

The hook starts vault discovery at `cwd` itself, is inert without `.harness/publish-pending.json`, and runs the shared publish surface when armed. Publish-closing UNMATCHED or any genuine UNREACHABLE blocks. Pass or an explicit bypass clears the flag; bypass appends a human-reasoned inbox record.

Use the hook payload's `stop_hook_active` field to make the bound genuinely consecutive. On a block, increment the stored count only when `stop_hook_active is true`; otherwise reset it to 1. A non-blocking intervening invocation clears/resets the run. At eight consecutive active blocks, stop blocking, leave the flag in place, and emit a visible system message.

Synthetic offline outcomes never block or mutate. Surface selection changes only the blocking decision; markers, events, current failure projection, and inbox auditing stay identical to direct verification.

RED tests cover inert/pass/block/bypass, exception fail-closed while armed, the `project` key/path, exact inbox records, seven versus eight consecutive active blocks, and reset after `stop_hook_active: false`.

Run: `python -m pytest tests/test_hooks.py -k stop -v`.

Commit: `feat: add bounded armed publish gate`.

## Task 7: Add the setup-vault skill and provisioning constants

Create `skills/setup-vault/SKILL.md` with frontmatter `name: setup-vault` and `disable-model-invocation: true`. The skill:

1. asks for the destination and whether read-only CI is wanted;
2. separately asks whether the scheduled write-capable RW workflow is wanted;
3. runs `python3 -m harness_core scaffold --vault PATH` with only the consented flags;
4. explains the exact created paths and never implies unrelated changes were committed;
5. runs doctor, showing the URL override both before and after the verb;
6. reports every probe, inbox count, and age;
7. performs detect → report → per-item consent → install/guide → verify for companions;
8. treats Zotero `.xpi` installs as human-only wizard steps.

Add the ruled `PROVISION_COMPANIONS` constant and tests for exact frontmatter, commands, separate CI consent, doctor routing, and human-only installs.

Run: `python -m pytest tests/test_skill_files.py -v`.

Commit: `feat: add setup-vault workflow`.

## Task 8: Run the live scaffold/doctor caveat discharge

Add `test_scaffold_live.py`, guarded by the existing live marker/environment convention. It scaffolds a temporary vault, invokes doctor against real Zotero/BBT, waits for genuine BBT output, imports one real item, verifies the bibliography and note, reruns to NOOP, and runs the offline suite.

Cleanup is part of the test contract, not a note: remove the exact auto-export registration created for the temporary path, require the BBT removal RPC to confirm that target, query registrations again and assert the target is absent, then remove the temporary vault. A human verifies the same target is absent in BBT preferences. Record the accepted add/remove signatures and confirmation in `docs/environment.md`.

Run:

```bash
HARNESS_LIVE=1 python -m pytest tests/test_scaffold_live.py -v
HARNESS_LIVE=1 HARNESS_LIVE_NET=1 python -m pytest tests -v
```

Do not transmit credentials merely to satisfy this gate. If the environment is not already authorized, defer the live run explicitly to this task.

Commit: `feat: verify live scaffold and BBT cleanup`.

## Task 9: Final acceptance and merge

Run from `core/`:

```bash
python -m pytest tests -m 'not live and not live_net' -q -p no:cacheprovider
python -m ruff format --check . --no-cache
python -m ruff check . --no-cache
```

Then run `git diff --check` and the scoped terminology scan from the repository root. Verify:

- all packaged paths and OKF exceptions match Task 1;
- scaffold commits only created paths;
- BBT alone writes the export; doctor waits/re-registers/verifies, and import waits/observes/commits genuine output;
- offline audits are non-mutating while genuine outages persist;
- managed witnesses cover current, HEAD, and explicit CI-base comparisons;
- detection/state projection is surface-independent;
- RW verification commits the exact complete verifier-owned output manifest without sweeping unrelated paths;
- `--with-ci` and `--with-rw-ci` remain separate authorities;
- the Stop bound is consecutive through `stop_hook_active`;
- exact live auto-export cleanup is confirmed;
- the required live gates pass or are explicitly deferred only for unavailable authorization.

Merge only after all nine task commits and acceptance evidence are present.

## Self-review

Tasks 1–2 own templates and scoped creation. Task 3 owns the BBT-writer boundary for doctor and import plus doctor routing. Task 4 owns managed witnesses, state/surface separation, the exact verifier-output manifest, pre-commit, and both CI contracts. Task 5 owns the unconditional literature-touch warning. Task 6 owns publish arming and the consecutive bound. Task 7 owns user consent. Task 8 owns real add/remove validation. No task depends on a trailing ruling block to override its snippets.
