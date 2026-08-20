"""Create a new knowledge-harness vault from packaged templates."""

import shutil
import stat
import subprocess
from importlib import resources
from pathlib import Path

VAULT_DIRS = [
    "inbox",
    "literatures",
    "synthesis",
    "log",
    "projects",
    "x/templates",
    "x/bases",
]
_EMPTY_ROOTS = ("literatures", "log", "projects")


def _git(vault: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=vault,
        check=check,
        text=True,
        capture_output=True,
    )


def _git_is_initialized(vault: Path) -> bool:
    result = _git(vault, "rev-parse", "--is-inside-work-tree", check=False)
    return result.returncode == 0 and result.stdout.strip() == "true"


def _template_files(root):
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if child.is_dir():
            yield from _template_files(child)
        elif child.is_file():
            yield child


def _copy_if_absent(source, target: Path, created: list[str], vault: Path) -> None:
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as input_file, target.open("xb") as output_file:
        shutil.copyfileobj(input_file, output_file)
    created.append(target.relative_to(vault).as_posix())


def _copy_vault_templates(vault: Path, templates, created: list[str]) -> None:
    source_root = templates.joinpath("vault")
    for source in _template_files(source_root):
        relative = source.relative_to(source_root).as_posix()
        target = vault / (".gitignore" if relative == "gitignore" else relative)
        _copy_if_absent(source, target, created, vault)


def _add_empty_root_sentinels(vault: Path, created: list[str]) -> None:
    for root in _EMPTY_ROOTS:
        directory = vault / root
        if not any(directory.iterdir()):
            sentinel = directory / ".gitkeep"
            sentinel.touch(exist_ok=False)
            created.append(sentinel.relative_to(vault).as_posix())


def _trackable_paths(vault: Path, created: list[str]) -> list[str]:
    trackable = []
    for relative in created:
        if relative.startswith(".git/"):
            continue
        result = _git(vault, "check-ignore", "-q", "--", relative, check=False)
        if result.returncode != 0:
            trackable.append(relative)
    return sorted(trackable)


def _commit_created_paths(vault: Path, created: list[str]) -> None:
    trackable = _trackable_paths(vault, created)
    if not trackable:
        return
    _git(vault, "add", "--", *trackable)
    _git(
        vault,
        "commit",
        "--no-verify",
        "--only",
        "-m",
        "Scaffold knowledge vault",
        "--",
        *trackable,
    )


def scaffold_vault(dest, with_ci: bool = False, with_rw_ci: bool = False) -> list[str]:
    """Create missing vault assets and commit only the newly created trackable paths."""
    vault = Path(dest).resolve()
    vault.mkdir(parents=True, exist_ok=True)
    if not _git_is_initialized(vault):
        _git(vault, "init", "-q")

    created: list[str] = []
    for directory in VAULT_DIRS:
        (vault / directory).mkdir(parents=True, exist_ok=True)

    templates = resources.files("harness_core").joinpath("templates")
    _copy_vault_templates(vault, templates, created)
    _add_empty_root_sentinels(vault, created)
    _copy_if_absent(
        templates.joinpath("harness", "machine.json.example"),
        vault / ".harness" / "machine.json",
        created,
        vault,
    )
    hook = vault / ".git" / "hooks" / "pre-commit"
    _copy_if_absent(templates.joinpath("git", "pre-commit"), hook, created, vault)
    if ".git/hooks/pre-commit" in created:
        hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    if with_ci:
        _copy_if_absent(
            templates.joinpath("ci", "verify.yml"),
            vault / ".github" / "workflows" / "verify.yml",
            created,
            vault,
        )
    if with_rw_ci:
        _copy_if_absent(
            templates.joinpath("ci", "rw-batch.yml"),
            vault / ".github" / "workflows" / "rw-batch.yml",
            created,
            vault,
        )

    _commit_created_paths(vault, created)
    return sorted(created)
