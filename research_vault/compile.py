"""The compile wrapper: selection, locators, ledger records, invocation (spec §4.5).

Glue. It names ``fulltext/<attachment key>.md`` as each source's locator,
fills the tool's source-ledger record from the captured metadata, and drives
the tool's own ``transaction inspect`` / ``transaction apply``. It never
writes under ``wiki/`` itself and carries no prompt.
"""

import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from . import captured, clock, frontmatter, literature_notes, paths
from .outcome import Outcome, Result

LEDGER_PATH = literature_notes.LEDGER_PATH
LEDGER_SCHEMA = "claude-obsidian.source-ledger.v1"
BUNDLE_SCHEMA = "claude-obsidian.transaction.v1"
PLUGIN_ID = "claude-obsidian@agricidaniel-claude-obsidian"
CHECK = "compile"
BUNDLE_DIR = ".research-vault/compile"
# The one spelling of a file-kind origin: the record's own origin.kind and
# the stable_source_id() call that hashes it must always agree, or the id
# would no longer match what the record itself declares.
FILE_KIND = "file"
# How many same-second bundle names _claim_bundle tries before it gives up.
# A bound, not `while True`: the loop must not be able to spin under any
# mutation of its counter (a timeout verdict is environment-dependent), and
# a thousand plans in one second is not a case the wrapper serves.
_BUNDLE_CLAIM_ATTEMPTS = 1000


class BundleClaimError(OSError):
    """No free ``research-vault-compile-<stamp>[-N].json`` within the bound.

    An ``OSError`` so the CLI's named-failure net maps it to exit 2 — the
    verb could not run — never a silent overwrite of an earlier plan.
    """


class ToolMissingError(RuntimeError):
    """The compile tool cannot run: not installed and machine.json names no
    root, or the resolved root has no ``scripts/claude-obsidian.py`` (a stale
    ``claude_obsidian_root`` or ``installPath``). An outage on either leg,
    never a mismatch — the message names what to fix."""


def stable_source_id(kind: str, locator: str, content_sha256: str | None) -> str:
    """Byte-for-byte the tool's ``ledgers.stable_source_id`` (read at ad67087; byte-identical at 32ac5a0)."""
    normalized = (
        PurePosixPath(locator).as_posix() if kind.casefold() == "file" else locator
    )
    # No explicit "utf-8": str.encode()'s default codec already is utf-8, so
    # naming it leaves a literal a mutation gate can flip with no observable
    # effect (Global Constraints: "no literal codec names").
    digest = hashlib.sha256(
        f"{kind.casefold()}\0{normalized}\0{(content_sha256 or '').casefold()}".encode(
            errors="surrogatepass"
        )
    ).hexdigest()
    return f"src-{digest[:20]}"


def tool_root(vault_root) -> Path | None:
    config = paths.load_machine_config(Path(vault_root))
    override = config.get("claude_obsidian_root")
    if isinstance(override, str) and override.strip():
        return Path(override)
    from .scaffold import _installed_plugins

    records = _installed_plugins().get(PLUGIN_ID) or []
    install_path = records[0].get("installPath") if records else None
    return Path(install_path) if isinstance(install_path, str) else None


def tool_script(vault_root) -> Path:
    """The tool's entry script under the resolved root, or ``ToolMissingError``."""
    root = tool_root(Path(vault_root))
    if root is None:
        raise ToolMissingError("claude-obsidian is not installed")
    script = root / "scripts" / "claude-obsidian.py"
    if not script.is_file():
        raise ToolMissingError(f"claude-obsidian script not found: {script}")
    return script


def _selected_notes(vault: Path, keys):
    wanted = set(keys)
    for path in sorted((vault / "literature").glob("*.md")):
        try:
            # bytes.decode()'s default codec already is utf-8, so this carries
            # no literal codec name a mutation gate could flip with no effect.
            text = path.read_bytes().decode()
        except (OSError, UnicodeError):
            # Skipped exactly as an unparseable note is (read_provenance ->
            # None); captured-set/okf-frontmatter are where it's reported.
            continue
        provenance = literature_notes.read_provenance(text)
        if provenance is None or provenance.citation_key not in wanted:
            continue
        data, _ = frontmatter.parse(text)
        yield provenance, data


def ledger_record(citation_key, provenance, data, today) -> tuple[str, dict] | None:
    if not provenance.compile_input_sha256:
        return None
    key = next(
        (
            f["attachment-key"]
            for f in provenance.fulltext
            if f.get("sha256") == provenance.compile_input_sha256
        ),
        None,
    )
    if key is None:
        return None
    locator = f"fulltext/{key}.md"
    record = {
        "origin": {"kind": FILE_KIND, "locator": locator},
        "content_kind": "document",
        "authority": "unknown",
        "review_status": "unreviewed",
        "title": str(data.get("title") or citation_key),
        "content_sha256": provenance.compile_input_sha256,
        "ingested_at": today,
        "retrieved_at": str(data.get("accessed") or today),
        "refresh_due": None,
        "independence_key": citation_key,
        "supersedes": None,
        "pages": [],
    }
    return stable_source_id(FILE_KIND, locator, provenance.compile_input_sha256), record


def records_for(vault_root, keys, *, today=None) -> dict[str, dict]:
    vault = Path(vault_root)
    today = clock.today(today)
    records = {}
    for provenance, data in _selected_notes(vault, keys):
        entry = ledger_record(provenance.citation_key, provenance, data, today)
        if entry:
            records[entry[0]] = entry[1]
    return records


def select(vault_root, keys, *, today=None) -> tuple[dict[str, dict], list[Outcome]]:
    """The records a selection registers, and one row per requested key that
    registers nothing (four-state: a skipped selection must not read as clean).

    ``UNMATCHED … not-captured`` for a key outside the captured set — the
    capture-to-compile seam's own code (spec §4.4) — and ``SKIPPED …
    no-fulltext`` for a captured note whose ``compile-input-sha256`` is
    absent or names no ``fulltext[]`` entry: the fourth state, as ``capture``
    reports an item with no attachment to read. Each requested key answers
    once, in request order.
    """
    vault = Path(vault_root)
    records = records_for(vault, keys, today=today)
    registered = {record["independence_key"] for record in records.values()}
    known = captured.captured_set(vault)
    rows = []
    for key in dict.fromkeys(keys):
        if key in registered:
            continue
        if key in known:
            rows.append(
                Outcome(
                    CHECK,
                    key,
                    Result.SKIPPED,
                    "no-fulltext — no compile input recorded; nothing to register",
                )
            )
        else:
            rows.append(
                Outcome(
                    CHECK,
                    key,
                    Result.UNMATCHED,
                    "not-captured — no literature note; capture it first",
                )
            )
    return records, rows


def _same_locator(record, locator: str) -> bool:
    """Whether a ledger record's ``origin.locator`` is ``locator``.

    Only a record in the tool's shape (an object whose ``origin`` is an
    object) can match; anything else is left alone for the tool's own
    validation to report.
    """
    if not isinstance(record, dict):
        return False
    origin = record.get("origin")
    return isinstance(origin, dict) and origin.get("locator") == locator


def _claim_bundle(bundle_dir: Path, stamp: str) -> tuple[str, Path, BinaryIO]:
    """The first unclaimed ``research-vault-compile-<stamp>[-N].json``, created
    exclusively, with its operation id.

    Two plans within one second (a re-run after a refused apply) would
    otherwise name one path and the second would silently overwrite the
    first. Exclusive creation, not an existence check, so two processes
    cannot claim the same path either; the suffix stays inside the tool's
    operation-id charset (``[A-Za-z0-9-_.]``, at most 128). The loop is
    bounded by ``_BUNDLE_CLAIM_ATTEMPTS`` so that no mutation of its counter
    can spin it; past the bound it raises ``BundleClaimError``.
    """
    for attempt in range(_BUNDLE_CLAIM_ATTEMPTS):
        operation_id = f"research-vault-compile-{stamp}" + (
            f"-{attempt}" if attempt else ""
        )
        path = bundle_dir / f"{operation_id}.json"
        try:
            return operation_id, path, path.open("xb")
        except FileExistsError:
            continue
    raise BundleClaimError(
        f"no free bundle path under {bundle_dir} after {_BUNDLE_CLAIM_ATTEMPTS} attempts"
    )


def _run(script: Path, vault: Path, *args) -> subprocess.CompletedProcess:
    # The wrapper's own interpreter, not a bare `python3` looked up on PATH:
    # it is the one known to exist (a missing one was an uncaught
    # FileNotFoundError). ruff PLW1510 requires `check=` spelled out
    # explicitly; `False` is subprocess.run's own default, so a
    # `check=False` -> `check=None` mutant is behaviorally equivalent (both
    # are falsy to the `if check` test inside subprocess.run). Baselined
    # (R21): mutation-baseline.txt already carries the identical shape for
    # gitstate.py's own `_git`.
    return subprocess.run(
        [sys.executable, str(script), *args, "--vault", str(vault)],
        capture_output=True,
        text=True,
        check=False,
    )


def plan(vault_root, keys, *, today=None) -> tuple[Path, dict]:
    """Write the bundle registering the selection and run ``transaction inspect``.

    Raises ``ToolMissingError`` when the tool cannot run and
    ``literature_notes.LedgerUnreadableError`` when the ledger exists but is not the
    tool's document — an outage, never an empty ledger to merge into (the
    same split ``literature_notes.compiled_pages`` makes).
    """
    vault = Path(vault_root)
    script = tool_script(vault)
    today = clock.today(today)
    ledger = vault / LEDGER_PATH
    if ledger.is_file():
        try:
            raw = ledger.read_bytes()
            current = json.loads(raw)
        except (OSError, ValueError) as error:
            raise literature_notes.LedgerUnreadableError(
                f"{LEDGER_PATH} unreadable: {error}"
            ) from error
        if not isinstance(current, dict):
            raise literature_notes.LedgerUnreadableError(
                f"{LEDGER_PATH} unreadable: not an object"
            )
        expected = hashlib.sha256(raw).hexdigest()
        mode = "replace"
    else:
        current = {
            "schema": LEDGER_SCHEMA,
            "generated_at": f"{today}T00:00:00Z",
            "sources": {},
        }
        expected = None
        mode = "create"
    sources = dict(current.get("sources", {}))
    for source_id, record in records_for(vault, keys, today=today).items():
        # A changed text has a new id, and the record it replaces must go (R30):
        # the tool checks every file record's content_sha256 against the
        # file's current bytes on every bundle, so a stale record for the same
        # locator wedges every later compile, vault-wide. The new record names
        # the retired id; pages[] is not carried — pages are the tool's (spec
        # §4.5), filled once its pages exist, and a stale embed would
        # misrepresent the refreshed note. At most one record per locator
        # survives this rule, so `stale` holds several only for a ledger
        # written before it.
        locator = record["origin"]["locator"]
        stale = [
            existing_id
            for existing_id, existing in sources.items()
            if existing_id != source_id and _same_locator(existing, locator)
        ]
        for existing_id in stale:
            del sources[existing_id]
        if stale:
            record["supersedes"] = stale[-1]
        # An id already registered keeps its record: its review_status and
        # pages[] are the tool's (spec §4.5, R19).
        sources.setdefault(source_id, record)
    merged = {
        **current,
        "schema": LEDGER_SCHEMA,
        "generated_at": f"{today}T00:00:00Z",
        "sources": sources,
    }
    content = json.dumps(merged, indent=2, sort_keys=True) + "\n"
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    bundle_dir = vault / BUNDLE_DIR
    bundle_dir.mkdir(parents=True, exist_ok=True)
    operation_id, bundle_path, handle = _claim_bundle(bundle_dir, stamp)
    bundle = {
        "schema": BUNDLE_SCHEMA,
        "operation_id": operation_id,
        "operation_type": "ingest",
        "expected_hashes": {LEDGER_PATH: expected},
        "writes": [
            {
                "path": LEDGER_PATH,
                "mode": mode,
                "content": content,
                "sha256": hashlib.sha256(content.encode()).hexdigest(),
            }
        ],
    }
    # A binary handle + str.encode()'s default utf-8: no literal codec name
    # here either, same reasoning as _selected_notes' read.
    with handle:
        handle.write((json.dumps(bundle, indent=2) + "\n").encode())
    completed = _run(script, vault, "transaction", "inspect", str(bundle_path))
    try:
        inspected = json.loads(completed.stdout) if completed.stdout else {}
    except ValueError:
        inspected = {}
    inspected.setdefault("exit", completed.returncode)
    inspected.setdefault("stderr", completed.stderr.strip())
    return bundle_path, inspected


def apply(vault_root, bundle_path, approved_sha256) -> Outcome:
    vault = Path(vault_root)
    operation = Path(bundle_path).stem
    try:
        script = tool_script(vault)
    except ToolMissingError as error:
        return Outcome(CHECK, operation, Result.UNREACHABLE, f"outage — {error}")
    completed = _run(
        script,
        vault,
        "transaction",
        "apply",
        str(bundle_path),
        "--approved-plan-sha256",
        approved_sha256,
    )
    if completed.returncode == 0:
        try:
            changed = json.loads(completed.stdout).get("changed_paths", [])
        except ValueError:
            changed = []
        return Outcome(
            CHECK,
            operation,
            Result.MATCHED,
            "matched — " + (", ".join(changed) or "no paths reported"),
        )
    detail = (completed.stderr or completed.stdout).strip().splitlines()[-1:] or [
        f"exit {completed.returncode}"
    ]
    return Outcome(CHECK, operation, Result.UNMATCHED, f"mismatch — {detail[0]}")
