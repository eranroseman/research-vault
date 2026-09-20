"""OKF §11 structure checks over vault files (audit §1).

The vault rule: a note's ``type`` is determined by its folder. ``system/``
and root-level concepts carry any non-empty type. ``inbox/`` captures other
than the review queue are the recorded fleeting exemption — never checked
here; the stamp converges them at chokepoints.

``projects/`` is narrower than the other folders: ``publish.project_note()``
requires exactly one ``type: "project"`` note per project directory, found
by scanning ``projects/<name>/**/*.md`` for that type field — not by
filename. The codebase's actual convention for that one file is
``projects/<name>/draft.md`` (every test fixture across the suite builds
it there). So only that exact shape derives ``"project"``; every other
``.md`` under ``projects/`` — including a flat ``projects/<name>.md`` with
no subdirectory, and any other file alongside ``draft.md`` in the same
project directory — derives no type (``None``), so it is free to carry
any non-empty ``type`` (an appendix, a supplementary note, ...).
"""

import os
import re
from pathlib import Path

from . import frontmatter
from .outcome import Outcome, Result
from .pathcodec import RepoPath

_FOLDER_TYPES = {
    "literature": "literature",
    "log": "daily",
    "inbox": "fleeting",
}
# The compile tool's own stores (ingest spec §4.3): `.raw/` would hold a
# duplicate of `fulltext/` if its capture were ever run, and `.vault-meta/` is
# its runtime state. Both are gitignored and never walked.
EXCLUDED_DIRS = frozenset({".git", ".raw", ".vault-meta"})
# ADR 0001, second exemption: the adopted compile tool writes
# `wiki/index.md` with frontmatter at a hard-coded path; OKF §8 forbids it on
# a nested index and the tool's own lint requires it. The vault carries the
# deviation; nothing the vault authors deviates.
_EXEMPT_INDEXES = frozenset({"wiki/index.md"})

_PROJECT_NOTE_NAME = "draft.md"


def is_excluded(path: Path, vault: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.relative_to(vault).parts)


def is_fleeting(relative: str) -> bool:
    return relative.startswith("inbox/") and relative != "inbox/review-queue.md"


def expected_type(relative: str) -> str | None:
    if relative == "inbox/review-queue.md":
        return "review-queue"
    if is_fleeting(relative):
        return None
    parts = relative.split("/")
    if parts[0] == "projects":
        if len(parts) == 3 and parts[2] == _PROJECT_NOTE_NAME:
            return "project"
        return None
    top = parts[0]
    if "/" in relative and top in _FOLDER_TYPES:
        return _FOLDER_TYPES[top]
    return None


def _repo_path(relative: str) -> RepoPath:
    return RepoPath(os.fsencode(relative))


def check_note_frontmatter(vault_root, path) -> list[Outcome]:
    """Rules 1 and 2 plus the folder-type vault rule, for one non-reserved file."""
    vault = Path(vault_root)
    relative = Path(path).relative_to(vault).as_posix()
    if is_fleeting(relative):
        return []
    try:
        data, _body = frontmatter.parse(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, frontmatter.FrontmatterError) as error:
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                f"schema-violation — frontmatter unparseable ({error})",
            )
        ]
    okf_type = data.get("type")
    if not isinstance(okf_type, str) or not okf_type.strip():
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                "schema-violation — missing type (OKF §11 rule 2)",
            )
        ]
    derived = expected_type(relative)
    if derived is not None and okf_type != derived:
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                f"schema-violation — type {okf_type!r} but folder derives {derived!r}",
            )
        ]
    return [Outcome("okf-frontmatter", _repo_path(relative), Result.MATCHED, "matched")]


_DATE_HEADING = re.compile(r"## (\d{4}-\d{2}-\d{2})\s*$")


def _log_shape_problems(text: str) -> list[str]:
    """§9 log shape: only ``## YYYY-MM-DD`` second-level headings, newest first."""
    try:
        _data, body = frontmatter.parse(text)
    except frontmatter.FrontmatterError:
        # frontmatter on log.md is legal but optional (§8 names index.md only)
        body = text
    dates = []
    for line in body.splitlines():
        if line.startswith("## "):
            match = _DATE_HEADING.match(line)
            if not match:
                return [f"non-date second-level heading {line!r}"]
            dates.append(match.group(1))
    if dates != sorted(dates, reverse=True):
        return ["day headings not newest first"]
    return []


def check_reserved(vault_root) -> list[Outcome]:
    """§11 rule 3: index.md per §8/§12, log.md per §9, at any depth."""
    vault = Path(vault_root)
    problems: list[tuple[str, str]] = []
    for path in sorted(vault.rglob("*.md")):
        if is_excluded(path, vault):
            continue
        relative = path.relative_to(vault).as_posix()
        if path.name == "index.md":
            try:
                data, _body = frontmatter.parse(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, frontmatter.FrontmatterError) as error:
                problems.append((relative, f"unreadable ({error})"))
                continue
            if relative == "index.md":
                extra = sorted(set(data) - {"okf_version"})
                if extra:
                    problems.append(
                        (
                            relative,
                            f"root index carries keys beyond okf_version: {extra}",
                        )
                    )
                if not str(data.get("okf_version", "")).strip():
                    problems.append((relative, "missing okf_version"))
            elif relative in _EXEMPT_INDEXES:
                continue
            elif data:
                problems.append((relative, "nested index.md must be frontmatter-free"))
        elif path.name == "log.md":
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                problems.append((relative, f"unreadable ({error})"))
                continue
            problems.extend((relative, p) for p in _log_shape_problems(text))
    if problems:
        return [
            Outcome(
                "okf-structure",
                _repo_path(relative),
                Result.UNMATCHED,
                f"schema-violation — {detail}",
            )
            for relative, detail in problems
        ]
    return [Outcome("okf-structure", "reserved-files", Result.MATCHED, "matched")]


def check_tree(vault_root) -> list[Outcome]:
    """Vault-wide directory scaffolding attestation (verify-side; see doctor.doctor).

    Doctor keeps a separate `tree` probe for repair-at-setup; this is a
    different job — verify-side attestation only, no repair. The existing
    tree row, plus one row per directory nested under `literature/`: every
    reader of the evidence layer globs it flat (decision 08), so a note in a
    nested directory is a literature note nowhere — reported here rather than
    typed by folder and forgotten.
    """
    from . import scaffold

    vault = Path(vault_root)
    missing = [d for d in scaffold.VAULT_DIRS if not (vault / d).is_dir()]
    rows = [
        Outcome(
            "tree", "vault", Result.UNMATCHED, f"schema-violation — missing {missing}"
        )
        if missing
        else Outcome("tree", "vault", Result.MATCHED, "matched")
    ]
    literature = vault / "literature"
    if literature.is_dir():
        for child in sorted(literature.iterdir()):
            if child.is_dir():
                relative = f"literature/{child.name}/"
                rows.append(
                    Outcome(
                        "tree",
                        relative,
                        Result.UNMATCHED,
                        f"schema-violation — literature/ is flat: {relative}",
                    )
                )
    return rows
