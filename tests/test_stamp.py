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
    (tmp_path / "literature").mkdir(parents=True)
    note = tmp_path / "literature" / "x.md"
    note.write_text('---\ncitationKey: "x"\n---\nbody\n')
    stamped, _ = stamp.stamp_types(tmp_path)
    assert stamped == ["literature/x.md"]
    data, _ = frontmatter.parse(note.read_text())
    assert data["type"] == "literature"
    assert data["citationKey"] == "x"


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
    (tmp_path / "literature").mkdir(parents=True)
    note = tmp_path / "literature" / "x.md"
    original = '---\ntags: "a"\ntags: "b"\n---\nbody\n'
    note.write_text(original)
    stamped, reported = stamp.stamp_types(tmp_path)
    assert stamped == []
    assert reported == [("literature/x.md", "unparseable")]
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
    (tmp_path / "literature").mkdir(parents=True)
    note = tmp_path / "literature" / "x.md"
    note.write_bytes(b'---\r\ncitationKey: "x"\r\n---\r\nbody text\r\n')
    stamped, _ = stamp.stamp_types(tmp_path)
    assert stamped == ["literature/x.md"]
    raw = note.read_bytes()
    assert b"\n" not in raw.replace(b"\r\n", b"")  # every \n is part of \r\n
    data, _ = frontmatter.parse(raw.decode("utf-8"))
    assert data["type"] == "literature"
    assert data["citationKey"] == "x"
    assert raw.endswith(b"---\r\nbody text\r\n")


def test_idempotent(tmp_path):
    (tmp_path / "inbox").mkdir(parents=True)
    (tmp_path / "inbox" / "idea.md").write_text("thought\n")
    stamp.stamp_types(tmp_path)
    stamped, _ = stamp.stamp_types(tmp_path)
    assert stamped == []


# --- boundaries pinned against mutation survivors -----------------------------


def test_every_skip_is_a_pass_over_not_the_end_of_the_walk(tmp_path):
    """In walk order, before the one stampable note: a note under an excluded
    directory, a note no type is derivable for, a directory named like a note,
    a symlink, an unparseable note, a duplicate-key note, an already-typed
    note, the root index.md and log.md. Each is skipped or reported on its
    own, and the project note sorted after all of them is still stamped."""
    (tmp_path / ".raw").mkdir()
    (tmp_path / ".raw" / "a.md").write_text("raw\n")
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "a-dir.md").mkdir()
    (inbox / "b-link.md").symlink_to(tmp_path / "nowhere.md")
    (inbox / "c-bad.md").write_text("---\n  bad: nested\n---\ntext\n")
    (tmp_path / "literature").mkdir()
    (tmp_path / "literature" / "dup.md").write_text(
        '---\ntags: "a"\ntags: "b"\n---\ntext\n'
    )
    (inbox / "d-typed.md").write_text('---\ntype: "fleeting"\n---\ntext\n')
    (tmp_path / "index.md").write_text("root index\n")
    (tmp_path / "log.md").write_text("log\n")
    (tmp_path / "a-loose").mkdir()
    (tmp_path / "a-loose" / "e-notype.md").write_text("loose\n")
    (tmp_path / "projects" / "p").mkdir(parents=True)
    (tmp_path / "projects" / "p" / "draft.md").write_text("the draft\n")

    stamped, reported = stamp.stamp_types(tmp_path)

    assert stamped == ["projects/p/draft.md"]
    assert reported == [
        ("a-loose/e-notype.md", "no-type"),
        ("inbox/b-link.md", "symlink"),
        ("inbox/c-bad.md", "unparseable"),
        ("literature/dup.md", "unparseable"),
    ]
    assert (tmp_path / "index.md").read_text() == "root index\n"
    assert (tmp_path / "log.md").read_text() == "log\n"
    assert (inbox / "d-typed.md").read_text() == '---\ntype: "fleeting"\n---\ntext\n'
    data, _body = frontmatter.parse(
        (tmp_path / "projects" / "p" / "draft.md").read_text()
    )
    assert data == {"type": "project"}


def test_explicit_paths_skip_git_and_index_but_stamp_the_rest(tmp_path):
    """Named paths, relative or absolute: anything under .git and index.md are
    passed over; the named note is stamped and nothing else is walked."""
    (tmp_path / ".git" / "hooks").mkdir(parents=True)
    (tmp_path / ".git" / "hooks" / "note.md").write_text("hook\n")
    (tmp_path / "inbox").mkdir()
    (tmp_path / "inbox" / "index.md").write_text("an index\n")
    (tmp_path / "inbox" / "idea.md").write_text("thought\n")
    (tmp_path / "inbox" / "other.md").write_text("not named\n")

    stamped, reported = stamp.stamp_types(
        tmp_path,
        paths=[
            ".git/hooks/note.md",
            "inbox/index.md",
            str(tmp_path / "inbox" / "idea.md"),
        ],
    )

    assert (stamped, reported) == (["inbox/idea.md"], [])
    assert (tmp_path / ".git" / "hooks" / "note.md").read_text() == "hook\n"
    assert (tmp_path / "inbox" / "index.md").read_text() == "an index\n"
    assert (tmp_path / "inbox" / "other.md").read_text() == "not named\n"
