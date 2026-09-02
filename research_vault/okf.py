"""Root log.md regeneration: the single writer for OKF's log summary artifact."""

from pathlib import Path

from . import frontmatter


def _day_lines(day_file: Path) -> list[str]:
    try:
        _data, body = frontmatter.parse(day_file.read_text())
    except (OSError, UnicodeError, frontmatter.FrontmatterError):
        # A malformed or unreadable day file (hand-edited by a human) must
        # not crash regeneration for every other, well-formed day file — the
        # same tolerance _okf_probe already applies when scanning day files.
        return []
    return [line for line in body.splitlines() if line.strip()]


def regenerate_log(vault_root, tail_entries: int = 20) -> str:
    """Rewrite root ``log.md``: ``type: "log"`` frontmatter, a recent tail of
    entries across ``log/*.md`` day files (chronological), then a link to
    each day file."""
    vault = Path(vault_root)
    log_dir = vault / "log"
    day_files = sorted(log_dir.glob("*.md")) if log_dir.is_dir() else []

    lines = [line for day_file in day_files for line in _day_lines(day_file)]
    tail = lines[-tail_entries:] if tail_entries > 0 else []

    body_lines = ["# Log", ""]
    body_lines.extend(tail)
    if tail:
        body_lines.append("")
    # No "## Days" heading: OKF §11 rule 3 (structure.check_reserved) permits
    # only "## YYYY-MM-DD" second-level headings in log.md.
    body_lines.extend(f"- [[log/{day_file.stem}]]" for day_file in day_files)

    text = frontmatter.serialize({"type": "log"}) + "\n".join(body_lines) + "\n"
    (vault / "log.md").write_text(text)
    return text
