import json
import os
import re
import subprocess
from pathlib import Path

from research_vault import frontmatter

REPO = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = REPO / "research_vault" / "templates"

EXPECTED_PATHS = {
    "vault/index.md",
    "vault/log.md",
    "vault/AGENTS.md",
    "vault/inbox/review-queue.md",
    "context.md",
    "vault/system/templates/project.md",
    "vault/system/templates/daily.md",
    "vault/system/bases/open-questions.base",
    "vault/system/bases/trust-tier.base",
    "vault/gitignore",
    "vault/prettierignore",
    "vault/markdownlintignore",
    "vault/editorconfig",
    "research-vault/machine.json.example",
    "zotero-addons.md",
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
        "- [literature/](literature/) — evidence layer: literature notes, one per "
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
    assert asset("vault/log.md").read_text() == "# Log\n"
    # The machine-surface rule says "raise a finding", never "fail the gate":
    # append-only covers log/ and inbox/review-queue.md but is in no
    # CLOSING_BY_SURFACE set, so "fail the gate" would be false. Pinned
    # whole-file, byte-for-byte, below: a per-line startswith/in pattern
    # admits append, reorder, and layout drift undetected; each line is
    # load-bearing.
    # Constraint on the opening paragraph (the preamble, first two sentences
    # below): it names machine surfaces but must assert no enforcement
    # mechanism — no claim of a session warning, a commit-time gate, or a
    # guaranteed trace. None holds uniformly across the seven it names —
    # literature/, log/, log.md, inbox/review-queue.md, system/bibliography.json,
    # fulltext/ and system/propagations/: an in-format append to log/ or
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
        "This is a research-vault vault. `literature/`, `log/`, `log.md`, "
        "`inbox/review-queue.md`, `system/bibliography.json`, `fulltext/`, and "
        "`system/propagations/` are machine-written — the CLI writes them; don't edit them by hand.\n\n"
        "Evidence is added to Zotero and projected into `literature/` — "
        "evidence notes exist only by projection, never by hand. Read "
        "`wiki/index.md` and recent `log/` entries before editing; review "
        "findings live in `inbox/review-queue.md`.\n\n"
        "Prefer the two model-invocable research-vault skills over generic "
        "drafting, even for free-form requests: run `evidence-conventions` for "
        "claim syntax and `synthesis-conventions` for the rules of the compiled "
        "layer.\n\n"
        "These eight are the user-invoked entry points — type the name to run "
        "one; an agent cannot reach them on its own:\n\n"
        "| Skill                     | Use it to                                                      |\n"
        "| ------------------------- | -------------------------------------------------------------- |\n"
        "| `setup-vault`             | create, repair, or provision a vault                           |\n"
        "| `project-flow`            | start or resume a research project                             |\n"
        "| `find-sources`            | find literature before it is added to Zotero                   |\n"
        "| `capture-source`          | add, capture, refresh, propagate a re-key, or compile a source |\n"
        "| `verify-citations`        | verify citations and run the citation checks                   |\n"
        "| `factcheck-draft`         | factcheck a draft against its sources before review            |\n"
        "| `publish`                 | publish, park, correct, or withdraw a project                  |\n"
        "| `paper-critical-analysis` | write an in-depth critical analysis report of one paper        |\n"
        "\n"
        "Literature notes are wholly machine-written: `capture` regenerates "
        "the whole note from Zotero on every run, so per-source prose belongs "
        "in a Zotero child note, which capture renders.\n\n"
        "Machine surfaces are owner-written: hand or tool edits are "
        "regenerated away or raise a finding.\n\n"
        "`wiki/` is written only by the adopted compile tool's transaction "
        "engine; never `Write` or `Edit` under it.\n\n"
        "`capture` is the sole writer of the CSL file `system/bibliography.json`, "
        "rendered from Better BibTeX; users and other tools must not write it.\n\n"
        "Formatters are writers too: `.prettierignore` and `.markdownlintignore` "
        "keep them off the machine surfaces; `.editorconfig` disables an "
        "editor's own trim/final-newline defaults there instead.\n\n"
        "`.research-vault/` is machine-local: nothing in it travels with the vault.\n"
    )
    assert asset("vault/inbox/review-queue.md").read_text() == (
        '---\ntype: "review-queue"\n---\n'
    )
    assert asset("vault/system/templates/project.md").read_text() == (
        '---\ntitle: "{{TITLE}}"\ntype: "project"\n'
        'status: "draft"\ngenerated: {by: "{{ACTOR}}", at: "{{NOW}}"}\n---\n'
    )
    assert asset("vault/system/templates/daily.md").read_text() == (
        '---\ntype: "daily"\n---\n\n<!-- log/YYYY-MM-DD.md; append-only -->\n'
    )


def test_bases_and_machine_example_match_canonical_shapes():
    open_questions = asset("vault/system/bases/open-questions.base").read_text()
    trust_tier = asset("vault/system/bases/trust-tier.base").read_text()
    assert re.search(
        r"name: Open questions\nfilters:\n  and:\n    - 'type == \"concept\"'",
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
        "claude_obsidian_root": "",
        "mailto": "you@example.edu",
        "path_map": {"D:\\Zotero\\": "/mnt/d/Zotero/"},
        "zotero_base": "http://localhost:23119",
        "zotero_profile": "",
    }
    gitignore = asset("vault/gitignore").read_text()
    assert ".research-vault/\n" in gitignore
    assert ".obsidian/workspace*\n" in gitignore


# Anchored (leading "/") gitignore-style form, as research_vault/lints.py's
# _is_append_only_path names the append-only three (log/, inbox/review-queue.md,
# projects/*/search-log.md) plus system/bibliography.json (capture's CSL
# render), literature/ (the evidence layer), and fulltext/ (capture's
# derived text layer, hash-tracked by the literature note it belongs to).
# Anchoring matters: an unanchored "log/" also matches a nested
# projects/<name>/log/, silently widening what a formatter skips.
_MACHINE_SURFACES = (
    "/literature/",
    "/log/",
    "/inbox/review-queue.md",
    "/system/bibliography.json",
    "/projects/*/search-log.md",
    "/fulltext/",
    "/system/propagations/",
)


def test_formatter_ignores_cover_every_machine_surface():
    # prettier and markdownlint both read gitignore-style patterns, so their
    # ignore files list the seven machine surfaces as plain, anchored
    # gitignore lines.
    for name in ("vault/prettierignore", "vault/markdownlintignore"):
        text = asset(name).read_text()
        for surface in _MACHINE_SURFACES:
            assert surface in text, (name, surface)

    # .editorconfig has no gitignore-style ignore mechanism, and ships no
    # [*] section -- it defends only the seven machine surfaces and makes
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
    assert "- uses: actions/checkout@v7" in text
    assert "fetch-depth: 0" in text
    assert "- uses: actions/setup-python@v7" in text
    assert "python-version: '3.12'" in text
    assert (
        'python -m pip install "research-vault-core @ git+https://github.com/eranroseman/'
        'research-vault.git"'
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
    assert "- uses: actions/checkout@v7" in text
    assert "fetch-depth: 0" in text
    assert "- uses: actions/setup-python@v7" in text
    assert "python-version: '3.12'" in text
    assert (
        'python -m pip install "research-vault-core @ git+https://github.com/eranroseman/'
        'research-vault.git"'
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


def test_glossary_carries_the_ingest_vocabulary_and_no_retired_terms():
    text = (REPO / "CONTEXT.md").read_text()
    for term in (
        "**Ingest**",
        "**Selection**",
        "**Add**",
        "**Capture**",
        "**Compile**",
        "**Drift**",
        "**Refresh**",
        "**Item key**",
        "**Citation key**",
        "**Captured set**",
        "**Provenance tuple**",
        "**Text layer**",
        "**Compiled layer**",
        "**Propagation plan**",
    ):
        assert term in text, term
    for retired in (
        "**Admission**",
        "**Managed region**",
        "**Screening state**",
        "**Bibliography export**",
        "**Synthesis layer**",
    ):
        assert retired not in text, retired
    # named once, as the spelling to avoid
    assert text.count("citekey") == 1
    assert "_Avoid_: citekey" in text


def test_readme_embeds_the_addon_declaration_verbatim():
    table = asset("zotero-addons.md").read_text()
    assert table.strip() in (REPO / "README.md").read_text()


def _guard_constants():
    """`hooks/pretooluse_guard.py`'s three deny surfaces, imported from the file
    (the hooks directory is no package)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "pretooluse_guard", ROOT / "hooks" / "pretooluse_guard.py"
    )
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    return guard


def test_agents_template_preamble_names_every_guarded_surface_but_wiki():
    """Line 7's roster is derived from the guard's constants — the directory
    names, the nested prefixes and the exact files the PreToolUse guard
    denies — minus `wiki/`, which has its own sentence (line 29). A surface
    the guard denies and the preamble omits (`system/bibliography.json`, #25)
    is one an agent is never told about."""
    guard = _guard_constants()
    guarded = (
        {f"{name}/" for name in guard.MACHINE_SURFACE_DIR_NAMES if name != "wiki"}
        | {f"{prefix.as_posix()}/" for prefix in guard.MACHINE_SURFACE_PREFIXES}
        | {path.as_posix() for path in guard.MACHINE_SURFACE_FILES}
    )
    preamble = asset("vault/AGENTS.md").read_text().splitlines()[6]
    assert preamble.startswith("This is a research-vault vault. ")
    assert set(re.findall(r"`([^`]+)`", preamble)) == guarded


def test_agents_template_names_capture_as_the_csl_files_writer():
    text = asset("vault/AGENTS.md").read_text()
    assert (
        "`capture` is the sole writer of the CSL file `system/bibliography.json`, "
        "rendered from Better BibTeX; users and other tools must not write it."
    ) in text
    assert "Better BibTeX is the sole writer" not in text
