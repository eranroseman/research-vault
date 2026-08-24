import re
import subprocess

import pytest

from knowledge_harness import Result, frontmatter, gitstate, lints, notes


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
    note = fixture_vault / "synthesis" / "synthèse.md"
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
            "path-bytes:synthesis/synth%C3%A8se.md",
            {
                "note_path": "path-bytes:synthesis/synth%C3%A8se.md",
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


def test_claim_immutability_rejects_marker_change_when_a_selector_continuation_changes(
    fixture_vault,
):
    note = fixture_vault / "literatures" / "smith2020.md"
    note.write_text(
        note.read_text()
        .replace(
            "  > Mortality fell 12% across all strata.",
            "  > Mortality rose 12% across all strata.",
        )
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


def test_screening_state_deduplicates_repeated_references_and_records_origin(
    fixture_vault,
):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text()
        + "- (paraphrase) Old claim [@gone2019, p. 1] [@gone2019, p. 2] ^c-88888888\n"
    )

    outs = lints.lint_screening_state(fixture_vault, draft)

    assert [(out.target, out.extra) for out in outs] == [
        (
            "gone2019",
            {
                "note_path": "path-bytes:projects/brief/draft.md",
                "claim_id": "c-88888888",
            },
        )
    ]
    assert outs[0].reason.startswith("superseded-note")


def test_screening_state_catches_excluded_sources(fixture_vault):
    excluded = fixture_vault / "literatures" / "excluded2024.md"
    excluded.write_text(
        '---\ncitekey: "excluded2024"\nstatus: "excluded"\n---\n# Excluded\n'
    )
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text() + "- (paraphrase) Bad source [@excluded2024] ^c-12121212\n"
    )

    outs = lints.lint_screening_state(fixture_vault, draft)

    assert len(outs) == 1
    assert outs[0].reason.startswith("superseded-note — cites excluded2024")


def test_screening_state_sorts_mixed_anchored_origins_without_crashing(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text()
        + "- (paraphrase) Old source [@gone2019]\n"
        + "- (paraphrase) Also old [@gone2019] ^c-34343434\n"
    )

    outs = lints.lint_screening_state(fixture_vault, draft)

    assert [out.extra["claim_id"] for out in outs] == ["c-34343434", None]


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


def test_web_archive_lint_requires_archive_for_a_doi_less_web_source(fixture_vault):
    web = fixture_vault / "literatures" / "webonly2024.md"
    web.write_text(
        '---\ncitekey: "webonly2024"\nurl: "https://example.org/post"\n---\n# Web\n'
    )

    outs = lints.lint_web_archive(fixture_vault)

    assert [(out.target, out.reason) for out in outs] == [
        ("webonly2024", "missing-archive — web source has no archive-url")
    ]


def test_web_archive_lint_accepts_an_archived_web_source(fixture_vault):
    web = fixture_vault / "literatures" / "webonly2024.md"
    web.write_text(
        '---\ncitekey: "webonly2024"\nurl: "https://example.org/post"\n'
        'archive-url: "https://archive.example.org/post"\n---\n# Web\n'
    )

    assert lints.lint_web_archive(fixture_vault) == []


def test_lints_report_malformed_frontmatter_without_crashing(fixture_vault):
    web = fixture_vault / "literatures" / "webonly2024.md"
    web.write_text('---\nurl: "https://example.org"\n')
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text() + "- (paraphrase) Old claim [@webonly2024] ^c-12345678\n"
    )

    source = lints.lint_screening_state(fixture_vault, draft)
    archive = lints.lint_web_archive(fixture_vault)

    assert source == [
        lints.Outcome(
            "screening-state",
            "webonly2024",
            Result.UNMATCHED,
            "schema-violation — malformed frontmatter",
            extra={
                "note_path": lints.RepoPath(b"projects/brief/draft.md"),
                "claim_id": "c-12345678",
            },
        )
    ]
    assert any(out.reason.startswith("schema-violation") for out in archive)


def _refresh_managed_witness(path):
    text = path.read_text()
    data, body = frontmatter.parse(text)
    data["managed-sha256"] = notes.managed_sha256(text.encode())
    path.write_text(frontmatter.serialize(data) + body)


@pytest.mark.parametrize("change", ["add", "edit", "delete", "rename"])
def test_managed_change_always_yields_typed_evidence_finding_with_fresh_witness(
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
    if change == "add":
        added = fixture_vault / "literatures" / "added.md"
        added.write_bytes(source.read_bytes())
        expected = "path-bytes:literatures/added.md"
    elif change == "edit":
        source.write_text(
            source.read_text().replace("# Mortality decline", "# Changed")
        )
        _refresh_managed_witness(source)
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

    finding = next(item for item in outcomes if item.result is Result.UNMATCHED)
    assert finding.check == "evidence-layer"
    assert finding.target == expected
    assert finding.target_kind == "repo-path"
    assert finding.reason.startswith("drift")


def test_free_region_only_edit_is_not_evidence_layer_change(fixture_vault):
    base = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=fixture_vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    source = fixture_vault / "literatures" / "smith2020.md"
    source.write_text(source.read_text() + "human free prose\n")

    outcomes = lints.lint_evidence_layer(
        gitstate.snapshot_tree(fixture_vault, base),
        gitstate.snapshot_worktree(fixture_vault),
    )

    assert not any(
        item.result is Result.UNMATCHED and item.reason.startswith("drift")
        for item in outcomes
    )


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
    """Mutate exactly one machine-owned frontmatter field, managed slice untouched."""
    if key == "archive-url":
        return text.replace(
            'doi: "10.1000/xyz"\n',
            'doi: "10.1000/xyz"\n'
            'archive-url: "https://web.archive.org/web/20260101000000/'
            'https://example.org/x"\n',
            1,
        )
    if key == "managed-sha256":
        digest = re.search(r'managed-sha256: "([0-9a-f]{64})"', text).group(1)
        return text.replace(digest, "b" * 64, 1)
    if key == "fixity-sha256":
        digest = re.search(r'fixity-sha256:\n  - "([0-9a-f]+)"', text).group(1)
        return text.replace(digest, "c" * 64, 1)
    if key == "generated":
        return text.replace(
            'generated: {by: "knowledge_harness/0.1.0"',
            'generated: {by: "human:hand-edit"',
            1,
        )
    if key == "citekey":
        return text.replace('citekey: "smith2020"', 'citekey: "smith2020x"', 1)
    raise ValueError(key)


@pytest.mark.parametrize(
    "key",
    ["archive-url", "managed-sha256", "fixity-sha256", "generated", "citekey"],
)
def test_hand_edited_machine_owned_frontmatter_key_is_drift(fixture_vault, key):
    """Task 17b: machine-owned frontmatter sits outside %%hk-managed%%, so a
    hand-edit to it — with the managed slice untouched and no writer
    attestation (a `generated` bump by the machine actor in the same diff) —
    must surface as drift, the same as a managed-region change would.
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


def test_screening_status_hand_edit_is_not_evidence_layer_drift(fixture_vault):
    """Screening state is deliberately human-writable (spec) — the guard must
    not treat it as machine-owned.
    """
    base = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=fixture_vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    source = fixture_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace('status: "included"', 'status: "excluded"', 1)
    )

    outcomes = lints.lint_evidence_layer(
        gitstate.snapshot_tree(fixture_vault, base),
        gitstate.snapshot_worktree(fixture_vault),
    )

    assert not any(
        item.result is Result.UNMATCHED and item.reason.startswith("drift")
        for item in outcomes
    )
