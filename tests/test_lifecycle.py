import json
from pathlib import Path

from research_vault import Result, fulltext, lifecycle, literature_notes, zotero
from tests.fakes import FakeZotero

FIXTURES = Path(__file__).parent / "fixtures" / "lifecycle"
_ATTACHMENT = {
    "key": "ATT00001",
    "version": 4,
    "md5": "aa11",
    "contentType": "application/pdf",
    "filename": "a.pdf",
}


def _map(name):
    return json.loads((FIXTURES / name).read_text())


def _prov(
    item_key="ALKT2NF7", version=0, citation_key="alkt2026", attachments=(), fulltext=()
):
    return literature_notes.Provenance(
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
    lines = [
        "---",
        'type: "literature"',
        f'zotero-server-id: "{provenance.server_id}"',
        f'zotero-item-key: "{provenance.item_key}"',
        f"zotero-item-version: {provenance.item_version}",
        f'citationKey: "{provenance.citation_key}"',
        "attachments:",
        *(
            f'  - {{key: "{a["key"]}", version: {a["version"]}, md5: "{a["md5"]}", '
            f'contentType: "{a["contentType"]}", filename: "{a["filename"]}"}}'
            for a in provenance.attachments
        ),
        "fulltext:",
        *(
            f'  - {{attachment-key: "{f["attachment-key"]}", sha256: "{f["sha256"]}"}}'
            for f in provenance.fulltext
        ),
        "---",
    ]
    (vault / "literature" / f"{provenance.citation_key}.md").write_text(
        "\n".join(lines) + "\n"
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


def test_trashed_transition_replays_from_the_live_snapshot():
    fixture = json.loads((FIXTURES / "items-trashed.json").read_text())
    (item_key,) = fixture["live"]
    prov = _prov(
        item_key=item_key, version=fixture["live"][item_key], citation_key="live2026"
    )
    assert lifecycle.classify(prov, _live(fixture["live"], {}, {}))[0] == "current"
    assert lifecycle.classify(
        prov, _live(fixture["trashed_items"], fixture["trashed_trash"], {})
    ) == ("trashed", item_key)


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
    note = tmp_vault / "literature" / "alkt2026.md"
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
    note = tmp_vault / "literature" / "alkt2026.md"
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
    note = tmp_vault / "literature" / "alkt2026.md"
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
    client built on the ``base`` it was given, and the fixture's captured
    notes come back classified."""
    from research_vault import verify

    fake = FakeZotero()  # the production id the fixture notes record
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={"SMITH020": 12, "ATT00001": 13, "GONE2019": 7},
    )
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[
            {"key": "SMITH020", "data": {"citationKey": "smith2020"}},
            {"key": "GONE2019", "data": {"citationKey": "gone2019"}},
        ],
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
    assert rows == {"smith2020": Result.MATCHED, "gone2019": Result.MATCHED}
    assert bases == ["http://zotero.invalid:1"]
    assert all(o.extra.get("synthetic_offline") is None for o in effective)


def test_a_purged_attachment_is_drift_not_trashed():
    """Absent from the versions map and not in the trash: the child was purged
    while the item stayed, which is a content change on a live item."""
    top = {"ALKT2NF7": {"citationKey": "alkt2026", "replaces": set()}}
    prov = _prov(attachments=(_ATTACHMENT,))
    assert lifecycle.classify(prov, _live({"ALKT2NF7": 0}, {}, top)) == (
        "drifted",
        "attachment ATT00001 absent",
    )


def _drift_fake(children):
    """The three reads with ATT00001 moved 4 → 5, plus the item's children route
    (``None`` leaves it unregistered, so the fake answers 404)."""
    fake = FakeZotero(server_id="Tdoqsn2J4q4h")
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={"ALKT2NF7": 0, "ATT00001": 5},
    )
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[{"key": "ALKT2NF7", "data": {"citationKey": "alkt2026"}}],
    )
    if children is not None:
        fake.get("/api/users/0/items/ALKT2NF7/children", body=children)
    return fake


def _drift_reason(tmp_vault, monkeypatch, fake, cached=()):
    _write_note(tmp_vault, _prov(attachments=(_ATTACHMENT,), fulltext=cached))
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    (outcome,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert outcome.result is Result.UNMATCHED
    return outcome.reason


def test_drift_detail_names_a_changed_file_and_a_stale_cache(tmp_vault, monkeypatch):
    """§3.4 step 5: the md5 moved with the version, and the cached text is gone."""
    fake = _drift_fake([{"key": "ATT00001", "data": {"md5": "bb22"}}])
    cached = ({"attachment-key": "ATT00001", "sha256": "0" * 64},)
    assert _drift_reason(tmp_vault, monkeypatch, fake, cached) == (
        "drift — attachment ATT00001 4 → 5; ATT00001: file changed, cached text stale"
    )


def test_drift_detail_names_a_metadata_only_move_with_a_current_cache(
    tmp_vault, monkeypatch
):
    fake = _drift_fake([{"key": "ATT00001", "data": {"md5": "aa11"}}])
    path = fulltext.path_for(tmp_vault, "ATT00001")
    path.parent.mkdir()
    path.write_bytes(b"cached text")
    cached = ({"attachment-key": "ATT00001", "sha256": fulltext.sha256_of(path)},)
    assert _drift_reason(tmp_vault, monkeypatch, fake, cached) == (
        "drift — attachment ATT00001 4 → 5; ATT00001: metadata only"
    )


def test_drift_detail_says_when_the_children_read_failed(tmp_vault, monkeypatch):
    """The verdict is already drift from the three reads; an unreadable children
    route withholds the refinement and says so, rather than guessing."""
    assert _drift_reason(tmp_vault, monkeypatch, _drift_fake(None)) == (
        "drift — attachment ATT00001 4 → 5; children unreadable"
    )


def test_drift_detail_is_silent_on_an_attachment_the_children_read_lacks(
    tmp_vault, monkeypatch
):
    assert _drift_reason(tmp_vault, monkeypatch, _drift_fake([])) == (
        "drift — attachment ATT00001 4 → 5"
    )


def test_an_item_only_drift_never_reads_the_children(tmp_vault, monkeypatch):
    fake = FakeZotero(server_id="Tdoqsn2J4q4h")
    fake.get("/api/users/0/items?since=0&format=versions", body={"ALKT2NF7": 1708})
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[{"key": "ALKT2NF7", "data": {"citationKey": "alkt2026"}}],
    )
    _write_note(tmp_vault, _prov())
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    (outcome,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert outcome.reason == "drift — item ALKT2NF7 0 → 1708"
    assert not [call for call in fake.calls if call[1].endswith("/children")]


def test_blocked_names_a_database_change_by_its_own_code():
    """A 412 is a typed refusal with a code of its own; `not-admitted` would hide
    it, and Tasks 13 and 17 route through here with no catch of their own."""
    outcome = lifecycle.blocked("capture", "vault", zotero.DatabaseChangedError())
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason == (
        "database-changed — Zotero-Server-ID does not match this server"
    )


def test_a_top_item_with_null_data_is_read_not_a_traceback(tmp_vault, monkeypatch):
    """`data: null` on one top-items row used to raise AttributeError past
    `lint_lifecycle`'s `except ZoteroError`, taking a verify run down with a
    traceback. The row reads as carrying no citation key
    and no relations; the note classifies from the versions map as before."""
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
            {"key": "ALKT2NF7", "version": 0, "data": None},
            {"key": "OTHER001", "version": 0, "data": {"relations": "not-a-map"}},
        ],
    )
    _write_note(tmp_vault, _prov())
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    outcomes = lifecycle.lint_lifecycle(tmp_vault, client)
    assert [(o.target, o.result) for o in outcomes] == [("alkt2026", Result.MATCHED)]


# --- boundaries pinned against mutation survivors -----------------------------


def test_replaces_keys_takes_the_last_segment_and_ignores_non_strings():
    """A trailing slash, a key ending in X, an empty string and a non-string
    value: the key is the last path segment, and only non-empty strings count."""
    assert lifecycle.replaces_keys(
        ["http://zotero.org/users/1/items/T6GF6HH7/", "", 7, None]
    ) == {"T6GF6HH7"}
    assert lifecycle.replaces_keys("http://zotero.org/users/1/items/ABCDEFGX/") == {
        "ABCDEFGX"
    }
    assert lifecycle.replaces_keys([""]) == set()


def test_read_live_reads_replaces_from_the_dc_relations(tmp_vault, monkeypatch):
    fake = FakeZotero(server_id="Tdoqsn2J4q4h")
    fake.get("/api/users/0/items?since=0&format=versions", body={"NEW00001": 9})
    fake.get("/api/users/0/items/trash?format=versions", body={"OLD00001": 8})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[
            {
                "key": "NEW00001",
                "data": {
                    "citationKey": "new2026",
                    "relations": {
                        "dc:replaces": ["http://zotero.org/users/1/items/OLD00001"]
                    },
                },
            }
        ],
    )
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    live = lifecycle.read_live(client)
    assert live.top == {
        "NEW00001": {"citationKey": "new2026", "replaces": {"OLD00001"}}
    }
    assert (live.versions, live.trash) == ({"NEW00001": 9}, {"OLD00001": 8})


def test_drift_detail_refines_every_moved_attachment_and_skips_shapeless_children(
    tmp_vault, monkeypatch
):
    """Two attachments, the first unmoved and the second moved, with a child
    envelope without `data` in the children read: the moved one is refined
    (file changed, no cache to judge -- so no "cached text stale") and the
    unmoved one is passed over without ending the walk."""
    second = dict(_ATTACHMENT, key="ATT00002", md5="cc33")
    fake = FakeZotero(server_id="Tdoqsn2J4q4h")
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={"ALKT2NF7": 0, "ATT00001": 4, "ATT00002": 5},
    )
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[{"key": "ALKT2NF7", "data": {"citationKey": "alkt2026"}}],
    )
    fake.get(
        "/api/users/0/items/ALKT2NF7/children",
        body=[
            {"key": "N0DATA01"},
            {"key": "ATT00001", "data": {"md5": "aa11"}},
            {"key": "ATT00002", "data": {"md5": "dd44"}},
        ],
    )
    _write_note(tmp_vault, _prov(attachments=(_ATTACHMENT, second)))
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    (outcome,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert outcome.reason == (
        "drift — attachment ATT00002 4 → 5; ATT00002: file changed"
    )


def test_drift_detail_joins_two_refinements_with_a_semicolon(tmp_vault, monkeypatch):
    second = dict(_ATTACHMENT, key="ATT00002", md5="cc33")
    fake = FakeZotero(server_id="Tdoqsn2J4q4h")
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={"ALKT2NF7": 0, "ATT00001": 5, "ATT00002": 5},
    )
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[{"key": "ALKT2NF7", "data": {"citationKey": "alkt2026"}}],
    )
    fake.get(
        "/api/users/0/items/ALKT2NF7/children",
        body=[
            {"key": "ATT00001", "data": {"md5": "aa11"}},
            {"key": "ATT00002", "data": {"md5": "dd44"}},
        ],
    )
    _write_note(tmp_vault, _prov(attachments=(_ATTACHMENT, second)))
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    (outcome,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert outcome.reason == (
        "drift — attachment ATT00001 4 → 5; attachment ATT00002 4 → 5; "
        "ATT00001: metadata only; ATT00002: file changed"
    )


def test_the_vault_rows_name_the_vault_target(tmp_vault, monkeypatch):
    """The decision-26 SKIPPED row of a tupleless vault and the outage row of
    a failed read both target `vault`, with their full reasons."""
    client = FakeZotero(server_id="Tdoqsn2J4q4h").install(
        zotero.ZoteroClient(), monkeypatch
    )
    (skipped,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert (skipped.check, skipped.target, skipped.result, skipped.reason) == (
        "lifecycle",
        "vault",
        Result.SKIPPED,
        "no-identifier — no note carries a provenance tuple",
    )
    _write_note(tmp_vault, _prov())
    monkeypatch.setattr(
        client,
        "_http",
        lambda *a, **k: (_ for _ in ()).throw(zotero.ZoteroError("down")),
    )
    (outage,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert (outage.check, outage.target, outage.result, outage.reason) == (
        "lifecycle",
        "vault",
        Result.UNREACHABLE,
        "outage — down",
    )


def test_provenances_skip_an_unreadable_note_and_keep_reading(tmp_vault):
    (tmp_vault / "literature" / "a-dir.md").mkdir()
    (tmp_vault / "literature" / "b-latin1.md").write_bytes(b"---\ntitle: \xe9\n---\n")
    _write_note(tmp_vault, _prov())
    found = lifecycle._provenances(tmp_vault)
    assert [(p.name, prov.citation_key) for p, prov in found] == [
        ("alkt2026.md", "alkt2026")
    ]


def test_lint_lifecycle_rows_every_note_after_a_foreign_one_and_a_current_one(
    tmp_vault, monkeypatch
):
    """Three notes in path order: one recording another database (rowed,
    passed over), one current (matched), one moved (drift) -- the walk reaches
    all three."""
    fake = FakeZotero(server_id="Tdoqsn2J4q4h")
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={"ALKT2NF7": 0, "MOVED001": 3},
    )
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[
            {"key": "ALKT2NF7", "data": {"citationKey": "alkt2026"}},
            {"key": "MOVED001", "data": {"citationKey": "moved2026"}},
        ],
    )
    foreign = literature_notes.Provenance(
        "Zzzzzzzzzzzz", "FOREIGN1", 0, "a-foreign2026", (), (), None
    )
    _write_note(tmp_vault, foreign)
    _write_note(tmp_vault, _prov())
    _write_note(tmp_vault, _prov(item_key="MOVED001", citation_key="moved2026"))
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    outcomes = lifecycle.lint_lifecycle(tmp_vault, client)
    assert [(o.target, o.result, o.reason) for o in outcomes] == [
        (
            "a-foreign2026",
            Result.UNMATCHED,
            "database-changed — note records Zzzzzzzzzzzz",
        ),
        ("alkt2026", Result.MATCHED, "matched"),
        ("moved2026", Result.UNMATCHED, "drift — item MOVED001 0 → 3"),
    ]


def test_read_live_skips_a_null_top_item_row():
    """Residual 1: `_validate_object_list` refuses the row in the real client;
    the guard here is defence in depth for a stub that does not."""

    class Stub:
        def versions(self):
            return {}, {}

        def trash_versions(self):
            return {}

        def top_items(self):
            return [None, {"key": "E352DFS8", "data": {"citationKey": "a"}}], {}

    live = lifecycle.read_live(Stub())
    assert list(live.top) == ["E352DFS8"]
