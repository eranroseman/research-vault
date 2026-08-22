"""Config surfaces that currently fail SILENTLY, made to fail loudly in CI.

Three classes of silent failure live here, all of the same shape — a file the
plugin loader or a human reader trusts, which nothing mechanically checks:

* a malformed ``hooks.json`` or plugin manifest is swallowed at plugin load;
* a typo'd ``SKILL.md`` frontmatter key is swallowed the same way;
* an identifier coined in code but never given a row in ``docs/terminology.md``
  §4.4 stays ungoverned until somebody happens to run a naming audit.

The JSON half doubles as the *formatter*: ``json.tool``'s canonical form is
asserted here rather than run as a separate hook, so the one-form-owner matrix
gains a JSON owner with zero new dependencies (docs/2026-08-21-lint-format-rethink.md).
"""

import ast
import json
import re
import sys
from pathlib import Path

import pytest
import tomllib

from knowledge_harness import frontmatter, inbox

ROOT = Path(__file__).resolve().parents[1]

# The repo's own JSON manifests, and only those. Deliberately NOT globbed:
# `research/` and `analysis/` JSON are immutable records (AGENTS.md history rule),
# `.vscode/*.json` is JSONC — a dialect VS Code owns — and a vault's
# `system/bibliography.json` is BBT-owned, outside every repo formatter.
JSON_MANIFESTS = [
    "hooks/hooks.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    "knowledge_harness/templates/harness/machine.json.example",
]

TOML_FILES = ["pyproject.toml"]

SKILL_FILES = sorted(ROOT.glob("skills/*/SKILL.md"))


def _canonical(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


@pytest.mark.parametrize("relative", JSON_MANIFESTS)
def test_json_manifest_parses(relative):
    """A manifest the plugin loader cannot parse fails at load with no message."""
    path = ROOT / relative
    assert path.is_file(), f"{relative} is missing"
    json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("relative", JSON_MANIFESTS)
def test_json_manifest_is_in_canonical_form(relative):
    """JSON's form owner is stdlib ``json.tool``; this assertion IS the check."""
    path = ROOT / relative
    raw = path.read_text(encoding="utf-8")
    assert raw == _canonical(json.loads(raw)), (
        f"{relative} is not in canonical JSON form. Fix it with:\n"
        f"    python -m json.tool --indent 2 --no-ensure-ascii "
        f"{relative} {relative}"
    )


@pytest.mark.parametrize("relative", TOML_FILES)
def test_toml_parses(relative):
    path = ROOT / relative
    assert path.is_file(), f"{relative} is missing"
    with path.open("rb") as handle:
        tomllib.load(handle)


def test_pyproject_pins_the_tools_the_seam_runs():
    """The seam's promise is a PINNED toolchain: an unpinned row breaks it."""
    with (ROOT / "pyproject.toml").open("rb") as handle:
        data = tomllib.load(handle)
    dev = data["project"]["optional-dependencies"]["dev"]
    pinned = {row.split("==")[0] for row in dev if "==" in row}
    for tool in ("ruff", "mypy", "mdformat", "yamlfix", "pyproject-fmt", "pre-commit"):
        assert tool in pinned, f"{tool} must be pinned with == in the dev extra"


# --------------------------------------------------------------------------
# Identifier governance (terminology.md §4.4) — mechanical, not an audit.
# --------------------------------------------------------------------------


def _governance_row(group: str) -> str:
    # Padding-tolerant by construction: mdformat owns docs/ and pads table cells to
    # align columns, so an exact-prefix match would break on the next reflow.
    prefix = re.compile(rf"\|\s*{re.escape(group)}\s*\|")
    rows = [
        line
        for line in (ROOT / "docs/terminology.md")
        .read_text(encoding="utf-8")
        .splitlines()
        if prefix.match(line)
    ]
    assert len(rows) == 1, f"terminology.md §4.4 must carry exactly one '{group}' row"
    return rows[0]


def _backticked(row: str) -> set[str]:
    return set(re.findall(r"`([^`]+)`", row))


def _probe_ids() -> set[str]:
    """Every doctor probe id the code can emit, read off scaffold.py's AST.

    Probe ids are literals at their construction sites rather than a registry
    constant, so the AST is the only honest source; a grep would also match
    prose in docstrings.
    """
    tree = ast.parse((ROOT / "knowledge_harness/scaffold.py").read_text())
    return {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and getattr(node.func, "id", None) == "Probe"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    }


def test_every_check_id_at_head_is_governed():
    """A check id coined in code with no §4.4 row is an ungoverned identifier."""
    ungoverned = sorted(
        _backticked(_governance_row("check ids")).symmetric_difference(inbox.CHECK_IDS)
        & inbox.CHECK_IDS
    )
    assert not ungoverned, (
        "check ids in CHECK_IDS with no backticked entry in terminology.md §4.4: "
        f"{ungoverned}"
    )


def test_every_doctor_probe_id_at_head_is_governed():
    probes = _probe_ids()
    assert probes, "AST scan found no Probe ids — the scan itself is broken"
    ungoverned = sorted(probes - _backticked(_governance_row("doctor probe ids")))
    assert not ungoverned, (
        "doctor probe ids emitted by scaffold.py with no backticked entry in "
        f"terminology.md §4.4: {ungoverned}"
    )


def test_reason_codes_row_delegates_to_the_code_registry():
    """§4.4 governs reason codes BY REFERENCE, not by enumeration.

    That row's own status reads "one registry, code is authoritative", and it
    lists only the renamed/notable members after "incl." — so enumerating parity
    here would assert a contract the document deliberately does not make. What
    IS checkable, and what this guards, is that the delegation survives: if the
    row stops naming ``REASON_CODES``, the group has silently lost its owner.
    """
    row = _governance_row("reason codes")
    assert "REASON_CODES" in row
    assert inbox.REASON_CODES, "the reason-code registry must not be empty"
    for named in ("superseded-note", "not-admitted", "drift", "outage", "budget-cap"):
        assert named in _backticked(row), f"{named} lost its §4.4 reference row"
        assert named in inbox.REASON_CODES, (
            f"§4.4 names {named}, code does not carry it"
        )


# --------------------------------------------------------------------------
# Skill frontmatter — the hooks.json failure class, one surface over.
# --------------------------------------------------------------------------


def test_skill_files_exist():
    assert SKILL_FILES, "no skills/*/SKILL.md found — the glob is wrong"


def _raw_frontmatter_lines(skill_md: Path) -> list[str]:
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{skill_md} does not open with a --- fence"
    closing = text.index("\n---", len("---\n"))
    return text[len("---\n") : closing + 1].splitlines()


@pytest.mark.parametrize("skill_md", SKILL_FILES, ids=lambda p: p.parent.name)
def test_skill_frontmatter_matches_the_plugin_contract(skill_md):
    """Dogfood the core's own tokenizer on real files; zero new dependencies."""
    data, _body = frontmatter.parse(skill_md.read_text(encoding="utf-8"))
    assert data, f"{skill_md.parent.name}/SKILL.md has no frontmatter block"
    assert data.get("name") == skill_md.parent.name, (
        f"{skill_md.parent.name}/SKILL.md declares name={data.get('name')!r}; "
        "the plugin contract requires it to equal the skill directory name"
    )
    description = data.get("description")
    assert isinstance(description, str), (
        f"{skill_md.parent.name}/SKILL.md needs a description"
    )
    assert description.strip(), (
        f"{skill_md.parent.name}/SKILL.md needs a NONEMPTY description"
    )


@pytest.mark.parametrize("skill_md", SKILL_FILES, ids=lambda p: p.parent.name)
def test_skill_disable_model_invocation_is_a_yaml_boolean_literal(skill_md):
    """Asserted against the RAW line, deliberately, not the parsed value.

    ``frontmatter.parse`` is the VAULT-dialect tokenizer: a flat quoted-string
    schema (spec §5) that yields ``'true'`` for ``true`` and for ``"true"``
    alike, and never a bool. The plugin loader, by contrast, reads this file as
    real YAML — so ``"true"``, ``yes``, ``1`` and ``True`` are all silent
    mis-reads that the tokenizer physically cannot distinguish. Checking the raw
    line is therefore the STRONGER assertion, not a concession: it catches every
    one of those, which an ``isinstance(..., bool)`` on the parsed value cannot.
    """
    for line in _raw_frontmatter_lines(skill_md):
        key, _, value = line.partition(":")
        if key.strip() == "disable-model-invocation":
            assert value.strip() in {"true", "false"}, (
                f"{skill_md.parent.name}/SKILL.md: disable-model-invocation must be "
                f"the unquoted YAML boolean `true` or `false`, got {value.strip()!r}"
            )


def test_repo_python_is_the_version_the_pins_were_measured_against():
    """A guard, not a gate: the pinned toolchain's behaviour is version-bound."""
    assert sys.version_info >= (3, 10), "pyproject requires-python is >=3.10"
