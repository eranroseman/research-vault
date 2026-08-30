import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "research_vault" / "templates" / "git" / "pre-commit"


def _git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _fake_python(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = bin_dir / "python3"
    script.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "-c" ]; then exit 0; fi\n'
        'printf "%s\\0" "$@" > "$ARGS_FILE"\n'
        'exit "${VERIFY_STATUS:-0}"\n'
    )
    script.chmod(0o755)
    return bin_dir


@pytest.mark.parametrize(("status", "expected"), [(0, 0), (1, 1), (3, 0), (2, 2)])
@pytest.mark.parametrize("unborn", [False, True])
def test_hook_resolves_one_verified_tree_and_invokes_exact_index_contract(
    tmp_path, status, expected, unborn
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    if not unborn:
        (repo / "base.md").write_text("base\n")
        _git(repo, "add", "base.md")
        _git(repo, "commit", "-qm", "base")
    hook = repo / "pre-commit"
    shutil.copy2(HOOK, hook)
    hook.chmod(0o755)
    args_file = tmp_path / "args"
    bin_dir = _fake_python(tmp_path)
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "ARGS_FILE": str(args_file),
        "VERIFY_STATUS": str(status),
    }

    completed = subprocess.run(
        [str(hook)], cwd=repo, env=env, capture_output=True, check=False
    )

    assert completed.returncode == expected
    argv = args_file.read_bytes().split(b"\0")[:-1]
    assert argv[:5] == [
        b"-m",
        b"research_vault",
        b"verify",
        b"--vault",
        os.fsencode(repo),
    ]
    assert argv[5:9] == [b"--offline", b"--surface", b"commit", b"--git-base"]
    base = argv[9].decode()
    assert argv[10:] == [b"--git-candidate", b"index"]
    assert _git(repo, "cat-file", "-e", f"{base}^{{tree}}") == ""
    if unborn:
        assert base == _git(repo, "hash-object", "-w", "-t", "tree", "/dev/null")
    else:
        assert base == _git(repo, "rev-parse", "HEAD")


def test_hook_documents_escape_hatch_and_replay_and_is_executable():
    text = HOOK.read_text()
    assert HOOK.stat().st_mode & os.X_OK
    subprocess.run(["sh", "-n", str(HOOK)], check=True)
    assert "git commit --no-verify" in text
    assert "CI replay" in text
