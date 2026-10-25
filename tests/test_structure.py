import ast
import os
import subprocess
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
    assert structure.expected_type("log/2026-08-20.md") == "log"
    assert structure.expected_type("daily/2026-08-20.md") == "daily"
    assert structure.expected_type("daily/weekly/2026-W34.md") == "daily"
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
        == "schema-violation — type 'literature' but folder derives 'log'"
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


def test_reserved_check_passes_only_the_compile_tools_files_under_wiki(tmp_path):
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
    assert problems[0].reason == (
        "schema-violation — reserved name under wiki/ outside the compile tool's "
        "files (wiki/index.md, wiki/log.md, wiki/canvases/index.md)"
    )


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
        "daily/log.md",
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
            "schema-violation — literature/ is flat",
        ),
        (
            "tree",
            "literature/zzz/",
            Result.UNMATCHED,
            "schema-violation — literature/ is flat",
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
            "schema-violation — literature/ is flat",
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
        # The link index's whole file set and the captured-set maps it adds.
        "captured-link-index": lambda v: (
            captured.literature_paths(v),
            sorted(captured.link_index(v)._exact.values()),
        ),
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
        "log-dir": structure.check_log_dir,
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
# The stray inventories of the flat machine folders (`check_log_dir` over
# log/, `check_tree` over literature/) are not listed: they call
# `is_excluded`, but only to skip a dot-directory, and report a dot-named
# file as a stray rather than exclude it (#204, #211).
_NOT_NOTE_WALKS = {
    "scaffold.py::_template_files": "the package's own template tree, not a vault",
    "scaffold.py::_add_empty_root_sentinels": "asks only whether a root is empty, to seed .gitkeep",
    "scaffold.py::_preflight_conflicts": "the same emptiness question, asked before any write",
}
_WALK_CALLS = frozenset({"glob", "rglob", "iterdir", "walk"})
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
    `glob`, `rglob`, `iterdir` and `walk` (`os.walk`, `Path.walk`) in the
    package must call `is_excluded` in its nearest enclosing comprehension,
    else its statement (a `for` loop's body included), or be listed in
    `_NOT_NOTE_WALKS`. `gitstate`'s `os.scandir` and `os.listdir` are not
    scanned: a content-identity snapshot hashes every node."""
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


WRITER = "research_vault/0.1.0"


def _rows(vault, check=None):
    rows = structure.check_reserved(vault) + structure.check_log_dir(vault)
    return [
        (o.check, o.target, o.reason)
        for o in rows
        if o.result is Result.UNMATCHED and (check is None or o.check == check)
    ]


def test_log_dir_reports_strays_under_their_own_paths_never_under_log_md(tmp_path):
    """#204: a non-date file, a dot-named file, a compact date, an impossible
    date, a stray heading and a hand-typed line are each a row on their own
    file, numbered by the file's own lines; so is a day file whose frontmatter
    only the OKF reader accepts, which the render drops whole. OS litter and
    `.gitkeep` are no entry, nor is a sync tool's dot-directory (#194)."""
    from research_vault import okf

    _scaffold_min(tmp_path)
    log = tmp_path / "log"
    _write(tmp_path, "log/Untitled.md", "- stray\n")
    _write(
        tmp_path, "log/2026-13-45.md", f'---\ntype: "log"\n---\n- 09:00 {WRITER} — x\n'
    )
    _write(
        tmp_path, "log/20261004.md", f'---\ntype: "log"\n---\n- 09:00 {WRITER} — x\n'
    )
    _write(
        tmp_path,
        "log/2026-10-01.md",
        f'---\ntype: "log"\n---\n## Agenda\n- 09:00 {WRITER} — real\n- hand-typed\n',
    )
    _write(
        tmp_path,
        "log/2026-10-02.md",
        "---\ntype: log\nmeta:\n  a: 1\n---\n- hand-typed\n",
    )
    (log / "nested").mkdir()
    (log / ".stversions").mkdir()  # a sync tool's store: no entry
    (log / ".gitkeep").touch()
    _write(tmp_path, "log/.x.md", "- a force-added dot-named stray\n")
    (log / ".DS_Store").write_bytes(b"\x00\x05\x16\x07")  # OS litter: no entry
    okf.regenerate_log(tmp_path)
    rows = _rows(tmp_path)
    assert rows == [
        (
            "okf-structure",
            "path-bytes:log/.x.md",
            "schema-violation — log/ holds only <YYYY-MM-DD>.md day files and .gitkeep",
        ),
        (
            "okf-structure",
            "path-bytes:log/2026-10-01.md",
            "schema-violation — line 4 is not in the writer's format: '## Agenda'",
        ),
        (
            "okf-structure",
            "path-bytes:log/2026-10-01.md",
            "schema-violation — line 6 is not in the writer's format: '- hand-typed'",
        ),
        (
            "okf-structure",
            "path-bytes:log/2026-10-02.md",
            "schema-violation — frontmatter is not the writer's flat form",
        ),
        (
            "okf-structure",
            "path-bytes:log/2026-13-45.md",
            "schema-violation — log/ holds only <YYYY-MM-DD>.md day files and .gitkeep",
        ),
        (
            "okf-structure",
            "path-bytes:log/20261004.md",
            "schema-violation — log/ holds only <YYYY-MM-DD>.md day files and .gitkeep",
        ),
        (
            "okf-structure",
            "path-bytes:log/Untitled.md",
            "schema-violation — log/ holds only <YYYY-MM-DD>.md day files and .gitkeep",
        ),
        ("tree", "log/nested/", "schema-violation — log/ is flat"),
    ]
    assert not any("log.md" in target for _check, target, _reason in rows)


_TOOL_INDEX = (
    "---\ntype: meta\ntitle: W\nstatus: s\ncreated: 2026-01-01\n"
    "updated: 2026-01-01\ntags:\n  - m\n---\n# W\n"
)


@pytest.mark.parametrize(
    ("relative", "text", "refused"),
    [
        # a reserved name under wiki/ outside the tool's files
        ("wiki/topic/index.md", "", True),
        ("wiki/other/log.md", "prose, no date headings\n", True),
        ("system/propagations/index.md", "", True),
        ("projects/p/index.md", "Some prose that is not a heading or a list.\n", True),
        ("projects/p/index.md", "# Project\n\n- [draft](draft.md)\n", False),
        # a list entry's indented continuation line
        (
            "projects/p/index.md",
            "# P\n\n- [draft](draft.md)\n  the current draft\n",
            False,
        ),
        # indented prose under no list entry
        ("projects/p/index.md", "# P\n\n  indented prose\n", True),
        # a nested index carries no frontmatter (OKF §8), an empty block included
        ("projects/p/index.md", '---\ntype: "index"\n---\n# P\n', True),
        ("projects/p/index.md", "---\n\n---\n# P\n", True),
        # an empty nested index is valid (OKF §8, Q22)
        ("daily/index.md", "", False),
        ("daily/log.md", "", False),
        ("daily/log.md", '---\ntype: "log"\n---\n## 2026-10-24\n- x\n', False),
        # a heading that is no calendar date
        ("daily/log.md", "## 2026-13-45\n- x\n", True),
        # a block that does not parse
        ("daily/log.md", "---\nnot a mapping\n---\n", True),
        # rule 2 when a block is present
        ("daily/log.md", "---\ntype: null\n---\n", True),
        ("wiki/index.md", _TOOL_INDEX, False),
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


_LOG_DIFFERS = (
    "schema-violation — root log.md differs from its render; run stamp-type, "
    "which regenerates it, and stage log.md; or stage the day files it renders from"
)


def test_log_dir_numbers_lines_as_an_editor_counts_them(tmp_path):
    """A form feed, NEL or U+2028 inside a day file's line does not shift the
    numbers of the rows after it: a line ends at `\\n` only. The render reads
    lines through `splitlines`, so it drops what follows the separator, and
    the line holding it is a row of its own."""
    _scaffold_min(tmp_path)
    _write(
        tmp_path,
        "log/2026-10-01.md",
        f'---\ntype: "log"\n---\n- 09:00 {WRITER} — a\x0cb\n'
        f"- 09:00 {WRITER} — c\x85d\u2028e\n- 09:00 {WRITER} — fine\n- hand-typed\n",
    )
    assert _rows(tmp_path) == [
        (
            "okf-structure",
            "path-bytes:log/2026-10-01.md",
            (
                "schema-violation — line 4 is not in the writer's format: "
                f"'- 09:00 {WRITER} — a\\x0cb'"
            ),
        ),
        (
            "okf-structure",
            "path-bytes:log/2026-10-01.md",
            (
                "schema-violation — line 5 is not in the writer's format: "
                f"'- 09:00 {WRITER} — c\\x85d\\u2028e'"
            ),
        ),
        (
            "okf-structure",
            "path-bytes:log/2026-10-01.md",
            "schema-violation — line 7 is not in the writer's format: '- hand-typed'",
        ),
    ]


def test_root_log_md_must_equal_its_render(tmp_path):
    """#210: every edit to the root log — an entry, a removed entry, the
    frontmatter, the heading order, an extra line, CRLF line endings — is
    refused naming log.md, a missing log.md passes, and the fixer repairs it."""
    from research_vault import fixer, okf

    _scaffold_min(tmp_path)
    _write(
        tmp_path,
        "log/2026-10-01.md",
        f'---\ntype: "log"\n---\n- 09:00 {WRITER} — one\n',
    )
    _write(
        tmp_path,
        "log/2026-10-02.md",
        f'---\ntype: "log"\n---\n- 09:00 {WRITER} — two\n',
    )
    rendered = okf.regenerate_log(tmp_path)
    assert _rows(tmp_path) == []
    for edit in (
        rendered.replace("— one", "— won"),
        rendered.replace(f"- 09:00 {WRITER} — one\n", ""),
        rendered.replace('---\ntype: "log"\n---\n', ""),
        rendered.replace("## 2026-10-02", "## 2026-10-03"),
        rendered + "- a hand-typed line\n",
        rendered.replace("\n", "\r\n"),  # byte for byte, not text for text
    ):
        assert edit != rendered
        (tmp_path / "log.md").write_bytes(edit.encode("utf-8"))
        rows = _rows(tmp_path)
        assert rows == [("okf-structure", "path-bytes:log.md", _LOG_DIFFERS)], edit
    report = fixer.fix(tmp_path, paths=[])
    assert report.log_regenerated is True
    assert _rows(tmp_path) == []
    (tmp_path / "log.md").unlink()
    assert _rows(tmp_path) == []


_LOG_BLOCKER = f"UNMATCHED okf-structure path-bytes:log.md — {_LOG_DIFFERS}"


def _staged_fixer_says(vault, capsys):
    from research_vault.__main__ import main

    assert main(["stamp-type", "--vault", str(vault), "--staged"]) == 0
    return capsys.readouterr().out.splitlines()


def _commit_blockers(vault, candidate):
    from research_vault import verify

    _report, effective, _hashes, warning = verify.verify_state(
        vault, network=False, git_candidate=candidate
    )
    return verify.surface_decision("commit", effective, warning)[1]


def test_a_staged_day_file_deletion_is_refused_at_commit(fixture_vault, capsys):
    """A staged deletion of a day file triggers the hook's render (R8), which
    writes the worktree only (#203), so the commit surface compares the
    index's log.md with a render of the index's day files: the deleted
    day's heading is still in the staged log until the render is staged."""
    subprocess.run(
        ["git", "rm", "-q", "log/2026-08-16.md"], cwd=fixture_vault, check=True
    )
    assert _staged_fixer_says(fixture_vault, capsys) == ["regenerated log.md"]
    assert _LOG_BLOCKER in _commit_blockers(fixture_vault, "index")
    subprocess.run(["git", "add", "log.md"], cwd=fixture_vault, check=True)
    # verify wrote the review queue and its marks (#260, #269); an
    # index-candidate run refuses a tracked file that differs from the
    # index, so every other file is restored to it.
    subprocess.run(["git", "checkout", "--", "."], cwd=fixture_vault, check=True)
    assert _LOG_BLOCKER not in _commit_blockers(fixture_vault, "index")


def test_a_stale_staged_log_beside_a_fresh_worktree_one_is_refused_at_commit(
    fixture_vault, capsys
):
    """A day file staged without log.md: the worktree's log.md equals its
    render, so the hook's fixer says nothing; the index's lacks the new day,
    and the index is what the commit records."""
    from research_vault import okf

    _write(
        fixture_vault,
        "log/2026-08-17.md",
        f'---\ntype: "log"\n---\n- 09:00 {WRITER} — staged\n',
    )
    subprocess.run(["git", "add", "log/2026-08-17.md"], cwd=fixture_vault, check=True)
    okf.regenerate_log(fixture_vault)
    assert _staged_fixer_says(fixture_vault, capsys) == []
    assert _LOG_BLOCKER in _commit_blockers(fixture_vault, "index")
    assert _LOG_BLOCKER not in _commit_blockers(fixture_vault, "worktree")


def test_stamp_leaves_reserved_names_untouched_anywhere(tmp_path):
    from research_vault import stamp

    _write(tmp_path, "log/log.md", "bare\n")
    _write(tmp_path, "projects/p/index.md", "bare\n")
    stamped, _reported = stamp.stamp_types(tmp_path)
    assert stamped == []
    assert (tmp_path / "log" / "log.md").read_text() == "bare\n"


_LITERATURE_STRAY = (
    "schema-violation — literature/ holds only <citation key>.md and .gitkeep"
)


def test_check_tree_reports_a_stray_file_under_literature(tmp_path):
    from research_vault import scaffold

    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "literature" / "smith2020.pdf").write_bytes(b"%PDF")
    (tmp_path / "literature" / "notes.txt").write_text("x\n")
    (tmp_path / "literature" / "bad key.md").write_text("x\n")
    (tmp_path / "literature" / "smith2020.md").write_text(
        '---\ntype: "literature"\n---\n'
    )
    (tmp_path / "literature" / ".DS_Store").write_bytes(b"\0")
    rows = [
        (o.target, o.reason)
        for o in structure.check_tree(tmp_path)
        if o.result is Result.UNMATCHED
    ]
    assert rows == [
        ("path-bytes:literature/bad%20key.md", _LITERATURE_STRAY),
        ("path-bytes:literature/notes.txt", _LITERATURE_STRAY),
        ("path-bytes:literature/smith2020.pdf", _LITERATURE_STRAY),
    ]


def test_a_dot_named_stray_under_literature_is_a_row_too(tmp_vault):
    """literature/ is a machine surface, so a force-added dot-named file is a
    stray, as it is in log/: every reader skips it, so it is a literature note
    nowhere. OS litter and a sync tool's dot-directory (#194) are no entry."""
    literature = tmp_vault / "literature"
    (literature / ".x.md").write_text('---\ntype: "literature"\n---\n')
    (literature / ".notes.pdf").write_bytes(b"%PDF")
    (literature / "._smith2020.md").write_bytes(b"\x00\x05\x16\x07")
    (literature / ".DS_Store").write_bytes(b"\0")
    (literature / "desktop.ini").write_bytes(b"[.ShellClassInfo]\r\n")
    (literature / ".stversions").mkdir()
    assert [
        o.target
        for o in structure.check_tree(tmp_vault)
        if o.result is Result.UNMATCHED
    ] == ["path-bytes:literature/.notes.pdf", "path-bytes:literature/.x.md"]


def test_stray_file_in_literature_closes_the_commit(tmp_path):
    from research_vault import scaffold, verify

    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "literature" / "paper.pdf").write_bytes(b"%PDF")
    _report, effective, _hashes, warning = verify.verify_state(
        tmp_path, network=False, git_candidate="worktree"
    )
    decision, blockers = verify.surface_decision("commit", effective, warning)
    assert decision == 1
    assert any(
        "literature/paper.pdf" in b and b.startswith("UNMATCHED tree") for b in blockers
    )


def test_a_stray_with_a_non_utf8_name_is_a_row_not_a_crash(tmp_path):
    """The reason carries no path: a raw name that is not UTF-8 decodes to a
    lone surrogate, which the queue's strict UTF-8 write refuses. The encoded
    target names the file."""
    from research_vault import scaffold, verify

    scaffold.scaffold_vault(tmp_path)
    try:
        (tmp_path / "literature" / os.fsdecode(b"caf\xe9.pdf")).write_bytes(b"%PDF")
    except OSError:
        pytest.skip("the filesystem refuses a name that is not UTF-8")
    _report, effective, _hashes, warning = verify.verify_state(
        tmp_path, network=False, git_candidate="worktree"
    )
    decision, blockers = verify.surface_decision("commit", effective, warning)
    assert decision == 1
    assert (
        f"UNMATCHED tree path-bytes:literature/caf%E9.pdf — {_LITERATURE_STRAY}"
        in blockers
    )


@pytest.mark.parametrize(
    "relative", ["wiki/x.md", "inbox/moved.md", "projects/p/text.md", "D7EJ9FTG.md"]
)
def test_type_fulltext_is_reserved_for_the_text_layer(tmp_path, relative):
    """§5.5: a text file an Obsidian rename or Auto Note Mover carried out of
    fulltext/ is refused, before inbox/'s fleeting exemption (Q26)."""
    path = _write(
        tmp_path,
        relative,
        '---\ntype: "fulltext"\nzotero-attachment-key: "D7EJ9FTG"\n---\ntext\n',
    )
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.UNMATCHED
    assert (
        outcome.reason == "schema-violation — type 'fulltext' is reserved for fulltext/"
    )


def test_a_text_file_in_its_own_layer_still_passes(tmp_path):
    path = _write(
        tmp_path, "fulltext/D7EJ9FTG.md", '---\ntype: "fulltext"\n---\ntext\n'
    )
    (outcome,) = structure.check_note_frontmatter(tmp_path, path)
    assert outcome.result is Result.MATCHED
    assert (
        structure.check_note_frontmatter(
            tmp_path, _write(tmp_path, "inbox/idea.md", "bare\n")
        )
        == []
    )


@pytest.mark.parametrize(
    "data",
    [b"---\nsee: x\n[[nowhere]]\n", b"caf\xe9\n"],
    ids=["unterminated-frontmatter", "not-utf-8"],
)
def test_an_unreadable_fleeting_capture_is_still_exempt(tmp_path, data):
    """Parsing now comes before the fleeting return, so a capture whose
    frontmatter does not parse, or whose bytes do not decode, is still no row."""
    path = tmp_path / "inbox" / "x.md"
    path.parent.mkdir()
    path.write_bytes(data)
    assert structure.check_note_frontmatter(tmp_path, path) == []


def test_the_text_layer_folder_is_one_name_in_every_module_that_spells_it():
    """structure copies `fulltext.FULLTEXT_DIR` rather than import the
    transport (`literature_notes`' precedent for `ITEM_KEY`), and stamp's
    whole-vault skip spells it too: one name, pinned here."""
    from research_vault import fulltext, stamp

    assert structure._FULLTEXT_DIR == fulltext.FULLTEXT_DIR
    assert frozenset({fulltext.FULLTEXT_DIR}) == stamp._SKIP_DIRS
