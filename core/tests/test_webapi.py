import io
import json
import urllib.error
import urllib.parse

import pytest

from harness_core import Result, webapi


class FakeResponse(io.BytesIO):
    def __init__(self, payload, status=200):
        encoded = (
            payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        )
        super().__init__(encoded)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


@pytest.fixture
def vault_with_mailto(fixture_vault):
    config_dir = fixture_vault / ".harness"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "machine.json").write_text('{"mailto": "eran@example.edu"}')
    return fixture_vault


def test_mailto_requires_a_machine_or_environment_value(fixture_vault, monkeypatch):
    monkeypatch.delenv("HARNESS_MAILTO", raising=False)

    with pytest.raises(webapi.ApiError):
        webapi.mailto(fixture_vault)


def test_get_json_returns_the_actual_success_status(vault_with_mailto, monkeypatch):
    monkeypatch.setattr(
        webapi, "_urlopen", lambda request, timeout: FakeResponse({"ok": True}, 201)
    )

    status, data = webapi.get_json("https://api.example.test/record", vault_with_mailto)

    assert status == 201
    assert data == {"ok": True}


def test_get_json_merges_query_and_fragment_with_one_canonical_mailto(
    vault_with_mailto, monkeypatch
):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        seen["ua"] = request.get_header("User-agent")
        seen["accept"] = request.get_header("Accept")
        return FakeResponse({"ok": True})

    monkeypatch.setattr(webapi, "_urlopen", fake_urlopen)

    webapi.get_json(
        "https://api.example.test/record?existing=value&rows=prior&mailto=wrong@example.test#part",
        vault_with_mailto,
        params={"rows": "20", "mailto": "caller@example.test"},
        headers={"Accept": "application/json", "User-Agent": "not-canonical"},
    )

    parts = urllib.parse.urlsplit(seen["url"])
    query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    assert parts.fragment == "part"
    assert ("existing", "value") in query
    assert ("rows", "prior") in query
    assert ("rows", "20") in query
    assert query.count(("mailto", "eran@example.edu")) == 1
    assert not any(
        key == "mailto" and value != "eran@example.edu" for key, value in query
    )
    assert seen["timeout"] == 10.0
    assert seen["ua"] == "harness_core/0.1.0 (mailto:eran@example.edu)"
    assert seen["accept"] == "application/json"


def test_malformed_json_is_unreachable(vault_with_mailto, monkeypatch):
    monkeypatch.setattr(
        webapi,
        "_urlopen",
        lambda request, timeout: FakeResponse(b"<html>rate limited"),
    )

    with pytest.raises(webapi.ApiError) as error:
        webapi.get_json("https://api.example.test/record", vault_with_mailto)

    assert error.value.result is Result.UNREACHABLE


def test_get_json_returns_none_for_404(vault_with_mailto, monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(
            request.full_url, 404, "not found", {}, io.BytesIO()
        )

    monkeypatch.setattr(webapi, "_urlopen", fake_urlopen)

    status, data = webapi.get_json("https://api.example.test/record", vault_with_mailto)

    assert status == 404
    assert data is None


def test_get_status_accepts_an_html_success_response(vault_with_mailto, monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["method"] = request.get_method()
        return FakeResponse(b"<html>archive</html>", 200)

    monkeypatch.setattr(
        webapi,
        "_urlopen",
        fake_urlopen,
    )

    status = webapi.get_status("https://archive.example.test/record", vault_with_mailto)

    assert status == 200
    assert seen["method"] == "HEAD"


def test_get_status_returns_404(vault_with_mailto, monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(
            request.full_url, 404, "not found", {}, io.BytesIO()
        )

    monkeypatch.setattr(webapi, "_urlopen", fake_urlopen)

    status = webapi.get_status("https://archive.example.test/record", vault_with_mailto)

    assert status == 404


def test_network_outage_is_unreachable(vault_with_mailto, monkeypatch):
    monkeypatch.setattr(
        webapi,
        "_urlopen",
        lambda request, timeout: (_ for _ in ()).throw(OSError("offline")),
    )

    with pytest.raises(webapi.ApiError) as error:
        webapi.get_json("https://api.example.test/record", vault_with_mailto)

    assert error.value.result is Result.UNREACHABLE


def test_malformed_machine_config_is_an_api_error(fixture_vault, monkeypatch):
    monkeypatch.delenv("HARNESS_MAILTO", raising=False)
    config_dir = fixture_vault / ".harness"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "machine.json").write_text("[]")

    with pytest.raises(webapi.ApiError) as error:
        webapi.mailto(fixture_vault)

    assert error.value.result is Result.UNREACHABLE
