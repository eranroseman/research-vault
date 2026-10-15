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


def _brief_under(version: str) -> str:
    """A brief frozen 2026-10-10 under `version` that breaks every entry rule:
    a 500-character Decision, an entry for the retired item 6.7, no entry for
    7.9."""
    assert "6.7" not in ITEMS
    assert "7.9" in DESIGN_TREE
    text = mutate(
        valid_brief(status="frozen 2026-10-10"),
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


def test_the_row_pattern_accepts_every_result_word():
    for result in checker.RESULTS:
        match = checker.ROW.match(f"- **1.1** {result}: x")
        assert match is not None, result
        assert match.group(2) == result


# --------------------------------------------------------------------------
# draft
# --------------------------------------------------------------------------

SENTENCE = "Participants will select targets on the screen with each device in turn. "


def valid_draft(body_sentences: int = 240, reference_count: int = 16) -> str:
    """A draft with the course's sections in order, about 2,900 body words,
    sixteen references, a bulleted contributions list and the supervision
    sentence."""
    prose = SENTENCE * (body_sentences // 7)
    references = "\n".join(
        f"- Author {n} ({2000 + n}). A paper about pointing, number {n}. A Journal."
        for n in range(reference_count)
    )
    return (
        "# A controlled experiment\n\n"
        f"## Introduction\n\nWe ask a question. {prose}\n\nThe contributions will be:\n\n- an estimate;\n- a test;\n- a program.\n\n"
        f"## Literature review\n\n{prose}\n\n"
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
        "references: 14 entries; the template asks for 15 to 20"
        in run("draft", str(path)).stdout
    )
    path.write_text(valid_draft(), encoding="utf-8")
    out = run("draft", str(path), "--supervisor", "Dr. Someone Else").stdout
    assert "appendix: the supervision sentence names 'Dr. Example" in out
    assert "not 'Dr. Someone Else'" in out


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


@pytest.mark.parametrize("heading", ["Hypotheses", "Research Questions and Hypotheses"])
def test_a_section_named_with_or_matches_either_side(tmp_path, heading):
    text = mutate(
        valid_draft(), "## Research questions or Hypotheses\n", f"## {heading}\n"
    )
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    result = run("draft", str(path), "--supervisor", "Dr. Example")
    assert result.returncode == 0, result.stdout


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
    messages = [line.split(": ", 1)[1] for line in result.stdout.splitlines()]
    assert messages == [
        "references: 14 entries; the template asks for 15 to 20",
        "introduction: no bullet list of contributions",
        "appendix: no consent sentence saying the study is under the supervision of the instructor",
    ]


def test_the_checker_stops_with_an_install_pointer_on_an_old_python(
    monkeypatch, capsys
):
    monkeypatch.setattr(checker.sys, "version_info", (3, 10, 0))
    assert checker.main(["brief", "proposal/design-brief.md"]) == 2
    assert "Python 3.11 or later" in capsys.readouterr().err
