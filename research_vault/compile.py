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
from pathlib import Path, PurePosixPath

from . import clock, frontmatter, notes, paths
from .outcome import Outcome, Result

LEDGER_PATH = notes.LEDGER_PATH
LEDGER_SCHEMA = "claude-obsidian.source-ledger.v1"
BUNDLE_SCHEMA = "claude-obsidian.transaction.v1"
PLUGIN_ID = "claude-obsidian@agricidaniel-claude-obsidian"
CHECK = "compile"
BUNDLE_DIR = ".research-vault/compile"
# The one spelling of a file-kind origin: the record's own origin.kind and
# the stable_source_id() call that hashes it must always agree, or the id
# would no longer match what the record itself declares.
FILE_KIND = "file"


class ToolMissingError(RuntimeError):
    """The compile tool is not installed and machine.json names no root."""


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


def _selected_notes(vault: Path, keys):
    wanted = set(keys)
    for path in sorted((vault / "literatures").glob("*.md")):
        # bytes.decode()'s default codec already is utf-8, so this carries no
        # literal codec name a mutation gate could flip with no effect.
        text = path.read_bytes().decode()
        provenance = notes.read_provenance(text)
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


def _run(root: Path, vault: Path, *args) -> subprocess.CompletedProcess:
    # ruff PLW1510 requires `check=` spelled out explicitly; `False` is
    # subprocess.run's own default, so a `check=False` -> `check=None`
    # mutant is behaviorally equivalent (both are falsy to the `if check`
    # test inside subprocess.run). Baselined (R21): mutation-baseline.txt
    # already carries the identical shape for gitstate.py's own `_git`.
    return subprocess.run(
        [
            "python3",
            str(root / "scripts" / "claude-obsidian.py"),
            *args,
            "--vault",
            str(vault),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def plan(vault_root, keys, *, today=None) -> tuple[Path, dict]:
    vault = Path(vault_root)
    root = tool_root(vault)
    if root is None:
        raise ToolMissingError("claude-obsidian is not installed")
    today = clock.today(today)
    ledger = vault / LEDGER_PATH
    if ledger.is_file():
        raw = ledger.read_bytes()
        current = json.loads(raw)
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
        # An id already registered keeps its record: its review_status and
        # pages[] are the tool's (spec §4.5), and a changed text has a new id.
        sources.setdefault(source_id, record)
    merged = {
        **current,
        "schema": LEDGER_SCHEMA,
        "generated_at": f"{today}T00:00:00Z",
        "sources": sources,
    }
    content = json.dumps(merged, indent=2, sort_keys=True) + "\n"
    operation_id = "research-vault-compile-" + datetime.datetime.now(
        datetime.UTC
    ).strftime("%Y%m%dT%H%M%SZ")
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
    bundle_dir = vault / BUNDLE_DIR
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = bundle_dir / f"{operation_id}.json"
    # write_bytes + str.encode()'s default utf-8: no literal codec name here
    # either, same reasoning as _selected_notes' read.
    bundle_path.write_bytes((json.dumps(bundle, indent=2) + "\n").encode())
    completed = _run(root, vault, "transaction", "inspect", str(bundle_path))
    try:
        inspected = json.loads(completed.stdout) if completed.stdout else {}
    except ValueError:
        inspected = {}
    inspected.setdefault("exit", completed.returncode)
    inspected.setdefault("stderr", completed.stderr.strip())
    return bundle_path, inspected


def apply(vault_root, bundle_path, approved_sha256) -> Outcome:
    vault = Path(vault_root)
    root = tool_root(vault)
    operation = Path(bundle_path).stem
    if root is None:
        return Outcome(
            CHECK,
            operation,
            Result.UNREACHABLE,
            "outage — claude-obsidian is not installed",
        )
    completed = _run(
        root,
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
