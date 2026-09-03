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
    """Rewrite root ``log.md`` per OKF §9: date-grouped, newest first."""
    vault = Path(vault_root)
    log_dir = vault / "log"
    day_files = sorted(log_dir.glob("*.md"), reverse=True) if log_dir.is_dir() else []

    body_lines = ["# Log"]
    remaining = tail_entries
    for day_file in day_files:
        lines = _day_lines(day_file)
        take = lines[:remaining] if remaining > 0 else []
        body_lines.extend(["", f"## {day_file.stem}"])
        body_lines.extend(take)
        body_lines.append(f"- [{day_file.stem}](log/{day_file.stem}.md)")
        remaining -= len(take)

    text = frontmatter.serialize({"type": "log"}) + "\n".join(body_lines) + "\n"
    (vault / "log.md").write_text(text)
    return text
