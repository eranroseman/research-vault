# Plan A: Bridge Core + Plugin Skeleton — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A dependency-free Python core (`harness_core`) that talks to local Zotero + Better BibTeX, translates paths across the WSL boundary, maintains the in-repo bibliography with a staleness check, and generates §5-conformant literature notes with managed regions and stable claim anchors — plus the installable Claude Code plugin skeleton.

**Architecture:** Deterministic-Python-core + thin-prompt-skill split (spec §7 "Shipped architecture"). This plan builds only the deterministic core and packaging; skills arrive in Plan D. Every module is stdlib-only, testable against canned fixtures, with live tests auto-skipped when Zotero is absent.

**Tech Stack:** Python ≥3.10, stdlib only (urllib, json, hashlib, subprocess, pathlib). pytest (dev-only). No third-party runtime dependencies — auditability is a trust feature (spec §1).

**Spec:** `docs/superpowers/specs/2026-08-16-foundation-spec.md` (APPROVED 2026-08-16). Section references (§N) below point there.

## Global Constraints

- **No absolute paths ever land in the vault repo** — resolve at use time via the path shim; per-machine config is gitignored (§4).
- **Stdlib-only runtime** for `harness_core`; pytest is the only dev dependency.
- **Four-state result vocabulary** everywhere a check can run: `MATCHED | UNMATCHED | UNREACHABLE | SKIPPED` (§6) — this plan introduces the enum; Plan B builds the checkers.
- **Actor convention** for any recorded identity: `human:<id>` / `<agent>/<version>` / `process:<id>` (§5).
- **Managed regions are full re-render**. Preservation contract (ruling): the **free region below the close marker survives byte-for-byte**; **frontmatter is preserved semantically** — every key outside the renderer's owned field set passes through with its value intact, serialization normalized (§3/§5).
- **Execution isolation (ruling):** create the isolated workspace via `superpowers:using-git-worktrees` at execution start (branch `build/plan-a` in a worktree); all Run/Commit paths are relative to that worktree root, not `~/knowledge-harness` directly.
- **Manifest code blocks (ruling):** lines like `// .claude-plugin/plugin.json` inside JSON fences are plan annotations naming the target file — never write them into the file; JSON has no comments and the tests parse strictly.
- **Block IDs derive from stable content** (Zotero annotation key, else quote hash), never render order (§5).
- **Zotero 9 is the floor**; Zotero 10 features are feature-detected, never assumed (§2).
- **Quotes render as blockquotes** under a claim line carrying tag + citation + anchor (§5).
- Commit messages: conventional (`feat:`, `test:`, `chore:`).
- Repo: `~/knowledge-harness` (this repo doubles as plugin + marketplace, §8). Work on branch `build/plan-a`.
- **Execution conventions (cwd resets between steps under subagent execution):** every command starts from the isolated worktree root. Every test Run begins `cd core && source .venv/bin/activate`; every Commit runs from the worktree root after `cd "$(git rev-parse --show-toplevel)"`. Never `cd ~/knowledge-harness` during implementation. This machine's system Python is PEP 668 externally managed — the venv from Task 1 is mandatory, not optional.
- **Recorded deviation (selector capture):** §5 requires quote prefix/suffix capture at extraction. BBT's annotation payload carries no surrounding context, and deriving it needs PDF text extraction — outside this stdlib-only plan. Task 6 Part B renders the selector comment whenever context fields are present; **Plan B owns producing them** (its quote-verification work requires PDF text access anyway) and must backfill selectors for any notes imported before it lands; Plan B's selector consumer also unescapes the HTML-escaped selector values symmetrically (Task 6/7 ruling). This is an explicit, tracked deviation — not a silent drop.

## File Structure

```
knowledge-harness/
├── .claude-plugin/
│   ├── plugin.json           # plugin manifest (Task 1)
│   └── marketplace.json      # self-marketplace (Task 1)
├── core/
│   ├── pyproject.toml        # package metadata, pytest config (Task 1)
│   ├── harness_core/
│   │   ├── __init__.py       # version, Result enum (Task 1)
│   │   ├── frontmatter.py    # flat YAML subset: parse/serialize (Task 2)
│   │   ├── zotero.py         # BBT JSON-RPC + local-API clients, feature detect (Task 3)
│   │   ├── paths.py          # machine config + wslpath shim (Task 4)
│   │   ├── bibliography.py   # CSL JSON load, citekey universe, staleness, commit step (Task 5)
│   │   ├── notes.py          # literature-note render/re-render, block IDs, hashes (Task 6)
│   │   └── __main__.py       # CLI: probe / import-note / staleness (Task 7)
│   └── tests/
│       ├── conftest.py       # fixtures: canned RPC payloads, tmp vault, live-skip marker (Task 1)
│       ├── test_frontmatter.py
│       ├── test_zotero.py
│       ├── test_paths.py
│       ├── test_bibliography.py
│       ├── test_notes.py
│       └── test_cli_live.py  # live smoke, skipped without Zotero
```

One module = one responsibility. `notes.py` is one composite Task 6: Part A builds render mechanics and Part B completes annotation anchors/hashes before the unit's single commit and review.

______________________________________________________________________

### Task 1: Package + plugin skeleton

**Files:**

- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Create: `core/pyproject.toml`
- Create: `core/harness_core/__init__.py`
- Create: `core/tests/conftest.py`
- Test: `core/tests/test_skeleton.py`

**Interfaces:**

- Consumes: nothing (first task).

- Produces: `harness_core.Result` (enum: `MATCHED`, `UNMATCHED`, `UNREACHABLE`, `SKIPPED`), `harness_core.__version__: str`; pytest marker `live` (auto-skipped unless `HARNESS_LIVE=1`); fixture `tmp_vault(tmp_path) -> Path` (vault tree per §3).

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_skeleton.py
import json
from pathlib import Path

import harness_core


REPO = Path(__file__).resolve().parents[2]


def test_version_and_result_enum():
    assert harness_core.__version__ == "0.1.0"
    assert [r.name for r in harness_core.Result] == [
        "MATCHED", "UNMATCHED", "UNREACHABLE", "SKIPPED",
    ]


def test_plugin_manifest_valid():
    manifest = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "knowledge-harness"
    assert manifest["version"] == "0.1.0"
    for key in ("description", "author", "license"):
        assert key in manifest


def test_marketplace_lists_plugin():
    market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())
    names = [p["name"] for p in market["plugins"]]
    assert "knowledge-harness" in names


def test_tmp_vault_fixture(tmp_vault):
    for d in ("+", "literatures", "atlas", "calendar", "efforts", "x"):
        assert (tmp_vault / d).is_dir()
    assert (tmp_vault / ".git").is_dir()
```

- [ ] **Step 2: Run test to verify it fails**

Run (bootstraps the venv first — PEP 668 blocks system pip, and later steps assume it exists):

```bash
cd core && python3 -m venv .venv && source .venv/bin/activate
pip install -q pytest
python -m pytest tests/test_skeleton.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'harness_core'`

- [ ] **Step 3: Write the package, manifests, and conftest**

```toml
# core/pyproject.toml
[project]
name = "harness-core"
version = "0.1.0"
description = "Deterministic core for the knowledge-harness plugin"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8"]

[tool.pytest.ini_options]
markers = ["live: requires a running local Zotero (set HARNESS_LIVE=1)"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["harness_core*"]
```

```python
# core/harness_core/__init__.py
"""Deterministic core for the knowledge-harness plugin (spec docs/superpowers/specs/2026-08-16-foundation-spec.md)."""
import enum

__version__ = "0.1.0"

AGENT_ACTOR = f"harness_core/{__version__}"  # §5 actor convention for process-written records


class Result(enum.Enum):
    MATCHED = "MATCHED"
    UNMATCHED = "UNMATCHED"
    UNREACHABLE = "UNREACHABLE"
    SKIPPED = "SKIPPED"
```

```json
// .claude-plugin/plugin.json
{
  "name": "knowledge-harness",
  "description": "Trust-first academic research on an Obsidian-convention vault: Zotero bridge, per-claim provenance, deterministic citation gates.",
  "version": "0.1.0",
  "author": { "name": "Eran Roseman" },
  "homepage": "https://github.com/eranroseman/knowledge-harness",
  "repository": "https://github.com/eranroseman/knowledge-harness",
  "license": "MIT",
  "keywords": ["research", "zotero", "citations", "provenance", "obsidian"]
}
```

```json
// .claude-plugin/marketplace.json
{
  "name": "knowledge-harness",
  "owner": { "name": "Eran Roseman" },
  "plugins": [
    {
      "name": "knowledge-harness",
      "source": "./",
      "description": "Trust-first academic research harness: Zotero bridge, per-claim provenance, deterministic citation gates."
    }
  ]
}
```

```python
# core/tests/conftest.py
import os
import subprocess

import pytest

VAULT_DIRS = ["+", "literatures", "atlas", "calendar", "efforts", "x"]


@pytest.fixture
def tmp_vault(tmp_path):
    for d in VAULT_DIRS:
        (tmp_path / d).mkdir()
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return tmp_path


def pytest_collection_modifyitems(config, items):
    if os.environ.get("HARNESS_LIVE") == "1":
        return
    skip = pytest.mark.skip(reason="live Zotero not enabled (HARNESS_LIVE=1)")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)
```

- [ ] **Step 4: Install the package editable, run tests to verify they pass**

Run (venv exists from Step 2):

```bash
cd core && source .venv/bin/activate
pip install -e ".[dev]" -q
python -m pytest tests/test_skeleton.py -v
```

Expected: 4 PASS.

Also add `core/.venv/` to the worktree-root `.gitignore` (committed with this task).

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add .claude-plugin core .gitignore
git commit -m "feat: harness_core package + plugin/marketplace skeleton"
```

(The `build/plan-a` worktree from the Execution-isolation ruling is already checked out; every required artifact — including `.gitignore` — is in this commit.)

______________________________________________________________________

### Task 2: Frontmatter — flat YAML subset

> **Ruling (execution-time):** the round-trip contract governs over the prescribed code. `_parse_item`'s `.split(", ")` corrupts values containing `", "` — implement quote-aware tokenization (track in-quote state; no pattern splitting) and add regression tests for three cases: comma inside a value, `": "` inside a value, and an escaped quote inside a value. The code block below is superseded on this point.

**Files:**

- Create: `core/harness_core/frontmatter.py`
- Test: `core/tests/test_frontmatter.py`

**Interfaces:**

- Consumes: nothing.
- Produces: `parse(text: str) -> tuple[dict, str]` (frontmatter dict, body) and `serialize(data: dict) -> str` (the `---`-fenced block, trailing newline). Values: `str`, `int`, `list[str]`, `list[dict]` (for `verified` events). Round-trip stable: `parse(serialize(d) + body)[0] == d`. Order preserved (insertion order).

The spec's schema is deliberately flat (§5, "flat frontmatter — the only thing Bases can query"), so a hand-rolled subset beats a PyYAML dependency. Supported: scalar strings/ints, block lists of scalars, block lists of single-line inline dicts (`- {by: "x", at: "2026-08-16", check: "doi"}`) for `verified` events.

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_frontmatter.py
from harness_core import frontmatter


SAMPLE = {
    "citekey": "smith2020",
    "type": "literature",
    "doi": "10.1000/xyz",
    "retrieved": "2026-08-16",
    "attachment-sha256": ["aa11", "bb22"],
    "status": "unreviewed",
    "verified": [
        {"by": "harness_core/0.1.0", "at": "2026-08-16", "check": "doi"},
    ],
    "aliases": ["Smith 2020 — Mortality decline"],
}


def test_roundtrip():
    text = frontmatter.serialize(SAMPLE) + "body line\n"
    data, body = frontmatter.parse(text)
    assert data == SAMPLE
    assert body == "body line\n"


def test_serialize_shape():
    text = frontmatter.serialize(SAMPLE)
    assert text.startswith("---\n") and text.endswith("---\n")
    assert 'citekey: "smith2020"' in text
    assert "attachment-sha256:" in text
    assert '- {by: "harness_core/0.1.0", at: "2026-08-16", check: "doi"}' in text


def test_parse_no_frontmatter():
    data, body = frontmatter.parse("just a body\n")
    assert data == {} and body == "just a body\n"


def test_quotes_in_titles_roundtrip():
    data = {"aliases": ['The "gold standard" myth'], "citekey": "x2020"}
    parsed, _ = frontmatter.parse(frontmatter.serialize(data))
    assert parsed == data


def test_parse_rejects_nested_maps():
    bad = '---\nouter:\n  inner: "x"\n---\n'
    try:
        frontmatter.parse(bad)
        assert False, "should raise"
    except frontmatter.FrontmatterError:
        pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_frontmatter.py -v`
Expected: FAIL — `No module named 'harness_core.frontmatter'`

- [ ] **Step 3: Implement**

```python
# core/harness_core/frontmatter.py
"""Flat YAML subset for note frontmatter (spec §5: flat, Bases-queryable)."""
import re


class FrontmatterError(ValueError):
    pass


_INLINE_DICT = re.compile(r"^\{(.*)\}$")


def _emit_scalar(v):
    if isinstance(v, int):
        return str(v)
    escaped = str(v).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def serialize(data: dict) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                if isinstance(item, dict):
                    inner = ", ".join(f"{k}: {_emit_scalar(v)}" for k, v in item.items())
                    lines.append(f"  - {{{inner}}}")
                else:
                    lines.append(f"  - {_emit_scalar(item)}")
        else:
            lines.append(f"{key}: {_emit_scalar(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def _parse_scalar(raw: str):
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw


def _parse_item(raw: str):
    m = _INLINE_DICT.match(raw)
    if not m:
        return _parse_scalar(raw)
    out = {}
    for part in m.group(1).split(", "):
        k, _, v = part.partition(": ")
        out[k.strip()] = _parse_scalar(v)
    return out


def parse(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.index("\n---\n", 4)
    block, body = text[4:end], text[end + 5:]
    data: dict = {}
    current_list = None
    for line in block.split("\n"):
        if line.startswith("  - "):
            if current_list is None:
                raise FrontmatterError(f"list item outside list: {line!r}")
            current_list.append(_parse_item(line[4:].strip()))
        elif line.startswith("  "):
            raise FrontmatterError(f"nested maps unsupported (flat schema, spec §5): {line!r}")
        else:
            key, sep, raw = line.partition(":")
            if not sep:
                raise FrontmatterError(f"bad line: {line!r}")
            if raw.strip() == "":
                current_list = []
                data[key] = current_list
            else:
                data[key] = _parse_scalar(raw)
                current_list = None
    return data, body
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_frontmatter.py -v`
Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: flat-YAML frontmatter parse/serialize"
```

______________________________________________________________________

### Task 3: Zotero clients — BBT JSON-RPC + local API

> **Ruling (execution-time):** the "no absolute paths in the vault repo" constraint governs persisted vault-repo content only — RPC test fixtures in the plugin repo are out of its scope, and BBT auto-export targets are necessarily absolute at runtime (stored in Zotero's profile, never in a committed file; Plan C's vault-setup computes them transiently at provisioning). Reviewer finding on the fixture path rejected. Pagination gets a two-page regression test.

**Files:**

- Create: `core/harness_core/zotero.py`
- Test: `core/tests/test_zotero.py`

**Interfaces:**

- Consumes: `harness_core.Result` (Task 1).

- Produces:

  - `class ZoteroError(Exception)` with `.result: Result` (`UNREACHABLE` on network/HTTP failure).
  - `class ZoteroClient(base="http://localhost:23119", timeout=5.0)`:
    - `ready() -> dict` — BBT `api.ready`, e.g. `{"zotero": "9.0.6", "betterbibtex": "9.0.55"}`.
    - `search(terms: str) -> list[dict]` — BBT `item.search`; CSL-JSON items carrying `citekey`.
    - `citekey_of(item_keys: list[str]) -> dict[str, str]` — BBT `item.citationkey`.
    - `attachments(citekey: str) -> list[dict]` — BBT `item.attachments`; raw dicts with `path`, `annotations` (list, possibly empty), `open`.
    - `export_csl(citekeys: list[str] | None) -> list[dict]` — BBT `item.export(citekeys, "Better CSL JSON")`; `None` = whole library via local API **`/api/users/0/items/top?format=csljson`** (paged; `/top` is the ruling — plain `/items` returns child attachments/notes with URI ids, live-verified).
    - `register_autoexport(target_path: str) -> dict` — BBT `autoexport.add`; returns the RPC result verbatim.
    - `supports_local_writes() -> bool` — **fail-closed capability check (ruling)**: True only when the Zotero major version reported by `ready()` is ≥ 10; False on Zotero 9 and on any error. HTTP-status probing is rejected — Zotero 9 answers 400, not 501, to write probes (live-verified), so status sniffing fails open (§2).
  - `_rpc(method: str, params: list) -> object` (module-private, patchable in tests).

- [ ] **Step 1: Write the failing test (fixtures, no network)**

```python
# core/tests/test_zotero.py
import pytest

from harness_core import Result, zotero


class FakeTransport:
    """Patches ZoteroClient._post/_get with canned payloads."""
    def __init__(self):
        self.rpc_calls = []
        self.canned_rpc = {
            "api.ready": {"zotero": "9.0.6", "betterbibtex": "9.0.55"},
            "item.search": [{"id": "smith2020", "citekey": "smith2020",
                             "title": "Mortality decline", "type": "article-journal"}],
            "item.citationkey": {"2WHVXRX3": "smith2020"},
            "item.attachments": [{"path": "D:\\Zotero\\storage\\AB12CD34\\smith2020.pdf",
                                  "open": "zotero://open-pdf/library/items/AB12CD34",
                                  "annotations": []}],
            "item.export": [{"id": "smith2020", "type": "article-journal",
                             "title": "Mortality decline"}],
            "autoexport.add": {"path": "/vault/x/bibliography.json"},
        }

    def rpc(self, method, params):
        self.rpc_calls.append((method, params))
        return self.canned_rpc[method]


@pytest.fixture
def client(monkeypatch):
    c = zotero.ZoteroClient()
    fake = FakeTransport()
    monkeypatch.setattr(c, "_rpc", fake.rpc)
    c._fake = fake
    return c


def test_ready(client):
    info = client.ready()
    assert info["betterbibtex"] == "9.0.55"


def test_search_carries_citekey(client):
    items = client.search("mortality")
    assert items[0]["citekey"] == "smith2020"
    assert client._fake.rpc_calls[0] == ("item.search", ["mortality"])


def test_attachments_raw_windows_path(client):
    atts = client.attachments("smith2020")
    assert atts[0]["path"].startswith("D:\\")


def test_export_named_translator(client):
    client.export_csl(["smith2020"])
    assert client._fake.rpc_calls[0] == ("item.export", [["smith2020"], "Better CSL JSON"])


def test_network_failure_is_unreachable(monkeypatch):
    c = zotero.ZoteroClient(base="http://127.0.0.1:1")  # nothing listens
    with pytest.raises(zotero.ZoteroError) as e:
        c.ready()
    assert e.value.result is Result.UNREACHABLE


@pytest.mark.live
def test_live_ready_and_export():
    c = zotero.ZoteroClient()
    info = c.ready()
    assert "betterbibtex" in info
    items = c.export_csl(None)          # whole library, top-level, via local API
    assert isinstance(items, list) and len(items) > 0
    assert all("/" not in i["id"] for i in items[:25])   # citekey ids, not URIs
    # named-translator export by explicit citekey — the signature this plan bets on
    one = c.export_csl([items[0]["id"]])
    assert one and one[0]["id"] == items[0]["id"]
    # search signature (BBT rejects nested-list params — this catches regressions)
    assert isinstance(c.search(items[0]["id"]), list)
    # Zotero 9 on this machine: writes NOT supported — assert the real value,
    # not merely the type (fails open otherwise)
    major = int(str(info["zotero"]).split(".")[0])
    assert c.supports_local_writes() is (major >= 10)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_zotero.py -v`
Expected: FAIL — `No module named 'harness_core.zotero'`

- [ ] **Step 3: Implement**

```python
# core/harness_core/zotero.py
"""Clients for local Zotero: BBT JSON-RPC (citekeys, attachments, exports) and
the Zotero local web API (whole-library reads, write feature-detect). Spec §4."""
import json
import urllib.error
import urllib.request

from . import Result

CSL_TRANSLATOR = "Better CSL JSON"


class ZoteroError(Exception):
    def __init__(self, msg, result=Result.UNREACHABLE):
        super().__init__(msg)
        self.result = result


class ZoteroClient:
    def __init__(self, base="http://localhost:23119", timeout=5.0):
        self.base = base.rstrip("/")
        self.timeout = timeout

    # -- transport ---------------------------------------------------------
    def _http(self, url, data=None, headers=None, method=None):
        req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()
        except OSError as e:
            raise ZoteroError(f"Zotero unreachable at {self.base}: {e}") from e

    def _rpc(self, method, params):
        payload = json.dumps({"jsonrpc": "2.0", "method": method,
                              "params": params, "id": 1}).encode()
        status, body = self._http(f"{self.base}/better-bibtex/json-rpc", data=payload,
                                  headers={"Content-Type": "application/json"})
        if status != 200:
            raise ZoteroError(f"JSON-RPC HTTP {status}")
        reply = json.loads(body)
        if "error" in reply:
            raise ZoteroError(f"JSON-RPC error: {reply['error']}", Result.UNMATCHED)
        return reply["result"]

    # -- BBT surface -------------------------------------------------------
    def ready(self):
        return self._rpc("api.ready", [])

    def search(self, terms):
        # BBT 9.0.55 rejects [[terms]] with -32602; the param is a plain string (live-verified)
        return self._rpc("item.search", [terms])

    def citekey_of(self, item_keys):
        return self._rpc("item.citationkey", [item_keys])

    def attachments(self, citekey):
        return self._rpc("item.attachments", [citekey])

    def register_autoexport(self, target_path):
        return self._rpc("autoexport.add", [target_path, CSL_TRANSLATOR])

    def export_csl(self, citekeys):
        if citekeys is not None:
            out = self._rpc("item.export", [citekeys, CSL_TRANSLATOR])
            return out if isinstance(out, list) else json.loads(out)
        # whole library: local web API mirror, TOP-LEVEL items only, paged (§4 export scope).
        # /items (without /top) includes child attachments/notes whose CSL ids are
        # zotero.org URIs — polluting the citekey universe (live-verified);
        # /items/top returns citekey ids only.
        items, start = [], 0
        while True:
            status, body = self._http(
                f"{self.base}/api/users/0/items/top?format=csljson&limit=100&start={start}")
            if status != 200:
                raise ZoteroError(f"local API HTTP {status}")
            page = json.loads(body)
            page_items = page["items"] if isinstance(page, dict) else page
            items.extend(page_items)
            if len(page_items) < 100:
                return items
            start += 100

    # -- feature detection (§2): default CLOSED, affirmative signal required --
    def supports_local_writes(self):
        # Zotero 9.0.6 answers HTTP 400 (not 501) to a write probe (live-verified
        # 2026-08-16), so response-code sniffing fails open. Gate on the version
        # BBT reports; writes are a Zotero 10+ feature (spec §2).
        try:
            major = int(str(self.ready().get("zotero", "0")).split(".")[0])
        except (ValueError, ZoteroError):
            return False
        return major >= 10
```

- [ ] **Step 4: Run fixture tests to verify they pass**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_zotero.py -v`
Expected: 5 PASS, 1 SKIP (live)

- [ ] **Step 5: Run the live smoke against this machine**

Run: `cd core && source .venv/bin/activate && HARNESS_LIVE=1 python -m pytest tests/test_zotero.py::test_live_ready_and_export -v`
Expected: PASS (Zotero 9.0.6 + BBT 9.0.55 respond; library non-empty; ids are citekeys; `supports_local_writes()` is False on Zotero 9). The live test now exercises `search`, named-translator `item.export`, and the top-level export — the three surfaces whose signatures this plan bets on; the BBT JSON-RPC doc (retorque.re/zotero-better-bibtex/exporting/json-rpc/) is the reference for any residual deviation. **`register_autoexport` ships live-unverified until Plan C provisions it** — its first real invocation is `vault-setup`, which validates or corrects the parameter shape then. Also in this step: (a) append the verified facts to `docs/environment.md` — "Zotero 9.0.6 answers HTTP 400 (not 501) to POST /api/users/0/items (2026-08-16)" and "local API `/items/top?format=csljson` returns citekey ids; `/items` includes URI-id children"; (b) if the library has an annotated PDF, call `attachments()` on it and record the observed annotation dict shape in `docs/environment.md` — if none exists, ask your human partner to highlight one line in any PDF in Zotero, then record it (the shape is currently source-verified only).

- [ ] **Step 6: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core docs/environment.md
git commit -m "feat: Zotero clients with fail-closed feature detection; record live-verified API facts"
```

(`docs/environment.md` carries this task's live-verified facts — the 400-not-501 write probe, `/items/top` id behavior, and the observed annotation shape — and ships in the same commit.)

______________________________________________________________________

### Task 4: Path shim — per-machine config + wslpath

**Files:**

- Create: `core/harness_core/paths.py`
- Test: `core/tests/test_paths.py`

**Interfaces:**

- Consumes: nothing.

- Produces:

  - `load_machine_config(vault_root: Path) -> dict` — reads `<vault>/.harness/machine.json`; `{}` when absent. `vault-setup` (Plan C) writes it and gitignores `.harness/`.
  - `to_local(path: str, vault_root: Path) -> pathlib.Path` — resolution order: (1) config `path_map` prefix match (case-insensitive on the prefix), (2) `wslpath -u` subprocess, (3) raise `PathError`. Never writes anything into the repo (Global Constraints).

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_paths.py
import json
import subprocess
from pathlib import Path

import pytest

from harness_core import paths


@pytest.fixture
def vault_with_map(tmp_vault):
    h = tmp_vault / ".harness"
    h.mkdir()
    (h / "machine.json").write_text(json.dumps(
        {"path_map": {"D:\\Zotero\\": "/mnt/d/Zotero/"}}))
    return tmp_vault


def test_prefix_map(vault_with_map):
    p = paths.to_local("D:\\Zotero\\storage\\AB\\x.pdf", vault_with_map)
    assert p == Path("/mnt/d/Zotero/storage/AB/x.pdf")


def test_prefix_map_case_insensitive(vault_with_map):
    p = paths.to_local("d:\\zotero\\storage\\AB\\x.pdf", vault_with_map)
    assert p == Path("/mnt/d/Zotero/storage/AB/x.pdf")


def test_wslpath_fallback(tmp_vault, monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(
        a, 0, stdout="/mnt/d/Zotero/storage/AB/x.pdf\n"))
    p = paths.to_local("D:\\Zotero\\storage\\AB\\x.pdf", tmp_vault)
    assert p == Path("/mnt/d/Zotero/storage/AB/x.pdf")


def test_unresolvable_raises(tmp_vault, monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError("wslpath missing")
    monkeypatch.setattr(subprocess, "run", boom)
    with pytest.raises(paths.PathError):
        paths.to_local("D:\\x.pdf", tmp_vault)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_paths.py -v`
Expected: FAIL — `No module named 'harness_core.paths'`

- [ ] **Step 3: Implement**

```python
# core/harness_core/paths.py
"""Windows→WSL path resolution at use time; nothing machine-specific in-repo (spec §4)."""
import json
import subprocess
from pathlib import Path


class PathError(Exception):
    pass


def load_machine_config(vault_root: Path) -> dict:
    f = Path(vault_root) / ".harness" / "machine.json"
    if not f.is_file():
        return {}
    return json.loads(f.read_text())


def to_local(path: str, vault_root: Path) -> Path:
    cfg = load_machine_config(vault_root)
    for prefix, repl in cfg.get("path_map", {}).items():
        if path.lower().startswith(prefix.lower()):
            rest = path[len(prefix):].replace("\\", "/")
            return Path(repl + rest)
    try:
        proc = subprocess.run(["wslpath", "-u", path],
                              capture_output=True, text=True, check=False)
        if proc.returncode == 0 and proc.stdout.strip():
            return Path(proc.stdout.strip())
    except FileNotFoundError:
        pass
    raise PathError(f"cannot resolve {path!r}: no path_map match, wslpath unavailable")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_paths.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: per-machine path shim with wslpath fallback"
```

______________________________________________________________________

### Task 5: Bibliography — citekey universe, staleness, commit step

**Files:**

- Create: `core/harness_core/bibliography.py`
- Test: `core/tests/test_bibliography.py`

**Interfaces:**

- Consumes: `ZoteroClient.export_csl` (Task 3).

- Produces:

  - `BIB_PATH = "x/bibliography.json"` (§3/§4 — the one canonical location).
  - `load(vault_root) -> Bibliography` — `.citekeys: set[str]`, `.entry(citekey) -> dict | None`. Missing file ⇒ empty universe (not an error — doctor reports it).
  - `staleness(vault_root, client) -> Result` — `MATCHED` = committed file's item set equals a fresh whole-library export (compared as sorted citekey ids + per-entry title, the settle-window tolerance lives in the *caller*: Plan C's lint re-probes after 60 s before declaring stale, §4); `UNMATCHED` = differs; `UNREACHABLE` = Zotero down; `SKIPPED` = no committed file yet.
  - `write_and_commit(vault_root, items: list[dict]) -> bool` — writes sorted-by-id JSON, `git add x/bibliography.json && git commit` only when content changed; returns whether a commit happened.
  - **Writer-ownership note (§4):** in the finished system, BBT's on-change auto-export writes this file and the harness owns only the commit step. Plan A has no auto-export yet, so `write_and_commit` is the **interim writer** — an explicit, temporary deviation. Plan C's acceptance criteria include: register the auto-export, demote this function to commit-only (stage-and-commit the BBT-written file), and verify `staleness` reads MATCHED against genuine auto-export output (serialization differences between the two writers surface and die there, before the git-diffed bibliography becomes the rename detector in anger).

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_bibliography.py
import json
import subprocess

import pytest

from harness_core import Result, bibliography


ITEMS = [
    {"id": "smith2020", "title": "Mortality decline", "type": "article-journal"},
    {"id": "jones2021", "title": "Replication study", "type": "article-journal"},
]


class StubClient:
    def __init__(self, items):
        self._items = items
        self.fail = False

    def export_csl(self, citekeys):
        if self.fail:
            from harness_core.zotero import ZoteroError
            raise ZoteroError("down")
        return self._items


def test_write_and_commit_then_load(tmp_vault):
    changed = bibliography.write_and_commit(tmp_vault, ITEMS)
    assert changed is True
    bib = bibliography.load(tmp_vault)
    assert bib.citekeys == {"smith2020", "jones2021"}
    assert bib.entry("smith2020")["title"] == "Mortality decline"
    log = subprocess.run(["git", "log", "--oneline"], cwd=tmp_vault,
                         capture_output=True, text=True).stdout
    assert "bibliography" in log


def test_write_is_idempotent(tmp_vault):
    assert bibliography.write_and_commit(tmp_vault, ITEMS) is True
    assert bibliography.write_and_commit(tmp_vault, ITEMS) is False  # no second commit


def test_staleness_matched(tmp_vault):
    bibliography.write_and_commit(tmp_vault, ITEMS)
    assert bibliography.staleness(tmp_vault, StubClient(ITEMS)) is Result.MATCHED


def test_staleness_unmatched(tmp_vault):
    bibliography.write_and_commit(tmp_vault, ITEMS)
    newer = ITEMS + [{"id": "lee2022", "title": "New paper", "type": "article-journal"}]
    assert bibliography.staleness(tmp_vault, StubClient(newer)) is Result.UNMATCHED


def test_staleness_unreachable(tmp_vault):
    bibliography.write_and_commit(tmp_vault, ITEMS)
    client = StubClient(ITEMS)
    client.fail = True
    assert bibliography.staleness(tmp_vault, client) is Result.UNREACHABLE


def test_staleness_skipped_without_file(tmp_vault):
    assert bibliography.staleness(tmp_vault, StubClient(ITEMS)) is Result.SKIPPED
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_bibliography.py -v`
Expected: FAIL — `No module named 'harness_core.bibliography'`

- [ ] **Step 3: Implement**

```python
# core/harness_core/bibliography.py
"""The in-repo citekey universe: x/bibliography.json (spec §4)."""
import json
import subprocess
from pathlib import Path

from . import Result
from .zotero import ZoteroError

BIB_PATH = "x/bibliography.json"


class Bibliography:
    def __init__(self, items):
        self._by_id = {i["id"]: i for i in items}

    @property
    def citekeys(self):
        return set(self._by_id)

    def entry(self, citekey):
        return self._by_id.get(citekey)


def _path(vault_root):
    return Path(vault_root) / BIB_PATH


def load(vault_root) -> Bibliography:
    p = _path(vault_root)
    if not p.is_file():
        return Bibliography([])
    return Bibliography(json.loads(p.read_text()))


def _canonical(items):
    return json.dumps(sorted(items, key=lambda i: i["id"]), indent=1, sort_keys=True)


def write_and_commit(vault_root, items) -> bool:
    p = _path(vault_root)
    new = _canonical(items)
    if p.is_file() and p.read_text() == new:
        return False
    p.write_text(new)
    subprocess.run(["git", "add", BIB_PATH], cwd=vault_root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "chore: bibliography export"],
                   cwd=vault_root, check=True)
    return True


def _fingerprint(items):
    return sorted((i["id"], i.get("title", "")) for i in items)


def staleness(vault_root, client) -> Result:
    p = _path(vault_root)
    if not p.is_file():
        return Result.SKIPPED
    try:
        fresh = client.export_csl(None)
    except ZoteroError:
        return Result.UNREACHABLE
    committed = json.loads(p.read_text())
    return Result.MATCHED if _fingerprint(committed) == _fingerprint(fresh) \
        else Result.UNMATCHED
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_bibliography.py -v`
Expected: 6 PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: bibliography universe, staleness check, harness-owned commit step"
```

______________________________________________________________________

### Task 6: Literature notes + claim anchors (composite review unit)

> **Composite-task ruling:** Part A's temporary `render_claim` stub is working-tree scaffolding, not a deliverable. One implementer receives this entire Task 6 brief, completes Parts A and B, runs the combined `test_notes.py`, commits once after Part B, and then receives one task review. There is no dispatch, commit, or review boundary between the parts.
>
> **Ruling (execution-time, edge-case package approved):** (1) Task 6's normalized annotation contract stands; Task 7 maps raw BBT fields (`annotationPageLabel`, `annotationComment`, `annotationType`, …) to it at the boundary — mapping authority is the live shape recorded in docs/environment.md; unknown/missing fields degrade to comment-only rendering, never crash. (2) The closing marker matches only as an exact standalone line (collision regression included). (3) Multiline quotes: every line blockquote-prefixed; multiline comments whitespace-collapse to one inline claim line — single-line claims are load-bearing for `^claim-id` block addressing. (4) Selector values HTML-escaped (quotes, ampersands, `-->`); **escaping is symmetric — Plan B's selector consumer must unescape identically** (added to the selector-deviation contract).

**Files:**

- Create: `core/harness_core/notes.py`
- Test: `core/tests/test_notes.py`

**Interfaces:**

- Consumes: `frontmatter.parse/serialize` (Task 2).

- Produces:

  - `MANAGED_OPEN = "%%hk-managed%%"`, `MANAGED_CLOSE = "%%/hk-managed%%"` (§3 managed markers; `hk-` prefix so a later ZotLit install can't collide).
  - `note_path(vault_root, citekey) -> Path` — `literatures/<citekey>.md`.
  - `render_note(item: dict, attachment_hashes: list[str], annotations: list[dict], existing: str | None, retrieved: str) -> str` — full note text. Frontmatter per §5 (`citekey`, `type: "literature"`, `doi`/`url`/`pmid`/`version` when present in the CSL item, `retrieved`, `attachment-sha256`, `status: "unreviewed"`, `aliases: [title]`). Managed region: title heading + one claim per annotation (Part B renders them). Free region: everything below `MANAGED_CLOSE` in `existing` is preserved **byte-for-byte**; a fresh note gets the seed free region `\n## Notes\n`.
  - Re-render is idempotent: `render_note(..., existing=render_note(...)) == render_note(...)` given identical inputs.
  - `retrieved` is preserved from an existing note's frontmatter (day-one, never overwritten — §5).

- [ ] **Part A — Step 1: Write the foundational failing tests**

```python
# core/tests/test_notes.py
from harness_core import frontmatter, notes


ITEM = {"id": "smith2020", "type": "article-journal", "title": "Mortality decline",
        "DOI": "10.1000/xyz"}


def test_note_path(tmp_vault):
    assert notes.note_path(tmp_vault, "smith2020").as_posix().endswith(
        "literatures/smith2020.md")


def test_fresh_note_shape():
    text = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    data, body = frontmatter.parse(text)
    assert data["citekey"] == "smith2020"
    assert data["type"] == "literature"
    assert data["doi"] == "10.1000/xyz"
    assert data["retrieved"] == "2026-08-16"
    assert data["attachment-sha256"] == ["aa11"]
    assert data["status"] == "unreviewed"
    assert data["aliases"] == ["Mortality decline"]
    assert notes.MANAGED_OPEN in body and notes.MANAGED_CLOSE in body
    assert body.rstrip().endswith("## Notes")


def test_free_region_survives_rerender():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    edited = v1 + "my own prose [[link]] under the markers\n"
    v2 = notes.render_note(ITEM, ["aa11", "bb22"], [], existing=edited,
                           retrieved="2026-08-17")
    assert "my own prose [[link]] under the markers" in v2
    data, _ = frontmatter.parse(v2)
    assert data["retrieved"] == "2026-08-16"          # day-one value preserved
    assert data["attachment-sha256"] == ["aa11", "bb22"]  # managed metadata updated


def test_rerender_idempotent():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    v2 = notes.render_note(ITEM, ["aa11"], [], existing=v1, retrieved="2026-08-16")
    assert v1 == v2


def test_unowned_frontmatter_fields_survive_rerender():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    data, body = frontmatter.parse(v1)
    data["verified"] = [{"by": "harness_core/0.1.0", "at": "2026-08-16", "check": "doi"}]
    data["superseded-by"] = "smith2024"
    data["authority"] = "peer-reviewed journal"
    data["archive-url"] = "https://web.archive.org/web/x"
    edited = frontmatter.serialize(data) + body
    v2 = notes.render_note(ITEM, ["aa11"], [], existing=edited, retrieved="2026-08-17")
    kept, _ = frontmatter.parse(v2)
    assert kept["verified"] == data["verified"]
    assert kept["superseded-by"] == "smith2024"
    assert kept["authority"] == "peer-reviewed journal"
    assert kept["archive-url"] == "https://web.archive.org/web/x"


def test_free_region_byte_exact():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    with_blanks = v1 + "\n\n\nspaced prose\n"
    v2 = notes.render_note(ITEM, ["aa11"], [], existing=with_blanks, retrieved="2026-08-16")
    assert v2.endswith("\n## Notes\n\n\n\nspaced prose\n")
    emptied = v2[: v2.index(notes.MANAGED_CLOSE) + len(notes.MANAGED_CLOSE) + 1]
    v3 = notes.render_note(ITEM, ["aa11"], [], existing=emptied, retrieved="2026-08-16")
    assert v3.endswith(notes.MANAGED_CLOSE + "\n")   # emptied region stays empty
```

- [ ] **Part A — Step 2: Run tests to verify they fail**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_notes.py -v`
Expected: FAIL — `No module named 'harness_core.notes'`

- [ ] **Part A — Step 3: Implement rendering mechanics**

```python
# core/harness_core/notes.py
"""Literature-note generation: managed region + preserved free region (spec §3–§5)."""
from pathlib import Path

from . import frontmatter

MANAGED_OPEN = "%%hk-managed%%"
MANAGED_CLOSE = "%%/hk-managed%%"
SEED_FREE = "\n## Notes\n"


def note_path(vault_root, citekey) -> Path:
    return Path(vault_root) / "literatures" / f"{citekey}.md"


def _managed_body(item, annotations) -> str:
    lines = [MANAGED_OPEN, f"# {item.get('title', item['id'])}", ""]
    for ann in annotations:
        lines.append(render_claim(ann))          # completed in Part B before commit/review
    lines.append(MANAGED_CLOSE)
    return "\n".join(lines) + "\n"


def _split_free(existing) -> str:
    if existing is None:
        return SEED_FREE
    idx = existing.find(MANAGED_CLOSE)
    if idx == -1:
        return SEED_FREE
    # verbatim tail after "CLOSE\n" — byte-for-byte, including blank lines,
    # including a deliberately emptied free region (Global Constraint §3)
    return existing[idx + len(MANAGED_CLOSE) + 1:]


# Fields the renderer owns and may rewrite; EVERYTHING else in prior frontmatter
# passes through unchanged (verified events, superseded-by, authority, archive-url,
# human-added keys — §5 never-delete applies to metadata too).
MANAGED_FIELDS = {"citekey", "type", "attachment-sha256", "aliases",
                  "doi", "url", "pmid", "version"}


def render_note(item, attachment_hashes, annotations, existing, retrieved) -> str:
    prior = frontmatter.parse(existing)[0] if existing else {}
    fm = {"citekey": item["id"], "type": "literature"}
    if item.get("DOI"):
        fm["doi"] = item["DOI"]
    if item.get("URL"):
        fm["url"] = item["URL"]
    if item.get("PMID"):
        fm["pmid"] = item["PMID"]
    if item.get("version"):
        fm["version"] = item["version"]
    fm["retrieved"] = prior.get("retrieved", retrieved)   # day-one, never overwritten
    fm["attachment-sha256"] = attachment_hashes
    fm["status"] = prior.get("status", "unreviewed")
    fm["aliases"] = [item.get("title", item["id"])]
    for key, value in prior.items():                      # pass-through of unowned fields
        if key not in MANAGED_FIELDS and key not in fm:
            fm[key] = value
    return frontmatter.serialize(fm) + _managed_body(item, annotations) + _split_free(existing)
```

Add the temporary stub `def render_claim(ann): raise NotImplementedError` at module bottom. It exists only to run Part A's annotation-free tests; continue immediately into Part B, which replaces it before any commit or review.

- [ ] **Part A — Step 4: Run the foundational tests**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_notes.py -v`
Expected: 6 PASS

- [ ] **Part A — Step 5: Continue without a commit or review**

Continue directly to Part B; the temporary stub is never committed as a task deliverable.

______________________________________________________________________

#### Part B: Claim anchors — stable block IDs, blockquote quotes, selector capture

**Files:**

- Modify: `core/harness_core/notes.py` (replace the `render_claim` stub; add `claim_id`, `sha256_file`, `content_changed`)
- Test: `core/tests/test_notes.py` (append)

**Interfaces:**

- Consumes: Part A's in-progress `notes.py`.

- Produces:

  - `claim_id(annotation: dict) -> str` — `c-` + first 8 hex of sha256 of the annotation's Zotero `key` if present, else of its NFKC+whitespace-normalized `annotationText`. **Stable content, never render order** (§5 invariant).
  - `render_claim(annotation: dict) -> str` — §5 shape: claim line `- (quote) [@<citekey>, p. <pageLabel>] ^<claim_id>` followed by a blockquote of the exact text, then an HTML-comment selector line `<!-- hk-sel prefix="…" suffix="…" -->` carrying 32-char context (Web-Annotation capture, §5). Comment annotations (no quoted text) render as `- (paraphrase)` claim lines with the comment text inline, no blockquote.
  - `sha256_file(path: Path) -> str` — hex digest.
  - `content_changed(existing_text: str | None, attachment_hashes: list[str]) -> bool` — the §7 content-hash no-op comparator: False when the existing note's `attachment-sha256` equals the new list.
  - Annotation dict fields consumed (BBT `item.attachments` annotation shape): `key`, `type`, `annotationText`, `comment`, `pageLabel`, plus the parent `citekey` injected by the caller as `citekey`.

- [ ] **Part B — Step 1: Append the failing tests to `test_notes.py`**

```python
# append to core/tests/test_notes.py
QUOTE_ANN = {"key": "ANNKEY01", "type": "highlight", "citekey": "smith2020",
             "annotationText": "Mortality fell 12% (95% CI 8-16).",
             "comment": "", "pageLabel": "12",
             "context_prefix": "the cohort showed that ",
             "context_suffix": " across all strata studied"}

COMMENT_ANN = {"key": "ANNKEY02", "type": "note", "citekey": "smith2020",
               "annotationText": "", "comment": "Design is retrospective only",
               "pageLabel": "3"}


def test_claim_id_stable_from_key():
    a = notes.claim_id(QUOTE_ANN)
    b = notes.claim_id(dict(QUOTE_ANN, annotationText="edited text"))
    assert a == b                      # key wins over text
    assert a.startswith("c-") and len(a) == 10


def test_claim_id_from_text_when_no_key():
    ann = dict(QUOTE_ANN, key=None)
    a = notes.claim_id(ann)
    b = notes.claim_id(dict(ann, annotationText="Mortality  fell 12% (95% CI 8-16)."))
    assert a == b                      # whitespace-normalized


def test_render_quote_claim():
    out = notes.render_claim(QUOTE_ANN)
    lines = out.split("\n")
    cid = notes.claim_id(QUOTE_ANN)
    assert lines[0] == f"- (quote) [@smith2020, p. 12] ^{cid}"
    assert lines[1] == "  > Mortality fell 12% (95% CI 8-16)."
    assert 'hk-sel prefix="the cohort showed that "' in lines[2]


def test_render_comment_claim():
    out = notes.render_claim(COMMENT_ANN)
    cid = notes.claim_id(COMMENT_ANN)
    assert out.split("\n")[0] == \
        f"- (paraphrase) Design is retrospective only [@smith2020, p. 3] ^{cid}"


def test_content_changed(tmp_vault):
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-16")
    assert notes.content_changed(v1, ["aa11"]) is False   # no-op re-import
    assert notes.content_changed(v1, ["aa11", "bb22"]) is True
    assert notes.content_changed(None, ["aa11"]) is True


def test_sha256_file(tmp_path):
    f = tmp_path / "x.pdf"
    f.write_bytes(b"pdfbytes")
    assert len(notes.sha256_file(f)) == 64
```

- [ ] **Part B — Step 2: Run tests to verify the new cases fail**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_notes.py -v`
Expected: new tests FAIL (`NotImplementedError` / missing names); Part A tests still PASS

- [ ] **Part B — Step 3: Replace the stub and add helpers**

```python
# in core/harness_core/notes.py — replace the render_claim stub with:
import hashlib
import unicodedata


def _norm(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def claim_id(annotation: dict) -> str:
    basis = annotation.get("key") or _norm(annotation.get("annotationText", ""))
    return "c-" + hashlib.sha256(basis.encode()).hexdigest()[:8]


def render_claim(annotation: dict) -> str:
    cid = claim_id(annotation)
    cite = f"[@{annotation['citekey']}, p. {annotation['pageLabel']}]" \
        if annotation.get("pageLabel") else f"[@{annotation['citekey']}]"
    text = annotation.get("annotationText") or ""
    if text:
        lines = [f"- (quote) {cite} ^{cid}", f"  > {text}"]
        pre, suf = annotation.get("context_prefix"), annotation.get("context_suffix")
        if pre or suf:
            lines.append(f'  <!-- hk-sel prefix="{(pre or "")[-32:]}" '
                         f'suffix="{(suf or "")[:32]}" -->')
        return "\n".join(lines)
    return f"- (paraphrase) {annotation.get('comment', '')} {cite} ^{cid}"


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_changed(existing_text, attachment_hashes) -> bool:
    if not existing_text:
        return True
    prior = frontmatter.parse(existing_text)[0]
    return prior.get("attachment-sha256") != attachment_hashes
```

- [ ] **Part B — Step 4: Run the complete Task 6 tests**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_notes.py -v`
Expected: all Part A + Part B tests PASS

- [ ] **Part B — Step 5: Commit the complete composite task**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core
git commit -m "feat: literature notes with stable claim anchors and content-hash no-op"
```

______________________________________________________________________

### Task 7: CLI — probe, import-note, staleness

**Files:**

- Create: `core/harness_core/__main__.py`
- Test: `core/tests/test_cli_live.py`

**Interfaces:**

- Consumes: everything above — `ZoteroClient`, `paths.to_local`, `bibliography`, `notes`.

- Produces: `python -m harness_core <command>`:

  - `probe` — prints JSON `{"zotero": …, "betterbibtex": …, "local_writes": bool}`; exit 0, or exit 3 with `{"result": "UNREACHABLE"}` when Zotero is down.
  - `import-note <citekey> --vault <path>` — fetches item (BBT search by citekey), attachments (hashes via resolved paths; unresolvable paths recorded as hash `"unresolved"` and a warning on stderr — never a crash), annotations (with `citekey` injected and prefix/suffix passed through when BBT provides position context), writes/re-renders `literatures/<citekey>.md` honoring `content_changed` (no-op prints `NOOP`), refreshes the bibliography via `write_and_commit`. Exit 0.
  - `staleness --vault <path>` — prints the four-state name; exit 0 on `MATCHED`/`SKIPPED`, 1 on `UNMATCHED`, 3 on `UNREACHABLE`.
  - This CLI is the surface Plan C's hooks and Plan D's skills call; the exit-code contract above is load-bearing.

- [ ] **Step 1: Write the failing test (live — this is the end-to-end deliverable)**

```python
# core/tests/test_cli_live.py
import json
import subprocess
import sys

import pytest


def run_cli(*args):
    return subprocess.run([sys.executable, "-m", "harness_core", *args],
                          capture_output=True, text=True)


@pytest.mark.live
def test_probe():
    proc = run_cli("probe")
    assert proc.returncode == 0
    info = json.loads(proc.stdout)
    assert "betterbibtex" in info and isinstance(info["local_writes"], bool)


@pytest.mark.live
def test_import_note_end_to_end(tmp_vault):
    # pick any real citekey from the live library
    from harness_core.zotero import ZoteroClient
    items = ZoteroClient().export_csl(None)
    citekey = items[0]["id"]

    proc = run_cli("import-note", citekey, "--vault", str(tmp_vault))
    assert proc.returncode == 0, proc.stderr
    note = (tmp_vault / "literatures" / f"{citekey}.md").read_text()
    assert f'citekey: "{citekey}"' in note
    assert "%%hk-managed%%" in note
    assert (tmp_vault / "x" / "bibliography.json").is_file()

    # second import is a no-op
    proc2 = run_cli("import-note", citekey, "--vault", str(tmp_vault))
    assert "NOOP" in proc2.stdout


@pytest.mark.live
def test_staleness_after_import(tmp_vault):
    from harness_core.zotero import ZoteroClient
    citekey = ZoteroClient().export_csl(None)[0]["id"]
    run_cli("import-note", citekey, "--vault", str(tmp_vault))
    proc = run_cli("staleness", "--vault", str(tmp_vault))
    assert proc.stdout.strip() in {"MATCHED", "UNMATCHED"}
    assert proc.returncode in (0, 1)


def test_probe_unreachable(monkeypatch):
    proc = subprocess.run(
        [sys.executable, "-m", "harness_core", "probe", "--base", "http://127.0.0.1:1"],
        capture_output=True, text=True)
    assert proc.returncode == 3
    assert json.loads(proc.stdout)["result"] == "UNREACHABLE"
```

- [ ] **Step 2: Run to verify failure**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_cli_live.py -v`
Expected: `test_probe_unreachable` FAIL (`No module named harness_core.__main__`); live tests SKIP

- [ ] **Step 3: Implement**

```python
# core/harness_core/__main__.py
"""CLI surface consumed by hooks (Plan C) and skills (Plan D)."""
import argparse
import datetime
import json
import sys

from . import Result
from . import bibliography, notes, paths
from .zotero import ZoteroClient, ZoteroError


def cmd_probe(args):
    client = ZoteroClient(base=args.base)
    try:
        info = client.ready()
        info["local_writes"] = client.supports_local_writes()
    except ZoteroError:
        print(json.dumps({"result": Result.UNREACHABLE.value}))
        return 3
    print(json.dumps(info))
    return 0


def cmd_import_note(args):
    client = ZoteroClient(base=args.base)
    vault = args.vault
    matches = [i for i in client.search(args.citekey) if i.get("citekey") == args.citekey]
    if not matches:
        print(f"citekey not found: {args.citekey}", file=sys.stderr)
        return 1
    item = matches[0]
    item["id"] = args.citekey

    hashes, annotations = [], []
    for att in client.attachments(args.citekey):
        try:
            local = paths.to_local(att["path"], vault)
            hashes.append(notes.sha256_file(local))
        except (paths.PathError, OSError) as e:
            print(f"warning: attachment unresolved: {e}", file=sys.stderr)
            hashes.append("unresolved")
        for ann in att.get("annotations") or []:
            ann["citekey"] = args.citekey
            annotations.append(ann)

    # Refresh the bibliography BEFORE any early return (ruling): the §4 commit
    # step runs inside import-source unconditionally — a NOOP note re-import can
    # still coincide with a stale bibliography (other items admitted meanwhile).
    bibliography.write_and_commit(vault, client.export_csl(None))

    path = notes.note_path(vault, args.citekey)
    existing = path.read_text() if path.is_file() else None
    if not notes.content_changed(existing, hashes):
        print("NOOP")
        return 0
    today = datetime.date.today().isoformat()
    path.write_text(notes.render_note(item, hashes, annotations, existing, today))
    print(str(path))
    return 0


def cmd_staleness(args):
    result = bibliography.staleness(args.vault, ZoteroClient(base=args.base))
    print(result.value)
    return {Result.MATCHED: 0, Result.SKIPPED: 0,
            Result.UNMATCHED: 1, Result.UNREACHABLE: 3}[result]


def main(argv=None):
    # --base rides a parents=[] parser so it is accepted before OR after the
    # subcommand (argparse subparsers consume all remaining argv otherwise —
    # empirically verified failure mode).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--base", default="http://localhost:23119")
    p = argparse.ArgumentParser(prog="harness_core", parents=[common])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe", parents=[common])
    imp = sub.add_parser("import-note", parents=[common])
    imp.add_argument("citekey")
    imp.add_argument("--vault", required=True)
    stale = sub.add_parser("staleness", parents=[common])
    stale.add_argument("--vault", required=True)
    args = p.parse_args(argv)
    return {"probe": cmd_probe, "import-note": cmd_import_note,
            "staleness": cmd_staleness}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
```

Note: `--base` is defined via a shared `parents=[common]` parser on the root *and* every subparser, so both `probe --base …` and `--base … probe` parse (the test uses the former).

- [ ] **Step 4: Run offline test, then the live end-to-end**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_cli_live.py -v`
Expected: `test_probe_unreachable` PASS, 3 SKIP

Run: `cd core && source .venv/bin/activate && HARNESS_LIVE=1 python -m pytest tests/test_cli_live.py -v`
Expected: 4 PASS — **this is Plan A's deliverable**: a real literature note generated from your live Zotero into a scratch vault, idempotent on re-import, bibliography committed, staleness answering.

- [ ] **Step 5: Run the full suite, then commit**

Run: `cd core && source .venv/bin/activate && python -m pytest tests -v` — Expected: all PASS (live ones per `HARNESS_LIVE`)

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: harness_core CLI — probe, import-note, staleness"
```

______________________________________________________________________

### Task 8: Merge

- [ ] **Step 1: Full suite green** — `cd core && source .venv/bin/activate && HARNESS_LIVE=1 python -m pytest tests -v`
- [ ] **Step 2: Merge** — use `superpowers:finishing-a-development-branch` to integrate `build/plan-a` into `main` and push.

______________________________________________________________________

## Whole-branch rulings (execution-time)

1. **`register_autoexport` sends `["//", CSL_TRANSLATOR, target_path]`** (BBT-documented personal-library root), with an exact request/response fixture. Still live-unverified until Plan C's vault-setup performs the first real registration — the caveat stands.
2. **NOOP detection is render-first**: compare the complete newly rendered managed projection (frontmatter managed fields + managed region incl. normalized annotations) against the existing note; NOOP only on identity. Rationale: Zotero annotations live in its database — annotation and metadata changes never alter attachment bytes, so hash-keyed NOOP silently skips real changes. Attachment hashes remain recorded for their §5 roles (fixity, ack-scope trigger) — they were never a change detector. Spec §7 clarified accordingly.
3. Ordinary fixes queued without ruling: path-limited bibliography commits, CRLF-preserving note I/O, citekey traversal rejection, malformed-JSON four-state handling.

## Self-Review (completed at authoring)

**Spec coverage (this plan's slice):** §4 bibliography/export-scope/commit-step/staleness → Task 5; §4 path rule → Task 4; §3/§5 note shape, managed regions, day-one `retrieved`, attachment hashes, aliases, anchors, blockquotes, and selectors + §7 content-hash no-op → composite Task 6; §2 feature detection → Task 3; §8 plugin/marketplace manifests → Task 1. Deliberately out (later plans): all §6 checkers and events (B), identifier discovery (B), hooks/CI/scaffold/vault-setup (C), all skills and integrate-at-import (D), `autoexport.add` *invocation at setup time* (C — the client method ships here in Task 3).
**Placeholders:** none — every step carries runnable content. Live-API risk points are exercised where the plan says they are: Task 3's live test now calls `search`, named-translator `item.export`, and top-level export; `register_autoexport` is explicitly live-unverified until Plan C. Two recorded deviations (Global Constraints): selector capture's producer lives in Plan B; `write_and_commit` is the interim bibliography writer until Plan C registers the auto-export.
**Verification history:** three-lens adversarial pass (spec fidelity / Python desk-check in sandbox / zero-context walkthrough against live Zotero) found 2 CRITICAL + 5 IMPORTANT + 5 MINOR defects — all fixed in this revision: `item.search` param shape, `/items/top` endpoint, version-gated write detection (Zotero 9 answers 400, not 501), argparse parents, PEP 668 venv, frontmatter pass-through of unowned fields, byte-exact free region, scalar escaping, cwd discipline.
**Type consistency:** `Result` (T1) consumed by T3/T5/T7; `frontmatter.parse/serialize` (T2) by T6; `ZoteroClient` method names identical across T3/T5/T7; `render_claim`/`claim_id` names are completed within composite T6; CLI exit codes match `staleness` mapping.
