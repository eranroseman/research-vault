"""Static acceptance checks for user-invoked skill files."""

from pathlib import Path

from harness_core import scaffold

REPOSITORY = Path(__file__).resolve().parents[2]
SKILL = REPOSITORY / "skills" / "setup-vault" / "SKILL.md"


def _skill_text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_setup_vault_frontmatter_is_user_invoked_and_discoverable():
    """Removing the user-only setup-vault frontmatter must fail."""
    text = _skill_text()

    assert text.startswith("---\nname: setup-vault\ndescription: Use when ")
    assert "disable-model-invocation: true\n---\n" in text


def test_setup_vault_uses_scaffold_with_separate_ci_consents():
    """Hand-building a vault or coupling the two CI permissions must fail."""
    text = _skill_text()

    assert "Ask together:" in text
    assert "destination" in text
    assert "read-only CI" in text
    assert "Ask separately:" in text
    assert "scheduled write-capable RW workflow" in text
    assert "python3 -m harness_core scaffold --vault PATH" in text
    assert "--with-ci" in text
    assert "--with-rw-ci" in text
    assert "only the flags the user consented to" in text
    assert "Do not create directories or files by hand" in text
    assert "use `git add .`" in text


def test_setup_vault_documents_doctor_routing_and_complete_reporting():
    """Wrong base-URL placement or partial doctor reporting must fail."""
    text = _skill_text()

    assert "python3 -m harness_core --base URL doctor --vault PATH" in text
    assert "python3 -m harness_core doctor --base URL --vault PATH" in text
    assert "every doctor probe" in text
    assert "inbox count" in text
    assert "oldest age" in text


def test_setup_vault_provisions_each_companion_only_after_item_consent():
    """Installing companions before consent or automating Zotero must fail."""
    text = _skill_text()

    sequence = [
        "Detect",
        "Report",
        "per-item consent",
        "Install or guide",
        "Verify",
    ]
    companion_section = text[text.index("## Provision companions") :]
    positions = [companion_section.index(step) for step in sequence]
    assert positions == sorted(positions)
    assert companion_section.index("per-item consent") < companion_section.index(
        "claude plugin install"
    )
    assert "restart-to-activate" in text
    assert "Zotero .xpi installs are human-only wizard steps" in text
    assert "BBT required" in text
    assert "MarkDB-Connect optional" in text
    for forbidden in ("download", "click", "close Zotero"):
        assert f"never {forbidden}" in text


def test_setup_vault_treats_the_whole_library_auto_export_as_a_human_wizard_step():
    """Registering an auto-export or claiming one doctor has not verified must fail."""
    text = _skill_text()
    companion_section = text[text.index("## Provision companions") :]

    for phrase in (
        "human-only wizard step",
        "exact target path doctor reported",
        "whole-library scope",
        "Better CSL JSON translator",
        "keep updated",
        "re-run doctor to verify",
    ):
        assert phrase in companion_section
    assert "Never register an auto-export for them" in companion_section
    assert (
        "never say an auto-export exists until doctor reports `autoexport` MATCHED"
        in companion_section
    )


def test_setup_vault_reports_only_scaffold_created_commit_paths():
    """Claiming unrelated work was committed must fail."""
    text = _skill_text()

    for path in (
        "AGENTS.md",
        "inbox/review-queue.md",
        "x/templates/",
        "x/bases/",
        ".git/hooks/pre-commit",
    ):
        assert path in text
    assert "only scaffold-created paths are committed" in text
    assert "never claim unrelated changes were committed" in text


def test_scaffold_provisioning_companions_are_exact_and_current():
    """Changing the ruled companion package spelling must fail."""
    assert scaffold.PROVISION_COMPANIONS == ["kepano/obsidian-skills"]


def test_no_old_skill_names_survive():
    """Guarding against skill name regressions — old names must not survive."""
    old_names = ["vault-setup", "find-papers", "atlas-conventions"]

    # Glob all SKILL.md files in skills/
    skill_files = list(REPOSITORY.glob("skills/**/SKILL.md"))

    # Must have at least one skill file to guard against
    assert skill_files, "No SKILL.md files found in skills/"

    for skill_file in skill_files:
        file_path = str(skill_file)
        file_content = skill_file.read_text(encoding="utf-8")

        for old_name in old_names:
            assert old_name not in file_path, (
                f"Old skill name '{old_name}' found in path: {file_path}"
            )
            assert old_name not in file_content, (
                f"Old skill name '{old_name}' found in content of {skill_file}"
            )
