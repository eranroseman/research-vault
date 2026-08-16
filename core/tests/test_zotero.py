import pytest
import json

from harness_core import Result, zotero


class FakeTransport:
    """Patches ZoteroClient._rpc with canned JSON-RPC payloads."""

    def __init__(self):
        self.rpc_calls = []
        self.canned_rpc = {
            "api.ready": {"zotero": "9.0.6", "betterbibtex": "9.0.55"},
            "item.search": [{
                "id": "smith2020",
                "citekey": "smith2020",
                "title": "Mortality decline",
                "type": "article-journal",
            }],
            "item.citationkey": {"2WHVXRX3": "smith2020"},
            "item.attachments": [{
                "path": "D:\\Zotero\\storage\\AB12CD34\\smith2020.pdf",
                "open": "zotero://open-pdf/library/items/AB12CD34",
                "annotations": [],
            }],
            "item.export": [{
                "id": "smith2020",
                "type": "article-journal",
                "title": "Mortality decline",
            }],
            "autoexport.add": {"path": "/vault/x/bibliography.json"},
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


def test_search_carries_citekey(client):
    items = client.search("mortality")
    assert items[0]["citekey"] == "smith2020"
    assert client._fake.rpc_calls[0] == ("item.search", ["mortality"])


def test_attachments_raw_windows_path(client):
    attachments = client.attachments("smith2020")
    assert attachments[0]["path"].startswith("D:\\")


def test_export_named_translator(client):
    client.export_csl(["smith2020"])
    assert client._fake.rpc_calls[0] == (
        "item.export",
        [["smith2020"], "Better CSL JSON"],
    )


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
    monkeypatch.setattr(client, "_http", lambda *args, **kwargs: (200, json.dumps(page).encode()))

    items = client.export_csl(None)

    assert [item["id"] for item in items] == ["smith2020", "mapped2024"]
    assert items[1]["title"] == "Top-level attachment"
    assert client._fake.rpc_calls == [
        ("item.citationkey", [["ATTACH01", "ORPHAN01"]]),
    ]


def test_network_failure_is_unreachable():
    zotero_client = zotero.ZoteroClient(base="http://127.0.0.1:1")
    with pytest.raises(zotero.ZoteroError) as error:
        zotero_client.ready()
    assert error.value.result is Result.UNREACHABLE


@pytest.mark.live
def test_live_ready_and_export():
    zotero_client = zotero.ZoteroClient()
    info = zotero_client.ready()
    assert "betterbibtex" in info
    items = zotero_client.export_csl(None)
    assert isinstance(items, list) and len(items) > 0
    assert all("/" not in item["id"] for item in items)

    one = zotero_client.export_csl([items[0]["id"]])
    assert one and one[0]["id"] == items[0]["id"]
    assert isinstance(zotero_client.search(items[0]["id"]), list)

    major = int(str(info["zotero"]).split(".")[0])
    assert zotero_client.supports_local_writes() is (major >= 10)
