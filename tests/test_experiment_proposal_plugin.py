"""Plugin-scoped checks for ``plugins/experiment-proposal``.

Spec: ``docs/superpowers/specs/2026-10-13-experiment-proposal-plugin-design.md``,
section Tests. The plugin is a second plugin in this repository's marketplace
and shares no code with ``research_vault``; the repository's skill tests glob
only the root ``skills/``, so this module carries the plugin's own contract:
manifests, skill frontmatter and Codex metadata, provenance headers, licence
notices, the checklist's grammar and graph, the citations the skills make, the
paths they name and the vendored scripts.
"""

import ast
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "experiment-proposal"
MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"


def _canonical(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------
# Manifests
# --------------------------------------------------------------------------


def test_plugin_manifest_is_valid_and_canonical():
    """A manifest the plugin loader cannot parse fails at load with no message;
    a non-canonical one drifts from the repository's one JSON form owner."""
    assert MANIFEST.is_file(), f"{MANIFEST.relative_to(ROOT)} is missing"
    raw = MANIFEST.read_text(encoding="utf-8")
    manifest = json.loads(raw)
    assert raw == _canonical(manifest), (
        "plugin.json is not in canonical JSON form. Fix it with:\n"
        "    python -m json.tool --indent 2 --no-ensure-ascii "
        f"{MANIFEST.relative_to(ROOT)} {MANIFEST.relative_to(ROOT)}"
    )
    assert manifest["name"] == "experiment-proposal"
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]), manifest["version"]
    for key in ("description", "author", "license"):
        assert key in manifest, f"plugin.json lacks {key}"
    assert manifest["license"] == "MIT"


def test_marketplace_entry_names_the_plugin_and_resolves_to_its_folder():
    """The entry's name equals the manifest's name, carries no version (the
    version has one writer: plugin.json), and its source resolves to the folder
    that holds the plugin's own .claude-plugin/plugin.json."""
    market = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    entries = [p for p in market["plugins"] if p["name"] == "experiment-proposal"]
    assert len(entries) == 1, (
        "marketplace.json needs exactly one experiment-proposal entry"
    )
    entry = entries[0]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert entry["name"] == manifest["name"]
    assert "version" not in entry
    assert entry["source"] == "./plugins/experiment-proposal"
    source = (ROOT / entry["source"]).resolve()
    assert (source / ".claude-plugin" / "plugin.json") == MANIFEST.resolve()
    assert entry["description"].strip()


def test_plugin_ships_its_own_mit_licence():
    """A subdirectory install does not ship the repository's root LICENSE."""
    text = (PLUGIN / "LICENSE").read_text(encoding="utf-8")
    assert text.startswith("MIT License")
    assert "Copyright (c) 2026 Eran Roseman" in text
    assert "Permission is hereby granted, free of charge" in text


# --------------------------------------------------------------------------
# Skills: frontmatter and Codex metadata (the generic contract, every skill)
# --------------------------------------------------------------------------

SKILLS_DIR = PLUGIN / "skills"
SKILL_DIRS = (
    sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()) if SKILLS_DIR.is_dir() else []
)
EXPECTED_SKILLS = {"design", "review", "lit-search", "the-ethics-board"}


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path.relative_to(ROOT)} does not open with ---"
    closing = text.index("\n---\n", len("---\n"))
    data = yaml.safe_load(text[len("---\n") : closing + 1])
    assert isinstance(data, dict), f"{path.relative_to(ROOT)} frontmatter is not a map"
    return data


def _raw_frontmatter_lines(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    closing = text.index("\n---\n", len("---\n"))
    return text[len("---\n") : closing + 1].splitlines()


def test_the_four_skills_ship():
    assert {p.name for p in SKILL_DIRS} == EXPECTED_SKILLS


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda p: p.name)
def test_skill_frontmatter_names_itself_and_is_name_only(skill_dir):
    """name == directory (the plugin contract); a non-empty description; and
    `disable-model-invocation: true` as a raw unquoted YAML boolean line, which
    the loader reads as real YAML -- `"true"`, `yes` and `True` are silent
    mis-reads a parsed value would not distinguish."""
    skill_md = skill_dir / "SKILL.md"
    data = _frontmatter(skill_md)
    assert data.get("name") == skill_dir.name
    assert isinstance(data.get("description"), str)
    assert data["description"].strip()
    raw = [
        line.partition(":")[2].strip()
        for line in _raw_frontmatter_lines(skill_md)
        if line.partition(":")[0].strip() == "disable-model-invocation"
    ]
    assert raw == ["true"], f"{skill_dir.name}: disable-model-invocation line is {raw}"


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda p: p.name)
def test_skill_has_codex_metadata_that_forbids_implicit_invocation(skill_dir):
    """Codex reads agents/openai.yaml instead of disable-model-invocation."""
    meta_path = skill_dir / "agents" / "openai.yaml"
    assert meta_path.is_file(), f"{skill_dir.name} lacks agents/openai.yaml"
    meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
    assert meta["policy"]["allow_implicit_invocation"] is False
    assert meta["interface"]["display_name"].strip()
    assert meta["interface"]["short_description"].strip()


# --------------------------------------------------------------------------
# Vendored files: provenance headers, local edits, notices
# --------------------------------------------------------------------------

KDENSE = (
    "https://github.com/K-Dense-AI/scientific-agents",
    "98c7fae46648724e1a43a1f2b207b0c82fcc462e",
    "K-Dense, Inc.",
)
HUTZELMANN = (
    "https://github.com/hutzelmann/thesis-proposal-skills",
    "a38b7b117513b9e4e50f08770d0049aae3e75398",
    "Thomas Hutzelmann",
)
PM_SKILLS = (
    "https://github.com/mohitagw15856/pm-claude-skills",
    "f93fee7459e2bf452ec9bc43163004812efba51f",
    "Mohit Aggarwal",
)
LIT_SEARCH_SCRIPTS = [
    "arxiv.py",
    "common.py",
    "crossref.py",
    "dblp.py",
    "openalex.py",
    "opencitations.py",
    "search.py",
    "semantic_scholar.py",
    "snowball.py",
]
SCRIPTS = PLUGIN / "skills" / "lit-search" / "scripts"
# plugin path -> (upstream url, sha, holder, upstream path)
VENDORED = {
    "agents/hci-researcher.md": (
        *KDENSE,
        (
            "scientific-agents/human-computer-interaction-researcher/agents/"
            "human-computer-interaction-researcher.md"
        ),
    ),
    "skills/the-ethics-board/SKILL.md": (
        *PM_SKILLS,
        "skills/the-ethics-board/SKILL.md",
    ),
    **{
        f"skills/lit-search/scripts/{name}": (
            *HUTZELMANN,
            f"skills/proposal-lit-search/scripts/{name}",
        )
        for name in LIT_SEARCH_SCRIPTS
    },
}
HEADER_CLOSE = "Do not hand-edit this file; re-vendor from upstream to update it."


@pytest.mark.parametrize(
    "relative", sorted(VENDORED), ids=lambda s: s.rsplit("/", 1)[-1]
)
def test_every_vendored_file_carries_a_full_provenance_header(relative):
    url, sha, holder, upstream_path = VENDORED[relative]
    path = PLUGIN / relative
    text = path.read_text(encoding="utf-8")
    assert f"Vendored from {url} @ {sha}" in text, f"{relative}: header lacks url @ sha"
    assert f"({upstream_path})" in text, f"{relative}: header lacks the upstream path"
    assert "license MIT" in text, f"{relative}: no licence"
    assert holder in text, f"{relative}: no copyright holder"
    assert "experiment-proposal plugin" in text, f"{relative}: no rename note"
    assert HEADER_CLOSE in text, f"{relative}: header lacks the closing line"
    if relative.endswith(".py"):
        lines = text.splitlines()
        assert lines[0] == "#!/usr/bin/env python3"
        assert lines[1].startswith("# Vendored from "), (
            f"{relative}: header not after shebang"
        )
    else:
        # Opens with YAML frontmatter; the header follows the closing fence.
        assert text.startswith("---\n")
        closing = text.index("\n---\n", len("---\n")) + len("\n---\n")
        assert text.index("<!--") >= closing, (
            f"{relative}: header must follow frontmatter"
        )
        assert "mdformat normalized this file" in text
        if relative == "agents/hci-researcher.md":
            assert "a tools line" in text, (
                f"{relative}: header lacks the tools-line edit"
            )


def test_the_subagent_is_renamed_with_a_marked_local_edit():
    agent = PLUGIN / "agents" / "hci-researcher.md"
    assert _frontmatter(agent)["name"] == "hci-researcher"
    raw = "\n".join(_raw_frontmatter_lines(agent))
    assert "# local edit (experiment-proposal)" in raw
    assert (
        "human-computer-interaction-researcher" in raw
    )  # the edit names what it replaced


def test_the_ethics_board_gains_only_the_marked_invocation_edit():
    raw = "\n".join(
        _raw_frontmatter_lines(PLUGIN / "skills" / "the-ethics-board" / "SKILL.md")
    )
    assert "# local edit (experiment-proposal)" in raw
    assert "disable-model-invocation: true" in raw


def test_third_party_notices_carry_the_mit_text_and_every_copyright_holder():
    text = (PLUGIN / "THIRD-PARTY-NOTICES.md").read_text(encoding="utf-8")
    assert "Permission is hereby granted, free of charge" in text
    assert 'THE SOFTWARE IS PROVIDED "AS IS"' in text
    for holder in (
        "K-Dense, Inc.",
        "Thomas Hutzelmann",
        "Mohit Aggarwal",
        "Matt Pocock",
    ):
        assert f"Copyright (c) 2026 {holder}" in text, f"notices lack {holder}"
    assert "statistical-power" not in text
    assert "three marked local edits" in text


# --------------------------------------------------------------------------
# lit-search scripts: frozen upstream code that must still work after the
# header edit, offline, and never write a file or import research_vault
# --------------------------------------------------------------------------


def test_exactly_the_nine_upstream_scripts_are_vendored():
    assert sorted(p.name for p in SCRIPTS.glob("*.py")) == LIT_SEARCH_SCRIPTS


@pytest.mark.parametrize("name", LIT_SEARCH_SCRIPTS)
def test_vendored_script_compiles(name):
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(SCRIPTS / name)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


# Run in a child process, where the suite's in-process socket block does not
# reach: replace the two ways out to the network with functions that raise,
# then run the script as __main__. With -c, sys.path[0] is the cwd (the scripts
# directory), so the scripts' bare-name sibling imports resolve.
_NO_NETWORK_RUNNER = """
import runpy, socket, sys


def _blocked(*args, **kwargs):
    raise OSError("network blocked in test")


socket.socket.connect = _blocked
socket.getaddrinfo = _blocked
script = sys.argv[1]
sys.argv = [script, *sys.argv[2:]]
runpy.run_path(script, run_name="__main__")
"""


@pytest.mark.parametrize("name", ["search.py", "snowball.py"])
def test_vendored_entry_point_prints_help_without_network(name):
    """The entry points import their siblings by bare name, so they run from
    their own directory (never with -I). The child process has socket.connect
    and socket.getaddrinfo replaced by functions that raise, so a --help that
    reached for the network would fail here (the suite's own socket block
    patches only the pytest process, not a subprocess). -B keeps the child
    from writing __pycache__ into the vendored directory."""
    result = subprocess.run(
        [sys.executable, "-B", "-c", _NO_NETWORK_RUNNER, name, "--help"],
        capture_output=True,
        text=True,
        check=False,
        cwd=SCRIPTS,
    )
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout


_WRITE_SHAPES = re.compile(
    r"write_text\(|write_bytes\(|\.mkdir\(|makedirs\(|\bopen\([^)]*[\"'][wax]"
)


@pytest.mark.parametrize("name", LIT_SEARCH_SCRIPTS)
def test_vendored_script_writes_no_files_and_stays_standalone(name):
    """The spec's claim that lit-search writes nothing rests on the scripts
    printing CSL-YAML to stdout and nothing to disk; a re-vendor that adds a
    cache file must fail here, not surprise a user."""
    text = (SCRIPTS / name).read_text(encoding="utf-8")
    assert not _WRITE_SHAPES.search(text), f"{name} writes a file"
    assert "research_vault" not in text, f"{name} imports research_vault"


def _names_the_scripts_read_from_the_environment() -> set[str]:
    """Literal names passed to os.environ.get / os.getenv / common.get_key,
    plus the KEY_FILE_ENV constant that names the key-file override, off the
    scripts' ASTs."""
    names: set[str] = set()
    for path in SCRIPTS.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
                if "KEY_FILE_ENV" in targets and isinstance(node.value, ast.Constant):
                    names.add(node.value.value)
            if not isinstance(node, ast.Call) or not node.args:
                continue
            func = node.func
            attr = getattr(func, "attr", None) or getattr(func, "id", None)
            if attr not in {"get", "getenv", "get_key"}:
                continue
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                if attr == "get":
                    source = (
                        ast.unparse(func.value)
                        if isinstance(func, ast.Attribute)
                        else ""
                    )
                    if source not in {"os.environ", "environ"}:
                        continue
                names.add(first.value)
    return names


def test_the_scripts_read_exactly_the_documented_environment_names():
    """Pinned so the lit-search SKILL.md (Task 7) can name every variable and
    file the scripts consult; a re-vendor that reads a new name fails here."""
    assert _names_the_scripts_read_from_the_environment() == {
        "OPENALEX_API_KEY",
        "CONTACT_EMAIL",
        "OPENCITATIONS_TOKEN",
        "THESIS_PROPOSAL_KEYS",
    }


# --------------------------------------------------------------------------
# The checklist: grammar, graph, and the sets the skills rely on
# --------------------------------------------------------------------------

CHECKLIST = PLUGIN / "references" / "checklist.md"
CITATION = re.compile(r"\bitems? (\d{1,2}\.\d{1,2}(?:(?:, | and )\d{1,2}\.\d{1,2})*)")
# The spec's design tree, by step: 1 question, ethics route, data plan; 2 session
# estimate, pilot, timeline, challenges; 6 hypotheses, directions, interactions;
# 7 variables, within/between, carry-over, assignment, counterbalancing,
# controls, confounds; 8 eligibility, the justified count.
DESIGN_TREE = {
    "1.1", "1.2", "1.3",
    "2.2", "2.3", "2.4", "2.5",
    "6.1", "6.2", "6.5",
    "7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "7.8", "7.9",
    "8.3", "8.5",
}  # fmt: skip
ATTESTED = {"3.1", "5.2", "13.1", "13.4"}
DEFEND_STAGE = {"13.2", "13.3"}


_CHECKER_SPEC = importlib.util.spec_from_file_location(
    "check_proposal", PLUGIN / "scripts" / "check_proposal.py"
)
assert _CHECKER_SPEC is not None
assert _CHECKER_SPEC.loader is not None
_checker = importlib.util.module_from_spec(_CHECKER_SPEC)
# a dataclass resolves its module through sys.modules while the class is built
sys.modules[_CHECKER_SPEC.name] = _checker
_CHECKER_SPEC.loader.exec_module(_checker)


def _checklist_items() -> dict[str, dict]:
    """The checklist through the checker's own parser: one grammar, one writer."""
    return {
        item_id: {
            "kind": item.kind,
            "scope": item.scope,
            "depends": list(item.depends),
            "text": item.text,
            "line": item.line,
        }
        for item_id, item in _checker.read_checklist(CHECKLIST).items()
    }


def _cited_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for match in CITATION.finditer(text):
        ids.update(re.findall(r"\d{1,2}\.\d{1,2}", match.group(1)))
    return ids


def test_checklist_has_the_items_of_the_twelve_checked_steps():
    """Step 11 is not checked (the lens's section list has no Planned Analysis
    section); the other twelve steps keep their items."""
    items = _checklist_items()
    assert len(items) == 67, len(items)
    assert {int(i.split(".")[0]) for i in items} == set(range(1, 14)) - {11}
    for item_id, item in items.items():
        assert item["text"].rstrip().endswith("."), (
            f"{item_id} does not end in a full stop"
        )


def test_every_dependency_resolves_and_the_graph_is_acyclic():
    """`design` orders its rounds by `depends on`; a cycle would leave the
    frontier empty with items still missing."""
    items = _checklist_items()
    for item_id, item in items.items():
        for dep in item["depends"]:
            assert dep in items, f"{item_id} depends on {dep}, which does not exist"
            assert dep != item_id, f"{item_id} depends on itself"
    state: dict[str, int] = {}

    def visit(node: str, path: list[str]) -> None:
        if state.get(node) == 2:
            return
        assert state.get(node) != 1, f"dependency cycle: {' -> '.join([*path, node])}"
        state[node] = 1
        for dep in items[node]["depends"]:
            visit(dep, [*path, node])
        state[node] = 2

    for item_id in items:
        visit(item_id, [])


def test_the_design_tree_attested_and_defend_stage_sets_are_the_specs():
    items = _checklist_items()
    assert {i for i, it in items.items() if it["scope"] == "design-tree"} == DESIGN_TREE
    assert {i for i, it in items.items() if it["kind"] == "attested"} == ATTESTED
    assert {
        i for i, it in items.items() if it["kind"] == "defend-stage"
    } == DEFEND_STAGE
    assert all(items[i]["scope"] == "review-only" for i in DEFEND_STAGE)
    assert items["8.5"]["kind"] == "draft-checked"
    assert "similar experiments" in items["8.5"]["text"]
    assert "power" not in items["8.5"]["text"]
    assert {i for i in items if i.startswith("13.") and int(i.split(".")[1]) >= 6} == {
        "13.6",
        "13.7",
        "13.8",
        "13.9",
        "13.10",
        "13.11",
    }


def test_checklist_names_its_provenance_the_lens_and_its_deviations():
    text = CHECKLIST.read_text(encoding="utf-8")
    assert "98b978fb74b7480c9967ceb2a1100e4560081af5" in text
    assert "the lens" in text
    assert "2026-10-14-experiment-proposal-v2-design.md" in text
    assert "## Deviations" in text
    assert (
        "Planned Analysis" in text
    )  # the dropped step is named, so a reader knows why
    for credit in ("proposal-supervise", "research-grill", "lit-search"):
        assert credit in text, f"the deviations do not credit {credit}"
    assert "statistical-power" not in text  # its items left with the power analysis
    assert "sphericity" not in text
    missing = _cited_ids(text) - set(_checklist_items())
    assert not missing, (
        f"the checklist cites items that do not exist: {sorted(missing)}"
    )


# --------------------------------------------------------------------------
# The skills we wrote: citations resolve, paths resolve, contracts hold
# --------------------------------------------------------------------------

PLUGIN_ROOT_PATH = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)")


def _skill_text(name: str) -> str:
    return (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", ["design", "review"])
def test_every_item_the_skill_cites_exists(name):
    missing = _cited_ids(_skill_text(name)) - set(_checklist_items())
    assert not missing, f"{name} cites items that do not exist: {sorted(missing)}"


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda p: p.name)
def test_every_plugin_root_path_a_skill_names_exists(skill_dir):
    """`${CLAUDE_PLUGIN_ROOT}/<path>` in skill text must resolve inside the
    plugin folder; the Codex fallback moves files, and this is what keeps the
    skill text honest when it does."""
    if skill_dir.name == "the-ethics-board":
        pytest.skip("vendored upstream text; it names no plugin path")
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    named = {m.group(1).rstrip(".,;:)") for m in PLUGIN_ROOT_PATH.finditer(text)}
    assert named, f"{skill_dir.name} names no plugin path (did the path shape change?)"
    missing = sorted(p for p in named if not (PLUGIN / p).exists())
    assert not missing, f"{skill_dir.name} names paths that do not exist: {missing}"


def test_lit_search_names_every_environment_name_and_key_file_the_scripts_read():
    """A file read from the user's home directory is a fact the user should
    know from the skill text, not discover from a script."""
    text = _skill_text("lit-search")
    for name in sorted(_names_the_scripts_read_from_the_environment()):
        assert name in text, f"lit-search does not name {name}, which a script reads"
    assert "api-keys.env" in text
    assert "~/.config/thesis-proposal/api-keys.env" in text


def test_lit_search_checks_python_names_the_indexes_the_target_and_writes_nothing():
    text = _skill_text("lit-search")
    assert "3.11" in text
    assert "${CLAUDE_PLUGIN_ROOT}/skills/lit-search/scripts/search.py" in text
    assert "${CLAUDE_PLUGIN_ROOT}/skills/lit-search/scripts/snowball.py" in text
    assert "writes nothing" in text
    assert "adds no kept source" in text  # the stop rule
    assert "the claim it" in text  # keep a source only with a named claim
    assert "item 5.2" in text
    assert "15 to 20" in text
    assert "which indexes will answer" in text
    assert "no Semantic Scholar key" in text
    # search.py's stderr hint names the section; a re-vendor that renames it fails here.
    source = (PLUGIN / "skills" / "lit-search" / "scripts" / "search.py").read_text(
        encoding="utf-8"
    )
    heading = re.search(r'see "([^"]+)"', source)
    assert heading is not None
    assert f"## {heading.group(1)}" in text
    for index in (
        "Crossref",
        "OpenAlex",
        "DBLP",
        "arXiv",
        "Semantic Scholar",
        "OpenCitations",
    ):
        assert index in text
    assert text.count("Done when") >= 4


def test_readme_states_the_lens_the_mechanics_the_prerequisites_and_the_vendored_facts():
    text = (PLUGIN / "README.md").read_text(encoding="utf-8")
    assert "claude plugin marketplace add eranroseman/research-vault" in text
    assert "claude plugin install experiment-proposal@research-vault" in text
    for command in ("design", "review", "lit-search", "the-ethics-board"):
        assert f"/experiment-proposal:{command}" in text, (
            f"README lacks the {command} command"
        )
    for mechanic in (
        "2,000 to 4,000",
        "15 to 20",
        "under the supervision of",
        "Research questions or Hypotheses",
    ):
        assert mechanic in text, f"README lacks the mechanic {mechanic}"
    for prerequisite in ("git", "3.11", "research-grill"):
        assert prerequisite in text, f"README lacks the prerequisite {prerequisite}"
    # Observed 2026-10-14: the-ethics-board wrote proposal/ethics-review.md in the author's
    # own project during the 0.1.0 real-material session (method: the file's listing and date).
    assert "proposal/ethics-review.md" in text
    assert "Semantic Scholar key" in text
    assert "THESIS_PROPOSAL_KEYS" in text
    assert "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" in text
    assert "CITATION.cff" in text
    assert "scientific-agents" in text
    assert "pm-claude-skills" in text
    assert "THIRD-PARTY-NOTICES.md" in text
    assert "plugin.json" in text
    assert "0.1.0" not in text
    assert "0.2.0" not in text
    lowered = text.lower()
    assert "rscript" not in lowered
    assert "simr" not in lowered
    assert "power" not in lowered


def test_the_reference_examples_carry_the_manifest_version():
    manifest = PLUGIN / ".claude-plugin" / "plugin.json"
    version = json.loads(manifest.read_text(encoding="utf-8"))["version"]
    for name in ("brief.md", "review.md"):
        text = (PLUGIN / "references" / name).read_text(encoding="utf-8")
        assert f"Checklist: experiment-proposal {version}" in text, (
            f"{name} carries a stale version"
        )


# --------------------------------------------------------------------------
# Word budgets and the shapes the skills share with the checker
# --------------------------------------------------------------------------


def _words(path: Path) -> int:
    """The pinned word count: tokens after the closing frontmatter fence."""
    text = path.read_text(encoding="utf-8")
    body = text.split("\n---\n", 1)[1] if text.startswith("---\n") else text
    return len(body.split())


WORD_BUDGETS = {
    "skills/design/SKILL.md": 1400,
    "skills/review/SKILL.md": 1100,
    "skills/lit-search/SKILL.md": 650,
    "references/brief.md": 700,
    "references/review.md": 800,
}


@pytest.mark.parametrize("relative", sorted(WORD_BUDGETS))
def test_the_file_is_within_its_word_budget(relative):
    """Sprawl shows up red; the numbers are the spec's and move by a spec edit."""
    assert _words(PLUGIN / relative) <= WORD_BUDGETS[relative]


def test_the_status_words_agree_between_the_brief_shape_and_the_checker():
    reference = (PLUGIN / "references" / "brief.md").read_text(encoding="utf-8")
    for status in _checker.STATUSES:
        assert f"`{status}`" in reference, f"brief.md does not define `{status}`"
    assert "`weak`" in reference
    assert "`missing`" in reference
    for label in _checker.ENTRY_LINES:
        assert f"- {label}:" in reference


def test_design_is_steps_that_point_at_the_shape_the_checker_and_the_subagent():
    text = _skill_text("design")
    for pointer in (
        "${CLAUDE_PLUGIN_ROOT}/references/checklist.md",
        "${CLAUDE_PLUGIN_ROOT}/references/brief.md",
        "${CLAUDE_PLUGIN_ROOT}/scripts/check_proposal.py",
        "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json",
        "../../references/checklist.md",
        "../../references/brief.md",
        "../../scripts/check_proposal.py",
        "../../.claude-plugin/plugin.json",
    ):
        assert pointer in text, f"design does not point at {pointer}"
    assert "Write only `proposal/design-brief.md`" in text
    assert "Steps 4 and 5 run inside these rounds" in text
    assert "experiment-proposal:hci-researcher" in text
    assert "Why this matters:" in text
    assert "Recommended:" in text
    assert "frontier" in text
    assert "Freeze the design brief" in text
    assert text.count("Done when") >= 8
    lowered = text.lower()
    assert "power" not in lowered
    assert "rscript" not in lowered
    assert "blocked" not in lowered
    for status in ("settled", "pilot settles", "provisional", "weak", "missing"):
        assert status in text


def test_the_subagent_runs_nothing():
    """The third marked edit: a tools line without Bash, and a routing
    sentence that names only the questions design still asks."""
    raw = "\n".join(_raw_frontmatter_lines(PLUGIN / "agents" / "hci-researcher.md"))
    assert _frontmatter(PLUGIN / "agents" / "hci-researcher.md")["tools"] == (
        "Read, Grep, Glob"
    )
    assert "# local edit (experiment-proposal): tools restricted" in raw
    # the text before "Not for unprompted use." is ours; the upstream text follows
    routing = raw.split("Not for unprompted use.", 1)[0]
    assert "random-effects" not in routing
    assert "effect-size" not in routing
    assert "counterbalancing" in routing
    assert "confounds" in routing
    header = (PLUGIN / "agents" / "hci-researcher.md").read_text(encoding="utf-8")
    assert "a tools line" in header


def test_review_is_steps_that_run_the_checker_and_keep_the_evidence_rule():
    text = _skill_text("review")
    for pointer in (
        "${CLAUDE_PLUGIN_ROOT}/references/checklist.md",
        "${CLAUDE_PLUGIN_ROOT}/references/review.md",
        "${CLAUDE_PLUGIN_ROOT}/scripts/check_proposal.py",
        "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json",
        "../../references/review.md",
        "../../.claude-plugin/plugin.json",
    ):
        assert pointer in text, f"review does not point at {pointer}"
    assert "run /experiment-proposal:design first" in text
    assert "not frozen" in text
    assert "no quote, no pass" in text.lower()
    assert "confirmed by the user" in text
    assert "(fix N applied)" in text
    assert "Which fixes" in text
    assert "check_proposal.py draft <draft>" in text
    assert "review proposal/review.md" in text
    assert '--supervisor "<name>"' in text
    for note in (
        "sections to item 3.2",
        "words to item 13.5",
        "references to item 5.1",
        "the bullet list to item 4.3",
        "the supervision sentence to item 12.3",
    ):
        assert note in text, f"review does not map {note}"
    assert "/oss:research-grill defend" in text
    assert "~/.claude/plugins/installed_plugins.json" in text
    assert "claude plugin marketplace add scdenney/open-science-skills" in text
    assert "claude plugin install oss@open-science-skills" in text
    assert "could someone run a session from the Method alone?" in text
    assert "declares no dependency" in text
    assert text.count("Done when") >= 7
    lowered = text.lower()
    assert "power" not in lowered
    assert "blocked" not in lowered


def test_review_names_the_attested_items_and_the_defaults():
    text = _skill_text("review")
    ordered = sorted(ATTESTED, key=lambda i: tuple(int(p) for p in i.split(".")))
    assert f"items {', '.join(ordered[:-1])} and {ordered[-1]}" in text
    assert "items 13.2 and 13.3" in text
    for default in (
        "2,000 to 4,000",
        "15 to 20",
        "ACM reference format",
        "Research questions or Hypotheses",
    ):
        assert default in text, f"review does not state the default {default}"


def test_the_result_words_and_counts_agree_between_the_review_shape_and_the_checker():
    reference = (PLUGIN / "references" / "review.md").read_text(encoding="utf-8")
    for result in ("pass", "pass narrowly", "fail", "fail (waived)", "not checked"):
        assert f"`{result}`" in reference, f"review.md does not define `{result}`"
    for label in _checker.SUMMARY_LABELS:
        assert label in reference
    assert _checker.DEFEND in reference
    for command in _checker.INSTALL:
        assert command in reference
