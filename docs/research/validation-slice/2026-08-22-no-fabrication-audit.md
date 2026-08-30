# No-fabrication audit — specs, skills, implementation

Run 2026-08-22, author-directed ("review specs and implementation and ensure we never fabricate missing information"). Method: five finder lanes (render projection, verification layer, CLI writers, skills prose + templates, spec cross-check), 39 candidate findings, each adversarially verified by a fresh agent instructed to refute against the actual code. 21 confirmed, 18 refuted. Full per-agent evidence: the workflow journal (session record, run wf_e23da149-e35). READ-ONLY audit — nothing was changed; every fix routes through the normal plan chain.

## Distinct defects (deduplicated, 17)

Cross-lane duplicates: checks.py:522 (date padding) found independently by two lanes; the "unresolved" fixity placeholder confirmed as verify.py:209 + __main__.py:234 (one defect, two surfaces).

**Trust-core (fix-first candidates):**

1. **Retraction Watch screening is inert** — checks.py:924 drops every RW row whose RetractionDate is not ISO; the production CSV uses "M/D/YYYY 0:00". The entire RW leg silently dead while verify reports as if coverage ran.
2. **UNMATCHED rounded to MATCHED** — checks.py:1024 discards a genuine non-blocking version-mismatch UNMATCHED when the RW leg is MATCHED-with-warns; mints a verified update-notice event and unblocks publish.
3. **Vacuous machine-confirmed tier** — events.py:255: no DOI + no PMID means empty applicable-check set, subset test passes vacuously, top machine tier minted with zero MATCHED ever recorded. Spec §86 shares the gap (never states the zero-applicable-checks tier).
4. **Tier-2 citability unenforced** — checks.py:151 validates whole-library bibliography membership only; a never-imported citation reports MATCHED and publishes where spec L45 requires the literature note to exist.
5. **Free-region destruction** — notes.py:151: an existing note without the exact %%/rv-managed%% marker line loses its whole body to the pristine seed on import/backfill, silently, printed as success. Violates §5 never-delete.

**Fabricated values on durable surfaces:**

06. **Date-precision fabrication** — checks.py:522 pads year-only/year-month Crossref notice dates to Jan 1; invented precision drives the reinstatement-clears-retraction ordering and persists in inbox notice-dates and ack fingerprints.
07. **Placeholder as ack anchor** — __main__.py:234 writes literal "unresolved" into fixity-sha256; verify.py:209 adopts it as the acknowledgment target-hash — acks scope to a constant, not content.
08. **Unverified snapshot recorded** — archive.py:191 supplied-snapshot branch records any live archive.org URL as archive-url MATCHED without confirming it is a Wayback snapshot of anything.
09. **Citekey-as-title substitution unrecorded** — notes.py:133/229.
10. **Ambiguous citekey resolved arbitrarily** — __main__.py:207 takes matches[0] across libraries; item["id"] overwrite erases which record was chosen.
11. **Midnight-UTC generated.at default** — notes.py:215 (latent; CLI passes real time).
12. **Backdated log line wears today's HH:MM** — publish.py:357.

**Prose/template/config surfaces:**

13. **evidence-conventions abstract row** — SKILL.md:94's "or mark (inference)" branch still permits abstract-derived content without disclosing the abstract-only basis — conflicts with the same-day full-text-only ruling (finding 16).
14. **Placeholder mailto reaches registries** — machine.json.example's you@example.edu is copied by scaffold and, unedited, transmitted to Crossref/OpenAlex/Unpaywall as a real contact; doctor flags it but nothing gates the requests.
15. **Template provenance stamps without a source** — project.md/synthesis.md seeds carry generated: {by: {{ACTOR}}, at: {{NOW}}} with no CLI verb owning the values: placeholders persist or the agent invents them.
16. **pre-commit fails open on unimportable package** — templates/git/pre-commit:12 exits 0, inconsistent with its own missing-python3 exit-1 branch.

**Spec under-specification (implementer may legally fabricate):**

17. Spec rows never define: the metadata gate's absent-field outcome (line 98); the update-notice result for a missing local version field (line 99); the zero-applicable-checks trust tier (line 86, = defect 3's licence).

## Confirmed findings — verifier evidence

### docs/superpowers/specs/2026-08-16-foundation-spec.md:86 — HIGH, class B (spec lane)

**Claim:** The machine-confirmed definition ("requires all applicable note-level checks and quote claims to match") never states what tier an item with zero applicable checks receives, so vacuous satisfaction legally mints the top machine tier with no MATCHED result at all.

**Verifier:** CONFIRMED empirically. events.py:255 `machine_confirmed = _applicable_note_checks(data) <= checks` — the applicable set is {} for any note lacking doi/pmid (events.py:234-239), and {} \<= checks is vacuously True, so trust_tier() returns "machine-confirmed" for a note with zero identifiers, zero quote claims, and ZERO verified events (verified by running it: even a frontmatter-less file derives "machine-confirmed"). The spec sentence at line 86 indeed has no empty-set floor, and no other spec section supplies one. The path is reachable (URL-only web sources / discovery-failed items are first-cl …[trimmed; full verdict in the workflow journal]

### docs/superpowers/specs/2026-08-16-foundation-spec.md:98 — HIGH, class B (spec lane)

**Claim:** The metadata gate row names the compared fields (title/authors/year) but never specifies the outcome when a compared field is absent on either side, so an implementer can legally fold the missing comparison into MATCHED with no trace.

**Verifier:** CONFIRMED. The spec row (foundation-spec.md:98) names title/authors/year as the compared fields but carries no absent-field clause, and the implementation took exactly the silent-vacuous option: checks.py:436 compares year only `if local_year is not None and remote_year is not None`, and checks.py:423-428 compares given-name initials only when `local_given and remote_given` — both fall through to `Outcome("metadata", target, Result.MATCHED, "matched", extra={doi, agency})` at checks.py:444. No surface records the partial coverage: the reason is "matched", extra carries only doi+agency, and the …[trimmed; full verdict in the workflow journal]

### docs/superpowers/specs/2026-08-16-foundation-spec.md:99 — HIGH, class B (spec lane)

**Claim:** The update-notice row orders DataCite/arXiv items to check "OpenAlex is_retracted + version status instead of silently passing" but never defines the result when the local item lacks a `version` field, leaving the implementer to invent a state.

**Verifier:** CONFIRMED. checks.py:662-664/746-748 return UNREACHABLE with reason "outage — <provider> version status unavailable" (checks.py:637-643) when the LOCAL entry lacks `version` (arXiv also for non-`vN` values like "2") — in the DataCite branch before any network request is attempted, so the asserted outage is pure invention. Path is the default one: CSL-JSON rarely carries `version`. The fabricated cause reaches durable + acted-on surfaces: verify.py:747-779 (\_file_effects) appends every non-MATCHED outcome, including this UNREACHABLE, to the append-only inbox/review-queue.md (inbox.py:21) with t …[trimmed; full verdict in the workflow journal]

### research_vault/__main__.py:234 — HIGH, class A (spec lane)

**Claim:** An unresolvable attachment path appends the placeholder string "unresolved" into the literature note's `fixity-sha256` list — a durable frontmatter surface whose first element verify.py reuses as the acknowledgment-scope hash, so acks scope to a constant instead of content.

**Verifier:** CONFIRMED, with the mechanism sharpened. The frontmatter write alone would be refutable (loud stderr warning at __main__.py:233, self-describing value, documented in plan-a-bridge-core L1264, pinned by test_cli_live.py:545) — but the reuse leg is real fabrication: verify.py \_citekey_hash (L206-211 candidate path, L218-222 live path) accepts ANY nonempty string as fixity-sha256[0], so "hash unavailable" routes into the "fixity present" branch and returns the constant "unresolved" as the ack-scope hash, bypassing the note-content-hash fallback (verify.py L211/L223) that governs when fixity is ho …[trimmed; full verdict in the workflow journal]

### research_vault/archive.py:191 — HIGH, class B (writers lane)

**Claim:** The supplied-snapshot branch of archive_source records any caller-supplied archive.org URL into the durable literature note's archive-url field with Result.MATCHED after only a host + non-404 liveness probe — it never confirms the URL is a Wayback snapshot at all (no /web/<timestamp>/ shape check; is_archive_url checks only scheme and netloc) nor that it snapshots this note's url, contradicting the module's own contract that archive-url is written only on a snapshot the archive confirms it is serving for this source.

**Verifier:** CONFIRMED. Decisive: no surface records the substitution — \_record (archive.py:140) emits extra={"archive_url": url} and note frontmatter byte-identical to the availability-confirmed path, so a reader cannot tell the URL was caller-asserted rather than archive-confirmed. Mechanics verified: is_archive_url (archive.py:63-68) checks only scheme+netloc, so https://archive.org/donate passes; webapi.get_status returns only \<400 or 404 (403/405/501 on GET raise ApiError, webapi.py:80-101), so any 2xx/3xx reaches \_record at archive.py:191 — no /web/<timestamp>/ shape check, no check that the snapshot …[trimmed; full verdict in the workflow journal]

### research_vault/checks.py:151 — HIGH, class B (spec lane)

**Claim:** Tier-2 citability (spec L45: a citekey is citable only if its literature note exists) is enforced nowhere — the closing citekey check validates only tier-1 whole-library bibliography membership, so a never-imported cross-project citation reports MATCHED and publishes cleanly where the spec requires loud failure.

**Verifier:** CONFIRMED. checks.py:150-153 is tier-1 only (`citekey in bibliography_universe`, universe = whole-library bibliography.load — verify.py:832/867), while foundation-spec L45 (ruled 2026-08-22, commit 8df8c9c) makes the citekey check's contract tier-2: citable only if literatures/<citekey>.md exists, with accidental cross-project citation required to "fail loudly". Every backstop is confirmed absent for paraphrase/inference claims: lints.py:479-481 \_note_status returns (None,None,True) for a missing note so lint_screening_state emits nothing; factcheck.py:104-106 silently drops the claim (deferri …[trimmed; full verdict in the workflow journal]

### research_vault/checks.py:522 — HIGH, class A (verification lane)

**Claim:** Partial Crossref notice dates (year-only or year-month date-parts) are padded with month/day 1 into full ISO dates, fabricating precision that is written durably into inbox notice-date fields and ack fingerprints and that drives the reinstatement-clears-retraction ordering comparison.

**Verifier:** CONFIRMED by execution. checks.py:522 `(parts + [1, 1])[:3]` pads \[[2023]\]->"2023-01-01" and \[[2023,7]\]->"2023-07-01"; missing dates honestly return None but partial dates are silently promoted to day precision with no precision marker. The padded date (a) drives line 572 `reinstatement >= notice["notice_date"]` — executed: a year-only retraction padded to Jan 1 is cleared by a 2023-06-15 reinstatement, making check_update_notice mint MATCHED (checks.py:841-849) from invented ordering; and (b) flows via \_blocking_outcome extra (checks.py:623) -> verify.py:750-772 inbox.append_entry(notice_date …[trimmed; full verdict in the workflow journal]

### research_vault/checks.py:522 — HIGH, class A (spec lane)

**Claim:** A year-only or year-month Crossref `updated` date is padded to January 1 and written as a full ISO `notice_date`, and that invented precision both feeds the reinstatement-clearing comparison and persists as the inbox's bi-temporal notice-date.

**Verifier:** CONFIRMED. checks.py:522 `year, month, day = (parts + [1, 1])[:3]` pads year-only/year-month Crossref `updated` date-parts to a full ISO date with no precision marker (notice dict at :548 keeps only type+notice_date). The padded date feeds :572 `reinstatement >= notice["notice_date"]`, so a year-only retraction padded to Jan 1 is cleared by a mid-year reinstatement and check_update_notice returns MATCHED (trust minted per spec §86); it also persists verbatim as the bi-temporal `notice-date` inbox field (verify.py \_file_effects -> inbox.append_entry; inbox.py:357) and enters the acknowledgment …[trimmed; full verdict in the workflow journal]

### research_vault/checks.py:924 — HIGH, class B (verification lane)

**Claim:** load_rw_csv silently drops every Retraction Watch row whose RetractionDate is not ISO format, and the real production CSV uses "M/D/YYYY 0:00" dates, so the entire RW retraction-screening leg is inert while verify reports SKIPPED/None as if RW coverage ran.

**Verifier:** CONFIRMED by independent reproduction. Fetched the production RW CSV from the exact URL templates/ci/rw-batch.yml:27 curls (passed raw to --rw-csv, line 36): RetractionDate is "M/D/YYYY 0:00" ("4/10/2026 0:00"); in a 2,023-row sample all 2,022 dated rows are \_INVALID under _rw_date (checks.py:904, fromisoformat-only), so checks.py:922-927 silently drops every row — load_rw_csv returned doi index 0 / pmid index 0, and check_rw_batch on a genuinely retracted entry (10.1002/2211-5463.13173, PMID 33989451, nature "Retraction") returned None. No surface records the drop: no counter/warning in load_ …[trimmed; full verdict in the workflow journal]

### research_vault/checks.py:1024 — HIGH, class B (verification lane)

**Claim:** reduce_update_notice_outcomes discards a genuine non-blocking UNMATCHED live leg (DataCite/arXiv version mismatch) whenever the RW leg is MATCHED-with-warns, reducing ran-and-disagreed to MATCHED, which mints a verified update-notice event, clears markers, and unblocks the publish gate.

**Verifier:** CONFIRMED, empirically. checks.py:1024-1032 selects by (UNREACHABLE, MATCHED, SKIPPED) — UNMATCHED absent — and the only UNMATCHED rescue (1008-1013) requires extra["class"]=="blocking", which \_version_mismatch (646-652, empty extra) never carries. Repro: reduce(\_version_mismatch("citeA","arXiv"), rw MATCHED-with-correction-warn) → MATCHED "matched" + warn only; the ran-and-disagreed live leg leaves zero trace (verify.py:562-564 appends only the reduced outcome — not a recorded substitution; the filed warn entry records the RW correction, not the mismatch). Durable/trust impact when it fires: …[trimmed; full verdict in the workflow journal]

### research_vault/events.py:255 — HIGH, class B (spec lane)

**Claim:** trust_tier() mints "machine-confirmed" for a note on which zero checks ever ran: with no DOI and no PMID the applicable-check set is empty, the subset test passes vacuously, and no floor requires even one verified event.

**Verifier:** CONFIRMED, empirically reproduced: a literature note with neither doi nor pmid, no managed quote claims, and no verified events returns "machine-confirmed" from events.trust_tier. Decisive lines: research_vault/events.py:239 (`_applicable_note_checks` falls through to `return set()`) and :255 (`machine_confirmed = _applicable_note_checks(data) <= checks` — `set() <= set()` is vacuously True, and no floor requires even one event). Ran it: a url-only note with empty `verified` prints "machine-confirmed". The class is real and first-class — lints.py:573 and skills/import-source/SKILL.md §9 def …[trimmed; full verdict in the workflow journal]

### research_vault/notes.py:151 — HIGH, class F (render lane)

**Claim:** If an existing note at literatures/<citekey>.md lacks the exact %%/rv-managed%% marker line (hand-written note, or a note whose marker was edited), \_split_free discards its entire body and render_note replaces it with the pristine SEED_FREE scaffold, so import-note silently destroys the free region and the resulting empty '## Notes' section reads as if no notes were ever taken while the CLI prints the path as success.

**Verifier:** CONFIRMED. notes.py:145-151 matches only the three exact standalone spellings of %%/rv-managed%%; any existing note without that exact line hits `return SEED_FREE` (line 151), and render_note:257 emits frontmatter + fresh managed body + SEED_FREE, dropping the whole prior body. Reachable in production: __main__.py cmd_import_note (lines 223, 271, 301-303) overwrites via \_write_note_text and prints the path with exit 0; the guarded FrontmatterError never fires because frontmatter.parse returns ({}, text) for a no-frontmatter body (frontmatter.py:134-137), so hand-written notes and notes with a …[trimmed; full verdict in the workflow journal]

### research_vault/verify.py:209 — HIGH, class A (verification lane)

**Claim:** \_citekey_hash adopts fixity-sha256[0] as the acknowledgment target-hash whenever it is any nonempty string, including the literal "unresolved" placeholder that import-note writes when an attachment cannot be hashed, so a placeholder serves as the fixity basis that scopes human acknowledgments.

**Verifier:** CONFIRMED. verify.py:207-210 (and live twin 218-222) `if isinstance(first, str) and first: return first` adopts fixity-sha256[0] unconditionally; __main__.py:234 writes the literal "unresolved" there, and test_cli_live.py:545 pins it landing durably. The sentinel then becomes the ack target-hash for every finding on that citekey (verify.py:254 and :359 consult \_citekey_hash first, even short-circuiting claim-block hashing for citekey#^claim targets), is auto-adopted into human acks (inbox.py:402-403), and is_acknowledged (inbox.py:694-700) matches "unresolved"=="unresolved" forever — equating …[trimmed; full verdict in the workflow journal]

### research_vault/__main__.py:207 — MEDIUM, class C (render lane)

**Claim:** When Zotero item.search returns more than one item carrying the requested citekey (possible across libraries), the importer silently takes the first match, so the projected metadata (title, DOI, URL, attachments) may come from the wrong record with no record that an alternative existed.

**Verifier:** CONFIRMED. The search is library-unscoped while the integrity gate is library-scoped, so an ambiguous citekey resolves silently to an arbitrary record. Decisive lines: zotero.py:111 sends item.search with no library scope (repo's own docs/research/raw/zotero-integration.json:29 records that results carry "citekey and library fields", i.e. span libraries), while zotero.py:147 export_csl(None) reads /api/users/0/ — My Library only — so the autoexport gate at __main__.py:210 cannot see a group-library item sharing the citekey. __main__.py:192-207 keeps every same-citekey match and takes matches[0]; li …[trimmed; full verdict in the workflow journal]

### research_vault/notes.py:133 — MEDIUM, class C (render lane)

**Claim:** When the Zotero item has no title, the citekey is silently substituted into the title's slots — the managed H1 heading and the aliases frontmatter entry — with no record of the substitution; a present-but-empty title instead renders a bare '# ' heading and aliases: [""] (empty string as a value).

**Verifier:** CONFIRMED, reproduced end to end. Missing-key half: notes.py:133 (`heading = display_text(item.get("title", item["id"]))`) and notes.py:229 (`fm["aliases"] = [display_text(item.get("title", item["id"]))]`) write the citekey into the title's two slots of the durable note `literatures/<citekey>.md`; a live run of render_note with a title-less item emits `# smith2020` and `aliases: - "smith2020"` with no record of the substitution — classic class C. Reachable: zotero.py `_validate_object_list` imposes no title requirement on `item.search` results, and `__main__.py:207-208,271` passes the match st …[trimmed; full verdict in the workflow journal]

### research_vault/templates/git/pre-commit:12 — MEDIUM, class E (spec lane)

**Claim:** The commit-closing pre-commit surface exits 0 when research_vault is not importable, silently opening the gate — inconsistent with its own missing-python3 branch two lines earlier, which exits 1 "refusing an unverifiable commit".

**Verifier:** Confirmed with one correction: not fully silent (stderr note exists), but the note couples an unconditionally false assurance to a success exit. pre-commit:10-13 exits 0 when research_vault is not importable while asserting "CI will replay verification"; scaffold.py:192 defaults with_ci=False and verify.yml is only copied at scaffold.py:225-231, so in a default vault no CI replay exists — the promised compensating control is fabricated. Contrast pre-commit:6-9 (missing python3 fails closed, exit 1). Reachable as the common case: no [project.scripts] in pyproject.toml, the CLI runs as \`pytho …[trimmed; full verdict in the workflow journal]

### research_vault/templates/research-vault/machine.json.example:2 — MEDIUM, class F (skills lane)

**Claim:** The placeholder contact "you@example.edu" is copied verbatim by scaffold into .research-vault/machine.json and, if never edited, is transmitted to Crossref/OpenAlex/Unpaywall as a real mailto contact on every polite-pool request — the guard is inconsistent: doctor names that exact string invalid, but the request path accepts and sends it.

**Verifier:** CONFIRMED. templates/research-vault/machine.json.example:2 is copied verbatim to .research-vault/machine.json by scaffold.py:212-217; webapi.py mailto() (lines 38-44) checks only non-empty, so the placeholder passes and rides every Crossref/OpenAlex/Unpaywall/Wayback request in the query string (webapi.py:60) and User-Agent (webapi.py:75-76). The project's own code rules this string equivalent to missing — scaffold.py:258-263 flags exactly `mailto.strip() == "you@example.edu"` UNMATCHED ("mailto is missing or still uses you@example.edu") — yet the request path transmits it as configured, so the fail-closed …[trimmed; full verdict in the workflow journal]

### research_vault/templates/vault/system/templates/project.md:5 — MEDIUM, class F (skills lane)

**Claim:** The project note seed (and synthesis.md line 5 identically) ships a machine-provenance stamp `generated: {by: "{{ACTOR}}", at: "{{NOW}}"}` that the project skill directs the agent to author question.md from with no CLI verb or stated source for those values, so either literal placeholders persist in durable frontmatter or an agent-invented actor/timestamp lands there indistinguishable from the CLI-written stamps on literature notes.

**Verifier:** CONFIRMED, and stronger than the finder stated. project.md:5 (and synthesis.md:5) ship `generated: {by: "{{ACTOR}}", at: "{{NOW}}"}`; skills/project/SKILL.md:48 directs hand-authoring question.md "starting from system/templates/project.md ... no CLI verb is involved" and names only type/status, so the agent must handle line 5 alone with no sourced value for actor or time. The honest omit path is foreclosed: docs/superpowers/specs/2026-08-16-foundation-spec.md §5 requires "generation metadata" on project and synthesis notes while defining `generated` as what "machine-written mutable concepts ca …[trimmed; full verdict in the workflow journal]

### skills/evidence-conventions/SKILL.md:94 — MEDIUM, class D (skills lane)

**Claim:** The abstract rationalization row's second branch — "or mark (inference) and accept the lower confidence" — permits retaining abstract-derived content as a durable inference claim without disclosing its abstract-only basis, counter to the ruling that an abstract-derived summary is fabricated facts; medium rather than high only because import-source §4 holds low/absent-confidence inference claims at integration with a review record.

**Verifier:** CONFIRMED. skills/evidence-conventions/SKILL.md:94's own first sentence names the scenario "a memory of the abstract", then the second branch — "or mark `(inference)` and accept the lower confidence" — permits keeping that memory-derived content as a durable tagged claim: summarizing from memory, class D by definition, no ruling extension needed. The tag-is-the-disclosure defense is foreclosed by the author ruling in docs/research/validation-slice/2026-08-22-slice-findings.md finding 16 ("a tag does not launder it"), which governs the same claim grammar — the ruled digest form is itself evidence-conventions tagged clai …[trimmed; full verdict in the workflow journal]

### research_vault/notes.py:215 — LOW, class A (render lane)

**Claim:** When a caller omits generated_at, render_note fabricates a midnight-UTC generation timestamp from the accessed date and writes it into the durable generated.at frontmatter field, indistinguishable from a real timestamp; the production CLI passes the real time, so this is a latent library-API path (exercised throughout the tests).

**Verifier:** Confirmed but latent. research_vault/notes.py:214-215 (`if generated_at is None: generated_at = f"{accessed}T00:00:00Z"`) synthesizes a midnight-UTC timestamp that lines 246-248 write into the durable `generated.at` frontmatter field, byte-indistinguishable from a clock reading; foundation-spec §5 defines `generated.at` as "the last meaningful content change" and Plan Q's author ruling requires machine timestamps to derive from an explicit timezone-aware UTC clock, so the default asserts a change time nobody measured. Nothing in the rendered note records that the value was defaulted. Howeve …[trimmed; full verdict in the workflow journal]

### research_vault/publish.py:357 — LOW, class A (writers lane)

**Claim:** publish.\_append_log stamps the current wall-clock time (now:%H:%M) onto whatever day file the caller-supplied date names, so a backdated withdrawal (mark_withdrawn(date=...)) writes a log line into log/<past-date>.md whose HH:MM is today's time presented as that day's — a fabricated timestamp on the durable activity log; latent, since the CLI exposes no --date for dispositions (library callers only).

**Verifier:** Confirmed: publish.py:351-357 computes `now` once, names the day file from caller `date` (`f"{now.date().isoformat() if date is None else date}.md"`) but stamps the line `f"- {now:%H:%M} ..."`, so mark_withdrawn(date=<past>) (publish.py:396-404, its only caller) writes today's HH:MM into log/<past-date>.md — and into root log.md via okf.regenerate_log — with no marker; a reader cannot tell the time is not that day's. No mitigation exists: no date validation, no recorded substitution, and tests/test_publish.py:430-445 exercise only the dateless CLI path. Reachable only via the library kwarg — C …[trimmed; full verdict in the workflow journal]

## Refuted (18) — the honest side of the ledger

Notable refutations (the checks that looked fabrication-shaped and are not): empty-annotation render, quote-claim fallback comparison, discovery-merge identifiers, missing-version UNREACHABLE wording, scaffold placeholder install (guarded by doctor at the right moment), CI exit-3 rounding (recorded loudly), factcheck SKIPPED wording. Full list in the workflow journal — kept as negative knowledge so the next audit does not re-litigate them.

## Routing

Fixes are plan-chain material, not live edits: Plan Q owns the tree mid-flight. Proposed routing at triage — trust-core items 1–5 warrant their own remediation plan before the slice's Phase 4–6 (verify/publish legs would exercise defective gates); items 6–12 batch candidates; 13 lands with the polish pass (amends the same SKILL.md row); 14–16 small-fix batch; 17 spec amendments alongside their implementation fixes. Author triages.
