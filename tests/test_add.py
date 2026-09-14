import json

import pytest

from research_vault import Result, capture, zotero
from tests.fakes import ITEM, FakeZotero, canned_item


def _fake_for_add(monkeypatch):
    fake = canned_item(FakeZotero())
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={},
        headers={"Last-Modified-Version": "1"},
    )
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[ITEM],
        headers={"Last-Modified-Version": "1"},
    )
    fake.get(
        "/api/users/0/items/top?format=versions",
        body={},
        headers={"Last-Modified-Version": "1"},
    )
    fake.get(
        "/better-bibtex/library?/My%20Library.json",
        body=[{"id": "jakesch.etal2023a", "type": "paper-conference"}],
    )
    fake.post("/api/local/authorize", body={"key": "k" * 32, "remember": True})
    fake.post(
        "/api/users/0/items",
        body={
            "successful": {"0": {"key": "E352DFS8", "version": 544}},
            "unchanged": {},
            "failed": {},
        },
    )
    return fake, fake.install(zotero.ZoteroClient(), monkeypatch)


def test_add_authorizes_once_stores_the_key_creates_and_captures(
    tmp_vault, monkeypatch
):
    fake, client = _fake_for_add(monkeypatch)
    items = [
        {
            "itemType": "journalArticle",
            "title": "T",
            "creators": [{"creatorType": "author", "lastName": "X"}],
        }
    ]
    outcomes = capture.add(tmp_vault, client, items, collection="IQZW5UVX")
    assert outcomes[0].reason == "matched — created E352DFS8"
    assert (tmp_vault / "literatures" / "jakesch.etal2023a.md").is_file()
    store = tmp_vault / ".research-vault" / "zotero-keys.json"
    assert json.loads(store.read_text()) == {"6LpvURP2E933": "k" * 32}
    assert oct(store.stat().st_mode & 0o777) == "0o600"
    posts = [c for c in fake.calls if c[0] == "POST"]
    assert [p[1] for p in posts] == ["/api/local/authorize", "/api/users/0/items"]
    sent = json.loads(fake._last_post_body)
    assert sent[0]["collections"] == ["IQZW5UVX"]

    # A fresh client per call is what production does (`cmd_add` builds one
    # each invocation); the "authorize once across runs" promise rests on
    # `_load_key` reading the store, not on the same client object surviving.
    fresh_client = fake.install(zotero.ZoteroClient(), monkeypatch)
    capture.add(tmp_vault, fresh_client, items)
    assert [c[1] for c in fake.calls if c[0] == "POST"].count(
        "/api/local/authorize"
    ) == 1


def test_add_refuses_unknown_fields_before_any_network(tmp_vault, monkeypatch):
    fake, client = _fake_for_add(monkeypatch)
    outcomes = capture.add(tmp_vault, client, [{"itemType": "book", "isbn": "x"}])
    assert outcomes[0].result is Result.UNMATCHED
    assert "unknown field isbn" in outcomes[0].reason
    assert not [c for c in fake.calls if c[0] == "POST"]


def test_add_uses_the_recorded_server_id_when_notes_exist(tmp_vault, monkeypatch):
    fake, client = _fake_for_add(monkeypatch)
    (tmp_vault / "literatures" / "x.md").write_text(
        '---\ntype: "literature"\nzotero-server-id: "Tdoqsn2J4q4h"\nzotero-item-key: "AAAA0000"\n'
        'zotero-item-version: 1\ncitationKey: "x"\nattachments:\nfulltext:\n---\n'
    )
    outcomes = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    assert outcomes[0].result is Result.UNMATCHED
    assert outcomes[0].reason.startswith("database-changed")
    assert not [c for c in fake.calls if c[0] == "POST" and c[1].endswith("/items")]


def test_add_reports_a_denied_dialog_and_a_failed_create(tmp_vault, monkeypatch):
    fake, client = _fake_for_add(monkeypatch)
    fake.post("/api/local/authorize", status=403, body={"denied": True})
    outcomes = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    assert outcomes[0].reason.startswith("not-admitted — authorization denied")
    fake.post("/api/local/authorize", body={"key": "k" * 32, "remember": False})
    fake.post(
        "/api/users/0/items",
        body={
            "successful": {},
            "unchanged": {},
            "failed": {"0": {"code": 400, "message": "bad"}},
        },
    )
    outcomes = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    assert outcomes[0].reason.startswith("mismatch — create failed")


def test_a_400_from_the_local_api_is_a_refusal_not_an_outage(tmp_vault, monkeypatch):
    """`lifecycle.blocked` spells the local API's refusal `not-admitted`, the
    same as a capture read's (row 49): one refusal, one spelling."""
    fake = FakeZotero()
    fake.rpc("api.ready", {"zotero": "10.0.1", "betterbibtex": "9.0.63"})
    fake.post("/api/local/authorize", body={"key": "k" * 32, "remember": True})
    fake.post("/api/users/0/items", status=400, body=b"Invalid item type 'bogus'")
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    (outcome,) = capture.add(tmp_vault, client, [{"itemType": "bogus", "title": "x"}])
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith(
        "not-admitted — local API 400 for /api/users/0/items"
    )


def test_a_400_body_containing_the_text_401_is_not_mistaken_for_a_rejected_key(
    tmp_vault, monkeypatch
):
    """`_local`'s 400 branch echoes up to 200 bytes of the server's own body;
    a 400 whose body happens to contain "401" must not be read as the typed
    `ApiKeyRejectedError` a real 401 raises — that would pop an extra
    authorize dialog and re-POST a payload Zotero already refused."""
    fake = FakeZotero()
    fake.post("/api/local/authorize", body={"key": "k" * 32, "remember": True})
    fake.post("/api/users/0/items", status=400, body=b"error 401: bogus item type")
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    (outcome,) = capture.add(tmp_vault, client, [{"itemType": "bogus", "title": "x"}])
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith(
        "not-admitted — local API 400 for /api/users/0/items"
    )
    posts = [c for c in fake.calls if c[0] == "POST"]
    assert [p[1] for p in posts] == ["/api/local/authorize", "/api/users/0/items"]


def test_store_key_replaces_a_non_object_store(tmp_vault, monkeypatch):
    """A valid-JSON store whose top level is not an object (a list, a string,
    a number) must not crash the write after the dialog is already granted —
    that would lose the just-granted key and re-dialog on every later run."""
    _fake, client = _fake_for_add(monkeypatch)
    store = tmp_vault / ".research-vault" / "zotero-keys.json"
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text("[]")
    outcomes = capture.add(
        tmp_vault, client, [{"itemType": "journalArticle", "title": "T"}]
    )
    assert outcomes[0].reason.startswith("matched — created")
    assert json.loads(store.read_text()) == {"6LpvURP2E933": "k" * 32}


def test_add_reauthorizes_once_after_a_401_and_retries(tmp_vault, monkeypatch):
    fake, client = _fake_for_add(monkeypatch)
    real_http = fake._http
    rejected_once = {"done": False}

    def flaky(url, data=None, headers=None, method=None, *, timeout=None):
        if (
            url.endswith("/api/users/0/items")
            and method == "POST"
            and not rejected_once["done"]
        ):
            rejected_once["done"] = True
            # Log it as `real_http` would have: this intercept short-circuits
            # before the fake's own call-recording line runs.
            fake.calls.append(("POST", "/api/users/0/items", dict(headers or {})))
            return zotero.Response(401, b"", {})
        return real_http(
            url, data=data, headers=headers, method=method, timeout=timeout
        )

    monkeypatch.setattr(client, "_http", flaky)
    outcomes = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    posts = [c for c in fake.calls if c[0] == "POST"]
    assert [p[1] for p in posts] == [
        "/api/local/authorize",
        "/api/users/0/items",
        "/api/local/authorize",
        "/api/users/0/items",
    ]
    # The rejected key must not ride the re-authorize request.
    assert "Zotero-API-Key" not in posts[2][2]
    assert outcomes[0].reason.startswith("matched — created")


def test_add_stops_after_one_retry_when_the_second_create_also_401s(
    tmp_vault, monkeypatch
):
    fake, client = _fake_for_add(monkeypatch)
    fake.post("/api/users/0/items", status=401, body=b"")
    outcomes = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    posts = [c for c in fake.calls if c[0] == "POST"]
    assert [p[1] for p in posts] == [
        "/api/local/authorize",
        "/api/users/0/items",
        "/api/local/authorize",
        "/api/users/0/items",
    ]
    assert outcomes[0].result is Result.UNMATCHED
    assert outcomes[0].reason.startswith("not-admitted — API key rejected")


def test_add_refuses_a_non_list_creators_or_tags_before_any_network(
    tmp_vault, monkeypatch
):
    fake, client = _fake_for_add(monkeypatch)
    outcomes = capture.add(
        tmp_vault, client, [{"itemType": "book", "creators": "not-a-list"}]
    )
    assert outcomes[0].result is Result.UNMATCHED
    assert "creators must be a list" in outcomes[0].reason
    outcomes = capture.add(tmp_vault, client, [{"itemType": "book", "tags": "ai"}])
    assert outcomes[0].result is Result.UNMATCHED
    assert "tags must be a list" in outcomes[0].reason
    assert not [c for c in fake.calls if c[0] == "POST"]


@pytest.mark.parametrize(
    ("route", "status", "expected"),
    [
        ("/api/local/authorize", 412, "database-changed — Zotero-Server-ID"),
        ("/api/users/0/items", 412, "database-changed — Zotero-Server-ID"),
        ("/api/users/0/items", 403, "not-admitted — local API preference is disabled"),
        ("/api/users/0/items", 500, "outage — local API HTTP 500"),
    ],
    ids=["authorize-412", "create-412", "create-403", "create-500"],
)
def test_add_routes_every_write_error_through_blocked(
    route, status, expected, tmp_vault, monkeypatch
):
    """A 412 on either write is `database-changed` — the one code the skill
    tells the agent to stop on — never `not-admitted` or `mismatch` (review
    I-2); a 403 is the preference a person can fix; a 500 is the outage."""
    fake, client = _fake_for_add(monkeypatch)
    fake.post(route, status=status, body=b"")
    (outcome,) = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    assert outcome.target == "add"
    assert outcome.result is (Result.UNREACHABLE if status == 500 else Result.UNMATCHED)
    assert outcome.reason.startswith(expected)
    assert not (tmp_vault / "literatures" / "jakesch.etal2023a.md").exists()


@pytest.mark.parametrize("successful", [None, [], "E352DFS8"])
def test_a_create_envelope_whose_successful_is_not_an_object_is_a_mismatch(
    successful, tmp_vault, monkeypatch
):
    """`successful` not a dict used to be an AttributeError after the item was
    already created (review I-5); it reads as no key created."""
    fake, client = _fake_for_add(monkeypatch)
    fake.post(
        "/api/users/0/items",
        body={"successful": successful, "unchanged": {}, "failed": {}},
    )
    (outcome,) = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith("mismatch — create failed")


def _cli_item(tmp_vault, payload):
    path = tmp_vault / "item.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def test_cli_add_creates_captures_and_prints_every_row(tmp_vault, monkeypatch, capsys):
    """`add` through the CLI: one object or a list in `--item`, the create row
    then capture's rows, exit 0, nothing held."""
    import research_vault.__main__ as cli
    from research_vault import inbox

    fake, client = _fake_for_add(monkeypatch)
    monkeypatch.setattr(cli, "ZoteroClient", lambda base=None: client)
    item = _cli_item(tmp_vault, {"itemType": "journalArticle", "title": "T"})
    assert (
        cli.main(
            [
                "add",
                "--vault",
                str(tmp_vault),
                "--item",
                item,
                "--collection",
                "IQZW5UVX",
            ]
        )
        == 0
    )
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "MATCHED add — matched — created E352DFS8"
    assert lines[1] == "MATCHED jakesch.etal2023a — matched"
    assert (tmp_vault / "literatures" / "jakesch.etal2023a.md").is_file()
    assert json.loads(fake._last_post_body)[0]["collections"] == ["IQZW5UVX"]
    assert not [f for f in inbox.load(tmp_vault) if f.check == "capture"]


def test_cli_add_holds_a_refusal_and_exits_1_and_a_denied_key_is_not_stored(
    tmp_vault, monkeypatch, capsys
):
    """A denied dialog is `not-admitted` on `add`: printed, held under check
    id `capture`, exit 1. A key granted with `remember: false` never reaches
    the store (row 50)."""
    import research_vault.__main__ as cli
    from research_vault import inbox

    fake, client = _fake_for_add(monkeypatch)
    monkeypatch.setattr(cli, "ZoteroClient", lambda base=None: client)
    item = _cli_item(tmp_vault, [{"itemType": "book", "title": "T"}])
    fake.post("/api/local/authorize", status=403, body={"denied": True})
    assert cli.main(["add", "--vault", str(tmp_vault), "--item", item]) == 1
    assert capsys.readouterr().out.startswith(
        "UNMATCHED add — not-admitted — authorization denied"
    )
    (held,) = [f for f in inbox.load(tmp_vault) if f.check == "capture"]
    assert (held.target, held.result) == ("add", Result.UNMATCHED.value)
    store = tmp_vault / ".research-vault" / "zotero-keys.json"
    fake.post("/api/local/authorize", body={"key": "k" * 32, "remember": False})
    assert cli.main(["add", "--vault", str(tmp_vault), "--item", item]) == 0
    assert not store.exists()


@pytest.mark.parametrize(
    "content", [None, "{not json", b"\xff\xfe"], ids=["absent", "not-json", "not-utf8"]
)
def test_cli_add_with_an_unreadable_item_file_is_exit_2(
    content, tmp_vault, monkeypatch, capsys
):
    """A file the verb cannot even read is "could not run" (exit 2), never a
    four-state verdict, and nothing reaches Zotero."""
    import research_vault.__main__ as cli

    path = tmp_vault / "item.json"
    if isinstance(content, bytes):
        path.write_bytes(content)
    elif content is not None:
        path.write_text(content)
    fake, client = _fake_for_add(monkeypatch)
    monkeypatch.setattr(cli, "ZoteroClient", lambda base=None: client)
    assert cli.main(["add", "--vault", str(tmp_vault), "--item", str(path)]) == 2
    assert capsys.readouterr().err.startswith("add: cannot read --item:")
    assert not [c for c in fake.calls if c[0] == "POST"]


def test_cli_add_reports_a_named_failure_as_exit_2(tmp_vault, monkeypatch, capsys):
    """Same contract as `cmd_capture` (review M-2): a named failure outside
    the verb's own four-state handling is exit 2 with a stderr line."""
    import research_vault.__main__ as cli

    _fake, client = _fake_for_add(monkeypatch)
    monkeypatch.setattr(cli, "ZoteroClient", lambda base=None: client)
    item = _cli_item(tmp_vault, {"itemType": "book", "title": "T"})

    def failing(*_args, **_kwargs):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(capture, "_store_key", failing)
    assert cli.main(["add", "--vault", str(tmp_vault), "--item", item]) == 2
    assert capsys.readouterr().err.startswith("add unavailable: [Errno 28]")


# --- rows pinned against mutation survivors -----------------------------------


def test_add_rows_an_invalid_batch_and_a_failed_server_read_on_add(
    tmp_vault, monkeypatch
):
    """Both refusals before any write carry the check, the `add` target and
    the full reason -- the schema violation as UNMATCHED, the /api/ outage
    through `blocked` as UNREACHABLE."""
    fake, client = _fake_for_add(monkeypatch)
    (row,) = capture.add(tmp_vault, client, [])
    assert (row.check, row.target, row.result, row.reason) == (
        "capture",
        "add",
        Result.UNMATCHED,
        "schema-violation — items must be a non-empty list of at most 50 objects",
    )
    fake.get("/api/", status=500, body=b"")
    (row,) = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    assert (row.check, row.target, row.result) == (
        "capture",
        "add",
        Result.UNREACHABLE,
    )
    assert row.reason.startswith("outage — local API HTTP 500")
    assert not [c for c in fake.calls if c[0] == "POST"]


def test_add_names_the_add_target_on_a_recorded_server_mismatch(tmp_vault, monkeypatch):
    _fake, client = _fake_for_add(monkeypatch)
    (tmp_vault / "literatures" / "x.md").write_text(
        '---\ntype: "literature"\nzotero-server-id: "Tdoqsn2J4q4h"\nzotero-item-key: "AAAA0000"\n'
        'zotero-item-version: 1\ncitationKey: "x"\nattachments:\nfulltext:\n---\n'
    )
    (row,) = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    assert (row.check, row.target, row.result, row.reason) == (
        "capture",
        "add",
        Result.UNMATCHED,
        "database-changed — notes record Tdoqsn2J4q4h, Zotero answers 6LpvURP2E933",
    )


def test_add_reports_a_partial_or_malformed_create_as_a_mismatch_naming_failed(
    tmp_vault, monkeypatch
):
    """A create envelope with anything under `failed` is a mismatch even when
    `successful` also names a key, and an entry under `successful` that is
    not an object counts as no key created -- never a traceback."""
    fake, client = _fake_for_add(monkeypatch)
    fake.post(
        "/api/users/0/items",
        body={
            "successful": {"0": {"key": "E352DFS8", "version": 544}},
            "unchanged": {},
            "failed": {"1": {"code": 400, "message": "bad"}},
        },
    )
    (row,) = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    assert (row.target, row.result, row.reason) == (
        "add",
        Result.UNMATCHED,
        "mismatch — create failed: {'1': {'code': 400, 'message': 'bad'}}",
    )
    fake.post(
        "/api/users/0/items",
        body={"successful": {"0": "E352DFS8"}, "unchanged": {}, "failed": {}},
    )
    (row,) = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    assert (row.result, row.reason) == (
        Result.UNMATCHED,
        "mismatch — create failed: {}",
    )


def test_add_posts_each_item_whole_names_every_created_key_and_captures_at_now(
    tmp_vault, monkeypatch
):
    from research_vault import frontmatter

    fake, client = _fake_for_add(monkeypatch)
    fake.post(
        "/api/users/0/items",
        body={
            "successful": {
                "0": {"key": "E352DFS8", "version": 544},
                "1": {"key": "F441KKD2", "version": 545},
            },
            "unchanged": {},
            "failed": {},
        },
    )
    items = [
        {"itemType": "journalArticle", "title": "T"},
        {"itemType": "book", "title": "U", "tags": [{"tag": "x"}]},
    ]
    import datetime

    outcomes = capture.add(
        tmp_vault,
        client,
        items,
        collection="IQZW5UVX",
        now=datetime.datetime.fromisoformat("2026-09-07T10:00:00Z"),
    )

    assert outcomes[0].reason == "matched — created E352DFS8, F441KKD2"
    assert json.loads(fake._last_post_body) == [
        {"itemType": "journalArticle", "title": "T", "collections": ["IQZW5UVX"]},
        {
            "itemType": "book",
            "title": "U",
            "tags": [{"tag": "x"}],
            "collections": ["IQZW5UVX"],
        },
    ]
    data, _body = frontmatter.parse(
        (tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text()
    )
    assert data["accessed"] == "2026-09-07"
    assert data["generated"]["at"] == "2026-09-07T10:00:00Z"
