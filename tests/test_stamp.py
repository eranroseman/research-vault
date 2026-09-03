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
    bad.write_text("---\n  bad: nested\n---\ntext\n")
    loose = tmp_path / "system" / "note.md"
    loose.write_text("no type derivable here\n")
    stamped, reported = stamp.stamp_types(tmp_path)
    assert stamped == []
    assert sorted(reported) == [
        ("inbox/broken.md", "unparseable"),
        ("system/note.md", "no-type"),
    ]
    assert bad.read_text().startswith("---\n  bad: nested")  # untouched


def test_reports_duplicate_key_frontmatter_instead_of_collapsing(tmp_path):
    (tmp_path / "literatures").mkdir(parents=True)
    note = tmp_path / "literatures" / "x.md"
    original = '---\ntags: "a"\ntags: "b"\n---\nbody\n'
    note.write_text(original)
    stamped, reported = stamp.stamp_types(tmp_path)
    assert stamped == []
    assert reported == [("literatures/x.md", "unparseable")]
    assert note.read_text() == original  # untouched — no data loss


def test_refuses_to_write_through_symlinked_md(tmp_path):
    """A `.md` inside the vault that's actually a symlink to a file OUTSIDE
    the vault must not get its target rewritten — reported, not edited."""
    vault = tmp_path / "vault"
    (vault / "inbox").mkdir(parents=True)
    outside = tmp_path / "outside-target.md"
    outside.write_text("untouched outside content\n")
    link = vault / "inbox" / "linked.md"
    link.symlink_to(outside)
    stamped, reported = stamp.stamp_types(vault)
    assert stamped == []
    assert reported == [("inbox/linked.md", "symlink")]
    assert outside.read_text() == "untouched outside content\n"


def test_preserves_crlf_for_bare_capture(tmp_path):
    (tmp_path / "inbox").mkdir(parents=True)
    note = tmp_path / "inbox" / "idea.md"
    note.write_bytes(b"a half thought\r\nsecond line\r\n")
    stamped, _ = stamp.stamp_types(tmp_path)
    assert stamped == ["inbox/idea.md"]
    raw = note.read_bytes()
    assert b"\n" not in raw.replace(b"\r\n", b"")  # every \n is part of \r\n
    assert raw == (
        b'---\r\ntype: "fleeting"\r\n---\r\na half thought\r\nsecond line\r\n'
    )


def test_preserves_crlf_for_insert_as_first_key(tmp_path):
    (tmp_path / "literatures").mkdir(parents=True)
    note = tmp_path / "literatures" / "x.md"
    note.write_bytes(b'---\r\ncitekey: "x"\r\n---\r\nbody text\r\n')
    stamped, _ = stamp.stamp_types(tmp_path)
    assert stamped == ["literatures/x.md"]
    raw = note.read_bytes()
    assert b"\n" not in raw.replace(b"\r\n", b"")  # every \n is part of \r\n
    data, _ = frontmatter.parse(raw.decode("utf-8"))
    assert data["type"] == "literature"
    assert data["citekey"] == "x"
    assert raw.endswith(b"---\r\nbody text\r\n")


def test_idempotent(tmp_path):
    (tmp_path / "inbox").mkdir(parents=True)
    (tmp_path / "inbox" / "idea.md").write_text("thought\n")
    stamp.stamp_types(tmp_path)
    stamped, _ = stamp.stamp_types(tmp_path)
    assert stamped == []
