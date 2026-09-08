# Ingest Redesign Implementation Plan — Part B: compile adoption, live legs, closing

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Drive the adopted compile tool (`AgriciDaniel/claude-obsidian` at `ad67087`) through a glue wrapper once its tracers pass; add the compile sections to the skills; close the docs, registries and the CI deferral; run the write-capable live legs on the test instance; and close the ingest redesign with its one upstream issue.

**Architecture:** Compile is adopted unmodified: `research_vault/compile.py` selects captured sources, registers ledger records through the tool's own `transaction inspect`/`apply`, and never writes under `wiki/`. Everything else here is documentation, live-leg tests and one report. Capture, the lifecycle linter, propagation, the captured-set lint, doctor and `add` are Part A's and are consumed unchanged.

**Tech Stack:** Python 3.11+ stdlib only (`urllib`, `json`, `hashlib`, `html.parser`, `subprocess`, `pathlib`). pytest with `monkeypatch` fakes; two live Zotero 10.0.1 instances (production `localhost:23119`, test `localhost:23129`). No new dependency.

**Spec:** `docs/superpowers/specs/2026-09-04-import-redesign-design.md` (the active spec; §9 is its fact register). Also binding: `docs/superpowers/specs/2026-09-05-assembly-design.md` decisions 12, 17, 22, 28, 29 and §9; ADR 0001–0003.

**Prerequisite:** Part A (`docs/superpowers/plans/2026-09-07-ingest-redesign-a-capture.md`) merged to `main`. This part consumes, by name: `captured.captured_set`, `notes.read_provenance` and `notes.Provenance`, `fulltext.path_for`, `capture.capture` and `capture.add`, `lifecycle.lint_lifecycle` and `lifecycle.classify`, `zotero.ZoteroClient` on the local API with the `Zotero-Server-ID` header, `scaffold._installed_plugins` and the thirteen-probe doctor, and `skills/capture-source` and `skills/setup-vault` as Part A Task 19 left them. Part A's "Decisions this plan settles" (01–25) bind here unchanged; this part leans on 03 (verbs), 06 (probe ids), 17 (tool location and pin), 18 (`wiki/` in the guard), 22 (tracer results), 24 (the tool's inbox) and 25 (`linkMode`).

**Human attendance:** Task 1 (the tracers, one sitting with Obsidian open), Task 5 (one consent dialog on the test instance) and Task 6 (the go-ahead for the upstream issue) need the author present; Tasks 2, 3 and 4 do not.

## Global Constraints

- **Commit with an explicit pathspec** (`git commit -m "..." -- <files>`; the message precedes `--`). Parallel sessions share this checkout: never revert or restore another session's uncommitted files; report the precondition as unmeetable instead. Every commit message ends with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- **Offline suite before every commit:** `.venv/bin/python -m pytest tests -q -n auto` from the repo root. Baseline on 2026-09-07: 1838 passed, 7 skipped, 28 s. Pass `-n` on the command line, never in addopts.
- **Form owners, run directly on touched files, never `pre-commit run`** (it stashes onto a stack every worktree shares): `ruff format research_vault tests scripts hooks`, `ruff check research_vault tests scripts hooks`, `mypy research_vault`, `mdformat --number --wrap keep <touched .md files>`, `python -m json.tool --indent 2 --no-ensure-ascii <file> <file>` for JSON manifests.
- **Ruff rules that bite new code:** `T20` (no `print` outside `research_vault/__main__.py` and `scripts/`), `C90` (`max-complexity = 28`), `PTH` (use `pathlib`), `S` (no `shell=True`), `DTZ` (timezone-aware `datetime`). mypy rung 1: annotated functions are checked; no `cast()` laundering.
- **Stdlib only.** The package's one runtime dependency (`defusedxml`) is untouched. `pytest-recording`/`vcrpy` are not adopted (spec §7: no recorder).
- **Four-state everywhere.** Every mechanical step returns `Outcome`s in `MATCHED`/`UNMATCHED`/`UNREACHABLE`/`SKIPPED`. An outage never reads as a pass; a skipped check never reads as clean (ADR 0002).
- **Reason codes and check ids are registries.** `Outcome.__post_init__` validates `reason` against `inbox.REASON_CODES` at construction, so a task adds its codes to `REASON_CODES` **before** any `Outcome` uses them. Every change to `REASON_CODES` must also update the `## Reason-code vocabulary` table in `skills/evidence-conventions/SKILL.md` (`tests/test_skill_contracts.py:440-494` requires every code exactly once) and the `reason codes` row of `docs/terminology.md` §4.4. Every change to `inbox.CHECK_IDS` or a doctor probe id updates the matching §4.4 row in the same commit.
- **Deprecate, never delete, for vault records** (ADR 0003): no transition deletes a literature note. Repository artifacts (plans, docs, code) are outside that rule; deleting them is hygiene.
- **No `Disposition:` line** on new Markdown: the marker system was deleted on 2026-09-07 (`7ec2c95`, `8e2721b`).
- **Machine-local facts stay out of the repo.** Nothing commits a local-API key, a Windows path, a server id, or a version count as a constant. Live values come from `python -m research_vault probe`.
- **Deleting a module** deletes its `research_vault/<module>.py.manifest.json` sidecar (mutate4py sidecars; nothing enforces them) and prunes its rows from `mutation-baseline.txt` (`grep -v '^research_vault/<module>.py::'`). New modules need no sidecar; the gate writes one on its first run.
- **Live legs** stay under the existing `live` marker (`RV_LIVE=1`). Write-capable legs additionally require `RV_LIVE_WRITE_BASE` (the test instance, `http://localhost:23129`) and refuse to run against `zotero.DEFAULT_BASE`; `RV_LIVE_WRITE_KEY` optionally supplies a key granted by an earlier **Always Allow** so the leg runs without the dialog. Nothing in the suite ever writes to the production instance.
- **Outward-facing actions need explicit go-ahead in that turn**: Task 6's upstream Zotero issue is not run on plan approval alone.
- **Scope held by the spec:** annotations (spec §3.2, decision 28) are specified, tested against a fixture, and **not wired into capture**; the pre-commit lifecycle leg is held (invariant 5); substrate absence is deferred (§0); web pages and repositories are deferred (§0).

______________________________________________________________________

## Interface index

Signatures this part adds, then the Part A signatures its tasks call (copied from Part A's index; Part A's file is the authority).

```python
# research_vault/compile.py                                   (Task 2) 
LEDGER_PATH = "wiki/meta/ledgers/source-ledger.json"; PIN = "ad67087"
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

- Modify: `docs/superpowers/plans/2026-09-07-ingest-redesign-b-compile.md` (this section's results), `docs/superpowers/specs/2026-09-04-import-redesign-design.md` §4.3 (one sentence: "Tracers run 2026-MM-DD: \<pass|fail> — see the plan.")

- [ ] **Step 1: Install the tool at the pin and confirm doctor sees it**

```bash
claude plugin marketplace add AgriciDaniel/claude-obsidian
claude plugin install claude-obsidian@agricidaniel-claude-obsidian
python3 -c "import json,pathlib;p=json.load(open(pathlib.Path.home()/'.claude/plugins/installed_plugins.json'))['plugins']['claude-obsidian@agricidaniel-claude-obsidian'][0];print(p['gitCommitSha'],p['installPath'])"
```

Expected: a sha starting `ad67087`. If the marketplace has moved past the pin, pin locally: `git -C "$installPath" checkout ad67087` is **not** available (the cache is not a git checkout) — record the sha found, and treat `compile-tool` UNMATCHED as the tracer's finding; Task 2 still targets the documented `ad67087` surface (agent-read 2026-09-07) and the author decides whether to move the pin.

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

Expected: `mode get` reports `sources_folder: wiki/sources/`, `concepts_folder: wiki/concepts/`; `.vault-meta/mode.json` exists; `adopt` created `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, `wiki/overview.md`, `.raw/.manifest.json`, `wiki/meta/ledgers/*.json`, `.claude-obsidian.json`, `.obsidian/*`, and **did not overwrite** the vault's `.gitignore` (it refuses without `--force`; append its rules by hand: `.vault-meta/`, `.mcp.json`, `.trash/`). (If the exact flag names differ from the ones above, read `python3 "$CORE" adopt --help`; the approve-then-apply shape is `_require_approved_plan` in `claude_obsidian/cli.py:86-104`.)

- [ ] **Step 4: T3 — a compile run over three captured sources writes only under `wiki/`**

Capture three sources into the scratch vault (`capture A B C --base http://localhost:23129`), snapshot `literatures/` and `fulltext/` (`find "$scratch/literatures" "$scratch/fulltext" -type f -exec sha256sum {} + | sort > /tmp/before.txt`). In the session, invoke the tool's `wiki-ingest` skill on the three `fulltext/<key>.md` files (hand it the paths; Task 2's wrapper is not built yet). Approve its bundle by hash, apply. Then:

```bash
find "$scratch/literatures" "$scratch/fulltext" -type f -exec sha256sum {} + | sort | diff - /tmp/before.txt && echo "literatures and fulltext byte-identical"
git -C "$scratch" status --porcelain | grep -v '^?? wiki/\|^ M wiki/\|^?? \.raw/\|^?? \.claude-obsidian\.json\|^?? \.obsidian/' ; echo "(nothing above this line means only wiki/ changed)"
```

Expected: byte-identical evidence and text layers; every changed path under `wiki/` (plus the tool's own dotfiles). Record what `wiki/log.md` looks like after the run: if it carries a `## ` heading that is not `## YYYY-MM-DD`, `okf-structure` will fail on it — record that as a fourth conflict and decide with the author whether `wiki/log.md` joins the `wiki/index.md` exemption (a one-line addition to `structure._EXEMPT_INDEXES`' sibling set and to ADR 0001).

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

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- docs/superpowers/plans/2026-09-07-ingest-redesign-b-compile.md docs/superpowers/specs/2026-09-04-import-redesign-design.md
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
    assert record["content_sha256"] == "f" * 64 and record["title"] == "Co-writing"
    assert record["review_status"] == "unreviewed" and record["pages"] == []
    assert record["retrieved_at"] == "2026-09-07" and record["ingested_at"] == "2026-09-07"


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


def test_plan_writes_the_bundle_and_apply_reports_four_state(tmp_vault, tmp_path, monkeypatch):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch)
    bundle_path, inspected = compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    assert bundle_path.parent == tmp_vault / ".research-vault" / "compile"
    bundle = json.loads(bundle_path.read_text())
    assert bundle["operation_type"] == "ingest"
    (write,) = bundle["writes"]
    assert write["path"] == "wiki/meta/ledgers/source-ledger.json" and write["mode"] == "create"
    assert write["sha256"] == hashlib.sha256(write["content"].encode()).hexdigest()
    assert bundle["expected_hashes"] == {"wiki/meta/ledgers/source-ledger.json": None}
    assert json.loads(write["content"])["schema"] == "claude-obsidian.source-ledger.v1"
    assert inspected["approval_sha256"] == "abc123"

    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert outcome.result is Result.MATCHED and "source-ledger.json" in outcome.reason


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
    assert "src-keep" in merged and len(merged) == 2
    assert bundle["writes"][0]["mode"] == "replace"


def test_apply_maps_tool_exit_codes(tmp_vault, tmp_path, monkeypatch):
    _note(tmp_vault)
    _fake_tool(tmp_path, monkeypatch, apply_code=2)
    bundle_path, _ = compile_mod.plan(tmp_vault, ["jakesch.etal2023a"], today="2026-09-07")
    outcome = compile_mod.apply(tmp_vault, bundle_path, "abc123")
    assert outcome.result is Result.UNMATCHED and outcome.reason.startswith("mismatch")
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
import subprocess
from pathlib import Path, PurePosixPath

from . import captured, frontmatter, notes, paths
from .outcome import Outcome, Result

LEDGER_PATH = "wiki/meta/ledgers/source-ledger.json"
LEDGER_SCHEMA = "claude-obsidian.source-ledger.v1"
BUNDLE_SCHEMA = "claude-obsidian.transaction.v1"
PLUGIN_ID = "claude-obsidian@agricidaniel-claude-obsidian"
PIN = "ad67087"
CHECK = "compile"
BUNDLE_DIR = ".research-vault/compile"


class ToolMissingError(RuntimeError):
    """The compile tool is not installed and machine.json names no root."""


def stable_source_id(kind: str, locator: str, content_sha256: str | None) -> str:
    """Byte-for-byte the tool's ``ledgers.stable_source_id`` (read at ad67087)."""
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
        text = path.read_text(encoding="utf-8")
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
    today = today or datetime.datetime.now(datetime.UTC).date().isoformat()
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
        raise ToolMissingError("claude-obsidian is not installed; see setup-vault")
    today = today or datetime.datetime.now(datetime.UTC).date().isoformat()
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
    sources.update(records_for(vault, keys, today=today))
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

______________________________________________________________________

## Phase 2 — the skills' compile sections, docs, live legs

### Task 3: The compile sections of the skills, and `synthesis-conventions` (spec §6 "Rewritten skills: import-source, setup-vault and synthesis-conventions")

Part A Task 19 shipped `capture-source` and `setup-vault` without their compile sections, because `compile` did not exist until Task 2. This task adds those sections, rewrites `synthesis-conventions` for the adopted tool, and registers the plugin as a provision companion.

**Files:**

- Modify: `skills/capture-source/SKILL.md`, `skills/setup-vault/SKILL.md`, `skills/synthesis-conventions/SKILL.md`, `research_vault/scaffold.py:23` (`PROVISION_COMPANIONS = ["kepano/obsidian-skills", "claude-obsidian@agricidaniel-claude-obsidian"]`), `research_vault/templates/vault/AGENTS.md` (the skills table row), `tests/test_capture_source_skill.py`, `tests/test_skill_files.py`, `tests/test_templates.py`

**Interfaces:**

- Consumes: the `compile` verb (Task 2: `compile KEY... --vault PATH` prints the plan and its approval hash; `compile --vault PATH --bundle BUNDLE --approved-plan-sha256 SHA` applies), the `compile-tool` doctor probe (Part A Task 16), the `captured-set` check (Part A Task 15), `scaffold.PROVISION_COMPANIONS`.

- Produces: three skills whose frontmatter passes `tests/test_skill_contracts.py` (name equals directory, description begins `Use when `, entry skills carry `disable-model-invocation: true`, every backticked check id names one the code files).

- [ ] **Step 1: Write the failing tests**

In `tests/test_capture_source_skill.py::test_capture_source_keeps_the_kept_rules`, add to the needle tuple:

```python
        "python3 -m research_vault compile", "--approved-plan-sha256", "wiki-ingest", "recompile-needed",
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

Show the person the plan before applying; the approval hash is the tool's own human gate, and there is no second one. Then run the tool's `wiki-ingest` skill on the registered `fulltext/<attachment key>.md` files; the pages it writes cite the literature note as `[[<citation key>]]`. A note whose text changed after compile is reported `recompile-needed` by `verify`.
````

`skills/setup-vault/SKILL.md`: insert before `## Migrate an older vault`:

````markdown
The compile tool is a Claude Code plugin and installs from its own marketplace, after per-item consent, with two commands the person runs (restart-to-activate):

```sh
claude plugin marketplace add AgriciDaniel/claude-obsidian
claude plugin install claude-obsidian@agricidaniel-claude-obsidian
```

Doctor's `compile-tool` probe reports the installed commit against the pin `ad67087`; a different commit is a warning, not a failure. Then adopt the vault into the tool once, with its own inspect-then-apply gate: `python3 "$ROOT/scripts/claude-obsidian.py" adopt PATH` (dry run), then the same command with `--apply --approved-plan-sha256 <hash>` from the dry run. The tool refuses to overwrite the vault's `.gitignore`; append its four rules by hand.
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

`wiki/` is a machine surface: pages are created and replaced only through the tool's `wiki-ingest` skill and its `transaction inspect` / `transaction apply` gate. Never `Write` or `Edit` under `wiki/`; the pre-tool-use guard refuses it. Register sources first with `python3 -m research_vault compile KEY --vault PATH` (see `capture-source`).

## Orientation first

Before proposing any page, read `wiki/index.md`, `wiki/hot.md` and the recent `log/` entries. Arrive knowing which concept pages exist and what happened recently — never propose a page that duplicates one already indexed.

## The 2+-source threshold, and the tool's compilation-value gate

A concept page earns its existence at two or more captured sources on the same topic — the vault's one threshold. The tool adds its own gate, which is compatible and stricter: create or expand a canonical page only when the source adds durable synthesis, navigation, a decision, or a reusable connection beyond the source page itself. Two sources set side by side with nothing said about how they relate are a compilation, and a compilation earns no page: say plainly that there was nothing to arrange yet.

## Minimum-link discipline

Every concept page carries at least two outgoing wikilinks, at least one of them a `[[<citation key>]]`. The tool's lint reports orphans (no incoming link) and dead links; both block its checkpoint.

## Frontmatter

The tool's lint requires six keys on every page under `wiki/`: `title`, `type`, `status`, `created`, `updated`, `tags`. `type` is one of the tool's own values (`source`, `concept`, `entity`, `meta`); the vault derives none for `wiki/`. No `{{TITLE}}`-style template exists for this layer any more.

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

- Modify: `docs/testing.md`, `docs/terminology.md` §4.4 (final registries), `.github/workflows/quality.yml:48-65`, `research_vault/templates/git/pre-commit` (comment, if Part A Task 12 did not add it)

**Interfaces:**

- Produces: the final §4.4 rows, verbatim:

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

`docs/terminology.md` §4.4: the three rows exactly as in Interfaces. `docs/testing.md`, replace "## The suite" through the end of its second paragraph with:

````markdown
## The suite

Offline (default): `python -m pytest tests -q -n auto` from the repo root, inside `.venv` (xdist pinned; pass `-n` on the command line, never in addopts). Env-gated live legs are skipped unless flagged; live runs stay serial.

**Live invocation.** Two Zotero 10.0.1 instances run on this machine: production on `localhost:23119` (server id from `python -m research_vault probe`) and an unsynced test instance on `localhost:23129` (profile `~/.zotero/zotero/rfnse7tz.default`, data `~/Zotero/`, one add-on: Better BibTeX 9.0.63 with the library's citekey pattern). Read-only legs run against whichever `--base` they are given; **write-capable legs run only against the test instance** and refuse `zotero.DEFAULT_BASE`:

```bash
RV_LIVE=1 python -m pytest tests -q                                   # read-only local-Zotero legs
RV_LIVE=1 RV_LIVE_WRITE_BASE=http://localhost:23129 python -m pytest tests -q -k live   # plus the add/trash/delete leg (one consent dialog the first time)
RV_LIVE_NET=1 RV_MAILTO=<real address> python -m pytest tests -q     # external-registry legs
```

The first write leg on a machine pops Zotero's consent dialog on the test instance; answer **Always Allow** there and the key persists in the scratch vault's `.research-vault/zotero-keys.json` for the run. If a later run re-opens the dialog, export that key as `RV_LIVE_WRITE_KEY` and the leg runs unattended. Gated tests are invisible to offline suite-green — after renames or seam moves, run the live legs before claiming the wave complete.
````

and under "## Poking Zotero" item 1 add: "`python -m research_vault probe --base http://localhost:23129` names the test instance." Remove the `RV_LIVE_AUTOEXPORT_VAULT` and `test_dispositions` sentence if Part A Task 2 left any of it.

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
- Modify: `research_vault/zotero.py` (`trash_item(key, version)`, `delete_item(key, version)` — PATCH `{"deleted": true}` and DELETE with `If-Unmodified-Since-Version`; both need the API key), `tests/fixtures/lifecycle/README.md` (the trashed fixture becomes replayable), `tests/test_lifecycle.py` (a replay test for the observed trashed transition), `tests/conftest.py` (`pytest_collection_modifyitems` also skips `live_write` without `RV_LIVE_WRITE_BASE`; `pyproject.toml` registers the marker `live_write: writes to the Zotero test instance (set RV_LIVE_WRITE_BASE)`)

**Interfaces:**

- Produces: `ZoteroClient.trash_item(key: str, version: int) -> int` and `delete_item(key: str, version: int) -> int` (both return the HTTP status, 204 expected; 412 raises `ZoteroError(UNMATCHED)` "version moved").

- [ ] **Step 1: Write the live tests**

`tests/test_capture_live.py`:

```python
"""Live legs against Zotero 10 (spec §7). Read legs need RV_LIVE=1; the write
leg needs RV_LIVE_WRITE_BASE too and refuses the production instance."""

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
    assert item_key not in trashed_versions and item_key in trash
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
RV_LIVE=1 RV_LIVE_WRITE_BASE=http://localhost:23129 .venv/bin/python -m pytest tests/test_capture_live.py -q -k transitions -s
```

Expected: both PASS (answer **Always Allow** on the test instance's dialog the first time). **Unmeasured:** whether a second `authorize` for the same `appName` after **Always Allow** returns the remembered key silently or re-opens the dialog — the sitting authorized once, and `tmp_vault` is fresh per run so the key store never carries over. If the dialog reappears, read the granted key from the attended run's `<basetemp>/.../.research-vault/zotero-keys.json` and export it as `RV_LIVE_WRITE_KEY`; the leg then runs unattended (`add` uses a preset `client.api_key` before consulting the store). Record which of the two happened in `tests/fixtures/lifecycle/README.md`. Copy the written `items-trashed.json` from the test's `tmp_vault` (pytest prints the path with `--basetemp`; use `--basetemp=/tmp/rvlive`) to `tests/fixtures/lifecycle/items-trashed.json`.

- [ ] **Step 3: Implement the two write helpers and the replay test**

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

Update the fixture README's `trash-trashed.json` bullet: "superseded by `items-trashed.json`, recorded live on 2026-MM-DD by `tests/test_capture_live.py`; the transition now replays." Register the `live_write` marker and its skip.

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

- Modify: nothing in the tree except what the live run touches; this task's deliverable is a message and, on go-ahead, one GitHub issue on `zotero/zotero`.

- [ ] **Step 1: Full verification**

```bash
.venv/bin/python -m pytest tests -q -n auto
ruff format --check research_vault tests scripts hooks && ruff check research_vault tests scripts hooks && mypy research_vault
.venv/bin/python -m pytest tests -q --cov=research_vault --cov-branch --cov-report=lcov:lcov.info && .venv/bin/crap4py research_vault --lcov lcov.info --max-crap 30 && .venv/bin/drywall research_vault
RV_LIVE=1 .venv/bin/python -m pytest tests -q -k live
python3 scripts/mutation_gate.py --lcov lcov.info --max-workers 1 --base main
git status --porcelain   # must be empty
```

Expected: every command exits 0; report the pytest counts and the mutation-gate summary line verbatim. Add the attended leg's result from Task 5 to the report; it is not re-run here.

- [ ] **Step 2: Draft the upstream issue and wait for go-ahead**

Spec §6 keeps verify's update-notice check because Zotero exposes its Retraction Watch verdict nowhere a client can read, "and asking them to is worth an issue." Draft, do not post:

```
Title: Local API: expose the retraction flag on item JSON

Zotero 10.0.1 flags retracted items natively (retractions.js, the
retractedItems table) and warns at cite time, but the local API exposes
that verdict nowhere: no field in item JSON or meta, and /retractions and
/retracted both return 404 (measured 2026-09-05). A client that keeps its
own retraction check therefore duplicates work Zotero has already done.
Request: a boolean (or the notice's date and type) on item JSON, or an
endpoint listing retracted item keys, on the local API.
```

Post only when the user says so in that turn: `gh issue create --repo zotero/zotero --title "..." --body "..."`. Record the issue number in the completion message.

- [ ] **Step 3: Merge to `main`**

Per `AGENTS.md`: fetch first, merge back to `main` locally and push `main` to origin in the same motion. If this part ran on `main` directly, push.

- [ ] **Step 4: Completion message**

Report: the tasks landed (with commit shas), the tracer results (Task 1), the live-leg results (Task 5), the issue number or that it was not posted, and anything skipped with its reason. Part A Task 20 delivered decision 23's invariant-5 report; restate it in one line only if the write-side gate changed since.

______________________________________________________________________

## Self-review

### Spec coverage

This part's sections only; Part A's table carries the rest and names these tasks as `B n`.

| Spec section          | Requirement                                                                                                                      | Task |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---- |
| §1 invariant 6        | falsifiability: full verification, write-capable live legs, mutation gate                                                        | 5, 6 |
| §3.1                  | alias probe (T5)                                                                                                                 | 1    |
| §4.1–4.3              | adoption at `ad67087`; tracers T1–T4 before any compile task; `capture` unused; modes; results recorded in the plan and the spec | 1, 2 |
| §4.4                  | the wrapper's ledger record carries `content_sha256`, the value `captured-set` compares for `recompile-needed`                   | 2    |
| §4.5                  | wrapper owns selection, locators, ledger records, invocation; no prompt                                                          | 2    |
| §5                    | setup skill's compile-tool install and adoption steps; `compile-tool` probe consumed                                             | 3    |
| §6 skills             | synthesis-conventions rewritten; compile sections of capture-source and setup-vault                                              | 3    |
| §6 update-notice kept | the upstream issue, drafted and gated                                                                                            | 6    |
| §7                    | live legs on the test instance; the missing trashed snapshot; `docs/testing.md`                                                  | 4, 5 |
| Assembly decision 21  | the dated CRAP deferral closed                                                                                                   | 4    |
| Decision 22           | tracer results land here and in the spec                                                                                         | 1    |

### Placeholder scan

The `2026-MM-DD` tokens in Task 1's results block and Task 5's fixture README sentence are dates the executor fills at run time; nothing else is deferred.

### Type consistency

- `compile.ledger_record` consumes `notes.Provenance` (Part A Task 11) and writes the `fulltext.write` sha256 (Part A Task 10) as `content_sha256`, the value `captured._structural` (Part A Task 15) compares.
- `ZoteroClient.versions()` returns `(map, version)`; `trash_versions()` returns the map alone — used that way in Task 5.
- The `compile` check id Task 2 registers is in the §4.4 row Task 4 fixes.
