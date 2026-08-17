"""Windows→WSL path resolution at use time; nothing machine-specific in-repo (spec §4)."""

import json
import subprocess
from pathlib import Path


class PathError(Exception):
    pass


def load_machine_config(vault_root: Path) -> dict:
    f = Path(vault_root) / ".harness" / "machine.json"
    if not f.is_file():
        return {}
    return json.loads(f.read_text())


def to_local(path: str, vault_root: Path) -> Path:
    cfg = load_machine_config(vault_root)
    for prefix, repl in cfg.get("path_map", {}).items():
        if path.lower().startswith(prefix.lower()):
            rest = path[len(prefix) :].replace("\\", "/")
            return Path(repl + rest)
    try:
        proc = subprocess.run(
            ["wslpath", "-u", path], capture_output=True, text=True, check=False
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return Path(proc.stdout.strip())
    except FileNotFoundError:
        pass
    raise PathError(f"cannot resolve {path!r}: no path_map match, wslpath unavailable")
