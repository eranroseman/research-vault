"""check_report.py enforces the report rules the spec lists; the templates are
its single source of truth for structure.

The passing fixture is BUILT FROM THE SHIPPED TEMPLATES through the checker's
own heading parser, so a template edit that breaks agreement fails here rather
than in a live run. Each spec rule then gets one failing mutation.
"""

import contextlib
import importlib.util
import io
import re
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "paper-critical-analysis"
CHECKER = SKILL_DIR / "scripts" / "check_report.py"

_spec = importlib.util.spec_from_file_location("check_report", CHECKER)
check_report = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_report)

KEY_LINE = (
    "Key: a locator cites the paper; (W12) cites a source outside the paper "
    "through the evidence file; [inferred] marks the writer's own reasoning; "
    'a number marked "derived" cites the C, W or J entry holding its '
    "computation; recalled knowledge appears only under Coverage."
)


def _topic_body(heading: str) -> str:
    body = "Verdict: the paper holds on this dimension (Table 2; N1). J1 bears here."
    if heading.startswith("### Credibility"):
        body += " Confidence: medium; an independent replication would raise it."
    return body


def _coverage_body() -> str:
    leads = check_report.coverage_leads()
    lines = []
    for lead in leads:
        if lead == "Evidence file only":
            lines.append(f"- {lead}: J2.")
        else:
            lines.append(f"- {lead}: none; checked: the whole run.")
    return "\n".join(lines)


def build_report() -> str:
    """Fill the shipped report template heading-by-heading."""
    lines = []
    for _, full in check_report.template_headings(check_report.REPORT_TEMPLATE):
        heading = full.replace("{{paper title}}", "Example")
        lines.append(heading)
        if heading.startswith("# Critical analysis"):
            lines.append(
                "Doe (2026). Example. Venue. Version read: v1. Written 2026-10-04."
            )
            lines.append(KEY_LINE)
        elif heading.startswith("### Verdicts"):
            lines.append("Nine one-line verdicts stand here (Section 1; W1).")
        elif heading.startswith("## 4."):
            lines.append(_coverage_body())
        elif heading.startswith("### 2.3"):
            lines.append(
                "The rate is 4.2 per day, derived, from C1. CORE ranks it (W1)."
            )
        elif heading.startswith("###") and check_report.is_topic(heading):
            lines.append(_topic_body(heading))
        else:
            lines.append("Filled in prose; see Section 2 of the paper.")
        lines.append("")
    return "\n".join(lines)


def build_evidence() -> str:
    """Fill the shipped evidence template heading-by-heading."""
    lines = []
    for _, full in check_report.template_headings(check_report.EVIDENCE_TEMPLATE):
        heading = full.replace("{{paper title}}", "Example")
        lines.append(heading)
        if heading.startswith("## Not-stated"):
            lines.append("- N1: consent wording; needed by Claim 1.")
        elif heading.startswith("## Inconsistency"):
            lines.append(
                "- C1: Table 2 says 4.2, abstract says 4.4; recomputed in code."
            )
        elif heading.startswith("## External-check"):
            lines.append("- W1: venue rigor; CORE; saved copy; ranked A.")
            lines.extend(
                f"- {lead}: W1." for lead in check_report.external_check_leads()
            )
        elif heading.startswith("## Judge points"):
            lines.append(
                "- J1: Not reported; Table 2; no denominator; N1; weakens the rate."
            )
            lines.append(
                "- J2: Not reported; Section 5; minor wording slip; C1; low stakes."
            )
        else:
            lines.append("Filled; pending sections read pending: stage 7.")
        lines.append("")
    return "\n".join(lines)


def run(report: str, evidence: str | None, tmp_path: Path) -> tuple[int, str]:
    report_path = tmp_path / "critical-analysis-example.md"
    report_path.write_text(report, encoding="utf-8")
    if evidence is not None:
        (tmp_path / "critical-analysis-example.evidence.md").write_text(
            evidence, encoding="utf-8"
        )
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        status = check_report.main([str(report_path)])
    return status, out.getvalue()


def test_the_template_built_pair_passes(tmp_path):
    status, out = run(build_report(), build_evidence(), tmp_path)
    assert status == 0, out


def test_the_shipped_templates_carry_the_checker_tokens():
    """The key line and the pending device live in the templates; the checker
    requires them in the filled files. If the template drops one, every run
    fails at stage 6 with no way to comply."""
    report_template = check_report.REPORT_TEMPLATE.read_text(encoding="utf-8")
    assert "\nKey: " in report_template
    evidence_template = check_report.EVIDENCE_TEMPLATE.read_text(encoding="utf-8")
    assert "- N1:" in evidence_template
    for text in (report_template, evidence_template):
        assert "pending: stage" in text


def _drop_heading(report: str) -> str:
    return report.replace("### 1.4 Motivation\n", "")


def _empty_section(report: str) -> str:
    return report.replace(
        "### 1.4 Motivation\nFilled in prose; see Section 2 of the paper.",
        "### 1.4 Motivation\n",
    )


def _leftover_placeholder(report: str) -> str:
    return report.replace("Written 2026-10-04.", "Written {{date}}.")


def _topic_without_evidence(report: str) -> str:
    return report.replace(
        "### Importance\n"
        "Verdict: the paper holds on this dimension (Table 2; N1). J1 bears here.",
        "### Importance\nVerdict: fine, broadly speaking.",
    )


def _no_confidence(report: str) -> str:
    return report.replace(
        " Confidence: medium; an independent replication would raise it.", ""
    )


def _missing_coverage_line(report: str) -> str:
    return report.replace("- Not checked: none; checked: the whole run.\n", "")


def _derived_without_id(report: str) -> str:
    return report.replace(
        "The rate is 4.2 per day, derived, from C1.",
        "The rate is 4.2 per day, derived from the tables.",
    )


def _missing_key(report: str) -> str:
    return report.replace(KEY_LINE + "\n", "")


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (_drop_heading, "missing heading"),
        (_empty_section, "empty section"),
        (_leftover_placeholder, "placeholder"),
        (_topic_without_evidence, "no locator"),
        (_no_confidence, "confidence"),
        (_missing_coverage_line, "Not checked"),
        (_derived_without_id, "derived"),
        (_missing_key, "provenance key"),
    ],
)
def test_each_report_rule_fails_its_fixture(tmp_path, mutate, expected):
    status, out = run(mutate(build_report()), build_evidence(), tmp_path)
    assert status == 1
    assert expected in out


def test_an_unused_evidence_id_breaks_the_ledger(tmp_path):
    evidence = build_evidence().replace(
        "- N1: consent wording; needed by Claim 1.",
        "- N1: consent wording; needed by Claim 1.\n- N9: never cited anywhere.",
    )
    status, out = run(build_report(), evidence, tmp_path)
    assert status == 1
    assert "N9" in out
    assert "ledger" in out


def test_a_dangling_report_id_breaks_the_ledger(tmp_path):
    report = build_report().replace("(Table 2; N1)", "(Table 2; N1; W7)", 1)
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 1
    assert "W7" in out
    assert "ledger" in out


def test_a_missing_evidence_file_is_an_error(tmp_path):
    status, out = run(build_report(), None, tmp_path)
    assert status == 1
    assert "evidence" in out
    assert "not found" in out


def test_a_missing_evidence_heading_is_an_error(tmp_path):
    evidence = build_evidence().replace("## Stage log\n", "")
    status, out = run(build_report(), evidence, tmp_path)
    assert status == 1
    assert "missing heading" in out


def test_an_unfilled_mandated_check_slot_is_an_error(tmp_path):
    """Run F: a mandated check that silently never ran was invisible because
    the list had no slot-by-slot accounting. The slots make it a hole."""
    evidence = build_evidence().replace("- Tree forward: W1.\n", "")
    status, out = run(build_report(), evidence, tmp_path)
    assert status == 1
    assert "Tree forward" in out
    assert "slot" in out


@pytest.mark.parametrize(
    "replacement",
    [
        "The rate is 4.2 per day, derived from p. 4 (C1).",
        "The rate is 4.2 per day, derived (see pp. 12-13, C1).",
    ],
)
def test_a_locator_abbreviation_does_not_end_a_derived_sentence(tmp_path, replacement):
    """Locator abbreviations like p., pp., Fig., Eq. do not end a sentence."""
    report = build_report().replace(
        "The rate is 4.2 per day, derived, from C1.", replacement
    )
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 0, out


def test_a_sentence_split_at_a_real_period_flagged_derived(tmp_path):
    """A period that is not part of a locator abbreviation does end a sentence;
    if that sentence has 'derived' but no C/W/J, it fails."""
    report = build_report().replace(
        "The rate is 4.2 per day, derived, from C1.",
        "The rate is 4.2 per day, derived from p. 4. C1 holds it.",
    )
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 1
    assert "derived number cites no C, W or J entry" in out


def _swap(text: str, old: str, new: str) -> str:
    """Replace ``old`` with ``new``, failing if ``old`` is absent, so a fixture
    that stopped matching cannot pass by changing nothing."""
    assert old in text, f"fixture text not found: {old!r}"
    return text.replace(old, new)


IMPORTANCE = "### Importance\n" + _topic_body("### Importance")
CONFIDENCE = "Confidence: medium; an independent replication would raise it."
RATE = "The rate is 4.2 per day, derived, from C1."


def test_a_participant_label_is_not_a_ledger_citation(tmp_path):
    """Bloom labels its participants P1-P54 and reports quote them; a judge
    point prefix of P made every such quote a ledger citation."""
    report = _swap(
        build_report(),
        "CORE ranks it (W1).",
        "CORE ranks it (W1). Participant P14 said the coach felt human (Section 5).",
    )
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 0, out


def _template_only(path: Path) -> str:
    """The template below its first thematic break with every placeholder
    filled: what a run that copied the template and filled nothing else
    would hand the checker."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if check_report.BREAK_RE.match(line))
    return re.sub(r"\{\{[^}]*\}\}", "Example", "\n".join(lines[start + 1 :]) + "\n")


def test_a_template_only_pair_fails(tmp_path):
    status, out = run(
        _template_only(check_report.REPORT_TEMPLATE),
        _template_only(check_report.EVIDENCE_TEMPLATE),
        tmp_path,
    )
    assert status == 1
    assert "empty section" in out
    assert "slot is unfilled" in out


def test_an_emptied_slot_is_an_error(tmp_path):
    evidence = _swap(build_evidence(), "- Tree forward: W1.", "- Tree forward:")
    status, out = run(build_report(), evidence, tmp_path)
    assert status == 1
    assert "Tree forward" in out
    assert "unfilled" in out


def test_an_emptied_coverage_line_is_an_error(tmp_path):
    report = _swap(
        build_report(), "- Not checked: none; checked: the whole run.", "- Not checked:"
    )
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 1
    assert "Not checked" in out
    assert "unfilled" in out


def test_a_slot_citing_an_undefined_id_is_an_error(tmp_path):
    evidence = _swap(build_evidence(), "- Tree forward: W1.", "- Tree forward: W9.")
    status, out = run(build_report(), evidence, tmp_path)
    assert status == 1
    assert "Tree forward" in out
    assert "W9" in out


def test_a_left_in_preamble_is_an_error(tmp_path):
    report = (
        "# Report template\n\nGuidance.\n\n"
        "______________________________________________________________________\n\n"
    ) + build_report()
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 1
    assert "preamble" in out


def test_guidance_left_beside_content_still_passes(tmp_path):
    """Template text is not content, but it does not cancel the content
    beside it."""
    template = check_report.EVIDENCE_TEMPLATE.read_text(encoding="utf-8")
    guidance = template.split("## Stage log\n\n", 1)[1].split("\n", 1)[0]
    filled = "## Stage log\nFilled; pending sections read pending: stage 7."
    evidence = _swap(build_evidence(), filled, f"{filled}\n{guidance}")
    status, out = run(build_report(), evidence, tmp_path)
    assert status == 0, out


@pytest.mark.parametrize(
    "verdict",
    [
        "Verdict: not assessable from the paper, since no claim of importance is made.",
        "Verdict: the motivation is absent (whole paper).",
        "Verdict: the framing oversells (abstract).",
    ],
)
def test_the_skills_own_vocabulary_satisfies_the_topic_rule(tmp_path, verdict):
    """judge.md writes "not assessable from the paper"; SKILL.md's Locators
    section makes the front-matter parts and "whole paper" locators. N1 and
    J1 stay cited by the other topics, so the ledger stays closed."""
    report = _swap(build_report(), IMPORTANCE, f"### Importance\n{verdict}")
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 0, out


def test_a_lowercased_topic_heading_is_still_a_topic(tmp_path):
    """The structure check matches headings case-insensitively, so the topic
    rule must too, or a lowercased heading escapes it."""
    report = _swap(
        build_report(), IMPORTANCE, "### importance\nVerdict: fine, broadly speaking."
    )
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 1
    assert "no locator" in out


def test_a_fenced_code_comment_is_not_a_heading(tmp_path):
    fence = "```python\n# recompute H1\nprint(4.2)\n```"
    evidence = _swap(
        build_evidence(), "\n\n## Judge points", f"\n\n{fence}\n\n## Judge points"
    )
    headings = [
        heading for _, heading, _ in check_report.sections(evidence.splitlines())
    ]
    assert "# recompute H1" not in headings
    status, out = run(build_report(), evidence, tmp_path)
    assert status == 0, out


def test_a_confidence_interval_is_not_a_confidence_level(tmp_path):
    report = _swap(
        build_report(),
        CONFIDENCE,
        "The 95% confidence interval is wide because power is low.",
    )
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 1
    assert "confidence" in out


@pytest.mark.parametrize(
    "sentence",
    [
        "confidence is low; a replication would raise it.",
        "Confidence level: high; a replication would lower it.",
        "Our confidence remains medium; a replication would raise it.",
        "We hold medium confidence; a replication would raise it.",
    ],
)
def test_a_stated_confidence_level_passes(tmp_path, sentence):
    report = _swap(build_report(), CONFIDENCE, sentence)
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 0, out


def test_a_table_header_naming_a_derived_column_is_exempt(tmp_path):
    report = _swap(
        build_report(),
        "CORE ranks it (W1).",
        "CORE ranks it (W1).\n\n| Reported | Derived |\n| --- | --- |\n| 4.4 | 4.2 (C1) |",
    )
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 0, out


def test_a_table_data_row_is_still_checked(tmp_path):
    report = _swap(
        build_report(),
        "CORE ranks it (W1).",
        "CORE ranks it (W1).\n\n| Reported | Value |\n| --- | --- |\n"
        "| 4.4 | 4.2, derived |",
    )
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 1
    assert "derived" in out


@pytest.mark.parametrize(
    "replacement",
    [
        "The rate is 4.2 per day, derived; cf. C1.",
        "The rate is 4.2 per day, derived vs. 4.4 reported (C1).",
        "The rate is 4.2 per day, derived from Sec. 4 (C1).",
        "The rate is 4.2 per day, derived from Tab. 2 (C1).",
    ],
)
def test_more_abbreviations_do_not_end_a_derived_sentence(tmp_path, replacement):
    report = _swap(build_report(), RATE, replacement)
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 0, out
