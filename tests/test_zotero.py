import json
import re
from pathlib import Path

import pytest

from knowledge_harness import Result, zotero


class FakeTransport:
    """Patches ZoteroClient._rpc with canned JSON-RPC payloads."""

    def __init__(self):
        self.rpc_calls = []
        self.canned_rpc = {
            "api.ready": {"zotero": "9.0.6", "betterbibtex": "9.0.55"},
            "item.search": [
                {
                    "id": "smith2020",
                    "citekey": "smith2020",
                    "title": "Mortality decline",
                    "type": "article-journal",
                }
            ],
            "item.citationkey": {"2WHVXRX3": "smith2020"},
            "item.attachments": [
                {
                    "path": "D:\\Zotero\\storage\\AB12CD34\\smith2020.pdf",
                    "open": "zotero://open-pdf/library/items/AB12CD34",
                    "annotations": [],
                }
            ],
            "item.export": [
                {
                    "id": "smith2020",
                    "type": "article-journal",
                    "title": "Mortality decline",
                }
            ],
        }

    def rpc(self, method, params):
        self.rpc_calls.append((method, params))
        return self.canned_rpc[method]


@pytest.fixture
def client(monkeypatch):
    zotero_client = zotero.ZoteroClient()
    fake = FakeTransport()
    monkeypatch.setattr(zotero_client, "_rpc", fake.rpc)
    zotero_client._fake = fake
    return zotero_client


def test_ready(client):
    info = client.ready()
    assert info["betterbibtex"] == "9.0.55"


def test_ready_malformed_result_is_unreachable(client):
    client._fake.canned_rpc["api.ready"] = []

    with pytest.raises(zotero.ZoteroError) as error:
        client.ready()

    assert error.value.result is Result.UNREACHABLE


def test_search_carries_citekey(client):
    items = client.search("mortality")
    assert items[0]["citekey"] == "smith2020"
    assert client._fake.rpc_calls[0] == ("item.search", ["mortality"])


def test_method_results_accept_valid_empty_collections(client):
    client._fake.canned_rpc["item.search"] = []
    client._fake.canned_rpc["item.citationkey"] = {}
    client._fake.canned_rpc["item.attachments"] = []

    assert client.search("missing") == []
    assert client.citekey_of([]) == {}
    assert client.attachments("noAttachments2026") == []


def test_citekey_result_filters_live_null_absences(client):
    client._fake.canned_rpc["item.citationkey"] = {"UNMAPPED": None}

    assert client.citekey_of(["UNMAPPED"]) == {}


@pytest.mark.parametrize(
    ("method", "result"),
    [
        ("item.search", None),
        ("item.search", 17),
        ("item.search", [None]),
        ("item.citationkey", None),
        ("item.citationkey", 17),
        ("item.citationkey", []),
        ("item.citationkey", {"ITEMKEY": 17}),
        ("item.citationkey", {17: "smith2020"}),
        ("item.attachments", None),
        ("item.attachments", 17),
        ("item.attachments", [None]),
    ],
)
def test_method_results_reject_malformed_shapes(client, method, result):
    client._fake.canned_rpc[method] = result
    invoke = {
        "item.search": lambda: client.search("smith2020"),
        "item.citationkey": lambda: client.citekey_of(["ITEMKEY"]),
        "item.attachments": lambda: client.attachments("smith2020"),
    }[method]

    with pytest.raises(zotero.ZoteroError) as error:
        invoke()

    assert error.value.result is Result.UNREACHABLE


def test_attachments_raw_windows_path(client):
    attachments = client.attachments("smith2020")
    assert attachments[0]["path"].startswith("D:\\")


def test_export_named_translator(client):
    client.export_csl(["smith2020"])
    assert client._fake.rpc_calls[0] == (
        "item.export",
        [["smith2020"], "Better CSL JSON"],
    )


def test_no_harness_module_can_issue_an_autoexport_rpc():
    """Restoring any autoexport.* JSON-RPC call or client registration must fail."""
    package = Path(zotero.__file__).parent
    callers = sorted(
        module.name
        for module in package.glob("*.py")
        if re.search(r"autoexport\.[A-Za-z]", module.read_text(encoding="utf-8"))
    )

    assert callers == []
    assert [name for name in dir(zotero.ZoteroClient) if "register" in name] == []


def test_whole_library_export_normalizes_uri_ids_and_excludes_orphans(
    client, monkeypatch
):
    page = [
        {"id": "smith2020", "type": "article-journal", "title": "Ordinary item"},
        {
            "id": "http://zotero.org/users/0/items/ATTACH01",
            "type": "document",
            "title": "Top-level attachment",
        },
        {
            "id": "http://zotero.org/users/0/items/ORPHAN01",
            "type": "document",
            "title": "Top-level orphan",
        },
    ]
    client._fake.canned_rpc["item.citationkey"] = {"ATTACH01": "mapped2024"}
    monkeypatch.setattr(
        client, "_http", lambda *args, **kwargs: (200, json.dumps(page).encode())
    )

    items = client.export_csl(None)

    assert [item["id"] for item in items] == ["smith2020", "mapped2024"]
    assert items[1]["title"] == "Top-level attachment"
    assert client._fake.rpc_calls == [
        ("item.citationkey", [["ATTACH01", "ORPHAN01"]]),
    ]


def test_whole_library_export_fetches_all_pages_before_normalizing(client, monkeypatch):
    first_page = [
        {"id": f"first{i}", "type": "article-journal", "title": "First page item"}
        for i in range(100)
    ]
    second_page = [
        {"id": "second2024", "type": "article-journal", "title": "Second page item"},
        {
            "id": "http://zotero.org/users/0/items/SECOND01",
            "type": "document",
            "title": "Second page attachment",
        },
    ]
    requested_urls = []

    def http(url, *args, **kwargs):
        requested_urls.append(url)
        if url.endswith("start=0"):
            return 200, json.dumps(first_page).encode()
        if url.endswith("start=100"):
            return 200, json.dumps(second_page).encode()
        raise AssertionError(f"unexpected page request: {url}")

    client._fake.canned_rpc["item.citationkey"] = {"SECOND01": "mapped2024"}
    monkeypatch.setattr(client, "_http", http)

    items = client.export_csl(None)

    assert len(items) == 102
    assert [item["id"] for item in items[-2:]] == ["second2024", "mapped2024"]
    assert requested_urls == [
        "http://localhost:23119/api/users/0/items/top?format=csljson&limit=100&start=0",
        "http://localhost:23119/api/users/0/items/top?format=csljson&limit=100&start=100",
    ]
    assert client._fake.rpc_calls == [("item.citationkey", [["SECOND01"]])]


def test_network_failure_is_unreachable():
    zotero_client = zotero.ZoteroClient(base="http://127.0.0.1:1")
    with pytest.raises(zotero.ZoteroError) as error:
        zotero_client.ready()
    assert error.value.result is Result.UNREACHABLE


def test_rpc_malformed_json_is_unreachable(monkeypatch):
    zotero_client = zotero.ZoteroClient()
    monkeypatch.setattr(zotero_client, "_http", lambda *args, **kwargs: (200, b"{"))

    with pytest.raises(zotero.ZoteroError) as error:
        zotero_client._rpc("api.ready", [])

    assert error.value.result is Result.UNREACHABLE


@pytest.mark.parametrize("body", [b"[]", b'{"jsonrpc": "2.0", "id": 1}'])
def test_rpc_malformed_response_shape_is_unreachable(monkeypatch, body):
    zotero_client = zotero.ZoteroClient()
    monkeypatch.setattr(
        zotero_client,
        "_http",
        lambda *args, **kwargs: (200, body),
    )

    with pytest.raises(zotero.ZoteroError) as error:
        zotero_client._rpc("api.ready", [])

    assert error.value.result is Result.UNREACHABLE


@pytest.mark.parametrize(
    "reply",
    [
        {"id": 1, "result": {}},
        {"jsonrpc": "1.0", "id": 1, "result": {}},
        {"jsonrpc": "2.0", "result": {}},
        {"jsonrpc": "2.0", "id": None, "result": {}},
        {"jsonrpc": "2.0", "id": 2, "result": {}},
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {},
            "error": {"code": -32603, "message": "conflicting"},
        },
    ],
)
def test_rpc_rejects_malformed_envelope_as_unreachable(monkeypatch, reply):
    zotero_client = zotero.ZoteroClient()
    monkeypatch.setattr(
        zotero_client,
        "_http",
        lambda *args, **kwargs: (200, json.dumps(reply).encode()),
    )

    with pytest.raises(zotero.ZoteroError) as error:
        zotero_client._rpc("api.ready", [])

    assert error.value.result is Result.UNREACHABLE


def test_rpc_valid_success_envelope_returns_result(monkeypatch):
    zotero_client = zotero.ZoteroClient()
    result = {"zotero": "9.0.6", "betterbibtex": "9.0.55"}
    reply = {"jsonrpc": "2.0", "id": 1, "result": result}
    monkeypatch.setattr(
        zotero_client,
        "_http",
        lambda *args, **kwargs: (200, json.dumps(reply).encode()),
    )

    assert zotero_client._rpc("api.ready", []) == result


def test_rpc_valid_error_envelope_remains_unmatched(monkeypatch):
    zotero_client = zotero.ZoteroClient()
    reply = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32602, "message": "invalid params"},
    }
    monkeypatch.setattr(
        zotero_client,
        "_http",
        lambda *args, **kwargs: (200, json.dumps(reply).encode()),
    )

    with pytest.raises(zotero.ZoteroError) as error:
        zotero_client._rpc("item.search", ["smith2020"])

    assert error.value.result is Result.UNMATCHED


def test_rpc_bbt_null_id_error_envelope_surfaces_error_as_unmatched(monkeypatch):
    zotero_client = zotero.ZoteroClient()
    reply = {
        "jsonrpc": "2.0",
        "id": None,
        "error": {"code": -32602, "message": "sentinel"},
    }
    monkeypatch.setattr(
        zotero_client,
        "_http",
        lambda *args, **kwargs: (200, json.dumps(reply).encode()),
    )

    with pytest.raises(zotero.ZoteroError, match="sentinel") as error:
        zotero_client._rpc("item.export", [["smith2020"], "Better CSL JSON"])

    assert error.value.result is Result.UNMATCHED


def test_whole_library_export_malformed_json_is_unreachable(client, monkeypatch):
    monkeypatch.setattr(client, "_http", lambda *args, **kwargs: (200, b"{"))

    with pytest.raises(zotero.ZoteroError) as error:
        client.export_csl(None)

    assert error.value.result is Result.UNREACHABLE


@pytest.mark.live
def test_live_ready_and_export():
    zotero_client = zotero.ZoteroClient()
    info = zotero_client.ready()
    assert "betterbibtex" in info
    items = zotero_client.export_csl(None)
    assert isinstance(items, list)
    assert len(items) > 0
    assert all("/" not in item["id"] for item in items)

    one = zotero_client.export_csl([items[0]["id"]])
    assert one
    assert one[0]["id"] == items[0]["id"]
    assert isinstance(zotero_client.search(items[0]["id"]), list)
