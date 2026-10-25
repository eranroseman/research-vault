import ast
from pathlib import Path

import pytest

from research_vault import Result, structure
from tests.conftest import package_ast


def _write(tmp_path, relative, text):
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_expected_type_is_the_folder():
    assert structure.expected_type("literature/smith2020.md") == "literature"
    assert structure.expected_type("projects/brief/draft.md") == "project"
    assert structure.expected_type("log/2026-08-20.md") == "daily"
    assert structure.expected_type("inbox/review-queue.md") == "review-queue"
    assert structure.expected_type("system/templates/literature.md") is None
    assert structure.expected_type("scratch.md") is None


def test_wiki_derives_no_type_and_synthesis_is_gone():
    assert structure.expected_type("wiki/concepts/topic.md") is None
    assert structure.expected_type("wiki/sources/A paper.md") is None
    assert "synthesis" not in structure._FOLDER_TYPES


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
    assert not structure.is_fleeting("literature/smith2020.md")


def test_check_flags_missing_frontmatter_and_wrong_folder_type(tmp_path):
    path = _write(tmp_path, "literature/untyped.md", "# no frontmatter\n")
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.check == "okf-frontmatter"
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason == "schema-violation — missing type (OKF §11 rule 2)"

    path = _write(tmp_path, "log/mislabeled.md", '---\ntype: "literature"\n---\nbody\n')
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.UNMATCHED
    assert (
        outcome.reason
        == "schema-violation — type 'literature' but folder derives 'daily'"
    )


def test_check_passes_conformant_and_underived_notes(tmp_path):
    path = _write(
        tmp_path, "projects/brief/draft.md", '---\ntype: "project"\n---\nbody\n'
    )
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.MATCHED

    # A second file alongside draft.md in the same project directory is
    # underived — any non-empty type passes (research-vault#105).
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
    for d in ("literature", "wiki", "projects", "log", "inbox", "system"):
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
    assert (
        problems[0].reason
        == "schema-violation — root index carries keys beyond okf_version: ['type']"
    )


def test_reserved_check_exempts_wiki_index_only(tmp_path):
    _write(tmp_path, "index.md", '---\nokf_version: "0.2"\n---\n# Root\n')
    _write(
        tmp_path,
        "wiki/index.md",
        "---\ntype: meta\ntitle: Wiki Index\nstatus: evergreen\n"
        "created: 2026-09-07\nupdated: 2026-09-07\ntags:\n  - meta\n---\n# Wiki Index\n",
    )
    (outcome,) = structure.check_reserved(tmp_path)
    assert outcome.result is Result.MATCHED

    _write(tmp_path, "wiki/concepts/index.md", '---\ntype: "index"\n---\n# S\n')
    problems = structure.check_reserved(tmp_path)
    assert problems[0].result is Result.UNMATCHED
    assert "wiki/concepts/index.md" in problems[0].target


def test_reserved_check_skips_the_tool_stores(tmp_path):
    _write(tmp_path, "index.md", '---\nokf_version: "0.2"\n---\n# Root\n')
    _write(tmp_path, ".raw/captured/index.md", '---\ntype: "x"\n---\n')
    _write(tmp_path, ".vault-meta/index.md", '---\ntype: "x"\n---\n')
    (outcome,) = structure.check_reserved(tmp_path)
    assert outcome.result is Result.MATCHED


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
    assert problems[0].reason == "schema-violation — day headings not newest first"


def test_tree_check(tmp_path):
    from research_vault import scaffold

    scaffold.scaffold_vault(tmp_path)
    assert [o.result for o in structure.check_tree(tmp_path)] == [Result.MATCHED]


def test_commit_surface_closes_on_structure_violation(tmp_path):
    from research_vault import scaffold, verify

    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "literature" / "untyped.md").write_text("# no frontmatter\n")
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


# --- boundaries pinned against mutation survivors -----------------------------


def test_log_shape_reads_a_log_whose_frontmatter_does_not_parse_as_all_body():
    assert (
        structure._log_shape_problems(
            "---\nnot a mapping\n---\n## 2026-08-21\n- y\n\n## 2026-08-20\n- x\n"
        )
        == []
    )
    assert structure._log_shape_problems("## 2026-08-20\n\n## 2026-08-21\n") == [
        "day headings not newest first"
    ]


def test_check_tree_reports_each_nested_directory_under_literature(tmp_path):
    """Residual 3: every literature reader ignores a nested directory (flat
    since 4c6eca9), so a `literature/<dir>/` is a tree finding — one row per
    stray directory, beside the existing tree row; the id stays `tree`."""
    from research_vault import scaffold

    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "literature" / "older").mkdir()
    (tmp_path / "literature" / "zzz").mkdir()
    rows = structure.check_tree(tmp_path)
    assert [(o.check, o.target, o.result, o.reason) for o in rows] == [
        ("tree", "vault", Result.MATCHED, "matched"),
        (
            "tree",
            "literature/older/",
            Result.UNMATCHED,
            "schema-violation — literature/ is flat: literature/older/",
        ),
        (
            "tree",
            "literature/zzz/",
            Result.UNMATCHED,
            "schema-violation — literature/ is flat: literature/zzz/",
        ),
    ]


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


@pytest.mark.parametrize(
    ("name", "litter"),
    [
        ("._x", True),
        (".DS_Store", True),
        ("desktop.ini", True),
        ("Desktop.ini", True),
        ("notes.md", False),
    ],
)
def test_is_os_litter_names_each_upstream_pattern(name, litter):
    """Q25: every arm on its own — inside `is_excluded` the dot rule would hide
    the AppleDouble prefix and `.DS_Store`."""
    assert structure.is_os_litter(name) is litter


def test_check_tree_leaves_a_dot_directory_under_literature_alone(tmp_vault):
    """#194: a sync tool's `.stversions/` under `literature/` is no nested
    literature directory; a real one still is."""
    (tmp_vault / "literature" / ".stversions").mkdir()
    (tmp_vault / "literature" / "nested").mkdir()
    assert [
        (o.target, o.reason)
        for o in structure.check_tree(tmp_vault)
        if o.result is Result.UNMATCHED
    ] == [
        (
            "literature/nested/",
            "schema-violation — literature/ is flat: literature/nested/",
        )
    ]


# An AppleDouble header (magic, version, `Mac OS X` filler) and resource bytes
# that are not UTF-8: what macOS leaves beside a note copied to a FAT or SMB volume.
_APPLE_DOUBLE = (
    b"\x00\x05\x16\x07\x00\x02\x00\x00Mac OS X        \x00\x02\x00\x00\x00\t"
    b"\x00\x00\x002\x00\x00\x0e\xb0\x00\x00\x00\x02\x00\x00\x0e\xe2\xff\xfe"
)
# Litter that carries a real note's bytes, so a walker that reads it would
# take it for a second copy of that note.
_LITTER_COPIES = {
    "literature/._smith2020.md": "literature/smith2020.md",
    "literature/.stversions/smith2020.md": "literature/smith2020.md",
    "log/._2026-08-16.md": "log/2026-08-16.md",
    "wiki/concepts/._mortality-trends.md": "wiki/concepts/mortality-trends.md",
    "wiki/.trash/mortality-trends.md": "wiki/concepts/mortality-trends.md",
    "projects/brief/._draft.md": "projects/brief/draft.md",
    "projects/brief/.hot/draft.md": "projects/brief/draft.md",
    ".obsidian/plugins/dataview/README.md": "wiki/concepts/mortality-trends.md",
}
_LITTER_BYTES = {
    # Obsidian's own bin: a deleted page whose wikilink resolves nowhere.
    "wiki/.trash/old.md": b'---\ntype: "concept"\n---\nSee [[Nowhere at all]].\n',
    "literature/._gone2019.md": _APPLE_DOUBLE,
    "log/._2026-01-01.md": _APPLE_DOUBLE,
    "wiki/._p.md": _APPLE_DOUBLE,
    "projects/brief/._notes.md": _APPLE_DOUBLE,
    "system/propagations/._propagate-x.json": _APPLE_DOUBLE,
    "literature/.DS_Store": _APPLE_DOUBLE,
    "projects/brief/desktop.ini": b"[.ShellClassInfo]\r\n",
    "projects/brief/Desktop.ini": b"[.ShellClassInfo]\r\n",
}


def _drop_litter(vault):
    for relative, source in _LITTER_COPIES.items():
        (vault / relative).parent.mkdir(parents=True, exist_ok=True)
        (vault / relative).write_bytes((vault / source).read_bytes())
    for relative, data in _LITTER_BYTES.items():
        (vault / relative).parent.mkdir(parents=True, exist_ok=True)
        (vault / relative).write_bytes(data)


def _walkers():
    from research_vault import (
        capture,
        captured,
        lifecycle,
        lints,
        markers,
        okf,
        propagate,
        publish,
        stamp,
        verify,
    )
    from research_vault import compile as compile_mod

    return {
        "captured-set": lambda v: captured.lint_captured_set(v, as_of="2026-10-24"),
        "captured-notes": captured._read_notes,
        "captured-page-names": captured._page_names,
        "capture-all": capture._every_note,
        "lifecycle": lifecycle._provenances,
        "compile": lambda v: list(
            compile_mod._selected_notes(v, {"smith2020", "gone2019"})
        ),
        "markers": markers._claim_notes,
        # Each run appends `verified:` markers, so claim line numbers (in
        # `extra`) move between reads. `evidence-layer` is left out: it judges
        # the git snapshot's path set (`lints._literature_files`), not a walk.
        "verify": lambda v: [
            (o.check, o.target, o.result, o.reason)
            for o in verify.verify_state(v, network=False, git_candidate="worktree")[1]
            if o.check != "evidence-layer"
        ],
        "okf-log": okf.regenerate_log,
        "stamp": lambda v: list(stamp._candidate_paths(v, None)),
        "publish": lambda v: publish.project_note(v, "brief"),
        "disputed-links": lints.disputed_claim_links,
        "published-paths": lambda v: lints._current_paths(v, "projects"),
        "propagate-surfaces": lambda v: list(propagate._surfaces(v)),
        "propagate-records": propagate.lint_propagation,
        "reserved": structure.check_reserved,
        "tree": structure.check_tree,
    }


@pytest.mark.parametrize("walker", sorted(_walkers()))
def test_a_littered_vault_reads_the_same_to_every_walker(fixture_vault, walker):
    """#194, Q25: AppleDouble files, `.DS_Store`, `desktop.ini` and dot-directory
    copies of real notes change nothing any walker reports."""
    read = _walkers()[walker]
    read(fixture_vault)  # the first read writes: verify's markers, okf's `log.md`
    before = read(fixture_vault)
    _drop_litter(fixture_vault)
    assert read(fixture_vault) == before


# Walks over paths that hold no vault note, keyed by module and enclosing
# function (line numbers drift); each says why the predicate has nothing to
# exclude there. A stale entry fails the test below, so none outlives its walk.
_NOT_NOTE_WALKS = {
    "scaffold.py::_template_files": "the package's own template tree, not a vault",
    "scaffold.py::_add_empty_root_sentinels": "asks only whether a root is empty, to seed .gitkeep",
    "scaffold.py::_preflight_conflicts": "the same emptiness question, asked before any write",
}
_WALK_CALLS = frozenset({"glob", "rglob", "iterdir"})
_SCOPES = (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp, ast.stmt)


def _calls_is_excluded(node: ast.AST) -> bool:
    return any(
        isinstance(sub, ast.Call)
        and (
            (isinstance(sub.func, ast.Name) and sub.func.id == "is_excluded")
            or (isinstance(sub.func, ast.Attribute) and sub.func.attr == "is_excluded")
        )
        for sub in ast.walk(node)
    )


def test_every_walker_in_the_package_uses_the_one_predicate():
    """#194: the predicate is only a mechanism if every walker calls it. Every
    `glob`, `rglob` and `iterdir` in the package must call `is_excluded` in its
    nearest enclosing comprehension, else its statement (a `for` loop's body
    included), or be listed in `_NOT_NOTE_WALKS`. `gitstate`'s `os.scandir` and
    `os.listdir` are not scanned: a content-identity snapshot hashes every node."""
    root = Path(__file__).resolve().parents[1] / "research_vault"
    offenders, allowed = [], set()
    for module in sorted(root.glob("*.py")):
        tree = package_ast(module)
        parents = {
            child: node
            for node in ast.walk(tree)
            for child in ast.iter_child_nodes(node)
        }
        for call in ast.walk(tree):
            if not (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and call.func.attr in _WALK_CALLS
            ):
                continue
            scope: ast.AST = parents[call]
            while not isinstance(scope, _SCOPES):
                scope = parents[scope]
            function: ast.AST = scope
            while function in parents and not isinstance(
                function, (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                function = parents[function]
            key = f"{module.name}::{getattr(function, 'name', '<module>')}"
            if key in _NOT_NOTE_WALKS:
                allowed.add(key)
            elif not _calls_is_excluded(scope):
                offenders.append(f"{module.name}:{call.lineno}")
    assert offenders == [], offenders
    assert allowed == set(_NOT_NOTE_WALKS), set(_NOT_NOTE_WALKS) - allowed


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


def test_check_note_frontmatter_reports_an_unconstructable_value_not_a_traceback(
    tmp_path,
):
    """`!!int abc` makes PyYAML's int constructor raise a plain ValueError;
    the check reports it as unparseable frontmatter."""
    path = _write(
        tmp_path, "projects/brief/notes.md", "---\ntype: note\ntitle: !!int abc\n---\n"
    )
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.reason.startswith(
        "schema-violation — frontmatter unparseable (frontmatter is not valid YAML: "
        "cannot construct a value (ValueError: "
    )


def test_root_index_with_a_boolean_key_is_reported_not_a_traceback(tmp_path):
    """`yes: 1` gives a bool key under the YAML loader; `sorted()` over mixed
    keys raises TypeError without `key=str` (Q18)."""
    _write(tmp_path, "index.md", '---\nokf_version: "0.2"\nyes: 1\n---\n# x\n')
    rows = structure.check_reserved(tmp_path)
    assert any("carries keys beyond okf_version: ['True']" in o.reason for o in rows)
