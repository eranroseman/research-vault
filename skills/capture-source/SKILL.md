---
name: capture-source
description: Use when a person asks to capture, refresh, add, or compile a source in a research-vault vault, or to propagate a citation-key change
disable-model-invocation: true
---

# Capture a source

Ingest is the process that gets a source from outside the vault into the vault: **selection** (the person's decision), **add** (the Zotero item), **capture** (the deterministic copy into the vault), **compile** (the adopted tool's pages). This skill runs the mechanical steps; the decision is never yours. If the person has not decided, stop and ask; nothing in `inbox/` is citable, and no amount of capturing changes that.

**No project is required.** The flow is continuous and project-independent, so every step below runs on a vault with zero projects; only `find-sources` is project-scoped.

In every command, `PATH` is the vault and `KEY` is either the Zotero item key (eight upper-case characters, shown in Zotero's item pane) or the citation key — Zotero's own **Citation Key** field, which Better BibTeX fills and which shows in the item list's Citation Key column. Never invent or guess one. Every mechanical act below is a CLI verb call: you compose and explain, the CLI writes. `literatures/`, `fulltext/`, `system/bibliography.json`, `system/propagations/` and `wiki/` are machine surfaces; never `Write` or `Edit` them.

## 1. Add: `add`

When the item is not in Zotero yet and the person has asked you to add it, write a Zotero item JSON file — `itemType` plus any of the snapshot fields (`title`, `creators`, `date`, `DOI`, `url`, `publicationTitle`, `volume`, `issue`, `pages`, `publisher`, `ISBN`, `language`, `abstractNote`, `extra`, `accessDate`, `tags`) — and run:

```sh
python3 -m research_vault add --vault PATH --item ITEM.json [--collection COLLECTION_KEY]
```

The first run on a machine opens Zotero's own consent dialog (**Allow**, **Always Allow**, **Deny**); tell the person to answer it in Zotero. Never retry `add` in a loop: the dialog is rate-limited to five a minute. Better BibTeX fills the citation key a few seconds after creation; `add` waits up to ten seconds and then captures the new item. `unkeyed` means the key never arrived: report it, do not write a note by hand.

## 2. Capture: `capture`

```sh
python3 -m research_vault capture KEY [KEY ...] --vault PATH
python3 -m research_vault capture --all --vault PATH      # refresh every captured note
```

Capture runs the lifecycle linter first, then for each item reads the item, its children and the indexed text, writes `literatures/<citation key>.md` (frontmatter: Zotero's own fields verbatim, the provenance tuple, a body carrying only the attachment list and the item's Zotero child notes), writes `fulltext/<attachment key>.md` for every attachment with usable text, and regenerates `system/bibliography.json` whole. One line per outcome:

| Line                                                    | What happened                                                                                                                                                                                                                                                |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `MATCHED KEY — matched`                                 | The note was written or rewritten.                                                                                                                                                                                                                           |
| `MATCHED KEY — matched — NOOP`                          | The projection is identical. Nothing was written. Report it as "already current", never as an error and never as a capture you performed.                                                                                                                    |
| `UNMATCHED KEY — not-admitted — …`                      | The key is not in the library.                                                                                                                                                                                                                               |
| `UNMATCHED KEY — no-fulltext — …`                       | The note was written, but no attachment has usable text (absent, partial past Zotero's page cap, or below the content floor), so there is no compile input. Read the reason back verbatim.                                                                   |
| `SKIPPED KEY — no-fulltext — no attachment to read (…)` | The item holds no file at all — a web page, a repository, a program. The note was written; the text checks do not apply, and nothing was filed. Getting text for such sources is a later lane's work, not a capture failure.                                 |
| `UNMATCHED KEY — re-keyed — old → new; run propagate`   | The citation key changed. Capture refuses while `literatures/old.md` still exists, because writing `new.md` beside it would dead-end `propagate`; run `propagate` (§4), whose own recapture proceeds because the rename has already moved the old note away. |
| `UNMATCHED KEY — merged\|trashed\|deleted — …`          | The item left the library. Nothing was written; the note is kept.                                                                                                                                                                                            |
| `UNMATCHED vault — database-changed — …`                | A different Zotero database answered. Nothing was written. Stop and tell the person which server id the notes record.                                                                                                                                        |
| `UNREACHABLE … — outage — …`                            | Zotero did not answer. **Never a verdict on the source.** Retry later.                                                                                                                                                                                       |

Every UNMATCHED and UNREACHABLE line already filed its own review record under check id `capture`; a SKIPPED line is never filed (the fourth state is automatic-only, never a finding). Never file one for a failed capture yourself. If stderr carries `warning: review record refused:`, say so out loud.

## 3. Verify what capture cannot see

Run `python3 -m research_vault verify --vault PATH` with the network on after a capture: it runs the lifecycle linter over every note (check id `lifecycle`), the captured-set lint at the compile seam (`captured-set`) and the update-notice check. Route reading of that run to `verify-citations`.

## 4. Propagate a citation-key change: `propagate`

A `re-keyed` finding means the source's *name* changed while its identity (the item key) did not. Until propagation runs, the note's filename contradicts its recorded key and every `[@old]` and `[[old]]` dangles. Propagation is the one command here that rewrites what a person wrote, so it is planned, shown, and applied only against the plan you showed:

```sh
python3 -m research_vault propagate --vault PATH                    # plan: every re-keyed note the linter reports
python3 -m research_vault propagate --vault PATH --map OLD=NEW      # plan from an explicit mapping, e.g. after a deliberate regenerate
python3 -m research_vault propagate --vault PATH --plan FILE --approved-plan-sha256 SHA   # apply, exactly as printed
```

The plan lists the rename, the item key and every file it will rewrite, and ends with the apply line carrying the plan's hash; show it to the person and run that line unchanged. If anything the plan named moved in between, apply refuses with `mismatch — plan changed`: plan again. Apply renames the note, rewrites `[@key]` and `[[key]]` in drafts and wiki pages, re-captures the item, and keeps the applied plan under `system/propagations/` — the record a reader follows an old key forward through. The review queue is never rewritten; acknowledgments on the renamed note lapse by scope, as they do for any content change. The `propagation` check fails a commit while any surface still names a key an applied plan mapped away.

## 5. Compile: `compile`

Compile is the adopted tool's job (claude-obsidian; see `setup-vault`). The wrapper registers the captured sources in the tool's ledger and never writes under `wiki/`:

```sh
python3 -m research_vault compile KEY [KEY ...] --vault PATH        # prints the tool's plan and approval hash
python3 -m research_vault compile --all --vault PATH                # the whole captured set; a note without text is a SKIPPED row
python3 -m research_vault compile --vault PATH --bundle BUNDLE --approved-plan-sha256 SHA
```

Show the person the plan before applying; the approval hash is the tool's own human gate, and there is no second one. Then run the tool's wiki-ingest skill on the registered `fulltext/<attachment key>.md` files; the pages it writes cite the literature note as `[[<citation key>]]`. Then run `capture KEY` again (or `capture --all`): the note now embeds the compiled page, `![[<page path>]]`, from the ledger's `pages[]`. Until that second capture the embed is absent — expected, not an error. A note whose text changed after compile is reported `recompile-needed` by `verify`.

## Four-state honesty

| Result      | Meaning at capture                                                                                                     |
| ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| MATCHED     | The step ran and agreed. Only the CLI's deterministic checks mint a `verified` event; nothing in this skill ever does. |
| UNMATCHED   | The step ran and disagreed. Already in the review queue — do not file it again.                                        |
| UNREACHABLE | The step could not run — Zotero or the network is down. Never a verdict on the source. Retry later.                    |
| SKIPPED     | The step does not apply. Automatic only.                                                                               |

The same honesty covers your own reading. A source you read only in part is reported **partial**, with the range you did not read named — pages the text layer stops at, sections you never reached. That is SKIPPED applied to reading: an unread stretch must never read as read.

## Routing

| Need                                       | Route to                                     |
| ------------------------------------------ | -------------------------------------------- |
| Find sources to add                        | `find-sources`                               |
| Rules for the compiled layer               | `synthesis-conventions`                      |
| Run the deterministic checks               | `verify-citations`                           |
| Acknowledge a finding capture filed        | `project-flow` or `publish` (the `ack` verb) |
| Install Zotero add-ons or the compile tool | `setup-vault`                                |
