import os
import subprocess

from research_vault import fixer, okf


def _git(vault, *args, env=None):
    return subprocess.run(
        ["git", *args], cwd=vault, check=True, capture_output=True, text=True, env=env
    ).stdout


def _page(vault, relative, text):
    path = vault / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_fix_stamps_normalises_and_regenerates_the_log_in_one_pass(tmp_vault):
    _page(tmp_vault, "wiki/concepts/Only Here.md", "---\ntype: concept\n---\n")
    draft = _page(
        tmp_vault, "projects/brief/draft.md", "See [[Only Here]] and [[nowhere]].\n"
    )
    day = _page(
        tmp_vault,
        "log/2026-10-24.md",
        '---\ntype: "log"\n---\n- 09:00 research_vault/0.1.0 — captured smith2020\n',
    )
    report = fixer.fix(tmp_vault)
    assert report.stamped == ["projects/brief/draft.md"]
    assert report.normalised == ["projects/brief/draft.md"]
    assert report.log_regenerated is True
    assert report.changed == ["projects/brief/draft.md", "log.md"]
    assert [(relative, p.kind, p.target) for relative, p in report.problems] == [
        ("projects/brief/draft.md", "dead", "nowhere")
    ]
    assert draft.read_text() == (
        '---\ntype: "project"\n---\nSee [Only Here](/wiki/concepts/Only%20Here.md) and [[nowhere]].\n'
    )
    assert (tmp_vault / "log.md").read_text() == okf.render_log(tmp_vault)
    assert "captured smith2020" in (tmp_vault / "log.md").read_text()
    assert day.read_text().endswith("captured smith2020\n")  # log/ is never normalised
    again = fixer.fix(tmp_vault)
    assert again.changed == []


def test_fix_with_paths_touches_only_those_paths_and_the_log(tmp_vault):
    _page(tmp_vault, "inbox/a.md", "a thought\n")
    _page(tmp_vault, "inbox/b.md", "another\n")
    report = fixer.fix(tmp_vault, paths=["inbox/a.md"])
    assert report.stamped == ["inbox/a.md"]
    assert (tmp_vault / "inbox" / "b.md").read_text() == "another\n"
    assert (
        report.log_regenerated is False
    )  # no log.md and no day file: nothing to render


def test_fix_leaves_the_skipped_surfaces_alone(tmp_vault):
    """§5.2: literature/, log/, log.md, the review queue, the propagation
    records, wiki/ and fulltext/ are never normalised."""
    _page(tmp_vault, "wiki/concepts/Only Here.md", "---\ntype: concept\n---\n")
    page = _page(
        tmp_vault, "wiki/sources/A.md", "---\ntype: source\n---\n[[Only Here]]\n"
    )
    note = _page(
        tmp_vault,
        "literature/x.md",
        '---\ntype: "literature"\n---\n[[Only Here]]\n',
    )
    report = fixer.fix(tmp_vault)
    assert report.normalised == []
    assert "[[Only Here]]" in page.read_text()
    assert "[[Only Here]]" in note.read_text()


def test_fix_reports_an_unwritable_file_and_continues(tmp_vault, monkeypatch):
    """#174: an OSError on write is a `unwritable` report, not a traceback."""
    from research_vault import stamp

    _page(tmp_vault, "inbox/a.md", "a thought\n")
    _page(tmp_vault, "inbox/b.md", "b thought\n")
    real = stamp._write_text

    def failing(path, text):
        if path.name == "a.md":
            raise OSError(30, "Read-only file system")
        real(path, text)

    monkeypatch.setattr(stamp, "_write_text", failing)
    report = fixer.fix(tmp_vault)
    assert report.stamped == ["inbox/b.md"]
    assert ("inbox/a.md", "unwritable") in report.reported


def test_fix_leaves_a_staged_non_note_alone_and_unreported(tmp_vault):
    """P-6a: a listed path is a note only if it ends in `.md` and no walker
    excludes it. A staged canvas under inbox/, a `.gitkeep` sentinel and a
    plugin's README under `.obsidian/` are neither stamped nor normalised."""
    _page(tmp_vault, "wiki/concepts/Only Here.md", "---\ntype: concept\n---\n")
    files = {
        "inbox/x.canvas": '{"nodes":[],"edges":[]}\n',
        "literature/.gitkeep": "",
        ".obsidian/p/README.md": "See [[Only Here]].\n",
    }
    for relative, text in files.items():
        _page(tmp_vault, relative, text)
    _git(tmp_vault, "add", "-f", *files)
    staged, partial = fixer.staged_paths(tmp_vault)
    assert sorted(staged) == sorted(files)
    assert partial == []
    report = fixer.fix(tmp_vault, staged)
    assert (report.stamped, report.normalised, report.reported, report.problems) == (
        [],
        [],
        [],
        [],
    )
    for relative, text in files.items():
        assert (tmp_vault / relative).read_text() == text, relative


def test_fix_reports_an_unterminated_frontmatter_block_once(tmp_vault):
    """Stamp reports the block `unparseable`; the normaliser leaves the note
    alone rather than add a second line for the same fault."""
    note = _page(tmp_vault, "inbox/broken.md", "---\nsee: x\n[[nowhere]]\n")
    report = fixer.fix(tmp_vault, paths=["inbox/broken.md"])
    assert report.reported == [("inbox/broken.md", "unparseable")]
    assert report.problems == []
    assert note.read_text() == "---\nsee: x\n[[nowhere]]\n"


def test_an_index_under_a_symlinked_ancestor_is_reported_outside(tmp_path):
    """#107: stamp skips every `index.md` before its containment check, so
    the normaliser makes its own and never writes through to outside."""
    vault = tmp_path / "vault"
    _page(vault, "wiki/concepts/Only Here.md", "---\ntype: concept\n---\n")
    outside = tmp_path / "outside"
    target = _page(outside, "index.md", "See [[Only Here]].\n")
    (vault / "inbox").mkdir()
    (vault / "inbox" / "link").symlink_to(outside, target_is_directory=True)
    report = fixer.fix(vault, paths=["inbox/link/index.md"])
    assert report.normalised == []
    assert report.reported == [("inbox/link/index.md", "outside")]
    assert target.read_text() == "See [[Only Here]].\n"


def test_staged_paths_splits_fully_from_partially_staged(tmp_vault):
    _git(tmp_vault, "init", "-q")
    _page(tmp_vault, "inbox/full.md", "a\n")
    _page(tmp_vault, "inbox/partial.md", "a\n")
    _git(tmp_vault, "add", "inbox/full.md", "inbox/partial.md")
    (tmp_vault / "inbox" / "partial.md").write_text("a\nb\n")
    assert fixer.staged_paths(tmp_vault) == (["inbox/full.md"], ["inbox/partial.md"])


def test_staged_paths_reads_the_index_git_names(tmp_vault, tmp_path):
    """Under `git commit -- <paths>` the hook runs against a temporary index named
    by GIT_INDEX_FILE; the two git reads must both honour it."""
    _git(tmp_vault, "init", "-q")
    _page(tmp_vault, "inbox/a.md", "a\n")
    private = tmp_path / "private-index"
    env = {**os.environ, "GIT_INDEX_FILE": str(private)}
    _git(tmp_vault, "add", "inbox/a.md", env=env)
    with_private = fixer.staged_paths(tmp_vault, env=env)
    assert with_private == (["inbox/a.md"], [])
    assert fixer.staged_paths(tmp_vault) == ([], [])


def test_an_unreadable_index_is_reported_by_the_normaliser(tmp_vault, monkeypatch):
    """Stamp skips every `index.md` before reading it, so a normalised-surface
    index the normaliser cannot read is reported by it, under stamp's words."""
    from research_vault import stamp

    (tmp_vault / "index.md").write_text("[[Only Here]]\n")
    _page(tmp_vault, "projects/brief/index.md", "")
    (tmp_vault / "projects" / "brief" / "index.md").write_bytes(b"\xff [[x]]\n")
    real = stamp._read_text

    def failing(path):
        if path == tmp_vault / "index.md":
            raise OSError(5, "Input/output error")
        return real(path)

    monkeypatch.setattr(stamp, "_read_text", failing)
    report = fixer.fix(tmp_vault, paths=["index.md", "projects/brief/index.md"])
    assert report.reported == [
        ("index.md", "outage"),
        ("projects/brief/index.md", "not-utf-8"),
    ]
    assert report.normalised == []


def test_a_staged_move_out_of_the_inbox_is_stamped(tmp_vault):
    """A rename is listed under its new path (`--no-renames`): moving a
    typeless capture out of `inbox/` is the ordinary triage act."""
    _page(tmp_vault, "inbox/x.md", "a thought worth keeping\n")
    _git(tmp_vault, "add", "inbox/x.md")
    _git(tmp_vault, "commit", "-qm", "capture")
    (tmp_vault / "daily").mkdir(exist_ok=True)
    _git(tmp_vault, "mv", "inbox/x.md", "daily/x.md")
    staged, partial = fixer.staged_paths(tmp_vault)
    assert (staged, partial) == (["daily/x.md"], [])
    report = fixer.fix(tmp_vault, staged)
    assert report.stamped == ["daily/x.md"]
    assert (tmp_vault / "daily" / "x.md").read_text() == (
        '---\ntype: "daily"\n---\na thought worth keeping\n'
    )


def test_a_staged_file_moved_in_the_worktree_is_partially_staged(tmp_vault):
    """The worktree read pairs no renames either: a staged note moved to an
    intent-to-add path is listed under its own name as partially staged."""
    _page(tmp_vault, "inbox/x.md", "a thought worth keeping\n")
    _git(tmp_vault, "add", "inbox/x.md")
    (tmp_vault / "inbox" / "x.md").rename(tmp_vault / "inbox" / "y.md")
    _git(tmp_vault, "add", "-N", "inbox/y.md")
    assert fixer.staged_paths(tmp_vault) == ([], ["inbox/x.md"])


def test_an_unwritable_root_log_is_reported_not_raised(tmp_vault, monkeypatch):
    """#174 for the fixer's own write: `log.md` is reported unwritable and
    is not counted as regenerated."""
    _page(
        tmp_vault,
        "log/2026-10-24.md",
        '---\ntype: "log"\n---\n- 09:00 research_vault/0.1.0 — captured x\n',
    )

    def failing(_vault, _text):
        raise OSError(30, "Read-only file system")

    monkeypatch.setattr(okf, "write_log", failing)
    report = fixer.fix(tmp_vault, paths=[])
    assert report.log_regenerated is False
    assert report.reported == [("log.md", "unwritable")]
    assert not (tmp_vault / "log.md").exists()


def test_a_listed_path_outside_the_vault_reaches_stamp_and_an_excluded_one_does_not(
    tmp_path,
):
    """P-6a's filter judges exclusion lexically under the vault: a `..` that
    leaves it and an absolute path elsewhere are kept, so stamp reports them
    `outside`; `inbox/../.obsidian/x.md` is under `.obsidian/` and dropped."""
    vault = tmp_path / "vault"
    (vault / "inbox").mkdir(parents=True)
    escaped = _page(tmp_path, "x.md", "a thought\n")
    elsewhere = _page(tmp_path, "y.md", "a thought\n")
    plugin = _page(vault, ".obsidian/x.md", "a thought\n")
    report = fixer.fix(
        vault, paths=["inbox/../../x.md", str(elsewhere), "inbox/../.obsidian/x.md"]
    )
    assert report.stamped == []
    assert report.reported == sorted(
        [("inbox/../../x.md", "outside"), (str(elsewhere), "outside")]
    )
    for path in (escaped, elsewhere, plugin):
        assert path.read_text() == "a thought\n", path


def test_fix_with_no_paths_touches_only_the_root_log(tmp_vault):
    """`paths=[]` (Task 8's call) regenerates root `log.md` and nothing else."""
    _page(tmp_vault, "wiki/concepts/Only Here.md", "---\ntype: concept\n---\n")
    note = _page(tmp_vault, "inbox/a.md", "a thought\n")
    draft = _page(tmp_vault, "projects/brief/draft.md", "See [[Only Here]].\n")
    _page(
        tmp_vault,
        "log/2026-10-24.md",
        '---\ntype: "log"\n---\n- 09:00 research_vault/0.1.0 — captured x\n',
    )
    report = fixer.fix(tmp_vault, paths=[])
    assert report.changed == ["log.md"]
    assert (report.reported, report.problems) == ([], [])
    assert note.read_text() == "a thought\n"
    assert draft.read_text() == "See [[Only Here]].\n"
    assert (tmp_vault / "log.md").read_text() == okf.render_log(tmp_vault)
