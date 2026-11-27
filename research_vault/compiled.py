"""The compiled-page record and the `seal` verb (spec §5.4, #212).

`system/compiled-pages.json` holds the sha256 of every file under `wiki/`.
The custody rule: an entry may change only when the file's current bytes
equal the entry, or equal the *latest* complete compile-journal write for
that exact path — so a File-recovery restore of an older compile is never
re-sealed. Two changes no journal wrote are accepted too, each a definite
test against the sealed bytes: a change only of link destinations that now
resolve (decision 13, a rename), and a change only of the citation-key
rewrites an applied propagation record under `system/propagations/` names
(R35, the record `propagate.apply` writes). Seal normalises a page's links
(spec §5.2) and records the hash of the normalised bytes. The
`compiled-layer` check compares every file with its entry; locally it also
accepts the latest complete journal write, so a fresh compile files no row
before seal; CI, with no `.vault-meta/`, reads only the record, and so does
the per-commit re-check, which reads the sealed bytes from each commit's
parent.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path

from . import captured, frontmatter, gitstate, links, structure
from .outcome import Outcome, Result
from .pathcodec import RepoPath

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
    "wiki_files",
    "write_record",
]

# A reader of the sealed bytes of one path, or None when none are known.
RecordedBytes = Callable[[str], bytes | None]


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


def wiki_files(vault_root) -> dict[str, bytes]:
    vault = Path(vault_root)
    wiki = vault / "wiki"
    if not wiki.is_dir():
        return {}
    files: dict[str, bytes] = {}
    for path in sorted(wiki.rglob("*")):
        if (
            path.is_file()
            and not path.is_symlink()
            and not structure.is_excluded(path, vault)
        ):
            files[path.relative_to(vault).as_posix()] = path.read_bytes()
    return files


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
    destinations, and every destination in `new` resolves to one file."""
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
        if a.target != b.target and len(index.resolve(b.target, source=source)) != 1:
            return False
        cursor_old, cursor_new = a.end, b.end
    return old[cursor_old:] == new[cursor_new:]


def propagated_by(old: str, new: str, vault: Path, source: str) -> str | None:
    """R35's definite test: the operation id of the applied propagation
    record whose rewrites, replayed over `old` exactly as `propagate.apply`
    made them, give `new`; None when no record does. One record at a time:
    `propagate.apply` reseals after each."""
    # Imported here: propagate imports capture, which imports this module.
    from . import propagate

    if old == new:
        return None
    try:
        records = propagate.read_records(vault)
    except (OSError, ValueError, KeyError, TypeError):
        return None  # lint_propagation reports the unreadable record
    for record in records:
        text = old
        for before, after in propagate.rewrites(record):
            text = propagate.rewrite_text(text, before, after, source=source)
        if text == new:
            return record.operation_id
    return None


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


def _head_bytes(repository: Path) -> RecordedBytes:
    def read(relative: str) -> bytes | None:
        if not repository.is_dir():
            return None
        return gitstate.blob_bytes(repository, "HEAD", os.fsencode(relative))

    return read


def _recorded_text(
    recorded_bytes: RecordedBytes, relative: str, recorded: str
) -> str | None:
    """The bytes the record describes, or None when the reader's revision does
    not hold them. Locally that revision is HEAD (the record and the page are
    committed together); in the re-check it is the pair's base."""
    data = recorded_bytes(relative)
    if data is not None and _sha(data) == recorded:
        return _text(data)
    return None


class _Witness:
    """The two definite tests over one vault, its link index built once."""

    def __init__(self, vault: Path, recorded_bytes: RecordedBytes) -> None:
        self._vault = vault
        self._recorded_bytes = recorded_bytes
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
        old = _recorded_text(self._recorded_bytes, relative, recorded)
        if old is None:
            return None
        new = _text(data)
        if only_link_targets_changed(old, new, self.index(), relative):
            return "matched — link targets follow a rename; reseal"
        operation = propagated_by(old, new, self._vault, relative)
        if operation is not None:
            return f"matched — citation keys follow propagation {operation}; reseal"
        return None


def lint_compiled_layer(
    vault_root, *, repository_root=None, base: RecordedBytes | None = None
) -> list[Outcome]:
    """Every file under `wiki/` against the record.

    ``base`` is the per-commit re-check's mode (ruling C2): it reads the
    sealed bytes from the pair's base revision, and no journal is read, as in
    CI. Without it, the sealed bytes come from the repository's HEAD and the
    latest complete journal write of a path is MATCHED."""
    vault = Path(vault_root)
    if not (vault / "wiki").is_dir():
        return [
            Outcome(CHECK, "wiki", Result.SKIPPED, "no-identifier — no compiled layer")
        ]
    files = wiki_files(vault)
    try:
        record = load_record(vault)
    except RecordError as error:
        return [_row(Result.UNMATCHED, RECORD_PATH, f"schema-violation — {error}")]
    repository = Path(repository_root) if repository_root is not None else vault
    journal = journal_hashes(repository) if base is None else {}
    witness = _Witness(vault, base if base is not None else _head_bytes(repository))
    rows: list[Outcome] = []
    for relative, data in files.items():
        current = _sha(data)
        recorded = record.get(relative)
        if recorded == current or journal.get(relative) == current:
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
    for relative in sorted(set(record) - set(files)):
        if journal.get(relative, "") is None:
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
    files = wiki_files(vault)
    wanted = (
        set(files) | set(record) if paths is None else {p.strip("/") for p in paths}
    )
    witness = _Witness(vault, _head_bytes(repository))
    refusals: list[Outcome] = []
    sealed = 0
    for relative in sorted(wanted):
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
        record[relative] = current
        sealed += 1
    if sealed:
        write_record(vault, record)
    return refusals or [
        Outcome(CHECK, RECORD_PATH, Result.MATCHED, f"matched — sealed {sealed}")
    ]
