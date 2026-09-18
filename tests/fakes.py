"""The shared Zotero double: canned local-API and JSON-RPC responses.

Every offline test that needs Zotero installs one of these on a client. It
answers by exact path (query string included) so a test asserts the wire
shape spec §3.7 records, and it logs every call in order.
"""

import json
from urllib.parse import urlsplit

from research_vault import zotero


class FakeZotero:
    def __init__(self, server_id="6LpvURP2E933", library_name="My Library"):
        self.server_id = server_id
        self.library_name = library_name
        self.calls: list[tuple[str, str, dict]] = []
        self.timeouts: list[float | None] = []  # parallel to `calls`, same index
        self._gets: dict[str, tuple[int, bytes, dict]] = {}
        self._posts: dict[str, tuple[int, bytes, dict]] = {}
        self._rpc: dict[str, object] = {}
        self.get(
            "/api/",
            body=b"",
            headers={
                "X-Zotero-Version": "10.0.1",
                "Zotero-API-Version": "3",
                "Zotero-Schema-Version": "44",
            },
        )

    def get(self, path, status=200, body=None, headers=None, method="GET"):
        payload = body if isinstance(body, bytes) else json.dumps(body).encode()
        table = self._posts if method == "POST" else self._gets
        table[path] = (status, payload, dict(headers or {}))

    def post(self, path, status=200, body=None, headers=None):
        self.get(path, status, body, headers, method="POST")

    def rpc(self, method, result):
        self._rpc[method] = result

    def _http(self, url, data=None, headers=None, method=None, *, timeout=None):
        parts = urlsplit(url)
        path = parts.path + (f"?{parts.query}" if parts.query else "")
        verb = method or ("POST" if data is not None else "GET")
        self.calls.append((verb, path, dict(headers or {})))
        self.timeouts.append(timeout)
        if verb == "POST":
            self._last_post_body = data
        sent_id = (headers or {}).get("Zotero-Server-ID")
        if path.startswith("/api/") and sent_id and sent_id != self.server_id:
            return zotero.Response(412, b"does not match this server", {})
        if verb == "POST" and path.startswith("/api/") and not sent_id:
            # measured server answer; authorize() raises before sending
            return zotero.Response(428, b"Precondition Required", {})
        table = self._posts if verb == "POST" else self._gets
        if path not in table:
            return zotero.Response(404, b"", {"Zotero-Server-ID": self.server_id})
        status, payload, extra = table[path]
        return zotero.Response(
            status, payload, {"Zotero-Server-ID": self.server_id, **extra}
        )

    def _rpc_call(self, method, params, *, timeout=None):
        self.calls.append(("RPC", method, {"params": params}))
        self.timeouts.append(timeout)
        if method not in self._rpc:
            raise zotero.ZoteroError(f"JSON-RPC error: unknown method {method}")
        result = self._rpc[method]
        return result(params) if callable(result) else result

    def install(self, client, monkeypatch):
        monkeypatch.setattr(client, "_http", self._http)
        monkeypatch.setattr(client, "_rpc", self._rpc_call)
        return client


ITEM = {
    "key": "E352DFS8",
    "version": 544,
    "library": {"type": "user", "id": 16413661, "name": "My Library"},
    "meta": {"numChildren": 1},
    "data": {
        "key": "E352DFS8",
        "version": 544,
        "itemType": "journalArticle",
        "title": "Co-writing with opinionated language models affects users' views",
        "creators": [
            {"creatorType": "author", "firstName": "Maurice", "lastName": "Jakesch"}
        ],
        "date": "2023",
        "DOI": "10.1145/3544548.3581196",
        "url": "https://doi.org/10.1145/3544548.3581196",
        "publicationTitle": "CHI 2023",
        "language": "en",
        "abstractNote": "Line one.\n\tLine  two.",
        "extra": "PMID: 28503678\nPMCID: PMC5428074",
        "accessDate": "2026-06-06T10:00:00Z",
        "tags": [{"tag": "ai", "type": 1}],
        "citationKey": "jakesch.etal2023a",
        "relations": {},
        "dateModified": "2026-06-06T10:00:00Z",
    },
}

ATTACHMENT = {
    "key": "D7EJ9FTG",
    "version": 551,
    "data": {
        "key": "D7EJ9FTG",
        "version": 551,
        "itemType": "attachment",
        "linkMode": "imported_file",
        "contentType": "application/pdf",
        "filename": "Jakesch et al. - 2023.pdf",
        "md5": "aa59569ae4f4b3a7c546158d4771c738",
        "mtime": 1788285164904,
        "parentItem": "E352DFS8",
    },
}

CHILD_NOTE = {
    "key": "N0TE0001",
    "version": 552,
    "data": {
        "key": "N0TE0001",
        "version": 552,
        "itemType": "note",
        "note": "<p>Read for the <b>method</b>.</p><p>Second paragraph.</p>",
        "parentItem": "E352DFS8",
    },
}

FULLTEXT = {
    "content": "Page one text " * 60 + "\fPage two text " * 60,
    "indexedPages": 2,
    "totalPages": 2,
}


def canned_item(fake, item=ITEM, children=(ATTACHMENT, CHILD_NOTE), fulltext=FULLTEXT):
    """Register one whole item the way capture reads it."""
    key = item["key"]
    fake.get(f"/api/users/0/items/{key}?format=json", body=item)
    fake.get(f"/api/users/0/items/{key}/children", body=list(children))
    fake.get(f"/api/users/0/items/{key}/children?itemType=annotation", body=[])
    for child in children:
        if child["data"]["itemType"] == "attachment":
            att = child["key"]
            if fulltext is None:
                fake.get(f"/api/users/0/items/{att}/fulltext", status=404, body=b"")
            else:
                fake.get(f"/api/users/0/items/{att}/fulltext", body=fulltext)
            fake.get(
                f"/api/users/0/items/{att}/file/view/url",
                body=b"file:///D:/Zotero/storage/D7EJ9FTG/Jakesch%20et%20al.%20-%202023.pdf",
            )
    return fake
