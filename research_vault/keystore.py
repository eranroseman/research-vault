"""The vault-local store of Zotero local-API keys (Path A's grant, ingest spec §2).

One JSON object per vault, `{<server id>: <key>}`, created 0600 before any
byte lands (row 47). `capture.add` is its one caller.
"""

import datetime
import json
import os
import sys
from pathlib import Path

KEY_STORE = ".research-vault/zotero-keys.json"


def _read_store(path: Path) -> dict | None:
    """The store's object, or None: absent, unreadable, not JSON, or not an
    object. Reading never moves the file; `store_key` does that once it is
    about to write."""
    try:
        current = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return current if isinstance(current, dict) else None


def load_key(vault: Path, server_id: str) -> str | None:
    store = _read_store(Path(vault) / KEY_STORE)
    value = store.get(server_id) if store else None
    return value if isinstance(value, str) else None


def _move_aside(path: Path) -> None:
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    aside = path.with_name(f"{path.name}.bad-{stamp}")
    path.rename(aside)
    print(  # noqa: T201 -- the one stderr line row 47(a) promises the person
        f"warning: {path} is not a JSON object; moved aside to {aside.name}",
        file=sys.stderr,
    )


def _write_store(path: Path, current: dict) -> None:
    # Created 0600 by the same call that opens it, so no instant exists in
    # which the key sits at the umask default (row 47); O_TRUNC so a shorter
    # store leaves no stale tail; the chmod covers a file that already existed.
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(current, indent=2) + "\n")
    path.chmod(0o600)


def store_key(vault: Path, server_id: str, key: str) -> None:
    path = Path(vault) / KEY_STORE
    path.parent.mkdir(parents=True, exist_ok=True)
    current = _read_store(path)
    if current is None and path.exists():
        # Row 47(a): the bytes are kept for the person, the grant is not lost.
        _move_aside(path)
        current = {}
    current = current or {}
    current[server_id] = key
    _write_store(path, current)


def forget_key(vault: Path, server_id: str) -> None:
    """Row 47(b): drop one server id's entry before a re-grant; an absent or
    unreadable store is nothing to forget."""
    path = Path(vault) / KEY_STORE
    current = _read_store(path)
    if not current or server_id not in current:
        return
    del current[server_id]
    _write_store(path, current)
