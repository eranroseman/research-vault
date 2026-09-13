import json

import pytest

from research_vault import Result, capture, frontmatter, notes, zotero
from tests.fakes import ITEM, FakeZotero, canned_item

LIBRARY = [
    {
        "id": "jakesch.etal2023a",
        "citation-key": "jakesch.etal2023a",
        "type": "paper-conference",
        "title": "T",
    }
]


def _client(monkeypatch, fake):
    return fake.install(zotero.ZoteroClient(), monkeypatch)


def _canned_run(fake, items=(ITEM,)):
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={"E352DFS8": 544, "D7EJ9FTG": 551, "N0TE0001": 552},
        headers={"Last-Modified-Version": "565"},
    )
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=list(items),
        headers={"Last-Modified-Version": "565"},
    )
    fake.get(
        "/api/users/0/items/top?format=versions",
        body={"E352DFS8": 544},
        headers={"Last-Modified-Version": "565"},
    )
    fake.get("/better-bibtex/library?/My%20Library.json", body=LIBRARY)
    return fake


def test_capture_writes_note_text_layer_and_csl_file(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)

    outcomes = capture.capture(tmp_vault, client, ["jakesch.etal2023a"])

    assert [(o.target, o.result, o.reason) for o in outcomes] == [
        ("jakesch.etal2023a", Result.MATCHED, "matched"),
        ("system/bibliography.json", Result.MATCHED, "matched"),
    ]
    note = tmp_vault / "literatures" / "jakesch.etal2023a.md"
    data, _body = frontmatter.parse(note.read_text())
    assert data["zotero-server-id"] == "6LpvURP2E933"
    assert data["zotero-item-version"] == 544
    assert data["attachments"][0]["version"] == 551
    text = tmp_vault / "fulltext" / "D7EJ9FTG.md"
    assert text.is_file()
    assert data["fulltext"][0]["sha256"] == data["compile-input-sha256"]
    assert (
        json.loads((tmp_vault / "system" / "bibliography.json").read_text())[0]["id"]
        == "jakesch.etal2023a"
    )
    assert (tmp_vault / "log.md").is_file()


def test_capture_accepts_an_item_key_and_resolves_a_citation_key(
    tmp_vault, monkeypatch
):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    assert capture.resolve_keys(
        client, ["E352DFS8", "jakesch.etal2023a", "nobody2020"]
    ) == {
        "E352DFS8": "E352DFS8",
        "jakesch.etal2023a": "E352DFS8",
        "nobody2020": None,
    }
    outcomes = capture.capture(tmp_vault, client, ["nobody2020"])
    assert outcomes[0].result is Result.UNMATCHED
    assert outcomes[0].reason.startswith("not-admitted")


def test_second_run_is_a_noop_and_keeps_generated(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"], now=_at("2026-09-07T10:00:00Z"))
    first = (tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text()
    outcomes = capture.capture(
        tmp_vault, client, ["E352DFS8"], now=_at("2026-09-08T10:00:00Z")
    )
    assert outcomes[0].reason == "matched — NOOP"
    assert (tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text() == first


def _at(text):
    import datetime

    return datetime.datetime.fromisoformat(text)


def test_refresh_after_compile_embeds_the_page_and_completes_the_note(
    tmp_vault, monkeypatch
):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    note = tmp_vault / "literatures" / "jakesch.etal2023a.md"
    assert (
        "## Compiled" not in note.read_text()
    )  # capture runs before compile (§3.3 step 5)
    ledger = tmp_vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(
        json.dumps(
            {
                "schema": "claude-obsidian.source-ledger.v1",
                "sources": {
                    "src-1": {
                        "origin": {"kind": "file", "locator": "fulltext/D7EJ9FTG.md"},
                        "pages": ["wiki/sources/Co-Writing.md"],
                    },
                },
            }
        )
    )
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert (
        outcomes[0].reason == "matched"
    )  # the second write is what completes the note
    assert (
        "## Compiled\n\n![[wiki/sources/Co-Writing.md]]\n\n## Item\n"
        in note.read_text()
    )
    assert (
        capture.capture(tmp_vault, client, ["E352DFS8"])[0].reason == "matched — NOOP"
    )


def test_an_unreadable_ledger_holds_the_item_and_leaves_the_note_alone(
    tmp_vault, monkeypatch
):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    note = tmp_vault / "literatures" / "jakesch.etal2023a.md"
    before = note.read_text()
    ledger = tmp_vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("{not json")
    held = [
        o
        for o in capture.capture(tmp_vault, client, ["E352DFS8"])
        if o.target == "jakesch.etal2023a"
    ]
    assert [o.result for o in held] == [Result.UNREACHABLE]
    assert held[0].reason.startswith(
        "outage — wiki/meta/ledgers/source-ledger.json unreadable"
    )
    assert (
        note.read_text() == before
    )  # not rewritten from a view that could not be read


def test_read_restarts_when_the_item_moves_mid_read(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    versions = iter([544, 545, 545, 545])
    real_item = client.item

    def moving_item(key):
        envelope = json.loads(json.dumps(real_item(key)))
        envelope["version"] = envelope["data"]["version"] = next(versions)
        return envelope

    monkeypatch.setattr(client, "item", moving_item)
    read = capture.read_item(client, "E352DFS8")
    assert read.version == 545
    assert read.item["data"]["citationKey"] == "jakesch.etal2023a"


def test_no_usable_text_writes_the_note_and_files_no_fulltext(tmp_vault, monkeypatch):
    partial = {"content": "x" * 900, "indexedPages": 100, "totalPages": 143}
    fake = _canned_run(canned_item(FakeZotero(), fulltext=partial))
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    reasons = [
        (o.result, o.reason) for o in outcomes if o.target == "jakesch.etal2023a"
    ]
    assert reasons == [
        (Result.MATCHED, "matched"),
        (Result.UNMATCHED, "no-fulltext — D7EJ9FTG partial — indexedPages 100 of 143"),
    ]
    data, _ = frontmatter.parse(
        (tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text()
    )
    assert "compile-input-sha256" not in data
    assert data["fulltext"] == []
    assert not (tmp_vault / "fulltext").exists()


def test_url_only_item_without_attachment_is_skipped_not_a_finding(
    tmp_vault, monkeypatch, capsys
):
    import research_vault.__main__ as cli
    from research_vault import inbox

    webpage = json.loads(json.dumps(ITEM))
    webpage["data"]["itemType"] = "webpage"
    webpage["links"] = {}
    fake = _canned_run(
        canned_item(FakeZotero(), item=webpage, children=()), items=(webpage,)
    )
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert [
        (o.result, o.reason) for o in outcomes if o.target == "jakesch.etal2023a"
    ] == [
        (Result.MATCHED, "matched"),
        (
            Result.SKIPPED,
            "no-fulltext — no attachment to read (webpage); text checks do not apply",
        ),
    ]
    assert (tmp_vault / "literatures" / "jakesch.etal2023a.md").is_file()
    monkeypatch.setattr(cli, "ZoteroClient", lambda base=None: client)
    assert cli.main(["capture", "E352DFS8", "--vault", str(tmp_vault)]) == 0
    assert "SKIPPED jakesch.etal2023a — no-fulltext" in capsys.readouterr().out
    assert not [
        f for f in inbox.load(tmp_vault) if f.check == "capture"
    ]  # nothing to clear, so nothing filed


def test_an_unreadable_machine_json_is_a_refusal_not_the_production_default(
    tmp_vault, monkeypatch, capsys
):
    import research_vault.__main__ as cli

    (tmp_vault / ".research-vault").mkdir(exist_ok=True)
    (tmp_vault / ".research-vault" / "machine.json").write_text("{not json")
    assert (
        zotero.base_for(tmp_vault, None, strict=False) == zotero.DEFAULT_BASE
    )  # doctor's tolerant read
    # A malformed machine.json must not resolve to the production instance.
    with pytest.raises(zotero.ZoteroError) as caught:
        zotero.base_for(tmp_vault, None)
    assert caught.value.result is Result.UNMATCHED
    assert "machine.json unreadable" in str(caught.value)
    assert cli.main(["capture", "E352DFS8", "--vault", str(tmp_vault)]) == 2
    assert "machine.json unreadable" in capsys.readouterr().err


def test_unkeyed_item_is_reported_not_written(tmp_vault, monkeypatch):
    unkeyed = json.loads(json.dumps(ITEM))
    unkeyed["data"]["citationKey"] = None
    fake = _canned_run(canned_item(FakeZotero(), item=unkeyed), items=(unkeyed,))
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"], key_wait_seconds=0)
    assert outcomes[0].result is Result.UNMATCHED
    assert outcomes[0].reason.startswith("unkeyed")
    assert not list((tmp_vault / "literatures").glob("*.md"))


def test_capture_runs_the_linter_first_and_refuses_a_trashed_item(
    tmp_vault, monkeypatch
):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={"D7EJ9FTG": 551},
        headers={"Last-Modified-Version": "566"},
    )
    fake.get("/api/users/0/items/trash?format=versions", body={"E352DFS8": 566})
    before = (tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text()
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert outcomes[0].reason.startswith("trashed — ")
    assert (tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text() == before


def test_database_changed_aborts_before_any_write(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    fake.server_id = "Tdoqsn2J4q4h"
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert [(o.target, o.result) for o in outcomes] == [("vault", Result.UNMATCHED)]
    assert outcomes[0].reason.startswith("database-changed")


def test_csl_file_falls_back_to_item_export_when_the_library_route_breaks(
    tmp_vault, monkeypatch
):
    fake = _canned_run(canned_item(FakeZotero()))
    fake.get("/better-bibtex/library?/My%20Library.json", status=500, body=b"")
    fake.rpc("item.export", LIBRARY)
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert outcomes[-1].reason == "matched — item.export fallback"
    assert (
        "RPC",
        "item.export",
        {"params": [["jakesch.etal2023a"], "Better CSL JSON"]},
    ) in fake.calls


def test_library_route_is_reread_once_when_zotero_moved_during_the_run(
    tmp_vault, monkeypatch
):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    seen = iter(["565", "570"])
    original = fake._http

    def moving(url, data=None, headers=None, method=None, *, timeout=None):
        response = original(url, data, headers, method, timeout=timeout)
        if url.endswith("/items/top?format=versions"):
            return zotero.Response(
                response.status,
                response.body,
                {**response.headers, "Last-Modified-Version": next(seen, "570")},
            )
        return response

    monkeypatch.setattr(client, "_http", moving)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    library_reads = [c for c in fake.calls if c[1].startswith("/better-bibtex/library")]
    assert len(library_reads) == 2


def test_cli_capture_exit_codes_and_holds(tmp_vault, monkeypatch, capsys):
    import research_vault.__main__ as cli

    fake = _canned_run(canned_item(FakeZotero()))
    monkeypatch.setattr(
        cli,
        "ZoteroClient",
        lambda **kw: fake.install(zotero.ZoteroClient(**kw), monkeypatch),
    )
    assert cli.main(["capture", "E352DFS8", "--vault", str(tmp_vault)]) == 0
    assert cli.main(["capture", "nobody2020", "--vault", str(tmp_vault)]) == 1
    queue = (tmp_vault / "inbox" / "review-queue.md").read_text()
    assert "[check:: capture]" in queue
    assert "not-admitted" in queue


def test_cli_capture_all_files_a_repo_path_hold_that_an_ack_closes(
    tmp_vault, monkeypatch
):
    """A note with no citationKey is a repo-path target (`_every_note`); the
    hold `_hold` files for it must carry that target kind through
    `record_finding` to `inbox.append_entry`, or `inbox.is_acknowledged`'s
    repo-path lookup — the one `verify`'s dedup uses — can never match the id
    a human acknowledgment references."""
    import research_vault.__main__ as cli
    from research_vault import inbox

    (tmp_vault / "literatures").mkdir(parents=True, exist_ok=True)
    (tmp_vault / "literatures" / "nameless.md").write_text(
        '---\ntype: "literature"\n---\n'
    )
    fake = FakeZotero()
    fake.get(
        "/api/users/0/items/top?format=versions",
        body={},
        headers={"Last-Modified-Version": "1"},
    )
    monkeypatch.setattr(
        cli,
        "ZoteroClient",
        lambda **kw: fake.install(zotero.ZoteroClient(**kw), monkeypatch),
    )
    assert cli.main(["capture", "--all", "--vault", str(tmp_vault)]) == 1

    entries = [e for e in inbox.load(tmp_vault) if e.check == "capture"]
    assert len(entries) == 1
    entry = entries[0]
    assert entry.target_kind == "repo-path"

    inbox.append_ack(tmp_vault, entry.id, "manual — resolved", "human:tester")
    assert inbox.is_acknowledged(
        tmp_vault, entry.check, entry.target, target_kind=entry.target_kind
    )


def test_a_database_change_during_the_csl_read_voids_the_run_not_the_file(
    tmp_vault, monkeypatch
):
    """A 412 on the version read that brackets the library route is
    database-changed on the vault — every recorded version is void, and the
    CSL file records no server id, so it cannot carry that condition. The
    item.export fallback is JSON-RPC, which carries no server id either, so
    falling through would write the CSL file from whichever database now
    answers and call it a matched fallback. The per-item outcomes stay: they
    are the record of what was written before the database moved."""
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    original = fake._http
    answers = iter([200, 412])  # the run's own read answers; the CSL bracket is refused

    def changing(url, data=None, headers=None, method=None, *, timeout=None):
        if url.endswith("/items/top?format=versions") and next(answers, 412) == 412:
            return zotero.Response(412, b"does not match this server", {})
        return original(url, data, headers, method, timeout=timeout)

    monkeypatch.setattr(client, "_http", changing)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert [(o.target, o.result) for o in outcomes] == [
        ("jakesch.etal2023a", Result.MATCHED),
        ("vault", Result.UNMATCHED),
    ]
    assert outcomes[-1].reason.startswith("database-changed")
    assert not (tmp_vault / "system" / "bibliography.json").exists()
    assert not [c for c in fake.calls if c[0] == "RPC"]  # never item.export


def test_a_key_filled_during_the_wait_is_captured_at_its_post_fill_version(
    tmp_vault, monkeypatch
):
    """Better BibTeX's fill is a save that moves the item (sitting 2026-09-07:
    II7E6CVR 1710 on create, 1711 once keyed). The pass that saw the item
    unkeyed is re-read whole, so the tuple records the post-fill version and
    the next lifecycle lint does not report drift on an item add just made."""
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    real_item = client.item
    keyed = ("jakesch.etal2023a", 545)
    states = iter([(None, 544), (None, 544), keyed])  # first pass unkeyed, then filled

    def filling_item(key):
        envelope = json.loads(json.dumps(real_item(key)))
        citation_key, version = next(states, keyed)
        envelope["data"]["citationKey"] = citation_key
        envelope["version"] = envelope["data"]["version"] = version
        return envelope

    monkeypatch.setattr(client, "item", filling_item)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"], key_wait_seconds=0)
    assert outcomes[0].reason == "matched"
    data, _ = frontmatter.parse(
        (tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text()
    )
    assert data["citationKey"] == "jakesch.etal2023a"
    assert data["zotero-item-version"] == 545


def test_a_corrupt_existing_note_is_a_schema_violation_not_a_traceback(
    tmp_vault, monkeypatch
):
    """An existing note with unterminated frontmatter reaches render_note as a
    FrontmatterError. The linter cannot see that note (read_provenance declines
    it), so capture is the one place it becomes a finding — and it must be a
    finding on that item, not a traceback that ends the run."""
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    note = tmp_vault / "literatures" / "jakesch.etal2023a.md"
    csl = tmp_vault / "system" / "bibliography.json"
    assert [e["id"] for e in json.loads(csl.read_text())] == ["jakesch.etal2023a"]
    corrupt = '---\ntype: "literature"\nno closing delimiter\n'
    note.write_text(corrupt)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert [(o.target, o.result) for o in outcomes] == [
        ("E352DFS8", Result.UNMATCHED),
        ("system/bibliography.json", Result.MATCHED),
    ]
    assert outcomes[0].reason.startswith("schema-violation — ")
    assert note.read_text() == corrupt  # not rewritten over a note it could not read
    # The CSL file is regenerated from the captured set, which decision 08 defines
    # as the parseable notes: the corrupt note's entry is gone, and this run says
    # so only through the per-item finding. Task 15's captured-set lint is the
    # mechanism that names the gap between the two files.
    assert json.loads(csl.read_text()) == []


def test_a_refused_item_export_is_unmatched_not_an_outage(tmp_vault, monkeypatch):
    """Better BibTeX answers a JSON-RPC error envelope for a key list it will
    not export (a stale captured key after a re-key); the client types that
    UNMATCHED. The CSL step must keep that split rather than tell the operator
    to wait out an outage that will not end. The real _rpc parser runs over the
    fake transport so the envelope is typed the way the client types it."""
    fake = _canned_run(canned_item(FakeZotero()))
    fake.get("/better-bibtex/library?/My%20Library.json", status=500, body=b"")
    fake.post(
        "/better-bibtex/json-rpc",
        body={
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": "no item with citation key"},
            "id": 1,
        },
    )
    client = _client(monkeypatch, fake)
    monkeypatch.delattr(client, "_rpc")  # the class's real parser, over fake._http
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert (outcomes[-1].target, outcomes[-1].result) == (
        "system/bibliography.json",
        Result.UNMATCHED,
    )
    assert outcomes[-1].reason.startswith("not-admitted — JSON-RPC error")
    assert not (tmp_vault / "system" / "bibliography.json").exists()


def test_a_trashed_source_requested_by_citation_key_reports_trashed_not_not_admitted(
    tmp_vault, monkeypatch
):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={"D7EJ9FTG": 551},
        headers={"Last-Modified-Version": "566"},
    )
    fake.get("/api/users/0/items/trash?format=versions", body={"E352DFS8": 566})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[],
        headers={"Last-Modified-Version": "566"},
    )  # /items/top excludes trashed items: the exclusion this follow-up exists for
    by_key = capture.capture(tmp_vault, client, ["jakesch.etal2023a"])
    assert by_key[0].reason.startswith(
        "trashed — "
    )  # resolved through the tuple, not through /items/top
    refreshed = capture.capture(tmp_vault, client, [], refresh_all=True)
    assert refreshed[0].reason.startswith("trashed — ")


def test_csl_regeneration_needs_no_library_name_when_nothing_was_read(
    tmp_vault, monkeypatch
):
    fake = _canned_run(canned_item(FakeZotero()))
    fake.rpc("item.export", LIBRARY)
    client = _client(monkeypatch, fake)
    capture.capture(
        tmp_vault, client, ["E352DFS8"]
    )  # this run reads a name and takes the library route
    fake.calls.clear()
    outcomes = capture.capture(
        tmp_vault, client, ["GHOST001"]
    )  # 404: nothing read this run
    assert outcomes[0].reason.startswith("not-admitted")
    assert outcomes[-1].reason == "matched — item.export fallback"
    assert not [
        c for c in fake.calls if "better-bibtex/library" in c[1]
    ]  # no library route without a name


def test_a_note_recording_another_database_is_refused_not_read(tmp_vault, monkeypatch):
    """A mixed-id vault: the linter reports `database-changed` on that note alone
    (not on `vault`, so the run continues). Capturing it would re-home the note to
    this database's item of the same key, so the refuse set holds it — and the row
    is the linter's typed refusal, not a `not-admitted` from a read that should
    never have happened."""
    fake = _canned_run(canned_item(FakeZotero()))
    fake.rpc("item.export", LIBRARY)
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    other = tmp_vault / "literatures" / "other2020.md"
    other.write_text(
        '---\ntype: "literature"\ntitle: "Other"\n'
        'zotero-server-id: "Tdoqsn2J4q4h"\nzotero-item-key: "OTHER001"\n'
        'zotero-item-version: 1\ncitationKey: "other2020"\n'
        "attachments:\nfulltext:\n---\n"
    )
    before = other.read_text()
    outcomes = capture.capture(tmp_vault, client, ["other2020"])
    assert (outcomes[0].target, outcomes[0].result) == ("other2020", Result.UNMATCHED)
    assert outcomes[0].reason == "database-changed — note records Tdoqsn2J4q4h"
    assert other.read_text() == before
    assert not [c for c in fake.calls if c[1].endswith("/items/OTHER001?format=json")]


def test_a_mid_run_412_stamps_what_was_written_before_the_vault_row(
    tmp_vault, monkeypatch
):
    """The database moves between two items. The notes written before it moved are
    stamped and their log regenerated — the run's record of what it did — and the
    `vault` row ends the list. No CSL file: it would be written from the database
    that answered after the move."""
    second = json.loads(json.dumps(ITEM))
    second["key"] = second["data"]["key"] = "F441KKD2"
    second["data"]["citationKey"] = "second2023"
    second["links"] = {}
    fake = _canned_run(canned_item(FakeZotero()), items=(ITEM, second))
    canned_item(fake, item=second, children=())
    client = _client(monkeypatch, fake)
    real_item = client.item
    reads = []

    def flipping_item(key):
        reads.append(key)
        if len(reads) == 3:  # read_item reads twice per item: this is the second item's
            fake.server_id = "Tdoqsn2J4q4h"
        return real_item(key)

    monkeypatch.setattr(client, "item", flipping_item)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8", "F441KKD2"])
    assert [(o.target, o.result) for o in outcomes] == [
        ("jakesch.etal2023a", Result.MATCHED),
        ("vault", Result.UNMATCHED),
    ]
    assert outcomes[-1].reason.startswith("database-changed")
    assert (tmp_vault / "literatures" / "jakesch.etal2023a.md").is_file()
    # log.md is the discriminator: tmp_vault ships none, and the pre-fix early
    # return skipped okf.regenerate_log. (A `type` assertion on the note would be
    # vacuous — render_note writes that field on every write, stamped or not.)
    assert (tmp_vault / "log.md").is_file()
    assert not (tmp_vault / "system" / "bibliography.json").exists()


def test_refresh_all_reaches_a_note_that_carries_no_tuple(tmp_vault, monkeypatch):
    """An older vault's note has citationKey and no zotero-* fields; --all captures it by name."""
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    (tmp_vault / "literatures").mkdir(exist_ok=True)
    legacy = tmp_vault / "literatures" / "jakesch.etal2023a.md"
    legacy.write_text(
        '---\ntype: "literature"\ncitationKey: "jakesch.etal2023a"\n---\nold prose\n'
    )
    (tmp_vault / "literatures" / "nameless.md").write_text(
        '---\ntype: "literature"\n---\n'
    )
    outcomes = capture.capture(tmp_vault, client, [], refresh_all=True)
    rows = [(str(o.target), o.result, o.reason.split(" — ")[0]) for o in outcomes]
    assert ("jakesch.etal2023a", Result.MATCHED, "matched") in rows
    assert [r[1:] for r in rows if r[0].endswith("literatures/nameless.md")] == [
        (Result.UNMATCHED, "schema-violation")
    ]
    assert (
        notes.read_provenance(legacy.read_text()) is not None
    )  # the capture gave it its tuple
    assert (
        "old prose" not in legacy.read_text()
    )  # greenfield: rewritten whole from Zotero
