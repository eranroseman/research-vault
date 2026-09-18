"""The lifecycle linter: one check, one code path (ingest spec §3.4).

Three reads answer every transition: the whole versions map (children and
annotations included), the trash map, and the top-level items, which alone
carry ``citationKey`` and ``relations.dc:replaces``. Every key in a note's
tuple is compared, because Zotero versions objects independently (§9).
"""

from collections.abc import Mapping
from pathlib import Path
from typing import NamedTuple

from . import fulltext, literature_notes
from .outcome import Outcome, Result
from .zotero import DatabaseChangedError, ZoteroClient, ZoteroError

CHECK = "lifecycle"
# First transition that matches wins; merged outranks deleted and trashed
# because Zotero trashes a merge's predecessor and a later purge removes it.
# classify's branch order below implements this precedence; exported for the
# docs, never iterated.
ORDER = ("database-changed", "merged", "deleted", "trashed", "re-keyed", "drift")


class Live(NamedTuple):
    versions: dict[str, int]
    trash: dict[str, int]
    # item key -> {"citationKey": str | None, "replaces": set[str]}
    top: dict[str, dict]


def replaces_keys(relations) -> set[str]:
    """``dc:replaces`` is a Zotero URI or a list of them; the key is the last segment."""
    if relations is None:
        return set()
    values = relations if isinstance(relations, list) else [relations]
    return {
        str(v).rstrip("/").rsplit("/", 1)[-1]
        for v in values
        if isinstance(v, str) and v
    }


def read_live(client: ZoteroClient) -> Live:
    versions, _ = client.versions()
    trash = client.trash_versions()
    items, _ = client.top_items()
    top: dict[str, dict] = {}
    for item in items:
        # A malformed row (a null row, `data: null`, `relations` not an
        # object) reads as carrying nothing rather than ending the run with
        # an AttributeError that no caller's `except ZoteroError` sees.
        if not isinstance(item, Mapping):
            continue
        data = item.get("data")
        if not isinstance(data, Mapping):
            data = {}
        relations = data.get("relations")
        key = item.get("key")
        if isinstance(key, str):
            top[key] = {
                "citationKey": data.get("citationKey"),
                "replaces": replaces_keys(
                    relations.get("dc:replaces")
                    if isinstance(relations, Mapping)
                    else None
                ),
            }
    return Live(versions, trash, top)


def _successor(item_key: str, live: Live) -> str | None:
    for key, entry in live.top.items():
        if item_key in entry["replaces"]:
            return key
    return None


def classify(provenance: literature_notes.Provenance, live: Live) -> tuple[str, str]:
    key = provenance.item_key
    successor = _successor(key, live)
    if successor is not None:
        return "merged", successor
    if key not in live.versions:
        return ("trashed", key) if key in live.trash else ("deleted", key)
    # Spec §3.4 step 6 puts trashed before re-keyed, and step 4 makes any key in
    # the trash set — an attachment's included — a trashed note.
    for attachment in provenance.attachments:
        att_key = attachment.get("key")
        if att_key in live.trash:
            return "trashed", str(att_key)
    live_key = live.top.get(key, {}).get("citationKey")
    if live_key and live_key != provenance.citation_key:
        return "re-keyed", f"{provenance.citation_key} → {live_key}"
    moved: list[str] = []
    if live.versions[key] != provenance.item_version:
        moved.append(f"item {key} {provenance.item_version} → {live.versions[key]}")
    for attachment in provenance.attachments:
        att_key = attachment.get("key")
        recorded = attachment.get("version")
        current = live.versions.get(att_key) if isinstance(att_key, str) else None
        if current is None:
            moved.append(f"attachment {att_key} absent")
        elif current != recorded:
            moved.append(f"attachment {att_key} {recorded} → {current}")
    if moved:
        return "drifted", "; ".join(moved)
    return "current", ""


def _drift_detail(
    client: ZoteroClient,
    vault: Path,
    provenance: literature_notes.Provenance,
    detail: str,
) -> str:
    """Name whether a moved attachment's file changed or only its metadata did (§3.4 step 5)."""
    if "attachment" not in detail:
        return detail
    live_md5: dict[str, object] = {}
    try:
        for child in client.children(provenance.item_key):
            child_key = child.get("key")
            if isinstance(child_key, str):
                live_md5[child_key] = child.get("data", {}).get("md5")
    except ZoteroError:
        return detail + "; children unreadable"
    notes_out: list[str] = []
    cached = {f.get("attachment-key"): f.get("sha256") for f in provenance.fulltext}
    for attachment in provenance.attachments:
        key = attachment.get("key")
        if key not in live_md5 or f"attachment {key}" not in detail:
            continue
        file_changed = live_md5[key] != attachment.get("md5")
        text_changed = False
        if key in cached:
            path = fulltext.path_for(vault, key)
            text_changed = not path.is_file() or fulltext.sha256_of(path) != cached[key]
        notes_out.append(
            f"{key}: {'file changed' if file_changed else 'metadata only'}"
            + (", cached text stale" if text_changed else "")
        )
    return detail + ("; " + "; ".join(notes_out) if notes_out else "")


def _provenances(vault: Path) -> list[tuple[Path, literature_notes.Provenance]]:
    found: list[tuple[Path, literature_notes.Provenance]] = []
    for path in sorted((vault / "literature").glob("*.md")):
        try:
            provenance = literature_notes.read_provenance(
                path.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError):
            continue
        if provenance is not None:
            found.append((path, provenance))
    return found


def blocked(check: str, target, error: ZoteroError) -> Outcome:
    """A typed refusal is a verdict, an outage is not (ADR 0002).

    ``DatabaseChangedError`` (412: another database is answering) is the one
    refusal with a code of its own, ``database-changed``, and it is named here
    so that no caller has to catch it ahead of the split (Tasks 13 and 17 do
    not). ``LocalApiDisabledError`` (403: the local-API preference is off) carries
    ``result=UNMATCHED`` and names a condition a person can fix; reporting it
    as an outage would tell them to wait for something that will not change.
    Only ``error.result is UNREACHABLE`` — a refused connection, a 500, a
    malformed body — is the outage the four-state rule says never reads as a
    pass. Every verb's vault-level Zotero read routes its ``ZoteroError`` here.
    """
    if isinstance(error, DatabaseChangedError):
        return Outcome(check, target, Result.UNMATCHED, f"database-changed — {error}")
    if error.result is Result.UNREACHABLE:
        return Outcome(check, target, Result.UNREACHABLE, f"outage — {error}")
    return Outcome(check, target, Result.UNMATCHED, f"not-admitted — {error}")


def lint_lifecycle(vault_root, client: ZoteroClient, provenances=None) -> list[Outcome]:
    """One outcome per captured note, or one ``vault`` row when the read fails.

    Sets ``client.server_id`` to the lowest recorded id before the three reads,
    so every request carries the tuple's id and a different database is a 412.
    The caller's client keeps that id afterwards: ``capture`` reads it back as
    the id Zotero accepted and records it in every tuple it writes.
    """
    vault = Path(vault_root)
    pairs = provenances if provenances is not None else _provenances(vault)
    if not pairs:
        # Decision 26: nothing depends on Zotero yet, so the check does not
        # apply; say so rather than vanish.
        return [
            Outcome(
                CHECK,
                "vault",
                Result.SKIPPED,
                "no-identifier — no note carries a provenance tuple",
            )
        ]
    recorded_ids = {p.server_id for _, p in pairs}
    client.server_id = min(recorded_ids)
    try:
        live = read_live(client)
    except DatabaseChangedError as error:
        return [
            Outcome(
                CHECK,
                "vault",
                Result.UNMATCHED,
                f"database-changed — {error}; every recorded version is void",
            )
        ]
    except ZoteroError as error:
        return [blocked(CHECK, "vault", error)]  # 403 is not-admitted, not an outage
    outcomes: list[Outcome] = []
    for _path, provenance in pairs:
        if provenance.server_id != client.server_id:
            outcomes.append(
                Outcome(
                    CHECK,
                    provenance.citation_key,
                    Result.UNMATCHED,
                    f"database-changed — note records {provenance.server_id}",
                )
            )
            continue
        state, detail = classify(provenance, live)
        if state == "current":
            outcomes.append(
                Outcome(CHECK, provenance.citation_key, Result.MATCHED, "matched")
            )
            continue
        code = "drift" if state == "drifted" else state
        if state == "drifted":
            detail = _drift_detail(client, vault, provenance, detail)
        outcomes.append(
            Outcome(
                CHECK, provenance.citation_key, Result.UNMATCHED, f"{code} — {detail}"
            )
        )
    return outcomes
