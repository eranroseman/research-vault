import json
import os
import subprocess
import sys
from importlib import resources
from importlib.util import find_spec
from pathlib import Path

import pytest

from research_vault import frontmatter, scaffold

VAULT_DIRS = [
    "inbox",
    "literatures",
    "log",
    "projects",
    "system/templates",
    "system/bases",
]
EXPECTED_CREATED = [
    ".editorconfig",
    ".git/hooks/pre-commit",
    ".gitignore",
    ".markdownlintignore",
    ".prettierignore",
    ".research-vault/machine.json",
    "AGENTS.md",
    "inbox/review-queue.md",
    "index.md",
    "literatures/.gitkeep",
    "log.md",
    "log/.gitkeep",
    "projects/.gitkeep",
    "system/bases/open-questions.base",
    "system/bases/trust-tier.base",
    "system/glossary.md",
    "system/templates/daily.md",
    "system/templates/project.md",
]
TRACKABLE_CREATED = [
    path
    for path in EXPECTED_CREATED
    if not path.startswith((".git/", ".research-vault/"))
]


def git(path, *args):
    return subprocess.run(
        ["git", *args], cwd=path, check=True, text=True, capture_output=True
    ).stdout


def git_result(path, *args):
    return subprocess.run(
        ["git", *args], cwd=path, text=True, capture_output=True, check=False
    )


def initialize_repo(path):
    path.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    git(path, "config", "user.name", "Test User")
    git(path, "config", "user.email", "test@example.edu")


def test_scaffold_module_is_available():
    """Removing the scaffold command implementation makes this fail."""
    assert find_spec("research_vault.scaffold") is not None


def test_scaffold_creates_the_complete_okf_vault_and_returns_paths(tmp_path):
    """Omitting an owned vault artifact or returning a non-auditable path fails."""
    vault = tmp_path / "vault"

    created = scaffold.scaffold_vault(vault)

    assert created == EXPECTED_CREATED
    assert scaffold.VAULT_DIRS == VAULT_DIRS
    assert all((vault / path).exists() for path in EXPECTED_CREATED)
    assert all((vault / path).is_dir() for path in VAULT_DIRS)
    assert (vault / ".git").is_dir()
    glossary = vault / "system" / "glossary.md"
    glossary_data, glossary_body = frontmatter.parse(glossary.read_text())
    canonical_context = resources.files("research_vault").joinpath(
        "templates", "context.md"
    )
    assert glossary_data == {"type": "guide"}
    # The parser retains the blank line that separates the fixed frontmatter
    # envelope from the canonical body, which travels unchanged.
    assert glossary_body.removeprefix("\n").encode() == canonical_context.read_bytes()
    assert glossary.is_file()
    assert not glossary.is_symlink()
    assert (vault / "index.md").read_text() == (
        '---\nokf_version: "0.2"\n---\n'
        "# Vault index\n\n"
        "- [literatures/](literatures/) — evidence layer: literature notes, one per "
        "captured source, named by citation key\n"
        "- [wiki/](wiki/) — compiled layer: per-source pages under `wiki/sources/`, "
        "cross-source pages under `wiki/concepts/`, written by the adopted compile tool\n"
        "- [projects/](projects/) — manuscripts and deliverables\n"
        "- [log/](log/) — daily activity log (summary: [[log]])\n"
        "- [inbox/](inbox/) — fleeting notes and the review queue\n"
        "- [system/](system/) — support artifacts: templates, bases, the CSL file, "
        "the applied propagation plans\n\n"
        "Literature notes, for trust-tier review:\n\n"
        "![[system/bases/trust-tier.base]]\n\n"
        "Concept pages, flagged where they contain an open-question:\n\n"
        "![[system/bases/open-questions.base]]\n"
    )
    assert (vault / "log.md").read_text() == ('---\ntype: "log"\n---\n# Log\n')
    assert (vault / ".gitignore").read_text() == (
        ".research-vault/\n.obsidian/workspace*\n.raw/\n.vault-meta/\nfulltext/\n"
    )
    # Byte-pinned against the CANONICAL json.tool form the JSON owner produces
    # (tests/test_config_validity.py asserts the template itself equals it). Same
    # object, expanded nesting; the one-time canonicalization is its own commit.
    assert (vault / ".research-vault" / "machine.json").read_text() == (
        "{\n"
        '  "claude_obsidian_root": "",\n'
        '  "mailto": "you@example.edu",\n'
        '  "path_map": {\n'
        '    "D:\\\\Zotero\\\\": "/mnt/d/Zotero/"\n'
        "  },\n"
        '  "zotero_base": "http://localhost:23119",\n'
        '  "zotero_profile": ""\n'
        "}\n"
    )
    for path in (
        "AGENTS.md",
        "inbox/review-queue.md",
        "system/glossary.md",
        "system/templates/daily.md",
        "system/templates/project.md",
    ):
        data, _ = frontmatter.parse((vault / path).read_text())
        assert data["type"]
    log_data, _ = frontmatter.parse((vault / "log.md").read_text())
    assert log_data == {"type": "log"}


def test_scaffold_is_idempotent_and_never_overwrites_existing_files(tmp_path):
    """Replacing user-maintained scaffold paths or making a second pass mutating fails."""
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "index.md").write_text("human index\n")
    (vault / ".research-vault").mkdir()
    (vault / ".research-vault" / "machine.json").write_text('{"mailto": "human"}\n')
    (vault / "system").mkdir()
    glossary = vault / "system" / "glossary.md"
    glossary.write_text("human glossary\n")
    hooks = vault / ".git" / "hooks"
    hooks.mkdir(parents=True)
    hook = hooks / "pre-commit"
    hook.write_text("#!/bin/sh\necho human\n")

    created = scaffold.scaffold_vault(vault)

    assert "index.md" not in created
    assert ".research-vault/machine.json" not in created
    assert ".git/hooks/pre-commit" not in created
    assert "system/glossary.md" not in created
    assert (vault / "index.md").read_text() == "human index\n"
    assert (
        vault / ".research-vault" / "machine.json"
    ).read_text() == '{"mailto": "human"}\n'
    assert hook.read_text() == "#!/bin/sh\necho human\n"
    assert glossary.read_text() == "human glossary\n"
    assert not os.access(hook, os.X_OK)
    assert scaffold.scaffold_vault(vault) == []
    assert glossary.read_text() == "human glossary\n"


def test_scaffold_git_calls_run_in_the_vault_wherever_the_process_sits(
    tmp_path, monkeypatch
):
    """From a cwd that is no repository at all, scaffold still commits into the
    vault. `.research-vault/machine.json` is created and stays out of that
    commit by the local-only rule (`_LOCAL_ONLY_PATHS`), which runs before any
    git call -- the vault's own ignore rules are pinned by
    test_scaffold_skips_a_created_path_the_vaults_own_gitignore_ignores."""
    monkeypatch.chdir(tmp_path)
    vault = tmp_path / "vault"
    created = scaffold.scaffold_vault(vault)
    assert ".research-vault/machine.json" in created
    assert git(vault, "log", "--format=%s") == "Scaffold knowledge vault\n"
    assert git(vault, "ls-files", "--", ".research-vault") == ""
    assert git(vault, "ls-files", "--", "index.md") == "index.md\n"


def test_scaffold_installs_an_executable_hook_and_keeps_empty_roots_in_clones(tmp_path):
    """Dropping hook execute permission or empty vault roots after clone fails."""
    vault = tmp_path / "vault"
    scaffold.scaffold_vault(vault)

    assert os.access(vault / ".git" / "hooks" / "pre-commit", os.X_OK)
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(vault), str(clone)], check=True)
    for root in ("literatures", "log", "projects"):
        assert (clone / root / ".gitkeep").is_file()


def test_scaffold_ci_flags_are_independent(tmp_path):
    """Making either CI workflow imply the other fails."""
    read_only = tmp_path / "read-only"
    rw = tmp_path / "rw"

    read_only_created = scaffold.scaffold_vault(read_only, with_ci=True)
    rw_created = scaffold.scaffold_vault(rw, with_rw_ci=True)

    assert ".github/workflows/verify.yml" in read_only_created
    assert ".github/workflows/rw-batch.yml" not in read_only_created
    assert ".github/workflows/rw-batch.yml" in rw_created
    assert ".github/workflows/verify.yml" not in rw_created


def test_scaffold_copies_exact_authority_assets_with_consent_and_modes(tmp_path):
    vault = tmp_path / "vault"
    created = scaffold.scaffold_vault(vault, with_ci=True, with_rw_ci=True)
    packaged = resources.files("research_vault").joinpath("templates")
    expected = {
        ".git/hooks/pre-commit": packaged.joinpath("git", "pre-commit"),
        ".github/workflows/verify.yml": packaged.joinpath("ci", "verify.yml"),
        ".github/workflows/rw-batch.yml": packaged.joinpath("ci", "rw-batch.yml"),
        "system/templates/project.md": packaged.joinpath(
            "vault", "system", "templates", "project.md"
        ),
    }

    assert set(expected) <= set(created)
    for relative, source in expected.items():
        assert (vault / relative).read_bytes() == source.read_bytes()
    assert (vault / ".git/hooks/pre-commit").stat().st_mode & 0o111 == 0o111
    assert (vault / ".github/workflows/verify.yml").stat().st_mode & 0o111 == 0
    assert (vault / ".github/workflows/rw-batch.yml").stat().st_mode & 0o111 == 0


def test_scaffold_commits_only_its_created_paths_and_preserves_user_index(tmp_path):
    """Sweeping user changes into the scaffold commit or altering their index fails."""
    vault = tmp_path / "vault"
    vault.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=vault, check=True)
    git(vault, "config", "user.name", "Test User")
    git(vault, "config", "user.email", "test@example.edu")
    (vault / "baseline.md").write_text("baseline\n")
    git(vault, "add", "--", "baseline.md")
    git(vault, "commit", "-qm", "baseline")
    (vault / "staged.md").write_text("staged\n")
    git(vault, "add", "--", "staged.md")
    (vault / "unstaged.md").write_text("unstaged\n")
    (vault / "untracked.md").write_text("untracked\n")
    index_before = git(vault, "diff", "--cached", "--binary")

    created = scaffold.scaffold_vault(vault)

    assert created == EXPECTED_CREATED
    assert git(vault, "diff", "--cached", "--binary") == index_before
    assert git(vault, "show", "--format=", "--name-only", "HEAD").splitlines() == (
        TRACKABLE_CREATED
    )
    assert (vault / "unstaged.md").read_text() == "unstaged\n"
    assert (vault / "untracked.md").read_text() == "untracked\n"


def test_scaffold_refuses_a_staged_deletion_of_an_owned_target_before_writing(tmp_path):
    """Recreating an owned file that the user staged for deletion must fail."""
    vault = tmp_path / "vault"
    initialize_repo(vault)
    index = vault / "index.md"
    index.write_text("user version\n")
    git(vault, "add", "--", "index.md")
    git(vault, "commit", "-qm", "baseline")
    index.unlink()
    git(vault, "add", "--", "index.md")
    index_before = git(vault, "diff", "--cached", "--binary")

    with pytest.raises(ValueError, match="conflict"):
        scaffold.scaffold_vault(vault)

    assert not index.exists()
    assert git(vault, "diff", "--cached", "--binary") == index_before
    assert not (vault / ".gitignore").exists()
    assert not (vault / ".research-vault").exists()
    assert not (vault / "inbox").exists()


def test_scaffold_refuses_a_staged_glossary_deletion_before_writing(tmp_path):
    """Recreating a staged glossary deletion must fail before any output writes."""
    vault = tmp_path / "vault"
    initialize_repo(vault)
    glossary = vault / "system" / "glossary.md"
    glossary.parent.mkdir()
    glossary.write_text("user glossary\n")
    git(vault, "add", "--", "system/glossary.md")
    git(vault, "commit", "-qm", "baseline")
    glossary.unlink()
    git(vault, "add", "--", "system/glossary.md")
    index_before = git(vault, "diff", "--cached", "--binary")

    with pytest.raises(ValueError, match="conflict"):
        scaffold.scaffold_vault(vault)

    assert not glossary.exists()
    assert git(vault, "diff", "--cached", "--binary") == index_before
    assert not (vault / ".gitignore").exists()
    assert not (vault / ".research-vault").exists()
    assert not (vault / "inbox").exists()


def test_scaffold_keeps_machine_configuration_local_without_an_ignore_rule(tmp_path):
    """A missing .research-vault ignore rule must not make machine config committable."""
    vault = tmp_path / "vault"
    initialize_repo(vault)
    (vault / ".gitignore").write_text(".obsidian/\n")

    scaffold.scaffold_vault(vault)

    assert (vault / ".research-vault" / "machine.json").is_file()
    assert git_result(
        vault, "ls-files", "--error-unmatch", ".research-vault/machine.json"
    ).returncode
    assert "?? .research-vault/" in git(vault, "status", "--short")


def test_scaffold_initializes_a_nested_repository_instead_of_using_an_enclosing_one(
    tmp_path,
):
    """A destination inside another repository must become its own vault root."""
    outer = tmp_path / "outer"
    initialize_repo(outer)
    vault = outer / "vault"

    scaffold.scaffold_vault(vault)

    assert git(vault, "rev-parse", "--show-toplevel").strip() == str(vault)
    hook = Path(git(vault, "rev-parse", "--git-path", "hooks/pre-commit").strip())
    assert (hook if hook.is_absolute() else vault / hook).is_file()


def test_scaffold_uses_git_plumbing_for_a_linked_worktree_hook(tmp_path):
    """A linked worktree's .git file must not be treated as a hooks directory."""
    main = tmp_path / "main"
    initialize_repo(main)
    (main / "baseline.md").write_text("baseline\n")
    git(main, "add", "--", "baseline.md")
    git(main, "commit", "-qm", "baseline")
    vault = tmp_path / "vault"
    git(main, "worktree", "add", "-q", "-b", "vault", str(vault))

    scaffold.scaffold_vault(vault)

    hook = Path(git(vault, "rev-parse", "--git-path", "hooks/pre-commit").strip())
    assert (hook if hook.is_absolute() else vault / hook).is_file()


def test_scaffold_refuses_owned_symlink_paths_before_writing(tmp_path):
    """An owned symlink must not redirect scaffold writes outside the vault."""
    vault = tmp_path / "vault"
    vault.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (vault / "inbox").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="symlink"):
        scaffold.scaffold_vault(vault)

    assert not (outside / "review-queue.md").exists()
    assert not (vault / ".git").exists()
    assert not (vault / ".gitignore").exists()


def test_scaffold_refuses_a_symlinked_destination_before_writing(tmp_path):
    """A destination symlink must not redirect the entire scaffold outside."""
    vault = tmp_path / "vault"
    outside = tmp_path / "outside"
    outside.mkdir()
    vault.symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="symlink"):
        scaffold.scaffold_vault(vault)

    assert not (outside / ".git").exists()
    assert not (outside / "index.md").exists()


def test_scaffold_refuses_a_symlinked_destination_ancestor_before_writing(tmp_path):
    """A lexical parent symlink must not redirect a missing vault leaf."""
    outside = tmp_path / "outside"
    outside.mkdir()
    parent = tmp_path / "symlinked-parent"
    parent.symlink_to(outside, target_is_directory=True)
    vault = parent / "vault"

    with pytest.raises(ValueError, match="symlink"):
        scaffold.scaffold_vault(vault)

    assert not (outside / "vault").exists()


def test_scaffold_cli_prints_the_created_paths(tmp_path):
    """A CLI that hides local-only creation or ignores the flags fails."""
    vault = tmp_path / "vault"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "research_vault",
            "scaffold",
            "--vault",
            str(vault),
            "--with-ci",
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        text=True,
        capture_output=True,
    )

    assert completed.stdout.splitlines() == sorted(
        [*EXPECTED_CREATED, ".github/workflows/verify.yml"]
    )


def test_scaffold_cli_requires_literal_rw_consent_and_installs_only_rw_workflow(
    tmp_path,
):
    """The literal RW flag must not install or imply the read-only workflow."""
    vault = tmp_path / "rw-vault"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "research_vault",
            "scaffold",
            "--vault",
            str(vault),
            "--with-rw-ci",
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        text=True,
        capture_output=True,
    )

    assert completed.stdout.splitlines() == sorted(
        [*EXPECTED_CREATED, ".github/workflows/rw-batch.yml"]
    )
    packaged_rw = resources.files("research_vault").joinpath(
        "templates", "ci", "rw-batch.yml"
    )
    rw_workflow = vault / ".github/workflows/rw-batch.yml"
    assert rw_workflow.read_bytes() == packaged_rw.read_bytes()
    assert not (vault / ".github/workflows/verify.yml").exists()
    assert (vault / ".git/hooks/pre-commit").stat().st_mode & 0o111 == 0o111
    assert rw_workflow.stat().st_mode & 0o111 == 0


# --- boundaries the blanket mutation run (Plan W Task 25) found unpinned ------


@pytest.mark.parametrize(
    ("relative", "flags"),
    [
        (".research-vault/machine.json", {}),
        (".github/workflows/verify.yml", {"with_ci": True}),
        (".github/workflows/rw-batch.yml", {"with_rw_ci": True}),
    ],
)
def test_scaffold_refuses_a_staged_deletion_of_each_optional_owned_target(
    tmp_path, relative, flags
):
    """Each of the three optional owned paths is a preflight candidate exactly
    when scaffold would create it: tracked but deleted from the worktree is
    the conflict, named by its path."""
    vault = tmp_path / "vault"
    initialize_repo(vault)
    target = vault / relative
    target.parent.mkdir(parents=True)
    target.write_text("user version\n")
    git(vault, "add", "--", relative)
    git(vault, "commit", "-qm", "baseline")
    target.unlink()
    git(vault, "add", "--", relative)

    with pytest.raises(
        ValueError, match=f"scaffold conflict with tracked path: {relative}"
    ):
        scaffold.scaffold_vault(vault, **flags)
    assert not (vault / "inbox").exists()


def test_scaffold_ignores_a_tracked_workflow_it_was_not_asked_for_and_its_own_commits(
    tmp_path,
):
    """A tracked-but-deleted workflow is no conflict when its flag is off, and
    a second scaffold over the workflows and machine.json it committed or
    wrote itself is a no-op, never a conflict."""
    vault = tmp_path / "vault"
    initialize_repo(vault)
    workflow = vault / ".github" / "workflows" / "verify.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("user version\n")
    git(vault, "add", "--", ".github/workflows/verify.yml")
    git(vault, "commit", "-qm", "baseline")
    workflow.unlink()
    git(vault, "add", "--", ".github/workflows/verify.yml")
    created = scaffold.scaffold_vault(vault, with_rw_ci=True)
    assert ".github/workflows/rw-batch.yml" in created
    assert ".github/workflows/verify.yml" not in created

    git(vault, "add", "-f", "--", ".research-vault/machine.json")
    git(vault, "commit", "-qm", "track machine.json")
    assert scaffold.scaffold_vault(vault, with_rw_ci=True) == []

    # The user's own verify.yml committed again (past the vault's verifier
    # hook, which is not under test here): asking for CI over it is a no-op
    # too, not a conflict and not an overwrite.
    workflow.write_text("user version\n")
    git(vault, "add", "--", ".github/workflows/verify.yml")
    git(vault, "commit", "--no-verify", "-qm", "the user's own workflow")
    assert scaffold.scaffold_vault(vault, with_ci=True, with_rw_ci=True) == []
    assert workflow.read_text() == "user version\n"


# --- the survivors the observed CI gate run (34827110718) exposed -----------
# Locally each of the four git-subcommand mutants read as a timeout (an invalid
# `git LS-FILES` walks PATH, slow enough under WSL2 to hit mutmut's limit),
# which the gate never baselines; on the runner the same call exited 1 in
# milliseconds and read as "not tracked" / "not ignored", and no test told the
# difference. The runner is the arbiter; these pin the answers.


def test_is_tracked_reads_the_index_and_head_and_nothing_else(tmp_path):
    """A path in the index but not yet in HEAD is tracked -- the state only
    `ls-files --error-unmatch` answers, since `cat-file -e HEAD:` cannot see
    it; a committed path is tracked; an untracked or absent one is not."""
    vault = tmp_path / "vault"
    initialize_repo(vault)
    (vault / "committed.md").write_text("committed\n")
    git(vault, "add", "--", "committed.md")
    git(vault, "commit", "-qm", "baseline")
    (vault / "staged.md").write_text("staged\n")
    git(vault, "add", "--", "staged.md")
    (vault / "untracked.md").write_text("untracked\n")

    assert scaffold._is_tracked(vault, "staged.md") is True
    assert scaffold._is_tracked(vault, "committed.md") is True
    assert scaffold._is_tracked(vault, "untracked.md") is False
    assert scaffold._is_tracked(vault, "absent.md") is False


def test_scaffold_refuses_an_owned_target_staged_but_never_committed(tmp_path):
    """The index alone makes a path tracked: an `index.md` the user added and
    then removed from the worktree before any commit is the conflict, named,
    and nothing is written."""
    vault = tmp_path / "vault"
    initialize_repo(vault)
    index = vault / "index.md"
    index.write_text("user version\n")
    git(vault, "add", "--", "index.md")
    index.unlink()

    with pytest.raises(
        ValueError, match=r"scaffold conflict with tracked path: index\.md"
    ):
        scaffold.scaffold_vault(vault)

    assert not index.exists()
    assert not (vault / "inbox").exists()
    assert git(vault, "ls-files", "--", "index.md") == "index.md\n"


def test_scaffold_skips_a_created_path_the_vaults_own_gitignore_ignores(
    tmp_path, monkeypatch
):
    """A user `.gitignore` that ignores a template path: the file is still
    created (the template is the template), but scaffold asks git -- in the
    vault, from a cwd that is no repository -- whether each created path is
    ignored, and commits only the rest; `git add` of an ignored path refuses."""
    monkeypatch.chdir(tmp_path)
    vault = tmp_path / "vault"
    initialize_repo(vault)
    (vault / ".gitignore").write_text("log.md\n")

    created = scaffold.scaffold_vault(vault)

    assert "log.md" in created
    assert ".gitignore" not in created
    assert (vault / "log.md").is_file()
    committed = git(vault, "show", "--format=", "--name-only", "HEAD").splitlines()
    assert "log.md" not in committed
    assert "index.md" in committed
    assert git_result(vault, "check-ignore", "-q", "--", "log.md").returncode == 0
    assert git(vault, "ls-files", "--", "log.md") == ""


def test_installed_plugins_reads_the_registry_under_home_as_utf8_or_answers_empty(
    tmp_path, monkeypatch
):
    """`~/.claude/plugins/installed_plugins.json`, read as UTF-8: its
    `plugins` mapping when the file parses to an object carrying one; `{}`
    for an absent, unreadable, undecodable, malformed or shapeless registry.
    Under a temporary HOME: the one suite test that reached this read
    (doctor's probe list) answered from the developer's own home, where a
    registry exists, and the CI runner has none -- so a mutant that broke the
    read died here and lived there."""
    monkeypatch.setenv("HOME", str(tmp_path))
    registry = tmp_path / ".claude" / "plugins" / "installed_plugins.json"
    assert scaffold._installed_plugins() == {}
    registry.parent.mkdir(parents=True)
    plugins = {
        "claude-obsidian@agricidaniel-claude-obsidian": [
            {"gitCommitSha": "ad67087cad22", "installPath": "/plugins/claude-obsidian"}
        ]
    }
    registry.write_text(
        json.dumps({"version": 2, "plugins": plugins}), encoding="utf-8"
    )
    assert scaffold._installed_plugins() == plugins
    for body in ('{"version": 2}', '{"plugins": ["x"]}', "[1, 2]", "{not json"):
        registry.write_text(body, encoding="utf-8")
        assert scaffold._installed_plugins() == {}
    registry.write_bytes(b"\xff\xfe\x00")
    assert scaffold._installed_plugins() == {}
    registry.unlink()
    registry.mkdir()
    assert scaffold._installed_plugins() == {}
