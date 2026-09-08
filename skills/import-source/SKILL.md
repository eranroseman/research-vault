---
name: import-source
description: Use when a person asks to import, catalog, refresh, or backfill a source they have admitted to Zotero in a research-vault vault
disable-model-invocation: true
---

# Import an admitted source

Admission is the human act of accepting a source into Zotero, and it is the **only** way anything becomes citable. This skill is the step after: the machine projection of an admitted item into the evidence layer, plus the synthesis work that projection makes possible. If the item is not in Zotero yet, stop and say so — nothing in `inbox/` is citable, and no amount of importing changes that.

**No project is required.** The information flow — admit, catalog, integrate — is continuous and project-independent, so every step below runs on a vault with zero projects; only `find-sources` is project-scoped, because its deliverable is one project's PRISMA-S search trail.

In every command, `PATH` is the vault and `CITEKEY` is the Better BibTeX key — read it off the admitted item in Zotero, where Better BibTeX shows it in the item list's **Citation Key** column and in the item pane's own `Citation Key` row; never invent or guess one. Every mechanical act below — a literature note, a managed region, a `verified` event, a review-inbox entry — is a CLI verb call: you compose and explain, the CLI writes.

## 1. Catalog: `import-note`

```sh
python3 -m research_vault import-note CITEKEY --vault PATH
```

The catalog comes first and answers to no judgment of yours: nothing downstream — no dedup question, no synthesis decision, no hold — can stop the literature note from landing or hold it back until you have made up your mind. When the projection changed, this renders `literatures/CITEKEY.md` from Zotero (managed region above the free region, which survives untouched) and regenerates root `log.md`.

Every outcome is an answer, including the two that write nothing:

| Exit | stdout        | What happened                                                       |
| ---- | ------------- | ------------------------------------------------------------------- |
| `0`  | the note path | The projection changed; the managed region was rewritten.           |
| `0`  | `NOOP`        | The projection is identical. Nothing was written. See §6 below.     |
| `1`  | *(nothing)*   | Invalid citekey, citekey not in Zotero, or the render was rejected. |

**Every nonzero exit files its own review record.** The CLI writes it through the same writer the `finding` verb uses, in addition to the message it prints on stderr — you never file one for a failed import yourself, and you never need to:

| Failure                                   | Check id  | Result    | Reason code        |
| ----------------------------------------- | --------- | --------- | ------------------ |
| Citekey cannot name a literature note     | `citekey` | UNMATCHED | `schema-violation` |
| Citekey is absent from the Zotero library | `citekey` | UNMATCHED | `not-admitted`     |

Read the stderr message back verbatim; do not summarize it as "the import failed". If stderr also carries `warning: review record refused:`, say so out loud — that means the failure has **no** durable record, and the person needs to know the queue is not carrying it.

## 2. Identifier discovery before any SKIPPED sticks

An item with no DOI and no PMID would make the `update-notice` check SKIPPED — and a DOI-less retracted paper must never be structurally exempt from the update-notice gate. So no SKIPPED identifier result is final until discovery has been attempted:

```sh
python3 -m research_vault verify --vault PATH
```

`verify` runs discovery itself, on the network, for every bibliography entry lacking a DOI: a Crossref bibliographic query by title/author/year and a PubMed lookup, feeding whatever it finds into the same run's identifier checks. It reports the attempt under check id `identifier-discovery` and files its own finding when discovery comes up empty or unreachable.

Discovery reads the bibliography, so it can only run **after** the catalog step has put the item there — the ordering rule is about what may be believed, not about clock time. Never report a SKIPPED identifier result as settled from a run made with `--offline` or from before the import; run `verify` with the network on and report what it says. Route any deeper reading of that run to `verify-citations`.

## 3. Registry-first dedup

Before creating or editing anything in `synthesis/`, read `synthesis/index.md` and the recent `log/` entries. This is a different question from the re-import no-op: the no-op asks whether *this note* changed; dedup asks whether the *topic* already has a page. Invoke `synthesis-conventions` and follow it directly — its rules govern this step, and restating them here is exactly the drift that guard exists to prevent.

If an indexed page already covers the topic, add to it. Never create a second page for a topic the index already names.

## 5. The 2+-source threshold

A synthesis page earns its existence at two or more sources on the same topic — `synthesis-conventions` owns that threshold and it is the only one. Importing the first source on a topic creates no page: its claims stay in the literature note until a second source gives them something to arrange against. Say that plainly rather than presenting it as a shortfall.

## 6. Re-import is a no-op, and that is a result

`import-note` decides re-imports by **render-first comparison**: it re-renders the managed projection from Zotero and compares it with what is on disk. Identical means `NOOP` and exit `0`, and it means the vault is already correct.

Report it as the outcome it is — "already current, nothing to write" — never as an error, and never as an import you performed. Attachment hashes (`fixity-sha256`) play no part in this: annotations and metadata live in Zotero's database, so an unchanged PDF says nothing about whether the projection changed. Those hashes are fixity and acknowledgment-scope anchors, nothing more.

## Four-state honesty

| Result      | Meaning at import                                                                                                       |
| ----------- | ----------------------------------------------------------------------------------------------------------------------- |
| MATCHED     | The check ran and agreed. Only the CLI's deterministic checks mint a `verified` event; nothing in this skill ever does. |
| UNMATCHED   | The check ran and disagreed. Already in the review queue — do not file it again.                                        |
| UNREACHABLE | The check could not run — a network or service outage. **Never a verdict on the source.** Retry later.                  |
| SKIPPED     | The item lacks the field the check needs. Automatic only, and never final before discovery has been attempted (§2).     |

The same honesty covers your own reading. A source you read only in part is reported **partial**, with the range you did not read named — the free region you skipped, the pages an attachment would not open past, the sections you never reached. That is SKIPPED applied to reading: an unread stretch must never read as read, exactly as an unrun check must never read as run. It is a rule about what you say, not about what you file — no verb watches your reading, which is precisely why the label has to come from you.

Never describe an outage as a failure or as "probably fine". Never report a `NOOP` as an import you performed. Never claim a check ran that did not, and never claim a `verified` event exists — reading events is `trust-tier`'s job, running checks is `verify-citations`', and minting events is the CLI's alone.

## Routing

| Need                                    | Route to                                     |
| --------------------------------------- | -------------------------------------------- |
| Find sources to admit                   | `find-sources`                               |
| Claim, quote, and stance-link syntax    | `evidence-conventions`                       |
| Synthesis page rules and thresholds     | `synthesis-conventions`                      |
| Run the deterministic checks            | `verify-citations`                           |
| Acknowledge a finding this import filed | `project-flow` or `publish` (the `ack` verb) |
