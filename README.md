# research-vault

A Claude Code plugin for knowledge work — academic research first (question → literature → compile → draft → submit), then analysis/reports, personal knowledge management, and long-form writing.

Success criterion: **trustworthy output** — every claim traceable to a real source, zero fabricated citations.

research-vault is an Obsidian vault, a Python CLI (`research_vault`), and a set of agent skills. The vault holds the evidence; the CLI performs every mechanical write; the skills carry the judgment. That separation is the whole design: **the agent composes and explains, the CLI writes.** No skill hand-edits a machine surface — `literature/`, `fulltext/`, `wiki/`, `log/`, root `log.md`, `inbox/review-queue.md`, `system/bibliography.json`, `system/propagations/` and `system/compiled-pages.json` (the rest of `system/` is hand-edited) — mints a verification event, or files a review record: those are verbs, and only the CLI runs them (under `wiki/`, the adopted compile tool's transaction engine). Prose is composed by hand where it belongs: project drafts, and per-source notes written in Zotero, which capture renders into the literature note. A scaffolded vault's `.claude/settings.json` denies the common shell forms of a write to those paths — redirects, `tee`, `sed -i`, `cp`, `mv`, `touch`, `rm` — in a session started at the vault root; interpreters, scripts and git restores are caught only where verification detects the change (most changes to what the CLI owns are; the vault guide names the gaps).

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

Quotes put the verbatim text in a blockquote beneath the claim line, where a checker can byte-compare it (that check is frozen while the compiled layer settles; see CONTEXT.md). Nothing is retyped: when the same quote is needed elsewhere, link the existing claim (`[[citation-key#^claim-id]]`) rather than creating a second, unverified copy. That wikilink form survives only inside a claim block or an inline field; elsewhere in a note the commit normalises, it is rewritten to the markdown form `[citation-key > ^claim-id](/literature/citation-key.md#^claim-id)`, which links the same claim.

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

| Step           | Skill                     | What it does                                                                                                                                                                                                              |
| -------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Provision      | `setup-vault`             | Scaffold, diagnose, and provision companions — with per-item consent, never inferred                                                                                                                                      |
| Frame / resume | `project-flow`            | Orient, drain the inbox, surface trust tiers, frame the question, run gap analysis                                                                                                                                        |
| Search         | `find-sources`            | Literature search upstream of Zotero, logged PRISMA-S style; terminates at the person's selection                                                                                                                         |
| Catalog        | `capture-source`          | Add an item to Zotero, capture it into `literature/` and `fulltext/`, propagate a citation-key change                                                                                                                     |
| Critique       | `paper-critical-analysis` | Critical analysis of one paper: read everything it ships including released code and data, check every number, judge nine dimensions in a fresh context, edit, machine-check, then verify every locator and outside claim |
| Verify         | `verify-citations`        | Run the deterministic suite and report it grouped by check id                                                                                                                                                             |
| Factcheck      | `factcheck-draft`         | Non-blocking LLM adjudication of selected claims                                                                                                                                                                          |
| Publish        | `publish`                 | The armed gate and its disposition menu                                                                                                                                                                                   |

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

Installing a Zotero add-on is a human step in the setup wizard. Doctor reads these two tables (packaged as `research_vault/templates/zotero-addons.md`): the first names every add-on the vault declares — required, recommended, optional, or excluded on harm grounds (the lanes 2–3 spec §3) — the second the preference values each must hold, as `prefs.js` spells them. Doctor's `plugins` row fails when a required add-on is not active, an active add-on is below its minimum version, or an active add-on's effective value (its `prefs.js` line, else the default shipped in its `.xpi`) is not an accepted literal (`unset` accepts an absent key, `set` any value but an absent or empty one); its `advisory` row warns when a recommended add-on is `appDisabled` or an excluded one is active. `DOI Manager`'s two values must be in `prefs.js` before the add-on is installed.

### Add-ons

| Add-on                        | Add-on id                                    | Need        | Minimum version | Key prefix                                     | Workflows                                                  |
| ----------------------------- | -------------------------------------------- | ----------- | --------------- | ---------------------------------------------- | ---------------------------------------------------------- |
| Better BibTeX                 | `better-bibtex@iris-advies.com`              | required    | —               | `extensions.zotero.translators.better-bibtex.` | research, long-form writing                                |
| PMCID fetcher                 | `zotero-pmcid-fetcher@iris-advies.com`       | recommended | —               | —                                              | research                                                   |
| DOI Manager                   | `zoteroshortdoi@wiernik.org`                 | recommended | 2.2.0           | —                                              | research                                                   |
| Meta Refresh                  | `metarefresh@zhibo.ark0`                     | recommended | —               | —                                              | research                                                   |
| Linter for Zotero             | `zotero-format-metadata@northword.cn`        | recommended | —               | —                                              | research, personal knowledge management, long-form writing |
| Zotero Duplicate Cleaner      | `zotero-dedup@local.dev`                     | recommended | —               | —                                              | research                                                   |
| Attachment Scanner            | `attachmentscanner@changlab.um.edu.mo`       | recommended | —               | —                                              | research                                                   |
| RapidOCR for Zotero           | `pdfocrforzotero@example.com`                | recommended | —               | —                                              | research                                                   |
| MarkDB-Connect                | `daeda@mit.edu`                              | optional    | —               | —                                              | personal knowledge management                              |
| arXiv Workflow                | `arxiv@allanchain.github.com`                | optional    | —               | —                                              | research                                                   |
| scite                         | `scite-zotero-plugin@scite.ai`               | optional    | —               | —                                              | research                                                   |
| PubPeer                       | `zotero-pubpeer@pubpeer.com`                 | optional    | —               | —                                              | research, long-form writing                                |
| Citation counts               | `zotero-citation-counts@tangzhao20`          | optional    | —               | —                                              | research                                                   |
| open-citations                | `open-citations@zotero-plugin.org`           | optional    | —               | —                                              | research                                                   |
| Google Scholar citation count | `justin@justinribeiro.com`                   | optional    | —               | —                                              | research                                                   |
| ZotSeek                       | `zotseek@zotero.org`                         | optional    | —               | —                                              | personal knowledge management, research                    |
| Better Notes                  | `Knowledge4Zotero@windingwind.com`           | optional    | —               | —                                              | research, personal knowledge management, long-form writing |
| Zutilo                        | `zutilo@www.wesailatdawn.com`                | optional    | —               | —                                              | personal knowledge management, long-form writing           |
| Open PDF                      | `zotero-open-pdf@iris-advies.com`            | optional    | —               | —                                              | research, personal knowledge management                    |
| KeepZotero                    | `keepzotero@yhmtsai`                         | optional    | —               | —                                              | research                                                   |
| Zotero Focused Mode           | `zotero-focused-mode@jaeheelee.de`           | optional    | —               | —                                              | research                                                   |
| Actions and Tags              | `zoterotag@euclpts.com`                      | optional    | —               | —                                              | personal knowledge management                              |
| ZotMoov                       | `zotmoov@wileyy.com`                         | optional    | —               | —                                              | personal knowledge management                              |
| zotxt                         | `zotxt@e6h.org`                              | optional    | —               | —                                              | long-form writing                                          |
| zotero-docling                | `zotero-docling@max3925vats`                 | optional    | —               | —                                              | research, analysis and reports                             |
| MinerU for Zotero             | `mineru-for-zotero@asianfleet.github.io`     | optional    | —               | —                                              | analysis and reports, long-form writing, research          |
| Reading Time                  | `reading-time@local`                         | optional    | —               | —                                              | personal knowledge management                              |
| Zoplicate                     | `zoplicate@chenglongma.com`                  | excluded    | —               | —                                              | —                                                          |
| DOI Fix                       | `doi-fix@zotero.org`                         | excluded    | —               | —                                              | —                                                          |
| Metadata Hunter               | `metadatahunter@federicotorrielli.github.io` | excluded    | —               | —                                              | —                                                          |
| ZotMeta                       | `zotmeta@roadtodream.tech`                   | excluded    | —               | —                                              | —                                                          |
| zotero-ner                    | `zotero-name-normalizer@marcinmilkowski.pl`  | excluded    | —               | —                                              | —                                                          |
| Scholar Sidekick              | `scholar-sidekick@scholar-sidekick.com`      | excluded    | —               | —                                              | —                                                          |
| arxiv-marker                  | `arxiv-marker@lele.dev`                      | excluded    | —               | —                                              | —                                                          |
| Cita                          | `zotero-wikicite@wikidata.org`               | excluded    | —               | —                                              | —                                                          |
| zotero-openalex               | `zotero-openalex@example.com`                | excluded    | —               | —                                              | —                                                          |
| Zotero TLDR                   | `zoterotldr@syt.com`                         | excluded    | —               | —                                              | —                                                          |
| zotero-citation-tally         | `dev@daeh.info`                              | excluded    | —               | —                                              | —                                                          |
| semantic-zotero               | `tomasdanis26@gmail.com`                     | excluded    | —               | —                                              | —                                                          |
| Zotero Attanger               | `zoteroattanger@polygon.org`                 | excluded    | —               | —                                              | —                                                          |
| Zotero OCR                    | `zotero-ocr@bib.uni-mannheim.de`             | excluded    | —               | —                                              | —                                                          |
| Mktero                        | `mktero@tenglvjun.github.io`                 | excluded    | —               | —                                              | —                                                          |
| Chartero                      | `chartero@volatile.static`                   | excluded    | —               | —                                              | —                                                          |
| Add-on Market for Zotero      | `zoteroAddons@ytshen.com`                    | excluded    | —               | —                                              | —                                                          |
| Notero                        | `notero@vanoni.dev`                          | excluded    | —               | —                                              | —                                                          |
| Zotero Reading List           | `reading-list@hotmail.com`                   | excluded    | —               | —                                              | —                                                          |
| Folder Import for Zotero      | `zotero-folder-import@iris-advies.com`       | excluded    | —               | —                                              | —                                                          |
| Zotero Watch Folder           | `watch-folder@zotero-plugin.org`             | excluded    | —               | —                                              | —                                                          |
| Replication Checker (FLoRA)   | `replication-checker@forrt.org`              | excluded    | —               | —                                              | —                                                          |

### Declared settings

| Add-on                        | Preference                                                                     | Accepted             |
| ----------------------------- | ------------------------------------------------------------------------------ | -------------------- |
| PMCID fetcher                 | `extensions.zotero.pmcid.auto`                                                 | `false`              |
| PMCID fetcher                 | `extensions.zotero.pmcid.tags`                                                 | `false`              |
| DOI Manager                   | `extensions.shortdoi.autoretrieve`                                             | `"none"`             |
| DOI Manager                   | `extensions.shortdoi.monthly_verify`                                           | `false`              |
| Meta Refresh                  | `extensions.zotero.metarefresh.titleSimilarityThreshold`                       | `"2"`                |
| Meta Refresh                  | `extensions.zotero.metarefresh.useS2`                                          | `false`              |
| Meta Refresh                  | `extensions.zotero.metarefresh.useOpenAlex`                                    | `false`              |
| Meta Refresh                  | `extensions.zotero.metarefresh.fieldConferenceName`                            | `false`              |
| Meta Refresh                  | `extensions.zotero.metarefresh.backupToExtra`                                  | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.lint.onAdded`                                | `true`               |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.require-language`                       | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.require-doi`                            | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.require-journal-abbr`                   | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.require-short-title`                    | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.require-university-place`               | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.no-value-nullish`                       | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.no-field-misuse`                        | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.no-title-trailing-dot`                  | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.no-issue-extra-zeros`                   | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.no-pages-extra-zeros`                   | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.no-volume-extra-zeros`                  | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-title-sentence-case`            | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-shortTitle-sentence-case`       | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-bookTitle-sentence-case`        | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-proceedingsTitle-sentence-case` | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-title-chemical-formula`         | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-creators-case`                  | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-creators-pinyin`                | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-date-format`                    | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-filing-date-format`             | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-issue-date-format`              | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-priority-date-format`           | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-extra-order`                    | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-doi-long`                       | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-publication-title-alias`        | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-publication-title-case`         | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-pages-range`                    | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-conference-abbr`                | `false`              |
| Linter for Zotero             | `extensions.zotero.formatmetadata.rule.correct-thesis-type`                    | `false`              |
| Attachment Scanner            | `extensions.attachmentscanner.monitor_attachments`                             | `true`               |
| Attachment Scanner            | `extensions.attachmentscanner.scan_duplicates`                                 | `false`              |
| MarkDB-Connect                | `extensions.zotero.mdbc.removetags`                                            | `"addonly"`          |
| MarkDB-Connect                | `extensions.zotero.mdbc.sourcedir`                                             | `set`                |
| MarkDB-Connect                | `extensions.zotero.mdbc.matchstrategy`                                         | `"citekeyyaml"`      |
| MarkDB-Connect                | `extensions.zotero.mdbc.yamlkeyword`                                           | `"citationKey"`      |
| MarkDB-Connect                | `extensions.zotero.mdbc.filefilterstrategy`                                    | `"customfileregexp"` |
| MarkDB-Connect                | `extensions.zotero.mdbc.filepattern`                                           | `"^.+\\.md$"`        |
| arXiv Workflow                | `extensions.zotero.arxiv-workflow.merge.arXivExtra`                            | `true`               |
| arXiv Workflow                | `extensions.zotero.arxiv-workflow.features.arXivUpdate`                        | `false`              |
| arXiv Workflow                | `extensions.zotero.arxiv-workflow.merge.trashUnannotatedPDF`                   | `false`              |
| Citation counts               | `extensions.citationcounts.autoretrieve`                                       | `"none"`, `unset`    |
| open-citations                | `extensions.zotero.opencitations.writeExtra`                                   | `false`, `unset`     |
| Google Scholar citation count | `extensions.zotero.gscc.useAutoCountUpdate`                                    | `false`, `unset`     |
| ZotSeek                       | `extensions.zotero.zotseek.mcpServer.enabled`                                  | `false`, `unset`     |
| Better Notes                  | `extensions.zotero.Knowledge4Zotero.annotationNote.enableTagSync`              | `false`              |
| Better Notes                  | `extensions.zotero.Knowledge4Zotero.syncNoteIds`                               | `""`                 |
| Better Notes                  | `extensions.zotero.Knowledge4Zotero.sync.autoSyncLinkedNotes`                  | `false`, `unset`     |
| ZotMoov                       | `extensions.zotmoov.file_behavior`                                             | `"copy"`             |
| ZotMoov                       | `extensions.zotmoov.enable_automove`                                           | `false`              |
| zotero-docling                | `extensions.zoteroDocling.autoConvert`                                         | `false`, `unset`     |
| MinerU for Zotero             | `extensions.zotero.mineruForZotero.apiEnabled`                                 | `false`, `unset`     |

## Obsidian plugins

A new vault's `.obsidian/` is seeded by `scaffold --with-obsidian` from this declaration (packaged as `research_vault/templates/obsidian-plugins.md`): seeded plugins are vendored at their pin (their licence permits redistribution with no source obligation), recommended ones ship only their settings and are installed by the person from Obsidian's community list, excluded ones are not declared further. Doctor's `obsidian` row compares the configured folder (`obsidian_config_dir` in `machine.json`, default `.obsidian`) with it: it fails when an enabled plugin's, or Core's, declared key is off its accepted values, and notes a version off the pin, a core plugin toggled away from the seed, and an installed recommended plugin; its `advisory` row warns when an excluded plugin is enabled.

### Plugins

| Plugin                       | Id                                  | Need        | Pin    | Licence                          | Workflows                                           |
| ---------------------------- | ----------------------------------- | ----------- | ------ | -------------------------------- | --------------------------------------------------- |
| Dataview                     | `dataview`                          | seeded      | 0.5.68 | MIT                              | personal knowledge management, analysis and reports |
| Calendar                     | `calendar`                          | seeded      | 1.5.10 | MIT                              | daily logs                                          |
| Periodic Notes               | `periodic-notes`                    | seeded      | 0.0.17 | MIT                              | daily logs                                          |
| Homepage                     | `homepage`                          | seeded      | 4.5.0  | MIT                              | personal knowledge management                       |
| Outliner                     | `obsidian-outliner`                 | seeded      | 4.10.2 | MIT                              | long-form writing                                   |
| Callout Manager              | `callout-manager`                   | seeded      | 1.1.2  | MIT                              | long-form writing                                   |
| Iconize                      | `obsidian-icon-folder`              | seeded      | 2.14.7 | MIT                              | personal knowledge management                       |
| Footnote Shortcut            | `obsidian-footnotes`                | seeded      | 0.2.0  | MIT                              | long-form writing                                   |
| Better Word Count            | `better-word-count`                 | seeded      | 0.10.1 | MIT                              | long-form writing                                   |
| Novel word count             | `novel-word-count`                  | seeded      | 5.0.0  | MIT                              | long-form writing                                   |
| Hider                        | `obsidian-hider`                    | seeded      | 1.7.1  | MIT                              | personal knowledge management                       |
| Auto Note Mover              | `auto-note-mover`                   | seeded      | 1.2.0  | MIT                              | personal knowledge management                       |
| Tasks                        | `obsidian-tasks-plugin`             | seeded      | 8.4.0  | MIT                              | personal knowledge management, daily logs           |
| Citations                    | `obsidian-citation-plugin`          | seeded      | 0.4.5  | MIT                              | long-form writing, research                         |
| Zotero Cite Links            | `zotero-cite-links`                 | seeded      | 0.2.0  | MIT                              | research, long-form writing                         |
| Zotero Annotation Citations  | `zotero-annotation-to-pandoc`       | seeded      | 1.0.3  | MIT                              | research, long-form writing                         |
| Omnisearch                   | `omnisearch`                        | recommended | 1.31.0 | GPL-3.0                          | personal knowledge management                       |
| Advanced Tables              | `table-editor-obsidian`             | recommended | 0.23.2 | GPL-3.0                          | long-form writing                                   |
| Editing Toolbar              | `editing-toolbar`                   | recommended | 4.1.5  | MPL-2.0                          | long-form writing                                   |
| Focus Mode                   | `obsidian-focus-mode`               | recommended | 1.12.0 | MPL-2.0                          | long-form writing                                   |
| Kanban                       | `obsidian-kanban`                   | recommended | 2.0.51 | GPL-3.0                          | personal knowledge management                       |
| TaskNotes                    | `tasknotes`                         | recommended | 4.13.8 | MIT (bundles MPL-2.0 ical.js)    | personal knowledge management, daily logs           |
| Templater                    | `templater-obsidian`                | recommended | 2.25.1 | AGPL-3.0                         | long-form writing                                   |
| QuickAdd                     | `quickadd`                          | recommended | 2.30.0 | MIT                              | personal knowledge management                       |
| Pandoc Plugin                | `obsidian-pandoc`                   | recommended | 0.4.1  | MIT (embeds Obsidian CSS)        | analysis and reports, long-form writing             |
| Typewriter Scroll            | `cm-typewriter-scroll-obsidian`     | recommended | 0.2.2  | none at the pin                  | long-form writing                                   |
| Citation Suite               | `citation-suite`                    | recommended | 2.2.0  | AGPL-3.0                         | long-form writing, research                         |
| Better Pandoc Reference List | `better-pandoc-reference-list`      | recommended | 3.1.0  | GPL-3.0                          | long-form writing, research                         |
| Reference Map                | `reference-map`                     | recommended | 1.8.1  | GPL-3.0                          | research, personal knowledge management             |
| Simple Citations             | `simple-citations`                  | recommended | 1.10.0 | MIT                              | long-form writing, analysis and reports, research   |
| Zotero Lib View              | `zotero-lib-view`                   | recommended | 1.2.14 | MIT (grant in package.json only) | research, personal knowledge management             |
| Zotero Deep Linker           | `zotero-deep-linker`                | recommended | 0.2.0  | MIT (placeholder holder)         | research, personal knowledge management             |
| Git                          | `obsidian-git`                      | excluded    | —      | —                                | —                                                   |
| Longform                     | `longform`                          | excluded    | —      | —                                | —                                                   |
| Advanced URI                 | `obsidian-advanced-uri`             | excluded    | —      | —                                | —                                                   |
| Tag Wrangler                 | `tag-wrangler`                      | excluded    | —      | —                                | —                                                   |
| Note Refactor                | `note-refactor-obsidian`            | excluded    | —      | —                                | —                                                   |
| Excalidraw                   | `obsidian-excalidraw-plugin`        | excluded    | —      | —                                | —                                                   |
| Quadro                       | `quadro`                            | excluded    | —      | —                                | —                                                   |
| Local REST API               | `obsidian-local-rest-api`           | excluded    | —      | —                                | —                                                   |
| Claudian                     | `realclaudian`                      | excluded    | —      | —                                | —                                                   |
| Copilot                      | `copilot`                           | excluded    | —      | —                                | —                                                   |
| Agent Client                 | `agent-client`                      | excluded    | —      | —                                | —                                                   |
| Remotely Save                | `remotely-save`                     | excluded    | —      | —                                | —                                                   |
| Importer                     | `obsidian-importer`                 | excluded    | —      | —                                | —                                                   |
| Enhancing Export             | `obsidian-enhancing-export`         | excluded    | —      | —                                | —                                                   |
| ZotLit                       | `zotlit`                            | excluded    | —      | —                                | —                                                   |
| Zotero Integration           | `obsidian-zotero-desktop-connector` | excluded    | —      | —                                | —                                                   |
| Citation Extended            | `citation-extended`                 | excluded    | —      | —                                | —                                                   |
| Citation Links               | `citation-links`                    | excluded    | —      | —                                | —                                                   |
| Deep Sit                     | `deep-sit`                          | excluded    | —      | —                                | —                                                   |

### Declared plugin settings

| Plugin                      | File                | Key                                      | Accepted                     |
| --------------------------- | ------------------- | ---------------------------------------- | ---------------------------- |
| Core                        | `core-plugins.json` | `sync`                                   | `false`                      |
| Core                        | `core-plugins.json` | `publish`                                | `false`                      |
| Core                        | `core-plugins.json` | `canvas`                                 | `false`                      |
| Core                        | `core-plugins.json` | `properties`                             | `false`                      |
| Core                        | `core-plugins.json` | `markdown-importer`                      | `false`                      |
| Core                        | `app.json`          | `useMarkdownLinks`                       | `true`                       |
| Core                        | `app.json`          | `newLinkFormat`                          | `"absolute"`                 |
| Core                        | `app.json`          | `newFileLocation`                        | `"folder"`                   |
| Core                        | `app.json`          | `newFileFolderPath`                      | `"inbox"`                    |
| Core                        | `app.json`          | `attachmentFolderPath`                   | `"inbox"`                    |
| Core                        | `daily-notes.json`  | `folder`                                 | `"daily"`                    |
| Core                        | `zk-prefixer.json`  | `folder`                                 | `"inbox"`                    |
| Dataview                    | `data.json`         | `enableDataviewJs`                       | `false`, `unset`             |
| Dataview                    | `data.json`         | `enableInlineDataviewJs`                 | `false`, `unset`             |
| Iconize                     | `data.json`         | `iconPacksPath`                          | `".obsidian/icons"`          |
| Footnote Shortcut           | `data.json`         | `lintOnSave`                             | `false`                      |
| Novel word count            | `data.json`         | `writeCountsToFile`                      | `false`, `unset`             |
| Better Word Count           | `data.json`         | `collectStats`                           | `false`, `unset`             |
| Auto Note Mover             | `data.json`         | `use_regex_to_check_for_excluded_folder` | `true`                       |
| Homepage                    | `data.json`         | `homepages.Main Homepage.autoCreate`     | `false`                      |
| Citations                   | `data.json`         | `citationExportPath`                     | `"system/bibliography.json"` |
| Citations                   | `data.json`         | `literatureNoteFolder`                   | `"Reading notes"`            |
| Zotero Annotation Citations | `data.json`         | `source`                                 | `"betterbibtex"`, `unset`    |
| Omnisearch                  | `data.json`         | `httpApiEnabled`                         | `false`, `unset`             |
| Editing Toolbar             | `data.json`         | `ai.enabled`                             | `false`                      |
| Kanban                      | `data.json`         | `new-note-folder`                        | `"inbox"`                    |
| TaskNotes                   | `data.json`         | `enableAPI`                              | `false`                      |
| TaskNotes                   | `data.json`         | `enableMCP`                              | `false`                      |
| TaskNotes                   | `data.json`         | `tasksFolder`                            | `"TaskNotes/Tasks"`          |
| Templater                   | `data.json`         | `templates_folder`                       | `"system/templates"`         |
| Templater                   | `data.json`         | `startup_templates`                      | `[]`                         |
| QuickAdd                    | `data.json`         | `disableOnlineFeatures`                  | `true`                       |
| QuickAdd                    | `data.json`         | `enableUriCallbacks`                     | `false`                      |
| Reference Map               | `data.json`         | `pullFromZotero`                         | `false`                      |
| Reference Map               | `data.json`         | `searchCiteKeyPath`                      | `"system/bibliography.json"` |
| Simple Citations            | `data.json`         | `autoAddCitations`                       | `false`, `unset`             |
| Simple Citations            | `data.json`         | `autoSyncCitations`                      | `false`, `unset`             |
| Zotero Lib View             | `data.json`         | `autoImportOnBibChange`                  | `false`, `unset`             |
| Zotero Lib View             | `data.json`         | `exportPath`                             | `"zotero-lib-view"`          |

## Development

One command runs every form and lint owner, locally and in CI:

```bash
source .venv/bin/activate && pre-commit run --all-files
```

Each file type has exactly one form owner (`.pre-commit-config.yaml` is the matrix): ruff for Python, mdformat for CommonMark Markdown, yamlfix for YAML, pyproject-fmt for TOML, stdlib `json.tool` canonical form for JSON manifests (asserted in `tests/test_config_validity.py`), and — for vault-dialect Markdown, which no off-the-shelf formatter speaks — the sole writer, verified by `tests/test_canonical_form.py`.
