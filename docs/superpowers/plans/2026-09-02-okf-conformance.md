# OKF Conformance Implementation Plan

Disposition: historical (2026-09-06)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close every OKF v0.2 §11 violation the 2026-09-01 audit confirmed, migrate the two structure probes out of doctor into verify (the doctor split), add the mechanical type-stamp fixer, and record what remains — per `docs/research/2026-09-01-okf-conformance-audit.md` §7 as ruled in the 2026-09-02 grill.

**Architecture:** Structure conformance becomes verify checks (per-file `okf-frontmatter` on the commit surface, vault-wide `okf-structure` alongside `tree`), so the pre-commit hook and vault CI inherit them with zero new wiring. Doctor slims to substrate + posture (the `okf` and `inbox` probes are deleted). A new `stamp` module fixes what is mechanical (folder-derived `type`) at the hook and producer touch-paths; everything non-mechanical files to the review queue through verify's existing outcome machinery. The events reader learns OKF's own `verified` shapes without touching ADR 0002's minting rules.

**Tech Stack:** Python 3.12 stdlib only (package rule: one runtime dep, `defusedxml`, untouched). pytest. GitHub Actions cron for the spec-drift job.

## Global Constraints

- Commit with explicit pathspec (`git commit -- <files>`); parallel sessions share this checkout. Every commit message ends with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Run `python -m pytest tests -q` (offline suite) before every commit; live Zotero legs are out of scope for this plan.
- mdformat owns tracked markdown — run the pre-commit hook's mdformat over any doc you edit.
- Every `Outcome.reason` must start with a code from `research_vault/inbox.py` `REASON_CODES` (line 25). Use `schema-violation` for structure violations. No new reason codes.
- New check ids are governed coinages (terminology §4.4): this plan mints `okf-frontmatter`, `okf-structure`, `tree` (verify-side), and the verb `stamp-type`. **Naming cell:** the grill ruled `stamp-fleeting` before the folder-derives-type generalization; `stamp-type` is the generalized name. If the user objects at plan review, rename mechanically — nothing else changes.
- The fleeting exemption (ruled 2026-09-02): human captures in `inbox/` (all `.md` except `inbox/review-queue.md`) are **out of scope for closing checks**. The stamp converges them at chokepoints; they are never a red build, never a blocking finding.
- Vault rule (ruled 2026-09-02): **a note's `type` is determined by its folder.** Map: `literature/**` → `literature`, `synthesis/**` → `synthesis`, `projects/<name>/draft.md` → `project` (narrowed 2026-09-02 per knowledge-harness#105: only the project's one canonical `type: "project"` note derives — every other `.md` under `projects/**`, including a flat `projects/<name>.md` and any sibling file beside `draft.md`, derives nothing), `log/*` → `daily`, `inbox/*` → `fleeting` (`inbox/review-queue.md` → `review-queue`). `system/**` and root-level concept files: any non-empty `type` (no derivation).
- Doctor stays report-only and keeps its own `tree` probe (repair-at-setup via `scaffold_vault` is doctor's job; verify's `tree` check is attestation — different jobs, both stay).
- OKF spec pin: `open-knowledge-format@ad30107`, `SPEC.md` sha256 `26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`.
- Out of scope (ruled): Tier 4 adoption (`resource`/`sources`/`title`/`description`), Alternative A′/B, the §2.1 `status` rename, inbox adjudication machinery, #102 (rides #91).

______________________________________________________________________

## File map

- Create: `research_vault/structure.py` (folder-type map, per-file + vault-wide structure checks), `research_vault/stamp.py` (mechanical type stamp), `tests/test_structure.py`, `tests/test_stamp.py`.
- Modify: `research_vault/verify.py` (wire checks + closing sets), `research_vault/scaffold.py` (delete `_okf_probe`, `_okf_typed_markdown`, `_inbox_probe`; slim `doctor`), `research_vault/__main__.py` (`DOCTOR_WARN_ONLY`, `stamp-type` verb, import touch-path), `research_vault/okf.py` (log rewrite), `research_vault/events.py` (reader tolerance + write-path normalization), `research_vault/templates/vault/index.md`, `research_vault/templates/git/pre-commit`, `.github/workflows/quality.yml`, `research_vault/inbox.py` (CHECK_IDS), `skills/synthesis-conventions/SKILL.md`, `skills/project-flow/SKILL.md`, `skills/evidence-conventions/SKILL.md`, `docs/terminology.md`, `CONTEXT.md`, `docs/superpowers/specs/2026-08-16-foundation-spec.md`, `docs/adr/0001-vault-outlives-its-tools.md`.
- Tests to invert or delete are named per task.

### Task 1: `structure.py` — folder-type map and the per-file `okf-frontmatter` check

**Files:**

- Create: `research_vault/structure.py`
- Test: `tests/test_structure.py`

**Interfaces:**

- Consumes: `research_vault.frontmatter.parse`, `research_vault.outcome.Outcome`, `research_vault.Result`, `research_vault.pathcodec.RepoPath`.

- Produces: `expected_type(relative: str) -> str | None` (None = no derivation, any non-empty type passes; also None for exempt fleeting paths — callers skip those via `is_fleeting`), `is_fleeting(relative: str) -> bool`, `check_note_frontmatter(vault_root, path) -> list[Outcome]` (check id `okf-frontmatter`, one Outcome per file: MATCHED, or UNMATCHED with reason starting `schema-violation`). Task 3 wires these into verify; Task 6 reuses `expected_type`/`is_fleeting`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_structure.py
from pathlib import Path

from research_vault import Result, structure


def _write(tmp_path, relative, text):
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_expected_type_is_the_folder():
    assert structure.expected_type("literature/smith2020.md") == "literature"
    assert structure.expected_type("synthesis/topic.md") == "synthesis"
    assert structure.expected_type("projects/brief.md") == "project"
    assert structure.expected_type("log/2026-08-20.md") == "daily"
    assert structure.expected_type("inbox/review-queue.md") == "review-queue"
    assert structure.expected_type("system/templates/literature.md") is None
    assert structure.expected_type("scratch.md") is None


def test_fleeting_paths_are_named_not_typed():
    assert structure.is_fleeting("inbox/half-thought.md")
    assert not structure.is_fleeting("inbox/review-queue.md")
    assert not structure.is_fleeting("literature/smith2020.md")


def test_check_flags_missing_frontmatter_and_wrong_folder_type(tmp_path):
    path = _write(tmp_path, "literature/untyped.md", "# no frontmatter\n")
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.check == "okf-frontmatter"
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith("schema-violation")

    path = _write(
        tmp_path, "synthesis/mislabeled.md", '---\ntype: "literature"\n---\nbody\n'
    )
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.UNMATCHED
    assert "synthesis" in outcome.reason


def test_check_passes_conformant_and_underived_notes(tmp_path):
    path = _write(tmp_path, "projects/brief.md", '---\ntype: "project"\n---\nbody\n')
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.MATCHED

    path = _write(tmp_path, "system/note.md", '---\ntype: "guide"\n---\nbody\n')
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.MATCHED


def test_check_skips_fleeting_notes(tmp_path):
    path = _write(tmp_path, "inbox/half-thought.md", "just an idea\n")
    assert structure.check_note_frontmatter(tmp_path, path) == []
```

- [ ] **Step 2: Run to verify failure** — `python -m pytest tests/test_structure.py -q`. Expected: FAIL with `ModuleNotFoundError` / `AttributeError` on `structure`.

- [ ] **Step 3: Implement `research_vault/structure.py`**

```python
"""OKF §11 structure checks over vault files (audit §1, ruled 2026-09-02).

The vault rule: a note's ``type`` is determined by its folder. ``system/``
and root-level concepts carry any non-empty type. ``inbox/`` captures other
than the review queue are the recorded fleeting exemption — never checked
here; the stamp converges them at chokepoints.
"""

import os
from pathlib import Path

from . import frontmatter
from .outcome import Outcome, Result
from .pathcodec import RepoPath

_FOLDER_TYPES = {
    "literature": "literature",
    "synthesis": "synthesis",
    "projects": "project",
    "log": "daily",
    "inbox": "fleeting",
}


def is_fleeting(relative: str) -> bool:
    return relative.startswith("inbox/") and relative != "inbox/review-queue.md"


def expected_type(relative: str) -> str | None:
    if relative == "inbox/review-queue.md":
        return "review-queue"
    if is_fleeting(relative):
        return None
    top = relative.split("/", 1)[0]
    if "/" in relative and top in _FOLDER_TYPES:
        return _FOLDER_TYPES[top]
    return None


def _repo_path(relative: str) -> RepoPath:
    return RepoPath(os.fsencode(relative))


def check_note_frontmatter(vault_root, path) -> list[Outcome]:
    """Rules 1 and 2 plus the folder-type vault rule, for one non-reserved file."""
    vault = Path(vault_root)
    relative = Path(path).relative_to(vault).as_posix()
    if is_fleeting(relative):
        return []
    try:
        data, _body = frontmatter.parse(Path(path).read_text())
    except (OSError, UnicodeError, frontmatter.FrontmatterError) as error:
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                f"schema-violation — frontmatter unparseable ({error})",
            )
        ]
    okf_type = data.get("type")
    if not isinstance(okf_type, str) or not okf_type.strip():
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                "schema-violation — missing type (OKF §11 rule 2)",
            )
        ]
    derived = expected_type(relative)
    if derived is not None and okf_type != derived:
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                f"schema-violation — type {okf_type!r} but folder derives {derived!r}",
            )
        ]
    return [
        Outcome(
            "okf-frontmatter", _repo_path(relative), Result.MATCHED, "matched"
        )
    ]
```

- [ ] **Step 4: Run to verify pass** — `python -m pytest tests/test_structure.py -q`. Expected: PASS.
- [ ] **Step 5: Commit** — `git add research_vault/structure.py tests/test_structure.py && git commit -m "feat: okf-frontmatter structure check with folder-derived types" -- research_vault/structure.py tests/test_structure.py`

### Task 2: `okf-structure` — reserved-file shapes (rule 3, §8, §12) and the tree check

**Files:**

- Modify: `research_vault/structure.py`
- Test: `tests/test_structure.py`

**Interfaces:**

- Consumes: Task 1's module internals; `research_vault.scaffold.VAULT_DIRS` (import inside the function to avoid a cycle: `from . import scaffold`).

- Produces: `check_reserved(vault_root) -> list[Outcome]` (check id `okf-structure`; one Outcome per problem, or a single MATCHED) and `check_tree(vault_root) -> Outcome` (check id `tree`, target `vault`, MATCHED iff every `VAULT_DIRS` entry is a directory). Log-shape rule used by Task 5's rewrite: root or nested `log.md`, when present, must contain only `## YYYY-MM-DD` second-level headings, newest first.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_structure.py`)

```python
import re


def _scaffold_min(tmp_path):
    for d in ("literature", "synthesis", "projects", "log", "inbox", "system"):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    _write(tmp_path, "index.md", '---\nokf_version: "0.2"\n---\n# Vault index\n')


def test_reserved_root_index_carries_only_okf_version(tmp_path):
    _scaffold_min(tmp_path)
    assert all(
        o.result is Result.MATCHED for o in structure.check_reserved(tmp_path)
    )
    _write(
        tmp_path, "index.md", '---\ntype: "index"\nokf_version: "0.2"\n---\n# V\n'
    )
    problems = [
        o for o in structure.check_reserved(tmp_path) if o.result is Result.UNMATCHED
    ]
    assert problems and "okf_version" in problems[0].reason


def test_reserved_nested_index_must_be_frontmatter_free(tmp_path):
    _scaffold_min(tmp_path)
    _write(tmp_path, "synthesis/index.md", '---\ntype: "index"\n---\n# S\n')
    problems = [
        o for o in structure.check_reserved(tmp_path) if o.result is Result.UNMATCHED
    ]
    assert problems and "synthesis/index.md" in problems[0].target


def test_reserved_log_must_be_date_grouped_newest_first(tmp_path):
    _scaffold_min(tmp_path)
    _write(
        tmp_path,
        "log.md",
        '---\ntype: "log"\n---\n# Log\n\n## 2026-08-20\n- x\n\n## 2026-08-21\n- y\n',
    )
    problems = [
        o for o in structure.check_reserved(tmp_path) if o.result is Result.UNMATCHED
    ]
    assert problems and "newest first" in problems[0].reason


def test_tree_check(tmp_path):
    from research_vault import scaffold

    scaffold.scaffold_vault(tmp_path)
    assert structure.check_tree(tmp_path).result is Result.MATCHED
```

- [ ] **Step 2: Run to verify failure** — `python -m pytest tests/test_structure.py -q`. Expected: FAIL (`check_reserved` undefined).

- [ ] **Step 3: Implement** (append to `structure.py`)

```python
_DATE_HEADING = None  # set below; module-level compiled regex
import re as _re

_DATE_HEADING = _re.compile(r"## (\d{4}-\d{2}-\d{2})\s*$")


def _log_shape_problems(relative: str, text: str) -> list[str]:
    try:
        _data, body = frontmatter.parse(text)
    except frontmatter.FrontmatterError:
        body = text  # frontmatter on log.md is legal but optional (§8 names index.md only)
    dates = []
    for line in body.splitlines():
        if line.startswith("## "):
            match = _DATE_HEADING.match(line)
            if not match:
                return [f"{relative}: non-date second-level heading {line!r}"]
            dates.append(match.group(1))
    if dates != sorted(dates, reverse=True):
        return [f"{relative}: day headings not newest first"]
    return []


def check_reserved(vault_root) -> list[Outcome]:
    """§11 rule 3: index.md per §8/§12, log.md per §9, at any depth."""
    vault = Path(vault_root)
    problems: list[tuple[str, str]] = []
    for path in sorted(vault.rglob("*.md")):
        if ".git" in path.parts:
            continue
        relative = path.relative_to(vault).as_posix()
        if path.name == "index.md":
            try:
                data, _body = frontmatter.parse(path.read_text())
            except (OSError, UnicodeError, frontmatter.FrontmatterError) as error:
                problems.append((relative, f"unreadable ({error})"))
                continue
            if relative == "index.md":
                extra = sorted(set(data) - {"okf_version"})
                if extra:
                    problems.append(
                        (relative, f"root index carries keys beyond okf_version: {extra}")
                    )
                if not str(data.get("okf_version", "")).strip():
                    problems.append((relative, "missing okf_version"))
            elif data:
                problems.append((relative, "nested index.md must be frontmatter-free"))
        elif path.name == "log.md":
            try:
                text = path.read_text()
            except (OSError, UnicodeError) as error:
                problems.append((relative, f"unreadable ({error})"))
                continue
            problems.extend(("", p) for p in _log_shape_problems(relative, text))
    if problems:
        return [
            Outcome(
                "okf-structure",
                _repo_path(relative) if relative else "log-shape",
                Result.UNMATCHED,
                f"schema-violation — {detail}",
            )
            for relative, detail in problems
        ]
    return [Outcome("okf-structure", "reserved-files", Result.MATCHED, "matched")]


def check_tree(vault_root) -> Outcome:
    from . import scaffold

    vault = Path(vault_root)
    missing = [d for d in scaffold.VAULT_DIRS if not (vault / d).is_dir()]
    if missing:
        return Outcome(
            "tree", "vault", Result.UNMATCHED, f"schema-violation — missing {missing}"
        )
    return Outcome("tree", "vault", Result.MATCHED, "matched")
```

Adjust the two problem tuples so `target` is always a real value: use the file's `relative` for both index and log problems (`_log_shape_problems` already embeds `relative` in the detail; pass `(relative, p)` instead of `("", p)` and strip the duplicated prefix from the detail — implementer's choice, tests assert on `target`/`reason` as written above).

- [ ] **Step 4: Run to verify pass** — `python -m pytest tests/test_structure.py -q`. Expected: PASS.
- [ ] **Step 5: Commit** — `git commit -m "feat: okf-structure reserved-shape and tree checks" -- research_vault/structure.py tests/test_structure.py`

### Task 3: Wire structure checks into verify; closing sets; check-id registry

**Files:**

- Modify: `research_vault/verify.py:53-60` (CLOSING_BY_SURFACE), `research_vault/verify.py:986-991` (the `note_files` region of `_plan_state`), `research_vault/inbox.py:59-79` (CHECK_IDS), `docs/terminology.md` §4.4 (register the three ids + `stamp-type`).
- Test: `tests/test_structure.py`

**Interfaces:**

- Consumes: Task 1–2's `check_note_frontmatter`, `check_reserved`, `check_tree`; `import structure` in verify.py's package import block (verify.py:17-29).

- Produces: commit-surface verification that fails (exit 1) on structure violations; audit surface files them as non-closing findings. Task 4 relies on this coverage existing before doctor's probes are deleted.

- [ ] **Step 1: Write the failing test** (append to `tests/test_structure.py`)

```python
def test_commit_surface_closes_on_structure_violation(tmp_path):
    from research_vault import scaffold, verify

    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "literature" / "untyped.md").write_text("# no frontmatter\n")
    report, effective, hashes, warning = verify.verify_state(
        tmp_path, network=False, git_candidate="worktree"
    )
    decision, blockers = verify.surface_decision("commit", effective, warning)
    assert decision == 1
    assert any("okf-frontmatter" in blocker for blocker in blockers)


def test_commit_surface_ignores_fleeting_notes(tmp_path):
    from research_vault import scaffold, verify

    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "inbox" / "half-thought.md").write_text("just an idea\n")
    report, effective, hashes, warning = verify.verify_state(
        tmp_path, network=False, git_candidate="worktree"
    )
    decision, _blockers = verify.surface_decision("commit", effective, warning)
    assert decision == 0
```

Note: read `surface_decision`'s actual return shape at `verify.py:1128-1160` before asserting — if it returns a different tuple, adapt the assertions to its real contract (the decision int and the rendered blocker strings, wherever they live).

- [ ] **Step 2: Run to verify failure** — `python -m pytest tests/test_structure.py -q`. Expected: FAIL (no structure outcomes produced; decision 0 in the first test).

- [ ] **Step 3: Wire in.** In `verify.py`:

  - Add `structure` to the `from . import (...)` block.
  - In `CLOSING_BY_SURFACE`, add the ids to `commit` and `publish`: `frozenset({"citekey", "evidence-layer", "okf-frontmatter", "okf-structure", "tree"})` and publish's set likewise extended. `audit` stays `frozenset()`.
  - In `_plan_state`, after the `note_files` loop (verify.py:986-991), add a structure sweep over every non-reserved `.md` (not just the three folders), plus the vault-wide checks:

```python
    for path in sorted(vault.rglob("*.md")):
        if ".git" in path.parts:
            continue
        relative = path.relative_to(vault).as_posix()
        if path.name == "index.md" or path.name == "log.md":
            continue
        raw.extend(structure.check_note_frontmatter(vault, path))
    raw.extend(structure.check_reserved(vault))
    raw.append(structure.check_tree(vault))
```

- In `inbox.py` CHECK_IDS, append `"okf-frontmatter", "okf-structure", "tree",` with a comment `# OKF structure migration (2026-09-02 plan)`.

- In `docs/terminology.md` §4.4, add one line registering the three check ids and the `stamp-type` verb as §4.3 imperative-verb coinages.

- [ ] **Step 4: Run the full suite** — `python -m pytest tests -q`. Expected: `tests/test_structure.py` passes. If pre-existing verify tests fail because scaffolded fixtures are now non-conformant (root `index.md` still ships `type: "index"` until Task 5), mark the *minimal* set of newly-failing assertions with the exact template fix they await and do Task 5's template change in this task instead — the two tasks may merge if the suite forces it; note it in the commit message.

- [ ] **Step 5: Commit** — `git commit -m "feat: structure checks close on commit surface; doctor migration groundwork" -- research_vault/verify.py research_vault/inbox.py tests/test_structure.py docs/terminology.md`

### Task 4: The doctor split — delete the `okf` and `inbox` probes

**Files:**

- Modify: `research_vault/scaffold.py:322-392` (delete `_inbox_probe`, `_okf_typed_markdown`, `_okf_probe`), the `doctor()` body where those probes are appended (read `scaffold.py:395-475` and remove the two `probes.append(...)`/`probes.extend(...)` sites that reference them), `research_vault/__main__.py:46` (`DOCTOR_WARN_ONLY = {"staleness", "remote", "backup"}`).
- Test: `tests/test_okf.py` (delete the probe tests at lines 60-110 shown below; keep any regenerate_log tests), `tests/test_scaffold.py`, `tests/test_cli_live.py` (grep for `"okf"`/`"inbox"` probe assertions and doctor probe-count assertions — doctor returns 8 probes after this task, not 10; the docstring at `scaffold.py:401` says "ten ordered probes" — update it).

**Interfaces:**

- Consumes: Task 3's verify coverage (structure checks must be closing on commit before this deletion lands — never leave the vault uncovered).

- Produces: `doctor()` returning exactly: `tree`, `machine-config`, `zotero`, `bbt`, `autoexport`, `staleness`, `remote`, `backup`.

- [ ] **Step 1: Grep for consumers first** — `grep -rn "\"okf\"\|'okf'\|\"inbox\"\|'inbox'" research_vault/ tests/ skills/ docs/agents/` and list every hit that reads the *probe* (not the module). Update each.

- [ ] **Step 2: Delete the three functions and their call sites; update `DOCTOR_WARN_ONLY`; update the doctor docstring.**

- [ ] **Step 3: Delete/adjust the pinned tests** — in `tests/test_okf.py`: delete `test_doctor_okf_probe`, `test_okf_probe_matches_a_freshly_scaffolded_vault`, `test_okf_probe_ignores_fleeting_inbox_notes_but_flags_machine_owned_files`, `test_okf_probe_root_index_missing_okf_version`, `test_okf_probe_root_index_missing_type`, `test_okf_probe_missing_log_md_with_a_day_file_present`. Their coverage now lives in `tests/test_structure.py` (Tasks 1–3). Add one replacement:

```python
def test_doctor_is_substrate_and_posture_only(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    names = [p[0] for p in scaffold.doctor(tmp_path, client=None, settle_seconds=0)]
    assert names == [
        "tree", "machine-config", "zotero", "bbt", "autoexport",
        "staleness", "remote", "backup",
    ]
```

(Adjust the expected order to the actual append order read from `doctor()` — zotero-down collapses several probes to UNREACHABLE but the names still appear; run and pin what the code produces.)

- [ ] **Step 4: Full suite** — `python -m pytest tests -q`. Expected: PASS.
- [ ] **Step 5: Commit** — `git commit -m "refactor: doctor split - okf and inbox probes deleted, coverage moved to verify" -- research_vault/scaffold.py research_vault/__main__.py tests/test_okf.py tests/test_scaffold.py tests/test_cli_live.py`

### Task 5: Producer fixes — root index template, navigation links, log rewrite

**Files:**

- Modify: `research_vault/templates/vault/index.md` (drop `type: "index"`; convert the six `[[folder/]]` wikilinks to relative markdown links), `research_vault/okf.py` (rewrite `regenerate_log`), `research_vault/scaffold.py:360-365` region is already gone (Task 4) — nothing to do there.
- Test: `tests/test_templates.py:73,86-88` (root index canonical assertions), `tests/test_okf.py` (regenerate_log tests), `tests/test_scaffold.py:87` if it asserts index content.

**Interfaces:**

- Consumes: Task 2's log-shape rule (`## YYYY-MM-DD`, newest first, no `## Days`).

- Produces: a freshly scaffolded vault that passes `structure.check_reserved` and `check_note_frontmatter` end to end.

- [ ] **Step 1: Write the failing tests.** Update `tests/test_templates.py`'s canonical root-index assertion to:

```python
    root_data, _ = frontmatter.parse(asset("vault/index.md").read_text())
    assert root_data == {"okf_version": "0.2"}
```

and the canonical-content assertion to the new body (markdown links, e.g. `- [literature/](literature/) — evidence layer: citekey-keyed literature notes`). Add to `tests/test_okf.py`:

```python
def test_regenerated_log_is_date_grouped_newest_first(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-20.md").write_text(
        '---\ntype: "daily"\n---\n- 09:00 imported a\n'
    )
    (tmp_path / "log" / "2026-08-21.md").write_text(
        '---\ntype: "daily"\n---\n- 10:00 imported b\n'
    )
    text = okf.regenerate_log(tmp_path)
    body = text.split("---\n", 2)[2]
    assert "## Days" not in body
    first, second = body.index("## 2026-08-21"), body.index("## 2026-08-20")
    assert first < second
    assert "[2026-08-21](log/2026-08-21.md)" in body
```

- [ ] **Step 2: Run to verify failure** — `python -m pytest tests/test_okf.py tests/test_templates.py -q`.

- [ ] **Step 3: Implement.** New `regenerate_log` body (replace `okf.py:19-39`):

```python
def regenerate_log(vault_root, tail_entries: int = 20) -> str:
    """Rewrite root ``log.md`` per OKF §9: date-grouped, newest first."""
    vault = Path(vault_root)
    log_dir = vault / "log"
    day_files = sorted(log_dir.glob("*.md"), reverse=True) if log_dir.is_dir() else []

    body_lines = ["# Log"]
    remaining = tail_entries
    for day_file in day_files:
        lines = _day_lines(day_file)
        take = lines[:remaining] if remaining > 0 else []
        body_lines.extend(["", f"## {day_file.stem}"])
        body_lines.extend(take)
        body_lines.append(f"- [{day_file.stem}](log/{day_file.stem}.md)")
        remaining -= len(take)

    text = frontmatter.serialize({"type": "log"}) + "\n".join(body_lines) + "\n"
    (vault / "log.md").write_text(text)
    return text
```

Every day file keeps a heading and link even past the tail budget (entries truncate, navigation never does). Edit the index template to drop line 2 and use markdown links.

- [ ] **Step 4: Full suite** — `python -m pytest tests -q`. Expected: PASS, including Task 3's `test_commit_surface_*` now running against a fully conformant scaffold.
- [ ] **Step 5: Commit** — `git commit -m "fix: conformant root index and section 9 log; markdown nav links" -- research_vault/templates/vault/index.md research_vault/okf.py tests/test_okf.py tests/test_templates.py tests/test_scaffold.py`

### Task 6: `stamp.py`, the `stamp-type` verb, hook and producer wiring

**Files:**

- Create: `research_vault/stamp.py`; Test: `tests/test_stamp.py`
- Modify: `research_vault/__main__.py` (new subparser `stamp-type` + wiring dict at `__main__.py:890-920`; call `stamp.stamp_types(vault)` at the top of the import verb's handler and inside `publish` — locate `cmd_` handlers by reading `__main__.py`), `research_vault/templates/git/pre-commit` (stamp before verify).

**Interfaces:**

- Consumes: Task 1's `expected_type`, `is_fleeting`; `frontmatter.parse`/`frontmatter.serialize`.

- Produces: `stamp_types(vault_root, paths=None) -> tuple[list[str], list[str]]` — `(stamped_relatives, reported_relatives)`. Stamps only when **purely additive and fully determined**: no frontmatter at all → prepend `---\ntype: "<derived>"\n---\n`; parseable block missing `type` and folder derives one → insert `type` as the first key. Reports (never edits): unparseable YAML-shaped head, or no derivation (`system/`, root). CLI verb prints one line per action: `stamped <path>` / `skipped <path> — <reason>`, exit 0 always (a fixer, not a gate).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_stamp.py
from research_vault import frontmatter, stamp


def test_stamps_bare_capture_with_folder_type(tmp_path):
    (tmp_path / "inbox").mkdir(parents=True)
    note = tmp_path / "inbox" / "idea.md"
    note.write_text("a half thought\n")
    stamped, reported = stamp.stamp_types(tmp_path)
    assert stamped == ["inbox/idea.md"] and reported == []
    data, body = frontmatter.parse(note.read_text())
    assert data == {"type": "fleeting"}
    assert "a half thought" in body


def test_inserts_type_into_parseable_block(tmp_path):
    (tmp_path / "literature").mkdir(parents=True)
    note = tmp_path / "literature" / "x.md"
    note.write_text('---\ncitekey: "x"\n---\nbody\n')
    stamped, _ = stamp.stamp_types(tmp_path)
    assert stamped == ["literature/x.md"]
    data, _ = frontmatter.parse(note.read_text())
    assert data["type"] == "literature" and data["citekey"] == "x"


def test_reports_unparseable_and_underived(tmp_path):
    (tmp_path / "inbox").mkdir(parents=True)
    (tmp_path / "system").mkdir(parents=True)
    bad = tmp_path / "inbox" / "broken.md"
    bad.write_text("---\nnot: [closed\n---\ntext\n")
    loose = tmp_path / "system" / "note.md"
    loose.write_text("no type derivable here\n")
    stamped, reported = stamp.stamp_types(tmp_path)
    assert stamped == []
    assert sorted(reported) == ["inbox/broken.md", "system/note.md"]
    assert bad.read_text().startswith("---\nnot: [closed")  # untouched


def test_idempotent(tmp_path):
    (tmp_path / "inbox").mkdir(parents=True)
    (tmp_path / "inbox" / "idea.md").write_text("thought\n")
    stamp.stamp_types(tmp_path)
    stamped, _ = stamp.stamp_types(tmp_path)
    assert stamped == []
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `stamp.py`.** Walk `vault.rglob("*.md")` (skip `.git`, `index.md` at any depth, root `log.md`). For each file: if `frontmatter.parse` succeeds and `type` present → skip. If the text starts with `---\n`/`---\r\n` but parse fails → report. If parse succeeds, `type` missing, `expected_type(relative)` is not None → re-serialize with `type` first: `frontmatter.serialize({"type": derived, **data}) + body`, preserving the body byte-for-byte. If no frontmatter delimiter at all and derivation exists → prepend `f'---\ntype: "{derived}"\n---\n' + text`. No derivation → report. Return sorted lists of relatives.
- [ ] **Step 4: Wire the CLI verb** (`stamp-type`, `--vault` required, prints action lines) into `__main__.py`'s subparser + dispatch dict; call `stamp.stamp_types(vault)` at the start of the import handler and the publish handler (read `__main__.py` to find them; the audit cites `publish.py:411` and `__main__.py:301` as log-regeneration touch-points — stamp beside the same call sites).
- [ ] **Step 5: Hook wiring.** In `templates/git/pre-commit`, after the importability check and before the verify invocation, insert:

```sh
stamped="$(python3 -m research_vault stamp-type --vault "$vault" | sed -n 's/^stamped //p')"
if [ -n "$stamped" ]; then
  printf '%s\n' "$stamped" | while IFS= read -r path; do git add -- "$path"; done
fi
```

- [ ] **Step 6: Full suite; commit** — `git commit -m "feat: stamp-type fixer at hook and producer touch-paths" -- research_vault/stamp.py research_vault/__main__.py research_vault/templates/git/pre-commit tests/test_stamp.py`

### Task 7: Events reader tolerance (audit §1.4, §1.5)

**Files:**

- Modify: `research_vault/events.py:26-66` and the `trust_tier` region (read `events.py:250-300`).
- Test: `tests/test_events.py` (locate the existing file; append).

**Interfaces:**

- Produces: `_verified_events` normalizes a bare mapping to a one-element list; `_valid_event` accepts `{"by","at"} <= set(event)` with `at` either a calendar date or an offset-bearing ISO 8601 datetime; `trust_tier` counts check-less foreign events for the `human:` test but excludes them from the checks-coverage set. `record_pass` still writes `{by, at, check}` with calendar dates — the write contract is untouched (ADR 0002 intact).

- [ ] **Step 1: Failing tests** (spec's own example from audit §1.4):

```python
def test_bare_verified_mapping_is_one_element_list():
    text = (
        '---\ntype: "literature"\n'
        'verified: {by: "human:eran", at: "2026-08-02T09:00:00Z"}\n---\nbody\n'
    )
    data, _ = frontmatter.parse(text)
    events_list, malformed = events._verified_events(data)
    assert not malformed and len(events_list) == 1


def test_foreign_by_at_event_does_not_poison_the_list():
    data = {
        "verified": [
            {"by": "human:eran", "at": "2026-08-02T09:00:00Z"},
            {"by": "research_vault/0.1.0", "at": "2026-09-01", "check": "doi"},
        ]
    }
    events_list, malformed = events._verified_events(data)
    assert not malformed and len(events_list) == 2
```

Add a `trust_tier` test after reading its real signature at `events.py:~250-300`: a note whose only event is the foreign `human:` mapping must not derive `unverified` blindly — pin whatever tier the ruled semantics give it (`human:` seen, coverage empty), reading ADR 0002's tier rules in `CONTEXT.md:91` first.

- [ ] **Step 2–4: red, implement, green.** `_valid_event` becomes:

```python
def _iso_or_date(value) -> bool:
    if _calendar_date(value):
        return True
    if not _single_line(value):
        return False
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _valid_event(event) -> bool:
    return (
        type(event) is dict
        and {"by", "at"} <= set(event)
        and set(event) <= {"by", "at", "check"}
        and _single_line(event["by"])
        and _iso_or_date(event["at"])
        and ("check" not in event or _single_line(event["check"]))
    )
```

`_verified_events` inserts `raw_events = [raw_events] if type(raw_events) is dict else raw_events` before the list check.

- [ ] **Step 5: Commit** — `git commit -m "fix: verified reader accepts OKF section 5.2 shapes" -- research_vault/events.py tests/test_events.py`

### Task 8: Events write path — no duplicate `verified` block

**Files:**

- Modify: `research_vault/events.py:153-190` (`_replace_frontmatter_list`).
- Test: `tests/test_events.py`.

**Interfaces:**

- Consumes: Task 7's reader. Produces: `record_pass` on a note whose `verified` is a bare inline mapping rewrites that line into list form — never appends a second `verified:` block (the corruption the audit's Tier 2 correction named).

- [ ] **Step 1: Failing test**

```python
def test_record_pass_on_bare_mapping_note_writes_one_verified_block():
    text = (
        '---\ntype: "literature"\n'
        'verified: {by: "human:eran", at: "2026-08-02T09:00:00Z"}\n---\nbody\n'
    )
    updated = events.record_pass(text, "doi", Result.MATCHED, at="2026-09-02")
    assert updated.count("verified:") == 1
    data, _ = frontmatter.parse(updated)
    assert len(data["verified"]) == 2
```

- [ ] **Step 2–4: red, implement, green.** In `_replace_frontmatter_list`, the `headers` scan (events.py:178-182) currently matches only a bare `verified:` header line. Extend it to also match an inline-value line — `line.rstrip().startswith(f"{field}:")` with content after the colon — and when that form is found, replace that single line with the rendered list block instead of inserting beside it. Keep the `len(headers) > 1` duplicate guard.
- [ ] **Step 5: Commit** — `git commit -m "fix: record_pass normalizes inline verified mapping instead of duplicating it" -- research_vault/events.py tests/test_events.py`

### Task 9: Spec pin and the weekly drift job

**Files:**

- Modify: `.github/workflows/quality.yml` (append a job), `docs/adr/0001-vault-outlives-its-tools.md` (Task 10 rewrites the full text; this task only needs the pin recorded — fold the pin into Task 10 if executing in order, or add a `<!-- okf-spec-pin: ad30107 sha256=26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101 -->` comment line the job greps).

**Interfaces:** none downstream. Constraint from #101: repo-only, never in the vault templates; opens an issue on mismatch; doctor never fetches the spec.

- [ ] **Step 1: Append to `quality.yml`:**

```yaml
  okf-spec-drift:
    name: OKF spec drift (pin vs upstream)
    if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    permissions:
      issues: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - name: Compare upstream SPEC.md against the pin
        env:
          GH_TOKEN: ${{ github.token }}
          PINNED: 26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101
        run: |
          set -euo pipefail
          curl --fail --silent --show-error --location --output /tmp/SPEC.md \
            https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md
          actual="$(sha256sum /tmp/SPEC.md | cut -d' ' -f1)"
          if [ "$actual" != "$PINNED" ]; then
            title="OKF SPEC.md drifted from the ad30107 pin"
            if ! gh issue list --state open --search "$title" --json title -q '.[].title' | grep -qF "$title"; then
              gh issue create --title "$title" --label needs-triage --body "> *Opened automatically by the okf-spec-drift job.*

          Upstream \`SPEC.md\` sha256 is \`$actual\`; the pin is \`$PINNED\` (\`open-knowledge-format@ad30107\`). Reconcile per ADR 0001: read the diff, decide adopt/deviate, move the pin deliberately."
            fi
          fi
```

and add to the workflow's top-level `on:` block: `schedule: [{cron: "17 4 * * 1"}]`.

- [ ] **Step 2: Validate** — `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/quality.yml'))"` (or `actionlint` if installed). Trigger once via `gh workflow run quality.yml` after push and confirm the job passes.
- [ ] **Step 3: Commit** — `git commit -m "ci: weekly OKF spec-drift job against the ad30107 pin (closes #101)" -- .github/workflows/quality.yml`

### Task 10: Register and documentation corrections (audit Tier 5)

**Files:**

- Modify: `docs/terminology.md` (§3 deviation rows + §4 adoption block), `CONTEXT.md`, `docs/superpowers/specs/2026-08-16-foundation-spec.md:16,25,61-62`, `docs/adr/0001-vault-outlives-its-tools.md`, `skills/synthesis-conventions/SKILL.md`, `skills/project-flow/SKILL.md`, `skills/evidence-conventions/SKILL.md`.

No code; each bullet is one edit, all reviewable in a single diff:

- [ ] `CONTEXT.md`: add the folder-derives-type line to the glossary ("Type (OKF): determined by a note's folder — the folder map lives in `research_vault/structure.py`; `system/` and root files carry any non-empty type") and scope the conformance claim at `CONTEXT.md:9` to "the knowledge bundle, minus the recorded `inbox/` fleeting exemption".
- [ ] `docs/terminology.md` §3: add rows — fleeting exemption (declines OKF §11 rule 1 on `inbox/` captures, **class 1**, the capture-time editor as the uncontrolled surface, `stamp-type` as convergence, upstream bundle-scope filing cited when it exists); `verified[].check` extension + coverage-derived tiers (class 3, from audit item 1.5 fix part 4); `verified[].at` calendar precision (class 3, until the ADR 0002 reconciliation); claim-link wikilink syntax (class 1); §10 Attested Computation declination. Delete the phantom "OKF identity merge" row (D8). Split the `sources`/`resource` row per audit §3.1 (D9): keep footnote-attribution at class 1, re-record `sources` adoption as deferred-with-maintenance-cost, not declined-on-identity.
- [ ] `docs/terminology.md` §4: restore the OKF adoption block (D10): `{by, at}` is OKF §5.2 and `check` is the research-vault extension; §5.3 as the source of the three tier names; §7 as the source of the actor convention.
- [ ] `foundation-spec.md:16`: rescope the bolded conformance claim to match CONTEXT.md's wording; `:25` drop the root-index `type` claim; `:61-62` note `generated` is skill-substituted at instantiation (Task 6's producers).
- [ ] `skills/synthesis-conventions/SKILL.md` (D11): add the frontmatter sentence — new synthesis notes route through `system/templates/synthesis.md`, substituting `{{TITLE}}`/`{{ACTOR}}`/`{{NOW}}` (actor per §7: `human:<id>` or `<producer>/<version>`; time via `python3 -c "from research_vault.notes import generated_at_now; print(generated_at_now())"`).
- [ ] `skills/project-flow/SKILL.md`: same substitution instruction at its template step (audit §2.3's fix).
- [ ] `skills/evidence-conventions/SKILL.md:12`: append the one line — a fleeting note opens with `type: "fleeting"` frontmatter when the agent writes it; humans capture free-form and the stamp converges.
- [ ] `docs/adr/0001-vault-outlives-its-tools.md`: replace with the audit §8.2 text **as amended by the rulings**: no "(mechanism restated)" status suffix; the probe sentence reads "The doctor's structure probes are gone; verify's `okf-frontmatter`/`okf-structure` checks assert all three rules on the commit surface, and the weekly CI job re-checks the pinned hash" (one owner per drift — the ADR's probe never fetches); the fleeting passage states the ruled exemption; the pin block verbatim from Global Constraints.
- [ ] mdformat every touched file; run `python -m pytest tests -q` (docs-only, but cheap).
- [ ] Commit — `git commit -m "docs: OKF register rows, adoption block, ADR 0001 replacement, skill frontmatter wiring" -- docs/terminology.md CONTEXT.md docs/superpowers/specs/2026-08-16-foundation-spec.md docs/adr/0001-vault-outlives-its-tools.md skills/synthesis-conventions/SKILL.md skills/project-flow/SKILL.md skills/evidence-conventions/SKILL.md`

### Task 11: Close-out

- [ ] Re-run the audit's five §1 items against the tree by hand (each was verified by a test above — list test name per item in the report): §1.1 → Task 5 template test; §1.2 → Task 5 log test; §1.3 → Tasks 1/6; §1.4 → Task 7; §1.5 → Tasks 7/8.
- [ ] `gh issue close 101` citing Task 9's commit. Comment on #70 with the landed scope and what stays open (Tier 4, A′, B, §2.1 rename).
- [ ] Update `docs/research/2026-09-01-okf-conformance-audit.md`'s header with one line: "Tiers 0–2 + Tier 5 landed <date>, plan `docs/superpowers/plans/2026-09-02-okf-conformance.md`" — per the deletion doctrine the audit doc is scaffolding; flag it for the user's delete-or-keep call rather than deleting unprompted.
- [ ] Final full suite + push: `python -m pytest tests -q && git push origin main`.
