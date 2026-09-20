"""The doctor: repair the scoped vault substrate, then thirteen ordered probes (assembly spec §9).

Scaffolding (`scaffold.py`) creates and commits; this module observes. It
calls only `scaffold_vault`, `VAULT_DIRS` and `_git` from the other side.
"""

import json
import re
import subprocess
import urllib.parse
from pathlib import Path
from typing import NamedTuple

from . import Result, addons, paths
from .scaffold import VAULT_DIRS, _git, scaffold_vault
from .zotero import LocalApiDisabledError, ZoteroClient, ZoteroError, header


class Probe(NamedTuple):
    """One doctor row, in the Outcome vocabulary (check/result/reason)."""

    check: str
    result: Result
    reason: str


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
    """A readable zotero_profile directory and its prefs.js."""

    path: Path
    prefs: dict[str, str | bool | int]


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
    if not path.is_dir():
        return _ProfileHold(
            Result.UNMATCHED, f"zotero_profile {path} is not a directory"
        )
    try:
        prefs = addons.read_prefs(path)
    except OSError as error:
        return _ProfileHold(Result.UNREACHABLE, f"prefs.js unreadable: {error}")
    except (UnicodeError, ValueError) as error:
        return _ProfileHold(Result.UNMATCHED, f"prefs.js unparseable: {error}")
    return _ProfileFacts(path, prefs)


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


def _bbt_git_probe(profile: _ProfileFacts | _ProfileHold) -> Probe:
    if isinstance(profile, _ProfileHold):
        return Probe("bbt-git", profile.result, profile.reason)
    value = profile.prefs.get("extensions.zotero.translators.better-bibtex.git", "off")
    if value == "off":
        return Probe("bbt-git", Result.MATCHED, "git=off")
    return Probe(
        "bbt-git",
        Result.UNMATCHED,
        f"git={value} — Better BibTeX may run git inside an export target",
    )


def _plugins_probe(profile: _ProfileFacts | _ProfileHold) -> Probe:
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
        declared = addons.declared()
    except (OSError, ValueError) as error:
        return Probe(
            "plugins", Result.UNMATCHED, f"add-on declaration malformed: {error}"
        )
    failures: list[str] = []
    notes_out: list[str] = []
    for addon in declared:
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
            and profile.prefs.get(addon.auto_pref) is not True
        ):
            failures.append(f"{addon.name} automatic mode off ({addon.auto_pref})")
    if failures:
        return Probe("plugins", Result.UNMATCHED, "; ".join(failures))
    return Probe("plugins", Result.MATCHED, "; ".join(notes_out))


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


def _compile_tool_probe() -> Probe:
    records = _installed_plugins().get(_COMPILE_PLUGIN)
    record = records[0] if isinstance(records, list) and records else None
    if not isinstance(record, dict):
        return Probe("compile-tool", Result.SKIPPED, f"{_COMPILE_PLUGIN} not installed")
    sha = str(record.get("gitCommitSha") or "")
    if not sha:
        return Probe(
            "compile-tool",
            Result.UNMATCHED,
            f"{_COMPILE_PLUGIN} record has no gitCommitSha, pin is {_COMPILE_PIN}",
        )
    if sha.startswith(_COMPILE_PIN):
        return Probe("compile-tool", Result.MATCHED, f"{_COMPILE_PLUGIN} at {sha[:7]}")
    return Probe(
        "compile-tool",
        Result.UNMATCHED,
        f"{_COMPILE_PLUGIN} at {sha[:7]}, pin is {_COMPILE_PIN}",
    )


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


def doctor(vault_root, client=None) -> list[Probe]:
    """Repair the scoped vault substrate and return its thirteen ordered probes (§5)."""
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
        _bbt_git_probe(profile),
        _plugins_probe(profile),
        _path_shim_probe(client, skip, vault),
        _translator_formats_probe(client, skip),
        _compile_tool_probe(),
        _remote_probe(vault),
        _backup_probe(config),
    ]
