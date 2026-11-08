import datetime
import hashlib
import json
import os
import subprocess

import pytest

from research_vault import Result, capture, gitstate, lints, propagate, zotero
from research_vault.outcome import Outcome
from tests.conftest import must_replace
from tests.fakes import ITEM, FakeZotero, canned_item


def _seed(vault):
    (vault / "literature" / "old2020.md").write_text(
        '---\ntype: "literature"\nzotero-server-id: "S"\nzotero-item-key: "E352DFS8"\n'
        'zotero-item-version: 1\ncitationKey: "old2020"\nattachments:\nfulltext:\n---\n'
    )
    (vault / "projects" / "brief").mkdir(parents=True)
    (vault / "projects" / "brief" / "draft.md").write_text(
        '---\ntype: "project"\n---\nSee [@old2020, p. 3] and [@old2020] and [[old2020]] and [[old2020#^c-1]] and [[old2020|alias]] and [old2020](/literature/old2020.md#^c-1).\n'
    )
    (vault / "wiki" / "sources").mkdir(parents=True)
    (vault / "wiki" / "sources" / "A.md").write_text(
        "---\ntype: source\n---\n[[old2020]] and [../../literature/old2020.md](../../literature/old2020.md) and [[older2020]]\n"
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
    """``mapping=None`` plans from the lifecycle linter, as the CLI without --map does."""
    planned, outcomes = propagate.plan(
        vault, client, None if mapping is None else dict(mapping), now=now
    )
    assert planned is not None, outcomes
    return planned, propagate.write_plan(vault, planned), propagate.plan_sha256(planned)


def test_plan_operation_id_is_utc_and_the_format_is_pinned(tmp_vault, monkeypatch):
    """`datetime.now(None)` would be local time: under a non-UTC TZ the id
    drifts by the offset; an explicit `now` pins the strftime format."""
    import time

    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    explicit = datetime.datetime(2026, 9, 17, 10, 20, 30, tzinfo=datetime.UTC)
    planned, _path, _digest = _planned(tmp_vault, client, now=explicit)
    assert planned.operation_id == "propagate-20260917T102030Z"
    monkeypatch.setenv("TZ", "Asia/Kolkata")
    time.tzset()
    try:
        before = datetime.datetime.now(datetime.UTC).replace(microsecond=0)
        planned, _path, _digest = _planned(tmp_vault, client)
        stamped = datetime.datetime.strptime(
            planned.operation_id[len("propagate-") :], "%Y%m%dT%H%M%SZ"
        ).replace(tzinfo=datetime.UTC)
        assert abs((stamped - before).total_seconds()) < 60
    finally:
        monkeypatch.delenv("TZ")
        time.tzset()


def test_plan_refuses_an_unsafe_new_key_by_the_real_validation_error(
    tmp_vault, monkeypatch
):
    """`literature_notes.note_path`'s `InvalidCitationKeyError` names the
    problem; a mutant that discards it into a bare `None` (or `str(None)`,
    the same text either way) would still refuse but say nothing true about
    why."""
    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    planned, outcomes = propagate.plan(tmp_vault, client, {"old2020": "new/2020"})
    assert planned is None
    assert outcomes[0].reason == "schema-violation — unsafe citation key: 'new/2020'"


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
            "See [@old2020, p. 3] and [@old2020] and [[old2020]] and [[old2020#^c-1]] and [[old2020|alias]] and [old2020](/literature/old2020.md#^c-1).\n"
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
    assert (
        refused.reason
        == "database-changed — Zotero-Server-ID does not match this server"
    )
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


def test_read_plan_refuses_a_file_that_is_not_a_propagation_plan(tmp_vault):
    path = tmp_vault / "not-a-plan.json"
    path.write_text(json.dumps({"schema": "something-else"}))
    with pytest.raises(ValueError, match=r"^not a propagation plan: ") as excinfo:
        propagate.read_plan(path)
    assert str(excinfo.value) == f"not a propagation plan: {path}"


def test_plan_refuses_a_missing_note_and_never_reads_an_outage_as_nothing_to_do(
    tmp_vault, monkeypatch
):
    planned, outcomes = propagate.plan(
        tmp_vault, _zotero(monkeypatch), {"ghost2020": "new2020"}
    )
    assert planned is None
    assert outcomes[0].result is Result.UNMATCHED
    assert outcomes[0].reason == (
        "schema-violation — no note under literature/ records citationKey ghost2020"
    )
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
        "See [@new2020, p. 3] and [@new2020] and [[new2020]] and [[new2020#^c-1]] and [[new2020|alias]] and [new2020](/literature/new2020.md#^c-1).\n"
    )
    assert (tmp_vault / "wiki" / "sources" / "A.md").read_text() == (
        "---\ntype: source\n---\n[[new2020]] and [../../literature/old2020.md](/literature/new2020.md) and [[older2020]]\n"
    )


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
    assert refused.reason == (
        "mismatch — plan changed: the vault moved since this plan was "
        "computed; run propagate again"
    )
    assert (tmp_vault / "literature" / "old2020.md").is_file()
    assert not (tmp_vault / "system" / "propagations").exists()
    (wrong,) = propagate.apply(tmp_vault, client, path, "0" * 64)
    assert wrong.result is Result.UNMATCHED
    assert wrong.reason == "mismatch — approved hash does not name this plan"


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
    assert (
        outcomes[0].reason
        == "matched — rewrote projects/brief/draft.md, wiki/sources/A.md"
    )
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
    planned, path, digest = _planned(tmp_vault, client)
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
    assert {o.reason for o in stale} == {
        f"stale-key — names old2020, mapped to new2020 by {planned.operation_id}"
    }


def test_plan_and_lint_read_a_markdown_link_from_the_surface_that_holds_it(
    tmp_vault, monkeypatch
):
    """A markdown link is matched through `links.names_note` from its own
    surface: `../../literature/old2020.md` names the note from
    `projects/brief/`, so it is planned, rewritten and, written again
    afterwards, residue; `../literature/old2020.md` from there names
    `projects/literature/old2020.md`, and `/old2020.md` from the root names
    the root file `old2020.md`: neither is any of these."""
    _seed(tmp_vault)
    client = _zotero(monkeypatch)
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    notes = tmp_vault / "projects" / "brief" / "notes.md"
    notes.write_text("[n](../../literature/old2020.md) [m](../literature/old2020.md)\n")
    # From the root, each of these is the root file `old2020.md`, not the note.
    root = tmp_vault / "root-note.md"
    root.write_text("[r](/old2020.md) [s](./old2020.md) [t](../old2020.md)\n")
    planned, path, digest = _planned(tmp_vault, client)
    assert "projects/brief/notes.md" in [s.path for s in planned.surfaces]
    assert "root-note.md" not in [s.path for s in planned.surfaces]
    propagate.apply(tmp_vault, client, path, digest)
    assert notes.read_text() == (
        "[n](/literature/new2020.md) [m](../literature/old2020.md)\n"
    )
    assert root.read_text() == "[r](/old2020.md) [s](./old2020.md) [t](../old2020.md)\n"
    (clean,) = propagate.lint_propagation(tmp_vault)
    assert clean.result is Result.MATCHED, clean
    (tmp_vault / "projects" / "brief" / "late.md").write_text(
        "[n](../../literature/old2020.md)\n"
    )
    (tmp_vault / "projects" / "brief" / "near.md").write_text(
        "[m](../literature/old2020.md)\n"
    )
    (stale,) = propagate.lint_propagation(tmp_vault)
    assert stale.target == "path-bytes:projects/brief/late.md"


def test_a_uri_destination_names_no_note_even_for_a_colon_key(tmp_vault, monkeypatch):
    """`[x](re:2020)` is a URI (`links.is_external`), never the note `re:2020`:
    it is neither planned, rewritten nor residue, while `[[re:2020]]`, a
    wikilink target, names the note and is all three."""
    (tmp_vault / "literature" / "re:2020.md").write_text(_note("E352DFS8", "re:2020"))
    (tmp_vault / "projects" / "brief").mkdir(parents=True)
    uri = tmp_vault / "projects" / "brief" / "uri.md"
    uri.write_text("[x](re:2020)\n")
    wiki = tmp_vault / "projects" / "brief" / "wiki.md"
    wiki.write_text("[[re:2020]]\n")
    client = _zotero(monkeypatch, "re2021")
    monkeypatch.setattr(
        propagate.capture, "capture", lambda vault, client, keys, **kw: []
    )
    planned, path, digest = _planned(tmp_vault, client, (("re:2020", "re2021"),))
    assert [s.path for s in planned.surfaces] == ["projects/brief/wiki.md"]
    propagate.apply(tmp_vault, client, path, digest)
    assert uri.read_text() == "[x](re:2020)\n"
    assert wiki.read_text() == "[[re2021]]\n"
    (clean,) = propagate.lint_propagation(tmp_vault)
    assert clean.result is Result.MATCHED, clean
    wiki.write_text("[[re:2020]]\n")
    (stale,) = propagate.lint_propagation(tmp_vault)
    assert stale.target == "path-bytes:projects/brief/wiki.md"


def test_lint_parses_each_surface_once_whatever_the_number_of_keys(
    tmp_vault, monkeypatch
):
    """The lint runs on the commit path: a surface's links are found once and
    every stale key is tested against them, not one parse per key."""
    _seed(tmp_vault)
    records = tmp_vault / "system" / "propagations"
    records.mkdir(parents=True, exist_ok=True)
    (records / "propagate-20260908T101500Z.json").write_text(
        json.dumps(
            {
                "schema": propagate.SCHEMA,
                "operation_id": "propagate-20260908T101500Z",
                "date": "2026-09-08",
                "mapping": {"a2020": "b2020", "c2020": "d2020", "e2020": "f2020"},
                "item_keys": {},
                "surfaces": [],
            }
        )
    )
    parsed: list[str] = []
    find_links = propagate.links.find_links

    def counted(text):
        parsed.append(text)
        return find_links(text)

    monkeypatch.setattr(propagate.links, "find_links", counted)
    (clean,) = propagate.lint_propagation(tmp_vault)
    assert clean.result is Result.MATCHED, clean
    assert len(parsed) == len(list(propagate._surfaces(tmp_vault))) == 3


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
    assert propagate._mapping_from_linter(tmp_vault, _zotero(monkeypatch)) == (
        {},
        {},
        [],
    )
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
        {},
        [],
    )
    mapping, _merges, blocking = propagate._mapping_from_linter(
        tmp_vault, _zotero(monkeypatch, server_id="Tdoqsn2J4q4h")
    )
    assert mapping == {}
    assert [(o.target, o.result) for o in blocking] == [("vault", Result.UNMATCHED)]
    assert blocking[0].reason == (
        "database-changed — Zotero-Server-ID does not match this server; "
        "every recorded version is void"
    )


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
    # The tail is the OS's; the path it names is the plan the test asked for.
    assert outcome.reason.split(" — ")[0] == "schema-violation"
    assert outcome.reason.startswith(
        "schema-violation — unreadable plan: [Errno 2] No such file or directory: "
    )
    assert outcome.reason.endswith(f"'{missing}'")


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
    assert by_target["path-bytes:projects/brief/draft.md"].reason == (
        f"stale-key — names old2020, mapped to new2020 by {_planned_plan.operation_id}"
    )


def _merge_fake(
    monkeypatch,
    *,
    survivor_has_note,
    citation_key="new2020",
    losers=("E352DFS8",),
    extra=(),
):
    """old2020 (E352DFS8) was merged into NEW00001, whose key is new2020."""
    fake = FakeZotero(server_id="S")
    survivor = {
        **ITEM,
        "key": "NEW00001",
        "data": {
            **ITEM["data"],
            "key": "NEW00001",
            "citationKey": citation_key,
            "relations": {
                "dc:replaces": [f"http://zotero.org/users/0/items/{k}" for k in losers]
            },
        },
    }
    canned_item(fake, item=survivor)
    for item in extra:
        canned_item(fake, item=item, children=())
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={"NEW00001": 600, "D7EJ9FTG": 551, "N0TE0001": 552},
        headers={"Last-Modified-Version": "600"},
    )
    fake.get(
        "/api/users/0/items/trash?format=versions",
        body={key: 545 + i for i, key in enumerate(losers)},
    )
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[survivor],
        headers={"Last-Modified-Version": "600"},
    )
    fake.rpc("item.export", lambda params: [{"id": citation_key, "title": "T"}])
    return fake.install(zotero.ZoteroClient(), monkeypatch)


def test_plan_maps_a_merged_loser_to_the_survivor_through_its_item(
    tmp_vault, monkeypatch
):
    _seed(tmp_vault)
    client = _merge_fake(monkeypatch, survivor_has_note=False)
    planned, outcomes = propagate.plan(tmp_vault, client, None)
    assert planned is not None, outcomes
    assert planned.mapping == {"old2020": "new2020"}
    assert planned.merges == {"old2020": "NEW00001"}
    assert planned.item_keys == {"old2020": "NEW00001"}
    assert propagate.read_plan(propagate.write_plan(tmp_vault, planned)).merges == {
        "old2020": "NEW00001"
    }


def test_apply_renames_the_loser_when_the_survivor_has_no_note(tmp_vault, monkeypatch):
    _seed(tmp_vault)
    client = _merge_fake(monkeypatch, survivor_has_note=False)
    planned, path, sha = _planned(tmp_vault, client, mapping=None)
    assert planned.removes == {}
    outcomes = propagate.apply(tmp_vault, client, path, sha)
    assert all(o.result is Result.MATCHED for o in outcomes), outcomes
    assert not (tmp_vault / "literature" / "old2020.md").exists()
    note = tmp_vault / "literature" / "new2020.md"
    assert note.is_file()
    assert 'zotero-item-key: "NEW00001"' in note.read_text()  # re-rendered
    assert "[[new2020]]" in (tmp_vault / "wiki" / "sources" / "A.md").read_text()


def test_apply_deletes_the_loser_when_the_survivor_already_has_a_note(
    tmp_vault, monkeypatch
):
    """§5.3.6: the loser's note is wholly machine-written and the merge moved
    its Zotero child notes onto the survivor; nothing person-written is lost.
    ADR 0003's scope note of 2026-11-07 covers this one deletion."""
    _seed(tmp_vault)
    (tmp_vault / "literature" / "new2020.md").write_text(_note("NEW00001", "new2020"))
    client = _merge_fake(monkeypatch, survivor_has_note=True)
    planned, path, sha = _planned(tmp_vault, client, mapping=None)
    assert planned.merges == {"old2020": "NEW00001"}
    assert planned.removes == {"old2020": "literature/old2020.md"}
    outcomes = propagate.apply(tmp_vault, client, path, sha)
    assert all(o.result is Result.MATCHED for o in outcomes), outcomes
    assert not (tmp_vault / "literature" / "old2020.md").exists()
    assert (tmp_vault / "literature" / "new2020.md").is_file()
    record = json.loads(
        next((tmp_vault / "system" / "propagations").glob("*.json")).read_text()
    )
    assert record["merges"] == {"old2020": "NEW00001"}
    assert record["removes"] == {"old2020": "literature/old2020.md"}
    assert record["removed"] == ["literature/old2020.md"]


def test_a_plain_re_key_still_refuses_an_existing_target(tmp_vault, monkeypatch):
    """The exists-check is bypassed for merges only."""
    _seed(tmp_vault)
    (tmp_vault / "literature" / "new2020.md").write_text(_note("OTHER001", "new2020"))
    client = _zotero(monkeypatch)
    planned, outcomes = propagate.plan(tmp_vault, client, {"old2020": "new2020"})
    assert planned is None
    assert "already exists" in outcomes[0].reason


def test_a_merge_into_a_survivor_without_a_citation_key_maps_nothing(
    tmp_vault, monkeypatch
):
    """`merged — NEW00001 (?)`: no target name yet, so neither a mapping nor a
    merge; the plan says there is nothing to propagate."""
    (tmp_vault / "literature" / "old2020.md").write_text(_note("E352DFS8", "old2020"))
    client = _lint_fake(
        monkeypatch,
        versions={"NEW00001": 1},
        trash={"E352DFS8": 1},
        top=[
            {
                "key": "NEW00001",
                "data": {
                    "relations": {
                        "dc:replaces": "http://zotero.org/users/0/items/E352DFS8"
                    }
                },
            }
        ],
    )
    assert propagate._mapping_from_linter(tmp_vault, client) == ({}, {}, [])


def test_a_merge_is_verified_against_the_survivors_item(tmp_vault, monkeypatch):
    """The live read for a merged loser is the survivor's item: a survivor
    whose key moved between plan and apply refuses before anything changes."""
    _seed(tmp_vault)
    _plan, path, sha = _planned(
        tmp_vault, _merge_fake(monkeypatch, survivor_has_note=False), mapping=None
    )
    moved = FakeZotero(server_id="S")
    canned_item(
        moved,
        item={
            **ITEM,
            "key": "NEW00001",
            "data": {**ITEM["data"], "key": "NEW00001", "citationKey": "new2020b"},
        },
    )
    client = moved.install(zotero.ZoteroClient(), monkeypatch)
    (refused,) = propagate.apply(tmp_vault, client, path, sha)
    assert refused.reason == (
        "mismatch — item NEW00001 carries citation key 'new2020b', not 'new2020'"
    )
    assert (tmp_vault / "literature" / "old2020.md").is_file()


def test_a_plan_document_without_merges_reads_as_a_re_key(tmp_vault, monkeypatch):
    """Records written before #183 carry no `merges`; they read as `{}`."""
    _seed(tmp_vault)
    _plan, path, _sha = _planned(tmp_vault, _zotero(monkeypatch))
    document = json.loads(path.read_text())
    assert document["merges"] == {}
    del document["merges"]
    path.write_text(json.dumps(document))
    assert propagate.read_plan(path).merges == {}


def _survivor_note(vault, item_key="NEW00001"):
    note = vault / "literature" / "new2020.md"
    note.write_text(_note(item_key, "new2020"))
    return note


def test_apply_refuses_a_merge_whose_survivor_note_appeared_after_the_plan(
    tmp_vault, monkeypatch
):
    """P19: rename or removal is the plan's, hashed in `removes`, never chosen
    at apply time. `literature/` hashes no surface, so only `removes` can
    tell an approved rename from the removal it would otherwise become."""
    _seed(tmp_vault)
    client = _merge_fake(monkeypatch, survivor_has_note=False)
    planned, path, sha = _planned(tmp_vault, client, mapping=None)
    assert planned.removes == {}
    loser = (tmp_vault / "literature" / "old2020.md").read_bytes()
    survivor = _survivor_note(tmp_vault).read_bytes()
    (refused,) = propagate.apply(tmp_vault, client, path, sha)
    assert refused.reason.startswith("mismatch — plan changed")
    assert (tmp_vault / "literature" / "old2020.md").read_bytes() == loser
    assert (tmp_vault / "literature" / "new2020.md").read_bytes() == survivor


def test_cli_prints_a_merge_and_the_removal_it_approves(tmp_vault, monkeypatch, capsys):
    """P19: the printed plan names the removal the hash binds; a plain re-key
    still prints `rename`."""
    _seed(tmp_vault)
    cli, _bases = _cli(monkeypatch, _merge_fake(monkeypatch, survivor_has_note=False))
    assert cli.main(["propagate", "--vault", str(tmp_vault)]) == 0
    assert capsys.readouterr().out.splitlines()[0] == (
        "merge old2020 → new2020 (item NEW00001)"
    )
    _survivor_note(tmp_vault)
    assert cli.main(["propagate", "--vault", str(tmp_vault)]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == (
        "merge old2020 → new2020 (item NEW00001); removes literature/old2020.md"
    )
    assert not any(line.startswith("rename ") for line in lines)


def test_plan_refuses_a_merge_onto_another_items_note(tmp_vault, monkeypatch):
    """P20: the survivor's path holding another item's note (or another
    database's) is no survivor note; nothing is removed or recaptured over."""
    _seed(tmp_vault)
    loser = (tmp_vault / "literature" / "old2020.md").read_bytes()
    for text in (
        _note("OTHER001", "new2020"),
        must_replace(_note("NEW00001", "new2020"), '"S"', '"T"'),
        "---\ntype: literature\n---\nno tuple\n",
    ):
        note = tmp_vault / "literature" / "new2020.md"
        note.write_text(text)
        client = _merge_fake(monkeypatch, survivor_has_note=True)
        planned, outcomes = propagate.plan(tmp_vault, client, None)
        assert planned is None
        assert outcomes[0].reason == (
            "schema-violation — literature/new2020.md is not item NEW00001's "
            "note; the loser's note is not removed for it"
        )
        assert (tmp_vault / "literature" / "old2020.md").read_bytes() == loser
        assert note.read_text() == text


def test_a_merge_into_the_losers_own_key_leaves_no_stale_key(tmp_vault, monkeypatch):
    """P21: a survivor carrying the loser's key maps nothing: no rename, no
    rewrite, no `mapping` entry for lint_propagation to call stale; the
    survivor is still recaptured over the note."""
    _seed(tmp_vault)
    client = _merge_fake(monkeypatch, survivor_has_note=False, citation_key="old2020")
    planned, path, sha = _planned(tmp_vault, client, mapping=None)
    assert planned.mapping == {}
    assert planned.merges == {"old2020": "NEW00001"}
    assert planned.item_keys == {"old2020": "NEW00001"}
    assert (planned.removes, planned.surfaces) == ({}, ())
    outcomes = propagate.apply(tmp_vault, client, path, sha)
    assert all(o.result is Result.MATCHED for o in outcomes), outcomes
    note = (tmp_vault / "literature" / "old2020.md").read_text()
    assert 'zotero-item-key: "NEW00001"' in note
    assert "[[old2020]]" in (tmp_vault / "wiki" / "sources" / "A.md").read_text()
    assert not [
        o for o in propagate.lint_propagation(tmp_vault) if "stale-key" in o.reason
    ]


def _stub_capture(monkeypatch, vault, *rows):
    seen = []

    def capture(_vault, _client, keys, **_kw):
        seen.append((list(keys), (vault / "literature" / "old2020.md").exists()))
        return list(rows)

    monkeypatch.setattr(propagate.capture, "capture", capture)
    return seen


def test_the_removal_unlinks_the_loser_and_never_renames_over_the_survivor(
    tmp_vault, monkeypatch
):
    """P22, P23: with capture stubbed, the survivor's note keeps its own
    bytes (a rename over it would leave old2020's), and the loser's note
    still exists while the survivor is recaptured."""
    _seed(tmp_vault)
    survivor = _survivor_note(tmp_vault).read_bytes()
    client = _merge_fake(monkeypatch, survivor_has_note=True)
    _plan, path, sha = _planned(tmp_vault, client, mapping=None)
    seen = _stub_capture(
        monkeypatch, tmp_vault, Outcome("capture", "new2020", Result.MATCHED, "matched")
    )
    outcomes = propagate.apply(tmp_vault, client, path, sha)
    assert all(o.result is Result.MATCHED for o in outcomes), outcomes
    assert seen == [(["NEW00001"], True)]
    assert not (tmp_vault / "literature" / "old2020.md").exists()
    assert (tmp_vault / "literature" / "new2020.md").read_bytes() == survivor


@pytest.mark.parametrize(
    "rows",
    [
        [Outcome("capture", "new2020", Result.UNREACHABLE, "outage — refused")],
        [Outcome("capture", "new2020", Result.SKIPPED, "no-fulltext — none")],
        # A real capture that fails the survivor's render still reports the
        # CSL bibliography it updated, MATCHED: that row is not the survivor's.
        [
            Outcome("capture", capture.CSL_TARGET, Result.MATCHED, "matched"),
            Outcome("capture", "new2020", Result.UNMATCHED, "mismatch — refused"),
        ],
    ],
    ids=["outage", "no-render-row", "csl-row-only"],
)
def test_a_survivor_recapture_that_did_not_render_keeps_the_loser(
    tmp_vault, monkeypatch, rows
):
    """P23: the scope note's condition is the survivor re-rendered in the
    same act; without capture's MATCHED row for it the loser's note stays,
    the apply says so, and the record does not name it as removed."""
    _seed(tmp_vault)
    loser = (tmp_vault / "literature" / "old2020.md").read_bytes()
    _survivor_note(tmp_vault)
    client = _merge_fake(monkeypatch, survivor_has_note=True)
    planned, path, sha = _planned(tmp_vault, client, mapping=None)
    _stub_capture(monkeypatch, tmp_vault, *rows)
    outcomes = propagate.apply(tmp_vault, client, path, sha)
    assert outcomes[-1] == Outcome(
        "propagation",
        "old2020",
        Result.UNMATCHED,
        "merged — kept literature/old2020.md: item NEW00001's recapture did "
        "not match; run propagate again",
    )
    assert (tmp_vault / "literature" / "old2020.md").read_bytes() == loser
    record = json.loads(
        (
            tmp_vault / "system" / "propagations" / f"{planned.operation_id}.json"
        ).read_text()
    )
    assert record["removes"] == {"old2020": "literature/old2020.md"}
    assert record["removed"] == []


@pytest.mark.parametrize("shape", ["symlink", "directory"])
def test_plan_refuses_a_merge_onto_a_survivor_path_it_cannot_read_as_a_note(
    tmp_vault, monkeypatch, shape
):
    """P20: a symlink (even to the survivor's own note) or a directory at the
    survivor's path is not a note plan may remove the loser's for."""
    _seed(tmp_vault)
    target = tmp_vault / "literature" / "new2020.md"
    if shape == "symlink":
        real = tmp_vault / "elsewhere.md"
        real.write_text(_note("NEW00001", "new2020"))
        target.symlink_to(real)
    else:
        target.mkdir()
    planned, outcomes = propagate.plan(
        tmp_vault, _merge_fake(monkeypatch, survivor_has_note=True), None
    )
    assert planned is None
    assert "is not item NEW00001's note" in outcomes[0].reason
    assert (tmp_vault / "literature" / "old2020.md").is_file()


def _seed_second_loser(vault):
    """old2021 (LOSER002), a second note merged into the same survivor."""
    old2021 = vault / "literature" / "old2021.md"
    old2021.write_text(_note("LOSER002", "old2021"))
    (vault / "wiki" / "sources" / "C.md").write_text(
        "---\ntype: source\n---\nSee [[old2021]].\n"
    )
    return old2021.read_bytes()


def _two_loser_fake(monkeypatch):
    return _merge_fake(
        monkeypatch, survivor_has_note=False, losers=("E352DFS8", "LOSER002")
    )


def test_two_losers_into_a_note_less_survivor_plan_one_rename_and_one_removal(
    tmp_vault, monkeypatch, capsys
):
    """P24: the first loser (sorted) is renamed onto the survivor's path, which
    the plan then holds as occupied by the survivor-to-be; the second is a
    planned, hashed, printed removal — never a rename over the first."""
    _seed(tmp_vault)
    _seed_second_loser(tmp_vault)
    planned, outcomes = propagate.plan(tmp_vault, _two_loser_fake(monkeypatch), None)
    assert planned is not None, outcomes
    assert planned.mapping == {"old2020": "new2020", "old2021": "new2020"}
    assert planned.removes == {"old2021": "literature/old2021.md"}
    cli, _bases = _cli(monkeypatch, _two_loser_fake(monkeypatch))
    assert cli.main(["propagate", "--vault", str(tmp_vault)]) == 0
    assert capsys.readouterr().out.splitlines()[:2] == [
        "merge old2020 → new2020 (item NEW00001)",
        "merge old2021 → new2020 (item NEW00001); removes literature/old2021.md",
    ]


def test_two_losers_apply_renames_one_and_removes_the_other_after_the_render(
    tmp_vault, monkeypatch
):
    """P24 (3): the survivor's note is its render, not old2021's bytes;
    old2021.md goes only after a MATCHED recapture, `removed` names exactly
    it, and the evidence-layer lint is silent on both notes that left."""
    _seed(tmp_vault)
    old2021 = _seed_second_loser(tmp_vault)
    for args in (["add", "-A"], ["commit", "-q", "-m", "seed"]):
        subprocess.run(["git", *args], cwd=tmp_vault, check=True, capture_output=True)
    base = gitstate.snapshot_tree(tmp_vault, "HEAD")
    client = _two_loser_fake(monkeypatch)
    planned, path, sha = _planned(tmp_vault, client, mapping=None)
    real = propagate.capture.capture
    seen = []

    def capture_(vault, client, keys, **kw):
        seen.append((list(keys), (vault / "literature" / "old2021.md").exists()))
        return real(vault, client, keys, **kw)

    monkeypatch.setattr(propagate.capture, "capture", capture_)
    outcomes = propagate.apply(tmp_vault, client, path, sha)
    assert all(o.result is Result.MATCHED for o in outcomes), outcomes
    assert seen == [(["NEW00001"], True), (["NEW00001"], True)]
    survivor = (tmp_vault / "literature" / "new2020.md").read_bytes()
    assert survivor != old2021
    assert b'zotero-item-key: "NEW00001"' in survivor
    assert not (tmp_vault / "literature" / "old2020.md").exists()
    assert not (tmp_vault / "literature" / "old2021.md").exists()
    record = json.loads(
        (
            tmp_vault / "system" / "propagations" / f"{planned.operation_id}.json"
        ).read_text()
    )
    assert record["removed"] == ["literature/old2021.md"]
    rows = lints.lint_evidence_layer(base, gitstate.snapshot_worktree(tmp_vault))
    assert not [o for o in rows if o.reason == "drift — literature note deleted"], rows


@pytest.mark.parametrize("shape", ["file", "dangling-symlink"])
def test_apply_entry_never_renames_onto_an_existing_path(tmp_vault, monkeypatch, shape):
    """P24 (2), the backstop: an entry not planned as a removal whose target
    exists at rename time is refused; nothing moves, nothing is recaptured
    or recorded as removed."""
    _seed(tmp_vault)
    target = tmp_vault / "literature" / "new2020.md"
    if shape == "file":
        target.write_text(_note("NEW00001", "new2020"))
    else:
        target.symlink_to(tmp_vault / "nowhere.md")
    loser = (tmp_vault / "literature" / "old2020.md").read_bytes()
    seen = _stub_capture(monkeypatch, tmp_vault)
    approved = propagate.Plan(
        "propagate-20261024T100000Z",
        "2026-10-24",
        {"old2020": "new2020"},
        {"old2020": "NEW00001"},
        {"old2020": "NEW00001"},
        {},
        (),
    )
    document = {**propagate._document(approved), "removed": [], "moved": {}}
    outcomes = propagate._apply_entry(
        tmp_vault,
        None,
        approved,
        "old2020",
        "new2020",
        tmp_vault / "literature" / "old2020.md",
        document,
    )
    assert outcomes == [
        Outcome(
            "propagation",
            "old2020",
            Result.UNMATCHED,
            "schema-violation — literature/new2020.md already exists; "
            "nothing is renamed over it",
        )
    ]
    assert seen == []
    # P26: the refused entry leaves the record; it never happened.
    assert (document["removed"], document["moved"]) == ([], {})
    assert (document["mapping"], document["item_keys"], document["merges"]) == (
        {},
        {},
        {},
    )
    assert (tmp_vault / "literature" / "old2020.md").read_bytes() == loser
    assert target.is_symlink() == (shape == "dangling-symlink")


@pytest.mark.parametrize("stale", ["zed2020", "aaa2020"])
def test_a_survivor_re_keyed_in_the_same_pass_takes_the_rename_and_the_loser_goes(
    tmp_vault, monkeypatch, capsys, stale
):
    """P25: zed2020 is the survivor's own note under a stale key (re-keyed),
    old2020 a loser merged into it, and new2020.md does not exist. Whatever
    the keys' sort order, the survivor's note is renamed and recaptured, and
    the loser is a planned removal that goes after the MATCHED recapture."""
    real = propagate.capture.capture
    _seed(tmp_vault)
    (tmp_vault / "literature" / f"{stale}.md").write_text(_note("NEW00001", stale))
    for args in (["add", "-A"], ["commit", "-q", "-m", "seed"]):
        subprocess.run(["git", *args], cwd=tmp_vault, check=True, capture_output=True)
    base = gitstate.snapshot_tree(tmp_vault, "HEAD")
    client = _merge_fake(monkeypatch, survivor_has_note=False)
    planned, path, sha = _planned(tmp_vault, client, mapping=None)
    assert planned.mapping == {"old2020": "new2020", stale: "new2020"}
    assert planned.merges == {"old2020": "NEW00001"}
    assert planned.removes == {"old2020": "literature/old2020.md"}
    cli, _bases = _cli(monkeypatch, client)
    assert cli.main(["propagate", "--vault", str(tmp_vault)]) == 0
    assert capsys.readouterr().out.splitlines()[:2] == [
        f"rename {stale} → new2020 (item NEW00001)",
        "merge old2020 → new2020 (item NEW00001); removes literature/old2020.md",
    ]
    seen = []

    def capture_(vault, client, keys, **kw):
        seen.append(
            (
                (vault / "literature" / "new2020.md").exists(),
                (vault / "literature" / "old2020.md").exists(),
            )
        )
        return real(vault, client, keys, **kw)

    monkeypatch.setattr(propagate.capture, "capture", capture_)
    outcomes = propagate.apply(tmp_vault, client, path, sha)
    assert all(o.result is Result.MATCHED for o in outcomes), outcomes
    assert seen == [(True, True), (True, True)]  # renamed first; loser kept till then
    note = (tmp_vault / "literature" / "new2020.md").read_text()
    assert 'zotero-item-key: "NEW00001"' in note
    assert not (tmp_vault / "literature" / f"{stale}.md").exists()
    assert not (tmp_vault / "literature" / "old2020.md").exists()
    record = json.loads(
        (
            tmp_vault / "system" / "propagations" / f"{planned.operation_id}.json"
        ).read_text()
    )
    assert (record["removed"], record["moved"]) == (["literature/old2020.md"], {})
    rows = lints.lint_evidence_layer(base, gitstate.snapshot_worktree(tmp_vault))
    assert not [o for o in rows if o.reason == "drift — literature note deleted"], rows


def test_two_re_keys_onto_one_key_name_the_claim_not_a_file(tmp_vault, monkeypatch):
    """P25: the second entry for a path the first claims is refused by the
    claim; the file does not exist, so "already exists" would be false."""
    _seed(tmp_vault)
    (tmp_vault / "literature" / "other2020.md").write_text(
        _note("F441KKD2", "other2020")
    )
    fake = FakeZotero(server_id="S")
    canned_item(fake, item={**ITEM, "data": {**ITEM["data"], "citationKey": "new2020"}})
    canned_item(fake, item=_second_item("new2020"), children=())
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    planned, outcomes = propagate.plan(
        tmp_vault, client, {"old2020": "new2020", "other2020": "new2020"}
    )
    assert planned is None
    assert [(o.target, o.reason) for o in outcomes] == [
        (
            "other2020",
            (
                "schema-violation — literature/new2020.md is claimed by old2020 "
                "in this plan"
            ),
        )
    ]


def test_a_merge_loser_onto_another_items_claim_names_the_claim(tmp_vault, monkeypatch):
    """A plain re-key of a different item claims the survivor's path first;
    the loser is refused by that claim, not removed for it."""
    _seed(tmp_vault)
    (tmp_vault / "literature" / "aaa2020.md").write_text(_note("F441KKD2", "aaa2020"))
    client = _merge_fake(
        monkeypatch, survivor_has_note=False, extra=(_second_item("new2020"),)
    )
    planned, outcomes = propagate.plan(
        tmp_vault,
        client,
        {"aaa2020": "new2020", "old2020": "new2020"},
        merges={"old2020": "NEW00001"},
    )
    assert planned is None
    assert outcomes[-1].reason == (
        "schema-violation — literature/new2020.md is claimed by aaa2020 in this plan"
    )


def test_a_backstop_refused_entry_leaves_no_stale_key(tmp_vault, monkeypatch):
    """P26: the record names only what was applied. An entry the backstop
    refused keeps its old key live, so lint_propagation must not call the
    surfaces naming it stale."""
    _seed(tmp_vault)
    (tmp_vault / "literature" / "other2020.md").write_text(
        _note("F441KKD2", "other2020")
    )
    (tmp_vault / "wiki" / "sources" / "C.md").write_text(
        "---\ntype: source\n---\nSee [[other2020]].\n"
    )
    fake = FakeZotero(server_id="S")
    canned_item(fake, item={**ITEM, "data": {**ITEM["data"], "citationKey": "new2020"}})
    canned_item(fake, item=_second_item("zzz2020"), children=())
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    planned, path, sha = _planned(
        tmp_vault, client, mapping=(("old2020", "new2020"), ("other2020", "zzz2020"))
    )

    def capture_(vault, _client, keys, **_kw):
        # The first entry's recapture leaves a file at the second's target.
        (vault / "literature" / "zzz2020.md").write_text(_note("F441KKD2", "zzz2020"))
        return []

    monkeypatch.setattr(propagate.capture, "capture", capture_)
    outcomes = propagate.apply(tmp_vault, client, path, sha)
    assert outcomes[-1].reason == (
        "schema-violation — literature/zzz2020.md already exists; "
        "nothing is renamed over it"
    )
    assert (tmp_vault / "literature" / "other2020.md").is_file()
    record = json.loads(
        (
            tmp_vault / "system" / "propagations" / f"{planned.operation_id}.json"
        ).read_text()
    )
    assert record["mapping"] == {"old2020": "new2020"}
    assert "other2020" not in record["item_keys"]
    stale = [
        o for o in propagate.lint_propagation(tmp_vault) if "stale-key" in o.reason
    ]
    assert not [o for o in stale if "other2020" in o.reason], stale
