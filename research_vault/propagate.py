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

from . import capture, lifecycle, notes, structure
from .outcome import Outcome, Result
from .pathcodec import RepoPath
from .zotero import ZoteroError

PLAN_DIR = ".research-vault/propagate"
RECORD_DIR = "system/propagations"
CHECK = "propagation"
SCHEMA = "research-vault.propagation.v1"
_SKIP_FILES = {"log.md", "inbox/review-queue.md"}
_SKIP_DIRS = {"literatures", "fulltext", "log"}


class Surface(NamedTuple):
    path: str
    sha256: str


class Plan(NamedTuple):
    operation_id: str
    date: str
    mapping: dict[str, str]
    item_keys: dict[str, str]
    surfaces: tuple[Surface, ...]


def _patterns(old: str) -> list[tuple[re.Pattern[str], str]]:
    key = re.escape(old)
    return [
        (re.compile(rf"\[@{key}(?=[\],\s])"), "[@{new}"),
        (re.compile(rf"\[\[{key}(?=[\]#|])"), "[[{new}"),
    ]


def _names(text: str, old: str) -> bool:
    return any(pattern.search(text) for pattern, _ in _patterns(old))


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


def _mapping_from_linter(vault: Path, client) -> tuple[dict[str, str], list[Outcome]]:
    mapping: dict[str, str] = {}
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
    return mapping, blocking


def _refusal(old: str, detail: str) -> Outcome:
    return Outcome(CHECK, old, Result.UNMATCHED, f"schema-violation — {detail}")


def _sources(
    vault: Path, mapping: dict[str, str]
) -> tuple[dict[str, tuple[Path, notes.Provenance]], list[Outcome]]:
    """The note behind each old key, found by its recorded ``citationKey``.

    Decision 08's identity, not the filename: after a partial apply — an
    outage during the recapture is the realistic route — the note sits at
    ``literatures/<new>.md`` still recording ``<old>``, and a plan that opened
    ``literatures/<old>.md`` would refuse the very state it produced. Found by
    the recorded key, a re-run treats that note as already at its target.
    """
    by_key: dict[str, list[tuple[Path, notes.Provenance]]] = {}
    by_name: dict[str, notes.Provenance] = {}
    for path, provenance in lifecycle._provenances(vault):
        by_key.setdefault(provenance.citation_key, []).append((path, provenance))
        by_name[path.name] = provenance
    found: dict[str, tuple[Path, notes.Provenance]] = {}
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
                    f"literatures/{named} records citationKey "
                    f"{by_name[named].citation_key}, not {old}",
                )
            )
        elif (vault / "literatures" / named).is_file():
            outcomes.append(_refusal(old, "note carries no provenance tuple"))
        else:
            outcomes.append(
                _refusal(old, f"no note under literatures/ records citationKey {old}")
            )
    return found, outcomes


def plan(
    vault_root, client, mapping: dict[str, str] | None, *, now=None
) -> tuple[Plan | None, list[Outcome]]:
    """Compute one re-key pass without touching anything (spec §3.5, decision 01)."""
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
        mapping, blocking = _mapping_from_linter(vault, client)
        if blocking:
            return None, blocking
    if not mapping:
        return None, [
            Outcome(
                CHECK,
                RECORD_DIR,
                Result.SKIPPED,
                "no-identifier — nothing to propagate",
            )
        ]
    sources, outcomes = _sources(vault, mapping)
    item_keys: dict[str, str] = {}
    for old, new in mapping.items():
        if old not in sources:
            continue
        source, provenance = sources[old]
        try:
            target = notes.note_path(vault, new)
        except notes.InvalidCitationKeyError as error:
            outcomes.append(_refusal(old, str(error)))
            continue
        if source.name != target.name and (target.exists() or target.is_symlink()):
            # ADR 0003: no transition deletes a literature note, and a POSIX
            # rename over an existing file replaces it silently. The note
            # already sitting at its target is the one exception: no rename.
            outcomes.append(
                _refusal(
                    old,
                    f"literatures/{new}.md already exists; nothing is renamed over it",
                )
            )
            continue
        # The mapping is verified against Zotero whatever its source: the note's
        # item must carry the new name live. A name nobody in the library holds
        # (a --map typo) is refused here, before it can become a rename; the
        # read sends the tuple's server id, so the wrong database is a 412.
        client.server_id = provenance.server_id
        try:
            live = client.item(provenance.item_key)["data"].get("citationKey")
        except ZoteroError as error:
            return None, [lifecycle.blocked(CHECK, old, error)]
        if live != new:
            outcomes.append(
                Outcome(
                    CHECK,
                    old,
                    Result.UNMATCHED,
                    f"mismatch — item {provenance.item_key} carries citation key "
                    f"{live!r}, not {new!r}",
                )
            )
            continue
        item_keys[old] = provenance.item_key
    if outcomes:
        return None, outcomes
    surfaces = []
    for path, relative in _surfaces(vault):
        data = path.read_bytes()
        text = data.decode("utf-8", errors="surrogateescape")
        if not any(_names(text, old) for old in mapping):
            continue
        try:
            relative.encode("utf-8")
        except UnicodeEncodeError:
            # The plan is canonical JSON; a path the codec can only spell as
            # bytes has no place in it, and a traceback is not a verdict.
            return None, [
                Outcome(
                    CHECK,
                    RepoPath(os.fsencode(relative)),
                    Result.UNMATCHED,
                    "schema-violation — surface path is not UTF-8; rename it first",
                )
            ]
        surfaces.append(Surface(relative, hashlib.sha256(data).hexdigest()))
    operation_id = "propagate-" + now.strftime("%Y%m%dT%H%M%SZ")
    return Plan(
        operation_id, now.date().isoformat(), dict(mapping), item_keys, tuple(surfaces)
    ), []


def _document(plan: Plan) -> dict:
    return {
        "schema": SCHEMA,
        "operation_id": plan.operation_id,
        "date": plan.date,
        "mapping": dict(plan.mapping),
        "item_keys": dict(plan.item_keys),
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


def read_plan(path) -> Plan:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError(f"not a propagation plan: {path}")
    return Plan(
        str(data["operation_id"]),
        str(data["date"]),
        dict(data["mapping"]),
        dict(data["item_keys"]),
        tuple(Surface(str(s["path"]), str(s["sha256"])) for s in data["surfaces"]),
    )


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
        rewritten = text
        for pattern, template in _patterns(old):
            rewritten = pattern.sub(template.format(new=new), rewritten)
        if rewritten != text:
            with path.open(
                "w", encoding="utf-8", errors="surrogateescape", newline=""
            ) as handle:
                handle.write(rewritten)
            changed.append(relative)
    return changed


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
    current, outcomes = plan(vault, client, approved.mapping, now=now)
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
    sources, refused = _sources(vault, approved.mapping)
    if refused:
        return refused
    outcomes = []
    for old, new in approved.mapping.items():
        source, _provenance = sources[old]
        target = notes.note_path(vault, new)
        if source.name != target.name:
            source.rename(target)
        changed = rewrite_surfaces(vault, old, new)
        recapture = capture.capture(vault, client, [approved.item_keys[old]])
        outcomes.append(
            Outcome(
                CHECK,
                new,
                Result.MATCHED,
                "matched — rewrote " + (", ".join(changed) or "nothing"),
            )
        )
        outcomes.extend(o for o in recapture if o.result is not Result.MATCHED)
    record = vault / RECORD_DIR / f"{approved.operation_id}.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    document = _document(approved)
    document["applied_at"] = now.replace(microsecond=0).isoformat()
    document["approved_plan_sha256"] = approved_sha256
    record.write_text(_canonical(document), encoding="utf-8")
    return outcomes


def read_records(vault_root) -> list[Plan]:
    directory = Path(vault_root) / RECORD_DIR
    if not directory.is_dir():
        return []
    return [read_plan(path) for path in sorted(directory.glob("*.json"))]


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
    texts = [
        (relative, path.read_text(encoding="utf-8", errors="surrogateescape"))
        for path, relative in _surfaces(vault)
    ]
    recorded = {path.name: p for path, p in lifecycle._provenances(vault)}
    outcomes: list[Outcome] = []
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
        if (vault / "literatures" / f"{old}.md").is_file():
            outcomes.append(_stale(f"literatures/{old}.md", old, new, operation_id))
        outcomes.extend(
            _stale(relative, old, new, operation_id)
            for relative, text in texts
            if _names(text, old)
        )
    return outcomes or [Outcome(CHECK, RECORD_DIR, Result.MATCHED, "matched")]
