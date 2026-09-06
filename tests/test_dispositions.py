"""The §10 status-marking pass: the module's unit tests, then the standing linter."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts import dispositions

ROOT = Path(__file__).resolve().parents[1]


def test_nothing_that_ships_to_a_consumer_is_in_scope():
    """One test governs the exclusion list: does this path ship to a consumer?"""
    scope = dispositions.in_scope(ROOT)
    assert "docs/testing.md" in scope
    assert ".superpowers/sdd/2026-08-22-post-q-batch/task-1-brief.md" in scope
    assert dispositions.ISSUE_TABLE in scope, "the table the pass writes is a document"
    assert "CLAUDE.md" not in scope, "§10 exempts CLAUDE.md by name"
    assert not [p for p in scope if p.startswith("research_vault/templates/")], (
        "ships into a user's vault"
    )
    assert not [p for p in scope if p.startswith("skills/")], (
        "ships in the installed plugin, where a SKILL.md body is read as instruction"
    )
    assert not [p for p in scope if p.startswith(".out-of-scope/")]


def test_no_skill_body_opens_with_repo_bookkeeping():
    """A skill is a prompt. The marker would be its first instruction line."""
    marked = [
        path
        for path in subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "--", "skills/*.md"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
        if "\nDisposition: " in (ROOT / path).read_text(encoding="utf-8")
    ]
    assert not marked, f"repo bookkeeping shipped into the plugin surface: {marked}"


def test_every_vendored_file_stays_out_of_scope():
    """Their own header says do not hand-edit; tests/test_find_sources_vendor.py:210."""
    vendored = [
        p
        for p in dispositions.in_scope(ROOT)
        if "Do not hand-edit" in (ROOT / p).read_text(encoding="utf-8")[:600]
    ]
    assert not vendored, f"marking would drift these against upstream: {vendored}"


def test_no_document_in_scope_opens_with_yaml_frontmatter():
    """The frontmatter anchor class retired with `skills/`: it held only SKILL.md.

    `anchor()` reaches a heading below a frontmatter block either way, so this
    is not a capability the module lost — it is a class of document the corpus
    no longer contains, asserted so the claim stays true rather than remembered.
    """
    with_frontmatter = [
        path
        for path in dispositions.in_scope(ROOT)
        if (ROOT / path).read_text(encoding="utf-8").startswith("---\n")
    ]
    assert not with_frontmatter, with_frontmatter


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


def test_the_fence_scanner_reads_an_indented_fence():
    """CommonMark allows up to three spaces; five in-scope files use them."""
    lines = ["  ```bash", "# not a heading", "  ```", "", "# Title", ""]
    assert dispositions.unfenced(lines) == [False, False, False, True, True, True]
    assert dispositions.anchor(lines) == 5


def test_the_fence_scanner_needs_a_closer_of_the_same_length_and_character():
    """A four-backtick block survives the three-backtick fences inside it."""
    lines = ["````python", "```", "# not a heading", "```", "````", "# Title"]
    assert dispositions.unfenced(lines) == [False] * 5 + [True]
    assert dispositions.anchor(lines) == 6
    # Same length, wrong character: a tilde does not close a backtick fence.
    assert dispositions.unfenced(["```", "~~~", "# no", "```", "# Title"]) == [
        False,
        False,
        False,
        False,
        True,
    ]


def test_the_fence_scanner_closes_on_a_longer_fence():
    """`>= opener`, not `== opener`: CommonMark lets the closer be longer."""
    assert dispositions.unfenced(["```", "code", "`````", "# Title"]) == [
        False,
        False,
        False,
        True,
    ]


def test_displaced_markers_finds_the_one_the_window_hides():
    """The linter's zero means something only if a non-zero is reachable."""
    text = "# T\n\nBody.\n\n\n\n\nDisposition: current (2026-09-06)\n"
    lines = text.split("\n")
    assert dispositions.read_marker(text) is None
    assert dispositions.displaced_markers(lines) == [7]
    # In the window, and so not displaced.
    assert (
        dispositions.displaced_markers(
            ["# T", "", "Disposition: current (2026-09-06)", ""]
        )
        == []
    )
    # Fenced: an example quoted in prose, not a marker.
    assert (
        dispositions.displaced_markers(
            ["# T", "", "Body.", "", "```", "Disposition: current (2026-09-06)", "```"]
        )
        == []
    )


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


def test_proposal_marks_the_binding_surfaces_current():
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


def test_propose_or_existing_lets_a_marker_beat_the_classifier():
    path, text = (
        "docs/product-landscape/zotero.md",
        "# Zotero\n\nDisposition: current (2026-09-05)\n",
    )
    assert dispositions.propose(path, text).value == "pending-map"
    assert dispositions.propose_or_existing(path, text) == dispositions.Proposal(
        "current", "", False, "existing"
    )


def test_emit_keeps_what_the_author_already_approved(tmp_path):
    """The human gate, exercised through `emit` — for BOTH halves.

    The earlier version of this test never called `emit`: the one test guarding
    the gate did not exercise the gate, and the issue half had no protection at
    all. Re-running `propose --issues-json` against the reviewed table reverted
    42 of 66 values and overwrote 57 notes (measured 2026-09-06).
    """
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "docs").mkdir()
    # A document the classifier calls `pending-map`, marked `current` by review.
    (tmp_path / "docs" / "zotero.md").write_text(
        "# Zotero\n\nDisposition: current (2026-09-05)\n", encoding="utf-8"
    )
    # An issue the classifier calls `pending-map`, ruled `still-open` by review.
    assert dispositions.propose_issue(94).value == "pending-map"
    (tmp_path / dispositions.ISSUE_TABLE).write_text(
        dispositions.render_issue_table(
            [
                dispositions.Row(
                    "issue:94", "still-open", "", False, "r", "the author's reason"
                )
            ],
            date="2026-09-05",
            titles={"issue:94": "Implement the one-source glossary"},
        ),
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", "--", "docs/zotero.md", dispositions.ISSUE_TABLE],
        cwd=tmp_path,
        check=True,
    )

    text = dispositions.emit(
        tmp_path,
        issues=[{"number": 94, "title": "Implement the one-source glossary"}],
    )

    rows = {row.key: row for row in dispositions.parse_rows(text)}
    assert rows["docs/zotero.md"].value == "current"
    assert rows["docs/zotero.md"].rule == "existing"
    assert rows["issue:94"].value == "still-open"
    assert rows["issue:94"].rule == "existing"
    assert rows["issue:94"].note == "the author's reason", (
        "the reviewed reason is the record; the GitHub title must not overwrite it"
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


def test_marker_line_renders_every_shape():
    assert dispositions.marker_line("current", "", False, "2026-09-05") == (
        "Disposition: current (2026-09-05)"
    )
    assert dispositions.marker_line("pending-issue", "116", False, "2026-09-05") == (
        "Disposition: pending-issue: 116 (2026-09-05)"
    )
    assert dispositions.marker_line("historical", "", True, "2026-09-05") == (
        "Disposition: historical (2026-09-05) [should-be-scoping-review]"
    )


def test_marker_line_rejects_a_row_the_reader_would_reject():
    with pytest.raises(dispositions.MarkerError):
        dispositions.marker_line("pending-issue", "", False, "2026-09-05")
    with pytest.raises(dispositions.MarkerError):
        dispositions.marker_line("retired", "", False, "2026-09-05")


@pytest.mark.parametrize("date", ["2026-9-6", "26-09-06", "2026/09/06", "", "today"])
def test_marker_line_rejects_a_date_the_reader_would_reject(date):
    """`apply --date 2026-9-6` rewrote every document, exit 0, unreadable after.

    The vocabulary checks never looked at SHAPE, so the one grammar the reader
    uses is now the one the writer validates against.
    """
    with pytest.raises(dispositions.MarkerError, match="read_marker rejects"):
        dispositions.marker_line("current", "", False, date)


@pytest.mark.parametrize(
    "argument", ["docs/a b.md", "116 ", "with\ttab", "trailing garbage"]
)
def test_marker_line_rejects_an_argument_that_would_not_read_back(argument):
    """`\\S+` in the grammar: whitespace in the target ends the marker early."""
    with pytest.raises(dispositions.MarkerError, match="read_marker rejects"):
        dispositions.marker_line("superseded-by", argument, False, "2026-09-05")


@pytest.mark.parametrize(
    "line",
    [
        "Disposition: current (2026-9-6)",
        "Disposition: current 2026-09-06",
        "Disposition: current (2026-09-06) trailing garbage",
        "Disposition: current (2026-09-06) [should-be-scoping-reveiw]",
        "Disposition: current (2026-09-06) [SHOULD-BE-SCOPING-REVIEW]",
        "Disposition: current",
    ],
)
def test_read_marker_rejects_a_malformed_line(line):
    """A marker that exists but does not parse is an error, never a None."""
    with pytest.raises(dispositions.MarkerError, match="unparsable"):
        dispositions.read_marker(f"# T\n\n{line}\n")


def test_apply_marker_inserts_a_paragraph_after_the_heading():
    text = "# The vault outlives its tools\n\nStatus: accepted (2026-08-20)\n\nBody.\n"
    out = dispositions.apply_marker(text, "Disposition: current (2026-09-05)")
    assert out == (
        "# The vault outlives its tools\n\n"
        "Disposition: current (2026-09-05)\n\n"
        "Status: accepted (2026-08-20)\n\nBody.\n"
    )
    assert dispositions.read_marker(out).value == "current"


def test_apply_marker_inserts_after_a_third_level_heading():
    text = "### Task 1: Rename\n\nRuled 2026-08-22.\n"
    out = dispositions.apply_marker(text, "Disposition: historical (2026-09-05)")
    assert out == (
        "### Task 1: Rename\n\nDisposition: historical (2026-09-05)\n\nRuled 2026-08-22.\n"
    )


def test_apply_marker_inserts_at_the_top_of_a_headingless_file():
    text = "Raw transcripts live here.\n\nBody.\n"
    out = dispositions.apply_marker(text, "Disposition: historical (2026-09-05)")
    assert (
        out
        == "Disposition: historical (2026-09-05)\n\nRaw transcripts live here.\n\nBody.\n"
    )


def test_apply_marker_is_idempotent_and_replaces_in_place():
    text = "# T\n\nStatus: accepted (2026-08-20)\n"
    once = dispositions.apply_marker(text, "Disposition: current (2026-09-05)")
    twice = dispositions.apply_marker(once, "Disposition: current (2026-09-05)")
    assert once == twice
    changed = dispositions.apply_marker(once, "Disposition: historical (2026-09-05)")
    assert dispositions.read_marker(changed).value == "historical"
    assert changed.count("Disposition: ") == 1


def test_apply_marker_moves_a_displaced_marker_rather_than_adding_a_second():
    """A marker below the window reads as ABSENT, so inserting would duplicate.

    Two markers can then disagree while the linter — which also reads only the
    window — passes. Moving keeps the count at one.
    """
    text = "# T\n\nStatus: accepted (2026-08-20)\n\nBody.\n\nDisposition: historical (2026-09-05)\n\nMore body.\n"
    assert dispositions.read_marker(text) is None, "the premise: it reads as absent"

    out = dispositions.apply_marker(text, "Disposition: current (2026-09-06)")

    assert out.count("Disposition: ") == 1
    assert dispositions.read_marker(out).value == "current"
    assert out == (
        "# T\n\nDisposition: current (2026-09-06)\n\n"
        "Status: accepted (2026-08-20)\n\nBody.\n\nMore body.\n"
    )
    assert dispositions.apply_marker(out, "Disposition: current (2026-09-06)") == out


def test_apply_marker_leaves_a_fenced_disposition_example_alone():
    """This repository's own plan quotes the table preamble inside a fence."""
    text = (
        "# T\n\nBody.\n\n````python\n"
        '_TABLE_PREAMBLE = """# Issue dispositions\n\n'
        "Disposition: current (%(date)s)\n"
        '"""\n````\n'
    )
    out = dispositions.apply_marker(text, "Disposition: current (2026-09-06)")
    assert "Disposition: current (%(date)s)" in out
    assert out == "# T\n\nDisposition: current (2026-09-06)\n\n" + text.removeprefix(
        "# T\n\n"
    )


def test_applying_the_marker_the_plan_already_carries_changes_nothing():
    """The live file, fenced example and all: a re-sweep must be a no-op."""
    path = ROOT / "docs/superpowers/plans/2026-09-05-status-marking-pass.md"
    text = path.read_text(encoding="utf-8")
    marker = dispositions.read_marker(text)
    line = dispositions.marker_line(
        marker.value, marker.argument, marker.flag, marker.date
    )
    assert dispositions.apply_marker(text, line) == text


def test_apply_marker_never_touches_the_status_line():
    text = "# The citekey\n\nStatus: suspended (2026-09-03) — under re-derivation.\n"
    out = dispositions.apply_marker(
        text, "Disposition: pending-issue: 116 (2026-09-05)"
    )
    assert "Status: suspended (2026-09-03) — under re-derivation." in out


def test_apply_rows_writes_only_the_rows_it_is_given(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("# A\n\nBody.\n", encoding="utf-8")
    (tmp_path / "docs" / "b.md").write_text("# B\n\nBody.\n", encoding="utf-8")
    rows = [dispositions.Row("docs/a.md", "current", "", False, "shipped-surface", "")]
    written = dispositions.apply_rows(rows, root=tmp_path, date="2026-09-05")
    assert written == ["docs/a.md"]
    assert "Disposition: " in (tmp_path / "docs" / "a.md").read_text(encoding="utf-8")
    assert "Disposition: " not in (tmp_path / "docs" / "b.md").read_text(
        encoding="utf-8"
    )


def test_apply_rows_rejects_an_unreviewed_superseded_placeholder(tmp_path):
    """The `?` the classifier emits must never reach a file. Fails in marker_line."""
    (tmp_path / "a.md").write_text("# A\n", encoding="utf-8")
    rows = [
        dispositions.Row("a.md", "superseded-by", "?", False, "header-superseded", "")
    ]
    with pytest.raises(dispositions.MarkerError):
        dispositions.apply_rows(rows, root=tmp_path, date="2026-09-05")


def test_apply_rows_rejects_a_superseded_target_that_does_not_resolve(
    tmp_path, monkeypatch
):
    """The tracked guard runs only when root is ROOT, so ROOT is the tmp repo here.

    Without this, the guard protecting the live sweep from a typo'd target is
    never executed by any test: every other test passes a tmp root, which sets
    `tracked` to None and skips the branch entirely.
    """
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "a.md").write_text("# A\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("# B\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.md", "b.md"], cwd=tmp_path, check=True)
    monkeypatch.setattr(dispositions, "ROOT", tmp_path)

    resolves = [
        dispositions.Row(
            "a.md", "superseded-by", "b.md", False, "header-superseded", ""
        )
    ]
    assert dispositions.apply_rows(resolves, root=tmp_path, date="2026-09-05") == [
        "a.md"
    ]

    typo = [
        dispositions.Row(
            "a.md", "superseded-by", "docs/typo.md", False, "header-superseded", ""
        )
    ]
    with pytest.raises(dispositions.MarkerError, match="does not resolve"):
        dispositions.apply_rows(typo, root=tmp_path, date="2026-09-05")


# ---------------------------------------------------------------------------
# The standing linter. Everything above tests the module; everything below
# tests the repository, per §10's rule that a mechanical process gets a
# mechanical check.
# ---------------------------------------------------------------------------


def _markers() -> dict[str, dispositions.Marker | None]:
    markers = {}
    for path in dispositions.in_scope(ROOT):
        try:
            markers[path] = dispositions.read_marker(
                (ROOT / path).read_text(encoding="utf-8")
            )
        except dispositions.MarkerError as error:
            # read_marker never sees a path; without this the linter's failure
            # says what is wrong and not which of two hundred files it is wrong in.
            raise dispositions.MarkerError(f"{path}: {error}") from error
    return markers


def test_every_in_scope_document_carries_exactly_one_marker():
    unmarked = sorted(path for path, marker in _markers().items() if marker is None)
    assert not unmarked, (
        f"{len(unmarked)} document(s) carry no Disposition line: {unmarked[:10]}"
    )


def test_no_in_scope_document_carries_a_marker_outside_its_window():
    """A second marker below the window is invisible to `read_marker` and here.

    So the linter would pass while two markers disagreed. Fenced lines are
    examples — this plan quotes the table preamble in a code block — and are
    not counted. Zero hits at 2026-09-06.
    """
    displaced = {
        path: [index + 1 for index in indices]
        for path in dispositions.in_scope(ROOT)
        if (
            indices := dispositions.displaced_markers(
                (ROOT / path).read_text(encoding="utf-8").split("\n")
            )
        )
    }
    assert not displaced, f"Disposition lines outside the anchor window: {displaced}"


def test_every_superseded_by_target_resolves():
    tracked = set(dispositions.in_scope(ROOT))
    broken = [
        (path, marker.argument)
        for path, marker in _markers().items()
        if marker and marker.value == "superseded-by" and marker.argument not in tracked
    ]
    assert not broken, f"superseded-by targets that do not resolve: {broken}"


def test_every_pending_issue_argument_is_an_issue_number():
    bad = [
        (path, marker.argument)
        for path, marker in _markers().items()
        if marker and marker.value == "pending-issue" and not marker.argument.isdigit()
    ]
    assert not bad, f"pending-issue arguments that are not issue numbers: {bad}"


# Issue disposition tests


def test_propose_issue_uses_the_spec_named_dispositions():
    assert dispositions.propose_issue(96) == dispositions.Proposal(
        "absorbed-by", "§6", False, "spec-named-absorbed"
    )
    assert dispositions.propose_issue(116).value == "still-open"
    assert dispositions.propose_issue(94) == dispositions.Proposal(
        "pending-map", "", False, "residual"
    )


def test_emit_appends_issue_rows_with_the_title_as_the_note():
    issues = [
        {"number": 96, "title": "Distribution model for the recommended plugin bucket"}
    ]
    rows = dispositions.parse_rows(dispositions.emit(ROOT, issues=issues))
    issue_rows = [row for row in rows if row.key.startswith("issue:")]
    assert len(issue_rows) == 1
    assert issue_rows[0].key == "issue:96"
    assert issue_rows[0].note == "Distribution model for the recommended plugin bucket"


def test_render_and_read_the_issue_table_round_trip():
    rows = [
        dispositions.Row(
            "issue:96",
            "absorbed-by",
            "§6",
            False,
            "spec-named-absorbed",
            "Distribution model",
        ),
        dispositions.Row(
            "issue:116",
            "still-open",
            "",
            False,
            "spec-named-open",
            "Land the vocabulary",
        ),
    ]
    titles = {"issue:96": "Distribution model for the recommended plugin bucket"}
    text = dispositions.render_issue_table(rows, titles=titles)
    assert text.startswith("# Issue dispositions\n")
    # The title renders from GitHub and is deliberately not read back — the Row's
    # own last field is the author's reason, which is what `Note` carries.
    assert "| 96 | Distribution model for the recommended plugin bucket |" in text
    assert "| 116 |  |" in text, (
        "a title GitHub does not supply renders empty, not absent"
    )
    # Highest number first, so regenerating the table never emits a diff that is
    # only row movement. The reversal here IS the sort under test.
    assert dispositions.read_issue_table(text) == [rows[1], rows[0]]


def test_render_issue_table_rejects_a_pipe_in_a_cell():
    """A `|` ends the cell, and the row would then vanish on read in silence."""
    rows = [
        dispositions.Row(
            "issue:96",
            "absorbed-by",
            "§6",
            False,
            "spec-named-absorbed",
            "Foo | Bar",
        )
    ]
    with pytest.raises(dispositions.MarkerError, match="pipe"):
        dispositions.render_issue_table(rows)


def test_render_issue_table_rejects_a_pipe_in_a_github_title():
    """Titles are GitHub's, not ours — nothing stops one carrying a pipe."""
    rows = [
        dispositions.Row(
            "issue:96", "still-open", "", False, "spec-named-open", "a reason"
        )
    ]
    with pytest.raises(dispositions.MarkerError, match="pipe"):
        dispositions.render_issue_table(rows, titles={"issue:96": "Fix a | b"})


def test_read_issue_table_tolerates_mdformat_column_padding():
    """mdformat pads table cells; render_issue_table does not. Measured 2026-09-05."""
    text = (
        "# Issue dispositions\n\n"
        "| Issue | Title | Disposition     | Note |\n"
        "| ----- | ----- | --------------- | ---- |\n"
        "| 96    | A title | absorbed-by: §6 | X    |\n"
    )
    assert dispositions.read_issue_table(text) == [
        dispositions.Row(
            "issue:96", "absorbed-by", "§6", False, "spec-named-absorbed", "X"
        )
    ]


def test_read_issue_table_rejects_an_off_vocabulary_disposition():
    text = dispositions.render_issue_table(
        [dispositions.Row("issue:96", "absorbed-by", "§6", False, "r", "t")]
    ).replace("absorbed-by: §6", "retired")
    with pytest.raises(dispositions.MarkerError):
        dispositions.read_issue_table(text)


_ISSUE_96 = dispositions.Row(
    "issue:96", "absorbed-by", "§6", False, "spec-named-absorbed", "Distribution model"
)


def test_apply_rows_writes_the_issue_table_and_no_file_named_issue(tmp_path):
    (tmp_path / "docs").mkdir()
    written = dispositions.apply_rows(
        [_ISSUE_96],
        root=tmp_path,
        date="2026-09-05",
        titles={"issue:96": "Distribution model for the recommended plugin bucket"},
    )
    assert written == [dispositions.ISSUE_TABLE]
    assert "| 96 |" in (tmp_path / dispositions.ISSUE_TABLE).read_text(encoding="utf-8")


def test_apply_rows_carries_the_titles_forward_when_none_are_supplied(tmp_path):
    """`apply` without `--issues-json` blanked all 66 Title cells, unrecoverably.

    `read_issue_table` never reads Title back and no other file holds one, so
    the committed table is the only copy. Both operational commands in the plan
    omit the flag. Reproduced 2026-09-06 against the committed table: 66
    populated cells in, 0 out.
    """
    (tmp_path / "docs").mkdir()
    title = "Distribution model for the recommended plugin bucket"
    dispositions.apply_rows(
        [_ISSUE_96], root=tmp_path, date="2026-09-05", titles={"issue:96": title}
    )

    dispositions.apply_rows([_ISSUE_96], root=tmp_path, date="2026-09-06")

    text = (tmp_path / dispositions.ISSUE_TABLE).read_text(encoding="utf-8")
    assert f"| 96 | {title} |" in text
    assert dispositions.read_issue_titles(text) == {"issue:96": title}


def test_apply_rows_refuses_to_write_a_table_it_would_blank(tmp_path):
    """No table to carry forward and no titles given: refuse, never blank."""
    (tmp_path / "docs").mkdir()
    with pytest.raises(dispositions.MarkerError, match="Title"):
        dispositions.apply_rows([_ISSUE_96], root=tmp_path, date="2026-09-05")
    assert not (tmp_path / dispositions.ISSUE_TABLE).exists()


def test_apply_rows_gives_the_issue_table_one_writer(tmp_path):
    """The table is in scope, so a full proposal carries a document row for it.

    Applying both wrote the document row's marker and then overwrote the whole
    file with the render, discarding the reviewed row. The render owns the
    file; the document row is the no-op.
    """
    (tmp_path / "docs").mkdir()
    document_row = dispositions.Row(
        dispositions.ISSUE_TABLE, "historical", "", False, "residual", ""
    )
    written = dispositions.apply_rows(
        [document_row, _ISSUE_96],
        root=tmp_path,
        date="2026-09-06",
        titles={"issue:96": "Distribution model"},
    )

    assert written == [dispositions.ISSUE_TABLE], "written once, not twice"
    text = (tmp_path / dispositions.ISSUE_TABLE).read_text(encoding="utf-8")
    assert text.count("Disposition: ") == 1
    assert dispositions.read_marker(text).value == "current", (
        "the render's preamble is the table's own marker"
    )


def test_apply_rows_leaves_the_table_alone_when_no_issue_rows_are_applied(tmp_path):
    """The no-op is total: with no render to own the file, nothing writes it."""
    (tmp_path / "docs").mkdir()
    table = tmp_path / dispositions.ISSUE_TABLE
    table.write_text("# Issue dispositions\n\nhand-written\n", encoding="utf-8")
    document_row = dispositions.Row(
        dispositions.ISSUE_TABLE, "current", "", False, "residual", ""
    )

    assert (
        dispositions.apply_rows([document_row], root=tmp_path, date="2026-09-06") == []
    )
    assert table.read_text(encoding="utf-8") == "# Issue dispositions\n\nhand-written\n"


def test_main_apply_wires_the_titles_through_end_to_end(tmp_path, monkeypatch, capsys):
    """`main`'s apply branch is the only path that mutates the repository.

    It had no test at all. `root=ROOT` is named at both call sites precisely so
    this one can point the module at a temporary repository.
    """
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("# A\n\nBody.\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", "docs/a.md"], cwd=tmp_path, check=True)
    monkeypatch.setattr(dispositions, "ROOT", tmp_path)
    proposal = tmp_path / "proposal.tsv"
    proposal.write_text(
        dispositions.HEADER
        + "\ndocs/a.md\tcurrent\t\t\tshipped-surface\t"
        + "\nissue:96\tabsorbed-by\t§6\t\tspec-named-absorbed\tthe author's reason\n",
        encoding="utf-8",
    )
    issues = tmp_path / "issues.json"
    issues.write_text(
        json.dumps([{"number": 96, "title": "Distribution model"}]), encoding="utf-8"
    )

    assert (
        dispositions.main(
            [
                "apply",
                str(proposal),
                "--date",
                "2026-09-06",
                "--issues-json",
                str(issues),
            ]
        )
        == 0
    )

    assert "marked 1 documents and the issue table" in capsys.readouterr().out
    table = (tmp_path / dispositions.ISSUE_TABLE).read_text(encoding="utf-8")
    assert (
        "| 96 | Distribution model | absorbed-by: §6 | the author's reason |" in table
    )
    assert (
        dispositions.read_marker(
            (tmp_path / "docs" / "a.md").read_text(encoding="utf-8")
        ).value
        == "current"
    )

    # Re-run with the flag dropped, which is what both operational commands in
    # the plan actually do: the titles must survive.
    assert dispositions.main(["apply", str(proposal), "--date", "2026-09-07"]) == 0
    assert "| 96 | Distribution model |" in (
        tmp_path / dispositions.ISSUE_TABLE
    ).read_text(encoding="utf-8")


# Linter section


def test_the_issue_table_is_well_formed():
    rows = dispositions.read_issue_table(
        (ROOT / dispositions.ISSUE_TABLE).read_text(encoding="utf-8")
    )
    numbers = [row.key for row in rows]
    assert len(numbers) == len(set(numbers)), "duplicate issue rows"
    for row in rows:
        assert row.value in dispositions.ISSUE_VALUES, row
        assert bool(row.argument) == (row.value == "absorbed-by"), row
        if row.value == "absorbed-by":
            assert row.argument.startswith("§"), row


@pytest.mark.live_net
@pytest.mark.skipif(shutil.which("gh") is None, reason="gh CLI absent")
def test_the_issue_table_covers_every_open_issue():
    listed = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--state",
            "open",
            "--limit",
            "300",
            "--json",
            "number",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    if listed.returncode != 0:
        pytest.skip(f"gh unusable: {listed.stderr.strip()[:120]}")
    open_numbers = {f"issue:{item['number']}" for item in json.loads(listed.stdout)}
    covered = {
        row.key
        for row in dispositions.read_issue_table(
            (ROOT / dispositions.ISSUE_TABLE).read_text(encoding="utf-8")
        )
    }
    assert not open_numbers - covered, (
        f"open issues with no disposition: {sorted(open_numbers - covered)}"
    )
