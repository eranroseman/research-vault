# Repository Simplification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the validated duplicate and dead code, consolidate repeated mechanics, and correct the stale no-op sentence without changing any foundation-spec behavior.

**Architecture:** Keep the existing module boundaries except for one focused `gitstate` module that owns byte-preserving reads from Git revisions. Every other change deletes unused surfaces or replaces repeated adapters with one existing/native path; the verification, acknowledgment, marker, event, and four-state contracts remain unchanged.

**Tech Stack:** Python 3.10+, standard library, pytest 8+, Ruff 0.15.21, Git, Markdown.

## Global Constraints

- Work in an isolated worktree created at execution time with `superpowers:using-git-worktrees`; do not implement directly on `main`.
- Before creating that worktree, require `git ls-files --error-unmatch docs/superpowers/plans/2026-08-20-repository-simplification.md`, `git diff --quiet -- docs/superpowers/plans/2026-08-20-repository-simplification.md`, and `git diff --cached --quiet -- docs/superpowers/plans/2026-08-20-repository-simplification.md` all to pass; the plan must be committed unchanged on the starting branch so every executor reads the same document.
- Treat every fenced shell block as an independent invocation starting at the active isolated-worktree root printed by `git rev-parse --show-toplevel`, with `set -e` active so the first unexpected nonzero command stops the block; never carry a `cd core` into the next block and never run implementation commands in the main checkout. An explicitly negated search and a test step labeled “Expected: FAIL” are the only intentional nonzero results.
- Preserve the foundation success criterion verbatim: “Every claim traceable to a real source; zero fabricated citations.”
- Preserve the four states exactly: `MATCHED / UNMATCHED / UNREACHABLE / SKIPPED`; an outage is never reported as fabrication.
- Preserve the inbox acknowledgment boundary: standing scope lasts only until the target content hash changes.
- Preserve claim markers: UNMATCHED stamps `[verify-failed:: <check>/<date>]`; MATCHED clears the exact marker; do not revive the obsolete marker-exclusion hash path.
- Preserve verified-event ownership: only `MATCHED` appends `{by, at, check}` events, and current failures remain substantive state.
- Preserve integrity-lint coverage over `HEAD ∪ working tree` for `literatures/`, `atlas/`, and `efforts/`; whole-file deletion must remain visible.
- Preserve raw Git bytes and distinguish a missing Git object (`None`) from an existing empty blob (`b""`); decode text with `errors="surrogateescape"` only at text consumers.
- Preserve note reads and writes as UTF-8 with `newline=""`; managed/free-region bytes and CRLF marker transitions must not churn.
- Preserve update-notice taxonomy, deterministic type/date deduplication, notice date, detection date, and blocking precedence across live and Retraction Watch legs.
- Preserve archive classification exactly: request failure → `UNREACHABLE`, HTTP 404 → `UNMATCHED`, successful resolution → `MATCHED`.
- Preserve render-first import no-op detection; attachment hashes remain fixity anchors and acknowledgment-scope triggers, never change detectors.
- Add no runtime dependency. `core/pyproject.toml` must retain `dependencies = []`; optional `pypdf` and development `pytest`/`ruff` remain.
- Use TDD for changed interfaces and characterization-before/refactor for behavior-preserving deletions. Run Ruff and focused pytest after every task.
- Preserve unrelated and user-owned work; stage only the files named by each task.

---

## File Structure

- Delete `notes.md`: redundant root copy; `analysis/dev-harness-analysis.md` remains canonical.
- Modify `docs/specs/2026-08-16-foundation-spec.md`: make §5’s attachment-hash wording agree with §7’s render-first correction.
- Create `core/harness_core/gitstate.py`: the sole revision-aware, byte-preserving Git blob/tree boundary.
- Modify `core/harness_core/__main__.py`: consume `gitstate`, remove dead hash/warning helpers, collapse note I/O and marker wrappers, and simplify archive outcome construction.
- Modify `core/harness_core/lints.py`: consume `gitstate` while retaining `HEAD ∪ working tree` enumeration.
- Modify `core/harness_core/checks.py`: accept raw notice groups and expose one shared CSL issued-year parser.
- Modify `core/harness_core/identify.py`: reuse the shared issued-year parser.
- Modify `core/harness_core/notes.py`: delete the unreachable marker-stripping lexer and its unused `re` dependency.
- Modify `core/harness_core/events.py`: delete two unused verified-list aliases; retain `_replace_frontmatter_list`.
- Modify `core/harness_core/inbox.py`: delete the unused loaded-reason wrapper; retain direct reason validation.
- Create `core/tests/test_gitstate.py`: pin missing/empty/blob/ref and revision-tree behavior.
- Modify `core/tests/test_checks.py`: pin the new raw notice-group interface.
- Modify `core/tests/test_verify_cli.py`: reuse verification isolation and standard-library spies.
- Modify `core/tests/test_webapi.py`: reuse the shared network vault and `BytesIO` context behavior.
- Modify `core/tests/test_lints.py`: inline a one-use fixture mutation.

## Explicitly Out of Scope

- Do not remove or redesign `run_verify`'s `scope="all"` parameter, the `Bibliography` wrapper, or `ZoteroClient.register_autoexport`; earlier implementation plans prescribe those surfaces and Plan C consumes the auto-export call.
- Do not change acknowledgment scope, failure-projection semantics, trust-tier derivation, provider routing, selector behavior, or any CLI argument/exit code.
- Do not split `__main__.py`, `checks.py`, or `lints.py` beyond the focused `gitstate.py` extraction; broad restructuring would turn a deletion pass into an architecture migration.
- Do not create a shared line-ending utility for the three tiny local parsers in `__main__.py`, `events.py`, and `lints.py`: one consumer needs only an ending while two need `(content, ending)`, so a cross-module API would add coupling for negligible net deletion.

---

### Task 1: Canonical Documentation and No-op Contract

**Files:**
- Delete: `notes.md`
- Preserve unchanged: `analysis/dev-harness-analysis.md`
- Modify: `docs/specs/2026-08-16-foundation-spec.md:55`

**Interfaces:**
- Consumes: Foundation spec §7’s render-first managed-projection rule at line 110.
- Produces: One canonical dev-harness analysis and one internally consistent no-op contract for all later tasks.

- [ ] **Step 1: Prove the root note is redundant before deletion**

Run:

```bash
sha256sum notes.md analysis/dev-harness-analysis.md
! rg -n 'notes\.md' . \
  --glob '!notes.md' \
  --glob '!docs/superpowers/plans/2026-08-20-repository-simplification.md'
```

Expected: both files print SHA-256 `45bf89a9fd92ec2916ae123e234cfb0a5a9cc036a8b1ec802f7a1ac98b27a2eb`; the reference search returns no matches. Do not proceed if either fact differs.

- [ ] **Step 2: Delete only the redundant copy**

Use `apply_patch` with:

```text
*** Begin Patch
*** Delete File: notes.md
*** End Patch
```

Then stage the deletion:

```bash
git add -u -- notes.md
```

Expected: `analysis/dev-harness-analysis.md` still exists and remains byte-identical to its pre-task content.

- [ ] **Step 3: Correct §5’s stale attachment-hash clause**

Replace this exact clause in the literature-note frontmatter paragraph:

```markdown
the hash of the attachment a quote came from is the re-import no-op comparator and the ack-scope trigger
```

with:

```markdown
attachment hashes are fixity anchors and ack-scope triggers, never re-import change detectors — §7's render-first managed-projection comparison governs no-op detection
```

Do not alter the field list, `attachment-sha256` list shape, OAIS rationale, or §7 paragraph.

- [ ] **Step 4: Verify the documentation boundary**

Run:

```bash
test ! -e notes.md
test -f analysis/dev-harness-analysis.md
git diff --exit-code -- analysis/dev-harness-analysis.md
rg -n 'render-first managed-projection comparison governs no-op detection' docs/specs/2026-08-16-foundation-spec.md
! rg -n 're-import no-op comparator' docs/specs/2026-08-16-foundation-spec.md
git diff --check
```

Expected: the first four commands pass; the stale-phrase search returns no matches; `git diff --check` is silent.

- [ ] **Step 5: Commit**

```bash
git add docs/specs/2026-08-16-foundation-spec.md
git commit -m "docs: clarify render-first no-op detection"
```

`notes.md` is already staged by `git add -u`; verify the commit contains exactly the deletion and the one spec-clause replacement.

---

### Task 2: Delete Unreachable Verification Remnants

**Files:**
- Modify: `core/harness_core/notes.py:4,143-150,222-263`
- Modify: `core/harness_core/events.py:152-154,203-205`
- Modify: `core/harness_core/inbox.py:502-506`
- Modify: `core/harness_core/__main__.py:354-361,451-521,765-767`
- Test: `core/tests/test_notes.py`
- Test: `core/tests/test_events.py`
- Test: `core/tests/test_inbox.py`
- Test: `core/tests/test_verify_cli.py`

**Interfaces:**
- Consumes: `notes.canonical_content(note_text: str) -> str`, `events._replace_frontmatter_list(note_text: str, field: str, rows: list[dict], body: str) -> str`, `inbox.validate_reason(reason: str) -> str`, and `_target_hash(vault_root, outcome, bibliography_universe=_OMITTED_BIBLIOGRAPHY) -> str | None`.
- Produces: The same public behavior with no marker-stripping lexer, no unused aliases, and no impossible line-hash fallback.

- [ ] **Step 1: Run the characterization suite before deletion**

Run:

```bash
cd core
python -m pytest tests/test_notes.py tests/test_events.py tests/test_inbox.py tests/test_verify_cli.py -m "not live and not live_net" -q
```

Expected: PASS; tests marked `live` or `live_net` are deterministically deselected.

- [ ] **Step 2: Record the exact dead-symbol baseline**

Run from the repository root:

```bash
rg -n '_strip_verify_fields|_closes_fence|_replace_verified_events|_render_verified_events|_validate_loaded_reason|_warning_type|_line_bytes' core
```

Expected: `_strip_verify_fields` and `_closes_fence` refer only to each other and their six local regex constants; `_replace_verified_events`, `_render_verified_events`, `_validate_loaded_reason`, and `_warning_type` appear only at their definitions; `_line_bytes` appears at its definition and in the branch after the earlier identical `origin.is_file()` return.

- [ ] **Step 3: Delete the orphaned marker-stripping pipeline**

In `core/harness_core/notes.py`, use `apply_patch` to remove the `re` import, all six constants printed by this command, and the complete two function definitions printed by it:

```bash
rg -n '^import re$|^_VERIFY_MARKER|^_VERIFY_BEFORE_ANCHOR|^_VERIFY_TERMINAL|^_CLAIM_LINE|^_FENCE_OPEN|^_FENCE_CLOSE|^def _strip_verify_fields|^def _closes_fence' core/harness_core/notes.py
```

Delete from `def _strip_verify_fields` through its final `return "".join(lines)`, and from `def _closes_fence` through its final boolean return. Keep `canonical_content`, `_frontmatter_close`, `_verified_list_index`, and `_verified_only_envelope` unchanged.

- [ ] **Step 4: Delete the definition-only aliases and validators**

Use `apply_patch` to delete exactly these complete functions and no callers, because none exist:

```bash
rg -n '^def _replace_verified_events|^def _render_verified_events' core/harness_core/events.py
rg -n '^def _validate_loaded_reason' core/harness_core/inbox.py
rg -n '^def _warning_type' core/harness_core/__main__.py
```

Retain `events._replace_frontmatter_list`, `events._render_frontmatter_list`, every direct `validate_reason(data["reason"])` call in `inbox.load`, and structured notice fingerprints.

- [ ] **Step 5: Delete the impossible line-hash path**

In `_target_hash`, remove the unused assignment and unreachable branch:

```python
line_no = outcome.extra.get("line_no")

if origin and origin.is_file() and isinstance(line_no, int):
    data = _line_bytes(origin, line_no)
    if data is not None:
        return hashlib.sha256(data).hexdigest()[:16]
```

Then delete `_line_bytes` completely. Keep the preceding reachable whole-origin-file hash and the claim-address hash paths unchanged; this preserves §3’s file/content acknowledgment scope.

- [ ] **Step 6: Prove the symbols are gone and behavior remains green**

Run:

```bash
! rg -n '_strip_verify_fields|_closes_fence|_replace_verified_events|_render_verified_events|_validate_loaded_reason|_warning_type|_line_bytes' core
cd core
ruff format --check harness_core tests
ruff check harness_core tests
python -m pytest tests/test_notes.py tests/test_events.py tests/test_inbox.py tests/test_verify_cli.py -m "not live and not live_net" -q
```

Expected: the negative search succeeds, Ruff passes, and the same characterization suite passes.

- [ ] **Step 7: Commit**

```bash
git add core/harness_core/notes.py core/harness_core/events.py core/harness_core/inbox.py core/harness_core/__main__.py
git commit -m "refactor: delete obsolete verification remnants"
```

---

### Task 3: One Byte-preserving Git Revision Boundary

**Files:**
- Create: `core/harness_core/gitstate.py`
- Modify: `core/harness_core/__main__.py:16-30,313-322,378,464,492,506`
- Modify: `core/harness_core/lints.py:1-12,105-141,254-260,298-348`
- Create: `core/tests/test_gitstate.py`
- Test: `core/tests/test_lints.py`
- Test: `core/tests/test_verify_cli.py`

**Interfaces:**
- Consumes: Git CLI and `Path`.
- Produces: `gitstate.blob_bytes(vault_root: Path, revision: str, relative: str) -> bytes | None` and `gitstate.revision_paths(vault_root: Path, revision: str, *prefixes: str) -> set[str]`.

- [ ] **Step 1: Write failing contract tests for the new boundary**

Create `core/tests/test_gitstate.py`:

```python
import subprocess

from harness_core import gitstate


def test_revision_paths_and_blob_bytes_preserve_an_arbitrary_revision(tmp_vault):
    path = tmp_vault / "atlas" / "deleted.md"
    path.write_bytes(b"claim \xff\n")
    subprocess.run(["git", "add", "atlas/deleted.md"], cwd=tmp_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "binary claim"],
        cwd=tmp_vault,
        check=True,
    )
    subprocess.run(["git", "tag", "snapshot"], cwd=tmp_vault, check=True)
    path.write_bytes(b"replacement\n")
    subprocess.run(["git", "add", "atlas/deleted.md"], cwd=tmp_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "replace claim"],
        cwd=tmp_vault,
        check=True,
    )
    path.unlink()

    assert gitstate.revision_paths(tmp_vault, "snapshot", "atlas") == {
        "atlas/deleted.md"
    }
    assert (
        gitstate.blob_bytes(tmp_vault, "snapshot", "atlas/deleted.md")
        == b"claim \xff\n"
    )
    assert (
        gitstate.blob_bytes(tmp_vault, "HEAD", "atlas/deleted.md")
        == b"replacement\n"
    )
    assert gitstate.blob_bytes(tmp_vault, "snapshot", "atlas/missing.md") is None


def test_blob_bytes_distinguishes_an_empty_blob_from_a_missing_blob(tmp_vault):
    path = tmp_vault / "atlas" / "empty.md"
    path.write_bytes(b"")
    subprocess.run(["git", "add", "atlas/empty.md"], cwd=tmp_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "empty claim"],
        cwd=tmp_vault,
        check=True,
    )

    assert gitstate.blob_bytes(tmp_vault, "HEAD", "atlas/empty.md") == b""
    assert gitstate.blob_bytes(tmp_vault, "HEAD", "atlas/absent.md") is None
```

- [ ] **Step 2: Run the tests to verify the interface is absent**

Run:

```bash
cd core
python -m pytest tests/test_gitstate.py -m "not live and not live_net" -q
```

Expected: collection fails because `harness_core.gitstate` does not exist.

- [ ] **Step 3: Implement the focused Git boundary**

Create `core/harness_core/gitstate.py`:

```python
"""Byte-preserving reads from Git revisions."""

import subprocess
from pathlib import Path


def blob_bytes(vault_root: Path, revision: str, relative: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{revision}:{relative}"],
        cwd=Path(vault_root),
        capture_output=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def revision_paths(
    vault_root: Path, revision: str, *prefixes: str
) -> set[str]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", revision, "--", *prefixes],
        cwd=Path(vault_root),
        capture_output=True,
        text=True,
        check=False,
    )
    return set(result.stdout.splitlines()) if result.returncode == 0 else set()
```

- [ ] **Step 4: Route CLI HEAD reads through `gitstate.blob_bytes`**

Import the module with the existing package imports:

```python
from . import gitstate
```

Delete `_head_bytes`. Replace its four calls exactly:

```python
gitstate.blob_bytes(vault_root, "HEAD", target)
gitstate.blob_bytes(vault_root, "HEAD", outcome.extra["note_path"])
gitstate.blob_bytes(vault_root, "HEAD", outcome.extra.get("note_path", ""))
```

The `target` form occurs in `_append_only_basis` and the missing-file branch; retain each caller’s existing `or b""` and `_note_bytes(data)` behavior.

- [ ] **Step 5: Route lints through `gitstate` without losing HEAD-side enumeration**

Import `gitstate`. Delete `_head_text`, `_head_markdown_paths`,
`_current_markdown_paths`, `_tag_paths`, and `_tag_bytes`. In
`lint_claim_immutability`, use `apply_patch` to replace this exact loop prefix:

```python
for rel in sorted(_head_markdown_paths(vault) | _current_markdown_paths(vault)):
    head = _head_text(vault, rel)
    if head is None:
        continue
```

with:

```python
roots = ("literatures", "atlas", "efforts")
head_paths = gitstate.revision_paths(vault, "HEAD", *roots)
current_paths = {
    rel
    for root in roots
    for rel in _current_paths(vault, root)
}
markdown_paths = {
    rel for rel in head_paths | current_paths if rel.endswith(".md")
}
for rel in sorted(markdown_paths):
    head_bytes = gitstate.blob_bytes(vault, "HEAD", rel)
    if head_bytes is None:
        continue
    head = head_bytes.decode(errors="surrogateescape")
```

Replace tag-side calls with the exact interfaces:

```python
gitstate.revision_paths(vault_root, tag, prefix)
gitstate.blob_bytes(vault_root, tag, rel)
```

Do not use working-tree-only enumeration for claim immutability; deleted HEAD files are mandatory inputs.

- [ ] **Step 6: Run focused regression tests**

Run:

```bash
cd core
ruff format harness_core/gitstate.py harness_core/__main__.py harness_core/lints.py tests/test_gitstate.py
ruff check harness_core tests
python -m pytest tests/test_gitstate.py tests/test_lints.py tests/test_verify_cli.py -m "not live and not live_net" -q
```

Expected: PASS, including whole-file deletion, invalid UTF-8, nested-symlink containment, published-tag drift, and empty-vs-missing blob regressions.

- [ ] **Step 7: Commit**

```bash
git add core/harness_core/gitstate.py core/harness_core/__main__.py core/harness_core/lints.py core/tests/test_gitstate.py
git commit -m "refactor: consolidate git revision reads"
```

---

### Task 4: Raw Notice Normalization, Archive Outcomes, and Shared CSL Year Parsing

**Files:**
- Modify: `core/harness_core/checks.py:211-227,519-545,760-789,900-929,931-978`
- Modify: `core/harness_core/identify.py:3-4,27-47`
- Modify: `core/harness_core/__main__.py:719-762`
- Modify: `core/tests/test_checks.py`
- Modify: `core/tests/test_identify.py`
- Test: `core/tests/test_verify_cli.py`

**Interfaces:**
- Consumes: raw notice dictionaries shaped as `{"type": str, "notice_date": str | None}` and existing `webapi.get_status` behavior.
- Produces: `checks._merge_warn_notices(*notice_groups) -> list[dict]` and `checks.metadata_year(value) -> tuple[bool, int | None]`; public `Outcome` behavior is unchanged.

- [ ] **Step 1: Write a failing test for raw notice groups**

Append to `core/tests/test_checks.py` near the update-notice reducer tests:

```python
def test_merge_warn_notices_accepts_raw_groups_and_deduplicates_type_date():
    merged = checks._merge_warn_notices(
        [
            {"type": "correction", "notice_date": "2020-01-01"},
            {"type": "correction", "notice_date": "2020-01-01"},
        ],
        [
            {"type": "erratum", "notice_date": None},
            {"type": "retraction", "notice_date": "2020-01-02"},
            {"type": 7, "notice_date": "2020-01-03"},
        ],
    )

    assert merged == [
        {"type": "correction", "notice_date": "2020-01-01"},
        {"type": "erratum", "notice_date": None},
    ]
```

- [ ] **Step 2: Run the test to verify the old adapter rejects raw lists**

Run:

```bash
cd core
python -m pytest tests/test_checks.py::test_merge_warn_notices_accepts_raw_groups_and_deduplicates_type_date -m "not live and not live_net" -q
```

Expected: FAIL with `AttributeError` because the old helper expects `Outcome.extra`.

- [ ] **Step 3: Make warning normalization consume raw groups**

Replace `_merge_warn_notices` with:

```python
def _merge_warn_notices(*notice_groups) -> list[dict]:
    """Merge warning notices in deterministic, de-duplicated order."""
    notices = set()
    for values in notice_groups:
        if not isinstance(values, list):
            continue
        for value in values:
            if not isinstance(value, dict):
                continue
            notice_type = _norm_type(value.get("type"))
            notice_date = value.get("notice_date")
            if notice_type not in WARN_TYPES or not (
                notice_date is None or isinstance(notice_date, str)
            ):
                continue
            notices.add((notice_type, notice_date))
    return [
        {"type": notice_type, "notice_date": notice_date}
        for notice_type, notice_date in sorted(
            notices,
            key=lambda notice: (notice[0], notice[1] is None, notice[1] or ""),
        )
    ]
```

Change the Crossref and RW call sites to:

```python
warns = _merge_warn_notices(warns)
```

Change the reducer call to:

```python
warnings = _merge_warn_notices(
    *(outcome.extra.get("warn_notices", []) for outcome in outcomes)
)
```

Delete only the throwaway adapters with this exact shape:

```python
Outcome(
    "update-notice",
    target,
    Result.MATCHED,
    "matched",
    {"warn_notices": warns},
)
```

- [ ] **Step 4: Add a characterization test for malformed discovery years**

Append this test to `core/tests/test_identify.py` before consolidating the
parser:

```python
@pytest.mark.parametrize(
    "issued",
    [None, {"date-parts": "malformed"}, {"date-parts": [[True]]}],
)
def test_discover_omits_an_absent_or_malformed_issued_year_without_failing(
    net_vault, monkeypatch, issued
):
    crossref_queries = []

    def fake(url, vault_root, params=None, headers=None, timeout=10.0):
        if "api.crossref.org/works" in url:
            crossref_queries.append(params["query.bibliographic"])
            return 200, {"message": {"items": []}}
        if "esearch.fcgi" in url:
            return 200, {"esearchresult": {"idlist": []}}
        raise AssertionError(f"unexpected URL {url}")

    monkeypatch.setattr(webapi, "get_json", fake)

    outcome = identify.discover(
        net_vault,
        _entry(issued=issued),
    )

    assert outcome.result is Result.SKIPPED
    assert outcome.extra == {"identifiers": {}}
    assert crossref_queries == ["Mortality  Decline Smith"]
```

Run:

```bash
cd core
python -m pytest tests/test_identify.py::test_discover_omits_an_absent_or_malformed_issued_year_without_failing -m "not live and not live_net" -q
```

Expected: PASS against the existing local traversal. This characterizes the
behavior the shared parser must preserve.

- [ ] **Step 5: Share the CSL issued-year parser**

Rename `_metadata_year` to `metadata_year` in `checks.py` and update both `check_metadata` call sites. In `identify.py`, import it:

```python
from .checks import Outcome, metadata_year, normalize_text
```

Replace the local `issued.date-parts` traversal in `_query_terms` with:

```python
_, issued_year = metadata_year(entry.get("issued"))
year = str(issued_year) if issued_year is not None else ""
```

Malformed and absent dates must continue to omit the year rather than making discovery fail.

- [ ] **Step 6: Collapse web-archive construction without collapsing states**

Replace the three `Outcome` construction branches inside `_archive_outcomes` with:

```python
try:
    status = webapi.get_status(archive_url, vault_root)
except webapi.ApiError:
    result = Result.UNREACHABLE
    reason = "outage — archive-url unavailable"
else:
    if status == 404:
        result = Result.UNMATCHED
        reason = "missing-archive — archive-url 404s"
    else:
        result = Result.MATCHED
        reason = "matched"
outcomes.append(checks.Outcome("web-archive", target, result, reason))
```

Do not treat `ApiError` as 404 and do not treat 404 as an outage.

- [ ] **Step 7: Run focused network and discovery tests**

Run:

```bash
cd core
ruff format harness_core/checks.py harness_core/identify.py harness_core/__main__.py tests/test_checks.py tests/test_identify.py
ruff check harness_core tests
python -m pytest tests/test_checks.py tests/test_identify.py tests/test_verify_cli.py -m "not live and not live_net" -q
```

Expected: PASS, including Crossref/RW warning merge, notice-date retention, blocking precedence, arXiv/DataCite routing, archive 200/404/outage, and malformed issued-date behavior.

- [ ] **Step 8: Commit**

```bash
git add core/harness_core/checks.py core/harness_core/identify.py core/harness_core/__main__.py core/tests/test_checks.py core/tests/test_identify.py
git commit -m "refactor: simplify notice and archive outcomes"
```

---

### Task 5: One Note I/O Pair and Direct Marker Mutation

**Files:**
- Modify: `core/harness_core/__main__.py:95-102,153-248,282-289,544-625`
- Test: `core/tests/test_cli_live.py`
- Modify: `core/tests/test_verify_cli.py:10-18,325,607,622,704,722,751,806,903`

**Interfaces:**
- Consumes: `Path.open`, `_terminal_marker_pattern(check, claim_id) -> re.Pattern`, and `_mutate_marker(vault_root, outcome, date, *, clear=False)`.
- Produces: `_read_note_text(path) -> str` and `_write_note_text(path, text) -> None` as the only note I/O pair; tests call the real `_mutate_marker` path with `clear=True` directly; marker behavior is unchanged.

- [ ] **Step 1: Run byte/newline characterization tests**

Run:

```bash
cd core
python -m pytest \
  tests/test_cli_live.py::test_import_note_rerender_preserves_crlf_free_tail_bytes \
  tests/test_verify_cli.py::test_marker_mutation_preserves_crlf_and_exact_claim_spacing \
  tests/test_verify_cli.py::test_marker_preserves_legal_trailing_anchor_whitespace \
  tests/test_verify_cli.py::test_marker_stamp_ignores_prose_lookalike_and_clears_only_terminal_field \
  -m "not live and not live_net" \
  -q
```

Expected: all four tests PASS before refactoring.

- [ ] **Step 2: Keep one explicit note I/O pair**

Keep one pair near the first current call site, with these exact bodies:

```python
def _read_note_text(path):
    with Path(path).open("r", encoding="utf-8", newline="") as note:
        return note.read()


def _write_note_text(path, text):
    with Path(path).open("w", encoding="utf-8", newline="") as note:
        note.write(text)
```

Replace `_read_note(path)` with `_read_note_text(path)`, replace `_write_note(path, text)` with `_write_note_text(path, text)`, and delete the second pair at the old lines 282-289. Do not use `Path.read_text()`/`write_text()` here because they do not expose `newline=""`.

- [ ] **Step 3: Inline the one-caller marker wrappers**

Inside `_mutate_marker`, after `terminal_claim_id` is known, bind one pattern and use it for both paths:

```python
pattern = _terminal_marker_pattern(outcome.check, terminal_claim_id)
replacement = (
    pattern.sub(" " if isinstance(terminal_claim_id, str) else "", content)
    if clear
    else line
)
if not clear and pattern.search(content) is None:
    if anchored:
        before = content[: anchor.start()]
        terminal_anchor = content[anchor.start() :]
        replacement = (
            before
            + f"[verify-failed:: {outcome.check}/{date}] "
            + terminal_anchor
        )
    else:
        replacement = content + f" [verify-failed:: {outcome.check}/{date}]"
    replacement += ending
elif clear:
    replacement += ending
```

Delete `_clear_marker` and `_has_terminal_marker`; retain `_terminal_marker_pattern`, `_terminal_anchor_match`, and `_split_line_ending`.

- [ ] **Step 4: Delete the test-only marker-clear compatibility shim**

Remove `_clear_verify_failed` from the imports in `core/tests/test_verify_cli.py`.
Replace its eight calls mechanically, preserving each existing outcome variable:

```python
_mutate_marker(net_vault, outcome, "2026-08-16", clear=True)
_mutate_marker(net_vault, origin, "2026-08-16", clear=True)
_mutate_marker(net_vault, citekey, "2026-08-16", clear=True)
_mutate_marker(net_vault, anchored, "2026-08-16", clear=True)
_mutate_marker(net_vault, line_only, "2026-08-16", clear=True)
```

Several forms occur more than once; replace every occurrence. Then delete
`_clear_verify_failed` from `core/harness_core/__main__.py`. This removes only a
test delegation wrapper; production already calls
`_mutate_marker(vault_root, outcome, detection_date, clear=True)`.

- [ ] **Step 5: Run all import and marker regressions**

Run:

```bash
cd core
ruff format harness_core/__main__.py tests/test_verify_cli.py
ruff check harness_core tests
python -m pytest tests/test_cli_live.py tests/test_verify_cli.py -m "not live and not live_net" -q
! rg -n '_clear_marker|_has_terminal_marker|_clear_verify_failed' harness_core tests
```

Expected: PASS, including import NOOP, free-tail preservation, exact marker placement/clearing, acknowledgment hash stability, and CLI routing.

- [ ] **Step 6: Commit**

```bash
git add core/harness_core/__main__.py core/tests/test_verify_cli.py
git commit -m "refactor: collapse note IO and marker wrappers"
```

---

### Task 6: Verification Test Isolation and Native Spies

**Files:**
- Modify: `core/tests/test_verify_cli.py:1-15,123-140,838-857,1098-1120,1133-1137,1242-1246,1329-1370`

**Interfaces:**
- Consumes: pytest’s `monkeypatch` fixture, `unittest.mock.Mock`, and `_isolate_network_verify(monkeypatch, outcomes) -> None`.
- Produces: The same verification assertions with one isolation setup and one standard call-spy pattern.

- [ ] **Step 1: Establish the test-file baseline**

Run:

```bash
cd core
python -m pytest tests/test_verify_cli.py -m "not live and not live_net" -q
```

Expected: PASS before test-only refactoring.

- [ ] **Step 2: Use pytest’s managed monkeypatch fixture**

Change the offline RW test signature and setup to:

```python
def test_update_notice_is_one_effective_outcome_with_rw_blocker_offline(
    net_vault, tmp_path, monkeypatch
):
    csv_file = tmp_path / "rw.csv"
    csv_file.write_text(
        "OriginalPaperDOI,OriginalPaperPubMedID,RetractionDate,RetractionNature\n"
        ",123,2020-01-01,Retraction\n"
    )
    monkeypatch.setattr(
        "harness_core.__main__._bibliography_entries",
        lambda _: [{"id": "pmid", "PMID": "123"}],
    )
    report = run_verify(
        net_vault, network=False, detection_date="2026-08-16", rw_csv=csv_file
    )
```

Keep the existing notice assertions; delete `pytest.MonkeyPatch()`, `try/finally`, and `.undo()`.

- [ ] **Step 3: Reuse the isolation helper everywhere**

Replace the repeated block at the acknowledged-warning test with:

```python
_isolate_network_verify(monkeypatch, [warning])
```

Delete the two redundant repatches immediately after these existing calls:

```python
_isolate_network_verify(monkeypatch, current)
```

The helper’s lambda already closes over the mutable `current` list and returns `list(outcomes)` on every invocation.

- [ ] **Step 4: Replace handwritten load counters with `Mock`**

Add:

```python
from unittest.mock import Mock
```

Use this exact pattern in both bibliography-load tests:

```python
load = Mock(wraps=bibliography.load)
monkeypatch.setattr(bibliography, "load", load)

run_verify(net_vault, network=False, detection_date="2026-08-16")

load.assert_called_once_with(net_vault)
```

Retain the invalid-bibliography setup and `_file_outcomes`/lint isolation in the second test. Delete both `calls` lists and both `counted` closures.

- [ ] **Step 5: Run and format the test file**

Run:

```bash
cd core
ruff format tests/test_verify_cli.py
ruff check tests/test_verify_cli.py
python -m pytest tests/test_verify_cli.py -m "not live and not live_net" -q
```

Expected: PASS with unchanged test selection and assertions.

- [ ] **Step 6: Commit**

```bash
git add core/tests/test_verify_cli.py
git commit -m "test: simplify verification fixtures"
```

---

### Task 7: Shared Web Fixture and Minimal Lint Setup

**Files:**
- Modify: `core/tests/test_webapi.py:11-44`
- Modify: `core/tests/test_lints.py:1-10,303-309`
- Consume unchanged: `core/tests/conftest.py:117-122`

**Interfaces:**
- Consumes: shared `net_vault` fixture and `io.BytesIO`’s inherited context-manager protocol.
- Produces: No new interface; only smaller tests with identical assertions.

- [ ] **Step 1: Establish both test-file baselines**

Run:

```bash
cd core
python -m pytest tests/test_webapi.py tests/test_lints.py -m "not live and not live_net" -q
```

Expected: PASS before refactoring.

- [ ] **Step 2: Use `BytesIO`’s native context manager and the shared vault fixture**

Reduce `FakeResponse` to:

```python
class FakeResponse(io.BytesIO):
    def __init__(self, payload, status=200):
        encoded = (
            payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        )
        super().__init__(encoded)
        self.status = status
```

Delete the local `vault_with_mailto` fixture. Rename every `vault_with_mailto` parameter and use in `test_webapi.py` to `net_vault`; the shared fixture already creates the identical `.harness/machine.json` value `{"mailto": "eran@example.edu"}`.

Verify the mechanical rename with:

```bash
! rg -n 'vault_with_mailto' core/tests/test_webapi.py
rg -n '\bnet_vault\b' core/tests/test_webapi.py
```

- [ ] **Step 3: Inline the one-use published-drift mutation**

Delete `_write_published`. At `test_published_drift_includes_untracked_files`, replace its call with:

```python
draft.write_text(
    draft.read_text().replace('status: "drafting"', 'status: "published"')
    + "\nnew paragraph after publishing\n"
)
```

Do not change the tag setup, untracked-file setup, or expected drift outcome.

- [ ] **Step 4: Run and format both test files**

Run:

```bash
cd core
ruff format tests/test_webapi.py tests/test_lints.py
ruff check tests/test_webapi.py tests/test_lints.py
python -m pytest tests/test_webapi.py tests/test_lints.py -m "not live and not live_net" -q
```

Expected: PASS; `FakeResponse` still closes through `BytesIO.__exit__`, network tests still receive the canonical mailto, and the untracked published-drift regression still fires.

- [ ] **Step 5: Commit**

```bash
git add core/tests/test_webapi.py core/tests/test_lints.py
git commit -m "test: reuse standard test scaffolding"
```

---

### Task 8: Whole-branch Verification and Simplification Accounting

**Files:**
- Verify only: all files changed by Tasks 1-7

**Interfaces:**
- Consumes: every task and fix commit since the branch merge base, plus every global constraint above.
- Produces: A green, Ruff-clean, behavior-preserving simplification branch ready for code review.

- [ ] **Step 1: Run the complete offline suite**

Run:

```bash
cd core
python -m pytest tests -m "not live and not live_net" -q
```

Expected: PASS; tests marked `live` or `live_net` are deterministically deselected even if their environment flags are inherited.

- [ ] **Step 2: Run the formatting and lint gates**

Run:

```bash
cd core
ruff format --check harness_core tests
ruff check harness_core tests
```

Expected: both commands pass with no output other than Ruff’s success summary.

- [ ] **Step 3: Recheck load-bearing focused suites**

Run:

```bash
cd core
python -m pytest \
  tests/test_gitstate.py \
  tests/test_notes.py \
  tests/test_events.py \
  tests/test_inbox.py \
  tests/test_checks.py \
  tests/test_identify.py \
  tests/test_lints.py \
  tests/test_verify_cli.py \
  tests/test_cli_live.py \
  tests/test_webapi.py \
  -m "not live and not live_net" \
  -q
```

Expected: PASS, including HEAD-side deletion, invalid bytes, marker transitions, verified/current-failure state, notice fingerprints, archive four-state routing, and render-first import NOOP behavior.

- [ ] **Step 4: Run static deletion and documentation checks**

Run from the repository root:

```bash
test ! -e notes.md
test -f analysis/dev-harness-analysis.md
! rg -n '_strip_verify_fields|_closes_fence|_replace_verified_events|_render_verified_events|_validate_loaded_reason|_warning_type|_line_bytes|_head_bytes|_head_text|_head_markdown_paths|_current_markdown_paths|_tag_paths|_tag_bytes|_metadata_year|_clear_marker|_has_terminal_marker|_clear_verify_failed|_write_published|^def _read_note\(|^def _write_note\(|vault_with_mailto' core
rg -n 'render-first managed-projection comparison governs no-op detection' docs/specs/2026-08-16-foundation-spec.md
! rg -n 're-import no-op comparator' docs/specs/2026-08-16-foundation-spec.md
MERGE_BASE="$(git merge-base main HEAD)"
git diff --check "$MERGE_BASE"..HEAD
git diff --quiet "$MERGE_BASE"..HEAD -- core/pyproject.toml
rg -n '^dependencies = \[\]$' core/pyproject.toml
```

Expected: every positive check finds exactly the retained contract, every negative search succeeds, and the diff check is silent.

- [ ] **Step 5: Inspect the actual simplification rather than trusting the estimate**

Run:

```bash
MERGE_BASE="$(git merge-base main HEAD)"
git diff --stat "$MERGE_BASE"..HEAD
git diff --numstat "$MERGE_BASE"..HEAD
git status --short
```

Expected: net deletions exceed additions, no dependency file changes, no unrelated files, and a clean worktree. The Ponytail estimate (`-353` lines possible) is a ceiling, not an acceptance threshold; behavioral contracts and review quality govern.

- [ ] **Step 6: Prepare the final-review contract for the execution workflow**

The chosen execution workflow owns exactly one whole-branch review. Under
`superpowers:subagent-driven-development`, provide its built-in final reviewer
the merge-base-to-HEAD diff. Under `superpowers:executing-plans`, invoke
`superpowers:requesting-code-review` once against that same range. Give either
reviewer this exact checklist:

```bash
git merge-base main HEAD
git rev-parse HEAD
```

Pass the two printed commit IDs as the review base and head, respectively.

```text
1. HEAD ∪ working-tree enumeration still catches whole-file deletion.
2. Git blob reads preserve bytes and missing-vs-empty semantics.
3. Warning notice type/date/detection-date and blocking precedence are unchanged.
4. Archive 404/outage/success remain UNMATCHED/UNREACHABLE/MATCHED.
5. UTF-8/newline-preserving note I/O keeps CRLF/free-tail tests green.
6. Only the stale §5 no-op phrase changed; §7 render-first semantics remain intact.
7. No runtime dependency was added.
```

Expected: reviewer returns no unresolved Critical, Important, or Minor findings before integration.
