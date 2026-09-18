"""Create a new research-vault vault from packaged templates."""

import shutil
import stat
import subprocess
from importlib import resources
from pathlib import Path

from . import okf

VAULT_DIRS = [
    "inbox",
    "literature",
    "log",
    "projects",
    "system/templates",
    "system/bases",
]
PROVISION_COMPANIONS = [
    "kepano/obsidian-skills",
    "claude-obsidian@agricidaniel-claude-obsidian",
]
_EMPTY_ROOTS = ("literature", "log", "projects")
_LOCAL_ONLY_PATHS = {".git/hooks/pre-commit", ".research-vault/machine.json"}
GLOSSARY_PATH = "system/glossary.md"
GLOSSARY_ENVELOPE = b'---\ntype: "guide"\n---\n\n'


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


# Dotfiles ship dotless (packaging pitfall: a dotfile committed directly as
# a template asset risks silently failing to package) and are renamed here
# on write.
_DOTLESS_TEMPLATE_RENAMES = {
    "gitignore": ".gitignore",
    "prettierignore": ".prettierignore",
    "markdownlintignore": ".markdownlintignore",
    "editorconfig": ".editorconfig",
}


def _vault_template_paths(templates):
    source_root = templates.joinpath("vault")
    for relative, source in _template_files(source_root):
        yield _DOTLESS_TEMPLATE_RENAMES.get(relative, relative), source


def _copy_vault_templates(vault: Path, templates, created: list[str]) -> None:
    for relative, source in _vault_template_paths(templates):
        _copy_if_absent(source, vault / relative, relative, created)


def _render_glossary_if_absent(vault: Path, templates, created: list[str]) -> None:
    target = vault / GLOSSARY_PATH
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    source = templates.joinpath("context.md")
    with target.open("xb") as output_file:
        output_file.write(GLOSSARY_ENVELOPE)
        output_file.write(source.read_bytes())
    created.append(GLOSSARY_PATH)


def _add_empty_root_sentinels(vault: Path, created: list[str]) -> None:
    for root in _EMPTY_ROOTS:
        directory = vault / root
        if not any(directory.iterdir()):
            sentinel = directory / ".gitkeep"
            sentinel.touch(exist_ok=False)
            created.append(sentinel.relative_to(vault).as_posix())


def _owned_paths(templates, with_ci: bool, with_rw_ci: bool) -> list[str]:
    owned = [*VAULT_DIRS]
    owned.extend(relative for relative, _source in _vault_template_paths(templates))
    owned.append(GLOSSARY_PATH)
    owned.extend(f"{root}/.gitkeep" for root in _EMPTY_ROOTS)
    owned.extend((".research-vault/machine.json", ".git/hooks/pre-commit"))
    if with_ci:
        owned.append(".github/workflows/verify.yml")
    if with_rw_ci:
        owned.append(".github/workflows/rw-batch.yml")
    return owned


def _reject_owned_symlinks(vault: Path, owned_paths: list[str]) -> None:
    for current in (vault, *vault.parents):
        if current.is_symlink():
            raise ValueError(f"scaffold symlink conflict: {current}")
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
    else:
        result = _git(vault, "rev-parse", "--show-toplevel", check=False)
        if result.returncode != 0:
            _git(vault, "init", "-q")
        elif Path(result.stdout.strip()).resolve() != vault.resolve():
            raise ValueError(f"scaffold destination is not its own Git root: {vault}")
    # The hook is installed at the literal `.git/hooks/pre-commit`, so the
    # repository's git directory must be that `.git` (a linked worktree's or a
    # gitfile's is another repository's) and git must read hooks from it (a
    # core.hooksPath sends every hook elsewhere). Measured 2026-09-17, git
    # 2.43.0: both put the hook in a foreign directory.
    common = Path(
        _git(
            vault, "rev-parse", "--path-format=absolute", "--git-common-dir"
        ).stdout.strip()
    )
    if common.resolve() != metadata.resolve():
        raise ValueError(
            "scaffold destination's git directory is not its own: "
            f"{common.resolve()} is not {metadata}"
        )
    hooks_path = _git(vault, "config", "--get", "core.hooksPath", check=False)
    if hooks_path.returncode == 0 and hooks_path.stdout.strip():
        raise ValueError(
            f"scaffold refuses core.hooksPath {hooks_path.stdout.strip()}: the "
            f"vault hook lives at {metadata / 'hooks' / 'pre-commit'} and nothing "
            "reads where git would resolve it"
        )


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
    if not (vault / GLOSSARY_PATH).exists():
        candidates.append(GLOSSARY_PATH)
    for root in _EMPTY_ROOTS:
        directory = vault / root
        if not directory.exists() or not any(directory.iterdir()):
            candidates.append(f"{root}/.gitkeep")
    if not (vault / ".research-vault" / "machine.json").exists():
        candidates.append(".research-vault/machine.json")
    if with_ci and not (vault / ".github" / "workflows" / "verify.yml").exists():
        candidates.append(".github/workflows/verify.yml")
    if with_rw_ci and not (vault / ".github" / "workflows" / "rw-batch.yml").exists():
        candidates.append(".github/workflows/rw-batch.yml")
    conflicts = sorted(
        relative for relative in candidates if _is_tracked(vault, relative)
    )
    if conflicts:
        raise ValueError(f"scaffold conflict with tracked path: {conflicts[0]}")


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
    templates = resources.files("research_vault").joinpath("templates")
    owned_paths = _owned_paths(templates, with_ci, with_rw_ci)
    _reject_owned_symlinks(vault, owned_paths)
    _prepare_repository(vault)
    _preflight_conflicts(vault, templates, with_ci, with_rw_ci)

    created: list[str] = []
    for directory in VAULT_DIRS:
        (vault / directory).mkdir(parents=True, exist_ok=True)

    _copy_vault_templates(vault, templates, created)
    _render_glossary_if_absent(vault, templates, created)
    if "log.md" in created:
        # Ship a freshly-scaffolded vault's log.md already OKF-conformant
        # (type: "log") rather than leaving the inert packaged placeholder
        # until a later verb regenerates it.
        okf.regenerate_log(vault)
    _add_empty_root_sentinels(vault, created)
    _copy_if_absent(
        templates.joinpath("research-vault", "machine.json.example"),
        vault / ".research-vault" / "machine.json",
        ".research-vault/machine.json",
        created,
    )
    hook = vault / ".git" / "hooks" / "pre-commit"
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
