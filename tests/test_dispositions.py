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


def test_proposal_prefers_sibling_project_over_every_later_rule():
    """Double fit: this file also declares SUPERSEDED in its header window."""
    path = "docs/2026-08-31-proposed-adr-software-development-component-seam.md"
    proposal = dispositions.propose(path, "# Seam\n\nStatus: **SUPERSEDED.**\n")
    assert proposal.value == "sibling-project"


def test_proposal_prefers_superseded_over_historical():
    """Double fit: a closed-workspace path that also declares supersession."""
    path = ".superpowers/sdd/2026-08-22-post-q-batch/task-7-report.md"
    proposal = dispositions.propose(path, "# Task 7\n\nStatus: **SUPERSEDED.**\n")
    assert (proposal.value, proposal.argument) == ("superseded-by", "?")


def test_proposal_prefers_the_named_issue_over_current():
    """Double fit: ADR 0004 matches `docs/adr/` AND is owned by issue #116.

    Both rules genuinely fire on this path — drop the precedence order and the
    answer flips to `current`, which is the discrimination this test exists for.
    """
    path = "docs/adr/0004-citekey-is-the-only-identity.md"
    text = (
        "# The citekey is the vault's only identity\n\nStatus: suspended (2026-09-03)\n"
    )
    proposal = dispositions.propose(path, text)
    assert (proposal.value, proposal.argument) == ("pending-issue", "116")
    # The `current` rule really is reachable for this path, so the assertion
    # above is precedence deciding and not one rule matching alone.
    assert path.startswith(dispositions._CURRENT_PREFIXES)


def test_proposal_keeps_the_unsuspended_adrs_current():
    path = "docs/adr/0001-vault-outlives-its-tools.md"
    text = "# The vault outlives its tools\n\nStatus: accepted (2026-08-20)\n"
    assert dispositions.propose(path, text).value == "current"


def test_proposal_marks_the_closed_sdd_workspace_historical():
    path = ".superpowers/sdd/2026-08-22-post-q-batch/task-1-brief.md"
    assert dispositions.propose(path, "### Task 1: Rename\n").value == "historical"


def test_proposal_marks_shipped_surfaces_current():
    skill = "---\nname: publish\n---\n\n# Publish a project\n"
    assert dispositions.propose("skills/publish/SKILL.md", skill).value == "current"
    assert (
        dispositions.propose("docs/agents/issue-tracker.md", "# Issue tracker\n").value
        == "current"
    )
    assert dispositions.propose("AGENTS.md", "# research-vault\n").value == "current"
    assert (
        dispositions.propose("docs/testing.md", "# Testing instruments\n").value
        == "current"
    )


def test_proposal_keeps_this_spec_current_and_defaults_the_rest_to_pending_map():
    spec = "docs/superpowers/specs/2026-09-05-assembly-design.md"
    assert (
        dispositions.propose(spec, "# research-vault as an assembly\n").value
        == "current"
    )
    demoted = "docs/superpowers/specs/2026-08-16-foundation-spec.md"
    proposal = dispositions.propose(demoted, "# Foundation spec\n")
    assert (proposal.value, proposal.rule) == ("pending-map", "residual")


def test_the_scoping_review_flag_is_orthogonal_to_the_value():
    path = (
        "docs/research/harness-audits/2026-08-30-installed-asset-disposition-survey.md"
    )
    proposal = dispositions.propose(path, "# Installed asset disposition survey\n")
    assert (proposal.value, proposal.flag) == ("historical", True)


def test_a_body_supersession_does_not_fire_the_header_rule():
    """task-21-report says SUPERSEDED twice, both far below the window."""
    path = ".superpowers/sdd/2026-08-22-post-q-batch/task-21-report.md"
    text = (
        "# Task 21 report\n\nStatus: **complete**\n"
        + "\n" * 40
        + "**SUPERSEDED by Fix Round 1**\n"
    )
    assert dispositions.propose(path, text).value == "historical"


def test_every_proposal_value_is_in_the_closed_vocabulary():
    for path in dispositions.in_scope(ROOT):
        proposal = dispositions.propose(path, (ROOT / path).read_text(encoding="utf-8"))
        assert proposal.value in dispositions.DOCUMENT_VALUES, path
        assert proposal.rule, f"{path}: proposal carries no rule name"


def test_emit_writes_a_header_and_one_row_per_in_scope_file():
    text = dispositions.emit(ROOT)
    lines = text.rstrip("\n").split("\n")
    assert lines[0] == dispositions.HEADER
    assert len(lines) - 1 == len(dispositions.in_scope(ROOT))
    assert all(line.count("\t") == 5 for line in lines)


def test_emit_round_trips_through_parse_rows():
    rows = dispositions.parse_rows(dispositions.emit(ROOT))
    assert [row.key for row in rows] == dispositions.in_scope(ROOT)
    adr = next(
        row for row in rows if row.key.endswith("0004-citekey-is-the-only-identity.md")
    )
    assert (adr.value, adr.argument) == ("pending-issue", "116")
    # `spec-named-issue` before Task 5 marks the corpus, `existing` after it.
    assert adr.rule in ("spec-named-issue", "existing")


def test_emit_keeps_a_marker_the_author_already_approved():
    """Re-running propose over a reviewed corpus must not undo the review."""
    path, text = (
        "docs/product-landscape/zotero.md",
        "# Zotero\n\nDisposition: current (2026-09-05)\n",
    )
    assert dispositions.propose(path, text).value == "pending-map"
    assert dispositions.propose_or_existing(path, text) == dispositions.Proposal(
        "current", "", False, "existing"
    )


def test_parse_rows_reads_the_flag_column_as_a_boolean():
    text = (
        dispositions.HEADER
        + "\ndocs/a.md\thistorical\t\tshould-be-scoping-review\tclosed-pass-path\t"
        + "\ndocs/b.md\tcurrent\t\t\tshipped-surface\t\n"
    )
    rows = dispositions.parse_rows(text)
    assert [row.flag for row in rows] == [True, False]


def test_parse_rows_rejects_an_off_vocabulary_flag_column():
    text = (
        dispositions.HEADER + "\ndocs/a.md\thistorical\t\tmaybe\tclosed-pass-path\t\n"
    )
    with pytest.raises(dispositions.MarkerError):
        dispositions.parse_rows(text)


def test_propose_subcommand_writes_the_file(tmp_path, capsys):
    target = tmp_path / "proposal.tsv"
    assert dispositions.main(["propose", "--out", str(target)]) == 0
    assert target.read_text(encoding="utf-8").startswith(dispositions.HEADER)
    assert "rows" in capsys.readouterr().out
