import json
import os
import re
import subprocess
from pathlib import Path

from knowledge_harness import frontmatter

REPO = Path(__file__).resolve().parents[1]
TEMPLATES = REPO / "knowledge_harness" / "templates"

EXPECTED_PATHS = {
    "vault/index.md",
    "vault/log.md",
    "vault/AGENTS.md",
    "vault/inbox/review-queue.md",
    "vault/synthesis/index.md",
    "vault/system/glossary.md",
    "vault/system/templates/literature.md",
    "vault/system/templates/synthesis.md",
    "vault/system/templates/project.md",
    "vault/system/templates/daily.md",
    "vault/system/bases/open-questions.base",
    "vault/system/bases/trust-tier.base",
    "vault/gitignore",
    "harness/machine.json.example",
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
    assert root_data == {"type": "index", "okf_version": "0.2"}
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
        '---\ntype: "index"\nokf_version: "0.2"\n---\n'
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
    # against CLOSING_BY_SURFACE (knowledge_harness/verify.py) and
    # lint_append_only's startswith predicate (knowledge_harness/lints.py)
    # before landing.
    assert asset("vault/AGENTS.md").read_text() == (
        '---\ntype: "guide"\n---\n'
        "# Vault agents guide\n\n"
        "This is a knowledge-harness vault. `literatures/`, `log/`, `log.md`, "
        "and `inbox/review-queue.md` are machine-written — the CLI writes "
        "them; don't edit them by hand.\n\n"
        "Evidence is admitted through Zotero and projected into `literatures/` — "
        "evidence notes exist only by projection, never by hand. Read "
        "`synthesis/index.md` and recent `log/` entries before editing; review "
        "findings live in `inbox/review-queue.md`.\n\n"
        "Prefer the knowledge-harness skills over generic drafting, even for "
        "free-form requests. Run `evidence-conventions` for claim syntax.\n\n"
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
        "Text between `%%hk-managed%%` markers is regenerated by the bridge — "
        "edits there do not survive. Free prose below the managed region is "
        "yours and persists.\n\n"
        "Machine surfaces (`log/`, `inbox/review-queue.md`, managed regions, "
        "`system/bibliography.json`) are owner-written: hand or tool edits are "
        "regenerated away or raise a finding.\n\n"
        "Formatters are writers too. Each machine surface has one owner and a "
        "byte contract, and the trust machinery rejects foreign writers "
        "mechanically — so running a Markdown or JSON formatter across the vault "
        "is what sets the alarms off. This paragraph explains the alarms; it is "
        "not what enforces them.\n\n"
        "`.harness/` is machine-local: nothing in it travels with the vault.\n"
    )
    assert asset("vault/inbox/review-queue.md").read_text() == (
        '---\ntype: "review-queue"\n---\n'
    )
    assert asset("vault/synthesis/index.md").read_text() == "# Synthesis index\n"
    assert asset("vault/system/templates/literature.md").read_text() == (
        '---\ncitekey: "{{CITEKEY}}"\ntype: "literature"\n'
        'accessed: "{{TODAY}}"\nfixity-sha256:\n'
        'managed-sha256: "{{MANAGED_SHA256}}"\nstatus: "unscreened"\n'
        'generated: {by: "{{ACTOR}}", at: "{{NOW}}"}\n---\n'
        "%%hk-managed%%\n# {{TITLE}}\n%%/hk-managed%%\n\n## Notes\n"
    )
    for kind in ("synthesis", "project"):
        assert asset(f"vault/system/templates/{kind}.md").read_text() == (
            f'---\ntitle: "{{{{TITLE}}}}"\ntype: "{kind}"\n'
            'status: "draft"\ngenerated: {by: "{{ACTOR}}", at: "{{NOW}}"}\n---\n'
        )
    assert asset("vault/system/templates/daily.md").read_text() == (
        '---\ntype: "daily"\n---\n<!-- log/YYYY-MM-DD.md; append-only -->\n'
    )
    assert asset("vault/system/glossary.md").read_text() == (
        "---\n"
        'type: "guide"\n'
        "---\n"
        "# Vault glossary\n\n"
        "Trust-first academic research on this vault: every claim traceable to a "
        "real source, verified by mechanical checks. This page defines the words "
        "this vault's notes, folders, and fields use.\n\n"
        "## Vault\n\n"
        "**Vault**: A private git repository of markdown notes — the researcher's "
        "durable knowledge store, packaged to survive its tools (currently as an "
        "OKF — Open Knowledge Format — bundle).\n"
        "_Avoid_: knowledge base, second brain\n\n"
        "**Evidence layer**: The vault's machine-projected record of admitted "
        "sources (`literatures/`); never free-written.\n"
        "_Avoid_: sources folder, references layer\n\n"
        "**Synthesis layer**: The LLM-maintained topic pages (`synthesis/`) that "
        "arrange claims across sources; freely rewritable because it asserts "
        "arrangement, not evidence.\n"
        "_Avoid_: atlas, wiki, topic pages\n\n"
        "**Literature note**: The vault projection of one Zotero item, filename = "
        "citekey; a managed region above free prose.\n"
        "_Avoid_: source note, paper note, reference note\n\n"
        "**Synthesis note**: One page of the synthesis layer, carrying "
        "block-anchored claims with stance links.\n"
        "_Avoid_: topic page (collides with OpenAlex topics), evergreen note, "
        "concept page\n\n"
        "**Project**: A manuscript or deliverable in progress "
        "(`projects/<name>/`), with a publication lifecycle.\n"
        "_Avoid_: effort, draft folder\n\n"
        "**Inbox**: Fleeting captures and the review queue (`inbox/`); never an "
        "admission path for citable sources.\n"
        "_Avoid_: `+`, capture folder\n\n"
        "**Log**: The append-only per-day activity record (`log/`), summarized in "
        "root `log.md`.\n"
        "_Avoid_: calendar, journal, daily notes folder\n\n"
        "**System folder**: The vault's support artifacts (`system/`): templates, "
        "bases, the bibliography export. Sorts last, out of the knowledge "
        "folders' way.\n"
        "_Avoid_: x (old name), assets, meta\n\n"
        "**Managed region**: The bridge-regenerated span of a literature note "
        "between `%%hk-managed%%` markers; never hand-edited.\n"
        "_Avoid_: generated section, machine block\n\n"
        "## Evidence and claims\n\n"
        "**Item**: A bibliographic record in Zotero/CSL terms — the thing a "
        "citekey names.\n"
        "_Avoid_: work (OpenAlex sense), paper (narrower than the corpus)\n\n"
        "**Source**: The cited document itself, in the scholarly sense "
        "(primary/secondary source).\n"
        '_Avoid_: using "source" for a journal or repository — that is a '
        "**venue**\n\n"
        "**Venue**: The journal, repository, or outlet an item appeared in.\n"
        '_Avoid_: OpenAlex\'s "source" sense in our prose\n\n'
        "**Citekey**: The stable, human-readable key (Better BibTeX) joining "
        "prose citations, filenames, and the bibliography.\n"
        "_Avoid_: reference ID, bibkey\n\n"
        "**Claim**: One assertion carried by a note line, tagged with its "
        "evidence boundary and anchored for linking.\n"
        "_Avoid_: statement, fact\n\n"
        "**Evidence-boundary tag**: The per-claim marker of epistemic status — "
        "quote, paraphrase, inference, or open-question.\n"
        "_Avoid_: claim type, epistemic label\n\n"
        "**Claim link**: The global address of a claim: `citekey#^claim-id` (an "
        "Obsidian block link).\n"
        "_Avoid_: claim address, claim ID (that is only the anchor fragment)\n\n"
        "**Stance link**: A typed claim-to-claim relation — `supports` or "
        "`disputes` (CiTO senses).\n"
        "_Avoid_: supported-by/contested-by (old names), related links\n\n"
        "**Admission**: The human act of accepting a source into Zotero — the "
        "only way anything becomes citable.\n"
        "_Avoid_: import (that is the projection step that follows), ingestion\n\n"
        "**Import**: The machine projection of an admitted item into the evidence "
        "layer — a literature note rendered from Zotero, never authored.\n"
        "_Avoid_: admission (that is the human act before), sync\n\n"
        "**Bibliography export**: The citekey universe: the Better BibTeX "
        "auto-export at `system/bibliography.json`, written only by BBT, that "
        "citations, filenames, and checks all join against.\n"
        "_Avoid_: bibliography file, reference list\n\n"
        "**Screening state**: A literature note's PRISMA-style status: "
        "unscreened, included, excluded, or superseded.\n"
        "_Avoid_: unreviewed/active/rejected (old values), review status\n\n"
        "## Verification\n\n"
        "**Check**: One mechanical verification (citekey exists, DOI resolves, "
        "quote matches, update-notice scan, …).\n"
        "_Avoid_: test, validation\n\n"
        "**Four-state result**: A check's outcome: MATCHED, UNMATCHED, "
        "UNREACHABLE (could not run — never guilt), or SKIPPED (does not apply — "
        "automatic only).\n"
        "_Avoid_: pass/fail, pytest vocabulary in vault prose\n\n"
        "**Verified event**: The dated, attributed record of which check passed, "
        "appended to a note; only MATCHED mints one.\n"
        "_Avoid_: verification log entry, audit record\n\n"
        "**Trust tier**: A note's derived standing: unverified → "
        "machine-confirmed → human-reviewed (cumulative).\n"
        "_Avoid_: confidence level (that is a per-claim field), quality score\n\n"
        "**Review inbox**: The append-only findings file "
        "(`inbox/review-queue.md`) every warn, hold, and alert writes to; drained "
        "at project orientation.\n"
        "_Avoid_: issue list, warning log\n\n"
        "**Acknowledgment**: A human's standing, hash-scoped acceptance of a "
        "finding — the only way to bypass a check that would otherwise block.\n"
        "_Avoid_: dismissal, override (an ack keeps the record; it never deletes)\n\n"
        "**Publish gate**: The armed, fail-closed verification boundary a project "
        "crosses at publish; inert unless armed.\n"
        "_Avoid_: release check, CI gate (CI is the async auditor, not the gate)\n\n"
        "**Update notice**: A registry's post-publication signal about an item "
        "(retraction, correction, expression of concern, …), recorded "
        "bi-temporally.\n"
        "_Avoid_: retraction flag (one class of notice, not the concept)\n"
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

    machine = json.loads(asset("harness/machine.json.example").read_text())
    assert machine == {
        "mailto": "you@example.edu",
        "path_map": {"D:\\Zotero\\": "/mnt/d/Zotero/"},
    }
    gitignore = asset("vault/gitignore").read_text()
    assert ".harness/\n" in gitignore
    assert ".obsidian/workspace*\n" in gitignore


def test_precommit_hook_is_executable_and_has_exact_contract():
    hook = asset("git/pre-commit")
    text = hook.read_text()
    assert hook.stat().st_mode & os.X_OK
    subprocess.run(["sh", "-n", str(hook)], check=True)
    assert (
        'python3 -m knowledge_harness verify --vault "$vault" --offline --surface commit --git-base "$git_base" --git-candidate index'
        in text
    )
    assert 'git_base="$(git rev-parse --verify HEAD 2>/dev/null)"' in text
    assert "git hash-object -w -t tree /dev/null" in text
    assert 'git cat-file -e "$git_base^{tree}"' in text
    assert "git commit --no-verify" in text
    assert 'if ! python3 -c "import knowledge_harness" 2>/dev/null; then' in text
    assert (
        "pre-commit: knowledge_harness is not importable; CI will replay verification."
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
        '--offline --surface audit --git-candidate worktree --rw-csv "$RUNNER_TEMP/rw.csv" --changed-paths-file "$RUNNER_TEMP/harness-changed-paths" --commit-projected "chore: rw-batch findings"'
        in text
    )
    assert "No verifier-owned changes." in text
    assert 'git config user.name "harness-ci"' in text
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
