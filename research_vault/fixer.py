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

from . import captured, gitstate, links, okf, stamp, structure

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


def is_note(vault: Path, listed: str) -> bool:
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
        # Only a name stamp never reads (`index.md`) can fail here: stamp
        # reported every other failed read, and `skipped` holds those.
        try:
            text = stamp._read_text(path)
        except OSError:
            report.reported.append((relative, "outage"))
            continue
        except UnicodeError:
            report.reported.append((relative, "not-utf-8"))
            continue
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


def _regenerate_root_log(vault: Path, report: FixReport) -> bool:
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
    try:
        okf.write_log(vault, rendered)
    except OSError:
        # #174: reported like any unwritable file; the run still exits 0.
        report.reported.append(("log.md", "unwritable"))
        return False
    return True


def fix(vault_root, paths: Iterable[str] | None = None) -> FixReport:
    """Stamp, normalise, regenerate — on ``paths`` or the whole vault."""
    vault = Path(vault_root)
    listed = None if paths is None else [p for p in paths if is_note(vault, p)]
    stamped, reported = stamp.stamp_types(vault, listed)
    report = FixReport(stamped=list(stamped), reported=list(reported))
    _normalise(vault, listed, report)
    report.log_regenerated = _regenerate_root_log(vault, report)
    report.reported.sort()
    return report


def _git_names(vault: Path, *args: str, env=None) -> list[str]:
    """``git <args> -z``'s names; a failed run (no repository) is a named
    ``GitStateError`` carrying git's own first line, never a traceback."""
    completed = subprocess.run(
        ["git", *args, "-z"], cwd=vault, check=False, capture_output=True, env=env
    )
    if completed.returncode != 0:
        said = completed.stderr.decode("utf-8", "replace").strip().splitlines()
        raise gitstate.GitStateError(
            f"git {args[0]} failed with status {completed.returncode}"
            + (f": {said[0]}" if said else "")
        )
    return [os.fsdecode(name) for name in completed.stdout.split(b"\0") if name]


def staged_paths(vault_root, env=None) -> tuple[list[str], list[str]]:
    """``(fully staged, partially staged)`` added-or-modified paths.

    Both reads honour ``GIT_INDEX_FILE``, which is how the hook sees the
    temporary index of a ``git commit -- <paths>`` (research Q1). Neither
    pairs renames: a staged ``git mv`` lists its new path as added, and a
    worktree move of a staged file lists that file as changed, not hidden
    behind the name it moved to.
    """
    vault = Path(vault_root)
    # Outside a repository `git diff` falls back to `--no-index`, whose
    # refusal of `--cached` would hide the cause; rev-parse names it. (It
    # echoes the `-z` back as output, which is never read.)
    _git_names(vault, "rev-parse", "--git-dir", env=env)
    staged = _git_names(
        vault,
        "diff",
        "--cached",
        "--name-only",
        "--no-renames",
        "--diff-filter=AM",
        env=env,
    )
    dirty = set(_git_names(vault, "diff", "--name-only", "--no-renames", env=env))
    return (
        [path for path in staged if path not in dirty],
        [path for path in staged if path in dirty],
    )
