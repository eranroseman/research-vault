# research-vault

Trust-first academic research on a personal knowledge vault: every claim traceable to a real source, verified by mechanical checks.

## Language

### Vault

**Vault**: A private git repository of markdown notes — the researcher's durable knowledge store, built to outlive its tools (ADR 0001) as an OKF bundle.

**Type (OKF)**: A note's kind, derived from its folder — `literatures/` → literature, `log/` → daily, `inbox/` → fleeting, and only `projects/<name>/draft.md` → project. `wiki/` derives none: the compile tool writes its own `type` values (source, concept, entity, meta). `fulltext/` notes carry `type: fulltext` by construction. Notes under `system/` and at the vault root carry any non-empty type, freely chosen.

**Evidence layer**: The vault's machine-projected record of captured sources (`literatures/`); never free-written.

**Text layer**: The extracted full text of every indexed attachment, one file per attachment at `fulltext/<attachment key>.md`, gitignored and regenerable from Zotero. Obsidian indexes it; git never carries it. Its sha256 is machine-local: two machines indexing one PDF do not produce identical text.

**Compiled layer**: The adopted compile tool's pages under `wiki/`: one per-source page under `wiki/sources/` and cross-source pages under `wiki/concepts/`. Nothing under `wiki/` passes an evidence gate; it asserts arrangement, not evidence, and is written only by the tool's transaction engine.
_Avoid_: synthesis layer, synthesis note (the layer moved under `wiki/` and took the tool's page names)

**Literature note**: The vault's record of one captured source, `literatures/<citation key>.md`, wholly machine-written by capture: a metadata snapshot, a provenance tuple, and a body carrying only what frontmatter cannot — the attachment list and the item's Zotero child notes. Per-source prose belongs in a Zotero child note, which capture renders.

**Project**: A manuscript or deliverable in progress (`projects/<name>/`), with a publication lifecycle.

**Inbox**: Fleeting captures and the review queue (`inbox/`); never an admission path for citable sources.

**Log**: The append-only per-day activity record (`log/`), summarized in root `log.md`.

**System folder**: The vault's support artifacts (`system/`): templates, bases, the CSL file (`system/bibliography.json`) and the applied propagation plans (`system/propagations/`).

**Propagation plan**: The computed description of one re-key pass — the old→new mapping, the item key behind it, the note rename, every surface to rewrite with its hash as it stands — printed for a person to approve and applied only against its own sha256. The applied plan, kept under `system/propagations/` and never rewritten, is the record a reader follows an old key forward through and the residue check reads. There is no separate rename log.

### Ingest

**Ingest**: The whole process that gets a source from outside the vault into the vault: selection, add, capture, compile. The last of three garbage-in gates (setup, lint, ingest).

**Selection**: The human decision that a source is accepted, with the outcomes **included** and **excluded**, recorded where it is made — the review's selection log or an ad hoc request. Never on the source.

**Add**: Creating the library record in Zotero, by a person or by the agent on the person's instruction over the local API's documented write path. **Import** is reserved for Zotero parsing a bibliographic file (RIS, BibTeX, CSL JSON) into items; it never names the vault's own projection.

**Capture**: The deterministic copy of an item's metadata, attachments, child notes and extracted text into the vault, with provenance. The sole writer of the literature note, the text layer and the CSL file. Runs on demand; re-running it is a **refresh**.

**Compile**: The LLM step that turns a captured source into wiki pages — a **source page** and updated **concept pages** — performed by the adopted compile tool under its own human gate. The compile input is the text-layer file capture wrote.

**Drift**: The lifecycle linter's finding that an object the note depends on carries a version other than the recorded one — the item, an attachment or an annotation, each versioned independently. **Refresh** is the re-copy capture performs on demand.

**Item key**: A source's identity: the Zotero item key qualified by the Zotero server id. Assigned once, never reused, never user-editable.

**Citation key**: A source's name: Zotero's native `citationKey` field, filled by Better BibTeX. It names the file, the prose citation and the CSL entry. A change is a rename of a thing whose identity did not change, propagated mechanically.
_Avoid_: citekey (a Better BibTeX synonym for a field Better BibTeX no longer owns)

**Standing**: A source's state after it was added, in the lifecycle linter's words: current, drifted, re-keyed, **merged**, **trashed**, **deleted** (Zotero's words); **retracted**, **corrected** (Retraction Watch, Cochrane). A transition never deletes a note; it files a finding.

**Captured set**: The citation keys read from the `citationKey` field of every parseable note under `literatures/` that also carries `zotero-item-key`. Not the filenames: a note whose filename disagrees with its recorded key is a re-key awaiting propagation. The CSL file's scope, the compile wrapper's selection and the captured-set lint all read this set.

**Provenance tuple**: The frontmatter fields that record what a literature note depends on: `zotero-server-id`, `zotero-item-key`, `zotero-item-version`, `citationKey`, `attachments` (key, version, md5, content type, filename), `fulltext` (attachment key, sha256), `compile-input-sha256`, `generated`. Versions and keys are meaningful only within one server id.

**Snapshot**: The fixed subset of the Zotero item's data fields a literature note carries verbatim under Zotero's own field names, `tags` and `extra` included. A value with line breaks is carried as a list of its lines.

### Evidence and claims

**Source**: The document itself, existing in the world before and independent of any library record — never the journal, repository, or outlet.
_Avoid_: "source" for an outlet — that is a **venue**, which is what OpenAlex's "source" means and ours never does

**Item**: A source's library record (CSL/Zotero vocabulary) — the object that carries the item key and the citation key.

**Venue**: The journal, repository, or outlet an item appeared in.

**Citable**: What a page or draft is allowed to cite: a source in the captured set. Being in the library is not yet being citable here; the captured-set lint enforces it on the commit surface.

**Claim**: One assertion carried by a note line, tagged with its evidence boundary and anchored for linking. Capture no longer writes claim lines; the checks that read them are frozen pending the workflow-component audit.

**Evidence-boundary tag**: The per-claim marker of epistemic status — quote, paraphrase, inference, or open-question.

**Claim link**: The global address of a claim: `citation-key#^claim-id` (an Obsidian block link).

**Stance link**: A typed claim-to-claim relation — `supports` or `disputes` (CiTO senses). Frozen pending the workflow-component audit.

**Authority**: Two unrelated things share the word. The compile tool's source ledger carries an `authority` enum (official, primary, secondary, community, synthetic, unknown), set by the compile wrapper. The vault's former `authority` frontmatter field had no writer and is retired.

### Verification

**Check**: One named verification a note or claim is put through; most are mechanical, some are LLM judgment.

**Four-state result**: A check's outcome: MATCHED, UNMATCHED, UNREACHABLE (could not run — never guilt), or SKIPPED (does not apply).

**Verified event**: The dated, attributed record that a named check passed on a note; only MATCHED mints one.

**Closing check**: A check whose standing can hold a surface; closing is a property of the surface, not of the check.

**Trust tier**: A note's derived standing: unverified → machine-confirmed → human-reviewed (cumulative).

**Lifecycle linter**: The one check that classifies every literature note against live Zotero from three reads (the versions map, the trash map, the top-level items), at capture and at verify through one code path. Its pre-commit leg is held.

**Review queue**: The append-only findings file (`inbox/review-queue.md`) every warn, hold, and alert writes to.

**Acknowledgment**: A human's standing acceptance of a finding, identified by the derived scope `sha256(check \0 target \0 target content hash)`; for a note-targeted finding the content hash is the note's `managed-sha256`. If the target's body changes, the scope no longer matches and the finding re-fires. An ack lets a check stand down; it never erases the finding.

**Publish gate**: The fail-closed verification boundary every publication crosses.

**Update notice**: A registry's post-publication signal about an item, such as a retraction or correction, recorded with its publication date and the date it was detected.
