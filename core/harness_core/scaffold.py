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
_LOCAL_ONLY_PATHS = {".git/hooks/pre-commit", ".harness/machine.json"}


def _git(vault: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=vault,
        check=check,
        text=True,
        capture_output=True,
    )


def _template_files(root, relative=()):
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        child_relative = (*relative, child.name)
        if child.is_dir():
            yield from _template_files(child, child_relative)
        elif child.is_file():
            yield Path(*child_relative).as_posix(), child


def _copy_if_absent(source, target: Path, relative: str, created: list[str]) -> None:
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as input_file, target.open("xb") as output_file:
        shutil.copyfileobj(input_file, output_file)
    created.append(relative)


def _vault_template_paths(templates):
    source_root = templates.joinpath("vault")
    for relative, source in _template_files(source_root):
        yield ".gitignore" if relative == "gitignore" else relative, source


def _copy_vault_templates(vault: Path, templates, created: list[str]) -> None:
    for relative, source in _vault_template_paths(templates):
        _copy_if_absent(source, vault / relative, relative, created)


def _add_empty_root_sentinels(vault: Path, created: list[str]) -> None:
    for root in _EMPTY_ROOTS:
        directory = vault / root
        if not any(directory.iterdir()):
            sentinel = directory / ".gitkeep"
            sentinel.touch(exist_ok=False)
            created.append(sentinel.relative_to(vault).as_posix())


def _owned_paths(templates, with_ci: bool, with_rw_ci: bool) -> list[str]:
    paths = [*VAULT_DIRS]
    paths.extend(relative for relative, _source in _vault_template_paths(templates))
    paths.extend(f"{root}/.gitkeep" for root in _EMPTY_ROOTS)
    paths.extend((".harness/machine.json", ".git/hooks/pre-commit"))
    if with_ci:
        paths.append(".github/workflows/verify.yml")
    if with_rw_ci:
        paths.append(".github/workflows/rw-batch.yml")
    return paths


def _reject_owned_symlinks(vault: Path, owned_paths: list[str]) -> None:
    if vault.is_symlink():
        raise ValueError(f"scaffold symlink conflict: {vault}")
    for relative in owned_paths:
        current = vault
        for component in Path(relative).parts:
            current /= component
            if current.is_symlink():
                raise ValueError(f"scaffold symlink conflict: {current}")


def _prepare_repository(vault: Path) -> None:
    metadata = vault / ".git"
    if not metadata.exists() and not metadata.is_symlink():
        vault.mkdir(parents=True, exist_ok=True)
        _git(vault, "init", "-q")
        return

    result = _git(vault, "rev-parse", "--show-toplevel", check=False)
    if result.returncode != 0:
        _git(vault, "init", "-q")
        return
    if Path(result.stdout.strip()).resolve() != vault.resolve():
        raise ValueError(f"scaffold destination is not its own Git root: {vault}")


def _is_tracked(vault: Path, relative: str) -> bool:
    in_index = (
        _git(
            vault, "ls-files", "--error-unmatch", "--", relative, check=False
        ).returncode
        == 0
    )
    in_head = _git(vault, "cat-file", "-e", f"HEAD:{relative}", check=False)
    return in_index or in_head.returncode == 0


def _preflight_conflicts(
    vault: Path, templates, with_ci: bool, with_rw_ci: bool
) -> None:
    candidates = []
    for relative, _source in _vault_template_paths(templates):
        if not (vault / relative).exists():
            candidates.append(relative)
    for root in _EMPTY_ROOTS:
        directory = vault / root
        if not directory.exists() or not any(directory.iterdir()):
            candidates.append(f"{root}/.gitkeep")
    if not (vault / ".harness" / "machine.json").exists():
        candidates.append(".harness/machine.json")
    if with_ci and not (vault / ".github" / "workflows" / "verify.yml").exists():
        candidates.append(".github/workflows/verify.yml")
    if with_rw_ci and not (vault / ".github" / "workflows" / "rw-batch.yml").exists():
        candidates.append(".github/workflows/rw-batch.yml")
    conflicts = sorted(
        relative for relative in candidates if _is_tracked(vault, relative)
    )
    if conflicts:
        raise ValueError(f"scaffold conflict with tracked path: {conflicts[0]}")


def _git_path(vault: Path, path: str) -> Path:
    result = _git(vault, "rev-parse", "--git-path", path)
    resolved = Path(result.stdout.strip())
    return resolved if resolved.is_absolute() else vault / resolved


def _trackable_paths(vault: Path, created: list[str]) -> list[str]:
    trackable = []
    for relative in created:
        if relative in _LOCAL_ONLY_PATHS:
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
    vault = Path(dest).absolute()
    templates = resources.files("harness_core").joinpath("templates")
    owned_paths = _owned_paths(templates, with_ci, with_rw_ci)
    _reject_owned_symlinks(vault, owned_paths)
    _prepare_repository(vault)
    _preflight_conflicts(vault, templates, with_ci, with_rw_ci)

    created: list[str] = []
    for directory in VAULT_DIRS:
        (vault / directory).mkdir(parents=True, exist_ok=True)

    _copy_vault_templates(vault, templates, created)
    _add_empty_root_sentinels(vault, created)
    _copy_if_absent(
        templates.joinpath("harness", "machine.json.example"),
        vault / ".harness" / "machine.json",
        ".harness/machine.json",
        created,
    )
    hook = _git_path(vault, "hooks/pre-commit")
    _copy_if_absent(
        templates.joinpath("git", "pre-commit"), hook, ".git/hooks/pre-commit", created
    )
    if ".git/hooks/pre-commit" in created:
        hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    if with_ci:
        _copy_if_absent(
            templates.joinpath("ci", "verify.yml"),
            vault / ".github" / "workflows" / "verify.yml",
            ".github/workflows/verify.yml",
            created,
        )
    if with_rw_ci:
        _copy_if_absent(
            templates.joinpath("ci", "rw-batch.yml"),
            vault / ".github" / "workflows" / "rw-batch.yml",
            ".github/workflows/rw-batch.yml",
            created,
        )

    _commit_created_paths(vault, created)
    return sorted(created)
