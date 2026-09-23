import re
import subprocess

import pytest

from research_vault import Result, frontmatter, gitstate, lints, literature_notes
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
    note = fixture_vault / "literature" / "smith2020.md"
    note.write_text(
        must_replace(note.read_text(), "Mortality fell 12%", "Mortality fell 21%")
    )

    outs = lints.lint_claim_immutability(fixture_vault)

    assert [(out.target, out.extra) for out in outs] == [
        (
            "smith2020#^c-11111111",
            {
                "note_path": "path-bytes:literature/smith2020.md",
                "claim_id": "c-11111111",
            },
        )
    ]


def test_claim_immutability_reports_each_claim_when_a_tracked_note_is_deleted(
    fixture_vault,
):
    (fixture_vault / "literature" / "smith2020.md").unlink()

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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    note = fixture_vault / "literature" / "smith2020.md"
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
    assert [out.reason for out in outs] == [
        "disputed-claim — mortality-trends#^c-55555555 has standing counter-evidence",
        "disputed-claim — smith2020#^c-11111111 has standing counter-evidence",
    ]


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
    data["managed-sha256"] = literature_notes.body_sha256(text)
    path.write_text(frontmatter.serialize(data) + body)


_FIXTURE_GENERATED = (
    'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}'
)


def _bump_generated(text: str, by: str = "research_vault/0.1.0") -> str:
    """What `literature_notes.render_note` does on every content change: a fresh `at`."""
    return must_replace(
        text,
        _FIXTURE_GENERATED,
        f'generated: {{by: "{by}", at: "2026-09-16T09:00:00Z"}}',
    )


def _base_tree(vault) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def _evidence_rows(vault, base):
    return [
        item
        for item in lints.lint_evidence_layer(
            gitstate.snapshot_tree(vault, base), gitstate.snapshot_worktree(vault)
        )
        if item.result is not Result.MATCHED
    ]


@pytest.mark.parametrize("write", ["add", "refresh", "rename"])
def test_an_attested_write_to_the_evidence_layer_is_not_drift(fixture_vault, write):
    """Capture, the compile refresh and propagate bump `generated` under the
    machine actor on every content change (`literature_notes.render_note`); the commit
    surface must let those writes through, or every capture blocks the next
    commit (ingest spec §6 amendment of 2026-09-16, Part B Task 1 T4)."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literature" / "smith2020.md"
    if write == "add":
        # A new capture: a note carrying a valid witness and a machine-class `generated`.
        added = fixture_vault / "literature" / "added.md"
        added.write_text(
            must_replace(
                source.read_text(), 'citationKey: "smith2020"', 'citationKey: "added"'
            )
        )
        _refresh_body_witness(added)
    elif write == "refresh":
        # The compile refresh: the body changes, `generated` moves, the witness is fresh.
        source.write_text(
            _bump_generated(
                source.read_text()
                + "\n## Compiled\n\n![[wiki/sources/Mortality decline.md]]\n"
            )
        )
        _refresh_body_witness(source)
    else:
        # Propagate: the note re-keys, is re-rendered at the new path, same Zotero identity.
        renamed = fixture_vault / "literature" / "smith2020b.md"
        renamed.write_text(
            _bump_generated(
                must_replace(
                    source.read_text(),
                    'citationKey: "smith2020"',
                    'citationKey: "smith2020b"',
                )
            )
        )
        _refresh_body_witness(renamed)
        source.unlink()

    rows = _evidence_rows(fixture_vault, base)

    assert rows == [], rows


@pytest.mark.parametrize("write", ["add", "edit", "rename", "delete"])
def test_an_unattested_write_to_the_evidence_layer_is_drift(fixture_vault, write):
    """The same four shapes with no writer attestation — a hand-written note,
    a hand edit that refreshed the witness, a bare `mv`, a deletion — each
    surface as exactly the drift row the shape names."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literature" / "smith2020.md"
    if write == "add":
        added = fixture_vault / "literature" / "added.md"
        added.write_text(
            must_replace(
                must_replace(
                    source.read_text(),
                    'citationKey: "smith2020"',
                    'citationKey: "added"',
                ),
                _FIXTURE_GENERATED,
                'generated: {by: "human:eran", at: "2026-09-16T09:00:00Z"}',
            )
        )
        _refresh_body_witness(added)
        expected = (
            "path-bytes:literature/added.md",
            "drift — literature note added without writer attestation",
        )
    elif write == "edit":
        source.write_text(
            must_replace(source.read_text(), "# Mortality decline", "# Changed")
        )
        _refresh_body_witness(source)
        expected = (
            "path-bytes:literature/smith2020.md",
            "drift — literature note body changed without writer attestation",
        )
    elif write == "rename":
        source.rename(fixture_vault / "literature" / "renamed.md")
        expected = (
            "path-bytes:literature/renamed.md",
            "drift — literature note renamed without writer attestation",
        )
    else:
        source.unlink()
        expected = (
            "path-bytes:literature/smith2020.md",
            "drift — literature note deleted",
        )

    rows = _evidence_rows(fixture_vault, base)

    matching = [item for item in rows if (item.target, item.reason) == expected]
    assert len(matching) == 1, rows
    assert matching[0].check == "evidence-layer"
    assert matching[0].result is Result.UNMATCHED
    assert matching[0].target_kind == "repo-path"
    if write == "rename":
        assert matching[0].extra["prior_path"] == "path-bytes:literature/smith2020.md"


def test_a_renamed_note_with_a_hand_edited_key_names_the_key(fixture_vault):
    """#21: the per-key attestation diagnostic reaches a renamed pair, so a
    bare `mv` that also edits a machine-owned key reports the key beside the
    wholesale rename row."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literature" / "smith2020.md"
    renamed = fixture_vault / "literature" / "renamed.md"
    renamed.write_text(
        must_replace(
            source.read_text(), "zotero-item-version: 12", "zotero-item-version: 13"
        )
    )
    source.unlink()

    reasons = {
        (item.target, item.reason) for item in _evidence_rows(fixture_vault, base)
    }

    assert reasons == {
        (
            "path-bytes:literature/renamed.md",
            "drift — literature note renamed without writer attestation",
        ),
        (
            "path-bytes:literature/renamed.md",
            "drift — zotero-item-version changed without writer attestation",
        ),
    }, reasons


def test_rename_pairs_by_zotero_identity_before_body_bytes(fixture_vault):
    """Propagate re-keys and re-renders, so the bytes differ; the pairing is
    decision 08's identity. A note with no tuple still pairs by body bytes.
    `_refresh_body_witness` also moves `managed-sha256` with no `generated`
    bump, so the per-key diagnostic that now reaches renamed pairs (#21)
    names that too — the rename row is not the only finding here."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literature" / "smith2020.md"
    renamed = fixture_vault / "literature" / "smith2020b.md"
    renamed.write_text(
        must_replace(
            source.read_text(), "# Mortality decline", "# Mortality decline, re-keyed"
        )
    )
    _refresh_body_witness(renamed)  # bytes differ from the base; `generated` untouched
    source.unlink()

    rows = _evidence_rows(fixture_vault, base)

    assert [item.reason for item in rows] == [
        "drift — literature note renamed without writer attestation",
        "drift — managed-sha256 changed without writer attestation",
    ], rows
    assert rows[0].extra["prior_path"] == "path-bytes:literature/smith2020.md"


def test_a_note_without_a_tuple_does_not_stop_identity_pairing(fixture_vault):
    """A note with no complete Zotero tuple has no identity; the pairing skips
    it (`continue`, not `break`, on a None key) and still pairs the next
    added note by identity, sorted right after it.

    Both the tuple-less note's body and the rename's body have to differ
    from the base note's own body — otherwise either one pairs with
    `smith2020.md` on the body-bytes fallback pass regardless of whether the
    identity pass ran, and hides a broken identity pass entirely (verified by
    hand: with an unchanged body on either note, this test still passes under
    a hand-flipped `break`)."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literature" / "smith2020.md"
    # Sorts before the rename below; no Zotero tuple, so `_note_identity`
    # returns None for it — and a body that cannot fallback-pair either, so
    # it never consumes `smith2020.md`'s removed slot on its own.
    bare = fixture_vault / "literature" / "aaa-bare.md"
    bare.write_text(
        must_replace(
            must_replace(
                source.read_text() + "a distinct bare body\n",
                'citationKey: "smith2020"',
                'citationKey: "aaa-bare"',
            ),
            'zotero-item-key: "SMITH020"\n',
            "",
        )
    )
    # Sorts after; same Zotero identity as the base note, but a changed body,
    # so only the identity pass -- not the body-bytes fallback -- can pair it.
    renamed = fixture_vault / "literature" / "zzz-renamed.md"
    renamed.write_text(
        must_replace(
            source.read_text(), "# Mortality decline", "# Mortality decline, re-keyed"
        )
    )
    source.unlink()

    rows = _evidence_rows(fixture_vault, base)

    assert not any(item.reason == "drift — literature note deleted" for item in rows), (
        rows
    )


def test_prose_appended_below_the_note_is_drift_with_or_without_a_fresh_witness(
    fixture_vault,
):
    """The free region is retired: the whole body is capture's. Hand-added
    prose is a stale witness when the person did not refresh it, and an
    unattested body change when they did; it is never silent."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literature" / "smith2020.md"
    source.write_text(source.read_text() + "hand-written prose\n")

    stale = {item.reason for item in _evidence_rows(fixture_vault, base)}
    # Exact: four strings share the `schema-violation` prefix on this path
    # (`literature_notes.py:124-131`, missing/duplicate/invalid/stale), so the
    # prefix cannot tell the stale witness this test is named for from the
    # other three (#22).
    assert "schema-violation — stale managed-sha256" in stale, stale

    _refresh_body_witness(source)
    fresh = {item.reason for item in _evidence_rows(fixture_vault, base)}
    assert "drift — literature note body changed without writer attestation" in fresh, (
        fresh
    )
    assert not any(reason.startswith("schema-violation") for reason in fresh), fresh


def test_stale_or_malformed_witness_is_schema_finding_even_without_git_change(
    fixture_vault,
):
    source = fixture_vault / "literature" / "smith2020.md"
    source.write_text(
        must_replace(source.read_text(), 'managed-sha256: "', 'managed-sha256: "A')
    )
    candidate = gitstate.snapshot_worktree(fixture_vault)

    outcomes = lints.lint_evidence_layer(candidate, candidate)

    finding = next(item for item in outcomes if item.result is Result.UNMATCHED)
    assert finding.check == "evidence-layer"
    assert finding.target_kind == "repo-path"
    assert finding.reason == "schema-violation — invalid managed-sha256"


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
    source = fixture_vault / "literature" / "smith2020.md"
    original = source.read_text()
    edited = _hand_edit_machine_owned_key(original, key)
    assert edited != original
    source.write_text(edited)

    outcomes = lints.lint_evidence_layer(
        gitstate.snapshot_tree(fixture_vault, base),
        gitstate.snapshot_worktree(fixture_vault),
    )

    expected_reason = f"drift — {key} changed without writer attestation"
    matching = [
        item
        for item in outcomes
        if item.target == "path-bytes:literature/smith2020.md"
        and item.reason == expected_reason
    ]
    assert matching, outcomes
    assert matching[0].check == "evidence-layer"


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
    `literature_notes._valid_generated` is the one place this field's shape is defined.
    """
    base = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=fixture_vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    source = fixture_vault / "literature" / "smith2020.md"
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
    source = fixture_vault / "literature" / "smith2020.md"
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
    source = fixture_vault / "literature" / "smith2020.md"
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
    source = fixture_vault / "literature" / "smith2020.md"
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
        and item.target == "path-bytes:literature/smith2020.md"
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
        "drift — literature note body changed without writer attestation",
    }


def test_screening_state_is_retired(fixture_vault):
    from research_vault import inbox, lints, verify

    assert not hasattr(lints, "lint_screening_state")
    assert "screening-state" not in inbox.CHECK_IDS
    assert "superseded-note" not in inbox.REASON_CODES
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    checks = {outcome.check for outcome in verify.file_outcomes(fixture_vault, draft)}
    assert "screening-state" not in checks


# --- boundaries pinned against mutation survivors -----------------------------


def _file(raw, data):
    return gitstate.FileImage(raw, "file", 0o100644, data)


_CLAIM = b'---\ncitationKey: "smith2020"\n---\n- (inference) A claim [@smith2020, p. 1] ^c-1\n'
_MUTATED = _CLAIM.replace(b"A claim", b"A changed claim")


def test_claim_immutability_watches_only_md_notes_under_its_roots(tmp_vault):
    """A mutated claim in a wiki page or in a non-.md file under literature/
    is not this lint's business; the same mutation under literature/ is."""
    base = gitstate.Snapshot(
        {
            b"wiki/concepts/a.md": _file(b"wiki/concepts/a.md", _CLAIM),
            b"literature/a.txt": _file(b"literature/a.txt", _CLAIM),
            b"literature": gitstate.FileImage(
                b"literature", "directory", 0o40000, None
            ),
            b"literature/b.md": _file(b"literature/b.md", _CLAIM),
        }
    )
    candidate = gitstate.Snapshot(
        {
            b"wiki/concepts/a.md": _file(b"wiki/concepts/a.md", _MUTATED),
            b"literature/a.txt": _file(b"literature/a.txt", _MUTATED),
            b"literature/b.md": _file(b"literature/b.md", _MUTATED),
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
    base = gitstate.Snapshot({b"literature/b.md": _file(b"literature/b.md", _CLAIM)})
    candidate = gitstate.Snapshot(
        {
            b"literature/a.md": _file(b"literature/a.md", _CLAIM),
            b"literature/b.md": _file(b"literature/b.md", _MUTATED),
        }
    )
    outs = lints.lint_claim_immutability(tmp_vault, base, candidate)
    assert [(o.check, o.target, o.result) for o in outs] == [
        ("claim-immutability", "smith2020#^c-1", Result.UNMATCHED)
    ]


def test_claim_target_is_the_claim_link_only_for_a_non_empty_string_key():
    text = '---\ncitationKey: "smith2020"\n---\n'
    assert lints._claim_target(b"literature/x.md", text, "c-1") == "smith2020#^c-1"
    for key in ('""', "5"):
        text = f"---\ncitationKey: {key}\n---\n"
        assert lints._claim_target(b"literature/x.md", text, "c-1") == RepoPath(
            b"literature/x.md"
        )


def test_claim_immutability_rows_a_malformed_candidate_by_its_path(tmp_vault):
    """A candidate whose frontmatter no longer parses is a schema row on the
    note's path (the head still parses); a deleted note whose head never
    parsed is not a schema row, only its vanished claims are drift."""
    base = gitstate.Snapshot({b"literature/b.md": _file(b"literature/b.md", _CLAIM)})
    candidate = gitstate.Snapshot(
        {b"literature/b.md": _file(b"literature/b.md", b"---\nnot a mapping\n---\n")}
    )
    outs = lints.lint_claim_immutability(tmp_vault, base, candidate)
    assert (outs[0].check, outs[0].target, outs[0].result, outs[0].reason) == (
        "claim-immutability",
        "path-bytes:literature/b.md",
        Result.UNMATCHED,
        "schema-violation — malformed frontmatter",
    )
    malformed_head = gitstate.Snapshot(
        {
            b"literature/c.md": _file(
                b"literature/c.md",
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
    (vault / "literature").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=vault, check=True)
    (vault / "literature" / "a.md").write_bytes(_CLAIM)
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
    target, extra = lints._origin(
        tmp_vault, note, anchored, note.read_text(encoding="utf-8")
    )
    assert target == "brief2020#^c-1"
    assert extra == {
        "note_path": RepoPath(b"projects/brief/draft.md"),
        "claim_id": "c-1",
    }
    target, _extra = lints._origin(
        tmp_vault, note, unanchored, note.read_text(encoding="utf-8")
    )
    assert target == RepoPath(b"projects/brief/draft.md")
    note.write_text('---\ncitationKey: ""\n---\n')
    target, _extra = lints._origin(
        tmp_vault, note, anchored, note.read_text(encoding="utf-8")
    )
    assert target == RepoPath(b"projects/brief/draft.md")


def test_body_bytes_and_frontmatter_need_a_file_image():
    directory = gitstate.FileImage(b"literature/d", "directory", 0o40000, None)
    assert lints._body_bytes(None) is None
    assert lints._body_bytes(directory) is None
    assert lints._frontmatter(None) is None
    assert lints._frontmatter(directory) is None
    note = _file(b"literature/a.md", _CLAIM)
    assert lints._body_bytes(note) == b"- (inference) A claim [@smith2020, p. 1] ^c-1\n"
    assert lints._frontmatter(note) == {"citationKey": "smith2020"}
    # An empty file reads as an empty body and no frontmatter, not as junk.
    empty = _file(b"literature/a.md", b"")
    assert lints._body_bytes(empty) == b""
    assert lints._frontmatter(empty) == lints._frontmatter(_file(b"x.md", b"body\n"))


def test_note_identity_needs_data_and_a_complete_tuple():
    """`_note_identity` takes only images `_literature_files` can yield — no
    `None`, no non-"file" kind is a call it has to handle — so its only guard
    is `image.data is None`. A note with no complete Zotero tuple also reads
    as no identity."""
    directory = gitstate.FileImage(b"literature/d", "directory", 0o40000, None)
    assert lints._note_identity(directory) is None
    assert lints._note_identity(_file(b"literature/a.md", _CLAIM)) is None
    tupled = _file(
        b"literature/a.md",
        b'---\nzotero-server-id: "S1"\nzotero-item-key: "ABCDEFG1"\n'
        b'zotero-item-version: 1\ncitationKey: "a2020"\n---\nbody\n',
    )
    assert lints._note_identity(tupled) == ("S1", "ABCDEFG1")


def _duplicate(text: str, key: str, first: str, last: str) -> str:
    """The fixture's `<key>: "<value>"` line duplicated: `first` above `last`."""
    line = next(line for line in text.splitlines() if line.startswith(f"{key}: "))
    return must_replace(text, line + "\n", f'{key}: "{first}"\n{key}: "{last}"\n')


@pytest.mark.parametrize(
    ("first", "last"),
    [("evil", "smith2020"), ("smith2020", "evil"), ("smith2020", "smith2020")],
    ids=["evil-first", "evil-last", "equal"],
)
def test_a_duplicated_capture_field_on_a_surviving_note_is_a_schema_violation(
    fixture_vault, first, last
):
    """#20: `data.get(key)` is last-key-wins, so `citationKey: "evil"` then
    `citationKey: "smith2020"` (equal to base) reported nothing. One row per
    duplicated key, and the drift comparison is skipped for that file — the
    duplicate is the finding, not whichever copy won."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literature" / "smith2020.md"
    source.write_text(_duplicate(source.read_text(), "citationKey", first, last))
    _refresh_body_witness(source)

    rows = _evidence_rows(fixture_vault, base)

    assert [(r.result, r.reason) for r in rows] == [
        (Result.UNMATCHED, "schema-violation — duplicate citationKey")
    ]
    assert all(r.target == "path-bytes:literature/smith2020.md" for r in rows)


@pytest.mark.parametrize("leg", ["surviving", "added"])
def test_a_duplicated_generated_never_attests(fixture_vault, leg):
    """A duplicated `generated`, human-first machine-last with a bumped `at`
    beside an altered key, used to attest the edit; on the added leg the
    same shape used to read as an attested new note."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literature" / "smith2020.md"
    text = must_replace(source.read_text(), 'DOI: "10.1000/xyz"', 'DOI: "10.1000/evil"')
    text = must_replace(
        text,
        _FIXTURE_GENERATED + "\n",
        'generated: {by: "human:eran", at: "2026-08-16T09:00:00Z"}\n'
        'generated: {by: "research_vault/0.1.0", at: "2026-09-17T09:00:00Z"}\n',
    )
    if leg == "added":
        target = fixture_vault / "literature" / "added.md"
        text = must_replace(text, 'citationKey: "smith2020"', 'citationKey: "added"')
    else:
        target = source
    target.write_text(text)
    _refresh_body_witness(target)

    rows = _evidence_rows(fixture_vault, base)

    duplicate_rows = [
        r for r in rows if r.reason == "schema-violation — duplicate generated"
    ]
    assert len(duplicate_rows) == 1
    assert duplicate_rows[0].target == f"path-bytes:literature/{target.name}"
    assert not [r for r in rows if r.reason.startswith("drift — DOI")]
    assert not [r for r in rows if "added without writer attestation" in r.reason]


def test_a_duplicate_in_the_base_that_capture_cleaned_is_not_a_finding(fixture_vault):
    """The cleaning path: the base carries a human-made duplicate; capture
    re-renders each capture key once (the candidate is clean) under a fresh
    machine `generated`. Candidate-side only, so this is []."""
    source = fixture_vault / "literature" / "smith2020.md"
    clean = source.read_text()
    source.write_text(_duplicate(clean, "citationKey", "smith2020", "smith2020"))
    subprocess.run(["git", "add", "-A"], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "a duplicated key in the base"],
        cwd=fixture_vault,
        check=True,
    )
    base = _base_tree(fixture_vault)
    source.write_text(_bump_generated(clean))
    _refresh_body_witness(source)

    assert _evidence_rows(fixture_vault, base) == []


def _added_note_keyed(fixture_vault, item_key_lines: str) -> None:
    """`literature/evil.md`: the fixture note under a new citation key, its
    `zotero-item-key` line replaced by `item_key_lines`, and one extra body
    line — so nothing can pair with it on the body-bytes fallback and the
    identity pass is the only pass in play."""
    source = fixture_vault / "literature" / "smith2020.md"
    text = must_replace(
        source.read_text(), 'citationKey: "smith2020"', 'citationKey: "evil"'
    )
    text = must_replace(text, 'zotero-item-key: "SMITH020"\n', item_key_lines)
    (fixture_vault / "literature" / "evil.md").write_text(
        text + "a body no other note carries\n"
    )


def test_an_added_note_with_an_unrelated_identity_leaves_the_deletion_reported(
    fixture_vault,
):
    """The control for the test below: an added note whose identity matches no
    removed note pairs with nothing, so the deleted note keeps its own row.
    Without this leg, the duplicate test could pass on a scenario that never
    produced a deletion row at all."""
    base = _base_tree(fixture_vault)
    _added_note_keyed(fixture_vault, 'zotero-item-key: "OTHER001"\n')
    (fixture_vault / "literature" / "gone2019.md").unlink()

    rows = {(item.target, item.reason) for item in _evidence_rows(fixture_vault, base)}

    assert rows == {
        ("path-bytes:literature/evil.md", "schema-violation — stale managed-sha256"),
        ("path-bytes:literature/gone2019.md", "drift — literature note deleted"),
    }, rows


def test_a_duplicated_identity_cannot_pair_away_a_deleted_note(fixture_vault):
    """#20 on the rename pairing: `_note_identity` reads `zotero-item-key`
    through the same last-key-wins mapping, so an added note whose *last*
    copy of the key is a removed note's identity used to pair with it and
    swallow `drift — literature note deleted` (ADR 0003: no verb deletes a
    literature note) behind one schema-violation row naming a different
    problem. A duplicate disqualifies the file from the pairing, not only
    from the drift comparison — the control above is the same scenario with
    a single key."""
    base = _base_tree(fixture_vault)
    _added_note_keyed(
        fixture_vault, 'zotero-item-key: "BOGUS001"\nzotero-item-key: "GONE2019"\n'
    )
    (fixture_vault / "literature" / "gone2019.md").unlink()

    rows = {(item.target, item.reason) for item in _evidence_rows(fixture_vault, base)}

    assert rows == {
        (
            "path-bytes:literature/evil.md",
            "schema-violation — duplicate zotero-item-key",
        ),
        ("path-bytes:literature/evil.md", "schema-violation — stale managed-sha256"),
        ("path-bytes:literature/gone2019.md", "drift — literature note deleted"),
    }, rows


def test_a_duplicated_key_leaves_an_attested_rename_paired_by_body_bytes(fixture_vault):
    """The exclusion above is the identity pass's alone. `_body_bytes` hashes
    the note body, which no duplicated frontmatter key can reach, so a rename
    it can pair is still a rename: excluding the file from that pass too minted
    `drift — literature note deleted` — ADR 0003's row, the loudest this check
    emits — for a note nobody deleted. Here the propagate re-keys `smith2020`
    under a machine `generated` bump and the candidate also carries a
    duplicated `accessed`; the duplicate is the one finding."""
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literature" / "smith2020.md"
    text = _bump_generated(
        must_replace(
            source.read_text(), 'citationKey: "smith2020"', 'citationKey: "smith2020b"'
        )
    )
    # The body is untouched, so `managed-sha256` stays fresh and the body-bytes
    # pass sees the same key on both sides.
    (fixture_vault / "literature" / "smith2020b.md").write_text(
        _duplicate(text, "accessed", "2026-08-16", "2026-09-16")
    )
    source.unlink()

    rows = {(item.target, item.reason) for item in _evidence_rows(fixture_vault, base)}

    assert rows == {
        ("path-bytes:literature/smith2020b.md", "schema-violation — duplicate accessed")
    }, rows


def _base_note_keyed(fixture_vault, item_key_lines: str) -> str:
    """`literature/gone2019.md`'s `zotero-item-key` line replaced by
    `item_key_lines` and committed, so the replacement is the *base* image the
    pairing reads. Returns the tree the candidate is judged against."""
    source = fixture_vault / "literature" / "gone2019.md"
    source.write_text(
        must_replace(
            source.read_text(), 'zotero-item-key: "GONE2019"\n', item_key_lines
        )
    )
    subprocess.run(["git", "add", "-A"], cwd=fixture_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "the base note's identity"],
        cwd=fixture_vault,
        check=True,
    )
    return _base_tree(fixture_vault)


def _note_from_gone2019(fixture_vault, clean: str, name: str, body: str) -> None:
    """`literature/<name>.md` rendered from `gone2019.md`'s pristine text: a new
    citation key, `TARGET01` as its single `zotero-item-key`, `body` appended
    and a machine `generated` bump with a fresh witness. Every write here is
    attested, so only the pairing decides whether `gone2019.md` reads as
    deleted."""
    text = must_replace(
        clean, 'zotero-item-key: "GONE2019"', 'zotero-item-key: "TARGET01"'
    )
    text = _bump_generated(
        must_replace(text, 'citationKey: "gone2019"', f'citationKey: "{name}"')
    )
    note = fixture_vault / "literature" / f"{name}.md"
    note.write_text(text + body)
    _refresh_body_witness(note)


@pytest.mark.parametrize(
    "base_item_key_lines",
    [
        pytest.param(
            'zotero-item-key: "GONE2019"\nzotero-item-key: "TARGET01"\n',
            id="duplicated",
        ),
        pytest.param('zotero-item-key: "OTHER001"\n', id="single"),
    ],
)
def test_a_duplicated_identity_in_the_base_cannot_pair_away_its_deletion(
    fixture_vault, base_item_key_lines
):
    """#20 symmetrically: `removed_by_key` reads the base note through the same
    last-key-wins mapping, so a base note whose *last* `zotero-item-key` is an
    added note's key used to pair with it and lose its own
    `drift — literature note deleted` row entirely — no row at all, where the
    candidate-side shape at least reported the duplicate. A base note carrying
    one supplies no identity key either. No candidate-style schema-violation
    row rides along: those are pinned candidate-side and the base is committed
    history. The `single` leg is the same scenario with an unrelated base
    key — the deletion row this check owes, arrived at without a duplicate."""
    clean = (fixture_vault / "literature" / "gone2019.md").read_text()
    base = _base_note_keyed(fixture_vault, base_item_key_lines)
    _note_from_gone2019(fixture_vault, clean, "evil", "a body no other note carries\n")
    (fixture_vault / "literature" / "gone2019.md").unlink()

    rows = {(item.target, item.reason) for item in _evidence_rows(fixture_vault, base)}

    assert rows == {
        ("path-bytes:literature/gone2019.md", "drift — literature note deleted")
    }, rows


def test_a_duplicated_identity_in_the_base_still_pairs_on_body_bytes(fixture_vault):
    """The base-side twin of the candidate-side rule above: the duplicate costs
    the note its identity, not its body. `gone2019` carries a duplicated
    `zotero-item-key` in the base and is re-keyed under a machine `generated`
    bump with its body untouched, so the body-bytes pass pairs the rename and
    there is nothing to report. Excluding the base note from that pass too
    would mint the deletion row for a renamed note."""
    source = fixture_vault / "literature" / "gone2019.md"
    clean = source.read_text()
    base = _base_note_keyed(
        fixture_vault, 'zotero-item-key: "GONE2019"\nzotero-item-key: "TARGET01"\n'
    )
    _note_from_gone2019(fixture_vault, clean, "gone2019b", "")
    source.unlink()

    rows = {(item.target, item.reason) for item in _evidence_rows(fixture_vault, base)}

    assert rows == set(), rows


def test_lint_disputed_claim_reports_an_undecodable_page_and_still_judges_the_note(
    fixture_vault,
):
    page = fixture_vault / "wiki" / "concepts" / "mortality-trends.md"
    page.write_bytes(b"\xff\xfe")
    rows = lints.lint_disputed_claim(
        fixture_vault, fixture_vault / "projects" / "brief" / "draft.md"
    )
    (page_row,) = [
        r for r in rows if r.target == "path-bytes:wiki/concepts/mortality-trends.md"
    ]
    assert (page_row.check, page_row.result) == ("disputed-claim", Result.UNMATCHED)
    # The tail is the codec's; the byte it names is the one the fixture planted.
    assert page_row.reason.startswith(
        "schema-violation — not UTF-8: 'utf-8' codec can't decode byte 0xff"
    )


def test_lint_disputed_claim_reports_an_undecodable_note(fixture_vault):
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_bytes(b"\xff\xfe")
    (row,) = lints.lint_disputed_claim(fixture_vault, draft)
    assert (row.check, row.target, row.result) == (
        "disputed-claim",
        "path-bytes:projects/brief/draft.md",
        Result.UNMATCHED,
    )
    assert row.reason.startswith(
        "schema-violation — not UTF-8: 'utf-8' codec can't decode byte 0xff"
    )
