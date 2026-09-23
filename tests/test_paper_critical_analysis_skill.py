"""The paper-critical-analysis skill's briefs are the contract its subagents obey.

SKILL.md points at them and no longer restates them (the judging contract lives
in prompts/judge.md, the verification contract in prompts/verify.md), so the two
surfaces can drift silently: an edit to a dimension name or a placeholder in one
file leaves the other stale, and nothing at runtime complains. These tests are
that complaint.
"""

import re
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "paper-critical-analysis"
SKILL_MD = SKILL_DIR / "SKILL.md"
BRIEFS = ("judge.md", "verify.md")

# A bolded dimension name opening a Discussion bullet: "- **Importance** — ..."
_DIMENSION_BULLET = re.compile(r"^- \*\*([A-Z][a-z]+)\*\* —", re.MULTILINE)
# A brace placeholder a brief expects the dispatcher to fill: "{PAPER_PATH}"
_PLACEHOLDER = re.compile(r"\{([A-Z_]+)\}")


def _skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _discussion_dimensions() -> list[str]:
    text = _skill_text()
    section = text[text.index("### 3. Discussion") : text.index("### What this report did not check")]
    return _DIMENSION_BULLET.findall(section)


def test_discussion_names_the_nine_dimensions_in_order():
    """The nine are the skill's contract with its eval runs; renaming or
    reordering one silently changes every report's shape."""
    assert _discussion_dimensions() == [
        "Importance",
        "Credibility",
        "Novelty",
        "Applicability",
        "Generalizability",
        "Scalability",
        "Assumptions",
        "Readability",
        "Ethics",
    ]


def test_judge_brief_returns_the_dimensions_the_discussion_asks_for():
    """The judge brief lists the headings it must return. When that list and the
    Discussion outline disagree, the subagent returns a section the report has no
    slot for, or leaves a slot empty, and neither shows up as an error."""
    brief = (SKILL_DIR / "prompts" / "judge.md").read_text(encoding="utf-8")
    listed = brief[brief.index("## What you return") : brief.index("Each subsection opens")]
    for dimension in _discussion_dimensions():
        assert dimension in listed, f"judge.md never asks for the {dimension} subsection"


@pytest.mark.parametrize("brief_name", BRIEFS)
def test_every_brief_placeholder_is_documented(brief_name):
    """A placeholder the brief never explains is one a dispatcher leaves
    unfilled, and the subagent then reads a literal brace as its input."""
    brief_path = SKILL_DIR / "prompts" / brief_name
    brief = brief_path.read_text(encoding="utf-8")
    fenced = brief[brief.index("```") : brief.rindex("```")]
    prose = brief.replace(fenced, "")
    for placeholder in sorted(set(_PLACEHOLDER.findall(fenced))):
        documented = f"{{{placeholder}}}" in prose or placeholder.lower().replace("_", " ") in prose.lower()
        assert documented or f"{{{placeholder}}}" in _skill_text() or _names_it(placeholder), (
            f"{brief_name} uses {{{placeholder}}} and nothing says what fills it"
        )


def _names_it(placeholder: str) -> bool:
    """The skill's dispatch line may name a placeholder in words rather than in
    braces ("the stage 1 extraction" for EXTRACTION_PATH)."""
    words = placeholder.lower().split("_")
    head = words[0]
    return head in _skill_text().lower()


@pytest.mark.parametrize("brief_name", BRIEFS)
def test_the_skill_dispatches_every_brief_it_ships(brief_name):
    """A brief nothing dispatches is dead weight, and a stage that names no
    brief has lost its contract."""
    assert f"prompts/{brief_name}" in _skill_text()


STAGES = (
    "## Stage 1 — Extract",
    "## Stage 2 — List what the paper does not say",
    "## Stage 3 — Judge",
    "## Stage 4 — Assemble the report",
    "## Stage 5 — Tighten the assembled report",
    "## Stage 6 — Verify the report against the paper",
)


def test_the_stages_run_in_order_and_none_went_missing():
    """The stages were renumbered once when assembly was given its own name, and
    a half-finished renumbering leaves the file pointing at stages that moved."""
    text = _skill_text()
    seen = []
    for heading in STAGES:
        assert heading in text, f"{heading!r} is gone from SKILL.md"
        seen.append(text.index(heading))
    assert seen == sorted(seen), "the stage headings are out of run order"
    assert f"{len(STAGES)} stages" in text or "Six stages" in text, (
        "the file never tells the reader how many stages there are"
    )


def test_the_skill_does_not_restate_the_judging_contract():
    """The contract moved into prompts/judge.md precisely because two copies
    drifted. A bolded field name reappearing in SKILL.md is that drift starting
    again: the skill may name a field in prose, never re-specify the set."""
    text = _skill_text()
    for phrase in ("**Observation**", "**Why it matters**", "**Evidence or criterion**"):
        assert phrase not in text, (
            f"SKILL.md restates {phrase!r}, which prompts/judge.md owns"
        )
