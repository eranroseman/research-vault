"""The Zotero add-on declaration doctor reads (decomposition decision 17, §6.1)."""

import json
import re
from importlib import resources
from pathlib import Path
from typing import NamedTuple

_ROW = re.compile(
    r"^\|\s*(?P<name>[^|]+?)\s*"
    r"\|\s*`(?P<id>[^`]+)`\s*"
    r"\|\s*(?P<need>required|recommended|optional)\s*"
    r"\|\s*(?:`(?P<pref>[^`]+)`)?\s*\|$"
)
_PREF = re.compile(r'^user_pref\("(?P<name>[^"]+)",\s*(?P<value>.+)\);$')


class Addon(NamedTuple):
    name: str
    addon_id: str
    need: str
    auto_pref: str | None


def declared() -> list[Addon]:
    text = (
        resources.files("research_vault")
        .joinpath("templates/zotero-addons.md")
        .read_text(encoding="utf-8")
    )
    rows = []
    for line in text.splitlines():
        match = _ROW.match(line.strip())
        if match:
            rows.append(
                Addon(
                    match.group("name"),
                    match.group("id"),
                    match.group("need"),
                    match.group("pref"),
                )
            )
    return rows


def observe(profile_dir: Path) -> dict[str, dict]:
    """`active` and `appDisabled` from the running Zotero's extensions.json — never the manifest cap."""
    data = json.loads(
        (Path(profile_dir) / "extensions.json").read_text(encoding="utf-8")
    )
    observed = {}
    for addon in data.get("addons", []):
        if addon.get("type") != "extension" or addon.get("location") != "app-profile":
            continue
        observed[addon["id"]] = {
            "version": addon.get("version"),
            "active": bool(addon.get("active")),
            "appDisabled": bool(addon.get("appDisabled")),
        }
    return observed


def read_prefs(profile_dir: Path) -> dict[str, str | bool | int]:
    prefs: dict[str, str | bool | int] = {}
    for line in (
        (Path(profile_dir) / "prefs.js").read_text(encoding="utf-8").splitlines()
    ):
        match = _PREF.match(line.strip())
        if not match:
            continue
        raw = match.group("value").strip()
        value: str | bool | int
        if raw in {"true", "false"}:
            value = raw == "true"
        elif raw.lstrip("-").isdigit():
            value = int(raw)
        else:
            value = _string_pref(raw)
        prefs[match.group("name")] = value
    return prefs


def _string_pref(raw: str) -> str:
    """A quoted token as JSON reads it; the token itself when JSON refuses it.

    prefs.js is JavaScript, so a build may escape a string in a way JSON does
    not accept. One such line must not fail the whole file.
    """
    if not raw.startswith('"'):
        return raw
    try:
        decoded = json.loads(raw)
    except ValueError:
        return raw
    return decoded if isinstance(decoded, str) else raw
