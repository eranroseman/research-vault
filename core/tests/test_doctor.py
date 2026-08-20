import argparse
import json
import subprocess

import pytest

from harness_core import Result, bibliography, scaffold
from harness_core.zotero import ZoteroError

PROBE_NAMES = [
    "tree",
    "machine-config",
    "zotero",
    "bbt",
    "autoexport",
    "staleness",
    "remote",
    "backup",
    "inbox",
]
HARD_UNMATCHED = ["tree", "machine-config", "bbt", "autoexport"]
HARD_UNREACHABLE = ["zotero", "bbt", "autoexport"]
WARN_ONLY = ["staleness", "remote", "backup", "inbox"]


def _probes(**states):
    return [
        (name, states.get(name, Result.MATCHED), f"{name} detail")
        for name in PROBE_NAMES
    ]


def _run_cmd(monkeypatch, capsys, probes):
    import harness_core.__main__ as cli

    monkeypatch.setattr(cli, "doctor", lambda *args, **kwargs: probes)
    code = cli.cmd_doctor(argparse.Namespace(vault="/unused", base="http://unused"))
    return code, capsys.readouterr()


def test_cmd_doctor_all_matched_exits_zero_and_prints_in_order(monkeypatch, capsys):
    code, captured = _run_cmd(monkeypatch, capsys, _probes())

    assert code == 0
    assert [line.split()[1] for line in captured.out.splitlines()] == PROBE_NAMES


@pytest.mark.parametrize("name", HARD_UNMATCHED)
def test_cmd_doctor_each_hard_unmatched_exits_one(name, monkeypatch, capsys):
    code, captured = _run_cmd(monkeypatch, capsys, _probes(**{name: Result.UNMATCHED}))

    assert code == 1
    assert f"UNMATCHED {name}" in captured.out


@pytest.mark.parametrize("name", HARD_UNREACHABLE)
def test_cmd_doctor_each_hard_unreachable_exits_three(name, monkeypatch, capsys):
    code, captured = _run_cmd(
        monkeypatch, capsys, _probes(**{name: Result.UNREACHABLE})
    )

    assert code == 3
    assert f"UNREACHABLE {name}" in captured.out


@pytest.mark.parametrize("name", WARN_ONLY)
@pytest.mark.parametrize("state", [Result.UNMATCHED, Result.UNREACHABLE])
def test_cmd_doctor_warn_only_failures_exit_zero_and_print_warn_prefix(
    name, state, monkeypatch, capsys
):
    code, captured = _run_cmd(monkeypatch, capsys, _probes(**{name: state}))

    assert code == 0
    line = next(line for line in captured.out.splitlines() if f" {name} " in line)
    assert line.startswith(f"warn:{state.value} {name}")


def test_cmd_doctor_hard_unmatched_wins_over_hard_unreachable(monkeypatch, capsys):
    code, _ = _run_cmd(
        monkeypatch,
        capsys,
        _probes(tree=Result.UNMATCHED, zotero=Result.UNREACHABLE),
    )
    assert code == 1


class ReadyClient:
    def __init__(self, ready=None):
        self.info = ready or {"zotero": "9.0.6", "betterbibtex": "9.0.55"}

    def ready(self):
        return self.info


def _doctor_vault(tmp_vault, *, backup="/backup"):
    for relative in scaffold.VAULT_DIRS:
        (tmp_vault / relative).mkdir(parents=True, exist_ok=True)
    harness = tmp_vault / ".harness"
    harness.mkdir(exist_ok=True)
    (harness / "machine.json").write_text(
        json.dumps({"mailto": "researcher@example.edu", "zotero_backup": backup})
    )
    subprocess.run(
        ["git", "remote", "add", "origin", "https://example.invalid/vault.git"],
        cwd=tmp_vault,
        check=True,
    )
    return tmp_vault


def test_doctor_returns_exact_nine_tuple_probes_and_repairs_tree(
    tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault)
    (vault / "projects").rmdir()
    observed = bibliography.AutoexportObservation(
        Result.MATCHED, "genuine BBT output", Result.MATCHED, "current"
    )
    monkeypatch.setattr(
        scaffold.bibliography, "observe_autoexport", lambda *a, **k: observed
    )

    probes = scaffold.doctor(vault, client=ReadyClient(), settle_seconds=0)

    assert [probe.name for probe in probes] == PROBE_NAMES
    assert all(isinstance(probe, tuple) and len(probe) == 3 for probe in probes)
    assert (vault / "projects").is_dir()
    assert probes[0].result is Result.MATCHED
    assert "9.0.6" in probes[2].detail
    assert "9.0.55" in probes[2].detail


def test_doctor_ready_failure_short_circuits_bbt_observation_but_keeps_all_probes(
    tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault)

    class DownClient:
        def ready(self):
            raise ZoteroError("connection refused")

    monkeypatch.setattr(
        scaffold.bibliography,
        "observe_autoexport",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not observe")),
    )

    probes = scaffold.doctor(vault, client=DownClient(), settle_seconds=0)
    by_name = {probe.name: probe for probe in probes}

    assert [probe.name for probe in probes] == PROBE_NAMES
    assert by_name["zotero"].result is Result.UNREACHABLE
    for name in ("bbt", "autoexport", "staleness"):
        assert by_name[name].result is Result.UNREACHABLE
        assert by_name[name].detail == "zotero down"
    assert [probe.name for probe in probes[-3:]] == ["remote", "backup", "inbox"]


def test_doctor_missing_bbt_skips_observation_with_prerequisite_detail(
    tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault)
    monkeypatch.setattr(
        scaffold.bibliography,
        "observe_autoexport",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not observe")),
    )

    probes = scaffold.doctor(
        vault, client=ReadyClient({"zotero": "9.0.6"}), settle_seconds=0
    )
    by_name = {probe.name: probe for probe in probes}

    assert by_name["bbt"].result is Result.UNMATCHED
    for name in ("autoexport", "staleness"):
        assert by_name[name].result is Result.SKIPPED
        assert "Better BibTeX" in by_name[name].detail
        assert "prerequisite" in by_name[name].detail


def test_doctor_treats_whitespace_bbt_version_as_missing(tmp_vault, monkeypatch):
    vault = _doctor_vault(tmp_vault)
    monkeypatch.setattr(
        scaffold.bibliography,
        "observe_autoexport",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not observe")),
    )

    probes = scaffold.doctor(
        vault,
        client=ReadyClient({"zotero": "9.0.6", "betterbibtex": "  "}),
        settle_seconds=0,
    )

    assert {probe.name: probe.result for probe in probes}["bbt"] is Result.UNMATCHED


def test_doctor_scaffold_failure_still_returns_all_nine_probes(tmp_path, monkeypatch):
    vault = tmp_path / "missing-vault"
    monkeypatch.setattr(
        scaffold,
        "scaffold_vault",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("cannot create")),
    )

    probes = scaffold.doctor(
        vault, client=ReadyClient({"zotero": "9.0.6"}), settle_seconds=0
    )

    assert [probe.name for probe in probes] == PROBE_NAMES
    assert probes[0].result is Result.UNMATCHED


@pytest.mark.parametrize("result", [Result.UNMATCHED, Result.UNREACHABLE])
def test_doctor_reports_shared_observation_and_cached_staleness(
    tmp_vault, monkeypatch, result
):
    vault = _doctor_vault(tmp_vault)
    calls = []
    observed = bibliography.AutoexportObservation(
        result, "raw BBT detail", Result.UNMATCHED, "cached stale detail"
    )

    def observe(*args, **kwargs):
        calls.append((args, kwargs))
        return observed

    monkeypatch.setattr(scaffold.bibliography, "observe_autoexport", observe)
    probes = scaffold.doctor(vault, client=ReadyClient(), settle_seconds=0)
    by_name = {probe.name: probe for probe in probes}

    assert len(calls) == 1
    assert (by_name["autoexport"].result, by_name["autoexport"].detail) == (
        result,
        "raw BBT detail",
    )
    assert (by_name["staleness"].result, by_name["staleness"].detail) == (
        Result.UNMATCHED,
        "cached stale detail",
    )


def test_cmd_doctor_post_commit_git_read_oserror_exits_three_without_traceback(
    tmp_vault, monkeypatch, capsys
):
    import harness_core.__main__ as cli

    vault = _doctor_vault(tmp_vault)
    items = [{"id": "smith2020", "title": "Mortality decline"}]
    (vault / bibliography.BIB_PATH).write_text(json.dumps(items))

    class ObservedClient(ReadyClient):
        def export_csl(self, citekeys):
            assert citekeys is None
            return items

        def register_autoexport(self, registered_target):
            raise AssertionError("matching target must not be registered again")

    real_run = bibliography.subprocess.run

    def fail_post_commit_read(command, *args, **kwargs):
        if command == ["git", "show", f"HEAD:{bibliography.BIB_PATH}"]:
            raise OSError("git unavailable")
        return real_run(command, *args, **kwargs)

    client = ObservedClient()
    monkeypatch.setattr(cli, "ZoteroClient", lambda base: client)
    monkeypatch.setattr(bibliography.subprocess, "run", fail_post_commit_read)

    code = cli.cmd_doctor(argparse.Namespace(vault=str(vault), base="http://unused"))

    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert code == 3
    assert len(lines) == 9
    assert [line.split()[1] for line in lines] == PROBE_NAMES
    assert any(
        line.startswith("UNREACHABLE autoexport") and "git unavailable" in line
        for line in lines
    )
    assert any(line.startswith("MATCHED staleness") for line in lines)
    assert captured.err == ""


def test_cmd_doctor_target_read_oserror_exits_three_without_traceback(
    tmp_vault, monkeypatch, capsys
):
    import harness_core.__main__ as cli

    vault = _doctor_vault(tmp_vault)
    items = [{"id": "smith2020", "title": "Mortality decline"}]
    (vault / bibliography.BIB_PATH).write_text(json.dumps(items))

    class ObservedClient(ReadyClient):
        def export_csl(self, citekeys):
            assert citekeys is None
            return items

    client = ObservedClient()
    monkeypatch.setattr(cli, "ZoteroClient", lambda base: client)
    monkeypatch.setattr(
        bibliography.os,
        "fdopen",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("target read denied")),
    )

    code = cli.cmd_doctor(argparse.Namespace(vault=str(vault), base="http://unused"))

    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert code == 3
    assert len(lines) == 9
    assert [line.split()[1] for line in lines] == PROBE_NAMES
    assert any(
        line.startswith("UNREACHABLE autoexport") and "target read denied" in line
        for line in lines
    )
    assert captured.err == ""


def test_doctor_classifies_machine_remote_backup_and_inbox_conditions(
    tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault, backup="")
    subprocess.run(["git", "remote", "remove", "origin"], cwd=vault, check=True)
    (vault / ".harness" / "machine.json").write_text(
        '{"mailto":"you@example.edu","zotero_backup":""}'
    )
    (vault / "inbox" / "review-queue.md").write_text(
        '---\ntype: "review-inbox"\n---\n'
        "- [id:: citekey/x/2026-08-01] [check:: citekey] [target:: x] "
        "[result:: UNMATCHED] [date:: 2026-08-01] [actor:: process:test] "
        "[reason:: mismatch — test]\n"
    )
    monkeypatch.setattr(
        scaffold.bibliography,
        "observe_autoexport",
        lambda *a, **k: bibliography.AutoexportObservation(
            Result.MATCHED, "ok", Result.MATCHED, "ok"
        ),
    )

    probes = scaffold.doctor(vault, client=ReadyClient(), settle_seconds=0)
    by_name = {probe.name: probe for probe in probes}

    assert by_name["machine-config"].result is Result.UNMATCHED
    assert by_name["remote"] == scaffold.Probe(
        "remote",
        Result.UNMATCHED,
        "no remote — vault endures only on this disk (§2)",
    )
    assert by_name["backup"] == scaffold.Probe(
        "backup",
        Result.UNMATCHED,
        "no stated Zotero storage backup (§2 boundary)",
    )
    assert by_name["inbox"].result is Result.UNMATCHED
    assert "1" in by_name["inbox"].detail
    assert "2026-08-01" in by_name["inbox"].detail


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["doctor", "--base", "http://after", "--vault", "/vault"], "http://after"),
        (["--base", "http://before", "doctor", "--vault", "/vault"], "http://before"),
    ],
)
def test_doctor_base_routes_before_and_after_subcommand(
    argv, expected, monkeypatch, capsys
):
    import harness_core.__main__ as cli

    bases = []

    class FakeClient:
        def __init__(self, base):
            bases.append(base)

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    monkeypatch.setattr(cli, "doctor", lambda vault, client: _probes())

    assert cli.main(argv) == 0
    assert bases == [expected]
    assert len(capsys.readouterr().out.splitlines()) == 9
