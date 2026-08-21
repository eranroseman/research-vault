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


class UnreadableHtmlResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        raise AssertionError("status-only requests must not read HTML bodies")


def test_mailto_requires_a_machine_or_environment_value(fixture_vault, monkeypatch):
    monkeypatch.delenv("HARNESS_MAILTO", raising=False)

    with pytest.raises(webapi.ApiError):
        webapi.mailto(fixture_vault)


def test_get_json_returns_the_actual_success_status(net_vault, monkeypatch):
    monkeypatch.setattr(
        webapi, "_urlopen", lambda request, timeout: FakeResponse({"ok": True}, 201)
    )

    status, data = webapi.get_json("https://api.example.test/record", net_vault)

    assert status == 201
    assert data == {"ok": True}


def test_get_json_merges_query_and_fragment_with_one_canonical_mailto(
    net_vault, monkeypatch
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
        net_vault,
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


def test_malformed_json_is_unreachable(net_vault, monkeypatch):
    monkeypatch.setattr(
        webapi,
        "_urlopen",
        lambda request, timeout: FakeResponse(b"<html>rate limited"),
    )

    with pytest.raises(webapi.ApiError) as error:
        webapi.get_json("https://api.example.test/record", net_vault)

    assert error.value.result is Result.UNREACHABLE


def test_get_json_returns_none_for_404(net_vault, monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(
            request.full_url, 404, "not found", {}, io.BytesIO()
        )

    monkeypatch.setattr(webapi, "_urlopen", fake_urlopen)

    status, data = webapi.get_json("https://api.example.test/record", net_vault)

    assert status == 404
    assert data is None


def test_get_status_accepts_an_html_success_response(net_vault, monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["method"] = request.get_method()
        return FakeResponse(b"<html>archive</html>", 200)

    monkeypatch.setattr(
        webapi,
        "_urlopen",
        fake_urlopen,
    )

    status = webapi.get_status("https://archive.example.test/record", net_vault)

    assert status == 200
    assert seen["method"] == "HEAD"


def test_get_status_returns_404(net_vault, monkeypatch):
    methods = []

    def fake_urlopen(request, timeout):
        methods.append(request.get_method())
        if request.get_method() == "GET":
            raise AssertionError("a hard 404 must not fall back to GET")
        raise urllib.error.HTTPError(
            request.full_url, 404, "not found", {}, io.BytesIO()
        )

    monkeypatch.setattr(webapi, "_urlopen", fake_urlopen)

    status = webapi.get_status("https://archive.example.test/record", net_vault)

    assert status == 404
    assert methods == ["HEAD"]


def test_get_status_retries_method_rejected_head_with_an_undecoded_get(
    net_vault, monkeypatch
):
    calls = []

    def fake_urlopen(request, timeout):
        calls.append((request.get_method(), request.full_url, timeout))
        if request.get_method() == "HEAD":
            raise urllib.error.HTTPError(
                request.full_url, 405, "method not allowed", {}, io.BytesIO()
            )
        return UnreadableHtmlResponse()

    monkeypatch.setattr(webapi, "_urlopen", fake_urlopen)

    status = webapi.get_status(
        "https://archive.example.test/record?existing=value#archive",
        net_vault,
    )

    assert status == 200
    assert [method for method, _, _ in calls] == ["HEAD", "GET"]
    assert calls[0][1] == calls[1][1]
    assert "mailto=eran%40example.edu" in calls[0][1]
    assert calls[0][2] == 10.0
    assert calls[1][2] == 10.0


def test_get_status_raises_api_error_when_the_get_fallback_fails(
    net_vault, monkeypatch
):
    methods = []

    def fake_urlopen(request, timeout):
        methods.append(request.get_method())
        if request.get_method() == "HEAD":
            raise urllib.error.HTTPError(
                request.full_url, 405, "method not allowed", {}, io.BytesIO()
            )
        raise urllib.error.HTTPError(
            request.full_url, 500, "server error", {}, io.BytesIO()
        )

    monkeypatch.setattr(webapi, "_urlopen", fake_urlopen)

    with pytest.raises(webapi.ApiError) as error:
        webapi.get_status("https://archive.example.test/record", net_vault)

    assert error.value.result is Result.UNREACHABLE
    assert methods == ["HEAD", "GET"]


def test_get_status_raises_api_error_when_the_get_fallback_is_unreachable(
    net_vault, monkeypatch
):
    methods = []

    def fake_urlopen(request, timeout):
        methods.append(request.get_method())
        if request.get_method() == "HEAD":
            raise urllib.error.HTTPError(
                request.full_url, 405, "method not allowed", {}, io.BytesIO()
            )
        raise OSError("offline")

    monkeypatch.setattr(webapi, "_urlopen", fake_urlopen)

    with pytest.raises(webapi.ApiError) as error:
        webapi.get_status("https://archive.example.test/record", net_vault)

    assert error.value.result is Result.UNREACHABLE
    assert methods == ["HEAD", "GET"]


def test_network_outage_is_unreachable(net_vault, monkeypatch):
    monkeypatch.setattr(
        webapi,
        "_urlopen",
        lambda request, timeout: (_ for _ in ()).throw(OSError("offline")),
    )

    with pytest.raises(webapi.ApiError) as error:
        webapi.get_json("https://api.example.test/record", net_vault)

    assert error.value.result is Result.UNREACHABLE


def test_malformed_machine_config_is_an_api_error(fixture_vault, monkeypatch):
    monkeypatch.delenv("HARNESS_MAILTO", raising=False)
    config_dir = fixture_vault / ".harness"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "machine.json").write_text("[]")

    with pytest.raises(webapi.ApiError) as error:
        webapi.mailto(fixture_vault)

    assert error.value.result is Result.UNREACHABLE


def test_get_text_returns_strict_utf8_primary_contract(net_vault, monkeypatch):
    monkeypatch.setattr(
        webapi,
        "_urlopen",
        lambda request, timeout: FakeResponse(b"<feed>ok</feed>"),
    )

    assert webapi.get_text("https://export.arxiv.org/api/query", net_vault) == (
        200,
        "<feed>ok</feed>",
    )


def test_get_text_rejects_undecodable_primary_contract(net_vault, monkeypatch):
    monkeypatch.setattr(
        webapi,
        "_urlopen",
        lambda request, timeout: FakeResponse(b"\xff"),
    )

    with pytest.raises(webapi.ApiError, match="undecodable"):
        webapi.get_text("https://export.arxiv.org/api/query", net_vault)
