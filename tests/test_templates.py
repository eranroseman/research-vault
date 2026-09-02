import json
import os
import re
import subprocess
from pathlib import Path

from research_vault import frontmatter

REPO = Path(__file__).resolve().parents[1]
TEMPLATES = REPO / "research_vault" / "templates"

EXPECTED_PATHS = {
    "vault/index.md",
    "vault/log.md",
    "vault/AGENTS.md",
    "vault/inbox/review-queue.md",
    "vault/synthesis/index.md",
    "context.md",
    "vault/system/templates/literature.md",
    "vault/system/templates/synthesis.md",
    "vault/system/templates/project.md",
    "vault/system/templates/daily.md",
    "vault/system/bases/open-questions.base",
    "vault/system/bases/trust-tier.base",
    "vault/gitignore",
    "vault/prettierignore",
    "vault/markdownlintignore",
    "vault/editorconfig",
    "research-vault/machine.json.example",
    "git/pre-commit",
    "ci/verify.yml",
    "ci/rw-batch.yml",
}


def asset(path):
    return TEMPLATES / path


def test_all_canonical_template_paths_are_packaged():
    actual = {
        path.relative_to(TEMPLATES).as_posix()
        for path in TEMPLATES.rglob("*")
        if path.is_file()
    }
    assert actual == EXPECTED_PATHS
    package_data = (REPO / "pyproject.toml").read_text()
    assert '"templates/**/*"' in package_data


def test_packaged_context_is_the_canonical_glossary_source():
    """A second authored glossary cannot diverge from CONTEXT.md."""
    assert asset("context.md").read_bytes() == (REPO / "CONTEXT.md").read_bytes()


def test_markdown_templates_have_expected_okf_frontmatter():
    reserved = {
        path
        for path in EXPECTED_PATHS
        if path == "vault/log.md"
        or (path.endswith("/index.md") and path != "vault/index.md")
    }
    concept_paths = {
        path
        for path in EXPECTED_PATHS
        if path.startswith("vault/") and path.endswith(".md")
    }
    for path in sorted(concept_paths - reserved - {"vault/index.md"}):
        data, _ = frontmatter.parse(asset(path).read_text())
        assert data.get("type"), path

    root_data, _ = frontmatter.parse(asset("vault/index.md").read_text())
    assert root_data == {"okf_version": "0.2"}
    for path in reserved:
        data, _ = frontmatter.parse(asset(path).read_text())
        assert data == {}, path

    queue_data, _ = frontmatter.parse(asset("vault/inbox/review-queue.md").read_text())
    assert queue_data == {"type": "review-queue"}
    daily_data, _ = frontmatter.parse(
        asset("vault/system/templates/daily.md").read_text()
    )
    assert daily_data == {"type": "daily"}


def test_markdown_templates_match_canonical_content():
    assert asset("vault/index.md").read_text() == (
        '---\nokf_version: "0.2"\n---\n'
        "# Vault index\n\n"
        "- [[literatures/]] — evidence layer: citekey-keyed literature notes\n"
        "- [[synthesis/]] — synthesis notes (see [[synthesis/index]])\n"
        "- [[projects/]] — manuscripts and deliverables\n"
        "- [[log/]] — daily activity log (summary: [[log]])\n"
        "- [[inbox/]] — fleeting notes and the review queue\n"
        "- [[system/]] — support artifacts: templates, bases, the bibliography export\n\n"
        "Literature notes, for trust-tier review:\n\n"
        "![[system/bases/trust-tier.base]]\n\n"
        "Synthesis notes, flagged where they contain an open-question:\n\n"
        "![[system/bases/open-questions.base]]\n"
    )
    assert asset("vault/log.md").read_text() == "# Log\n"
    # Ruled content, 2026-08-22: dangling spec §8 ref cut, managed-region rule
    # added, machine-surface rule reworded to "raise a finding" (append-only
    # covers log/ and inbox/review-queue.md but is in no CLOSING_BY_SURFACE
    # set, so "fail the gate" was false). Pinned whole-file, byte-for-byte,
    # below: the earlier per-line startswith/in pattern admitted append,
    # reorder, and layout drift undetected; each line remains load-bearing.
    # Constraint on the opening paragraph (the preamble, first two sentences
    # below): it names machine surfaces but must assert no enforcement
    # mechanism — no claim of a session warning, a commit-time gate, or a
    # guaranteed trace. None holds uniformly across literatures/, log/,
    # log.md, and inbox/review-queue.md: an in-format append to log/ or
    # inbox/review-queue.md keeps the prior bytes as a prefix, so
    # lint_append_only's startswith check never fires and
    # `verify --surface commit` exits 0 with zero findings. Any future
    # wording here that asserts detection or blocking must be re-verified
    # against CLOSING_BY_SURFACE (research_vault/verify.py) and
    # lint_append_only's startswith predicate (research_vault/lints.py)
    # before landing.
    assert asset("vault/AGENTS.md").read_text() == (
        '---\ntype: "guide"\n---\n\n'
        "# Vault agents guide\n\n"
        "This is a research-vault vault. `literatures/`, `log/`, `log.md`, "
        "and `inbox/review-queue.md` are machine-written — the CLI writes "
        "them; don't edit them by hand.\n\n"
        "Evidence is admitted through Zotero and projected into `literatures/` — "
        "evidence notes exist only by projection, never by hand. Read "
        "`synthesis/index.md` and recent `log/` entries before editing; review "
        "findings live in `inbox/review-queue.md`.\n\n"
        "Prefer the two model-invocable research-vault skills over generic "
        "drafting, even for free-form requests: run `evidence-conventions` for "
        "claim syntax and `synthesis-conventions` for synthesis-note rules.\n\n"
        "These seven are the user-invoked entry points — type the name to run "
        "one; an agent cannot reach them on its own:\n\n"
        "| Skill              | Use it to                                                |\n"
        "| ------------------ | -------------------------------------------------------- |\n"
        "| `setup-vault`      | create, repair, or provision a vault                     |\n"
        "| `project-flow`     | start or resume a research project                       |\n"
        "| `find-sources`     | find literature before it is admitted to Zotero          |\n"
        "| `import-source`    | import, catalog, refresh, or backfill an admitted source |\n"
        "| `verify-citations` | verify citations and run the citation checks             |\n"
        "| `factcheck-draft`  | factcheck a draft against its sources before review      |\n"
        "| `publish`          | publish, park, correct, or withdraw a project            |\n"
        "\n"
        "Text between `%%rv-managed%%` markers is regenerated by the bridge — "
        "edits there do not survive. Free prose below the managed region is "
        "yours and persists.\n\n"
        "Machine surfaces are owner-written: hand or tool edits are "
        "regenerated away or raise a finding.\n\n"
        "Better BibTeX is the sole writer of `system/bibliography.json`; users "
        "and other tools must not write it.\n\n"
        "Formatters are writers too: `.prettierignore` and `.markdownlintignore` "
        "keep them off the machine surfaces; `.editorconfig` disables an "
        "editor's own trim/final-newline defaults there instead.\n\n"
        "`.research-vault/` is machine-local: nothing in it travels with the vault.\n"
    )
    assert asset("vault/inbox/review-queue.md").read_text() == (
        '---\ntype: "review-queue"\n---\n'
    )
    assert asset("vault/synthesis/index.md").read_text() == "# Synthesis index\n"
    assert asset("vault/system/templates/literature.md").read_text() == (
        '---\ncitekey: "{{CITEKEY}}"\ntype: "literature"\n'
        'accessed: "{{TODAY}}"\nfixity-sha256:\n'
        'managed-sha256: "{{MANAGED_SHA256}}"\nstatus: "unscreened"\n'
        'generated: {by: "{{ACTOR}}", at: "{{NOW}}"}\n---\n\n'
        "%%rv-managed%%\n\n# {{TITLE}}\n\n%%/rv-managed%%\n\n## Notes\n"
    )
    for kind in ("synthesis", "project"):
        assert asset(f"vault/system/templates/{kind}.md").read_text() == (
            f'---\ntitle: "{{{{TITLE}}}}"\ntype: "{kind}"\n'
            'status: "draft"\ngenerated: {by: "{{ACTOR}}", at: "{{NOW}}"}\n---\n'
        )
    assert asset("vault/system/templates/daily.md").read_text() == (
        '---\ntype: "daily"\n---\n\n<!-- log/YYYY-MM-DD.md; append-only -->\n'
    )
def test_bases_and_machine_example_match_canonical_shapes():
    open_questions = asset("vault/system/bases/open-questions.base").read_text()
    trust_tier = asset("vault/system/bases/trust-tier.base").read_text()
    assert re.search(
        r"name: Open questions\nfilters:\n  and:\n    - 'type == \"synthesis\"'",
        open_questions,
    )
    assert (
        "formulas:\n  open_q: 'file.content.contains(\"(open-question)\")'\n"
        in open_questions
    )
    assert open_questions.count("type ==") == 1
    assert re.search(
        r"name: Trust tier\nfilters:\n  and:\n    - 'type == \"literature\"'",
        trust_tier,
    )
    assert trust_tier.count("type ==") == 1

    machine = json.loads(asset("research-vault/machine.json.example").read_text())
    assert machine == {
        "mailto": "you@example.edu",
        "path_map": {"D:\\Zotero\\": "/mnt/d/Zotero/"},
    }
    gitignore = asset("vault/gitignore").read_text()
    assert ".research-vault/\n" in gitignore
    assert ".obsidian/workspace*\n" in gitignore


# Anchored (leading "/") gitignore-style form, as research_vault/lints.py's
# _is_append_only_path names the append-only three (log/, inbox/review-queue.md,
# projects/*/search-log.md) plus system/bibliography.json (Better BibTeX's
# export) and literatures/ (the evidence layer). Anchoring matters: an
# unanchored "log/" also matches a nested projects/<name>/log/, silently
# widening what a formatter skips.
_MACHINE_SURFACES = (
    "/literatures/",
    "/log/",
    "/inbox/review-queue.md",
    "/system/bibliography.json",
    "/projects/*/search-log.md",
)


def test_formatter_ignores_cover_every_machine_surface():
    # prettier and markdownlint both read gitignore-style patterns, so their
    # ignore files list the five machine surfaces as plain, anchored
    # gitignore lines.
    for name in ("vault/prettierignore", "vault/markdownlintignore"):
        text = asset(name).read_text()
        for surface in _MACHINE_SURFACES:
            assert surface in text, (name, surface)

    # .editorconfig has no gitignore-style ignore mechanism, and ships no
    # [*] section -- it defends only the five machine surfaces and makes
    # no claim about any other vault file. `false` is the active override
    # for the two boolean properties: it wins even against a user's own
    # editor-wide setting, unlike `unset` or omission, either of which
    # yields to that global config (spec.editorconfig.org, "unset").
    # charset/end_of_line have no boolean "off" and are deliberately
    # absent: with no [*] section, there is nothing left in scope for
    # `unset` to undo, so it would be inert. EditorConfig glob sections
    # have no gitignore-style leading-slash syntax; an interior "/" is
    # what anchors them to this file's own directory.
    editorconfig = asset("vault/editorconfig").read_text()
    assert "root = true" in editorconfig
    assert "[*]" not in editorconfig.splitlines()
    for surface in _MACHINE_SURFACES:
        relative = surface.removeprefix("/")
        glob = f"{relative}**" if relative.endswith("/") else relative
        assert f"[{glob}]" in editorconfig, (surface, glob)
    assert "= unset" not in editorconfig
    assert "charset =" not in editorconfig
    assert "end_of_line =" not in editorconfig
    assert editorconfig.count("= false") == len(_MACHINE_SURFACES) * 2


def test_precommit_hook_is_executable_and_has_exact_contract():
    hook = asset("git/pre-commit")
    text = hook.read_text()
    assert hook.stat().st_mode & os.X_OK
    subprocess.run(["sh", "-n", str(hook)], check=True)
    assert (
        'python3 -m research_vault verify --vault "$vault" --offline --surface commit --git-base "$git_base" --git-candidate index'
        in text
    )
    assert 'git_base="$(git rev-parse --verify HEAD 2>/dev/null)"' in text
    assert "git hash-object -w -t tree /dev/null" in text
    assert 'git cat-file -e "$git_base^{tree}"' in text
    assert "git commit --no-verify" in text
    assert 'if ! python3 -c "import research_vault" 2>/dev/null; then' in text
    assert (
        "pre-commit: research_vault is not importable; CI will replay verification."
        in text
    )
    assert "1)" in text
    assert "pre-commit: commit-closing verification failed." in text
    assert "3)" in text
    assert (
        "pre-commit: verification unreachable; leaving commit open for CI replay."
        in text
    )
    assert (
        '*)\n    echo "pre-commit: verifier exited unexpectedly with status $code."'
        in text
    )


def test_verify_workflow_has_read_only_base_resolution_and_exit_contract():
    text = asset("ci/verify.yml").read_text()
    assert "name: verify\non: [push, pull_request]" in text
    assert "permissions:\n  contents: read" in text
    assert "- uses: actions/checkout@v4" in text
    assert "fetch-depth: 0" in text
    assert "- uses: actions/setup-python@v5" in text
    assert "python-version: '3.12'" in text
    assert (
        'python -m pip install "knowledge-harness @ git+https://github.com/eranroseman/'
        'knowledge-harness.git"'
    ) in text
    assert "EVENT_NAME: ${{ github.event_name }}" in text
    assert "PR_BASE: ${{ github.event.pull_request.base.sha }}" in text
    assert "PUSH_BASE: ${{ github.event.before }}" in text
    assert "zero=0000000000000000000000000000000000000000" in text
    assert "persist-credentials: false" in text
    assert 'empty_tree="$(git hash-object -w -t tree /dev/null)"' in text
    assert 'git fetch --no-tags origin "$base"' in text
    assert 'git cat-file -e "$base^{tree}"' in text
    assert 'printf \'sha=%s\\n\' "$base" >> "$GITHUB_OUTPUT"' in text
    assert "BASE: ${{ steps.base.outputs.sha }}" in text
    assert 'git-base "$BASE"' in text
    assert "--git-candidate HEAD" in text
    assert "git push" not in text
    assert "0) exit 0 ;;" in text
    assert "1) exit 1 ;;" in text
    assert (
        '3)\n              echo "::warning::verification unreachable; no closing mismatch reported"'
        in text
    )
    assert (
        '*)\n              echo "::error::verifier exited unexpectedly with status $code"'
        in text
    )


def test_rw_workflow_has_explicit_csv_only_write_boundary():
    text = asset("ci/rw-batch.yml").read_text()
    assert "name: rw-batch\non:" in text
    assert "cron: 17 3 * * *" in text
    assert "workflow_dispatch: {}" in text
    assert "concurrency:\n  group: rw-batch\n  cancel-in-progress: false\n" in text
    assert "permissions:\n  contents: write" in text
    assert "- uses: actions/checkout@v4" in text
    assert "fetch-depth: 0" in text
    assert "- uses: actions/setup-python@v5" in text
    assert "python-version: '3.12'" in text
    assert (
        'python -m pip install "knowledge-harness @ git+https://github.com/eranroseman/'
        'knowledge-harness.git"'
    ) in text
    assert 'curl --fail --show-error --location --output "$RUNNER_TEMP/rw.csv"' in text
    assert (
        "https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv"
        in text
    )
    assert (
        '--offline --surface audit --git-candidate worktree --rw-csv "$RUNNER_TEMP/rw.csv" --changed-paths-file "$RUNNER_TEMP/research-vault-changed-paths" --commit-projected "chore: rw-batch findings"'
        in text
    )
    assert "No verifier-owned changes." in text
    assert 'git config user.name "research-vault-ci"' in text
    assert 'git config user.email "actions@users.noreply.github.com"' in text
    assert "git push" in text
    assert "0) exit 0 ;;" in text
    assert "1)" in text
    assert "3)" in text
    assert 'if [[ ! -s "$manifest" ]]; then' in text
    assert "git add" not in text
    assert "git commit" not in text
    assert "--pathspec-from-file" not in text
    assert "|| true" not in text
