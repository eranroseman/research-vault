# Ingest Redesign Implementation Plan — Part B: compile adoption, live legs, closing

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Drive the adopted compile tool (`AgriciDaniel/claude-obsidian` at `32ac5a0`, v2.2.0 — the pin moved from `ad67087` on 2026-09-14, operator decision A, after a diff found nothing the wrapper or the tracers call moved between the two) through a glue wrapper once its tracers pass; add the compile sections to the skills; close the docs, registries and the CI deferral; run the write-capable live legs on the test instance; and close the ingest redesign with its one upstream issue.

**Architecture:** Compile is adopted unmodified: `research_vault/compile.py` selects captured sources, registers ledger records through the tool's own `transaction inspect`/`apply`, and never writes under `wiki/`. Everything else here is documentation, live-leg tests and one report. Capture, the lifecycle linter, propagation, the captured-set lint, doctor and `add` are Part A's and are consumed unchanged.

**Tech Stack:** Python 3.11+ stdlib only (`urllib`, `json`, `hashlib`, `html.parser`, `subprocess`, `pathlib`). pytest with `monkeypatch` fakes; two live Zotero 10 instances (production `localhost:23119`, test `localhost:23129`; versions from `python -m research_vault probe --base <base>`, never from this plan). No new dependency.

**Spec:** `docs/superpowers/specs/2026-09-06-import-redesign-design.md` (the active spec; §9 is its fact register). Also binding: `docs/superpowers/specs/2026-09-05-assembly-design.md` decisions 12, 17, 22, 28, 29 and §9; ADR 0001–0003.

**Prerequisite:** Part A (`docs/superpowers/plans/2026-09-07-ingest-redesign-a-capture.md`) merged to `main`. This part consumes, by name: `captured.captured_set`, `notes.read_provenance` and `notes.Provenance`, `fulltext.path_for`, `capture.capture` and `capture.add`, `lifecycle.lint_lifecycle` and `lifecycle.classify`, `zotero.ZoteroClient` on the local API with the `Zotero-Server-ID` header, `scaffold._installed_plugins` and the thirteen-probe doctor, and `skills/capture-source` and `skills/setup-vault` as Part A Task 19 left them. Part A's "Decisions this plan settles" (01–25) bind here unchanged; this part leans on 03 (verbs), 06 (probe ids), 17 (tool location and pin), 18 (`wiki/` in the guard), 22 (tracer results), 24 (the tool's inbox) and 25 (`linkMode`).

**Human attendance:** Task 1 (the tracers, one sitting with Obsidian open), Task 5 (one consent dialog on the test instance) and Task 6 (the go-ahead for the upstream issue) need the author present; Tasks 2, 3 and 4 do not.

## Global Constraints

- **Commit with an explicit pathspec** (`git commit -m "..." -- <files>`; the message precedes `--`). The `Co-Authored-By` trailer names the model that actually authored the commit, in the harness's own model name: an implementer dispatched on `sonnet` writes `Claude Sonnet 5`, one on `opus` writes `Claude Opus 5 (1M context)` (Part A's implementers ran on opus, which is why its commits carry that), and the controller's own commits (register rows, folds) name the controller's model. This plan's printed commit blocks carry `Claude Fable 5.1` because Fable wrote the plan; a trailer that differs from a printed block is therefore not a deviation to itemise, and a trailer naming a model that did not write the commit is a defect (corrected 2026-09-14 after ruling R8 read the earlier wording as "always Opus"). Parallel sessions share this checkout: never revert or restore another session's uncommitted files; report the precondition as unmeetable instead.
- **Offline suite before every commit:** `.venv/bin/python -m pytest tests -q -n auto` from the repo root. Baseline on 2026-09-07: 1838 passed, 7 skipped, 28 s; on 2026-09-14 after Plan W (`main` at `384d562`): 1955 passed, 5 skipped (the fifth skip is the live-marked pin of the HOME gate). Pass `-n` on the command line, never in addopts.
- **Form owners, run directly on touched files, never `pre-commit run`** (it stashes onto a stack every worktree shares): `ruff format research_vault tests scripts hooks`, `ruff check research_vault tests scripts hooks`, `mypy research_vault`, `mdformat --number --wrap keep <touched .md files>`, `python -m json.tool --indent 2 --no-ensure-ascii <file> <file>` for JSON manifests.
- **Ruff rules that bite new code:** `T20` (no `print` outside `research_vault/__main__.py` and `scripts/`), `C90` (`max-complexity = 28`), `PTH` (use `pathlib`), `S` (no `shell=True`), `DTZ` (timezone-aware `datetime`). mypy rung 1: annotated functions are checked; no `cast()` laundering.
- **Stdlib only.** The package's one runtime dependency (`defusedxml`) is untouched. `pytest-recording`/`vcrpy` are not adopted (spec §7: no recorder).
- **Four-state everywhere.** Every mechanical step returns `Outcome`s in `MATCHED`/`UNMATCHED`/`UNREACHABLE`/`SKIPPED`. An outage never reads as a pass; a skipped check never reads as clean (ADR 0002).
- **Reason codes and check ids are registries.** `Outcome.__post_init__` validates `reason` against `inbox.REASON_CODES` at construction, so a task adds its codes to `REASON_CODES` **before** any `Outcome` uses them. Every change to `REASON_CODES` must also update the `## Reason-code vocabulary` table in `skills/evidence-conventions/SKILL.md` (`tests/test_skill_contracts.py:440-494` requires every code exactly once) and the `reason codes` row of `docs/terminology.md` §4.4. Every change to `inbox.CHECK_IDS` or a doctor probe id updates the matching §4.4 row in the same commit.
- **Deprecate, never delete, for vault records** (ADR 0003): no transition deletes a literature note. Repository artifacts (plans, docs, code) are outside that rule; deleting them is hygiene.
- **No `Disposition:` line** on new Markdown: the marker system was deleted on 2026-09-07 (`7ec2c95`, `8e2721b`).
- **A test never substitutes into fixture text with bare `str.replace`.** When a fixture edit removes the literal, the substitution becomes a no-op and the test stays green while asserting nothing — Tasks 4, 5 and 11 each met it, and Task 11's review found seven at once. Use `tests/conftest.py::must_replace(text, old, new)`, which fails when `old` is absent (Task 18 adds it, converts the seven, and adds a scan over the fixture-heavy test files).
- **A deferral names the task whose Files block claims the file.** "The next touch of X" is not a schedule: if no later Files block names X, the deferral lands on the final task, after every task it was meant to protect, and reaches an implementer as a failing test it did not cause and cannot fix in scope (Task 13's ledger-message assertion against a string only Task 11 could change). Before deferring, grep the Files blocks for the file; if none claims it, name the task that will, or fix it now.
- **Dates an implementer writes are today's.** A literal date inside a printed test or fixture is a pinned value and stays as printed. A date written into a repository record — a supersession in the deviation register, an ADR exemption, a tracer result, a fixture README — is the day the work happens: the plan says "today's date" for those and the executor supplies it. The plan was written across a midnight, so any literal it printed for that purpose was stale by at least a day.
- **Machine-local facts stay out of the repo.** Nothing commits a local-API key, a Windows path, a server id, or a version count as a constant. Live values come from `python -m research_vault probe`. A fixture's canned server id is a test value, not a machine-local fact: `tests/fakes.py`'s `6LpvURP2E933` and Task 13's test's `Tdoqsn2J4q4h` are test values; whether either matches any machine is irrelevant, and the socket guard is what keeps a fixture id from ever meeting a live answer.
- **Deleting a module or a function prunes its `mutation-baseline.txt` rows in the same commit** (rewritten 2026-09-14 after Plan W: mutate4py and its `.manifest.json` sidecars are retired; the baseline is mutmut's, one key per survivor of the form `<relpath>::func/<name>::<diff>`). A deleted module's rows go with `grep -v '^research_vault/<module>.py::'`, a deleted function's with `grep -v '::func/<name>::'`; a renamed function's rows are pruned the same way and re-measured with `scripts/mutation_gate.py --update-baseline --only <module> --out-dir <dir>`, which rewrites that module's rows from a fresh run. A new module needs nothing up front: the gate measures it on the first run that changes it and reports every survivor as new until the baseline is updated. For a new module in this plan (`compile.py`), the task that creates it kills every behaviour survivor with a test; a survivor of the #42 classes (prose to a human; a literal never read back — the grep basis: the original literal occurs nowhere else in `research_vault/**` or `tests/**`) is accepted by appending its key to `mutation-baseline.txt` in the same commit, with the reason recorded in the results file (Task 6 Step 4); so is a mutant identical by construction — a keyword ruff mandates whose mutated value the callee treats the same (`check=False → check=None` on `subprocess.run`, which tests `if check and retcode`; Plan W's baseline carries three such rows) — recorded under its own reason beside the #42 classes. No `--update-baseline` run: it needs a record for every module.
- **Deletion lists are claims, not orders.** Every name a Files block says to delete carries the line number it had when the plan was written; before deleting it, grep for callers across `research_vault/`, `tests/`, `hooks/` and `scripts/`, and if kept code still uses it, keep it and report the call site as a deviation instead of deleting it or working around it (Task 3's `registry_agency`, called by the kept `check_update_notice`, and `metadata_year`, imported by `identify.py`, are the measured cases). Deleting an exception class also means removing it from every `except (...)` tuple that names it — `cmd_verify` and `_run_disposition` in `__main__.py` name `notes.ManagedRegionError` and `notes.RenderIntegrityError` — because Python evaluates that tuple only when an exception reaches it, so the suite may stay green while a real error is masked by `AttributeError` at runtime. Line numbers in Files blocks are navigation hints to verify by name.
- **What one task's design relies on another task's code doing is a claim to check, not a fact to assert.** Task 13's corrupt-note CSL loss relied on Task 15's lint reporting it, and the printed lint skipped such notes silently; Task 14's server-id argument relied on capture's read order, and the order was inverted. A brief that depends on such a behaviour says "if X does not hold, that is a finding to report" rather than asserting X, and the controller checks X against the ref that will run — the plan's printed code, or the branch — before dispatch. Both times this was done, X did not hold. The same rule covers a review finding relayed into a dispatch: Task 15's controller relayed "`validate_reason` is not pinned" without checking that `Outcome` construction already reaches it, and asked for three assertions that could not fail.
- **Every mutation run goes through `scripts/mutation_gate.py`, never through mutmut directly** (rewritten 2026-09-14 after Plan W). Gate mode diffs `<base>...HEAD`, so it measures committed changes only: run it after the commit it is measuring — an uncommitted tree reads "no changed research_vault modules" and passes, which is a false pass (measured 2026-09-16, Task 2). The gate owns what a bare run would get wrong: it sweeps `__pycache__` under `research_vault/`, `tests/` and `mutants/` and proves the source tree untouched (CPython's `mtime + size` pyc validation once reused a previous case's bytecode; `PYTHONDONTWRITEBYTECODE=1` blocks writing, not loading), caps every child's address space (`RLIMIT_AS`; a runaway-allocation mutant otherwise takes the whole memory scope down), makes `mutants/` its own git repository behind a ceiling directory (a scaffold mutant once installed the vault pre-commit hook into this repository's shared `.git/hooks`), and applies the CI mutant budget. Two facts a triage must carry: a local `timeout` verdict is environment-dependent and can mask a survivor — the runner is the arbiter, and a mutant a test can reach is killed rather than left flagged — and the gate's own tests run inside the gate's limits, so they must never depend on inherited process limits.
- **A task dispatched onto an inherited, uncommitted tree runs on `opus`.** Part A's Task 19: two `sonnet` implementers stalled at the moment of issuing a command on such a task, with no child process and no tool call recorded; an `opus` implementer from the same tree committed in ten minutes and verified every inherited path byte for byte. Classifying another author's half-finished work against printed text is a judgment task; the tier follows the task (Part A's deferred file, process note 9).
- **No string literal under `research_vault/` spells a hyphenated skill name.** The skill-directory scan (`tests/test_skill_contracts.py`) classifies a backticked kebab-case token in a skill or template as a skill name unless the code spells it as a substring of a non-docstring string literal, so a literal that spelled one would mask a route to a deleted skill; `test_the_code_spells_no_hyphenated_skill_name` pins the constraint (Task 19, `5b17dde`). Check ids, reason codes and field names are what the code spells; skill names are what the skills directory holds.
- **A pathspec commit ignores untracked files.** `git commit -- <paths>` picks up only files git already tracks; a file the task created stays behind silently. Every task that creates a file runs `git add -- <each created file>` before its commit and then checks that `git show --stat HEAD` lists every file it created (Task 10's first attempt missed both of its new files).
- **A new machine surface names itself where agents read.** A task that adds a directory to `hooks/pretooluse_guard.py`'s `MACHINE_SURFACE_DIR_NAMES` or `MACHINE_SURFACE_PREFIXES` also adds it to `research_vault/templates/vault/AGENTS.md`'s machine-written enumeration (the line-7 group: surfaces the CLI writes) and updates the byte-pin in `tests/test_templates.py`. A surface written by something other than the CLI gets its own sentence instead, as `wiki/` has — follow a precedent's reason, not its shape (Task 10 guarded `fulltext/` and left the enumeration unchanged).
- **No non-`live` test opens a socket to Zotero.** The offline suite must be green on a machine with no Zotero and give the same answer on one where a production instance is running; a test that reads a live instance is nondeterministic and green only by accident of someone's library. `tests/conftest.py::_no_zotero_socket` (autouse, Task 12) makes every `ZoteroClient` outside the `live` markers read an outage, and a test that needs a Zotero answer registers it on `FakeZotero`. Reads count as much as writes here: the write ban keeps production intact, this keeps the suite honest.
- **Live legs** stay under the existing `live` marker (`RV_LIVE=1`). Write-capable legs additionally require `RV_LIVE_WRITE_BASE` (the test instance, `http://localhost:23129`) and refuse to run against `zotero.DEFAULT_BASE`; `RV_LIVE_WRITE_KEY` optionally supplies a key granted by an earlier **Always Allow** so the leg runs without the dialog. Nothing in the suite ever writes to the production instance.
- **Outward-facing actions need explicit go-ahead in that turn**: Task 6's upstream Zotero issue is not run on plan approval alone.
- **Deferred findings have one home while the plan runs.** A review finding held out of a task's fix loop goes to `docs/superpowers/plans/2026-09-07-ingest-redesign-b-deferred.md` (created at the first finding; Part A's `…-a-deferred.md` is the shape: a numbered table with File, Finding, Task and Disposition, appended by the controller in a pathspec docs commit immediately after the task's review closes and before the next dispatch — the review that produces a finding runs after the task's commit, so "the same commit" cannot hold; ruling R7), never only to a task report — the SDD workspace is deleted at Finish (`AGENTS.md`, Task reports). Task 6 Step 1b dispositions every row before the merge.
- **Scope held by the spec:** annotations (spec §3.2, decision 28) are specified, tested against a fixture, and **not wired into capture**; the pre-commit lifecycle leg is held (invariant 5); substrate absence is deferred (§0); web pages and repositories are deferred (§0).

______________________________________________________________________

## Interface index

Signatures this part adds, then the Part A signatures its tasks call (copied from Part A's index; Part A's file is the authority).

```python
# research_vault/compile.py                                   (Task 2) 
LEDGER_PATH = notes.LEDGER_PATH   # one definition site (Part A Task 11). The compile-tool pin has one site too, scaffold._COMPILE_PIN ("32ac5a0", v2.2.0); compile.py carries no copy (R22)
PLUGIN_ID = "claude-obsidian@agricidaniel-claude-obsidian"; CHECK = "compile"
def stable_source_id(kind, locator, content_sha256) -> str
def tool_root(vault_root) -> Path | None
def ledger_record(citation_key, provenance, item_data, today) -> tuple[str, dict]
def plan(vault_root, keys, *, today=None) -> tuple[Path, dict]
def apply(vault_root, bundle_path, approved_sha256) -> Outcome

# research_vault/zotero.py additions                          (Task 5)
    def trash_item(self, key: str, version: int) -> int      # PATCH {"deleted": true} with If-Unmodified-Since-Version; 204
    def delete_item(self, key: str, version: int) -> int     # DELETE with If-Unmodified-Since-Version; 204

# consumed from Part A
def fulltext.path_for(vault_root, attachment_key) -> Path
def fulltext.write(vault_root, attachment_key, item_key, response) -> tuple[Path, str]   # (path, sha256 of file bytes)
@dataclass(frozen=True) class notes.Provenance:
    server_id: str; item_key: str; item_version: int; citation_key: str
    attachments: tuple[dict, ...]; fulltext: tuple[dict, ...]; compile_input_sha256: str | None
def notes.read_provenance(text: str) -> Provenance | None
def capture.capture(vault_root, client, keys, *, now=None, refresh_all=False, key_wait_seconds=KEY_WAIT_SECONDS) -> list[Outcome]
def capture.add(vault_root, client, items, *, collection=None, now=None) -> list[Outcome]
def lifecycle.lint_lifecycle(vault_root, client, provenances=None) -> list[Outcome]
def lifecycle.classify(provenance: Provenance, live: Live) -> tuple[str, str]   # (state, detail)
def captured.captured_set(vault_root) -> dict[str, str]            # citation key -> item key
def scaffold._installed_plugins() -> dict[str, list[dict]]          # ~/.claude/plugins/installed_plugins.json, plugins map
class zotero.ZoteroClient(base=DEFAULT_BASE, timeout=5.0, server_id=None, api_key=None)
    def versions(self) -> tuple[dict[str, int], int | None]; def trash_versions(self) -> dict[str, int]; def item(self, key) -> dict
```

______________________________________________________________________

## Phase 1 — compile: the tracers, then the wrapper

If any tracer in Task 1 fails, stop this phase: ship Tasks 4, 5 and 6 without Tasks 2 and 3, and record the failure in "Tracer results" below (spec §4.3: "the fallback is to defer compile to its own spec").

### Task 1: Tracers before any compile task (spec §3.1 alias probe, §4.3 "Tracers, before any compile task is written")

Manual, one sitting, on a scratch vault. Record each result as a dated line under "Tracer results" at the end of this task and one dated sentence in the spec's §4.3 tracer paragraph.

**Files:**

- Modify: `docs/superpowers/plans/2026-09-07-ingest-redesign-b-compile.md` (this section's results), `docs/superpowers/specs/2026-09-06-import-redesign-design.md` §4.3 (one sentence: "Tracers run 2026-MM-DD: \<pass|fail> — see the plan.")

- [ ] **Step 1: Install the tool at the pin and confirm doctor sees it**

```bash
claude plugin marketplace add AgriciDaniel/claude-obsidian
claude plugin install claude-obsidian@agricidaniel-claude-obsidian
python3 -c "import json,pathlib;p=json.load(open(pathlib.Path.home()/'.claude/plugins/installed_plugins.json'))['plugins']['claude-obsidian@agricidaniel-claude-obsidian'][0];print(p['gitCommitSha'],p['installPath'])"
```

Expected: a sha starting `32ac5a0` (v2.2.0; measured 2026-09-14: `32ac5a02c4e082e4a5628ca810776375e134708e`, installPath `~/.claude/plugins/cache/agricidaniel-claude-obsidian/claude-obsidian/2.2.0`). The pin moved from `ad67087` to `32ac5a0` on 2026-09-14 (operator decision A) after the controller diffed the two: `ledgers.py` byte-identical, the CLI verbs, flag shapes and exit codes unchanged, `wiki-ingest`'s write set unchanged; the move lands as one Task 1 commit before the tracers (`scaffold._COMPILE_PIN`, `tests/test_doctor.py`, `tests/test_scaffold.py`, spec §4.1, `ATTRIBUTION.md`), so this doctor run reads `compile-tool` MATCHED. If the marketplace has moved past the pin again, pin locally is **not** available (`claude plugin install` takes no version or commit and the cache is not a git checkout) — record the sha found, treat `compile-tool` UNMATCHED as the tracer's finding, and the operator decides whether to move the pin once more after the same diff.

- [ ] **Step 2: T1 — the plugin loads whole and an ordinary capture run still completes**

Start a Claude Code session in a scratch vault (`scratch=$(mktemp -d); python -m research_vault scaffold --vault "$scratch"`), with the research-vault plugin and claude-obsidian both loaded. In that session run `python -m research_vault capture jakesch.etal2023a --vault "$scratch" --base http://localhost:23129` and then `python -m research_vault doctor --vault "$scratch"`. Expected: both complete; no context compaction is forced during the run; `compile-tool` MATCHED. Record `/context` (or the session's reported token cost) so the "context cost" claim is a number.

- [ ] **Step 3: T2 — `mode set` writes the folder names and `mode get` reads them back**

```bash
CORE="$installPath/scripts/claude-obsidian.py"
python3 "$CORE" adopt "$scratch" | tee /tmp/adopt.json     # dry run: read changed_paths and approved_plan_sha256
python3 "$CORE" adopt "$scratch" --apply --approved-plan-sha256 "$(jq -r .approved_plan_sha256 /tmp/adopt.json)" --operation-id "$(jq -r .operation.operation_id /tmp/adopt.json)" --generated-at "$(jq -r .generated_at /tmp/adopt.json)"
python3 "$CORE" mode set generic --vault "$scratch" | tee /tmp/mode.json
python3 "$CORE" mode set generic --vault "$scratch" --apply --approved-plan-sha256 "$(jq -r .approved_plan_sha256 /tmp/mode.json)" --operation-id "$(jq -r .operation.operation_id /tmp/mode.json)" --generated-at "$(jq -r .generated_at /tmp/mode.json)"
python3 "$CORE" mode get --vault "$scratch"
```

Expected: `mode get` reports `sources_folder: wiki/sources/`, `concepts_folder: wiki/concepts/` and, since v2.2.0, `questions_folder: wiki/questions/`; `.vault-meta/mode.json` exists; `adopt` created `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, `wiki/overview.md`, `.raw/.manifest.json`, `wiki/meta/ledgers/*.json`, `.claude-obsidian.json`, `.obsidian/*`, and **did not overwrite** the vault's `.gitignore` (measured 2026-09-14 T2: it leaves an existing file untouched, silently rather than by refusing; append its rules by hand: `.vault-meta/`, `.mcp.json`, `.trash/`). (If the exact flag names differ from the ones above, read `python3 "$CORE" adopt --help`; the approve-then-apply shape is `_require_approved_plan` in `claude_obsidian/cli.py:86-104`.)

- [ ] **Step 4: T3 — a compile run over three captured sources writes only under `wiki/`**

Capture three sources into the scratch vault (`capture A B C --base http://localhost:23129`), snapshot `literatures/` and `fulltext/` (`find "$scratch/literatures" "$scratch/fulltext" -type f -exec sha256sum {} + | sort > /tmp/before.txt`). In the session, invoke the tool's `wiki-ingest` skill on the three `fulltext/<key>.md` files (hand it the paths; Task 2's wrapper is not built yet). Approve its bundle by hash, apply. Then:

```bash
find "$scratch/literatures" "$scratch/fulltext" -type f -exec sha256sum {} + | sort | diff - /tmp/before.txt && echo "literatures and fulltext byte-identical"
git -C "$scratch" status --porcelain | grep -v '^?? wiki/\|^ M wiki/\|^?? \.raw/\|^?? \.claude-obsidian\.json\|^?? \.obsidian/' ; echo "(nothing above this line means only wiki/ changed)"
```

Expected: byte-identical evidence and text layers; every changed path under `wiki/` (plus the tool's own dotfiles). Record what `wiki/log.md` looks like after the run: if it carries a `## ` heading that is not `## YYYY-MM-DD`, `okf-structure` will fail on it — record that as a fourth conflict and decide with the author whether `wiki/log.md` joins the `wiki/index.md` exemption (a one-line addition to `structure._EXEMPT_INDEXES`' sibling set and to ADR 0001).

Then the refresh that completes the notes (spec §3.3 step 5): `capture A B C --base http://localhost:23129` again. Expected: each of the three notes now opens with `## Compiled` and one `![[<page path>]]` per path in the ledger's `pages[]` for its text file; `fulltext/` is byte-identical to `/tmp/before.txt`; a third `capture A B C` reports `matched — NOOP` for all three. Record the page paths the ledger held (they are the tool's titles) and whether Obsidian renders the embed inline.

- [ ] **Step 5: T4 — the tool's pages pass `verify --surface commit`**

```bash
python -m research_vault verify --vault "$scratch" --offline --surface commit --git-base "$(git -C "$scratch" rev-parse HEAD)" --git-candidate worktree; echo "exit $?"
```

Expected: exit 0; no `okf-frontmatter` finding on `wiki/**`; `wiki/index.md` exempt; `captured-set` MATCHED (the pages cite only captured keys); `.raw/`, `.vault-meta/` unwalked. Record the counts line.

- [ ] **Step 6: T5 — Obsidian's `[[Title]]` resolution (spec §3.1)**

Open the scratch vault in Obsidian. In a scratch note type `[[<the title of one captured source>]]` and follow the link; then `[[<its citation key>]]`. Expected per the documentation: the title link opens the tool's `wiki/sources/<Title>.md` (exact filename beats alias) and the key link opens the literature note. Record which file each opened. Either result is acceptable; the record is what §3.1 asks for, and the captured-set lint's resolution order (Part A Task 15) already treats a page filename as a page.

- [ ] **Step 7: Record and commit**

Append under this heading:

```markdown
#### Tracer results

- 2026-MM-DD T1: <pass|fail> — <one line>
- 2026-MM-DD T2: ...
- 2026-MM-DD T3: ...
- 2026-MM-DD T4: ...
- 2026-MM-DD T5: title link opened <file>; key link opened <file>
```

and the one sentence in the spec. Commit:

```bash
git commit -m "record the compile tracers (ingest spec §4.3)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- docs/superpowers/plans/2026-09-07-ingest-redesign-b-compile.md docs/superpowers/specs/2026-09-06-import-redesign-design.md
```

### Task 2: The compile wrapper (spec §4.3, §4.4, §4.5)

Glue tier: it selects, fills a ledger record, calls the tool's CLI. It carries no prompt. The tool's own LLM skill writes the pages afterwards from the records the wrapper registered.

**Files:**

- Create: `research_vault/compile.py`, `tests/test_compile.py`
- Modify: `research_vault/__main__.py` (`compile KEY... --vault PATH [--approved-plan-sha256 SHA] [--all]`), `research_vault/inbox.py` (`CHECK_IDS` add `compile`), `docs/terminology.md` §4.4

**Interfaces:**

- Consumes: `captured.captured_set`, `notes.read_provenance`, `frontmatter.parse`, `fulltext.path_for`, `scaffold._installed_plugins`, `paths.load_machine_config`, `subprocess.run` on `python3 <root>/scripts/claude-obsidian.py transaction inspect|apply BUNDLE --vault V [--approved-plan-sha256 SHA]`.
- Produces: the Interface index `research_vault/compile.py` block. `stable_source_id("file", "fulltext/ABCD1234.md", "a"*64) == "src-2a09635ec6bad4de1b13"` (measured against the tool's own function, 2026-09-07). A ledger record:

```json
{
  "origin": {"kind": "file", "locator": "fulltext/D7EJ9FTG.md"},
  "content_kind": "document",
  "authority": "unknown",
  "review_status": "unreviewed",
  "title": "<the note's title>",
  "content_sha256": "<the note's compile-input-sha256, which is the fulltext sha256 of the locator's attachment>",
  "ingested_at": "<today>",
  "retrieved_at": "<the note's accessed>",
  "refresh_due": null,
  "independence_key": "<citation key>",
  "supersedes": null,
  "pages": []
}
```

The bundle: `{"schema": "claude-obsidian.transaction.v1", "operation_id": "research-vault-compile-<YYYYMMDDTHHMMSSZ>", "operation_type": "ingest", "expected_hashes": {"wiki/meta/ledgers/source-ledger.json": "<sha256 of the current file or null>"}, "writes": [{"path": "wiki/meta/ledgers/source-ledger.json", "mode": "replace"|"create", "content": "<merged ledger JSON>", "sha256": "<sha256 of content>"}]}` written to `.research-vault/compile/<operation_id>.json`. `plan()` runs `transaction inspect` and returns `(bundle_path, inspect_json)`; `apply()` runs `transaction apply --approved-plan-sha256` and returns `Outcome("compile", "<operation id>", MATCHED, "matched — <changed paths>")`, `UNMATCHED "mismatch — <ERR code>"` on exit 2/75, `UNREACHABLE "outage — tool not installed"` when no root resolves.

- [ ] **Step 1: Write the failing tests**

`tests/test_compile.py`:

```python
import hashlib
import json
import subprocess

import pytest

from research_vault import Result, compile as compile_mod


def test_stable_source_id_matches_the_tools_own_function():
    assert compile_mod.stable_source_id("file", "fulltext/ABCD1234.md", "a" * 64) == "src-2a09635ec6bad4de1b13"
    assert compile_mod.stable_source_id("FILE", "fulltext/ABCD1234.md", "A" * 64) == "src-2a09635ec6bad4de1b13"


def _note(vault, key="jakesch.etal2023a", sha="f" * 64):
    (vault / "literatures" / f"{key}.md").write_text(
        f'---\ntype: "literature"\ntitle: "Co-writing"\naliases:\n  - "Co-writing"\n'
        f'zotero-server-id: "S"\nzotero-item-key: "E352DFS8"\nzotero-item-version: 544\ncitationKey: "{key}"\n'
        f'attachments:\n  - {{key: "D7EJ9FTG", version: 551, md5: "m", contentType: "application/pdf", filename: "a.pdf"}}\n'
        f'fulltext:\n  - {{attachment-key: "D7EJ9FTG", sha256: "{sha}"}}\ncompile-input-sha256: "{sha}"\n'
        f'accessed: "2026-09-07"\ngenerated: {{by: "research_vault/0.1.0", at: "2026-09-07T00:00:00Z"}}\n---\n'
    )
    (vault / "fulltext").mkdir(exist_ok=True)
    (vault / "fulltext" / "D7EJ9FTG.md").write_text('---\ntype: "fulltext"\n---\ntext\n')


def test_ledger_record_and_bundle_shape(tmp_vault, monkeypatch):
    _note(tmp_vault)
    monkeypatch.setattr(compile_mod, "tool_root", lambda vault: None)
    with pytest.raises(compile_mod.ToolMissingError):
        compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    records = compile_mod.records_for(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    source_id, record = next(iter(records.items()))
    assert source_id == compile_mod.stable_source_id("file", "fulltext/D7EJ9FTG.md", "f" * 64)
    assert record["origin"] == {"kind": "file", "locator": "fulltext/D7EJ9FTG.md"}
    assert record["content_sha256"] == "f" * 64
    assert record["title"] == "Co-writing"
    assert record["review_status"] == "unreviewed"
    assert record["pages"] == []
    assert record["retrieved_at"] == "2026-09-07"
    assert record["ingested_at"] == "2026-09-07"


def test_records_skip_notes_without_a_compile_input(tmp_vault):
    _note(tmp_vault)
    text = (tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text().replace('compile-input-sha256: "' + "f" * 64 + '"\n', "")
    (tmp_vault / "literatures" / "jakesch.etal2023a.md").write_text(text)
    assert compile_mod.records_for(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07") == {}


def _fake_tool(tmp_path, monkeypatch, *, inspect_ok=True, apply_code=0):
    root = tmp_path / "tool"
    (root / "scripts").mkdir(parents=True)
    script = root / "scripts" / "claude-obsidian.py"
    script.write_text(
        "import json,sys\n"
        "args=sys.argv[1:]\n"
        "if args[:2]==['transaction','inspect']:\n"
        f"    print(json.dumps({{'schema':'claude-obsidian.transaction-plan.v1','valid':{str(inspect_ok)},'approval_sha256':'abc123','changed_paths':['wiki/meta/ledgers/source-ledger.json']}}))\n"
        "elif args[:2]==['transaction','apply']:\n"
        "    assert '--approved-plan-sha256' in args\n"
        f"    print(json.dumps({{'schema':'claude-obsidian.transaction-result.v1','operation_id':'op','changed_paths':['wiki/meta/ledgers/source-ledger.json']}})); sys.exit({apply_code})\n"
    )
    monkeypatch.setattr(compile_mod, "tool_root", lambda vault: root)
    return root


def test_selected_notes_skips_a_non_utf8_note_without_crashing(tmp_vault):
    """A corrupted note anywhere in ``literatures/`` must not crash the whole
    ``compile`` operation -- ``broken.md`` sorts before ``jakesch.etal2023a.md``
    so this also kills a ``continue`` -> ``break`` mutant: the wanted note, read
    later in the same walk, must still yield."""
    (tmp_vault / "literatures" / "broken.md").write_bytes(b"\xff\xfe")
    _note(tmp_vault)
    records = compile_mod.records_for(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    assert len(records) == 1


def test_selected_notes_skips_an_unreadable_note_without_crashing(tmp_vault):
    """A note path that raises ``OSError`` on read (a directory, so
    ``read_bytes()`` raises ``IsADirectoryError``) is skipped the same way a
    bad-encoding note is -- the ``except`` tuple really catches ``OSError``.
    ``dir.md`` sorts before ``jakesch.etal2023a.md``."""
    (tmp_vault / "literatures" / "dir.md").mkdir()
    _note(tmp_vault)
    records = compile_mod.records_for(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    assert len(records) == 1


def test_plan_writes_the_bundle_and_apply_reports_four_state(tmp_vault, tmp_path, monkeypatch):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    bundle_path, inspected = compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    assert bundle_path.parent == tmp_vault / ".research-vault" / "compile"
    bundle = json.loads(bundle_path.read_text())
    assert bundle["operation_type"] == "ingest"
    (write,) = bundle["writes"]
    assert write["path"] == "wiki/meta/ledgers/source-ledger.json"
    assert write["mode"] == "create"
    assert write["sha256"] == hashlib.sha256(write["content"].encode()).hexdigest()
    assert bundle["expected_hashes"] == {"wiki/meta/ledgers/source-ledger.json": None}
    assert json.loads(write["content"])["schema"] == "claude-obsidian.source-ledger.v1"
    assert inspected["approval_sha256"] == "abc123"

    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert outcome.result is Result.MATCHED
    assert "source-ledger.json" in outcome.reason


def test_plan_merges_into_an_existing_ledger_and_pins_its_hash(tmp_vault, tmp_path, monkeypatch):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    ledger = tmp_vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True)
    existing = {"schema": "claude-obsidian.source-ledger.v1", "generated_at": "2026-09-01T00:00:00Z", "sources": {"src-keep": {"origin": {"kind": "url", "locator": "https://x/"}}}}
    ledger.write_text(json.dumps(existing))
    bundle_path, _ = compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    bundle = json.loads(bundle_path.read_text())
    assert bundle["expected_hashes"]["wiki/meta/ledgers/source-ledger.json"] == hashlib.sha256(ledger.read_bytes()).hexdigest()
    merged = json.loads(bundle["writes"][0]["content"])["sources"]
    assert "src-keep" in merged
    assert len(merged) == 2
    assert bundle["writes"][0]["mode"] == "replace"


def test_apply_maps_tool_exit_codes(tmp_vault, tmp_path, monkeypatch):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch, apply_code=2)
    bundle_path, _ = compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith("mismatch")
    monkeypatch.setattr(compile_mod, "tool_root", lambda vault: None)
    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert outcome.result is Result.UNREACHABLE
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_compile.py -q`
Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Register `compile`; implement `research_vault/compile.py`; wire the verb**

```python
"""The compile wrapper: selection, locators, ledger records, invocation (spec §4.5).

Glue. It names ``fulltext/<attachment key>.md`` as each source's locator,
fills the tool's source-ledger record from the captured metadata, and drives
the tool's own ``transaction inspect`` / ``transaction apply``. It never
writes under ``wiki/`` itself and carries no prompt.
"""

import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath

from . import captured, clock, frontmatter, notes, paths
from .outcome import Outcome, Result

LEDGER_PATH = notes.LEDGER_PATH
LEDGER_SCHEMA = "claude-obsidian.source-ledger.v1"
BUNDLE_SCHEMA = "claude-obsidian.transaction.v1"
PLUGIN_ID = "claude-obsidian@agricidaniel-claude-obsidian"
CHECK = "compile"
BUNDLE_DIR = ".research-vault/compile"


class ToolMissingError(RuntimeError):
    """The compile tool is not installed and machine.json names no root."""


def stable_source_id(kind: str, locator: str, content_sha256: str | None) -> str:
    """Byte-for-byte the tool's ``ledgers.stable_source_id`` (read at ad67087; byte-identical at 32ac5a0)."""
    normalized = PurePosixPath(locator).as_posix() if kind.casefold() == "file" else locator
    digest = hashlib.sha256(
        f"{kind.casefold()}\0{normalized}\0{(content_sha256 or '').casefold()}".encode("utf-8", errors="surrogatepass")
    ).hexdigest()
    return f"src-{digest[:20]}"


def tool_root(vault_root) -> Path | None:
    config = paths.load_machine_config(Path(vault_root))
    override = config.get("claude_obsidian_root")
    if isinstance(override, str) and override.strip():
        return Path(override)
    from .scaffold import _installed_plugins

    records = _installed_plugins().get(PLUGIN_ID) or []
    install_path = records[0].get("installPath") if records else None
    return Path(install_path) if isinstance(install_path, str) else None


def _selected_notes(vault: Path, keys):
    wanted = set(keys)
    for path in sorted((vault / "literatures").glob("*.md")):
        try:
            # bytes.decode()'s default codec already is utf-8, so this carries
            # no literal codec name a mutation gate could flip with no effect.
            text = path.read_bytes().decode()
        except (OSError, UnicodeError):
            # Skipped exactly as an unparseable note is (read_provenance ->
            # None); captured-set/okf-frontmatter are where it's reported.
            continue
        provenance = notes.read_provenance(text)
        if provenance is None or provenance.citation_key not in wanted:
            continue
        data, _ = frontmatter.parse(text)
        yield provenance, data


def ledger_record(citation_key, provenance, data, today) -> tuple[str, dict] | None:
    if not provenance.compile_input_sha256:
        return None
    key = next((f["attachment-key"] for f in provenance.fulltext if f.get("sha256") == provenance.compile_input_sha256), None)
    if key is None:
        return None
    locator = f"fulltext/{key}.md"
    record = {
        "origin": {"kind": "file", "locator": locator},
        "content_kind": "document",
        "authority": "unknown",
        "review_status": "unreviewed",
        "title": str(data.get("title") or citation_key),
        "content_sha256": provenance.compile_input_sha256,
        "ingested_at": today,
        "retrieved_at": str(data.get("accessed") or today),
        "refresh_due": None,
        "independence_key": citation_key,
        "supersedes": None,
        "pages": [],
    }
    return stable_source_id("file", locator, provenance.compile_input_sha256), record


def records_for(vault_root, keys, *, today=None) -> dict[str, dict]:
    vault = Path(vault_root)
    today = clock.today(today)
    records = {}
    for provenance, data in _selected_notes(vault, keys):
        entry = ledger_record(provenance.citation_key, provenance, data, today)
        if entry:
            records[entry[0]] = entry[1]
    return records


def _run(root: Path, vault: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(root / "scripts" / "claude-obsidian.py"), *args, "--vault", str(vault)],
        capture_output=True, text=True, check=False,
    )


def plan(vault_root, keys, *, today=None) -> tuple[Path, dict]:
    vault = Path(vault_root)
    root = tool_root(vault)
    if root is None:
        raise ToolMissingError("claude-obsidian is not installed")
    today = clock.today(today)
    ledger = vault / LEDGER_PATH
    if ledger.is_file():
        raw = ledger.read_bytes()
        current = json.loads(raw)
        expected = hashlib.sha256(raw).hexdigest()
        mode = "replace"
    else:
        current = {"schema": LEDGER_SCHEMA, "generated_at": f"{today}T00:00:00Z", "sources": {}}
        expected = None
        mode = "create"
    sources = dict(current.get("sources", {}))
    for source_id, record in records_for(vault, keys, today=today).items():
        # An id already registered keeps its record: its review_status and
        # pages[] are the tool's (spec §4.5), and a changed text has a new id.
        sources.setdefault(source_id, record)
    merged = {**current, "schema": LEDGER_SCHEMA, "generated_at": f"{today}T00:00:00Z", "sources": sources}
    content = json.dumps(merged, indent=2, sort_keys=True) + "\n"
    operation_id = "research-vault-compile-" + datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    bundle = {
        "schema": BUNDLE_SCHEMA,
        "operation_id": operation_id,
        "operation_type": "ingest",
        "expected_hashes": {LEDGER_PATH: expected},
        "writes": [{"path": LEDGER_PATH, "mode": mode, "content": content, "sha256": hashlib.sha256(content.encode()).hexdigest()}],
    }
    bundle_dir = vault / BUNDLE_DIR
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = bundle_dir / f"{operation_id}.json"
    bundle_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    completed = _run(root, vault, "transaction", "inspect", str(bundle_path))
    try:
        inspected = json.loads(completed.stdout or "{}")
    except ValueError:
        inspected = {}
    inspected.setdefault("exit", completed.returncode)
    inspected.setdefault("stderr", completed.stderr.strip())
    return bundle_path, inspected


def apply(vault_root, bundle_path, approved_sha256) -> Outcome:
    vault = Path(vault_root)
    root = tool_root(vault)
    operation = Path(bundle_path).stem
    if root is None:
        return Outcome(CHECK, operation, Result.UNREACHABLE, "outage — claude-obsidian is not installed")
    completed = _run(root, vault, "transaction", "apply", str(bundle_path), "--approved-plan-sha256", approved_sha256)
    if completed.returncode == 0:
        try:
            changed = json.loads(completed.stdout).get("changed_paths", [])
        except ValueError:
            changed = []
        return Outcome(CHECK, operation, Result.MATCHED, "matched — " + (", ".join(changed) or "no paths reported"))
    detail = (completed.stderr or completed.stdout).strip().splitlines()[-1:] or [f"exit {completed.returncode}"]
    return Outcome(CHECK, operation, Result.UNMATCHED, f"mismatch — {detail[0]}")
```

CLI:

```python
def cmd_compile(args):
    keys = list(args.keys) or (sorted(captured.captured_set(args.vault)) if args.all else [])
    if args.approved_plan_sha256:
        outcome = compile_mod.apply(args.vault, args.bundle, args.approved_plan_sha256)
        print(f"{outcome.result.value} {outcome.target} — {outcome.reason}")
        if outcome.result is not Result.MATCHED:
            _hold(args.vault, compile_mod.CHECK, outcome.target, outcome.result, outcome.reason)
        return {Result.MATCHED: 0, Result.UNMATCHED: 1, Result.UNREACHABLE: 3, Result.SKIPPED: 0}[outcome.result]
    try:
        bundle_path, inspected = compile_mod.plan(args.vault, keys)
    except compile_mod.ToolMissingError as error:
        print(f"UNREACHABLE compile — outage — {error}", file=sys.stderr)
        return 3
    print(json.dumps({"bundle": str(bundle_path), **inspected}, indent=2))
    print(f"apply with: python3 -m research_vault compile --vault {args.vault} --bundle {bundle_path} --approved-plan-sha256 {inspected.get('approval_sha256', '<sha>')}")
    return 0 if inspected.get("valid") else 1
```

parser: `compile_cmd = sub.add_parser("compile", parents=[common]); compile_cmd.add_argument("keys", nargs="*"); compile_cmd.add_argument("--vault", required=True); compile_cmd.add_argument("--all", action="store_true"); compile_cmd.add_argument("--bundle"); compile_cmd.add_argument("--approved-plan-sha256")`; `main()` errors when `--approved-plan-sha256` is given without `--bundle`. Import as `from . import compile as compile_mod` (the module shadows a builtin name only inside the package namespace; ruff `A005` may object — if it does, name the module `research_vault/compiler.py` and update the Interface index and this task consistently).

- [ ] **Step 4: Run the suite and form owners; one live plan against the tracer vault; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS, clean. Live: `python -m research_vault compile jakesch.etal2023a --vault "$scratch"` prints a `valid: true` plan naming `wiki/meta/ledgers/source-ledger.json`; applying it with the printed hash returns MATCHED; `python -m research_vault verify --vault "$scratch" --offline` reports `captured-set` MATCHED with no `not-captured` ledger finding.

```bash
git commit -m "add the compile wrapper (ingest spec §4.5)

Selection from the captured set, fulltext/<attachment key>.md as the
locator, the ledger record filled from the tuple, and the tool's own
inspect-then-apply gate driven with its approval hash.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests docs
```

### Task 2b: The commit surface accepts capture's own writes — `evidence-layer`'s write legs require the writer attestation (spec §6 amendment of 2026-09-16; Task 1 T4 finding)

Independent of Tasks 1–3 (no compile dependency); runs at once, in parallel with Task 2. Operator decision of 2026-09-16 (option 1 of three: this; ack per note; defer to the audit).

**Why.** `lint_evidence_layer` reports every base→candidate change under `literatures/` — added, body changed, renamed, deleted — as UNMATCHED, the check sits in the commit and publish closing sets, and the vault template's pre-commit hook runs the commit surface. Measured by Task 1 T4 on 2026-09-14: a capture, a compile refresh (`## Compiled` inserted) or a propagate blocks the next commit until every note is acknowledged. The legs were the foundation design's human gate on a human-written evidence layer; the ingest spec made the whole note body capture's (§3: "capture writes literature notes … and touches nothing a person wrote") and retired admission (§1.1). The same function already carries the right mechanism for its frontmatter leg: a machine-owned key may change iff `generated` changed in the same diff with a machine-class `by` (`_frontmatter_attestation_outcomes`, "writer attestation"), and `notes.render_note` bumps `generated` on every content change (`notes.py:503-504`). This task puts the body, added and renamed legs under that one rule. A hand edit that refreshes `managed-sha256` but not `generated` is still drift; a forged attestation is the stated boundary the frontmatter leg already declares. A deletion stays a finding: no verb deletes a literature note (ADR 0003).

**Files:**

- Modify: `research_vault/lints.py` (`lint_evidence_layer`, `_frontmatter_attestation_outcomes`; add `_write_attested`, `_note_identity`; the per-key diagnostic reaches renamed pairs, which closes #21), `tests/test_lints.py` (`test_body_change_always_yields_typed_evidence_finding_with_fresh_witness` replaced by the two parametrized tests below; `test_prose_appended_below_the_note_is_a_body_change` rewritten; the reason string in `test_unparseable_base_frontmatter_does_not_auto_attest_via_a_valid_candidate`'s expected set), `docs/superpowers/specs/2026-09-06-import-redesign-design.md` §6 (the dated sentence is already on `main` at the commit that added this task; nothing to write), `docs/terminology.md` (nothing: check id and reason code unchanged)

**Interfaces:**

- Consumes: `notes.read_provenance(text) -> Provenance | None` (identity `(server_id, item_key)`, decision 08), `notes.validate_managed_witness`, `notes._valid_generated`, `lints._machine_attested`, `lints._frontmatter`, `lints._field`, `lints._body_bytes`, `lints._literature_files`.

- Produces: `lint_evidence_layer(base_snapshot, candidate_snapshot) -> list[Outcome]` with reasons `drift — literature note added without writer attestation`, `drift — literature note body changed without writer attestation`, `drift — literature note renamed without writer attestation` (with `extra={"prior_path": RepoPath(old)}`), `drift — literature note deleted`, the witness `schema-violation`/`outage` reasons and the per-key `drift — <key> changed without writer attestation` reasons, all unchanged in check id (`evidence-layer`) and reason code (`drift`). Attested writes yield no row.

- [ ] **Step 1: Write the failing tests**

In `tests/test_lints.py`, delete `test_body_change_always_yields_typed_evidence_finding_with_fresh_witness` (its "add" and "edit" expectations are the behaviour this task retires) and add, beside `_refresh_body_witness`:

```python
_FIXTURE_GENERATED = 'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}'


def _bump_generated(text: str, by: str = "research_vault/0.1.0") -> str:
    """What `notes.render_note` does on every content change: a fresh `at`."""
    return must_replace(
        text, _FIXTURE_GENERATED, f'generated: {{by: "{by}", at: "2026-09-16T09:00:00Z"}}'
    )


def _base_tree(vault) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def _evidence_rows(vault, base):
    return [
        item
        for item in lints.lint_evidence_layer(
            gitstate.snapshot_tree(vault, base), gitstate.snapshot_worktree(vault)
        )
        if item.result is not Result.MATCHED
    ]


@pytest.mark.parametrize("write", ["add", "refresh", "rename"])
def test_an_attested_write_to_the_evidence_layer_is_not_drift(fixture_vault, write):
    """Capture, the compile refresh and propagate bump `generated` under the
    machine actor on every content change (`notes.render_note`); the commit
    surface must let those writes through, or every capture blocks the next
    commit (ingest spec §6 amendment of 2026-09-16, Part B Task 1 T4)."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literatures" / "smith2020.md"
    if write == "add":
        # A new capture: a note carrying a valid witness and a machine-class `generated`.
        added = fixture_vault / "literatures" / "added.md"
        added.write_text(
            must_replace(source.read_text(), 'citationKey: "smith2020"', 'citationKey: "added"')
        )
        _refresh_body_witness(added)
    elif write == "refresh":
        # The compile refresh: the body changes, `generated` moves, the witness is fresh.
        source.write_text(
            _bump_generated(
                source.read_text() + "\n## Compiled\n\n![[wiki/sources/Mortality decline.md]]\n"
            )
        )
        _refresh_body_witness(source)
    else:
        # Propagate: the note re-keys, is re-rendered at the new path, same Zotero identity.
        renamed = fixture_vault / "literatures" / "smith2020b.md"
        renamed.write_text(
            _bump_generated(
                must_replace(source.read_text(), 'citationKey: "smith2020"', 'citationKey: "smith2020b"')
            )
        )
        _refresh_body_witness(renamed)
        source.unlink()

    rows = _evidence_rows(fixture_vault, base)

    assert rows == [], rows


@pytest.mark.parametrize("write", ["add", "edit", "rename", "delete"])
def test_an_unattested_write_to_the_evidence_layer_is_drift(fixture_vault, write):
    """The same four shapes with no writer attestation — a hand-written note,
    a hand edit that refreshed the witness, a bare `mv`, a deletion — each
    surface as exactly the drift row the shape names."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literatures" / "smith2020.md"
    if write == "add":
        added = fixture_vault / "literatures" / "added.md"
        added.write_text(
            must_replace(
                must_replace(source.read_text(), 'citationKey: "smith2020"', 'citationKey: "added"'),
                _FIXTURE_GENERATED,
                'generated: {by: "human:eran", at: "2026-09-16T09:00:00Z"}',
            )
        )
        _refresh_body_witness(added)
        expected = ("path-bytes:literatures/added.md", "drift — literature note added without writer attestation")
    elif write == "edit":
        source.write_text(must_replace(source.read_text(), "# Mortality decline", "# Changed"))
        _refresh_body_witness(source)
        expected = ("path-bytes:literatures/smith2020.md", "drift — literature note body changed without writer attestation")
    elif write == "rename":
        source.rename(fixture_vault / "literatures" / "renamed.md")
        expected = ("path-bytes:literatures/renamed.md", "drift — literature note renamed without writer attestation")
    else:
        source.unlink()
        expected = ("path-bytes:literatures/smith2020.md", "drift — literature note deleted")

    rows = _evidence_rows(fixture_vault, base)

    matching = [item for item in rows if (item.target, item.reason) == expected]
    assert len(matching) == 1, rows
    assert matching[0].result is Result.UNMATCHED
    assert matching[0].target_kind == "repo-path"
    if write == "rename":
        # Outcome.__post_init__ encodes a RepoPath in extra to its path-bytes string.
        assert matching[0].extra["prior_path"] == "path-bytes:literatures/smith2020.md"


def test_a_renamed_note_with_a_hand_edited_key_names_the_key(fixture_vault):
    """#21: the per-key attestation diagnostic reaches a renamed pair, so a
    bare `mv` that also edits a machine-owned key reports the key beside the
    wholesale rename row."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literatures" / "smith2020.md"
    renamed = fixture_vault / "literatures" / "renamed.md"
    renamed.write_text(
        must_replace(source.read_text(), "zotero-item-version: 12", "zotero-item-version: 13")
    )
    source.unlink()

    reasons = {(item.target, item.reason) for item in _evidence_rows(fixture_vault, base)}

    assert reasons == {
        ("path-bytes:literatures/renamed.md", "drift — literature note renamed without writer attestation"),
        ("path-bytes:literatures/renamed.md", "drift — zotero-item-version changed without writer attestation"),
    }, reasons


def test_rename_pairs_by_zotero_identity_before_body_bytes(fixture_vault):
    """Propagate re-keys and re-renders, so the bytes differ; the pairing is
    decision 08's identity. A note with no tuple still pairs by body bytes."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literatures" / "smith2020.md"
    renamed = fixture_vault / "literatures" / "smith2020b.md"
    renamed.write_text(
        must_replace(source.read_text(), "# Mortality decline", "# Mortality decline, re-keyed")
    )
    _refresh_body_witness(renamed)  # bytes differ from the base; `generated` untouched
    # `_body_bytes` excludes frontmatter, so the pairing must be decided on a
    # body that differs; the identity leg pairs it where the body leg cannot.
    source.unlink()

    rows = _evidence_rows(fixture_vault, base)

    assert [item.reason for item in rows] == [
        "drift — literature note renamed without writer attestation"
    ], rows
    assert rows[0].extra["prior_path"] == "path-bytes:literatures/smith2020.md"
```

Rewrite `test_prose_appended_below_the_note_is_a_body_change` to:

```python
def test_prose_appended_below_the_note_is_drift_with_or_without_a_fresh_witness(
    fixture_vault,
):
    """The free region is retired: the whole body is capture's. Hand-added
    prose is a stale witness when the person did not refresh it, and an
    unattested body change when they did; it is never silent."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literatures" / "smith2020.md"
    source.write_text(source.read_text() + "hand-written prose\n")

    stale = {item.reason for item in _evidence_rows(fixture_vault, base)}
    assert any(reason.startswith("schema-violation") for reason in stale), stale

    _refresh_body_witness(source)
    fresh = {item.reason for item in _evidence_rows(fixture_vault, base)}
    assert "drift — literature note body changed without writer attestation" in fresh, fresh
    assert not any(reason.startswith("schema-violation") for reason in fresh), fresh
```

In `test_unparseable_base_frontmatter_does_not_auto_attest_via_a_valid_candidate`, the expected set's last member `"drift — literature note body changed"` becomes `"drift — literature note body changed without writer attestation"`.

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_lints.py -q -k "evidence_layer or prose_appended or pairs_by or unparseable_base"`
Expected: FAIL — the three attested cases each carry a drift row; the unattested cases carry the old reason strings; the identity pairing case reads "deleted" plus "added".

- [ ] **Step 3: Implement**

In `research_vault/lints.py`, add after `_machine_attested`:

```python
def _write_attested(base_data: dict | None, candidate_data: dict | None) -> bool:
    """Whether a change to this note in this diff carries the writer attestation.

    One legality rule for the body and for every machine-owned key: a change
    is attested iff `generated` also changed in the same diff and the
    candidate's `generated` is validly shaped with a machine-class `by`. An
    unparseable base (`base_data is None`) has no prior state to compare
    against, so a validly machine-shaped candidate `generated` must not be
    read as evidence of a legitimate write — that would let an unreadable
    base auto-attest whatever hides behind it.
    """
    base_generated = _field(base_data, "generated")
    candidate_generated = _field(candidate_data, "generated")
    return (
        base_data is not None
        and base_generated != candidate_generated
        and _machine_attested(candidate_generated)
    )


def _note_identity(image: gitstate.FileImage | None) -> tuple[str, str] | None:
    """Decision 08's identity of a literature note, `(server id, item key)`,
    or None for a note that carries no complete tuple."""
    if image is None or image.kind != "file":
        return None
    try:
        text = (image.data or b"").decode("utf-8")
    except UnicodeDecodeError:
        return None
    provenance = notes.read_provenance(text)
    if provenance is None:
        return None
    return provenance.server_id, provenance.item_key
```

In `_frontmatter_attestation_outcomes`, replace the `base_generated` / `candidate_generated` / `generated_changed` / `attested = (...)` block with `attested = _write_attested(base_data, candidate_data)` and move the docstring's "unparseable base" paragraph onto `_write_attested` (it is printed there above). Replace `lint_evidence_layer` whole:

```python
def lint_evidence_layer(
    base_snapshot: gitstate.Snapshot,
    candidate_snapshot: gitstate.Snapshot,
) -> list[Outcome]:
    """Validate witnesses; report a deleted note and any write without attestation.

    Capture, the compile refresh and propagate are the only writers of
    `literatures/` (ingest spec §3; §6 amended 2026-09-16), and each of their
    writes bumps `generated` under the machine actor (`notes.render_note`).
    So an added note, a changed body and a renamed note are findings only
    when that attestation is absent — `_write_attested`, the rule the
    machine-owned keys already live under — and a deletion always is (ADR
    0003: no verb deletes a literature note). Stated boundary, shared with
    `_frontmatter_attestation_outcomes`: a forged attestation is deliberate
    circumvention, not this check's job.
    """
    outcomes = []
    base_files = _literature_files(base_snapshot)
    candidate_files = _literature_files(candidate_snapshot)

    for raw_path, image in sorted(candidate_files.items()):
        result, reason = notes.validate_managed_witness(image.data or b"")
        if result is not Result.MATCHED:
            outcomes.append(Outcome("evidence-layer", RepoPath(raw_path), result, reason))

    removed = set(base_files) - set(candidate_files)
    added = set(candidate_files) - set(base_files)
    # A rename is a removed path and an added path carrying the same note:
    # the same Zotero identity first (propagate re-keys and re-renders, so
    # the bytes differ), then the same body bytes for a note with no tuple.
    pairs: dict[bytes, bytes] = {}  # added path -> removed path
    unpaired_removed = set(removed)
    for pair_key in (_note_identity, _body_bytes):
        removed_by_key: dict[object, list[bytes]] = {}
        for raw_path in sorted(unpaired_removed):
            key = pair_key(base_files[raw_path])
            if key is not None:
                removed_by_key.setdefault(key, []).append(raw_path)
        for raw_path in sorted(added - set(pairs)):
            key = pair_key(candidate_files[raw_path])
            candidates = removed_by_key.get(key, []) if key is not None else []
            if candidates:
                old_path = candidates.pop(0)
                pairs[raw_path] = old_path
                unpaired_removed.discard(old_path)

    for raw_path in sorted(added):
        old_path = pairs.get(raw_path)
        candidate_data = _frontmatter(candidate_files[raw_path])
        if old_path is None:
            attested = _machine_attested(_field(candidate_data, "generated"))
            reason = "drift — literature note added without writer attestation"
            extra: dict[str, object] = {}
        else:
            base_data = _frontmatter(base_files[old_path])
            attested = _write_attested(base_data, candidate_data)
            reason = "drift — literature note renamed without writer attestation"
            extra = {"prior_path": RepoPath(old_path)}
            # The per-key diagnostic runs across the pair too (#21): a rename
            # that also hand-edits a machine-owned key names the key.
            outcomes.extend(_frontmatter_attestation_outcomes(raw_path, base_data, candidate_data))
        if not attested:
            outcomes.append(
                Outcome("evidence-layer", RepoPath(raw_path), Result.UNMATCHED, reason, extra=extra)
            )
    outcomes.extend(
        Outcome(
            "evidence-layer",
            RepoPath(raw_path),
            Result.UNMATCHED,
            "drift — literature note deleted",
        )
        for raw_path in sorted(unpaired_removed)
    )
    for raw_path in sorted(set(base_files) & set(candidate_files)):
        base_data = _frontmatter(base_files[raw_path])
        candidate_data = _frontmatter(candidate_files[raw_path])
        body_changed = _body_bytes(base_files[raw_path]) != _body_bytes(candidate_files[raw_path])
        if body_changed and not _write_attested(base_data, candidate_data):
            outcomes.append(
                Outcome(
                    "evidence-layer",
                    RepoPath(raw_path),
                    Result.UNMATCHED,
                    "drift — literature note body changed without writer attestation",
                )
            )
        outcomes.extend(_frontmatter_attestation_outcomes(raw_path, base_data, candidate_data))
    return _deduplicate(outcomes)
```

- [ ] **Step 4: Run to verify it passes; the whole suite; the gate on this module**

Run: `.venv/bin/python -m pytest tests/test_lints.py -q && .venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS. Then `python3 scripts/mutation_gate.py --base main --max-children 6 --child-address-space 4GiB` (gate mode; it measures `lints.py` as a changed module): expected `0 new survivors`; a new survivor is killed by one more test in this task, not accepted into the baseline. Report the gate's summary line verbatim.

- [ ] **Step 5: Commit**

```bash
git commit -m "evidence-layer: capture's own writes are not drift — the write legs require the writer attestation

Added, body-changed and renamed literature notes are findings only without the machine-actor generated bump the frontmatter leg already requires; a deletion stays one. Measured on Part B's tracer T4: a capture, a compile refresh or a propagate blocked the next commit through the vault hook until acknowledged per note. Ingest spec §6, amended 2026-09-16.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault/lints.py tests/test_lints.py
```

______________________________________________________________________

## Phase 2 — the skills' compile sections, docs, live legs

### Task 3: The compile sections of the skills, and `synthesis-conventions` (spec §6 "Rewritten skills: import-source, setup-vault and synthesis-conventions")

Part A Task 19 shipped `capture-source` and `setup-vault` without their compile sections, because `compile` did not exist until Task 2. This task adds those sections, rewrites `synthesis-conventions` for the adopted tool, and registers the plugin as a provision companion.

**Files:**

- Modify: `skills/capture-source/SKILL.md`, `skills/setup-vault/SKILL.md`, `skills/synthesis-conventions/SKILL.md`, `skills/evidence-conventions/SKILL.md` (`:16` "into a synthesis page" becomes the compiled layer under `wiki/` — Part A's deferred row 60, a one-word edit that rides with this rewrite; `skills/synthesis-conventions/SKILL.md:16,22` carry the same retired term), `research_vault/scaffold.py:23` (`PROVISION_COMPANIONS = ["kepano/obsidian-skills", "claude-obsidian@agricidaniel-claude-obsidian"]`), `research_vault/templates/vault/AGENTS.md` (the skills table row), `tests/test_capture_source_skill.py`, `tests/test_skill_files.py`, `tests/test_templates.py`

**Interfaces:**

- Consumes: Task 2b — after it, a capture, a compile refresh or a propagate commits through the vault's pre-commit hook without an acknowledgment, so no skill text says "ack each row" or "commit with --no-verify" (Task 1 T4's finding, closed by Task 2b).

- Consumes: the `compile` verb (Task 2: `compile KEY... --vault PATH` prints the plan and its approval hash; `compile --vault PATH --bundle BUNDLE --approved-plan-sha256 SHA` applies), the `compile-tool` doctor probe (Part A Task 16), the `captured-set` check (Part A Task 15), `scaffold.PROVISION_COMPANIONS`.

- Produces: three skills whose frontmatter passes `tests/test_skill_contracts.py` (name equals directory, description begins `Use when `, entry skills carry `disable-model-invocation: true`, every backticked check id names one the code files).

- [ ] **Step 1: Write the failing tests**

In `tests/test_capture_source_skill.py::test_capture_source_keeps_the_kept_rules`, add to the needle tuple:

```python
        "python3 -m research_vault compile", "--approved-plan-sha256", "wiki-ingest", "recompile-needed", "![[<page path>]]",
```

Append to `tests/test_capture_source_skill.py`:

```python
def test_synthesis_conventions_names_the_tool_and_the_seam():
    text = (REPOSITORY / "skills" / "synthesis-conventions" / "SKILL.md").read_text()
    for needle in (
        "claude-obsidian", "transaction inspect", "wiki-ingest", "`captured-set`",
        "[[<citation key>]]", "wiki/index.md", "two or more captured sources",
        "python3 -m research_vault compile",
    ):
        assert needle in text, needle
    assert "synthesis/" not in text
```

In `tests/test_skill_files.py`, add to the companions assertions:

```python
    assert "claude plugin marketplace add AgriciDaniel/claude-obsidian" in companions
    assert "claude plugin install claude-obsidian@agricidaniel-claude-obsidian" in companions
```

and change the `PROVISION_COMPANIONS` assertion to the two-element list.

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_capture_source_skill.py tests/test_skill_files.py -q`
Expected: FAIL — the `compile` needle is absent; `synthesis-conventions` still describes `synthesis/`; the companions text lacks the plugin commands.

- [ ] **Step 3: Write the sections**

`skills/capture-source/SKILL.md`: the frontmatter description becomes `Use when a person asks to capture, refresh, add, or compile a source in a research-vault vault, or to propagate a citation-key change`; the routing row `Install Zotero add-ons` becomes `Install Zotero add-ons or the compile tool`; insert before `## Four-state honesty`:

````markdown
## 5. Compile: `compile`

Compile is the adopted tool's job (claude-obsidian; see `setup-vault`). The wrapper registers the captured sources in the tool's ledger and never writes under `wiki/`:

```sh
python3 -m research_vault compile KEY [KEY ...] --vault PATH        # prints the tool's plan and approval hash
python3 -m research_vault compile --vault PATH --bundle BUNDLE --approved-plan-sha256 SHA
```

Show the person the plan before applying; the approval hash is the tool's own human gate, and there is no second one. Then run the tool's wiki-ingest skill on the registered `fulltext/<attachment key>.md` files; the pages it writes cite the literature note as `[[<citation key>]]`. Then run `capture KEY` again (or `capture --all`): the note now embeds the compiled page, `![[<page path>]]`, from the ledger's `pages[]`. Until that second capture the embed is absent — expected, not an error. A note whose text changed after compile is reported `recompile-needed` by `verify`.
````

`skills/setup-vault/SKILL.md`: insert before `## Migrate an older vault`:

````markdown
The compile tool is a Claude Code plugin and installs from its own marketplace, after per-item consent, with two commands the person runs (restart-to-activate):

```sh
claude plugin marketplace add AgriciDaniel/claude-obsidian
claude plugin install claude-obsidian@agricidaniel-claude-obsidian
```

Doctor's `compile-tool` probe reports the installed commit against the pin `32ac5a0`; a different commit is a warning, not a failure. `$ROOT` is the plugin's `installPath` recorded in `~/.claude/plugins/installed_plugins.json` (the record doctor's `compile-tool` probe reads); `.research-vault/machine.json` may name a `claude_obsidian_root` that overrides it. Then adopt the vault into the tool once, with its own inspect-then-apply gate: `python3 "$ROOT/scripts/claude-obsidian.py" adopt PATH` (dry run), then the same command with `--apply --approved-plan-sha256 <hash>` from the dry run. The tool leaves the vault's existing `.gitignore` untouched (silently, not by refusing — measured 2026-09-14); append its rules by hand: `.vault-meta/`, `.mcp.json`, `.trash/`.
````

`skills/synthesis-conventions/SKILL.md`:

```markdown
---
name: synthesis-conventions
description: Use when creating or editing pages of the compiled layer under wiki/ in a research-vault vault, arranging sources into concept pages, or asking about the rules of that layer
---

# Conventions for the compiled layer

The compiled layer lives under `wiki/` — per-source pages under `wiki/sources/`, cross-source pages under `wiki/concepts/` — and is written by the adopted compile tool (claude-obsidian) through its transaction engine. It asserts arrangement, not evidence: nothing under `wiki/` passes an evidence gate, which is why the folder is the boundary. The evidence underneath it never moves: every page cites its source as `[[<citation key>]]`, which resolves to `literatures/<citation key>.md`, and a page may cite only a source capture wrote — the `captured-set` check fails a commit otherwise.

## Never write the layer by hand

`wiki/` is a machine surface: pages are created and replaced only through the tool's wiki-ingest skill and its `transaction inspect` / `transaction apply` gate. Never `Write` or `Edit` under `wiki/`; the pre-tool-use guard refuses it. Register sources first with `python3 -m research_vault compile KEY --vault PATH` (see `capture-source`).

## Orientation first

Before proposing any page, read `wiki/index.md`, `wiki/hot.md` and the recent `log/` entries. Arrive knowing which concept pages exist and what happened recently — never propose a page that duplicates one already indexed.

## The 2+-source threshold, and the tool's compilation-value gate

A concept page earns its existence at two or more captured sources on the same topic — the vault's one threshold. The tool adds its own gate, which is compatible and stricter: create or expand a canonical page only when the source adds durable synthesis, navigation, a decision, or a reusable connection beyond the source page itself. Two sources set side by side with nothing said about how they relate are a compilation, and a compilation earns no page: say plainly that there was nothing to arrange yet.

## Minimum-link discipline

Every concept page carries at least two outgoing wikilinks, at least one of them a `[[<citation key>]]`. The tool's lint reports orphans (no incoming link) and dead links; both block its checkpoint.

## Frontmatter

The tool's lint requires six keys on every page under `wiki/`: `title`, `type`, `status`, `created`, `updated`, `tags`. `type` is one of the tool's own `PAGE_TYPES` at 32ac5a0 — `source`, `entity`, `concept`, `question`, `comparison`, `session`, `overview`, `meta`, `fold` (`claude_obsidian/page_schema.py`, read 2026-09-16); the vault derives none for `wiki/`. No `{{TITLE}}`-style template exists for this layer any more.

## Index registration

Every canonical page create or removal includes an update to `wiki/index.md` in the same transaction — the tool's rule, and the tool performs it. Never edit `wiki/index.md` by hand; it is the one nested index that legitimately carries frontmatter (ADR 0001, second exemption).

## What is frozen

Claim lines, stance links (`supports`/`disputes`) and claim links (`[[key#^claim-id]]`) are no longer the arrangement's currency; the checks that read them are frozen pending the workflow-component audit. Do not write new ones into `wiki/`.
```

`research_vault/templates/vault/AGENTS.md`: the `capture-source` row becomes "add, capture, refresh, propagate a re-key, or compile a source". `research_vault/scaffold.py:23`: `PROVISION_COMPANIONS` gains `"claude-obsidian@agricidaniel-claude-obsidian"`.

- [ ] **Step 4: Run the suite and form owners; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && mdformat --number --wrap keep skills/capture-source/SKILL.md skills/setup-vault/SKILL.md skills/synthesis-conventions/SKILL.md research_vault/templates/vault/AGENTS.md`
Expected: PASS.

```bash
git commit -m "compile sections of the skills; rewrite synthesis-conventions (ingest spec §6)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- skills tests research_vault
```

### Task 4: Docs, registries and CI (spec §5 "the standing facts file", §7, decision 21's dated deferral)

**Files:**

- Modify: `docs/testing.md`, `docs/terminology.md` §4.4 (final registries), `.github/workflows/quality.yml:87-104` (the CRAP comment block and step, lines as of `384d562`), `research_vault/templates/git/pre-commit` (comment, if Part A Task 12 did not add it)

**Interfaces:**

- Produces: the final §4.4 rows, verbatim — with one ordering rule: when Task 4 runs before Task 2 (allowed; the phase's own fallback ships Tasks 4–6 without 2–3), the check-ids row omits `compile`, because the test below asserts the row equals the code at that HEAD, and Task 2 adds `compile` to `inbox.CHECK_IDS` and to the row in one commit (its Files block claims §4.4):

  - check ids: `citation-key`, `quote`, `update-notice`, `evidence-layer`, `identifier-discovery`, `disputed-claim`, `publish`, `factcheck`, `okf-frontmatter`, `okf-structure`, `tree`, `lifecycle`, `capture`, `propagation`, `captured-set`, `compile`
  - doctor probe ids: `tree`, `machine-config`, `zotero`, `write-guard`, `fulltext-sync`, `bbt`, `bbt-git`, `plugins`, `path-shim`, `translator-formats`, `compile-tool`, `remote`, `backup`
  - reason codes: `budget-cap`, `contradiction`, `database-changed`, `deleted`, `disputed-claim`, `drift`, `fuzzy-quote`, `low-confidence`, `manual`, `matched`, `merged`, `mismatch`, `no-fulltext`, `no-identifier`, `not-admitted`, `not-captured`, `outage`, `re-keyed`, `recompile-needed`, `retracted`, `schema-violation`, `stale-key`, `trashed`, `unkeyed`, `warn-notice`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_skill_contracts.py`:

```python
def test_terminology_registries_match_the_code():
    import re

    from research_vault import __main__ as cli
    from research_vault import inbox

    text = (ROOT / "docs" / "terminology.md").read_text()
    rows = {m.group(1): set(re.findall(r"`([a-z-]+)`", m.group(2)))
            for m in re.finditer(r"^\| (check ids|doctor probe ids|reason codes) +\| (.+) \|$", text, re.MULTILINE)}
    assert rows["check ids"] == set(inbox.CHECK_IDS)
    assert rows["reason codes"] == set(inbox.REASON_CODES)
    assert rows["doctor probe ids"] == cli.DOCTOR_HARD_UNMATCHED | cli.DOCTOR_HARD_UNREACHABLE | cli.DOCTOR_WARN_ONLY | {"tree", "machine-config"}
```

(`ROOT` is that file's repository-root constant.) The reason-code row must be **one physical table row** (terminology §4.4).

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_skill_contracts.py -q -k registries`
Expected: FAIL on whichever row drifted.

- [ ] **Step 3: Write the docs and the CI change**

`docs/terminology.md` §4.4: the three rows exactly as in Interfaces.

`docs/testing.md` — Plan W (2026-09-14, `08cd9e6`) rewrote "## The suite" around four hermeticity mechanisms (the Zotero client patch, the socket and resolver block, `dead_base`, the per-test HOME). Keep that text; make three edits inside it, and write no environment fact into the file (Zotero and Better BibTeX versions, profile paths and add-on lists come from `probe` and the spec's §7 substrate paragraph, per `AGENTS.md`):

1. Replace the **Live invocation** paragraph and the code block under it with:

````markdown
**Live invocation** (Zotero must be running on the Windows host; the local API answers on `localhost:23119`, the unsynced test instance on `localhost:23129` — `python -m research_vault probe --base <base>` names each). Read-only legs run against whichever `--base` they are given; **write-capable legs run only against the test instance** and refuse `zotero.DEFAULT_BASE`:

```bash
RV_LIVE=1 RV_LIVE_NET=1 RV_MAILTO=<real address> python -m pytest tests -q            # read-only local-Zotero and external-registry legs
RV_LIVE=1 RV_LIVE_WRITE_BASE=http://localhost:23129 python -m pytest tests -q -k live  # plus the add/trash/delete leg (one consent dialog the first time)
```
````

2. In the paragraph that begins "`RV_LIVE` unlocks the local-Zotero legs", replace the sentence "Nothing else is gated: with both flags set the suite has no remaining skip." with: "`RV_LIVE_WRITE_BASE` unlocks the write-capable leg, which carries both the `live` and the `live_write` markers — the hermeticity fixtures honour `live`; `live_write` only adds the base gate. With all three set the suite has no remaining skip."

3. After that paragraph, add:

```markdown
The first write leg on a machine pops Zotero's consent dialog on the test instance; answer **Always Allow** there and the key persists in the scratch vault's `.research-vault/zotero-keys.json` for the run. If a later run re-opens the dialog, export that key as `RV_LIVE_WRITE_KEY` and the leg runs unattended. `--as-of YYYY-MM-DD` on `verify` and `inbox` pins the instant a check compares against, which is how a recorded fixture replays without drifting (spec §7).
```

Under "## Poking Zotero" item 1 add: "`python -m research_vault probe --base http://localhost:23129` names the test instance." (Part A left no `RV_LIVE_AUTOEXPORT_VAULT` or `test_dispositions` sentence; checked 2026-09-14.)

`.github/workflows/quality.yml`: delete `continue-on-error: true` from the CRAP step and replace the comment block above it with:

```yaml
      # The ceiling is 30 and stays 30 (986086e). The two functions that sat
      # above it — `_bump_generated` (archive.py) and `check_metadata`
      # (checks.py) — were deleted by the ingest redesign (2026-09), so the
      # dated deferral decision 21 carried is closed and this step fails the
      # lane again on any new breach.
```

Confirm locally before committing: `.venv/bin/python -m pytest tests -q --cov=research_vault --cov-branch --cov-report=lcov:lcov.info && .venv/bin/crap4py research_vault --lcov lcov.info --max-crap 30` — expected: no function above 30. If one is, split it in the same commit rather than restoring the deferral.

- [ ] **Step 4: Run everything; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && mdformat --number --wrap keep docs/testing.md docs/terminology.md && yamlfix .github/workflows`
Expected: PASS.

```bash
git commit -m "docs and registries for ingest; close the CRAP deferral

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- docs tests .github/workflows/quality.yml
```

### Task 5: Live legs on the test instance, and the missing trashed snapshot (spec §7)

**Files:**

- Create: `tests/test_capture_live.py`, `tests/fixtures/lifecycle/items-trashed.json`
- Modify: `research_vault/zotero.py` (`trash_item(key, version)`, `delete_item(key, version)` — PATCH `{"deleted": true}` and DELETE with `If-Unmodified-Since-Version`; both need the API key; and `authorize` waits `AUTHORIZE_TIMEOUT` for the consent click — see Step 3), `tests/fixtures/lifecycle/README.md` (the trashed fixture becomes replayable), `tests/test_lifecycle.py` (a replay test for the observed trashed transition), `tests/conftest.py` (`pytest_collection_modifyitems` also skips `live_write` without `RV_LIVE_WRITE_BASE`; `pyproject.toml` registers the marker `live_write: writes to the Zotero test instance (set RV_LIVE_WRITE_BASE)`), `docs/research/2026-09-05-zotero-api-reading.md` (append one dated record — the request, the answering headers and the shape of the map — for `GET /api/users/0/items/trash?format=versions` as this leg observes it: `trash_versions` is the one route the client reads on the spec's own measurement with no corpus record behind it, and Task 7 showed what an uncorroborated assertion costs; the three records 449–451 that Part A's Task 20 attended leg measured on 2026-09-13 (the native `citationKey` PATCH with `If-Unmodified-Since-Version` → 204, the version headers, Better BibTeX's agreement), copied from its report into the reading doc, and a second re-measured record for `GET /api/users/0/items/top?format=csljson&limit=1`, which Part A's Task 16 live leg measured on 2026-09-13 answering 200 with a CSL JSON body on Zotero 10.0.1 and 10.0.2 where record 15 and the spec's §9 row measured 500 on 2026-09-04 — re-measure it in this leg and record what answers, since the route has now been observed both ways)

**Interfaces:**

- Produces: `ZoteroClient.trash_item(key: str, version: int) -> int` and `delete_item(key: str, version: int) -> int` (both return the HTTP status, 204 expected; 412 raises `ZoteroError(UNMATCHED)` "version moved").

- [ ] **Step 1: Write the live tests**

`tests/test_capture_live.py`:

```python
"""Live legs against Zotero 10 (spec §7). Read legs need RV_LIVE=1; the write
leg needs RV_LIVE_WRITE_BASE too and refuses the production instance."""

# An automated propagate leg (Part A Task 20 Step 1 ran it attended on
# 2026-09-13) re-keys an item over the local API: measured, PATCH accepts the
# native ``citationKey`` field — ``PATCH /api/users/0/items/<key>`` with
# ``If-Unmodified-Since-Version`` answered 204 and Better BibTeX agreed within
# seconds; the legacy Extra line was never needed (research records 449-451,
# appended by this task from the Task 20 report). Print the leg from those
# records: authorize once, PATCH the native field, run the linter, propagate,
# restore the key with a second PATCH.

import json
import os
import time

import pytest

from research_vault import Result, capture, lifecycle, notes, zotero

READ_BASE = os.environ.get("RV_LIVE_WRITE_BASE") or zotero.DEFAULT_BASE


@pytest.mark.live
def test_capture_round_trip_on_a_live_item(tmp_vault):
    client = zotero.ZoteroClient(base=READ_BASE)
    items, _ = client.top_items()
    keyed = next(i for i in items if i["data"].get("citationKey") and i.get("meta", {}).get("numChildren"))
    key = keyed["data"]["citationKey"]
    outcomes = capture.capture(tmp_vault, client, [key])
    assert outcomes[0].result is Result.MATCHED
    text = (tmp_vault / "literatures" / f"{key}.md").read_text()
    provenance = notes.read_provenance(text)
    assert provenance.server_id == client.server_info()["server_id"]
    assert provenance.item_version == keyed["version"]
    again = capture.capture(tmp_vault, client, [key])
    assert again[0].reason == "matched — NOOP"
    (row,) = [o for o in lifecycle.lint_lifecycle(tmp_vault, client) if o.target == key]
    assert row.result is Result.MATCHED


@pytest.mark.live
@pytest.mark.live_write
def test_add_edit_trash_delete_transitions_and_record_the_trashed_snapshot(tmp_vault):
    base = os.environ["RV_LIVE_WRITE_BASE"]
    assert base.rstrip("/") != zotero.DEFAULT_BASE, "write legs never touch production"
    client = zotero.ZoteroClient(base=base, api_key=os.environ.get("RV_LIVE_WRITE_KEY") or None)
    stamp = time.strftime("%Y%m%d%H%M%S")
    outcomes = capture.add(tmp_vault, client, [{"itemType": "journalArticle", "title": f"research-vault live leg {stamp}",
                                                 "creators": [{"creatorType": "author", "lastName": "Sitting", "firstName": "Live"}], "date": "2026"}])
    assert outcomes[0].reason.startswith("matched — created "), outcomes
    item_key = outcomes[0].reason.split("created ")[1].split(",")[0]
    note = next((tmp_vault / "literatures").glob("*.md"))
    provenance = notes.read_provenance(note.read_text())
    assert provenance.item_key == item_key

    # the snapshot the sitting missed: the scratch item live in the items map
    versions, _ = client.versions()
    assert item_key in versions
    live_snapshot = {k: v for k, v in versions.items() if k == item_key}

    envelope = client.item(item_key)
    status = client.trash_item(item_key, envelope["version"])
    assert status == 204
    trashed_versions, _ = client.versions()
    trash = client.trash_versions()
    assert item_key not in trashed_versions
    assert item_key in trash
    (row,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert row.reason.startswith("trashed — ")
    fixture = {"live": live_snapshot, "trashed_items": {k: v for k, v in trashed_versions.items() if k == item_key},
               "trashed_trash": {k: v for k, v in trash.items() if k == item_key}}
    (tmp_vault / "items-trashed.json").write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n")

    status = client.delete_item(item_key, trash[item_key])
    assert status == 204
    (row,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert row.reason.startswith("deleted — ")
```

- [ ] **Step 2: Run the read leg; then the write leg once, attended**

```bash
RV_LIVE=1 .venv/bin/python -m pytest tests/test_capture_live.py -q -k round_trip
RV_LIVE=1 RV_LIVE_WRITE_BASE=http://localhost:23129 .venv/bin/python -m pytest tests/test_capture_live.py -q -k transitions -s --basetemp=/tmp/rvlive -o tmp_path_retention_policy=all   # pyproject's retention policy "failed" deletes a PASSING run's tmp_vault, fixture included (measured 2026-09-16, run 3)
```

Expected: both PASS (answer **Always Allow** on the test instance's dialog the first time). **Measured 2026-09-16 (runs 3 and 4):** a second `authorize` for the same `appName` after **Always Allow** re-opens the dialog against a fresh `tmp_vault` — the grant lives in the key store, not in Zotero. For an unattended re-run, read the granted key from the attended run's `<basetemp>/.../.research-vault/zotero-keys.json` and export it as `RV_LIVE_WRITE_KEY`; the leg then runs unattended (`add` uses a preset `client.api_key` before consulting the store). Record which of the two happened in `tests/fixtures/lifecycle/README.md`. Copy the written `items-trashed.json` from the test's `tmp_vault` (pytest prints the path with `--basetemp`; use `--basetemp=/tmp/rvlive`) to `tests/fixtures/lifecycle/items-trashed.json`.

- [ ] **Step 3: Implement the two write helpers and the replay test**

**The authorize wait (ruled 2026-09-16, from the attended half's first run).** `authorize` POSTs under the client's default `timeout=5.0`, and Zotero answers only when the person clicks Allow / Always Allow / Deny, so an unanswered dialog reads `UNREACHABLE outage — timed out` after 5 s — in this leg and in the CLI's `add`. A human act gets a human-scale wait, on the product side (a test-only `timeout=180` would leave `add` broken for every user). `EXPORT_TIMEOUT` is the precedent for a per-route timeout. In `research_vault/zotero.py`:

```python
# The consent dialog is answered by a person; a network timeout is the wrong
# clock for it. Measured 2026-09-16: an unanswered dialog under the default 5 s
# reads as an outage in `add` and in the live leg.
AUTHORIZE_TIMEOUT = 180.0
```

`_local(...)` gains `*, timeout: float | None = None`, passed straight to `self._http(..., timeout=timeout)`; `authorize` calls `self._local("/api/local/authorize", ..., timeout=AUTHORIZE_TIMEOUT)`. `capture.add` is unchanged (it calls `authorize()`; the wait is the route's). Test, in `tests/test_zotero.py` (extend `tests/fakes.py::FakeZotero._http` to record the `timeout` it received if it does not already):

```python
def test_authorize_waits_for_the_person_not_the_network(fake):
    """The consent dialog is answered by a person, not the network: `authorize`
    must ride `AUTHORIZE_TIMEOUT`, not the client's 5 s default (measured
    2026-09-16)."""
    fake.client.server_id = "6LpvURP2E933"
    fake.post("/api/local/authorize", body={"key": "k"})
    fake.client.authorize()
    index = next(i for i, c in enumerate(fake.calls) if c[1] == "/api/local/authorize")
    assert fake.timeouts[index] == zotero.AUTHORIZE_TIMEOUT
```

(`FakeZotero` records a `timeouts` list parallel to `calls`; the assertion is the pin.) The gate re-measures `zotero.py` with the rest of this task's changes.

```python
    def trash_item(self, key: str, version: int) -> int:
        return self._mutate(key, version, method="PATCH", data=json.dumps({"deleted": True}).encode())

    def delete_item(self, key: str, version: int) -> int:
        return self._mutate(key, version, method="DELETE")

    def _mutate(self, key, version, *, method, data=None) -> int:
        if not self.api_key:
            raise ZoteroError(f"{method} needs an API key from authorize", Result.UNMATCHED)
        headers = self._headers({"If-Unmodified-Since-Version": str(version), "Content-Type": "application/json"})
        response = self._http(f"{self.base}{_USER}/items/{key}", data=data, headers=headers, method=method)
        if response.status == 412:
            raise ZoteroError(f"{method} {key}: version moved (412)", Result.UNMATCHED)
        if response.status not in (200, 204):
            raise ZoteroError(f"{method} {key}: HTTP {response.status}")
        return response.status
```

Add to `tests/test_lifecycle.py`:

```python
def test_trashed_transition_replays_from_the_live_snapshot():
    fixture = json.loads((FIXTURES / "items-trashed.json").read_text())
    (item_key,) = fixture["live"]
    prov = _prov(item_key=item_key, version=fixture["live"][item_key], citation_key="live2026")
    assert lifecycle.classify(prov, _live(fixture["live"], {}, {}))[0] == "current"
    assert lifecycle.classify(prov, _live(fixture["trashed_items"], fixture["trashed_trash"], {})) == ("trashed", item_key)
```

Update the fixture README's `trash-trashed.json` bullet: "superseded by `items-trashed.json`, recorded live on 2026-MM-DD by `tests/test_capture_live.py`; the transition now replays." Register the `live_write` marker and its skip — `pyproject.toml` `[tool.pytest.ini_options] markers` gains `"live_write: writes to the Zotero test instance (set RV_LIVE_WRITE_BASE; never production)",` beside the two existing rows (`--strict-markers` refuses an unregistered one), and `tests/conftest.py::pytest_collection_modifyitems` gains, after the `live_net` skip:

```python
    skip_write = pytest.mark.skip(
        reason="write-capable live leg not enabled (RV_LIVE_WRITE_BASE=http://localhost:23129)"
    )
    for item in items:
        if "live_write" in item.keywords and not os.environ.get("RV_LIVE_WRITE_BASE"):
            item.add_marker(skip_write)
```

(The leg keeps its `live` marker too, so the hermeticity fixtures — `_no_zotero_socket`, `_no_socket`, `_per_test_home` — let it through on that marker alone; nothing in `conftest.py` learns `live_write` beyond this skip.)

- [ ] **Step 4: Run everything; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS (the live legs skip offline).

```bash
git add tests/fixtures/lifecycle/items-trashed.json
git commit -m "live legs on the test instance; the trashed transition now replays (ingest spec §7)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests pyproject.toml
```

______________________________________________________________________

## Phase 3 — closing

### Task 6: Final verification, the upstream issue, the merge, the completion message

**Files:**

- Create: `docs/superpowers/specs/2026-09-06-import-redesign-part-b-results.md`

- Modify: `docs/superpowers/plans/2026-09-07-ingest-redesign-b-deferred.md` (every row dispositioned), plus whatever Step 1b's fix wave touches. The outward deliverables are a message and, on go-ahead, one GitHub issue on `zotero/zotero`.

- [ ] **Step 1: Full verification**

```bash
.venv/bin/python -m pytest tests -q -n auto
ruff format --check research_vault tests scripts hooks && ruff check research_vault tests scripts hooks && mypy research_vault
.venv/bin/python -m pytest tests -q --cov=research_vault --cov-branch --cov-report=lcov:lcov.info && .venv/bin/crap4py research_vault --lcov lcov.info --max-crap 30 && .venv/bin/drywall research_vault
RV_LIVE=1 .venv/bin/python -m pytest tests -q -k live
python3 scripts/mutation_gate.py --base main --max-children 6 --child-address-space 4GiB   # the mutmut gate (Plan W): reads no LCOV; children and cap as measured locally, CI passes --max-mutants 9000 at 2 x 3GiB
git status --porcelain   # must be empty
```

Expected: every command exits 0; report the pytest counts and the mutation-gate summary line verbatim. Add the attended leg's result from Task 5 to the report; it is not re-run here.

- [ ] **Step 1b: Whole-branch review, one fix wave, the register's dispositions**

Dispatch the review on the most capable model over `git diff $(git merge-base HEAD main)..HEAD` — the merge base, never the branch tip (Part A process note 3) — with the spec, this plan and the deferred file in hand; it returns Critical, Important and Minor findings with file and line. One fix wave lands them as pathspec commits (tests first for a behaviour fix); a scoped re-review over the wave's commits confirms no new Critical or Important. Then every row of `docs/superpowers/plans/2026-09-07-ingest-redesign-b-deferred.md` ends **fixed** naming the commit, **declined** with the reason in the row, or **open → issue**: the open rows become one issue (`gh issue create --label ready-for-agent`, the rows as its body; Part A's #129 is the shape) and each such row names the number. Findings the review raises outside the table are dispositioned the same way in the results file (Step 4). Read the task reports' Concerns (`.superpowers/sdd/…/task-N-report.md`) once more here: each names a destination, and the SDD workspace is not deleted until every destination holds it (`AGENTS.md`, Task reports).

Expected: no open row without an issue number; the re-review's verdict quoted in the results file.

- [ ] **Step 2: Draft the upstream issue and wait for go-ahead**

Spec §6 keeps verify's update-notice check because Zotero exposes its Retraction Watch verdict nowhere a client can read, "and asking them to is worth an issue." Draft, do not post:

```
Title: Local API: expose the retraction flag on item JSON

Zotero <version from probe at posting> flags retracted items natively (retractions.js, the
retractedItems table) and warns at cite time, but the local API exposes
that verdict nowhere: no field in item JSON or meta, and /retractions and
/retracted both return 404 (measured 2026-09-05). A client that keeps its
own retraction check therefore duplicates work Zotero has already done.
Request: a boolean (or the notice's date and type) on item JSON, or an
endpoint listing retracted item keys, on the local API.
```

Fill the version from `python -m research_vault probe` when posting (10.0.2 on 2026-09-14). Post only when the user says so in that turn: `gh issue create --repo zotero/zotero --title "..." --body "..."`. Record the issue number in the completion message. The repository-side record of this filing is #113 (`ready-for-human`): on posting, comment the upstream URL there and close it; if not posted, leave #113 open and say so.

- [ ] **Step 3: Merge to `main`**

Per `AGENTS.md`: fetch first, merge back to `main` locally and push `main` to origin in the same motion. If this part ran on `main` directly, push.

- [ ] **Step 4: Results file, then the completion message**

Write `docs/superpowers/specs/2026-09-06-import-redesign-part-b-results.md` beside the spec, in the shape of `…-part-a-results.md` (date, method, spec, a binds-nothing line; what landed with commit ranges; verification measured in a table; the review's verdict and rounds; what moved in the spec; what remains) — the durable record, since the SDD workspace is deleted at Finish. Commit it with the merge or immediately after.

Report: the tasks landed (with commit shas), the tracer results (Task 1), the live-leg results (Task 5), the review's verdict and the register's final counts (fixed / declined / the follow-up issue number), the upstream issue number or that it was not posted, and anything skipped with its reason. Part A Task 20 delivered decision 23's invariant-5 report; restate it in one line only if the write-side gate changed since.

______________________________________________________________________

## Self-review

### Spec coverage

This part's sections only; Part A's table carries the rest and names these tasks as `B n`.

| Spec section          | Requirement                                                                                                                      | Task |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---- |
| §1 invariant 6        | falsifiability: full verification, write-capable live legs, mutation gate                                                        | 5, 6 |
| §3.1                  | alias probe (T5)                                                                                                                 | 1    |
| §4.1–4.3              | adoption at `32ac5a0`; tracers T1–T4 before any compile task; `capture` unused; modes; results recorded in the plan and the spec | 1, 2 |
| §4.4                  | the wrapper's ledger record carries `content_sha256`, the value `captured-set` compares for `recompile-needed`                   | 2    |
| §4.5                  | wrapper owns selection, locators, ledger records, invocation; no prompt                                                          | 2    |
| §5                    | setup skill's compile-tool install and adoption steps; `compile-tool` probe consumed                                             | 3    |
| §6 skills             | synthesis-conventions rewritten; compile sections of capture-source and setup-vault                                              | 3    |
| §6 update-notice kept | the upstream issue, drafted and gated                                                                                            | 6    |
| §6 frozen checks      | `evidence-layer`'s write legs take the writer attestation; capture's writes commit through the hook (amendment 2026-09-16)       | 2b   |
| §7                    | live legs on the test instance; the missing trashed snapshot; `docs/testing.md`                                                  | 4, 5 |
| Assembly decision 21  | the dated CRAP deferral closed                                                                                                   | 4    |
| Decision 22           | tracer results land here and in the spec                                                                                         | 1    |

### Placeholder scan

The `2026-MM-DD` tokens in Task 1's results block and Task 5's fixture README sentence are dates the executor fills at run time; nothing else is deferred.

### Type consistency

- `compile.ledger_record` consumes `notes.Provenance` (Part A Task 11) and writes the `fulltext.write` sha256 (Part A Task 10) as `content_sha256`, the value `captured._structural` (Part A Task 15) compares.
- `ZoteroClient.versions()` returns `(map, version)`; `trash_versions()` returns the map alone — used that way in Task 5.
- The `compile` check id Task 2 registers is in the §4.4 row Task 4 fixes.
