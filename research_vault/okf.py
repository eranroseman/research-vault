"""Root ``log.md``: the pure render and its one writer (OKF §9; #204, #210).

``render_log`` reads only the day files — ``log/<YYYY-MM-DD>.md`` — and copies
only lines in the writer's own format, so a stray file or a hand-typed line
under ``log/`` can neither break the render nor smuggle text into it;
``structure.check_log_dir`` reports those under their own paths. The fixer
regenerates ``log.md`` and ``check_reserved`` compares it byte for byte.
"""

import re
from pathlib import Path

from . import frontmatter, structure

# `publish._append_log`'s line: `- HH:MM research_vault/<version> — <text>`.
WRITER_LINE = re.compile(r"^- \d{2}:\d{2} research_vault/\S+ — .+$")


def day_files(vault_root) -> list[Path]:
    """``log/<day>.md``, newest first; only calendar-date stems are day files."""
    vault = Path(vault_root)
    log_dir = vault / "log"
    if not log_dir.is_dir():
        return []
    return sorted(
        (
            path
            for path in log_dir.glob("*.md")
            if not structure.is_excluded(path, vault)
            and structure.is_day_stem(path.stem)
        ),
        reverse=True,
    )


def _day_lines(day_file: Path) -> list[str]:
    try:
        _data, body = frontmatter.parse(day_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, frontmatter.FrontmatterError):
        # A malformed day file is check_log_dir's row, never the end of the render.
        return []
    return [line for line in body.splitlines() if WRITER_LINE.match(line)]


def render_log(vault_root, tail_entries: int = 20) -> str:
    """OKF §9's shape: date-grouped, newest first, the `tail_entries` newest lines."""
    body_lines = ["# Log"]
    remaining = tail_entries
    for day_file in day_files(vault_root):
        lines = _day_lines(day_file)
        take = lines[:remaining] if remaining > 0 else []
        body_lines.extend(["", f"## {day_file.stem}"])
        body_lines.extend(take)
        body_lines.append(f"- [{day_file.stem}](/log/{day_file.stem}.md)")
        remaining -= len(take)
    return frontmatter.serialize({"type": "log"}) + "\n".join(body_lines) + "\n"


def write_log(vault_root, text: str) -> None:
    # #170: utf-8 named, newline="" so the bytes match the render on every
    # platform (#210 compares them).
    with (Path(vault_root) / "log.md").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        handle.write(text)


def regenerate_log(vault_root, tail_entries: int = 20) -> str:
    text = render_log(vault_root, tail_entries)
    write_log(vault_root, text)
    return text
