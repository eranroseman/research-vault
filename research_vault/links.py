"""Links: parse, resolve and render Obsidian's two link forms (spec §5.2).

Resolution follows Obsidian 1.13.7's ``getLinkpathDest`` and rendering its
``generateMarkdownLink`` (app.js, read 2026-10-04; paraphrased, the app is
unlicensed): a ``/``-led link is an exact path or nothing; ``./`` and ``../``
are relative to the linking file; anything else tries the exact path, then a
trailing-components match; path matching is case-insensitive; a name without
a dot resolves only as ``<name>.md``. research-vault's extensions:
``literature/`` resolves only through the captured set (a key, a title or an
alias, each matched exactly as recorded), and an unparseable literature file
resolves nowhere; a target ending in ``/`` is a folder (``is_folder``), which
resolves to no file and is never read as ``<name>.md``.
"""

from __future__ import annotations

import posixpath
import re
import urllib.parse
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from . import structure

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from pathlib import Path

# Obsidian 1.13.7's registered non-markdown extensions (image, audio, video,
# pdf, canvas, base); a wikilink target ending in one is an attachment, and an
# unresolved one is `dead-link`, never `not-captured` (designs cluster 2(b)).
ATTACHMENT_EXTENSIONS = frozenset(
    {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "bmp",
        "svg",
        "webp",
        "avif",
        "mp3",
        "wav",
        "m4a",
        "3gp",
        "flac",
        "ogg",
        "oga",
        "opus",
        "mp4",
        "webm",
        "ogv",
        "mov",
        "mkv",
        "pdf",
        "canvas",
        "base",
    }
)
_WIKI = re.compile(r"(?P<embed>!?)\[\[(?P<inner>[^\[\]\n]+?)\]\]")
# A destination is one run without whitespace, with one level of balanced
# parentheses (Obsidian writes `a%20(b)` unencoded); a `[x](dest "title")`
# form is not a link this module reads.
_MARKDOWN = re.compile(
    r"(?P<embed>!?)\[(?P<text>[^\]\n]*)\]\((?P<dest>[^()\s]*(?:\([^()\s]*\)[^()\s]*)*)\)"
)
_URI = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
# `generateMarkdownLink`'s encoder (`YE`, app.js @1254563): only `\`, control
# characters and the space are percent-encoded; `(`, `%` and the rest pass.
_ENCODE = re.compile(r"[\\\x00-\x1f\x7f ]")


@dataclass(frozen=True)
class Link:
    kind: Literal["wiki", "markdown"]
    embed: bool
    target: str
    subpath: str
    alias: str | None
    start: int
    end: int


def is_uri(target: str) -> bool:
    return _URI.match(target.strip()) is not None


def is_folder(target: str) -> bool:
    """A target ending in ``/`` (``[log/](log/)``, ``[[wiki/]]``, ``/``) names a
    folder, not a file: ``Index.resolve`` gives it no hit, and a caller leaves
    it alone and unreported rather than calling it dead."""
    return target.strip().endswith(("/", "\\"))


def _split_subpath(raw: str) -> tuple[str, str]:
    head, sep, tail = raw.partition("#")
    return head, (sep + tail if sep else "")


def find_links(text: str) -> list[Link]:
    """Every link in ``text`` in order of appearance. Nothing is masked here:
    the normaliser decides what a code fence or a claim block protects."""
    found: list[Link] = []
    for match in _WIKI.finditer(text):
        inner = match.group("inner")
        path_part, _, alias = inner.partition("|")
        target, subpath = _split_subpath(path_part)
        found.append(
            Link(
                "wiki",
                match.group("embed") == "!",
                target.strip(),
                subpath.strip(),
                alias if "|" in inner else None,
                match.start(),
                match.end(),
            )
        )
    for match in _MARKDOWN.finditer(text):
        dest = match.group("dest")
        if is_uri(dest):
            target, subpath = dest, ""
        else:
            raw_target, subpath = _split_subpath(dest)
            target = urllib.parse.unquote(raw_target)
        found.append(
            Link(
                "markdown",
                match.group("embed") == "!",
                target,
                subpath,
                match.group("text"),
                match.start(),
                match.end(),
            )
        )
    return sorted(found, key=lambda link: link.start)


class Index:
    """Every non-excluded file outside ``literature/``, plus the captured set."""

    def __init__(
        self,
        files: Iterable[str],
        literature: Mapping[str, str],
        names: Mapping[str, str],
    ) -> None:
        self._exact: dict[str, str] = {}
        self._suffix: dict[str, list[str]] = {}
        for path in files:
            lowered = path.lower()
            self._exact[lowered] = path
            parts = lowered.split("/")
            for start in range(len(parts)):
                self._suffix.setdefault("/".join(parts[start:]), []).append(path)
        self._literature = dict(literature)
        self._literature_exact = {path.lower(): path for path in literature.values()}
        self._names = dict(names)

    @classmethod
    def build(
        cls, vault: Path, literature: Mapping[str, str], names: Mapping[str, str]
    ) -> Index:
        files = []
        for path in sorted(vault.rglob("*")):
            if not path.is_file() or structure.is_excluded(path, vault):
                continue
            relative = path.relative_to(vault)
            if relative.parts[0] == "literature":
                continue  # resolved through the captured set only
            files.append(relative.as_posix())
        return cls(files, literature, names)

    def _exact_hit(self, candidate: str) -> str | None:
        lowered = candidate.lower()
        return self._exact.get(lowered) or self._literature_exact.get(lowered)

    def resolve(self, target: str, *, source: str) -> list[str]:
        """Vault-relative posix paths: none (dead), one (resolved), several (ambiguous).

        An empty target (`[see](#section)`, `[[#heading]]`) is the linking file
        itself, as Obsidian and the compile tool's lint both read it. A folder
        target (``is_folder``) and a URI resolve to none. A bare name is tried
        as an exact path, then as a captured-set key, then as a recorded title
        or alias, and only then by trailing components."""
        raw = target.strip().replace("\\", "/")
        if is_uri(raw):
            return []
        if not raw:
            return [source]
        if is_folder(raw):
            return []  # before normpath, which strips the slash
        if raw.startswith("/"):
            candidate, exact_only = posixpath.normpath(raw.lstrip("/")), True
        elif raw.startswith(("./", "../")):
            candidate = posixpath.normpath(
                posixpath.join(posixpath.dirname(source), raw)
            )
            exact_only = True
        else:
            candidate, exact_only = posixpath.normpath(raw), False
        if candidate in {".", ""} or candidate.startswith("../"):
            return []
        # Obsidian reads `[[Foo.md]]` as `[[Foo]]`: the stem is what the
        # captured set and the names are keyed by.
        stem = (
            candidate[: -len(".md")] if candidate.lower().endswith(".md") else candidate
        )
        dotless = "." not in posixpath.basename(stem)
        wanted = f"{stem}.md" if dotless else candidate
        hit = self._exact_hit(wanted)
        if hit is not None:
            return [hit]
        if exact_only:
            return []
        if dotless and "/" not in stem:
            if stem in self._literature:
                return [self._literature[stem]]
            if stem in self._names:
                return [self._names[stem]]
        return sorted(self._suffix.get(wanted.lower(), []))


def _encode(path: str) -> str:
    return _ENCODE.sub(lambda m: f"%{ord(m.group(0)):02X}", path)


def render_markdown(link: Link, path: str) -> str:
    """``[[x]]`` → ``[basename](/p/x.md)``; alias and subpath carried; embeds
    keep only their alias (a size such as ``480``) as the text."""
    destination = "/" + _encode(path) + _encode(link.subpath)
    if link.embed:
        return f"![{link.alias or ''}]({destination})"
    if link.alias is not None:
        text = link.alias
    else:
        base = posixpath.basename(path)
        text = base.removesuffix(".md")
        if link.subpath:
            text = f"{text} > {link.subpath[1:]}"
    return f"[{text}]({destination})"
