"""The capture verb: the deterministic copy into the vault (ingest spec §3.3).

One verb, per item or batch, keyed by citation key or item key. Reads are
version-checked per item and restart when the item moves; the CSL file is
regenerated whole at the end of the run; NOOP is a result.
"""

import datetime
import os
import time
from collections.abc import Mapping
from pathlib import Path
from typing import NamedTuple

from . import (
    bibliography,
    captured,
    frontmatter,
    fulltext,
    lifecycle,
    literature_notes,
    okf,
    stamp,
)
from .keystore import (  # noqa: F401 -- re-exported for the tests' patch targets
    KEY_STORE,
    _forget_key,
    _load_key,
    _store_key,
)
from .outcome import Outcome, Result
from .pathcodec import RepoPath
from .zotero import (
    ITEM_KEY,
    ApiKeyRejectedError,
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
# ``database-changed`` joins the refused set: capturing a note the linter says
# records another database would re-home it to this database's item of the
# same key. ``drift`` is what a refresh repairs, so it proceeds; ``re-keyed``
# proceeds only once the old note is gone (``_refused``: the rename is
# propagation's).
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
    ``None`` would read it as "no index".
    """
    for _attempt in range(MAX_READ_RESTARTS):
        item = client.item(item_key)
        children = client.children(item_key)
        texts = {
            c["key"]: client.fulltext(c["key"])
            for c in children
            if _stored(c) and isinstance(c.get("key"), str)
        }
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
    path = literature_notes.note_path(vault, citation_key)
    entries, usable, reasons = _write_texts(vault, read)
    best = _best_attachment(item, usable)
    digest_by_key = {e["attachment-key"]: e["sha256"] for e in entries}
    provenance = literature_notes.Provenance(
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
        pages = literature_notes.compiled_pages(vault, provenance)
    except literature_notes.LedgerUnreadableError as error:
        # An outage for this item, not an empty view: rendering without the embed
        # would strip ## Compiled and bump generated for a transient fault, so the
        # note is left as it stands.
        return [Outcome(CHECK, citation_key, Result.UNREACHABLE, f"outage — {error}")]
    candidate = literature_notes.render_note(
        item["data"],
        provenance,
        read.children,
        child_notes,
        existing,
        accessed=now.date().isoformat(),
        generated_at=literature_notes.generated_at_now(now),
        pages=pages,
    )
    outcomes = []
    if existing is not None and not literature_notes.content_changed(
        existing, candidate
    ):
        outcomes.append(Outcome(CHECK, citation_key, Result.MATCHED, "matched — NOOP"))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(candidate)
        outcomes.append(Outcome(CHECK, citation_key, Result.MATCHED, "matched"))
    if not read.texts:
        # Spec §0 (b555d77): a web page, a repository, a program — no stored
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


def _every_note(vault: Path) -> tuple[list[str], list[Outcome]]:
    """--all: every note under literature/, by its recorded citationKey — tuple or not.

    A note without a tuple is an older vault's, captured once to acquire one; a note
    that cannot even be named is a row, never a silent omission.
    """
    keys: list[str] = []
    outcomes: list[Outcome] = []
    for path in sorted((vault / "literature").glob("*.md")):
        target = RepoPath(os.fsencode(f"literature/{path.name}"))
        try:
            data, _body = frontmatter.parse(path.read_text(encoding="utf-8"))
        except OSError as error:
            outcomes.append(
                Outcome(CHECK, target, Result.UNREACHABLE, f"outage — {error}")
            )
            continue
        except (UnicodeError, frontmatter.FrontmatterError) as error:
            outcomes.append(
                Outcome(CHECK, target, Result.UNMATCHED, f"schema-violation — {error}")
            )
            continue
        key = data.get("citationKey")
        if isinstance(key, str) and key:
            keys.append(key)
        else:
            outcomes.append(
                Outcome(
                    CHECK,
                    target,
                    Result.UNMATCHED,
                    "schema-violation — no citationKey to request by",
                )
            )
    return keys, outcomes


def _standing_by_item_key(
    linted: list[Outcome], item_key_of: dict[str, str]
) -> dict[str, Outcome]:
    """The linter's outcome per item key; a target it cannot join stays under its own name."""
    return {
        # Outcome normalises target to str at construction; only the declared
        # union still names RepoPath.
        item_key_of.get(outcome.target, outcome.target): outcome
        for outcome in linted
        if isinstance(outcome.target, str)
    }


def _read_keyed(
    client: ZoteroClient, item_key: str, key_wait_seconds: float
) -> ItemRead | None:
    """One whole read pass, or None when the item has no citation key to name it.

    Better BibTeX fills the key after ``fillKeyAfter`` (§2); an unkeyed item is
    polled to the ceiling. The fill is a save that moves the item's version
    (sitting 2026-09-07: II7E6CVR 1710 -> 1711 once keyed), so the pass is
    re-read whole rather than the item swapped under a stale version.
    """
    read = read_item(client, item_key)
    if read.item["data"].get("citationKey"):
        return read
    keyed = _wait_for_key(client, item_key, key_wait_seconds)
    if not keyed["data"].get("citationKey"):
        return None
    return read_item(client, item_key)


def _refused(vault: Path, prior: Outcome | None, requested_key: str) -> Outcome | None:
    """The linter's standing this item is not written over, or None to proceed.

    A ``_REFUSED`` transition is refused outright. ``re-keyed`` is refused only
    while ``literature/<old>.md`` still exists: rendering under the live key
    would leave a second note beside it, and ``propagate.plan`` refuses to
    rename over an existing file — the file renames only on a re-key, and the
    propagation task set performs it (spec §3.1). ``propagate.apply`` renames
    before it recaptures, and a partial-apply re-run finds the note already at
    ``<new>.md``, so the old path is gone in both and the recapture proceeds.
    """
    if prior is None or prior.result is not Result.UNMATCHED:
        return None
    code = prior.reason.split(" — ")[0]
    if code in _REFUSED:
        return Outcome(CHECK, requested_key, Result.UNMATCHED, prior.reason)
    if code != "re-keyed":
        return None
    try:
        old_note = literature_notes.note_path(vault, prior.target)
    except literature_notes.InvalidCitationKeyError:
        # A recorded key no filename can carry is a hand edit this check
        # cannot place; capture proceeds as it did before the check existed.
        return None
    if not old_note.is_file():
        return None
    return Outcome(
        CHECK, requested_key, Result.UNMATCHED, f"{prior.reason}; run propagate"
    )


def capture(
    vault_root,
    client: ZoteroClient,
    keys,
    *,
    now: datetime.datetime | None = None,
    refresh_all: bool = False,
    key_wait_seconds: float = KEY_WAIT_SECONDS,
) -> list[Outcome]:
    """The capture verb (spec §3.3): the linter first, then one read and one
    render per requested item, then the CSL file whole.

    ``keys`` are item keys or citation keys (``resolve_keys``); ``refresh_all``
    adds every note under ``literature/`` by its recorded ``citationKey``.
    Returns one ``Outcome`` per requested item — plus a ``vault`` row when a
    vault-level read or refusal ends the run, and the CSL file's row when the
    run reached it. Nothing is written for a refused, unkeyed or unreadable
    item; NOOP is ``matched — NOOP``.
    """
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
    all_keys, unrequestable = _every_note(vault) if refresh_all else ([], [])
    requested = list(keys) + all_keys
    # The linter runs first, through its one code path (§3.4). A vault-level
    # refusal or outage stops the run; its decision-26 SKIPPED — no note carries
    # a tuple yet — is the first capture into a fresh vault, not a reason to stop.
    linted = lifecycle.lint_lifecycle(vault, client)
    blocking = [
        o for o in linted if o.target == "vault" and o.result is not Result.SKIPPED
    ]
    if blocking:
        # `unrequestable` (--all's `_every_note` rows) is already computed
        # here, before `outcomes` even exists; a vault-level lint refusal
        # must not silently drop it either (ADR 0002, same shape as the
        # _top_version/resolve_keys failure below).
        return [*unrequestable, *blocking]
    # The linter targets citation keys; capture resolves item keys. Join the two
    # through the provenance tuples.
    item_key_of = {p.citation_key: p.item_key for _, p in existing}
    standing = _standing_by_item_key(linted, item_key_of)
    # The id the linter sent and Zotero accepted, recorded in every tuple written.
    server_id = client.server_id or info["server_id"]
    outcomes: list[Outcome] = []
    outcomes.extend(unrequestable)
    library_name = None
    aborted: Outcome | None = None
    try:
        run_version = _top_version(client)
        resolved = resolve_keys(client, requested, item_key_of)
    except ZoteroError as error:
        # `outcomes` may already hold `_every_note`'s unrequestable rows
        # (--all); a vault-level failure here must not silently drop them
        # (ADR 0002).
        return [*outcomes, lifecycle.blocked(CHECK, "vault", error)]
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
        refusal = _refused(vault, standing.get(item_key), requested_key)
        if refusal is not None:
            outcomes.append(refusal)
            continue
        try:
            read = _read_keyed(client, item_key, key_wait_seconds)
            if read is None:
                outcomes.append(
                    Outcome(
                        CHECK,
                        requested_key,
                        Result.UNMATCHED,
                        f"unkeyed — item {item_key} has no citation key",
                    )
                )
                continue
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
        except OSError as error:
            # A disk fault writing fulltext/ or reading the existing note is an
            # outage for this item, never a verdict on the record (ADR 0002).
            outcomes.append(
                Outcome(CHECK, requested_key, Result.UNREACHABLE, f"outage — {error}")
            )
        except (
            literature_notes.InvalidCitationKeyError,
            frontmatter.FrontmatterError,
        ) as error:
            # A corrupt existing note reaches render_note as FrontmatterError; the
            # linter cannot see it (read_provenance declines it), so this is the
            # only place it becomes a finding.
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


_ITEM_FIELDS = frozenset(literature_notes.SNAPSHOT_FIELDS) | {"collections"}


def _validate_items(items) -> str | None:
    if not isinstance(items, list) or not items or len(items) > 50:
        return "items must be a non-empty list of at most 50 objects"
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            return f"item {index}: not an object"
        if not isinstance(item.get("itemType"), str) or not item["itemType"]:
            return f"item {index}: itemType missing"
        for field_name in item:
            if field_name != "itemType" and field_name not in _ITEM_FIELDS:
                return f"item {index}: unknown field {field_name}"
        for list_field in ("creators", "tags"):
            if list_field in item and not isinstance(item[list_field], list):
                return f"item {index}: {list_field} must be a list"
    return None


def add(
    vault_root, client: ZoteroClient, items, *, collection=None, now=None
) -> list[Outcome]:
    """Path A: authorize once, create, poll for the citation key, capture (§2)."""
    vault = Path(vault_root)
    problem = _validate_items(items)
    if problem:
        return [
            Outcome(CHECK, "add", Result.UNMATCHED, f"schema-violation — {problem}")
        ]
    try:
        info = client.server_info()
    except ZoteroError as error:
        return [
            lifecycle.blocked(CHECK, "add", error)
        ]  # 412 database-changed, 403 not-admitted, else outage
    existing = lifecycle._provenances(vault)
    client.server_id = existing[0][1].server_id if existing else info["server_id"]
    if client.server_id != info["server_id"]:
        return [
            Outcome(
                CHECK,
                "add",
                Result.UNMATCHED,
                f"database-changed — notes record {client.server_id}, Zotero answers {info['server_id']}",
            )
        ]
    payload = [
        dict(item, **({"collections": [collection]} if collection else {}))
        for item in items
    ]
    key = client.api_key or _load_key(
        vault, client.server_id
    )  # a preset key (RV_LIVE_WRITE_KEY) wins over the store
    for attempt in (1, 2):
        if key is None:
            try:
                granted = client.authorize()
            except ZoteroError as error:
                # 412 database-changed, 403 not-admitted, a denial not-admitted,
                # a rate limit or a transport failure outage: one split.
                return [lifecycle.blocked(CHECK, "add", error)]
            key = granted["key"]
            if granted["remember"]:
                _store_key(vault, client.server_id, key)
        client.api_key = key
        try:
            envelope = client.create_items(payload)
            break
        except ZoteroError as error:
            if isinstance(error, ApiKeyRejectedError) and attempt == 1:
                key = None
                client.api_key = None
                _forget_key(vault, client.server_id)
                continue
            return [lifecycle.blocked(CHECK, "add", error)]
    successful = envelope.get("successful")
    created = [
        entry["key"]
        for entry in (successful.values() if isinstance(successful, Mapping) else ())
        if isinstance(entry, dict) and entry.get("key")
    ]
    if envelope.get("failed") or not created:
        return [
            Outcome(
                CHECK,
                "add",
                Result.UNMATCHED,
                f"mismatch — create failed: {envelope.get('failed')}",
            )
        ]
    outcomes = [
        Outcome(CHECK, "add", Result.MATCHED, "matched — created " + ", ".join(created))
    ]
    return outcomes + capture(vault, client, created, now=now)
