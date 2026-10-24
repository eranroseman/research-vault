# Substrate Components, Plan C: The Compiled Layer, the Text Layer and Agent Shell Writes

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the two machine surfaces detection did not reach — `fulltext/` (#207, the `fulltext/` half of #211) and `wiki/` (#212, with the `seal` verb) — and settle agent shell writes as detection plus a speed bump (#193, #192).

**Architecture:** The text layer gains a self-witness: `fulltext._render` writes `managed-sha256` over the rest of the file, and a new pipeline-only check `text-layer` compares it at publish, where the gitignored folder is visible. The compiled layer gains a tracked record, `system/compiled-pages.json`, holding the hash of every file under `wiki/`; a `compiled-layer` check compares bytes with the record and, locally, with the compile tool's latest complete journal; `seal` moves entries from journal to record and normalises links; a link-only change from a rename reseals itself through Plan A's resolver. The seed carries eight `Edit(...)` deny rules for the guard's roster, and doctor compares them with the roster.

**Tech Stack:** Python 3.12 in `.venv`; pytest with xdist; the compile tool's journal shape (`.vault-meta/transactions/<operation>/journal.json`, `state: complete`, `writes[].path`, `writes[].new_sha256`, read at `32ac5a0`); Claude Code 2.1.x permission rules for the live leg.

**Spec:** `docs/superpowers/specs/2026-10-03-substrate-components-design.md` §5.4, §5.5 (#207, #211's `fulltext/` half), §5.7, §6.2's deny-rules row, §11's `README.md`, `templates/vault/AGENTS.md`, `docs/agents/okf-conformance.md:42` and `skills/synthesis-conventions` amendments. Designs cluster 2(a) and cluster 4 carry the acceptance tests; research Q4–Q7, Q27 the mechanisms. Cites as in Plan A.

**Precondition:** Plans A and B have merged to `main` (`research_vault/links.py`, `fixer.py`, the `capture-monitor` check and the per-commit history re-check exist).

## Global Constraints

Plan A's Global Constraints apply verbatim; branch names are `substrate-c/<task-slug>`. Two more:

- `text-layer` is pipeline-only (deviation 3 of Plan A): it joins `CLOSING_BY_SURFACE["publish"]` and `skills/publish/SKILL.md:33`, never `inbox.CHECK_IDS` nor terminology §4.4's check-ids row (which `tests/test_skill_contracts.py:625` pins to `CHECK_IDS`).
- `compiled-layer` and `seal` are governed names (§7): `compiled-layer` joins `CHECK_IDS`, both closing sets, terminology §4.4 and `skills/publish/SKILL.md:33`; `seal` joins the CLI's dispatch table and the skills that call it.

## Deviations from the spec, settled here

1. **"Sealing also updates the compile tool's recorded `content_sha256`."** §5.4 cites `compile.py:283-286`, which is the source ledger's hash of the *text file*, not a page hash; the tool keeps no persistent page hash — its page preconditions are `expected_hashes` computed per bundle at inspect time (`transaction.py:3329-3429` @ 32ac5a0). There is nothing for `seal` to update; the sentence's intent (a hand edit must surface in the session that made it, not weeks later) is met by the `compiled-layer` check closing the commit (decision 13). Recorded here so no task hunts for a record that does not exist.
2. **Who seals the pages wiki-ingest writes.** The tool's own `transaction apply` writes pages outside research-vault, so no verb of ours sees the write. `capture` seals at the end of every run (§5.4's "capture after compile"), `compile apply` seals the paths the tool reports, `propagate apply` reseals the wiki surfaces it rewrote, and the `capture-source` and `setup-vault` skills run `seal` after wiki-ingest and after adopt. A page compiled and never sealed is MATCHED locally through the journal and UNMATCHED in CI until sealed, which is the spec's own rule.
3. **The deny rules' spelling.** Claude Code resolves a `/`-led path in a permission rule relative to the directory holding `settings.json`'s project, so the eight rules are `Edit(/literature/**)` and so on. §8's live re-run confirms the eight strings; the doctor row derives the same eight from the guard's roster, so one source governs both.

______________________________________________________________________

### Task 1: The text layer's self-witness and stray files under `fulltext/` (#207, #211 half 2, Q5)

**Files:**

- Modify: `research_vault/fulltext.py:63-88` (`_render` adds `managed-sha256`; `validate_text`), `research_vault/structure.py` (`check_text_layer`, `check_tree(vault_root, candidate_name)`), `research_vault/verify.py:53-79,743-760` (`text-layer` closes publish; the two checks get the candidate name), `skills/publish/SKILL.md:33`, `docs/agents/okf-conformance.md:42`
- Test: `tests/test_fulltext.py:21-35`, `tests/test_structure.py`, `tests/test_verify_cli.py`

**Interfaces:**

- Produces: `fulltext.WITNESS = "managed-sha256"`; `fulltext._render` emits `managed-sha256` as the last frontmatter key, the sha256 of the whole render with that one line removed; `fulltext.validate_text(data: bytes, stem: str) -> tuple[Result, str]` (MATCHED, or UNMATCHED with `schema-violation — stale|missing|duplicate|invalid managed-sha256` or `schema-violation — key does not match file name`, or UNREACHABLE `outage — text file is not UTF-8`); `structure.check_text_layer(vault_root) -> list[Outcome]` (check `text-layer`, target `RepoPath(fulltext/<name>)`, `extra={}` — never a note path, claim id or line number, so `_mutate_marker` writes nothing); `structure.check_tree(vault_root, candidate_name="worktree")` — on any other candidate every path under `fulltext/` is a `tree` row.

- Consumes: Plan A's `structure.is_excluded`.

- [ ] **Step 1: Write the failing tests**

In `tests/test_fulltext.py::test_write_renders_deterministic_frontmatter_and_verbatim_body` (`:21-35`), the expected `data` gains `"managed-sha256": fulltext.witness_of(raw)` as its last key (add the helper below), and append:

```python
def test_witness_covers_every_byte_but_its_own_line(tmp_vault):
    response = {"content": "x" * 600, "indexedPages": 1, "totalPages": 1}
    path, _digest = fulltext.write(tmp_vault, "D7EJ9FTG", "E352DFS8", response)
    raw = path.read_bytes()
    assert fulltext.validate_text(raw, "D7EJ9FTG") == (Result.MATCHED, "matched")
    for edit, reason in (
        (raw + b"appended\n", "stale"),
        (raw.replace(b'zotero-item-key: "E352DFS8"', b'zotero-item-key: "E352DFS8"\nextra: "x"'), "stale"),
        (raw.replace(b'type: "fulltext"', b"type: 'fulltext'"), "stale"),
        (raw.replace(b"managed-sha256", b"managed-sha255"), "missing"),
        (raw.replace(b'type: "fulltext"\n', b'type: "fulltext"\nmanaged-sha256: "' + b"0" * 64 + b'"\n'), "duplicate"),
    ):
        result, detail = fulltext.validate_text(edit, "D7EJ9FTG")
        assert (result, detail) == (Result.UNMATCHED, f"schema-violation — {reason} managed-sha256"), edit
    assert fulltext.validate_text(raw, "OTHERKEY") == (Result.UNMATCHED, "schema-violation — key does not match file name")
    assert fulltext.validate_text(b"\xff\xfe", "D7EJ9FTG") == (Result.UNREACHABLE, "outage — text file is not UTF-8")
    assert fulltext.validate_text(b'---\ntype: "fulltext"\n---\nbody\n', "D7EJ9FTG") == (Result.UNMATCHED, "schema-violation — missing managed-sha256")
```

with, at the top of the test module, `from research_vault import Result` and in `fulltext.py` a test-facing `witness_of(raw: bytes) -> str` (the hash the render would carry). Append to `tests/test_structure.py`:

```python
def _text(vault, key="D7EJ9FTG", item="E352DFS8"):
    from research_vault import fulltext

    path, _ = fulltext.write(vault, key, item, {"content": "x" * 600, "indexedPages": 1, "totalPages": 1})
    return path


def test_text_layer_rows_follow_the_acceptance_table(tmp_path):
    """Designs cluster 4 (a): the five edits and their rows; a deleted text gives
    no row, a fresh render none, and no row carries a marker origin."""
    from research_vault import scaffold

    scaffold.scaffold_vault(tmp_path)
    path = _text(tmp_path)
    assert [o for o in structure.check_text_layer(tmp_path) if o.result is not Result.MATCHED] == []
    raw = path.read_bytes()
    path.write_bytes(raw + b"edited\n")
    (row,) = [o for o in structure.check_text_layer(tmp_path) if o.result is Result.UNMATCHED]
    assert (row.check, row.target, row.reason, dict(row.extra)) == (
        "text-layer", "path-bytes:fulltext/D7EJ9FTG.md", "schema-violation — stale managed-sha256", {}
    )
    path.write_text('---\ntype: "fulltext"\nzotero-attachment-key: "D7EJ9FTG"\n---\nstub\n')
    (row,) = [o for o in structure.check_text_layer(tmp_path) if o.result is Result.UNMATCHED]
    assert row.reason == "schema-violation — missing managed-sha256"
    path.write_bytes(raw)
    (tmp_path / "fulltext" / "OTHERKEY.md").write_bytes(raw)
    (row,) = [o for o in structure.check_text_layer(tmp_path) if o.result is Result.UNMATCHED]
    assert (row.target, row.reason) == ("path-bytes:fulltext/OTHERKEY.md", "schema-violation — key does not match file name")
    (tmp_path / "fulltext" / "OTHERKEY.md").unlink()
    path.unlink()
    assert structure.check_text_layer(tmp_path) == [
        Outcome("text-layer", "fulltext", Result.SKIPPED, "no-identifier — no text file to check")
    ]


def test_text_layer_reports_strays_under_fulltext(tmp_path):
    """#211's fulltext/ half: one shape, <attachment key>.md."""
    from research_vault import scaffold

    scaffold.scaffold_vault(tmp_path)
    _text(tmp_path)
    (tmp_path / "fulltext" / "x.pdf").write_bytes(b"%PDF")
    (tmp_path / "fulltext" / "notes.md").write_text('---\ntype: "fulltext"\n---\n')
    (tmp_path / "fulltext" / "sub").mkdir()
    (tmp_path / "fulltext" / ".DS_Store").write_bytes(b"\0")
    rows = [(o.target, o.reason) for o in structure.check_text_layer(tmp_path) if o.result is Result.UNMATCHED]
    assert rows == [
        ("path-bytes:fulltext/notes.md", "schema-violation — fulltext/ holds only <attachment key>.md: fulltext/notes.md"),
        ("path-bytes:fulltext/sub/", "schema-violation — fulltext/ holds only <attachment key>.md: fulltext/sub/"),
        ("path-bytes:fulltext/x.pdf", "schema-violation — fulltext/ holds only <attachment key>.md: fulltext/x.pdf"),
    ]


def test_a_text_file_in_a_committed_candidate_is_a_tree_row(tmp_path):
    """#211: fulltext/ is gitignored; a force-added text on an index or HEAD
    candidate commits licensed text with no finding unless check_tree says so."""
    from research_vault import scaffold

    scaffold.scaffold_vault(tmp_path)
    _text(tmp_path)
    assert [o for o in structure.check_tree(tmp_path, candidate_name="worktree") if "fulltext" in str(o.target)] == []
    rows = [(o.target, o.reason) for o in structure.check_tree(tmp_path, candidate_name="index") if "fulltext" in str(o.target)]
    assert rows == [("path-bytes:fulltext/D7EJ9FTG.md", "schema-violation — fulltext/ is never committed: fulltext/D7EJ9FTG.md")]
```

Append to `tests/test_verify_cli.py`:

```python
def test_text_layer_closes_publish_and_writes_no_marker(net_vault):
    """Cluster 4's [risk]: a closing check's rows reach _mutate_marker; a row
    with no origin writes nothing into the text file."""
    from research_vault import fulltext, inbox, verify

    assert "text-layer" in verify.CLOSING_BY_SURFACE["publish"]
    assert "text-layer" not in verify.CLOSING_BY_SURFACE["commit"]
    assert "text-layer" not in inbox.CHECK_IDS
    path, _ = fulltext.write(net_vault, "ATT00001", "SMITH020", {"content": "x" * 600, "indexedPages": 1, "totalPages": 1})
    path.write_bytes(path.read_bytes() + b"edited\n")
    before = path.read_bytes()
    _report, effective, _hashes, warning = verify.verify_state(net_vault, network=False)
    assert verify.surface_decision("publish", effective, warning)[0] == 1
    assert verify.surface_decision("commit", effective, warning)[0] == 0
    assert path.read_bytes() == before
    finding = next(f for f in inbox.open_entries(net_vault) if f.check == "text-layer")
    inbox.append_ack(net_vault, finding.id, "manual — accepted", "human:eran")
    _report, effective, _hashes, warning = verify.verify_state(net_vault, network=False)
    assert verify.surface_decision("publish", effective, warning)[0] == 0
    path.write_bytes(path.read_bytes() + b"again\n")
    _report, effective, _hashes, warning = verify.verify_state(net_vault, network=False)
    assert verify.surface_decision("publish", effective, warning)[0] == 1


def test_a_force_added_text_file_is_refused_at_commit(net_vault):
    from research_vault import fulltext, verify

    fulltext.write(net_vault, "ATT00001", "SMITH020", {"content": "x" * 600, "indexedPages": 1, "totalPages": 1})
    subprocess.run(["git", "add", "-f", "fulltext/ATT00001.md"], cwd=net_vault, check=True)
    _report, effective, _hashes, warning = verify.verify_state(net_vault, network=False, git_candidate="index")
    decision, blockers = verify.surface_decision("commit", effective, warning)
    assert decision == 1
    assert any(b.startswith("UNMATCHED tree") and "fulltext/ATT00001.md" in b for b in blockers)
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_fulltext.py tests/test_structure.py tests/test_verify_cli.py -q -k "witness or text_layer or force_added or committed_candidate"`
Expected: FAIL — no witness, no `check_text_layer`, `check_tree` takes one argument.

- [ ] **Step 3: `fulltext.py`**

Replace `_render` and append the reader:

```python
WITNESS = "managed-sha256"
_WITNESS_LINE = re.compile(rb'^managed-sha256: "[0-9a-f]{64}"\r?\n', re.MULTILINE)


def _render(attachment_key, item_key, response) -> str:
    fields: list[tuple[str, object]] = [
        ("type", "fulltext"),
        ("zotero-attachment-key", attachment_key),
        ("zotero-item-key", item_key),
    ]
    for pair in (("indexedPages", "totalPages"), ("indexedChars", "totalChars")):
        if pair[0] in response or pair[1] in response:
            values = [response.get(name) for name in pair]
            if not all(isinstance(value, int) for value in values):
                raise ValueError(f"malformed — {pair[0]} pair missing")
            fields.extend(zip(pair, values, strict=True))
    body = response.get("content") or ""
    without = frontmatter.serialize(dict(fields)) + body
    # #207: the self-witness — the hash of the render with its own line absent,
    # emitted as the last frontmatter key. Any byte change afterwards (body,
    # value, added key, requoting) reads as stale.
    digest = hashlib.sha256(without.encode("utf-8")).hexdigest()
    return frontmatter.serialize(dict([*fields, (WITNESS, digest)])) + body


def witness_of(raw: bytes) -> str:
    """The witness `raw` should carry: the hash of its bytes without the one witness line."""
    return hashlib.sha256(_WITNESS_LINE.sub(b"", raw, count=1)).hexdigest()


def validate_text(raw: bytes, stem: str) -> tuple[Result, str]:
    """#207's check side: exactly one well-formed witness line, equal to the
    hash of everything else; the attachment key equal to the file stem."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return Result.UNREACHABLE, "outage — text file is not UTF-8"
    try:
        data, _body = frontmatter.parse(text)
    except frontmatter.FrontmatterError:
        return Result.UNMATCHED, "schema-violation — malformed frontmatter"
    witnesses = [value for key, value in frontmatter._mapping_items(data) if key == WITNESS]
    if not witnesses:
        return Result.UNMATCHED, "schema-violation — missing managed-sha256"
    if len(witnesses) != 1:
        return Result.UNMATCHED, "schema-violation — duplicate managed-sha256"
    witness = witnesses[0]
    if not isinstance(witness, str) or re.fullmatch(r"[0-9a-f]{64}", witness) is None:
        return Result.UNMATCHED, "schema-violation — invalid managed-sha256"
    if witness != witness_of(raw):
        return Result.UNMATCHED, "schema-violation — stale managed-sha256"
    if data.get("zotero-attachment-key") != stem:
        return Result.UNMATCHED, "schema-violation — key does not match file name"
    return Result.MATCHED, "matched"
```

with `import re` and `from . import Result, frontmatter` at the top (`fulltext.py:11` imports only `frontmatter` today; `Result` comes from the package). The `_WITNESS_LINE` regex removes the serialised line `managed-sha256: "<64 hex>"` with its newline; a requoted or moved witness line therefore no longer matches and the hash goes stale, which is the intent. `fulltext.write`'s returned digest stays the hash of the whole file (the note's `fulltext[].sha256`), unchanged in meaning.

- [ ] **Step 4: `structure.check_text_layer` and `check_tree`'s candidate**

Append to `research_vault/structure.py`:

```python
def check_text_layer(vault_root) -> list[Outcome]:
    """#207 and #211: every file under fulltext/ is `<attachment key>.md` carrying a
    valid self-witness. Rows carry no note path, claim id or line number, so verify
    never writes a marker into a text file. A missing text is no row: a fresh clone
    has none."""
    from . import fulltext  # noqa: PLC0415

    vault = Path(vault_root)
    folder = vault / fulltext.FULLTEXT_DIR
    if not folder.is_dir():
        return [Outcome("text-layer", "fulltext", Result.SKIPPED, "no-identifier — no text layer")]
    rows: list[Outcome] = []
    seen = False
    for child in sorted(folder.iterdir()):
        if is_excluded(child, vault):
            continue
        relative = f"{fulltext.FULLTEXT_DIR}/{child.name}"
        if child.is_dir() or child.suffix != ".md" or not fulltext.ITEM_KEY.match(child.stem):
            shown = f"{relative}/" if child.is_dir() else relative
            rows.append(
                Outcome(
                    "text-layer",
                    _repo_path(shown),
                    Result.UNMATCHED,
                    f"schema-violation — fulltext/ holds only <attachment key>.md: {shown}",
                )
            )
            continue
        seen = True
        try:
            raw = child.read_bytes()
        except OSError as error:
            rows.append(Outcome("text-layer", _repo_path(relative), Result.UNREACHABLE, f"outage — {error}"))
            continue
        result, reason = fulltext.validate_text(raw, child.stem)
        if result is not Result.MATCHED:
            rows.append(Outcome("text-layer", _repo_path(relative), result, reason))
    if not rows and not seen:
        return [Outcome("text-layer", "fulltext", Result.SKIPPED, "no-identifier — no text file to check")]
    return rows or [Outcome("text-layer", "fulltext", Result.MATCHED, "matched")]
```

`check_tree(vault_root, candidate_name: str = "worktree")`: after the `literature/` loop, add:

```python
    text_layer = vault / "fulltext"
    if candidate_name != "worktree" and text_layer.is_dir():
        # #211: the layer is gitignored; a path under it on a committed candidate
        # is a force-added text, licensed material with no finding otherwise.
        for path in sorted(text_layer.rglob("*")):
            if path.is_file() and not is_excluded(path, vault):
                relative = path.relative_to(vault).as_posix()
                rows.append(
                    Outcome("tree", _repo_path(relative), Result.UNMATCHED, f"schema-violation — fulltext/ is never committed: {relative}")
                )
```

`research_vault/verify.py:757-759`: `raw.extend(structure.check_tree(vault, candidate_name=snapshots.candidate_name))` and `raw.extend(structure.check_text_layer(vault))`. `CLOSING_BY_SURFACE["publish"]` gains `"text-layer"`. `skills/publish/SKILL.md:33`'s list gains `text-layer`. `docs/agents/okf-conformance.md:42`: the last row's cost cell becomes “Declined — `managed-sha256` on literature notes and on the text layer's files (`fulltext/<key>.md`, #207), and the bibliography byte-comparison, can't be attested consumer-side; they remain tool-only computations”.

- [ ] **Step 5: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS. Tests that hash a text file at run time (`tests/test_capture.py:61`, `tests/test_lifecycle.py:384`) still pass; the one byte pin (`tests/test_fulltext.py:29-35`) was updated in Step 1.

- [ ] **Step 6: Form, commit, branch, close #207 and #211**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat skills/publish/SKILL.md docs/agents/okf-conformance.md
git switch -c substrate-c/text-layer
git commit -m "feat(verify): text-layer — the text file's self-witness and stray files under fulltext/ hold publish; a force-added text is a tree row (#207, #211)" -- research_vault/fulltext.py research_vault/structure.py research_vault/verify.py skills/publish/SKILL.md docs/agents/okf-conformance.md tests/test_fulltext.py tests/test_structure.py tests/test_verify_cli.py
git push -u origin substrate-c/text-layer
```

After the merge:

```bash
gh issue close 207 --comment "Closed by Plan C Task 1: every text file carries managed-sha256 over the rest of its bytes and zotero-attachment-key must equal its stem; the pipeline-only text-layer check holds publish, the Stop gate and plain verify; a deleted text gives no row; capture <key> repairs."
gh issue close 211 --comment "Closed by Plan A Task 9 and Plan C Task 1: a file under literature/ other than <citation key>.md and .gitkeep is a tree row at commit; anything under fulltext/ other than <attachment key>.md is a text-layer row, and any path under fulltext/ on a committed candidate is a tree row. OS litter joined the walker predicate and the seeded gitignore."
```

______________________________________________________________________

### Task 2: The compiled-page record, the `compiled-layer` check and the `seal` verb (#212, Q4, Q27)

**Files:**

- Create: `research_vault/compiled.py`
- Modify: `research_vault/verify.py` (`compiled-layer` in both closing sets; the check joins `_plan_state` and `HISTORY_CHECKS`), `research_vault/inbox.py` (`compiled-layer` in `CHECK_IDS`), `research_vault/__main__.py` (`seal` verb), `research_vault/compile.py:328-374` (`apply` seals the reported paths), `research_vault/propagate.py:307-376` (`apply` reseals the wiki surfaces it rewrote), `research_vault/capture.py` (seals at the end of a run)
- Modify: `docs/agents/terminology.md:137` (`compiled-layer`), `:108-127` (§4.3 commands gain `seal`), `skills/publish/SKILL.md:33`, `skills/capture-source/SKILL.md:74`, `skills/setup-vault/SKILL.md:61-63`, `skills/synthesis-conventions/SKILL.md:12`, `research_vault/templates/vault/AGENTS.md:28,30`
- Test: `tests/test_compiled.py` (new), `tests/test_verify_cli.py`, `tests/test_compile.py`, `tests/test_propagate.py`, `tests/test_capture.py`

**Interfaces:**

- Produces:

  - `compiled.RECORD_PATH = "system/compiled-pages.json"`, `compiled.SCHEMA = "research-vault.compiled-pages.v1"`, `compiled.CHECK = "compiled-layer"`.
  - `compiled.load_record(vault_root) -> dict[str, str]` (path → sha256; `{}` when absent; `RecordError` when unreadable), `compiled.write_record(vault_root, pages: Mapping[str, str])` (canonical JSON, sorted).
  - `compiled.wiki_files(vault_root) -> dict[str, bytes]` — every non-excluded file under `wiki/`.
  - `compiled.journal_hashes(repository_root) -> dict[str, str | None]` — for every path the compile tool's complete journals name, the `new_sha256` of its latest complete write (`None` for a delete), by `created_epoch`.
  - `compiled.seal(vault_root, paths=None, *, repository_root=None) -> list[Outcome]` — the custody rule: an entry may change only when the file's current bytes equal the entry (no-op), or equal the latest complete journal write for that exact path; a sealed `.md` page is link-normalised first (Plan A's `links.normalize`) and the hash recorded is of the normalised bytes; an absent path whose latest journal write is a delete leaves the record. Returns one MATCHED row (`matched — sealed N`) or UNMATCHED rows naming what it could not seal.
  - `compiled.lint_compiled_layer(vault_root, *, repository_root=None) -> list[Outcome]` — the check: every file under `wiki/` against the record; locally, a file equal to the latest complete journal write is MATCHED; a `.md` page differing from the record only in link destinations that now resolve is MATCHED with the note `reseal`; everything else is `drift — <path> differs from the compiled-page record; seal or acknowledge` / `drift — <path> is not sealed: no complete compile wrote these bytes` / `drift — <path> is recorded but absent`.
  - `compiled.only_link_targets_changed(old: str, new: str, index, source) -> bool`.
  - CLI `seal --vault V [PATH ...]`: prints the rows, exit 0/1.

- Consumes: Plan A's `links.find_links`, `links.normalize`, `captured.link_index`, `structure.is_excluded`; Plan B's `verify.HISTORY_CHECKS`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_compiled.py`:

```python
import hashlib
import json
import subprocess
import time

import pytest

from research_vault import Result, compiled, scaffold


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _page(vault, relative, text):
    path = vault / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def _journal(vault, operation, writes, *, state="complete", epoch=None):
    """A complete compile-tool journal naming `writes` ({path: sha256 or None})."""
    folder = vault / ".vault-meta" / "transactions" / operation
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "journal.json").write_text(json.dumps({
        "schema": "claude-obsidian.transaction-journal.v1",
        "operation_id": operation,
        "operation_type": "ingest",
        "state": state,
        "created_epoch": epoch if epoch is not None else time.time(),
        "writes": [{"path": path, "mode": "replace", "new_sha256": sha, "original_sha256": None} for path, sha in writes.items()],
        "applied": list(writes),
    }))


@pytest.fixture
def wiki_vault(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "wiki").mkdir()
    return tmp_path


def test_seal_moves_a_complete_journal_write_into_the_record_and_normalises_links(wiki_vault):
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nSee [[B]].\n")
    _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes()), "wiki/concepts/B.md": _sha((wiki_vault / "wiki" / "concepts" / "B.md").read_bytes())})
    rows = compiled.seal(wiki_vault)
    assert [(o.result, o.reason) for o in rows] == [(Result.MATCHED, "matched — sealed 2")]
    assert page.read_text() == "---\ntype: source\n---\nSee [B](/wiki/concepts/B.md).\n"
    record = compiled.load_record(wiki_vault)
    assert record == {"wiki/sources/A.md": _sha(page.read_bytes()), "wiki/concepts/B.md": _sha((wiki_vault / "wiki" / "concepts" / "B.md").read_bytes())}
    assert compiled.seal(wiki_vault) == [compiled.Outcome(compiled.CHECK, compiled.RECORD_PATH, Result.MATCHED, "matched — sealed 0")]


def test_seal_refuses_bytes_no_complete_compile_wrote(wiki_vault):
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nhand-written\n")
    _journal(wiki_vault, "op0", {"wiki/sources/A.md": "0" * 64}, state="applying")
    rows = compiled.seal(wiki_vault)
    assert [(o.result, o.target, o.reason) for o in rows] == [
        (Result.UNMATCHED, "path-bytes:wiki/sources/A.md", "drift — wiki/sources/A.md is not sealed: no complete compile wrote these bytes")
    ]
    assert compiled.load_record(wiki_vault) == {}
    assert page.read_text().endswith("hand-written\n")


def test_seal_accepts_only_the_latest_complete_write_for_a_path(wiki_vault):
    """Accepting any complete journal would re-seal a File-recovery restore of an older compile."""
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nolder\n")
    older = _sha(page.read_bytes())
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": older}, epoch=1_000)
    _journal(wiki_vault, "op2", {"wiki/sources/A.md": "f" * 64}, epoch=2_000)
    (row,) = compiled.seal(wiki_vault)
    assert row.result is Result.UNMATCHED
    assert compiled.journal_hashes(wiki_vault) == {"wiki/sources/A.md": "f" * 64}


def test_seal_drops_a_recorded_page_the_tool_deleted(wiki_vault):
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())}, epoch=1_000)
    compiled.seal(wiki_vault)
    page.unlink()
    _journal(wiki_vault, "op2", {"wiki/sources/A.md": None}, epoch=2_000)
    (row,) = compiled.seal(wiki_vault)
    assert row.result is Result.MATCHED
    assert compiled.load_record(wiki_vault) == {}


def test_lint_reports_drift_against_the_record_and_accepts_the_local_journal(wiki_vault):
    """Designs cluster 2(a): a hand edit is drift; a fresh compile before seal is
    MATCHED locally; CI, with no .vault-meta, reads only the record."""
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nv1\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())}, epoch=1_000)
    compiled.seal(wiki_vault)
    assert [o.result for o in compiled.lint_compiled_layer(wiki_vault)] == [Result.MATCHED]
    page.write_text("---\ntype: source\n---\nv1 edited by hand\n")
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert (row.check, row.result, row.target, row.reason) == (
        "compiled-layer", Result.UNMATCHED, "path-bytes:wiki/sources/A.md",
        "drift — wiki/sources/A.md differs from the compiled-page record; seal or acknowledge",
    )
    page.write_text("---\ntype: source\n---\nv2\n")
    _journal(wiki_vault, "op2", {"wiki/sources/A.md": _sha(page.read_bytes())}, epoch=2_000)
    assert [o.result for o in compiled.lint_compiled_layer(wiki_vault)] == [Result.MATCHED]
    assert [o.result for o in compiled.lint_compiled_layer(wiki_vault, repository_root=wiki_vault / "nowhere")] == [Result.UNMATCHED]


def test_lint_hashes_bases_canvases_and_attachments_too(wiki_vault):
    """Q27: every file under wiki/, not only pages."""
    base = _page(wiki_vault, "wiki/views/all.base", "views: []\n")
    canvas = _page(wiki_vault, "wiki/canvases/map.canvas", "{}\n")
    image = wiki_vault / "wiki" / "fig.png"
    image.write_bytes(b"\x89PNG")
    _journal(wiki_vault, "op1", {"wiki/views/all.base": _sha(base.read_bytes()), "wiki/canvases/map.canvas": _sha(canvas.read_bytes()), "wiki/fig.png": _sha(image.read_bytes())})
    compiled.seal(wiki_vault)
    base.write_text("views: [{type: table}]\n")
    (row,) = [o for o in compiled.lint_compiled_layer(wiki_vault) if o.result is Result.UNMATCHED]
    assert "wiki/views/all.base" in row.target


def test_lint_reports_a_recorded_page_that_vanished_and_an_unsealed_newcomer(wiki_vault):
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    page.unlink()
    _page(wiki_vault, "wiki/sources/New.md", "---\ntype: source\n---\n")
    rows = sorted((o.target, o.reason) for o in compiled.lint_compiled_layer(wiki_vault) if o.result is Result.UNMATCHED)
    assert rows == [
        ("path-bytes:wiki/sources/A.md", "drift — wiki/sources/A.md is recorded but absent"),
        ("path-bytes:wiki/sources/New.md", "drift — wiki/sources/New.md is not sealed: no complete compile wrote these bytes"),
    ]


def test_a_link_only_change_from_a_rename_reseals_itself(wiki_vault):
    """Decision 13: Obsidian's rename rewrote `[B](/wiki/concepts/B.md)` to
    `[B](/wiki/concepts/C.md)`; the only differences are link destinations
    that resolve, so the page is MATCHED and seal updates the entry."""
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nSee [B](/wiki/concepts/B.md) and [B](/wiki/concepts/B.md#h).\n")
    target = _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes()), "wiki/concepts/B.md": _sha(target.read_bytes())})
    compiled.seal(wiki_vault)
    # The record and the page are committed together: `_recorded_text` reads
    # the sealed bytes back from HEAD.
    subprocess.run(["git", "add", "-A"], cwd=wiki_vault, check=True)
    subprocess.run(["git", "commit", "-qm", "sealed", "--no-verify"], cwd=wiki_vault, check=True)
    target.rename(wiki_vault / "wiki" / "concepts" / "C.md")
    page.write_text("---\ntype: source\n---\nSee [B](/wiki/concepts/C.md) and [B](/wiki/concepts/C.md#h).\n")
    rows = compiled.lint_compiled_layer(wiki_vault)
    assert [(o.result, o.target, o.reason) for o in rows if "A.md" in o.target] == [
        (Result.MATCHED, "path-bytes:wiki/sources/A.md", "matched — link targets follow a rename; reseal")
    ]
    assert any(o.result is Result.UNMATCHED and "B.md" in o.target for o in rows)  # the renamed-away path is recorded but absent
    assert any(o.result is Result.UNMATCHED and "C.md" in o.target for o in rows)  # and the new one is not sealed
    (sealed,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert sealed.result is Result.MATCHED
    assert compiled.load_record(wiki_vault)["wiki/sources/A.md"] == _sha(page.read_bytes())


def test_a_content_change_beside_a_link_change_is_still_drift(wiki_vault):
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nSee [B](/wiki/concepts/B.md). Old prose.\n")
    _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _page(wiki_vault, "wiki/concepts/C.md", "---\ntype: concept\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    page.write_text("---\ntype: source\n---\nSee [B](/wiki/concepts/C.md). New prose.\n")
    rows = [o for o in compiled.lint_compiled_layer(wiki_vault) if "A.md" in o.target]
    assert rows[0].result is Result.UNMATCHED


def test_an_unreadable_record_is_one_row_not_a_traceback(wiki_vault):
    (wiki_vault / "system" / "compiled-pages.json").write_text("{not json")
    _page(wiki_vault, "wiki/sources/A.md", "x\n")
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert (row.result, row.target) == (Result.UNMATCHED, "path-bytes:system/compiled-pages.json")
    assert row.reason.startswith("schema-violation — compiled-page record unreadable")


def test_no_wiki_is_skipped(tmp_vault):
    assert compiled.lint_compiled_layer(tmp_vault) == [
        compiled.Outcome(compiled.CHECK, "wiki", Result.SKIPPED, "no-identifier — no compiled layer")
    ]
```

Append to `tests/test_verify_cli.py`:

```python
def test_compiled_layer_closes_commit_and_publish_and_the_seal_verb_runs(net_vault, capsys):
    import research_vault.__main__ as cli
    from research_vault import compiled, inbox, verify

    assert "compiled-layer" in inbox.CHECK_IDS
    assert "compiled-layer" in verify.CLOSING_BY_SURFACE["commit"]
    assert "compiled-layer" in verify.CLOSING_BY_SURFACE["publish"]
    assert "compiled-layer" in verify.HISTORY_CHECKS
    page = net_vault / "wiki" / "concepts" / "mortality-trends.md"
    page.write_text(page.read_text() + "\nA hand-written line.\n")
    _report, effective, _hashes, warning = verify.verify_state(net_vault, network=False)
    assert verify.surface_decision("commit", effective, warning)[0] == 1
    assert cli.main(["seal", "--vault", str(net_vault)]) == 1
    assert "not sealed" in capsys.readouterr().out
```

In `tests/test_compile.py`, add a test that `compile.apply` seals the reported `wiki/` paths when a complete journal names them (use `_fake_tool(..., apply_changed_paths=("wiki/meta/ledgers/source-ledger.json",))` and write the journal with `_journal` imported from `tests/test_compiled.py`), asserting `compiled.load_record(vault)` holds the ledger path afterwards. In `tests/test_propagate.py`, add a test that `apply` reseals `wiki/sources/A.md` after rewriting it (seed the record and journal for the page first; after apply the record's hash equals the rewritten bytes). In `tests/test_capture.py`, add a test that `capture` calls `compiled.seal` once per run (monkeypatch `capture.compiled.seal` to record the call and return `[]`).

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_compiled.py tests/test_verify_cli.py -q -k "seal or compiled"`
Expected: FAIL — no `research_vault.compiled`.

- [ ] **Step 3: `research_vault/compiled.py`**

```python
"""The compiled-page record and the `seal` verb (spec §5.4, #212).

`system/compiled-pages.json` holds the sha256 of every file under `wiki/`.
The custody rule: an entry may change only when the file's current bytes
equal the entry, or equal the *latest* complete compile-journal write for
that exact path — so a File-recovery restore of an older compile is never
re-sealed. Seal normalises a page's links (spec §5.2) and records the hash of
the normalised bytes. The `compiled-layer` check compares every file with
its entry; locally it also accepts the latest complete journal write, so a
fresh compile files no row before seal; CI, with no `.vault-meta/`, reads
only the record.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterable, Mapping
from pathlib import Path

from . import captured, frontmatter, links, structure
from .outcome import Outcome, Result
from .pathcodec import RepoPath

RECORD_PATH = "system/compiled-pages.json"
SCHEMA = "research-vault.compiled-pages.v1"
CHECK = "compiled-layer"
_JOURNALS = ".vault-meta/transactions"


class RecordError(ValueError):
    """The record exists but is not this module's document."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_record(vault_root) -> dict[str, str]:
    path = Path(vault_root) / RECORD_PATH
    if not path.is_file():
        return {}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise RecordError(f"compiled-page record unreadable: {error}") from error
    pages = document.get("pages") if isinstance(document, dict) else None
    if document.get("schema") != SCHEMA or not isinstance(pages, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in pages.items()
    ):
        raise RecordError("compiled-page record unreadable: not a research-vault.compiled-pages.v1 document")
    return dict(pages)


def write_record(vault_root, pages: Mapping[str, str]) -> Path:
    path = Path(vault_root) / RECORD_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {"schema": SCHEMA, "pages": dict(sorted(pages.items()))}
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def wiki_files(vault_root) -> dict[str, bytes]:
    vault = Path(vault_root)
    wiki = vault / "wiki"
    if not wiki.is_dir():
        return {}
    files: dict[str, bytes] = {}
    for path in sorted(wiki.rglob("*")):
        if path.is_file() and not path.is_symlink() and not structure.is_excluded(path, vault):
            files[path.relative_to(vault).as_posix()] = path.read_bytes()
    return files


def journal_hashes(repository_root) -> dict[str, str | None]:
    """Path → `new_sha256` of its latest complete compile-tool write (None: a delete).

    Journals the tool left in `prepared`, `applying` or `rolled-back` state are
    not writes that happened; a missing journal directory means no compile ran
    here (a CI checkout, a fresh clone)."""
    folder = Path(repository_root) / _JOURNALS
    if not folder.is_dir():
        return {}
    latest: dict[str, tuple[float, str | None]] = {}
    for journal_path in sorted(folder.glob("*/journal.json")):
        try:
            journal = json.loads(journal_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            continue
        if not isinstance(journal, dict) or journal.get("state") != "complete":
            continue
        epoch = journal.get("created_epoch")
        stamp = float(epoch) if isinstance(epoch, (int, float)) else 0.0
        for write in journal.get("writes", []):
            if not isinstance(write, dict) or not isinstance(write.get("path"), str):
                continue
            new = write.get("new_sha256")
            if new is not None and not isinstance(new, str):
                continue
            if write["path"] not in latest or stamp >= latest[write["path"]][0]:
                latest[write["path"]] = (stamp, new)
    return {path: new for path, (_stamp, new) in latest.items()}


def only_link_targets_changed(old: str, new: str, index: links.Index, source: str) -> bool:
    """Decision 13's definite test: the two texts differ only in link
    destinations, and every destination in `new` resolves to one file."""
    old_links, new_links = links.find_links(old), links.find_links(new)
    if len(old_links) != len(new_links) or not old_links:
        return False
    cursor_old = cursor_new = 0
    for a, b in zip(old_links, new_links, strict=True):
        if old[cursor_old : a.start] != new[cursor_new : b.start]:
            return False
        if (a.kind, a.embed, a.alias, a.subpath) != (b.kind, b.embed, b.alias, b.subpath):
            return False
        if a.target != b.target and len(index.resolve(b.target, source=source)) != 1:
            return False
        cursor_old, cursor_new = a.end, b.end
    return old[cursor_old:] == new[cursor_new:]


def _row(result: Result, relative: str, reason: str) -> Outcome:
    return Outcome(CHECK, RepoPath(os.fsencode(relative)), result, reason)


def lint_compiled_layer(vault_root, *, repository_root=None) -> list[Outcome]:
    vault = Path(vault_root)
    files = wiki_files(vault)
    if not (vault / "wiki").is_dir():
        return [Outcome(CHECK, "wiki", Result.SKIPPED, "no-identifier — no compiled layer")]
    try:
        record = load_record(vault)
    except RecordError as error:
        return [_row(Result.UNMATCHED, RECORD_PATH, f"schema-violation — {error}")]
    repository = Path(repository_root) if repository_root is not None else vault
    journal = journal_hashes(repository)
    rows: list[Outcome] = []
    index: links.Index | None = None
    for relative, data in files.items():
        current = _sha(data)
        recorded = record.get(relative)
        if recorded == current or journal.get(relative) == current:
            continue
        if recorded is not None and relative.endswith(".md"):
            if index is None:
                index = captured.link_index(vault)
            old = _recorded_text(repository, relative, recorded)
            if old is not None and only_link_targets_changed(old, data.decode("utf-8", errors="surrogateescape"), index, relative):
                rows.append(_row(Result.MATCHED, relative, "matched — link targets follow a rename; reseal"))
                continue
        if recorded is None:
            rows.append(_row(Result.UNMATCHED, relative, f"drift — {relative} is not sealed: no complete compile wrote these bytes"))
        else:
            rows.append(_row(Result.UNMATCHED, relative, f"drift — {relative} differs from the compiled-page record; seal or acknowledge"))
    for relative in sorted(set(record) - set(files)):
        if journal.get(relative, "") is None:
            continue  # the tool deleted it; seal drops the entry
        rows.append(_row(Result.UNMATCHED, relative, f"drift — {relative} is recorded but absent"))
    return rows or [Outcome(CHECK, RECORD_PATH, Result.MATCHED, "matched")]


def _recorded_text(repository: Path, relative: str, recorded: str) -> str | None:
    """The bytes the record describes, read from the repository's HEAD (the
    record and the page were committed together), or None when no revision
    holds them. `repository`, never the materialised candidate verify plans
    in: that copy has no `.git`."""
    from . import gitstate  # noqa: PLC0415

    for revision in ("HEAD",):
        data = gitstate.blob_bytes(repository, revision, relative)
        if data is not None and _sha(data) == recorded:
            return data.decode("utf-8", errors="surrogateescape")
    return None


def seal(vault_root, paths: Iterable[str] | None = None, *, repository_root=None) -> list[Outcome]:
    """Move entries from the latest complete journal into the record, normalising
    a page's links first; drop the entry of a page the tool deleted; refuse bytes
    no complete compile wrote. Returns one MATCHED summary or the refusals."""
    vault = Path(vault_root)
    try:
        record = load_record(vault)
    except RecordError as error:
        return [_row(Result.UNMATCHED, RECORD_PATH, f"schema-violation — {error}")]
    repository = Path(repository_root) if repository_root is not None else vault
    journal = journal_hashes(repository)
    files = wiki_files(vault)
    wanted = set(files) | set(record) if paths is None else {p.strip("/") for p in paths}
    refusals: list[Outcome] = []
    sealed = 0
    index: links.Index | None = None
    for relative in sorted(wanted):
        if relative not in files:
            if relative in record and journal.get(relative, "") is None:
                del record[relative]
                sealed += 1
            elif relative in record:
                refusals.append(_row(Result.UNMATCHED, relative, f"drift — {relative} is recorded but absent"))
            continue
        current = _sha(files[relative])
        if record.get(relative) == current:
            continue
        follows_rename = False
        if record.get(relative) is not None and relative.endswith(".md"):
            if index is None:
                index = captured.link_index(vault)
            old = _recorded_text(repository, relative, record[relative])
            follows_rename = old is not None and only_link_targets_changed(old, files[relative].decode("utf-8", errors="surrogateescape"), index, relative)
        if journal.get(relative) != current and not follows_rename:
            refusals.append(_row(Result.UNMATCHED, relative, f"drift — {relative} is not sealed: no complete compile wrote these bytes"))
            continue
        if relative.endswith(".md"):
            if index is None:
                index = captured.link_index(vault)
            text = files[relative].decode("utf-8", errors="surrogateescape")
            try:
                # §5.6: the OKF reader runs at seal too, so a compile-tool page
                # with an unquoted `title: A: B` fails inside the session that
                # can redo it, not weeks later at commit.
                frontmatter.read_okf(text)
            except frontmatter.FrontmatterError as error:
                refusals.append(_row(Result.UNMATCHED, relative, f"schema-violation — {relative}: frontmatter is not valid YAML ({error})"))
                continue
            normalised, _problems = links.normalize(text, index, source=relative)
            if normalised != text:
                (vault / relative).write_text(normalised, encoding="utf-8", newline="")
                files[relative] = normalised.encode("utf-8", errors="surrogateescape")
                current = _sha(files[relative])
        record[relative] = current
        sealed += 1
    if sealed:
        write_record(vault, record)
    return refusals or [Outcome(CHECK, RECORD_PATH, Result.MATCHED, f"matched — sealed {sealed}")]
```

`Outcome` is re-exported from the module (`from .outcome import Outcome`) so the tests' `compiled.Outcome(...)` reads. Run `mypy research_vault/compiled.py`.

- [ ] **Step 4: Registries, verify, the verb, the callers**

`inbox.CHECK_IDS` gains `"compiled-layer"` (comment: `# The compiled-page record (spec §5.4, #212).`); `verify.CLOSING_BY_SURFACE` both sets gain it; `verify.HISTORY_CHECKS`/`_history_lints` gain `compiled.lint_compiled_layer` run against the commit's materialised tree — because the lint reads files, `_history_outcomes` materialises each commit into a temporary directory with `gitstate.materialize_snapshot` before calling it (the other history lints take snapshots; this one takes a path, so the re-check's per-commit cost grows: measure in Step 7). `_plan_state` adds `raw.extend(compiled.lint_compiled_layer(vault, repository_root=repository))`. `docs/agents/terminology.md:137` gains `` `compiled-layer` ``; §4.3's command list (`:108-127`) gains `` `seal` `` with the others; `skills/publish/SKILL.md:33` gains `` `compiled-layer` ``.

`research_vault/__main__.py`:

```python
def cmd_seal(args):
    """Seal compiled pages (spec §5.4): journal → record, links normalised."""
    try:
        outcomes = compiled.seal(args.vault, args.paths or None)
    except _NAMED_FAILURES as error:
        print(f"seal unavailable: {error}", file=sys.stderr)
        return 2
    return _print_and_hold(args.vault, outcomes, compiled.CHECK)
```

with `seal_cmd = sub.add_parser("seal", parents=[common]); seal_cmd.add_argument("paths", nargs="*"); seal_cmd.add_argument("--vault", required=True)` and `"seal": cmd_seal` in the dispatch table. `research_vault/compile.py::apply`, on exit 0, seals the reported `changed` paths that start with `wiki/` (`compiled.seal(vault, [p for p in changed if p.startswith("wiki/")])`) and appends `; sealed N` to the reason, or `; seal refused: <reason>` when `seal` returned refusals. `research_vault/propagate.py::apply`, after `rewrite_surfaces`, calls `compiled.seal(vault, [p for p in changed if p.startswith("wiki/")])` and reports a refusal as an extra UNMATCHED row. `research_vault/capture.py::capture`, before the CSL update, calls `compiled.seal(vault)` and appends a row on `compiled.RECORD_PATH` only when the seal did something: `MATCHED matched — sealed N` for `N > 0`, or one UNMATCHED row whose reason folds the refusals (`drift — …; …`). A run that sealed nothing and refused nothing appends no row, so every existing capture test's outcome list is unchanged.

Skills: `skills/capture-source/SKILL.md:74` gains, after the wiki-ingest and wiki-lint sentences: “Then `python3 -m research_vault seal --vault PATH`: it records the hash of every page the tool wrote and normalises their links; a page left unsealed is reported by `compiled-layer` and holds the commit until sealed or acknowledged.” `skills/setup-vault/SKILL.md:61-63`: after the adopt step, “Then `python3 -m research_vault seal --vault PATH`, so the tool's own files under `wiki/` enter the compiled-page record.” `skills/synthesis-conventions/SKILL.md:12`: append “Every file under `wiki/` is hashed in `system/compiled-pages.json`; a hand edit holds the commit until `seal` (which accepts only bytes the tool wrote) or an acknowledgement.” `research_vault/templates/vault/AGENTS.md:30`: append “A hand edit under `wiki/` is reported by the compiled-page record (`compiled-layer`) and holds the commit.” (the byte pin in `tests/test_templates.py:123-170` changes with it).

- [ ] **Step 5: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS once every fixture that writes under `wiki/` and then reaches `verify_state` or a disposition also seals: `tests/conftest.py::_populate_fixture_vault` (`wiki/concepts/mortality-trends.md`) and `tests/test_publish.py::_build_vault` (`wiki/index.md`, so `green_vault` stays green) each write `compiled.write_record(root, {<path>: sha256 of its bytes})` before their commit; grep `tests/` for every other helper writing a `wiki/` path (`rg '"wiki" /|wiki/' tests/`) and seal there too. Tests that edit a sealed page expect the row. `compile.apply`'s reason gains `; sealed N` only when `N > 0` and `; seal refused: …` only when the seal refused something: `tests/test_compile.py`'s fake tool reports `wiki/meta/ledgers/source-ledger.json` without writing it, so `seal` finds no file and the reason is unchanged; a test that does write the ledger file must also write a complete journal naming it (`tests/test_compiled.py::_journal`) or expect the refusal suffix.

- [ ] **Step 6: Live check owed (§8): a Bases column resize**

Attended, on the scratch Obsidian vault with the compile tool adopted: seal a `.base` the tool wrote, resize a column in Obsidian, run `verify --offline --surface commit`. Record whether the `.base` file changed (a `compiled-layer` row) and the date; if it did, that resize costs an acknowledgement, which decision 13 accepts.

- [ ] **Step 7: Form, commit, branch, close #212**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat docs/agents/terminology.md skills/publish/SKILL.md skills/capture-source/SKILL.md skills/setup-vault/SKILL.md skills/synthesis-conventions/SKILL.md research_vault/templates/vault/AGENTS.md
git switch -c substrate-c/compiled-layer
git commit -m "feat(verify): the compiled-page record — compiled-layer compares every wiki/ file with system/compiled-pages.json; seal moves journal to record and normalises links; a rename's link change reseals itself (#212)" -- research_vault/compiled.py research_vault/verify.py research_vault/inbox.py research_vault/__main__.py research_vault/compile.py research_vault/propagate.py research_vault/capture.py docs/agents/terminology.md skills/publish/SKILL.md skills/capture-source/SKILL.md skills/setup-vault/SKILL.md skills/synthesis-conventions/SKILL.md research_vault/templates/vault/AGENTS.md tests/test_compiled.py tests/test_verify_cli.py tests/test_compile.py tests/test_propagate.py tests/test_capture.py tests/conftest.py tests/test_templates.py
git push -u origin substrate-c/compiled-layer
```

After the merge: `gh issue close 212 --comment "Closed by Plan C Task 2: system/compiled-pages.json holds the hash of every file under wiki/; compiled-layer closes commit and publish; seal accepts only the latest complete compile-journal write and normalises links; a link-only change from a rename reseals itself; the record travels with the vault so CI reads it."`

______________________________________________________________________

### Task 3: Agent shell writes — the seeded deny rules, the `deny-rules` row, the prose (#193, #192, §5.7, Q6)

**Files:**

- Create: `research_vault/templates/vault/claude/settings.json`
- Modify: `research_vault/scaffold.py:57-71` (first-component rename), `research_vault/doctor.py` (`_deny_rules_probe`), `research_vault/__main__.py` (`DOCTOR_WARN_ONLY`), `hooks/pretooluse_guard.py` (unchanged; its roster becomes the one source), `README.md:7`, `research_vault/templates/vault/AGENTS.md:7,28`, `skills/synthesis-conventions/SKILL.md:12`, `docs/agents/terminology.md:139`
- Test: `tests/test_templates.py`, `tests/test_scaffold.py:20-38`, `tests/test_doctor.py`, `tests/test_hooks.py:812-820` (stays) plus one new pin, `tests/test_config_validity.py:48-54`

**Interfaces:**

- Produces: `templates/vault/claude/settings.json` → `.claude/settings.json` in a scaffolded vault, `{"permissions": {"deny": [eight Edit rules]}}`; `scaffold._DOTLESS_TEMPLATE_RENAMES` maps the first path component `claude` → `.claude`; `doctor._deny_rules_probe(vault) -> Probe` (`deny-rules`: MATCHED when the file's deny list equals the roster's eight rules; UNMATCHED naming the missing or extra rules; SKIPPED when the file is absent — scaffold's `_copy_if_absent` skipped it); `doctor.expected_deny_rules() -> list[str]` derived from the guard's three constants.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_templates.py` (add `"vault/claude/settings.json"` to `EXPECTED_PATHS`):

```python
def test_seeded_deny_rules_equal_the_guards_roster():
    """§5.7: the eight Edit(...) deny rules are the roster, spelled the way
    Claude Code resolves a /-led project path. One source: the guard."""
    import json

    guard = _guard_constants()
    expected = sorted(
        [f"Edit(/{name}/**)" for name in guard.MACHINE_SURFACE_DIR_NAMES]
        + [f"Edit(/{prefix.as_posix()}/**)" for prefix in guard.MACHINE_SURFACE_PREFIXES]
        + [f"Edit(/{path.as_posix()})" for path in guard.MACHINE_SURFACE_FILES]
    )
    assert len(expected) == 8
    settings = json.loads(asset("vault/claude/settings.json").read_text())
    assert settings == {"permissions": {"deny": expected}}
```

In `tests/test_scaffold.py:20-38`, `EXPECTED_CREATED` gains `".claude/settings.json"` (first, sorted); in `tests/test_config_validity.py:48-54`, `JSON_MANIFESTS` gains `"research_vault/templates/vault/claude/settings.json"`. Append to `tests/test_doctor.py` (adding `"deny-rules"` to `PROBE_NAMES` after `"pyyaml"` and to `WARN_ONLY`; `tests/test_okf.py:80-94` likewise):

```python
def test_deny_rules_row_compares_the_vault_settings_with_the_roster(tmp_vault):
    import json

    assert doctor._deny_rules_probe(tmp_vault) == doctor.Probe("deny-rules", Result.SKIPPED, ".claude/settings.json absent — scaffold seeds it")
    settings = tmp_vault / ".claude" / "settings.json"
    settings.parent.mkdir()
    settings.write_text(json.dumps({"permissions": {"deny": doctor.expected_deny_rules()}}))
    probe = doctor._deny_rules_probe(tmp_vault)
    assert probe.result is Result.MATCHED
    assert probe.reason == "8 Edit deny rules equal the guard's roster"
    rules = doctor.expected_deny_rules()[:-1] + ["Edit(/daily/**)"]
    settings.write_text(json.dumps({"permissions": {"deny": rules}}))
    probe = doctor._deny_rules_probe(tmp_vault)
    assert probe.result is Result.UNMATCHED
    assert "missing Edit(/wiki/**)" in probe.reason or "missing" in probe.reason
    assert "extra Edit(/daily/**)" in probe.reason
    settings.write_text("{not json")
    assert doctor._deny_rules_probe(tmp_vault).result is Result.UNMATCHED
```

Append to `tests/test_hooks.py`, beside `:812-820`:

```python
def test_what_detection_covers_and_what_still_passes_is_pinned(fixture_vault):
    """§5.7: detection is the boundary. A hand edit to a literature note's body,
    a stray PDF under literature/, a hand edit to a compiled page and a hand
    edit to a text file are all caught; an in-format append to log/ and to the
    review queue still pass. Closing one of those gaps flips this test on
    purpose."""
    from research_vault import compiled, verify

    def decision(surface="commit"):
        _report, effective, _hashes, warning = verify.verify_state(fixture_vault, network=False)
        return verify.surface_decision(surface, effective, warning)[0]

    from research_vault import okf

    assert decision() == 0
    day = fixture_vault / "log" / "2026-08-16.md"
    day.write_text(day.read_text() + "- 10:00 research_vault/0.1.0 — a shell append in the writer's format\n")
    assert decision() == 1  # #210: root log.md no longer equals its render
    okf.regenerate_log(fixture_vault)
    assert decision() == 0  # the append rides through once log.md is regenerated with it
    queue = fixture_vault / "inbox" / "review-queue.md"
    queue.write_text(queue.read_text() + "- id: x check: capture target: y result: UNMATCHED date: 2026-08-16 actor: human:eran reason: manual — appended\n")
    assert decision() == 0  # the gaps that remain: a log/ append with its log.md, a queue append
    page = fixture_vault / "wiki" / "concepts" / "mortality-trends.md"
    page.write_text(page.read_text() + "shell edit\n")
    assert decision() == 1  # compiled-layer (Plan C Task 2)
```

Adjust the queue line to the exact field grammar `inbox._FIELD` accepts (read `appendlog.py:17-28` and `inbox._serialize`); if a hand-typed line is rejected by the reader, replace it with an `inbox.append_entry` call, which is the same append.

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_templates.py tests/test_scaffold.py tests/test_doctor.py tests/test_okf.py tests/test_hooks.py tests/test_config_validity.py -q -k "deny or EXPECTED or thirteen or probes or pinned or manifest"`
Expected: FAIL — no settings template, no probe.

- [ ] **Step 3: The seed and the rename**

Create `research_vault/templates/vault/claude/settings.json` (canonical `json.dumps(indent=2)` form, trailing newline):

```json
{
  "permissions": {
    "deny": [
      "Edit(/fulltext/**)",
      "Edit(/inbox/review-queue.md)",
      "Edit(/literature/**)",
      "Edit(/log.md)",
      "Edit(/log/**)",
      "Edit(/system/bibliography.json)",
      "Edit(/system/propagations/**)",
      "Edit(/wiki/**)"
    ]
  }
}
```

`research_vault/scaffold.py:57-71`:

```python
# Dotfiles and dot-directories ship dotless: setuptools' package-data glob
# skips any component starting with a dot (measured 2026-10-04, research Q11),
# so a template path's first component is renamed on write.
_DOTLESS_TEMPLATE_RENAMES = {
    "gitignore": ".gitignore",
    "prettierignore": ".prettierignore",
    "markdownlintignore": ".markdownlintignore",
    "editorconfig": ".editorconfig",
    "claude": ".claude",
}


def _vault_template_paths(templates):
    source_root = templates.joinpath("vault")
    for relative, source in _template_files(source_root):
        first, _sep, rest = relative.partition("/")
        renamed = _DOTLESS_TEMPLATE_RENAMES.get(first, first)
        yield (f"{renamed}/{rest}" if rest else renamed), source
```

`_owned_paths` derives from `_vault_template_paths`, so `.claude/settings.json` is owned and preflighted; `_copy_if_absent` leaves an existing `.claude/settings.json` alone, which is what the doctor row is for.

- [ ] **Step 4: The doctor row**

`research_vault/doctor.py`:

```python
# The guard's roster, repeated here only for a pip install that has no hooks/
# beside the package; `tests/test_templates.py` pins this copy against the
# guard's constants so the two cannot drift.
_ROSTER_DIR_NAMES = ("literature", "log", "wiki", "fulltext")
_ROSTER_PREFIXES = ("system/propagations",)
_ROSTER_FILES = ("log.md", "inbox/review-queue.md", "system/bibliography.json")


def expected_deny_rules() -> list[str]:
    """The guard's roster as Claude Code deny rules (spec §5.7): one source — the
    guard file when it is beside the package, the pinned copy otherwise."""
    import importlib.util  # noqa: PLC0415

    guard_path = Path(__file__).resolve().parents[1] / "hooks" / "pretooluse_guard.py"
    dir_names, prefixes, files = _ROSTER_DIR_NAMES, _ROSTER_PREFIXES, _ROSTER_FILES
    if guard_path.is_file():
        spec = importlib.util.spec_from_file_location("pretooluse_guard", guard_path)
        guard = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(guard)
        dir_names = tuple(guard.MACHINE_SURFACE_DIR_NAMES)
        prefixes = tuple(p.as_posix() for p in guard.MACHINE_SURFACE_PREFIXES)
        files = tuple(p.as_posix() for p in guard.MACHINE_SURFACE_FILES)
    return sorted(
        [f"Edit(/{name}/**)" for name in dir_names]
        + [f"Edit(/{prefix}/**)" for prefix in prefixes]
        + [f"Edit(/{path})" for path in files]
    )


def _deny_rules_probe(vault: Path) -> Probe:
    settings = vault / ".claude" / "settings.json"
    if not settings.is_file():
        return Probe("deny-rules", Result.SKIPPED, ".claude/settings.json absent — scaffold seeds it")
    try:
        document = json.loads(settings.read_text(encoding="utf-8"))
        deny = document["permissions"]["deny"]
        if not isinstance(deny, list):
            raise ValueError("permissions.deny is not a list")
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
        return Probe("deny-rules", Result.UNMATCHED, f".claude/settings.json unreadable: {error}")
    expected = expected_deny_rules()
    present = {rule for rule in deny if isinstance(rule, str) and rule.startswith("Edit(")}
    missing = sorted(set(expected) - present)
    extra = sorted(present - set(expected))
    if not missing and not extra:
        return Probe("deny-rules", Result.MATCHED, f"{len(expected)} Edit deny rules equal the guard's roster")
    parts = [f"missing {rule}" for rule in missing] + [f"extra {rule}" for rule in extra]
    return Probe("deny-rules", Result.UNMATCHED, "; ".join(parts))
```

The guard file travels with the plugin, not the wheel: a pip install has no `hooks/` beside the package, so the three roster constants are repeated in `doctor.py` and `tests/test_templates.py` pins that copy against the guard's constants (`_guard_constants()`), so the two cannot drift. `templates/vault/AGENTS.md:7` (the roster sentence) keeps its wording: its roster is already derived from the guard by `test_agents_template_preamble_names_every_guarded_surface_but_wiki`, which is what §11's `:7` asks for. Append `_deny_rules_probe(vault),` to `doctor()`'s list after `_pyyaml_probe()`, add `"deny-rules"` to `DOCTOR_WARN_ONLY`, and to `docs/agents/terminology.md:139`.

- [ ] **Step 5: The prose, stated exactly (#192, §5.7)**

`README.md:7`: replace “`literature/`, `fulltext/`, `wiki/`, `log/`, `system/`, the review queue” with “`literature/`, `fulltext/`, `wiki/`, `log/`, root `log.md`, `inbox/review-queue.md`, `system/bibliography.json` and `system/propagations/` (the rest of `system/` is hand-edited)” and append the sentence “A scaffolded vault's `.claude/settings.json` denies the common shell forms of a write to those paths — redirects, `tee`, `sed -i`, `cp`, `mv`, `touch`, `rm` — in a session started at the vault root; interpreters, scripts and git restores are caught only where verification detects the change (every change to what the CLI owns is).”

`research_vault/templates/vault/AGENTS.md:28`: replace `Machine surfaces are owner-written: hand or tool edits are regenerated away or raise a finding.` with:

```markdown
Machine surfaces are owner-written, and every change to them is detected: a hand or shell edit to `literature/`, `wiki/`, root `log.md`, `inbox/review-queue.md`, `system/bibliography.json` or `system/propagations/` raises a finding at commit, and an edit to `fulltext/` at publish. The seeded `.claude/settings.json` refuses the common shell forms of such a write (redirects, `tee`, `sed -i`, `cp`, `mv`, `touch`, `rm`) in a session started at the vault root; an interpreter one-liner, a script or a git restore is caught by detection, not refused. What detection does not reach: an in-format append to `log/` committed together with a regenerated `log.md`, an append to the review queue, and the non-capture keys a literature note carries forward.
```

(`tests/test_templates.py:123-170` pins the file byte for byte; update it.) `skills/synthesis-conventions/SKILL.md:12`: replace “never `Write` or `Edit` under `wiki/`; the pre-tool-use guard refuses it.” with “never `Write` or `Edit` under `wiki/`: the pre-tool-use guard refuses the tools, the seeded deny rules refuse the common shell forms, and `compiled-layer` holds the commit on any byte that reaches a page another way.”

- [ ] **Step 6: Live check owed (§8): the deny rules re-run**

Attended, with the shipped `.claude/settings.json` in a scaffolded scratch vault and the current Claude Code: from a session started at the vault root, attempt `echo x > literature/a.md`, `tee literature/b.md`, `sed -i s/a/b/ literature/smith.md`, `cp x wiki/y.md`, `mv x log/z.md`, `touch fulltext/K.md`, `rm log.md`, `rm -r wiki`, and the three that are expected to pass: `python3 -c "open('literature/c.md','w')"`, `python3 -m research_vault capture --vault . <key>`, `perl -i -pe s/a/b/ literature/smith.md`. Record the Claude Code version, each verdict and the date in the task report. If a listed form that the research measured as refused now passes, update the two prose surfaces to say so in the same commit; if `python3 -m research_vault capture` is refused, the rules are wrong and the task stops.

- [ ] **Step 7: Run the suite, commit, branch, close #192 and #193**

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat README.md research_vault/templates/vault/AGENTS.md skills/synthesis-conventions/SKILL.md docs/agents/terminology.md
git switch -c substrate-c/deny-rules
git commit -m "feat(scaffold): eight Edit deny rules for the roster in the seeded .claude/settings.json; doctor's deny-rules row; the machine-surface prose states coverage exactly (#193, #192)" -- research_vault/templates/vault/claude/settings.json research_vault/scaffold.py research_vault/doctor.py research_vault/__main__.py README.md research_vault/templates/vault/AGENTS.md skills/synthesis-conventions/SKILL.md docs/agents/terminology.md tests/test_templates.py tests/test_scaffold.py tests/test_doctor.py tests/test_okf.py tests/test_hooks.py tests/test_config_validity.py
git push -u origin substrate-c/deny-rules
```

After the merge:

```bash
gh issue close 193 --comment "Closed by Plan C Task 3 (spec §5.7): detection is the boundary — literature/, wiki/, log.md, the review queue, the bibliography and the propagation records are caught at commit, fulltext/ at publish. The seed carries eight Edit(...) deny rules for the guard's roster as a speed bump (measured: redirects, tee, sed -i, cp, mv, touch, rm refused; interpreters, scripts and git restores not), doctor compares them with the roster, and the vault guide, README and synthesis-conventions state the coverage exactly. The guard itself is unchanged (tests/test_hooks.py:812-820)."
gh issue close 192 --comment "Closed by Plan C Task 3: README.md:7 names the roster exactly (system/bibliography.json and system/propagations/, not all of system/)."
```

______________________________________________________________________

### Task 4: The records, the review, the baseline

- [ ] **Step 1: Verify the issues and the registries**

```bash
for n in 192 193 207 211 212; do gh issue view $n --json state --jq ".state"; done
python -c "from research_vault import inbox, verify; assert 'compiled-layer' in inbox.CHECK_IDS; assert 'text-layer' not in inbox.CHECK_IDS; assert {'compiled-layer','text-layer'} <= verify.CLOSING_BY_SURFACE['publish']"
```

- [ ] **Step 2: The spec's §7 line for `deny-rules`**

Plan A Task 11 wrote the amendment naming both probe ids; confirm it reads `deny-rules` and that `docs/agents/terminology.md:139` carries both. The `okf-conformance.md` register needs no new row from this plan.

- [ ] **Step 3: Review and baseline**

As Plan A Task 11: the gate over `compiled.py`, `fulltext.py`, `structure.py`, `doctor.py`; survivors in `only_link_targets_changed`, `journal_hashes`, `validate_text` and `_deny_rules_probe` need a stated reason or a killing test. The whole-plan review; findings filed. Measure the per-commit re-check's cost now that `compiled-layer` materialises each commit (`time python -m research_vault verify --vault <scratch> --offline --recheck-commits all` on a vault with a few hundred commits); if it exceeds about 5 s for 300 commits, open an issue proposing a tree-level short-circuit (skip commits whose `wiki/` tree oid equals the parent's) rather than fixing it here.

- [ ] **Step 4: Commit**

```bash
git switch -c substrate-c/close
git commit -m "chore(gate): Plan C survivors triaged" -- mutation-baseline.txt
git push -u origin substrate-c/close
```

Merge `--ff-only` when green. Plan D opens from this `main`.

______________________________________________________________________

## Coverage notes

- §5.4 (#212, #208's check already in Plan A, Q27's hashes, the Bases live check): Task 2.
- §5.5's #207 and #211's `fulltext/` half: Task 1. (#204, #209, #210, #170, #174, OS litter and the reserved `fulltext` type are Plan A's.)
- §5.7 (#193) and #192: Task 3, including `tests/test_hooks.py:812-820` kept and the coverage pin.
- §6.2's deny-rules row: Task 3. §11's `README.md:7`, `templates/vault/AGENTS.md:28`, `okf-conformance.md:42`, `synthesis-conventions` and `setup-vault`/`capture-source` seal steps: Tasks 1–3.
- Deviations recorded in the header: the compile tool keeps no page hash to update; `capture`, `compile apply`, `propagate apply` and the skills are the seal's callers.
