import fnmatch
import json
import os
import re
import subprocess
from pathlib import Path

import pytest

from research_vault import frontmatter, structure

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
    "vault/system/templates/weekly.md",
    "vault/system/templates/monthly.md",
    "vault/system/bases/trust-tier.base",
    "vault/gitignore",
    "vault/prettierignore",
    "vault/markdownlintignore",
    "vault/editorconfig",
    "vault/claude/settings.json",
    "research-vault/machine.json.example",
    "zotero-addons.md",
    "obsidian-plugins.md",
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
    seed = {path for path in actual if path.startswith("obsidian/")}
    assert actual - seed == EXPECTED_PATHS
    assert seed
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
        "- [log/](log/) — the machines' activity log (summary: [log](/log.md))\n"
        "- [daily/](daily/) — the person's diary: Obsidian's Daily notes write here\n"
        "- [inbox/](inbox/) — fleeting notes and the review queue\n"
        "- [system/](system/) — support artifacts: templates, bases, the CSL file, "
        "the applied propagation plans\n\n"
        "Literature notes, for trust-tier review:\n\n"
        "![](/system/bases/trust-tier.base)\n\n"
        "Open questions, wherever a claim line carries one:\n\n"
        '```query\npath:projects/ "(open-question)"\n```\n'
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
    # guaranteed trace. None holds uniformly across the eight it names —
    # literature/, log/, log.md, inbox/review-queue.md, system/bibliography.json,
    # fulltext/, system/propagations/ and system/compiled-pages.json: an in-format append to log/ or
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
        "`inbox/review-queue.md`, `system/bibliography.json`, `fulltext/`, "
        "`system/propagations/`, and `system/compiled-pages.json` are machine-written — the CLI writes them; don't edit them by hand.\n\n"
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
        "Machine surfaces are owner-written, and changes to them are "
        "detected: a hand or shell edit to `literature/`, `wiki/`, root "
        "`log.md`, `inbox/review-queue.md`, `system/bibliography.json`, "
        "`system/propagations/` or `system/compiled-pages.json` raises a finding at commit, and an edit to "
        "`fulltext/` at publish. The seeded `.claude/settings.json` refuses "
        "the common shell forms of such a write (redirects, `tee`, `sed -i`, "
        "`cp`, `mv`, `touch`, `rm`) in a session started at the vault root; "
        "an interpreter one-liner, a script or a git restore is caught by "
        "detection, not refused. What detection does not reach: an in-format "
        "append to `log/` committed together with a regenerated `log.md`, an "
        "append to the review queue, deleting a `fulltext/` file (a fresh "
        "clone has none), the non-capture keys a literature "
        "note carries forward, and a page and its record entry co-edited "
        "through an interpreter, either committed with --no-verify or beside "
        "planted local evidence (a compile journal under "
        "`.vault-meta/transactions/` or a seal-store copy under "
        "`.vault-meta/research-vault/`), which the hook must accept because a "
        "seal that normalised links, or a reseal chain between commits, has "
        "no other evidence; CI and the replay cannot tell either route from a "
        "legitimate seal. A record entry taken from another branch outside a "
        "merge, cherry-pick or revert (`git checkout other -- "
        "system/compiled-pages.json`) is a hold, not a gap: the commit waits "
        "for an acknowledgement.\n\n"
        "`wiki/` is written only by the adopted compile tool's transaction "
        "engine; never `Write` or `Edit` under it. A hand edit under `wiki/` "
        "is reported against the compiled-page record, "
        "`system/compiled-pages.json`, and holds the commit.\n\n"
        "`capture` is the sole writer of the CSL file `system/bibliography.json`, "
        "rendered from Better BibTeX; users and other tools must not write it.\n\n"
        "Formatters are writers too: `.prettierignore` and `.markdownlintignore` "
        "keep them off the machine surfaces; `.editorconfig` disables an "
        "editor's own trim/final-newline defaults there instead.\n\n"
        "`.research-vault/` is machine-local: nothing in it travels with the vault.\n\n"
        "`.obsidian/` is the person's Obsidian configuration, seeded once by "
        "scaffold; doctor's `obsidian` row compares it with the declared "
        "settings and never rewrites it.\n"
    )
    assert asset("vault/inbox/review-queue.md").read_text() == (
        '---\ntype: "review-queue"\n---\n'
    )
    assert asset("vault/system/templates/project.md").read_text() == (
        '---\ntitle: "{{TITLE}}"\ntype: "project"\n'
        'status: "draft"\ngenerated: {by: "{{ACTOR}}", at: "{{NOW}}"}\n---\n'
    )
    assert asset("vault/system/templates/daily.md").read_text() == (
        '---\ntype: "daily"\n---\n'
    )


def test_bases_and_machine_example_match_canonical_shapes():
    trust_tier = asset("vault/system/bases/trust-tier.base").read_text()
    assert re.search(
        r"name: Trust tier\nfilters:\n  and:\n    - 'type == \"literature\"'",
        trust_tier,
    )
    assert trust_tier.count("type ==") == 1

    machine = json.loads(asset("research-vault/machine.json.example").read_text())
    assert machine == {
        "claude_obsidian_root": "",
        "mailto": "you@example.edu",
        "obsidian_config_dir": "",
        "path_map": {"D:\\Zotero\\": "/mnt/d/Zotero/"},
        "zotero_base": "http://localhost:23119",
        "zotero_profile": "",
    }
    gitignore = asset("vault/gitignore").read_text()
    assert ".research-vault/\n" in gitignore
    assert ".obsidian/workspace*\n" in gitignore
    for litter in (".DS_Store\n", "._*\n", "[Dd]esktop.ini\n"):
        assert litter in gitignore
    # The walkers' litter names are the seed's own gitignore lines: each name
    # the predicate excludes is one a seeded pattern ignores, AppleDouble's
    # prefix included, and each casing a seeded pattern ignores is excluded.
    patterns = [line for line in gitignore.splitlines() if line and line[0] != "#"]
    for name in (*structure.OS_LITTER, f"{structure._APPLE_DOUBLE_PREFIX}x.md"):
        assert any(fnmatch.fnmatchcase(name, line) for line in patterns), name
    for name in ("desktop.ini", "Desktop.ini"):
        assert structure.is_os_litter(name), name


# Anchored (leading "/") gitignore-style form, as research_vault/lints.py's
# _is_append_only_path names the append-only three (log/, inbox/review-queue.md,
# projects/*/search-log.md) plus system/bibliography.json (capture's CSL
# render), literature/ (the evidence layer), fulltext/ (capture's
# derived text layer, hash-tracked by the literature note it belongs to),
# system/propagations/ (the write-once applied plans), wiki/ (the compile
# tool's pages, sealed by hash), root log.md (the fixer's render) and
# system/compiled-pages.json (the compiled-page record) (spec §4.5).
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
    "/wiki/",
    "/log.md",
    "/system/compiled-pages.json",
)


def test_formatter_ignores_cover_every_machine_surface():
    # prettier and markdownlint both read gitignore-style patterns, so their
    # ignore files list the ten machine surfaces as plain, anchored
    # gitignore lines.
    for name in ("vault/prettierignore", "vault/markdownlintignore"):
        text = asset(name).read_text()
        for surface in _MACHINE_SURFACES:
            assert surface in text, (name, surface)

    # .editorconfig has no gitignore-style ignore mechanism, and ships no
    # [*] section -- it defends only the ten machine surfaces and makes
    # no claim about any other vault file. `false` is the active override
    # for the two boolean properties: it wins even against a user's own
    # editor-wide setting, unlike `unset` or omission, either of which
    # yields to that global config (spec.editorconfig.org, "unset").
    # charset/end_of_line have no boolean "off" and are deliberately
    # absent: with no [*] section, there is nothing left in scope for
    # `unset` to undo, so it would be inert. A "/" in an EditorConfig glob
    # anchors it to this file's own directory: an interior one for a nested
    # path, a leading one for a root file, which a bare name would match at
    # every depth (spec.editorconfig.org, "Glob Expressions").
    editorconfig = asset("vault/editorconfig").read_text()
    assert "root = true" in editorconfig
    assert "[*]" not in editorconfig.splitlines()
    for surface in _MACHINE_SURFACES:
        relative = surface.removeprefix("/")
        if relative.endswith("/"):
            glob = f"{relative}**"
        elif "/" in relative:
            glob = relative
        else:
            # a root file keeps its leading slash: that is what anchors it
            glob = surface
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
    assert 'python3 -m research_vault stamp-type --vault "$vault" --staged' in text
    assert "git add" not in text
    assert "pathspec) and commit again" in text
    assert 'git_base="$(git rev-parse --verify HEAD 2>/dev/null)"' in text
    assert "git hash-object -w -t tree /dev/null" in text
    assert 'git cat-file -e "$git_base^{tree}"' in text
    assert "git commit --no-verify" in text
    assert 'if ! python3 -c "import research_vault" 2>/dev/null; then' in text
    assert (
        "pre-commit: research_vault is not importable; the publish re-check "
        "(and CI, if configured) replays this commit." in text
    )
    assert "1)" in text
    assert "pre-commit: commit-closing verification failed." in text
    assert (
        "Bypass with --no-verify; the publish re-check (and CI, if configured) "
        "replays a bypassed commit." in text
    )
    assert "3)" in text
    assert (
        "pre-commit: verification unreachable; leaving commit open for the "
        "publish re-check (and CI, if configured)." in text
    )
    assert (
        '*)\n    echo "pre-commit: verifier exited unexpectedly with status $code."'
        in text
    )


def test_verify_workflow_has_read_only_base_resolution_and_exit_contract():
    text = asset("ci/verify.yml").read_text()
    assert "name: verify\non:\n  push:\n    branches: ['**']\n  pull_request:\n" in text
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
    assert "empty_tree" not in text
    assert 'git fetch --no-tags origin "$base"' in text
    assert 'git cat-file -e "$base^{tree}"' in text
    assert 'printf \'sha=%s\\n\' "$base" >> "$GITHUB_OUTPUT"' in text
    assert 'printf \'recheck=%s\\n\' "$recheck" >> "$GITHUB_OUTPUT"' in text
    assert "BASE: ${{ steps.base.outputs.sha }}" in text
    assert "RECHECK: ${{ steps.base.outputs.recheck }}" in text
    assert (
        '--git-base "$BASE" --git-candidate HEAD --recheck-commits "$RECHECK"'
    ) in text
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


def _verify_steps():
    import yaml

    workflow = yaml.safe_load(asset("ci/verify.yml").read_text())
    # YAML 1.1 reads the bare key `on` as True.
    triggers = workflow[True]
    steps = {
        step.get("id", step.get("name")): step
        for step in workflow["jobs"]["offline-verify"]["steps"]
    }
    return triggers, steps


def test_verify_workflow_runs_on_branches_and_pull_requests_never_on_a_tag():
    """R27 (a): publish pushes every publication tag (push.followTags); a
    `branches` filter alone leaves tag pushes out, so a tag runs nothing."""
    triggers, _steps = _verify_steps()
    assert triggers == {"push": {"branches": ["**"]}, "pull_request": None}


def test_a_created_branch_replays_from_publishs_base_not_the_empty_tree(
    net_vault, tmp_path_factory, capsys
):
    """R27 (b) (F2), R30 (P50): a created ref arrives with `before` all zeros.
    The base step gives the leg HEAD (an empty range) and the replay
    `publish`, which the CLI resolves through `publish.recheck_base` alone.
    The run raises the seed's own unacked recapture and a bypass after the
    seed, each at its commit, and leaves a pre-CI, never-acked recapture
    alone, as publish does; the empty-tree base this replaced raises that
    one too."""
    import shlex

    from research_vault.__main__ import main
    from tests.conftest import must_replace
    from tests.test_verify_cli import _ack_standing_citation_key, _commit_all

    def recapture(old, new, at):
        text = must_replace(note.read_text(), old, new)
        note.write_text(must_replace(text, *at))

    _ack_standing_citation_key(net_vault)
    for empty in ("system/templates", "system/bases"):  # so HEAD's tree has them
        (net_vault / empty / ".gitkeep").write_text("")
    note = net_vault / "literature" / "smith2020.md"
    recapture(
        'DOI: "10.1000/xyz"\n',
        'DOI: "10.1000/xyz"\nvolume: "3"\n',
        ('at: "2026-08-16T09:00:00Z"', 'at: "2026-08-17T09:00:00Z"'),
    )
    _commit_all(net_vault, "a recapture before CI, never acknowledged")
    recapture(
        'volume: "3"\n',
        'volume: "3"\nissue: "2"\n',
        ('at: "2026-08-17T09:00:00Z"', 'at: "2026-08-18T09:00:00Z"'),
    )
    workflows = net_vault / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "verify.yml").write_bytes(asset("ci/verify.yml").read_bytes())
    seed = _commit_all(net_vault, "add CI, with a recapture never acknowledged")
    note.write_text(
        must_replace(note.read_text(), 'DOI: "10.1000/xyz"', 'DOI: "10.1000/abc"')
    )
    bypassed = _commit_all(net_vault, "a hand edit, bypassed")
    _triggers, steps = _verify_steps()
    # Outside the vault: the fixture vault is `tmp_path` itself, and CI's
    # output file lives outside its checkout.
    outputs = tmp_path_factory.mktemp("runner") / "github-output"
    env = {
        **os.environ,
        "EVENT_NAME": "push",
        "PUSH_BASE": "0" * 40,
        "PR_BASE": "",
        "GITHUB_OUTPUT": str(outputs),
    }
    subprocess.run(
        ["bash", "-c", steps["base"]["run"]], cwd=net_vault, env=env, check=True
    )
    resolved = dict(line.split("=", 1) for line in outputs.read_text().splitlines())
    assert resolved == {"sha": bypassed, "recheck": "publish"}
    (command,) = [
        line.strip()
        for line in steps["Verify committed changes"]["run"].splitlines()
        if line.strip().startswith("python -m research_vault verify")
    ]
    command = must_replace(command, '"$BASE"', resolved["sha"])
    argv = shlex.split(must_replace(command, '"$RECHECK"', resolved["recheck"]))[3:]
    assert argv[argv.index("--recheck-commits") + 1] == "publish"
    argv[argv.index("--vault") + 1] = str(net_vault)
    capsys.readouterr()
    assert main(argv) == 1
    out = capsys.readouterr().out.splitlines()
    assert any(
        line.startswith(f"re-check: {seed} and every commit after it") for line in out
    )
    rows = [line for line in out if line.startswith("UNMATCHED")]
    target = "path-bytes:literature/smith2020.md"
    assert (
        f'UNMATCHED capture-monitor {target} — drift — issue added: "2" (commit {seed[:7]})'
        in rows
    )
    assert (
        f"UNMATCHED evidence-layer {target} — drift — DOI changed without writer "
        f"attestation (commit {bypassed[:7]})"
    ) in rows
    assert not [line for line in rows if "volume added" in line]
    # The empty-tree base this replaced replays the whole history and turns
    # the pre-CI recapture into a closing row too.
    empty = subprocess.run(
        ["git", "hash-object", "-t", "tree", "/dev/null"],
        cwd=net_vault,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    # A fresh checkout, as each CI run gets: the run above filed its rows.
    subprocess.run(["git", "reset", "-q", "--hard"], cwd=net_vault, check=True)
    whole = [*argv[: argv.index("--git-base")], "--git-base", empty]
    whole += ["--git-candidate", "HEAD", "--recheck-commits", empty]
    assert main(whole) == 1
    assert any("volume added" in line for line in capsys.readouterr().out.splitlines())


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


def test_readme_embeds_the_obsidian_plugin_declaration_verbatim():
    table = asset("obsidian-plugins.md").read_text()
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


def _roster_rules(dir_names, prefixes, files):
    return sorted(
        [f"Edit(/{name}/**)" for name in dir_names]
        + [f"Edit(/{prefix}/**)" for prefix in prefixes]
        + [f"Edit(/{path})" for path in files]
    )


def test_seeded_deny_rules_equal_the_guards_roster():
    """§5.7: the nine Edit(...) deny rules are the roster, spelled the way
    Claude Code resolves a /-led project path. One source: the guard."""
    import json

    guard = _guard_constants()
    expected = _roster_rules(
        guard.MACHINE_SURFACE_DIR_NAMES,
        [prefix.as_posix() for prefix in guard.MACHINE_SURFACE_PREFIXES],
        [path.as_posix() for path in guard.MACHINE_SURFACE_FILES],
    )
    assert len(expected) == 9
    settings = json.loads(asset("vault/claude/settings.json").read_text())
    assert settings == {"permissions": {"deny": expected}}
    assert asset("vault/claude/settings.json").read_text() == (
        json.dumps(settings, indent=2) + "\n"
    )


def test_doctors_roster_copy_equals_the_guards_constants():
    """A pip install has no hooks/ beside the package, so doctor repeats the
    roster; this pins the copy against the guard so the two cannot drift."""
    from research_vault import doctor

    guard = _guard_constants()
    assert set(doctor._ROSTER_DIR_NAMES) == set(guard.MACHINE_SURFACE_DIR_NAMES)
    assert set(doctor._ROSTER_PREFIXES) == {
        prefix.as_posix() for prefix in guard.MACHINE_SURFACE_PREFIXES
    }
    assert set(doctor._ROSTER_FILES) == {
        path.as_posix() for path in guard.MACHINE_SURFACE_FILES
    }


def test_expected_deny_rules_falls_back_to_the_copy_when_hooks_is_absent(monkeypatch):
    from research_vault import doctor

    with_guard = doctor.expected_deny_rules()
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    assert doctor.expected_deny_rules() == with_guard
    assert doctor.expected_deny_rules() == _roster_rules(
        doctor._ROSTER_DIR_NAMES, doctor._ROSTER_PREFIXES, doctor._ROSTER_FILES
    )


def test_package_data_glob_reaches_every_template_file():
    """Designs cluster 6(a): setuptools' build_py uses the standard-library glob,
    which skips dot entries at any depth. The hermetic form of that call must
    equal the rglob file set, and no template path may carry a dot component."""
    import glob

    globbed = {
        Path(p).relative_to(TEMPLATES).as_posix()
        # the stdlib glob is the call under test (setuptools build_py)
        for p in glob.glob(str(TEMPLATES / "**" / "*"), recursive=True)  # noqa: PTH207
        if Path(p).is_file()
    }
    walked = {
        p.relative_to(TEMPLATES).as_posix() for p in TEMPLATES.rglob("*") if p.is_file()
    }
    assert globbed == walked
    dotted = [p for p in walked if any(part.startswith(".") for part in p.split("/"))]
    assert dotted == []


def test_no_markdown_under_the_obsidian_seed():
    """verify walks every *.md in a vault; the seed is excluded there (#194) but a
    plugin README in the package would be shipped for nothing."""
    seed = TEMPLATES / "obsidian"
    assert seed.is_dir()
    assert list(seed.rglob("*.md")) == []


SEED = TEMPLATES / "obsidian"
CORE_IDS = {
    "file-explorer",
    "global-search",
    "switcher",
    "graph",
    "backlink",
    "canvas",
    "outgoing-link",
    "tag-pane",
    "properties",
    "page-preview",
    "daily-notes",
    "templates",
    "note-composer",
    "command-palette",
    "slash-command",
    "editor-status",
    "bookmarks",
    "markdown-importer",
    "zk-prefixer",
    "random-note",
    "outline",
    "word-count",
    "slides",
    "audio-recorder",
    "workspaces",
    "file-recovery",
    "publish",
    "sync",
    "bases",
    "footnotes",
    "webviewer",
}
CORE_OFF = {"properties", "canvas", "sync", "publish", "markdown-importer"}


def test_core_plugins_json_names_every_registered_id_in_object_form():
    """Screen B §7.4: a missing id makes Obsidian rewrite the file on first open."""
    core = json.loads((SEED / "core-plugins.json").read_text())
    assert set(core) == CORE_IDS
    assert {k for k, v in core.items() if v is False} == CORE_OFF
    assert all(isinstance(v, bool) for v in core.values())


def test_app_json_keeps_new_notes_links_and_attachments_where_detection_reaches():
    app = json.loads((SEED / "app.json").read_text())
    assert app == {
        "alwaysUpdateLinks": True,
        "attachmentFolderPath": "inbox",
        "newFileFolderPath": "inbox",
        "newFileLocation": "folder",
        "newLinkFormat": "absolute",
        "useMarkdownLinks": True,
    }
    assert "userIgnoreFilters" not in app  # literature/ stays visible (§4.5)


def test_core_settings_files_route_new_notes_off_the_machine_folders():
    assert json.loads((SEED / "daily-notes.json").read_text()) == {
        "folder": "daily",
        "format": "YYYY-MM-DD",
        "template": "system/templates/daily",
    }
    assert json.loads((SEED / "templates.json").read_text()) == {
        "folder": "system/templates"
    }
    assert json.loads((SEED / "zk-prefixer.json").read_text()) == {
        "folder": "inbox",
        "format": "YYYYMMDDHHmm",
        "template": "",
    }
    assert json.loads((SEED / "webviewer.json").read_text()) == {
        "markdownPath": "inbox"
    }


def test_community_plugins_json_lists_exactly_the_vendored_ids():
    from research_vault import obsidian_plugins

    declaration = obsidian_plugins.declared()
    seeded = sorted(p.plugin_id for p in declaration.plugins if p.need == "seeded")
    assert json.loads((SEED / "community-plugins.json").read_text()) == seeded
    for plugin in declaration.plugins:
        folder = SEED / "plugins" / plugin.plugin_id
        if plugin.need == "seeded":
            # Task 3 vendors them
            assert (folder / "manifest.json").is_file(), plugin.plugin_id
        elif plugin.need == "recommended":
            # data.json only loads nothing (Q10)
            assert not (folder / "manifest.json").exists(), plugin.plugin_id
        else:
            assert not folder.exists(), plugin.plugin_id


def test_seeded_settings_satisfy_the_declaration():
    """Designs cluster 5(d): a repo test asserts the seed's own files meet the
    declared keys, so doctor's drift notes on a fresh vault are empty."""
    from research_vault import obsidian_plugins

    declaration = obsidian_plugins.declared()
    for setting in declaration.settings:
        if setting.file == "data.json":
            plugin = declaration.by_name[setting.plugin]
            path = SEED / "plugins" / plugin.plugin_id / "data.json"
        else:
            path = SEED / setting.file
        value = obsidian_plugins.read_key(path, setting.key)
        assert value in setting.accepted, (setting, value)


# Obsidian 1.15.1's Bases File properties, `FILE_PROPERTIES` in `app.js`
# (read from obsidian-1.15.1.asar, 2026-11-27, Plan E Task 6 Step 5). None
# reads a note body (#202): `file.content` is absent.
BASES_FILE_PROPERTIES = frozenset(
    {
        "file.file",
        "file.name",
        "file.basename",
        "file.fullname",
        "file.path",
        "file.folder",
        "file.ext",
        "file.ctime",
        "file.mtime",
        "file.size",
        "file.links",
        "file.backlinks",
        "file.embeds",
        "file.tags",
    }
)
# `file.<name>` not continued by a word character or a dot on the left. A name
# followed by `(` is a method call (`file.hasTag(`, `file.inFolder(`), which
# the property list does not cover, so it is left out of the check.
_BASES_FILE_KEY = re.compile(r"(?<![\w.])(file\.[A-Za-z_]\w*)(?!\w)(\s*\()?")


def _bases_file_properties(text):
    return {key for key, call in _BASES_FILE_KEY.findall(text) if not call}


def test_bases_file_property_reader_skips_method_calls():
    text = (
        'file.name, file.hasTag("x"), file.inFolder ("y"), note.file.size, file.content'
    )
    assert _bases_file_properties(text) == {"file.name", "file.content"}


def test_every_seeded_base_parses_and_reads_no_note_body():
    import yaml

    for base in (TEMPLATES / "vault" / "system" / "bases").glob("*.base"):
        text = base.read_text()
        document = yaml.safe_load(text)
        assert "views" in document, base
        # #202: Bases cannot read bodies; every File key is one Obsidian defines
        assert _bases_file_properties(text) <= BASES_FILE_PROPERTIES, base
    assert not (
        TEMPLATES / "vault" / "system" / "bases" / "open-questions.base"
    ).exists()


def test_index_uses_a_core_search_block_for_open_questions():
    text = asset("vault/index.md").read_text()
    assert '```query\npath:projects/ "(open-question)"\n```' in text
    assert "open-questions.base" not in text


def _declaration_text(plugin_rows, setting_rows=()):
    return (
        "### Plugins\n\n| Plugin | Id | Need | Pin | Licence | Workflows |\n| - | - | - | - | - | - |\n"
        + "".join(f"{row}\n" for row in plugin_rows)
        + "\n### Declared plugin settings\n\n| Plugin | File | Key | Accepted |\n| - | - | - | - |\n"
        + "".join(f"{row}\n" for row in setting_rows)
    )


@pytest.mark.parametrize(
    ("plugin_rows", "setting_rows", "fault"),
    [
        (["| A | `a` | vendored | 1.0 | MIT | x |"], [], "need"),
        (["| A | `a` | seeded | — | MIT | x |"], [], "no pin"),
        (["| A | a | seeded | 1.0 | MIT | x |"], [], "cell"),
        (
            ["| A | `a` | seeded | 1.0 | MIT | x |"],
            ["| B | `data.json` | `k` | `true` |"],
            "no declared plugin",
        ),
        (
            ["| A | `a` | seeded | 1.0 | MIT | x |"],
            ["| Core | `data.json` | `k` | `true` |"],
            "cannot declare",
        ),
        (
            ["| A | `a` | seeded | 1.0 | MIT | x |"],
            ["| A | `app.json` | `k` | `true` |"],
            "cannot declare",
        ),
        (
            ["| A | `a` | seeded | 1.0 | MIT | x |"],
            ["| A | `data.json` | `k` | `yes` |"],
            "accepted literal",
        ),
        (
            ["| A | `a` | seeded | 1.0 | MIT | x |"],
            ["| A | `data.json` | `k` | `true` or `false` |"],
            "accepted literals",
        ),
        (
            [
                "| A | `a` | seeded | 1.0 | MIT | x |",
                "| B | `a` | seeded | 1.0 | MIT | x |",
            ],
            [],
            "twice",
        ),
    ],
)
def test_the_plugin_declaration_reader_refuses_a_row_it_cannot_read(
    plugin_rows, setting_rows, fault
):
    from research_vault import obsidian_plugins

    with pytest.raises(ValueError, match=fault):
        obsidian_plugins.parse(_declaration_text(plugin_rows, setting_rows))


def test_the_plugin_declaration_reader_normalises_literals_and_excluded_rows():
    from research_vault import obsidian_plugins

    declaration = obsidian_plugins.parse(
        _declaration_text(
            [
                "| A | `a` | seeded | 1.0 | MIT | x |",
                "| X | `x` | excluded | — | — | — |",
            ],
            [
                "| A | `data.json` | `k` | `[ ]`, `unset` |",
                '| Core | `app.json` | `j` | `"v"` |',
            ],
        )
    )
    assert declaration.by_id["x"].pin is None
    assert declaration.by_id["x"].licence is None
    assert declaration.settings_for("a") == [
        obsidian_plugins.Setting("A", "data.json", "k", ("[]", "unset"))
    ]
    assert declaration.settings[1].accepted == ('"v"',)


def test_the_plugin_declaration_reader_keeps_a_data_row_named_like_the_header():
    """Only the whole header row is skipped; a plugin called `Plugin` is data,
    and a literal holding `, ` is one literal."""
    from research_vault import obsidian_plugins

    declaration = obsidian_plugins.parse(
        _declaration_text(
            ["| Plugin | `p` | seeded | 1.0 | MIT | x |"],
            ['| Plugin | `data.json` | `k` | `["a", "b"]`, `unset` |'],
        )
    )
    assert declaration.by_id["p"].name == "Plugin"
    assert declaration.settings_for("p") == [
        obsidian_plugins.Setting("Plugin", "data.json", "k", ('["a","b"]', "unset"))
    ]


def test_read_key_follows_a_dotted_path_and_says_unset_or_unreadable(tmp_path):
    from research_vault import obsidian_plugins

    path = tmp_path / "data.json"
    assert obsidian_plugins.read_key(path, "a") == "unset"
    path.write_text(
        '{"homepages": {"Main Homepage": {"autoCreate": false}}, "l": [1, 2], "s": "é"}'
    )
    assert (
        obsidian_plugins.read_key(path, "homepages.Main Homepage.autoCreate") == "false"
    )
    assert obsidian_plugins.read_key(path, "l") == "[1,2]"
    assert obsidian_plugins.read_key(path, "s") == '"é"'
    assert obsidian_plugins.read_key(path, "l.0") == "unset"
    assert obsidian_plugins.read_key(path, "homepages.Other") == "unset"
    path.write_text("{")
    with pytest.raises(obsidian_plugins.ConfigUnreadableError, match=r"data\.json"):
        obsidian_plugins.read_key(path, "a")


@pytest.mark.parametrize(
    ("demotion_row", "fault"),
    [
        ("| A | 1.0 | Obsidian 1 | e | 2026-11-27 |", "declared seeded"),
        ("| B | 1.0 | Obsidian 1 | e | 2026-11-27 |", "no vendorable plugin"),
        ("| X | 1.0 | Obsidian 1 | e | 2026-11-27 |", "no vendorable plugin"),
        ("| R | 1.0 | Obsidian 1 | e | 27 Nov |", "demotion cells"),
        ("| R | 1.0 | Obsidian 1 | | 2026-11-27 |", "demotion cells"),
    ],
)
def test_the_plugin_declaration_reader_refuses_a_demotion_it_cannot_apply(
    demotion_row, fault
):
    from research_vault import obsidian_plugins

    text = _declaration_text(
        [
            "| A | `a` | seeded | 1.0 | MIT | x |",
            "| R | `r` | recommended | 1.0 | MIT | x |",
            "| X | `x` | excluded | — | — | — |",
        ]
    ) + (
        "\n### Load demotions\n\n| Plugin | Version | Host | Error | Measured |\n"
        f"| - | - | - | - | - |\n{demotion_row}\n"
    )
    with pytest.raises(ValueError, match=fault):
        obsidian_plugins.parse(text)


def test_the_plugin_declaration_reader_reads_a_load_demotion():
    from research_vault import obsidian_plugins

    text = _declaration_text(["| R | `r` | recommended | 1.0 | MIT | x |"]) + (
        "\n### Load demotions\n\n| Plugin | Version | Host | Error | Measured |\n"
        "| - | - | - | - | - |\n| R | 1.0 | Obsidian 1 | it's broken | 2026-11-27 |\n"
    )
    declaration = obsidian_plugins.parse(text)
    assert declaration.demotion_for("r") == obsidian_plugins.Demotion(
        "R", "1.0", "Obsidian 1", "it's broken", "2026-11-27"
    )


def test_a_load_demotion_applies_to_every_tag_of_its_plugin():
    """R66: the row is keyed by the version measured, and a pin bump does not
    lift it; only removing the row does."""
    from research_vault import obsidian_plugins

    text = _declaration_text(["| R | `r` | recommended | 2.0 | MIT | x |"]) + (
        "\n### Load demotions\n\n| Plugin | Version | Host | Error | Measured |\n"
        "| - | - | - | - | - |\n| R | 1.0 | Obsidian 1 | broken | 2026-11-27 |\n"
    )
    demotion = obsidian_plugins.parse(text).demotion_for("r")
    assert demotion is not None
    assert demotion.version == "1.0"


def test_the_load_demotions_lead_says_a_row_outlives_a_pin_bump():
    table = asset("obsidian-plugins.md").read_text()
    lead = table.split("### Load demotions", 1)[1].split("|", 1)[0]
    assert "applies until a measured load clears it" in lead
    assert "a pin bump does not lift it" in lead


def test_a_demotion_error_cannot_hold_the_records_separator():
    """Review 5(c): the vendoring script splits SOURCE.json's method on it."""
    from research_vault import obsidian_plugins

    text = _declaration_text(["| R | `r` | recommended | 1.0 | MIT | x |"]) + (
        "\n### Load demotions\n\n| Plugin | Version | Host | Error | Measured |\n"
        "| - | - | - | - | - |\n| R | 1.0 | Obsidian 1 | a; licence screen: b | 2026-11-27 |\n"
    )
    with pytest.raises(ValueError, match="licence screen"):
        obsidian_plugins.parse(text)
