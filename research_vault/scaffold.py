"""Create a new research-vault vault from packaged templates."""

import json
import shutil
import stat
import subprocess
import urllib.parse
from importlib import resources
from pathlib import Path
from typing import NamedTuple

from . import Result, addons, okf, paths
from .zotero import LocalApiDisabledError, ZoteroClient, ZoteroError

VAULT_DIRS = [
    "inbox",
    "literatures",
    "log",
    "projects",
    "system/templates",
    "system/bases",
]
PROVISION_COMPANIONS = ["kepano/obsidian-skills"]
_EMPTY_ROOTS = ("literatures", "log", "projects")
_LOCAL_ONLY_PATHS = {".git/hooks/pre-commit", ".research-vault/machine.json"}
GLOSSARY_PATH = "system/glossary.md"
GLOSSARY_ENVELOPE = b'---\ntype: "guide"\n---\n\n'


class Probe(NamedTuple):
    """One doctor row, in the Outcome vocabulary (check/result/reason)."""

    check: str
    result: Result
    reason: str


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


def _machine_config(vault: Path) -> tuple[dict, Probe]:
    path = vault / ".research-vault" / "machine.json"
    try:
        config = json.loads(path.read_text())
        if not isinstance(config, dict):
            raise ValueError("expected an object")
    except (OSError, UnicodeError, ValueError) as error:
        return {}, Probe(
            "machine-config", Result.UNMATCHED, f"machine config unreadable: {error}"
        )
    mailto = config.get("mailto")
    if (
        not isinstance(mailto, str)
        or not mailto.strip()
        or mailto.strip() == "you@example.edu"
    ):
        return config, Probe(
            "machine-config",
            Result.UNMATCHED,
            "mailto is missing or still uses you@example.edu",
        )
    return config, Probe("machine-config", Result.MATCHED, f"mailto {mailto.strip()}")


def _remote_probe(vault: Path) -> Probe:
    try:
        result = _git(vault, "remote", check=False)
    except OSError as error:
        return Probe("remote", Result.UNREACHABLE, f"Git remote unreadable: {error}")
    if result.returncode == 0 and result.stdout.strip():
        return Probe("remote", Result.MATCHED, result.stdout.splitlines()[0])
    return Probe(
        "remote",
        Result.UNMATCHED,
        "no remote — vault endures only on this disk (§2)",
    )


def _backup_probe(config: dict) -> Probe:
    backup = config.get("zotero_backup")
    if isinstance(backup, str) and backup.strip():
        return Probe("backup", Result.MATCHED, backup.strip())
    return Probe(
        "backup",
        Result.UNMATCHED,
        "no stated Zotero storage backup (§2 boundary)",
    )


_WRONG_ID = "research-vault-wrong-id"
_COMPILE_PLUGIN = "claude-obsidian@agricidaniel-claude-obsidian"
_COMPILE_PIN = "ad67087"


def _tree_probe(vault: Path) -> Probe:
    try:
        scaffold_vault(vault)
        tree_complete = all((vault / relative).is_dir() for relative in VAULT_DIRS)
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        return Probe("tree", Result.UNMATCHED, f"vault tree repair failed: {error}")
    if tree_complete:
        return Probe("tree", Result.MATCHED, "required vault tree complete")
    return Probe(
        "tree", Result.UNMATCHED, "required vault tree incomplete after repair"
    )


def _installed_plugins() -> dict:
    path = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return {}
    plugins = data.get("plugins") if isinstance(data, dict) else None
    return plugins if isinstance(plugins, dict) else {}


def _zotero_probe(client) -> tuple[Probe, dict | None]:
    try:
        info = client.server_info()
    except LocalApiDisabledError:
        return Probe(
            "zotero",
            Result.UNMATCHED,
            "local API preference is off — enable it in Settings, Advanced",
        ), None
    except (ZoteroError, OSError, UnicodeError, ValueError) as error:
        return Probe("zotero", Result.UNREACHABLE, str(error)), None
    reason = " ".join(f"{key}={value}" for key, value in info.items())
    return Probe("zotero", Result.MATCHED, reason), info


def _write_guard_probe(client, info) -> Probe:
    if info is None:
        return Probe("write-guard", Result.SKIPPED, "zotero unreachable")
    try:
        response = client._http(
            f"{client.base}/api/users/0/items",
            data=b"[]",
            headers={"Zotero-Server-ID": _WRONG_ID, "Content-Type": "application/json"},
            method="POST",
        )
    except ZoteroError as error:
        return Probe("write-guard", Result.UNREACHABLE, str(error))
    if response.status == 412:
        return Probe(
            "write-guard",
            Result.MATCHED,
            "a wrong server id is refused before any key (412)",
        )
    return Probe(
        "write-guard",
        Result.UNMATCHED,
        f"wrong server id answered {response.status}, not 412 — the guard is not armed",
    )


def _profile_dir(config) -> Path | None:
    value = config.get("zotero_profile")
    if isinstance(value, str) and value.strip() and Path(value).is_dir():
        return Path(value)
    return None


def _fulltext_sync_probe(prefs) -> Probe:
    if prefs is None:
        return Probe("fulltext-sync", Result.SKIPPED, "zotero_profile not configured")
    enabled = prefs.get("extensions.zotero.sync.fulltext.enabled", False)
    protocol = prefs.get("extensions.zotero.sync.storage.protocol", "zotero")
    return Probe(
        "fulltext-sync",
        Result.MATCHED,
        f"sync.fulltext.enabled={enabled} storage.protocol={protocol}",
    )


def _bbt_git_probe(prefs) -> Probe:
    if prefs is None:
        return Probe("bbt-git", Result.SKIPPED, "zotero_profile not configured")
    value = prefs.get("extensions.zotero.translators.better-bibtex.git", "off")
    if value == "off":
        return Probe("bbt-git", Result.MATCHED, "git=off")
    return Probe(
        "bbt-git",
        Result.UNMATCHED,
        f"git={value} — Better BibTeX may run git inside an export target",
    )


def _plugins_probe(profile, prefs) -> Probe:
    if profile is None or prefs is None:
        return Probe("plugins", Result.SKIPPED, "zotero_profile not configured")
    try:
        observed = addons.observe(profile)
    except (OSError, UnicodeError, ValueError, KeyError, AttributeError) as error:
        return Probe(
            "plugins", Result.UNREACHABLE, f"extensions.json unreadable: {error}"
        )
    failures: list[str] = []
    notes_out: list[str] = []
    for addon in addons.declared():
        seen = observed.get(addon.addon_id)
        if seen is None:
            state = "missing"
        elif seen["appDisabled"]:
            state = "appDisabled"
        elif not seen["active"]:
            state = "inactive"
        else:
            state = "active"
        notes_out.append(f"{addon.addon_id} {state}")
        if addon.need == "required" and state != "active":
            failures.append(f"{addon.name} {state}")
        if (
            addon.auto_pref
            and state == "active"
            and prefs.get(addon.auto_pref) is not True
        ):
            failures.append(f"{addon.name} automatic mode off ({addon.auto_pref})")
    if failures:
        return Probe("plugins", Result.UNMATCHED, "; ".join(failures))
    return Probe("plugins", Result.MATCHED, "; ".join(notes_out))


def _path_shim_probe(client, info, vault: Path) -> Probe:
    if not paths._running_in_wsl():
        return Probe("path-shim", Result.SKIPPED, "not running in WSL")
    if info is None:
        return Probe("path-shim", Result.SKIPPED, "zotero unreachable")
    try:
        # Measured 2026-09-07: the local API ignores a `linkMode` query filter (it
        # answered `imported_url` rows for `linkMode=imported_file`), so fetch
        # attachments and filter client-side (decision 25).
        payload, _ = client._local_json(
            "/api/users/0/items?itemType=attachment&limit=50&format=json"
        )
        stored = [
            row
            for row in payload
            if isinstance(row, dict)
            and isinstance(row.get("data"), dict)
            and row["data"].get("linkMode") == "imported_file"
        ]
        key = stored[0]["key"] if stored else None
        url = client.file_view_url(key) if key else None
    except (ZoteroError, KeyError, IndexError, TypeError) as error:
        return Probe(
            "path-shim", Result.UNREACHABLE, f"no stored attachment to resolve: {error}"
        )
    if not url:
        return Probe("path-shim", Result.UNREACHABLE, "no stored attachment to resolve")
    windows_path = urllib.parse.unquote(url.removeprefix("file:///")).replace("/", "\\")
    try:
        local = paths.to_local(windows_path, vault)
    except paths.PathError as error:
        return Probe("path-shim", Result.UNMATCHED, str(error))
    result = Result.MATCHED if local.is_file() else Result.UNMATCHED
    return Probe("path-shim", result, str(local))


def _translator_formats_probe(client, info) -> Probe:
    if info is None:
        return Probe("translator-formats", Result.SKIPPED, "zotero unreachable")
    try:
        response = client._http(
            f"{client.base}/api/users/0/items/top?format=csljson&limit=1"
        )
    except ZoteroError as error:
        return Probe("translator-formats", Result.UNREACHABLE, str(error))
    if response.status == 500:
        return Probe(
            "translator-formats",
            Result.MATCHED,
            "translator formats still answer 500 (closed route)",
        )
    return Probe(
        "translator-formats",
        Result.UNMATCHED,
        f"format=csljson answered {response.status} — a route this design closed has reopened",
    )


def _compile_tool_probe() -> Probe:
    records = _installed_plugins().get(_COMPILE_PLUGIN)
    record = records[0] if isinstance(records, list) and records else None
    if not isinstance(record, dict):
        return Probe("compile-tool", Result.SKIPPED, f"{_COMPILE_PLUGIN} not installed")
    sha = str(record.get("gitCommitSha", ""))
    if sha.startswith(_COMPILE_PIN):
        return Probe("compile-tool", Result.MATCHED, f"{_COMPILE_PLUGIN} at {sha[:7]}")
    return Probe(
        "compile-tool",
        Result.UNMATCHED,
        f"{_COMPILE_PLUGIN} at {sha[:7]}, pin is {_COMPILE_PIN}",
    )


def _bbt_probe(client) -> Probe:
    """Independent of the local-API preference: `/better-bibtex/json-rpc` answers with it off (§9)."""
    try:
        versions = client.ready()
    except (ZoteroError, OSError, UnicodeError, ValueError) as error:
        return Probe("bbt", Result.UNREACHABLE, f"zotero down: {error}")
    bbt_version = versions.get("betterbibtex")
    if not isinstance(bbt_version, str) or not bbt_version.strip():
        return Probe("bbt", Result.UNMATCHED, "Better BibTeX version missing")
    return Probe("bbt", Result.MATCHED, bbt_version.strip())


def doctor(vault_root, client=None) -> list[Probe]:
    """Repair the scoped vault substrate and return its thirteen ordered probes (§5)."""
    vault = Path(vault_root)
    tree = _tree_probe(vault)
    config, machine = _machine_config(vault)
    client = ZoteroClient() if client is None else client
    zotero_probe, info = _zotero_probe(client)
    profile = _profile_dir(config)
    prefs: dict[str, str | bool | int] | None = None
    if profile is not None:
        try:
            prefs = addons.read_prefs(profile)
        except (OSError, UnicodeError, ValueError):
            prefs = None
    # Never gated on `info`: the json-rpc route ignores the local-API preference.
    bbt = _bbt_probe(client)
    return [
        tree,
        machine,
        zotero_probe,
        _write_guard_probe(client, info),
        _fulltext_sync_probe(prefs),
        bbt,
        _bbt_git_probe(prefs),
        _plugins_probe(profile, prefs),
        _path_shim_probe(client, info, vault),
        _translator_formats_probe(client, info),
        _compile_tool_probe(),
        _remote_probe(vault),
        _backup_probe(config),
    ]
