"""The checker is the single source of truth for the brief's, the review's and
the draft's shapes (spec v2, The checker). These tests load the checker as a
module, build one valid document per shape from the checklist itself, and
mutate it into each defect the checker must name."""

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "experiment-proposal"
CHECKER = PLUGIN / "scripts" / "check_proposal.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_proposal", CHECKER)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # a dataclass resolves its module through sys.modules while the class is built
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = _load()
ITEMS = checker.read_checklist()
DESIGN_TREE = sorted(
    (i for i, it in ITEMS.items() if it.scope == "design-tree"), key=checker.item_key
)


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def mutate(text: str, old: str, new: str) -> str:
    assert text.count(old) >= 1, f"mutation target not found: {old!r}"
    return text.replace(old, new, 1)


def valid_brief(status: str = "frozen 2026-10-20") -> str:
    entries = [
        f"### {item_id} A title\n"
        "- Decision: a decision.\n"
        '- Rationale: "the user\'s words"\n'
        "- Would change if: something changed.\n"
        "- Status: settled\n"
        "- Source: user, round 1\n"
        for item_id in DESIGN_TREE
    ]
    return (
        "# Design brief: a test\n\n"
        "Draft: proposal/draft.md\n"
        f"Status: {status}\n"
        "Checklist: experiment-proposal 0.2.0\n\n"
        "## Decisions\n\n" + "\n".join(entries) + "\n"
        "## Looked up\n\n- a fact: a value (a source, 2026-10-20)\n\n"
        "## Open items\n\n1. Run `/experiment-proposal:lit-search` for the gap\n"
    )


# --------------------------------------------------------------------------
# The checklist parser and the CLI
# --------------------------------------------------------------------------


def test_the_checker_reads_the_shipped_checklist():
    assert len(ITEMS) == 67
    assert len(DESIGN_TREE) == 21
    assert ITEMS["8.5"].scope == "design-tree"
    assert ITEMS["13.2"].kind == "defend-stage"


def test_an_unreadable_file_exits_2(tmp_path):
    result = run("brief", str(tmp_path / "missing.md"))
    assert result.returncode == 2
    assert "cannot read" in result.stderr


def test_json_output_lists_defects(tmp_path):
    path = tmp_path / "brief.md"
    path.write_text(
        mutate(valid_brief(), "Draft: proposal/draft.md\n", ""), encoding="utf-8"
    )
    result = run("--json", "brief", str(path))
    assert result.returncode == 1
    defects = json.loads(result.stdout)
    assert defects[0]["message"] == "header: no `Draft: <path>` line"


def test_a_duplicated_checklist_item_exits_2(tmp_path):
    """The checker reads the checklist beside itself; a repeated item ID is a
    defect of that file, reported as unreadable (exit 2) with the file named."""
    scripts = tmp_path / "scripts"
    references = tmp_path / "references"
    scripts.mkdir()
    references.mkdir()
    script = scripts / "check_proposal.py"
    shutil.copy(CHECKER, script)
    lines = (PLUGIN / "references" / "checklist.md").read_text(encoding="utf-8")
    lines = lines.splitlines(keepends=True)
    first = next(i for i, line in enumerate(lines) if line.startswith("- **1.1** ("))
    lines.insert(first + 1, lines[first])
    (references / "checklist.md").write_text("".join(lines), encoding="utf-8")
    brief = tmp_path / "brief.md"
    brief.write_text(valid_brief(), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(script), "brief", str(brief)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2, result.stdout
    assert "duplicate item" in result.stderr
    assert "checklist.md" in result.stderr


# --------------------------------------------------------------------------
# brief
# --------------------------------------------------------------------------


def test_a_valid_frozen_brief_is_clean(tmp_path):
    path = tmp_path / "brief.md"
    path.write_text(valid_brief(), encoding="utf-8")
    result = run("brief", str(path))
    assert result.returncode == 0, result.stdout
    assert result.stdout == ""


def test_an_open_brief_may_lack_entries(tmp_path):
    text = valid_brief(status="open")
    start = text.index("### 8.5")
    end = text.index("## Looked up")
    text = text[:start] + text[end:]
    path = tmp_path / "brief.md"
    path.write_text(text, encoding="utf-8")
    assert run("brief", str(path)).returncode == 0


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        (
            "Status: frozen 2026-10-20\n",
            "Status: done\n",
            "no `Status: open` or `Status: frozen YYYY-MM-DD` line",
        ),
        (
            "Checklist: experiment-proposal 0.2.0\n",
            "Checklist: 0.2.0\n",
            "no `Checklist: experiment-proposal <version>` line",
        ),
        (
            "- Status: settled\n",
            "- Status: done\n",
            "Status must be settled, pilot settles or provisional",
        ),
        (
            "- Would change if: something changed.\n",
            "",
            "lines must be exactly - Decision:, - Rationale:, - Would change if:, - Status:, - Source:",
        ),
        (
            "- Decision: a decision.\n",
            "- Decision: " + "x" * 400 + "\n",
            "Decision line is 412 characters; at most 400",
        ),
        (
            "## Looked up",
            "## Notes\n\n## Looked up",
            "section `## Notes` is not one of",
        ),
        ("### 1.1 A title", "### 11.1 A title", "entry 11.1 is not a design-tree item"),
    ],
)
def test_brief_defects_are_named(tmp_path, old, new, message):
    path = tmp_path / "brief.md"
    path.write_text(mutate(valid_brief(), old, new), encoding="utf-8")
    result = run("brief", str(path))
    assert result.returncode == 1
    assert message in result.stdout, result.stdout


def test_a_frozen_brief_names_every_design_tree_item(tmp_path):
    text = valid_brief()
    start = text.index("### 8.5")
    end = text.index("## Looked up")
    path = tmp_path / "brief.md"
    path.write_text(text[:start] + text[end:], encoding="utf-8")
    result = run("brief", str(path))
    assert "frozen brief has no entry for design-tree item 8.5" in result.stdout


def test_a_provisional_entry_must_be_listed_under_open_items(tmp_path):
    text = mutate(valid_brief(), "- Status: settled\n", "- Status: provisional\n")
    path = tmp_path / "brief.md"
    path.write_text(text, encoding="utf-8")
    result = run("brief", str(path))
    assert "entry 1.1 is provisional but not listed under Open items" in result.stdout
    listed = mutate(
        text,
        "## Open items\n\n",
        "## Open items\n\n1. Item 1.1 provisional, recommendation: the one-sentence question.\n",
    )
    path.write_text(listed, encoding="utf-8")
    assert run("brief", str(path)).returncode == 0
    reordered = mutate(
        text,
        "## Open items\n\n1. Run `/experiment-proposal:lit-search` for the gap\n",
        "## Open items\n\n1. Run `/experiment-proposal:lit-search` for the gap\n"
        "2. Item 1.1 provisional, recommendation: the one-sentence question.\n",
    )
    path.write_text(reordered, encoding="utf-8")
    assert (
        "provisional items come before the commands" in run("brief", str(path)).stdout
    )


def test_amendments_have_the_pinned_shape(tmp_path):
    good = valid_brief() + (
        "\n## Amendments\n\n### 2026-11-02, item 7.1, device between subjects\n"
        '- New decision: between subjects.\n- Reason: "habits transfer one way"\n'
        "- Replaces: the 7.1 entry under Decisions\n"
    )
    path = tmp_path / "brief.md"
    path.write_text(good, encoding="utf-8")
    assert run("brief", str(path)).returncode == 0
    path.write_text(
        mutate(
            good,
            "### 2026-11-02, item 7.1, device between subjects",
            "### Amendment one",
        ),
        encoding="utf-8",
    )
    assert (
        "amendment heading must be `### YYYY-MM-DD, item <ID>, <title>`"
        in run("brief", str(path)).stdout
    )
    path.write_text(
        mutate(good, '- Reason: "habits transfer one way"\n', ""), encoding="utf-8"
    )
    assert (
        "lines must be exactly - New decision:, - Reason:, - Replaces:"
        in run("brief", str(path)).stdout
    )


def test_mdformat_escapes_do_not_break_the_brief(tmp_path):
    """mdformat writes `\\_` and `\\*` into prose; the checker reads through them."""
    text = mutate(
        valid_brief(),
        "- Decision: a decision.",
        "- Decision: a decision about the n\\_grid and 2 \\* 3 cells.",
    )
    path = tmp_path / "brief.md"
    path.write_text(text, encoding="utf-8")
    assert run("brief", str(path)).returncode == 0
