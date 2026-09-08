"""Mechanical `type` stamping: the fixer half of OKF §11 rule 2 (audit §1).

`structure.check_note_frontmatter` only reports a missing/mismatched `type`;
this module repairs the mechanical half of that finding. It is purely
additive and fully determined only — it never overrides an existing `type`,
never guesses at ambiguous folders, and never touches a frontmatter block it
cannot parse. Two shapes are stamped:

- No frontmatter delimiter at all (a bare capture): folder derivation
  (`structure.expected_type`), falling back to the recorded `inbox/`
  fleeting exemption (`structure.is_fleeting`) since that exemption is
  deliberately excluded from `expected_type` itself — prepend a fresh block.
- A parseable block missing `type`, with `structure.expected_type` deriving
  one (the fleeting fallback does *not* apply here — a file that already
  carries hand-written frontmatter keys but no `type` is ambiguous, not a
  bare capture) — insert `type` as the first key, otherwise byte-for-byte,
  including the file's original line-ending style (CRLF is preserved, never
  flattened to LF).

Everything else is reported, never edited: a human decides those. Each
reported path carries a reason — `"symlink"` (the path itself is a symlink;
writing through it could escape the vault boundary), `"unparseable"`
(unparseable YAML-shaped frontmatter, or frontmatter with a duplicate
top-level key — `frontmatter._DuplicateKeyMapping` — since a plain
`{"type": derived, **data}` spread would silently collapse the repeats to
last-write-wins), or `"no-type"` (no derivation at all — `system/`, root
files, non-canonical `projects/` files).
"""

from pathlib import Path

from . import events, frontmatter, structure

_SKIP_NAMES = {"index.md"}
_SKIP_DIRS = structure.EXCLUDED_DIRS | {"fulltext"}


def _has_delimiter(text: str) -> bool:
    return text.startswith(("---\n", "---\r\n"))


def _candidate_paths(vault: Path, paths):
    if paths is not None:
        for raw in paths:
            candidate = Path(raw)
            yield candidate if candidate.is_absolute() else vault / candidate
        return
    for path in sorted(vault.rglob("*.md")):
        if any(part in _SKIP_DIRS for part in path.relative_to(vault).parts):
            continue
        yield path


def _read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _write_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def stamp_types(vault_root, paths=None) -> tuple[list[str], list[tuple[str, str]]]:
    """Stamp what's fully determined; report the rest. Never raises for content.

    ``reported`` entries are ``(path, reason)`` pairs — see the module
    docstring for the reason vocabulary.
    """
    vault = Path(vault_root)
    stamped: list[str] = []
    reported: list[tuple[str, str]] = []
    for path in _candidate_paths(vault, paths):
        if ".git" in path.parts or path.name in _SKIP_NAMES:
            continue
        if path.is_symlink():
            # Refuse to write through a symlink — the target could sit
            # outside the vault boundary entirely. Report, don't edit.
            reported.append((path.relative_to(vault).as_posix(), "symlink"))
            continue
        if not path.is_file():
            continue
        relative = path.relative_to(vault).as_posix()
        if relative == "log.md":
            continue

        text = _read_text(path)
        has_delimiter = _has_delimiter(text)
        try:
            data, body = frontmatter.parse(text)
        except frontmatter.FrontmatterError:
            reported.append((relative, "unparseable"))
            continue

        if "type" in data:
            continue

        if has_delimiter:
            # Ambiguous block: only the folder derivation applies, not the
            # fleeting fallback (see module docstring).
            derived = structure.expected_type(relative)
        else:
            derived = structure.expected_type(relative)
            if derived is None and structure.is_fleeting(relative):
                derived = "fleeting"

        if derived is None:
            reported.append((relative, "no-type"))
            continue

        newline = events._first_line_ending(text)

        if has_delimiter:
            if isinstance(data, frontmatter._DuplicateKeyMapping):
                # A plain-dict spread would collapse repeated keys to
                # last-write-wins before serialize ever sees them — report,
                # don't edit, same as unparseable YAML above.
                reported.append((relative, "unparseable"))
                continue
            block = frontmatter.serialize({"type": derived, **data})
        else:
            block = f'---\ntype: "{derived}"\n---\n'
        if newline == "\r\n":
            block = block.replace("\n", newline)
        new_text = block + body
        _write_text(path, new_text)
        stamped.append(relative)

    return sorted(stamped), sorted(reported)
