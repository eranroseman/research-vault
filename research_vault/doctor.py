"""The doctor: repair the scoped vault substrate, then the ordered probes (assembly spec §9).

Scaffolding (`scaffold.py`) creates and commits; this module observes. It
calls only `scaffold_vault`, `VAULT_DIRS` and `_git` from the other side.
"""

import json
import re
import subprocess
import urllib.parse
from importlib import resources
from pathlib import Path
from typing import NamedTuple

from . import Result, addons, obsidian_plugins, paths, structure
from .scaffold import VAULT_DIRS, _git, scaffold_vault
from .zotero import LocalApiDisabledError, ZoteroClient, ZoteroError, header


class Probe(NamedTuple):
    """One doctor row, in the Outcome vocabulary (check/result/reason).

    `facts` are the per-component failing facts, one entry per component id:
    hashable, so they never carry an installed version (DP18).
    """

    check: str
    result: Result
    reason: str
    facts: tuple[tuple[str, tuple[str, ...]], ...] = ()


def _machine_config(vault: Path) -> tuple[dict, Probe]:
    path = vault / ".research-vault" / "machine.json"
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
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
_COMPILE_PIN = "32ac5a0"
_UNSET = "unset (Zotero default)"
_PAGE_SIZE = 50
_MAX_PAGES = 20
_ATTACHMENT_PAGE = (
    "/api/users/0/items?itemType=attachment&sort=dateAdded&direction=asc"
    f"&limit={_PAGE_SIZE}&start={{start}}&format=json"
)
_WINDOWS_FILE_URL = re.compile(r"^file:///[A-Za-z]:/")


class _ProfileHold(NamedTuple):
    """The row every profile probe reports instead of reading the profile."""

    result: Result
    reason: str


class _ProfileFacts(NamedTuple):
    """A readable zotero_profile directory and its prefs.js.

    `unreadable` holds the prefs.js lines the grammar refused: a declared key
    named on one is UNREACHABLE, never unset (spec §6.1).
    """

    path: Path
    prefs: dict[str, str | bool | int]
    unreadable: tuple[str, ...] = ()


_OLD_LITERATURE_ROOT = "literatures"


def _tree_probe(vault: Path) -> Probe:
    if (vault / _OLD_LITERATURE_ROOT).exists():
        # A vault from before the 2026-09-17 rename: scaffolding here would
        # create an empty literature/ beside the populated old root and report
        # the tree complete. The rename is the person's act (a machine surface
        # is never renamed by doctor); nothing is created while it stands.
        return Probe(
            "tree",
            Result.UNMATCHED,
            f"stray {_OLD_LITERATURE_ROOT}/: rename to literature/ by hand, "
            "then run capture --all",
        )
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


def _zotero_probe(client) -> Probe:
    try:
        info = client.server_info()
    except LocalApiDisabledError:
        return Probe(
            "zotero",
            Result.UNMATCHED,
            "local API preference is off — enable it in Settings, Advanced",
        )
    except (ZoteroError, OSError, UnicodeError, ValueError) as error:
        return Probe("zotero", Result.UNREACHABLE, str(error))
    reason = " ".join(f"{key}={value}" for key, value in info.items())
    return Probe("zotero", Result.MATCHED, reason)


def _local_api_skip(zotero_probe: Probe) -> str | None:
    """Why a probe that needs the local API cannot run, or None when it answered."""
    if zotero_probe.result is Result.MATCHED:
        return None
    if zotero_probe.result is Result.UNMATCHED:
        return "local API preference is off"
    return "zotero unreachable"


def _write_guard_probe(client, skip: str | None) -> Probe:
    if skip:
        return Probe("write-guard", Result.SKIPPED, skip)
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


def _profile_facts(config) -> _ProfileFacts | _ProfileHold:
    """Read the profile once for the three probes that need it (decision 15).

    A configured-but-wrong profile is a finding, never "not configured": only an
    absent, null or empty key is unconfigured (as zotero_base is read).
    Could not read is an outage and malformed content a fault —
    the split captured.py makes on every file it opens.
    """
    value = config.get("zotero_profile")
    if value is None or (isinstance(value, str) and not value.strip()):
        return _ProfileHold(Result.SKIPPED, "zotero_profile not configured")
    if not isinstance(value, str):
        return _ProfileHold(Result.UNMATCHED, "zotero_profile must be a string")
    path = Path(value)
    try:
        is_dir = path.is_dir()
    except OSError as error:  # permission denied, a name too long: an outage
        return _ProfileHold(Result.UNREACHABLE, f"zotero_profile unreadable: {error}")
    if not is_dir:
        return _ProfileHold(
            Result.UNMATCHED, f"zotero_profile {path} is not a directory"
        )
    try:
        prefs = addons.read_prefs(path)
        unreadable = addons.unreadable_pref_lines(path)
    except OSError as error:
        return _ProfileHold(Result.UNREACHABLE, f"prefs.js unreadable: {error}")
    except (UnicodeError, ValueError) as error:
        return _ProfileHold(Result.UNMATCHED, f"prefs.js unparseable: {error}")
    return _ProfileFacts(path, prefs, unreadable)


def _fulltext_sync_probe(profile: _ProfileFacts | _ProfileHold) -> Probe:
    if isinstance(profile, _ProfileHold):
        return Probe("fulltext-sync", profile.result, profile.reason)
    # prefs.js stores only non-defaults: an absent key is Zotero's shipped
    # default, which this probe did not observe and does not assert.
    enabled = profile.prefs.get("extensions.zotero.sync.fulltext.enabled", _UNSET)
    protocol = profile.prefs.get("extensions.zotero.sync.storage.protocol", _UNSET)
    return Probe(
        "fulltext-sync",
        Result.MATCHED,
        f"sync.fulltext.enabled={enabled} storage.protocol={protocol}",
    )


_BBT_GIT = addons.BBT_PREFIX + "git"
_GIT_RISK = "Better BibTeX may run git inside an export target"
_ZOTERO_SECTION = re.compile(r"^\s*\[zotero\b", re.IGNORECASE | re.MULTILINE)
# Ruling 1's roster as vault-relative prefixes a Better BibTeX export must not target.
_MACHINE_FOLDERS = (
    "literature/",
    "wiki/",
    "log/",
    "fulltext/",
    "system/propagations/",
    "log.md",
    "inbox/review-queue.md",
    "system/bibliography.json",
)
_WINDOWS_PATH = re.compile(r"^[A-Za-z]:[\\/]|^\\\\")


def _shown(value: str) -> str:
    """A prefs.js literal as a reason shows it: a string without its quotes."""
    if value.startswith('"'):
        try:
            decoded = json.loads(value)
        except ValueError:
            return value
        if isinstance(decoded, str):
            return decoded
    return value


def _names_key(lines: tuple[str, ...], key: str, key_prefix: str | None) -> bool:
    return any(addons.line_names_key(line, (key,), key_prefix) for line in lines)


def _bbt_git_probe(profile: _ProfileFacts | _ProfileHold, vault: Path) -> Probe:
    """`git` resolved through the key prefix (spec §6.1): `off` passes, `config`
    passes only when the vault's .git/config holds no Better BibTeX opt-in."""
    if isinstance(profile, _ProfileHold):
        return Probe("bbt-git", profile.result, profile.reason)
    if _BBT_GIT not in profile.prefs and _names_key(
        profile.unreadable, _BBT_GIT, addons.BBT_PREFIX
    ):
        return Probe(
            "bbt-git", Result.UNREACHABLE, f"prefs.js line naming {_BBT_GIT} unreadable"
        )
    defaults: dict[str, str] = {}
    if _BBT_GIT not in profile.prefs:  # a known prefs.js value needs no default
        try:
            defaults = addons.xpi_defaults(
                profile.path,
                addons.BBT_ID,
                keys=(_BBT_GIT,),
                key_prefix=addons.BBT_PREFIX,
            )
        except addons.DefaultsUnreadableError as error:
            return Probe(
                "bbt-git",
                Result.UNREACHABLE,
                f"Better BibTeX defaults unreadable: {error}",
            )
    value = addons.effective_value(profile.prefs, defaults, _BBT_GIT, addons.BBT_PREFIX)
    if value == "unset":
        return Probe("bbt-git", Result.MATCHED, "git unset")
    if value == '"off"':
        return Probe("bbt-git", Result.MATCHED, "git=off")
    if value == '"config"':
        # The opt-in's key name is measured in Task 4; until then any [zotero]
        # section counts as one.
        try:
            config = (vault / ".git" / "config").read_text(encoding="utf-8")
        except FileNotFoundError:
            config = ""
        except (OSError, UnicodeError) as error:
            return Probe(
                "bbt-git", Result.UNREACHABLE, f".git/config unreadable: {error}"
            )
        if not _ZOTERO_SECTION.search(config):
            return Probe(
                "bbt-git",
                Result.MATCHED,
                "git=config, no Better BibTeX opt-in in .git/config",
            )
    return Probe(
        "bbt-git",
        Result.UNMATCHED,
        f"git={_shown(value)} — {_GIT_RISK}",
        facts=((addons.BBT_ID, ("git not accepted",)),),
    )


def _export_targets_vault(export: dict, vault: Path) -> str | None:
    """The vault-relative machine path a Better BibTeX auto-export writes, if any
    (spec §6.2; Windows paths through `paths.to_local`).

    Only a path outside the vault, or a relative POSIX path (never resolved
    against the cwd), is no hit. A path that cannot be resolved raises
    `paths.PathError`: an outage, never a pass (DP47).
    """
    raw = export.get("path")
    if not isinstance(raw, str) or not raw:
        return None
    try:
        if _WINDOWS_PATH.match(raw):
            # Windows reads `/` as a separator too; path_map keys use `\\`.
            local = paths.to_local(raw.replace("/", "\\"), vault)
        else:
            local = Path(raw)
            if not local.is_absolute():
                return None
        target, root = local.resolve(), vault.resolve()
    # AttributeError/TypeError: machine.json parses but path_map has the wrong
    # shape, as the path-shim probe reads it.
    except (paths.PathError, OSError, ValueError, AttributeError, TypeError) as error:
        raise paths.PathError(f"{raw!r}: {error}") from error
    try:
        relative = target.relative_to(root).as_posix()
    except ValueError:
        return None
    for entry in _MACHINE_FOLDERS:
        if relative == entry or (entry.endswith("/") and relative.startswith(entry)):
            return relative
    return None


def _addon_state(seen: dict | None) -> str:
    if seen is None:
        return "missing"
    if seen["appDisabled"]:
        return "appDisabled"
    if not seen["active"]:
        return "inactive"
    return "active"


def _setting_findings(profile: _ProfileFacts, addon, settings):
    """(facts, unreachable) for one active add-on's declared settings."""
    facts: list[tuple[str, str]] = []  # (hashable fact, shown)
    unreachable: list[str] = []
    keys = tuple(setting.pref for setting in settings)
    defaults: dict[str, str] | None
    defaults_error = ""
    try:
        defaults = addons.xpi_defaults(
            profile.path, addon.addon_id, keys=keys, key_prefix=addon.key_prefix
        )
    except addons.DefaultsUnreadableError as error:
        defaults, defaults_error = None, str(error)
    for setting in settings:
        if setting.pref not in profile.prefs:
            if _names_key(profile.unreadable, setting.pref, addon.key_prefix):
                unreachable.append(
                    f"{addon.name}: prefs.js line naming {setting.pref} unreadable"
                )
                continue
            if defaults is None:
                unreachable.append(
                    f"{addon.name}: {setting.pref} needs the shipped default and "
                    f"{defaults_error}"
                )
                continue
        value = addons.effective_value(
            profile.prefs, defaults or {}, setting.pref, addon.key_prefix
        )
        if not addons.accepts(setting.accepted, value):
            accepted = ", ".join(setting.accepted)
            # the hashed fact keys off the setting, never its value (DP46)
            facts.append(
                (
                    f"{setting.pref} not accepted ({accepted})",
                    f"{setting.pref}={value} (accepted {accepted})",
                )
            )
    return facts, unreachable


def _grouped(
    found: list[tuple[str, str, str]],
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """(id, fact, shown) entries as one facts entry per component id (DP24)."""
    by_id: dict[str, list[str]] = {}
    for addon_id, fact, _shown_text in found:
        by_id.setdefault(addon_id, []).append(fact)
    return tuple((addon_id, tuple(facts)) for addon_id, facts in by_id.items())


def _plugins_probe(profile: _ProfileFacts | _ProfileHold, vault: Path) -> Probe:
    """Required add-ons active, the minimum versions, every active add-on's
    effective value accepted, no Better BibTeX auto-export into the vault
    (spec §6.1, §6.2). A failure outranks an outage."""
    if isinstance(profile, _ProfileHold):
        return Probe("plugins", profile.result, profile.reason)
    try:
        observed = addons.observe(profile.path)
    except OSError as error:
        return Probe(
            "plugins", Result.UNREACHABLE, f"extensions.json unreadable: {error}"
        )
    except (UnicodeError, ValueError, KeyError, AttributeError, TypeError) as error:
        return Probe("plugins", Result.UNMATCHED, f"extensions.json malformed: {error}")
    try:
        declaration = addons.declared()
    except (OSError, ValueError) as error:
        return Probe(
            "plugins", Result.UNMATCHED, f"add-on declaration malformed: {error}"
        )
    found: list[tuple[str, str, str]] = []  # (addon id, hashable fact, shown)
    unreachable: list[str] = []
    notes_out: list[str] = []
    for addon in declaration.addons:
        if addon.need == "excluded":
            continue
        seen = observed.get(addon.addon_id)
        state = _addon_state(seen)
        notes_out.append(f"{addon.addon_id} {state}")
        if addon.need == "required" and state != "active":
            found.append((addon.addon_id, state, state))
        if seen is None or state != "active":
            continue
        if addon.min_version:
            version = seen["version"] or ""
            at_least = addons.version_at_least(version, addon.min_version)
            floor = addon.min_version
            if at_least is None:
                found.append(
                    (
                        addon.addon_id,
                        f"version unreadable against floor {floor}",
                        f"version {seen['version']!r} unreadable against floor {floor}",
                    )
                )
            elif not at_least:
                found.append(
                    (addon.addon_id, f"below {floor}", f"{version} below {floor}")
                )
        settings = declaration.settings_for(addon.addon_id)
        if settings:
            facts, lost = _setting_findings(profile, addon, settings)
            found.extend((addon.addon_id, fact, shown) for fact, shown in facts)
            unreachable.extend(lost)
    notes_out.extend(
        f"{addon_id} undeclared"
        for addon_id in sorted(set(observed) - set(declaration.by_id))
    )
    try:
        exports = addons.bbt_auto_exports(profile.prefs)
    except ValueError as error:
        exports = []
        unreachable.append(f"Better BibTeX auto-export unreadable: {error}")
    for export in exports:
        try:
            hit = _export_targets_vault(export, vault)
        except paths.PathError as error:
            unreachable.append(f"Better BibTeX auto-export path unresolvable: {error}")
            continue
        if hit is not None:
            fact = f"auto-export targets {hit}"
            found.append((addons.BBT_ID, fact, fact))
    if found:
        shown = "; ".join(
            f"{declaration.by_id[addon_id].name} {text}" for addon_id, _f, text in found
        )
        return Probe("plugins", Result.UNMATCHED, shown, facts=_grouped(found))
    if unreachable:
        return Probe("plugins", Result.UNREACHABLE, "; ".join(unreachable))
    return Probe("plugins", Result.MATCHED, "; ".join(notes_out))


def _excluded_obsidian_plugins(vault: Path, config: dict) -> list[tuple[str, str, str]]:
    """Enabled Obsidian plugins the declaration excludes (Plan E deviation 5).
    A folder that is absent or will not read is the `obsidian` row's to name."""
    _name, folder = _obsidian_folder(vault, config)
    try:
        enabled = _enabled_obsidian_plugins(folder)
        declaration = obsidian_plugins.declared()
    except (OSError, ValueError, _ConfigMisshapenError):
        return []
    fact = "enabled (excluded Obsidian plugin)"
    return [
        (plugin.plugin_id, fact, f"{plugin.name} {fact}")
        for plugin in declaration.plugins
        if plugin.need == "excluded" and plugin.plugin_id in enabled
    ]


def _advisory_probe(
    profile: _ProfileFacts | _ProfileHold, vault: Path, config: dict
) -> Probe:
    """Warn-only (#191, Q14; R40): a recommended add-on Zotero refuses to load,
    an add-on excluded on harm grounds that is active, and an excluded
    Obsidian plugin that is enabled (R38). A required add-on's fault stays
    the plugins row's (DP26); the Obsidian fact stands whatever the profile."""
    obsidian = _excluded_obsidian_plugins(vault, config)
    zotero = _advisory_addons(profile)
    if isinstance(zotero, Probe):
        if not obsidian:
            return zotero
        found = obsidian
        held = f"; {zotero.reason}"
    else:
        found = [
            *((addon_id, fact, f"{name} {fact}") for addon_id, name, fact in zotero),
            *obsidian,
        ]
        held = ""
    if found:
        shown = "; ".join(text for _id, _fact, text in found) + held
        return Probe("advisory", Result.UNMATCHED, shown, facts=_grouped(found))
    return Probe(
        "advisory",
        Result.MATCHED,
        "no appDisabled recommended add-on, no active excluded add-on, "
        "no enabled excluded Obsidian plugin",
    )


def _advisory_addons(
    profile: _ProfileFacts | _ProfileHold,
) -> list[tuple[str, str, str]] | Probe:
    """(id, name, fact) for each Zotero add-on advisory warns on, or the row a
    held profile or the plugins row's fault leaves."""
    if isinstance(profile, _ProfileHold):
        return Probe("advisory", profile.result, profile.reason)
    try:
        observed = addons.observe(profile.path)
        declaration = addons.declared()
    except (
        OSError,
        UnicodeError,
        ValueError,
        KeyError,
        AttributeError,
        TypeError,
    ) as error:
        return Probe(
            "advisory", Result.SKIPPED, f"plugins row carries the fault: {error}"
        )
    found: list[tuple[str, str, str]] = []
    for addon in declaration.addons:
        seen = observed.get(addon.addon_id)
        if seen is None:
            continue
        if addon.need == "recommended" and seen["appDisabled"]:
            found.append((addon.addon_id, addon.name, f"appDisabled ({addon.need})"))
        elif addon.need == "excluded" and seen["active"]:
            found.append(
                (addon.addon_id, addon.name, "active (excluded on harm grounds)")
            )
    return found


def _is_stored_file(row) -> bool:
    return (
        isinstance(row, dict)
        and isinstance(row.get("key"), str)
        and isinstance(row.get("data"), dict)
        and row["data"].get("linkMode") == "imported_file"
    )


def _first_stored_attachment(client) -> str | Probe:
    """The oldest stored attachment's key, or the path-shim row to report instead.

    The listing is walked fifty rows at a time, oldest first, stopping at the
    first ``imported_file`` and capped at twenty pages. Measured 2026-09-13 on
    both instances: the route honours ``sort=dateAdded&direction=asc`` (dates
    non-decreasing within and across pages, order stable across reads), so the
    walk meets the same file on every run as the library grows; the unpaged
    read answered in 22 s on 1,372 rows against the client's 5 s timeout; a
    page answers in under half a second. The local API ignores a ``linkMode``
    query filter (measured 2026-09-07, decision 25), hence the client-side test.
    """
    inspected = 0
    total: str | None = None
    for page in range(_MAX_PAGES):
        path = _ATTACHMENT_PAGE.format(start=page * _PAGE_SIZE)
        try:
            payload, headers = client._local_json(path)
        except ZoteroError as error:
            return Probe(
                "path-shim", Result.UNREACHABLE, f"attachment listing: {error}"
            )
        if not isinstance(payload, list):
            return Probe(
                "path-shim",
                Result.UNMATCHED,
                "attachment listing malformed: expected a list",
            )
        if page == 0:
            reported = header(headers, "Total-Results")
            total = (
                reported if isinstance(reported, str) and reported.isdigit() else None
            )
        inspected += len(payload)
        for row in payload:
            if _is_stored_file(row):
                return str(row["key"])
        if len(payload) < _PAGE_SIZE:
            break  # the listing ended before the cap
    span = f"of {total}" if total is not None else "(total unreported)"
    # nothing to check is not an outage; the reason says what span was read
    return Probe(
        "path-shim",
        Result.SKIPPED,
        f"no stored attachment among the first {inspected} {span}",
    )


def _path_shim_probe(client, skip: str | None, vault: Path) -> Probe:
    if not paths._running_in_wsl():
        return Probe("path-shim", Result.SKIPPED, "not running in WSL")
    if skip:
        return Probe("path-shim", Result.SKIPPED, skip)
    found = _first_stored_attachment(client)
    if isinstance(found, Probe):
        return found
    key = found
    try:
        url = client.file_view_url(key)
    except ZoteroError as error:
        return Probe("path-shim", Result.UNREACHABLE, f"file URL for {key}: {error}")
    if not url:
        # the server's two definite negatives (404, 400) for a row it listed as stored
        return Probe(
            "path-shim", Result.SKIPPED, f"stored attachment {key} has no file URL"
        )
    if _WINDOWS_FILE_URL.match(url) is None:
        # The Part A plan's decision 10: the shim resolves Windows file URLs
        # only. A POSIX URL is reported, not unwound through wslpath.
        return Probe(
            "path-shim",
            Result.SKIPPED,
            f"file URL is not a Windows path; the shim resolves Windows file "
            f"URLs only: {url}",
        )
    windows_path = urllib.parse.unquote(url.removeprefix("file:///")).replace("/", "\\")
    try:
        local = paths.to_local(windows_path, vault)
    except (paths.PathError, OSError, ValueError, AttributeError, TypeError) as error:
        # to_local re-reads machine.json without machine-config's shape checks: a
        # malformed file raises ValueError/OSError, a non-object path_map or a
        # non-string entry AttributeError/TypeError. All are setup faults, not outages.
        return Probe(
            "path-shim",
            Result.UNMATCHED,
            f"machine.json path_map: {type(error).__name__}: {error}",
        )
    if local.is_file():
        return Probe("path-shim", Result.MATCHED, str(local))
    return Probe("path-shim", Result.UNMATCHED, f"{local} does not exist")


def _translator_formats_probe(client, skip: str | None) -> Probe:
    if skip:
        return Probe("translator-formats", Result.SKIPPED, skip)
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


def _compile_mode(vault: Path) -> tuple[str, str | None]:
    """The compile tool's mode as (shown, fact): absent `.vault-meta/mode.json`
    is generic (`wiki-mode.py:12` @32ac5a0), and so is a file without a `mode`
    key (`loaded.get("mode", "generic")`, `wiki-mode.py:156,160`); fact is None
    when generic, and never names the mode found (DP34)."""
    path = vault / ".vault-meta" / "mode.json"
    try:
        mode = json.loads(path.read_text(encoding="utf-8")).get("mode", "generic")
    except FileNotFoundError:
        return "mode generic (no .vault-meta/mode.json)", None
    except (OSError, UnicodeError, ValueError, AttributeError):
        return "mode.json unreadable", "mode.json unreadable"
    if mode == "generic":
        return "mode generic", None
    shown = mode if isinstance(mode, str) else json.dumps(mode)
    return (
        f"mode {shown}, the vault runs generic (CONTEXT.md's paths)",
        "mode not generic",
    )


def _compile_tool_probe(vault: Path) -> Probe:
    """The compile tool at its pin, and the vault's mode (#161): both findings
    share the one cell (assembly §9's accepted defect). An UNMATCHED row's
    facts name the pin and generic, never the installed sha or the mode
    found (DP34): a move between two wrong values re-fires nothing."""
    records = _installed_plugins().get(_COMPILE_PLUGIN)
    record = records[0] if isinstance(records, list) and records else None
    if not isinstance(record, dict):
        return Probe("compile-tool", Result.SKIPPED, f"{_COMPILE_PLUGIN} not installed")
    sha = str(record.get("gitCommitSha") or "")
    mode, mode_fact = _compile_mode(vault)
    facts = [] if sha.startswith(_COMPILE_PIN) else [f"off pin {_COMPILE_PIN}"]
    if mode_fact is not None:
        facts.append(mode_fact)
    if sha.startswith(_COMPILE_PIN):
        pin = f"{_COMPILE_PLUGIN} at {sha[:7]}"
    elif not sha:
        pin = f"{_COMPILE_PLUGIN} record has no gitCommitSha, pin is {_COMPILE_PIN}"
    else:
        pin = f"{_COMPILE_PLUGIN} at {sha[:7]}, pin is {_COMPILE_PIN}"
    if not facts:
        return Probe("compile-tool", Result.MATCHED, f"{pin}; {mode}")
    return Probe(
        "compile-tool",
        Result.UNMATCHED,
        f"{pin}; {mode}",
        facts=((_COMPILE_PLUGIN, tuple(facts)),),
    )


def _obsidian_folder(vault: Path, config: dict) -> tuple[str, Path]:
    """The configured Obsidian folder (`obsidian_config_dir`, default `.obsidian`)."""
    configured = config.get("obsidian_config_dir")
    name = (
        configured.strip()
        if isinstance(configured, str) and configured.strip()
        else ".obsidian"
    )
    return name, vault / name


class _ConfigMisshapenError(Exception):
    """A config file that parses but is not the JSON type Obsidian writes: no
    re-read clears it, so it is a finding, not an outage."""

    def __init__(self, relative: str, shape: type):
        super().__init__(f"{relative} malformed (expected a JSON {shape.__name__})")
        parts = relative.split("/")
        self.component = parts[1] if parts[0] == "plugins" else "core"


def _config_json(folder: Path, relative: str, shape: type):
    """A config file's JSON, or None when absent; an unparseable file raises
    `ConfigUnreadableError` and a misshapen one `_ConfigMisshapenError`, each
    naming the file."""
    try:
        document = json.loads((folder / relative).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError, ValueError) as error:
        raise obsidian_plugins.ConfigUnreadableError(f"{relative}: {error}") from error
    if not isinstance(document, shape):
        raise _ConfigMisshapenError(relative, shape)
    return document


def _enabled_obsidian_plugins(folder: Path) -> set[str]:
    enabled = _config_json(folder, "community-plugins.json", list) or []
    return {plugin_id for plugin_id in enabled if isinstance(plugin_id, str)}


def _obsidian_probe(vault: Path, config: dict) -> Probe:
    """Spec §6.3: cold reads of the configured Obsidian folder against the
    packaged declaration. UNMATCHED only for a declared key off its values on
    an enabled plugin (or Core); an unparseable file is UNREACHABLE (Obsidian
    rewrites them non-atomically), one of the wrong JSON type UNMATCHED (no
    re-read clears it); drift from the seed is a note; an absent
    folder is SKIPPED. An enabled excluded plugin is a note here and an
    `advisory` fact (Plan E deviation 5)."""
    name, folder = _obsidian_folder(vault, config)
    if not folder.is_dir():
        return Probe("obsidian", Result.SKIPPED, f"{name} absent")
    try:
        declaration = obsidian_plugins.declared()
    except (OSError, ValueError) as error:
        return Probe(
            "obsidian", Result.UNMATCHED, f"plugin declaration malformed: {error}"
        )
    seed = _OBSIDIAN_SEED.joinpath("core-plugins.json").read_text(encoding="utf-8")
    seed_core = json.loads(seed)
    found: list[tuple[str, str, str]] = []  # (component, hashable fact, shown)
    notes_out: list[str] = []
    try:
        enabled = _enabled_obsidian_plugins(folder)
        core = _config_json(folder, "core-plugins.json", dict) or {}
        for core_id, value in sorted(core.items()):
            if core_id in seed_core and seed_core[core_id] != value:
                notes_out.append(
                    f"core-plugins.json drifts: {core_id}={json.dumps(value)}"
                )
        for plugin in declaration.plugins:
            manifest = f"plugins/{plugin.plugin_id}/manifest.json"
            if plugin.need == "excluded":
                if plugin.plugin_id in enabled:
                    notes_out.append(f"excluded plugin {plugin.plugin_id} enabled")
                continue
            if plugin.need == "recommended":
                # presence only: no declared key reads a recommended manifest
                if (folder / manifest).is_file():
                    notes_out.append(f"recommended plugin {plugin.plugin_id} installed")
                continue
            installed = _config_json(folder, manifest, dict)
            if installed is None:
                continue
            if installed.get("version") != plugin.pin:
                notes_out.append(
                    f"{plugin.plugin_id} pinned {plugin.pin}, "
                    f"installed {installed.get('version')}"
                )
        for setting in declaration.settings:
            if setting.plugin == obsidian_plugins.CORE:
                component, relative = "core", setting.file
            else:
                plugin_id = declaration.by_name[setting.plugin].plugin_id
                if plugin_id not in enabled:
                    continue
                component, relative = plugin_id, f"plugins/{plugin_id}/{setting.file}"
            try:
                value = obsidian_plugins.read_key(folder / relative, setting.key)
            except obsidian_plugins.ConfigUnreadableError as error:
                # read_key names the file's basename; name it from the folder
                raise obsidian_plugins.ConfigUnreadableError(
                    f"{relative}: {error.__cause__}"
                ) from error
            if value not in setting.accepted:
                accepted = ", ".join(setting.accepted)
                # the hashed fact keys off the setting, never its value (DP46)
                found.append(
                    (
                        component,
                        f"{setting.file} {setting.key} not accepted ({accepted})",
                        f"{setting.file} {setting.key}={value} (accepted {accepted})",
                    )
                )
    except obsidian_plugins.ConfigUnreadableError as error:
        return Probe(
            "obsidian",
            Result.UNREACHABLE,
            f"{name}: config unreadable, read again: {error}",
        )
    except _ConfigMisshapenError as error:
        found = [(error.component, str(error), str(error))]
    names = {"core": obsidian_plugins.CORE}
    names.update((p.plugin_id, p.name) for p in declaration.plugins)
    if found:
        shown = "; ".join(f"{names[c]} {text}" for c, _fact, text in found)
        return Probe("obsidian", Result.UNMATCHED, shown, facts=_grouped(found))
    detail = (
        "; ".join(notes_out)
        if notes_out
        else "every declared key holds; no drift from the seed"
    )
    return Probe("obsidian", Result.MATCHED, f"{name}: {detail}")


_OBSIDIAN_SEED = resources.files("research_vault").joinpath("templates", "obsidian")


def _bbt_probe(client, zotero_probe: Probe) -> Probe:
    """Asked whatever the local-API preference: `/better-bibtex/json-rpc` ignores it (§9)."""
    try:
        versions = client.ready()
    except (ZoteroError, OSError, UnicodeError, ValueError) as error:
        if zotero_probe.result is Result.UNREACHABLE:
            return Probe("bbt", Result.UNREACHABLE, f"zotero down: {error}")
        # Zotero answered /api/, so a json-rpc failure is Better BibTeX's, not the
        # transport's: _rpc types a non-200 (404 when it is not installed) as a
        # plain ZoteroError and cannot tell the two apart; the zotero row already has.
        return Probe(
            "bbt", Result.UNMATCHED, f"Better BibTeX not answering json-rpc: {error}"
        )
    bbt_version = versions.get("betterbibtex")
    if not isinstance(bbt_version, str) or not bbt_version.strip():
        return Probe("bbt", Result.UNMATCHED, "Better BibTeX version missing")
    return Probe("bbt", Result.MATCHED, bbt_version.strip())


def _pyyaml_probe() -> Probe:
    """The OKF reader's dependency (#194, §5.6): `verify` exits 4 without it."""
    try:
        import yaml
    except ImportError:
        return Probe(
            "pyyaml",
            Result.UNMATCHED,
            "PyYAML is not importable — verify exits 4 and the commit hook refuses; "
            "pip install PyYAML into the environment that runs research_vault",
        )
    loader = "C" if hasattr(yaml, "CSafeLoader") else "pure"
    return Probe(
        "pyyaml", Result.MATCHED, f"PyYAML {yaml.__version__} ({loader} loader)"
    )


# The guard's roster, repeated here only for a pip install that has no hooks/
# beside the package; `tests/test_templates.py` pins this copy against the
# guard's constants so the two cannot drift.
_ROSTER_DIR_NAMES = ("literature", "log", "wiki", "fulltext")
_ROSTER_PREFIXES = ("system/propagations",)
_ROSTER_FILES = (
    "log.md",
    "inbox/review-queue.md",
    "system/bibliography.json",
    "system/compiled-pages.json",
)


def expected_deny_rules() -> list[str]:
    """The guard's roster as Claude Code deny rules (spec §5.7): one source, the
    guard file when it is beside the package, the pinned copy otherwise."""
    import importlib.util

    guard_path = Path(__file__).resolve().parents[1] / "hooks" / "pretooluse_guard.py"
    dir_names, prefixes, files = _ROSTER_DIR_NAMES, _ROSTER_PREFIXES, _ROSTER_FILES
    if guard_path.is_file():
        spec = importlib.util.spec_from_file_location("pretooluse_guard", guard_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {guard_path}")
        guard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guard)
        dir_names = tuple(guard.MACHINE_SURFACE_DIR_NAMES)
        prefixes = tuple(p.as_posix() for p in guard.MACHINE_SURFACE_PREFIXES)
        files = tuple(p.as_posix() for p in guard.MACHINE_SURFACE_FILES)
    return sorted(
        [f"Edit(/{name}/**)" for name in dir_names]
        + [f"Edit(/{prefix}/**)" for prefix in prefixes]
        + [f"Edit(/{path})" for path in files]
    )


def _deny_rules_probe(vault: Path) -> Probe:
    """The seeded `.claude/settings.json` deny list against the roster (§5.7)."""
    settings = vault / ".claude" / "settings.json"
    if not settings.is_file():
        return Probe(
            "deny-rules",
            Result.SKIPPED,
            ".claude/settings.json absent — scaffold seeds it",
        )
    try:
        document = json.loads(settings.read_text(encoding="utf-8"))
        deny = document["permissions"]["deny"]
        if not isinstance(deny, list):
            raise ValueError("permissions.deny is not a list")
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
        return Probe(
            "deny-rules", Result.UNMATCHED, f".claude/settings.json unreadable: {error}"
        )
    expected = expected_deny_rules()
    present = {
        rule for rule in deny if isinstance(rule, str) and rule.startswith("Edit(")
    }
    missing = sorted(set(expected) - present)
    if not missing:
        # R43: a person's own Edit rules beside the roster are theirs to keep.
        return Probe(
            "deny-rules",
            Result.MATCHED,
            f"{len(expected)} Edit deny rules equal the guard's roster"
            if present == set(expected)
            else f"the guard's {len(expected)} Edit deny rules are all present",
        )
    extra = present - set(expected)
    # W11: a rule that is not UTF-8 text (a lone surrogate JSON allows) would
    # crash the print, so it is counted, never shown.
    shown = sorted(rule for rule in extra if structure._is_plain_text(rule))
    hidden = len(extra) - len(shown)
    parts = [f"missing {rule}" for rule in missing] + [
        f"extra {rule}" for rule in shown
    ]
    if hidden:
        parts.append(
            f"extra {hidden} rule{' that is' if hidden == 1 else 's that are'} "
            "not UTF-8 text"
        )
    return Probe("deny-rules", Result.UNMATCHED, "; ".join(parts))


# The network-free, repair-free probes capture runs after every successful run
# (spec §6.4, Q13): the component rows. `tree` repairs, the Zotero rows need
# the app; `pyyaml`, `deny-rules`, `machine-config`, `remote` and `backup`
# are setup facts, not components (DP40).
COMPONENT_PROBES = (
    "fulltext-sync",
    "bbt-git",
    "plugins",
    "advisory",
    "compile-tool",
    "obsidian",
)


def cold_rows(vault_root) -> list[Probe]:
    """The component probes alone: no network client, no repair; reads
    ``machine.json`` and the profile cold."""
    vault = Path(vault_root)
    config, _machine = _machine_config(vault)
    profile = _profile_facts(config)
    probes = (
        ("fulltext-sync", lambda: _fulltext_sync_probe(profile)),
        ("bbt-git", lambda: _bbt_git_probe(profile, vault)),
        ("plugins", lambda: _plugins_probe(profile, vault)),
        ("advisory", lambda: _advisory_probe(profile, vault, config)),
        ("compile-tool", lambda: _compile_tool_probe(vault)),
        ("obsidian", lambda: _obsidian_probe(vault, config)),
    )
    return [_guarded(check, probe) for check, probe in probes]


def _guarded(check: str, probe) -> Probe:
    """One cold row that cannot end the capture that runs it: a probe that
    raises is that probe's UNMATCHED row, its fact the exception's type alone
    (stable across messages), its message in the reason."""
    try:
        return probe()
    except Exception as error:
        fact = f"probe raised {type(error).__name__}"
        # `_make`, not `Probe(...)`: the probe-id scan in tests/test_doctor.py
        # reads literal ids off `Probe(` calls, and this row's id is each
        # guarded probe's own; its result is UNMATCHED, never UNREACHABLE.
        return Probe._make(
            (check, Result.UNMATCHED, f"{fact}: {error}", ((check, (fact,)),))
        )


def doctor(vault_root, client=None) -> list[Probe]:
    """Repair the scoped vault substrate and return its ordered probes (§5)."""
    vault = Path(vault_root)
    tree = _tree_probe(vault)
    config, machine = _machine_config(vault)
    client = ZoteroClient() if client is None else client
    zotero_probe = _zotero_probe(client)
    skip = _local_api_skip(zotero_probe)
    profile = _profile_facts(config)
    return [
        tree,
        machine,
        zotero_probe,
        _write_guard_probe(client, skip),
        _fulltext_sync_probe(profile),
        _bbt_probe(client, zotero_probe),
        _bbt_git_probe(profile, vault),
        _plugins_probe(profile, vault),
        _advisory_probe(profile, vault, config),
        _path_shim_probe(client, skip, vault),
        _translator_formats_probe(client, skip),
        _compile_tool_probe(vault),
        _obsidian_probe(vault, config),
        _pyyaml_probe(),
        _deny_rules_probe(vault),
        _remote_probe(vault),
        _backup_probe(config),
    ]
