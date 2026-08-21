from harness_core import frontmatter, okf, scaffold


def test_scaffold_ships_okf_artifacts(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    idx, _ = frontmatter.parse((tmp_path / "index.md").read_text())
    assert idx["okf_version"] == "0.2" and idx["type"] == "index"
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
    assert "— b" in body and "— a" not in body
    assert "[[log/2026-08-19]]" in body and "[[log/2026-08-20]]" in body


def test_inbox_load_tolerates_frontmatter(fixture_vault):
    # HEAD already wraps review-queue.md in a `type` frontmatter block (Plan
    # C); build a clean single block from whatever body is already there
    # rather than concatenating a second header onto an existing one.
    from harness_core import Result, inbox
    p = fixture_vault / "inbox" / "review-queue.md"
    _data, body = frontmatter.parse(p.read_text())
    p.write_text('---\ntype: "review-queue"\n---\n' + body)
    inbox.append_entry(fixture_vault, "doi", "x", Result.UNMATCHED, "mismatch — t",
                       date="2026-08-20")
    assert inbox.load(fixture_vault)[-1].check == "doi"


def test_doctor_okf_probe(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    probes = {p[0] for p in scaffold.doctor(tmp_path, client=None, network=False)}
    assert "okf" in probes
