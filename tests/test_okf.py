from research_vault import frontmatter, okf, scaffold


def test_scaffold_ships_okf_artifacts(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    idx, _ = frontmatter.parse((tmp_path / "index.md").read_text())
    assert idx["okf_version"] == "0.2"
    assert "type" not in idx
    rq, _ = frontmatter.parse((tmp_path / "inbox" / "review-queue.md").read_text())
    assert rq["type"] == "review-queue"
    ag, _ = frontmatter.parse((tmp_path / "AGENTS.md").read_text())
    assert ag["type"] == "guide"


def test_regenerate_log_tail(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-19.md").write_text("- 09:00 human:eran — a\n")
    (tmp_path / "log" / "2026-08-20.md").write_text("- 10:00 human:eran — b\n")
    okf.regenerate_log(tmp_path, tail_entries=1)
    text = (tmp_path / "log.md").read_text()
    data, body = frontmatter.parse(text)
    assert data["type"] == "log"
    assert "— b" in body
    assert "— a" not in body
    assert "[2026-08-19](log/2026-08-19.md)" in body
    assert "[2026-08-20](log/2026-08-20.md)" in body


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


def test_regenerate_log_skips_a_malformed_day_file(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-19.md").write_text("- 09:00 human:eran — a\n")
    # Unterminated frontmatter: a plausible hand-edit mistake in a daily note.
    (tmp_path / "log" / "2026-08-20.md").write_text(
        '---\ntype: "daily"\n- 10:00 human:eran — broken\n'
    )

    text = okf.regenerate_log(tmp_path)

    data, body = frontmatter.parse(text)
    assert data["type"] == "log"
    assert "— a" in body
    assert "[2026-08-19](log/2026-08-19.md)" in body
    assert "[2026-08-20](log/2026-08-20.md)" in body


def test_regenerated_log_is_date_grouped_newest_first(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-20.md").write_text(
        '---\ntype: "daily"\n---\n- 09:00 imported a\n'
    )
    (tmp_path / "log" / "2026-08-21.md").write_text(
        '---\ntype: "daily"\n---\n- 10:00 imported b\n'
    )
    text = okf.regenerate_log(tmp_path)
    body = text.split("---\n", 2)[2]
    assert "## Days" not in body
    first, second = body.index("## 2026-08-21"), body.index("## 2026-08-20")
    assert first < second
    assert "[2026-08-21](log/2026-08-21.md)" in body


def test_doctor_is_substrate_and_posture_only(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    names = [p[0] for p in scaffold.doctor(tmp_path, client=None)]
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
        "remote",
        "backup",
    ]
