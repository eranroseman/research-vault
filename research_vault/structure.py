"""OKF §11 structure checks over vault files (audit §1).

The vault rule: a note's ``type`` is determined by its folder. ``system/``
and root-level concepts carry any non-empty type. ``inbox/`` captures other
than the review queue are the recorded fleeting exemption — checked here only
for the reserved ``type: fulltext`` (§5.5); the fixer converges them when they
are staged (§5.1).

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

import datetime
import os
import re
from pathlib import Path

from . import frontmatter, fulltext, literature_notes
from .outcome import Outcome, Result
from .pathcodec import RepoPath

_FOLDER_TYPES = {
    "literature": "literature",
    # §4.4: `log/` is the machines' activity record and `daily/` the person's
    # diary. The type comes from the top folder at any depth, so a weekly note
    # under `daily/weekly/` is `daily` too.
    "log": "log",
    "daily": "daily",
    "inbox": "fleeting",
}
# The compile tool's own stores (ingest spec §4.3): `.raw/` would hold a
# duplicate of `fulltext/` if its capture were ever run, and `.vault-meta/` is
# its runtime state. Both are gitignored and never walked: `is_excluded`'s
# dot-component rule covers them, and `.git/` with them.
# #194: Obsidian itself skips any path with a component starting with a dot
# (`validateConfigDir`, app.js 1.13.7), so a plugin's README.md under
# `.obsidian/`, Claude Code's `.claude/`, Obsidian's `.trash/` and a
# plugin's nested dotfile are never notes. The OS-litter names are the
# three upstream gitignore templates spell (Q25): macOS `.DS_Store` and
# AppleDouble `._*` (which match a `*.md` glob), and Windows `desktop.ini`
# in both casings.
OS_LITTER = frozenset({".DS_Store", "desktop.ini", "Desktop.ini"})
_APPLE_DOUBLE_PREFIX = "._"
RESERVED_NAMES = frozenset({"index.md", "log.md"})
# docs/agents/okf-conformance.md's register, rows 1 and 2: the adopted compile
# tool writes these three reserved-name files with its own shape (frontmatter
# on the two indexes, model-formatted bullets in its log), at hard-coded paths.
# They pass by name; any other reserved name under wiki/ is refused by name
# until the compiled-page record (#212) can say who wrote it.
_TOOL_RESERVED_FILES = frozenset(
    {"wiki/index.md", "wiki/log.md", "wiki/canvases/index.md"}
)
# Folders whose reserved-name files nobody but a machine writes: a stray one
# is refused outright.
_MACHINE_RESERVED_PREFIXES = ("system/propagations/",)

_PROJECT_NOTE_NAME = "draft.md"


def is_os_litter(name: str) -> bool:
    return name in OS_LITTER or name.startswith(_APPLE_DOUBLE_PREFIX)


def is_excluded(path: Path, vault: Path) -> bool:
    """The one walker predicate (#194): dot-components, the stores among them, OS litter.

    Every walker in the package calls this; a test pins that every `glob`,
    `rglob` and `iterdir` calls it or walks no vault note. `.gitkeep` is a
    dot-name too, so a walker over every file (not only `*.md`) treats the
    sentinel as excluded, which is right: nothing reads it.
    """
    parts = path.relative_to(vault).parts
    return any(part.startswith(".") for part in parts) or (
        bool(parts) and is_os_litter(parts[-1])
    )


def is_fleeting(relative: str) -> bool:
    return relative.startswith("inbox/") and relative != "inbox/review-queue.md"


def is_reserved(relative: str) -> bool:
    """OKF §3.1: `index.md` and `log.md` are reserved at any depth (#209)."""
    return relative.rsplit("/", 1)[-1] in RESERVED_NAMES


def is_day_stem(stem: str) -> bool:
    """A `log/` day file's stem is exactly a calendar date (#204): `2026-13-45`
    and `20261004` are strays, not day files."""
    try:
        return datetime.date.fromisoformat(stem).isoformat() == stem
    except ValueError:
        return False


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
    """Rules 1 and 2 plus the folder-type vault rule, for one non-reserved file.

    `type: fulltext` is reserved for `fulltext/` (§5.5), tested before the
    fleeting exemption, so a text file moved into `inbox/` is refused too.
    """
    vault = Path(vault_root)
    relative = Path(path).relative_to(vault).as_posix()
    try:
        data, _body = frontmatter.read_okf(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, frontmatter.FrontmatterError) as error:
        if is_fleeting(relative):
            return []
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                f"schema-violation — frontmatter unparseable ({error})",
            )
        ]
    # §5.5: `type: fulltext` belongs to fulltext/ alone, and the test comes
    # before inbox/'s exemption so a moved text file is refused anywhere (Q26).
    if data.get("type") == "fulltext" and not relative.startswith(
        f"{fulltext.FULLTEXT_DIR}/"
    ):
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                "schema-violation — type 'fulltext' is reserved for "
                f"{fulltext.FULLTEXT_DIR}/",
            )
        ]
    if is_fleeting(relative):
        return []
    if not frontmatter.okf_type(data):
        return [
            Outcome(
                "okf-frontmatter",
                _repo_path(relative),
                Result.UNMATCHED,
                "schema-violation — missing type (OKF §11 rule 2)",
            )
        ]
    okf_type = data["type"]
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


_DATE_HEADING = re.compile(r"## (?P<day>\S+)\s*$")
_LIST_LINE = re.compile(r"^(?:[-*+] |\d+[.)] )")


def _log_shape_problems(text: str) -> list[str]:
    """§9 log shape: only ``## YYYY-MM-DD`` second-level headings, newest first."""
    try:
        _data, body = frontmatter.read_okf(text)
    except frontmatter.FrontmatterError:
        # frontmatter on log.md is legal but optional (§8 names index.md only)
        body = text
    dates = []
    for line in body.splitlines():
        if line.startswith("## "):
            match = _DATE_HEADING.match(line)
            if not match or not is_day_stem(match.group("day")):
                return [f"non-date second-level heading {line!r}"]
            dates.append(match.group("day"))
    if dates != sorted(dates, reverse=True):
        return ["day headings not newest first"]
    return []


def _index_shape_problems(body: str) -> list[str]:
    """§8 index shape: headings carrying lists of entries; an empty body is
    valid (Q22). Prose outside a heading or a list item is the finding; an
    indented line under a list entry is that entry's continuation."""
    in_list = False
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            in_list = False
        elif _LIST_LINE.match(stripped):
            in_list = True
        elif not (in_list and line[0] in " \t"):
            return [
                f"index body line is neither a heading nor a list entry: {stripped!r}"
            ]
    return []


def _okf_structure(relative: str, detail: str) -> Outcome:
    return Outcome(
        "okf-structure",
        _repo_path(relative),
        Result.UNMATCHED,
        f"schema-violation — {detail}",
    )


def check_log_dir(vault_root) -> list[Outcome]:
    """#204: `log/` holds `.gitkeep` and `<YYYY-MM-DD>.md` day files whose body
    lines are the writer's; a directory is a `tree` row and anything else an
    `okf-structure` row under its own path, never under log.md."""
    # Lazy: okf imports structure.
    from . import okf

    vault = Path(vault_root)
    log_dir = vault / "log"
    if not log_dir.is_dir():
        return []
    rows: list[Outcome] = []
    for child in sorted(log_dir.iterdir()):
        # One rule for both flat machine folders, log/ and literature/: the
        # sentinel, OS litter and a dot-directory (a sync tool's store, which
        # Obsidian ignores; #194) are no entry. Any other directory is a
        # `tree` row; every other file, a dot-named one too, meets the
        # folder's name rule (#204, #211). Reasons carry no path: the
        # encoded target does, and a raw name may not be UTF-8.
        if child.name == ".gitkeep" or is_os_litter(child.name):
            continue
        relative = f"log/{child.name}"
        if child.is_dir():
            if not is_excluded(child, vault):
                rows.append(
                    Outcome(
                        "tree",
                        f"{relative}/",
                        Result.UNMATCHED,
                        "schema-violation — log/ is flat",
                    )
                )
            continue
        if child.suffix != ".md" or not is_day_stem(child.stem):
            rows.append(
                _okf_structure(
                    relative, "log/ holds only <YYYY-MM-DD>.md day files and .gitkeep"
                )
            )
            continue
        try:
            text = child.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue  # check_note_frontmatter's row
        try:
            _data, body = frontmatter.parse(text)
        except frontmatter.FrontmatterError:
            # The render reads a day file through the flat parser: a block only
            # the OKF reader accepts passes check_note_frontmatter, yet drops
            # the file's lines from log.md, so this is its one row (#204).
            rows.append(
                _okf_structure(relative, "frontmatter is not the writer's flat form")
            )
            continue
        # The file's own line numbers: the body starts below the block.
        first = text.count("\n", 0, len(text) - len(body)) + 1
        for number, line in enumerate(body.splitlines(), start=first):
            if line.strip() and not okf.WRITER_LINE.match(line):
                rows.append(
                    _okf_structure(
                        relative,
                        f"line {number} is not in the writer's format: {line!r}",
                    )
                )
    return rows


def check_reserved(vault_root) -> list[Outcome]:
    """§11 rule 3: index.md per §8/§12, log.md per §9, at any depth (#209, #210)."""
    # Lazy: okf imports structure.
    from . import okf

    vault = Path(vault_root)
    problems: list[tuple[str, str]] = []
    for path in sorted(vault.rglob("*.md")):
        if is_excluded(path, vault):
            continue
        relative = path.relative_to(vault).as_posix()
        if not is_reserved(relative) or relative.startswith("log/"):
            continue  # a log/ entry is check_log_dir's row
        try:
            raw = path.read_bytes()
        except OSError as error:
            problems.append((relative, f"unreadable ({error})"))
            continue
        if relative == "log.md":
            # #210: byte for byte, so a CRLF copy of the render differs too.
            if raw != okf.render_log(vault).encode("utf-8"):
                problems.append(
                    (
                        relative,
                        (
                            "root log.md differs from its render; run stamp-type, "
                            "which regenerates it, and stage log.md"
                        ),
                    )
                )
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeError as error:
            problems.append((relative, f"unreadable ({error})"))
            continue
        if relative == "index.md":
            try:
                data, _body = frontmatter.read_okf(text)
            except frontmatter.FrontmatterError as error:
                problems.append((relative, f"unreadable ({error})"))
                continue
            extra = sorted((str(key) for key in set(data) - {"okf_version"}), key=str)
            if extra:
                problems.append(
                    (relative, f"root index carries keys beyond okf_version: {extra}")
                )
            if not str(data.get("okf_version", "")).strip():
                problems.append((relative, "missing okf_version"))
            continue
        if relative in _TOOL_RESERVED_FILES:
            continue
        if relative.startswith("wiki/"):
            problems.append(
                (
                    relative,
                    (
                        "reserved name under wiki/ outside the compile tool's files "
                        "(wiki/index.md, wiki/log.md, wiki/canvases/index.md)"
                    ),
                )
            )
            continue
        if relative.startswith(_MACHINE_RESERVED_PREFIXES):
            problems.append((relative, "reserved name under a machine-written folder"))
            continue
        try:
            data, body = frontmatter.read_okf(text)
        except frontmatter.FrontmatterError as error:
            problems.append((relative, f"frontmatter block does not parse ({error})"))
            continue
        has_block = frontmatter._FRONTMATTER_OPEN.match(text) is not None
        if path.name == "index.md":
            if has_block:  # an empty block too: §8 wants none at all
                problems.append((relative, "nested index.md must be frontmatter-free"))
            problems.extend((relative, p) for p in _index_shape_problems(body))
        else:
            if has_block and not frontmatter.okf_type(data):
                problems.append((relative, "missing type (OKF §11 rule 2)"))
            problems.extend((relative, p) for p in _log_shape_problems(text))
    if problems:
        return [_okf_structure(relative, detail) for relative, detail in problems]
    return [Outcome("okf-structure", "reserved-files", Result.MATCHED, "matched")]


def check_tree(vault_root) -> list[Outcome]:
    """Vault-wide directory scaffolding attestation (verify-side; see doctor.doctor).

    Doctor keeps a separate `tree` probe for repair-at-setup; this is a
    different job — verify-side attestation only, no repair. The existing
    tree row, plus one row per directory nested under `literature/`: every
    reader of the evidence layer globs it flat (decision 08), so a note in a
    nested directory is a literature note nowhere — reported here rather than
    typed by folder and forgotten. So is every file there but `.gitkeep` and
    `<citation key>.md` (#211): a PDF, a text file, a name no key gives.
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
            # One rule for both flat machine folders, log/ and literature/: the
            # sentinel, OS litter and a dot-directory (a sync tool's store, which
            # Obsidian ignores; #194) are no entry. Any other directory is a
            # `tree` row; every other file, a dot-named one too, meets the
            # folder's name rule (#204, #211). Reasons carry no path: the
            # encoded target does, and a raw name may not be UTF-8.
            if child.name == ".gitkeep" or is_os_litter(child.name):
                continue
            excluded = is_excluded(child, vault)
            relative = f"literature/{child.name}"
            if child.is_dir():
                if not excluded:
                    rows.append(
                        Outcome(
                            "tree",
                            f"{relative}/",
                            Result.UNMATCHED,
                            "schema-violation — literature/ is flat",
                        )
                    )
                continue
            if excluded or not _is_citation_key_note(vault, child):
                rows.append(
                    Outcome(
                        "tree",
                        _repo_path(relative),
                        Result.UNMATCHED,
                        "schema-violation — literature/ holds only "
                        "<citation key>.md and .gitkeep",
                    )
                )
    return rows


def _is_citation_key_note(vault: Path, path: Path) -> bool:
    """`<key>.md` for a key capture could have written (`note_path`'s rule)."""
    if path.suffix != ".md":
        return False
    try:
        literature_notes.note_path(vault, path.stem)
    except literature_notes.InvalidCitationKeyError:
        return False
    return True
