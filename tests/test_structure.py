from research_vault import Result, structure


def _write(tmp_path, relative, text):
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_expected_type_is_the_folder():
    assert structure.expected_type("literatures/smith2020.md") == "literature"
    assert structure.expected_type("synthesis/topic.md") == "synthesis"
    assert structure.expected_type("projects/brief/draft.md") == "project"
    assert structure.expected_type("log/2026-08-20.md") == "daily"
    assert structure.expected_type("inbox/review-queue.md") == "review-queue"
    assert structure.expected_type("system/templates/literature.md") is None
    assert structure.expected_type("scratch.md") is None


def test_expected_type_project_note_is_narrow():
    # Only the canonical draft.md, exactly one project-name level deep, derives.
    assert structure.expected_type("projects/brief/draft.md") == "project"
    # A second file in the same project directory derives nothing.
    assert structure.expected_type("projects/brief/appendix.md") is None
    # A flat projects/<name>.md with no subdirectory derives nothing.
    assert structure.expected_type("projects/brief.md") is None
    # Deeper nesting past the canonical file derives nothing either.
    assert structure.expected_type("projects/brief/notes/appendix.md") is None


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
    path = _write(
        tmp_path, "projects/brief/draft.md", '---\ntype: "project"\n---\nbody\n'
    )
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.MATCHED

    # A second file alongside draft.md in the same project directory is
    # underived — any non-empty type passes (knowledge-harness#105).
    path = _write(
        tmp_path, "projects/brief/appendix.md", '---\ntype: "appendix"\n---\nbody\n'
    )
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.MATCHED

    path = _write(tmp_path, "system/note.md", '---\ntype: "guide"\n---\nbody\n')
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.MATCHED


def test_check_skips_fleeting_notes(tmp_path):
    path = _write(tmp_path, "inbox/half-thought.md", "just an idea\n")
    assert structure.check_note_frontmatter(tmp_path, path) == []


def _scaffold_min(tmp_path):
    for d in ("literatures", "synthesis", "projects", "log", "inbox", "system"):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    _write(tmp_path, "index.md", '---\nokf_version: "0.2"\n---\n# Vault index\n')


def test_reserved_root_index_carries_only_okf_version(tmp_path):
    _scaffold_min(tmp_path)
    assert all(o.result is Result.MATCHED for o in structure.check_reserved(tmp_path))
    _write(tmp_path, "index.md", '---\ntype: "index"\nokf_version: "0.2"\n---\n# V\n')
    problems = [
        o for o in structure.check_reserved(tmp_path) if o.result is Result.UNMATCHED
    ]
    assert problems
    assert "okf_version" in problems[0].reason


def test_reserved_nested_index_must_be_frontmatter_free(tmp_path):
    _scaffold_min(tmp_path)
    _write(tmp_path, "synthesis/index.md", '---\ntype: "index"\n---\n# S\n')
    problems = [
        o for o in structure.check_reserved(tmp_path) if o.result is Result.UNMATCHED
    ]
    assert problems
    assert "synthesis/index.md" in problems[0].target


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
    assert problems
    assert "newest first" in problems[0].reason


def test_tree_check(tmp_path):
    from research_vault import scaffold

    scaffold.scaffold_vault(tmp_path)
    assert structure.check_tree(tmp_path).result is Result.MATCHED


def test_commit_surface_closes_on_structure_violation(tmp_path):
    from research_vault import scaffold, verify

    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "literatures" / "untyped.md").write_text("# no frontmatter\n")
    _report, effective, _hashes, warning = verify.verify_state(
        tmp_path, network=False, git_candidate="worktree"
    )
    decision, blockers = verify.surface_decision("commit", effective, warning)
    assert decision == 1
    assert any("okf-frontmatter" in blocker for blocker in blockers)


def test_commit_surface_ignores_fleeting_notes(tmp_path):
    from research_vault import scaffold, verify

    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "inbox" / "half-thought.md").write_text("just an idea\n")
    _report, effective, _hashes, warning = verify.verify_state(
        tmp_path, network=False, git_candidate="worktree"
    )
    decision, _blockers = verify.surface_decision("commit", effective, warning)
    assert decision == 0
