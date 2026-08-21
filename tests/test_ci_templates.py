from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "harness_core" / "templates" / "ci"


def test_read_only_ci_has_explicit_base_head_candidate_and_no_repository_authority():
    text = (ASSETS / "verify.yml").read_text()
    assert text.count("permissions:") == 1
    assert "permissions:\n  contents: read" in text
    assert "persist-credentials: false" in text
    assert "git hash-object -w -t tree /dev/null" in text
    assert 'git fetch --no-tags origin "$base"' in text
    assert 'git cat-file -e "$base^{tree}"' in text
    assert "BASE: ${{ steps.base.outputs.sha }}" in text
    assert (
        "python -m harness_core verify --vault . --offline --surface commit "
        '--git-base "$BASE" --git-candidate HEAD'
    ) in text
    assert '--git-base "${{' not in text
    assert "git push" not in text
    assert "git commit" not in text
    assert "contents: write" not in text
    assert "1) exit 1 ;;" in text
    assert "3)" in text
    assert "::warning::verification unreachable" in text


def test_rw_ci_delegates_exact_snapshot_commit_to_verifier_and_accepts_only_zero():
    text = (ASSETS / "rw-batch.yml").read_text()
    command = (
        "python -m harness_core verify --vault . --offline --surface audit "
        '--git-candidate worktree --rw-csv "$RUNNER_TEMP/rw.csv" '
        '--changed-paths-file "$RUNNER_TEMP/harness-changed-paths" '
        '--commit-projected "chore: rw-batch findings"'
    )
    assert "permissions:\n  contents: write" in text
    assert "concurrency:\n  group: rw-batch\n  cancel-in-progress: false\n" in text
    assert 'git config user.name "harness-ci"' in text
    assert 'git config user.email "actions@users.noreply.github.com"' in text
    assert "curl --fail --show-error --location" in text
    assert command in text
    assert "0) exit 0 ;;" in text
    assert "0|1)" not in text
    assert "1)" in text
    assert "3)" in text
    assert 'if [[ ! -s "$manifest" ]]; then' in text
    assert "git push" in text
    assert "git add" not in text
    assert "git commit" not in text
    assert "--pathspec-from-file" not in text
    assert "|| true" not in text


def test_rw_push_is_guarded_by_nonempty_manifest_after_verifier_step():
    text = (ASSETS / "rw-batch.yml").read_text()
    verify_at = text.index("--commit-projected")
    manifest_at = text.index('if [[ ! -s "$manifest" ]]')
    push_at = text.index("git push")
    assert verify_at < manifest_at < push_at
