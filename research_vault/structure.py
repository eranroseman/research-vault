"""OKF §11 structure checks over vault files (audit §1, ruled 2026-09-02).

The vault rule: a note's ``type`` is determined by its folder. ``system/``
and root-level concepts carry any non-empty type. ``inbox/`` captures other
than the review queue are the recorded fleeting exemption — never checked
here; the stamp converges them at chokepoints.
"""

import os
from pathlib import Path

from . import frontmatter
from .outcome import Outcome, Result
from .pathcodec import RepoPath

_FOLDER_TYPES = {
    "literatures": "literature",
    "synthesis": "synthesis",
    "projects": "project",
    "log": "daily",
    "inbox": "fleeting",
}


def is_fleeting(relative: str) -> bool:
    return relative.startswith("inbox/") and relative != "inbox/review-queue.md"


def expected_type(relative: str) -> str | None:
    if relative == "inbox/review-queue.md":
        return "review-queue"
    if is_fleeting(relative):
        return None
    top = relative.split("/", 1)[0]
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
        data, _body = frontmatter.parse(Path(path).read_text())
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
    return [
        Outcome(
            "okf-frontmatter", _repo_path(relative), Result.MATCHED, "matched"
        )
    ]
