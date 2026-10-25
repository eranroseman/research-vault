# Attributions

research-vault is an original work, MIT licensed. The following third-party
guidelines, tools, and source informed or are carried by its design. Every
entry states what was taken and what was not.

Vendored files each carry their own provenance header at the top of the file,
or directly after the YAML frontmatter when the file must open with one (a
skill or agent file); this document is the index, not the record.

______________________________________________________________________

## Founding guidelines

These bind the design and are indexed, never translated, by the assembly
spec's obligations index (`docs/superpowers/specs/2026-09-05-assembly-design.md` §4). Ideas only — no code or content is copied from any
of them.

| Guideline                 | Author or body                  | Use                                                                                                                                                                                    |
| ------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The LLM-wiki pattern      | Andrej Karpathy                 | The shape of the compile step: an LLM building and maintaining a structured wiki from captured sources. An independent implementation, and the same pattern `claude-obsidian` credits. |
| Notetaking for Historians | the `history-notes` publication | The method behind annotation handling and the split from source into research notes.                                                                                                   |
| PRISMA-S                  | the PRISMA statement            | Search-strategy reporting.                                                                                                                                                             |
| PRISMA-ScR                | the PRISMA statement            | Scoping-review conduct and flow counts.                                                                                                                                                |
| ACM submission guidelines | ACM                             | Manuscript and reference-format obligations for the publication step.                                                                                                                  |

## Conformance mechanism

**Open Knowledge Format (OKF)** — GoogleCloudPlatform/open-knowledge-format.
The vault's survivability guarantee, pinned rather than versioned: the OKF
commit and the `SPEC.md` digest are recorded once in `.github/okf-pin.json`.
The decision is [ADR 0001](docs/adr/0001-vault-outlives-its-tools.md); the
rules, how they are discharged and the conformance deviation register are
[docs/agents/okf-conformance.md](docs/agents/okf-conformance.md).

## Adopted components

| Component                                                          | Author                          | License      | Adopted as                                                                                                                                                                                                                  |
| ------------------------------------------------------------------ | ------------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) | AgriciDaniel / AI Marketing Hub | MIT          | The compile step, installed whole and unmodified at pin `32ac5a0` and driven by a wrapper. No fork, no vendored prose — see [.out-of-scope/vendoring-compile-tool-prose.md](.out-of-scope/vendoring-compile-tool-prose.md). |
| [defuddle](https://github.com/kepano/defuddle)                     | kepano                          | MIT          | Candidate for URL-source acquisition; screened, not adopted.                                                                                                                                                                |
| Better BibTeX                                                      | Emiliano Heyns (retorquere)     | MIT          | Citation keys and CSL rendering. A Zotero plugin, installed by the person, never by this repository.                                                                                                                        |
| [research-grill](https://github.com/scdenney/open-science-skills)  | scdenney                        | CC BY-NC 4.0 | The experiment-proposal plugin's defend stage; a separate install, never a declared dependency, read at `cd70e9b4` and not copied. The exit: stop invoking it; what it wrote stays ordinary Markdown.                       |

**The exit, for the one adoption that writes into the vault:** stop invoking
`claude-obsidian` and everything under `wiki/` remains ordinary markdown with
YAML frontmatter, readable without it and OKF-conformant apart from the single
`wiki/index.md` deviation the conformance register records. Nothing to unwind.

## Vendored source

**[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)**
— MIT, vendored at pin `336c4f83`. Sixteen files under `skills/find-sources/`:
eight API reference documents (Crossref, OpenAlex, Semantic Scholar, PubMed,
PMC, Europe PMC, arXiv, bioRxiv, medRxiv, CORE, Unpaywall) and five scripts
(`arxiv_atom.py`, `jats_to_text.py`, `openalex_abstract.py`, `paginate.py`,
`_common.py`). Each carries a provenance header naming the pin.

**[obra/superpowers](https://github.com/obra/superpowers)** — MIT, © Jesse
Vincent. Skill workflows vendored under their own provenance headers, with
local changes limited to frontmatter descriptions and marked as such.

**[K-Dense-AI/scientific-agents](https://github.com/K-Dense-AI/scientific-agents)**
— MIT, © 2026 K-Dense, Inc., vendored at pin `98c7fae4` into
`plugins/experiment-proposal/agents/hci-researcher.md`: the upstream
human-computer-interaction-researcher subagent, its frontmatter name changed to
`hci-researcher`, a routing sentence prefixed to its description and narrowed to the
questions design asks, and a tools line added, three marked local edits. The
upstream README and `CITATION.cff` ask to be cited; the plugin README repeats the
request.

**[hutzelmann/thesis-proposal-skills](https://github.com/hutzelmann/thesis-proposal-skills)**
— MIT, © 2026 Thomas Hutzelmann, vendored at pin `1666e690` (v0.9.0): the nine upstream
proposal-lit-search scripts, unchanged apart from their headers, under
`plugins/experiment-proposal/skills/lit-search/scripts/`. The `lit-search`
SKILL.md over them is this repository's own. The six substance tests of its
`shared/guidelines/guidelines.md` are closely paraphrased, some clauses verbatim,
into the plugin's `references/checklist.md` items 13.6 to 13.11 (read at `1666e690`,
v0.9.0; text unchanged since `a38b7b1`).

**[mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills)**
— MIT, © 2026 Mohit Aggarwal, vendored at pin `f93fee74` into
`plugins/experiment-proposal/skills/the-ethics-board/SKILL.md`, with two marked
local edits (the frontmatter description replaced by a name-only line; two
sentences that write `proposal/ethics-review.md` and let an agent run proceed on
the inputs given); the repository was unreachable on 2026-10-24, archived as
`swh:1:rev:f93fee7459e2bf452ec9bc43163004812efba51f`. The upstream
`CITATION.cff` asks to be cited; the plugin README repeats the request.

**Adapted into `skills/paper-critical-analysis/`** — text from nine skill
projects, all MIT; each copyright notice is reproduced here as that licence
requires, and the permission text is the standard MIT text in each
repository's LICENSE file.

| Project                                                                                                   | Copyright                                               |
| --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| [affaan-m/ECC](https://github.com/affaan-m/ECC)                                                           | Copyright (c) 2026 Affaan Mustafa                       |
| [bytedance/deer-flow](https://github.com/bytedance/deer-flow)                                             | Copyright (c) 2025 Bytedance Ltd. and/or its affiliates |
| [K-Dense-AI/claude-scientific-writer](https://github.com/K-Dense-AI/claude-scientific-writer)             | Copyright (c) 2025-2026 K-Dense Inc.                    |
| [pedrohcgs/claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow)                 | Copyright (c) 2026 Pedro H. C. Sant'Anna                |
| [AlexWortega/ai-peer-review-skill](https://github.com/AlexWortega/ai-peer-review-skill)                   | Copyright (c) 2026 AlexWortega                          |
| [stephenturner/skill-peer-review-assistant](https://github.com/stephenturner/skill-peer-review-assistant) | Copyright (c) 2026 Stephen D. Turner                    |
| [BESSER-PEARL/research-agent-skills](https://github.com/BESSER-PEARL/research-agent-skills)               | Copyright (c) 2026 BESSER-PEARL                         |
| [Marazii/research-co-pilot](https://github.com/Marazii/research-co-pilot)                                 | Copyright (c) 2026 Maya Arazi                           |
| [honghuy127/cs-ai-research-skills](https://github.com/honghuy127/cs-ai-research-skills)                   | Copyright (c) 2026 Huy H. Nguyen                        |

The process itself, the nine discussion dimensions, and the remaining text are the author's own. [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) (CC BY-NC 4.0) was consulted; no text from it is reproduced.

**Adapted into `plugins/experiment-proposal/`** — the frontier-rounds mechanic of
one MIT-licensed skill, restated in the `design` skill's own words; the copyright
notice is reproduced here as that licence requires, and the full notice text is in
the plugin's `THIRD-PARTY-NOTICES.md`.

| Project                                                   | Copyright                      |
| --------------------------------------------------------- | ------------------------------ |
| [mattpocock/skills](https://github.com/mattpocock/skills) | Copyright (c) 2026 Matt Pocock |

Ideas only, no text reproduced: scdenney's research-grill (CC BY-NC 4.0; the "why this
matters" line, provisional answers and a written record) was consulted and not copied.

The guide the plugin's checklist derives from, `docs/guides/experiment-proposal-guide.md`,
is the author's own, adapted from the Research Methods in HCI course materials
(the project assignment and the course methods guide), its test table aligned
with UCLA OARC's test-selection table; restated, not quoted.

The retired `critical-analysis-report` skill was merged into this one
(spec: `docs/superpowers/specs/2026-10-04-paper-critical-analysis-merge-design.md`).
Its material — the report outline, the notes-file structure that became the
evidence file, the checker, and the background file — derives from the vault
owner's own guide to critical analysis of a research paper; no third-party
text rode along.

The stage 5 editor brief paraphrases, and copies nothing from, Editors
Canada's *Professional Editorial Standards 2024* (its structural and
copy-editing stages; the text is copyrighted). Its stylistic pass, dropped
in the 2026-10 cost tuning, paraphrased Strunk's *The Elements of Style*
(the 1918 edition, public domain) and Wikipedia's "Signs of AI writing"
(CC BY-SA); git retains that text.

## Obsidian resources, screened

Recorded so a later screen starts here rather than from a search. Nothing here is adopted or
installed.

| Resource                                                                     | Author                                               | License     | Note                                                                                                                                                               |
| ---------------------------------------------------------------------------- | ---------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `vault-colors.css`                                                           | claude-obsidian                                      | MIT         | Folder-type colour coding and callout styles; the only snippet that project distributes. Compatible with this repository's licence.                                |
| [Obsidian ITS Theme snippets](https://github.com/SlRvb/Obsidian--ITS-Theme)  | SlRvb                                                | **GPL-2.0** | **Licence hazard.** Attractive Dataview-card and image snippets, but GPL-2.0 into an MIT repository is a one-way door. Cite the technique; do not vendor the file. |
| [obsidian-skills](https://github.com/kepano/obsidian-skills)                 | kepano                                               | MIT         | Named by `skills/setup-vault` as a scriptable companion install, restart-to-activate.                                                                              |
| Calendar, Thino, Excalidraw, Banners                                         | Liam Cain; Quorafind; Zsolt Viczian; Danny Hernandez | various     | Present in `claude-obsidian`'s contributor vault and **not endorsed by it** — listed there as historical state absent from its artifact. Screen independently.     |
| [obsidian-reference-map](https://github.com/anoopkcn/obsidian-reference-map) | anoopkcn                                             | —           | Screened and rejected for capture: within-note and stale (`docs/superpowers/specs/2026-09-06-import-redesign-design.md` §3.8).                                     |
| [ZotLit](https://github.com/aidenlx/zotlit)                                  | aidenlx                                              | —           | Screened: clears three floors, reads SQLite directly, never reads the extracted-text cache.                                                                        |
| [MarkDB-Connect](https://github.com/daeh/zotero-markdb-connect)              | daeh                                                 | —           | Composes with this design, writing one tag and no files.                                                                                                           |

Two hazards `claude-obsidian`'s own plugin guidance names, both of which apply
here and neither of which is obvious: an Obsidian **Git or sync plugin** races
agent operations and makes exact-operation checkpoints ambiguous; and **Web
Clipper** material is untrusted input — *"a clip is not evidence of truth
merely because it was successfully imported"*, which is this vault's admission
rule arrived at independently.

## What is not bundled

This repository downloads no plugin binary and installs no Zotero or Obsidian
extension. Zotero `.xpi` installs are human wizard steps; the vault's README
table declares which are required and which recommended, and doctor reports
what it finds. Obsidian community plugins are the person's to install and
review under their own licences.
