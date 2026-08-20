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

Add `doctor(vault_root, client=None, network=True, settle_seconds=60, poll_interval=1) -> list[Probe]` and the CLI verb. Preserve the probe order: tree, machine-config, zotero, bbt, autoexport, staleness, remote, backup, inbox.

Replace the existing import path that calls `bibliography.write_and_commit(vault, client.export_csl(None))`. Doctor and `import-note` must share one observation boundary for the registered auto-export: an on-demand export may be held in memory only as comparison evidence; BBT alone writes `x/bibliography.json`. `import-note` waits for the actual target to settle and match that evidence before it treats the bibliography as refreshed. The harness may then stage and commit exactly the observed target file, but it must never synthesize or write the export bytes. A timeout or mismatch fails explicitly instead of manufacturing a bibliography.

Auto-export algorithm:

1. Read BBT's actual target file and compare it with the on-demand export in memory.
2. If absent or mismatched, wait and poll for up to 60 seconds for genuine BBT output.
3. Only after a persistent mismatch, call `register_autoexport(target)` once.
4. Wait and poll again, then verify the file matches.
5. Record UNMATCHED/UNREACHABLE on failure. Never call a bibliography writer to manufacture the target.
6. When BBT changes the file, the harness may stage that exact file and commit it with `--no-verify`; no other path enters that bookkeeping commit.

`doctor --base URL --vault PATH` and `--base URL doctor --vault PATH` must both route the same URL into `ZoteroClient`. Keep the existing common-parent parser contract for all verbs.

RED tests in `test_doctor.py` use an injected fake poller/clock and prove: output arriving during the first wait prevents re-registration; persistent mismatch registers exactly once; post-registration mismatch remains a failure; the harness never writes export bytes; only genuine BBT output is committed; `--base` works before and after the verb; hard/warn probe exit classes remain correct.

Add import regressions in `test_cli_live.py` with the same injected observation boundary. Prove that `import-note` never invokes a bibliography writer or writes the in-memory comparison bytes, waits for a fake BBT actor to create the target, and stages/commits only those genuine target bytes. Cover the NOOP-note case, successful delayed output, timeout/mismatch, and an unrelated staged/unstaged/untracked file; the auto-export bookkeeping commit must contain only `x/bibliography.json` and must leave unrelated index/worktree state untouched.

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
