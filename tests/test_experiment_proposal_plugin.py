"""Plugin-scoped checks for ``plugins/experiment-proposal``.

Spec: ``docs/superpowers/specs/2026-10-13-experiment-proposal-plugin-design.md``,
section Tests. The plugin is a second plugin in this repository's marketplace
and shares no code with ``research_vault``; the repository's skill tests glob
only the root ``skills/``, so this module carries the plugin's own contract:
manifests, skill frontmatter and Codex metadata, provenance headers, licence
notices, the checklist's grammar and graph, the citations the skills make, the
paths they name, the vendored scripts and the R template.
"""

import ast
import json
import re
import shutil
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
ITEM = re.compile(
    r"^- \*\*(\d{1,2}\.\d{1,2})\*\* "
    r"\((draft-checked|attested|defend-stage); (design-tree|review-only); "
    r"depends on ([^)]+)\) (.+)$"
)
CITATION = re.compile(r"\bitems? (\d{1,2}\.\d{1,2}(?:(?:, | and )\d{1,2}\.\d{1,2})*)")
# The spec's design tree, by step: 1 question, ethics route, data plan; 2 session
# estimate, pilot, timeline, challenges; 6 direction, SESOI with equivalence,
# decision rule; 7 variables, within/between, carry-over, assignment,
# counterbalancing, controls, confounds; 8 eligibility, justified count;
# 11 the mixed-model plan.
DESIGN_TREE = {
    "1.1", "1.2", "1.3",
    "2.2", "2.3", "2.4", "2.5",
    "6.1", "6.2", "6.5", "6.6", "6.7",
    "7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "7.8", "7.9",
    "8.3", "8.5", "8.6", "8.7",
    "11.2", "11.4", "11.5", "11.6", "11.7", "11.8", "11.9",
}  # fmt: skip
ATTESTED = {"3.1", "5.2", "11.10", "13.1", "13.4"}
DEFEND_STAGE = {"13.2", "13.3"}


def _checklist_items() -> dict[str, dict]:
    """Every item line under a `## Step` heading, parsed by the pinned grammar;
    a bullet under a step heading that does not fit the grammar is a defect."""
    items: dict[str, dict] = {}
    in_steps = False
    for number, line in enumerate(
        CHECKLIST.read_text(encoding="utf-8").splitlines(), 1
    ):
        if line.startswith("## "):
            in_steps = line.startswith("## Step ")
            continue
        if not in_steps or not line.startswith("- "):
            continue
        match = ITEM.match(line)
        assert match, f"checklist.md:{number}: not an item line: {line[:90]}"
        item_id, kind, scope, depends, text = match.groups()
        assert item_id not in items, f"checklist.md:{number}: duplicate item {item_id}"
        deps = [] if depends == "none" else [d.strip() for d in depends.split(",")]
        items[item_id] = {
            "kind": kind,
            "scope": scope,
            "depends": deps,
            "text": text,
            "line": number,
        }
    return items


def _cited_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for match in CITATION.finditer(text):
        ids.update(re.findall(r"\d{1,2}\.\d{1,2}", match.group(1)))
    return ids


def test_checklist_has_the_items_of_all_thirteen_steps():
    items = _checklist_items()
    assert len(items) == 81, len(items)
    assert {int(i.split(".")[0]) for i in items} == set(range(1, 14))
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
    assert "BLOCKED" in items["8.5"]["text"]
    assert "waiver" in items["8.5"]["text"]


def test_checklist_names_its_provenance_deviations_and_credits():
    text = CHECKLIST.read_text(encoding="utf-8")
    assert "98b978fb74b7480c9967ceb2a1100e4560081af5" in text
    assert "## Deviations" in text
    for credit in (
        "statistical-power",
        "proposal-supervise",
        "research-grill",
        "lit-search",
    ):
        assert credit in text, f"the deviations do not credit {credit}"
    assert "sphericity" in text  # the dropped check is named, so a reader knows why
    missing = _cited_ids(text) - set(_checklist_items())
    assert not missing, (
        f"the checklist cites items that do not exist: {sorted(missing)}"
    )


# --------------------------------------------------------------------------
# The R power template
# --------------------------------------------------------------------------

TEMPLATE = PLUGIN / "templates" / "power-simr.R"


def test_the_power_template_has_the_block_design_fills_and_names_its_prerequisites():
    text = TEMPLATE.read_text(encoding="utf-8")
    start = text.index("## ---- PARAMETERS (filled by design from the brief) ----")
    end = text.index("## ---- END OF PARAMETERS ----")
    assert start < end
    block = text[start:end]
    for field in (
        "n_sims",
        "alpha",
        "target_power",
        "n_grid",
        "trials_per_condition",
        "within",
        "between",
        "models",
    ):
        assert f"{field} =" in block, f"the PARAMETERS block lacks {field}"
    for package in ("lme4", "lmerTest", "ordinal", "simr"):
        assert f"library({package})" in text
    for family in ('"lmer"', '"glmer"', '"clmm"'):
        assert family in text
    assert "powerCurve" in text
    assert "clmm(" in text


def test_the_power_template_parses_where_rscript_exists():
    """Where Rscript is absent the test SKIPS and says so; it never passes
    on a machine that could not parse the file."""
    rscript = shutil.which("Rscript")
    if rscript is None:
        pytest.skip(
            "Rscript is not on PATH: the R template was NOT parsed (skipped, not passed)"
        )
    result = subprocess.run(
        [rscript, "-e", f"invisible(parse(file = '{TEMPLATE.as_posix()}'))"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


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


def test_design_reads_the_checklist_and_the_template_and_calls_the_subagent():
    text = _skill_text("design")
    assert "${CLAUDE_PLUGIN_ROOT}/references/checklist.md" in text
    assert "${CLAUDE_PLUGIN_ROOT}/templates/power-simr.R" in text
    assert "../../references/checklist.md" in text  # the unexpanded-variable fallback
    assert "hci-researcher" in text
    assert "experiment-proposal:hci-researcher" in text
    assert "Never read the guide" in text


def test_design_checks_r_prerequisites_and_blocks_the_count_loudly():
    text = _skill_text("design")
    assert 'Rscript -e \'for (p in c("lme4","lmerTest","ordinal","simr"))' in text
    assert 'install.packages(c("lme4","lmerTest","ordinal","simr")' in text
    assert "BLOCKED" in text
    assert "waived" in text
    assert "waiver" in text
    assert "item 8.5" in text
    for status in ("settled", "pilot settles", "provisional", "weak", "missing"):
        assert status in text, f"design never names the status {status}"


def test_design_runs_rounds_with_the_three_question_parts_and_freezes_by_commit():
    text = _skill_text("design")
    assert "Why this matters:" in text
    assert "Recommended:" in text
    assert "frontier" in text
    assert "Matt Pocock" in text
    assert "## Decisions" in text
    assert "## Looked up" in text
    assert "## Open items" in text
    assert "## Amendments" in text
    assert "Draft:" in text
    assert "git commit" in text
    assert "/experiment-proposal:lit-search" in text
    assert "/experiment-proposal:the-ethics-board" in text


def test_review_reads_the_brief_the_draft_and_the_checklist_and_stops_on_a_missing_one():
    text = _skill_text("review")
    assert "${CLAUDE_PLUGIN_ROOT}/references/checklist.md" in text
    assert "../../references/checklist.md" in text
    assert "proposal/design-brief.md" in text
    assert "Draft:" in text
    assert "proposal/review.md" in text
    assert "stop and say which" in text
    assert "run /experiment-proposal:design first" in text


def test_review_passes_only_with_evidence_checks_the_four_dimensions_and_applies_picked_fixes():
    text = _skill_text("review")
    assert "No quote, no pass" in text
    assert "confirmed by the user" in text
    assert "defend-stage" in text
    assert "items 13.2 and 13.3" in text
    assert "BLOCKED" in text
    assert "waiver" in text
    assert "Cross-section consistency" in text
    assert "Brief against draft" in text
    assert "## Amendments" in text
    for test in (
        "Delta",
        "Falsifiability",
        "Swap",
        "Necessity",
        "Method fit",
        "Executability",
    ):
        assert test in text, f"review never names the {test} test"
    assert "pass narrowly" in text
    assert "fix 1" in text
    assert "Which fixes" in text
    assert "## Summary" in text
    assert "## Waivers" in text


def test_review_hands_off_to_research_grill_or_prints_its_install_commands():
    text = _skill_text("review")
    assert "/oss:research-grill defend" in text
    assert "claude plugin marketplace add scdenney/open-science-skills" in text
    assert "claude plugin install oss@open-science-skills" in text
    assert "seed list" in text
    assert "could someone run a session from the Method alone?" in text
    assert "declares no dependency" in text
    assert "~/.claude/plugins/installed_plugins.json" in text


def test_lit_search_names_every_environment_name_and_key_file_the_scripts_read():
    """A file read from the user's home directory is a fact the user should
    know from the skill text, not discover from a script."""
    text = _skill_text("lit-search")
    for name in sorted(_names_the_scripts_read_from_the_environment()):
        assert name in text, f"lit-search does not name {name}, which a script reads"
    assert "api-keys.env" in text
    assert "~/.config/thesis-proposal/api-keys.env" in text


def test_lit_search_checks_python_runs_both_entry_points_and_writes_nothing():
    text = _skill_text("lit-search")
    assert "3.11" in text
    assert "${CLAUDE_PLUGIN_ROOT}/skills/lit-search/scripts/search.py" in text
    assert "${CLAUDE_PLUGIN_ROOT}/skills/lit-search/scripts/snowball.py" in text
    assert "writes nothing" in text or "Write no files" in text
    assert "adds no kept source" in text  # the stop rule
    assert "the claim it" in text  # keep a source only with a named claim
    assert "item 5.2" in text
    for index in (
        "Crossref",
        "OpenAlex",
        "DBLP",
        "arXiv",
        "Semantic Scholar",
        "OpenCitations",
    ):
        assert index in text


def test_readme_covers_install_commands_prerequisites_and_citation_requests():
    text = (PLUGIN / "README.md").read_text(encoding="utf-8")
    assert "claude plugin marketplace add eranroseman/research-vault" in text
    assert "claude plugin install experiment-proposal@research-vault" in text
    for command in ("design", "review", "lit-search", "the-ethics-board"):
        assert f"/experiment-proposal:{command}" in text, (
            f"README lacks the {command} command"
        )
    for prerequisite in (
        "Rscript",
        "lme4",
        "lmerTest",
        "ordinal",
        "simr",
        "3.11",
        "research-grill",
    ):
        assert prerequisite in text, f"README lacks the prerequisite {prerequisite}"
    assert "CITATION.cff" in text
    assert "scientific-agents" in text
    assert "pm-claude-skills" in text
    assert "THIRD-PARTY-NOTICES.md" in text
