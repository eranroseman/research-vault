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

    changed = bibliography.commit_autoexport(tmp_vault)

    assert changed is True
    assert target.read_bytes() == bbt_bytes
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
    assert bibliography.commit_autoexport(tmp_vault) is True
    assert bibliography.commit_autoexport(tmp_vault) is False


def test_commit_autoexport_excludes_and_preserves_all_unrelated_state(tmp_vault):
    unstaged = tmp_vault / "unstaged.txt"
    unstaged.write_bytes(b"baseline\n")
    untracked = tmp_vault / "untracked.txt"
    untracked.write_bytes(b"untracked bytes\n")
    subprocess.run(["git", "add", "unstaged.txt"], cwd=tmp_vault, check=True)
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
    (tmp_vault / bibliography.BIB_PATH).write_bytes(
        b'[{"title":"Mortality decline","id":"smith2020"}]\n'
    )
    status_before = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout

    assert bibliography.commit_autoexport(tmp_vault) is True

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
    assert unstaged.read_bytes() == b"unstaged bytes\n"
    assert untracked.read_bytes() == b"untracked bytes\n"
    status_after = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout
    unrelated_before = [
        line for line in status_before.splitlines() if not line.endswith(b" x/")
    ]
    assert status_after.splitlines() == unrelated_before


def test_commit_autoexport_uses_exact_no_verify_target_only_commit(
    tmp_vault, monkeypatch
):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_text("[]")
    calls = []
    real_run = subprocess.run

    def recording_run(command, *args, **kwargs):
        calls.append(command)
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(bibliography.subprocess, "run", recording_run)

    assert bibliography.commit_autoexport(tmp_vault) is True
    assert [
        "git",
        "commit",
        "-q",
        "--no-verify",
        "--only",
        "-m",
        "chore: bibliography export",
        "--",
        bibliography.BIB_PATH,
    ] in calls


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
        if path == target:
            raise PermissionError("denied")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(bibliography.os, "open", fail_target)
    observed = _observe(tmp_vault, StubClient(ITEMS), FakeClock())

    assert observed.result is Result.UNREACHABLE
    assert observed.staleness is Result.UNREACHABLE


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
        if path == target:
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

    observed = _observe(tmp_vault, StubClient(ITEMS), FakeClock(), settle_seconds=0)

    assert observed.result is Result.UNMATCHED
    assert observed.staleness is Result.UNMATCHED


def test_observe_checks_committed_head_after_target_races_back_to_match(
    tmp_vault, monkeypatch
):
    target = tmp_vault / bibliography.BIB_PATH
    target.write_text(json.dumps(ITEMS))
    original_commit = bibliography.commit_autoexport

    def raced_commit(vault):
        target.write_text('[{"id":"raced","title":"Raced"}]')
        committed = original_commit(vault)
        target.write_text(json.dumps(ITEMS))
        return committed

    monkeypatch.setattr(bibliography, "commit_autoexport", raced_commit)

    observed = _observe(tmp_vault, StubClient(ITEMS), FakeClock())

    assert observed.result is Result.UNMATCHED
    assert observed.staleness is Result.MATCHED
    committed = subprocess.run(
        ["git", "show", f"HEAD:{bibliography.BIB_PATH}"],
        cwd=tmp_vault,
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    assert json.loads(committed)[0]["id"] == "raced"
