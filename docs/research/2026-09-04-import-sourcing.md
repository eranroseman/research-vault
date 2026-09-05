# Sourcing findings: the import redesign

**What this artifact is.** An adopt-first sourcing run. It searches for existing components that might serve the import redesign's requirements, reads each candidate's own body, and reports what each one covers, what it does not, and what could not be determined. It follows the `sourcing` skill (`docs/superpowers/reqs/2026-09-02-sourcing.md`), whose own requirements govern this artifact: S27 for this header, S24 for the method, S16 for coverage, S5 for the per-candidate opinions, S6 for the null report, S14 for the handoff.

**What consumes it.** The import redesign brainstorm of 2026-09-04 and the spec that came out of it, `docs/superpowers/specs/2026-09-04-import-redesign-design.md`. Sections 4.2 and 4.3 of that spec draw their candidate descriptions from this note.

**Which requirement set, at which state.** The import requirement set as carried through the 2026-09-04 brainstorm. The set has no standing file of its own, so it is reproduced in full below rather than cited by path. Every requirement was at **version 1** for the whole run; no requirement changed meaning while the run was open, so nothing here is void under S2.

**Which requirements the run treated as marked.** Nine floors: **D1, D2, D3, D4, D6, D10, C1, C2, C6**. The Z register carries no floors. One internal inconsistency is recorded rather than smoothed: the verification block of one record enumerates the floors as eight and omits D2, while the D2 rows of six other records close with "Floor requirement not met" and the critic pass treats D2 as a floor. This note follows the nine-floor reading, which is the stricter one, and the null report below turns on it.

**Nothing here is a decision.** This note carries findings and, per candidate, one opinion about which treatment that candidate's own evidence points toward. It ranks nothing, shortlists nothing, and names no single answer. The treatments are design's to choose among: install as-is, fork and keep merging, copy frozen, copy plus a delta, author to the design and credit it, or write from scratch.

**Conventions.** Every quote is verbatim from the candidate's body at the pin named in that candidate's section, reproduced with its own punctuation, spelling, and language. Authored text is this note's wording. A finding drawn from what a body says it does, rather than from a shipped script, schema, template, or worked example, is marked `basis: claim`; a finding drawn from an artifact is marked `basis: evidence`. Where a record carries a second, adversarial read, its result appears in that candidate's Verify line.

______________________________________________________________________

## The requirement set, reproduced in full

Three lanes. The digest lane (D) is about turning a captured source into vault pages. The capture lane (C) is about getting a source out of a local Zotero and into a vault note. The Zotero-fact lane (Z) is not a set of requirements a component can cover; it is a register of facts about Zotero 10 and Better BibTeX that the redesign needs established from primary sources, and candidates in that lane are documentation and source files read for those facts.

Every requirement below was at version 1 throughout the run. Floors are marked.

### Digest lane

| Id  | Requirement                                                                                                                                                       | Floor   | Version |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ------- |
| D1  | Writes a per-source page carrying a summary and key points, derived from the source document (markdown or PDF).                                                   | **yes** | 1       |
| D2  | Fills a charting template whose field list is supplied per project by the caller, for example population, concept, context, design, findings, page locator.       | **yes** | 1       |
| D3  | Maintains cross-source concept or synthesis pages with an index and an append-only log; contradictions are kept and flagged, never resolved by deleting one side. | **yes** | 1       |
| D4  | Ingest is separable from integrate: the tool consumes a note another process wrote and does not own creation of the source file.                                  | **yes** | 1       |
| D5  | Re-ingest of an unchanged source is a no-op.                                                                                                                      | no      | 1       |
| D6  | Runs as a Claude Code skill or plugin, installable as-is. Codex compatibility is recorded separately rather than counted here.                                    | **yes** | 1       |
| D7  | Works on an existing vault with a caller-chosen layout, or states its layout requirements explicitly.                                                             | no      | 1       |
| D8  | References each source by a caller-supplied stable id in page links and provenance markers.                                                                       | no      | 1       |
| D9  | The human review gate before integration is configurable, or at least documented as per-source versus batch.                                                      | no      | 1       |
| D10 | The licence permits use and modification.                                                                                                                         | **yes** | 1       |

### Capture lane

| Id  | Requirement                                                                                                                                                                    | Floor   | Version |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- | ------- |
| C1  | Reads a local Zotero rather than the web API (the local API on localhost:23119, or Better BibTeX JSON-RPC): item metadata, attachments, annotations.                           | **yes** | 1       |
| C2  | Emits a citekey-keyed markdown literature note with a machine-owned managed region and a preserved free region, or can be driven to.                                           | **yes** | 1       |
| C3  | Detects change after capture: drift, orphan, re-key.                                                                                                                           | no      | 1       |
| C4  | Extracts PDF text locally, with no cloud call.                                                                                                                                 | no      | 1       |
| C5  | Runs headless from a CLI or an agent, with no Obsidian application running.                                                                                                    | no      | 1       |
| C6  | The licence permits use.                                                                                                                                                       | **yes** | 1       |
| C7  | Provides Zotero-side enrichment or lint that the vault would otherwise replicate: DOI verification, PMCID lookup, citation counts, arXiv version update, metadata format lint. | no      | 1       |

### Zotero-fact register

| Id  | Fact to establish                                                                                                                                             | Floor | Version |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ------- |
| Z1  | Local API write support on Zotero 10: how a key is granted, the consent dialog, key lifetime, `Zotero-Write-Token`, and the `Zotero-Server-ID` precondition.  | no    | 1       |
| Z2  | Version semantics: local versions against synced versions, `?since=`, `format=versions`, `Last-Modified-Version`, and partitioning cached state by server id. | no    | 1       |
| Z3  | Full-text endpoints: what `GET /items/<key>/fulltext` returns, how pages are separated inside `content`, and what a 404 means.                                | no    | 1       |
| Z4  | File endpoints: what `/file`, `/file/view` and `/file/view/url` return, the form of the URL, and the upload flow.                                             | no    | 1       |
| Z5  | Saved-search execution and the collection endpoints.                                                                                                          | no    | 1       |
| Z6  | The native `citationKey` item field, and the Zotero version from which it exists across item types.                                                           | no    | 1       |
| Z7  | Better BibTeX JSON-RPC at 9.0.6x: the method inventory, the auto-export API, the citekey pin store, and what `item.regenerate_key` returns.                   | no    | 1       |

______________________________________________________________________

## Method

### Declared before the search

**Candidate concept.** Anything already built that a person could install, fork, copy, or read against the set: Claude Code plugins and skills, Codex and other agent skills, Obsidian plugins, Zotero plugins, command-line tools and libraries, published starter bundles, and, for the Z register, primary documentation and source files. A body that only describes a method, with nothing to install, still counts as a candidate for the parts of the set it addresses.

**Kinds of source.** GitHub repository search, GitHub code search, GitHub topic search, plugin catalogues and marketplaces (Anthropic's official marketplaces, community `marketplace.json` aggregators, the Zotero plugin catalogues, the Obsidian community plugin list), the vendors' own documentation sites, and open web search.

**Stopping rule.** Search on the marked subset only, from more than one kind of source, until new sources return only candidates already seen, or the sources are spent. Where results are too many to report, search again with the remaining requirements added and say so.

**Search cap.** The digest sweep was declared with a cap of twelve searches. Thirteen were run. The overrun is the llmwikis.org read, which the task named as a required source; it is recorded here rather than left implicit.

### Every search run

Hit counts are as the tool reported them at the time of the search. Where an API `total_count` is approximate, that is said.

01. **GitHub repo search** (`gh search repos` / `search/repositories` API). Terms: `"llm wiki" --sort stars`. Hits: 4,897. API `total_count`; top 40 by stars reviewed.
02. **GitHub repo search.** Terms: `"llm-wiki" --sort stars`. Hits: 5,089. API `total_count`; top 40 reviewed; heavy overlap with search 1.
03. **GitHub repo search.** Terms: `topic:llm-wiki --sort stars`. Hits: 448. Top 40 reviewed.
04. **GitHub repo search.** Terms: `topic:karpathy-wiki`. Hits: 15. All 15 reviewed.
05. **GitHub repo search.** Terms: `topic:karpathy-llm-wiki`. Hits: 43. Top 30 reviewed.
06. **GitHub repo search.** Terms: `topic:karpathy wiki`. Hits: 142. Top 30 reviewed.
07. **GitHub repo search.** Terms: `obsidian claude wiki --sort stars`. Hits: 526. Top 40 reviewed.
08. **GitHub repo search.** Terms: `"llm wiki" claude skill --sort stars`. Hits: 181. Top 40 reviewed.
09. **GitHub repo search.** Terms: `"llm wiki" plugin --sort stars`. Hits: 133. Top 40 reviewed.
10. **Anthropic official marketplaces** (`gh api contents`). Terms: `anthropics/claude-code .claude-plugin/marketplace.json`; `anthropics/claude-plugins-official .claude-plugin/marketplace.json` grepped for `wiki|obsidian|knowledge`. Hits: 0. The `claude-code` marketplace path gave an empty result, and absence is not distinguished from no-match there; `claude-plugins-official` lists 291 plugins, none an LLM-wiki implementation (the keyword matches were gitlab, notion, knowledge-catalog, netsuite, twilio).
11. **GitHub code search** (`gh search code` / `search/code` API). Terms: `llm-wiki filename:marketplace.json`. Hits: 136. API `total_count`; 60 files listed, giving 61 community marketplace repositories, about 25 of them not seen in the repository searches. The first attempt used a `path:.claude-plugin/marketplace.json` qualifier and returned 0; that syntax is unsupported, and the re-run with `--filename` returning 136 is what establishes the tool and the query were working.
12. **GitHub code search.** Terms: `karpathy wiki ingest filename:SKILL.md`. Hits: 2,456. The API `total_count` is approximate; the CLI returned only 4 results, 1 of them relevant (`bcmcpher/memex-vault`).
13. **llmwikis.org.** Pages read: `/`, `/implementations/tooling-landscape/`, `/related-links/`, `/examples/`, `/content-license/`, `/downloads/llm-wiki-starter-bundle-v3.2.0.zip`. Hits: 5. The tooling-landscape page names no products (it carries a category taxonomy and a maturity ladder only); related-links lists four GitHub repositories, two of which are digest candidates; the examples page has no external links; the starter bundle is 108 files with no `SKILL.md`.
14. **Community `marketplace.json` parse** across 20 aggregator repositories found by search 11. Terms: `plugins[]` entries matching `wiki|knowledge|karpathy|brain`. Hits: 12 wiki plugin entries, 6 of which led to sources not otherwise surfaced.
15. **Stop condition.** Not saturated. See the next subsection.
16. **GitHub repo search.** Terms: `topic:zotero-plugin --sort stars --limit 100`. Hits: 100. The densest single source: the Zotero 7+ plugin-template ecosystem.
17. **GitHub repo search.** Terms: `topic:zotero --sort stars --limit 100`. Hits: 100. Non-plugin tooling.
18. **Zotero plugin catalogue**, `zotero-chinese/zotero-plugins` `src/plugins.ts`. The URL `github.com/windingwind/zotero-plugins` named in the seed list is a 404; the catalogue lives at `zotero-chinese`, its maintenance is suspended, and submissions are redirected to `syt2/zotero-addons-scraper`. Terms: repository names grepped for `lint`, `format`, `doi`, `pmc`, `cit`, `scite`, `opencit`, `arxiv`, `ocr`, `tldr`, `fulltext`, `markdown`, `obsidian`, `scholar`, `pdf2`, `mineru`, `mcp`, `cli`, `meta`, `export`. Hits: 31 name matches out of 135 catalogued repositories.
19. **Zotero plugin catalogue successor**, `syt2/zotero-addons-scraper` `addons/` (298 `owner@repo` files, feeding the Zotero Add-on Market and zotero-chinese.com/plugins). Terms: the same name grep, minus repositories already in the zotero-chinese list. Hits: 29 new name matches out of 298 catalogued.
20. **zotero.org/support/plugins.** Terms: the page grepped for `lint`, `format`, `DOI`, `PMCID`, `citation`, `scite`, `arXiv`, `OCR`, `TL;DR`, `fulltext`, `markdown`, `Obsidian`, `MCP`, `CLI`. Hits: 0. The page was reached and read; it no longer carries a plugin list. Its own text is what establishes the null: "We don't currently provide a list of available plugins... An official plugin directory is planned." There were zero rows to grep.
21. **Obsidian community plugin list**, raw `obsidianmd/obsidian-releases` `community-plugins.json` (7,270 plugins). Terms: id, name and description matched against the regex `zotero|citation|bibtex|bibliograph|pandoc|reference manager|citekey|better bibtex|literature note|csl`. Hits: 71 rows.
22. **GitHub repo search.** Terms: `zotero obsidian --sort stars --limit 60`. Hits: 60.
23. **GitHub repo search.** Terms: `zotero markdown export --sort stars --limit 50`. Hits: 24.
24. **GitHub repo search.** Terms: `zotero mcp --sort stars --limit 50`. Hits: 50.
25. **GitHub repo search.** Terms: `zotero cli --sort stars --limit 50`. Hits: 50.
26. **GitHub repo search.** Terms: `zotero "semantic scholar" --sort stars --limit 40`. Hits: 37. Run to fill the TL;DR branch.
27. **GitHub repo search plus code search.** Terms: `scinet zotero --limit 30`, then `scinet filename:manifest.json`. Hits: 1. The only hit is `a1ix2/zotero-scihub-scinet` (1 star, a single README), a Zotero PDF-resolver configuration for Sci-Hub and Sci-Net mirrors, which is full-text retrieval and not a citation-count source. No Zotero plugin named SciNet providing citation data exists on GitHub; the seed's "SciNet" most likely conflates scite (scitedotai) with Sci-Net.
28. **GitHub repo search.** Terms: `zotero doi --sort stars --limit 40`. Hits: 40. Run to fill the DOI branch.
29. **GitHub repo search.** Terms: `zotero fulltext pdf text --sort stars --limit 40`. Hits: 3. One new hit of value, `matthiaskloft/zotero-fulltext-mcp`.
30. **Web search.** Terms: `"LLM wiki" Claude Code plugin`. Hits: 7.
31. **Web search.** Terms: `"llm wiki" obsidian skill 2026`. Hits: 6.
32. **Web search.** Terms: `scoping review data charting LLM tool`. Hits: 7. Only software-as-a-service with no readable body (Covidence, JBI SUMARI) and papers (arXiv 2507.06623, an LLM data-extraction protocol, not fetched). No installable charting tool surfaced. This is the search that bears directly on D2.
33. **Web search.** Terms: `"literature note" zotero generator CLI markdown`. Hits: 8.
34. **Web search.** Terms: `zotero "local API" markdown export tool`. Hits: 10.
35. **Web search.** Terms: `zotero annotations to markdown CLI`. Hits: 10.
36. **Web search.** Terms: `"Better BibTeX" "JSON-RPC" markdown notes`. Hits: 9.
37. **Web search.** Terms: `zotero plugin "DOI" verify PMCID "citation count"`. Hits: 9.
38. **Web search.** Terms: `zotero 10 local API write plugin`. Hits: 7.
39. **Web search.** Terms: `"PRISMA-ScR" software charting`. Hits: 10. Guidance pages and library guides only; Covidence the sole software named; no charting tool with a readable body. The second search bearing on D2.
40. **Web search.** Terms: `zotero local API "Zotero-Write-Token" OR "Always Allow" write key consent dialog`. Hits: 10.
41. **Web search.** Terms: `zotero local API "format=versions" "since" "Last-Modified-Version" localhost:23119`. Hits: 8. One hit (forum 129225, a Zotero 8 `include=citation` bug) was irrelevant to Z2 and Z3 and was dropped.
42. **Web search.** Terms: `zotero item JSON "citationKey" field native Zotero 7 API`. Hits: 9. The results claimed the field is not native; that claim was falsified against the `zotero-schema` git history, which shows the field on 37 of 40 item types.
43. **Web search.** Terms: `"Better BibTeX" JSON-RPC "autoexport.add" "item.citationkey" "item.pandoc_filter"`. Hits: 9. Confirmed the `autoexport.add` signature and the `pandoc_filter` parameters.

### Sources and queries added mid-search, with their reasons

- Search 11 was re-run after its first form returned zero, because the `path:` qualifier is unsupported in GitHub code search. The re-run is what shows the null was a syntax artefact and not a fact about the field.
- Searches 26 to 29 (`zotero "semantic scholar"`, `scinet zotero`, `zotero doi`, `zotero fulltext pdf text`) were added after the catalogue sweeps left the TL;DR, SciNet, DOI and full-text branches of C7 unresolved. Each was added to close a named branch, not to change an unwelcome result.
- Search 19 was added because the catalogue named in the seed list had moved: `windingwind/zotero-plugins` is a 404, `zotero-chinese/zotero-plugins` is suspended, and `syt2/zotero-addons-scraper` is the live successor.
- Searches 40 to 43 were added for the Z register once the D and C lanes were closed, because the register needs primary sources rather than candidates.

### Where saturation fell

**It did not.** The stop condition is recorded as not saturated. The `marketplace.json` code search was still producing about 25 unseen repositories when the sweep stopped, and the two broad repository searches carry more than 4,800 hits each. The run stopped on its declared cap, not on saturation, and the digest lane's coverage should be read as a sample of a field that is still producing new candidates rather than as a census of it. Two seeded candidates, `garrytan/gbrain` and `NousResearch/hermes-agent`, never surfaced in any search and were read only because they were seeded; that is direct evidence that search alone was not reaching the field.

Excluded classes, seen in results and not carried forward as candidates, recorded here so the same ground is not swept again: desktop and hosted applications (nashsu/llm_wiki, inkeep/open-knowledge, Tencent, jonex, synthadoc, lucasastorian/llmwiki, Molio, polywise); Ollama-only applications (kytmanov twice, NiharShrotri); code-to-wiki tools (Egonex, repolore, nium-wiki, vault-anything, ivankuznetsov/llm-wiki, roboco-io/claude-wiki); session-memory-only tools (ctxr-dev, eugeniughelbur, KevinLuo1, LaserPhaser, berrydev-ai, xiaolai/bureau, daehyeonxyz, bartolli/kmd); pure Obsidian plugins with no agent surface (Jindequan, ouyearllla, wfukatsu, OgnjenKop, pssah4); and vaults or guides with no surface at all (Lyra-stellAI, Beever-AI, cclank/Hermes-Wiki, ScrapingArt, julianoczkowski, Emmimal, sillok, Alirezajalilii, Vesna, ddsyasas, crabin, xiaoyuze88, Hockwang, HaowenHou, lanbai-sunsky).

### The seeded list

Twenty-one candidates were seeded rather than found, and are marked as seeded in their own sections: nvk/llm-wiki, the hermes-agent llm-wiki skill, AgriciDaniel/claude-obsidian, atomicstrata/llm-wiki-compiler, garrytan/gbrain, swarmclawai/swarmvault, Pratiyush/llm-wiki, SamurAIGPT/llm-wiki-agent, kepano/obsidian-skills, the Karpathy gist, llmwikis.org, PKM-er/obsidian-zotlit, mgmeyers/obsidian-zotero-integration, 54yyyu/zotero-mcp, daeh/zotero-markdb-connect, dvanoni/notero, urschrei/pyzotero, retorquere/zotero-better-bibtex, northword/zotero-format-metadata, the Zotero plugin catalogue, and UB-Mannheim/zotero-ocr. Two of the seeded URLs redirect: `PKM-er/obsidian-zotlit` to `aidenlx/zotlit`, and `mgmeyers/obsidian-zotero-integration` to `community-archive/obsidian-zotero-integration`. Both were read at the redirect target and the duplicate discovery entries were folded into the seeded records.

### The triage bound

Every discovery was placed in one of three buckets, and every drop carries a reason and a count. Nothing was capped silently.

| Bucket                      | Count   | What it means                                                                                             |
| --------------------------- | ------- | --------------------------------------------------------------------------------------------------------- |
| Keep, read as a candidate   | 43      | Read at a pin, described against the set.                                                                 |
| Enrichment catalogue        | 36      | Zotero-side enrichment and lint plugins, read for C7 as one catalogue record rather than one record each. |
| Dropped                     | 206     | Five reasons, below.                                                                                      |
| **Triaged total**           | **285** |                                                                                                           |
| Added after the critic pass | 3       | Astro-Han/karpathy-llm-wiki, sdyckjq-lab/llm-wiki-skill, PiaoyangGuohai1/cli-anything-zotero.             |
| **Considered in total**     | **288** |                                                                                                           |

Drops by reason:

1. **Duplicate mechanism of a kept candidate: 134.** Ninety-one digest-lane Karpathy-style skills and plugins whose raw-to-wiki ingest, index and log bookkeeping, contradiction flagging or approval gate is already carried by a kept candidate, plus 40 capture-lane Zotero readers, MCP servers, command-line tools and note bridges covered by the kept capture set, plus 3 secondary Zotero forum threads superseded by the kept primaries. Examples: `Astro-Han/karpathy-llm-wiki` (2,151 stars, dropped here as a generic raw-plus-wiki skill; the critic pass reversed this drop and it was read, see its own section), `IssacW228/student-llm-wiki` (an md5 manifest hash that ar9av already covers), `zotero-cli-ai` (205 stars, sqlite reads and a dual AGPL/commercial licence; alex-roc/zotero-agent covers the local-API and Better BibTeX path).
2. **Out of lane: 33.** Seventeen digest entries that are not Claude Code plugins or skills for document digest (Obsidian-plugin-only engines, pi/Copilot/Cursor-only hosts, project-memory or code-semantics wikis, todo and calendar companions, a NotebookLM cloud pipeline, a Docker application with no skill), and 16 capture entries that do not read a local Zotero or do not emit literature notes (web-API-only tools, cloud-gated services, cloud-LLM plugins, link-insertion or search-only tools, connector emulators, audit-only workflows). Examples: `ZotFlow` (183 stars, web API and WebDAV only), `Stratum` (stratumnotes.com account, Zotero OAuth, Sentry), `zosmaai/pi-llm-wiki` (555 stars, pi-extension tools, Claude Code unverified).
3. **Personal starter template: 29.** `CLAUDE.md` and `AGENTS.md` vault templates, scaffold-only init commands, and setup walkthroughs with no adoptable ingest mechanism beyond what the seeded gist and handbook already state. Examples: `jason-effi-lab/karpathy-llm-wiki-vault` (701 stars, no licence), `shannhk/llm-wikid` (415 stars, no licence), `eleven-net-cn/llm-wiki-starter` (explicitly not for ingesting into an existing wiki).
4. **No body reachable: 6.** Command or skill bodies that were never read (cajias, cosen1024, gal-Tab, songzhuozhu), a VS Code listing with no source repository, and the zotero.org JSON documentation page marked "FIXME work in progress". These are drops, not not-examined candidates: none was described against the set.
5. **Fork or duplicate URL of a kept candidate: 4.** The two seeded redirects above, the hermes-agent blob URL that is the same `SKILL.md` as the seeded tree URL, and `Lambenthan/empiricalwiki`, an AutoSci derivative.

### The verify pass

A second, adversarial pass re-read candidates at their pins. Each pass re-fetched the licence file, re-resolved the pin, and re-checked up to three coverage rows, taken from the rows the record had scored `covers` on a floor. Every pass reported per row whether the row was refuted, and reported separately whether the licence and the pin still held.

| Measure                                        | Count    |
| ---------------------------------------------- | -------- |
| Read records in the run                        | 48       |
| Read records carrying at least one verify pass | 42       |
| Read records verified twice                    | 19       |
| Read records with no verify pass               | 6        |
| Verify passes recorded                         | 61       |
| Coverage rows re-checked                       | 146      |
| Rows refuted                                   | 4        |
| Licence re-confirmed at the pin                | 61 of 61 |
| Pin re-confirmed                               | 61 of 61 |
| Passes reporting a refuted fact                | 0 of 61  |

The four refutations split two ways. One is a real refutation of a written quote: atomicstrata/llm-wiki-compiler's D4 evidence dropped a word from the source line, which the second pass on the same candidate then confirmed on the corrected line. The other three fall on the Zotero-fact record for the Web API Write Requests page, whose coverage array is empty; the verifier applied its default-refuted rule to three rows the record never asserted. No coverage row's finding was overturned in this run.

The six records with no verify pass are the Zotero enrichment catalogue, the Better BibTeX documentation site record, and the four bodies read after the critic pass: cli-anything-zotero, Astro-Han/karpathy-llm-wiki, sdyckjq-lab/llm-wiki-skill, and the AutoSci runtime schema re-read. The last of these matters for the null report below, because the AutoSci re-read is what moves the run's only D2 cover.

### What was not examined, and why

No record in this run carries the not-examined marker of S8: every candidate in the keep bucket was read at a pin. The honest equivalents are bodies that a record named and then did not open, which are listed here so a later reader does not have to infer them:

- **`skyllwt/AutoSci` branch `autosci-codex`.** The sole basis for AutoSci's separately recorded Codex-compatibility claim. The branch exists (the record's own branch listing confirms it) and was not opened; the claim rests on `README.md` line 57 and line 68 rather than on the branch.
- **claude-obsidian's "Community early-access mirror (Pro)"** at `github.com/AI-Marketing-Hub`, named in that candidate's `ATTRIBUTION.md`. Not opened, so what the paid tier contains is unknown here.
- **notero's `auth/storage.ts` and `auth/crypto.ts`.** Not read, which leaves the credential-storage claim in its `PRIVACY.md` unverified.
- **The three prior-art repositories named in Pratiyush's own acknowledgements** (`lucasastorian/llmwiki`, `xoai/sage-wiki`, `bashiraziz/llm-wiki-template`) and the fourth, `SamurAIGPT/llm-wiki-agent`, which was read. The first three were named in a body this run read and were not followed.
- **The digest cohort at or above the star count of the candidates read.** The critic pass named five specific repositories in that cohort; two of them (Astro-Han, sdyckjq-lab) were read afterwards and appear below, and three (`lucasastorian/llmwiki`, `xoai/sage-wiki`, `kytmanov/obsidian-llm-wiki-local`) were not.
- **The canonical Zotero-to-markdown literature-note lineage**, named by the critic: `argenos/zotero-mdnotes`, `hans/obsidian-citation-plugin`, `stefanopagliari/bibnotes`, `windingwind/zotero-actions-tags`. None was read. This is the lineage every C2 candidate that was read inherits from.
- **Enrichment plugins beyond the 36 in the catalogue record.** The two Zotero catalogues hold 135 and 298 entries; the name-grep matched 31 and 29 of them, and only the matches were opened.

______________________________________________________________________

## Coverage matrix

**Legend.** `Y` covers, `P` partial, `N` does not, `U` undetermined and said so, blank means the run recorded no row, which under S16 reads as undetermined. A trailing `*` marks a row whose basis is a claim (the body says it does this) rather than evidence (a shipped script, schema, template, or worked example). A trailing `!` marks a row an adversarial verify pass refuted. One coverage row in the run carries it: atomicstrata/llm-wiki-compiler at D4, refuted for quote fidelity rather than for the finding. The run's other three refutations fall on a Zotero-fact record whose coverage array is empty, where the verifier defaulted three unasserted rows to refuted; they are discussed under Gaps. Floor requirements are bold in the header. Candidate names are shortened; each row links to the section of the same name below.

### Digest lane

| Candidate                            | **D1** | **D2** | **D3** | **D4** | D5  | **D6** | D7  | D8  | D9  | **D10** |
| ------------------------------------ | ------ | ------ | ------ | ------ | --- | ------ | --- | --- | --- | ------- |
| nvk/llm-wiki                         | P      | N\*    | Y\*    | Y      | P\* | Y      | Y   | P   | P\* | Y       |
| hermes-agent llm-wiki                | N\*    | N\*    | Y      | P\*    | Y\* | P\*    | Y   | P\* | Y\* | Y       |
| AgriciDaniel/claude-obsidian         | Y      | N      | Y      | Y      | P   | Y      | Y   | P   | Y   | Y       |
| atomicstrata/llm-wiki-compiler       | N      | N      | Y      | Y!     | Y   | N      | Y   | P   | Y   | Y       |
| garrytan/gbrain                      | P\*    | P\*    | P\*    | Y      | Y   | Y      | Y   | P   | P\* | Y       |
| swarmclawai/swarmvault               | Y      | N      | Y      | Y      | Y   | P      | Y   | P   | Y   | Y       |
| Pratiyush/llm-wiki                   | Y      | P      | P\*    | Y      | P   | P      | Y   | P   | P   | Y       |
| SamurAIGPT/llm-wiki-agent            | Y      | P      | P      | Y      | N   | P      | Y   | P\* | N   | Y       |
| kepano/obsidian-skills               | N\*    | N\*    | N\*    | N\*    | N\* | Y      | Y   | N\* | N\* | Y       |
| Karpathy llm-wiki gist               | Y\*    | N\*    | P\*    | Y\*    | N\* | N\*    | P\* | N\* | Y\* | U\*     |
| llmwikis.org handbook                | P      | N      | P      | Y      | P\* | N      | Y   | P   | Y   | P\*     |
| llmwikis.org starter bundle v3.2.0   | N      | N      | P      | P      | P   | N      | Y   | P   | Y   | U       |
| kfchou/wiki-skills                   | Y      | N      | P      | Y\*    | N\* | Y      | Y   | P\* | P\* | Y       |
| gaebalai/cc-llm-wiki                 | Y      | N      | P\*    | Y      | N   | Y      | Y   | P   | Y   | Y       |
| ussumant/llm-wiki-compiler           | N      | P      | P\*    | Y      | P   | Y      | Y   | N   | Y\* | Y       |
| pumblus/okf-harness                  | Y      | N      | P      | Y      | P   | Y      | Y   | N   | P\* | Y       |
| skyllwt/AutoSci                      | P\*    | Y      | P      | Y      | P\* | Y      | Y   | N   | P\* | Y       |
| AutoSci runtime schema, second read  | Y      | P      | Y      | Y      | P\* | Y      | Y   | N   | N\* | Y       |
| ar9av/obsidian-wiki                  | P      | N      | P\*    | Y      | Y   | Y      | Y   | N\* | Y\* | Y       |
| Astro-Han/karpathy-llm-wiki          | P      | N      | Y      | P      | N\* | Y      | Y   | P   | N\* | Y       |
| sdyckjq-lab/llm-wiki-skill           | Y      | N      | Y      | Y      | Y   | Y      | Y   | N   | P\* | P       |
| 917Dhj/DeepPaperNote                 | Y      | N      | N      | P      | P   | Y      | Y   | N   | N\* | Y       |
| Mappedinfo/local-zotero-mirror       | N      | N      |        |        |     |        | Y   | P   |     |         |
| alex-roc/zotero-agent                | P\*    |        |        |        |     | Y      |     | P   |     | Y       |
| PKM-er/obsidian-zotlit               |        |        |        |        |     | P      | Y   | P   |     | Y       |
| mgmeyers/obsidian-zotero-integration |        | P      |        |        |     |        | Y   | Y   |     |         |
| 54yyyu/zotero-mcp                    |        |        |        |        |     | P      |     | P   |     | Y       |
| daeh/zotero-markdb-connect           |        |        |        | P      |     |        | P   | P   |     | Y       |
| masaki39/simple-citations            |        |        |        |        |     |        | Y   | Y   |     | Y       |
| windingwind/zotero-better-notes      |        | P      |        |        | P   |        |     |     |     | Y       |
| UB-Mannheim/zotero-ocr               |        |        |        |        |     |        |     |     |     | Y       |
| cli-anything-zotero                  |        |        |        |        |     | P      |     |     |     | Y       |

**AutoSci appears twice on purpose.** The first row is the original read; the second is the re-read the critic pass ordered, which is what settles D2. The D2 cell moves from `Y` to `P`, and with it the run's only D2 cover.

### Capture lane

| Candidate                               | **C1** | **C2** | C3  | C4  | C5  | **C6** | C7  |
| --------------------------------------- | ------ | ------ | --- | --- | --- | ------ | --- |
| PKM-er/obsidian-zotlit                  | Y      | Y      | P   | N   | N   | Y      | N   |
| mgmeyers/obsidian-zotero-integration    | Y      | Y      | P   | N   | N   | Y      | N   |
| 54yyyu/zotero-mcp                       | Y      | N      | P   | P   | Y   | Y      | P   |
| cookjohn/zotero-mcp                     | Y      | N      | N   | Y   | Y   | Y      | P   |
| alex-roc/zotero-agent                   | Y      | N      | N   | P   | Y   | Y      | Y   |
| cli-anything-zotero                     | Y      | N      | P   | N   | Y   | Y      | P   |
| retorquere/zotero-better-bibtex         | Y      | N      | P   | N   | Y   | Y      | P   |
| windingwind/zotero-better-notes         | Y      | P      | P   | N   | P   | Y      | N   |
| 917Dhj/DeepPaperNote                    | Y      | N      | N   | Y   | Y   | Y      | N   |
| urschrei/pyzotero                       | P      | N      | Y   | P   | Y   | Y      | P   |
| Mappedinfo/local-zotero-mirror          | P      | P      | P   | N   | N   | Y      | N   |
| daeh/zotero-markdb-connect              | P      | N      | N   | N   | N   | Y      | N   |
| dvanoni/notero                          | P      | N      | P   | N   | N   | Y      | N   |
| UB-Mannheim/zotero-ocr                  | P      | N      | N   | Y   | N   | Y      | P   |
| masaki39/simple-citations               | N      | Y      | P   | N   | N   | Y      | N   |
| northword/zotero-format-metadata        | N      | N      | N   | N   | N   | Y      | Y   |
| Zotero enrichment catalogue, 36 plugins |        |        |     |     |     |        | Y   |
| zotero-chinese/zotero-plugins catalogue | N      | N      | N   | N   | N   | Y      | P   |
| nvk/llm-wiki                            | N\*    |        |     | P\* | P\* | Y      |     |
| AgriciDaniel/claude-obsidian            | N      |        |     | N   | Y   |        |     |
| atomicstrata/llm-wiki-compiler          | N      |        |     | P   | Y   | Y      | N   |
| garrytan/gbrain                         |        |        |     | N   | Y   |        | N\* |
| swarmclawai/swarmvault                  |        |        |     | Y   | Y   |        |     |
| Pratiyush/llm-wiki                      |        |        |     | N   | Y   |        |     |
| SamurAIGPT/llm-wiki-agent               |        |        |     | Y   | Y   |        |     |
| kepano/obsidian-skills                  |        | N\*    |     | N\* | P\* | Y      |     |
| Karpathy llm-wiki gist                  |        |        |     |     | P\* |        |     |
| kfchou/wiki-skills                      |        |        |     |     | Y   | Y      |     |
| skyllwt/AutoSci                         | N      |        |     | P   | Y   |        |     |
| AutoSci runtime schema, second read     | N      | P      | N   | P   | Y   | Y      | P\* |
| ar9av/obsidian-wiki                     |        |        |     | N\* | Y   |        |     |
| Astro-Han/karpathy-llm-wiki             |        |        |     |     |     | Y      |     |
| sdyckjq-lab/llm-wiki-skill              |        |        |     | N   | Y   |        |     |

The enrichment catalogue is one record covering 36 plugins, scored as seven C7 rows by capability group rather than one row per plugin: DOI and PMCID `Y`, citation counts and citation lists `Y`, TL;DR `P`, arXiv version update and metadata refresh `Y`, metadata-format lint and pre-admission verification `P`, OCR and PDF-to-markdown `Y`, and a `N` row recording four plugins that provide no enrichment at all. The single cell above is the aggregate; the seven rows are in that candidate's section.

### Zotero-fact register

The fact lane is not coverage. Each record is a documentation page or a source file read for the facts in the register, and the cell says which fact identifiers that body answered. `partial` means the body answers part of the fact and names what it does not.

| Body read                                                                  | Z1  | Z2  | Z3  | Z4  | Z5  | Z6  | Z7  |
| -------------------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
| Zotero Local API page, with linked write, full-text, basics, syncing pages | Y   | Y   | Y   | Y   | Y   | P   | Y   |
| Zotero Web API v3 Write Requests, with the same linked set                 | Y   | Y   | Y   | Y   | Y   | P   | Y   |
| Zotero Web API v3 Full-Text Content                                        | Y   | Y   | Y   | Y   | Y   | P   |     |
| Zotero Web API v3 Basics                                                   | Y   | Y   | Y   | Y   | Y   | P   | Y   |
| Zotero 10 for Developers                                                   | Y   | Y   | Y   | Y   | Y   | Y   | Y   |
| zotero-schema commit 55a1312                                               | Y   | Y   | Y   | Y   | Y   | Y   | Y   |
| Better BibTeX docs, JSON-RPC page                                          |     |     |     |     |     | P   | Y   |
| Better BibTeX `content/json-rpc.ts` at v9.0.63                             |     |     |     |     |     | P   | Y   |
| Better BibTeX `content/key-manager.ts` at v9.0.63                          |     |     |     |     |     | P   | Y   |

Z3's page separator and Z6's introducing Zotero version are the two facts no documentation page states. Both are answered from source and from a live probe, and are marked as such in the facts section.

______________________________________________________________________

## Candidates, digest lane

### 1. nvk/llm-wiki

Seeded. `https://github.com/nvk/llm-wiki` (Claude Code plugin `wiki`, marketplace `llm-wiki`). Pin `7c94c9bf2968f17deb496b285db0afdb610a01d9`, tag v0.24.4, committed 2026-08-27T16:52:34Z; `plugin.json` version 0.24.4. Kind: Claude Code plugin, 30 command files and one skill with 22 reference files, plus a 5,965-line stdlib-only Python CLI for deterministic lint, schema, archive, retract, adapter, specialist and checkpoint work; a generated Codex plugin and an OpenCode profile ship alongside.

**Maintenance.** Last push 2026-08-27T16:55:02Z, release v0.24.4 the same day, v0.24.3 on 08-23 and v0.24.2 on 08-22, so near-daily releases. 1,193 stars, 110 forks, 21 open issues; created 2026-04-04. Effectively single-maintainer: nvk 259 commits, next contributors 5, 4, 3, 1. Not archived. Shell tests, promptfoo evals, a golden fixture, and generated-plugin drift tests.

**Originator and supplier.** nvk, both. The LLM-wiki concept is credited in `README.md` line 862 to Karpathy's gist, not incorporated as code.

**Licence.** MIT, found. Read from `/LICENSE` lines 1-13 at the pin, and corroborated by `claude-plugin/.claude-plugin/plugin.json` line 8 and the Codex manifest line 11.

```
MIT License

Copyright (c) 2026 nvk

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
```

IP assertions: nothing beyond the copyright line. No contributor agreement, no trademark, no patent clause.

**Verify.** Licence confirmed at the pin; the record's quote reflows the file's hard line breaks without altering wording, and stops before the warranty disclaimer, which lies outside the cited range. Pin confirmed: the commit resolves and its committer date matches. Three rows re-checked, none refuted.

**Smallest part.** The compile and structure protocol trio, which is runtime-neutral prose: `claude-plugin/skills/wiki-manager/references/compilation.md` (142 lines: survey, extract, map to existing, classify, write with `sources:` and See Also, bidirectional links, index update, plus the confidence and volatility rules and the honest-disagreement standard); the Source File Format and Wiki Article Format sections of `references/wiki-structure.md` (lines 370-452); optionally the derived-index protocol and the log format. The PDF ingestion section of `references/ingestion.md` (lines 266-292) is separately liftable. The deterministic checker `scripts/llm-wiki lint` is liftable but welded to the `raw/` plus `wiki/{concepts,topics,references}` layout and the hub resolver.

**Fitting.** *Inputs:* a URL, a local file path, quoted text, an `inbox/` folder, or a collection adapter (git, MediaWiki dump or API, CSV or JSON message archive, Wayback CDX); on the compile side, any markdown file under `<wiki>/raw/<type>/` whose frontmatter carries `title, source, type, ingested, tags, summary`, whoever wrote it. A human-owned `schema.md` topic guide is read in full before compile planning. *Outputs:* `raw/<type>/YYYY-MM-DD-<slug>.md` with frontmatter and full content (PDFs get `content_format: pdf`, `sha256`, `page_count`, `extraction_tool`, `## Page N` headings); compiled articles under `wiki/<concepts|topics|references>/` with `sources:`, dual See Also links and a `## Sources` back-link block; per-directory `_index.md` tables; an append-only `log.md`. *Invocation:* slash commands `/wiki:ingest`, `/wiki:compile`, `/wiki:lint` and 27 others; the deterministic CLI is `python3 claude-plugin/bin/llm-wiki lint|schema|archive|retract|checkpoint`. *Harnesses:* Claude Code natively; Codex through a generated plugin with skills only and no slash commands; OpenCode through a single instruction file. Obsidian is an optional viewer. The wiki location resolves from `~/.config/llm-wiki/config.json`, then `~/wiki/`, then `<cwd>/.wiki/`; it is not Obsidian-vault-path aware.

**Surplus.** Parallel multi-agent web research and thesis investigation (the largest share of the 30 commands, and always-on skill context) is a cost here. The hub and multi-topic architecture with its registry and routing prompts coerces a hub-plus-topics layout, a cost against an existing vault. Deterministic lint with auto-fix that relocates files by frontmatter and quarantines unknowns is helpful for structure health and a cost against a caller-chosen layout. Inventory, ideas, projects and portfolio workflows; a dataset registry; session capture with harness hooks (a per-tool-use hook on Codex, nothing wired on Claude Code); private adapters and project knowledge checkpoints (about 1,500 lines of CLI for an execution plane the set does not need); personal specialist skills; an archive and retraction lifecycle; refresh, librarian and audit workflows with a freshness score, which is a helpful vault-side drift detector though it re-fetches source URLs rather than checking a local store; X.com, GitHub, Wayback and MediaWiki ingestion; and output generation into `output/`.

**Coverage.**

**D1 partial** (evidence). `tests/fixtures/golden-wiki/raw/papers/2026-01-01-sample-paper.md` line 7, with the format spec at `references/wiki-structure.md` lines 370-385.

```
summary: "A paper on evaluation methodology for AI agents, covering pass@k reliability metrics."
```

The only per-source page the tool emits is the immutable raw copy carrying the full text and a two-to-three-sentence `summary:`; PDFs are converted locally with `pdftotext -layout`, pypdf or pymupdf. There is no per-source key-points page: articles are per-concept and synthesized, and `references/ingestion.md` line 211 prefers synthesized clusters over one article per page. Key points from a source land inside concept, topic and reference articles that cite it.

**D2 does not** (claim). `claude-plugin/skills/wiki-manager/references/wiki-structure.md` lines 302-305, with the required set enforced at `scripts/llm-wiki` line 741.

```
The guide cannot redefine deeper global primitives: the `category` vocabulary
stays `concept`/`topic`/`reference`, the physical layout stays `raw/` →
`wiki/concepts|topics|references/`, and the required-frontmatter set stays
fixed. Additional topic fields remain optional to deterministic tooling.
```

No mechanism accepts a caller-supplied field list and fills it per source. Raw and article frontmatter sets are fixed and lint-enforced; extra fields are merely tolerated. The only route is prose: the human-owned `schema.md` has a free Source Conventions section, so a caller could write charting instructions there and rely on the agent honouring them in advisory mode, but the guide's declared scope is cardinality, boundaries and scope, and nothing validates the result. Floor requirement not met.

**D3 covers** (claim). `claude-plugin/skills/wiki-manager/references/compilation.md` line 138, with `SKILL.md` lines 68, 313 and `wiki-structure.md` line 246.

```
- **Honest disagreement**: When sources disagree, note the disagreement rather than picking a side
```

The structural half is evidenced by the shipped golden-wiki fixture: cross-source concept pages with `sources:` lists, a per-directory `_index.md` rebuilt from frontmatter, and an append-only `log.md` with dated operation entries. Contradiction handling is prose: compile must note disagreement rather than pick a side and set `confidence: low`; the deterministic lint only enum-validates `confidence`, and nothing checks that both sides were kept. Raw immutability guarantees neither side is deleted at the source layer. A thesis mode adds explicit Evidence For and Evidence Against sections with a Contradicted or Mixed verdict.

**D4 covers** (evidence). `scripts/llm-wiki` line 741, with `claude-plugin/commands/compile.md` lines 34 and 41.

```
require_fields(ctx, doc, ["title", "source", "type", "ingested", "tags", "summary"])
```

Ingest and compile are separate commands, and compile does not require that ingest created the file: it surveys `raw/` by `ingested:` date, rebuilds indexes from frontmatter, relocates any markdown file whose `type:` is in the raw vocabulary, and reports every raw file no article cites. A note written by another process needs only those six frontmatter keys and a location under `raw/`.

**D5 partial** (claim). `references/ingestion.md` line 324, against lines 102-103 and 290.

```
5. If a file with that slug already exists, append `-2`, `-3`, etc.
```

Single-source re-ingest is not a no-op: the same title on the same day gets a `-2` suffix and a new raw file, and nothing compares URL or content hash. Collection ingests are described as deduplicated on `collection` plus `upstream_id` plus revision, but no code path does it; the PDF `sha256` is recorded when known and never consulted. Compile is date-gated, which makes recompile of an already-compiled source a no-op without detecting an unchanged re-ingest.

**D6 covers** (evidence). `claude-plugin/.claude-plugin/plugin.json` lines 1-4, with the marketplace manifest and the skill.

```
{
  "name": "wiki",
  "description": "LLM-compiled knowledge base with Project Knowledge Checkpoints Export, personal specialist skills, trusted adapters, Idea-to-Project workflows, compact queries, inventory, datasets, ingestion, audits, sessions, research, and outputs.",
  "version": "0.24.4",
```

A shipped plugin manifest, marketplace manifest, skill and slash commands, with no external dependencies (Python standard library only; PDF extraction optionally uses poppler or a temporary virtual environment). Codex compatibility, recorded separately: a generated Codex plugin exists with its own manifest, marketplace file and bootstrap script, and its `SKILL.md` line 27 states that Codex plugins do not register Claude-style commands, so the workflows are invoked as `@wiki` natural language there; the Codex plugin also adds session hooks. The Claude manifest declares no hooks.

**D7 covers** (evidence). `scripts/llm-wiki` lines 29-35, with the layout spec at `wiki-structure.md` lines 44-131 and the enforcement code at lines 862-941.

```
RAW_TYPES = {"articles", "papers", "repos", "notes", "data"}
ARTICLE_CATEGORIES = {"concept", "topic", "reference"}
ARTICLE_DIRS = {
    "concept": "concepts",
    "topic": "topics",
    "reference": "references",
}
```

Covered on the second branch: layout requirements are stated explicitly and completely, from the hub path down to the per-wiki directory set. It does not work on a caller-chosen layout: compile step 0 and lint rules C11 and C12 relocate misplaced files by frontmatter and quarantine unknown files into `inbox/.unknown/`, and compile stops with "No wiki found" otherwise. The cost is that an existing vault must be adopted as a topic wiki or a `.wiki/` subtree and will be reshaped on the first `lint --fix`.

**D8 partial** (evidence). `scripts/llm-wiki` lines 869-870, with the slug fallback at lines 1530-1532 and the link form at `wiki-structure.md` lines 420 and 451.

```
        if source_type in RAW_TYPES:
            return root / "raw" / str(source_type) / doc.path.name
```

The stable id is the raw file path, not a separate citekey field; nothing in the body knows a citekey, and tool-driven ingest generates slugs from title plus date. But the code preserves whatever filename exists, the resolver matches stems with or without a date prefix, and the prose forbids renaming raw files, so a caller writing `raw/papers/<citekey>.md` gets that path in every article's `sources:` list. The id is positional, so a re-key is a rename that breaks existing `sources:` unless the slug fallback catches it.

**D9 partial** (claim). `claude-plugin/commands/ingest.md` line 179, with lines 151-161 and `compilation.md` lines 48-50.

```
4. User confirms: `y` (process all), `edit` (reassign items), `abort`
```

Review gates are documented but sit on the ingest side: a routing prompt per item, a batch confirmation table, an inventory queue, `--dry-run`, and a confirmation above 500 items. Before integration there is no configurable gate; compile writes articles directly, and the only stop is `schema_state: strict` on planned deviations from the topic guide. `compile --source <path>` gives per-source granularity by invocation rather than by setting.

**D10 covers** (evidence). `/LICENSE` lines 5-9 and `plugin.json` line 8.

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software
```

MIT at the repository root at the pinned commit, with the manifests declaring the same. Use and modification are permitted with attribution and notice retention.

**C1 does not** (claim). `references/ingestion.md` lines 9-15.

```
| Type | Directory | Auto-detect signals |
|------|-----------|-------------------|
| articles | raw/articles/ | General web URLs, blog posts |
| papers | raw/papers/ | arxiv.org, scholar.google, .pdf URLs/files, academic language |
| repos | raw/repos/ | github.com, gitlab.com URLs |
| notes | raw/notes/ | Freeform text, tweets, no URL |
| data | raw/data/ | small .csv, .json, .tsv URLs or files, dataset references |
```

Inputs are URLs, local files, PDFs, quoted text, an inbox folder, and five collection adapters. A grep of the whole body for `zotero` returns nothing: no local API, no Better BibTeX, no attachment or annotation reading.

**C4 partial** (claim). `references/ingestion.md` lines 276-281, with the command allow-list at `commands/ingest.md` line 4.

```
2. Try `pdftotext -layout <pdf> -` only if it is available and produces
   non-trivial text. If local poppler is broken, missing, or returns garbled
   output, do not keep retrying it.
3. Fallback to a temporary Python virtual environment and a PDF library:
   - Prefer `pypdf` for text-first PDFs because it is lightweight.
   - Use `pymupdf` when layout fidelity or extraction quality matters.
```

Local PDF-to-markdown with no cloud call is the documented flow, including an OCR-needed stub and `## Page N` boundaries. It is agent-driven prose rather than a shipped script, and it is not Zotero-attachment aware; it takes a path or a URL.

**C5 partial** (claim). `claude-plugin/skills/wiki-manager/SKILL.md` line 28, with the CLI docstring at `scripts/llm-wiki` lines 2-5.

```
Claude Code is both the compiler and the query engine — no Obsidian, no external tools.
```

No Obsidian process is needed anywhere. But ingest and compile run only as an agent inside a harness; the headless Python CLI has lint, archive, schema, retract, specialist, adapter and checkpoint subcommands and no ingest or compile. Headless-from-CLI holds for maintenance, not for note production.

**C6 covers** (evidence). `/LICENSE` lines 1-3. Same MIT licence as D10; the quote is the licence block above, at those lines.

**Treatment opinion: copy plus a delta.** Install-as-is does not apply against this set: D2 has no caller-supplied field list and the frontmatter sets are fixed and lint-enforced, D7 is met only by the states-its-layout branch while the layout is actively imposed, D8 has no id concept beyond the file path, and D1 yields a raw copy plus a short summary. What the body does well is separable and licence-clean: the compilation protocol, the six-key raw contract that lets another process write the input, the derived-index and append-only-log conventions, and the local PDF extraction ladder, together about 300 lines of runtime-neutral markdown under MIT. Copying them with two deltas would fit: citekey-as-filename for raw sources, which the code already tolerates because it preserves `doc.path.name` and resolves stems without the date prefix, and a per-project charting template section the compile step fills, with a compile-side review gate. The one question that would move this to install-as-is is whether the caller accepts a hub or `.wiki/` layout and is content to express charting fields as advisory prose in `schema.md`. A full fork carries the 30-command surface, hub resolver, adapters, checkpoints and sessions for nothing.

### 2. NousResearch/hermes-agent, `skills/research/llm-wiki`

Seeded. `https://github.com/NousResearch/hermes-agent/tree/main/skills/research/llm-wiki`. Pin `79445a496c86a19332ad786494b8384d2167e2d0` (main HEAD, 2026-09-05T00:24:51Z); the `SKILL.md` at that SHA is byte-identical to main, sha256 `0229e37c...b515b6`, and last changed in `1c94338` on 2026-08-08. Frontmatter `version: 2.1.0`. Kind: a single prompt-only `SKILL.md` of 507 lines. The pinned directory listing contains only that file: no scripts, templates, references, tests or schema. The Python block at lines 323-331 is a comment sketch, not runnable code.

**Maintenance.** Repository stars 241,518 at read time; `pushed_at` 2026-09-05. The skill file itself was last touched 2026-08-08 by a standards sweep across 42 bundled skills; earlier touches 2026-06-10, 2026-05-08, 2026-04-27, 2026-04-23. The skill does not meet its own repository's authoring rules 4 and 6 (a human author first, and ship scripts).

**Originator and supplier.** Originator per `SKILL.md` line 5 is `author: Hermes Agent`, that is, agent-drafted inside NousResearch; the pattern originator is Karpathy, credited at line 18. Supplier is NousResearch.

**Licence.** MIT, found, at the repository root, corroborated by `SKILL.md` line 6 and the repository API SPDX id.

```
MIT License

Copyright (c) 2025 Nous Research

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software [...] subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

IP assertions: nothing beyond the copyright line. The bracketed elision is at a clause boundary and drops only "and to permit persons to whom the Software is furnished to do so,".

**Verify.** Licence re-read at the pin and matching, including the elision. Pin confirmed: the SHA resolves, the file is 507 lines and 20,121 bytes with the recorded sha256, the frontmatter matches, and the pinned directory listing confirms the no-scripts claim. Two rows re-checked, none refuted. Two read-time drifts sit in the maintenance note rather than in a row: stars now 241,797 and `pushed_at` now later in the same day.

**Smallest part.** The SCHEMA.md template block, `SKILL.md` lines 109-213, which a caller writes into the vault as a file. Its separable sub-parts are the page frontmatter schema with `sources`, `confidence`, `contested` and `contradictions` (131-149), the raw frontmatter with `source_url`, `ingested` and `sha256` (151-165), the page thresholds (179-184) and the update policy (207-213). The index template (219-234) and the log template (242-253) lift on their own.

**Fitting.** *Inputs:* a source handed to the agent in conversation, meaning a URL, file, or paste; URLs and PDFs are fetched with the Hermes-native `web_extract`. Environment: `WIKI_PATH`, default `~/wiki`, read from `${HERMES_HOME:-~/.hermes}/.env`. Session start reads SCHEMA.md, index.md and the last 20 to 30 log entries. *Outputs:* `raw/<articles|papers|transcripts>/<descriptive-name>.md` with `source_url`, `ingested` and `sha256` frontmatter; entity, concept, comparison and query pages with YAML frontmatter and at least two wikilinks; index entries and header counts; log entries of the form `## [YYYY-MM-DD] ingest | Source Title`; a chat report of files touched. *Invocation:* natural language only; no CLI, no script entry point, no slash command. *Harnesses:* Hermes Agent. The vault works as an Obsidian vault out of the box, and an Obsidian-headless plus systemd recipe is given for servers. Claude Code would load the frontmatter, but the tool names must be mapped by the agent.

**Surplus.** A query operation filing substantial answers into `queries/`; a lint with 13 checks that is prose-only, so the agent writes the scanning code afresh each run; entity, comparison and query page types that fix folder names the rest of the body assumes; a tag taxonomy with add-before-use governance; confidence and contested frontmatter, which is helpful and directly supports the contradiction flagging; archiving, log rotation at 500 entries and index splitting; about 55 lines of Obsidian-headless and systemd setup requiring a paid sync subscription, which is a cost on every load; web capture through `web_extract`, which is the capture ownership D4 wants separated; Hermes-specific environment plumbing; and a pointer to `llm-wiki-compiler` as a batch alternative.

**Coverage.**

**D1 does not** (claim). `SKILL.md` line 279, with lines 300 and 137.

```
- **New entities/concepts:** Create pages only if they meet the Page Thresholds
```

The ingest procedure captures the source verbatim into `raw/` and then fans its content out into entity and concept pages; no step writes a page whose subject is the source itself with a summary and key points. The only hook is a `summary` value in the frontmatter `type:` enum, which has no producing step, no section list and no folder in the layout tree. The raw file gets `source_url`, `ingested` and `sha256`, not a summary.

**D2 does not** (claim). `SKILL.md` line 111, with the per-type section lists at 186-205.

```
Adapt to the user's domain. The schema constrains agent behavior and ensures consistency:
```

There is no per-source structured template and no mechanism for a caller-supplied field list. The nearest hook is the caller-edited SCHEMA.md, whose Include lists dictate sections per page type rather than per source, and since D1 is absent there is no per-source page to chart into.

**D3 covers** (evidence). `SKILL.md` lines 210-212, with the index and log templates, the `contested` and `contradictions` frontmatter, and the pitfalls at 497-498.

```
2. If genuinely contradictory, note both positions with dates and sources
3. Mark the contradiction in frontmatter: `contradictions: [page-name]`
4. Flag for user review in the lint report
```

Cross-source concept pages, a sectioned index template and an append-only log template are shipped as inline templates; the frontmatter schema carries `contested` and `contradictions`, and the lint step surfaces them. Two nuances: update policy step 1 says newer sources generally supersede older ones, applied before the keep-both rule, and line 184 archives fully superseded pages to `_archive/`, moved rather than deleted.

**D4 partial** (claim). `SKILL.md` line 259, with line 262, the raw contract at 155-161, the lint at 352, and Related Tools at 502-507.

```
When the user provides a source (URL, file, paste), integrate it into the wiki:
```

There is no integrate-only entry point: ingest step 1 owns capture. But `file` is an accepted input, `raw/` is a plain directory with a stated frontmatter contract another writer could satisfy, lint tolerates raw files lacking that frontmatter, and Related Tools explicitly contemplates another tool writing into the same vault. Steps 2 to 6 do not depend on step 1, so an agent could be asked to integrate a pre-existing raw note, but the body never names that as an operation.

**D5 covers** (claim). `SKILL.md` lines 267-268, with the schema at 155-165.

```
On re-ingest of the same URL: recompute the sha256, compare to the stored value —
     skip if identical, flag drift and update if different.
```

The no-op-on-unchanged rule and the `sha256` raw frontmatter field are specified, but nothing computes or compares the hash; the agent is instructed to do it inline each time. The skip rule is phrased for the same URL; for local files the only stated check is the generic drift scan in lint step 8.

**D6 partial** (claim). `SKILL.md` line 324, with the Hermes tool names at 262, 83-85 and 374-380, the frontmatter at 1-13, and the house rule at `skills/AGENTS.md` lines 32-36.

```
# Use execute_code for this — programmatic scan across all wiki pages
```

The frontmatter is agentskills-shaped, so Claude Code would load the folder, but every procedure names Hermes-native tools with Hermes call syntax, which is mandatory house style, and a Claude Code agent must translate them to WebFetch, Read, Grep and Bash. The wiki path is read from a Hermes `.env`. Whether Claude Code tolerates the extra frontmatter keys was not tested. Codex compatibility is the same status for the same reason. Not installable as-is in the sense of working unmodified.

**D7 covers** (evidence). `SKILL.md` line 38, with the layout tree at 51-65.

```
**Location:** Set via `WIKI_PATH` environment variable (e.g. in `${HERMES_HOME:-~/.hermes}/.env`).
```

Covered on the states-its-layout branch, not the caller-chosen-layout branch: the caller chooses only the root, and inside it the tree is fixed, with lint checks and search examples assuming those folder names. The tree diagram is the shipped layout spec.

**D8 partial** (claim). `SKILL.md` line 126, with `sources:` at 139 and the naming rule at 265.

```
- **Provenance markers:** On pages that synthesize 3+ sources, append `^[raw/articles/source-file.md]`
```

A stable per-source reference mechanism exists, the raw file path used in `sources:` frontmatter and in provenance markers, but the id is an agent-chosen descriptive filename rather than a caller-supplied identifier; there is no citekey concept and no field for an external id. A caller who names raw files by citekey gets citekey-keyed links for free, and nothing in the body specifies or enforces that.

**D9 covers** (claim). `SKILL.md` lines 271-272, with the pitfalls at 493-494 and bulk ingest at 386-394.

```
② **Discuss takeaways** with the user — what's interesting, what matters for
   the domain. (Skip this in automated/cron contexts — proceed directly.)
```

A per-source human gate is documented before any page is written, with an explicit opt-out for automated contexts, a scope-confirmation gate when ten or more pages would change, and a separately documented batch mode. Contradictions route to user review through lint. All prose; the gate is configurable only by context.

**D10 covers** (evidence). `LICENSE` lines 5-8 at the pin, with `SKILL.md` line 6.

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
```

MIT at the repository root; the skill's own frontmatter repeats `license: MIT`. Use and modification are permitted, with notice retention the only condition.

**Treatment opinion: copy plus a delta.** MIT permits both copying and modification. What survives verbatim is the SCHEMA.md template with its frontmatter schema, raw `sha256` contract, page thresholds and update policy, the index and log templates, the layout tree, and the orientation and pitfalls rules. What must be rewritten is every operation, because the tool names are Hermes-native (D6), there is no per-source page step (D1) and no caller-supplied field list (D2), capture and integrate are fused in ingest step 1 (D4), and the source id is an agent-chosen filename rather than a citekey (D8). The Obsidian-headless section and the Hermes environment plumbing would be dropped. If the rewritten operations end up larger than the retained templates, author-and-credit is the equally honest label, since the retained material is itself an instantiation of Karpathy's gist. Not install-as-is: three of six floor items scored at the time were does-not or partial.

**Facts carried from this body.** Hermes house style requires skill prose to name Hermes-native tools rather than shell utilities, which is why every Hermes SKILL.md carries tool names that do not exist in Claude Code or Codex (`skills/AGENTS.md` lines 32-36). The repository claims agentskills.io compatibility (`README.md` line 26). The skill points to `llm-wiki-compiler` as a Node CLI writing into the same Obsidian-compatible vault (lines 502-505). The headless-Obsidian recipe depends on a paid Obsidian Sync subscription (lines 432-433).

### 3. AgriciDaniel/claude-obsidian

Seeded ("staged transaction integration"). `https://github.com/AgriciDaniel/claude-obsidian`. Pin `ad67087cad22ad84cc3288f915588ae42c0c2b44`, HEAD of main, committed 2026-08-26T11:43:18Z; this is past tag v2.1.1 and the manifest still declares 2.1.1. Kind: Claude Code plugin manifest plus hooks over a portable Agent Skills package of 15 skills, 3 agent definitions, and a standard-library-only Python 3.11 CLI core.

**Maintenance.** Last push 2026-08-26; 14,631 stars, 1,463 forks, 140 open issues, 42 commits in the preceding 90 days; created 2026-04-07. Tags v2.0.0, v2.1.0, v2.1.1; HEAD carries unreleased fixes. CI with a ten-check matrix; `make test` runs the Python and shell suites.

**Originator and supplier.** AgriciDaniel (AI Marketing Hub), both. `ATTRIBUTION.md` also names a separate community early-access mirror at `github.com/AI-Marketing-Hub`, which was not examined.

**Licence.** MIT, found, at `LICENSE` lines 1-9, corroborated by `.claude-plugin/plugin.json` line 9, the marketplace manifest, and `CITATION.cff`.

```
MIT License

Copyright (c) 2026 AgriciDaniel (AI Marketing Hub)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software
```

IP assertions: `ATTRIBUTION.md` states the work is original, credits Karpathy's pattern as an independent implementation with no code copied, and excludes GPL-2.0 ITS CSS snippets from the public artifact, so the public tree carries no GPL material.

**Verify.** Licence confirmed at the pin (the record reflows hard line wraps; wording and copyright line identical, 1,088 bytes, standard MIT), corroborated by the plugin manifest. The marketplace manifest, `CITATION.cff` and `ATTRIBUTION.md` were not re-fetched, so the IP-assertion sentences above are unverified. Pin confirmed: the SHA and committer date match exactly, repository metadata matches within star drift, and all seven cited paths return 200 at that SHA. Three rows re-checked, none refuted.

**Smallest part.** The operation-transaction contract and engine: `skills/wiki/references/operation-transactions.md` (bundle shape at lines 44-63, the inspect to approval-hash to apply workflow at 25-40, failure semantics at 115-126) implemented by `claude_obsidian/transaction.py` (179 KB) whose only in-package imports are `paths.py` (14 KB) and `json_utils.py` (1 KB), with `tests/test_transaction.py` (104 KB). Second-smallest: the provenance schema, `skills/wiki/references/provenance.md` plus the `validate_source_ledger` and `validate_claim_ledger` rules in `ledgers.py`.

**Fitting.** *Inputs:* files staged by any process under `<vault>/inbox/` (the directory name is set by `.claude-obsidian.json`) or already under `.raw/`; pasted text; consented HTTPS URLs through an external runner the body does not ship. Text, markdown, JSON, CSV, YAML and HTML are read in full; PDF, EPUB and images yield hash, size and metadata only. Paths outside the vault are refused. *Outputs:* one `claude-obsidian.transaction.v1` JSON bundle applied atomically: immutable `.raw/captured/<sha256>.<ext>` copies, `wiki/sources/*.md`, `wiki/concepts/*.md`, `wiki/entities/*.md`, `wiki/questions/*.md` with flat YAML frontmatter, updates to `wiki/index.md`, `wiki/log.md` (newest first), `wiki/hot.md`, ledger records, `.raw/.manifest.json`, journals under `.vault-meta/transactions/<op-id>/`, and an optional git checkpoint. *Invocation:* `claude plugin marketplace add AgriciDaniel/claude-obsidian` then `claude plugin install claude-obsidian@agricidaniel-claude-obsidian`; skills `/claude-obsidian:wiki`, `wiki-ingest`, `wiki-query`, `save`, `wiki-lint`; CLI `python3 scripts/claude-obsidian.py init|adopt|capture plan|capture apply|transaction inspect|transaction apply|lint|checkpoint|migrate|doctor`. *Harnesses:* Claude Code natively (manifest, hooks, namespaced skills); Codex, OpenCode and Gemini through `bin/setup-multi-agent.sh` symlinking each skill into `~/.agents/skills`; Cursor and Windsurf per workspace. Obsidian is not required. Vault mutation needs POSIX directory descriptors and `fcntl.flock`, so Linux, macOS or WSL only; native Windows is refused.

**Surplus.** An autoresearch skill with a bounded web loop and egress consent (a cost, unasked network surface); `wiki-retrieve` with a contextual-prefix chunker, a standard-library BM25 index and an optional Ollama rerank (about 100 KB, a cost); `wiki-fold` log rollups (helpful at scale); `wiki-mode` filing routers for LYT, PARA and Zettelkasten; 15 skills in total, whose trigger phrases and context weight are a cost; a git checkpoint subsystem (50 KB, helpful but optional); release build and audit tooling (90 KB, a cost for a consumer); a capture queue for external runners that are not shipped; session hooks that are silent by default; a deterministic lint engine covering dead links, orphans, required frontmatter and ledger violations, which is helpful; prompt-injection hardening prose in every skill and agent, which is helpful; and a Windows and WSL compatibility layer plus multi-host installers, dead weight for a single-harness user.

**Coverage.**

**D1 covers** (evidence). `skills/wiki/references/frontmatter.md`, Source properties, lines 35-46 (quote at 45-46).

```
key_claims:
  - "No claims extracted yet."
```

A `source` page type is defined with a YAML property schema carrying `key_claims`, `source_id`, `sha256`, `authority` and `review_state`, and the ingest skill couples source summaries into the ingest bundle and instructs extraction of falsifiable claims, entities, concepts, contradictions and open questions. The summary prose itself is LLM-authored, and no shipped example shows a filled one. Input caveat: only text and markdown are read, the PDF adapter is `"maturity": "metadata-only"`, and the skill says PDFs require a host capability or a configured adapter, so a raw PDF in `inbox/` will not be digested by this body.

**D2 does not** (evidence). `claude_obsidian/lint_engine.py` line 48.

```
REQUIRED_FRONTMATTER_FIELDS = ("title", "type", "status", "created", "updated", "tags")
```

No slot anywhere accepts a caller-supplied field list: no skill parameter, no `.claude-obsidian.json` key (its five keys are fixed in `vault_ops.py`), no CLI argument, no template hook. `frontmatter.md` fixes the page types and the source property set, and the mode templates are per methodology rather than per project. The escape hatch a delta could use is rule 7, preserve unknown valid properties during an edit, plus the six-field lint minimum, so extra charting fields would not be rejected; but the tool provides no mechanism to inject them.

**D3 covers** (evidence). `claude_obsidian/ledgers.py` line 1149, inside `validate_claim_ledger`.

```
"accepted claims with fresh contradictory evidence require contested assessment or adjudication notes",
```

Contradiction handling is enforced by code: evidence items carry a `relation` from `{"supports", "contradicts", "context"}`; an accepted claim with fresh contradicting evidence fails validation unless the assessment is contested or the notes adjudicate; contested claims must cite contradicting evidence. `provenance.md` line 46 says to preserve contradictory evidence and not silently select a winner. The index template ships Sources, Concepts, Entities and Questions sections, and the log template says newest completed operations appear first. Append-only is convention rather than code: the engine permits `replace` on `wiki/log.md` under a SHA-256 precondition, and only the `fold` operation type is restricted to the fold page, index and log.

**D4 covers** (evidence). `claude_obsidian/capture.py` line 627, with the separate `capture plan` and `capture apply` subcommands.

```
"SOURCE_OUTSIDE_INBOX", "source is outside the configured inbox roots"
```

Capture is a byte copy into `.raw/captured/<sha256>.<ext>` and a separate CLI subcommand from the wiki-ingest skill; it only reads regular files already placed under the configured inbox roots by any process. The ingest skill states that pasted text and files already under `inbox/` or `.raw/` are read locally and remain user-owned and read-only, and the ingest agent analyses one local source the parent has already captured and placed in scope. The constraint is that the other process must write inside the vault.

**D5 partial** (evidence). `claude_obsidian/capture.py` line 938 in `plan_filesystem_batch`, with `tests/test_transaction.py` line 73.

```
skip_reason = "content-unchanged"
```

Two layers are enforced by code: capture is content-addressed by SHA-256 so re-capture of unchanged bytes is a no-op, and re-applying an identical bundle with the same operation id returns the prior result. The digest-level check is prose only: the skill instructs the model to compute SHA-256 and check `.raw/.manifest.json` and the source ledger, while the engine stores the record with no hash comparison, so nothing stops a re-digest of an unchanged source producing a new bundle.

**D6 covers** (evidence). `.claude-plugin/plugin.json` lines 1-3, with the marketplace catalogue, `hooks/hooks.json`, and the install command in `docs/install-guide.md` lines 26-27.

```
{
  "name": "claude-obsidian",
  "version": "2.1.1",
```

A native Claude Code plugin: manifest, marketplace catalogue, `hooks.json` with SessionStart and Stop command hooks using `${CLAUDE_PLUGIN_ROOT}`, and skills invoked as `/claude-obsidian:wiki-ingest`. `config/product-contract.json` declares `claude-code` support level native. Codex compatibility, recorded separately: the same file declares `codex-cli` compatible, and `bin/setup-multi-agent.sh` line 161 symlinks each skill into `$HOME/.agents/skills`; hooks are Claude-only adapters. Every skill shells out to the Python core, so the checkout must be reachable, and vault writes need POSIX descriptors and `flock`.

**D7 covers** (evidence). `claude_obsidian/paths.py` lines 278-282, with the root layout table in `WIKI.md`.

```
def is_initialized_vault(path: Path) -> bool:
    path = canonical(path)
    return (path / "wiki").is_dir() and (
        (path / ".obsidian").is_dir() or (path / ".raw").is_dir()
    )
```

Covered on the second branch: `wiki/` is hard-required for vault discovery and writes are confined to it. Fixed paths include `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, `wiki/overview.md`, the two ledgers, `.raw/.manifest.json`, `.vault-meta/` and the `.claude-obsidian.json` marker; only `source_inbox` and `legacy_raw` are configurable. Methodology modes re-route new pages but stay under `wiki/`. `adopt` on an existing Obsidian vault is non-destructive: it skips any path whose current hash exists unless forced.

**D8 partial** (evidence). `claude_obsidian/ledgers.py` lines 618-623, inside `validate_source_ledger`.

```
            expected_source_id = stable_source_id(kind, locator, content_hash)
            if source_id != expected_source_id:
                _error(
                    errors,
                    prefix,
                    f"source ID must equal canonical identity {expected_source_id}",
```

The source-ledger key is derived rather than caller-supplied: `src-` plus the first 20 hex of a SHA-256 over origin kind, canonical locator and content hash, and the validator rejects any record whose key differs. A caller id can live in the page title or filename (wikilinks resolve by title), in the free `source_id` frontmatter property, and in `source_manifest_updates` keys, which are free non-empty strings; the ingest agent also accepts a stable source identifier from the parent if assigned. The concrete delta would be an `aliases` or `external_id` field on the ledger record, or relaxing the identity check.

**D9 covers** (evidence). `claude_obsidian/transaction.py` lines 4495-4499 on the apply path.

```
        if not hmac.compare_digest(approved_plan_sha256, str(prelock_approval)):
            raise TransactionValidationError(
                "PLAN_CHANGED",
                "the transaction or selected vault differs from the reviewed approval_sha256",
            )
```

The review gate is enforced by code: `transaction inspect` emits an `approval_sha256` bound to the expanded plan and the resolved vault, and `transaction apply --approved-plan-sha256` refuses any drift. Granularity is per batch by design (the skill drafts a single bundle for the whole agreed batch and forbids per-source applies); per-source review is obtainable by choosing a batch of one. Workers are read-only, so the human gate sits at the orchestrator's single apply, and `capture apply` has the same gate.

**D10 covers** (evidence). `LICENSE` lines 1-3 with `plugin.json` line 9.

```
MIT License

Copyright (c) 2026 AgriciDaniel (AI Marketing Hub)
```

Standard MIT: use, copy, modify, merge, publish, distribute and sublicense with notice retention. No GPL material in the public tree.

**C1 does not** (evidence). `config/adapters.json` lines 11-13, the only implemented adapter.

```
      "id": "filesystem",
      "maturity": "implemented",
      "input": "local-file",
```

The only implemented capture adapter is a local filesystem byte copy from `inbox/`. A case-insensitive grep across all markdown, Python, JSON and shell files for `zotero`, `citekey`, `bibtex`, `doi` and `pmcid` returned nothing. No local API, no Better BibTeX JSON-RPC, no web API.

**C4 does not** (evidence). `config/adapters.json` lines 64-66, with the maturity definition at line 6.

```
      "id": "pdf",
      "maturity": "metadata-only",
      "input": "local-file",
```

`capture.py` detects the `%PDF-` magic and records kind, media type, size and hash only; text extraction is delegated to an `extract-pdf-content` runner capability the body does not ship. Local, but not implemented.

**C5 covers** (evidence). `scripts/claude-obsidian.py` lines 14-17, with the subcommand tree in `cli.py`.

```
from claude_obsidian.cli import main


raise SystemExit(main())
```

The whole mutation and lint surface is a headless Python CLI. Obsidian is never required; `mcp-setup.md` line 3 says the portable baseline reads vault files directly, and the Obsidian CLI is an optional read transport. The caveat for this lane is that nothing Zotero-shaped exists to run headlessly: the property holds, the capture does not.

**Treatment opinion: author to the design and credit it.** Install-as-is does not apply because of D2 (no caller-supplied field list, fixed page and property schema) and D8 (the source-ledger validator rejects any key other than the hash-derived one, which conflicts with citekey-keyed provenance); PDF input is metadata-only, so a Zotero-PDF-heavy vault gets nothing from the digest until text is extracted upstream. Between copy-plus-delta and author-and-credit, the seeded value lives in the contract, inspect to `approval_sha256` to a single apply with per-path SHA-256 preconditions, journaled rollback, idempotent operation ids, create-only raw payloads, and contradiction-requires-contested, and that contract is fully specified in two short reference files plus the ledger validation rules. The implementation behind it (179 KB of engine plus 104 KB of tests) hard-codes this vault's layout, write authorities, size limits, descriptor pinning and Windows refusal, so copying means editing a large coupled module to lift D2 and D8 and relax the layout, which is more delta than core. A thin engine written to the documented contract, keeping the claim-ledger rules verbatim as the specification and crediting the project, fits the consuming repository's own preference for eliminating a problem over adding a mechanism. If the concurrency and rollback guarantees later turn out to matter, copy-plus-delta of `transaction.py`, `paths.py` and `json_utils.py` remains open under MIT.

**Facts carried from this body.** Claude Code's Stop hook accepts no matcher, and Stop-time warnings return through the top-level `systemMessage` field while SessionStart adds context through stdout (`hooks/README.md` lines 16-17). The portable Agent Skills frontmatter subset that Claude Code, Codex, OpenCode and Gemini all accept is exactly `name` and `description`, and plugin skills are invoked namespaced rather than mirrored under `commands/` (`AGENTS.md` lines 39-42). Codex discovers user-level skills at `~/.agents/skills/<name>/SKILL.md`, matching the symlink topology this environment already uses (`bin/setup-multi-agent.sh` line 161).

### 4. atomicstrata/llm-wiki-compiler

Seeded ("deterministic compile, refresh, review"). `https://github.com/atomicstrata/llm-wiki-compiler`, npm `llm-wiki-compiler`, CLI `llmwiki`. Pin `cbd09c6c415f36b6001adf89a02aa805a5a5aba6` (main, 2026-09-03T09:37:40Z), package version 1.1.0 with an unreleased changelog section. Kind: Node.js CLI plus an MCP server and a TypeScript SDK, about 400 source files. Not a Claude Code skill or plugin: a recursive search at the pin for `skill`, `plugin`, `.claude`, `.codex` and `marketplace` returned nothing.

**Maintenance.** Last push 2026-09-03 (the HEAD commit adds the `codex-agent` provider); 1,997 stars; created 2026-04-05; not archived, not a fork; published on npm at 1.1.0; CI, husky hooks, several hundred vitest files; external contributors credited in the changelog.

**Originator and supplier.** Author `Ethan Joffe` in `package.json`, copyright holder `atomicmemory` in `LICENSE`, GitHub organisation `atomicstrata`. Three names for what appears to be one party; all three are recorded because the licence names one of them.

**Licence.** MIT, found, at `LICENSE` lines 1-9, with `package.json` line 40 and `README.md` line 384.

```
MIT License

Copyright (c) 2026 atomicmemory

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software
```

Also read: `docs/LICENSE` (MIT, copyright Mintlify, the documentation-site template rather than the tool) and `src/viewer/assets/THIRD_PARTY_NOTICES.txt` (vendored D3.js v7.9.0 under ISC, Space Grotesk and JetBrains Mono under SIL OFL 1.1, viewer assets only). IP assertions: none beyond the notice.

**Verify.** Two passes ran on this candidate. Licence re-read at the pin: the standard 21-line MIT text, lines 1-9 matching character for character including the copyright line; `package.json` line 40 and the author line at 41 confirmed. One pass records that the quoted licence block is truncated mid-line without an ellipsis. The README line and the two third-party notices were not re-fetched. Pin confirmed by both passes: SHA, committer date, creation date, star count, package version, `bin.llmwiki` and `engines.node >=24` all match, and the npm registry returns 200. Three rows re-checked in each pass. One refutation, on the D4 quote, for fidelity rather than for the finding; the second pass confirms the finding on the corrected line.

**Smallest part.** `src/compiler/prompts.ts` (340 lines): the `extract_concepts` tool schema with `confidence`, `provenance_state` and `contradicted_by`, plus `buildPagePrompt`, which fixes the `^[filename.md:START-END]` citation grammar. It depends only on types, output language and prompt modifiers. Two other standalone pieces: `src/utils/activity-log.ts` (128 lines, the append-only log format) and `SOURCES_CONTRACT.md` (147 lines, a producer contract for the ingest and integrate seam).

**Fitting.** *Inputs:* a flat `sources/` directory of markdown files, non-recursive, each with frontmatter `title`, `source`, `ingestedAt` and optional `sourceType`, `truncated`, `originalChars`; `llmwiki ingest` produces them from markdown, text, PDF (local `pdf-parse`), transcripts, images (an Anthropic vision call), web pages and YouTube; bodies are capped at 100,000 characters. Optional `.llmwiki/profile.json`, `config.json` and `schema.json`. *Outputs:* `wiki/concepts/<slug>.md` per merged concept with `sources[]`, `confidence`, `provenanceState`, `contradictedBy`, `modelId` and `promptVersion`, plus wikilinks and `^[file.md:L-L]` citations; `wiki/index.md`; `wiki/MOC.md`; an append-only `log.md`; `.llmwiki/state.json` with per-source SHA-256; review candidates; optional exports. *Invocation:* `npm install -g llm-wiki-compiler` (Node 24 or newer), then `llmwiki ingest`, `compile [--review]`, `review list|show|approve|reject`, `refresh --stale`, `lint`, `query`; compile and ingest run at the current working directory and only `serve` takes a `--root`. *Harnesses:* CLI first; Claude Code, Claude Desktop and Cursor through the MCP server; the LLM backend can be the local Claude Code login or the Codex CLI login. Obsidian opens the generated `wiki/` folder as a vault; there is no Obsidian plugin.

**Surplus.** Configurable lifecycle profiles with typed entities, relations, finite-state machines, workflows and signed template taps (about 200 files, a cost); hybrid retrieval with chunk embeddings and BM25 (needs an embedding provider); a local read-only web viewer with vendored D3 and fonts; an MCP server; Open Knowledge Format import and export plus JSON-LD, GraphML, Marp and llms.txt; an eval harness with a health score and LLM-judged citation support, which is helpful for auditing digests; lint rules for broken citations, cross-links, contradicted pages and staleness, which are helpful; a Crossref DOI connector requiring a contact email; session-transcript adapters; web, YouTube and image ingest, the last of which is a cloud vision call; a rule-extraction learning loop; and a multi-provider LLM abstraction, helpful for portability and a dependency cost.

**Coverage.**

**D1 does not** (evidence). `src/compiler/prompts.ts` line 159 and `src/compiler/extraction-merge.ts` line 96.

```
"and identify 3-8 distinct, meaningful concepts worth documenting as wiki pages.", | * Merge extractions so each concept slug maps to ALL contributing sources.
```

The compile pipeline emits per-concept pages, not a per-source page: extraction asks for three to eight concepts per source, then same-slug concepts from different sources are folded into one file. No code path writes a page whose subject is the source document. The `autosci` profile's `papers` entity looks like a per-source page, but no LLM writes it: every `callClaude` call site is in extraction, page rendering, seed pages, rule extraction, query, page selection or eval, and none is in workflows, trust, connectors or artifacts. Floor requirement not met.

**D2 does not** (evidence). `src/profile/field-contract.ts` lines 179-180, with the schema at `src/profile/schema/profile.v1.schema.json`.

```
 * Validate a page's parsed frontmatter against its entity type's declared field
 * contract, returning a list of PATH-FREE violation messages (empty when the page
```

The profile mechanism lets a caller declare a per-project field list with types, requiredness, enums and ranges, and the write gates validate frontmatter against it. But nothing fills those fields from a source document: staging accepts frontmatter the caller already populated, the Crossref connector fills from an API rather than from source text, and no `callClaude` site derives field values from a source. Validation is not filling, so the floor is unmet, though the field-contract plus JSON-schema pair is a clean model for a charting-template validator.

**D3 covers** (evidence). `src/compiler/extraction-merge.ts` line 81, `src/utils/activity-log.ts` line 2, `src/compiler/indexgen.ts` line 21, `src/linter/rules.ts` line 296.

```
  // Union contradictedBy entries, deduplicating by slug. |  * Append-only activity log (log.md). |  * Generate the wiki/index.md listing all concept pages with summaries. |       rule: "contradicted-page",
```

Same-slug concepts from many sources become one page carrying every contributor in `sources:`, with confidence as the minimum, provenance state merged and `contradictedBy` unioned. `wiki/index.md` is regenerated each compile; the log is appended with dated operation headings. Contradictions are kept and flagged rather than deleted: the extraction tool schema has `contradicted_by`, references are stamped into frontmatter, lint emits `contradicted-page`, the review policy holds contradicted pages, and pages whose source was deleted are marked orphaned rather than removed. The caveat is that the merged frontmatter is rebuilt from the current extraction, so a flag persists across a later recompile only if the model re-emits it.

**D4 covers, verify-refuted on the quote** (evidence). `SOURCES_CONTRACT.md` line 7, `src/compiler/hasher.ts` line 59, `test/compile-delta.test.ts` lines 83-84.

```
Anything that can write a markdown file with the frontmatter described here can feed |     return entries.filter((f) => f.endsWith(".md")); |     await writeFile(
      path.join(ctx.dir, "sources", SECOND_SOURCE),
```

Ingest and integrate are separate commands and the integrate side does not own source creation: `detectChanges` simply reads the `sources/` directory for markdown files and compiles whatever is there. `SOURCES_CONTRACT.md` is a dedicated, versioned input contract for a foreign producer, and the shipped test writes a source file directly and then compiles, which is a worked example. The constraint is a flat directory of markdown only. This is the one refuted row in the run. The record's own evidence field dropped the word `that` from line 7; the line reproduced above is the verbatim text both verify passes read at the pin, and the sentence continues on the following line. Both passes confirm the finding itself, and the other two quotes were verbatim in the record.

**D5 covers** (evidence). `src/compiler/hasher.ts` lines 81-83 with `test/commands/ingest-status.test.ts` line 29.

```
    if (!prev) return "new";
    if (prev.hash !== hash) return "changed";
    return "unchanged"; |   it("ingestSource: re-ingesting an unchanged file is a no-op (writeStatus + no journal)", async () => {
```

A SHA-256 of each source file is persisted in `.llmwiki/state.json` and unchanged files are skipped without an LLM call; re-ingest is also a no-op because `saveSource` compares a stable content key that excludes `ingestedAt`. The interaction with D4 is that the compiler hashes the entire file including frontmatter, so an external producer that rewrites a note with a fresh `ingestedAt` triggers a recompile.

**D6 does not** (evidence). `package.json` lines 15-17 with `docs/cli/serve.mdx` line 26.

```
  "bin": {
    "llmwiki": "dist/cli.js"
  }, | To connect Claude Desktop, Cursor, or Claude Code, add llmwiki to your MCP client's server configuration:
```

Not installable as a Claude Code skill or plugin: no `SKILL.md`, `.claude-plugin/`, `plugin.json` or marketplace manifest anywhere in the tree. It is an npm global CLI requiring Node 24 or newer, whose Claude Code path is an MCP server plus a `claude-agent` provider that reuses the local Claude Code login. Codex compatibility, recorded separately: a `codex-agent` provider runs `codex exec` sandboxed with the Codex CLI login, minimum Codex 0.152.1, and an adapter ingests Codex and ChatGPT conversation exports. No Codex skill or plugin either.

**D7 covers** (evidence). `src/utils/constants.ts` lines 144-145, 363 and 446, with `src/commands/compile.ts` line 27.

```
export const SOURCES_DIR = "sources";
export const CONCEPTS_DIR = "wiki/concepts"; | export const INDEX_FILE = "wiki/index.md"; | export const LOG_FILE = "log.md"; |   await compile(process.cwd(), options);
```

Satisfies the states-its-layout branch: `sources/`, `wiki/concepts/`, `wiki/queries/`, `wiki/index.md`, `wiki/MOC.md`, `log.md` and `.llmwiki/` are hard-coded constants and documented. It does not work on a caller-chosen layout: compile runs at the current working directory, `sources/` is flat and markdown-only, and concept pages always land in `wiki/concepts/`. The one caller-chosen element is a profile entity's `directory`, confined under `wiki/`. Output is declared Obsidian-compatible.

**D8 partial** (evidence). `src/compiler/citation-normalize.ts` lines 92-93 with `SOURCES_CONTRACT.md` line 93.

```
  // Case 1: valid filename — keep as-is.
  if (sourceFiles.includes(fileToken)) return trimmed; | stable `<producer-chosen-name>.md` of its own choosing — the compiler keys change
```

Provenance markers and the page `sources:` frontmatter are keyed on the source filename in `sources/`, and lint and eval validate against that filename. The caller-supplied `source` frontmatter URI is only the identity key for re-ingest and collision handling; it never reaches page links or export provenance. So a stable id works only if the caller puts it in the filename, which the contract explicitly permits and the hasher accepts. Id by filename, not id by field.

**D9 covers** (evidence). `src/compiler/review-pipeline.ts` lines 74-75 with `src/cli/review-commands.ts` line 46 and `docs/configuration/review-policy.mdx` line 7.

```
  if (options.review) {
    const heldReasons = [{ code: "manual-review-requested" } as HeldReason, ...reasons]; |     .command("approve <id>")
```

Two configurable gates before integration: `compile --review` holds every generated page as a JSON candidate under `.llmwiki/candidates/`, and a fail-closed review policy holds only pages tripping low-confidence, contradicted, schema-violating, provenance-violating or all. Approval is per candidate id, with no `--all`, and rejection archives. Granularity is per concept page rather than per source, and no batch approve is shipped.

**D10 covers** (evidence). `LICENSE` lines 1-3 with `package.json` line 40.

```
MIT License

Copyright (c) 2026 atomicmemory
```

MIT permits use and modification. The copyright holder differs from the organisation and the package author; no contributor agreement or additional IP assertion was found. The vendored viewer assets carry ISC and OFL notices that do not affect the compiler code.

**C1 does not** (evidence). `src/connectors/impl/crossref.ts` line 77.

```
  allowedHosts: ["api.crossref.org"],
```

No Zotero integration of any kind: a case-insensitive grep across the source, documentation, README and sources contract for `zotero`, `bibtex`, `citekey` and `pmcid` returned nothing. The only external-record connector is Crossref. This row exists because a caller might otherwise assume the `autosci` papers template reads a reference manager.

**C4 partial** (evidence). `src/ingest/pdf.ts` lines 4-5 and 40.

```
 * Reads a local PDF file using the pdf-parse v2 PDFParse class, extracts the
 * text content via getText() and the document metadata via getInfo(). The |   const { PDFParse } = await import("pdf-parse");
```

PDF-to-text is local with no network call, and the PDF title is read from the Info dictionary. It is not Zotero-attachment aware, and the result is truncated at 100,000 characters, which many full papers exceed. By contrast, image ingest is not local: it calls Anthropic vision.

**C5 covers** (evidence). `package.json` lines 15-17, with the MCP server and the SDK.

```
  "bin": {
    "llmwiki": "dist/cli.js"
  },
```

Runs headless from the CLI, from an MCP client, or in process through the SDK. Obsidian is never required: `src/compiler/obsidian.ts` only writes tags and aliases frontmatter and a `MOC.md` so the folder can be opened as a vault.

**C6 covers** (evidence). `package.json` line 40 and `LICENSE` line 1. Same MIT licence as D10.

**C7 does not** (evidence). `src/connectors/impl/crossref.ts` lines 78-79 and 81.

```
  inputs: ["doi"],
  draftFields: ["title", "doi", "authors", "year", "abstract", "stage"], |   requiresContactEmail: true,
```

Not a Zotero plugin and no Zotero-side lint. The Crossref connector does DOI-to-metadata lookup staged as a review candidate; it is tool-side, requires a contact email for the polite pool, and has no PMCID, citation-count or arXiv features.

**Treatment opinion: author to the design and credit it.** Three floor requirements are unmet: D1 (pages are per concept and merged across sources), D2 (caller-declared field lists are validated but never filled from source text) and D6 (an npm CLI and MCP server, not a Claude Code skill or plugin). D8 is reachable only by naming the source file after the citekey. That leaves a roughly 400-file TypeScript codebase with Node 24, a 100,000-character source cap, a current-working-directory-bound compile and a flat markdown-only `sources/` directory as a poor base to carry. What is worth reproducing under MIT credit is specific: the `^[file.md:START-END]` citation grammar and its lint; the `confidence`, `provenanceState` and `contradictedBy` contract with minimum, merged and union reconciliation; the dated append-only log format; the per-source SHA-256 state with orphan-not-delete semantics; the review-candidate hold policy with a fail-closed configuration; and `SOURCES_CONTRACT.md` as the model for an ingest and integrate seam a Zotero-side capture process can write into.

**Facts carried from this body.** The tool implements the gist's log convention as dated operation headings greppable with `^## \[` (`src/utils/activity-log.ts` line 4). It treats `~/.claude/settings.json`'s `env` block as a read-only credential source for Anthropic keys, below explicit process environment (`src/utils/claude-settings.ts` line 4). Crossref lookups are rate-limited to one request per second and declared to require a contact email (`src/connectors/impl/crossref.ts` lines 80-81). The input contract hashes the whole source file including frontmatter, so a producer that rewrites `ingestedAt` on every run defeats incremental no-op behaviour (`SOURCES_CONTRACT.md` line 41).

### 5. garrytan/gbrain

Seeded ("ingest gate, dream cycle"). `https://github.com/garrytan/gbrain`. Pin `8c70f6255047a7647adb30b1d6333a48068d9fa5` (master HEAD 2026-09-03; `VERSION` 0.48.2.0). Kind: a Bun and TypeScript CLI plus an MCP server and a Postgres or PGLite engine, with 67 markdown skills, shipped as a Claude Code plugin, a Codex plugin and an OpenClaw bundle.

**Maintenance.** Last push 2026-09-03; 29,593 stars; not archived; very high commit velocity (pull-request numbers above 4800) with per-release skill migrations tracked.

**Originator and supplier.** Garry Tan, both. Several skills carry an `upstream: <skill>@fc834ee` frontmatter key indicating a port from a private upstream fork; no separate licence is asserted for them.

**Licence.** MIT, found, at `LICENSE` lines 1-9, with `"license": "MIT"` in both the Claude and Codex plugin manifests and the API SPDX id.

```
MIT License

Copyright (c) 2026 Garry Tan

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software
```

**Verify.** Licence confirmed at the pin, matching verbatim apart from reflowed line breaks; corroborated by the plugin manifest and the API. No per-file headers were checked, so the claim that upstream-marked skills fall under the repository MIT is not independently verified. Pin confirmed: SHA, committer date and commit message match; stars drifted upward by 20. Three rows re-checked, none refuted.

**Smallest part.** `skills/brain-ingest-gate/SKILL.md`, a single 313-line markdown file, byte-identical to its copy under `plugin/skills/`. It is self-contained prose: a named-entity resolution gate, a read-the-top-hit dedup decision tree, and a one-line-per-item output table. Its only coupling is four CLI verbs that grep or ripgrep could replace. Runner-up: `docs/guides/compiled-truth.md` (147 lines), the rewrite-zone and append-only-timeline page contract, with the two-line conflict rule from `skills/_brain-filing-rules.md`.

**Fitting.** *Inputs:* markdown files with YAML frontmatter in a git repository (the system of record), drop-in files in `~/.gbrain/inbox/` (text types only unless a processor skillpack is installed), `gbrain capture`, and conversation transcripts for the dream cycle. PDFs must be pre-extracted to text or markdown. *Outputs:* pages written to the database and through to disk as `<repo>/<slug>.md`; concept pages and a `concepts/README.md` map; research folders with sources, summaries, a compendium and an index; a JSON cycle report; and per-page zones, compiled truth above a `<!-- timeline -->` sentinel with an append-only timeline below, plus machine-owned fenced tables between begin and end comment markers. *Invocation:* `gbrain sync|import|capture|dream|schema|check-backlinks`, an MCP server with seven memory verbs, and trigger phrases resolved by the host harness. *Harnesses:* Claude Code (native plugin with three marketplace variants), Codex (its own plugin and MCP config), OpenClaw and Hermes, plus plain CLI and cron. Not an Obsidian plugin, though an Obsidian-style vault can be the brain repository. Prerequisites: Bun, `gbrain init` with PGLite or Postgres, Unix only, optional API keys for embeddings and LLM phases.

**Surplus.** A Postgres or PGLite plus pgvector search engine with chunking, embeddings, rerank and multi-language full-text search (a cost: a database, a Bun runtime and optional API keys); an MCP server with OAuth, remote HTTP mode and an admin UI (a cost in attack surface); a durable job queue with worker pools and an autopilot daemon (heavy); dream-cycle maintenance phases beyond digest (helpful for backlink and orphan hygiene, at nightly LLM spend); a takes and facts epistemology layer (a helpful idea for D3's temporal verdicts, at the cost of two database tables); schema packs and lens packs (helpful for D7 layout adaptation); about 60 non-digest skills, which are routing noise; an eval framework; a personal-agent identity layer, opinionated and unrelated; and a privacy-wall convention that is helpful and liftable as prose.

**Coverage.**

**D1 partial** (claim). `skills/research-compendium/SKILL.md` lines 203-206, with `src/core/minions/handlers/ingest-capture.ts` lines 130-134 and `skills/bulk-ingestion/SKILL.md` lines 100-126.

```
For EACH source, write `research/<topic-slug>/summaries/NN-<source-slug>`, 150-300 words: **Source** (title + link) / **Type** / **Key findings** (bullets, with the actual numbers — effect sizes, percentages, speeds) / **Relevance** / **Caveats & limitations**.  ||  `ingest_capture: content_type '${event.content_type}' requires a content-type ` + `processor that is not yet installed. Install a processor skillpack ` + `(e.g. gbrain-audio-transcribe, gbrain-image-ocr) or pre-extract the ` + `content to text/markdown before emitting.`
```

Per-source summary and key-point pages are prescribed by several skills, but every one is markdown instructions executed by the host model; no shipped script emits the page. Markdown sources are handled natively; PDF text is not extracted by the runtime, which throws for `application/pdf` unless an external processor is installed, and the capture path documents that a captured PDF's real text is lost.

**D2 partial** (claim). `skills/bulk-ingestion/SKILL.md` lines 97-100 with `skills/data-research/SKILL.md` lines 58-61.

```
Define what a brain page looks like for this data type BEFORE ingesting anything. Every data type gets four artifacts:  ### 1a. Page template  ||  Define a custom recipe with: source queries, classification rules, extraction schema, tracker page path, tracker format
```

The field list is not fixed by the tool: bulk ingestion tells the agent to author a per-pipeline page template first, and data-research parameterises extraction through a per-recipe schema in `~/.gbrain/recipes/`. But no shipped mechanism takes a caller-supplied field list and fills it per source, the named built-in recipes are not present anywhere in the tree, and the schema-pack mechanism types pages by path prefix rather than defining per-source charting fields.

**D3 partial** (claim). `skills/_brain-filing-rules.md` lines 91-92, `docs/guides/compiled-truth.md` line 95, `skills/concept-synthesis/SKILL.md` line 72, `src/core/cycle/synthesize-concepts.ts` lines 1-22.

```
When sources conflict, note the contradiction with both citations. Don't silently pick one.  ||  | Timeline | **APPEND** | Evidence trail. Never edited, only added to. |  ||  Build a master concepts/README.md with the full map
```

Cross-source concept pages exist both as prose and as a shipped dream phase that groups extracted atoms across pages. The per-page timeline zone is append-only by convention and the consolidate phase never deletes facts. Contradictions keep both citations, the contradictions probe never mutates the brain, and supersede marks rather than deletes. Two gaps: the compiled-truth zone is rewritten, so a superseded claim survives only in the timeline, and concept synthesis issues reversible delete verdicts. All of it is convention rather than enforced code.

**D4 covers** (evidence). `src/core/ingestion/sources/inbox-folder.ts` lines 4-7, with `docs/architecture/system-of-record.md` lines 3-5 and `src/core/import-file.ts` line 288.

```
Watches `~/.gbrain/inbox/` by default. When a file appears (anyone can drop one — iOS Shortcuts share-extension, macOS AirDrop, Drafts export, Finder drag), the source emits an IngestionEvent then moves the file to `~/.gbrain/inbox/.archived/YYYY-MM-DD/<filename>`
```

Capture and integrate are separate layers by design: any process may write markdown into the brain repository (the system of record) or drop a file in the inbox, and `gbrain sync`, `gbrain import` and the inbox daemon index whatever is there. The tool does not own creation of the source file. The caveat is that binary inbox drops fail without a processor.

**D5 covers** (evidence). `src/core/import-file.ts` lines 728-730, with the hash formula at 710-717 and the daemon dedup window in `dedup.ts`.

```
if (existing?.content_hash === hash && !opts.forceRechunk) {
    return { slug, status: 'skipped', chunks: 0, parsedPage, ...(typeWarning ? { type_warning: typeWarning } : {}) };
  }
```

Re-importing an unchanged file at the same slug short-circuits on the content hash with no re-chunk and no re-embed. The hash deliberately excludes timestamp frontmatter keys so capture stamps do not defeat it. Cross-slug duplicates are skipped only when a frontmatter `id` matches. One body-internal discrepancy: a skill states that import and sync skip only matching frontmatter ids, while the code shows the same-slug skip is by content hash.

**D6 covers** (evidence). `.claude-plugin/plugin.json` lines 21-31, with the marketplace entries and the Codex manifest.

```
"skills": "./plugin/skills/",
  "mcpServers": {
    "gbrain": {
      "command": "${CLAUDE_PLUGIN_ROOT}/.agents/gbrain-launcher",
      "args": [
        "serve",
        "--surface",
        "starter",
        "--source-guard"
      ],
```

A native Claude Code plugin manifest with a skills directory and an MCP server entry, installable through a marketplace. Codex compatibility is first-class and separate: its own plugin manifest and MCP configuration. The caveat on as-is is that the skills drive the `gbrain` CLI, so the plugin is functional only after a global Bun install and `gbrain init`, and it is Unix only.

**D7 covers** (evidence). `docs/architecture/schema-packs.md` lines 164-171, with per-skill `writes_to:` frontmatter.

```
page_types:
  - name: project-x
    primitive: entity
    path_prefixes:
      - Projects/
    aliases: []
    extractable: false
    expert_routing: false
```

Both halves are met: the engine adapts to a caller-chosen layout through schema packs mapping arbitrary path prefixes to page types, and the layout the shipped skills assume is stated explicitly, with every writing skill declaring `writes_to:` and the filing rules naming the directory conventions. The layout is a git repository of markdown; there is no index or log convention, and the analogues are `concepts/README.md`, the per-page timeline and a `.raw/` sidecar.

**D8 partial** (evidence). `src/core/markdown.ts` line 308 with `src/core/import-file.ts` lines 768-769 and the citation format in `skills/conventions/quality.md`.

```
const slug = coerceFrontmatterString(frontmatter.slug) || inferSlug(filePath);  ||  - SKIP only when frontmatter.id matches (true external duplicate).
```

A caller can supply a stable id two ways: a frontmatter `slug`, which becomes the page slug that all links reference, and a frontmatter `id` honoured for cross-slug dedup, so a citekey-as-slug scheme works for links. Provenance markers, however, are free-text source citations with no id slot, and nothing in the body mentions citekeys.

**D9 partial** (claim). `skills/bulk-ingestion/SKILL.md` line 205 and line 52, with `skills/two-tier-extraction/SKILL.md` lines 128-130 and `skills/brain-ingest-gate/SKILL.md` lines 61-64.

```
Review trial results with the user. Ask:  ||  **Ambiguous** (partial match, pattern inside quoted third-party text, low-confidence contact match) → **fail closed**: divert to a human-review queue. Never send ambiguous content to the LLM "to check."  ||  Nothing in the gbrain runtime mechanically blocks an unenriched or duplicate write if the skill never loads.
```

A batch-style human gate is documented (test before bulk, a trial-and-evaluate loop, a fail-closed review queue), but it is not a configurable runtime gate: the ingest gate is explicitly a routing convention, the dream dry run does not mean zero LLM calls, and per-source versus batch is not a setting. The one real interactive gate is on schema-type promotion, not on page integration.

**D10 covers** (evidence). `LICENSE` lines 5-9 with the plugin manifest.

```
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software
```

MIT permits use and modification with notice retention.

**C4 does not** (evidence). `src/core/minions/handlers/ingest-capture.ts` lines 126-129 with `src/core/capture-content.ts` lines 126-131.

```
// Binary content without a processor would land as a path-string
      // page, which isn't useful. Surface as job-level error so the
      // operator sees the gap in `gbrain doctor` and can decide whether
      // to install the appropriate skillpack-distributed processor.
```

No local PDF-to-text: PDF events are rejected until an external processor skillpack is installed, and the capture path documents that PDF text is lost. A skill line saying to extract text or OCR is an instruction to the agent with no shipped extractor.

**C5 covers** (evidence). `src/commands/dream.ts` line 21 with the `package.json` bin entry.

```
 * Cron: 0 2 * * * gbrain dream --json >> /var/log/gbrain-dream.log
```

Everything runs from the CLI or the MCP server; no Obsidian or other GUI dependency. Requires the Bun runtime and a PGLite or Postgres brain.

**C7 does not** (claim). `skills/academic-verify/SKILL.md` lines 71-72 with `skills/citation-fixer/SKILL.md` lines 33-41.

```
academic-verify is a thin orchestrator. The actual web search is done by [perplexity-research](../perplexity-research/SKILL.md).
```

The repository contains zero Zotero references. The nearest capabilities are vault-side: claim and DOI tracing routed through a cloud search, and a lint of the citation format. Neither is Zotero-side enrichment, so nothing here would be replicated by the vault.

**Treatment opinion: copy plus a delta.** Installing gbrain as-is means adopting a Bun CLI, a database, an MCP server and 67 skills whose page model is a personal-CRM brain, far more than the digest lane asked for; its native PDF path is absent, its charting template is caller-authored prose, and its human gate is convention only. What is valuable and MIT-licensed is a handful of tool-agnostic prose contracts: the ingest gate's read-the-top-hit dedup bands, the compiled-truth and timeline page zones with their sentinel, the note-the-contradiction-with-both-citations rule, the research compendium's one-to-one sources, summaries and index folder contract, and the idempotency rules (a content hash excluding timestamp frontmatter, plus a frontmatter id for cross-path dedup). Copying those sections and re-keying them to citekeys and a caller-supplied field list, with attribution, fits. A fork is unwarranted because the runtime is not wanted, and copy-frozen is too rigid because the conventions must change from slug and entity vocabulary to citekey and charting vocabulary.

**Facts carried from this body.** The content hash excludes timestamp-bearing frontmatter keys so re-ingest of identical content is a no-op even when capture stamps a new time (`src/core/import-file.ts` lines 620-622). Cross-path duplicate policy skips only on a matching external frontmatter id and warns when content matches but identity differs (lines 768-771). A page can be split into a rewritable zone and an append-only zone at a sentinel comment, with a documented precedence order (`docs/guides/compiled-truth.md` lines 116-123), and machine-owned fenced tables can be delimited by begin and end HTML comments with markdown staying canonical (`docs/architecture/system-of-record.md` line 55). The contradiction verdict enum has six members including temporal supersession, regression and evolution, with an effective date threaded into the judge prompt (`docs/contradictions.md` lines 155-159). PGLite is single-writer, so the first running server owns the data directory for its lifetime (`docs/mcp/CLAUDE_CODE.md` lines 61-63).

### 6. swarmclawai/swarmvault

Seeded ("approval bundles, shrink guard"). `https://github.com/swarmclawai/swarmvault`. Pin `815412d24298e59e5073ded1ddd6c0e6aee9b91b` (main, "chore: release SwarmVault 3.21.0", 2026-06-30). Kind: a TypeScript tool with a CLI, an MCP stdio server, an engine library, a React viewer and an optional desktop-only Obsidian plugin.

**Maintenance.** Last push 2026-06-30; 679 stars; created 2026-04-06; not archived; five minor releases from 3.17.0 to 3.21.0 with detailed changelog entries, so a rapid cadence up to about two months before this run.

**Originator and supplier.** SwarmVault (the copyright holder, with `authorUrl` swarmvault.ai) as originator; the GitHub organisation `swarmclawai` and the npm scope `@swarmvaultai` as supplier.

**Licence.** MIT, found, at `LICENSE` lines 1-9, with `"license": "MIT"` in the CLI, engine and Obsidian-plugin manifests and the API SPDX id.

```
MIT License

Copyright (c) 2026 SwarmVault

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software
```

IP assertions: the copyright line only; no contributor agreement, patent grant or trademark clause in the licence, the contributing guide header, or the package manifests.

**Verify.** Licence confirmed at the pin, matching including the grant text; the CLI manifest and the API SPDX id agree; the licence file is the standard 21-line MIT. Pin confirmed: SHA, message, author date, star count and push date all match, and every cited path returns 200 at the pin. Three rows re-checked, none refuted.

**Smallest part.** The shrink guard: `shrinkDimension` and `evaluateGraphShrinkGuard` in `packages/engine/src/watch.ts` lines 120-152, a pure function over previous and next node and edge counts with a default 0.25 threshold and a message telling the user to re-run with `--force`. Next smallest: the approval-bundle shape, the `ApprovalEntry` and `ApprovalManifest` types plus `stageApprovalBundle`, `acceptApproval` and `rejectApproval`. Both are separable from the code-graph, MCP and viewer machinery, though staging depends on the engine's path and graph types.

**Fitting.** *Inputs:* local file paths, directories or URLs through `swarmvault ingest`, `swarmvault add`, `swarmvault inbox import` and `swarmvault source add`: markdown, PDF (pdfjs text layer), DOCX, RTF, ODT, EPUB, CSV, XLSX, PPTX, `.bib` (through the Better BibTeX author's parser), transcripts, audio and video (needing a provider), and code trees. Configuration through `swarmvault.config.json` and a free-text `swarmvault.schema.md`; markdown frontmatter `title` steers the source id slug. *Outputs:* `wiki/sources/<sourceId>.md` with frontmatter and Summary, Concepts, Entities, Claims with `[source:...]` markers and Questions; concept and entity pages with Seen In and Source Claims; `wiki/index.md` and per-folder indexes; an append-only `wiki/log.md`; dashboards including contradictions; a graph report and `state/graph.json`; per-source manifests with content and semantic hashes; and staged approval bundles under `state/approvals/<id>/`. *Invocation:* `npm install -g @swarmvaultai/cli` (Node 24 or newer), then `init`, `ingest [--guide|--review]`, `compile [--approve]`, `review list|show|accept|reject`, `candidate`, `graph update`, `lint`, `mcp`. The engine is importable. *Harnesses:* CLI first; Claude Code through `swarmvault install --agent claude --hook --mcp`, which writes a thin skill, a graph-first hook, a managed CLAUDE.md block and an MCP entry; Codex through `.agents/skills` and its own hook; Obsidian through a desktop-only plugin that shells out to the CLI. LLM synthesis requires configuring a provider inside SwarmVault, the default being a heuristic first-sentences summarizer.

**Surplus.** A code knowledge graph over 40-plus languages through tree-sitter (about 8,600 lines, the dominant cost and irrelevant to a literature vault); graph-first agent hooks that deny or annotate broad searches (a cost that would intercept normal vault searches unless disabled); an MCP server with about 40 tools; a React graph viewer and workbench; chat sessions, context packs and task ledgers; audio, video and image transcription needing extra binaries; a multi-provider LLM layer whose configuration determines digest quality; installers for about 60 agent targets; Neo4j push and several graph exports; PII and secret redaction at ingest, a sensible default; the `init --lite` minimal starter, which is a small faithful seed and separable; and the research-profile default schema text, whose wording about preserving contradictions is reusable.

**Coverage.**

**D1 covers** (evidence). `packages/engine/src/markdown.ts` line 405 in `buildSourcePage`, with `## Summary` at line 370, PDF text at `extraction.ts` line 801, and the worked example at `test/vault.test.ts` line 3192.

```
? analysis.claims.map((claim) => `- ${claim.text} [source:${claim.citation}]`)
```

`buildSourcePage` writes `wiki/sources/<sourceId>.md` with frontmatter and the sections title, Source ID, Summary, Concepts, Entities, Claims each carrying a source marker, and Questions. PDFs are text-extracted locally with `pdfjs-dist` into `state/extracts/` before analysis, and markdown is ingested directly. The caveat is that with the default heuristic provider the summary is the first three sentences and claims are sentence heuristics; a configured LLM provider is needed for real synthesis.

**D2 does not** (evidence). `packages/engine/src/analysis.ts` line 31, with the guided-session questions at `sources.ts` line 909.

```
const sourceAnalysisSchema = z.object({
```

The per-source structured output is a fixed Zod schema (title, summary, concepts capped at 12, entities capped at 12, claims capped at 8 with text, confidence, status, polarity and citation, questions, tags) validated on every provider response. The caller's `swarmvault.schema.md` is injected as free-text instructions and cannot add fields such as population, design or a page locator to the structured record or the rendered sections. The only structured per-source question-and-answer path uses five hard-coded question ids.

**D3 covers** (evidence). `packages/engine/src/logs.ts` line 66 in `appendLogEntry`, with index rebuilding in `vault.ts` lines 3482-3494 and contradictions kept as graph edges at lines 3331-3332.

```
await fs.writeFile(logPath, `${existing}${entry}\n`, "utf8");
```

Concept and entity pages aggregate across sources with a `source_ids` list, a Seen In section and per-source claims; `wiki/index.md` and per-folder indexes are regenerated each compile; `wiki/log.md` is read then appended and never rewritten, and the lite-mode header states it is an append-only chronological record. `detectContradictions` keeps both claims with their source ids and confidences, surfacing them as `contradicts` edges, in the graph report and in a contradictions dashboard; nothing deletes a side, and a separate human-driven supersede marks rather than deletes. Caveats: concept pages are regenerated wholesale from analyses each compile except for guided-session marker blocks, and the built-in contradiction detection is a polarity plus token-overlap heuristic, with LLM-graded checks living in deep lint.

**D4 covers** (evidence). `packages/engine/src/ingest.ts` line 2112 in `persistPreparedInput`, with the CLI description at `packages/cli/src/index.ts` line 1171, the worked example in `test/vault.test.ts`, and `importInbox` at `ingest.ts` line 4087.

```
const storedPath = path.join(paths.rawSourcesDir, `${sourceId}${prepared.storedExtension}`);
```

Ingest and compile are separate commands and separate engine functions. `swarmvault ingest <path>` accepts a file written by any other process at any path and records its original path for later re-ingest; `swarmvault inbox import` sweeps a drop folder. The tool does not create the source note; it copies it into `raw/sources/`, and the skill states the design rule that raw sources are kept immutable.

**D5 covers** (evidence). `packages/engine/src/ingest.ts` line 2103, guarded by content, semantic and extraction hashes at 2083-2102, with tests at `vault.test.ts` line 3251 and `managed-sources.test.ts` line 190.

```
return { manifest: existingByOrigin, isNew: false, wasUpdated: false };
```

Re-ingesting a path whose SHA-256 over payload and attachments matches the stored manifest returns the existing manifest without rewriting anything; a second hash lookup dedupes identical content at a new path. The semantic hash ignores non-semantic markdown frontmatter, so a cosmetic edit re-stores the file while compile reports zero changed pages. The managed-source test shows a second add returning unchanged with no compile.

**D6 partial** (evidence). `packages/engine/src/agents.ts` line 219, with the hook install at line 834 and the Codex targets at 220 and 1047.

```
claude: [".claude/skills"],
```

There is a real Claude Code integration: `swarmvault install --agent claude --hook --mcp` writes a skill under `.claude/skills/swarmvault/`, a hook, a managed CLAUDE.md block and an MCP entry. But the skill is a thin front door that only lists CLI commands, and the digest itself runs inside the separately installed Node 24 CLI using SwarmVault's own provider layer, so the host model is not the digest engine and installable-as-is holds only for the wrapper. Codex compatibility, recorded separately: a project skill under `.agents/skills/`, a user skill under `~/.codex/skills`, and a Codex hook.

**D7 covers** (evidence). `packages/engine/src/config.ts` line 148 with the workspace block at 146-154 and the fixed sub-layout in `vault.ts`.

```
rawDir: z.string().min(1).default(WORKSPACE_DIR_DEFAULTS.rawDir),
```

Top-level directory names are caller-configurable and can be relocated wholesale with an environment variable; the layout below `wiki/` is fixed and documented. It does not adopt an existing vault's notes in place: existing notes become sources only if ingested. `init --lite` creates the minimal raw, index, log and schema layout for an agent-maintained wiki.

**D8 partial** (evidence). `packages/engine/src/ingest.ts` line 2110, with the provenance format at `markdown.ts` lines 353 and 405.

```
const sourceId = previous?.sourceId ?? `${slugify(prepared.title)}-${contentHash.slice(0, 8)}`;
```

Every page and claim carries the source id in frontmatter, in a `Source ID:` line and in `[source:...]` claim markers, and the id is stable across re-ingest of the same origin path. But the id is tool-derived, a title slug plus an eight-character content-hash suffix. A caller can steer the prefix by setting `title: <citekey>` in markdown frontmatter, yielding `<citekey>-<hash8>`, but cannot supply the id, and new content at a new path gets a new suffix.

**D9 covers** (evidence). `packages/cli/src/index.ts` line 1219 for the per-source gate, with `stageApprovalBundle` at `vault.ts` line 3053 and accept and reject at 4487 and 4592.

```
const guideEnabled = options.guide ?? vaultConfig?.config.profile.guidedIngestDefault ?? false;
```

Two documented, configurable gates: per source (`ingest --guide` or `--review`, defaulting from a profile setting, with a canonical-review mode staging canonical edits into an approval bundle) and per batch (`compile --approve`, staging every changed page under `state/approvals/<id>/` with a manifest whose entries carry pending, accepted or rejected status, then `review list|show|accept|reject` applying or discarding per entry with unified diffs). Decay and consolidation passes are skipped while a bundle is staged.

**D10 covers** (evidence). `LICENSE` line 1 with the grant at lines 5-10 and `packages/cli/package.json` line 29.

```
MIT License
```

MIT permits use and modification; the only conditions are retaining the copyright and permission notice.

**C4 covers** (evidence). `packages/engine/src/extraction.ts` line 801 in `extractPdfText`, with `docs/pdf-extraction.md` lines 12 and 18.

```
const pdfjs = await import("pdfjs-dist/legacy/build/pdf.mjs");
```

Attachment-style PDFs are converted to text in process with `pdfjs-dist` and no network call; the documentation states it needs no provider API key and that the heuristic path produces usable extractions with no network. It is not Zotero-aware, so it covers only the PDF-to-text-locally half when given a file path, and scanned PDFs with no text layer produce empty extractions because there is no OCR.

**C5 covers** (evidence). `packages/cli/package.json` line 31, with the engine exercised headlessly in the test suite and the Obsidian plugin shelling out to the CLI.

```
"swarmvault": "dist/index.js",
```

Everything runs from the CLI, an MCP stdio server, or the engine library; Obsidian is only an optional desktop front end. Node 24 or newer is required.

**Treatment opinion: author to the design and credit it.** Installing as-is is a poor fit: the two floor gaps are structural (D2's fixed Zod analysis schema with no caller fields, and D8's tool-derived ids with a hash suffix), the sub-layout and provider configuration are imposed, Node 24 plus a roughly 54,000-line TypeScript engine dominated by code-graph, MCP, viewer and agent-memory features would be carried for a literature vault, and the Claude Code skill is only a thin wrapper. Forking to strip that down means maintaining a large engine for a few hundred useful lines. The mechanisms of interest are small designs rather than code to lift: the shrink guard (abort a refresh when node or edge counts drop more than a ratio, overridable); the approval bundle (stage changed pages under an id with a manifest of entries, then accept or reject per entry with diffs, with per-source and per-batch entry points); content-hash plus semantic-hash no-op re-ingest keyed by origin path; an append-only log with dated verb and subject entries; and contradictions kept as both-sided records surfaced on a dashboard rather than resolved. All are cheap to re-author and credit. Copy-frozen of the shrink guard alone would be acceptable in a TypeScript vault, but the function is trivial enough that authoring costs less than importing its types.

**Facts carried from this body.** SwarmVault parses `.bib` files with `@retorquere/bibtex-parser`, the Better BibTeX author's parser, so the parser the Zotero ecosystem relies on is already vetted for Node ingestion of BibTeX exports (`packages/engine/src/extraction.ts` line 2144). BibTeX citekeys are rendered only as list text inside the extracted markdown of a `.bib` source, one page for the whole library and the first 200 entries, and never become page ids (line 2189). PDF extraction is text-layer only, with no OCR in the default path (`docs/pdf-extraction.md` line 18). The CLI requires Node 24 or newer (`packages/cli/package.json` line 38). The repository never mentions Zotero: a case-insensitive grep across all TypeScript, markdown and JSON files at the pin returned no matches.

### 7. Pratiyush/llm-wiki

Seeded ("maturity frontmatter"). `https://github.com/Pratiyush/llm-wiki`, PyPI `llm-notebook`, CLI `llmwiki`. Pin `b1088890ee0743810a92577aecad946c6b3eb2d2` (master HEAD, 2026-06-14; package version 1.3.82). Kind: a Python CLI package plus project-scoped Claude Code slash commands and skills, a `CLAUDE.md` and `AGENTS.md` ingest schema, and a `.claude-plugin` manifest. Its native input is coding-agent session transcripts.

**Maintenance.** Last push 2026-06-18; HEAD commit 2026-06-14; 383 stars; created 2026-04-08; changelog at 1.3.82 with an unreleased section; more than 700 issue and pull-request numbers referenced in code comments. Active and very fast-moving, with Cursor-agent co-authored commits.

**Originator and supplier.** Pratiyush, both; not a fork. Commits are co-authored with a Cursor agent.

**Licence.** MIT, found, at `LICENSE` lines 1-21, corroborated by `pyproject.toml` line 11, `.claude-plugin/plugin.json` line 11, `llmwiki/__init__.py` line 20 and the README.

```
MIT License

Copyright (c) 2026 Pratiyush

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
```

IP assertions: none beyond the notice. The acknowledgements credit Karpathy's gist and four prior-art repositories as influences rather than as vendored code.

**Verify.** Licence confirmed at the pin verbatim, with the two manifest declarations at the cited lines; the repository is not a fork, so there is no upstream licence conflict. Pin confirmed: SHA, date and commit message match, including the Cursor co-author trailer; the package version matches. Three rows re-checked, none refuted.

**Smallest part.** The synthesis subsystem `llmwiki/synth/`: `pipeline.py` (discover raw markdown, mtime state, `_build_source_page`, `_rebuild_index`, `_append_log`), `base.py`, `agent_delegate.py` (a pending-prompt sentinel plus `complete_pending`) and `prompts/source_page.md`, plus the standard-library frontmatter parser. About 60 KB, standard library only, though it imports the package root constant and a tag helper that would need stubbing. Smaller still: `prompts/source_page.md` alone, or the `CLAUDE.md` ingest workflow and source page format sections as agent prose.

**Fitting.** *Inputs:* markdown files under `<repo>/raw/sessions/` (or `<vault>/raw/sessions/` with `--vault`) with optional frontmatter `slug`, `project`, `date`, `title`, `model`, `source_file`, `tags`; an optional prompt override at `<repo>/wiki/prompts/source_page.md` with `{body}` and `{meta}` placeholders; a configuration file selecting the synthesis backend (dummy, Ollama or agent). Environment variables detect a running Claude Code, Codex or Cursor session. *Outputs:* `wiki/sources/<project>/<date>-<slug>.md` with frontmatter and Summary, Key Claims, Key Quotes, Connections and Contradictions sections; a rewritten index Sources section; one appended log entry with auto-archiving at 50 KB; an mtime state file. The agent backend additionally writes a pending prompt file and a placeholder page whose first line is a UUID sentinel. Entity, concept and synthesis pages and contradiction content are produced by the agent following `CLAUDE.md`, not by code. *Invocation:* `python3 -m llmwiki synthesize|all|candidates|init|sync|lint|build`, or Claude Code commands `/wiki-ingest`, `/wiki-sync`, `/wiki-synthesize`, `/wiki-candidates`, plus skills that auto-trigger on ingest phrasing. *Harnesses:* Claude Code through project-scoped commands and skills loaded by opening the clone; Codex through `AGENTS.md` and a skill installer that mirrors skills into `.codex/skills/`; plain CLI with a single dependency; Obsidian through a vault overlay and Templater templates; an MCP stdio server with twelve read and lint tools. Runtime paths are anchored to the clone.

**Surplus.** A static-site compiler and server (113 KB plus 117 KB of renderers, the bulk of the repository and irrelevant to vault pages); coding-agent session adapters with redaction and quarantine (not needed for Zotero-captured sources, though the raw write guard is a reusable idea); a local Ollama backend with a localhost privacy check, which is helpful for offline digest; the agent-delegate backend, a helpful zero-API-key pattern; the candidates approval workflow, a concrete review gate; sixteen lint rules, helpful for hygiene though the contradiction and claim rules are stubs needing an LLM callback; a wikilink graph and exporters; confidence scoring, a lifecycle state machine and nine seeded navigation files, which are clutter in a real vault; AI-suggested tags; a vault-overlay mode that is helpful in principle but ignored by synthesize at this pin; and an MCP server, VS Code extension, Obsidian plugin, Homebrew formula, Dockerfile, Nix flake, GitHub Action and Playwright suite.

**Coverage.**

**D1 covers** (evidence). `llmwiki/synth/prompts/source_page.md` lines 35-42, with the pipeline at `pipeline.py` line 9 and lines 697-703.

```
## Summary

2-4 sentence synthesis of what the session accomplished. Focus on
decisions made, problems solved, and tools/libraries chosen.

## Key Claims

- Claim 1 (a concrete, falsifiable statement from the session)
```

A shipped prompt template plus a shipped pipeline that reads each markdown file under `raw/sessions/`, calls a backend and writes `wiki/sources/<project>/<date>-<slug>.md`. Real backends exist: a local Ollama HTTP client and an agent-delegate backend that writes the rendered prompt to a pending file for the running Claude Code or Codex agent to fill. The default backend is a dummy that emits a skeleton. Input is markdown only: the PDF adapter was removed, and although the ingest skill's description still mentions PDF, nothing in the body handles it.

**D2 partial** (evidence). `llmwiki/synth/pipeline.py` lines 110-117, with the command documentation at `.claude/commands/wiki-synthesize.md` lines 42-43.

```
USER_PROMPT_OVERRIDE = REPO_ROOT / "wiki" / "prompts" / "source_page.md"


def _load_prompt_template() -> str:
    """Load the synthesis prompt template. User override wins."""
    if USER_PROMPT_OVERRIDE.is_file():
        return USER_PROMPT_OVERRIDE.read_text(encoding="utf-8")
    return PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
```

The caller can replace the whole synthesis prompt per checkout and therefore dictate any section list. But it is a whole-prompt override rather than a field list: it must keep the placeholders and a suggested-tags contract, the frontmatter fields are hard-coded in `_build_source_page` so caller fields live only in the body, the override path is inside the clone rather than per vault even in vault mode, and the agent backend truncates the source body to 8,000 characters.

**D3 partial** (claim). `CLAUDE.md` line 54, with line 15 and the prompt at `source_page.md` lines 66-67.

```
9. **Flag contradictions** — if a new source contradicts existing wiki content, add a `## Contradictions` section to the affected page and leave BOTH claims visible. Do not silently overwrite.
```

Index and log are maintained by shipped code (`_rebuild_index` rewrites the index Sources section; `_append_log` appends a structured entry with 50 KB auto-archiving). Cross-source entity and concept pages and contradiction handling are prose for the agent: no shipped code creates concept pages or compares claims, and the contradiction lint rule only reports pages that already contain a Contradictions section, returning "skipped: requires LLM callback" without one. The only code-created cross-source pages are per-project stubs.

**D4 covers** (evidence). `llmwiki/synth/pipeline.py` lines 333-338, with the command at `.claude/commands/wiki-ingest.md` lines 3-9 and the raw write guard at `convert.py` lines 121-144.

```
"""Walk raw/sessions/ and return (path, meta, body) for each .md file."""
    root = raw_dir or RAW_SESSIONS
    if not root.is_dir():
        return []
    out: list[tuple[Path, dict[str, Any], str]] = []
    for p in sorted(root.rglob("*.md")):
```

Integrate is a separate command from ingest and simply globs whatever markdown exists under `raw/sessions/`; it does not care who wrote it. Frontmatter `slug`, `project` and `date` are read if present with filename fallbacks, the Obsidian adapter is an in-body example of consuming user-written markdown, and the changelog states that sync alone only fills `raw/` while semantic pages require synthesize. The constraint is a fixed directory.

**D5 partial** (evidence). `pipeline.py` lines 134 and 639-640, with the expected no-op run shown at `.claude/commands/wiki-synthesize.md` lines 31-36.

```
"""Load the mtime state file. Returns {relative_path: mtime}.   ||   if rel in state and state[rel] >= mtime and not force:
            continue
```

A re-run on an unchanged tree is a no-op, but the key is file modification time rather than a content hash: copying, touching or a checkout that rewrites identical content re-triggers synthesis, and an edit preserving mtime is missed. The converter side is likewise mtime-keyed. The agent backend is idempotent per slug, and `--force` bypasses the state.

**D6 partial** (evidence). `.claude-plugin/plugin.json` lines 21-37, with the skill frontmatter and the tutorial.

```
"commands": [
    "commands/wiki-init.md",
    "commands/wiki-sync.md",
    "commands/wiki-ingest.md",
  …
  "skills": [
    "skills/llmwiki-sync/SKILL.md",
    "skills/llmwiki-ingest/SKILL.md",
    "skills/llmwiki-query/SKILL.md"
  ],
  "hooks": {
    "SessionStart": "hooks/session-start.sh"
  },
```

Three real skills and fifteen slash commands ship under `.claude/`, and Claude Code picks them up when the clone is opened as the project. It is not installable as a plugin as-is: the manifest points at `commands/`, `skills/` and `hooks/session-start.sh` relative to the plugin root, and none of those paths exists at the pin. The skills also hard-depend on the clone, shelling out to the package and reading `CLAUDE.md`, with all paths anchored to the checkout. Codex compatibility, recorded separately: `AGENTS.md` mirrors `CLAUDE.md`, a skill installer copies skills into `.codex/skills/` and `.agents/skills/`, and the agent-delegate backend detects the Codex CLI.

**D7 covers** (evidence). `llmwiki/cli.py` lines 68-72 in `cmd_init`, with the three-layer description in `CLAUDE.md` lines 7-26.

```
for name in ("raw/sessions", "wiki/sources", "wiki/entities", "wiki/concepts", "wiki/syntheses", "site"):
        p = REPO_ROOT / name
        p.mkdir(parents=True, exist_ok=True)
```

Satisfies the second clause: layout requirements are stated explicitly and created by init. The first clause is only partly real: `--vault PATH` exists and a vault layout abstraction exists, but `cmd_synthesize` hard-codes the raw and wiki source directories under the vault root and ignores it, and the guide says command-level overrides land in a follow-up. Init also seeds nine navigation files the requirement did not ask for.

**D8 partial** (evidence). `pipeline.py` lines 663, 677 and 584.

```
raw_slug = meta.get("slug", p.stem)   ||   filename = f"{date}-{slug}" if date else slug   ||   f"source_file: {source_file}",
```

The output filename and the `source_file` provenance field are taken from the raw note's frontmatter, so a caller who writes `slug: <citekey>` and omits `date` gets a citekey-named page and can put the citekey in `source_file`. Nothing in the body knows a citekey: the converter generates its own slug, and wikilinks inside pages are whatever the model emits. Slug normalisation preserves case and only replaces unsafe characters, so typical citekeys survive.

**D9 partial** (evidence). `llmwiki/candidates.py` lines 3-6, with `cmd_candidates` and the >20-file question in `.claude/commands/wiki-sync.md` line 15.

```
New entity/concept pages created by `/wiki-ingest` land in
``wiki/candidates/`` first with ``status: candidate`` frontmatter.
A human then runs `/wiki-candidates` to promote, merge, or discard each
one. Promoted pages move into ``wiki/entities/`` or ``wiki/concepts/``.
```

Three gates exist in code or command text: a candidates approval workflow with per-page promote, merge and discard and archived discards; the agent-delegate backend, which leaves a pending sentinel the agent completes one source at a time; and a batch threshold plus a dry run. Partial because the wiring is inconsistent and not configurable: `CLAUDE.md` tells the agent to write entities directly while the candidates command says ingest routes new pages to `candidates/`, and `llmwiki synthesize` with the dummy or Ollama backends writes source pages and rebuilds the index with no gate at all.

**D10 covers** (evidence). `LICENSE` lines 1-8 with three manifest declarations.

```
MIT License

Copyright (c) 2026 Pratiyush

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
```

MIT permits use and modification with attribution and notice retention; all four declarations agree.

**C4 does not** (evidence). `llmwiki/convert.py`, the comment block in `convert_all` at about lines 1515-1520, with `pyproject.toml` lines 58-59.

```
# #493: PDF dispatch removed. There was never a concrete PDF
            # adapter — `adapter.convert_pdf` raised AttributeError on
            # every adapter, the exception got swallowed into
            # `_quarantine_add`
```

Recorded because the ingest skill's description advertises PDF input; the body has no PDF-to-text path at all, local or otherwise.

**C5 covers** (evidence). `llmwiki/cli.py` lines 472-473 with the entry point and the Ollama default base URL.

```
def cmd_synthesize(args: argparse.Namespace) -> int:
    """Synthesize wiki source pages from raw sessions (v1.1.0 · #35).
```

The digest side runs headless from the CLI with a local Ollama backend and no Obsidian process; vault-overlay mode writes into an Obsidian vault directory directly. This is the plausibly-relevant half of C5 only: the capture lane's Zotero requirements are untouched.

**Treatment opinion: copy plus a delta.** Install-as-is does not apply: the plugin manifest does not resolve, the skills work only inside this clone, the default backend produces skeleton pages, and D2 and D3 are prose-only or fixed-frontmatter. Forking a 300-file session-transcript site generator to obtain about 60 KB of digest logic is poor value. The pieces that earn their place, the source page prompt shape, the pending-prompt sentinel and completion loop for zero-key agent synthesis, the index rebuild and log append, the standard-library frontmatter parser, and the candidates gate, are small, MIT-licensed and separable. Copying them with these deltas would fit: content-hash rather than mtime state; a caller-supplied field list rendered into the prompt rather than a whole-prompt override; a citekey as the slug, the provenance id and the link target; vault-relative paths honouring a caller layout; and a code-level rule that concept pages append rather than overwrite.

**Facts carried from this body.** The acknowledgements name four prior-art LLM-wiki implementations worth sourcing as further digest candidates (`README.md`, Acknowledgements). The canonical spec is Karpathy's gist (`CLAUDE.md` line 3). The environment variables the body uses to detect a running Claude Code, Codex or Cursor session are recorded at `llmwiki/synth/agent_delegate.py` lines 121-125. The agent-delegate pattern uses an HTML-comment sentinel on the page's first line as the machine-readable pending marker, and completion preserves frontmatter while replacing the body (lines 92-95). The PyPI distribution name differs from the repository and import names.

### 8. SamurAIGPT/llm-wiki-agent

Seeded ("two lanes"). `https://github.com/SamurAIGPT/llm-wiki-agent`. Pin `4ea2c7f916a8f7de6c787d1be014cd392250c161` (main, 2026-08-31; no tags or releases exist). Kind: an agent contract, a repository root with `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, four project-scoped slash commands and ten Python tools.

**Maintenance.** 3,487 stars. `pushed_at` 2026-08-31, but that and the preceding four weekly pushes are a star-history GitHub Action; the last human commit is 2026-07-30. 106 commits, ten author identities, created 2023-04-21, no tags, no releases. Treat 2026-07-30 as the last real change.

**Originator and supplier.** Supplier SamurAIGPT (the organisation and copyright holder). Originator differs in name only: the top committer is Anil Chandra Naidu Matcha, whose repositories are linked as Related Projects, so the organisation appears to be his. Other substantive contributors: watsonk1998 and Tony Lin.

**Licence.** MIT, found, at `LICENSE` lines 1-13, with the README badge and licence section agreeing.

```
MIT License

Copyright (c) 2023 SamurAIGPT

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

IP assertions: only the copyright line. No contributor agreement, patent grant, trademark or attribution clause beyond the notice-retention condition. `pyproject.toml` line 6 still carries the placeholder author, so the manifest asserts no authorship.

**Verify.** Licence re-read at the pin: lines 1-13 match verbatim, the file is the full 21-line MIT text, and the copyright holder is the organisation as recorded. Pin confirmed: SHA, author date and the "chore: refresh star history" message match, consistent with the star-bot note; tags and releases both return empty, confirming none exist. Three rows re-checked, none refuted.

**Smallest part.** The prose workflow sections of `CLAUDE.md`, lines 64-109 (the ten-step ingest workflow plus the source page format) together with lines 237-265 (index format and log format). They need no Python, no LLM gateway and no graph directory, and they are what both the slash command and the script path execute. A secondary independently-liftable piece is `tools/health.py`, a deterministic index-sync, log-coverage and stub check depending only on the path constants.

**Fitting.** *Inputs:* a file path inside the repository, conventionally under `raw/`: markdown ingested directly; PDF, DOCX, PPTX, XLSX, HTML, TXT, CSV, JSON, XML, RST, RTF, EPUB, IPYNB, YAML, TSV, WAV and MP3 auto-converted by markitdown; directories and globs for batch. An optional pre-step converts an arXiv id or a local PDF to markdown. Wiki context read on each ingest is the index, the overview and the five most recent source pages. *Outputs:* `wiki/sources/<slug>.md` with frontmatter and Summary, Key Claims, Key Quotes, Connections and Contradictions; new or overwritten entity and concept pages; a replaced overview when the model returns one; an index entry; a dated log line; and contradiction and validation output printed to standard output. Side outputs from other tools include a graph, health and lint reports, syntheses and a refresh cache. *Invocation:* in Claude Code, `/wiki-ingest raw/<file>.md` or the phrase; in Codex or OpenCode through `AGENTS.md`; headless as `python tools/ingest.py <path>` and nine sibling scripts, with LLM calls routed through litellm and a model chosen by environment variable. *Harnesses:* Claude Code (project-scoped, not a packaged plugin), Codex and OpenCode, Gemini CLI, plain CLI and cron, and Obsidian as a passive viewer through a symlink of `wiki/` into a vault.

**Surplus.** A knowledge-graph layer (45 KB) with inferred edges, communities and a self-contained viewer, plus a graph health report: a cost in two dependencies and LLM tokens, neutral for a vault that already has a graph view. Entity pages auto-created on every ingest and overwritten blind on later ingests: a cost for a research vault. A heal tool that materialises pages from wikilinks mentioned three or more times, which is the exact failure the repository's own hard rules forbid for the graph layer, and which the nightly pipeline runs. A query workflow and syntheses pages; lint with an LLM semantic pass; a deterministic health check that is cheap and directly reusable; multi-format ingestion through a heavy optional install; higher-fidelity PDF conversion through optional backends; a batch directory converter; a stale-source re-ingest that is broken as shipped; a cron and launchd pipeline whose template contains a placeholder API key; domain templates for diary and meeting notes; three parallel agent contracts that have already drifted; a CJK showcase; a star-history bot that makes `pushed_at` unreliable; and litellm as the CLI gateway, a large dependency with a recent supply-chain incident.

**Coverage.**

**D1 covers** (evidence). `tools/ingest.py` line 252, with the template at `CLAUDE.md` lines 82-109.

```
write_file(WIKI_DIR / "sources" / f"{slug}.md", data["source_page"])
```

One page per source is the core loop: the shipped script asks the model for source-page content using the schema's format and writes it to `wiki/sources/<slug>.md`, and the schema mandates a Summary section and a Key Claims bullet list plus Key Quotes, Connections and Contradictions. The same workflow is prose-only for the Claude Code path. Input can be markdown directly or PDF text through markitdown auto-conversion.

**D2 partial** (evidence). `tools/ingest.py` line 205 with `tools/_utils.py` line 25, the templates at `CLAUDE.md` lines 82-151, and `README.md` line 200.

```
schema = read_file(SCHEMA_FILE)
```

The field list does reach the model from a per-project file, because ingest injects `CLAUDE.md` wholesale into the prompt and Claude Code reads it natively, so a caller can define a charting template by editing that file. But there is no template parameter, no per-project template file separate from the tool's own instructions, and the three shipped templates are tool-fixed with no charting fields. Editing the tool's instruction file is indistinguishable from forking once installed, so the not-fixed-by-the-tool clause is only half met. The shipped source page format has no page-locator field of any kind.

**D3 partial** (evidence). `tools/ingest.py` line 72 (the context builder), with the overwrite at lines 259-260, the contradictions field at 235, the log append at `_utils.py` line 141 and `CLAUDE.md` line 31.

```
recent = sorted(sources_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
```

Three of four clauses hold: concept pages are created and updated across sources, the index is maintained by code and checked by health, and the log is written by pure append despite a docstring saying otherwise. Contradictions are flagged through a `## Contradictions` section and printed to standard output. The preservation clause fails by construction in the script path: the context builder shows the model only the index, the overview and the five most recent source pages, never the existing entity or concept pages, yet asks for full markdown content for concept pages and overwrites them. An existing concept page and any contradiction recorded on it are regenerated blind. The overview is likewise replaced wholesale. No rule anywhere says contradictions must be kept rather than resolved.

**D4 covers** (evidence). `tools/ingest.py` line 178 with the CLI description at line 179-198 and the worked cron example in `docs/automated-sync.md` lines 39-42.

```
def ingest(source_path: str, auto_convert: bool = True):
```

The tool never creates the source note; it consumes whatever file path it is given. The automated-sync document is a shipped worked example in which another process (a vault symlink script) populates `raw/` and ingest runs afterwards over the results. The README also invites the Obsidian Web Clipper or direct writes into `raw/`. One caveat: for non-markdown inputs the converter writes the converted markdown next to the original, which sits awkwardly with the declaration that `raw/` is immutable, though it adds a sibling rather than altering the original.

**D5 does not** (evidence). `tools/refresh.py` line 72 against line 147, with the print-only hash at `tools/ingest.py` lines 199-202.

```
current_hash = sha256(raw_content, truncate=16)
```

Two independent causes, both confirmed by reading and by running the code. Ingest computes a content hash and only prints it: every invocation calls the LLM and rewrites pages regardless of prior state, and it never writes the refresh cache. Refresh is the intended hash gate but compares a 16-character truncated digest against a stored 64-character digest, so with the repository's own hash function these never match and every source is reported stale on every run after the first. Even with the one-token fix, the cache is populated only by refresh. The Claude Code prose path has no dedup instruction at all.

**D6 partial** (evidence). `README.md` line 45, with the command bodies at `.claude/commands/wiki-ingest.md` line 7 and the missing health command at `CLAUDE.md` line 11.

```
claude      # reads CLAUDE.md + .claude/commands/ (slash commands available)
```

It runs natively in Claude Code, but as a cloned repository root rather than an installable skill or plugin: the tree has no `SKILL.md`, `plugin.json`, marketplace manifest or `.claude-plugin/` directory. The four project-scoped commands each defer to `CLAUDE.md` by name, so dropped into a vault that has its own `CLAUDE.md` they point at nothing; adoption means merging sections and copying `.claude/commands/` and `tools/` by hand. The schema also advertises a `/wiki-health` command whose file does not ship. Codex compatibility, recorded separately: `AGENTS.md` carries the same workflows and is in fact a superset of `CLAUDE.md`, while the Python tools hard-code `CLAUDE.md` as the schema whatever agent is in use, so the two contracts have drifted.

**D7 covers** (evidence). `tools/_utils.py` line 19 with the layout prose at `CLAUDE.md` lines 25-42 and the Obsidian symlink at `README.md` line 227.

```
WIKI_DIR = REPO_ROOT / "wiki"
```

Covered on the second clause only: the layout is stated explicitly and completely, and the Python constants are hard-coded relative to the repository root with no CLI or environment override. It does not work on a caller-chosen layout: an existing vault must adopt this tree or symlink `wiki/` into the vault, which is how the body proposes Obsidian coexistence. Naming conventions are also fixed.

**D8 partial** (claim). `CLAUDE.md` line 232, against the model-returned slug at `tools/ingest.py` line 224 and the provenance markers at `CLAUDE.md` lines 90 and 55.

```
- Source slugs: `kebab-case` matching source filename
```

There is no caller-supplied id parameter. The only stable identifier is the source slug, which by convention matches the source filename, so a caller who names the raw file by citekey gets a citekey slug and a citekey-bearing `source_file` provenance marker by convention. But ingest delegates slug choice to the model with no enforcement, and the Claude Code path is prose. Provenance is carried as a path and as a slug list, never as an explicit id field, and the two frontmatter schemas in the body are inconsistent with each other.

**D9 does not** (evidence). `tools/refresh.py` line 101, with the immediate writes at `tools/ingest.py` lines 250-270 and the derived-artefact prompts at `CLAUDE.md` lines 163 and 179.

```
parser.add_argument("--dry-run", action="store_true", help="Only list stale pages, don't refresh")
```

No review gate exists before integration. Ingest parses the model's JSON and writes the source page, entities, concepts, overview, index and log in one pass with no flag to preview, approve or stage. The ask-before-save prompts apply only to query answers and lint reports. The refresh dry run lists which sources would be re-ingested and shows nothing of what would change. Per-source versus batch is not discussed, and the promotion gate described in `AGENTS.md` is an explicitly open Phase 3 proposal with no implementation.

**D10 covers** (evidence). `LICENSE` line 8 within the full text at lines 1-21.

```
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
```

Standard MIT, permitting use and modification subject only to notice retention. No manifest licence field and no per-file headers contradict it.

**C4 covers** (evidence). `tools/pdf2md.py` line 135 and line 90, with the ingest-time converter at `tools/ingest.py` line 157.

```
md_text = pymupdf4llm.to_markdown(str(pdf_path))
```

Listed from the capture lane because the body plausibly covers it. Both PDF-to-markdown routes run locally: the converter dispatches to `pymupdf4llm` or `marker` on the local machine, and ingest converts through markitdown with plugins disabled and no cloud endpoint configured. The `arxiv2md` backend is a network fetch of arXiv source rather than a cloud extraction call, and applies only to arXiv identifiers. Dependencies are optional and absent from the requirements file, with install hints on exit.

**C5 covers** (evidence). `docs/automated-sync.md` line 41, with the zero-API health tool and the README note.

```
python3 tools/ingest.py "$file" >> "$LOG_FILE" 2>&1
```

Every tool is a plain Python CLI; the shipped launchd or cron example runs the full ingest and heal pipeline unattended, and health runs with no API at all. Obsidian is only a viewer and is never required. The caveat is that this is headless digest rather than headless capture: nothing in the body touches Zotero.

**Treatment opinion: copy plus a delta.** Install-as-is is not available: the body is a repository root with a hard-coded layout, no skill or plugin manifest, and slash commands that name `CLAUDE.md` literally, so it cannot be dropped into an existing vault or installed alongside the vault's own `CLAUDE.md`. A fork would carry the graph layer, litellm, the heal tool and the three drifting agent contracts, none of which the requirement set asks for, and the one script that matters for D5 is confirmed broken. Copy-frozen fails because every floor gap is a change to the prose: D2 needs a caller-supplied charting field list, D3 needs an explicit keep-both rule and a read-before-rewrite instruction for concept pages, D8 needs the citekey to replace the model-chosen slug, and D9 needs a review gate. The reusable core is the ingest workflow, source page format, index format and log format sections, which are clear, proven in the wild and MIT-licensed; carrying them into the vault's own skill body with those four deltas, and optionally lifting the health tool, keeps what works.

**Facts carried from this body.** litellm 1.82.7 and 1.82.8 were compromised in a March 2026 supply-chain attack, and this repository pins 1.83.10 as the verified-safe floor (`requirements.txt` line 1). A hard rule worth carrying: never auto-create pages from broken wikilinks, because LLM ingest produces hallucinated link targets, so report them instead (`AGENTS.md` line 293). The ecosystem pattern for coexisting an agent-owned wiki with an Obsidian vault is to symlink the wiki directory into the vault rather than run the agent inside it, filtering the index and log out of the graph view (`README.md` lines 218-235). The Python tools hard-code `CLAUDE.md` as the schema injected into every prompt regardless of the agent in use, so a multi-harness skill needs a single source of truth (`tools/_utils.py` line 25).

### 9. kepano/obsidian-skills

Seeded ("installed; markdown, bases, cli skills"). `https://github.com/kepano/obsidian-skills`. Pin `a1dc48e68138490d522c04cbf5822214c6eb1202` (main HEAD; `plugin.json` version 1.0.1), identical to the local install at `/home/eranr/.claude/plugins/cache/obsidian-skills/obsidian/1.0.1`: the recorded `gitCommitSha` matches and all fourteen files are sha256-identical to the raw files at that SHA. Kind: a Claude Code plugin that is an Agent Skills bundle of five skills plus markdown reference files, with no scripts, no executable code and no templates.

**Maintenance.** Last push 2026-06-08 (a documentation merge); 47,870 stars; default branch main; about three months without a push at read time; plugin version 1.0.1.

**Originator and supplier.** Steph Ango (kepano), both.

**Licence.** MIT, found, at `LICENSE` lines 1-21 with `plugin.json` line 10 and the repository API SPDX id.

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
```

IP assertions: `LICENSE` line 3 carries `Copyright (c) 2026 Steph Ango (@kepano)` and nothing else. No contributor agreement, patent grant or trademark notice anywhere in the tree.

**Verify.** Licence re-read at the pin: the full 21-line standard MIT text, with the copyright line and the quoted permission block matching exactly, corroborated by the manifest and the API. Pin confirmed: the commit resolves with the recorded message and date, and since the repository `pushed_at` equals that commit's date, nothing has been pushed since. Stars drifted to 47,888. Three rows re-checked, none refuted.

**Smallest part.** One skill directory; nothing cross-references another. For this set the useful unit is `skills/obsidian-markdown/` (about 8.6 KB: the skill plus properties, callouts and embeds references), which carries Obsidian-Flavored-Markdown output syntax including frontmatter, wikilinks, block ids, PDF page embeds and callouts. Second: `skills/obsidian-bases/` for authoring a dynamic index view over literature or concept notes. The manifests are needed only to install the whole bundle.

**Fitting.** *Inputs:* for the markdown, bases and canvas skills, the agent's own file reads and writes over vault files plus the user's request, with no external input format; for `obsidian-cli`, a running Obsidian desktop instance and the `obsidian` binary with `file=`, `path=`, `vault=`, `content=`, `template=` parameters; for `defuddle`, a URL and the separate npm CLI. *Outputs:* Obsidian Flavored Markdown, `.base` YAML files, `.canvas` JSON per JSON Canvas 1.0, command output on standard output, and defuddle markdown or JSON. *Invocation:* auto-triggered Claude Code skills selected by their frontmatter descriptions; installed here already at user scope through the marketplace, or with `npx skills add`. *Harnesses:* Claude Code plugin, with the README claiming Agent Skills portability to Codex and OpenCode by copying `skills/` into `~/.codex/skills`; `obsidian-cli` additionally requires the Obsidian desktop application to be open, while the format skills work in any file-writing harness.

**Surplus.** The JSON Canvas skill (neutral, one more description resident in the system prompt); the defuddle skill, which is helpful for capturing non-Zotero web sources but requires a global npm install and instructs the agent to prefer defuddle over the built-in fetch for any URL, changing default behaviour vault-wide; the CLI plugin and theme development commands (neutral); the CLI vault primitives, helpful only while Obsidian is open and therefore unusable headless; the Bases skill, helpful because a filtered `.base` gives a dynamic index over literature or concept notes and can be embedded in a page, replacing a hand-maintained list; and the markdown callouts, Mermaid, LaTeX, footnotes and block ids, helpful for digest-page formatting.

**Coverage.**

**D1 does not** (claim). `.claude-plugin/plugin.json` line 4.

```
"description": "Create and edit Obsidian vault files including Markdown, Bases, and Canvas. Use when working with .md, .base, or .canvas files in an Obsidian vault.",
```

The entire body was read, all fourteen files. No skill reads a source document or produces a summary or key points: `digest` has zero hits and `key point` has zero hits, and the `summar` hits are Bases summary formulas and a callout alias. The closest primitive is a note-creation workflow that starts from content the agent already has.

**D2 does not** (claim). `skills/obsidian-cli/SKILL.md` line 49.

```
obsidian create name="New Note" content="# Hello" template="Template" silent
```

No charting or template-fill behaviour. The `template=` parameter instantiates an Obsidian template note, so a caller-supplied field list could live in the vault, but the skill never reads a source to populate it; `template` has exactly one occurrence in the whole body.

**D3 does not** (claim). `skills/obsidian-bases/SKILL.md` lines 345-348.

```
filters:
  or:
    - file.hasTag("book")
    - file.hasTag("article")
```

No concept or synthesis pages, no log, no contradiction handling: `contradict` and `synthes` have zero hits, and the `log` hits are algorithmic notation and console output. A `.base` view can render a dynamic index over notes selected by tag, folder or property, and the CLI can append to a note when Obsidian is running, but neither maintains anything.

**D4 does not** (claim). `skills/obsidian-cli/SKILL.md` line 32.

```
Many commands accept `file` or `path` to target a file. Without either, the active file is used.
```

There is no integrate or digest step, so nothing can be separable from ingest. On the ingest side the skills are indifferent to who wrote a file, which is compatible with the requirement's premise but does not satisfy it.

**D5 does not** (claim). `skills/obsidian-bases/SKILL.md` line 139.

```
| `file.mtime` | Date | Modified time |
```

`hash`, `idempot` and `no-op` all have zero hits; no re-ingest concept exists. The only change-detection primitive is file modification time exposed inside Bases formulas, which is a display computation.

**D6 covers** (evidence). `.claude-plugin/plugin.json` lines 2-3 with the marketplace manifest.

```
"name": "obsidian",
  "version": "1.0.1",
```

Both Claude Code manifests are present, and the plugin is installed as-is on this machine at the pinned SHA, with the five skills appearing in the active skill list. Codex compatibility, recorded separately, is a README claim: the skills are said to follow the Agent Skills specification so any skills-compatible agent including Codex can use them, with installation by copying `skills/` into the Codex skills path. On the body side, every skill frontmatter carries only `name` and `description`, the spec-minimal form, and there is no Codex-specific manifest.

**D7 covers** (evidence). `skills/obsidian-bases/SKILL.md` line 392.

```
    - file.inFolder("Daily Notes")
```

Layout-agnostic: folder names are caller-chosen arguments in the worked examples, the CLI targets any vault path, and canvas file nodes take any path. Nothing requires an index, a log, a raw directory or any fixed folder. The caveat is that this is vacuous relative to digest output, because the body produces no digest; it holds for every operation the body does define.

**D8 does not** (claim). `skills/obsidian-markdown/SKILL.md` lines 24-25.

```
[[Note Name]]                          Link to note
[[Note Name|Display Text]]             Custom display text
```

`citekey` and `provenance` have zero hits, and `cite` has one, a callout alias. No stable-id concept. The syntax a citekey-keyed design would use is documented (wikilinks with heading and block anchors, block ids, and the PDF page-locator embed), but the skill never assigns or references sources by any id.

**D9 does not** (claim). `skills/obsidian-cli/SKILL.md` line 60.

```
Use `--copy` on any command to copy output to clipboard. Use `silent` to prevent files from opening. Use `total` on list commands to get a count.
```

`gate` has zero hits; the `review` hits are example prose. The closest affordance is that `obsidian create` opens the new file unless `silent` is passed, which is visibility to a human rather than a gate, and there is no integration step to gate.

**D10 covers** (evidence). `LICENSE` lines 5-9 with `plugin.json` line 10.

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software
```

Standard MIT text; use and modification are permitted subject only to retaining the copyright and permission notice.

**C2 does not** (claim). `skills/obsidian-markdown/SKILL.md` line 108.

```
This is visible %%but this is hidden%% text.
```

Included because a reader might expect region-marker syntax here. The comment syntax and callouts could physically delimit a managed region, but the body has no managed or free region concept, no citekey (zero hits) and no literature-note shape.

**C4 does not** (claim). `skills/defuddle/SKILL.md` line 17.

```
defuddle parse <url> --md
```

Included to prevent a misreading: defuddle is a web-page-to-markdown extractor taking a URL, provided by a separate npm binary. It is not a PDF text extractor. The markdown skill's PDF page embed displays a PDF page in Obsidian and extracts nothing.

**C5 partial** (claim). `skills/obsidian-cli/SKILL.md` line 8.

```
Use the `obsidian` CLI to interact with a running Obsidian instance. Requires Obsidian to be open.
```

Split by skill: `obsidian-cli` explicitly needs the desktop application running, so no headless pipeline can rely on it. The markdown, bases and canvas skills are pure file-format skills; the agent writes the files with its own tools, and the only Obsidian-dependent step is an optional verification in reading view.

**C6 covers** (evidence). `LICENSE` lines 5-7. Same MIT licence as D10; the quote is the licence block above, at those lines.

**Treatment opinion: install as-is.** This candidate is not a digest implementation and should not be assessed as one: D1, D2, D3 and D4 are all does-not, because no file in the body reads a source document, fills a template, maintains concept, index or log pages, or has an integrate step at all. What it is instead is a small (about 50 KB, fourteen files, zero scripts) MIT-licensed syntax-knowledge bundle that teaches the agent Obsidian Flavored Markdown, Bases and Canvas formats, and it is already installed at the pinned SHA with byte-identical files. As a format dependency for whichever digest is adopted, keeping it installed unchanged is the cheapest correct treatment: it is upstream-maintained, version-pinned by the plugin system, and nothing in it needs changing. Forking or copying would create drift for no gain. The one thing to watch is the defuddle skill's instruction to prefer defuddle over the built-in fetch, which is a behavioural default rather than a syntax fact. If the project ever wants only the markdown syntax rules vendored into its own digest skill, copy-frozen of that one skill directory with the MIT notice is the alternative.

**Facts carried from this body.** Obsidian has a native PDF page-locator embed syntax, `![[document.pdf#page=3]]`, usable for a per-source page locator or provenance marker (`references/EMBEDS.md` line 37). Paragraph-level block ids give stable intra-note anchors usable as provenance markers (`SKILL.md` line 34). The Obsidian CLI can create a note from a vault template and set arbitrary properties, but only with the application running (lines 49 and 54). Bases expose per-file modification time, outgoing links and backlinks as queryable properties, and a `.base` view can be embedded inside a markdown page, so an index page can host a live index without a hand-maintained list (lines 139-142 and 421). The markdown skill scopes itself to Obsidian-specific extensions only and carries no note-authoring workflow beyond syntax (line 8).

### 10. Karpathy's llm-wiki gist

Seeded ("the doctrine"). `https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f`. Pin `ac46de1ad27f92b28ac95459c782c07f6b8c964a`, the sole gist revision, committed 2026-04-04T16:25:13Z, read by cloning the gist. Kind: doctrine. One markdown idea file of 75 lines; no code, script, template, manifest or schema.

**Maintenance.** A single revision, with no later revision at the time of this run. The gist page renders stars and forks as "5,000+", GitHub's display ceiling, so both are more than 5,000 with no exact count exposed. Thirty comment identifiers on the first page. The gist API returned HTTP 502 on four attempts, so all metadata here comes from the git clone and the HTML pages.

**Originator and supplier.** Andrej Karpathy, both.

**Licence.** **None found.** Looked in: the git clone across all revisions, whose single revision contains only `llm-wiki.md` and no licence or copying file; the header lines 1-5 of that file, which carry a title, a tagline and a copy-paste invitation and no licence line; a grep of the whole body for licence, copyright, MIT, Apache, CC-BY, public-domain and all-rights wording, which returned nothing; the gist HTML page, where the only occurrences of "LICENSE" and "Apache 2.0" are inside reader comments rather than in the gist; and the gist API, which returned 502 every time and in any case carries no licence field for gists.

The nearest text is an invitation to copy rather than a grant: line 5 says the document "is designed to be copy pasted to your own LLM Agent", and line 75 invites the reader to "share it with your LLM agent and work together to instantiate a version that fits your needs". With no licence instrument, default copyright applies.

**Verify.** Licence absence confirmed at the pin by re-cloning: the single revision contains exactly one file, a case-insensitive grep for licence, copyright, MIT, Apache, CC-BY, public domain and all rights returned no hits, and the header carries only the copy-paste invitation. Pin confirmed: the clone yields exactly one commit with the recorded SHA, author and date, and one file of 75 lines. Two rows re-checked, none refuted.

**Smallest part.** The indexing and logging section, lines 43-49: the index catalogue convention (link, one-line summary, optional metadata, organised by category, updated on every ingest) and the append-only log convention with the grep-parseable entry prefix. The single sentence on line 49 giving the log prefix is the atom, liftable into a schema on its own.

**Fitting.** *Inputs:* raw source documents that the human, or the Obsidian Web Clipper, places in an immutable raw collection, described as articles, papers, images and data files, with images optionally downloaded to a fixed attachment folder. No PDF-to-text step, no Zotero path and no stable id are described. *Outputs:* markdown files in an LLM-owned wiki directory: a per-source summary page, entity, concept, comparison, overview and synthesis pages, an index catalogue and an append-only log, query answers filed back as new pages, and optionally slide decks, charts and canvases, with optional YAML frontmatter for Dataview. *Invocation:* none; there is no command or entry point. The human copy-pastes the idea file into the agent, co-authors a schema file, then per source tells the agent to process it; query and lint are likewise conversational prompts. *Harnesses:* agent-agnostic by declaration, naming OpenAI Codex, Claude Code and OpenCode or Pi, with the schema living in `CLAUDE.md` or `AGENTS.md`; Obsidian is the viewer. Not a skill, plugin or CLI.

**Surplus.** A query operation filing answers back as pages (helpful; matches how a research vault compounds); a lint operation covering contradictions, stale claims, orphan pages, missing concept pages, missing cross-references and web-search gaps (helpful as a home for contradiction flagging, but its treatment of stale claims as superseded can violate a never-delete-one-side rule unless the schema forbids deletion); a hybrid search CLI or MCP server (neutral at the stated scale, a dependency if adopted); alternative output formats (neutral); Obsidian workflow tips (helpful for a human-browsed vault); a use-case catalogue and the Memex framing (motivational prose); and git-repository advice (neutral, the vault already has that).

**Coverage.** Every row here carries `basis: claim`, because the body contains no script, schema, template or worked page: it is prose describing behaviour throughout.

**D1 covers** (claim). Line 37, the Ingest operation.

```
An example flow: the LLM reads the source, discusses key takeaways with you, writes a summary page in the wiki, updates the index, updates relevant entity and concept pages across the wiki, and appends an entry to the log.
```

The ingest flow prescribes exactly a per-source summary page derived from reading the source and its key takeaways. Prose only, so the basis is a claim; the status is covers because the requirement is addressed in full as described behaviour.

**D2 does not** (claim). Line 75, with the Dataview tip at line 61.

```
The exact directory structure, the schema conventions, the page formats, the tooling — all of that will depend on your domain, your preferences, and your LLM of choice.
```

No per-source template or field mechanism is described anywhere. Page formats are explicitly delegated to the caller-authored schema, and the only field-like mention is optional YAML frontmatter for Dataview, which is not a caller-supplied charting field list. Delegating the format is not a mechanism for filling one.

**D3 partial** (claim). Lines 31, 49, 11 and 41.

```
Summaries, entity pages, concept pages, comparisons, an overview, a synthesis. || **log.md** is chronological. It's an append-only record of what happened and when — ingests, queries, lint passes. || noting where new data contradicts old claims || Look for: contradictions between pages, stale claims that newer sources have superseded, orphan pages with no inbound links
```

Cross-source concept and synthesis pages, an index catalogue and an append-only log are all prescribed, and contradictions are to be noted and flagged. The never-resolved-by-deleting-one-side rule is not stated; on the contrary, lint is told to look for stale claims that newer sources have superseded, which contemplates supersession without saying whether the older claim is kept.

**D4 covers** (claim). Lines 29 and 37.

```
These are immutable — the LLM reads from them but never modifies them. This is your source of truth. || You drop a new source into the raw collection and tell the LLM to process it.
```

The raw layer is created by the human, or by the Web Clipper, and is immutable to the LLM; digestion begins only when the human tells the LLM to process a source already present. Capture and integrate are separate by construction and the LLM never owns creation of the source file.

**D5 does not** (claim). Line 49.

```
The log gives you a timeline of the wiki's evolution and helps the LLM understand what's been done recently.
```

No content hash, fingerprint or idempotency rule appears in the body. The only guard against re-processing is the human-readable log the LLM is meant to consult, which is a memory aid rather than a no-op mechanism.

**D6 does not** (claim). Lines 5 and 33.

```
This is an idea file, it is designed to be copy pasted to your own LLM Agent (e.g. OpenAI Codex, Claude Code, OpenCode / Pi, or etc.). || **The schema** — a document (e.g. CLAUDE.md for Claude Code or AGENTS.md for Codex) that tells the LLM how the wiki is structured, what the conventions are, and what workflows to follow when ingesting sources, answering questions, or maintaining the wiki.
```

Self-described as an idea file to copy-paste into an agent. There is no skill file, plugin manifest, command, hook or script; the gist's only file in its only revision is the idea file. Nothing is installable. Codex compatibility, recorded separately: the body names OpenAI Codex as a target and `AGENTS.md` as the Codex schema file, so the pattern is harness-agnostic even though nothing installs.

**D7 partial** (claim). Lines 31, 45 and 75.

```
The LLM owns this layer entirely. It creates pages, updates them when new sources arrive, maintains cross-references, and keeps everything consistent. You read it; the LLM writes it. || Two special files help the LLM (and you) navigate the wiki as it grows. || The exact directory structure, the schema conventions, the page formats, the tooling — all of that will depend on your domain, your preferences, and your LLM of choice.
```

The first alternative (an existing vault with a caller-chosen layout) is not really addressed: the body assumes a fresh LLM-owned wiki layer, though nothing forbids coexistence. The second alternative is only partly met: it names two special files and a three-layer split and gives a raw-assets example, then declines to fix a directory structure. Partial on both halves.

**D8 does not** (claim). Lines 49 and 47.

```
A useful tip: if each entry starts with a consistent prefix (e.g. `## [2026-04-02] ingest | Article Title`), the log becomes parseable with simple unix tools || each page listed with a link, a one-line summary, and optionally metadata like date or source count
```

The one worked identifier in the body is an article title in the log prefix; the index identifies pages by link plus one-line summary, and query answers come with citations. No stable id, citekey or provenance-marker convention is described anywhere.

**D9 covers** (claim). Line 37.

```
Personally I prefer to ingest sources one at a time and stay involved — I read the summaries, check the updates, and guide the LLM on what to emphasize. But you could also batch-ingest many sources at once with less supervision. It's up to you to develop the workflow that fits your style and document it in the schema for future sessions.
```

Per-source review and batch ingest with less supervision are both documented, and the chosen mode is to be recorded in the schema, which meets the at-least-documented bar. Line 22 also anticipates humans in the loop reviewing updates for team wikis. Nothing is configurable in a mechanical sense.

**D10 undetermined** (claim). Line 5, with the absence of any licence file.

```
This is an idea file, it is designed to be copy pasted to your own LLM Agent (e.g. OpenAI Codex, Claude Code, OpenCode / Pi, or etc.).
```

No licence instrument exists, so default copyright applies. The copy-paste invitation and the instantiate-a-version line signal the author's intent that the pattern be reused and adapted, but an invitation is not a grant of modification rights. Undetermined rather than does-not, because no licence forbids use either; the caller has to judge whether the invitation suffices.

**C5 partial** (claim). Line 15.

```
In practice, I have the LLM agent open on one side and Obsidian open on the other. The LLM makes edits based on our conversation, and I browse the results in real time — following links, checking the graph view, reading the updated pages. Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.
```

A cross-lane row included only as a property of the pattern: the agent edits markdown files directly and Obsidian is a viewer, so nothing in the workflow depends on the Obsidian application, yet the body never states that it runs without Obsidian and the author describes running with it open. It is not a capture tool: it reads no Zotero.

**Treatment opinion: author to the design and credit it.** The body is a pattern rather than a program, and says so: it is intentionally abstract, describes the idea rather than a specific implementation, and tells the reader to instantiate a version that fits their needs. There is nothing to install (D6 does not) and no licence instrument (D10 undetermined), so install-as-is is impossible and both copy-frozen and copy-plus-delta are excluded by the licence gap rather than by preference; copying the prose would rest on an informal invitation rather than a grant. Fork has no target: a one-file gist with no code. What remains is to author the project's own schema and skill encoding the parts the doctrine does prescribe (a per-source summary page; entity, concept and synthesis pages; an index; an append-only log with a grep-parseable entry prefix; immutable raw sources produced by another process; and a documented per-source versus batch review), adding what it does not (a caller-supplied charting field list, content-hash no-op re-ingest, citekey provenance, and an explicit never-delete-one-side rule), and crediting the gist by URL and pin as the source of the pattern.

**Facts carried from this body.** The doctrine recommends `qmd` as the local search layer once an index file stops sufficing, noting it has both a CLI and an MCP server (line 53). The log-entry prefix convention that makes the log greppable is the only concrete format the doctrine specifies (line 49). The stated scale ceiling at which an index file alone replaces embedding retrieval is about 100 sources and hundreds of pages (line 47). The Obsidian Web Clipper is the doctrine's capture path for web sources, and no Zotero path is mentioned anywhere (line 57). Images need a two-pass read because LLMs cannot read markdown with inline images in one pass (line 58). The harness mapping is `CLAUDE.md` for Claude Code and `AGENTS.md` for Codex (line 33). Dataview over YAML frontmatter is the suggested route to dynamic tables, and is the closest thing in the body to structured per-page fields (line 61).

### 11. llmwikis.org handbook

Seeded ("update discipline statement"). `https://llmwikis.org`. Pin: no repository and no SHA. Read 2026-09-04: handbook pages carry "Last reviewed July 2, 2026"; the starter bundle ZIP had sha256 `dd8a5875d11e78f142902ae2a1d8a97ac526a6bda6207ee5573e9831f910c898` as fetched, and the bundle page describes the ZIP as generated dynamically from a canonical template registry, so that hash is a read-time pin rather than a release identifier; the bundle manifest declares version `2026.07.02.1`, its templates declare `3.2.0`, and the site's well-known file declares 1.3.2 generated 2026-07-05. Kind: a WordPress handbook of prose standards, copy-paste prompts and page shapes, plus a downloadable starter bundle with markdown templates, JSON schemas and three Node scripts.

**Maintenance.** No public repository was found for the handbook or the bundle; the only GitHub link in the body is to Google Cloud's open-knowledge specification. Freshness signals are the review dates above and a single named maintainer contact.

**Originator and supplier.** Originator: Michael Kappel of Protocol5, per the site footer; the file layer originates with Google Cloud's Open Knowledge Format. Supplier: LlmWikis.org, which is the manifest's declared publisher.

**Licence.** Found, and split. The rendered page carries no licence notice; the content licence page states:

```
Unless a page states otherwise, LlmWikis.org public explanatory text may be quoted, summarized, and linked with attribution to LlmWikis.org. Starter examples are provided as implementation scaffolds and should preserve source attribution and local project ownership.

## Third-party material

Source excerpts, package metadata, logos, code, and linked third-party references retain their original ownership and license terms. Software files follow the license declared in their package, repository, or file header.
```

Looked for a software licence and found none: no licence file in the bundle root or scripts directory, no licence header in any of the three Node scripts, no licence key in the bundle manifest or the site specification, and a recursive grep of the unpacked bundle for licence, copyright, MIT, Apache and CC returned nothing. So the prose may be quoted, summarised and linked with attribution (modification is not addressed), the scaffolds may be used with attribution, and the scripts have no declared licence at all.

IP assertions: the bundle manifest states that it is a starter structure rather than legal, security or compliance approval, that consumer sites should link to or consume the bundle rather than relabel it, and that examples should be replaced with reviewed organisation-specific content before production use. The site also asserts canonical authority over how to build LLM wikis while pointing at UAIX.org for its schema and validator specifications.

**Verify.** Licence confirmed by re-fetching the content licence page: both quoted blocks are present verbatim and the page still carries the July 2 review date. Pin confirmed as a read-time artifact pin: the bundle re-downloaded a day later gives the identical sha256, so the dynamic ZIP is byte-stable across those dates, and the secondary pins (well-known version, manifest version, page review dates) all match. One numeric discrepancy, not on a covers row: the record says 95 files where the extracted ZIP contains 108 across 24 directories; the related claims still hold, since no skill file, plugin manifest or `CLAUDE.md` exists anywhere in the bundle. One row re-checked, none refuted.

**Smallest part.** The ingest page's copy-paste prompt plus its source page shape, about 40 lines: a prompt that reads one raw file, writes one source page with Summary, Key Claims, Connections and Contradictions, updates the index and appends to the log. For the seeded item, the smallest excerpt is the three-sentence update-discipline statement from the home page's agents card, together with the forbidden list in the bundle's update rules. Of the scripts, the OKF validator (232 lines, no dependencies) is separable on its own but licence-undeclared.

**Fitting.** *Inputs:* a source file already placed under `raw/` (the ingest prompt names a PDF path, and PDFs are meant to be compiled from a reviewable text proxy that points back to the original); a wiki tree with a reserved index file carrying only the OKF version in frontmatter and a newest-first dated log; an optional preflight configuration naming the wiki, raw and proposal directories, a large-file limit of 256 KB, public status values and typed relations. The scripts need only Node. *Outputs:* a source page with frontmatter and Summary, Key Claims, Connections and Contradictions; edits to concept, entity and synthesis pages; entries in a contradictions page; rows in the index; a dated log entry; and, from the preparation helper, a hash-suffixed copy in `raw/` or, above the size limit, a segmented directory with an abstract file. Validators print a text or JSON report and exit non-zero on failure. *Invocation:* the digest has no CLI; the user pastes the ingest, query and lint prompts into any coding agent. The scripts are `node scripts/llmwiki-preflight.js validate|prepare`, `node scripts/llmwiki-okf-validate.js wiki`, a frontmatter migrator and a freshness wrapper, and the bundle's own agent contract makes both validators a required preflight before ingest. *Harnesses:* harness-agnostic folder plus coding agent; the root contract is `AGENTS.md` or `CLAUDE.md`, and the bundle ships `AGENTS.md`, which is Codex-native, while no `CLAUDE.md` is shipped. No Claude Code skill or plugin, no MCP, no Obsidian dependency.

**Surplus.** A governed multi-agent transactive-memory subsystem (13 documents, 6 schemas, examples and fixtures, plus an OpenAPI stub) that is irrelevant to a single-user vault; a split-memory doctrine hard-coded into the README, the agent contract and the checklist; a multisite tenant namespace topology enabled by default in the shipped configuration, which rejects root-level pages; a public-publication SEO and discovery contract requiring 33 frontmatter fields; private-to-public promotion gates; long-run agent state packets; a 256 KB raw-file limit with byte-chunk segmentation, which is a cost for PDFs; a local-path lint applied to every wiki page by default, which on WSL fails any page citing a Zotero storage path; a dependency-free OKF validator, which is a helpful small idea; a trust-label vocabulary with per-label agent behaviour, which is helpful; query answers saved as syntheses, which is helpful; source-policy citation rules for preprints, model cards, repositories and datasets, which are helpful for literature notes; and a knowledge map, redirect and alias templates.

**Coverage.**

**D1 partial** (evidence). The ingest page's copy-paste prompt and source page shape.

```
- Create or update exactly one wiki/sources/ page for the source.
- Extract Summary, Key Claims, Evidence, Entities, Connections, and Contradictions.
```

The body supplies a worked prompt and a page-shape template for exactly the per-source summary and key-points page, taking a PDF path in `raw/`. Nothing in the body executes it: the digest is done by whichever coding agent the user pastes the prompt into, and PDF text extraction is delegated. An empirical check found that the body's own source page shape fails its own shipped validators: the OKF validator reports four errors for missing governance fields, and the preflight validator rejects the status value and the missing trust fields. So the template is usable as a specification but not as-is with the body's tooling.

**D2 does not** (evidence). The source-record template's field list, with the ingest blueprint's fixed keys and the tolerant frontmatter schema.

```
- Source ID:
- Source path or URL:
- Owner:
- Date captured:
- Sensitivity:
- Checksum:
- Summary:
- Supports pages:
- Restrictions:
```

Every per-source template in the body has a fixed field list authored by the tool. The schema tolerates extra keys and the agent contract says to preserve unknown frontmatter keys, but no prompt, template or script accepts or fills a caller-supplied field list such as population, concept, context, design, findings or a page locator.

**D3 partial** (evidence). The ingest algorithm's preserve-and-extend and record-contradictions rules, with the shipped navigation surfaces and the typed relation.

```
- Preserve and extend. Rewrite target pages so new knowledge integrates with prior content without deleting unresolved history.

- Record contradictions. Add unresolved conflicts to wiki/contradictions.md instead of smoothing them over.

- Update navigation. Add or revise index.md entries and append a log.md event.
```

The design is exactly the requirement: concept and synthesis pages, an index and an append-only log shipped as files, a `contradicts` relation in the schema, and an explicit ban on removing disagreement to make text cleaner. Shipped artifacts are real (index, log, concept template, schema relation, a log-order check). The maintaining itself is done by the consuming agent; nothing in the body executes the merge, and the never-delete rule is enforced only as prose plus a lint that checks a relation is present rather than a deletion guard.

**D4 covers** (evidence). The bundle's OKF profile roots, the ingest prompt's read-only rule, and the raw directory's own README.

```
    "bundle_root": "wiki/",
    "raw_source_root": "raw/",
```

Capture and digest are separate layers by construction: `raw/` is an immutable input directory that any process may populate, and the digest prompt consumes a path already in it. The preparation helper is mandatory only above 256 KB, so the tool does not own source-file creation. Conditions found in the scripts: preflight fails any raw file over 256 KB that is not segmented, the preparation command splits such files into byte chunks (meaningless for a PDF binary), and duplicate content hashes across raw, wiki and proposals are a failure, so a Zotero PDF corpus dropped into `raw/` will fail preflight unless those checks are disabled.

**D5 partial** (claim). The two-step pipeline's hash-and-register stage, against the script that turns a duplicate into a failure.

```
Hash and register
Detect duplicate or changed source files.
Path, checksum, source type, intake date.
Unknown origin, unsafe file, or duplicate already reviewed.
```

The no-op-on-unchanged behaviour is prescribed in prose with "duplicate already reviewed" as a stop condition, but no shipped code implements a skip: preflight computes SHA-256 and turns a duplicate into a validation failure, and the preparation command re-copies a source to a hash-suffixed name without checking whether the target already exists. The hash plumbing exists; the idempotent short-circuit does not.

**D6 does not** (evidence). The specification's conformance profiles, with the bundle's file inventory.

```
Profile A plus AGENTS.md or CLAUDE.md, agent read order, update rules, citation rules, stop conditions, staged-write policy, local route manifest, private-file exclusion, and review checklist.
```

Not a Claude Code skill or plugin; the body is harness-agnostic folder-plus-agent, and its only agent contract is a root `AGENTS.md` whose content is a governance schema rather than a skill. There is no skill file, plugin manifest or marketplace manifest anywhere in the bundle. Codex compatibility, recorded separately: the bundle ships `AGENTS.md`, which Codex reads natively; `CLAUDE.md` appears only as an alternative filename in prose and in the preflight allowlist, and none is shipped.

**D7 covers** (evidence). The bundle's agent contract on the OKF profile, with configurable directory names in the preflight configuration and script arguments.

```
Use `wiki/` as the OKF bundle root. Root `wiki/index.md` is reserved and may contain only `okf_version` in frontmatter; nested `index.md` files should be plain routing files; `wiki/log.md` records newest-first activity. Every other Markdown concept file under `wiki/` needs YAML frontmatter with `type` plus the LLMWikis governance overlay: `llmwiki_status`, `llmwiki_owner`, `llmwiki_source_status`, and `llmwiki_agent_use`.
```

Layout requirements are explicit and the folder names are caller-configurable. Hard constraints that bite an existing markdown vault: nested index files must carry no frontmatter, the root index may hold only the OKF version, every other markdown file must carry a type plus four governance fields, and preflight additionally demands owner, status, source status, last-reviewed, canonical URL and typed relations on every page. Empirically the pristine bundle passes its OKF validator with zero errors and six warnings and fails its own preflight with 96 failures under the shipped configuration.

**D8 partial** (evidence). The knowledge-graph page's stable-id rule, against the tool-derived raw filename.

```
Stable IDs
Identify pages, sections, entities, claims, sources, contradictions, and review events.
Do not use titles as permanent IDs.
```

The body wants stable non-title identifiers and provides a free Source ID slot and a free-string checksum-or-source-identity field, so a caller-supplied citekey can be recorded. But every worked example links and traces by raw path, slug or hash prefix, nothing propagates a caller id into wiki links or provenance markers, and the preparation script invents its own hash-based names.

**D9 covers** (evidence). The OKF profile's agent update policy, with the per-page agent-use enum, the staged-proposal quarantine and the pipeline's review stage.

```
"agent_update_policy": "proposal-only until human review promotes a change",
```

The review gate is both documented and configurable per page through an agent-use enum of read-only, read-cite, read-cite-propose, proposal-only, human-approval-required and blocked, with a human-review-required flag, a staged-proposals quarantine folder shipped, and a per-source cadence (each source gets an ingest preflight, and the pipeline stages analyse, stage, review, write). Batch review is not named as a mode; it is implicit in staging many proposals before one review pass.

**D10 partial** (claim). The content licence page's first paragraph and its third-party clause, against the absence of any licence in the bundle.

```
Unless a page states otherwise, LlmWikis.org public explanatory text may be quoted, summarized, and linked with attribution to LlmWikis.org. Starter examples are provided as implementation scaffolds and should preserve source attribution and local project ownership.
```

Use is permitted for prose (quote, summarise, link, with attribution) and for the starter scaffolds (attribution and local project ownership preserved, with the manifest expecting examples to be replaced). Modification and derivative rights for the prose are not granted, and the executable half, three Node scripts and the JSON schemas, has no declared licence at all: by the page's own rule that means the scripts fall back to whatever their package, repository or header declares, which is nothing. A floor requirement for use and modification is therefore only partly met.

**Treatment opinion: author to the design and credit it.** Three floor requirements are unmet: D2 (no caller-supplied charting fields), D6 (no Claude Code skill or plugin, only an `AGENTS.md` governance schema) and, for the executable half, D10 (scripts and schemas carry no licence, and the prose is quote-with-attribution only). What is valuable is the pattern rather than the artifacts: the two-step ingest (hash, analyse, stage, review, write), the per-source page shape, the raw and wiki separation, the contradictions-are-kept rule, the index plus append-only log, per-page agent-use gating, and the seeded update-discipline sentence. Those can be re-authored in the project's own skill and credited to llmwikis.org with short verbatim quotes, which is exactly what the content licence grants. Copying the bundle would import heavy surplus and, empirically, a toolchain that contradicts itself: the handbook's own source page shape fails both shipped validators, and the pristine bundle fails its own required preflight with 96 failures. Copy-plus-delta would mean adapting licence-undeclared scripts and prose not licensed for modification; install-as-is is impossible because nothing installs.

**Facts carried from this body.** The seeded update-discipline statement reads, verbatim from the home page card, "How agents should update|Analyze first, stage proposed wiki changes, then write only reviewed durable records." (the vertical bar marks the boundary between the card heading and its body, which are separate HTML elements). The file layer is Google Cloud's Open Knowledge Format v0.1, giving reserved index and log files, `type` frontmatter and tolerant readers, with the governance layer added on top. The ingest pages state explicitly that they are runbooks rather than a live ingestion product, and that the site provides no automated ingestion, public MCP access, hosted file processing or anonymous public editing. The bundle's required preflight cannot pass on the bundle itself, which was verified by running both validators on the pristine unpacked ZIP. The source-policy guidance for citing papers is a usable field checklist regardless of adoption: title, authors, date, version, venue or preprint identifier, DOI when available, and whether a later peer-reviewed publication exists.

### 12. llmwikis.org LLM Wiki Starter Bundle v3.2.0

Discovered through the handbook. `https://llmwikis.org/downloads/llm-wiki-starter-bundle-v3.2.0.zip`. Pin: the same read-time artifact pin as the handbook, sha256 `dd8a5875d11e78f142902ae2a1d8a97ac526a6bda6207ee5573e9831f910c898`, 108 zip entries, manifest version `2026.07.02.1`, page frontmatter `llmwiki_version: "3.2.0"`. Kind: vault template, a folder skeleton plus two Node validators and one raw-copy and segmentation command; no digest engine, no skill file, no plugin manifest.

**Maintenance.** No source repository; the same site-side freshness signals as the handbook.

**Originator and supplier.** LlmWikis.org is the declared publisher; the site footer names Michael Kappel of Protocol5.

**Licence.** **None found in the bundle.** No licence file, no licence key in the manifest, no SPDX or copyright header in any of the four scripts, and a whole-word grep of all 108 entries for licence, license, copyright, SPDX, CC-BY, creative commons and all-rights-reserved returned zero hits. The closest statements are on the site rather than in the bundle, and are reproduced in the handbook section above. Because the software files declare no licence, the site's own deferral clause resolves to no declared licence for the scripts.

**Verify.** Licence absence re-confirmed by re-downloading and re-grepping the ZIP: no licence or copying file anywhere, and zero matching files for the whole grep. Pin confirmed exactly: the re-downloaded ZIP has the identical sha256 and the same 108 entries, and the manifest and page versions match. Six rows re-checked, none refuted.

**Smallest part.** `scripts/llmwiki-okf-validate.js`, 232 lines using Node built-ins only, exporting a frontmatter parser, a validator and a CLI runner. It implements the reserved index and log convention, the `type` frontmatter requirement and a markdown-link existence check, and runs standalone against any directory. Second-smallest: the source-record template with its nine bullet fields.

**Fitting.** *Inputs:* for the preparation command, any single file path, copied verbatim under 256 KB or byte-segmented above it with an abstract file carrying a SHA-256, a byte count and a 4,096-byte text sample; for the validators, a folder tree with configurable wiki, raw and proposal directories, an optional sitemap and llms.txt, and an optional agent contract file. *Outputs:* one JSON report on standard output from preflight with a non-zero exit on failure; a text or JSON report from the OKF validator; hash-suffixed files written into `raw/`. No wiki page is ever generated by any script. *Invocation:* the four Node and shell commands named in the handbook section. *Harnesses:* CLI with Node and zero third-party dependencies; the agent surface is a root `AGENTS.md`, which is Codex-native, with no `CLAUDE.md` shipped though the validator accepts either name.

**Surplus.** Identical to the handbook's list, since the bundle is where most of it ships: multisite topology enforcement enabled by default, which makes the bundle fail its own preflight; the transactive-memory subsystem, 34 of the 108 entries; SEO and publication lint requiring 33 frontmatter fields; the split-memory doctrine; long-run agent packets; the promotion pipeline; 256 KB segmentation with a text sample, a cost for PDFs; duplicate-content detection by SHA-256 across raw, wiki and proposals, helpful for catching a source captured twice though it blocks rather than skips; a tolerant frontmatter schema plus a key-preserving migrator, helpful because caller-added charting fields survive validation even though nothing fills them; and the proposals quarantine, helpful as a review-gate shape.

**Coverage.**

**D1 does not** (evidence). The source-record template's two bullets, with the preparation script's text sample.

```
- Summary:
- Supports pages:
```

Nothing in the body emits a summary or key points. The only per-source artifacts shipped are a blank template bullet list and, for files above the size limit, an abstract file containing a SHA-256, a byte count and the first 4,096 bytes decoded as text, which is a raw excerpt rather than a digest. The agent contract describes a two-step ingest but assigns the writing to the agent; no prompt, skill or script performs it.

**D2 does not** (evidence). The frontmatter schema's tolerance, against the fixed template field lists.

```
"additionalProperties": true,
```

Templates carry a fixed, tool-defined field list of 33 required frontmatter keys. The schema tolerates extra keys and the contract says to preserve unknown frontmatter, so caller-added fields would not break validation, but no component reads a caller-supplied field list or fills fields from a source. Filling is absent entirely.

**D3 partial** (evidence). The OKF validator's log-order warning, with the reserved index rule, the typed-relation whitelist and the concept template's relation block.

```
addWarning('log.md date headings should be newest-first');
```

Structure is shipped and script-checked: a reserved index and log, log date headings validated newest-first (a prepend-only, that is add-only rather than literally append, ordering), a concept template with a `contradicts` typed relation, and a validator that rejects any relation key outside the five allowed. The never-delete-one-side half is prose only: the forbidden list in the update rules bans removing disagreement to make text cleaner, the knowledge map says to preserve stale, contradicted, blocked and candidate states, and the lint checklist says a contradicted page without a contradiction relation fails, but none of that has implementing code.

**D4 partial** (evidence). The preparation command's arbitrary source argument, with the two-step contract.

```
const target = path.join(rawDir, `${safeBase}-${hash.slice(0, 8)}${ext}`);
fs.copyFileSync(source, target);
```

Capture is separable in code: preparation copies any externally written file into `raw/` under a hash-suffixed name, and validation scans whatever is already in `raw/` regardless of who wrote it, so the bundle does not own source creation. The integrate half has no code at all. For a Zotero-attachment flow, any file over 256 KB placed in `raw/` by another process fails validation until run through preparation, which byte-chunks it and decodes the first 4 KB as text, meaningless for a binary PDF; the bundle assumes text has already been extracted.

**D5 partial** (evidence). The preflight duplicate check, against the absence of a skip.

```
report.failures.push(`Duplicate content hash ${hash}: ${relative(report.root, previous)} and ${relative(report.root, file)}`);
```

Content hashing exists and drives the raw filename, so re-running preparation on an unchanged file rewrites the same target path, which was tested: two runs both reported the same copy. There is no skip branch. The opposite behaviour is what is enforced: the same content under a second name is a validation failure and a documented hard stop.

**D6 does not** (evidence). The validator's agent-scope check, with the bundle inventory.

```
for (const name of ['AGENTS.md', 'CLAUDE.md']) {
```

Nothing is packaged as a Claude Code skill or plugin. The validator anticipates a `CLAUDE.md` and accepts either name for its scope check, but the bundle ships only `AGENTS.md`. Codex compatibility, recorded separately: `AGENTS.md` is Codex's native project-instruction file, so dropping the bundle into a repository gives Codex its instructions as-is; it is still an instruction file plus CLI scripts rather than a skill for either harness.

**D7 covers** (evidence). The bundle's agent contract on the OKF profile, with the configurable directory names in the preflight configuration and the script's own overrides.

```
Use `wiki/` as the OKF bundle root. Root `wiki/index.md` is reserved and may contain only `okf_version` in frontmatter; nested `index.md` files should be plain routing files; `wiki/log.md` records newest-first activity. Every other Markdown concept file under `wiki/` needs YAML frontmatter with `type` plus the LLMWikis governance overlay: `llmwiki_status`, `llmwiki_owner`, `llmwiki_source_status`, and `llmwiki_agent_use`.
```

Layout requirements are explicit and the wiki, raw and proposal directory names are caller-configurable through the shipped configuration file or command-line flags, and the OKF validator takes any root as its positional argument. The hard constraints are the ones listed in the handbook section: reserved index and log files, a `type` plus four governance fields on every other markdown file, and, from preflight, owner, status, source status, last-reviewed, canonical URL and typed relations on every page. This is the same statement the handbook cites, because the bundle is where it ships.

**D8 partial** (evidence). The source-record template's identifier slot, against the tool-derived filename.

```
- Source ID:
```

There are slots for an identifier (a free-text Source ID bullet, a free-string checksum-or-source-identity field, and a `source_for` relation), and the citation rule shows a path-based provenance format. The only identifier the tooling actually generates is its own basename-plus-hash raw filename. There is no citekey concept, and nothing links or validates by the Source ID.

**D9 covers** (evidence). The OKF profile's update policy, with the per-page agent-use enum and the staged-proposals README.

```
"agent_update_policy": "proposal-only until human review promotes a change",
```

The gate is documented and declared per page through a schema enum, with a proposals quarantine and a dated log entry template naming source records and reviewer. No script acts on the enum value: the OKF validator only checks the field is non-empty, and the only code enforcement is a regex requiring source-trace or owner-review language near mentions of staged proposals. Per-source versus batch granularity is not addressed; the log template implies dated batches listing several source records.

**D10 undetermined** (evidence). The site's deferral clause, against the absence of any licence in the bundle.

```
Software files follow the license declared in their package, repository, or file header.
```

No grant exists in the bundle, and the site defers software licensing to a declaration the scripts do not make. The site permits quoting and summarising explanatory text with attribution and calls starter examples implementation scaffolds whose examples should be replaced, which implies modification is anticipated, but neither is a licence. Rights to copy and modify the code cannot be affirmed from the body.

**Treatment opinion: author to the design and credit it.** Zero floor requirements reach covers here (D1, D2 and D6 are does-not, D3 and D4 partial, D10 undetermined). The bundle is a governance scaffold with validators rather than an implementation that turns a source into pages. Install-as-is, fork and copy-frozen are excluded by D6 (no skill or plugin packaging) and D10 (no licence grant anywhere in the body, so copying about a thousand lines of script verbatim is not defensible when the site defers software licensing to a header the scripts lack). Copy-plus-delta fails on the same ground and on fit: the delta would be larger than the kept part once multisite, SEO and doctrine obligations are stripped. What is worth keeping is a handful of conventions, each re-authorable in a few dozen lines: reserved index and log files with a newest-first date-heading check, typed relations restricted to a small set including `contradicts` and `source_for`, a source-record field list, a staged-proposals quarantine promoted only with a log entry, and the two-step analyse-then-write ingest rule. Re-author those and credit LlmWikis.org for the OKF-compatible shape, which its content licence asks for on quoted explanatory text.

**Facts carried from this body.** The bundle uses an Open Knowledge Format 0.1 reserved-file convention: the root index carries only the OKF version in frontmatter, the log carries none and is validated newest-first, and every other markdown file under the wiki root must have a non-empty `type`. Its OKF validator's link checker recognises only markdown link syntax, so Obsidian wikilinks are invisible to it, which was verified by a test page. The shipped preflight configuration fails the bundle's own tree with about 60 failures while the OKF validator on the same tree reports zero errors, so the two validators enforce incompatible rules for the reserved files. Raw sources over 256 KB are rejected unless byte-segmented, and the segmenter decodes the first 4,096 bytes as text, so the tooling assumes text is already extracted and is unsuitable for binary PDFs. Re-ingesting identical content is an error rather than a no-op. The scripts have zero third-party dependencies and there is no package manifest; the bundle manifest hashes 107 of the 108 entries. The only agent-facing instruction file is `AGENTS.md`.

### 13. kfchou/wiki-skills

Discovered through the `marketplace.json` code search. `https://github.com/kfchou/wiki-skills`. Pin `d9267ec9ccef1b43aa9f2a5f65c1fc56ac1701b0` (HEAD of main, 2026-07-03; `plugin.json` version 1.0.0; the repository has no tags or releases). Kind: a Claude Code plugin with a plugin manifest and a marketplace manifest, seven skills (`wiki-init`, `wiki-ingest`, `wiki-query`, `wiki-lint`, `wiki-audit`, `wiki-update`, `wiki-merge`), four standard-library Python helper scripts, a git pre-commit hook that `wiki-init` copies into each wiki, two link-style configuration files, and unit tests for the scripts.

**Maintenance.** Last push 2026-07-03 (the pinned commit); 181 stars, 30 forks; created 2026-04-05; 11 commits by one maintainer; no tags, no releases; two open issues.

**Originator and supplier.** kfchou, both; the pattern is credited to Karpathy's gist, and the HEAD commit carries an LLM co-author trailer.

**Licence.** MIT, found, at `LICENSE` lines 1-21, with `plugin.json` line 11 and the README.

```
MIT License

Copyright (c) 2026 kfchou

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND [...]
```

IP assertions: only the copyright line; no contributor agreement, patent or trademark clause. The design pattern is credited to Karpathy's gist but no code is taken from it.

**Verify.** Licence confirmed: 1,063 bytes, 21 lines, standard MIT, corroborated by the plugin manifest, the README licence section and the API SPDX id. Pin confirmed: SHA, committer date and commit message match, and the repository push date equals the pin, so it is still HEAD. Three rows re-checked, none refuted.

**Smallest part.** The citations convention plus the audit skill that enforces it: the citations block of the schema template (footnote grammar with a target, a locator, an optional line range and a verbatim quote, or a synthesis tag; three target forms; a PDF exemption) and `wiki-audit`, which carries its own inline fallback copy of the convention so it runs on a wiki that never saw `wiki-init`. Second-smallest: the two standard-library scripts that generate the index and run the mechanical lint, both unit-tested and usable on any flat pages directory after changing the two hard-coded path constants at their top.

**Fitting.** *Inputs:* a file path, copied to `raw/<filename>` if absent; a URL, through an unshipped browse skill; or pasted text; plus a schema file found by searching upward from the working directory, the wiki-root link-style configuration, and existing pages. The audit skill takes one page slug and its raw sources; the scripts take the wiki tree relative to their own location. *Outputs:* a source page with fixed sections (Summary, Key Takeaways, Entities and Concepts, Relation to Other Wiki Pages) and frontmatter (title, category, summary, tags, sources, created, updated) with numbered footnotes; created or edited entity and concept pages; backlinks; a regenerated, gitignored index; edits to an overview; and a git commit with an operation trailer on user confirmation, or an appended log entry on non-git wikis. Audit and lint write dated report pages; the mechanical lint emits JSON findings and clusters or a non-zero exit in staged mode. *Invocation:* `/plugin marketplace add kfchou/wiki-skills` then `/plugin install wiki-skills@wiki-skills`, after which the skills are invoked by name; the scripts run as `python bin/generate-index.py`, `python bin/lint-mechanical.py [--staged]` and `python bin/render-log.py`, and the hook runs them through `uv` after setting the git hooks path. *Harnesses:* Claude Code (the audit and lint skills dispatch subagents through the agent tool); Obsidian as an optional viewer through the default wikilink style; a CLI for the standard-library scripts, with the hook needing `uv`; Codex compatibility is untested here because the frontmatter is portable but the subagent dispatch and the browse dependency are Claude-Code-specific.

**Surplus.** Per-page footnote verification with a deterministic string-match fast path for footnotes carrying line ranges and one parallel subagent per raw file otherwise, plus uncited-claim detection and a verdict report: helpful for a research vault, at the cost that PDFs are exempt from line ranges so they always take the slow path. A cross-model adversarial review through an external CLI (neutral, an extra dependency). The line-range provenance convention with an immutable raw directory (helpful, and it makes the audit deterministic, at the cost that raw files must never be rewritten). A mechanical lint covering broken links, orphans, missing frontmatter, slug collisions, stale dates and missing concepts, plus a tag-cluster sweep (helpful hygiene, though each run adds a report page to the index). Merge and split with inbound-link rewriting; query with save-back; git-history-as-log through a commit trailer and a tracked pre-commit hook installed by taking over the hooks path (a cost: it conflicts with existing hooks, needs `uv`, is silently absent after a clone, and assumes the wiki root is the git top level); a contradiction gate that blocks the commit; a mandatory per-source interactive question-and-answer before any write; a generated, gitignored index; a configurable link style; and a domain guide.

**Coverage.**

**D1 covers** (evidence). `skills/wiki-ingest/SKILL.md` lines 68-74, the source-summary template.

```
## Summary

<2-3 paragraph synthesis — your own words, not abstract copy-paste>

## Key Takeaways

- <bullet>
```

A shipped per-source page template with a summary and a key-takeaways section, written to `wiki/pages/<slug>.md`, plus entities, concepts and relation sections and mandatory footnotes. PDFs and markdown are both accepted; the model reads the file itself, with no extractor shipped. Markdown and plaintext raws additionally get line-range provenance in footnotes.

**D2 does not** (evidence). `skills/wiki-init/assets/bin/lint-mechanical.py` line 23, with the fixed template and the caller-configurable choices in `wiki-init`.

```
REQUIRED_FIELDS = ("title", "category", "summary", "tags", "sources", "created", "updated")
```

The source page's body sections and frontmatter are fixed by the skill text, and the only per-project configuration `wiki-init` gathers is the path, the domain, the source types, the index category taxonomy and the link style, with no field list. No mechanism fills caller-supplied charting fields. A delta path exists: the schema file is caller-owned and every skill reads it for the page frontmatter format, and the mechanical lint tolerates extra frontmatter keys, so extra fields could be declared there; but that is an edit rather than a shipped capability.

**D3 partial** (evidence). `skills/wiki-init/SKILL.md` line 243 in the schema template, with the resolution options, the contradiction-check script, the index generator and the log rule.

```
commits. It is a **gate, not an annotation**: every page that lands in git is clean.
```

Cross-source concept and entity pages exist with a synthesis section and an appearances list, the index is a generated artifact with a tested script, and the log is append-only through git commits with an operation trailer or an appended log file. But contradiction handling is the inverse of the requirement: a blocking contradiction must be resolved before commit, the offered resolutions are to correct one page or the other, reconcile both with a scope qualifier, or declare it soft; the flag is removed on resolution, the check refuses commits that still carry it, soft tensions are surfaced rather than recorded, and the lint report asks which source to trust. Nothing persists a contradiction as a kept, flagged fact, so adopting the requirement as written means removing this gate.

**D4 covers** (claim). `skills/wiki-ingest/SKILL.md` line 23, with the raw-directory rule in `wiki-init`.

```
- **File path** — read it directly; copy to `raw/<filename>` if not already there
```

Ingest accepts an existing file path or pasted text and copies into the raw directory only when the file is not already there, so a note produced by another process is consumed without the skill owning its creation; the raw directory is explicitly user-managed and immutable. Prose only, and the per-source interactive stop still runs on every consumed note.

**D5 does not** (claim). `skills/wiki-ingest/SKILL.md` line 49.

```
Write `wiki/pages/<slug>.md`:
```

The page write is unconditional; the only idempotence anywhere is the raw copy's if-not-already-there. A grep of the skills for hash, idempotent, re-ingest and dedup finds no hashing or re-ingest logic, so re-running ingest on an unchanged source repeats the full interactive process and rewrites the page along with the entity pages, index, overview and log.

**D6 covers** (evidence). `.claude-plugin/plugin.json` lines 2-3, with the marketplace manifest and the README install lines.

```
"name": "wiki-skills",
  "version": "1.0.0",
```

A Claude Code plugin with both manifests present, installing as-is from the repository acting as its own marketplace. Codex compatibility, recorded separately: each skill file uses portable name-and-description frontmatter, but `wiki-audit` and `wiki-lint` dispatch subagents through the Claude Code agent tool, `wiki-ingest` fetches URLs with a browse skill that is not shipped in this repository, and the pre-commit hook shells out to `uv`; nothing in the body demonstrates a Codex run.

**D7 covers** (evidence). `skills/wiki-init/assets/bin/generate-index.py` lines 11-12, with the layout tree in `wiki-init`.

```
WIKI_ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = WIKI_ROOT / "wiki" / "pages"
```

Covers only the second clause: the layout is fixed and stated explicitly, with a schema file, a link-style configuration, a scripts directory, raw and asset directories, a generated index, a log for non-git wikis, an overview, and a flat pages directory. It does not adapt to a caller-chosen layout; the scripts hard-code paths relative to their own location. An additional constraint found in code: the gate machinery assumes the wiki root is the git top level, because the hook resolves the repository top level and the contradiction check filters staged paths by a root-relative prefix, so a wiki nested inside an existing vault repository, a case the init skill itself contemplates, would not be gated. Obsidian browsing works through the default wikilink style because Obsidian resolves by basename.

**D8 partial** (claim). `skills/wiki-ingest/SKILL.md` lines 44-45, with the sources frontmatter, the footnote targets and the link parser.

```
Lowercase, hyphens, no special characters.
Example: "Attention Is All You Need" → `attention-is-all-you-need`
```

A stable id, the slug, is used consistently in page links, the sources frontmatter list and footnote provenance markers, which is half the requirement. But the slug is generated by the tool from the title rather than supplied by the caller, and no citekey, BibTeX or Zotero mention exists anywhere in the body. A lowercase-hyphen citekey would fit the slug character set; mixed-case or underscore keys would not parse.

**D9 partial** (claim). `skills/wiki-ingest/SKILL.md` line 40, with the commit rule at line 271.

```
Wait for the user's response before proceeding.
```

A human gate is documented and mandatory per source: two stops per ingest (a pre-write takeaways exchange, then a commit confirmation) plus a hard stop on any blocking contradiction. It is not configurable and there is no batch mode; the only batch hits are prohibitions, and the README says to add sources one at a time, so importing many sources means many interactive dialogues.

**D10 covers** (evidence). `LICENSE` lines 1-3 with `plugin.json` line 11.

```
MIT License

Copyright (c) 2026 kfchou
```

MIT grants use, copy, modify, merge and distribute; the only condition is retaining the notice.

**C5 covers** (evidence). `skills/wiki-init/SKILL.md` line 28, with the standard-library scripts and the hook.

```
   2. GitHub / VS Code preview / static-site generator / plain markdown — uses `[[slug](pages/slug.md)]` syntax
```

A plausible cross-lane cover for the headless clause only: nothing depends on the Obsidian application, the skills run inside Claude Code, the scripts are standard-library Python invoked from a shell or a git hook, and a non-Obsidian link style is offered. The candidate reads no Zotero at all, so the capture requirements proper are untouched.

**C6 covers** (evidence). `LICENSE` lines 1-3. Same MIT licence as D10; the quote is the licence block above, at those lines.

**Treatment opinion: copy plus a delta.** Install-as-is does not apply because two floors fail: D2 is absent (a fixed template with no caller-supplied field list) and D3 is inverted (the contradiction gate deletes or reconciles one side before commit, and a script enforces that). The remaining gaps, D5's no-op, D8's caller-supplied id and D9's batch mode, all sit in the core of the ingest skill and the schema template, so the required deltas are policy changes to that file rather than additive settings. A fork would carry those inversions against every upstream edit to the same file, and upstream is a single-maintainer repository with eleven commits, no tags and two open issues, so tracking it buys little. Copy-plus-delta fits: take the MIT-licensed pieces that stand alone and match the requirements well (the citations convention with line-range provenance, the audit skill, which carries its own fallback convention, and the two tested standard-library scripts, with the two path constants edited and the root-relative filter fixed if the vault is nested) and write the ingest against the caller's charting fields, citekey slugs, a content-hash manifest, a kept-and-flagged contradiction record and a batch mode, crediting the project under MIT. Drop the hooks-path takeover and the browse dependency.

**Facts carried from this body.** The plugin is an implementation of Karpathy's gist, credited in the README. The footnote citation grammar pairs a semantic locator with a line range into the immutable raw file, and offers a synthesis tag as the only alternative to a verbatim quote, which is a reusable provenance convention. The Claude Code install form when a repository is its own marketplace is to add the repository as a marketplace and then install `<plugin>@<marketplace>`. The shipped git hook runs its Python gates through `uv` and resolves its script directory from the git top level, so the gate assumes the wiki root is the repository root and that `uv` is installed. The index generator parses only scalar key-value frontmatter lines and has no YAML dependency, so multi-line YAML in page frontmatter is invisible to it.

### 14. gaebalai/cc-llm-wiki

Discovered through the `marketplace.json` code search. `https://github.com/gaebalai/cc-llm-wiki`. Pin `158c6ab30a86d9bcb3b53c1f77b7c0d8ad71e098` (master HEAD, 2026-05-17; `VERSION` 0.4.4.0 per the changelog and manifest). Kind: a Claude Code plugin, that is a marketplace manifest plus a plugin manifest, eight skills, one install command, hooks in the project settings, Python graph scripts, and a shipped sample vault.

**Maintenance.** Last push 2026-05-17 (the HEAD commit); 3 stars; a single author; the changelog runs from 0.1.0 to 0.4.4 with every release dated 2026-05-17 or 18, so the whole project was built in a two-day burst and has not been touched in the roughly three and a half months since. CI workflow present.

**Originator and supplier.** Jaewoo Kim (`gaebalai`), both, for the plugin code and skills; the design lineage is credited to Karpathy's pattern and to a series of third-party articles, one of which, translated, is the shipped sample raw file.

**Licence.** MIT, found, at `LICENSE` lines 1-21, with the plugin manifest and the changelog.

```
MIT License

Copyright (c) 2026 Jaewoo Kim <jaewoo@claudecode.to>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software
```

IP assertions: none beyond the notice. One caveat worth recording: the shipped sample raw file is a Korean translation of a third-party article, and its own licence is not stated anywhere in the tree.

**Verify.** Licence confirmed at the pin, matching verbatim including the copyright line, and corroborated by the manifest. Pin confirmed: SHA and committer date match, and the manifest reports the version the pin claims. Three rows re-checked, none refuted.

**Smallest part.** The pre-tool-use raw-guard hook: a single Node one-liner in the project settings that reads the tool input from standard input and exits with a blocking code for any write whose path matches the raw folder. It is self-contained, harness-native and portable by changing one regular expression. The next-larger separable unit is the ingest and compile skill pair together with the schema document's frontmatter keys and its ten lint rules, which define the raw-to-drafts-to-topics gate and depend on nothing else in the repository.

**Fitting.** *Inputs:* one markdown file per invocation under the raw directory in one of six genres, passed as a path or auto-suggested as the newest raw lacking a draft. PDF is not read; text must already be markdown. Optional inputs are an alias file for the graph layer, a positioning file for the digest, and environment variables for the optional Neo4j and Slack layers. *Outputs:* a draft page under the drafts directory with eight-key frontmatter and four fixed Korean-headed sections, plus one appended log line; on compile, a git move into topics or decisions with the status changed, one appended index line and one log line, and no commit; lint writes a dated report; the graph sync upserts to Neo4j and updates a frontmatter timestamp; the digest writes a dated page on a branch with a pull request. *Invocation:* inside a Claude Code session, `/ingest`, `/compile`, `/lint`, `/query`, `/graph-sync`, `/morning-brief`, `/evening-reflect`, `/daily-digest`, with an install command wrapping the shell installer. Routine files are cron specifications that must be registered separately. Hooks use Node and bash, so both are required at runtime. *Harnesses:* Claude Code (plugin, skills, settings hooks and the ask-user tool). Obsidian is listed as a manifest requirement and used for a dashboard and web-clipper capture, but ingest, compile and lint use only file tools and git, so they run headless. Neo4j through Docker and Python 3.10 or newer are needed only for the graph parts; the installer is macOS-centric.

**Surplus.** A Neo4j graph layer with its own scripts, templates, Docker compose, alias table and a queue hook, which costs Docker, a Python driver, an optional cloud key and a nightly maintenance routine; an external-source daily digest with web search, a Slack webhook and pull-request automation on branches; git-flow conventions baked into the skills and hooks, including a hook that blocks pushing to main, which directly conflicts with this repository's own merge-and-push rule; Korean-language prose throughout, including the generated section headings, so every instruction needs translation before an English-operated vault could use it; Obsidian-specific assets including a Dataview dashboard; a morning-brief skill with session hooks; an evening-reflect skill with a stop hook that can block session end; a lint skill with ten schema rules and a report, which is helpful though prose-executed; a private folder with a model-read-only policy; and a seven-step interactive installer that mixes environment setup with vault scaffolding.

**Coverage.**

**D1 covers** (evidence). `skills/ingest/SKILL.md` lines 72-83 (the body template) with the shipped worked example and its log line.

```
## 핵심 주장
  (3~5줄, raw의 핵심)

  ## 횡단적 지견
  - [[related-slug-1]]과의 공통점: ...
  - [[related-slug-2]]와의 차이: ...

  ## 인용
  > raw에서 발췌 (페이지/타임코드/줄 번호 보존)

  ## 미해결 질문
```

One raw markdown file produces exactly one draft page with a fixed four-section body: a three-to-five-line core-claim summary, cross-cutting insights linking other pages, verbatim quotes with a page, timecode or line locator, and open questions. Three shipped topic pages were produced this way from the shipped raw article. Caveats: input is markdown only, so PDF text must be pre-converted and dropped into one of six genre folders; the section headings and all instructions are Korean; and the skill forbids plain summarisation in favour of a discussion shape.

**D2 does not** (evidence). `skills/ingest/SKILL.md` lines 68-71, with the frontmatter key list in the schema document.

```
### Step 5. 본문 작성 (토론형)
- 단순 요약 금지 — **횡단적 지견** 섹션을 만들어 다른 페이지와의 연결을 명시
- 본문 구조:
```

The per-source body structure is hard-coded in the skill (four fixed sections) and the frontmatter key set is fixed by the schema with lint rule 1 failing on missing keys. There is no template file, argument or configuration hook through which a caller supplies a project-specific field list. The only template in the repository configures the external-search digest rather than per-source charting.

**D3 partial** (claim). The schema document's evidence-first rule, with the index and log files, the compile skill and the evening-reflect detector.

```
5. **반증 우선**: 모순 발견 시 기존 페이지를 덮어쓰지 말고 `CONTRADICTS` 메모 추가 → 사람에게 토론 요청
```

The index and the append-only log are real shipped artifacts: the index is a catalogue to which compile appends one line, and the log is time-ordered append-only with every skill defining its log line format. Contradiction handling exists only as prose policy (add a note, never overwrite) plus a git-diff grep in the evening skill that flags newly added contradiction lines as a warning; no shipped page contains such a marker and no marker syntax is defined beyond the word. Cross-source concept pages are weak: ingest asks whether to extend an existing topic but always writes a new draft, compile forbids restructuring the draft, and no step merges a second source into an existing topic's source list. All three shipped topics derive from a single raw file.

**D4 covers** (evidence). The pre-tool-use hook in the project settings, with the ingest skill's read-only rule, the init-mode rule and the sweep routine.

```
if(/(^|\/)vault\/01_raw\//.test(p)){console.error('[hook] vault/01_raw/ is Read-Only. See CLAUDE.md §2.');process.exit(2)}
```

Capture is entirely outside the tool: raw files are dropped into the genre folders by the user or by the Obsidian Web Clipper, the tool only reads them, and a hook blocks any write under the raw directory. The ingest skill takes a target path or auto-suggests the newest raw lacking a paired draft. The caveat is that the hook's regular expression requires the literal path segment, and in the plugin's default flat install mode the raw folder sits directly under the target directory, so the guard silently does not fire unless the vault directory happens to be named as the pattern expects; the separation still holds by skill design, but the mechanism is prose-only in flat mode.

**D5 does not** (evidence). The ingest skill's failure branch, against the absence of hashing anywhere.

```
- 동일 `id`가 이미 존재 → 새 timestamp로 재생성 시도, 3회 실패 시 중단
```

There is no content hash, modification-time record or source-to-draft registry: a grep for hashing across the skills and scripts finds only installer idempotency and a third-party mention inside the sample article. Re-running ingest on an already-ingested raw mints a new timestamp identifier and writes another draft, the opposite of a no-op. The only pairing logic is the candidate-selection heuristic, which is a suggestion for which file to pick rather than a guard, and it stops matching once the draft has been compiled out of the drafts folder.

**D6 covers** (evidence). `.claude-plugin/plugin.json` lines 1-3, with the marketplace manifest and the skill and command files.

```
{
  "name": "cc-llm-wiki",
  "version": "0.4.4",
```

A standard Claude Code plugin layout whose JSON and skill frontmatter are validated in CI. Installable-as-is caveats found in the body: hooks live in the project settings rather than a plugin hooks file, so they are not applied by a plugin install and are instead merged into the user's settings by the installer when the install command is run; all skill paths hard-code the subdirectory prefix while the documentation makes the flat mode the default for new users, and the hook regular expressions do the same; the manifest carries non-standard requirement and note keys; and all skill prose, hook messages and generated headings are Korean. Codex compatibility: none present. There is no `AGENTS.md` and no Codex mention anywhere in the body, and behaviour depends on Claude-Code-specific frontmatter fields, the ask-user tool and settings hooks.

**D7 covers** (evidence). The installer's layout detection, with the layout contract in the project instructions and the shipped tree.

```
VAULT_DIR="$TARGET_DIR"
VAULT_MODE="flat"
if [ -d "$TARGET_DIR/vault/.obsidian" ] || [ -d "$TARGET_DIR/vault/01_raw" ]; then
  VAULT_DIR="$TARGET_DIR/vault"
  VAULT_MODE="subdir"
```

The layout is not caller-chosen but it is stated explicitly and enforced: a fixed three-tier tree of raw with six genres, wiki with six subfolders and a schema directory, plus a schema document, an index and a log at the vault root, with the installer auto-detecting whether that tree sits at the target directory or one level down. Lint rules enforce the wiki filename pattern and warn on raw filenames that do not match the date-slug form. Adapting to a caller-chosen layout means editing every path in eight skill files and four hook regular expressions; the states-its-layout clause is what is satisfied.

**D8 partial** (evidence). The schema document's frontmatter contract, with the shipped provenance line, the quote locator rule and the slug approval step.

```
id: <ISO8601-timestamp>-<kebab-slug>   # 불변, 4층 공유 키
type: topic | decision | self | digest # enum 외 값은 lint 실패
status: draft | reviewed | published   # status 게이트
locale: ko | en | ja                   # 기본 ko, publish가 파생 생성
sources: [<vault/01_raw/...>]          # 출처 명시 (없으면 lint 실패)
```

Every page carries a mandatory sources array whose entries are vault-relative raw file paths, with lint failing on an empty one, and quotes must keep a page, timecode or line locator. But the stable identifier is a tool-minted page id plus the raw path; there is no caller-supplied source id such as a citekey, and links between pages are slug wikilinks rather than source ids. A caller could smuggle a citekey into the raw filename, since the slug is user-approved, but the lint expects a date prefix and the path would still be the only reference form.

**D9 covers** (evidence). The compile skill's frontmatter, with the ingest checkpoints, the batch prohibition and the sweep routine.

```
name: compile
description: vault/02_wiki/_drafts/ 의 draft 1건을 사람 승인 후 vault/02_wiki/topics/ 또는 decisions/ 로 승급한다. 승급 전 lint 동등 검사를 수행해 ERROR 가 있으면 거부한다. [...] 사용자가 명시적으로 "/compile <draft_path>" 라고 호출했을 때만 발동한다 (자동 호출 금지).
disable-model-invocation: true
```

The gate is documented and mechanised at per-source granularity: ingest has two mandatory human checkpoints before it writes the draft, and promotion to the topics folder is a separate skill that is user-invocable only through the Claude Code frontmatter field, refuses on lint errors (broken wikilinks escalate from warning to error at promotion), and moves the file with git without committing. Batch is explicitly forbidden rather than configurable, and the hourly sweep routine only notifies, so the gate is documented as per-source only.

**D10 covers** (evidence). `LICENSE` lines 1-3 with the plugin manifest.

```
MIT License

Copyright (c) 2026 Jaewoo Kim <jaewoo@claudecode.to>
```

Standard MIT permitting use, copy, modification, merge, distribution and sublicensing subject to notice retention; the manifest's licence field agrees.

**Treatment opinion: copy plus a delta.** Install-as-is is not supported by the body: two floors are unmet (D2 has no caller-supplied template mechanism; D3's contradiction handling is prose-only and multi-source synthesis has no procedure), D5 is the inverse of a no-op, the guard hooks and every skill path hard-code the subdirectory prefix so they silently stop working in the plugin's own default flat mode, hooks are not delivered by a plugin install, the git-push-to-main deny hook conflicts with the consuming repository's merge-and-push rule, and all prose is Korean. A fork would drag along the Neo4j, Docker, Slack and daily-digest surplus that is roughly two thirds of the repository. What is worth taking is the mechanisms rather than the rules: the raw-guard hook one-liner with its regular expression parameterised to the caller's raw folder; the frontmatter contract and the ten-rule lint table as a schema for a scripted linter; the ingest-to-drafts-to-compile gate shape with the model-invocation flag on the promotion skill; and the one-line-per-action log format. The delta is substantial: translate to English; add a per-project field list injected into the draft body; define a contradiction marker and a multi-source append procedure; record a content hash per source so re-ingest is a no-op; replace the raw-path reference with a caller-supplied id; and drop the git-flow hooks. Because the retained pieces are small and concrete while the prose must be rewritten anyway, this lands as copy-plus-delta rather than author-and-credit, and MIT permits it with notice retention.

**Facts carried from this body.** This plugin ships its Claude Code hooks in the project settings rather than a plugin hooks file, and relies on its installer to merge them into the user's settings, a merge that is skipped unless the script detects it is running from a plugin directory. The skill frontmatter field that makes a write-capable skill invocable only by explicit user command or routine, never by the model on its own, is applied here to compile, evening-reflect and daily-digest. The shipped sample article records an identity-design trade-off relevant to re-ingest: when a graph loader is given no explicit metadata id, the source node's merge key becomes a content hash, so any minor edit creates a new source identity, which is why this project fixes the frontmatter id as the shared key instead.

### 15. ussumant/llm-wiki-compiler

Discovered through the `marketplace.json` code search. `https://github.com/ussumant/llm-wiki-compiler`. Pin `f43551b0a8dd680f0422a7e2e2216d3c4f5ca04c` (main; `plugin/.claude-plugin/plugin.json` version 2.1.0; the repository has no git tags and no GitHub releases). Kind: a Claude Code plugin of prompt markdown, twelve command files, templates, a bash session-start hook and a zero-dependency Node visualization server; it also ships a Codex plugin manifest and a portable, agent-agnostic compile protocol.

**Maintenance.** Last push 2026-08-21 (a funding-link commit); 321 stars; 32 commits since 2026-04-04 by a single author; no tags, no releases (the 2.1.0 version exists only in the manifests); no tests, no CI workflows. The last substantive change was 2026-07-10, adding the portable protocol and its deployment tooling, whose inline-configuration path is self-described as pending cross-platform verification.

**Originator and supplier.** Sumant (`ussumant`), both; all 32 commits are his, and the manifest and licence agree.

**Licence.** MIT, found, at `LICENSE` lines 1-8 with the Codex manifest line 11; the Claude plugin manifest carries no licence field, which is a manifest omission rather than a conflict.

```
MIT License / Copyright (c) 2026 Sumant / "Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software"
```

IP assertions: nothing beyond the copyright line. The X adapter credits a third-party MIT tool it drives but does not vendor.

**Verify.** Licence confirmed: the standard 21-line MIT text at the pin with the copyright line as recorded, and the Codex manifest agreeing; the record's observation that the Claude manifest omits the field was verified (its keys are name, version, description, author and keywords only). Pin confirmed: SHA, message and date match, as do the repository push date and star count. Three rows re-checked, none refuted.

**Smallest part.** The synthesis phases of the skill, lines 200-318, which carry the concept-page discovery and format block, the schema generate-or-update step with its evolution log and never-remove rule, the index block, and the log-append plus state-write step, together with the schema and index templates. That is the contradiction and index machinery and it lifts without the earlier phases, the codebase mode, the capture adapters, the hook or the visualizer. The author also ships a designed alternative: a self-contained, plugin-free copy of the whole algorithm with templates inlined, for a caller who wants the full compile loop rather than only the synthesis phases.

**Fitting.** *Inputs:* a configuration file at the project root (or the nearest parent, or a global knowledge directory) declaring mode, source directories with excludes, an output directory, a name, topic hints, a link style, article sections with name and description, and codebase-mode extras. Knowledge mode reads every markdown file under the sources; codebase mode reads README, instruction and architecture files and optionally about twenty code files per topic. A prior schema and state file are read if present. Source dates come from frontmatter, then the filename, then the modification time. The capture path takes a URL plus free-text user context. *Outputs:* topic pages with frontmatter and one section per configured section carrying a coverage tag, plus a sources list; concept pages; a schema document with topics, concepts, article structure, naming conventions, cross-reference rules and an evolution log; an index; a log appended per run; a state file with the compiled topics, source locations and a scanned count; and, in codebase mode on the first run, a context document. Captures are written under a captures directory from a captured-source template with user context, extracted content, relevance notes, candidate connections and provenance. *Invocation:* Claude Code slash commands for init, global init, compile with full, topic and dry-run flags, ingest with a quiet flag, capture with a context and a no-update flag, lint, query, search, visualize, fetch-bookmarks, migrate and upgrade; Codex through natural-language prompts mapped in the skill; any agent through the portable protocol deployed into the output directory. *Harnesses:* Claude Code plugin (root marketplace manifest pointing at the plugin directory, plugin manifest, a session-start bash hook that shells to Node to parse the configuration and print wiki context with a modification-time-based stale warning); a Codex plugin manifest and marketplace with no Codex hook; the session-start wrapper also emits Cursor-shaped and generic JSON. Obsidian-compatible output through the default wikilink style, with no Obsidian plugin.

**Surplus.** Codebase mode with its own template and context document, roughly half the skill's 21 KB, which is dead weight for a literature vault; a zero-dependency knowledge-graph visualization server; the fetch-bookmarks path, which installs a third-party CLI globally, reads browser cookies and offers a daily scheduled job; URL capture adapters for web, X and YouTube plus the captured-source template, whose per-source shape is a reasonable seed though it is URL-keyed; time-decay annotations with aging and stale thresholds tuned for tooling bookmarks rather than journal articles; per-section coverage tags, a cheap and useful trust signal; a migration command that rewrites the startup section of the repository's own instruction files; a session-start hook injecting wiki context into every session in any directory with a configuration file; a query mode that files answers back into topic articles with a filed-from marker, which muddies provenance; a global wiki default with routing; parallel subagent compilation, helpful for speed and prone to stopping after phase three; and the portable protocol plus its deployment scripts, which give Codex parity at the cost of a second copy of the algorithm that the author admits can drift.

**Coverage.**

**D1 does not** (evidence). The skill's concept-extraction instruction, with the merge module's own comment.

```
1. For each entry in `sources[]`, list all `.md` files using Glob
```

The compile pipeline is many-sources-to-one-topic: every write target in the algorithm and in the shipped templates is a topic article synthesized from all files classified under that topic, and no phase emits a page whose subject is the source document. The ingest command reads one file, but its three-to-five bullet summary goes to the chat and then updates topic articles, so no per-source page is written. The only per-source file shape shipped is the captured-source template, which is the capture input for a URL rather than a digest emitted from a document. PDF appears once in the body, as a paste fallback in the web adapter, and the first phase scans markdown only.

**D2 partial** (evidence). The skill's article-section step, with the shipped configuration instance and the portable protocol.

```
   - If `.wiki-compiler.json` has an `article_sections` array: use those sections in order. Each section's `description` field tells you what content belongs there.
```

The mechanism the requirement asks for exists: a caller-supplied ordered field list of name, description and optional requiredness read from the project configuration, with a shipped instance and an init command that proposes domain-specific sections, including a research preset listing key findings, methodology, evidence, gaps and contradictions, and open questions. But it structures topic articles rather than a per-source charting record, and a page-locator field has no per-source home. The right mechanism at the wrong granularity: satisfying the floor would need a new per-source phase.

**D3 partial** (claim). The skill's conflicting-sources rule, with the no-deletion rule, the concept-page format, the index block, the log format, the schema evolution log and the lint counter-signal.

```
   - **Conflicting sources**: when two sources disagree and one is materially newer (>12 months for time-sensitive, >24 months for stable), prefer the newer synthesis and note the shift explicitly in Key Decisions: `"YYYY-MM: {earlier framing} → {new framing}"`. Attribute both to their source files.
```

Cross-source synthesis pages gated at three or more topics, an index with a concepts table, an append-only log, and a schema with an append-only evolution log are all shipped as templates or worked blocks, and the skill states that stale content is not to be deleted but flagged, re-ordered or annotated, because the wiki is a time-series artifact. The contradiction half is prose only and weaker than the requirement: conflicts are handled by preferring the newer synthesis with both sides attributed, and only when one source is materially newer; same-age contradictions have no stated rule beyond a lint flag suggesting the user find the correct value. The no-deletion rule does protect the losing side from erasure.

**D4 covers** (evidence). The X adapter's description of a third-party writer's directory, with the ingest command's arbitrary path, the capture command's no-update flag, and the skill's safety rule.

```
- Field Theory writes markdown into nested subdirectories under `~/.ft-bookmarks/md/`. Each bookmark becomes its own `.md` file under `~/.ft-bookmarks/md/bookmarks/`. (Future `ft classify` runs may add `~/.ft-bookmarks/md/categories/` and similar.)
```

Ingest and integrate are cleanly separated: the source array is any directory of markdown files that the tool treats as read-only, the X adapter is a shipped worked example of another process writing the notes while the compiler merely registers the directory, the ingest command takes an arbitrary existing file path, and capture has an explicit flag that stops after writing the source file. A vault where a Zotero-side process writes literature notes into a listed directory would be consumed without the plugin owning creation.

**D5 partial** (evidence). The state-file schema, with the incremental comparison, the lint staleness check and the hook's modification-time count.

```
  "topics": ["{slug1}", "{slug2}", ...],
```

Incremental compilation is the stated default with a full-rebuild flag, but the shipped state schema records only a path list plus a single last-compiled date, so a changed file cannot be distinguished from an unchanged one by content; the only concrete change detector in the body is a modification-time comparison in the hook script and the lint, both outside the compile path. Re-ingesting an unchanged file through the ingest command has no idempotence check at all.

**D6 covers** (evidence). The root marketplace manifest's source pointer, with the plugin manifest, the hook registration and the skill frontmatter.

```
      "source": "./plugin",
```

Installable as-is as a Claude Code plugin: a root marketplace manifest pointing at the plugin directory, a plugin manifest, a commands directory, a skill, and a hooks file registering a session-start bash hook. Runtime needs bash and Node for that hook. Codex compatibility, recorded separately: a separate Codex plugin manifest and marketplace ship, slash commands are replaced by a natural-language prompt table, no Codex hook is registered, and the author also ships the portable protocol for any agent with no plugin at all.

**D7 covers** (evidence). The init command's directory creation, with the caller-chosen roots in the configuration and the fixed subtree.

```
1. Create `wiki/`, `wiki/topics/`, `wiki/concepts/` directories
```

Source directories and the output root are caller-chosen through the configuration, and the fixed subtree under the output is stated explicitly everywhere it matters: topics, concepts, index, schema, log, state and a context document in codebase mode, plus a captures directory. It runs on an existing markdown vault as long as the output directory is excluded from the sources. Obsidian wikilinks are the default link style.

**D8 does not** (evidence). The article template's sources link form, with the link-style rule and the relative-path rule.

```
- [[relative/path/to/source]]
```

Every provenance marker in the body is a relative file path from the topics directory to the source file; there is no notion of a caller-supplied stable id, and the capture template's provenance section keys on URL and date. A grep for citekey, cite key, BibTeX and Zotero across the plugin, the portable protocol and the exporting guide returned no hits. A citekey-named file would incidentally yield a citekey-bearing path link, but that is a property of the caller's filenames rather than a tool feature, and renames would break provenance silently.

**D9 covers** (claim). The ingest command's wait instruction, with its confirmation step, its quiet flag, the capture confirmation, the compile dry run and the schema-removal rule.

```
- Wait for the user's response before proceeding — this is the interactive part where the user guides what matters
```

Per-source integration has a documented two-step human gate (discuss takeaways, confirm the topic mapping) that is configurable off with a quiet flag or a no-update flag. Batch integration through compile has no confirmation gate and writes directly, but offers a dry run as a preview, and schema removals always require human approval. The per-source versus batch asymmetry is documented, which is what the requirement asks; the basis is a claim because the gate is prompt instructions rather than enforced code.

**D10 covers** (evidence). `LICENSE` line 8 within the full text.

```
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
```

MIT permits use and modification; the licence file is at the repository root and the Codex manifest repeats it. The driven third-party CLI is credited as MIT and is neither vendored nor required for the digest path.

**Treatment opinion: copy plus a delta.** Install-as-is is excluded by two floors: D1, because pages are per concept and merged across sources with the scan restricted to markdown and PDF appearing only as a paste fallback, and D2, because the caller-supplied field list structures topic articles rather than a per-source chart. D8 adds a path-based provenance with no stable id, and D5's state schema has no hash. What the body does well, and what this set otherwise lacks, is the cross-source layer: concept pages gated on three or more topics, a schema with a never-remove rule and an evolution log, an index with aliases, an append-only log, per-section coverage tags, no deletion of stale content, and a documented per-source review gate separable from batch compile. Because the whole body is prompt markdown under MIT, the economical treatment is to copy the synthesis phases with the schema and index templates (or the portable protocol if the full loop is wanted) and add the delta the floors demand: a per-source digest phase writing one page per source keyed by citekey; a per-source charting template fed by the caller's field list, for which the existing article-sections shape can be reused verbatim; citekey-based provenance markers in the sources lists; a content hash per source in the state file; and a keep-and-flag contradiction rule replacing prefer-newer. A fork is not warranted: the codebase mode, capture adapters, bookmark sync, hook and visualizer are surplus that would have to be carried. If the caller judges the many-to-one topic framing too far from a per-source literature workflow, author-and-credit is the fallback, and the licence permits either.

**Facts carried from this body.** The body is internally inconsistent about the log filename: the skill, the lint and the query write to one name while the ingest and init commands use another, so an ingest-then-compile vault ends up with two logs. The session-start hook shells out to Node to parse JSON, so the plugin's hook silently does nothing on a machine without Node on the path, because the call is error-suppressed. The Codex ecosystem shape used here is a Codex plugin manifest with a skills directory pointer and an interface block, plus an agents-level marketplace manifest with a local source and install policy, and the author states that no Codex hook is registered because no supported hook schema is available yet. The session-start wrapper emits three different JSON envelopes depending on host environment variables, which is a reusable pattern for multi-harness hooks. Stale detection is modification-time based against the compile date rather than content-based.

### 16. pumblus/okf-harness

Discovered through the `marketplace.json` code search; recorded as the only Open Knowledge Format conformance tool in the field. `https://github.com/pumblus/okf-harness`. Pin `0dd4f806c454a68088c5a3e64b4cbebbe2c216be` (HEAD of main, committed 2026-08-14T10:53:20Z; package and plugin version 0.8.1). Kind: a Claude Code plugin, that is a monorepo with a Claude plugin, an Agent Plugins package for Codex and others, and an npm runtime with a core library, an agent pack and a setup launcher.

**Maintenance.** Last push 2026-08-14; 34 stars; a single author; version 0.8.1; a CI workflow, issue templates, a security policy, a contributing guide, 54 architecture decision records and a roadmap; vitest suites across all four packages plus golden-file tests for the Claude and Codex adapters.

**Originator and supplier.** Originator Eric Zhou (the author field in the package, plugin and marketplace manifests, and the copyright holder). Supplier the GitHub account `pumblus`, plus the npm scope and a scoped package.

**Licence.** Apache-2.0, found, at `LICENSE` (the full text) with the plugin manifest line 11, the package manifest line 6, and the skill frontmatter line 4.

```
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/ [...] Copyright 2026 Eric Zhou

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License.
```

IP assertions: the standard Apache grants (copyright section 2, patent section 3) and the section 4 redistribution conditions, that is retain notices and mark modifications. There is no notice file. One vendored third-party file is an unmodified copy of the official Agent Plugins manifest JSON schema, with no licence stated there; it is used only by tests and is not shipped in the plugin.

**Verify.** Licence confirmed at the pin: the header lines match, the appendix carries the copyright line and the standard grant paragraph, and Apache-2.0 is declared consistently in the plugin manifest and the skill frontmatter. The record's quote elides the sentence tail without an ellipsis marker, but the quoted words are verbatim and unaltered, and the cited line numbers are within about one line of the actual. Pin confirmed: SHA and committer date match exactly, and the star count and push date match. Four rows re-checked, none refuted.

**Smallest part.** The Codex-facing agent-pack templates, the skill plus its ingest, reconcile, answer and check reference files, about 17 KB of plain markdown with no build step. That is the actual digest, reconcile and answer workflow prose that the Claude workspace adapter installs verbatim, and it stands alone once the CLI command lines are swapped for the vault's own verbs. The companion shape to take with it is the shipped reference page example with its frontmatter, summary, key points and citations. The next-smallest code piece is the core's source module set (a SHA-256 manifest, reused-on-same-hash, same-filename revision edges and an append-only ledger), which depends only on the configuration and path modules.

**Fitting.** *Inputs:* a local file path of any type (mime-tagged for markdown, text, PDF, HTML and JSON, otherwise a byte stream) or an http URL recorded as a pointer and never fetched; a workspace directory containing a configuration file declaring the version, workspace name, runtime version pin, OKF bundle root, paths and a maximum-files-changed-per-ingest safety value; for answers, a question with an optional budget. *Outputs:* an immutable copy under a dated raw path; one JSONL row per source in a manifest with an id, kind, original, path, SHA-256 and added-at; reconciliation rows linking a prior source to a revision; agent-written pages, that is a reference page with frontmatter, summary, key points and a citations list of source ids, plus topic, entity, project, decision and question pages citing reference paths, together with index link entries; a backlinks file and a graph report; and every command printing a JSON envelope on standard output. *Invocation:* Claude Code `/okf-harness <request>`, whose skill shells to a launcher; direct CLI `okfh init|source add|ingest plan|check|source reconcile|evidence|read|search|graph|checkpoint|history|restore|doctor|agent install`. *Harnesses:* Claude Code (root marketplace plus plugin, a workspace-local adapter and a managed block in the project instruction file); Codex (an Agent Plugins package installed through a marketplace command, plus a workspace-local adapter and a managed block in `AGENTS.md`); host skills for other agents; a CLI on Node 22 or newer with npm access; and a git-based workspace-recovery dependency. Not Obsidian: the roadmap keeps Obsidian support documentation-first with no runtime dependency.

**Surplus.** Deterministic, non-vector evidence briefs with provenance pointers and seals that withhold pages whose source is missing, drifted or unregistered, which is helpful for an answer workflow at the cost of a second retrieval surface; suspected-revision detection by same original filename plus a different hash, with an append-only reconciliation ledger and a currency seal, helpful for re-imported changed notes though revision identity is by filename so renamed notes never form an edge; git-backed checkpoint, history and restore with opaque completion ids, helpful as an undo at the cost of hiding git; a backlinks and HTML graph report; a lint vocabulary of nine codes with ready, needs-attention and blocked triage, helpful as a vault-integrity model at the cost that OKF frontmatter conformance is mandatory for every markdown file under the wiki root; a per-workspace runtime version pin resolved through a floating setup package, so each skill invocation resolves a package from npm and the pinned CLI is fetched on first use, which is not offline; multi-host distribution and a doctor with host probes; an answer path that may write a conversation-derived page with no citations on a proven no-match, a cost for a vault that wants every page anchored to a source; URL sources registered as pointers only; and Chinese-language documentation plus a static homepage build.

**Coverage.**

**D1 covers** (evidence). The shipped example reference page, with the checklist string in the ingest module.

```
# Summary

The source describes a local LLM Wiki pattern where raw material stays separate from synthesized wiki pages.

# Key Points

- Raw source material is the evidence layer.
```

The per-source page is the OKF reference document: frontmatter with a type, title, description, resource path, tags, timestamp and source id, plus summary, key points and citations sections, shown by the shipped example and by the core test fixture. The CLI itself never writes it: the skill states that the CLI does not synthesize wiki content, the ingest plan returns a recommended reference path plus a checklist, and the agent writes the page under the ingest workflow reference. Markdown and text sources are read directly by the agent; PDFs are copied byte-for-byte with a PDF mime type and there is no PDF-to-text code anywhere, so the caller must supply PDF text or rely on the agent's own reading.

**D2 does not** (evidence). The configuration schema's strictness, with the fixed six-string checklist.

```
        max_files_changed_per_ingest: z.number().int().positive(),
      })
      .strict(),
  })
  .strict()
```

Nothing in the body accepts a caller-supplied field list. The workspace configuration is validated by a strict schema whose only sections are version, workspace, runtime, OKF, agents, paths and safety, so an extra key fails as invalid; the ingest plan emits a fixed checklist and a fixed reference path; and the reference page shape is a convention from fixtures rather than a template the tool reads. The only place a project could inject charting fields is user prose outside the managed block of the instruction file, which is the caller's mechanism rather than the tool's.

**D3 partial** (evidence). The lint's index-entry warning, with the removal of the log from the concept scan and the ingest checklist's contradiction line.

```
      {
        code: MISSING_INDEX_ENTRY,
        severity: "warning",
        path: file.workspacePath,
        message: `Concept is not linked from a root or directory index: ${file.workspacePath}`,
```

Cross-source synthesis pages exist as topic, entity, project, decision and question concept documents with a citations section pointing at reference pages, and `okfh init` scaffolds a wiki index plus per-folder indexes, with missing-index-entry and broken-link lint keeping the index honest. The append-only log is explicitly removed: the code comment says the log file is no longer scaffolded and stays reserved so a leftover file in an older workspace is ignored, and the CLI documentation says a log is not part of a workspace and is not a read target. History is instead git-backed through checkpoint, history and restore, plus two append-only machine ledgers that record registrations and revision acknowledgements rather than wiki edits. Contradictions are prose: an architecture decision record says the harness should not decide which claim is correct and the ingest checklist says to preserve uncertainty and contradictions, but the stop contract routes an unresolved contradiction to the user for adjudication, and one workflow describes an ingest that resolved a contradiction against a page. Nothing flags a contradiction in a page or ledger, and nothing prevents deleting one side.

**D4 covers** (evidence). The source command's register verb against the ingest command's plan verb, with the resolved-path copy and the create-only write.

```
    .command("source <action> [input] [revision]")
    .description("Register, list, and reconcile OKF Harness raw sources.")
```

Ingest and integrate are separate verbs and separate modules: `okfh source add <path>` accepts any local file path, hashes it, copies it into a dated raw path and appends a manifest row, while `okfh ingest plan <src_id>` later plans the digest from manifest metadata only, which the shipped test demonstrates by writing a source body the plan never reads. A note written by another process is therefore consumed without the harness creating it, always through an immutable copy; alternatively another process may write the raw file and the manifest row itself, since the row schema is enforced by a parser and the shipped example workspace is exactly such a hand-authored manifest.

**D5 partial** (evidence). The registration path's hash lookup, confirmed by the reconciliation test.

```
  const contents = await readFile(sourcePath);
  const sha256 = sha256Hex(contents);
  const existing = context.manifest.entries.find(
    (entry) => entry.kind === "file" && entry.sha256 === sha256,
  );
  if (existing !== undefined) {
    return {
      workspaceRoot: context.workspaceRoot,
      input: context.input,
      action: "reused",
```

Registration is idempotent by content hash regardless of filename: an unchanged file returns a reused action and writes nothing. The digest step, however, has no hash-keyed already-integrated check: the manifest's optional reference-concept field is parsed and echoed by the evidence command but never written by the add verb, and the fixture frontmatter's source-hash key is read by no code. Whether the reference page already reflects that hash is left to the agent's judgement under the checklist. Drift the other way is detected: a source-hash-drift lint fires if a registered raw copy's bytes change.

**D6 covers** (evidence). The plugin manifest, with the root marketplace manifest and the README install line.

```
{
  "name": "okf-harness",
  "displayName": "OKF Harness",
  "version": "0.8.1",
  "description": "Adds the unified okf-harness skill for workspace setup and daily maintenance through the pinned runtime launcher.",
  "author": {
    "name": "Eric Zhou"
  },
  "homepage": "https://github.com/pumblus/okf-harness#readme",
  "repository": "https://github.com/pumblus/okf-harness",
  "license": "Apache-2.0",
  "keywords": ["okf", "llm-wiki", "agent-skills", "claude-code"],
  "skills": "./skills/"
}
```

A Claude Code plugin with a marketplace manifest at the repository root and one skill with reference files. The skill does no work itself: every route shells to a floating setup package that launches the pinned CLI, so installation as-is additionally requires Node 22 or newer and npm network access on first run. Codex compatibility, recorded separately, is first-class: a second artifact conforming to the Agent Plugins standard with an OpenAI extension, installed through a Codex marketplace command and documented as verified end to end on a named Codex CLI version, plus workspace-local adapters written by `okfh init --agents codex|claude|all` that place a skill under the agents skills path and a managed block in `AGENTS.md`.

**D7 covers** (evidence). The scaffolded directory list, with the configurable paths and the wiki-root refinement.

```
  return [
    ".agents/skills",
    ".claude/skills",
    ".codex",
    ".okfh/cache",
    ".okfh/reports",
    "raw/assets",
    "raw/inbox",
    "raw/sources",
    "wiki/decisions",
    "wiki/entities",
    "wiki/projects",
    "wiki/questions",
    "wiki/references",
    "wiki/topics",
  ];
```

Satisfies the second branch: layout requirements are explicit in code and documentation, a configuration file sits at the workspace root, and the raw and wiki paths plus the manifest path are configurable, with a refinement requiring the wiki root to match the OKF bundle root. It does not work on an existing vault in place: `okfh init` refuses a non-empty directory and the skill forbids it, and every markdown file under the wiki root lacking frontmatter with a type is an OKF conformance error that makes the check command return blocked. The paths are configurable in principle, but the ingest module hard-codes the references and topics directories and the concept-id helper strips a literal wiki prefix, so a non-standard bundle root is only partly honoured.

**D8 does not** (evidence). The source-id pattern, enforced by the manifest parser and minted by the id generator.

```
const SOURCE_ID_PATTERN = /^src_\d{8}_\d{4}$/;
```

Source ids are minted by the tool in a fixed dated form and any other id in a manifest row is rejected as invalid, so a citekey cannot be the stable id. All provenance markers use that id: the reference frontmatter's source id, bare ids in the citations section, and the source ids in the evidence brief. The workaround within the tool is that the manifest title is the input filename stem and the recommended reference path is a slug of that title, so naming the captured note by citekey yields a citekey-slugged page filename and title while ids and citations still use the minted ids. The free notes field is parsed and never written by the CLI.

**D9 partial** (claim). The ingest workflow reference's file-count ceiling, with the stop contract and the source add dry run.

```
- If the planned or actual wiki edit would exceed `max_files_changed_per_ingest` from `okfh.config.yaml`, stop and ask the user before editing more files. This limit is agent-enforced guidance; the CLI does not enforce it yet.
```

The only pre-integration gate is prose: a per-ingest file-count ceiling the agent is told to honour, plus a stop contract that actually restricts stopping, since a stop is permitted only when the information needed to decide safely exists solely in the user's head. The plugin skill requires a confirmation only before setup writes, not before wiki edits, and the dry run exists for source add and init rather than ingest. No per-source versus batch review mode is documented. What the tool does provide is after-the-fact review: checkpoint, history and restore let a human undo a completed cycle.

**D10 covers** (evidence). The licence header, with the copyright line and the manifest and frontmatter declarations.

```
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/
```

Apache-2.0 permits use, modification and redistribution subject to notice retention and marking of modified files. The licence is declared consistently in the licence file, the root package, every workspace package, both plugin manifests and every skill frontmatter; there is no contributor agreement and no notice file.

**Treatment opinion: copy plus a delta.** Two floor requirements fall short from the body: D2 is does-not (no caller-supplied charting template; a strict configuration schema and a fixed checklist) and D3 is partial (an index yes, but the append-only log is deliberately removed in favour of git checkpoints, and contradiction handling is prose only). D8 is blocked outright by the source-id pattern enforced on every manifest row, so a citekey cannot be the identity. Install-as-is is therefore excluded. Forking is disproportionate: the runtime is a four-package TypeScript monorepo whose Claude plugin resolves a floating setup package and a pinned CLI from npm at every invocation, so a fork must republish packages or rewrite the skill's launcher lines, and the id pattern plus the literal wiki paths sit in the core. What transfers cleanly is the markdown: the ingest, reconcile and answer workflow references (register, plan, agent reads the source, bounded edits, check, record the judgement), the reference page shape with its summary, key points and citations, the SHA-256 manifest with reused-on-same-hash and same-filename revision edges, and the lint vocabulary. Copy those files, replace the tool's verbs with the vault's own, add the missing pieces (per-project charting fields, citekey ids, an append-only log, contradiction flags), and credit the author and project under Apache-2.0 with the required notice.

**Facts carried from this body.** Codex CLI natively reads Agent Plugins standard manifests, and the repository records an end-to-end verification against a named Codex CLI version: the install identifier held, the skill reached the model-visible list, the storefront fields survived byte for byte, and removal restored the environment. The wiki bundle format is Google's Open Knowledge Format specification and the workflow follows Karpathy's gist pattern. The Claude Code skill frontmatter keys this plugin relies on are name, description, licence, compatibility and a nested metadata map. The managed-block convention for a shared instruction file uses HTML comment markers so user prose survives upgrades. The project's stated posture on Obsidian is documentation-first, with no runtime dependency or plugin on the default path.

### 17. skyllwt/AutoSci (ΩmegaWiki)

Discovered through the digest sweep. `https://github.com/skyllwt/AutoSci`. Pin `e02cb3b766597c4fc345f653513c56d21b6f7ef5` (main HEAD, committed 2026-08-30T01:01:31Z). Kind: a vault template with agent instructions, that is 25 project-scoped Claude Code skills over a Python wiki runtime with a YAML entity, edge and cross-reference schema, a schema-access loader, a structural linter and a wiki CLI. No plugin manifest; the repository is the vault.

**Maintenance.** Last push 2026-08-30; 1,660 stars; six contributors; tags v1.0.0 and an arXiv tag; no GitHub releases; the changelog's last entry is 1.4.0 dated 2026-05-18, three months before the pinned commit, so recent changes are traceable only through the git log. A status badge reads internal beta.

**Originator and supplier.** The licence names "OmegaWiki Contributors" as copyright holder; the README citation names a Peking University group; the supplier is the GitHub repository, which also distributes Codex and OpenCode adaptation branches.

**Licence.** MIT, found, at `LICENSE` lines 1-9.

```
MIT License

Copyright (c) 2026 OmegaWiki Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software
```

IP assertions: no contributor agreement in the contributing guide, and only the notice-retention condition. The README asks users to cite an arXiv paper, which is a request rather than a licence condition. The copyright holder's name differs from the GitHub owner and from the paper's author list, and there are no per-file copyright headers. One skill directory is stated to be adapted from a third-party project, which is a third-party origin for that skill; its licence was not chased.

**Verify.** Licence confirmed at the pin: the standard 21-line MIT text with the recorded copyright line, and the API SPDX id agrees; the cited line range is off by one at the end, which is not a defect. The contributor-agreement absence was not re-checked. Pin confirmed: SHA and committer date match, as do the push date and star count. Two rows re-checked, none refuted.

**Smallest part.** The runtime contract module: the entity schema YAML (a per-kind frontmatter field list with type, requiredness, default, enum and range), the paper body template, and the field-derivation block of the loader that reads the YAML and derives the required-field and valid-value maps. It stands without any skill: a caller edits YAML to define the charting fields and the linter validates pages against it. Two other detachable pieces: the append-log helper (15 lines) plus the git merge-union attributes for the log, index and JSONL accumulators, and the deduplication policy reference with its similarity thresholds and per-paper creation caps.

**Fitting.** *Inputs:* one source per invocation, that is an arXiv URL, a local TeX file, a local PDF, or a canonical path handed over by the init skill through a checkpoint manifest. Local PDFs are first normalised by a preparation script into a prepared TeX file under a temporary raw directory. The skills read the index and the existing pages for deduplication and placement. Optional network enrichment through Semantic Scholar, a preprint brief service and arXiv, with keys from an environment file. *Outputs:* a paper page with frontmatter per the entity schema plus eight body sections; created or edited concept, method and people pages; edits to topic pages; appended JSON lines in the graph edge and citation files with required confidence and evidence; appended YAML entries in the index; an appended dated log line naming the skill and the changed pages; rebuilt derived pages for the context brief and open questions; optional canvas files; and a terminal summary. Side effects on the source tree are sidecars under a temporary raw directory and downloads under a discovered directory. *Invocation:* in Claude Code from the repository root, an ingest command with optional discover and visualize flags; a batch init that fans out one ingest per paper in isolated git worktrees and merges at fan-in; a scheduled arXiv command and a GitHub Actions workflow; and deterministic helpers invoked as Python scripts for slug generation, edge and citation writing, index and derived-page rebuilds, and the linter. *Harnesses:* Claude Code, as project-scoped skills synced from an internationalisation tree by a setup script, plus a project instruction file and an MCP server for an optional review model. Codex and OpenCode are separate branches; this pinned tree has no agents directory. Obsidian is a consumer only, through an optional graph configuration and canvas output.

**Surplus.** A full idea and experiment research lifecycle with two entity kinds, lifecycle transition maps and eight skills, whose required fields a digest-only vault would have to delete from the schema; a publication pipeline of seven skills plus a LaTeX toolchain; outbound enrichment and discovery through four services plus a scheduled workflow and an email sender, which needs keys and network on the ingest path and hardwires an arXiv worldview into the per-source fields; a typed knowledge graph with fourteen edge types requiring confidence and evidence, helpful for the contradiction story and a second store to keep consistent; a single-page web application of eleven modules with its own server, plus canvas generation; a bundled MCP review server needing a second model provider; and a bilingual duplication in which every skill exists three times, so any local edit must be mirrored or abandoned.

**Coverage.**

**D1 partial** (claim). The ingest skill's source list and its one-sentence summary field, with the PDF text extractor.

```
`source`: one of — arXiv URL (e.g. `https://arxiv.org/abs/2106.09685`), local `.tex`, local `.pdf`, or a `canonical_ingest_path` handed off by `/init` via `.checkpoints/init-sources.json`(see `references/init-mode.md`) | `tldr` — one-sentence summary of the paper, suitable as a search/preview line. NOT a multi-paragraph abstract; one sentence. | Body sections to populate, in this order: `Problem & Context`, `Key idea`, `Method`, `Experiment & Results`, `Limitations`, `Open questions`, `My take`, `Related`. | ## Problem & Context

## Key idea

## Method

## Experiment & Results

## Limitations

## Open questions

## My take

## Related | doc = fitz.open(path)
        try:
            text_parts = [page.get_text("text") for page in doc]
```

A shipped per-source page skeleton exists and the schema supplies the summary field, with key points landing in the fixed body sections and PDF-to-text handled by a shipped local extractor that produces a synthetic TeX file. The page itself is written by the model following the skill: no script renders the template (a grep for the template extension across the tools and runtime finds nothing), and the paper directory ships only a placeholder, so there is no worked example.

**D2 covers** (evidence). The entity schema's papers block, with the runtime contract's own claim, the loader's derivation and the linter's consumption.

```
papers:
  dir: wiki/papers/
  fields:
    title:             { type: str, required: true } | Every change below is **YAML-only, zero Python change**.  Edit, save, done. | - **New field on an entity** — add it under that entity's `fields:` block with
  `type` + optional `required` / `default` / `range` / `values` / `to`. | REQUIRED_FIELDS = {
    kind: [n for n, f in e['fields'].items() if f.get('required')]
    for kind, e in ENTITIES.items()
} | Open `runtime/schema/entities.yaml` (papers section) for the field set and `runtime/templates/papers.md.tmpl` for body section order. Fill every required frontmatter field
```

**This row is the run's only D2 cover, and the re-read below downgrades it.** As originally scored: the per-source field list is a project-owned YAML schema with per-field type, requiredness, default, enum and range, and shipped code derives the required-field and valid-value maps from it while the linter validates pages against them, so the caller controls the field list without touching Python. The caveats recorded even in the original row are that the fields ship as bibliographic metadata rather than charting fields, that values land in YAML frontmatter rather than a body charting table, and that the ingest-time fill is LLM prose. See section 18 for what a second read of the same three files established.

**D3 partial** (evidence). The append-log helper, with the index rebuild, the append-only convention, the git merge attribute, the challenge and critique edges, the check skill's detector and the concept template.

```
def append_log(wiki_root: str, message: str) -> None:
    """Append a timestamped entry to log.md.
```

Cross-source concept pages, an index rebuilt from frontmatter and an append-only log opened in append mode with a declared convention and a git merge-union attribute are all shipped. Contradictions are representable: a paper-to-paper challenge edge and a paper-to-concept critique edge both require confidence and evidence, the edge writer rejects writes without them, edges land append-only in a JSONL file, and the check skill lists contradictory-statement detection under report-only behaviour. The caveat worth carrying is that nothing states a never-delete rule as policy, and the deduplication reference instructs merging near-duplicate concepts, which can silently absorb one side of a disagreement.

**D4 covers** (evidence). The conventions file's ownership block, with the ingest skill's read-only rule and the init skill's raw scan.

```
ownership:
  user_owned:  [raw/papers, raw/notes, raw/web]   # skills must not overwrite
  tools_only:  [wiki/graph]                       # only via tools/research_wiki.py
  append_only: [wiki/log.md]                      # never rewritten in place
```

Capture and digest are separate by contract and by input shape: the digest consumes a path it did not create, the raw directories are declared user-owned and read-only, and the init mode forbids any raw write. Notes written by another process are first-class inputs to init. The caveat is that for a direct PDF the pipeline writes derived sidecars under a temporary raw directory, though never into the user-owned trees.

**D5 partial** (claim). The ingest error-handling reference's already-ingested branch.

```
- the paper is already ingested (slug + arXiv ID match an existing page)
```

Re-ingest is short-circuited by identity rather than by content: the skill says to stop if the page already exists and the arXiv identifier or title matches. There is no content hash anywhere (a grep for the usual hashing names across the checkout returns zero hits). The consequences run both ways: an unchanged source is a no-op only because the page already exists, and a changed source under the same title or identifier is also skipped. The guard is prose in a skill rather than code.

**D6 covers** (evidence). The setup script's skill copy, with the skill frontmatter and the contributing note.

```
cp "$I18N_DIR/CLAUDE.md" CLAUDE.md
for src in "$I18N_DIR/skills"/*/SKILL.md; do | cp -R "$skill_dir"/. ".claude/skills/$name/" | description: Ingest a paper into the wiki — creates pages (papers + concepts + methods + people) and builds all cross-references and graph edges. Trigger whenever the user says "ingest", "add this paper", drops a `.pdf` / `.tex` / arXiv URL, or asks to fold a paper into the knowledge base.
argument-hint: <local-path-or-arXiv-URL> [--discover] [--visualize] | Do **NOT** create a `src/` Python package. This is a Claude Code skill project, not a pip-installable library. | **Pre-condition**: working directory contains `wiki/`, `raw/`, and `tools/`.
```

Runs as 25 project-local Claude Code skills installed as-is by cloning the repository and running its setup script. It is not a plugin and cannot be dropped into an existing project: every skill hard-depends on the tools, runtime, wiki and raw directories, so as-is means adopting the repository as the vault. Codex compatibility, recorded separately, is not in this branch's body: the README points at a separate Codex preview branch using an agents skills directory, and this pinned tree contains no such directory.

**D7 covers** (evidence). The conventions file's path pattern and the layout tree in the schema template, with the wiki root as a positional argument.

```
path_pattern: "wiki/{kind}/{slug}.md"
```

Satisfies the second branch: the layout is fixed and stated explicitly, with a per-kind directory set created by the init verb, a graph directory, index and log files, and a raw tree of six genres. The wiki root is a positional argument, but the subdirectory names come from the entity-kind keys rather than from the schema's per-kind directory values. One documentation drift worth noting: the directory-structure document lists a runtime schema file at the wiki root that is absent from the tree.

**D8 does not** (evidence). The slug generator's docstring and cap, with the skill's never-hand-craft rule and the frozen-after-first-write policy.

```
"""Generate a kebab-case slug from a paper/concept title. | # Cap at 6 keywords to keep slugs manageable
    return "-".join(keywords[:6]) | - Slugs always come from `tools/research_wiki.py slug`. Never hand-craft. | papers.slug:              { writers: [ingest], frozen_after_first_write: true } | arxiv:             { type: str } | s2_id:             { type: str }
```

Page identifiers are title-derived slugs computed by the tool, mandated by the skill and frozen after the first write; provenance in the graph files uses those slugs as node ids, and the identity fields are arXiv and Semantic Scholar ids. There is no field or flag for a caller-supplied stable identifier such as a citekey, and no mention of Zotero or citekeys anywhere in the digest path.

**D9 partial** (claim). The scheduled skill's mode flag and its policy reference, with the discover prohibition and the check skill's report-only default.

```
- `--mode inform|auto-ingest`: default `inform`. Never infer `auto-ingest` from repo state. | - `inform`: default. Produce digest, e-mail when configured, and stop.
- `auto-ingest`: explicit opt-in. Only `decision: ingest` with
  `confidence: high` can proceed, and only up to `max_auto_ingest`. | Do not auto-ingest anything from the shortlist — the user picks. | - **Report-only by default**: without `--fix`, only reports, no modifications
- **`--fix` only repairs deterministic issues**: xref reverse-link completion, missing fields filled with safe default values. Non-deterministic issues output recommendations (`--suggest`) for user approval | if [ "$DAILY_ARXIV_MODE" = "auto-ingest" ] && [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$CLAUDE_CODE_OAUTH_TOKEN" ]; then
```

A batch review gate is documented: the scheduled skill defaults to inform, auto-ingest is an explicit opt-in capped and confidence-gated, discover never ingests, and the check skill offers a dry run and a suggest mode for user approval. However the gate sits at the selection stage: a direct ingest writes the paper page, entity pages, edges, index and log immediately with no preview or approval step, and there is no per-source review toggle. So per batch is documented and per source is not.

**D10 covers** (evidence). The licence file with its grant clause.

```
MIT License

Copyright (c) 2026 OmegaWiki Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software
```

MIT permits use and modification subject to retaining the notice.

**C1 does not** (evidence). The ingest skill's source list, with the external API list.

```
`source`: one of — arXiv URL (e.g. `https://arxiv.org/abs/2106.09685`), local `.tex`, local `.pdf`, or a `canonical_ingest_path` handed off by `/init` via `.checkpoints/init-sources.json`(see `references/init-mode.md`) | ### External APIs

- Semantic Scholar (via `tools/fetch_s2.py`)
- DeepXiv (via `tools/fetch_deepxiv.py`, optional; graceful fallback)
- arXiv (source download)
```

Included to make the lane explicit: nothing reads a local Zotero (no localhost port, no Better BibTeX). Sources are files or arXiv, and enrichment is over the network.

**C4 partial** (evidence). The PDF text extractor, with the Semantic Scholar import, the arXiv source download, the vision fallback and the dependency pin.

```
doc = fitz.open(path)
        try:
            text_parts = [page.get_text("text") for page in doc]
```

PDF-to-text is genuinely local, with a graceful degradation path when the library is absent. Partial rather than covers because there is no attachment concept (the input is a filesystem path the user placed under the raw tree), and because the enclosing preparation flow is not offline: it calls Semantic Scholar when a title is supplied, downloads arXiv source when an identifier is found, and documents a vision-API fallback for title recovery.

**C5 covers** (evidence). The linter's argument parser, with the Python-binary preference order and the Obsidian note.

```
parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", required=True)
    parser.add_argument("--source", required=True)
```

Every mechanical operation is a plain Python CLI and the skills run inside the agent; Obsidian appears only as an optional visualization target that nothing in the ingest path depends on. Auto-ingest in CI is gated to the Claude Code runtime, so headless from an agent holds while headless from a bare script without an LLM does not for the digest step itself.

**Treatment opinion: copy plus a delta.** Install-as-is or fork would import a whole-repository research platform (25 skills, a large tools tree, a fixed vault layout, network enrichment on every ingest) whose identifiers are title-derived slugs, whose digest input excludes markdown notes, and whose layout is fixed. The pieces that fit are small, self-contained and MIT: the runtime contract (a YAML field schema plus a body template plus loader-derived validation), the append-log and merge-union append-only pattern, the challenge and critique edge shape with required confidence and evidence, and the deduplication thresholds and per-source creation caps. Copying those with a delta (citekey as the stable id in slugs and edge node ids, markdown literature notes as an accepted source, caller-chosen directory names, and a per-source review gate) obtains the D2, D3 and D7 mechanisms without the platform. Author-and-credit would also work but discards working code for no gain. This opinion is about this candidate alone and implies no ranking.

### 18. AutoSci runtime schema contract, second read

The critic pass named this as the cheapest and first re-read to run, because AutoSci's D2 cover was the run's only one and its verification block had not checked that row. This is a second record against the same repository at the same pin, scoped to `runtime/schema/entities.yaml` with `runtime/loader.py` and `tools/lint.py`. Everything in section 17 about maintenance, licence, originator and supplier applies unchanged.

**Licence.** MIT, found, at `LICENSE` lines 1-9, as above; there is no SPDX header in the loader, the linter or the entity schema, so the licence file is the only notice. Standard MIT notice retention is the only condition. Supplier and originator diverge in naming: the repository owner against the "OmegaWiki Contributors" copyright line, with the codebase still calling itself by the older name internally.

**Verify.** Licence confirmed at the pin (the full FSF-style MIT text with the recorded copyright line, corroborated by the API SPDX id). Pin confirmed: SHA and committer date match, and the repository push date and star count agree. Four rows re-checked, none refuted.

**Smallest part.** The entity schema YAML, 183 lines, self-contained, one block per entity kind with a directory, a field list, optional lifecycle and terminal markers, and an 18-line header comment defining the field-attribute vocabulary, taken together with about 60 lines of the loader (the schema read and the comprehensions that derive the entity directories, the required fields, the valid values and the field defaults). That pair is liftable with a YAML library as its only dependency. Deliberately excluded: the 1,170-line linter, which imports eighteen loader symbols and carries a hard-coded validation table, and the skills tree, each of whose files assumes the wiki, raw and tools directories and a project virtual environment. The body template alone is even smaller but inert, because no code renders it.

**Coverage.** The rows below re-score the three requirements the critic named, plus the rest of the set against this narrower body.

**D1 covers** (evidence). The paper body template, whole file.

```
---
{{ frontmatter }}
---

## Problem & Context

## Key idea

## Method

## Experiment & Results

## Limitations

## Open questions

## My take

## Related
```

A shipped per-source page skeleton, with the summary field supplied by the schema and described in the skill as a one-sentence search or preview line, and key points landing in the fixed body sections. Input is a PDF, TeX or arXiv URL. The page is written by the agent following the skill rather than by a renderer, and the shipped papers directory contains only a placeholder.

**D2 partial** (evidence). The linter's hard-coded value-check table, against the schema's data-driven field list and the loader's derivations.

```
        enum_checks = {
            "papers": [("importance", "papers.importance")],
            "concepts": [("maturity", "concepts.maturity")],
            "ideas": [("status", "ideas.status"), ("priority", "ideas.priority")],
            "experiments": [("status", "experiments.status"), ("outcome", "experiments.outcome")],
            "methods": [("type", "methods.type")],
            "foundations": [("status", "foundations.status")],
        }
```

**This is the finding the re-read was run for: the original covers does not verify, and the row drops to partial.** Half of D2 verifies and half does not. What verifies is that the field list is data rather than code: the schema declares each kind with a directory and a field block, and the loader derives everything by comprehension, with its own module docstring claiming that adding an entity or field in YAML propagates without any code change. A caller could replace the papers field list with population, concept, context, design, findings and a page locator, and the required-field, default and valid-value maps plus the required-field lint check would follow. What does not verify, three ways. First, value validation is a hard-coded per-kind table, quoted above, plus a hard-coded range check for one kind, so a caller-added enum field gets a valid-value entry from the loader and is never checked by the linter, which directly falsifies the runtime contract's own promise of YAML-only, zero-Python change for its new-field case. Second, there is no caller-facing supply mechanism: the schema path is resolved relative to the loader file, with no flag, environment variable or configuration override, and the linter's arguments offer only a wiki directory, JSON output, fix, dry-run and suggest, so per project means per fork of the tool's own shipped file. Third, the fill path is prose that hard-codes the shipped fields: the ingest skill names three frontmatter fields to populate, one of them drawn from a closed set, and re-lists the body sections in prose, so swapping the charting field list means editing the skill too. The only code that scaffolds schema fields into a page is the linter's default filler, which fills declared defaults and never charted content.

**D3 covers** (evidence). The append-log function, with the index rebuild, the open-questions rebuild sources, the append-only convention, the merge attribute and the edge definitions.

```
def append_log(wiki_root: str, message: str) -> None:
    """Append a timestamped entry to log.md.
```

All three parts are present as shipped artifacts. Cross-source synthesis pages: the schema declares a concepts kind with a required key-papers link list and a summary kind with scope and key topics; the concept template ships variants, comparison and known-limitations sections; and derived synthesis is regenerated by a rebuild function whose docstring names the three source sections it reads. Index: the wiki index ships with one heading per entity kind and is regenerated by a function exposed as a CLI subcommand. Append-only log: the conventions file declares the log append-only, the log grammar is declared, and the code opens the file in append mode. Contradictions kept and flagged: the edge schema declares a paper-to-paper challenge edge and a generic contradicts edge, both requiring confidence and evidence; edges land append-only in a JSONL file; and the check skill lists contradictory-statement detection under report-only behaviour. The caveats are that no rule states never delete one side, and that the generic contradicts edge is rejected on new paper-to-paper writes because the loader marks it legacy.

**D4 covers** (evidence). The conventions file's ownership block, with the ingest and init skills' rules and the shipped drop-zones.

```
ownership:
  user_owned:  [raw/papers, raw/notes, raw/web]   # skills must not overwrite
  tools_only:  [wiki/graph]                       # only via tools/research_wiki.py
  append_only: [wiki/log.md]                      # never rewritten in place
```

The digest step consumes a path it did not create, the raw directories are user-owned and read-only, the init mode forbids any raw write, and notes written by another process are first-class inputs to init, whose skill explicitly handles empty notes and web directories. The repository ships the drop-zones as tracked empty directories.

**D5 partial** (claim). The ingest error-handling reference, against the absence of hashing.

```
- the paper is already ingested (slug + arXiv ID match an existing page)
```

Re-ingest is short-circuited by identity rather than content: the skill stops if the page exists and the identifier or title matches. A grep for content hashing across the checkout returns zero hits. So an unchanged source is a no-op only incidentally, a changed source under the same title is also skipped, and the guard is skill prose with nothing in the tools enforcing it.

**D6 covers** (evidence). The setup script's skill copy with the skill frontmatter and the pre-condition.

```
cp "$I18N_DIR/CLAUDE.md" CLAUDE.md
for src in "$I18N_DIR/skills"/*/SKILL.md; do
```

Genuine Claude Code project-scope skills with valid frontmatter, plus an MCP server declaration and a bootstrap script that checks prerequisites, creates a virtual environment and copies configuration templates. There is no plugin manifest at the repository root, so the unit of installation is the whole repository cloned as the vault rather than a skill dropped into an existing project, and every skill hard-codes repository-relative tooling. Codex compatibility, recorded separately: not in this branch, which contains no agents directory; the README points at a Codex preview branch that regenerates an agents skills tree from the same sources.

**D7 covers** (evidence). The conventions file's path pattern and wikilink syntax.

```
# Where an entity page lives, given its kind and slug.
path_pattern: "wiki/{kind}/{slug}.md"

# How wikilinks resolve.  `[[slug]]` matches by trying each entity dir until a
# `{slug}.md` file is found.
wikilink_syntax: "[[slug]]"
```

Covered on the states-its-layout branch: the layout is declared rather than implied, through per-entity directory keys, the path pattern and wikilink syntax, an edge-storage default, shipped index and log files, and a directory-structure document. The caller-chosen-layout branch is weaker: the linter takes a wiki directory so the vault root moves, but subdirectory names are re-hard-coded in the derived-page code, and wikilinks are bare slugs with no folder segment, so an Obsidian vault with its own scheme would need the entity directories renamed in the schema and those call sites edited.

**D8 does not** (evidence). The conventions file's slug rule, with the generator subcommand, the skill's invocation and the frozen-after-first-write policy.

```
slug_rule: "^[a-z0-9]+(-[a-z0-9]+)*$"
```

The stable identifier is generated by the tool from the title rather than supplied by the caller, and page links and cross-reference actions use that slug, which is declared identity-critical and frozen after the first write. Nothing accepts a caller-supplied id: a grep for citekey, citation key and BibTeX over the checkout finds BibTeX only in the LaTeX drafting skills, never as a page key. A lowercase citekey would pass the slug rule, but only if the caller bypassed the generation step by hand.

**D9 does not** (claim). The check skill's fix policy, against the ingest workflow's uninterrupted writes.

```
- **`--fix` only repairs deterministic issues**: xref reverse-link completion, missing fields filled with safe default values. Non-deterministic issues output recommendations (`--suggest`) for user approval
```

The only documented approval gates sit downstream of integration or outside it. The ingest workflow's seven steps write the paper page, concept, method and people pages, the index and graph edges with no pause; the closest thing to a gate on that path is a discovery guardrail stating that suggestions are never auto-ingested. The quoted line gates the linter's non-deterministic fixes rather than source integration. The other approval prompts found are a setup confirmation before writing an environment file and an init stop on a detached git head. No per-source versus batch setting exists, and no configuration key controls one.

**D10 covers** (evidence). The licence grant.

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software
```

MIT: use and modification are permitted, subject only to notice retention. Copying the schema and the loader derivation block into another repository is licensed with the copyright line preserved.

**C1 does not** (evidence). The ingest skill's source list.

```
- `source`: one of — arXiv URL (e.g. `https://arxiv.org/abs/2106.09685`), local `.tex`, local `.pdf`, or a `canonical_ingest_path` handed off by `/init` via `.checkpoints/init-sources.json`(see `references/init-mode.md`)
```

No Zotero anywhere: a grep over the whole checkout returns zero hits, and there is no local-API or JSON-RPC client under the tools directory. The source of record is the filesystem plus arXiv and Semantic Scholar HTTP APIs.

**C2 partial** (evidence). The write-permission policy's own status header.

```
# STATUS: SPEC, NOT A RUNTIME GATE.
# Nothing in tools/ or .claude/skills/ reads this file at write time. It is a
# declarative contract for SKILL.md authors and for Claude when reading the
# repo's rules — "this is who is supposed to write this."
```

Plausibly relevant because the candidate does emit markdown notes with a machine region and a human region: YAML frontmatter is the managed region and the templates reserve free sections for the human, with field-level ownership even declared. It falls short twice: the note is keyed by a tool-generated slug rather than a citekey, and the managed and free split is unenforced by construction, as the quoted header says outright, adding that the frozen-after-first-write marker is also a specification marker rather than a hard lock. No begin and end region markers exist in the templates, so a regenerating writer has nothing mechanical to respect.

**C3 does not** (evidence). The papers field block, which carries no version, tag or modification-time field.

```
arxiv:             { type: str }
```

There is no upstream-change detection of any kind: no item version, no since cursor, no modification-date comparison and no content hash. The only per-item date fields are locally authored. Wiki-internal orphan detection does exist in the linter, but that is a different question.

**C4 partial** (evidence). The PDF text extractor with its dependency guard.

```
        doc = fitz.open(path)
        try:
            text_parts = [page.get_text("text") for page in doc]
        finally:
            doc.close()
```

PDF-to-text is genuinely local and cloud-free, with a graceful degradation path. Partial because there is no attachment concept, the input being a filesystem path the user placed under the raw tree, and because the surrounding preprocessing is not offline: the same module fetches arXiv source and calls Semantic Scholar, and the preprocessing reference asks the agent itself to open the PDF for title recovery before any tool runs.

**C5 covers** (evidence). The linter's usage docstring, mirrored in the check skill.

```
Usage:
    python3 tools/lint.py                      # lint wiki/ in current dir
    python3 tools/lint.py --wiki-dir wiki/     # specify wiki directory
    python3 tools/lint.py --json               # output as JSON
```

Every mechanical operation is a plain Python CLI runnable from a shell with no editor attached, and Obsidian is not a dependency anywhere in the body; the optional viewer is a self-hosted application served by a script. The page-authoring step itself needs an agent harness rather than a bare script, which is consistent with the requirement's CLI-or-agent wording.

**C7 partial** (claim). The citation-verification reference's rule.

```
**BibTeX entries must come from authoritative sources, not from LLM memory.**
```

Not Zotero-side enrichment, since there is no Zotero plugin here, but the candidate does ship overlapping capability worth recording so a vault does not replicate it: Semantic Scholar metadata and citation counts, arXiv source and identifier resolution, a preprint brief service, Wikipedia backgrounding, citation-key verification with an explicit unconfirmed prefix convention, and a structural metadata linter. There is no DOI verification, no PMCID lookup and no arXiv version-update check, and none of it writes back to a reference manager.

**Treatment opinion: copy plus a delta.** The liftable asset is small, licensed and good: a YAML entity contract plus about sixty lines of comprehension-based loader that turn a field list into required-field, default, enum-range and link-target knowledge with no code generation, and MIT permits copying it outright with the notice. Copy-plus-delta rather than install-as-is, because installing as-is means adopting the repository as the vault, with 25 skills, a LaTeX publication pipeline, an idea and experiment lifecycle the schema makes mandatory, a single-page application, an MCP server and a trilingual skill tree, and because the two halves this set needs are the two that do not transfer clean: the fill path is prose that hard-codes the shipped field names, and value validation is the hard-coded table quoted in the D2 row. The delta is therefore concrete and known in advance: replace the papers field block with the caller's charting fields; make the value check iterate the entity schema rather than the literal dictionary, a change of about ten lines that also makes the repository's own YAML-only claim true; key pages by a caller-supplied citekey instead of the generated slug; and write the filler. A fork was not chosen because nothing upstream needs tracking once the schema pattern is copied, and author-and-credit is the honest fallback if only the pattern rather than the file is taken.

**Facts carried from this body.** The schema layer states that adding entities or fields is a YAML-only change requiring no Python edit, a claim this candidate's own linter partly contradicts through the hard-coded value-check table. The field and edge write-ownership file is explicitly documentation rather than enforcement, so any managed-region guarantee in this ecosystem is prompt-level only. Codex support exists only on a separate branch that regenerates an agents skills tree from the same internationalisation sources; the Claude Code tree pinned here contains no agents directory.

### 19. ar9av/obsidian-wiki

Discovered through the digest sweep; the strongest mechanism evidence in the field for hash idempotency and staged writes. `https://github.com/ar9av/obsidian-wiki`. Pin `f268d437442a551e4121aa1b7dd680ef987a8d50` (HEAD of main, committed 2026-09-03T11:09:35Z). Kind: an agent-skills tree (skill directories symlinked into six agent skill paths) plus a standard-library Python CLI published on PyPI. **Not** a Claude Code plugin: no plugin directory exists at the pin, confirmed by a tree listing.

**Maintenance.** Last push 2026-09-03 (the pinned commit); 3,350 stars; created 2026-04-05; CI workflows for tests, publishing, Docker, setup and README sync; 40 test modules. Development is active and disciplined but its centre of gravity is not the digest skill.

**Originator and supplier.** Ar9av, both, with the pattern credited in-body to Karpathy's gist. One vendored subtree carries a different licence and no named holder.

**Licence.** MIT, found, at `LICENSE` lines 1-21 with the package manifest.

```
MIT License

Copyright (c) 2026 Ar9av

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND [...]
```

IP assertions: the copyright line only; no contributor agreement, patent or trademark statement. One subtree, a vendored skill-authoring toolkit, carries a bare Apache-2.0 licence text with no named copyright holder; it is outside the digest smallest part but a fork of the whole repository would carry both licences.

**Verify.** Licence confirmed by re-reading the full 21-line file at the pin: the recorded text matches, with hard line breaks reflowed and the warranty disclaimer elided at a clause boundary; the manifest corroborates. The Apache subtree claim was not re-verified. Pin confirmed: the commit resolves with the recorded date, the repository push date equals it so the pin is the branch head, the star count matches, and the licence field agrees. Three rows re-checked, none refuted.

**Smallest part.** The cache module, 376 lines, standard library only and with no intra-package imports: a SHA-256 content-hash manifest with check and update functions, dual manifest-shape support, prefix-insensitive hash comparison, an advisory lockfile and atomic replacement. That is the idempotency mechanism, importable alone, with two shipped test modules. Next-smallest, all prose or templates: the paper deep-dive template; the index and log format sections; the staged-writes rules plus the stage-commit skill including its patch-file format; and the raw hand-off block with its format reference.

**Fitting.** *Inputs:* local file paths given to the skill or listed in a sources directory (markdown, text, PDF read through the agent's own reader with page ranges, web-clipper markdown, JSON, CSV, HTML, chat exports, images for vision models, whole directories through a batch planner, git clones enumerated by git, and web URLs through an unshipped browse skill), plus raw notes written by another process carrying the documented frontmatter. Configuration resolves from an override, a dotfile walked up from the working directory, or a user configuration directory, and covers the vault path, the sources directory, the categories, the link format, the raw directory, a per-ingest page cap and a staged-writes switch. *Outputs:* Obsidian markdown pages with YAML frontmatter under the configured category directories, or, with staged writes on, a staging directory holding a page or a patch file; root files for the index (rebuilt), the log (appended with a timestamped operation line), a hot cache and a manifest with per-source content hashes; extracted figures; an archive of promoted drafts; and an optional search index refresh. *Invocation:* by natural language into the skill, dispatched by the frontmatter description; commands include ingest, an URL ingest, stage-commit with list, all and reject-all forms, lint, synthesize and setup. The CLI the skills shell out to offers cache check and update, a batch plan, an AST extract, a lint, a trust check and a setup that symlinks every bundled skill into a dozen agent directories. *Harnesses:* Claude Code (skills through relative symlinks, plus a session-end hook registered in the repository settings that runs a quick-capture script), Codex (a global skills path and a project-local agents path, with repository-shipped symlinks), and nine other agent hosts. Python 3.9 or newer with zero runtime dependencies; Obsidian is a viewer only.

**Surplus.** Session-history ingest skills for six agent hosts plus session search and graph modules, the largest part of the tree and unrelated to literature sources, yet installed by default into every agent directory; a session-end hook that runs quick capture at the end of every session in any project where the repository's settings are present; a Chrome extension with a native-messaging host, force-included in the wheel; a trust ledger and confidence machinery that makes two extra frontmatter fields required, so the lint errors on pages lacking them; importance tiering; provenance markers for inferred and ambiguous claims with per-page fractions and a drift check, which is helpful and directly supports the keep-and-flag behaviour; typed relationships validated by the lint, which gives a machine-readable contradiction edge; a staged-write patch format with conflict detection on promotion, which is a helpful per-source review artefact; an optional semantic-search integration; an optional long-PDF preprocessing path requiring an external repository and an LLM key; code-source handling with AST extraction and repository ingest; graph analysis and export or import; and about a dozen further operational skills, all of which add to the roughly thirty-skill install footprint.

**Coverage.**

**D1 partial** (evidence). The skill's category table and page template, with the ingest skill's own framing and its step-four cap, and the URL adapter's target path.

```
| `references/` | Summaries of specific sources; academic papers use the Paper Deep-Dive Template (below) | `references/attention-is-all-you-need.md` |  ...  > [!tldr] One sentence: what's new, plus the headline result.  ...  You are ingesting source documents into an Obsidian wiki. Your job is not to summarize — it is to **distill and integrate** knowledge across the entire wiki.  ...  This is the deliberate exception to "aim for 10–15 small pages" (Step 4) — a paper earns one rich, self-contained page.
```

A per-source page with a summary and key points is produced for two source classes: academic PDFs, through a deep-dive template with a one-line callout, problem, method, key equations, results and limitations, and web URLs, one page per URL. For a generic markdown or text document the skill's stated job is the opposite of a per-source page: not to summarize but to distribute ten to fifteen topic pages across concepts, entities and skills; a references page is permitted but not mandated by the steps or the quality checklist. The basis is evidence because the deep-dive template is a shipped fenced template; the generic-document gap is what makes it partial.

**D2 does not** (claim). The template's own scope note, with the writing-profile rule and the vault instruction-file rule.

```
Use this template only when the source is an academic paper (arXiv/conference) with load-bearing figures or equations. Everything else uses the generic Page Template above. Frontmatter, provenance markers, confidence, lifecycle, and `relationships:` are unchanged — only the body sections differ.  ...  Writing preferences apply only to newly drafted or rewritten natural-language fields and body content. This includes natural-language title and summary values in YAML frontmatter, but preferences cannot alter YAML syntax, required keys, structure, types, or machine-generated fields.  ...  **After reading config, always read `$OBSIDIAN_VAULT_PATH/AGENTS.md` if it exists.** It contains owner-specific conventions (domain vocabulary, ingest preferences, writing style, project scoping) that override framework defaults for all skills.
```

The per-source template's field list is fixed in the skill, and the generic template's sections are likewise fixed. No flag, environment variable, configuration file or template directory accepts a caller-supplied field list. The only extension points are the categories setting, which names folders rather than page fields, and a vault-level instruction file read for owner-specific conventions, whose own writing-profile rules explicitly say preferences cannot alter required keys or structure. A project could put charting instructions in that file as free prose, but that is an off-book instruction rather than a mechanism.

**D3 partial** (claim). The log and index descriptions, with the contradicts relationship type, the ambiguous marker, the core principle, the lint contradiction callouts, the merge instruction and the synthesis tensions section.

```
Chronological append-only record tracking every operation. Each entry is parseable:  ...  A content-oriented catalog organized by category. Each entry has a one-line summary and tags. Rebuild this after every ingest operation.  ...  - Do not resolve the contradiction; only flag it visually.  ...  - Resolve any contradictions between old and new information (note them if unresolvable)  ...  Merge new information into existing pages, resolve contradictions, strengthen cross-references.  ...  *Where the two concepts pull in opposite directions. Unresolved contradictions. Cases where applying one undermines the other.*
```

The mechanical half is present and templated: a root index rebuilt per ingest, a log declared append-only with a parseable worked example, a synthesis category whose page template has an unresolved-contradictions section, a typed contradicts relationship validated by code, inline ambiguity markers, and a hot-cache scaffold with a flagged-contradictions section. The floor's never-resolved-by-deleting-one-side clause is where the body contradicts itself: the lint path says not to resolve the contradiction and only to flag it visually, while the ingest path, which is the one this lane is about, instructs the agent to resolve contradictions between old and new information and to merge rather than append, and the core principle repeats resolve. Nothing prevents the ingest merge from dropping the older side. The basis is a claim: the keep-both behaviour is prose with no code enforcing it, and it is overridden by the ingest-time prose. This is a blocking finding for adopting the ingest skill unchanged.

**D4 covers** (evidence). The ingest skill's raw mode, with the raw-format specification, the immutable-sources statement and the cache module's arbitrary-path check.

```
In raw mode, each file in `OBSIDIAN_VAULT_PATH/_raw/` (or `OBSIDIAN_RAW_DIR`) is treated as a source.  ...  Full specification for `_raw/` files written by `wiki-capture` (quick mode). These files are designed to be promoted by `/wiki-ingest`.  ...  These are never modified by the system. They live wherever the user keeps them (configured via `OBSIDIAN_SOURCES_DIR` in `.env`).  ...  def check_sources(vault: Path, source_paths: list[Path]) -> CheckResult:
```

Ingest and integrate are separate by design. Sources are read from wherever they already are and are never modified by the system; the tool does not create them. The raw route is the explicit hand-off: notes written by another process, whether by the capture skill, the session hook, the browser extension or a human drop, are consumed by ingest, which derives the promoted page's sources from the note's own frontmatter and archives the original rather than deleting it. The raw format specification is a shipped schema for the hand-off note, and the cache functions accept any path, so a note a Zotero-side process writes into the raw or sources directory would be consumed without the tool owning its creation.

**D5 covers** (evidence). The cache module's classification branch, with the hashing helper, the skill's skip rule and the manifest schema.

```
        elif _strip_algo(entry.get("content_hash")) != current_hash:
            result["modified"].append(key)
        else:
            result["unchanged"].append(key)  ...  - `unchanged` → skip entirely — hash matches, content is identical  ...  "content_hash": "sha256:<64-char-hex>",
```

Shipped standard-library code computes a SHA-256 per file (or a stable digest over a directory tree), compares it prefix-insensitively against the manifest and classifies each source as new, modified, unchanged or missing, while the update function records the hash under an advisory lock with atomic replacement. The no-op itself is the agent honouring the skip-entirely instruction, and the batch planner drops unchanged files from its batches and tells the user when nothing is left. Caveats: the fallback when the CLI is absent is a manual hash or a modification-time comparison, and a separate helper script's delta command is modification-time based, a weaker second path used by the history-ingest skills.

**D6 covers** (evidence). The repository-shipped symlink entries for the Claude and agents skill paths, with the installer's target lists, the console script and the documented no-CLI fallbacks.

```
{"target":"../../.skills/wiki-ingest","type":"symlink"}  ...  (".claude/skills", "~/.claude/skills/ (Claude Code)", None),  ...  (".codex/skills", "~/.codex/skills/ (Codex)", None),  ...  [project.scripts]
obsidian-wiki = "obsidian_wiki.cli:main"  ...  **Fallback** (if `obsidian-wiki` is not installed): compute hashes manually with `sha256sum -- "<file>"` (Linux) or `shasum -a 256 -- "<file>"` (macOS) and compare against `content_hash` in `.manifest.json`.
```

Runs as Claude Code skills as-is: each skill directory is a skill file with name and description frontmatter, and the repository ships relative symlinks under the Claude skills path so a clone is immediately a project-scoped skill set. It is not a plugin (no plugin directory, no marketplace manifest), so a plugin install does not apply; installation is a clone plus symlinks, or a pip install plus a setup command whose installer symlinks every bundled skill into a dozen agent directories. Codex compatibility, recorded separately: the CLI installs into the Codex global skills path and the project-local agents path, and the repository ships those symlinks too. Every CLI call in the skills has a documented no-CLI fallback. The footprint caveat is that the repository's own settings register a session-end hook that runs whenever the repository is opened in Claude Code.

**D7 covers** (evidence). The root files list, the category defaults and the scaffold code with its idempotence docstring.

```
Every wiki has these files at its root:  ...  Organize pages into these default categories (customizable in `.env`):  ...  OBSIDIAN_CATEGORIES=concepts,entities,skills,references,synthesis,journal  ...  mkdir -p "$OBSIDIAN_VAULT_PATH"/{concepts,entities,skills,references,synthesis,journal,projects,_archives,_raw,_staging,.obsidian}  ...  Idempotent: existing files/dirs are left untouched. Returns True if the vault
```

Covers through the states-its-layout branch rather than the caller-chosen branch. Required at the vault root are an index, a log, a hot cache and a manifest, plus raw, staging, archive and metadata directories, a project tree and the category folders. Category folder names are configurable, as is the raw inbox, but the special files and underscore directories are fixed. The scaffold is idempotent on an existing vault, so it can be pointed at an existing markdown vault, and pages outside the category folders are simply not part of the framework's index and lint model. The link format is configurable between wikilink and markdown.

**D8 does not** (claim). The canonical source-key rule, with the manifest writer, the URL slug rule, the source inheritance rule and the provenance-marker table.

```
**Canonical source keys.** Source keys MUST be stored in a single canonical form: **absolute paths with `~` and env vars expanded** (e.g. `/Users/me/.claude/projects/.../abc.jsonl`, never `~/.claude/...`).  ...  yield (entry.get("path") or entry.get("source_id")), entry  ...  6. Prepend `web-`  ...  - If the file has only `sources:`, copy those entries verbatim.  ...  | **Inferred** | `^[inferred]` suffix | An LLM-synthesized claim — a connection, generalization, or implication the source doesn't state directly. |
```

The requirement is a caller-supplied stable id in page links and provenance markers, and neither carries one: page filenames and wikilinks are title slugs or URL-derived slugs; the manifest is keyed by canonical absolute path; the provenance markers encode truth-state rather than source identity; and the alternative id key appears only as a read fallback in the cache module and as an undefined count in the confidence formula, with nothing writing it. The single hook is that the sources frontmatter is a free-form list copied verbatim from a raw note, so a citekey placed there by another process would survive promotion into that field, but it would not key the page or its links. No citekey, BibTeX or Zotero concept exists in the body.

**D9 covers** (claim). The ingest skill's staged-writes check, with the stage-commit skill's invocation forms and per-file review, the configuration comment and the lint safety protocol.

```
2. **Check `WIKI_STAGED_WRITES`** — if set to `true`, all new and updated category pages go to `_staging/<category>/` instead of their final location.  ...  /wiki-stage-commit               # interactive review: show each file and ask accept/reject
/wiki-stage-commit --all         # accept all staged files without per-file review  ...  Accept [a], Reject [r], Skip [s], Preview full [p]?  ...  # When true, LLM-written pages land in <vault>/_staging/ for human review instead of
# going straight into the live wiki. Promote or reject them with /wiki-stage-commit.  ...  3. Ask the user: `"Apply these N changes? [yes / no / select]"`.
```

A configurable review gate exists and is documented in both modes the requirement names: with staged writes on, new pages go to a staging directory and updates to a patch file, and the stage-commit skill reviews per file (accept, reject, skip, with a conflict warning if the target changed since staging) or in batch, with rejected files returned to the raw directory for manual editing and the index and log bypassing the gate by design. The lint's consolidation adds a dry run plus explicit confirmation. The basis is a claim because enforcement is instruction-level: the only code that knows the staging directory is a set of skip-directory constants and the scaffold list, no CLI command stages, promotes or blocks a direct write, and no test exercises staging.

**D10 covers** (evidence). The licence file with the manifest declaration.

```
MIT License

Copyright (c) 2026 Ar9av

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software
```

MIT permits use and modification with retention of the copyright and permission notice. One vendored subtree is Apache-2.0 with no named holder and is not part of any digest piece a caller would take, but a fork of the whole repository would carry both.

**C5 covers** (evidence). The console script entry point, with the core principle naming Obsidian as the interface and the optional server.

```
[project.scripts]
obsidian-wiki = "obsidian_wiki.cli:main"  ...  6. **Obsidian is the IDE.** The user browses and explores the wiki in Obsidian. Everything must be valid Obsidian markdown with working wikilinks.  ...  # Only used by the Dockerized HTTP + MCP server (`python -m obsidian_wiki.server`),
```

Recorded for the headless property only: all skills and the CLI operate on the filesystem from an agent session or a shell, and Obsidian is a viewer. The candidate does not read Zotero, so this is not a capture candidate; the row exists so the no-Obsidian-application property is not re-verified elsewhere.

**C4 does not** (claim). The ingest skill's supported formats and its figure-extraction recipe, with the optional long-PDF branch.

```
- PDF (`.pdf`) — use the Read tool with page ranges.  ...  With PyMuPDF (`fitz`): use `page.get_image_info(xrefs=True)` to find the figure's `xref` and bbox  ...  # Install: clone https://github.com/VectifyAI/PageIndex, create a venv (uv), and put an
# LLM key in <repo>/.env (LiteLLM; e.g. deepseek/deepseek-v4-flash or openai/glm-4.6).
```

Included because ingesting PDFs invites the assumption. PDF text reaches the wiki through the agent's own reader, that is model-mediated rather than a local extractor the repository ships; the library recipe in the body extracts figures rather than text; and the optional long-PDF branch requires an external LLM key, which is a cloud call. No local PDF-to-text code exists in the package.

**Treatment opinion: copy plus a delta.** Install-as-is is excluded by two floors: D2 is absent (the per-source template is fixed and pinned to a template inside the install directory, with no configuration path) and D3 is inverted at the ingest step, where resolve-contradictions and merge-do-not-append override the lint-side flag-only rule. D1 is partial (a per-source page only for papers and URLs), and the install footprint is heavy, since the setup command symlinks more than thirty skills into every agent directory and the repository ships a session-end hook that auto-writes raw files. A fork would inherit all of that plus the vendored Apache-2.0 subtree. The pieces worth taking are small and separable: the cache module verbatim (standard library, tested, and the whole of D5), the index, log and manifest conventions, the paper deep-dive template as the seed of a reference page, the staging and patch review gate, and the raw hand-off contract for D4. The delta is concrete: a caller-supplied charting field list rendered into the per-source page; keying the sources list, page filenames and links by a caller-supplied citekey rather than an absolute path or URL slug; deleting the ingest-side resolve-contradictions instruction so the lint-side flag-only rule is the only contradiction rule; and reconciling the manifest schema's two different field-name sets.

**Facts carried from this body.** The framework is an implementation of Karpathy's gist, which the reference file cites by URL. The cache compares manifest hashes ignoring an algorithm prefix, so a manifest written by another process may store either form and still interoperate, and it reads both a dictionary-keyed and a list-of-entries source shape. Manifest source keys are absolute paths by rule, which is why no citekey-style id exists, so any delta must replace that rule rather than extend it. The Codex compatibility path is that the CLI installs skills into the Codex global skills path and the project-local agents path. Opening this repository in Claude Code activates a session-end hook that runs a capture script, which a fork or a clone inside a working project would inherit. The optional long-PDF path is a cloud LLM call. The manifest schema is internally inconsistent about its provenance field names, which matters if another process reads or writes the manifest.

### 20. Astro-Han/karpathy-llm-wiki

Added by the critic pass, which reversed the triage drop that had filed it as a duplicate mechanism. `https://github.com/Astro-Han/karpathy-llm-wiki`. Pin `eafcc77001e496cc43499e4923b663aec722c813`, main HEAD, read 2026-09-05. Kind: an Agent Skills skill. A 14 KB `SKILL.md` with YAML frontmatter, four reference templates for raw, article, index and archive pages, `scripts/check_evidence.py` at 431 lines of standard-library Python, `tests/test_check_evidence.py` with 52 tests, and an `examples/` directory holding a real raw, compiled, index and log quartet. No package manifest, no MCP server, no runtime beyond `python3` for the lint leg.

**Maintenance.** Last push 2026-07-23T16:57:44Z, about six weeks before the read. 2,154 stars, default branch main, single author, no release tags read, pinned by commit SHA.

**Originator and supplier.** Yuhan Lei is the copyright holder in `LICENSE`; the supplier is the repository owner Astro-Han. The body never says the two are the same person, so both are named here. The idea is credited upstream to Karpathy's gist, and the repository calls itself an unofficial community implementation of that workflow.

**Licence.** MIT, found, at `LICENSE` lines 1-13, corroborated by the GitHub API SPDX id and by `README.md` line 148.

```
MIT License

Copyright (c) 2026 Yuhan Lei

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

IP assertions: no patent grant, no trademark clause, no contributor agreement, no attribution requirement beyond the standard notice retention. No per-file licence headers in the script or the templates, and no `NOTICE`, `CONTRIBUTING` or CLA file in the tree. One credit worth carrying that is not a licence term: `README.md` line 142 reads "Unofficial community implementation of the workflow from [Karpathy's LLM Wiki idea]", so only this repository's prose, prompt and script expression is covered by this grant, not the idea.

**Verify.** No verify pass ran on this record. It was read after the critic pass and the adversarial reader never reached it, so every row here rests on the first read alone.

**Smallest part.** `scripts/check_evidence.py`, one self-contained 431-line Python file using only `re`, `sys`, `dataclasses` and `pathlib`, invoked as `python3 check_evidence.py <project-root> [article.md ...]`, report-only and non-mutating. It is takeable without the rest of the skill because it barely depends on page format: `raw_links_of()` reads only the `> Raw:` line of the metadata header at line 265, candidate extraction skips metadata and status lines, and section structure is never inspected, so it verifies a differently templated vault unchanged. Its only hard couplings are the folder names `raw/` and `wiki/` at lines 298, 346 and 360, and the `index.md` and `log.md` skip set. The 52-test file travels with it as a single second file. The runner-up, if the script is not wanted, is the `Status: Outdated` and `Status: Disputed` block convention, `references/article-template.md` lines 15-21 plus the governing rule at `SKILL.md` line 96, about ten lines of copyable convention that carry the contradiction-preservation behaviour on their own.

**Fitting.** *Inputs:* a source the agent already holds, which is a URL the harness fetched, a local file, or text the user pasted; `SKILL.md` line 51 delegates acquisition to the harness and falls back to asking the user to paste. No PDF, Zotero or database input path. The lint leg takes a project root holding `raw/` and `wiki/`, with optional article paths to narrow scope. *Outputs:* four markdown artifacts under the project root, all plain standard markdown with relative links, no wikilinks and no frontmatter on vault pages: `raw/<topic>/YYYY-MM-DD-slug.md` holding the preserved source under a Source, Collected and Published header; `wiki/<topic>/<concept>.md` with a Sources, Raw and Updated header, an Overview paragraph, synthesized body sections, optional status blocks and an optional See Also section; rows in `wiki/index.md`; and append-only entries in `wiki/log.md` of the form `## [YYYY-MM-DD] ingest|query|lint | <subject>`. The checker writes no files; it prints a markdown report to standard output and its exit code is documented as carrying no information. *Invocation:* natural language routed by the frontmatter trigger list, with three named operations, Ingest, Query and Lint, plus a research sub-mode gated on the user asking for it. Initialization is implicit on the first ingest. The one mechanical call-out is `python3 <skill-dir>/scripts/check_evidence.py <project-root>`. *Harnesses:* Claude Code first, installed with `npx add-skill Astro-Han/karpathy-llm-wiki`; Codex CLI is recorded separately as a copy rather than an installer, `Copy to .agents/skills/karpathy-llm-wiki/`; Cursor and OpenCode use the same npx path. Nothing is Obsidian-specific and nothing needs an application running. The only host dependency is `python3`, confirmed working on 3.12.3 with the standard library alone.

**Surplus.** Query mode, a read path over the vault that answers in conversation and writes no files, is helpful and costs the write path nothing. Archive pages, which are synthesized query answers written as wiki pages with no Raw field and exempted from the fidelity sweep, are a cost: a second page class that no script verifies, designed to go stale, in the same tree as the verified pages. Lint auto-fix authority is a cost: the skill rewrites index rows, repairs links when exactly one match is found, and deletes dead See Also links unattended, which is a hazard on a vault other processes also write, and the single-match repair can silently retarget a link. The unreferenced-raw inventory sweep is helpful and is the mechanism that partly carries D4. The 52 shipped tests are helpful because they pin the candidate-extraction contract. Research mode, with its instruction to search the opposing side, is mixed: useful for a literature vault, but it presumes the tool owns source discovery, which cuts against the D4 separation. The marketing surface, a 283 KB tweet screenshot, usage statistics, a comparison table and an FAQ, is neutral to cost and is most of the repository's byte weight, though the Design Boundaries list is useful intelligence about what the author tried and rejected.

**Coverage.**

**D1 partial** (evidence). `examples/claude-code-statusline-landscape.md` line 9, the compiled page shipped alongside its own source.

```
Around Claude Code's opaque quota problem, the community has spawned over a dozen statusline tools, forming a rapidly evolving ecosystem. By mid-March 2026, competitive focus shifted from "feature count" to "data accuracy and runtime reliability", with zero runtime dependencies becoming a differentiation point.
```

A worked example ships both halves, a markdown source and the page compiled from it, carrying an Overview paragraph and structured key-point sections, so the summary-and-key-points emission is demonstrated rather than described. Three deductions keep it off covers. The page is concept-keyed, not source-keyed: `SKILL.md` line 80 instructs naming the file after the concept, not the raw file, and the example's Sources field carries two dates, so it was updated across ingests. Under the update disposition a source merges into an existing page, and under the "No material" disposition at line 71 no page is emitted at all, so a source is not guaranteed a page. And no PDF-to-text step exists: line 51 defers acquisition to the harness. The per-source artifact that is guaranteed is the raw file, which is a verbatim copy with a metadata header, not a summary.

**D2 does not** (evidence). `references/article-template.md` line 13, under the body-sections heading.

```
{Synthesize a coherent structure from the source material. Do not copy source text verbatim; distill and reorganize. Use blockquotes sparingly for particularly important original phrasing.}
```

The only per-page schema is fixed in that template: a header of exactly Sources, Raw and Updated, then Overview, then body sections the model invents per source, then optional status blocks and See Also. Body structure is model-chosen at compile time, which is the opposite of a caller-supplied field list. Nothing in the skill, the templates or the checker reads a project-level field configuration, and `SKILL.md` line 87 points at the one fixed template. There is no population, concept, context, design, findings or page-locator surface, and no page-locator concept at all; `README.md` line 129 records that persisted line-number citations were deliberately not built. Worth recording for a delta: the checker never reads body structure, so a charting template substituted for this one would still be fully fidelity-checked. The miss is the template, not the tooling. Floor requirement not met.

**D3 covers** (evidence). `references/article-template.md` lines 20-21, the optional status blocks, with the paired Outdated form and its required date at lines 17-18.

```
> **Status: Disputed**
> {The competing claims, each with source attribution.}
```

All four parts of D3 are present as shipped artifacts rather than prose promises. Cross-source synthesis: articles merge multiple sources, with See Also cross-links and a cascade-updates pass that searches the whole wiki for affected articles. Index: `SKILL.md` line 21 specifies one row per article grouped by topic with link, summary and updated date, with a shipped table example. Append-only log: line 22, with `examples/log-sample.md` showing every entry type. Contradictions kept: line 96 says to keep the old claim for the record and mark it with a status block and never silently rewrite history, and line 83 requires both sides marked and cross-linked when the conflict spans two articles; the shipped log sample shows a real disputed disposition, and lint flags missing conflict annotations and malformed status blocks. The reader verified the script-enforced invariant empirically at the pin: a vault built from the shipped example pair ran clean at zero suspects, zero errors and zero unreferenced; altering one table figure to 12,999 and adding a raw file produced exactly that figure under fidelity suspects and the new file under unreferenced raw files, while a second raw file logged as no material was correctly excluded. All 52 tests pass on Python 3.12. Two boundaries: append-only is a prose rule with no code behind it, and the checker deliberately exempts status-block prose from the fidelity sweep, pinned by a named test, so a fabricated "superseded by X" inside a status block is not machine-checked.

**D4 partial** (evidence). `scripts/check_evidence.py` line 353, inside `unreferenced_raws()`.

```
        if path.resolve() not in referenced and path.relative_to(root).as_posix() not in disposed:
```

Shipped code treats an un-integrated raw file as a normal expected state rather than an error: the function walks `raw/` and reports every file no article's Raw field points at, minus those logged as no material, and both branches were confirmed by planting two raw files in a test vault. `SKILL.md` line 201 frames the output as a genuine backlog reminder. The phases are separately scheduled at line 128, where searching may run in parallel but compilation must not, because the index, the log and cascade updates are shared state. The parser also tolerates a foreign note's format: with no leading heading every line goes into the body, so a note another process wrote is still readable as evidence. What is missing is the stated interface. Ingest opens with "Always fetch; whether to compile depends on the triage below" at line 47, and step one tells the agent to obtain the source itself, so there is no documented compile-only entry point for a file already on disk. Integrating a foreign note is an emergent capability the lint surfaces, not a contract the skill offers.

**D5 does not** (claim). `SKILL.md` line 58, under the fetch step.

```
   - If a file with the same name already exists, append a numeric suffix (e.g., `descriptive-slug-2.md`).
```

No content hash, item version, mtime or ETag check appears anywhere in the skill, the templates or the 431-line checker; the only file-identity logic is path resolution. Re-ingesting an unchanged source writes a second raw file under a suffixed name and appends a log entry, which is the opposite of a no-op. The nearest mechanism is the no-material triage disposition, but that is a model judgment about knowledge novelty rather than source-identity detection, it is non-deterministic, and even on that path the raw file is kept and logged. `README.md` line 128 makes this a deliberate design decision rather than an oversight.

**D6 covers** (evidence). `SKILL.md` line 2, the YAML frontmatter, whose description on line 3 carries the trigger list.

```
name: karpathy-llm-wiki
```

`SKILL.md` sits at the repository root with valid Agent Skills frontmatter, with `references/` and `scripts/` beside it, which is the installable-as-is layout, with no build step and no manifest to reconcile. The only runtime dependency is `python3` for the mechanical lint leg, invoked at line 195 by a skill-relative path. The reader ran that script and its test suite at the pin on Python 3.12.3 using only the standard library, 52 tests passing, so the skill-relative path resolves and the tool works as shipped. Codex compatibility is recorded separately as the requirement asks: `README.md` line 106 gives a manual copy into `.agents/skills/karpathy-llm-wiki/` rather than the npx installer, which fits this environment's skills topology; the README was used only to narrow the install path, not to establish the capability.

**D7 covers** (evidence). `SKILL.md` line 230, under Conventions.

```
- wiki/ supports one level of topic subdirectories only. No deeper nesting.
```

This satisfies the second arm of D7: the layout requirements are stated explicitly. The architecture section specifies `raw/` as immutable source material organized by topic, `wiki/` as owned compiled pages, plus the index and the log; initialization creates only what is missing and never overwrites existing files, so it can be pointed at a vault that already exists. The layout is not caller-chosen, and the cost of changing it is concrete: the script hard-codes the `wiki` directory at line 360 and the `raw` directory at lines 298 and 346, and the templates hard-code a two-levels-up relative path, so renaming folders means three script edits plus template edits. The prose is stricter than the code, since the walk would happily descend deeper than line 230 allows. It also assumes total ownership of `wiki/`, which matters if other processes write there.

**D8 partial** (evidence). `references/article-template.md` line 4, the metadata header.

```
> Raw: [{source1}](../../raw/{topic1}/{filename1}.md); [{source2}](../../raw/{topic2}/{filename2}.md)
```

A provenance marker exists on every page and is machine-enforced: the checker reports an evidence error for a non-archive article with no Raw field, for a Raw link that does not resolve, and for a Raw link escaping `raw/`, the last pinned by a named test, and the reader saw the first two branches fire. The identifier is tool-generated rather than caller-supplied: lines 55-57 derive the filename from the source title as a kebab-case slug capped at 60 characters with a date prefix, and line 58's collision rule appends a numeric suffix, which breaks id stability across re-ingests. Sources fields are author-and-date prose, not keys. Nothing forbids a caller from naming raw files by citekey, and the Raw-field plumbing and link checker would carry it unchanged, but no part of the body offers that as an interface, and links are by relative path rather than by id lookup. This and D4 share one fix: let the caller name the raw file.

**D9 does not** (claim). `SKILL.md` line 195, under the mechanical-reports heading.

```
Default scope is the whole wiki; the script is fast. Report findings; never auto-fix facts.
```

The skill has a well-drawn authority ladder, with safe fixes auto-applied, mechanical and judgment reports never fixing, and ambiguous link repairs reported to the user, but every rung of it is lint-side, that is, after integration has happened. The ingest path runs fetch, triage, compile, cascade, index and log in one motion with no approval point: triage states the disposition before editing, which is disclosure rather than a gate, and nothing pauses for a yes. There is no per-source versus batch setting, no dry-run flag, and no configuration surface in the frontmatter or the script. `README.md` line 134 puts scheduling and hooks out of scope deliberately. After-the-fact review is served by reading the log, which is a different thing from a gate before integration.

**D10 covers** (evidence). `LICENSE` lines 5-9, with the header at line 1 and the copyright at line 3.

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software
```

Unmodified MIT text read from the file at the pin, granting use, modification, merging and redistribution with only the notice-retention condition, so copying the templates and script into another repository with a delta is permitted provided the notice travels. The GitHub API license field independently reports MIT and `README.md` line 148 agrees. No per-file headers, no CLA, no additional terms. The only attribution nuance is non-legal: the repository credits Karpathy's gist as the origin of the idea, so a courtesy chain of Karpathy for the idea and Yuhan Lei or Astro-Han for the expression is appropriate.

**C6 covers** (evidence). `LICENSE` lines 5-7.

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction
```

The only capture-lane requirement this body plausibly covers, recorded because C6 is a floor and MIT satisfies it regardless of lane. Every other capture requirement fails on absence: a grep of the whole tree at the pin finds no Zotero, no `localhost:23119`, no Better BibTeX, no JSON-RPC, no citekey, no annotation and no attachment surface, which disposes of C1, C3 and C7; there is no PDF text extraction, which disposes of C4; and while the skill runs headless from an agent with no Obsidian involved, it reads no Zotero at all, so C5's premise is unmet. C2 fails on kind as well as on Zotero: this tool splits ownership by whole file, `raw/` immutable and `wiki/` fully owned, rather than maintaining a machine-owned region inside a note that also has a preserved human region, and its pages are keyed by concept slug rather than by citekey.

**Treatment opinion: copy plus a delta.** The reasoning is that the parts worth taking are the parts the reader watched run, and the parts that miss are fixable without touching them. Verified working at the pin: the evidence invariant bites, a planted figure came back as a fidelity suspect and a planted orphan raw came back as unreferenced while a raw logged as no material was suppressed; the 52 tests pass on standard-library Python 3.12; and the status-block convention is a concrete artifact in the template with a governing rule and a real log entry demonstrating it. That covers D3, and D6, D7 and D10 land as written. The delta is small and localized away from what is worth keeping. D2, the one hard floor miss, needs the body of the article template replaced with the project's charting fields, and because the checker parses only the Raw header line and never inspects body structure, a page with charting sections stays fully fidelity-checked with no script change. D4 and D8 are one fix, not two: let the caller name the raw file by citekey, and add a compile-only entry sentence to ingest so a note another process wrote can be integrated without the always-fetch step. Against install-as-is: D2 cannot be met by configuration because there is no configuration surface at all, and D5 and D9 have no hook to attach one to, since the design deliberately rejects hash tracking and puts scheduling out of scope. Against fork: the change is two prose sentences and one template body, and carrying a divergent history for that is more ceremony than the delta deserves, with upstream six weeks stale. Against copy-frozen: the article template must change, so it cannot be frozen. Against author-and-credit: that would rewrite from scratch the one thing confirmed to work. MIT with notice retention makes the copy clean; carry `LICENSE` and name both Yuhan Lei for copyright and Astro-Han as supplier, with the Karpathy gist noted as the idea's origin. Two boundaries would be inherited knowingly: append-only is prose with no enforcement, and status-block explanations are exempt from the fidelity sweep, so script-verified does not extend to the text inside a contradiction marker.

**Facts carried from this body.** Seven, each with its own quote in the record.

**F1.** The author deliberately rejected source-hash freshness tracking, reasoning that an immutable `raw/` makes it unnecessary. `README.md` line 128, under Design Boundaries.

```
- **Source-hash freshness tracking** — raw/ is immutable, so hashes guard against events that cannot happen. Genuinely new information arrives as new sources through normal ingest.
```

The reasoning does not transfer to a re-run-driven import pipeline, where the same source is re-read on every sync.
**F2.** Persisted line-number citations were also rejected, on the empirical ground that every observed fidelity error was a value simply absent from the source, which a whole-file grep catches. `README.md` line 129.

```
- **Persisted line-number citations** — every observed fidelity error was "value absent from the source", which a whole-file grep catches. Anchors only disambiguate a failure mode that has not occurred, and the annotation friction makes agents skip the rule.
```

This bears on any page-locator field in a charting template.
**F3.** Codex CLI is supported by manual copy rather than by the npx installer used for Claude Code, Cursor and OpenCode. `README.md` line 106, in the tool-compatibility table.

```
| Codex CLI | Copy to `.agents/skills/karpathy-llm-wiki/` |
```

**F4.** The mechanical lint leg is report-only and its exit code is explicitly meaningless, so it cannot be wired into a gate without wrapping. `scripts/check_evidence.py` line 28.

```
The exit code carries no information; the report is the interface.
```

**F5.** Open Knowledge Format conformance is tracked and deferred. `README.md` line 137.

```
- **OKF conformance** — the spec is a v0.1 draft with a minimal tooling ecosystem. Tracked; will be revisited.
```

Sibling projects `lucasastorian/llmwiki` and `atomicmemory/llm-wiki-compiler` are named at line 144.
**F6.** Automatic hooks and scheduled runs are out of scope as a matter of tool-agnosticism, which is why no review gate or configuration surface exists. `README.md` line 134.

```
- **Automatic hooks and scheduled runs** — those belong to the agent harness, not a tool-agnostic skill.
```

**F7.** An ecosystem observation rather than a body fact: a `karpathy-llm-wiki` name search on GitHub returns a `total_count` of 1,246 repositories, queried 2026-09-05, of which roughly a dozen on the first page are same-idea implementations. The digest-lane candidate space is crowded and largely unexamined by this run.

### 21. sdyckjq-lab/llm-wiki-skill

Added by the critic pass, which named it as the run's best remaining chance at a caller-supplied field list and asked for its licence hole to be recorded. `https://github.com/sdyckjq-lab/llm-wiki-skill`. Pin `efa2294dd7c00479f7d8463fef88812d2fd5d1bc`, HEAD of main, committed 2026-07-27T03:30:42Z, `SKILL.md` frontmatter version 3.6.4. Kind: an agent skill, `SKILL.md` plus bash, Python and Node scripts and markdown templates, shipped inside a larger monorepo that also holds a React and Node workbench web application and a graph-engine package. The installable unit is a subset of the repository.

**Maintenance.** Last push 2026-07-27; 2,424 stars; created 2026-04-05; not archived, not a fork; repository about 40 MB. Development is active and disciplined, but its centre of gravity is the workbench and graph engine rather than the skill: HEAD is a browser-test flake fix, issue numbers run in the 280 to 310 range, and the repository carries 32 architecture decision records, a 72 KB changelog, three CI workflows and dated performance baselines. Commits are co-authored by the owner and by a model. Documentation, CI and internal process are unusually thorough for the star count; the gaps are licensing hygiene at the root and a release cadence shared with the web application.

**Originator and supplier.** The methodology is Karpathy's, credited in both READMEs to the llm-wiki gist. The implementation is sdyckjq-lab, named as author in the skill frontmatter, with copyright held as Kiro in `workbench/LICENSE`, the same identity as the HEAD commit co-author. Bundled third-party originators ship inside the install payload: JimLiu for the URL-to-markdown skill, jackwener for a WeChat converter fetched at install time, an unidentified author for the YouTube transcript skill, plus Mike Bostock, Preet Shihn and the marked, DOMPurify and Unicode Consortium licences under `deps/`. Supplier and originator diverge only for the method and for that vendored payload, where sdyckjq-lab is the redistributor.

**Licence.** MIT, declared but incompletely papered.

```
license: MIT
```

Declared at `SKILL.md` line 5, in the header of the exact artifact a taker would take, and at `package.json` line 6. The only full grant text in the tree is `workbench/LICENSE`, opening "MIT License" and "Copyright (c) 2026 Kiro" at lines 1-3, and its location scopes it to the workbench subtree, which `install.sh` does not ship. The hole: there is no `LICENSE` at the repository root at this pin. The contents API returns 404 for it, and a commit query on that path returns zero, so a root licence has never existed in history, which makes the README badge a link that has always been dead. The GitHub repository API reports the licence as null. IP assertions: attribution of the MIT declaration is coherent, since `workbench/LICENSE` names Kiro and the HEAD co-author is the repository owner. Third-party code ships inside the payload, because `install.sh` includes `deps` in its managed items, and `deps/` vendors d3, marked, DOMPurify and roughjs each with a matching licence text file, Unicode data files, and two whole third-party skills. Neither vendored skill carries a licence field in its frontmatter and neither has a licence file; the reader resolved one upstream out of band to MIT and left the other unresolved.

**Verify.** No verify pass ran on this record. It was read after the critic pass, so every row rests on the first read alone. The reader states that every quote was checked with a fixed-string grep against the working tree at the pin.

**Smallest part.** The hash-cache trio: `scripts/cache.sh` at 9.1 KB, `scripts/create-source-page.sh` at 2.4 KB, and their shared `scripts/shared-config.sh`, which does Python detection and forces UTF-8. The trio sources no other repository file and delivers the whole of D5 on its own: a check, update and invalidate interface over a `.wiki-cache.json` keyed by a hash of relative path and content, and an atomic write that rolls the page back if the cache update fails. Its only coupling to the rest is the sentinel convention, since the root finder walks up looking for `.wiki-cache.json` or `.wiki-schema.md`, so a taker either keeps one of those filenames or patches two duplicated copies of that function. Smaller still, if only the idea is wanted, `templates/schema-template.md` at 7.2 KB is a standalone human-editable per-project wiki contract covering layout, naming, cross-reference syntax, ingest rules, an alias table and a lint checklist, instantiated by one substitution. The `templates/` directory as a whole is not the useful cut, because its field lists are fixed.

**Fitting.** *Inputs:* a local file path, where PDFs route to `raw/pdfs` and markdown, text and HTML route to `raw/notes`; a pasted text block; a folder for batch ingest; or a URL through optional adapters only. Routing is data-driven through `scripts/source-registry.tsv`. Per-project context is read from `purpose.md`, then `.wiki-schema.md`, then `index.md`. The wiki root is discovered from a `.wiki-schema.md` in the working directory, else from a `~/.llm-wiki-path` singleton pointer, so there is one default wiki per user unless the caller changes directory. *Outputs:* markdown written into a fixed tree under a caller-chosen root: a per-source page under `wiki/sources/`, entity pages, topic pages, cross-source reports under `wiki/synthesis/`, plus a maintained index, an appended log, an overview, and the state files `.wiki-cache.json` and `.wiki-schema.md`. Links are Obsidian wikilinks. Confidence is carried as inline HTML comments over an extracted, inferred, ambiguous and unverified vocabulary. The graph workflow additionally emits a knowledge-graph page, a JSON data file and a self-contained interactive HTML view. Output language follows a setting read from the schema file and defaults to Chinese. *Invocation:* natural-language intent routed by a keyword table to one of ten workflows: init, ingest, batch-ingest, query, digest, lint, status, graph, delete, crystallize. A bare URL or file path with no stated intent defaults to ingest and runs init first if no wiki exists. Underneath, the model shells out to named scripts. Install is `bash install.sh --platform <claude|codex|openclaw|hermes|auto>` with dry-run, optional-adapter, hook-install, upgrade and target-directory flags. *Harnesses:* Claude Code primarily, installing to `~/.claude/skills/llm-wiki`, with an optional session-start hook and a companion upgrade skill. Codex is first-class at `~/.codex/skills/llm-wiki`, with a legacy path auto-detected, and OpenClaw and Hermes targets ship as well. Obsidian is a recommended viewer only. Host prerequisites are bash, Python 3.8 or later with a Windows fallback, perl for template substitution, jq for step-one validation, and node for the lint runner and the graph builders. Optional URL adapters additionally want bun or npx and a Chrome with a debugging port.

**Surplus.** The interactive knowledge-graph workflow is a cost: it is why `deps/` vendors d3, marked, DOMPurify, roughjs and three Unicode data tables, it drags node into an otherwise bash and Python toolchain, and it is the largest surface with no counterpart in the requirement set. Ten workflows where the set asks for about three is neutral to helpful: delete with cache invalidation is genuinely useful for a re-ingest loop, and the rest is carried weight in a 1,136-line skill file that must be loaded into context. The mandatory privacy self-check before every ingest is a cost for automated import, because it is written as required, blocks on a user reply, and its documented bypass is conversational rather than a flag. The confidence vocabulary with an evidence quote field, validated by a script and reported per bucket by lint, is helpful and is exactly the provenance discipline a charting workflow wants, but it is applied to a transient JSON object and rendered only as HTML comments rather than as structured fields. The per-project alias table and the optional relation-type vocabulary are helpful, and the alias table is the one place the design lets the caller extend behaviour. Chinese-first authoring is a cost for an English vault: the skill file, script messages and default output are Chinese, English is supported but only three seed templates have English variants, and English output is produced by instructing the model to restructure the Chinese examples. The vendored third-party extraction skills are a cost in licence paperwork, install footprint and supply-chain surface for a capability the set never asked for. The second product in the same repository is neutral in practice, because the installer's managed items exclude it, but it dominates the repository, sets the maintenance cadence, and is the only place the MIT text lives. The Windows and WSL portability work is helpful and free.

**Coverage.**

**D1 covers** (evidence). `templates/source-template.md` line 24, under the key-points heading, with the one-line summary blockquote at line 14 and the mandated section list at `SKILL.md` line 423.

```
（3-5 个要点，每个要点用 1-2 句话说清楚）
```

A shipped template file rather than prose: the per-source page skeleton carries a one-line summary blockquote and a three-to-five key-point section, and step 8 of the full processing flow writes it under `wiki/sources/`. PDF and markdown inputs are first-class core routes rather than adapter-gated: the registry file registers a local PDF route and a local document route as built-in, with the note that providing a file path is enough to enter the main line.

**D2 does not** (evidence). `SKILL.md` line 423, step 8 of the ingest workflow, with line 421 pointing that step at the shipped template.

```
包含：基本信息、核心观点、关键概念、与其他素材的关联、原文精彩摘录
```

The per-source field list is fixed by the tool. Line 423 hard-codes the five sections and line 421 points step 8 at a template inside the installed skill directory rather than at anything under the project. Two near-misses, neither a caller-supplied field list. First, `.wiki-schema.md` is per-project and explicitly user-editable, and it is read at ingest time, but its page-format section prescribes only generic frontmatter plus title, summary, body and related pages, and nothing in the ingest flow parameterises the source page from it. Second, `purpose.md` steers which entities and topics get weight, which is direction rather than fields. A grep for customisation across the skill file and the templates turns up only a customisable path, language, alias table and relation-type vocabulary. No charting field surface exists or can be configured. Floor requirement not met.

**D3 covers** (evidence). `templates/entity-template.md` line 26, with companion evidence in the topic template at line 33 and in the auto-fix script header.

```
## 不同素材中的观点
```

Cross-source pages exist as shipped structure: the initializer creates entity, topic, source, comparison, synthesis, session and query directories, and the digest workflow persists cross-source reports under `wiki/synthesis/`. Index and log are first-class files, both regenerated by the initializer. Contradictions are kept rather than resolved: the entity template gives divergent readings of the same entity a durable section, `SKILL.md` line 441 instructs appending and updating that section rather than overwriting, the topic template parks unresolved conflicts, and the lint workflow reports contradictory information with the source page on each side. The no-delete half is enforced mechanically by the one script that auto-fixes, whose header restricts it to deterministic index repairs and forbids deleting pages or editing content. Two caveats the reader declined to upgrade to evidence: append-only on the log is a model instruction with no script behind it, and the contradictions array validated at step one validates a transient object that the flow deletes, so it is not persistence evidence.

**D4 covers** (evidence). `scripts/source-registry.tsv` lines 2-3, the fallback-hint column for the local PDF and local document routes, with the matching call at `SKILL.md` line 312.

```
直接提供文件路径即可进入主线
```

The shipped registry makes caller-provided files a core path with no adapter: local PDF, local document and plain text are all built-in with no adapter name and no dependency, and batch ingest takes a folder and runs ingest per file. So the tool consumes notes another process wrote and does not own their creation, and the URL adapters are strictly optional at install time. One constraint is worth stating: the root finder, duplicated verbatim in two scripts, walks up from the raw file looking for the cache or schema sentinel and hard-fails outside the wiki tree. A note another process wrote must therefore live under the wiki root, or the copy step that saves raw material into the tree becomes load-bearing. For a vault whose PDFs live in Zotero storage, that copy is mandatory.

**D5 covers** (evidence). `scripts/cache.sh` line 128, inside the hashing helper, with the miss branch at lines 220-222 and the skip wired at `SKILL.md` line 367.

```
digest = hashlib.sha256(relative_path + b"\0" + content).hexdigest()
```

A shipped script that does the thing. The check returns a hit, a repaired hit, or one of four miss reasons against `.wiki-cache.json`; the skill makes the check mandatory before the model step in both the full and the simplified flow, and batch ingest skips cached files outright. Writes go through the page creator, which does an atomic temporary-file rename and then updates the cache, rolling the page back if the cache write fails. Two nuances: the hash covers the relative path as well as the content, so renaming an unchanged file is a miss and re-digests it; and the self-heal adopts an orphaned source page only when both the filename stem and the page's `source_path` frontmatter match, otherwise returning a miss that needs verification.

**D6 covers** (evidence). `platforms/claude/CLAUDE.md` line 25, with the installer usage at `install.sh` line 63.

```
默认安装位置：`~/.claude/skills/llm-wiki`
```

A shipped installer, not a claim. It copies a named managed-items set, the skill file, the documentation files, the install scripts, `scripts`, `templates`, `deps`, `platforms` and one JavaScript file, into the platform skill directory; a dry run prints the plan and an upgrade refreshes in place preserving hooks. The skill file carries valid Claude Code frontmatter with explicit trigger and anti-trigger wording. An optional session-start hook ships as a script emitting additional context pointing at the detected wiki. Codex compatibility, recorded separately as the requirement asks, is first-class: the Codex platform file names `~/.codex/skills/llm-wiki` as the default install location with a legacy path auto-detected, and OpenClaw and Hermes targets also ship, both accepting an explicit target directory.

**D7 covers** (evidence). `scripts/wiki-compat.sh` line 2, with the machine-readable layout contract at lines 19-31 and the human-readable tree in the schema template.

```
# 旧知识库兼容脚本：惰性默认、目录检查、按需创建
```

This satisfies the second limb of D7, stating layout requirements explicitly, not the first. The layout is fixed rather than configurable: the initializer hard-codes the raw subdirectories and the wiki subdirectories, and only the wiki root is caller-chosen. What earns covers is that the requirement is stated in a checkable form: the compatibility script exposes inspect, validate and ensure-source-dir subcommands over an explicit required-paths list, and is written to a stated principle of no required migration with lazy on-demand creation, so an existing markdown vault is adapted rather than migrated. Root discovery is by sentinel, with the working directory winning over the singleton pointer.

**D8 does not** (evidence). `templates/source-template.md` line 7, the frontmatter, with the naming rule in the schema template at line 42.

```
source_path: {{RAW_PATH}}
```

There is no caller-supplied stable id anywhere in the body. Grepping the skill file, the templates and the scripts for citekey, citation, bibtex, Zotero, unique identifier and slug returns nothing but an unrelated co-citation graph metric. Identity is derived, not supplied: pages are named by date and short title, cross-references are Obsidian wikilinks resolved by title, and the only provenance marker is a frontmatter path pointing at the raw file plus an empty sources list. That makes identity path-coupled and title-coupled, and the cache hash even folds the relative path in, so a rename breaks the link. The repository is aware of this class of problem, but its resolution is filename governance rather than a caller-supplied key.

**D9 partial** (claim). `SKILL.md` line 255, the privacy self-check in the ingest workflow, with the batch behaviour at line 549.

```
在开始提取或分析任何内容之前，AI **必须**先对用户说下面这句话，然后等待确认：
```

Gates are documented and the per-source versus batch distinction is explicit, but they are prose instructions to the model with no script or configuration behind them, and none of them is a review of the generated pages before integration. What exists: a mandatory yes-or-no privacy self-check before any extraction, with a documented bypass when the user has already consented or when running under batch ingest where it is confirmed once at the top, which is the per-source versus batch documentation D9 asks for; a batch ingest that shows the file list and asks before starting and pauses every five files; a lint that asks which findings to auto-fix; and a delete that requires a second confirmation past five affected pages. What does not exist is any gate between page generation and writing, since step 8 writes unconditionally. Nothing is configurable and there is no setting to switch the gate mode.

**D10 partial** (evidence). `SKILL.md` line 5, the frontmatter of the artifact itself, corroborated at `package.json` line 6 and `workbench/LICENSE` lines 1-3.

```
license: MIT
```

MIT permits use and modification and it is declared in the header of the file a taker would take, plus in the repository manifest, so the intent is unambiguous and attributable. The hole, as the critic asked to have recorded: no licence file at the repository root at this pin. The contents API returns 404 and the commit query on that path returns zero, so it never existed, the README badge has always pointed nowhere, and the repository API reports the licence as null. The only full grant text is `workbench/LICENSE`, in a subtree the installer's managed items do not ship, so an installed copy contains a licence string and no licence text. Compounding it, the installer ships `deps/` wholesale, and the two vendored third-party skills there carry no licence field and no licence file of their own; one upstream resolves to MIT out of band and the other is unresolved. Adoptable in practice, but a floor requirement whose paperwork is incomplete, and trivially fixable by asking upstream for a root licence or by vendoring the MIT text alongside a copy.

**C5 covers** (evidence). `SKILL.md` line 239, the init workflow's closing guidance, with a bash runtime throughout.

```
推荐：用 Obsidian 打开这个文件夹，可以实时看到知识库的构建效果。
```

A cross-lane row, recorded because it is genuinely covered. Obsidian is a recommended viewer, never a runtime dependency: nothing in the skill talks to Obsidian, its URI scheme or any plugin API. Everything runs headless from bash, driven by an agent or directly from a shell, and the skill installs to a command-line agent's skills directory on four platforms.

**C4 does not** (evidence). `scripts/source-registry.tsv` line 2, with the routing note in the schema template at line 123.

```
local_pdf	PDF / 本地 PDF	core_builtin	file	file_ext:.pdf	raw/pdfs	-	-	none	直接提供文件路径即可进入主线
```

Recorded to head off a misreading. The schema template's "直接读取", read directly, does not mean local PDF-to-text extraction. It means the file is handed to the model to read through the harness, which is exactly the cloud call C4 excludes. There is no pdftotext, pypdf, mupdf or equivalent anywhere in the scripts or the dependencies, and the registry row for a local PDF has no adapter and no dependency precisely because no extractor is invoked. All other capture requirements have no counterpart in this body at all.

**Treatment opinion: copy plus a delta.** Install-as-is is off the table because D2 is a floor and the body fails it outright: the per-source field list is hard-coded in the skill file and pinned to a template inside the install directory, with no configuration path. The missing root licence is a second, smaller reason not to simply install, since an installed copy would carry a licence string with no grant text, though that one is fixable by asking upstream or vendoring the text next to a copy. Fork is unattractive for a different reason: the repository is a 40 MB monorepo whose centre of gravity is a React workbench and a graph engine the installer does not even ship, its cadence is driven by renderer work, and every file is authored in Chinese, so tracking that upstream buys nothing for a digest pipeline. Copy-frozen undersells what is worth taking, because the useful parts need modification anyway. What earns copy plus a delta is that the two hardest-won pieces are small, self-contained and directly on requirement. The first is the hash-cache trio, which delivers D5 completely, including the atomic write with rollback and a conservative self-heal that refuses to adopt an orphan page unless both the filename stem and the frontmatter path agree. The second is the two-step ingest seam, a schema-validated structured extraction with an explicit confidence and evidence discipline feeding a separate page-generation step, with an automatic single-step fallback when validation fails. That seam is precisely where a caller-supplied charting field list belongs, and the delta is well defined: make the step-one schema and the source-page section list read from the project's `.wiki-schema.md` instead of being fixed in the skill file, and persist the step-one object as charting fields rather than deleting it. Add a caller-supplied stable id to the source-page frontmatter and to the naming rule to close D8, since identity is currently title-derived and path-derived and the hash folds the relative path in. Left behind: the graph stack and its vendored JavaScript, the URL adapters, the mandatory interactive privacy prompt, and the eight surplus workflows. Attribution obligations if copied: the MIT notice for sdyckjq-lab and Kiro, plus the Karpathy gist credit the README carries for the methodology.

**Facts carried from this body.** Eight, each with its own quote in the record.

- **F1.** The implementation credits Karpathy's gist as the source of its methodology. `README.md` line 7, with an English equivalent and a credits list in the English README: "基于 [Andrej Karpathy](https://karpathy.ai/) 的 [llm-wiki 方法论](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)".
- **F2.** The re-ingest no-op keys on a hash over the relative path, a null byte and the content, so a rename of an otherwise unchanged file is a cache miss and triggers a full re-digest. `scripts/cache.sh` line 128: "digest = hashlib.sha256(relative_path + b"\\0" + content).hexdigest()". Anything that renames source notes, including a citekey rename or a Zotero re-key, will re-run the model.
- **F3.** The structured, schema-validated extraction that would be the natural home for charting fields is explicitly transient, generated, validated, then deleted, never persisted as fields on the page. `SKILL.md` line 377: "输出：JSON 格式的分析结果，不持久化，只在当前 ingest 流程里临时传递". Line 402 deletes the file.
- **F4.** The only script that auto-repairs the vault is constrained by design to additive deterministic fixes and is forbidden from deleting pages or editing content, which is what makes the keep-both-sides property hold mechanically rather than by instruction. `scripts/lint-fix.sh` line 4: "# 修复范围：仅处理确定性修复（补 index 条目），不做高风险操作（删页面、改内容）".
- **F5.** Wiki-root discovery uses a per-user singleton pointer as the fallback, so without changing directory into a vault holding the schema sentinel there is exactly one active knowledge base per user account. `SKILL.md` line 148: "回退到读取 `~/.llm-wiki-path`".
- **F6.** The installed payload is a named subset of the monorepo, so the repository's bulk is not inherited by an install, but `deps/` is. `install.sh` line 24: "MANAGED_ITEMS=(", with the list running to line 38.
- **F7.** The per-project config file is framed as jointly user-editable and model-editable and is read at ingest time. `templates/schema-template.md` line 3: "这个文件告诉 AI 如何维护你的知识库。你和 AI 可以一起调整它。" It is the only genuine per-project extension point in the design, though it governs layout, aliases and lint rules rather than per-source fields.
- **F8.** The upstream licence of the largest vendored third-party skill, which ships in every install without an in-tree declaration, resolved out of band as "MIT" from the GitHub API for `JimLiu/baoyu-skills`.

______________________________________________________________________

## Candidates, capture lane

### 22. PKM-er/obsidian-zotlit

Seeded. `https://github.com/PKM-er/obsidian-zotlit`, which is a GitHub redirect to `aidenlx/zotlit`. Pin `e628e3953837881a53966156d4cebfad7d62435d` on main, Obsidian plugin 2.1.2 per the manifest, HEAD the 2.1.2 release commit of 2026-09-04T17:23:01Z. Kind: an Obsidian plugin in a monorepo that also ships a required Zotero add-on called ZotLit Companion, three agent skills, and private workspace libraries for the database, the templates and the wire protocol.

**Maintenance.** Last push 2026-09-04T18:30:47Z; 1,012 stars; not archived; default branch main, with a documented convention that betas ship from a `next` branch and stable from main. Single maintainer with a sponsors funding URL. The version 1 codebase is retained on a `v1` branch with separate documentation.

**Originator and supplier.** AidenLx is both; the manifest names the author and the author URL, and the seeded organisation URL is a redirect to the personal account.

**Licence.** AGPL-3.0-or-later, found, at `LICENSE` lines 1-2 with the grant in `NOTICE` lines 1-15, the root `package.json` line 4 and the README footer. The plugin manifest carries no licence field.

```
GNU AFFERO GENERAL PUBLIC LICENSE
Version 3, 19 November 2007
```

```
ZotLit
Copyright (C) 2022-present AidenLx
This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
```

IP assertions are unusually explicit. The notice asserts derived works: "This project contains code derived from the following AGPL-3.0-licensed projects by the Corporation for Digital Scholarship: Zotero, Zotero Utilities, Zotero Reader, Zotero Note Editor, Zotero Data Server", naming ten specific files. It also names Mozilla-derived code under MPL-2.0 in two development-server files, and fixture assets under Creative Commons licences that it declares outside the AGPL grant. Copyleft attaches: use and modification are permitted, but distributing or network-serving modified code must be AGPL and source-available.

**Verify.** Two passes ran. Both re-fetched the body files at the pin and found the C1, C2 and C6 quotes verbatim, including the marker constants, the region-replacement comment and the 661-line licence file. Licence confirmed from body files rather than from the README, with the API SPDX id agreeing. Pin confirmed in both passes, including that the seeded organisation URL resolves to the personal account. Three rows re-checked in each pass, none refuted.

**Smallest part.** `packages/templates/src/obsidian.ts`, 63 lines with no Obsidian or Zotero imports: the managed-region marker constants, the region formatter, the transform, and a first-region replace with a duplicate count and a safe replacer. The next-larger self-contained modules are the 515-line WAL-safe snapshot reader for `zotero.sqlite`, which has reflink, copy and immutable modes and torn-snapshot fingerprinting and depends only on Node plus three small local helpers, and the private database workspace library, which carries a schema for Zotero userdata 125, a Node client over `node:sqlite`, and queries for items, annotations, attachments, collections, tags and the citekey. Takeable as a design rather than as code: the Companion's checkpoint-then-signal freshness pipeline, and the protocol package's URI action and HTTP wire contracts.

**Fitting.** *Inputs:* the Zotero data directory, meaning `zotero.sqlite` and its write-ahead log, resolved per device from the profile files or from a device override; an optional base attachment path preference; vault template files in Liquid, or in a second engine behind a consent gate, with embedded defaults; and plugin settings for the managed frontmatter field list, library scope, read mode and attachment folders. Item selection comes through a quick switcher, through `obsidian://zotlit/...` URIs, or through an HTTP PUT from the Companion. *Outputs:* markdown literature notes with YAML frontmatter carrying a system `zotero-key` field plus managed fields, whose body holds a managed region rendered from a content template with note links and annotation callouts; imported notes converted from Zotero HTML notes and keyed by note key and last-modified stamp; copied attachment images; JSON envelopes from the command-line interface; and a key list served back to the Companion. *Invocation:* the Obsidian command palette, Zotero context menus in the Companion that launch URIs, Companion HTTP pushes to a local listener that is off by default, and agent skills that drive the Obsidian command-line interface. *Harnesses:* Obsidian desktop only, with the manifest marking it desktop-only and requiring a recent installer for `node:sqlite`, plus the required Companion add-on in Zotero 9 or later. An optional Pandoc WASM engine is downloaded for citation rendering. Agent skills exist for Claude Code, Codex and pi, but the agent path still requires a running Obsidian with the vault open.

**Surplus.** The citation system, with a downloaded Pandoc engine, formatted in-text citations, two sidebars, a popover, a key suggester and export, is a large surface the capture role never needs, though it is neutral if left uninstalled because the engine's absence is a normal mode. The annotation sidebar that follows the active reader is helpful for reading and neutral for capture. Zotero note import is helpful and is the only per-item change check in the body. The template workbench, its skill and its data explorer are helpful for authoring the note template. The live-update listener and the Companion pushes are neutral, off by default, and only add refresh immediacy. The Companion add-on itself is a cost: a second install inside Zotero is mandatory for freshness on Zotero 10. Attachment import with a reflink copy and an approved-roots security model is neutral and only fires for images. Downloaded language packs, release assets and runtime schema fetches are a cost in network calls and consent prompts unrelated to capture. Library scope across group libraries is helpful if group libraries matter. The second template engine behind a consent gate is neutral, because the Liquid defaults suffice.

**Coverage.**

**C1 covers** (evidence). `apps/obsidian/src/services/database/read-source.ts` lines 2-6 and 119-141, with the client creation in the database service and the queries in the database package, including the citekey field constant.

```
WAL-fresh read sources for the live Zotero SQLite database. | Zotero keeps `zotero.sqlite` open with exclusive locking while it runs. From Zotero 10 it also runs the database in WAL mode, so recent writes live in `zotero.sqlite-wal` until a checkpoint | db.query.itemAnnotations.findMany({ | db.query.itemAttachments.findMany({
```

Item metadata, attachments, annotations, tags, collections and the native citation key are read from the local database through a typed query layer over `node:sqlite`, snapshotting the main file and the write-ahead log by reflink or copy, or opening the file immutable. That is a local read rather than the web API, so it satisfies C1's intent. One load-bearing caveat: the transport is neither the local API on port 23119 nor Better BibTeX JSON-RPC. A grep for those found only the Zotero preference-port constant and fixture installers, and no Better BibTeX database is read, so the requirement set's local-API vocabulary and the whole Z register do not apply to this capture path. The documented hard dependency is "ZotLit supports Zotero 9 or later and requires the Companion.", and on Zotero 10 an immutable read skips un-checkpointed rows unless the Companion issues a passive checkpoint.

**C2 covers** (evidence). `packages/templates/src/obsidian.ts` lines 2-3 and 40, with the default filename template, the frontmatter reference table, the update operations and the key-writing line.

```
export const MARKER_START = "%%zt-managed%%"; | export const MARKER_END = "%%/zt-managed%%"; | Replace the first `%%zt-managed%%` region in `content` with `region()`. | {{ zt.citationKey | default: zt.DOI | default: zt.title | default: zt.key }}{% suffix %} | { key: "citekey", expr: "zt.citationKey", merge: "replace", language: "liquid" }
```

The tool emits a markdown literature note whose body carries a machine-owned region between markers, re-rendered from the content template on update, with everything outside preserved. The default filename is the citekey and a default managed frontmatter field writes the citekey with a replace strategy. One identity nuance the vault must absorb: the plugin's own key is `zotero-key`, an indexed key rather than the citekey, and the documentation states that it writes a null citekey when the Zotero item has no citation key. Two free-region caveats: only the first managed region is replaced, and a note without markers receives frontmatter-only updates with a message saying no managed region was found. Unmanaged frontmatter keys are preserved and managed ones follow replace, append or keep strategies.

**C3 partial** (evidence). `apps/obsidian/src/services/note-feature/update-batch.ts` lines 238-247, with the imported-note action builder, the protocol's notify type, the last-modified constant and the citekey documentation.

```
const file = deps.noteIndex.getNotesByItemKey(ref.indexedKey)[0]; | if (file) { actions.push({ ...row, kind: "update", file }); | /** Existing file with matching `zotero-lastmod` → up-to-date; missing field → overwrite. */ | The Freshness Signal: the Zotero database changed and the main database file is as current as the companion can make it. Carries no item identity
```

Change detection is whole-database rather than per-item: a file watch on the database and its log, plus the Companion's payload-free freshness signal, trigger a full snapshot refresh. For literature notes, batch classification is only create, update or not-found by note existence, with no item version or modification-date comparison, so every update re-renders. Per-item drift detection exists only for imported notes, through a last-modified frontmatter field compared at second resolution. Orphans surface as a not-found group when an item is absent from the database. On re-key, the citekey frontmatter field is rewritten on each update and citation resolution rebuilds from the native field after each refresh. The modification date is exposed on every item row, so a caller could add a managed field for it, but no drift check for literature notes ships.

**C4 does not** (evidence). `packages/db/drizzle/schema.ts` lines 725-726, a schema mirror only; a recursive grep for full text across the database package, the plugin source and the add-on source returned no query.

```
export const fulltextItems = sqliteTable( | "fulltextItems",
```

No PDF-to-text extraction exists anywhere in the body. Zotero's full-text tables are mirrored in the schema but no query reads them, and the PDF library appears only as a submodule path and in lint and format configuration, never imported by plugin source. Attachments are exposed as resolved file paths and links, and annotations as Zotero-stored highlight text, not as extracted page text.

**C5 does not** (evidence). The documentation's prerequisites, the vault-window evaluation helper, and the desktop-only manifest flag, with the database package marked private.

```
- An open vault with ZotLit loaded. | /** Run JavaScript in a vault window. Without `target`, the focused one answers. */ | "isDesktopOnly": true
```

All note emission runs inside the Obsidian process: the note feature imports the application and file types from Obsidian and writes through the vault API. The agent-facing commands are Obsidian command-line handlers that execute in a running vault window, and the documented prerequisite list requires an open vault. The Zotero-reading layer has a Node-only client with no Obsidian dependency, but it is marked private and unpublished, and it does not produce notes, so it is recorded under the smallest part rather than as coverage.

**C6 covers** (evidence). `LICENSE` lines 1-2, `package.json` line 4 and `NOTICE` lines 1-15.

```
GNU AFFERO GENERAL PUBLIC LICENSE | Version 3, 19 November 2007 | "license": "AGPL-3.0-or-later",
```

The licence permits use. Copyleft attaches to distribution or network provision of modified code; adopting the note file contract, meaning the key field and the managed markers, is format adoption and carries no code-licence exposure.

**C7 does not** (evidence). `apps/zotero/src/menus/item.ts` lines 105-191, with the menu registry, the freshness pipeline and the note-status column.

```
l10nID: "zotlit-menu-item-open", | l10nID: "zotlit-menu-item-copy-key", | l10nID: "zotlit-menu-item-update", | l10nID: "zotlit-menu-item-update-metadata", | l10nID: "zotlit-menu-item-import-child-notes", | l10nID: "zotlit-menu-item-import-notes", | l10nID: "zotlit-menu-item-explore",
```

There is no Zotero-side enrichment or metadata lint: a grep for the enrichment vocabulary hits only field-mapping tables, never a lookup. What the Companion does provide, so the vault need not replicate it, is a passive write-ahead-log checkpoint after notifier events plus a manual truncate control, a payload-free change signal posted to the plugin's listener, an item-tree column fed by a key list, the seven item and collection context menus quoted above, and two reader push events for the annotation sidebar. All are transport and freshness features, and none touches item metadata.

**D6 partial** (evidence). `skills/zotlit-template/SKILL.md` lines 1-4 with its two sibling skills, their Codex metadata files, the install page and the discovery route.

```
name: zotlit-template | npx skills@latest add https://zotlit.aidenlx.site/ | Install the ZotLit skill in one vault for Claude Code, Codex, or pi. | const AGENT_SKILLS_ROUTE = "/.well-known/agent-skills";
```

Three installable agent skills ship, discoverable at a well-known route and installed with a single command, targeting Claude Code, Codex and pi, with a Codex metadata block for each. The skills drive the Obsidian command-line contract for template authoring, citation queries and Pandoc export. None digests a source into pages, so the D6 mechanism is present but not for the digest role. The command-line-and-skill pairing policy and the per-namespace contract versions are reusable design patterns.

**D7 covers** (evidence). `apps/obsidian/src/services/note-index/service.ts` lines 198 and 33-40, with the parser and the documented rule.

```
for (const file of this.#app.vault.getMarkdownFiles()) { | const value = cache?.frontmatter?.[FIELD_ZOTERO_KEY]; | ZotLit identifies a literature note by a single frontmatter field: `zotero-key`. Any Markdown file in your vault that contains this field is treated as a literature note, regardless of filename or folder location.
```

It works on an existing vault with a caller-chosen layout: the note index scans every markdown file and keys only on frontmatter, so location is free. The layout requirements it does state are that templates live in a configured folder under a fixed name pattern, that the path for a new note comes from a filename template plus a configured folder, and that attachment imports go to the vault attachment folder.

**D8 partial** (evidence). `packages/db/src/queries/citekey.ts` lines 7-8 and the citekey documentation page.

```
const CITEKEY_FIELD = "citationKey"; | ZotLit resolves Pandoc citation keys against Zotero's native citation key field, across every library in your **Library scope**. It does not use the `citekey` frontmatter field for resolution.
```

Citekeys are first-class for citations: Pandoc citations and citation wikilinks resolve through the native field, the default filename is the citekey, and the citekey is written to frontmatter. But provenance identity in the note is the indexed key, so a vault that wants the citekey as its sole stable id must keep the mapping itself, and ambiguous keys across libraries are deliberately left unresolved.

**D10 covers** (evidence). `LICENSE` lines 1-2, `package.json` line 4 and `NOTICE` lines 1-15, the same reading as C6, whose quote is the C6 block above. The licence permits use and modification; modified redistribution or network use must remain AGPL with source offered.

**Treatment opinion: install as-is.** The reasoning is that for the capture role this is a mature, actively released two-part install, the plugin plus the mandatory Companion. It meets the capture floors with shipped code rather than prose: a local read, a managed region with a preserved free region keyed by a citekey filename and frontmatter field, and a licence that permits use. Its note contract, meaning the key frontmatter, the citekey managed field, the markers, and the rule that notes are adopted from any folder, is a stable seam another process can write to or read from, and adopting that format is not code copying and carries no copyleft exposure for the vault's own tooling. Forking or copying with a delta is disproportionate against a monorepo of more than 1,600 paths with private workspace packages, an Electron-bound emitter, and copyleft on any modified distribution. The two real gaps do not argue for a fork either: no headless run, because everything needs a running Obsidian and the database package is private, and whole-database refresh with no per-item version for literature notes are both architectural. A headless companion for drift and orphan detection is better authored separately against the same frontmatter, crediting the marker convention. One thing to watch: because this candidate reads SQLite directly, none of the run's local-API facts transfer from it.

**Facts carried from this body.** Eleven, all with quotes in the record; they are the richest Zotero-internals source in the run and several are carried into the Zotero facts section below. In summary: Zotero 10 runs the database in write-ahead-log mode with exclusive locking, so no shared-memory file exists and recent writes sit in the log until a checkpoint, while Zotero 9 and earlier use a rollback journal (F1); an immutable read on Zotero 10 misses every committed but un-checkpointed row, measured as five items read back as five rows from a snapshot and zero from an immutable read (F2); the citation key is a native Zotero field named `citationKey`, originally a Better BibTeX feature, read from item data rather than from Better BibTeX, with no Zotero version stated (F3); schema versions are userdata 125 for Zotero 9.0.0 through 9.0.6 and 129 for Zotero 10.0.0, with compatibility 7 and 9 respectively (F4); the HTTP server port defaults to 23119 under a named preference, and a value of minus one means automatic selection whose effective port is not persisted (F5); attachment link modes are five named integers, with a storage prefix for files in the item directory and a placeholder for linked files under the base directory (F6); a passive checkpoint is non-blocking and is the same operation Zotero 10 runs at idle and shutdown (F7); the notifier types that mean a database write include tag events, because bulk tag operations bypass the item save path and fire no item event (F8); cross-library identity is a bare key for the personal library and a key with a group suffix for group libraries (F9); the Companion is required and keeps the main file current by default without any server (F10); and personal and group web-library URLs take different forms, with a never-synced account having no username (F11).

The record also notes seam observations kept out of coverage: the plugin adopts any markdown file carrying a valid key field regardless of who wrote it, and updates only the first managed region, so an external process may own note creation and the plugin can still refresh it. The plugin never writes to Zotero; the README states that it reads only. Better BibTeX appears only in advice to use its CSL-JSON auto-export as a bibliography and in fixture installers.

### 23. mgmeyers/obsidian-zotero-integration

Seeded. `https://github.com/mgmeyers/obsidian-zotero-integration`, distributed through the Obsidian community directory as "Zotero Integration" with the plugin id `obsidian-zotero-desktop-connector`. Pin `2043211d87ff2ca5db31bf587b5024eac9f49171`, HEAD of main, 2026-03-06, whose code is identical to release 3.2.1. Kind: an Obsidian plugin.

**Maintenance.** The last push is 2026-03-06, but that commit removes a funding file and changes no code. The last code commit is 2024-08-11, tagged 3.2.1, which is also the latest release. 1,759 stars, 104 forks, 258 open issues as of 2026-09-04; created 2022-01-09. About 24 months without a code change, and not archived. Its hard external dependency, the annotation-extraction binary, was last pushed 2024-01-29.

**Originator and supplier.** mgmeyers, both.

**Licence.** GPL-3.0, found, at `LICENSE.md` lines 1-2, an unmodified 673-line text.

```
                    GNU GENERAL PUBLIC LICENSE
                      Version 3, 29 June 2007
```

IP assertions: no author copyright line was ever filled in, so the only copyright notice in the file is the Free Software Foundation's own at line 4, and the apply-these-terms template at the tail is blank. There is a metadata conflict: `package.json` line 21 declares MIT while the licence file is GPL-3.0, and the manifest carries no licence field. The licence file governs, so the record treats it as GPL-3.0, with copyleft on distribution of derived code. The body also credits borrowed code in three places: a lighter version of a heap implementation, a component copied and modified from ZotLit, which is AGPL-3.0, and a fragment from a Nunjucks discussion. Its runtime dependency, the annotation binary, is AGPL-3.0 and is auto-downloaded from GitHub releases at install.

**Verify.** Two passes ran, three rows each, none refuted. Both confirmed the JSON-RPC attachment call and the port helper verbatim in body code, the persist-region template and its extraction regex verbatim, and the 673-line licence file with the Foundation copyright at line 4. One pass explicitly confirms that the declared metadata conflict is real and that both readings permit use. Pin confirmed in both passes; one pass notes it did not re-check that the pin is still HEAD of main.

**Smallest part.** The persist-region mechanism: the Nunjucks extension class in `src/bbt/template.env.ts` lines 144-203, which implements a `persist` tag whose run method emits the begin-and-end marker pair and whose static preparation harvests existing regions with one regex, plus the import-date trailer pair in `src/bbt/template.helpers.ts` lines 51-70. It depends only on Nunjucks and a date library, about 75 lines, separable from all Obsidian and Zotero code. Second-smallest: the JSON-RPC client at 683 lines, but it imports three symbols from Obsidian and a modal, so it needs a shim to run outside the application.

**Fitting.** *Inputs:* a running Zotero desktop with Better BibTeX, reached over HTTP at the JSON-RPC endpoint on the loopback address, with items chosen either through the cite-as-you-write picker, which opens Zotero's own dialog, or by an explicit citekey and library id; per-format settings in the plugin's data file naming an output path template, image path and base-name templates, a template path pointing at any Nunjucks markdown file in the vault, and a CSL style; an optional annotation binary auto-downloaded from GitHub releases, with an optional OCR engine for image annotations; and the existing note at the output path, read for persist regions and the import-date trailer. *Outputs:* one markdown file per item at the rendered output path, created or fully rewritten. Template data includes the citekey, a bibliography string, collections, child notes converted to markdown, attachments with annotations merged from native Zotero annotations and from the binary's output, relations, tags, dates as date objects, and a set of helper fields. Rectangle-annotation images are copied into the vault. When the template has a persist block, an import-date trailer is appended. Separately, an import-notes command writes one file per citekey from Zotero child notes, and citation commands insert picker text at the cursor. *Invocation:* the Obsidian command palette only, with one command per import format plus note-import, note-insert, a debug view and citation commands. There is one programmatic entry, an import method taking a format name, a citekey and a library number, reachable by another plugin or script inside a running Obsidian. No command-line interface and no URI handler. *Harnesses:* Obsidian desktop only, marked desktop-only in the manifest, using Electron's remote module, Node file and path modules, and a subprocess runner. No Claude Code, Codex or command-line surface, so Codex compatibility is not applicable.

**Surplus.** Cite-as-you-write insertion in six formats is helpful for writing inside the vault and neutral for capture. The data explorer with live template preview is helpful for authoring the note template and costs bundle size. PDF rectangle-annotation image extraction with optional OCR is a cost: an AGPL-3.0 platform-specific binary auto-downloaded from releases and version-pinned in code, plus permission and rename bookkeeping. Zotero child-note import with rewriting of annotation and citation HTML into Zotero links is neutral. Annotation concatenation, where a comment beginning with a plus merges into the previous annotation, is neutral. Related-item resolution one level deep is helpful for link graphs and costs two extra round trips per item with relations. The bundled CSL style catalogue at 269 KB is a bundle-size cost with neutral function. The legacy three-file template mode with its own annotation wrapper is a cost, because it means two code paths and two marker conventions to be aware of when parsing notes. Open-note-after-import with a hard-coded one-second delay is neutral. Unwired citekey autocomplete scaffolding is dead code and neutral, though the export-endpoint call inside it is a useful fact.

**Coverage.**

**C1 covers** (evidence). `src/bbt/jsonRPC.ts` lines 131-139, the attachment fetch, with the port helper at `src/bbt/helpers.ts` line 12.

```
      url: `http://127.0.0.1:${getPort(
        database.database,
        database.port
      )}/better-bibtex/json-rpc`,
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'item.attachments',
        params: [citeKey.key, citeKey.library],
      }),
```

All reads go to Better BibTeX JSON-RPC on the loopback address at port 23119, with 24119 for Juris-M or a custom port. Metadata comes from an export call with a named translator, attachments and native annotations from the attachments call, child notes from the notes call, and collections from the collections call. Item selection is through the picker or through an explicit citekey. There is no web API use anywhere in the body. Note that this is Better BibTeX JSON-RPC, not Zotero's own local API, and Better BibTeX is a hard dependency stated in the README and in the picker's error text.

**C2 covers** (evidence). `src/bbt/template.env.ts` lines 180-182, the persist extension's run method, with the extraction regex at line 193, a worked test at lines 238-262 of the test file, and the citekey path rendering in the exporter.

```
    return new nunjucks.runtime.SafeString(
      `%% begin ${id} %%${retained}${trimmed}%% end ${id} %%`
    );
```

The model is the inverse framing of the requirement but functionally the same: the whole file is machine-owned and rewritten on every import, and only persist regions survive, serialised between begin and end markers. It is keyed by citekey only when the caller's output path template uses the citekey, which is what the settings example shows; the separate note-import command always writes a citekey-named file but with no persist region, so it is a plain overwrite. Two caveats. The persist body is retained and the freshly rendered body is appended on every import unless the template guards on first-import or filters by the last import date, and the project's own documentation shows the resulting repetition. And the import-date trailer is only written when a persist block is present. The shipped test demonstrates retained text merging with new text.

**C3 partial** (evidence). `src/bbt/template.helpers.ts` lines 51-52, the last-export reader, with the trailer writer at lines 68-70 and the annotation and item date fields in the exporter.

```
export function getLastExport(md: string): moment.Moment {
  let match = md.match(/%% Import Date: (\S+) %%\n$/);
```

What exists is a per-file last-import timestamp read from the trailer and exposed to templates as a last-import date and a first-import flag, a per-annotation date from Zotero's annotation modification time, and item modification and added dates as template data. That supports annotations-since-last-import inside one note. What does not exist is any item-version or since-parameter comparison, any comparison of the Zotero modification date against the note, or any vault scan for orphans or re-keys. A function that fetches every citekey per library through the export endpoint exists but is unwired, with its search index field declared and never used. One fragility: the trailer regex anchors on end-of-file, so any text after the trailer makes the reader return the epoch and all annotations re-import as new.

**C4 does not** (evidence). `src/bbt/extractAnnotations.ts` lines 75-78, the subprocess call, with the parameter map and the binary URLs.

```
    const result = await execa(
      overridePath || path.join(getExeRoot(), getExeName()),
      args
    );
```

The only PDF processing is the external binary, which returns annotations, meaning highlight text, comments and rectangle images, not the document's full text; the annotated-text field is the highlighted span. Optional OCR applies to image annotations only. Extraction itself is local, but the binary is fetched from GitHub releases at install and update time. There is no PDF-to-text of the body anywhere in the code.

**C5 does not** (evidence). `manifest.json` line 9, the plugin class declaration, and the Electron dependency in the helpers.

```
"isDesktopOnly": true
```

Every input and output path runs through the Obsidian runtime: the HTTP request and HTML conversion helpers come from Obsidian, file writes go through the vault API, template includes go through the metadata cache, and Electron's remote module supplies window focus and file dialogs. There is no command-line interface, no exported library entry point and no package binary. The one non-interactive entry is the import method, which bypasses the picker and can be called by another plugin or script inside a running Obsidian, which is scriptable rather than headless.

**C6 covers** (evidence). `LICENSE.md` lines 1-2, with the conflicting declaration at `package.json` line 21 and no licence field in the manifest. GPL-3.0 permits use, study and modification, with copyleft only on distribution of derived code. Either reading of the conflict permits use, so C6 holds under both.

**C7 does not** (evidence). `src/bbt/jsonRPC.ts` lines 254-262, the bibliography parameters, with the collection walk, the relation resolution, the issued-date parse and the colour categoriser.

```
    const params: Record<string, any> = {
      quickCopy: true,
      contentType: 'html',
    };

    if (cslStyle) {
      delete params.quickCopy;
      params.id = cslStyle;
    }
```

No DOI verification, PMCID lookup, citation count, arXiv version update or metadata lint exists in the body. What it does provide, so the vault need not replicate it, is a CSL-styled bibliography string through Better BibTeX, collection full paths built by walking the parent chain, related-item resolution from relation URIs to citekeys and then to full item JSON, a parsed issued date from CSL date parts, annotation colour names bucketed from hex, and tag lists in two forms.

**D2 partial** (evidence). `src/bbt/template.env.ts` lines 285-289, the render entry point, with the documentation's statement that templates may live anywhere in the vault.

```
export function renderTemplate(
  sourceFile: string,
  templateStr: string,
  templateData: Record<any, any>
) {
```

The per-source template and its field list are fully caller-supplied, since the template is any Nunjucks markdown file in the vault with include-based composition, and one note is rendered per item. But every value available to the template is Zotero metadata, child notes or annotations; nothing is read or inferred from the source document itself, and there is no model in the loop. It can lay out a charting skeleton, for instance persist blocks named for the charting fields, but it cannot fill those fields.

**D7 covers** (evidence). `src/types.ts` lines 47-51, the export-format interface, with the path rendering and the folder creation helper.

```
export interface ExportFormat {
  name: string;
  outputPathTemplate: string;
  imageOutputPathTemplate: string;
  imageBaseNameTemplate: string;
```

Folder layout is entirely caller-chosen: the note path, the image folder and the image base name are each templates over item data, and missing folders are created. Templates live anywhere in the vault. The only fixed locations are the plugin's own directory for the annotation binary and Obsidian's attachment folder setting for note-import images. It works on an existing vault with no index, log or tree assumptions.

**D8 covers** (evidence). `src/main.ts` line 39, the default suggestion template, with citekey population in the exporter and the explicit citekey argument on the programmatic entry.

```
  citeSuggestTemplate: '[[{{citekey}}]]',
```

Every rendered item carries the citekey under two names, usable in the output path and in wikilinks. Per-item and per-annotation provenance markers are Zotero select and open-PDF URIs with page and annotation parameters. The stable id is the Better BibTeX citekey supplied by Zotero, which the caller passes explicitly to the import method or picks through the dialog.

**Treatment opinion: author to the design and credit it.** Two constraints decide it. First, C5 fails outright: the plugin cannot run without the Obsidian desktop application, so it cannot be the agent's capture tool as installed, and its only non-interactive entry still needs Obsidian running. Second, the governing licence is GPL-3.0, with a conflicting MIT string in the manifest, so lifting the persist extension or the JSON-RPC client into the vault's tooling would carry copyleft onto anything distributed. What is worth taking is not code but the contract: the begin-and-end persist markers, the import-date trailer, the template data field names, and the JSON-RPC call inventory recorded in the facts below. Authoring a headless writer that emits notes in exactly that shape keeps every note interoperable with this plugin for users who also want the interactive path, and the marker regex and the method names are facts rather than copyrightable expression. If the vault later decides to run inside Obsidian anyway, install-as-is becomes viable for the interactive path while the headless tool stays format-compatible. Copy plus a delta was the alternative if code were to be lifted, but the copyleft cost and the fact that the 75-line persist mechanism is trivial to reimplement tip it to author-and-credit.

**Facts carried from this body.** Fifteen, and they are the run's densest Better BibTeX JSON-RPC inventory. The endpoint is `/better-bibtex/json-rpc` on the loopback address, port 23119 for Zotero, 24119 for Juris-M, else a supplied port (F1). The export method takes citekeys, a translator id and a library id, with one translator returning Better BibTeX JSON carrying an items array and another returning CSL JSON with issued date parts and a citation key; the client handles two result shapes, which proves the return shape changed across versions (F2). The citation-key method accepts identifiers of the form library-colon-key and returns a map to citekeys (F3). The bibliography method takes citekeys, an options object that either asks for quick-copy or names a CSL style, and a library id, and an empty result surfaces as a conversion error when no quick-copy style is set (F4). The collections method returns collection objects with a nested parent chain that can be walked into a full path (F5). The attachments method returns attachments carrying a path and native annotations with type, colour, text, comment, page label, position with page index and rectangles, an image path, tags and a modification date (F6). The notes method returns an object keyed by citekey whose values are arrays of note HTML (F7). The search method returns hits carrying a citekey and a library name rather than an id, and a groups method supplies the id by joining on name (F8). Better BibTeX also exposes a library export over HTTP whose CSL JSON entries carry a citation key and a title (F9). A liveness probe returns the bare string `ready` when Zotero and Better BibTeX are up (F10). Exported item JSON carries the citation key under either of two field names depending on version, so a robust reader must accept both (F11). The record also documents the Zotero URI forms for opening and selecting items in personal and group libraries, including a legacy form and an annotation deep link (F12); that Zotero note HTML embeds URL-encoded JSON provenance in annotation and citation attributes (F13); that the relations field is an object whose values are arrays of item URIs whose last path segment is the key (F14); and the marker contract a compatible headless writer would need (F15):

```
  static hasPersist(str: string) {
    return /%% begin (.+?) %%([\w\W]*?)%% end \1 %%/gi.test(str);
  }
```

Gotchas the record flags: only the first attachment that has annotations is exposed as the top-level annotations field, and other attachments' annotations are reachable only through the attachment array; persist regions re-append the rendered body on every import, which the project's own documentation demonstrates; the trailer reader anchors on end-of-file, so trailing text resets the last-import date to the epoch; the note-import path overwrites with no persist protection; and the template environment disables auto-escaping and overrides member lookup to block prototype access.

### 24. 54yyyu/zotero-mcp

Seeded. `https://github.com/54yyyu/zotero-mcp`. Pin `3cb3e2e34fab1fab7dc252102b03cdeec9915b78`, main HEAD, the release commit for v0.11.0 of 2026-08-25; the PyPI package is `zotero-mcp-server`, and the registry manifest in the tree still declares 0.9.1. Kind: an MCP server in Python, plus a standalone command-line tool and a packaged agent skill that an install command copies into place.

**Maintenance.** Last push 2026-08-25T02:00:54Z; 4,897 stars, 390 forks, 80 open issues, not archived; 622 commits from 2025-03-22 to 2026-08-24. Five releases in August 2026 alone. Top contributors are 302, 52, 24, 22 and 22 commits, so it is single-led with real outside help. The release commit body reports 2,727 tests passed, 42 skipped, none failed, and is co-authored by a model. The changelog follows Keep a Changelog with an upgrading note per version.

**Originator and supplier.** The licence names "Zotero MCP Contributors" as the copyright holder while the package metadata names 54yyyu as author. The supplier is the GitHub repository, the PyPI distribution and container images. Third-party components are not restated in the body: a PDF inspection wheel, pyzotero, and the annotation binary from another author downloaded at runtime.

**Licence.** MIT, found, at `LICENSE` lines 1-21, with the package metadata and the README agreeing. No per-file SPDX headers.

```
MIT License

Copyright (c) 2025 Zotero MCP Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software [...] subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
```

IP assertions: none beyond the notice. The holder and the author are named differently, which is worth carrying if the code is copied.

**Verify.** Two passes ran, three rows each, none refuted. Both re-fetched the client at the pin and found the local-connection docstring verbatim at line 243, with the supporting environment check and client construction present as described. The full 21-line licence text was confirmed at the pin in both passes, with the record's elided quote matching lines 1-13. Pin confirmed in both, one pass noting that the head of main returns the same SHA and that the release commit body carries the test tally the record quotes.

**Smallest part.** `src/zotero_mcp/better_bibtex_client.py`, 450 lines importing only standard library modules and a request library, with no intra-package imports: a self-contained Better BibTeX JSON-RPC client covering a probe, the citation-key, export and attachments methods, plus annotation normalisation and markdown rendering. Two other pieces are equally separable: `src/zotero_mcp/extract.py` at 362 lines, the PDF, HTML and text to markdown seam with form-feed page separators, and `src/zotero_mcp/identifiers.py` at 81 stdlib-only lines, a DOI normaliser. The only managed-region code in the body is a 35-line upsert helper in the skill installer, which could be lifted for note regions.

**Fitting.** *Inputs:* environment variables select local read mode, with an optional web API key and library id enabling hybrid writes, an optional database path, a search backend selector, a toolset selector, and WebDAV settings for remote files. Arguments are eight-character item, attachment and collection keys, Better BibTeX citekeys, identifiers or files for adds, and one-indexed page ranges. Preconditions are a running Zotero desktop with the local API enabled, Better BibTeX optional, and a config file written by a setup command. *Outputs:* markdown on standard output by default, with a documented item block, full text under a heading, and annotations as blockquotes with colour, kind and page; with a JSON flag, one envelope per call carrying an ok flag, the command name, a schema number and either data or an error, with configurable item projections; metadata, full text, annotations and BibTeX each have their own JSON shape. MCP tools return the same strings, and MCP resources serve item text. *Invocation:* install from PyPI, run a setup command, then invoke the command-line tool with subcommands for search, metadata, full text, page-range reads, annotations, citekey search and paths, or run the MCP server over standard input and output or over HTTP. A skill installer targets Claude Code, an agents directory, Cursor, Windsurf and Gemini. A container mode runs the command-line tool. *Harnesses:* the command-line route is what the body itself recommends for agents with shell access; the MCP server serves several desktop clients; a Claude Code skill ships in the wheel, and Codex and other agents are served by a pointer block in an agents file plus a skill directory. There is no Obsidian integration or dependency.

**Surplus.** The semantic search index with several embedding backends and batch APIs is a cost only if its extra is installed, since the core install carries no machine-learning dependencies. The full write surface over the web API, at 5,679 lines, is helpful for write-back but requires web credentials and carries write risk and review surface. The open-access PDF cascade across four third-party services is helpful for filling missing PDFs at the cost of outbound calls. Citation tallies and retraction checks plus a related-papers service are helpful for enrichment, network-dependent, and off by default. The annotation binary downloaded from GitHub on first use is a cost. PDF geometry work behind an optional extra is neutral for capture. MCP prompts and resources are neutral, and the prompts are instruction strings that call no model. WebDAV downloads, feeds, library switching, a connector and a weekly schema refresh are neutral, and the refresh is an outbound call that can be disabled. The MCP tool surface costs about 13,400 tokens on the default profile, which the body itself mitigates by recommending the command-line route and a toolset switch. The large test suite is helpful for trust; the validation corpus of about 200 files is dead weight for an installer.

**Coverage.**

**C1 covers** (evidence). `src/zotero_mcp/client.py` line 243, the local client docstring, with the environment check at line 217 and the client construction at lines 230-236.

```
This client connects to the local Zotero instance running on port 23119.
```

Three local read paths exist in code: pyzotero in local mode against the loopback port with an HTTP/1.1-pinned transport; Better BibTeX JSON-RPC for citekeys, BibTeX export and attachments; and direct SQLite reads of the Zotero database through a reader that locates the file from the profile. Metadata comes from an item call, attachments from a children call and from the attachment tables, and annotations from a children call filtered to the annotation type through a two-hop walk from parent to attachment to annotation, with a Better BibTeX path and an optional binary fallback. The web API is optional and only required for writes.

**C2 partial** (evidence). `src/zotero_mcp/tools/_helpers.py` line 1776, the citekey result formatter, with the item markdown block and the annotation renderer.

```
lines = [f"# Citation Key: {citekey}", ""]
```

The body emits markdown for items, a citekey-headed block from the citekey search, full text under a heading, and annotations as blockquotes. It never writes a note file, never keys a file by citekey, and has no managed or free region for notes. The only managed-region primitive is the skill installer's upsert helper, which uses HTML-comment markers and replaces in place while preserving the rest, and it is used for agent pointer blocks rather than literature notes. An outer process can drive the JSON commands to assemble a note, but the note format and the region handling are for the caller to author.

**C3 partial** (evidence). `src/zotero_mcp/semantic_search.py` line 1940, the changed-items query, with the watermark call at line 2414 and the gating condition at lines 2380-2383.

```
changed_versions = self.zotero_client.item_versions(since=since_version) or {}
```

Version-based change detection exists but only inside the semantic-index updater, which keeps a per-library watermark, asks for the last modified version, requests versions since that point, and diffs current keys for deletions. It is gated behind several conditions, items read from SQLite are stamped with version zero because local items carry no version, and the local full-text path invalidates on the attachment file's modification time and size rather than on item version. No tool or command exposes a caller-visible what-changed feed, and there is no orphan or re-key detection for external notes. What a caller can use is that the metadata command returns the raw Zotero record and the full projection carries it, so version and modification date are obtainable per item for an externally built drift check.

**C4 covers** (evidence). `src/zotero_mcp/extract.py` line 174, the extraction call, with the dependency pinned in the package metadata at line 36.

```
result = pdf_inspector.extract_pages_markdown(path, pages=wanted)
```

PDF text is extracted in process by a core rather than optional dependency, whose docstring states that it runs in process. In local mode the full-text getter first resolves the attachment from the database and the storage folder and extracts locally, falling back to Zotero's own on-disk text cache, then to the Zotero full-text index, and finally to a download and parse. HTML snapshots go through a converter, and EPUB needs an optional extra. Page-range reads use the same seam. Pages are joined with a form feed so offsets map to pages. Extraction itself makes no network call, and OCR is only flagged, with the body noting that nothing reads the flag yet. A local page cap of 50 is configurable.

**C5 covers** (evidence). `pyproject.toml` line 89, the console script entry, with the container entrypoint and the JSON envelope definition.

```
zotero-cli = "zotero_mcp.cli_standalone:main"
```

A standalone command-line tool with a stable JSON envelope ships for shell pipelines, scheduled jobs and agents with shell access, and a container mode exists. The MCP server runs over standard input and output. No Obsidian dependency or reference exists in the source. The stated precondition is that local mode needs the Zotero desktop application running with its local API enabled, and the SQLite-backed reads open the database file directly.

**C6 covers** (evidence). `LICENSE` line 8.

```
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
```

Full MIT text is present and the package metadata and README agree. It permits use and modification.

**C7 partial** (evidence). `src/zotero_mcp/scite_client.py` line 39, the tally endpoint, with the tools that use it.

```
f"{_BASE}/tallies/{doi}",
```

Provided by the body: citation tallies and editorial notices covering retraction, correction and expression of concern, in an off-by-default toolset; a stdlib DOI normaliser and CrossRef resolution when adding items, batched fifty per request; a DOI-to-PMCID conversion, but only to locate an open-access PDF and never written back to metadata; duplicate detection by normalised title and DOI with a dry-run merge; a related-papers and coverage report; and schema-validated metadata writes including the native citation key field. Not provided: arXiv version update, PMCID write-back, DOI verification of existing items, and metadata format lint. Every write requires web credentials, because writes are routed to a write client and the local API is treated as read-only.

**D6 partial** (evidence). `src/zotero_mcp/skill_install.py` line 225, the Claude target, with the shipped skill body and the targets table.

```
dst = base / "skills" / SKILL_NAME
```

A real Claude Code skill with frontmatter and a reference file ships in the wheel, and an install command copies it to a project or user skills directory. Codex is served separately by upserting a pointer block into an agents file and placing the body in an agents skills directory. It is installable as-is, but its subject is library access, finding keys and acting on keys, rather than turning a captured source into vault pages, so it does not meet D6's digest purpose.

**D8 partial** (evidence). `src/zotero_mcp/tools/search.py` line 734, the citekey match, with the command-line mode flag.

```
if data.get("citationKey") == citekey or _helpers._extra_has_citekey(extra, citekey):
```

Citekeys are accepted as lookup keys, native field first and then an Extra-field line, and are preserved on BibTeX export and on BibTeX or CSL import. But the body's own stable identity is the eight-character item key, which its skill calls the currency of every command, and no page links or provenance markers are produced.

**D10 covers** (evidence). `LICENSE` line 5, the same MIT finding as C6.

```
Permission is hereby granted, free of charge, to any person obtaining a copy
```

**Treatment opinion: install as-is.** The reasoning is that for the capture lane this is a maintained MIT-licensed package whose command-line tool already delivers the local read, local extraction and headless operation behind a versioned JSON envelope whose contract states that additive changes are always allowed and removals are not, so the clean seam is to consume that JSON from a vault-side skill rather than vendor roughly 39,000 lines. What it lacks, a citekey-keyed note file with managed and free regions, a caller-visible change feed, and everything in the digest lane, is absent rather than half-built, so a fork would inherit maintenance without shortening the work; those layers are to be authored on top, keyed by the version and modification date from the metadata command and by citekeys from the BibTeX and citekey-search commands. If only the extraction or the Better BibTeX seam is wanted, those two files are self-contained enough to copy frozen. Costs to weigh before installing: it moves fast, with four releases in one month and a documented breaking default change in the latest; the write module and the MCP tool surface are large, avoidable by using the command-line route and disabling toolsets; optional heavy extras must simply not be installed; a runtime binary download backs the annotation fallback; and there is a body-internal inconsistency, because the Better BibTeX annotation path still calls a method the same module and its tests describe as no longer existing, so in practice the local-API children call is what runs. Pin the version in any install.

**Facts carried from this body.** Twenty-one, and this record is one of the two main sources behind the Zotero facts section below. The load-bearing ones: Zotero's local server speaks HTTP/1.0 only, so a client must be pinned to HTTP/1.1 or the local API answers 502 (F1); the local API is single-threaded, and the body serialises all access behind one lock with a bounded wait (F2); this body treats the local API as read-only and routes every write to the web API, implementing none of the local-API write semantics (F3); the local API has a citation engine but rejects Atom, so content-based bibliography requests return a 501 while include-based ones and a top-level BibTeX format are served locally with no credentials (F4); for a linked attachment the local API answers the file endpoint with a redirect to a `file://` URL that the HTTP client refuses to follow, so the body reads the path from SQLite instead (F5); Zotero writes a plain-text full-text cache beside each indexed attachment, which is flat extractor output mostly without page separators (F6); server-side full text is read through a full-text call that returns a content field (F7); item JSON carries a native citation key field, which the body reads first and writes through an update parameter, with no Zotero version stated (F8); Better BibTeX auto-pins citekeys from metadata on creation and, per this body, offers no programmatic refresh path in the 9.x line (F9); the Better BibTeX JSON-RPC inventory as used here, including the named-parameter form of the citation-key method and two translator identifiers (F10); the search method is described as no longer existing and yet is still called in two places (F11); trashed items are not indexed and return a null citekey (F12); each library has its own monotonically increasing version counter, and items read from SQLite carry no version (F13); an immutable SQLite read cannot see rows still in an un-checkpointed log (F14); annotations are children of the attachment rather than of the parent item, and only three attachment content types carry them (F15); attaching a file does not bump the parent's modification date, so date-based change detection misses new attachments (F16); the SQLite date field stores an ISO prefix plus the original text while the web API returns only the display half (F17); collection deletion does not cascade to items, so an item's collection array can hold dangling keys (F18); local API enablement lives under advanced settings, with the toggle wording differing by Zotero version, and the local API defaults to library id zero (F19); collections are per-library while tags are database-wide (F20); and the pyzotero floor for a custom transport is 1.8.0, with this body pinning a later version because it raises on rate limiting instead of returning the error body as data (F21).

The record's own caveats: the README says Zotero 7 in one place and quotes a Zotero 9 toggle in another while code comments reference Zotero 8, so the body does not pin behaviour to Zotero 10; the registry manifest version disagrees with the package version; and a grep confirms no vault-note writer exists anywhere in the source.

### 25. cookjohn/zotero-mcp

Found in the capture sweep. `https://github.com/cookjohn/zotero-mcp`. Pin `5b0640f0f39f9ecaaeaa76bbf7c43f76bcef9599` on main, package version 1.6.0. Kind: a Zotero plugin, distributed as an installable add-on and built with the standard plugin scaffold, that embeds a streamable HTTP MCP server inside the Zotero desktop process.

**Maintenance.** Pushed 2026-09-03T11:24:58Z; 1,128 stars. Some metadata is stale: the packaged add-on file in the tree is older than the package version, and the server's own advertised version and repository URL are hard-coded to values that do not match this repository. Issue numbers in code comments show active issue-driven fixes.

**Originator and supplier.** The licence names "the Zotero-MCP project contributors" while the package metadata names cookjohn, who is also the GitHub owner. The server information block hard-codes a third name and an organisation URL that is not this repository, which the record reads as stale or aspirational metadata rather than a claim by the Zotero organisation.

**Licence.** MIT, found, at the root licence file and a byte-identical copy inside the plugin directory, verified with a diff, with the package metadata and the API SPDX id agreeing.

```
MIT License

Copyright (c) 2024 the Zotero-MCP project contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software ...
```

IP assertions: none beyond the notice.

**Verify.** One pass ran; no row was refuted. The pass confirmed the licence text at the pin and re-resolved the pin.

**Smallest part.** The PDF processor module of about 260 lines: a self-contained wrapper over Zotero's bundled PDF worker that handles the differences between the Zotero 7-to-9 worker and the Zotero 10 worker in URL, action name and asset callback, depending only on the Zotero and toolkit globals. A second candidate is the client configuration generator, which holds config templates for several agents. In practice the unit of adoption is the built add-on, because every tool runs inside Zotero's process.

**Fitting.** *Inputs:* MCP JSON-RPC over streamable HTTP to a loopback port, defaulting to 23120, with a session header managed by the server. Tool arguments use eight-character item keys, an optional library id, a content mode, include flags and an output format. Twenty-eight tools cover libraries, search, annotations, item details, content, collections, full text, abstracts, semantic search, and a write set. *Outputs:* JSON tool results with documented shapes for item details, content, annotations and writes, or plain text when the format is set accordingly. *Invocation:* install the add-on in Zotero, enable the server in preferences, then register it with the agent, for which the body generates the exact command for Claude Code and the exact TOML block for Codex, plus a health-check request. Zotero desktop must be running. *Harnesses:* Claude Code over native HTTP MCP, Codex over TOML, and several desktop clients through a remote shim, all generated by the configuration module. It is not an Obsidian plugin and not a command-line tool. The manifest declares support from Zotero 7 through 10, and the PDF module gates the Zotero 10 path on a major-version check.

**Surplus.** Semantic search with several embedding endpoints is a cost: optional cloud egress of full text if a key is set, background indexing, and an extra database in the Zotero data directory, all disableable by a preference that also filters the tools. The write tools, with a deferred committer so slow observers do not block responses, are helpful for enrichment and import when wanted, and a cost because an unauthenticated local endpoint can mutate the library once writes are enabled, which they are not by default. Collection management tools are neutral for capture. Content modes with intelligent truncation are a cost, because the default mode caps attachment text at 3,000 characters and the truncation is otherwise silent. PDF text post-processing is a cost for page-locator provenance, because it removes form feeds and strips repeated lines. A cached full-text database tool is neutral to helpful. The configuration generator and first-install prompt are helpful. Optional remote binding is a security cost if enabled and is off by default. Webpage-snapshot and HTML extraction are helpful for non-PDF sources. A six-locale preference interface is neutral.

**Coverage.**

**C1 covers** (evidence). `src/modules/annotationService.ts` line 227 for annotations, `src/modules/apiHandlers.ts` line 194 for metadata, and the item formatter at lines 62-135 for attachments.

```
const annotationItems = attachment.getAnnotations();
```

It reads item metadata, child attachments and PDF annotations from the local Zotero. The mechanism differs from the requirement's parenthetical: it is in-process through Zotero's internal JavaScript API, not the local API on 23119 and not Better BibTeX JSON-RPC, and it exposes its own server on an adjacent port. It never touches the Zotero web API. The item-details tool returns the key, item type, a Zotero URL, type-aware fields, creators, tags, notes and attachments, and the annotations tool returns identity, type, content, colour, tags, keys, page and modification date.

**C2 does not** (evidence). `src/modules/itemFormatter.ts` line 50, the identity it emits, with the note-writing path.

```
zoteroUrl: `zotero://select/library/items/${item.key}`,
```

There is no citekey concept anywhere in the body: a grep across the source for the citation-key field names and for Better BibTeX returns nothing. Items are keyed by the eight-character Zotero item key. Output is JSON tool results or plain text, and the only write path converts markdown to HTML and stores it as a Zotero note. There is no managed-and-free region concept and no markdown file emission. An agent could be driven to assemble a note from two tool calls, but the tool does not emit one and cannot supply the citekey; the caller would have to map the item key to a citekey through Better BibTeX. A pinned citation key in the Extra field would pass through, because Extra is in the preview field list, but the tool does not parse it.

**C3 partial** (evidence). `src/modules/streamableMCPServer.ts` line 1550, the complete-mode attachment of the item's API JSON, with a date filter and a sort field in the search engine.

```
result.apiJSON = item.toJSON();
```

Per-item modification date and version are obtainable inside the API JSON in complete mode, and a modified-date range filter exists in the search engine; the search tool passes all arguments through, so that filter reaches the handler even though the tool schema does not advertise it. There is no since parameter, no library-version endpoint and no deleted-items feed, so orphan and re-key detection are not directly supported, and per-item drift detection is possible only by polling.

**C4 covers** (evidence). `src/modules/pdfProcessor.ts` line 196, the local byte read, with the worker URL selection at line 39, the action name at line 206, and the cache-first path in the extractor at line 534.

```
const fileData = await IOUtils.read(path);
```

The content tool first reads Zotero's own full-text cache and then falls back to Zotero's bundled PDF worker running in process. The only HTTP requests in the PDF module fetch bundled assets from local resource URLs. There is no cloud call in the extraction path. Caveats: the default content mode truncates attachment text to 3,000 characters, so a complete mode must be requested for full text; the formatter replaces form feeds with paragraph breaks, which discards page boundaries and loses page locators; and a repeated-line heuristic may drop legitimate headers or footers. HTML and text attachments and webpage snapshots are also handled.

**C5 covers** (evidence). `src/modules/clientConfigGenerator.ts` line 57, the registration command, with the socket binding and the readiness wait.

```
return `claude mcp add --transport http zotero-mcp http://127.0.0.1:${port}/mcp`;
```

There is no Obsidian dependency anywhere, and it is driven from any MCP client over HTTP, including Claude Code and the Codex command-line tool. It is not headless with respect to Zotero: the server starts only after Zotero's interface is ready, so the desktop application must be running, which is inherent to any local-Zotero reader, but the process is Zotero's rather than a command-line tool's. There is no authentication on the endpoint, and the server states that CORS headers are not currently set.

**C6 covers** (evidence). Both copies of the licence file at line 5, with the package metadata.

```
Permission is hereby granted, free of charge, to any person obtaining a copy
```

MIT. The licence file is the artifact itself rather than prose describing behaviour.

**C7 partial** (evidence). `src/modules/streamableMCPServer.ts` line 2872, the translation search, with the duplicate check at line 3003 and the tool schema at lines 1081-1140.

```
const translate = new (Zotero as any).Translate.Search();
```

It provides identifier-based item creation across five identifier kinds, with existing-item and title-duplicate detection and a dry-run, plus a metadata write tool for field edits. It does not provide DOI verification of existing items, PMCID lookup, citation counts, arXiv version update, or metadata format lint. Write tools are hidden unless a preference is strictly true, and the preference interface describes them as disabled by default for safety. So the vault need not replicate identifier-driven import and deduplication, but must supply the lint and enrichment itself or get it elsewhere.

No digest-lane row is given. The record states that no D requirement is plausibly covered: the plugin produces no vault pages, has no template or charting notion, no cross-source pages, no content-hash idempotency, and is not a Claude Code skill or plugin but an MCP server registered with a command. Its closest touchpoints, attaching an existing markdown file to a Zotero item and converting markdown to a Zotero note, both write into Zotero rather than into a vault.

**Treatment opinion: install as-is.** The reasoning is that it is a released MIT-licensed add-on whose value is entirely in running inside Zotero, so forking or copying modules would mean maintaining a Zotero plugin, and the one module worth lifting only works inside Zotero anyway. Installed as-is it gives an agent local, cloud-free metadata, attachment, annotation and PDF-text reads over Claude Code's native HTTP transport. What it does not do, citekey-keyed markdown notes with managed and free regions, since-style change detection, and identifier lint, are things the vault would own regardless; the vault must map citekeys to Zotero item keys itself and must request the complete mode for full text. Two operational cautions before adopting: the endpoint has no authentication, so remote binding and writes should stay off unless needed, and the server exists only while the Zotero desktop application is running.

**Facts carried from this body.** Ten. Zotero 10 replaced the PDF worker with a unified document worker at a new URL with prefixed action names and a unified asset callback, while Zotero 7 through 9 use the older worker path (F1); the Zotero 10 asset layout splits character maps and standard fonts into a reader path and everything else into the worker path, and the fetch response must be a raw byte array (F2); in process, the full-text cache for an attachment is readable through a named Zotero call that returns an object with a content string (F3); linked-file attachments are supported only in the personal library, not in group libraries (F4); Zotero loads item data lazily per library, so items in libraries not opened in the session return empty fields unless data types are loaded explicitly (F5); Zotero's add-by-identifier pipeline is callable in process through a documented four-step sequence (F6); the plugin's default port is 23120, adjacent to Zotero's own 23119, and it binds loopback unless remote access is enabled (F7); the manifest supports Zotero 7 through 10 even though the README badge says Zotero 7 (F8); a separately published copy of the plugin exists under another account, MIT, capped at Zotero 9 (F9); and write tools are hidden from the tool list unless a preference is strictly true (F10).

### 26. alex-roc/zotero-agent

Found in the capture sweep. `https://github.com/alex-roc/zotero-agent`, distributed on PyPI as `zotero-agent` with the command `zot`. Pin `e6ba67c02d35c18c1a93f4cba42f01634406ea32`, main HEAD, committed 2026-08-25T02:31:00Z, one commit after the v0.8.5 tag. Kind: a command-line tool, plus an unsigned Zotero bridge add-on shipped as a release asset.

**Maintenance.** Last push 2026-08-25T02:31:05Z; 4 stars; latest release 2026-08-24; the changelog shows releases from 0.4.0 in July 2026 through 0.8.5 in August 2026. A single-maintainer project working directly on main, with continuous integration running 201 offline unit tests plus 18 PDF-library tests.

**Originator and supplier.** Alex Ojeda Copa is named as author in the package metadata, the copyright line says "zotero-agent contributors", and the supplier is the GitHub owner alex-roc, who also publishes to PyPI and a Homebrew tap.

**Licence.** AGPL-3.0-or-later, found, at `LICENSE` lines 1-2, the full unmodified text at 34,523 bytes with no project appendix, corroborated by the package metadata, a header in the package init file and the same header in the add-on bootstrap.

```
                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007
```

The relicensing is documented in the changelog for 0.4.0, which states that the licence is now AGPL-3.0-or-later, was MIT, that the table-of-contents feature is built on an AGPL library, and that releases 0.1.0 through 0.3.0 remain MIT and can still be used under those terms. The add-on manifest has no licence field. IP assertions: the copyright line and the author name, which differ in form from the supplier's account name. Copyleft attaches to derivative works, not to invoking the installed binary.

**Verify.** One pass ran; no row was refuted. Licence and pin confirmed at the pin.

**Smallest part.** `src/zotero_agent/resolve.py`, 32 lines mapping a citekey to a Zotero key through Better BibTeX JSON-RPC with an at-sign prefix forcing citekey interpretation, together with the three read helpers in `src/zotero_agent/http.py`: the URL builder, the list pager and the JSON-RPC caller. Together those give the whole local read path, meaning local-API reads plus JSON-RPC, in about 120 standard-library-only lines with no bridge add-on. The flat item shaper, which includes the citekey, is a second candidate. The record warns that copying these makes the recipient a derivative work under the copyleft, and that the annotations reader cannot be taken without the add-on.

**Fitting.** *Inputs:* an eight-character item key or a Better BibTeX citekey, a collection key or name, JSONL edit files for batch apply, an HTML or text file or standard input for note writing, a JavaScript file or inline snippet for the execution command, and a config file written by an init command holding a token, a user id and a base URL, all overridable by flags or environment variables. It requires Zotero 7.0 through 10 running with the local API enabled and the bridge add-on installed, plus Better BibTeX for citekeys. *Outputs:* text on standard output, or with a JSON flag one flat record per item carrying key, citekey, type, title, date, year, creators, venue, DOI, URL, tags and abstract, with a raw mode giving the Zotero wire JSON. Dedicated JSON shapes exist for attachment paths, annotations and citation lookups, and exports are available in six formats. Writes land inside Zotero as child notes, tags, fields, collections and attachments through the bridge. There is an append-only audit log, undo snapshots, and five documented exit codes. *Invocation:* subcommands with JSON, assume-yes and quiet flags, a ping command to verify connectivity, an MCP server over standard input and output, a skill installer that writes into the user or project skills directory, and an agents-file generator. Installation is through a Python tool installer, a package installer, Homebrew, or a checkout script, with the add-on installed from a release file inside Zotero. *Harnesses:* a Python command-line tool with a standard-library core and two optional extras, plus external tools for OCR and PDF work. Claude Code gets a bundled skill or an MCP registration; the Codex command-line tool gets an MCP entry or an agents file; several other clients are served over MCP. There is no Obsidian involvement. On the Zotero side the bridge add-on registers a POST endpoint guarded by a token header.

**Surplus.** The arbitrary privileged-JavaScript write path through the bridge is a cost: an unsigned add-on running arbitrary code inside Zotero, with a token in a private config file and an audit log. The capture set did not ask for it, and it is needed here only for annotations and attachment paths. Declarative batch edits with snapshot and undo are neutral for capture and helpful for library hygiene. Duplicate detection and merge is helpful as Zotero-side lint, at the cost that merges are irreversible. PDF outline reading and writing is neutral and modifies PDF files on disk. Scan preparation with splitting and OCR is helpful adjacent to local extraction, because it creates a text layer locally, at the cost of an external toolchain, minutes per book and a second attached PDF. Storage management is a cost, with lossy rewrites unrelated to capture. Metadata enrichment from two scholarly APIs is helpful for enrichment but makes network calls, which contradicts the project's own no-cloud positioning for that command. Import by identifier and open-access PDF fetch are helpful for library growth and go over the network through Zotero's translators. Tag management is neutral. Administrative commands are helpful operationally, though restart is disruptive. The MCP surface of about 21 tools is neutral. Storage-migration recipes are neutral. The packaging infrastructure is neutral.

**Coverage.**

**C1 covers** (evidence). `src/zotero_agent/http.py` lines 36-43, 46-76 and 192-206, with the default base in the constants and the bridge-driven readers in the read commands.

```
    url = "%s/api/users/%s/%s" % (cfg["base"].rstrip("/"), uid, path.lstrip("/")) || DEFAULT_BASE = "http://localhost:23119" || url = cfg["base"].rstrip("/") + "/better-bibtex/json-rpc" || "var anns = pdf.getAnnotations().map(function(a){ return { type:a.annotationType, page:a.annotationPageLabel, color:a.annotationColor, text:a.annotationText||'', comment:a.annotationComment||'' }; });\n" || out.push({ attachmentKey: att.key, path: att.getFilePath(), title: att.getField('title'),
```

Three local mechanisms, all on the loopback port. Item metadata, collections, tags, search and bibliographies come from local-API GET requests. Citekey resolution and attachment paths come from Better BibTeX JSON-RPC. Attachment file paths and annotations come only through the bridge add-on's privileged-JavaScript endpoint. No web API appears anywhere in the source. One caveat: annotation reading depends on installing the write-capable unsigned add-on, and every command calls a configuration check that fails without a bridge token, so even pure local-API reads need the init command to have run.

**C2 does not** (evidence). `src/zotero_agent/commands/write.py` lines 742-743 and 729-730, with the flat item shaper; a grep of the source, the skill, the documentation and the agents file for markdown, Obsidian and literature note returned no hits.

```
        "  var exists = parent.getNotes().map(function(i){return Zotero.Items.get(i).getNote();})\n" / "    .some(function(n){ return n === html; });\n" || if "<" not in html: / html = "".join("<p>%s</p>" % line for line in html.splitlines() if line.strip())
```

Nothing in the body emits a markdown file. The only note-writing path writes HTML into Zotero as a child note, which is the reverse direction from a vault. Its idempotency flag compares the whole note body for exact string equality rather than splitting a managed region from a free one. The flat item JSON carries a citekey an external writer could key on, but that is an input to a note rather than a note. Floor requirement not met.

**C3 does not** (evidence). `src/zotero_agent/http.py` line 62, the only response header read, with the recent-items sort and the undo snapshot; a grep for since parameters, version headers, modification dates and item versions returned no hits.

```
        if total is None and headers.get("Total-Results") is not None: || params = {"sort": "dateAdded", "direction": "desc"} || "for (var k of keys){ var it=await Zotero.Items.getByLibraryAndKeyAsync(lib,k); if(it) snap[k]=it.toJSON(); }\n"
```

The only header the local-API client reads is the total-results pagination header. The recent command sorts by added date, not modification date. The snapshot captures item JSON solely for undo and is never compared for drift. No per-item version, since parameter or modification-date logic exists, so drift, orphan and re-key detection are not provided.

**C4 partial** (evidence). `src/zotero_agent/pdf/scan.py` line 162 and `src/zotero_agent/pdf/prep.py` line 413, with the skill's own statement of the shipped path.

```
    total = sum(len(doc[i].get_text().strip()) for i in range(doc.page_count)) || args = ["ocrmypdf", "-l", language] || PDF as a normal file on disk, so once you have its path you read it with your
own PDF-reading tool — no OCR pipeline, no extraction step.
```

Local, no-cloud text extraction code exists, both a PDF library's text call behind an optional extra and OCR through a local subprocess, but it is consumed internally for the text-layer verdict, contents-page parsing and heading candidates rather than exposed as a PDF-to-text command. The shipped path for full text is to print the local path and let the agent's own reader open it. The search command passes only a query to the local API, which is Zotero's index rather than extraction. So the extraction capability is present locally and the emission is absent.

**C5 covers** (evidence). The bridge's headless tolerance, the console entry point, and the non-interactive flag.

```
    win = Zotero.getMainWindow();\n  } catch (e) {\n    /* headless */ || zot = "zotero_agent.cli:main" || common.add_argument("-y", "--yes", action="store_true", help="assume yes; don't prompt for writes")
```

A pure command-line tool with a standard-library core, a JSON flag and an assume-yes flag for non-interactive agent use, plus an MCP server over standard input and output. There is no Obsidian involvement anywhere, and the bridge tolerates the absence of a main window. The constraint is that the Zotero application itself must be running, because both the local API and the bridge endpoint live inside it.

**C6 covers** (evidence). `LICENSE` lines 1-2 with the package metadata line 10.

```
                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007 || license = "AGPL-3.0-or-later"
```

The licence permits use. Running the installed binary from a vault workflow imposes no obligation on the vault; copying source into the vault repository would make it a derivative work under the copyleft.

**C7 covers** (evidence). `src/zotero_agent/commands/features.py` line 6, the enrich summary, with the match verifier, the CrossRef call and the lint command.

```
- enrich: fill missing DOI / date / abstract from Crossref / OpenAlex. || def verify(item_title, item_year, item_surname, candidate,\n           min_similarity=MIN_TITLE_SIMILARITY): || data = _try_json("https://api.crossref.org/works?" + q) || "var out = { total: items.length, combinedCreators: [], noDate: [], noCreators: [], duplicateTitles: [] };\n"
```

The inventory the vault would not need to replicate: an enrichment command that fills missing DOI, date and abstract, looking up items with a DOI exactly and others by title search gated by a verifier requiring high title similarity, a year within one, the first author's surname present, and rejection of vague titles, with a higher floor when uncorroborated, all snapshotted for undo; a lint command reporting combined creator fields, missing dates, missing creators and duplicate titles; a missing-field lister; a duplicate detector with identifier-first verdicts and a reviewable merge plan; identifier-based import through Zotero's translators; an open-access PDF fetch; and tag normalisation. Absent: PMCID lookup, citation counts, arXiv version update, and metadata format lint beyond one regex. One honesty note the record makes: the enrichment command calls two external APIs, so the project's no-cloud claim does not hold for that command.

**D1 partial** (claim). The skill's summarize-then-save procedure and the project's own statement about where intelligence lives.

```
zot note <ITEMKEY|@citekey> --file summary.html   # add a child note || The CLI never calls an LLM: it exposes these primitives, and the agent (skill /
MCP) supplies the intelligence (which items, which values, which tag mapping).
```

The skill documents a bottom-up summarize-then-save workflow in prose and the note command ships the write path, but the summary is authored by the agent and the destination is a Zotero HTML child note rather than a vault page. The tool emits no per-source page.

**D6 covers** (evidence). `src/zotero_agent/assets.py` line 41, the skill installer, with the skill frontmatter and the documented install and Codex configuration.

```
def install_skill(dest, force=False, link=False): || ---\nname: zotero || zot skill install              # -> ~/.claude/skills/zotero || [mcp_servers.zotero-agent]\ncommand = "zot"\nargs = ["mcp"]
```

This is the capture skill rather than a digest skill, recorded here only because the mechanism satisfies D6's form: a Claude Code skill bundled in the wheel and installed as-is into the user or project skills directory. Codex compatibility, recorded separately, is either an MCP entry in the Codex config or a generated agents file.

**D8 partial** (evidence). `src/zotero_agent/resolve.py` lines 29-31 with the flat item shaper at line 27.

```
        if r.get("citekey") == ck or r.get("citation-key") == ck:\n            item_id = r.get("id", "")  # e.g. http://zotero.org/users/2960998/items/WD7FCHBW\n            return item_id.rstrip("/").split("/")[-1] || "citekey": d.get("citationKey") or None,
```

Every command accepts a citekey as the stable id and every JSON item carries it, with shipped tests covering resolution. But there are no page links or provenance markers, which belong to a vault writer this tool does not include.

**D10 covers** (evidence). The package metadata and the licence file, the same reading as C6, whose quote is the C6 block above: the licence permits use and modification, and derivative works must carry the copyleft.

**Treatment opinion: install as-is, conditionally, and never as the sole capture tool.** The reasoning has four parts. First, the licence decides the form: the copyleft permits invoking the installed binary with no obligation on the vault, whereas copying any module, even the roughly 120-line read path, makes the vault a derivative work, so copying is the wrong shape here. Second, what it gives the capture lane is the local read, headless operation and the enrichment set with real code and shipped tests, plus a stable JSON item shape keyed by citekey and a one-line attachment path lookup. Third, what it does not give is the C2 floor, because there is no markdown literature note and no managed region and the note command writes into Zotero in the reverse direction, and C3, because there is no version or since handling, with C4 only partial. A vault-side writer must own the note and the drift detection regardless. Fourth, the condition: the bridge is an unsigned add-on running arbitrary privileged code inside Zotero, and in this body it is the only route to annotations and attachment paths, while even pure local-API reads refuse to run without a bridge token. If the vault needs annotations, installing as-is is defensible with the security model read. If metadata and citekeys suffice, the local API and JSON-RPC can be reached directly in a few dozen standard-library lines authored independently, and the add-on is unneeded attack surface, in which case taking nothing is the better answer for this candidate. Maintenance is a single-maintainer project at 4 stars, active through the read date.

**Facts carried from this body.** Fourteen. The local HTTP API is read-only by design on Zotero 7 and 9.x, returning a 400 with a specific message for POST and offering no preference to enable writing, a claim the body scopes to those versions and does not state for Zotero 10 (F1); Better BibTeX JSON-RPC writes almost nothing, only two named methods, and the older debug bridge no longer exists in the 9.x line (F2); the two JSON-RPC methods used here return records carrying a citekey under either of two field names and an item URI whose last segment is the key, and attachment records carrying a path (F3); Better BibTeX keeps a separate export cache that can serve stale citekeys and is not invalidated by regenerating keys or restarting Zotero, so its export may disagree with a direct read (F4); local-API item JSON carries the citation key in its data object, and in process the Better BibTeX key is read from a key manager, with no version stated for when the API field appeared (F5); the bridge declares compatibility from Zotero 7.0 through 10 while the README says tested through 9.x (F6); the local API is enabled by a preference that is on by default (F7); the local API's native BibTeX and RIS exporters cap at one page and the collection items endpoint does not see into subcollections, so the body pages by key and names items explicitly (F8); Zotero's own server rejects cross-origin requests, closing the connection on a browser origin and returning 400 on a spoofed host, and binds loopback only by default (F9); annotations live in the Zotero database rather than in the PDF, so they survive a rewritten file but do not follow a re-attached processed PDF (F10); intercepting the save method as a dry run leaks writes on Zotero 7, confirmed by a tag that stayed on an item (F11); a bootstrap add-on registers a local endpoint by assigning into the server's endpoint table after initialization resolves, with a declared method and data type and an init function returning status, content type and body (F12); searching for an empty field does not work because Zotero does not store an unset field as an empty string, so the reliable pattern filters on the field value (F13); and Zotero checks plugin updates once every 24 hours, with update manifests able to carry an enforced hash (F14).

### 27. PiaoyangGuohai1/cli-anything-zotero

Added by the critic pass, which named it as the closest unread candidate to the local-read-plus-headless half of the missing seam and asked whether anything in it emits a vault-side citekey-keyed note. `https://github.com/PiaoyangGuohai1/cli-anything-zotero`. Pin `e42a930e9374422c9966a38e477adec71436a61e`, package version 1.2.1. Kind: a Python package and command-line tool that ships one skill file and a Zotero bootstrap add-on called the JS Bridge.

**Maintenance.** Last push 2026-07-28T08:07:24Z; 132 stars at read time.

**Originator and supplier.** The licence appendix names the HKUDS CLI-Anything Team, and the README credits an upstream framework by that organisation. The supplier is the repository owner PiaoyangGuohai1, and the package metadata gives the author as "cli-anything contributors". The distribution is on PyPI.

**Licence.** Apache-2.0, found, at `LICENSE` lines 1 and 178-201, with the package metadata agreeing and the API SPDX id confirming.

```
                                 Apache License
```

```
   Licensed under the Apache License, Version 2.0 (the "License");
```

IP assertions: the licence appendix copyright line is unfilled boilerplate with the placeholder brackets still in place, reading "Copyright [2026] [HKUDS CLI-Anything Team]". There is no notice file and there are no per-file copyright headers. Because the supplier and the named holder differ, the record advises honouring the attribution obligation to both names if code is copied.

**Verify.** No verify pass ran on this record. It was read after the critic pass, so every row rests on the first read alone.

**Smallest part.** `cli_anything/zotero/utils/zotero_sqlite.py`, about 29 KB and standard-library-only. It is the one module that can be lifted whole: it imports nothing from the package, opens the live Zotero database read-only, and encapsulates the schema knowledge that is the expensive part. That knowledge is a base item select joining the item, type, note, attachment and annotation tables with correlated subselects for title, DOI, date and a has-PDF existence test, plus item resolution, child fetching, attachment path resolution that expands the storage prefix into a real path, collection and saved-search readers, and a note HTML to text converter. If a capability rather than a module is wanted, a 34-line citation-metrics module or the per-source open-access URL builders are next. Not separable: the bridge client, which is inert without the shipped add-on.

**Fitting.** *Inputs:* command-line arguments only. Item references accept an eight-character key, a title fragment or a numeric identifier; collection references accept a key or a numeric identifier. There is no config file, and behaviour is tuned by environment variables for embeddings and for a model key. Ambient inputs discovered at runtime are the Zotero profile directory, the database file, the storage directory and the loopback port. A session file holds the current library, collection and item across invocations. Note content comes from a flag or a file in text, markdown or HTML. *Outputs:* standard output only, plus a few explicit file writes. A root JSON flag gives structured output per command; item JSON carries identifiers, type, dates, a sync version, title, DOI, a has-PDF flag, kind flags, a parent identifier, note and annotation text, an attachment path, and fields, creators and tags when related data is included. The file outputs are a bibliography export, JSON resume state, document outputs, and a profile preferences file. No markdown file is ever written. Write operations append to a local audit log. *Invocation:* install from PyPI and run the command, or the module. The skill's recommended opening move is a doctor command in JSON mode, acting on its next steps if the tool is not write-ready. Bridge commands require a one-time add-on install that builds an add-on file into the profile and needs a manual install step in Zotero the first time. There is also an interactive shell. *Harnesses:* command-line first and harness-agnostic, usable from Claude Code, Codex, Cursor or a plain shell. A skill file ships inside the package but is not wired into any skills layout, so adopting it means copying the file. MCP is explicitly deprecated, with the final MCP release named in the README. There is no Obsidian integration. The hard runtime prerequisite is a running Zotero desktop.

**Surplus.** The document citation pipeline, roughly 90 KB across four modules and about a third of the codebase, is a cost: nothing in either lane asks for manuscript writing, it dominates the skill file an agent would load into context, and its dynamic mode drags in an office-suite dependency chain. Arbitrary privileged JavaScript execution inside Zotero is a cost: the shipped add-on registers an endpoint whose handler evaluates the request body with Zotero's full privileges, surfaced to users as a command, so installing the capture tool means standing up an unauthenticated local endpoint that any local process can drive, and the JavaScript is string-interpolated from Python with ad hoc escaping. Semantic search and embeddings are a cost, requiring an index and an embedding service for a capability neither lane requested. The model call-out command is a cost, putting a cloud round trip inside a tool the vault would otherwise treat as strictly local, and competing with the vault's own digest step; its local sibling is the useful half. The write and import surface is neutral to cost: neutral if unused on a read-only path, a cost in that delete and merge and experimental direct database writes give an agent library-mutating power the capture role does not need, mitigated by confirmation gates, a dry-run-by-default merge and the audit log. The interactive shell and its terminal chrome are neutral dead weight for headless use. The frozen legacy MCP server is neutral, but worth knowing so that stale MCP advice about this project is recognised. The skill self-generator is helpful as a pattern, an independently useful technique for keeping a skill file in sync with a command tree, and surplus as a feature.

**Coverage.**

**C1 covers** (evidence). `cli_anything/zotero/utils/zotero_sqlite.py` lines 375-376 inside the base select, reached through the children command; the local-API path is in the catalog module at line 46 and the HTTP helper at line 12.

```
            an.text AS annotationText,
            an.comment AS annotationComment,
```

Three local backends, all on the loopback interface and none of them the web API: a read-only SQLite read of the live profile, which is what most read commands use; Zotero's local API under a personal-library scope with an API version header, used for quick search, CSL rendering and export; and the repository's own add-on exposing an evaluation endpoint. Item metadata, attachments with a resolved path, and annotations are all reachable. One defect is worth recording: neither annotation path is complete. The SQLite path returns untruncated annotation text and comment but the base select carries no page label, colour or annotation type, while the documented annotation commands go through the bridge, which carries type, colour and page but truncates the highlight to 200 characters. No path yields full annotation text together with a page locator. The SQLite annotation route is also undocumented, and because annotations are children of the attachment it takes two hops.

**C2 does not** (evidence). `cli_anything/zotero/core/notes.py` lines 151-152, the note write, with the format option in the command surface.

```
        f"note.setNote('{safe_html}'); "
        f"await note.saveTx(); "
```

This is the critic's question and the answer is unambiguous: nothing emits a vault-side note, and the note command writes into Zotero. The markdown format is an input format only, routed through a markdown-to-safe-HTML converter and pushed through the bridge as a Zotero child note. A case-insensitive grep across the whole repository for citekey, citation key and Better BibTeX returns zero hits. There is no citekey concept, no Better BibTeX integration, no managed-region marker and no markdown file writer. The only files written are a bibliography export, JSON resume state, document outputs and the profile preferences file. The nearest miss, recorded so it need not be re-checked, is a context command that builds a plain-text prompt blob keyed by the eight-character item key, with no citekey, no markdown structure and no region markers; it could be piped into a caller-owned writer, but the note-emitting half would be entirely the caller's. Floor requirement not met.

**C3 partial** (evidence). `cli_anything/zotero/utils/zotero_sqlite.py` lines 332-333 in the base select, surfaced by the item-get command through a normaliser that passes the whole row through.

```
            i.dateModified,
            i.version,
```

The raw signals exist and are emitted: every item row carries a modification date and the Zotero sync version, and the normaliser passes the row through to JSON, so a caller can diff them. But the tool does no change detection: there is no since parameter, no versions format request anywhere, no last-modified-version handling, and no drift, orphan or re-key logic. The title search only orders by modification date. The caller would have to store and compare versions itself.

**C4 does not** (evidence). `setup.py` lines 67-70, the dependency list, contrasted with the bridge's full-text search condition.

```
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
    ],
```

There is no PDF-to-text extraction anywhere. A grep for the usual PDF libraries returns only an unrelated helper in the model-API module. Dependencies are two packages. The full-text search command does not extract text: it asks Zotero's own prebuilt index through a search condition and returns matching items rather than text. The local API's full-text endpoints are never called. The nearest offering is location rather than extraction: a file command returns the resolved absolute path so an external tool can open the PDF.

**C5 covers** (evidence). `cli_anything/zotero/skills/SKILL.md` line 11, with the console entry points.

```
Agent-native CLI for Zotero 7/8/9 desktop. 40+ commands across four backends.
```

A shipped console script with a root JSON flag for machine-readable output on every command. There is no Obsidian dependency of any kind, and no reference to Obsidian, a vault or a REST plugin anywhere in the repository. It runs headless from a shell or an agent. Two hard prerequisites are its own and are Zotero-side rather than Obsidian-side, so they do not break C5: the desktop application must be running, stated as a hard prerequisite and not optional, and the bridge add-on is required, though only for bridge commands, since the pure-read paths do not need it.

**C6 covers** (evidence). `setup.py` line 39 with the full text at `LICENSE` lines 1-201.

```
    license="Apache-2.0",
```

Apache-2.0 permits use, modification and redistribution. The manifest field and the licence file agree. The obligations if copied are to retain the licence, state changes and preserve attribution notices, which is complicated here by the unfilled copyright placeholder and the two candidate holders.

**C7 partial** (evidence). `cli_anything/zotero/core/hygiene.py` line 1, with the metrics endpoint and the source cascade.

```
"""Library hygiene: duplicates by DOI/title and merge helpers."""
```

What it provides, so the vault need not replicate: duplicate detection by normalised DOI and normalised title with a dry-run merge preview and a confirmation gate; citation counts and related metrics from a keyless government API, resolved from a Zotero item by reading a dedicated identifier field with a free-text fallback; an open-access PDF acquisition cascade across four sources with per-collection batching and resume; an environment doctor; and an append-only audit log of writes. What it does not provide, so the vault still owns these: DOI verification, since DOIs are only read and normalised and never checked against a registry; a standalone PMCID lookup, since those appear only inside one URL builder; arXiv version update, since a version suffix is captured but nothing updates a stale version; and metadata format lint. Two of those capabilities make outbound calls to third parties, so they are not offline-safe.

**D6 partial** (evidence). `cli_anything/zotero/skills/SKILL.md` lines 1-5, the frontmatter, with the packaging that includes it.

```
---
name: cli-anything-zotero
description: >-
  Full-featured CLI for Zotero reference management.
```

A cross-lane row, because this is the one digest requirement the body plausibly touches. It does ship a well-formed skill file with name and description frontmatter and 285 lines of command guidance, decision flows and constraints, and a generator regenerates it from the command tree by walking the source. But it is not installable as a skill as-is: the file lives inside the package, there is no skills tree, no plugin manifest, and no instruction anywhere telling a user to copy it into a skills directory. A caller would copy it manually. It is also a capture-tool brief rather than a digest implementation, and it describes no page emission. Codex compatibility rests on a README claim that the tool works well for several agents, which is prose; the mechanism is a plain console script, so it is harness-agnostic in practice.

**D10 covers** (evidence). The same Apache-2.0 finding as C6, recorded for the digest lane because D10 asks the same question. It permits both use and modification.

**Treatment opinion: copy plus a delta, scoped to one module rather than the package.** Against install-as-is: the critic's question is answered negatively, since the candidate contributes nothing to the note-emitting half of the missing seam, so that half stays fully unbuilt whichever way this lands, while its local-read half arrives with a defect the vault would have to work around anyway, because no single path gives full annotation text together with a page locator. Adopting the whole tool would also mean standing up the privileged evaluation endpoint and carrying the document pipeline. Against taking nothing: the SQLite module is genuinely worth having and is legally clean to take, being standard-library-only, importing nothing from the package, needing no add-on, and encoding the schema knowledge that is the real expense, including the join, the storage-path expansion, the exposure of a modification date and a version, and the handling of ambiguous keys across libraries. The delta is small and well defined: extend the base select with the annotation columns the bridge path already proves are available, so that one read yields text plus locator, and add the citekey source the module has no concept of, since Zotero's own database as read here does not carry one and Better BibTeX keeps citekeys in its own store. Under Apache-2.0 this needs the licence retained, changes stated, and attribution to both named parties. Separately worth a look for its own sake and unrelated to either lane: the skill generator that regenerates a skill file from a command tree. If a shipped tool rather than a module is what is wanted, install-as-is is defensible for pure-read metadata and attachment-path capture, which needs no add-on, but it would not close the note-emitting floor and would not fix the annotation seam.

**Facts carried from this body.** Fifteen, named by their own identifiers rather than numbered. The local API is off by default and is enabled by a profile preference the tool writes, and a 403 on a GET is the specific signal that the local API is disabled as opposed to Zotero not running. The local API is addressed with an API version header and a personal-library scope of `/api/users/0`, with group libraries the other case and anything else raising, on the default port. Quick search is driven by a query plus a mode parameter against the top-items endpoint, with three scopes exposed. A bootstrap add-on can register an arbitrary endpoint on Zotero's built-in server, and this project's add-on uses it to evaluate caller-supplied JavaScript with full privileges, which is the mechanism behind every write and every annotation and full-text read in the tool. The add-on declares compatibility from Zotero 6.999 through 9.0, which is Zotero 7, 8 and 9. Zotero's internal search API exposes full-text content and annotation text as conditions, so both searches can run against Zotero's own index without extracting any text, though the results are identifiers rather than text. PDF annotations hang off the attachment rather than the top-level item and carry type, text, comment, colour and page label, living in a dedicated table with text and comment columns. A stored attachment's path column uses a storage prefix that resolves to a path under the data directory keyed by the attachment key. The item table carries both a modification date and a sync version per item, and libraries, collections and saved searches carry versions too, which is the raw material for since-style change detection without the web API. Zotero 7 and later store one identifier as a dedicated field rather than only in the free-text block, though the tool keeps a fallback. A keyless government endpoint returns four citation metrics by identifier. A practical open-access cascade is implemented across five sources with specific URL forms. This project's MCP server is frozen at a named version. And one fact that sits in tension with the Zotero facts section below:

```
0
```

That is the output of a repository-wide case-insensitive grep for citekey, citation key and Better BibTeX at the pin, in a project that reads the local SQLite schema, the local API item JSON and CSL-JSON exports. The record reads it as corroborating that citekeys are Better BibTeX's rather than Zotero's. The Z register's own reading, from the schema commit, is that `citationKey` is a native Zotero item field. Both observations stand as recorded: this project never looks for the field, which is not the same as the field being absent. The tension is left open rather than resolved.

### 28. retorquere/zotero-better-bibtex

Seeded. `https://github.com/retorquere/zotero-better-bibtex`. Pin `cfdba6ac507a0b49a99d4b23fc4fed359edebc5d`, master HEAD of 2026-09-04, package version 9.0.63; the release tag for that version is a different, earlier commit, and the record confirms that the key-regeneration method is already present at the tag. Kind: a Zotero add-on installed into Zotero 8 through 10 that exposes HTTP endpoints on Zotero's built-in server.

**Maintenance.** Pushed 2026-09-04T17:29:40Z; 7,089 stars; latest release 2026-08-26; default branch master; the add-on declares a minimum Zotero version of 8.0.1 and a maximum of 10; continuous integration runs behaviour tests against a real Zotero under a virtual display.

**Originator and supplier.** Emiliano Heyns, both, distributed as a release asset.

**Licence.** MIT, found, at `LICENSE` lines 1-21, with the licence detector agreeing.

```
MIT License

Copyright (c) 2016 Emiliano Heyns

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software [...] THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

The package manifest declares a different permissive licence at line 7, which the record notes as a mismatch and resolves in favour of the licence file for the distributed source. IP assertions: the copyright line, plus translator manifests naming three creators for one translator. No patent or trademark assertions.

**Verify.** One pass ran, with an empty rows array, so no coverage row was re-checked. Licence and pin were both confirmed: the licence file at the pin is verbatim MIT with the same copyright line, and a comparison against master returns identical with zero commits ahead or behind, so the pin is upstream master, with the package version confirmed on the same line the record cites.

**Smallest part.** The JSON-RPC endpoint itself, consumed over HTTP. It runs inside Zotero and cannot be extracted. The second-smallest useful piece is the pull-export endpoint that takes comma-separated citekeys and a translator.

**Fitting.** *Inputs:* JSON-RPC over HTTP POST, or GET with the request JSON as the bare query string, to the endpoint on the loopback port; parameters may be positional or named, with named mapped onto positional through a generated schema, and batch arrays are accepted. Inputs are citekeys with a leading at-sign stripped, library selectors by name, numeric id or a wildcard for some methods, item keys in a library-and-key form, translator names or identifiers, and CSL style identifiers. The pull endpoint takes its own query parameters. *Outputs:* per method. Search returns CSL-JSON objects plus a library name and a citekey. Attachments returns per-attachment objects with a deep link, a local file path, and full annotation JSON with parsed positions and an image cache path for image annotations. Notes returns note HTML keyed by citekey. Collections returns collection JSON keyed by citekey. The citation-key method returns a map from item key to citekey or null. Key regeneration returns a map from old key to new key or null. Export returns translator output as a string. The Pandoc filter method returns an errors map and an items map. There are also bibliography, groups, AUX-scan, auto-export, viewer and readiness methods. *Invocation:* any HTTP client. The documentation shows a curl form, the shipped test harness uses Python, and a Pandoc Lua filter calls the filter method. *Harnesses:* any HTTP client. It is not a Claude Code skill or plugin, not an Obsidian plugin and not a Codex tool; it is an add-on inside a running Zotero desktop. Obsidian is not required.

**Surplus.** Auto-export with a keep-updated option and optional git commit and push of the export directory is a cost if enabled unintentionally, because it commits whatever is staged in that clone, and neutral otherwise. The cite-as-you-write picker endpoint with several output formats is neutral for capture and helpful if interactive citation insertion is wanted. The AUX scanner is neutral. The Pandoc Lua filter is helpful as a worked client example. The export translators with scripting hooks are neutral for a markdown vault. The citation-key pattern engine with transliteration and duplicate postfixing is helpful, because it is the citekey originator the vault keys on. An error-report upload is a user-triggered network call and neutral. The import translators are neutral. Journal abbreviation, title-case warnings and a quality report are helpful lint the vault need not replicate.

**Coverage.**

**C1 covers** (evidence). `content/json-rpc.ts` line 787, the registration, with the server helper, the attachment method at lines 261-308 including the file path and the annotation read, the notes method, and the search method that returns CSL-JSON plus a citekey.

```
Server.register('/better-bibtex/json-rpc', Handler)
```

The code registers a handler on Zotero's local HTTP server, on the port from Zotero's own preference. Search returns CSL-JSON metadata plus a citekey and a library name; attachments returns a local file path, a deep link and full annotation JSON, including an image cache path for image annotations; notes returns note HTML; collections returns membership. All reads are against the running local Zotero rather than the web API, and the desktop application must be running.

**C2 does not** (evidence). `translators/Collected notes.ts` line 98, the markdown conversion, with the quick-copy translator's link form.

```
if (this.translation.collected.displayOptions.markdown) this.markdown = turndown.turndown(this.html) || let keys = items.map(item => `[[@${ item.citationKey }]]`)
```

Nothing in the body emits a literature note or knows about a managed region against a free region. The nearest ingredients are a collected-notes translator that produces HTML for an item's title, extra, notes and attachment notes and can convert it to markdown, with no per-file split and no region markers; quick-copy strings in a wikilink form and a select-URI form; an export method returning bibliography or JSON text; and a templating format on the picker. A caller must assemble the note itself. Because this is a floor, the ingredients earn no partial credit.

**C3 partial** (evidence). `content/json-rpc.ts` line 591, the errors map in the Pandoc filter method, with the serialized export type carrying dates, the key-regeneration signature at line 483, and the notifier registration.

```
result.errors[citationKey] = found.length
```

Orphan and duplicate detection per citekey is available through the filter method's non-throwing errors map, where zero means the citekey was not found and more than one means duplicates; the export method throws on the first missing key, so it is not a detector. Re-key is exposed as an old-to-new map. Drift can be approximated by comparing modification dates from a JSON export. No per-item Zotero version and no since parameter is exposed. The add-on's own change detection feeds auto-export scheduling and is not queryable. One caveat recorded in the facts: key regeneration saves with a flag that skips the modification-date update, so the modification date will not reveal a re-key.

**C4 does not** (evidence). `content/json-rpc.ts` line 274, the attachment path; a repository-wide grep for extraction helpers finds only an unrelated log-line regex.

```
path: att.getFilePath(),
```

The attachments method returns the local file path and the annotations, rendering image annotations through Zotero's own worker, but no text extraction exists anywhere in the body. The caller must run its own PDF-to-text on the returned path.

**C5 covers** (evidence). `test/features/steps/steps.py` lines 590-594, the shipped test client, with the documented curl form and the virtual-display CI.

```
response = requests.post(
    'http://127.0.0.1:23119/better-bibtex/json-rpc',
    json={'jsonrpc': '2.0', 'method': method, 'params': json.loads(params), 'id': 1},
    headers={'Content-Type': 'application/json'},
)
```

The shipped test harness drives the API from Python over HTTP with no Obsidian, and the documentation shows curl. The precondition is that the Zotero desktop application with the add-on loaded must be running, since the endpoint lives on Zotero's server, which is the data-source precondition rather than an Obsidian dependency.

**C6 covers** (evidence). `LICENSE` lines 1-3.

```
MIT License

Copyright (c) 2016 Emiliano Heyns
```

MIT permits use. The manifest's differing declaration is also permissive, so the discrepancy is recorded and does not affect permission.

**C7 partial** (evidence). `content/inspire-hep.ts` line 42, a lookup by identifier, with the quality-check helper, the duplicate tagger, a title-case preference, arXiv identifier regexes and a citation-graph translator.

```
const citekey = parse(type, id, await (await fetch(url, { method: 'GET', cache: 'no-cache', redirect: 'follow' })).json())
```

It provides a physics-database key lookup by identifier, which is a user-triggered network call; a quality report checking identifier and date validity and missing required fields in export output, emitted only when a preference is on; duplicate-citekey tagging; a title-case warning on import and save; arXiv identifier parsing for export fields; a DOI-and-URL export policy; journal abbreviation; and a citation-graph translator. It does not provide DOI resolution or verification, PMCID lookup, citation counts, arXiv version update, or a general metadata format lint. The vault should not replicate duplicate-key detection or the identifier checks, and must still own the enrichment.

No digest-lane row is given: the add-on originates the citekey but does not write or reference vault pages.

**Treatment opinion: install as-is.** The reasoning is that this is a Zotero add-on, MIT-licensed and actively maintained, with a stable HTTP interface, so there is no code to copy or fork and the vault consumes it over the loopback interface. It is the citekey originator and the only local source that returns annotations, note HTML, attachment paths, collection membership and an old-to-new re-key map keyed by citekey, so it satisfies the local-read, headless and licence floors and parts of change detection and enrichment. It does not write literature notes and does not extract PDF text; those must be authored vault-side on top of its methods. The record's closing preference is to use JSON-RPC rather than reading the Zotero database directly.

**Facts carried from this body.** Twenty, and with the key-manager read below they are the primary source for the Z7 register entry. The method inventory at 9.0.63 is six namespaces and fourteen methods (F1). The auto-export API is add-only, with no list, remove or run over JSON-RPC (F2). The citekey pin store is now Zotero's native field: the in-memory key map is loaded by a SQL join on the field name, and the changelog records both that the add-on is now strictly Zotero 8 and later and that the native field is hidden and replaced by one at the top of the pane, so there is no separate pin store any more (F3):

```
JOIN fields f ON id.fieldID = f.fieldID AND f.fieldName = 'citationKey'
```

Legacy pin locations are still parsed, meaning citation-key and BibTeX lines in the Extra field, plus a pinned column in the old add-on database used only by the one-time migration (F4). The key-regeneration method returns a map from the input citekey to the new one or null, with null only when the input cannot be resolved and an unchanged key echoing the input, and read-only library handling is deferred to a named issue (F5). Key generation and regeneration save with a skip-modification-date flag, so a vault using that date for drift will not see re-keys and must use the regeneration map or the citation-key method instead (F6). Named parameters are mapped onto positional ones through a generated schema and unknown names are rejected (F7). Batch arrays are handled, and GET is supported with the request JSON as the bare query string (F8). The port comes from Zotero's own preference rather than being hard-coded, with a different default documented for the Juris-M fork (F9). Since a named Zotero version the local endpoints reject browser access while programmatic clients work (F10). Library scoping differs per method, with export resolving a single library and three other methods accepting a wildcard (F11). The attachments method returns a deep link per attachment and, for image annotations, a rendered image cache path (F12). The pull endpoint takes comma-separated citekeys and a translator and, with a filter-data flag, returns items, a Zotero map and errors (F13). Search returns CSL-JSON plus a library name and a citekey, and plain-string search also matches the citation-key field while excluding feeds and attachments (F14). Keys for read-only group libraries are cache-only shadow keys never written into Zotero's field (F15). Change detection is internal, registered through Zotero's notifier over six types and feeding auto-export scheduling, and is not exposed over JSON-RPC (F16). CSL JSON export can carry a Zotero URI and item id under a custom key when a display option is set (F17). The quick-copy translator emits wikilink and select-URI forms keyed by citekey (F18). Serialized export items carry item key, item id, library id, URI and both dates, plus attachments with a local path and notes, and the Zotero version is not in the typed shape (F19). And the supported Zotero range for the current add-on is 8.0.1 through 10 (F20).

### 29. windingwind/zotero-better-notes

Found in the capture sweep. `https://github.com/windingwind/zotero-better-notes`. Pin `4215a882e9f3528ddd4820c20b2c29e732c14e7e`, master HEAD of 2026-08-24, release tag and package version 3.3.3. Kind: a bootstrapped Zotero add-on in TypeScript.

**Maintenance.** Pushed 2026-08-24T13:21:23Z; 8,172 stars; the latest release is the same day as the pin; default branch master.

**Originator and supplier.** windingwind, both, distributed as a release asset.

**Licence.** AGPL-3.0, found, at `LICENSE` lines 1-2, the stock 661-line text with the template copyright line left unfilled, and the package manifest declaring the or-later variant.

```
GNU AFFERO GENERAL PUBLIC LICENSE
Version 3, 19 November 2007
```

The record records the discrepancy that the licence file is the plain version 3 text while only the package manifest says or-later. The add-on manifest has no licence field, and a grep found no per-file headers. IP assertions: none beyond the licence terms. The bootstrap file credits Zotero's own example add-on as the origin of most of that file. The record notes that this is strong copyleft: use is unrestricted, but copying code into a non-copyleft vault tool would bind that tool.

**Verify.** One pass ran; no row was refuted. Licence and pin confirmed at the pin.

**Smallest part.** The sync state model, taken as a design rather than as code: the sync status record shape carrying a path, filename, two hashes, a last-sync stamp and an item id; the YAML frontmatter carrying a version, a library id and an item key, with the merge rule that user frontmatter keys survive except tags and dollar-prefixed keys; and the three-state comparison that yields up-to-date, note-ahead, markdown-ahead or needs-diff from the paired hashes plus the version. That is about 120 lines of logic with no dependency on the editor, the worker or the interface. The export templates look separable but execute only inside an installed copy, so they are not.

**Fitting.** *Inputs:* Zotero note items, meaning HTML wrapped in a schema-versioned container, selected in Zotero or passed by id; a sync folder chosen through a file picker or set programmatically through the sync API; existing markdown files with the three frontmatter keys, which the body parses; and user-editable templates in the template editor. *Outputs:* one markdown file per note at a template-rendered name, defaulting to a title and note key, with YAML frontmatter for tags, parent title and collections plus the three system keys; images copied into an attachments folder under the sync directory; and on import, a new or updated Zotero note. Document, PDF, LaTeX and mind-map exports also exist. *Invocation:* from JavaScript inside Zotero only, through a documented API surface for export, import, sync, templates and conversion. Auto-sync runs on a timer while Zotero has focus and on item-modify notifications. The README points to a separate automation add-on as the entry point for scripting. *Harnesses:* a Zotero desktop add-on with a manifest declaring 8.0-beta.21 through 10.99.99. None of Claude Code, Codex, Obsidian or a command line, and no HTTP surface of its own.

**Surplus.** The note editor enhancements are a cost: a large surface unrelated to capture, all loaded into Zotero. The workspace window with an outline pane and graphs is neutral, being interface-only and untouched by API calls. Note-to-note links with their own URI scheme and a relation index are neutral and off by default. Exports to four other formats, one of which calls Better BibTeX over JSON-RPC, are neutral for capture, though that call is a useful worked example. A quick-note button in the reader sidebar and annotation tag sync are helpful as capture primitives if the vault's unit were the Zotero note, and otherwise neutral. The template picker and editor with community sharing is helpful, because the same templates drive the exported file's name, header and content. An integration hook for another add-on is neutral. The sync manager window with a folder scan that re-attaches existing files by their library and item keys is a helpful rediscovery pattern, but it is keyed by note key.

**Coverage.**

**C1 covers** (evidence). `src/utils/annotation.ts` line 17 for annotations, with the template documentation's worked attachment and metadata examples.

```
const annotationJSON = await Zotero.Annotations.toJSON(annotationItem);
```

It reads item metadata through template variables with field, creator and tag accessors, attachments through a best-attachment call and a PDF check with image attachments resolved by path, and annotations through Zotero's own JSON serialiser, all from the local Zotero. Access is in process, plugin JavaScript against Zotero's item API, rather than through the local API port or Better BibTeX. That is more local than either listed mechanism, but it means an external process can reach this data only by triggering plugin code inside Zotero.

**C2 partial** (evidence). `src/modules/template/data.ts` line 44, the default filename template, with the whole-body note write on import, the frontmatter merge rule, the YAML wrapper and the refresh module.

```
text: '${(noteItem.getNoteTitle ? noteItem.getNoteTitle().replace(/[/\\\\?%*:|"<> ]/g, "-") + "-" : "")}${noteItem.key}.md',
```

Three facets. On keying, it emits one markdown file per note, named by title and note key, which is the note's own Zotero key rather than the parent item's citekey. The filename template receives the note item, so a parent citekey could be used, but no shipped example does this, and that sub-point is a claim rather than evidence. The rediscovery scan matches only files whose stem ends with the note key, so a citekey-named file is found only through the stored preference and never by a directory scan. On the managed split in the file body, there is none: import replaces the whole note body and export rewrites the whole file. The only preserved region is the frontmatter, where user-added keys survive re-export unless the key is tags or dollar-prefixed. A managed-region mechanism does exist inside the Zotero note, where refresh-marked templates are wrapped in a delimiter pair and only the text between markers is replaced, but whether that wrapper survives a markdown round trip is not verified in the body and is left undetermined. Net: it can be driven to emit a citekey-keyed note, but the file itself has no managed-and-free body split.

**C3 partial** (evidence). `src/modules/sync/hooks.ts` lines 241-243, the version comparison, with the hash pair, the notifier filter and the rediscovery scan.

```
if (Number(mdStatus.meta.$version) !== noteItem.version) {
    noteAhead = true;
  }
```

Per-note change detection is real: the comparison checks the stored hash of the file body and of the note HTML plus the note's version against the version in the file's frontmatter, yielding the four states, a notifier on item modification triggers sync, and a periodic timer is configurable. The limits are that the notifier filters to notes only, so parent-item metadata drift is invisible; the rediscovery scan silently returns when the stored keys do not resolve to a note, so orphans are dropped rather than reported; and nothing handles a re-key. The body itself flags the note version as unreliable when the account is not logged in.

**C4 does not** (evidence). The annotation serialiser is the only text path; a grep across the source for extraction helpers hit only image-attachment copying.

```
const annotationJSON = await Zotero.Annotations.toJSON(annotationItem);
```

There is no PDF-to-text anywhere in the tree, and the module whose name suggests otherwise is note-to-PDF export. Text comes only from annotation JSON, meaning highlight text and comment. The template documentation's PDF snippet builds a link rather than reading the file.

**C5 partial** (evidence). `src/modules/sync/hooks.ts` lines 21-24, the auto-sync gate, with the import confirmation and the export file pickers.

```
if (
          Zotero.getMainWindow().document.hasFocus() &&
          (getPref("syncPeriodSeconds") as number) > 0
        ) {
```

There is no Obsidian involvement anywhere, so that half holds. Headless does not: the add-on runs only inside the Zotero desktop application, auto-sync fires only while the main window has focus, the import path raises a confirmation dialog when the note is newer than the file, and the export path opens file pickers unless the directory and filename are pre-supplied. Two API calls are dialog-free when fully parameterised, but they are reachable only from JavaScript executing inside Zotero. There is no command-line tool and no HTTP endpoint.

**C6 covers** (evidence). `LICENSE` lines 1-2 with the package manifest.

```
GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007
```

The licence permits use without restriction. Copyleft obligations attach only to distribution, modification or network service of derived works, and installing the add-on and calling its API from a script does not create a derived work. The version discrepancy between the two declarations is recorded.

**C7 does not** (evidence). The template documentation's DOI snippet with the only outbound call in the body.

```
[${topItem.getField("DOI")}]("https://doi.org/${topItem.getField('DOI')}") || method: "item.export" ... fetch(`http://localhost:${port}/better-bibtex/json-rpc`
```

There is no DOI verification, PMCID lookup, citation count, arXiv update or metadata lint. The DOI snippet is a field read into a link. The only outbound network call is to Better BibTeX to render a bibliography for one export path, guarded by an installed-extension check. A grep for the enrichment vocabulary found nothing else. There is nothing here for the vault to avoid replicating.

**D2 partial** (evidence). `src/modules/template/api.ts` lines 202-209, the item-template run, with the documented template type, stages and variables.

```
await runTemplate(
        key,
        "topItem, targetNoteItem, itemNotes, copyNoteImage, sharedObj",
        [topItem, targetNoteItem, itemNotes, copyNoteImage, sharedObj],
```

An other-lane row. Item templates are caller-authored per project with arbitrary field lists, filled per source item through field accessors or asynchronous script, with worked examples. That is a per-source structured template with caller-supplied fields, but the values must come from Zotero metadata or from a script, and there is no extraction of charting content from the source text. It fills the template shape rather than the charting content.

**D5 partial** (evidence). `src/modules/sync/hooks.ts` lines 250-263, the up-to-date return, with the hash computed through Zotero's own helper.

```
} else {
    // const maxLastModifiedPeriod = 3000;
```

An other-lane row. Unchanged content is a no-op by content hash, with both sides compared plus the version. The mechanism applies to note-and-file sync rather than to digesting a source document, so it is the pattern rather than the requirement.

**D10 covers** (evidence). The package manifest line 29 with the licence file, an other-lane row. The licence permits use and modification; modification plus distribution or network use requires releasing the derived work under the same terms, which is a cost if vault tooling is not.

```
"license": "AGPL-3.0-or-later",
```

**Treatment opinion: author to the design and credit it.** Install-as-is fails the lane on three counts: the sync unit is the Zotero note rather than the item, the markdown file is whole-file two-way with no free body region, and execution is bound to a focused Zotero interface with confirmation and picker dialogs on several paths. Fork or copy would carry the copyleft into vault tooling and drag in the editor and worker stack the converter depends on. What is worth taking is the design named in the smallest part: paired content hashes plus a version in frontmatter, three-state drift classification, and the frontmatter merge rule that preserves user keys except tags and dollar-prefixed ones. That is small enough to re-author cleanly under the vault's own licence with a credit line. If the vault's own drift model is already settled, the honest answer collapses to taking nothing.

**Facts carried from this body.** Nine. Better BibTeX JSON-RPC is reachable in process at the loopback address on the port from Zotero's own preference, and the export method takes citekeys, a translator and a library id (F1). Zotero items expose a native citation-key field readable both by a field accessor and as a property, and this body treats an empty string as no key (F2):

```
const citationKey = item_.getField("citationKey");
        if (citationKey === "") {
          ztoolkit.log("[Bid Export] Detect empty citationKey.");
```

An item's version is not a reliable change marker when the Zotero account is not logged in, which the plugin states in its own comment (F3). Zotero note HTML is wrapped in a schema-versioned container, and this body targets version 9 and strips and re-adds the wrapper when converting (F4). Four in-process helpers are named for hashing, annotation JSON, CSL conversion and citation formatting (F5). The add-on declares compatibility from 8.0-beta.21 through 10.99.99 (F6). Saving a note with a specific notifier field defers Zotero's own upload after a programmatic write (F7). Zotero's reader exposes a sidebar-header event for plugins to add per-annotation buttons (F8). And a spec-compliant conversion pipeline escapes Obsidian extended syntax typed as literal text, while task-list checkboxes are lost because the Zotero note editor has no checkbox element (F9).

The record also corrects its own launch description: the markdown side carries the three system keys in YAML frontmatter, while the schema-versioned container is the note-HTML wrapper on the Zotero side rather than something in the file. Sync state, meaning paths and hashes, lives in Zotero preferences rather than in the vault.

### 30. 917Dhj/DeepPaperNote

Found in the capture sweep. `https://github.com/917Dhj/DeepPaperNote`. Pin `e2de69483271e11f1eefcdc75b16cd57dac86733` on main, plugin and package version 2.3.0. Kind: a Claude Code skill, shipped as a dual-stack plugin with a Codex manifest alongside.

**Maintenance.** Last push 2026-09-04T07:16:37Z, whose commit message is a star-history chore; 1,034 stars at read time; continuous integration on two operating systems with a test run; a changelog maintained through the current version.

**Originator and supplier.** The copyright holder and package author is dingdingcar, while the repository owner and manifest author is 917Dhj. The Zotero local API client, which is the smallest separable part, was contributed by a third party through a named pull request, which the changelog credits.

**Licence.** MIT, found, at `LICENSE` lines 1-21, corroborated by both plugin manifests and the package metadata. No per-file headers.

```
MIT License

Copyright (c) 2026 dingdingcar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

IP assertions: only the copyright line. Because the supplier, the copyright holder and the contributor of the part worth taking are three different parties, all three should be credited if the client is copied. No contributor agreement, patent or trademark statements were found.

**Verify.** One pass ran; no row was refuted. Licence and pin confirmed at the pin.

**Smallest part.** The local API client in `skills/deeppapernote/scripts/_zotero_local.py`, 864 lines, of which the takeable core is the client class covering probe, item fetch, top-item search, children and the attachment file URL; the transport builder, which is proxy-free and no-redirect over the standard library; the HTTP status mapper; and the file-URL to local-path helpers. That core needs only two small helpers inlined from the shared module. The higher-level matching functions import eight helpers from a 148 KB shared module and are not freestanding. The mocked test file, with 29 test functions, ports with the core.

**Fitting.** *Inputs:* a paper reference in any of seven forms, including a Zotero item key or a select link, or a trusted JSON input record from a prior stage. Run overrides for language, save mode, vault, papers directory and Zotero mode are available through flags, environment variables or a user config file. *Outputs:* one markdown note per paper at a layered path under the vault, with YAML frontmatter, a paper-local images directory, and a hidden JSON sidecar carrying a source hash, a note stem, a per-language note record and a paper id. Intermediate JSON and JSONL artifacts land under a work directory, twelve of them named in the pipeline. The Zotero lookup emits a record with the item key, item type, version, attachment status and key, filename and a local PDF path. *Invocation:* a slash command in Claude Code, a dollar-prefixed command in Codex, or the Python scripts directly, with the pipeline run first, the model writing the note plan and note, and a preflight and formal save afterwards. Zotero-only pieces can be run alone, including an environment check that probes the local port. *Harnesses:* a Claude Code plugin manifest with auto-discovered skills and no marketplace file, plus a Codex plugin manifest with its own adapter file. The scripts are plain Python command-line tools usable from any agent or shell. Obsidian is a filesystem target only, with no application, URI scheme or plugin needed. Zotero desktop must be running with the local API enabled for the Zotero path, and the automatic mode falls back to web resolution when it is not.

**Surplus.** Web metadata enrichment across four scholarly services, with identity adjudication so web hits cannot override a Zotero match, is helpful for backfilling and costs outbound network calls on every run that is not fully disabled. Web PDF acquisition is neutral for a Zotero-first vault and costs a cloud fetch when no local PDF exists. Figure and table asset extraction with placement planning and image materialisation is helpful for presentation and costs large mandatory stages and an imposed images directory per paper. The multi-gate note pipeline, with grounding lint, final lint, a style gate, two review passes and a strict language contract, is a cost as a rigid seventeen-step workflow the agent must follow. Domain-folder routing with an editable taxonomy imposes subfolders unless overridden. Vault-wide save-target admission keyed by a PDF hash with a hidden sidecar is helpful for deduplication and costs hidden files in the vault and whole-file overwrite semantics. A companion glossary skill is neutral to helpful if terminology notes are wanted. An optional OCR path is helpful for scanned PDFs at no cost when absent. Bilingual output is neutral, with the Chinese-first reference prose a reading cost. The Codex manifest and adapter are helpful if Codex compatibility is wanted.

**Coverage.**

**C1 partial** (evidence). `skills/deeppapernote/scripts/_zotero_local.py` lines 339, 587 and 647, with the base URL at line 28 and three more endpoint constructions.

```
f"users/0/items/{key}/children", | if _item_data(item).get("itemType") not in {"", "attachment", "note", "annotation"} | if is_pdf_attachment(item)
```

A floor row. A shipped and tested read-only client hits the desktop local API on the loopback port: an item by key, a quick search on the top-items endpoint with a query and a mode, children, and a local PDF path through the file-view-URL endpoint. Item metadata and PDF attachments are read. Annotations and notes are not: search results of those types are dropped, and the attachment helper keeps only PDF children. There is no annotation endpoint, no annotation normalisation, and no Better BibTeX anywhere. So metadata and attachments yes, annotations no.

**C2 does not** (evidence). `skills/deeppapernote/scripts/common.py` lines 3169-3170, the path resolver, with the atomic write and the documented layout.

```
note_slug = slugify_filename(title) | target_name = filename.strip() or f"{note_slug}.md" | os.replace(temp_path, path)
```

A floor row. The note is keyed by a sanitised title slug in a folder per paper with a language suffix, not by a citekey. The internal paper id is auto-derived with one of four prefixes, and a grep for the citation-key names across the skills and tests returns no hits. There is no managed region: a grep for the usual marker vocabulary in the writer returns nothing, the writer replaces the whole file atomically, and an existing same-language note is either blocked or overwritten wholesale after a hash-bound confirmation. No preserved free region exists. Floor requirement not met.

**C3 does not** (evidence). `skills/deeppapernote/scripts/_zotero_local.py` line 459, the version copy.

```
record["zotero_version"] = version
```

The item wrapper's version is copied into the record, but a repository-wide grep shows it is consumed nowhere else in the scripts. There is no since parameter, no versions format and no last-modified-version handling, and no per-item modification comparison. The only change detection in the tool is on PDF bytes, used for vault save-target admission, which is vault-side rather than Zotero-side. Drift, orphan and re-key detection are absent.

**C4 covers** (evidence). `skills/deeppapernote/scripts/extract_source_text.py` lines 128 and 132, with the dependency declared in the package metadata.

```
doc = fitz.open(pdf_path) | {"page": page_index + 1, "text": doc[page_index].get_text("text")}
```

Page text is extracted locally with a PDF library, and the extraction script has no HTTP imports. The output is a sectioned JSONL file, a source manifest and an optional full-text markdown file. It extracts from the resolved local attachment path rather than from Zotero's full-text index. Optional OCR is probed but not required.

**C5 covers** (evidence). `skills/deeppapernote/scripts/run_pipeline.py` line 2 with the atomic write in the note writer.

```
"""Run the deterministic DeepPaperNote stages sequentially for one paper.""" | os.replace(temp_path, path)
```

All stages are Python command-line scripts driven by the agent, and the vault note is written through the filesystem with a temporary file and a rename. A grep across the scripts for the Obsidian URI scheme, the REST plugin port, the phrase for that plugin, and the Obsidian command-line tool returns nothing, so no Obsidian application or plugin is required at runtime. The companion skill only checks for a vault marker directory, likewise filesystem-only.

**C6 covers** (evidence). `LICENSE` line 1 with the package metadata reference.

```
MIT License
```

A floor row. MIT permits use, copying, modification and redistribution with notice retention.

**C7 does not** (evidence). `skills/deeppapernote/scripts/_zotero_local.py` line 2, the module docstring, with the web enrichment hosts in the shared module.

```
"""Read-only client and matching helpers for Zotero's desktop Local API."""
```

Nothing is written back to or linted in Zotero: the client is GET-only by construction. The tool does perform web metadata enrichment and validates a web DOI against Zotero's author and year before accepting it, which a named test covers, but that feeds the note's own metadata record only. So there is no Zotero-side enrichment for the vault to avoid replicating, and the enrichment it does is vault-side and listed under surplus.

**D1 covers** (evidence). `skills/deeppapernote/SKILL.md` line 3, the skill description, with the writer's docstring and the extraction call.

```
description: Generate a high-quality deep-reading note for a single paper and write it into an Obsidian-style vault. | """Write the final Markdown note into an Obsidian-style vault."""
```

An other-lane row. The whole product is a per-source page from a PDF: the scripts extract text, sections and figures and build a synthesis bundle, the model writes summary, contributions, method, results and limitations against a documented section order, and the writer saves it. The input must be a PDF, failing closed without one, and markdown sources are not accepted as the source document.

**D2 does not** (evidence). `skills/deeppapernote/scripts/localization.py` line 23, the English field tuple, consumed by the contracts module.

```
"core_info_fields": ("Title", "Translated title", "Authors", "Institutions", "Publication date", "Venue", "DOI", "arXiv", "Paper link", "Code / Project", "Data / Resources", "Paper type"),
```

An other-lane row. The structured metadata block and the section list are hard-coded per language and enforced by the lint script, and the skill instructs the model to use only the declared fields and order. There is no caller-supplied field list and no charting template mechanism.

**D3 does not** (evidence). `skills/deeppapernote/SKILL.md` line 44 with the agents file's explicit non-goal.

```
- it handles one paper at a time | - a multi-paper review framework
```

An other-lane row. There are no cross-source synthesis pages, no index, no append-only log and no contradiction handling. The optional companion skill accumulates term occurrences into shared glossary notes across papers, with a rule that existing notes are never replaced and only missing fields and an absent occurrence may be added, which is terminology accumulation rather than synthesis with an index and a log.

**D4 partial** (evidence). `skills/deeppapernote/scripts/create_input_record.py` line 2 with the skill's statement about trusted artifacts and the resolver's loaders.

```
"""Create a deterministic paper input record from trusted metadata such as Zotero results.""" | A trusted JSON artifact or explicit local PDF remains authoritative and bypasses this lookup.
```

An other-lane row. The pipeline accepts an externally produced JSON input record and an externally supplied PDF path, so it does not own creation of the source file. But it does not consume a markdown note written by another process as its integration input, and it owns creation of the note it writes. Ingest and digest are not separable at the note level.

**D5 partial** (evidence). `skills/deeppapernote/scripts/write_obsidian_note.py` lines 493 and 555, with the skill's instruction and the source hash.

```
admission = "reuse_source_directory" | conflict_code="same_language_note_exists", | when it returns `same_language_note_exists`, stop before drafting and ask whether to overwrite the reported note.
```

An other-lane row. Re-running on an unchanged PDF is detected by hash through the hidden sidecar and the run is blocked with an overwrite prompt rather than silently rewriting. It is not a no-op: four earlier pipeline stages re-run before the preflight, and the outcome is a stop-and-ask rather than a skip.

**D6 covers** (evidence). The project's own statement that the skill file is both workflow definition and entry point, with the plugin manifest name and the Codex manifest and adapter.

```
`skills/deeppapernote/SKILL.md` is both the canonical workflow definition and the Claude Code skill entrypoint. | "name": "deeppapernote",
```

An other-lane row. It ships a Claude Code plugin manifest with the skill under the auto-discovered directory and a slash command. There is no marketplace file in the tree, so installation is by a plugin directory flag or the documented package route. Prerequisites are a Python floor and the PDF library. Codex compatibility, recorded separately, is the Codex manifest plus the adapter, and the agents file calls the repository a dual-stack plugin.

**D7 covers** (evidence). The layout statement in the format reference with the writer's path flags and the default papers directory.

```
- the paper-local `images/` directory is part of the required note layout, not an optional optimization | p.add_argument("--papers-dir", default="", help="Vault-relative paper directory.")
```

An other-lane row. Layout requirements are explicit: a four-level path plus an images directory plus a hidden sidecar, with domain routing from a rules file. The vault, papers directory, subdirectory and filename are caller-chosen, while the folder per paper, the images directory, the sidecar and the domain subfolders are imposed. The reference's instruction to preserve an existing vault convention is prose only.

**D8 partial** (evidence). The writer's paper-id flag and the sidecar field, with the derivation in the shared module.

```
p.add_argument("--paper-id", default="", help="Canonical paper id.") | "paper_id": paper_id,
```

An other-lane row. A caller may pass a paper id and it is carried into the pipeline artifacts and the sidecar as provenance, but it is not used in note filenames, which are title slugs, or in wikilinks, which resolve by vault basename or by frontmatter aliases. There is no citekey concept.

**D9 does not** (claim). `skills/deeppapernote/SKILL.md` lines 181-182, the single-pass instruction.

```
- A normal note-generation request should complete in one pass: note text, figure placeholder decisions, image materialization when confident, and final save. | - Do not stop after a text-only draft just to ask whether the user wants figures inserted.
```

An other-lane row. The documented default is a single pass to the formal save with model-side gates only. Human intervention is requested only for a same-language overwrite or for an ambiguous identity. There is no configurable pre-integration human review and no batch mode.

**D10 covers** (evidence). `LICENSE` line 1, an other-lane row, whose quote is the C6 block above: MIT permits use and modification.

**Treatment opinion: copy plus a delta.** For the capture lane this candidate fails the note floor outright, with title-slug filenames, no citekey, no managed region and whole-file overwrite, and it is only partial on the local-read floor because no annotations or notes are read, while change detection and enrichment are absent. Installing the plugin as-is would bring the seventeen-stage digest workflow, the figure pipeline, the domain routing and the sidecar conventions, none of which the capture requirement asked for. What is worth taking is the hardened read-only client: a loopback-only base URL, a proxy bypass, a no-redirect transport, an API-version probe with status mapping, a quick search with a mode parameter, a children call, and a file-URL endpoint resolved to a validated local path with both path conventions handled, plus its mocked test suite. Copy that class and its transport and path helpers under MIT, crediting all three parties, then add the delta the set needs: fetch children of the annotation and note types, read the citation-key field from item data, add a since or version comparison for change detection, and pass results to a citekey-keyed managed-region note writer this candidate does not have. A fork is unnecessary because the delta is additive and the rest of the repository would be dead weight.

**Facts carried from this body.** Ten, named by their own identifiers, and this record is one of the two main sources for the local-API entries in the Zotero facts section. The local API is addressed at the loopback port under a user-library scope, and the client refuses non-loopback base URLs and group-library select links. Requests send an API-version header and no authorization header, and the root response is checked for a matching version and for a schema-version header, with a test fixture expecting a specific value. A 403 is interpreted as the API being disabled in Zotero settings, a 501 as an unsupported API version, and a 404 as item not found. The file-view-URL endpoint with a plain-text accept header returns a file URL that the client converts to an absolute local path, handling both path conventions and rejecting network paths, without fetching the bytes. Quick search runs on the top-items endpoint with a JSON format, a data include, a negated attachment type, a query and one of two modes, with identifier lookups using the broad mode and title lookups using the narrow one. The item wrapper carries a top-level version integer that the client copies but does not use for change detection. The item normaliser reads a documented set of fields and never reads a citation-key field, and the repository has no citekey concept. Local requests are built with an empty proxy handler and a no-redirect handler so system proxies and off-host redirects are never followed, with a named test for the latter. An attachment key given directly is resolved to its bibliographic parent through a parent field, and attachments without a parent are rejected. And a fallback discovery path without the API assumes one of two storage roots with one directory per attachment key.

The record also corrects the brief it was given: the client's test file holds 29 test functions plus one parameterisation rather than the 44 the brief stated. And it notes that the shared module is a 148 KB monolith that most scripts import, which limits detachability of anything beyond the client class.

### 31. urschrei/pyzotero

Seeded. `https://github.com/urschrei/pyzotero`, on PyPI and conda-forge. Pin `60c51812577baccbd20f2336cb863619c2e97980`, main HEAD of 2026-08-30, two commits past the 1.15.1 tag of the same day. Kind: a Python library, with optional extras adding a command-line tool and an MCP server.

**Maintenance.** Last push 2026-08-30T19:16:55Z; 1,404 stars; the latest release is the same day; twelve commits across two days adding local write support, new commands and an MCP migration. Sole author and maintainer, with a contributors file.

**Originator and supplier.** Stephan Hügel and the contributors, with a citation file carrying an identifier and a digital object identifier. One vendored module originates from a third party's file transport under a different licence. The supplier is the same person through three distribution channels.

**Licence.** Blue Oak Model License 1.0.0, found, at `LICENSE.md`, with the package metadata and the citation file agreeing.

```
Each contributor licenses you to do everything with this software that would otherwise infringe that contributor's copyright in it.
```

```
You must ensure that everyone who gets a copy of any part of this software from you, with or without changes, also gets the text of this license or a link to <https://blueoakcouncil.org/license/1.0.0>.
```

```
No contributor can revoke this license.
```

The GitHub API reports no assertion because it does not recognise this licence, while the file and the manifest are unambiguous. IP assertions: an explicit patent grant, "Each contributor licenses you to do everything with this software that would otherwise infringe any patent claims they can license or become able to license." The vendored transport module is BSD-3-Clause with its own notice in the file header and is not under the main licence.

**Verify.** Two passes ran, none refuted. Both confirmed the licence file's headings and the manifest declaration, and both re-resolved the pin.

**Smallest part.** The core client is not separable below the package, because the client class imports five sibling modules, so the smallest installable unit is the package with no extras, which drops the command-line and MCP dependencies. The smallest copyable snippets are the four shipped example scripts, each between about ten and seventy lines against a local-mode client. One helper module carrying local-key storage, a DOI index and creator formatting is standalone and could be copied on its own.

**Fitting.** *Inputs:* a running Zotero desktop, at least version 7 for reads and 10 for local writes, with the communication preference enabled, serving the local API. Item and collection keys and query parameters including a query string, a mode, an item type, a tag, a collection, a since value and paging. For writes, a local API key obtained through an authorisation call that raises a consent dialog, supplied directly, through an environment variable or through a config file written by an authorise command, plus an optional server id to skip the bootstrap request. *Outputs:* Python lists and dictionaries in Zotero's item shape; key-to-version maps for the versions format; a full-text structure with content and index counts; raw bytes from a file call; and a dump call that writes the attachment to disk. The command-line tool prints human text or JSON, with documented shapes for search, item and children. The MCP server returns JSON strings per tool across ten read tools, with write and delete tools behind flags. *Invocation:* the library API directly, the command-line tool with eight documented subcommands, or the MCP server over standard input and output. *Harnesses:* a Python library and command-line tool, plus an MCP server whose README example is a desktop client configuration; as a standard-input MCP server it is consumable by Claude Code and Codex equally, though the body names only the desktop client. There is no Obsidian coupling.

**Surplus.** The web API client is neutral, unused in local mode and costing only package size. The local write API, covering item and collection changes, tags and uploads, with key persistence, is helpful later if the vault wants to write back, and costs a consent dialog, key lifetime handling and concurrency preconditions. The scholarly-service integration is helpful for enrichment but is a cloud call with rate limits and coverage gaps. The MCP server is helpful for agent-driven capture and costs an extra dependency and a long-running process. Saved-search creation and deletion is neutral because there is no execution endpoint. Export-format processors are neutral in local mode, since one format is documented as unsupported locally and the others are unverified in the body. The file transport is neutral and adds a second licence to track. Item-schema lint for writes is helpful if the vault ever creates items.

**Coverage.**

**C1 partial** (evidence). `src/pyzotero/_client.py` line 87, the local endpoint, with the example scripts and the children command's enclosure read.

```
self.endpoint = "http://localhost:23119/api"
```

Item metadata and attachments are read from the local API by shipped code: the item, top, items and children calls are exercised in local mode by the four example scripts and by every command and tool, since both build clients through a helper that hard-codes local mode and the local library id; the file and dump calls fetch attachment bytes. Annotations are the gap: the only annotation-aware code is a write whitelist of field names, and no method, example, test or documentation reads annotation items, while the children command's docstring names only attachments and notes. Annotations would be reachable solely through the generic children call on an attachment key, which the body never demonstrates. This is not the web-API-only case: local is a first-class mode rather than a fallback.

**C2 does not** (evidence). `src/pyzotero/cli.py` item command and the MCP JSON helper; a grep of the source, the documentation and the README for markdown and the citation-key names returned no hits.

```
click.echo(json.dumps(result, indent=2))
```

All outputs are dictionaries in Zotero's item shape, JSON strings, plain-text listings, or raw bytes. There is no note template, no markdown emission, no citekey concept and no managed-region mechanism. The vault would own this layer entirely.

**C3 covers** (evidence). `src/pyzotero/_client.py` line 752, the last-modified-version read, with the versions-format calls at lines 729 and 739, the new-full-text call at lines 708-720 and the server-id property at lines 193-212.

```
lmv = self.request.headers.get("last-modified-version", 0)
```

The versions calls with a since parameter return key-to-version maps; a dedicated call reads the last-modified-version header; a new-full-text call lists attachments whose index changed; and item JSON carries both a version and a modification date. All send the server-id header in local mode, and the documentation instructs callers to partition stored versions by that id and discard on mismatch, with a dedicated error class. One caveat: a deleted-items call exists in the client, but the body never states that the endpoint is implemented by the local API, so orphan detection through it is unverified, while orphan detection through a full versions diff is available.

**C4 partial** (evidence). `src/pyzotero/cli.py` full-text command, with the same call in the MCP tool and the client method that builds the endpoint.

```
result = zot.fulltext_item(key)
```

Full text is obtained over the loopback interface with no cloud call, but the library does not extract it: it returns Zotero's own already-built index, with content and page counts. If Zotero has not indexed the attachment the call returns nothing and the command prints an error object. Two useful properties for the vault: the indexed and total page counts give a completeness signal, and the file and dump calls return the raw bytes so a local extractor can be run as a fallback. Search in the broad mode queries the same index.

**C5 covers** (evidence). The console script entries in the package metadata, with the MCP server's transport and the command group.

```
pyzotero = "pyzotero._entry:cli"
```

The library, the command-line tool and the MCP server all run from a terminal or an agent process, and nothing imports or depends on Obsidian. The one runtime requirement is that the Zotero desktop application is running with the local API enabled, which the README states along with the version floors.

**C6 covers** (evidence). The copyright section of the licence with the package metadata.

```
Each contributor licenses you to do everything with this software that would otherwise infringe that contributor's copyright in it.
```

The licence is permissive: use, modification and redistribution are granted with a notice-preservation obligation only. The vendored transport module is also permissive, is exercised only for file URLs, and carries its own notice in the file.

**C7 partial** (evidence). `src/pyzotero/semantic_scholar.py` line 16, the base URL, with the DOI helpers and six command-line subcommands.

```
BASE_URL = "https://api.semanticscholar.org/graph/v1"
```

What it provides, so the vault need not replicate: scholarly-service lookups for three count fields, citations, references, recommendations and paper search, each optionally annotated with in-library presence through a normalised-DOI index, which is a cloud call; DOI normalisation and a whole-library DOI-to-key index; and item field-name validation against the Zotero schema for writes. What it does not provide: DOI verification against a registry, PMCID lookup, arXiv version update, or lint of existing items' metadata format. This is a client library rather than a Zotero add-on, so the row records what its command-line and MCP layers provide.

No digest-lane row is given. The record states that no digest requirement is plausibly covered, since the library produces no pages, templates, synthesis or skill, and omits the rows rather than padding with negative ones.

**Treatment opinion: install as-is.** The reasoning is a permissive licence, an active project pushed on the day of the pin with twelve commits in two days, and a local mode that is first-class rather than bolted on: the endpoint switch, the server-id capture and partitioning, the disambiguation of three HTTP statuses, key persistence and the missing-template gap are all handled in code with tests. Nothing the set asks for requires modifying the library: the gaps, meaning a markdown note with a managed region, citekey keying, annotation reading and a PDF extraction fallback, are all a layer above the client and can be written against its public API. Installing without extras keeps the dependency small, and the command-line extra is worth adding only if the agent prefers shelling out to JSON. The record recommends one live probe, a children call on an attachment key, to settle the annotation question before treating the local-read floor as fully met.

**Facts carried from this body.** Twenty, and this record is the run's most detailed source on local-API write semantics. Local write authorisation is a POST to an authorise path with an application name, exposed as a client method (F1). The consent dialog offers three choices, where allow is one-time and always-allow is permanent (F2). The response carries a key and a remember flag, and when remember is false the key is valid for one write only, so the following write fails (F3). The key travels in a dedicated header, distinct from the web API's bearer scheme (F4). Writes without a server-id header are rejected with a 428, and the bootstrap endpoint is the API root with a trailing slash, because the bare path returns a 404 (F5). Three statuses are reused for several conditions and the plain-text body distinguishes them, which the error table maps to four named conditions (F6). One observation is recorded with its requirement left undetermined: the client sends a write-token header on creation in local mode too, because the header is set before the local headers are added, and the body never states whether the local API requires it (F7). Keyed local writes need a concurrency precondition, either a header or a version on each object, or the API returns a 428 (F8). Reads need Zotero 7 and local writes need Zotero 10, with the toggle under advanced settings (F9). Local-API versions are scoped to the server id, bear no relation to web versions, and are typically lower than pre-write-support values, so cached versions must be partitioned (F10). The full-text endpoint returns content plus either page or character counts depending on the document kind, and the same shape is accepted on write (F11). In local mode attachment children carry an enclosure link that the documentation describes as a local file path, though the body never shows the path form, and the file endpoint is also used for bytes (F12). Saved searches are listed, created and deleted, with no execution method, while six collection endpoints are wrapped (F13). There is no reference to a citation key anywhere in the body (F14). There is no reference to Better BibTeX, JSON-RPC, auto-export or key pinning anywhere in the body (F15). The documented differences from the web API are no item-template endpoint, an ignored locale parameter, no Atom, no rate limits on ordinary requests, and results not paginated by default (F16). Local deletes are permanent rather than trashed, and propagate on sync (F17). In local mode the second upload step posts to Zotero's own receiver rather than to cloud storage, and that endpoint needs the server id but not the key (F18). The documentation points at the Zotero-side source file that implements the local API, which is the primary source to confirm these against (F19). And the library persists the key and server id in a mode-restricted file under a config directory, with two environment variables overriding (F20).

The record is explicit that all of these are the library's own description of Zotero rather than Zotero's documentation, and names the Zotero-side file to confirm against. It also names two live probes that would close the remaining uncertainty: a children call on an attachment key to see whether annotation items are returned locally, and the concrete form of the enclosure link.

### 32. Mappedinfo/local-zotero-mirror

Found in the capture sweep. `https://github.com/Mappedinfo/local-zotero-mirror`, with the companion `https://github.com/Mappedinfo/local-zotero-bridge`. Pins: the mirror at `8e61e37e38e35759263ceee61a0cacc3a635ed80`, manifest version 0.1.14, committed 2026-06-07T13:46:31Z; the bridge at `59604a2b28839f141b8d4754fd3d43c0d4946a96`, manifest version 0.2.19, committed a minute later. Kind: an Obsidian plugin in TypeScript with an Obsidian-free shared core, plus a bootstrapped Zotero add-on in plain JavaScript.

**Maintenance.** Both repositories were pushed the same day, in lockstep; the mirror has 1 star and the bridge 4. Three smells are recorded: a hard-coded version constant in the bridge lags the manifest by two patch versions, the bridge README names the older release file, and the bridge's configuration, meaning the vault name, path and target folder, is a hard-coded literal with no preference read while the preferences file is a one-line placeholder. That last one means the Zotero-side open-in-Obsidian and search-pane features only work on the developer's own machine as shipped.

**Originator and supplier.** mappedinfo, both. The bridge's bootstrap file hard-codes a developer vault path, which suggests a single-developer project. Distribution is through a beta installer from releases for the mirror and through an update URL or a guarded install script for the bridge.

**Licence.** MIT, found, at each repository's licence file lines 1-13, identical in both, with the API reporting MIT for both. Neither manifest nor package file carries a licence field.

```
MIT License

Copyright (c) 2026 mappedinfo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

IP assertions: only the copyright line in each repository. No contributor agreement, patent grant, trademark clause or third-party notices. The bridge ships an inline transliteration table and a stop-word list, both authored in place, and no vendored third-party code was found in either repository.

**Verify.** One pass ran; no row was refuted. Licence and pin confirmed at both pins.

**Smallest part.** The managed and free block-region functions in the mirror's shared package: the marker constants, the managed-block upsert, the user-notes render, detect, extract and ensure helpers, a content hash with canonicalisation, an insertion-point finder, and the native-notes detect and upsert pair. These are pure string functions with no Obsidian or Zotero imports. Optionally add the frontmatter merge and its managed-key list, with the caveat that it is a line-regex and JSON-quote handler rather than a YAML parser. Together roughly 250 lines under MIT, covered by two test files.

**Fitting.** *Inputs:* a snapshot JSON fetched by the mirror from the bridge's endpoint on the connector port with a scope and citation-mode query, validated by a shipped schema assertion. This requires the bridge add-on installed and enabled in a running Zotero, whose manifest spans a wide version range. The mirror also reads existing vault markdown under the target folder, adopting any note whose frontmatter carries an item key or a note key, plus its own JSON state files. *Outputs:* one markdown note per regular item at a configurable path template, containing managed YAML frontmatter with more than twenty keys, a marked metadata callout block, a marked native-notes block when the item has child notes, with HTML converted to markdown, and a marked user-notes block seeded with a seven-heading scaffold and preserved thereafter. Also collection index notes, standalone note files, three JSON index files under the plugin directory, conflict files, and a deleted-items archive when configured. It optionally writes back into Zotero a child note per item, tagged with a marker comment, holding the user-notes block as HTML. *Invocation:* Obsidian command palette entries including sync, a dry-run preview, index rebuild, two write-back commands and citation commands, plus a scheduled interval. The programmatic core is one function taking a snapshot, a note store, settings and options, returning per-path operations. Auto write-back fires three seconds after any modification of a paper note. *Harnesses:* Obsidian desktop only, paired with the Zotero add-on. It is not a Claude Code skill or plugin, not Codex, and has no command-line tool. The shared core runs under Node against any note-store implementation, and the mirror talks to the bridge over Node's HTTP module, forcing IPv4 for the loopback hostname, with Obsidian's request helper as a fallback.

**Surplus.** Citation rendering in reading mode with editor decorations and a virtual references block is neutral for an agent-driven vault and a cost if adopted as-is, being Obsidian-only with a network round trip per note. A citations side panel with copy and save commands is neutral, and its bibliography entry is hand-built rather than a real export. The write-back into Zotero, auto-triggered after edits with conflict files on hash mismatch, is a cost because it writes into the user's library without a review gate and would need disabling. The citekey alias registry with vault-wide rewriting of citation references on every sync is a cost, because it mutates files outside managed regions, and is helpful only if automatic re-keying is wanted. Bridge-side citekey generation with transliteration aliases and suffix disambiguation is a cost, because it silently diverges from Better BibTeX keys for unpinned items. Collection index notes are helpful if collection mirrors are wanted. Native-note migration into a managed block is helpful, though its heading is in Chinese and is not configurable. Tag normalisation with originals kept is helpful to neutral. The full-text search index and the Zotero item-pane section that reads it are a cost, because the bridge reads the index from the hard-coded developer vault path and is therefore non-functional elsewhere without code edits. The Zotero context-menu open-in-Obsidian action carries the same cost. Health diagnostics and a guarded installer that verifies no other add-on's state changed are neutral. Three delete-handling modes with tombstone frontmatter are helpful for orphan handling.

**Coverage.**

**C1 partial** (evidence). The bridge's endpoint registration, the attachment serialiser, and the mirror's default bridge URL.

```
    Zotero.Server.Endpoints[path] = Endpoint;  ||  async function serializeAttachment(Zotero, attachment, library) {
    return {
      key: attachment.key,
      title: getField(attachment, "title"),
      fileName: getField(attachment, "filename"),
      mimeType: getField(attachment, "contentType") || attachment.attachmentContentType || undefined,
      zoteroUri: getZoteroSelectUri(library, attachment.key)
    };
  }  ||  bridgeUrl: "http://127.0.0.1:23119/obsidian-zotero",
```

It reads a local Zotero, but through an endpoint the bridge registers on Zotero's connector server rather than through the stock local API or Better BibTeX, neither of which is referenced anywhere in either body. This works with the stock local-API preference off, because it rides the connector server on the same port. What is read: item metadata through a serialiser covering fifteen fields, enumerated by a full library scan; child and standalone native notes as HTML; and collections with paths and item keys. Attachments are a list only, carrying a key, title, filename, MIME type and a select URI, with no file path and no content. Annotations are absent, confirmed by a grep across both bodies. So metadata and native notes yes, attachments list-only, annotations no, and the transport is a custom add-on endpoint.

**C2 partial** (evidence). The mirror's marker constants and the ensure call, with the bridge's citekey regex and a named preservation test.

```
export const MANAGED_BLOCK_START = "<!-- BEGIN OBSIDIAN-ZOTERO-METADATA -->";
export const MANAGED_BLOCK_END = "<!-- END OBSIDIAN-ZOTERO-METADATA -->";
export const NATIVE_NOTES_HEADING = "# zotero原生笔记迁移";
export const NATIVE_NOTES_BLOCK_START = "<!-- BEGIN OBSIDIAN-ZOTERO-NATIVE-NOTES -->";
export const NATIVE_NOTES_BLOCK_END = "<!-- END OBSIDIAN-ZOTERO-NATIVE-NOTES -->";
export const USER_NOTES_BLOCK_START = "<!-- BEGIN OBSIDIAN-ZOTERO-USER-NOTES -->";
export const USER_NOTES_BLOCK_END = "<!-- END OBSIDIAN-ZOTERO-USER-NOTES -->";  ||  return deleted ? withNativeNotes : ensureUserNotesBlock(withNativeNotes);  ||  const key = readFrontmatterString(record.content, "zotero_key");  ||  const match = typeof extra === "string" ? extra.match(/Citation Key:\s*(\S+)/i) : null;  ||  assert.match(store.files.get(path)!, /My long hand-written note\./);
```

The managed-and-free split is solidly implemented and tested: the managed upsert replaces only the text between the metadata markers, the native-notes upsert does the same for its block, the ensure helper wraps everything after the managed blocks into the user-notes block on first contact, and the frontmatter merge regenerates only the managed keys while keeping other lines. Two named tests prove preservation, one migrating a legacy note without markers while hand-written text survives, and one asserting that text outside the markers stays. What blocks a full covers: note identity is the item key in frontmatter rather than the citekey, though the citekey is written to frontmatter and to a callout line and is an available filename-template token, so it can be driven to name files by citekey but not to key on it; and the citekey is Better BibTeX's only when that add-on has pinned it into the Extra field, because otherwise the bridge generates its own key and never queries Better BibTeX, so unpinned libraries get keys that diverge.

**C3 partial** (evidence). The mirror's content comparison and orphan loop, the bridge's version and modification-date fields, the tombstone status line, and the citekey rewrite function.

```
    } else if (existing.content !== nextContent) {  ||  version: item.version || undefined,
      dateModified: getField(item, "dateModified"),  ||  for (const [itemKey, existing] of existingByItemKey.entries()) {
    if (activeItemKeys.has(itemKey) || settings.deleteBehavior === "ignore") continue;  ||  deleted ? "> Status: missing from latest Zotero snapshot" : undefined,  ||  export function rewritePandocCitekeys(markdown: string, rewriteMap: Map<string, string>): CitekeyRewriteResult {
```

Per-item version and modification date are serialised by the bridge and the version is written into frontmatter, but nothing compares them: every sync fetches the full library, re-renders every note, and detects drift by whole-content string inequality, with a helper suppressing timestamp-only churn and a test covering it. There is no since parameter, no last-modified-version and no incremental fetch. Orphans are found: a handler marks notes whose key is absent from the snapshot with a deleted flag and the status line, or archives them, with a test. Re-key is handled: an alias registry records previous citekeys from the prior index as history, and a rewrite function updates citation references across vault files on every non-dry-run sync. So drift by brute-force diff, orphan yes, re-key yes, version-based detection no.

**C4 does not** (evidence). The bridge's item serialiser, where the PDF field is a URI rather than a path.

```
      pdfUri: attachments.find((attachment) => attachment.mimeType === "application/pdf")?.zoteroUri,
      attachments,
```

The only attachment data crossing the bridge is a key, title, filename, MIME type and a select URI. There is no file path, no PDF text and no full-text index read, confirmed by a grep across both bodies. The open-PDF command just launches the URI externally.

**C5 does not** (evidence). The mirror's desktop-only manifest flag and its plugin class.

```
  "isDesktopOnly": true  ||  export default class ObsidianZoteroConnectorPlugin extends Plugin {
```

Nothing shipped runs without Obsidian: the only entry points are Obsidian commands and an Obsidian interval, and the only note-store implementation wraps the Obsidian vault. There is no command-line tool and no filesystem store. The bridge endpoint itself is reachable by any HTTP client while Zotero runs, and the sync core is Obsidian-free and proven under Node with an in-memory store, so headless use is a small delta, but that belongs under the smallest part and the treatment rather than to coverage.

**C6 covers** (evidence). Both licence files, lines 1-8.

```
MIT License

Copyright (c) 2026 mappedinfo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
```

Both repositories ship the standard MIT text, so use, copying, modification and redistribution are permitted subject to retaining the notice.

**C7 does not** (evidence). The bridge's citation rendering call, its health warning, its bibliography builder and its write-back entry.

```
      const content = await Zotero.QuickCopy.getContentFromItems(items, quickCopyFormat(style), null, asCitation);  ||  health.warnings.push("Better BibTeX is not installed; explicit Citation Key values may be unavailable.");  ||  function buildBibtex(item, citekey) {  ||  async function syncObsidianNote(Zotero, payload = {}) {
```

None of the listed enrichment or lint kinds exists in either body. The inventory of what the bridge does provide, so the vault need not replicate it: citekey resolution or generation, with an explicit key from the Extra field and otherwise a generated key with alias variants, a transliteration table and suffix disambiguation; citation and reference strings rendered by Zotero's own engine through its quick-copy API with a named style URL, with a hand-rolled fallback; a simplified bibliography entry with seven fields; an endpoint resolving citekey groups to rendered citations and a bibliography; add-on health reporting whether Better BibTeX is installed or enabled and which other add-ons are disabled; the write-back of the user-notes block as a marker-tagged child note with hash conflict detection; and an item-pane search over the generated index, which works only with the hard-coded vault path.

**D1 does not** (evidence). The mirror's note template, whose first heading is a summary.

```
export function paperNoteTemplate(): string {
  return [
    "## Summary",
    "",
    "",
    "## Research Question",
    "",
    "",
    "## Method",
    "",
    "",
    "## Evidence",
```

The per-source page contains a summary heading, but it is an empty scaffold seeded into the user-notes block; no source text is read and nothing fills it. The row is listed only so the heading is not misread as a digest.

**D2 does not** (evidence). The remainder of the same template.

```
    "## Useful Ideas",
    "",
    "",
    "## Critique",
    "",
    "",
    "## Follow-up",
    ""
  ].join("\n");
}
```

The seven-heading scaffold is fixed in code, and there is no setting, file or parameter through which a caller supplies a field list; the only user-facing template is the filename template, and none exists for the note body. No field is ever populated.

**D7 covers** (evidence). The mirror's default sync settings with the two settings-tab controls.

```
export const DEFAULT_SYNC_SETTINGS: SyncSettings = {
  targetFolder: "Zotero",
  papersFolderName: "Papers",
  collectionsFolderName: "Collections",
  standaloneNotesFolderName: "Zotero原生独立笔记",
  archiveDeletedFolderName: "_Deleted",
  filenameTemplate: "{year} - {firstAuthor} - {title}",
  libraryScope: "all",
  deleteBehavior: "mark"
};
```

The layout is explicit and configurable, with a documented path shape for items and for collection indexes plus three special folders. Only the target folder and the filename template are exposed in the settings tab, while the subfolder names are settings-file fields. It works inside an existing vault, because existing notes are adopted by their key frontmatter wherever they sit under the target folder, and the generated JSON indexes live under the plugin directory, with a migration from older in-folder copies.

**D8 partial** (evidence). The template's citekey frontmatter and callout line, the wikilink builder, and the markdown post-processor.

```
    citekey: item.citekey,  ||  item.citekey ? `> Citekey: ${item.citekey}` : undefined,  ||  return `[[${linkPath}|${alias}]]`;  ||  this.registerMarkdownPostProcessor((element, context) => this.renderPandocCitations(element, context));
```

Provenance markers carry the citekey in three frontmatter keys and a callout line, and citation references are resolved through the bridge and the alias registry. But the citekey is bridge-derived rather than caller-supplied, and generated cross-page links in collection indexes are wikilinks by file path rather than by citekey.

**Treatment opinion: copy plus a delta.** Install-as-is fails the lane's harness and transport shape: the mirror is Obsidian-only, its data source is a bespoke add-on endpoint rather than the stock local API or Better BibTeX, it keys notes on the Zotero item key rather than the citekey and may generate non-Better-BibTeX citekeys, it does no version-based change detection, and it carries write-back and vault-wide rewrite behaviours that would need disabling. Forking would mean maintaining roughly 2,400 lines of Obsidian interface plus a Zotero add-on from a one-star single-developer project with a version-string mismatch. What is valuable and cleanly separable is the three-block managed-and-free region merge with its frontmatter-key merge: pure string functions, MIT, Obsidian-free, tested under Node, and the closest worked implementation in this run of a machine-owned region plus a preserved free region plus a native-notes region. Copy those functions with attribution and apply a delta: key identity on the citekey, or keep the item key as a secondary id; rename the Chinese native-notes heading; drop the hash if not writing back; and feed them from the stock local API or Better BibTeX in a command-line tool. The bridge's endpoint-registration pattern is worth remembering as a fact rather than adopting.

**Facts carried from this body.** Ten. A Zotero plugin can serve its own HTTP endpoints on the connector port by assigning a constructor into the server's endpoint table whose prototype declares supported methods and data types and an initialiser returning status, content type and body, which bypasses the stock local API and its preference (F1). The bridge treats a citation-key line in the Extra field as the pinned key and otherwise generates its own, so it never reads the Better BibTeX key store directly (F2). Zotero's in-process citation rendering is reachable through its quick-copy API with a style URL and an as-citation flag, and the style URL used here is the APA one (F3). Better BibTeX's add-on identifier as seen by Zotero's add-on manager is a specific string, which the bridge inspects to warn when it is missing or disabled (F4). The bridge declares compatibility across a wide version range and self-updates from a raw file in its own repository (F5). Select URIs take one form for the user library and another for group libraries, and the same form is used for attachment and note keys (F6). Two named Zotero 7-and-later plugin interface hooks are used for an item-pane section and for context menus, each guarded because they may be unavailable, with registration gated on a readiness promise (F7). Library enumeration for the snapshot is a full scan every call, filtered to regular items, with collections fetched by library and note bodies and titles read through two accessors (F8). The bridge marks notes it created from Obsidian with an HTML comment carrying six fields, and excludes such notes from the snapshot so they do not round-trip (F9). And on the Obsidian side, reaching a loopback Zotero endpoint reliably means using Node's HTTP module directly and forcing IPv4 for the loopback hostname, with the application's own request helper only as a fallback (F10).

The record's caveats for a later reader: the snapshot schema carries a per-item version and modification date that the mirror never uses for change detection; the bridge's configuration is a hard-coded literal so the Zotero-side open and search features are developer-machine-only as shipped, while four endpoints work anywhere; the frontmatter merge is regex-based, so pre-existing user YAML with multi-line values under a managed key would be dropped and re-emitted; the content hash exists only for the write-back conflict check rather than for a re-ingest no-op; and the bridge's version constant lags its manifest. Every quoted line was checked against the raw files at the pinned commits.

### 33. daeh/zotero-markdb-connect

Seeded. `https://github.com/daeh/zotero-markdb-connect`. Pin `825ef2d1015181b2ce5765607d9587f75d3a7f9d`, main HEAD of 2026-08-19, tag and package version 0.2.4. Kind: a Zotero add-on.

**Maintenance.** Last push 2026-08-19T20:29:40Z; 680 stars; 12 open issues. Three releases are named, the current one adding Zotero 10 support, the one before it the last for Zotero 9, and one withdrawn release recorded by a commit that stops advertising it. Continuous integration lints, type-checks, tests and builds on every push and pull request, with automated dependency updates configured. Single maintainer, with a pinned toolchain.

**Originator and supplier.** Dae Houlihan, both, with an institutional affiliation recorded in the archival metadata file, distributed as a release asset.

**Licence.** MIT, found, at `LICENSE` lines 1-10 of a full 21-line text, with the package metadata, the archival metadata and the API all agreeing.

```
MIT License

Copyright (c) 2023 Sean Dae Houlihan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
```

IP assertions: none beyond the notice. One vendored third-party test library carries its own licence file and is test-only, not shipped in the add-on. The project is built on a community plugin template, which is a development dependency rather than an encumbrance on the source read here.

**Verify.** Two passes ran, none refuted. Both confirmed the licence at the pin and re-resolved the pin.

**Smallest part.** For the seeded purpose, which is presence-marker write-back, the smallest usable piece is the installed add-on itself: the reconcile logic is about sixty lines that find items carrying the tag, add it to matched ids and remove it from unmatched ids under the default policy, plus a small tagged-item finder. Both call Zotero internals and cannot run outside the Zotero process. The piece the vault actually takes is not code but the note-naming contract the scanner enforces: a filename matching an at-sign-prefixed pattern, or a frontmatter key in a leading delimiter block. The vault-scanning half is separable in principle but is written against Zotero's file helpers rather than Node's.

**Fitting.** *Inputs:* a single root folder path chosen through a Zotero file picker, which Zotero's own process must be able to read, validated through Zotero's path helpers. It is scanned recursively, skipping dotfiles, hidden, special and symlinked entries. The file filter defaults to an at-sign-prefixed markdown pattern or a caller regex with one capture group. Three match strategies exist: a frontmatter citekey, which is the documented default but which fails validation out of the box because the key name preference defaults to empty, so matching is filename-only until it is set; a caller regex over the note body; and a regex capturing an eight-character Zotero item key. On the Zotero side, all non-deleted regular items in the user library or in all libraries, joined on the native citation-key field or on the item key. *Outputs:* a Zotero tag added to each matched item, with a default policy that removes it from previously tagged items whose note is gone and an alternative add-only policy; an in-memory map exposed read-only through the add-on instance; two item context-menu entries that launch vault URIs or the system handler; popup notifications with counts and an optional report dialog, with JSON dumps in the most verbose debug mode; and a preference stamped with the plugin version after each run. *Invocation:* the Zotero interface only. Install the add-on file from releases, then sync runs automatically on every main-window load, from a tools-menu entry, and from a troubleshooting entry registered only when the last run was unclean. A keyboard shortcut opens the selected item's first linked note. Programmatically it is callable from inside Zotero through the exposed instance, which the integration tests do. *Harnesses:* a Zotero desktop bootstrap add-on. At this pin it installs only on the Zotero 10 line, with earlier lines routed to older releases by the update manifest. It is not a Claude Code skill or plugin, not a Codex tool, and has no command-line entry. The two vault applications appear only as URI launch targets and neither is required for the sync itself.

**Surplus.** The jump-to-note direction from Zotero is helpful and costs the import pipeline nothing. The presence-marker write-back is helpful and is the seeded capability: it lets Zotero saved searches and tag colours show which items already have a literature note without the vault touching Zotero. The removal semantics of the default policy are a cost and a real footgun, because any item whose note was not found in a given run loses the tag, and the zero-match guard prevents wholesale stripping only when nothing at all matched, so a partially readable vault will strip tags from the missing part; the add-only policy is the mitigation. The automatic full sync on every main-window load is a cost proportional to library and vault size, with no preference to disable it at this pin, because the enable preference exists but is never read. The item-key matching strategy is neutral if the vault keys by citekey. The group-library toggle is neutral. The second vault application's support is neutral. Preference migration of about 350 lines is neutral code bulk. A startup update check that fetches a manifest is neutral for the release build but is a network call at every start for any fork that changes the add-on id. The troubleshooting dialog and JSON dumps are helpful while tuning the naming contract. Two dead helpers have no callers and should not be counted as features.

**Coverage.**

**C1 partial** (evidence). `src/modules/mdbcScan.ts` lines 386-416, the citekey query, with the item-key query at lines 424-447.

```
const ZotItems: Zotero.Item[] = await Zotero.Items.getAsync(itemIds) … citationKey = zotitem.getField('citationKey') || ''
```

It reads item metadata, meaning the internal id, the item key and the native citation-key field, from the local library, but only item metadata: a grep of the source for the attachment and full-text vocabulary returned nothing, so attachments and annotations are never read. And the read is in process through Zotero's own search and item APIs, not through the local API port or Better BibTeX, confirmed by a grep, since the only HTTP request in the source is the update check. The vault pipeline therefore cannot reach this read path from outside Zotero. Floor requirement not met.

**C2 does not** (evidence). `src/modules/mdbcUX.ts` lines 97, 113 and 141, the only two writes, with the read side in the scanner.

```
const filename = `${config.addonName.replace('-', '')}-logs.json` … await Zotero.File.putContentsAsync(filepathstr, data)
```

A grep of the source for the write helpers finds exactly two writes, both JSON debug dumps behind a file-picker dialog. The plugin never emits a markdown note; it only reads notes another tool wrote. No managed-and-free region concept exists because no note is written. Floor requirement not met: this is the consumer side of the note contract rather than the producer.

**C3 does not** (evidence). `src/modules/mdbcScan.ts` lines 725-751, the tag reconciliation.

```
items_removetag = items_withtags.filter((item) => !items_withnotes_zotids.includes(item.id))
```

There is no Zotero-side change detection: a grep for observers, notifiers, modification dates, versions and since parameters returns only a version string in the logger. Each sync is a full recompute: query every non-deleted item, rebuild the citekey map, rescan the vault, then diff the current tag set against the matched ids. It detects vault-side orphans, meaning notes whose citekey matches no item, and both untagged and over-tagged items, but nothing about item version, modification date or re-keying on the Zotero side.

**C4 does not** (evidence). The scanner's file filter and suffix pattern.

```
const re_suffix = /\.md$/i … const filteredFiles = allFiles.filter((file) => re_file.test(file.name))
```

The only file contents read are the matched markdown notes themselves. A grep for the extraction vocabulary is empty; there is no PDF-to-text of any kind, local or cloud.

**C5 does not** (evidence). `src/hooks.ts` lines 29 and 52, the main-window load hook, with the bootstrap call and the programmatic hook the tests use.

```
async function onMainWindowLoad(win: _ZoteroTypes.MainWindow): Promise<void> { … await ScanMarkdownFiles.syncWrapper(false, false)
```

The plugin is a bootstrap extension that runs inside the Zotero interface process; the sync fires automatically on window load and from menu entries. There is no command-line tool, no standalone script and no external entry point. It does not need Obsidian running, since that is only a launch target, but the main clause of the requirement, headless from a command line or an agent, is not met. Noted for completeness: the add-on instance is exposed globally, so its sync is callable from anything that can execute JavaScript inside a running Zotero window, which is exactly what the integration tests do, but that still requires a running Zotero with a main window.

**C6 covers** (evidence). `LICENSE` lines 5-9 with the package metadata.

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software
```

The licence file is present at the pin and permits use, copying and modification with attribution.

**C7 does not** (evidence). `src/modules/mdbcScan.ts` lines 743-751, the tag write loops, with three report paths.

```
for (const item of items_removetag) {
      item.removeTag(tagstr)
      await item.saveTx()
    }

    for (const item of items_totag) {
      item.addTag(tagstr)
      await item.saveTx()
    }
```

There is no metadata enrichment or format lint: a grep for the enrichment vocabulary is empty and the plugin never edits any item field. What it does provide on the Zotero side, so the vault need not replicate it, is the presence-marker tag with its two removal policies, and vault-to-Zotero consistency reports naming notes with no extractable citekey and citekeys or item keys that match no library item, with optional JSON dumps in debug mode. That is the seeded write-back capability, and it lands in surplus rather than in this row.

**D4 partial** (evidence). The scanner's default file and title patterns, with the frontmatter and body-regex paths.

```
let re_file = /^@.+\.md$/i
    let re_title = /^@(\S+).*\.md$/i
```

An other-lane row that is plausibly touched: the plugin is exactly the consume-a-note-another-process-wrote half of the requirement, since it never owns note creation and reads any conforming note regardless of who wrote it. It performs no integrate or digest step, so the requirement as a whole is not covered.

**D7 partial** (evidence). The source-directory and file-pattern preferences with the recursive lister.

```
pref('sourcedir', '') … pref('filepattern', '^@.+\\.md$') … for await (const file of listFilesRecursively(zfileBaseDir.path)) {
```

An other-lane row, read side only: it works on an existing vault with a caller-chosen root, recurses through any sub-layout, and states its one layout requirement explicitly. It is not a digest tool, so it cannot cover the writing side.

**D8 partial** (evidence). The citekey precedence line and the join against the citekey map.

```
entry_res.citekey = entry_res.citekey_metadata || entry_res.citekey_title … if (citekeys.includes(entry_res.citekey)) {
          entry_res.zotids = citekeymap[entry_res.citekey] ?? []
```

An other-lane row: the citekey is the stable id that binds a note to a Zotero item, with the metadata value winning over the filename, and the item's native field is the join key on the Zotero side. The plugin emits no page links or provenance markers, so only the id-as-key half applies.

**D10 covers** (evidence). `LICENSE` lines 6-8, an other-lane row on the same artifact as C6: MIT permits use and modification.

**Treatment opinion: install as-is.** As a capture candidate it fails both capture floors: it reads item metadata only, in process, never attachments or annotations and never through the local API or Better BibTeX, and it writes no markdown at all. It should not be adopted to produce literature notes. It is worth installing unchanged for its surplus, the Zotero-side presence tag and the Zotero-to-vault jump, which is exactly the seeded write-back and which the vault pipeline would otherwise have to implement through the local API. Install rather than fork or copy because the code is written against Zotero internals and cannot be lifted into a command-line tool or a skill; the only coupling the vault must honour is the note-naming contract, which the vault's own emitter controls; and the project is live. Three conditions to record when installing: pin the release to the one matching the installed Zotero line; set the add-only removal policy unless the vault folder is guaranteed readable by Zotero on every start; and set the frontmatter key name if matching should come from frontmatter rather than the filename. A fork would only be justified to add per-item change detection or a headless entry point, both of which are outside this architecture and better served by the local API from the vault side.

**Facts carried from this body.** Nine, named by their own identifiers. At Zotero 10 the citation key is a native item field readable and settable through the field accessors on a journal article, with the code guarding against item types that do not expose it, and the body does not say since which version the field exists (F1):

```
let citationKey = ''
      try {
        citationKey = zotitem.getField('citationKey') || ''
      } catch {
        // Some regular item types do not expose citationKey.
      }
```

Zotero 10 is built on a named Firefox extended-support release, and the version comparator treats the manifest's minimum as excluding the last Zotero 9 patch and admitting Zotero 10, which is the mechanism plugins use to gate a release to one major line (F2). In update manifests, Zotero 6 reads one application selector while Zotero 7 and later read another, so an entry carrying only one is invisible to the other generation (F3). This project's release routing maps four Zotero versions to four plugin versions (F4). Zotero 10 removed the flat icon set, so notifications must use the vector icons (F5). Zotero 10 plugin menus are registered through a menu manager with two named targets and localisation identifiers that require the localisation file to be inserted first (F6). The plugin scaffold can run integration tests inside a real launched Zotero with preferences injected per run and a readiness probe, which the record flags as a reference pattern for this repository's own live testing (F7). A reveal call is unavailable on some platforms including Linux, with a launch on the parent directory as the fallback (F8). And one README-sourced item recorded for narrowing only: the external-link security dialog for custom URI schemes is suppressed per scheme by a boolean preference on the newer Zotero lines and by a different preference on the older ones (F9).

The record's gotchas for adoption: the default configuration is filename-only matching because the frontmatter key name defaults to empty and fails validation; frontmatter parsing is a naive split, so the file must start with the delimiter at the first byte; the enable preference exists but is never read, so the startup sync cannot be turned off; the source directory is validated inside the Zotero process, which matters for this repository's path-translation notes; and at this pin the add-on installs on the Zotero 10 line only.

### 34. dvanoni/notero

Seeded. `https://github.com/dvanoni/notero`. Pin `011be2ca9ddc6b34326f7e5ce75089266cbf94bc`, main HEAD and the 2.1.0 release, committed 2026-08-19T05:53:18Z. Kind: a Zotero add-on.

**Maintenance.** Active. Last push 2026-08-20T03:40:01Z; 3,207 stars; not archived; the latest release is a day before the pin, published through release automation. It requires the Zotero 10 line at this pin, with earlier Zotero generations served only by an older release. Three runtime dependencies and a modern toolchain.

**Originator and supplier.** David Hoff-Vanoni, both, with the concept credited to another account in the README. The release is published to GitHub releases and to a project download page.

**Licence.** MIT, found, at `LICENSE` lines 1-8 of a full 21-line text. The package metadata carries no licence field, and the generated install manifest carries none either. No per-file headers in the sources read.

```
MIT License

Copyright (c) 2021–2025 David Hoff-Vanoni

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software
```

IP assertions: none beyond the copyright notice. The concept credit in the README is attribution rather than an IP claim.

**Verify.** Two passes ran, none refuted. Both confirmed the licence text at the pin and re-resolved the pin.

**Smallest part.** The property-definition array in the sync package: a self-describing map from Zotero item fields to named literature-note properties, covering more than twenty properties including a citation key read from the native field, a file path from the best attachment, and formatted citations from Zotero's quick-copy API. It is the only lane-relevant unit and could be lifted as a field schema, but its builders need the in-process Zotero runtime. The only zero-dependency block is the highlight and text colour tables in the note converter.

**Fitting.** *Inputs:* Zotero regular items and their child notes, selected either by notifier events on collections enabled in a preference, or by two context-menu entries. Plus an access token for the cloud sink, obtained through a hosted authorisation proxy or a legacy preference, and a database identifier preference. Note HTML is read through the item's note accessor. *Outputs:* one cloud database page per Zotero item, titled per a format preference with five alternatives including the citation key, carrying only properties whose names already exist in the target database with a matching type. Notes become toggle blocks under a single container block. It also writes back into Zotero: a tag, and a linked-URL attachment whose note holds a JSON block with a container identifier and per-note identifiers and timestamps. *Invocation:* install the add-on into Zotero 10. Sync runs automatically on notifier events, debounced by two seconds, or from the context menus, and one maintenance function is callable from Zotero's console. A developer script builds and launches Zotero. *Harnesses:* the Zotero desktop interface only. None of Claude Code, Codex, Obsidian or a command line. There is no Obsidian involvement at all, and a cloud service is the sink.

**Surplus.** The authorisation flow through a developer-hosted proxy with token unwrapping is a cost: a third-party hosted dependency and a cloud sink the set did not ask for. Library mutation on every sync, adding a tag and a linked attachment carrying sync state, is a cost for a capture tool that should read rather than write. The debounced serialised sync queue is helpful only if the vault ever hooks a push from inside Zotero. Formatted citations through the quick-copy API with a style fallback are a helpful pattern for a literature note's citation line, but are in-process only. The HTML-to-blocks converter is neutral, being specific to the cloud sink, except for the colour tables, which are carried as a fact. The duplicate finder is neutral. Localisation and a preference pane are neutral to a build-weight cost. The menu and protocol-handler code is neutral and useful only as Zotero-API reference.

**Coverage.**

**C1 partial** (evidence). `src/content/sync/property-builder.ts` lines 130-132, the citation-key read, with the attachment path at lines 280-284 and the notifier filter in the sync manager.

```
  private getCitationKey(): string | undefined {
    return this.item.getField('citationKey');
  }
```

It reads item metadata locally, but through Zotero's in-process plugin API rather than the local API port or Better BibTeX; a grep across the sources for those transports hit only an add-on check in the preference pane. Attachments: the only access is a best-attachment call resolved to a file path, not content. Annotations: never read as items, since the notifier filter admits only regular items and notes, and a grep for the annotation vocabulary returned nothing. So metadata yes but in-process only, attachments path-only, annotations no.

**C2 does not** (evidence). `src/content/sync/sync-regular-item.ts` lines 60-63, the page creation, with the container-block comment in the note sync module.

```
  return notion.pages.create({
    parent: { database_id: databaseID },
    properties,
  });
```

The output is a cloud database page created or updated through an API; there is no markdown emitter and nothing that can be driven to write a file. The container block is a machine-owned region inside a user-owned page, described in the code as a single container the tool can update without affecting anything the user added, and the page title can be the citation key, so the managed-and-free split and citekey keying exist as a design pattern, but not in markdown, so the requirement is not met.

**C3 partial** (evidence). `src/content/services/sync-manager.ts` lines 176-179, the note staleness check, with the observer registration and the orphan behaviour.

```
        const syncedAt = syncedNotes?.[note.key]?.syncedAt;
        if (!syncedAt || syncedAt < parseItemDate(note.dateModified)) {
          notesToSync.push(note);
        }
```

Per-note change detection exists: a per-note timestamp stored in the linked attachment's note is compared with the note's modification date. Regular items have no version or date comparison and are re-pushed on every relevant notifier event. There is no item version, no since parameter, and no orphan or re-key detection: when the remote page is gone the code recreates it rather than flagging it. Everything is event-driven inside Zotero, so nothing is exposed to an external process.

**C4 does not** (evidence). `src/content/sync/notion-client.ts` lines 10-13, the client construction, with the only attachment access.

```
export function getNotionClient(authToken: string, window: Window) {
  return new Client({
    auth: authToken,
    fetch: window.fetch.bind(window),
```

There is no PDF or full-text extraction anywhere, confirmed by a grep, and the sole attachment call returns a file path for one property. Every output is a cloud call through the window's fetch.

**C5 does not** (evidence). `src/content/services/sync-manager.ts` lines 252-256, the main-window guard, with the bootstrap loader.

```
    const mainWindow = Zotero.getMainWindow();
    if (!mainWindow) {
      logger.warn('Zotero main window not available - cannot sync items');
      return;
    }
```

It is a bootstrap add-on that loads inside the Zotero desktop process and refuses to sync without a main window, which it also needs for its progress window and for fetch. There is no command-line tool and no external entry point, and the only programmatic handle is a global inside Zotero's runtime. Obsidian is indeed not required, but the requirement is conjunctive with headless operation, which fails.

**C6 covers** (evidence). `LICENSE` lines 1-8.

```
MIT License

Copyright (c) 2021–2025 David Hoff-Vanoni

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
```

Standard MIT text at the pin, permitting use, copying and modification subject to notice retention.

**C7 does not** (evidence). `src/content/sync/property-builder.ts` lines 249-250, the DOI property, with the duplicate finder's query.

```
        const doi = this.item.getField('DOI');
        return doi ? `https://doi.org/${doi}` : null;
```

There is no Zotero-side enrichment or lint: the DOI is only string-prefixed into a URL with no verification, there are no identifier or citation-count lookups, and there is no metadata lint. The duplicate finder queries the remote database for repeated property values rather than Zotero. Recorded for the vault: this candidate provides nothing under this requirement, so there is nothing to avoid replicating.

No digest-lane row is given. The record explains the choice: the tool produces cloud pages rather than vault pages, so none of the digest requirements is plausibly covered, and while the licence requirement would be satisfied by the same MIT text already recorded, listing it would misrepresent the candidate as a digest candidate.

**Treatment opinion: take nothing.** The architecture is orthogonal to the capture lane: it lives inside the Zotero interface process, reads through the in-process plugin API rather than the local HTTP API or Better BibTeX, writes to a cloud service, mutates the Zotero library, and has no markdown or file output. It covers the licence floor fully and the local-read and change-detection requirements only partially, and the rest not at all. Nothing in it can be installed, forked or copied to satisfy a floor requirement, and the reusable content, meaning the field map, the note-staleness check, the managed-container idea and the Zotero API facts, is design knowledge rather than code that would run in an agent harness. Carry those as facts and do not take the code.

**Facts carried from this body.** Ten. Inside Zotero the citation key is readable through the in-process item accessor, and this tool gates that option on the Better BibTeX add-on being active by its add-on identifier; because that is the in-process API rather than item JSON, it does not answer the register's question about the field's presence in the API (F1). Zotero note-editor text colours are given as an eight-entry table derived empirically, with the companion background palette derived from Zotero's own note-template documentation and then adjusted, so the record flags the second table as approximate (F2). On the plugin menu API, the manager exists only from Zotero 8, and Zotero 10 renamed one menu-context field, with three registration targets seen (F3). The notifier observer types used for change detection are four, and two of them deliver compound identifiers that must be split (F4). Formatted citations can be produced in process through the quick-copy API, with the user's format in a named preference and an APA fallback, and the call may return either synchronously or through a callback (F5). The item URI helper yields an HTTP URI whose path contains a local marker for a never-synced library, which this tool deliberately excludes from username substitution (F6). Writing back into Zotero without re-triggering observers is done through a skip-notifier save option, with the README narrowing that the tag and attachment may then not appear in the interface until the item is reselected (F7). As a design fact, this tool stores its per-item sync state inside the Zotero library, as JSON in a marked element within the note of a linked attachment, so it rides along with account sync and survives reinstalls, and the note also carries a human warning and a last-synced timestamp (F8). The Zotero 10 install manifest shape is given, with this project pinning a narrow version range while earlier Zotero generations are directed to an older release (F9). And custom-scheme URLs are parsed differently by Zotero 7 and Zotero 8 and later, with a plugin able to register a handler by writing into the protocol handler's extension table (F10).

The record notes that the README was used only to narrow, and that its statement about extracting annotations into a Zotero note first confirms the code finding that annotation items are never read directly. It also flags that the converter's test fixtures are samples of Zotero note-editor HTML, including annotation exports, which could serve as parsing fixtures for a vault-side note importer. Two authentication modules were not read, so the credential-storage claim in the project's privacy document is not carried as a fact; that omission is also listed under what was not examined.

### 35. UB-Mannheim/zotero-ocr

Seeded as "local OCR". `https://github.com/UB-Mannheim/zotero-ocr`. Pin `73b0d73b1564be9d6205bde7dde7df62cd5f5885` on master, a 2026-08-27 commit, manifest version 0.9.5.1, whose release tag was published 2026-05-04. Kind: a bootstrapped Zotero add-on covering Zotero 7 through 10, with a legacy Zotero 6 overlay path still in the tree.

**Maintenance.** Last push 2026-08-27T15:59:46Z; 820 stars; three releases named across 2026. Continuous integration builds the add-on on every push and pull request.

**Originator and supplier.** Philipp Zumstein is named as author in both manifests; the supplier is the UB-Mannheim organisation, whose domain appears in the plugin identifier.

**Licence.** AGPL-3.0, found, at `LICENSE` lines 1-2, the unmodified 661-line text, with the README agreeing and the API reporting the same.

```
GNU AFFERO GENERAL PUBLIC LICENSE
Version 3, 19 November 2007
```

The apply-these-terms placeholders are unfilled and the only copyright line in the file is the Foundation's own, so no copyright holder is named anywhere in the body. A grep found no per-file licence or copyright headers. IP assertions: none beyond the licence terms. The record notes that this is strong copyleft with a network-use clause, so copying code into the vault would bind that code.

**Verify.** One pass ran; no row was refuted. Licence and pin confirmed at the pin.

**Smallest part.** The OCR recipe inside the recognise function: the rasteriser argument construction, with six named flags and a resolution, followed by the OCR-engine invocation with a page-list file, a base name, a segmentation mode, a language and one to three output formats, plus a noise-filtering error regex and the executable search-path lists. This is a two-command shell recipe rather than a module; everything else in the file is Zotero interface plumbing that cannot be taken without Zotero.

**Fitting.** *Inputs:* items selected in the Zotero main window, either a regular item with at least one PDF file attachment, of which the first is used, or a PDF attachment item itself, in which case a top-level PDF gets an empty parent created. Sixteen preferences cover the two executable paths, the language, the resolution, the segmentation mode, five output toggles, a page cap for one output kind, and four image-encoding options. It requires two local binaries. *Outputs:* written into the attachment's own directory: an OCR text file always; an OCR PDF, which is then imported or linked as a sibling attachment with a suffixed title; a page-split HTML output with a viewer script tag, capped by a preference; a Zotero child note holding the OCR text with line breaks converted to HTML; and optionally the intermediate page images and the page-list file. *Invocation:* the interface only, through a context-menu entry. It installs as an add-on file built by a script, registered through a bootstrap that loads the main script and registers a preference pane. *Harnesses:* a Zotero desktop add-on spanning Zotero 7 through 10 by its manifest, with a legacy path for Zotero 6. None of Claude Code, Codex, Obsidian or a command line, and Codex compatibility is not applicable because there is nothing to invoke from an agent.

**Surplus.** The text-layer PDF twin attached to the item is helpful for the vault, because Zotero's own full-text indexer and any downstream extraction can then read image-only PDFs; the cost is that the item now carries two PDFs and the original may remain image-only, so attachment-selection logic must prefer the suffixed twin. The per-page HTML attachments with an embedded viewer script are neutral to the vault and cost up to five attachments per item plus a content-delivery fetch whenever one is opened. The OCR text as a Zotero child note is neutral, with the caveat that a capture step harvesting notes from Zotero will see this HTML note alongside user notes and must not mistake it for a literature note. Creating an empty parent for top-level PDF attachments is neutral to helpful, and it mutates the library so orphan PDFs become regular items, which changes what a capture scan sees. The option to overwrite the original PDF is a cost and is irreversible if the OCR misbehaves, as the README itself warns. The Zotero 6 legacy path is neutral dead weight. The hidden image-tuning preferences and the progress window are neutral.

**Coverage.**

**C1 partial** (evidence). `src/zotero-ocr.js` lines 245-247, the attachment filter, with the file path and the selection call.

```
let pdfAttachments = item.getAttachments(false)
                        .map(itemID => Zotero.Items.get(itemID))
                        .filter(att => att.isFileAttachment() && att.attachmentContentType == 'application/pdf');
```

It reads attachments and their file paths from the local Zotero, but only through the in-process API on items the user has selected in the interface. It reads almost no metadata, three fields in total, and never touches annotations. It exposes nothing on the local API port and nothing through Better BibTeX, so an external process cannot call it. It is local rather than web, which is the requirement's core, but it is not a reader a capture pipeline can drive.

**C2 does not** (evidence). `src/zotero-ocr.js` lines 458-461, the note creation.

```
contents = contents.replace(/(?:\r\n|\r|\n)/g, '<br />');
                    let newNote = new Zotero.Item('note');
                    newNote.setNote(contents);
                    newNote.parentID = item.id;
```

The only note it emits is a Zotero child note in HTML containing the raw OCR text. It is not markdown, is not keyed by citekey, since a grep over both source variants returned nothing, and has no managed region. The note lives inside Zotero rather than in a vault.

**C3 does not** (evidence). `src/zotero-ocr.js` line 264, an open comment, with the only re-run guard.

```
// TODO filter out PDFs which have already a text layer ?
```

There is no item version, modification date or since handling anywhere, confirmed by a grep. The only re-run guard is a filesystem check for the page-list file, which skips the rasterising stage but still re-runs the OCR engine. Nothing detects Zotero-side drift, orphans or re-keys.

**C4 covers** (evidence). `src/zotero-ocr.js` lines 392-397, the subprocess call, with the text-output flag, the rasteriser call and the executable search paths.

```
let proc = await Subprocess.call({
                    command: ocrEngine,
                    workdir: dir,
                    arguments: parameters,
                    stderr: "stdout"
                })
```

This is the plugin's core: the rasteriser turns the attachment PDF into per-page images, then a local OCR binary produces a text file plus optional PDF and HTML outputs in the attachment directory. Both are local executables located through preferences or fixed paths on three platforms. There is no cloud call during extraction. Two caveats: it is raster OCR of every page rather than text-layer extraction, so a born-digital PDF is rasterised and re-recognised too, which the open comment above acknowledges; and the single outbound reference, a script tag in the generated HTML attachment, fires only when a user opens that attachment, not during extraction.

**C5 does not** (evidence). `src/zotero-ocr.js` line 227, the selection read, with the menu entry as the only entry point.

```
let items = Zotero.getActiveZoteroPane().getSelectedItems();
```

The only entry point is a context-menu item in the main window; the recognise function needs an interface selection, calls alert dialogs in six places, and opens a progress window. There is no command-line tool, no exported function and no HTTP endpoint. The no-Obsidian half holds trivially, but the tool cannot run headless from a command line or an agent.

**C6 covers** (evidence). `LICENSE` lines 1-2 with the README.

```
GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007
```

The licence permits use, and modification and redistribution under copyleft terms. Using the plugin inside Zotero imposes no obligation on the vault; copying its code would.

**C7 partial** (evidence). `src/zotero-ocr.js` line 263, the base-name choice, with the attachment title, the note, the page outputs and the empty-parent call.

```
let ocrbase = Zotero.Prefs.get("zoteroocr.overwritePDF") ? baseFilename : baseFilename + '.ocr';
```

The Zotero-side enrichment it provides, so the vault should not replicate it: a text-layer PDF twin imported as a sibling attachment with a suffixed title, or overwriting the original when that preference is set; a child note containing the OCR text as HTML; up to a configurable number of per-page HTML attachments with a viewer; and creation of an empty parent for top-level PDF attachments. It provides none of the enumerated metadata lints.

**D10 covers** (evidence). The same licence lines, listed because it is the one digest-lane requirement this body plausibly satisfies. It does not satisfy the others: no page emission, no template, no synthesis pages, no vault layout and no skill.

```
GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007
```

**Treatment opinion: install as-is.** This candidate does not meet the capture floors: it emits an HTML Zotero note rather than a citekey-keyed markdown note with a managed region, it is interface-only, and its local read is only partial, being in-process on user-selected items with no annotations and no external surface. It cannot be the capture tool. What it does well, and what the vault should not replicate, is local no-cloud OCR of image-only PDFs producing a text-layer PDF that Zotero itself then indexes. The adopt-first move is therefore to install it in Zotero as a user-driven prerequisite for scanned PDFs, so that by the time capture runs, full text exists on the Zotero side, and the vault's capture logic then only needs to prefer the suffixed sibling attachment when present. It is actively maintained and its manifest already targets the Zotero 10 line. Do not fork or copy: the copyleft would bind any copied code, and the reusable content is a two-command shell recipe that, if a headless OCR fallback is ever needed outside Zotero, is cheaper to re-author from the upstream tool documentation and credit than to carry as a copyleft dependency.

**Facts carried from this body.** Eight. Zotero note bodies are HTML, and this plugin converts newlines to break tags before saving, so any process writing notes into Zotero must emit HTML and any process reading them gets HTML (F1). One attachment import call works in group libraries while the linking call does not, which the code states in a comment repeated twice (F2). A Zotero 7-era manifest can declare compatibility up to the Zotero 10 line with a fractional minimum, so one add-on file spans four Zotero generations (F3). Plugin code gates on the Zotero version to import a platform module in the newer module format rather than the older one, meaning Zotero 8 and later moved to a newer runtime where the old modules are gone, while the subprocess module is loaded in the newer form on all versions (F4). After a default run the item carries a second PDF attachment with a suffixed filename and a suffixed attachment title, while the original is left untouched and may remain image-only unless the overwrite preference is set, so vault attachment-selection logic should prefer the twin for text extraction (F5). Zotero 7 and later plugins register a settings pane through a named API from the bootstrap start-up and load their main script through a subscript loader (F6). A top-level PDF attachment can be given an empty parent programmatically, which this plugin does so its outputs have somewhere to attach, so capture scans should expect auto-created metadata-less parents (F7). And the plugin does not detect an existing text layer and rasterises every selected PDF regardless, which is an open item in its own source (F8).

The record's closing note for the requirement set: the OCR twin is the one enrichment the vault must account for, and the HTML OCR note must be filtered out when harvesting user notes.

### 36. masaki39/simple-citations

Found in the capture sweep. `https://github.com/masaki39/simple-citations`. Pin `26f955b50a9c6a6c4147e1ecb25c2ffa13392901`, HEAD of main, a docs-only commit after the 1.6.2 release, so all source read is identical to that release. Kind: an Obsidian plugin.

**Maintenance.** Last push 2026-08-13T00:38:28Z; 25 stars. Three releases in May 2026 and five commits from May to August. Single maintainer with one external contributor credited in two changelog entries. A test suite is present, and the release workflow publishes with artifact attestation.

**Originator and supplier.** masaki39, both, distributed through GitHub and the Obsidian community catalogue.

**Licence.** MIT, found, at `LICENSE` lines 1-21 with the package metadata agreeing. The plugin manifest, read in full, has no licence field, and no source file carries a licence header.

```
MIT License

Copyright (c) 2024 masaki39

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software ... subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
```

IP assertions: none beyond the notice. One external contributor is credited in the changelogs, and no contributor agreement is mentioned anywhere in the body.

**Verify.** One pass ran, three rows re-checked, none refuted. It confirmed all four cited body locations verbatim at the pin, including the filename construction, the tag regex with its ten-line module and its replace, insert-after-frontmatter and strip-when-empty logic, a named test, and the alias reset with the full-sync deletion loop immediately above it. The licence was confirmed at the pin as verbatim MIT with the record's elision matching character for character, and the pin was confirmed as still the head of the default branch with the repository metadata matching. The pass records two items it did not re-fetch for budget reasons, the package metadata line and the manifest's absence of a licence field, and the release-tag claim.

**Smallest part.** The managed-region cluster: a ten-line tag-replacement module plus its three imports for trimming, frontmatter parsing and insertion, together with their test specs, about 80 lines of code and 100 of tests. It is the only unit with no Obsidian import and it fully expresses the replace, insert-after-frontmatter and strip-when-empty semantics. Three other modules are Obsidian-free but less relevant. Three pure functions sit in files that do import Obsidian, so they are liftable only by copy-paste rather than by module import.

**Fitting.** *Inputs:* one or more JSON files inside the vault written by Better BibTeX auto-export, in either of two shapes that the plugin auto-detects, with documented field sets. Optionally a template file, a line-separated list of extra field names, several toggles, and a per-property merge strategy when several exports overlap. Settings persist through the plugin's own data API. *Outputs:* one note per valid citekey at a configured folder with an at-sign-prefixed filename, created empty then filled, with existing notes updated in place. The frontmatter carries eleven named keys plus hierarchical tags and any extra fields. The body carries two comment-delimited spans inserted directly after the frontmatter, with the rest of the body untouched apart from blank-line trimming. Side outputs are a document export through an external converter, PDF copies and extracted images into an absolute folder, and a clipboard list of orphan links. *Invocation:* ten command-palette entries, one of which is modal-confirmed because it wipes frontmatter. Automatic triggers are a vault modify event on a registered JSON path gated by a stored modification time, a file-open hook that re-renders the opened note, and a layout-ready hook at startup. Nothing is callable from outside Obsidian. *Harnesses:* an Obsidian community plugin, not desktop-only in its manifest, though the converter and PDF commands are guarded by a desktop check and use Node modules. It is not a Claude Code skill or plugin, not Codex, and has no command-line entry.

**Surplus.** The document export with link rewriting is neutral for capture and costs an external converter dependency, and it temporarily rewrites the active file on disk before restoring it. PDF export and image extraction cost another external dependency and yield no text, so they do not advance local extraction. Multi-bibliography support with per-property strategies and a provenance property is neutral and matters only when several exports overlap. Hierarchical tags are helpful for navigation and optional. Auto-generated aliases are helpful for link autocomplete and cost the wiping of user-added aliases on every run. Group-library link construction is helpful. The three automatic triggers are neutral and Obsidian-only. The settings interface is neutral. The README's index queries are helpful as a pattern and are prose only. The full-sync command that wipes and rebuilds all frontmatter behind a confirmation is a data-destructive path.

**Coverage.**

**C1 does not** (evidence). `src/utils/loadBibliographyData.ts` lines 97-98 and 103, the sole data-ingress path.

```
const file = app.vault.getFileByPath(normalizedPath); || if (!file || file.extension !== 'json') continue; || const contents = await app.vault.cachedRead(file);
```

The only channel is a static JSON file inside the vault read through Obsidian's vault API. A grep of every source file for the local port, the two JSON-RPC spellings and three HTTP call forms returned only link strings for a resolver and two external tools; no local-API or JSON-RPC client exists. The file is expected to be a Better BibTeX auto-export in one of two shapes, detected by a label field. Item metadata and attachment paths do therefore originate from local Zotero, but only as far as the export already wrote them; annotations are wholly absent, and the plugin cannot query Zotero, filter, or fetch anything the export did not contain. The floor's named mechanisms are not used.

**C2 covers** (evidence). `src/commands/addCitations.ts` line 51, the filename, with the tag regex, a named test and the alias reset.

```
const targetFileName = "@" + citekey + ".md"; || const tagRegex = new RegExp(`${startTag}[\\s\\S]*?${endTag}`); || it('removes tags when replacement is empty', () => { || fm.aliases = [];
```

The note filename is an at-sign followed by the citekey in the configured folder. The body's managed regions are two comment-tag spans; the replacement helper regex-replaces only the tagged span, inserts it after the frontmatter when absent, and strips the tags when the replacement is empty, and all three behaviours are exercised by tests, including one asserting that surrounding content survives. Everything outside the spans is preserved except blank-line normalisation. In the frontmatter, plugin-owned keys are overwritten while other user keys survive normal runs. Two breaches of the preserved free region are recorded: the alias key is reset on every update, wiping user-added aliases, and the full-sync path deletes every frontmatter key, gated only by a confirmation dialog. Managed-region content is limited to a static template file plus the abstract, and there is no hook for arbitrary machine-generated content.

**C3 partial** (evidence). `src/commands/autoCitations.ts` lines 11-21, the file-level staleness check, with the orphan computation and the update loop.

```
return lastKnownTime !== new Date(file.stat.mtime).getTime(); || const missingFiles = fileNames.filter(fileName => !citationKeys.has(fileName.slice(1)));
```

Change detection is whole-file: the export file's modification time is compared with a stored value, and that only gates the automatic triggers. There is no per-item version, modification date or since parameter; the update path rewrites every note unconditionally and reads before and after only to count changed files. Orphans are found by a set difference and their links are put on the clipboard. Re-key is handled only indirectly, since a new note is created under the new key and the old one surfaces as an orphan with nothing linking the two. Drift of individual fields is not detected, only overwritten.

**C4 does not** (evidence). `src/commands/pdfCommands.ts` lines 37 and 64, the copy and the image extraction.

```
await copyFile(src, join(settings.pandocOutputPath, basename(src))); || const proc = spawn(pdfimagesPath, ['-png', pdfPaths[i], prefix], { env: process.env });
```

The only PDF handling is copying the files named in a frontmatter property and shelling out to an image extractor. There is no PDF-to-text anywhere in the source, and the abstract inserted into the note comes from the JSON rather than from the attachment.

**C5 does not** (evidence). `src/main.ts` line 13, the plugin class, with the two write paths.

```
export default class SimpleCitations extends Plugin { || await app.vault.process(targetFile, (fileContent: string) => { || await app.fileManager.processFrontMatter(targetFile, (fm) => {
```

Every read and write path goes through Obsidian's own objects, commands are registered through the plugin API, and triggers are Obsidian events. Only the test suite runs outside Obsidian, against a mock. There is no command-line entry point and no exported programmatic API.

**C6 covers** (evidence). `LICENSE` lines 1 and 3 with the package metadata.

```
MIT License || Copyright (c) 2024 masaki39 || "license": "MIT",
```

Standard MIT text, echoed in the package metadata, permitting use, copying, modification, merging, distribution and sublicensing with only notice retention as a condition.

**C7 does not** (evidence). `src/utils/updateFrontMatter.ts` lines 75, 108 and 136-139, the DOI and link construction.

```
if (item['DOI']) vals.doi = `https://doi.org/${item['DOI']}`; || fm.zotero = item['select'] ?? "";
```

The plugin only formats what the export contained: it wraps a DOI into a resolver URL and builds a select link, using the group-library form when the export supplies a matching URI, or a ready-made field in the other export shape. There is no DOI verification, identifier lookup, citation count, version check or metadata lint, and a grep found no network calls at all. There is nothing for the vault to avoid replicating.

**D7 covers** (evidence). The settings description and the two configured paths, with the required-file check.

```
.setDesc('Folder to save literature notes. Default: root folder.') || folderPath: string; || templatePath: string;
```

It works on an existing vault with a caller-chosen note folder and a caller-chosen template file, and its layout requirement is explicit and narrow: notes must be direct children of that one folder and must carry the at-sign-prefixed name, and the export must live inside the vault. No index, log or tree structure is imposed or provided.

**D8 covers** (evidence). The filename construction, the link rewriting and the provenance property.

```
const targetFileName = "@" + citekey + ".md"; || result = result.replace(/\[\[@(.*?)\]\]/g, "[@$1]"); || fm.bibliography = item['_source_files'];
```

The Better BibTeX citekey, normalised from either export shape, is the note filename, and the link convention is a wikilink to that name. The optional provenance property records which export files an entry came from. Provenance is per-note by source file rather than per-claim or per-page.

**D10 covers** (evidence). `LICENSE` lines 1-21: MIT permits use and modification.

```
MIT License || Copyright (c) 2024 masaki39
```

**Treatment opinion: author to the design and credit it.** Two capture floors fail on the body as read: the ingress is an export file read through the vault API with no local-API or JSON-RPC client anywhere, and every read and write goes through Obsidian's own objects with no command-line or exported API. Installing as-is therefore cannot meet the set, and a fork would mean rewriting both the ingress and the whole input-output layer, after which nothing of the plugin's shape would remain. The reusable value is small and pattern-shaped rather than code-shaped: the at-sign-prefixed filename convention, the comment-tag managed span with its strip-when-off semantics and its tests, the export field-mapping table, the orphan set-difference check, and the set of characters a citekey may not contain. The Obsidian-free cluster is about eighty lines of TypeScript, and the host repository is a Python project that already carries its own marker scheme, so copying the TypeScript buys nothing over re-authoring those semantics in place and crediting this project. The alias wipe and the full-sync behaviours are things to explicitly not replicate.

**Facts carried from this body.** Ten. The two export shapes are told apart by a label field plus a top-level items array, with the other shape being a bare array (F1). The consumed item fields of the object shape are nine, and collections are a map keyed by collection key with a name and two child lists (F2). The attachment path in that shape is a local filesystem path, which the plugin filters by extension to populate a property, with no postscript needed (F3). That shape carries a ready-made select link for both personal and group libraries, while the other shape does not, so the plugin builds one, using a group form when a postscript has added a URI (F4). The other shape carries both a citation key and an identifier, with the identifier used in the select URL (F5). Date strings in these exports come in five forms, so year extraction must handle all of them, which a changelog entry states and a parser implements (F6). One export shape is not accepted by the external citation processor as a bibliography, and only the other is (F7). Citekeys containing any of eight characters cannot be Obsidian filenames and are skipped, with a regex and a message in the source and a restatement in the README (F8). The README hosts worked export postscripts that expose seven named handles for adding fields to an export (F9). And the plugin relies on the export file living inside the vault and on the vault's modify event firing for it, with change detection being the file's modification time, so a consumer of an auto-export file has no item-level version signal (F10).

The record corrects three points in the brief it was given: the notes are named with the at-sign prefix rather than bare; the managed tags are the two named spans rather than a generic pair, which appear only as test fixtures; and the file watcher is Obsidian's own modify event gated by a stored modification time plus two other hooks, rather than an operating-system watcher. Its preservation caveats are the alias reset on every run, the blank-line collapsing, and the full-sync deletion of all frontmatter keys.

### 37. northword/zotero-format-metadata

Seeded. `https://github.com/northword/zotero-format-metadata`, distributed as "Linter for Zotero". Pin `095ada8b6cb8ed1e853b1c0f49b13d7020f514d0`, main HEAD of 2026-09-01, a dependency bump after the 3.3.2 release of 2026-08-05. Kind: a Zotero add-on.

**Maintenance.** Last push 2026-09-01T12:07:46Z; 1,046 stars; not archived; the latest release is a month before the pin; default branch main.

**Originator and supplier.** northword, both, with releases shipping the add-on file and a listing on a community plugin index. Parts of the body derive from four third parties, named in the licence block below.

**Licence.** AGPL-3.0-or-later, found, at `LICENSE` lines 1-2, the full text, with the package metadata declaring the or-later variant and the README confirming.

```
GNU AFFERO GENERAL PUBLIC LICENSE
Version 3, 19 November 2007
```

The apply-these-terms line is unfilled, so no named copyright holder appears in the licence file. IP assertions: third-party code and inspiration inside the body are declared in four places, a transliteration snippet under a permissive licence, a sentence-case routine modified from Zotero's own utilities and therefore itself copyleft, a credited inspiration under a third licence, and bundled abbreviation, standard and institutional data sets, plus an acknowledgement of model assistance during development. The copyleft means any copy or fork path carries it into the receiving tooling.

**Verify.** Two passes ran, none refuted. Both confirmed the licence at the pin and re-resolved the pin.

**Smallest part.** The handle-API DOI validator: a request helper, a long-DOI resolver, a validator, a result interface and worked API response examples. It depends only on one HTTP helper, trivially replaceable, and lifts free of the rule system. The runner-up is a pure URL-to-DOI extractor. Either carries the copyleft if copied.

**Fitting.** *Inputs:* Zotero items chosen inside Zotero, either the selection or a collection's children, or items newly added through a notifier event filtered to regular, non-feed, titled, non-group items; plus rule identifiers or a standard set meaning all preference-enabled non-tool rules. Rules read item fields, creators and the Extra field through a toolkit helper, and one rule reads the best PDF attachment's page count. *Outputs:* in-place mutation of item fields, creators, item type and the Extra field, committed with a save call; a records list shown in an in-application report window; and progress interface. There are no files, notes or exports. *Invocation:* a context-menu submenu, per-field item-pane row menus, a keyboard shortcut, and automatic lint on item add when a preference is set. It is also callable programmatically from inside Zotero through a named global. Tool rules may open a settings dialog, which one preference silences. *Harnesses:* a Zotero desktop add-on whose manifest declares a wide version range. It is not a Claude Code skill or plugin, not Codex, not Obsidian and not a command-line tool.

**Surplus.** Auto-lint on item add with no warn-only mode for most rules is a cost: it mutates items the moment they enter Zotero, outside any vault review gate, and is itself a source of Zotero-side drift the vault must detect. One rule blanks seven field families by regex and is on by default, which is a cost because it will erase values any other plugin or workflow stores in those fields. The DOI resolution rule is on by default and makes one request per DOI-bearing item on every run, which is helpful as verification and costs a network call per item per run. The DOI fill rule makes lookups for items lacking one, which is helpful and costs network, and it skips items in one language. The metadata-update tool uses translators, a scholarly graph API with an optional token, and an identifier resolver, with item-type change allowed by default, which is helpful for enrichment and costs network and possible type rewrites. The Extra-ordering rule rewrites the whole Extra field and places the citation key first, which is neutral to helpful for a pinned key and costs touching a region Better BibTeX also owns. A rich-text toolbar is neutral. Sentence-case, abbreviation, institutional and transliteration rules are neutral for the vault and helpful for citation output, and several are language-specific with one off by default. Duplicate detection on add is helpful. An extra item-tree column is neutral.

**Coverage.**

**C1 does not** (evidence). `src/hooks.ts` line 155, the selection read, with a representative field read in a rule.

```
items = Zotero.getActiveZoteroPane()?.getSelectedItems() ?? [];
```

The plugin runs inside the Zotero process and reads items through the in-process item API. It uses neither named mechanism: a grep of the body at the pin for the port, the two Better BibTeX spellings, the RPC spelling and the citation-key names returns only the Extra-key sort. It reads metadata and, for one rule, an attachment's page count, and it reads no annotations. It exposes nothing readable outside Zotero, so it is not a local-Zotero reader in the sense the requirement names.

**C2 does not** (evidence). `src/api.ts` line 3, the entire exported surface, with a translation service that strips notes.

```
const utils = { getTextLanguage };
```

No code path writes markdown, files or Zotero notes. The only public surface is a language-detection helper. Outputs are in-place field mutations saved through the item API plus an in-application report window.

**C3 does not** (evidence). `src/hooks.ts` line 65, the event filter, with the observer registered for one type.

```
if (event !== "add" || type !== "item")
```

The observer reacts only to in-process add events, to trigger auto-lint. It records no item version, modification date or cursor, persists nothing, and exposes nothing to an external consumer, so drift, orphan and re-key detection are not possible from it. The record notes the inverse: because it mutates items on add, it is itself a source of Zotero-side change a vault would need to detect.

**C4 does not** (evidence). `src/modules/rules/correct-pages-range.ts` line 55, the page-count read.

```
const pages = await Zotero.Fulltext.getPages(attachment.id);
```

The only attachment access reads the page count from Zotero's existing full-text index to fill a page range. No text is extracted, returned or written anywhere. Two rule scopes are declared but unimplemented, which the source marks as an open item.

**C5 does not** (evidence). `src/hooks.ts` line 18, the start-up await, with the bootstrap that loads the bundle.

```
await Promise.all([Zotero.initializationPromise, Zotero.unlockPromise, Zotero.uiReadyPromise]);
```

Start-up awaits Zotero's interface-ready promise and per-window hooks register menus, shortcuts and a toolbar; it is an add-on loaded by a running Zotero desktop, not a command-line tool. It needs no Obsidian, but it is not headless. The in-Zotero programmatic entry point is recorded under invocation rather than as coverage.

**C6 covers** (evidence). `package.json` line 15 with the licence file.

```
"license": "AGPL-3.0-or-later",
```

The licence permits use and modification. Using the plugin as shipped is unencumbered; copying code into other tooling triggers copyleft.

**C7 covers** (evidence). `src/modules/rules/correct-doi-long.ts` lines 82-84, the validation predicate, with the request at line 56, the rule inventory and the rule-id typings.

```
return result.values.some(v => v.type === "URL");
```

Provided, with code present at the pin: DOI verification, where every DOI is resolved against the handle API, short DOIs are expanded to long form through an alias value, and an unresolvable DOI is reported with a specific message; DOI fill through a registry OpenURL query built from a Zotero-generated context object for two item types lacking a DOI, skipping one language; DOI cleaning through a Zotero utility; short-DOI storage in a named Extra key; metadata format lint across about forty rules covering case, creators, date format, page ranges and connectors, leading zeros, journal aliases and abbreviations from bundled data, thesis and institutional fields, edition numerals, nullish values, field misuse and Extra ordering; duplicate detection on add; two item-type sanity rules, one of which only warns; and metadata update through translators, a scholarly graph API and an identifier resolver, with optional type change. Not provided, verified against the seed: PMCID lookup, because that identifier is only extracted from the item field or the Extra field and passed along, with no service requesting or filling it, and although one service maps one identifier to a prefixed form, the update path checks only three identifier kinds and the fetch uses only two, so neither identifier ever drives a request; citation counts, which appear only in an example fixture with no transform writing them; and arXiv version update, since that service only resolves an identifier to a DOI with no version tracking.

No digest-lane row is given. The record states that nothing is plausibly covered, because the body produces no pages, templates, synthesis or file output.

**Treatment opinion: install as-is.** The only requirement this body serves is the enrichment one, and it serves it as a self-contained add-on: DOI verification and fill, DOI cleaning, short-DOI storage, duplicate detection, format lint and identifier-driven metadata update all live in process and need nothing from the vault. Nothing in it produces a note, reads annotations, extracts text, tracks versions or runs headless, so there is no seam to fork or copy for the capture side. The licence decides against every copy path, because the copyleft would pull into vault tooling for a few dozen lines that are cheap to author independently against the same public API. So install the plugin in Zotero, record in the vault what it already provides so the vault does not replicate DOI verification, normalisation or deduplication, and set three named preferences deliberately, because with defaults it mutates items with no warn-only mode. Codex compatibility is moot, since this is neither a Claude Code nor a Codex artifact.

**Facts carried from this body.** Twelve. The shipped manifest declares a wide Zotero range while the repository's own developer instructions name a narrower one, which is documentation lag (F1). Zotero's internal full-text API exposes a page-count object with a total member for an indexed attachment, in process rather than over HTTP (F2). This plugin treats the citation key as an Extra-field key and references no native item field anywhere in the body, which is a negative fact bearing on the register (F3):

```
const isCitationKey = (key: string) => key.toLowerCase() === "citation key" || key.toLowerCase() === "citation-key";
```

Notifier add events for items arriving through sync carry a skip flag in their extra data, which the plugin uses to avoid linting synced items (F4). Calling Zotero's translate search with a false library identifier returns plain field objects rather than saving item records, which the source documents with a citation to the upstream implementation (F5). The menu manager supports per-field item-pane row menus through a named target (F6). The resolver exposes a JSON handle API, where a short identifier resolves through an alias value and a long one is validated by the presence of a URL value (F7). Short identifiers are fetched from a companion service as JSON and stored under a named Extra key (F8). Missing identifiers are looked up through a registry's OpenURL endpoint using a context object Zotero builds from the item (F9). Two biomedical identifiers are read from the native field or from the Extra field but only extracted, with no lookup service using them (F10). Zotero exposes both a cleaning utility and a duplicates search object usable in process (F11). And a notifier observer's priority can be set high so a plugin runs after other plugins' observers, which this project does with a comment explaining that it wants to clean up after them (F12).

The record also notes an internal disagreement about supported Zotero versions between the manifest and two documentation surfaces, and resolves it in favour of the manifest as the shipped artifact. It flags that the repository ships developer instruction files that are for hacking on the plugin rather than a skill or plugin for an agent.

### 38. Zotero enrichment plugins, one catalogue record covering 36 repositories

Seeded as the Zotero plugin catalogue branch, then read as one record rather than 36. The URL field holds all 36 repository URLs. Pin: 2026-09-04, with each body read at its own HEAD SHA, recorded per plugin in the record's facts. Kind: a catalogue of Zotero-side enrichment and lint plugins, all bootstrap add-ons except one Python service.

**Maintenance.** Twenty of the 36 were pushed within 90 days of the read, six of them within the two weeks before it. Six are dormant or dead, including one archived repository, one Zotero 5 plugin whose upstream API has been retired, and two Zotero 6 overlay plugins. Stars range from zero to 1,632, and among the live candidates that load on the current Zotero line the highest are 384, 322, 201 and 90.

**Originator and supplier.** Various independent authors, one per plugin, named in the record's facts. Two vendor plugins are in the set. The supplier for each is its GitHub releases page, and every body was read from the raw file host at the recorded SHA.

**Licence.** Per plugin, listed in the table below. The families present are nine under one weak copyleft, nine under a permissive licence, nine under a strong network copyleft, two under a general copyleft, one under a European public licence, four with no licence anywhere in the body, and two with a README-only claim. Two repositories carry a conflict between their licence file and their package metadata, in both cases a permissive or general copyleft file against a network copyleft declaration.

IP assertions: all of these permit running the plugin inside a user's own Zotero. The copyleft ones matter only if the vault forks or vendors plugin code. The vault reads plugin output from the user's own database, which no plugin licence restricts.

**Verify.** No verify pass ran on this record. The record itself states that all 36 quotes were re-verified byte-for-byte at their recorded file and line, which is an internal check rather than an independent one.

**Smallest part.** Nothing is installed into the vault from this record. The consumable unit is the set of write-target grammars each plugin leaves in the local Zotero database, meaning Extra-line prefixes, tag strings, child-note shapes and sibling-attachment content types, which the vault's capture step must parse and preserve rather than regenerate.

**Fitting.** *Inputs:* a local Zotero library on which zero or more of these plugins have run. The outputs the vault will encounter are all readable through the local API item JSON. Extra lines take at least eight distinct grammars across the set, including two different citation-count forms, a zero-padded legacy marker, a prefixed scholar count, three namespaced keys from one plugin, a bare integer, a summary prefix, a timestamped JSON backup line, and identifier lines. Tags take at least twelve documented vocabularies across DOI status, identifier failure, refresh status, venue and tier, conversion status, and a retraction flag. Child notes take four documented shapes, one of which carries an explicit do-not-edit warning. Sibling attachments include markdown files and an OCR'd PDF with a text layer. Two plugins keep state outside the item, one in a database file in the Zotero data directory and one in a results folder in the profile that is queryable over Zotero's own local HTTP port. *Outputs for the vault:* three things. A parse-and-preserve rule set, so the literature note's managed region may surface identifiers, counts with their source and date, summaries, venue and tier tags, and markdown or OCR availability by reading those grammars, while round-tripping the Extra field untouched. A do-not-build list, because identifier validation, identifier resolution, citation counting, version update, metadata refresh, name lint, OCR and layout parsing are all available on the Zotero side. And an install shortlist for the reader's own Zotero version. *Invocation:* each plugin is installed into Zotero from its own release file and run from context menus, the tools menu or add notifiers. None is invoked by the vault, which only reads their results. *Harness for verification:* fixture items carrying each Extra grammar and tag string, asserting that capture extracts the fields it wants, leaves the Extra field byte-identical on write-back, and does not add its own identifier, count or summary lines. Loadability was judged from each manifest's declared version range rather than by installing, and the record names three plugins where a live install check is still needed.

**Surplus.** Twelve entries are recorded as superseded, dead or out of scope so the same ground is not swept again: the origin plugin of the identifier lineage and the origin plugin of the counts-in-Extra design, both version-capped below the current line; two count plugins whose live fork is elsewhere; three summary plugins, one archived, one capped, one that is a chat sidebar rather than a summary fetcher; two dead plugins on retired platforms or APIs; one off-site graph search that writes nothing; one vendor plugin that keeps its tallies in memory only, so nothing is readable from the database; one converter capped below the current line, unlicensed and cloud-dependent; one unlicensed count plugin that writes a bare number and strips other plugins' count lines, which is destructive to their data; one scraper whose terms-of-service position is fragile and which needs a pinned older release; one plugin that is current-line-only at HEAD with a pinned older release for the previous line; and the Python half of one project, which uses the web API while its bundled plugin half is the local write path.

**Coverage.** Seven C7 rows, scored by capability group rather than one row per plugin.

**C7 covers, DOI and identifier group, five plugins** (evidence). Four cited locations across four bodies.

```
doi-updater.js:164 'if (prefs.tagInvalid) item.addTag(prefs.tagInvalid, 1);' with manifest.json:11-12 8.0-10.0.*; doiManager.js:21 'const TAG_NO_DOI = "doi-fix:no-doi-found";' with manifest.json:13-14 7.0-10.*; index.ts:19 'const TAG_NO_DOI = "MetadataHunter: No DOI";' with addon/manifest.json:10-11 6.999-10.0.*; lib.ts:253 'item.extra.push(`${field}: ${value}`)' (PMID/PMCID) with update.pug:13 maxVersion 7.0.*
```

Verification, cleaning, short-and-long conversion, registry lookup for missing identifiers and monthly re-verification are provided by three plugins that load on the current line under three different licences; all write the identifier field in place and signal failures with documented tag strings the vault can read as-is. The biomedical identifier lookup exists in only one plugin, which writes two Extra lines but has no licence file and no manifest in the body, so its loadability is unverified from the body. The origin plugin cannot load. The vault should not replicate identifier validation or resolution.

**C7 covers, citation counts and citation lists, eleven plugins** (evidence). Six cited locations across six bodies.

```
UNT_PREFIX = "openalex.cit_count:";'; bootstrap.js:853 'const citationLine = `${sourceResult.count}`;'; lib.ts:193 api.scite.ai/tallies with no setField anywhere in scite lib.ts; opencitations.ts:119 'https://opencitations.net/index/api/v2/references/'
```

Counts from seven services are all provided. Four plugins load on the current line unmodified, and two of the highest-starred need their pinned older releases. Every count plugin except one persists into the Extra field with a distinct grammar, six forms in total, which the vault can parse but must not overwrite. One plugin keeps tallies in memory only, so its data is not readable from the database. One plugin is the only one that stores full citation lists rather than counts, and the only one that queries one particular open citation index. Three plugins in the lineage are dead or non-loading.

**C7 partial, summary group, three plugins** (evidence). Three cited locations.

```
tldrFetcher.ts:11 'const TLDR_LINE_PREFIX = "TLDR: ";' with zTLDR addon/manifest.json:16-17 6.999-8.*; Zotero-TLDR tldrFetcher.ts:55 'note.setNote(`<p>TL;DR</p>\n<p>${info.tldr}</p>`);' with addon/manifest.json:16-17 6.999-7.0.* and repository archived; zoTLDR llm.ts:35 generativelanguage.googleapis.com with addon/manifest.json:16-17 7.999-8.*
```

Summary retrieval from a scholarly service is implemented, one plugin writing an Extra line and the other a child note, but neither manifest admits the current Zotero line and one repository is archived, while the third is a chat sidebar rather than a summary fetcher. The negative finding is explicit: no plugin in the sweep that fetches these summaries loads on the current line. If the vault wants them it must fetch them itself or fork one plugin by raising its version ceiling, and it should still recognise the Extra prefix and the note shape in libraries that used them.

**C7 covers, version update and metadata refresh, five plugins** (evidence). Five cited locations across five bodies.

```
arxiv-merge.ts:159 'preprintItem.setType(publishedItem.itemTypeID);' with README.md:34 keeping the arXiv item ID and addon/manifest.json:16-17 7.999-10.*; utilities.js:557 'item.setField(\'archiveID\', "arXiv:" + identifiers.arxivID);' with src/manifest.json:11-12 7.0-9.0.*; engine.ts:499 'const line = `[${BACKUP_TAG} ${stamp}] ${JSON.stringify(payload)}`;' with addon/manifest.json:14-15 7.0-9.*; ArxivProcessor.ts:86 'item.addTag("Updated to Published Version", 1);' with addon/manifest.json:10-11 8.0-9.*; resolver.js:552 'kept.push(`Citations: ${res.citation_count} (SemanticScholar) [${today}]`);'
```

All five load on the current line. One merges preprint and published items while keeping the preprint's item id, so item-keyed plugin data survives, detects newer versions from several preprint servers, and downloads the published file while keeping both. One refreshes from three identifier kinds and creates parents for orphan PDFs from the full-text cache. One refreshes from four services with a preview, a field whitelist and a restorable timestamped backup line in the Extra field. One validates attachments, refreshes from six services and converts preprints. One resolves venue and tier, converts the item type, writes two tag vocabularies and a count line. The vault must not refresh metadata itself and must treat item-type changes, backup lines and these tag vocabularies as plugin-owned.

**C7 partial, metadata-format lint and pre-admission verification, two plugins** (evidence). Two cited locations.

```
README.md:34 '- Fix diacritics vs ASCII mismatches (e.g. "Miłkowski" vs "Milkowski")' with item-processor.js:117 applyNormalizations and manifest.json:17-18 6.999-9.0.*; zotero.ts:291 'note.setNote(buildVerificationNote(row));' with client.ts:14-15 '/api/retraction-check — Crossref + Retraction Watch' / '/api/oa-check — Unpaywall' and addon/manifest.json:17-18 7.0-9.*
```

One plugin lints and fixes creator, publisher, place and journal name variants in place after a review dialog, and is the only metadata-format linter found; it covers names only rather than field-format lint in general, and no date, identifier or page-range lint exists anywhere in the sweep, which is why the row is partial. The other verifies pasted bibliography files against a cloud API with a retraction check and an open-access check, and imports new items with a provenance child note and a retraction tag, but does not lint existing items. The vault should not normalise names itself and should treat that tag and those provenance notes as plugin-owned.

**C7 covers, OCR and PDF-to-markdown, seven plugins** (evidence). Seven cited locations across seven bodies.

```
rapidocr hooks.ts:258 Zotero.Attachments.importFromFile and :266 'indexItems: (ids, opts) => Zotero.Fulltext.indexItems(ids, opts),' with README.md:16 'PP-OCRv4（onnxruntime-web WASM）', README.md:19 '不访问网络（识别在本地）' and addon/manifest.json:16-17 9.0-10.0.*; convert.ts:1 '// Core conversion flow: read PDF → POST to docling-serve → attach .md back.' with prefs.js:2 serverUrl http://localhost:5001; mineru-client.js:7 'https://mineru.net/api/v4'; mineru prefs.js:4 'pref("localApiBaseURL", "http://127.0.0.1:8000");'; mdbundle.js:357 'let text = await pdfAtt.attachmentText;' and :361 addTag('needs-ocr'); mistralClient.js:2 'API_BASE: "https://api.mistral.ai/v1",' with manifest.json:13-14 7.0-7.*; context-menu.ts:1066 'const note = new Zotero.Item("note");'
```

Fully local OCR exists in one plugin, running in process and writing a sibling text-layer PDF that it then indexes. Local PDF-to-markdown exists through a user-run conversion server in one plugin, which attaches a markdown sibling and tags three outcomes, and through a self-hosted server in another, whose results land in the profile folder and are exposed over Zotero's own local HTTP port with a command-line skill file alongside. Three plugins are cloud-only. One re-uses Zotero's own full-text cache and tags items that need OCR. The vault should not implement OCR or layout parsing; for local text it can read those outputs or Zotero's cache, and must recognise the status tags and the markdown sibling attachments as plugin-owned.

**C7 does not, non-enrichment or dead, four plugins** (evidence). Four cited locations.

```
inciteful.ts:95 'launchURL("https://inciteful.xyz/p", params);' (off-site, no writes); semantic-zotero install.rdf:15 '<em:maxVersion>6.*</em:maxVersion>'; mas-metadata install.rdf:16 '<em:maxVersion>5.0.*</em:maxVersion>' and masAPIQuery.js:3 api.labs.cognitive.microsoft.com (retired API); zoTLDR addon/manifest.json:16-17 7.999-8.*
```

Recorded so the branches are not re-searched. One sends collections off-site and writes nothing, two cannot load on any current Zotero, and one is a chat sidebar. None provides enrichment the vault would otherwise replicate.

**Treatment opinion: install as-is, per plugin, with no plugin code entering the vault.** Eighteen of the 36 are usable as-is on the reader's Zotero version, each with a licence file in the body and a manifest range covering it; the record names all eighteen with their licence and range. Because the requirement asks only that the vault know what these provide so it does not replicate it, the treatment is to install the chosen ones unchanged in Zotero and have the vault parse their outputs. The one gap is the summary group, where nothing loads on the reader's line, which would require forking one plugin by raising its ceiling or having the vault fetch the summaries itself.

**Per-plugin table.** One row per repository, drawn from the record's 36 facts. The compatibility column reproduces the manifest range the reader found in the body, which is what decides loadability, together with the star count and push date at the read.

| Repository (record id)               | Provides                                                                                                                                                   | Writes into Zotero                                                                                                                                           | Licence                                                          | Compatibility and activity                                                                                                    |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| zotero-pmcid-fetcher                 | PMID + PMCID resolution from an item's DOI via NCBI eutils esearch (lib.ts:326) and the PMC idconv service (lib.ts:366), throttled at one request per ...  | to the PMID/PMCID item field when the item type has one, otherwise appends 'PMID: <n>' / 'PMCID: <n>' lines to Extra (lib.ts:249-253, 440); optional M ...   | none, no LICENSE file in the tree, no license field in ...       | no manifest in the repo (generated at build by 'zotero-plugin/make-manifest', esbuild.js:7); the only version range in t ...  |
| zotero-doi-manager                   | DOI verification and cleaning, resolves via doi.org handles API, converts short/long via shortdoi.org, strips URL/text prefixes, looks up Crossref Op ...  | the DOI field in place (README.md:17); status tags with defaults '⚠️ Invalid DOI', '❓ Multiple DOI', '⛔ No DOI found' (prefs.js:4-6; doi-updater.js:16 ... | MPL-2.0 (LICENSE)                                                | manifest.json:11-12 strict_min_version 8.0 / strict_max_version 10.0.\*, loads on 9.0.6. Continuation of bwiernik/zotero ...  |
| zotero-shortdoi                      | the origin of the DOI validate/clean/shortDOI logic, Crossref auto-fetch of DOIs, shortdoi.org lookup, 'Verify and clean DOIs' that marks invalid DOI ...  | DOI field in place; invalid/no-DOI/multiple tags from prefs.                                                                                                 | MPL-2.0 (LICENSE)                                                | manifest.json:15-16 6.999-7.0.*; install.rdf:21-22 6.0-7.*, will NOT load on Zotero 9. Idea source only; superseded by ...    |
| zotero-doi-fix                       | missing-DOI retrieval from Crossref OpenURL (doiManager.js:292) then Crossref REST works search by title/author/year with a title-similarity gate (doi ... | the DOI field, or an Extra line when the item type has no DOI field ('saved to Extra', doiManager.js:106-110, 230-234); status tags doi-fix:no-doi-fou ...   | MIT (LICENSE)                                                    | manifest.json:13-14 7.0-10.\*, loads on 9.0.6. 16 stars, pushed 2026-07-05, HEAD a3a3eca.                                     |
| zotero-metadata-hunter               | missing-DOI lookup in the order CrossRef (index.ts:521) → DBLP (562-564) → Semantic Scholar (800) → arXiv (769); abstract lookup in parallel from Sema ... | DOI field (index.ts:1070, 2223), abstractNote (1100, 2184), other fields in place; status tags 'MetadataHunter: No DOI', 'MetadataHunter: No Published ...   | EUPL-1.2 (LICENSE; package.json:14)                              | addon/manifest.json:10-11 6.999-10.0.\*, loads on 9.0.6. 34 stars, pushed 2026-08-31, HEAD 017cc64.                           |
| zotero-citation-tally                | citation counts from Crossref 'is-referenced-by-count' (citationTally.ts:841-865), INSPIRE 'citation_count' (917-951) and Semantic Scholar (optional A ... | one Extra line per source of the form 'Citations: N (crossref) [YYYY-MM-DD]' (extraField.ts:14), inserted before the BBT 'Citation Key:' line (citatio ...   | AGPL-3.0 (LICENSE; package.json:7)                               | HEAD addon/manifest.json:16-17 strict_min_version 9.999 / 10.\*, Zotero 10 only at HEAD; README.md:38 'The last release ...   |
| zotero-citation-counts-tangzhao20    | citation counts from Crossref, INSPIRE-HEP and Semantic Scholar (zoterocitationcounts.js:43-63; README.md:14), Crossref title search when the item has ... | a single Extra line 'N citations (Source) [YYYY-MM-DD]' at the top of Extra, replacing prior 'N citations'/'Citations:' lines (zoterocitationcounts.js ...   | MPL-2.0 (LICENSE)                                                | manifest.json:11-12 6.999-9.\*, loads on 9.0.6; README.md:15 'compatible with Zotero 8 and Zotero 9'. Fork lineage: esch ...  |
| zotero-open-citations                | a sortable citation-count column (lib/open-citations.js:550-558) filled from OpenAlex works API by DOI or title search, no key (197-202, primary); Cro ... | Extra line 'ZSCC: 0000042' (zero-padded, the legacy Scholar Citations marker, lib/open-citations.js:10, 165-176; README.md:56) when writeExtra is on; ...    | MPL-2.0 (LICENSE)                                                | manifest.json:17-18 6.999-9.\*, loads on 9.0.6. 0 stars, pushed 2026-06-24, HEAD d6304a1.                                     |
| zotero-google-scholar-citation-count | Google Scholar citation counts scraped from scholar.google.com (gscc.js:241 defaultGsApiEndpoint) with three columns gsccCount, gsccCountUpdated and g ... | an Extra line prefixed 'GSCC:' with a zero-padded count (gscc.js:195, 613-637, 861-868).                                                                     | MPL-2.0 (LICENSE; package.json:7 'MPLv2')                        | HEAD src/manifest.json:16-17 9.999-10.\* (v7.0.0, Zotero 10); README.md:16 pins v6.0.0 for Zotero 9. 421 stars, pushed 20 ... |
| scite-zotero-plugin                  | five item-tree columns, Supporting, Contrasting, Mentioning, Total Smart Citations, Total Distinct Citing Publications (client/content/columns.jsx:19 ...  | nothing on the item, tallies are held in memory (lib.ts:200 this.tallies) and served to columns; lib.ts contains no setField/addTag/setNote. Conseque ...    | none, no LICENSE file, no license field in package.jso ...       | client/manifest.json:10-11 6.999-8.0.\*, may not load on 9.0.6; lib.ts:88 'only supports Zotero 7 and after'. 862 stars, ...  |
| zotero-cita                          | full citation LISTS (not just counts) fetched per item from Wikidata, Crossref, Semantic Scholar, OpenAlex and OpenCitations (README.md:7, 28; src/cit ... | identifiers DOI/QID/OMID/arXiv/PMID/PMCID/CorpusID/OpenAlex on the item (src/cita/PID.ts:27-42, sourceItemWrapper.ts:601); citation records serialised ...   | GPL-3.0 (LICENSE.md; package.json:35 GPL-3.0-or-later)           | static/manifest.json:17-18 6.999-10.0.\*, loads on 9.0.6. 322 stars, pushed 2026-09-03, HEAD 5e577eb.                         |
| zotero-openalex                      | OpenAlex work resolution by DOI/arXiv URL (openalex.ts:16, 528-541), citation count column (openalex.ts:402-414), citation/co-author graphs per collec ... | not recorded                                                                                                                                                 | not recorded                                                     | addon/manifest.json:16-17 6.999-10.\*, loads on 9.0.6. 16 stars, pushed 2026-08-18, HEAD d7c08eb.                             |
| zotero-citationcounts-eschnett       | the origin of the counts-in-Extra design, Crossref, INSPIRE, (ADS commented out) and Semantic Scholar v1 API (chrome/content/scripts/zoterocitationco ...  | Extra line 'N citations (Source) [YYYY-MM-DD]' unshifted to the top (zoterocitationcounts.js:39-58); README.md:31 'they are stored in the Extra field' ...   | MPL-2.0 (LICENSE)                                                | install.rdf:20-21 minVersion 6.0 / maxVersion 6.\*, Zotero 6 only, overlay-era, dead. 932 stars, pushed 2023-11-09, HEAD ...  |
| ZoteroCitationCountsManager-FrLars21 | Crossref/INSPIRE-HEP/Semantic Scholar counts (zoterocitationcounts.js:42-62, 529-552) and a 'Citation Counts' column (README.md:16).                       | Extra line 'N citations (Source) [YYYY-MM-DD]' (zoterocitationcounts.js:391-400).                                                                            | MPL-2.0 (LICENSE)                                                | manifest.json:11-12 6.999-7.0.\*, will not load on Zotero 9; update_url points at zotero's make-it-red sample (manifest. ...  |
| ZoteroCitationCountsAgent-flychen50  | FrLars21 fork adding NASA ADS with a bearer API key and title/author/year fallback (src/zoterocitationcounts.js:80-87, 599-601; README.md:15-16, 49-53 ... | Extra line via \_setCitationCount (src/zoterocitationcounts.js:445-477).                                                                                     | MPL-2.0 (LICENSE; no license field in package.json)              | manifest.json:11-12 6.999-7.0.\*, will not load on Zotero 9. 6 stars, pushed 2025-11-06, HEAD 600519b.                        |
| zotero-getcitation                   | a 'Citations' column (bootstrap.js:29-30, 118-120) filled through a fallback chain Semantic Scholar graph API → Crossref → INSPIRE-HEP (bootstrap.js:5 ... | a bare number as the first line of Extra (bootstrap.js:847-854; README.md:14 'Stores the result in Extra as a plain number such as 188'), stripping pr ...   | none, no LICENSE file and no package.json in the tree            | manifest.json:16-17 6.999-9.\*, would load on 9.0.6. 0 stars, pushed 2026-04-03, HEAD 445f4fe.                                |
| zTLDR                                | Semantic Scholar TL;DR summaries fetched from the graph API by DOI (tldrFetcher.ts:160) or title match (216), auto on item add (README.md:22), shown i ... | an Extra line 'TLDR: <text>' inserted at the top, other lines preserved (tldrFetcher.ts:11, 109-127).                                                        | AGPL-3.0 (LICENSE; package.json:22)                              | addon/manifest.json:16-17 6.999-8.\*, will not load on 9.0.6. Negative finding for the group: no Zotero-9-loadable S2 TL ...  |
| Zotero-TLDR-syt2                     | auto-fetched Semantic Scholar TL;DR for all items (README.md:6, 16) displayed in the item pane; uses the undocumented site endpoint https://www.semant ... | a child note '<p>TL;DR</p><p>…</p>' (tldrFetcher.ts:41-55) and a note-key map in plugin data storage (dataStorage.ts:122).                                   | AGPL-3.0 (LICENSE; package.json:29)                              | repository ARCHIVED (GitHub API archived=true); addon/manifest.json:16-17 6.999-7.0.\*, Zotero 7 only. 61 stars, pushed ...   |
| zoTLDR-menyoung                      | not recorded                                                                                                                                               | chat transcripts as child notes tagged zs-chat and responses as standalone notes tagged zs-note (README.md:59-60; noteWriter.ts:24-35, 56-57). Cloud L ...   | MIT (LICENSE; package.json:22)                                   | addon/manifest.json:16-17 7.999-8.\*, not loadable on 9.0.6. Recorded so the TL;DR search is not repeated. 2 stars, push ...  |
| zotero-arxiv-workflow                | arXiv version update, merges a preprint with its published item while keeping the preprint's item ID so item-keyed plugin data survives (README.md:33 ...  | item type and fields in place; new PDF attachment.                                                                                                           | AGPL-3.0 (LICENSE; package.json:32)                              | addon/manifest.json:16-17 7.999-10.\* (README.md:18 'alpha stage and only supports Zotero 8, 9, and 10'); update.json:10 ...  |
| ZotMeta                              | bulk metadata refresh, journalArticle from DOI via doi.org content negotiation (journal.js:91), book from ISBN via openlibrary.org books API (book.js ...  | fields in place (DOI, archiveID 'arXiv:…', repository, url, utilities.js:553-565); 'skipped'/'failed' status tags (utilities.js:423-449).                    | MIT (LICENSE)                                                    | src/manifest.json:11-12 7.0-9.0.\* (README.md:37 'supports Zotero 7.0 through 9.0.x'); install.rdf mirrors it. 201 stars, ... |
| zotero-meta-refresh                  | batch metadata refresh from CrossRef by DOI or bibliographic query (sources.ts:88, 100), OpenAlex (186, 189), Semantic Scholar by DOI/arXiv/title (257 ... | whitelisted fields and author creators in place (editors/translators kept); when backupToExtra is on, one JSON line '\[MetaRefresh <ISO stamp>\] {"field ... | AGPL-3.0 (LICENSE; package.json:19)                              | addon/manifest.json:14-15 7.0-9.\*, loads on 9.0.6. 0 stars, pushed 2026-06-19, HEAD b676c98.                                 |
| zotero-zotadata                      | attachment validation that moves broken file attachments to the trash while keeping valid PDFs and web links (AttachmentChecker.ts:156-168, 224-226; R ... | not recorded                                                                                                                                                 | not recorded                                                     | addon/manifest.json:10-11 8.0-9.\*, loads on 9.0.6 (README.md:5). 90 stars, pushed 2026-08-21, HEAD 782c547.                  |
| arxiv-marker                         | resolves the real venue of arXiv preprints via the Semantic Scholar batch API keyed on arXiv id (resolver.js:164-165, 223) and DBLP title search (237) ... | item type conversion and venue fields (arxiv-marker.js:111-125), tags 'venue:<canonical>' and 'CORE:<tier>' (resolver.js:358-360), Extra lines 'Citati ...   | MIT (LICENSE)                                                    | plugin/manifest.json:12-13 6.999-99.99.99 (README.md:14 'Zotero 7/9 plugin'). 9 stars, pushed 2026-06-11, HEAD 56683f9.       |
| zotero-ner                           | not recorded                                                                                                                                               | creator names and publisher/place/journal fields in place after review (item-processor.js:117-135; zotero-ner.js:835-839).                                   | GPL-3.0 (LICENSE)                                                | manifest.json:17-18 6.999-9.0.\*, loads on 9.0.6 (README.md:20 'tested on Zotero 7/8'). 22 stars, pushed 2026-06-15, HEA ...  |
| scholar-sidekick-zotero              | not recorded                                                                                                                                               | creates NEW items from the resolved metadata in a chosen collection (import/zotero.ts:273), a 'Retracted' tag when flagged (280), and a child provenan ...   | MIT (LICENSE; no license field in package.json)                  | addon/manifest.json:17-18 7.0-9.\*, loads on 9.0.6 (README.md:37 'proven on Zotero 9'). 4 stars, pushed 2026-08-05, HEAD ...  |
| semantic-zotero                      | fetches the reference list of a selected paper from the Semantic Scholar graph API (chrome/content/semanticZotero.js:62, 126) and lets the user add ch ... | new items.                                                                                                                                                   | MIT (LICENSE)                                                    | install.rdf:14-15 6.0-6.\*, Zotero 6 overlay plugin, dead; not loadable on 7+. Superseded by Cita for in-library citatio ...  |
| inciteful-zotero-plugin              | not recorded                                                                                                                                               | nothing to Zotero.                                                                                                                                           | AGPL-3.0 (LICENSE; package.json:22)                              | addon/manifest.json:16-17 7.999-10.99.99 (README.md:3 'works with Zotero 10 and continues to support Zotero 8 and 9'). R ...  |
| rapidocr-for-zotero                  | not recorded                                                                                                                                               | a new sibling PDF attachment carrying the text layer, imported via Zotero.Attachments.importFromFile and then indexed with Zotero.Fulltext.indexItems ...    | no LICENSE file; README.md:96 'MPL-2.0。OCR 模型来自 PaddleO ... | addon/manifest.json:16-17 9.0-10.0.*, loads on 9.0.6; uses Zotero 10 APIs with shims (scripts/zotero10-*.js). 1 stars, ...    |
| zotero-docling                       | not recorded                                                                                                                                               | the .md as a sibling attachment via Zotero.Attachments.importFromFile with contentType text/markdown when attachToItem is on (convert.ts:709, 732-735; ...   | AGPL-3.0 (LICENSE; package.json:22)                              | addon/manifest.json:16-17 6.999-\* (README.md:3 'Zotero 7 or later'), loads on 9.0.6. 12 stars, pushed 2026-09-03, HEAD ...   |
| mktero                               | not recorded                                                                                                                                               | not an attachment by default, a Zotero 'snapshot' (HTML+Markdown+source maps) can be saved to a writable library (README.md:42-45, 58) and the correc ...    | MIT (LICENSE; no license field in package.json)                  | manifest.json:15-16 7.0-10.0.\*, loads on 9.0.6. 32 stars, pushed 2026-09-01, HEAD 3f5baaf.                                   |
| mineru-for-zotero                    | not recorded                                                                                                                                               | parse results (Markdown, box data, images) into a result folder under the Zotero profile, not as attachments (README.md:73; parseManager.ts storage); ...    | AGPL-3.0 (LICENSE; package.json:22)                              | addon/manifest.json:16-17 6.999-9.\*, loads on 9.0.6. 4 stars, pushed 2026-09-02, HEAD 946cadb.                               |
| MdBundle-for-Zotero                  | pairs PDF and .md attachments by identical base filename (README.md:16), exports pairs to a folder, diagnoses attachment health (README.md:34), and 'g ... | a .md file next to the PDF containing a title/authors/year header plus the cached text, linked as a child attachment via Zotero.Attachments.linkFromFi ...   | no LICENSE file; README.md:6 shows an MIT badge only             | src/manifest.json:16-17 6.999-9.\*, loads on 9.0.6. 3 stars, pushed 2026-07-27, HEAD 1ec7473.                                 |
| ZotPDF2md                            | not recorded                                                                                                                                               | .md files into a user-chosen export directory (pdf2markdown.js:265-283; README.md:38), NOT attached to the item.                                             | none, no LICENSE file and no licence statement in READ ...       | manifest.json:13-14 7.0-7.\*, will not load on Zotero 9. 0 stars, pushed 2026-02-18, HEAD aabf248.                            |
| zotero-AI-OCR                        | not recorded                                                                                                                                               | the recognised Markdown converted to HTML as a child note titled by template '<engine> (Pages …)' on the parent item (context-menu.ts:1060-1072; READM ...   | AGPL-3.0 (LICENSE; package.json:22)                              | addon/manifest.json:16-17 6.999-9.\*, loads on 9.0.6 (README.md:22 'Zotero 7/8/9 插件'). 1 stars, pushed 2026-08-30, HEAD ... |
| zotero-mas-metadata                  | metadata and estimated citation count (ECC) from the Microsoft Academic Search API at api.labs.cognitive.microsoft.com/academic/v1.0/ with a user key ...  | the count into Extra (masmetadata.js:324-352).                                                                                                               | MIT (LICENSE)                                                    | install.rdf:15-16 minVersion 5.0.79 / maxVersion 5.0.*, the body says Zotero 5 only, not 6.* as previously claimed. Rec ...   |

**Discrepancies the record found between the bodies and what it had been told.** Eleven, recorded rather than smoothed. One plugin's declared maximum version is a full generation lower than claimed. Two repositories declare a different licence in their package metadata than in their licence file. One owner slug in the seed list had one character too many and returned a 404. One plugin has no manifest in its tree at all, since it is generated at build time, and no licence anywhere, so its only version evidence is an update template. One vendor plugin persists nothing on items, so its tallies are not readable from the database. One summary plugin calls an undocumented site endpoint rather than the documented graph API. One converter's unidentified engine turns out to be Zotero's own full-text cache, so no OCR is performed. One project's update manifest and its add-on manifest disagree about the minimum version. One unlicensed count plugin strips other plugins' count lines from the Extra field, so installing it alongside two others loses their data. And one star count was one higher than claimed.

The record also flags a collision the vault must handle: three plugins write one count grammar and four write another, and only one of them parses both.

### 39. zotero-chinese/zotero-plugins

Seeded, after the seeded URL turned out to be a 404 and the catalogue was located at its real owner. `https://github.com/zotero-chinese/zotero-plugins`. Pin `main@cbb7245b0af3f2a581128debd9818dd280b8cec9`, committed 2026-09-01, with the deployed data branch read separately at its own commit of 2026-09-05 and attributed as such. Kind: a plugin catalogue. It is a TypeScript data repository holding a repository list and a fetch script, which publishes a JSON index and mirrored add-on files. It is neither a Zotero plugin nor a capture tool.

**Maintenance.** 685 stars; the last push is a bot deploy and the last source commit is a dependency bump. The repository description is prefixed with a maintenance-suspended marker, and the status section says submissions are closed with an archive planned. A daily cron still deploys, but what it deploys is another project's release file.

**Originator and supplier.** The copyright holder is Northword, whose package metadata still points at a personal repository URL, and the project describes itself as a reimplementation of an earlier catalogue. The supplier is the community organisation that now owns the repository.

**Licence.** MIT, found, at `LICENSE` lines 1-9 with the package metadata agreeing.

```
MIT License

Copyright (c) 2023 Northword

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software
```

IP assertions: only the copyright notice. The catalogue's licence does not cover the listed plugins, which carry their own.

**Verify.** One pass ran; no row was refuted. Licence and pin confirmed at the pin.

**Smallest part.** The metadata-tagged entries of the repository list plus the deprecated list: a repository-name, target-version and release-channel list that can be read without the fetch pipeline. One caveat: the live index now lives in a successor project, whose per-plugin files carry only tags, while its released index file carries per-release identifiers, versions and both minimum and maximum Zotero versions, and it is that file the build now deploys.

**Fitting.** *Inputs:* the two source lists, an API token, the GitHub REST API through a client library, and add-on archive contents. *Outputs:* two JSON indexes, mirrored add-on files, a badge file and a chart file, deployed to a pages branch and to a public site. *Invocation:* two documented package scripts. But the actual build at the pin has the data-fetch line commented out and instead downloads the successor project's release file, while the chart file is re-downloaded from the old deployed copy with a dated note about an API fault. *Harnesses:* a command-line script plus a scheduled workflow that deploys and then notifies a website repository. There is no Claude Code, Codex or Obsidian surface, and it is consumable only as a JSON URL.

**Surplus.** Add-on mirroring with rewritten links across four mirrors is a cost irrelevant to the vault that adds a distribution concern. Chart and dashboard data are neutral. Locale translation of repository descriptions is neutral. A legacy manifest-parsing fallback is neutral. A mirror-sync workflow and a website notification are neutral. Repository tooling is neutral.

**Coverage.**

**C1 does not** (evidence). `src/handler/plugins-data.ts` lines 41-43, the repository fetch.

```
await octokit.rest.repos.get({ owner, repo }).then((resp) => {
    plugin.description = translateString(resp.data.description)
    plugin.stars = resp.data.stargazers_count
```

The only data sources in the body are the GitHub REST API and the downloaded archive. Nothing opens the local port, Better BibTeX or a Zotero database. The catalogue never reads a Zotero library.

**C2 does not** (evidence). `src/index.ts` lines 41-42, the two output writes.

```
fs.outputJSONSync(`${dist}/plugins-debug.json`, pluginsInfoDist, { spaces: 2 })
  fs.outputJSONSync(`${dist}/plugins.json`, pluginsInfoDist)
```

The outputs are four JSON files and mirrored archives. There is no markdown, no per-item note and no citekey concept anywhere in the body.

**C3 does not** (evidence). `src/handler/plugins-data.ts` lines 101-103, the release asset fields.

```
release.assetId = asset.id
  release.releaseDate = asset.updated_at
  release.downloadCount = asset.download_count
```

The only change detection is per release asset. There is no Zotero item version, since parameter or modification date handling.

**C4 does not** (evidence). `src/handler/plugins-data.ts` lines 162-166, the archive read.

```
const zip = new AdmZip(filePath)
  const zipEntries = zip.getEntries()
  const zipEntryNames = zipEntries.map(zipEntrie => zipEntrie.entryName)

  if (zipEntryNames.includes('manifest.json')) {
```

The only file parsing is unzipping an add-on to read its manifest. There is no PDF or attachment text extraction.

**C5 does not** (evidence). `package.json` line 21, the fetch script, with the token check in the entry point.

```
"data:info": "tsx src/index.ts fetchPlugins",
```

The script is headless and is run by a scheduled workflow, but it performs no capture, and there is no literature-note production to run headlessly, so the requirement is not met in substance.

**C6 covers** (evidence). `LICENSE` lines 1-3.

```
MIT License

Copyright (c) 2023 Northword
```

The licence permits use and modification. It applies to the catalogue code and data only, and each listed plugin has its own licence, which the record records per plugin.

**C7 partial** (evidence). `src/plugins.ts` lines 1254-1261, one entry, with eight more entry ranges named and one deprecated entry.

```
repo: 'retorquere/zotero-pmcid-fetcher',
    releases: [
      {
        targetZoteroVersion: '7',
        tagName: 'latest',
      },
    ],
    tags: ['metadata'],
```

The catalogue provides no enrichment itself; it is a typed data list that indexes the enrichment plugins under a metadata tag with a target version and a release channel. It answered the seed by naming, for each seeded capability, which plugin provides it and for which Zotero versions, in five capability groups. What each plugin reads and writes was then recorded from that plugin's own body at its own SHA, so the vault knows what not to replicate. One caveat is load-bearing: at the pin the catalogue's own list is no longer what gets published.

**Treatment opinion: take nothing.** There is nothing here to install or fork for the capture lane: the body is a scraping build script and a static repository list, it never touches Zotero, and its own pipeline is commented out in favour of downloading the successor project's release file. The status section says submissions are closed and the repository will be archived. Its value was as a lookup, which this pass has consumed: the seeded enrichment plugins are identified and their behaviours recorded. Each of those plugins would need its own record, and installing them is a Zotero-side decision rather than a vault dependency.

**Facts carried from this body.** Fifteen. The catalogue is on hold, no longer accepts submissions and plans to archive, with new plugins going to a named successor (F1). At the pin the deployed index is not produced by this repository's own pipeline but downloaded from that successor's latest release, with the original line commented out immediately above (F2). The successor holds one file per plugin carrying only tags, while its released index carries per-release identifiers, versions and both version bounds, which makes a mechanical compatibility check possible (F3). The biomedical identifier plugin resolves through two named services and writes to the native field when valid for the item type and otherwise as an Extra line, throttled to the service's rate limit, with an optional automatic mode and optional subject headings added as tags (F4). That same plugin has no licence anywhere, so default all-rights-reserved applies (F5). One count plugin prepends its own line format to the Extra field from three services, reading only two fields, and does not run on current Zotero (F6). Another writes a different line format, strips its own legacy formats first, and deliberately inserts its stamp above a Better BibTeX citation-key line (F7). The origin identifier plugin validates against the handle API, fetches short forms, looks up missing identifiers through a registry, writes the field and marks failures with three configurable tags, and does not run on current Zotero (F8). The version-update plugin finds the published version through six routes and then merges it into the preprint item, so the preprint's key, collections, dates, tags and relations survive while its type and fields change, and it pins a random citation key on the merged-away item to avoid a key collision (F9). That last point is the one with a direct consequence for a citekey-keyed vault, which the record states plainly: the surviving item's citekey may regenerate because the year and type change, unless it is pinned, and unannotated preprint files may be trashed. The lint plugin is the current-line-capable identifier verifier, with three named rules and their behaviours (F10). Its metadata-update tool refreshes through an ordered service chain with the preprint service first, recognises six preprint servers, and can auto-run on item add through a preference with a delay, registered at a high observer priority so it runs after other plugins (F11). Five in-process Zotero helpers are named that a vault-side or plugin-side implementation could rely on, including structured parsing and recombination of the Extra field, item merging, identifier cleaning, context-object construction and field validity checking (F13). The catalogue derives each plugin's identifier and version from the archive's own manifest, so the published identifiers are the installed-plugin identifiers (F14). And one count plugin states that a major search service is not supported because automated access is against its terms of service, which the record marks as README-sourced and used only to narrow (F15).

The record's own resolution notes: the seeded URL does not exist and the catalogue is at the community organisation; a second name in the seed string was checked by metadata only and is a translation plugin with no capture-lane relevance. Its version reality check found that two of the four classic seeded plugins are capped below the current Zotero line and dead for it, and it names the current-line-capable equivalents for each capability, two of whose bodies were not read here and were read later as part of the enrichment catalogue. Its three implications for the vault are that the merge behaviour is a re-key and orphan case for change detection, that enrichment lands in the Extra field in several competing line formats and one plugin may reorder that field, so a managed region should parse the field by key rather than by position, and that the deployed index carries version bounds usable for a mechanical compatibility check.

______________________________________________________________________

## The Zotero fact register

The Z lane's output has moved to `docs/research/2026-09-05-zotero-api-reading.md`, which carries all 448 deduplicated facts, Z1 through Z7, each with its verbatim quote and location, and the table of the bodies read with their pins. It moved because it is environment documentation rather than a sourcing finding: a register of API facts frozen on one day goes stale, and a third of this note spent on it buried the candidate findings the note exists to report. What stays here is the Z lane's place in the run, meaning the fact list in the requirement set above and the per-body rows in the coverage matrix. Neither file is where the design reads its facts from: the facts the ingest design depends on live in section 9 of `docs/superpowers/specs/2026-09-04-import-redesign-design.md` with their method and date, and are re-probed.

______________________________________________________________________

## Null report

Nine requirements were treated as floors. For each, the table gives the coverage measured across all 48 read records, counting one status per record and taking the later read where the same URL was read twice. The two AutoSci reads have different URLs, so they count as two records here, exactly as the coverage matrix lists them as two rows. That is why the D2 covers count is one rather than zero: the first AutoSci read is the covers row, and the second read of the same body, at a narrower URL, is a separate record scoring partial. The verified column counts covers rows that an adversarial verify pass re-checked by name and did not refute.

| Floor   | Covers | Verified covers | Partial | Does not | Undetermined | No row |
| ------- | ------ | --------------- | ------- | -------- | ------------ | ------ |
| **D1**  | 11     | 9               | 8       | 5        | 0            | 24     |
| **D2**  | 1      | **0**           | 7       | 17       | 0            | 23     |
| **D3**  | 8      | 5               | 12      | 2        | 0            | 26     |
| **D4**  | 16     | 13              | 6       | 1        | 0            | 25     |
| **D6**  | 15     | 12              | 7       | 4        | 0            | 22     |
| **D10** | 26     | 16              | 2       | 1        | 1            | 18     |
| **C1**  | 8      | 6               | 6       | 9        | 0            | 25     |
| **C2**  | 3      | 3               | 4       | 12       | 0            | 29     |
| **C6**  | 24     | 16              | 0       | 0        | 0            | 24     |

Two notes on how to read the verified column. It counts only rows a verify pass named. For the two licence floors that undercounts, because every one of the 61 verify passes re-fetched the licence file at the pin and confirmed it, so a licence finding was checked for all 42 records that carry a verify pass whether or not the pass listed D10 or C6 among its three rows. And a blank row is not a negative: under the run's own convention a candidate with no row for a requirement is undetermined for it, which is usually because the requirement is out of that candidate's lane.

**D2 is the only floor with no verified covers row.** The measurement, and how it got there, in order.

One candidate scored D2 `covers` in the whole run: skyllwt/AutoSci, on its first read, with basis evidence. No verify pass re-checked that row. The verify pass that ran on AutoSci re-checked D6 and D10, and its own note calls those two "the only covers among floor requirements", which is false in the record it was checking. So the run's single D2 cover went unverified under any reading of verified.

The critic pass ordered a re-read of the same body, narrowed to the runtime schema contract. That re-read scores D2 `partial`, and its own reasoning concedes two things: the ingest-time fill is model prose, and the shipped fields are bibliographic, meaning title, venue, year, a short summary and an importance marker, rather than charting fields. There is no population, design or page locator. So the run's only D2 cover is superseded by a second read of the same body, and the record that supersedes it is itself unverified, because it was read after the critic pass and no verifier reached it.

What is left, measured across all 48 records: one covers, superseded; seven partial; seventeen does not; and 23 records carrying no D2 row at all. The seven partials are SamurAIGPT/llm-wiki-agent, Pratiyush/llm-wiki, garrytan/gbrain, ussumant/llm-wiki-compiler, mgmeyers/obsidian-zotero-integration, windingwind/zotero-better-notes, and the AutoSci re-read. They divide into two shapes. In the two capture-lane partials the per-source template and its field list are fully caller-supplied, and the reason they are not covers is that every value available to the template is Zotero metadata: the template can lay out a charting skeleton but cannot fill it from the source document. In the digest-lane partials a field list exists but is fixed in code or in a shipped template, with the caller able to influence emphasis rather than fields.

The two candidates the critic added specifically to probe D2 both came back negative. The one whose templates directory was the run's best remaining chance scores does not, because the five sections are hard-coded in the skill file and restated inline so that editing the template would fight the instruction. The other scores does not because body structure is model-chosen at compile time, which is the opposite of a caller-supplied field list.

Stated plainly: after 48 reads across 43 searches, no candidate in this run has a verified covers row for D2, and the one covers row it produced is contradicted by a second read of the same body. That is a measurement of this run, not a claim about the world. Nothing here says a component covering D2 does not exist; it says this run did not find one, and that the field it swept was not saturated when the sweep stopped.

The other eight floors each have at least one verified covers row. The narrowest after D2 is the pairing the critic names in its third gap, which is not a single floor but a seam: no candidate covers C2 and C5 together. Every C2 cover in the run is a desktop application plugin scored C5 does not, and every C5 cover is C2 does not or partial. That is recorded here because it has the same practical shape as an uncovered floor, and because the run never read a headless, citekey-keyed, managed-region note writer.

______________________________________________________________________

## Gaps

A separate critic pass read the whole run against itself. Its three fields are reproduced verbatim below, in fenced blocks so that nothing is reflowed or re-punctuated. The critic ran before the four bodies that were added because of it were read, so where a gap names a candidate as unread, the section above for that candidate is the answer the run gave afterwards.

### The critic's gaps, verbatim

8 entries.

**Gap 1.**

```
FLOOR D2 rests on a single row the verifier never checked. AutoSci (runtime/schema/entities.yaml + runtime/loader.py L34-90 + tools/lint.py) is the run's only 'covers' for D2, and AutoSci's own verification.pin_note enumerates the re-checked rows as D6 and D10 and calls them 'the only covers among floor requirements' — which is false in its own record, so the D2 claim went unverified under any reading of 'verified'. The row also self-undercuts: its reasoning concedes 'the ingest-time fill is LLM prose' and that the shipped fields are bibliographic (title/venue/year/tldr/importance), not charting (no population, design, or page locator). Across the 23 records carrying a D2 row the tally is 1 covers / 9 partial / 13 does_not — D2 is the run's weakest floor by a wide margin, and the unread candidate closest to it (Astro-Han/karpathy-llm-wiki) also ships FIXED templates in references/, so D2 is probably author-and-credit territory rather than adoptable.
```

**Gap 2.**

```
No lane is unread — DIGEST (18 records), CAPTURE (17) and ZOTERO-FACT (9) all have reads. The defect is allocation, not absence: the 9 ZOTERO-FACT records re-quote the same six zotero.org pages plus BBT source, with the Z1 consent-dialog/Always-Allow/key-lifetime quotes duplicated across at least 5 records and the 14-method BBT JSON-RPC inventory across at least 4, while the two thinnest floors (D2, and the C2-with-C5 seam) received no additional reads at all.
```

**Gap 3.**

```
Structural hole no single record states, visible only across the set: no candidate covers C2 and C5 together. All three C2 'covers' (PKM-er/obsidian-zotlit, mgmeyers/obsidian-zotero-integration, masaki39/simple-citations) are Obsidian desktop plugins scored C5 does_not; every C5 'covers' (urschrei/pyzotero, 54yyyu/zotero-mcp, cookjohn/zotero-mcp, alex-roc/zotero-agent, Better BibTeX, 917Dhj/DeepPaperNote) is C2 does_not or partial. So the run never read a headless, citekey-keyed, managed-region note writer — precisely the seam the redesign needs. The closest unread candidates (PiaoyangGuohai1/cli-anything-zotero, xunhe730/ZotPilot) are C1+C5-shaped and their documented note command writes INTO Zotero ('zotero-cli note add KEY --text'), so neither is confirmed to emit a vault-side citekey-keyed note; the hole may be real rather than a search miss.
```

**Gap 4.**

```
Every one of Z1-Z7 carries at least one verbatim quote, so no Zotero fact is empty — but four sub-facts rest on source code, commit history or a single live probe rather than any documentation quote, and should be labelled as such in the register: (Z3) the full-text page separator — no Zotero page states it; evidence is zotero/pdf-worker `text.push('\f')` plus one probe showing 16 form feeds in a 17-page PDF; (Z4) the /file/view/url path form — docs say only 'a file:// URL', while the concrete `file:///D:/Zotero/storage/<KEY>/<name>` shape is one WSL-side probe; (Z5) saved-search execution — documented but never exercised, because the probe library contained 0 saved searches; (Z6) 'since which version' — the records state that neither the Zotero 8.0 nor the 9.0 changelog mentions citationKey, so the version is triangulated (zotero-schema commit 55a1312 -> schema v40 -> client tag 7.0.32) and is left in unresolved tension with BBT's own 'With the advent of Zotero 8' changelog line. Also unreconciled across two records: a live local GET /fulltext returned Last-Modified-Version 20694 for an attachment at item version 0 in a library at version 540, contradicting the Local API page's claim that these are local versions (Z2/Z3); both records log it as an observation and neither resolves it.
```

**Gap 5.**

```
The not_examined probe is vacuous: no record in the run carries not_examined:true. The equivalent misses are bodies named inside examined records and then skipped although reachable — AutoSci's `autosci-codex` branch (the sole basis for its separately-recorded Codex-compatibility claim; the record's own branch listing confirms the branch exists), claude-obsidian's 'Community early-access mirror (Pro)' at github.com/AI-Marketing-Hub, notero's auth/storage.ts and auth/crypto.ts (leaving the PRIVACY.md credential-storage claim unverified), and the three prior-art repos named in Pratiyush F1.
```

**Gap 6.**

```
Expected-but-absent, DIGEST: the run read 18 Karpathy-pattern implementations but skipped most of the same-or-higher-star cohort, including two that are exactly D6-shaped. Astro-Han/karpathy-llm-wiki (2,154 stars, MIT, pushed 2026-07-23) ships SKILL.md + references/{raw,article,index,archive}-template.md + scripts/check_evidence.py and enforces the D3 keep-both rule with a 'Status: Disputed'/'Outdated' block and 'Never silently rewrite history', script-verified by grepping high-signal literals back into the linked raw files — a stronger D3 than any row currently in the run, all of which are prose-only. sdyckjq-lab/llm-wiki-skill (2,424 stars, pushed 2026-07-27) ships SKILL.md + CLAUDE.md + AGENTS.md + templates/ but has NO LICENSE file, a D10 hole worth recording. Also unread: lucasastorian/llmwiki (1,573, Apache-2.0, pushed 2026-09-03) and xoai/sage-wiki (597, MIT, pushed 2026-08-29), both of which the run's own facts (Pratiyush F1) named as prior art and never followed; and kytmanov/obsidian-llm-wiki-local (818, MIT), which drops Markdown notes into an existing Obsidian vault and bears directly on D4/D7.
```

**Gap 7.**

```
Expected-but-absent, CAPTURE: the canonical Zotero-to-Markdown literature-note lineage is entirely missing, which is why C2 is evidenced only by three Obsidian desktop plugins. argenos/zotero-mdnotes (1,400 stars, GPL-3.0, archived 2024) is the original citekey-named Markdown exporter and the direct ancestor of every C2 candidate read; hans/obsidian-citation-plugin (1,338, MIT) is the most-installed caller-templated literature-note generator; stefanopagliari/bibnotes (364, NO licence — a C6 check in itself) has as its headline feature re-importing annotations into an existing note without clobbering user text, i.e. exactly the C2 managed/free split; and windingwind/zotero-actions-tags (2,808, AGPL-3.0, pushed 2026-08-24) is the canonical Zotero-side automation hook — the zotero-agent record names it as the automation route yet it was never read.
```

**Gap 8.**

```
Bookkeeping defect in the verification layer: the ZOTERO-FACT record 'Zotero Web API v3 - Write Requests (plus linked Local API, Basics, Full-Text Content, File Uploads, Syncing pages...)' reports verification.rows_checked=3 and rows_refuted=3 while its coverage array is empty — three refutations against zero rows. It is the only non-zero rows_refuted in the entire run, so the single 'something was refuted' signal the run produces is uninterpretable as written and should be re-stated (facts refuted? miscount?) before any coverage table is trusted.
```

### The critic's uncovered floors, verbatim

```
D2
```

### The critic's candidates to add, verbatim

15 entries. Four of them were read afterwards and have their own sections above: the AutoSci re-read, Astro-Han/karpathy-llm-wiki, sdyckjq-lab/llm-wiki-skill and PiaoyangGuohai1/cli-anything-zotero. The remaining eleven were not read, and are the run's own list of where to look next.

**Candidate 1.**

```
https://github.com/skyllwt/AutoSci/blob/e02cb3b766597c4fc345f653513c56d21b6f7ef5/runtime/schema/entities.yaml (with runtime/loader.py L34-90 and tools/lint.py) — CHEAPEST AND FIRST: one re-read settles answer (a). Either D2's only 'covers' row verifies, or it drops to partial and the run has zero D2 coverage. No new repo changes the answer as directly.
```

**Candidate 2.**

```
https://github.com/Astro-Han/karpathy-llm-wiki — 2,154 stars, MIT, SKILL.md + references/{raw,article,index,archive}-template.md + scripts/check_evidence.py. Read for D3 (Status: Disputed/Outdated blocks, 'Never silently rewrite history', script-verified evidence invariant — stronger than every D3 row in the run) and to confirm D2 does_not (templates look fixed, not caller-supplied).
```

**Candidate 3.**

```
https://github.com/sdyckjq-lab/llm-wiki-skill — 2,424 stars, SKILL.md + CLAUDE.md + AGENTS.md + templates/ + platforms/. Read for D2 (a templates/ directory is the run's best remaining shot at a caller-supplied field list) and record the D10 hole: no LICENSE file at HEAD.
```

**Candidate 4.**

```
https://github.com/PiaoyangGuohai1/cli-anything-zotero — 132 stars, Apache-2.0, Python, 70+ CLI commands for Zotero 7/8/9 incl. item annotations, search-annotations, note add, plus templates/ and skill_generator.py. Closest unread candidate to the C1+C5 half of the C2-with-C5 hole; confirm whether anything emits a vault-side citekey-keyed note or only writes into Zotero.
```

**Candidate 5.**

```
https://github.com/xunhe730/ZotPilot — 71 stars, MIT, MCP server + agent skill + a connector/ (Zotero-side) component. Second probe at the C1+C5 seam, and a Codex/Claude-skill packaging comparison for D6.
```

**Candidate 6.**

```
https://github.com/stefanopagliari/bibnotes — 364 stars, Obsidian plugin whose stated feature is updating an existing literature note with new annotations without overwriting user text: the closest prior art to C2's managed/free region. Note it has no LICENSE file, so C6 is a live question.
```

**Candidate 7.**

```
https://github.com/hans/obsidian-citation-plugin — 1,338 stars, MIT. The most-installed Zotero-to-Obsidian literature-note generator: citekey-keyed notes from a caller-supplied template over a BBT CSL-JSON/BibTeX export. Bears on C2 and on D2's 'caller-supplied field list' question from the Obsidian side.
```

**Candidate 8.**

```
https://github.com/argenos/zotero-mdnotes — 1,400 stars, GPL-3.0, ARCHIVED (last push 2024-10-18). The origin of citekey-named Markdown export with configurable templates; read and record as dead-but-formative (as the run already does for eschnett/zotero-citationcounts), since its file/field conventions are what the C2 candidates inherit.
```

**Candidate 9.**

```
https://github.com/windingwind/zotero-actions-tags — 2,808 stars, AGPL-3.0, pushed 2026-08-24. The canonical Zotero-side automation/trigger plugin, named by the zotero-agent record as its automation route but never read; relevant to C7 and to any Zotero-side write-back or on-add hook.
```

**Candidate 10.**

```
https://github.com/lucasastorian/llmwiki — 1,573 stars, Apache-2.0, pushed 2026-09-03, has api/ converter/ mcp/ extension/. Named as prior art in the run's own facts (Pratiyush F1) and never followed; screen for D1/D6 and for its MCP surface.
```

**Candidate 11.**

```
https://github.com/xoai/sage-wiki — 597 stars, MIT, pushed 2026-08-29. Second unfollowed lead from Pratiyush F1.
```

**Candidate 12.**

```
https://github.com/kytmanov/obsidian-llm-wiki-local — 818 stars, MIT, Python + CLAUDE.md. 'Karpathy's LLM Wiki, 100% local with Ollama. Drop Markdown notes -> AI extracts...' — directly probes D4 (consume a note another process wrote) and D7 (existing Obsidian vault, caller-chosen layout) with no cloud call.
```

**Candidate 13.**

```
https://github.com/skyllwt/AutoSci/tree/autosci-codex — the unread branch that is the sole basis for AutoSci's separately-recorded Codex-compatibility claim (main's setup.sh has no .agents/skills sync). Confirms or refutes that claim without re-reading the whole repo.
```

**Candidate 14.**

```
https://github.com/papis/papis and https://github.com/papis/papis-zotero — 1,774 + 86 stars, GPL-3.0, both live (2026-09). Headless CLI bibliography manager with a Zotero importer and per-document metadata files: a different shape from every capture candidate read, and the only realistic non-plugin route to C5 + a caller-templated per-source record.
```

**Candidate 15.**

```
https://www.zotero.org/support/note_templates — the Zotero-side note-template documentation. Cited only second-hand in the run (notero's colour table quotes it), yet it is the primary source for the HTML/structure conventions any managed region written INTO a Zotero note must respect (C2's in-Zotero counterpart).
```
