import builtins
import os
import stat
import subprocess

import pytest

from research_vault import gitstate


def test_revision_paths_and_blob_bytes_preserve_an_arbitrary_revision(tmp_vault):
    path = tmp_vault / "wiki" / "concepts" / "deleted.md"
    path.write_bytes(b"claim \xff\n")
    subprocess.run(
        ["git", "add", "wiki/concepts/deleted.md"], cwd=tmp_vault, check=True
    )
    subprocess.run(
        ["git", "commit", "-q", "-m", "binary claim"],
        cwd=tmp_vault,
        check=True,
    )
    subprocess.run(["git", "tag", "snapshot"], cwd=tmp_vault, check=True)
    path.write_bytes(b"replacement\n")
    subprocess.run(
        ["git", "add", "wiki/concepts/deleted.md"], cwd=tmp_vault, check=True
    )
    subprocess.run(
        ["git", "commit", "-q", "-m", "replace claim"],
        cwd=tmp_vault,
        check=True,
    )
    path.unlink()

    assert gitstate.revision_paths(tmp_vault, "snapshot", "wiki/concepts") == {
        b"wiki/concepts/deleted.md"
    }
    assert (
        gitstate.blob_bytes(tmp_vault, "snapshot", "wiki/concepts/deleted.md")
        == b"claim \xff\n"
    )
    assert (
        gitstate.blob_bytes(tmp_vault, "HEAD", "wiki/concepts/deleted.md")
        == b"replacement\n"
    )
    assert (
        gitstate.blob_bytes(tmp_vault, "snapshot", "wiki/concepts/missing.md") is None
    )


def test_blob_bytes_distinguishes_an_empty_blob_from_a_missing_blob(tmp_vault):
    path = tmp_vault / "wiki" / "concepts" / "empty.md"
    path.write_bytes(b"")
    subprocess.run(["git", "add", "wiki/concepts/empty.md"], cwd=tmp_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "empty claim"],
        cwd=tmp_vault,
        check=True,
    )

    assert gitstate.blob_bytes(tmp_vault, "HEAD", "wiki/concepts/empty.md") == b""
    assert gitstate.blob_bytes(tmp_vault, "HEAD", "wiki/concepts/absent.md") is None


def _git(vault, *args, stdin=None, check=True):
    return subprocess.run(
        ["git", *args], cwd=vault, input=stdin, capture_output=True, check=check
    )


def _commit(vault, message="baseline"):
    _git(vault, "add", "-A")
    _git(vault, "commit", "-q", "-m", message)
    return _git(vault, "rev-parse", "HEAD").stdout.decode().strip()


def test_snapshot_resolution_separates_base_expected_head_index_and_live(tmp_vault):
    path = tmp_vault / "wiki" / "concepts" / "note.md"
    path.write_bytes(b"base\n")
    parent = _commit(tmp_vault)
    path.write_bytes(b"staged\n")
    _git(tmp_vault, "add", "wiki/concepts/note.md")
    path.write_bytes(b"unstaged scratch\n")
    index_before = (tmp_vault / ".git" / "index").read_bytes()

    snapshots = gitstate.resolve_snapshots(
        tmp_vault, git_base=parent, candidate="index"
    )

    assert (
        snapshots.base_tree
        == _git(tmp_vault, "rev-parse", f"{parent}^{{tree}}").stdout.decode().strip()
    )
    assert snapshots.expected_head == parent
    assert snapshots.candidate.image(b"wiki/concepts/note.md").data == b"staged\n"
    assert snapshots.live.image(b"wiki/concepts/note.md").data == b"unstaged scratch\n"
    assert (tmp_vault / ".git" / "index").read_bytes() == index_before
    assert _git(tmp_vault, "rev-parse", "HEAD").stdout.decode().strip() == parent


def test_unborn_defaults_to_stored_empty_tree_and_index_candidate(tmp_vault):
    (tmp_vault / "literature" / "first.md").write_bytes(b"first\n")
    _git(tmp_vault, "add", "literature/first.md")
    index_before = (tmp_vault / ".git" / "index").read_bytes()

    snapshots = gitstate.resolve_snapshots(tmp_vault, candidate="index")

    assert snapshots.expected_head is None
    assert (
        _git(
            tmp_vault, "cat-file", "-e", f"{snapshots.base_tree}^{{tree}}", check=False
        ).returncode
        == 0
    )
    assert snapshots.candidate.image(b"literature/first.md").data == b"first\n"
    assert (tmp_vault / ".git" / "index").read_bytes() == index_before


def test_corrupt_head_is_not_silently_treated_as_an_unborn_branch(tmp_vault):
    head = tmp_vault / ".git" / "HEAD"
    head.write_text("not-an-object\n")
    before = gitstate.snapshot_worktree(tmp_vault)

    with pytest.raises(gitstate.GitStateError, match="HEAD"):
        gitstate.resolve_snapshots(tmp_vault, candidate="worktree")

    assert gitstate.snapshot_worktree(tmp_vault) == before


def test_snapshot_rejects_same_inode_rewrite_during_read(tmp_vault, monkeypatch):
    path = tmp_vault / "wiki" / "concepts" / "changing.md"
    path.write_bytes(b"before\n")
    raw_path = b"wiki/concepts/changing.md"
    before = os.lstat(path)
    real_open = builtins.open

    class RacingReader:
        def __init__(self, stream):
            self._stream = stream

        def __enter__(self):
            self._stream.__enter__()
            return self

        def __exit__(self, *args):
            return self._stream.__exit__(*args)

        def fileno(self):
            return self._stream.fileno()

        def read(self):
            data = self._stream.read()
            with real_open(path, "r+b") as writer:
                writer.write(b"changed\n")
                writer.flush()
                os.fsync(writer.fileno())
            return data

    def racing_open(name, mode="r", *args, **kwargs):
        stream = real_open(name, mode, *args, **kwargs)
        if os.fsencode(name) == os.fsencode(path) and mode == "rb":
            return RacingReader(stream)
        return stream

    monkeypatch.setattr(builtins, "open", racing_open)
    with pytest.raises(gitstate.GitStateError, match="changed while snapshotting"):
        gitstate._normalized_live_image(os.fsencode(tmp_vault), raw_path, before)

    assert os.lstat(path).st_ino == before.st_ino


@pytest.mark.parametrize("revision", ["missing", "HEAD:no-such-path", "HEAD^{blob}"])
def test_bad_explicit_base_is_operational_error_before_snapshot(tmp_vault, revision):
    (tmp_vault / "index.md").write_bytes(b"base\n")
    _commit(tmp_vault)
    with pytest.raises(gitstate.GitStateError, match="base"):
        gitstate.resolve_snapshots(tmp_vault, git_base=revision, candidate="HEAD")


def test_tree_snapshot_preserves_raw_nul_paths_and_rename_identity(tmp_vault):
    root = os.fsencode(tmp_vault)
    old = b"wiki/concepts/old\xff\nname.md"
    old_abs = os.path.join(root, old)
    os.makedirs(os.path.dirname(old_abs), exist_ok=True)
    with open(old_abs, "wb") as stream:
        stream.write(b"raw\n")
    _git(tmp_vault, "add", "--", old)
    first = _commit(tmp_vault)
    new = b"wiki/concepts/new\xfe\nname.md"
    os.rename(old_abs, os.path.join(root, new))
    _git(tmp_vault, "add", "-A")
    second = _commit(tmp_vault, "rename")

    before = gitstate.snapshot_tree(tmp_vault, f"{first}^{{tree}}")
    after = gitstate.snapshot_tree(tmp_vault, f"{second}^{{tree}}")
    assert before.image(old).data == b"raw\n"
    assert after.image(new).data == b"raw\n"
    assert old not in after.images
    assert new not in before.images


def test_planning_materialization_never_exposes_a_candidate_symlink_target(
    tmp_vault, tmp_path
):
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.write_bytes(b"mutable outside\n")
    link = tmp_vault / "wiki" / "concepts" / "outside.md"
    link.symlink_to(outside)
    candidate = gitstate.snapshot_worktree(tmp_vault)
    planning = tmp_path / "planning"

    gitstate.materialize_snapshot(candidate, planning)
    captured = gitstate.snapshot_worktree(planning)
    restored = gitstate.restore_candidate_nonfiles(candidate, captured)

    assert not (planning / "wiki" / "concepts" / "outside.md").exists()
    assert restored.image(b"wiki/concepts/outside.md") == candidate.image(
        b"wiki/concepts/outside.md"
    )
    assert gitstate.outputs_between(candidate, restored) == ()


def test_publish_outputs_uses_exact_captured_blobs_and_leaves_live_index_unchanged(
    tmp_vault,
):
    target = tmp_vault / "wiki" / "concepts" / "out.md"
    target.write_bytes(b"base\n")
    unrelated = tmp_vault / "projects" / "scratch.md"
    unrelated.write_bytes(b"base scratch\n")
    parent = _commit(tmp_vault)
    unrelated.write_bytes(b"staged scratch\n")
    _git(tmp_vault, "add", "projects/scratch.md")
    unrelated.write_bytes(b"unstaged scratch\n")
    untracked = tmp_vault / "untracked.txt"
    untracked.write_bytes(b"untracked\n")
    index_before = (tmp_vault / ".git" / "index").read_bytes()
    snapshots = gitstate.resolve_snapshots(tmp_vault, candidate="worktree")
    captured = gitstate.CapturedOutput(
        b"wiki/concepts/out.md", stat.S_IFREG | 0o644, b"captured\n"
    )
    target.write_bytes(b"later rewrite\n")

    commit = gitstate.publish_outputs(
        tmp_vault, snapshots, [captured], "snapshot projection"
    )

    assert _git(tmp_vault, "rev-parse", "HEAD^").stdout.decode().strip() == parent
    assert _git(tmp_vault, "show", "HEAD:wiki/concepts/out.md").stdout == b"captured\n"
    assert (
        _git(tmp_vault, "show", "HEAD:projects/scratch.md").stdout == b"base scratch\n"
    )
    assert target.read_bytes() == b"later rewrite\n"
    assert unrelated.read_bytes() == b"unstaged scratch\n"
    assert untracked.read_bytes() == b"untracked\n"
    assert (tmp_vault / ".git" / "index").read_bytes() == index_before
    assert commit == _git(tmp_vault, "rev-parse", "HEAD").stdout.decode().strip()


def test_publish_outputs_loses_concurrent_head_cas_without_touching_index(
    tmp_vault, monkeypatch
):
    path = tmp_vault / "wiki" / "concepts" / "out.md"
    path.write_bytes(b"base\n")
    expected = _commit(tmp_vault)
    snapshots = gitstate.resolve_snapshots(tmp_vault, candidate="worktree")
    index_before = (tmp_vault / ".git" / "index").read_bytes()
    real_git = gitstate._git

    def race(vault, *args, **kwargs):
        if args[:2] == ("update-ref", "HEAD"):
            tree = _git(tmp_vault, "rev-parse", f"{expected}^{{tree}}").stdout.strip()
            raced = (
                _git(
                    tmp_vault,
                    "commit-tree",
                    tree,
                    "-p",
                    expected,
                    stdin=b"human commit\n",
                )
                .stdout.decode()
                .strip()
            )
            _git(tmp_vault, "update-ref", "HEAD", raced, expected)
        return real_git(vault, *args, **kwargs)

    monkeypatch.setattr(gitstate, "_git", race)
    with pytest.raises(gitstate.GitStateError, match=r"concurrent|update-ref"):
        gitstate.publish_outputs(
            tmp_vault,
            snapshots,
            [
                gitstate.CapturedOutput(
                    b"wiki/concepts/out.md", stat.S_IFREG | 0o644, b"captured\n"
                )
            ],
            "snapshot projection",
        )

    assert _git(tmp_vault, "rev-parse", "HEAD^").stdout.decode().strip() == expected
    assert (tmp_vault / ".git" / "index").read_bytes() == index_before


def test_empty_publication_is_a_noop(tmp_vault, monkeypatch):
    (tmp_vault / "index.md").write_bytes(b"base\n")
    head = _commit(tmp_vault)
    snapshots = gitstate.resolve_snapshots(tmp_vault, candidate="worktree")
    called = []
    monkeypatch.setattr(gitstate, "_git", lambda *_a, **_k: called.append(_a))

    assert gitstate.publish_outputs(tmp_vault, snapshots, [], "unused") is None
    assert called == []
    assert _git(tmp_vault, "rev-parse", "HEAD").stdout.decode().strip() == head


@pytest.mark.parametrize(
    "stage",
    [
        "hash-object",
        "mkstemp",
        "read-tree",
        "update-index",
        "write-tree",
        "commit-tree",
        "update-ref",
    ],
)
def test_each_publication_stage_failure_preserves_head_index_and_captured_source(
    tmp_vault, monkeypatch, stage
):
    target = tmp_vault / "wiki" / "concepts" / "out.md"
    target.write_bytes(b"base\n")
    expected_head = _commit(tmp_vault)
    snapshots = gitstate.resolve_snapshots(tmp_vault, candidate="worktree")
    index_before = (tmp_vault / ".git" / "index").read_bytes()
    captured = gitstate.CapturedOutput(
        b"wiki/concepts/out.md", stat.S_IFREG | 0o644, b"captured\n"
    )
    target.write_bytes(b"reread bytes\n")
    real_git = gitstate._git
    calls = []
    commits = []

    def fail_stage(vault, *args, **kwargs):
        calls.append((args, kwargs.get("stdin")))
        command = args[0]
        if command == stage:
            if stage == "update-ref":
                return subprocess.CompletedProcess(args, 1, b"", b"injected failure")
            raise gitstate.GitStateError(f"injected {stage} failure")
        result = real_git(vault, *args, **kwargs)
        if command == "commit-tree":
            commits.append(result.stdout.decode().strip())
        return result

    monkeypatch.setattr(gitstate, "_git", fail_stage)
    if stage == "mkstemp":
        monkeypatch.setattr(
            gitstate.tempfile,
            "mkstemp",
            lambda **_kwargs: (_ for _ in ()).throw(
                OSError("injected mkstemp failure")
            ),
        )

    with pytest.raises(gitstate.GitStateError):
        gitstate.publish_outputs(
            tmp_vault, snapshots, [captured], "snapshot projection"
        )

    assert _git(tmp_vault, "rev-parse", "HEAD").stdout.decode().strip() == expected_head
    assert (tmp_vault / ".git" / "index").read_bytes() == index_before
    assert target.read_bytes() == b"reread bytes\n"
    hash_inputs = [stdin for args, stdin in calls if args[0] == "hash-object"]
    assert hash_inputs == [b"captured\n"]
    assert b"reread bytes\n" not in hash_inputs
    assert len(commits) == (1 if stage == "update-ref" else 0)
    for commit in commits:
        assert (
            _git(tmp_vault, "show", f"{commit}:wiki/concepts/out.md").stdout
            == b"captured\n"
        )


def test_projection_refuses_preimage_divergence_before_first_write(tmp_vault):
    first = tmp_vault / "wiki" / "concepts" / "a.md"
    second = tmp_vault / "projects" / "b.md"
    first.write_bytes(b"one\n")
    second.write_bytes(b"two\n")
    before = gitstate.snapshot_worktree(tmp_vault)
    second.write_bytes(b"human rewrite\n")
    outputs = [
        gitstate.CapturedOutput(b"projects/b.md", stat.S_IFREG | 0o644, b"B\n"),
        gitstate.CapturedOutput(b"wiki/concepts/a.md", stat.S_IFREG | 0o644, b"A\n"),
    ]

    with pytest.raises(gitstate.GitStateError, match="diverged"):
        gitstate.apply_outputs(tmp_vault, before, outputs)

    assert first.read_bytes() == b"one\n"
    assert second.read_bytes() == b"human rewrite\n"


def test_planned_out_of_allowlist_output_is_rejected_before_apply(
    tmp_vault, monkeypatch
):
    path = tmp_vault / "system" / "forbidden.md"
    path.write_bytes(b"before\n")
    output = gitstate.CapturedOutput(b"system/forbidden.md", 0o100644, b"planned\n")
    called = []
    monkeypatch.setattr(
        gitstate,
        "_atomic_install",
        lambda *_args, **_kwargs: called.append(True),
    )

    with pytest.raises(gitstate.GitStateError, match="allowlist"):
        gitstate.validate_planned_outputs([output])

    assert path.read_bytes() == b"before\n"
    assert called == []


def test_projection_rolls_back_owned_postimages_and_preserves_concurrent_successor(
    tmp_vault, monkeypatch
):
    first = tmp_vault / "wiki" / "concepts" / "a.md"
    second = tmp_vault / "projects" / "b.md"
    first.write_bytes(b"one\n")
    second.write_bytes(b"two\n")
    before = gitstate.snapshot_worktree(tmp_vault)
    outputs = [
        gitstate.CapturedOutput(b"projects/b.md", stat.S_IFREG | 0o644, b"B\n"),
        gitstate.CapturedOutput(b"wiki/concepts/a.md", stat.S_IFREG | 0o644, b"A\n"),
    ]
    real_install = gitstate._atomic_install
    calls = []

    def fail_second(vault, output):
        calls.append(output.raw_path)
        if len(calls) == 2:
            second.write_bytes(b"concurrent successor\n")
            raise OSError("injected write failure")
        return real_install(vault, output)

    monkeypatch.setattr(gitstate, "_atomic_install", fail_second)

    with pytest.raises(gitstate.GitStateError, match="projection failed"):
        gitstate.apply_outputs(tmp_vault, before, outputs)

    # Raw-byte order applies projects/b.md before wiki/concepts/a.md. Its installed
    # postimage is replaced by the injected successor and rollback must not win.
    assert second.read_bytes() == b"concurrent successor\n"
    assert first.read_bytes() == b"one\n"


def test_projection_reports_both_primary_and_rollback_conflicts(tmp_vault, monkeypatch):
    first = tmp_vault / "projects" / "a.md"
    second = tmp_vault / "wiki" / "concepts" / "b.md"
    first.write_bytes(b"one\n")
    second.write_bytes(b"two\n")
    before = gitstate.snapshot_worktree(tmp_vault)
    outputs = [
        gitstate.CapturedOutput(b"projects/a.md", stat.S_IFREG | 0o644, b"A\n"),
        gitstate.CapturedOutput(b"wiki/concepts/b.md", stat.S_IFREG | 0o644, b"B\n"),
    ]
    real_install = gitstate._atomic_install
    calls = []

    def fail_second(vault, output):
        calls.append(output.raw_path)
        if len(calls) == 2:
            first.write_bytes(b"successor\n")
            raise OSError("primary")
        return real_install(vault, output)

    monkeypatch.setattr(gitstate, "_atomic_install", fail_second)
    with pytest.raises(
        gitstate.GitStateError,
        match=r"projection failed at path-bytes:wiki/concepts/b.md: primary; rollback failed at path-bytes:projects/a.md: diverged",
    ):
        gitstate.apply_outputs(tmp_vault, before, outputs)

    assert first.read_bytes() == b"successor\n"
    assert second.read_bytes() == b"two\n"


def test_manifest_is_raw_sorted_exact_and_rejects_out_of_allowlist(tmp_vault, tmp_path):
    before = gitstate.snapshot_worktree(tmp_vault)
    high = os.path.join(os.fsencode(tmp_vault), b"literature/\xff.md")
    low = os.path.join(os.fsencode(tmp_vault), b"literature/\x80.md")
    with open(high, "wb") as stream:
        stream.write(b"high\n")
    with open(low, "wb") as stream:
        stream.write(b"low\n")
    outputs = [
        gitstate.CapturedOutput(b"literature/\xff.md", stat.S_IFREG | 0o644, b"high\n"),
        gitstate.CapturedOutput(b"literature/\x80.md", stat.S_IFREG | 0o644, b"low\n"),
    ]
    manifest = tmp_path.parent / f"{tmp_path.name}-manifest"

    captured = gitstate.audit_and_write_manifest(tmp_vault, before, outputs, manifest)

    assert manifest.read_bytes() == b"literature/\x80.md\0literature/\xff.md\0"
    assert [item.raw_path for item in captured] == [
        b"literature/\x80.md",
        b"literature/\xff.md",
    ]

    bad_before = gitstate.snapshot_worktree(tmp_vault)
    (tmp_vault / "system" / "unexpected.txt").write_bytes(b"bad\n")
    with pytest.raises(gitstate.GitStateError, match=r"allowlist|actual"):
        gitstate.audit_and_write_manifest(tmp_vault, bad_before, [], manifest)


def test_manifest_destination_must_resolve_outside_vault(tmp_vault, tmp_path):
    inside = tmp_vault / "manifest"
    outside = tmp_path.parent / f"{tmp_path.name}-manifest"
    assert gitstate.validate_manifest_destination(tmp_vault, outside) == outside
    with pytest.raises(gitstate.GitStateError, match="outside"):
        gitstate.validate_manifest_destination(tmp_vault, inside)
    link = tmp_path.parent / f"{tmp_path.name}-inside-link"
    link.symlink_to(tmp_vault / "manifest")
    with pytest.raises(gitstate.GitStateError, match="outside"):
        gitstate.validate_manifest_destination(tmp_vault, link)


def test_manifest_destination_preflight_rejects_unusable_targets(
    tmp_vault, tmp_path, monkeypatch
):
    directory = tmp_path.parent / f"{tmp_path.name}-manifest-dir"
    directory.mkdir()
    with pytest.raises(gitstate.GitStateError, match="file"):
        gitstate.validate_manifest_destination(tmp_vault, directory)

    missing_parent = tmp_path.parent / "missing-parent" / "manifest"
    with pytest.raises(gitstate.GitStateError, match="parent"):
        gitstate.validate_manifest_destination(tmp_vault, missing_parent)

    destination = tmp_path.parent / f"{tmp_path.name}-unwritable"

    def refuse_probe(*_args, **_kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(gitstate.tempfile, "mkstemp", refuse_probe)
    with pytest.raises(gitstate.GitStateError, match="writable"):
        gitstate.validate_manifest_destination(tmp_vault, destination)


def test_manifest_rejects_same_path_rewrite_and_never_recaptures_raced_bytes(
    tmp_vault, tmp_path
):
    path = tmp_vault / "literature" / "out.md"
    path.write_bytes(b"before\n")
    before = gitstate.snapshot_worktree(tmp_vault)
    planned = gitstate.CapturedOutput(
        b"literature/out.md", stat.S_IFREG | 0o644, b"planned\n"
    )
    path.write_bytes(b"concurrent rewrite\n")
    manifest = tmp_path.parent / f"{tmp_path.name}-manifest-race"

    with pytest.raises(gitstate.GitStateError, match=r"postimage|actual"):
        gitstate.audit_and_write_manifest(tmp_vault, before, [planned], manifest)

    assert path.read_bytes() == b"concurrent rewrite\n"
    assert not manifest.exists()


def _index_info(vault, records):
    payload = b"".join(
        f"{mode:o} {oid} {stage}\t".encode() + path + b"\0"
        for mode, oid, stage, path in records
    )
    return _git(vault, "update-index", "-z", "--index-info", stdin=payload)


def test_dirty_overlap_ignores_unrelated_conflicts_and_gitlinks(tmp_vault):
    target = tmp_vault / "wiki" / "concepts" / "out.md"
    target.write_bytes(b"base\n")
    head = _commit(tmp_vault)
    snapshots = gitstate.resolve_snapshots(tmp_vault, candidate="worktree")
    blob = (
        _git(tmp_vault, "hash-object", "-w", "--stdin", stdin=b"conflict\n")
        .stdout.decode()
        .strip()
    )
    _index_info(
        tmp_vault,
        [
            (0o100644, blob, 1, b"projects/conflict.md"),
            (0o100644, blob, 2, b"projects/conflict.md"),
            (0o100644, blob, 3, b"projects/conflict.md"),
            (0o160000, head, 0, b"projects/unrelated-submodule"),
        ],
    )
    index_before = (tmp_vault / ".git" / "index").read_bytes()

    gitstate.validate_dirty_overlap(
        tmp_vault,
        snapshots,
        [gitstate.CapturedOutput(b"wiki/concepts/out.md", 0o100644, b"planned\n")],
    )

    assert (tmp_vault / ".git" / "index").read_bytes() == index_before


@pytest.mark.parametrize("overlap_kind", ["conflict", "gitlink"])
def test_dirty_overlap_rejects_conflict_or_gitlink_at_output(tmp_vault, overlap_kind):
    target = tmp_vault / "wiki" / "concepts" / "out.md"
    target.write_bytes(b"base\n")
    head = _commit(tmp_vault)
    snapshots = gitstate.resolve_snapshots(tmp_vault, candidate="worktree")
    blob = (
        _git(tmp_vault, "hash-object", "-w", "--stdin", stdin=b"conflict\n")
        .stdout.decode()
        .strip()
    )
    if overlap_kind == "conflict":
        _git(tmp_vault, "update-index", "--force-remove", "--", "wiki/concepts/out.md")
        records = [
            (0o100644, blob, stage, b"wiki/concepts/out.md") for stage in (1, 2, 3)
        ]
    else:
        records = [(0o160000, head, 0, b"wiki/concepts/out.md")]
    _index_info(tmp_vault, records)

    with pytest.raises(gitstate.GitStateError, match=r"unmerged|dirty overlapping"):
        gitstate.validate_dirty_overlap(
            tmp_vault,
            snapshots,
            [gitstate.CapturedOutput(b"wiki/concepts/out.md", 0o100644, b"planned\n")],
        )


def test_invalid_utf8_publication_failure_has_canonical_ascii_diagnostic(
    tmp_vault, monkeypatch
):
    (tmp_vault / "index.md").write_bytes(b"base\n")
    _commit(tmp_vault)
    snapshots = gitstate.resolve_snapshots(tmp_vault, candidate="worktree")
    output = gitstate.CapturedOutput(b"literature/\xff.md", 0o100644, b"planned\n")
    real_run = gitstate.subprocess.run

    def fail_update(command, **kwargs):
        if len(command) > 1 and command[1] == "update-index":
            return subprocess.CompletedProcess(
                command,
                1,
                b"",
                b"fatal: b'literature/\\xff.md' \xff",
            )
        return real_run(command, **kwargs)

    monkeypatch.setattr(gitstate.subprocess, "run", fail_update)
    with pytest.raises(gitstate.GitStateError) as caught:
        gitstate.publish_outputs(tmp_vault, snapshots, [output], "snapshot")

    message = str(caught.value)
    message.encode("utf-8", "strict")
    assert "path-bytes:literature/%FF.md" in message
    assert "b'" not in message
    assert "\\xff" not in message.lower()
    assert "\ufffd" not in message
    assert not any(0xD800 <= ord(character) <= 0xDFFF for character in message)


def test_apply_outputs_sweeps_scratch_files_stranded_by_a_killed_run(tmp_vault):
    """A SIGKILL mid-write leaves a scratch file the finally block never ran."""
    target = tmp_vault / "wiki" / "concepts" / "note.md"
    target.write_bytes(b"base\n")
    _commit(tmp_vault)
    dead_pid = 999999
    while gitstate._owner_is_live(dead_pid):
        dead_pid += 1
    stranded = (
        tmp_vault / "wiki" / "concepts" / f".research-vault-projection-{dead_pid}-0"
    )
    stranded.write_bytes(b"half-written\n")
    live = (
        tmp_vault / "wiki" / "concepts" / f".research-vault-projection-{os.getpid()}-0"
    )
    live.write_bytes(b"mine\n")

    before = gitstate.snapshot_worktree(tmp_vault)
    output = gitstate.CapturedOutput(b"wiki/concepts/note.md", 0o100644, b"projected\n")
    gitstate.apply_outputs(tmp_vault, before, [output])

    assert not stranded.exists(), "a dead owner's scratch file must be swept"
    assert live.exists(), "this process's own scratch namespace is never swept"
    assert target.read_bytes() == b"projected\n"


def test_rollback_restores_a_deletion_a_file_and_a_symlink_preimage(tmp_vault):
    """Rollback undoes a projection by each preimage's own kind.

    A path the projection created is removed outright, a replaced file returns
    byte- and mode-exact, and a symlink the projection flattened into a regular
    file becomes a symlink to its original target again. Restoring only the
    bytes would leave the first as a stray file and the last as a real file
    holding the link text.
    """
    kept = tmp_vault / "wiki" / "concepts" / "kept.md"
    kept.write_bytes(b"before\n")
    kept.chmod(0o755)
    link = os.path.join(os.fsencode(tmp_vault), b"wiki/concepts/link.md")
    os.symlink(b"kept.md", link)
    created = tmp_vault / "wiki" / "concepts" / "created.md"
    preimage = gitstate.snapshot_worktree(tmp_vault)

    kept.write_bytes(b"AFTER\n")
    kept.chmod(0o644)
    os.unlink(link)
    with open(link, "wb") as stream:
        stream.write(b"link flattened\n")
    created.write_bytes(b"new\n")
    outputs = [
        gitstate.CapturedOutput(
            b"wiki/concepts/kept.md", stat.S_IFREG | 0o644, b"AFTER\n"
        ),
        gitstate.CapturedOutput(
            b"wiki/concepts/link.md", stat.S_IFREG | 0o644, b"link flattened\n"
        ),
        gitstate.CapturedOutput(
            b"wiki/concepts/created.md", stat.S_IFREG | 0o644, b"new\n"
        ),
    ]

    gitstate.rollback_outputs(tmp_vault, preimage, outputs)

    assert kept.read_bytes() == b"before\n"
    assert stat.S_IMODE(kept.stat().st_mode) == 0o755
    assert os.readlink(link) == b"kept.md"
    assert not created.exists()


def test_rollback_refuses_a_directory_preimage_and_names_the_path(tmp_vault):
    """There is no byte-exact way back from a flattened directory.

    A projection may only install regular files, so a directory preimage means
    the worktree diverged outside the projection's vocabulary. Rollback must say
    so and name the path, not silently accept the postimage as the new truth.
    """
    folder = tmp_vault / "wiki" / "concepts" / "part"
    folder.mkdir()
    preimage = gitstate.snapshot_worktree(tmp_vault)
    folder.rmdir()
    flattened = tmp_vault / "wiki" / "concepts" / "part"
    flattened.write_bytes(b"flattened\n")
    output = gitstate.CapturedOutput(
        b"wiki/concepts/part", stat.S_IFREG | 0o644, b"flattened\n"
    )

    with pytest.raises(
        gitstate.GitStateError,
        match=(
            r"rollback failed at path-bytes:wiki/concepts/part: "
            r"cannot restore a non-file projection preimage"
        ),
    ):
        gitstate.rollback_outputs(tmp_vault, preimage, [output])

    assert flattened.read_bytes() == b"flattened\n"


# --- boundaries pinned against mutation survivors -----------------------------


def test_allowed_manifest_path_needs_a_file_image_an_md_suffix_and_an_owned_root():
    """The verifier's output allowlist: a regular file image, a `.md` path,
    under literature/ or projects/ or exactly the review queue -- each of
    the three guards refuses on its own."""
    file_image = gitstate.FileImage(b"literature/x.md", "file", 0o100644, b"")
    directory = gitstate.FileImage(b"literature/x.md", "directory", 0o40000, None)
    allowed = gitstate._allowed_manifest_path
    assert allowed(b"literature/x.md", file_image) is True
    assert allowed(b"projects/brief/draft.md", file_image) is True
    assert allowed(b"inbox/review-queue.md", file_image) is True
    assert allowed(b"literature/x.md", None) is False
    assert allowed(b"literature/x.md", directory) is False
    assert allowed(b"literature/x.txt", file_image) is False
    assert allowed(b"system/x.md", file_image) is False
    assert allowed(b"inbox/other.md", file_image) is False
