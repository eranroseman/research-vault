import json
import subprocess
import sys
from pathlib import Path

import pytest

PROVISIONED_VAULT_ENV = "RV_LIVE_AUTOEXPORT_VAULT"

DEFERRAL_REASON = (
    "deferred: research-vault never registers an auto-export, so no BBT output "
    "reaches a throwaway vault. Set "
    f"{PROVISIONED_VAULT_ENV} to the absolute path of a vault after a person "
    "creates the whole-library Better CSL JSON auto-export in BBT Preferences "
    "targeting that vault's system/bibliography.json."
)


def _provisioned_vault_or_defer(environ):
    """Return the human-provisioned vault, or defer aloud naming the human step."""
    configured = environ.get(PROVISIONED_VAULT_ENV, "").strip()
    if not configured:
        pytest.skip(DEFERRAL_REASON)
    vault = Path(configured)
    if not vault.is_absolute() or not vault.is_dir():
        pytest.fail(
            f"{PROVISIONED_VAULT_ENV} must name an existing vault by absolute "
            f"path; got {configured!r}"
        )
    return vault


def test_end_to_end_legs_defer_aloud_until_a_person_provisions_a_vault():
    """Deferring the falsified-contract legs silently must fail."""
    with pytest.raises(pytest.skip.Exception) as deferred:
        _provisioned_vault_or_defer({})

    reason = str(deferred.value)
    assert PROVISIONED_VAULT_ENV in reason
    assert "whole-library Better CSL JSON auto-export in BBT Preferences" in reason
    assert "system/bibliography.json" in reason


def test_provisioned_vault_opt_in_rejects_a_path_that_is_not_a_vault(tmp_path):
    """Letting a mistyped opt-in quietly skip the end-to-end legs must fail."""
    with pytest.raises(pytest.fail.Exception, match=PROVISIONED_VAULT_ENV):
        _provisioned_vault_or_defer({PROVISIONED_VAULT_ENV: str(tmp_path / "absent")})


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
    info = json.loads(proc.stdout)
    assert "betterbibtex" in info


def test_probe_unreachable():
    proc = run_cli("probe", "--base", "http://127.0.0.1:1")
    assert proc.returncode == 3
    assert json.loads(proc.stdout)["result"] == "UNREACHABLE"


def test_base_option_works_before_and_after_subcommand(monkeypatch, capsys):
    import research_vault.__main__ as cli

    bases = []

    class FakeClient:
        def __init__(self, base):
            bases.append(base)

        def ready(self):
            return {"zotero": "9.0.6", "betterbibtex": "9.0.55"}

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)

    assert cli.main(["--base", "http://before.invalid", "probe"]) == 0
    assert cli.main(["probe", "--base", "http://after.invalid"]) == 0

    assert bases == ["http://before.invalid", "http://after.invalid"]
    assert len(capsys.readouterr().out.splitlines()) == 2
