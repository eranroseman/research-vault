"""Clients for the Zotero local API and Better BibTeX JSON-RPC (ingest spec §3.7).

Reads go to the local API. The server id a note recorded rides every request
as ``Zotero-Server-ID``; Zotero answers 412 when a different database is
listening, and that is the only database-changed test this package makes.
Writes take the documented local write path (§2): ``authorize`` once, then an
API key on each write. Better BibTeX JSON-RPC is kept for ``api.ready``, the
annotation fallback ``item.attachments`` and the CSL fallback ``item.export``.
"""

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from pathlib import Path
from typing import NamedTuple

from . import Result, paths

DEFAULT_BASE = "http://localhost:23119"
CSL_TRANSLATOR = "Better CSL JSON"
APP_NAME = "research-vault"
ITEM_KEY = re.compile(r"^[A-Z0-9]{8}$")


def header(headers, name: str) -> str | None:
    """One response header, matched case-insensitively (row 21): the transport
    hands back a plain dict of whatever names the server sent."""
    wanted = name.lower()
    for key, value in headers.items():
        if key.lower() == wanted:
            return value
    return None


_USER = "/api/users/0"
# Decision 13: the Better BibTeX library route measured 4.78 s cold against
# the client's 5.0 s default, and a busy Zotero's own retry then timed out
# too. About six times the cold measurement, so a library three times larger
# still clears; only the two whole-library export calls use it (never a
# per-item read, and never `ready()` — a busy Zotero must not hang the loop).
EXPORT_TIMEOUT = 30.0
# The consent dialog is answered by a person; a network timeout is the wrong
# clock for it. Measured 2026-09-16: an unanswered dialog under the default 5 s
# reads as an outage in `add` and in the live leg.
AUTHORIZE_TIMEOUT = 180.0


class ZoteroError(Exception):
    """A Zotero operation failure with a research-vault outcome classification."""

    def __init__(self, message, result=Result.UNREACHABLE):
        super().__init__(message)
        self.result: Result = result


class DatabaseChangedError(ZoteroError):
    """412: the instance answering is not the one the tuple recorded (§3.4)."""

    def __init__(self, message="Zotero-Server-ID does not match this server"):
        super().__init__(message, Result.UNMATCHED)


class LocalApiDisabledError(ZoteroError):
    """403: Zotero runs but its local API preference is off (§5)."""

    def __init__(self, message="local API preference is disabled"):
        super().__init__(message, Result.UNMATCHED)


class ApiKeyRejectedError(ZoteroError):
    """401: the API key ``authorize`` granted is no longer valid (§2).

    Its own type, not a string match: ``_local``'s 400 branch echoes up to
    200 bytes of the server's own body, and a 400 and a 401 both carry
    ``result=UNMATCHED``, so only the type tells ``add`` which one to retry.
    """

    def __init__(self, message="API key rejected (401); re-authorize"):
        super().__init__(message, Result.UNMATCHED)


class NotFoundError(ZoteroError):
    """404 from the local API."""

    def __init__(self, message):
        super().__init__(message, Result.UNMATCHED)


class Response(NamedTuple):
    status: int
    body: bytes
    headers: Mapping[str, str]


def base_for(vault_root, override: str | None = None, *, strict: bool = True) -> str:
    """--base, then machine.json's zotero_base, then the default (§6).

    The default is the production instance, so an unreadable or malformed
    ``machine.json`` — a typo in the file that meant to say "use 23129" — is
    refused with ``ZoteroError(result=UNMATCHED)`` rather than silently
    routing every verb at production. Only ``doctor`` resolves with
    ``strict=False``: its ``machine-config`` probe is the one that reports the
    file, so it must still get to run.
    """
    if override:
        return override.rstrip("/")
    if not vault_root:
        return DEFAULT_BASE
    try:
        config: object = paths.load_machine_config(Path(vault_root))
        if not isinstance(config, Mapping):
            raise ValueError("expected an object")
    except (OSError, ValueError, paths.PathError) as error:
        if strict:
            raise ZoteroError(
                f"machine.json unreadable: {error}", Result.UNMATCHED
            ) from error
        return DEFAULT_BASE
    base = config.get("zotero_base")
    if isinstance(base, str) and base.strip():
        return base.strip().rstrip("/")
    if base is not None and strict:
        # JSON null is the spelling of unset and keeps the default; anything
        # else present and not a non-empty string (a number, "", a list) is a
        # typo the production default must not silently absorb.
        raise ZoteroError(
            "machine.json unreadable: zotero_base must be a non-empty string",
            Result.UNMATCHED,
        )
    return DEFAULT_BASE


class ZoteroClient:
    """Access local Zotero through its local web API and BBT JSON-RPC."""

    def __init__(
        self,
        base: str = DEFAULT_BASE,
        timeout: float = 5.0,
        server_id: str | None = None,
        api_key: str | None = None,
    ):
        self.base = base.rstrip("/")
        self.timeout = timeout
        self.server_id = server_id
        self.api_key = api_key

    # -- transport -----------------------------------------------------------

    def _headers(self, extra=None) -> dict[str, str]:
        headers = dict(extra or {})
        if self.server_id:
            headers["Zotero-Server-ID"] = self.server_id
        if self.api_key:
            headers["Zotero-API-Key"] = self.api_key
        return headers

    def _http(
        self, url, data=None, headers=None, method=None, *, timeout=None
    ) -> Response:
        request = urllib.request.Request(
            url, data=data, headers=headers or {}, method=method
        )
        try:
            with urllib.request.urlopen(
                request, timeout=timeout if timeout is not None else self.timeout
            ) as response:
                return Response(
                    response.status, response.read(), dict(response.headers)
                )
        except urllib.error.HTTPError as error:
            return Response(error.code, error.read(), dict(error.headers))
        except OSError as error:
            raise ZoteroError(f"Zotero unreachable at {self.base}: {error}") from error

    def _local(
        self,
        path,
        *,
        data=None,
        method=None,
        expect=(200,),
        timeout: float | None = None,
    ) -> Response:
        response = self._http(
            f"{self.base}{path}",
            data=data,
            headers=self._headers(
                {"Content-Type": "application/json"} if data is not None else None
            ),
            method=method,
            timeout=timeout,
        )
        if response.status in expect:
            return response
        if response.status == 412:
            raise DatabaseChangedError()
        if response.status == 403:
            raise LocalApiDisabledError()
        if response.status == 404:
            raise NotFoundError(f"local API 404 for {path}")
        if response.status == 400:
            # Spec §9 measured a malformed POST /items answering 400: a
            # definite refusal of the payload, not an outage to retry.
            raise ZoteroError(
                f"local API 400 for {path}: {response.body[:200]!r}",
                result=Result.UNMATCHED,
            )
        raise ZoteroError(f"local API HTTP {response.status} for {path}")

    def _local_json(self, path):
        response = self._local(path)
        return self._decode_json(response.body, f"local API {path}"), response.headers

    @staticmethod
    def _decode_json(payload, context):
        try:
            return json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as error:
            raise ZoteroError(f"malformed {context}: {error}") from error

    @staticmethod
    def _validate_object_list(items, context):
        if not isinstance(items, list):
            raise ZoteroError(f"malformed {context}: expected a list")
        for index, item in enumerate(items):
            if not isinstance(item, Mapping):
                raise ZoteroError(
                    f"malformed {context}: invalid object at index {index}"
                )
        return items

    @classmethod
    def _validate_csl_items(cls, items, context):
        cls._validate_object_list(items, context)
        for index, item in enumerate(items):
            if not isinstance(item.get("id"), str) or not item["id"]:
                raise ZoteroError(f"malformed {context}: invalid item at index {index}")
        return items

    @staticmethod
    def _version_header(headers) -> int | None:
        raw = header(headers, "Last-Modified-Version")
        return int(raw) if isinstance(raw, str) and raw.isdigit() else None

    # -- local API reads (§3.3, §3.4) -----------------------------------------

    def server_info(self) -> dict:
        """One GET /api/: four facts from one response's headers (§5)."""
        response = self._local("/api/")
        headers = response.headers
        info = {
            "zotero": header(headers, "X-Zotero-Version") or "",
            "api": header(headers, "Zotero-API-Version") or "",
            "schema": header(headers, "Zotero-Schema-Version") or "",
            "server_id": header(headers, "Zotero-Server-ID") or "",
        }
        if not info["server_id"]:
            raise ZoteroError("malformed /api/ response: no Zotero-Server-ID header")
        return info

    def item(self, key) -> dict:
        payload, _ = self._local_json(f"{_USER}/items/{key}?format=json")
        if not isinstance(payload, Mapping) or not isinstance(
            payload.get("data"), Mapping
        ):
            raise ZoteroError("malformed item JSON: expected an envelope with data")
        return dict(payload)

    def children(self, key) -> list[dict]:
        payload, _ = self._local_json(f"{_USER}/items/{key}/children")
        return self._validate_object_list(payload, "children")

    def annotations(self, key) -> list[dict]:
        """§3.3 step 2's route; measured but unwired this iteration (decision 28)."""
        payload, _ = self._local_json(
            f"{_USER}/items/{key}/children?itemType=annotation"
        )
        return self._validate_object_list(payload, "annotations")

    def fulltext(self, attachment_key) -> dict | None:
        try:
            payload, _ = self._local_json(f"{_USER}/items/{attachment_key}/fulltext")
        except NotFoundError:
            return None
        if not isinstance(payload, Mapping) or not isinstance(
            payload.get("content"), str
        ):
            raise ZoteroError("malformed fulltext response: expected content")
        return dict(payload)

    def file_view_url(self, attachment_key) -> str | None:
        """The attachment's ``file://`` URL as plain text, or ``None``.

        ``None`` means exactly the two definite negatives the server source
        gives (research records 182/187/192): 404, no such item, and 400, not
        a file attachment. Anything else propagates — a 500 or a refused
        connection is an outage, never "no file".
        """
        try:
            response = self._local(
                f"{_USER}/items/{attachment_key}/file/view/url", expect=(200, 400)
            )
        except NotFoundError:
            return None
        if response.status == 400:
            return None
        text = response.body.decode("utf-8", errors="replace").strip()
        if not text:
            raise ZoteroError("malformed file URL response: expected a file:// URL")
        return text

    def versions(self) -> tuple[dict[str, int], int | None]:
        payload, headers = self._local_json(f"{_USER}/items?since=0&format=versions")
        return self._versions_map(payload, "versions"), self._version_header(headers)

    def trash_versions(self) -> dict[str, int]:
        payload, _ = self._local_json(f"{_USER}/items/trash?format=versions")
        return self._versions_map(payload, "trash versions")

    @staticmethod
    def _versions_map(payload, context) -> dict[str, int]:
        if not isinstance(payload, Mapping) or not all(
            isinstance(k, str) and isinstance(v, int) for k, v in payload.items()
        ):
            raise ZoteroError(f"malformed {context}: expected a key-to-version map")
        return dict(payload)

    def top_items(self) -> tuple[list[dict], int | None]:
        payload, headers = self._local_json(f"{_USER}/items/top?format=json")
        return (
            self._validate_object_list(payload, "top items"),
            self._version_header(headers),
        )

    def library_csl(self, library_name) -> list[dict]:
        """The whole library as Better CSL JSON in one read (§3.3 step 4).

        Undocumented route; ``export_csl`` is the documented fallback.
        """
        quoted = urllib.parse.quote(library_name, safe="")
        response = self._http(
            f"{self.base}/better-bibtex/library?/{quoted}.json", timeout=EXPORT_TIMEOUT
        )
        if response.status != 200:
            raise ZoteroError(f"Better BibTeX library route HTTP {response.status}")
        items = self._decode_json(response.body, "Better BibTeX library export")
        return self._validate_csl_items(items, "Better BibTeX library export")

    # -- local API writes (§2) ------------------------------------------------

    def authorize(self, app_name: str = APP_NAME) -> dict:
        """POST /api/local/authorize: Zotero shows Allow / Always Allow / Deny."""
        if not self.server_id:
            raise ZoteroError(
                "authorize needs the live server id (428 without it)",
                Result.UNMATCHED,
            )
        response = self._local(
            "/api/local/authorize",
            data=json.dumps({"appName": app_name}).encode(),
            method="POST",
            expect=(200, 403, 429),
            timeout=AUTHORIZE_TIMEOUT,
        )
        if response.status == 429:
            retry = header(response.headers, "Retry-After") or "60"
            raise ZoteroError(f"authorize rate-limited; retry after {retry} s")
        if response.status == 403:
            # A denial answers {"denied": true} (record 19); the preference-off
            # 403 every request gets has no specified body (record 32), so the
            # status is branched on first and the body read leniently.
            try:
                verdict = json.loads(response.body)
            except ValueError:
                verdict = None
            if isinstance(verdict, Mapping) and verdict.get("denied"):
                raise ZoteroError("authorization denied", Result.UNMATCHED)
            raise LocalApiDisabledError()
        payload = self._decode_json(response.body, "authorize response")
        if isinstance(payload, Mapping) and payload.get("denied"):
            raise ZoteroError("authorization denied", Result.UNMATCHED)
        if not isinstance(payload, Mapping) or not isinstance(payload.get("key"), str):
            raise ZoteroError("malformed authorize response: expected a key")
        return {"key": payload["key"], "remember": bool(payload.get("remember"))}

    def create_items(self, items: list[dict]) -> dict:
        """POST up to 50 items; returns Zotero's successful/unchanged/failed envelope.

        No ``If-Unmodified-Since-Version`` and no ``Zotero-Write-Token`` ride
        the request: research records 24/69 scope the 428 to writes that
        modify existing objects, and the 2026-09-07 sitting's bare
        ``POST /items`` (server id and API key only) was accepted with
        ``successful`` carrying the new key.
        """
        if not self.server_id:
            raise ZoteroError(
                "create_items needs the live server id (428 without it)",
                Result.UNMATCHED,
            )
        if not self.api_key:
            raise ZoteroError(
                "create_items needs an API key from authorize", Result.UNMATCHED
            )
        response = self._local(
            f"{_USER}/items",
            data=json.dumps(items).encode(),
            method="POST",
            expect=(200, 401),
        )
        if response.status == 401:
            raise ApiKeyRejectedError()
        payload = self._decode_json(response.body, "create response")
        if not isinstance(payload, Mapping) or "successful" not in payload:
            raise ZoteroError(
                "malformed create response: expected successful/unchanged/failed"
            )
        return dict(payload)

    def trash_item(self, key: str, version: int) -> int:
        return self._mutate(
            key, version, method="PATCH", data=json.dumps({"deleted": True}).encode()
        )

    def delete_item(self, key: str, version: int) -> int:
        return self._mutate(key, version, method="DELETE")

    def _mutate(self, key, version, *, method, data=None) -> int:
        if not self.api_key:
            raise ZoteroError(
                f"{method} needs an API key from authorize", Result.UNMATCHED
            )
        headers = self._headers(
            {
                "If-Unmodified-Since-Version": str(version),
                "Content-Type": "application/json",
            }
        )
        response = self._http(
            f"{self.base}{_USER}/items/{key}", data=data, headers=headers, method=method
        )
        if response.status == 412:
            raise ZoteroError(f"{method} {key}: version moved (412)", Result.UNMATCHED)
        if response.status not in (200, 204):
            raise ZoteroError(f"{method} {key}: HTTP {response.status}")
        return response.status

    # -- Better BibTeX JSON-RPC -------------------------------------------------

    def _rpc(
        self, method: str, params: list, *, timeout: float | None = None
    ) -> object:
        payload = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": 1,
            }
        ).encode()
        response = self._http(
            f"{self.base}/better-bibtex/json-rpc",
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )
        if response.status != 200:
            raise ZoteroError(f"JSON-RPC HTTP {response.status}")
        reply = self._decode_json(response.body, "JSON-RPC response")
        if not isinstance(reply, dict):
            raise ZoteroError("malformed JSON-RPC response: expected an object")
        if reply.get("jsonrpc") != "2.0":
            raise ZoteroError("malformed JSON-RPC response: invalid version")
        has_result = "result" in reply
        has_error = "error" in reply
        if has_result == has_error:
            raise ZoteroError(
                "malformed JSON-RPC response: expected exactly one of result or error"
            )
        valid_id = type(reply.get("id")) is int and reply["id"] == 1
        bbt_null_error_id = has_error and "id" in reply and reply["id"] is None
        if not (valid_id or bbt_null_error_id):
            raise ZoteroError("malformed JSON-RPC response: invalid id")
        if has_error:
            raise ZoteroError(f"JSON-RPC error: {reply['error']}", Result.UNMATCHED)
        return reply["result"]

    def ready(self) -> dict:
        result = self._rpc("api.ready", [])
        if not isinstance(result, dict):
            raise ZoteroError("malformed api.ready result: expected an object")
        return result

    def attachments(self, citation_key: str) -> list[dict]:
        """BBT ``item.attachments``: the annotation fallback §3.3 step 2 names (unwired)."""
        result = self._rpc("item.attachments", [citation_key])
        return self._validate_object_list(result, "item.attachments result")

    def export_csl(self, citation_keys: list[str]) -> list[dict]:
        """BBT ``item.export``: the documented CSL fallback (§3.3 step 4)."""
        exported = self._rpc(
            "item.export", [citation_keys, CSL_TRANSLATOR], timeout=EXPORT_TIMEOUT
        )
        if not isinstance(exported, list):
            exported = self._decode_json(exported, "item.export result")
        return self._validate_csl_items(exported, "item.export result")
