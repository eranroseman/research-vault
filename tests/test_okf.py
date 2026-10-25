from research_vault import doctor, frontmatter, okf, scaffold

WRITER = "research_vault/0.1.0"


def test_scaffold_ships_okf_artifacts(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    idx, _ = frontmatter.parse((tmp_path / "index.md").read_text())
    assert idx["okf_version"] == "0.2"
    assert "type" not in idx
    rq, _ = frontmatter.parse((tmp_path / "inbox" / "review-queue.md").read_text())
    assert rq["type"] == "review-queue"
    ag, _ = frontmatter.parse((tmp_path / "AGENTS.md").read_text())
    assert ag["type"] == "guide"


def test_render_log_tail_and_links(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-19.md").write_text(
        f'---\ntype: "log"\n---\n- 09:00 {WRITER} — a\n'
    )
    (tmp_path / "log" / "2026-08-20.md").write_text(
        f'---\ntype: "log"\n---\n- 10:00 {WRITER} — b\n'
    )
    text = okf.render_log(tmp_path, tail_entries=1)
    data, body = frontmatter.parse(text)
    assert data["type"] == "log"
    assert "— b" in body
    assert "— a" not in body
    assert "- [2026-08-19](/log/2026-08-19.md)" in body
    assert "- [2026-08-20](/log/2026-08-20.md)" in body
    assert not (tmp_path / "log.md").read_text().endswith(body)  # render_log is pure
    assert okf.regenerate_log(tmp_path, tail_entries=1) == text
    assert (tmp_path / "log.md").read_bytes() == text.encode("utf-8")


def test_render_log_skips_a_malformed_day_file_and_keeps_its_link(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-19.md").write_text(
        f'---\ntype: "log"\n---\n- 09:00 {WRITER} — a\n'
    )
    (tmp_path / "log" / "2026-08-20.md").write_text(
        f'---\ntype: "log"\n- 10:00 {WRITER} — broken\n'
    )
    text = okf.render_log(tmp_path)
    assert "— a" in text
    assert "— broken" not in text
    assert "[2026-08-20](/log/2026-08-20.md)" in text


def test_render_log_is_date_grouped_newest_first(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-20.md").write_text(
        f'---\ntype: "log"\n---\n- 09:00 {WRITER} — a\n'
    )
    (tmp_path / "log" / "2026-08-21.md").write_text(
        f'---\ntype: "log"\n---\n- 10:00 {WRITER} — b\n'
    )
    body = okf.render_log(tmp_path).split("---\n", 2)[2]
    assert body.index("## 2026-08-21") < body.index("## 2026-08-20")


def test_render_log_renders_only_day_stems_and_writer_lines(tmp_path):
    """#204: a non-date file is not a day file, and a line outside the writer's
    format is not an entry. A 25-line stray uses none of the 20-line budget."""
    scaffold.scaffold_vault(tmp_path)
    log = tmp_path / "log"
    (log / "Untitled.md").write_text(
        "".join(f"- {i:02d}:00 {WRITER} — stray\n" for i in range(25))
    )
    (log / "2026-13-45.md").write_text(
        f'---\ntype: "log"\n---\n- 09:00 {WRITER} — bad date\n'
    )
    (log / "20261004.md").write_text(
        f'---\ntype: "log"\n---\n- 09:00 {WRITER} — compact\n'
    )
    (log / "2026-10-01.md").write_text(
        f'---\ntype: "log"\n---\n## Agenda\n- 09:00 {WRITER} — real\n- hand-typed line\n'
    )
    text = okf.render_log(tmp_path)
    assert "## 2026-10-01" in text
    assert "— real" in text
    for absent in (
        "Agenda",
        "hand-typed",
        "stray",
        "bad date",
        "compact",
        "Untitled",
        "2026-13-45",
        "20261004",
    ):
        assert absent not in text, absent
    assert [p.name for p in okf.day_files(tmp_path)] == ["2026-10-01.md"]


def test_okf_write_text_sites_name_their_encoding():
    """#170: under an ASCII locale the em dash in the writer's format raised
    UnicodeEncodeError from `write_text`; every write in the package names utf-8."""
    import ast
    from pathlib import Path

    from tests.conftest import package_ast

    root = Path(__file__).resolve().parents[1] / "research_vault"
    bare = [
        f"{module.name}:{node.lineno}"
        for module in sorted(root.glob("*.py"))
        for node in ast.walk(package_ast(module))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "write_text"
        and not any(k.arg == "encoding" for k in node.keywords)
    ]
    assert bare == [], bare


def test_regenerate_log_writes_utf8_under_an_ascii_locale(tmp_path):
    """#170 measured: `LC_ALL=C python3 -X utf8=0` gives an ASCII locale; the em
    dash in `render_log`'s lines raised before the fix."""
    import subprocess
    import sys

    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-19.md").write_text(
        f'---\ntype: "log"\n---\n- 09:00 {WRITER} — ascii locale\n', encoding="utf-8"
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8=0",
            "-c",
            "import sys; from research_vault import okf; okf.regenerate_log(sys.argv[1])",
            str(tmp_path),
        ],
        env={**__import__("os").environ, "LC_ALL": "C", "PYTHONUTF8": "0"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "ascii locale" in (tmp_path / "log.md").read_text(encoding="utf-8")


def test_inbox_load_tolerates_frontmatter(fixture_vault):
    # HEAD already wraps review-queue.md in a `type` frontmatter block (Plan
    # C); build a clean single block from whatever body is already there
    # rather than concatenating a second header onto an existing one.
    from research_vault import Result, inbox

    p = fixture_vault / "inbox" / "review-queue.md"
    _data, body = frontmatter.parse(p.read_text())
    p.write_text('---\ntype: "review-queue"\n---\n' + body)
    inbox.append_entry(
        fixture_vault, "doi", "x", Result.UNMATCHED, "mismatch — t", date="2026-08-20"
    )
    assert inbox.load(fixture_vault)[-1].check == "doi"


def test_doctor_is_substrate_and_posture_only(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    names = [p[0] for p in doctor.doctor(tmp_path, client=None)]
    assert names == [
        "tree",
        "machine-config",
        "zotero",
        "write-guard",
        "fulltext-sync",
        "bbt",
        "bbt-git",
        "plugins",
        "path-shim",
        "translator-formats",
        "compile-tool",
        "pyyaml",
        "remote",
        "backup",
    ]
