# Section 1 research: the comparisons behind the Zotero add-on table — working record

- **Date:** 2026-10-04 to 2026-10-06
- **Method:** read-only comparison runs over screen A's evidence, the add-ons' code at their pins, production Zotero 10.0.5 (local API, read-only) and the test instance; each answer was re-checked by an adversarial checker, whose corrected version is printed here ([corrected], [added]). Two operator-facing measurements follow: Obsidian's trust prompt and the daily-notes folder convention.
- **Spec:** 2026-10-03-substrate-components-design.md
- **Binds:** nothing — evidence the spec's §3 and §4 rest on; the spec carries the verdicts. Paths under `/tmp/` are session-local raw logs, not retained.

## DOI repair: DOI Fix and DOI Manager 2.2.0

`ev` = ~/research-vault/.worktrees/lanes-2-3-spec/docs/superpowers/specs/2026-10-03-substrate-components-design-zotero-screen-evidence.md. Code cites are to the pinned xpis. updates.json files read 2026-10-04.

**DOI Fix 1.1.6** (`doi-fix@zotero.org`, MIT)

- By itself: nothing. No notifier, timer or preference (ev:493).
- On command, selected items only. Retrieve fills empty DOIs (doiManager.js:96-108). Update checks a DOI with a Crossref /works lookup plus a 0.86 title match, so valid DataCite DOIs fail. A failed DOI is replaced if Crossref offers a candidate, and a single OpenURL hit is taken with no title check. Otherwise the item is only tagged [corrected] (:202-241, 262-266; ev:492).
- Writes: the DOI field. Before a replacement it adds the Extra line `DOI Fix previous DOI: <old>` (:721-736). It has four `doi-fix:` tags, leaves at most one per item and removes only its own [corrected] (:684-713).
- Installed and active on 10.0.5, range up to 10.\* (ev:484). 1.1.9 fixes a Zotero-10 menu-label bug. Production auto-update is off [corrected] (ev:483, 1781-1783).

**DOI Manager 2.2.0** (MPL-2.0)

- By itself, on every add from any writer including sync, in mode `long`: fills empty DOIs from one Crossref hit, lower-cases DOIs and expands shortDOIs (ev:477).
- By itself, a silent monthly check of the personal library's top-level items; group libraries are not swept [corrected] (zoteroshortdoi.js:105). The first run is at the first startup and was seen live.
- Turning it off needs autoretrieve=none and monthly_verify=false (prefs.js:1-2).
- Validates against doi.org handles, so DataCite DOIs pass [added] (doi-service.js:5-9).
- Writes: the DOI field, three status tags, link attachments. No Extra (doi-updater.js:162-300).
- Not installed. Passed the live load check (ev:478). Manifest and updates.json both cap at 10.0.\*, which Zotero cannot lift, so Zotero 10.1 would disable it (ev:1786). It shares 1.6.0's id, so installing it replaces 1.6.0 (ev:470).

**Linter 3.3.2, installed and active** [added]

- On add, for journalArticle and conferencePaper: fills empty DOIs from one Crossref OpenURL hit and expands shortDOIs. All on by default (Linter prefs.js:2, 39, 62; linter.js:6339-6362, 9216-9260; ev:507).
- Its A3 pass needs lint.onAdded=false, which also stops this (ev:517). If DOI Manager is added too, only Linter's priority orders the two (ev:1800-1801).

**Vault side**

- Capture snapshots DOI and Extra (literature_notes.py:34-52). Lower-casing changes the snapshot (ev:460). The vault's DOI comparisons ignore case (checks.py:276).
- Any write moves the item version, and lifecycle reports that as drift [added] (lifecycle.py:95-107). DOI Manager's sweep reaches captured items across the library; DOI Fix touches only the selection.
- A note whose snapshot has no DOI or PMID, and no quote claims, stays unverified [added] (events.py:256-262, 304-310). verify's DOI lookup stays in memory (verify.py:782-787).
- The PMCID fetcher (auto on) runs on add and modify, keyed on the DOI, so a save by either add-on triggers it again (lib.js:152-163, 226-246). It does not read DOI Fix's Extra line (lib.js:235), but a fetch in progress can overwrite that line (ev:436, not tested live).

**The README row today**

- README.md:125 and templates/zotero-addons.md:5 (the copy doctor reads) declare `zoteroshortdoi@wiernik.org` as recommended, with `autoretrieve` (ev:1806). The installed 1.6.0 is appDisabled and cannot update itself. Its update URL answers 200 but lists only 1.5.1 (ev:446-449).
- Doctor checks the preference only when the add-on is active; appDisabled is a note (doctor.py:262-280). With 2.2.0 active the row fails at every value: an unset preference reads as absent, and a set one is a string [corrected] (doctor.py:278; addons.py:72-89). A row holds one preference (addons.py:9-14). Doctor cannot tell apart the builds that share this id (ev:1807-1809).
- No skill names either add-on [added].

## Duplicate handling and metadata quality

§ = screen A evidence. Native = Zotero 10.0.5 omni.ja; installed = production extensions.json; read 2026-10-04.

DUPLICATE HANDLING

Native: detection lives only in the Duplicate Items view (collectionTree.js:3309-3314). It matches book ISBN, DOI, or normalised title plus a shared creator (or neither has any) and no year gap over one (duplicates.js:194-401) [corrected]. The merge pane takes one same-type group, preselects the oldest, merges fields the person picks (duplicatesMergePane.js:79-161, 203-211). Every merge leaves dc:replaces (read by lifecycle.py:33-83), never the loser's citekey (§2a).

- Zoplicate (capture, §3 r2; installed, active). By itself, on add, extensions.zotero.zoplicate.duplicate.default.action decides: keep or discard merges unprompted, the new or an old item surviving (duplicates.ts:431-439); ask (shipped) prompts; cancel (production) does nothing. An always-on, unconfinable \_saveData patch moves another writer's new child of a trashed item to the master, passing A3 only on an open reading (§2a). Beyond native: on-add and bulk merge, non-duplicate marks; same detection and mergeItems.mjs. A4 needs-live. Its 10.0.\* cap would appDisable it on 10.1 (§7 item 5). Not in README.
- Duplicate Cleaner (capture, protective, §3 r46; A2 by protection is open, §7 item 4). By itself nothing: every merge, blank-field fill (citationKey included) and trash follows one confirm (§4 r46). Groups by item type plus DOI, else plus exact title (bootstrap.js:286-290) [corrected]; distinct same-title works can merge. Its Items.merge, a shim over mergeItems.mjs, is the only path BBT patches, inert unless extraMergeCitekeys is set (§2a). Installed on neither production nor the restored test instance (§7 item 34) [corrected].

METADATA QUALITY

Native: Retrieve Metadata takes only top-level PDF or EPUB attachments (recognizeDocument.js:133-138), automatically while autoRecognizeFiles is on (shipped true, defaults/preferences/zotero.js:1617). No native refresh of an existing item (grep). PMCID arrives only via translators, as a field (PubMed XML.js:259-272) or an Extra line the connector moves in (§7 item 25) [corrected]; Find Available PDF uses it (attachments.js:1284-1332).

- Linter (capture, §3 r9; installed, active): fills DOI from Crossref, expands short DOIs. By itself, a priority-666 notifier lints each new item: no-field-misuse blanks other writers' archive, callNumber, shortTitle and series values, and it reports native-detected duplicates (linter.js:8973-9006). extensions.zotero.formatmetadata.lint.onAdded=false stops all of it; shipped and production true; not in README (§4 r9).
- PMCID fetcher, another job: PMID, PMCID, MeSH tags (capture, §3 r5; installed, active). For journalArticle it writes native PMID and PMCID, which SNAPSHOT_FIELDS omits (literature_notes.py:34-52); events.py:258-261 reads lowercase pmid or a PMID: Extra line, missing the field [corrected]. By itself, on add and modify, it rewrites Extra from a stale snapshot and re-adds MeSH tags. extensions.zotero.pmcid.auto=false confines it; unset (off) in the asset, true on production (§4 r5). README declares that key; doctor demands exactly True (doctor.py:275-280); no confining value here is (§2a).

Only Linter's priority orders on-add writers (§7 item 9).

## Attachment Scanner and capture

EV as before. Bare line numbers are attachmentscanner.js v0.5.1.

**The conflict**
While `monitor_attachments` is on, every item modify is checked at its parent item (354-371). Production sets it, `remove_snapshot` and `remove_pubmed_entry` true (prefs.js:29-31); all three ship false (xpi prefs.js:5-8). It trashes a snapshot whose PDF/EPUB sibling is on disk, and any "PubMed entry" link (411-462). A note listing that child is classed trashed (lifecycle.py:88-91). Capture refuses it until the child is restored or purged (capture.py:48, 410-411; EV row 26 ¤).

**1. Declare the prefs off**

- Setting both false stops both trash paths, and tagging continues (EV row 26 ¤). [added] The prefs are read only at startup or when the prefs pane loses focus (128-138, 280). [added] Production also has `scan_nonfiles=true` (prefs.js:32), so a kept PubMed entry gets its parent tagged `#nonfile` (449-451, 475-477).
- The A3 pass assumes `monitor_attachments=false`, which ends automatic tagging. With monitoring on, the scanner strips same-named tags set by any writer unless its tag strings are unique (EV row 26 §). [added] Changing those strings renames the existing tags across the library (132-160).
- Doctor holds one pref per row, tests `is not True`, and reads prefs.js only, so a shipped false shows as a missing key (addons.py:9-14, 72-90; doctor.py:275-280). [corrected] Declaring `remove_snapshot` today would pass production's true and fail the wanted false.

**2. Change lifecycle**

- [corrected] Spec §3.4 step 4 classes a note as trashed (it does not trash it) when any tuple key is in the trash (import-redesign-design.md:195; tests/test_lifecycle.py:117-135). This is research-vault's own choice (EV 1926).
- An exemption for children capture reads no text from misses snapshots, because capture reads snapshot text (capture.py:84-106; Zotero fulltext.js:491-499 @ ca61760). [added] The tuple records no linkMode (capture.py:127-135).
- If the rule is narrowed, the note reads drifted (lifecycle.py:98-107; EV row 26 ¤). Capture proceeds ([corrected] capture.py:48, 407-413) and drops the child (zotero.py:273-275).
- [corrected] Cost: a spec and test change. A child trashed by mistake drops out while capture reports "matched"; verify reports only `drift — attachment KEY absent` (lifecycle.py:234-239).

**3. Drop the scanner**

- Nothing in research_vault reads `#nosource` or `#broken`. Capture copies tags (literature_notes.py:51) and itself reports no-fulltext, no-index, partial and empty (capture.py:236-257; fulltext.py:25-54). `#broken` (unresolvable file, 411-423) has no counterpart. The screen credits the scanner with protecting capture (EV row 26).
- [added] Its `#nosource` tag stays on 175 items and is captured (EV 1834-1835).
- It is "recommended", so dropping the row loses a doctor note, not a gate (doctor.py:273).
- Disabling stops new trashing but does not clear existing refusals (EV row 26 ¤). [added] No other live candidate exists for this job (EV 101-102).

**The 19 snapshots**

- 15 were trashed on their own, 14 sit under live parents with a live PDF/EPUB, and 4 are trashed only through their parent. The trash also holds 8 PubMed entries. [corrected] Which writer trashed them is unproven (EV 866).
- [corrected] No captured note was found under ~ (EV row 26 ¤). A first capture leaves trashed children out.
- [corrected] Under production prefs, a restored child is trashed again at once. Saving it queues a modify (zoteroPane.js:2891-2900; item.js:1677-1679 @ ca61760), which the notifier lifts to the parent (368-371, 454-462).
- If not restored, Zotero's 30-day default purges them (defaults/preferences/zotero.js:51 @ ca61760); production does not override it.

## OCR candidates (first comparison)

E = ~/research-vault/.worktrees/lanes-2-3-spec/docs/superpowers/specs/2026-10-03-substrate-components-design-zotero-screen-evidence.md; code b06e212; omni = Zotero 10.0.5 Windows omni.ja; m. = read-only measurement, 2026-10-04.

**Why the job exists:** a scanned PDF indexes as masthead text only, so capture reports `no-fulltext` (fulltext.py:50-53; capture.py:248-255) and compile skips it (compile.py:110-111) [corrected]. Production had 3 scanned PDFs (import-redesign-design.md:584, 2026-09-05). E §6.3's OCR capture legs never ran (E §6.4).

**Zotero OCR** (E row 30)

- Needs tesseract and pdftoppm, the latter set by hand on Windows (zotero-ocr.js:211-219). Neither is on Windows PATH or in WSL (m.). Tesseract language pref, default eng (371-378).
- Stores a "<title>.ocr" PDF copy, indexed to pdfMaxPages (default 100, omni defaults/preferences/zotero.js:1695); longer copies read `partial`. Also an OCR note (enters the literature note) and up to 5 page-HTMLs (each a fulltext/ file); outputNote and outputHocr, default on, stop those.
- Context menu only; AGPL-3.0. Production: user-disabled, loadable; max 10.\*.

**RapidOCR** (E row 32)

- No external program; 68.7 MB unpacked, 15.6 MB models [corrected]. One Chinese PP-OCRv4 model, no language pref; its character list lacks ß, ñ, ö, ç, Hebrew (m.).
- Appends " [OCR]" to the copy's title [corrected]; indexes it with no page limit (asset pdf-ocr-for-zotero.js:154283; omni fulltext.js:719).
- On command; no notifier (m.). MPL-2.0 claimed, no LICENSE. 37 commits since 2026-09-04. Loads on 10.0.5; max 10.0.\*, also in its update.json (m.), so E §7 item 6's bypass does not apply: 10.1 disables it [corrected].

**zotero-docling** (E row 33)

- OCR runs in a docling-serve the user hosts (default localhost:5001). Nothing answers there from WSL or Windows (m.) [corrected].
- Stores a .md, indexed as text; past 500,000 characters it reads `partial` (omni defaults/preferences/zotero.js:1694) [corrected]. By default the .md opens with YAML metadata (zoteroDocling.js:6161-6186).
- On command; autoConvert (default off) converts every new PDF. AGPL-3.0. Last commit 2026-06-19. Loads on 10.0.5; no max.

**Capture and lifecycle**

- Zotero's best attachment is the oldest PDF, the scan (omni item.js:4329-4334); it fails the floor, so the first usable child in /children order becomes compile input (capture.py:138-143). Zotero OCR's copy and page-HTMLs compete; past 100 pages only page-HTMLs qualify. Untested.
- OCR after capture goes unseen: lifecycle compares only tuple keys (lifecycle.py:88-105) [corrected]; children don't move their parent's version (import-redesign-design.md:575). Parent writes show as drift: docling's tags (6451-6480), or Attachment Scanner's duplicate tag from a second PDF or several HTML pages (E §7 item 15).
- Re-capture adds the key (capture.py:177-181) and sets compile-input-sha256: a new compile source (compile.py:110-137). Trashing the scan makes the note `trashed`, which capture refuses (lifecycle.py:88-91).
- Doctor checks add-on state and fails an active add-on whose declared automatic-mode pref is not true (doctor.py:262-280): declaring docling's autoConvert forces it on. Nothing checks programs or services.

## Zotero fields research-vault depends on

Facts at HEAD b06e212; counts from read-only GETs on 2026-10-04: production 1574 regular items, test 1455. "evidence.md" is docs/superpowers/specs/2026-10-03-substrate-components-design-zotero-screen-evidence.md.

Capture copies SNAPSHOT_FIELDS into the literature note (literature_notes.py:34-52, 327-335). verify takes identifiers (checks.py:291-297) from system/bibliography.json, Better BibTeX's CSL export (zotero.py:339-346, 502-509). The trust tier reads the note. [added] Every capture rewrites bibliography.json for all captured items from the live library (capture.py:274, 305); a note, only when its item is captured. So a background change to a DOI or Extra reaches verify first, and note and CSL can disagree.

| Field                                                                                                  | Read by                                                                                                                                     | If missing, wrong or stale                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| citationKey                                                                                            | note path (literature_notes.py:147); re-key check (lifecycle.py:92-93); CSL id (checks.py:176-184)                                          | Missing: no note, `unkeyed` (capture.py:386-391, 522 [corrected]). Changed: capture refuses until propagate runs (capture.py:394-421); old-key citations read UNMATCHED. Production: 0 unkeyed.                                                                                                                                                                                                                                         |
| item/attachment version, md5                                                                           | lifecycle.py:96-104, 125                                                                                                                    | Any writer's write reads "drifted"; the next capture rewrites the note.                                                                                                                                                                                                                                                                                                                                                                 |
| dc:replaces                                                                                            | lifecycle.py:58-65                                                                                                                          | A merge reads as deleted or trashed.                                                                                                                                                                                                                                                                                                                                                                                                    |
| DOI                                                                                                    | trust tier (events.py:257); retraction check (checks.py:685-771)                                                                            | Missing: with network on, a title search runs first and any DOI found is checked; else the check skips (verify.py:782-787) [corrected]. Wrong: another paper's notices. 236 production items lack one, 112 of them software [added].                                                                                                                                                                                                    |
| PMID                                                                                                   | trust tier: lowercase `pmid` or Extra `PMID:` only (events.py:258-261); CSL `PMID`: Retraction Watch only (checks.py:296, 693-699)          | Replayed in memory: native PMID, no DOI, matched quote, failed retraction check gives "machine-confirmed"; PMID in Extra gives "unverified". 3 production items. [added] With no DOI, a single PubMed title hit replaces the CSL PMID in memory (verify.py:787).                                                                                                                                                                        |
| title, creators, date                                                                                  | aliases, wikilinks (literature_notes.py:488-492; captured.py:84-91); compile (compile.py:128); identifier search (identify.py:28-80)        | Crossref needs an exact title match; PubMed takes one hit unchecked (identify.py:100-105). Found identifiers are never written back.                                                                                                                                                                                                                                                                                                    |
| CSL `version`                                                                                          | DataCite/arXiv version check (checks.py:535-536, 618-623)                                                                                   | [corrected] Comes from native versionNumber (absent from preprint in schema 44; no arXiv item has one) or an Extra `Version Number:` line. Of 144 arXiv DOIs, 131 have none: SKIPPED. 13 carry a bare digit ("2"), failing the `v[1-9]\d*` test: UNREACHABLE, which, unacknowledged, makes publish wait (verify.py:938-942). None can match as the library stands. arXiv's withdrawal flag is read only past this gate (checks.py:664). |
| extra                                                                                                  | trust-tier PMID route; [corrected] Better BibTeX also lifts Extra lines into CSL `PMID`, `PMCID`, `version` (CSL 383/253 vs native 370/241) | The Connector moves `PMID:` lines into the native field (evidence.md:1877), emptying the trust-tier route.                                                                                                                                                                                                                                                                                                                              |
| abstractNote, tags, url, volume, issue, pages, publisher, ISBN, language, accessDate, publicationTitle | nothing                                                                                                                                     | Display only.                                                                                                                                                                                                                                                                                                                                                                                                                           |

[added] 65 arXiv preprints carry a published version's DOI: the retraction check reads that version's record; no arXiv check runs.

Skills: publish counts `retracted` findings (skills/publish/SKILL.md:25); project-flow reads bibliography.json and the trust tier (skills/project-flow/SKILL.md:29-37, 52); verify-citations wraps `verify`; paper-critical-analysis takes metadata from the paper (SKILL.md:39-52); find-sources precedes Zotero; factcheck.py reads no Zotero field.

Fields Zotero 10 fills that capture omits (production):

- **PMID 370, PMCID 241:** in the CSL file (pierre.etal2025: PMID 41635747, PMCID PMC12863933), not the note; nothing reads PMCID (evidence.md:1789-1792).
- **Venue** in a type-specific field for 421 items \[corrected\]: proceedingsTitle 342, bookTitle 57, websiteTitle 19, blogTitle 3; CSL container-title carries all.
- **Publisher** likewise for 273: repository 212, company 59, other 2; CSL publisher carries all.
- **Other:** archiveID 199, conferenceName 302, place 362, ISSN 658, journalAbbreviation 678, shortTitle 839, series 61, edition 30, versionNumber 2.
- **`add`** accepts only snapshot fields plus `collections` (capture.py:582-595) [corrected].

## Registry refresh: ZotMeta, Meta Refresh, Metadata Hunter

Per-must results, not verdicts (E:6, 8): ZotMeta and Meta Refresh pass every must; Metadata Hunter all but A4, still needs-live (E:219-221). [added] Linter and DOI Manager 2.2.0 pass too, but their A3 passes rest on settings doctor cannot assert: lint.onAdded=false (production has true); autoretrieve=none plus monthly_verify=false (E:216, 218, 191, 193, 477, 517).

**Effects on research-vault**

- Any save bumps the item version; lifecycle reports `drifted` until re-capture (lifecycle.py:96-97).
- The snapshot's 17 fields include extra, creators and tags (literature_notes.py:34-52). [corrected] Writes to journalAbbreviation, proceedingsTitle, conferenceName, place, numPages, repository, archiveID, ISSN or series reach BBT's export, not the note.
- [corrected] Existing keys hold while resetKeyOnChange stays false, as shipped (E:332); Metadata Hunter's swap aside.
- The first three act only on the person's command (E:533, 555, 572).
- A1: all five load on 10.0.5 (E:498, 1661-1664); the 10.0.\* caps of ZotMeta, Metadata Hunter and DOI Manager would disable them on 10.1 unless an update entry lifts them (E:446, 604, 1784, 1786; inferred).
- Native Zotero has no refresh for existing items (zoteroPane.js:4158-4186).

**ZotMeta 2.1** (MIT)

- Identifier lookups only (journal.js:73-133; book.js:103-127; arxiv.js:137-187), [added] for journal articles, books and arXiv preprints (zotmeta.js:141-152).
- Overwrites every mapped field returned and all creators, editors included; no backup, no preview (utilities.js:420-435).
- [corrected] An arXiv entry replaces an existing DOI only without journal_ref; with one, the update throws first (arxiv.js:248-258; Zotero item.js:811-820).
- [corrected] From a PDF it fills empty DOI, archiveID, repository and url (utilities.js:597-612).

**Meta Refresh 0.5.0** (AGPL-3.0)

- Four registries: by DOI, then arXiv ID, then title similarity ≥0.85 (metarefresh.js:2187-2262).
- Overwrites title, venue, date, volume, issue, pages, DOI, abstract and authors (editors kept; skipped below 0.34 surname overlap); fillEmptyOnly=true (ships false) fills empties only (:2292, 2310-2361). Never changes type.
- Default backup: one Extra line `[MetaRefresh <time>] {old}`, read by Restore, copied by capture (:2363-2377).
- Applies after a preview with per-item exclusion (:2848-2884). [added] upgradePreprints (ships true) can give a preprint its published DOI, type unchanged (:1958-1978, 2209-2216, 2454-2470).

**Metadata Hunter 0.8.0** (EUPL-1.2)

- Finds missing DOIs by title across four registries (index.js:587-597, 813-838).
- Fetches records via a scratch library item, then erases it; [added] effects on BBT keys and other add-ons' on-add handlers are untested (:1641-1672; E:1718).
- Fills empty fields; overwrites a year-only date, a short abstract, an arXiv DOI and the item type (dropping invalid fields); replaces creators by a size rule (:1674-1728, 1753-1758; E:532).
- No backup or preview; [corrected] with nothing selected it takes the selected collection, else the whole library, unconfirmed (E:533).
- Find Published Version trashes the original for a new item and key; [added] tags, Extra and relations stay behind. Lifecycle reads `trashed` (E:531; lifecycle.py:80-85).

**DOI Manager 2.2.0** (MPL-2.0; not installed; replaces production's non-loading 1.6.0, E:470)

- [corrected] By itself, on every added item (synced too) and a monthly sweep from first startup, it fills empty DOIs from Crossref, lower-cases or expands others, and writes three status tags and link attachments (E:465, 471-478).

**Linter 3.3.2** (AGPL-3.0-or-later; active on production)

- [corrected] On add, after other plugins (priority 666), its enabled rules blank pattern-matched shortTitle, archive, callNumber, rights, catalog or series values, reorder Extra and fill empty DOIs (linter.js:8914-8966, 9216-9260, 11948-11975; E:509-517).
- Menu-only update tool: shipped mode "all" overwrites returned fields, Extra and all creators unbacked (:10924-11072; E:513).

E = ~/research-vault/.worktrees/lanes-2-3-spec/docs/superpowers/specs/2026-10-03-substrate-components-design-zotero-screen-evidence.md. Add-on code is from /tmp/vA/{zm,mr,mh,linter,regl}; all sha256 match the pins in E. Zotero code is from the production omni.ja of 10.0.5, read on 2026-10-04.

## Linter for Zotero, rule by rule

Source: installed add-on (sha256 1c169881…) at /tmp/linter332/x. L = content/scripts/linter.js; P = its prefs.js; prod = …/881hrcxd.default/prefs.js.

**On add.** lint.onAdded is the master switch; lint.onGroup extends it to group libraries. At least 500 ms after an add, enabled non-tool rules run in register order, then one save (L11192-11196, 11948-11975, 12358-12392). [added] Untitled and sync-arriving items are skipped; edits never trigger it (L11952-11955; Zotero sync/syncLocal.js:1011-1013). All rules default on except no-pages-extra-zeros, correct-title-chemical-formula, correct-creators-pinyin and correct-proceedingsTitle-sentence-case (P24, 44, 49, 66). Production turns on no-pages-extra-zeros, proceedingsTitle and onGroup, and leaves onAdded true (prod:72-74).

**Report only.** no-item-duplication, no-article-webpage, no-journal-preprint, require-creators.

**Fills an empty field only.** require-doi (journalArticle, conferencePaper; not zh) fills an empty DOI only on a single Crossref OpenURL match; otherwise it reports (L9217-9262). [corrected]

**Format only.** no-doi-prefix, correct-pages-connector, correct-university-punctuation, correct-edition-numeral and correct-volume-numeral ("2nd ed." → "2"). [corrected] correct-title-punctuation and correct-creators-punctuation only map dash and interpunct variants and drop spaces before title colons (L7149-7220).

**Replaces, blanks or loses data.**

- no-value-nullish blanks any field exactly equal to n.d., N/A, null or eight similar tokens (L9039-9075).
- no-field-misuse (L8915-8966) blanks a shortTitle unless the title starts with the shortTitle's first word [corrected]; series fields matching /SCI/i ("Lecture Notes in Computer Science"); archive, callNumber, rights or libraryCatalog values starting with a decimal. It cuts abstracts at a "摘要翻译" marker. [corrected]
- require-language overwrites any language with a zh-or-en guess from the title (L9269-9296, 5684-5704; P27-31). [corrected] [added] It runs before sentence-casing, so a "de" item becomes "en", loses the zh,de exemption (P43), and German nouns get lowercased.
- no-title-trailing-dot, require-short-title and the four sentence-case rules.
- correct-creators-case: "IEEE Computer Society" → "Ieee Computer Society" (L6189).
- The four date rules keep only year-month-day: "Spring 2020" → "2020", [added] "1998-1999" → "1998" (node, Zotero's date.js, English months).
- correct-extra-order rebuilds Extra: same-key lines grouped, blank lines dropped, free text gathered (L6557-6610, 5390-5431).
- correct-doi-long swaps a short DOI for the long form and adds short-doi to a rebuilt Extra (L6340-6365).
- [corrected] correct-conference-abbr rebuilds Extra on every named conferencePaper, setting or deleting shortConferenceName (L9119-9157).
- correct-publication-title-alias and -case; correct-thesis-type; require-university-place.
- require-journal-abbr overwrites journalAbbreviation, blanking it when none is found (L9076-9117).
- [corrected] correct-pages-range fills empty pages with "1-<PDF page count>" or extends a lone start page (L6628-6675).
- The extra-zeros rules turn "100-110" into "101-110" (L8884; node). [added] Production's pages rule is on.

**Can on-add linting stay on?** Yes. Set these 28 keys false: no-value-nullish, no-field-misuse, require-language, no-title-trailing-dot, correct-title-sentence-case, require-short-title, correct-shortTitle-sentence-case, correct-bookTitle-sentence-case, correct-proceedingsTitle-sentence-case, correct-title-chemical-formula, correct-creators-case, correct-creators-pinyin, correct-date-format, correct-filing-date-format, correct-issue-date-format, correct-priority-date-format, correct-extra-order, correct-doi-long, correct-publication-title-alias, correct-publication-title-case, require-journal-abbr, correct-pages-range, no-issue-extra-zeros, no-pages-extra-zeros, no-volume-extra-zeros, correct-conference-abbr, correct-thesis-type, require-university-place. Read strictly, "rewrite" adds the seven format rules. [corrected]

[added] **Keys, tags, notes.** No on-add rule writes citationKey, tags, notes or attachments; extra-order keeps the Citation Key line (L6572-6584; evidence:506). BBT does not re-key on field changes (evidence:331).

**Verification.** No rule checks fields against a registry. correct-doi-long asks doi.org only whether a DOI resolves; [added] require-doi's DOI is Crossref's match on the item's own metadata, unchecked (L9238). require-journal-abbr sends unlisted journal titles to abbreviso.toolforge.org (L9170, P34).

**research-vault fields** (literature_notes.py:34-52). [corrected] Rewritten: title, creators, date, DOI, publicationTitle, volume, issue, pages, language, extra, abstractNote. url, publisher, ISBN, accessDate: only no-value-nullish.

[corrected] **Not in the evidence file:** extra-zeros corruption, the SCI match, require-language, sentence-case, creators-case, date truncation, require-journal-abbr and conference-abbr's Extra writes, contradicting evidence:1587.

## Production library: languages and scanned PDFs

Production, read-only, 2026-10-04, Zotero 10.0.5 (`fulltext-probe.headers`); library version 37204 at start and end of both passes (`summary-1-2.json`, `fulltext-language-summary.json`); pin b06e212. Files: `/tmp/lane23-ocr/`.

**Method**

- [corrected] 2,839 GETs, under the 6,000 cap: 1,442 (`requests.log`), 3 probes, 2 itemTypeFields reads, plus [added] 1,389 (`fulltext-language-requests.log`) and 3 spot checks (`fulltext-language-spotcheck.txt`).
- Read-only files: profile `prefs.js` (dataDir `D:\Zotero`); 26 storage listings; 21 PDFs via PyMuPDF 1.28.2 (`pdf-textlayer-check.txt`); [added] `extensions.json`, the installed Linter xpi, page 2 of the 19 OCR candidates (`render/`).

**(1) Language field, 1,582 top items** (`summary-1-2.json`, `analysis-3.txt`)

- "en" 1,458, exact; nothing else. Missing 124: 113 computerProgram (no such field, `itemTypeFields-computerProgram.json`), 7 attachments, 1 note, 3 empty, the API omitting empty fields (2 preprint, 1 journalArticle; `analysis-lang-extra.txt`).
- [corrected] The field reflects Linter, not the documents. Linter 3.3.2 is active (`linter-active.txt`). Its require-language rule, on by default, runs on each added titled item and overwrites the field from the title alone, choosing only "zh" or "en", else "en"; production overrides none of these prefs (`linter-x/prefs.js:2, 26-31`; `linter.js:5684-5705, 9268-9292, 11128, 11189-11195, 11948-11972`; `linter-language-rule.txt`). 994 of the 1,458 were added after its 2026-05-14 install; the other 464 were all modified since (`linter-install-vs-dateadded.txt`). The 3 empty items postdate the install, so the rule misses some adds (same file).

**(2) Title scripts**, NFC (`analysis-title-scripts.txt`): Hebrew, Cyrillic, Arabic, CJK 0; Greek 1 (τ, 93YWTK4V); è in 2 (LTNM6UTR, 5GJPLHIR). None mostly non-Latin. Titles cannot reveal a Latin-script non-English language.

**[added] (2b) Document text**, 1,387 indexed PDFs (`fulltext-language.py`, `fulltext-language-summary.json`): a crude stopword count scores all 1,387 (four near-empty) English over de/fr/es/it/nl/pt. Totals: 20 Hebrew, 7 Arabic, 107 Cyrillic characters; CJK is ≥1% of letters in 2: SD96KX49, filed under "What is e-health?" (field "en"), is Japanese (56% CJK); BF3LTGMX is English with a Chinese abstract (`fulltext-language-spotcheck.txt`). 833 abstracts of ≥200 characters all score English (`abstract-language.txt`).

**(3) Stored PDFs:** 1,409 (1,107 `imported_url`, 302 `imported_file`); fulltext 200 for 1,387, 404 for 22 (`fulltext-rows.jsonl`).

- Indexed, >2 pages, \<2,000 characters, all pages indexed: 4: TMDD7Z3A (62 chars/34 pp), 7UT57634 (62/21), 6HSD7RXJ (126/15), 9FZZQMGJ (1,462/14). The first three fall under capture's 500-character floor (`fulltext.py:17, 50-53`); 9FZZQMGJ rates "complete".
- 404, file on disk, 0–2 characters: 15, none with `.zotero-ft-cache`; capture reads 404 as "no-index" (`fulltext.py:27-28`). 14 have page images. [corrected] RBPXNLX3 is also a scan: each of its 23 pages is a form XObject of inline 1-bit CCITT image strips, which `get_images` does not list (`render/rbpxnlx3.txt`).
- 404 with a text layer: 2 (3N7ICNHZ, 5YVRCTGL); no folder or md5: 5.
- Partial to page 100: 50, each ≥2,000 characters (`fulltext.py:47-48`).

**Roll-up** (`analysis-ocr-rollup.txt`, `analysis-ocr-parents.txt`): 19 parents; each PDF is its parent's only child and `links.attachment`, so capture has no other text (`capture.py:84-89, 101-105, 138-143`). 11 journalArticle, 5 bookSection, 2 book, 1 magazineArticle; 1945–2002, one undated. [corrected] Their "en" is not independent evidence: 12 were added after the Linter install, 7 earlier that morning (`linter-install-vs-dateadded.txt`). [added] Titles and venues are English (`ocr-parents-metadata.txt`); page 2 of all 19 renders as printed English (`render/contact-sheet.png`).

**[added] Default OCR language per route:** Zotero OCR "eng" (`xpi/prefs.js:1`; `zotero-ocr.js:371-378`). RapidOCR plugin ships ch_PP-OCRv4; its dictionary has all 94 ASCII characters and 6,270 CJK, but no Hebrew, Arabic, ö, ß, ç or ñ (`rapidocr-model-sha256.txt`, `rapidocr-dict-analysis.txt`). zotero-docling sends no `ocr_lang` by default (`docling-x/prefs.js:20`; `zoteroDocling.js:6419-6421`), so the server engine's default applies: RapidOCR ch, EasyOCR en/es/fr/de, Tesseract eng/spa/fra/deu (`docling-pipeline_options-v2.133.0.py:377, 553, 634`; `docling-serve-usage.md:20`).

## Zotero OCR: setup and capture interplay

Pins: zotero-ocr 0.9.5.1 xpi (f100b3e6…, = installed, loaded files = tag cc87c21) as ocr.js/prefs.js; Zotero 10.0.5 omni.ja (ab1580c0…, /tmp/lane23-ocr/zomni). Outputs: /tmp/lane23-ocr/{zocr,check}/; ev = evidence file.

**Release** \[added\]: 0.9.6 (2026-09-06, sha256 9362734d…) is latest; it adds only -cropbox and progress text (check/diff-0951-096.txt). Production auto-update is off (ev:1781-1783). It was not in the live batch (/tmp/lane23-live/zotero/a1/candidates.tsv); all below is from code.

**Setup**

- [corrected] In both releases a never-set path pref returns undefined and .match throws (Zotero prefs.js:248-272; ocr.js:166-168); the run ends in an alert (204, 540-542). pdftoppm is checked first, with no Windows folder searched (211-212). The C:\\Program Files\\Tesseract-OCR\\ search (218) runs only when ocrPath holds an empty string. Fix: unreleased f23f9ad (zocr/issue-132.txt).
- [added] Neither tesseract.exe nor pdftoppm.exe is on production Windows (check/windows-ocr-tools.txt).
- Install: tesseract-ocr-w64-setup-5.5.3.20260724.exe (UB-Mannheim wiki Home.md:13-14 @1c7e98b); heb/deu via installer or tessdata, checked by `tesseract --list-langs` (Install-additional-language-and-script-models.md:3-11). pdftoppm: unzip oschwartz10612/poppler-windows v26.09.0-0 (zotero-ocr wiki Install-pdftoppm.md:7-13 @8564a1d; zocr/poppler-windows-latest.txt).
- language is free text passed to -l (ocr.js:371-378); eng+deu+heb is valid (tessdoc Command-Line-Usage.md:64-68 @bae104c).

**Outputs** (defaults prefs.js:1-16)

- Child note with the OCR text (456-464).
- Up to 5 stored text/html children "page-N.html", each loading remote hocrjs (466-506).
- Stored twin "<title>.ocr", file <name>.ocr.pdf (509-520): [added] page images (JPEG q70, 300 DPI) plus a text layer (prefs.js:9, 13-16; ocr.js:272-279; Command-Line-Usage.md:161-165).
- overwritePDF (off) overwrites the original, no twin (263, 510). [added] Zotero won't reindex it: its queue skips indexed attachments (fulltext.js:1443-1446). Manual Reindex Item does, uncapped (zoteroPane.js:2372-2384).
- outputAsCopyAttachment off: linked files, ignored by capture (521-527; capture.py:84-89).
- .txt, .hocr and (default) page images stay in storage (530-537).

**Trigger**: item context menu only (110-117; bootstrap.js:11-23; zocr/autorun-grep.txt). Each selected item runs (228); a selected PDF runs itself (231-239). [added] For a parent it takes the first PDF by title (245-255; item.js:4280-4283; sortAttachmentsChronologically false: zotero.js:1593, check/production-prefs-sort.txt): "X" precedes "X.ocr", so a re-run re-OCRs the original and adds a second set (264). Production: user-disabled, no zoteroocr/fulltext.\* prefs (zocr/production-state.txt).

**Indexing**: importFromFile indexes twin and pages at once (attachments.js:150, 3357-3358); PDFs to fulltext.pdfMaxPages=100 (zotero.js:1658; fulltext.js:624). [added] Raising it re-extracts truncated items (fulltext.js:340-360).

**Capture**

- Each usable stored child becomes a fulltext/ file (capture.py:84-106, 146-160); the scan stays unusable (fulltext.py:50-53).
- Best attachment: PDF, URL match, oldest (item.js:4334, 6217-6222), the original stays best; capture falls back to the first usable child (capture.py:138-143).
- /children is newest-modified first, one-second resolution (server_localAPI.js:344, 366-385). [added] On a tie the earlier-added child came first (7A5GMWR4, zocr/children-order.txt). Only an HTML delete and the PDF copy separate the last page's save from the twin's (ocr.js:497, 514; attachments.js:117-147): a page can win (unmeasured).
- [added] A twin over 100 pages is partial (fulltext.py:47-48); with default pages, compile input becomes one page's HTML.
- The OCR note enters the note body (capture.py:205-225).

**Lifecycle**: a new child only notifies the parent (item.js:1872-1894); 88 production attachments are newer than their parent (zocr/parent-vs-child-version.txt). classify checks the parent and recorded attachments (lifecycle.py:95-108). [corrected] In production that notification runs Attachment Scanner (monitor_attachments=true, production prefs.js:29; scan_duplicates default true, its prefs.js:3): a second PDF or text/html child adds #duplicate and saves the parent (attachmentscanner.js:430-443, 471-473, 486 @0.5.1), so lint says drift unless already tagged. [added] Trashing a recorded OCR child makes the note trashed, which capture refuses (lifecycle.py:88-91; capture.py:48); [corrected] so is re-keyed while the old note stands (412-422). Re-capture records the new compile input and drops no-fulltext (183, 249-257).

## OCR alternatives: RapidOCR, zotero-docling, OCRmyPDF

Pins: Z = Zotero 10.0.5 app/omni.ja, test ab1580c0…, production e8aba3eb…; cited files identical except defaults/preferences/zotero.js [corrected] (verify/omni-compare.txt). R = RapidOCR xpi 70cba55d…; D = zotero-docling xpi 3233a991…; O = OCRmyPDF v17.13.0 docs (1a1cfb5). Repo @b06e212. Outputs /tmp/lane23-ocr/; re-checks in verify/.

Scope \[added\]: 19 scans, one per parent, 407 pages, all "en" (analysis-ocr-parents.txt; pdf-textlayer-check.txt). Two are rotated or two-up (render/layout-check.txt). Each has a fulltextItems row: 15 marked missing, 4 with indexedPages=totalPages (verify/fulltextitems-rows.txt; immutable sqlite read, WAL unread). Zotero has no OCR of its own (verify/omni-ocr-grep.txt). No route has run: §6.3's OCR legs did not (evidence:1728).

Host \[added\]: Windows lacks tesseract, pdftoppm, Ghostscript, ocrmypdf; has Python 3.14, uv, winget, choco, stopped Docker Desktop. WSL apt offers ocrmypdf 15.2.0, tesseract 5.3.4 (+heb), poppler, ghostscript, uninstalled (verify/windows-tools.txt, wsl-and-docker.txt).

Siblings, (a)(b)(d) \[added\]: the original stays best attachment but fails the verdict, so capture takes the first usable child (capture.py:138-143). A second PDF child draws Attachment Scanner's duplicate tag, which capture carries; production monitors (production prefs.js:29; evidence:1832).

(a) RapidOCR for Zotero

- Fixed ch_PP-OCRv4 det+rec, no angle classifier or language setting (R pdf-ocr-for-zotero.js:100045-100062).
- Dictionary: all ASCII letters and digits; lacks ö ß ç ñ, many accented letters, Hebrew, Arabic (rapidocr-dict-analysis.txt).
- 36.5 MB xpi; range 9.0–10.0.\*, loaded on the test instance only; no LICENSE file, MPL-2.0 claimed [added] (evidence row 32).

(b) zotero-docling

- Needs user-run docling-serve at localhost:5001 (D prefs.js:1): pip, or a container of 8.7 GB (amd64) or 4.4 GB (CPU) (docling-serve README:27-31, 60-65 @07b1d3d).
- Sends do_ocr=true, force_ocr=false, ocr_lang if set (zoteroDocling.js:6378-6421); advancedJson can set any field, an engine included [corrected] (6423-6440).
- Server "auto" never picks Tesseract (auto_ocr_model.py:67-200). Language defaults: RapidOCR ch, EasyOCR en/es/fr/de, Tesseract eng/spa/fra/deu [corrected] (pipeline_options.py:377, 553, 634).

(c) OCRmyPDF

- Windows: Tesseract (winget/choco), Ghostscript (by hand/choco), `uv tool install ocrmypdf` (O installation.md:525-575). MPL-2.0, Python ≥3.11 (ocrmypdf-pypi.txt). apt's 15.2.0 predates O [added].
- In place under D:\\Zotero\\storage\<key>, on success only (cookbook.md:44-50); key and best attachment unchanged (Z item.js:4317-4337).
- Masthead pages: default exits unmodified; --skip-text skips them; --redo-ocr OCRs around visible text; --force-ocr rasterises all (advanced.md:95-124); --rotate-pages (cookbook.md:59).
- Losses: default PDF/A drops hidden annotations (advanced.md:589-591); --force-ocr flattens non-link annotations (:125-127); signed PDFs refused (cookbook.md:486-490).
- Re-index: the background pass skips rowed attachments (fulltext.js:1434-1447), so all 19. Manual: Reindex Item, multi-select (zoteroPane.js:2372-2386); rebuildIndex has no caller [added] (verify/rebuildindex-callers.txt). Local-API PUT fulltext needs the authorize dialog (server_localAPI.js:41-52, 2605-2629); a later Reindex re-extracts the file over it [added] (fulltext.js:755-762).
- md5 changes at once (server_localAPI.js:1722; item.js:6231-6233); versions move when file sync re-saves the attachment (webdav.js:1595-1600; dataObject.js:1300-1306); lifecycle then reports "file changed" (lifecycle.py:94-138). Production syncs: account and verified WebDAV set; autoSync, file sync default-on [corrected] (verify/production-sync-prefs.txt; Windows zotero.js:1753, 1756). Not measured.
- Local-API file upload writes through Zotero: dialog key, version bumped at once, no re-index [added] (server_localAPI.js:2351-2590).
- Classes: Zotero plugin, Obsidian plugin, Claude Code, Python (assembly-design.md:207-212); Tesseract and Ghostscript fit none (installation.md:527-528). Shell-outs: git, wslpath, claude-obsidian (gitstate.py:113; paths.py:26; compile.py:230-244).

(d) Zotero OCR [added]

- 0.9.5.1 (f100b3e6…) installed on production, disabled; range 6.999–10.\*; AGPL-3.0; language eng (prefs.js:1).
- Needs tesseract (sought in C:\\Program Files\\Tesseract-OCR) and pdftoppm (pref; no Windows default) (zotero-ocr.js:211-224).
- Writes a note, ≤5 page-HTML attachments and an .ocr PDF sibling (456-528); the note enters the literature note (evidence row 30).

Others \[added\]: Mktero, MinerU for Zotero (never reaches capture), Zotero-AI-OCR (unscreened, capped 9.\*) (evidence rows 34-35, :57).

## Obsidian's trust prompt for a vault that ships plugins (measured 2026-10-06)

Measured on the scratch vault with Obsidian 1.13.7 in WSL, through the Obsidian CLI, read-and-restore; the code path read in `app.js`.

- With restricted mode on and one MIT plugin (obsidian-hider 1.7.1) seeded in `.obsidian/plugins/`, a reload showed the modal `.modal.mod-trust-folder`: title "Do you trust the author of this vault?", buttons "Browse vault in Restricted Mode" (default focus) and "Trust author and enable plugins". No plugin loaded while it was open; no notices; `dev:errors` empty.
- The prompt fires from `PluginManager.initialize()` on every load when the key `localStorage["enable-plugin-" + appId]` is null and `.obsidian/plugins/` holds at least one loadable `manifest.json`. `community-plugins.json` does not decide whether it fires; it decides which plugins Trust enables. Dismissing writes nothing, so the prompt returns on the next load.
- Trust calls `app.plugins.setEnable(true)`, which writes the key, enables every id in `community-plugins.json` and opens Settings → Community plugins (read in the source; not clicked).
- `setEnable(false)` and `obsidian plugins:restrict on` write `"false"`, which silences the prompt for that vault permanently; plugins then stay off with no message.
- The key is per vault registration (`appId` from `obsidian.json`), stored outside the vault, so a template copied and opened as a new vault prompts.
- Limits: reloads were measured, not a first open of a never-seen folder (the check runs on every load, so the two should match); 1.13.7 only.

## The daily-notes folder convention (measured 2026-10-04)

GitHub code search for committed `.obsidian/daily-notes.json` files (`filename:daily-notes.json path:.obsidian`): 1,536 hits; the first 500 hits came from 406 distinct repositories, of which 403 files parsed. Grouped by the folder's last path segment, case-folded:

| Folder                                                        | Vaults   |
| ------------------------------------------------------------- | -------- |
| `daily`                                                       | 76       |
| `daily notes`                                                 | 47       |
| no `folder` key                                               | 20       |
| empty (new-note location)                                     | 14       |
| `journals`                                                    | 9        |
| `diary`                                                       | 9        |
| `journal`                                                     | 9        |
| `日记`                                                        | 8        |
| `daily-notes`                                                 | 8        |
| a long tail (`06 - daily`, `_daily`, `3_logs`, `calendar`, …) | the rest |

Committed vaults skew towards published starter kits and templates; this is the convention among people who publish vault setups.
