import argparse
import json
import subprocess

import pytest

from research_vault import Result, scaffold
from research_vault.zotero import ZoteroError

PROBE_NAMES = [
    "tree",
    "machine-config",
    "zotero",
    "bbt",
    "remote",
    "backup",
]
HARD_UNMATCHED = ["tree", "machine-config", "bbt"]
HARD_UNREACHABLE = ["zotero", "bbt"]
WARN_ONLY = ["remote", "backup"]


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


def test_doctor_returns_exact_six_tuple_probes_and_repairs_tree(tmp_vault):
    vault = _doctor_vault(tmp_vault)
    (vault / "projects").rmdir()

    probes = scaffold.doctor(vault, client=ReadyClient())

    assert [probe.check for probe in probes] == PROBE_NAMES
    assert all(isinstance(probe, tuple) and len(probe) == 3 for probe in probes)
    assert (vault / "projects").is_dir()
    assert probes[0].result is Result.MATCHED
    assert "9.0.6" in probes[2].reason
    assert "9.0.55" in probes[2].reason


def test_doctor_ready_failure_short_circuits_bbt_but_keeps_all_probes(tmp_vault):
    vault = _doctor_vault(tmp_vault)

    class DownClient:
        def ready(self):
            raise ZoteroError("connection refused")

    probes = scaffold.doctor(vault, client=DownClient())
    by_check = {probe.check: probe for probe in probes}

    assert [probe.check for probe in probes] == PROBE_NAMES
    assert by_check["zotero"].result is Result.UNREACHABLE
    assert by_check["bbt"].result is Result.UNREACHABLE
    assert by_check["bbt"].reason == "zotero down"
    assert [probe.check for probe in probes[-2:]] == [
        "remote",
        "backup",
    ]


def test_doctor_missing_bbt_reports_unmatched(tmp_vault):
    vault = _doctor_vault(tmp_vault)

    probes = scaffold.doctor(vault, client=ReadyClient({"zotero": "9.0.6"}))
    by_check = {probe.check: probe for probe in probes}

    assert by_check["bbt"].result is Result.UNMATCHED


def test_doctor_treats_whitespace_bbt_version_as_missing(tmp_vault):
    vault = _doctor_vault(tmp_vault)

    probes = scaffold.doctor(
        vault,
        client=ReadyClient({"zotero": "9.0.6", "betterbibtex": "  "}),
    )

    assert {probe.check: probe.result for probe in probes}["bbt"] is Result.UNMATCHED


def test_doctor_scaffold_failure_still_returns_all_six_probes(tmp_path, monkeypatch):
    vault = tmp_path / "missing-vault"
    monkeypatch.setattr(
        scaffold,
        "scaffold_vault",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("cannot create")),
    )

    probes = scaffold.doctor(vault, client=ReadyClient({"zotero": "9.0.6"}))

    assert [probe.check for probe in probes] == PROBE_NAMES
    assert probes[0].result is Result.UNMATCHED


def test_doctor_classifies_machine_remote_and_backup_conditions(tmp_vault):
    vault = _doctor_vault(tmp_vault, backup="")
    subprocess.run(["git", "remote", "remove", "origin"], cwd=vault, check=True)
    (vault / ".research-vault" / "machine.json").write_text(
        '{"mailto":"you@example.edu","zotero_backup":""}'
    )

    probes = scaffold.doctor(vault, client=ReadyClient())
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
    assert len(capsys.readouterr().out.splitlines()) == 6
