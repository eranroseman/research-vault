"""The captured set, and the one lint at the capture-to-compile seam (spec §4.4).

"Captured" is a fact about this vault's evidence layer that nothing external
knows. The set is the citation keys recorded in parseable literature notes
that carry an item key (decision 8) — not the filenames.
"""

import json
import os
import re
from pathlib import Path

from . import clock, frontmatter, links, literature_notes, structure
from .outcome import Outcome, Result
from .pathcodec import RepoPath

CHECK = "captured-set"
LEDGER_PATH = literature_notes.LEDGER_PATH
_CITATION = re.compile(r"\[@(?P<key>[A-Za-z0-9_.:-]+)")
# A line holding `[[` with no `]]` after it: Obsidian reads no link there, so
# `links.find_links` sees none; the first stray `[[` swallows the rest of its
# line, so a line is one row however many it holds.
_UNTERMINATED = re.compile(r"\[\[(?:(?!\]\])[^\n])*$", re.MULTILINE)
_LOCATOR = re.compile(r"^fulltext/(?P<key>[A-Z0-9]{8})\.md$")


def _read_notes(
    vault: Path,
) -> tuple[list[tuple[dict, literature_notes.Provenance]], list[Outcome]]:
    """Every note under literature/ with its tuple — and a row for every note the reader cannot take.

    lifecycle._provenances skips such a note silently, and capture reports it only when its key is
    requested; decision 08 then drops the key from the captured set and so from the CSL file. This
    lint is the mechanism that design relies on: the omission is reported here, never silent.
    """
    entries: list[tuple[dict, literature_notes.Provenance]] = []
    outcomes: list[Outcome] = []
    for path in sorted((vault / "literature").glob("*.md")):
        if structure.is_excluded(path, vault):
            continue
        target = RepoPath(os.fsencode(f"literature/{path.name}"))
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as error:
            outcomes.append(
                Outcome(CHECK, target, Result.UNREACHABLE, f"outage — {error}")
            )  # could not read: no verdict on the note
            continue
        except UnicodeError as error:
            outcomes.append(
                Outcome(
                    CHECK,
                    target,
                    Result.UNMATCHED,
                    f"schema-violation — not UTF-8: {error}",
                )
            )
            continue
        try:
            data, _body = frontmatter.parse(text)
        except frontmatter.FrontmatterError as error:
            outcomes.append(
                Outcome(CHECK, target, Result.UNMATCHED, f"schema-violation — {error}")
            )
            continue
        provenance = literature_notes.read_provenance(text)
        if provenance is None:
            outcomes.append(
                Outcome(
                    CHECK,
                    target,
                    Result.UNMATCHED,
                    "schema-violation — no provenance tuple",
                )
            )
            continue
        entries.append((data, provenance))
    return entries, outcomes


def _notes(vault: Path) -> list[tuple[dict, literature_notes.Provenance]]:
    return _read_notes(vault)[0]


def captured_set(vault_root) -> dict[str, str]:
    return {p.citation_key: p.item_key for _data, p in _notes(Path(vault_root))}


DEAD_LINK = "dead-link"


def literature_paths(vault_root) -> tuple[dict[str, str], dict[str, str]]:
    """Citation key → the note recording it, and title or alias → that note.

    The captured set's own reading (decision 08): the key is the recorded
    `citationKey`, never the filename, so a re-keyed note awaiting propagation
    still resolves under the name its tuple records.
    """
    vault = Path(vault_root)
    by_key: dict[str, str] = {}
    by_name: dict[str, str] = {}
    for path in sorted((vault / "literature").glob("*.md")):
        if structure.is_excluded(path, vault):
            continue
        try:
            text = path.read_text(encoding="utf-8")
            data, _body = frontmatter.parse(text)
        except (OSError, UnicodeError, frontmatter.FrontmatterError):
            continue
        provenance = literature_notes.read_provenance(text)
        if provenance is None:
            continue
        relative = f"literature/{path.name}"
        by_key[provenance.citation_key] = relative
        title = data.get("title")
        if isinstance(title, str) and title:
            by_name.setdefault(title, relative)
        for alias in data.get("aliases", []):
            if isinstance(alias, str) and alias:
                by_name.setdefault(alias, relative)
    return by_key, by_name


def link_index(vault_root) -> links.Index:
    vault = Path(vault_root)
    by_key, by_name = literature_paths(vault)
    return links.Index.build(vault, by_key, by_name)


def _is_path_shaped(link: links.Link) -> bool:
    """#208's split: a target with a `/` or an attachment extension names a file,
    so an unresolved one is `dead-link`; anything else is a would-be citation."""
    extension = link.target.rsplit(".", 1)[-1].lower() if "." in link.target else ""
    return (
        link.kind == "markdown"
        or "/" in link.target
        or extension in links.ATTACHMENT_EXTENSIONS
    )


def _reportable(text: str) -> str:
    """Decoded body text or path, made safe to write to the review queue.

    Two faults, both of which end ``verify`` with a bare ``ValueError`` that
    ``cmd_verify``'s except tuple deliberately excludes — a traceback, not exit 2.

    ``surrogateescape`` keeps an undecodable byte alive as a lone surrogate, and a
    reason carrying one passes ``inbox.validate_reason`` and then raises
    ``UnicodeEncodeError`` inside ``append_entry``'s utf-8 stream. ``RepoPath`` is this
    repo's codec for a non-UTF-8 *path* and the target uses it; body content has no such
    codec, so the byte is replaced rather than encoded.

    A line break fails earlier still: ``Outcome.__post_init__`` validates the reason at
    construction, so an unterminated ``[[`` or a page named ``A\nB.md`` raises inside the
    lint itself. ``literature_notes.display_text``'s idiom is used rather than a newline strip
    because it is total for every separator ``str.splitlines()`` honours.
    """
    decoded = text.encode("utf-8", "surrogateescape").decode("utf-8", "replace")
    return " ".join(decoded.split())


def _textual(vault: Path, keys: set[str]) -> list[Outcome]:
    outcomes: list[Outcome] = []
    wiki = vault / "wiki"
    if not wiki.is_dir():
        return outcomes
    index = link_index(vault)
    for path in sorted(wiki.rglob("*.md")):
        if structure.is_excluded(path, vault):
            continue
        relative = path.relative_to(vault).as_posix()
        reported = _reportable(relative)
        target_path = RepoPath(os.fsencode(relative))
        try:
            # frontmatter scanned with the body (§4.4). surrogateescape, as the sibling
            # residue lint reads its surfaces (propagate.py): a stray byte in one page
            # must not end verify with a UnicodeDecodeError the CLI does not catch.
            text = path.read_text(encoding="utf-8", errors="surrogateescape")
        except OSError as error:
            # One page nobody could read is an outage against that page, not the end
            # of the walk. _read_notes and _structural type the same fault the same
            # way; this was the third read in the file and the last one that did not.
            outcomes.append(
                Outcome(CHECK, target_path, Result.UNREACHABLE, f"outage — {error}")
            )
            continue
        for match in _CITATION.finditer(text):
            key = match.group("key")
            if key not in keys:
                outcomes.append(
                    Outcome(
                        CHECK,
                        target_path,
                        Result.UNMATCHED,
                        f"not-captured — {reported} cites [@{key}], not in the captured set",
                    )
                )
        for link in links.find_links(text):
            # A folder (`[log/](log/)`) names no file: neither dead nor a citation.
            if links.is_uri(link.target) or links.is_folder(link.target):
                continue
            # Reported as written, so the finding's text is what the file says and
            # grepping the vault for it succeeds.
            written = _reportable(link.target)
            verb = "embeds" if link.embed else "links"
            hits = index.resolve(link.target, source=relative)
            if len(hits) == 1:
                continue
            if len(hits) > 1:
                shown = ", ".join(_reportable(hit) for hit in hits)
                outcomes.append(
                    Outcome(
                        CHECK,
                        target_path,
                        Result.UNMATCHED,
                        f"schema-violation — {reported} links [[{written}]], which "
                        f"{len(hits)} files match ({shown}); resolve by hand",
                    )
                )
                continue
            if link.kind == "markdown":
                outcomes.append(
                    Outcome(
                        DEAD_LINK,
                        target_path,
                        Result.UNMATCHED,
                        f"dead-link — {reported} {verb} to {written}, which no file matches",
                    )
                )
            elif _is_path_shaped(link):
                outcomes.append(
                    Outcome(
                        DEAD_LINK,
                        target_path,
                        Result.UNMATCHED,
                        f"dead-link — {reported} {verb} [[{written}]], which no file matches",
                    )
                )
            else:
                outcomes.append(
                    Outcome(
                        CHECK,
                        target_path,
                        Result.UNMATCHED,
                        f"not-captured — {reported} links [[{written}]], "
                        "not a page and not in the captured set",
                    )
                )
        outcomes.extend(
            Outcome(
                CHECK,
                target_path,
                Result.UNMATCHED,
                f"schema-violation — unterminated [[ on {reported}",
            )
            for _line in _UNTERMINATED.finditer(text)
        )
    return outcomes


def _structural(vault: Path, as_of=None) -> list[Outcome]:
    ledger = vault / LEDGER_PATH
    if not ledger.is_file():
        return [
            Outcome(
                CHECK, LEDGER_PATH, Result.SKIPPED, "no-identifier — no source ledger"
            )
        ]
    unreadable = Outcome(
        CHECK,
        RepoPath(os.fsencode(LEDGER_PATH)),
        Result.UNMATCHED,
        "schema-violation — source ledger unreadable",
    )
    try:
        text = ledger.read_text(encoding="utf-8")
    except OSError as error:
        # Could not read: no verdict on content nobody saw (the same split _read_notes makes).
        return [
            Outcome(
                CHECK,
                RepoPath(os.fsencode(LEDGER_PATH)),
                Result.UNREACHABLE,
                f"outage — source ledger unreadable: {error}",
            )
        ]
    except UnicodeError:
        return [unreadable]
    try:
        # .items() belongs inside this guard too: a ledger whose "sources" is an
        # array raises AttributeError here rather than at the loop below.
        records = sorted(json.loads(text).get("sources", {}).items())
    except (ValueError, AttributeError):
        return [unreadable]
    written = {}
    for _data, provenance in _notes(vault):
        for entry in provenance.fulltext:
            written[entry.get("attachment-key")] = (
                provenance.citation_key,
                provenance.compile_input_sha256,
                entry.get("sha256"),
            )
    outcomes = []
    for source_id, record in records:
        origin = record.get("origin", {}) if isinstance(record, dict) else {}
        if origin.get("kind") != "file":
            continue
        locator = str(origin.get("locator", ""))
        match = _LOCATOR.match(locator)
        if match is None or match.group("key") not in written:
            outcomes.append(
                Outcome(
                    CHECK,
                    RepoPath(os.fsencode(LEDGER_PATH)),
                    Result.UNMATCHED,
                    f"not-captured — ledger {source_id} names {locator}, which no capture wrote",
                )
            )
            continue
        _key, _compile_sha, text_sha = written[match.group("key")]
        recorded = record.get("content_sha256")
        if recorded and text_sha and recorded != text_sha:
            outcomes.append(
                Outcome(
                    CHECK,
                    RepoPath(os.fsencode(LEDGER_PATH)),
                    Result.UNMATCHED,
                    f"recompile-needed — ledger {source_id} holds {recorded} for {locator}; the note records {text_sha}",
                )
            )
        if record.get("review_status") == "active":
            # The tool's own predicate (ledgers.py source_is_stale), so the two never disagree about "stale";
            # its lint never calls it, so this is the only reporter (spec §7 at b555d77).
            due = record.get("refresh_due")
            observed = record.get("retrieved_at") or record.get("ingested_at")
            instant = clock.today(as_of)
            stale = (
                not isinstance(due, str)
                or not isinstance(observed, str)
                or observed[:10] > instant
                or due[:10] < instant
            )
            if stale:
                outcomes.append(
                    Outcome(
                        CHECK,
                        RepoPath(os.fsencode(LEDGER_PATH)),
                        Result.UNMATCHED,
                        f"recompile-needed — ledger {source_id} stale: observed {observed}, refresh due {due}, as of {instant}",
                    )
                )
    return outcomes


def lint_captured_set(vault_root, as_of=None) -> list[Outcome]:
    vault = Path(vault_root)
    entries, outcomes = _read_notes(vault)
    keys = {p.citation_key for _data, p in entries}
    outcomes += _textual(vault, keys)
    outcomes += _structural(vault, as_of)
    if all(o.result is Result.SKIPPED for o in outcomes):
        # One verdict per run: the summary row exists only when nothing failed or was
        # unreachable in either half, so a report never says matched and unmatched
        # about one check at once.
        outcomes.insert(0, Outcome(CHECK, CHECK, Result.MATCHED, "matched"))
    return outcomes
