import json
import re
import socket
from pathlib import Path

import pytest

from research_vault import Result, zotero
from tests.fakes import FULLTEXT, ITEM, FakeZotero, canned_item


@pytest.fixture
def fake(monkeypatch):
    client = zotero.ZoteroClient()
    double = FakeZotero()
    double.install(client, monkeypatch)
    double.client = client
    return double


def test_base_for_prefers_flag_then_machine_config_then_default(tmp_vault):
    assert zotero.base_for(tmp_vault) == zotero.DEFAULT_BASE
    (tmp_vault / ".research-vault").mkdir()
    (tmp_vault / ".research-vault" / "machine.json").write_text(
        '{"zotero_base": "http://localhost:23129/"}'
    )
    assert zotero.base_for(tmp_vault) == "http://localhost:23129"
    assert zotero.base_for(tmp_vault, "http://other:1/") == "http://other:1"


def test_base_for_falls_back_when_machine_config_is_unreadable(tmp_vault):
    """`doctor` owns the machine-config finding; resolving --base must not
    crash the CLI before that probe can report it."""
    (tmp_vault / ".research-vault").mkdir()
    machine = tmp_vault / ".research-vault" / "machine.json"
    machine.write_text("{not json")
    assert zotero.base_for(tmp_vault) == zotero.DEFAULT_BASE
    machine.write_text("[]")
    assert zotero.base_for(tmp_vault) == zotero.DEFAULT_BASE


def test_server_info_reads_the_four_headers(fake):
    assert fake.client.server_info() == {
        "zotero": "10.0.1",
        "api": "3",
        "schema": "44",
        "server_id": "6LpvURP2E933",
    }


def test_recorded_server_id_rides_every_request_and_412_is_typed(fake, monkeypatch):
    canned_item(fake)
    fake.client.server_id = "6LpvURP2E933"
    assert fake.client.item("E352DFS8")["data"]["citationKey"] == "jakesch.etal2023a"
    assert fake.calls[-1][2]["Zotero-Server-ID"] == "6LpvURP2E933"

    fake.client.server_id = "Tdoqsn2J4q4h"
    with pytest.raises(zotero.DatabaseChangedError) as error:
        fake.client.item("E352DFS8")
    assert error.value.result is Result.UNMATCHED


def test_item_children_fulltext_and_file_url(fake):
    canned_item(fake)
    children = fake.client.children("E352DFS8")
    assert [child["data"]["itemType"] for child in children] == ["attachment", "note"]
    assert fake.client.annotations("E352DFS8") == []
    assert fake.client.fulltext("D7EJ9FTG") == FULLTEXT
    assert fake.client.fulltext("MISSING1") is None
    assert fake.client.file_view_url("D7EJ9FTG").startswith(
        "file:///D:/Zotero/storage/"
    )


def test_file_view_url_returns_none_only_for_the_two_definite_negatives(fake):
    """404 (no such item) and 400 (not a file attachment; records 182/187/192)
    are "no file". Everything else is what it is: a 500 or a refused
    connection is an outage, 403 is the API off, an empty 200 is malformed."""
    fake.get(
        "/api/users/0/items/NOTFILE1/file/view/url",
        status=400,
        body=b"Not a file attachment: NOTFILE1",
    )
    assert fake.client.file_view_url("NOTFILE1") is None
    assert fake.client.file_view_url("MISSING1") is None

    fake.get("/api/users/0/items/BROKEN00/file/view/url", status=500, body=b"")
    with pytest.raises(zotero.ZoteroError) as error:
        fake.client.file_view_url("BROKEN00")
    assert error.value.result is Result.UNREACHABLE

    fake.get("/api/users/0/items/OFF00000/file/view/url", status=403, body=b"")
    with pytest.raises(zotero.LocalApiDisabledError):
        fake.client.file_view_url("OFF00000")

    fake.get("/api/users/0/items/EMPTY000/file/view/url", body=b"  \n")
    with pytest.raises(zotero.ZoteroError, match="malformed") as error:
        fake.client.file_view_url("EMPTY000")
    assert error.value.result is Result.UNREACHABLE


def test_file_view_url_on_a_dead_port_is_an_outage():
    client = zotero.ZoteroClient(base=_dead_port_base())
    with pytest.raises(zotero.ZoteroError) as error:
        client.file_view_url("D7EJ9FTG")
    assert error.value.result is Result.UNREACHABLE


def test_versions_trash_and_top_carry_the_version_header(fake):
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={"E352DFS8": 544, "D7EJ9FTG": 551},
        headers={"Last-Modified-Version": "565"},
    )
    fake.get("/api/users/0/items/trash?format=versions", body={"T6GF6HH7": 15})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[ITEM],
        headers={"Last-Modified-Version": "565"},
    )
    assert fake.client.versions() == ({"E352DFS8": 544, "D7EJ9FTG": 551}, 565)
    assert fake.client.trash_versions() == {"T6GF6HH7": 15}
    items, version = fake.client.top_items()
    assert items[0]["key"] == "E352DFS8"
    assert version == 565


def test_library_csl_reads_the_whole_library_route(fake):
    fake.get(
        "/better-bibtex/library?/My%20Library.json",
        body=[
            {
                "id": "jakesch.etal2023a",
                "citation-key": "jakesch.etal2023a",
                "type": "paper-conference",
            }
        ],
    )
    items = fake.client.library_csl("My Library")
    assert items[0]["id"] == "jakesch.etal2023a"


def test_local_api_403_and_404_are_typed_and_other_statuses_are_outages(fake):
    fake.get("/api/users/0/items/OFF00000?format=json", status=403, body=b"")
    with pytest.raises(zotero.LocalApiDisabledError):
        fake.client.item("OFF00000")
    with pytest.raises(zotero.NotFoundError):
        fake.client.item("NOPE0000")
    fake.get("/api/users/0/items/BROKEN00?format=json", status=500, body=b"")
    with pytest.raises(zotero.ZoteroError) as error:
        fake.client.item("BROKEN00")
    assert error.value.result is Result.UNREACHABLE


def test_authorize_requires_a_server_id_and_returns_the_key(fake):
    fake.post("/api/local/authorize", body={"key": "k" * 32, "remember": True})
    with pytest.raises(zotero.ZoteroError):
        fake.client.authorize()  # no server id -> authorize() raises before any request
    fake.client.server_id = "6LpvURP2E933"
    assert fake.client.authorize() == {"key": "k" * 32, "remember": True}
    verb, path, _headers = fake.calls[-1]
    assert (verb, path) == ("POST", "/api/local/authorize")


@pytest.mark.parametrize("body", [b"", b"Forbidden", b"{}", b"[]"])
def test_authorize_types_the_api_off_403(fake, body):
    """A 403 without ``{"denied": true}`` is the preference-off answer every
    request gets (record 32), not a person clicking Deny (record 19)."""
    fake.client.server_id = "6LpvURP2E933"
    fake.post("/api/local/authorize", status=403, body=body)

    with pytest.raises(zotero.LocalApiDisabledError) as error:
        fake.client.authorize()

    assert error.value.result is Result.UNMATCHED


def test_authorize_denial_stays_a_denial(fake):
    fake.client.server_id = "6LpvURP2E933"
    fake.post("/api/local/authorize", status=403, body={"denied": True})

    with pytest.raises(zotero.ZoteroError, match="authorization denied") as error:
        fake.client.authorize()

    assert error.value.result is Result.UNMATCHED
    assert not isinstance(error.value, zotero.LocalApiDisabledError)


def test_create_items_sends_key_and_id_and_returns_the_envelope(fake):
    fake.client.server_id = "6LpvURP2E933"
    fake.client.api_key = "k" * 32
    fake.post(
        "/api/users/0/items",
        body={
            "successful": {"0": {"key": "II7E6CVR", "version": 1710}},
            "unchanged": {},
            "failed": {},
        },
    )
    envelope = fake.client.create_items([{"itemType": "journalArticle", "title": "T"}])
    assert envelope["successful"]["0"]["key"] == "II7E6CVR"
    assert fake.calls[-1][2]["Zotero-API-Key"] == "k" * 32


def test_create_items_refuses_before_sending_without_a_key_or_a_server_id(fake):
    """The id is mandatory on every write (428 without it) and the key on
    every write but authorize (401): both are UNMATCHED preconditions, never
    an outage, and neither request leaves the client."""
    fake.client.api_key = "k" * 32
    with pytest.raises(zotero.ZoteroError) as error:
        fake.client.create_items([{"itemType": "journalArticle"}])
    assert error.value.result is Result.UNMATCHED
    fake.client.server_id = "6LpvURP2E933"
    fake.client.api_key = None
    with pytest.raises(zotero.ZoteroError) as error:
        fake.client.create_items([{"itemType": "journalArticle"}])
    assert error.value.result is Result.UNMATCHED
    assert fake.calls == []


def test_rpc_fallbacks_survive(fake):
    fake.rpc("api.ready", {"zotero": "10.0.1", "betterbibtex": "9.0.63"})
    fake.rpc("item.export", [{"id": "jakesch.etal2023a", "type": "paper-conference"}])
    fake.rpc("item.attachments", [])
    assert fake.client.ready()["betterbibtex"] == "9.0.63"
    assert fake.client.export_csl(["jakesch.etal2023a"])[0]["id"] == "jakesch.etal2023a"
    assert fake.client.attachments("jakesch.etal2023a") == []


def test_item_key_grammar():
    assert zotero.ITEM_KEY.match("E352DFS8")
    assert not zotero.ITEM_KEY.match("jakesch.etal2023a")


# -- JSON-RPC method results, ported from the retired FakeTransport suite -----


def test_ready_malformed_result_is_unreachable(fake):
    fake.rpc("api.ready", [])

    with pytest.raises(zotero.ZoteroError) as error:
        fake.client.ready()

    assert error.value.result is Result.UNREACHABLE


def test_attachments_raw_windows_path(fake):
    fake.rpc(
        "item.attachments",
        [
            {
                "path": "D:\\Zotero\\storage\\AB12CD34\\smith2020.pdf",
                "open": "zotero://open-pdf/library/items/AB12CD34",
                "annotations": [],
            }
        ],
    )

    attachments = fake.client.attachments("smith2020")

    assert attachments[0]["path"].startswith("D:\\")
    assert fake.calls[-1] == ("RPC", "item.attachments", {"params": ["smith2020"]})


@pytest.mark.parametrize("result", [None, 17, [None]])
def test_attachments_rejects_malformed_shapes(fake, result):
    fake.rpc("item.attachments", result)

    with pytest.raises(zotero.ZoteroError) as error:
        fake.client.attachments("smith2020")

    assert error.value.result is Result.UNREACHABLE


def test_export_csl_names_the_translator_and_decodes_the_string_result(fake):
    """``item.export`` returns the export as a string (research record 313)."""
    fake.rpc(
        "item.export", json.dumps([{"id": "smith2020", "type": "article-journal"}])
    )

    items = fake.client.export_csl(["smith2020"])

    assert items == [{"id": "smith2020", "type": "article-journal"}]
    assert fake.calls[-1] == (
        "RPC",
        "item.export",
        {"params": [["smith2020"], "Better CSL JSON"]},
    )


@pytest.mark.parametrize("exported", [17, "{", [None], [{"id": ""}], [{"type": "x"}]])
def test_export_csl_rejects_malformed_results(fake, exported):
    fake.rpc("item.export", exported)

    with pytest.raises(zotero.ZoteroError) as error:
        fake.client.export_csl(["smith2020"])

    assert error.value.result is Result.UNREACHABLE


def test_no_research_vault_module_can_issue_an_autoexport_rpc():
    """Restoring any autoexport.* JSON-RPC call or client registration must fail."""
    package = Path(zotero.__file__).parent
    callers = sorted(
        module.name
        for module in package.glob("*.py")
        if re.search(r"autoexport\.[A-Za-z]", module.read_text(encoding="utf-8"))
    )

    assert callers == []
    assert [name for name in dir(zotero.ZoteroClient) if "register" in name] == []


# -- the JSON-RPC envelope itself: these reach _rpc, so they patch the transport --


def _dead_port_base():
    # An ephemeral port fails at once; port 1 hangs for the whole connect
    # timeout under WSL2 (docs/testing.md, "The WSL2 low-port trap").
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return f"http://127.0.0.1:{sock.getsockname()[1]}"


def _transport_answering(body, status=200):
    return lambda *args, **kwargs: zotero.Response(status, body, {})


def test_network_failure_is_unreachable():
    zotero_client = zotero.ZoteroClient(base=_dead_port_base())
    with pytest.raises(zotero.ZoteroError) as error:
        zotero_client.ready()
    assert error.value.result is Result.UNREACHABLE


def test_rpc_malformed_json_is_unreachable(monkeypatch):
    zotero_client = zotero.ZoteroClient()
    monkeypatch.setattr(zotero_client, "_http", _transport_answering(b"{"))

    with pytest.raises(zotero.ZoteroError) as error:
        zotero_client._rpc("api.ready", [])

    assert error.value.result is Result.UNREACHABLE


def test_rpc_non_200_is_unreachable(monkeypatch):
    zotero_client = zotero.ZoteroClient()
    monkeypatch.setattr(zotero_client, "_http", _transport_answering(b"", status=500))

    with pytest.raises(zotero.ZoteroError) as error:
        zotero_client._rpc("api.ready", [])

    assert error.value.result is Result.UNREACHABLE


@pytest.mark.parametrize("body", [b"[]", b'{"jsonrpc": "2.0", "id": 1}'])
def test_rpc_malformed_response_shape_is_unreachable(monkeypatch, body):
    zotero_client = zotero.ZoteroClient()
    monkeypatch.setattr(zotero_client, "_http", _transport_answering(body))

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
        zotero_client, "_http", _transport_answering(json.dumps(reply).encode())
    )

    with pytest.raises(zotero.ZoteroError) as error:
        zotero_client._rpc("api.ready", [])

    assert error.value.result is Result.UNREACHABLE


def test_rpc_valid_success_envelope_returns_result(monkeypatch):
    zotero_client = zotero.ZoteroClient()
    result = {"zotero": "10.0.1", "betterbibtex": "9.0.63"}
    reply = {"jsonrpc": "2.0", "id": 1, "result": result}
    monkeypatch.setattr(
        zotero_client, "_http", _transport_answering(json.dumps(reply).encode())
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
        zotero_client, "_http", _transport_answering(json.dumps(reply).encode())
    )

    with pytest.raises(zotero.ZoteroError) as error:
        zotero_client._rpc("item.attachments", ["smith2020"])

    assert error.value.result is Result.UNMATCHED


def test_rpc_bbt_null_id_error_envelope_surfaces_error_as_unmatched(monkeypatch):
    zotero_client = zotero.ZoteroClient()
    reply = {
        "jsonrpc": "2.0",
        "id": None,
        "error": {"code": -32602, "message": "sentinel"},
    }
    monkeypatch.setattr(
        zotero_client, "_http", _transport_answering(json.dumps(reply).encode())
    )

    with pytest.raises(zotero.ZoteroError, match="sentinel") as error:
        zotero_client._rpc("item.export", [["smith2020"], "Better CSL JSON"])

    assert error.value.result is Result.UNMATCHED


# -- live ---------------------------------------------------------------------


@pytest.mark.live
def test_live_server_info_and_ready():
    client = zotero.ZoteroClient()
    info = client.server_info()
    assert info["zotero"].startswith("10.")
    assert len(info["server_id"]) == 12
    assert "betterbibtex" in client.ready()


@pytest.mark.live
def test_live_versions_carry_the_library_version():
    """``Last-Modified-Version`` is read from a plain dict by exact name; the
    lifecycle linter (Task 12) and capture (Task 13) key on that integer."""
    client = zotero.ZoteroClient()
    versions, library_version = client.versions()
    assert versions
    assert isinstance(library_version, int)
    assert all(zotero.ITEM_KEY.match(key) for key in versions)
