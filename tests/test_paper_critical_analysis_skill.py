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
BRIEFS = ("judge.md", "verify.md", "extract.md")

# A bolded dimension name opening a dimension bullet: "- **Importance** — ..."
_DIMENSION_BULLET = re.compile(r"^- \*\*([A-Z][a-z]+)\*\* —", re.MULTILINE)

NINE = (
    "Importance",
    "Credibility",
    "Novelty",
    "Applicability",
    "Generalizability",
    "Scalability",
    "Assumptions",
    "Readability",
    "Ethics",
)
# A stage 2 list bullet and the prefix its entries are numbered with:
# "- **Not-stated list** (N1, N2, ...)"
_STAGE_2_LIST = re.compile(r"^- \*\*([^*]+)\*\* \(([A-Z])1, ", re.MULTILINE)
# A brace placeholder a brief expects the dispatcher to fill: "{PAPER_PATH}"
_PLACEHOLDER = re.compile(r"\{([A-Z_]+)\}")


def _skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _judge_brief() -> str:
    return (SKILL_DIR / "prompts" / "judge.md").read_text(encoding="utf-8")


def test_the_judge_brief_owns_the_nine_dimensions_in_order():
    """The dimension bullets live in the brief, because the judge subagent cannot
    read SKILL.md. Renaming or reordering one silently changes every report."""
    section = _judge_brief()
    section = section[section.index("## The nine dimensions") :]
    assert tuple(_DIMENSION_BULLET.findall(section)) == NINE


def test_the_skill_lists_the_same_nine_in_the_same_order():
    """SKILL.md keeps the names so its report outline is legible, and the brief
    keeps what each asks. Two surfaces, one order: when they disagree, the judge
    returns a subsection the report has no slot for and nothing errors."""
    text = _skill_text()
    sentence = text[text.index("The nine, in order:") :].split("\n", 1)[0]
    found = tuple(n for n in re.findall(r"[A-Z][a-z]+", sentence) if n in NINE)
    assert found == NINE, f"SKILL.md lists {found}"


def test_the_judge_brief_asks_for_every_subsection_it_defines():
    """The brief's return contract and its dimension list are separate passages;
    when they disagree the subagent leaves a slot empty and nothing errors."""
    brief = _judge_brief()
    listed = brief[brief.index("## What you return") : brief.index("Each subsection opens")]
    for dimension in NINE:
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
def test_every_brief_that_handles_locations_is_given_the_convention(brief_name):
    """Every brief either writes Location fields or checks them, and each runs in
    a subagent that cannot read SKILL.md where the convention is defined. The
    verifier shipped without it once: it then checked Locations against a reading
    of its own and reported correct report items as failures."""
    brief = (SKILL_DIR / "prompts" / brief_name).read_text(encoding="utf-8")
    assert "{LOCATION_CONVENTION}" in brief, (
        f"{brief_name} handles Locations and is never handed the convention"
    )


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


def _stage_2_lists() -> list[tuple[str, str]]:
    text = _skill_text()
    stage_2 = text[text.index(STAGES[1]) : text.index(STAGES[2])]
    return _STAGE_2_LIST.findall(stage_2)


def test_every_list_stage_2_writes_is_admissible_to_the_judge():
    """Stage 3 is the Discussion's only source of findings, so a stage 2 list the
    judge may not cite reaches the report only through Context, where a reader
    takes it for scene-setting. The external-check list shipped that way once:
    its web-verified findings could not become findings at all."""
    sentence = _judge_brief()
    sentence = sentence[sentence.index("**Admissible evidence**") :].split("\n", 1)[0]
    lists = _stage_2_lists()
    assert len(lists) == 3, f"stage 2 writes {lists}"
    for name, prefix in lists:
        assert f"{prefix}-" in sentence, (
            f"stage 2 writes the {name} and the judge may not cite its entries"
        )


def test_the_appendix_carries_every_list_stage_2_writes():
    """The appendix is where a numbered list becomes citable: the Discussion's
    evidence points at an entry a reader can look up. A list written but never
    published leaves every point resting on it unverifiable."""
    heading = next(
        line for line in _skill_text().splitlines() if line.startswith("### Appendix:")
    )
    for name, _ in _stage_2_lists():
        assert name.lower() in heading.lower(), (
            f"stage 2 writes the {name} and the appendix never names it"
        )


_WORD_NUMBERS = {"three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}


def test_the_kind_values_match_the_count_the_brief_states():
    """The brief states the count twice and then lists the values, so a value
    added or removed leaves two numbers stale. That happened once in the other
    direction: SKILL.md's screen was told there were four admissible kinds when
    the contract it defers to lists three."""
    brief = _judge_brief()
    stated = re.findall(r"Kind is one of (?:the )?([a-z]+)", brief)
    assert stated and len(set(stated)) == 1, f"the brief states the Kind count as {stated}"
    start = brief.index("Kind is one of", brief.index("Kind is one of") + 1)
    listed = re.findall(r"^- ([A-Z][^—]*)—", brief[start : brief.index("Every quote", start)], re.MULTILINE)
    assert len(listed) == _WORD_NUMBERS[stated[0]], (
        f"the brief lists {len(listed)} Kind values and calls them {stated[0]}: {listed}"
    )


def test_every_section_the_judge_returns_has_a_destination():
    """The judge returns the nine dimension subsections and a Recalled section,
    and stage 4 discards anything it does not recognise. A section the brief asks
    for and the screen does not name is thrown away with the run's disclosure in
    it."""
    brief = _judge_brief()
    returned = brief[brief.index("## What you return") : brief.index("## Delegation")]
    assert "Recalled" in returned, "judge.md no longer asks for the Recalled section"
    screen = _skill_text()
    screen = screen[screen.index(STAGES[3]) : screen.index(STAGES[4])]
    assert "Recalled" in screen, "stage 4 never says what becomes of the Recalled section"
