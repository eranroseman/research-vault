"""Vendor one Obsidian community plugin at a pinned release (lanes 2-3 spec §4.2, §4.6).

Run by hand, with network: it resolves the plugin's repository from the
community registry, fetches the release assets at the tag byte for byte, reads
the licence at the tag's commit and every runtime dependency's licence from the
npm registry, and writes the plugin folder under
research_vault/templates/obsidian/plugins/<id>/ with LICENSE,
THIRD-PARTY-NOTICES and SOURCE.json. A licence with a source obligation, or one
that cannot be established, makes the plugin recommended: data.json stays, no
asset is written, SOURCE.json says why. The script never edits the declaration
table; a test compares the two.

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
from typing import Any

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
PERMISSIVE = re.compile(
    r"^(MIT|ISC|0BSD|BSD-[123]-Clause|Apache-2\.0|Unlicense|Zlib|CC0-1\.0"
    r"|BlueOak-1\.0\.0|WTFPL|PSF-2\.0|Python-2\.0)$",
    re.IGNORECASE,
)
# The plugin API package: every plugin's bundler marks it external and the
# running app supplies it (`require("obsidian")` in main.js), so none of it is
# in the asset. Often pinned to a git ref the npm registry cannot answer.
HOST_PROVIDED = {"obsidian"}
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
    licence is not established (unknown expression, empty, UNLICENSED)."""
    if not isinstance(licence, str) or not licence.strip():
        return None
    text = licence.strip()
    if " OR " in text or " AND " in text or "(" in text:
        parts = re.split(r"\s+(?:OR|AND)\s+", text.strip("()"))
        verdicts = [has_source_obligation(part) for part in parts]
        if " OR " in text and False in verdicts:
            return False
        return None if None in verdicts else any(verdicts)
    if COPYLEFT.match(text):
        return True
    if PERMISSIVE.match(text):
        return False
    return None


def verdict(licence: str | None, bundled: list[dict], *, holder: str) -> str:
    if has_source_obligation(licence) is not False:
        return "recommended"
    if holder.strip().lower() in PLACEHOLDER_HOLDERS:
        return "recommended"
    for dependency in bundled:
        if has_source_obligation(dependency.get("licence")) is not False:
            return "recommended"
    return "seeded"


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
    holder_match = re.search(
        r"Copyright\s+(?:\(c\)\s*|©\s*)?(?:\d{4}[-\u2013,\s\d]*)?\s*(.+)", text
    )
    holder = holder_match.group(1).strip() if holder_match else ""
    return _spdx_from_text(text), data, holder


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


def _locked_versions(repo: str, commit: str) -> dict[str, str]:
    """name -> version from package-lock.json at the commit (v1, v2 or v3); empty without one."""
    try:
        lock = _json(
            f"https://raw.githubusercontent.com/{repo}/{commit}/package-lock.json"
        )
    except urllib.error.HTTPError:
        return {}
    out = {
        key.removeprefix("node_modules/"): entry["version"]
        for key, entry in (lock.get("packages") or {}).items()
        if key.startswith("node_modules/")
        and "/node_modules/" not in key
        and "version" in entry
    }
    for name, entry in (lock.get("dependencies") or {}).items():
        out.setdefault(name, entry.get("version", ""))
    return out


def bundled_dependencies(repo: str, commit: str) -> list[dict]:
    """Every runtime dependency of package.json at the commit, with the licence
    the npm registry records for the version package-lock.json resolves (or the
    range's floor when there is no lockfile). A version the registry cannot
    answer is recorded with licence None, which demotes. HOST_PROVIDED
    packages are not bundled and are skipped."""
    try:
        package = _json(
            f"https://raw.githubusercontent.com/{repo}/{commit}/package.json"
        )
    except urllib.error.HTTPError:  # no package.json: no declared dependencies
        return []
    locked = _locked_versions(repo, commit)
    out = []
    for name, spec in sorted((package.get("dependencies") or {}).items()):
        if name in HOST_PROVIDED:
            continue
        floor = re.sub(r"^[\^~>=<\s]+", "", str(spec)).split(" ")[0] or "latest"
        version = locked.get(name) or floor
        try:
            metadata = _json(f"https://registry.npmjs.org/{name}/{version}")
            licence = metadata.get("license")
            if isinstance(licence, dict):
                licence = licence.get("type")
            version = metadata.get("version", version)
        except (urllib.error.HTTPError, ValueError):
            licence = None
        out.append(
            {
                "name": name,
                "version": version,
                "licence": licence,
                "url": f"https://www.npmjs.com/package/{name}",
            }
        )
    return out


def write_plugin(
    plugin_id: str, tag: str, *, registry: str = REGISTRY, today: str | None = None
) -> str:
    repo = resolve_repo(plugin_id, registry)
    commit = commit_for(repo, tag)
    spdx, licence_bytes, holder = licence_at(repo, commit)
    bundled = bundled_dependencies(repo, commit)
    decision = verdict(spdx, bundled, holder=holder)
    downloaded: dict[str, bytes] = {}
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
        "redistributable": decision == "seeded",
        "measured": today or datetime.datetime.now(datetime.UTC).date().isoformat(),
        "method": (
            "LICENSE at the tag's commit (SPDX read from its text); package.json "
            "dependencies at the commit, at package-lock.json's version or the range's "
            "floor, resolved against registry.npmjs.org; the assets are the GitHub "
            "release artifacts at the tag"
            if decision == "seeded"
            else f"demoted to recommended: licence {spdx!r}, holder {holder!r}, "
            f"bundled {[(d['name'], d['licence']) for d in bundled]}"
        ),
    }
    folder = PLUGINS / plugin_id
    folder.mkdir(parents=True, exist_ok=True)
    for name in (*ASSETS, "LICENSE", "THIRD-PARTY-NOTICES"):
        (folder / name).unlink(missing_ok=True)
    if decision == "seeded":
        for name, data in downloaded.items():
            (folder / name).write_bytes(data)
        (folder / "LICENSE").write_bytes(licence_bytes)
        notices = (
            "\n\n".join(
                f"{d['name']} {d['version']}\nLicence: {d['licence']}\n{d['url']}"
                for d in bundled
            )
            or "No bundled third-party dependencies declared at the pin."
        )
        (folder / "THIRD-PARTY-NOTICES").write_text(notices + "\n", encoding="utf-8")
    (folder / "SOURCE.json").write_text(
        json.dumps(source, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return decision


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("plugin_id")
    parser.add_argument("tag")
    parser.add_argument("--registry", default=REGISTRY)
    args = parser.parse_args(argv)
    decision = write_plugin(args.plugin_id, args.tag, registry=args.registry)
    print(f"{args.plugin_id} {args.tag}: {decision}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
