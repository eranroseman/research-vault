"""The vault-local store of Zotero local-API keys (Path A's grant, ingest spec §2).

One JSON object per vault, `{<server id>: <key>}`, created 0600 before any
byte lands (row 47). `capture.add` is its one caller.
"""

import datetime
import json
import sys
from pathlib import Path

KEY_STORE = ".research-vault/zotero-keys.json"


def _read_store(path: Path) -> dict | None:
    """The store's object, or None: absent, unreadable, not JSON, or not an
    object. Reading never moves the file; `_store_key` does that once it is
    about to write."""
    try:
        current = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return current if isinstance(current, dict) else None


def _load_key(vault: Path, server_id: str) -> str | None:
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
    # Created 0600 before any byte lands: write_text then chmod would leave the
    # key at the umask default for the instant between them (row 47).
    path.touch(mode=0o600, exist_ok=True)
    path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)


def _store_key(vault: Path, server_id: str, key: str) -> None:
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


def _forget_key(vault: Path, server_id: str) -> None:
    """Row 47(b): drop one server id's entry before a re-grant; an absent or
    unreadable store is nothing to forget."""
    path = Path(vault) / KEY_STORE
    current = _read_store(path)
    if not current or server_id not in current:
        return
    del current[server_id]
    _write_store(path, current)
