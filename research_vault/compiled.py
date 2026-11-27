"""The compiled-page record and the `seal` verb (spec §5.4, #212).

`system/compiled-pages.json` holds the sha256 of every file under `wiki/`.
The custody rule: an entry may change only when the file's current bytes
equal the entry, or equal the *latest* complete compile-journal write for
that exact path — so a File-recovery restore of an older compile is never
re-sealed. Two changes no journal wrote are accepted too, each a definite
test against the sealed bytes: a change only of link destinations that
follow a rename (decision 13: the old target no longer resolves, the new
one resolves to one file), and a change only of the citation-key rewrites
an applied propagation record this change adds names (R35, C8b). The sealed
bytes are looked up by hash: seal keeps a copy under `.vault-meta/`, and
otherwise the base revision and the path's recent history hold them (C7).
Seal normalises a page's links (spec §5.2) and records the hash of the
normalised bytes. The `compiled-layer` check compares every file with its
entry and reports every symlink under `wiki/`; on the worktree it also
accepts the latest complete journal write, so a fresh compile files no row
before seal; the commit hook's index, CI, and the per-commit re-check read
only the record (C6).
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from . import captured, frontmatter, gitstate, links, structure
from .outcome import Outcome, Result
from .pathcodec import RepoPath

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

RECORD_PATH = "system/compiled-pages.json"
SCHEMA = "research-vault.compiled-pages.v1"
CHECK = "compiled-layer"
# Where the compile tool keeps one directory per transaction, each holding a
# `journal.json` (claude-obsidian 2.2.0, `checkpoint.py` and
# `transaction.py::_journal_for`, read 2026-11-27).
_JOURNALS = ".vault-meta/transactions"

__all__ = [
    "CHECK",
    "RECORD_PATH",
    "SCHEMA",
    "Outcome",
    "RecordError",
    "journal_hashes",
    "lint_compiled_layer",
    "load_record",
    "only_link_targets_changed",
    "seal",
    "snapshot_base",
    "snapshot_rows",
    "wiki_files",
    "write_record",
]


class RecordError(ValueError):
    """The record exists but is not this module's document."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _text(data: bytes) -> str:
    return data.decode("utf-8", errors="surrogateescape")


def load_record(vault_root) -> dict[str, str]:
    path = Path(vault_root) / RECORD_PATH
    if not path.is_file():
        return {}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise RecordError(f"compiled-page record unreadable: {error}") from error
    pages = document.get("pages") if isinstance(document, dict) else None
    if (
        not isinstance(document, dict)
        or document.get("schema") != SCHEMA
        or not isinstance(pages, dict)
        or not all(
            isinstance(k, str) and structure._is_plain_text(k) and isinstance(v, str)
            for k, v in pages.items()
        )
    ):
        raise RecordError(f"compiled-page record unreadable: not a {SCHEMA} document")
    return dict(pages)


def write_record(vault_root, pages: Mapping[str, str]) -> Path:
    path = Path(vault_root) / RECORD_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {"schema": SCHEMA, "pages": dict(sorted(pages.items()))}
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path


def _walk(vault: Path) -> tuple[dict[str, bytes], dict[str, str]]:
    """Every non-excluded regular file under `wiki/` with its bytes, and every
    other node there (a symlink, to a file or a directory, or a special
    file) with what it is. Symlinks are never followed."""
    files: dict[str, bytes] = {}
    others: dict[str, str] = {}
    wiki = vault / "wiki"
    if not wiki.is_dir():
        return files, others
    for root, dirnames, filenames in os.walk(wiki, followlinks=False):
        here = Path(root)
        kept = []
        for name in sorted(dirnames):
            path = here / name
            if structure.is_excluded(path, vault):
                continue
            if path.is_symlink():
                others[path.relative_to(vault).as_posix()] = "symlink"
            else:
                kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames):
            path = here / name
            if structure.is_excluded(path, vault):
                continue
            relative = path.relative_to(vault).as_posix()
            if path.is_symlink():
                others[relative] = "symlink"
            elif path.is_file():
                files[relative] = path.read_bytes()
            else:
                others[relative] = "special"
    return dict(sorted(files.items())), others


def wiki_files(vault_root) -> dict[str, bytes]:
    return _walk(Path(vault_root))[0]


def _not_a_file(relative: str, kind: str) -> Outcome:
    what = "a symlink" if kind == "symlink" else "not a regular file"
    return _row(
        Result.UNMATCHED,
        relative,
        f"drift — {_shown(relative)} is {what}; a compiled page is a file",
    )


def snapshot_rows(snapshot) -> list[Outcome]:
    """The symlinks and special files under `wiki/` in a git snapshot. The
    materialised tree verify lints in holds no such node
    (`gitstate.materialize_snapshot`), so verify adds these beside the lint."""
    rows = []
    for raw_path, image in sorted(snapshot.images.items()):
        if not raw_path.startswith(b"wiki/") or image.kind not in {
            "symlink",
            "special",
        }:
            continue
        relative = os.fsdecode(raw_path)
        anchor = Path("/vault")
        if structure.is_excluded(anchor / relative, anchor):
            continue
        rows.append(_not_a_file(relative, image.kind))
    return rows


def journal_hashes(repository_root) -> dict[str, str | None]:
    """Path → `new_sha256` of its latest complete compile-tool write (None: a delete).

    Journals the tool left in `prepared`, `applying` or `rolled-back` state are
    not writes that happened; a missing journal directory means no compile ran
    here (a CI checkout, a fresh clone)."""
    folder = Path(repository_root) / _JOURNALS
    if not folder.is_dir():
        return {}
    latest: dict[str, tuple[float, str | None]] = {}
    for journal_path in sorted(folder.glob("*/journal.json")):
        try:
            journal = json.loads(journal_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            continue
        if not isinstance(journal, dict) or journal.get("state") != "complete":
            continue
        epoch = journal.get("created_epoch")
        stamp = float(epoch) if isinstance(epoch, (int, float)) else 0.0
        writes = journal.get("writes", [])
        for write in writes if isinstance(writes, list) else []:
            if not isinstance(write, dict) or not isinstance(write.get("path"), str):
                continue
            new = write.get("new_sha256")
            if new is not None and not isinstance(new, str):
                continue
            if write["path"] not in latest or stamp >= latest[write["path"]][0]:
                latest[write["path"]] = (stamp, new)
    return {path: new for path, (_stamp, new) in latest.items()}


def only_link_targets_changed(
    old: str, new: str, index: links.Index, source: str
) -> bool:
    """Decision 13's definite test: the two texts differ only in link
    destinations, and each changed one follows a rename (C8a): its old
    target no longer resolves in the current index and its new one resolves
    to exactly one file. A retarget between two pages that both exist is an
    edit, not a rename."""
    old_links, new_links = links.find_links(old), links.find_links(new)
    if len(old_links) != len(new_links) or not old_links:
        return False
    cursor_old = cursor_new = 0
    for a, b in zip(old_links, new_links, strict=True):
        if old[cursor_old : a.start] != new[cursor_new : b.start]:
            return False
        if (a.kind, a.embed, a.alias, a.subpath) != (
            b.kind,
            b.embed,
            b.alias,
            b.subpath,
        ):
            return False
        if a.target != b.target and (
            index.resolve(a.target, source=source)
            or len(index.resolve(b.target, source=source)) != 1
        ):
            return False
        cursor_old, cursor_new = a.end, b.end
    return old[cursor_old:] == new[cursor_new:]


def propagated_by(
    old: str, new: str, vault: Path, source: str, base: Base
) -> str | None:
    """R35's definite test: the operation id of an applied propagation record
    whose rewrites, replayed over `old` exactly as `propagate.apply` made
    them, give `new`; None when no record does. Only a record this change
    adds counts (C8b): one ``base`` does not hold, so an old record (a key a
    later item took) or one committed long ago never vouches for a hand edit.
    One record at a time: `propagate.apply` reseals after each."""
    # Imported here: propagate imports capture, which imports this module.
    from . import propagate

    if old == new:
        return None
    folder = vault / propagate.RECORD_DIR
    if not folder.is_dir():
        return None
    for path in sorted(folder.glob("*.json")):
        if structure.is_excluded(path, vault):
            continue
        relative = path.relative_to(vault).as_posix()
        if base.holds(relative):
            continue
        try:
            record = propagate.read_plan(path)
        except (OSError, ValueError, KeyError, TypeError):
            continue  # lint_propagation reports the unreadable record
        text = old
        for before, after in propagate.rewrites(record):
            text = propagate.rewrite_text(text, before, after, source=source)
        if text == new:
            return record.operation_id
    return None


# Where seal keeps a content-addressed copy of each page it sealed (C7):
# untracked and local, under the compile tool's own ignored `.vault-meta/`
# (the seeded `.gitignore` ignores it).
SEALED_STORE = ".vault-meta/research-vault/sealed"
# How many commits touching a path the history search reads for the sealed
# bytes when neither the store nor the base holds them (C7).
HISTORY_BOUND = 50


def _history_blob(repository: Path, relative: str, sha: str) -> bytes | None:
    """The bytes hashing to ``sha`` among the blobs the last `HISTORY_BOUND`
    commits touching ``relative`` wrote or replaced; None when none does."""
    if not (repository / ".git").exists():
        return None
    log = gitstate._git(
        repository,
        "log",
        f"-n{HISTORY_BOUND}",
        "--format=",
        "--raw",
        "--no-abbrev",
        "--no-renames",
        "HEAD",
        "--",
        os.fsencode(relative),
        check=False,
    )
    if log.returncode:
        return None
    oids: list[bytes] = []
    for line in log.stdout.splitlines():
        if not line.startswith(b":"):
            continue
        fields = line.split(b"\t", 1)[0].split()
        for oid in fields[2:4]:
            if oid.strip(b"0") and oid not in oids:
                oids.append(oid)
    if not oids:
        return None
    batch = gitstate._git(
        repository, "cat-file", "--batch", stdin=b"\n".join(oids) + b"\n", check=False
    )
    data = batch.stdout
    while data:
        header, _, data = data.partition(b"\n")
        parts = header.split()
        if len(parts) != 3 or parts[1] != b"blob":
            break  # `missing`, or not a blob: nothing more to read reliably
        size = int(parts[2])
        blob, data = data[:size], data[size + 1 :]
        if _sha(blob) == sha:
            return blob
    return None


class Base:
    """Where the sealed bytes and the change's base are read: the revision a
    change is judged against. Sealed bytes are looked up by their hash, never
    by one revision alone (C7)."""

    def __init__(self, repository: Path) -> None:
        self._repository = repository
        self._holds: dict[str, bool] = {}

    def sealed(self, relative: str, sha: str) -> bytes | None:
        raise NotImplementedError

    def _holds_uncached(self, relative: str) -> bool:
        raise NotImplementedError

    def holds(self, relative: str) -> bool:
        """Whether the base revision has ``relative`` at all."""
        if relative not in self._holds:
            self._holds[relative] = self._holds_uncached(relative)
        return self._holds[relative]


class _Local(Base):
    """The local judge: the seal store, then HEAD, then the path's history;
    the change's base is HEAD."""

    def sealed(self, relative: str, sha: str) -> bytes | None:
        stored = self._repository / SEALED_STORE / sha
        try:
            data = stored.read_bytes()
        except OSError:
            data = None
        if data is not None and _sha(data) == sha:
            return data
        if (self._repository / ".git").exists():
            head = gitstate.blob_bytes(self._repository, "HEAD", os.fsencode(relative))
            if head is not None and _sha(head) == sha:
                return head
        return _history_blob(self._repository, relative, sha)

    def _holds_uncached(self, relative: str) -> bool:
        if not (self._repository / ".git").exists():
            return False
        result = gitstate._git(
            self._repository,
            "cat-file",
            "-e",
            b"HEAD:" + os.fsencode(relative),
            check=False,
        )
        return result.returncode == 0


class _Snapshot(Base):
    """The re-check's judge (C2): the pair's base snapshot, then the path's
    history; no local store, as in CI."""

    def __init__(self, snapshot, repository: Path) -> None:
        super().__init__(repository)
        self._snapshot = snapshot

    def sealed(self, relative: str, sha: str) -> bytes | None:
        image = self._snapshot.image(os.fsencode(relative))
        if image is not None and image.kind == "file" and _sha(image.data) == sha:
            return image.data
        return _history_blob(self._repository, relative, sha)

    def _holds_uncached(self, relative: str) -> bool:
        return self._snapshot.image(os.fsencode(relative)) is not None


def snapshot_base(snapshot, repository) -> Base:
    """The per-commit re-check's `base` for `lint_compiled_layer`."""
    return _Snapshot(snapshot, Path(repository))


def _store(repository: Path, data: bytes) -> None:
    """Keep the sealed bytes by hash (C7), so a rename or a propagation before
    the next commit is still judged against them."""
    folder = repository / SEALED_STORE
    target = folder / _sha(data)
    if target.is_file():
        return
    folder.mkdir(parents=True, exist_ok=True)
    temporary = folder / f".{target.name}.{os.getpid()}"
    temporary.write_bytes(data)
    temporary.replace(target)


def _shown(relative: str) -> str:
    """`relative` as a reason may carry it: a name that is not plain UTF-8
    text would crash the queue's strict write, and the target names it."""
    return relative if structure._is_plain_text(relative) else "this file"


def _row(result: Result, relative: str, reason: str) -> Outcome:
    return Outcome(CHECK, RepoPath(os.fsencode(relative)), result, reason)


def _unsealed(relative: str) -> Outcome:
    return _row(
        Result.UNMATCHED,
        relative,
        f"drift — {_shown(relative)} is not sealed: no complete compile wrote "
        "these bytes",
    )


class _Witness:
    """The two definite tests over one vault, its link index built once."""

    def __init__(self, vault: Path, base: Base) -> None:
        self._vault = vault
        self._base = base
        self._index: links.Index | None = None

    def index(self) -> links.Index:
        if self._index is None:
            self._index = captured.link_index(self._vault)
        return self._index

    def reseal_note(self, relative: str, recorded: str, data: bytes) -> str | None:
        """The MATCHED note for a page whose change from its sealed bytes is a
        rename's link change or a named key rewrite; None otherwise."""
        if not relative.endswith(".md"):
            return None
        sealed = self._base.sealed(relative, recorded)
        if sealed is None:
            return None
        old, new = _text(sealed), _text(data)
        if only_link_targets_changed(old, new, self.index(), relative):
            return "matched — link targets follow a rename; reseal"
        operation = propagated_by(old, new, self._vault, relative, self._base)
        if operation is not None:
            return f"matched — citation keys follow propagation {operation}; reseal"
        return None


def lint_compiled_layer(
    vault_root,
    *,
    repository_root=None,
    base: Base | None = None,
    journal: bool = True,
) -> list[Outcome]:
    """Every file under `wiki/` against the record, and every symlink or
    special file there as a row.

    ``base`` is the per-commit re-check's mode (ruling C2, `snapshot_base`):
    the change is judged against the pair's base, and no journal is read, as
    in CI. Without it, the judge is local (the seal store, HEAD, the path's
    history). ``journal`` accepts the latest complete journal write of a path
    as MATCHED: only on the worktree candidate (C6), since a page committed
    unsealed would hold every later replay; the hook's index and CI's HEAD
    pass ``journal=False``."""
    vault = Path(vault_root)
    if not (vault / "wiki").is_dir():
        return [
            Outcome(CHECK, "wiki", Result.SKIPPED, "no-identifier — no compiled layer")
        ]
    files, others = _walk(vault)
    try:
        record = load_record(vault)
    except RecordError as error:
        return [_row(Result.UNMATCHED, RECORD_PATH, f"schema-violation — {error}")]
    repository = Path(repository_root) if repository_root is not None else vault
    journal_writes = journal_hashes(repository) if base is None and journal else {}
    witness = _Witness(vault, base if base is not None else _Local(repository))
    rows: list[Outcome] = [_not_a_file(path, kind) for path, kind in others.items()]
    for relative, data in files.items():
        current = _sha(data)
        recorded = record.get(relative)
        if recorded == current or journal_writes.get(relative) == current:
            continue
        if recorded is None:
            rows.append(_unsealed(relative))
            continue
        note = witness.reseal_note(relative, recorded, data)
        if note is not None:
            rows.append(_row(Result.MATCHED, relative, note))
            continue
        rows.append(
            _row(
                Result.UNMATCHED,
                relative,
                f"drift — {relative} differs from the compiled-page record; "
                "seal or acknowledge",
            )
        )
    for relative in sorted(set(record) - set(files) - set(others)):
        if journal_writes.get(relative, "") is None:
            continue  # the tool deleted it; seal drops the entry
        rows.append(
            _row(
                Result.UNMATCHED, relative, f"drift — {relative} is recorded but absent"
            )
        )
    return rows or [Outcome(CHECK, RECORD_PATH, Result.MATCHED, "matched")]


def seal(
    vault_root, paths: Iterable[str] | None = None, *, repository_root=None
) -> list[Outcome]:
    """Move entries from the latest complete journal into the record, normalising
    a page's links first; accept a rename's link change and a named key
    rewrite; drop the entry of a page the tool deleted; refuse bytes no
    complete compile wrote. Returns one MATCHED summary or the refusals."""
    vault = Path(vault_root)
    try:
        record = load_record(vault)
    except RecordError as error:
        return [_row(Result.UNMATCHED, RECORD_PATH, f"schema-violation — {error}")]
    repository = Path(repository_root) if repository_root is not None else vault
    journal = journal_hashes(repository)
    files, others = _walk(vault)
    wanted = (
        set(files) | set(record) | set(others)
        if paths is None
        else {p.strip("/") for p in paths}
    )
    witness = _Witness(vault, _Local(repository))
    refusals: list[Outcome] = []
    sealed = 0
    for relative in sorted(wanted):
        if relative in others:
            refusals.append(_not_a_file(relative, others[relative]))
            continue
        if relative not in files:
            if relative in record and journal.get(relative, "") is None:
                del record[relative]
                sealed += 1
            elif relative in record:
                refusals.append(
                    _row(
                        Result.UNMATCHED,
                        relative,
                        f"drift — {relative} is recorded but absent",
                    )
                )
            continue
        if not structure._is_plain_text(relative):
            # The record is UTF-8 JSON: a name that is not UTF-8 text has no
            # entry to hold it. Renaming the file is the remedy.
            refusals.append(_unsealed(relative))
            continue
        current = _sha(files[relative])
        if record.get(relative) == current:
            if relative.endswith(".md"):
                _store(repository, files[relative])  # an entry sealed before C7
            continue
        accepted = journal.get(relative) == current or (
            relative in record
            and witness.reseal_note(relative, record[relative], files[relative])
            is not None
        )
        if not accepted:
            refusals.append(_unsealed(relative))
            continue
        if relative.endswith(".md"):
            text = _text(files[relative])
            try:
                # §5.6: the OKF reader runs at seal too, so a compile-tool page
                # with an unquoted `title: A: B` fails inside the session that
                # can redo it, not weeks later at commit.
                frontmatter.read_okf(text)
            except frontmatter.FrontmatterError as error:
                refusals.append(
                    _row(
                        Result.UNMATCHED,
                        relative,
                        f"schema-violation — {relative}: frontmatter is not valid "
                        f"YAML ({' '.join(str(error).split())})",
                    )
                )
                continue
            normalised, _problems = links.normalize(
                text, witness.index(), source=relative
            )
            if normalised != text:
                (vault / relative).write_text(
                    normalised, encoding="utf-8", errors="surrogateescape", newline=""
                )
                files[relative] = normalised.encode("utf-8", errors="surrogateescape")
                current = _sha(files[relative])
        if relative.endswith(".md"):
            _store(repository, files[relative])
        record[relative] = current
        sealed += 1
    if sealed:
        write_record(vault, record)
    return refusals or [
        Outcome(CHECK, RECORD_PATH, Result.MATCHED, f"matched — sealed {sealed}")
    ]
