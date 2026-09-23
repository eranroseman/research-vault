# research-vault

A Claude Code plugin for knowledge work — academic research first (question → literature → compile → draft → submit), then analysis/reports, personal knowledge management, and long-form writing.

Success criterion: **trustworthy output** — every claim traceable to a real source, zero fabricated citations.

research-vault is an Obsidian vault, a Python CLI (`research_vault`), and a set of agent skills. The vault holds the evidence; the CLI performs every mechanical write; the skills carry the judgment. That separation is the whole design: **the agent composes and explains, the CLI writes.** No skill hand-edits a machine surface — `literature/`, `fulltext/`, `wiki/`, `log/`, `system/`, the review queue — mints a verification event, or files a review record: those are verbs, and only the CLI runs them (under `wiki/`, the adopted compile tool's transaction engine). Prose is composed by hand where it belongs: project drafts, and per-source notes written in Zotero, which capture renders into the literature note.

## The Iron Law

> No claim enters a draft without a verified source first.

A claim line exists only after its literature note exists and its citation key resolves. Prose written ahead of its evidence goes to `inbox/`, never `projects/` — it stays fleeting prose, not a tagged claim, until the source is captured.

**Selection is the person's act.** Adding a source to Zotero is the only way anything becomes citable, and no capture, search, or agent step can substitute for it.

## Claims carry their own evidence

Claims are written in project drafts and arranged into `wiki/` pages by the compile tool. A verified quote lives once, in the literature note capture writes from Zotero; a draft links it and never retypes it. Whatever is not on the line does not travel with it. So everything rides the line:

```
- (quote|paraphrase|inference|open-question) <text> [@citation-key, locator] [field:: value ...] ^claim-id
```

- The **evidence-boundary tag** states what kind of claim this is. `open-question` marks a claim with no derivation edge — itself lintable, not an escape hatch.
- The **citation key and locator** parse losslessly to CSL `locator` + `label`.
- The **anchor** derives from stable content (a Zotero annotation key, else a quote hash), never from render order, so re-rendering never breaks an existing claim link.

Quotes put the verbatim text in a blockquote beneath the claim line, where a checker can byte-compare it (that check is frozen while the compiled layer settles; see CONTEXT.md). Nothing is retyped: when the same quote is needed elsewhere, link the existing claim (`[[citation-key#^claim-id]]`) rather than creating a second, unverified copy.

**Claims are deprecated, never deleted.** Retirement is a transition record written on the same line — status, date, actor, reason, and a `superseded-by` link where a successor exists. The anchor survives the transition.

## Four-state honesty

Every check reports one of four states, and the distinctions are load-bearing:

| Result        | Meaning                                                                                 |
| ------------- | --------------------------------------------------------------------------------------- |
| `MATCHED`     | The check ran and agreed.                                                               |
| `UNMATCHED`   | The check ran and disagreed.                                                            |
| `UNREACHABLE` | The check could not run — a network or service outage. **Never a verdict on the work.** |
| `SKIPPED`     | The item lacks the field the check needs. Never presented as checked and clean.         |

An outage is never a failure and never a pass. A skipped claim is never reported as verified. The vocabulary exists so that silence can never read as clearance.

The same honesty governs reading, where no verb is watching: a source read only in part is reported **partial**, with the unread range named.

## Verification has two tiers, and only one of them blocks

**Deterministic checks** (`verify`) are the real gate. Quote text is byte-compared against the literature note; DOIs are resolved; metadata is reconciled against the registry; update notices are checked for retractions. Only these mint `verified` events, and only on a genuine `MATCHED`.

**Factored verification** (`factcheck`) is an LLM decompose-and-check pass at draft → review. It selects claims mechanically under a budget cap, adjudicates each in one pass, and files every non-matching result as a warn-tier finding. It **never blocks anything** — not a commit, not a publish. One pass, never a panel: re-running the same model in different roles separates the roles, not the errors, so a second agreeing voice buys agreement rather than confidence.

Even a clean factcheck is narrower than it sounds. It validates declarations, not their truth — whether a claim says what its cited source supports, never whether that source is right.

## The review queue

Every non-matching result becomes a finding in `inbox/review-queue.md`, carrying a reason code from a controlled registry (`schema-violation`, `mismatch`, `outage`, `retracted`, `drift`, `budget-cap`, `not-admitted`, …). The queue is append-only; a rewritten line is a lint failure.

Findings are acknowledged, never deleted — through the `ack` verb, with a registry reason code and a real `human:` actor. Consent spoken in conversation writes nothing. An acknowledgment is scoped to the content it was granted for, so editing the note takes it away again.

Draining the queue is part of every orientation, and the oldest entry's age gets reported out loud: a warn queue nobody drains is a silent failure.

## Trust tiers

A cumulative tier is derived per literature note — `unverified`, `machine-confirmed`, `human-reviewed` — by the `trust-tier` verb reading `verified` events; nothing is stored on the note. `unverified` is the normal starting state, not a verdict of failure; it means the checks have not yet run or not yet matched. (`human-reviewed` is today a named open deferral — no shipped surface mints its event yet; spec §10.2.)

## The layers

- **`literature/`** — one note per captured source, wholly machine-written: `capture` regenerates the whole note from Zotero on every run — frontmatter carrying Zotero's own fields and the provenance tuple (server id, item key, item version, citation key, attachments, text files); a body carrying the embed of the compiled page once one exists, the item and attachment links into Zotero, and the item's Zotero child notes. Per-source prose is written in Zotero as a child note, and capture renders it.
- **`fulltext/`** — the text layer, gitignored: one `<attachment key>.md` per attachment with usable extracted text, regenerated by capture; the compile input.
- **`wiki/`** — the compiled layer, arrangement not evidence, written only by the adopted compile tool (claude-obsidian) through its transaction gate: per-source pages under `wiki/sources/`, concept pages under `wiki/concepts/`, each citing its source as `[[<citation key>]]`. A page earns its existence at two or more captured sources on the same topic, and that threshold *permits* a page without obligating one — sources set side by side with nothing said about how they relate are a compilation, not a synthesis.
- **`projects/`** — the framed question, the search log, the draft. One project note carries the disposition frontmatter.
- **`inbox/`**, **`log/`** — the review queue and the append-only activity log.

Contradiction is preserved, not resolved. When a new claim contradicts one already in a draft or a compiled page, both sides stay and are linked with `disputes`; a `disputed-claim` finding surfaces standing counter-evidence rather than letting it get silently relied on.

## The flow

| Step           | Skill                      | What it does                                                                                                                                  |
| -------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Provision      | `setup-vault`              | Scaffold, diagnose, and provision companions — with per-item consent, never inferred                                                          |
| Frame / resume | `project-flow`             | Orient, drain the inbox, surface trust tiers, frame the question, run gap analysis                                                            |
| Search         | `find-sources`             | Literature search upstream of Zotero, logged PRISMA-S style; terminates at the person's selection                                             |
| Catalog        | `capture-source`           | Add an item to Zotero, capture it into `literature/` and `fulltext/`, propagate a citation-key change                                         |
| Analyze        | `critical-analysis-report` | Critical analysis of one paper: context, summary, nine judgments, each claim with a locator, plus a notes trail a fresh-context pass verifies |
| Critique       | `paper-critical-analysis`  | In-depth critique of one paper: extract, list what it does not say, judge nine dimensions in a fresh context, then verify every locator                        |
| Verify         | `verify-citations`         | Run the deterministic suite and report it grouped by check id                                                                                 |
| Factcheck      | `factcheck-draft`          | Non-blocking LLM adjudication of selected claims                                                                                              |
| Publish        | `publish`                  | The armed gate and its disposition menu                                                                                                       |

Skills route the need actually stated, never an enlarged version of it. "Capture this paper" is not "capture it and rebuild the concept page."

## Publishing

Publishing is the most irreversible thing the vault does, and it runs through an armed gate: `arm-publish` sets a flag the Stop hook reads, and from that moment the session is held until the attempt lands, is acknowledged, or is disarmed. A refusal leaves the gate armed.

The pre-publication menu is exactly three options — publish, park, keep-draft — and the person chooses. After publication, only two dispositions remain: correct or withdraw. Re-publishing is refused, because it would record a correction as a first publication in tags and events that are never deleted. **The original tag is never deleted.** A correction adds a tag; it does not replace one. A correction on the day of publication just works — every tag carries a UTC time.

Deletion is not on the menu. A project is deleted only when the person explicitly asks *and* types `discard` on its own; anything less gets park or keep-draft offered instead.

The gate has one audited bypass, and it is the person's to ask for, never the agent's to suggest. It is recorded, not forgiven.

## Rationalizations, answered

Guards attract excuses, so the skills answer the common ones in-line rather than trusting good intentions:

| The temptation                               | The rule that forbids it                                                                                                             |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| "I'll cite it later."                        | The Iron Law — no claim line before its citation key resolves.                                                                       |
| "It's common knowledge."                     | Common knowledge is not an evidence-boundary tag.                                                                                    |
| "The abstract said so."                      | An abstract cannot supply the methods, conditions, and magnitudes a claim states. Read the source or say no full text was available. |
| "It's paywalled, I can't check the wording." | Use `paraphrase` or `inference`. A `quote` tag commits to text a checker can byte-compare.                                           |
| "`UNREACHABLE` is basically fine."           | It holds the gate. An outage is never a failure and never a pass.                                                                    |
| "They said go ahead, so the ack is covered." | Consent spoken in conversation writes nothing. Only the verb writes.                                                                 |

## Zotero add-ons

Installing a Zotero add-on is a human step in the setup wizard. Doctor reads this same table (packaged as `research_vault/templates/zotero-addons.md`) and reports each row's `active`/`appDisabled` state from the running profile, plus whether its automatic mode is on.

| Add-on             | Add-on id                              | Need        | Automatic-mode preference          |
| ------------------ | -------------------------------------- | ----------- | ---------------------------------- |
| Better BibTeX      | `better-bibtex@iris-advies.com`        | required    |                                    |
| Attachment Scanner | `attachmentscanner@changlab.um.edu.mo` | recommended |                                    |
| DOI Manager        | `zoteroshortdoi@wiernik.org`           | recommended | `extensions.shortdoi.autoretrieve` |
| PMCID fetcher      | `zotero-pmcid-fetcher@iris-advies.com` | recommended | `extensions.zotero.pmcid.auto`     |
| MarkDB-Connect     | `daeda@mit.edu`                        | optional    |                                    |

## Development

One command runs every form and lint owner, locally and in CI:

```bash
source .venv/bin/activate && pre-commit run --all-files
```

Each file type has exactly one form owner (`.pre-commit-config.yaml` is the matrix): ruff for Python, mdformat for CommonMark Markdown, yamlfix for YAML, pyproject-fmt for TOML, stdlib `json.tool` canonical form for JSON manifests (asserted in `tests/test_config_validity.py`), and — for vault-dialect Markdown, which no off-the-shelf formatter speaks — the sole writer, verified by `tests/test_canonical_form.py`.
