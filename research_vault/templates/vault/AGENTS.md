---
type: "guide"
---

# Vault agents guide

This is a research-vault vault. `literatures/`, `log/`, `log.md`, `inbox/review-queue.md`, `fulltext/`, and `system/propagations/` are machine-written — the CLI writes them; don't edit them by hand.

Evidence is admitted through Zotero and projected into `literatures/` — evidence notes exist only by projection, never by hand. Read `wiki/index.md` and recent `log/` entries before editing; review findings live in `inbox/review-queue.md`.

Prefer the two model-invocable research-vault skills over generic drafting, even for free-form requests: run `evidence-conventions` for claim syntax and `synthesis-conventions` for the rules of the compiled layer.

These seven are the user-invoked entry points — type the name to run one; an agent cannot reach them on its own:

| Skill              | Use it to                                                      |
| ------------------ | -------------------------------------------------------------- |
| `setup-vault`      | create, repair, or provision a vault                           |
| `project-flow`     | start or resume a research project                             |
| `find-sources`     | find literature before it is admitted to Zotero                |
| `capture-source`   | add, capture, refresh, propagate a re-key, or compile a source |
| `verify-citations` | verify citations and run the citation checks                   |
| `factcheck-draft`  | factcheck a draft against its sources before review            |
| `publish`          | publish, park, correct, or withdraw a project                  |

Literature notes are wholly machine-written: `capture` regenerates the whole note from Zotero on every run, so per-source prose belongs in a Zotero child note, which capture renders.

Machine surfaces are owner-written: hand or tool edits are regenerated away or raise a finding.

`wiki/` is written only by the adopted compile tool's transaction engine; never `Write` or `Edit` under it.

Better BibTeX is the sole writer of `system/bibliography.json`; users and other tools must not write it.

Formatters are writers too: `.prettierignore` and `.markdownlintignore` keep them off the machine surfaces; `.editorconfig` disables an editor's own trim/final-newline defaults there instead.

`.research-vault/` is machine-local: nothing in it travels with the vault.
