import datetime
import hashlib
import json
import os

import pytest

from research_vault import Result, propagate, zotero
from research_vault.outcome import Outcome
from tests.fakes import ITEM, FakeZotero, canned_item


def _seed(vault):
    (vault / "literature" / "old2020.md").write_text(
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
    assert (tmp_vault / "literature" / "old2020.md").is_file()


def test_apply_verifies_again_and_renames_nothing_on_an_outage(tmp_vault, monkeypatch):
    _seed(tmp_vault)
    _, path, digest = _planned(tmp_vault, _zotero(monkeypatch))
    # A fresh client, not backed by the fake: the socket guard makes it an outage.
    (refused,) = propagate.apply(tmp_vault, zotero.ZoteroClient(), path, digest)
    assert refused.result is Result.UNREACHABLE
    assert (tmp_vault / "literature" / "old2020.md").is_file()
    assert (
        "[@old2020, p. 3]"
        in (tmp_vault / "projects" / "brief" / "draft.md").read_text()
    )


def test_apply_refuses_a_key_that_moved_again_between_plan_and_apply(
    tmp_vault, monkeypatch
):
    """The property the second read exists for: a citation key that moved in
    Zotero after the plan was approved is refused before the first rename."""
    _seed(tmp_vault)
    _, path, digest = _planned(tmp_vault, _zotero(monkeypatch))
    (refused,) = propagate.apply(
        tmp_vault, _zotero(monkeypatch, "newer2020"), path, digest
    )
    assert refused.result is Result.UNMATCHED
    assert refused.target == "old2020"
    assert refused.reason == (
        "mismatch — item E352DFS8 carries citation key 'newer2020', not 'new2020'"
    )
    assert (tmp_vault / "literature" / "old2020.md").is_file()
    assert (
        (tmp_vault / "projects" / "brief" / "draft.md")
        .read_text()
        .endswith(
            "See [@old2020, p. 3] and [@old2020] and [[old2020]] and [[old2020#^c-1]] and [[old2020|alias]].\n"
        )
    )
    assert not (tmp_vault / "system" / "propagations").exists()


def test_plan_refuses_without_a_client_and_writes_nothing(tmp_vault):
    _seed(tmp_vault)
    for mapping in ({"old2020": "new2020"}, None):
        planned, (refused,) = propagate.plan(tmp_vault, None, mapping)
        assert planned is None
        assert refused.result is Result.UNMATCHED
        assert refused.target == "system/propagations"
        assert refused.reason == (
            "schema-violation — no Zotero client to verify the mapping against"
        )
    assert not (tmp_vault / ".research-vault").exists()
    assert not (tmp_vault / "system" / "propagations").exists()
    assert (tmp_vault / "literature" / "old2020.md").is_file()


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
    assert (tmp_vault / "literature" / "old2020.md").is_file()


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
    assert (tmp_vault / "literature" / "old2020.md").is_file()
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
    assert (tmp_vault / "literature" / "new2020.md").is_file()
    assert not (tmp_vault / "literature" / "old2020.md").exists()
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
    (tmp_vault / "literature" / "old2020.md").write_text(
        '---\ntype: "literature"\n---\n'
    )
    stale = propagate.lint_propagation(tmp_vault)
    assert {o.target for o in stale} == {
        "path-bytes:projects/brief/late.md",
        "path-bytes:literature/old2020.md",
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
    assert words[words.index("--base") + 1] == zotero.base_for(
        tmp_vault, None, strict=True
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
    assert (tmp_vault / "literature" / "old2020.md").is_file()
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
    assert (tmp_vault / "literature" / "new2020.md").is_file()


# --- deviations from the printed module, each pinned --------------------------


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
    (tmp_vault / "literature" / "new2020.md").write_text(_note("E352DFS8", "new2020"))
    backward = _zotero(monkeypatch, "old2020")  # Zotero re-keyed the item back
    back, back_path, back_digest = _planned(
        tmp_vault,
        backward,
        (("new2020", "old2020"),),
        now=first + datetime.timedelta(seconds=1),
    )
    propagate.apply(tmp_vault, backward, back_path, back_digest)
    assert (tmp_vault / "literature" / "old2020.md").is_file()
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
    (tmp_vault / "literature" / "new2020.md").write_text(
        '---\ntype: "literature"\n---\n'
    )
    planned, (refused,) = propagate.plan(
        tmp_vault, _zotero(monkeypatch), {"old2020": "new2020"}
    )
    assert planned is None
    assert refused.result is Result.UNMATCHED
    assert refused.reason == (
        "schema-violation — literature/new2020.md already exists; nothing is renamed over it"
    )


# --- the recorded key is the note's identity, not its filename ----------------


def test_a_partial_apply_can_be_re_run_because_plan_finds_the_note_by_its_recorded_key(
    tmp_vault, monkeypatch
):
    """After an outage during the recapture the note sits at
    literature/new2020.md still recording citationKey: old2020. The captured
    set is the recorded key, not the filename (decision 08), so a re-run plans,
    treats the note as already at its target, and still rewrites, recaptures
    and records."""
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
    (tmp_vault / "literature" / "old2020.md").rename(
        tmp_vault / "literature" / "new2020.md"
    )
    planned, path, digest = _planned(tmp_vault, client)
    assert planned.item_keys == {"old2020": "E352DFS8"}
    (matched,) = propagate.apply(tmp_vault, client, path, digest)
    assert matched.result is Result.MATCHED
    assert calls == [["E352DFS8"]]
    assert (tmp_vault / "literature" / "new2020.md").is_file()
    assert not (tmp_vault / "literature" / "old2020.md").exists()
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
    literature = tmp_vault / "literature"
    (literature / "old2020.md").rename(literature / "moved.md")
    _, path, digest = _planned(tmp_vault, client)
    propagate.apply(tmp_vault, client, path, digest)
    assert (literature / "new2020.md").is_file()
    assert not (literature / "moved.md").exists()
    # Two notes recording one key is a refusal, never a guess.
    (literature / "a.md").write_text(_note("E352DFS8", "twice2020"))
    (literature / "b.md").write_text(_note("E352DFS8", "twice2020"))
    planned, (refused,) = propagate.plan(tmp_vault, client, {"twice2020": "x2020"})
    assert planned is None
    assert refused.reason == (
        "schema-violation — 2 notes record citationKey twice2020: a.md, b.md"
    )
    # A note at the old name with no tuple keeps the brief's own refusal.
    (literature / "bare2020.md").write_text('---\ntype: "literature"\n---\n')
    planned, (refused,) = propagate.plan(tmp_vault, client, {"bare2020": "x2020"})
    assert planned is None
    assert refused.reason == "schema-violation — note carries no provenance tuple"
    # A note at the old name recording another key says which, rather than
    # claiming it has no tuple: the shape a partial apply leaves when the
    # mapping is read off the filename instead of the linter.
    planned, (refused,) = propagate.plan(tmp_vault, client, {"new2020": "y2020"})
    assert planned is None
    assert refused.reason == (
        "schema-violation — literature/new2020.md records citationKey old2020, "
        "not new2020"
    )


def test_lint_lets_a_freed_name_go_when_a_different_item_now_holds_it(
    tmp_vault, monkeypatch
):
    """Finding 2: after old2020→new2020, a fresh Zotero item minted under the
    freed key and captured normally makes literature/old2020.md and every
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
    (tmp_vault / "literature" / "old2020.md").write_text(_note("FRESH001", "old2020"))
    (clean,) = propagate.lint_propagation(tmp_vault)
    assert clean.result is Result.MATCHED, clean
    (tmp_vault / "literature" / "old2020.md").write_text(_note("E352DFS8", "old2020"))
    stale = propagate.lint_propagation(tmp_vault)
    assert {o.target for o in stale} == {
        "path-bytes:literature/old2020.md",
        "path-bytes:projects/brief/late.md",
    }


# --- boundaries pinned against mutation survivors -----------------------------


def test_canonical_json_is_sorted_two_space_indented_and_keeps_non_ascii():
    """The plan's bytes are what the approval hash names: keys sorted, two
    spaces of indent, non-ASCII kept as is, one trailing newline."""
    assert propagate._canonical({"b": [1, {"z": None, "y": "é"}], "a": "→"}) == (
        '{\n  "a": "→",\n  "b": [\n    1,\n    {\n      "y": "é",\n      "z": null\n    }\n  ]\n}\n'
    )


def test_surfaces_are_every_note_outside_the_skipped_places(tmp_vault):
    """literature/, fulltext/, log/, log.md, the review queue, the
    propagation records, excluded directories and symlinks are not surfaces;
    a project note and a wiki page are."""
    _seed(tmp_vault)
    (tmp_vault / ".raw").mkdir(exist_ok=True)
    (tmp_vault / ".raw" / "a.md").write_text("[@old2020]\n")
    (tmp_vault / "fulltext").mkdir(exist_ok=True)
    (tmp_vault / "fulltext" / "ATT00001.md").write_text("[@old2020]\n")
    (tmp_vault / "log" / "2026-09-07.md").write_text("[@old2020]\n")
    (tmp_vault / "log.md").write_text("[@old2020]\n")
    (tmp_vault / "inbox" / "review-queue.md").write_text("[@old2020]\n")
    (tmp_vault / "system" / "propagations").mkdir(parents=True, exist_ok=True)
    (tmp_vault / "system" / "propagations" / "note.md").write_text("[@old2020]\n")
    (tmp_vault / "wiki" / "link.md").symlink_to(tmp_vault / "wiki" / "sources" / "A.md")
    assert [relative for _path, relative in propagate._surfaces(tmp_vault)] == [
        "projects/brief/draft.md",
        "wiki/sources/A.md",
        "wiki/sources/B.md",
    ]


def _lint_fake(monkeypatch, *, versions, trash, top, server_id="S"):
    fake = FakeZotero(server_id=server_id)
    fake.get("/api/users/0/items?since=0&format=versions", body=versions)
    fake.get("/api/users/0/items/trash?format=versions", body=trash)
    fake.get("/api/users/0/items/top?format=json", body=top)
    return fake.install(zotero.ZoteroClient(), monkeypatch)


def test_mapping_from_linter_takes_re_keys_and_blocks_only_on_vault_rows(
    tmp_vault, monkeypatch
):
    """A re-keyed note becomes a mapping entry; a trashed note is neither a
    mapping nor a block; a vault row blocks only when it is UNMATCHED
    (database-changed) or an outage -- the fresh vault's SKIPPED row does not."""
    assert propagate._mapping_from_linter(tmp_vault, _zotero(monkeypatch)) == ({}, [])
    (tmp_vault / "literature" / "old2020.md").write_text(_note("E352DFS8", "old2020"))
    (tmp_vault / "literature" / "gone2020.md").write_text(_note("TRASHED1", "gone2020"))
    client = _lint_fake(
        monkeypatch,
        versions={"E352DFS8": 1},
        trash={"TRASHED1": 1},
        top=[{"key": "E352DFS8", "data": {"citationKey": "new2020"}}],
    )
    assert propagate._mapping_from_linter(tmp_vault, client) == (
        {"old2020": "new2020"},
        [],
    )
    mapping, blocking = propagate._mapping_from_linter(
        tmp_vault, _zotero(monkeypatch, server_id="Tdoqsn2J4q4h")
    )
    assert mapping == {}
    assert [(o.target, o.result) for o in blocking] == [("vault", Result.UNMATCHED)]
    assert blocking[0].reason.startswith("database-changed")


def _second_item(citation_key):
    return {
        **ITEM,
        "key": "F441KKD2",
        "data": {**ITEM["data"], "key": "F441KKD2", "citationKey": citation_key},
    }


def test_plan_reports_every_refusal_in_a_mapping_not_only_the_first(
    tmp_vault, monkeypatch
):
    """Each entry of a mapping is judged: a missing note, an unsafe new key, a
    name already taken and a key the item does not carry are all reported,
    whichever comes first."""
    _seed(tmp_vault)
    (tmp_vault / "literature" / "other2020.md").write_text(
        _note("F441KKD2", "other2020")
    )
    (tmp_vault / "literature" / "taken2020.md").write_text(
        _note("TAKEN001", "taken2020")
    )
    fake = FakeZotero(server_id="S")
    canned_item(fake, item={**ITEM, "data": {**ITEM["data"], "citationKey": "new2020"}})
    canned_item(fake, item=_second_item("other2020"), children=())
    client = fake.install(zotero.ZoteroClient(), monkeypatch)

    def reasons(mapping):
        planned, outcomes = propagate.plan(tmp_vault, client, mapping)
        assert planned is None
        return [o.reason.split(" — ")[0] for o in outcomes]

    assert reasons({"missing2020": "x2020", "other2020": "wrong2020"}) == [
        "schema-violation",
        "mismatch",
    ]
    assert reasons({"old2020": "bad/key", "other2020": "wrong2020"}) == [
        "schema-violation",
        "mismatch",
    ]
    assert reasons({"old2020": "taken2020", "other2020": "wrong2020"}) == [
        "schema-violation",
        "mismatch",
    ]
    assert reasons({"old2020": "wrong2020", "other2020": "wrong2021"}) == [
        "mismatch",
        "mismatch",
    ]


def _cli(monkeypatch, client):
    import research_vault.__main__ as cli

    bases: list = []

    def build(base=None):
        bases.append(base)
        return client

    monkeypatch.setattr(cli, "ZoteroClient", build)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    return cli, bases


def test_cli_propagate_refuses_malformed_flags_on_stderr_with_exit_2(
    tmp_vault, monkeypatch, capsys
):
    """--plan without its hash (and the reverse), --map beside --plan, and a
    --map pair that is not OLD=NEW with both halves: each is one stderr line
    that starts with the verb's code and names the flag at fault, nothing on
    stdout, exit 2, and no client is built. The branch is the target, not the
    sentence: the code prefix is what every string mutant of the message
    breaks, and the flag name is what tells the branches apart."""
    cli, bases = _cli(monkeypatch, _zotero(monkeypatch))
    vault = str(tmp_vault)
    cases = [
        (["--plan", "p.json"], "--approved-plan-sha256"),
        (["--approved-plan-sha256", "0" * 64], "--approved-plan-sha256"),
        (
            ["--plan", "p.json", "--approved-plan-sha256", "0" * 64, "--map", "a=b"],
            "--map plans",
        ),
        (["--map", "old2020"], "OLD=NEW, not 'old2020'"),
        (["--map", "=new2020"], "OLD=NEW, not '=new2020'"),
        (["--map", "old2020="], "OLD=NEW, not 'old2020='"),
    ]
    for extra, named in cases:
        assert cli.main(["propagate", "--vault", vault, *extra]) == 2
        captured = capsys.readouterr()
        assert captured.out == ""
        assert len(captured.err.splitlines()) == 1
        assert captured.err.startswith("propagate: ")
        assert named in captured.err
    assert bases == []


def test_cli_propagate_splits_each_map_pair_once_and_plans_from_the_linter_without_map(
    tmp_vault, monkeypatch, capsys
):
    """`OLD=NEW=X` maps OLD to `NEW=X` (one split, at the first `=`); with no
    --map at all the mapping comes from the lifecycle linter, and the client
    is built on the resolved base."""
    _seed(tmp_vault)
    cli, bases = _cli(monkeypatch, _zotero(monkeypatch))
    assert (
        cli.main(["propagate", "--vault", str(tmp_vault), "--map", "old2020=new=2020"])
        == 1
    )
    out = capsys.readouterr().out
    assert out.startswith(
        "UNMATCHED old2020 — mismatch — item E352DFS8 carries citation key "
        "'new2020', not 'new=2020'"
    )
    assert bases == [zotero.DEFAULT_BASE]

    # One client answers the linter's three reads AND the item read.
    fake = FakeZotero(server_id="S")
    fake.get("/api/users/0/items?since=0&format=versions", body={"E352DFS8": 1})
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[{"key": "E352DFS8", "data": {"citationKey": "new2020"}}],
    )
    canned_item(fake, item={**ITEM, "data": {**ITEM["data"], "citationKey": "new2020"}})
    cli, _bases = _cli(monkeypatch, fake.install(zotero.ZoteroClient(), monkeypatch))
    assert cli.main(["propagate", "--vault", str(tmp_vault)]) == 0
    assert capsys.readouterr().out.splitlines()[:3] == [
        "rename old2020 → new2020 (item E352DFS8)",
        "rewrite projects/brief/draft.md",
        "rewrite wiki/sources/A.md",
    ]


def test_cli_propagate_shape_check_splits_once_and_leaves_the_halves_to_the_plan(
    tmp_vault, monkeypatch, capsys
):
    """`A==B` and `C==` have an `=` and two non-empty halves at the first
    split, so the flag parser passes them through as A→`=B` and C→`=`;
    whether those are citation keys is the plan's verdict, not exit 2."""
    cli, _bases = _cli(monkeypatch, _zotero(monkeypatch))
    seen = []

    def plan(vault, client, mapping, **kwargs):
        seen.append(mapping)
        return None, []

    monkeypatch.setattr(propagate, "plan", plan)
    argv = ["propagate", "--vault", str(tmp_vault), "--map", "A==B", "--map", "C=="]
    assert cli.main(argv) == 0
    assert seen == [{"A": "=B", "C": "="}]
    assert capsys.readouterr().err == ""


def test_cli_propagate_exit_codes_and_the_hold_it_files(tmp_vault, monkeypatch, capsys):
    """An UNMATCHED apply row is exit 1 and a hold carrying the row's check,
    target, target kind and reason; an outage with nothing UNMATCHED is 3."""
    from research_vault import inbox

    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    planned, path, _digest = _planned(tmp_vault, client)
    cli, _bases = _cli(monkeypatch, client)
    assert (
        cli.main(
            [
                "propagate",
                "--vault",
                str(tmp_vault),
                "--plan",
                str(path),
                "--approved-plan-sha256",
                "0" * 64,
            ]
        )
        == 1
    )
    (held,) = [f for f in inbox.load(tmp_vault) if f.check == "propagation"]
    assert (held.target, held.target_kind, held.result, held.reason) == (
        planned.operation_id,
        "identifier",
        "UNMATCHED",
        "mismatch — approved hash does not name this plan",
    )
    capsys.readouterr()
    outage = zotero.ZoteroClient()  # no fake behind it: the socket guard refuses
    cli, _bases = _cli(monkeypatch, outage)
    assert (
        cli.main(
            [
                "propagate",
                "--vault",
                str(tmp_vault),
                "--plan",
                str(path),
                "--approved-plan-sha256",
                propagate.plan_sha256(planned),
            ]
        )
        == 3
    )
    assert capsys.readouterr().out.startswith("UNREACHABLE old2020 — outage — ")


def test_cli_propagate_holds_a_repo_path_refusal_with_its_target_kind(
    tmp_vault, monkeypatch, capsys
):
    """A surface whose path is not UTF-8 is refused as a repo-path row; the
    hold the CLI files carries that target kind, not the identifier default."""
    from research_vault import inbox

    _seed(tmp_vault)
    (tmp_vault / "wiki" / "sources" / os.fsdecode(b"b\xff.md")).write_text(
        "---\ntype: source\n---\n[@old2020]\n"
    )
    cli, _bases = _cli(monkeypatch, _zotero(monkeypatch))
    assert (
        cli.main(["propagate", "--vault", str(tmp_vault), "--map", "old2020=new2020"])
        == 1
    )
    (held,) = [f for f in inbox.load(tmp_vault) if f.check == "propagation"]
    assert held.target_kind == "repo-path"
    assert held.target.startswith("path-bytes:wiki/sources/b")
    assert (
        held.reason == "schema-violation — surface path is not UTF-8; rename it first"
    )
    capsys.readouterr()


def test_plan_skips_a_quiet_surface_and_keeps_hashing_the_ones_after_it(
    tmp_vault, monkeypatch
):
    _seed(tmp_vault)
    (tmp_vault / "projects" / "a-quiet").mkdir()
    (tmp_vault / "projects" / "a-quiet" / "draft.md").write_text(
        '---\ntype: "project"\n---\nnames nothing\n'
    )
    planned, _path, _digest = _planned(tmp_vault, _zotero(monkeypatch))
    assert [s.path for s in planned.surfaces] == [
        "projects/brief/draft.md",
        "wiki/sources/A.md",
    ]


def test_apply_reports_rewrote_nothing_when_no_surface_names_the_key(
    tmp_vault, monkeypatch
):
    (tmp_vault / "literature" / "old2020.md").write_text(_note("E352DFS8", "old2020"))
    client = _zotero(monkeypatch)
    _planned_plan, path, digest = _planned(tmp_vault, client)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    (outcome,) = propagate.apply(tmp_vault, client, path, digest)
    assert (outcome.target, outcome.result, outcome.reason) == (
        "new2020",
        Result.MATCHED,
        "matched — rewrote nothing",
    )


def test_apply_names_every_rewritten_surface_and_stamps_applied_at_from_now(
    tmp_vault, monkeypatch
):
    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    planned, path, digest = _planned(tmp_vault, client)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    now = datetime.datetime.fromisoformat("2026-09-07T10:00:00.123456+00:00")
    (outcome,) = propagate.apply(tmp_vault, client, path, digest, now=now)
    assert (
        outcome.reason == "matched — rewrote projects/brief/draft.md, wiki/sources/A.md"
    )
    record = json.loads(
        (
            tmp_vault / "system" / "propagations" / f"{planned.operation_id}.json"
        ).read_text()
    )
    assert record["applied_at"] == "2026-09-07T10:00:00+00:00"


def test_apply_creates_the_record_directory_two_levels_deep(tmp_vault, monkeypatch):
    """A vault without `system/` still gets `system/propagations/<id>.json`."""
    import shutil

    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    planned, path, digest = _planned(tmp_vault, client)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    shutil.rmtree(tmp_vault / "system", ignore_errors=True)
    propagate.apply(tmp_vault, client, path, digest)
    record = tmp_vault / "system" / "propagations" / f"{planned.operation_id}.json"
    assert record.is_file()


def test_apply_without_now_stamps_an_aware_utc_instant(tmp_vault, monkeypatch):
    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    planned, path, digest = _planned(tmp_vault, client)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    propagate.apply(tmp_vault, client, path, digest)
    record = json.loads(
        (
            tmp_vault / "system" / "propagations" / f"{planned.operation_id}.json"
        ).read_text()
    )
    applied = datetime.datetime.fromisoformat(record["applied_at"])
    assert applied.tzinfo is not None
    assert applied.microsecond == 0


def test_apply_rows_an_unreadable_plan_with_its_path(tmp_vault, monkeypatch):
    missing = tmp_vault / ".research-vault" / "propagate" / "nowhere.json"
    (outcome,) = propagate.apply(tmp_vault, _zotero(monkeypatch), missing, "0" * 64)
    assert (outcome.check, outcome.target, outcome.result) == (
        "propagation",
        str(missing),
        Result.UNMATCHED,
    )
    assert outcome.reason.startswith("schema-violation — unreadable plan: [Errno 2]")


def test_lint_rows_an_unreadable_record_and_reads_surfaces_byte_tolerantly(
    tmp_vault, monkeypatch
):
    """A corrupt record is one row against the records directory; with sound
    records, a surface carrying a stray byte is still read (surrogateescape)
    and a freed name passed over does not stop the next stale key from being
    reported."""
    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    records = tmp_vault / "system" / "propagations"
    records.mkdir(parents=True, exist_ok=True)
    (records / "propagate-broken.json").write_text("{not json")
    (outcome,) = propagate.lint_propagation(tmp_vault)
    assert (outcome.check, outcome.target, outcome.result) == (
        "propagation",
        "path-bytes:system/propagations",
        Result.UNMATCHED,
    )
    assert outcome.reason.startswith(
        "schema-violation — unreadable propagation record: "
    )
    (records / "propagate-broken.json").unlink()

    _, path, digest = _planned(
        tmp_vault, client, now=datetime.datetime(2026, 9, 7, tzinfo=datetime.UTC)
    )
    propagate.apply(tmp_vault, client, path, digest)
    (tmp_vault / "literature" / "other2020.md").write_text(
        _note("F441KKD2", "other2020")
    )
    fake = FakeZotero(server_id="S")
    canned_item(fake, item=_second_item("newer2020"), children=())
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    _, path, digest = _planned(
        tmp_vault,
        client,
        mapping=(("other2020", "newer2020"),),
        now=datetime.datetime(2026, 9, 8, tzinfo=datetime.UTC),
    )
    propagate.apply(tmp_vault, client, path, digest)
    # old2020 is now held by a different item (a freed name, passed over);
    # other2020 is residue in a page carrying a stray byte.
    (tmp_vault / "literature" / "old2020.md").write_text(_note("FRESH001", "old2020"))
    (tmp_vault / "wiki" / "sources" / "C.md").write_bytes(
        b"---\ntype: source\n---\n[@old2020] and [@other2020] \xff\n"
    )
    stale = propagate.lint_propagation(tmp_vault)
    assert [(o.target, o.reason.split(",")[0]) for o in stale] == [
        ("path-bytes:wiki/sources/C.md", "stale-key — names other2020")
    ]


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads everything")
def test_lint_reports_a_surface_it_cannot_read_and_judges_the_rest(
    tmp_vault, monkeypatch
):
    """After an applied plan, `lint_propagation` reads every surface; one it
    cannot read gets its own row and the others are still judged.

    A page it cannot *decode* is a different answer here and deliberately so:
    the read is byte-tolerant, so the stray byte costs the page nothing and
    its residue verdict still stands (``test_lint_rows_an_unreadable_record_
    and_reads_surfaces_byte_tolerantly``).
    """
    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    _planned_plan, path, digest = _planned(tmp_vault, client)
    propagate.apply(tmp_vault, client, path, digest)
    (tmp_vault / "projects" / "brief" / "draft.md").write_text("[[old2020]]\n")
    unreadable = tmp_vault / "wiki" / "sources" / "B.md"
    unreadable.chmod(0)
    try:
        by_target = {r.target: r for r in propagate.lint_propagation(tmp_vault)}
    finally:
        unreadable.chmod(0o644)
    row = by_target["path-bytes:wiki/sources/B.md"]
    assert (row.result, row.reason.split(" — ")[0]) == (Result.UNREACHABLE, "outage")
    assert by_target["path-bytes:projects/brief/draft.md"].reason.startswith(
        "stale-key"
    )
