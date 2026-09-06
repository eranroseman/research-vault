# Status-Marking Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every in-scope repository document and every open issue exactly one machine-checked `Disposition:` line, drawn from §10's closed vocabulary, applied only through a proposal the author has reviewed.

**Architecture:** One repo-maintenance module, `scripts/dispositions.py`, carries four separable jobs — decide the scope, read a marker at its positional anchor, propose a value by §10's precedence order, and apply a reviewed row. Between propose and apply sits a human gate: the script writes a TSV of one row per document and issue, the author edits any cell, and apply is mechanical from the edited file, so no judgement is ever made by the classifier alone. `tests/test_dispositions.py` holds both the module's unit tests and the standing linter, so the check rides the existing suite and CI with no new verb, no new hook and no new dependency.

**Tech Stack:** Python 3.12 stdlib only (`re`, `subprocess`, `pathlib`, `argparse`, `json`, `datetime`). pytest. `gh` CLI for the issue legs, which are skipped when it is absent.

**Spec:** `docs/superpowers/specs/2026-09-05-assembly-design.md` — §10 is this plan's whole subject; §1 (shelf life) and §13 (T4) bind it.

## Global Constraints

- **Commit with an explicit pathspec** (`git commit -m "..." -- <files>`; the message must precede `--`, or `-m` is read as a pathspec); parallel sessions share this checkout. Never revert or restore another session's uncommitted files — report the precondition as unmeetable instead.
- Every commit message ends with `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
- Run the offline suite before every commit: `python -m pytest tests -q -n auto`, from the repo root, inside `.venv`. Pass `-n` on the command line, never in addopts.
- `scripts/` is stdlib-only. The package's one runtime dependency (`defusedxml`) is untouched, and no dependency is added anywhere.
- **mdformat owns tracked markdown** except `.superpowers/`, `.worktrees/`, `.claude/worktrees/` and `research_vault/templates/vault/index.md` (`.pre-commit-config.yaml` is the scope authority). In this shared checkout run the form owner directly on touched files — `mdformat --number --wrap keep <files>` — never `pre-commit run`, which stashes onto a stack every worktree shares.
- **Nothing moves, nothing is deleted** (§10). The pass writes one line per document and one file of issue rows. That is its entire footprint.
- **The existing `Status:` line is never touched.** Its vocabulary (`accepted`, `suspended`, `draft`, `APPROVED`, `SUPERSEDED`) is a lifecycle axis this pass has no business overwriting — §2 of the spec depends on ADRs 0004 and 0005 still reading `suspended`.
- **Marker syntax**, minted by this plan (the spec fixes only `Disposition: <value> (<date>)`):
  `Disposition: <value>[: <argument>] (<YYYY-MM-DD>)[ [should-be-scoping-review]]`
  Examples: `Disposition: current (2026-09-05)`; `Disposition: pending-issue: 116 (2026-09-05)`; `Disposition: historical (2026-09-05) [should-be-scoping-review]`.
- **Document vocabulary**, closed, in §10's precedence order: `sibling-project`, `superseded-by`, `pending-issue`, `historical`, `pending-map`, `current`. `superseded-by` and `pending-issue` require an argument; the other four forbid one.
- **Issue vocabulary**, closed: `absorbed-by` (argument is a spec section, `§5.2`-shaped), `superseded`, `still-open`, `pending-map`.
- **`should-be-scoping-review` is an orthogonal flag, not a status.** A document may be `historical` and flagged.
- **Outward-facing actions need explicit go-ahead.** Task 7 comments on and closes six GitHub issues. Do not run it until the user says so in that turn; a plan approval is not that go-ahead.

## Corrected premises

The spec's §10 numbers and its frontmatter rule do not reproduce. All five corrections below are measured 2026-09-05 in this checkout on `main`, and each is re-measured at execution time (§1: a fact older than the lane's start date is re-measured, not cited).

1. **Corpus.** `git ls-files -- "*.md"` returned **213** while this plan was being written and **214** once the plan itself was committed. The spec's 202 is the corpus minus `research_vault/templates/**` (10 files) and `.out-of-scope/**` (1); marking scope is that set minus `CLAUDE.md`, which §10 exempts by name — **202 files at the 2026-09-05 measurement, and still moving**: this plan file is in scope, and so is the `docs/issue-dispositions.md` Task 6 creates. Every count below is that measurement, not a contract; nothing in the code depends on one.
2. **`skills/` frontmatter.** The spec says "all 23 `skills/*/SKILL.md`" open with YAML. `skills/` holds 23 `.md` files of which **9** are `SKILL.md` with frontmatter; the other 14 are `find-sources/references/*.md` and `import-source/references/*.md`, with no frontmatter at all.
3. **Route deviation — no frontmatter key; one uniform body anchor.** All 9 `SKILL.md` carry a `# ` heading immediately after their frontmatter block, so the body anchor reaches every in-scope file. Writing a `disposition:` key would ship a repo-internal marker into the plugin surface a user installs, and would break `tests/test_skill_files.py:20` (`assert "disable-model-invocation: true\n---\n" in text`). **Route cell:** if the author prefers the spec's frontmatter route at plan review, the change is confined to `anchor()` plus a frontmatter write branch in `apply_marker()`, and `tests/test_skill_files.py:20` must be re-cut against the new tail.
4. **Anchor gap.** **25** in-scope files carry no `# ` heading at all — 21 `.superpowers/sdd/2026-08-22-post-q-batch/task-*-brief.md` and 4 `docs/research/**/README.md`. §10's rule ("within the five lines after the first `# ` heading") has no anchor for them, so this plan adds a second case: top of file. The three anchor classes partition the scope exactly — 9 files whose heading follows frontmatter, 25 headingless, 168 heading-first; 9 + 25 + 168 = 202.
5. **Both counted quantities have decayed.** The spec's "25 carry some header status marker" reads **19** files with a status-shaped line in their first 12 lines, and its "66 open issues" reads **30** from `gh issue list`. All six issues §10 names as first to close (#96, #97, #62, #63, #78, #118) and all three it keeps open (#116, #117, #119) are open today.

## File map

- Create: `scripts/dispositions.py` — scope, anchor, marker reader, precedence classifier, proposal emitter, applier, CLI. One file: the four jobs share the anchor rule and the vocabulary, and splitting them would put the constants in a fifth place.
- Create: `tests/test_dispositions.py` — unit tests for the module, then the standing repo-wide linter in the same file (the `tests/test_config_validity.py` pattern: a repo self-check lives in the suite, not in a separate runner).
- Create: `docs/issue-dispositions.md` — the issue half of the pass, written by Task 6.
- Modify: `.gitignore` — one line for the untracked proposal file.
- Modify: every in-scope tracked `.md` file — one added line each, Task 5.

Not created, deliberately: no `research_vault/` module (§11 dispositions verbs against the step map; a maintenance verb would serve none), no CLI verb, no new pre-commit hook (CI already runs `pytest tests`, and a second mechanism for one check is the rule this repo's ladder rejects).

______________________________________________________________________

### Task 1: Scope and the positional marker reader

**Files:**

- Create: `scripts/dispositions.py`
- Create: `tests/test_dispositions.py`

**Interfaces:**

- Consumes: nothing from this plan. `pyproject.toml`'s `pythonpath = ["."]` makes `import scripts.dispositions` resolve under bare `pytest` and `python -m pytest` alike (the `scripts.mutation_gate` precedent).

- Produces: `ROOT: Path`, `WINDOW: int = 5`, `DOCUMENT_VALUES: tuple[str, ...]`, `ARGUMENT_VALUES: frozenset[str]`, `FLAG: str`, `class MarkerError(ValueError)`, `class Marker(NamedTuple)` with fields `value: str, argument: str, date: str, flag: bool`, `in_scope(root: Path = ROOT) -> list[str]`, `anchor(lines: list[str]) -> int`, `read_marker(text: str) -> Marker | None`. Tasks 2–6 all build on `anchor` and `read_marker`.

- [ ] **Step 1: Re-measure the scope before writing anything**

The spec's counts have decayed once already. Run:

```bash
python3 - <<'PY'
import subprocess
files = subprocess.run(["git", "ls-files", "--", "*.md"], capture_output=True, text=True).stdout.split()
excluded = lambda p: p.startswith(("research_vault/templates/", ".out-of-scope/")) or p == "CLAUDE.md"
scope = [p for p in files if not excluded(p)]
frontmatter = [p for p in scope if open(p, encoding="utf-8").read().startswith("---\n")]
headless = [p for p in scope if p not in frontmatter and not any(l.startswith("# ") for l in open(p, encoding="utf-8"))]
print("tracked", len(files), "scope", len(scope), "frontmatter", len(frontmatter), "headless", len(headless))
PY
```

Expected, measured 2026-09-05 with this plan committed: `tracked 214 scope 202 frontmatter 9 headless 25`. If any number differs, the corpus moved — record the new numbers in the commit message for this task and carry on. Nothing in the code depends on the count, and every "201"/"202" printed later in this plan is that same measurement, not a contract.

- [ ] **Step 2: Write the failing tests**

````python
# tests/test_dispositions.py
"""The §10 status-marking pass: the module's unit tests, then the standing linter."""

from pathlib import Path

import pytest

from scripts import dispositions

ROOT = Path(__file__).resolve().parents[1]


def test_scope_excludes_the_three_named_surfaces():
    scope = dispositions.in_scope(ROOT)
    assert "docs/testing.md" in scope
    assert ".superpowers/sdd/2026-08-22-post-q-batch/task-1-brief.md" in scope
    assert "CLAUDE.md" not in scope, "§10 exempts CLAUDE.md by name"
    assert not [p for p in scope if p.startswith("research_vault/templates/")]
    assert not [p for p in scope if p.startswith(".out-of-scope/")]


def test_anchor_is_the_line_after_the_first_heading():
    assert dispositions.anchor(["# Title", "", "Body"]) == 1


def test_anchor_falls_back_to_the_top_when_there_is_no_heading():
    assert dispositions.anchor(["Task 1 brief", "", "Body"]) == 0


def test_anchor_ignores_a_hash_line_inside_a_fence():
    lines = ["```bash", "# not a heading", "```", "", "# Title", ""]
    assert dispositions.anchor(lines) == 5


def test_read_marker_returns_none_when_unmarked():
    assert dispositions.read_marker("# Title\n\nStatus: accepted (2026-08-20)\n") is None


def test_read_marker_reads_value_argument_date_and_flag():
    text = "# Title\n\nDisposition: pending-issue: 116 (2026-09-05)\n\nStatus: suspended\n"
    assert dispositions.read_marker(text) == dispositions.Marker(
        "pending-issue", "116", "2026-09-05", False
    )


def test_read_marker_reads_the_orthogonal_flag():
    text = "# Title\n\nDisposition: historical (2026-09-05) [should-be-scoping-review]\n"
    marker = dispositions.read_marker(text)
    assert (marker.value, marker.flag) == ("historical", True)


def test_read_marker_reads_the_headless_anchor():
    text = "Disposition: historical (2026-09-05)\n\nTask 1 brief\n"
    assert dispositions.read_marker(text).value == "historical"


def test_read_marker_ignores_a_status_line_and_a_body_disposition():
    """The six sdd review files carry `Status: **CONFIRMED.**` per finding."""
    text = (
        "# Title\n\nStatus: **CONFIRMED.**\n\n"
        + "\n" * 20
        + "Disposition: current (2026-09-05)\n"
    )
    assert dispositions.read_marker(text) is None


def test_read_marker_rejects_two_lines_in_the_window():
    text = (
        "# T\n\nDisposition: current (2026-09-05)\n"
        "Disposition: historical (2026-09-05)\n"
    )
    with pytest.raises(dispositions.MarkerError):
        dispositions.read_marker(text)


def test_read_marker_rejects_an_off_vocabulary_value():
    with pytest.raises(dispositions.MarkerError):
        dispositions.read_marker("# T\n\nDisposition: retired (2026-09-05)\n")


def test_read_marker_rejects_a_missing_argument():
    with pytest.raises(dispositions.MarkerError):
        dispositions.read_marker("# T\n\nDisposition: pending-issue (2026-09-05)\n")


def test_read_marker_rejects_an_argument_the_value_forbids():
    with pytest.raises(dispositions.MarkerError):
        dispositions.read_marker("# T\n\nDisposition: current: 116 (2026-09-05)\n")
````

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest tests/test_dispositions.py -q`
Expected: collection error — `ModuleNotFoundError: No module named 'scripts.dispositions'`.

- [ ] **Step 4: Write the minimal implementation**

````python
# scripts/dispositions.py
"""The §10 status-marking pass: scope, read, propose, and apply the Disposition line.

Repo maintenance, not product. Deliberately not a `research_vault` module and not
a CLI verb: §11 dispositions every verb against the step map, and a maintenance
verb would serve none of them.
"""

import re
import subprocess
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]

# Excluded from marking, each for its own reason:
#   research_vault/templates/** ships into a user's vault — a repo-internal
#     marker has no business travelling with the product;
#   .out-of-scope/** declares its disposition by path;
#   CLAUDE.md is an 11-byte import directive, not a document (spec §10).
EXCLUDED_PREFIXES = ("research_vault/templates/", ".out-of-scope/")
EXCLUDED_PATHS = frozenset({"CLAUDE.md"})

WINDOW = 5

DOCUMENT_VALUES = (
    "sibling-project",
    "superseded-by",
    "pending-issue",
    "historical",
    "pending-map",
    "current",
)
ARGUMENT_VALUES = frozenset({"superseded-by", "pending-issue"})
FLAG = "should-be-scoping-review"

_MARKER = re.compile(
    r"^Disposition: (?P<value>[a-z-]+)(?:: (?P<argument>\S+))?"
    r" \((?P<date>\d{4}-\d{2}-\d{2})\)(?P<flag> \[" + FLAG + r"\])?$"
)


class MarkerError(ValueError):
    """A Disposition line that exists but does not parse, or parses off-vocabulary."""


class Marker(NamedTuple):
    value: str
    argument: str
    date: str
    flag: bool


def in_scope(root: Path = ROOT) -> list[str]:
    """Every tracked Markdown file this pass marks, repo-relative and sorted."""
    listing = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--", "*.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split("\n")
    return sorted(
        path
        for path in listing
        if path
        and path not in EXCLUDED_PATHS
        and not path.startswith(EXCLUDED_PREFIXES)
    )


def anchor(lines: list[str]) -> int:
    """The index the marker window opens at: after the first `# ` heading, else 0.

    Fence-aware — a `# ` inside a fenced block is a shell comment, not a heading.
    No file in scope trips that today; new documents arrive without asking.
    """
    fenced = False
    for index, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if not fenced and line.startswith("# "):
            return index + 1
    return 0


def read_marker(text: str) -> Marker | None:
    """The document's marker, or None when it carries none. Raises on malformed."""
    lines = text.split("\n")
    start = anchor(lines)
    found = [
        line
        for line in lines[start : start + WINDOW]
        if line.startswith("Disposition: ")
    ]
    if not found:
        return None
    if len(found) > 1:
        raise MarkerError(f"{len(found)} Disposition lines in the anchor window")
    match = _MARKER.match(found[0])
    if match is None:
        raise MarkerError(f"unparsable Disposition line: {found[0]!r}")
    value = match["value"]
    if value not in DOCUMENT_VALUES:
        raise MarkerError(f"{value!r} is not one of {DOCUMENT_VALUES}")
    argument = match["argument"] or ""
    if (value in ARGUMENT_VALUES) != bool(argument):
        raise MarkerError(f"{value!r} carries argument {argument!r}")
    return Marker(value, argument, match["date"], bool(match["flag"]))
````

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_dispositions.py -q`
Expected: PASS, 13 tests.

- [ ] **Step 6: Run the form owner and the full offline suite**

Run: `ruff format scripts tests && ruff check scripts tests && python -m pytest tests -q -n auto`
Expected: ruff clean; suite green.

- [ ] **Step 7: Commit**

```bash
git add scripts/dispositions.py tests/test_dispositions.py
git commit -m "$(cat <<'MSG'
feat: scope and positional reader for the §10 disposition marker

Three anchor classes partition the marking scope: 9 files whose heading
follows frontmatter, 25 headingless, 168 heading-first. The reader looks only
inside the five-line window so a body `Status: **CONFIRMED.**` cannot be
mistaken for a header marker.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
)" -- scripts/dispositions.py tests/test_dispositions.py
```

______________________________________________________________________

### Task 2: The precedence classifier (tracer T4)

**Files:**

- Modify: `scripts/dispositions.py`
- Modify: `tests/test_dispositions.py`

**Interfaces:**

- Consumes: `anchor`, `WINDOW`, `FLAG`, `DOCUMENT_VALUES` from Task 1.
- Produces: `class Proposal(NamedTuple)` with fields `value: str, argument: str, flag: bool, rule: str`, and `propose(path: str, text: str) -> Proposal`. Task 3 emits these; Task 5's gate reads the `rule` column to see which rule fired.

**Why the classifier is allowed to be imperfect.** Four of §10's six values have a mechanical test (`sibling-project`, `superseded-by`, `pending-issue`, `historical`). The last two do not: "disposition needs the register" and "still binding" are not separable by any signal in the file. So `current` is an explicit allow-list of shipped surfaces and `pending-map` is the residual — an inversion of §10's stated order at that one boundary, and exactly what the author's review in Task 5 exists to settle. Every row carries the `rule` that fired, so a wrong proposal is visible rather than inferred.

- [ ] **Step 1: Write the failing tests**

These are tracer **T4** — the status linter over a hand-marked sample. Per the review, the sample deliberately includes files where two values fit.

```python
# append to tests/test_dispositions.py, after the Task 1 tests


def test_proposal_prefers_sibling_project_over_every_later_rule():
    """Double fit: this file also declares SUPERSEDED in its header window."""
    path = "docs/2026-08-31-proposed-adr-software-development-component-seam.md"
    proposal = dispositions.propose(path, "# Seam\n\nStatus: **SUPERSEDED.**\n")
    assert proposal.value == "sibling-project"


def test_proposal_prefers_superseded_over_historical():
    """Double fit: a closed-workspace path that also declares supersession."""
    path = ".superpowers/sdd/2026-08-22-post-q-batch/task-7-report.md"
    proposal = dispositions.propose(path, "# Task 7\n\nStatus: **SUPERSEDED.**\n")
    assert (proposal.value, proposal.argument) == ("superseded-by", "?")


def test_proposal_prefers_the_named_issue_over_current():
    """Double fit: ADR 0004 is a live decision record AND owned by issue #116."""
    path = "docs/adr/0004-citekey-is-the-only-identity.md"
    text = "# The citekey is the vault's only identity\n\nStatus: suspended (2026-09-03)\n"
    proposal = dispositions.propose(path, text)
    assert (proposal.value, proposal.argument) == ("pending-issue", "116")


def test_proposal_keeps_the_unsuspended_adrs_current():
    path = "docs/adr/0001-vault-outlives-its-tools.md"
    text = "# The vault outlives its tools\n\nStatus: accepted (2026-08-20)\n"
    assert dispositions.propose(path, text).value == "current"


def test_proposal_marks_the_closed_sdd_workspace_historical():
    path = ".superpowers/sdd/2026-08-22-post-q-batch/task-1-brief.md"
    assert dispositions.propose(path, "Task 1 brief\n").value == "historical"


def test_proposal_marks_shipped_surfaces_current():
    skill = "---\nname: publish\n---\n\n# Publish a project\n"
    assert dispositions.propose("skills/publish/SKILL.md", skill).value == "current"
    assert dispositions.propose("docs/agents/issue-tracker.md", "# Issue tracker\n").value == "current"
    assert dispositions.propose("AGENTS.md", "# research-vault\n").value == "current"
    assert dispositions.propose("docs/testing.md", "# Testing instruments\n").value == "current"


def test_proposal_keeps_this_spec_current_and_defaults_the_rest_to_pending_map():
    spec = "docs/superpowers/specs/2026-09-05-assembly-design.md"
    assert dispositions.propose(spec, "# research-vault as an assembly\n").value == "current"
    demoted = "docs/superpowers/specs/2026-08-16-foundation-spec.md"
    proposal = dispositions.propose(demoted, "# Foundation spec\n")
    assert (proposal.value, proposal.rule) == ("pending-map", "residual")


def test_the_scoping_review_flag_is_orthogonal_to_the_value():
    path = "docs/research/harness-audits/2026-08-30-installed-asset-disposition-survey.md"
    proposal = dispositions.propose(path, "# Installed asset disposition survey\n")
    assert (proposal.value, proposal.flag) == ("historical", True)


def test_a_body_supersession_does_not_fire_the_header_rule():
    """task-21-report says SUPERSEDED twice, both far below the window."""
    path = ".superpowers/sdd/2026-08-22-post-q-batch/task-21-report.md"
    text = "# Task 21 report\n\nStatus: **complete**\n" + "\n" * 40 + "**SUPERSEDED by Fix Round 1**\n"
    assert dispositions.propose(path, text).value == "historical"


def test_every_proposal_value_is_in_the_closed_vocabulary():
    for path in dispositions.in_scope(ROOT):
        proposal = dispositions.propose(path, (ROOT / path).read_text(encoding="utf-8"))
        assert proposal.value in dispositions.DOCUMENT_VALUES, path
        assert proposal.rule, f"{path}: proposal carries no rule name"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_dispositions.py -q`
Expected: FAIL with `AttributeError: module 'scripts.dispositions' has no attribute 'propose'`.

- [ ] **Step 3: Write the minimal implementation**

```python
# append to scripts/dispositions.py, after read_marker

# The two documents that self-declare a sibling product, by filename.
_SIBLING = re.compile(r"^docs/\d{4}-\d{2}-\d{2}-proposed-adr-software-development-")
# §10 names these two: their disposition belongs to a tracked issue, not to us.
_PENDING_ISSUE = {
    "docs/adr/0004-citekey-is-the-only-identity.md": "116",
    "docs/adr/0005-better-bibtex-owns-the-bibliography-export.md": "116",
}
# Dated passes that closed. Evidence, never a live decision.
_HISTORICAL_PREFIXES = (
    ".superpowers/sdd/",
    "docs/research/rethink-audits/",
    "docs/research/harness-audits/",
    "docs/research/raw/",
)
# Surfaces that ship or that AGENTS.md points agents at — binding by construction.
_CURRENT_PATHS = frozenset(
    {
        "AGENTS.md",
        "CONTEXT.md",
        "README.md",
        "docs/testing.md",
        "docs/terminology.md",
        "docs/superpowers/specs/2026-09-05-assembly-design.md",
    }
)
_CURRENT_PREFIXES = (
    "skills/",
    "docs/agents/",
    "docs/adr/0001-",
    "docs/adr/0002-",
    "docs/adr/0003-",
)
_SCOPING_REVIEW_HINTS = (
    "survey",
    "analysis",
    "landscape",
    "catalogue",
    "sourcing",
    "prior-art",
    "competitive",
)


class Proposal(NamedTuple):
    value: str
    argument: str
    flag: bool
    rule: str


def _declares_superseded(text: str) -> bool:
    """SUPERSEDED in the anchor window only — the sdd reports say it in their bodies."""
    lines = text.split("\n")
    start = anchor(lines)
    return any("SUPERSEDED" in line for line in lines[start : start + WINDOW])


def propose(path: str, text: str) -> Proposal:
    """§10's precedence order, first match wins, with the rule that fired named.

    `pending-map` and `current` are not mechanically separable, so `current` is
    an allow-list and `pending-map` is the residual. Every residual row is what
    the author's review is for.
    """
    flag = any(hint in path for hint in _SCOPING_REVIEW_HINTS)
    if _SIBLING.match(path):
        return Proposal("sibling-project", "", flag, "sibling-filename")
    if _declares_superseded(text):
        return Proposal("superseded-by", "?", flag, "header-superseded")
    if path in _PENDING_ISSUE:
        return Proposal("pending-issue", _PENDING_ISSUE[path], flag, "spec-named-issue")
    if path.startswith(_HISTORICAL_PREFIXES):
        return Proposal("historical", "", flag, "closed-pass-path")
    if path in _CURRENT_PATHS or path.startswith(_CURRENT_PREFIXES):
        return Proposal("current", "", flag, "shipped-surface")
    return Proposal("pending-map", "", flag, "residual")
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_dispositions.py -q`
Expected: PASS, 23 tests. `?` is the deliberate placeholder for a `superseded-by` target: the classifier can see that a document declares supersession but not what superseded it, and Task 5's linter rejects a `?` that survives review.

- [ ] **Step 5: Run the form owner and the full offline suite**

Run: `ruff format scripts tests && ruff check scripts tests && python -m pytest tests -q -n auto`
Expected: ruff clean; suite green.

- [ ] **Step 6: Commit**

```bash
git add scripts/dispositions.py tests/test_dispositions.py
git commit -m "$(cat <<'MSG'
feat: §10 precedence classifier, with T4's hand-marked double-fit sample

Tracer T4. The sample includes every case where two values fit: a sibling
document that also declares supersession, a closed-workspace report that
declares it, and ADR 0004, which is both a live decision record and issue
#116's to dispose of. Each proposal names the rule that fired.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
)" -- scripts/dispositions.py tests/test_dispositions.py
```

______________________________________________________________________

### Task 3: The `propose` subcommand — emit the reviewable TSV

**Files:**

- Modify: `scripts/dispositions.py`
- Modify: `tests/test_dispositions.py`
- Modify: `.gitignore`

**Interfaces:**

- Consumes: `in_scope`, `propose`, `FLAG` from Tasks 1–2.
- Produces: `HEADER: str`, `class Row(NamedTuple)` with fields `key: str, value: str, argument: str, flag: bool, rule: str, note: str`, `propose_or_existing(path: str, text: str) -> Proposal`, `emit(root: Path = ROOT) -> str`, `parse_rows(text: str) -> list[Row]`, `main(argv: list[str] | None = None) -> int`, and the CLI `python -m scripts.dispositions propose`. Task 4 consumes `parse_rows`; Task 6 adds issue rows to the same file.

**Why TSV and not a markdown table.** The author edits two hundred rows by hand. TSV is column-stable in any editor, is not owned by mdformat, and parses with `str.split("\t")` — no dependency, no ambiguity about escaped pipes. The file is untracked scratch: the markers themselves are the durable record.

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/test_dispositions.py


def test_emit_writes_a_header_and_one_row_per_in_scope_file():
    text = dispositions.emit(ROOT)
    lines = text.rstrip("\n").split("\n")
    assert lines[0] == dispositions.HEADER
    assert len(lines) - 1 == len(dispositions.in_scope(ROOT))
    assert all(line.count("\t") == 5 for line in lines)


def test_emit_round_trips_through_parse_rows():
    rows = dispositions.parse_rows(dispositions.emit(ROOT))
    assert [row.key for row in rows] == dispositions.in_scope(ROOT)
    adr = next(row for row in rows if row.key.endswith("0004-citekey-is-the-only-identity.md"))
    assert (adr.value, adr.argument) == ("pending-issue", "116")
    # `spec-named-issue` before Task 5 marks the corpus, `existing` after it.
    assert adr.rule in ("spec-named-issue", "existing")


def test_emit_keeps_a_marker_the_author_already_approved():
    """Re-running propose over a reviewed corpus must not undo the review."""
    path, text = "docs/product-landscape/zotero.md", "# Zotero\n\nDisposition: current (2026-09-05)\n"
    assert dispositions.propose(path, text).value == "pending-map"
    assert dispositions.propose_or_existing(path, text) == dispositions.Proposal(
        "current", "", False, "existing"
    )


def test_parse_rows_reads_the_flag_column_as_a_boolean():
    text = (
        dispositions.HEADER
        + "\ndocs/a.md\thistorical\t\tshould-be-scoping-review\tclosed-pass-path\t"
        + "\ndocs/b.md\tcurrent\t\t\tshipped-surface\t\n"
    )
    rows = dispositions.parse_rows(text)
    assert [row.flag for row in rows] == [True, False]


def test_parse_rows_rejects_an_off_vocabulary_flag_column():
    text = dispositions.HEADER + "\ndocs/a.md\thistorical\t\tmaybe\tclosed-pass-path\t\n"
    with pytest.raises(dispositions.MarkerError):
        dispositions.parse_rows(text)


def test_propose_subcommand_writes_the_file(tmp_path, capsys):
    target = tmp_path / "proposal.tsv"
    assert dispositions.main(["propose", "--out", str(target)]) == 0
    assert target.read_text(encoding="utf-8").startswith(dispositions.HEADER)
    assert "rows" in capsys.readouterr().out
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_dispositions.py -q`
Expected: FAIL with `AttributeError: module 'scripts.dispositions' has no attribute 'emit'`.

- [ ] **Step 3: Write the minimal implementation**

```python
# append to scripts/dispositions.py

HEADER = "key\tvalue\targument\tflag\trule\tnote"


class Row(NamedTuple):
    key: str
    value: str
    argument: str
    flag: bool
    rule: str
    note: str


def propose_or_existing(path: str, text: str) -> Proposal:
    """A marker already in the file wins over the classifier.

    `propose` is pure, so re-emitting over a corpus the author has already
    reviewed would hand back the classifier's guesses and the next `apply`
    would quietly undo the review. The file is the record; the classifier only
    fills blanks. This is also what makes re-running `propose` mid-review safe.
    """
    marker = read_marker(text)
    if marker is None:
        return propose(path, text)
    return Proposal(marker.value, marker.argument, marker.flag, "existing")


def emit(root: Path = ROOT) -> str:
    """One reviewable row per in-scope document, header first."""
    lines = [HEADER]
    for path in in_scope(root):
        proposal = propose_or_existing(path, (root / path).read_text(encoding="utf-8"))
        lines.append(
            "\t".join(
                [
                    path,
                    proposal.value,
                    proposal.argument,
                    FLAG if proposal.flag else "",
                    proposal.rule,
                    "",
                ]
            )
        )
    return "\n".join(lines) + "\n"


def parse_rows(text: str) -> list[Row]:
    """The reviewed file back into rows. The author's edits are the authority."""
    rows = []
    for line in text.split("\n"):
        if not line or line == HEADER:
            continue
        fields = line.split("\t")
        if len(fields) != 6:
            raise MarkerError(f"{len(fields)} columns, expected 6: {line!r}")
        key, value, argument, flag, rule, note = fields
        if flag not in ("", FLAG):
            raise MarkerError(f"flag column is {flag!r}, expected '' or {FLAG!r}")
        rows.append(Row(key, value, argument, flag == FLAG, rule, note))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.dispositions")
    sub = parser.add_subparsers(dest="command", required=True)
    propose_cmd = sub.add_parser("propose", help="write the reviewable proposal")
    propose_cmd.add_argument("--out", default="disposition-proposal.tsv")
    args = parser.parse_args(argv)
    if args.command == "propose":
        text = emit()
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"proposed {len(parse_rows(text))} rows to {args.out}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

Add `import argparse` and `import sys` to the module's import block.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_dispositions.py -q`
Expected: PASS, 28 tests.

- [ ] **Step 5: Ignore the scratch proposal**

```bash
printf 'disposition-proposal.tsv\n' >> .gitignore
```

- [ ] **Step 6: Run the form owner and the full offline suite**

Run: `ruff format scripts tests && ruff check scripts tests && python -m pytest tests -q -n auto`
Expected: ruff clean; suite green.

- [ ] **Step 7: Commit**

```bash
git add scripts/dispositions.py tests/test_dispositions.py .gitignore
git commit -m "$(cat <<'MSG'
feat: emit the reviewable disposition proposal as TSV

The proposal is the approval gate's surface: the author edits any cell and
apply is mechanical from the edited file, so no judgement is ever the
classifier's alone. Untracked — the markers are the durable record.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
)" -- scripts/dispositions.py tests/test_dispositions.py .gitignore
```

______________________________________________________________________

### Task 4: The `apply` subcommand — write markers from the reviewed file

**Files:**

- Modify: `scripts/dispositions.py`
- Modify: `tests/test_dispositions.py`

**Interfaces:**

- Consumes: `anchor`, `read_marker`, `parse_rows`, `Row`, `WINDOW`, `FLAG`, `ARGUMENT_VALUES`, `DOCUMENT_VALUES`.

- Produces: `marker_line(value: str, argument: str, flag: bool, date: str) -> str`, `apply_marker(text: str, line: str) -> str`, `apply_rows(rows: list[Row], root: Path = ROOT, date: str = "") -> list[str]` (returns the repo-relative paths written), and the CLI `python -m scripts.dispositions apply <file> [--date YYYY-MM-DD]`. Task 5 runs the CLI; Task 6 extends `apply_rows` to route `issue:` keys.

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/test_dispositions.py


def test_marker_line_renders_every_shape():
    assert dispositions.marker_line("current", "", False, "2026-09-05") == (
        "Disposition: current (2026-09-05)"
    )
    assert dispositions.marker_line("pending-issue", "116", False, "2026-09-05") == (
        "Disposition: pending-issue: 116 (2026-09-05)"
    )
    assert dispositions.marker_line("historical", "", True, "2026-09-05") == (
        "Disposition: historical (2026-09-05) [should-be-scoping-review]"
    )


def test_marker_line_rejects_a_row_the_reader_would_reject():
    with pytest.raises(dispositions.MarkerError):
        dispositions.marker_line("pending-issue", "", False, "2026-09-05")
    with pytest.raises(dispositions.MarkerError):
        dispositions.marker_line("retired", "", False, "2026-09-05")


def test_apply_marker_inserts_a_paragraph_after_the_heading():
    text = "# The vault outlives its tools\n\nStatus: accepted (2026-08-20)\n\nBody.\n"
    out = dispositions.apply_marker(text, "Disposition: current (2026-09-05)")
    assert out == (
        "# The vault outlives its tools\n\n"
        "Disposition: current (2026-09-05)\n\n"
        "Status: accepted (2026-08-20)\n\nBody.\n"
    )
    assert dispositions.read_marker(out).value == "current"


def test_apply_marker_inserts_at_the_top_of_a_headless_file():
    text = "Task 1 brief\n\nBody.\n"
    out = dispositions.apply_marker(text, "Disposition: historical (2026-09-05)")
    assert out == "Disposition: historical (2026-09-05)\n\nTask 1 brief\n\nBody.\n"


def test_apply_marker_is_idempotent_and_replaces_in_place():
    text = "# T\n\nStatus: accepted (2026-08-20)\n"
    once = dispositions.apply_marker(text, "Disposition: current (2026-09-05)")
    twice = dispositions.apply_marker(once, "Disposition: current (2026-09-05)")
    assert once == twice
    changed = dispositions.apply_marker(once, "Disposition: historical (2026-09-05)")
    assert dispositions.read_marker(changed).value == "historical"
    assert changed.count("Disposition: ") == 1


def test_apply_marker_never_touches_the_status_line():
    text = "# The citekey\n\nStatus: suspended (2026-09-03) — under re-derivation.\n"
    out = dispositions.apply_marker(text, "Disposition: pending-issue: 116 (2026-09-05)")
    assert "Status: suspended (2026-09-03) — under re-derivation." in out


def test_apply_rows_writes_only_the_rows_it_is_given(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("# A\n\nBody.\n", encoding="utf-8")
    (tmp_path / "docs" / "b.md").write_text("# B\n\nBody.\n", encoding="utf-8")
    rows = [dispositions.Row("docs/a.md", "current", "", False, "shipped-surface", "")]
    written = dispositions.apply_rows(rows, root=tmp_path, date="2026-09-05")
    assert written == ["docs/a.md"]
    assert "Disposition: " in (tmp_path / "docs" / "a.md").read_text(encoding="utf-8")
    assert "Disposition: " not in (tmp_path / "docs" / "b.md").read_text(encoding="utf-8")


def test_apply_rows_rejects_an_unresolved_superseded_target(tmp_path):
    (tmp_path / "a.md").write_text("# A\n", encoding="utf-8")
    rows = [dispositions.Row("a.md", "superseded-by", "?", False, "header-superseded", "")]
    with pytest.raises(dispositions.MarkerError):
        dispositions.apply_rows(rows, root=tmp_path, date="2026-09-05")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_dispositions.py -q`
Expected: FAIL with `AttributeError: module 'scripts.dispositions' has no attribute 'marker_line'`.

- [ ] **Step 3: Write the minimal implementation**

```python
# append to scripts/dispositions.py, before main()


def marker_line(value: str, argument: str, flag: bool, date: str) -> str:
    """Render one marker, rejecting anything read_marker would reject."""
    if value not in DOCUMENT_VALUES:
        raise MarkerError(f"{value!r} is not one of {DOCUMENT_VALUES}")
    if (value in ARGUMENT_VALUES) != bool(argument):
        raise MarkerError(f"{value!r} carries argument {argument!r}")
    if argument == "?":
        raise MarkerError(f"{value!r} still carries the unreviewed '?' target")
    rendered = f"Disposition: {value}"
    if argument:
        rendered += f": {argument}"
    rendered += f" ({date})"
    if flag:
        rendered += f" [{FLAG}]"
    return rendered


def apply_marker(text: str, line: str) -> str:
    """Write the marker at its anchor, replacing one already in the window."""
    lines = text.split("\n")
    start = anchor(lines)
    for index in range(start, min(start + WINDOW, len(lines))):
        if lines[index].startswith("Disposition: "):
            lines[index] = line
            return "\n".join(lines)
    prefix, rest = lines[:start], lines[start:]
    if rest and rest[0] == "":
        rest = rest[1:]
    block = ([""] if prefix else []) + [line, ""]
    return "\n".join(prefix + block + rest)


def apply_rows(rows: list[Row], root: Path = ROOT, date: str = "") -> list[str]:
    """Write every document row. Returns the repo-relative paths touched."""
    date = date or _dt.date.today().isoformat()
    tracked = set(in_scope(root)) if root == ROOT else None
    written = []
    for row in rows:
        line = marker_line(row.value, row.argument, row.flag, date)
        if row.value == "superseded-by" and tracked is not None:
            if row.argument not in tracked:
                raise MarkerError(f"{row.key}: superseded-by target {row.argument!r} does not resolve")
        path = root / row.key
        path.write_text(apply_marker(path.read_text(encoding="utf-8"), line), encoding="utf-8")
        written.append(row.key)
    return written
```

Add `import datetime as _dt` to the module's import block, and extend `main`:

```python
    apply_cmd = sub.add_parser("apply", help="write markers from a reviewed proposal")
    apply_cmd.add_argument("proposal")
    apply_cmd.add_argument("--date", default="")
```

```python
    if args.command == "apply":
        rows = parse_rows(Path(args.proposal).read_text(encoding="utf-8"))
        written = apply_rows(rows, date=args.date)
        print(f"marked {len(written)} documents from {args.proposal}")
        return 0
```

`marker_line` rejects `?` before any file is touched, and `apply_rows` renders every line before its first write only in the sense that each row fails on its own — so a bad row leaves earlier rows written. That is deliberate: the run is idempotent and re-runnable, and stopping at the offending row names it.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_dispositions.py -q`
Expected: PASS, 36 tests.

- [ ] **Step 5: Run the form owner and the full offline suite**

Run: `ruff format scripts tests && ruff check scripts tests && python -m pytest tests -q -n auto`
Expected: ruff clean; suite green.

- [ ] **Step 6: Commit**

```bash
git add scripts/dispositions.py tests/test_dispositions.py
git commit -m "$(cat <<'MSG'
feat: apply reviewed disposition rows, idempotently, without touching Status

The applier writes one paragraph at the anchor and replaces an existing marker
in place, so a re-run after an edited proposal converges instead of stacking.
An unreviewed '?' supersession target is rejected before any file is written.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
)" -- scripts/dispositions.py tests/test_dispositions.py
```

______________________________________________________________________

### Task 5: The standing linter, and the marking sweep behind the author's gate

**Files:**

- Modify: `tests/test_dispositions.py`
- Modify: every in-scope tracked `.md` file (one line each — 202 at the 2026-09-05 measurement)

**Interfaces:**

- Consumes: everything Tasks 1–4 produce.
- Produces: nothing new in code. Produces the marked corpus, and a linter that from here on refuses an unmarked or malformed document.

This is the task with the human gate in it. The linter is written first and fails — no in-scope file carries a marker yet. The "implementation" that makes it pass is the corpus the author approved.

- [ ] **Step 1: Write the failing linter**

```python
# append to tests/test_dispositions.py

# ---------------------------------------------------------------------------
# The standing linter. Everything above tests the module; everything below
# tests the repository, per §10's rule that a mechanical process gets a
# mechanical check.
# ---------------------------------------------------------------------------


def _markers() -> dict[str, dispositions.Marker | None]:
    markers = {}
    for path in dispositions.in_scope(ROOT):
        try:
            markers[path] = dispositions.read_marker((ROOT / path).read_text(encoding="utf-8"))
        except dispositions.MarkerError as error:
            # read_marker never sees a path; without this the linter's failure
            # says what is wrong and not which of two hundred files it is wrong in.
            raise dispositions.MarkerError(f"{path}: {error}") from error
    return markers


def test_every_in_scope_document_carries_exactly_one_marker():
    unmarked = sorted(path for path, marker in _markers().items() if marker is None)
    assert not unmarked, f"{len(unmarked)} document(s) carry no Disposition line: {unmarked[:10]}"


def test_every_superseded_by_target_resolves():
    tracked = set(dispositions.in_scope(ROOT))
    broken = [
        (path, marker.argument)
        for path, marker in _markers().items()
        if marker and marker.value == "superseded-by" and marker.argument not in tracked
    ]
    assert not broken, f"superseded-by targets that do not resolve: {broken}"


def test_every_pending_issue_argument_is_an_issue_number():
    bad = [
        (path, marker.argument)
        for path, marker in _markers().items()
        if marker and marker.value == "pending-issue" and not marker.argument.isdigit()
    ]
    assert not bad, f"pending-issue arguments that are not issue numbers: {bad}"
```

Malformed markers need no test of their own: `read_marker` raises `MarkerError`, which fails the collecting test with the offending file named.

- [ ] **Step 2: Run the linter to verify it fails**

Run: `python -m pytest tests/test_dispositions.py -q`
Expected: FAIL — `AssertionError: 202 document(s) carry no Disposition line` (the count is whatever Step 1 measured).

- [ ] **Step 3: Generate the proposal**

```bash
python -m scripts.dispositions propose
wc -l disposition-proposal.tsv
cut -f2 disposition-proposal.tsv | sort | uniq -c | sort -rn
cut -f5 disposition-proposal.tsv | sort | uniq -c | sort -rn
```

Expected: one header line plus one row per in-scope file (203 lines at the 2026-09-05 measurement), and a value histogram dominated by `historical` (the 71 `.superpowers/sdd/` files plus the dated research passes) and `pending-map` (the residual).

Learn mdformat's baseline in the same breath, because `.git/hooks/` holds only samples — no local hook has ever enforced the formatter, so some tracked files may already be unclean and Step 6's reflow gate would fire on that pre-existing debt rather than on this pass:

```bash
mdformat --check --number --wrap keep $(cut -f1 disposition-proposal.tsv | tail -n +2 | grep -v "^\.superpowers/") 2>&1 | tail -20
```

Record which files it names. Those, and only those, are permitted to reflow in Step 6.

- [ ] **Step 4: STOP — hand the proposal to the author**

**This is the approval gate. Do not proceed without it.** Post the value histogram and the rule histogram, then say:

> `disposition-proposal.tsv` holds one row per in-scope document (202 at the 2026-09-05 measurement). Columns: `key`, `value`, `argument`, `flag`, `rule`, `note`. Edit any of `value`, `argument`, `flag` — apply is mechanical from what you leave behind. Three things worth your eye: every row whose `rule` is `residual` is the classifier declining to guess between `pending-map` and `current`; every `superseded-by` row carries `?` as its target and will be rejected until you name the superseding path; and the `should-be-scoping-review` flag is a proposal from a filename hint, not a reading.

Wait for the edited file. The asymmetry that makes this gate load-bearing: **mis-marking a current document as `historical` makes the §8 cold-start contract refuse it later, and nobody will know why** — doctor fails if the reading list points at anything `historical` or `pending-map`. A wrong `current` is visible; a wrong `historical` is silent.

- [ ] **Step 5: Apply the reviewed proposal**

```bash
python -m scripts.dispositions apply disposition-proposal.tsv
marked=$(cut -f1 disposition-proposal.tsv | tail -n +2)
git status --porcelain -- $marked | wc -l
```

Expected: `marked <N> documents from disposition-proposal.tsv` for the N that Step 3 counted, and N modified files. The `$marked` pathspec is the proposal's own key column — never `git diff --name-only` over the whole tree, which in this shared checkout would sweep up another session's uncommitted work. If `apply` raises `MarkerError`, it names the offending row — fix that row in the TSV and re-run; the applier is idempotent.

- [ ] **Step 6: Run the form owner over the mdformat-owned subset**

`.superpowers/` is outside mdformat's scope (`.pre-commit-config.yaml`), so only the rest is reformatted:

```bash
marked=$(cut -f1 disposition-proposal.tsv | tail -n +2)   # shell state does not survive between steps
mdformat --number --wrap keep $(printf '%s\n' $marked | grep -v "^\.superpowers/")
git diff --stat -- $marked | tail -1
```

Expected: the diff stays at roughly one added line per file. **If mdformat reflows unrelated prose in any file, stop** — inspect with `git diff <file>`, and if the reflow is real, report it before committing. `--wrap keep` should prevent it; this step is the check that it did.

- [ ] **Step 7: Run the linter and the full offline suite**

Run: `python -m pytest tests -q -n auto`
Expected: green, including the three linter tests.

- [ ] **Step 8: Commit**

```bash
marked=$(cut -f1 disposition-proposal.tsv | tail -n +2)   # re-derived: each block is its own shell
git add -- $marked tests/test_dispositions.py
git commit -m "$(cat <<'MSG'
feat: mark every in-scope document with its §10 disposition

Every in-scope document carries one Disposition line, from an author-reviewed proposal.
The existing Status: line is untouched — it carries a lifecycle axis this pass
has no business overwriting, and §2 depends on ADRs 0004 and 0005 still
reading suspended.

The linter now refuses an unmarked or malformed document, an unresolved
superseded-by target, and a non-numeric pending-issue argument.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
)" -- $marked tests/test_dispositions.py
```

______________________________________________________________________

### Task 6: Issue dispositions

**Files:**

- Modify: `scripts/dispositions.py`
- Modify: `tests/test_dispositions.py`
- Create: `docs/issue-dispositions.md`

**Interfaces:**

- Consumes: `Row`, `parse_rows`, `emit`, `main`, `MarkerError`.
- Produces: `ISSUE_VALUES: tuple[str, ...]`, `ISSUE_TABLE: str = "docs/issue-dispositions.md"`, `propose_issue(number: int) -> Proposal`, `render_issue_table(rows: list[Row]) -> str`, `read_issue_table(text: str) -> list[Row]`, `emit(root, issues=None)` extended with an `issues` parameter, and `python -m scripts.dispositions propose --issues-json <file>`.

**Why a file and not labels.** The linter runs offline in the suite; it cannot call `gh`. A committed table is a fact the linter can read, and it is also the durable record §10 asks for — the label surface is triage state, a different axis (`docs/agents/triage-labels.md`).

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/test_dispositions.py, above the linter section


def test_propose_issue_uses_the_spec_named_dispositions():
    assert dispositions.propose_issue(96) == dispositions.Proposal(
        "absorbed-by", "§6", False, "spec-named-absorbed"
    )
    assert dispositions.propose_issue(116).value == "still-open"
    assert dispositions.propose_issue(94) == dispositions.Proposal(
        "pending-map", "", False, "residual"
    )


def test_emit_appends_issue_rows_with_the_title_as_the_note():
    issues = [{"number": 96, "title": "Distribution model for the recommended plugin bucket"}]
    rows = dispositions.parse_rows(dispositions.emit(ROOT, issues=issues))
    issue_rows = [row for row in rows if row.key.startswith("issue:")]
    assert len(issue_rows) == 1
    assert issue_rows[0].key == "issue:96"
    assert issue_rows[0].note == "Distribution model for the recommended plugin bucket"


def test_render_and_read_the_issue_table_round_trip():
    rows = [
        dispositions.Row("issue:96", "absorbed-by", "§6", False, "spec-named-absorbed", "Distribution model"),
        dispositions.Row("issue:116", "still-open", "", False, "spec-named-open", "Land the vocabulary"),
    ]
    text = dispositions.render_issue_table(rows)
    assert text.startswith("# Issue dispositions\n")
    assert dispositions.read_issue_table(text) == rows


def test_read_issue_table_tolerates_mdformat_column_padding():
    """mdformat pads table cells; render_issue_table does not. Measured 2026-09-05."""
    text = (
        "# Issue dispositions\n\n"
        "| Issue | Disposition     | Title |\n"
        "| ----- | --------------- | ----- |\n"
        "| 96    | absorbed-by: §6 | X     |\n"
    )
    assert dispositions.read_issue_table(text) == [
        dispositions.Row("issue:96", "absorbed-by", "§6", False, "spec-named-absorbed", "X")
    ]


def test_read_issue_table_rejects_an_off_vocabulary_disposition():
    text = dispositions.render_issue_table(
        [dispositions.Row("issue:96", "absorbed-by", "§6", False, "r", "t")]
    ).replace("absorbed-by: §6", "retired")
    with pytest.raises(dispositions.MarkerError):
        dispositions.read_issue_table(text)


def test_apply_rows_writes_the_issue_table_and_no_file_named_issue(tmp_path):
    (tmp_path / "docs").mkdir()
    rows = [dispositions.Row("issue:96", "absorbed-by", "§6", False, "spec-named-absorbed", "Distribution model")]
    written = dispositions.apply_rows(rows, root=tmp_path, date="2026-09-05")
    assert written == [dispositions.ISSUE_TABLE]
    assert "| 96 |" in (tmp_path / dispositions.ISSUE_TABLE).read_text(encoding="utf-8")
```

And, in the linter section:

```python
def test_the_issue_table_is_well_formed():
    rows = dispositions.read_issue_table((ROOT / dispositions.ISSUE_TABLE).read_text(encoding="utf-8"))
    numbers = [row.key for row in rows]
    assert len(numbers) == len(set(numbers)), "duplicate issue rows"
    for row in rows:
        assert row.value in dispositions.ISSUE_VALUES, row
        assert bool(row.argument) == (row.value == "absorbed-by"), row
        if row.value == "absorbed-by":
            assert row.argument.startswith("§"), row


@pytest.mark.live_net
@pytest.mark.skipif(shutil.which("gh") is None, reason="gh CLI absent")
def test_the_issue_table_covers_every_open_issue():
    listed = subprocess.run(
        ["gh", "issue", "list", "--state", "open", "--limit", "300", "--json", "number"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if listed.returncode != 0:
        pytest.skip(f"gh unusable: {listed.stderr.strip()[:120]}")
    open_numbers = {f"issue:{item['number']}" for item in json.loads(listed.stdout)}
    covered = {row.key for row in dispositions.read_issue_table((ROOT / dispositions.ISSUE_TABLE).read_text(encoding="utf-8"))}
    assert not open_numbers - covered, f"open issues with no disposition: {sorted(open_numbers - covered)}"
```

Add `import json`, `import shutil` and `import subprocess` to the test module's imports. `tests/conftest.py:165` already skips anything marked `live_net` unless `RV_LIVE_NET=1`, so this leg stays out of the default offline run and out of CI — the repo's posture for anything that touches an external API.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_dispositions.py -q`
Expected: FAIL with `AttributeError: module 'scripts.dispositions' has no attribute 'propose_issue'`.

- [ ] **Step 3: Write the minimal implementation**

```python
# append to scripts/dispositions.py

ISSUE_VALUES = ("absorbed-by", "superseded", "still-open", "pending-map")
ISSUE_TABLE = "docs/issue-dispositions.md"

# §10 names these six as the first to close against the assembly spec, and
# these three as staying open (§2, §4, §7.3). Sections are this plan's reading
# of where each issue's subject now lives; the author's review is the authority.
_ABSORBED = {96: "§6", 97: "§5.2", 62: "§9", 63: "§9", 78: "§9", 118: "§5"}
_STILL_OPEN = frozenset({116, 117, 119})

# mdformat's `tables` extension pads every cell to the column width (measured
# 2026-09-05: `| 96    | absorbed-by: §6 | X     |`), so the reader tolerates
# padding even though the renderer emits none.
_TABLE_ROW = re.compile(
    r"^\|\s*(?P<number>\d+)\s*\|\s*(?P<disposition>[^|]+?)\s*\|\s*(?P<title>[^|]*?)\s*\|$"
)

_TABLE_PREAMBLE = """# Issue dispositions

Disposition: current (%(date)s)

Written by the status-marking pass of `docs/superpowers/specs/2026-09-05-assembly-design.md`
§10 and maintained by `scripts/dispositions.py`. One row per open issue.
Vocabulary: `absorbed-by: <spec §>`, `superseded`, `still-open`, `pending-map`.
`tests/test_dispositions.py` refuses an off-vocabulary row and, where `gh` is
usable, an open issue with no row.

| Issue | Disposition | Title |
| --- | --- | --- |
"""


def propose_issue(number: int) -> Proposal:
    if number in _ABSORBED:
        return Proposal("absorbed-by", _ABSORBED[number], False, "spec-named-absorbed")
    if number in _STILL_OPEN:
        return Proposal("still-open", "", False, "spec-named-open")
    return Proposal("pending-map", "", False, "residual")


def render_issue_table(rows: list[Row], date: str = "") -> str:
    date = date or _dt.date.today().isoformat()
    lines = [_TABLE_PREAMBLE % {"date": date}]
    for row in sorted(rows, key=lambda row: -int(row.key.removeprefix("issue:"))):
        disposition = row.value + (f": {row.argument}" if row.argument else "")
        lines.append(f"| {row.key.removeprefix('issue:')} | {disposition} | {row.note} |\n")
    return "".join(lines)


def read_issue_table(text: str) -> list[Row]:
    rows = []
    for line in text.split("\n"):
        match = _TABLE_ROW.match(line)
        if match is None:  # the header and separator rows carry no digits
            continue
        disposition = match["disposition"].strip()
        value, _, argument = disposition.partition(": ")
        if value not in ISSUE_VALUES:
            raise MarkerError(f"{value!r} is not one of {ISSUE_VALUES}")
        rule = "spec-named-absorbed" if value == "absorbed-by" else (
            "spec-named-open" if value == "still-open" else "residual"
        )
        rows.append(Row(f"issue:{match['number']}", value, argument, False, rule, match["title"].strip()))
    return rows
```

Extend `emit` with the issue half:

```python
def emit(root: Path = ROOT, issues: list[dict] | None = None) -> str:
    ...  # documents exactly as before, then:
    for issue in issues or []:
        proposal = propose_issue(int(issue["number"]))
        lines.append(
            "\t".join(
                [
                    f"issue:{issue['number']}",
                    proposal.value,
                    proposal.argument,
                    "",
                    proposal.rule,
                    issue["title"],
                ]
            )
        )
    return "\n".join(lines) + "\n"
```

Route `issue:` keys in `apply_rows`, before the document loop:

```python
    issue_rows = [row for row in rows if row.key.startswith("issue:")]
    document_rows = [row for row in rows if not row.key.startswith("issue:")]
    ...  # the document loop, over document_rows
    if issue_rows:
        (root / ISSUE_TABLE).write_text(render_issue_table(issue_rows, date), encoding="utf-8")
        written.append(ISSUE_TABLE)
```

And add `--issues-json` to the `propose` subcommand:

```python
    propose_cmd.add_argument("--issues-json", default="")
```

```python
        issues = json.loads(Path(args.issues_json).read_text(encoding="utf-8")) if args.issues_json else None
        text = emit(issues=issues)
```

Add `import json` to the module's import block.

`ISSUE_TABLE` is itself an in-scope document, so it carries its own `Disposition: current` line inside the preamble, two lines under the heading — inside the window, and written by the same renderer that writes the table.

- [ ] **Step 4: Run the tests to verify the unit half passes**

Run: `python -m pytest tests/test_dispositions.py -q -k "issue"`
Expected: the five unit tests PASS; `test_the_issue_table_is_well_formed` FAILS with `FileNotFoundError` — the table does not exist yet.

- [ ] **Step 5: Generate the issue proposal**

```bash
gh issue list --state open --limit 300 --json number,title > /tmp/open-issues.json
jq length /tmp/open-issues.json
python -m scripts.dispositions propose --issues-json /tmp/open-issues.json
grep -c '^issue:' disposition-proposal.tsv
grep '^issue:' disposition-proposal.tsv | cut -f2 | sort | uniq -c
```

Expected: 30 open issues, measured 2026-09-05 — six `absorbed-by`, three `still-open`, the rest `pending-map`. A different count means the tracker moved; carry the new number.

- [ ] **Step 6: STOP — hand the issue rows to the author**

**Second approval gate.** Show the 30 issue rows and say:

> Nine rows carry a spec-named proposal; the other 21 default to `pending-map`. The six `absorbed-by` rows are the ones §10 says close against this spec, and the section each cites is this plan's reading of where the subject now lives — check §5.2 for #97 and §9 for #62, #63 and #78 in particular. Nothing is closed by applying this: the table is a file. Closing happens in the next task, and only when you say so.

- [ ] **Step 7: Apply, format, and verify**

```bash
python -m scripts.dispositions apply disposition-proposal.tsv
mdformat --number --wrap keep docs/issue-dispositions.md
python -m pytest tests -q -n auto
```

Expected: `docs/issue-dispositions.md` written; suite green, including `test_the_issue_table_covers_every_open_issue` (it runs, rather than skipping, wherever `gh` is authenticated).

- [ ] **Step 8: Commit**

```bash
git add scripts/dispositions.py tests/test_dispositions.py docs/issue-dispositions.md
git commit -m "$(cat <<'MSG'
feat: disposition every open issue in a linted table

The linter runs offline and cannot call gh, so the dispositions live in a
committed file it can read; the gh-backed coverage check runs where gh is
usable and skips where it is not. Applying this closes nothing — the table is
a file, and closing is a separate, gated act.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
)" -- scripts/dispositions.py tests/test_dispositions.py docs/issue-dispositions.md
```

______________________________________________________________________

### Task 7: Close the six absorbed issues — comment first, then close

**Files:** none. This task writes only to GitHub.

**Interfaces:**

- Consumes: `docs/issue-dispositions.md` as committed by Task 6.
- Produces: six closed issues, each carrying a comment that names what absorbed it.

**This task is outward-facing and is not casually reversible.** A closed issue is visible to anyone watching the repository, and the repository is scheduled to go public (§12). Per `docs/agents/issue-tracker.md`, a position is tracked, not just an outcome — so each issue gets a comment naming the absorbing section *before* it is closed, and the comment is what a reader lands on.

**Why these six and not others:** #96, #97, #62, #63, #78 and #118 each restate a question the assembly spec now answers. Left open, they send a parallel session down a path this spec already closed.

- [ ] **Step 1: STOP — ask for the go-ahead in this turn**

Do not run any `gh` write before the user says to, in the turn this task runs. Plan approval is not this go-ahead. Show the six rows from `docs/issue-dispositions.md` and the exact comment text below, then ask.

- [ ] **Step 2: Verify each issue is still open and still says what the table says**

```bash
for n in 62 63 78 96 97 118; do
  gh issue view "$n" --json number,state,title --jq '"\(.number) \(.state) \(.title)"'
done
```

Expected: six `OPEN` rows. If any is already closed, drop it from step 3 and say so — do not reopen.

- [ ] **Step 3: Comment, then close, one issue at a time**

`gh issue close --comment` posts the comment and closes in one call, which is the house idiom (`docs/agents/issue-tracker.md`) and leaves the reader landing on the reason. Run these as six separate calls, each in its own block — no shell function, because shell state does not survive between tool calls, and no loop, so a failure stops at a named issue.

```bash
gh issue close 96 --comment "Absorbed by the assembly spec §6 (\`docs/superpowers/specs/2026-09-05-assembly-design.md\`), which fixes the component classes and how each is pinned. Recorded in \`docs/issue-dispositions.md\` by the §10 status-marking pass. Reopen if §6 turns out not to answer this."
```

```bash
gh issue close 97 --comment "Absorbed by the assembly spec §5.2 (\`docs/superpowers/specs/2026-09-05-assembly-design.md\`), which sets the adopt/adapt/build bar and what a build verdict must record. Recorded in \`docs/issue-dispositions.md\`. Reopen if §5.2 turns out not to answer this."
```

```bash
gh issue close 62 --comment "Absorbed by the assembly spec §9 (\`docs/superpowers/specs/2026-09-05-assembly-design.md\`), which fixes setup, doctor and drift as one mechanism over four component classes. Recorded in \`docs/issue-dispositions.md\`. Reopen if §9 turns out not to answer this."
```

```bash
gh issue close 63 --comment "Absorbed by the assembly spec §9 (\`docs/superpowers/specs/2026-09-05-assembly-design.md\`), which gives each class its own drift leg. Recorded in \`docs/issue-dispositions.md\`. Reopen if §9 turns out not to answer this."
```

```bash
gh issue close 78 --comment "Absorbed by the assembly spec §9 (\`docs/superpowers/specs/2026-09-05-assembly-design.md\`), which extends the existing doctor rather than starting a second one, in a read-only --check-only mode. Recorded in \`docs/issue-dispositions.md\`. Reopen if §9 turns out not to answer this."
```

```bash
gh issue close 118 --comment "Absorbed by the assembly spec §5 (\`docs/superpowers/specs/2026-09-05-assembly-design.md\`), whose component register is where a component's disposition is now recorded. Recorded in \`docs/issue-dispositions.md\`. Reopen if §5 turns out not to answer this."
```

If the author edited a section in Task 6's gate, use the edited value from `docs/issue-dispositions.md`, not the value above.

- [ ] **Step 4: Re-run the coverage linter**

Closing six issues shrinks the open set, and the table now carries rows for issues that are closed. That is correct and the linter permits it — `test_the_issue_table_covers_every_open_issue` asserts `open_numbers - covered` is empty, not that the two sets are equal.

Run: `python -m pytest tests/test_dispositions.py -q`
Expected: green.

- [ ] **Step 5: Report, with no commit**

There is nothing to commit — this task's whole footprint is on GitHub. Report which issues closed, which (if any) were already closed, and the remaining open count from `gh issue list --state open --json number --jq length`.

______________________________________________________________________

## What this plan does not do

Named so the next session does not go looking:

- **The register (§5), lane 0 (§7.0), doctor (§9), the code audit (§11), the cutover (§12) and lanes 1–4.** Separate plans. §8's cold-start contract reads `historical` and `pending-map` out of the markers this plan writes, so it depends on this pass having run — but it is built with the register, not here.
- **Tracers T3, T5 and T6.** Only T4 belongs to §10.
- **Environment-fact staleness.** §1's shelf-life clause handles it, and `AGENTS.md` already carries the rule. The pass marks documents.
- **`Status:` line reconciliation.** A document may read `Status: accepted` and `Disposition: pending-map` at once; they are different axes and the pass keeps them that way.
