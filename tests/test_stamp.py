from research_vault import frontmatter, stamp


def test_stamps_bare_capture_with_folder_type(tmp_path):
    (tmp_path / "inbox").mkdir(parents=True)
    note = tmp_path / "inbox" / "idea.md"
    note.write_text("a half thought\n")
    stamped, reported = stamp.stamp_types(tmp_path)
    assert stamped == ["inbox/idea.md"]
    assert reported == []
    data, body = frontmatter.parse(note.read_text())
    assert data == {"type": "fleeting"}
    assert "a half thought" in body


def test_inserts_type_into_parseable_block(tmp_path):
    (tmp_path / "literatures").mkdir(parents=True)
    note = tmp_path / "literatures" / "x.md"
    note.write_text('---\ncitekey: "x"\n---\nbody\n')
    stamped, _ = stamp.stamp_types(tmp_path)
    assert stamped == ["literatures/x.md"]
    data, _ = frontmatter.parse(note.read_text())
    assert data["type"] == "literature"
    assert data["citekey"] == "x"


def test_reports_unparseable_and_underived(tmp_path):
    (tmp_path / "inbox").mkdir(parents=True)
    (tmp_path / "system").mkdir(parents=True)
    bad = tmp_path / "inbox" / "broken.md"
    bad.write_text("---\nnot: [closed\n---\ntext\n")
    loose = tmp_path / "system" / "note.md"
    loose.write_text("no type derivable here\n")
    stamped, reported = stamp.stamp_types(tmp_path)
    assert stamped == []
    assert sorted(reported) == ["inbox/broken.md", "system/note.md"]
    assert bad.read_text().startswith("---\nnot: [closed")  # untouched


def test_idempotent(tmp_path):
    (tmp_path / "inbox").mkdir(parents=True)
    (tmp_path / "inbox" / "idea.md").write_text("thought\n")
    stamp.stamp_types(tmp_path)
    stamped, _ = stamp.stamp_types(tmp_path)
    assert stamped == []
