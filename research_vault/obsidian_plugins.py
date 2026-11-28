"""The Obsidian plugin declaration the seed and doctor read (spec §4.2, §6.3).

Shaped as `addons`: one packaged Markdown file, two tables, a strict reader;
a third, the load demotions, is read by the vendoring script (R63).
"""

import json
import re
from importlib import resources
from pathlib import Path
from typing import NamedTuple

NEEDS = ("seeded", "recommended", "excluded")
CORE = "Core"
UNSET = "unset"
_SOURCE = "obsidian-plugins.md"
_CELL = r"\|\s*(?P<{name}>[^|]*?)\s*"
_PLUGIN_ROW = re.compile(
    "^"
    + "".join(
        _CELL.format(name=name)
        for name in ("name", "id", "need", "pin", "licence", "workflows")
    )
    + r"\|$"
)
_SETTING_ROW = re.compile(
    "^"
    + "".join(_CELL.format(name=name) for name in ("plugin", "file", "key", "accepted"))
    + r"\|$"
)
_DEMOTION_ROW = re.compile(
    "^"
    + "".join(
        _CELL.format(name=name)
        for name in ("plugin", "version", "host", "error", "measured")
    )
    + r"\|$"
)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# A header is recognised by the whole row, so a data row is never dropped
# for sharing a first cell with it.
_PLUGIN_HEADER = ("Plugin", "Id", "Need", "Pin", "Licence", "Workflows")
_SETTING_HEADER = ("Plugin", "File", "Key", "Accepted")
_DEMOTION_HEADER = ("Plugin", "Version", "Host", "Error", "Measured")
_ACCEPTED_LITERAL = re.compile(r"`([^`]+)`")
_NONE = "—"
_DATA_JSON = "data.json"


class ConfigUnreadableError(ValueError):
    """A settings file exists but does not parse as JSON (doctor: UNREACHABLE)."""


class Plugin(NamedTuple):
    name: str
    plugin_id: str
    need: str
    pin: str | None
    licence: str | None
    workflows: str


class Setting(NamedTuple):
    plugin: str
    file: str
    key: str
    accepted: tuple[str, ...]


class Demotion(NamedTuple):
    """A measured load failure that demotes a plugin to recommended (R63): the
    vendoring script reads it after the licence screen and writes no asset.
    Removing the row after a re-measure is what clears it."""

    plugin: str
    version: str
    host: str
    error: str
    measured: str


class Declaration(NamedTuple):
    plugins: list[Plugin]
    settings: list[Setting]
    demotions: tuple[Demotion, ...] = ()

    @property
    def by_id(self) -> dict[str, Plugin]:
        return {plugin.plugin_id: plugin for plugin in self.plugins}

    @property
    def by_name(self) -> dict[str, Plugin]:
        return {plugin.name: plugin for plugin in self.plugins}

    def demotion_for(self, plugin_id: str) -> Demotion | None:
        plugin = self.by_id.get(plugin_id)
        return next(
            (d for d in self.demotions if plugin and d.plugin == plugin.name), None
        )

    def settings_for(self, plugin_id: str) -> list[Setting]:
        name = self.by_id[plugin_id].name
        return [setting for setting in self.settings if setting.plugin == name]


def _fault(line: str, why: str = "") -> ValueError:
    detail = f" ({why})" if why else ""
    return ValueError(f"{_SOURCE}: unreadable row {line!r}{detail}")


def _code(cell: str, line: str) -> str | None:
    """A backticked cell's text; `—` or empty is None; anything else is a fault."""
    if cell in {"", _NONE}:
        return None
    if cell.startswith("`") and cell.endswith("`") and len(cell) > 2:
        return cell[1:-1]
    raise _fault(line, f"cell {cell!r}")


def _plain(cell: str) -> str | None:
    return None if cell in {"", _NONE} else cell


def _plugin_row(line: str) -> Plugin | None:
    match = _PLUGIN_ROW.match(line)
    if match is None:
        raise _fault(line)
    if tuple(match.groups()) == _PLUGIN_HEADER:
        return None
    need = match.group("need")
    if need not in NEEDS:
        raise _fault(line, f"need {need!r}")
    plugin_id = _code(match.group("id"), line)
    if not plugin_id:
        raise _fault(line, "no id")
    pin = _plain(match.group("pin"))
    if need != "excluded" and pin is None:
        raise _fault(line, "no pin")
    return Plugin(
        match.group("name"),
        plugin_id,
        need,
        pin,
        _plain(match.group("licence")),
        match.group("workflows"),
    )


def _literal(text: str, line: str) -> str:
    """An accepted cell literal in `read_key`'s compact form, or `unset`."""
    if text == UNSET:
        return text
    try:
        value = json.loads(text)
    except ValueError as error:
        raise _fault(line, f"accepted literal {text!r}") from error
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _setting_row(line: str) -> Setting | None:
    match = _SETTING_ROW.match(line)
    if match is None:
        raise _fault(line)
    if tuple(match.groups()) == _SETTING_HEADER:
        return None
    file = _code(match.group("file"), line)
    key = _code(match.group("key"), line)
    if not file or not file.endswith(".json") or not key:
        raise _fault(line, "file or key")
    plugin = match.group("plugin")
    # A plugin's settings live in its data.json; Core's in the config root.
    if (plugin == CORE) == (file == _DATA_JSON):
        raise _fault(line, f"{plugin} cannot declare {file}")
    # Split on the backticks, not on ", ": a literal may itself hold ", ".
    cell = match.group("accepted")
    literals = _ACCEPTED_LITERAL.findall(cell)
    if not literals or _ACCEPTED_LITERAL.sub("", cell).replace(",", "").strip():
        raise _fault(line, "accepted literals")
    accepted = [_literal(literal, line) for literal in literals]
    return Setting(plugin, file, key, tuple(accepted))


def _demotion_row(line: str) -> Demotion | None:
    match = _DEMOTION_ROW.match(line)
    if match is None:
        raise _fault(line)
    if tuple(match.groups()) == _DEMOTION_HEADER:
        return None
    if not all(match.groups()) or not _DATE.match(match.group("measured")):
        raise _fault(line, "demotion cells")
    return Demotion(*match.groups())


def parse(text: str) -> Declaration:
    """The two tables of `text`; every `|` line must parse, or this raises
    ``ValueError``: a typo must never delete a check silently."""
    plugins: list[Plugin] = []
    settings: list[Setting] = []
    demotions: list[Demotion] = []
    table = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("### "):
            table = line[4:].strip().lower()
            continue
        if not line.startswith("|") or set(line) <= {"|", "-", " "}:
            continue
        if table == "plugins":
            plugin = _plugin_row(line)
            if plugin is not None:
                plugins.append(plugin)
        elif table == "declared plugin settings":
            setting = _setting_row(line)
            if setting is not None:
                settings.append(setting)
        elif table == "load demotions":
            demotion = _demotion_row(line)
            if demotion is not None:
                demotions.append(demotion)
        else:
            raise ValueError(f"{_SOURCE}: a table row outside a known table: {line!r}")
    for field in ("name", "plugin_id"):
        values = [getattr(plugin, field) for plugin in plugins]
        if len(values) != len(set(values)):
            raise ValueError(f"{_SOURCE}: a plugin {field} is declared twice")
    names = {plugin.name for plugin in plugins}
    for setting in settings:
        if setting.plugin != CORE and setting.plugin not in names:
            raise ValueError(
                f"{_SOURCE}: settings row names no declared plugin: {setting.plugin!r}"
            )
    by_name = {plugin.name: plugin for plugin in plugins}
    for demotion in demotions:
        plugin = by_name.get(demotion.plugin)
        if plugin is None or plugin.need == "excluded":
            raise ValueError(
                f"{_SOURCE}: demotion row names no vendorable plugin: "
                f"{demotion.plugin!r}"
            )
        if plugin.need == "seeded":
            raise ValueError(
                f"{_SOURCE}: {demotion.plugin!r} is demoted but declared seeded; "
                "run the vendoring script and declare what it wrote"
            )
    if len({d.plugin for d in demotions}) != len(demotions):
        raise ValueError(f"{_SOURCE}: a plugin is demoted twice")
    return Declaration(plugins, settings, tuple(demotions))


def declared() -> Declaration:
    """The packaged declaration (`templates/obsidian-plugins.md`). Packaged
    beside the code, so a file that will not decode is a broken install."""
    source = resources.files("research_vault").joinpath(f"templates/{_SOURCE}")
    try:
        text = source.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{_SOURCE}: not UTF-8: {error}") from error
    return parse(text)


def read_key(path: Path, dotted: str) -> str:
    """The JSON literal at a dotted key in a JSON file, or `unset`; an unparseable
    file raises `ConfigUnreadableError` (doctor reports UNREACHABLE: Obsidian rewrites
    these files non-atomically, screen B §7.37). The key splits on `.` only, so
    `homepages.Main Homepage.autoCreate` names three levels."""
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return UNSET
    except (OSError, UnicodeError, ValueError) as error:
        raise ConfigUnreadableError(f"{Path(path).name}: {error}") from error
    node = document
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return UNSET
        node = node[part]
    return json.dumps(node, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
