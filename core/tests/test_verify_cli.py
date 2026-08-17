"""Integration regressions for the verify and inbox command surface."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from harness_core import Result, checks, events, inbox, webapi
from harness_core.__main__ import (
    _archive_outcomes,
    _clear_verify_failed,
    _mutate_marker,
    _safe_relative,
    _target_hash,
    _verify_state,
    cmd_inbox,
    cmd_verify,
    main,
    run_verify,
)


def _outcome(check, target, result, reason, **extra):
    return checks.Outcome(check, target, result, reason, extra)


def test_discovery_partial_identifiers_survive_outage_and_run_recovered_doi(
    net_vault, monkeypatch
):
    entry = {"id": "new", "title": "New"}
    monkeypatch.setattr(
        "harness_core.identify.discover",
        lambda *_: _outcome(
            "identifier-discovery",
            "new",
            Result.UNREACHABLE,
            "outage — PubMed unavailable",
            identifiers={"DOI": "10.1/recovered", "PMID": "12"},
        ),
    )
    monkeypatch.setattr(
        "harness_core.__main__._bibliography_entries", lambda _: [entry]
    )
    monkeypatch.setattr(
        "harness_core.__main__._network_outcomes",
        lambda _v, item, _d, _rw: [
            _outcome("doi", item["id"], Result.MATCHED, "matched"),
            _outcome("metadata", item["id"], Result.MATCHED, "matched"),
            _outcome("update-notice", item["id"], Result.MATCHED, "matched"),
        ],
    )
    report = run_verify(net_vault, network=True, detection_date="2026-08-16")
    assert any(
        o.check == "identifier-discovery" and o.result is Result.UNREACHABLE
        for o in report["outcomes"]
    )
    assert {o.check for o in report["outcomes"] if o.target == "new"} >= {
        "doi",
        "metadata",
        "update-notice",
    }


@pytest.mark.parametrize(
    ("discovery_result", "want"),
    [(Result.SKIPPED, Result.SKIPPED), (Result.UNREACHABLE, Result.UNREACHABLE)],
)
def test_no_doi_distinguishes_healthy_no_hit_from_discovery_outage(
    net_vault, monkeypatch, discovery_result, want
):
    monkeypatch.setattr(
        "harness_core.__main__._bibliography_entries",
        lambda _: [{"id": "empty", "title": "T"}],
    )
    monkeypatch.setattr(
        "harness_core.identify.discover",
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
    assert got["doi"] is want
    assert got["metadata"] is want
    assert got["update-notice"] is want


def test_discovery_outage_with_only_pmid_keeps_live_update_unreachable(
    net_vault, monkeypatch
):
    monkeypatch.setattr(
        "harness_core.__main__._bibliography_entries",
        lambda _: [{"id": "pmid-only", "title": "T"}],
    )
    monkeypatch.setattr(
        "harness_core.identify.discover",
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
    net_vault, tmp_path
):
    csv_file = tmp_path / "rw.csv"
    csv_file.write_text(
        "OriginalPaperDOI,OriginalPaperPubMedID,RetractionDate,RetractionNature\n,123,2020-01-01,Retraction\n"
    )
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        "harness_core.__main__._bibliography_entries",
        lambda _: [{"id": "pmid", "PMID": "123"}],
    )
    try:
        report = run_verify(
            net_vault, network=False, detection_date="2026-08-16", rw_csv=csv_file
        )
    finally:
        monkeypatch.undo()
    notices = [
        o
        for o in report["outcomes"]
        if o.check == "update-notice" and o.target == "pmid"
    ]
    assert len(notices) == 1
    assert notices[0].result is Result.UNMATCHED


def test_ack_suppresses_effects_but_retains_raw_outcome_and_reopens_on_hash(net_vault):
    draft = net_vault / "efforts" / "brief" / "draft.md"
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
    assert "[verify-failed:: quote/" not in draft.read_text()
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
    source.write_text(source.read_text().replace('  - "aa11"', '  - "bb22"'))
    fourth = run_verify(net_vault, network=False, detection_date="2026-08-16")
    assert any(
        e.check == "quote" and e.target == raw.target
        for e in inbox.open_entries(net_vault)
    )
    assert fourth["counts"]["UNMATCHED"] >= 1


def test_target_hash_routes_safe_file_claim_citekey_and_staleness(net_vault):
    file_outcome = _outcome(
        "append-only", "calendar/2026-08-16.md", Result.UNMATCHED, "drift — file"
    )
    claim_outcome = _outcome(
        "quote", "smith2020#^c-11111111", Result.UNMATCHED, "mismatch — quote"
    )
    citekey_outcome = _outcome("doi", "smith2020", Result.UNMATCHED, "mismatch — doi")
    stale = _outcome(
        "staleness", "x/bibliography.json", Result.UNMATCHED, "stale — old"
    )
    assert (
        _target_hash(net_vault, file_outcome)
        == hashlib.sha256(
            (net_vault / "calendar/2026-08-16.md").read_bytes()
        ).hexdigest()[:16]
    )
    claim_hash = _target_hash(net_vault, claim_outcome)
    assert claim_hash == "aa11"
    source = net_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            "^c-11111111", "[verify-failed:: quote/2026-08-16] ^c-11111111"
        )
    )
    assert _target_hash(net_vault, claim_outcome) == "aa11"
    assert _target_hash(net_vault, citekey_outcome) == "aa11"
    assert (
        _target_hash(net_vault, stale)
        == hashlib.sha256((net_vault / "x/bibliography.json").read_bytes()).hexdigest()[
            :16
        ]
    )
    assert (
        _target_hash(
            net_vault,
            _outcome("append-only", "../outside", Result.UNMATCHED, "drift — unsafe"),
        )
        is None
    )


def test_missing_citekey_hash_uses_exact_checked_origins_and_reopens(net_vault):
    draft = net_vault / "efforts" / "brief" / "draft.md"
    outcome = _outcome(
        "citekey",
        "fabricated2020",
        Result.UNMATCHED,
        "mismatch — citekey not in bibliography",
        note_path="efforts/brief/draft.md",
        claims=[{"claim_id": "c-77777777"}],
    )
    original = _target_hash(net_vault, outcome)
    assert original is not None
    draft.write_text(draft.read_text().replace("This will replicate", "This will not"))
    assert _target_hash(net_vault, outcome) != original


def test_no_note_bibliography_target_hashes_its_canonical_entry(net_vault):
    path = net_vault / "x" / "bibliography.json"
    entries = json.loads(path.read_text())
    entries.append({"id": "noted-yet", "title": "Admitted bibliography entry"})
    path.write_text(json.dumps(entries))
    outcome = _outcome("doi", "noted-yet", Result.UNMATCHED, "mismatch — DOI")
    assert _target_hash(net_vault, outcome) is not None


def test_unanchored_claim_marker_uses_its_exact_line_origin(net_vault):
    draft = net_vault / "efforts" / "brief" / "draft.md"
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
        note_path="efforts/brief/draft.md",
        line_no=line_no,
    )
    _mutate_marker(net_vault, outcome, "2026-08-16")
    assert (
        "verify-failed:: quote/2026-08-16"
        in draft.read_text().splitlines()[line_no - 1]
    )
    _clear_verify_failed(net_vault, outcome)
    assert "verify-failed" not in draft.read_text().splitlines()[line_no - 1]


def test_matching_outcome_still_mints_event_after_same_hash_ack(net_vault, monkeypatch):
    entry = inbox.append_entry(
        net_vault,
        "doi",
        "smith2020",
        Result.UNMATCHED,
        "mismatch — old result",
        target_hash="aa11",
    )
    inbox.append_ack(net_vault, entry.id, "manual — checked", "human:test", "aa11")
    monkeypatch.setattr(
        "harness_core.__main__._bibliography_entries",
        lambda _: [{"id": "smith2020", "DOI": "10.1000/xyz"}],
    )
    monkeypatch.setattr(
        "harness_core.__main__._network_outcomes",
        lambda *_: [_outcome("doi", "smith2020", Result.MATCHED, "matched")],
    )
    run_verify(net_vault, network=True, detection_date="2026-08-16")
    assert any(
        event["check"] == "doi"
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
    assert len(first_entries) == len(second_entries) == 1
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
        "harness_core.__main__._verify_state",
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
        "harness_core.__main__._verify_state",
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
        target_hash="aa11",
    )
    inbox.append_ack(net_vault, entry.id, "manual — checked", "human:test", "aa11")
    warning = _outcome(
        "update-notice",
        "smith2020",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction"}],
    )
    monkeypatch.setattr(
        "harness_core.__main__._bibliography_entries",
        lambda _: [{"id": "smith2020", "DOI": "10.1000/xyz"}],
    )
    monkeypatch.setattr("harness_core.__main__._network_outcomes", lambda *_: [warning])
    monkeypatch.setattr(
        "harness_core.__main__._staleness_outcome",
        lambda *_: _outcome(
            "staleness", "x/bibliography.json", Result.MATCHED, "matched"
        ),
    )
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


@pytest.mark.parametrize(
    ("status", "error", "want"),
    [
        (200, None, Result.MATCHED),
        (404, None, Result.UNMATCHED),
        (None, "down", Result.UNREACHABLE),
    ],
)
def test_archive_resolution_uses_status_and_distinguishes_404_from_outage(
    net_vault, monkeypatch, status, error, want
):
    source = net_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace(
            'doi: "10.1000/xyz"',
            'doi: "10.1000/xyz"\narchive-url: "https://archive.example/item"',
        )
    )
    if error:

        def unavailable(*_args):
            raise webapi.ApiError(error)

        monkeypatch.setattr(
            "harness_core.webapi.get_status",
            unavailable,
        )
    else:
        monkeypatch.setattr("harness_core.webapi.get_status", lambda *_: status)
    outcomes = _archive_outcomes(net_vault)
    assert outcomes[0].result is want


def test_cli_exit_precedence_ignores_warns_but_closing_beats_unreachable(
    net_vault, monkeypatch
):
    args = type("Args", (), {"vault": net_vault, "offline": True, "rw_csv": None})()
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
            "harness_core.__main__._verify_state",
            lambda *_args, items=outcomes, **_kwargs: (
                {"outcomes": items, "counts": {}},
                items,
                {id(item): "aa11" for item in items},
                {id(item): True for item in items},
            ),
        )
        assert cmd_verify(args) == expected


@pytest.mark.parametrize(
    ("result", "reason"),
    [
        (Result.MATCHED, "matched"),
        (Result.SKIPPED, "no-identifier — bibliography absent"),
        (Result.UNMATCHED, "stale — bibliography differs or is invalid"),
        (Result.UNREACHABLE, "outage — bibliography comparison unavailable"),
    ],
)
def test_staleness_reason_reflects_its_actual_result(
    net_vault, monkeypatch, result, reason
):
    monkeypatch.setattr("harness_core.bibliography.staleness", lambda *_: result)
    monkeypatch.setattr("harness_core.__main__._bibliography_entries", lambda _: [])
    report = run_verify(net_vault, network=True, detection_date="2026-08-16")
    staleness = next(o for o in report["outcomes"] if o.check == "staleness")
    assert staleness.result is result
    assert staleness.reason == reason


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
        "append-only", "+/review-queue.md", Result.UNMATCHED, "drift — inbox"
    )
    first = _target_hash(net_vault, append)
    (net_vault / "+" / "review-queue.md").write_text("new finding\n")
    assert _target_hash(net_vault, claim) is not None
    assert _target_hash(net_vault, append) == first


def test_marker_clear_uses_exact_origin_and_citekey_claim_collection(net_vault):
    other = net_vault / "atlas" / "other.md"
    other.write_text(
        "- (quote) [@smith2020] [verify-failed:: quote/2026-08-16] ^c-66666666\n"
    )
    origin = _outcome(
        "quote",
        "smith2020#^c-66666666",
        Result.MATCHED,
        "matched",
        note_path="efforts/brief/draft.md",
        claim_id="c-66666666",
    )
    _clear_verify_failed(net_vault, origin)
    assert "verify-failed" not in (net_vault / "efforts/brief/draft.md").read_text()
    assert "verify-failed" in other.read_text()
    citekey = _outcome(
        "citekey",
        "fabricated2020",
        Result.UNMATCHED,
        "mismatch — citekey not in bibliography",
        note_path="efforts/brief/draft.md",
        claims=[{"claim_id": "c-66666666"}, {"claim_id": "c-77777777"}],
    )
    _mutate_marker(net_vault, citekey, "2026-08-16")
    marked = (net_vault / "efforts/brief/draft.md").read_text()
    assert marked.count("verify-failed:: citekey/2026-08-16") == 2
    assert "verify-failed:: quote/2026-08-16" in other.read_text()
    _clear_verify_failed(net_vault, citekey)
    assert (
        "verify-failed:: citekey/2026-08-16"
        not in (net_vault / "efforts/brief/draft.md").read_text()
    )


def test_no_attachment_hash_ignores_event_and_marker_bytes_but_reopens_on_content(
    net_vault,
):
    source = net_vault / "literatures" / "smith2020.md"
    text = source.read_text().replace('attachment-sha256:\n  - "aa11"\n', "")
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
    finding = inbox.append_entry(
        net_vault,
        outcome.check,
        outcome.target,
        outcome.result,
        outcome.reason,
        target_hash=original,
    )
    inbox.append_ack(net_vault, finding.id, "manual — checked", "human:test", original)

    source.write_text(
        events.record_pass(
            source.read_bytes().decode(), "doi", Result.MATCHED, at="2026-08-16"
        ),
        newline="",
    )
    _mutate_marker(net_vault, outcome, "2026-08-17")
    after_effects = source.read_bytes()

    assert b"\r\r\n" not in after_effects
    assert _target_hash(net_vault, outcome) == original
    assert inbox.is_acknowledged(
        net_vault, outcome.check, outcome.target, current_hash=original
    )

    source.write_bytes(after_effects.replace(b"Mortality fell", b"Mortality rose", 1))
    assert _target_hash(net_vault, outcome) != original

    source.write_bytes(
        after_effects.replace(b'status: "active"', b'status: "deprecated"')
    )
    assert _target_hash(net_vault, outcome) != original


def test_marker_mutation_preserves_crlf_and_exact_claim_spacing(net_vault):
    note = net_vault / "atlas" / "crlf markers.md"
    original = (
        b"- (quote) anchored [@missing]   ^c-1\r\n- (quote) line only [@missing]\r\n"
    )
    note.write_bytes(original)
    anchored = _outcome(
        "citekey",
        "missing",
        Result.UNMATCHED,
        "mismatch — citekey not in bibliography",
        note_path="atlas/crlf markers.md",
        claims=[{"claim_id": "c-1"}],
    )
    anchored_hash = _target_hash(net_vault, anchored)

    _mutate_marker(net_vault, anchored, "2026-08-16")
    stamped = note.read_bytes()

    assert b"   [verify-failed:: citekey/2026-08-16] ^c-1\r\n" in stamped
    assert b"\r [verify-failed" not in stamped
    assert _target_hash(net_vault, anchored) == anchored_hash
    _clear_verify_failed(net_vault, anchored)
    assert note.read_bytes() == original
    assert _target_hash(net_vault, anchored) == anchored_hash

    line_only = _outcome(
        "quote",
        "missing",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="atlas/crlf markers.md",
        line_no=2,
    )
    line_hash = _target_hash(net_vault, line_only)
    _mutate_marker(net_vault, line_only, "2026-08-16")
    stamped = note.read_bytes()
    assert b"line only [@missing] [verify-failed:: quote/2026-08-16]\r\n" in stamped
    assert b"\r [verify-failed" not in stamped
    assert _target_hash(net_vault, line_only) == line_hash
    _clear_verify_failed(net_vault, line_only)
    assert note.read_bytes() == original
    assert _target_hash(net_vault, line_only) == line_hash


def test_marker_stamp_ignores_prose_lookalike_and_clears_only_terminal_field(
    net_vault,
):
    note = net_vault / "atlas" / "marker prose.md"
    original = (
        "- (quote) prose [verify-failed:: quote/2026-08-16] remains human text ^c-1\n"
    )
    note.write_text(original)
    outcome = _outcome(
        "quote",
        "missing#^c-1",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="atlas/marker prose.md",
        claim_id="c-1",
    )

    _mutate_marker(net_vault, outcome, "2026-08-17")

    assert note.read_text() == original.replace(
        " ^c-1", " [verify-failed:: quote/2026-08-17] ^c-1"
    )
    _clear_verify_failed(net_vault, outcome)
    assert note.read_text() == original


def test_no_attachment_acknowledged_warning_stays_suppressed_across_effects(
    net_vault, monkeypatch, capsys
):
    source = net_vault / "literatures" / "smith2020.md"
    source.write_text(
        source.read_text().replace('attachment-sha256:\n  - "aa11"\n', "")
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
    )
    inbox.append_ack(
        net_vault, finding.id, "manual — checked", "human:test", target_hash
    )
    monkeypatch.setattr("harness_core.__main__._file_outcomes", lambda *_: [])
    monkeypatch.setattr(
        "harness_core.__main__._bibliography_entries",
        lambda _: [{"id": "smith2020", "DOI": "10.1000/xyz"}],
    )
    monkeypatch.setattr("harness_core.__main__._network_outcomes", lambda *_: [warning])
    monkeypatch.setattr(
        "harness_core.__main__._staleness_outcome",
        lambda *_: _outcome(
            "staleness", "x/bibliography.json", Result.MATCHED, "matched"
        ),
    )
    for name in (
        "lint_append_only",
        "lint_claim_immutability",
        "lint_published_drift",
        "lint_web_archive",
    ):
        monkeypatch.setattr(f"harness_core.lints.{name}", lambda *_: [])
    monkeypatch.setattr("harness_core.__main__._archive_outcomes", lambda *_: [])

    first, effective, _hashes, warning_effective = _verify_state(
        net_vault, network=True, detection_date="2026-08-16"
    )
    second, _, _, second_warning_effective = _verify_state(
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
    note = net_vault / "atlas" / "synthèse space.md"
    note.write_text("- (quote) local [@missing] ^c-local\n")
    outcome = _outcome(
        "quote",
        "missing#^c-local",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="atlas/synthèse space.md",
        claim_id="c-local",
    )

    assert _target_hash(net_vault, outcome) is not None
    _mutate_marker(net_vault, outcome, "2026-08-16")
    assert "verify-failed:: quote/2026-08-16" in note.read_text()
    _clear_verify_failed(net_vault, outcome)
    assert "verify-failed" not in note.read_text()

    outside_root = tmp_path.parent / f"{tmp_path.name}-outside"
    outside_root.mkdir()
    outside = outside_root / "outside.md"
    outside.write_text("outside remains private\n")
    direct_link = net_vault / "atlas" / "outside-link.md"
    direct_link.symlink_to(outside)
    assert _safe_relative(net_vault, "atlas/outside-link.md") is None
    assert (
        _target_hash(
            net_vault,
            _outcome("append-only", "atlas/outside-link.md", Result.UNMATCHED, "drift"),
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

    directory = net_vault / "efforts" / "published"
    nested = directory / "nested"
    nested.mkdir(parents=True)
    first_target = outside_root / "first-target"
    second_target = outside_root / "second-target"
    first_target.write_text("outside bytes must not be read\n")
    second_target.write_text("also outside\n")
    link = nested / "escape"
    link.symlink_to(first_target)
    directory_outcome = _outcome(
        "published-drift", "efforts/published", Result.UNMATCHED, "drift"
    )
    first = _target_hash(net_vault, directory_outcome)
    first_target.write_text("changing outside content stays invisible\n")
    assert _target_hash(net_vault, directory_outcome) == first
    link.unlink()
    link.symlink_to(second_target)
    assert _target_hash(net_vault, directory_outcome) != first


@pytest.mark.parametrize(
    "raw_citekey",
    [42, ["not-a-citekey"], "", " ../escape", "nested/file", "bad\0key"],
)
def test_archive_invalid_citekey_falls_back_to_safe_note_target(
    net_vault, monkeypatch, raw_citekey
):
    source = net_vault / "literatures" / "smith2020.md"
    if isinstance(raw_citekey, list):
        citekey_line = 'citekey:\n  - "not-a-citekey"'
    elif isinstance(raw_citekey, int):
        citekey_line = f"citekey: {raw_citekey}"
    else:
        citekey_line = f'citekey: "{raw_citekey}"'
    source.write_text(
        source.read_text()
        .replace('citekey: "smith2020"', citekey_line)
        .replace(
            'doi: "10.1000/xyz"',
            'doi: "10.1000/xyz"\narchive-url: "https://archive.example/item"',
        )
    )
    monkeypatch.setattr("harness_core.webapi.get_status", lambda *_: 200)

    outcome = _archive_outcomes(net_vault)[0]

    assert outcome.target == "literatures/smith2020.md"
    assert _target_hash(net_vault, outcome) is not None
    filed = inbox.append_entry(
        net_vault,
        outcome.check,
        outcome.target,
        outcome.result,
        outcome.reason,
        target_hash=_target_hash(net_vault, outcome),
    )
    assert json.dumps(filed.__dict__)


def test_main_routes_base_before_and_after_verify(net_vault, monkeypatch, capsys):
    bases = []

    def state(*_args, **kwargs):
        bases.append(kwargs["base"])
        return {"outcomes": [], "counts": {}}, [], {}, {}

    monkeypatch.setattr("harness_core.__main__._verify_state", state)

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
            "harness_core",
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

    assert verify.returncode == 1
    assert "fabricated2020" in verify.stdout

    review = subprocess.run(
        [sys.executable, "-m", "harness_core", "inbox", "--vault", str(net_vault)],
        cwd=core,
        capture_output=True,
        text=True,
        check=False,
    )

    assert review.returncode == 0
    assert '"unacknowledged"' in review.stdout
    assert "fabricated2020" in review.stdout


def test_warn_dedup_reconstructs_type_and_inbox_is_oldest_first(net_vault, capsys):
    inbox.append_entry(
        net_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — correction",
        date="2026-08-01",
        target_hash="aa11",
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


@pytest.mark.live_net
def test_live_drill_wakefield_and_fabricated(net_vault_real_mailto):
    outcome = checks.check_update_notice(
        net_vault_real_mailto,
        {"id": "wakefield1998", "DOI": "10.1016/S0140-6736(97)11096-0"},
        "2026-08-16",
    )
    assert outcome.result is Result.UNMATCHED
    assert outcome.extra["notice_date"] == "2010-02-02"
    fabricated = checks.check_doi_exists(
        net_vault_real_mailto, "10.1000/completely-fabricated-2026"
    )
    assert fabricated.result is Result.UNMATCHED
    assert (
        checks.registry_agency(net_vault_real_mailto, "10.5281/zenodo.3678326")
        == "DataCite"
    )
