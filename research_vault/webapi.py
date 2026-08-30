"""Polite HTTP boundary for external verification APIs (spec §6)."""

import json
import os
import urllib.error
import urllib.parse
import urllib.request

from . import Result, __version__
from .paths import load_machine_config

_HEAD_FALLBACK_STATUSES = {403, 405, 501}


class ApiError(Exception):
    """An external service or its required client configuration is unavailable."""

    result = Result.UNREACHABLE


def _urlopen(request, timeout):
    return urllib.request.urlopen(request, timeout=timeout)


def mailto(vault_root) -> str:
    """Return the required contact address for polite third-party requests."""
    try:
        config = load_machine_config(vault_root)
    except (OSError, TypeError, ValueError) as error:
        raise ApiError(
            "invalid .research-vault/machine.json mailto configuration"
        ) from error

    if not isinstance(config, dict):
        raise ApiError("invalid .research-vault/machine.json mailto configuration")

    configured = config.get("mailto")
    if configured is not None and not isinstance(configured, str):
        raise ApiError("invalid .research-vault/machine.json mailto configuration")
    address = configured or os.environ.get("RV_MAILTO")
    if not isinstance(address, str) or not address.strip():
        raise ApiError(
            "no mailto configured (.research-vault/machine.json or RV_MAILTO) "
            "— polite pools are mandatory"
        )
    return address


def _request(url, vault_root, params, headers, method, query_mailto=True):
    address = mailto(vault_root)
    parts = urllib.parse.urlsplit(url)
    caller_params = params or {}
    query = [
        (key, value)
        for key, value in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
        if key != "mailto"
    ]
    query.extend(
        (key, value) for key, value in caller_params.items() if key != "mailto"
    )
    if query_mailto:
        query.append(("mailto", address))
    full_url = urllib.parse.urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urllib.parse.urlencode(query, doseq=True),
            parts.fragment,
        )
    )
    request_headers = {
        key: value
        for key, value in (headers or {}).items()
        if key.lower() != "user-agent"
    }
    ua = f"research_vault/{__version__} (mailto:{address})"
    request_headers["User-Agent"] = ua
    return urllib.request.Request(full_url, headers=request_headers, method=method)


def _check_status(status, url, method):
    if status == 404:
        return
    if method == "HEAD" and status in _HEAD_FALLBACK_STATUSES:
        return
    if status >= 400:
        raise ApiError(f"HTTP {status} from {url}")


def _open(url, vault_root, params, headers, timeout, method, read_body, query_mailto):
    request = _request(url, vault_root, params, headers, method, query_mailto)
    try:
        with _urlopen(request, timeout) as response:
            _check_status(response.status, url, method)
            body = response.read() if read_body else None
            return response.status, body
    except urllib.error.HTTPError as error:
        try:
            _check_status(error.code, url, method)
        except ApiError as api_error:
            raise api_error from error
        return error.code, None
    except OSError as error:
        raise ApiError(f"network failure: {error}") from error


def get_json(url, vault_root, params=None, headers=None, timeout=10.0):
    """GET JSON, returning its actual status and decoded body."""
    status, body = _open(url, vault_root, params, headers, timeout, "GET", True, True)
    if status == 404:
        return status, None
    try:
        return status, json.loads(body)
    except (TypeError, ValueError) as error:
        raise ApiError(f"undecodable body from {url}") from error


def get_text(url, vault_root, params=None, headers=None, timeout=10.0):
    """GET strict UTF-8 text, returning its actual status and decoded body."""
    status, body = _open(url, vault_root, params, headers, timeout, "GET", True, True)
    if status == 404:
        return status, None
    try:
        return status, body.decode("utf-8")
    except (AttributeError, UnicodeError) as error:
        raise ApiError(f"undecodable body from {url}") from error


def get_status(
    url, vault_root, params=None, headers=None, timeout=10.0, *, query_mailto=True
):
    """HEAD a resource, falling back to GET if the server rejects HEAD; pass
    ``query_mailto=False`` when the target URL rides in this URL's path, where
    an appended ``?mailto=`` would become part of that target instead."""
    status, _ = _open(
        url, vault_root, params, headers, timeout, "HEAD", False, query_mailto
    )
    if status in _HEAD_FALLBACK_STATUSES:
        status, _ = _open(
            url, vault_root, params, headers, timeout, "GET", False, query_mailto
        )
    return status
