import json
import subprocess

import pytest

from harness_core import Result, bibliography


ITEMS = [
    {"id": "smith2020", "title": "Mortality decline", "type": "article-journal"},
    {"id": "jones2021", "title": "Replication study", "type": "article-journal"},
]


class StubClient:
    def __init__(self, items):
        self._items = items
        self.fail = False

    def export_csl(self, citekeys):
        if self.fail:
            from harness_core.zotero import ZoteroError
            raise ZoteroError("down")
        return self._items


def test_write_and_commit_then_load(tmp_vault):
    changed = bibliography.write_and_commit(tmp_vault, ITEMS)
    assert changed is True
    bib = bibliography.load(tmp_vault)
    assert bib.citekeys == {"smith2020", "jones2021"}
    assert bib.entry("smith2020")["title"] == "Mortality decline"
    log = subprocess.run(["git", "log", "--oneline"], cwd=tmp_vault,
                         capture_output=True, text=True).stdout
    assert "bibliography" in log


def test_write_is_idempotent(tmp_vault):
    assert bibliography.write_and_commit(tmp_vault, ITEMS) is True
    assert bibliography.write_and_commit(tmp_vault, ITEMS) is False


def test_staleness_matched(tmp_vault):
    bibliography.write_and_commit(tmp_vault, ITEMS)
    assert bibliography.staleness(tmp_vault, StubClient(ITEMS)) is Result.MATCHED


def test_staleness_unmatched(tmp_vault):
    bibliography.write_and_commit(tmp_vault, ITEMS)
    newer = ITEMS + [{"id": "lee2022", "title": "New paper", "type": "article-journal"}]
    assert bibliography.staleness(tmp_vault, StubClient(newer)) is Result.UNMATCHED


def test_staleness_unreachable(tmp_vault):
    bibliography.write_and_commit(tmp_vault, ITEMS)
    client = StubClient(ITEMS)
    client.fail = True
    assert bibliography.staleness(tmp_vault, client) is Result.UNREACHABLE


def test_staleness_skipped_without_file(tmp_vault):
    assert bibliography.staleness(tmp_vault, StubClient(ITEMS)) is Result.SKIPPED
