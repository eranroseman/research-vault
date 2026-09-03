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
  bare capture) — insert `type` as the first key, otherwise byte-for-byte.

Everything else (unparseable YAML-shaped frontmatter, frontmatter with a
duplicate top-level key — `frontmatter._DuplicateKeyMapping` — since a plain
`{"type": derived, **data}` spread would silently collapse the repeats to
last-write-wins, or no derivation at all — `system/`, root files,
non-canonical `projects/` files) is reported, never edited: a human decides
those.
"""

from pathlib import Path

from . import frontmatter, structure

_SKIP_NAMES = {"index.md"}


def _has_delimiter(text: str) -> bool:
    return text.startswith(("---\n", "---\r\n"))


def _candidate_paths(vault: Path, paths):
    if paths is not None:
        for raw in paths:
            candidate = Path(raw)
            yield candidate if candidate.is_absolute() else vault / candidate
        return
    yield from sorted(vault.rglob("*.md"))


def stamp_types(vault_root, paths=None) -> tuple[list[str], list[str]]:
    """Stamp what's fully determined; report the rest. Never raises for content."""
    vault = Path(vault_root)
    stamped: list[str] = []
    reported: list[str] = []
    for path in _candidate_paths(vault, paths):
        if ".git" in path.parts or path.name in _SKIP_NAMES or not path.is_file():
            continue
        relative = path.relative_to(vault).as_posix()
        if relative == "log.md":
            continue

        text = path.read_text()
        has_delimiter = _has_delimiter(text)
        try:
            data, body = frontmatter.parse(text)
        except frontmatter.FrontmatterError:
            reported.append(relative)
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
            reported.append(relative)
            continue

        if has_delimiter:
            if isinstance(data, frontmatter._DuplicateKeyMapping):
                # A plain-dict spread would collapse repeated keys to
                # last-write-wins before serialize ever sees them — report,
                # don't edit, same as unparseable YAML above.
                reported.append(relative)
                continue
            new_text = frontmatter.serialize({"type": derived, **data}) + body
        else:
            new_text = f'---\ntype: "{derived}"\n---\n' + text
        path.write_text(new_text)
        stamped.append(relative)

    return sorted(stamped), sorted(reported)
