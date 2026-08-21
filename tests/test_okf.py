from harness_core import Result, frontmatter, okf, scaffold


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
    assert "[[log/2026-08-19]]" in body and "[[log/2026-08-20]]" in body


def test_doctor_okf_probe(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    probes = {p[0] for p in scaffold.doctor(tmp_path, client=None)}
    assert "okf" in probes


def test_okf_probe_matches_a_freshly_scaffolded_vault(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    probe = scaffold._okf_probe(tmp_path)
    assert probe.result == Result.MATCHED


def test_okf_probe_ignores_fleeting_inbox_notes_but_flags_machine_owned_files(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    # An untyped fleeting capture is exactly what inbox/ exists for (spec
    # §2's "tolerated residual") — it must not flip the probe.
    (tmp_path / "inbox" / "half-thought.md").write_text("just a fleeting idea\n")
    probe = scaffold._okf_probe(tmp_path)
    assert probe.result == Result.MATCHED

    # A machine-owned surface (literatures/) missing `type` is a real defect.
    (tmp_path / "literatures" / "untyped.md").write_text("# no frontmatter\n")
    probe = scaffold._okf_probe(tmp_path)
    assert probe.result == Result.UNMATCHED
    assert "literatures/untyped.md: missing type" in probe.reason


def test_okf_probe_root_index_missing_okf_version(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "index.md").write_text('---\ntype: "index"\n---\n# Vault index\n')
    probe = scaffold._okf_probe(tmp_path)
    assert probe.result == Result.UNMATCHED
    assert "index.md: missing okf_version" in probe.reason


def test_okf_probe_root_index_missing_type(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "index.md").write_text('---\nokf_version: "0.2"\n---\n# Vault index\n')
    probe = scaffold._okf_probe(tmp_path)
    assert probe.result == Result.UNMATCHED
    assert 'index.md: type must be "index"' in probe.reason


def test_okf_probe_missing_log_md_with_a_day_file_present(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log.md").unlink()
    (tmp_path / "log" / "2026-08-20.md").write_text('---\ntype: "daily"\n---\n')
    probe = scaffold._okf_probe(tmp_path)
    assert probe.result == Result.UNMATCHED
    assert "log.md missing despite day files present" in probe.reason
