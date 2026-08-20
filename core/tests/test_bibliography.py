import json
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

    def register_autoexport(self, target):
        self.registered = getattr(self, "registered", []) + [target]
        return {"ok": True}


class FakeClock:
    def __init__(self, on_sleep=None):
        self.now = 0.0
        self.sleeps = []
        self.on_sleep = on_sleep

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds
        if self.on_sleep is not None:
            self.on_sleep(len(self.sleeps), self.now)


def test_commit_autoexport_then_load_without_rewriting_bbt_bytes(tmp_vault):
    target = tmp_vault / bibliography.BIB_PATH
    bbt_bytes = b'[ { "title": "Mortality decline", "id": "smith2020" }, { "id": "jones2021", "title": "Replication study" } ]\n'
    target.write_bytes(bbt_bytes)

    changed = bibliography.commit_autoexport(tmp_vault, bbt_bytes)

    assert changed is True
    assert target.read_bytes() == bbt_bytes
    committed = subprocess.run(
        ["git", "show", f"HEAD:{bibliography.BIB_PATH}"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout
    assert committed == bbt_bytes
    bib = bibliography.load(tmp_vault)
    assert bib.citekeys == {"smith2020", "jones2021"}
    assert bib.entry("smith2020")["title"] == "Mortality decline"
    log = subprocess.run(
        ["git", "log", "--oneline"], cwd=tmp_vault, capture_output=True, text=True
    ).stdout
    assert "bibliography" in log


def test_commit_autoexport_is_idempotent(tmp_vault):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_text(json.dumps(ITEMS))
    snapshot = target.read_bytes()
    assert bibliography.commit_autoexport(tmp_vault, snapshot) is True
    assert bibliography.commit_autoexport(tmp_vault, snapshot) is False


def test_commit_autoexport_excludes_and_preserves_all_unrelated_state(tmp_vault):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_bytes(b'[{"id":"baseline","title":"Baseline"}]\n')
    unstaged = tmp_vault / "unstaged.txt"
    unstaged.write_bytes(b"baseline\n")
    untracked = tmp_vault / "untracked.txt"
    untracked.write_bytes(b"untracked bytes\n")
    subprocess.run(
        ["git", "add", "unstaged.txt", bibliography.BIB_PATH],
        cwd=tmp_vault,
        check=True,
    )
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=tmp_vault, check=True)
    unstaged.write_bytes(b"unstaged bytes\n")
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
    target.write_bytes(b'[{"title":"Mortality decline","id":"smith2020"}]\n')
    status_before = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout

    assert bibliography.commit_autoexport(tmp_vault, target.read_bytes()) is True

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
    assert (
        subprocess.run(
            ["git", "show", f":{bibliography.BIB_PATH}"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
        ).stdout
        == target.read_bytes()
    )
    assert unstaged.read_bytes() == b"unstaged bytes\n"
    assert untracked.read_bytes() == b"untracked bytes\n"
    status_after = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout
    unrelated_before = [
        line
        for line in status_before.splitlines()
        if not line.endswith(b" x/bibliography.json")
    ]
    assert status_after.splitlines() == unrelated_before


def test_commit_autoexport_rejects_preexisting_staged_bibliography_intent(
    tmp_vault,
):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_bytes(b'[{"id":"baseline","title":"Baseline"}]\n')
    subprocess.run(
        ["git", "add", "--", bibliography.BIB_PATH], cwd=tmp_vault, check=True
    )
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=tmp_vault, check=True)
    target.write_bytes(b'[{"id":"staged","title":"User staged"}]\n')
    subprocess.run(
        ["git", "add", "--", bibliography.BIB_PATH], cwd=tmp_vault, check=True
    )
    target.write_bytes(b'[{"id":"worktree","title":"User worktree"}]\n')
    head_before = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    index_path = Path(
        subprocess.run(
            ["git", "rev-parse", "--git-path", "index"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    if not index_path.is_absolute():
        index_path = tmp_vault / index_path
    status_before = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout
    index_before = index_path.read_bytes()
    worktree_before = target.read_bytes()

    with pytest.raises(OSError, match="live index bibliography") as caught:
        bibliography.commit_autoexport(
            tmp_vault, b'[{"id":"validated","title":"Validated"}]\n'
        )

    assert "index" in str(caught.value)
    assert (
        subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        == head_before
    )
    assert index_path.read_bytes() == index_before
    assert target.read_bytes() == worktree_before
    assert (
        subprocess.run(
            ["git", "status", "--porcelain=v1"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
        ).stdout
        == status_before
    )


def test_commit_autoexport_preserves_concurrent_bibliography_index_update(
    tmp_vault, monkeypatch
):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_bytes(b'[{"id":"baseline","title":"Baseline"}]\n')
    subprocess.run(
        ["git", "add", "--", bibliography.BIB_PATH], cwd=tmp_vault, check=True
    )
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=tmp_vault, check=True)
    expected_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    concurrent = b'[{"id":"concurrent","title":"Concurrent stage"}]\n'
    real_run = subprocess.run
    staged = []

    def stage_before_index_lock(command, *args, **kwargs):
        if command == ["git", "rev-parse", "--git-path", "index"] and not staged:
            target.write_bytes(concurrent)
            real_run(
                ["git", "add", "--", bibliography.BIB_PATH],
                cwd=tmp_vault,
                check=True,
            )
            staged.append(True)
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(bibliography.subprocess, "run", stage_before_index_lock)

    with pytest.raises(OSError, match="live index bibliography"):
        bibliography.commit_autoexport(
            tmp_vault, b'[{"id":"validated","title":"Validated"}]\n'
        )

    assert staged == [True]
    assert (
        subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        == expected_head
    )
    assert (
        subprocess.run(
            ["git", "show", f":{bibliography.BIB_PATH}"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
        ).stdout
        == concurrent
    )
    assert target.read_bytes() == concurrent


def test_commit_autoexport_holds_live_index_lock_through_head_cas(
    tmp_vault, monkeypatch
):
    index_path = Path(
        subprocess.run(
            ["git", "rev-parse", "--git-path", "index"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    if not index_path.is_absolute():
        index_path = tmp_vault / index_path
    snapshot = b'[{"id":"validated","title":"Validated"}]\n'
    real_run = subprocess.run
    lock_seen = []

    def require_index_lock(command, *args, **kwargs):
        if command[:3] == ["git", "update-ref", "HEAD"]:
            lock_seen.append(Path(f"{index_path}.lock").is_file())
            assert lock_seen[-1]
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(bibliography.subprocess, "run", require_index_lock)

    assert bibliography.commit_autoexport(tmp_vault, snapshot) is True

    assert lock_seen == [True]
    assert not Path(f"{index_path}.lock").exists()
    assert (
        subprocess.run(
            ["git", "show", f":{bibliography.BIB_PATH}"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
        ).stdout
        == snapshot
    )


def test_commit_autoexport_preserves_lock_reacquired_after_index_publication(
    tmp_vault, monkeypatch
):
    index_path = Path(
        subprocess.run(
            ["git", "rev-parse", "--git-path", "index"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    if not index_path.is_absolute():
        index_path = tmp_vault / index_path
    lock_path = Path(f"{index_path}.lock")
    concurrent_lock = b"concurrent writer lock\n"
    real_replace = bibliography.os.replace

    def publish_then_reacquire(source, destination):
        real_replace(source, destination)
        Path(source).write_bytes(concurrent_lock)

    monkeypatch.setattr(bibliography.os, "replace", publish_then_reacquire)

    assert (
        bibliography.commit_autoexport(
            tmp_vault, b'[{"id":"validated","title":"Validated"}]\n'
        )
        is True
    )

    assert lock_path.read_bytes() == concurrent_lock


def test_commit_autoexport_publication_failure_rolls_back_existing_head(
    tmp_vault, monkeypatch
):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_bytes(b'[{"id":"baseline","title":"Baseline"}]\n')
    staged = tmp_vault / "staged.txt"
    staged.write_bytes(b"unrelated staged bytes\n")
    subprocess.run(
        ["git", "add", "--", bibliography.BIB_PATH, "staged.txt"],
        cwd=tmp_vault,
        check=True,
    )
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=tmp_vault, check=True)
    staged.write_bytes(b"new unrelated staged bytes\n")
    subprocess.run(["git", "add", "--", "staged.txt"], cwd=tmp_vault, check=True)
    worktree_before = b'[{"id":"worktree","title":"Worktree"}]\n'
    target.write_bytes(worktree_before)
    head_before = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    index_path = Path(
        subprocess.run(
            ["git", "rev-parse", "--git-path", "index"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    if not index_path.is_absolute():
        index_path = tmp_vault / index_path
    index_before = index_path.read_bytes()
    lock_path = Path(f"{index_path}.lock")

    def fail_publication(source, destination):
        raise OSError("index publication failed")

    monkeypatch.setattr(bibliography.os, "replace", fail_publication)

    with pytest.raises(OSError, match="index publication failed"):
        bibliography.commit_autoexport(
            tmp_vault, b'[{"id":"validated","title":"Validated"}]\n'
        )

    assert (
        subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        == head_before
    )
    assert index_path.read_bytes() == index_before
    assert target.read_bytes() == worktree_before
    assert not lock_path.exists()


def test_commit_autoexport_publication_failure_restores_unborn_head(
    tmp_vault, monkeypatch
):
    target = tmp_vault / bibliography.BIB_PATH
    worktree_before = b'[{"id":"worktree","title":"Worktree"}]\n'
    target.write_bytes(worktree_before)
    staged = tmp_vault / "staged.txt"
    staged.write_bytes(b"unrelated staged bytes\n")
    subprocess.run(["git", "add", "--", "staged.txt"], cwd=tmp_vault, check=True)
    index_path = Path(
        subprocess.run(
            ["git", "rev-parse", "--git-path", "index"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    if not index_path.is_absolute():
        index_path = tmp_vault / index_path
    index_before = index_path.read_bytes()
    lock_path = Path(f"{index_path}.lock")

    def fail_publication(source, destination):
        raise OSError("index publication failed")

    monkeypatch.setattr(bibliography.os, "replace", fail_publication)

    with pytest.raises(OSError, match="index publication failed"):
        bibliography.commit_autoexport(
            tmp_vault, b'[{"id":"validated","title":"Validated"}]\n'
        )

    assert (
        subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=tmp_vault,
            capture_output=True,
        ).returncode
        != 0
    )
    assert index_path.read_bytes() == index_before
    assert target.read_bytes() == worktree_before
    assert not lock_path.exists()


def test_commit_autoexport_publication_rollback_cas_preserves_concurrent_head(
    tmp_vault, monkeypatch
):
    target = tmp_vault / bibliography.BIB_PATH
    worktree_before = b'[{"id":"baseline","title":"Baseline"}]\n'
    target.write_bytes(worktree_before)
    subprocess.run(
        ["git", "add", "--", bibliography.BIB_PATH], cwd=tmp_vault, check=True
    )
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=tmp_vault, check=True)
    expected_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    index_path = Path(
        subprocess.run(
            ["git", "rev-parse", "--git-path", "index"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    if not index_path.is_absolute():
        index_path = tmp_vault / index_path
    index_before = index_path.read_bytes()
    lock_path = Path(f"{index_path}.lock")
    concurrent = []

    def race_then_fail_publication(source, destination):
        published_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        tree = subprocess.run(
            ["git", "rev-parse", f"{expected_head}^{{tree}}"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        concurrent_head = subprocess.run(
            ["git", "commit-tree", tree, "-p", expected_head],
            cwd=tmp_vault,
            check=True,
            input="concurrent replacement\n",
            capture_output=True,
            text=True,
        ).stdout.strip()
        subprocess.run(
            ["git", "update-ref", "HEAD", concurrent_head, published_head],
            cwd=tmp_vault,
            check=True,
        )
        concurrent.append(concurrent_head)
        raise OSError("index publication failed")

    monkeypatch.setattr(bibliography.os, "replace", race_then_fail_publication)

    with pytest.raises(OSError, match="roll back HEAD"):
        bibliography.commit_autoexport(
            tmp_vault, b'[{"id":"validated","title":"Validated"}]\n'
        )

    assert (
        subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        == concurrent[0]
    )
    assert index_path.read_bytes() == index_before
    assert target.read_bytes() == worktree_before
    assert not lock_path.exists()


def test_commit_autoexport_uses_snapshot_plumbing_not_live_index_or_target(
    tmp_vault, monkeypatch
):
    target = tmp_vault / bibliography.BIB_PATH
    snapshot = b'[{"id":"validated","title":"Validated"}]\n'
    target.write_bytes(snapshot)
    calls = []
    real_run = subprocess.run

    def recording_run(command, *args, **kwargs):
        calls.append(command)
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(bibliography.subprocess, "run", recording_run)

    assert bibliography.commit_autoexport(tmp_vault, snapshot) is True
    commands = [command[:2] for command in calls]
    assert ["git", "hash-object"] in commands
    assert ["git", "read-tree"] in commands
    assert ["git", "update-index"] in commands
    assert ["git", "write-tree"] in commands
    assert ["git", "commit-tree"] in commands
    assert ["git", "update-ref"] in commands
    assert not any(
        command[:2] in (["git", "add"], ["git", "commit"]) for command in calls
    )


def test_commit_autoexport_commits_validated_snapshot_not_later_target_bytes(tmp_vault):
    target = tmp_vault / bibliography.BIB_PATH
    validated = b'[{"id":"validated","title":"Validated"}]\n'
    later = b'[{"id":"later","title":"Later"}]\n'
    target.write_bytes(later)

    assert bibliography.commit_autoexport(tmp_vault, validated) is True

    assert target.read_bytes() == later
    assert (
        subprocess.run(
            ["git", "show", f"HEAD:{bibliography.BIB_PATH}"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
        ).stdout
        == validated
    )
    assert (
        subprocess.run(
            ["git", "show", f":{bibliography.BIB_PATH}"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
        ).stdout
        == validated
    )
    assert (
        subprocess.run(
            ["git", "status", "--porcelain=v1", "--", bibliography.BIB_PATH],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
        ).stdout
        == b" M x/bibliography.json\n"
    )


def test_commit_autoexport_unborn_repo_preserves_live_index_and_commits_only_snapshot(
    tmp_vault,
):
    staged = tmp_vault / "staged.txt"
    staged.write_bytes(b"staged bytes\n")
    subprocess.run(["git", "add", "--", "staged.txt"], cwd=tmp_vault, check=True)
    index_before = subprocess.run(
        ["git", "diff", "--cached", "--binary"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout
    snapshot = b'[{"id":"validated","title":"Validated"}]\n'

    assert bibliography.commit_autoexport(tmp_vault, snapshot) is True

    assert subprocess.run(
        ["git", "show", "--pretty=format:", "--name-only", "HEAD"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines() == [bibliography.BIB_PATH]
    assert (
        subprocess.run(
            ["git", "diff", "--cached", "--binary"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
        ).stdout
        == index_before
    )
    assert (
        subprocess.run(
            ["git", "show", f":{bibliography.BIB_PATH}"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
        ).stdout
        == snapshot
    )
    assert staged.read_bytes() == b"staged bytes\n"


def test_commit_autoexport_head_cas_never_overwrites_concurrent_commit(
    tmp_vault, monkeypatch
):
    baseline = tmp_vault / "baseline.txt"
    baseline.write_text("baseline\n")
    subprocess.run(["git", "add", "baseline.txt"], cwd=tmp_vault, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=tmp_vault, check=True)
    expected_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    snapshot = b'[{"id":"validated","title":"Validated"}]\n'
    real_run = subprocess.run
    concurrent = []

    def race_update_ref(command, *args, **kwargs):
        if command[:3] == ["git", "update-ref", "HEAD"] and not concurrent:
            tree = real_run(
                ["git", "rev-parse", "HEAD^{tree}"],
                cwd=tmp_vault,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            commit = real_run(
                ["git", "commit-tree", tree, "-p", expected_head],
                cwd=tmp_vault,
                check=True,
                input="concurrent human commit\n",
                capture_output=True,
                text=True,
            ).stdout.strip()
            real_run(
                ["git", "update-ref", "HEAD", commit, expected_head],
                cwd=tmp_vault,
                check=True,
            )
            concurrent.append(commit)
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(bibliography.subprocess, "run", race_update_ref)

    with pytest.raises(subprocess.CalledProcessError):
        bibliography.commit_autoexport(tmp_vault, snapshot)

    assert (
        subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        == concurrent[0]
    )


def test_staleness_matched(tmp_vault):
    (tmp_vault / bibliography.BIB_PATH).write_text(json.dumps(ITEMS))
    assert bibliography.staleness(tmp_vault, StubClient(ITEMS)) is Result.MATCHED


def test_staleness_unmatched(tmp_vault):
    (tmp_vault / bibliography.BIB_PATH).write_text(json.dumps(ITEMS))
    newer = ITEMS + [{"id": "lee2022", "title": "New paper", "type": "article-journal"}]
    assert bibliography.staleness(tmp_vault, StubClient(newer)) is Result.UNMATCHED


def test_staleness_unreachable(tmp_vault):
    (tmp_vault / bibliography.BIB_PATH).write_text(json.dumps(ITEMS))
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
    (tmp_vault / bibliography.BIB_PATH).write_text(json.dumps(ITEMS))

    assert (
        bibliography.staleness(tmp_vault, StubClient(malformed)) is Result.UNREACHABLE
    )


@pytest.mark.parametrize(
    "contents",
    [
        "{",
        '{"items": []}',
        '["not-an-entry"]',
        '[{"id": "x", "DOI": 123}]',
        '[{"id": ""}]',
        '[{"id": "bad\\nkey"}]',
        '[{"id": "../escape"}]',
    ],
    ids=[
        "truncated-json",
        "wrong-top-level",
        "wrong-entry",
        "non-string-doi",
        "empty-id",
        "multiline-id",
        "unsafe-id",
    ],
)
def test_load_classifies_readable_invalid_bibliography_as_unmatched(
    tmp_vault, contents
):
    (tmp_vault / bibliography.BIB_PATH).write_text(contents)

    with pytest.raises(bibliography.BibliographyError) as caught:
        bibliography.load(tmp_vault)

    assert caught.value.result is Result.UNMATCHED


def test_load_classifies_undecodable_bibliography_as_unreachable(tmp_vault):
    (tmp_vault / bibliography.BIB_PATH).write_bytes(b"\xff")

    with pytest.raises(bibliography.BibliographyError) as caught:
        bibliography.load(tmp_vault)

    assert caught.value.result is Result.UNREACHABLE


def _observe(tmp_vault, client, clock, **kwargs):
    return bibliography.observe_autoexport(
        tmp_vault,
        client,
        settle_seconds=kwargs.pop("settle_seconds", 2),
        poll_interval=kwargs.pop("poll_interval", 1),
        monotonic=clock.monotonic,
        sleep=clock.sleep,
        **kwargs,
    )


def test_observe_rejects_nonpositive_poll_interval_before_any_io(tmp_vault):
    class ForbiddenClient:
        def export_csl(self, citekeys):
            raise AssertionError("must not fetch")

    with pytest.raises(ValueError, match="poll_interval"):
        bibliography.observe_autoexport(tmp_vault, ForbiddenClient(), poll_interval=0)


def test_observe_matches_byte_different_json_by_sorted_id_title(tmp_vault):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_bytes(
        b'[{"title":"Replication study","extra":true,"id":"jones2021"},'
        b'{"id":"smith2020","title":"Mortality decline"}]\n'
    )
    client = StubClient(ITEMS)
    clock = FakeClock()

    observed = _observe(tmp_vault, client, clock)

    assert observed.result is Result.MATCHED
    assert observed.staleness is Result.MATCHED
    assert getattr(client, "registered", []) == []
    assert clock.sleeps == []


@pytest.mark.parametrize("deadline_read", [1, 2], ids=["first-window", "second-window"])
def test_observe_accepts_target_appearing_on_each_final_deadline_read(
    tmp_vault, deadline_read
):
    target = tmp_vault / bibliography.BIB_PATH
    client = StubClient(ITEMS)

    def write_at_deadline(sleep_number, now):
        if sleep_number == deadline_read:
            target.write_text(json.dumps(ITEMS))

    clock = FakeClock(write_at_deadline)
    observed = _observe(tmp_vault, client, clock, settle_seconds=1)

    assert observed.result is Result.MATCHED
    assert observed.staleness is Result.MATCHED
    assert getattr(client, "registered", []) == (
        [] if deadline_read == 1 else [str(target)]
    )


def test_observe_uses_one_fresh_export_through_both_windows_and_staleness(
    tmp_vault,
):
    calls = []

    class ChangingClient(StubClient):
        def export_csl(self, citekeys):
            calls.append(citekeys)
            return ITEMS if len(calls) == 1 else []

    client = ChangingClient(ITEMS)
    clock = FakeClock()
    observed = _observe(tmp_vault, client, clock, settle_seconds=1)

    assert observed.result is Result.UNMATCHED
    assert observed.staleness is Result.UNMATCHED
    assert calls == [None]
    assert getattr(client, "registered", []) == [str(tmp_vault / bibliography.BIB_PATH)]
    assert clock.sleeps == [1, 1]


def test_observe_output_during_first_window_prevents_registration(tmp_vault):
    target = tmp_vault / bibliography.BIB_PATH
    clock = FakeClock(
        lambda sleep_number, now: (
            target.write_text(json.dumps(ITEMS)) if sleep_number == 1 else None
        )
    )
    client = StubClient(ITEMS)

    observed = _observe(tmp_vault, client, clock)

    assert observed.result is Result.MATCHED
    assert getattr(client, "registered", []) == []


def test_observe_registers_once_then_accepts_output_in_second_window(tmp_vault):
    target = tmp_vault / bibliography.BIB_PATH
    clock = FakeClock(
        lambda sleep_number, now: (
            target.write_text(json.dumps(ITEMS)) if sleep_number == 3 else None
        )
    )
    client = StubClient(ITEMS)

    observed = _observe(tmp_vault, client, clock)

    assert observed.result is Result.MATCHED
    assert getattr(client, "registered", []) == [str(target)]


def test_observe_registers_one_lexically_absolute_target_from_relative_vault(
    tmp_vault, monkeypatch
):
    monkeypatch.chdir(tmp_vault.parent)
    relative_vault = Path(tmp_vault.name)
    target = tmp_vault / bibliography.BIB_PATH

    class RegisteringClient(StubClient):
        def register_autoexport(self, registered_target):
            self.registered = [registered_target]
            Path(registered_target).write_text(json.dumps(ITEMS))
            return {"ok": True}

    client = RegisteringClient(ITEMS)
    observed = _observe(relative_vault, client, FakeClock(), settle_seconds=0)

    assert observed.result is Result.MATCHED
    assert client.registered == [str(target.absolute())]


@pytest.mark.parametrize(
    "target_setup",
    [
        lambda target: None,
        lambda target: target.mkdir(),
        lambda target: target.write_text("{"),
        lambda target: target.write_text('[{"id":"different","title":"Other"}]'),
    ],
    ids=["absent", "non-regular", "malformed", "mismatch"],
)
def test_observe_persistent_target_failures_are_unmatched(tmp_vault, target_setup):
    target_setup(tmp_vault / bibliography.BIB_PATH)
    client = StubClient(ITEMS)
    observed = _observe(tmp_vault, client, FakeClock(), settle_seconds=1)

    assert observed.result is Result.UNMATCHED
    assert observed.staleness is Result.UNMATCHED
    assert getattr(client, "registered", []) == [str(tmp_vault / bibliography.BIB_PATH)]


def test_observe_target_io_failure_is_unreachable(tmp_vault, monkeypatch):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_text("[]")
    real_open = bibliography.os.open

    def fail_target(path, *args, **kwargs):
        if path == target.name and kwargs.get("dir_fd") is not None:
            raise PermissionError("denied")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(bibliography.os, "open", fail_target)
    observed = _observe(tmp_vault, StubClient(ITEMS), FakeClock())

    assert observed.result is Result.UNREACHABLE
    assert observed.staleness is Result.UNREACHABLE


@pytest.mark.parametrize("failure_point", ["fdopen", "read"])
def test_observe_target_buffer_read_oserror_is_unreachable(
    tmp_vault, monkeypatch, failure_point
):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_text(json.dumps(ITEMS))

    class FailingRead:
        def __init__(self, descriptor):
            self.descriptor = descriptor

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            bibliography.os.close(self.descriptor)

        def read(self):
            raise OSError("target read denied")

    def fail_target_read(descriptor, *args, **kwargs):
        if failure_point == "fdopen":
            raise OSError("target fdopen denied")
        return FailingRead(descriptor)

    monkeypatch.setattr(bibliography.os, "fdopen", fail_target_read)

    observed = _observe(tmp_vault, StubClient(ITEMS), FakeClock())

    assert observed.result is Result.UNREACHABLE
    assert observed.staleness is Result.UNREACHABLE
    assert "denied" in observed.detail


def test_observe_fetches_fresh_evidence_once_even_when_target_read_fails(
    tmp_vault, monkeypatch
):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_text("[]")
    real_open = bibliography.os.open
    client = StubClient(ITEMS)
    calls = []
    original_export = client.export_csl

    def export(citekeys):
        calls.append(citekeys)
        return original_export(citekeys)

    def fail_target(path, *args, **kwargs):
        if path == target.name and kwargs.get("dir_fd") is not None:
            raise PermissionError("denied")
        return real_open(path, *args, **kwargs)

    client.export_csl = export
    monkeypatch.setattr(bibliography.os, "open", fail_target)

    observed = _observe(tmp_vault, client, FakeClock())

    assert observed.result is Result.UNREACHABLE
    assert calls == [None]


def test_observe_target_unicode_failure_is_unreachable(tmp_vault):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_bytes(b"\xff")

    observed = _observe(tmp_vault, StubClient(ITEMS), FakeClock())

    assert observed.result is Result.UNREACHABLE
    assert observed.staleness is Result.UNREACHABLE


@pytest.mark.parametrize("result", [Result.UNMATCHED, Result.UNREACHABLE])
def test_observe_preserves_raw_zotero_error_and_classification(tmp_vault, result):
    from harness_core.zotero import ZoteroError

    class FailingClient(StubClient):
        def export_csl(self, citekeys):
            raise ZoteroError("raw BBT failure", result)

    observed = _observe(tmp_vault, FailingClient(ITEMS), FakeClock())

    assert observed.result is result
    assert observed.detail == "raw BBT failure"
    assert observed.staleness is result


def test_observe_malformed_fresh_evidence_is_unreachable_without_registration(
    tmp_vault,
):
    client = StubClient([{"id": "valid", "title": 42}])

    observed = _observe(tmp_vault, client, FakeClock())

    assert observed.result is Result.UNREACHABLE
    assert getattr(client, "registered", []) == []


@pytest.mark.parametrize("result", [Result.UNMATCHED, Result.UNREACHABLE])
def test_observe_preserves_registration_error_result_and_raw_text(tmp_vault, result):
    from harness_core.zotero import ZoteroError

    class RegistrationFailure(StubClient):
        def register_autoexport(self, target):
            raise ZoteroError("raw registration failure", result)

    observed = _observe(tmp_vault, RegistrationFailure(ITEMS), FakeClock())

    assert observed.result is result
    assert observed.detail == "raw registration failure"


@pytest.mark.parametrize("link_kind", ["target", "parent"])
def test_observe_rejects_symlinked_target_or_parent(tmp_vault, tmp_path, link_kind):
    outside = tmp_path / "outside"
    outside.mkdir()
    outside_target = outside / "bibliography.json"
    outside_target.write_text(json.dumps(ITEMS))
    target = tmp_vault / bibliography.BIB_PATH
    if link_kind == "target":
        target.symlink_to(outside_target)
    else:
        target.parent.rmdir()
        target.parent.symlink_to(outside, target_is_directory=True)

    client = StubClient(ITEMS)
    observed = _observe(tmp_vault, client, FakeClock(), settle_seconds=0)

    assert observed.result is Result.UNMATCHED
    assert observed.staleness is Result.UNMATCHED
    assert getattr(client, "registered", []) == []


@pytest.mark.parametrize("link_level", ["vault", "earlier-ancestor"])
def test_observe_rejects_symlink_anywhere_in_absolute_vault_chain_without_mutation(
    tmp_vault, tmp_path, link_level
):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_text(json.dumps(ITEMS))
    if link_level == "vault":
        linked_vault = tmp_path / "linked-vault"
        linked_vault.symlink_to(tmp_vault, target_is_directory=True)
    else:
        linked_parent = tmp_path / "linked-parent"
        linked_parent.symlink_to(tmp_vault.parent, target_is_directory=True)
        linked_vault = linked_parent / tmp_vault.name
    client = StubClient(ITEMS)

    observed = _observe(linked_vault, client, FakeClock(), settle_seconds=0)

    assert observed.result is Result.UNMATCHED
    assert getattr(client, "registered", []) == []
    assert (
        subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=tmp_vault,
            capture_output=True,
        ).returncode
        != 0
    )


def test_observe_parent_replacement_during_window_never_registers_or_commits(
    tmp_vault,
):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_text("[]")
    original_parent = target.parent
    moved_parent = tmp_vault / "x-original"

    def replace_parent(sleep_number, now):
        if sleep_number == 1:
            original_parent.rename(moved_parent)
            original_parent.mkdir()
            target.write_text(json.dumps(ITEMS))

    client = StubClient(ITEMS)
    observed = _observe(
        tmp_vault,
        client,
        FakeClock(replace_parent),
        settle_seconds=1,
    )

    assert observed.result is Result.UNMATCHED
    assert getattr(client, "registered", []) == []
    assert (
        subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=tmp_vault,
            capture_output=True,
        ).returncode
        != 0
    )


def test_observe_parent_replacement_at_commit_boundary_never_mutates_git(
    tmp_vault, monkeypatch
):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_text(json.dumps(ITEMS))
    original_parent = target.parent
    moved_parent = tmp_vault / "x-original"
    original_commit = bibliography.commit_autoexport

    def replace_then_commit(vault, snapshot, **kwargs):
        original_parent.rename(moved_parent)
        original_parent.mkdir()
        target.write_bytes(snapshot)
        return original_commit(vault, snapshot, **kwargs)

    monkeypatch.setattr(bibliography, "commit_autoexport", replace_then_commit)

    observed = _observe(tmp_vault, StubClient(ITEMS), FakeClock())

    assert observed.result is Result.UNMATCHED
    assert (
        subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=tmp_vault,
            capture_output=True,
        ).returncode
        != 0
    )


@pytest.mark.parametrize(
    "change_target", [False, True], ids=["final-match", "final-change"]
)
def test_observe_commit_failure_preserves_cached_final_staleness(
    tmp_vault, monkeypatch, change_target
):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_text(json.dumps(ITEMS))

    def fail_commit(*args, **kwargs):
        if change_target:
            target.write_text('[{"id":"changed","title":"Changed"}]')
        raise OSError("commit unavailable")

    monkeypatch.setattr(bibliography, "commit_autoexport", fail_commit)

    observed = _observe(tmp_vault, StubClient(ITEMS), FakeClock())

    assert observed.result is Result.UNREACHABLE
    assert observed.staleness is (Result.UNMATCHED if change_target else Result.MATCHED)


def test_observe_post_commit_git_read_oserror_is_unreachable_with_cached_staleness(
    tmp_vault, monkeypatch
):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_text(json.dumps(ITEMS))
    real_run = bibliography.subprocess.run
    monkeypatch.setattr(bibliography, "commit_autoexport", lambda *a, **k: True)

    def fail_head_read(command, *args, **kwargs):
        if command[:2] == ["git", "show"] and command[-1] == (
            f"HEAD:{bibliography.BIB_PATH}"
        ):
            raise OSError("git unavailable")
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(bibliography.subprocess, "run", fail_head_read)

    observed = _observe(tmp_vault, StubClient(ITEMS), FakeClock())

    assert observed.result is Result.UNREACHABLE
    assert observed.staleness is Result.MATCHED
    assert "git unavailable" in observed.detail


def test_observe_commits_validated_snapshot_when_target_changes_before_commit(
    tmp_vault, monkeypatch
):
    target = tmp_vault / bibliography.BIB_PATH
    validated = json.dumps(ITEMS).encode()
    target.write_bytes(validated)
    original_commit = bibliography.commit_autoexport

    def raced_commit(vault, snapshot, **kwargs):
        target.write_text('[{"id":"raced","title":"Raced"}]')
        return original_commit(vault, snapshot, **kwargs)

    monkeypatch.setattr(bibliography, "commit_autoexport", raced_commit)

    observed = _observe(tmp_vault, StubClient(ITEMS), FakeClock())

    assert observed.result is Result.UNMATCHED
    assert observed.staleness is Result.UNMATCHED
    committed = subprocess.run(
        ["git", "show", f"HEAD:{bibliography.BIB_PATH}"],
        cwd=tmp_vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    assert committed.encode() == validated
    assert json.loads(target.read_text())[0]["id"] == "raced"
