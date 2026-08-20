import subprocess

from harness_core import gitstate


def test_revision_paths_and_blob_bytes_preserve_an_arbitrary_revision(tmp_vault):
    path = tmp_vault / "atlas" / "deleted.md"
    path.write_bytes(b"claim \xff\n")
    subprocess.run(["git", "add", "atlas/deleted.md"], cwd=tmp_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "binary claim"],
        cwd=tmp_vault,
        check=True,
    )
    subprocess.run(["git", "tag", "snapshot"], cwd=tmp_vault, check=True)
    path.write_bytes(b"replacement\n")
    subprocess.run(["git", "add", "atlas/deleted.md"], cwd=tmp_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "replace claim"],
        cwd=tmp_vault,
        check=True,
    )
    path.unlink()

    assert gitstate.revision_paths(tmp_vault, "snapshot", "atlas") == {
        "atlas/deleted.md"
    }
    assert (
        gitstate.blob_bytes(tmp_vault, "snapshot", "atlas/deleted.md")
        == b"claim \xff\n"
    )
    assert (
        gitstate.blob_bytes(tmp_vault, "HEAD", "atlas/deleted.md") == b"replacement\n"
    )
    assert gitstate.blob_bytes(tmp_vault, "snapshot", "atlas/missing.md") is None


def test_blob_bytes_distinguishes_an_empty_blob_from_a_missing_blob(tmp_vault):
    path = tmp_vault / "atlas" / "empty.md"
    path.write_bytes(b"")
    subprocess.run(["git", "add", "atlas/empty.md"], cwd=tmp_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "empty claim"],
        cwd=tmp_vault,
        check=True,
    )

    assert gitstate.blob_bytes(tmp_vault, "HEAD", "atlas/empty.md") == b""
    assert gitstate.blob_bytes(tmp_vault, "HEAD", "atlas/absent.md") is None
