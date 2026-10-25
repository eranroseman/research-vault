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
- A parseable block whose `type` is missing as the structure check reads it
  (`frontmatter.okf_type` over `frontmatter.read_okf`: absent, or a value
  OKF rule 2's `not value` test reads as missing — a blank `type:`, `null`,
  `~`, `false`, `0`, `[]` — whose line is replaced, never a second added),
  with `structure.expected_type` deriving one (the fleeting fallback
  does *not* apply here — a file that already carries hand-written
  frontmatter keys but no `type` is ambiguous, not a bare capture) — insert
  `type` as the first key, otherwise byte-for-byte, including the file's
  original line-ending style (CRLF is preserved, never flattened to LF).

Everything else is reported, never edited: a human decides those. Each
reported path carries a reason — `"symlink"` (the path itself is a symlink;
writing through it could escape the vault boundary), `"unparseable"`
(frontmatter the flat parser or `frontmatter.read_okf` refuses; a block
the two read with different keys — a duplicate top-level key, which a
plain `{"type": derived, **data}` spread would otherwise collapse to
last-write-wins, a key YAML reads as other than its text, or a quoted
value that runs onto a line the flat parser takes for a key; or a block
whose stamped form does not read back as `{type, **data}` under
`frontmatter.read_okf`), `"outage"` (the file could
not be read at all), `"not-utf-8"` (the file is not UTF-8, so no
frontmatter could be parsed from it), `"unwritable"` (the stamp could not
be written back, #174),
`"outside"` (the path resolves outside the vault: a symlinked ancestor, an
absolute path elsewhere, a `..` that lexically passes), or `"no-type"` (no
derivation at all — `system/`, root files, non-canonical `projects/` files).
"""

from pathlib import Path

from . import events, frontmatter, structure

_SKIP_NAMES = {"index.md"}
_SKIP_DIRS = frozenset({"fulltext"})


def _has_delimiter(text: str) -> bool:
    return text.startswith(("---\n", "---\r\n"))


def _candidate_paths(vault: Path, paths):
    if paths is not None:
        for raw in paths:
            candidate = Path(raw)
            yield candidate if candidate.is_absolute() else vault / candidate
        return
    for path in sorted(vault.rglob("*.md")):
        if structure.is_excluded(path, vault) or any(
            part in _SKIP_DIRS for part in path.relative_to(vault).parts
        ):
            continue
        yield path


def _read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _write_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def _reported_name(path: Path, vault: Path) -> str:
    """The unresolved spelling: vault-relative where the path lies under the
    vault lexically, the caller's absolute string otherwise."""
    try:
        return path.relative_to(vault).as_posix()
    except ValueError:
        return str(path)


def stamp_types(vault_root, paths=None) -> tuple[list[str], list[tuple[str, str]]]:
    """Stamp what's fully determined; report the rest. Never raises for content.

    ``reported`` entries are ``(path, reason)`` pairs — see the module
    docstring for the reason vocabulary.
    """
    vault = Path(vault_root)
    root = vault.resolve()
    stamped: list[str] = []
    reported: list[tuple[str, str]] = []
    for path in _candidate_paths(vault, paths):
        if ".git" in path.parts or path.name in _SKIP_NAMES:
            continue
        if path.is_symlink():
            # Refuse to write through a symlink — the target could sit
            # outside the vault boundary entirely. Report, don't edit.
            reported.append((_reported_name(path, vault), "symlink"))
            continue
        if not path.is_file():
            continue
        try:
            path.resolve().relative_to(root)
        except ValueError:
            # #107: a real file under a symlinked ancestor, an absolute path
            # elsewhere, or a `..` that lexically passes: outside the vault,
            # reported under the spelling the caller gave, never written.
            reported.append((_reported_name(path, vault), "outside"))
            continue
        relative = _reported_name(path, vault)
        if relative == "log.md":
            continue

        try:
            text = _read_text(path)
        except OSError:
            reported.append((relative, "outage"))
            continue
        except UnicodeError:
            reported.append((relative, "not-utf-8"))
            continue
        has_delimiter = _has_delimiter(text)
        try:
            data, body = frontmatter.parse(text)
            # Q18: "type missing" is decided by the structure check's own
            # reader and test, never by the flat parser's view of the value,
            # so every missing type the check reports is one stamp repairs.
            # A missing PyYAML is not content: it propagates (§5.6).
            okf_data, _ = frontmatter.read_okf(text)
        except frontmatter.FrontmatterError:
            reported.append((relative, "unparseable"))
            continue
        if frontmatter.okf_type(okf_data):
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
            # Q18: the insert rewrites the block from the flat parser's view,
            # so that view must have the keys the OKF reader reads, in order.
            # Otherwise the rewrite drops or invents a key: a repeated key
            # (a plain spread collapses it to last-write-wins), a key YAML
            # reads as other than its text (`yes`, `1`, `.nan`, a quoted
            # `"type"`), or a double-quoted value that runs onto a line the
            # flat parser takes for a key (`a: "x` / `a: y"`).
            keys = [key for key, _value in frontmatter._mapping_items(data)]
            if keys != list(okf_data):
                reported.append((relative, "unparseable"))
                continue
            rest = {k: v for k, v in frontmatter._mapping_items(data) if k != "type"}
            block = frontmatter.serialize({"type": derived, **rest})
            # After the insert, the block must read back as {type, **data}
            # under the OKF reader. With the keys agreeing, a value can still
            # re-emit as something YAML refuses: the flat parser reads an
            # empty `{}` as `{"": ""}`, which serializes as `{: ""}`.
            try:
                reparsed, _ = frontmatter.read_okf(block + body)
            except frontmatter.FrontmatterError:
                reported.append((relative, "unparseable"))
                continue
            if reparsed.get("type") != derived or set(reparsed) != {"type", *rest}:
                reported.append((relative, "unparseable"))
                continue
        else:
            block = f'---\ntype: "{derived}"\n---\n'
        if newline == "\r\n":
            block = block.replace("\n", newline)
        new_text = block + body
        try:
            _write_text(path, new_text)
        except OSError:
            # #174: an unwritable file is a report under its own path and the
            # walk continues; the verb still exits 0.
            reported.append((relative, "unwritable"))
            continue
        stamped.append(relative)

    return sorted(stamped), sorted(reported)
