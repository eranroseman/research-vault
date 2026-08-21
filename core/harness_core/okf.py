"""Root log.md regeneration: the single writer for OKF's log summary artifact."""

from pathlib import Path

from . import frontmatter


def _day_lines(day_file: Path) -> list[str]:
    _data, body = frontmatter.parse(day_file.read_text())
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
    body_lines.append("## Days")
    body_lines.extend(f"- [[log/{day_file.stem}]]" for day_file in day_files)

    text = frontmatter.serialize({"type": "log"}) + "\n".join(body_lines) + "\n"
    (vault / "log.md").write_text(text)
    return text
