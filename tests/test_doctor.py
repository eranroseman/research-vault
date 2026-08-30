import argparse
import json
import subprocess

import pytest

from research_vault import Result, bibliography, scaffold
from research_vault.zotero import ZoteroError

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
    "okf",
]
HARD_UNMATCHED = ["tree", "machine-config", "bbt", "autoexport"]
HARD_UNREACHABLE = ["zotero", "bbt", "autoexport"]
WARN_ONLY = ["staleness", "remote", "backup", "inbox", "okf"]


def _probes(**states):
    return [
        (name, states.get(name, Result.MATCHED), f"{name} detail")
        for name in PROBE_NAMES
    ]


def _run_cmd(monkeypatch, capsys, probes):
    import research_vault.__main__ as cli

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
    rv_dir = tmp_vault / ".research-vault"
    rv_dir.mkdir(exist_ok=True)
    (rv_dir / "machine.json").write_text(
        json.dumps({"mailto": "researcher@example.edu", "zotero_backup": backup})
    )
    subprocess.run(
        ["git", "remote", "add", "origin", "https://example.invalid/vault.git"],
        cwd=tmp_vault,
        check=True,
    )
    return tmp_vault


def test_doctor_returns_exact_ten_tuple_probes_and_repairs_tree(tmp_vault, monkeypatch):
    vault = _doctor_vault(tmp_vault)
    (vault / "projects").rmdir()
    observed = bibliography.AutoexportObservation(
        Result.MATCHED, "genuine BBT output", Result.MATCHED, "current"
    )
    monkeypatch.setattr(
        scaffold.bibliography, "observe_autoexport", lambda *a, **k: observed
    )

    probes = scaffold.doctor(vault, client=ReadyClient(), settle_seconds=0)

    assert [probe.check for probe in probes] == PROBE_NAMES
    assert all(isinstance(probe, tuple) and len(probe) == 3 for probe in probes)
    assert (vault / "projects").is_dir()
    assert probes[0].result is Result.MATCHED
    assert "9.0.6" in probes[2].reason
    assert "9.0.55" in probes[2].reason


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
    by_check = {probe.check: probe for probe in probes}

    assert [probe.check for probe in probes] == PROBE_NAMES
    assert by_check["zotero"].result is Result.UNREACHABLE
    for name in ("bbt", "autoexport", "staleness"):
        assert by_check[name].result is Result.UNREACHABLE
        assert by_check[name].reason == "zotero down"
    assert [probe.check for probe in probes[-4:]] == [
        "remote",
        "backup",
        "inbox",
        "okf",
    ]


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
    by_check = {probe.check: probe for probe in probes}

    assert by_check["bbt"].result is Result.UNMATCHED
    for name in ("autoexport", "staleness"):
        assert by_check[name].result is Result.SKIPPED
        assert "Better BibTeX" in by_check[name].reason
        assert "prerequisite" in by_check[name].reason


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

    assert {probe.check: probe.result for probe in probes}["bbt"] is Result.UNMATCHED


def test_doctor_scaffold_failure_still_returns_all_ten_probes(tmp_path, monkeypatch):
    vault = tmp_path / "missing-vault"
    monkeypatch.setattr(
        scaffold,
        "scaffold_vault",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("cannot create")),
    )

    probes = scaffold.doctor(
        vault, client=ReadyClient({"zotero": "9.0.6"}), settle_seconds=0
    )

    assert [probe.check for probe in probes] == PROBE_NAMES
    assert probes[0].result is Result.UNMATCHED


def _observed_probes(vault, monkeypatch, result, detail):
    calls = []
    observed = bibliography.AutoexportObservation(
        result, detail, Result.UNMATCHED, "cached stale detail"
    )

    def observe(*args, **kwargs):
        calls.append((args, kwargs))
        return observed

    monkeypatch.setattr(scaffold.bibliography, "observe_autoexport", observe)
    probes = scaffold.doctor(vault, client=ReadyClient(), settle_seconds=0)
    assert len(calls) == 1
    return {probe.check: probe for probe in probes}


def test_doctor_reports_an_unreachable_observation_verbatim_with_cached_staleness(
    tmp_vault, monkeypatch
):
    """Dressing a Zotero outage up as repair guidance must fail."""
    vault = _doctor_vault(tmp_vault)

    by_check = _observed_probes(
        vault, monkeypatch, Result.UNREACHABLE, "raw BBT detail"
    )

    assert (by_check["autoexport"].result, by_check["autoexport"].reason) == (
        Result.UNREACHABLE,
        "raw BBT detail",
    )
    assert (by_check["staleness"].result, by_check["staleness"].reason) == (
        Result.UNMATCHED,
        "cached stale detail",
    )


def test_doctor_reports_an_unmatched_observation_verbatim_with_cached_staleness(
    tmp_vault, monkeypatch
):
    """Re-composing or dropping the observer's repair guidance must fail."""
    vault = _doctor_vault(tmp_vault)
    detail = (
        "bibliography auto-export absent; a person must create or fix the "
        "whole-library Better CSL JSON auto-export in BBT Preferences with "
        "target C:\\live\\x\\bibliography.json"
    )

    by_check = _observed_probes(vault, monkeypatch, Result.UNMATCHED, detail)

    assert (by_check["autoexport"].result, by_check["autoexport"].reason) == (
        Result.UNMATCHED,
        detail,
    )
    assert (by_check["staleness"].result, by_check["staleness"].reason) == (
        Result.UNMATCHED,
        "cached stale detail",
    )
    assert by_check["tree"].result is Result.MATCHED
    assert (by_check["remote"].result, by_check["remote"].reason) == (
        Result.MATCHED,
        "origin",
    )


def test_doctor_probe_five_carries_the_observer_repair_guidance(tmp_vault, monkeypatch):
    """Leaving doctor's autoexport probe without the BBT Preferences repair fails."""
    vault = _doctor_vault(tmp_vault)
    monkeypatch.setattr(bibliography.paths, "_running_in_wsl", lambda: False)

    class ExportingClient(ReadyClient):
        def export_csl(self, citekeys):
            assert citekeys is None
            return [{"id": "smith2020", "title": "Mortality decline"}]

    probes = {
        probe.check: probe
        for probe in scaffold.doctor(vault, ExportingClient(), settle_seconds=0)
    }

    assert probes["tree"].result is Result.MATCHED
    assert probes["autoexport"].result is Result.UNMATCHED
    assert probes["autoexport"].reason == (
        "bibliography auto-export absent; a person must create or fix the "
        "whole-library Better CSL JSON auto-export in BBT Preferences with "
        f"target {vault / bibliography.BIB_PATH}"
    )
    assert (probes["staleness"].result, probes["staleness"].reason) == (
        Result.UNMATCHED,
        "bibliography auto-export absent",
    )
    assert not (vault / bibliography.BIB_PATH).exists()


def test_cmd_doctor_post_commit_git_read_oserror_exits_three_without_traceback(
    tmp_vault, monkeypatch, capsys
):
    import research_vault.__main__ as cli

    vault = _doctor_vault(tmp_vault)
    items = [{"id": "smith2020", "title": "Mortality decline"}]
    (vault / bibliography.BIB_PATH).write_text(json.dumps(items))

    class ObservedClient(ReadyClient):
        def export_csl(self, citekeys):
            assert citekeys is None
            return items

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
    assert len(lines) == 10
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
    import research_vault.__main__ as cli

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
    assert len(lines) == 10
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
    (vault / ".research-vault" / "machine.json").write_text(
        '{"mailto":"you@example.edu","zotero_backup":""}'
    )
    (vault / "inbox" / "review-queue.md").write_text(
        '---\ntype: "review-queue"\n---\n'
        "- [id:: citekey/kind-10:identifier;target-1:x/2026-08-01] [check:: citekey] [target:: x] "
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
    by_check = {probe.check: probe for probe in probes}

    assert by_check["machine-config"].result is Result.UNMATCHED
    assert by_check["remote"] == scaffold.Probe(
        "remote",
        Result.UNMATCHED,
        "no remote — vault endures only on this disk (§2)",
    )
    assert by_check["backup"] == scaffold.Probe(
        "backup",
        Result.UNMATCHED,
        "no stated Zotero storage backup (§2 boundary)",
    )
    assert by_check["inbox"].result is Result.UNMATCHED
    assert "1" in by_check["inbox"].reason
    assert "2026-08-01" in by_check["inbox"].reason


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
    import research_vault.__main__ as cli

    bases = []

    class FakeClient:
        def __init__(self, base):
            bases.append(base)

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    monkeypatch.setattr(cli, "doctor", lambda vault, client: _probes())

    assert cli.main(argv) == 0
    assert bases == [expected]
    assert len(capsys.readouterr().out.splitlines()) == 10
