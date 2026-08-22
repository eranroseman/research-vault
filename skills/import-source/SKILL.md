---
name: import-source
description: Use when a person asks to import, catalog, refresh, or backfill a source they have admitted to Zotero in a knowledge-harness vault
disable-model-invocation: true
---

# Import an admitted source

Admission is the human act of accepting a source into Zotero, and it is the **only** way anything becomes citable. This skill is the step after: the machine projection of an admitted item into the evidence layer, plus the synthesis work that projection makes possible. If the item is not in Zotero yet, stop and say so — nothing in `inbox/` is citable, and no amount of importing changes that.

**No project is required.** The information flow — admit, catalog, integrate — is continuous and project-independent, so every step below runs on a vault with zero projects; only `find-sources` is project-scoped, because its deliverable is one project's PRISMA-S search trail.

In every command, `PATH` is the vault and `CITEKEY` is the Better BibTeX key — read it off the admitted item in Zotero, where Better BibTeX shows it in the item list's **Citation Key** column and in the item pane's own `Citation Key` row; never invent or guess one. Every mechanical act below is a CLI verb call: you compose and explain, the CLI writes. Never hand-write a literature note, a managed region, a `verified` event, or a review-inbox entry.

## 1. Catalog: `import-note`

```sh
python3 -m knowledge_harness import-note CITEKEY --vault PATH
```

The catalog comes first and answers to no judgment of yours: nothing downstream — no dedup question, no synthesis decision, no hold — can stop the literature note from landing or hold it back until you have made up your mind. When the projection changed, this renders `literatures/CITEKEY.md` from Zotero (managed region above the free region, which survives untouched) and regenerates root `log.md`.

Every outcome is an answer, including the two that write nothing:

| Exit | stdout        | What happened                                                                                              |
| ---- | ------------- | ---------------------------------------------------------------------------------------------------------- |
| `0`  | the note path | The projection changed; the managed region was rewritten.                                                  |
| `0`  | `NOOP`        | The projection is identical. Nothing was written. See §6 below.                                            |
| `1`  | *(nothing)*   | Invalid citekey, citekey not in Zotero, the auto-export disagrees with Zotero, or the render was rejected. |
| `3`  | *(nothing)*   | The auto-export could not be observed at all — an outage. Retry later.                                     |

**Every nonzero exit files its own review record.** The CLI writes it through the same writer the `finding` verb uses, in addition to the message it prints on stderr — you never file one for a failed import yourself, and you never need to:

| Failure                                   | Check id     | Result      | Reason code        |
| ----------------------------------------- | ------------ | ----------- | ------------------ |
| Citekey cannot name a literature note     | `citekey`    | UNMATCHED   | `schema-violation` |
| Citekey is absent from the Zotero library | `citekey`    | UNMATCHED   | `not-admitted`     |
| Auto-export disagrees with the library    | `autoexport` | UNMATCHED   | `mismatch`         |
| Auto-export could not be observed         | `autoexport` | UNREACHABLE | `outage`           |
| Render rejected (nothing was written)     | `render`     | UNMATCHED   | `schema-violation` |

Read the stderr message back verbatim; do not summarize it as "the import failed". If stderr also carries `warning: review record refused:`, say so out loud — that means the failure has **no** durable record, and the person needs to know the queue is not carrying it.

## 2. Identifier discovery before any SKIPPED sticks

An item with no DOI and no PMID would make the `doi`, `metadata`, and `update-notice` checks SKIPPED — and a DOI-less retracted paper must never be structurally exempt from the update-notice gate. So no SKIPPED identifier result is final until discovery has been attempted:

```sh
python3 -m knowledge_harness verify --vault PATH
```

`verify` runs discovery itself, on the network, for every bibliography entry lacking a DOI: a Crossref bibliographic query by title/author/year and a PubMed lookup, feeding whatever it finds into the same run's identifier checks. It reports the attempt under check id `identifier-discovery` and files its own finding when discovery comes up empty or unreachable.

Discovery reads the bibliography, so it can only run **after** the catalog step has put the item there — the ordering rule is about what may be believed, not about clock time. Never report a SKIPPED identifier result as settled from a run made with `--offline` or from before the import; run `verify` with the network on and report what it says. Route any deeper reading of that run to `verify-citations`.

## 3. Registry-first dedup

Before creating or editing anything in `synthesis/`, read `synthesis/index.md` and the recent `log/` entries. This is a different question from the re-import no-op: the no-op asks whether *this note* changed; dedup asks whether the *topic* already has a page. Invoke `synthesis-conventions` and follow it directly — its rules govern this step, and restating them here is exactly the drift that guard exists to prevent.

If an indexed page already covers the topic, add to it. Never create a second page for a topic the index already names.

## 4. Integrate at import

Integration is not a separate later chore. Once the catalog has landed, the source's claims join the synthesis layer in the same session: update the covering synthesis page, and add `[supports:: [[citekey#^claim-id]]]` / `[disputes:: [[citekey#^claim-id]]]` stance links against the claims already there. Stance links target another *claim link*, never a bare note.

These land immediately, without asking. Exactly three conditions hold a single claim back — surgically, one claim at a time, never the whole import:

- **Contradiction** — the new claim contradicts a claim already in the synthesis layer. Preserve both and link them with `disputes`; never resolve a contradiction by rewording or dropping either side.
- **Low or absent confidence** — an inference claim whose `[confidence:: ...]` is low, or missing entirely.
- **Schema violation** — the claim cannot be written to §5's shape: no resolvable anchor, no citekey, a stance link with no claim-link target.

Each held claim gets a review record, and the `finding` verb is the only way you may write one:

```sh
python3 -m knowledge_harness finding integrate CLAIM_LINK UNMATCHED "contradiction — ONE-LINE REASON" --vault PATH
python3 -m knowledge_harness finding integrate CLAIM_LINK UNMATCHED "low-confidence — ONE-LINE REASON" --vault PATH
python3 -m knowledge_harness finding integrate CLAIM_LINK UNMATCHED "schema-violation — ONE-LINE REASON" --vault PATH
```

The target is the source claim link (`citekey#^claim-id`) — surgical means the record names the one claim, not the import. If one claim needs two of these on the same day, the verb refuses the second rather than quietly overwriting the first: give each a distinct `--target-hash` so both stay separately identifiable and acknowledgeable. Read the refusal back; never work around it by editing the queue.

A hold is a hold on *integration only*. The literature note is already written, the source is already citable, and the person can act on the finding whenever they get to it.

## 5. The 2+-source threshold

A synthesis page earns its existence at two or more sources on the same topic — `synthesis-conventions` owns that threshold and it is the only one. Importing the first source on a topic creates no page: its claims stay in the literature note until a second source gives them something to arrange against. Say that plainly rather than presenting it as a shortfall.

## 6. Re-import is a no-op, and that is a result

`import-note` decides re-imports by **render-first comparison**: it re-renders the managed projection from Zotero and compares it with what is on disk. Identical means `NOOP` and exit `0`, and it means the vault is already correct.

Report it as the outcome it is — "already current, nothing to write" — never as an error, and never as an import you performed. Attachment hashes (`fixity-sha256`) play no part in this: annotations and metadata live in Zotero's database, so an unchanged PDF says nothing about whether the projection changed. Those hashes are fixity and acknowledgment-scope anchors, nothing more.

## 7. Refresh mode: fresh, stale, orphaned

Refresh is note-level maintenance, and it is the same verb — re-running `import-note` for a citekey that already has a note. Three outcomes, and these are the words to use:

| Word         | What it means                                                                                 | How the CLI says it                                                                                             |
| ------------ | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **fresh**    | The projection matches Zotero.                                                                | `import-note` prints `NOOP`, exit `0`.                                                                          |
| **stale**    | Re-rendering differs, so the managed region was rewritten. The free region below it survives. | `import-note` prints the note path, exit `0`.                                                                   |
| **orphaned** | The note's item has left the library, so nothing projects onto it any more.                   | `import-note` reports `citekey not found` on stderr, exit `1`, and files the `citekey` / `not-admitted` record. |

Two honest limits. First, **orphan detection is per-citekey**: `verify` reports an orphaned note as a `citekey` UNMATCHED only if the note still cites itself, and a note with no quote or paraphrase claims cites nothing at all — so a sweep with `import-note` is the only way to find every orphan. Second, the CLI's `staleness` verb is a **different** question: it compares `system/bibliography.json` with the current Zotero library, not a note with its projection. Never report a `staleness` result as a note being stale.

An orphaned note is never deleted. Records deprecate, never delete — the note stays, and the person decides what its screening state should become.

## 8. Batch mode

For a backfill — refreshing every literature note in the vault:

```sh
python3 -m knowledge_harness backfill-selectors --vault PATH
```

This re-imports every note in `literatures/`, in citekey order, with the same per-note contract as above: each note comes back fresh, stale, or orphaned, and every failure files its own record. Exit `0` means every note succeeded; exit `1` means at least one did not — read the printed warnings, then run `inbox` to see the records they filed:

```sh
python3 -m knowledge_harness inbox --vault PATH
```

Report the per-note breakdown, not just the exit code. A batch that ends `1` because one item left the library is not a broken backfill.

## 9. Archive at import (web sources)

A source with a `url` and no `doi` is a web source, and web content rots. Rescue is impossible after the fact, so the snapshot has to exist **now**, at import — later detection cannot bring a dead page back. Run this for every web source you catalog, in the same session:

```sh
python3 -m knowledge_harness archive-source CITEKEY --vault PATH
```

The verb triggers Internet Archive Save Page Now, confirms the capture against the Wayback availability API, and writes the confirmed snapshot into the note's frontmatter as `archive-url`. **It is the sole writer of that field** — never hand-write, edit, or remove an `archive-url` yourself, in any note, for any reason. That single owner is what keeps the evidence layer machine-written.

If the person already has a snapshot, record that one instead of capturing a fresh one — the verb confirms it resolves before writing it:

```sh
python3 -m knowledge_harness archive-source CITEKEY --vault PATH --snapshot SNAPSHOT-URL
```

It answers with a four-state line and the shared exit codes:

| Exit | Result      | Meaning                                                                                                                |
| ---- | ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| `0`  | MATCHED     | A snapshot is recorded — freshly captured, supplied, or already present. The snapshot URL prints on the next line.     |
| `0`  | SKIPPED     | Not a web source (it has a `doi`, or no `url`). Nothing to archive, and nothing wrong.                                 |
| `1`  | UNMATCHED   | The archive is serving no snapshot for that URL, or the supplied one 404s. Nothing was written.                        |
| `3`  | UNREACHABLE | Save Page Now or the confirmation call could not be reached. **An outage, not a verdict** — retry on the next refresh. |
| `2`  | —           | The verb could not run: no such note, an unsafe citekey, malformed frontmatter. Read the message back verbatim.        |

Never present an UNREACHABLE archive attempt as archived, and never write a URL the verb declined to record — an outage is not a snapshot. `archive-url` is pass-through metadata, so a recorded snapshot survives every later re-render; `accessed` is captured on day one and never overwritten.

`verify`'s `web-archive` check is the reader on the other side: it files a `missing-archive` finding when a web source has no `archive-url`, or when the recorded one no longer resolves. That check only ever detects — this verb is the only thing that captures.

## Four-state honesty

| Result      | Meaning at import                                                                                                       |
| ----------- | ----------------------------------------------------------------------------------------------------------------------- |
| MATCHED     | The check ran and agreed. Only the CLI's deterministic checks mint a `verified` event; nothing in this skill ever does. |
| UNMATCHED   | The check ran and disagreed. Already in the review inbox — do not file it again.                                        |
| UNREACHABLE | The check could not run — a network or service outage. **Never a verdict on the source.** Retry later.                  |
| SKIPPED     | The item lacks the field the check needs. Automatic only, and never final before discovery has been attempted (§2).     |

Never describe an outage as a failure or as "probably fine". Never report a `NOOP` as an import you performed. Never claim a check ran that did not, and never claim a `verified` event exists — reading events is `trust-tier`'s job, running checks is `verify-citations`', and minting events is the CLI's alone.

## Routing

| Need                                    | Route to                                |
| --------------------------------------- | --------------------------------------- |
| Find sources to admit                   | `find-sources`                          |
| Claim, quote, and stance-link syntax    | `evidence-conventions`                  |
| Synthesis page rules and thresholds     | `synthesis-conventions`                 |
| Run the deterministic checks            | `verify-citations`                      |
| Acknowledge a finding this import filed | `project` or `publish` (the `ack` verb) |
