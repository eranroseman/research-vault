"""Integration regressions for the verify and inbox command surface."""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from research_vault import (
    Result,
    bibliography,
    checks,
    claims,
    events,
    gitstate,
    inbox,
)
from research_vault.__main__ import cmd_inbox, cmd_verify, main
from research_vault.pathcodec import PathCodecError, RepoPath, encode_repo_path
from research_vault.verify import (
    _apply_state_transitions,
    _file_effects,
    _mutate_marker,
    _note_bytes,
    _safe_relative,
    _target_hash,
    verify_state,
)


def run_verify(vault_root, **kwargs):
    """Report projection of the verification transaction, for assertions only."""
    return verify_state(vault_root, **kwargs)[0]


def _outcome(check, target, result, reason, **extra):
    if isinstance(extra.get("note_path"), str):
        extra["note_path"] = RepoPath(os.fsencode(extra["note_path"]))
    if check == "append-only" and isinstance(target, str):
        target = RepoPath(os.fsencode(target))
    return checks.Outcome(check, target, result, reason, extra)


def _git_bytes(vault, *args, stdin=None):
    return subprocess.run(
        ["git", *args], cwd=vault, input=stdin, check=True, capture_output=True
    ).stdout


@pytest.mark.parametrize(
    ("discovery_result", "want"),
    [(Result.SKIPPED, Result.SKIPPED), (Result.UNREACHABLE, Result.UNREACHABLE)],
)
def test_no_doi_distinguishes_healthy_no_hit_from_discovery_outage(
    net_vault, monkeypatch, discovery_result, want
):
    monkeypatch.setattr(
        "research_vault.verify._bibliography_entries",
        lambda _: [{"id": "empty", "title": "T"}],
    )
    monkeypatch.setattr(
        "research_vault.identify.discover",
        lambda *_: _outcome(
            "identifier-discovery",
            "empty",
            discovery_result,
            "no-identifier — no hit"
            if discovery_result is Result.SKIPPED
            else "outage — unavailable",
            identifiers={},
        ),
    )
    report = run_verify(net_vault, network=True, detection_date="2026-08-16")
    got = {o.check: o.result for o in report["outcomes"] if o.target == "empty"}
    assert got["update-notice"] is want


def test_discovery_outage_with_only_pmid_keeps_live_update_unreachable(
    net_vault, monkeypatch
):
    monkeypatch.setattr(
        "research_vault.verify._bibliography_entries",
        lambda _: [{"id": "pmid-only", "title": "T"}],
    )
    monkeypatch.setattr(
        "research_vault.identify.discover",
        lambda *_: _outcome(
            "identifier-discovery",
            "pmid-only",
            Result.UNREACHABLE,
            "outage — Crossref unavailable",
            identifiers={"PMID": "123"},
        ),
    )
    report = run_verify(net_vault, network=True, detection_date="2026-08-16")
    update = next(
        outcome
        for outcome in report["outcomes"]
        if outcome.check == "update-notice" and outcome.target == "pmid-only"
    )
    assert update.result is Result.UNREACHABLE


def test_update_notice_is_one_effective_outcome_with_rw_blocker_offline(
    net_vault, tmp_path, monkeypatch
):
    csv_file = tmp_path / "rw.csv"
    csv_file.write_text(
        "OriginalPaperDOI,OriginalPaperPubMedID,RetractionDate,RetractionNature\n,123,2020-01-01,Retraction\n"
    )
    monkeypatch.setattr(
        "research_vault.verify._bibliography_entries",
        lambda _: [{"id": "pmid", "PMID": "123"}],
    )
    report = run_verify(
        net_vault, network=False, detection_date="2026-08-16", rw_csv=csv_file
    )
    notices = [
        o
        for o in report["outcomes"]
        if o.check == "update-notice" and o.target == "pmid"
    ]
    assert len(notices) == 1
    assert notices[0].result is Result.UNMATCHED


def test_ack_suppresses_effects_but_retains_raw_outcome_and_reopens_on_hash(net_vault):
    draft = net_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text().replace(
            "Mortality fell 12% across all strata.", "wrong quote"
        )
    )
    first = run_verify(net_vault, network=False, detection_date="2026-08-16")
    raw = next(
        o
        for o in first["outcomes"]
        if o.check == "quote" and o.result is Result.UNMATCHED
    )
    target_hash = _target_hash(net_vault, raw)
    entry = next(
        e
        for e in inbox.open_entries(net_vault)
        if e.check == "quote" and e.target == raw.target
    )
    inbox.append_ack(net_vault, entry.id, "manual — checked", "human:test", target_hash)
    second = run_verify(net_vault, network=False, detection_date="2026-08-16")
    assert any(
        o is not None and o.check == "quote" and o.result is Result.UNMATCHED
        for o in second["outcomes"]
    )
    assert "[failed-verification:: quote/" in draft.read_text()
    assert not any(
        e.check == "quote" and e.target == raw.target
        for e in inbox.open_entries(net_vault)
    )
    draft.write_text(draft.read_text().replace("wrong quote", "different wrong quote"))
    run_verify(net_vault, network=False, detection_date="2026-08-16")
    assert not any(
        e.check == "quote" and e.target == raw.target
        for e in inbox.open_entries(net_vault)
    )
    source = net_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            '  - "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"',
            '  - "bb22bb22bb22bb22bb22bb22bb22bb22bb22bb22bb22bb22bb22bb22bb22bb22"',
        )
    )
    # Committed so `lint_evidence_layer`'s base and candidate agree on the
    # changed fixity-sha256 — this test exercises hash-based reopening, not
    # the machine-owned-frontmatter guard.
    subprocess.run(["git", "add", "-A"], cwd=net_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "change fixity-sha256"], cwd=net_vault, check=True
    )
    fourth = run_verify(net_vault, network=False, detection_date="2026-08-16")
    assert any(
        e.check == "quote" and e.target == raw.target
        for e in inbox.open_entries(net_vault)
    )
    assert fourth["counts"]["UNMATCHED"] >= 1


def test_target_hash_routes_safe_file_claim_and_citekey(net_vault):
    file_outcome = _outcome(
        "append-only", "log/2026-08-16.md", Result.UNMATCHED, "drift — file"
    )
    claim_outcome = _outcome(
        "quote", "smith2020#^c-11111111", Result.UNMATCHED, "mismatch — quote"
    )
    citekey_outcome = _outcome("doi", "smith2020", Result.UNMATCHED, "mismatch — doi")
    assert (
        _target_hash(net_vault, file_outcome)
        == hashlib.sha256((net_vault / "log/2026-08-16.md").read_bytes()).hexdigest()[
            :16
        ]
    )
    claim_hash = _target_hash(net_vault, claim_outcome)
    assert claim_hash == "aa11" * 16
    source = net_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            "^c-11111111", "[failed-verification:: quote/2026-08-16] ^c-11111111"
        )
    )
    assert _target_hash(net_vault, claim_outcome) == "aa11" * 16
    assert _target_hash(net_vault, citekey_outcome) == "aa11" * 16
    with pytest.raises(PathCodecError):
        RepoPath(b"../outside")


@pytest.mark.parametrize("placeholder", ["unresolved", "aa11"])
def test_ack_hash_rejects_placeholder_fixity_live_file(net_vault, placeholder):
    """Live-file branch of ``_citekey_hash`` (no ``candidate_snapshot``).

    Two shapes, not one: "unresolved" is non-hex (fails the character
    class), "aa11" is valid hex but short (fails the length bound) — so
    this also pins the ``{64}`` bound, not just hex-ness.
    """
    source = net_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            '  - "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"',
            f'  - "{placeholder}"',
        )
    )
    claim_outcome = _outcome(
        "quote", "smith2020#^c-11111111", Result.UNMATCHED, "mismatch — quote"
    )
    expected = hashlib.sha256(_note_bytes(source.read_bytes())).hexdigest()[:16]
    result = _target_hash(net_vault, claim_outcome)
    assert result != placeholder
    assert result == expected


@pytest.mark.parametrize("placeholder", ["unresolved", "aa11"])
def test_ack_hash_rejects_placeholder_fixity_candidate_snapshot(net_vault, placeholder):
    """Snapshot branch of ``_citekey_hash`` (explicit ``candidate_snapshot``).

    Two shapes, not one: "unresolved" is non-hex (fails the character
    class), "aa11" is valid hex but short (fails the length bound) — so
    this also pins the ``{64}`` bound, not just hex-ness.
    """
    source = net_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            '  - "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"',
            f'  - "{placeholder}"',
        )
    )
    candidate_snapshot = gitstate.snapshot_worktree(net_vault)
    claim_outcome = _outcome(
        "quote", "smith2020#^c-11111111", Result.UNMATCHED, "mismatch — quote"
    )
    expected = hashlib.sha256(_note_bytes(source.read_bytes())).hexdigest()[:16]
    result = _target_hash(
        net_vault, claim_outcome, candidate_snapshot=candidate_snapshot
    )
    assert result != placeholder
    assert result == expected


def test_ack_hash_falls_through_when_fixity_is_empty_list(net_vault):
    """A present-but-empty ``fixity-sha256`` list — the shape Task 17's side
    (a) now writes when every attachment fails to resolve — falls through to
    the managed-bytes hash on both ``_citekey_hash`` branches, same as an
    absent key.
    """
    source = net_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            'fixity-sha256:\n  - "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"\n',
            "fixity-sha256:\n",
        )
    )
    claim_outcome = _outcome(
        "quote", "smith2020#^c-11111111", Result.UNMATCHED, "mismatch — quote"
    )
    expected = hashlib.sha256(_note_bytes(source.read_bytes())).hexdigest()[:16]
    assert _target_hash(net_vault, claim_outcome) == expected
    candidate_snapshot = gitstate.snapshot_worktree(net_vault)
    assert (
        _target_hash(net_vault, claim_outcome, candidate_snapshot=candidate_snapshot)
        == expected
    )


@pytest.mark.parametrize("newline", ["\n", "\r\n"], ids=["lf", "crlf"])
@pytest.mark.parametrize(
    "frontmatter_line", ["", 'status: "included"'], ids=["empty", "nonempty"]
)
def test_preclose_blank_event_keeps_no_attachment_ack_hash(
    net_vault, newline, frontmatter_line
):
    existing_fields = f"{frontmatter_line}{newline}" if frontmatter_line else ""
    body = f"- (quote) body ^c-11111111{newline}"
    text = f"---{newline}{existing_fields}{newline}---{newline}{body}"
    note = net_vault / "literatures" / "blank.md"
    note.write_bytes(text.encode())
    outcome = _outcome("doi", "blank", Result.UNMATCHED, "mismatch — DOI")
    before = _target_hash(net_vault, outcome)
    entry = inbox.append_entry(
        net_vault,
        outcome.check,
        outcome.target,
        outcome.result,
        outcome.reason,
        date="2026-08-16",
        target_hash=before,
    )
    inbox.append_ack(
        net_vault,
        entry.id,
        "manual — checked",
        "human:test",
        target_hash=before,
    )

    note.write_bytes(
        events.record_pass(text, "doi", Result.MATCHED, at="2026-08-17").encode()
    )

    after = _target_hash(net_vault, outcome)
    assert after == before
    assert inbox.is_acknowledged(
        net_vault, outcome.check, outcome.target, current_hash=after
    )


def test_missing_citekey_hash_uses_exact_checked_origins_and_reopens(net_vault):
    draft = net_vault / "projects" / "brief" / "draft.md"
    outcome = _outcome(
        "citekey",
        "fabricated2020",
        Result.UNMATCHED,
        "mismatch — citekey not in bibliography",
        note_path="projects/brief/draft.md",
        claims=[{"claim_id": "c-77777777"}],
    )
    original = _target_hash(net_vault, outcome)
    assert original is not None
    draft.write_text(draft.read_text().replace("This will replicate", "This will not"))
    assert _target_hash(net_vault, outcome) != original


def test_no_note_bibliography_target_hashes_its_canonical_entry(net_vault):
    path = net_vault / "system" / "bibliography.json"
    entries = json.loads(path.read_text())
    entries.append({"id": "noted-yet", "title": "Admitted bibliography entry"})
    path.write_text(json.dumps(entries))
    outcome = _outcome("doi", "noted-yet", Result.UNMATCHED, "mismatch — DOI")
    assert _target_hash(net_vault, outcome) is not None


def test_unanchored_claim_marker_uses_its_exact_line_origin(net_vault):
    draft = net_vault / "projects" / "brief" / "draft.md"
    line_no = next(
        number
        for number, line in enumerate(draft.read_text().splitlines(), start=1)
        if "This will replicate" in line
    )
    outcome = _outcome(
        "quote",
        "smith2020",
        Result.UNMATCHED,
        "schema-violation — quote claim has no anchor",
        note_path="projects/brief/draft.md",
        line_no=line_no,
    )
    _mutate_marker(net_vault, outcome, "2026-08-16")
    assert (
        "failed-verification:: quote/2026-08-16"
        in draft.read_text().splitlines()[line_no - 1]
    )
    _mutate_marker(net_vault, outcome, "2026-08-16", clear=True)
    assert "failed-verification" not in draft.read_text().splitlines()[line_no - 1]


def test_matching_outcome_still_mints_event_after_same_hash_ack(net_vault, monkeypatch):
    entry = inbox.append_entry(
        net_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "mismatch — old result",
        target_hash="aa11" * 16,
    )
    inbox.append_ack(net_vault, entry.id, "manual — checked", "human:test", "aa11" * 16)
    monkeypatch.setattr(
        "research_vault.verify._bibliography_entries",
        lambda _: [{"id": "smith2020", "DOI": "10.1000/xyz"}],
    )
    monkeypatch.setattr(
        "research_vault.verify._network_outcomes",
        lambda *_: [_outcome("update-notice", "smith2020", Result.MATCHED, "matched")],
    )
    run_verify(net_vault, network=True, detection_date="2026-08-16")
    assert any(
        event["check"] == "update-notice"
        for event in events.verified_checks(
            (net_vault / "literatures" / "smith2020.md").read_text()
        )
    )


def test_run_verify_mints_exact_quote_event_on_cited_literature_note(net_vault):
    report = run_verify(net_vault, network=False, detection_date="2026-08-16")
    assert any(
        outcome.check == "citekey"
        and outcome.target == "fabricated2020"
        and outcome.result is Result.UNMATCHED
        for outcome in report["outcomes"]
    )
    assert all(
        outcome.result is Result.UNREACHABLE
        for outcome in report["outcomes"]
        if outcome.check == "doi"
    )
    quote_outcomes = [
        outcome for outcome in report["outcomes"] if outcome.check == "quote"
    ]
    assert any(outcome.result is Result.MATCHED for outcome in quote_outcomes)
    assert not any(outcome.result is Result.UNMATCHED for outcome in quote_outcomes)
    first_entries = [
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.check == "citekey" and entry.target == "fabricated2020"
    ]
    run_verify(net_vault, network=False, detection_date="2026-08-16")
    second_entries = [
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.check == "citekey" and entry.target == "fabricated2020"
    ]
    run_verify(net_vault, network=False, detection_date="2026-08-16")
    third_entries = [
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.check == "citekey" and entry.target == "fabricated2020"
    ]
    assert len(first_entries) == 1
    assert len(second_entries) == len(third_entries) == 2
    assert first_entries[0].target_hash != second_entries[-1].target_hash
    source = (net_vault / "literatures" / "smith2020.md").read_text()
    recorded = {event["check"] for event in events.verified_checks(source)}
    assert "quote:smith2020#^c-66666666:managed-region" in recorded


def test_cli_prints_unacknowledged_nested_warn_notice(net_vault, monkeypatch, capsys):
    warning = _outcome(
        "update-notice",
        "smith2020",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction", "notice_date": "2026-01-01"}],
    )
    monkeypatch.setattr(
        "research_vault.__main__.verify_state",
        lambda *_args, **_kwargs: (
            {"outcomes": [warning], "counts": {"MATCHED": 1}},
            [warning],
            {id(warning): "aa11"},
            {id(warning): True},
        ),
    )
    code = cmd_verify(
        type("Args", (), {"vault": net_vault, "offline": True, "rw_csv": None})()
    )
    assert code == 0
    assert "warn-notice — correction" in capsys.readouterr().out


def test_cli_prints_warning_alongside_blocking_update_notice(
    net_vault, monkeypatch, capsys
):
    outcome = _outcome(
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "retracted — retraction",
        warn_notices=[{"type": "correction"}],
    )
    monkeypatch.setattr(
        "research_vault.__main__.verify_state",
        lambda *_args, **_kwargs: (
            {"outcomes": [outcome], "counts": {"UNMATCHED": 1}},
            [outcome],
            {id(outcome): "aa11"},
            {id(outcome): True},
        ),
    )
    cmd_verify(
        type("Args", (), {"vault": net_vault, "offline": True, "rw_csv": None})()
    )
    output = capsys.readouterr().out
    assert "retracted — retraction" in output
    assert "warn-notice — correction" in output


def test_acknowledged_matched_warn_mints_event_without_refiling_or_printing(
    net_vault, monkeypatch, capsys
):
    entry = inbox.append_entry(
        net_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — correction",
        target_hash="aa11" * 16,
        notice_class="warn",
        notice_type="correction",
    )
    inbox.append_ack(net_vault, entry.id, "manual — checked", "human:test", "aa11" * 16)
    warning = _outcome(
        "update-notice",
        "smith2020",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction"}],
    )
    monkeypatch.setattr(
        "research_vault.verify._bibliography_entries",
        lambda _: [{"id": "smith2020", "DOI": "10.1000/xyz"}],
    )
    monkeypatch.setattr("research_vault.verify._network_outcomes", lambda *_: [warning])
    cmd_verify(
        type("Args", (), {"vault": net_vault, "offline": False, "rw_csv": None})()
    )
    source = (net_vault / "literatures" / "smith2020.md").read_text()
    assert any(
        event["check"] == "update-notice" for event in events.verified_checks(source)
    )
    assert not any(
        item.reason == "warn-notice — correction"
        for item in inbox.open_entries(net_vault)
    )
    assert "warn-notice — correction" not in capsys.readouterr().out


def test_apply_state_transitions_routes_unmatched_update_notice_to_failure_not_a_mint(
    net_vault,
):
    """A non-MATCHED update-notice outcome must record a failure, never mint
    a verified event."""
    outcome = checks.Outcome(
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "mismatch — version differs",
    )

    _apply_state_transitions(net_vault, [outcome], "2026-08-16")

    source = (net_vault / "literatures" / "smith2020.md").read_text()
    assert not any(
        event["check"] == "update-notice" for event in events.verified_checks(source)
    )
    assert any(
        row["check"] == "update-notice" for row in events.current_failures(source)
    )


def test_cli_exit_precedence_ignores_warns_but_closing_beats_unreachable(
    net_vault, monkeypatch
):
    args = type(
        "Args",
        (),
        {"vault": net_vault, "offline": True, "rw_csv": None, "surface": "publish"},
    )()
    cases = [
        (
            [
                _outcome(
                    "update-notice",
                    "smith2020",
                    Result.UNMATCHED,
                    "retracted — retraction",
                ),
                _outcome("doi", "smith2020", Result.UNREACHABLE, "outage — down"),
            ],
            1,
        ),
        ([_outcome("metadata", "smith2020", Result.UNMATCHED, "mismatch — title")], 0),
        ([_outcome("doi", "smith2020", Result.UNREACHABLE, "outage — down")], 3),
    ]
    for outcomes, expected in cases:
        monkeypatch.setattr(
            "research_vault.__main__.verify_state",
            lambda *_args, items=outcomes, **_kwargs: (
                {"outcomes": items, "counts": {}},
                items,
                {id(item): "aa11" for item in items},
                {id(item): True for item in items},
            ),
        )
        assert cmd_verify(args) == expected


def test_deleted_claim_and_append_only_inbox_hashes_are_stable(net_vault):
    note = net_vault / "literatures" / "smith2020.md"
    note.unlink()
    claim = _outcome(
        "claim-immutability",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "drift — deleted claim",
        note_path="literatures/smith2020.md",
        claim_id="c-11111111",
    )
    append = _outcome(
        "append-only", "inbox/review-queue.md", Result.UNMATCHED, "drift — inbox"
    )
    first = _target_hash(net_vault, append)
    with (net_vault / "inbox" / "review-queue.md").open("a") as queue:
        queue.write("new finding\n")
    assert _target_hash(net_vault, claim) is not None
    assert _target_hash(net_vault, append) == first


def test_deleted_claim_with_invalid_utf8_has_a_stable_target_hash(net_vault):
    note = net_vault / "projects" / "brief" / "invalid-utf8.md"
    claim_bytes = b"- (quote) invalid \xff [@missing] ^c-invalid\n"
    note.write_bytes(claim_bytes)
    subprocess.run(["git", "add", note], cwd=net_vault, check=True)
    subprocess.run(
        ["git", "commit", "-m", "add invalid utf8 claim"],
        cwd=net_vault,
        check=True,
    )
    note.unlink()
    outcome = _outcome(
        "claim-immutability",
        "projects/brief/invalid-utf8.md#^c-invalid",
        Result.UNMATCHED,
        "drift — deleted claim",
        note_path="projects/brief/invalid-utf8.md",
        claim_id="c-invalid",
    )

    first = _target_hash(net_vault, outcome)

    assert first == hashlib.sha256(claim_bytes).hexdigest()[:16]
    assert _target_hash(net_vault, outcome) == first


def test_marker_clear_uses_exact_origin_and_citekey_claim_collection(net_vault):
    other = net_vault / "projects" / "brief" / "other.md"
    other.write_text(
        "- (quote) [@smith2020] [failed-verification:: quote/2026-08-16] ^c-66666666\n"
    )
    origin = _outcome(
        "quote",
        "smith2020#^c-66666666",
        Result.MATCHED,
        "matched",
        note_path="projects/brief/draft.md",
        claim_id="c-66666666",
    )
    _mutate_marker(net_vault, origin, "2026-08-16", clear=True)
    assert (
        "failed-verification" not in (net_vault / "projects/brief/draft.md").read_text()
    )
    assert "failed-verification" in other.read_text()
    citekey = _outcome(
        "citekey",
        "fabricated2020",
        Result.UNMATCHED,
        "mismatch — citekey not in bibliography",
        note_path="projects/brief/draft.md",
        claims=[{"claim_id": "c-66666666"}, {"claim_id": "c-77777777"}],
    )
    _mutate_marker(net_vault, citekey, "2026-08-16")
    marked = (net_vault / "projects/brief/draft.md").read_text()
    assert marked.count("failed-verification:: citekey/2026-08-16") == 2
    assert "failed-verification:: quote/2026-08-16" in other.read_text()
    _mutate_marker(net_vault, citekey, "2026-08-16", clear=True)
    assert (
        "failed-verification:: citekey/2026-08-16"
        not in (net_vault / "projects/brief/draft.md").read_text()
    )


def test_no_attachment_hash_ignores_events_but_markers_and_content_are_substantive(
    net_vault,
):
    source = net_vault / "literatures" / "smith2020.md"
    text = source.read_text().replace(
        'fixity-sha256:\n  - "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"\n',
        "",
    )
    source.write_bytes(text.replace("\n", "\r\n").encode())
    outcome = _outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="literatures/smith2020.md",
        claim_id="c-11111111",
    )
    original = _target_hash(net_vault, outcome)
    source.write_text(
        events.record_pass(
            source.read_bytes().decode(), "doi", Result.MATCHED, at="2026-08-16"
        ),
        newline="",
    )
    assert _target_hash(net_vault, outcome) == original

    _mutate_marker(net_vault, outcome, "2026-08-17")
    after_effects = source.read_bytes()
    marked_hash = _target_hash(net_vault, outcome)
    finding = inbox.append_entry(
        net_vault,
        outcome.check,
        outcome.target,
        outcome.result,
        outcome.reason,
        target_hash=marked_hash,
    )
    inbox.append_ack(
        net_vault, finding.id, "manual — checked", "human:test", marked_hash
    )

    assert b"\r\r\n" not in after_effects
    assert marked_hash != original
    assert inbox.is_acknowledged(
        net_vault, outcome.check, outcome.target, current_hash=marked_hash
    )

    source.write_bytes(after_effects.replace(b"Mortality fell", b"Mortality rose", 1))
    assert _target_hash(net_vault, outcome) != original

    source.write_bytes(
        after_effects.replace(b'status: "included"', b'status: "deprecated"')
    )
    assert _target_hash(net_vault, outcome) != original


def test_marker_mutation_preserves_crlf_and_exact_claim_spacing(net_vault):
    note = net_vault / "projects" / "brief" / "crlf markers.md"
    original = (
        b"- (quote) anchored [@missing]   ^c-1\r\n- (quote) line only [@missing]\r\n"
    )
    note.write_bytes(original)
    anchored = _outcome(
        "citekey",
        "missing",
        Result.UNMATCHED,
        "mismatch — citekey not in bibliography",
        note_path="projects/brief/crlf markers.md",
        claims=[{"claim_id": "c-1"}],
    )
    anchored_hash = _target_hash(net_vault, anchored)

    _mutate_marker(net_vault, anchored, "2026-08-16")
    stamped = note.read_bytes()

    assert b"   [failed-verification:: citekey/2026-08-16] ^c-1\r\n" in stamped
    assert b"\r [failed-verification" not in stamped
    assert _target_hash(net_vault, anchored) != anchored_hash
    _mutate_marker(net_vault, anchored, "2026-08-16", clear=True)
    assert note.read_bytes() == original
    assert _target_hash(net_vault, anchored) == anchored_hash

    line_only = _outcome(
        "quote",
        "missing",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="projects/brief/crlf markers.md",
        line_no=2,
    )
    line_hash = _target_hash(net_vault, line_only)
    _mutate_marker(net_vault, line_only, "2026-08-16")
    stamped = note.read_bytes()
    assert (
        b"line only [@missing] [failed-verification:: quote/2026-08-16]\r\n" in stamped
    )
    assert b"\r [failed-verification" not in stamped
    assert _target_hash(net_vault, line_only) != line_hash
    _mutate_marker(net_vault, line_only, "2026-08-16", clear=True)
    assert note.read_bytes() == original
    assert _target_hash(net_vault, line_only) == line_hash


def test_marker_preserves_legal_trailing_anchor_whitespace(net_vault):
    note = net_vault / "projects" / "brief" / "trailing anchor.md"
    original = b"- (quote) trailing [@missing] ^c-1  \r\n"
    note.write_bytes(original)
    outcome = _outcome(
        "quote",
        "missing#^c-1",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="projects/brief/trailing anchor.md",
        claim_id="c-1",
        line_no=1,
    )
    before = _target_hash(net_vault, outcome)

    assert claims.parse_claims(original.decode())[0].claim_id == "c-1"
    _mutate_marker(net_vault, outcome, "2026-08-16")
    stamped = note.read_bytes()

    assert stamped == (
        b"- (quote) trailing [@missing] [failed-verification:: quote/2026-08-16] ^c-1  \r\n"
    )
    assert claims.parse_claims(stamped.decode())[0].claim_id == "c-1"
    assert _target_hash(net_vault, outcome) != before
    _mutate_marker(net_vault, outcome, "2026-08-16", clear=True)
    assert note.read_bytes() == original
    assert _target_hash(net_vault, outcome) == before


def test_body_only_literature_ack_survives_verifier_event_envelope(net_vault):
    note = net_vault / "literatures" / "bodyonly.md"
    original = "- (quote) body-only [@bodyonly] ^c-1\n"
    note.write_text(original)
    outcome = _outcome("doi", "bodyonly", Result.UNMATCHED, "mismatch — DOI")
    before = _target_hash(net_vault, outcome)
    finding = inbox.append_entry(
        net_vault,
        outcome.check,
        outcome.target,
        outcome.result,
        outcome.reason,
        target_hash=before,
    )
    inbox.append_ack(net_vault, finding.id, "manual — checked", "human:test", before)

    note.write_text(
        events.record_pass(original, "doi", Result.MATCHED, at="2026-08-16")
    )
    after = _target_hash(net_vault, outcome)

    assert events.verified_checks(note.read_text())[0]["check"] == "doi"
    assert after == before
    assert inbox.is_acknowledged(
        net_vault, outcome.check, outcome.target, current_hash=after
    )


def test_marker_stamp_ignores_prose_lookalike_and_clears_only_terminal_field(
    net_vault,
):
    note = net_vault / "projects" / "brief" / "marker prose.md"
    original = "- (quote) prose [failed-verification:: quote/2026-08-16] remains human text ^c-1\n"
    note.write_text(original)
    outcome = _outcome(
        "quote",
        "missing#^c-1",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="projects/brief/marker prose.md",
        claim_id="c-1",
    )

    _mutate_marker(net_vault, outcome, "2026-08-17")

    assert note.read_text() == original.replace(
        " ^c-1", " [failed-verification:: quote/2026-08-17] ^c-1"
    )
    _mutate_marker(net_vault, outcome, "2026-08-16", clear=True)
    assert note.read_text() == original


def test_no_attachment_acknowledged_warning_stays_suppressed_across_effects(
    net_vault, monkeypatch, capsys
):
    source = net_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            'fixity-sha256:\n  - "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"\n',
            "",
        )
    )
    # Committed so `lint_evidence_layer`'s base and candidate agree on the
    # missing fixity-sha256 — this test exercises warning suppression, not
    # the machine-owned-frontmatter guard.
    subprocess.run(["git", "add", "-A"], cwd=net_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "drop fixity-sha256"], cwd=net_vault, check=True
    )
    warning = _outcome(
        "update-notice",
        "smith2020",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction"}],
    )
    target_hash = _target_hash(net_vault, warning)
    finding = inbox.append_entry(
        net_vault,
        warning.check,
        warning.target,
        Result.UNMATCHED,
        "warn-notice — correction",
        target_hash=target_hash,
        notice_class="warn",
        notice_type="correction",
    )
    inbox.append_ack(
        net_vault, finding.id, "manual — checked", "human:test", target_hash
    )
    _isolate_network_verify(monkeypatch, [warning])

    first, effective, _hashes, warning_effective = verify_state(
        net_vault, network=True, detection_date="2026-08-16"
    )
    second, _, _, second_warning_effective = verify_state(
        net_vault, network=True, detection_date="2026-08-17"
    )

    assert first["outcomes"][-1] is warning
    assert warning in effective
    assert warning_effective[id(warning)] is False
    assert second_warning_effective[id(warning)] is False
    assert first["counts"] == second["counts"]
    assert not any(
        entry.reason == "warn-notice — correction"
        for entry in inbox.open_entries(net_vault)
    )
    assert [
        event["check"] for event in events.verified_checks(source.read_text())
    ].count("update-notice") == 2

    code = cmd_verify(
        type("Args", (), {"vault": net_vault, "offline": False, "rw_csv": None})()
    )
    output = capsys.readouterr().out
    assert code == 0
    assert "warn-notice — correction" not in output
    assert '"MATCHED"' in output


def test_safe_unicode_paths_and_nested_symlinks_are_contained(net_vault, tmp_path):
    note = net_vault / "projects" / "brief" / "synthèse space.md"
    note.write_text("- (quote) local [@missing] ^c-local\n")
    outcome = _outcome(
        "quote",
        "missing#^c-local",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="projects/brief/synthèse space.md",
        claim_id="c-local",
    )

    assert _target_hash(net_vault, outcome) is not None
    _mutate_marker(net_vault, outcome, "2026-08-16")
    assert "failed-verification:: quote/2026-08-16" in note.read_text()
    _mutate_marker(net_vault, outcome, "2026-08-16", clear=True)
    assert "failed-verification" not in note.read_text()

    outside_root = tmp_path.parent / f"{tmp_path.name}-outside"
    outside_root.mkdir()
    outside = outside_root / "outside.md"
    outside.write_text("outside remains private\n")
    direct_link = net_vault / "projects" / "brief" / "outside-link.md"
    direct_link.symlink_to(outside)
    assert _safe_relative(net_vault, "projects/brief/outside-link.md") is None
    assert (
        _target_hash(
            net_vault,
            _outcome(
                "append-only",
                "projects/brief/outside-link.md",
                Result.UNMATCHED,
                "drift",
            ),
        )
        is None
    )
    citekey_link = net_vault / "literatures" / "escaped.md"
    citekey_link.symlink_to(outside)
    assert (
        _target_hash(
            net_vault,
            _outcome("doi", "escaped", Result.UNMATCHED, "mismatch — DOI"),
        )
        is None
    )

    directory = net_vault / "projects" / "published"
    nested = directory / "nested"
    nested.mkdir(parents=True)
    first_target = outside_root / "first-target"
    second_target = outside_root / "second-target"
    first_target.write_text("outside bytes must not be read\n")
    second_target.write_text("also outside\n")
    link = nested / "escape"
    link.symlink_to(first_target)
    directory_outcome = _outcome(
        "published-drift",
        RepoPath(b"projects/published"),
        Result.UNMATCHED,
        "drift",
    )
    first = _target_hash(net_vault, directory_outcome)
    first_target.write_text("changing outside content stays invisible\n")
    assert _target_hash(net_vault, directory_outcome) == first
    link.unlink()
    link.symlink_to(second_target)
    assert _target_hash(net_vault, directory_outcome) != first


def test_main_routes_base_before_and_after_verify(net_vault, monkeypatch, capsys):
    bases = []

    def state(*_args, **kwargs):
        bases.append(kwargs["base"])
        return {"outcomes": [], "counts": {}}, [], {}, {}

    monkeypatch.setattr("research_vault.__main__.verify_state", state)

    assert (
        main(
            [
                "--base",
                "http://before.invalid",
                "verify",
                "--vault",
                str(net_vault),
                "--offline",
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "verify",
                "--base",
                "http://after.invalid",
                "--vault",
                str(net_vault),
                "--offline",
            ]
        )
        == 0
    )
    assert bases == ["http://before.invalid", "http://after.invalid"]
    assert capsys.readouterr().out.count("{}") == 2


def test_python_module_verify_and_inbox_acceptance(net_vault):
    core = Path(__file__).resolve().parents[1]
    verify = subprocess.run(
        [
            sys.executable,
            "-m",
            "research_vault",
            "verify",
            "--vault",
            str(net_vault),
            "--offline",
        ],
        cwd=core,
        capture_output=True,
        text=True,
        check=False,
    )

    assert verify.returncode == 0
    assert "fabricated2020" in verify.stdout

    review = subprocess.run(
        [sys.executable, "-m", "research_vault", "inbox", "--vault", str(net_vault)],
        cwd=core,
        capture_output=True,
        text=True,
        check=False,
    )

    assert review.returncode == 0
    assert '"unacknowledged"' in review.stdout
    assert "fabricated2020" in review.stdout


def test_file_effects_does_not_refile_an_already_open_skipped_finding(tmp_vault):
    """Excluding SKIPPED from the unacknowledged count must not exclude it
    from ``open_entries()``: ``_file_effects`` builds its dedup key set from
    that same call, and a SKIPPED row missing from it gets re-filed as a
    duplicate on every subsequent run.
    """
    existing = inbox.append_entry(
        tmp_vault,
        "metadata",
        "a",
        Result.SKIPPED,
        "no-identifier",
        date="2026-08-01",
    )
    outcome = checks.Outcome("metadata", "a", Result.SKIPPED, "no-identifier")

    _file_effects(tmp_vault, [outcome], {id(outcome): None}, {}, "2026-08-02")

    assert [entry.id for entry in inbox.open_entries(tmp_vault)] == [existing.id]


def test_warn_dedup_reconstructs_type_and_inbox_is_oldest_first(net_vault, capsys):
    inbox.append_entry(
        net_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — correction",
        date="2026-08-01",
        target_hash="aa11",
        notice_class="warn",
        notice_type="correction",
    )
    inbox.append_entry(
        net_vault,
        "doi",
        "gone2019",
        Result.UNMATCHED,
        "mismatch — old",
        date="2026-08-02",
    )
    assert run_verify(net_vault, network=False)["outcomes"]
    cmd_inbox(type("Args", (), {"vault": net_vault})())
    lines = capsys.readouterr().out.splitlines()
    assert "2026-08-01" in lines[1]
    assert (
        len(
            [
                e
                for e in inbox.open_entries(net_vault)
                if e.reason == "warn-notice — correction"
            ]
        )
        == 1
    )


def _isolate_network_verify(monkeypatch, outcomes):
    monkeypatch.setattr("research_vault.verify.file_outcomes", lambda *_args: [])
    monkeypatch.setattr(
        "research_vault.verify._bibliography_entries",
        lambda *_args: [{"id": "smith2020", "DOI": "10.1000/xyz"}],
    )
    monkeypatch.setattr(
        "research_vault.verify._network_outcomes", lambda *_args: list(outcomes)
    )
    for name in (
        "lint_append_only",
        "lint_claim_immutability",
        "lint_published_drift",
    ):
        monkeypatch.setattr(f"research_vault.lints.{name}", lambda *_args: [])


def test_correction_ack_does_not_suppress_same_hash_blocking_retraction(
    net_vault, monkeypatch, capsys
):
    correction = _outcome(
        "update-notice",
        "smith2020",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction", "notice_date": "2026-01-01"}],
    )
    current = [correction]
    _isolate_network_verify(monkeypatch, current)

    assert (
        cmd_verify(
            type(
                "Args",
                (),
                {
                    "vault": net_vault,
                    "offline": False,
                    "rw_csv": None,
                    "surface": "audit",
                },
            )()
        )
        == 0
    )
    warning = next(
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.notice_type == "correction"
    )
    inbox.append_ack(
        net_vault,
        warning.id,
        "manual — reviewed correction",
        "human:test",
        warning.target_hash,
    )
    capsys.readouterr()

    current[:] = [
        _outcome(
            "update-notice",
            "smith2020",
            Result.UNMATCHED,
            "retracted — retraction",
            **{
                "class": "blocking",
                "type": "retraction",
                "notice_date": "2026-01-01",
                "detection_date": "2026-08-17",
            },
        )
    ]
    assert (
        cmd_verify(
            type(
                "Args",
                (),
                {
                    "vault": net_vault,
                    "offline": False,
                    "rw_csv": None,
                    "surface": "publish",
                },
            )()
        )
        == 1
    )
    output = capsys.readouterr().out
    blocker = next(
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.notice_type == "retraction"
    )

    assert "retracted — retraction" in output
    assert blocker.target_hash == warning.target_hash == "aa11" * 16
    assert (
        events.trust_tier((net_vault / "literatures" / "smith2020.md").read_text())
        == "unverified"
    )

    inbox.append_ack(
        net_vault,
        blocker.id,
        "manual — reviewed retraction",
        "human:test",
        blocker.target_hash,
    )
    assert (
        cmd_verify(
            type(
                "Args",
                (),
                {"vault": net_vault, "offline": False, "rw_csv": None},
            )()
        )
        == 0
    )
    assert "retracted — retraction" not in capsys.readouterr().out
    assert not inbox.open_entries(net_vault)


def _projecting_failure(check):
    if check == "update-notice":
        return _outcome(
            "update-notice",
            "smith2020",
            Result.UNMATCHED,
            "retracted — retraction",
            **{
                "class": "blocking",
                "type": "retraction",
                "notice_date": "2026-01-01",
                "detection_date": "2026-08-16",
            },
        )
    return checks.Outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote",
        {
            "note_path": RepoPath(b"literatures/smith2020.md"),
            "claim_id": "c-11111111",
            "target": "managed-region",
        },
    )


@pytest.mark.parametrize(
    "reverse", [False, True], ids=["primary-first", "primary-last"]
)
@pytest.mark.parametrize("check", ["update-notice", "quote"])
def test_no_fixity_target_hashes_are_candidate_bound_before_projection(
    net_vault, monkeypatch, check, reverse
):
    source = net_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            'fixity-sha256:\n  - "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"\n',
            "",
        )
    )
    # Committed so `lint_evidence_layer`'s base and candidate agree on the
    # missing fixity-sha256 — this test exercises candidate-bound hashing, not
    # the machine-owned-frontmatter guard.
    subprocess.run(["git", "add", "-A"], cwd=net_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "drop fixity-sha256"], cwd=net_vault, check=True
    )
    primary = _projecting_failure(check)
    companion = _outcome("citekey", "smith2020", Result.UNREACHABLE, "outage — citekey")
    current = [primary, companion]
    if reverse:
        current.reverse()
    _isolate_network_verify(monkeypatch, current)

    candidate_hash = _target_hash(net_vault, primary)
    _report, _effective_outcomes, hashes, _warnings = verify_state(
        net_vault, network=True, detection_date="2026-08-16"
    )
    projected_hash = _target_hash(net_vault, primary)
    finding = next(
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.check == check and entry.target == primary.target
    )

    assert projected_hash != candidate_hash
    assert hashes[id(primary)] == candidate_hash
    assert finding.target_hash == candidate_hash


@pytest.mark.parametrize("check", ["update-notice", "quote"])
def test_no_fixity_acknowledgment_is_decided_from_candidate_before_projection(
    net_vault, monkeypatch, check
):
    source = net_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            'fixity-sha256:\n  - "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"\n',
            "",
        )
    )
    # Committed so `lint_evidence_layer`'s base and candidate agree on the
    # missing fixity-sha256 — this test exercises candidate-bound hashing, not
    # the machine-owned-frontmatter guard.
    subprocess.run(["git", "add", "-A"], cwd=net_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "drop fixity-sha256"], cwd=net_vault, check=True
    )
    primary = _projecting_failure(check)
    companion = _outcome("citekey", "smith2020", Result.UNREACHABLE, "outage — citekey")
    _isolate_network_verify(monkeypatch, [companion, primary])
    candidate_hash = _target_hash(net_vault, primary)
    notice_class, notice_type, notice_date = (
        (
            primary.extra.get("class"),
            primary.extra.get("type"),
            primary.extra.get("notice_date"),
        )
        if check == "update-notice"
        else (None, None, None)
    )
    finding = inbox.append_entry(
        net_vault,
        primary.check,
        primary.target,
        primary.result,
        primary.reason,
        date="2026-08-16",
        target_hash=candidate_hash,
        notice_class=notice_class,
        notice_type=notice_type,
        notice_date=notice_date,
        target_kind=primary.target_kind,
    )
    inbox.append_ack(
        net_vault,
        finding.id,
        "manual — checked candidate",
        "human:test",
        candidate_hash,
    )

    _report, effective, hashes, _warnings = verify_state(
        net_vault, network=True, detection_date="2026-08-16"
    )

    assert hashes[id(primary)] == candidate_hash
    assert primary not in effective
    assert _target_hash(net_vault, primary) != candidate_hash
    assert not any(
        entry.check == check and entry.target == primary.target
        for entry in inbox.open_entries(net_vault)
    )


def test_current_failure_projection_keeps_exact_recovery_behavior(
    net_vault, monkeypatch
):
    """The two surviving projecting check kinds — the bare ``update-notice``
    identity and the per-claim ``quote`` identity — recover independently,
    same as the retired ``doi``/``metadata`` pair once did."""
    source = net_vault / "literatures" / "smith2020.md"
    text = source.read_text()
    for verified_check in (
        "update-notice",
        "quote:smith2020#^c-11111111:managed-region",
    ):
        text = events.record_pass(text, verified_check, Result.MATCHED, at="2026-08-15")
    source.write_text(text)
    update_notice_failure = _projecting_failure("update-notice")
    quote_failure = _projecting_failure("quote")
    current = [update_notice_failure, quote_failure]
    _isolate_network_verify(monkeypatch, current)

    run_verify(net_vault, network=True, detection_date="2026-08-16")
    assert events.current_failures(source.read_text()) == [
        {
            "check": "quote:smith2020#^c-11111111:managed-region",
            "result": "UNMATCHED",
        },
        {"check": "update-notice", "result": "UNMATCHED"},
    ]
    assert events.trust_tier(source.read_text()) == "unverified"

    current[:] = [
        _outcome("update-notice", "smith2020", Result.MATCHED, "matched"),
        quote_failure,
    ]
    run_verify(net_vault, network=True, detection_date="2026-08-18")
    assert events.current_failures(source.read_text()) == [
        {
            "check": "quote:smith2020#^c-11111111:managed-region",
            "result": "UNMATCHED",
        }
    ]

    current[:] = [
        _outcome("update-notice", "smith2020", Result.MATCHED, "matched"),
        checks.Outcome(
            "quote",
            "smith2020#^c-11111111",
            Result.MATCHED,
            "matched",
            {
                "note_path": RepoPath(b"literatures/smith2020.md"),
                "claim_id": "c-11111111",
                "target": "managed-region",
            },
        ),
    ]
    run_verify(net_vault, network=True, detection_date="2026-08-19")
    assert events.current_failures(source.read_text()) == []
    assert events.trust_tier(source.read_text()) == "machine-confirmed"


@pytest.mark.parametrize(
    "contents",
    [
        "{",
        '{"items": []}',
        '[{"id": "bad", "DOI": 123}]',
        '[{"id": "bad\\nkey"}]',
    ],
    ids=["truncated-json", "wrong-top-level", "non-string-doi", "multiline-id"],
)
def test_real_verify_cli_reports_invalid_bibliography_without_traceback(
    net_vault, capsys, contents
):
    (net_vault / "system" / "bibliography.json").write_text(contents)

    code = main(["verify", "--vault", str(net_vault), "--offline"])
    output = capsys.readouterr().out

    assert code == 0
    assert "UNMATCHED citekey path-bytes:system/bibliography.json" in output
    assert "schema-violation" in output
    assert "Traceback" not in output


def test_real_verify_cli_reports_undecodable_bibliography_unreachable(
    net_vault, capsys
):
    (net_vault / "system" / "bibliography.json").write_bytes(b"\xff")

    code = main(["verify", "--vault", str(net_vault), "--offline"])
    output = capsys.readouterr().out

    assert code == 0
    assert "UNREACHABLE citekey path-bytes:system/bibliography.json" in output


def test_real_verify_cli_states_rw_leg_absence_without_rw_csv(net_vault, capsys):
    """An unarmed RW leg states its absence exactly once, as a stdout line
    that never files a review-queue entry."""
    code = main(["verify", "--vault", str(net_vault), "--offline"])
    output = capsys.readouterr().out

    assert code == 0
    assert output.count("update-notice: RW leg not run (no --rw-csv)") == 1
    assert not [
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.check == "update-notice"
    ]


def test_real_verify_cli_omits_rw_leg_absence_line_when_rw_csv_supplied(
    net_vault, capsys, tmp_path
):
    """Supplying --rw-csv arms the leg; the absence line must not print."""
    rw_csv = tmp_path / "rw.csv"
    rw_csv.write_text(
        "OriginalPaperDOI,OriginalPaperPubMedID,RetractionDate,RetractionNature\n"
    )

    code = main(
        ["verify", "--vault", str(net_vault), "--offline", "--rw-csv", str(rw_csv)]
    )
    output = capsys.readouterr().out

    assert code == 0
    assert "RW leg not run" not in output


@pytest.mark.parametrize(
    ("surface", "expected"), [("audit", 0), ("commit", 3), ("publish", 3)]
)
def test_genuine_unreachable_closes_only_on_explicit_surfaces(
    net_vault, monkeypatch, surface, expected
):
    outage = _outcome("doi", "smith2020", Result.UNREACHABLE, "outage — registry")
    monkeypatch.setattr(
        "research_vault.__main__.verify_state",
        lambda *_args, **_kwargs: (
            {"outcomes": [outage], "counts": {"UNREACHABLE": 1}},
            [outage],
            {id(outage): "aa11"},
            {},
        ),
    )

    assert (
        cmd_verify(
            type(
                "Args",
                (),
                {
                    "vault": net_vault,
                    "offline": False,
                    "rw_csv": None,
                    "surface": surface,
                },
            )()
        )
        == expected
    )


def test_deleted_nested_repo_path_hashes_resolved_base_without_live_parent(
    net_vault,
):
    directory = net_vault / "projects" / "nested"
    directory.mkdir()
    note = directory / "deleted.md"
    note.write_bytes(b"candidate evidence\n")
    subprocess.run(
        ["git", "add", "projects/nested/deleted.md"], cwd=net_vault, check=True
    )
    subprocess.run(
        ["git", "commit", "-qm", "nested evidence"], cwd=net_vault, check=True
    )
    snapshots = gitstate.resolve_snapshots(net_vault, candidate="worktree")
    note.unlink()
    directory.rmdir()
    outcome = checks.Outcome(
        "evidence-layer",
        RepoPath(b"projects/nested/deleted.md"),
        Result.UNMATCHED,
        "drift — deleted note",
    )
    expected = hashlib.sha256(b"candidate evidence\n").hexdigest()[:16]

    target_hash = _target_hash(net_vault, outcome, base_snapshot=snapshots.base)

    assert target_hash == expected
    finding = inbox.append_entry(
        net_vault,
        outcome.check,
        outcome.target,
        outcome.result,
        outcome.reason,
        date="2026-08-16",
        target_hash=target_hash,
        target_kind=outcome.target_kind,
    )
    inbox.append_ack(
        net_vault, finding.id, "manual — checked deletion", "human:test", target_hash
    )
    assert inbox.is_acknowledged(
        net_vault,
        outcome.check,
        outcome.target,
        current_hash=_target_hash(net_vault, outcome, base_snapshot=snapshots.base),
        target_kind=outcome.target_kind,
    )


def test_verify_loads_bibliography_once_at_orchestration_boundary(
    net_vault, monkeypatch
):
    load = Mock(wraps=bibliography.load)
    monkeypatch.setattr(bibliography, "load", load)

    run_verify(net_vault, network=False, detection_date="2026-08-16")

    assert load.call_count == 1
    assert load.call_args.args[0] != net_vault


def test_invalid_bibliography_is_not_reloaded_while_hashing(net_vault, monkeypatch):
    (net_vault / bibliography.BIB_PATH).write_text("{")
    load = Mock(wraps=bibliography.load)
    monkeypatch.setattr(bibliography, "load", load)
    outcome = _outcome("custom", "missing", Result.UNMATCHED, "mismatch")
    monkeypatch.setattr("research_vault.verify.file_outcomes", lambda *_args: [outcome])
    for name in (
        "lint_append_only",
        "lint_claim_immutability",
        "lint_published_drift",
    ):
        monkeypatch.setattr(f"research_vault.lints.{name}", lambda *_args: [])

    run_verify(net_vault, network=False, detection_date="2026-08-16")

    assert load.call_count == 1
    assert load.call_args.args[0] != net_vault


@pytest.mark.live_net
def test_live_drill_wakefield_and_fabricated(net_vault_real_mailto):
    outcome = checks.check_update_notice(
        net_vault_real_mailto,
        {"id": "wakefield1998", "DOI": "10.1016/S0140-6736(97)11096-0"},
        "2026-08-16",
    )
    assert outcome.result is Result.UNMATCHED
    # Crossref is authoritative; deposits may be re-issued within the month.
    assert outcome.extra["notice_date"].startswith("2010-02")
    assert (
        checks.registry_agency(net_vault_real_mailto, "10.5281/zenodo.3678326")
        == "DataCite"
    )


def _vault_bytes(vault):
    return {
        os.fsencode(path.relative_to(vault)): path.read_bytes()
        for path in vault.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(vault).parts
    }


def test_surface_contract_defaults_to_open_audit_and_explicit_commit_closes(
    fixture_vault,
):
    assert main(["verify", "--vault", str(fixture_vault), "--offline"]) == 0
    assert (
        main(
            [
                "verify",
                "--vault",
                str(fixture_vault),
                "--offline",
                "--surface",
                "commit",
            ]
        )
        == 1
    )
    assert {
        key: frozenset(value)
        for key, value in __import__(
            "research_vault.__main__", fromlist=["CLOSING_BY_SURFACE"]
        ).CLOSING_BY_SURFACE.items()
    } == {
        "audit": frozenset(),
        "commit": frozenset(
            {"citekey", "evidence-layer", "okf-frontmatter", "okf-structure", "tree"}
        ),
        "publish": frozenset(
            {
                "citekey",
                "evidence-layer",
                "quote",
                "update-notice",
                "okf-frontmatter",
                "okf-structure",
                "tree",
            }
        ),
    }


def test_literature_note_add_is_collected_and_projected_as_evidence_finding(
    fixture_vault,
):
    added = fixture_vault / "literatures" / "added.md"
    added.write_bytes((fixture_vault / "literatures" / "smith2020.md").read_bytes())

    report, effective, hashes, _warnings = verify_state(
        fixture_vault, network=False, detection_date="2026-08-16"
    )

    finding = next(
        outcome
        for outcome in report["outcomes"]
        if outcome.check == "evidence-layer"
        and outcome.target == "path-bytes:literatures/added.md"
        and outcome.reason == "drift — literature note added"
    )
    assert finding in effective
    assert hashes[id(finding)] is not None
    assert any(
        entry.check == "evidence-layer" and entry.target == finding.target
        for entry in inbox.open_entries(fixture_vault)
    )


def test_invalid_publication_flags_or_inside_manifest_exit_two_before_mutation(
    fixture_vault, tmp_path
):
    before = _vault_bytes(fixture_vault)
    with pytest.raises(SystemExit) as missing_manifest:
        main(
            [
                "verify",
                "--vault",
                str(fixture_vault),
                "--commit-projected",
                "message",
            ]
        )
    assert missing_manifest.value.code == 2
    assert _vault_bytes(fixture_vault) == before

    assert (
        main(
            [
                "verify",
                "--vault",
                str(fixture_vault),
                "--offline",
                "--changed-paths-file",
                str(fixture_vault / "manifest"),
            ]
        )
        == 2
    )
    assert _vault_bytes(fixture_vault) == before


def test_synthetic_offline_outcomes_have_no_state_or_effect_authority(tmp_vault):
    # A DOI-less entry is what still exercises the offline synthetic path
    # (`_offline_network_outcomes`) now that the staleness leg is retired.
    bibliography.write(tmp_vault, [{"id": "smith2020", "title": "Mortality decline"}])
    before = _vault_bytes(tmp_vault)

    report = run_verify(tmp_vault, network=False, detection_date="2026-08-16")

    synthetic = [
        item
        for item in report["outcomes"]
        if item.extra.get("synthetic_offline") is True
    ]
    assert synthetic
    assert all(item.result is Result.UNREACHABLE for item in synthetic)
    assert _vault_bytes(tmp_vault) == before
    assert inbox.load(tmp_vault) == []


def test_invalid_utf8_path_has_one_typed_token_across_outcome_record_and_inbox(
    fixture_vault,
):
    raw = b"projects/brief/bad-\xff.md"
    absolute = os.path.join(os.fsencode(fixture_vault), raw)
    with open(absolute, "wb") as stream:
        stream.write(b"plain text\n")

    report = run_verify(fixture_vault, network=False, detection_date="2026-08-16")

    token = encode_repo_path(raw)
    outcome = next(
        item
        for item in report["outcomes"]
        if item.target == token and item.target_kind == "repo-path"
    )
    record = checks.outcome_to_record(outcome)
    assert record["target"] == token
    assert "\udcff" not in json.dumps(record)
    matching = [
        item
        for item in inbox.load(fixture_vault)
        if item.target == token and item.target_kind == "repo-path"
    ]
    assert matching
    assert "\udcff" not in (fixture_vault / inbox.INBOX_PATH).read_text()


def test_hash_and_marker_filesystem_routing_requires_explicit_repo_path_kind(
    fixture_vault,
):
    raw = b"projects/brief/path-bytes:looks-like-id.md"
    path = os.path.join(os.fsencode(fixture_vault), raw)
    with open(path, "wb") as stream:
        stream.write(b"- (quote) body ^c-1\n")
    repo_target = RepoPath(raw)
    typed = checks.Outcome(
        "append-only", repo_target, Result.UNMATCHED, "drift — typed path"
    )
    identifier = checks.Outcome(
        "append-only",
        encode_repo_path(raw),
        Result.UNMATCHED,
        "drift — identifier text",
    )

    assert _target_hash(fixture_vault, typed) is not None
    assert _target_hash(fixture_vault, identifier) is None
    with open(path, "rb") as stream:
        before = stream.read()
    _mutate_marker(fixture_vault, identifier, "2026-08-16")
    with open(path, "rb") as stream:
        assert stream.read() == before


def test_commit_projected_publishes_only_manifest_captured_outputs_and_keeps_index(
    fixture_vault, tmp_path
):
    unrelated = fixture_vault / "unrelated.txt"
    unrelated.write_bytes(b"staged\n")
    subprocess.run(["git", "add", "unrelated.txt"], cwd=fixture_vault, check=True)
    unrelated.write_bytes(b"unstaged\n")
    untracked = fixture_vault / "scratch.txt"
    untracked.write_bytes(b"scratch\n")
    index_path = Path(
        _git_bytes(fixture_vault, "rev-parse", "--git-path", "index").decode().strip()
    )
    if not index_path.is_absolute():
        index_path = fixture_vault / index_path
    index_before = index_path.read_bytes()
    expected = _git_bytes(fixture_vault, "rev-parse", "HEAD").decode().strip()
    manifest = tmp_path.parent / f"{tmp_path.name}-changed"

    code = main(
        [
            "verify",
            "--vault",
            str(fixture_vault),
            "--offline",
            "--surface",
            "audit",
            "--git-candidate",
            "worktree",
            "--changed-paths-file",
            str(manifest),
            "--commit-projected",
            "snapshot projection",
        ]
    )

    assert code == 0
    head = _git_bytes(fixture_vault, "rev-parse", "HEAD").decode().strip()
    assert _git_bytes(fixture_vault, "rev-parse", "HEAD^").decode().strip() == expected
    changed = {
        item
        for item in _git_bytes(
            fixture_vault,
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            "-z",
            head,
        ).split(b"\0")
        if item
    }
    manifest_paths = {item for item in manifest.read_bytes().split(b"\0") if item}
    assert changed == manifest_paths
    assert b"unrelated.txt" not in changed
    assert index_path.read_bytes() == index_before
    assert unrelated.read_bytes() == b"unstaged\n"
    assert untracked.read_bytes() == b"scratch\n"


def test_commit_projected_rejects_dirty_output_overlap_before_any_projection(
    fixture_vault, tmp_path
):
    queue = fixture_vault / inbox.INBOX_PATH
    queue.write_text(queue.read_text() + "human scratch\n")
    before = _vault_bytes(fixture_vault)
    head = _git_bytes(fixture_vault, "rev-parse", "HEAD")
    index = _git_bytes(fixture_vault, "diff", "--cached", "--binary")
    manifest = tmp_path.parent / f"{tmp_path.name}-changed"

    code = main(
        [
            "verify",
            "--vault",
            str(fixture_vault),
            "--offline",
            "--changed-paths-file",
            str(manifest),
            "--commit-projected",
            "snapshot projection",
        ]
    )

    assert code == 2
    assert _vault_bytes(fixture_vault) == before
    assert _git_bytes(fixture_vault, "rev-parse", "HEAD") == head
    assert _git_bytes(fixture_vault, "diff", "--cached", "--binary") == index
    assert not manifest.exists()


def test_archive_source_verb_and_web_archive_check_are_retired(tmp_vault):
    import research_vault.__main__ as cli
    from research_vault import inbox

    with pytest.raises(SystemExit) as exit_info:
        cli.main(["archive-source", "smith2020", "--vault", str(tmp_vault)])
    assert exit_info.value.code == 2
    assert "web-archive" not in inbox.CHECK_IDS
    assert "missing-archive" not in inbox.REASON_CODES
    assert not hasattr(cli, "cmd_archive_source")


def test_network_outcomes_carry_only_update_notice(net_vault, monkeypatch):
    from research_vault import checks, verify

    monkeypatch.setattr(
        checks,
        "check_update_notice",
        lambda vault, entry, date: checks.Outcome(
            "update-notice", entry["id"], Result.MATCHED, "matched"
        ),
    )
    entry = {"id": "smith2020", "DOI": "10.1000/xyz"}
    outcomes = verify._network_outcomes(net_vault, entry, "2026-09-07", None)
    assert [outcome.check for outcome in outcomes] == ["update-notice"]

    offline = verify._offline_network_outcomes(entry, "2026-09-07", None)
    assert [outcome.check for outcome in offline] == ["update-notice"]
    assert offline[0].extra["synthetic_offline"] is True
    assert "doi" not in verify.CLOSING_BY_SURFACE["publish"]
