import subprocess
from pathlib import Path

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
    log = subprocess.run(
        ["git", "log", "--oneline"], cwd=tmp_vault, capture_output=True, text=True
    ).stdout
    assert "bibliography" in log


def test_write_is_idempotent(tmp_vault):
    assert bibliography.write_and_commit(tmp_vault, ITEMS) is True
    assert bibliography.write_and_commit(tmp_vault, ITEMS) is False


def test_write_commit_excludes_and_preserves_unrelated_staged_path(tmp_vault):
    sentinel = tmp_vault / "sentinel.txt"
    sentinel.write_bytes(b"unrelated staged bytes\n")
    subprocess.run(["git", "add", "sentinel.txt"], cwd=tmp_vault, check=True)
    staged_blob_before = subprocess.run(
        ["git", "show", ":sentinel.txt"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout
    staged_diff_before = subprocess.run(
        ["git", "diff", "--cached", "--binary", "--", "sentinel.txt"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout

    assert bibliography.write_and_commit(tmp_vault, ITEMS) is True

    committed_paths = subprocess.run(
        ["git", "show", "--pretty=format:", "--name-only", "HEAD"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    staged_blob_after = subprocess.run(
        ["git", "show", ":sentinel.txt"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout
    staged_diff_after = subprocess.run(
        ["git", "diff", "--cached", "--binary", "--", "sentinel.txt"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout

    assert committed_paths == [bibliography.BIB_PATH]
    assert staged_blob_after == staged_blob_before == sentinel.read_bytes()
    assert staged_diff_after == staged_diff_before


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


def test_staleness_present_directory_is_unmatched(tmp_vault):
    (tmp_vault / bibliography.BIB_PATH).mkdir()

    assert bibliography.staleness(tmp_vault, StubClient(ITEMS)) is Result.UNMATCHED


def test_staleness_stat_failure_is_unreachable(tmp_vault, monkeypatch):
    bib_path = tmp_vault / bibliography.BIB_PATH
    real_stat = Path.stat

    def denied(path, *args, **kwargs):
        if path == bib_path:
            raise PermissionError("stat denied")
        return real_stat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", denied)

    assert bibliography.staleness(tmp_vault, StubClient(ITEMS)) is Result.UNREACHABLE


def test_staleness_read_failure_is_unreachable(tmp_vault, monkeypatch):
    bib_path = tmp_vault / bibliography.BIB_PATH
    bib_path.write_text("[]", encoding="utf-8")
    real_read_text = Path.read_text

    def denied(path, *args, **kwargs):
        if path == bib_path:
            raise PermissionError("read denied")
        return real_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", denied)

    assert bibliography.staleness(tmp_vault, StubClient(ITEMS)) is Result.UNREACHABLE


def test_staleness_corrupt_committed_bibliography_is_unmatched(tmp_vault):
    (tmp_vault / bibliography.BIB_PATH).write_text("{", encoding="utf-8")

    assert bibliography.staleness(tmp_vault, StubClient(ITEMS)) is Result.UNMATCHED


def test_staleness_undecodable_committed_bibliography_is_unreachable(tmp_vault):
    (tmp_vault / bibliography.BIB_PATH).write_bytes(b"\xff")

    assert bibliography.staleness(tmp_vault, StubClient(ITEMS)) is Result.UNREACHABLE


@pytest.mark.parametrize("malformed", [{"items": ITEMS}, ["not-an-item"]])
def test_staleness_malformed_fresh_bibliography_is_unreachable(tmp_vault, malformed):
    bibliography.write_and_commit(tmp_vault, ITEMS)

    assert (
        bibliography.staleness(tmp_vault, StubClient(malformed)) is Result.UNREACHABLE
    )
