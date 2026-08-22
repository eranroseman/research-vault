"""`import-source`'s prose contract (spec §7's information-flow row).

The information flow — find, human admits via Zotero, catalog, integrate — is
continuous and project-independent (spec §7's two-flow accounting; CONTEXT.md
says the same in one line), and the 2026-08-22 ruling fixes where it enters:
at admission, not at search. `find-sources` alone stays project-scoped,
because its deliverable is a per-review PRISMA-S trail. These tests hold the
skill text to that ruling, and to the one fact a first real import cannot
start without: where to read the citekey after admission.
"""

from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "import-source" / "SKILL.md"


def _skill_text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_import_source_says_it_needs_no_project():
    """Leaving the standalone entry implicit must fail: an agent that arrives
    without a project has to read that it may proceed, not infer it."""
    text = _skill_text()

    assert "No project is required" in text
    assert "project-independent" in text
    assert "zero projects" in text


def test_import_source_says_where_to_read_the_citekey_after_admission():
    """First real import hits this: the skill takes CITEKEY as an argument and
    never said where a person finds it."""
    text = _skill_text()

    assert "Citation Key" in text
    assert "Better BibTeX" in text
