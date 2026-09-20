"""Integration regressions for the verify and inbox command surface."""

import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from unittest.mock import Mock

import pytest

from research_vault import (
    Result,
    bibliography,
    checks,
    claims,
    events,
    frontmatter,
    gitstate,
    identify,
    inbox,
    lints,
    literature_notes,
    markers,
    verify,
    zotero,
)
from research_vault.__main__ import cmd_inbox, cmd_verify, main
from research_vault.markers import _mutate_marker, _safe_relative
from research_vault.pathcodec import PathCodecError, RepoPath, encode_repo_path
from research_vault.verify import (
    DEFAULT_BASE,
    _apply_state_transitions,
    _citation_key_hash,
    _claim_bytes_from_text,
    _file_effects,
    _note_bytes,
    _target_hash,
    verify_state,
)
from tests.conftest import must_replace


def run_verify(vault_root, **kwargs):
    """Report projection of the verification transaction, for assertions only."""
    return verify_state(vault_root, **kwargs)[0]


def _verify_args(vault, **overrides):
    """The `Args` a direct `cmd_verify` call needs, complete: `cmd_verify`
    reads every attribute `main()` sets, with no `getattr` fallback."""
    args = {
        "vault": vault,
        "offline": True,
        "rw_csv": None,
        "surface": "audit",
        "base": DEFAULT_BASE,
        "git_base": None,
        "git_candidate": "worktree",
        "changed_paths_file": None,
        "commit_projected": None,
        "as_of": None,
    }
    args.update(overrides)
    return type("Args", (), args)()


def _outcome(check, target, result, reason, **extra):
    if isinstance(extra.get("note_path"), str):
        extra["note_path"] = RepoPath(os.fsencode(extra["note_path"]))
    if check == "append-only" and isinstance(target, str):
        target = RepoPath(os.fsencode(target))
    return checks.Outcome(check, target, result, reason, extra)


def _move_note_body(source):
    """Change the literature note's body and re-witness it, so the content an
    acknowledgment was scoped to moves (`managed-sha256` with it)."""
    old_text = source.read_text()
    new_text = must_replace(
        old_text, "# Mortality decline\n", "# Mortality decline, revised\n"
    )
    source.write_text(
        must_replace(
            new_text,
            f'managed-sha256: "{literature_notes.body_sha256(old_text)}"',
            f'managed-sha256: "{literature_notes.body_sha256(new_text)}"',
        )
    )


def _without_witness(text):
    """The note as capture never wrote it: no `managed-sha256`, so
    `_citation_key_hash` takes its `_note_bytes` fallback."""
    return must_replace(
        text, f'managed-sha256: "{literature_notes.body_sha256(text)}"\n', ""
    )


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
        must_replace(
            draft.read_text(), "Mortality fell 12% across all strata.", "wrong quote"
        )
    )
    first = run_verify(net_vault, network=False, detection_date="2026-08-16")
    raw = next(
        o
        for o in first["outcomes"]
        if o.check == "quote" and o.result is Result.UNMATCHED
    )
    entry = next(
        e
        for e in inbox.open_entries(net_vault)
        if e.check == "quote" and e.target == raw.target
    )
    assert (
        main(
            [
                "ack",
                entry.id,
                "--vault",
                str(net_vault),
                "--reason",
                "manual — checked",
                "--actor",
                "human:test",
            ]
        )
        == 0
    )
    second = run_verify(net_vault, network=False, detection_date="2026-08-16")
    assert any(
        o is not None and o.check == "quote" and o.result is Result.UNMATCHED
        for o in second["outcomes"]
    )
    # The marker mirrors the inbox row: the ack closed both, and the next run
    # stamps only what is still effective (open point 09, resolution i).
    assert "[failed-verification:: quote/" not in draft.read_text()
    assert not any(
        e.check == "quote" and e.target == raw.target
        for e in inbox.open_entries(net_vault)
    )
    draft.write_text(
        must_replace(draft.read_text(), "wrong quote", "different wrong quote")
    )
    run_verify(net_vault, network=False, detection_date="2026-08-16")
    assert not any(
        e.check == "quote" and e.target == raw.target
        for e in inbox.open_entries(net_vault)
    )
    source = net_vault / "literature" / "smith2020.md"
    _move_note_body(source)
    # Committed so `lint_evidence_layer`'s base and candidate agree on the
    # moved body — this test exercises hash-based reopening, not the
    # machine-owned-frontmatter guard.
    subprocess.run(["git", "add", "-A"], cwd=net_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "move the note body"], cwd=net_vault, check=True
    )
    fourth = run_verify(net_vault, network=False, detection_date="2026-08-16")
    assert any(
        e.check == "quote" and e.target == raw.target
        for e in inbox.open_entries(net_vault)
    )
    assert fourth["counts"]["UNMATCHED"] >= 1
    # The ack lapsed with the body, so the marker returns with the finding.
    assert "[failed-verification:: quote/" in draft.read_text()


def test_target_hash_routes_safe_file_claim_and_citation_key(net_vault):
    file_outcome = _outcome(
        "append-only", "log/2026-08-16.md", Result.UNMATCHED, "drift — file"
    )
    claim_outcome = _outcome(
        "quote", "smith2020#^c-11111111", Result.UNMATCHED, "mismatch — quote"
    )
    citation_key_outcome = _outcome(
        "doi", "smith2020", Result.UNMATCHED, "mismatch — doi"
    )
    candidate_snapshot = gitstate.snapshot_worktree(net_vault)
    assert (
        _target_hash(net_vault, file_outcome, candidate_snapshot=candidate_snapshot)
        == hashlib.sha256((net_vault / "log/2026-08-16.md").read_bytes()).hexdigest()[
            :16
        ]
    )
    # A claim target and a citation-key target both route to the cited note's
    # own `managed-sha256` (open point 07), and a marker landing on the note
    # does not move it: verify's own write never lapses the ack it is scoped by.
    claim_hash = _target_hash(net_vault, claim_outcome)
    assert claim_hash == _citation_key_hash(net_vault, "smith2020")
    assert _target_hash(net_vault, citation_key_outcome) == claim_hash
    source = net_vault / "literature" / "smith2020.md"
    source.write_text(
        must_replace(
            source.read_text(),
            "^c-11111111",
            "[failed-verification:: quote/2026-08-16] ^c-11111111",
        )
    )
    assert _target_hash(net_vault, claim_outcome) == claim_hash
    assert _target_hash(net_vault, citation_key_outcome) == claim_hash
    with pytest.raises(PathCodecError):
        RepoPath(b"../outside")


def test_well_formed_managed_sha256_never_reaches_the_note_bytes_fallback(
    net_vault, monkeypatch
):
    """Both `_citation_key_hash` branches return the witness capture wrote and
    never hash the note themselves (open point 07)."""
    from research_vault import verify

    source = net_vault / "literature" / "smith2020.md"
    witness = frontmatter.parse(source.read_text())[0]["managed-sha256"]

    def never(_data):
        raise AssertionError("a witnessed note must not reach the _note_bytes fallback")

    monkeypatch.setattr(verify, "_note_bytes", never)
    assert _citation_key_hash(net_vault, "smith2020") == witness
    candidate_snapshot = gitstate.snapshot_worktree(net_vault)
    assert (
        _citation_key_hash(
            net_vault, "smith2020", candidate_snapshot=candidate_snapshot
        )
        == witness
    )


@pytest.mark.parametrize("placeholder", ["unresolved", "aa11"])
def test_malformed_managed_sha256_falls_through_to_the_note_bytes_digest(
    net_vault, placeholder
):
    """Two shapes, not one: "unresolved" is non-hex (fails the character
    class), "aa11" is valid hex but short (fails the length bound) — so this
    pins the ``{64}`` bound on both `_citation_key_hash` branches, and that a
    witness capture did not write never becomes an ack scope.
    """
    source = net_vault / "literature" / "smith2020.md"
    text = source.read_text()
    source.write_text(
        must_replace(
            text,
            f'managed-sha256: "{literature_notes.body_sha256(text)}"',
            f'managed-sha256: "{placeholder}"',
        )
    )
    claim_outcome = _outcome(
        "quote", "smith2020#^c-11111111", Result.UNMATCHED, "mismatch — quote"
    )
    expected = hashlib.sha256(_note_bytes(source.read_bytes())).hexdigest()[:16]
    assert expected != placeholder
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
    note = net_vault / "literature" / "blank.md"
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


def test_missing_citation_key_hash_uses_exact_checked_origins_and_reopens(net_vault):
    draft = net_vault / "projects" / "brief" / "draft.md"
    outcome = _outcome(
        "citation-key",
        "fabricated2020",
        Result.UNMATCHED,
        "mismatch — citation key not in bibliography",
        note_path="projects/brief/draft.md",
        claims=[{"claim_id": "c-77777777"}],
    )
    original = _target_hash(net_vault, outcome)
    assert original is not None
    draft.write_text(
        must_replace(draft.read_text(), "This will replicate", "This will not")
    )
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
            (net_vault / "literature" / "smith2020.md").read_text()
        )
    )


def test_run_verify_mints_exact_quote_event_on_cited_literature_note(net_vault):
    report = run_verify(net_vault, network=False, detection_date="2026-08-16")
    assert any(
        outcome.check == "citation-key"
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
        if entry.check == "citation-key" and entry.target == "fabricated2020"
    ]
    run_verify(net_vault, network=False, detection_date="2026-08-16")
    second_entries = [
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.check == "citation-key" and entry.target == "fabricated2020"
    ]
    run_verify(net_vault, network=False, detection_date="2026-08-16")
    third_entries = [
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.check == "citation-key" and entry.target == "fabricated2020"
    ]
    # The tool's own stamp never moves an ack scope (open point 07):
    # one row across three runs, not a second one filed over the stamped draft.
    assert len(first_entries) == len(second_entries) == len(third_entries) == 1
    assert first_entries[0].target_hash == second_entries[0].target_hash
    source = (net_vault / "literature" / "smith2020.md").read_text()
    recorded = {event["check"] for event in events.verified_checks(source)}
    assert "quote:smith2020#^c-66666666:managed-region" in recorded


# --- the CLI's parser and pass-through contract -------------------------------

_SUBCOMMANDS_WITH_VAULT = [
    ["capture", "K"],
    ["add", "--item", "i.json"],
    ["propagate"],
    ["verify"],
    ["factcheck", "--draft", "d.md"],
    ["trust-tier", "key2020"],
    ["arm-publish", "brief"],
    ["disarm-publish"],
    ["mark-published", "brief"],
    ["mark-corrected", "brief"],
    ["mark-withdrawn", "brief"],
    ["mark-parked", "brief"],
    ["ack", "f-1", "--reason", "r", "--actor", "human:x"],
    ["finding", "quote", "t", "UNMATCHED", "reason"],
    ["search-log", "--project", "brief"],
    ["inbox"],
    ["scaffold"],
    ["doctor"],
    ["stamp-type"],
]


@pytest.mark.parametrize("argv", _SUBCOMMANDS_WITH_VAULT, ids=lambda a: a[0])
def test_every_vault_verb_requires_vault_and_accepts_base_after_it(argv, capsys):
    """Each verb refuses to run without --vault (argparse exit 2 naming it),
    and takes --base after the verb: the shared parent is attached to every
    subparser, so the only complaint is the missing --vault, never an
    unrecognized --base."""
    with pytest.raises(SystemExit) as caught:
        main([*argv, "--base", "http://127.0.0.1:9"])
    assert caught.value.code == 2
    err = capsys.readouterr().err
    assert "--vault" in err
    assert "unrecognized" not in err


class _StubClient:
    """A ZoteroClient stand-in whose every call is an outage: no socket."""

    def __init__(self, base=None):
        self.base = base
        self.server_id = None
        self.api_key = None

    def __getattr__(self, name):
        def refuse(*_args, **_kwargs):
            raise zotero.ZoteroError("stubbed — no Zotero here")

        return refuse


def _verb_argvs(vault):
    """Every verb with the arguments it takes on a bare vault, and the exit
    code its handler answers there: 3 where the stubbed Zotero is the first
    thing the verb reaches (UNREACHABLE), 2 where the verb refuses before
    Zotero -- a missing --item / --draft file, an unknown citation key, a
    project directory that is not there, a disposition on a project never
    published, an ack naming no finding, a search-log run with neither
    --query nor --not-admitted -- and 0 where it runs to the end (a plan
    with nothing to propagate, an offline verify, a filed finding, the
    readers and the fixers, doctor with its probes stubbed to none)."""
    v = str(vault)
    return [
        (["probe"], 3),
        (["capture", "K", "--vault", v], 3),
        (["add", "--vault", v, "--item", str(vault / "missing.json")], 2),
        (["propagate", "--vault", v], 0),
        (["verify", "--vault", v, "--offline"], 0),
        (["factcheck", "--vault", v, "--draft", "missing.md"], 2),
        (["trust-tier", "nobody2020", "--vault", v], 2),
        (["arm-publish", "brief", "--vault", v], 2),
        (["disarm-publish", "--vault", v], 0),
        (["mark-published", "brief", "--vault", v], 2),
        (["mark-corrected", "brief", "--vault", v], 2),
        (["mark-withdrawn", "brief", "--vault", v], 2),
        (["mark-parked", "brief", "--vault", v], 2),
        (
            [
                "ack",
                "f-1",
                "--vault",
                v,
                "--reason",
                "manual — x",
                "--actor",
                "human:x",
            ],
            2,
        ),
        (["finding", "quote", "t", "UNMATCHED", "mismatch — x", "--vault", v], 0),
        (["search-log", "--vault", v, "--project", "brief"], 2),
        (["inbox", "--vault", v], 0),
        (["scaffold", "--vault", v], 0),
        (["doctor", "--vault", v], 0),
        (["stamp-type", "--vault", v], 0),
    ]


def test_every_verb_takes_base_after_the_verb_and_runs(tmp_vault, monkeypatch, capsys):
    """The shared parent parser is attached to every subparser: `--base` after
    the verb parses (argparse's SystemExit is the one outcome a dropped
    parent would produce), and the verb then runs to the exit code its
    handler answers on a bare vault -- each one known, so a verb that stops
    at the wrong refusal is caught, not just one that fails to parse. Zotero
    is a stub that refuses every call, so no verb opens a socket."""
    import research_vault.__main__ as cli

    monkeypatch.setattr(cli, "ZoteroClient", _StubClient)
    monkeypatch.setattr(cli, "doctor", lambda vault, client: [])
    for argv, expected in _verb_argvs(tmp_vault):
        code = main([*argv, "--base", "http://127.0.0.1:9"])
        assert code == expected, (argv, capsys.readouterr())
        capsys.readouterr()


def test_doctor_alone_runs_on_an_unreadable_machine_json(
    tmp_vault, monkeypatch, capsys
):
    """Every other verb refuses an unreadable machine.json before running;
    doctor resolves its base non-strictly so its machine-config probe can be
    the one to report the file -- and doctor gets the vault, not None."""
    import research_vault.__main__ as cli

    seen: list = []
    monkeypatch.setattr(cli, "ZoteroClient", _StubClient)
    monkeypatch.setattr(
        cli, "doctor", lambda vault, client: seen.append((vault, client.base)) or []
    )
    (tmp_vault / ".research-vault").mkdir(exist_ok=True)
    (tmp_vault / ".research-vault" / "machine.json").write_text("{not json")
    assert main(["inbox", "--vault", str(tmp_vault)]) == 2
    assert capsys.readouterr().err.startswith("machine.json unreadable")
    assert main(["doctor", "--vault", str(tmp_vault)]) == 0
    assert capsys.readouterr().err == ""
    assert seen == [(str(tmp_vault), zotero.DEFAULT_BASE)]


def test_verify_surface_is_one_of_the_closing_surfaces(net_vault, capsys):
    with pytest.raises(SystemExit) as caught:
        main(["verify", "--vault", str(net_vault), "--surface", "release"])
    assert caught.value.code == 2
    assert "invalid choice: 'release'" in capsys.readouterr().err


def test_the_other_required_flags_and_the_verb_itself_are_required(capsys):
    for argv, flag in [
        (["add", "--vault", "v"], "--item"),
        (["factcheck", "--vault", "v"], "--draft"),
        (["ack", "f-1", "--vault", "v", "--actor", "human:x"], "--reason"),
        (["ack", "f-1", "--vault", "v", "--reason", "r"], "--actor"),
        (["search-log", "--vault", "v"], "--project"),
        ([], "cmd"),
    ]:
        with pytest.raises(SystemExit) as caught:
            main(argv)
        assert caught.value.code == 2
        assert flag in capsys.readouterr().err


def test_probe_takes_base_after_the_verb_and_nothing_positional(capsys):
    with pytest.raises(SystemExit) as caught:
        main(["probe", "--base", "http://127.0.0.1:9", "extra"])
    assert caught.value.code == 2
    assert capsys.readouterr().err.rstrip().endswith("unrecognized arguments: extra")


def test_verify_git_candidate_choices_and_git_base_are_parsed(net_vault, capsys):
    """`--git-candidate` accepts exactly worktree/index/HEAD; `--git-base`
    is a flag. The later `--commit-projected` usage error proves the parser
    accepted the flags before it."""
    for candidate in ("worktree", "index", "HEAD"):
        with pytest.raises(SystemExit) as caught:
            main(
                [
                    "verify",
                    "--vault",
                    str(net_vault),
                    "--git-candidate",
                    candidate,
                    "--git-base",
                    "HEAD",
                    "--commit-projected",
                    " ",
                ]
            )
        assert caught.value.code == 2
        assert "--commit-projected requires a non-empty message" in (
            capsys.readouterr().err
        )
    with pytest.raises(SystemExit) as caught:
        main(["verify", "--vault", str(net_vault), "--git-candidate", "stash"])
    assert caught.value.code == 2
    assert "invalid choice: 'stash'" in capsys.readouterr().err


def test_scaffold_and_stamp_type_run_in_process_with_their_flags(tmp_path, capsys):
    """The dispatch table names them and their flags parse: scaffold's two
    store_true flags take no value, and stamp-type's --vault is read."""
    vault = tmp_path / "vault"
    assert main(["scaffold", "--vault", str(vault), "--with-ci", "--with-rw-ci"]) == 0
    created = capsys.readouterr().out.splitlines()
    assert ".github/workflows/verify.yml" in created
    assert ".github/workflows/rw-batch.yml" in created
    (vault / "inbox" / "idea.md").write_text("a thought\n")
    assert main(["stamp-type", "--vault", str(vault)]) == 0
    assert capsys.readouterr().out.splitlines() == ["stamped inbox/idea.md"]


def test_stamp_type_prints_each_report_reason_on_its_own_line(tmp_path, capsys):
    """The three reasons stamp_types reports each get their own line, in walk
    order, after the stamped notes; the exit is 0 regardless. The branch,
    not the sentence: each line's `skipped <path> — ` prefix and the token
    that names its reason, which is what the branch mutants change (a
    comparison flipped or its literal rewritten sends a reason down the
    wrong branch; a `print(None)` breaks the prefix)."""
    vault = tmp_path / "vault"
    (vault / "a-loose").mkdir(parents=True)
    (vault / "a-loose" / "e-notype.md").write_text("loose\n")
    inbox = vault / "inbox"
    inbox.mkdir()
    (inbox / "b-link.md").symlink_to(vault / "nowhere.md")
    (inbox / "c-bad.md").write_text("---\n  bad: nested\n---\ntext\n")
    (inbox / "d-idea.md").write_text("a thought\n")
    assert main(["stamp-type", "--vault", str(vault)]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "stamped inbox/d-idea.md"
    reported = [
        ("skipped a-loose/e-notype.md — ", "no type"),
        ("skipped inbox/b-link.md — ", "symlink"),
        ("skipped inbox/c-bad.md — ", "unparseable"),
    ]
    assert len(lines) == 1 + len(reported)
    for line, (prefix, token) in zip(lines[1:], reported, strict=True):
        assert line.startswith(prefix), line
        assert token in line, line
        assert sum(other in line for _, other in reported) == 1, line


def test_verify_passes_every_flag_through_and_prints_sorted_counts(
    net_vault, monkeypatch, capsys, tmp_path
):
    seen: list[dict] = []

    def state(vault, **kwargs):
        seen.append({"vault": vault, **kwargs})
        return {"outcomes": [], "counts": {"b": 1, "a": 2}}, [], {}, {}

    monkeypatch.setattr("research_vault.__main__.verify_state", state)
    csv = tmp_path / "rw.csv"
    csv.write_text("")
    assert (
        main(
            [
                "verify",
                "--vault",
                str(net_vault),
                "--offline",
                "--as-of",
                "2026-09-07",
                "--rw-csv",
                str(csv),
                "--git-base",
                "HEAD",
                "--git-candidate",
                "index",
                "--surface",
                "commit",
            ]
        )
        == 0
    )
    assert seen == [
        {
            "vault": str(net_vault),
            "network": False,
            "detection_date": "2026-09-07",
            "rw_csv": str(csv),
            "base": seen[0]["base"],
            "git_base": "HEAD",
            "git_candidate": "index",
            "changed_paths_file": None,
            "commit_projected": None,
        }
    ]
    assert seen[0]["base"].startswith("http")
    assert capsys.readouterr().out.splitlines() == ['{"a": 2, "b": 1}']


def test_verify_prints_a_warn_notice_only_when_it_is_effective_by_index_or_outcome(
    net_vault, monkeypatch, capsys
):
    by_index = _outcome(
        "update-notice",
        "a2020",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction"}],
    )
    by_outcome = _outcome(
        "update-notice",
        "b2020",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "expression-of-concern"}],
    )
    ineffective = _outcome(
        "update-notice",
        "c2020",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "retraction"}],
    )
    unlisted = _outcome(
        "update-notice",
        "d2020",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "withdrawal"}],
    )
    items = [by_index, by_outcome, ineffective, unlisted]
    monkeypatch.setattr(
        "research_vault.__main__.verify_state",
        lambda *_args, **_kwargs: (
            {"outcomes": items, "counts": {}},
            items,
            {id(item): "aa11" for item in items},
            {
                (id(by_index), 0): True,
                id(by_outcome): True,
                (id(ineffective), 0): False,
            },
        ),
    )
    code = main(
        ["verify", "--vault", str(net_vault), "--offline", "--surface", "publish"]
    )
    out = capsys.readouterr().out
    assert code == 1
    assert "UNMATCHED update-notice a2020 — warn-notice — correction" in out
    assert "UNMATCHED update-notice b2020 — warn-notice — expression-of-concern" in out
    assert "c2020" not in out
    assert "d2020" not in out


def test_verify_reports_a_named_failure_on_stderr_only_and_exits_2(
    net_vault, monkeypatch, capsys
):
    def failing(*_args, **_kwargs):
        raise OSError(30, "Read-only file system")

    monkeypatch.setattr("research_vault.__main__.verify_state", failing)
    assert main(["verify", "--vault", str(net_vault), "--offline"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("verification unavailable: [Errno 30]")


def test_inbox_prints_a_sorted_summary_and_refuses_a_malformed_as_of(net_vault, capsys):
    assert main(["inbox", "--vault", str(net_vault), "--as-of", "2026-09-07"]) == 0
    first = capsys.readouterr().out.splitlines()[0]
    summary = json.loads(first)
    assert first == json.dumps(summary, sort_keys=True)
    assert list(summary) == sorted(summary)
    assert main(["inbox", "--vault", str(net_vault), "--as-of", "yesterday"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""


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
    code = cmd_verify(_verify_args(net_vault, offline=True, rw_csv=None))
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
    cmd_verify(_verify_args(net_vault, offline=True, rw_csv=None))
    output = capsys.readouterr().out
    assert "retracted — retraction" in output
    assert "warn-notice — correction" in output


def test_acknowledged_matched_warn_mints_event_without_refiling_or_printing(
    net_vault, monkeypatch, capsys
):
    warning = _outcome(
        "update-notice",
        "smith2020",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction"}],
    )
    target_hash = _target_hash(net_vault, warning)
    entry = inbox.append_entry(
        net_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — correction",
        target_hash=target_hash,
        notice_class="warn",
        notice_type="correction",
    )
    inbox.append_ack(net_vault, entry.id, "manual — checked", "human:test", target_hash)
    monkeypatch.setattr(
        "research_vault.verify._bibliography_entries",
        lambda _: [{"id": "smith2020", "DOI": "10.1000/xyz"}],
    )
    monkeypatch.setattr("research_vault.verify._network_outcomes", lambda *_: [warning])
    cmd_verify(_verify_args(net_vault, offline=False, rw_csv=None))
    source = (net_vault / "literature" / "smith2020.md").read_text()
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

    _apply_state_transitions(net_vault, [outcome], "2026-08-16", stamp=[outcome])

    source = (net_vault / "literature" / "smith2020.md").read_text()
    assert not any(
        event["check"] == "update-notice" for event in events.verified_checks(source)
    )
    assert any(
        row["check"] == "update-notice" for row in events.current_failures(source)
    )


def test_cli_exit_precedence_ignores_warns_but_closing_beats_unreachable(
    net_vault, monkeypatch
):
    args = _verify_args(net_vault, offline=True, rw_csv=None, surface="publish")
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
    note = net_vault / "literature" / "smith2020.md"
    note.unlink()
    claim = _outcome(
        "claim-immutability",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "drift — deleted claim",
        note_path="literature/smith2020.md",
        claim_id="c-11111111",
    )
    append = _outcome(
        "append-only", "inbox/review-queue.md", Result.UNMATCHED, "drift — inbox"
    )
    candidate_snapshot = gitstate.snapshot_worktree(net_vault)
    first = _target_hash(net_vault, append, candidate_snapshot=candidate_snapshot)
    with (net_vault / "inbox" / "review-queue.md").open("a") as queue:
        queue.write("new finding\n")
    candidate_snapshot = gitstate.snapshot_worktree(net_vault)
    assert _target_hash(net_vault, claim) is not None
    assert (
        _target_hash(net_vault, append, candidate_snapshot=candidate_snapshot) == first
    )


def test_deleted_claim_with_invalid_utf8_has_a_stable_target_hash(net_vault):
    """A leading, unrelated bullet makes the committed note bigger than the
    one claim: without it, `_target_hash`'s fallthrough to `_identifier_hash`
    (which hashes the whole note through the very same `"HEAD"` blob lookup
    once `_claim_anchor_hash` gives up) would coincidentally reproduce a
    single-bullet file's hash regardless of whether the claim-anchor leg's
    own `vault_root`/`"HEAD"`/`raw_origin` arguments are the real ones."""
    note = net_vault / "projects" / "brief" / "invalid-utf8.md"
    other_bytes = b"- (quote) unrelated bullet [@missing] ^c-other\n"
    claim_bytes = b"- (quote) invalid \xff [@missing] ^c-invalid\n"
    note.write_bytes(other_bytes + claim_bytes)
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


def test_marker_clear_uses_exact_origin_and_citation_key_claim_collection(net_vault):
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
    citation_key = _outcome(
        "citation-key",
        "fabricated2020",
        Result.UNMATCHED,
        "mismatch — citation key not in bibliography",
        note_path="projects/brief/draft.md",
        claims=[{"claim_id": "c-66666666"}, {"claim_id": "c-77777777"}],
    )
    _mutate_marker(net_vault, citation_key, "2026-08-16")
    marked = (net_vault / "projects/brief/draft.md").read_text()
    assert marked.count("failed-verification:: citation-key/2026-08-16") == 2
    assert "failed-verification:: quote/2026-08-16" in other.read_text()
    _mutate_marker(net_vault, citation_key, "2026-08-16", clear=True)
    assert (
        "failed-verification:: citation-key/2026-08-16"
        not in (net_vault / "projects/brief/draft.md").read_text()
    )


def test_unwitnessed_note_hash_ignores_events_and_markers_but_content_is_substantive(
    net_vault,
):
    """The `_note_bytes` fallback, for a note capture never wrote: verifier
    events and verify's own marker are not content (open point 07);
    the body and the frontmatter the author wrote are."""
    source = net_vault / "literature" / "smith2020.md"
    text = _without_witness(source.read_text())
    source.write_bytes(must_replace(text, "\n", "\r\n", -1).encode())
    outcome = _outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="literature/smith2020.md",
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
    assert marked_hash == original  # the stamp is not scope
    assert inbox.is_acknowledged(
        net_vault, outcome.check, outcome.target, current_hash=marked_hash
    )

    source.write_bytes(
        must_replace(
            after_effects.decode(), "Mortality fell", "Mortality rose"
        ).encode()
    )
    assert _target_hash(net_vault, outcome) != marked_hash

    source.write_bytes(
        must_replace(
            after_effects.decode(), "zotero-item-version: 12", "zotero-item-version: 13"
        ).encode()
    )
    assert _target_hash(net_vault, outcome) != marked_hash


def test_marker_mutation_preserves_crlf_and_exact_claim_spacing(net_vault):
    note = net_vault / "projects" / "brief" / "crlf markers.md"
    original = (
        b"- (quote) anchored [@missing]   ^c-1\r\n- (quote) line only [@missing]\r\n"
    )
    note.write_bytes(original)
    anchored = _outcome(
        "citation-key",
        "missing",
        Result.UNMATCHED,
        "mismatch — citation key not in bibliography",
        note_path="projects/brief/crlf markers.md",
        claims=[{"claim_id": "c-1"}],
    )
    anchored_hash = _target_hash(net_vault, anchored)

    _mutate_marker(net_vault, anchored, "2026-08-16")
    stamped = note.read_bytes()

    assert b"   [failed-verification:: citation-key/2026-08-16] ^c-1\r\n" in stamped
    assert b"\r [failed-verification" not in stamped
    assert _target_hash(net_vault, anchored) == anchored_hash  # the stamp is not scope
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
    assert _target_hash(net_vault, line_only) == line_hash  # the stamp is not scope
    _mutate_marker(net_vault, line_only, "2026-08-16", clear=True)
    assert note.read_bytes() == original
    assert _target_hash(net_vault, line_only) == line_hash


def test_mutate_marker_stamps_only_the_first_of_two_matching_lines(net_vault):
    """`_rewrite_marker_lines`'s own `first_only=True` is a real argument
    `_mutate_marker` must pass, not a stray `False`/`None`: two lines that
    both match the same claim anchor (an unusual note, but the rewriter
    itself does not police uniqueness) must only have the first stamped —
    `first_only`'s own `break` would otherwise stamp both."""
    note = net_vault / "projects" / "brief" / "duplicate-anchor.md"
    original = b"- (quote) first [@missing] ^c-1\n- (quote) second [@missing] ^c-1\n"
    note.write_bytes(original)
    outcome = _outcome(
        "citation-key",
        "missing",
        Result.UNMATCHED,
        "mismatch — citation key not in bibliography",
        note_path="projects/brief/duplicate-anchor.md",
        claims=[{"claim_id": "c-1"}],
    )
    _mutate_marker(net_vault, outcome, "2026-08-16")
    lines = note.read_bytes().splitlines()
    assert b"[failed-verification:: citation-key/2026-08-16]" in lines[0]
    assert b"[failed-verification:: citation-key/2026-08-16]" not in lines[1]


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
    assert _target_hash(net_vault, outcome) == before  # the stamp is not scope
    _mutate_marker(net_vault, outcome, "2026-08-16", clear=True)
    assert note.read_bytes() == original
    assert _target_hash(net_vault, outcome) == before


def test_marker_readers_accept_a_tab_before_the_marker(net_vault):
    """Row 55(a): `claims.ANCHOR_RE` needs no whitespace before `^`, so a
    tab-terminated claim `…\\t^id` is legal and the writer produces
    `…\\t[marker] ^id`. The readers accept `[ \\t]` before the marker; the
    writer stays, because normalising its output would move the claim's
    scope hash under the tool's own stamp."""
    from research_vault import markers

    note = net_vault / "projects" / "brief" / "tabbed.md"
    original = b"- (quote) tabbed [@missing]\t^c-1\n"
    note.write_bytes(original)
    outcome = _outcome(
        "quote",
        "missing#^c-1",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="projects/brief/tabbed.md",
        claim_id="c-1",
    )
    scope = _target_hash(net_vault, outcome)
    markers._mutate_marker(net_vault, outcome, "2026-09-17")
    assert (
        note.read_bytes()
        == b"- (quote) tabbed [@missing]\t[failed-verification:: quote/2026-09-17] ^c-1\n"
    )
    assert _target_hash(net_vault, outcome) == scope  # the stamp is not scope
    assert markers._without_own_marks(note.read_text()) == original.decode()
    assert markers.clear_marker_for(net_vault, "quote", "missing#^c-1")
    assert note.read_bytes() == original
    assert _target_hash(net_vault, outcome) == scope


def test_body_only_literature_ack_survives_verifier_event_envelope(net_vault):
    note = net_vault / "literature" / "bodyonly.md"
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

    assert note.read_text() == must_replace(
        original, " ^c-1", " [failed-verification:: quote/2026-08-17] ^c-1"
    )
    _mutate_marker(net_vault, outcome, "2026-08-16", clear=True)
    assert note.read_text() == original


def test_acknowledged_warning_stays_suppressed_across_effects(
    net_vault, monkeypatch, capsys
):
    source = net_vault / "literature" / "smith2020.md"
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

    # Identity, not position: the propagation lint's row now follows the
    # network outcomes, so the warning is no longer the last raw outcome.
    assert any(outcome is warning for outcome in first["outcomes"])
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

    code = cmd_verify(_verify_args(net_vault, offline=False, rw_csv=None))
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
    outside_link_snapshot = gitstate.snapshot_worktree(net_vault)
    assert (
        _target_hash(
            net_vault,
            _outcome(
                "append-only",
                "projects/brief/outside-link.md",
                Result.UNMATCHED,
                "drift",
            ),
            candidate_snapshot=outside_link_snapshot,
        )
        is None
    )
    citation_key_link = net_vault / "literature" / "escaped.md"
    citation_key_link.symlink_to(outside)
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
    directory_snapshot = gitstate.snapshot_worktree(net_vault)
    first = _target_hash(
        net_vault, directory_outcome, candidate_snapshot=directory_snapshot
    )
    first_target.write_text("changing outside content stays invisible\n")
    directory_snapshot = gitstate.snapshot_worktree(net_vault)
    assert (
        _target_hash(
            net_vault, directory_outcome, candidate_snapshot=directory_snapshot
        )
        == first
    )
    link.unlink()
    link.symlink_to(second_target)
    directory_snapshot = gitstate.snapshot_worktree(net_vault)
    assert (
        _target_hash(
            net_vault, directory_outcome, candidate_snapshot=directory_snapshot
        )
        != first
    )


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


def test_inbox_lists_oldest_first(net_vault, capsys):
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


def test_warn_dedup_collapses_the_re_file_and_keeps_a_competing_notice(
    net_vault, monkeypatch
):
    """#22: the old `== 1` held on a seeded record alone (network off, no
    rw_csv: nothing minted). The dedup key is (check, target, kind, result,
    target_hash, notice_class, notice_type, notice_date): a fresh correction
    filed twice reads one entry; a second run re-filing it (the re-file path)
    still reads one; a correction with another notice date is a new record."""
    warning = {"type": "correction", "notice_date": "2026-01-01"}
    outcome = _outcome(
        "update-notice", "smith2020", Result.MATCHED, "matched", warn_notices=[warning]
    )
    _isolate_network_verify(monkeypatch, [outcome])

    def open_corrections():
        return [
            e
            for e in inbox.open_entries(net_vault)
            if e.reason == "warn-notice — correction"
        ]

    run_verify(net_vault, network=True)
    (first,) = open_corrections()
    run_verify(net_vault, network=True)  # the re-file path: same key, deduplicated
    assert [e.id for e in open_corrections()] == [first.id]
    outcome.extra["warn_notices"] = [
        {"type": "correction", "notice_date": "2026-02-02"}
    ]
    run_verify(
        net_vault, network=True
    )  # a competing notice under a new date is not a duplicate
    assert len(open_corrections()) == 2


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
    monkeypatch.setattr("research_vault.lifecycle.lint_lifecycle", lambda *_args: [])


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
        cmd_verify(_verify_args(net_vault, offline=False, rw_csv=None, surface="audit"))
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
            _verify_args(net_vault, offline=False, rw_csv=None, surface="publish")
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
    assert blocker.target_hash == warning.target_hash
    assert (
        events.trust_tier((net_vault / "literature" / "smith2020.md").read_text())
        == "unverified"
    )

    inbox.append_ack(
        net_vault,
        blocker.id,
        "manual — reviewed retraction",
        "human:test",
        blocker.target_hash,
    )
    assert cmd_verify(_verify_args(net_vault, offline=False, rw_csv=None)) == 0
    assert "retracted — retraction" not in capsys.readouterr().out
    # The whole-set pin: the fixture's two structural SKIPPED rows (no applied
    # propagation plan, no source ledger) and nothing else — no update-notice
    # survives the ack.
    assert sorted(
        (entry.check, entry.result, entry.reason)
        for entry in inbox.open_entries(net_vault)
    ) == [
        ("captured-set", "SKIPPED", "no-identifier — no source ledger"),
        ("propagation", "SKIPPED", "no-identifier — no applied propagation plan"),
    ]


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
            "note_path": RepoPath(b"literature/smith2020.md"),
            "claim_id": "c-11111111",
            "target": "managed-region",
        },
    )


@pytest.mark.parametrize(
    "reverse", [False, True], ids=["primary-first", "primary-last"]
)
@pytest.mark.parametrize("check", ["update-notice", "quote"])
def test_unwitnessed_note_target_hashes_are_candidate_bound_before_projection(
    net_vault, monkeypatch, check, reverse
):
    # A note capture never wrote takes the `_note_bytes` fallback, which
    # ignores projection's own writes — the body marker and the frontmatter
    # failure row — as a witness would. Committed so
    # `lint_evidence_layer`'s base and candidate agree on the missing
    # managed-sha256 — this test exercises candidate-bound hashing, not the
    # machine-owned-frontmatter guard.
    source = net_vault / "literature" / "smith2020.md"
    source.write_text(_without_witness(source.read_text()))
    subprocess.run(["git", "add", "-A"], cwd=net_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "drop managed-sha256"], cwd=net_vault, check=True
    )
    primary = _projecting_failure(check)
    companion = _outcome(
        "citation-key", "smith2020", Result.UNREACHABLE, "outage — citation key"
    )
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

    assert projected_hash == candidate_hash  # projection is not scope
    assert hashes[id(primary)] == candidate_hash
    assert finding.target_hash == candidate_hash


@pytest.mark.parametrize("check", ["update-notice", "quote"])
def test_unwitnessed_note_acknowledgment_survives_projections_own_writes(
    net_vault, monkeypatch, check
):
    # A note capture never wrote takes the `_note_bytes` fallback, which
    # ignores projection's own writes — the body marker and the frontmatter
    # failure row — as a witness would, so the ack scoped to the candidate
    # hash still holds once projection has written. Committed so
    # `lint_evidence_layer`'s base and candidate agree on the missing
    # managed-sha256 — this test exercises candidate-bound hashing, not the
    # machine-owned-frontmatter guard.
    source = net_vault / "literature" / "smith2020.md"
    source.write_text(_without_witness(source.read_text()))
    subprocess.run(["git", "add", "-A"], cwd=net_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "drop managed-sha256"], cwd=net_vault, check=True
    )
    primary = _projecting_failure(check)
    companion = _outcome(
        "citation-key", "smith2020", Result.UNREACHABLE, "outage — citation key"
    )
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
    assert _target_hash(net_vault, primary) == candidate_hash  # projection is not scope
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
    source = net_vault / "literature" / "smith2020.md"
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
                "note_path": RepoPath(b"literature/smith2020.md"),
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
    assert "UNMATCHED citation-key path-bytes:system/bibliography.json" in output
    assert "schema-violation" in output
    assert "Traceback" not in output


def test_real_verify_cli_reports_undecodable_bibliography_unreachable(
    net_vault, capsys
):
    (net_vault / "system" / "bibliography.json").write_bytes(b"\xff")

    code = main(["verify", "--vault", str(net_vault), "--offline"])
    output = capsys.readouterr().out

    assert code == 0
    assert "UNREACHABLE citation-key path-bytes:system/bibliography.json" in output


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
        cmd_verify(_verify_args(net_vault, offline=False, rw_csv=None, surface=surface))
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
    candidate_snapshot = gitstate.snapshot_worktree(net_vault)

    target_hash = _target_hash(
        net_vault,
        outcome,
        base_snapshot=snapshots.base,
        candidate_snapshot=candidate_snapshot,
    )

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
        current_hash=_target_hash(
            net_vault,
            outcome,
            base_snapshot=snapshots.base,
            candidate_snapshot=candidate_snapshot,
        ),
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
    # Crossref is authoritative and re-issues deposits within the month; the
    # retraction's month is the stable fact, the day is whatever precision
    # the deposit carries (Task 19: partial dates keep their precision).
    assert re.fullmatch(r"2010-02(-\d{2})?", outcome.extra["notice_date"])
    assert outcome.reason == "retracted — retraction"
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
            {
                "citation-key",
                "evidence-layer",
                "okf-frontmatter",
                "okf-structure",
                "tree",
                "propagation",
                "captured-set",
            }
        ),
        "publish": frozenset(
            {
                "citation-key",
                "evidence-layer",
                "quote",
                "update-notice",
                "okf-frontmatter",
                "okf-structure",
                "tree",
                "propagation",
                "captured-set",
            }
        ),
    }


def test_literature_note_add_is_collected_and_projected_as_evidence_finding(
    fixture_vault,
):
    added = fixture_vault / "literature" / "added.md"
    # A hand-written note: no writer attestation (the fixture's machine-class
    # `generated` is replaced with a human actor), so the write itself is the
    # drift this test collects and projects. A plain byte-for-byte copy would
    # no longer do: its machine-class `generated` is now accepted as attested
    # by the write leg itself (evidence-layer's write legs, Part B Task 2b).
    added.write_text(
        must_replace(
            must_replace(
                (fixture_vault / "literature" / "smith2020.md").read_text(),
                'citationKey: "smith2020"',
                'citationKey: "added"',
            ),
            'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}',
            'generated: {by: "human:eran", at: "2026-08-16T09:00:00Z"}',
        )
    )

    report, effective, hashes, _warnings = verify_state(
        fixture_vault, network=False, detection_date="2026-08-16"
    )

    finding = next(
        outcome
        for outcome in report["outcomes"]
        if outcome.check == "evidence-layer"
        and outcome.target == "path-bytes:literature/added.md"
        and outcome.reason == "drift — literature note added without writer attestation"
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
    # The pipeline files every genuine non-MATCHED row, SKIPPED included
    # (lifecycle's decision-26 row is filed the same way, measured 2026-09-08),
    # so the two lints that report "this vault holds nothing of mine yet" — the
    # propagation residue lint with no applied plan, and the captured-set lint
    # with no source ledger — move the queue and nothing else; no synthetic row
    # reaches it.
    after = _vault_bytes(tmp_vault)
    moved = {key for key in before | after if before.get(key) != after.get(key)}
    assert moved == {b"inbox/review-queue.md"}
    filed = {entry.check for entry in inbox.load(tmp_vault)}
    assert filed == {"propagation", "captured-set"}
    assert filed.isdisjoint({item.check for item in synthetic})


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
    candidate_snapshot = gitstate.snapshot_worktree(fixture_vault)

    assert (
        _target_hash(fixture_vault, typed, candidate_snapshot=candidate_snapshot)
        is not None
    )
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


def test_ack_scope_hash_is_the_notes_managed_sha256(fixture_vault):
    from research_vault import frontmatter, verify

    digest = verify._citation_key_hash(fixture_vault, "smith2020")
    data, _ = frontmatter.parse(
        (fixture_vault / "literature" / "smith2020.md").read_text()
    )
    assert (
        digest == data["managed-sha256"]
    )  # open point 07: the body hash capture writes, never a hash passed by hand


def test_ack_scope_is_derived_and_lapses_when_the_body_moves(fixture_vault, capsys):
    import research_vault.__main__ as cli
    from research_vault import inbox

    target = "fabricated2020#^c-77777777"
    expected = hashlib.sha256(
        b"citation-key\x00" + target.encode() + b"\x00" + b"a" * 64
    ).hexdigest()
    assert inbox.scope_id("citation-key", target, "a" * 64) == expected
    assert inbox.scope_id("citation-key", target, "b" * 64) != expected
    assert (
        cli.main(
            [
                "finding",
                "citation-key",
                target,
                "UNMATCHED",
                "mismatch — not in bibliography",
                "--vault",
                str(fixture_vault),
                "--date",
                "2026-09-07",
                "--target-hash",
                "a" * 64,
            ]
        )
        == 0
    )
    finding_id = capsys.readouterr().out.strip()
    assert (
        cli.main(
            [
                "ack",
                finding_id,
                "--vault",
                str(fixture_vault),
                "--reason",
                "manual — known",
                "--actor",
                "human:eran",
            ]
        )
        == 0
    )
    assert inbox.is_acknowledged(fixture_vault, "citation-key", target, "a" * 64)
    assert not inbox.is_acknowledged(
        fixture_vault, "citation-key", target, "b" * 64
    )  # the body moved: the finding re-fires


def test_as_of_pins_the_instant_a_check_compares_against(fixture_vault, capsys):
    import research_vault.__main__ as cli
    from research_vault import inbox

    assert (
        cli.main(
            [
                "finding",
                "citation-key",
                "fabricated2020#^c-77777777",
                "UNMATCHED",
                "mismatch — not in bibliography",
                "--vault",
                str(fixture_vault),
                "--date",
                "2026-09-07",
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert inbox.summary(fixture_vault, as_of="2026-09-10")["oldest_age_days"] == 3
    assert (
        cli.main(["inbox", "--vault", str(fixture_vault), "--as-of", "2026-09-10"]) == 0
    )
    assert '"oldest_age_days": 3' in capsys.readouterr().out
    assert (
        cli.main(
            [
                "verify",
                "--vault",
                str(fixture_vault),
                "--offline",
                "--as-of",
                "2026-13-01",
            ]
        )
        == 2
    )
    assert "--as-of must be YYYY-MM-DD" in capsys.readouterr().err


def test_ack_clears_the_failed_verification_marker(fixture_vault, capsys):
    import research_vault.__main__ as cli

    draft = fixture_vault / "projects" / "brief" / "draft.md"
    text = must_replace(
        draft.read_text(),
        "- (inference) This will replicate [@fabricated2020] ^c-77777777",
        "- (inference) This will replicate [@fabricated2020] [failed-verification:: citation-key/2026-09-07] ^c-77777777",
    )
    draft.write_text(text)
    assert (
        cli.main(
            [
                "finding",
                "citation-key",
                "fabricated2020#^c-77777777",
                "UNMATCHED",
                "mismatch — not in bibliography",
                "--vault",
                str(fixture_vault),
                "--date",
                "2026-09-07",
            ]
        )
        == 0
    )
    finding_id = capsys.readouterr().out.strip()
    assert (
        cli.main(
            [
                "ack",
                finding_id,
                "--vault",
                str(fixture_vault),
                "--reason",
                "manual — known",
                "--actor",
                "human:eran",
            ]
        )
        == 0
    )
    assert "[failed-verification::" not in draft.read_text()


def test_clear_marker_for_clears_a_file_target_and_refuses_other_shapes(net_vault):
    """The `path-bytes:` shape names the file itself; a bare identifier of any
    check but `citation-key` is no shape at all and clears nothing."""
    from research_vault.markers import clear_marker_for

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
    assert "[failed-verification:: quote/2026-08-16]" in draft.read_text()

    assert clear_marker_for(net_vault, "quote", "smith2020") is False
    assert (
        clear_marker_for(
            net_vault, "citation-key", "path-bytes:projects/brief/draft.md"
        )
        is False
    )  # another check's marker is not this acknowledgment's to clear
    assert "[failed-verification:: quote/2026-08-16]" in draft.read_text()
    assert clear_marker_for(net_vault, "quote", "path-bytes:projects/brief/draft.md")
    assert "[failed-verification::" not in draft.read_text()
    assert draft.read_text().endswith("[@fabricated2020] ^c-77777777\n")


def test_ack_clears_the_marker_on_a_claim_citing_a_captured_note(fixture_vault, capsys):
    """A `#^` target whose literature note exists: the marker sits at the
    claim's origin in the project note (where `_mutate_marker` wrote it),
    never in the machine-written note, and that is where the ack clears it."""
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        must_replace(
            draft.read_text(),
            "- (quote) [@smith2020, p. 12] ^c-66666666",
            "- (quote) [@smith2020, p. 12] [failed-verification:: quote/2026-09-07] ^c-66666666",
        )
    )
    assert (fixture_vault / "literature" / "smith2020.md").is_file()
    assert (
        main(
            [
                "finding",
                "quote",
                "smith2020#^c-66666666",
                "UNMATCHED",
                "mismatch — quote",
                "--vault",
                str(fixture_vault),
                "--date",
                "2026-09-07",
            ]
        )
        == 0
    )
    finding_id = capsys.readouterr().out.strip()
    assert (
        main(
            [
                "ack",
                finding_id,
                "--vault",
                str(fixture_vault),
                "--reason",
                "manual — known",
                "--actor",
                "human:eran",
            ]
        )
        == 0
    )
    captured = capsys.readouterr()
    # stdout is the ack's id alone (`id=$(… ack …)` must take the right line,
    # row 53); what the ack stood down is said on stderr.
    assert captured.out == f"ack/{finding_id}\n"
    assert "cleared [failed-verification:: quote]" in captured.err
    assert "- (quote) [@smith2020, p. 12] ^c-66666666\n" in draft.read_text()
    assert "[failed-verification::" not in draft.read_text()


def test_ack_on_a_bare_key_citation_finding_clears_every_line_citing_that_key(
    fixture_vault, capsys
):
    """verify files a `citation-key` finding on the bare key, with the claim
    lines only in the outcome's extra; the citation is the filter, and the
    citation regex keeps `smith2020` from touching `smith2020a`."""
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        must_replace(
            draft.read_text(),
            "- (quote) [@smith2020, p. 12] ^c-66666666",
            "- (quote) [@smith2020, p. 12] "
            "[failed-verification:: citation-key/2026-09-07] ^c-66666666",
        )
    )
    other = fixture_vault / "projects" / "brief" / "other.md"
    other.write_text(
        "- (inference) unanchored [@smith2020] "
        "[failed-verification:: citation-key/2026-09-07]\n"
        "- (inference) longer key [@smith2020a] "
        "[failed-verification:: citation-key/2026-09-07] ^c-99999999\n"
    )
    assert (
        main(
            [
                "finding",
                "citation-key",
                "smith2020",
                "UNMATCHED",
                "not-captured — cited citation key has no literature note",
                "--vault",
                str(fixture_vault),
                "--date",
                "2026-09-07",
            ]
        )
        == 0
    )
    finding_id = capsys.readouterr().out.strip()
    assert (
        main(
            [
                "ack",
                finding_id,
                "--vault",
                str(fixture_vault),
                "--reason",
                "manual — known",
                "--actor",
                "human:eran",
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert "- (quote) [@smith2020, p. 12] ^c-66666666\n" in draft.read_text()
    assert "[failed-verification::" not in draft.read_text()
    assert other.read_text() == (
        "- (inference) unanchored [@smith2020]\n"
        "- (inference) longer key [@smith2020a] "
        "[failed-verification:: citation-key/2026-09-07] ^c-99999999\n"
    )


def test_clear_marker_for_never_writes_under_wiki(fixture_vault):
    """The compiled layer is the tool's write scope: a marker there was never
    verify's, and an ack leaves it alone, mirroring `_mutate_marker`'s guard."""
    from research_vault.markers import clear_marker_for

    concept = fixture_vault / "wiki" / "concepts" / "mortality-trends.md"
    # Terminal, the placement a file-target clear would otherwise match.
    marked = must_replace(
        concept.read_text(),
        "^c-55555555\n",
        "^c-55555555 [failed-verification:: quote/2026-09-07]\n",
    )
    concept.write_text(marked)
    assert (
        clear_marker_for(
            fixture_vault, "quote", "path-bytes:wiki/concepts/mortality-trends.md"
        )
        is False
    )
    assert concept.read_text() == marked


def test_ack_clears_a_file_target_from_a_relative_vault(
    fixture_vault, monkeypatch, capsys
):
    """`--vault .` is a shipped form; the `path-bytes:` candidate is absolute
    while the root a caller hands `cmd_ack` need not be, and the two must
    still meet in the `wiki/` guard."""
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        must_replace(
            draft.read_text(),
            "^c-77777777\n",
            "^c-77777777 [failed-verification:: quote/2026-09-07]\n",
        )
    )
    finding = inbox.append_entry(
        fixture_vault,
        "quote",
        "path-bytes:projects/brief/draft.md",
        Result.UNMATCHED,
        "schema-violation — quote claim has no anchor",
        date="2026-09-07",
        target_kind="repo-path",
    )
    monkeypatch.chdir(fixture_vault)
    assert (
        main(
            [
                "ack",
                finding.id,
                "--vault",
                ".",
                "--reason",
                "manual — known",
                "--actor",
                "human:eran",
            ]
        )
        == 0
    )
    out = capsys.readouterr().out.splitlines()
    assert out[-1] == f"ack/{finding.id}"
    assert "[failed-verification::" not in draft.read_text()
    assert len([e for e in inbox.load(fixture_vault) if e.ack_of == finding.id]) == 1


def test_ack_clears_the_marker_on_a_hand_authored_literature_note(
    fixture_vault, capsys
):
    """`_plan_state` scans `literature/` too, so a hand-authored note there
    that carries claim lines receives markers; the clear reaches them. A
    capture-rendered note carries no claim lines and matches nothing."""
    note = fixture_vault / "literature" / "smith2020.md"
    note.write_text(
        must_replace(
            note.read_text(),
            "- (quote) [@smith2020, p. 12] ^c-11111111",
            "- (quote) [@smith2020, p. 12] [failed-verification:: quote/2026-09-07] ^c-11111111",
        )
    )
    assert (
        main(
            [
                "finding",
                "quote",
                "smith2020#^c-11111111",
                "UNMATCHED",
                "mismatch — quote",
                "--vault",
                str(fixture_vault),
                "--date",
                "2026-09-07",
            ]
        )
        == 0
    )
    finding_id = capsys.readouterr().out.strip()
    assert (
        main(
            [
                "ack",
                finding_id,
                "--vault",
                str(fixture_vault),
                "--reason",
                "manual — known",
                "--actor",
                "human:eran",
            ]
        )
        == 0
    )
    assert "- (quote) [@smith2020, p. 12] ^c-11111111\n" in note.read_text()
    assert "[failed-verification::" not in note.read_text()


def test_every_scope_leg_ignores_verifys_own_marks():
    """An ack scope hashes what the person wrote, never the tool's marks: the
    anchored-claim, origin-note and repo-path legs all read the same bytes
    before a stamp, after it, and after the clear (open point 07)."""
    from research_vault.verify import _claim_bytes_from_text

    plain = (
        '---\ntype: "project"\n---\n'
        "- (quote) anchored [@k]   ^c-1\n"
        "- (inference) unanchored [@k]\n"
    )
    stamped = must_replace(
        plain, "   ^c-1", "   [failed-verification:: quote/2026-09-07] ^c-1"
    )
    stamped = must_replace(
        stamped, "[@k]\n", "[@k] [failed-verification:: citation-key/2026-09-07]\n"
    )
    assert _claim_bytes_from_text(stamped, "c-1") == _claim_bytes_from_text(
        plain, "c-1"
    )
    assert _note_bytes(stamped.encode()) == _note_bytes(plain.encode())


def test_ack_scope_survives_verifys_own_stamp_and_clear(net_vault, capsys):
    """The orphaning case, closed by mechanism: a row filed from a stamped
    state carries the same scope as one filed before the stamp, so acking it
    holds through the ack's own clear and through the next run."""
    draft = net_vault / "projects" / "brief" / "draft.md"
    run_verify(net_vault, network=False, detection_date="2026-08-16")
    assert "[failed-verification:: citation-key/2026-08-16]" in draft.read_text()
    run_verify(net_vault, network=False, detection_date="2026-08-16")
    rows = [
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.check == "citation-key" and entry.target == "fabricated2020"
    ]
    assert len(rows) == 1  # the stamp did not move the scope: no second row
    assert (
        main(
            [
                "ack",
                rows[0].id,
                "--vault",
                str(net_vault),
                "--reason",
                "manual — known",
                "--actor",
                "human:eran",
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert "[failed-verification:: citation-key/" not in draft.read_text()
    run_verify(net_vault, network=False, detection_date="2026-08-16")
    assert "[failed-verification:: citation-key/" not in draft.read_text()
    assert not [
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.check == "citation-key" and entry.target == "fabricated2020"
    ]


@pytest.mark.parametrize("check", ["update-notice", "quote"])
def test_ack_on_an_unwitnessed_note_survives_the_failure_row(
    net_vault, monkeypatch, capsys, check
):
    """For a note without a `managed-sha256`, the scope hash must not move
    with the frontmatter `failed-verification` row the projection writes, or
    an ack between two runs is orphaned — a second row, and the outcome
    effective again. The scope ignores the tool's own record as it ignores
    `verified` events; the record stays."""
    source = net_vault / "literature" / "smith2020.md"
    source.write_text(_without_witness(source.read_text()))
    subprocess.run(["git", "add", "-A"], cwd=net_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "drop managed-sha256"], cwd=net_vault, check=True
    )
    primary = _projecting_failure(check)
    _isolate_network_verify(monkeypatch, [primary])

    _report, effective, _hashes, _warnings = verify_state(
        net_vault, network=True, detection_date="2026-08-16"
    )
    assert primary in effective
    assert events.current_failures(source.read_text())  # the record is written
    rows = [
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.check == check and entry.target == primary.target
    ]
    assert len(rows) == 1
    assert (
        main(
            [
                "ack",
                rows[0].id,
                "--vault",
                str(net_vault),
                "--reason",
                "manual — checked",
                "--actor",
                "human:test",
            ]
        )
        == 0
    )
    capsys.readouterr()

    _report, effective, _hashes, _warnings = verify_state(
        net_vault, network=True, detection_date="2026-08-17"
    )

    assert primary not in effective
    assert not [
        entry
        for entry in inbox.open_entries(net_vault)
        if entry.check == check and entry.target == primary.target
    ]
    assert events.current_failures(source.read_text())  # ack leaves it


# --- The repo-path hash planes -------------------------------------------------


def _repo_path_outcome(relative):
    """A non-append-only repo-path target: routes to `_repo_path_hash`, not
    to the append-only basis."""
    return checks.Outcome(
        "okf-frontmatter",
        RepoPath(os.fsencode(relative)),
        Result.UNMATCHED,
        "schema-violation — frontmatter",
    )


def test_a_repo_path_target_requires_a_candidate_snapshot(net_vault):
    """The worktree leg is gone: the one production caller always passes the
    candidate snapshot, and reading the worktree instead would let a
    concurrent edit leak into an identity the transaction already fixed."""
    with pytest.raises(TypeError, match="candidate_snapshot"):
        _target_hash(net_vault, _repo_path_outcome("literature/smith2020.md"))
    snapshot = gitstate.snapshot_worktree(net_vault)
    assert (
        _target_hash(
            net_vault,
            _repo_path_outcome("literature/smith2020.md"),
            candidate_snapshot=snapshot,
        )
        is not None
    )


# --- hash-basis helpers pinned against mutation survivors ---------------------


def _image(raw, kind, data=None, mode=0o100644):
    return gitstate.FileImage(raw, kind, mode if kind == "file" else 0o40000, data)


def test_snapshot_directory_bytes_takes_only_the_prefix_children_that_carry_bytes():
    from research_vault import verify

    snapshot = gitstate.Snapshot(
        {
            b"inbox/x.md": _image(b"inbox/x.md", "file", b"elsewhere"),
            b"literature": _image(b"literature", "directory"),
            b"literature/a-link": _image(b"literature/a-link", "symlink", b"t"),
            b"literature/b.md": _image(
                b"literature/b.md",
                "file",
                b'---\nverified:\n  - {by: "bot", at: "2026-08-16"}\n---\nbody\n',
            ),
            b"literature/c.txt": _image(b"literature/c.txt", "file", b"C"),
            b"literature/sub": _image(b"literature/sub", "directory"),
            b"literatureX.md": _image(b"literatureX.md", "file", b"no"),
        }
    )
    assert verify._snapshot_directory_bytes(snapshot, b"literature") == b"\0".join(
        [b"a-link", b"symlink", b"t", b"b.md", b"body\n", b"c.txt", b"C"]
    )


def test_append_only_basis_is_the_base_file_bytes_or_nothing(net_vault):
    from research_vault import verify

    raw = b"inbox/review-queue.md"
    with_file = gitstate.Snapshot({raw: _image(raw, "file", b"queued")})
    as_directory = gitstate.Snapshot({raw: _image(raw, "directory")})
    assert verify._append_only_basis(net_vault, raw, with_file) == b"queued"
    assert verify._append_only_basis(net_vault, raw, as_directory) == b""
    assert verify._append_only_basis(net_vault, raw, gitstate.Snapshot({})) == b""


def test_snapshot_path_hash_takes_the_candidate_file_directory_or_base_bytes(
    net_vault,
):
    """A candidate file hashes its (note-normalised) bytes, a candidate
    directory its listing, an absent path the base file's bytes; an
    append-only target its base basis regardless of the candidate."""
    from research_vault import verify

    note = b'---\nverified:\n  - {by: "bot", at: "2026-08-16"}\n---\nbody\n'
    candidate = gitstate.Snapshot(
        {
            b"literature": _image(b"literature", "directory"),
            b"literature/a.md": _image(b"literature/a.md", "file", note),
            b"inbox/review-queue.md": _image(
                b"inbox/review-queue.md", "file", b"grown"
            ),
        }
    )
    base = gitstate.Snapshot(
        {
            b"literature/gone.md": _image(b"literature/gone.md", "file", note),
            b"inbox/review-queue.md": _image(
                b"inbox/review-queue.md", "file", b"basis"
            ),
        }
    )

    def digest(data):
        return hashlib.sha256(data).hexdigest()[:16]

    plain = _repo_path_outcome("literature/a.md")
    assert verify._snapshot_path_hash(
        net_vault, plain, b"literature/a.md", base, candidate
    ) == digest(b"body\n")
    assert verify._snapshot_path_hash(
        net_vault, plain, b"literature", base, candidate
    ) == digest(b"\0".join([b"a.md", b"body\n"]))
    assert verify._snapshot_path_hash(
        net_vault, plain, b"literature/gone.md", base, candidate
    ) == digest(b"body\n")
    append = _outcome(
        "append-only", "inbox/review-queue.md", Result.UNMATCHED, "drift — inbox"
    )
    assert verify._snapshot_path_hash(
        net_vault, append, b"inbox/review-queue.md", base, candidate
    ) == digest(b"basis")


def test_safe_relative_needs_the_repo_path_kind_and_a_string(net_vault):
    encoded = encode_repo_path(b"literature/smith2020.md")
    assert _safe_relative(net_vault, encoded, "identifier") is None
    assert _safe_relative(net_vault, b"literature/smith2020.md", "repo-path") is None
    assert _safe_relative(net_vault, encoded, "repo-path") == (
        net_vault / "literature" / "smith2020.md"
    )


def test_projection_identity_needs_an_anchored_quote_target_and_a_named_comparison():
    from research_vault import verify

    quote = _outcome("quote", "smith2020#^c-1", Result.UNMATCHED, "fuzzy-quote — x")
    assert verify._projection_identity(quote) == (
        "smith2020",
        "quote:smith2020#^c-1:managed-region",
    )
    unanchored = _outcome("quote", "smith2020", Result.UNMATCHED, "fuzzy-quote — x")
    assert verify._projection_identity(unanchored) is None
    blank = checks.Outcome(
        "quote", "smith2020#^c-1", Result.UNMATCHED, "fuzzy-quote — x", {"target": ""}
    )
    assert verify._projection_identity(blank) is None
    other = _outcome("doi", "smith2020#^c-1", Result.UNMATCHED, "mismatch — x")
    assert verify._projection_identity(other) is None


def test_origins_need_a_string_note_path_and_a_claim_id_or_line_number():

    with_claim = _outcome(
        "quote",
        "smith2020#^c-1",
        Result.UNMATCHED,
        "fuzzy-quote — x",
        note_path="projects/brief/draft.md",
        claim_id="c-1",
    )
    assert list(markers._origins(with_claim)) == [
        (encode_repo_path(b"projects/brief/draft.md"), "c-1", None)
    ]
    without_path = _outcome(
        "quote", "smith2020#^c-1", Result.UNMATCHED, "fuzzy-quote — x", claim_id="c-1"
    )
    assert list(markers._origins(without_path)) == []
    without_origin = _outcome(
        "quote",
        "smith2020#^c-1",
        Result.UNMATCHED,
        "fuzzy-quote — x",
        note_path="projects/brief/draft.md",
    )
    assert list(markers._origins(without_origin)) == []


def test_snapshot_path_hash_of_a_note_absent_from_the_candidate_falls_back_to_base(
    net_vault,
):
    """A candidate snapshot IS the vault for this hash; a path the candidate
    lacks falls back to the base image so a deletion keeps a stable hash."""
    source = net_vault / "literature" / "smith2020.md"
    before = _note_bytes(source.read_bytes())
    base = gitstate.snapshot_worktree(net_vault)
    source.unlink()
    candidate = gitstate.snapshot_worktree(net_vault)
    outcome = _repo_path_outcome("literature/smith2020.md")
    assert (
        _target_hash(
            net_vault, outcome, base_snapshot=base, candidate_snapshot=candidate
        )
        == hashlib.sha256(before).hexdigest()[:16]
    )
    assert (
        _target_hash(net_vault, outcome, candidate_snapshot=candidate)
        == hashlib.sha256(b"").hexdigest()[:16]
    )


def test_a_nested_note_under_literature_is_not_a_literature_note_anywhere(net_vault):
    """One rule at every reader of `literature/`:
    the captured set is `literature/*.md` (decision 08), capture writes only
    that shape (`note_path` refuses `/`), so a nested `.md` is not a
    literature note for the captured set, the linter, `--all`, the marker
    clear, the claim scan or the evidence layer. Two readers recursed: a
    nested note's claims were stamped by `_plan_state` and unreachable by
    `clear_marker_for`, and the evidence layer judged a witness capture could
    never have written."""
    from research_vault import capture, captured, lifecycle, lints

    nested = net_vault / "literature" / "older" / "nested2020.md"
    nested.parent.mkdir()
    nested.write_text(
        '---\ntype: "literature"\ncitationKey: "nested2020"\n'
        'zotero-server-id: "6LpvURP2E933"\nzotero-item-key: "NESTED01"\n'
        "zotero-item-version: 1\nattachments:\nfulltext:\n---\n"
        "- (quote) [@ghost2020, p. 1] ^c-99999999\n"
    )
    raw = os.fsencode("literature/older/nested2020.md")
    snapshot = gitstate.snapshot_worktree(net_vault)
    assert raw in snapshot.images
    assert raw not in lints._literature_files(snapshot)
    assert not [
        o for o in lints.lint_evidence_layer(snapshot, snapshot) if "older" in o.target
    ]
    assert "nested2020" not in captured.captured_set(net_vault)
    assert "nested2020" not in {
        p.citation_key for _, p in lifecycle._provenances(net_vault)
    }
    assert "nested2020" not in capture._every_note(net_vault)[0]
    assert nested not in markers._claim_notes(net_vault)
    _report, effective, _hashes, _warnings = verify_state(net_vault, network=False)
    # `structure.check_note_frontmatter` walks the whole vault and still types
    # the file by its folder (OKF rule 2, not a literature/ reader): that row
    # is the one thing verify says about it.
    assert sorted(
        (o.check, o.result, o.reason)
        for o in effective
        if "older" in str(o.target)
        or "older" in str(o.extra.get("note_path", ""))
        or (o.check == "tree" and "older" in o.reason)
    ) == [
        ("okf-frontmatter", Result.MATCHED, "matched"),
        (
            "tree",
            Result.UNMATCHED,
            "schema-violation — literature/ is flat: literature/older/",
        ),
    ]
    assert "[failed-verification::" not in nested.read_text()


def test_markers_is_its_own_module_and_verify_imports_from_it():
    """The cut: the marker writer and clearer, the note readers, the origin
    walk and the path guard live in `markers.py`; `verify` imports them and
    `markers` never imports `verify` (no cycle)."""
    from research_vault import markers

    for name in (
        "_mutate_marker",
        "clear_marker_for",
        "_rewrite_marker_lines",
        "_origins",
        "_safe_relative",
        "_read_note_text",
        "_write_note_text",
        "_without_own_marks",
        "_split_line_ending",
        "_terminal_anchor_match",
        "_terminal_marker_pattern",
        "_claim_notes",
        "_cites",
    ):
        assert callable(getattr(markers, name)), name
    assert verify.CLOSING_CHECKS  # stays in verify
    source = Path(markers.__file__).read_text(encoding="utf-8")
    assert "from .verify" not in source
    assert "import verify" not in source
    assert not hasattr(markers, "CLOSING_CHECKS")


def test_rewrite_marker_lines_is_one_core_for_stamp_and_clear(net_vault):
    """Row 54: `_mutate_marker` (first matching line, then stop) and
    `clear_marker_for` (every matching line) share one rewriter. Two claim
    lines carry the same anchor: the stamp lands on the first only; the clear
    removes both."""
    from research_vault import markers

    note = net_vault / "projects" / "brief" / "twice.md"
    note.write_text(
        "- (quote) first [@smith2020, p. 1] ^c-1\n- (quote) second [@smith2020, p. 2] ^c-1\n"
    )

    def matcher(_index, content):
        anchor = markers._terminal_anchor_match(content, "c-1")
        return (True, "c-1") if anchor else (False, None)

    assert markers._rewrite_marker_lines(
        note, "quote", matcher, clear=False, first_only=True, date="2026-09-17"
    )
    assert note.read_text() == (
        "- (quote) first [@smith2020, p. 1] [failed-verification:: quote/2026-09-17] ^c-1\n"
        "- (quote) second [@smith2020, p. 2] ^c-1\n"
    )
    assert markers._rewrite_marker_lines(
        note, "quote", matcher, clear=False, first_only=False, date="2026-09-17"
    )
    assert note.read_text().count("[failed-verification:: quote/2026-09-17]") == 2
    assert markers._rewrite_marker_lines(
        note, "quote", matcher, clear=True, first_only=False
    )
    assert "[failed-verification" not in note.read_text()
    assert not markers._rewrite_marker_lines(
        note, "quote", matcher, clear=True, first_only=False
    )


def test_mutate_marker_never_writes_under_wiki_when_the_vault_is_dot(
    fixture_vault, monkeypatch
):
    """Row 55(b): the `wiki/` guard roots on `gitstate._root_bytes`, as
    `clear_marker_for` does, so `--vault .` (a relative root) still guards
    the compiled layer instead of raising on `relative_to`."""
    from research_vault import markers

    monkeypatch.chdir(fixture_vault)
    page = fixture_vault / "wiki" / "concepts" / "mortality-trends.md"
    before = page.read_bytes()
    outcome = _outcome(
        "quote",
        "smith2020#^c-1",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="wiki/concepts/mortality-trends.md",
        line_no=1,
    )
    markers._mutate_marker(".", outcome, "2026-09-17")
    assert page.read_bytes() == before


def test_marker_walk_skips_an_undecodable_note_and_continues(net_vault):
    from research_vault import markers

    bad = net_vault / "projects" / "brief" / "bad.md"
    bad.write_bytes(b"\xff\xfe- (quote) x [@missing] ^c-1\n")
    good = net_vault / "projects" / "brief" / "good.md"
    good.write_text("- (quote) y [@missing] ^c-1\n")
    for name in ("bad.md", "good.md"):
        markers._mutate_marker(
            net_vault,
            _outcome(
                "quote",
                "missing#^c-1",
                Result.UNMATCHED,
                "mismatch — x",
                note_path=f"projects/brief/{name}",
                claim_id="c-1",
            ),
            "2026-09-17",
        )
    assert bad.read_bytes() == b"\xff\xfe- (quote) x [@missing] ^c-1\n"
    assert "[failed-verification:: quote/2026-09-17]" in good.read_text()
    assert markers.clear_marker_for(net_vault, "quote", "missing#^c-1") is True
    assert "[failed-verification" not in good.read_text()
    assert bad.read_bytes() == b"\xff\xfe- (quote) x [@missing] ^c-1\n"


# --- the survivor triage: kills the spec located (pre-lane-2 §6.2) ------------


def test_identifier_hash_of_a_bare_bibliography_entry_is_its_sorted_canonical_json(
    net_vault,
):
    """An identifier with no note falls through to its bibliography entry:
    canonical JSON with sorted keys and no spaces, sixteen hex characters.
    The entry's keys are written out of order so `sort_keys=True` is load-
    bearing; the literal length kills the `[:17]` shape at every return."""
    path = net_vault / "system" / "bibliography.json"
    entries = json.loads(path.read_text())
    entry = {"title": "Admitted entry", "id": "noted-yet", "DOI": "10.1/z"}
    entries.append(entry)
    path.write_text(json.dumps(entries))
    outcome = _outcome("update-notice", "noted-yet", Result.UNMATCHED, "retracted — x")
    expected = hashlib.sha256(
        json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:16]
    assert _target_hash(net_vault, outcome) == expected
    assert len(expected) == 16


@pytest.mark.parametrize("plane", ["origin", "origin_image"])
def test_identifier_hash_of_a_witness_less_note_reads_the_note_through_its_origin(
    net_vault, plane
):
    """A note whose `managed-sha256` is absent is not identified by its
    witness (`_citation_key_hash` answers None) but by its bytes, through
    the origin path (no candidate snapshot) or the origin image (with one)."""
    source = net_vault / "literature" / "smith2020.md"
    text = source.read_text()
    witness_line = next(
        line for line in text.splitlines() if line.startswith("managed-sha256:")
    )
    source.write_text(must_replace(text, witness_line + "\n", ""))
    outcome = _outcome(
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "retracted — x",
        note_path="literature/smith2020.md",
    )
    expected = hashlib.sha256(_note_bytes(source.read_bytes())).hexdigest()[:16]
    if plane == "origin":
        assert _target_hash(net_vault, outcome) == expected
    else:
        snapshot = gitstate.snapshot_worktree(net_vault)
        assert _target_hash(net_vault, outcome, candidate_snapshot=snapshot) == expected


def test_identifier_hash_of_a_deleted_note_holds_from_the_base_snapshot(net_vault):
    source = net_vault / "literature" / "smith2020.md"
    before = hashlib.sha256(_note_bytes(source.read_bytes())).hexdigest()[:16]
    base = gitstate.snapshot_worktree(net_vault)
    source.unlink()
    outcome = _outcome(
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "retracted — x",
        note_path="literature/smith2020.md",
    )
    assert _target_hash(net_vault, outcome, base_snapshot=base) == before
    assert len(before) == 16


def test_verify_state_refuses_an_index_candidate_whose_destination_differs_live(
    net_vault, monkeypatch
):
    """`_candidate_destinations_match_live` through its product caller: an
    index candidate (the pre-commit hook's shape) with a worktree that
    differs from the index at a planned output path."""
    # The retracted notice files a `failed-verification` event on the note:
    # `literature/smith2020.md` is a planned output. Staged as the fixture
    # committed it, then changed in the worktree only.
    source = net_vault / "literature" / "smith2020.md"
    subprocess.run(["git", "add", "-A"], cwd=net_vault, check=True)
    source.write_text(source.read_text() + "\n")
    _isolate_network_verify(
        monkeypatch,
        [_outcome("update-notice", "smith2020", Result.UNMATCHED, "retracted — x")],
    )
    with pytest.raises(gitstate.GitStateError) as excinfo:
        verify_state(net_vault, network=True, git_candidate="index")
    assert str(excinfo.value) == (
        "selected candidate differs from live projection destination: "
        "path-bytes:literature/smith2020.md"
    )


def test_network_outcomes_reduce_the_live_leg_with_an_rw_lookup(net_vault, monkeypatch):
    """The only direct test call passed `notice_lookup=None`; with a lookup
    the RW leg runs and the reduction sees both."""
    monkeypatch.setattr(
        checks,
        "check_update_notice",
        lambda vault, entry, date: checks.Outcome(
            "update-notice", entry["id"], Result.MATCHED, "matched"
        ),
    )
    entry = {"id": "smith2020", "DOI": "10.1000/xyz"}
    lookup = {
        "doi": {"10.1000/xyz": [{"type": "Retraction", "notice_date": "2026-01-01"}]},
        "pmid": {},
    }
    (outcome,) = verify._network_outcomes(net_vault, entry, "2026-09-07", lookup)
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason == "retracted — retraction"


def test_verify_state_defaults_to_the_network_leg(net_vault, monkeypatch):
    """`network=True` is the default of `verify_state` and `_plan_state`: the
    lifecycle leg runs (and, under the offline suite's socket block, files
    its outage); `network=False` files the synthetic offline row instead.

    Deviation from the brief's printed text: `check_update_notice` is
    stubbed here. Unlike the Zotero client (autouse-faked into a clean
    `ZoteroError` every offline run), a live DOI registry lookup is not
    autouse-mocked, and `webapi`'s narrow `except OSError` does not catch
    the socket guard's deliberately-not-`OSError` block — so the real
    `smith2020`/`gone2019` DOIs would otherwise leak a live socket connect
    through this test rather than exercising the lifecycle leg this test is
    about."""
    monkeypatch.setattr(
        checks,
        "check_update_notice",
        lambda vault, entry, date: checks.Outcome(
            "update-notice", entry["id"], Result.SKIPPED, "no-identifier — stubbed"
        ),
    )
    report, _effective, _hashes, _warnings = verify_state(net_vault)
    lifecycle_rows = [o for o in report["outcomes"] if o.check == "lifecycle"]
    assert lifecycle_rows
    assert all(o.extra.get("synthetic_offline") is not True for o in lifecycle_rows)
    report, _effective, _hashes, _warnings = verify_state(net_vault, network=False)
    (row,) = [o for o in report["outcomes"] if o.check == "lifecycle"]
    assert row.extra.get("synthetic_offline") is True


def test_plan_state_reports_an_unparseable_bibliography_as_a_citation_key_row(
    net_vault,
):
    """`bibliography.load`'s schema failure becomes one `citation-key` row
    targeting the bibliography file's own repo path, not a crash — the
    `_plan_state` group's first prose test (pre-lane-2 §6.2)."""
    bib_path = net_vault / "system" / "bibliography.json"
    bib_path.write_text("not json")
    report = run_verify(net_vault, network=False)
    (row,) = [o for o in report["outcomes"] if o.check == "citation-key"]
    assert row.target == encode_repo_path(os.fsencode(bibliography.BIB_PATH))
    assert row.result is Result.UNMATCHED
    assert row.reason == "schema-violation — bibliography JSON/schema invalid"


def test_plan_state_forwards_a_discovered_doi_to_the_update_notice_check(
    net_vault, monkeypatch
):
    """A bibliography entry with no DOI, under `network=True`: whatever
    `identify.discover` puts in `extra["identifiers"]` reaches
    `check_update_notice` on the very same entry, not the pre-discovery one
    — the `_plan_state` group's second prose test (pre-lane-2 §6.2)."""
    bib_path = net_vault / "system" / "bibliography.json"
    entries = json.loads(bib_path.read_text())
    entries.append({"id": "undoid2020", "title": "No DOI yet"})
    bib_path.write_text(json.dumps(entries))
    monkeypatch.setattr(
        identify,
        "discover",
        lambda vault, entry: checks.Outcome(
            "identifier-discovery",
            entry["id"],
            Result.MATCHED,
            "matched",
            {"identifiers": {"DOI": "10.1/found"}},
        ),
    )
    seen = []

    def record(vault, entry, date):
        seen.append(entry)
        return checks.Outcome("update-notice", entry["id"], Result.MATCHED, "matched")

    monkeypatch.setattr(checks, "check_update_notice", record)
    monkeypatch.setattr("research_vault.lifecycle.lint_lifecycle", lambda *_args: [])
    run_verify(net_vault, network=True, detection_date="2026-09-07")
    (entry,) = [e for e in seen if e["id"] == "undoid2020"]
    assert entry["DOI"] == "10.1/found"


def test_plan_state_counts_match_a_hand_tallied_counter_of_effective_results(
    net_vault,
):
    """`counts` is exactly a tally of `effective`'s results, not `raw`'s —
    the `_plan_state` group's third prose test (pre-lane-2 §6.2)."""
    report, effective, _hashes, _warnings = verify_state(
        net_vault, network=False, detection_date="2026-09-07"
    )
    assert report["counts"] == dict(Counter(o.result.value for o in effective))


def test_plan_state_forwards_repository_root_to_lint_append_only(
    net_vault, monkeypatch, tmp_path
):
    """`repository_root` is the real repo `verify_state` is publishing to,
    not the temporary materialized planning directory `_plan_state` itself
    scans notes from — `lint_append_only` must see the caller's value
    verbatim, not the planning directory — the `_plan_state` group's fourth
    prose test (pre-lane-2 §6.2)."""
    seen = []

    def record(repository, base_snapshot, candidate_snapshot):
        seen.append(repository)
        return []

    monkeypatch.setattr(lints, "lint_append_only", record)
    monkeypatch.setattr(lints, "lint_claim_immutability", lambda *_args: [])
    monkeypatch.setattr(lints, "lint_published_drift", lambda *_args: [])
    snapshots = gitstate.resolve_snapshots(net_vault)
    marker_repo = tmp_path / "elsewhere"
    marker_repo.mkdir()
    verify._plan_state(
        net_vault,
        network=False,
        detection_date="2026-09-07",
        repository_root=marker_repo,
        snapshots=snapshots,
    )
    assert seen == [marker_repo]


# --- the survivor triage: the rest of the inventory, verify.py (§6.2 continued) --


def test_apply_state_transitions_stamps_the_verified_event_with_detection_date(
    net_vault,
):
    """The `at=detection_date` argument to `events.record_pass` is load-
    bearing: `record_pass` defaults a missing `at` to `clock.today()`, so a
    `detection_date` that is not today's real date is the only thing that
    tells the two apart."""
    outcome = checks.Outcome("update-notice", "smith2020", Result.MATCHED, "matched")
    _apply_state_transitions(net_vault, [outcome], "2020-01-01", stamp=[outcome])
    source = (net_vault / "literature" / "smith2020.md").read_text()
    (event,) = [
        e for e in events.verified_checks(source) if e["check"] == "update-notice"
    ]
    assert event["at"] == "2020-01-01"


def test_apply_state_transitions_skips_a_projection_whose_citation_key_is_invalid(
    net_vault,
):
    """`_note_for_citation_key` returns `None` for a citation key
    `note_path` rejects (an embedded `/`); the guard's `and` must short-
    circuit before `note.is_file()` — an `or` would call `.is_file()` on
    `None` and crash."""
    outcome = checks.Outcome(
        "update-notice", "evil/key", Result.UNMATCHED, "outage — x"
    )
    _apply_state_transitions(net_vault, [outcome], "2026-08-16", stamp=[])


def test_apply_state_transitions_leaves_an_unreachable_outcomes_marker_alone(
    net_vault,
):
    """Only a genuine MATCHED clears a marker: `is not Result.MATCHED` would
    also fire for UNREACHABLE, which the branch above does not touch."""
    note = net_vault / "literature" / "smith2020.md"
    marked = must_replace(
        note.read_text(),
        "^c-11111111",
        "[failed-verification:: quote/2026-08-16] ^c-11111111",
    )
    note.write_text(marked)
    outcome = _outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNREACHABLE,
        "outage — x",
        note_path="literature/smith2020.md",
        claim_id="c-11111111",
    )
    _apply_state_transitions(net_vault, [outcome], "2026-08-16", stamp=[])
    assert "[failed-verification:: quote/2026-08-16]" in note.read_text()


def test_verify_state_accepts_an_index_candidate_whose_destination_matches_live(
    net_vault, monkeypatch
):
    """The pass twin of the refusal above: staged and worktree agree at the
    one output path this run touches (`literature/smith2020.md`, via the
    retraction's `record_failure`), so nothing raises — and the loop must
    have actually compared real images, not a stray `None`, for that to be
    meaningful."""
    subprocess.run(["git", "add", "-A"], cwd=net_vault, check=True)
    _isolate_network_verify(
        monkeypatch,
        [_outcome("update-notice", "smith2020", Result.UNMATCHED, "retracted — x")],
    )
    report, _effective, _hashes, _warnings = verify_state(
        net_vault, network=True, git_candidate="index"
    )
    assert report["outcomes"]


def test_mutate_marker_skips_an_origin_whose_safe_path_is_none(net_vault, tmp_path):
    """A `note_path` naming a symlink that escapes the vault resolves
    through `_safe_relative` to `None`. The guard's `or` must short-circuit
    before reaching `path.is_file()` — an `and` here evaluates
    `None.is_file()` and crashes instead of quietly skipping the origin."""
    outside_root = tmp_path.parent / f"{tmp_path.name}-outside"
    outside_root.mkdir()
    outside = outside_root / "outside.md"
    outside.write_text("outside remains private\n")
    link = net_vault / "projects" / "brief" / "escape-marker.md"
    link.symlink_to(outside)
    outcome = _outcome(
        "quote",
        "missing#^c-1",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="projects/brief/escape-marker.md",
        claim_id="c-1",
    )
    _mutate_marker(net_vault, outcome, "2026-08-16")  # must not raise
    assert outside.read_text() == "outside remains private\n"


def test_claim_anchor_hash_reads_the_candidate_image_through_surrogateescape(
    net_vault,
):
    """The origin-image plane's own decode: invalid UTF-8 forces the
    surrogateescape handler (a mis-cased or wrong handler name crashes only
    when a byte actually needs it — this one does), `or b""` only guards a
    genuinely absent image (discarding real bytes to `and` would lose the
    claim), and the claim id it searches for is the literal second
    argument — dropping, losing, or nulling any of the three changes the
    hash or crashes. A leading, unrelated bullet makes the file bigger than
    the one claim: `_target_hash`'s fallthrough to `_identifier_hash` hashes
    the *whole* note when the anchor plane comes up empty, which would
    coincidentally reproduce a single-bullet file's hash — the second
    bullet makes that fallback answer provably wrong instead."""
    note = net_vault / "projects" / "brief" / "invalid-claim.md"
    other_bytes = b"- (quote) unrelated bullet [@missing] ^c-other\n"
    claim_bytes = b"- (quote) invalid \xff [@missing] ^c-invalid\n"
    note.write_bytes(other_bytes + claim_bytes)
    candidate_snapshot = gitstate.snapshot_worktree(net_vault)
    outcome = _outcome(
        "quote",
        "missing#^c-invalid",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="projects/brief/invalid-claim.md",
        claim_id="c-invalid",
    )
    expected = hashlib.sha256(claim_bytes).hexdigest()[:16]
    assert (
        _target_hash(net_vault, outcome, candidate_snapshot=candidate_snapshot)
        == expected
    )


def test_claim_anchor_hash_of_a_deleted_note_holds_from_the_base_snapshot(net_vault):
    """The claim-anchor's own base-snapshot leg: the candidate lacks the
    note (deleted), the origin plane is forced off by the candidate
    snapshot's presence — the claim's bytes come from the base image, keyed
    by the base snapshot the caller passed, at the real raw origin, read as
    a real `"file"`-kind image from a real `"HEAD"`."""
    source = net_vault / "literature" / "smith2020.md"
    text = source.read_text()
    claim_bytes = _claim_bytes_from_text(text, "c-11111111")
    expected = hashlib.sha256(claim_bytes).hexdigest()[:16]
    base = gitstate.snapshot_worktree(net_vault)
    source.unlink()
    candidate = gitstate.snapshot_worktree(net_vault)
    outcome = _outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="literature/smith2020.md",
        claim_id="c-11111111",
    )
    assert (
        _target_hash(
            net_vault, outcome, base_snapshot=base, candidate_snapshot=candidate
        )
        == expected
    )


def test_claim_anchor_hash_stays_gone_when_base_snapshot_also_lacks_the_note(
    net_vault,
):
    """`head`'s HEAD-blob fallback is gated on `base_snapshot is None`; with
    an explicit (post-deletion) base snapshot that also lacks the note, the
    claim is genuinely gone — not recoverable from git HEAD behind the
    snapshot's back."""
    source = net_vault / "literature" / "smith2020.md"
    source.unlink()
    base = gitstate.snapshot_worktree(net_vault)
    candidate = gitstate.snapshot_worktree(net_vault)
    outcome = _outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="literature/smith2020.md",
        claim_id="c-11111111",
    )
    assert (
        _target_hash(
            net_vault, outcome, base_snapshot=base, candidate_snapshot=candidate
        )
        is None
    )


def test_claim_anchor_hash_uses_the_real_candidate_snapshot_for_the_citation_key_lookup(
    net_vault,
):
    """`_citation_key_hash`'s own `candidate_snapshot` argument must be the
    one this call received, not a stray `None`: a candidate snapshot that
    still has the note (even though the worktree has since lost it) must
    short-circuit on the candidate's witness, not fall through to a
    worktree-based absence that no longer holds."""
    source = net_vault / "literature" / "smith2020.md"
    candidate_snapshot = gitstate.snapshot_worktree(net_vault)  # note still present
    source.unlink()  # the worktree loses it; candidate_snapshot does not
    outcome = _outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="literature/smith2020.md",
        claim_id="c-11111111",
    )
    digest = _citation_key_hash(
        net_vault, "smith2020", candidate_snapshot=candidate_snapshot
    )
    assert digest is not None
    assert (
        _target_hash(net_vault, outcome, candidate_snapshot=candidate_snapshot)
        == digest
    )


def test_claim_anchor_hash_crashes_are_confined_to_the_citation_key_note_lookup(
    net_vault,
):
    """The last-resort plane (citation key has no note of its own anywhere,
    origin and base/HEAD both come up empty, no candidate snapshot): its own
    `_note_for_citation_key` and `_claim_bytes` calls must receive the real
    `vault_root`/`citation_key`/`note`, not a dropped or nulled argument —
    a wrong shape here raises `TypeError` where the real calls return
    `None` cleanly."""
    outcome = _outcome(
        "quote",
        "phantom2020#^c-1",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="projects/brief/never-existed.md",
        claim_id="c-1",
    )
    assert _target_hash(net_vault, outcome) is None


def test_target_hash_of_an_index_candidate_never_reads_a_claim_from_the_worktree(
    net_vault,
):
    """The last-resort citation-key note lookup (`_note_for_citation_key` +
    `_claim_bytes`) reads straight off the worktree, bypassing whatever
    snapshot the caller supplied — so its guard, `candidate_snapshot is
    None`, must gate it strictly to the no-candidate case. An index
    candidate (the pre-commit hook's shape) that omits a note — here, one
    never staged or committed at all, so neither the candidate nor base/HEAD
    plane can see it — must not let this fallback leak the worktree's claim
    bytes back in as if the candidate had verified them."""
    note = net_vault / "literature" / "leaked2020.md"
    note.write_text("- (quote) leaked [@leaked2020, p. 1] ^c-1\n")
    claim_bytes = _claim_bytes_from_text(note.read_text(), "c-1")
    leaked_hash = hashlib.sha256(claim_bytes).hexdigest()[:16]
    outcome = _outcome(
        "quote",
        "leaked2020#^c-1",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="literature/leaked2020.md",
        claim_id="c-1",
    )
    snapshots = gitstate.resolve_snapshots(net_vault, candidate="index")
    result = _target_hash(net_vault, outcome, candidate_snapshot=snapshots.candidate)
    assert (
        result is None
    )  # neither the candidate nor _identifier_hash's own legs see it
    assert result != leaked_hash


def test_claim_anchor_hash_does_not_re_derive_a_plane_the_origin_already_answered(
    net_vault,
):
    """Once the origin (worktree) plane has the claim's bytes, the base/HEAD
    leg must not run at all: a stale base snapshot that predates the claim
    would silently discard a good answer if the gate's `and`/`is None`
    conditions let it re-derive."""
    draft = net_vault / "projects" / "brief" / "draft.md"
    stale_base = gitstate.snapshot_worktree(net_vault)
    draft.write_text(
        draft.read_text()
        + "- (inference) Uncommitted claim [@fabricated2020] ^c-uncommitted\n"
    )
    outcome = _outcome(
        "quote",
        "fabricated2020#^c-uncommitted",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="projects/brief/draft.md",
        claim_id="c-uncommitted",
    )
    claim_bytes = _claim_bytes_from_text(draft.read_text(), "c-uncommitted")
    expected = hashlib.sha256(claim_bytes).hexdigest()[:16]
    assert _target_hash(net_vault, outcome, base_snapshot=stale_base) == expected


def test_clear_marker_for_continues_past_a_guarded_candidate_to_a_later_one(net_vault):
    """`_claim_notes` can list a candidate the guard skips (a broken symlink,
    sorted first) before a real one carrying the marker to clear —
    `continue` must move on to it, not `break` the whole walk."""
    broken = net_vault / "projects" / "brief" / "aaa-broken.md"
    broken.symlink_to(net_vault / "projects" / "brief" / "does-not-exist.md")
    draft = net_vault / "projects" / "brief" / "draft.md"
    marked = must_replace(
        draft.read_text(),
        "^c-77777777",
        "[failed-verification:: citation-key/2026-09-07] ^c-77777777",
    )
    draft.write_text(marked)
    assert markers.clear_marker_for(net_vault, "citation-key", "fabricated2020") is True
    assert "[failed-verification" not in draft.read_text()


def test_clear_marker_for_skips_a_path_bytes_target_whose_safe_path_is_none(
    net_vault, tmp_path
):
    """A `path-bytes:` target naming a symlink that escapes the vault
    resolves through `_safe_relative` to `None`; the guard's `or` must
    short-circuit before `path.is_file()` — an `and` would crash on
    `None.is_file()` instead of returning `False` quietly."""
    outside_root = tmp_path.parent / f"{tmp_path.name}-outside"
    outside_root.mkdir()
    outside = outside_root / "outside.md"
    outside.write_text("outside remains private\n")
    link = net_vault / "projects" / "brief" / "escape-clear.md"
    link.symlink_to(outside)
    assert (
        markers.clear_marker_for(
            net_vault, "quote", "path-bytes:projects/brief/escape-clear.md"
        )
        is False
    )


def test_clear_marker_for_claim_id_leaves_an_unanchored_lines_own_marker_alone(
    net_vault,
):
    """The `claim_id` matcher's own `(False, None)` for a line without the
    target claim's anchor must stay `False` — a stray `True` would make
    every line in the note "selected", so an unrelated line's own
    general-form marker (stamped by a different, no-anchor origin) would be
    cleared as collateral damage alongside the real target."""
    note = net_vault / "projects" / "brief" / "collateral.md"
    note.write_text(
        "- (quote) target [@missing] [failed-verification:: quote/2026-08-16] ^c-target\n"
        "- (quote) unrelated [@missing] [failed-verification:: quote/2026-08-16]\n"
    )
    assert markers.clear_marker_for(net_vault, "quote", "missing#^c-target") is True
    lines = note.read_text().splitlines()
    assert "[failed-verification" not in lines[0]
    assert "[failed-verification:: quote/2026-08-16]" in lines[1]


def test_clear_marker_for_citation_key_leaves_a_non_citing_lines_own_marker_alone(
    net_vault,
):
    """The `citation_key` matcher's own `(False, None)` for a line that
    does not cite the target key must stay `False` — a stray `True` would
    select every line in the note, clearing an unrelated citation's own
    general-form marker as collateral damage."""
    note = net_vault / "projects" / "brief" / "collateral-citation.md"
    note.write_text(
        "- (quote) cites [@smith2020, p. 1] [failed-verification:: citation-key/2026-08-16]\n"
        "- (quote) does not cite [@gone2019, p. 1] [failed-verification:: citation-key/2026-08-16]\n"
    )
    assert markers.clear_marker_for(net_vault, "citation-key", "smith2020") is True
    lines = note.read_text().splitlines()
    assert "[failed-verification" not in lines[0]
    assert "[failed-verification:: citation-key/2026-08-16]" in lines[1]


def test_identifier_hash_reads_the_candidate_image_when_no_citation_key_note_exists(
    net_vault,
):
    """An identifier whose citation key has no note of its own reads its
    origin through the candidate image: `or b""` only guards a genuinely
    absent image (discarding real bytes to `and` would lose the note), and
    only a real `"file"`-kind image counts."""
    note = net_vault / "projects" / "brief" / "orphan-note.md"
    note.write_text("some content for an orphan identifier\n")
    candidate_snapshot = gitstate.snapshot_worktree(net_vault)
    outcome = _outcome(
        "update-notice",
        "orphan2020",
        Result.UNMATCHED,
        "retracted — x",
        note_path="projects/brief/orphan-note.md",
    )
    expected = hashlib.sha256(_note_bytes(note.read_bytes())).hexdigest()[:16]
    assert (
        _target_hash(net_vault, outcome, candidate_snapshot=candidate_snapshot)
        == expected
    )


def test_identifier_hash_reads_the_worktree_origin_without_a_candidate_snapshot(
    net_vault,
):
    """No candidate snapshot at all: `origin_image` is never built (its own
    guard needs one), so `_identifier_hash`'s `origin and origin.is_file()`
    plane must read the real worktree `Path` directly. Distinct from the
    origin-image tests above, and from `_citation_key_hash`'s own
    witness-less fallback (this identifier has no note under its own
    citation key anywhere, so that fallback never fires first)."""
    note = net_vault / "projects" / "brief" / "orphan-worktree.md"
    note.write_text("some content for an orphan identifier read from the worktree\n")
    outcome = _outcome(
        "update-notice",
        "orphanworktree2020",
        Result.UNMATCHED,
        "retracted — x",
        note_path="projects/brief/orphan-worktree.md",
    )
    expected = hashlib.sha256(_note_bytes(note.read_bytes())).hexdigest()[:16]
    assert _target_hash(net_vault, outcome) == expected


def test_identifier_hash_of_an_empty_origin_image_hashes_true_empty_bytes(net_vault):
    """`origin_image.data or b""` only substitutes when the image itself
    carries no bytes — the substitute must be the true empty string, not a
    stray filler that becomes the hashed content."""
    note = net_vault / "projects" / "brief" / "empty-orphan.md"
    note.write_text("")
    candidate_snapshot = gitstate.snapshot_worktree(net_vault)
    outcome = _outcome(
        "update-notice",
        "emptyorphan2020",
        Result.UNMATCHED,
        "retracted — x",
        note_path="projects/brief/empty-orphan.md",
    )
    expected = hashlib.sha256(_note_bytes(b"")).hexdigest()[:16]
    assert (
        _target_hash(net_vault, outcome, candidate_snapshot=candidate_snapshot)
        == expected
    )


def test_identifier_hash_stays_gone_when_base_snapshot_also_lacks_the_orphan_note(
    net_vault,
):
    """`base_image is not None and base_image.kind == "file"` must
    short-circuit before `.kind`: an `or` here evaluates `None.kind` and
    crashes. And with `base_image` genuinely `None`, the HEAD-blob fallback
    stays gated on `base_snapshot is None` — a real (committed) HEAD is not
    read behind an explicit base snapshot's back."""
    note = net_vault / "projects" / "brief" / "orphan-gone.md"
    note.write_text("will be gone everywhere\n")
    subprocess.run(["git", "add", "-A"], cwd=net_vault, check=True)
    subprocess.run(["git", "commit", "-qm", "add orphan"], cwd=net_vault, check=True)
    note.unlink()
    base = gitstate.snapshot_worktree(net_vault)  # taken after deletion too
    candidate = gitstate.snapshot_worktree(net_vault)
    outcome = _outcome(
        "update-notice",
        "orphan2023",
        Result.UNMATCHED,
        "retracted — x",
        note_path="projects/brief/orphan-gone.md",
    )
    assert (
        _target_hash(
            net_vault, outcome, base_snapshot=base, candidate_snapshot=candidate
        )
        is None
    )


def test_identifier_hash_of_a_deleted_orphan_note_holds_from_head_without_base_snapshot(
    net_vault,
):
    """With no `base_snapshot` at all, the HEAD-blob fallback reads the real
    `vault_root`/`"HEAD"`/`raw_origin` — a dropped, `None`d, or wrong-cased
    argument returns nothing or crashes instead of the committed content."""
    note = net_vault / "projects" / "brief" / "orphan-head.md"
    note.write_text("orphan content from head\n")
    subprocess.run(["git", "add", "-A"], cwd=net_vault, check=True)
    subprocess.run(
        ["git", "commit", "-qm", "add orphan head"], cwd=net_vault, check=True
    )
    note.unlink()
    expected = hashlib.sha256(_note_bytes(b"orphan content from head\n")).hexdigest()[
        :16
    ]
    outcome = _outcome(
        "update-notice",
        "orphan2024",
        Result.UNMATCHED,
        "retracted — x",
        note_path="projects/brief/orphan-head.md",
    )
    assert _target_hash(net_vault, outcome) == expected


def test_identifier_hash_uses_the_real_candidate_snapshot_for_the_citation_key_lookup(
    net_vault,
):
    """`_citation_key_hash`'s own `candidate_snapshot` argument must be the
    one this call received, not a stray `None`: a candidate snapshot that
    still has the note (even though the worktree has since lost it) must
    short-circuit on the candidate's witness, not fall through to the
    bibliography entry's JSON."""
    source = net_vault / "literature" / "smith2020.md"
    candidate_snapshot = gitstate.snapshot_worktree(net_vault)  # note still present
    source.unlink()  # the worktree loses it; candidate_snapshot does not
    outcome = _outcome("update-notice", "smith2020", Result.UNMATCHED, "retracted — x")
    digest = _citation_key_hash(
        net_vault, "smith2020", candidate_snapshot=candidate_snapshot
    )
    assert digest is not None
    assert (
        _target_hash(net_vault, outcome, candidate_snapshot=candidate_snapshot)
        == digest
    )


def test_identifier_hash_returns_none_when_bibliography_universe_is_explicitly_none(
    net_vault,
):
    """`bibliography_universe=None` (as opposed to `_target_hash`'s omitted-
    sentinel default) must land on `entry = None`, not a stray truthy
    placeholder that would still hash."""
    outcome = _outcome(
        "update-notice", "totally-unknown-id", Result.UNMATCHED, "retracted — x"
    )
    assert _target_hash(net_vault, outcome, None) is None


def test_identifier_hash_uses_the_explicit_bibliography_universe_when_given(net_vault):
    """A real (non-sentinel, non-`None`) `bibliography_universe` is read
    through its own `.get(target)`, not the loaded file's and not a stray
    `None`/wrong key."""
    entry = {"id": "explicit-id", "title": "Explicit"}
    universe = {"explicit-id": entry}
    outcome = _outcome(
        "update-notice", "explicit-id", Result.UNMATCHED, "retracted — x"
    )
    expected = hashlib.sha256(
        json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:16]
    assert _target_hash(net_vault, outcome, universe) == expected


def test_plan_state_forwards_the_real_base_snapshot_to_target_hash(
    net_vault, monkeypatch
):
    """The `hashes` dict's `_target_hash` call must receive `_plan_state`'s
    own `base_snapshot`, not a stray `None` — a deleted note's update-notice
    hash must still resolve from HEAD's base image, not the bibliography
    entry's JSON fallback."""
    _isolate_network_verify(
        monkeypatch,
        [
            _outcome(
                "update-notice",
                "smith2020",
                Result.UNMATCHED,
                "retracted — x",
                note_path="literature/smith2020.md",
            )
        ],
    )
    source = net_vault / "literature" / "smith2020.md"
    expected = hashlib.sha256(_note_bytes(source.read_bytes())).hexdigest()[:16]
    source.unlink()
    report, _effective, hashes, _warnings = verify_state(
        net_vault, network=True, detection_date="2026-09-07"
    )
    (outcome,) = [
        o
        for o in report["outcomes"]
        if o.check == "update-notice" and o.target == "smith2020"
    ]
    assert hashes[id(outcome)] == expected


def test_plan_state_forwards_the_real_candidate_snapshot_to_target_hash(
    net_vault, monkeypatch
):
    """The `hashes` dict's `_target_hash` call must receive `_plan_state`'s
    own `candidate_snapshot`, not a stray `None` — a candidate snapshot
    whose note differs from the worktree's is the only way to tell "the
    real candidate" apart from "a worktree-based re-derivation"."""
    import dataclasses

    _isolate_network_verify(
        monkeypatch,
        [
            _outcome(
                "update-notice",
                "smith2020",
                Result.UNMATCHED,
                "retracted — x",
                note_path="literature/smith2020.md",
            )
        ],
    )
    source = net_vault / "literature" / "smith2020.md"
    real_snapshot = gitstate.snapshot_worktree(net_vault)  # taken before deletion
    digest = _citation_key_hash(
        net_vault, "smith2020", candidate_snapshot=real_snapshot
    )
    assert digest is not None
    source.unlink()  # a None-forced re-derivation would see this deletion instead
    snapshots = gitstate.resolve_snapshots(net_vault, candidate="worktree")
    forced_snapshots = dataclasses.replace(snapshots, candidate=real_snapshot)
    report, _effective, hashes, _warnings = verify._plan_state(
        net_vault,
        network=True,
        detection_date="2026-09-07",
        repository_root=net_vault,
        snapshots=forced_snapshots,
    )
    (outcome,) = [
        o
        for o in report["outcomes"]
        if o.check == "update-notice" and o.target == "smith2020"
    ]
    assert hashes[id(outcome)] == digest


def test_plan_state_forwards_the_loaded_bibliography_universe_to_target_hash(
    net_vault, monkeypatch
):
    """The `hashes` dict's `_target_hash` call must receive `_plan_state`'s
    own loaded `bibliography_universe`, not a stray `None` — a bibliography
    entry with no note of its own hashes its canonical JSON only when that
    universe reaches `_identifier_hash`."""
    bib_path = net_vault / "system" / "bibliography.json"
    entries = json.loads(bib_path.read_text())
    entry = {"id": "noted-yet2", "title": "No note yet"}
    entries.append(entry)
    bib_path.write_text(json.dumps(entries))
    _isolate_network_verify(
        monkeypatch,
        [_outcome("update-notice", "noted-yet2", Result.UNMATCHED, "retracted — x")],
    )
    expected = hashlib.sha256(
        json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:16]
    report, _effective, hashes, _warnings = verify_state(
        net_vault, network=True, detection_date="2026-09-07"
    )
    (outcome,) = [
        o
        for o in report["outcomes"]
        if o.check == "update-notice" and o.target == "noted-yet2"
    ]
    assert hashes[id(outcome)] == expected


def test_plan_state_continues_past_index_and_log_to_check_later_notes(net_vault):
    """`index.md`/`log.md` are skipped by name inside the frontmatter walk;
    `continue` must move on to check the rest, not `break` the whole scan."""
    bad = net_vault / "zz-bad-frontmatter.md"
    bad.write_text("---\nnot: [valid, frontmatter\n---\nbody\n")
    report = run_verify(net_vault, network=False, detection_date="2026-09-07")
    assert any(
        o.check == "okf-frontmatter" and "zz-bad-frontmatter.md" in str(o.target)
        for o in report["outcomes"]
    )


def test_plan_state_continues_past_an_excluded_directory_to_check_later_notes(
    net_vault,
):
    """`structure.is_excluded` is checked first in the same loop, on its own
    `continue`: a `.md` under `.raw/` (an excluded dir, sorted well before
    the rest of the walk) must not stop the scan from reaching a later,
    genuinely bad note."""
    excluded_dir = net_vault / ".raw"
    excluded_dir.mkdir(exist_ok=True)
    (excluded_dir / "aa-excluded.md").write_text("not frontmatter at all\n")
    bad = net_vault / "zz-bad-frontmatter.md"
    bad.write_text("---\nnot: [valid, frontmatter\n---\nbody\n")
    report = run_verify(net_vault, network=False, detection_date="2026-09-07")
    assert any(
        o.check == "okf-frontmatter" and "zz-bad-frontmatter.md" in str(o.target)
        for o in report["outcomes"]
    )


def test_plan_state_forwards_the_real_vault_and_entry_to_identify_discover(
    net_vault, monkeypatch
):
    bib_path = net_vault / "system" / "bibliography.json"
    entries = json.loads(bib_path.read_text())
    entries.append({"id": "nodoi2020", "title": "No DOI"})
    bib_path.write_text(json.dumps(entries))
    seen = []

    def record(vault, entry):
        seen.append((vault, entry))
        return checks.Outcome(
            "identifier-discovery",
            entry["id"],
            Result.SKIPPED,
            "no-identifier — x",
            {"identifiers": {}},
        )

    monkeypatch.setattr(identify, "discover", record)
    monkeypatch.setattr(
        checks,
        "check_update_notice",
        lambda vault, entry, date: checks.Outcome(
            "update-notice", entry["id"], Result.MATCHED, "matched"
        ),
    )
    monkeypatch.setattr("research_vault.lifecycle.lint_lifecycle", lambda *_args: [])
    run_verify(net_vault, network=True, detection_date="2026-09-07")
    (vault_seen, entry_seen) = next((v, e) for v, e in seen if e["id"] == "nodoi2020")
    # `_plan_state` runs against the materialized planning directory, not
    # `net_vault` itself — the mutation under test replaces this argument
    # with `None`, so a real (non-`None`) path is what distinguishes it.
    assert vault_seen is not None
    assert "research-vault-verification-plan-" in str(vault_seen)
    assert entry_seen["id"] == "nodoi2020"


def test_plan_state_forwards_vault_detection_date_and_notice_lookup_to_network_outcomes(
    net_vault, monkeypatch, tmp_path
):
    seen = []

    def record(vault, entry, detection_date, notice_lookup):
        seen.append((vault, entry, detection_date, notice_lookup))
        return []

    monkeypatch.setattr(verify, "_network_outcomes", record)
    monkeypatch.setattr("research_vault.lifecycle.lint_lifecycle", lambda *_args: [])
    csv = tmp_path / "rw.csv"
    csv.write_text(
        "OriginalPaperDOI,RetractionNature,RetractionDate,OriginalPaperPubMedID\n"
    )
    run_verify(net_vault, network=True, detection_date="2026-09-07", rw_csv=str(csv))
    assert seen
    vault_seen, _entry, date_seen, lookup_seen = seen[0]
    assert vault_seen is not None
    assert "research-vault-verification-plan-" in str(vault_seen)
    assert date_seen == "2026-09-07"
    assert lookup_seen is not None


def test_plan_state_forwards_detection_date_to_offline_network_outcomes(
    net_vault, monkeypatch, tmp_path
):
    """`network=False`'s own leg forwards `detection_date` to
    `_offline_network_outcomes`, which reaches `check_rw_batch`'s
    `_blocking_outcome` the same way the live leg does."""
    csv = tmp_path.parent / f"{tmp_path.name}-rw.csv"
    csv.write_text(
        "OriginalPaperDOI,RetractionNature,RetractionDate,OriginalPaperPubMedID\n"
        "10.1000/xyz,Retraction,2026-01-01,\n"
    )
    monkeypatch.setattr(
        verify,
        "_bibliography_entries",
        lambda _: [{"id": "smith2020", "DOI": "10.1000/xyz"}],
    )
    report = run_verify(
        net_vault, network=False, detection_date="2026-09-07", rw_csv=str(csv)
    )
    (outcome,) = [
        o
        for o in report["outcomes"]
        if o.check == "update-notice" and o.target == "smith2020"
    ]
    assert outcome.extra.get("detection_date") == "2026-09-07"


def test_plan_state_scans_wiki_notes_for_citation_key_and_quote_checks(net_vault):
    """`for folder in ("wiki", "projects")` must glob the real `wiki/`
    directory — a mistyped or wrong-cased name silently stops scanning it,
    and any citation a wiki note carries goes unchecked."""
    concept = net_vault / "wiki" / "concepts" / "new-wiki-note.md"
    concept.write_text(
        '---\ntitle: "New"\ntype: "concept"\nstatus: "draft"\n'
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}\n---\n'
        "- (inference) test claim [@fabricated-wiki-key] ^c-wikitest\n"
    )
    report = run_verify(net_vault, network=False, detection_date="2026-09-07")
    assert any(
        o.check == "citation-key" and o.target == "fabricated-wiki-key"
        for o in report["outcomes"]
    )


def test_plan_state_scans_literature_notes_for_citation_key_and_quote_checks(
    net_vault,
):
    """`(vault / "literature").glob("*.md")` must find the real directory
    and the real case-sensitive `"*.md"` suffix — a mistyped name or suffix
    silently stops scanning it, and any citation a literature note itself
    carries goes unchecked."""
    source = net_vault / "literature" / "smith2020.md"
    text = source.read_text()
    source.write_text(
        must_replace(
            text,
            "# Mortality decline\n",
            "# Mortality decline\n\n"
            "- (inference) stray claim [@fabricated-lit-key] ^c-littest\n",
        )
    )
    report = run_verify(net_vault, network=False, detection_date="2026-09-07")
    assert any(
        o.check == "citation-key" and o.target == "fabricated-lit-key"
        for o in report["outcomes"]
    )


def test_plan_state_skips_discovery_for_a_lowercase_doi_entry(net_vault, monkeypatch):
    """`entry.get("DOI") or entry.get("doi")` must check both spellings and
    take the true one: a lowercase-only `doi`, with `and` instead of `or` or
    a wrong/dropped key on the "doi" side, would wrongly run discovery
    instead of skipping it."""
    bib_path = net_vault / "system" / "bibliography.json"
    entries = json.loads(bib_path.read_text())
    entries.append({"id": "lowerdoi2020", "title": "Lower", "doi": "10.1/lower"})
    bib_path.write_text(json.dumps(entries))
    called = []

    def record(vault, entry):
        called.append(entry)
        return checks.Outcome(
            "identifier-discovery",
            entry["id"],
            Result.SKIPPED,
            "no-identifier — x",
            {"identifiers": {}},
        )

    monkeypatch.setattr(identify, "discover", record)
    monkeypatch.setattr(
        checks,
        "check_update_notice",
        lambda vault, entry, date: checks.Outcome(
            "update-notice", entry["id"], Result.MATCHED, "matched"
        ),
    )
    monkeypatch.setattr("research_vault.lifecycle.lint_lifecycle", lambda *_args: [])
    run_verify(net_vault, network=True, detection_date="2026-09-07")
    assert not any(e["id"] == "lowerdoi2020" for e in called)


def test_plan_state_skips_discovery_for_an_uppercase_doi_entry(net_vault, monkeypatch):
    """The "DOI" side of the same check, isolated the same way — a wrong or
    dropped key on the "DOI" side must not fall back to a stray lowercase-
    only lookup."""
    bib_path = net_vault / "system" / "bibliography.json"
    entries = json.loads(bib_path.read_text())
    entries.append({"id": "upperdoi2020", "title": "Upper", "DOI": "10.1/upper"})
    bib_path.write_text(json.dumps(entries))
    called = []

    def record(vault, entry):
        called.append(entry)
        return checks.Outcome(
            "identifier-discovery",
            entry["id"],
            Result.SKIPPED,
            "no-identifier — x",
            {"identifiers": {}},
        )

    monkeypatch.setattr(identify, "discover", record)
    monkeypatch.setattr(
        checks,
        "check_update_notice",
        lambda vault, entry, date: checks.Outcome(
            "update-notice", entry["id"], Result.MATCHED, "matched"
        ),
    )
    monkeypatch.setattr("research_vault.lifecycle.lint_lifecycle", lambda *_args: [])
    run_verify(net_vault, network=True, detection_date="2026-09-07")
    assert not any(e["id"] == "upperdoi2020" for e in called)


def test_plan_state_forwards_repository_and_snapshots_to_the_repo_lints(
    net_vault, monkeypatch
):
    """`repository`, `base_snapshot` and `candidate_snapshot` must reach
    `lint_append_only`, `lint_claim_immutability` and `lint_published_drift`
    exactly as `_plan_state` holds them — a dropped kwarg falls back to
    that lint's own default (`None`), and a dropped positional shifts the
    next argument into its slot."""
    (net_vault / "projects" / "brief" / "draft.md").write_text(
        (net_vault / "projects" / "brief" / "draft.md").read_text() + "uncommitted\n"
    )
    seen = {}

    def record_append_only(repository, base_snapshot, candidate_snapshot):
        seen["append_only"] = (repository, base_snapshot, candidate_snapshot)
        return []

    def record_claim_immutability(repository, base_snapshot, candidate_snapshot):
        seen["claim_immutability"] = (repository, base_snapshot, candidate_snapshot)
        return []

    def record_published_drift(repository, candidate_snapshot):
        seen["published_drift"] = (repository, candidate_snapshot)
        return []

    monkeypatch.setattr(lints, "lint_append_only", record_append_only)
    monkeypatch.setattr(lints, "lint_claim_immutability", record_claim_immutability)
    monkeypatch.setattr(lints, "lint_published_drift", record_published_drift)
    snapshots = gitstate.resolve_snapshots(net_vault)
    verify._plan_state(
        net_vault,
        network=False,
        detection_date="2026-09-07",
        repository_root=net_vault,
        snapshots=snapshots,
    )
    assert seen["append_only"] == (Path(net_vault), snapshots.base, snapshots.candidate)
    assert seen["claim_immutability"] == (
        Path(net_vault),
        snapshots.base,
        snapshots.candidate,
    )
    assert seen["published_drift"] == (Path(net_vault), snapshots.candidate)


def test_plan_state_forwards_detection_date_to_file_effects(net_vault, monkeypatch):
    seen = []

    def record(vault, effective, hashes, warning_effective, detection_date):
        seen.append(detection_date)
        return

    monkeypatch.setattr(verify, "_file_effects", record)
    run_verify(net_vault, network=False, detection_date="2026-09-07")
    assert seen == ["2026-09-07"]


def test_plan_state_own_network_parameter_defaults_to_true(net_vault, monkeypatch):
    """`_plan_state`'s own `network` default (its one production caller,
    `verify_state`, always forwards the value explicitly, so only a direct
    call exercises this default) must be `True`, matching `verify_state`'s."""
    monkeypatch.setattr(
        checks,
        "check_update_notice",
        lambda vault, entry, date: checks.Outcome(
            "update-notice", entry["id"], Result.SKIPPED, "no-identifier — stubbed"
        ),
    )
    snapshots = gitstate.resolve_snapshots(net_vault)
    report, _effective, _hashes, _warnings = verify._plan_state(
        net_vault, detection_date="2026-09-07", snapshots=snapshots
    )
    (row,) = [o for o in report["outcomes"] if o.check == "lifecycle"]
    assert row.extra.get("synthetic_offline") is not True


def test_plan_state_forwards_detection_date_as_of_to_lint_captured_set(
    net_vault, monkeypatch
):
    from research_vault import captured as captured_module

    seen = []

    def record(vault, as_of=None):
        seen.append(as_of)
        return []

    monkeypatch.setattr(captured_module, "lint_captured_set", record)
    run_verify(net_vault, network=False, detection_date="2026-09-07")
    assert seen == ["2026-09-07"]


def test_claim_bytes_from_text_collects_quote_and_comment_continuations_verbatim():
    """The block is the terminal-anchored line plus every immediately
    following continuation (a `  > ` quote line or a `  <!-- rv-selector`
    comment line) up to the first line that is neither — joined with no
    separator, both continuation prefixes case-sensitive, starting exactly
    one line after the anchor. A hard-coded expectation, not the function's
    own output, is the oracle: mutations inside this function cannot be
    caught by a test that recomputes its expectation through the same
    (equally mutated) call."""
    text = (
        "- (quote) [@k] ^c-1\n"
        "  > first quote line\n"
        "  <!-- rv-selector stuff -->\n"
        "- (quote) next claim [@k] ^c-2\n"
    )
    result = _claim_bytes_from_text(text, "c-1")
    assert result == (
        b"- (quote) [@k] ^c-1\n  > first quote line\n  <!-- rv-selector stuff -->\n"
    )


def test_target_hash_forwards_the_real_base_snapshot_to_the_claim_anchor_leg(
    net_vault,
):
    """`_target_hash` must pass its own `base_snapshot` argument through to
    `_claim_anchor_hash`, not a stray `None` — a base snapshot with content
    HEAD never had (an uncommitted claim) is the only way to tell "the real
    base_snapshot" apart from "silently falling back to HEAD"."""
    draft = net_vault / "projects" / "brief" / "draft.md"
    draft.write_text(
        draft.read_text()
        + "- (inference) Base-only claim [@fabricated2020] ^c-baseonly\n"
    )
    claim_bytes = _claim_bytes_from_text(draft.read_text(), "c-baseonly")
    expected = hashlib.sha256(claim_bytes).hexdigest()[:16]
    real_base = gitstate.snapshot_worktree(net_vault)  # has the uncommitted claim
    draft.unlink()  # origin (worktree) no longer has it either
    candidate = gitstate.snapshot_worktree(net_vault)  # candidate lacks it too
    outcome = _outcome(
        "quote",
        "fabricated2020#^c-baseonly",
        Result.UNMATCHED,
        "mismatch — quote",
        note_path="projects/brief/draft.md",
        claim_id="c-baseonly",
    )
    assert (
        _target_hash(
            net_vault, outcome, base_snapshot=real_base, candidate_snapshot=candidate
        )
        == expected
    )


def test_surface_decision_counts_a_warning_effective_by_its_own_index(net_vault):
    """`warning_effective.get((id(outcome), index), ...)` — a per-index
    entry answers before the per-outcome fallback is even consulted."""
    outcome = _outcome(
        "citation-key",
        "k",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction"}],
    )
    _code, blockers = verify.surface_decision(
        "commit", [outcome], {(id(outcome), 0): True}
    )
    assert any("warn-notice — correction" in b for b in blockers)


def test_surface_decision_falls_back_to_the_outcome_level_effectiveness(net_vault):
    """No per-index entry: the per-outcome fallback (`id(outcome)` alone,
    not a stray `None`/wrong key) decides."""
    outcome = _outcome(
        "citation-key",
        "k",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction"}],
    )
    _code, blockers = verify.surface_decision("commit", [outcome], {id(outcome): True})
    assert any("warn-notice — correction" in b for b in blockers)


def test_surface_decision_defaults_a_missing_warning_effectiveness_to_false(net_vault):
    """Neither entry present: the innermost default must stay falsy, not a
    stray `True`."""
    outcome = _outcome(
        "citation-key",
        "k",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction"}],
    )
    _code, blockers = verify.surface_decision("commit", [outcome], {})
    assert blockers == ()


def test_surface_decision_continues_past_an_ineffective_warning_to_a_later_one(
    net_vault,
):
    """Two warnings on one outcome, the first ineffective: `continue` must
    move on to the second, not `break` the whole per-outcome walk."""
    outcome = _outcome(
        "citation-key",
        "k",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction"}, {"type": "retraction"}],
    )
    _code, blockers = verify.surface_decision(
        "commit", [outcome], {(id(outcome), 0): False, (id(outcome), 1): True}
    )
    assert any("warn-notice — retraction" in b for b in blockers)
    assert not any("warn-notice — correction" in b for b in blockers)


def test_surface_decision_excludes_synthetic_offline_outcomes_from_genuine(net_vault):
    """`genuine` filters on the literal `"synthetic_offline"` key and `is
    not True`: a wrong key never matches (everything stays "genuine") and
    `is not False` also keeps a real synthetic row in — either way the
    synthetic outage leaks into the reported unreachable list."""
    real = _outcome("lifecycle", "vault", Result.UNREACHABLE, "outage — real")
    synthetic = _outcome(
        "lifecycle",
        "vault",
        Result.UNREACHABLE,
        "outage — network disabled",
        synthetic_offline=True,
    )
    code, unreachable = verify.surface_decision("commit", [real, synthetic], {})
    assert code == 3
    assert len(unreachable) == 1
    assert "outage — real" in unreachable[0]


def test_network_outcomes_forwards_vault_root_and_detection_date_to_check_update_notice(
    net_vault, monkeypatch
):
    seen = {}

    def record(vault, entry, date):
        seen["vault"] = vault
        seen["date"] = date
        return checks.Outcome("update-notice", entry["id"], Result.MATCHED, "matched")

    monkeypatch.setattr(checks, "check_update_notice", record)
    entry = {"id": "smith2020", "DOI": "10.1000/xyz"}
    verify._network_outcomes(net_vault, entry, "2026-09-07", None)
    assert seen == {"vault": net_vault, "date": "2026-09-07"}


def test_network_outcomes_forwards_detection_date_to_the_rw_leg(net_vault, monkeypatch):
    monkeypatch.setattr(
        checks,
        "check_update_notice",
        lambda vault, entry, date: checks.Outcome(
            "update-notice", entry["id"], Result.MATCHED, "matched"
        ),
    )
    entry = {"id": "smith2020", "DOI": "10.1000/xyz"}
    lookup = {
        "doi": {"10.1000/xyz": [{"type": "Retraction", "notice_date": "2026-01-01"}]},
        "pmid": {},
    }
    (outcome,) = verify._network_outcomes(net_vault, entry, "2026-09-07", lookup)
    assert outcome.extra.get("detection_date") == "2026-09-07"


def test_network_outcomes_uses_a_lowercase_doi_to_skip_the_synthetic_outage(
    net_vault, monkeypatch
):
    """`entry.get("DOI") or entry.get("doi")` must check both spellings and
    take the true one: a lowercase-only `doi`, with `and` instead of `or` or
    a wrong/dropped key on the "doi" side, would wrongly file the synthetic
    discovery-outage instead of running the real check."""
    seen = []

    def record(vault, entry, date):
        seen.append(entry)
        return checks.Outcome("update-notice", entry["id"], Result.MATCHED, "matched")

    monkeypatch.setattr(checks, "check_update_notice", record)
    entry = {"id": "x2020", "_discovery_unreachable": True, "doi": "10.1/found"}
    (outcome,) = verify._network_outcomes(net_vault, entry, "2026-09-07", None)
    assert seen == [entry]
    assert outcome.result is Result.MATCHED


def test_verify_state_rollback_forwards_the_real_arguments_on_manifest_failure(
    net_vault, monkeypatch, tmp_path
):
    """A manifest-audit failure rolls back with the real vault, live
    snapshot and outputs — not a dropped or `None` argument — and re-raises
    the original error chained, naming the rollback failure too."""
    _isolate_network_verify(
        monkeypatch,
        [_outcome("update-notice", "smith2020", Result.UNMATCHED, "retracted — x")],
    )
    manifest = tmp_path.parent / f"{tmp_path.name}-changed.manifest"
    primary = gitstate.GitStateError("manifest audit failed")

    def fail_audit(*_args, **_kwargs):
        raise primary

    monkeypatch.setattr(gitstate, "audit_and_write_manifest", fail_audit)
    seen = {}

    def record_rollback(vault, live, outputs):
        seen["vault"] = vault
        seen["live"] = live
        seen["outputs"] = outputs
        raise gitstate.GitStateError("rollback also failed")

    monkeypatch.setattr(gitstate, "rollback_outputs", record_rollback)
    with pytest.raises(
        gitstate.GitStateError, match="manifest audit failed; rollback also failed"
    ):
        verify_state(net_vault, network=True, changed_paths_file=str(manifest))
    assert seen["vault"] == net_vault
    assert seen["outputs"]


def test_verify_state_forwards_the_real_vault_as_repository_root(
    net_vault, monkeypatch
):
    """`_plan_state`'s `repository_root` must be `verify_state`'s own
    `vault`, not a stray `None` (nor the kwarg dropped, which is the same
    thing) — the temporary materialized planning directory `_plan_state`
    itself scans notes from is a different path entirely."""
    seen = []

    def record(repository, base_snapshot, candidate_snapshot):
        seen.append(repository)
        return []

    monkeypatch.setattr(lints, "lint_append_only", record)
    verify_state(net_vault, network=False, detection_date="2026-09-07")
    assert seen == [Path(net_vault)]


def test_verify_state_forwards_git_base_and_candidate_to_resolve_snapshots(
    net_vault, monkeypatch
):
    """`git_base`/`git_candidate` must reach `resolve_snapshots` verbatim —
    a dropped kwarg falls back to that function's own default, which is
    indistinguishable from a stray `None`/`"worktree"` only when the
    caller's real value happens to already be the default."""
    seen = {}
    real_resolve = gitstate.resolve_snapshots

    def record(vault, *, git_base=None, candidate="worktree"):
        seen["git_base"] = git_base
        seen["candidate"] = candidate
        return real_resolve(vault, git_base=git_base, candidate=candidate)

    monkeypatch.setattr(gitstate, "resolve_snapshots", record)
    verify_state(
        net_vault,
        network=False,
        detection_date="2026-09-07",
        git_base="HEAD",
        git_candidate="index",
    )
    assert seen == {"git_base": "HEAD", "candidate": "index"}


def test_verify_state_publishes_the_real_outputs_without_a_manifest(
    net_vault, monkeypatch
):
    """Without a changed-paths manifest, `captured` stays `outputs` itself —
    the value `publish_outputs` receives must be the real captured set, not
    a stray `None`."""
    _isolate_network_verify(
        monkeypatch,
        [_outcome("update-notice", "smith2020", Result.UNMATCHED, "retracted — x")],
    )
    verify_state(net_vault, network=True, commit_projected="snapshot projection")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=net_vault,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()
    changed = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", head],
        cwd=net_vault,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.split()
    assert "literature/smith2020.md" in changed


def test_file_effects_files_an_update_notice_finding_with_its_own_detection_date(
    net_vault,
):
    """The filed finding's `detection_date` is the outcome's own recorded
    value when it has a notice fingerprint — read through the literal key
    `"detection_date"`, with `_file_effects`'s own `detection_date`
    argument only as the fallback a differing recorded value must never
    fall through to."""
    outcome = _outcome(
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "retracted — retraction",
        **{
            "class": "blocking",
            "type": "retraction",
            "notice_date": "2026-01-01",
            "detection_date": "2020-01-01",
        },
    )
    hashes = {id(outcome): "aa11"}
    _file_effects(net_vault, [outcome], hashes, {}, "2026-09-07")
    (finding,) = [e for e in inbox.open_entries(net_vault) if e.target == "smith2020"]
    assert finding.detection_date == "2020-01-01"
    assert finding.date == "2026-09-07"
    assert finding.notice_date == "2026-01-01"


def test_file_effects_falls_back_to_its_own_detection_date_when_the_outcome_has_none(
    net_vault,
):
    outcome = _outcome(
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "retracted — retraction",
        **{"class": "blocking", "type": "retraction", "notice_date": "2026-01-01"},
    )
    hashes = {id(outcome): "aa11"}
    _file_effects(net_vault, [outcome], hashes, {}, "2026-09-07")
    (finding,) = [e for e in inbox.open_entries(net_vault) if e.target == "smith2020"]
    assert finding.detection_date == "2026-09-07"


def test_file_effects_files_a_warn_notice_finding_with_its_own_detection_date(
    net_vault,
):
    outcome = _outcome(
        "update-notice",
        "gone2019",
        Result.MATCHED,
        "matched",
        warn_notices=[
            {
                "type": "correction",
                "notice_date": "2026-02-01",
                "detection_date": "2020-02-02",
            }
        ],
    )
    hashes = {id(outcome): "bb22"}
    warning_effective = {(id(outcome), 0): True}
    _file_effects(net_vault, [outcome], hashes, warning_effective, "2026-09-07")
    (finding,) = [e for e in inbox.open_entries(net_vault) if e.target == "gone2019"]
    assert finding.detection_date == "2020-02-02"
    assert finding.notice_date == "2026-02-01"
    assert finding.date == "2026-09-07"


def test_file_effects_falls_back_to_its_own_detection_date_for_a_warn_notice(
    net_vault,
):
    outcome = _outcome(
        "update-notice",
        "gone2019",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction", "notice_date": "2026-02-01"}],
    )
    hashes = {id(outcome): "bb22"}
    warning_effective = {(id(outcome), 0): True}
    _file_effects(net_vault, [outcome], hashes, warning_effective, "2026-09-07")
    (finding,) = [e for e in inbox.open_entries(net_vault) if e.target == "gone2019"]
    assert finding.detection_date == "2026-09-07"


def test_file_effects_files_the_real_target_kind_not_the_append_entry_default(
    net_vault,
):
    """`target_kind=outcome.target_kind` is load-bearing: dropping it falls
    back to `append_entry`'s own `"identifier"` default, which is wrong for
    a repo-path outcome like `append-only`'s."""
    outcome = _outcome(
        "append-only", "log/2026-08-16.md", Result.UNMATCHED, "drift — file"
    )
    hashes = {id(outcome): "cc33"}
    _file_effects(net_vault, [outcome], hashes, {}, "2026-09-07")
    (finding,) = [e for e in inbox.open_entries(net_vault) if e.check == "append-only"]
    assert finding.target_kind == "repo-path"


def test_file_effects_does_not_refile_an_open_warn_notice_finding(net_vault):
    """The warn branch's own dedup key must use the literal `"warn"` class:
    a wrong-cased or mangled copy never matches an already-open finding's
    real `notice_class`, so a second run would refile it."""
    outcome = _outcome(
        "update-notice",
        "gone2019",
        Result.MATCHED,
        "matched",
        warn_notices=[{"type": "correction", "notice_date": "2026-02-01"}],
    )
    hashes = {id(outcome): "bb22"}
    warning_effective = {(id(outcome), 0): True}
    _file_effects(net_vault, [outcome], hashes, warning_effective, "2026-09-07")
    _file_effects(net_vault, [outcome], hashes, warning_effective, "2026-09-07")
    findings = [e for e in inbox.open_entries(net_vault) if e.target == "gone2019"]
    assert len(findings) == 1


def test_file_effects_continues_past_an_ineffective_warning_to_a_later_one(net_vault):
    """Two warnings on one outcome, the first ineffective: `continue` must
    move on to the second, not `break` the whole per-outcome walk."""
    outcome = _outcome(
        "update-notice",
        "gone2019",
        Result.MATCHED,
        "matched",
        warn_notices=[
            {"type": "correction", "notice_date": "2026-02-01"},
            {"type": "erratum", "notice_date": "2026-03-01"},
        ],
    )
    hashes = {id(outcome): "bb22"}
    warning_effective = {(id(outcome), 0): False, (id(outcome), 1): True}
    _file_effects(net_vault, [outcome], hashes, warning_effective, "2026-09-07")
    findings = [e for e in inbox.open_entries(net_vault) if e.target == "gone2019"]
    assert any(f.notice_type == "erratum" for f in findings)
    assert not any(f.notice_type == "correction" for f in findings)


def test_file_effects_deduplicates_two_identical_warn_notices_in_one_call(net_vault):
    """`open_keys.add(key)` must add the real composite key, not a stray
    `None` every duplicate would equally match — two identical warnings in
    one call must file only once."""
    outcome = _outcome(
        "update-notice",
        "gone2019",
        Result.MATCHED,
        "matched",
        warn_notices=[
            {"type": "correction", "notice_date": "2026-02-01"},
            {"type": "correction", "notice_date": "2026-02-01"},
        ],
    )
    hashes = {id(outcome): "bb22"}
    warning_effective = {(id(outcome), 0): True, (id(outcome), 1): True}
    _file_effects(net_vault, [outcome], hashes, warning_effective, "2026-09-07")
    findings = [e for e in inbox.open_entries(net_vault) if e.target == "gone2019"]
    assert len(findings) == 1


def test_file_effects_files_two_distinct_warn_notices_independently(net_vault):
    """The dedup `key` must be the real composite tuple, not a stray `None`
    every warning would equally match — two genuinely distinct warnings in
    one call must both file."""
    outcome = _outcome(
        "update-notice",
        "gone2019",
        Result.MATCHED,
        "matched",
        warn_notices=[
            {"type": "correction", "notice_date": "2026-02-01"},
            {"type": "erratum", "notice_date": "2026-03-01"},
        ],
    )
    hashes = {id(outcome): "bb22"}
    warning_effective = {(id(outcome), 0): True, (id(outcome), 1): True}
    _file_effects(net_vault, [outcome], hashes, warning_effective, "2026-09-07")
    findings = [e for e in inbox.open_entries(net_vault) if e.target == "gone2019"]
    assert len(findings) == 2


def test_file_effects_files_a_warn_notice_finding_with_the_real_target_kind(
    net_vault,
):
    """`target_kind=outcome.target_kind` is load-bearing in the warn branch
    too (mirrors the primary branch's own test): a repo-path-targeted
    outcome carrying a warn notice must file that notice's finding with
    `target_kind="repo-path"`, not `append_entry`'s own `"identifier"`
    default. `update-notice` is the only check a notice fingerprint is
    valid for, so the repo-path target is built directly rather than
    through `_outcome`'s `append-only`-only wrapping."""
    outcome = checks.Outcome(
        "update-notice",
        RepoPath(os.fsencode("log/2026-08-16.md")),
        Result.MATCHED,
        "matched",
        {"warn_notices": [{"type": "correction", "notice_date": "2026-02-01"}]},
    )
    hashes = {id(outcome): "cc33"}
    warning_effective = {(id(outcome), 0): True}
    _file_effects(net_vault, [outcome], hashes, warning_effective, "2026-09-07")
    (finding,) = [
        e for e in inbox.open_entries(net_vault) if e.notice_type == "correction"
    ]
    assert finding.target_kind == "repo-path"


def test_file_effects_continues_past_a_non_string_warning_type_to_a_later_one(
    net_vault,
):
    """A second `continue` guards the walk: a warning whose `type` is not a
    string (no `"type"` key at all, here) must not stop the loop — a
    `break` there would silently drop every later, well-formed warning."""
    outcome = _outcome(
        "update-notice",
        "gone2019",
        Result.MATCHED,
        "matched",
        warn_notices=[
            {"notice_date": "2026-01-01"},
            {"type": "erratum", "notice_date": "2026-03-01"},
        ],
    )
    hashes = {id(outcome): "bb22"}
    warning_effective = {(id(outcome), 0): True, (id(outcome), 1): True}
    _file_effects(net_vault, [outcome], hashes, warning_effective, "2026-09-07")
    findings = [e for e in inbox.open_entries(net_vault) if e.target == "gone2019"]
    assert any(f.notice_type == "erratum" for f in findings)
    assert not any(f.notice_class == "warn" and f.notice_type is None for f in findings)


def test_file_effects_deduplicates_two_identical_primary_findings_in_one_call(
    net_vault,
):
    """The primary branch's own dedup key must use the real composite
    tuple, not a stray `None` every duplicate would equally match — two
    Outcomes with an identical check/target/result/hash in one call must
    file only once."""
    outcome_a = _outcome(
        "update-notice", "gone2019", Result.UNMATCHED, "retracted — retraction"
    )
    outcome_b = _outcome(
        "update-notice", "gone2019", Result.UNMATCHED, "retracted — retraction"
    )
    hashes = {id(outcome_a): "dd44", id(outcome_b): "dd44"}
    _file_effects(net_vault, [outcome_a, outcome_b], hashes, {}, "2026-09-07")
    findings = [e for e in inbox.open_entries(net_vault) if e.target == "gone2019"]
    assert len(findings) == 1


def test_network_outcomes_uses_an_uppercase_doi_to_skip_the_synthetic_outage(
    net_vault, monkeypatch
):
    """The "DOI" side of the same check, isolated the same way — a wrong or
    dropped key on the "DOI" side must not fall back to a stray lowercase-
    only lookup."""
    seen = []

    def record(vault, entry, date):
        seen.append(entry)
        return checks.Outcome("update-notice", entry["id"], Result.MATCHED, "matched")

    monkeypatch.setattr(checks, "check_update_notice", record)
    entry = {"id": "y2020", "_discovery_unreachable": True, "DOI": "10.1/upper"}
    (outcome,) = verify._network_outcomes(net_vault, entry, "2026-09-07", None)
    assert seen == [entry]
    assert outcome.result is Result.MATCHED
