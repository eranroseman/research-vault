import json
from pathlib import Path

from research_vault import Result, lifecycle, notes, zotero
from tests.fakes import FakeZotero

FIXTURES = Path(__file__).parent / "fixtures" / "lifecycle"


def _map(name):
    return json.loads((FIXTURES / name).read_text())


def _prov(
    item_key="ALKT2NF7", version=0, citation_key="alkt2026", attachments=(), fulltext=()
):
    return notes.Provenance(
        "Tdoqsn2J4q4h",
        item_key,
        version,
        citation_key,
        tuple(attachments),
        tuple(fulltext),
        None,
    )


def _live(items, trash, top):
    return lifecycle.Live(items, trash, top)


def _write_note(vault, provenance):
    """A literature note carrying exactly the tuple ``provenance`` records."""
    (vault / "literatures" / f"{provenance.citation_key}.md").write_text(
        '---\ntype: "literature"\n'
        f'zotero-server-id: "{provenance.server_id}"\n'
        f'zotero-item-key: "{provenance.item_key}"\n'
        f"zotero-item-version: {provenance.item_version}\n"
        f'citationKey: "{provenance.citation_key}"\n'
        "attachments:\nfulltext:\n---\n"
    )


def test_replaces_keys_accepts_a_uri_list_or_a_single_uri():
    assert lifecycle.replaces_keys(["http://zotero.org/users/1/items/T6GF6HH7"]) == {
        "T6GF6HH7"
    }
    assert lifecycle.replaces_keys("http://zotero.org/users/1/items/A1B2C3D4") == {
        "A1B2C3D4"
    }
    assert lifecycle.replaces_keys(None) == set()


def test_current_and_drifted_from_the_recorded_edit():
    before, after = _map("items-before.json"), _map("items-after-delete.json")
    top = {"ALKT2NF7": {"citationKey": "alkt2026", "replaces": set()}}
    assert lifecycle.classify(
        _prov(version=before["ALKT2NF7"]), _live(before, {}, top)
    ) == ("current", "")
    state, detail = lifecycle.classify(
        _prov(version=before["ALKT2NF7"]), _live(after, {}, top)
    )
    assert state == "drifted"
    assert "ALKT2NF7" in detail
    assert "1708" in detail


def test_child_version_moves_the_note_even_when_the_item_did_not():
    items = {"ALKT2NF7": 0, "ATT00001": 5}
    top = {"ALKT2NF7": {"citationKey": "alkt2026", "replaces": set()}}
    prov = _prov(
        attachments=(
            {
                "key": "ATT00001",
                "version": 4,
                "md5": "x",
                "contentType": "",
                "filename": "",
            },
        )
    )
    state, detail = lifecycle.classify(prov, _live(items, {}, top))
    assert state == "drifted"
    assert "ATT00001" in detail


def test_rekeyed_when_the_live_citation_key_differs():
    top = {"ALKT2NF7": {"citationKey": "alkt2026a", "replaces": set()}}
    assert lifecycle.classify(_prov(), _live({"ALKT2NF7": 0}, {}, top)) == (
        "re-keyed",
        "alkt2026 → alkt2026a",
    )


def test_a_trashed_attachment_outranks_a_re_key():
    """§3.4 step 6: trashed precedes re-keyed, and step 4 makes any key in the
    trash set — an attachment's included — a trashed note."""
    top = {"ALKT2NF7": {"citationKey": "alkt2026a", "replaces": set()}}
    prov = _prov(
        attachments=(
            {
                "key": "ATT00001",
                "version": 4,
                "md5": "x",
                "contentType": "",
                "filename": "",
            },
        )
    )
    assert lifecycle.classify(prov, _live({"ALKT2NF7": 0}, {"ATT00001": 4}, top)) == (
        "trashed",
        "ATT00001",
    )


def test_merged_outranks_trashed_and_deleted():
    top = {"NEW00001": {"citationKey": "new2026", "replaces": {"ALKT2NF7"}}}
    assert lifecycle.classify(
        _prov(), _live({"NEW00001": 1}, {"ALKT2NF7": 9}, top)
    ) == ("merged", "NEW00001")
    assert lifecycle.classify(_prov(), _live({"NEW00001": 1}, {}, top)) == (
        "merged",
        "NEW00001",
    )


def test_trashed_and_deleted_from_the_sitting():
    prov = _prov(item_key="II7E6CVR", version=1711, citation_key="sitting2026")
    trashed = lifecycle.classify(
        prov, _live(_map("items-after-delete.json"), _map("trash-trashed.json"), {})
    )
    assert trashed == ("trashed", "II7E6CVR")
    deleted = lifecycle.classify(
        prov,
        _live(_map("items-after-delete.json"), _map("trash-after-delete.json"), {}),
    )
    assert deleted == ("deleted", "II7E6CVR")


def test_lint_reads_three_routes_with_the_recorded_server_id(tmp_vault, monkeypatch):
    fake = FakeZotero(server_id="Tdoqsn2J4q4h")
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={"ALKT2NF7": 0},
        headers={"Last-Modified-Version": "1707"},
    )
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[
            {
                "key": "ALKT2NF7",
                "version": 0,
                "data": {"citationKey": "alkt2026", "relations": {}},
            }
        ],
    )
    note = tmp_vault / "literatures" / "alkt2026.md"
    note.write_text(
        '---\ntype: "literature"\nzotero-server-id: "Tdoqsn2J4q4h"\nzotero-item-key: "ALKT2NF7"\n'
        'zotero-item-version: 0\ncitationKey: "alkt2026"\nattachments:\nfulltext:\n'
        'generated: {by: "research_vault/0.1.0", at: "2026-09-07T00:00:00Z"}\n---\n'
    )
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    outcomes = lifecycle.lint_lifecycle(tmp_vault, client)
    assert [(o.target, o.result) for o in outcomes] == [("alkt2026", Result.MATCHED)]
    assert all(
        call[2].get("Zotero-Server-ID") == "Tdoqsn2J4q4h"
        for call in fake.calls
        if call[0] == "GET"
    )
    assert [call[1] for call in fake.calls if call[0] == "GET"] == [
        "/api/users/0/items?since=0&format=versions",
        "/api/users/0/items/trash?format=versions",
        "/api/users/0/items/top?format=json",
    ]


def test_database_changed_stops_and_reports_once(tmp_vault, monkeypatch):
    # production answers, the tuple says test
    fake = FakeZotero(server_id="6LpvURP2E933")
    note = tmp_vault / "literatures" / "alkt2026.md"
    note.write_text(
        '---\ntype: "literature"\nzotero-server-id: "Tdoqsn2J4q4h"\nzotero-item-key: "ALKT2NF7"\n'
        'zotero-item-version: 0\ncitationKey: "alkt2026"\nattachments:\nfulltext:\n---\n'
    )
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    (outcome,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert (outcome.check, outcome.target, outcome.result) == (
        "lifecycle",
        "vault",
        Result.UNMATCHED,
    )
    assert outcome.reason.startswith("database-changed")


def test_outage_never_reads_as_a_classification(tmp_vault, monkeypatch):
    fake = FakeZotero()
    note = tmp_vault / "literatures" / "alkt2026.md"
    note.write_text(
        '---\ntype: "literature"\nzotero-server-id: "6LpvURP2E933"\nzotero-item-key: "ALKT2NF7"\n'
        'zotero-item-version: 0\ncitationKey: "alkt2026"\nattachments:\nfulltext:\n---\n'
    )
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    monkeypatch.setattr(
        client,
        "_http",
        lambda *a, **k: (_ for _ in ()).throw(zotero.ZoteroError("down")),
    )
    (outcome,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason.startswith("outage")


def test_the_api_off_403_is_a_refusal_not_an_outage(tmp_vault, monkeypatch):
    _write_note(tmp_vault, _prov())
    # The fake answers 412 to any server id but its own before it consults its
    # table (tests/fakes.py, FakeZotero._http), so it must carry the id the
    # tuple records for the 403 row to be reached at all.
    fake = FakeZotero(server_id="Tdoqsn2J4q4h")
    fake.get("/api/users/0/items?since=0&format=versions", status=403, body=b"")
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    (outcome,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith("not-admitted — ")
    assert (
        lifecycle.blocked("lifecycle", "vault", zotero.ZoteroError("down")).result
        is Result.UNREACHABLE
    )


def test_verify_offline_reports_the_held_leg_as_synthetic_unreachable(fixture_vault):
    from research_vault import verify

    report, effective, _hashes, _warn = verify.verify_state(
        fixture_vault, network=False
    )
    lifecycle_rows = [o for o in report["outcomes"] if o.check == "lifecycle"]
    assert len(lifecycle_rows) == 1
    assert lifecycle_rows[0].result is Result.UNREACHABLE
    assert lifecycle_rows[0].extra.get("synthetic_offline") is True
    assert not [o for o in effective if o.check == "lifecycle"]


def test_lint_lifecycle_with_no_captured_notes_is_skipped_and_asks_nothing(
    tmp_vault, monkeypatch
):
    fake = FakeZotero()
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    (outcome,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert outcome.result is Result.SKIPPED
    assert outcome.reason == "no-identifier — no note carries a provenance tuple"
    assert fake.calls == []  # decision 26: an empty vault does not wait on Zotero


def test_verify_online_runs_the_linter_against_the_configured_base(
    fixture_vault, monkeypatch
):
    """The one code path (§3.4): verify's network run calls the linter with a
    client built on the ``base`` it was given — the parameter Task 2 had
    underscored as unread — and the fixture's captured notes come back
    classified."""
    from research_vault import verify

    # The fixture's other note records `SMITH2020`, nine characters, which
    # `notes.read_provenance` declines as an item key: it carries no tuple, so
    # the linter has nothing to say about it and only `gone2019` is classified.
    fake = FakeZotero()  # the production id the fixture notes record
    fake.get("/api/users/0/items?since=0&format=versions", body={"GONE2019": 7})
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[{"key": "GONE2019", "data": {"citationKey": "gone2019"}}],
    )
    bases = []

    def client(base):
        bases.append(base)
        return fake.install(zotero.ZoteroClient(base=base), monkeypatch)

    monkeypatch.setattr(verify, "ZoteroClient", client)
    monkeypatch.setattr(verify, "_network_outcomes", lambda *_args: [])
    report, effective, _hashes, _warn = verify.verify_state(
        fixture_vault, network=True, base="http://zotero.invalid:1"
    )
    rows = {o.target: o.result for o in report["outcomes"] if o.check == "lifecycle"}
    assert rows == {"gone2019": Result.MATCHED}
    assert bases == ["http://zotero.invalid:1"]
    assert all(o.extra.get("synthetic_offline") is None for o in effective)
