"""The §10 status-marking pass: the module's unit tests, then the standing linter."""

from pathlib import Path

import pytest

from scripts import dispositions

ROOT = Path(__file__).resolve().parents[1]


def test_scope_excludes_the_four_named_surfaces():
    scope = dispositions.in_scope(ROOT)
    assert "docs/testing.md" in scope
    assert ".superpowers/sdd/2026-08-22-post-q-batch/task-1-brief.md" in scope
    assert "skills/find-sources/SKILL.md" in scope, (
        "the vendoring decision is repo-owned"
    )
    assert "CLAUDE.md" not in scope, "§10 exempts CLAUDE.md by name"
    assert not [p for p in scope if p.startswith("research_vault/templates/")]
    assert not [p for p in scope if p.startswith(".out-of-scope/")]
    assert not [p for p in scope if p.startswith("skills/find-sources/references/")]


def test_every_vendored_file_stays_out_of_scope():
    """Their own header says do not hand-edit; tests/test_find_sources_vendor.py:210."""
    vendored = [
        p
        for p in dispositions.in_scope(ROOT)
        if "Do not hand-edit" in (ROOT / p).read_text(encoding="utf-8")[:600]
    ]
    assert not vendored, f"marking would drift these against upstream: {vendored}"


def test_anchor_is_the_line_after_the_first_heading():
    assert dispositions.anchor(["# Title", "", "Body"]) == 1


def test_anchor_takes_a_heading_of_any_level():
    """21 in-scope files open at `###` — the sdd task briefs."""
    assert dispositions.anchor(["### Task 1: Rename", "", "Body"]) == 1
    assert dispositions.anchor(["## Section", "", "# Later", ""]) == 1


def test_anchor_falls_back_to_the_top_for_the_four_headingless_files():
    assert dispositions.anchor(["Raw transcripts live here.", "", "Body"]) == 0


def test_anchor_ignores_a_hash_line_inside_a_fence():
    lines = ["```bash", "# not a heading", "```", "", "# Title", ""]
    assert dispositions.anchor(lines) == 5


def test_read_marker_returns_none_when_unmarked():
    assert (
        dispositions.read_marker("# Title\n\nStatus: accepted (2026-08-20)\n") is None
    )


def test_read_marker_reads_value_argument_date_and_flag():
    text = (
        "# Title\n\nDisposition: pending-issue: 116 (2026-09-05)\n\nStatus: suspended\n"
    )
    assert dispositions.read_marker(text) == dispositions.Marker(
        "pending-issue", "116", "2026-09-05", False
    )


def test_read_marker_reads_the_orthogonal_flag():
    text = (
        "# Title\n\nDisposition: historical (2026-09-05) [should-be-scoping-review]\n"
    )
    marker = dispositions.read_marker(text)
    assert (marker.value, marker.flag) == ("historical", True)


def test_read_marker_reads_the_third_level_anchor():
    text = "### Task 1: Rename\n\nDisposition: historical (2026-09-05)\n\nRuled 2026-08-22.\n"
    assert dispositions.read_marker(text).value == "historical"


def test_read_marker_reads_the_headingless_fallback_anchor():
    text = "Disposition: historical (2026-09-05)\n\nRaw transcripts live here.\n"
    assert dispositions.read_marker(text).value == "historical"


def test_read_marker_ignores_a_status_line_and_a_body_disposition():
    """The six sdd review files carry `Status: **CONFIRMED.**` per finding."""
    text = (
        "# Title\n\nStatus: **CONFIRMED.**\n\n"
        + "\n" * 20
        + "Disposition: current (2026-09-05)\n"
    )
    assert dispositions.read_marker(text) is None


def test_read_marker_rejects_two_lines_in_the_window():
    text = (
        "# T\n\nDisposition: current (2026-09-05)\n"
        "Disposition: historical (2026-09-05)\n"
    )
    with pytest.raises(dispositions.MarkerError):
        dispositions.read_marker(text)


def test_read_marker_rejects_an_off_vocabulary_value():
    with pytest.raises(dispositions.MarkerError):
        dispositions.read_marker("# T\n\nDisposition: retired (2026-09-05)\n")


def test_read_marker_rejects_a_missing_argument():
    with pytest.raises(dispositions.MarkerError):
        dispositions.read_marker("# T\n\nDisposition: pending-issue (2026-09-05)\n")


def test_read_marker_rejects_an_argument_the_value_forbids():
    with pytest.raises(dispositions.MarkerError):
        dispositions.read_marker("# T\n\nDisposition: current: 116 (2026-09-05)\n")
