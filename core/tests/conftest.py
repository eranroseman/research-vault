import os
import subprocess

import pytest

VAULT_DIRS = ["+", "literatures", "atlas", "calendar", "efforts", "x"]


@pytest.fixture
def tmp_vault(tmp_path):
    for d in VAULT_DIRS:
        (tmp_path / d).mkdir()
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return tmp_path


def pytest_collection_modifyitems(config, items):
    if os.environ.get("HARNESS_LIVE") == "1":
        return
    skip = pytest.mark.skip(reason="live Zotero not enabled (HARNESS_LIVE=1)")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)
