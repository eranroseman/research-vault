"""Re-key propagation: the one vault-wide mutation over human content (spec §3.5).

Detection belongs to the lifecycle linter. This module computes a plan — the
mapping, the item keys behind it, every surface it will rewrite with that
surface's hash as it stands — applies only against that plan's hash, and keeps
the applied plan under system/propagations/: the record a reader follows a key
through and the residue lint's input (open point 12: the applied plan is the
log). A draft edited between plan and apply changes the hash, and the apply
refuses. Every mapping, whatever its source, is verified against Zotero
before the plan exists and again before the first rename: the note's item
must carry the new name live.
"""

import datetime
import hashlib
import json
import os
import re
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

from . import capture, lifecycle, links, literature_notes, structure
from .outcome import Outcome, Result
from .pathcodec import RepoPath
from .zotero import ZoteroError

PLAN_DIR = ".research-vault/propagate"
RECORD_DIR = "system/propagations"
CHECK = "propagation"
SCHEMA = "research-vault.propagation.v1"
_SKIP_FILES = {"log.md", "inbox/review-queue.md"}
_SKIP_DIRS = {"literature", "fulltext", "log"}


class Surface(NamedTuple):
    path: str
    sha256: str


class Plan(NamedTuple):
    operation_id: str
    date: str
    mapping: dict[str, str]
    item_keys: dict[str, str]
    # A merged loser's citation key -> the survivor's item key (#183, §5.3.6);
    # empty for a re-key. The note is verified against, and recaptured as, the
    # survivor, and apply removes it when the survivor already has a note.
    merges: dict[str, str]
    # A merged loser's citation key -> its note's path, when the survivor
    # already has a note and apply removes the loser's (ADR 0003's scope note
    # of 2026-11-07). Hashed with the rest, so the person approves the removal.
    removes: dict[str, str]
    surfaces: tuple[Surface, ...]


def _cite_pattern(old: str) -> tuple[re.Pattern[str], str]:
    return re.compile(rf"\[@{re.escape(old)}(?=[\],\s])"), "[@{new}"


def _names(text: str, found: list[links.Link], old: str, source: str) -> bool:
    """Whether ``text``, the surface ``source`` with its links ``found`` (one
    ``links.find_links`` pass, shared by every key), cites ``old`` or links
    the note in any spelling ``links.link_names_note`` reads."""
    pattern, _template = _cite_pattern(old)
    return pattern.search(text) is not None or any(
        links.link_names_note(link, old, source=source) for link in found
    )


def _surfaces(vault: Path) -> Iterator[tuple[Path, str]]:
    for path in sorted(vault.rglob("*.md")):
        relative = path.relative_to(vault).as_posix()
        parts = relative.split("/")
        if (
            structure.is_excluded(path, vault)
            or parts[0] in _SKIP_DIRS
            or relative in _SKIP_FILES
            or relative.startswith(RECORD_DIR + "/")
            # Never written through (stamp.py refuses the same), and verify
            # gives a symlink no content identity, so none is hashed either.
            or path.is_symlink()
        ):
            continue
        yield path, relative


# lint_lifecycle's `merged — <survivor item key> (<survivor citation key>)`;
# the item key is zotero.ITEM_KEY's shape.
_MERGED = re.compile(r"^merged — (?P<item>[A-Z0-9]{8}) \((?P<key>[^)]+)\)$")


def _mapping_from_linter(
    vault: Path, client
) -> tuple[dict[str, str], dict[str, str], list[Outcome]]:
    mapping: dict[str, str] = {}
    merges: dict[str, str] = {}
    blocking: list[Outcome] = []
    for outcome in lifecycle.lint_lifecycle(vault, client):
        if outcome.result is Result.UNREACHABLE or (
            outcome.target == "vault" and outcome.result is Result.UNMATCHED
        ):
            blocking.append(outcome)
        elif outcome.result is Result.UNMATCHED and outcome.reason.startswith(
            "re-keyed — "
        ):
            old, new = outcome.reason[len("re-keyed — ") :].split(" → ", 1)
            mapping[old] = new
        elif (
            outcome.result is Result.UNMATCHED
            and (match := _MERGED.match(outcome.reason))
            # A survivor not yet keyed (`?`) has no name to map to; the
            # finding stands until Zotero gives it one.
            and match.group("key") != "?"
        ):
            mapping[str(outcome.target)] = match.group("key")
            merges[str(outcome.target)] = match.group("item")
    return mapping, merges, blocking


def _refusal(old: str, detail: str) -> Outcome:
    return Outcome(CHECK, old, Result.UNMATCHED, f"schema-violation — {detail}")


def _targets(mapping: dict[str, str], merges: dict[str, str]) -> dict[str, str]:
    """Every note one pass touches, old key -> the key it ends under.

    A merge whose survivor carries the loser's own key is an identity entry:
    the survivor is recaptured over the note, nothing is renamed or rewritten,
    and it stays out of the plan's ``mapping`` — a record mapping a key to
    itself would leave every surface naming it stale-key forever. An identity
    re-key does nothing at all and is dropped.
    """
    targets = {old: new for old, new in mapping.items() if old != new or old in merges}
    targets.update({old: old for old in merges if old not in targets})
    return targets


def _holder(target: Path) -> tuple[str, str] | None:
    """``(item key, server id)`` of the note at ``target``, or None."""
    if target.is_symlink():
        return None
    try:
        held = literature_notes.read_provenance(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        return None
    return None if held is None else (held.item_key, held.server_id)


def _occupied_refusal(
    old: str,
    new: str,
    held: tuple[str, str] | None,
    server_id: str,
    survivor: str | None,
) -> Outcome | None:
    """Why ``old``'s note may not land on the occupied target, or None.

    ADR 0003: no transition deletes a literature note, and a POSIX rename over
    an existing file replaces it silently — a dangling symlink too, which
    exists() would not see. A merge is the one exception (ADR 0003's scope
    note of 2026-11-07): apply removes the loser's note, never the target, and
    only when ``held`` — the target's note, or the earlier entry of this plan
    that claimed it — is the survivor's own in the same database; an
    unrelated note at that path would be recaptured over and lost.
    """
    if survivor is None:
        return _refusal(
            old, f"literature/{new}.md already exists; nothing is renamed over it"
        )
    if held != (survivor, server_id):
        return _refusal(
            old,
            f"literature/{new}.md is not item {survivor}'s note; "
            "the loser's note is not removed for it",
        )
    return None


def _hashed_surfaces(
    vault: Path, keys: dict[str, str]
) -> tuple[tuple[Surface, ...], list[Outcome]]:
    """Every surface naming one of ``keys`` with its hash, or a refusal."""
    surfaces = []
    for path, relative in _surfaces(vault):
        data = path.read_bytes()
        text = data.decode("utf-8", errors="surrogateescape")
        found = links.find_links(text)
        if not any(_names(text, found, old, relative) for old in keys):
            continue
        try:
            relative.encode("utf-8")
        except UnicodeEncodeError:
            # The plan is canonical JSON; a path the codec can only spell as
            # bytes has no place in it, and a traceback is not a verdict.
            return (), [
                Outcome(
                    CHECK,
                    RepoPath(os.fsencode(relative)),
                    Result.UNMATCHED,
                    "schema-violation — surface path is not UTF-8; rename it first",
                )
            ]
        surfaces.append(Surface(relative, hashlib.sha256(data).hexdigest()))
    return tuple(surfaces), []


def _sources(
    vault: Path, mapping: dict[str, str]
) -> tuple[dict[str, tuple[Path, literature_notes.Provenance]], list[Outcome]]:
    """The note behind each old key, found by its recorded ``citationKey``.

    Decision 08's identity, not the filename: after a partial apply — an
    outage during the recapture is the realistic route — the note sits at
    ``literature/<new>.md`` still recording ``<old>``, and a plan that opened
    ``literature/<old>.md`` would refuse the very state it produced. Found by
    the recorded key, a re-run treats that note as already at its target.
    """
    by_key: dict[str, list[tuple[Path, literature_notes.Provenance]]] = {}
    by_name: dict[str, literature_notes.Provenance] = {}
    for path, provenance in lifecycle._provenances(vault):
        by_key.setdefault(provenance.citation_key, []).append((path, provenance))
        by_name[path.name] = provenance
    found: dict[str, tuple[Path, literature_notes.Provenance]] = {}
    outcomes: list[Outcome] = []
    for old in mapping:
        candidates = by_key.get(old, [])
        named = f"{old}.md"
        if len(candidates) == 1:
            found[old] = candidates[0]
        elif candidates:
            names = ", ".join(sorted(path.name for path, _ in candidates))
            outcomes.append(
                _refusal(
                    old, f"{len(candidates)} notes record citationKey {old}: {names}"
                )
            )
        elif named in by_name:
            outcomes.append(
                _refusal(
                    old,
                    f"literature/{named} records citationKey "
                    f"{by_name[named].citation_key}, not {old}",
                )
            )
        elif (vault / "literature" / named).is_file():
            outcomes.append(_refusal(old, "note carries no provenance tuple"))
        else:
            outcomes.append(
                _refusal(old, f"no note under literature/ records citationKey {old}")
            )
    return found, outcomes


def plan(
    vault_root,
    client,
    mapping: dict[str, str] | None,
    *,
    merges: dict[str, str] | None = None,
    now=None,
) -> tuple[Plan | None, list[Outcome]]:
    """Compute one re-key pass without touching anything (spec §3.5, decision 01).

    ``merges`` names the entries that are Zotero merges (§5.3.6): each is
    verified against the survivor's item, not the note's, and may land on the
    survivor's existing note, which the plan then ``removes`` the loser's
    note for. Without ``mapping``, the lifecycle linter supplies both.
    """
    vault = Path(vault_root)
    now = now or datetime.datetime.now(datetime.UTC)
    if client is None:
        return None, [
            Outcome(
                CHECK,
                RECORD_DIR,
                Result.UNMATCHED,
                "schema-violation — no Zotero client to verify the mapping against",
            )
        ]
    if mapping is None:
        mapping, merges, blocking = _mapping_from_linter(vault, client)
        if blocking:
            return None, blocking
    merges = dict(merges or {})
    targets = _targets(mapping, merges)
    if not targets:
        return None, [
            Outcome(
                CHECK,
                RECORD_DIR,
                Result.SKIPPED,
                "no-identifier — nothing to propagate",
            )
        ]
    sources, outcomes = _sources(vault, targets)
    item_keys: dict[str, str] = {}
    removes: dict[str, str] = {}
    # Target name -> (item key, server id) of the entry that will hold it.
    # Sorted, so apply walks the same order: a later loser for a path an
    # earlier entry claims (two losers, one note-less survivor) finds it
    # occupied by the survivor-to-be, and is a removal, not a rename over it.
    claimed: dict[str, tuple[str, str]] = {}
    for old, new in sorted(targets.items()):
        if old not in sources:
            continue
        source, provenance = sources[old]
        item_key = merges.get(old, provenance.item_key)
        try:
            target = literature_notes.note_path(vault, new)
        except literature_notes.InvalidCitationKeyError as error:
            outcomes.append(_refusal(old, str(error)))
            continue
        # The note already sitting at its target (a re-run after a partial
        # apply) is not occupied: no rename.
        held = claimed.get(target.name)
        if source.name != target.name and (
            held is not None or target.exists() or target.is_symlink()
        ):
            refusal = _occupied_refusal(
                old,
                new,
                held or _holder(target),
                provenance.server_id,
                merges.get(old),
            )
            if refusal is not None:
                outcomes.append(refusal)
                continue
            removes[old] = f"literature/{source.name}"
        claimed.setdefault(target.name, (item_key, provenance.server_id))
        # The mapping is verified against Zotero whatever its source: the note's
        # item must carry the new name live. A name nobody in the library holds
        # (a --map typo) is refused here, before it can become a rename; the
        # read sends the tuple's server id, so the wrong database is a 412.
        client.server_id = provenance.server_id
        try:
            live = client.item(item_key)["data"].get("citationKey")
        except ZoteroError as error:
            return None, [lifecycle.blocked(CHECK, old, error)]
        if live != new:
            outcomes.append(
                Outcome(
                    CHECK,
                    old,
                    Result.UNMATCHED,
                    f"mismatch — item {item_key} carries citation key "
                    f"{live!r}, not {new!r}",
                )
            )
            continue
        item_keys[old] = item_key
    if outcomes:
        return None, outcomes
    rekeys = {old: new for old, new in targets.items() if old != new}
    surfaces, refused = _hashed_surfaces(vault, rekeys)
    if refused:
        return None, refused
    operation_id = "propagate-" + now.strftime("%Y%m%dT%H%M%SZ")
    return Plan(
        operation_id,
        now.date().isoformat(),
        rekeys,
        item_keys,
        merges,
        removes,
        surfaces,
    ), []


def _document(plan: Plan) -> dict:
    return {
        "schema": SCHEMA,
        "operation_id": plan.operation_id,
        "date": plan.date,
        "mapping": dict(plan.mapping),
        "item_keys": dict(plan.item_keys),
        "merges": dict(plan.merges),
        "removes": dict(plan.removes),
        "surfaces": [surface._asdict() for surface in plan.surfaces],
    }


def _canonical(document: dict) -> str:
    return json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def plan_sha256(plan: Plan) -> str:
    return hashlib.sha256(_canonical(_document(plan)).encode("utf-8")).hexdigest()


def write_plan(vault_root, plan: Plan) -> Path:
    path = Path(vault_root) / PLAN_DIR / f"{plan.operation_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_canonical(_document(plan)), encoding="utf-8")
    return path


def plan_from_document(data, source) -> Plan:
    """A plan or applied record's document, as ``read_plan`` and the
    evidence-layer lint read it; ValueError, KeyError or TypeError otherwise."""
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError(f"not a propagation plan: {source}")
    return Plan(
        str(data["operation_id"]),
        str(data["date"]),
        dict(data["mapping"]),
        dict(data["item_keys"]),
        # Absent from a document written before #183: a re-key.
        dict(data.get("merges", {})),
        dict(data.get("removes", {})),
        tuple(Surface(str(s["path"]), str(s["sha256"])) for s in data["surfaces"]),
    )


def read_plan(path) -> Plan:
    return plan_from_document(json.loads(Path(path).read_text(encoding="utf-8")), path)


def rewrite_surfaces(vault_root, old: str, new: str) -> list[str]:
    vault = Path(vault_root)
    changed = []
    for path, relative in _surfaces(vault):
        # Bytes in, bytes out: line endings kept (newline=""), and the same
        # surrogateescape decoding plan() used, so a surface plan() accepted
        # cannot fail here, after the rename.
        with path.open(
            "r", encoding="utf-8", errors="surrogateescape", newline=""
        ) as handle:
            text = handle.read()
        pattern, template = _cite_pattern(old)
        rewritten = pattern.sub(template.format(new=new), text)
        rewritten = links.rewrite_key(rewritten, old, new, source=relative)
        if rewritten != text:
            with path.open(
                "w", encoding="utf-8", errors="surrogateescape", newline=""
            ) as handle:
                handle.write(rewritten)
            changed.append(relative)
    return changed


def _apply_entry(
    vault: Path,
    client,
    approved: Plan,
    old: str,
    new: str,
    source: Path,
    document: dict,
) -> list[Outcome]:
    """One entry of an approved plan; what it did joins the record ``document``.

    A rename never lands on an existing path or symlink, whatever the plan
    said (P24's backstop): the entry is refused and nothing moves. A merge's
    rename is recorded under ``moved``: the note changes identity with it, so
    the evidence-layer lint cannot pair the two paths and reads the record.

    A planned removal (§5.3.6) waits for the survivor's recapture: the scope
    note's condition is that the survivor's note is re-rendered in the same
    act, so the loser's note goes only once capture's row for the survivor's
    note is MATCHED (written, or already current), and stays — reported —
    otherwise. A text-check row after the render does not hold the removal. ADR 0003's scope note of 2026-11-07 covers the
    deletion; the applied record under system/propagations/ names it.
    """
    removal = approved.removes.get(old)
    target = literature_notes.note_path(vault, new)
    if source.name != target.name and removal is None:
        if target.exists() or target.is_symlink():
            return [
                _refusal(
                    old,
                    f"literature/{new}.md already exists; nothing is renamed over it",
                )
            ]
        source.rename(target)
        if old in approved.merges:
            document["moved"][f"literature/{source.name}"] = f"literature/{target.name}"
    changed = rewrite_surfaces(vault, old, new) if old != new else []
    recapture = capture.capture(vault, client, [approved.item_keys[old]])
    outcomes = [
        Outcome(
            CHECK,
            new,
            Result.MATCHED,
            "matched — rewrote " + (", ".join(changed) or "nothing"),
        )
    ]
    outcomes.extend(o for o in recapture if o.result is not Result.MATCHED)
    if removal is None:
        return outcomes
    if not any(o.result is Result.MATCHED and o.target == new for o in recapture):
        outcomes.append(
            Outcome(
                CHECK,
                old,
                Result.UNMATCHED,
                f"merged — kept {removal}: item {approved.item_keys[old]}'s "
                "recapture did not match; run propagate again",
            )
        )
        return outcomes
    source.unlink()
    document["removed"].append(removal)
    return outcomes


def apply(
    vault_root, client, plan_path, approved_sha256: str, *, now=None
) -> list[Outcome]:
    """Apply a plan only if the vault still computes to the approved hash (decision 01)."""
    vault = Path(vault_root)
    now = now or datetime.datetime.now(datetime.UTC)
    try:
        approved = read_plan(plan_path)
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [
            Outcome(
                CHECK,
                str(plan_path),
                Result.UNMATCHED,
                f"schema-violation — unreadable plan: {error}",
            )
        ]
    if plan_sha256(approved) != approved_sha256:
        return [
            Outcome(
                CHECK,
                approved.operation_id,
                Result.UNMATCHED,
                "mismatch — approved hash does not name this plan",
            )
        ]
    # Verified again, against Zotero, before anything is renamed.
    current, outcomes = plan(
        vault, client, approved.mapping, merges=approved.merges, now=now
    )
    if current is None:
        return outcomes
    current = current._replace(operation_id=approved.operation_id, date=approved.date)
    if plan_sha256(current) != approved_sha256:
        return [
            Outcome(
                CHECK,
                approved.operation_id,
                Result.UNMATCHED,
                "mismatch — plan changed: the vault moved since this plan was "
                "computed; run propagate again",
            )
        ]
    # Resolved again, by recorded key, for the rename itself; the recompute
    # above already proved each note's item key against the approved plan.
    targets = _targets(approved.mapping, approved.merges)
    sources, refused = _sources(vault, targets)
    if refused:
        return refused
    # The approved plan verbatim, then what applying it did, which the
    # evidence-layer lint reads: `removed`, the removals that happened (a
    # planned one whose recapture failed is in `removes` only), and `moved`,
    # each merge loser's note renamed onto the survivor's path.
    document = _document(approved)
    document["applied_at"] = now.replace(microsecond=0).isoformat()
    document["approved_plan_sha256"] = approved_sha256
    document["removed"] = []
    document["moved"] = {}
    outcomes = []
    for old, new in sorted(targets.items()):
        outcomes.extend(
            _apply_entry(vault, client, approved, old, new, sources[old][0], document)
        )
    document["removed"].sort()
    record = vault / RECORD_DIR / f"{approved.operation_id}.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(_canonical(document), encoding="utf-8")
    return outcomes


def read_records(vault_root) -> list[Plan]:
    directory = Path(vault_root) / RECORD_DIR
    if not directory.is_dir():
        return []
    return [
        read_plan(path)
        for path in sorted(directory.glob("*.json"))
        if not structure.is_excluded(path, Path(vault_root))
    ]


def _stale_keys(records: list[Plan]) -> dict[str, tuple[str, str, str | None]]:
    """Old key -> (new key, operation id, item key) after every record, oldest first.

    A later record supersedes an earlier one: a key a later plan mapped *to*
    is a current name again (a→b then b→a leaves only `b` stale), so the fold
    drops it before recording the new mapping. Without this, the first record
    would flag every surface naming `a` forever, and `propagation` closes
    `commit`. The item key rides along so the lint can tell the same item
    back under a retired name from a different item that now holds it.
    """
    stale: dict[str, tuple[str, str, str | None]] = {}
    for record in records:
        for old, new in record.mapping.items():
            stale.pop(new, None)
            stale[old] = (new, record.operation_id, record.item_keys.get(old))
    return stale


def _stale(relative: str, old: str, new: str, operation_id: str) -> Outcome:
    return Outcome(
        CHECK,
        RepoPath(os.fsencode(relative)),
        Result.UNMATCHED,
        f"stale-key — names {old}, mapped to {new} by {operation_id}",
    )


def lint_propagation(vault_root) -> list[Outcome]:
    vault = Path(vault_root)
    try:
        records = read_records(vault)
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [
            Outcome(
                CHECK,
                RepoPath(os.fsencode(RECORD_DIR)),
                Result.UNMATCHED,
                f"schema-violation — unreadable propagation record: {error}",
            )
        ]
    if not records:
        return [
            Outcome(
                CHECK,
                RECORD_DIR,
                Result.SKIPPED,
                "no-identifier — no applied propagation plan",
            )
        ]
    texts: list[tuple[str, str, list[links.Link]]] = []
    outcomes: list[Outcome] = []
    for path, relative in _surfaces(vault):
        # One surface nobody can read is a row against that surface, not the
        # end of the walk: the rest of the vault is still judged for residue.
        # surrogateescape, not a schema-violation row: a stray byte in one page
        # must not cost the page its residue verdict, and that tolerance is this
        # lint's own tested decision (test_lint_rows_an_unreadable_record_and_
        # reads_surfaces_byte_tolerantly). A decode fault therefore cannot reach
        # here; a read the filesystem refuses can, and it is that page's row.
        try:
            text = path.read_text(encoding="utf-8", errors="surrogateescape")
        except OSError as error:
            outcomes.append(
                Outcome(
                    CHECK,
                    RepoPath(os.fsencode(relative)),
                    Result.UNREACHABLE,
                    f"outage — {error}",
                )
            )
            continue
        texts.append((relative, text, links.find_links(text)))
    recorded = {path.name: p for path, p in lifecycle._provenances(vault)}
    for old, (new, operation_id, item_key) in _stale_keys(records).items():
        provenance = recorded.get(f"{old}.md")
        if (
            provenance is not None
            and item_key is not None
            and provenance.item_key != item_key
        ):
            # A different item now holds this name — a fresh item minted under
            # the freed key and captured normally — so the mapping's claim on
            # the name ends: the item key is identity, the name only a name.
            continue
        if (vault / "literature" / f"{old}.md").is_file():
            outcomes.append(_stale(f"literature/{old}.md", old, new, operation_id))
        outcomes.extend(
            _stale(relative, old, new, operation_id)
            for relative, text, found in texts
            if _names(text, found, old, relative)
        )
    return outcomes or [Outcome(CHECK, RECORD_DIR, Result.MATCHED, "matched")]
