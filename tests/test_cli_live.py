import json
import subprocess
import sys

import pytest


def run_cli(*args):
    # check=False: callers assert on returncode, and a nonzero exit is a normal
    # expected outcome for the refusal tests, not a research-vault failure.
    return subprocess.run(
        [sys.executable, "-m", "research_vault", *args],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.live
def test_probe():
    proc = run_cli("probe")
    assert proc.returncode == 0
    report = json.loads(proc.stdout)
    assert set(report) == {"server", "bbt"}
    assert set(report["server"]) == {"zotero", "api", "schema", "server_id"}
    assert len(report["server"]["server_id"]) == 12
    assert "betterbibtex" in report["bbt"]


def test_probe_unreachable(dead_base):
    proc = run_cli("probe", "--base", dead_base)
    assert proc.returncode == 3
    report = json.loads(proc.stdout)
    assert report["result"] == "UNREACHABLE"
    assert "server" not in report
    assert report["detail"]


def test_base_option_works_before_and_after_subcommand(monkeypatch, capsys):
    import research_vault.__main__ as cli

    bases = []

    class FakeClient:
        def __init__(self, base):
            bases.append(base)

        def server_info(self):
            return {
                "zotero": "10.0.1",
                "api": "3",
                "schema": "44",
                "server_id": "6LpvURP2E933",
            }

        def ready(self):
            return {"zotero": "10.0.1", "betterbibtex": "9.0.63"}

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)

    assert cli.main(["--base", "http://before.invalid", "probe"]) == 0
    assert cli.main(["probe", "--base", "http://after.invalid"]) == 0

    assert bases == ["http://before.invalid", "http://after.invalid"]
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {
        "server": FakeClient("unused").server_info(),
        "bbt": {"zotero": "10.0.1", "betterbibtex": "9.0.63"},
    }


def test_probe_unreachable_in_process_is_exit_3(dead_base, capsys):
    """The same refusal the subprocess test measures, reached through
    `main()` so the exit code is pinned in-process too."""
    import research_vault.__main__ as cli

    assert cli.main(["probe", "--base", dead_base]) == 3
    report = json.loads(capsys.readouterr().out)
    assert report["result"] == "UNREACHABLE"
    assert set(report) == {"result", "detail"}
    assert "127.0.0.1" in report["detail"]
