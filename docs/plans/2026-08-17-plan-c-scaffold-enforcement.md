# Plan C: Vault Scaffold + Enforcement Surfaces — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A fresh vault scaffolded by one command; a doctor that verifies and repairs the substrate (including the first **live** autoexport registration — discharging Plan A's oldest caveat); the enforcement surfaces of spec §6 wired: pre-commit, CI workflows, the plugin's PostToolUse warn hook, and the Stop-hook publish gate.

**Architecture:** Templates ship *inside* the Python package (`harness_core/templates/`, importlib.resources) so the CLI is self-contained; `scaffold` and `doctor` are CLI verbs beside the existing eight; hooks are thin Python scripts under the plugin's `hooks/`, registered in `hooks/hooks.json` (`${CLAUDE_PLUGIN_ROOT}` command pattern per the installed-plugin precedent), calling the same CLI — one binary, one exit-code contract (spec §7).

**Tech Stack:** Python ≥3.10 stdlib; templates as package data; GitHub Actions YAML; plugin `hooks/hooks.json`.

**Spec:** `docs/specs/2026-08-16-foundation-spec.md` (§3 tree/conventions, §6 surfaces + doctrine, §7 vault-setup/doctor scope, §8 plugin layout). **Hook-contract authority:** the vendored Claude Code docs at `~/.claude/plugins/cache/superpowers-developing-for-claude-code-dev/*/*/skills/working-with-claude-code/references/hooks.md` (locate with `find ~/.claude/plugins/cache -iname hooks.md` if the layout shifts) — where this plan's hook I/O shape disagrees with those docs, the docs govern and the implementer adapts within-task, recording it in the commit message.

## Global Constraints

- **As-built HEAD governs** over this plan's code where they disagree (same rule as Plan B). Consumed surfaces at `238fd27`: CLI verbs `probe / import-note / staleness / backfill-selectors / verify / inbox` (all `parents=[common]`, `--base`); `CLOSING_CHECKS = {"citekey", "quote", "update-notice", "evidence-layer"}` — **this plan splits it per surface** (spec §6 closes different rows at different surfaces): `COMMIT_CLOSING = {"citekey", "evidence-layer"}` (the only rows the table closes at pre-commit/CI) and `PUBLISH_CLOSING = {"citekey", "evidence-layer", "quote", "update-notice", "doi"}` (DOI closes at publish on UNMATCHED or UNREACHABLE — it was missing from the flat set). Implement as a `surface` parameter on the shared `_verify_state`/`cmd_verify` decision (`verify --surface commit|publish`, default `commit`); pre-commit uses commit, the Stop gate uses publish. `cmd_verify` exit contract 0/1/3 (1 = surface-closing UNMATCHED only); `inbox.summary(vault) -> {"unacknowledged", "oldest"}`; `notes.canonical_content`; `ZoteroClient.register_autoexport(target_path)` sending `["//", CSL_TRANSLATOR, target_path]` — **live-unverified until this plan's doctor runs it** (the standing caveat this plan discharges).
- **Four-state doctrine** (§6): doctor reports per-probe `MATCHED | UNMATCHED | UNREACHABLE | SKIPPED`; outage never reported as breakage of the vault.
- **Fail-open everywhere except the armed publish gate** (§6): PostToolUse warns only and must never break a session (crash ⇒ exit 0, empty output); the Stop gate blocks only while armed, with the 8-block bound and a bypass token recorded to the review inbox.
- **Publish = the skill action** (§6): the gate arms via `.harness/publish-pending.json`, written by Plan D's `publish` skill; the Stop hook is inert without it.
- **No absolute paths in committed vault content**; `.harness/` is gitignored by the scaffold's own `.gitignore`.
- **Consent for installs** (§7): vault-setup's provisioning is detect → report → per-item consent → install/guide → verify; Zotero `.xpi` installs are human-only wizard steps; companions are a build-time constant list of {plugin, marketplace} pairs (`PROVISION_COMPANIONS`).
- Worktree via `superpowers:using-git-worktrees`, branch `build/plan-c`; test Runs begin `cd core && python3 -m venv .venv 2>/dev/null; source .venv/bin/activate` (bootstrap on first use, PEP 668); commits from the worktree root.
- Reason codes and inbox/event semantics exactly as Plan B built them (validated prefixes).

## File Structure

```
core/harness_core/
├── templates/                      # package data (Task 1)
│   ├── vault/                      # tree skeleton, mirrored by scaffold
│   │   ├── AGENTS.md               # vault facts + routing (§3/§8 gray-zone line)
│   │   ├── gitignore               # -> .gitignore (dot-stripped on copy)
│   │   ├── atlas/index.md
│   │   ├── calendar/.keep  +/.keep  literatures/.keep  efforts/.keep
│   │   └── x/
│   │       ├── templates/{literature,topic,effort,daily}.md
│   │       └── bases/{open-questions,trust-tier}.base
│   ├── harness/machine.json.example
│   ├── git/pre-commit              # installed to .git/hooks/pre-commit
│   └── ci/{verify.yml,rw-batch.yml}
├── scaffold.py                     # scaffold + doctor logic (Tasks 2–3)
└── __main__.py                     # + scaffold / doctor verbs (Tasks 2–3, modify)
hooks/
├── hooks.json                      # PostToolUse + Stop registration (Task 6)
├── posttooluse_lint.py             # warn hook (Task 5)
└── stop_publish_gate.py            # armed gate (Task 6)
skills/vault-setup/SKILL.md         # the one Plan-C skill (Task 7)
core/tests/{test_scaffold,test_doctor,test_precommit,test_hooks,test_ci_templates}.py
```

---

### Task 1: Packaged templates

**Files:**
- Create: everything under `core/harness_core/templates/` per the tree above
- Modify: `core/pyproject.toml` (package data: `[tool.setuptools.package-data] harness_core = ["templates/**/*", "templates/**/.keep"]`)
- Test: `core/tests/test_templates.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `importlib.resources.files("harness_core") / "templates"` resolvable; template contents below are the canonical texts later tasks copy.

Key template contents (write exactly; `{{PLACEHOLDER}}` tokens are replaced by scaffold):

```markdown
<!-- templates/vault/AGENTS.md -->
# Vault agents guide

This is a knowledge-harness vault (spec: knowledge-harness/docs/specs/). Facts:

- Evidence lives in `literatures/` — machine-projected from Zotero, never free-written; the only admission path for citable sources is Zotero (a human act) followed by `/knowledge-harness:import-source`.
- Claims carry evidence-boundary tags, `[@citekey, locator]`, and `^claim-id` anchors; quotes are blockquotes. Run `/knowledge-harness:evidence-conventions` for the rules.
- Drafting, verifying, publishing go through the knowledge-harness skills (`/knowledge-harness:project`, `…:verify-citations`, `…:publish`) — in this vault, prefer them over generic drafting even for free-form requests (routing per spec §8: this line is the gray-zone mitigation).
- The review inbox is `+/review-queue.md`; orientation surfaces unacknowledged count + age.
- `.harness/` is machine-local (gitignored): machine.json (path map, mailto), publish flag, counters.
```

```markdown
<!-- templates/vault/x/templates/literature.md -->
---
citekey: "{{CITEKEY}}"
type: "literature"
retrieved: "{{TODAY}}"
status: "unreviewed"
aliases:
  - "{{TITLE}}"
---
%%hk-managed%%
# {{TITLE}}
%%/hk-managed%%

## Notes
```

```markdown
<!-- templates/vault/x/templates/topic.md -->
---
title: "{{TITLE}}"
type: "topic"
growth: "seedling"
planted: "{{TODAY}}"
last-tended: "{{TODAY}}"
---
```

```markdown
<!-- templates/vault/x/templates/effort.md -->
---
title: "{{TITLE}}"
type: "effort"
status: "drafting"
---
```

```markdown
<!-- templates/vault/x/templates/daily.md -->
---
type: "daily"
---
<!-- calendar/YYYY-MM-DD.md — append-only; entries: - HH:MM <actor> — <action> [links] -->
```

```yaml
# templates/vault/x/bases/open-questions.base
views:
  - type: table
    name: Open questions
filters:
  and:
    - 'type == "topic"'
formulas:
  open_q: 'file.content.contains("(open-question)")'
```

```yaml
# templates/vault/x/bases/trust-tier.base
views:
  - type: table
    name: Trust tier
filters:
  and:
    - 'type == "literature"'
```

(The `.base` files are structural stubs pinned to the documented Bases schema; Bases queries over inline claim fields are limited to frontmatter per the spec's §5 carrier note — the views list notes by `type` and the tier column derives from `verified` at build-review time. If the installed Obsidian Bases schema rejects a stub, fix the stub against `obsidian:obsidian-bases` vendored docs — docs govern.)

```gitignore
# templates/vault/gitignore
.harness/
.obsidian/workspace*
```

```json
// templates/harness/machine.json.example  (annotation line — not file content)
{
  "mailto": "you@example.edu",
  "path_map": { "D:\\Zotero\\": "/mnt/d/Zotero/" }
}
```

`templates/vault/atlas/index.md`:

```markdown
# Atlas index

<!-- one line per topic page: - [[name]] — gist (growth, last-tended) -->
```

`templates/git/pre-commit` and `templates/ci/*.yml` are written ONCE, **in this task**, from the code blocks shown in Tasks 3 and 4 (single-owner content, authored there for the reader; **the Task 1 implementer's brief must include Tasks 3–4's code blocks**). Tasks 3–4 verify the content, never rewrite it.

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_templates.py
from importlib import resources


def tpl(*parts):
    return resources.files("harness_core").joinpath("templates", *parts)


def test_tree_complete():
    for rel in [
        ("vault", "AGENTS.md"), ("vault", "gitignore"),
        ("vault", "atlas", "index.md"),
        ("vault", "x", "templates", "literature.md"),
        ("vault", "x", "templates", "topic.md"),
        ("vault", "x", "templates", "effort.md"),
        ("vault", "x", "templates", "daily.md"),
        ("vault", "x", "bases", "open-questions.base"),
        ("vault", "x", "bases", "trust-tier.base"),
        ("harness", "machine.json.example"),
        ("git", "pre-commit"),
        ("ci", "verify.yml"), ("ci", "rw-batch.yml"),
    ]:
        assert tpl(*rel).is_file(), rel


def test_agents_md_carries_routing_line():
    text = tpl("vault", "AGENTS.md").read_text()
    assert "gray-zone" in text and "review-queue.md" in text


def test_literature_template_matches_schema():
    text = tpl("vault", "x", "templates", "literature.md").read_text()
    for token in ('citekey: "{{CITEKEY}}"', 'status: "unreviewed"',
                  "%%hk-managed%%", "## Notes"):
        assert token in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python3 -m venv .venv 2>/dev/null; source .venv/bin/activate && pip install -e ".[dev]" -q && python -m pytest tests/test_templates.py -v`
Expected: FAIL — missing template files

- [ ] **Step 3: Write all template files + package-data config** (contents above; pre-commit/CI contents from Tasks 3–4 code blocks)

- [ ] **Step 4: Run test to verify it passes** — `python -m pytest tests/test_templates.py -v` — 3 PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: packaged vault templates"
```

---

### Task 2: `scaffold` verb

**Files:**
- Create: `core/harness_core/scaffold.py`
- Modify: `core/harness_core/__main__.py` (verb wiring)
- Test: `core/tests/test_scaffold.py`

**Interfaces:**
- Consumes: templates (Task 1); `bibliography.BIB_PATH`.
- Produces:
  - `scaffold_vault(dest: Path, with_ci: bool = False) -> list[str]` — creates the §3 tree from templates (dot-stripping `gitignore` → `.gitignore`); copies `machine.json.example` to `.harness/machine.json` only when absent (never overwrites); installs `templates/git/pre-commit` to `.git/hooks/pre-commit` (executable); `with_ci` copies `ci/*.yml` to `.github/workflows/`; `git init` + initial commit when no repo. **Idempotent**: existing files are never overwritten; returns the list of paths it actually created (empty on a fully scaffolded vault).
  - CLI `scaffold --vault <path> [--with-ci]` — prints created paths; exit 0.

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_scaffold.py
import os
import subprocess

from harness_core import scaffold


def test_scaffold_fresh(tmp_path):
    created = scaffold.scaffold_vault(tmp_path)
    for rel in ("+", "literatures", "atlas", "calendar", "efforts", "x",
                ".gitignore", "AGENTS.md", ".harness/machine.json",
                ".git/hooks/pre-commit", "x/templates/literature.md",
                "x/bases/trust-tier.base", "atlas/index.md"):
        assert (tmp_path / rel).exists(), rel
    assert os.access(tmp_path / ".git" / "hooks" / "pre-commit", os.X_OK)
    tracked = subprocess.run(["git", "ls-files"], cwd=tmp_path,
                             capture_output=True, text=True).stdout
    for d in ("literatures", "calendar", "efforts"):
        assert f"{d}/.keep" in tracked      # empty dirs survive a fresh clone
    assert ".harness/" in (tmp_path / ".gitignore").read_text()
    log = subprocess.run(["git", "log", "--oneline"], cwd=tmp_path,
                         capture_output=True, text=True).stdout
    assert "scaffold" in log
    assert created  # non-empty on fresh


def test_scaffold_idempotent_never_overwrites(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "AGENTS.md").write_text("customized\n")
    (tmp_path / ".harness" / "machine.json").write_text('{"mailto": "real@x.edu"}')
    created = scaffold.scaffold_vault(tmp_path)
    assert created == []
    assert (tmp_path / "AGENTS.md").read_text() == "customized\n"
    assert "real@x.edu" in (tmp_path / ".harness" / "machine.json").read_text()


def test_scaffold_with_ci(tmp_path):
    scaffold.scaffold_vault(tmp_path, with_ci=True)
    assert (tmp_path / ".github" / "workflows" / "verify.yml").is_file()
    assert (tmp_path / ".github" / "workflows" / "rw-batch.yml").is_file()
```

- [ ] **Step 2: Run to verify failure** — `python -m pytest tests/test_scaffold.py -v` — FAIL, no module

- [ ] **Step 3: Implement**

```python
# core/harness_core/scaffold.py
"""Vault scaffolding + doctor (spec §3 tree, §7 vault-setup scope)."""
import os
import shutil
import subprocess
from importlib import resources
from pathlib import Path

VAULT_DIRS = ["+", "literatures", "atlas", "calendar", "efforts",
              "x/templates", "x/bases"]


def _templates():
    return resources.files("harness_core").joinpath("templates")


def _copy_if_absent(src, dest: Path, created: list, executable=False):
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(str(src), dest)
    if executable:
        os.chmod(dest, 0o755)
    created.append(str(dest))


def scaffold_vault(dest, with_ci=False) -> list[str]:
    dest = Path(dest)
    created: list[str] = []
    for d in VAULT_DIRS:
        p = dest / d
        if not p.is_dir():
            p.mkdir(parents=True)
            created.append(str(p))
    t = _templates()
    vault_t = t / "vault"
    for entry in ("AGENTS.md", "atlas/index.md",
                  "x/templates/literature.md", "x/templates/topic.md",
                  "x/templates/effort.md", "x/templates/daily.md",
                  "x/bases/open-questions.base", "x/bases/trust-tier.base"):
        _copy_if_absent(vault_t / entry, dest / entry, created)
    _copy_if_absent(vault_t / "gitignore", dest / ".gitignore", created)
    _copy_if_absent(t / "harness" / "machine.json.example",
                    dest / ".harness" / "machine.json", created)
    if not (dest / "+" / "review-queue.md").exists():
        (dest / "+" / "review-queue.md").write_text("")
        created.append(str(dest / "+" / "review-queue.md"))
    for d in ("literatures", "calendar", "efforts"):   # empty dirs must survive
        keep = dest / d / ".keep"                      # a fresh clone (CI checkout)
        if not keep.exists():
            keep.write_text("")
            created.append(str(keep))
    if not (dest / ".git").is_dir():
        subprocess.run(["git", "init", "-q"], cwd=dest, check=True)
        created.append(str(dest / ".git"))
    _copy_if_absent(t / "git" / "pre-commit",
                    dest / ".git" / "hooks" / "pre-commit", created,
                    executable=True)
    if with_ci:
        for wf in ("verify.yml", "rw-batch.yml"):
            _copy_if_absent(t / "ci" / wf,
                            dest / ".github" / "workflows" / wf, created)
    if created:
        subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=dest)
        if r.returncode != 0:
            # --no-verify: the bookkeeping commit must not be blocked by the
            # pre-commit hook this very call installs (a vault scaffolded with
            # pre-existing closing failures would otherwise error in setup)
            subprocess.run(["git", "commit", "-q", "--no-verify", "-m",
                            "chore: scaffold vault"], cwd=dest, check=True)
    return created
```

CLI wiring in `main()`: `scaffold` subparser (`--vault` required, `--with-ci` flag) → `cmd_scaffold` printing created paths, return 0.

- [ ] **Step 4: Run to verify pass** — 3 PASS
- [ ] **Step 5: Commit** — `git add core && git commit -m "feat: scaffold verb — idempotent vault creation"`

---

### Task 3: `doctor` verb + pre-commit content (live autoexport registration)

**Files:**
- Modify: `core/harness_core/scaffold.py` (doctor), `core/harness_core/__main__.py`
- Modify: `core/harness_core/bibliography.py` — **`write_and_commit` commits with `--no-verify`** (machine bookkeeping commit of `x/bibliography.json` only; sandbox-confirmed: without it, doctor's bootstrap is blocked by the very pre-commit hook scaffold installs whenever the vault carries a pre-existing closing failure — doctor crashing in exactly the scenario it repairs). Regression test: doctor bootstraps on a vault containing a fabricated-citekey draft.
- Content authored here, **already written in Task 1** (verify, do not rewrite): `core/harness_core/templates/git/pre-commit`
- Test: `core/tests/test_doctor.py`

**Interfaces:**
- Consumes: `ZoteroClient` (`ready`, `register_autoexport`, `export_csl`), `bibliography` (`BIB_PATH`, `staleness`, `write_and_commit`), `webapi.mailto`, `inbox.summary`.
- Produces:
  - `doctor(vault_root, client=None, network=True) -> list[Probe]` where `Probe = (name, Result, detail)`. Probes, in order: `tree` (all §3 dirs present — repairs by scaffolding missing pieces); `machine-config` (mailto set and not the example placeholder); `zotero` (ready() — UNREACHABLE when down; detail carries versions); `bbt` (betterbibtex key present); `autoexport` (**the caveat-discharger**: when `x/bibliography.json` is absent or staleness is UNMATCHED, call `register_autoexport(str(vault/x/bibliography.json))` — on RPC error record UNMATCHED with the raw error in detail so the signature question surfaces loudly; then bootstrap via `write_and_commit(vault, export_csl(None))`); `staleness` (post-repair state); `remote` (git remote exists — UNMATCHED *warn* with the §2 endurance text when absent); `backup` (machine.json `zotero_backup` key documented — UNMATCHED warn when absent); `inbox` (summary; UNMATCHED warn when unacknowledged > 0 with count+oldest in detail).
  - Exit contract: 0 all MATCHED/SKIPPED-or-warn-only; 1 any hard UNMATCHED (`tree`, `machine-config`, `autoexport`, `bbt` — BBT is REQUIRED, the skill says so); 3 any **hard-probe** UNREACHABLE (`zotero`, `bbt`, `autoexport`) — warn-class probes never affect exit even when UNREACHABLE (staleness can flake with Zotero up). `remote`/`backup`/`inbox`/`staleness` are warn-class (never affect exit) — doctor prints them prefixed `warn:`.
  - The pre-commit template (Task 1 file, content owned here):

```bash
#!/bin/sh
# knowledge-harness pre-commit: offline closing checks (spec §6).
# Bypass: git commit --no-verify  (CI replays these checks as the honest layer.)
vault="$(git rev-parse --show-toplevel)"
# Fail-open when the CLI is not importable by commit-time python3 — a broken
# install must not block commits; CI replays as the honest layer. Residual
# honestly noted: a mid-run traceback also exits 1 and will read as a closing
# failure until investigated.
python3 -c "import harness_core" 2>/dev/null || exit 0
python3 -m harness_core verify --vault "$vault" --offline --surface commit
code=$?
if [ "$code" -eq 1 ]; then
  echo "pre-commit: closing-class verification failure (see above)." >&2
  echo "Bypass with --no-verify; CI will replay these checks." >&2
  exit 1
fi
exit 0   # UNREACHABLE (3) and warn-tier stay open at commit time (§6)
```

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_doctor.py
import json

from harness_core import Result, scaffold


class StubClient:
    def __init__(self, up=True):
        self.up = up
        self.registered = []
        self.items = [{"id": "smith2020", "title": "Mortality decline",
                       "type": "article-journal"}]

    def ready(self):
        if not self.up:
            from harness_core.zotero import ZoteroError
            raise ZoteroError("down")
        return {"zotero": "9.0.6", "betterbibtex": "9.0.55"}

    def register_autoexport(self, path):
        self.registered.append(path)
        return {"path": path}

    def export_csl(self, citekeys):
        if not self.up:
            from harness_core.zotero import ZoteroError
            raise ZoteroError("down")
        return self.items


def _configured(vault):
    (vault / ".harness" / "machine.json").write_text(
        json.dumps({"mailto": "real@x.edu", "zotero_backup": "cloud sync"}))


def test_doctor_registers_autoexport_and_bootstraps(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    _configured(tmp_path)
    client = StubClient()
    probes = {p[0]: p for p in scaffold.doctor(tmp_path, client=client)}
    assert client.registered and client.registered[0].endswith(
        "x/bibliography.json")
    assert probes["autoexport"][1] is Result.MATCHED
    assert (tmp_path / "x" / "bibliography.json").is_file()
    assert probes["staleness"][1] is Result.MATCHED


def test_doctor_placeholder_mailto_is_hard_unmatched(tmp_path):
    scaffold.scaffold_vault(tmp_path)   # machine.json is the example copy
    probes = {p[0]: p for p in scaffold.doctor(tmp_path, client=StubClient())}
    assert probes["machine-config"][1] is Result.UNMATCHED


def test_doctor_zotero_down_is_unreachable(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    _configured(tmp_path)
    probes = {p[0]: p for p in scaffold.doctor(tmp_path,
                                               client=StubClient(up=False))}
    assert probes["zotero"][1] is Result.UNREACHABLE
    assert probes["autoexport"][1] is Result.UNREACHABLE


def test_doctor_warns_without_remote(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    _configured(tmp_path)
    probes = {p[0]: p for p in scaffold.doctor(tmp_path, client=StubClient())}
    assert probes["remote"][1] is Result.UNMATCHED   # warn-class
```

- [ ] **Step 2: Run to verify failure** — `AttributeError: doctor`

- [ ] **Step 3: Implement** (append to `scaffold.py`)

```python
# append to core/harness_core/scaffold.py
import json

from . import Result
from . import bibliography, inbox
from .zotero import ZoteroClient, ZoteroError

HARD_PROBES = {"tree", "machine-config", "autoexport", "bbt"}
WARN_PROBES = {"remote", "backup", "inbox", "staleness"}


def doctor(vault_root, client=None, network=True):
    vault = Path(vault_root)
    client = client or ZoteroClient()
    probes = []

    missing = [d for d in VAULT_DIRS if not (vault / d).is_dir()]
    if missing:
        scaffold_vault(vault)
    probes.append(("tree", Result.MATCHED,
                   f"repaired: {missing}" if missing else "complete"))

    try:
        cfg = json.loads((vault / ".harness" / "machine.json").read_text())
    except (OSError, ValueError):
        cfg = {}
    mailto = cfg.get("mailto", "")
    probes.append(("machine-config",
                   Result.MATCHED if mailto and "example" not in mailto
                   else Result.UNMATCHED,
                   mailto or "mailto missing"))

    zotero_up = False
    try:
        info = client.ready()
        zotero_up = True
        probes.append(("zotero", Result.MATCHED, str(info)))
        probes.append(("bbt",
                       Result.MATCHED if info.get("betterbibtex")
                       else Result.UNMATCHED, str(info.get("betterbibtex"))))
    except ZoteroError as e:
        probes.append(("zotero", Result.UNREACHABLE, str(e)))
        probes.append(("bbt", Result.UNREACHABLE, "zotero down"))

    bib_file = vault / bibliography.BIB_PATH
    if not zotero_up:
        probes.append(("autoexport", Result.UNREACHABLE, "zotero down"))
        probes.append(("staleness", Result.UNREACHABLE, "zotero down"))
    else:
        state = bibliography.staleness(vault, client)
        if not bib_file.is_file() or state is Result.UNMATCHED:
            try:
                reply = client.register_autoexport(str(bib_file))
                bibliography.write_and_commit(vault, client.export_csl(None))
                probes.append(("autoexport", Result.MATCHED,
                               f"registered + bootstrapped: {reply}"))
            except ZoteroError as e:
                probes.append(("autoexport", Result.UNMATCHED,
                               f"registration failed: {e}"))
        elif state is Result.UNREACHABLE:
            probes.append(("autoexport", Result.UNREACHABLE,
                           "staleness probe flaked"))
        else:
            probes.append(("autoexport", Result.MATCHED, "already fresh"))
        probes.append(("staleness", bibliography.staleness(vault, client),
                       "post-repair"))

    has_remote = subprocess.run(["git", "remote"], cwd=vault,
                                capture_output=True, text=True).stdout.strip()
    probes.append(("remote",
                   Result.MATCHED if has_remote else Result.UNMATCHED,
                   has_remote or "no remote — vault endures only on this disk (§2)"))
    probes.append(("backup",
                   Result.MATCHED if cfg.get("zotero_backup")
                   else Result.UNMATCHED,
                   cfg.get("zotero_backup",
                           "no stated Zotero storage backup (§2 boundary)")))
    s = inbox.summary(vault)
    probes.append(("inbox",
                   Result.MATCHED if not s["unacknowledged"] else Result.UNMATCHED,
                   f"{s['unacknowledged']} unacknowledged, oldest {s['oldest']}"))
    return probes
```

`cmd_doctor`: print each probe (`warn:` prefix for WARN_PROBES with UNMATCHED); exit 1 on hard UNMATCHED, 3 on UNREACHABLE, else 0. Wire `doctor` subparser (`--vault`, `parents=[common]`).

- [ ] **Step 4: Run to verify pass** — 4 PASS
- [ ] **Step 5: Commit** — `git add core && git commit -m "feat: doctor verb — substrate probes, live autoexport repair path, warn-class boundaries"`

---

### Task 4: CI workflow templates + pre-commit test

**Files:**
- Content **authored here, already written in Task 1** (the Task 1 implementer receives Tasks 3–4's code blocks): `templates/ci/verify.yml`, `templates/ci/rw-batch.yml` — verify against the blocks below, do not rewrite
- Test: `core/tests/test_precommit.py`, `core/tests/test_ci_templates.py`

**Interfaces:** consumes the CLI contract only.

```yaml
# templates/ci/verify.yml
name: verify
on: [push]
jobs:
  offline-verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install harness-core --find-links https://github.com/eranroseman/knowledge-harness/releases || pip install "harness-core @ git+https://github.com/eranroseman/knowledge-harness.git#subdirectory=core"
      - run: python -m harness_core verify --vault . --offline
```

```yaml
# templates/ci/rw-batch.yml
name: rw-batch
on:
  schedule: [{ cron: "17 3 * * *" }]
  workflow_dispatch: {}
jobs:
  retraction-batch:
    runs-on: ubuntu-latest
    permissions: { contents: write }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install "harness-core @ git+https://github.com/eranroseman/knowledge-harness.git#subdirectory=core"
      - run: curl -sL -o /tmp/rw.csv https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv
      - run: python -m harness_core verify --vault . --offline --rw-csv /tmp/rw.csv || true
      - run: |
          git config user.name "harness-ci"
          git config user.email "actions@users.noreply.github.com"
          git add "+/review-queue.md" && git diff --cached --quiet || git commit -m "chore: rw-batch findings" && git push
```

(`--offline --rw-csv`: the batch leg is offline once the CSV is local; `HARNESS_MAILTO` is unneeded. The `|| true` keeps the scheduled job from failing on findings — findings are inbox entries, the async-auditor role, §6.)

- [ ] **Step 1: Write the failing tests**

```python
# core/tests/test_ci_templates.py
from importlib import resources


def test_workflows_are_valid_yaml_shaped():
    # stdlib-only: structural string checks, not a YAML parser
    for name, must in (("verify.yml", ["on: [push]", "verify --vault . --offline"]),
                       ("rw-batch.yml", ["schedule", "--rw-csv /tmp/rw.csv",
                                         "review-queue.md"])):
        text = resources.files("harness_core").joinpath(
            "templates", "ci", name).read_text()
        for frag in must:
            assert frag in text, (name, frag)
```

```python
# core/tests/test_precommit.py
import subprocess

from harness_core import scaffold


def test_precommit_blocks_fabricated_citekey(fixture_vault):
    scaffold.scaffold_vault(fixture_vault)      # installs the hook
    # bibliography exists in fixture; the draft cites fabricated2020 → closing UNMATCHED
    (fixture_vault / "efforts" / "brief" / "note.md").write_text(
        "- (inference) Bad cite [@fabricated2020] ^c-ab12cd34\n")
    subprocess.run(["git", "add", "-A"], cwd=fixture_vault, check=True)
    r = subprocess.run(["git", "commit", "-m", "should be blocked"],
                       cwd=fixture_vault, capture_output=True, text=True)
    assert r.returncode != 0
    assert "closing-class" in r.stderr


def test_precommit_bypass_no_verify(fixture_vault):
    scaffold.scaffold_vault(fixture_vault)
    (fixture_vault / "efforts" / "brief" / "note.md").write_text(
        "- (inference) Bad cite [@fabricated2020] ^c-ab12cd34\n")
    subprocess.run(["git", "add", "-A"], cwd=fixture_vault, check=True)
    r = subprocess.run(["git", "commit", "--no-verify", "-m", "bypassed"],
                       cwd=fixture_vault, capture_output=True, text=True)
    assert r.returncode == 0
```

(The pre-commit hook invokes `python3 -m harness_core`; the test environment's venv must be active so the module resolves — the Run step below activates it, and the hook inherits the environment.)

- [ ] **Step 2: Run the tests — expected GREEN immediately** (sandbox-confirmed: with Tasks 1–2 done, both pre-commit tests and test_ci_templates pass at once; this task is the first end-to-end verification of already-shipped content, not a red step — green here is correct, not suspicious)
- [ ] **Step 3: Verify the Task 1 file contents match the blocks above**; fix any divergence
- [ ] **Step 4: Run to verify pass** — `python -m pytest tests/test_precommit.py tests/test_ci_templates.py -v` — 3 PASS
- [ ] **Step 5: Commit** — `git add core && git commit -m "feat: pre-commit closing gate + CI replay and rw-batch workflows"`

---

### Task 5: PostToolUse warn hook

**Files:**
- Create: `hooks/posttooluse_lint.py`
- Test: `core/tests/test_hooks.py`

**Interfaces:**
- Consumes: CLI `verify --offline` machinery via direct import (`harness_core` on `sys.path` — the hook prepends the plugin's `core/` dir).
- Produces: a script reading the hook's stdin JSON (`tool_input.file_path` for Edit/Write per the vendored hooks docs — **verify field names against those docs; docs govern**), that: walks up from the file for a `.harness/` dir (not-a-vault ⇒ exit 0 silently); runs the per-file offline checks (`check_citekeys`, `check_all_quotes`, source-status/contested lints); prints a one-line `additionalContext`-style JSON warning listing failures; **always exits 0** (PostToolUse warns only, §6); any internal exception ⇒ exit 0, no output (fail-open, Global Constraints).

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_hooks.py
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "posttooluse_lint.py"


def _run_hook(payload):
    return subprocess.run([sys.executable, str(HOOK)],
                          input=json.dumps(payload), capture_output=True,
                          text=True)


def test_non_vault_file_is_silent(tmp_path):
    f = tmp_path / "x.md"
    f.write_text("- (quote) [@nobody2020] ^c-1\n")
    r = _run_hook({"tool_input": {"file_path": str(f)}})
    assert r.returncode == 0 and r.stdout.strip() == ""


def test_vault_file_with_bad_citekey_warns(fixture_vault):
    (fixture_vault / ".harness").mkdir(exist_ok=True)
    f = fixture_vault / "efforts" / "brief" / "draft.md"
    f.write_text(f.read_text() +
                 "- (inference) Bad [@fabricated2020] ^c-deadbeef\n")
    r = _run_hook({"tool_input": {"file_path": str(f)}})
    assert r.returncode == 0
    out = json.loads(r.stdout)
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert out["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert "fabricated2020" in ctx


def test_malformed_stdin_fails_open():
    r = subprocess.run([sys.executable, str(HOOK)], input="not json",
                       capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.strip() == ""
```

- [ ] **Step 2: Run to verify failure** — hook file absent
- [ ] **Step 3: Implement**

```python
#!/usr/bin/env python3
# hooks/posttooluse_lint.py — PostToolUse warn surface (spec §6: warns only,
# never blocks, fail-open). Field names per the vendored Claude Code hooks
# docs; adapt there if the schema differs — docs govern.
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))


def main():
    try:
        payload = json.load(sys.stdin)
        file_path = Path(payload.get("tool_input", {}).get("file_path", ""))
        if not file_path.is_file() or file_path.suffix != ".md":
            return
        vault = None
        for parent in file_path.parents:
            if (parent / ".harness").is_dir():
                vault = parent
                break
        if vault is None:
            return
        from harness_core import Result
        from harness_core.checks import check_citekeys
        from harness_core.lints import lint_contested, lint_source_status
        from harness_core.quotes import check_all_quotes
        # evidence-layer surface (§6 row: PostToolUse warn): free-writes into
        # literatures/ or edits inside managed regions — locate the as-built
        # evidence-layer check at HEAD (grep "evidence-layer" core/) and call
        # it per-file here; HEAD governs its exact name/signature
        from harness_core.lints import evidence_layer_findings
        findings = []
        for o in (check_citekeys(vault, file_path)
                  + check_all_quotes(vault, file_path)
                  + lint_source_status(vault, file_path)
                  + lint_contested(vault, file_path)
                  + evidence_layer_findings(vault, file_path)):
            if o.result is Result.UNMATCHED:
                findings.append(f"{o.check} {o.target}: {o.reason}")
        if findings:
            # documented PostToolUse shape (hooks.md): plain stdout at exit 0 is
            # transcript-only; context must ride hookSpecificOutput
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext":
                    "knowledge-harness warnings: " + "; ".join(findings)}}))
    except Exception:
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)
```

- [ ] **Step 4: Run to verify pass** — 3 PASS
- [ ] **Step 5: Commit** — `git add hooks core && git commit -m "feat: PostToolUse warn hook — vault detection, fail-open"`

---

### Task 6: Stop-hook publish gate + hooks.json

**Files:**
- Create: `hooks/stop_publish_gate.py`, `hooks/hooks.json`
- Test: `core/tests/test_hooks.py` (append)

**Interfaces:**
- Consumes: the CLI's **effective** verification state — as-built `run_verify` returns raw pre-acknowledgment outcomes while `cmd_verify`'s 0/1/3 exit is computed over acknowledgment-suppressed (`effective`) outcomes (HEAD `__main__.py`). The gate must apply the SAME rule as `cmd_verify`: within-task, either extend `run_verify` to also return the effective outcome list, or refactor the shared decision into one function (`_verify_state`) both consume — acknowledged findings must not block the gate the CLI passes. Also `CLOSING_CHECKS`, `inbox.append_entry`.
- Produces:
  - Flag file contract (Plan D's `publish` skill writes it): `.harness/publish-pending.json` = `{"effort": "efforts/<name>", "vault": "<abs path>", "blocks": 0}`.
  - `hooks/stop_publish_gate.py`: reads stdin JSON; locates the flag by `vault` recorded in `~/.harness-active-publish` pointer? No — simpler: the hook reads `payload.get("cwd") or os.getcwd()` (the docs list `cwd` as a common field but the Stop example omits it; hooks run in Claude Code's cwd, so the fallback is documented-safe); looks for `.harness/publish-pending.json` iterating `[cwd, *cwd.parents]` — the directory ITSELF first (`Path.parents` alone excludes it; the session cwd typically IS the vault root, which would leave the gate permanently inert). Absent ⇒ exit 0 (inert). On every armed run (pass or block), the run's SKIPPED outcomes append to the review inbox (§6: publish-gate runs stay auditable). Present ⇒ run the shared decision with `surface="publish"` (`PUBLISH_CLOSING` — includes `doi`, per §6's publish row); **publish-closing UNMATCHED or any UNREACHABLE ⇒ block** (§6: the armed gate fails closed on outage — publishing waits): emit the hooks-docs blocking JSON (`{"decision": "block", "reason": "..."}` — **verify shape against the vendored docs; docs govern**), increment `blocks` in the flag; at `blocks >= 8` ⇒ stop blocking: exit 0 emitting the documented `systemMessage` common field (`{"systemMessage": "publish gate: 8 blocks reached, verification still failing — flag left in place"}` — plain stdout at exit 0 is transcript-only, systemMessage is shown to the user), leave the flag. Pass ⇒ delete the flag, exit 0. A bypass token in the flag (`"bypass": "<reason>"`) ⇒ record a `manual — publish-gate bypass: <reason>` inbox entry, delete flag, exit 0.
  - `hooks/hooks.json`:

```json
{
  "description": "knowledge-harness enforcement surfaces (spec §6).",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/posttooluse_lint.py\"",
            "timeout": 20 }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/stop_publish_gate.py\"",
            "timeout": 120 }
        ]
      }
    ]
  }
}
```

- [ ] **Step 1: Write the failing test (append to test_hooks.py)**

```python
GATE = REPO / "hooks" / "stop_publish_gate.py"


def _run_gate(cwd):
    return subprocess.run([sys.executable, str(GATE)],
                          input=json.dumps({"cwd": str(cwd)}),
                          capture_output=True, text=True)


def test_gate_inert_without_flag(fixture_vault):
    r = _run_gate(fixture_vault)
    assert r.returncode == 0 and r.stdout.strip() == ""


def test_gate_blocks_on_closing_failure(fixture_vault, monkeypatch):
    (fixture_vault / ".harness").mkdir(exist_ok=True)
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(draft.read_text() +
                     "- (inference) Bad [@fabricated2020] ^c-deadbeef\n")
    (fixture_vault / ".harness" / "publish-pending.json").write_text(json.dumps(
        {"effort": "efforts/brief", "vault": str(fixture_vault), "blocks": 0}))
    env = {"HARNESS_GATE_OFFLINE": "1"}  # test knob: gate uses network=False
    # (offline injects a staleness UNREACHABLE — the knob also suppresses
    # UNREACHABLE-blocking for network-disabled outcomes so the closing-class
    # path is what this test exercises; see the knob contract below)
    r = subprocess.run([sys.executable, str(GATE)],
                       input=json.dumps({"cwd": str(fixture_vault)}),
                       capture_output=True, text=True,
                       env={**__import__("os").environ, **env})
    out = json.loads(r.stdout)
    assert out["decision"] == "block"
    assert "fabricated2020" in out["reason"]
    flag = json.loads(
        (fixture_vault / ".harness" / "publish-pending.json").read_text())
    assert flag["blocks"] == 1


def test_gate_bypass_records_inbox_and_clears(fixture_vault):
    from harness_core import inbox
    (fixture_vault / ".harness").mkdir(exist_ok=True)
    (fixture_vault / ".harness" / "publish-pending.json").write_text(json.dumps(
        {"effort": "efforts/brief", "vault": str(fixture_vault), "blocks": 3,
         "bypass": "conference deadline, verified by hand"}))
    r = _run_gate(fixture_vault)
    assert r.returncode == 0
    assert not (fixture_vault / ".harness" / "publish-pending.json").exists()
    assert any(e.reason.startswith("manual — publish-gate bypass")
               for e in inbox.load(fixture_vault))
```

(`HARNESS_GATE_OFFLINE=1` is a **test-only knob**: the gate runs `network=False` AND ignores UNREACHABLE outcomes whose reason is `outage — network disabled` — otherwise the knob-injected staleness outage would make every knob run block and the pass path would be untestable. Knob read only from the environment, documented in the script header; production is network-on with full UNREACHABLE fail-closed. Add a third gate test: a clean fixture (no fabricated citekey) with the knob ⇒ gate passes, flag deleted, exit 0.)

- [ ] **Step 2: Run to verify failure** — gate file absent
- [ ] **Step 3: Implement `stop_publish_gate.py`** (per the Produces contract; ~60 lines mirroring the PostToolUse structure: stdin JSON → walk up from `cwd` for `.harness/publish-pending.json` → offline knob → `run_verify` → decide block/pass/bypass → flag bookkeeping; blocking output `{"decision": "block", "reason": ...}` printed to stdout; every other path exits 0 silently; internal exception while ARMED prints a block decision with the exception as reason — an armed gate fails closed, the one exception to fail-open)
- [ ] **Step 4: Run to verify pass** — all test_hooks.py PASS
- [ ] **Step 5: Commit** — `git add hooks core && git commit -m "feat: Stop-hook publish gate — armed via flag, 8-block bound, bypass to inbox"`

---

### Task 7: vault-setup skill + provisioning constants

**Files:**
- Create: `skills/vault-setup/SKILL.md`
- Modify: `core/harness_core/scaffold.py` (add `PROVISION_COMPANIONS = [{"plugin": "obsidian@obsidian-skills", "marketplace": "kepano/obsidian-skills"}, {"plugin": "*", "marketplace": "mattpocock/skills"}]` — `"*"` means: after the consent-gated `marketplace add`, list that marketplace's plugins and offer each individually; the mattpocock set is the process-skill companion the #11 doctrine allows as install-never-depend)
- Test: `core/tests/test_skill_files.py`

**Interfaces:** the SKILL.md is the §7-decided entry point (user-typed): frontmatter `name: vault-setup`, `description` (vault-scoped trigger text), `disable-model-invocation: true`. Body (write it fully — this is content, not code):

```markdown
---
name: vault-setup
description: Scaffold or repair a knowledge-harness vault - creates the folder tree, templates, Bases, AGENTS.md, git hooks, and CI; verifies and repairs the Zotero/BBT substrate (doctor mode). Use in or for a research vault.
disable-model-invocation: true
---

# vault-setup

One-time scaffold + recurring doctor for a knowledge-harness vault (spec §3/§7).

## Steps

1. **Locate or create the vault.** Ask for the target path if not given.
   **Ask the human** whether this vault has or will have a GitHub remote
   (spec §7: setup asks — CI is skipped without one); add `--with-ci` on yes.
   Run: `python3 -m harness_core scaffold --vault <path> [--with-ci]`.
   Scaffold is idempotent — safe on existing vaults; never overwrites.
2. **Configure the machine file.** Open `.harness/machine.json`; the human fills
   `mailto` (a real address — polite API pools require it) and the Zotero path
   map if attachments live on another drive. Record their Zotero backup
   arrangement in `zotero_backup`.
3. **Run doctor.** `python3 -m harness_core doctor --vault <path>`. Walk through
   every probe with the human; doctor repairs what it can (tree, autoexport
   registration, bibliography bootstrap) and reports what it cannot.
4. **Human-only installs (wizard steps — never attempt these yourself):**
   - Better BibTeX (REQUIRED — citekeys do not exist without it): Zotero →
     Tools → Plugins → install the BBT `.xpi` from retorque.re. Then re-run
     doctor.
   - MarkDB-Connect (OPTIONAL — marks Zotero items that have vault notes):
     same flow with the MarkDB-Connect `.xpi`.
5. **Companion plugins (per-item consent).** Offer each entry in
   `PROVISION_COMPANIONS`: plugin `obsidian@obsidian-skills` from marketplace
   `kepano/obsidian-skills` (vault format/ops), and the `mattpocock/skills`
   marketplace (process skills — grilling, domain-modeling, wayfinder, … ;
   optional enrichment per the dependency doctrine: install-never-depend).
   On consent run BOTH steps (install alone fails where the marketplace was
   never added): `claude plugin marketplace add <marketplace>`, then for a
   `"*"` entry list that marketplace's plugins and offer each individually,
   else `claude plugin install <plugin>`; a restart activates them.
   Never install without the offer.
6. **Finish.** Re-run doctor; read the warn-class probes aloud (remote, backup,
   inbox age) — they are standing conditions, not failures. The vault is ready
   when doctor exits 0.
```

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_skill_files.py
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_vault_setup_skill_frontmatter():
    text = (REPO / "skills" / "vault-setup" / "SKILL.md").read_text()
    assert text.startswith("---\n")
    head = text.split("---")[1]
    assert "name: vault-setup" in head
    assert "disable-model-invocation: true" in head
    assert "scaffold --vault" in text and "doctor --vault" in text
    assert ".xpi" in text            # wizard steps present


def test_provision_companions_constant():
    from harness_core import scaffold
    assert scaffold.PROVISION_COMPANIONS == [
        {"plugin": "obsidian@obsidian-skills",
         "marketplace": "kepano/obsidian-skills"},
        {"plugin": "*", "marketplace": "mattpocock/skills"}]
```

- [ ] **Step 2–4:** fail (file absent) → write SKILL.md + constant → 2 PASS
- [ ] **Step 5: Commit** — `git add skills core && git commit -m "feat: vault-setup skill — scaffold/doctor flow, wizard installs, consent-gated companions"`

---

### Task 8: Live end-to-end — the caveat discharge

**Files:**
- Test: `core/tests/test_scaffold_live.py`

- [ ] **Step 1: Write the live test**

```python
# core/tests/test_scaffold_live.py
import json
import subprocess
import sys

import pytest

from harness_core import Result, scaffold
from harness_core.zotero import ZoteroClient


@pytest.mark.live
def test_scaffold_doctor_end_to_end(tmp_path):
    import os
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / ".harness" / "machine.json").write_text(json.dumps(
        {"mailto": os.environ.get("HARNESS_MAILTO", "dev@localhost"),
         "zotero_backup": "documented elsewhere"}))
    probes = {p[0]: p for p in scaffold.doctor(tmp_path, client=ZoteroClient())}
    # THE CAVEAT DISCHARGE: first live autoexport registration
    assert probes["autoexport"][1] is Result.MATCHED, probes["autoexport"][2]
    assert probes["staleness"][1] is Result.MATCHED
    assert (tmp_path / "x" / "bibliography.json").is_file()
    # import one real item end to end through the scaffolded vault
    items = ZoteroClient().export_csl(None)
    citekey = items[0]["id"]
    r = subprocess.run([sys.executable, "-m", "harness_core", "import-note",
                        citekey, "--vault", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "literatures" / f"{citekey}.md").is_file()
```

- [ ] **Step 2: Run it live**

Run: `cd core && source .venv/bin/activate && HARNESS_LIVE=1 python -m pytest tests/test_scaffold_live.py -v`
Expected: PASS. **If `autoexport` probe reads UNMATCHED, the detail carries BBT's raw RPC error — fix `register_autoexport`'s parameter shape in `zotero.py` against the BBT JSON-RPC doc within this task** (the ruling that has waited since Plan A: the live call is the authority). After PASS: append to `docs/environment.md` — "BBT `autoexport.add` live-verified (date, accepted signature); Plan A caveat discharged" — and verify in the Zotero UI (human step, note it in the task report) that the auto-export appears under BBT preferences — then **remove the test registration there** (each live run registers an auto-export against a deleted tmp_path; without cleanup, dead entries accumulate one per run — note this in docs/environment.md).

- [ ] **Step 3: Full suite + commit**

Run: `cd core && source .venv/bin/activate && HARNESS_LIVE=1 python -m pytest tests -q`
Expected: all PASS.

```bash
cd "$(git rev-parse --show-toplevel)"
git add core docs/environment.md && git commit -m "feat: live scaffold+doctor drill — autoexport registration verified, Plan A caveat discharged"
```

---

### Task 9: Merge

- [ ] Full suite green (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>`), then `superpowers:finishing-a-development-branch`.

---

## Pre-execution batched rulings (all approved, 2026-08-20)

1. **Byte-preserving git paths**: NUL-delimited `git ls-tree`, surrogateescape decoding, matching re-encoding — non-ASCII/invalid-byte filenames handled correctly in lints.
2. **BBT is the sole bibliography writer**; the harness is commit-only across import/verify/doctor. Doctor: 60 s settle before declaring staleness, re-register only on persistent mismatch, then verify and commit genuine BBT output. (Completes Plan A's interim-writer expiry as designed.)
3. **Synthetic offline outcomes do not persist**: `--offline` runs may show "network disabled" in explicit audits but never demote trust, stamp markers, or fill the inbox; CI treats exit 3 as warning, fails only on closing exit 1; RW-only runs use the CSV leg without fabricating a failed live leg. **Genuine** network failures (attempted and failed) still persist — outage is information; self-imposed offline is not.
4. **`managed-sha256` integrity witness** over exact managed-region bytes: pre-commit compares vs HEAD; CI gets an explicit git baseline (exposes deletion/rename); current-file validation catches managed edits; PostToolUse warns on any LLM touch of literatures/. Key is bridge-owned; harmless in canonical_content (changes iff the region changes) — document in spec §5 during the rename wave.
5. **Surface sets govern enforcement only** — detection, verified events, current-failure projection, markers, and inbox audit are surface-independent.
6. **Scaffold commits only files it created**, preserving unrelated staged/working-tree changes; idempotent existing-vault behavior retained.
7. **CI authority split**: `--with-ci` installs read-only verification; the scheduled `contents: write` RW workflow is a separate explicit opt-in, fails loudly on download/infrastructure failure, commits only verifier-owned outputs.

Ordinary corrections without ruling: doctor `--base` routing; exact live autoexport cleanup confirmation; `stop_hook_active` for a genuinely consecutive eight-block bound.

## Task 3 review ruling (approved, 2026-08-20)

**Bibliography commit uses an isolated temporary-index snapshot, not `git commit --only`.** `--only` re-reads the live worktree at commit time; BBT can atomically replace the file after validation, so Git may commit bytes that were never compared (TOCTOU — post-checking detects only after history changed). The ownership contract governs. Required properties, implementation free: (1) committed blob is the exact validated in-memory bytes (`hash-object --stdin`, no re-read); (2) tree = HEAD tree + that one blob, temp index built from HEAD never the live index, so nothing rides along; (3) live index/worktree untouched; (4) HEAD update race-safe (native commit lock via temporary `GIT_INDEX_FILE`, or `commit-tree` + compare-and-swap `update-ref` that fails cleanly on a concurrent commit). Harness still never writes `x/bibliography.json`; commit contains only that path; BBT remains sole writer; newer mid-window BBT bytes are the next staleness pass's business.

## Task 4 preflight rulings (all approved, 2026-08-20)

1. **Pre-commit compares HEAD to the git index** — the prospective commit — never the worktree. The commit gate's subject is what becomes durable: staged deletes/renames are commit content even when unstaged bytes mask them, and unstaged scratch never triggers holds. First-commit edge: no HEAD → diff against the empty tree.
2. **No actor self-authorizes managed-region changes — including the deterministic importer.** The commit hook cannot verify byte provenance, and re-rendering from Zotero to prove machine origin would put a network dependency inside a closing check (UNREACHABLE cannot close; an outage would block commits). Any managed-region base→candidate change is an evidence-layer finding routed to the review inbox; the existing hash-scoped human acknowledgment is the sole pass, standing until the target's content hash changes. No auto-commit shortcut: the importer writes, the human commits. (Consistent reading of the user-driven control model.)
3. **Bare `verify` is an open audit surface**: collect and project everything, close nothing. Closing sets bind only to explicitly named surfaces (commit, publish) — detect-always / enforce-at-surface verbatim.

## Task 4 execution rulings (all approved, 2026-08-20)

1. **RW commits**: captured post-projection blobs (never re-read), temporary index from HEAD, expected-HEAD compare-and-swap. Dirty overlapping output paths → exit 2 (environment-not-as-expected; distinct from closing 1 / warning 3) — the batch never clobbers uncommitted human work. The NUL manifest is audit evidence, never the source of committed bytes.
2. **Projection**: one immutable live-worktree snapshot; compute ALL postimages first, then apply with rollback-safe byte-CAS; any divergence → exit 2 before mutation; the live index is never altered. Byte-CAS is discipline not a kernel lock — acceptable because divergence is detected and refused, never silently absorbed.
3. **Persisted git paths**: canonical ASCII path-bytes — identities `/` + RFC 3986 unreserved; every other byte including `%` encoded uppercase `%HH`; decode validates exact round-trip (re-encode reproduces input) before any filesystem use, rejecting non-canonical aliases.

## Task 8 rulings (all approved, 2026-08-20)

Live-contract blocker: installed BBT 9.0.55 JSON-RPC exposes `autoexport.add` only — `.list`/`.remove`/`.delete`/`.get` all live-probed `-32601 METHOD_NOT_FOUND`. The live call is the authority; no fictional RPC methods.

1. **Gated manual cleanup replaces automated cleanup.** The drill creates nothing unless explicitly enabled (§7 consent); it retains the exact target and the temporary vault until removal in BBT Preferences is human-confirmed (deleting the vault first would leave a dangling registration exporting to a dead path), then records that confirmation. Record the probed API surface in `docs/environment.md` with the date, so the constraint is a documented environment fact.
2. **WSL path translation for the transient target**: `wslpath -w` before sending to Windows-host BBT; native absolute path otherwise. Nothing machine-specific is committed (standing shim doctrine applied).

## Task 8 follow-up ruling (approved, 2026-08-20): whole-library auto-export is human-created

Live drill result: `autoexport.add("//", …)` fails 404 "path is too short" before registration storage; BBT 9.0.55's public RPC supports collection auto-exports only (implementation hardcodes collection scope, source-verified). Target absence confirmed by read-only inspection of the Windows profile (prefs keys `better-bibtex.autoExport.<encoded-path>`) and `zotero.sqlite`: only the user's pre-existing unrelated auto-export exists.

**Ruling:** whole-library scope and BBT sole-writer ownership are preserved; programmatic registration is replaced by **one-time human creation of the whole-library auto-export in BBT Preferences** — same §7 class as `.xpi` wizard steps (detect → guide → verify). The harness is observation/commit-only for this contract and never calls collection-only `autoexport.add`; the dead whole-library registration path is removed (git history preserves it). `docs/environment.md` records three dated facts: RPC surface add-only + collection-only (source ref); the 404-before-storage behavior; auto-export persistence as profile prefs keys (human-debugging fact only — doctor detection stays behavioral: export presence + staleness, never prefs-scraping). Spec §4 amended to match.

## Self-Review (completed at authoring)

**Spec coverage:** §3 tree/templates/AGENTS.md/Bases → T1–T2; §7 vault-setup + doctor + provisioning consent + wizard installs → T2–T3, T7; §6 surfaces: pre-commit → T3/T4, CI replay + rw-batch async auditor → T4, PostToolUse warn (fail-open) → T5, armed Stop gate (fail-closed incl. UNREACHABLE, 8-block bound, bypass-as-data to inbox) → T6; §8 hooks.json in plugin layout → T6; Plan A caveat (autoexport live) → T3 (repair path) + T8 (discharge). Deliberately out: the eight remaining skills and the publish skill that writes the flag (Plan D); paths-frontmatter guard scoping (Plan D, with the guard skills); marketplace version bump (Plan D ships the full skill set).
**Placeholders:** none — hook I/O field names and the Stop blocking JSON are written to best current knowledge with the vendored hooks docs named as governing authority (same HEAD-governs pattern as Plan B).
**Verification history (final):** all three lenses completed as independent agents (the hooks lens first; spec-fidelity and desk-check on resume after a limit reset — the desk-check executed plan code in a sandbox against as-built 238fd27). Total: 3 CRITICAL + 5 IMPORTANT + 15 MINOR across both passes, all fixed. Load-bearing corrections: per-surface closing sets (COMMIT_CLOSING vs PUBLISH_CLOSING — DOI was missing from publish closure, quote wrongly closed commits); bibliography bookkeeping commits bypass the hook (doctor crashed in exactly the scenario it repairs); hookSpecificOutput shape; evidence-layer check on the PostToolUse surface; gate walk-up includes cwd itself; import-guard fail-open in pre-commit; SKIPPED auditing on gate runs; .keep survival across fresh clones.

**Type consistency:** `scaffold_vault`/`doctor` names consistent T2→T3→T7→T8; `PROVISION_COMPANIONS` T7; flag-file schema identical in T6 contract and tests; CLI verbs consistent with as-built `main()` wiring; `Probe` tuple shape used uniformly.
