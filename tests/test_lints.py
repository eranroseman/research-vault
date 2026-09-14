import re
import subprocess

import pytest

from research_vault import Result, frontmatter, gitstate, lints, notes
from research_vault.pathcodec import RepoPath
from tests.conftest import must_replace


def test_all_clean_on_fixture(fixture_vault):
    assert lints.lint_append_only(fixture_vault) == []
    assert lints.lint_claim_immutability(fixture_vault) == []
    assert lints.lint_published_drift(fixture_vault) == []


def test_append_only_reports_each_tracked_file_with_removed_content(fixture_vault):
    daily_log = fixture_vault / "log" / "2026-08-16.md"
    queue = fixture_vault / "inbox" / "review-queue.md"
    daily_log.write_text("")
    queue.write_text("- old finding\n")
    subprocess.run(["git", "add", queue], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "queue history"], cwd=fixture_vault, check=True
    )
    queue.write_text("")

    outs = lints.lint_append_only(fixture_vault)

    assert [(out.target, out.reason) for out in outs] == [
        (
            "path-bytes:inbox/review-queue.md",
            "drift — append-only file rewrote history",
        ),
        ("path-bytes:log/2026-08-16.md", "drift — append-only file rewrote history"),
    ]


def test_append_only_reports_whole_tracked_file_deletion_but_not_untracked_addition(
    fixture_vault,
):
    (fixture_vault / "log" / "2026-08-16.md").unlink()
    (fixture_vault / "log" / "new.md").write_text("- new event\n")

    outs = lints.lint_append_only(fixture_vault)

    assert [out.target for out in outs] == ["path-bytes:log/2026-08-16.md"]


def test_append_only_guards_project_search_logs(fixture_vault):
    """`projects/<name>/search-log.md` joins the same guard as
    ``inbox/review-queue.md`` and ``log/``: it is a PRISMA-S search trail,
    and a trail that can be silently rewritten cannot be trusted."""
    search_log = fixture_vault / "projects" / "brief" / "search-log.md"
    search_log.write_text(
        '---\ntype: "search-log"\n---\n- [query:: q] [source:: PubMed] [date:: 2026-08-20] [hits:: 5] [actor:: human:eran]\n'
    )
    subprocess.run(["git", "add", search_log], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "search log history"], cwd=fixture_vault, check=True
    )
    search_log.write_text('---\ntype: "search-log"\n---\n')

    outs = lints.lint_append_only(fixture_vault)

    assert [(out.target, out.reason) for out in outs] == [
        (
            "path-bytes:projects/brief/search-log.md",
            "drift — append-only file rewrote history",
        )
    ]


def test_append_only_log_pathspec_excludes_reserved_root_log(tmp_vault):
    daily = tmp_vault / "log" / "2026-08-20.md"
    daily.parent.mkdir(exist_ok=True)
    daily.write_text("- daily history\n")
    root_log = tmp_vault / "log.md"
    root_log.write_text("# Dehydrated log tail\n")
    subprocess.run(["git", "add", daily, root_log], cwd=tmp_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "log collision fixture"], cwd=tmp_vault, check=True
    )
    daily.write_text("")
    root_log.write_text("")

    outs = lints.lint_append_only(tmp_vault)

    assert [out.target for out in outs] == ["path-bytes:log/2026-08-20.md"]


def test_claim_immutability_catches_silent_edit_and_records_origin(fixture_vault):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        must_replace(note.read_text(), "Mortality fell 12%", "Mortality fell 21%")
    )

    outs = lints.lint_claim_immutability(fixture_vault)

    assert [(out.target, out.extra) for out in outs] == [
        (
            "smith2020#^c-11111111",
            {
                "note_path": "path-bytes:literatures/smith2020.md",
                "claim_id": "c-11111111",
            },
        )
    ]


def test_claim_immutability_reports_each_claim_when_a_tracked_note_is_deleted(
    fixture_vault,
):
    (fixture_vault / "literatures" / "smith2020.md").unlink()

    outs = lints.lint_claim_immutability(fixture_vault)

    assert [out.target for out in outs] == [
        "smith2020#^c-11111111",
        "smith2020#^c-22222222",
    ]


def test_claim_immutability_reports_a_deleted_claim_from_a_non_ascii_path(
    fixture_vault,
):
    note = fixture_vault / "projects" / "synthèse.md"
    note.write_text("- (inference) Unicode path claim ^c-unicode\n")
    subprocess.run(["git", "add", note], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "add unicode path claim"],
        cwd=fixture_vault,
        check=True,
    )
    note.unlink()

    outs = lints.lint_claim_immutability(fixture_vault)

    assert [(out.target, out.extra) for out in outs] == [
        (
            "path-bytes:projects/synth%C3%A8se.md",
            {
                "note_path": "path-bytes:projects/synth%C3%A8se.md",
                "claim_id": "c-unicode",
            },
        )
    ]


def test_claim_immutability_allows_complete_deprecation_transition(fixture_vault):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        must_replace(
            note.read_text(),
            "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
            "- (paraphrase) Retrospective design [@smith2020, p. 3] "
            "[status:: deprecated] [deprecated-at:: 2026-08-16] "
            "[deprecated-by:: human:eran] [reason:: superseded] ^c-22222222",
        )
    )

    assert lints.lint_claim_immutability(fixture_vault) == []


def test_claim_immutability_allows_complete_deprecation_transition_with_a_successor(
    fixture_vault,
):
    """§5: `superseded-by` is optional but load-bearing when present — a
    deprecation transition that names a successor claim link must pass
    exactly like one that doesn't (the "both ways" pair)."""
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        must_replace(
            note.read_text(),
            "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
            "- (paraphrase) Retrospective design [@smith2020, p. 3] "
            "[status:: deprecated] [deprecated-at:: 2026-08-16] "
            "[deprecated-by:: human:eran] [reason:: superseded] "
            "[superseded-by:: jones2024#^c-11111111] ^c-22222222",
        )
    )

    assert lints.lint_claim_immutability(fixture_vault) == []


def test_claim_immutability_rejects_deprecation_with_empty_superseded_by(
    fixture_vault,
):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        must_replace(
            note.read_text(),
            "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
            "- (paraphrase) Retrospective design [@smith2020, p. 3] "
            "[status:: deprecated] [deprecated-at:: 2026-08-16] "
            "[deprecated-by:: human:eran] [reason:: superseded] "
            "[superseded-by:: ] ^c-22222222",
        )
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-22222222"
    ]


def test_claim_immutability_rejects_duplicate_superseded_by(fixture_vault):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        must_replace(
            note.read_text(),
            "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
            "- (paraphrase) Retrospective design [@smith2020, p. 3] "
            "[status:: deprecated] [deprecated-at:: 2026-08-16] "
            "[deprecated-by:: human:eran] [reason:: superseded] "
            "[superseded-by:: jones2024#^c-11111111] "
            "[superseded-by:: other2024#^c-33333333] ^c-22222222",
        )
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-22222222"
    ]


def test_claim_immutability_rejects_incomplete_deprecation_or_deprecation_with_mutation(
    fixture_vault,
):
    note = fixture_vault / "literatures" / "smith2020.md"
    text = must_replace(note.read_text(), "Mortality fell 12%", "Mortality rose 12%")
    text = must_replace(
        text,
        "^c-11111111",
        "[status:: deprecated] [deprecated-at:: 2026-08-16] "
        "[deprecated-by:: human:eran] [reason:: superseded] ^c-11111111",
    )
    note.write_text(
        must_replace(text, "^c-22222222", "[status:: deprecated] ^c-22222222")
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-11111111",
        "smith2020#^c-22222222",
    ]


def test_claim_immutability_rejects_duplicate_deprecation_status(fixture_vault):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        must_replace(
            note.read_text(),
            "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
            "- (paraphrase) Retrospective design [@smith2020, p. 3] "
            "[status:: deprecated] [status:: deprecated] "
            "[deprecated-at:: 2026-08-16] [deprecated-by:: human:eran] "
            "[reason:: superseded] ^c-22222222",
        )
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-22222222"
    ]


def test_claim_immutability_rejects_duplicate_deprecation_reason(fixture_vault):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        must_replace(
            note.read_text(),
            "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
            "- (paraphrase) Retrospective design [@smith2020, p. 3] "
            "[status:: deprecated] [deprecated-at:: 2026-08-16] "
            "[deprecated-by:: human:eran] [reason:: superseded] "
            "[reason:: duplicate] ^c-22222222",
        )
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-22222222"
    ]


def test_claim_immutability_allows_only_one_exact_verify_failed_marker_change(
    fixture_vault,
):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        must_replace(
            note.read_text(),
            "^c-11111111",
            "[failed-verification:: quote/2026-08-16] ^c-11111111",
        )
    )

    assert lints.lint_claim_immutability(fixture_vault) == []


def test_claim_immutability_allows_only_exact_failed_verification_marker_change(
    fixture_vault,
):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        must_replace(
            note.read_text(),
            "^c-11111111",
            "[failed-verification:: quote/2026-08-20] ^c-11111111",
        )
    )

    assert lints.lint_claim_immutability(fixture_vault) == []


def test_claim_immutability_allows_removing_a_committed_verify_failed_marker(
    fixture_vault,
):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        must_replace(
            note.read_text(),
            "^c-11111111",
            "[failed-verification:: quote/2026-08-16] ^c-11111111",
        )
    )
    subprocess.run(["git", "add", note], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "stamp failure"], cwd=fixture_vault, check=True
    )
    note.write_text(
        must_replace(note.read_text(), "[failed-verification:: quote/2026-08-16] ", "")
    )

    assert lints.lint_claim_immutability(fixture_vault) == []


def test_claim_immutability_rejects_verify_failed_marker_replacement(fixture_vault):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        must_replace(
            note.read_text(),
            "^c-11111111",
            "[failed-verification:: quote/2026-08-16] ^c-11111111",
        )
    )
    subprocess.run(["git", "add", note], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "stamp failure"], cwd=fixture_vault, check=True
    )
    note.write_text(
        must_replace(
            note.read_text(),
            "[failed-verification:: quote/2026-08-16]",
            "[failed-verification:: citation-key/2026-08-17]",
        )
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-11111111"
    ]


def test_claim_immutability_rejects_verify_failed_marker_replacement_with_mutation(
    fixture_vault,
):
    note = fixture_vault / "literatures" / "smith2020.md"
    text = must_replace(note.read_text(), "Mortality fell 12%", "Mortality rose 12%")
    note.write_text(
        must_replace(
            text, "^c-11111111", "[failed-verification:: quote/2026-08-16] ^c-11111111"
        )
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-11111111"
    ]


def test_claim_immutability_does_not_mask_a_continuation_newline_change(
    fixture_vault,
):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_bytes(must_replace(note.read_bytes(), b"\n", b"\r\n", -1))
    subprocess.run(["git", "add", note], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "preserve source line endings"],
        cwd=fixture_vault,
        check=True,
    )
    note.write_bytes(
        must_replace(
            note.read_bytes(),
            b"^c-11111111\r\n  > Mortality fell 12% across all strata.\r\n",
            b"[failed-verification:: quote/2026-08-16] ^c-11111111\r\n"
            b"  > Mortality fell 12% across all strata.\n",
        )
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-11111111"
    ]


def test_claim_immutability_does_not_mask_header_newline_change_in_deprecation(
    fixture_vault,
):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_bytes(must_replace(note.read_bytes(), b"\n", b"\r\n", -1))
    subprocess.run(["git", "add", note], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "preserve source line endings"],
        cwd=fixture_vault,
        check=True,
    )
    note.write_bytes(
        must_replace(
            note.read_bytes(),
            b"- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222\r\n",
            b"- (paraphrase) Retrospective design [@smith2020, p. 3] "
            b"[status:: deprecated] [deprecated-at:: 2026-08-16] "
            b"[deprecated-by:: human:eran] [reason:: superseded] ^c-22222222\n",
        )
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-22222222"
    ]


def test_claim_immutability_detects_distinct_invalid_utf8_bytes(fixture_vault):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_bytes(
        must_replace(note.read_bytes(), b"  > Mortality fell", b"  > \xffortality fell")
    )
    subprocess.run(["git", "add", note], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "record invalid source byte"],
        cwd=fixture_vault,
        check=True,
    )
    note.write_bytes(
        must_replace(
            note.read_bytes(), b"  > \xffortality fell", b"  > \xfeortality fell"
        )
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-11111111"
    ]


def test_published_drift_includes_untracked_files(fixture_vault):
    subprocess.run(
        ["git", "tag", "published/brief-2026-08-16-120000"],
        cwd=fixture_vault,
        check=True,
    )
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        must_replace(draft.read_text(), 'status: "draft"', 'status: "published"')
        + "\nnew paragraph after publishing\n"
    )
    (draft.parent / "untracked.md").write_text("new material\n")

    outs = lints.lint_published_drift(fixture_vault)

    assert [(out.target, out.reason) for out in outs] == [
        ("path-bytes:projects/brief", "drift — published project diverged from its tag")
    ]


def test_published_drift_catches_tracked_changes_after_a_published_tag(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        must_replace(draft.read_text(), 'status: "draft"', 'status: "published"')
    )
    subprocess.run(["git", "add", draft], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "publish brief"], cwd=fixture_vault, check=True
    )
    subprocess.run(
        ["git", "tag", "published/brief-2026-08-16-120000"],
        cwd=fixture_vault,
        check=True,
    )
    draft.write_text(draft.read_text() + "\npost-publish edit\n")

    assert [out.target for out in lints.lint_published_drift(fixture_vault)] == [
        "path-bytes:projects/brief"
    ]


def test_published_drift_reports_wholly_deleted_effort_from_prior_published_status(
    fixture_vault,
):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        must_replace(draft.read_text(), 'status: "draft"', 'status: "published"')
    )
    subprocess.run(["git", "add", draft], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "publish brief"], cwd=fixture_vault, check=True
    )
    subprocess.run(
        ["git", "tag", "published/brief-2026-08-16-120000"],
        cwd=fixture_vault,
        check=True,
    )
    draft.unlink()

    assert [out.target for out in lints.lint_published_drift(fixture_vault)] == [
        "path-bytes:projects/brief"
    ]


@pytest.mark.parametrize("status", ["withdrawn", "parked"])
def test_published_drift_leaves_the_unwatched_statuses_alone(fixture_vault, status):
    """`withdrawn` and `parked` are unwatched by design, not by accident.

    Both say the project is no longer standing as a publication, so divergence
    from its tag is expected rather than reportable. Pinned so the ruling
    survives the `corrected` widening rather than being re-litigated by
    whoever next reads `WATCHED_PUBLICATION_STATUSES`.
    """
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        must_replace(draft.read_text(), 'status: "draft"', f'status: "{status}"')
    )
    subprocess.run(["git", "add", draft], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"{status} brief"], cwd=fixture_vault, check=True
    )
    subprocess.run(
        ["git", "tag", "published/brief-2026-08-16-120000"],
        cwd=fixture_vault,
        check=True,
    )
    draft.write_text(draft.read_text() + "\npost-tag edit\n")

    assert lints.lint_published_drift(fixture_vault) == []


def test_published_drift_keeps_drift_finding_with_malformed_sibling(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        must_replace(draft.read_text(), 'status: "draft"', 'status: "published"')
    )
    subprocess.run(["git", "add", draft], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "publish brief"], cwd=fixture_vault, check=True
    )
    subprocess.run(
        ["git", "tag", "published/brief-2026-08-16-120000"],
        cwd=fixture_vault,
        check=True,
    )
    (draft.parent / "broken.md").write_text('---\nstatus: "published"\n')

    outs = lints.lint_published_drift(fixture_vault)

    assert [(out.target, out.reason) for out in outs] == [
        (
            "path-bytes:projects/brief",
            "drift — published project diverged from its tag",
        ),
        (
            "path-bytes:projects/brief/broken.md",
            "schema-violation — malformed frontmatter",
        ),
    ]


def test_disputed_claim_lint_surfaces_only_carrier_and_supported_addresses(
    fixture_vault,
):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text() + "- (inference) Relies on contested support [supports:: "
        "[[smith2020#^c-11111111]] [[mortality-trends#^c-55555555]] "
        "[[gone2019#^c-22222222]] [[smith2020#^c-11111111]]] ^c-99999999\n"
    )

    outs = lints.lint_disputed_claim(fixture_vault, draft)

    assert [(out.target, out.extra) for out in outs] == [
        (
            "mortality-trends#^c-55555555",
            {
                "note_path": "path-bytes:projects/brief/draft.md",
                "claim_id": "c-99999999",
            },
        ),
        (
            "smith2020#^c-11111111",
            {
                "note_path": "path-bytes:projects/brief/draft.md",
                "claim_id": "c-99999999",
            },
        ),
    ]
    assert all(out.reason.startswith("disputed-claim") for out in outs)


def test_citing_the_counterevidence_address_is_clean(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text() + "- (inference) Cites the contester [supports:: "
        "[[gone2019#^c-22222222]]] ^c-99999998\n"
    )

    assert lints.lint_disputed_claim(fixture_vault, draft) == []


def _refresh_body_witness(path):
    text = path.read_text()
    data, body = frontmatter.parse(text)
    data["managed-sha256"] = notes.body_sha256(text)
    path.write_text(frontmatter.serialize(data) + body)


@pytest.mark.parametrize("change", ["add", "edit", "delete", "rename"])
def test_body_change_always_yields_typed_evidence_finding_with_fresh_witness(
    fixture_vault, change
):
    base = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=fixture_vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    source = fixture_vault / "literatures" / "smith2020.md"
    expected_reason = {
        "add": "drift — literature note added",
        "edit": "drift — literature note body changed",
        "delete": "drift — literature note deleted",
        "rename": "drift — literature note renamed",
    }[change]
    if change == "add":
        added = fixture_vault / "literatures" / "added.md"
        added.write_bytes(source.read_bytes())
        expected = "path-bytes:literatures/added.md"
    elif change == "edit":
        source.write_text(
            must_replace(source.read_text(), "# Mortality decline", "# Changed")
        )
        _refresh_body_witness(source)
        expected = "path-bytes:literatures/smith2020.md"
    elif change == "delete":
        source.unlink()
        expected = "path-bytes:literatures/smith2020.md"
    else:
        renamed = fixture_vault / "literatures" / "renamed.md"
        source.rename(renamed)
        expected = "path-bytes:literatures/renamed.md"

    outcomes = lints.lint_evidence_layer(
        gitstate.snapshot_tree(fixture_vault, base),
        gitstate.snapshot_worktree(fixture_vault),
    )

    findings = [
        item
        for item in outcomes
        if item.result is Result.UNMATCHED and item.target == expected
    ]
    assert findings, outcomes
    for finding in findings:
        assert finding.check == "evidence-layer"
        assert finding.target_kind == "repo-path"
    # Pinned, not prefix-matched: the `edit` case's witness refresh also
    # changes `managed-sha256` with no writer attestation, so this target
    # can carry a second same-target "drift" finding. A prefix check would
    # let that second finding stand in for this one if the managed-region
    # comparison itself ever regressed — pin the exact reason instead.
    assert any(finding.reason == expected_reason for finding in findings), findings


def test_prose_appended_below_the_note_is_a_body_change(fixture_vault):
    """The free region is retired: the whole body is capture's, so hand-added
    prose is drift rather than the one edit the linter used to wave through."""
    base = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=fixture_vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    source = fixture_vault / "literatures" / "smith2020.md"
    source.write_text(source.read_text() + "hand-written prose\n")

    outcomes = lints.lint_evidence_layer(
        gitstate.snapshot_tree(fixture_vault, base),
        gitstate.snapshot_worktree(fixture_vault),
    )

    assert "drift — literature note body changed" in {
        item.reason for item in outcomes if item.result is Result.UNMATCHED
    }


def test_stale_or_malformed_witness_is_schema_finding_even_without_git_change(
    fixture_vault,
):
    source = fixture_vault / "literatures" / "smith2020.md"
    source.write_text(
        must_replace(source.read_text(), 'managed-sha256: "', 'managed-sha256: "A')
    )
    candidate = gitstate.snapshot_worktree(fixture_vault)

    outcomes = lints.lint_evidence_layer(candidate, candidate)

    finding = next(item for item in outcomes if item.result is Result.UNMATCHED)
    assert finding.check == "evidence-layer"
    assert finding.target_kind == "repo-path"
    assert finding.reason.startswith("schema-violation")


def _hand_edit_machine_owned_key(text: str, key: str) -> str:
    """Mutate exactly one machine-owned frontmatter field, the body untouched."""
    if key == "managed-sha256":
        digest = re.search(r'managed-sha256: "([0-9a-f]{64})"', text).group(1)
        return must_replace(text, digest, "b" * 64)
    if key == "zotero-item-version":
        return must_replace(text, "zotero-item-version: 12", "zotero-item-version: 13")
    if key == "generated":
        return must_replace(
            text,
            'generated: {by: "research_vault/0.1.0"',
            'generated: {by: "human:hand-edit"',
        )
    if key == "citationKey":
        return must_replace(
            text, 'citationKey: "smith2020"', 'citationKey: "smith2020x"'
        )
    raise ValueError(key)


@pytest.mark.parametrize(
    "key",
    ["managed-sha256", "zotero-item-version", "generated", "citationKey"],
)
def test_hand_edited_machine_owned_frontmatter_key_is_drift(fixture_vault, key):
    """Machine-owned frontmatter sits above the body, so a hand-edit to it —
    with the body untouched and no writer attestation (a `generated` bump by
    the machine actor in the same diff) — must surface as drift, the same as a
    body change would.
    """
    base = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=fixture_vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    source = fixture_vault / "literatures" / "smith2020.md"
    original = source.read_text()
    edited = _hand_edit_machine_owned_key(original, key)
    assert edited != original
    source.write_text(edited)

    outcomes = lints.lint_evidence_layer(
        gitstate.snapshot_tree(fixture_vault, base),
        gitstate.snapshot_worktree(fixture_vault),
    )

    expected_reason = f"drift — {key} changed without writer attestation"
    assert any(
        item.target == "path-bytes:literatures/smith2020.md"
        and item.reason == expected_reason
        for item in outcomes
    ), outcomes


@pytest.mark.parametrize(
    "malformed_generated",
    [
        'generated: {by: "research_vault/0.1.0", at: "banana"}',
        'generated: {by: "research_vault/0.1.0"}',
    ],
    ids=["invalid-at", "missing-at"],
)
def test_malformed_generated_does_not_attest_a_machine_owned_key_change(
    fixture_vault, malformed_generated
):
    """A `generated` whose `by` looks machine-class but whose shape is invalid
    (bad `at`, or no `at` at all) must not legalize anything —
    `notes._valid_generated` is the one place this field's shape is defined.
    """
    base = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=fixture_vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    source = fixture_vault / "literatures" / "smith2020.md"
    edited = must_replace(
        source.read_text(), 'citationKey: "smith2020"', 'citationKey: "smith2020x"'
    )
    edited = must_replace(
        edited,
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}',
        malformed_generated,
    )
    source.write_text(edited)

    outcomes = lints.lint_evidence_layer(
        gitstate.snapshot_tree(fixture_vault, base),
        gitstate.snapshot_worktree(fixture_vault),
    )

    assert any(
        item.reason == "drift — citationKey changed without writer attestation"
        for item in outcomes
    ), outcomes


def test_two_unequal_junk_generated_values_are_not_seen_as_unchanged(fixture_vault):
    """Two different non-dict `generated` values must not compare equal just
    because both get coerced to "no shape" — the comparison has to see the
    raw value, or a hand-edit could hide behind a same-looking coercion.
    """
    source = fixture_vault / "literatures" / "smith2020.md"
    source.write_text(
        must_replace(
            source.read_text(),
            'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}',
            'generated: "junk-one"',
        )
    )
    subprocess.run(["git", "add", "-A"], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "junk generated base"],
        cwd=fixture_vault,
        check=True,
    )
    base = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=fixture_vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()

    edited = must_replace(
        source.read_text(), 'generated: "junk-one"', 'generated: "junk-two"'
    )
    source.write_text(edited)

    outcomes = lints.lint_evidence_layer(
        gitstate.snapshot_tree(fixture_vault, base),
        gitstate.snapshot_worktree(fixture_vault),
    )

    assert any(
        item.reason == "drift — generated changed without writer attestation"
        for item in outcomes
    ), outcomes


def test_unparseable_base_frontmatter_does_not_skip_the_per_key_check(fixture_vault):
    """An unparseable *base* frontmatter must not silently skip the whole
    per-key comparison. The candidate side already has an independent parse
    check (`validate_managed_witness`, first loop); this loop must not
    short-circuit on the base side going unparseable instead.
    """
    source = fixture_vault / "literatures" / "smith2020.md"
    original = source.read_text()
    malformed = must_replace(
        original,
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}\n---\n',
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}\n'
        "  bad: nested\n---\n",
    )
    with pytest.raises(frontmatter.FrontmatterError):
        frontmatter.parse(malformed)
    source.write_text(malformed)
    subprocess.run(["git", "add", "-A"], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "malformed base frontmatter"],
        cwd=fixture_vault,
        check=True,
    )
    base = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=fixture_vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()

    source.write_text(_hand_edit_machine_owned_key(original, "generated"))

    outcomes = lints.lint_evidence_layer(
        gitstate.snapshot_tree(fixture_vault, base),
        gitstate.snapshot_worktree(fixture_vault),
    )

    assert any(
        item.reason == "drift — generated changed without writer attestation"
        for item in outcomes
    ), outcomes


def test_unparseable_base_frontmatter_does_not_auto_attest_via_a_valid_candidate(
    fixture_vault,
):
    """An unparseable base cannot attest anything. A candidate whose
    `generated` is otherwise validly machine-shaped must not be read as
    evidence this diff was a legitimate write when there is no prior state to
    compare it against — that would let an unreadable base auto-attest any
    machine-owned key change hiding behind it.
    """
    source = fixture_vault / "literatures" / "smith2020.md"
    original = source.read_text()
    malformed = must_replace(
        original,
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}\n---\n',
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}\n'
        "  bad: nested\n---\n",
    )
    source.write_text(malformed)
    subprocess.run(["git", "add", "-A"], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "malformed base frontmatter"],
        cwd=fixture_vault,
        check=True,
    )
    base = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=fixture_vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()

    # Candidate is the pristine, untouched note: valid frontmatter, a
    # validly-shaped machine-attested `generated`, nothing hand-edited at
    # all — exactly the shape that would auto-attest a sibling machine-owned
    # key change if the base's unreadability weren't itself the problem.
    source.write_text(original)

    outcomes = lints.lint_evidence_layer(
        gitstate.snapshot_tree(fixture_vault, base),
        gitstate.snapshot_worktree(fixture_vault),
    )

    findings = {
        item.reason
        for item in outcomes
        if item.result is Result.UNMATCHED
        and item.target == "path-bytes:literatures/smith2020.md"
    }
    # Pinned, not presence-only: a truthiness check survives the loss of any
    # single reason below, because the rest keep the set non-empty. Measured —
    # dropping only the citationKey outcome leaves a presence-only assertion
    # green. Every capture field the fixture carries fires, `generated`
    # included: an unparseable base attests nothing, so a machine-shaped
    # candidate `generated` is itself an unattested change.
    assert findings == {
        f"drift — {key} changed without writer attestation"
        for key in (
            "DOI",
            "accessed",
            "aliases",
            "attachments",
            "citationKey",
            "compile-input-sha256",
            "fulltext",
            "generated",
            "itemType",
            "managed-sha256",
            "title",
            "type",
            "zotero-item-key",
            "zotero-item-version",
            "zotero-server-id",
        )
    } | {
        # `_body_bytes` fails closed on the unparseable side too, so the body
        # comparison cannot be silenced by the frontmatter that hid it.
        "drift — literature note body changed",
    }


def test_screening_state_is_retired(fixture_vault):
    from research_vault import inbox, lints, verify

    assert not hasattr(lints, "lint_screening_state")
    assert "screening-state" not in inbox.CHECK_IDS
    assert "superseded-note" not in inbox.REASON_CODES
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    checks = {outcome.check for outcome in verify.file_outcomes(fixture_vault, draft)}
    assert "screening-state" not in checks


# --- boundaries the blanket mutation run (Plan W Task 25) found unpinned ------


def _file(raw, data):
    return gitstate.FileImage(raw, "file", 0o100644, data)


_CLAIM = b'---\ncitationKey: "smith2020"\n---\n- (inference) A claim [@smith2020, p. 1] ^c-1\n'
_MUTATED = _CLAIM.replace(b"A claim", b"A changed claim")


def test_claim_immutability_watches_only_md_notes_under_its_roots(tmp_vault):
    """A mutated claim in a wiki page or in a non-.md file under literatures/
    is not this lint's business; the same mutation under literatures/ is."""
    base = gitstate.Snapshot(
        {
            b"wiki/concepts/a.md": _file(b"wiki/concepts/a.md", _CLAIM),
            b"literatures/a.txt": _file(b"literatures/a.txt", _CLAIM),
            b"literatures": gitstate.FileImage(
                b"literatures", "directory", 0o40000, None
            ),
            b"literatures/b.md": _file(b"literatures/b.md", _CLAIM),
        }
    )
    candidate = gitstate.Snapshot(
        {
            b"wiki/concepts/a.md": _file(b"wiki/concepts/a.md", _MUTATED),
            b"literatures/a.txt": _file(b"literatures/a.txt", _MUTATED),
            b"literatures/b.md": _file(b"literatures/b.md", _MUTATED),
        }
    )
    outs = lints.lint_claim_immutability(tmp_vault, base, candidate)
    assert [(o.check, o.target, o.result) for o in outs] == [
        ("claim-immutability", "smith2020#^c-1", Result.UNMATCHED)
    ]
    assert (
        outs[0].reason == "drift — claim ^c-1 mutated or vanished without deprecation"
    )


def test_claim_immutability_walks_past_a_candidate_only_note_to_the_drift_after_it(
    tmp_vault,
):
    """A note the base does not carry (new in the candidate) sorts first and
    is passed over, not the end of the walk: the mutated note after it still
    rows its drift."""
    base = gitstate.Snapshot({b"literatures/b.md": _file(b"literatures/b.md", _CLAIM)})
    candidate = gitstate.Snapshot(
        {
            b"literatures/a.md": _file(b"literatures/a.md", _CLAIM),
            b"literatures/b.md": _file(b"literatures/b.md", _MUTATED),
        }
    )
    outs = lints.lint_claim_immutability(tmp_vault, base, candidate)
    assert [(o.check, o.target, o.result) for o in outs] == [
        ("claim-immutability", "smith2020#^c-1", Result.UNMATCHED)
    ]


def test_claim_target_is_the_claim_link_only_for_a_non_empty_string_key():
    text = '---\ncitationKey: "smith2020"\n---\n'
    assert lints._claim_target(b"literatures/x.md", text, "c-1") == "smith2020#^c-1"
    for key in ('""', "5"):
        text = f"---\ncitationKey: {key}\n---\n"
        assert lints._claim_target(b"literatures/x.md", text, "c-1") == RepoPath(
            b"literatures/x.md"
        )


def test_claim_immutability_rows_a_malformed_candidate_by_its_path(tmp_vault):
    """A candidate whose frontmatter no longer parses is a schema row on the
    note's path (the head still parses); a deleted note whose head never
    parsed is not a schema row, only its vanished claims are drift."""
    base = gitstate.Snapshot({b"literatures/b.md": _file(b"literatures/b.md", _CLAIM)})
    candidate = gitstate.Snapshot(
        {b"literatures/b.md": _file(b"literatures/b.md", b"---\nnot a mapping\n---\n")}
    )
    outs = lints.lint_claim_immutability(tmp_vault, base, candidate)
    assert (outs[0].check, outs[0].target, outs[0].result, outs[0].reason) == (
        "claim-immutability",
        "path-bytes:literatures/b.md",
        Result.UNMATCHED,
        "schema-violation — malformed frontmatter",
    )
    malformed_head = gitstate.Snapshot(
        {
            b"literatures/c.md": _file(
                b"literatures/c.md",
                b"---\nnot a mapping\n---\n- (inference) x [@smith2020, p. 1] ^c-9\n",
            )
        }
    )
    outs = lints.lint_claim_immutability(
        tmp_vault, malformed_head, gitstate.Snapshot({})
    )
    assert [(o.result, o.reason.split(" — ")[0]) for o in outs] == [
        (Result.UNMATCHED, "drift")
    ]


def test_claim_immutability_on_a_repository_without_a_head_reads_an_empty_base(
    tmp_path,
):
    vault = tmp_path / "vault"
    (vault / "literatures").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=vault, check=True)
    (vault / "literatures" / "a.md").write_bytes(_CLAIM)
    assert lints.lint_claim_immutability(vault) == []


def test_disputed_claim_links_walk_every_page_and_name_it_by_key_or_stem(tmp_vault):
    """A page's disputing claims are keyed by its citationKey when it has a
    non-empty string one and by its stem otherwise; a claim without
    `disputes` before a disputing one does not end the walk; a disputing
    claim without `supports` adds only its own link; a page whose
    frontmatter does not parse is one schema row and still read."""
    wiki = tmp_vault / "wiki" / "concepts"
    wiki.mkdir(parents=True, exist_ok=True)
    (wiki / "keyed.md").write_text(
        '---\ncitationKey: "keyed2020"\n---\n'
        "- (inference) Plain [@a2020] ^c-0\n"
        "- (inference) Dispute [disputes:: [[x2020#^c-5]]] ^c-1\n"
    )
    (wiki / "blank-key.md").write_text(
        '---\ncitationKey: ""\n---\n'
        "- (inference) Dispute [disputes:: [[x2020#^c-5]]] "
        "[supports:: [[y2020#^c-6]]] ^c-2\n"
    )
    (wiki / "broken.md").write_text(
        "---\nnot a mapping\n---\n- (inference) Dispute [disputes:: [[x2020#^c-5]]] ^c-3\n"
    )
    disputed, outcomes = lints.disputed_claim_links(tmp_vault)
    assert disputed == {"keyed2020#^c-1", "blank-key#^c-2", "y2020#^c-6", "broken#^c-3"}
    assert [(o.check, o.target, o.result, o.reason) for o in outcomes] == [
        (
            "disputed-claim",
            "path-bytes:wiki/concepts/broken.md",
            Result.UNMATCHED,
            "schema-violation — malformed frontmatter",
        )
    ]


def test_origin_targets_the_claim_link_only_with_a_key_and_an_anchor(tmp_vault):
    from research_vault import claims as claims_mod

    note = tmp_vault / "projects" / "brief" / "draft.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text('---\ncitationKey: "brief2020"\n---\n')
    anchored = claims_mod.Claim("inference", "smith2020", None, "c-1", 4)
    unanchored = claims_mod.Claim("inference", "smith2020", None, None, 4)
    target, extra = lints._origin(tmp_vault, note, anchored)
    assert target == "brief2020#^c-1"
    assert extra == {
        "note_path": RepoPath(b"projects/brief/draft.md"),
        "claim_id": "c-1",
    }
    target, _extra = lints._origin(tmp_vault, note, unanchored)
    assert target == RepoPath(b"projects/brief/draft.md")
    note.write_text('---\ncitationKey: ""\n---\n')
    target, _extra = lints._origin(tmp_vault, note, anchored)
    assert target == RepoPath(b"projects/brief/draft.md")


def test_body_bytes_and_frontmatter_need_a_file_image():
    directory = gitstate.FileImage(b"literatures/d", "directory", 0o40000, None)
    assert lints._body_bytes(None) is None
    assert lints._body_bytes(directory) is None
    assert lints._frontmatter(None) is None
    assert lints._frontmatter(directory) is None
    note = _file(b"literatures/a.md", _CLAIM)
    assert lints._body_bytes(note) == b"- (inference) A claim [@smith2020, p. 1] ^c-1\n"
    assert lints._frontmatter(note) == {"citationKey": "smith2020"}
    # An empty file reads as an empty body and no frontmatter, not as junk.
    empty = _file(b"literatures/a.md", b"")
    assert lints._body_bytes(empty) == b""
    assert lints._frontmatter(empty) == lints._frontmatter(_file(b"x.md", b"body\n"))
