"""The in-repo citekey universe: x/bibliography.json (spec §4)."""
import json
import subprocess
from pathlib import Path

from . import Result
from .zotero import ZoteroError

BIB_PATH = "x/bibliography.json"


class Bibliography:
    def __init__(self, items):
        self._by_id = {i["id"]: i for i in items}

    @property
    def citekeys(self):
        return set(self._by_id)

    def entry(self, citekey):
        return self._by_id.get(citekey)


def _path(vault_root):
    return Path(vault_root) / BIB_PATH


def load(vault_root) -> Bibliography:
    p = _path(vault_root)
    if not p.is_file():
        return Bibliography([])
    return Bibliography(json.loads(p.read_text()))


def _canonical(items):
    return json.dumps(sorted(items, key=lambda i: i["id"]), indent=1, sort_keys=True)


def write_and_commit(vault_root, items) -> bool:
    p = _path(vault_root)
    new = _canonical(items)
    if p.is_file() and p.read_text() == new:
        return False
    p.write_text(new)
    subprocess.run(["git", "add", BIB_PATH], cwd=vault_root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "chore: bibliography export"],
                   cwd=vault_root, check=True)
    return True


def _fingerprint(items):
    return sorted((i["id"], i.get("title", "")) for i in items)


def staleness(vault_root, client) -> Result:
    p = _path(vault_root)
    if not p.is_file():
        return Result.SKIPPED
    try:
        fresh = client.export_csl(None)
    except ZoteroError:
        return Result.UNREACHABLE
    committed = json.loads(p.read_text())
    return Result.MATCHED if _fingerprint(committed) == _fingerprint(fresh) \
        else Result.UNMATCHED
