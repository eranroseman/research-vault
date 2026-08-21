import builtins
import os
import stat
import subprocess

import pytest

from knowledge_harness import gitstate


def test_revision_paths_and_blob_bytes_preserve_an_arbitrary_revision(tmp_vault):
    path = tmp_vault / "synthesis" / "deleted.md"
    path.write_bytes(b"claim \xff\n")
    subprocess.run(["git", "add", "synthesis/deleted.md"], cwd=tmp_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "binary claim"],
        cwd=tmp_vault,
        check=True,
    )
    subprocess.run(["git", "tag", "snapshot"], cwd=tmp_vault, check=True)
    path.write_bytes(b"replacement\n")
    subprocess.run(["git", "add", "synthesis/deleted.md"], cwd=tmp_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "replace claim"],
        cwd=tmp_vault,
        check=True,
    )
    path.unlink()

    assert gitstate.revision_paths(tmp_vault, "snapshot", "synthesis") == {
        b"synthesis/deleted.md"
    }
    assert (
        gitstate.blob_bytes(tmp_vault, "snapshot", "synthesis/deleted.md")
        == b"claim \xff\n"
    )
    assert (
        gitstate.blob_bytes(tmp_vault, "HEAD", "synthesis/deleted.md")
        == b"replacement\n"
    )
    assert gitstate.blob_bytes(tmp_vault, "snapshot", "synthesis/missing.md") is None


def test_blob_bytes_distinguishes_an_empty_blob_from_a_missing_blob(tmp_vault):
    path = tmp_vault / "synthesis" / "empty.md"
    path.write_bytes(b"")
    subprocess.run(["git", "add", "synthesis/empty.md"], cwd=tmp_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "empty claim"],
        cwd=tmp_vault,
        check=True,
    )

    assert gitstate.blob_bytes(tmp_vault, "HEAD", "synthesis/empty.md") == b""
    assert gitstate.blob_bytes(tmp_vault, "HEAD", "synthesis/absent.md") is None


def _git(vault, *args, stdin=None, check=True):
    return subprocess.run(
        ["git", *args], cwd=vault, input=stdin, capture_output=True, check=check
    )


def _commit(vault, message="baseline"):
    _git(vault, "add", "-A")
    _git(vault, "commit", "-q", "-m", message)
    return _git(vault, "rev-parse", "HEAD").stdout.decode().strip()


def test_snapshot_resolution_separates_base_expected_head_index_and_live(tmp_vault):
    path = tmp_vault / "synthesis" / "note.md"
    path.write_bytes(b"base\n")
    parent = _commit(tmp_vault)
    path.write_bytes(b"staged\n")
    _git(tmp_vault, "add", "synthesis/note.md")
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
    assert snapshots.candidate.image(b"synthesis/note.md").data == b"staged\n"
    assert snapshots.live.image(b"synthesis/note.md").data == b"unstaged scratch\n"
    assert (tmp_vault / ".git" / "index").read_bytes() == index_before
    assert _git(tmp_vault, "rev-parse", "HEAD").stdout.decode().strip() == parent


def test_unborn_defaults_to_stored_empty_tree_and_index_candidate(tmp_vault):
    (tmp_vault / "literatures" / "first.md").write_bytes(b"first\n")
    _git(tmp_vault, "add", "literatures/first.md")
    index_before = (tmp_vault / ".git" / "index").read_bytes()

    snapshots = gitstate.resolve_snapshots(tmp_vault, candidate="index")

    assert snapshots.expected_head is None
    assert (
        _git(
            tmp_vault, "cat-file", "-e", f"{snapshots.base_tree}^{{tree}}", check=False
        ).returncode
        == 0
    )
    assert snapshots.candidate.image(b"literatures/first.md").data == b"first\n"
    assert (tmp_vault / ".git" / "index").read_bytes() == index_before


def test_corrupt_head_is_not_silently_treated_as_an_unborn_branch(tmp_vault):
    head = tmp_vault / ".git" / "HEAD"
    head.write_text("not-an-object\n")
    before = gitstate.snapshot_worktree(tmp_vault)

    with pytest.raises(gitstate.GitStateError, match="HEAD"):
        gitstate.resolve_snapshots(tmp_vault, candidate="worktree")

    assert gitstate.snapshot_worktree(tmp_vault) == before


def test_snapshot_rejects_same_inode_rewrite_during_read(tmp_vault, monkeypatch):
    path = tmp_vault / "synthesis" / "changing.md"
    path.write_bytes(b"before\n")
    raw_path = b"synthesis/changing.md"
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
    old = b"synthesis/old\xff\nname.md"
    old_abs = os.path.join(root, old)
    os.makedirs(os.path.dirname(old_abs), exist_ok=True)
    with open(old_abs, "wb") as stream:
        stream.write(b"raw\n")
    _git(tmp_vault, "add", "--", old)
    first = _commit(tmp_vault)
    new = b"synthesis/new\xfe\nname.md"
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
    link = tmp_vault / "synthesis" / "outside.md"
    link.symlink_to(outside)
    candidate = gitstate.snapshot_worktree(tmp_vault)
    planning = tmp_path / "planning"

    gitstate.materialize_snapshot(candidate, planning)
    captured = gitstate.snapshot_worktree(planning)
    restored = gitstate.restore_candidate_nonfiles(candidate, captured)

    assert not (planning / "synthesis" / "outside.md").exists()
    assert restored.image(b"synthesis/outside.md") == candidate.image(
        b"synthesis/outside.md"
    )
    assert gitstate.outputs_between(candidate, restored) == ()


def test_publish_outputs_uses_exact_captured_blobs_and_leaves_live_index_unchanged(
    tmp_vault,
):
    target = tmp_vault / "synthesis" / "out.md"
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
        b"synthesis/out.md", stat.S_IFREG | 0o644, b"captured\n"
    )
    target.write_bytes(b"later rewrite\n")

    commit = gitstate.publish_outputs(
        tmp_vault, snapshots, [captured], "snapshot projection"
    )

    assert _git(tmp_vault, "rev-parse", "HEAD^").stdout.decode().strip() == parent
    assert _git(tmp_vault, "show", "HEAD:synthesis/out.md").stdout == b"captured\n"
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
    path = tmp_vault / "synthesis" / "out.md"
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
    with pytest.raises(gitstate.GitStateError, match="concurrent|update-ref"):
        gitstate.publish_outputs(
            tmp_vault,
            snapshots,
            [
                gitstate.CapturedOutput(
                    b"synthesis/out.md", stat.S_IFREG | 0o644, b"captured\n"
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
    target = tmp_vault / "synthesis" / "out.md"
    target.write_bytes(b"base\n")
    expected_head = _commit(tmp_vault)
    snapshots = gitstate.resolve_snapshots(tmp_vault, candidate="worktree")
    index_before = (tmp_vault / ".git" / "index").read_bytes()
    captured = gitstate.CapturedOutput(
        b"synthesis/out.md", stat.S_IFREG | 0o644, b"captured\n"
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
            _git(tmp_vault, "show", f"{commit}:synthesis/out.md").stdout
            == b"captured\n"
        )


def test_projection_refuses_preimage_divergence_before_first_write(tmp_vault):
    first = tmp_vault / "synthesis" / "a.md"
    second = tmp_vault / "projects" / "b.md"
    first.write_bytes(b"one\n")
    second.write_bytes(b"two\n")
    before = gitstate.snapshot_worktree(tmp_vault)
    second.write_bytes(b"human rewrite\n")
    outputs = [
        gitstate.CapturedOutput(b"projects/b.md", stat.S_IFREG | 0o644, b"B\n"),
        gitstate.CapturedOutput(b"synthesis/a.md", stat.S_IFREG | 0o644, b"A\n"),
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
    first = tmp_vault / "synthesis" / "a.md"
    second = tmp_vault / "projects" / "b.md"
    first.write_bytes(b"one\n")
    second.write_bytes(b"two\n")
    before = gitstate.snapshot_worktree(tmp_vault)
    outputs = [
        gitstate.CapturedOutput(b"projects/b.md", stat.S_IFREG | 0o644, b"B\n"),
        gitstate.CapturedOutput(b"synthesis/a.md", stat.S_IFREG | 0o644, b"A\n"),
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

    # Raw-byte order applies projects/b.md before synthesis/a.md. Its installed
    # postimage is replaced by the injected successor and rollback must not win.
    assert second.read_bytes() == b"concurrent successor\n"
    assert first.read_bytes() == b"one\n"


def test_projection_reports_both_primary_and_rollback_conflicts(tmp_vault, monkeypatch):
    first = tmp_vault / "projects" / "a.md"
    second = tmp_vault / "synthesis" / "b.md"
    first.write_bytes(b"one\n")
    second.write_bytes(b"two\n")
    before = gitstate.snapshot_worktree(tmp_vault)
    outputs = [
        gitstate.CapturedOutput(b"projects/a.md", stat.S_IFREG | 0o644, b"A\n"),
        gitstate.CapturedOutput(b"synthesis/b.md", stat.S_IFREG | 0o644, b"B\n"),
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
        match=r"projection failed at path-bytes:synthesis/b.md: primary; rollback failed at path-bytes:projects/a.md: diverged",
    ):
        gitstate.apply_outputs(tmp_vault, before, outputs)

    assert first.read_bytes() == b"successor\n"
    assert second.read_bytes() == b"two\n"


def test_manifest_is_raw_sorted_exact_and_rejects_out_of_allowlist(tmp_vault, tmp_path):
    before = gitstate.snapshot_worktree(tmp_vault)
    high = os.path.join(os.fsencode(tmp_vault), b"literatures/\xff.md")
    low = os.path.join(os.fsencode(tmp_vault), b"literatures/\x80.md")
    with open(high, "wb") as stream:
        stream.write(b"high\n")
    with open(low, "wb") as stream:
        stream.write(b"low\n")
    outputs = [
        gitstate.CapturedOutput(
            b"literatures/\xff.md", stat.S_IFREG | 0o644, b"high\n"
        ),
        gitstate.CapturedOutput(b"literatures/\x80.md", stat.S_IFREG | 0o644, b"low\n"),
    ]
    manifest = tmp_path.parent / f"{tmp_path.name}-manifest"

    captured = gitstate.audit_and_write_manifest(tmp_vault, before, outputs, manifest)

    assert manifest.read_bytes() == b"literatures/\x80.md\0literatures/\xff.md\0"
    assert [item.raw_path for item in captured] == [
        b"literatures/\x80.md",
        b"literatures/\xff.md",
    ]

    bad_before = gitstate.snapshot_worktree(tmp_vault)
    (tmp_vault / "system" / "unexpected.txt").write_bytes(b"bad\n")
    with pytest.raises(gitstate.GitStateError, match="allowlist|actual"):
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
    path = tmp_vault / "synthesis" / "out.md"
    path.write_bytes(b"before\n")
    before = gitstate.snapshot_worktree(tmp_vault)
    planned = gitstate.CapturedOutput(
        b"synthesis/out.md", stat.S_IFREG | 0o644, b"planned\n"
    )
    path.write_bytes(b"concurrent rewrite\n")
    manifest = tmp_path.parent / f"{tmp_path.name}-manifest-race"

    with pytest.raises(gitstate.GitStateError, match="postimage|actual"):
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
    target = tmp_vault / "synthesis" / "out.md"
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
        [gitstate.CapturedOutput(b"synthesis/out.md", 0o100644, b"planned\n")],
    )

    assert (tmp_vault / ".git" / "index").read_bytes() == index_before


@pytest.mark.parametrize("overlap_kind", ["conflict", "gitlink"])
def test_dirty_overlap_rejects_conflict_or_gitlink_at_output(tmp_vault, overlap_kind):
    target = tmp_vault / "synthesis" / "out.md"
    target.write_bytes(b"base\n")
    head = _commit(tmp_vault)
    snapshots = gitstate.resolve_snapshots(tmp_vault, candidate="worktree")
    blob = (
        _git(tmp_vault, "hash-object", "-w", "--stdin", stdin=b"conflict\n")
        .stdout.decode()
        .strip()
    )
    if overlap_kind == "conflict":
        _git(tmp_vault, "update-index", "--force-remove", "--", "synthesis/out.md")
        records = [(0o100644, blob, stage, b"synthesis/out.md") for stage in (1, 2, 3)]
    else:
        records = [(0o160000, head, 0, b"synthesis/out.md")]
    _index_info(tmp_vault, records)

    with pytest.raises(gitstate.GitStateError, match="unmerged|dirty overlapping"):
        gitstate.validate_dirty_overlap(
            tmp_vault,
            snapshots,
            [gitstate.CapturedOutput(b"synthesis/out.md", 0o100644, b"planned\n")],
        )


def test_invalid_utf8_publication_failure_has_canonical_ascii_diagnostic(
    tmp_vault, monkeypatch
):
    (tmp_vault / "index.md").write_bytes(b"base\n")
    _commit(tmp_vault)
    snapshots = gitstate.resolve_snapshots(tmp_vault, candidate="worktree")
    output = gitstate.CapturedOutput(b"literatures/\xff.md", 0o100644, b"planned\n")
    real_run = gitstate.subprocess.run

    def fail_update(command, **kwargs):
        if len(command) > 1 and command[1] == "update-index":
            return subprocess.CompletedProcess(
                command,
                1,
                b"",
                b"fatal: b'literatures/\\xff.md' \xff",
            )
        return real_run(command, **kwargs)

    monkeypatch.setattr(gitstate.subprocess, "run", fail_update)
    with pytest.raises(gitstate.GitStateError) as caught:
        gitstate.publish_outputs(tmp_vault, snapshots, [output], "snapshot")

    message = str(caught.value)
    message.encode("utf-8", "strict")
    assert "path-bytes:literatures/%FF.md" in message
    assert "b'" not in message
    assert "\\xff" not in message.lower()
    assert "\ufffd" not in message
    assert not any(0xD800 <= ord(character) <= 0xDFFF for character in message)


def test_apply_outputs_sweeps_scratch_files_stranded_by_a_killed_run(tmp_vault):
    """A SIGKILL mid-write leaves a scratch file the finally block never ran."""
    target = tmp_vault / "synthesis" / "note.md"
    target.write_bytes(b"base\n")
    _commit(tmp_vault)
    dead_pid = 999999
    while gitstate._owner_is_live(dead_pid):
        dead_pid += 1
    stranded = tmp_vault / "synthesis" / f".harness-projection-{dead_pid}-0"
    stranded.write_bytes(b"half-written\n")
    live = tmp_vault / "synthesis" / f".harness-projection-{os.getpid()}-0"
    live.write_bytes(b"mine\n")

    before = gitstate.snapshot_worktree(tmp_vault)
    output = gitstate.CapturedOutput(b"synthesis/note.md", 0o100644, b"projected\n")
    gitstate.apply_outputs(tmp_vault, before, [output])

    assert not stranded.exists(), "a dead owner's scratch file must be swept"
    assert live.exists(), "this process's own scratch namespace is never swept"
    assert target.read_bytes() == b"projected\n"
