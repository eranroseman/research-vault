"""Vendor one Obsidian community plugin at a pinned release (lanes 2-3 spec §4.2, §4.6).

Run by hand, with network: it resolves the plugin's repository from the
community registry, fetches the release assets at the tag byte for byte, reads
the licence at the tag's commit and every bundled package's licence from the
npm registry, and writes the plugin folder under
research_vault/templates/obsidian/plugins/<id>/ with LICENSE,
THIRD-PARTY-NOTICES and SOURCE.json. A licence with a source obligation, or one
that cannot be established, makes the plugin recommended: data.json stays, no
asset is written, SOURCE.json says why. The script never edits the declaration
table; a test compares the two.

A measured load failure demotes too (R63). The declaration's Load demotions
table names the plugin, the version and host measured, the error and the
date; after the licence screen the script makes a plugin named there
recommended whatever its licence, drops the assets, LICENSE and
THIRD-PARTY-NOTICES, and starts SOURCE.json's method with the measured
error. The row applies to every tag of the plugin until it is removed after
a re-measure, so a later release is not seeded unmeasured. `--reapply ID`
applies the table to the committed record offline, without the network:
it demotes from SOURCE.json as it stands and never re-seeds (clearing a
demotion needs the assets, so it is a run with network after the row goes).

What is bundled (R50, #306). The rule is chosen so that any error is
over-attribution: THIRD-PARTY-NOTICES and SOURCE.json's `bundled` list

1. the lockfile's full transitive production closure: package-lock.json or
   npm-shrinkwrap.json (every entry npm does not mark `dev`), else yarn.lock v1
   or pnpm-lock.yaml v9 (the closure of package.json's dependencies and
   optionalDependencies through the lockfile's entries), each package at every
   version installed;
2. plus every package.json devDependency whose name occurs in main.js, at each
   version the lockfile installs, because bundlers inline runtime libraries
   listed under dev. "Occurs" is in_bundle: the exact, case-sensitive name not
   continued by `[A-Za-z0-9_-]` on either side, anywhere in the file (a
   require, an import path, a comment, or an unrelated word that is also the
   name, which over-attributes); deterministic for a given main.js;
3. less HOST_PROVIDED, the only subtraction (R64): Obsidian's documented
   externals, the names the official sample plugin's esbuild.config.mjs marks
   external (obsidianmd/obsidian-sample-plugin at
   07ceb81d1fb3384af611ebf665a1ec42a7e5926d: `obsidian`, `electron`, eight
   `@codemirror/*`, three `@lezer/*`, and Node's builtinModules), each
   subtracted only when main.js does nothing with the name but `require("…")`
   it (is_host_provided): that is what an external reference compiles to, and
   any other occurrence means the code was bundled, so the name stays listed.
   Where the package was resolved from does not matter. A Node builtin name
   an installed npm package also carries (a polyfill) is never subtracted,
   and `obsidian` followed by `:` or `.` is a URI or host, not a module.

A plugin with no lockfile records no install, so the closure is walked through
registry.npmjs.org from package.json at each range's floor (unlocked): it
over-attributes names and records floor versions, and SOURCE.json's method
says so. A stale npm or pnpm lockfile (its root record names other
dependencies than package.json) is refused as not describing the build, and
the next lockfile, or the walk, is used instead (obsidian-icon-folder's
package-lock.json, measured 2026-11-27, gives way to its pnpm-lock.yaml). A plugin with no package.json lists nothing. A package is not
enumerated from a licence banner: dev-only transitive code that left no name in
main.js (tslib's helpers, inlined by a TypeScript plugin) is not listed. The
main.js banner scan (copyleft_banner) only demotes, for copyleft code that kept
its banner whichever package carried it.

GitHub's unauthenticated API allows 60 requests an hour; a token in
GITHUB_TOKEN (for instance `GITHUB_TOKEN=$(gh auth token)`) rides the API
requests only. The downloaded assets are data: nothing here executes them.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, NamedTuple

from research_vault import obsidian_plugins

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "research_vault" / "templates" / "obsidian" / "plugins"
REGISTRY = "https://raw.githubusercontent.com/obsidianmd/obsidian-releases/HEAD/community-plugins.json"
ASSETS = ("main.js", "manifest.json", "styles.css")
_API = "https://api.github.com/"
# SPDX families that carry a source obligation on redistribution. Anything not
# matched here and not in PERMISSIVE is "not established" and demotes too.
COPYLEFT = re.compile(
    r"^(GPL|LGPL|AGPL|MPL|EUPL|CPAL|CDDL|OSL|EPL|CECILL|SSPL)\b", re.IGNORECASE
)
# CC-BY-4.0 (R65) carries attribution but no source obligation, so it does not
# demote; THIRD-PARTY-NOTICES, which names every bundled package with its
# licence and URL, discharges its BY term.
PERMISSIVE = re.compile(
    r"^(MIT|ISC|0BSD|BSD-[123]-Clause|Apache-2\.0|Unlicense|Zlib|CC0-1\.0"
    r"|CC-BY-4\.0|BlueOak-1\.0\.0|WTFPL|PSF-2\.0|Python-2\.0)$",
    re.IGNORECASE,
)
# Obsidian's documented externals (R64): `external` in the official sample
# plugin's esbuild.config.mjs at obsidianmd/obsidian-sample-plugin
# 07ceb81d1fb3384af611ebf665a1ec42a7e5926d (fetched 2026-11-27), whose last
# entry is `...builtinModules` from `node:module`; NODE_BUILTINS is that list
# as Node 24.21.0 prints it (measured 2026-11-27), without the `node:`-only
# names, which no npm package can carry. The running app supplies each, so a
# reference main.js only require()s is not bundled code.
OBSIDIAN_EXTERNALS = frozenset(
    {
        "obsidian",
        "electron",
        "@codemirror/autocomplete",
        "@codemirror/collab",
        "@codemirror/commands",
        "@codemirror/language",
        "@codemirror/lint",
        "@codemirror/search",
        "@codemirror/state",
        "@codemirror/view",
        "@lezer/common",
        "@lezer/highlight",
        "@lezer/lr",
    }
)
NODE_BUILTINS = frozenset(
    {
        "_http_agent",
        "_http_client",
        "_http_common",
        "_http_incoming",
        "_http_outgoing",
        "_http_server",
        "_stream_duplex",
        "_stream_passthrough",
        "_stream_readable",
        "_stream_transform",
        "_stream_wrap",
        "_stream_writable",
        "_tls_common",
        "_tls_wrap",
        "assert",
        "assert/strict",
        "async_hooks",
        "buffer",
        "child_process",
        "cluster",
        "console",
        "constants",
        "crypto",
        "dgram",
        "diagnostics_channel",
        "dns",
        "dns/promises",
        "domain",
        "events",
        "fs",
        "fs/promises",
        "http",
        "http2",
        "https",
        "inspector",
        "inspector/promises",
        "module",
        "net",
        "os",
        "path",
        "path/posix",
        "path/win32",
        "perf_hooks",
        "process",
        "punycode",
        "querystring",
        "readline",
        "readline/promises",
        "repl",
        "stream",
        "stream/consumers",
        "stream/promises",
        "stream/web",
        "string_decoder",
        "sys",
        "timers",
        "timers/promises",
        "tls",
        "trace_events",
        "tty",
        "url",
        "util",
        "util/types",
        "v8",
        "vm",
        "wasi",
        "worker_threads",
        "zlib",
    }
)
HOST_PROVIDED = OBSIDIAN_EXTERNALS | NODE_BUILTINS
_IDENTIFIER = re.compile(r"[A-Za-z_$][\w$]*")
_SPECIFIER_EDGE = "\"'`/"
COPYLEFT_BANNER = re.compile(
    r"GNU (?:Lesser |Library |Affero )?General Public License"
    r"|Mozilla Public License|European Union Public Licen[cs]e"
    r"|SPDX-License-Identifier:\s*(?:L?GPL|AGPL|MPL|EUPL|CPAL)"
    r"|@license\s+(?:L?GPL|AGPL|MPL|EUPL|CPAL)",
    re.IGNORECASE,
)
# Licences whose text carries the grantor's copyright line; Apache-2.0 names
# its Licensor elsewhere (NOTICE, headers), so a holder is read only for these.
HOLDER_IN_TEXT = re.compile(r"^(MIT|ISC|0BSD|BSD-[123]-Clause)$")
PLACEHOLDER_HOLDERS = {
    "",
    "local",
    "your name",
    "author",
    "[fullname]",
    "<copyright holders>",
}


def has_source_obligation(licence: object) -> bool | None:
    """True for a copyleft family, False for a permissive licence, None when the
    licence is not established (unknown expression, empty, UNLICENSED). An SPDX
    expression is parsed with AND binding tighter than OR: an OR is free when
    any side is, an AND carries every side's obligation."""
    if not isinstance(licence, str) or not licence.strip():
        return None
    tokens = re.findall(r"\(|\)|[^\s()]+", licence)
    try:
        result, rest = _or(tokens)
    except IndexError:
        return None
    return None if rest else result


def _or(tokens: list[str]) -> tuple[bool | None, list[str]]:
    verdicts = []
    while True:
        verdict_, tokens = _and(tokens)
        verdicts.append(verdict_)
        if not tokens or tokens[0].upper() != "OR":
            break
        tokens = tokens[1:]
    if False in verdicts:
        return False, tokens
    return (None if None in verdicts else True), tokens


def _and(tokens: list[str]) -> tuple[bool | None, list[str]]:
    verdicts = []
    while True:
        verdict_, tokens = _term(tokens)
        verdicts.append(verdict_)
        if not tokens or tokens[0].upper() != "AND":
            break
        tokens = tokens[1:]
    if True in verdicts:
        return True, tokens
    return (None if None in verdicts else False), tokens


def _term(tokens: list[str]) -> tuple[bool | None, list[str]]:
    head, tokens = tokens[0], tokens[1:]
    if head == "(":
        result, tokens = _or(tokens)
        if not tokens or tokens[0] != ")":
            raise IndexError("unbalanced")
        return result, tokens[1:]
    if head == ")" or head.upper() in ("AND", "OR", "WITH"):
        raise IndexError(head)
    if tokens and tokens[0].upper() == "WITH":  # an exception never adds an obligation
        tokens = tokens[2:]
    if COPYLEFT.match(head):
        return True, tokens
    if PERMISSIVE.match(head):
        return False, tokens
    return None, tokens


def copyleft_banner(main_js: bytes) -> str | None:
    """The first copyleft licence banner bundled code left in main.js, or None.
    It demotes and does not enumerate: code a lockfile does not name is
    caught here only if it kept its banner."""
    match = COPYLEFT_BANNER.search(main_js.decode("utf-8", errors="replace"))
    return match.group(0) if match else None


def verdict(licence: str | None, bundled: list[dict], *, holder: str) -> str:
    if has_source_obligation(licence) is not False:
        return "recommended"
    if HOLDER_IN_TEXT.match(licence or "") and is_placeholder(holder):
        return "recommended"
    for dependency in bundled:
        if has_source_obligation(dependency.get("licence")) is not False:
            return "recommended"
    return "seeded"


def is_placeholder(holder: str) -> bool:
    """A template's unfilled holder: bracketed fields like `[year] [fullname]`
    and bare years removed, nothing or a stock name is left."""
    rest = re.sub(r"\[[^\]]*\]|<[^>]*>|\{[^}]*\}|\b\d{4}\b|[-\u2013,]", " ", holder)
    return " ".join(rest.split()).lower() in PLACEHOLDER_HOLDERS


def holder_of(text: str) -> str:
    """The holder on the first line that opens with `Copyright`, years dropped."""
    match = re.search(
        r"^[ \t]*Copyright\b[ \t]*(?:\(c\)|©)?[ \t]*(?:\d{4}[-\u2013,\s\d]*)?(.*)$",
        text,
        re.MULTILINE | re.IGNORECASE,
    )
    return match.group(1).strip() if match else ""


def _get(url: str) -> bytes:
    headers = {"User-Agent": "research-vault-vendor"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith(_API):
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def _json(url: str) -> Any:
    return json.loads(_get(url).decode("utf-8"))


def resolve_repo(plugin_id: str, registry: str) -> str:
    for entry in _json(registry):
        if entry.get("id") == plugin_id:
            return entry["repo"]
    raise SystemExit(f"{plugin_id}: not in the community registry")


def release(repo: str, tag: str) -> dict:
    return _json(f"{_API}repos/{repo}/releases/tags/{tag}")


def commit_for(repo: str, tag: str) -> str:
    ref = _json(f"{_API}repos/{repo}/git/ref/tags/{tag}")["object"]
    if ref["type"] == "tag":  # an annotated tag points at a tag object first
        ref = _json(ref["url"])["object"]
    return ref["sha"]


def licence_at(repo: str, commit: str) -> tuple[str | None, bytes, str]:
    """(SPDX id or None, LICENSE bytes, copyright holder) from the LICENSE* file at the commit."""
    tree = _json(f"{_API}repos/{repo}/git/trees/{commit}")["tree"]
    names = sorted(
        e["path"]
        for e in tree
        if e["type"] == "blob"
        and e["path"].upper().startswith(("LICENSE", "LICENCE", "COPYING"))
    )
    if not names:
        return None, b"", ""
    data = _get(f"https://raw.githubusercontent.com/{repo}/{commit}/{names[0]}")
    text = data.decode("utf-8", errors="replace")
    return _spdx_from_text(text), data, holder_of(text)


def _spdx_from_text(text: str) -> str | None:
    head = text[:600]
    if "MIT License" in head or "Permission is hereby granted, free of charge" in text:
        return "MIT"
    if "Apache License" in head and "2.0" in head:
        return "Apache-2.0"
    if "GNU AFFERO GENERAL PUBLIC LICENSE" in head:
        return "AGPL-3.0"
    if "GNU GENERAL PUBLIC LICENSE" in head:
        return "GPL-3.0" if "Version 3" in head else "GPL-2.0"
    if "GNU LESSER GENERAL PUBLIC LICENSE" in head:
        return "LGPL-3.0" if "Version 3" in head else "LGPL-2.1"
    if "Mozilla Public License" in head:
        return "MPL-2.0"
    if "ISC License" in head:
        return "ISC"
    if "BSD" in head and "Redistribution and use in source and binary forms" in text:
        return "BSD-3-Clause" if "Neither the name" in text else "BSD-2-Clause"
    return None


# Read in this order; a stale one is skipped. Yarn 2+ and pnpm before
# lockfileVersion 9 are refused, not read.
LOCKFILES = ("package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml")


_NAME_CHAR = re.compile(r"[A-Za-z0-9_-]+")


class Locked(NamedTuple):
    """One package a lockfile installs: production when the plugin's runtime
    dependencies reach it, otherwise dev-only."""

    name: str
    version: str
    production: bool
    resolved: str


def is_host_provided(
    name: str, main_js: str | None, installed: frozenset[str] = frozenset()
) -> bool:
    """The HOST_PROVIDED subtraction (R64): a host-provided name main.js
    references only as the whole argument of `require("…")` (either quote).
    Any other occurrence is bundled code and keeps the name listed; so does
    no require at all, or no main.js, because the error must be
    over-attribution. An occurrence is in_bundle's whole name, except that a
    name which can be a JavaScript identifier counts only where a specifier
    or a path segment starts, after a quote, a backtick or `/`: `var obsidian
    = require("obsidian"); obsidian.Notice` binds the module, and
    `".obsidian/plugins"` names the config folder; neither bundles anything
    (measured 2026-11-27: the config-folder strings alone would keep
    `obsidian` listed for three seeded plugins). For `obsidian` alone, an
    occurrence followed by `:` or `.` is a URI or a host (`obsidian://open`,
    `https://obsidian.md`), not a module. A Node builtin name is subtracted
    only when `installed`, the lockfile's packages (the registry walk's
    without one), holds no npm package of that name: a polyfill such as
    `buffer` can be bundled under the builtin's name, so an installed one
    stays listed."""
    if name not in HOST_PROVIDED or main_js is None:
        return False
    if name in NODE_BUILTINS and name in installed:
        return False
    requires = len(
        re.findall(
            r"(?<![\w$.])require\(\s*([\"'])" + re.escape(name) + r"\1\s*\)", main_js
        )
    )
    can_bind = _IDENTIFIER.fullmatch(name) is not None
    occurrences = 0
    start = main_js.find(name)
    while start != -1:
        before = main_js[start - 1 : start] if start else ""
        after = main_js[start + len(name) :][:1]
        whole = not _NAME_CHAR.match(before) and not _NAME_CHAR.match(after)
        starts_specifier = bool(before) and before in _SPECIFIER_EDGE
        uri = name == "obsidian" and after in (":", ".")
        if whole and not uri and (starts_specifier or not can_bind):
            occurrences += 1
        start = main_js.find(name, start + 1)
    return requires > 0 and occurrences == requires


def in_bundle(name: str, main_js: str, tokens: set[str] | None = None) -> bool:
    """The name occurs in main.js as a whole package name: not continued by a
    letter, digit, `_` or `-` on either side. A require or import path
    (`"jszip"`, `node_modules/jszip/lib`), a minified `e("pako")` and a comment
    all count; so does an unrelated word that happens to be the name, which
    over-attributes and never misses a spelled-out name. Case-sensitive, as
    npm names are. `tokens`, main.js's maximal runs of those characters, is
    the same test for a name made only of them."""
    if tokens is not None and _NAME_CHAR.fullmatch(name):
        return name in tokens
    start = main_js.find(name)
    while start != -1:
        before, after = main_js[start - 1 : start], main_js[start + len(name) :][:1]
        if not (start and _NAME_CHAR.match(before)) and not _NAME_CHAR.match(after):
            return True
        start = main_js.find(name, start + 1)
    return False


def npm_lock(lock: dict) -> list[Locked]:
    """package-lock.json or npm-shrinkwrap.json, lockfileVersion 1, 2 or 3. npm
    marks a package reached only through devDependencies `dev`; every other
    entry (optional, peer, devOptional) is production."""
    out = []
    for key, entry in (lock.get("packages") or {}).items():
        if "node_modules/" not in key or entry.get("link"):
            continue  # the root project, a workspace or a link to one
        name = entry.get("name") or key.rsplit("node_modules/", 1)[1]
        out.append(
            Locked(
                name,
                str(entry.get("version", "")),
                not entry.get("dev"),
                str(entry.get("resolved", "")),
            )
        )
    if out or "packages" in lock:
        return out

    def walk(dependencies: dict) -> None:  # lockfileVersion 1 nests its tree
        for name, entry in dependencies.items():
            out.append(
                Locked(
                    name,
                    str(entry.get("version", "")),
                    not entry.get("dev"),
                    str(entry.get("resolved", "")),
                )
            )
            walk(entry.get("dependencies") or {})

    walk(lock.get("dependencies") or {})
    return out


def yarn_lock(text: str, package: dict) -> list[Locked]:
    """yarn.lock v1, which records no dev flag: production is the closure of
    package.json's dependencies and optionalDependencies through each entry's
    dependencies, and every other entry is dev-only. Yarn 2+ (`__metadata`)
    is refused rather than misread."""
    if "__metadata:" in text:
        raise SystemExit("yarn.lock is Yarn 2+, which this script does not read")
    entries: dict[str, dict] = {}
    current: dict = {}
    section = False
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            current = {"version": "", "resolved": "", "dependencies": {}}
            for spec in line.rstrip(":").split(","):
                entries[spec.strip().strip('"')] = current
            section = False
        elif line.startswith("    ") and section:
            name, _, spec = line.strip().partition(" ")
            current["dependencies"][name.strip('"')] = spec.strip('"')
        else:
            key, _, value = line.strip().partition(" ")
            section = key in ("dependencies:", "optionalDependencies:")
            if key in ("version", "resolved"):
                current[key] = value.strip('"')

    def spec_name(spec: str) -> str:
        return spec[: spec.index("@", 1)]

    production: set[int] = set()
    queue = [
        f"{name}@{spec}"
        for field in ("dependencies", "optionalDependencies")
        for name, spec in (package.get(field) or {}).items()
    ]
    while queue:
        entry = entries.get(queue.pop())
        if entry is None or id(entry) in production:
            continue
        production.add(id(entry))
        queue.extend(f"{n}@{s}" for n, s in entry["dependencies"].items())
    out, seen = [], set()
    for spec, entry in entries.items():
        if id(entry) not in seen:
            seen.add(id(entry))
            out.append(
                Locked(
                    spec_name(spec),
                    entry["version"],
                    id(entry) in production,
                    entry["resolved"],
                )
            )
    return out


def pnpm_lock(text: str, package: dict) -> list[Locked] | None:
    """pnpm-lock.yaml lockfileVersion 9, read line by line (stdlib only):
    production is the closure of the root importer's dependencies and
    optionalDependencies through `snapshots`, every other snapshot dev-only.
    A version keeps pnpm's spelling minus the `(peer)` suffix; a git or URL
    version is also `resolved`. None when the root importer names other
    dependencies than package.json (stale). Another lockfileVersion is
    refused rather than misread."""
    if not re.search(r"^lockfileVersion: '?9\.", text, re.MULTILINE):
        raise SystemExit("pnpm-lock.yaml is not lockfileVersion 9")
    root: dict[str, dict[str, str]] = {}
    snapshots: dict[str, dict[str, str]] = {}
    section = field = name = key = ""

    def unquote(value: str) -> str:
        return value.strip().strip("'\"")

    for line in text.splitlines():
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        head, _, value = line.strip().partition(": ")
        head = unquote(head.rstrip(":"))
        if indent == 0:
            section = head
        elif section == "importers":
            if indent == 2:
                key = head
            elif key == "." and indent == 4:
                field = head
                root.setdefault(field, {})
            elif key == "." and indent == 6:
                name = head
            elif key == "." and indent == 8 and head == "version":
                root[field][name] = unquote(value)
        elif section == "snapshots":
            if indent == 2:
                key = head
                snapshots[key] = {}
            elif indent == 4:
                field = head
            elif indent == 6 and field in ("dependencies", "optionalDependencies"):
                snapshots[key][head] = unquote(value)
    if any(set(root.get(f) or {}) != set(package.get(f) or {}) for f in _FIELDS):
        return None
    production: set[str] = set()
    queue = [
        f"{n}@{v}"
        for f in ("dependencies", "optionalDependencies")
        for n, v in (root.get(f) or {}).items()
    ]
    while queue:
        key = queue.pop()
        if key in production or key not in snapshots:
            continue
        production.add(key)
        queue.extend(f"{n}@{v}" for n, v in snapshots[key].items())
    out = []
    for key in snapshots:
        name, version = key[: key.index("@", 1)], key[key.index("@", 1) + 1 :]
        version = version.split("(", 1)[0]
        resolved = version if "/" in version else ""
        out.append(Locked(name, version, key in production, resolved))
    return out


def _floor(spec: object) -> str:
    """The lowest version a range admits, as the registry spells versions:
    the first `||` alternative, operators dropped, `x`/`*` parts as 0, padded
    to three parts. A git or URL spec passes through (the registry refuses it)."""
    first = str(spec).split("||")[0].strip()
    floor = re.sub(r"^[\^~>=<v\s]+", "", first).split(" ")[0]
    if floor in ("", "*", "x", "X"):
        return "latest"
    if not re.fullmatch(r"[\dxX*]+(\.[\dxX*]+){0,2}", floor):
        return floor
    parts = [re.sub(r"[xX*]", "0", part) for part in floor.split(".")]
    return ".".join([*parts, "0", "0"][:3])


def _registry(name: str, version: str) -> dict | None:
    try:
        metadata = _json(f"https://registry.npmjs.org/{name}/{version}")
    except (urllib.error.HTTPError, ValueError):
        return None
    return metadata if isinstance(metadata, dict) else None


def unlocked(package: dict) -> list[Locked]:
    """No lockfile at the commit: nothing records what the release build
    installed, so the closure is walked through registry.npmjs.org, each range
    at its floor. The names over-attribute (a floor can require more than the
    build's version did); a version is the floor's, not the build's. The
    package.json spec stands in for `resolved`; the registry cannot answer a
    git or URL pin, which demotes unless is_host_provided subtracts the
    package. Only `obsidian`'s own dependencies are not walked: it is type
    declarations alone, and any other host name may be bundled."""
    out: list[Locked] = []
    seen: set[tuple[str, str]] = set()

    def walk(dependencies: dict, production: bool) -> None:
        for name, spec in sorted(dependencies.items()):
            version = _floor(spec)
            if (name, version) in seen:
                continue
            seen.add((name, version))
            out.append(Locked(name, version, production, str(spec)))
            # only `obsidian` is type declarations alone; any other host
            # name may be bundled, so its tree is walked (over-attribution)
            if production and name != "obsidian":
                walk((_registry(name, version) or {}).get("dependencies") or {}, True)

    walk(
        {
            **(package.get("dependencies") or {}),
            **(package.get("optionalDependencies") or {}),
        },
        True,
    )
    walk(package.get("devDependencies") or {}, False)
    return out


_FIELDS = ("dependencies", "devDependencies", "optionalDependencies")


def stale(lock: dict, package: dict) -> bool:
    """An npm lockfile (v2, v3) whose root record names other dependencies
    than package.json does, in any of _FIELDS: it describes an earlier tree,
    not the build at the commit. Its root `version` is not compared, as it
    routinely lags (measured 2026-11-27: seven of eleven lockfiles)."""
    root = (lock.get("packages") or {}).get("")
    return root is not None and any(
        set(root.get(field) or {}) != set(package.get(field) or {}) for field in _FIELDS
    )


def installed(repo: str, commit: str) -> tuple[str, dict, list[Locked]]:
    """(how the packages were read, package.json, every package installed).
    The first of LOCKFILES that is present and not stale is read; with none,
    the registry walk (unlocked). No package.json: no packages."""
    raw = f"https://raw.githubusercontent.com/{repo}/{commit}/"
    try:
        package = _json(f"{raw}package.json")
    except urllib.error.HTTPError:
        return "no package.json at the commit, so no package", {}, []
    refused = []
    for name in LOCKFILES:
        try:
            body = _get(f"{raw}{name}")
        except urllib.error.HTTPError:
            continue
        closure = f"the production closure of {name} at the commit"
        if name == "yarn.lock":
            return closure, package, yarn_lock(body.decode("utf-8"), package)
        if name == "pnpm-lock.yaml":
            pnpm = pnpm_lock(body.decode("utf-8"), package)
            if pnpm is None:
                refused.append(name)
                continue
            return closure, package, pnpm
        lock = json.loads(body.decode("utf-8"))
        if stale(lock, package):
            refused.append(name)
            continue
        return closure, package, npm_lock(lock)
    why = (
        f"{' and '.join(refused)} names other dependencies than package.json"
        if refused
        else "no lockfile this script reads at the commit"
    )
    walk = (
        f"{why}, so the production closure of package.json walked through "
        "registry.npmjs.org at each range's floor"
    )
    return walk, package, unlocked(package)


def enumerate_bundled(
    packages: list[Locked], package: dict, main_js: str | None
) -> list[Locked]:
    """R50: the production closure, plus every package.json devDependency
    whose name in_bundle finds in main.js (each version the lockfile installs),
    less is_host_provided. Without main.js (a plugin already demoted by its own
    licence) only the closure is listed."""
    tokens = set(_NAME_CHAR.findall(main_js)) if main_js is not None else set()
    dev = {
        name
        for name in package.get("devDependencies") or {}
        if main_js is not None and in_bundle(name, main_js, tokens)
    }
    installed = frozenset(p.name for p in packages)
    picked = {
        (p.name, p.version): p
        for p in packages
        if not is_host_provided(p.name, main_js, installed)
        and (p.production or p.name in dev)
    }
    return [picked[key] for key in sorted(picked)]


def licensed(packages: list[Locked]) -> list[dict]:
    """Each package with the licence registry.npmjs.org records for its
    version. A version the registry cannot answer is recorded with licence
    None, which demotes."""
    out = []
    for package in packages:
        metadata = _registry(package.name, package.version or "latest")
        licence = (metadata or {}).get("license")
        if isinstance(licence, dict):
            licence = licence.get("type")
        out.append(
            {
                "name": package.name,
                "version": (metadata or {}).get("version", package.version),
                "licence": licence,
                "url": f"https://www.npmjs.com/package/{package.name}",
            }
        )
    return out


LOAD_DEMOTED = "demoted to recommended by a measured load failure"
_LICENCE_SCREEN = obsidian_plugins.LICENCE_SCREEN


def load_demotion(plugin_id: str) -> obsidian_plugins.Demotion | None:
    """The declaration's Load demotions row for `plugin_id`, or None (R63)."""
    return obsidian_plugins.declared().demotion_for(plugin_id)


def demoted_method(demotion: obsidian_plugins.Demotion, licence_method: str) -> str:
    return (
        f"{LOAD_DEMOTED}: {demotion.error} ({demotion.plugin} {demotion.version} "
        f"on {demotion.host}, measured {demotion.measured}){_LICENCE_SCREEN}"
        f"{licence_method}"
    )


def _licence_method(method: str) -> str:
    """A record's method with any load-demotion prefix taken off."""
    if method.startswith(LOAD_DEMOTED) and _LICENCE_SCREEN in method:
        return method.split(_LICENCE_SCREEN, 1)[1]
    return method


def _write_record(folder: Path, source: dict, files: dict[str, bytes]) -> None:
    # SOURCE.json goes first and is written last: a run that fails between
    # leaves no record vouching for a half-written folder.
    folder.mkdir(parents=True, exist_ok=True)
    for name in ("SOURCE.json", *ASSETS, "LICENSE", "THIRD-PARTY-NOTICES"):
        (folder / name).unlink(missing_ok=True)
    for name, data in files.items():
        (folder / name).write_bytes(data)
    (folder / "SOURCE.json").write_text(
        json.dumps(source, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def reapply(plugin_id: str) -> str:
    """Apply the Load demotions table to the committed record, offline (R63)."""
    folder = PLUGINS / plugin_id
    record = folder / "SOURCE.json"
    try:
        source = json.loads(record.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(
            f"{plugin_id}: no record at {record}; vendor it with network first"
        ) from None
    demotion = load_demotion(plugin_id)
    if demotion is None:
        if source["assets"]:
            return "seeded"
        if not source["redistributable"]:
            return "recommended"  # its licence demoted it; nothing to apply
        raise SystemExit(
            f"{plugin_id}: no load demotion declared and no asset in the record; "
            "re-seeding needs the release assets, so run with network"
        )
    source = {
        **source,
        "assets": {},
        "source": f"https://github.com/{source['repo']}/tree/{source['tag']}",
        "method": demoted_method(demotion, _licence_method(source["method"])),
    }
    _write_record(folder, source, {})
    return "recommended"


def write_plugin(
    plugin_id: str, tag: str, *, registry: str = REGISTRY, today: str | None = None
) -> str:
    repo = resolve_repo(plugin_id, registry)
    commit = commit_for(repo, tag)
    spdx, licence_bytes, holder = licence_at(repo, commit)
    closure, package, packages = installed(repo, commit)
    decision = verdict(spdx, [], holder=holder)
    downloaded: dict[str, bytes] = {}
    banner = None
    main_js = None
    if decision == "seeded":
        urls = {
            a["name"]: a["browser_download_url"] for a in release(repo, tag)["assets"]
        }
        for name in ASSETS:
            if name in urls:
                downloaded[name] = _get(urls[name])
            elif name != "styles.css":
                raise SystemExit(f"{plugin_id} {tag}: release ships no {name}")
        manifest = json.loads(downloaded["manifest.json"].decode("utf-8"))
        if manifest.get("id") != plugin_id or manifest.get("version") != tag:
            raise SystemExit(
                f"{plugin_id}: manifest version {manifest.get('version')!r} "
                f"(id {manifest.get('id')!r}) is not the tag {tag!r}"
            )
        main_js = downloaded["main.js"].decode("utf-8", errors="replace")
    bundled = licensed(enumerate_bundled(packages, package, main_js))
    decision = verdict(spdx, bundled, holder=holder)
    if decision == "seeded":
        banner = copyleft_banner(downloaded["main.js"])
        if banner:
            decision = "recommended"
    licence_decision = decision
    demotion = load_demotion(plugin_id)
    if demotion is not None:
        decision = "recommended"
    if decision != "seeded":
        downloaded = {}
    method = (
        "LICENSE at the tag's commit (SPDX read from its text); bundled is "
        f"{closure}, plus each package.json devDependency whose name occurs "
        "in main.js, less each of Obsidian's documented externals (the sample "
        "plugin's esbuild externals and Node's builtins) that main.js only "
        "require()s, each licence read from "
        "registry.npmjs.org at its version; main.js scanned for a copyleft "
        "licence banner, none found; the assets are the GitHub release "
        "artifacts at the tag"
        if licence_decision == "seeded"
        else f"demoted to recommended: licence {spdx!r}, holder {holder!r}, "
        f"bundled {[(d['name'], d['licence']) for d in bundled]} from {closure}, "
        f"main.js banner {banner!r}"
        + ("" if main_js is not None else " (main.js not fetched)")
    )
    source = {
        "repo": repo,
        "tag": tag,
        "commit": commit,
        "assets": {
            name: hashlib.sha256(data).hexdigest() for name, data in downloaded.items()
        },
        "licence": spdx,
        "bundled": bundled,
        "source": None
        if decision == "seeded"
        else f"https://github.com/{repo}/tree/{tag}",
        # the licence's answer; a load demotion leaves it true (R63)
        "redistributable": licence_decision == "seeded",
        "measured": today or datetime.datetime.now(datetime.UTC).date().isoformat(),
        "method": method if demotion is None else demoted_method(demotion, method),
    }
    files = dict(downloaded)
    if decision == "seeded":
        files["LICENSE"] = licence_bytes
        notices = (
            "\n\n".join(
                f"{d['name']} {d['version']}\nLicence: {d['licence']}\n{d['url']}"
                for d in bundled
            )
            or "No bundled third-party package found at the pin."
        )
        files["THIRD-PARTY-NOTICES"] = (notices + "\n").encode("utf-8")
    _write_record(PLUGINS / plugin_id, source, files)
    return decision


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("plugin_id")
    parser.add_argument("tag", nargs="?")
    parser.add_argument("--registry", default=REGISTRY)
    parser.add_argument(
        "--reapply",
        action="store_true",
        help="apply the Load demotions table to the committed record, offline",
    )
    args = parser.parse_args(argv)
    if args.reapply:
        print(f"{args.plugin_id}: {reapply(args.plugin_id)}")
        return 0
    if args.tag is None:
        parser.error("a tag is required unless --reapply")
    decision = write_plugin(args.plugin_id, args.tag, registry=args.registry)
    print(f"{args.plugin_id} {args.tag}: {decision}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
