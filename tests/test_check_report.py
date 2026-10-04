"""check_report.py enforces the report rules the spec lists; the templates are
its single source of truth for structure.

The passing fixture is BUILT FROM THE SHIPPED TEMPLATES through the checker's
own heading parser, so a template edit that breaks agreement fails here rather
than in a live run. Each spec rule then gets one failing mutation.
"""

import contextlib
import importlib.util
import io
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
    'a number marked "derived" cites the C, W or P entry holding its '
    "computation; recalled knowledge appears only under Coverage."
)


def _topic_body(heading: str) -> str:
    body = "Verdict: the paper holds on this dimension (Table 2; N1). P1 bears here."
    if heading.startswith("### Credibility"):
        body += " Confidence: medium; an independent replication would raise it."
    return body


def _coverage_body() -> str:
    leads = check_report.coverage_leads()
    lines = []
    for lead in leads:
        if lead == "Evidence file only":
            lines.append(f"- {lead}: P2.")
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
                "- P1: Not reported; Table 2; no denominator; N1; weakens the rate."
            )
            lines.append(
                "- P2: Not reported; Section 5; minor wording slip; C1; low stakes."
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
        "Verdict: the paper holds on this dimension (Table 2; N1). P1 bears here.",
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
    if that sentence has 'derived' but no C/W/P, it fails."""
    report = build_report().replace(
        "The rate is 4.2 per day, derived, from C1.",
        "The rate is 4.2 per day, derived from p. 4. C1 holds it.",
    )
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 1
    assert "derived number cites no C, W or P entry" in out
