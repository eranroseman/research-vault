"""The live drill's shared vault-provisioning helper.

`research_vault` never registers a Better BibTeX auto-export; that was the
now-retired doctor probe's whole point, and no replacement watches for one.
This module keeps the throwaway-vault-under-a-synthetic-Git-identity helper
that other live drills build on.
"""

import json
import subprocess
from pathlib import Path

from research_vault import scaffold

DRILL_USER_NAME = "research-vault-live-drill"
DRILL_USER_EMAIL = "live-drill@example.invalid"


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
    (vault / ".research-vault" / "machine.json").write_text(
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
