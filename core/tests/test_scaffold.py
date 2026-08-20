import os
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path

from harness_core import frontmatter, scaffold

VAULT_DIRS = [
    "inbox",
    "literatures",
    "synthesis",
    "log",
    "projects",
    "x/templates",
    "x/bases",
]
EXPECTED_CREATED = [
    ".git/hooks/pre-commit",
    ".gitignore",
    ".harness/machine.json",
    "AGENTS.md",
    "inbox/review-queue.md",
    "index.md",
    "literatures/.gitkeep",
    "log.md",
    "log/.gitkeep",
    "projects/.gitkeep",
    "synthesis/index.md",
    "x/bases/open-questions.base",
    "x/bases/trust-tier.base",
    "x/templates/daily.md",
    "x/templates/literature.md",
    "x/templates/project.md",
    "x/templates/synthesis.md",
]
TRACKABLE_CREATED = [
    path for path in EXPECTED_CREATED if not path.startswith((".git/", ".harness/"))
]


def git(path, *args):
    return subprocess.run(
        ["git", *args], cwd=path, check=True, text=True, capture_output=True
    ).stdout


def test_scaffold_module_is_available():
    """Removing the scaffold command implementation makes this fail."""
    assert find_spec("harness_core.scaffold") is not None


def test_scaffold_creates_the_complete_okf_vault_and_returns_paths(tmp_path):
    """Omitting an owned vault artifact or returning a non-auditable path fails."""
    vault = tmp_path / "vault"

    created = scaffold.scaffold_vault(vault)

    assert created == EXPECTED_CREATED
    assert scaffold.VAULT_DIRS == VAULT_DIRS
    assert all((vault / path).exists() for path in EXPECTED_CREATED)
    assert all((vault / path).is_dir() for path in VAULT_DIRS)
    assert (vault / ".git").is_dir()
    assert (vault / "index.md").read_text() == (
        '---\nokf_version: "0.2"\n---\n# Knowledge bundle\n'
    )
    assert (vault / "log.md").read_text() == "# Log\n"
    assert (
        (vault / ".gitignore")
        .read_text()
        .startswith("# vault/gitignore; scaffold copies this to .gitignore\n")
    )
    assert (vault / ".harness" / "machine.json").read_text() == (
        '{\n  "mailto": "you@example.edu",\n'
        '  "path_map": {"D:\\\\Zotero\\\\": "/mnt/d/Zotero/"}\n}\n'
    )
    for path in (
        "AGENTS.md",
        "inbox/review-queue.md",
        "x/templates/daily.md",
        "x/templates/literature.md",
        "x/templates/project.md",
        "x/templates/synthesis.md",
    ):
        data, _ = frontmatter.parse((vault / path).read_text())
        assert data["type"]
    for path in ("log.md", "synthesis/index.md"):
        data, _ = frontmatter.parse((vault / path).read_text())
        assert data == {}


def test_scaffold_is_idempotent_and_never_overwrites_existing_files(tmp_path):
    """Replacing user-maintained scaffold paths or making a second pass mutating fails."""
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "index.md").write_text("human index\n")
    (vault / ".harness").mkdir()
    (vault / ".harness" / "machine.json").write_text('{"mailto": "human"}\n')
    hooks = vault / ".git" / "hooks"
    hooks.mkdir(parents=True)
    hook = hooks / "pre-commit"
    hook.write_text("#!/bin/sh\necho human\n")

    created = scaffold.scaffold_vault(vault)

    assert "index.md" not in created
    assert ".harness/machine.json" not in created
    assert ".git/hooks/pre-commit" not in created
    assert (vault / "index.md").read_text() == "human index\n"
    assert (vault / ".harness" / "machine.json").read_text() == '{"mailto": "human"}\n'
    assert hook.read_text() == "#!/bin/sh\necho human\n"
    assert not os.access(hook, os.X_OK)
    assert scaffold.scaffold_vault(vault) == []


def test_scaffold_installs_an_executable_hook_and_keeps_empty_roots_in_clones(tmp_path):
    """Dropping hook execute permission or empty vault roots after clone fails."""
    vault = tmp_path / "vault"
    scaffold.scaffold_vault(vault)

    assert os.access(vault / ".git" / "hooks" / "pre-commit", os.X_OK)
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(vault), str(clone)], check=True)
    for root in ("literatures", "log", "projects"):
        assert (clone / root / ".gitkeep").is_file()


def test_scaffold_ci_flags_are_independent(tmp_path):
    """Making either CI workflow imply the other fails."""
    read_only = tmp_path / "read-only"
    rw = tmp_path / "rw"

    read_only_created = scaffold.scaffold_vault(read_only, with_ci=True)
    rw_created = scaffold.scaffold_vault(rw, with_rw_ci=True)

    assert ".github/workflows/verify.yml" in read_only_created
    assert ".github/workflows/rw-batch.yml" not in read_only_created
    assert ".github/workflows/rw-batch.yml" in rw_created
    assert ".github/workflows/verify.yml" not in rw_created


def test_scaffold_commits_only_its_created_paths_and_preserves_user_index(tmp_path):
    """Sweeping user changes into the scaffold commit or altering their index fails."""
    vault = tmp_path / "vault"
    vault.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=vault, check=True)
    git(vault, "config", "user.name", "Test User")
    git(vault, "config", "user.email", "test@example.edu")
    (vault / "baseline.md").write_text("baseline\n")
    git(vault, "add", "--", "baseline.md")
    git(vault, "commit", "-qm", "baseline")
    (vault / "staged.md").write_text("staged\n")
    git(vault, "add", "--", "staged.md")
    (vault / "unstaged.md").write_text("unstaged\n")
    (vault / "untracked.md").write_text("untracked\n")
    index_before = git(vault, "diff", "--cached", "--binary")

    created = scaffold.scaffold_vault(vault)

    assert created == EXPECTED_CREATED
    assert git(vault, "diff", "--cached", "--binary") == index_before
    assert git(vault, "show", "--format=", "--name-only", "HEAD").splitlines() == (
        TRACKABLE_CREATED
    )
    assert (vault / "unstaged.md").read_text() == "unstaged\n"
    assert (vault / "untracked.md").read_text() == "untracked\n"


def test_scaffold_cli_prints_the_created_paths(tmp_path):
    """A CLI that hides local-only creation or ignores the flags fails."""
    vault = tmp_path / "vault"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "harness_core",
            "scaffold",
            "--vault",
            str(vault),
            "--with-ci",
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        text=True,
        capture_output=True,
    )

    assert completed.stdout.splitlines() == sorted(
        [*EXPECTED_CREATED, ".github/workflows/verify.yml"]
    )
