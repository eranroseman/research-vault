"""Clients for local Zotero and Better BibTeX JSON-RPC."""

import json
import urllib.error
import urllib.request
from collections.abc import Mapping

from . import Result

CSL_TRANSLATOR = "Better CSL JSON"


class ZoteroError(Exception):
    """A Zotero operation failure with a research-vault outcome classification."""

    def __init__(self, message, result=Result.UNREACHABLE):
        super().__init__(message)
        self.result: Result = result


class ZoteroClient:
    """Access local Zotero through BBT JSON-RPC and its local web API."""

    def __init__(self, base: str = "http://localhost:23119", timeout: float = 5.0):
        self.base = base.rstrip("/")
        self.timeout = timeout

    def _http(self, url, data=None, headers=None, method=None):
        request = urllib.request.Request(
            url,
            data=data,
            headers=headers or {},
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.read()
        except OSError as error:
            raise ZoteroError(f"Zotero unreachable at {self.base}: {error}") from error

    def _rpc(self, method: str, params: list) -> object:
        payload = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": 1,
            }
        ).encode()
        status, body = self._http(
            f"{self.base}/better-bibtex/json-rpc",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        if status != 200:
            raise ZoteroError(f"JSON-RPC HTTP {status}")
        reply = self._decode_json(body, "JSON-RPC response")
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

    def ready(self) -> dict:
        result = self._rpc("api.ready", [])
        if not isinstance(result, dict):
            raise ZoteroError("malformed api.ready result: expected an object")
        return result

    def search(self, terms: str) -> list[dict]:
        result = self._rpc("item.search", [terms])
        return self._validate_object_list(result, "item.search result")

    def citation_key_of(self, item_keys: list[str]) -> dict[str, str]:
        result = self._rpc("item.citationkey", [item_keys])
        if not isinstance(result, Mapping):
            raise ZoteroError(
                "malformed item.citationkey result: expected string mapping"
            )
        citation_keys = {}
        for key, value in result.items():
            if not isinstance(key, str) or (
                value is not None and not isinstance(value, str)
            ):
                raise ZoteroError(
                    "malformed item.citationkey result: expected string mapping"
                )
            if value is not None:
                citation_keys[key] = value
        return citation_keys

    def attachments(self, citation_key: str) -> list[dict]:
        result = self._rpc("item.attachments", [citation_key])
        return self._validate_object_list(result, "item.attachments result")

    def export_csl(self, citation_keys: list[str] | None) -> list[dict]:
        if citation_keys is not None:
            exported = self._rpc("item.export", [citation_keys, CSL_TRANSLATOR])
            if not isinstance(exported, list):
                exported = self._decode_json(exported, "item.export result")
            return self._validate_csl_items(exported, "item.export result")

        items = []
        start = 0
        while True:
            status, body = self._http(
                f"{self.base}/api/users/0/items/top?format=csljson&limit=100&start={start}"
            )
            if status != 200:
                raise ZoteroError(f"local API HTTP {status}")
            page = self._decode_json(body, "local API CSL response")
            if isinstance(page, dict):
                if "items" not in page:
                    raise ZoteroError("malformed local API CSL response: missing items")
                page = page["items"]
            page_items = self._validate_csl_items(page, "local API CSL response")
            items.extend(page_items)
            if len(page_items) < 100:
                return self._normalize_top_level_csl_ids(items)
            start += 100

    def _normalize_top_level_csl_ids(self, items: list[dict]) -> list[dict]:
        uri_keys = [
            item["id"].rsplit("/", 1)[1]
            for item in items
            if isinstance(item.get("id"), str) and "/items/" in item["id"]
        ]
        if not uri_keys:
            return items

        citation_keys = self.citation_key_of(uri_keys)
        normalized = []
        for item in items:
            item_id = item.get("id")
            if not isinstance(item_id, str) or "/items/" not in item_id:
                normalized.append(item)
                continue
            citation_key = citation_keys.get(item_id.rsplit("/", 1)[1])
            if citation_key:
                normalized.append({**item, "id": citation_key})
        return normalized
