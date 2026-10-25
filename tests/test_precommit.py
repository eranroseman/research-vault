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
    """A python3 that answers the import probe, the fixer call and the verify
    call separately: the fixer prints FIXER_OUTPUT and exits FIXER_STATUS; the
    verify call records its argv and exits VERIFY_STATUS."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = bin_dir / "python3"
    script.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "-c" ]; then exit 0; fi\n'
        'if [ "$3" = "stamp-type" ]; then\n'
        '  printf "%s\\0" "$@" > "$FIXER_ARGS_FILE"\n'
        '  printf "%s" "${FIXER_OUTPUT:-}"\n'
        '  exit "${FIXER_STATUS:-0}"\n'
        "fi\n"
        'printf "%s\\0" "$@" > "$ARGS_FILE"\n'
        'exit "${VERIFY_STATUS:-0}"\n'
    )
    script.chmod(0o755)
    return bin_dir


@pytest.mark.parametrize(
    ("status", "expected"), [(0, 0), (1, 1), (3, 0), (2, 2), (4, 4)]
)
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
    fixer_args_file = tmp_path / "fixer-args"
    bin_dir = _fake_python(tmp_path)
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "ARGS_FILE": str(args_file),
        "FIXER_ARGS_FILE": str(fixer_args_file),
        "VERIFY_STATUS": str(status),
    }

    completed = subprocess.run(
        [str(hook)], cwd=repo, env=env, capture_output=True, check=False
    )

    assert completed.returncode == expected
    if status == 4:
        assert (
            b"pre-commit: the OKF reader's dependency is missing (PyYAML); refusing an unverified commit."
            in completed.stderr
        )
    fixer_argv = fixer_args_file.read_bytes().split(b"\0")[:-1]
    assert fixer_argv == [
        b"-m",
        b"research_vault",
        b"stamp-type",
        b"--vault",
        os.fsencode(repo),
        b"--staged",
    ]
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


@pytest.mark.parametrize(
    ("fixer_output", "fixer_status", "expected", "verify_ran"),
    [
        ("stamped daily/d.md\n", 0, 1, False),
        ("normalised projects/p/draft.md\nregenerated log.md\n", 0, 1, False),
        ("stamped daily/d.md\nnormalised daily/d.md\n", 0, 1, False),
        ("unfixed inbox/x.md\n", 0, 1, False),
        ("stamped daily/d.md\nunfixed inbox/x.md\n", 0, 1, False),
        (
            "skipped inbox/x.md — partially staged; stage the whole file or none of it\n",
            0,
            0,
            True,
        ),
        (
            "unresolved projects/p/draft.md — [[gone]] no file matches; resolve by hand\n",
            0,
            0,
            True,
        ),
        ("", 4, 4, False),
    ],
)
def test_hook_refuses_when_the_fixer_changed_a_file_and_never_stages(
    tmp_path, fixer_output, fixer_status, expected, verify_ran
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
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
        "FIXER_ARGS_FILE": str(tmp_path / "fixer-args"),
        "FIXER_OUTPUT": fixer_output,
        "FIXER_STATUS": str(fixer_status),
    }
    # Every path the fixer names exists untracked, and one other file is
    # staged: a hook that staged anything would change this listing.
    for path in ("daily/d.md", "projects/p/draft.md", "log.md", "inbox/x.md"):
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_text("changed by the fixer\n")
    (repo / "staged.md").write_text("staged\n")
    _git(repo, "add", "staged.md")
    staged_before = _git(repo, "diff", "--cached", "--name-only")
    completed = subprocess.run(
        [str(hook)], cwd=repo, env=env, capture_output=True, text=True, check=False
    )
    assert _git(repo, "diff", "--cached", "--name-only") == staged_before
    assert completed.returncode == expected
    assert args_file.exists() is verify_ran
    changed = any(
        line.startswith(("stamped ", "normalised ", "regenerated "))
        for line in fixer_output.splitlines()
    )
    if changed:
        for path in ("daily/d.md", "projects/p/draft.md", "log.md"):
            if path in fixer_output:
                # once each: a file both stamped and normalised is one re-stage
                assert completed.stderr.count(path) == 1, path
        assert (
            "stage them (or add them to the commit's `--` pathspec) and commit again"
            in completed.stderr
        )
    if "unfixed " in fixer_output:
        # R1: a partially staged note whose staged copy the fixer would
        # change, named once, in the hook's words, never as the bare line.
        assert completed.stderr.count("inbox/x.md") == 1
        assert (
            "pre-commit: the staged copy is not fixed — stage it: inbox/x.md\n"
            in completed.stderr
        )
    if fixer_output.startswith(("skipped", "unresolved")):
        assert fixer_output.strip() in completed.stderr
    if fixer_status == 4:
        assert (
            "pre-commit: the OKF reader's dependency is missing (PyYAML); refusing an unverified commit."
            in completed.stderr
        )


def test_hook_documents_escape_hatch_and_replay_and_is_executable():
    text = HOOK.read_text()
    assert HOOK.stat().st_mode & os.X_OK
    subprocess.run(["sh", "-n", str(HOOK)], check=True)
    assert "git commit --no-verify" in text
    assert "CI replay" in text
    assert "git add" not in text
    assert "never stages" in text
