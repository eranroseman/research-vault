# Ingest redesign: design

Status: draft for author review (2026-09-04). Nothing here is decided. Each statement is one of: **chosen** (the author picked it in the 2026-09-04 brainstorm, and it can be re-picked), **measured** (probed live on the date given), **proposed** (the design's suggestion), or **open** (not yet answered). Supersedes foundation spec §4 (Zotero bridge) and the suspended ADR 0004 and 0005 when accepted.

Consumers: the implementation plan for this iteration; the later specs for search (PRISMA-S), scoping review (PRISMA-ScR), and the workflow-component audit.

## 0. Purpose and boundary

Ingest is the process that gets a source from outside the vault into the vault. It is the first of three garbage-in gates (setup, lint, ingest). This spec covers the whole ingest path and the setup and lint machinery ingest depends on. It follows one priority order throughout: adopt an existing component as-is, else adapt one, else build. Capture and its linter are mechanical and built here; the compile step is adopted.

Chosen scope (2026-09-04):

- Source classes: scholarly and grey-literature documents, meaning anything Zotero can hold as an item with a file or DOI (papers, preprints, standards, reports, books, theses). Web pages, repositories, and product documentation are deferred.
- Post-capture events covered: identity changes, removal, and content drift. Substrate absence (Zotero not running, a clone with no Zotero, CI with no Zotero) is deferred, so a live Zotero at every mechanical check is assumed.
- Trigger: capture on demand; a drift check at every mechanical chokepoint. Nothing writes the vault unattended.
- Greenfield: no existing vault content must survive.
- Derived full text lives in the vault as a gitignored cache, regenerable from Zotero.
- Screening decisions belong to a review, not to the source. The hand-edited note status is retired.

Terms in this document are the industry terms proposed in §1.1, each taken from a primary source recorded in `docs/research/2026-09-04-import-terminology.md`: **ingest** (the whole process), **selection** (the human decision), **add** (creating the Zotero item), **capture** (the deterministic copy into the vault), **compile** (the LLM step), **drift** and **refresh** (change detection and re-copy), **item key** and **citation key** (identity and name). The brainstorm's working labels were import, admission, capture, and digest; §1.1 records why each stays or goes.

## 1. Source lifecycle

The design object is the source's relationship with the vault over time, not the files. States, the event that moves a source between them, and the owner of each move:

| State | Meaning | Entered by | Owner |
| --- | --- | --- | --- |
| identified, screened, selected | The review found the source, screened it, and chose it for retrieval. Lives in the review's selection log. | Search and screening | The scoping review workflow, specified separately |
| added | A Zotero item exists. Zotero assigned its item key; Better BibTeX assigned its citation key. | A person adds the item, or the agent adds it on the person's instruction (§3) | Person, with the agent as operator |
| captured | The literature note exists with a metadata snapshot and a provenance tuple. Identity is fixed here, once. | The capture verb (§2) | Capture verb |
| compiled | The source page and concept-page updates exist; the compile input hash is recorded. | The adopted wiki (§4) | Adopted wiki |
| current | Live item version equals the recorded version. | The linter finds no change | Linter |
| drifted | Live version is newer: metadata, attachment, or annotation changed in Zotero. | Linter | Linter files a finding; the capture verb refreshes on demand |
| re-keyed | Live citation key differs from the recorded one. | Linter | Linter records the old-to-new mapping; propagation rewrites every citation-key surface |
| merged | The item key is gone and another item's `dc:replaces` names it. | Linter | Linter records the successor; the note points forward |
| trashed | The item key is in Zotero's trash. | Linter | Note kept; finding filed |
| deleted | The item key is absent from the library and the trash. | Linter | Note kept, state recorded; finding filed |
| retracted or corrected | A registry notice names the source. | Existing update-notice check | Standing recorded on the note |
| database changed | The Zotero server id differs from the recorded one; Zotero's documentation: a different id means a different database. | Linter | Linter stops and reports; every recorded version is void |

Invariants:

1. Identity is assigned exactly once, at capture, and never reused.
2. Every provenance tuple carries the Zotero server id. Versions and keys are meaningful only within one server id.
3. No transition deletes a note. Records deprecate; they do not vanish.
4. Every transition is visible: a finding in the review queue or a line in the log.
5. The linter runs at capture, at verify, and at pre-commit, through one code path.
6. A mechanical step without a named linter is incomplete.

Cost, measured 2026-09-04: `GET /api/users/0/items?since=0&format=versions` returns all 2,846 object versions in one response; `GET /api/users/0/items/trash?format=versions` returns the 267 trashed keys in one response. A whole-vault check is those two calls plus one fetch per changed item.

### 1.1 Glossary (proposed)

The glossary in `CONTEXT.md` is rewritten around eight concepts. Each proposed term is the word a field already uses, with the primary source it was read from; the evidence and the competing terms are in `docs/research/2026-09-04-import-terminology.md`. Where two fields use one word for different things, the collision is named so the glossary can say which sense applies.

| Concept | Proposed term | Field and primary source | Working label, and why it goes |
| --- | --- | --- | --- |
| The whole process from outside the vault into the vault | **ingest** | LLM wiki (Karpathy's gist: "Ingest. You drop a new source into the raw collection and tell the LLM to process it"); digital preservation (OAIS Ingest functional entity) | import: Zotero uses it for bringing a bibliographic file into Zotero, which is a step inside ingest, and the connector endpoint is named `/connector/import` |
| The human decision that a source is accepted | **selection**, with the outcomes **included** and **excluded** | Evidence synthesis (JBI: "selection (also known as screening) of evidence sources"; PRISMA-ScR item 9; PRISMA 2020 item 16b) | admission: found only in the llmwikis handbook, for agent-memory records; no review guideline uses it |
| Creating the library record in Zotero | **add** (to Zotero); **import** when Zotero parses a bibliographic file | Reference managers (Zotero: "Adding Items to Zotero"; the connector: "Clicking the save button will create an item in Zotero") | admission (the act): same as above; archival "accession" is the field term but no Zotero user says it |
| The deterministic copy of metadata, attachments, annotations, and text into the vault, with provenance | **capture** | LLM wiki (hermes llm-wiki: "Capture the raw source"); preservation metadata (PREMIS event type "capture") | keeps its label; collision: change data capture in data engineering means capturing changes, which is drift here |
| The LLM step that turns a captured source into wiki pages | **compile**, producing a **source page** and updated **concept pages** | LLM wiki (nvk/llm-wiki: "Transform raw sources into wiki articles"; llmwikis handbook: "the agent turns it into a source summary, updated concept pages") | digest: nvk uses it for a memory record, no other field for this step |
| Detecting that the Zotero item changed, vanished, or was re-keyed, and re-copying | **drift** (the detection) and **refresh** (the re-copy) | LLM wiki (hermes: "flag drift when it has changed"; nvk: "refresh: Freshness check ... re-fetches ... detects changes"); Zotero's own mechanism words stay verbatim: version, `Last-Modified-Version`, `?since=` | sync: Zotero's sync is client to zotero.org; using it here would name the wrong thing |
| The stable identifier across a source's life, and its name | **item key** (identity) and **citation key** (name) | Reference managers (Zotero API: `<itemKey>`; Zotero schema field "Citation Key"; Better BibTeX: "the citation key is the piece of data that connects your bibliography") | citekey: a spelling no product uses; the field is `citationKey` |
| A source's standing after it was added | **trashed**, **deleted**, **merged** (Zotero's words); **retracted**, **corrected** (Retraction Watch, Cochrane); **superseded** (nvk status; EndNote keeps the record) | Reference managers and evidence synthesis | screening state on the note: excluded and included belong to the review's selection, not to the source |

Kept as they are, with their field: **item** (Zotero's record), **record** (PRISMA 2020: a title or abstract indexed in a database), **source of evidence** (PRISMA-ScR), **literature note** (Obsidian community: ZotLit, Obsidian Zotero Integration), **fixity** (OAIS, PREMIS).

Entries retired: Admission, Import as currently defined, Screening state, Bibliography export, Citable as defined through the note status, and the citekey spelling.

## 2. Capture

### 2.1 Identity and name (chosen: bundle 1)

The vault's identity for a source is the Zotero item key qualified by the Zotero server id. Item keys are assigned by Zotero, are not user-editable, are unique within a library, and survive metadata edits and citation-key changes. The citation key is the source's name: it names the file and appears in prose citations and the CSL file. A citation-key change is a rename of a thing whose identity did not change, so propagation is mechanical.

This answers the two objections to ADR 0004: a third party cannot change the identity, and uniqueness is Zotero's guarantee within one server id. A freed suffix (`chen2025a` reused for a different source) is detected because the item key differs from the one recorded under that name.

Filename (chosen): `literatures/<citation key>.md`. The title is carried in frontmatter and as the H1, and in `aliases`, so Obsidian resolves `[[Title]]` as well as `[[citation key]]`. The file renames only on a re-key.

### 2.2 Record home (chosen: both, one writer)

Two files carry bibliographic data, and the capture verb is the sole writer of both.

**The literature note's frontmatter** carries:

- a metadata snapshot: a fixed subset of the Zotero item's data fields, copied verbatim under Zotero's own field names (`itemType`, `title`, `creators`, `date`, `DOI`, `url`, `publicationTitle`, `volume`, `issue`, `pages`, `publisher`, `ISBN`, `language`, `abstractNote`), so no field is renamed and no mapping is ours;
- a provenance tuple: `zotero-server-id`, `zotero-item-key`, `zotero-item-version`, `citationKey`, `attachments` (a list of `{key, md5, contentType, filename}`), `fulltext` (`{version, sha256}` of the cached text), `annotations-version`, and `generated: {by, at}` (OKF §5.2 shape, already adopted);
- `title` and `aliases` for Obsidian; `type: literature` for OKF.

Frontmatter is machine-owned above the managed region marker; the free region below the managed close marker is never touched by capture. The current `%%rv-managed%%` markers stay.

**The CSL JSON file** (`system/bibliography.json` today; name follows the glossary) holds one entry per captured item, rendered by Better BibTeX's `item.export` with the Better CSL JSON translator, sorted by citation key. It exists for pandoc. Its scope is the captured set, not the library. It is regenerated whole by the capture verb; no auto-export, no observation, no byte-compare against a third-party writer.

The capture verb writes both from the same Zotero read, so they cannot disagree with each other. The linter diffs both against live Zotero.

### 2.3 The capture verb

One verb, per item or batch, keyed by citation key or item key. For each item it:

1. reads the item JSON from the local API (`/api/users/0/items/<key>?format=json`);
2. reads the children (`/items/<key>/children`): attachments with `md5`, `mtime`, `contentType`, `filename`, and the file URL from `/items/<attachment>/file/view/url`; notes; annotations, which are items with `parentItem` set to the attachment;
3. reads the attachment's indexed full text (`/items/<attachment>/fulltext`) into the gitignored cache, recording `indexedPages` and `totalPages`; a 404 means not indexed, and the cache entry says so rather than holding partial text;
4. asks Better BibTeX for the item's CSL entry (`item.export([citation key], "Better CSL JSON")`). This one call is keyed by the name rather than the identity, because that is the only key the method takes; the citation key used is the one just read from the item JSON in step 1, so it cannot be a stale one;
5. renders the note: frontmatter, managed region (title, creators, venue, identifiers, attachments, annotations as a list with page labels and verbatim highlight text), and the preserved free region;
6. writes the CSL file entry and the cache;
7. compares the rendered projection with what is on disk and reports NOOP when nothing changed.

Every mechanical outcome is four-state. UNREACHABLE (Zotero not answering) writes nothing and files an outage finding. A malformed response writes nothing.

### 2.4 The lifecycle linter

One check, one code path, run at capture (before rendering), at verify, and at pre-commit. It:

1. reads every literature note's provenance tuple;
2. reads the server id from `GET /api/` and stops with a database-changed report if it differs from the recorded one;
3. fetches the whole key set with `?since=0&format=versions` and the trashed set with `items/trash?format=versions`. The full set is required, not `?since=<lowest recorded version>`: a `since` window returns only items that changed, so a key that vanished appears in neither the window nor the trash and would read as current. One response carried 2,846 versions on 2026-09-04, so the full set costs nothing;
4. classifies every note: current, drifted, re-keyed (live `citationKey` differs), merged (key absent and some changed item's `dc:replaces` names it), trashed, deleted;
5. on drifted items, compares attachment `md5` values and the fulltext version to the recorded ones, so an attachment swap or new annotations are named, not just "changed";
6. files one finding per non-current note with the transition's reason code, and blocks nothing except database-changed.

This costs a running Zotero at every commit, which follows from the scope in §0: substrate absence is deferred. Until it is taken up, a commit made with Zotero closed reports the linter UNREACHABLE, and the pre-commit hook treats an outage as it treats any other: it files the finding and does not block. The plan states that behaviour as a test, so an outage never silently reads as a clean classification.

Reason codes, proposed: `drift`, `re-keyed`, `merged`, `trashed`, `deleted`, `database-changed`, `outage`. `drift` already exists in the registry. `superseded-note` and `not-admitted` are retired with the note status.

### 2.5 Re-key propagation

A re-key is detected by the linter or reported by Better BibTeX's `item.regenerate_key`, which returns an old-to-new mapping. Propagation is one mechanical pass driven by the recorded mapping: rename the file, rewrite the CSL entry id, rewrite `[@old]` citations, rewrite `[[old]]` wikilinks, rewrite the frontmatter `citationKey`. The mapping is appended to a rename log so a later reader can follow any key backwards. The identity never changes, which is what makes the pass safe to repeat.

### 2.6 Paths and the text cache

No absolute paths in the repository. The file URL from Zotero is a Windows `file://` path; the existing `wslpath` shim resolves it at use time. The text cache lives beside the notes under a gitignored folder, one file per attachment, named by attachment key, with its sha256 recorded in the note. The cache is regenerable from Zotero and never committed.

### 2.7 API use (measured 2026-09-04)

- Zotero 10.0.1 local API, version 3, serves item JSON with `key`, `version`, `citationKey`, `dateModified`, `relations`; children with `md5` and `mtime`; `/file/view/url`; per-attachment `fulltext`; `fulltext?since=`; `?since=&format=versions`; `items/trash`; a `Zotero-Server-ID` header on every response. It has no `/deleted` endpoint.
- Every translator-based format on the local API (`format=csljson`, `format=bibtex`, `include=csljson`) returns HTTP 500 on 10.0.1. Better BibTeX 9.0.63 `item.export` is the working CSL renderer.
- Better BibTeX JSON-RPC is used for exactly two things: CSL rendering and re-key mappings. Its auto-export is not used.
- The Zotero web API is not used. The bib-file export is not used.

## 3. Selection and adding to Zotero

Selection is the human act, recorded where it is made: the review's selection log, or an ad hoc request. The keystrokes that add the item are not the decision, so the agent may perform them.

Record creation by the agent uses Zotero's own translators through the connector server (measured 2026-09-04, read from `server_connector.js` at zotero/zotero main):

- `POST /connector/import?session=<id>` with an RIS, BibTeX, or CSL JSON body runs Zotero's import translator, saves the items into the currently selected library or collection, and returns HTTP 201 with the created items as JSON, including their keys.
- `POST /connector/saveAttachment` in the same session attaches a file to the saved item.
- For a DOI, the body comes from content negotiation on doi.org (`Accept: application/x-research-info-systems` or `application/x-bibtex`). For an identifier-less document, the agent composes a minimal RIS from the metadata it holds. In both cases Zotero parses the record; the vault never builds Zotero item JSON.
- No consent dialog guards these endpoints; the browser connector uses them. One batch is one session.

Capture runs on the returned keys at once, so adding and capture are one conversation.

Record creation by the person (browser connector, drag-in, add by identifier) stays valid and reaches capture the same way.

No citation-key pinning. Under item-key identity a later key change is a rename, not a lost address.

Open, to be settled in the plan with one attended write test on a scratch collection: the connector save target is whatever is selected in the Zotero window. The verb either moves the saved items to the intended collection through the local API afterwards, or refuses when the target reported by `/connector/getSelectedCollection` is not the expected one.

## 4. Compile

Chosen outputs (2026-09-04): a source page and cross-source concept pages, both in the adopted wiki's own shape. Claims with locators are dropped as a vault syntax; the requirement that a quoted passage be traceable to a page and byte-checkable on demand is carried by Zotero annotations captured at ingest. Charting belongs to the scoping review and is not a compile output, so the earlier requirement D2 (a caller-supplied per-source template) leaves this set and moves to the scoping review spec.

### 4.1 Requirement set the adoption was screened against

Floors: D1 a per-source page; D3 concept pages with an index, an append-only log, and contradictions kept rather than resolved; D4 the capture of the source file is separable from compiling it, so the tool accepts a raw file another process wrote; D6 installable as a Claude Code plugin or skill as-is; D10 a licence that permits use and modification. Not floors: D5 idempotent re-compile; D7 works on an existing layout or states its own; D8 references a source by a caller-supplied stable id; D9 documents its human gate.

The evidence is in `docs/research/2026-09-04-import-sourcing.md`: 43 candidates read after a triage of 295 discoveries, with every drop counted by reason. The candidate descriptions below are drawn from that note's records. Where its adversarial verify pass had not confirmed a row when this section was written, the note marks it, not this document.

### 4.2 Candidates that meet every floor as-is

Two Claude Code plugins meet D1, D3, D4, D6, and D10 without modification. Both are MIT, both were pushed in the last ten days of August 2026, both are Python underneath.

**AgriciDaniel/claude-obsidian** (v2.1.1, pin `ad67087`, 14,631 stars, 42 commits in 90 days). Integration is a transaction: read-only workers propose a bundle of page writes with expected content hashes, the person approves the plan by its hash, and an engine applies it atomically or not at all. Source pages carry key claims; a claims ledger marks contested claims and refuses contradictory evidence without an adjudication note. Sources enter through a configured inbox directory, and paths outside the vault are refused. Layout: a `wiki/` directory beside an `.obsidian/` directory. The ledger key is a content hash, so the citation key rides in the source locator and the page properties, not in the ledger id. Components at the pin: 15 skills, 3 agents, a SessionStart and a Stop hook, and the `claude_obsidian/` Python engine the skills call. `plugin.json` declares no components, so component discovery is by directory.

**nvk/llm-wiki** (v0.24.4, pin `7c94c9b`, 1,034 stars). Ingest and compile are separate commands: ingest writes an immutable raw page with a fixed six-key frontmatter, compile turns uncompiled raw pages into concept, topic, and reference pages, with a nudge at five uncompiled sources. A raw page written by another process is accepted if it carries those keys, which is the capture-then-compile split of §1 exactly. Layout: `raw/<type>/` and `wiki/`, imposed by a lint that relocates files by their frontmatter. Components: 1 skill (403 lines plus 22 reference files), 27 commands, no hooks.

Candidates that fell on a floor, for the record: ussumant/llm-wiki-compiler (Claude and Codex plugin, no per-source page); kfchou/wiki-skills (contradictions must be resolved before commit, the opposite of D3); pumblus/okf-harness (OKF-native, Apache-2.0, no append-only log by design); the hermes-agent llm-wiki skill (a Hermes skill, not a Claude Code one; its schema template is the strongest pattern donor); atomicstrata/llm-wiki-compiler and SwarmVault (Node CLIs, not plugins); llmwikis.org (prompts and a starter bundle, scripts without a licence).

### 4.3 Proposed adoption: a curated subset of claude-obsidian

Proposed: adopt claude-obsidian through a **curated marketplace entry**, taking a subset of its components as-is and changing none of them. This follows the precedent set for obra/superpowers in the `agent-plugins` repository: a marketplace entry with a git source pinned by sha, `strict: false`, and an explicit component list, which installs upstream's own files while leaving out what this vault does not want.

Taken as-is: the skills `wiki`, `wiki-ingest`, `wiki-lint`, and `wiki-fold`; the agents `wiki-ingest`, `wiki-lint`, and `verifier`; and the `claude_obsidian/` engine the skills invoke.

Left out: `wiki-retrieve` and `autoresearch` (a chunker, a BM25 index, and a network research loop this vault does not ask for), `wiki-mode` and `wiki-query` and `save` and `think` (methodology and capture surface this vault owns elsewhere), and `canvas`, `obsidian-bases`, `obsidian-markdown`, and `defuddle`, which duplicate the kepano/obsidian-skills plugin already installed. The two hooks are left out with them.

Nothing is edited. The two things that must fit this vault are configuration, not code: `.claude-obsidian.json` sets the source inbox directory and the vault root. If the trial finds a change is needed after all, the fallback is to vendor that single skill into this plugin with a provenance header and a byte-check in CI, the treatment the `brainstorming` skill already receives in the `agent-plugins` repository. The second fallback, if the transaction ceremony proves too heavy for daily single-source use, is the same curated-subset treatment of nvk/llm-wiki: the commands `ingest`, `compile`, `lint`, `refresh`, `retract`, and `wiki`, plus `wiki-manager`.

Two mechanism facts are unverified and are the plan's first tracer, before any compile task is written:

1. Whether a `strict: false` curated entry that lists components suppresses upstream's auto-discovered `hooks/hooks.json`. The superpowers precedent proves component curation works, but that upstream ships no hooks file, so hook omission is untested. If hooks arrive anyway, they are silent by default (SessionStart context injection is opt-in through an environment variable) and the fallback is to accept them or to vendor.
2. That `wiki-lint` leaves `literatures/` untouched and that a source page can be reached from a citation key.

### 4.4 The seam between capture and compile

- Capture is the only writer of the literature note and the text cache. It also drops the compile input where the tool expects it: a markdown file in the configured inbox directory whose locator is the literature note path `literatures/<citation key>.md`.
- The compile input is the attachment text from the cache with the metadata snapshot as its header. Where no text is indexed, capture writes no compile input and files a finding. Nothing is compiled from an abstract alone. This also answers the tool's own limit, which reads PDFs as metadata only: it never sees a PDF, only text this vault extracted.
- The tool's `.raw/captured/` store holds a second, content-addressed copy of that text. It is gitignored with the cache unless the plan finds the lint requires it committed.
- The tool's `wiki/` directory replaces `synthesis/`. The vault's OKF bundle root and the tool's `wiki/index.md` are reconciled in the plan; both claim an `index.md`.
- Compile runs when the person asks, after capture, for one source or a batch. The tool's own gate is the human gate: inspect, approve by plan hash, apply. No second gate is added.
- The lifecycle linter records the compile input hash in the note. A refreshed note whose input hash changed is reported as needing recompile, which the tool then performs.

## 5. Setup and lint integrity

Doctor is setup's linter. It probes Zotero version, Better BibTeX version, local API reachability, server id, connector ping, translator-format health, fulltext index presence, and the path shim, and writes a machine-local, gitignored facts file in the vault. Runtime reads that file; the server id in it is what the provenance tuple carries.

The plugin repository's `docs/environment.md` stays a developer document. A live-lane test compares its version rows against doctor's output, so a stale row (the table said Zotero 9.0.6 on 2026-09-04 while 10.0.1 was running) fails the suite.

Retired from setup: the whole-library auto-export step and its staleness probe. Kept: the human-only wizard steps for Zotero plugin installs.

Every mechanical step in this spec names its linter: setup has doctor; capture, the CSL file, and the text cache have the lifecycle linter through recorded hashes and versions; adding has capture, which runs immediately on the returned keys and reports what it could not read.

## 6. What changes in the existing machinery

Retired by this spec:

- the Better BibTeX auto-export contract: observation, byte-compare, the `staleness` verb, the `autoexport` doctor probe, and the `bibliography.py` machinery around them;
- the note-level screening status, `lint_screening_state`, and the `superseded-note` reason code;
- claim lines as an ingest output, and anchors derived from annotations.

Superseded: ADR 0004 by a new record, "identity is the Zotero item key; the citation key is the name"; ADR 0005 by a new record, "capture is the sole writer of the vault's bibliographic record"; foundation spec §4 by this document. ADR 0001's scope bound gains the text cache. `CONTEXT.md`'s glossary is rewritten per §1.1.

Kept: four-state results; findings and the review queue; deprecate-never-delete for vault records; the managed region above a free region; the path shim; `find-sources` until the search spec; verify's DOI, metadata, and update-notice checks, rebased onto the frontmatter snapshot.

Frozen, dispositioned in the workflow-component audit: the quote check, the evidence-layer check, factcheck, stance links, the publish gate, project-flow, and archive-source. Ingest neither produces nor depends on them.

Rewritten skills: import-source and setup-vault. Others untouched until their own spec.

## 7. Testing

- Offline suite on recorded fixtures: a fixture-recorder verb captures local-API responses (item JSON, children, versions, trash, fulltext) from a live Zotero into redacted JSON files, so every lifecycle transition has a replayable fixture: drifted, re-keyed, merged via `dc:replaces`, trashed, deleted, database changed.
- Live legs against Zotero 10 on a scratch collection: capture round-trip, linter classification after a live edit, one connector import of an RIS string. The first write leg runs once with the author present.
- The doc-versus-doctor live test for the repository environment table.
- Gates unchanged: coverage, mutation baseline, form owners.

## 8. Open points

1. Connector save target (§3).
2. Preprint-to-published supersession: a Zotero relation, a vault fact, or out of scope for this iteration.
3. Whether the OCR path (scanned PDFs with no text layer) is in this iteration; the fulltext endpoint reports them as not indexed.
4. Verb and file names, after the glossary is fixed, including the CSL file's own name.
5. The `index.md` collision: the vault's OKF bundle root reserves it, and the adopted tool writes its own under `wiki/`. Whether one file serves both, or the bundle root moves, is settled in the plan against the tool's actual behaviour.
6. The exact shape of the compile input file: which metadata fields head it, and how the literature note path is carried so the tool's source page can be traced back to the citation key.

## 9. Measured facts (2026-09-04, this machine)

| Fact | Value |
| --- | --- |
| Zotero | 10.0.1 on Windows, local API enabled, reachable from WSL2 |
| Better BibTeX | 9.0.63; JSON-RPC `api.ready` answers |
| `Zotero-Server-ID` | present on every local API response |
| `?since=0&format=versions` | 2,846 versions in one response, `Last-Modified-Version: 540` |
| `items/trash?format=versions` | 267 keys |
| `/deleted` | 404, no endpoint |
| `citationKey` in item JSON | populated on 297 of 300 top items; the 3 without were standalone attachments |
| `relations.dc:replaces` | on 126 of 300 top items (merge history) |
| attachment child JSON | carries `md5`, `mtime`, `contentType`, `filename` |
| `/items/<attachment>/file/view/url` | returns a `file:///D:/Zotero/storage/...` URL |
| `/items/<attachment>/fulltext` | 404 for an unindexed PDF; `fulltext?since=0` lists 1,350 attachments with text |
| annotations | 1 highlight item in the library, with `parentItem`, `annotationPageLabel`, `annotationText` |
| `format=csljson`, `format=bibtex` | HTTP 500 on every item and on `/items/top` |
| BBT `item.export` Better CSL JSON | works; entry carries `citation-key` |
| connector endpoints | `/connector/import`, `/connector/saveAttachment`, `/connector/saveStandaloneAttachment`, `/connector/getSelectedCollection`, `/connector/ping` (200) |
| `POST /api/users/0/items` malformed | 400; does not discriminate write support |

## 10. Deferred

Substrate absence; web pages, repositories, product documentation; the claims layer and pinpoint citations (long-form spec); charting (scoping review spec); search (PRISMA-S spec); the workflow-component audit. The `import-source` and `find-sources` skill names are current names and are renamed with the glossary.
