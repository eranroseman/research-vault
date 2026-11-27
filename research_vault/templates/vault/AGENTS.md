---
type: "guide"
---

# Vault agents guide

This is a research-vault vault. `literature/`, `log/`, `log.md`, `inbox/review-queue.md`, `system/bibliography.json`, `fulltext/`, `system/propagations/`, and `system/compiled-pages.json` are machine-written — the CLI writes them; don't edit them by hand.

Evidence is added to Zotero and projected into `literature/` — evidence notes exist only by projection, never by hand. Read `wiki/index.md` and recent `log/` entries before editing; review findings live in `inbox/review-queue.md`.

Prefer the two model-invocable research-vault skills over generic drafting, even for free-form requests: run `evidence-conventions` for claim syntax and `synthesis-conventions` for the rules of the compiled layer.

These eight are the user-invoked entry points — type the name to run one; an agent cannot reach them on its own:

| Skill                     | Use it to                                                      |
| ------------------------- | -------------------------------------------------------------- |
| `setup-vault`             | create, repair, or provision a vault                           |
| `project-flow`            | start or resume a research project                             |
| `find-sources`            | find literature before it is added to Zotero                   |
| `capture-source`          | add, capture, refresh, propagate a re-key, or compile a source |
| `verify-citations`        | verify citations and run the citation checks                   |
| `factcheck-draft`         | factcheck a draft against its sources before review            |
| `publish`                 | publish, park, correct, or withdraw a project                  |
| `paper-critical-analysis` | write an in-depth critical analysis report of one paper        |

Literature notes are wholly machine-written: `capture` regenerates the whole note from Zotero on every run, so per-source prose belongs in a Zotero child note, which capture renders.

Machine surfaces are owner-written, and changes to them are detected: a hand or shell edit to `literature/`, `wiki/`, root `log.md`, `inbox/review-queue.md`, `system/bibliography.json` or `system/propagations/` raises a finding at commit, and an edit to `fulltext/` at publish. The seeded `.claude/settings.json` refuses the common shell forms of such a write (redirects, `tee`, `sed -i`, `cp`, `mv`, `touch`, `rm`) in a session started at the vault root; an interpreter one-liner, a script or a git restore is caught by detection, not refused. What detection does not reach: an in-format append to `log/` committed together with a regenerated `log.md`, an append to the review queue, deleting a `fulltext/` file (a fresh clone has none), the non-capture keys a literature note carries forward, and a page and its record entry co-edited through an interpreter, either committed with --no-verify or beside planted local evidence (a compile journal under `.vault-meta/transactions/` or a seal-store copy under `.vault-meta/research-vault/`), which the hook must accept because a seal that normalised links, or a reseal chain between commits, has no other evidence; CI and the replay cannot tell either route from a legitimate seal.

`wiki/` is written only by the adopted compile tool's transaction engine; never `Write` or `Edit` under it. A hand edit under `wiki/` is reported against the compiled-page record, `system/compiled-pages.json`, and holds the commit.

`capture` is the sole writer of the CSL file `system/bibliography.json`, rendered from Better BibTeX; users and other tools must not write it.

Formatters are writers too: `.prettierignore` and `.markdownlintignore` keep them off the machine surfaces; `.editorconfig` disables an editor's own trim/final-newline defaults there instead.

`.research-vault/` is machine-local: nothing in it travels with the vault.
