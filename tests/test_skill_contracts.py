"""Generic contract every shipped ``skills/*/SKILL.md`` must satisfy (spec §7, §8).

Unlike ``test_skill_files.py`` (setup-vault-specific content acceptance),
this module asserts only what the control model and plugin architecture
require of *every* skill, present and future. It is written to stay green
as later Plan D tasks add entry skills — nothing here is scoped to the two
guard skills shipped alongside it.
"""

import re
import shlex
from pathlib import Path

import pytest

from knowledge_harness import inbox
from knowledge_harness.frontmatter import FrontmatterError, parse

REPOSITORY = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPOSITORY / "skills"
TEMPLATES_DIR = REPOSITORY / "knowledge_harness" / "templates"

# Control model (spec §7/§8, ruled 2026-08-22): entry skills ship
# `disable-model-invocation: true` so they never enter the model catalog;
# every other shipped skill is a guard/reference skill, model-invoked AND
# user-invocable, so it carries neither `disable-model-invocation` nor
# `user-invocable`. This list grows by one name per Plan D task as each
# entry skill ships (Task 2 publish; Task 3 verify-citations,
# factcheck-draft; Task 4 project; Task 5 import-source; Task 6
# find-sources) — it only ever grows, never shrinks.
ENTRY_SKILLS = {
    "setup-vault",
    "publish",
    "verify-citations",
    "factcheck-draft",
    "project",
    "import-source",
}

# A bare kebab-case token in backticks, e.g. `` `evidence-conventions` `` —
# the shape a skill name takes when a template cites one in prose. Requires
# at least one hyphen so ordinary single words never match, and excludes
# slashes/dots/percents so path fragments (`` `synthesis/index.md` ``),
# managed markers (`` `%%hk-managed%%` ``), and similar template furniture
# never false-positive.
_BACKTICKED_KEBAB_TOKEN = re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`")


def _skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())


def _skill_md_files() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def _shipped_template_files() -> list[Path]:
    return sorted(p for p in TEMPLATES_DIR.rglob("*") if p.is_file())


def test_every_skill_directory_ships_a_skill_md():
    dirs = _skill_dirs()
    assert dirs, "expected at least one skills/<name>/ directory"
    for directory in dirs:
        assert (directory / "SKILL.md").is_file(), f"{directory} has no SKILL.md"


def test_every_entry_skill_named_here_is_actually_shipped():
    """Keeps ENTRY_SKILLS load-bearing: the per-skill invocation check below is
    parametrized over shipped files, so a name added here without its
    directory would otherwise assert nothing."""
    missing = sorted(ENTRY_SKILLS - {directory.name for directory in _skill_dirs()})
    assert not missing, f"ENTRY_SKILLS names unshipped skill(s): {missing}"


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_frontmatter_parses_via_the_core_parser(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    try:
        data, body = parse(text)
    except FrontmatterError as error:
        pytest.fail(f"{skill_md}: frontmatter does not parse: {error}")
    assert data, f"{skill_md}: frontmatter is empty"
    assert body.strip(), f"{skill_md}: body is empty"


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_name_matches_directory(skill_md):
    data, _ = parse(skill_md.read_text(encoding="utf-8"))
    assert data.get("name") == skill_md.parent.name


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_description_is_nonempty(skill_md):
    data, _ = parse(skill_md.read_text(encoding="utf-8"))
    description = data.get("description")
    assert isinstance(description, str)
    assert description.strip()


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_invocation_flags_match_the_ruled_control_model(skill_md):
    name = skill_md.parent.name
    data, _ = parse(skill_md.read_text(encoding="utf-8"))
    if name in ENTRY_SKILLS:
        assert data.get("disable-model-invocation") == "true", (
            f"{name} is an entry skill and must ship disable-model-invocation: true"
        )
    else:
        assert "disable-model-invocation" not in data, (
            f"{name} is a guard/reference skill (model-invoked AND "
            "user-invocable) and must not ship disable-model-invocation"
        )
    # Reserved for future machine contracts; no skill ships it yet (spec §7).
    assert "user-invocable" not in data, (
        f"{name}: user-invocable is reserved for future machine contracts"
    )


_FINDING_INVOCATION = "python3 -m knowledge_harness finding "


def _shipped_finding_invocations() -> list[tuple[Path, list[str]]]:
    invocations = []
    for skill_md in _skill_md_files():
        for line in skill_md.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith(_FINDING_INVOCATION):
                invocations.append((skill_md, shlex.split(line.strip())))
    return invocations


def test_every_shipped_finding_invocation_names_registered_identifiers():
    """A skill that spells a check id or reason code the registry dropped would
    ship a command the CLI refuses — and prose is the one surface no test
    otherwise reads. Catches the drift at build time, not at a person's shell."""
    invocations = _shipped_finding_invocations()
    assert invocations, "expected at least one shipped `finding` invocation"
    for skill_md, tokens in invocations:
        check, _target, result, reason = tokens[4:8]
        assert check in inbox.CHECK_IDS, (
            f"{skill_md}: unregistered check id {check!r} in a shipped command"
        )
        assert result in {"UNMATCHED", "UNREACHABLE", "SKIPPED"}, (
            f"{skill_md}: {result!r} is not a result the `finding` verb accepts"
        )
        try:
            inbox.validate_reason(reason)
        except ValueError as error:
            pytest.fail(f"{skill_md}: {error}")


def test_every_skill_name_a_shipped_template_cites_has_a_skill_directory():
    """Subsumes the 2026-08-22 landing check: scans every shipped template
    generically rather than asserting any one cited name by hand."""
    cited = set()
    for template in _shipped_template_files():
        text = template.read_text(encoding="utf-8")
        cited.update(_BACKTICKED_KEBAB_TOKEN.findall(text))
    assert cited, "expected at least one skill name cited in a shipped template"
    existing = {directory.name for directory in _skill_dirs()}
    missing = sorted(cited - existing)
    assert not missing, (
        f"shipped templates cite skill name(s) with no skills/<name>/ "
        f"directory: {missing}"
    )
