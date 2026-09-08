"""The captured set, and the one lint at the capture-to-compile seam (spec §4.4).

"Captured" is a fact about this vault's evidence layer that nothing external
knows. The set is the citation keys recorded in parseable literature notes
that carry an item key (decision 8) — not the filenames.
"""

import json
import os
import re
from pathlib import Path

from . import clock, frontmatter, notes, structure
from .outcome import Outcome, Result
from .pathcodec import RepoPath

CHECK = "captured-set"
LEDGER_PATH = notes.LEDGER_PATH
_CITATION = re.compile(r"\[@(?P<key>[A-Za-z0-9_.:-]+)")
_WIKILINK = re.compile(r"\[\[(?P<target>[^\]#|]+)")
_LOCATOR = re.compile(r"^fulltext/(?P<key>[A-Z0-9]{8})\.md$")


def _read_notes(
    vault: Path,
) -> tuple[list[tuple[dict, notes.Provenance]], list[Outcome]]:
    """Every note under literatures/ with its tuple — and a row for every note the reader cannot take.

    lifecycle._provenances skips such a note silently, and capture reports it only when its key is
    requested; decision 08 then drops the key from the captured set and so from the CSL file. This
    lint is the mechanism that design relies on: the omission is reported here, never silent.
    """
    entries: list[tuple[dict, notes.Provenance]] = []
    outcomes: list[Outcome] = []
    for path in sorted((vault / "literatures").glob("*.md")):
        target = RepoPath(os.fsencode(f"literatures/{path.name}"))
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
        provenance = notes.read_provenance(text)
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


def _notes(vault: Path) -> list[tuple[dict, notes.Provenance]]:
    return _read_notes(vault)[0]


def captured_set(vault_root) -> dict[str, str]:
    return {p.citation_key: p.item_key for _data, p in _notes(Path(vault_root))}


def _aliases(vault: Path) -> set[str]:
    names = set()
    for data, _p in _notes(vault):
        title = data.get("title")
        if isinstance(title, str):
            names.add(title)
        names.update(a for a in data.get("aliases", []) if isinstance(a, str))
    return names


def _page_names(vault: Path) -> set[str]:
    """Every name a wikilink resolves to as a page: the stem, and each trailing path form Obsidian accepts
    (`concepts/Foo`, `wiki/concepts/Foo` for `wiki/concepts/Foo.md`)."""
    names: set[str] = set()
    for path in vault.rglob("*.md"):
        if structure.is_excluded(path, vault):
            continue
        parts = path.relative_to(vault).with_suffix("").parts
        if parts[0] == "literatures":
            continue
        names.update("/".join(parts[k:]) for k in range(len(parts)))
    return names


def _textual(vault: Path, keys: set[str]) -> list[Outcome]:
    outcomes: list[Outcome] = []
    wiki = vault / "wiki"
    if not wiki.is_dir():
        return outcomes
    pages, aliases = _page_names(vault), _aliases(vault)
    for path in sorted(wiki.rglob("*.md")):
        if structure.is_excluded(path, vault):
            continue
        relative = path.relative_to(vault).as_posix()
        # frontmatter scanned with the body (§4.4). surrogateescape, as the sibling
        # residue lint reads its surfaces (propagate.py): a stray byte in one page
        # must not end verify with a UnicodeDecodeError the CLI does not catch.
        text = path.read_text(encoding="utf-8", errors="surrogateescape")
        for match in _CITATION.finditer(text):
            key = match.group("key")
            if key not in keys:
                outcomes.append(
                    Outcome(
                        CHECK,
                        RepoPath(os.fsencode(relative)),
                        Result.UNMATCHED,
                        f"not-captured — {relative} cites [@{key}], not in the captured set",
                    )
                )
        for match in _WIKILINK.finditer(text):
            target = match.group("target").strip()
            target = target.removesuffix(
                ".md"
            )  # Obsidian resolves [[Foo.md]] as [[Foo]]
            if target in keys or target in pages or target in aliases:
                continue
            outcomes.append(
                Outcome(
                    CHECK,
                    RepoPath(os.fsencode(relative)),
                    Result.UNMATCHED,
                    f"not-captured — {relative} links [[{target}]], not a page and not in the captured set",
                )
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
            # its lint never calls it, so this is the only reporter (spec §7 at ac0cfd2).
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
