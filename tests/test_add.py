import json

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


def test_a_400_from_the_local_api_is_a_mismatch_not_an_outage(tmp_vault, monkeypatch):
    fake = FakeZotero()
    fake.rpc("api.ready", {"zotero": "10.0.1", "betterbibtex": "9.0.63"})
    fake.post("/api/local/authorize", body={"key": "k" * 32, "remember": True})
    fake.post("/api/users/0/items", status=400, body=b"Invalid item type 'bogus'")
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    (outcome,) = capture.add(tmp_vault, client, [{"itemType": "bogus", "title": "x"}])
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith("mismatch — local API 400 for /api/users/0/items")


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
    assert outcome.reason.startswith("mismatch — local API 400 for /api/users/0/items")
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
    assert outcomes[0].reason.startswith("mismatch — API key rejected")


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
