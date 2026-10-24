# Substrate Components, Plan A: Structure, Links and the Commit Hook

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the detection substrate every later plan of this spec builds on: one walker predicate and an OKF frontmatter reader (#194), markdown links with a `/`-led path and the resolver behind them (§5.2, #208), the fix-then-fail commit hook (§5.1, #203), the `daily/` and `log/` retype (§4.4), and the reserved-file, stray-file and encoding repairs of §5.5 (#204, #209, #210, #211, #170, #174).

**Architecture:** `research_vault/frontmatter.py` gains `read_okf`, a PyYAML reader beside the flat parser; `structure.is_excluded` becomes the one walker predicate. A new `research_vault/links.py` parses, resolves and renders both link forms the way Obsidian does, and `captured.py` switches to it before anything else changes. `stamp-type --paths` becomes the one fixer (type stamp, link normalisation, root `log.md` render); the hook runs it on fully staged files and refuses the commit when it changed any, never staging. Every check that gains a row files it under an existing or §7-coined check id, and every new id joins its registries in the same commit.

**Tech Stack:** Python 3.12 in `.venv`; pytest with xdist; PyYAML (becomes a runtime dependency in Task 2); git 2.43; the repository's form owners (ruff, mdformat, yamlfix) through `.pre-commit-config.yaml`; `gh`.

**Spec:** `docs/superpowers/specs/2026-10-03-substrate-components-design.md` — the plan argues from it; executors read both. "§N" is the spec's section; "decision NN" its §1; "ruling N" its §2. "Designs" is `…-section-3-designs.md` and "research" is `…-section-3-research.md`; "Qn" is a research question. Every `file:line` cite is the spec's, valid at `6419497` (`research_vault/`, `hooks/` and `tests/` are byte-identical to the spec's `13035fb`; checked 2026-10-24 with `git diff --stat 13035fb HEAD -- research_vault hooks tests`, empty).

## The plan family

The spec is executed as five plans, each producing working software, in this order. A later plan assumes every earlier one has merged to `main`.

| Plan | File                                                            | Carries                                                                                                                        | Closes                                                                      |
| ---- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| A    | this file                                                       | §5.6 (#194), §5.2 and #208, §5.1 (#203), §4.4, §5.5's #204 #209 #210 #211 #170 #174, #178 item 3                               | #170, #174, #194, #203, #204, #208, #209, #210, #211; #178 item 3 commented |
| B    | `2026-10-24-substrate-components-b-capture-monitor.md`          | §5.3 whole (#185, #188, #195, the monitor with #205, #189, #196, #206, #183), publish's per-commit re-check (Q2)               | #183, #185, #188, #189, #195, #196, #205, #206                              |
| C    | `2026-10-24-substrate-components-c-compiled-and-text-layers.md` | §5.4 (#212, the `seal` verb), §5.5's #207 and the `fulltext/` half of #211, §5.7 (#193, #192)                                  | #192, #193, #207, #212                                                      |
| D    | `2026-10-24-substrate-components-d-zotero-declaration.md`       | §3 as the declaration, §6.1 (#190, #191), §6.2, §6.4, #172, the Zotero live checks of §8                                       | #172, #190, #191                                                            |
| E    | `2026-10-24-substrate-components-e-obsidian-seed.md`            | §4 whole, §6.3, #161, #202, the Obsidian live checks of §8, the assembly-spec and ATTRIBUTION amendments that concern the seed | #161, #202                                                                  |

Why this order: §9 forbids the seed (E) before detection (A, B, C) has landed. D precedes E because E's `obsidian` doctor check reuses D's two-table declaration loader. B precedes D because the Attachment Scanner's declared settings are safe only once #189 has landed (§9 item 2). A precedes everything: every later check walks through the predicate of Task 1 and resolves links through Task 4.

## Global Constraints

- Every Run begins `source .venv/bin/activate`, from the repository root.
- The offline suite is `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider`; `-n` on the command line, never in addopts. Green at the end of every task.
- Form: run the owners directly on the touched files — `ruff check --fix <files> && ruff format <files>` for Python, `mdformat <files>` for Markdown, `yamlfix <file>` for YAML — never `pre-commit run` in this shared checkout (`.pre-commit-config.yaml:3-6`: it stashes across every worktree). CI runs `pre-commit run --all-files`; a form drift you did not run locally fails the required check. `mypy` runs bare (`[tool.mypy] files`); every new module must pass it.
- Commits are conventional and pathspec-form: `git commit -m "…" -- <files>`, and every commit ends with the trailer `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (the printed `git commit -m` examples omit the trailer for brevity, never the commit). Renames use `git mv`. Never revert or restore another session's uncommitted files (`AGENTS.md`).
- Branch motion (`AGENTS.md`, Git): `git switch -c substrate-a/<task-slug>` from `main`; commit; `git push -u origin substrate-a/<task-slug>`; wait until `gh api repos/{owner}/{repo}/commits/$(git rev-parse HEAD)/check-runs --jq '.check_runs[] | select(.name=="quality") | .conclusion'` prints `success`; then `git switch main && git merge --ff-only substrate-a/<task-slug> && git push origin main`. A branch behind `main` cannot fast-forward: `git rebase main`, push, wait again. The non-required `mutation-gate` job may report new survivors on a branch that adds code; it blocks nothing, and Task 12 triages them.
- `must_replace` (`tests/conftest.py:17`), never bare `str.replace`, on fixture text in `conftest.py`, `test_verify_cli.py`, `test_lints.py`, `test_events.py` (`tests/test_config_validity.py::test_fixture_substitutions_cannot_become_no_ops`).
- Skill names stay unbackticked in `skills/*/SKILL.md` prose unless they name a research-vault skill: `tests/test_skill_contracts.py:230-253` reads every backticked kebab token as a skill name.
- The spec and its siblings are scanned surfaces of `tests/test_current_state.py::test_no_dangling_repository_path`: a task that renames or deletes a path the spec cites as `tests/…`, `research_vault/…` or `skills/…` either updates the spec's citation in the same commit or leaves it on a line the `_NOT_A_POINTER` hatch matches (`deleted`, `removed`, `retired`, `goes`, `to be created`, `planned`).
- `mutation-baseline.txt` is hand-edited only to prune a deleted function's keys (`grep -v '^research_vault/<module>.py::func/<name>::' mutation-baseline.txt > t && mv t mutation-baseline.txt`) in the commit that deletes it. New survivors are triaged in Task 12 with `scripts/mutation_gate.py --update-baseline`, each key above a `# reason:` line.
- Dates an implementer writes into a repository record are today's; dates inside printed tests and fixtures stay as printed.
- Machine-local facts stay out of the repository (`AGENTS.md`); live values come from `python -m research_vault probe`.
- Every check id, reason code and doctor probe id this plan coins joins `inbox.CHECK_IDS` or `inbox.REASON_CODES`, `docs/agents/terminology.md` §4.4's table, `skills/publish/SKILL.md:33` where it closes publish, and the `CLOSING_BY_SURFACE` sets, in the commit that first emits it (`tests/test_config_validity.py:157`, `tests/test_skill_contracts.py:618-630`).
- Issues close in the task that lands their fix (`gh issue close <n> --comment "…"`), never at approval (spec §11).
- Where a task's design relies on another task's code doing something, that is a claim to check, not a fact to assert; a mismatch is reported as a deviation in the task's report, not worked around.
- A live check (§8) is an attended task that blocks only the item it gates. If the instrument it needs is down (the test Zotero at `localhost:23129`, the scratch Obsidian vault), the task reports that and the gated item does not ship; #180 is the precedent.

## Deviations from the spec, settled here

Each is a place where the spec's text cannot be executed as written; the plan settles it so no task discovers it.

1. **Missing PyYAML exits 4.** §5.6 says "a distinct exit code the hook refuses". `verify` exits 0–3 today; `4` is the new code (`cmd_verify`), and the hook's `*)` branch already refuses any code outside 0, 1 and 3 (`templates/git/pre-commit:42-45`). `tests/test_precommit.py:32` gains the pair `(4, 4)`.
2. **New doctor probe ids §7 does not coin.** §5.6 wants "doctor reports it" for PyYAML, and §6.2 a deny-rules row. §7 names no probe id for either. This plan coins `pyyaml` (Task 2); Plan C coins `deny-rules`. Both join terminology §4.4's doctor-probe row and the `DOCTOR_WARN_ONLY` set, and each plan's closing task adds the name to §7 as a dated amendment.
3. **`text-layer` stays out of `CHECK_IDS`.** §7 says each new check id "joins `CHECK_IDS` or `REASON_CODES`", but designs cluster 4 keeps `text-layer` pipeline-only as `append-only` is, so no skill can file it through `finding`. Plan C follows the designs; `tests/test_skill_contracts.py:625` pins `CHECK_IDS` against terminology's check-ids row, so the row stays silent about it too and `skills/publish/SKILL.md:33` names it as a closing check.
4. **Ambiguous wikilinks are rows under `captured-set`.** §5.2 says ambiguous and dead targets get "resolve by hand" rows, dead ones under `dead-link`, and names no check for the ambiguous ones. They stay under `captured-set` with the existing `schema-violation` code and a reason that names the candidates (Task 4).

______________________________________________________________________

### Task 0: The records at approval (§11)

**Files:**

- Modify: `docs/superpowers/specs/2026-10-03-substrate-components-design.md:3` (status line)
- Modify: `docs/superpowers/specs/2026-09-17-pre-lane-2-design.md:3` (status line becomes an execution record)
- Modify: `docs/superpowers/specs/2026-09-05-assembly-design.md` (§7.1 State line; §7.3's lane rows point here)
- Create: the five plan files of this family, committed with the records on this task's branch (the `main` ruleset refuses a sha its required check has not run on, so even a records commit rides a branch)

**Interfaces:**

- Produces: nothing in code; the spec is the active spec and the issues it carries stay open until their tasks land.

- [ ] **Step 1: Approval gate**

Stop and ask the operator: *"Approve `docs/superpowers/specs/2026-10-03-substrate-components-design.md` as the active spec? On approval nothing closes: each of the 27 issues it carries closes in the task that lands it (§11)."* Continue only on an explicit yes. On a no, the plan does not run.

- [ ] **Step 2: The spec's status line**

Replace line 3 of the spec (the paragraph beginning `Status: **written, awaiting the operator's review**`) with:

```markdown
Status: **the active spec** (approved 2026-10-24), beside the open decomposition (`2026-09-05-assembly-design.md`). It carries lanes 2, 3a and 3b of the assembly spec's §7.3 and is executed as five plans, `docs/superpowers/plans/2026-10-24-substrate-components-{a,b,c,d,e}-*.md`, in that order (§9). It succeeds `2026-09-17-pre-lane-2-design.md`, whose plan closed on 2026-09-23 (milestone `pre-lane-2`, 19 of 19 issues closed).
```

- [ ] **Step 3: The pre-lane-2 spec becomes an execution record**

Replace line 3 of `docs/superpowers/specs/2026-09-17-pre-lane-2-design.md` (the paragraph beginning `Status: **the active spec** (2026-09-17)`) with:

```markdown
Status: **executed** (2026-09-17 to 2026-09-23; milestone `pre-lane-2`, 19 of 19 issues closed). It binds until superseded and is amended from `2026-10-03-substrate-components-design.md` (the active spec from 2026-10-24), which succeeds it. It succeeded `2026-09-06-import-redesign-design.md` (lane 1, closed 2026-09-16) and amended it in place where a finding here changed it, each amendment dated. The skills comparison's briefs and matrix are the evidence sibling `2026-09-17-pre-lane-2-design-skills-evidence.md`.
```

- [ ] **Step 4: The assembly spec's §7.1 State line and §7.3 pointers**

In `docs/superpowers/specs/2026-09-05-assembly-design.md`, append to the end of the §7.1 paragraph that ends `lane 2 opens when its plan lands.`:

```markdown
 **State 2026-10-24:** lanes 2, 3a and 3b are one spec, `2026-10-03-substrate-components-design.md` (declare, provision, observe), the active spec; its five plans run in the order its §9 binds.
```

Append after the §7.3 table's last paragraph (the one beginning `*Pointer, 2026-09-17:* lane 3a also owns two items`):

```markdown
*Pointer, 2026-10-24:* lanes 2, 3a and 3b are decided in `2026-10-03-substrate-components-design.md` (§3 the Zotero add-ons, §4 the seeded `.obsidian/` and the Obsidian plugins that read Zotero, §5–§6 the detection their rulings rest on). #161's two items are that spec's §6.2 and §8.
```

- [ ] **Step 5: Commit the records and the plans; merge when green**

```bash
mdformat docs/superpowers/specs/2026-10-03-substrate-components-design.md docs/superpowers/specs/2026-09-17-pre-lane-2-design.md docs/superpowers/specs/2026-09-05-assembly-design.md docs/superpowers/plans/2026-10-24-substrate-components-*.md
git switch -c substrate-a/records
git add docs/superpowers/plans/2026-10-24-substrate-components-*.md
git commit -m "docs(spec): lanes 2-3 — the active spec; pre-lane-2 becomes an execution record; the five plans" -- docs/superpowers/specs/2026-10-03-substrate-components-design.md docs/superpowers/specs/2026-09-17-pre-lane-2-design.md docs/superpowers/specs/2026-09-05-assembly-design.md docs/superpowers/plans/2026-10-24-substrate-components-*.md
git push -u origin substrate-a/records
```

Wait for `quality` on the branch head, then `git switch main && git merge --ff-only substrate-a/records && git push origin main`. `tests/test_current_state.py::test_no_dangling_repository_path` scans the active specs, not `docs/superpowers/plans/`, so the plans' `Create:` paths are not pointers it reads; the spec's own `to be created` lines are hatched.

______________________________________________________________________

### Task 1: One walker predicate, dot-directories and OS litter (#194 half 1, Q25)

**Files:**

- Modify: `research_vault/structure.py:36-47` (`EXCLUDED_DIRS`, `is_excluded`)
- Modify: `research_vault/verify.py:745-753`, `research_vault/lints.py:503`, `research_vault/publish.py:135`, `research_vault/markers.py:180-182`, `research_vault/stamp.py:38,51-54`, `research_vault/propagate.py:62-75`, `research_vault/captured.py:35,98-99,139-140`
- Modify: `research_vault/templates/vault/gitignore` (three OS-litter lines)
- Test: `tests/test_structure.py`, `tests/test_verify_cli.py`, `tests/test_templates.py:176-200`, `tests/test_scaffold.py:95-115`

**Interfaces:**

- Produces: `structure.is_excluded(path: Path, vault: Path) -> bool` — true for any path with a component in `EXCLUDED_DIRS`, any component starting with `.`, or a final component matching `OS_LITTER`. `structure.OS_LITTER: frozenset[str]` and `structure.is_os_litter(name: str) -> bool`. Every walker in the package calls `is_excluded`; nothing else decides exclusion.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_structure.py`:

```python
import pytest


@pytest.mark.parametrize(
    "relative",
    [
        ".obsidian/plugins/dataview/README.md",
        ".claude/settings.md",
        "wiki/.trash/old.md",
        "projects/brief/.hot/notes.md",
        "literature/.DS_Store",
        "literature/._smith2020.md",
        "wiki/desktop.ini",
        "wiki/Desktop.ini",
        ".git/COMMIT_EDITMSG",
        ".raw/x.md",
        ".vault-meta/mode.json",
    ],
)
def test_is_excluded_covers_every_dot_component_and_os_litter(tmp_path, relative):
    assert structure.is_excluded(tmp_path / relative, tmp_path)


@pytest.mark.parametrize(
    "relative",
    ["wiki/a.md", "literature/smith2020.md", "projects/brief/draft.md", "dotless.md"],
)
def test_is_excluded_leaves_ordinary_paths_alone(tmp_path, relative):
    assert not structure.is_excluded(tmp_path / relative, tmp_path)


def test_every_walker_in_the_package_uses_the_one_predicate():
    """#194: the predicate is only a mechanism if every walker calls it. A
    `rglob("*.md")` whose loop body does not call `structure.is_excluded`
    is a walker that reaches `.obsidian/`."""
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parents[1] / "research_vault"
    offenders = []
    for module in sorted(root.glob("*.py")):
        text = module.read_text(encoding="utf-8")
        for match in re.finditer(r'\.rglob\("\*\.md"\)', text):
            window = text[match.end() : match.end() + 400]
            if "is_excluded(" not in window and module.name != "structure.py":
                offenders.append(f"{module.name}:{text[: match.start()].count(chr(10)) + 1}")
    assert offenders == [], offenders


def test_a_plugin_readme_under_the_config_dir_is_not_checked(tmp_path):
    """The #194 report: a community plugin's `.md` under `.obsidian/` was held
    to OKF §11 rules 1-2 and blocked the commit."""
    from research_vault import scaffold, verify

    scaffold.scaffold_vault(tmp_path)
    readme = tmp_path / ".obsidian" / "plugins" / "dataview" / "README.md"
    readme.parent.mkdir(parents=True)
    readme.write_text("# Dataview\n\nNo frontmatter here.\n")
    _report, effective, _hashes, warning = verify.verify_state(
        tmp_path, network=False, git_candidate="worktree"
    )
    decision, blockers = verify.surface_decision("commit", effective, warning)
    assert decision == 0, blockers
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_structure.py -q -k "is_excluded or walker or plugin_readme"`
Expected: FAIL — `.obsidian/...` and the litter names are not excluded; `verify.py`, `lints.py`, `publish.py`, `markers.py`, `propagate.py` listed as offenders.

- [ ] **Step 3: The predicate**

In `research_vault/structure.py`, replace lines 33-47 (the `EXCLUDED_DIRS` comment and constant through `is_excluded`) with:

```python
# The compile tool's own stores (ingest spec §4.3): `.raw/` would hold a
# duplicate of `fulltext/` if its capture were ever run, and `.vault-meta/` is
# its runtime state. Both are gitignored and never walked. Kept as a named set
# for the readers that spell them (`stamp._SKIP_DIRS`); `is_excluded` below
# covers them through the dot-component rule as well.
EXCLUDED_DIRS = frozenset({".git", ".raw", ".vault-meta"})
# #194: Obsidian itself skips any path with a component starting with a dot
# (`validateConfigDir`, app.js 1.13.7), so a plugin's README.md under
# `.obsidian/`, Claude Code's `.claude/`, Obsidian's `.trash/` and a
# plugin's nested dotfile are never notes. The OS-litter names are the
# three upstream gitignore templates spell (Q25): macOS `.DS_Store` and
# AppleDouble `._*` (which match a `*.md` glob), and Windows `desktop.ini`
# in both casings.
OS_LITTER = frozenset({".DS_Store", "desktop.ini", "Desktop.ini"})
_APPLE_DOUBLE_PREFIX = "._"


def is_os_litter(name: str) -> bool:
    return name in OS_LITTER or name.startswith(_APPLE_DOUBLE_PREFIX)


def is_excluded(path: Path, vault: Path) -> bool:
    """The one walker predicate (#194): dot-components, the excluded stores, OS litter.

    Every walker in the package calls this; a test pins that no `rglob("*.md")`
    loop body skips it. `.gitkeep` is a dot-name too, so a walker over every
    file (not only `*.md`) treats the sentinel as excluded, which is right:
    nothing reads it.
    """
    parts = path.relative_to(vault).parts
    return any(part in EXCLUDED_DIRS or part.startswith(".") for part in parts) or (
        bool(parts) and is_os_litter(parts[-1])
    )
```

- [ ] **Step 4: Every walker calls it**

`research_vault/verify.py:745-753` — the literature glob and the `wiki`/`projects` rglobs gain the predicate; the whole-vault walk already has it:

```python
    note_files = [
        path
        for path in sorted((vault / "literature").glob("*.md"))
        if not structure.is_excluded(path, vault)
    ] + [
        path
        for folder in ("wiki", "projects")
        for path in sorted((vault / folder).rglob("*.md"))
        if not structure.is_excluded(path, vault)
    ]
```

`research_vault/lints.py:503-508` — `disputed_claim_links`:

```python
    for path in (
        [
            page
            for page in sorted((vault_root / "wiki").rglob("*.md"))
            if not structure.is_excluded(page, vault_root)
        ]
        if (vault_root / "wiki").is_dir()
        else []
    ):
```

and add `structure` to the `from . import frontmatter, gitstate, literature_notes` line (`lints.py:13`). `structure` imports nothing from `lints`, so no cycle.

`research_vault/publish.py:135` — `project_note`:

```python
    for path in sorted(directory.rglob("*.md")):
        if structure.is_excluded(path, Path(vault)):
            continue
```

and add `structure` to `publish.py:24`'s import list.

`research_vault/markers.py:180-182` — `_claim_notes`:

```python
    return [
        path
        for path in sorted((vault / "projects").rglob("*.md"))
        + sorted((vault / "literature").glob("*.md"))
        if not structure.is_excluded(path, vault)
    ]
```

and import `structure` in `markers.py` (`from . import claims, gitstate, structure` — read the existing import line and add the name).

`research_vault/stamp.py:38` and `:51-54`:

```python
_SKIP_DIRS = frozenset({"fulltext"})
```

```python
    for path in sorted(vault.rglob("*.md")):
        if structure.is_excluded(path, vault) or any(
            part in _SKIP_DIRS for part in path.relative_to(vault).parts
        ):
            continue
        yield path
```

`research_vault/propagate.py:61-75` already calls `is_excluded`; leave it. `research_vault/captured.py:35` — `_read_notes`:

```python
    for path in sorted((vault / "literature").glob("*.md")):
        if structure.is_excluded(path, vault):
            continue
```

`research_vault/capture.py:333` (`_every_note`), `research_vault/lifecycle.py:148` (`_provenances`), `research_vault/compile.py:93` (`_selected_notes`) and `research_vault/okf.py:23` (`regenerate_log`'s day files) gain the same two lines; `okf.py` imports `structure` for it (`from . import frontmatter, structure`). `structure` imports `frontmatter` only, so none of these cycles.

- [ ] **Step 5: The seeded gitignore**

`research_vault/templates/vault/gitignore` becomes:

```
.research-vault/
.obsidian/workspace*
.raw/
.vault-meta/
fulltext/
.DS_Store
._*
[Dd]esktop.ini
```

Update the two byte pins: `tests/test_scaffold.py:112-114` (`.gitignore` read_text equality) to the eight lines above, and add to `tests/test_templates.py::test_bases_and_machine_example_match_canonical_shapes` after the two `gitignore` asserts:

```python
    for litter in (".DS_Store\n", "._*\n", "[Dd]esktop.ini\n"):
        assert litter in gitignore
    assert set(structure.OS_LITTER) == {".DS_Store", "desktop.ini", "Desktop.ini"}
```

with `from research_vault import frontmatter, structure` at the top of `tests/test_templates.py`.

- [ ] **Step 6: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider`
Expected: PASS. `tests/test_captured.py:218-222` (literature stays out of the page index) still holds: the predicate only adds exclusions.

- [ ] **Step 7: Form, commit, branch**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests
git switch -c substrate-a/walker-predicate
git commit -m "fix(structure): one walker predicate — dot-directories and OS litter are never notes (#194)" -- research_vault/structure.py research_vault/verify.py research_vault/lints.py research_vault/publish.py research_vault/markers.py research_vault/stamp.py research_vault/captured.py research_vault/capture.py research_vault/lifecycle.py research_vault/compile.py research_vault/okf.py research_vault/templates/vault/gitignore tests/test_structure.py tests/test_templates.py tests/test_scaffold.py
git push -u origin substrate-a/walker-predicate
```

Wait for `quality`; `git switch main && git merge --ff-only substrate-a/walker-predicate && git push origin main`. #194 stays open until Task 2 lands the reader.

______________________________________________________________________

### Task 2: `read_okf`, PyYAML as a runtime dependency, the fail-closed exit (#194 half 2, Q18)

**Files:**

- Modify: `pyproject.toml:18-23` (`dependencies`), `research_vault/frontmatter.py` (append `read_okf` and its loader), `research_vault/structure.py:74-111,136-171` (the two readers switch), `research_vault/lints.py:530` (`disputed_claim_links`'s parse), `research_vault/stamp.py:116-154` (null `type:` replaced; re-parse after insert), `research_vault/__main__.py` (`cmd_verify` exit 4; doctor sets), `research_vault/doctor.py` (the `pyyaml` row)
- Modify: `docs/agents/terminology.md:139` (doctor probe ids row), `docs/agents/okf-conformance.md:23` (names `read_okf`), `skills/setup-vault/SKILL.md:36` ("thirteen rows" → "every row")
- Test: `tests/test_frontmatter.py`, `tests/test_structure.py`, `tests/test_stamp.py`, `tests/test_precommit.py:32`, `tests/test_doctor.py:17-42,148-155`, `tests/test_okf.py:78-94`

**Interfaces:**

- Produces: `frontmatter.read_okf(text: str) -> tuple[dict, str]` — the OKF reader: PyYAML `CSafeLoader` (falling back to `SafeLoader`) with the timestamp resolver removed, a duplicate-key constructor, a non-mapping block rejected, an empty block read as `{}`, the same delimiter regexes as `parse`. Raises `FrontmatterError` on any YAML fault and `frontmatter.DependencyMissingError` when PyYAML cannot be imported. `frontmatter.okf_type(data) -> bool` — OKF rule 2's `not value` test. `__main__.EXIT_DEPENDENCY_MISSING = 4`. Doctor probe `pyyaml` (warn-only).

- Consumes: Task 1's predicate (unchanged here).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_frontmatter.py`:

```python
import pytest

from research_vault import frontmatter


def test_read_okf_reads_nested_yaml_the_flat_parser_refuses():
    text = (
        "---\ntitle: A page\ntype: concept\ntags:\n  - a\n  - b\n"
        "meta:\n  nested: 1\n---\nbody\n"
    )
    data, body = frontmatter.read_okf(text)
    assert data == {
        "title": "A page",
        "type": "concept",
        "tags": ["a", "b"],
        "meta": {"nested": 1},
    }
    assert body == "body\n"


def test_read_okf_splits_on_the_same_delimiters_as_parse():
    text = "---\r\ntype: concept\r\n---\r\nbody\r\n"
    assert frontmatter.read_okf(text)[1] == frontmatter.parse(text)[1] == "body\r\n"
    assert frontmatter.read_okf("no block\n") == ({}, "no block\n")
    with pytest.raises(frontmatter.FrontmatterError, match="unterminated"):
        frontmatter.read_okf("---\ntype: concept\nbody\n")


@pytest.mark.parametrize("value", ["null", "~", "NULL", "Null", ""])
def test_read_okf_rule_2_reads_every_null_spelling_as_missing(value):
    """OKF's reference reader tests `not fm.get("type")`; BaseLoader would read
    `null` as the string "null" and pass it (Q18)."""
    data, _ = frontmatter.read_okf(f"---\ntype: {value}\n---\n")
    assert not frontmatter.okf_type(data)


def test_read_okf_keeps_a_quoted_null_as_present():
    data, _ = frontmatter.read_okf('---\ntype: "null"\n---\n')
    assert frontmatter.okf_type(data)


def test_read_okf_leaves_a_date_shaped_scalar_as_text():
    """The reference loader removes the timestamp resolver: `2026-13-45` is text,
    not a ValueError and not a datetime."""
    data, _ = frontmatter.read_okf("---\ntype: daily\nday: 2026-13-45\nreal: 2026-10-24\n---\n")
    assert data["day"] == "2026-13-45"
    assert data["real"] == "2026-10-24"


def test_read_okf_refuses_a_duplicate_key_and_a_non_mapping_block():
    with pytest.raises(frontmatter.FrontmatterError, match="duplicate key 'type'"):
        frontmatter.read_okf("---\ntype: a\ntype: b\n---\n")
    with pytest.raises(frontmatter.FrontmatterError, match="not a mapping"):
        frontmatter.read_okf("---\n- a\n- b\n---\n")
    with pytest.raises(frontmatter.FrontmatterError, match="not a mapping"):
        frontmatter.read_okf("---\njust a scalar\n---\n")


def test_read_okf_turns_an_unhashable_key_into_a_frontmatter_error():
    """`date: {{date}}` is a Templater placeholder; without a hashability check the
    duplicate-key constructor raises a bare TypeError (Q18)."""
    with pytest.raises(frontmatter.FrontmatterError):
        frontmatter.read_okf("---\ndate: {{date}}\n---\n")


def test_read_okf_refuses_a_custom_tag_and_an_unquoted_colon_title():
    with pytest.raises(frontmatter.FrontmatterError):
        frontmatter.read_okf("---\ntype: !custom x\n---\n")
    with pytest.raises(frontmatter.FrontmatterError):
        frontmatter.read_okf("---\ntitle: A: B\ntype: concept\n---\n")


def test_read_okf_reads_an_empty_block_as_an_empty_mapping():
    assert frontmatter.read_okf("---\n---\nbody\n") == ({}, "body\n")


def test_read_okf_names_a_missing_pyyaml_as_its_own_error(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def refuse(name, *args, **kwargs):
        if name == "yaml":
            raise ImportError("No module named 'yaml'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", refuse)
    monkeypatch.setattr(frontmatter, "_LOADER", None)
    with pytest.raises(frontmatter.DependencyMissingError, match="PyYAML"):
        frontmatter.read_okf("---\ntype: a\n---\n")
```

Append to `tests/test_structure.py`:

```python
def test_check_note_frontmatter_reads_nested_yaml(tmp_path):
    """#194's second half: a Pandoc or Templater note with nested YAML is a note,
    not a schema violation."""
    path = _write(
        tmp_path,
        "projects/brief/notes.md",
        "---\ntitle: Notes\ntype: note\nmeta:\n  nested: 1\n---\nbody\n",
    )
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.MATCHED


def test_check_note_frontmatter_reads_a_null_type_as_missing(tmp_path):
    path = _write(tmp_path, "projects/brief/notes.md", "---\ntype: null\n---\n")
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.reason == "schema-violation — missing type (OKF §11 rule 2)"


def test_root_index_with_a_boolean_key_is_reported_not_a_traceback(tmp_path):
    """`yes: 1` gives a bool key under the YAML loader; `sorted()` over mixed
    keys raises TypeError without `key=str` (Q18)."""
    _write(tmp_path, "index.md", '---\nokf_version: "0.2"\nyes: 1\n---\n# x\n')
    rows = structure.check_reserved(tmp_path)
    assert any("carries keys beyond okf_version: ['True']" in o.reason for o in rows)
```

Append to `tests/test_stamp.py`:

```python
def test_stamp_replaces_a_null_type_line_rather_than_adding_a_second(tmp_path):
    from research_vault import stamp

    (tmp_path / "literature").mkdir()
    note = tmp_path / "literature" / "x.md"
    note.write_text("---\ntype: null\ntitle: x\n---\nbody\n")
    stamped, reported = stamp.stamp_types(tmp_path)
    assert stamped == ["literature/x.md"]
    assert reported == []
    assert note.read_text() == '---\ntype: "literature"\ntitle: x\n---\nbody\n'


def test_stamp_reports_a_block_whose_insert_does_not_round_trip(tmp_path):
    """After the insert, stamp re-parses; a block that does not read back as
    `{type, **data}` is reported `unparseable`, never written."""
    from research_vault import stamp

    (tmp_path / "literature").mkdir()
    note = tmp_path / "literature" / "x.md"
    before = "---\nmeta:\n  nested: 1\n---\nbody\n"
    note.write_text(before)
    stamped, reported = stamp.stamp_types(tmp_path)
    assert stamped == []
    assert reported == [("literature/x.md", "unparseable")]
    assert note.read_text() == before
```

In `tests/test_precommit.py:32`, the parametrize becomes `[(0, 0), (1, 1), (3, 0), (2, 2), (4, 4)]`.

In `tests/test_doctor.py:17-42`, add `"pyyaml"` to `PROBE_NAMES` (after `"compile-tool"`) and to `WARN_ONLY`; in `tests/test_okf.py:78-94` add `"pyyaml"` after `"compile-tool"`. Add to `tests/test_doctor.py`:

```python
def test_pyyaml_row_reports_the_import_state(monkeypatch):
    probe = doctor._pyyaml_probe()
    assert probe.check == "pyyaml"
    assert probe.result is Result.MATCHED
    assert probe.reason.startswith("PyYAML ")

    import builtins

    real_import = builtins.__import__

    def refuse(name, *args, **kwargs):
        if name == "yaml":
            raise ImportError("No module named 'yaml'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", refuse)
    probe = doctor._pyyaml_probe()
    assert probe.result is Result.UNMATCHED
    assert "pip install" in probe.reason
```

Append to `tests/test_verify_cli.py`:

```python
def test_verify_exits_4_when_pyyaml_is_missing(net_vault, monkeypatch, capsys):
    """§5.6: fail closed. The hook's `*)` branch refuses 4; exit 3 would let the
    commit through as an outage."""
    import research_vault.__main__ as cli
    from research_vault import frontmatter

    def missing(*_args, **_kwargs):
        raise frontmatter.DependencyMissingError("PyYAML is not installed")

    monkeypatch.setattr(cli, "verify_state", missing)
    code = cli.main(["verify", "--vault", str(net_vault), "--offline"])
    assert code == cli.EXIT_DEPENDENCY_MISSING == 4
    assert "PyYAML" in capsys.readouterr().err
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_frontmatter.py tests/test_structure.py tests/test_stamp.py tests/test_precommit.py tests/test_doctor.py tests/test_okf.py tests/test_verify_cli.py -q -k "okf or null or pyyaml or round_trip or hook_resolves or thirteen or exits_4 or boolean_key"`
Expected: FAIL — `read_okf`, `okf_type`, `DependencyMissingError`, `_pyyaml_probe`, `EXIT_DEPENDENCY_MISSING` do not exist; the thirteen-probe tests fail on the fourteenth name.

- [ ] **Step 3: PyYAML as a runtime dependency**

`pyproject.toml:18-23` becomes:

```toml
dependencies = [
  # Lazy-imported at research_vault's single parse site (package boundary only —
  # the vendored find-sources scripts parse via stdlib by upstream's choice, recorded
  # in that skill's vendoring notes).
  "defusedxml==0.7.1",
  # The OKF frontmatter reader (`frontmatter.read_okf`, #194): the flat parser
  # stays for capture's own writes; OKF §11 is judged by a YAML reader. A floor
  # by design — the loader API has not moved since 5.1; the C loader is used
  # when the wheel carries it and the pure loader otherwise.
  "PyYAML>=6.0",
]
```

Run `pyproject-fmt pyproject.toml` (the form owner; it may reorder nothing here) and `pip install -e ".[dev]"`.

- [ ] **Step 4: `read_okf`**

Append to `research_vault/frontmatter.py`:

```python
# --- the OKF reader (#194): PyYAML, the reference loader's rules -----------------
#
# `parse` above is capture's own grammar: flat, quoted, one spelling per value,
# used for every surface capture or verify writes. OKF §11 rules 1-2 are judged
# against YAML, which is what the reference implementation reads
# (open-knowledge-format/okf-ref, document.py), so the structure checks read
# through this function instead. The two readers split the block on the same
# delimiters (`_FRONTMATTER_OPEN`, `_FRONTMATTER_CLOSE`) so they never disagree
# about where a body starts.


class DependencyMissingError(RuntimeError):
    """PyYAML cannot be imported: the OKF reader cannot run, and nothing that
    depends on it may read as a pass. `cmd_verify` maps this to exit 4, which
    the vault's pre-commit hook refuses (its `*)` branch), and doctor's
    `pyyaml` row names the repair."""


_LOADER = None


def _loader():
    """The reference loader: SafeLoader (C when available) minus the timestamp
    resolver, with a duplicate-key constructor that checks hashability first."""
    global _LOADER  # noqa: PLW0603 — one lazily built loader class per process
    if _LOADER is not None:
        return _LOADER
    try:
        import yaml
    except ImportError as error:
        raise DependencyMissingError(
            "PyYAML is not installed; the OKF frontmatter reader cannot run "
            "(pip install PyYAML)"
        ) from error

    base = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

    class _OkfLoader(base):  # type: ignore[misc,valid-type]
        pass

    # OKF's reference loader keeps every implicit resolver except timestamps:
    # a date-shaped scalar stays text, so `2026-13-45` is neither a datetime
    # nor a ValueError, and a calendar date compares as the string it is.
    _OkfLoader.yaml_implicit_resolvers = {
        first: [
            (tag, regexp)
            for tag, regexp in resolvers
            if tag != "tag:yaml.org,2002:timestamp"
        ]
        for first, resolvers in base.yaml_implicit_resolvers.items()
    }

    def construct_mapping(self, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as error:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found unhashable key {key!r}",
                    key_node.start_mark,
                ) from error
            if key in mapping:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping

    _OkfLoader.add_constructor(
        "tag:yaml.org,2002:map", lambda loader, node: construct_mapping(loader, node)
    )
    _LOADER = _OkfLoader
    return _LOADER


def read_okf(text: str) -> tuple[dict, str]:
    """OKF §11's reader: YAML frontmatter as the reference implementation reads it.

    Returns ``({}, text)`` for a file with no block and ``({}, body)`` for an
    empty block (document.py:71-75). A non-mapping block, a duplicate key, an
    unhashable key, a custom tag and any YAML syntax fault are
    ``FrontmatterError``; a missing PyYAML is ``DependencyMissingError``.
    """
    opening = _FRONTMATTER_OPEN.match(text)
    if opening is None:
        return {}, text
    closing = _FRONTMATTER_CLOSE.search(text, opening.end())
    if closing is None:
        raise FrontmatterError("unterminated frontmatter")
    block = text[opening.end() : closing.start()]
    body = text[closing.end() :]
    # `_loader()` raises DependencyMissingError before any `yaml` name is
    # touched; once it has returned, the import below cannot fail.
    loader = _loader()
    import yaml  # noqa: PLC0415 — the lazy import is the dependency boundary

    try:
        # The loader is a SafeLoader (C or pure) subclass that only narrows the
        # resolver table and tightens the mapping constructor: `safe_load`
        # itself is `load(stream, SafeLoader)`, and no constructor here builds
        # an arbitrary Python object.
        data = yaml.load(block, Loader=loader)  # noqa: S506
    except yaml.YAMLError as error:
        message = str(error).splitlines()
        detail = next(
            (line.strip() for line in message if "duplicate key" in line), None
        ) or " ".join(line.strip() for line in message[:2])
        raise FrontmatterError(f"frontmatter is not valid YAML: {detail}") from error
    if data is None:
        return {}, body
    if not isinstance(data, dict):
        raise FrontmatterError("frontmatter block is not a mapping")
    return data, body


def okf_type(data) -> bool:
    """OKF §11 rule 2 as the reference tests it: ``not fm.get("type")`` is a
    missing type. A whitespace-only string is also missing — the one divergence,
    in the strict direction, that `check_note_frontmatter` already made."""
    value = data.get("type") if isinstance(data, dict) else None
    return bool(value) and not (isinstance(value, str) and not value.strip())
```

- [ ] **Step 5: The structure checks read through it**

`research_vault/structure.py:74-100` — `check_note_frontmatter`:

```python
    try:
        data, _body = frontmatter.read_okf(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, frontmatter.FrontmatterError) as error:
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                f"schema-violation — frontmatter unparseable ({error})",
            )
        ]
    if not frontmatter.okf_type(data):
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                "schema-violation — missing type (OKF §11 rule 2)",
            )
        ]
    okf_type = data["type"]
```

`DependencyMissingError` is a `RuntimeError`, not a `FrontmatterError`, so it propagates out of the check to `cmd_verify` (Step 7). `check_reserved` (`structure.py:146,151`) switches its `frontmatter.parse` to `frontmatter.read_okf` and its `sorted(set(data) - {"okf_version"})` to `sorted((str(key) for key in set(data) - {"okf_version"}), key=str)`. `_log_shape_problems` (`structure.py:120`) switches to `read_okf` as well, keeping the `except frontmatter.FrontmatterError: body = text` tolerance.

`research_vault/lints.py:530` — `disputed_claim_links`'s `_parse_frontmatter(text)` call becomes a local read through `read_okf`:

```python
        try:
            data, _ = frontmatter.read_okf(text)
            parsed = True
        except frontmatter.FrontmatterError:
            data, parsed = {}, False
```

(`_parse_frontmatter` stays for the literature readers, which read capture's flat grammar.)

- [ ] **Step 6: Stamp replaces a null `type:` and re-parses**

In `research_vault/stamp.py`, replace lines 123-124 (`if "type" in data: continue`) with:

```python
        if "type" in data and (
            not isinstance(data["type"], str) or data["type"].strip()
        ) and data["type"] not in {"null", "~", "NULL", "Null", None}:
            continue
        null_typed = "type" in data
```

and replace lines 141-155 (the `if has_delimiter:` block through `stamped.append`) with:

```python
        if has_delimiter:
            if isinstance(data, frontmatter._DuplicateKeyMapping):
                reported.append((relative, "unparseable"))
                continue
            rest = {k: v for k, v in frontmatter._mapping_items(data) if k != "type"}
            block = frontmatter.serialize({"type": derived, **rest})
            # Q18: after the insert, the block must read back as {type, **data}
            # under the OKF reader; a block with indented keys the flat parser
            # happened to pass would otherwise be rewritten into something
            # neither reader accepts.
            try:
                reparsed, _ = frontmatter.read_okf(block + body)
            except frontmatter.FrontmatterError:
                reported.append((relative, "unparseable"))
                continue
            if reparsed.get("type") != derived or set(reparsed) != {"type", *rest}:
                reported.append((relative, "unparseable"))
                continue
        else:
            block = f'---\ntype: "{derived}"\n---\n'
        if newline == "\r\n":
            block = block.replace("\n", newline)
        new_text = block + body
        _write_text(path, new_text)
        stamped.append(relative)
```

The flat parser (`stamp.py:118`) refuses a nested block already (`nested maps unsupported`), so the second stamp test's `meta:\n  nested: 1` reaches `reported` through the existing `except frontmatter.FrontmatterError` branch at `:119-121`; the re-parse guard above is what pins the contract for a block the flat parser passes but the YAML reader rejects. Rename the local `null_typed` away if ruff reports it unused.

- [ ] **Step 7: Exit 4 and the doctor row**

`research_vault/__main__.py` — after `_NAMED_FAILURES` add:

```python
# §5.6: the OKF reader's dependency is missing. Not 3 (an outage the hook
# lets through for CI replay) and not 2 (could not run): a distinct code the
# hook's `*)` branch refuses, so a vault with no PyYAML never commits unchecked.
EXIT_DEPENDENCY_MISSING = 4
```

In `cmd_verify`, wrap the `verify_state` call's `try` with a second handler before `_NAMED_FAILURES`:

```python
    except frontmatter.DependencyMissingError as error:
        print(f"verification cannot run: {error}", file=sys.stderr)
        return EXIT_DEPENDENCY_MISSING
```

Add `"pyyaml"` to `DOCTOR_WARN_ONLY`. In `research_vault/doctor.py`, add before `doctor()`:

```python
def _pyyaml_probe() -> Probe:
    """The OKF reader's dependency (#194, §5.6): `verify` exits 4 without it."""
    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        return Probe(
            "pyyaml",
            Result.UNMATCHED,
            "PyYAML is not importable — verify exits 4 and the commit hook refuses; "
            "pip install PyYAML into the environment that runs research_vault",
        )
    loader = "C" if hasattr(yaml, "CSafeLoader") else "pure"
    return Probe("pyyaml", Result.MATCHED, f"PyYAML {yaml.__version__} ({loader} loader)")
```

and append `_pyyaml_probe(),` after `_compile_tool_probe(),` in `doctor()`'s list. Change `doctor.py:1` to `"""The doctor: repair the scoped vault substrate, then the ordered probes (assembly spec §9).` and `:450`'s docstring to `"""Repair the scoped vault substrate and return its ordered probes (§5)."""`. In `skills/setup-vault/SKILL.md:36` replace `— thirteen rows —` with `— every row doctor prints —`.

`docs/agents/terminology.md:139` (doctor probe ids row): append `` `pyyaml` `` after `` `backup` ``. `docs/agents/okf-conformance.md:23`: append the sentence `Rules 1 and 2 are read through `research_vault/frontmatter.py`'s `read_okf`, PyYAML under OKF's reference-loader rules (#194); the flat parser stays capture's own grammar.`

- [ ] **Step 8: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS. If `tests/test_config_validity.py` reads `pyproject.toml`'s dependency list, the PyYAML line is a runtime dependency with a floor; the sourcing rule (`docs/agents/sourcing.md:27`) admits it as "a commodity hard problem" — record that sentence in the commit message.

- [ ] **Step 9: Live check owed (§8): `read_okf` against a compile-tool page**

Attended. In the scratch vault the compile tool has adopted (`skills/setup-vault/SKILL.md:61`), write `wiki/concepts/colon.md` through the tool's transaction engine with `title: A: B` unquoted, then run `python -m research_vault verify --vault <scratch> --offline --surface commit`. Expected: an `okf-frontmatter` UNMATCHED row naming `wiki/concepts/colon.md` with `frontmatter is not valid YAML`. Record the outcome (date, tool commit, the row) in the task report; Plan C's `seal` verb runs the same reader so the page fails inside the session that can redo it.

- [ ] **Step 10: Form, commit, branch, close #194**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat docs/agents/terminology.md docs/agents/okf-conformance.md skills/setup-vault/SKILL.md
git switch -c substrate-a/read-okf
git commit -m "feat(frontmatter): read_okf — OKF §11 judged by PyYAML; verify exits 4 without it; doctor's pyyaml row (#194)" -- pyproject.toml research_vault/frontmatter.py research_vault/structure.py research_vault/lints.py research_vault/stamp.py research_vault/__main__.py research_vault/doctor.py docs/agents/terminology.md docs/agents/okf-conformance.md skills/setup-vault/SKILL.md tests/test_frontmatter.py tests/test_structure.py tests/test_stamp.py tests/test_precommit.py tests/test_doctor.py tests/test_okf.py tests/test_verify_cli.py
git push -u origin substrate-a/read-okf
```

After the merge: `gh issue close 194 --comment "Closed by Plan A Task 1-2: one walker predicate (dot-components, OS litter) across every walker; OKF §11 read through read_okf (PyYAML, reference-loader rules); a missing PyYAML is verify exit 4, refused by the hook; doctor's pyyaml row."`

______________________________________________________________________

### Task 3: `daily/` is the diary, `log/` is the machines' record (§4.4)

**Files:**

- Modify: `research_vault/structure.py:28-32` (`_FOLDER_TYPES`), `research_vault/publish.py:425` (`{"type": "log"}`), `research_vault/scaffold.py:11-23` (`_EMPTY_ROOTS` gains `daily`; the directory is created), `research_vault/templates/vault/system/templates/daily.md`, `research_vault/templates/context.md:11,26` and `CONTEXT.md:11,26` (the glossary entries), `docs/agents/okf-conformance.md:13`
- Test: `tests/test_structure.py:11-16`, `tests/test_publish.py:625-647,735-742`, `tests/conftest.py:327`, `tests/test_scaffold.py:20-38`, `tests/test_templates.py:170-173`, `tests/test_hooks.py:572`

**Interfaces:**

- Produces: `structure.expected_type("log/<day>.md") == "log"`, `structure.expected_type("daily/<anything>.md") == "daily"` at any depth; `scaffold._EMPTY_ROOTS == ("daily", "literature", "log", "projects")`. The `daily` type is a person's; the `log` type is a machine's.

- [ ] **Step 1: Write the failing tests**

In `tests/test_structure.py::test_expected_type_is_the_folder`, change the `log/` line and add two:

```python
    assert structure.expected_type("log/2026-08-20.md") == "log"
    assert structure.expected_type("daily/2026-08-20.md") == "daily"
    assert structure.expected_type("daily/weekly/2026-W34.md") == "daily"
```

In `tests/test_publish.py::test_append_log_writes_the_day_header_once_and_keeps_every_line`, the expected text's header becomes `'---\ntype: "log"\n---\n'`; at `:740` the assertion becomes `assert frontmatter.parse(logged)[0] == {"type": "log"}`. In `tests/conftest.py:327` the fixture day file is written as `'---\ntype: "log"\n---\n- 09:00 human:eran — imported smith2020\n'` (use `must_replace` only where a fixture is edited from an earlier string; this is the literal). In `tests/test_scaffold.py:20-38`, `EXPECTED_CREATED` gains `"daily/.gitkeep"` (sorted position: after `"AGENTS.md"`). In `tests/test_templates.py:170-173`, the `daily.md` pin becomes:

```python
    assert asset("vault/system/templates/daily.md").read_text() == (
        '---\ntype: "daily"\n---\n'
    )
```

`tests/test_hooks.py:572` (`test_pretooluse_denies_write_creating_new_log_day_file`) stays: `log/` is still a machine surface. Add to `tests/test_scaffold.py`:

```python
def test_scaffold_seeds_daily_through_the_empty_roots_not_vault_dirs(tmp_path):
    """§4.4: deleting an unused diary folder must never block a commit, so
    `daily/` is a sentinel, not a required directory."""
    created = scaffold.scaffold_vault(tmp_path)
    assert "daily/.gitkeep" in created
    assert "daily" not in scaffold.VAULT_DIRS
    assert "daily" in scaffold._EMPTY_ROOTS
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_structure.py tests/test_publish.py tests/test_scaffold.py tests/test_templates.py -q -k "expected_type or append_log or withdrawn or daily or EXPECTED or canonical"`
Expected: FAIL on the type names and the missing `daily/.gitkeep`.

- [ ] **Step 3: The data change**

`research_vault/structure.py:28-32`:

```python
_FOLDER_TYPES = {
    "literature": "literature",
    # §4.4: `log/` is the machines' activity record and `daily/` the person's
    # diary. The type comes from the top folder at any depth, so a weekly note
    # under `daily/weekly/` is `daily` too.
    "log": "log",
    "daily": "daily",
    "inbox": "fleeting",
}
```

`research_vault/publish.py:425`: `day.write_text(frontmatter.serialize({"type": "log"}))`. `research_vault/scaffold.py:23`: `_EMPTY_ROOTS = ("daily", "literature", "log", "projects")`, and in `_add_empty_root_sentinels` create the directory first:

```python
    for root in _EMPTY_ROOTS:
        directory = vault / root
        directory.mkdir(parents=True, exist_ok=True)
        if not any(directory.iterdir()):
```

`_preflight_conflicts` (`scaffold.py:180-183`) already handles a missing root. `research_vault/templates/vault/system/templates/daily.md` becomes exactly `---\ntype: "daily"\n---\n` (the `log/` comment goes; `log/` needs no template).

- [ ] **Step 4: The glossary and the register**

`CONTEXT.md:11` and `research_vault/templates/context.md:11` — the **Type (OKF)** entry: replace `` `log/` → daily, `` with `` `log/` → log, `daily/` → daily, ``. `CONTEXT.md:26` and `context.md:26` — replace the **Log** entry with two entries:

```markdown
**Log**: The machines' append-only per-day activity record (`log/`), typed `log`, written only by `publish` and summarized in root `log.md`. Never hand-written.

**Daily note**: The person's diary (`daily/`), typed `daily` at any depth, written by Obsidian's Daily notes. Not a machine surface.
```

`docs/agents/okf-conformance.md:13`: replace `` `log/` → `daily`, `` with `` `log/` → `log`, `daily/` → `daily`, ``. `tests/test_templates.py::test_glossary_carries_the_ingest_vocabulary_and_no_retired_terms` (`:364`) may pin the `log/ → daily` phrase; read it and update the expectation to the new text.

- [ ] **Step 5: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider`
Expected: PASS. The fixture vault's day file now parses as `{"type": "log"}` and `okf-frontmatter` passes it; a leftover `daily` on a `log/` file is `type 'daily' but folder derives 'log'`.

- [ ] **Step 6: Form, commit, branch**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat CONTEXT.md research_vault/templates/context.md docs/agents/okf-conformance.md
git switch -c substrate-a/daily-and-log
git commit -m "feat(structure): daily/ is the person's diary, log/ the machines' record typed log (§4.4)" -- research_vault/structure.py research_vault/publish.py research_vault/scaffold.py research_vault/templates/vault/system/templates/daily.md research_vault/templates/context.md CONTEXT.md docs/agents/okf-conformance.md tests/test_structure.py tests/test_publish.py tests/conftest.py tests/test_scaffold.py tests/test_templates.py
git push -u origin substrate-a/daily-and-log
```

______________________________________________________________________

### Task 4: `links.py`, and `captured.py` resolves through it (§5.2, #208)

**Files:**

- Create: `research_vault/links.py`
- Modify: `research_vault/captured.py:17-21,84-109,133-190` (`_WIKILINK`, `_page_names`, `_aliases` and `_textual` go; a `literature_paths` helper and the index-based walk arrive)
- Modify: `research_vault/inbox.py:25-58,67-91` (`dead-link` joins both registries), `research_vault/verify.py:53-79` (`dead-link` closes commit and publish)
- Modify: `docs/agents/terminology.md:137-140` (check-ids and reason-codes rows), `skills/publish/SKILL.md:33`, `skills/evidence-conventions/SKILL.md` (reason-code table gains `dead-link`)
- Test: `tests/test_links.py` (new), `tests/test_captured.py`

**Interfaces:**

- Produces:

  - `links.Link` — frozen dataclass: `kind: Literal["wiki", "markdown"]`, `embed: bool`, `target: str` (the path part, decoded), `subpath: str` (`""` or `#…`), `alias: str | None`, `start: int`, `end: int`.
  - `links.find_links(text: str) -> list[Link]` — every link in `text`, in order, both forms; nothing is masked here.
  - `links.is_uri(target: str) -> bool`.
  - `links.Index.build(vault: Path, literature: Mapping[str, str], names: Mapping[str, str]) -> Index` — `literature` maps citation key → `literature/<file>.md`, `names` maps title or alias → that path; the index walks every non-excluded file outside `literature/` itself.
  - `Index.resolve(target: str, *, source: str) -> list[str]` — vault-relative posix paths: `[]` dead, one hit resolved, several ambiguous.
  - `links.render_markdown(link: Link, path: str) -> str` — the markdown spelling of a wikilink to `path`.
  - `links.ATTACHMENT_EXTENSIONS: frozenset[str]`.
  - `captured.literature_paths(vault) -> tuple[dict[str, str], dict[str, str]]` — the two maps above, read from the captured set.
  - Check id `dead-link`, reason code `dead-link`; closing on commit and publish.

- Consumes: Task 1's `structure.is_excluded`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_links.py`:

```python
from pathlib import Path

import pytest

from research_vault import links


def _vault(tmp_path: Path) -> Path:
    for relative in (
        "wiki/concepts/Foo.md",
        "wiki/sources/Foo.md",
        "wiki/concepts/Only Here.md",
        "wiki/img.png",
        "system/bases/trust-tier.base",
        "projects/brief/draft.md",
        "literature/smith2020.md",
        "literature/junk.md",
        ".obsidian/plugins/x/README.md",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")
    return tmp_path


def _index(tmp_path: Path) -> links.Index:
    return links.Index.build(
        _vault(tmp_path),
        literature={"smith2020": "literature/smith2020.md"},
        names={"Mortality decline": "literature/smith2020.md"},
    )


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("Only Here", ["wiki/concepts/Only Here.md"]),
        ("only here", ["wiki/concepts/Only Here.md"]),  # case-insensitive
        ("Only Here.md", ["wiki/concepts/Only Here.md"]),
        ("concepts/Foo", ["wiki/concepts/Foo.md"]),
        ("wiki/concepts/Foo", ["wiki/concepts/Foo.md"]),
        ("/wiki/concepts/Foo.md", ["wiki/concepts/Foo.md"]),
        ("/concepts/Foo.md", []),  # a /-led link is an exact path or nothing
        ("Foo", ["wiki/concepts/Foo.md", "wiki/sources/Foo.md"]),  # ambiguous
        ("img.png", ["wiki/img.png"]),
        ("wiki/img.png", ["wiki/img.png"]),
        ("trust-tier", []),  # a dotless name resolves only as <name>.md
        ("trust-tier.base", ["system/bases/trust-tier.base"]),
        ("smith2020", ["literature/smith2020.md"]),  # through the captured set
        ("literature/smith2020", ["literature/smith2020.md"]),
        ("smith2020.md", ["literature/smith2020.md"]),  # [[Foo.md]] reads as [[Foo]]
        ("", ["wiki/concepts/Other.md"]),  # a same-page anchor names the linking file
        ("junk", []),  # a literature file with no provenance resolves nowhere
        ("literature/junk.md", []),
        ("Mortality decline", ["literature/smith2020.md"]),  # a note's alias
        ("README", []),  # excluded directories are not indexed
        ("nowhere", []),
        ("https://example.org/x", []),
        ("mailto:a@b.c", []),
    ],
)
def test_resolve_follows_obsidian_for_a_page_in_wiki(tmp_path, target, expected):
    index = _index(tmp_path)
    assert index.resolve(target, source="wiki/concepts/Other.md") == expected


def test_resolve_relative_forms_are_exact_from_the_source(tmp_path):
    index = _index(tmp_path)
    assert index.resolve("./Foo", source="wiki/concepts/Other.md") == [
        "wiki/concepts/Foo.md"
    ]
    assert index.resolve("../sources/Foo.md", source="wiki/concepts/Other.md") == [
        "wiki/sources/Foo.md"
    ]
    assert index.resolve("../Foo", source="wiki/concepts/Other.md") == []


def test_find_links_parses_both_forms_with_subpath_alias_and_embed():
    text = (
        "see [[Foo]], [[Foo#Heading|shown]], ![[img.png|480]], "
        "[x](wiki/concepts/Foo.md#^c-1), ![](/wiki/img.png), "
        "[u](https://example.org/a(b)) and [[ Spaced ]]"
    )
    found = links.find_links(text)
    assert [(l.kind, l.embed, l.target, l.subpath, l.alias) for l in found] == [
        ("wiki", False, "Foo", "", None),
        ("wiki", False, "Foo", "#Heading", "shown"),
        ("wiki", True, "img.png", "", "480"),
        ("markdown", False, "wiki/concepts/Foo.md", "#^c-1", "x"),
        ("markdown", True, "/wiki/img.png", "", ""),
        ("markdown", False, "https://example.org/a(b)", "", "u"),
        ("wiki", False, "Spaced", "", None),
    ]
    assert text[found[1].start : found[1].end] == "[[Foo#Heading|shown]]"


def test_find_links_decodes_a_markdown_destination():
    (link,) = links.find_links("[a](wiki/concepts/Only%20Here.md)")
    assert link.target == "wiki/concepts/Only Here.md"


@pytest.mark.parametrize(
    ("wiki", "path", "rendered"),
    [
        ("[[Only Here]]", "wiki/concepts/Only Here.md", "[Only Here](/wiki/concepts/Only%20Here.md)"),
        ("[[Foo|shown]]", "wiki/concepts/Foo.md", "[shown](/wiki/concepts/Foo.md)"),
        ("[[Foo#Heading]]", "wiki/concepts/Foo.md", "[Foo > Heading](/wiki/concepts/Foo.md#Heading)"),
        ("[[Foo#^c-1]]", "wiki/concepts/Foo.md", "[Foo > ^c-1](/wiki/concepts/Foo.md#^c-1)"),
        ("![[img.png]]", "wiki/img.png", "![](/wiki/img.png)"),
        ("![[img.png|480]]", "wiki/img.png", "![480](/wiki/img.png)"),
        ("[[a (b) 100%]]", "wiki/a (b) 100%.md", "[a (b) 100%](/wiki/a%20(b)%20100%.md)"),
    ],
)
def test_render_markdown_follows_generate_markdown_link(wiki, path, rendered):
    (link,) = links.find_links(wiki)
    assert links.render_markdown(link, path) == rendered


def test_render_encodes_only_backslash_space_and_controls():
    (link,) = links.find_links("[[x]]")
    assert links.render_markdown(link, "w/a\\b c\x01.md") == "[a\\b c\x01](/w/a%5Cb%20c%01.md)"


def test_attachment_extensions_are_obsidians_registered_set():
    for extension in ("png", "jpg", "jpeg", "gif", "bmp", "svg", "webp", "avif",
                      "mp3", "wav", "m4a", "3gp", "flac", "ogg", "oga", "opus",
                      "mp4", "webm", "ogv", "mov", "mkv", "pdf", "canvas", "base"):
        assert extension in links.ATTACHMENT_EXTENSIONS
    assert "md" not in links.ATTACHMENT_EXTENSIONS
```

Add to `tests/test_captured.py` (keep every existing test; the reasons they pin are unchanged):

```python
def test_an_embed_of_an_existing_image_pdf_or_base_is_not_a_finding(tmp_vault):
    """#208: embeds resolve against every file, not only pages."""
    _note(tmp_vault, "smith2020", "SMITH001")
    pages = tmp_vault / "wiki" / "sources"
    pages.mkdir(parents=True)
    (tmp_vault / "wiki" / "figure.png").write_bytes(b"\x89PNG")
    (tmp_vault / "wiki" / "paper.pdf").write_bytes(b"%PDF")
    (tmp_vault / "system" / "bases").mkdir(parents=True, exist_ok=True)
    (tmp_vault / "system" / "bases" / "trust-tier.base").write_text("views: []\n")
    (pages / "A.md").write_text(
        "---\ntype: source\n---\n![[figure.png]] ![[paper.pdf|200]] "
        "![[system/bases/trust-tier.base]] ![](/wiki/figure.png)\n"
    )
    assert [o for o in captured.lint_captured_set(tmp_vault) if o.result is Result.UNMATCHED] == []


def test_a_dead_embed_or_path_link_is_a_dead_link_row_not_a_not_captured_row(tmp_vault):
    """#208's split: a target with a `/` or an attachment extension, or an
    unresolved markdown destination, is `dead-link` under its own check, so an
    ack on it cannot hide a missing citation on the same page."""
    _note(tmp_vault, "smith2020", "SMITH001")
    pages = tmp_vault / "wiki" / "sources"
    pages.mkdir(parents=True)
    (pages / "A.md").write_text(
        "---\ntype: source\n---\n![[nowhere.png]] [[sources/Ghost]] "
        "[text](concepts/Missing.md) [[ghost2020]] [u](https://example.org)\n"
    )
    rows = [o for o in captured.lint_captured_set(tmp_vault) if o.result is Result.UNMATCHED]
    assert [(o.check, o.reason) for o in rows] == [  # in link order
        ("dead-link", "dead-link — wiki/sources/A.md embeds [[nowhere.png]], which no file matches"),
        ("dead-link", "dead-link — wiki/sources/A.md links [[sources/Ghost]], which no file matches"),
        ("dead-link", "dead-link — wiki/sources/A.md links to concepts/Missing.md, which no file matches"),
        ("captured-set", "not-captured — wiki/sources/A.md links [[ghost2020]], not a page and not in the captured set"),
    ]
    assert all(decode_repo_path(o.target) == b"wiki/sources/A.md" for o in rows)


def test_an_ambiguous_wikilink_is_a_resolve_by_hand_row(tmp_vault):
    pages = tmp_vault / "wiki" / "sources"
    pages.mkdir(parents=True)
    (tmp_vault / "wiki" / "concepts").mkdir()
    (tmp_vault / "wiki" / "concepts" / "Foo.md").write_text("---\ntype: concept\n---\n")
    (pages / "Foo.md").write_text("---\ntype: source\n---\n")
    (pages / "A.md").write_text("---\ntype: source\n---\n[[Foo]]\n")
    rows = [o for o in captured.lint_captured_set(tmp_vault) if o.result is Result.UNMATCHED]
    assert [(o.check, o.reason) for o in rows] == [
        (
            "captured-set",
            "schema-violation — wiki/sources/A.md links [[Foo]], which 2 files match "
            "(wiki/concepts/Foo.md, wiki/sources/Foo.md); resolve by hand",
        )
    ]


def test_a_slash_led_markdown_link_to_a_literature_note_resolves_through_the_captured_set(tmp_vault):
    _note(tmp_vault, "smith2020", "SMITH001")
    pages = tmp_vault / "wiki" / "sources"
    pages.mkdir(parents=True)
    (pages / "A.md").write_text(
        "---\ntype: source\n---\n[smith2020](/literature/smith2020.md) "
        "[gone](/literature/gone2020.md)\n"
    )
    rows = [o for o in captured.lint_captured_set(tmp_vault) if o.result is Result.UNMATCHED]
    assert [o.reason for o in rows] == [
        "dead-link — wiki/sources/A.md links to /literature/gone2020.md, which no file matches"
    ]


def test_literature_paths_maps_keys_and_names_to_the_note_that_records_them(tmp_vault):
    _note(tmp_vault, "smith2020", "SMITH001", title="Mortality decline")
    (tmp_vault / "literature" / "renamed2020.md").write_text(
        (tmp_vault / "literature" / "smith2020.md")
        .read_text()
        .replace('citationKey: "smith2020"', 'citationKey: "smith2020a"')
    )
    by_key, by_name = captured.literature_paths(tmp_vault)
    assert by_key == {
        "smith2020": "literature/smith2020.md",
        "smith2020a": "literature/renamed2020.md",
    }
    assert by_name["Mortality decline"] in by_key.values()
```

Add to `tests/test_config_validity.py` or `tests/test_verify_cli.py`:

```python
def test_dead_link_is_registered_and_closes_both_surfaces():
    from research_vault import inbox, verify

    assert "dead-link" in inbox.CHECK_IDS
    assert "dead-link" in inbox.REASON_CODES
    assert "dead-link" in verify.CLOSING_BY_SURFACE["commit"]
    assert "dead-link" in verify.CLOSING_BY_SURFACE["publish"]
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_links.py tests/test_captured.py tests/test_config_validity.py tests/test_skill_contracts.py -q`
Expected: FAIL — no `research_vault.links`; `dead-link` unregistered; `literature_paths` missing.

- [ ] **Step 3: `research_vault/links.py`**

```python
"""Links: parse, resolve and render Obsidian's two link forms (spec §5.2).

Resolution follows Obsidian 1.13.7's ``getLinkpathDest`` and rendering its
``generateMarkdownLink`` (app.js, read 2026-10-04; paraphrased, the app is
unlicensed): a ``/``-led link is an exact path or nothing; ``./`` and ``../``
are relative to the linking file; anything else tries the exact path, then a
trailing-components match; matching is case-insensitive; a name without a dot
resolves only as ``<name>.md``. research-vault's extensions: ``literature/``
resolves only through the captured set (a key, a title or an alias), and an
unparseable literature file resolves nowhere.
"""

from __future__ import annotations

import posixpath
import re
import urllib.parse
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from . import structure

# Obsidian 1.13.7's registered non-markdown extensions (image, audio, video,
# pdf, canvas, base); a wikilink target ending in one is an attachment, and an
# unresolved one is `dead-link`, never `not-captured` (designs cluster 2(b)).
ATTACHMENT_EXTENSIONS = frozenset(
    {
        "png", "jpg", "jpeg", "gif", "bmp", "svg", "webp", "avif",
        "mp3", "wav", "m4a", "3gp", "flac", "ogg", "oga", "opus",
        "mp4", "webm", "ogv", "mov", "mkv",
        "pdf", "canvas", "base",
    }
)
_WIKI = re.compile(r"(?P<embed>!?)\[\[(?P<inner>[^\[\]\n]+?)\]\]")
# A destination is one run without whitespace, with one level of balanced
# parentheses (Obsidian writes `a%20(b)` unencoded); a `[x](dest "title")`
# form is not a link this module reads.
_MARKDOWN = re.compile(
    r"(?P<embed>!?)\[(?P<text>[^\]\n]*)\]\((?P<dest>[^()\s]*(?:\([^()\s]*\)[^()\s]*)*)\)"
)
_URI = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
# `generateMarkdownLink`'s encoder (`YE`, app.js @1254563): only `\`, control
# characters and the space are percent-encoded; `(`, `%` and the rest pass.
_ENCODE = re.compile(r"[\\\x00-\x1f\x7f ]")


@dataclass(frozen=True)
class Link:
    kind: Literal["wiki", "markdown"]
    embed: bool
    target: str
    subpath: str
    alias: str | None
    start: int
    end: int


def is_uri(target: str) -> bool:
    return _URI.match(target.strip()) is not None


def _split_subpath(raw: str) -> tuple[str, str]:
    head, sep, tail = raw.partition("#")
    return head, (sep + tail if sep else "")


def find_links(text: str) -> list[Link]:
    """Every link in ``text`` in order of appearance. Nothing is masked here:
    the normaliser decides what a code fence or a claim block protects."""
    found: list[Link] = []
    for match in _WIKI.finditer(text):
        inner = match.group("inner")
        path_part, _, alias = inner.partition("|")
        target, subpath = _split_subpath(path_part)
        found.append(
            Link(
                "wiki",
                match.group("embed") == "!",
                target.strip(),
                subpath.strip(),
                alias if "|" in inner else None,
                match.start(),
                match.end(),
            )
        )
    for match in _MARKDOWN.finditer(text):
        dest = match.group("dest")
        if is_uri(dest):
            target, subpath = dest, ""
        else:
            raw_target, subpath = _split_subpath(dest)
            target = urllib.parse.unquote(raw_target)
        found.append(
            Link(
                "markdown",
                match.group("embed") == "!",
                target,
                subpath,
                match.group("text"),
                match.start(),
                match.end(),
            )
        )
    return sorted(found, key=lambda link: link.start)


class Index:
    """Every non-excluded file outside ``literature/``, plus the captured set."""

    def __init__(
        self,
        files: Iterable[str],
        literature: Mapping[str, str],
        names: Mapping[str, str],
    ) -> None:
        self._exact: dict[str, str] = {}
        self._suffix: dict[str, list[str]] = {}
        for path in files:
            lowered = path.lower()
            self._exact[lowered] = path
            parts = lowered.split("/")
            for start in range(len(parts)):
                self._suffix.setdefault("/".join(parts[start:]), []).append(path)
        self._literature = dict(literature)
        self._literature_exact = {path.lower(): path for path in literature.values()}
        self._names = dict(names)

    @classmethod
    def build(cls, vault: Path, literature: Mapping[str, str], names: Mapping[str, str]) -> Index:
        files = []
        for path in sorted(vault.rglob("*")):
            if not path.is_file() or structure.is_excluded(path, vault):
                continue
            relative = path.relative_to(vault)
            if relative.parts[0] == "literature":
                continue  # resolved through the captured set only
            files.append(relative.as_posix())
        return cls(files, literature, names)

    def _exact_hit(self, candidate: str) -> str | None:
        lowered = candidate.lower()
        return self._exact.get(lowered) or self._literature_exact.get(lowered)

    def resolve(self, target: str, *, source: str) -> list[str]:
        """Vault-relative posix paths: none (dead), one (resolved), several (ambiguous).

        An empty target (`[see](#section)`, `[[#heading]]`) is the linking file
        itself, as Obsidian and the compile tool's lint both read it."""
        raw = target.strip().replace("\\", "/")
        if is_uri(raw):
            return []
        if not raw:
            return [source]
        if raw.startswith("/"):
            candidate, exact_only = posixpath.normpath(raw.lstrip("/")), True
        elif raw.startswith(("./", "../")):
            candidate = posixpath.normpath(posixpath.join(posixpath.dirname(source), raw))
            exact_only = True
        else:
            candidate, exact_only = posixpath.normpath(raw), False
        if candidate in {".", ""} or candidate.startswith("../"):
            return []
        # Obsidian reads `[[Foo.md]]` as `[[Foo]]`: the stem is what the
        # captured set and the names are keyed by.
        stem = candidate[: -len(".md")] if candidate.lower().endswith(".md") else candidate
        dotless = "." not in posixpath.basename(stem)
        wanted = f"{stem}.md" if dotless else candidate
        hit = self._exact_hit(wanted)
        if hit is not None:
            return [hit]
        if exact_only:
            return []
        if dotless and "/" not in stem:
            if stem in self._literature:
                return [self._literature[stem]]
            if stem in self._names:
                return [self._names[stem]]
        return sorted(self._suffix.get(wanted.lower(), []))

def _encode(path: str) -> str:
    return _ENCODE.sub(lambda m: f"%{ord(m.group(0)):02X}", path)


def render_markdown(link: Link, path: str) -> str:
    """``[[x]]`` → ``[basename](/p/x.md)``; alias and subpath carried; embeds
    keep only their alias (a size such as ``480``) as the text."""
    destination = "/" + _encode(path) + _encode(link.subpath)
    if link.embed:
        return f"![{link.alias or ''}]({destination})"
    if link.alias is not None:
        text = link.alias
    else:
        base = posixpath.basename(path)
        text = base[: -len(".md")] if base.endswith(".md") else base
        if link.subpath:
            text = f"{text} > {link.subpath[1:]}"
    return f"[{text}]({destination})"
```

Run `mypy research_vault/links.py` and fix any annotation it wants (the `files` iterable is `Iterable[str]`; `Mapping` imports come from `collections.abc`).

- [ ] **Step 4: The registries**

`research_vault/inbox.py` — add to `REASON_CODES` after `"recompile-needed"`:

```python
        # An embed or a path link to a file that does not exist (#208, spec §5.4).
        "dead-link",
```

and to `CHECK_IDS` after `"compile"`:

```python
        # Unresolved embeds and path links in the compiled layer (#208, spec §5.4).
        "dead-link",
```

`research_vault/verify.py:53-79`: add `"dead-link"` to both the `commit` and `publish` sets (after `"captured-set"`). `docs/agents/terminology.md:137`: append `` `dead-link` `` to the check-ids row; `:139` (reason codes): insert `` `dead-link` `` alphabetically after `` `database-changed` ``. `skills/publish/SKILL.md:33`: the parenthesised list gains `` `dead-link` `` after `` `captured-set` ``. `skills/evidence-conventions/SKILL.md`'s reason-code table gains a row (alphabetically, after `contradiction`):

```markdown
| `dead-link`        | A compiled page embeds or links by path to a file that does not exist — `![[figure.png]]`, `[[sources/Ghost]]`, `[x](concepts/Missing.md)`. Its own check (`dead-link`), so acknowledging a dead embed never hides a missing citation on the same page.                                                                                                    |
```

- [ ] **Step 5: `captured.py` resolves through the index**

Replace `research_vault/captured.py:13` with `from . import clock, frontmatter, links, literature_notes, structure`, delete `_WIKILINK` (`:20`), delete `_aliases` and `_page_names` (`:84-109`), and add after `captured_set`:

```python
DEAD_LINK = "dead-link"


def literature_paths(vault_root) -> tuple[dict[str, str], dict[str, str]]:
    """Citation key → the note recording it, and title or alias → that note.

    The captured set's own reading (decision 08): the key is the recorded
    `citationKey`, never the filename, so a re-keyed note awaiting propagation
    still resolves under the name its tuple records.
    """
    vault = Path(vault_root)
    by_key: dict[str, str] = {}
    by_name: dict[str, str] = {}
    for path in sorted((vault / "literature").glob("*.md")):
        if structure.is_excluded(path, vault):
            continue
        try:
            text = path.read_text(encoding="utf-8")
            data, _body = frontmatter.parse(text)
        except (OSError, UnicodeError, frontmatter.FrontmatterError):
            continue
        provenance = literature_notes.read_provenance(text)
        if provenance is None:
            continue
        relative = f"literature/{path.name}"
        by_key[provenance.citation_key] = relative
        title = data.get("title")
        if isinstance(title, str) and title:
            by_name.setdefault(title, relative)
        for alias in data.get("aliases", []):
            if isinstance(alias, str) and alias:
                by_name.setdefault(alias, relative)
    return by_key, by_name


def link_index(vault_root) -> links.Index:
    vault = Path(vault_root)
    by_key, by_name = literature_paths(vault)
    return links.Index.build(vault, by_key, by_name)


def _is_path_shaped(link: links.Link) -> bool:
    """#208's split: a target with a `/` or an attachment extension names a file,
    so an unresolved one is `dead-link`; anything else is a would-be citation."""
    extension = link.target.rsplit(".", 1)[-1].lower() if "." in link.target else ""
    return (
        link.kind == "markdown"
        or "/" in link.target
        or extension in links.ATTACHMENT_EXTENSIONS
    )
```

Replace `_textual` (`:133-190`) whole:

```python
def _textual(vault: Path, keys: set[str]) -> list[Outcome]:
    outcomes: list[Outcome] = []
    wiki = vault / "wiki"
    if not wiki.is_dir():
        return outcomes
    index = link_index(vault)
    for path in sorted(wiki.rglob("*.md")):
        if structure.is_excluded(path, vault):
            continue
        relative = path.relative_to(vault).as_posix()
        reported = _reportable(relative)
        target_path = RepoPath(os.fsencode(relative))
        try:
            text = path.read_text(encoding="utf-8", errors="surrogateescape")
        except OSError as error:
            outcomes.append(
                Outcome(CHECK, target_path, Result.UNREACHABLE, f"outage — {error}")
            )
            continue
        for match in _CITATION.finditer(text):
            key = match.group("key")
            if key not in keys:
                outcomes.append(
                    Outcome(
                        CHECK,
                        target_path,
                        Result.UNMATCHED,
                        f"not-captured — {reported} cites [@{key}], not in the captured set",
                    )
                )
        for link in links.find_links(text):
            if links.is_uri(link.target):
                continue
            written = _reportable(link.target)
            verb = "embeds" if link.embed else "links"
            hits = index.resolve(link.target, source=relative)
            if len(hits) == 1:
                continue
            if len(hits) > 1:
                shown = ", ".join(_reportable(hit) for hit in hits)
                outcomes.append(
                    Outcome(
                        CHECK,
                        target_path,
                        Result.UNMATCHED,
                        f"schema-violation — {reported} links [[{written}]], which "
                        f"{len(hits)} files match ({shown}); resolve by hand",
                    )
                )
                continue
            if link.kind == "markdown":
                outcomes.append(
                    Outcome(
                        DEAD_LINK,
                        target_path,
                        Result.UNMATCHED,
                        f"dead-link — {reported} {verb} to {written}, which no file matches",
                    )
                )
            elif _is_path_shaped(link):
                outcomes.append(
                    Outcome(
                        DEAD_LINK,
                        target_path,
                        Result.UNMATCHED,
                        f"dead-link — {reported} {verb} [[{written}]], which no file matches",
                    )
                )
            else:
                outcomes.append(
                    Outcome(
                        CHECK,
                        target_path,
                        Result.UNMATCHED,
                        f"not-captured — {reported} links [[{written}]], "
                        "not a page and not in the captured set",
                    )
                )
    return outcomes
```

`lint_captured_set` (`:287-298`) is unchanged: its MATCHED summary row still appears only when nothing failed. The existing reason strings for `[@ghost2021]` and `[[ghost2020]]` are byte-identical to today's, so `tests/test_captured.py:96,113,164-165,184,209-210` hold. `test_captured.py:218-222` (a root `literature.md` is still a page) holds because the index excludes only the `literature/` directory. A test that imports `captured._page_names` or `captured._WIKILINK` by name must be deleted or rewritten against `link_index` in this step; grep `tests/` for both names first.

- [ ] **Step 6: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS. If `tests/test_skill_contracts.py:589-601` fails on the reason table, the `dead-link` row's spelling in the evidence-conventions table is off: the first cell must be exactly `` `dead-link` ``.

- [ ] **Step 7: Form, commit, branch, close #208**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat docs/agents/terminology.md skills/publish/SKILL.md skills/evidence-conventions/SKILL.md
git switch -c substrate-a/links-resolver
git commit -m "feat(links): one resolver for both link forms; captured-set resolves embeds against every file; dead-link check (#208, §5.2)" -- research_vault/links.py research_vault/captured.py research_vault/inbox.py research_vault/verify.py docs/agents/terminology.md skills/publish/SKILL.md skills/evidence-conventions/SKILL.md tests/test_links.py tests/test_captured.py tests/test_config_validity.py
git push -u origin substrate-a/links-resolver
```

After the merge: `gh issue close 208 --comment "Closed by Plan A Task 4: captured-set resolves every link through research_vault/links.py against every non-excluded file, so an embed of an existing image, PDF or .base is not a finding; an unresolved path-shaped target is a dead-link row under its own check id."`

______________________________________________________________________

### Task 5: The normaliser (§5.2, Q19)

**Files:**

- Modify: `research_vault/links.py` (append `normalize`)
- Test: `tests/test_links.py`

**Interfaces:**

- Produces: `links.Problem` — frozen dataclass `(kind: Literal["dead", "ambiguous", "frontmatter"], target: str, candidates: tuple[str, ...])`; `links.normalize(text: str, index: Index, *, source: str) -> tuple[str, list[Problem]]` — the rewritten text and what it left alone. `links.NORMALISER_SKIPS: tuple[str, ...]` — the vault-relative prefixes and files the fixer never normalises: `literature/`, `log/`, `log.md`, `inbox/review-queue.md`, `system/propagations/`, `wiki/`, `fulltext/`. `links.is_normalised_surface(relative: str) -> bool`.

- Consumes: Task 4's `Index`, `find_links`, `render_markdown`; `lints._claim_blocks` and `claims.FIELD_RE` (read lazily).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_links.py`:

````python
def test_normalize_rewrites_every_resolvable_wikilink_and_is_idempotent(tmp_path):
    index = _index(tmp_path)
    text = "See [[Only Here]] and [[Foo#Heading|shown]] and ![[img.png|480]].\n"
    out, problems = links.normalize(text, index, source="wiki/concepts/Other.md")
    assert out == (
        "See [Only Here](/wiki/concepts/Only%20Here.md) and "
        "[[Foo#Heading|shown]] and ![480](/wiki/img.png).\n"
    )  # Foo is ambiguous (two Foo.md), so its link stays as written
    assert [(p.kind, p.target) for p in problems] == [("ambiguous", "Foo")]
    again, _ = links.normalize(out, index, source="wiki/concepts/Other.md")
    assert again == out


def test_normalize_adds_the_slash_to_a_markdown_destination_that_resolves(tmp_path):
    index = _index(tmp_path)
    text = (
        "[a](wiki/concepts/Only%20Here.md) [b](concepts/Foo.md#^c-1) "
        "[c](./Foo.md) [d](../sources/Foo.md) [e](https://x.org/y) "
        "[f](/wiki/img.png) [g](nowhere.md)\n"
    )
    out, problems = links.normalize(text, index, source="wiki/concepts/Other.md")
    assert out == (
        "[a](/wiki/concepts/Only%20Here.md) [b](/wiki/concepts/Foo.md#^c-1) "
        "[c](./Foo.md) [d](../sources/Foo.md) [e](https://x.org/y) "
        "[f](/wiki/img.png) [g](nowhere.md)\n"
    )
    assert [(p.kind, p.target) for p in problems] == [("dead", "nowhere.md")]


def test_normalize_leaves_dead_and_ambiguous_targets_as_written(tmp_path):
    index = _index(tmp_path)
    text = "[[Foo]] [[nowhere]] ![[gone.png]]\n"
    out, problems = links.normalize(text, index, source="projects/brief/draft.md")
    assert out == text
    assert [(p.kind, p.target, p.candidates) for p in problems] == [
        ("ambiguous", "Foo", ("wiki/concepts/Foo.md", "wiki/sources/Foo.md")),
        ("dead", "nowhere", ()),
        ("dead", "gone.png", ()),
    ]


def test_normalize_masks_code_fences_inline_code_and_comments(tmp_path):
    index = _index(tmp_path)
    text = (
        "```\n[[Only Here]]\n```\n"
        "~~~md\n[[Only Here]]\n~~~\n"
        "inline `[[Only Here]]` here\n"
        "<!-- [[Only Here]] -->\n"
        "%% [[Only Here]] %%\n"
        "real [[Only Here]]\n"
    )
    out, _ = links.normalize(text, index, source="projects/brief/draft.md")
    assert out.count("[[Only Here]]") == 5
    assert out.endswith("real [Only Here](/wiki/concepts/Only%20Here.md)\n")


def test_normalize_skips_anchored_claim_blocks_whole_and_masks_inline_fields(tmp_path):
    """Q19: a committed claim's bytes are frozen (claim-immutability), and
    Dataview reads only `[[…]]` inside a `[k:: …]` field."""
    index = _index(tmp_path)
    text = (
        "- (quote) Mortality fell [@smith2020, p. 3] [supports:: [[smith2020#^c-1]]] ^c-2\n"
        "  > the quoted [[Only Here]] text\n"
        "Prose with [[Only Here]] and a field [related:: [[Only Here]]] here.\n"
    )
    out, _ = links.normalize(text, index, source="projects/brief/draft.md")
    assert out == (
        "- (quote) Mortality fell [@smith2020, p. 3] [supports:: [[smith2020#^c-1]]] ^c-2\n"
        "  > the quoted [[Only Here]] text\n"
        "Prose with [Only Here](/wiki/concepts/Only%20Here.md) and a field "
        "[related:: [[Only Here]]] here.\n"
    )


def test_normalize_refuses_a_rewrite_that_leaves_frontmatter_unparseable(tmp_path):
    index = _index(tmp_path)
    text = "---\ntype: note\nrelated: [[Only Here]]\n---\nbody [[Only Here]]\n"
    out, problems = links.normalize(text, index, source="projects/brief/draft.md")
    assert out == "---\ntype: note\nrelated: [[Only Here]]\n---\nbody [Only Here](/wiki/concepts/Only%20Here.md)\n"
    assert [(p.kind, p.target) for p in problems] == [("frontmatter", "Only Here")]


def test_normalize_rewrites_a_quoted_frontmatter_link_that_stays_valid(tmp_path):
    index = _index(tmp_path)
    text = '---\ntype: note\nrelated: "[[Only Here]]"\n---\n'
    out, problems = links.normalize(text, index, source="projects/brief/draft.md")
    assert out == '---\ntype: note\nrelated: "[Only Here](/wiki/concepts/Only%20Here.md)"\n---\n'
    assert problems == []


@pytest.mark.parametrize(
    ("relative", "skipped"),
    [
        ("literature/smith2020.md", True),
        ("log/2026-10-24.md", True),
        ("log.md", True),
        ("inbox/review-queue.md", True),
        ("system/propagations/p.json", True),
        ("wiki/concepts/Foo.md", True),
        ("fulltext/ABCD1234.md", True),
        ("projects/brief/draft.md", False),
        ("inbox/idea.md", False),
        ("daily/2026-10-24.md", False),
        ("system/templates/project.md", False),
        ("index.md", False),
    ],
)
def test_normaliser_skips_the_surfaces_the_spec_names(relative, skipped):
    assert links.is_normalised_surface(relative) is (not skipped)
````

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_links.py -q -k "normalize or normalised_surface"`
Expected: FAIL — `normalize`, `Problem`, `is_normalised_surface` do not exist.

- [ ] **Step 3: The normaliser**

Append to `research_vault/links.py`:

```python
# --- the normaliser (§5.2) -----------------------------------------------------

# Never normalised (§5.2): the machine surfaces capture, publish and the
# verifier own, the compiled layer (normalised at seal, §5.4) and the text
# layer. Everything else — projects/, inbox/, daily/, system/ outside the
# propagation records, root files — is the person's and is kept in the
# markdown form.
NORMALISER_SKIPS: tuple[str, ...] = (
    "literature/",
    "log/",
    "log.md",
    "inbox/review-queue.md",
    "system/propagations/",
    "wiki/",
    "fulltext/",
)
_FENCE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})")
_INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`).+?(?<!`)\1(?!`)", re.DOTALL)
_HTML_COMMENT = re.compile(r"<!--.*?(?:-->|\Z)", re.DOTALL)
_OBSIDIAN_COMMENT = re.compile(r"%%.*?(?:%%|\Z)", re.DOTALL)


@dataclass(frozen=True)
class Problem:
    kind: Literal["dead", "ambiguous", "frontmatter"]
    target: str
    candidates: tuple[str, ...] = ()


def is_normalised_surface(relative: str) -> bool:
    return not any(
        relative == skip or (skip.endswith("/") and relative.startswith(skip))
        for skip in NORMALISER_SKIPS
    )


def _fence_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    open_at: int | None = None
    token: tuple[str, int] | None = None
    offset = 0
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        fence = _FENCE.match(stripped)
        if token is None and fence:
            token = (fence.group(1)[0], len(fence.group(1)))
            open_at = offset
        elif token is not None and re.match(
            rf"^[ ]{{0,3}}{re.escape(token[0])}{{{token[1]},}}[ \t]*$", stripped
        ):
            spans.append((open_at or 0, offset + len(line)))
            token, open_at = None, None
        offset += len(line)
    if token is not None:
        spans.append((open_at or 0, len(text)))
    return spans


def _protected_spans(text: str) -> list[tuple[int, int]]:
    """Code fences, inline code, HTML and Obsidian comments, anchored claim
    blocks whole (Q19: their bytes are frozen by claim-immutability), and
    `[k:: …]` field spans on every other line (Dataview reads only `[[…]]`
    inside a field)."""
    from . import claims, lints  # noqa: PLC0415 — neither imports links

    spans = _fence_spans(text)
    for pattern in (_INLINE_CODE, _HTML_COMMENT, _OBSIDIAN_COMMENT):
        spans.extend((m.start(), m.end()) for m in pattern.finditer(text))
    for block in lints._claim_blocks(text).values():
        start = text.find(block)
        while start != -1:
            spans.append((start, start + len(block)))
            start = text.find(block, start + 1)
    spans.extend((m.start(), m.end()) for m in claims.FIELD_RE.finditer(text))
    return spans


def _protected(spans: list[tuple[int, int]], link: Link) -> bool:
    return any(start <= link.start < end or start < link.end <= end for start, end in spans)


def _rewrite(text: str, index: Index, source: str) -> tuple[str, list[Problem]]:
    spans = _protected_spans(text)
    problems: list[Problem] = []
    pieces: list[str] = []
    cursor = 0
    for link in find_links(text):
        if link.start < cursor or _protected(spans, link) or is_uri(link.target):
            continue
        if link.kind == "markdown" and link.target.startswith(("/", "./", "../")):
            continue
        hits = index.resolve(link.target, source=source)
        if len(hits) != 1:
            problems.append(
                Problem("ambiguous" if hits else "dead", link.target, tuple(hits))
            )
            continue
        if link.kind == "wiki":
            replacement = render_markdown(link, hits[0])
        else:
            destination = "/" + _encode(hits[0]) + _encode(link.subpath)
            replacement = f"{'!' if link.embed else ''}[{link.alias or ''}]({destination})"
        pieces.append(text[cursor : link.start])
        pieces.append(replacement)
        cursor = link.end
    pieces.append(text[cursor:])
    return "".join(pieces), problems


def normalize(text: str, index: Index, *, source: str) -> tuple[str, list[Problem]]:
    """Rewrite every resolvable wikilink to the markdown form and add the `/`
    to a bare markdown destination that resolves to one file; leave URIs,
    relative forms, dead and ambiguous targets alone and report them. The
    frontmatter block is rewritten only if the result still reads as YAML."""
    from . import frontmatter  # noqa: PLC0415

    opening = frontmatter._FRONTMATTER_OPEN.match(text)
    closing = (
        frontmatter._FRONTMATTER_CLOSE.search(text, opening.end()) if opening else None
    )
    if opening is None or closing is None:
        return _rewrite(text, index, source)
    head = text[: opening.end()]
    block = text[opening.end() : closing.start()]
    delimiter = text[closing.start() : closing.end()]
    body = text[closing.end() :]
    new_body, problems = _rewrite(body, index, source)
    new_block, block_problems = _rewrite(block, index, source)
    if new_block == block:
        return head + block + delimiter + new_body, block_problems + problems
    try:
        frontmatter.read_okf(head + new_block + delimiter)
    except frontmatter.FrontmatterError:
        # An unquoted `related: [[x]]` would become `related: [x](/p/x.md)`,
        # a flow sequence followed by junk: the block is kept as written and
        # every link it holds that would have been rewritten is reported.
        kept = [
            Problem("frontmatter", link.target)
            for link in find_links(block)
            if not is_uri(link.target)
            and len(index.resolve(link.target, source=source)) == 1
        ]
        return head + block + delimiter + new_body, kept + problems
    return head + new_block + delimiter + new_body, block_problems + problems
```

`_FRONTMATTER_CLOSE` matches the newline before `---`, the `---` and its own newline, so `delimiter` is exactly the closing delimiter text and the three pieces concatenate back to the original. Run `mypy research_vault/links.py`.

- [ ] **Step 4: Run the tests**

Run: `python -m pytest tests/test_links.py -q`
Expected: PASS. If `test_normalize_masks_code_fences_inline_code_and_comments` leaves the `~~~` fence unprotected, `_FENCE` must accept both fence characters — check the regex above kept `~{3,}`.

- [ ] **Step 5: Form, commit, branch**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests
git switch -c substrate-a/link-normaliser
git commit -m "feat(links): the normaliser — resolvable wikilinks become /-led markdown links; claim blocks, code and comments are skipped (§5.2, Q19)" -- research_vault/links.py tests/test_links.py
git push -u origin substrate-a/link-normaliser
```

______________________________________________________________________

### Task 6: One fixer — `stamp-type --paths`, the `log.md` render, the writers (§5.1, #204 render half, #170, #174, #178 item 3)

**Files:**

- Create: `research_vault/fixer.py`
- Modify: `research_vault/okf.py` (rewritten: `day_files`, `render_log`, `write_log`, `regenerate_log`, the `/log/` link), `research_vault/structure.py` (`is_day_stem`), `research_vault/stamp.py:150-157` (#174: an unwritable file is reported), `research_vault/__main__.py` (`cmd_stamp_type`, the three flags), `research_vault/capture.py:15-25,567-569` (the whole-vault sweep goes), `research_vault/publish.py:24,414-430` (`_append_log` calls the fixer; `write_text` encoding), `research_vault/inbox.py:291`, `research_vault/searchlog.py:116` (#170 encodings)
- Modify: `docs/agents/okf-conformance.md:24,36`, `research_vault/structure.py:4-6` and `research_vault/stamp.py:1-12` docstrings
- Test: `tests/test_fixer.py` (new), `tests/test_okf.py`, `tests/test_stamp.py`, `tests/test_verify_cli.py:712-750`, `tests/test_capture.py:66,743-746,1028-1045`, `tests/test_publish.py`, `tests/conftest.py:327`, `tests/test_config_validity.py`

**Interfaces:**

- Produces:

  - `fixer.FixReport` — dataclass `(stamped: list[str], normalised: list[str], log_regenerated: bool, reported: list[tuple[str, str]], problems: list[tuple[str, links.Problem]])` with a `changed` property (`stamped + normalised + ["log.md"]` when the log was regenerated).
  - `fixer.fix(vault_root, paths: Iterable[str] | None = None) -> FixReport` — stamp types, normalise links on the normalised surfaces, regenerate root `log.md` when it or any day file exists and the render differs. `paths=None` walks the vault; `paths=[]` touches nothing but the log.
  - `fixer.staged_paths(vault_root) -> tuple[list[str], list[str]]` — `(fully_staged, partially_staged)` from `git diff --cached --name-only -z --diff-filter=AM` and `git diff --name-only -z`, both honouring `GIT_INDEX_FILE`.
  - `okf.WRITER_LINE`, `okf.day_files(vault_root) -> list[Path]` (newest first, calendar-date stems only), `okf.render_log(vault_root, tail_entries=20) -> str` (pure), `okf.write_log(vault_root, text)`, `okf.regenerate_log(vault_root, tail_entries=20) -> str` (render then write, UTF-8, no newline translation).
  - `structure.is_day_stem(stem: str) -> bool`.
  - `stamp-type --vault V [--paths P ...] [--paths-file F] [--staged]`: prints `stamped <p>`, `normalised <p>`, `regenerated log.md`, `unresolved <p> — …`, `skipped <p> — <reason>`; exit 0, or 4 when PyYAML is missing.

- Consumes: Task 4's `captured.link_index`, Task 5's `links.normalize` and `links.is_normalised_surface`, Task 2's `DependencyMissingError`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_fixer.py`:

```python
import os
import subprocess

from research_vault import fixer, frontmatter, okf, scaffold


def _git(vault, *args, env=None):
    return subprocess.run(
        ["git", *args], cwd=vault, check=True, capture_output=True, text=True, env=env
    ).stdout


def _page(vault, relative, text):
    path = vault / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_fix_stamps_normalises_and_regenerates_the_log_in_one_pass(tmp_vault):
    _page(tmp_vault, "wiki/concepts/Only Here.md", "---\ntype: concept\n---\n")
    draft = _page(tmp_vault, "projects/brief/draft.md", "See [[Only Here]] and [[nowhere]].\n")
    day = _page(
        tmp_vault,
        "log/2026-10-24.md",
        '---\ntype: "log"\n---\n- 09:00 research_vault/0.1.0 — captured smith2020\n',
    )
    report = fixer.fix(tmp_vault)
    assert report.stamped == ["projects/brief/draft.md"]
    assert report.normalised == ["projects/brief/draft.md"]
    assert report.log_regenerated is True
    assert report.changed == ["projects/brief/draft.md", "log.md"]
    assert [(relative, p.kind, p.target) for relative, p in report.problems] == [
        ("projects/brief/draft.md", "dead", "nowhere")
    ]
    assert draft.read_text() == (
        '---\ntype: "project"\n---\nSee [Only Here](/wiki/concepts/Only%20Here.md) and [[nowhere]].\n'
    )
    assert (tmp_vault / "log.md").read_text() == okf.render_log(tmp_vault)
    assert "captured smith2020" in (tmp_vault / "log.md").read_text()
    assert day.read_text().endswith("captured smith2020\n")  # log/ is never normalised
    again = fixer.fix(tmp_vault)
    assert again.changed == []


def test_fix_with_paths_touches_only_those_paths_and_the_log(tmp_vault):
    _page(tmp_vault, "inbox/a.md", "a thought\n")
    _page(tmp_vault, "inbox/b.md", "another\n")
    report = fixer.fix(tmp_vault, paths=["inbox/a.md"])
    assert report.stamped == ["inbox/a.md"]
    assert (tmp_vault / "inbox" / "b.md").read_text() == "another\n"
    assert report.log_regenerated is False  # no log.md and no day file: nothing to render


def test_fix_leaves_the_skipped_surfaces_alone(tmp_vault):
    """§5.2: literature/, log/, log.md, the review queue, the propagation
    records, wiki/ and fulltext/ are never normalised."""
    _page(tmp_vault, "wiki/concepts/Only Here.md", "---\ntype: concept\n---\n")
    page = _page(tmp_vault, "wiki/sources/A.md", "---\ntype: source\n---\n[[Only Here]]\n")
    note = _page(
        tmp_vault,
        "literature/x.md",
        '---\ntype: "literature"\n---\n[[Only Here]]\n',
    )
    report = fixer.fix(tmp_vault)
    assert report.normalised == []
    assert "[[Only Here]]" in page.read_text()
    assert "[[Only Here]]" in note.read_text()


def test_fix_reports_an_unwritable_file_and_continues(tmp_vault, monkeypatch):
    """#174: an OSError on write is a `unwritable` report, not a traceback."""
    from research_vault import stamp

    _page(tmp_vault, "inbox/a.md", "a thought\n")
    _page(tmp_vault, "inbox/b.md", "b thought\n")
    real = stamp._write_text

    def failing(path, text):
        if path.name == "a.md":
            raise OSError(30, "Read-only file system")
        real(path, text)

    monkeypatch.setattr(stamp, "_write_text", failing)
    report = fixer.fix(tmp_vault)
    assert report.stamped == ["inbox/b.md"]
    assert ("inbox/a.md", "unwritable") in report.reported


def test_staged_paths_splits_fully_from_partially_staged(tmp_vault):
    _git(tmp_vault, "init", "-q")
    _page(tmp_vault, "inbox/full.md", "a\n")
    _page(tmp_vault, "inbox/partial.md", "a\n")
    _git(tmp_vault, "add", "inbox/full.md", "inbox/partial.md")
    (tmp_vault / "inbox" / "partial.md").write_text("a\nb\n")
    assert fixer.staged_paths(tmp_vault) == (["inbox/full.md"], ["inbox/partial.md"])


def test_staged_paths_reads_the_index_git_names(tmp_vault, tmp_path):
    """Under `git commit -- <paths>` the hook runs against a temporary index named
    by GIT_INDEX_FILE; the two git reads must both honour it."""
    _git(tmp_vault, "init", "-q")
    _page(tmp_vault, "inbox/a.md", "a\n")
    private = tmp_path / "private-index"
    env = {**os.environ, "GIT_INDEX_FILE": str(private)}
    _git(tmp_vault, "add", "inbox/a.md", env=env)
    with_private = fixer.staged_paths(tmp_vault, env=env)
    assert with_private == (["inbox/a.md"], [])
    assert fixer.staged_paths(tmp_vault) == ([], [])
```

Replace `tests/test_okf.py`'s four `regenerate_log` tests with these (the fixture lines move to the writer's format, #204):

```python
from research_vault import doctor, frontmatter, okf, scaffold

WRITER = "research_vault/0.1.0"


def test_render_log_tail_and_links(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-19.md").write_text(f'---\ntype: "log"\n---\n- 09:00 {WRITER} — a\n')
    (tmp_path / "log" / "2026-08-20.md").write_text(f'---\ntype: "log"\n---\n- 10:00 {WRITER} — b\n')
    text = okf.render_log(tmp_path, tail_entries=1)
    data, body = frontmatter.parse(text)
    assert data["type"] == "log"
    assert "— b" in body
    assert "— a" not in body
    assert "- [2026-08-19](/log/2026-08-19.md)" in body
    assert "- [2026-08-20](/log/2026-08-20.md)" in body
    assert not (tmp_path / "log.md").read_text().endswith(body)  # render_log is pure
    assert okf.regenerate_log(tmp_path, tail_entries=1) == text
    assert (tmp_path / "log.md").read_bytes() == text.encode("utf-8")


def test_render_log_skips_a_malformed_day_file_and_keeps_its_link(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-19.md").write_text(f'---\ntype: "log"\n---\n- 09:00 {WRITER} — a\n')
    (tmp_path / "log" / "2026-08-20.md").write_text(f'---\ntype: "log"\n- 10:00 {WRITER} — broken\n')
    text = okf.render_log(tmp_path)
    assert "— a" in text
    assert "— broken" not in text
    assert "[2026-08-20](/log/2026-08-20.md)" in text


def test_render_log_is_date_grouped_newest_first(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-20.md").write_text(f'---\ntype: "log"\n---\n- 09:00 {WRITER} — a\n')
    (tmp_path / "log" / "2026-08-21.md").write_text(f'---\ntype: "log"\n---\n- 10:00 {WRITER} — b\n')
    body = okf.render_log(tmp_path).split("---\n", 2)[2]
    assert body.index("## 2026-08-21") < body.index("## 2026-08-20")


def test_render_log_renders_only_day_stems_and_writer_lines(tmp_path):
    """#204: a non-date file is not a day file, and a line outside the writer's
    format is not an entry. A 25-line stray uses none of the 20-line budget."""
    scaffold.scaffold_vault(tmp_path)
    log = tmp_path / "log"
    (log / "Untitled.md").write_text("".join(f"- {i:02d}:00 {WRITER} — stray\n" for i in range(25)))
    (log / "2026-13-45.md").write_text(f'---\ntype: "log"\n---\n- 09:00 {WRITER} — bad date\n')
    (log / "20261004.md").write_text(f'---\ntype: "log"\n---\n- 09:00 {WRITER} — compact\n')
    (log / "2026-10-01.md").write_text(
        f'---\ntype: "log"\n---\n## Agenda\n- 09:00 {WRITER} — real\n- hand-typed line\n'
    )
    text = okf.render_log(tmp_path)
    assert "## 2026-10-01" in text
    assert "— real" in text
    for absent in ("Agenda", "hand-typed", "stray", "bad date", "compact", "Untitled", "2026-13-45", "20261004"):
        assert absent not in text, absent
    assert [p.name for p in okf.day_files(tmp_path)] == ["2026-10-01.md"]


def test_okf_write_text_sites_name_their_encoding():
    """#170: under an ASCII locale the em dash in the writer's format raised
    UnicodeEncodeError from `write_text`; every write in the package names utf-8."""
    import ast
    from pathlib import Path

    from tests.conftest import package_ast

    root = Path(__file__).resolve().parents[1] / "research_vault"
    bare = []
    for module in sorted(root.glob("*.py")):
        for node in ast.walk(package_ast(module)):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "write_text"
                and not any(k.arg == "encoding" for k in node.keywords)
            ):
                bare.append(f"{module.name}:{node.lineno}")
    assert bare == [], bare


def test_regenerate_log_writes_utf8_under_an_ascii_locale(tmp_path):
    """#170 measured: `LC_ALL=C python3 -X utf8=0` gives an ASCII locale; the em
    dash in `render_log`'s lines raised before the fix."""
    import subprocess
    import sys

    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-19.md").write_text(
        f'---\ntype: "log"\n---\n- 09:00 {WRITER} — ascii locale\n', encoding="utf-8"
    )
    completed = subprocess.run(
        [sys.executable, "-X", "utf8=0", "-c",
         "import sys; from research_vault import okf; okf.regenerate_log(sys.argv[1])",
         str(tmp_path)],
        env={**__import__("os").environ, "LC_ALL": "C", "PYTHONUTF8": "0"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "ascii locale" in (tmp_path / "log.md").read_text(encoding="utf-8")
```

Keep `test_scaffold_ships_okf_artifacts`, `test_inbox_load_tolerates_frontmatter` and `test_doctor_is_substrate_and_posture_only` as they are. In `tests/conftest.py:327` the fixture day line becomes `f'---\ntype: "log"\n---\n- 09:00 research_vault/0.1.0 — imported smith2020\n'`. In `tests/test_capture.py` delete the `log.md` assertions at `:66` and `:743-746` (capture writes no day file and no longer regenerates the log; reword the `:743` comment to say the written note is the discriminator), and at `:1041` monkeypatch `capture.bibliography.write` instead of `capture.stamp.stamp_types` (the CSL write is the named-failure site that remains outside the per-item try). In `tests/test_verify_cli.py:712-750` the two `stamp-type` tests keep their expectations; add:

```python
def test_stamp_type_takes_paths_a_paths_file_and_staged(tmp_path, capsys):
    vault = tmp_path / "vault"
    assert main(["scaffold", "--vault", str(vault)]) == 0
    capsys.readouterr()
    (vault / "inbox" / "a.md").write_text("a\n")
    (vault / "inbox" / "b.md").write_text("b\n")
    assert main(["stamp-type", "--vault", str(vault), "--paths", "inbox/a.md"]) == 0
    assert capsys.readouterr().out.splitlines() == ["stamped inbox/a.md"]
    listing = tmp_path / "paths"
    listing.write_bytes(b"inbox/b.md\0")
    assert main(["stamp-type", "--vault", str(vault), "--paths-file", str(listing)]) == 0
    assert capsys.readouterr().out.splitlines() == ["stamped inbox/b.md"]
    (vault / "inbox" / "c.md").write_text("c\n")
    subprocess.run(["git", "add", "inbox/c.md"], cwd=vault, check=True)
    (vault / "inbox" / "d.md").write_text("d\n")
    subprocess.run(["git", "add", "inbox/d.md"], cwd=vault, check=True)
    (vault / "inbox" / "d.md").write_text("d\nmore\n")
    assert main(["stamp-type", "--vault", str(vault), "--staged"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "stamped inbox/c.md",
        "skipped inbox/d.md — partially staged; stage the whole file or none of it",
    ]
    assert (vault / "inbox" / "d.md").read_text() == "d\nmore\n"


def test_stamp_type_exits_4_without_pyyaml(tmp_path, monkeypatch, capsys):
    import research_vault.__main__ as cli
    from research_vault import fixer, frontmatter

    def missing(*_args, **_kwargs):
        raise frontmatter.DependencyMissingError("PyYAML is not installed")

    monkeypatch.setattr(fixer, "fix", missing)
    assert main(["stamp-type", "--vault", str(tmp_path)]) == cli.EXIT_DEPENDENCY_MISSING
    assert "PyYAML" in capsys.readouterr().err
```

In `tests/test_publish.py`, the `mark_withdrawn` tests (`:735-742`) keep asserting the log line reaches `log.md`; nothing else changes there.

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_fixer.py tests/test_okf.py tests/test_verify_cli.py -q -k "fix or render_log or staged or write_text or stamp_type"`
Expected: FAIL — no `research_vault.fixer`; `render_log`, `day_files`, `is_day_stem` missing; `--paths` unknown.

- [ ] **Step 3: `okf.py` rewritten and `structure.is_day_stem`**

Add to `research_vault/structure.py` (after `is_fleeting`), with `import datetime` at the top:

```python
def is_day_stem(stem: str) -> bool:
    """A `log/` day file's stem is exactly a calendar date (#204): `2026-13-45`
    and `20261004` are strays, not day files."""
    try:
        return datetime.date.fromisoformat(stem).isoformat() == stem
    except ValueError:
        return False
```

`research_vault/okf.py` becomes:

```python
"""Root ``log.md``: the pure render and its one writer (OKF §9; #204, #210).

``render_log`` reads only the day files — ``log/<YYYY-MM-DD>.md`` — and copies
only lines in the writer's own format, so a stray file or a hand-typed line
under ``log/`` can neither break the render nor smuggle text into it;
``structure.check_log_dir`` reports those under their own paths. The fixer
regenerates ``log.md`` and ``check_reserved`` compares it byte for byte.
"""

import re
from pathlib import Path

from . import frontmatter, structure

# `publish._append_log`'s line: `- HH:MM research_vault/<version> — <text>`.
WRITER_LINE = re.compile(r"^- \d{2}:\d{2} research_vault/\S+ — .+$")


def day_files(vault_root) -> list[Path]:
    """``log/<day>.md``, newest first; only calendar-date stems are day files."""
    vault = Path(vault_root)
    log_dir = vault / "log"
    if not log_dir.is_dir():
        return []
    return sorted(
        (
            path
            for path in log_dir.glob("*.md")
            if not structure.is_excluded(path, vault) and structure.is_day_stem(path.stem)
        ),
        reverse=True,
    )


def _day_lines(day_file: Path) -> list[str]:
    try:
        _data, body = frontmatter.parse(day_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, frontmatter.FrontmatterError):
        # A malformed day file is check_log_dir's row, never the end of the render.
        return []
    return [line for line in body.splitlines() if WRITER_LINE.match(line)]


def render_log(vault_root, tail_entries: int = 20) -> str:
    """OKF §9's shape: date-grouped, newest first, the `tail_entries` newest lines."""
    body_lines = ["# Log"]
    remaining = tail_entries
    for day_file in day_files(vault_root):
        lines = _day_lines(day_file)
        take = lines[:remaining] if remaining > 0 else []
        body_lines.extend(["", f"## {day_file.stem}"])
        body_lines.extend(take)
        body_lines.append(f"- [{day_file.stem}](/log/{day_file.stem}.md)")
        remaining -= len(take)
    return frontmatter.serialize({"type": "log"}) + "\n".join(body_lines) + "\n"


def write_log(vault_root, text: str) -> None:
    # #170: utf-8 named, newline="" so the bytes match the render on every
    # platform (#210 compares them).
    with (Path(vault_root) / "log.md").open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def regenerate_log(vault_root, tail_entries: int = 20) -> str:
    text = render_log(vault_root, tail_entries)
    write_log(vault_root, text)
    return text
```

- [ ] **Step 4: `fixer.py`**

```python
"""The one fixer behind ``stamp-type`` (spec §5.1): type stamp, link normalisation, root ``log.md``.

Writers call it on the paths they wrote; the commit hook calls it with
``--staged`` on the fully staged files and refuses the commit when it changed
any (#203). It never stages, and it never touches a file whose worktree copy
differs from its staged blob.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from . import captured, links, okf, stamp

# Reasons stamp reports that mean "the file was not read": the normaliser
# does not try again.
_UNREADABLE = frozenset({"symlink", "outside", "outage", "not-utf-8", "unwritable"})


@dataclass
class FixReport:
    stamped: list[str] = field(default_factory=list)
    normalised: list[str] = field(default_factory=list)
    log_regenerated: bool = False
    reported: list[tuple[str, str]] = field(default_factory=list)
    problems: list[tuple[str, links.Problem]] = field(default_factory=list)

    @property
    def changed(self) -> list[str]:
        """Every path the fixer rewrote, once each, in order: a file both stamped
        and normalised is one entry."""
        paths = [*self.stamped, *self.normalised, *(["log.md"] if self.log_regenerated else [])]
        return list(dict.fromkeys(paths))


def _normalise(vault: Path, paths, report: FixReport) -> None:
    index: links.Index | None = None
    skipped = {relative for relative, reason in report.reported if reason in _UNREADABLE}
    for path in stamp._candidate_paths(vault, paths):
        relative = stamp._reported_name(path, vault)
        if (
            relative in skipped
            or path.is_symlink()
            or not path.is_file()
            or not relative.endswith(".md")
            or not links.is_normalised_surface(relative)
        ):
            continue
        try:
            text = stamp._read_text(path)
        except (OSError, UnicodeError):
            continue  # stamp already reported it
        if index is None:
            index = captured.link_index(vault)
        new_text, problems = links.normalize(text, index, source=relative)
        report.problems.extend((relative, problem) for problem in problems)
        if new_text == text:
            continue
        try:
            stamp._write_text(path, new_text)
        except OSError:
            report.reported.append((relative, "unwritable"))
            continue
        report.normalised.append(relative)


def _regenerate_root_log(vault: Path) -> bool:
    target = vault / "log.md"
    if not target.exists() and not okf.day_files(vault):
        return False
    rendered = okf.render_log(vault)
    try:
        current = target.read_bytes()
    except OSError:
        current = None
    if current == rendered.encode("utf-8"):
        return False
    okf.write_log(vault, rendered)
    return True


def fix(vault_root, paths: Iterable[str] | None = None) -> FixReport:
    """Stamp, normalise, regenerate — on ``paths`` or the whole vault."""
    vault = Path(vault_root)
    listed = None if paths is None else list(paths)
    stamped, reported = stamp.stamp_types(vault, listed)
    report = FixReport(stamped=list(stamped), reported=list(reported))
    _normalise(vault, listed, report)
    report.log_regenerated = _regenerate_root_log(vault)
    report.reported.sort()
    return report


def _git_names(vault: Path, *args: str, env=None) -> list[str]:
    completed = subprocess.run(
        ["git", *args, "-z"],
        cwd=vault,
        check=True,
        capture_output=True,
        env=env if env is not None else os.environ,
    )
    return [
        os.fsdecode(name) for name in completed.stdout.split(b"\0") if name
    ]


def staged_paths(vault_root, env=None) -> tuple[list[str], list[str]]:
    """``(fully staged, partially staged)`` added-or-modified paths.

    Both reads honour ``GIT_INDEX_FILE``, which is how the hook sees the
    temporary index of a ``git commit -- <paths>`` (research Q1).
    """
    vault = Path(vault_root)
    staged = _git_names(vault, "diff", "--cached", "--name-only", "--diff-filter=AM", env=env)
    dirty = set(_git_names(vault, "diff", "--name-only", env=env))
    return (
        [path for path in staged if path not in dirty],
        [path for path in staged if path in dirty],
    )
```

`stamp._candidate_paths` already resolves a relative path against the vault and yields a given path whether or not it exists; `stamp_types` skips a non-file, and `_normalise` does too.

- [ ] **Step 5: #174 in `stamp.py`, #170 in the three writers**

`research_vault/stamp.py:150-157` — wrap the write:

```python
        new_text = block + body
        try:
            _write_text(path, new_text)
        except OSError:
            # #174: an unwritable file is a report under its own path and the
            # walk continues; the verb still exits 0.
            reported.append((relative, "unwritable"))
            continue
        stamped.append(relative)
```

and add `"unwritable"` to the module docstring's reason vocabulary (`stamp.py:20-30`). `research_vault/publish.py:425`: `day.write_text(frontmatter.serialize({"type": "log"}), encoding="utf-8")`. `research_vault/inbox.py:291`: `queue.write_text(frontmatter.serialize({"type": INBOX_TYPE}), encoding="utf-8")`. `research_vault/searchlog.py:116`: `path.write_text(frontmatter.serialize({"type": SEARCH_LOG_TYPE}), encoding="utf-8")`.

- [ ] **Step 6: The verb and the writers**

`research_vault/__main__.py` — `cmd_stamp_type` becomes:

```python
def cmd_stamp_type(args):
    """The one fixer (spec §5.1), not a gate: stamp what is fully determined,
    normalise links, regenerate root log.md; report the rest; exit 0. Exit 4
    only when the OKF reader's dependency is missing (§5.6)."""
    paths = None
    partial: list[str] = []
    if args.staged:
        paths, partial = fixer.staged_paths(args.vault)
    elif args.paths_file:
        try:
            raw = Path(args.paths_file).read_bytes()
        except OSError as error:
            print(f"stamp-type: cannot read --paths-file: {error}", file=sys.stderr)
            return 2
        paths = [os.fsdecode(name) for name in raw.split(b"\0") if name]
    elif args.paths:
        paths = list(args.paths)
    try:
        report = fixer.fix(args.vault, paths)
    except frontmatter.DependencyMissingError as error:
        print(f"stamp-type cannot run: {error}", file=sys.stderr)
        return EXIT_DEPENDENCY_MISSING
    for path in report.stamped:
        print(f"stamped {path}")
    for path in report.normalised:
        print(f"normalised {path}")
    if report.log_regenerated:
        print("regenerated log.md")
    for path in partial:
        print(f"skipped {path} — partially staged; stage the whole file or none of it")
    for path, reason in report.reported:
        if reason == "unparseable":
            print(f"skipped {path} — frontmatter is unparseable")
        elif reason == "symlink":
            print(f"skipped {path} — path is a symlink, refusing to write through it")
        elif reason == "outage":
            print(f"skipped {path} — file could not be read")
        elif reason == "not-utf-8":
            print(f"skipped {path} — file is not UTF-8")
        elif reason == "outside":
            print(f"skipped {path} — path resolves outside the vault, refusing to write through it")
        elif reason == "unwritable":
            print(f"skipped {path} — file could not be written")
        else:
            print(f"skipped {path} — no type could be derived")
    for path, problem in report.problems:
        detail = (
            f"{len(problem.candidates)} files match ({', '.join(problem.candidates)})"
            if problem.kind == "ambiguous"
            else "kept as written: the frontmatter would not stay valid YAML"
            if problem.kind == "frontmatter"
            else "no file matches"
        )
        print(f"unresolved {path} — [[{problem.target}]] {detail}; resolve by hand")
    return 0
```

Add `import os` and `fixer` to the module's imports (`from . import ..., fixer, ...`). The parser:

```python
    stamp_type = sub.add_parser("stamp-type", parents=[common])
    stamp_type.add_argument("--vault", required=True)
    stamp_type.add_argument("--paths", nargs="+", metavar="PATH")
    stamp_type.add_argument("--paths-file", metavar="FILE", help="NUL-separated vault-relative paths")
    stamp_type.add_argument("--staged", action="store_true", help="the fully staged files of the index git names")
```

and after `args = parser.parse_args(argv)`: `if args.cmd == "stamp-type" and sum(bool(x) for x in (args.paths, args.paths_file, args.staged)) > 1: parser.error("stamp-type: --paths, --paths-file and --staged are exclusive")`.

`research_vault/capture.py`: delete lines 567-569 (`if any(o.reason == "matched" ...): stamp.stamp_types(vault); okf.regenerate_log(vault)`) and drop `okf` and `stamp` from the import list at `:15-25`. `research_vault/publish.py:24`: `from . import AGENT_ACTOR, Result, fixer, frontmatter, gitstate` (drop `okf`, `stamp`); `_append_log`'s last two statements become `fixer.fix(vault, paths=[f"log/{date}.md"])`. `research_vault/propagate.py` keeps calling `capture.capture` and needs no fixer call: its surfaces are rewritten through the resolver in Task 10.

Docstrings: `structure.py:4-6` — replace “the stamp converges them at chokepoints” with “the fixer converges them when they are staged (§5.1)”. `docs/agents/okf-conformance.md:24`: replace “at capture, at publish and through `stamp-type`” with “through the one fixer, `stamp-type` — run by the commit hook on every fully staged file and by `publish` on the day file it writes”. `:36`'s cost cell: replace “`stamp-type` converges frontmatter at triage” with “the fixer converges frontmatter the first time the file is staged”.

**A known wrinkle, stated here so no executor is surprised.** Under `--staged` the fixer renders root `log.md` from the *worktree's* `log/`, while `check_reserved` compares the candidate's `log.md` with the candidate's `log/`. An untracked day file in the worktree therefore makes the hook demand a `log.md` that names a day the index lacks, and the commit is refused until that day file is staged too; CI, reading HEAD, agrees. That is the right answer — a day file and the log that summarises it travel together — but the message a person sees is "stage `log.md`" when the fix is "stage `log/<day>.md` as well".

- [ ] **Step 7: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS. `tests/test_capture.py::test_a_mid_run_412_stamps_what_was_written_before_the_vault_row` is renamed to `…_writes_the_notes_before_the_vault_row` with the `log.md` assertion removed.

- [ ] **Step 8: Form, commit, branch, close #170 and #174, comment #178**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat docs/agents/okf-conformance.md
git switch -c substrate-a/one-fixer
git commit -m "feat(fixer): stamp-type --paths is the one fixer — type stamp, link normalisation, root log.md; capture and publish drop their vault-wide sweeps (§5.1, #170, #174)" -- research_vault/fixer.py research_vault/okf.py research_vault/structure.py research_vault/stamp.py research_vault/__main__.py research_vault/capture.py research_vault/publish.py research_vault/inbox.py research_vault/searchlog.py docs/agents/okf-conformance.md tests/test_fixer.py tests/test_okf.py tests/test_stamp.py tests/test_verify_cli.py tests/test_capture.py tests/test_publish.py tests/conftest.py
git push -u origin substrate-a/one-fixer
```

After the merge:

```bash
gh issue close 170 --comment "Closed by Plan A Task 6: every write_text in research_vault names utf-8 (okf.py, publish.py, inbox.py, searchlog.py); okf.regenerate_log is tested under LC_ALL=C python -X utf8=0, and an AST test pins the rest."
gh issue close 174 --comment "Closed by Plan A Task 6: an OSError on a stamp write is an 'unwritable' report under the file's path; the walk continues and stamp-type exits 0."
gh issue comment 178 --body "Item 3 (capture's whole-vault stamp sweep) closed by Plan A Task 6: capture no longer stamps or regenerates log.md; stamp-type --paths is the one fixer and writers call it on their own paths."
```

______________________________________________________________________

### Task 7: The commit hook never stages (§5.1, #203, Q1)

**Files:**

- Modify: `research_vault/templates/git/pre-commit` (rewritten)
- Test: `tests/test_precommit.py` (the fake-python contract gains the fixer call and two cases), `tests/test_hooks.py` (the real-hook legs), `tests/test_templates.py:258-286`

**Interfaces:**

- Consumes: Task 6's `stamp-type --staged` output contract (`stamped `, `normalised `, `regenerated ` lines mean "changed"; exit 4 means PyYAML missing).

- Produces: a hook whose only writes are the fixer's worktree rewrites; exit 1 with the changed paths on stderr; exit 4 passed through.

- [ ] **Step 1: Write the failing tests**

Rewrite `tests/test_precommit.py::_fake_python` and the parametrised test:

```python
def _fake_python(tmp_path):
    """A python3 that answers the import probe, the fixer call and the verify
    call separately: the fixer prints FIXER_OUTPUT and exits FIXER_STATUS; the
    verify call records its argv and exits VERIFY_STATUS."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = bin_dir / "python3"
    script.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "-c" ]; then exit 0; fi\n'
        'if [ "$3" = "stamp-type" ]; then\n'
        '  printf "%s\\0" "$@" > "$FIXER_ARGS_FILE"\n'
        '  printf "%s" "${FIXER_OUTPUT:-}"\n'
        '  exit "${FIXER_STATUS:-0}"\n'
        "fi\n"
        'printf "%s\\0" "$@" > "$ARGS_FILE"\n'
        'exit "${VERIFY_STATUS:-0}"\n'
    )
    script.chmod(0o755)
    return bin_dir


@pytest.mark.parametrize(("status", "expected"), [(0, 0), (1, 1), (3, 0), (2, 2), (4, 4)])
@pytest.mark.parametrize("unborn", [False, True])
def test_hook_resolves_one_verified_tree_and_invokes_exact_index_contract(
    tmp_path, status, expected, unborn
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    if not unborn:
        (repo / "base.md").write_text("base\n")
        _git(repo, "add", "base.md")
        _git(repo, "commit", "-qm", "base")
    hook = repo / "pre-commit"
    shutil.copy2(HOOK, hook)
    hook.chmod(0o755)
    args_file = tmp_path / "args"
    fixer_args_file = tmp_path / "fixer-args"
    bin_dir = _fake_python(tmp_path)
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "ARGS_FILE": str(args_file),
        "FIXER_ARGS_FILE": str(fixer_args_file),
        "VERIFY_STATUS": str(status),
    }

    completed = subprocess.run([str(hook)], cwd=repo, env=env, capture_output=True, check=False)

    assert completed.returncode == expected
    fixer_argv = fixer_args_file.read_bytes().split(b"\0")[:-1]
    assert fixer_argv == [b"-m", b"research_vault", b"stamp-type", b"--vault", os.fsencode(repo), b"--staged"]
    argv = args_file.read_bytes().split(b"\0")[:-1]
    assert argv[:5] == [b"-m", b"research_vault", b"verify", b"--vault", os.fsencode(repo)]
    assert argv[5:9] == [b"--offline", b"--surface", b"commit", b"--git-base"]
    base = argv[9].decode()
    assert argv[10:] == [b"--git-candidate", b"index"]
    assert _git(repo, "cat-file", "-e", f"{base}^{{tree}}") == ""
    if unborn:
        assert base == _git(repo, "hash-object", "-w", "-t", "tree", "/dev/null")
    else:
        assert base == _git(repo, "rev-parse", "HEAD")


@pytest.mark.parametrize(
    ("fixer_output", "fixer_status", "expected", "verify_ran"),
    [
        ("stamped daily/d.md\n", 0, 1, False),
        ("normalised projects/p/draft.md\nregenerated log.md\n", 0, 1, False),
        ("skipped inbox/x.md — partially staged; stage the whole file or none of it\n", 0, 0, True),
        ("unresolved projects/p/draft.md — [[gone]] no file matches; resolve by hand\n", 0, 0, True),
        ("", 4, 4, False),
    ],
)
def test_hook_refuses_when_the_fixer_changed_a_file_and_never_stages(
    tmp_path, fixer_output, fixer_status, expected, verify_ran
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "base.md").write_text("base\n")
    _git(repo, "add", "base.md")
    _git(repo, "commit", "-qm", "base")
    hook = repo / "pre-commit"
    shutil.copy2(HOOK, hook)
    hook.chmod(0o755)
    args_file = tmp_path / "args"
    bin_dir = _fake_python(tmp_path)
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "ARGS_FILE": str(args_file),
        "FIXER_ARGS_FILE": str(tmp_path / "fixer-args"),
        "FIXER_OUTPUT": fixer_output,
        "FIXER_STATUS": str(fixer_status),
    }
    completed = subprocess.run([str(hook)], cwd=repo, env=env, capture_output=True, text=True, check=False)
    assert completed.returncode == expected
    assert args_file.exists() is verify_ran
    if expected == 1:
        for path in ("daily/d.md", "projects/p/draft.md", "log.md"):
            if path in fixer_output:
                assert path in completed.stderr
        assert "run the same commit again" in completed.stderr
    if fixer_output.startswith(("skipped", "unresolved")):
        assert fixer_output.strip() in completed.stderr


def test_hook_documents_escape_hatch_and_replay_and_is_executable():
    text = HOOK.read_text()
    assert HOOK.stat().st_mode & os.X_OK
    subprocess.run(["sh", "-n", str(HOOK)], check=True)
    assert "git commit --no-verify" in text
    assert "CI replay" in text
    assert "git add" not in text
    assert "never stages" in text
```

Append to `tests/test_hooks.py` the real-hook legs (designs cluster 3(b)); they shim `python3` to `sys.executable` with the repository on `PYTHONPATH`, so the not-importable branch cannot pass vacuously:

```python
REPO = Path(__file__).resolve().parents[1]


def _hook_env(tmp_path: Path) -> dict[str, str]:
    bin_dir = tmp_path / "hook-bin"
    bin_dir.mkdir()
    shim = bin_dir / "python3"
    shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
    shim.chmod(0o755)
    return {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "PYTHONPATH": str(REPO),
    }


def _commit(vault: Path, env, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "commit", "-q", "-m", "x", *args],
        cwd=vault,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _hook_vault(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    from research_vault import scaffold

    vault = tmp_path / "vault"
    scaffold.scaffold_vault(vault)
    env = _hook_env(tmp_path)
    # The import probe must find research_vault: a hook that cannot import it
    # exits 0 before any assertion below could fail.
    probe = subprocess.run(
        ["python3", "-c", "import research_vault, sys; print(research_vault.__file__)"],
        env=env, capture_output=True, text=True, check=True,
    )
    assert probe.stdout.startswith(str(REPO))
    return vault, env


def _fingerprint(path: Path) -> tuple[bytes, int]:
    return path.read_bytes(), path.stat().st_mtime_ns


def test_real_hook_never_stages_untracked_files(tmp_path):
    vault, env = _hook_vault(tmp_path)
    strays = {
        "log/x.md": "- a hand-typed line\n",
        "inbox/s.md": "a thought\n",
        "literature/stray.md": "no frontmatter\n",
    }
    for relative, text in strays.items():
        (vault / relative).write_text(text)
    before = {relative: _fingerprint(vault / relative) for relative in strays}
    (vault / "projects" / "p").mkdir()
    (vault / "projects" / "p" / "draft.md").write_text('---\ntype: "project"\n---\nbody\n')
    subprocess.run(["git", "add", "projects/p/draft.md"], cwd=vault, env=env, check=True)
    assert _commit(vault, env).returncode == 0
    (vault / "projects" / "p" / "notes.md").write_text('---\ntype: "note"\n---\nbody\n')
    assert _commit(vault, env, "--", "projects/p/notes.md").returncode == 0
    for relative, fingerprint in before.items():
        assert _fingerprint(vault / relative) == fingerprint, relative
    status = subprocess.run(["git", "status", "--porcelain"], cwd=vault, env=env, capture_output=True, text=True, check=True).stdout
    for relative in strays:
        assert f"?? {relative}" in status


def test_real_hook_refuses_a_bare_staged_note_until_it_is_restaged(tmp_path):
    vault, env = _hook_vault(tmp_path)
    (vault / "daily" / "d.md").write_text("a thought\n")
    subprocess.run(["git", "add", "daily/d.md"], cwd=vault, env=env, check=True)
    refused = _commit(vault, env)
    assert refused.returncode == 1
    assert "daily/d.md" in refused.stderr
    assert (vault / "daily" / "d.md").read_text() == '---\ntype: "daily"\n---\na thought\n'
    staged = subprocess.run(["git", "show", ":daily/d.md"], cwd=vault, env=env, capture_output=True, text=True, check=True).stdout
    assert staged == "a thought\n"  # the hook wrote the worktree, never the index
    subprocess.run(["git", "add", "daily/d.md"], cwd=vault, env=env, check=True)
    assert _commit(vault, env).returncode == 0


def test_real_hook_under_a_pathspec_commit_passes_on_the_second_run(tmp_path):
    """`git commit -- <path>` needs the path known to git, so it is added bare
    first; the pathspec commit then builds its temporary index from the
    worktree copy, which the fixer rewrote on the first run."""
    vault, env = _hook_vault(tmp_path)
    (vault / "daily" / "d.md").write_text("a thought\n")
    subprocess.run(["git", "add", "daily/d.md"], cwd=vault, env=env, check=True)
    assert _commit(vault, env, "--", "daily/d.md").returncode == 1
    assert _commit(vault, env, "--", "daily/d.md").returncode == 0
    shown = subprocess.run(["git", "show", "HEAD:daily/d.md"], cwd=vault, env=env, capture_output=True, text=True, check=True).stdout
    assert shown == '---\ntype: "daily"\n---\na thought\n'


def test_real_hook_reports_a_partially_staged_file_and_leaves_it(tmp_path):
    vault, env = _hook_vault(tmp_path)
    note = vault / "daily" / "d.md"
    note.write_text("a\n")
    subprocess.run(["git", "add", "daily/d.md"], cwd=vault, env=env, check=True)
    note.write_text("a\nb\n")
    refused = _commit(vault, env)
    assert refused.returncode == 1
    assert "partially staged" in refused.stderr
    assert "commit-closing verification failed" in refused.stderr  # the bare index copy
    assert note.read_text() == "a\nb\n"


def test_real_hook_regenerates_root_log_and_names_it(tmp_path):
    vault, env = _hook_vault(tmp_path)
    day = vault / "log" / "2026-10-24.md"
    day.write_text('---\ntype: "log"\n---\n- 09:00 research_vault/0.1.0 — a line\n')
    subprocess.run(["git", "add", "log/2026-10-24.md"], cwd=vault, env=env, check=True)
    refused = _commit(vault, env)
    assert refused.returncode == 1
    assert "log.md" in refused.stderr
    assert "a line" in (vault / "log.md").read_text()
    subprocess.run(["git", "add", "log.md"], cwd=vault, env=env, check=True)
    assert _commit(vault, env).returncode == 0
```

Add `import sys` to `tests/test_hooks.py` if absent. In `tests/test_templates.py::test_precommit_hook_is_executable_and_has_exact_contract`, add asserts for `python3 -m research_vault stamp-type --vault "$vault" --staged`, `"git add" not in text`, and `"run the same commit again" in text`.

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_precommit.py tests/test_hooks.py tests/test_templates.py -q -k "hook"`
Expected: FAIL — the hook still stages (`git add` in text) and calls `stamp-type --vault` without `--staged`.

- [ ] **Step 3: The hook**

`research_vault/templates/git/pre-commit` becomes:

```sh
#!/bin/sh
# research-vault pre-commit: the fixer, then the offline commit-closing checks.
# Bypass: git commit --no-verify. CI replays the same checks.
# This hook never stages (#203). It runs the one fixer (stamp-type --staged:
# type stamp, link normalisation, root log.md) on the staged files whose
# worktree copy equals the staged blob, and refuses the commit when the fixer
# changed any of them: stage them and run the same commit again. A partially
# staged file is reported, never rewritten. Under `git commit -- <paths>` the
# fixer sees the temporary index git names in GIT_INDEX_FILE.
# The lifecycle leg is held — verify --offline reports it UNREACHABLE and
# never blocks; ingest spec invariant 5.
vault="$(git rev-parse --show-toplevel)" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "pre-commit: python3 unavailable; refusing an unverifiable commit." >&2
  exit 1
fi
if ! python3 -c "import research_vault" 2>/dev/null; then
  echo "pre-commit: research_vault is not importable; CI will replay verification." >&2
  exit 0
fi

git_base="$(git rev-parse --verify HEAD 2>/dev/null)" ||
  git_base="$(git hash-object -w -t tree /dev/null)" || exit 1
if ! git cat-file -e "$git_base^{tree}"; then
  echo "pre-commit: comparison base is not an available tree." >&2
  exit 1
fi

fixed="$(python3 -m research_vault stamp-type --vault "$vault" --staged)"
fixer_code=$?
if [ "$fixer_code" -ne 0 ]; then
  echo "pre-commit: the fixer exited with status $fixer_code; refusing an unfixed commit." >&2
  exit "$fixer_code"
fi
printf '%s\n' "$fixed" | grep -v -e '^stamped ' -e '^normalised ' -e '^regenerated ' -e '^$' >&2
changed="$(printf '%s\n' "$fixed" | sed -n -e 's/^stamped //p' -e 's/^normalised //p' -e 's/^regenerated //p')"
if [ -n "$changed" ]; then
  echo "pre-commit: the fixer changed these files; stage them and run the same commit again:" >&2
  printf '%s\n' "$changed" | sed 's/^/  /' >&2
  exit 1
fi

python3 -m research_vault verify --vault "$vault" --offline --surface commit --git-base "$git_base" --git-candidate index
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

`grep -v … >&2` relays the fixer's `skipped` and `unresolved` lines to the person and exits 1 when nothing is left; the script is not under `set -e`, so that is harmless. Run `shellcheck research_vault/templates/git/pre-commit` (the dev lane's manual-stage hook does; `shfmt -d` too).

- [ ] **Step 4: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider`
Expected: PASS. The real-hook legs take a few seconds each (git plus two Python processes per commit).

- [ ] **Step 5: Form, commit, branch, close #203**

```bash
shfmt -w research_vault/templates/git/pre-commit && shellcheck research_vault/templates/git/pre-commit
ruff check --fix tests && ruff format tests
git switch -c substrate-a/hook-never-stages
git commit -m "fix(hook): the commit hook never stages — fixer on fully staged files, refuse when it changed any (#203)" -- research_vault/templates/git/pre-commit tests/test_precommit.py tests/test_hooks.py tests/test_templates.py
git push -u origin substrate-a/hook-never-stages
```

After the merge: `gh issue close 203 --comment "Closed by Plan A Task 7: the hook runs stamp-type --staged on the fully staged files, never calls git add, and exits 1 naming the files the fixer changed; a partially staged file is reported, not rewritten. Measured under plain, pathspec and partial commits (tests/test_hooks.py real-hook legs)."`

______________________________________________________________________

### Task 8: Reserved files — `log/` strays, nested `index.md` and `log.md`, root `log.md` byte for byte (#204, #209, #210; Q22–Q24)

**Files:**

- Modify: `research_vault/structure.py:36-42,114-182` (`is_reserved`, `_TOOL_RESERVED_FILES`, `check_log_dir`, `check_reserved` rewritten), `research_vault/verify.py:752-757` (`is_reserved`; `check_log_dir` joins the plan), `research_vault/stamp.py:37,87,105-106` (`is_reserved`)
- Modify: `docs/agents/okf-conformance.md:35` (row 1 widened to `wiki/canvases/index.md`; a new row for `wiki/log.md`)
- Test: `tests/test_structure.py`, `tests/conftest.py:232`, `tests/test_publish.py:110`, `tests/test_verify_cli.py`

**Interfaces:**

- Produces: `structure.RESERVED_NAMES = frozenset({"index.md", "log.md"})`, `structure.is_reserved(relative: str) -> bool`, `structure.check_log_dir(vault_root) -> list[Outcome]` (`tree` rows for directories under `log/`; `okf-structure` rows for non-day entries and off-format lines), `structure.check_reserved(vault_root)` with the rules below. Every row targets the offending file's own path; nothing targets `log.md` for another file's fault.

- Consumes: Task 6's `okf.render_log`, `okf.WRITER_LINE`, `structure.is_day_stem`; Task 2's `read_okf`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_structure.py`:

```python
WRITER = "research_vault/0.1.0"


def _rows(vault, check=None):
    rows = structure.check_reserved(vault) + structure.check_log_dir(vault)
    return [
        (o.check, o.target, o.reason)
        for o in rows
        if o.result is Result.UNMATCHED and (check is None or o.check == check)
    ]


def test_log_dir_reports_strays_under_their_own_paths_never_under_log_md(tmp_path):
    """#204: a non-date file, a compact date, an impossible date, a stray
    heading and a hand-typed line are each a row on their own file."""
    from research_vault import okf

    _scaffold_min(tmp_path)
    log = tmp_path / "log"
    _write(tmp_path, "log/Untitled.md", "- stray\n")
    _write(tmp_path, "log/2026-13-45.md", f'---\ntype: "log"\n---\n- 09:00 {WRITER} — x\n')
    _write(tmp_path, "log/20261004.md", f'---\ntype: "log"\n---\n- 09:00 {WRITER} — x\n')
    _write(tmp_path, "log/2026-10-01.md", f'---\ntype: "log"\n---\n## Agenda\n- 09:00 {WRITER} — real\n- hand-typed\n')
    (log / "nested").mkdir()
    (log / ".gitkeep").touch()
    okf.regenerate_log(tmp_path)
    rows = _rows(tmp_path)
    assert rows == [
        ("okf-structure", "path-bytes:log/2026-10-01.md", "schema-violation — line 1 is not in the writer's format: '## Agenda'"),
        ("okf-structure", "path-bytes:log/2026-10-01.md", "schema-violation — line 3 is not in the writer's format: '- hand-typed'"),
        ("okf-structure", "path-bytes:log/2026-13-45.md", "schema-violation — log/ holds only <YYYY-MM-DD>.md day files and .gitkeep"),
        ("okf-structure", "path-bytes:log/20261004.md", "schema-violation — log/ holds only <YYYY-MM-DD>.md day files and .gitkeep"),
        ("okf-structure", "path-bytes:log/Untitled.md", "schema-violation — log/ holds only <YYYY-MM-DD>.md day files and .gitkeep"),
        ("tree", "log/nested/", "schema-violation — log/ is flat: log/nested/"),
    ]
    assert not any("log.md" in target for _check, target, _reason in rows)


@pytest.mark.parametrize(
    ("relative", "text", "refused"),
    [
        ("wiki/topic/index.md", "", True),  # reserved name under wiki/ outside the tool's files
        ("wiki/other/log.md", "prose, no date headings\n", True),
        ("system/propagations/index.md", "", True),
        ("projects/p/index.md", "Some prose that is not a heading or a list.\n", True),
        ("projects/p/index.md", "# Project\n\n- [draft](draft.md)\n", False),
        ("daily/index.md", "", False),  # an empty nested index is valid (OKF §8, Q22)
        ("daily/log.md", "", False),
        ("daily/log.md", '---\ntype: "log"\n---\n## 2026-10-24\n- x\n', False),
        ("daily/log.md", "---\nnot a mapping\n---\n", True),  # a block that does not parse
        ("daily/log.md", "---\ntype: null\n---\n", True),  # rule 2 when a block is present
        ("wiki/index.md", "---\ntype: meta\ntitle: W\nstatus: s\ncreated: 2026-01-01\nupdated: 2026-01-01\ntags:\n  - m\n---\n# W\n", False),
        ("wiki/log.md", "Prose and bullets, the tool's own shape.\n- entry\n", False),
        ("wiki/canvases/index.md", "---\ntype: meta\ntitle: C\n---\n# C\n", False),
    ],
)
def test_nested_reserved_names_follow_one_shape_rule(tmp_path, relative, text, refused):
    """#209: one body-shape rule for every person-owned folder; the compile
    tool's three files pass by name; any other reserved name under wiki/ or
    system/propagations/ is refused by name until #212's record lands (Q23)."""
    from research_vault import okf

    _scaffold_min(tmp_path)
    _write(tmp_path, relative, text)
    okf.regenerate_log(tmp_path)
    rows = _rows(tmp_path, "okf-structure")
    assert any(relative in target for _c, target, _r in rows) is refused, rows


def test_root_log_md_must_equal_its_render(tmp_path):
    """#210: every edit to the root log — an entry, a removed entry, the
    frontmatter, the heading order, an extra line — is refused naming log.md,
    a missing log.md passes, and the fixer repairs it."""
    from research_vault import fixer, okf

    _scaffold_min(tmp_path)
    _write(tmp_path, "log/2026-10-01.md", f'---\ntype: "log"\n---\n- 09:00 {WRITER} — one\n')
    _write(tmp_path, "log/2026-10-02.md", f'---\ntype: "log"\n---\n- 09:00 {WRITER} — two\n')
    rendered = okf.regenerate_log(tmp_path)
    assert _rows(tmp_path) == []
    for edit in (
        rendered.replace("— one", "— won"),
        rendered.replace(f"- 09:00 {WRITER} — one\n", ""),
        rendered.replace('---\ntype: "log"\n---\n', ""),
        rendered.replace("## 2026-10-02", "## 2026-10-03"),
        rendered + "- a hand-typed line\n",
    ):
        (tmp_path / "log.md").write_text(edit, encoding="utf-8")
        rows = _rows(tmp_path)
        assert rows == [
            ("okf-structure", "path-bytes:log.md", "schema-violation — root log.md differs from its render; run stamp-type, which regenerates it")
        ], edit
    report = fixer.fix(tmp_path, paths=[])
    assert report.log_regenerated is True
    assert _rows(tmp_path) == []
    (tmp_path / "log.md").unlink()
    assert _rows(tmp_path) == []


def test_stamp_leaves_reserved_names_untouched_anywhere(tmp_path):
    from research_vault import stamp

    _write(tmp_path, "log/log.md", "bare\n")
    _write(tmp_path, "projects/p/index.md", "bare\n")
    stamped, _reported = stamp.stamp_types(tmp_path)
    assert stamped == []
    assert (tmp_path / "log" / "log.md").read_text() == "bare\n"
```

Update `tests/test_structure.py::test_reserved_check_exempts_wiki_index_only` so its second half expects the new reason: `assert problems[0].reason == "schema-violation — reserved name under wiki/ outside the compile tool's files (wiki/index.md, wiki/log.md, wiki/canvases/index.md)"`, and its first half still passes `wiki/index.md` by name. `tests/test_structure.py::test_reserved_log_must_be_date_grouped_newest_first` writes a hand-made root `log.md`: it now fails the byte comparison first, so move its text to `daily/log.md` and keep the assertion on the shape reason.

Fixtures: `tests/conftest.py:232` — replace `(tmp_vault / "log.md").write_text("# Log\n")` with a call after the day file is written at `:327`: `okf.regenerate_log(tmp_vault)` (import `okf` from `research_vault` at the top of `conftest.py`). `tests/test_publish.py:110` — replace `(root / "log.md").write_text("# Log\n")` with `okf.regenerate_log(root)` (import `okf`).

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_structure.py -q`
Expected: FAIL — `check_log_dir` missing; the root log compare and the nested rules do not exist.

- [ ] **Step 3: `structure.py`**

Replace `structure.py:37-41` (the `_EXEMPT_INDEXES` comment and constant) with:

```python
RESERVED_NAMES = frozenset({"index.md", "log.md"})
# docs/agents/okf-conformance.md's register, rows 1 and 2: the adopted compile
# tool writes these three reserved-name files with its own shape (frontmatter
# on the two indexes, model-formatted bullets in its log), at hard-coded paths.
# They pass by name; any other reserved name under wiki/ is refused by name
# until the compiled-page record (#212) can say who wrote it.
_TOOL_RESERVED_FILES = frozenset({"wiki/index.md", "wiki/log.md", "wiki/canvases/index.md"})
# Folders whose reserved-name files nobody but a machine writes: a stray one
# is refused outright.
_MACHINE_RESERVED_PREFIXES = ("system/propagations/",)
```

Add after `is_fleeting`:

```python
def is_reserved(relative: str) -> bool:
    """OKF §3.1: `index.md` and `log.md` are reserved at any depth (#209)."""
    return relative.rsplit("/", 1)[-1] in RESERVED_NAMES
```

Replace `_DATE_HEADING` and `_log_shape_problems` (`:114-133`) with:

```python
_DATE_HEADING = re.compile(r"## (?P<day>\S+)\s*$")
_LIST_LINE = re.compile(r"^(?:[-*+] |\d+[.)] )")


def _log_shape_problems(text: str) -> list[str]:
    """§9 log shape: only ``## YYYY-MM-DD`` second-level headings, newest first."""
    try:
        _data, body = frontmatter.read_okf(text)
    except frontmatter.FrontmatterError:
        # frontmatter on log.md is legal but optional (§8 names index.md only)
        body = text
    dates = []
    for line in body.splitlines():
        if line.startswith("## "):
            match = _DATE_HEADING.match(line)
            if not match or not is_day_stem(match.group("day")):
                return [f"non-date second-level heading {line!r}"]
            dates.append(match.group("day"))
    if dates != sorted(dates, reverse=True):
        return ["day headings not newest first"]
    return []


def _index_shape_problems(body: str) -> list[str]:
    """§8 index shape: headings carrying lists of entries; an empty body is
    valid (Q22). Prose outside a heading or a list item is the finding."""
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or _LIST_LINE.match(stripped):
            continue
        return [f"index body line is neither a heading nor a list entry: {stripped!r}"]
    return []


def _okf_structure(relative: str, detail: str) -> Outcome:
    return Outcome(
        "okf-structure", _repo_path(relative), Result.UNMATCHED, f"schema-violation — {detail}"
    )


def check_log_dir(vault_root) -> list[Outcome]:
    """#204: `log/` holds `.gitkeep` and `<YYYY-MM-DD>.md` day files whose body
    lines are the writer's; a directory is a `tree` row and anything else an
    `okf-structure` row under its own path, never under log.md."""
    from . import okf  # noqa: PLC0415 — okf imports structure

    vault = Path(vault_root)
    log_dir = vault / "log"
    if not log_dir.is_dir():
        return []
    rows: list[Outcome] = []
    for child in sorted(log_dir.iterdir()):
        if is_excluded(child, vault) and child.name != ".gitkeep":
            continue
        relative = f"log/{child.name}"
        if child.is_dir():
            rows.append(
                Outcome("tree", f"{relative}/", Result.UNMATCHED, f"schema-violation — log/ is flat: {relative}/")
            )
            continue
        if child.name == ".gitkeep":
            continue
        if child.suffix != ".md" or not is_day_stem(child.stem):
            rows.append(_okf_structure(relative, "log/ holds only <YYYY-MM-DD>.md day files and .gitkeep"))
            continue
        try:
            _data, body = frontmatter.parse(child.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, frontmatter.FrontmatterError):
            continue  # check_note_frontmatter's row
        for number, line in enumerate(body.splitlines(), start=1):
            if line.strip() and not okf.WRITER_LINE.match(line):
                rows.append(
                    _okf_structure(relative, f"line {number} is not in the writer's format: {line!r}")
                )
    return rows
```

Replace `check_reserved` (`:136-182`) with:

```python
def check_reserved(vault_root) -> list[Outcome]:
    """§11 rule 3: index.md per §8/§12, log.md per §9, at any depth (#209, #210)."""
    from . import okf  # noqa: PLC0415 — okf imports structure

    vault = Path(vault_root)
    problems: list[tuple[str, str]] = []
    for path in sorted(vault.rglob("*.md")):
        if is_excluded(path, vault) or path.name not in RESERVED_NAMES:
            continue
        relative = path.relative_to(vault).as_posix()
        if relative.startswith("log/"):
            continue  # check_log_dir's rows
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            problems.append((relative, f"unreadable ({error})"))
            continue
        if relative == "index.md":
            try:
                data, _body = frontmatter.read_okf(text)
            except frontmatter.FrontmatterError as error:
                problems.append((relative, f"unreadable ({error})"))
                continue
            extra = sorted((str(key) for key in set(data) - {"okf_version"}), key=str)
            if extra:
                problems.append((relative, f"root index carries keys beyond okf_version: {extra}"))
            if not str(data.get("okf_version", "")).strip():
                problems.append((relative, "missing okf_version"))
            continue
        if relative == "log.md":
            if text.encode("utf-8") != okf.render_log(vault).encode("utf-8"):
                problems.append(
                    (relative, "root log.md differs from its render; run stamp-type, which regenerates it")
                )
            continue
        if relative in _TOOL_RESERVED_FILES:
            continue
        if relative.startswith("wiki/"):
            problems.append(
                (
                    relative,
                    "reserved name under wiki/ outside the compile tool's files "
                    "(wiki/index.md, wiki/log.md, wiki/canvases/index.md)",
                )
            )
            continue
        if relative.startswith(_MACHINE_RESERVED_PREFIXES):
            problems.append((relative, "reserved name under a machine-written folder"))
            continue
        try:
            data, body = frontmatter.read_okf(text)
        except frontmatter.FrontmatterError as error:
            problems.append((relative, f"frontmatter block does not parse ({error})"))
            continue
        if path.name == "index.md":
            if data:
                problems.append((relative, "nested index.md must be frontmatter-free"))
            problems.extend((relative, p) for p in _index_shape_problems(body))
        else:
            if frontmatter._FRONTMATTER_OPEN.match(text) and not frontmatter.okf_type(data):
                problems.append((relative, "missing type (OKF §11 rule 2)"))
            problems.extend((relative, p) for p in _log_shape_problems(text))
    if problems:
        return [_okf_structure(relative, detail) for relative, detail in problems]
    return [Outcome("okf-structure", "reserved-files", Result.MATCHED, "matched")]
```

The root `log.md` comparison reads the bytes as `read_text` decoded them; the render is written with `newline=""`, so a CRLF edit differs and is refused, which is the intent (#210: byte for byte).

- [ ] **Step 4: The callers**

`research_vault/verify.py:752-757`:

```python
    for path in sorted(vault.rglob("*.md")):
        if structure.is_excluded(path, vault):
            continue
        if structure.is_reserved(path.relative_to(vault).as_posix()):
            continue
        raw.extend(structure.check_note_frontmatter(vault, path))
    raw.extend(structure.check_reserved(vault))
    raw.extend(structure.check_log_dir(vault))
    raw.extend(structure.check_tree(vault))
```

`research_vault/stamp.py`: delete `_SKIP_NAMES` (`:37`); at `:87` replace `path.name in _SKIP_NAMES` with `structure.is_reserved(path.name)`; delete `:105-106` (`if relative == "log.md": continue`).

- [ ] **Step 5: The register rows**

`docs/agents/okf-conformance.md:35` — the first row's deviation cell becomes “Frontmatter on `wiki/index.md` and `wiki/canvases/index.md`, written by the adopted compile tool”, and its cost cell names both paths (“…whose index paths are hard-coded…”, `_TOOL_RESERVED_FILES`). Add a row after it:

```markdown
| `wiki/log.md` as the compile tool writes it: model-formatted bullets, no date headings | OKF §9 (log files are date-grouped, newest first) | 1 — permanent mismatch with the tool's own log (`WIKI.md:120-125` @ 32ac5a0); one file in a machine-owned tree, passed by name (`research_vault/structure.py`, `_TOOL_RESERVED_FILES`), and the vault's own log keeps §9's shape (ruling 7) |
```

- [ ] **Step 6: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS. If `tests/test_verify_cli.py` fixtures hand-write a root `log.md`, switch them to `okf.regenerate_log` as the two above.

- [ ] **Step 7: Form, commit, branch, close #204, #209, #210**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat docs/agents/okf-conformance.md
git switch -c substrate-a/reserved-files
git commit -m "fix(structure): log/ strays, nested reserved names and the root log byte for byte (#204, #209, #210)" -- research_vault/structure.py research_vault/verify.py research_vault/stamp.py docs/agents/okf-conformance.md tests/test_structure.py tests/conftest.py tests/test_publish.py tests/test_verify_cli.py
git push -u origin substrate-a/reserved-files
```

After the merge:

```bash
gh issue close 204 --comment "Closed by Plan A Tasks 6 and 8: render_log reads only calendar-date stems and writer-format lines; check_log_dir files every stray entry, directory and off-format line under its own path, never under log.md."
gh issue close 209 --comment "Closed by Plan A Task 8: one structure.is_reserved check; nested index.md and log.md get OKF's body-shape rules at any depth, an empty one is valid, the compile tool's three files pass by name and any other reserved name under wiki/ or system/propagations/ is refused."
gh issue close 210 --comment "Closed by Plan A Task 8: root log.md must equal okf.render_log byte for byte at commit and publish; a missing one passes; stamp-type regenerates it."
```

______________________________________________________________________

### Task 9: Stray files in `literature/`, and `type: fulltext` is reserved (#211 half, §5.5, Q26)

**Files:**

- Modify: `research_vault/structure.py:74-111,185-219` (`check_note_frontmatter`'s reserved-type test; `check_tree`'s `literature/` rule)
- Modify: `CONTEXT.md:11` and `research_vault/templates/context.md:11`
- Test: `tests/test_structure.py`

**Interfaces:**

- Produces: a `tree` row for any file under `literature/` other than `.gitkeep` and `<safe citation key>.md`; an `okf-frontmatter` row for `type: fulltext` outside `fulltext/`, tested before `inbox/`'s fleeting exemption.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_structure.py`:

```python
def test_check_tree_reports_a_stray_file_under_literature(tmp_path):
    from research_vault import scaffold

    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "literature" / "smith2020.pdf").write_bytes(b"%PDF")
    (tmp_path / "literature" / "notes.txt").write_text("x\n")
    (tmp_path / "literature" / "bad key.md").write_text("x\n")
    (tmp_path / "literature" / "smith2020.md").write_text('---\ntype: "literature"\n---\n')
    (tmp_path / "literature" / ".DS_Store").write_bytes(b"\0")
    rows = [(o.target, o.reason) for o in structure.check_tree(tmp_path) if o.result is Result.UNMATCHED]
    assert rows == [
        ("path-bytes:literature/bad key.md", "schema-violation — literature/ holds only <citation key>.md and .gitkeep: literature/bad key.md"),
        ("path-bytes:literature/notes.txt", "schema-violation — literature/ holds only <citation key>.md and .gitkeep: literature/notes.txt"),
        ("path-bytes:literature/smith2020.pdf", "schema-violation — literature/ holds only <citation key>.md and .gitkeep: literature/smith2020.pdf"),
    ]


def test_stray_file_in_literature_closes_the_commit(tmp_path):
    from research_vault import scaffold, verify

    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "literature" / "paper.pdf").write_bytes(b"%PDF")
    _report, effective, _hashes, warning = verify.verify_state(tmp_path, network=False, git_candidate="worktree")
    decision, blockers = verify.surface_decision("commit", effective, warning)
    assert decision == 1
    assert any("literature/paper.pdf" in b and b.startswith("UNMATCHED tree") for b in blockers)


@pytest.mark.parametrize("relative", ["wiki/x.md", "inbox/moved.md", "projects/p/text.md", "D7EJ9FTG.md"])
def test_type_fulltext_is_reserved_for_the_text_layer(tmp_path, relative):
    """§5.5: a text file an Obsidian rename or Auto Note Mover carried out of
    fulltext/ is refused, before inbox/'s fleeting exemption (Q26)."""
    path = _write(tmp_path, relative, '---\ntype: "fulltext"\nzotero-attachment-key: "D7EJ9FTG"\n---\ntext\n')
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason == "schema-violation — type 'fulltext' is reserved for fulltext/"


def test_a_text_file_in_its_own_layer_still_passes(tmp_path):
    path = _write(tmp_path, "fulltext/D7EJ9FTG.md", '---\ntype: "fulltext"\n---\ntext\n')
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.MATCHED
    assert structure.check_note_frontmatter(tmp_path, _write(tmp_path, "inbox/idea.md", "bare\n")) == []
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_structure.py -q -k "stray or fulltext"`
Expected: FAIL — no tree row for a stray file; `inbox/moved.md` returns `[]`.

- [ ] **Step 3: `structure.py`**

In `check_note_frontmatter`, replace the opening (`:76-90`) so the parse comes first and the reserved type is tested before the fleeting return:

```python
    vault = Path(vault_root)
    relative = Path(path).relative_to(vault).as_posix()
    try:
        data, _body = frontmatter.read_okf(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, frontmatter.FrontmatterError) as error:
        if is_fleeting(relative):
            return []
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                f"schema-violation — frontmatter unparseable ({error})",
            )
        ]
    # §5.5: `type: fulltext` belongs to fulltext/ alone, and the test comes
    # before inbox/'s exemption so a moved text file is refused anywhere (Q26).
    if data.get("type") == "fulltext" and not relative.startswith("fulltext/"):
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                "schema-violation — type 'fulltext' is reserved for fulltext/",
            )
        ]
    if is_fleeting(relative):
        return []
```

In `check_tree` (`:206-218`), replace the `literature.iterdir()` loop with:

```python
    literature = vault / "literature"
    if literature.is_dir():
        from . import literature_notes  # noqa: PLC0415 — literature_notes imports nothing from here

        for child in sorted(literature.iterdir()):
            if is_excluded(child, vault) and child.name != ".gitkeep":
                continue
            relative = f"literature/{child.name}"
            if child.is_dir():
                rows.append(
                    Outcome("tree", f"{relative}/", Result.UNMATCHED, f"schema-violation — literature/ is flat: {relative}/")
                )
                continue
            if child.name == ".gitkeep":
                continue
            safe = child.suffix == ".md"
            if safe:
                try:
                    literature_notes.note_path(vault, child.stem)
                except literature_notes.InvalidCitationKeyError:
                    safe = False
            if not safe:
                rows.append(
                    Outcome(
                        "tree",
                        _repo_path(relative),
                        Result.UNMATCHED,
                        f"schema-violation — literature/ holds only <citation key>.md and .gitkeep: {relative}",
                    )
                )
    return rows
```

`CONTEXT.md:11` and `research_vault/templates/context.md:11`: replace `` `fulltext/` notes carry `type: fulltext` by construction. `` with `` `fulltext/` notes carry `type: fulltext` by construction, and that type is reserved for them: a text file moved anywhere else is refused at commit. ``

- [ ] **Step 4: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider`
Expected: PASS (`tests/test_structure.py:200-214`'s nested-directory rows keep their exact shape).

- [ ] **Step 5: Form, commit, branch**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat CONTEXT.md research_vault/templates/context.md
git switch -c substrate-a/literature-strays
git commit -m "fix(structure): a stray file under literature/ is a tree row; type fulltext is reserved for fulltext/ (#211, §5.5)" -- research_vault/structure.py CONTEXT.md research_vault/templates/context.md tests/test_structure.py
git push -u origin substrate-a/literature-strays
```

#211 stays open: its `fulltext/` half (a force-added text on a committed candidate) lands in Plan C with `text-layer`.

______________________________________________________________________

### Task 10: The link form everywhere else — `propagate`, the literature body, the seed, the skills, the formatter lists, the register (§5.2 callers, §4.5)

**Files:**

- Modify: `research_vault/links.py` (append `names_note`, `rewrite_key`), `research_vault/propagate.py:49-58,284-304` (through the resolver), `research_vault/literature_notes.py:419-449` (`render_body`), `research_vault/templates/vault/index.md:9,15,19`, `research_vault/templates/vault/prettierignore`, `…/markdownlintignore`, `…/editorconfig`
- Modify: `skills/synthesis-conventions/SKILL.md:8,24`, `skills/capture-source/SKILL.md:54,62,74`, `skills/setup-vault/SKILL.md:42`, `docs/agents/okf-conformance.md:41`
- Test: `tests/test_links.py`, `tests/test_propagate.py:234-245`, `tests/test_literature_notes.py:462-488`, `tests/test_capture.py:134`, `tests/test_capture_source_skill.py:43,58`, `tests/test_templates.py:85-101,214-256`, `tests/test_scaffold.py:95-108`

**Interfaces:**

- Produces: `links.names_note(target: str, key: str, *, source: str) -> bool` — whether a link target names `literature/<key>.md` in any of its spellings (`key`, `literature/key`, `/literature/key.md`, `../literature/key.md` from `source`); `links.rewrite_key(text: str, old: str, new: str, *, source: str) -> str` — every link naming the old key renamed, wiki form kept as wiki, markdown form re-pointed at `/literature/<new>.md`, display text `old` → `new`. `propagate._names` and `propagate.rewrite_surfaces` use them.

- Consumes: Task 4's `find_links`, `is_uri`, `_encode`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_links.py`:

```python
@pytest.mark.parametrize(
    ("target", "named"),
    [
        ("old2020", True),
        ("literature/old2020", True),
        ("literature/old2020.md", True),
        ("/literature/old2020.md", True),
        ("../literature/old2020.md", True),  # from wiki/sources/A.md
        ("old2020a", False),
        ("concepts/old2020", False),
        ("https://x.org/old2020", False),
    ],
)
def test_names_note_recognises_every_spelling_of_a_literature_link(target, named):
    assert links.names_note(target, "old2020", source="wiki/sources/A.md") is named


def test_rewrite_key_renames_wiki_and_markdown_links_and_display_text():
    text = (
        "[[old2020]] [[old2020#^c-1]] [[old2020|alias]] [old2020](/literature/old2020.md) "
        "[shown](literature/old2020.md#^c-1) [x](../literature/old2020.md) "
        "[[old2020a]] [other](/literature/other2020.md) ![[old2020]]\n"
    )
    assert links.rewrite_key(text, "old2020", "new2020", source="wiki/sources/A.md") == (
        "[[new2020]] [[new2020#^c-1]] [[new2020|alias]] [new2020](/literature/new2020.md) "
        "[shown](/literature/new2020.md#^c-1) [x](/literature/new2020.md) "
        "[[old2020a]] [other](/literature/other2020.md) ![[new2020]]\n"
    )
```

In `tests/test_propagate.py::_seed`, extend the draft's text and the wiki page so the rewrite test covers the markdown form:

```python
        '---\ntype: "project"\n---\nSee [@old2020, p. 3] and [@old2020] and [[old2020]] and [[old2020#^c-1]] and [[old2020|alias]] and [old2020](/literature/old2020.md#^c-1).\n'
```

and `wiki/sources/A.md`: `"---\ntype: source\n---\n[[old2020]] and [../literature/old2020.md](../literature/old2020.md) and [[older2020]]\n"`. Update the expectations at `:141`, `:240` accordingly (`[new2020](/literature/new2020.md#^c-1)`; `[../literature/old2020.md](/literature/new2020.md)` — the display text is not the key, so it stays) and `test_rewrite_surfaces_touches_every_citation_and_wikilink_shape` asserts both files.

`tests/test_literature_notes.py:462-488` — the body pins become `text layer [D7EJ9FTG](/fulltext/D7EJ9FTG.md)` and `![](/wiki/sources/Co-Writing%20with%20Opinionated%20Language%20Models.md)`; `tests/test_capture.py:134` becomes `"## Compiled\n\n![](/wiki/sources/Co-Writing.md)\n\n## Item\n"`. `tests/test_capture_source_skill.py:43` needle `"![[<page path>]]"` → `"![](/<page path>)"`; `:58` needle `"[[<citation key>]]"` → `"[<citation key>](/literature/<citation key>.md)"`. `tests/test_templates.py:85-101` and `tests/test_scaffold.py:95-108`: the three index lines become `- [log/](log/) — daily activity log (summary: [log](/log.md))`, `![](/system/bases/trust-tier.base)`, `![](/system/bases/open-questions.base)`. `tests/test_templates.py:214-222`: `_MACHINE_SURFACES` gains `"/wiki/"`, `"/log.md"`, `"/system/compiled-pages.json"`, and the editorconfig derivation becomes:

```python
    for surface in _MACHINE_SURFACES:
        relative = surface.removeprefix("/")
        if relative.endswith("/"):
            glob = f"{relative}**"
        elif "/" in relative:
            glob = relative
        else:
            glob = surface  # a root file keeps its leading slash: that is what anchors it
        assert f"[{glob}]" in editorconfig, (surface, glob)
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_links.py tests/test_propagate.py tests/test_literature_notes.py tests/test_capture.py tests/test_capture_source_skill.py tests/test_templates.py tests/test_scaffold.py -q -k "names_note or rewrite_key or rewrite_surfaces or body or Compiled or synthesis or capture_source or canonical or formatter or index"`
Expected: FAIL on every pin above.

- [ ] **Step 3: `links.names_note` and `links.rewrite_key`**

Append to `research_vault/links.py`:

```python
# --- re-key support for propagate (§5.2 callers, item 2) ------------------------


def names_note(target: str, key: str, *, source: str) -> bool:
    """Whether a link target names ``literature/<key>.md`` in any spelling
    Obsidian or a person writes: the bare key, ``literature/<key>``, with or
    without ``.md``, ``/``-led, or relative to ``source``."""
    raw = urllib.parse.unquote(target.strip()).replace("\\", "/")
    if not raw or is_uri(raw):
        return False
    if raw.startswith(("./", "../")):
        raw = posixpath.normpath(posixpath.join(posixpath.dirname(source), raw))
    raw = raw.lstrip("/")
    if raw.endswith(".md"):
        raw = raw[: -len(".md")]
    return raw in {key, f"literature/{key}"}


def rewrite_key(text: str, old: str, new: str, *, source: str) -> str:
    """Rename every link naming ``old``: a wikilink keeps its form, a markdown
    link is re-pointed at ``/literature/<new>.md`` with its subpath, and a
    display text equal to the old key becomes the new one."""
    pieces: list[str] = []
    cursor = 0
    for link in find_links(text):
        if link.start < cursor or not names_note(link.target, old, source=source):
            continue
        bang = "!" if link.embed else ""
        if link.kind == "wiki":
            alias = f"|{link.alias}" if link.alias is not None else ""
            replacement = f"{bang}[[{new}{link.subpath}{alias}]]"
        else:
            shown = new if link.alias == old else (link.alias or "")
            replacement = f"{bang}[{shown}](/literature/{_encode(new)}.md{_encode(link.subpath)})"
        pieces.append(text[cursor : link.start])
        pieces.append(replacement)
        cursor = link.end
    pieces.append(text[cursor:])
    return "".join(pieces)
```

- [ ] **Step 4: `propagate` through the resolver**

`research_vault/propagate.py:49-58` becomes:

```python
def _cite_pattern(old: str) -> tuple[re.Pattern[str], str]:
    return re.compile(rf"\[@{re.escape(old)}(?=[\],\s])"), "[@{new}"


def _names(text: str, old: str, source: str) -> bool:
    pattern, _template = _cite_pattern(old)
    return pattern.search(text) is not None or any(
        links.names_note(link.target, old, source=source) for link in links.find_links(text)
    )
```

with `links` added to `propagate.py:23`'s import. `plan` (`:223`) passes the surface: `if not any(_names(text, old, relative) for old in mapping)`. `rewrite_surfaces` (`:295-297`) becomes:

```python
        pattern, template = _cite_pattern(old)
        rewritten = pattern.sub(template.format(new=new), text)
        rewritten = links.rewrite_key(rewritten, old, new, source=relative)
```

and `lint_propagation` (`:475`) passes `relative` to `_names`.

- [ ] **Step 5: The literature body, the seed, the skills, the lists, the register**

`research_vault/literature_notes.py:425` → `lines.extend(f"![](/{links._encode(page)})" for page in pages)`; `:440` → `line += f", text layer [{child['key']}](/fulltext/{child['key']}.md)"`; `literature_notes.py:11` imports `links` (`links` imports `structure` only; no cycle). `research_vault/templates/vault/index.md:9,15,19`: `(summary: [log](/log.md))`, `![](/system/bases/trust-tier.base)`, `![](/system/bases/open-questions.base)`.

`research_vault/templates/vault/prettierignore` and `markdownlintignore` each gain, after `/system/propagations/`:

```
/wiki/
/log.md
/system/compiled-pages.json
```

and the header comment's `plus fulltext/ (capture's derived text layer)` continues `, plus wiki/ (the compile tool's pages, sealed by hash), root log.md (the fixer's render) and system/compiled-pages.json (the compiled-page record)`. `editorconfig` gains three sections before the closing blank line:

```
[wiki/**]
insert_final_newline = false
trim_trailing_whitespace = false

[/log.md]
insert_final_newline = false
trim_trailing_whitespace = false

[system/compiled-pages.json]
insert_final_newline = false
trim_trailing_whitespace = false
```

and its header comment's surface list names the three.

Skills — `skills/synthesis-conventions/SKILL.md:8`: replace `` every page cites its source as `[[<citation key>]]`, which resolves to `literature/<citation key>.md` `` with `` every page links its source as `[<citation key>](/literature/<citation key>.md)` — the markdown form with a `/`-led vault path, which the commit hook's fixer keeps (research-vault's link form; OKF §6.1) ``; `:24`: `` at least one of them a `[<citation key>](/literature/<citation key>.md)` ``. `skills/capture-source/SKILL.md:54`: `` every `[@old]` citation and every link to `literature/old.md` dangles ``; `:62`: `` rewrites `[@key]` citations and the links that name the note in drafts and wiki pages ``; `:74`: `` the note now embeds the compiled page, `![](/<page path>)`, ``. `skills/setup-vault/SKILL.md:42`: `` Every `[<citation key>](/literature/<citation key>.md)` link resolves as before ``. `skills/evidence-conventions/SKILL.md` is unchanged: claim links stay `[[citation-key#^claim-id]]`.

`docs/agents/okf-conformance.md:41` — the cost cell becomes “1 — the vault's three frozen claim readers require the wikilink form: `FIELD_RE` (`research_vault/claims.py:12`) rejects single brackets, `CLAIM_LINK` (`research_vault/lints.py:24`) reads only the double-bracket form, and the claim-immutability byte comparison freezes a committed claim's bytes; the link normaliser skips anchored claim blocks whole (spec §5.2, Q19)”.

- [ ] **Step 6: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS. `tests/test_templates.py::test_markdown_templates_match_canonical_content` and `tests/test_scaffold.py:95-108` pin `index.md` byte for byte; both were updated in Step 1.

- [ ] **Step 7: Form, commit, branch**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat skills/synthesis-conventions/SKILL.md skills/capture-source/SKILL.md skills/setup-vault/SKILL.md docs/agents/okf-conformance.md
git switch -c substrate-a/link-form-callers
git commit -m "feat(links): the markdown link form everywhere — propagate through the resolver, the literature body, the seed index, the skills, the formatter lists (§5.2, §4.5)" -- research_vault/links.py research_vault/propagate.py research_vault/literature_notes.py research_vault/templates/vault/index.md research_vault/templates/vault/prettierignore research_vault/templates/vault/markdownlintignore research_vault/templates/vault/editorconfig skills/synthesis-conventions/SKILL.md skills/capture-source/SKILL.md skills/setup-vault/SKILL.md docs/agents/okf-conformance.md tests/test_links.py tests/test_propagate.py tests/test_literature_notes.py tests/test_capture.py tests/test_capture_source_skill.py tests/test_templates.py tests/test_scaffold.py
git push -u origin substrate-a/link-form-callers
```

______________________________________________________________________

### Task 11: The whole-plan review, the baseline, the spec's §7 amendment

**Files:**

- Modify: `mutation-baseline.txt` (survivor triage), `docs/superpowers/specs/2026-10-03-substrate-components-design.md` (§7: the `pyyaml` probe id, dated)

- Tracker: the issues this plan closed are verified closed; findings a review will not fix become issues

- [ ] **Step 1: Verify every task merged and every closed issue is closed**

```bash
git fetch origin && git status -sb
for n in 170 174 194 203 204 208 209 210; do gh issue view $n --json state --jq ".state"; done
gh issue view 178 --comments --jq '.comments[-1].body' | head -3
```

Expected: `main` equal to `origin/main`; every listed issue `CLOSED`; #178's last comment is Task 6's.

- [ ] **Step 2: The mutation gate on the plan's modules**

Run the gate locally over the modules this plan touched, from a clean tree:

```bash
python scripts/mutation_gate.py --base $(git merge-base origin/main $(git rev-parse HEAD~40)) --max-children 2 --child-address-space 3GiB --max-mutants 9000
```

If the diff is oversize, run it per module with `--modules research_vault/links.py research_vault/fixer.py …` (read `scripts/mutation_gate.py --help` for the flag's exact name). For each survivor: write a test that kills it, or accept it with `--update-baseline` and a `# reason:` line above the key naming why the mutant is equivalent or unreachable. Never accept a survivor in `links.py`'s resolver or `fixer.staged_paths` without a stated reason: both decide what the commit hook rewrites.

- [ ] **Step 3: The whole-plan review**

Use the superpowers:requesting-code-review skill over `git diff <merge-base of Task 1's branch>..main -- research_vault tests hooks docs skills`. Every Concern becomes a commit on a `substrate-a/review-fixes` branch or an issue titled `substrate plan A review: <finding>` with label `ready-for-agent`. The workspace closes when none is left unfiled.

- [ ] **Step 4: The spec's §7 amendment**

In `docs/superpowers/specs/2026-10-03-substrate-components-design.md` §7, append after the first paragraph:

```markdown
*Amended 2026-10-24 (Plan A Task 2):* doctor probe ids `pyyaml` (§5.6's PyYAML row) and, from Plan C, `deny-rules` (§6.2's deny-list row) join `docs/agents/terminology.md` §4.4's doctor-probe row; §7 had coined neither.
```

```bash
mdformat docs/superpowers/specs/2026-10-03-substrate-components-design.md
git switch -c substrate-a/close
git commit -m "docs(spec): lanes 2-3 §7 — the pyyaml and deny-rules probe ids (Plan A Task 11)" -- docs/superpowers/specs/2026-10-03-substrate-components-design.md mutation-baseline.txt
git push -u origin substrate-a/close
```

Merge `--ff-only` when green. Plan B opens from this `main`.

______________________________________________________________________

## Coverage notes

- §5.1 (#203): Task 7, with Task 6 supplying the fixer and the dropped sweeps (#178 item 3).
- §5.2: Tasks 4, 5 and 10; #208 in Task 4; the claim-link register row's reason in Task 10.
- §5.5: #204 Tasks 6 and 8; #209 and #210 Task 8; #211's `literature/` half and the reserved `fulltext` type Task 9; OS litter Task 1; #174 and #170 Task 6. #207 and #211's `fulltext/` half are Plan C's.
- §5.6 (#194): Tasks 1 and 2.
- §4.4: Task 3. §4.5's formatter lists: Task 10.
- §11 amendments this plan owns: `CONTEXT.md` (Tasks 3, 9), `docs/agents/okf-conformance.md` (Tasks 2, 6, 8, 10), `docs/agents/terminology.md` (Tasks 2, 4), `pyproject.toml` PyYAML (Task 2), the pre-lane-2 and assembly status lines (Task 0), the skills' link instructions (Task 10), the spec's §7 (Task 11).
- Not here, by design: the capture monitor and the publish re-check (Plan B), the compiled-page record, `text-layer` and the deny rules (Plan C), the add-on declaration and doctor rows beyond `pyyaml` (Plan D), the seed (Plan E).
