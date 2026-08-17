import json
import subprocess
from pathlib import Path

import pytest

from harness_core import paths


@pytest.fixture
def vault_with_map(tmp_vault):
    h = tmp_vault / ".harness"
    h.mkdir()
    (h / "machine.json").write_text(
        json.dumps({"path_map": {"D:\\Zotero\\": "/mnt/d/Zotero/"}})
    )
    return tmp_vault


def test_prefix_map(vault_with_map):
    p = paths.to_local("D:\\Zotero\\storage\\AB\\x.pdf", vault_with_map)
    assert p == Path("/mnt/d/Zotero/storage/AB/x.pdf")


def test_prefix_map_case_insensitive(vault_with_map):
    p = paths.to_local("d:\\zotero\\storage\\AB\\x.pdf", vault_with_map)
    assert p == Path("/mnt/d/Zotero/storage/AB/x.pdf")


def test_wslpath_fallback(tmp_vault, monkeypatch):
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(
            a, 0, stdout="/mnt/d/Zotero/storage/AB/x.pdf\n"
        ),
    )
    p = paths.to_local("D:\\Zotero\\storage\\AB\\x.pdf", tmp_vault)
    assert p == Path("/mnt/d/Zotero/storage/AB/x.pdf")


def test_unresolvable_raises(tmp_vault, monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError("wslpath missing")

    monkeypatch.setattr(subprocess, "run", boom)
    with pytest.raises(paths.PathError):
        paths.to_local("D:\\x.pdf", tmp_vault)
