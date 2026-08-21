# Plan C: Vault Scaffold + Enforcement Surfaces — Implementation Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` or `superpowers:executing-plans`; follow RED → GREEN in every task and commit only after the task's focused tests pass.

**Goal:** Ship a one-command OKF v0.2 vault scaffold, a doctor that verifies and repairs the Zotero/BBT substrate, and the pre-commit, CI, PostToolUse, and armed Stop enforcement surfaces defined by the foundation spec.

**Authority:** `docs/specs/2026-08-16-foundation-spec.md` and `docs/terminology.md` govern. As-built HEAD governs implementation details that this plan does not expressly change. Vendored Claude Code hook documentation governs hook input/output shapes.

**Stack:** Python 3.10+ stdlib, package resources, Git/GitHub Actions, and plugin `hooks/hooks.json`.

## Global contracts

- Final vault roots are `inbox`, `literatures`, `synthesis`, `log`, `projects`, `x/templates`, and `x/bases`.
- Root `index.md` has exactly `okf_version: "0.2"` frontmatter. Root `log.md` and every nested basename `index.md` or `log.md` have no frontmatter. Every other packaged concept Markdown file has parseable frontmatter and a non-empty `type`.
- `inbox/review-queue.md` begins with exactly `type: "review-inbox"`; daily notes use exactly `type: "daily"`. Inbox and daily-note bodies are append-only and never receive `generated` updates.
- Raw Git path records and changed-path manifests stay byte-preserving and NUL-delimited; no task may newline-split or lossy-normalize them. Internal filesystem adapters may use `surrogateescape` only transiently with an exact byte round trip. Every path that crosses into an `Outcome`, inbox/ack identity, JSON, CSV, or diagnostic uses Task 4's canonical ASCII `path-bytes:` encoding; no surrogate code point may enter persisted or displayed text.
- Detection, verified pass events, current failure projection, markers, and inbox auditing are independent of enforcement surface. Surface sets decide blocking only.
- Synthetic `--offline` network outcomes may be printed in an explicit report but never change trust, events, markers, or inbox state. A genuinely attempted outage remains persisted as UNREACHABLE.
- `COMMIT_CLOSING = {"citekey", "evidence-layer"}`. `PUBLISH_CLOSING = {"citekey", "evidence-layer", "quote", "update-notice", "doi"}`. Exit 1 means a selected-surface closing UNMATCHED; explicit commit/publish surfaces use exit 3 for a genuine UNREACHABLE. The default open audit surface returns 0 for findings/outages and 2 only for operational or usage failure.
- BBT is the sole writer of `x/bibliography.json` after a human creates the whole-library auto-export in BBT Preferences. The harness may stage and commit genuine BBT output; it never synthesizes or writes that export, and it never registers an auto-export (author ruling 2026-08-20, Task 8: BBT 9.0.55's public `autoexport.add` is collection-scoped and rejects whole-library `//` before storage, so provisioning is a human wizard step).
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
managed-sha256: "{{MANAGED_SHA256}}"
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
if head="$(git rev-parse --verify HEAD 2>/dev/null)"; then
  git_base="$head"
else
  git_base="$(git hash-object -w -t tree /dev/null)" || exit 1
fi
git cat-file -e "$git_base^{tree}" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "pre-commit: python3 unavailable; refusing an unverifiable commit." >&2
  exit 1
fi
if ! python3 -c "import harness_core" 2>/dev/null; then
  echo "pre-commit: harness_core is not importable; CI will replay verification." >&2
  exit 0
fi

python3 -m harness_core verify --vault "$vault" --offline --surface commit --git-base "$git_base" --git-candidate index
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
          persist-credentials: false
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
          empty_tree="$(git hash-object -w -t tree /dev/null)"
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
          git cat-file -e "$base^{tree}"
          printf 'sha=%s\n' "$base" >> "$GITHUB_OUTPUT"
      - name: Verify committed changes
        shell: bash
        run: |
          set +e
          python -m harness_core verify --vault . --offline --surface commit --git-base "${{ steps.base.outputs.sha }}" --git-candidate HEAD
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
      - name: Run CSV-only audit and commit exact projection snapshot
        shell: bash
        run: |
          git config user.name "harness-ci"
          git config user.email "actions@users.noreply.github.com"
          set +e
          python -m harness_core verify --vault . --offline --surface audit --git-candidate worktree --rw-csv "$RUNNER_TEMP/rw.csv" --changed-paths-file "$RUNNER_TEMP/harness-changed-paths" --commit-projected "chore: rw-batch findings"
          code=$?
          set -e
          case "$code" in
            0) exit 0 ;;
            *)
              echo "::error::CSV audit exited unexpectedly with status $code"
              exit "$code"
              ;;
          esac
      - name: Push exact projection snapshot
        shell: bash
        run: |
          set -euo pipefail
          manifest="$RUNNER_TEMP/harness-changed-paths"
          if [[ ! -s "$manifest" ]]; then
            echo "No verifier-owned changes."
            exit 0
          fi
          git push
```

Task 1 is the single owner of these packaged bytes: it writes and packages them once. Task 4 must explicitly review and correct the already-packaged literature witness, pre-commit candidate, read-only CI candidate/credential, and RW audit commands above because its RED tests expose those defects; later work may not make unrelated template rewrites.

RED tests in `test_templates.py` must enumerate every packaged path, including both Bases files and all five operational assets above. Parse every non-reserved Markdown file and assert non-empty `type`; assert root index frontmatter equals `{"okf_version": "0.2"}`; assert root log and all nested indexes have no frontmatter; assert the inbox header is exactly the required type; and assert the daily template uses exactly `type: "daily"`.

The same tests must parse both `.base` files enough to prove their exact type filters; parse `machine.json.example` as JSON and assert the `mailto` and `path_map` shapes; assert `gitignore` contains both canonical entries; run `sh -n` on `git/pre-commit`, assert its executable bit, and assert the exact verify command, exit-1 block, exit-3 open path, import-only fail-open path, `--no-verify`, and CI replay text. For each workflow, assert the event/permission boundary and the exact commands above. In particular, prove the pre-commit hook resolves HEAD once, stores the empty-tree object on an unborn repository, verifies `"$git_base^{tree}"`, and passes `--git-candidate index`; prove `verify.yml` stores the empty-tree fallback, fetches and verifies an explicit base tree, passes `--git-candidate HEAD`, has read-only contents authority without persisted push credentials, and handles 0/1/3/unexpected exits; prove `rw-batch.yml` uses the required curl flags, performs only the offline CSV leg on the explicit open audit/worktree surface, accepts only verifier exit 0, rejects 1, 3, and every other status, passes `--changed-paths-file` and `--commit-projected`, handles a zero-byte manifest without a commit or push, pushes only the verifier-created snapshot commit, and contains no `git add`, pathspec commit, or `commit --only` path.

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

- Replace Plan A's interim `bibliography.write_and_commit(vault_root, items)` writer with `bibliography.commit_autoexport(vault_root, validated_bytes) -> bool`, where `validated_bytes` is the exact in-memory buffer read and validated by the observer. The replacement captures expected HEAD exactly once (a commit OID or the unborn state), never writes or rereads the target, and publishes one coordinated HEAD/live-index transaction that changes only the bibliography entry while preserving every unrelated index entry.
- Add `AutoexportObservation = (result, detail, staleness, staleness_detail)`, where both result fields are `Result` values and both detail fields are strings. Add one shared `bibliography.observe_autoexport(vault_root, client, *, settle_seconds=60, poll_interval=1, monotonic=None, sleep=None) -> AutoexportObservation`; doctor and `import-note` both call it. The optional clock and sleeper are injection seams; `None` selects the real monotonic clock and sleeper. Reject `poll_interval <= 0` before polling.

Add `doctor(vault_root, client=None, network=True, settle_seconds=60, poll_interval=1) -> list[Probe]` and the CLI verb. `Probe = (name, Result, detail)`, with a string name, a `MATCHED | UNMATCHED | UNREACHABLE | SKIPPED` result, and a human-readable string detail. Return exactly these probes in this order and with these meanings:

1. `tree`: every required directory exists: `inbox`, `literatures`, `synthesis`, `log`, `projects`, `x/templates`, and `x/bases`. Repair missing pieces through the scoped scaffold, then report MATCHED only when this exact tree is complete.
2. `machine-config`: `.harness/machine.json` is readable and its `mailto` value is present and differs from the packaged `you@example.edu` placeholder.
3. `zotero`: `client.ready()` succeeds; MATCHED detail includes the reported versions, and inability to reach or decode the service is UNREACHABLE.
4. `bbt`: the ready response contains a non-empty `betterbibtex` version; absence is UNMATCHED, while a failed ready call is UNREACHABLE. If `client.ready()` fails, do not call `observe_autoexport`: report `bbt`, `autoexport`, and `staleness` as UNREACHABLE, with the exact downstream detail `zotero down`, then continue with `remote`, `backup`, and `inbox` so the returned list still contains all nine probes in order. When Zotero is ready but this required BBT version is absent, do not attempt downstream BBT operations: report `autoexport` and `staleness` as SKIPPED with a missing-BBT prerequisite detail; the hard `bbt` UNMATCHED still exits 1.
5. `autoexport`: the sole-writer observation flow below proves that the genuine `x/bibliography.json` target matches the on-demand comparison export by Plan A's exact sorted `(id, title)` fingerprint. A persistent absence, persistent mismatch, invalid target, or BBT JSON-RPC rejection is UNMATCHED; an I/O, transport, or malformed-response failure is UNREACHABLE. The UNMATCHED detail is human-repair guidance: it names the exact `x/bibliography.json` target — in BBT's host path syntax through `paths.to_bbt_host` where that translation succeeds, otherwise the native absolute path — and states that a person must create or fix the whole-library Better CSL JSON auto-export in BBT Preferences. The harness never registers an auto-export. Preserve `ZoteroError.result` and put the raw error text in detail. Missing BBT is the prerequisite SKIPPED case defined above, not a synthetic outage.
6. `staleness`: the post-observation sorted-`(id, title)` target-versus-on-demand comparison result. This is diagnostic and warn-only, including when it is UNREACHABLE; it is SKIPPED when BBT is the known missing prerequisite.
7. `remote`: the vault Git repository has a remote; otherwise report UNMATCHED with `no remote — vault endures only on this disk (§2)`.
8. `backup`: machine config contains a non-empty `zotero_backup`; otherwise report UNMATCHED with `no stated Zotero storage backup (§2 boundary)`.
9. `inbox`: `inbox.summary(vault)` has zero unacknowledged findings; otherwise report UNMATCHED and include the count and oldest date in detail.

The hard-UNMATCHED set is exactly `{"tree", "machine-config", "bbt", "autoexport"}`. The hard-UNREACHABLE set is exactly `{"zotero", "bbt", "autoexport"}`. The warn-only set is exactly `{"staleness", "remote", "backup", "inbox"}`; neither UNMATCHED nor UNREACHABLE from those probes changes the exit status. Print all probe lines to stdout in probe order. Prefix every warn-only UNMATCHED or UNREACHABLE line with the literal `warn:`. Exit 1 if any hard probe is UNMATCHED; otherwise exit 3 if any hard probe is UNREACHABLE; otherwise exit 0. `doctor --base URL --vault PATH` and `--base URL doctor --vault PATH` must both route the same URL into `ZoteroClient`; keep the common-parent parser contract used by the existing verbs.

The foundation spec defines synthetic offline behavior for verification, not for doctor. Keep `network=True` in the historical doctor interface, but Task 3 must not invent `network=False` probe results, mutations, output, or RED expectations.

Replace the existing import path that calls `bibliography.write_and_commit(vault, client.export_csl(None))`. Doctor and `import-note` must call the same auto-export observer and receive the same MATCHED/UNMATCHED/UNREACHABLE classification and detail. Fetch and validate the whole-library on-demand export exactly once per observation, retain it in memory only as comparison evidence, and reuse its fingerprint through the settle window and the final staleness result; do not race the target against a second fresh export. Compare the actual target and that evidence by their sorted `(id, title)` fingerprints, so serialization and byte-layout differences do not make the bibliography stale. No doctor or import path may pass the on-demand payload or its serialized bytes to a file writer, replace the target, or otherwise synthesize `x/bibliography.json`; BBT remains its sole writer.

The shared observer performs this exact sequence:

1. Capture the current target state, obtain and validate the whole-library on-demand comparison export once, and retain its sorted `(id, title)` fingerprint for every later comparison in this observation.
2. If the target is absent, non-regular, readable but malformed/invalid, or fingerprint-mismatched, poll for genuine BBT output for one settle window of at most `settle_seconds` using `poll_interval`. Target I/O or Unicode failures are UNREACHABLE rather than mismatch. At the deadline, perform one final read and comparison before declaring the first window persistently mismatched.
3. There is no registration step and no second window: the observation closes on that first window's final comparison. No code path may call `autoexport.add` or any other `autoexport.*` JSON-RPC method.
4. Require the final actual target to be a regular, valid Better CSL JSON file whose sorted `(id, title)` fingerprint matches the retained on-demand evidence. A persistent absence, non-regular target, readable malformed/invalid file, or fingerprint mismatch is UNMATCHED; target I/O/Unicode failure or inability to reach/decode the authoritative service is UNREACHABLE. Return this same final comparison as the observation's `staleness` result instead of making a second export request.
5. Pass the exact validated in-memory target buffer to `commit_autoexport`, which performs this transaction:
   - Resolve expected HEAD once and return `False` when its bibliography blob already equals the supplied buffer. Otherwise write the buffer with `git hash-object -w --stdin`; build a temporary `GIT_INDEX_FILE` from expected HEAD, or an empty tree when unborn; update only `x/bibliography.json` to mode `100644` and that blob; and create a hook-free commit whose tree is exactly expected HEAD plus that one replacement.
   - Before moving HEAD, resolve the current worktree's standard live index with `git rev-parse --git-path index` and acquire that linked-worktree-specific `<index>.lock` with exclusive creation. Seed the lock from the complete live index, or from a valid empty index when it does not yet exist. Keep the lock through the HEAD compare-and-swap and index publication.
   - Read the locked index's `x/bibliography.json` entry. It must equal expected HEAD's entry, including matching absence: when present it is exactly one matching stage-0 mode/blob entry, and when HEAD is unborn it is absent. A pre-staged bibliography entry, conflict stages, or a concurrent bibliography stage that lands before lock acquisition fails without changing HEAD, the live index, or any worktree byte. Preserve every unrelated live-index entry byte-for-byte.
   - Update only the locked index's `x/bibliography.json` entry to the captured validated blob. Move HEAD with an expected-old compare-and-swap (`git update-ref HEAD <new> <expected-old>`, using Git's zero OID when unborn), then atomically publish the locked index over the live index. A concurrent HEAD move fails without overwriting it or publishing the locked index.
   - After a successful commit, an unchanged BBT target is clean because HEAD and the live index contain the captured blob. If BBT has written newer target bytes, HEAD and the live index still contain the captured blob and the newer worktree target remains an unstaged bibliography change for the next staleness pass. Never reread or write the target after validation; no unrelated staged, unstaged, or untracked path may enter the commit or change state.
   - Cleanup may unlink `<index>.lock` only while the path still names the same lock inode held by this process. If atomic publication removes that inode and a concurrent writer reacquires the lock path, preserve the successor lock.
   - If atomic index publication fails after the HEAD CAS, roll HEAD back by expected-old CAS to the exact expected parent, or delete the new ref to restore the unborn state. Preserve the original live index and worktree. If a concurrent writer moved HEAD after the forward CAS, the rollback CAS must fail rather than overwrite that writer; surface a clean combined publication/rollback failure. Unreachable temporary objects are acceptable.

The observer maps every lock, Git, publication, or rollback failure to UNREACHABLE with its detail. The former `git commit --only` transaction is superseded because it rereads the live worktree and cannot coordinate HEAD with the live index.

`import-note` invokes that observer before any note write or NOOP output, because another Zotero admission can change the bibliography while the rendered note remains identical. MATCHED continues the existing note write/NOOP path. UNMATCHED prints the observer detail to stderr, returns 1, and writes no note or comparison bytes. UNREACHABLE does the same and returns 3. Doctor reports `result`/`detail` through `autoexport` and the cached final `staleness`/`staleness_detail` through `staleness`; it makes no second on-demand export.

RED coverage is mandatory and exact:

- `test_doctor.py`: test `cmd_doctor`'s output/exit matrix by stubbing `doctor` or injecting explicit `Probe` tuples: all-MATCHED exits 0; each hard UNMATCHED (`tree`, `machine-config`, `bbt`, `autoexport`) exits 1; each hard UNREACHABLE (`zotero`, `bbt`, `autoexport`) exits 3; every warn-only probe as UNMATCHED and UNREACHABLE stays exit 0 and prints `warn:`; if hard UNMATCHED and hard UNREACHABLE coexist, exit 1 wins. These CLI-routing cases do not add states to any probe producer.
- `test_doctor.py`: test producer classifications separately through the concrete conditions in the probe meanings. Assert tuple shape and exact nine-probe order. A failed `client.ready()` must not call `observe_autoexport` and must return, in order, `zotero`, `bbt`, `autoexport`, and `staleness` as UNREACHABLE; the latter three details are exactly `zotero down`, and the full list continues through `remote`, `backup`, and `inbox`. Missing BBT makes `bbt` UNMATCHED and makes `autoexport`/`staleness` prerequisite-SKIPPED without downstream calls; output arriving during the settle window passes; a persistent absence, invalid target, or mismatch remains UNMATCHED and its detail carries the BBT Preferences repair guidance with the exact target; no observation issues any `autoexport.*` RPC; transport/read failures remain UNREACHABLE; raw BBT errors reach detail.
- `test_doctor.py`: monkeypatch the old bibliography writer to fail if called and prove the harness never writes the in-memory comparison export; prove the observer passes its exact validated BBT buffer into the snapshot commit, and that later BBT bytes remain for the next staleness pass rather than entering the current commit.
- `test_doctor.py`: both legal `--base` positions construct `ZoteroClient` with the supplied URL.
- `test_bibliography.py`: deterministic fake clock/poller coverage for the settle window, `poll_interval <= 0`, a target appearing on the final-deadline read, exactly one fresh-evidence fetch reused through the window and final staleness, the exact sorted `(id, title)` comparator (including byte-different JSON that MATCHES), a client stub that fails the test if any `autoexport.*` call is attempted, and missing/non-regular/malformed versus I/O/Unicode classification without real sleeping.
- `test_bibliography.py`: transaction regressions cover existing and unborn HEADs. Assert the committed blob is the supplied validated buffer even if the worktree target changes after validation; the commit tree is expected HEAD with only `x/bibliography.json` replaced; its parent is exactly expected HEAD when one exists; and hooks, `git add`, and `git commit --only` never run. Resolve and lock the linked-worktree-specific live index. A pre-staged/conflicted bibliography entry and a concurrent bibliography index writer must fail before HEAD/index/worktree mutation; the standard lock must remain held through HEAD CAS. Assert every unrelated live-index entry remains byte-for-byte identical while only the bibliography entry becomes the captured blob. After success, an unchanged target is clean and a newer BBT target is exactly an unstaged bibliography change.
- `test_bibliography.py`: inject a concurrent HEAD move and require forward CAS failure with no overwrite or index publication. Simulate lock-path reacquisition after successful publication and prove cleanup preserves the successor inode. Simulate index-publication failure for both existing and unborn HEAD and require exact HEAD rollback plus original index/worktree preservation. Race a new HEAD after the forward CAS and require rollback CAS to preserve that concurrent HEAD and surface the combined failure. Repeat the ordinary transaction in a real linked worktree and prove it uses that worktree's own standard index/lock without changing the main worktree's index. Assert cleanup removes only the still-owned lock inode and the code never rereads or writes the target.
- `test_cli_live.py`: patch the shared observer, not a duplicate import-only implementation. Cover note NOOP while the observer still runs, delayed genuine BBT output, UNMATCHED timeout/mismatch returning 1, UNREACHABLE returning 3, no note write on either failure, and no call to the old bibliography writer or write of comparison bytes.
- `test_cli_live.py`: with unrelated staged, unstaged, and untracked files present, the bookkeeping commit contains only the captured genuine `x/bibliography.json` bytes atop expected HEAD. Every unrelated live-index entry, worktree byte, and status remains exact; the intended bibliography index entry advances with HEAD. A target rewrite after validation is excluded from that commit and remains as an unstaged bibliography change for the next observer pass.

Run: `python -m pytest tests/test_doctor.py tests/test_bibliography.py tests/test_verify_cli.py tests/test_cli_live.py -m 'not live and not live_net' -v`.

Commit: `feat: add BBT-owned doctor and import flow`.

## Task 4: Implement verification witnesses, pre-commit, and CI authority split

Implement this task as one RED → GREEN sequence. It deliberately corrects the Task 1 canonical literature, pre-commit, and workflow resources after their focused tests expose the reviewed defects.

**Files:**

- Create: `core/harness_core/pathcodec.py`.
- Modify: `core/harness_core/gitstate.py`, `core/harness_core/checks.py`, `core/harness_core/quotes.py`, `core/harness_core/inbox.py`, `core/harness_core/notes.py`, `core/harness_core/lints.py`, and `core/harness_core/__main__.py`.
- Modify the reviewed Task 1 assets: `core/harness_core/templates/vault/x/templates/literature.md`, `core/harness_core/templates/git/pre-commit`, `core/harness_core/templates/ci/verify.yml`, and `core/harness_core/templates/ci/rw-batch.yml`.
- Create: `core/tests/test_pathcodec.py`, `core/tests/test_precommit.py`, and `core/tests/test_ci_templates.py`.
- Modify: `core/tests/test_checks.py`, `core/tests/test_quotes.py`, `core/tests/test_identify.py`, `core/tests/test_gitstate.py`, `core/tests/test_lints.py`, `core/tests/test_inbox.py`, `core/tests/test_notes.py`, `core/tests/test_verify_cli.py`, `core/tests/test_templates.py`, and `core/tests/test_scaffold.py`.

### Interfaces

`pathcodec.py` owns the only persisted textual representation of a Git path:

```python
PATH_BYTES_PREFIX = "path-bytes:"

class PathCodecError(ValueError): ...

@dataclass(frozen=True)
class RepoPathValue:
    raw: bytes

def encode_repo_path(raw: bytes) -> str: ...
def decode_repo_path(value: str) -> bytes: ...
```

Both functions either return one exact canonical value or raise `PathCodecError`; CLI callers map that error to exit 2 before any projection or inbox mutation and without a traceback. `RepoPathValue.raw` and `encode_repo_path` accept bytes only, and `decode_repo_path` returns bytes only. `RepoPathValue.__post_init__` applies the same raw repo-relative path validation as the encoder without producing text.

`checks.Outcome` is the typed persistence seam:

```python
@dataclass(frozen=True)
class Outcome:
    check: str
    target: str | RepoPathValue
    result: Result
    reason: str
    extra: Mapping[str, object] = field(default_factory=dict)
    target_kind: Literal["identifier", "repo-path"] = field(init=False)
    path_extra_fields: tuple[str, ...] = field(init=False)
    __hash__ = None

def outcome_to_record(outcome: Outcome) -> dict[str, object]: ...
def outcome_from_record(record: Mapping[str, object]) -> Outcome: ...
def outcome_to_csv_row(outcome: Outcome) -> dict[str, str]: ...
def outcome_from_csv_row(row: Mapping[str, str]) -> Outcome: ...
```

`Outcome.__post_init__` classifies each instance from the supplied value, never its contents. It uses `object.__setattr__` only during construction to store the validated reason, canonical target string, derived kind metadata, and recursively detached/frozen extras. A string target remains unchanged with `target_kind == "identifier"`; a `RepoPathValue` target is encoded exactly once and replaced by its canonical string with `target_kind == "repo-path"`. Each direct `extra` value that is a `RepoPathValue` is encoded exactly once before recursive freezing, replaced by its canonical string, and its key enters a lexicographically sorted, duplicate-free `path_extra_fields` tuple. Identifier targets and direct identifier-valued extras must be strings. Reject any other target type.

The recursive detach/freeze routine accepts only an acyclic JSON-shaped graph with string mapping keys. It copies each mapping to a new `dict`, recursively freezes its values, and exposes it through `types.MappingProxyType`; it copies each list or tuple to a tuple of recursively frozen values; and it retains JSON scalar values unchanged. Reject cycles, bytes at any depth, a `RepoPathValue` anywhere except a direct `extra` value handled before recursion, sets/frozensets, non-string keys, and every unsupported object. Thus mutating any caller-owned nested mapping/list after construction cannot affect the Outcome, and neither a top-level nor nested Outcome value exposes a mutation path.

`target`, `target_kind`, `path_extra_fields`, `reason`, and `extra` cannot be assigned after construction, and `__hash__ = None` deliberately keeps Outcome unhashable despite `frozen=True`. No API mutates an Outcome or its extra graph. A producer that needs changed metadata completes a fresh mutable builder before construction or constructs a new input graph and a new Outcome. `dataclasses.replace` is also construction: tests/callers must supply each new repo-path target or direct path extra as `RepoPathValue`, and `__post_init__` recomputes both `init=False` metadata fields instead of accepting or copying them. In particular, a path-changing replace supplies a new typed target/extra; no implementation recovers kind from the old canonical string.

`outcome_to_record` first revalidates every metadata-marked canonical repo-path token, then emits exactly `check`, `target`, `target_kind`, `result`, `reason`, `extra`, and `path_extra_fields`. It recursively thaws mappings to fresh ordinary `dict` values and tuples to fresh JSON lists, converts `Result` to its four-state string, and converts the immutable metadata tuple to a sorted JSON array; mutating any returned record or nested value cannot affect the source Outcome. `outcome_from_record` validates a plain acyclic JSON graph, those exact snake_case fields, the two kind literals, unique/sorted field names, and canonical path tokens. It reconstructs `RepoPathValue` only for a `repo-path` target and the direct extras named in `path_extra_fields`, then lets `Outcome` encode each wrapper once and recursively freeze the graph. It never infers from a check name, field name, slash, or `path-bytes:` prefix. An identifier remains an identifier even when its characters equal a `path-bytes:` token. `Outcome.__dict__`, `dataclasses.asdict`, generic deep-copy, and pickle are not serialization paths.

Raw JSON uses `outcome_to_record` unchanged. Raw CSV uses the exact columns `check,target,target_kind,result,reason,extra,path_extra_fields`; `extra` is one compact, key-sorted JSON object and `path_extra_fields` one compact JSON array. The CSV reader validates both before calling `outcome_from_record`. Reducers and enrichers never reconstruct from `outcome.target` plus `dict(outcome.extra)`: they recursively thaw with `outcome_to_record`, modify that detached typed record, and rebuild through `outcome_from_record`, preserving `target_kind` and every direct path-extra declaration. They return a new Outcome and leave all source Outcomes unchanged.

In-memory consumers treat structured extras as `collections.abc.Mapping`, not `dict`. In particular, `__main__.py` uses `Mapping` for identifier and warning records; its existing `.get`, iteration, and `entry.update(identifiers)` operations remain valid on frozen mappings. List-shaped extras such as `claims` and `warn_notices` are tuples in an Outcome and become lists only in a detached serialized record. `identify.py` may keep its local mutable `identifiers` builder because it finishes that builder before constructing an Outcome; it requires no production edit.

Inbox findings add the exact inline field `target-kind`; inbox code retains Python `target_kind`, while serialized inline field names keep their established kebab-case. Finding IDs, open/dedup keys, acknowledgment lookup, and acknowledgments include both the canonical target string and `target_kind`; acknowledgment lines repeat `target-kind` and the loader requires it to match the referenced finding. New writers always emit it. A legacy line without `target-kind` is an `identifier` and is never upgraded by inspecting its target. JSON/CSV/inbox consumers call `decode_repo_path` only for a target explicitly marked `repo-path` or a direct extra explicitly listed in `path_extra_fields`; a filesystem consumer rejects an identifier kind even when its string begins `path-bytes:` or contains `/`.

`gitstate.py` exposes immutable base/candidate/live snapshots and the projection publisher. A file image contains the raw repo-relative path, node kind, Git-normalized mode, and exact bytes or symlink target. A projection plan contains the single resolved expected HEAD, selected candidate, complete live preimage, and every computed postimage. Before publication, a captured output contains only its raw path, exact regular-file mode, and exact in-memory bytes; the publisher records its blob OID only after the post-projection manifest audit hashes that buffer. `__main__.py` owns orchestration and exposes:

```text
verify --surface {audit,commit,publish} --git-base REV
       --git-candidate {worktree,index,HEAD}
       [--changed-paths-file FILE] [--commit-projected MESSAGE]
```

`--commit-projected` is valid only with `--changed-paths-file`, requires a non-empty message, and keeps planning, projection, manifest audit, blob capture, and publication in this one verifier process. Invalid combinations are usage exit 2 before mutation. The packaged RW job is the only Task 4 caller of this publication flag; ordinary audit, pre-commit, and read-only CI do not publish.

### Base and candidate snapshots

`--surface` defaults to `audit`; `--git-candidate` defaults to `worktree`; an omitted `--git-base` defaults to HEAD, or to Git's stored empty tree when HEAD is unborn. Resolve the base exactly once, before collection or projection, to one immutable tree OID and thread that OID through every base-dependent lint, Git collector, deleted-target fallback, target hash, and acknowledgment lookup. An explicit missing, malformed, ambiguous, or non-tree-ish base is an operational error: print a concise diagnostic, return 2, and perform no verifier mutation. Published drift is the exception to base routing: it remains a comparison from the applicable `published/*` tag to the selected candidate and must not be silently rebound to `--git-base`.

Resolve expected HEAD exactly once as either its commit OID or the unborn state. Whenever an empty baseline is needed, create/store the empty-tree object with `git hash-object -w -t tree /dev/null` or an exact equivalent, then require `git cat-file -e "$git_base^{tree}"`. The expected HEAD is the parent and expected-old value for an optional RW snapshot commit; it is distinct from `--git-base` when an explicit comparison base is supplied.

Immutable snapshot resolution may create only two kinds of required Git snapshot object before output discovery: the stored empty tree and the selected index candidate's single `git write-tree` tree. These object-only writes may leave unreachable objects, but they move no ref and change no live-index or worktree byte. No other object/publication command is permitted in snapshot resolution. If base, expected-HEAD, candidate, or live-preimage resolution fails, return operational exit 2 before collection or projection.

Resolve the selected candidate exactly once as well:

- `worktree` is one immutable bytes/kind/mode snapshot of the live vault taken before collection and is the interactive/audit default; no later collector rereads mutable candidate state.
- `index` is the prospective commit. Snapshot it with one successful `git write-tree`; staged additions, edits, deletions, renames, and acknowledgment entries count, while unstaged scratch bytes do not. An unmerged or unreadable index is exit 2. A pre-commit comparison is therefore resolved HEAD → index, with the empty tree as the base of an unborn first commit.
- `HEAD` is the checked-out commit tree. CI compares the explicit fetched base → this checked-out HEAD snapshot; it never substitutes the workflow's mutable worktree.

Before collection, also take exactly one complete immutable live-worktree preimage snapshot. For `worktree` it is the selected candidate; for `index` and `HEAD` it is a separate snapshot used for divergence checks, projection CAS, rollback, and the manifest's before-state. Do not take a second drifting before snapshot.

Git diff/tree interfaces return raw path bytes as NUL-delimited records and preserve rename pairs without newline parsing. Internal Git paths and changed-path manifests remain raw bytes. A filesystem adapter may use `os.fsdecode`/`surrogateescape` only transiently after proving `os.fsencode(decoded) == raw`; no surrogate may enter a persisted or displayed string. Prefer byte-path calls where available. No lossy replacement, Unicode normalization, case folding, or newline split is permitted.

### Canonical textual path identity

For each raw path byte, `encode_repo_path` emits `/` and RFC 3986 unreserved ASCII bytes `[A-Za-z0-9._~-]` literally and emits every other byte, including `%`, as `%HH` with uppercase hexadecimal. It prepends the exact lowercase prefix `path-bytes:`. It encodes bytes directly, never decodes as UTF-8, and never recursively percent-decodes. Thus `b"literatures/a b%2F.md"` becomes `path-bytes:literatures/a%20b%252F.md`, while `b"literatures/\xff.md"` becomes `path-bytes:literatures/%FF.md`.

The decoder requires a `str` containing the exact prefix, an ASCII-only and surrogate-free payload, literal bytes only from the allowed set, and escapes matching `%[0-9A-F]{2}`. It rejects lowercase hex, malformed/truncated/non-hex escapes, literal reserved ASCII, literal non-ASCII, and over-encoded safe bytes or slash such as `%41`, `%7E`, or `%2F`. After decoding once, it requires `encode_repo_path(decoded) == value`; any alias is invalid.

Decoded values must be non-empty Git repo-relative byte paths: no leading slash, NUL, empty component, `.` component, or `..` component, hence no trailing/doubled slash or lexical traversal. Only byte `/` separates Git components; backslash remains an ordinary filename byte on POSIX. Before filesystem use, an adapter must reject any platform-specific drive, UNC, separator, device, case-folding, or normalization alias and verify that directory entries preserve the requested raw spelling. Symlink containment remains a separate safety check. Never use decoded display text, `normcase`, normalization, or `resolve()` as path identity.

Every repo path crosses the textual boundary through `RepoPathValue`; no `(check, field)` table or string heuristic assigns kind. Migrate producers exactly as follows:

- `checks.py` wraps every repo-relative target and direct path extra, including a citation-free note target and `note_path`; citekeys, DOIs, PMIDs, and other identifiers remain strings.
- `quotes.py` wraps the checked-note target used by no-quote/no-citekey fallback outcomes and every `note_path` extra; citekeys and claim-link addresses remain strings. Thus two `quote` outcomes may have different `target_kind` values without ambiguity.
- `lints.py` wraps file targets and direct note/path extras sourced from raw Git or filesystem paths; citekeys, claim links, notice identifiers, and gate references remain strings. Mixed-target checks such as `claim-immutability` and `web-archive` carry their per-instance kind.
- `__main__.py` wraps bibliography/staleness, managed-note, archive, and other repo-path targets/extras at construction; bibliography item IDs, citekeys, DOI/PMID values, claim links, and external references remain strings.

Use already-raw snapshot/Git bytes when available. A `Path` producer may transiently use the proven `os.fsencode` round trip before constructing `RepoPathValue`; it may not persist the intermediate text. Every path-bearing Outcome/inbox/JSON/CSV/diagnostic surface then uses the encoded token stored by `Outcome`. The finding and its acknowledgment compare the canonical token plus kind; a rename changes that identity even when content is unchanged. A malformed/noncanonical stored token, kind mismatch, or metadata mismatch is exit 2 before filesystem access or mutation. Serializers may quote the token for their format but may not Markdown-escape, URL-quote, normalize, or independently re-encode it. Raw NUL Git records and manifests never pass through this codec.

### Exact managed-region witness and evidence boundary

The managed delimiters are the exact ASCII line contents `%%hk-managed%%` and `%%/hk-managed%%`, with no leading/trailing spaces or other bytes. A delimiter line may end in LF or CRLF; the closing delimiter may instead end at EOF. A valid literature note contains exactly one opening and one closing delimiter in that order, with no duplicate or nested delimiter. Its raw managed slice starts at the first `%` of the opening delimiter and ends after the closing delimiter's actual line ending, or at EOF when it has none. Thus the hash includes both delimiter bytes, every interior byte, and the file's actual line endings; it never normalizes text or newlines.

`managed-sha256` is one top-level YAML scalar containing exactly the lowercase 64-hex SHA-256 of that raw slice. Add `managed-sha256: "{{MANAGED_SHA256}}"` to the packaged literature template and to the renderer's owned managed fields. Import/render computes it from the rendered slice and changes it only when those slice bytes change; a byte-identical managed projection preserves it and the existing `generated.at`. For an existing candidate literature note, a missing, non-string, non-lowercase-hex, or stale witness, or a missing/duplicate/misordered/malformed delimiter, produces an `evidence-layer` UNMATCHED/schema finding. A target I/O or Unicode/frontmatter-decoding failure is UNREACHABLE, while Git command/object/protocol failure is an operational exit 2 rather than an invented content state.

Independently of witness correctness, every base → candidate change to a managed region is an `evidence-layer` finding: adding or deleting a managed note, editing any byte in its raw managed slice, or renaming its path. A free-region-only edit is not such a finding. No actor, importer, witness refresh, or successful import self-authorizes this change, and neither import nor verification stages or auto-commits managed-note changes. The existing append-only, content-hash-scoped human acknowledgment is the sole pass: it must have a `human:` actor and match the evidence-layer finding's check, target, and target hash. Hash against the selected candidate content, using the resolved base blob only for the existing deleted-target fallback; a changed target hash or renamed target requires a new acknowledgment. A valid acknowledgment suppresses only the effective closing decision, not collection or the raw finding/audit record.

### Collection, projection, surfaces, and offline state

Refactor verification into one ordered pipeline: resolve the base, expected HEAD, immutable selected candidate, and complete live preimage once; collect every deterministic and requested network/CSV outcome against those snapshots once; calculate target hashes and acknowledgments against those same snapshots; compute every genuine pass/failure event, current marker, inbox record, and resulting per-path postimage in memory; validate and transactionally apply that complete plan; audit the applied change with the manifest; optionally publish the captured postimages; then apply the selected surface's closing set. Collection and planning perform no vault write. Multiple mutations of one path compose deterministically into one final postimage. Surface selection must not change raw outcomes, acknowledgment lookup, planned/applied bytes, captured outputs, or manifest.

`CLOSING_BY_SURFACE` is exactly:

```python
{
    "audit": frozenset(),
    "commit": frozenset({"citekey", "evidence-layer"}),
    "publish": frozenset({"citekey", "evidence-layer", "quote", "update-notice", "doi"}),
}
```

Bare `verify` is therefore the open `audit` surface: it collects and projects everything but closes nothing and returns 0 for findings or genuine outages. Operational/usage failure still returns 2. On explicit `commit` or `publish`, return 1 when an unacknowledged closing check is UNMATCHED; otherwise return 3 when a genuine UNREACHABLE must be surfaced; otherwise return 0. The pre-commit and read-only CI callers deliberately leave exit 3 open with a warning, while the later publish gate treats it as closed. The same fixture run on commit and publish must have identical raw outcomes and mutations and differ only in the effective closing decision/exit.

Represent synthetic network-disabled results structurally by constructing the Outcome with a fresh input mapping such as `extra={"synthetic_offline": True}`, never by mutating an Outcome or matching reason text. They may appear in explicit raw/JSON reporting, but exclude them from all target hashes, acknowledgment lookup, trust derivation, verified events, failure markers, inbox records, effective findings, changed-path manifests, and exit decisions. A network call that is genuinely attempted and raises remains a persisted UNREACHABLE. `--offline --rw-csv FILE` runs deterministic offline checks plus the supplied CSV leg only; it does not run or fabricate DOI, registry, or other live-network legs.

### Candidate projection transaction

The projection output set is the raw-byte-keyed set of paths whose planned postimage differs in bytes, kind, or Git-normalized mode from the selected candidate. Before the first write, validate every destination and compute every postimage. For an `index` or `HEAD` candidate, each destination's candidate image must equal the captured live preimage byte-for-byte and in kind/mode, including equal absence; any divergence is exit 2 with no vault mutation. A `worktree` candidate is the captured live preimage, so it has the same immutable comparison point.

`--commit-projected` adds a stricter dirty-overlap preflight after complete postimage/output discovery. The two required snapshot-object writes above may already have occurred. The preflight must finish before any vault projection, manifest write, postimage `git hash-object -w --stdin`, temporary-publication-index creation or `read-tree`/`update-index`/`write-tree`, `commit-tree`, or `update-ref`. For every eventual output path, the selected candidate image and captured live preimage must both equal that path in expected HEAD, byte-for-byte and in kind/mode/absence. Its linked-worktree live index must have one stage-0 entry equal to expected HEAD, or no entry when expected HEAD has none; an unmerged entry, staged bytes, deletion, addition, type/mode change, unreadable index, or any other output overlap is exit 2 with no HEAD/index/worktree mutation. Unrelated staged, unstaged, and untracked state is permitted and must remain exact.

Apply planned outputs in lexicographic raw-byte path order. Immediately before each atomic replace/create, compare the live destination's bytes, kind, and mode with its captured preimage. A divergence before the first write exits 2 with zero writes. A divergence or write failure after earlier writes triggers reverse-order rollback: restore a prior preimage, or remove a path created by this transaction, only while the live path still equals this transaction's installed postimage in bytes, kind, and mode. Never overwrite a concurrent successor. If any rollback comparison or operation conflicts/fails, print the exact combined diagnostic `projection failed at PATH: CAUSE; rollback failed at PATH: CAUSE`, using canonical encoded paths and the two underlying causes, then return 2; never claim success or silently absorb partial state. The same owned-postimage rollback applies to a pre-publication snapshot, manifest-validation, or manifest-write failure.

The live index is never written by projection or Task 4 publication. This is the accepted solo-local concurrency bound: filesystem compare-and-replace is best-effort rather than a kernel transaction; the immutable preimage, pre-write divergence refusal, atomic per-file replacement, and ownership-gated rollback are sufficient. Do not claim cross-process serializability. Preserve a concurrent human change even when that means reporting a rollback conflict.

### Exact verifier-owned output manifest

`--changed-paths-file FILE` is canonical audit evidence of verifier mutations, never caller authority or commit input. Resolve its destination before collection and require it to be outside the vault, including through symlink resolution; an invalid or unwritable destination is exit 2 before projection. Reuse the single complete live preimage as the before-state and take one complete after snapshot once projection finishes, excluding only `.git` and its descendants. Snapshot every node by raw repo-relative path bytes, node kind, permission mode, and file bytes or raw symlink target; include directories so additions, removals, type changes, and mode-only changes cannot escape detection. Snapshot/read errors are exit 2 with a concise diagnostic and no traceback.

Derive the actual changed-path set from those snapshots. Every changed node must be a regular Markdown file in exactly one of these locations: `inbox/review-queue.md`, or recursively below `literatures/`, `synthesis/`, or `projects/`. Directories, symlinks, special files, `.git`, absolute paths, empty paths, `.`/`..` components, and every other vault path are outside the allowlist. The planned output set, actual snapshot difference, and emitted manifest entries must be exactly equal: no missing, phantom, unchanged, duplicate, or extra entry. Serialize each repo-relative raw path once, in lexicographic raw-byte order, followed by one NUL; an empty run is a zero-byte file. Sorting and deduplication operate on raw bytes, not encoded display tokens. Manifest generation, validation, or write failure returns 2 without a traceback and follows the owned-postimage rollback rule above.

### Exact RW snapshot publication

After successful projection and manifest audit, `--commit-projected MESSAGE` publishes only when the captured output set is non-empty. The captured postimage bytes and modes are the commit source. Hash each exact in-memory byte buffer with `git hash-object -w --stdin` and retain its OID; never reread the worktree, decode a path, or use the manifest to choose a path, mode, or byte. A rewrite after the after-snapshot remains visible as a later unstaged worktree change and never enters this commit.

Create a private temporary `GIT_INDEX_FILE` seeded from the exact expected HEAD tree, or from the stored empty tree when HEAD is unborn. Install only the captured output entries with their captured modes and blob OIDs, write the tree, and create the commit with `git commit-tree` using `MESSAGE` and the configured Git identity. No hook runs. The commit parent is exactly expected HEAD when one exists, and its tree is exactly expected HEAD plus only the captured output replacements. Publish with `git update-ref HEAD NEW EXPECTED_OLD`, using the zero OID as the expected-old value for an unborn ref. A concurrent HEAD wins: the CAS fails cleanly with exit 2 and never overwrites it. A publication failure leaves the successfully projected/captured outputs visible for diagnosis, leaves the entire live index byte-for-byte unchanged, and does not broaden the commit; a subsequent workflow push occurs only after verifier exit 0.

A zero-byte manifest and empty captured-output set produce no commit. The publisher never invokes `git add`, a broad pathspec, pathspec-file staging, `git commit`, or `git commit --only`. It preserves every unrelated staged entry and every unrelated staged, unstaged, and untracked byte. The manifest remains raw NUL audit evidence and cannot inject a commit path or select stale/current worktree bytes. Task 4 publication does not authorize a managed-region finding, does not auto-commit a pre-existing managed-note edit, and does not reuse Task 3's live-index publication transaction.

### Packaged authority contracts

Review and correct the Task 1 assets rather than assuming their current bytes are authoritative:

- The executable pre-commit hook resolves the current HEAD OID once; when unborn, it stores the empty-tree object with `git hash-object -w -t tree /dev/null`. It requires `git cat-file -e "$git_base^{tree}"` before invoking exactly `python3 -m harness_core verify --vault "$vault" --offline --surface commit --git-base "$git_base" --git-candidate index`. It blocks exit 1, leaves exit 3 open, treats unexpected/operational codes as failures, and documents `--no-verify` plus CI replay.
- `verify.yml` has only `permissions: contents: read`, checks out with `persist-credentials: false`, stores its empty-tree fallback, fetches/resolves its explicit event base, and requires `git cat-file -e "$base^{tree}"` before exposing that base. It invokes exactly `python -m harness_core verify --vault . --offline --surface commit --git-base "${{ steps.base.outputs.sha }}" --git-candidate HEAD`. It has no commit or push step. Verification may mutate the ephemeral checkout while projecting results; read-only means repository authority/no push, not a falsely immutable runner filesystem. Exit 1 fails, exit 3 warns and succeeds, and every unexpected code fails.
- `rw-batch.yml` remains separately installed only by `--with-rw-ci`, has `contents: write`, configures the commit identity, downloads with `curl --fail --show-error --location`, and invokes exactly `python -m harness_core verify --vault . --offline --surface audit --git-candidate worktree --rw-csv "$RUNNER_TEMP/rw.csv" --changed-paths-file "$RUNNER_TEMP/harness-changed-paths" --commit-projected "chore: rw-batch findings"`. It accepts only verifier exit 0; exit 1, exit 3, and every other status are unexpected/infrastructure failures. It runs only the CSV network-data leg, fails installation/download/infrastructure errors without `|| true`, and pushes only after a non-zero-byte manifest proves that the verifier already published its exact snapshot commit. It never stages or commits from the manifest.

### Required RED coverage

- `test_gitstate.py` and `test_lints.py`: exact one-time base, expected-HEAD, candidate, and complete live-preimage resolution; bad explicit base, failed snapshot command, and unmerged index exit 2 before projection. Prove snapshot resolution may store only the required empty tree and index candidate `write-tree` before output discovery; both leave refs/live-index/worktree exact. Cover HEAD → index prospective-commit semantics including unborn stored empty tree, staged delete/rename/ack, and ignored unstaged scratch; explicit base → HEAD CI semantics; every baseline-dependent collector/hash receives the resolved base; published-tag independence; raw NUL records and rename pairs without newline parsing.
- `test_pathcodec.py`: `RepoPathValue` accepts bytes and rejects text/invalid raw paths; cover the exact `path-bytes:` prefix and examples, literal `/` plus `[A-Za-z0-9._~-]`, and uppercase `%HH` for every other byte including space, `%`, brackets, control/newline, backslash, non-ASCII, invalid UTF-8, and every other reserved byte. Exercise all 256 byte values for encoder treatment and round-trip every value legal in a component; NUL remains invalid after decode. Prove round-trip/injectivity, `b"\xE9"` distinct from UTF-8 `b"\xC3\xA9"`, slash distinct from literal `%2F`, and no case/Unicode normalization. Reject wrong/missing prefix, empty payload, raw reserved/non-ASCII/surrogate text, malformed/truncated/non-hex/lowercase escapes, over-encoded safe bytes/slash, absolute/trailing/doubled paths, `.`/`..`, encoded traversal, NUL, and platform spelling aliases; require decode → re-encode equality before filesystem use.
- `test_checks.py` and `test_quotes.py`: `Outcome` assigns the exact per-instance `target_kind` and sorted immutable `path_extra_fields`, encodes direct wrappers once, and recursively detaches/freezes caller extras as mapping proxies and tuples. Assignment to `target`, `target_kind`, or `path_extra_fields` raises `dataclasses.FrozenInstanceError`; top-level extra item assignment raises `TypeError`; nested mapping/list mutation is impossible; and `hash(outcome)` raises `TypeError`. Mutating the caller's original nested mapping/list after construction cannot affect the Outcome. Reject bare bytes at every depth, unsupported targets/objects, non-string keys, sets/frozensets, cycles, and nested path wrappers. `dataclasses.replace` with freshly supplied typed target/extras and direct new-Outcome construction each recompute kind metadata. Rename/update `test_outcome_rejects_invalid_or_empty_reasons_and_has_fresh_extra_dicts` so it asserts two independent recursively immutable graphs and never mutates an Outcome as setup.
- `test_checks.py`, `test_identify.py`, and `test_verify_cli.py`: recursively thawed records contain fresh dict/list values and no mapping proxy, tuple, bytes, wrapper, surrogate, set, or frozenset; mutating a returned record at any depth cannot affect the Outcome. Freeze → record → reconstruct preserves values, target kind, and sorted direct path-extra metadata; malformed/missing/duplicate metadata fails before decode. Notice reduction uses the typed record/rebuild path, preserves typed target/path extras, leaves both source Outcomes unchanged, and still projects frozen `warn_notices` through `Mapping` consumers. Frozen nested `identifiers` remain immutable but still update the local bibliography entry through the `__main__.py` `Mapping` consumer. Assertions that need JSON list/dict shape inspect `outcome_to_record(outcome)["extra"]`, not the frozen in-memory tuple/proxy.
- `test_checks.py` and `test_quotes.py`: cover mixed identifier/repo-path `citekey`, `quote`, `claim-immutability`, and `web-archive` outcomes; identifiers containing `/` or beginning `path-bytes:` remain identifiers, while a path without `/` remains a repo path. Prove every listed producer and `note_path` extra uses the wrapper, claim links remain identifiers, and no assertion expects the old raw textual path. JSON and CSV records validate the immutable metadata before round-tripping kind plus canonical strings.
- `test_inbox.py` and `test_verify_cli.py`: one invalid-UTF-8 path has the same canonical token and immutable `repo-path` kind metadata in Outcome fields/extras, inbox finding, deduplication, human acknowledgment, JSON, CSV, and diagnostics, with valid UTF-8 persistence and no surrogate/no-crash. Prove `target-kind` finding/ack round-trip, legacy absence defaults only to `identifier`, kind participates in finding ID/open/dedup/ack identity, and a prefix-like identifier cannot collide with the same canonical repo-path string. Prove exact-token-plus-kind/current-hash acknowledgment, rename invalidation, noncanonical alias or kind mismatch rejection before mutation, and exact raw bytes at filesystem lookup. Target hashing, origin lookup, marker mutation, and deleted-target fallback require explicit repo-path metadata and never infer from check, field, slash, or prefix.
- `test_notes.py` and `test_verify_cli.py`: LF, CRLF, and closing-at-EOF witness bytes; exact delimiter inclusion; missing/duplicate/nested/reordered/whitespace-altered delimiters; missing/malformed/uppercase/stale witnesses; render-only witness update and byte-identical preservation; current candidate and resolved-base error classifications.
- `test_verify_cli.py`: managed add/edit/delete/rename each yields an evidence-layer finding even with a correct refreshed witness and an importer/agent actor; free-only edits do not. Prove import never stages/commits the note. Prove only a matching `human:` acknowledgment for the current candidate target hash makes the closing finding pass, and changing content or path invalidates it. Run identical outcomes through audit/commit/publish: audit collects/projects all and closes none; explicit surfaces use the exact sets above without changing raw outcomes or vault mutations.
- `test_verify_cli.py`: structural synthetic-offline outcomes may report but produce no hash, ack, trust/event/marker/inbox/manifest/exit effect or planned postimage; a genuinely attempted outage is persisted; offline plus RW CSV runs only the CSV leg. Compare complete vault snapshots. Cover the reserved root `log.md` versus `log/` path collision.
- `test_verify_cli.py`: candidate projection snapshots once and computes all postimages before any write; a computation error or index/HEAD candidate divergence at an unstaged origin/inbox path produces zero writes. Race a rewrite before the first apply, during a multi-path apply, and into an absent path; inject a write failure; prove reverse owned-postimage rollback. Race a second rewrite during rollback and prove it is preserved while exit 2 reports both failures. No case may silently leave partial state. Prove deterministic composition, the same postimages on audit/commit/publish, and byte-for-byte live-index preservation.
- `test_verify_cli.py`: manifest destination outside-vault preflight; reuse of the one complete preimage; complete after detection; exact allowlist and planned-equals-actual-equals-manifest invariant; raw-byte ordering rather than encoded ordering, deduplication, one-NUL termination, and zero-byte empty run. Cover regular-file/type/mode/symlink/directory changes; missing, phantom, duplicate, absolute, traversal, out-of-allowlist, snapshot, validation, and write failures. All return exit 2 without traceback, and post-write failures use ownership-gated rollback.
- `test_gitstate.py` and `test_verify_cli.py`: RW dirty-overlap refusal before mutation for an output that is unstaged, staged, conflicted, added/deleted, or differs in type/mode from expected HEAD/candidate/live preimage/index. Empty-tree storage and the selected index candidate's one snapshot `write-tree` may precede refusal; assert overlap invokes no vault projection, manifest write, postimage `hash-object`, private `GIT_INDEX_FILE`/`read-tree`/`update-index`/publication `write-tree`, `commit-tree`, or `update-ref`. Cover existing and unborn HEAD publication, exact captured buffer/blob/mode despite a worktree rewrite after manifest/snapshot, a tree equal to expected HEAD plus only captured outputs, and the exact parent. Preserve unrelated staged/unstaged/untracked state and the entire live index byte-for-byte. A concurrent HEAD CAS loses cleanly; a later rewrite remains visible and is not committed; zero outputs invoke no publication command; hooks never run. Manifest tampering cannot select a path, mode, or byte. Inject each publication-stage failure and prove HEAD/live index stay exact before CAS; unreachable objects are allowed, but no commit may contain reread bytes. Assert no `git add`, broad pathspec, pathspec-file commit, `git commit`, or `commit --only` path.
- `test_precommit.py`, `test_ci_templates.py`, `test_templates.py`, and `test_scaffold.py`: explicitly prove the corrected Task 1 bytes, executable/mode and scaffold copies. Exercise the exact `--git-candidate index` hook contract on ordinary and unborn repos, including stored empty-tree objects and successful `cat-file` tree checks; the explicit fetched-base → HEAD read-only workflow with stored/verified base trees and no push credentials; and ephemeral RO projection with no push. Prove the explicit open RW audit/CSV command passes `--commit-projected`, accepts only exit 0, rejects 1, 3, and unexpected statuses, pushes only the verifier-created snapshot after a nonempty manifest, and performs no manifest-driven stage/commit. A RW fixture changes verifier-owned metadata/markers in literature, synthesis, and project notes plus the inbox and commits all and only captured outputs while preserving unrelated status.

Run: `python -m pytest tests/test_pathcodec.py tests/test_checks.py tests/test_quotes.py tests/test_identify.py tests/test_gitstate.py tests/test_lints.py tests/test_inbox.py tests/test_notes.py tests/test_verify_cli.py tests/test_precommit.py tests/test_ci_templates.py tests/test_templates.py tests/test_scaffold.py -v`.

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
8. treats Zotero `.xpi` installs as human-only wizard steps;
9. treats creation of the whole-library Better CSL JSON auto-export in BBT Preferences as the same class of human-only wizard step (author ruling 2026-08-20): the skill states the exact target path doctor reported, the whole-library scope, the Better CSL JSON translator, and the keep-updated setting, then re-runs doctor to verify — it never registers an auto-export itself and never claims one exists before doctor reports `autoexport` MATCHED.

Add the ruled `PROVISION_COMPANIONS` constant and tests for exact frontmatter, commands, separate CI consent, doctor routing, human-only installs, and the human-only auto-export wizard step.

Run: `python -m pytest tests/test_skill_files.py -v`.

Commit: `feat: add setup-vault workflow`.

## Task 8: Run the live observation drill (registration-free caveat discharge)

**Files:**

- Modify: `core/harness_core/zotero.py`, `core/harness_core/bibliography.py`, and `core/harness_core/paths.py`.
- Rewrite: `core/tests/test_scaffold_live.py`.
- Modify: `core/tests/test_zotero.py`, `core/tests/test_bibliography.py`, `core/tests/test_doctor.py`, `core/tests/test_cli_live.py`, and `core/tests/test_paths.py` exactly as removing the registration surface requires.
- Modify after the corresponding evidence exists: `docs/environment.md`.

**Governing ruling (author, 2026-08-20) — supersedes every earlier Task 3/Task 8 registration contract in this plan.** The live drill falsified programmatic provisioning: `autoexport.add("//", …)` returns 404 `path is too short` before registration storage, because BBT 9.0.55's public JSON-RPC hardcodes collection scope (source-verified). Whole-library scope and BBT sole-writer ownership stand; provisioning becomes a **one-time human creation of the whole-library auto-export in BBT Preferences**, guided and verified by setup-vault and doctor — the same §7 class as the `.xpi` wizard steps (detect → guide → verify). The harness is observation/commit-only for this contract.

Remove the dead registration path; Git history preserves it:

- Delete the client's auto-export registration method and every stub, fake client method, test, and assertion that exercises it. No client method may issue `autoexport.add` or any other `autoexport.*` JSON-RPC method, and no test may assert one is issued.
- Delete the observer's registration branch and its second settle window (Task 3 as amended above): one settle window, one final comparison, then MATCHED/UNMATCHED/UNREACHABLE.
- `paths.to_bbt_host(path)` keeps its exact WSL contract — detect WSL from `WSL_INTEROP`, `WSL_DISTRO_NAME`, or `"microsoft"` in `platform.release().lower()`; on WSL require `wslpath -w PATH` to launch, exit zero, and print non-empty stripped output, raising `PathError` otherwise and never falling back to a WSL-native path; off WSL return the native absolute path. Its only remaining consumer is the human-facing repair guidance, where `PathError` degrades the guidance to the native absolute path and never changes a probe result. Never write either machine path to the repository, a tracked fixture, or `docs/environment.md`.
- Delete the registration-protection machinery with the registration it protected — the harness now creates nothing on the Zotero side, so no dangling export can survive a drill: `HARNESS_LIVE_BBT_REGISTER`, `HARNESS_LIVE_AUTOEXPORT_REMOVED`, `HARNESS_LIVE_SCAFFOLD_VAULT`, the persistent `tempfile.mkdtemp` reservation, the sibling `.<vault-name>.state.json` schema-1 recovery file, its device/inode ownership rules, and the human cleanup-confirmation protocol all go. The drill uses pytest's `tmp_path`.

`HARNESS_LIVE=1` is the drill's only gate. With it set, the drill:

1. scaffolds a fresh `tmp_path` vault under a synthetic local Git identity — exactly `user.name=knowledge-harness-live-drill` and `user.email=live-drill@example.invalid`, set locally before scaffold; the drill never depends on or changes global Git identity;
2. runs `doctor` against real Zotero/BBT through a real `ZoteroClient`;
3. requires `zotero` MATCHED with the reported versions in detail and `bbt` MATCHED with the live BBT version;
4. requires `autoexport` UNMATCHED — no human has created an auto-export for a throwaway vault — with a detail that names the exact `x/bibliography.json` target and the BBT Preferences repair, and requires `staleness` to stay warn-only;
5. requires that the run issued zero `autoexport.*` JSON-RPC calls (record every method name the transport sends) and that `x/bibliography.json` was never created;
6. requires the `doctor` CLI to exit 1 on that hard UNMATCHED and to print the guidance line.

**Explicitly deferred, by author decision 2026-08-20:** the MATCHED end-to-end leg — genuine BBT output observed, one real item imported, rerun to NOOP — requires a human-created whole-library auto-export pointing at the drill vault. None was created, so that leg is deferred, not silently skipped, and Task 9 accepts the deferral only while this record stands.

`docs/environment.md` records exactly these dated facts and no machine path:

1. 2026-08-20 — BBT 9.0.55's public JSON-RPC auto-export surface is `autoexport.add` only; `.list`, `.remove`, `.delete`, and `.get` each returned `-32601 METHOD_NOT_FOUND`; `add` is collection-scoped by implementation (source-verified).
2. 2026-08-20 — `autoexport.add("//", …)` fails 404 `path is too short` before registration storage: no entry is created, so whole-library registration is impossible through the public RPC.
3. 2026-08-20 — BBT persists auto-exports as profile preference keys `better-bibtex.autoExport.<encoded-path>`. Human-debugging fact only: doctor detection stays behavioral (target presence plus staleness) and never scrapes preferences.
4. 2026-08-21 — the retained drill vault was removed through the drill's own confirmed-cleanup path after read-only inspection of the Windows profile preferences and `zotero.sqlite` confirmed no registration was ever stored for its target; the sibling audit state is stamped `cleanup-confirmed`. Record the fact only, never the vault path.

Task 8 RED/acceptance coverage proves: no importable module exposes an auto-export registration call, and no `autoexport.*` method name is reachable from the client; the observer closes a persistent absence or mismatch after exactly one settle window with zero RPC registration attempts; the UNMATCHED detail names the target and the BBT Preferences repair; `to_bbt_host` still translates through `wslpath -w` on WSL and returns the native absolute path off WSL, while a `PathError` degrades guidance to the native path instead of changing a probe result; the live drill assertions above. Live assertions may be deferred only for genuinely unavailable authorization, recorded explicitly.

Run:

```bash
python -m pytest tests/test_zotero.py tests/test_bibliography.py tests/test_doctor.py tests/test_paths.py tests/test_scaffold_live.py tests/test_cli_live.py -m 'not live and not live_net' -v
HARNESS_LIVE=1 python -m pytest tests/test_scaffold_live.py -v
```

Commit: `feat: observe the human-created auto-export in the live drill`.

## Task 9: Final acceptance and merge

Run from `core/`:

```bash
python -m pytest tests -m 'not live and not live_net' -q -p no:cacheprovider
HARNESS_LIVE=1 python -m pytest tests -m 'live' -q -p no:cacheprovider
HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<authorized address> python -m pytest tests -q -p no:cacheprovider
python -m ruff format --check . --no-cache
python -m ruff check . --no-cache
```

The network leg transmits the supplied `HARNESS_MAILTO` to the polite API pools; run it only with an address the author authorized for this run, and record which legs ran and which were deferred.

Then run `git diff --check` and the scoped terminology scan from the repository root. Verify:

- all packaged paths and OKF exceptions match Task 1;
- scaffold commits only created paths;
- BBT alone writes the export after a human creates it; doctor and import wait, observe, and commit genuine output, and no code path registers an auto-export;
- offline audits are non-mutating while genuine outages persist;
- managed witnesses cover current, HEAD, and explicit CI-base comparisons;
- detection/state projection is surface-independent;
- RW verification commits the exact captured postimage bytes/modes from expected HEAD with an expected-old HEAD CAS, separately audits them against the raw manifest, and preserves the live index plus unrelated paths;
- `--with-ci` and `--with-rw-ci` remain separate authorities;
- the Stop bound is consecutive through `stop_hook_active`;
- Task 8 creates nothing on the Zotero side: the drill issues zero `autoexport.*` calls, leaves no registration and no retained vault, and its `docs/environment.md` entries carry no machine path;
- the required live gates pass or are explicitly deferred with a recorded reason, and the deferred MATCHED end-to-end leg names the human step it waits on.

Merge only after all nine task commits and acceptance evidence are present.

## Self-review

Tasks 1–2 own templates and scoped creation. Task 3 owns the BBT-writer boundary for doctor and import plus doctor routing. Task 4 owns managed witnesses, state/surface separation, the exact verifier-output manifest, pre-commit, and both CI contracts. Task 5 owns the unconditional literature-touch warning. Task 6 owns publish arming and the consecutive bound. Task 7 owns user consent. Task 8 owns the live observation drill and the removal of the falsified registration path. No task depends on a trailing ruling block to override its snippets.
