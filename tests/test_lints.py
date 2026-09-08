import re
import subprocess

import pytest

from research_vault import Result, frontmatter, gitstate, lints, notes


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
    """`projects/<name>/search-log.md` (Task 6) joins the same guard as
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
        note.read_text().replace("Mortality fell 12%", "Mortality fell 21%")
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
        note.read_text().replace(
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
        note.read_text().replace(
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
        note.read_text().replace(
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
        note.read_text().replace(
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
    note.write_text(
        note.read_text()
        .replace("Mortality fell 12%", "Mortality rose 12%")
        .replace(
            "^c-11111111",
            "[status:: deprecated] [deprecated-at:: 2026-08-16] "
            "[deprecated-by:: human:eran] [reason:: superseded] ^c-11111111",
        )
        .replace("^c-22222222", "[status:: deprecated] ^c-22222222")
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-11111111",
        "smith2020#^c-22222222",
    ]


def test_claim_immutability_rejects_duplicate_deprecation_status(fixture_vault):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        note.read_text().replace(
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
        note.read_text().replace(
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
        note.read_text().replace(
            "^c-11111111", "[failed-verification:: quote/2026-08-16] ^c-11111111"
        )
    )

    assert lints.lint_claim_immutability(fixture_vault) == []


def test_claim_immutability_allows_only_exact_failed_verification_marker_change(
    fixture_vault,
):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        note.read_text().replace(
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
        note.read_text().replace(
            "^c-11111111", "[failed-verification:: quote/2026-08-16] ^c-11111111"
        )
    )
    subprocess.run(["git", "add", note], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "stamp failure"], cwd=fixture_vault, check=True
    )
    note.write_text(
        note.read_text().replace("[failed-verification:: quote/2026-08-16] ", "")
    )

    assert lints.lint_claim_immutability(fixture_vault) == []


def test_claim_immutability_rejects_verify_failed_marker_replacement(fixture_vault):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        note.read_text().replace(
            "^c-11111111", "[failed-verification:: quote/2026-08-16] ^c-11111111"
        )
    )
    subprocess.run(["git", "add", note], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "stamp failure"], cwd=fixture_vault, check=True
    )
    note.write_text(
        note.read_text().replace(
            "[failed-verification:: quote/2026-08-16]",
            "[failed-verification:: citekey/2026-08-17]",
        )
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-11111111"
    ]


def test_claim_immutability_rejects_verify_failed_marker_replacement_with_mutation(
    fixture_vault,
):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        note.read_text()
        .replace("Mortality fell 12%", "Mortality rose 12%")
        .replace("^c-11111111", "[failed-verification:: quote/2026-08-16] ^c-11111111")
    )

    assert [out.target for out in lints.lint_claim_immutability(fixture_vault)] == [
        "smith2020#^c-11111111"
    ]


def test_claim_immutability_does_not_mask_a_continuation_newline_change(
    fixture_vault,
):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_bytes(note.read_bytes().replace(b"\n", b"\r\n"))
    subprocess.run(["git", "add", note], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "preserve source line endings"],
        cwd=fixture_vault,
        check=True,
    )
    note.write_bytes(
        note.read_bytes().replace(
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
    note.write_bytes(note.read_bytes().replace(b"\n", b"\r\n"))
    subprocess.run(["git", "add", note], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "preserve source line endings"],
        cwd=fixture_vault,
        check=True,
    )
    note.write_bytes(
        note.read_bytes().replace(
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
        note.read_bytes().replace(b"  > Mortality fell", b"  > \xffortality fell", 1)
    )
    subprocess.run(["git", "add", note], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "record invalid source byte"],
        cwd=fixture_vault,
        check=True,
    )
    note.write_bytes(
        note.read_bytes().replace(b"  > \xffortality fell", b"  > \xfeortality fell", 1)
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
        draft.read_text().replace('status: "draft"', 'status: "published"')
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
        draft.read_text().replace('status: "draft"', 'status: "published"')
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
        draft.read_text().replace('status: "draft"', 'status: "published"')
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
        draft.read_text().replace('status: "draft"', f'status: "{status}"')
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
        draft.read_text().replace('status: "draft"', 'status: "published"')
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
            source.read_text().replace("# Mortality decline", "# Changed")
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
        source.read_text().replace('managed-sha256: "', 'managed-sha256: "A', 1)
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
        return text.replace(digest, "b" * 64, 1)
    if key == "fixity-sha256":
        digest = re.search(r'fixity-sha256:\n  - "([0-9a-f]+)"', text).group(1)
        return text.replace(digest, "c" * 64, 1)
    if key == "generated":
        return text.replace(
            'generated: {by: "research_vault/0.1.0"',
            'generated: {by: "human:hand-edit"',
            1,
        )
    if key == "citekey":
        return text.replace('citekey: "smith2020"', 'citekey: "smith2020x"', 1)
    raise ValueError(key)


@pytest.mark.parametrize(
    "key",
    ["managed-sha256", "fixity-sha256", "generated", "citekey"],
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
    edited = source.read_text().replace(
        'citekey: "smith2020"', 'citekey: "smith2020x"', 1
    )
    edited = edited.replace(
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}',
        malformed_generated,
        1,
    )
    source.write_text(edited)

    outcomes = lints.lint_evidence_layer(
        gitstate.snapshot_tree(fixture_vault, base),
        gitstate.snapshot_worktree(fixture_vault),
    )

    assert any(
        item.reason == "drift — citekey changed without writer attestation"
        for item in outcomes
    ), outcomes


def test_two_unequal_junk_generated_values_are_not_seen_as_unchanged(fixture_vault):
    """Two different non-dict `generated` values must not compare equal just
    because both get coerced to "no shape" — the comparison has to see the
    raw value, or a hand-edit could hide behind a same-looking coercion.
    """
    source = fixture_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}',
            'generated: "junk-one"',
            1,
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

    edited = source.read_text().replace(
        'generated: "junk-one"', 'generated: "junk-two"', 1
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
    malformed = original.replace(
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}\n---\n',
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}\n'
        "  bad: nested\n---\n",
        1,
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
    malformed = original.replace(
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}\n---\n',
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}\n'
        "  bad: nested\n---\n",
        1,
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
    # single reason below, because the remaining two keep the set non-empty.
    # Measured — dropping only the citekey outcome leaves a presence-only
    # assertion green.
    assert findings == {
        "drift — citekey changed without writer attestation",
        "drift — fixity-sha256 changed without writer attestation",
        "drift — managed-sha256 changed without writer attestation",
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
