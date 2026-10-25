"""Links: parse, resolve, render and normalise Obsidian's two link forms (spec §5.2).

Resolution follows Obsidian 1.13.7's ``getLinkpathDest`` and rendering its
``generateMarkdownLink`` (app.js, read 2026-10-04; paraphrased, the app is
unlicensed): a ``/``-led link is an exact path or nothing; ``./`` and ``../``
are relative to the linking file; anything else tries the exact path, then a
trailing-components match; path matching is case-insensitive; a name without
a dot resolves only as ``<name>.md``. research-vault's extensions:
``literature/`` resolves only through the captured set (a key, a title or an
alias, each matched exactly as recorded), and an unparseable literature file
resolves nowhere; a dot followed by neither ``md`` nor a registered attachment
extension is part of the name (``Dr. Smith``, ``v1.2 notes``, ``smith.2020``),
which is tried as written and as ``<name>.md``; a target ending in ``/`` is a
folder (``is_folder``), which resolves to no file and is never read as
``<name>.md``. Only a markdown destination can be a URI (``is_external``),
and the caller skips one before resolving: a wikilink target never is one,
so ``[[ghost:2020]]`` resolves as a name.
"""

from __future__ import annotations

import os
import posixpath
import re
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from . import claims, frontmatter, structure

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

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


def is_external(link: Link) -> bool:
    """A markdown destination with a scheme (``[x](https://a.b)``): a URL, not a
    vault file, so a caller neither resolves nor reports it. A wikilink target
    never is one: ``[[Re: Ghost]]`` and ``[[ghost:2020]]`` are names, since a
    captured-set key may hold a ``:``."""
    return link.kind == "markdown" and is_uri(link.target)


def is_folder(target: str) -> bool:
    """A target ending in ``/`` (``[log/](log/)``, ``[[wiki/]]``, ``/``) names a
    folder, not a file: ``Index.resolve`` gives it no hit, and a caller leaves
    it alone and unreported rather than calling it dead."""
    return target.strip().endswith(("/", "\\"))


def _extension(target: str) -> str | None:
    """What follows the last dot of the last component, lowercased; None for no dot."""
    base = posixpath.basename(target)
    return base.rpartition(".")[2].lower() if "." in base else None


def is_attachment(target: str) -> bool:
    """A target whose last component ends in one of ``ATTACHMENT_EXTENSIONS``."""
    return _extension(target) in ATTACHMENT_EXTENSIONS


def _forms(candidate: str) -> tuple[list[str], str | None]:
    """The paths ``candidate`` may name, most literal first, and the bare name
    the captured set may know it by (None for an attachment)."""
    extension = _extension(candidate)
    if extension is None:
        return [f"{candidate}.md"], candidate
    if extension == "md":
        # Obsidian reads `[[Foo.md]]` as `[[Foo]]`: the stem is what the
        # captured set and the names are keyed by.
        return [candidate], candidate[: -len(".md")]
    if extension in ATTACHMENT_EXTENSIONS:
        return [candidate], None
    # An unregistered "extension" is part of the name: `Dr. Smith`, `smith.2020`.
    return [candidate, f"{candidate}.md"], candidate


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
        files: list[Path] = []
        for root, dirnames, filenames in os.walk(vault):
            here = Path(root)
            # Pruned in place, so the walk never enters `.git/` and its kin: on
            # the commit hook's path, not one stat per object file. A directory
            # is skipped whole only when every path under it is excluded; an
            # OS-litter name excludes a file by its own name, so a directory
            # called `desktop.ini` is still entered, as `rglob` entered it.
            dirnames[:] = [
                name
                for name in dirnames
                if structure.is_os_litter(name)
                or not structure.is_excluded(here / name, vault)
            ]
            for name in filenames:
                path = here / name
                if structure.is_excluded(path, vault) or not path.is_file():
                    continue
                relative = path.relative_to(vault)
                if relative.parts[0] == "literature":
                    continue  # resolved through the captured set only
                files.append(relative)
        return cls((path.as_posix() for path in sorted(files)), literature, names)

    def _exact_hit(self, candidate: str) -> str | None:
        lowered = candidate.lower()
        return self._exact.get(lowered) or self._literature_exact.get(lowered)

    def resolve(self, target: str, *, source: str) -> list[str]:
        """Vault-relative posix paths: none (dead), one (resolved), several (ambiguous).

        An empty target (`[see](#section)`, `[[#heading]]`) is the linking file
        itself, as Obsidian and the compile tool's lint both read it. A folder
        target (``is_folder``) resolves to none. A markdown destination that
        is a URI (``is_external``) is the caller's to skip; a wikilink target
        never is one. A bare name is tried as an exact path, then as a
        captured-set key, then as a recorded title or alias, and only then by
        trailing components; a name whose dot starts no ``md`` or attachment
        extension is tried as written and then as ``<name>.md``."""
        raw = target.strip().replace("\\", "/")
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
        wanted, name = _forms(candidate)
        for form in wanted:
            hit = self._exact_hit(form)
            if hit is not None:
                return [hit]
        if exact_only:
            return []
        if name is not None and "/" not in name:
            if name in self._literature:
                return [self._literature[name]]
            if name in self._names:
                return [self._names[name]]
        return sorted(
            path for form in wanted for path in self._suffix.get(form.lower(), [])
        )


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


# --- the normaliser (§5.2) -----------------------------------------------------

# Never normalised: the machine surfaces capture, publish and the verifier own,
# and the compiled layer (normalised at seal, §5.4) — §5.2's list — plus the
# text layer `fulltext/`, whose files carry a `managed-sha256` a rewrite
# would break (§5.5).
# Everything else — projects/, inbox/, daily/, system/ outside the propagation
# records, root files — is the person's and is kept in the markdown form.
NORMALISER_SKIPS: tuple[str, ...] = (
    "literature/",
    "log/",
    "log.md",
    "inbox/review-queue.md",
    "system/propagations/",
    "wiki/",
    "fulltext/",
)
_FENCE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})")
_INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`).+?(?<!`)\1(?!`)", re.DOTALL)
_HTML_COMMENT = re.compile(r"<!--.*?(?:-->|\Z)", re.DOTALL)
_OBSIDIAN_COMMENT = re.compile(r"%%.*?(?:%%|\Z)", re.DOTALL)


@dataclass(frozen=True)
class Problem:
    """A link the normaliser left as written for a person to resolve: its target
    names no file (``dead``) or several (``ambiguous``, with the candidates), or
    its rewrite would leave the frontmatter unreadable (``frontmatter``)."""

    kind: Literal["dead", "ambiguous", "frontmatter"]
    target: str
    candidates: tuple[str, ...] = ()


def is_normalised_surface(relative: str) -> bool:
    return not any(
        relative == skip or (skip.endswith("/") and relative.startswith(skip))
        for skip in NORMALISER_SKIPS
    )


def _fence_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    fence: tuple[str, int, int] | None = None  # character, length, where it opened
    offset = 0
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        if fence is None:
            opening = _FENCE.match(stripped)
            if opening:
                fence = (opening.group(1)[0], len(opening.group(1)), offset)
        elif re.match(
            rf"^[ ]{{0,3}}{re.escape(fence[0])}{{{fence[1]},}}[ \t]*$", stripped
        ):
            spans.append((fence[2], offset + len(line)))
            fence = None
        offset += len(line)
    if fence is not None:
        spans.append((fence[2], len(text)))
    return spans


def _protected_spans(text: str) -> list[tuple[int, int]]:
    """Code fences, inline code, HTML and Obsidian comments, anchored claim
    blocks whole (Q19: their bytes are frozen by claim-immutability), and
    `[k:: …]` field spans on every other line (Dataview reads only `[[…]]`
    inside a field)."""
    # Imported here: lints is the verify layer above this module, and must
    # stay free to import links (through literature_notes) without a cycle.
    from . import lints

    spans = _fence_spans(text)
    for pattern in (_INLINE_CODE, _HTML_COMMENT, _OBSIDIAN_COMMENT):
        spans.extend((m.start(), m.end()) for m in pattern.finditer(text))
    for block in lints._claim_blocks(text).values():
        start = text.find(block)
        while start != -1:
            spans.append((start, start + len(block)))
            start = text.find(block, start + 1)
    spans.extend((m.start(), m.end()) for m in claims.FIELD_RE.finditer(text))
    return spans


def _protected(spans: list[tuple[int, int]], link: Link) -> bool:
    return any(
        start <= link.start < end or start < link.end <= end for start, end in spans
    )


def _unresolvable(link: Link) -> bool:
    """Not a vault file to resolve: a URL, a folder, or a same-page anchor —
    the linking file itself, which as a `/`-led path would break on `git mv`."""
    return is_external(link) or is_folder(link.target) or not link.target.strip()


def _kept_as_written(link: Link) -> bool:
    """A relative target in either form (§5.2), or a markdown destination that
    is already `/`-led: resolved, and so reported if dead, but never rewritten."""
    target = link.target.strip().replace("\\", "/")
    return target.startswith(("./", "../")) or (
        link.kind == "markdown" and target.startswith("/")
    )


def _rewrite(
    text: str, index: Index, source: str
) -> tuple[str, list[Problem], list[Link]]:
    """``text`` normalised, the links left for a person, and the links rewritten."""
    spans = _protected_spans(text)
    problems: list[Problem] = []
    rewritten: list[Link] = []
    pieces: list[str] = []
    cursor = 0
    for link in find_links(text):
        if link.start < cursor or _protected(spans, link) or _unresolvable(link):
            continue
        hits = index.resolve(link.target, source=source)
        if len(hits) != 1:
            problems.append(
                Problem("ambiguous" if hits else "dead", link.target, tuple(hits))
            )
            continue
        if _kept_as_written(link):
            continue
        # A markdown link's text is its alias, never None, so the renderer
        # keeps it as written; only the destination changes.
        pieces += [text[cursor : link.start], render_markdown(link, hits[0])]
        rewritten.append(link)
        cursor = link.end
    pieces.append(text[cursor:])
    return "".join(pieces), problems, rewritten


def normalize(text: str, index: Index, *, source: str) -> tuple[str, list[Problem]]:
    """Rewrite every resolvable wikilink to the markdown form and add the `/`
    to a bare markdown destination that resolves to one file; leave URIs,
    folders, same-page anchors, relative forms, dead and ambiguous targets
    alone, and report every dead and ambiguous one. The frontmatter block is
    rewritten only if the result still reads as YAML. What is reported is
    the caller's to print, not a review-queue row: outside `wiki/` a link to
    a note not yet written is an ordinary act, never a refused commit."""
    opening = frontmatter._FRONTMATTER_OPEN.match(text)
    closing = (
        frontmatter._FRONTMATTER_CLOSE.search(text, opening.end()) if opening else None
    )
    if opening is None or closing is None:
        new_text, problems, _ = _rewrite(text, index, source)
        return new_text, problems
    head = text[: opening.end()]
    block = text[opening.end() : closing.start()]
    delimiter = text[closing.start() : closing.end()]
    new_body, problems, _ = _rewrite(text[closing.end() :], index, source)
    new_block, block_problems, rewritten = _rewrite(block, index, source)
    if rewritten:
        try:
            frontmatter.read_okf(head + new_block + delimiter)
        except frontmatter.FrontmatterError:
            # An unquoted `related: [[x]]` would become `related: [x](/p/x.md)`,
            # a flow sequence followed by junk: the block is kept as written and
            # every link that would have been rewritten is reported with it.
            kept = [Problem("frontmatter", link.target) for link in rewritten]
            return head + block + delimiter + new_body, kept + block_problems + problems
    return head + new_block + delimiter + new_body, block_problems + problems
