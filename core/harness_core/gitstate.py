"""Byte-preserving reads from Git revisions."""

import subprocess
from pathlib import Path


def blob_bytes(vault_root: Path, revision: str, relative: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{revision}:{relative}"],
        cwd=Path(vault_root),
        capture_output=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def revision_paths(vault_root: Path, revision: str, *prefixes: str) -> set[str]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", revision, "--", *prefixes],
        cwd=Path(vault_root),
        capture_output=True,
        text=True,
        check=False,
    )
    return set(result.stdout.splitlines()) if result.returncode == 0 else set()
