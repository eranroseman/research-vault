# knowledge-harness

Trust-first academic research on a personal knowledge vault: every claim traceable to a real source, verified by mechanical checks. This glossary is the meaning layer; naming governance (why these words) lives in docs/terminology.md.

## Vault

**Vault**: A private git repository of markdown notes — the researcher's durable knowledge store, packaged to survive its tools (currently as an OKF — Open Knowledge Format — bundle; ADR 0001).
_Avoid_: knowledge base, second brain

**Evidence layer**: The vault's machine-projected record of admitted sources (`literatures/`); never free-written.
_Avoid_: sources folder, references layer

**Synthesis layer**: The LLM-maintained pages (`synthesis/`) that arrange claims across sources; freely rewritable because it asserts arrangement, not evidence.
_Avoid_: atlas, wiki, topic pages

**Literature note**: The vault projection of one Zotero item, filename = citekey; a managed region above free prose.
_Avoid_: source note, paper note, reference note

**Project**: A manuscript or deliverable in progress (`projects/<name>/`), with a publication lifecycle.
_Avoid_: effort, draft folder

**Inbox**: Fleeting captures and the review queue (`inbox/`); never an admission path for citable sources.
_Avoid_: `+`, capture folder

**Log**: The append-only per-day activity record (`log/`), summarized in root `log.md`.
_Avoid_: calendar, journal, daily notes folder

**Managed region**: The bridge-regenerated span of a literature note between `%%hk-managed%%` markers; never hand-edited.
_Avoid_: generated section, machine block

## Evidence and claims

**Item**: A bibliographic record in Zotero/CSL terms — the thing a citekey names.
_Avoid_: work (OpenAlex sense), paper (narrower than the corpus)

**Source**: The cited document itself, in the scholarly sense (primary/secondary source).
_Avoid_: using "source" for a journal, repository, or outlet — that is a **venue**, which is also what OpenAlex's "source" means and ours never does

**Citekey**: The stable, human-readable key (Better BibTeX) joining prose citations, filenames, and the bibliography.
_Avoid_: reference ID, bibkey

**Citable**: What a claim is allowed to cite: an item admitted in Zotero whose literature note exists here and is neither excluded nor superseded — being in the library is not yet being citable here.
_Avoid_: in the library, in the bibliography

**Claim**: One assertion carried by a note line, tagged with its evidence boundary and anchored for linking.
_Avoid_: statement, fact

**Evidence-boundary tag**: The per-claim marker of epistemic status — quote, paraphrase, inference, or open-question.
_Avoid_: claim type, epistemic label

**Claim link**: The global address of a claim: `citekey#^claim-id` (an Obsidian block link).
_Avoid_: claim address, claim ID (that is only the anchor fragment)

**Stance link**: A typed claim-to-claim relation — `supports` or `disputes` (CiTO senses).
_Avoid_: supported-by/contested-by (old names), related links

**Admission**: The human act of accepting a source into Zotero — the only way anything becomes citable.
_Avoid_: import (that is the projection step that follows), ingestion

**Import**: The machine projection of an admitted item into the evidence layer — a literature note rendered from Zotero, never authored.
_Avoid_: admission (that is the human act before), sync

**Bibliography export**: The universe of items a citekey can name: the Better BibTeX auto-export at `system/bibliography.json`, written only by BBT.
_Avoid_: bibliography file, reference list, citation universe (that is the evidence layer)

**Screening state**: A literature note's PRISMA-style status: unscreened, included, excluded, or superseded.
_Avoid_: unreviewed/active/rejected (old values), review status

## Verification

**Check**: One mechanical verification (citekey exists, DOI resolves, quote matches, update-notice scan, …).
_Avoid_: test, validation

**Four-state result**: A check's outcome: MATCHED, UNMATCHED, UNREACHABLE (could not run — never guilt), or SKIPPED (does not apply — automatic only).
_Avoid_: pass/fail, pytest vocabulary in vault prose

**Verified event**: The dated, attributed record of which check passed, appended to a note; only MATCHED mints one.
_Avoid_: verification log entry, audit record

**Closing check**: A check that can hold a surface (commit, publish) when it fails; warn-tier findings only inform, through the review inbox.
_Avoid_: blocking check, hard check

**Trust tier**: A note's derived standing: unverified → machine-confirmed → human-reviewed (cumulative).
_Avoid_: confidence level (that is a per-claim field), quality score

**Review inbox**: The append-only findings file (`inbox/review-queue.md`) every warn, hold, and alert writes to; drained at project orientation.
_Avoid_: issue list, warning log

**Acknowledgment**: A human's standing, hash-scoped acceptance of a finding — the recorded decision that lets a check stand down without the finding being erased.
_Avoid_: dismissal, override (an ack keeps the record; it never deletes)

**Publish gate**: The armed, fail-closed verification boundary a project crosses at publish; inert unless armed.
_Avoid_: release check, CI gate (CI is the async auditor, not the gate)

**Update notice**: A registry's post-publication signal about an item (retraction, correction, expression of concern, …), recorded bi-temporally.
_Avoid_: retraction flag (one class of notice, not the concept)
