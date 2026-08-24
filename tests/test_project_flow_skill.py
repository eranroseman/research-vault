"""Content acceptance checks for the `project-flow` entry skill (spec §7).

Unlike ``test_skill_contracts.py`` (the generic frontmatter/control-model
contract every skill satisfies), this module asserts what makes `project-flow`
specifically *this* skill: the four verbatim elicitation elements, the
resume-orientation triple, the inbox-drain and trust-tier surfaces, gap
analysis's three buckets with `disputes` links surfaced, the draft frame
invoking `evidence-conventions` rather than restating its Iron Law, and
every routing target the brief names.
"""

from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
SKILL = REPOSITORY / "skills" / "project-flow" / "SKILL.md"
EVIDENCE_CONVENTIONS = REPOSITORY / "skills" / "evidence-conventions" / "SKILL.md"


def _skill_text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_project_frontmatter_is_entry_only_and_undiscoverable():
    """Removing the entry-only frontmatter, or making it user-invocable, must fail."""
    text = _skill_text()

    assert text.startswith("---\nname: project-flow\ndescription: Use when ")
    assert "disable-model-invocation: true\n---\n" in text
    assert "user-invocable" not in text


def test_project_elicitation_states_all_four_fields_verbatim():
    """Dropping or paraphrasing any of the four required elicitation elements
    must fail — spec §7's project row names these exactly."""
    text = _skill_text()

    for phrase in (
        "The question itself",
        "Scope bounds",
        "in/out",
        "Expected source types",
        "Success criteria",
    ):
        assert phrase in text, f"missing verbatim elicitation element: {phrase!r}"
    assert "no external reference" in text


def test_project_documents_the_resume_orientation_triple_in_order():
    """Skipping a piece of the triple, or reordering orientation after
    drafting, must fail. Orientation happens before gap analysis, every time."""
    text = _skill_text()

    sequence = [
        "synthesis/index.md",
        "recent `log/`",
        "the project's files",
        "## Gap analysis",
    ]
    positions = [text.index(token) for token in sequence]
    assert positions == sorted(positions)


def test_project_documents_inbox_drain_with_count_and_age_oldest_first():
    """Losing the count-and-age, oldest-first framing, or the escalating
    display for an aging queue, must fail (spec §3's Whittaker guard)."""
    text = _skill_text()

    assert "python3 -m knowledge_harness inbox --vault PATH" in text
    assert "unacknowledged count and the oldest entry's date, oldest first" in text
    assert "aging queue earns more prominence" in text
    # Non-blocking: the inbox never gates anything at project orientation.
    assert "nothing here blocks on age" in text


def test_project_documents_trust_tier_surface_read_only():
    """Dropping the trust-tier lookup, or any of the three cumulative tier
    names, must fail — this is the CLI surface `events.trust_tier` was
    retained for."""
    text = _skill_text()

    assert "python3 -m knowledge_harness trust-tier CITEKEY --vault PATH" in text
    for tier in ("unverified", "machine-confirmed", "human-reviewed"):
        assert tier in text
    assert "read-only report; it writes nothing" in text


def test_project_documents_gap_analysis_buckets_with_disputes_surfaced():
    """Losing any of the three buckets, or the instruction to surface
    `disputes` links rather than folding contested claims into 'covered',
    must fail."""
    text = _skill_text()
    gap_section = text[text.index("## Gap analysis") : text.index("## Draft frame")]

    assert "Covered" in gap_section
    assert "Contested" in gap_section
    assert "Missing" in gap_section
    assert "[disputes:: ...]" in gap_section
    assert "never silently folded into" in gap_section
    assert "`find-sources`" in gap_section


def test_project_draft_frame_invokes_evidence_conventions_never_restates_it():
    """Restating (even paraphrasing closely) the Iron Law here instead of
    invoking the guard skill must fail — a restatement that drifts from the
    guard is the exact failure this rule exists to prevent."""
    text = _skill_text()
    iron_law = "No claim enters a draft without a verified source first."

    assert iron_law in EVIDENCE_CONVENTIONS.read_text(encoding="utf-8")
    assert "`evidence-conventions`" in text
    assert iron_law not in text
    assert "verified source first" not in text.lower()


def test_project_documents_every_routing_target():
    """Dropping a routing row, or routing to the wrong skill, must fail."""
    text = _skill_text()
    routing = text[text.index("## Routing") : text.index("## Acknowledgments")]

    for skill_name in (
        "find-sources",
        "import-source",
        "verify-citations",
        "factcheck-draft",
        "publish",
    ):
        assert f"`{skill_name}`" in routing


def test_project_routing_forbids_silently_broadening_the_routed_intent():
    """An orchestrator that hands a routed skill more than the person asked
    for does unrequested work under a routing decision nobody made. The slice
    is the point of this test, not incidental: the guard has to sit where the
    routing decision is taken, because the same sentence anywhere else in the
    file is not read at the moment it would have to bind.
    """
    text = _skill_text()
    routing = text[text.index("## Routing") : text.index("## Acknowledgments")]

    assert "route the user's intent without silently broadening it" in routing.lower()
    assert "let the person widen it" in routing


def test_project_documents_acks_via_the_ack_verb_with_human_consent():
    """Hand-writing an acknowledgment, or skipping the human-consent step,
    must fail."""
    text = _skill_text()
    ack_section = text[text.index("## Acknowledgments") :]

    assert (
        "python3 -m knowledge_harness ack FINDING-ID --vault PATH "
        '--reason "CODE free text" --actor "human:NAME"'
    ) in ack_section
    assert "the person consents; the CLI writes" in ack_section


def test_project_never_hand_writes_a_mechanical_act():
    """A skill claiming to write an event, status, tag, or ack itself
    (outside a CLI verb call) must fail — every mechanical act routes
    through the CLI, per the global constraint."""
    text = _skill_text()

    assert "the CLI writes" in text
    assert (
        "every mechanical act in this skill (events, statuses, tags, holds, "
        "acknowledgments) is a CLI verb call"
    ) in text
