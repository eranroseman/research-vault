"""The paper-critical-analysis skill's briefs are the contract its subagents obey.

SKILL.md points at them and does not restate them (the judging contract lives
in prompts/judge.md, the editing contract in prompts/edit.md, the verification
contract in prompts/verify.md), so the surfaces can drift silently: an edit to
a dimension name, a placeholder, or a reference path in one file leaves the
others stale, and nothing at runtime complains. These tests are that complaint.
"""

import re
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "paper-critical-analysis"
SKILL_MD = SKILL_DIR / "SKILL.md"
BRIEFS = ("judge.md", "edit.md", "verify.md")

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
# A brace placeholder a brief expects the dispatcher to fill: "{PAPER_PATHS}"
_PLACEHOLDER = re.compile(r"\{([A-Z_]+)\}")
# A load-table or brief reference to a shipped file, e.g. `references/participants.md`
_SHIPPED_PATH = re.compile(r"`((?:references|prompts|templates|scripts)/[\w./-]+)`")


def _skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _brief(name: str) -> str:
    return (SKILL_DIR / "prompts" / name).read_text(encoding="utf-8")


def test_the_judge_brief_owns_the_nine_dimensions_in_order():
    """The dimension bullets live in the brief, because the judge subagent
    cannot read SKILL.md. Renaming or reordering one silently changes every
    report."""
    section = _brief("judge.md")
    section = section[section.index("## The nine dimensions") :]
    assert tuple(_DIMENSION_BULLET.findall(section)) == NINE


def test_the_skill_lists_the_same_nine_in_the_same_order():
    """SKILL.md keeps the names so the report outline is legible, and the brief
    keeps what each asks. Two surfaces, one order."""
    text = _skill_text()
    sentence = text[text.index("The nine, in order:") :].split("\n", 1)[0]
    found = tuple(n for n in re.findall(r"[A-Z][a-z]+", sentence) if n in NINE)
    assert found == NINE, f"SKILL.md lists {found}"


def test_the_report_template_carries_the_same_nine_as_headings_in_order():
    """The checker takes its required headings from the template, so the
    template is where a renamed dimension would strand every future report."""
    template = (SKILL_DIR / "templates" / "report-template.md").read_text(
        encoding="utf-8"
    )
    body = template[template.index("## 3.") : template.index("## 4.")]
    found = tuple(
        line[4:].strip() for line in body.splitlines() if line.startswith("### ")
    )
    assert found == ("Verdicts", *NINE)


def test_the_judge_brief_asks_for_every_subsection_it_defines():
    """The brief's return contract and its dimension list are separate
    passages; when they disagree the subagent leaves a slot empty and nothing
    errors."""
    brief = _brief("judge.md")
    listed = brief[
        brief.index("## What you return") : brief.index("Each subsection opens")
    ]
    for dimension in NINE:
        assert dimension in listed, (
            f"judge.md never asks for the {dimension} subsection"
        )


@pytest.mark.parametrize("brief_name", BRIEFS)
def test_every_brief_placeholder_is_documented(brief_name):
    """A placeholder the brief never explains is one a dispatcher leaves
    unfilled, and the subagent then reads a literal brace as its input."""
    brief = _brief(brief_name)
    fenced = brief[brief.index("```") : brief.rindex("```")]
    prose = brief.replace(fenced, "")
    for placeholder in sorted(set(_PLACEHOLDER.findall(fenced))):
        documented = (
            f"{{{placeholder}}}" in prose
            or placeholder.lower().replace("_", " ") in prose.lower()
        )
        assert (
            documented
            or f"{{{placeholder}}}" in _skill_text()
            or _names_it(placeholder)
        ), f"{brief_name} uses {{{placeholder}}} and nothing says what fills it"


def _names_it(placeholder: str) -> bool:
    """The skill's dispatch line may name a placeholder in words rather than
    in braces ("the evidence file" for EVIDENCE_PATH)."""
    head = placeholder.lower().split("_")[0]
    return head in _skill_text().lower()


@pytest.mark.parametrize("brief_name", ["judge.md", "verify.md"])
def test_every_brief_that_handles_locators_is_given_the_convention(brief_name):
    """The judge writes Locator fields and the verifier checks them, and each
    runs in a subagent that cannot read SKILL.md where the convention is
    defined. The verifier shipped without it once: it then checked locators
    against a reading of its own and reported correct items as failures. The
    editor only preserves locators verbatim, so it needs no convention."""
    assert "{LOCATOR_CONVENTION}" in _brief(brief_name), (
        f"{brief_name} handles locators and is never handed the convention"
    )


@pytest.mark.parametrize("brief_name", BRIEFS)
def test_the_skill_dispatches_every_brief_it_ships(brief_name):
    """A brief nothing dispatches is dead weight, and a stage that names no
    brief has lost its contract."""
    assert f"prompts/{brief_name}" in _skill_text()


def test_no_retired_brief_survives():
    """Fan-out is a spec non-goal; the extractor brief went with it."""
    assert not (SKILL_DIR / "prompts" / "extract.md").exists()


STAGES = (
    "## Stage 0 — Settle conditions",
    "## Stage 1 — Read into the evidence file",
    "## Stage 2 — Check exhaustively",
    "## Stage 3 — Judge",
    "## Stage 4 — Write",
    "## Stage 5 — Edit",
    "## Stage 6 — Check",
    "## Stage 7 — Verify",
)


def test_the_stages_run_in_order_and_none_went_missing():
    """The stages were renumbered in the merge; a half-finished renumbering
    leaves the file pointing at stages that moved."""
    text = _skill_text()
    seen = []
    for heading in STAGES:
        assert heading in text, f"{heading!r} is gone from SKILL.md"
        seen.append(text.index(heading))
    assert seen == sorted(seen), "the stage headings are out of run order"
    assert "Eight stages" in text, (
        "the file never tells the reader how many stages there are"
    )


def test_the_skill_does_not_restate_the_judging_contract():
    """The contract lives in prompts/judge.md precisely because two copies
    drift. A bolded field name reappearing in SKILL.md is that drift starting
    again: the skill may name a field in prose, never re-specify the set."""
    text = _skill_text()
    for phrase in ("**Observation**", "**Why it matters**", "**Evidence**"):
        assert phrase not in text, (
            f"SKILL.md restates {phrase!r}, which prompts/judge.md owns"
        )


def test_every_ledger_the_evidence_file_defines_is_admissible_to_the_judge():
    """Stage 3 is the discussion's only source of findings, so a ledger the
    judge may not cite reaches the report only through Context, where a reader
    takes it for scene-setting. The external-check list shipped that way once."""
    sentence = _brief("judge.md")
    sentence = sentence[sentence.index("**Admissible evidence**") :].split("\n", 1)[0]
    template = (SKILL_DIR / "templates" / "evidence-template.md").read_text(
        encoding="utf-8"
    )
    for prefix in "NCW":
        assert f"- {prefix}1:" in template, (
            f"evidence-template.md shows no {prefix}1 entry shape"
        )
        assert f"{prefix}-" in sentence or f"{prefix}1" in sentence, (
            f"the evidence file defines {prefix} entries and the judge may not "
            "cite them"
        )


def test_the_kind_values_match_the_count_the_brief_states():
    """The brief states the count and then lists the values, so a value added
    or removed leaves the number stale."""
    brief = _brief("judge.md")
    stated = re.findall(r"Kind is one of (?:the )?([a-z]+)", brief)
    assert stated, "the brief never states how many Kind values there are"
    assert len(set(stated)) == 1, f"the brief states the Kind count as {stated}"
    word_numbers = {"three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
    start = brief.index("Kind is one of", brief.index("Kind is one of") + 1)
    listed = re.findall(
        r"^- ([A-Z][^—]*)—",
        brief[start : brief.index("Every quote", start)],
        re.MULTILINE,
    )
    assert len(listed) == word_numbers[stated[0]], (
        f"the brief lists {len(listed)} Kind values and calls them {stated[0]}"
    )


def test_every_section_the_judge_returns_has_a_destination():
    """The judge returns the nine subsections and a Recalled section, and
    stage 3's screen drops what it does not recognise. A section the brief
    asks for and the skill never routes is thrown away with the run's
    disclosure in it."""
    brief = _brief("judge.md")
    returned = brief[brief.index("## What you return") : brief.index("## Delegation")]
    assert "Recalled" in returned, "judge.md no longer asks for the Recalled section"
    text = _skill_text()
    stage_3 = text[text.index(STAGES[3]) : text.index(STAGES[4])]
    assert "Recalled" in stage_3, (
        "stage 3 never says what becomes of the Recalled section"
    )


def test_the_paper_type_bar_covers_the_spec_types():
    """The spec names seven paper types; a type with no row is judged against
    somebody else's bar."""
    brief = _brief("judge.md")
    bar = brief[brief.index("## The bar") : brief.index("## The nine dimensions")]
    for paper_type in (
        "Empirical",
        "Theoretical",
        "Survey",
        "Systems",
        "Position",
        "Replication",
        "Negative results",
    ):
        assert paper_type in bar, f"the bar table has no {paper_type} row"


def test_every_shipped_path_the_skill_and_briefs_cite_exists():
    """The load table and the briefs route by repository-relative path; a
    renamed reference file strands the stage that loads it."""
    missing = {
        f"{owner}: {path}"
        for owner, text in (
            ("SKILL.md", _skill_text()),
            *((name, _brief(name)) for name in BRIEFS),
        )
        for path in _SHIPPED_PATH.findall(text)
        if not (SKILL_DIR / path).exists()
    }
    assert not missing, f"cited but not shipped: {sorted(missing)}"


def test_every_reference_file_is_reachable_from_the_load_table():
    """A reference file the load table never assigns is dead weight no stage
    walks and no brief hands the judge."""
    text = _skill_text()
    table = text[text.index("## What the paper loads") :]
    table = table.split("## Stage", 1)[0]
    for path in sorted((SKILL_DIR / "references").glob("*.md")):
        assert f"references/{path.name}" in table, (
            f"references/{path.name} is shipped and the load table never assigns it"
        )
