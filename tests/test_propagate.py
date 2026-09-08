import datetime
import hashlib
import json

from research_vault import Result, propagate, zotero
from research_vault.outcome import Outcome
from tests.fakes import ITEM, FakeZotero, canned_item


def _seed(vault):
    (vault / "literatures" / "old2020.md").write_text(
        '---\ntype: "literature"\nzotero-server-id: "S"\nzotero-item-key: "E352DFS8"\n'
        'zotero-item-version: 1\ncitationKey: "old2020"\nattachments:\nfulltext:\n---\n'
    )
    (vault / "projects" / "brief").mkdir(parents=True)
    (vault / "projects" / "brief" / "draft.md").write_text(
        '---\ntype: "project"\n---\nSee [@old2020, p. 3] and [@old2020] and [[old2020]] and [[old2020#^c-1]] and [[old2020|alias]].\n'
    )
    (vault / "wiki" / "sources").mkdir(parents=True)
    (vault / "wiki" / "sources" / "A.md").write_text(
        "---\ntype: source\n---\n[[old2020]] and [[older2020]]\n"
    )
    (vault / "wiki" / "sources" / "B.md").write_text(
        "---\ntype: source\n---\nnames nothing\n"
    )


def _note(item_key, citation_key):
    return (
        f'---\ntype: "literature"\nzotero-server-id: "S"\nzotero-item-key: "{item_key}"\n'
        f'zotero-item-version: 1\ncitationKey: "{citation_key}"\nattachments:\nfulltext:\n---\n'
    )


def _zotero(monkeypatch, citation_key="new2020", server_id="S"):
    """A fake whose item E352DFS8 carries ``citation_key`` live — what every
    mapping is verified against."""
    fake = FakeZotero(server_id=server_id)
    canned_item(
        fake, item={**ITEM, "data": {**ITEM["data"], "citationKey": citation_key}}
    )
    return fake.install(zotero.ZoteroClient(), monkeypatch)


# A tuple of pairs, not the brief's dict literal: ruff's `B` set (B006) refuses
# a mutable default argument. `now` pins an operation id where a test needs two.
def _planned(vault, client, mapping=(("old2020", "new2020"),), now=None):
    planned, outcomes = propagate.plan(vault, client, dict(mapping), now=now)
    assert planned is not None, outcomes
    return planned, propagate.write_plan(vault, planned), propagate.plan_sha256(planned)


def test_plan_refuses_a_mapping_zotero_does_not_carry(tmp_vault, monkeypatch):
    """A typo in --map never becomes a rename: the note's item must carry the new name live."""
    _seed(tmp_vault)
    planned, outcomes = propagate.plan(
        tmp_vault, _zotero(monkeypatch, "jakesch.etal2023a"), {"old2020": "wrong2020"}
    )
    assert planned is None
    assert outcomes[0].reason == (
        "mismatch — item E352DFS8 carries citation key 'jakesch.etal2023a', "
        "not 'wrong2020'"
    )
    assert (tmp_vault / "literatures" / "old2020.md").is_file()


def test_apply_verifies_again_and_renames_nothing_on_an_outage(tmp_vault, monkeypatch):
    _seed(tmp_vault)
    _, path, digest = _planned(tmp_vault, _zotero(monkeypatch))
    # A fresh client, not backed by the fake: the socket guard makes it an outage.
    (refused,) = propagate.apply(tmp_vault, zotero.ZoteroClient(), path, digest)
    assert refused.result is Result.UNREACHABLE
    assert (tmp_vault / "literatures" / "old2020.md").is_file()
    assert (
        "[@old2020, p. 3]"
        in (tmp_vault / "projects" / "brief" / "draft.md").read_text()
    )


def test_plan_refuses_the_wrong_database_before_any_rename(tmp_vault, monkeypatch):
    """The verification read sends the tuple's server id, so a Zotero that is
    not the one the note recorded answers 412 — database-changed, never a
    rename and never an outage."""
    _seed(tmp_vault)
    planned, (refused,) = propagate.plan(
        tmp_vault, _zotero(monkeypatch, server_id="OTHER"), {"old2020": "new2020"}
    )
    assert planned is None
    assert refused.result is Result.UNMATCHED
    assert refused.target == "old2020"
    assert refused.reason.startswith("database-changed — ")
    assert (tmp_vault / "literatures" / "old2020.md").is_file()


def test_plan_lists_the_mapping_the_item_key_and_the_hashed_surfaces(
    tmp_vault, monkeypatch
):
    _seed(tmp_vault)
    planned, path, digest = _planned(tmp_vault, _zotero(monkeypatch))
    assert planned.mapping == {"old2020": "new2020"}
    assert planned.item_keys == {"old2020": "E352DFS8"}
    assert [s.path for s in planned.surfaces] == [
        "projects/brief/draft.md",
        "wiki/sources/A.md",
    ]
    draft = (tmp_vault / "projects" / "brief" / "draft.md").read_bytes()
    assert planned.surfaces[0].sha256 == hashlib.sha256(draft).hexdigest()
    assert (
        path
        == tmp_vault / ".research-vault" / "propagate" / f"{planned.operation_id}.json"
    )
    assert propagate.read_plan(path) == planned
    assert digest == hashlib.sha256(path.read_bytes()).hexdigest()
    assert json.loads(path.read_text())["schema"] == "research-vault.propagation.v1"


def test_plan_refuses_a_missing_note_and_never_reads_an_outage_as_nothing_to_do(
    tmp_vault, monkeypatch
):
    planned, outcomes = propagate.plan(
        tmp_vault, _zotero(monkeypatch), {"ghost2020": "new2020"}
    )
    assert planned is None
    assert outcomes[0].result is Result.UNMATCHED
    assert outcomes[0].reason.startswith("schema-violation")
    monkeypatch.setattr(
        propagate.lifecycle,
        "lint_lifecycle",
        lambda vault, client: [
            Outcome("lifecycle", "vault", Result.UNREACHABLE, "outage — down")
        ],
    )
    planned, outcomes = propagate.plan(tmp_vault, object(), None)
    assert planned is None
    # an outage is not "nothing to propagate"
    assert outcomes[0].result is Result.UNREACHABLE


def test_rewrite_surfaces_touches_every_citation_and_wikilink_shape(tmp_vault):
    _seed(tmp_vault)
    changed = propagate.rewrite_surfaces(tmp_vault, "old2020", "new2020")
    assert changed == ["projects/brief/draft.md", "wiki/sources/A.md"]
    draft = (tmp_vault / "projects" / "brief" / "draft.md").read_text()
    assert draft.endswith(
        "See [@new2020, p. 3] and [@new2020] and [[new2020]] and [[new2020#^c-1]] and [[new2020|alias]].\n"
    )
    assert "[[older2020]]" in (tmp_vault / "wiki" / "sources" / "A.md").read_text()


def test_apply_refuses_when_the_vault_moved_since_planning(tmp_vault, monkeypatch):
    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    _, path, digest = _planned(tmp_vault, client)
    (tmp_vault / "wiki" / "sources" / "B.md").write_text(
        "---\ntype: source\n---\n[[old2020]] now\n"
    )
    (refused,) = propagate.apply(tmp_vault, client, path, digest)
    assert refused.result is Result.UNMATCHED
    assert refused.reason.startswith("mismatch — plan changed")
    assert (tmp_vault / "literatures" / "old2020.md").is_file()
    assert not (tmp_vault / "system" / "propagations").exists()
    (wrong,) = propagate.apply(tmp_vault, client, path, "0" * 64)
    assert wrong.result is Result.UNMATCHED
    assert wrong.reason.startswith("mismatch — approved hash")


def test_apply_renames_rewrites_recaptures_and_records_the_plan(tmp_vault, monkeypatch):
    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    planned, path, digest = _planned(tmp_vault, client)
    calls = []
    monkeypatch.setattr(
        propagate.capture,
        "capture",
        lambda vault, client, keys, **kw: calls.append(list(keys)) or [],
    )
    outcomes = propagate.apply(tmp_vault, client, path, digest)
    assert outcomes[0].check == "propagation"
    assert outcomes[0].result is Result.MATCHED
    assert "projects/brief/draft.md" in outcomes[0].reason
    assert (tmp_vault / "literatures" / "new2020.md").is_file()
    assert not (tmp_vault / "literatures" / "old2020.md").exists()
    assert calls == [["E352DFS8"]]
    record = json.loads(
        (
            tmp_vault / "system" / "propagations" / f"{planned.operation_id}.json"
        ).read_text()
    )
    assert record["mapping"] == {"old2020": "new2020"}
    assert record["approved_plan_sha256"] == digest
    assert record["applied_at"]
    assert record["surfaces"][0]["path"] == "projects/brief/draft.md"
    assert propagate.read_records(tmp_vault)[0].operation_id == planned.operation_id


def test_lint_reports_residue_and_is_quiet_when_clean(tmp_vault, monkeypatch):
    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    (skipped,) = propagate.lint_propagation(tmp_vault)
    assert skipped.result is Result.SKIPPED
    _, path, digest = _planned(tmp_vault, client)
    propagate.apply(tmp_vault, client, path, digest)
    (clean,) = propagate.lint_propagation(tmp_vault)
    assert clean.result is Result.MATCHED
    (tmp_vault / "projects" / "brief" / "late.md").write_text(
        '---\ntype: "project"\n---\n[@old2020]\n'
    )
    (tmp_vault / "literatures" / "old2020.md").write_text(
        '---\ntype: "literature"\n---\n'
    )
    stale = propagate.lint_propagation(tmp_vault)
    assert {o.target for o in stale} == {
        "path-bytes:projects/brief/late.md",
        "path-bytes:literatures/old2020.md",
    }
    assert all(
        o.reason.startswith(
            "stale-key — names old2020, mapped to new2020 by propagate-"
        )
        for o in stale
    )


def test_cli_plans_then_applies_only_against_the_printed_hash(
    tmp_vault, monkeypatch, capsys
):
    import research_vault.__main__ as cli

    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    # The fake installs per instance; the CLI builds its own client.
    monkeypatch.setattr(cli, "ZoteroClient", lambda base=None: client)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    assert (
        cli.main(["propagate", "--vault", str(tmp_vault), "--map", "old2020=new2020"])
        == 0
    )
    # `line`, not the brief's `l`: ruff's default E741 refuses the ambiguous name.
    line = next(
        line
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("apply with:")
    )
    words = line.split()
    path, digest = (
        words[words.index("--plan") + 1],
        words[words.index("--approved-plan-sha256") + 1],
    )
    assert (
        cli.main(
            [
                "propagate",
                "--vault",
                str(tmp_vault),
                "--plan",
                path,
                "--approved-plan-sha256",
                "0" * 64,
            ]
        )
        == 1
    )
    assert (tmp_vault / "literatures" / "old2020.md").is_file()
    assert (
        cli.main(
            [
                "propagate",
                "--vault",
                str(tmp_vault),
                "--plan",
                path,
                "--approved-plan-sha256",
                digest,
            ]
        )
        == 0
    )
    assert (tmp_vault / "literatures" / "new2020.md").is_file()


# --- deviations from the printed module, each pinned (see the task report) -----


def test_lint_follows_a_key_renamed_back_and_reports_only_the_latest_mapping(
    tmp_vault, monkeypatch
):
    """A later record supersedes an earlier one: after a→b then b→a, a surface
    naming `a` is current, and one naming `b` is the residue. Without the fold,
    the first record would flag every `a` forever and `propagation` closes
    `commit`."""
    _seed(tmp_vault)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    first = datetime.datetime(2026, 9, 8, 10, 15, tzinfo=datetime.UTC)
    forward = _zotero(monkeypatch)
    _, path, digest = _planned(tmp_vault, forward, now=first)
    propagate.apply(tmp_vault, forward, path, digest)
    # The recapture is monkeypatched away; stand in for the one that re-renders
    # the note under its new key, which is what the second plan resolves by.
    (tmp_vault / "literatures" / "new2020.md").write_text(_note("E352DFS8", "new2020"))
    backward = _zotero(monkeypatch, "old2020")  # Zotero re-keyed the item back
    back, back_path, back_digest = _planned(
        tmp_vault,
        backward,
        (("new2020", "old2020"),),
        now=first + datetime.timedelta(seconds=1),
    )
    propagate.apply(tmp_vault, backward, back_path, back_digest)
    assert (tmp_vault / "literatures" / "old2020.md").is_file()
    assert (
        "[@old2020, p. 3]"
        in (tmp_vault / "projects" / "brief" / "draft.md").read_text()
    )
    (clean,) = propagate.lint_propagation(tmp_vault)
    assert clean.result is Result.MATCHED, clean
    (tmp_vault / "projects" / "brief" / "late.md").write_text(
        '---\ntype: "project"\n---\n[@new2020]\n'
    )
    (stale,) = propagate.lint_propagation(tmp_vault)
    assert stale.target == "path-bytes:projects/brief/late.md"
    assert stale.reason == (
        f"stale-key — names new2020, mapped to old2020 by {back.operation_id}"
    )


def test_plan_refuses_to_rename_over_an_existing_note(tmp_vault, monkeypatch):
    """ADR 0003: no transition deletes a literature note, and a POSIX rename
    over an existing file replaces it silently."""
    _seed(tmp_vault)
    (tmp_vault / "literatures" / "new2020.md").write_text(
        '---\ntype: "literature"\n---\n'
    )
    planned, (refused,) = propagate.plan(
        tmp_vault, _zotero(monkeypatch), {"old2020": "new2020"}
    )
    assert planned is None
    assert refused.result is Result.UNMATCHED
    assert refused.reason == (
        "schema-violation — literatures/new2020.md already exists; nothing is renamed over it"
    )


# --- fix round 1 ---------------------------------------------------------------


def test_a_partial_apply_can_be_re_run_because_plan_finds_the_note_by_its_recorded_key(
    tmp_vault, monkeypatch
):
    """Finding 1: after an outage during the recapture the note sits at
    literatures/new2020.md still recording citationKey: old2020. The captured
    set is the recorded key, not the filename (decision 08), so a re-run plans,
    treats the note as already at its target, and still rewrites and records."""
    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    # The recapture is what re-renders the note under its new key; with it
    # stubbed, proof that it ran is the assertion, not the note's content.
    calls = []
    monkeypatch.setattr(
        propagate.capture,
        "capture",
        lambda vault, client, keys, **kw: calls.append(list(keys)) or [],
    )
    (tmp_vault / "literatures" / "old2020.md").rename(
        tmp_vault / "literatures" / "new2020.md"
    )
    planned, path, digest = _planned(tmp_vault, client)
    assert planned.item_keys == {"old2020": "E352DFS8"}
    (matched,) = propagate.apply(tmp_vault, client, path, digest)
    assert matched.result is Result.MATCHED
    assert calls == [["E352DFS8"]]
    assert (tmp_vault / "literatures" / "new2020.md").is_file()
    assert not (tmp_vault / "literatures" / "old2020.md").exists()
    assert (
        "[@new2020, p. 3]"
        in (tmp_vault / "projects" / "brief" / "draft.md").read_text()
    )
    assert propagate.read_records(tmp_vault)[0].mapping == {"old2020": "new2020"}


def test_plan_resolves_the_note_wherever_its_recorded_key_puts_it_and_refuses_two(
    tmp_vault, monkeypatch
):
    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    literatures = tmp_vault / "literatures"
    (literatures / "old2020.md").rename(literatures / "moved.md")
    _, path, digest = _planned(tmp_vault, client)
    propagate.apply(tmp_vault, client, path, digest)
    assert (literatures / "new2020.md").is_file()
    assert not (literatures / "moved.md").exists()
    # Two notes recording one key is a refusal, never a guess.
    (literatures / "a.md").write_text(_note("E352DFS8", "twice2020"))
    (literatures / "b.md").write_text(_note("E352DFS8", "twice2020"))
    planned, (refused,) = propagate.plan(tmp_vault, client, {"twice2020": "x2020"})
    assert planned is None
    assert refused.reason == (
        "schema-violation — 2 notes record citationKey twice2020: a.md, b.md"
    )
    # A note at the old name with no tuple keeps the brief's own refusal.
    (literatures / "bare2020.md").write_text('---\ntype: "literature"\n---\n')
    planned, (refused,) = propagate.plan(tmp_vault, client, {"bare2020": "x2020"})
    assert planned is None
    assert refused.reason == "schema-violation — note carries no provenance tuple"
    # A note at the old name recording another key says which, rather than
    # claiming it has no tuple: the shape a partial apply leaves when the
    # mapping is read off the filename instead of the linter.
    planned, (refused,) = propagate.plan(tmp_vault, client, {"new2020": "y2020"})
    assert planned is None
    assert refused.reason == (
        "schema-violation — literatures/new2020.md records citationKey old2020, "
        "not new2020"
    )


def test_lint_lets_a_freed_name_go_when_a_different_item_now_holds_it(
    tmp_vault, monkeypatch
):
    """Finding 2: after old2020→new2020, a fresh Zotero item minted under the
    freed key and captured normally makes literatures/old2020.md and every
    [@old2020] current again — the item key is identity, the name only a name.
    The same item back under the retired name is still residue."""
    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    _, path, digest = _planned(tmp_vault, client)
    propagate.apply(tmp_vault, client, path, digest)
    (tmp_vault / "projects" / "brief" / "late.md").write_text(
        '---\ntype: "project"\n---\n[@old2020]\n'
    )
    (tmp_vault / "literatures" / "old2020.md").write_text(_note("FRESH001", "old2020"))
    (clean,) = propagate.lint_propagation(tmp_vault)
    assert clean.result is Result.MATCHED, clean
    (tmp_vault / "literatures" / "old2020.md").write_text(_note("E352DFS8", "old2020"))
    stale = propagate.lint_propagation(tmp_vault)
    assert {o.target for o in stale} == {
        "path-bytes:literatures/old2020.md",
        "path-bytes:projects/brief/late.md",
    }
