"""The checker is the single source of truth for the brief's, the review's and
the draft's shapes (spec v2, The checker). These tests load the checker as a
module, build one valid document per shape from the checklist itself, and
mutate it into each defect the checker must name."""

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import textwrap
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


def test_the_usage_text_names_every_exit_2_cause():
    out = " ".join(run("--help").stdout.split())
    assert (
        "Exit 2: a file could not be read, the arguments were malformed, "
        "or the interpreter is older than 3.11." in out
    )


def test_json_output_lists_defects(tmp_path):
    path = tmp_path / "brief.md"
    path.write_text(
        mutate(valid_brief(), "Draft: proposal/draft.md\n", ""), encoding="utf-8"
    )
    result = run("--json", "brief", str(path))
    assert result.returncode == 1
    defects = json.loads(result.stdout)
    assert defects[0]["message"] == "header: no `Draft: <path>` line"


SUFFIX = re.compile(r" \[(?P<rule>[a-z]+(?:-[a-z]+)*); item (?P<item>[0-9.]+|none)\]$")


def message_of(line: str) -> str:
    """The text of a defect line between the location and the rule suffix."""
    return SUFFIX.sub("", line.split(": ", 1)[1])


def test_every_defect_carries_a_rule_and_an_item(tmp_path):
    """Text lines end ` [<rule>; item <ID or none>]`; JSON carries the two keys,
    `item` null for a shape defect no item owns and the entry's ID for an
    entry defect. The JSON message stays bare so the skills can quote it."""
    text = mutate(valid_brief(), "Draft: proposal/draft.md\n", "")
    text = mutate(text, "- Status: settled\n", "- Status: done\n")
    path = tmp_path / "brief.md"
    path.write_text(text, encoding="utf-8")
    lines = run("brief", str(path)).stdout.splitlines()
    assert lines[0].endswith(" [header-draft; item none]"), lines[0]
    assert any(line.endswith(" [entry-status; item 1.1]") for line in lines), lines
    defects = json.loads(run("--json", "brief", str(path)).stdout)
    for defect in defects:
        assert set(defect) == {"path", "line", "message", "rule", "item"}
        assert re.fullmatch(r"[a-z]+(?:-[a-z]+)*", defect["rule"]), defect
        assert not SUFFIX.search(defect["message"])
    assert defects[0]["rule"] == "header-draft"
    assert defects[0]["item"] is None
    status = next(d for d in defects if d["rule"] == "entry-status")
    assert status["item"] == "1.1"


def test_draft_defects_name_the_owning_item(tmp_path):
    path = tmp_path / "draft.md"
    path.write_text(valid_draft(reference_count=14), encoding="utf-8")
    out = run("draft", str(path)).stdout
    assert "[references-count; item 5.1]" in out
    path.write_text(
        mutate(valid_draft(), "- an estimate;\n- a test;\n- a program.\n", "none.\n"),
        encoding="utf-8",
    )
    assert "[contributions; item 4.3]" in run("draft", str(path)).stdout


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
        (
            '- Rationale: "the user\'s words"\n',
            "- Rationale:\n",
            "entry 1.1: Rationale is empty",
        ),
    ],
)
def test_brief_defects_are_named(tmp_path, old, new, message):
    path = tmp_path / "brief.md"
    path.write_text(mutate(valid_brief(), old, new), encoding="utf-8")
    result = run("brief", str(path))
    assert result.returncode == 1
    assert message in result.stdout, result.stdout


def test_entries_are_in_checklist_order(tmp_path):
    text = valid_brief()
    first = text.index("### 1.1 A title")
    second = text.index("### 1.2 A title")
    third = text.index("### 1.3 A title")
    swapped = text[:first] + text[second:third] + text[first:second] + text[third:]
    path = tmp_path / "brief.md"
    path.write_text(swapped, encoding="utf-8")
    assert "entries are not in checklist order" in run("brief", str(path)).stdout


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


def _brief_under(version: str, status: str = "frozen 2026-10-10") -> str:
    """A brief under `version` that breaks every entry rule: a 500-character
    Decision, an entry for the retired item 6.7, no entry for 7.9 (a defect only
    once the brief is frozen)."""
    assert "6.7" not in ITEMS
    assert "7.9" in DESIGN_TREE
    text = mutate(
        valid_brief(status=status),
        "Checklist: experiment-proposal 0.2.0",
        f"Checklist: experiment-proposal {version}",
    )
    text = mutate(text, "- Decision: a decision.", "- Decision: " + "x" * 488)
    return mutate(text, "### 7.9 A title", "### 6.7 A title")


def test_a_brief_frozen_under_an_older_checklist_is_checked_on_header_and_amendments(
    tmp_path,
):
    path = tmp_path / "brief.md"
    path.write_text(_brief_under("0.1.0"), encoding="utf-8")
    old = run("brief", str(path))
    assert old.returncode == 0, old.stdout
    assert old.stdout == ""
    assert old.stderr == (
        f"{path}: brief frozen under checklist 0.1.0; "
        "only the header and Amendments are checked\n"
    )
    path.write_text(_brief_under("0.2.0"), encoding="utf-8")
    current = run("brief", str(path))
    assert current.returncode == 1
    assert current.stderr == ""
    for message in (
        "Decision line is 500 characters; at most 400",
        "entry 6.7 is not a design-tree item",
        "frozen brief has no entry for design-tree item 7.9",
    ):
        assert message in current.stdout, current.stdout


def test_an_open_brief_is_checked_in_full_whatever_its_version(tmp_path):
    path = tmp_path / "brief.md"
    path.write_text(_brief_under("0.1.0", status="open"), encoding="utf-8")
    result = run("brief", str(path))
    assert result.returncode == 1
    assert result.stderr == ""
    for message in (
        "Decision line is 500 characters; at most 400",
        "entry 6.7 is not a design-tree item",
    ):
        assert message in result.stdout, result.stdout


def test_an_older_brief_still_answers_for_its_header_and_amendments(tmp_path):
    amended = _brief_under("0.1.0") + (
        "\n## Amendments\n\n### Amendment one\n- New decision: between subjects.\n"
    )
    amended = mutate(amended, "Draft: proposal/draft.md\n", "")
    path = tmp_path / "brief.md"
    path.write_text(amended, encoding="utf-8")
    result = run("brief", str(path))
    assert result.returncode == 1
    assert "header: no `Draft: <path>` line" in result.stdout
    assert "amendment heading must be `### YYYY-MM-DD, item <ID>, <title>`" in (
        result.stdout
    )
    assert "brief frozen under checklist 0.1.0" in result.stderr


@pytest.mark.parametrize(
    ("version", "skipped"),
    [
        ("0.0.9", True),
        ("0.1.9", True),
        ("0.2.0", False),
        ("0.2.7", False),
        ("0.10.0", False),
        ("1.0.0", False),
    ],
)
def test_the_shape_version_compares_major_and_minor_as_numbers(
    tmp_path, version, skipped
):
    path = tmp_path / "brief.md"
    path.write_text(_brief_under(version), encoding="utf-8")
    result = run("brief", str(path))
    assert (result.returncode == 0) is skipped, result.stdout
    assert ("brief frozen under checklist" in result.stderr) is skipped


# --------------------------------------------------------------------------
# review
# --------------------------------------------------------------------------

SUBSTANCE = ("13.6", "13.7", "13.8", "13.9", "13.10", "13.11")


def _row(item_id: str) -> str:
    item = ITEMS[item_id]
    if item.kind == "defend-stage":
        return f"- **{item_id}** not checked: defend-stage"
    if item.kind == "attested":
        return f"- **{item_id}** pass: confirmed by the user, 2026-10-27"
    return f'- **{item_id}** pass: "a quoted passage" (Design, para 2)'


def valid_review() -> str:
    ordered = sorted(ITEMS, key=checker.item_key)
    items_rows = "\n".join(_row(i) for i in ordered if i not in SUBSTANCE)
    substance_rows = "\n".join(_row(i) for i in SUBSTANCE)
    return (
        "# Review: proposal/draft.md\n\n"
        "Brief: proposal/design-brief.md (frozen 2026-10-20)\n"
        "Draft: proposal/draft.md (from the brief)\n"
        "Date: 2026-10-27\n"
        "Checklist: experiment-proposal 0.2.0\n\n"
        f"## Items\n\n{items_rows}\n\n"
        "## Cross-section consistency\n\n- pass: counts, durations and variable names agree\n\n"
        "## Brief against draft\n\n- pass: no departures\n\n"
        f"## Substance tests\n\n{substance_rows}\n\n"
        "## Summary\n\nItems checked: 65. Pass: 65. Fail: 0. Not checked (defend-stage): 2. "
        "Consistency and brief findings: 0. Fixes proposed: 0. Waivers: 0.\n\n"
        "## Waivers\n\n- none\n\n"
        "## Hand-off\n\n/oss:research-grill defend proposal/draft.md\n\nSeed list: could someone run a session from the Method alone?\n"
    )


def test_a_valid_review_is_clean(tmp_path):
    path = tmp_path / "review.md"
    path.write_text(valid_review(), encoding="utf-8")
    result = run("review", str(path))
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("Date: 2026-10-27\n", "", "header: no `Date:` line"),
        (
            "## Waivers\n\n- none\n\n",
            "",
            "sections must be Items, Cross-section consistency, Brief against draft, Substance tests, Summary, Waivers, Hand-off",
        ),
        (
            '- **1.1** pass: "a quoted passage" (Design, para 2)',
            "- **1.1** pass: it is there",
            "row 1.1 passes without a quoted passage and its location",
        ),
        (
            "- **3.1** pass: confirmed by the user, 2026-10-27",
            "- **3.1** pass: the user said so",
            "row 3.1 passes without `confirmed by the user, <date>`",
        ),
        (
            "- **13.2** not checked: defend-stage",
            '- **13.2** pass: "x" (y)',
            "row 13.2 is a defend-stage item and must read `not checked`",
        ),
        (
            '- **1.1** pass: "a quoted passage" (Design, para 2)',
            "- **1.1** not checked: skipped",
            "row 1.1 reads `not checked`; only items 13.2 and 13.3 may",
        ),
        (
            '- **1.1** pass: "a quoted passage" (Design, para 2)',
            '- **1.1** passed: "a" (b)',
            "row does not fit",
        ),
        (
            "/oss:research-grill defend proposal/draft.md",
            "run the defend step later",
            "Hand-off: neither the defend command nor both install commands are present",
        ),
    ],
)
def test_review_defects_are_named(tmp_path, old, new, message):
    path = tmp_path / "review.md"
    path.write_text(mutate(valid_review(), old, new), encoding="utf-8")
    result = run("review", str(path))
    assert result.returncode == 1
    assert message in result.stdout, result.stdout


def test_review_rows_cover_every_item_in_order(tmp_path):
    text = valid_review()
    path = tmp_path / "review.md"
    path.write_text(
        mutate(text, '- **1.2** pass: "a quoted passage" (Design, para 2)\n', ""),
        encoding="utf-8",
    )
    assert "Items: missing rows for 1.2" in run("review", str(path)).stdout
    swapped = mutate(
        text,
        '- **1.1** pass: "a quoted passage" (Design, para 2)\n- **1.2** pass: "a quoted passage" (Design, para 2)\n',
        '- **1.2** pass: "a quoted passage" (Design, para 2)\n- **1.1** pass: "a quoted passage" (Design, para 2)\n',
    )
    path.write_text(swapped, encoding="utf-8")
    assert "Items: rows are not in checklist order" in run("review", str(path)).stdout


def test_fix_numbers_are_contiguous_and_the_summary_recomputes(tmp_path):
    text = valid_review()
    failing = mutate(
        text,
        '- **7.5** pass: "a quoted passage" (Design, para 2)',
        "- **7.5** fail: the order of the nine combinations is not stated. fix 1: add a sentence to Design.",
    )
    failing = mutate(
        failing,
        '- **10.5** pass: "a quoted passage" (Design, para 2)',
        "- **10.5** fail: nothing on illness or breakdown. fix 2: add a sentence to Procedure.",
    )
    failing = mutate(
        failing,
        "- pass: counts, durations and variable names agree",
        "- fail: participant count 24 (Participants) vs 20 (Appendix B). fix 3: change the consent form to 24.",
    )
    failing = mutate(
        failing,
        "Items checked: 65. Pass: 65. Fail: 0. Not checked (defend-stage): 2. Consistency and brief findings: 0. Fixes proposed: 0. Waivers: 0.",
        "Items checked: 65. Pass: 63. Fail: 2. Not checked (defend-stage): 2. Consistency and brief findings: 1. Fixes proposed: 3. Waivers: 0.",
    )
    path = tmp_path / "review.md"
    path.write_text(failing, encoding="utf-8")
    assert run("review", str(path)).returncode == 0, run("review", str(path)).stdout
    quoted = mutate(
        failing,
        '- **1.1** pass: "a quoted passage" (Design, para 2)',
        '- **1.1** pass: "we will fix 2 bugs before the pilot" (Design, para 2)',
    )
    path.write_text(quoted, encoding="utf-8")
    assert run("review", str(path)).returncode == 0, run("review", str(path)).stdout
    gap = mutate(failing, "fix 3: change", "fix 5: change")
    path.write_text(gap, encoding="utf-8")
    assert "fix 5 appears before fix 3" in run("review", str(path)).stdout
    wrong = mutate(failing, "Pass: 63. Fail: 2.", "Pass: 64. Fail: 1.")
    path.write_text(wrong, encoding="utf-8")
    out = run("review", str(path)).stdout
    assert "Summary: Pass says 64, the rows give 63" in out
    assert "Summary: Fail says 1, the rows give 2" in out
    applied = mutate(
        failing,
        "- **7.5** fail: the order",
        '- **7.5** pass (fix 1 applied): "The nine combinations will be presented in a random order" (Design, para 3). Was: the order',
    )
    applied = mutate(applied, "Pass: 63. Fail: 2.", "Pass: 64. Fail: 1.")
    path.write_text(applied, encoding="utf-8")
    assert run("review", str(path)).returncode == 0, run("review", str(path)).stdout


def test_a_group_of_waivers_counts_its_entries(tmp_path):
    text = mutate(
        valid_review(),
        '- **9.3** pass: "a quoted passage" (Design, para 2)',
        "- **9.3** fail (waived): no logging statement. fix 1: add one.",
    )
    text = mutate(
        text,
        "## Waivers\n\n- none\n",
        '## Waivers\n\n- 9.3 waived, reason: "the program is bought, not written" (2026-10-27)\n',
    )
    text = mutate(
        text,
        "Items checked: 65. Pass: 65. Fail: 0. Not checked (defend-stage): 2. Consistency and brief findings: 0. Fixes proposed: 0. Waivers: 0.",
        "Items checked: 65. Pass: 64. Fail: 1. Not checked (defend-stage): 2. Consistency and brief findings: 0. Fixes proposed: 1. Waivers: 1.",
    )
    path = tmp_path / "review.md"
    path.write_text(text, encoding="utf-8")
    assert run("review", str(path)).returncode == 0, run("review", str(path)).stdout
    orphan_row = mutate(
        text,
        '- 9.3 waived, reason: "the program is bought, not written" (2026-10-27)\n',
        '- 9.4 waived, reason: "x" (2026-10-27)\n',
    )
    path.write_text(orphan_row, encoding="utf-8")
    out = run("review", str(path)).stdout
    assert "row 9.3 is waived but has no Waivers entry" in out
    assert "Waivers names 9.4, whose row is not `fail (waived)`" in out
    misspelt = mutate(text, "- 9.3 waived, reason:", "- 9.3 waivedx, reason:")
    path.write_text(misspelt, encoding="utf-8")
    assert (
        "row 9.3 is waived but has no Waivers entry" in run("review", str(path)).stdout
    )


def test_a_capitalised_fix_and_fail_are_counted(tmp_path):
    text = mutate(
        valid_review(),
        "- pass: counts, durations and variable names agree",
        "- Fail: participant count 24 (Participants) vs 20 (Appendix B). Fix 1: change the consent form to 24.",
    )
    text = mutate(
        text,
        "Consistency and brief findings: 0. Fixes proposed: 0.",
        "Consistency and brief findings: 1. Fixes proposed: 1.",
    )
    path = tmp_path / "review.md"
    path.write_text(text, encoding="utf-8")
    result = run("review", str(path))
    assert result.returncode == 0, result.stdout


def test_an_applied_marker_is_not_a_fix_in_the_order_scan(tmp_path):
    """Row 1.1 re-checked reads `(fix 11 applied)`; the fixes themselves sit
    further down, so the marker precedes fix 9's first appearance."""
    findings = "\n".join(
        f"- fail: a mismatch, number {n}. fix {n}: change it." for n in range(1, 13)
    )
    text = mutate(
        valid_review(), "- pass: counts, durations and variable names agree", findings
    )
    text = mutate(
        text,
        '- **1.1** pass: "a quoted passage" (Design, para 2)',
        '- **1.1** pass (fix 11 applied): "The new sentence" (Introduction, para 1)',
    )
    text = mutate(
        text,
        "Consistency and brief findings: 0. Fixes proposed: 0.",
        "Consistency and brief findings: 12. Fixes proposed: 12.",
    )
    path = tmp_path / "review.md"
    path.write_text(text, encoding="utf-8")
    result = run("review", str(path))
    assert result.returncode == 0, result.stdout
    gap = mutate(text, "fix 4: change it.", "fix 14: change it.")
    path.write_text(gap, encoding="utf-8")
    assert "fix 14 appears before fix 4" in run("review", str(path)).stdout


def _review_with_fixes_1_and_3(*, marker: bool) -> str:
    """Fix 1 on row 7.1, fix 3 on row 10.5; row 7.5 sits between them and,
    when `marker` is set, reads `(fix 2 applied)` with no other `fix 2` text."""
    text = mutate(
        valid_review(),
        '- **7.1** pass: "a quoted passage" (Design, para 2)',
        "- **7.1** fail: nothing on the carry-over. fix 1: add a sentence to Design.",
    )
    text = mutate(
        text,
        '- **10.5** pass: "a quoted passage" (Design, para 2)',
        "- **10.5** fail: nothing on illness. fix 3: add a sentence to Procedure.",
    )
    if marker:
        text = mutate(
            text,
            '- **7.5** pass: "a quoted passage" (Design, para 2)',
            '- **7.5** pass (fix 2 applied): "The nine combinations will be presented in a random order" (Design, para 3)',
        )
    return mutate(
        text,
        "Items checked: 65. Pass: 65. Fail: 0. Not checked (defend-stage): 2. Consistency and brief findings: 0. Fixes proposed: 0.",
        "Items checked: 65. Pass: 63. Fail: 2. Not checked (defend-stage): 2. Consistency and brief findings: 0. Fixes proposed: 3.",
    )


def test_an_applied_marker_counts_its_number_without_a_definition(tmp_path):
    """(i) A correct step-6 rewrite: fix 2 was applied and its row now carries
    only the marker, while fixes 1 and 3 are still defined."""
    path = tmp_path / "review.md"
    path.write_text(_review_with_fixes_1_and_3(marker=True), encoding="utf-8")
    result = run("review", str(path))
    assert result.returncode == 0, result.stdout
    wrong = mutate(
        _review_with_fixes_1_and_3(marker=True),
        "Fixes proposed: 3.",
        "Fixes proposed: 2.",
    )
    path.write_text(wrong, encoding="utf-8")
    assert "Summary: Fixes proposed says 2, the rows give 3" in (
        run("review", str(path)).stdout
    )


def test_a_gap_with_no_marker_is_still_an_order_defect(tmp_path):
    """(iii) Fixes 1 and 3 defined, and no `fix 2` anywhere, not even a marker."""
    path = tmp_path / "review.md"
    path.write_text(_review_with_fixes_1_and_3(marker=False), encoding="utf-8")
    result = run("review", str(path))
    assert result.returncode == 1
    assert "fix 3 appears before fix 2" in result.stdout


def test_a_marker_covers_only_its_own_number(tmp_path):
    """Fixes 1 and 4 defined with a marker for 2: fix 3 is the gap named."""
    text = mutate(_review_with_fixes_1_and_3(marker=True), "fix 3: add", "fix 4: add")
    path = tmp_path / "review.md"
    path.write_text(text, encoding="utf-8")
    assert "fix 4 appears before fix 3" in run("review", str(path)).stdout


def test_the_row_pattern_accepts_every_result_word():
    for result in checker.RESULTS:
        match = checker.ROW.match(f"- **1.1** {result}: x")
        assert match is not None, result
        assert match.group(2) == result


def test_not_confirmed_is_accepted_on_attested_items_and_counts_under_fail(tmp_path):
    text = mutate(
        valid_review(),
        "- **3.1** pass: confirmed by the user, 2026-10-27",
        "- **3.1** not confirmed: earlier review.md read confirmed by the user, 2026-10-15",
    )
    text = mutate(text, "Pass: 65. Fail: 0.", "Pass: 64. Fail: 1.")
    path = tmp_path / "review.md"
    path.write_text(text, encoding="utf-8")
    result = run("review", str(path))
    assert result.returncode == 0, result.stdout
    wrong = mutate(text, "Pass: 64. Fail: 1.", "Pass: 65. Fail: 0.")
    path.write_text(wrong, encoding="utf-8")
    assert "Summary: Fail says 0, the rows give 1" in run("review", str(path)).stdout
    draft_checked = mutate(
        valid_review(),
        '- **7.5** pass: "a quoted passage" (Design, para 2)',
        "- **7.5** not confirmed: nobody asked",
    )
    path.write_text(draft_checked, encoding="utf-8")
    assert (
        "row 7.5: attested result on a draft-checked item [row-attested; item 7.5]"
        in run("review", str(path)).stdout
    )


def test_a_pass_quoted_from_a_placeholder_is_a_defect(tmp_path):
    text = mutate(
        valid_review(),
        '- **8.9** pass: "a quoted passage" (Design, para 2)',
        '- **8.9** pass: "[NO-SHOW EXTRAS] extra bookings" (Appendix A, para 2)',
    )
    path = tmp_path / "review.md"
    path.write_text(text, encoding="utf-8")
    result = run("review", str(path))
    assert result.returncode == 1
    assert (
        "row 8.9 passes on a placeholder: [NO-SHOW EXTRAS] [pass-placeholder; item 8.9]"
        in result.stdout
    )
    for quote in ('"the TODO list" (Design)', '"a TBD count" (Design)'):
        path.write_text(
            mutate(
                valid_review(),
                '- **8.9** pass: "a quoted passage" (Design, para 2)',
                f"- **8.9** pass: {quote}",
            ),
            encoding="utf-8",
        )
        assert "pass-placeholder" in run("review", str(path)).stdout
    acronym = mutate(
        valid_review(),
        '- **8.9** pass: "a quoted passage" (Design, para 2)',
        '- **8.9** pass: "the [27] source and a [Named] thing" (Design, para 2)',
    )
    path.write_text(acronym, encoding="utf-8")
    assert run("review", str(path)).returncode == 0


def test_the_checker_header_line_is_accepted_when_it_is_a_draft_option_set(tmp_path):
    text = mutate(
        valid_review(),
        "Checklist: experiment-proposal 0.2.0\n",
        'Checklist: experiment-proposal 0.2.0\nChecker: draft --words 2000-4000 --references 15-20 --supervisor "Dr. Example"\n',
    )
    path = tmp_path / "review.md"
    path.write_text(text, encoding="utf-8")
    assert run("review", str(path)).returncode == 0, run("review", str(path)).stdout
    full = mutate(
        text,
        'Checker: draft --words 2000-4000 --references 15-20 --supervisor "Dr. Example"',
        'Checker: draft --sections "Introduction, Design, Appendix" --words 2000-4000 --references 15-27 --review-section "Related work"',
    )
    path.write_text(full, encoding="utf-8")
    assert run("review", str(path)).returncode == 0, run("review", str(path)).stdout
    for bad, why in (
        (
            "Checker: draft --words 2000-4000 --references 15-20 --colour blue",
            "unknown option(s): --colour blue",
        ),
        ("Checker: review proposal/review.md", "must begin `Checker: draft`"),
        ("Checker: draft --words 2000-4000", "missing --references"),
        (
            "Checker: draft --words lots --references 15-20",
            "--words and --references take LOW-HIGH",
        ),
        (
            "Checker: draft --word 2000-4000 --references 15-20",
            "unknown option(s): --word 2000-4000",
        ),
    ):
        path.write_text(
            mutate(
                text,
                'Checker: draft --words 2000-4000 --references 15-20 --supervisor "Dr. Example"',
                bad,
            ),
            encoding="utf-8",
        )
        out = run("review", str(path)).stdout
        assert (
            f"header: Checker line is not a draft option set: {why} [checker-line; item 3.1]"
            in out
        ), out


def test_a_judged_section_is_accepted_after_items_only(tmp_path):
    text = mutate(
        valid_review(),
        "## Cross-section consistency\n",
        "## Judged\n\n- RQ1: Is target selection faster with a mouse or a trackball?\n- H1: faster with the mouse.\n\n## Cross-section consistency\n",
    )
    path = tmp_path / "review.md"
    path.write_text(text, encoding="utf-8")
    assert run("review", str(path)).returncode == 0, run("review", str(path)).stdout
    misplaced = mutate(
        valid_review(),
        "## Summary\n",
        "## Judged\n\n- RQ1.\n\n## Summary\n",
    )
    path.write_text(misplaced, encoding="utf-8")
    assert (
        "sections must be Items, Cross-section consistency, Brief against draft, Substance tests, Summary, Waivers, Hand-off, in that order (Judged, optional, after Items)"
        in run("review", str(path)).stdout
    )


# --------------------------------------------------------------------------
# draft
# --------------------------------------------------------------------------

SENTENCE = "Participants will select targets on the screen with each device in turn. "


def valid_draft(body_sentences: int = 240, reference_count: int = 16) -> str:
    """A draft with the course's sections in order, about 2,900 body words,
    sixteen references each cited in the Literature review, a bulleted
    contributions list and the supervision sentence."""
    prose = SENTENCE * (body_sentences // 7)
    references = "\n".join(
        f"- Author {n} ({2000 + n}). A paper about pointing, number {n}. A Journal."
        for n in range(reference_count)
    )
    cites = "; ".join(f"Author {n} ({2000 + n})" for n in range(reference_count))
    return (
        "# A controlled experiment\n\n"
        f"## Introduction\n\nWe ask a question. {prose}\n\nThe contributions will be:\n\n- an estimate;\n- a test;\n- a program.\n\n"
        f"## Literature review\n\n{prose} Prior work: {cites}.\n\n"
        f"## Research questions or Hypotheses\n\n- H1: faster with the mouse.\n\n{prose}\n\n"
        f"## Participants\n\n{prose}\n\n"
        f"## Materials\n\n{prose}\n\n"
        f"## Procedure\n\n{prose}\n\n"
        f"## Design\n\n{prose}\n\n"
        f"## References\n\n{references}\n\n"
        "## Appendix A: recruiting announcement\n\nCome and take part.\n\n"
        "## Appendix B: consent form\n\nThis study is run by the author under the supervision of Dr. Example as a course project. You may stop at any time.\n\n"
        "## Appendix C: session script\n\nWelcome.\n"
    )


def test_a_valid_draft_is_clean(tmp_path):
    path = tmp_path / "draft.md"
    path.write_text(valid_draft(), encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert result.returncode == 0, result.stdout


def _body_count(text: str) -> int:
    """The pinned rule applied by hand: every token on the lines before the
    References heading, minus any appendix section, a section running to the
    next heading at its own level or higher."""
    lines = text.splitlines()
    heads = [
        (number, len(m.group(1)), m.group(2))
        for number, line in enumerate(lines, 1)
        if (m := re.match(r"^(#{1,6}) (.+)$", line))
    ]
    reference_line = next(n for n, _, h in heads if h.lower().startswith("references"))
    skipped: set[int] = set()
    for index, (number, level, heading) in enumerate(heads):
        if heading.lower().startswith("append"):
            end = len(lines)
            for later_number, later_level, _ in heads[index + 1 :]:
                if later_level <= level:
                    end = later_number - 1
                    break
            skipped.update(range(number, end + 1))
    body = " ".join(
        line
        for n, line in enumerate(lines, 1)
        if n < reference_line and n not in skipped
    )
    return len(body.split())


def test_the_body_word_count_excludes_references_and_appendices(tmp_path):
    """The count is checked exactly, so removing either exclusion fails."""
    text = valid_draft()
    expected = _body_count(text)
    assert 2000 <= expected <= 4000
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    assert run("draft", str(path), "--words", f"{expected}-{expected}").returncode == 0
    assert (
        f"words: the body has {expected} words"
        in run("draft", str(path), "--words", f"{expected + 1}-4000").stdout
    )
    moved = text.replace("## Appendix C: session script\n\nWelcome.\n", "")
    moved = moved.replace(
        "## References\n",
        "## Appendix C: session script\n\n### Script\n\nWelcome.\n\n## References\n",
    )
    assert _body_count(moved) == expected
    path.write_text(moved, encoding="utf-8")
    assert run("draft", str(path), "--words", f"{expected}-{expected}").returncode == 0
    path.write_text(valid_draft(body_sentences=100), encoding="utf-8")
    assert "the template asks for 2000 to 4000" in run("draft", str(path)).stdout


def test_reference_lists_in_three_forms_count_the_same(tmp_path):
    text = valid_draft()
    path = tmp_path / "draft.md"
    numbered = re.sub(r"^- (Author)", r"1. \1", text, flags=re.MULTILINE)
    paragraphs = re.sub(r"^- (Author.*)$", r"\1\n", text, flags=re.MULTILINE)
    for variant in (text, numbered, paragraphs):
        path.write_text(variant, encoding="utf-8")
        result = run("draft", str(path), "--supervisor", "Dr. Example")
        assert result.returncode == 0, result.stdout
    path.write_text(text.replace("## References\n", "## Sources\n"), encoding="utf-8")
    assert "references: no `References` heading" in run("draft", str(path)).stdout


def test_numbered_headings_appendices_and_a_wrapped_supervision_sentence(tmp_path):
    text = valid_draft()
    for name in (
        "Introduction",
        "Literature review",
        "Research questions or Hypotheses",
        "Participants",
        "Materials",
        "Procedure",
        "Design",
    ):
        text = text.replace(f"## {name}\n", f"## 1. {name}\n", 1)
    text = text.replace(
        "## Appendix A: recruiting announcement\n",
        "## Appendices\n\n### A: recruiting announcement\n",
    )
    text = text.replace("## Appendix B: consent form\n", "### B: consent form\n")
    text = text.replace("## Appendix C: session script\n", "### C: session script\n")
    text = text.replace(
        "under the supervision of Dr. Example", "under the\nsupervision of Dr. Example"
    )
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        (
            "## Materials\n",
            "## Apparatus\n",
            "sections: `Materials` not found after `Participants`",
        ),
        (
            "- an estimate;\n- a test;\n- a program.\n",
            "an estimate, a test and a program.\n",
            "introduction: no bullet list of contributions",
        ),
        (
            "under the supervision of Dr. Example",
            "supervised by Dr. Example",
            "appendix: no consent sentence saying the study is under the supervision of the instructor",
        ),
    ],
)
def test_draft_defects_are_named(tmp_path, old, new, message):
    path = tmp_path / "draft.md"
    path.write_text(mutate(valid_draft(), old, new), encoding="utf-8")
    result = run("draft", str(path))
    assert result.returncode == 1
    assert message in result.stdout, result.stdout


def test_the_reference_count_and_the_supervisor_name(tmp_path):
    path = tmp_path / "draft.md"
    path.write_text(valid_draft(reference_count=14), encoding="utf-8")
    assert (
        "references: the Literature review cites 14 of the list's 14 entries; the template asks for 15 to 20"
        in run("draft", str(path)).stdout
    )
    path.write_text(valid_draft(), encoding="utf-8")
    out = run("draft", str(path), "--supervisor", "Dr. Someone Else").stdout
    assert "appendix: the supervision sentence names 'Dr. Example" in out
    assert "not 'Dr. Someone Else'" in out


def _numbered_draft(cited: int = 18, listed: int = 28, extra_citation: str = "") -> str:
    """An ACM-numbered draft: `[n]` entries, the Literature review citing the
    first `cited` of them as `[1]`, `[2, 3]`, `[4-6]` and single brackets."""
    text = valid_draft()
    entries = "\n".join(
        f"[{n}] Author {n}. {2000 + n}. A paper about pointing, number {n}. A Journal."
        for n in range(1, listed + 1)
    )
    start, end = (
        text.index("## References\n\n") + len("## References\n\n"),
        text.index("## Appendix A"),
    )
    text = text[:start] + entries + "\n\n" + text[end:]
    rest = ", ".join(f"[{n}]" for n in range(7, cited + 1))
    citations = f"Prior work [1] showed it [2, 3] and so did others [4–6]; see also {rest}{extra_citation}."
    return re.sub(r"Prior work: .*?\.\n", citations + "\n", text, count=1)


def test_numbered_reference_lines_count_as_entries_and_the_review_citations_are_counted(
    tmp_path,
):
    """An ACM-numbered list is 28 entries, not one; the count the template
    bounds is the Literature review's 18 distinct cited numbers, so the draft
    passes `--references 15-20` with 28 entries listed. The list total and the
    uncited entries are informational, on stderr, never in --json."""
    path = tmp_path / "draft.md"
    path.write_text(_numbered_draft(), encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert result.returncode == 0, result.stdout
    assert "references: 28 entries in the list" in result.stderr
    assert "references: entry [19] is not cited" in result.stderr
    assert "references: entry [28] is not cited" in result.stderr
    assert "entry [18] is not cited" not in result.stderr
    assert (
        json.loads(
            run("--json", "draft", str(path), "--supervisor", "Dr. Example").stdout
        )
        == []
    )
    path.write_text(_numbered_draft(cited=14), encoding="utf-8")
    out = run("draft", str(path), "--supervisor", "Dr. Example").stdout
    assert (
        "references: the Literature review cites 14 of the list's 28 entries; the template asks for 15 to 20 [references-count; item 5.1]"
        in out
    )


def test_a_numbered_entry_wrapped_onto_a_year_line_stays_one_entry(tmp_path):
    """An ACM entry whose author list fills a line wraps before its year, so
    its continuation starts `2001. `; inside a `[n]` list that line continues
    the entry, and the list stays numbered with the same total and count."""
    wrapped = _numbered_draft(cited=14).replace(
        "[1] Author 1. 2001. A paper", "[1] Author 1.\n2001. A paper", 1
    )
    assert "\n2001. A paper about pointing, number 1." in wrapped
    path = tmp_path / "draft.md"
    path.write_text(wrapped, encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert "references: 28 entries in the list" in result.stderr
    assert "without a surname and year" not in result.stderr
    assert (
        "references: the Literature review cites 14 of the list's 28 entries; the template asks for 15 to 20 [references-count; item 5.1]"
        in result.stdout
    )
    assert checker._listed_entries(
        [
            "[1] Paul M. Fitts. The information capacity of the",
            "1954. Journal.",
            "[2] B.",
        ]
    ) == ["[1] Paul M. Fitts. The information capacity of the 1954. Journal.", "[2] B."]


def test_a_citation_without_an_entry_is_a_defect_under_item_3_3(tmp_path):
    path = tmp_path / "draft.md"
    path.write_text(_numbered_draft(extra_citation=" and [29]"), encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert result.returncode == 1
    assert (
        "references: [29] is cited but has no entry in the list [citation-no-entry; item 3.3]"
        in result.stdout
    )
    defects = json.loads(
        run("--json", "draft", str(path), "--supervisor", "Dr. Example").stdout
    )
    assert [d["rule"] for d in defects] == ["citation-no-entry"]
    assert defects[0]["line"] == next(
        n
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if "[29]" in line
    )


def test_an_author_year_entry_counts_when_its_first_surname_and_year_are_cited(
    tmp_path,
):
    """`Fitts (1954)` and `Soukoreff and MacKenzie (2004)` count; an entry
    cited nowhere is informational; a surname in prose with no entry (`Zhai
    (2004)`) is not a cited-without-entry defect, since the checker cannot
    prove an author-year citation."""
    text = valid_draft(reference_count=0)
    entries = (
        "- Fitts, P. M. (1954). The information capacity of the human motor system. Journal of Experimental Psychology, 47(6), 381-391.\n"
        "- Soukoreff, R. W., and MacKenzie, I. S. (2004). Towards a standard for pointing device evaluation. IJHCS, 61(6), 751-789.\n"
        "- Card, S. K., English, W. K., and Burr, B. J. (1978). Evaluation of mouse, joystick, step keys and text keys. Ergonomics, 21(8), 601-613.\n"
    )
    text = mutate(text, "## References\n\n\n", f"## References\n\n{entries}\n")
    text = mutate(
        text,
        "Prior work: .",
        "Fitts (1954) showed it; Soukoreff and MacKenzie (2004) set the standard; Zhai (2004) cautioned.",
    )
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert (
        "references: the Literature review cites 2 of the list's 3 entries; the template asks for 15 to 20"
        in result.stdout
    )
    assert "citation-no-entry" not in result.stdout
    assert "references: 3 entries in the list" in result.stderr
    assert "references: entry Card (1978) is not cited" in result.stderr
    assert checker.first_surname("- Card, S. K., English, W. K. (1978). X.") == "Card"
    assert checker.first_surname("- ISO (2000). ISO 9241-9.") == "ISO"
    assert checker.first_surname("1. Author 3 (2003). A paper.") == "Author 3"
    assert checker.year_of("- Fitts, P. M. (1954). X, 47(6).") == "1954"
    suffixed = "- Fitts, P. M. (1954a). X."
    assert checker.year_of(suffixed) == "1954a"
    assert checker._count_author_year([suffixed], "Fitts (1954a) showed it.", "") == 1
    assert checker.cited_numbers("see [1], [2, 3] and [4–6]; not [NAME]") == {
        1,
        2,
        3,
        4,
        5,
        6,
    }
    assert checker.cited_numbers("dated [2026-10-24] and [1-2-3]") == set()


def test_a_wrapped_list_entry_keeps_its_continuation_lines(tmp_path):
    """A list item hard-wrapped with its year on an indented continuation line
    (pandoc's 72-column wrap, kept by mdformat --wrap keep) is one entry, read
    with its continuation, so its year is found and it counts as cited."""
    text = valid_draft(reference_count=14)
    text = mutate(
        text,
        "\n\n## Appendix A",
        "\n- Wobbrock, J. O., Findlater, L., Gergle, D., and Higgins, J. J.\n"
        "  (2011). The aligned rank transform. CHI 2011.\n\n## Appendix A",
    )
    text = mutate(text, "Prior work: ", "Prior work: Wobbrock et al. (2011); ")
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert result.returncode == 0, result.stdout
    assert "references: 15 entries in the list" in result.stderr
    assert "without a surname and year" not in result.stderr
    assert "is not cited" not in result.stderr
    out = run(
        "draft", str(path), "--supervisor", "Dr. Example", "--references", "16-20"
    ).stdout
    assert (
        "references: the Literature review cites 15 of the list's 15 entries; the template asks for 16 to 20"
        in out
    )


def test_the_review_section_can_be_named_and_is_a_defect_when_absent(tmp_path):
    text = mutate(valid_draft(), "## Literature review\n", "## Related work\n")
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    named = run(
        "draft",
        str(path),
        "--supervisor",
        "Dr. Example",
        "--sections",
        "Introduction, Related work, Design",
        "--review-section",
        "Related work",
    )
    assert named.returncode == 0, named.stdout
    default = run(
        "draft",
        str(path),
        "--supervisor",
        "Dr. Example",
        "--sections",
        "Introduction, Design",
    )
    assert (
        "references: no `Literature review` section to count citations in [references-section; item 5.1]"
        in default.stdout
    )


def test_subheadings_stay_inside_their_sections(tmp_path):
    """A `###` under Introduction, References or an appendix must not end the
    section early: the bullets, the entries and the supervision sentence are
    still found."""
    text = valid_draft()
    text = mutate(
        text,
        "The contributions will be:\n",
        "### Contributions\n\nThe contributions will be:\n",
    )
    text = mutate(text, "## References\n\n", "## References\n\n### Primary\n\n")
    text = mutate(
        text,
        "## Appendix B: consent form\n\n",
        "## Appendix B: consent form\n\n### Consent form\n\n",
    )
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert result.returncode == 0, result.stdout


def test_a_malformed_range_is_a_usage_error(tmp_path):
    path = tmp_path / "draft.md"
    path.write_text(valid_draft(), encoding="utf-8")
    result = run("draft", str(path), "--words", "lots")
    assert result.returncode == 2
    assert "LOW-HIGH" in result.stderr


def test_sections_can_be_overridden_and_headings_match_case_insensitively(tmp_path):
    text = mutate(valid_draft(), "## Literature review\n", "## LITERATURE REVIEW\n")
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    assert run("draft", str(path)).returncode == 0
    custom = run("draft", str(path), "--sections", "Introduction, Design, Appendix")
    assert custom.returncode == 0, custom.stdout


@pytest.mark.parametrize(
    "heading",
    [
        "Hypotheses",
        "Research Questions and Hypotheses",
        "Research Questions",
        "Research Question",
        "Hypothesis",
        "Research Question and Hypotheses",
    ],
)
def test_a_section_named_with_or_matches_either_side(tmp_path, heading):
    text = mutate(
        valid_draft(), "## Research questions or Hypotheses\n", f"## {heading}\n"
    )
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert result.returncode == 0, result.stdout


def test_or_in_a_section_name_is_read_in_any_case(tmp_path):
    text = mutate(
        valid_draft(), "## Research questions or Hypotheses\n", "## Hypotheses\n"
    )
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    sections = "Introduction, Research questions OR hypotheses, Design"
    result = run("draft", str(path), "--sections", sections)
    assert result.returncode == 0, result.stdout
    assert checker._matches("Hypotheses", "Research questions Or hypotheses")


def test_singular_and_plural_words_match_and_appendix_stays_exact():
    assert checker._singular("research questions and hypotheses") == (
        "research question and hypothes"
    )
    assert checker._singular("hypothesis") == "hypothesi"
    assert checker._singular("appendices") == "appendic"
    assert checker._singular("s") == "s"
    assert checker._singular("procedures") == "procedur"
    assert checker._singular("procedure") == "procedur"
    assert checker._singular("e") == "e"
    assert checker._matches("Materials and Methods", "Material")
    assert checker._matches("Participant Information", "Participants")
    assert checker._matches("Appendices", "Appendix")
    assert checker._matches("Appendix B: consent form", "Appendix")
    assert checker._matches("Appendix B: consent form", "Appendix B")
    assert not checker._matches("Appendices", "Appendix B")
    assert not checker._matches("Appendix A: recruiting", "Appendix B")
    assert not checker._matches("Appendix A: recruiting", "Appendix S")


def test_a_plural_procedures_heading_passes_the_default_procedure_section(tmp_path):
    text = mutate(valid_draft(), "## Procedure\n", "## Procedures\n")
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert result.returncode == 0, result.stdout


def test_a_trailing_comma_in_sections_names_no_section(tmp_path):
    path = tmp_path / "draft.md"
    path.write_text(valid_draft(), encoding="utf-8")
    result = run("draft", str(path), "--sections", "Introduction, Design,")
    assert result.returncode == 0, result.stdout
    result = run("draft", str(path), "--sections", "Introduction,, Design , ")
    assert result.returncode == 0, result.stdout


def test_a_name_with_an_empty_side_matches_no_heading_by_it(tmp_path):
    assert not checker._matches("Introduction", "Nonexistent or ")
    assert not checker._matches("Introduction", " or ")
    assert not checker._matches("Introduction", "")
    path = tmp_path / "draft.md"
    path.write_text(valid_draft(), encoding="utf-8")
    result = run("draft", str(path), "--sections", "Introduction, Participants or")
    assert result.returncode == 1
    assert "sections: `Participants or` not found after `Introduction`" in (
        result.stdout
    )


def test_the_appendix_stem_belongs_to_a_bare_appendix_only(tmp_path):
    path = tmp_path / "draft.md"
    path.write_text(valid_draft(), encoding="utf-8")
    named = run("draft", str(path), "--sections", "Introduction, Appendix B")
    assert named.returncode == 0, named.stdout
    text = mutate(
        valid_draft(),
        "## Appendix A: recruiting announcement\n",
        "## Appendices\n\n### A: recruiting announcement\n",
    )
    text = mutate(text, "## Appendix B: consent form\n", "### B: consent form\n")
    text = mutate(text, "## Appendix C: session script\n", "### C: session script\n")
    path.write_text(text, encoding="utf-8")
    assert run("draft", str(path)).returncode == 0
    result = run("draft", str(path), "--sections", "Introduction, Appendix B")
    assert result.returncode == 1
    assert "sections: `Appendix B` not found after `Introduction`" in result.stdout


def test_a_consent_form_wrapped_between_the_title_and_the_name_passes(tmp_path):
    sentence = textwrap.fill(
        "This study is a project run by the author under the supervision of Dr. "
        "Jane Smith. You may stop at any time.",
        width=72,
    )
    assert "supervision of Dr.\nJane Smith." in sentence
    text = mutate(
        valid_draft(),
        "This study is run by the author under the supervision of Dr. Example as a course project. You may stop at any time.",
        sentence,
    )
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Jane Smith")
    assert result.returncode == 0, result.stdout


def test_the_supervision_sentence_is_sought_in_the_consent_appendix_first(tmp_path):
    """With a consent-headed appendix the sentence must be there; with none,
    every appendix is searched and stderr says so."""
    path = tmp_path / "draft.md"
    path.write_text(valid_draft(), encoding="utf-8")
    clean_run = run("draft", str(path), "--supervisor", "Dr. Example")
    assert clean_run.returncode == 0, clean_run.stdout
    assert "outside a consent-headed appendix" not in clean_run.stderr
    moved = mutate(
        valid_draft(),
        "## Appendix B: consent form\n\nThis study is run by the author under the supervision of Dr. Example as a course project. You may stop at any time.\n\n"
        "## Appendix C: session script\n\nWelcome.\n",
        "## Appendix B: consent form\n\nYou may stop at any time.\n\n"
        "## Appendix C: session script\n\nWelcome. This study is run under the supervision of Dr. Example.\n",
    )
    path.write_text(moved, encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert result.returncode == 1
    assert (
        "appendix: no consent sentence saying the study is under the supervision of the instructor [supervision; item 12.3]"
        in result.stdout
    )
    no_consent_heading = moved.replace(
        "## Appendix B: consent form\n", "## Appendix B: participant information\n"
    )
    path.write_text(no_consent_heading, encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert result.returncode == 0, result.stdout
    assert (
        "supervision sentence found outside a consent-headed appendix" in result.stderr
    )


def _numbers_fixture() -> str:
    """52 twice in prose, 36 once in the body and once in a consent-headed
    appendix, 45 once, a citation bracket `[52]` beside "participants", a
    heading `## 36 Consent form`, a dollar figure, a percentage, inline code.
    The Participants 52 is followed by a comma and the appendix 36 ends a
    sentence, so punctuation after an integer keeps it; the decimal 52.5 is
    not a 52."""
    text = valid_draft()
    text = mutate(
        text,
        "## Participants\n\n",
        "## Participants\n\nWe will recruit N = 52, about 36 in the full study, paying $847 in all; power is not computed. ",
    )
    text = mutate(
        text,
        "## Procedure\n\n",
        "## Procedure\n\nEach of the 52 sessions lasts a 45-minute slot of 52.5 trials on average; participants [52] agree; completion was 93% in `run.py --n 52`. ",
    )
    return mutate(
        text,
        "## Appendix B: consent form\n\n",
        "## 36 Consent form\n\nAs the 2026 plan says, the participants number about 36. ",
    )


def test_numbers_groups_repeated_values_and_masks_citations_code_and_heading_numbers(
    tmp_path,
):
    path = tmp_path / "draft.md"
    path.write_text(_numbers_fixture(), encoding="utf-8")
    result = run("--json", "draft", str(path), "--numbers")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)["numbers"]
    by_value = {group["value"]: group["locations"] for group in report}
    assert set(by_value) == {"52", "36", "$847", "93%"}, by_value
    # document order, within a line too: `52` and `36` precede `$847` on one line
    assert [group["value"] for group in report] == ["52", "36", "$847", "93%"]
    # the comma-followed 52 and the sentence-final 36 count; the decimal 52.5 does not
    assert len(by_value["52"]) == 2
    assert len(by_value["36"]) == 2
    assert {loc["heading"] for loc in by_value["36"]} == {
        "Participants",
        "36 Consent form",
    }
    assert all("52" in loc["text"] for loc in by_value["52"])
    assert [loc["heading"] for loc in by_value["52"]] == ["Participants", "Procedure"]
    assert "45" not in by_value
    assert "2026" not in by_value
    for loc in by_value["52"]:
        assert isinstance(loc["line"], int)
        assert len(loc["text"].split()) <= 13
    text_mode = run("draft", str(path), "--numbers")
    assert text_mode.returncode == 0
    assert "52: 2 occurrences\n  Participants (line " in text_mode.stdout
    # the report mode judges nothing: the mechanics of the same draft would fail
    assert run("draft", str(path), "--words", "1-2").returncode == 1


def test_placeholders_lists_todo_and_bracketed_names_and_compares_with_the_list(
    tmp_path,
):
    text = mutate(
        valid_draft(),
        "## Materials\n\n",
        "## Materials\n\nThe device is [NAME]; TODO decide the display. ",
    )
    text = mutate(
        text,
        "## Appendix C: session script\n\nWelcome.\n",
        "## Appendix C: session script\n\nWelcome.\n\n## Appendix H: Placeholders\n\n- [VENUE]: where the sessions run.\n",
    )
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    plain = json.loads(run("--json", "draft", str(path), "--placeholders").stdout)
    assert [p["text"] for p in plain["placeholders"]] == ["[NAME]", "TODO", "[VENUE]"]
    assert plain["placeholders"][0]["heading"] == "Materials"
    assert plain["unlisted"] == []
    assert plain["unused"] == []
    listed = json.loads(
        run(
            "--json",
            "draft",
            str(path),
            "--placeholders",
            "--placeholder-list",
            "Appendix H",
        ).stdout
    )
    assert listed["unlisted"] == ["TODO", "[NAME]"]
    assert listed["unused"] == ["[VENUE]"]
    text_mode = run(
        "draft", str(path), "--placeholders", "--placeholder-list", "Appendix H"
    )
    assert text_mode.returncode == 0
    assert "[NAME]: Materials (line " in text_mode.stdout
    assert "used but not listed: TODO, [NAME]" in text_mode.stdout
    assert "listed but unused: [VENUE]" in text_mode.stdout
    both = run("draft", str(path), "--numbers", "--placeholders")
    assert both.returncode == 2


# --------------------------------------------------------------------------
# The evaluation fixtures agree with the checker
# --------------------------------------------------------------------------

FIXTURES = (
    ROOT / "docs" / "research" / "2026-10-13-experiment-proposal-evals" / "fixtures"
)


def test_the_brief_fixture_is_a_frozen_brief_the_checker_accepts():
    result = run("brief", str(FIXTURES / "proposal-with-defects.brief.md"))
    assert result.returncode == 0, result.stdout


def test_the_draft_fixture_fails_exactly_the_three_planted_mechanics():
    """D3 (no bullet list), D8 (14 references) and D9 (no supervision
    sentence) are the lens defects; sections and the word count hold."""
    result = run(
        "draft",
        str(FIXTURES / "proposal-with-defects.md"),
        "--supervisor",
        "the course instructor",
    )
    assert result.returncode == 1
    messages = [message_of(line) for line in result.stdout.splitlines()]
    assert messages == [
        "references: the Literature review cites 14 of the list's 14 entries; the template asks for 15 to 20",
        "introduction: no bullet list of contributions",
        "appendix: no consent sentence saying the study is under the supervision of the instructor",
    ]


def test_the_checker_stops_with_an_install_pointer_on_an_old_python(
    monkeypatch, capsys
):
    monkeypatch.setattr(checker.sys, "version_info", (3, 10, 0))
    assert checker.main(["brief", "proposal/design-brief.md"]) == 2
    assert "Python 3.11 or later" in capsys.readouterr().err
