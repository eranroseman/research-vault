"""The live observation drill: doctor against real Zotero/BBT, registration-free.

The harness never registers an auto-export; a person creates the whole-library
Better CSL JSON auto-export in BBT Preferences. The drill therefore observes an
absent auto-export against a throwaway vault. The MATCHED end-to-end leg —
genuine BBT output observed, one real item imported, rerun to NOOP — is
deferred by author decision 2026-08-20 because no human-created auto-export
points at a throwaway vault.

`HARNESS_LIVE=1` alone means "run everything that can honestly run on this
machine". The end-to-end legs that need genuine BBT output — the import and
staleness legs in `test_cli_live.py` — additionally read
`HARNESS_LIVE_AUTOEXPORT_VAULT`, the absolute path of a vault a person has
already pointed a whole-library Better CSL JSON auto-export at in BBT
Preferences. Unset, those legs skip aloud naming that human step; they never
fabricate the export, and the harness still writes nothing to it.
"""

import argparse
import json
import subprocess
from pathlib import Path

import pytest

import harness_core.__main__ as cli
from harness_core import Result, bibliography, paths, scaffold
from harness_core.zotero import ZoteroClient

REPO = Path(__file__).resolve().parents[2]
DRILL_USER_NAME = "knowledge-harness-live-drill"
DRILL_USER_EMAIL = "live-drill@example.invalid"
SETTLE_SECONDS = 2


def test_environment_records_the_live_probed_bbt_autoexport_facts():
    """Losing the falsified-registration record that justifies this drill must fail."""
    environment = (REPO / "docs" / "environment.md").read_text(encoding="utf-8")

    assert (
        "BBT 9.0.55 JSON-RPC exposes `autoexport.add` only; "
        "`.list`/`.remove`/`.delete`/`.get` live-probed `-32601 METHOD_NOT_FOUND`; "
        "`add` is collection-scoped by implementation (source-verified). "
        "| 2026-08-20 |"
    ) in environment
    assert (
        '`autoexport.add("//", …)` fails 404 `path is too short` before registration '
        "storage: no entry is created, so whole-library registration is impossible "
        "through the public RPC."
    ) in environment
    assert (
        "BBT persists auto-exports as profile preference keys "
        "`better-bibtex.autoExport.<encoded-path>`. Human-debugging fact only: doctor "
        "detection stays behavioral (target presence plus staleness) and never "
        "scrapes preferences. | 2026-08-20 |"
    ) in environment
    assert (
        "The retained drill vault was removed through the drill's own "
        "confirmed-cleanup path"
    ) in environment
    assert (
        "the sibling audit state is stamped `cleanup-confirmed`. | 2026-08-21 |"
        in environment
    )


class RecordingClient(ZoteroClient):
    """A real Zotero/BBT client that records every JSON-RPC method it sends."""

    def __init__(self):
        super().__init__()
        self.rpc_methods: list[str] = []

    def _rpc(self, method, params):
        self.rpc_methods.append(method)
        return super()._rpc(method, params)


def _drill_vault(tmp_path: Path) -> Path:
    """Return a throwaway scaffolded vault bound to a local synthetic identity."""
    vault = tmp_path / "live-drill-vault"
    vault.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=vault, check=True, capture_output=True)
    for key, value in (
        ("user.name", DRILL_USER_NAME),
        ("user.email", DRILL_USER_EMAIL),
    ):
        subprocess.run(
            ["git", "config", "--local", key, value],
            cwd=vault,
            check=True,
            capture_output=True,
        )
    scaffold.scaffold_vault(vault)
    (vault / ".harness" / "machine.json").write_text(
        json.dumps(
            {
                "mailto": DRILL_USER_EMAIL,
                "zotero_backup": "temporary live drill; no evidence stored",
            }
        )
    )
    return vault


def test_drill_vault_commits_under_the_synthetic_local_identity(tmp_path):
    """Letting the drill borrow or change the operator's Git identity must fail."""
    vault = _drill_vault(tmp_path)

    author = subprocess.run(
        ["git", "log", "-1", "--format=%an <%ae>"],
        cwd=vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    global_identity = subprocess.run(
        ["git", "config", "--global", "--get-regexp", r"^user\."],
        check=False,
        capture_output=True,
        text=True,
    ).stdout

    assert author == f"{DRILL_USER_NAME} <{DRILL_USER_EMAIL}>"
    assert DRILL_USER_EMAIL not in global_identity


@pytest.mark.live
def test_live_doctor_reports_the_absent_human_created_auto_export(
    tmp_path, monkeypatch, capsys
):
    """Silently passing, registering, or writing the target must fail."""
    vault = _drill_vault(tmp_path)
    target = vault / bibliography.BIB_PATH
    host_target = paths.to_bbt_host(target)
    client = RecordingClient()

    probes = {
        probe.check: probe
        for probe in scaffold.doctor(vault, client, settle_seconds=SETTLE_SECONDS)
    }

    assert probes["tree"].result is Result.MATCHED
    assert probes["machine-config"].result is Result.MATCHED
    assert probes["zotero"].result is Result.MATCHED
    assert "zotero=" in probes["zotero"].detail
    assert probes["bbt"].result is Result.MATCHED
    assert f"betterbibtex={probes['bbt'].detail}" in probes["zotero"].detail
    assert probes["autoexport"].result is Result.UNMATCHED
    assert host_target in probes["autoexport"].detail
    assert (
        "create or fix the whole-library Better CSL JSON auto-export in BBT Preferences"
        in probes["autoexport"].detail
    )
    assert not target.exists()
    assert [method for method in client.rpc_methods if "autoexport" in method] == []

    monkeypatch.setattr(cli, "ZoteroClient", lambda base: client)
    code = cli.cmd_doctor(
        argparse.Namespace(vault=str(vault), base="http://localhost:23119")
    )
    printed = capsys.readouterr()

    assert code == 1
    assert printed.err == ""
    lines = printed.out.splitlines()
    assert [
        line
        for line in lines
        if line.startswith("UNMATCHED autoexport")
        and host_target in line
        and "BBT Preferences" in line
    ]
    assert [
        line for line in lines if line.startswith("warn:") and " staleness " in line
    ]
    assert not target.exists()
    assert [method for method in client.rpc_methods if "autoexport" in method] == []
