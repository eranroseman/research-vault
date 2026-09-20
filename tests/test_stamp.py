import os

import pytest

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


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads everything")
def test_an_unreadable_or_undecodable_file_is_reported_not_stamped(tmp_path, capsys):
    from research_vault.__main__ import main

    (tmp_path / "inbox").mkdir(parents=True)
    bad = tmp_path / "inbox" / "bad.md"
    bad.write_bytes(b"\xff\xfe")
    (tmp_path / "projects" / "p").mkdir(parents=True)
    later = tmp_path / "projects" / "p" / "draft.md"
    later.write_text("the draft\n")
    # "inbox" sorts before "projects": each bad-read case below must still
    # `continue` on to stamp this later note, not `break` the whole walk.
    assert stamp.stamp_types(tmp_path) == (
        ["projects/p/draft.md"],
        [("inbox/bad.md", "not-utf-8")],
    )
    assert bad.read_bytes() == b"\xff\xfe"
    assert main(["stamp-type", "--vault", str(tmp_path)]) == 0
    assert "skipped inbox/bad.md — file is not UTF-8" in capsys.readouterr().out
    later.write_text("the draft\n")  # stamp_types above already stamped it once
    bad.write_text("x\n")
    bad.chmod(0)
    try:
        assert stamp.stamp_types(tmp_path) == (
            ["projects/p/draft.md"],
            [("inbox/bad.md", "outage")],
        )
        assert main(["stamp-type", "--vault", str(tmp_path)]) == 0
        assert (
            "skipped inbox/bad.md — file could not be read" in capsys.readouterr().out
        )
    finally:
        bad.chmod(0o644)


def test_a_real_file_under_a_symlinked_ancestor_is_reported_outside(tmp_path):
    """#107: with explicit paths only the leaf's is_symlink() was checked, so
    a file inside a symlinked directory was rewritten outside the vault."""
    vault = tmp_path / "vault"
    (vault / "inbox").mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    target = outside / "idea.md"
    target.write_text("a thought\n")
    (vault / "inbox" / "link").symlink_to(outside, target_is_directory=True)

    stamped, reported = stamp.stamp_types(vault, paths=["inbox/link/idea.md"])

    assert (stamped, reported) == ([], [("inbox/link/idea.md", "outside")])
    assert target.read_text() == "a thought\n"


def test_an_absolute_outside_path_and_a_dot_dot_path_are_reported_outside(tmp_path):
    vault = tmp_path / "vault"
    (vault / "inbox").mkdir(parents=True)
    elsewhere = tmp_path / "elsewhere.md"
    elsewhere.write_text("not yours\n")

    stamped, reported = stamp.stamp_types(
        vault, paths=[str(elsewhere), "inbox/../../elsewhere.md"]
    )

    assert stamped == []
    assert reported == sorted(
        [(str(elsewhere), "outside"), ("inbox/../../elsewhere.md", "outside")]
    )
    assert elsewhere.read_text() == "not yours\n"


def test_the_reported_string_stays_the_unresolved_one(tmp_path):
    """`test_stamp.py`'s explicit-paths pin: the person's spelling is what
    the report names, resolved only for the containment decision."""
    vault = tmp_path / "vault"
    (vault / "inbox").mkdir(parents=True)
    (vault / "inbox" / "idea.md").write_text("a thought\n")
    stamped, reported = stamp.stamp_types(vault, paths=["inbox/./idea.md"])
    assert (stamped, reported) == (["inbox/idea.md"], [])
