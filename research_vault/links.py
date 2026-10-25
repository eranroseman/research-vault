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

The normaliser rewrites a note's body only; its frontmatter block is never
normalised. Dataview's frontmatter reader takes only ``[[…]]`` as a link, so
a rewritten property would lose its Link type (the reason Q19 masks
``[k:: …]`` fields in the body), while Obsidian core reads both forms there
(app.js ``cD``, per the plan author's ruling of 2026-10-25), so nothing core
is lost; and ``read_okf`` at seal is the YAML gate. This deviates from spec
§5.2, which has the normaliser refuse a rewrite that leaves frontmatter
unparseable: with no rewrite there is nothing to refuse.
"""

from __future__ import annotations

import os
import posixpath
import re
import urllib.parse
from dataclasses import dataclass, field
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
# Obsidian's table escape: in a table it writes `[[x\|y]]`, so the row keeps
# its cells. `\|` separates the alias as `|` does, and its `\` is no part of
# the target, which `_fold` would otherwise turn into a folder's `/` (§5.2).
_ALIAS_SEPARATOR = re.compile(r"\\?\|")
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


def _fold(target: str) -> str:
    """A target as resolution reads it: trimmed, with each ``\\`` as ``/``."""
    return target.strip().replace("\\", "/")


def is_folder(target: str) -> bool:
    """A target ending in ``/`` (``[log/](log/)``, ``[[wiki/]]``, ``/``) names a
    folder, not a file: ``Index.resolve`` gives it no hit, and a caller leaves
    it alone and unreported rather than calling it dead."""
    return _fold(target).endswith("/")


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


def _candidate(target: str, *, source: str) -> tuple[str, bool] | None:
    """The one vault path ``target`` is read as, before any lookup, and
    whether only that exact path may answer it (a ``/``-led or ``./``/``../``
    target, joined to ``source``'s folder). None for a folder (``is_folder``)
    and for a path that leaves the vault. ``Index.resolve`` and ``names_note``
    both read a target through this step, so they cannot read it apart."""
    raw = _fold(target)
    if is_folder(raw):
        return None  # before normpath, which strips the slash
    if raw.startswith("/"):
        candidate, exact_only = posixpath.normpath(raw.lstrip("/")), True
    elif raw.startswith(("./", "../")):
        candidate = posixpath.normpath(posixpath.join(posixpath.dirname(source), raw))
        exact_only = True
    else:
        candidate, exact_only = posixpath.normpath(raw), False
    if candidate in {".", ""} or candidate.startswith("../"):
        return None
    return candidate, exact_only


def _split_subpath(raw: str) -> tuple[str, str]:
    head, sep, tail = raw.partition("#")
    return head, (sep + tail if sep else "")


def _split_alias(inner: str) -> tuple[str, str, str | None]:
    """A wikilink's inside as ``(path part, separator as written, alias)``:
    the separator is ``|`` or a table's ``\\|``; with none, ``("", None)``."""
    separator = _ALIAS_SEPARATOR.search(inner)
    if separator is None:
        return inner, "", None
    return inner[: separator.start()], separator.group(), inner[separator.end() :]


def find_links(text: str) -> list[Link]:
    """Every link in ``text`` in order of appearance. Nothing is masked here:
    the normaliser decides what a code fence or a claim block protects."""
    found: list[Link] = []
    for match in _WIKI.finditer(text):
        path_part, _separator, alias = _split_alias(match.group("inner"))
        target, subpath = _split_subpath(path_part)
        found.append(
            Link(
                "wiki",
                match.group("embed") == "!",
                target.strip(),
                subpath.strip(),
                alias,
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
        if not _fold(target):
            return [source]
        read = _candidate(target, source=source)
        if read is None:
            return []
        candidate, exact_only = read
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


def encode_path(path: str) -> str:
    """``path`` as a markdown destination spells it, as Obsidian's
    ``generateMarkdownLink`` encodes it: ``\\``, control characters and the
    space percent-encoded, everything else as written."""
    return _ENCODE.sub(lambda m: f"%{ord(m.group(0)):02X}", path)


def render_markdown(link: Link, path: str) -> str:
    """``[[x]]`` → ``[basename](/p/x.md)``; alias and subpath carried; embeds
    keep only their alias (a size such as ``480``) as the text."""
    destination = "/" + encode_path(path) + encode_path(link.subpath)
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
# A fence may stand behind a container prefix: a blockquote or callout (`>`),
# a list marker (`-`, `1.`) or any indent. Masking an indented code block
# with it errs safe. A backtick fence's info string holds no backtick
# (CommonMark), so a line led by ```x``` is a code span, not a fence that
# would mask the rest of the file. A closer stands behind quotes and indent
# only: a list marker opens a new container, so a line led by one is content
# (or an opener), never a closer.
_CONTAINER = r"(?:[ \t]*(?:>|[-+*][ \t]|\d{1,9}[.)][ \t]))*[ \t]*"
_QUOTES = r"(?:[ \t]*>)*[ \t]*"
_FENCE = re.compile(rf"({_CONTAINER})(`{{3,}}(?!.*`)|~{{3,}})")
# A code span ends at a blank line, a blockquote's bare `>` line included
# (CommonMark: a span never crosses a paragraph).
_BLANK_LINE = rf"\r?\n{_QUOTES}\r?\n"
_CODE_SPAN = rf"(?<!`)(?P<ticks>`+)(?!`)(?:(?!{_BLANK_LINE}).)+?(?<!`)(?P=ticks)(?!`)"
_HTML_COMMENT = r"<!--.*?(?:-->|\Z)"
_OBSIDIAN_COMMENT = r"%%.*?(?:%%|\Z)"
# One pattern, so the leftmost opener wins: a `%%` in a code span is code,
# a backtick in a comment is comment. It runs with the fences blanked out.
_INLINE_MASK = re.compile(
    f"{_CODE_SPAN}|{_HTML_COMMENT}|{_OBSIDIAN_COMMENT}", re.DOTALL
)
_NOT_LINE_END = re.compile(r"[^\r\n]")


@dataclass(frozen=True)
class Problem:
    """What the normaliser left as written for a person to resolve: a link
    whose target names no file (``dead``) or several (``ambiguous``, with the
    candidates), or a note whose frontmatter block has no closing ``---``
    line (``frontmatter``: the note was not normalised; ``target`` is empty).
    ``written`` is the link's span, or the block's opening line, exactly as
    the text holds it."""

    kind: Literal["dead", "ambiguous", "frontmatter"]
    target: str
    candidates: tuple[str, ...] = ()
    written: str = field(kw_only=True)


def is_normalised_surface(relative: str) -> bool:
    return not any(
        relative == skip or (skip.endswith("/") and relative.startswith(skip))
        for skip in NORMALISER_SKIPS
    )


def _closes(opening: re.Match[str], line: str) -> bool:
    """``line`` ends the fence ``opening`` opened: a run of its character at
    least as long, alone on the line, behind quotes of the same `>` depth
    indented at most three columns away from the opener's (CommonMark). A
    fence quoted, listed or indented inside the code is content, not a
    closer."""
    prefix, run = opening.groups()
    closing = re.match(rf"({_QUOTES}){re.escape(run[0])}{{{len(run)},}}[ \t]*$", line)
    return (
        closing is not None
        and closing.group(1).count(">") == prefix.count(">")
        and abs(len(closing.group(1)) - len(prefix)) <= 3
    )


def _fence_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    fence: tuple[re.Match[str], int] | None = None  # its opener, where it opened
    offset = 0
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        if fence is None:
            opening = _FENCE.match(stripped)
            fence = (opening, offset) if opening else None
        elif _closes(fence[0], stripped):
            spans.append((fence[1], offset + len(line)))
            fence = None
        offset += len(line)
    if fence is not None:
        spans.append((fence[1], len(text)))
    return spans


def _blanked(text: str, spans: list[tuple[int, int]]) -> str:
    """``text`` with every character of ``spans`` but its line ends turned to a
    space: offsets hold, no token inside a span survives, and each of its
    lines reads as blank."""
    pieces: list[str] = []
    cursor = 0
    for start, end in spans:
        pieces += [text[cursor:start], _NOT_LINE_END.sub(" ", text[start:end])]
        cursor = end
    pieces.append(text[cursor:])
    return "".join(pieces)


def _protected_spans(text: str) -> list[tuple[int, int]]:
    """Code fences, then inline code and HTML and Obsidian comments outside
    them, anchored claim blocks whole (Q19: their bytes are frozen by
    claim-immutability), and `[k:: …]` field spans on every other line
    (Dataview reads only `[[…]]` inside a field)."""
    # Imported here: lints is the verify layer above this module, and must
    # stay free to import links (through literature_notes) without a cycle.
    from . import lints

    spans = _fence_spans(text)
    unfenced = _blanked(text, spans)
    spans.extend((m.start(), m.end()) for m in _INLINE_MASK.finditer(unfenced))
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
    target = _fold(link.target)
    return target.startswith(("./", "../")) or (
        link.kind == "markdown" and target.startswith("/")
    )


def _rewrite(text: str, index: Index, source: str) -> tuple[str, list[Problem]]:
    """``text`` normalised, and the links left for a person."""
    spans = _protected_spans(text)
    problems: list[Problem] = []
    pieces: list[str] = []
    cursor = 0
    for link in find_links(text):
        if link.start < cursor or _protected(spans, link) or _unresolvable(link):
            continue
        hits = index.resolve(link.target, source=source)
        if len(hits) != 1:
            problems.append(
                Problem(
                    "ambiguous" if hits else "dead",
                    link.target,
                    tuple(hits),
                    written=text[link.start : link.end],
                )
            )
            continue
        if _kept_as_written(link):
            continue
        # A markdown link's text is its alias, never None, so the renderer
        # keeps it as written; only the destination changes.
        pieces += [text[cursor : link.start], render_markdown(link, hits[0])]
        cursor = link.end
    pieces.append(text[cursor:])
    return "".join(pieces), problems


def normalize(text: str, index: Index, *, source: str) -> tuple[str, list[Problem]]:
    """Rewrite every resolvable wikilink in the body to the markdown form and
    add the `/` to a bare markdown destination that resolves to one file;
    leave URIs, folders, same-page anchors, relative forms, dead and
    ambiguous targets alone, and report every dead and ambiguous one.

    The frontmatter block, opening `---` line through closing delimiter, is
    passed through byte for byte and nothing in it is reported: Dataview
    reads only `[[…]]` as a link in a property, and read_okf at seal is the
    YAML gate (a deviation from §5.2's "refuses a rewrite that leaves
    frontmatter unparseable"; see the module docstring). A note whose block
    has no closing `---` line is not normalised at all, and is reported once.

    What is reported is the caller's to print, not a review-queue row:
    outside `wiki/` a link to a note not yet written is an ordinary act,
    never a refused commit."""
    opening = frontmatter._FRONTMATTER_OPEN.match(text)
    if opening is None:
        return _rewrite(text, index, source)
    closing = frontmatter._FRONTMATTER_CLOSE.search(text, opening.end())
    if closing is None:
        # No closing `---` line (none at all, or a last one with no newline
        # after it, which read_okf also refuses): where the block ends is
        # unknown, so no part of the note is the body.
        opening_line = text[: opening.end()].rstrip("\r\n")
        return text, [Problem("frontmatter", "", written=opening_line)]
    new_body, problems = _rewrite(text[closing.end() :], index, source)
    return text[: closing.end()] + new_body, problems


# --- re-key support for propagate (§5.2 callers, item 2) ------------------------


def names_note(target: str, key: str, *, source: str) -> bool:
    """Whether a link target names ``literature/<key>.md``, read through the
    resolver's own candidate step (``_candidate``): a path to it, ``/``-led,
    relative to ``source`` or neither, with or without ``.md``, matched
    case-insensitively as ``Index.resolve`` matches a path; or, led by
    neither, the bare key, matched exactly as the captured set holds it. A
    folder names no note, and ``/<key>.md`` is the root file, not the note.
    The target is read as given: a markdown one ``find_links`` has already
    decoded, a wikilink one never is. A markdown URI is ``link_names_note``'s
    to skip; a wikilink target never is one, so a key holding a ``:`` is
    still named."""
    read = _candidate(target, source=source)
    if read is None:
        return False
    candidate, exact_only = read
    wanted, name = _forms(candidate)
    note = f"literature/{key}.md".lower()
    if any(form.lower() == note for form in wanted):
        return True
    return not exact_only and name == key


def link_names_note(link: Link, key: str, *, source: str) -> bool:
    """Whether ``link``, in ``source``, names ``literature/<key>.md``
    (``names_note``); a markdown URI (``is_external``) names no note."""
    return not is_external(link) and names_note(link.target, key, source=source)


def rewrite_key(text: str, old: str, new: str, *, source: str) -> str:
    """Rename every link naming ``old``: a wikilink keeps its form (a table's
    ``\\|`` included), a markdown
    link is re-pointed at ``/literature/<new>.md`` with its subpath, and a
    display text equal to the old key, or starting ``<old> > `` as the
    normaliser renders a subpath link, has the key renamed."""
    pieces: list[str] = []
    cursor = 0
    for link in find_links(text):
        if link.start < cursor or not link_names_note(link, old, source=source):
            continue
        bang = "!" if link.embed else ""
        if link.kind == "wiki":
            # The separator as written: a table's `\|` stays escaped. The
            # span's first `|` is its separator: `[[` holds none.
            _path, separator, _alias = _split_alias(text[link.start : link.end])
            alias = f"{separator}{link.alias}" if link.alias is not None else ""
            replacement = f"{bang}[[{new}{link.subpath}{alias}]]"
        else:
            shown = link.alias or ""
            if shown == old or shown.startswith(f"{old} > "):
                shown = new + shown[len(old) :]
            destination = (
                f"/literature/{encode_path(new)}.md{encode_path(link.subpath)}"
            )
            replacement = f"{bang}[{shown}]({destination})"
        pieces.append(text[cursor : link.start])
        pieces.append(replacement)
        cursor = link.end
    pieces.append(text[cursor:])
    return "".join(pieces)
