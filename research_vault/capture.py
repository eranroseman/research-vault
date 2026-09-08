"""The capture verb: the deterministic copy into the vault (ingest spec §3.3).

One verb, per item or batch, keyed by citation key or item key. Reads are
version-checked per item and restart when the item moves; the CSL file is
regenerated whole at the end of the run; NOOP is a result.
"""

import datetime
import time
from pathlib import Path
from typing import NamedTuple

from . import (
    bibliography,
    captured,
    frontmatter,
    fulltext,
    lifecycle,
    notes,
    okf,
    stamp,
)
from .outcome import Outcome, Result
from .zotero import (
    ITEM_KEY,
    DatabaseChangedError,
    NotFoundError,
    ZoteroClient,
    ZoteroError,
)

CHECK = "capture"
MAX_READ_RESTARTS = 3
KEY_WAIT_SECONDS = 10
CSL_TARGET = bibliography.BIB_PATH
# The linter transitions capture will not write over (spec §3.4 step 6): the
# item's identity has moved or gone, and a fresh render would paper over it.
# ``re-keyed`` and ``drift`` are what a refresh repairs, so they proceed.
# ``database-changed`` joins them: capturing a note the linter says records
# another database would re-home it to this database's item of the same key.
_REFUSED = frozenset({"merged", "trashed", "deleted", "database-changed"})


class ItemRead(NamedTuple):
    item: dict
    children: list[dict]
    texts: dict[str, dict | None]  # attachment key -> fulltext response
    version: int


def resolve_keys(
    client: ZoteroClient, keys: list[str], known: dict[str, str] | None = None
) -> dict[str, str | None]:
    """An item key is itself; a captured citation key resolves through its tuple; anything else through /items/top."""
    known = known or {}
    resolved: dict[str, str | None] = {}
    by_citation: dict[str, str] | None = None
    for key in keys:
        if ITEM_KEY.match(key):
            resolved[key] = key
        elif key in known:
            # the linter's trashed/merged/deleted verdict reaches a captured source this way
            resolved[key] = known[key]
        else:
            if by_citation is None:
                items, _ = client.top_items()
                by_citation = {
                    item["data"]["citationKey"]: item["key"]
                    for item in items
                    if isinstance(item.get("data"), dict)
                    and item["data"].get("citationKey")
                }
            resolved[key] = by_citation.get(key)
    return resolved


def _stored(child) -> bool:
    data = child.get("data", {})
    return data.get("itemType") == "attachment" and data.get("linkMode") in {
        "imported_file",
        "imported_url",
    }


def read_item(client: ZoteroClient, item_key: str) -> ItemRead:
    """Steps 1-3 of §3.3, restarted when the item's version moves (§3.3, re-read boundary).

    A ``client.fulltext`` failure propagates to the caller's per-item handler:
    only a 404 is ``None``, and feeding an outage to ``fulltext.verdict`` as
    ``None`` would read it as "no index" — the distinction Task 10 kept out of
    its domain on purpose.
    """
    for _attempt in range(MAX_READ_RESTARTS):
        item = client.item(item_key)
        children = client.children(item_key)
        texts = {c["key"]: client.fulltext(c["key"]) for c in children if _stored(c)}
        again = client.item(item_key)
        if again["version"] == item["version"]:
            return ItemRead(item, children, texts, int(item["version"]))
    raise ZoteroError(
        f"item {item_key} moved during {MAX_READ_RESTARTS} consecutive read passes"
    )


def _wait_for_key(client: ZoteroClient, item_key: str, wait_seconds: float) -> dict:
    """Better BibTeX fills the key after ``fillKeyAfter``; poll to a ceiling (§2)."""
    deadline = time.monotonic() + wait_seconds
    while True:
        item = client.item(item_key)
        if item["data"].get("citationKey"):
            return item
        if time.monotonic() >= deadline:
            return item
        time.sleep(1)


def _attachment_tuple(child) -> dict:
    data = child.get("data", {})
    return {
        "key": child.get("key", ""),
        "version": int(child.get("version", 0)),
        "md5": data.get("md5") or "absent",
        "contentType": data.get("contentType") or "",
        "filename": data.get("filename") or "",
    }


def _best_attachment(item: dict, usable: list[str]) -> str | None:
    href = ((item.get("links") or {}).get("attachment") or {}).get("href", "")
    best = href.rstrip("/").rsplit("/", 1)[-1] if href else None
    if best in usable:
        return best
    return usable[0] if usable else None


def _write_texts(
    vault: Path, read: ItemRead
) -> tuple[list[dict], list[str], list[str]]:
    """Returns (fulltext tuple entries, usable attachment keys, verdict reasons)."""
    entries, usable, reasons = [], [], []
    for att_key, response in read.texts.items():
        verdict = fulltext.verdict(response)
        if not verdict.usable:
            reasons.append(f"{att_key} {verdict.reason}")
            continue
        _path, digest = fulltext.write(vault, att_key, read.item["key"], response)
        entries.append({"attachment-key": att_key, "sha256": digest})
        usable.append(att_key)
    return entries, usable, reasons


def _capture_one(
    vault: Path, read: ItemRead, server_id: str, now: datetime.datetime
) -> list[Outcome]:
    item = read.item
    citation_key = item["data"].get("citationKey")
    # Resolved before anything is written: an unsafe key refuses the whole item.
    path = notes.note_path(vault, citation_key)
    entries, usable, reasons = _write_texts(vault, read)
    best = _best_attachment(item, usable)
    digest_by_key = {e["attachment-key"]: e["sha256"] for e in entries}
    provenance = notes.Provenance(
        server_id=server_id,
        item_key=item["key"],
        item_version=read.version,
        citation_key=citation_key,
        attachments=tuple(
            _attachment_tuple(c)
            for c in read.children
            if c.get("data", {}).get("itemType") == "attachment"
        ),
        fulltext=tuple(entries),
        compile_input_sha256=digest_by_key.get(best) if best else None,
    )
    existing = None
    if path.is_file():
        with path.open("r", encoding="utf-8", newline="") as handle:
            existing = handle.read()
    child_notes = [
        c for c in read.children if c.get("data", {}).get("itemType") == "note"
    ]
    try:
        # Absent until the first compile; the refresh after it completes the note.
        pages = notes.compiled_pages(vault, provenance)
    except notes.LedgerUnreadableError as error:
        # An outage for this item, not an empty view: rendering without the embed
        # would strip ## Compiled and bump generated for a transient fault, so the
        # note is left as it stands.
        return [Outcome(CHECK, citation_key, Result.UNREACHABLE, f"outage — {error}")]
    candidate = notes.render_note(
        item["data"],
        provenance,
        read.children,
        child_notes,
        existing,
        accessed=now.date().isoformat(),
        generated_at=notes.generated_at_now(now),
        pages=pages,
    )
    outcomes = []
    if existing is not None and not notes.content_changed(existing, candidate):
        outcomes.append(Outcome(CHECK, citation_key, Result.MATCHED, "matched — NOOP"))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(candidate)
        outcomes.append(Outcome(CHECK, citation_key, Result.MATCHED, "matched"))
    if not read.texts:
        # Spec §0 (ac0cfd2): a web page, a repository, a program — no stored
        # attachment, nothing to read. The fourth state, not a failure: the note
        # is written, the text checks do not apply, nothing is filed.
        outcomes.append(
            Outcome(
                CHECK,
                citation_key,
                Result.SKIPPED,
                f"no-fulltext — no attachment to read ({item['data'].get('itemType')}); "
                "text checks do not apply",
            )
        )
    elif reasons and best is None:
        outcomes.append(
            Outcome(
                CHECK,
                citation_key,
                Result.UNMATCHED,
                "no-fulltext — " + "; ".join(reasons),
            )
        )
    return outcomes


def _regenerate_csl(
    vault: Path,
    client: ZoteroClient,
    library_name: str | None,
    run_version: int | None,
) -> Outcome:
    """§3.3 step 4: one whole-library read, re-read once if Zotero moved, item.export fallback.

    The library route needs a name, and decision 13 forbids hardcoding one: it is
    read from the item envelope this run, so a run that read no item (a refusal,
    a 404) goes straight to ``item.export`` over the captured keys, which needs none.
    """
    captured_keys = sorted(_captured_keys(vault))
    items = None
    route = "matched"
    if library_name is not None:
        try:
            items = client.library_csl(library_name)
            after = _top_version(client)
            if run_version is not None and after is not None and after != run_version:
                items = client.library_csl(library_name)
        except DatabaseChangedError as error:
            # Never fall into item.export here: neither Better BibTeX call carries
            # Zotero-Server-ID, so the fallback would write the CSL file from
            # whichever database now answers and call it matched. The row targets
            # the vault, not the file: `database-changed` means every recorded
            # version is void, and the CSL file records no server id, so a finding
            # on it would name a condition the file cannot have. What is void is
            # every note this run wrote from the database that answered.
            return Outcome(
                CHECK, "vault", Result.UNMATCHED, f"database-changed — {error}"
            )
        except ZoteroError:
            items = None
    if items is None:
        try:
            items = client.export_csl(captured_keys) if captured_keys else []
            route = "matched — item.export fallback"
        except ZoteroError as error:
            # A JSON-RPC error (a stale captured key after a re-key) is UNMATCHED;
            # only a transport failure is the outage — the four-state split
            # lifecycle.blocked already makes.
            return lifecycle.blocked(CHECK, CSL_TARGET, error)
    selected = [item for item in items if item.get("id") in captured_keys]
    try:
        bibliography.write(vault, selected)
    except bibliography.BibliographyError as error:
        return Outcome(
            CHECK, CSL_TARGET, Result.UNMATCHED, f"schema-violation — {error}"
        )
    return Outcome(CHECK, CSL_TARGET, Result.MATCHED, route)


def _top_version(client: ZoteroClient) -> int | None:
    """Zotero's own library version (decision 13: the BBT library route returns none)."""
    _payload, headers = client._local_json("/api/users/0/items/top?format=versions")
    return client._version_header(headers)


def _captured_keys(vault: Path) -> set[str]:
    return set(captured.captured_set(vault))


def capture(
    vault_root,
    client: ZoteroClient,
    keys,
    *,
    now: datetime.datetime | None = None,
    refresh_all: bool = False,
    key_wait_seconds: float = KEY_WAIT_SECONDS,
) -> list[Outcome]:
    vault = Path(vault_root)
    now = now or datetime.datetime.now(datetime.UTC).replace(microsecond=0)
    try:
        info = client.server_info()
    except ZoteroError as error:
        # A client that still carries an earlier run's server id is refused with
        # 412 before any read; ``blocked`` names that as database-changed.
        return [lifecycle.blocked(CHECK, "vault", error)]
    existing = lifecycle._provenances(vault)
    client.server_id = existing[0][1].server_id if existing else info["server_id"]
    requested = list(keys) + (
        [p.citation_key for _, p in existing] if refresh_all else []
    )
    # The linter runs first, through its one code path (§3.4). A vault-level
    # refusal or outage stops the run; its decision-26 SKIPPED — no note carries
    # a tuple yet — is the first capture into a fresh vault, not a reason to stop.
    linted = lifecycle.lint_lifecycle(vault, client)
    blocking = [
        o for o in linted if o.target == "vault" and o.result is not Result.SKIPPED
    ]
    if blocking:
        return blocking
    # The linter targets citation keys; capture resolves item keys. Join the two
    # through the provenance tuples.
    item_key_of = {p.citation_key: p.item_key for _, p in existing}
    standing: dict[str, Outcome] = {}
    for outcome in linted:
        # Outcome normalises target to str at construction; only the declared
        # union still names RepoPath.
        if isinstance(outcome.target, str):
            standing[item_key_of.get(outcome.target, outcome.target)] = outcome
    # The id the linter sent and Zotero accepted, recorded in every tuple written.
    server_id = client.server_id or info["server_id"]
    outcomes: list[Outcome] = []
    library_name = None
    aborted: Outcome | None = None
    try:
        run_version = _top_version(client)
        resolved = resolve_keys(client, requested, item_key_of)
    except ZoteroError as error:
        return [lifecycle.blocked(CHECK, "vault", error)]
    for requested_key, item_key in resolved.items():
        if item_key is None:
            outcomes.append(
                Outcome(
                    CHECK,
                    requested_key,
                    Result.UNMATCHED,
                    f"not-admitted — {requested_key} is not in the library",
                )
            )
            continue
        prior = standing.get(item_key)
        if (
            prior is not None
            and prior.result is Result.UNMATCHED
            and prior.reason.split(" — ")[0] in _REFUSED
        ):
            outcomes.append(
                Outcome(CHECK, requested_key, Result.UNMATCHED, prior.reason)
            )
            continue
        try:
            read = read_item(client, item_key)
            if not read.item["data"].get("citationKey"):
                keyed = _wait_for_key(client, item_key, key_wait_seconds)
                if not keyed["data"].get("citationKey"):
                    outcomes.append(
                        Outcome(
                            CHECK,
                            requested_key,
                            Result.UNMATCHED,
                            f"unkeyed — item {item_key} has no citation key",
                        )
                    )
                    continue
                # The fill is a save that moves the item's version (sitting
                # 2026-09-07: II7E6CVR 1710 -> 1711 once keyed), so the whole pass
                # is re-read rather than the item swapped under a stale version.
                read = read_item(client, item_key)
            library_name = library_name or read.item.get("library", {}).get("name")
            outcomes.extend(_capture_one(vault, read, server_id, now))
        except DatabaseChangedError as error:
            # The database moved mid-run: stop reading, but let the notes already
            # written be stamped and logged before the vault row ends the list.
            aborted = Outcome(
                CHECK, "vault", Result.UNMATCHED, f"database-changed — {error}"
            )
            break
        except NotFoundError:
            outcomes.append(
                Outcome(
                    CHECK,
                    requested_key,
                    Result.UNMATCHED,
                    f"not-admitted — {item_key} is not in the library",
                )
            )
        except ZoteroError as error:
            outcomes.append(lifecycle.blocked(CHECK, requested_key, error))
        except (
            notes.InvalidCitationKeyError,
            frontmatter.FrontmatterError,
            OSError,
        ) as error:
            # A corrupt existing note reaches render_note as FrontmatterError; the
            # linter cannot see it (read_provenance declines it), so this is the
            # only place it becomes a finding. The OSError branch is the
            # whole-branch review's to reclassify as an outage (deferred).
            outcomes.append(
                Outcome(
                    CHECK,
                    requested_key,
                    Result.UNMATCHED,
                    f"schema-violation — {error}",
                )
            )
    if any(o.reason == "matched" for o in outcomes):
        stamp.stamp_types(vault)
        okf.regenerate_log(vault)
    if aborted is not None:
        # No CSL file from the database that answered after the move.
        return [*outcomes, aborted]
    if library_name is not None or existing:
        outcomes.append(_regenerate_csl(vault, client, library_name, run_version))
    return outcomes
