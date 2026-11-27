"""The Zotero add-on declaration doctor reads (decomposition decision 17, §6.1)."""

import json
import re
import zipfile
import zlib
from importlib import resources
from pathlib import Path
from typing import NamedTuple

NEEDS = ("required", "recommended", "optional", "excluded")
_CELL = r"\|\s*(?P<{name}>[^|]*?)\s*"
_ADDON_ROW = re.compile(
    "^"
    + "".join(
        _CELL.format(name=name)
        for name in ("name", "id", "need", "min", "prefix", "workflows")
    )
    + r"\|$"
)
_SETTING_ROW = re.compile(
    "^"
    + "".join(_CELL.format(name=name) for name in ("addon", "pref", "accepted"))
    + r"\|$"
)
_LITERAL = re.compile(r'^(?:true|false|-?\d+|"(?:[^"\\]|\\.)*"|unset)$')
_NONE = "—"
# prefs.js writes `user_pref(...);`; an .xpi's shipped defaults write
# `pref(...)`, Better BibTeX 9.0.68's without the semicolon.
_PREF = re.compile(r'^(?:user_)?pref\("(?P<name>[^"]+)",\s*(?P<value>.+?)\);?\s*$')


class Addon(NamedTuple):
    name: str
    addon_id: str
    need: str
    min_version: str | None
    key_prefix: str | None
    workflows: str


class Setting(NamedTuple):
    addon: str
    pref: str
    accepted: tuple[str, ...]


class Declaration(NamedTuple):
    addons: list[Addon]
    settings: list[Setting]

    @property
    def by_id(self) -> dict[str, Addon]:
        return {addon.addon_id: addon for addon in self.addons}

    def settings_for(self, addon_id: str) -> list[Setting]:
        name = self.by_id[addon_id].name
        return [setting for setting in self.settings if setting.addon == name]


def _code(cell: str) -> str | None:
    """A backticked cell's text; `—` or empty is None; anything else is a grammar fault."""
    if cell in {"", _NONE}:
        return None
    if cell.startswith("`") and cell.endswith("`") and len(cell) > 2:
        return cell[1:-1]
    raise ValueError(f"zotero-addons.md: unreadable row cell {cell!r}")


def _addon_row(line: str) -> Addon | None:
    """One add-ons row, None for the header row; a row it cannot read raises."""
    match = _ADDON_ROW.match(line)
    if match is None:
        raise ValueError(f"zotero-addons.md: unreadable row {line!r}")
    if match.group("name") == "Add-on":
        return None
    need = match.group("need")
    if need not in NEEDS:
        raise ValueError(f"zotero-addons.md: unreadable row {line!r} (need {need!r})")
    addon_id = _code(match.group("id"))
    if not addon_id:
        raise ValueError(f"zotero-addons.md: unreadable row {line!r} (no id)")
    minimum = match.group("min")
    return Addon(
        match.group("name"),
        addon_id,
        need,
        None if minimum in {"", _NONE} else minimum,
        _code(match.group("prefix")),
        match.group("workflows"),
    )


def _setting_row(line: str) -> Setting | None:
    """One declared-settings row, None for the header row; a row it cannot read raises."""
    match = _SETTING_ROW.match(line)
    if match is None:
        raise ValueError(f"zotero-addons.md: unreadable row {line!r}")
    if match.group("addon") == "Add-on":
        return None
    pref = _code(match.group("pref"))
    if not pref:
        raise ValueError(f"zotero-addons.md: unreadable row {line!r} (no preference)")
    accepted = tuple(
        literal
        for literal in (
            _code(part.strip()) for part in match.group("accepted").split(", ")
        )
        if literal is not None
    )
    if not accepted or any(_LITERAL.match(literal) is None for literal in accepted):
        raise ValueError(
            f"zotero-addons.md: unreadable row {line!r} (accepted literals)"
        )
    return Setting(match.group("addon"), pref, accepted)


def declared() -> Declaration:
    """The packaged declaration (decomposition decision 17, spec §6.1): two tables.

    Every `|` line under either header must parse, or this raises
    ``ValueError``: a typo must never delete a check silently. A settings row
    must name an add-on of the first table. Packaged beside the code, so a
    file that will not decode is a broken install, not a vault fault (an
    ``OSError`` for a file that cannot be opened at all passes through as
    itself); ``doctor._plugins_probe`` turns either into one ``plugins`` row.
    """
    declaration = resources.files("research_vault").joinpath(
        "templates/zotero-addons.md"
    )
    try:
        text = declaration.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"zotero-addons.md: not UTF-8: {error}") from error
    addons: list[Addon] = []
    settings: list[Setting] = []
    table = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("### "):
            table = line[4:].strip().lower()
            continue
        if not line.startswith("|") or set(line) <= {"|", "-", " "}:
            continue
        if table == "add-ons":
            addon = _addon_row(line)
            if addon is not None:
                addons.append(addon)
        elif table == "declared settings":
            setting = _setting_row(line)
            if setting is not None:
                settings.append(setting)
        else:
            raise ValueError(
                f"zotero-addons.md: a table row outside a known table: {line!r}"
            )
    names = {addon.name for addon in addons}
    for setting in settings:
        if setting.addon not in names:
            raise ValueError(
                f"zotero-addons.md: settings row names no declared add-on: {setting.addon!r}"
            )
    return Declaration(addons, settings)


def observe(profile_dir: Path) -> dict[str, dict]:
    """`active` and `appDisabled` from the running Zotero's extensions.json — never the manifest cap."""
    data = json.loads(
        (Path(profile_dir) / "extensions.json").read_text(encoding="utf-8")
    )
    observed = {}
    for addon in data.get("addons", []):
        if addon.get("type") != "extension" or addon.get("location") != "app-profile":
            continue
        version = addon.get("version")
        observed[addon["id"]] = {
            # a non-string version is unreadable, never a crash (DP48c)
            "version": version if isinstance(version, str) else None,
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


def unreadable_pref_lines(profile_dir: Path) -> tuple[str, ...]:
    """The prefs.js lines that are neither blank, a comment, nor a line `_PREF`
    reads. A declared key named on one is UNREACHABLE, never unset (spec §6.1)."""
    lines = []
    for line in (
        (Path(profile_dir) / "prefs.js").read_text(encoding="utf-8").splitlines()
    ):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "/*", "*")):
            continue
        if _PREF.match(stripped) is None:
            lines.append(stripped)
    return tuple(lines)


class DefaultsUnreadableError(RuntimeError):
    """An xpi exists but cannot be read, or a `pref(` line in it cannot be parsed."""


def literal(value: str | bool | int) -> str:
    """A decoded preference as prefs.js spells it."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return json.dumps(value, ensure_ascii=False)


def line_names_key(line: str, keys, key_prefix: str | None) -> bool:
    """Whether `line` names one of `keys`, in full or minus `key_prefix`; every
    line names a key when `keys` is None."""
    if keys is None:
        return True
    for key in keys:
        if key in line:
            return True
        if key_prefix and key.startswith(key_prefix) and key[len(key_prefix) :] in line:
            return True
    return False


def xpi_defaults(
    profile_dir: Path, addon_id: str, keys=None, key_prefix: str | None = None
) -> dict[str, str]:
    """The shipped defaults of one add-on, key → prefs.js literal.

    Read from `prefs.js` at the archive root, then every
    `defaults/preferences/*.js` (designs cluster 5 (a), measured); the first
    occurrence of a key wins, so the root `prefs.js` outranks the rest. Keys
    are as written — full, or relative to the add-on's prefix (Better BibTeX).
    `{}` when the xpi is absent. An archive that cannot be opened raises
    `DefaultsUnreadableError`; so does a `pref(` line the grammar cannot read,
    when `keys` is None or the line names one of `keys` (in full, or minus
    `key_prefix`) — a broken line about another key costs nothing.
    """
    xpi = Path(profile_dir) / "extensions" / f"{addon_id}.xpi"
    if not xpi.is_file():
        return {}
    defaults: dict[str, str] = {}
    try:
        with zipfile.ZipFile(xpi) as archive:
            names = [
                n
                for n in archive.namelist()
                if n == "prefs.js"
                or (n.startswith("defaults/preferences/") and n.endswith(".js"))
            ]
            for name in sorted(names, key=lambda n: (n != "prefs.js", n)):
                text = archive.read(name).decode("utf-8", errors="replace")
                for line in text.splitlines():
                    stripped = line.strip()
                    if not stripped.startswith(("pref(", "user_pref(")):
                        continue
                    match = _PREF.match(stripped)
                    if match is None:
                        if line_names_key(stripped, keys, key_prefix):
                            raise DefaultsUnreadableError(
                                f"{xpi.name}: unreadable preference line {stripped!r}"
                            )
                        continue
                    defaults.setdefault(
                        match.group("name"),
                        _literal_token(match.group("value").strip()),
                    )
    except DefaultsUnreadableError:
        raise
    # zipfile surfaces a damaged or unsupported archive as any of these: a
    # corrupt deflate stream is zlib.error, an encrypted entry RuntimeError,
    # an unknown method NotImplementedError, a truncated stream EOFError.
    except (
        OSError,
        zipfile.BadZipFile,
        zlib.error,
        RuntimeError,
        NotImplementedError,
        EOFError,
    ) as error:
        raise DefaultsUnreadableError(f"{xpi.name}: {error}") from error
    return defaults


def _literal_token(raw: str) -> str:
    if raw in {"true", "false"} or raw.lstrip("-").isdigit():
        return raw
    return literal(_string_pref(raw)) if raw.startswith('"') else raw


def effective_value(
    prefs: dict, defaults: dict[str, str], key: str, key_prefix: str | None
) -> str:
    """prefs.js first, then the shipped default under the full key, then under
    the key minus the add-on's prefix; `unset` when none holds it."""
    if key in prefs:
        return literal(prefs[key])
    if key in defaults:
        return defaults[key]
    if key_prefix and key.startswith(key_prefix):
        relative = key[len(key_prefix) :]
        if relative in defaults:
            return defaults[relative]
    return "unset"


def version_at_least(installed: str, floor: str) -> bool | None:
    """Each segment's leading integer (#191): `1.7.0-beta` reads as 1.7.0; a
    segment with no leading digits is None, which the probe names."""

    def parse(text: str) -> list[int] | None:
        parts = []
        for segment in text.split("."):
            match = re.match(r"\d+", segment)
            if match is None:
                return None
            parts.append(int(match.group(0)))
        return parts

    have, want = parse(installed), parse(floor)
    if have is None or want is None:
        return None
    width = max(len(have), len(want))
    have += [0] * (width - len(have))
    want += [0] * (width - len(want))
    return have >= want


BBT_ID = "better-bibtex@iris-advies.com"
BBT_PREFIX = "extensions.zotero.translators.better-bibtex."
BBT_AUTO_EXPORT = BBT_PREFIX + "autoExport."


def bbt_auto_exports(prefs: dict) -> list[dict]:
    """Every auto-export Better BibTeX keeps as a JSON string under its branch
    (designs cluster 5 (e), measured on 9.0.68); an unparseable one raises."""
    exports = []
    for key in sorted(k for k in prefs if k.startswith(BBT_AUTO_EXPORT)):
        value = prefs[key]
        if isinstance(value, str) and value.startswith('"'):
            value = _string_pref(value)
        try:
            document = json.loads(value) if isinstance(value, str) else value
        except ValueError as error:
            raise ValueError(f"{key}: {error}") from error
        if isinstance(document, dict):
            exports.append(document)
    return exports
