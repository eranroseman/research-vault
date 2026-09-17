# Attributions

research-vault is an original work, MIT licensed. The following third-party
guidelines, tools, and source informed or are carried by its design. Every
entry states what was taken and what was not.

Vendored files each carry their own provenance header at the top of the file;
this document is the index, not the record.

______________________________________________________________________

## Founding guidelines

These bind the design and are indexed, never translated, by the assembly
spec's obligations index. Ideas only — no code or content is copied from any
of them.

| Guideline                 | Author or body                  | Use                                                                                                                                                                                    |
| ------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The LLM-wiki pattern      | Andrej Karpathy                 | The shape of the compile step: an LLM building and maintaining a structured wiki from captured sources. An independent implementation, and the same pattern `claude-obsidian` credits. |
| Notetaking for Historians | the `history-notes` publication | The method behind annotation handling and the split from source into research notes.                                                                                                   |
| PRISMA-S                  | the PRISMA statement            | Search-strategy reporting; one of lane 4's screening floors.                                                                                                                           |
| PRISMA-ScR                | the PRISMA statement            | Scoping-review conduct and flow counts.                                                                                                                                                |
| ACM submission guidelines | ACM                             | Manuscript and reference-format obligations for the publication step.                                                                                                                  |

## Conformance mechanism

**Open Knowledge Format (OKF)** — GoogleCloudPlatform/open-knowledge-format.
The vault's survivability guarantee, pinned rather than versioned: v0.2 at
`open-knowledge-format@ad30107`, `SPEC.md` sha256
`26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`. See
[ADR 0001](docs/adr/0001-vault-outlives-its-tools.md); deviations are priced
in [docs/terminology.md](docs/terminology.md).

## Adopted components

| Component                                                          | Author                          | License | Adopted as                                                                                                                                                                                                                  |
| ------------------------------------------------------------------ | ------------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) | AgriciDaniel / AI Marketing Hub | MIT     | The compile step, installed whole and unmodified at pin `32ac5a0` and driven by a wrapper. No fork, no vendored prose — see [.out-of-scope/vendoring-compile-tool-prose.md](.out-of-scope/vendoring-compile-tool-prose.md). |
| [defuddle](https://github.com/kepano/defuddle)                     | kepano                          | MIT     | Candidate for URL-source acquisition, screened in lane 2.                                                                                                                                                                   |
| Better BibTeX                                                      | Emiliano Heyns (retorquere)     | MIT     | Citation keys and CSL rendering. A Zotero plugin, installed by the person, never by this repository.                                                                                                                        |

**The exit, for the one adoption that writes into the vault:** stop invoking
`claude-obsidian` and everything under `wiki/` remains ordinary markdown with
YAML frontmatter, readable without it and OKF-conformant apart from the single
`wiki/index.md` deviation ADR 0001 records. Nothing to unwind.

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

## Resources for lane 3 (the Obsidian half)

Recorded so lane 3a screens rather than searches. Nothing here is adopted or
installed; the seeded `.obsidian/` folder is lane 3a's own work.

| Resource                                                                     | Author                                               | License     | Note                                                                                                                                                                     |
| ---------------------------------------------------------------------------- | ---------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `vault-colors.css`                                                           | claude-obsidian                                      | MIT         | Folder-type colour coding and callout styles; the only snippet that project distributes. Compatible with this repository's licence.                                      |
| [Obsidian ITS Theme snippets](https://github.com/SlRvb/Obsidian--ITS-Theme)  | SlRvb                                                | **GPL-2.0** | **Licence hazard.** Attractive Dataview-card and image snippets, but GPL-2.0 into an MIT repository is a one-way door. Cite the technique; do not vendor the file.       |
| [obsidian-skills](https://github.com/kepano/obsidian-skills)                 | kepano                                               | MIT         | Named by `skills/setup-vault` as a scriptable companion install, restart-to-activate.                                                                                    |
| Calendar, Thino, Excalidraw, Banners                                         | Liam Cain; Quorafind; Zsolt Viczian; Danny Hernandez | various     | Present in `claude-obsidian`'s contributor vault and **not endorsed by it** — listed there as historical state absent from its artifact. Screen independently.           |
| [obsidian-reference-map](https://github.com/anoopkcn/obsidian-reference-map) | anoopkcn                                             | —           | Screened and rejected for capture: within-note and stale (ingest spec §3.8).                                                                                             |
| [ZotLit](https://github.com/aidenlx/zotlit)                                  | aidenlx                                              | —           | Screened: clears three floors, reads SQLite directly, never reads the extracted-text cache.                                                                              |
| [MarkDB-Connect](https://github.com/daeh/zotero-markdb-connect)              | daeh                                                 | —           | Composes with this design, writing one tag and no files. **Currently misconfigured destructively on the author's machine** — see decomposition §15.16 before running it. |

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
