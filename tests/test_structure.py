from pathlib import Path

from research_vault import Result, structure


def _write(tmp_path, relative, text):
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_expected_type_is_the_folder():
    assert structure.expected_type("literatures/smith2020.md") == "literature"
    assert structure.expected_type("synthesis/topic.md") == "synthesis"
    assert structure.expected_type("projects/brief.md") == "project"
    assert structure.expected_type("log/2026-08-20.md") == "daily"
    assert structure.expected_type("inbox/review-queue.md") == "review-queue"
    assert structure.expected_type("system/templates/literature.md") is None
    assert structure.expected_type("scratch.md") is None


def test_fleeting_paths_are_named_not_typed():
    assert structure.is_fleeting("inbox/half-thought.md")
    assert not structure.is_fleeting("inbox/review-queue.md")
    assert not structure.is_fleeting("literatures/smith2020.md")


def test_check_flags_missing_frontmatter_and_wrong_folder_type(tmp_path):
    path = _write(tmp_path, "literatures/untyped.md", "# no frontmatter\n")
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
