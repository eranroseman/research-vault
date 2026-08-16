"""Clients for local Zotero and Better BibTeX JSON-RPC."""

import json
import urllib.error
import urllib.request

from . import Result


CSL_TRANSLATOR = "Better CSL JSON"


class ZoteroError(Exception):
    """A Zotero operation failure with a harness outcome classification."""

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
            raise ZoteroError(
                f"Zotero unreachable at {self.base}: {error}"
            ) from error

    def _rpc(self, method: str, params: list) -> object:
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        }).encode()
        status, body = self._http(
            f"{self.base}/better-bibtex/json-rpc",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        if status != 200:
            raise ZoteroError(f"JSON-RPC HTTP {status}")
        reply = json.loads(body)
        if "error" in reply:
            raise ZoteroError(f"JSON-RPC error: {reply['error']}", Result.UNMATCHED)
        return reply["result"]

    def ready(self) -> dict:
        return self._rpc("api.ready", [])

    def search(self, terms: str) -> list[dict]:
        return self._rpc("item.search", [terms])

    def citekey_of(self, item_keys: list[str]) -> dict[str, str]:
        return self._rpc("item.citationkey", [item_keys])

    def attachments(self, citekey: str) -> list[dict]:
        return self._rpc("item.attachments", [citekey])

    def export_csl(self, citekeys: list[str] | None) -> list[dict]:
        if citekeys is not None:
            exported = self._rpc("item.export", [citekeys, CSL_TRANSLATOR])
            return exported if isinstance(exported, list) else json.loads(exported)

        items = []
        start = 0
        while True:
            status, body = self._http(
                f"{self.base}/api/users/0/items/top?format=csljson&limit=100&start={start}"
            )
            if status != 200:
                raise ZoteroError(f"local API HTTP {status}")
            page = json.loads(body)
            page_items = page["items"] if isinstance(page, dict) else page
            items.extend(page_items)
            if len(page_items) < 100:
                return items
            start += 100

    def register_autoexport(self, target_path: str) -> dict:
        return self._rpc("autoexport.add", [target_path, CSL_TRANSLATOR])

    def supports_local_writes(self) -> bool:
        """Return True only for affirmatively known Zotero 10+ installs."""
        try:
            major = int(str(self.ready().get("zotero", "0")).split(".")[0])
        except Exception:
            return False
        return major >= 10
