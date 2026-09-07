# research-vault

Trust-first academic research on a personal knowledge vault: every claim traceable to a real source, verified by mechanical checks.

## Language

### Vault

**Vault**: A private git repository of markdown notes — the researcher's durable knowledge store, built to outlive its tools (ADR 0001) as an OKF bundle.

**Type (OKF)**: A note's kind, derived from its folder — `literatures/` → literature, `synthesis/` → synthesis, `log/` → daily, `inbox/` → fleeting, and only `projects/<name>/draft.md` → project. Notes under `system/` and at the vault root carry any non-empty type, freely chosen.

**Evidence layer**: The vault's machine-projected record of admitted sources (`literatures/`); never free-written.

**Synthesis layer**: The LLM-maintained pages (`synthesis/`) that arrange claims across sources; freely rewritable because it asserts arrangement, not evidence.

**Literature note**: The vault projection of one item, filename = citekey; a managed region above free prose.

**Synthesis note**: One page of the synthesis layer, carrying block-anchored claims with stance links.
_Avoid_: topic page (collides with OpenAlex topics)

**Project**: A manuscript or deliverable in progress (`projects/<name>/`), with a publication lifecycle.

**Inbox**: Fleeting captures and the review queue (`inbox/`); never an admission path for citable sources.

**Log**: The append-only per-day activity record (`log/`), summarized in root `log.md`.

**System folder**: The vault's support artifacts (`system/`): templates, bases, and the bibliography export.

**Managed region**: The machine-regenerated span of a literature note, marked in the note; never hand-edited.

### Evidence and claims

**Source**: The document itself, existing in the world before and independent of any library record — never the journal, repository, or outlet.
_Avoid_: "source" for an outlet — that is a **venue**, which is what OpenAlex's "source" means and ours never does

**Item**: A source's library record (CSL/Zotero vocabulary) — the citekey-bearing metadata object that admission creates.

**Venue**: The journal, repository, or outlet an item appeared in.

**Citekey**: The stable, human-readable key (Better BibTeX) joining prose citations, filenames, and the bibliography.

**Citable**: What a claim is allowed to cite: an item admitted in Zotero whose literature note exists here and is neither excluded nor superseded — being in the library is not yet being citable here.

**Claim**: One assertion carried by a note line, tagged with its evidence boundary and anchored for linking.

**Evidence-boundary tag**: The per-claim marker of epistemic status — quote, paraphrase, inference, or open-question.

**Claim link**: The global address of a claim: `citekey#^claim-id` (an Obsidian block link).

**Stance link**: A typed claim-to-claim relation — `supports` or `disputes` (CiTO senses).

**Admission**: The human act of accepting a source into Zotero — the only way anything becomes citable.

**Import**: The machine projection of an admitted item into the evidence layer — a literature note rendered, never authored.

**Bibliography export**: The whole admitted library used to resolve a citekey, before any citability judgment.

### Verification

**Screening state**: A literature note's PRISMA-style status: unscreened, included, excluded, or superseded — note-level only (a superseded *claim* is a deprecation carrying a superseded-by pointer, not a status).

**Check**: One named verification a note or claim is put through; most are mechanical, some are LLM judgment.

**Four-state result**: A check's outcome: MATCHED, UNMATCHED, UNREACHABLE (could not run — never guilt), or SKIPPED (does not apply).

**Verified event**: The dated, attributed record that a named check passed on a note; only MATCHED mints one.

**Closing check**: A check whose standing can hold a surface; closing is a property of the surface, not of the check.

**Trust tier**: A note's derived standing: unverified → machine-confirmed → human-reviewed (cumulative).

**Review queue**: The append-only findings file (`inbox/review-queue.md`) every warn, hold, and alert writes to.

**Acknowledgment**: A human's standing acceptance of a finding, scoped to the target's content hash — if the target changes, the finding re-fires. An ack lets a check stand down; it never erases the finding.

**Publish gate**: The fail-closed verification boundary every publication crosses.

**Update notice**: A registry's post-publication signal about an item, such as a retraction or correction, recorded with its publication date and the date it was detected.
