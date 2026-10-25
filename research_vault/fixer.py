"""The one fixer behind ``stamp-type`` (spec §5.1): type stamp, link normalisation, root ``log.md``.

Writers call it on the paths they wrote; the commit hook calls it with
``--staged`` on the fully staged files and refuses the commit when it changed
any (#203). It never stages. Under ``--staged`` it is given only the files
whose worktree copy equals the staged blob; root ``log.md`` it regenerates
whatever its staging state.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from . import captured, links, okf, stamp, structure

if TYPE_CHECKING:
    from collections.abc import Iterable

# Reasons stamp reports under which the normaliser leaves the file alone: the
# file was not read or not written, or (`unparseable`) its frontmatter is
# broken, which stamp has already reported — one fault, one line.
_LEFT_ALONE = frozenset(
    {"symlink", "outside", "outage", "not-utf-8", "unwritable", "unparseable"}
)


@dataclass
class FixReport:
    stamped: list[str] = field(default_factory=list)
    normalised: list[str] = field(default_factory=list)
    log_regenerated: bool = False
    reported: list[tuple[str, str]] = field(default_factory=list)
    problems: list[tuple[str, links.Problem]] = field(default_factory=list)

    @property
    def changed(self) -> list[str]:
        """Every path the fixer rewrote, once each, in order: a file both stamped
        and normalised is one entry."""
        paths = [
            *self.stamped,
            *self.normalised,
            *(["log.md"] if self.log_regenerated else []),
        ]
        return list(dict.fromkeys(paths))


def _is_note(vault: Path, listed: str) -> bool:
    """A listed path is fixed only if it ends in ``.md`` and no walker excludes
    it: a canvas, a ``.gitkeep`` or a plugin's README under ``.obsidian/`` is
    not a note. A path outside the vault is kept, so stamp reports it."""
    if not listed.endswith(".md"):
        return False
    # Lexical, never resolved: symlinks are stamp's to judge and report.
    root = Path(os.path.normpath(vault.absolute()))
    path = Path(os.path.normpath(root / listed))
    try:
        path.relative_to(root)
    except ValueError:
        return True
    return not structure.is_excluded(path, root)


def _normalise(vault: Path, paths, report: FixReport) -> None:
    index: links.Index | None = None
    root = vault.resolve()
    skipped = {
        relative for relative, reason in report.reported if reason in _LEFT_ALONE
    }
    for path in stamp._candidate_paths(vault, paths):
        relative = stamp._reported_name(path, vault)
        if (
            relative in skipped
            or path.is_symlink()
            or not path.is_file()
            or not relative.endswith(".md")
            or not links.is_normalised_surface(relative)
        ):
            continue
        try:
            path.resolve().relative_to(root)
        except ValueError:
            # #107 for the names stamp skips before its own containment
            # check (`index.md`): never write through to outside the vault.
            report.reported.append((relative, "outside"))
            continue
        try:
            text = stamp._read_text(path)
        except (OSError, UnicodeError):
            continue  # stamp already reported it
        if index is None:
            index = captured.link_index(vault)
        new_text, problems = links.normalize(text, index, source=relative)
        report.problems.extend((relative, problem) for problem in problems)
        if new_text == text:
            continue
        try:
            stamp._write_text(path, new_text)
        except OSError:
            report.reported.append((relative, "unwritable"))
            continue
        report.normalised.append(relative)


def _regenerate_root_log(vault: Path) -> bool:
    target = vault / "log.md"
    if not target.exists() and not okf.day_files(vault):
        return False
    rendered = okf.render_log(vault)
    try:
        current = target.read_bytes()
    except OSError:
        current = None
    if current == rendered.encode("utf-8"):
        return False
    okf.write_log(vault, rendered)
    return True


def fix(vault_root, paths: Iterable[str] | None = None) -> FixReport:
    """Stamp, normalise, regenerate — on ``paths`` or the whole vault."""
    vault = Path(vault_root)
    listed = None if paths is None else [p for p in paths if _is_note(vault, p)]
    stamped, reported = stamp.stamp_types(vault, listed)
    report = FixReport(stamped=list(stamped), reported=list(reported))
    _normalise(vault, listed, report)
    report.log_regenerated = _regenerate_root_log(vault)
    report.reported.sort()
    return report


def _git_names(vault: Path, *args: str, env=None) -> list[str]:
    completed = subprocess.run(
        ["git", *args, "-z"], cwd=vault, check=True, capture_output=True, env=env
    )
    return [os.fsdecode(name) for name in completed.stdout.split(b"\0") if name]


def staged_paths(vault_root, env=None) -> tuple[list[str], list[str]]:
    """``(fully staged, partially staged)`` added-or-modified paths.

    Both reads honour ``GIT_INDEX_FILE``, which is how the hook sees the
    temporary index of a ``git commit -- <paths>`` (research Q1).
    """
    vault = Path(vault_root)
    staged = _git_names(
        vault, "diff", "--cached", "--name-only", "--diff-filter=AM", env=env
    )
    dirty = set(_git_names(vault, "diff", "--name-only", env=env))
    return (
        [path for path in staged if path not in dirty],
        [path for path in staged if path in dirty],
    )
