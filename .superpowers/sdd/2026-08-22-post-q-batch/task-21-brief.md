### Task 21: Spec gap closures + acceptance

**Files:**

- Modify: `docs/superpowers/specs/2026-08-16-foundation-spec.md` (§6 gate rows: metadata, update-notice)

- Modify: `docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md` (second sequencing gate: mark satisfied)

- [ ] **Step 1: Metadata row (§6, ~line 98)** — append: *"A compared field absent on either side is SKIPPED for that field, recorded in the outcome's detail — never folded into MATCHED (closed 2026-08-22, audit gap)."* Then verify the implementation agrees (read `check_metadata`'s absent-field handling; if it silently folds, fix it with a failing-test-first micro-cycle inside this task and note it).

- [ ] **Step 2: Update-notice row (§6, ~line 99)** — append the missing-local-version rule by the four-state definitions: *"an item lacking a local `version` field is SKIPPED for the version leg (the item lacks the field the check needs) — never UNREACHABLE, which is reserved for attempted-and-failed"* — then reconcile the implementation (`_datacite_version_outcome` / arXiv twin report UNREACHABLE "outage — version status unavailable" for a missing local field today; both audit lanes disputed this — settle it by the doctrine definition, failing test first, and record the resolution in the commit body).

- [ ] **Step 3: Acceptance sweep** — re-run the audit's confirmed reproductions for every defect this plan claims (defects 1, 2, 3, 6, the fixity pair, the archive branch): each must now be unreproducible. Full suite offline AND live (`RV_LIVE=1 RV_LIVE_NET=1 RV_MAILTO=<real>`, Zotero running). 8/8 hooks.

- [ ] **Step 4: Mark BOTH Plan S sequencing gates satisfied** (one line each, dated, pointing at this plan) — Phases 2–6 and the drill unblock together.

- [ ] **Step 5: Commit** `fix: close spec §6 missing-data gaps; trust-core remediation acceptance` — then merge to main and push in the same motion.

______________________________________________________________________

## Part 3: Terminology (added 2026-08-23)

**NAMING RULING (author, 2026-08-23) — the authored per-source account is a `summary`.** Binding on every implementer who touches this artifact; it creates no work in this plan.

**What is named:** the authored prose account of what one source says, written into that source's literature note free region — authored (salience judgment), never machine-projected. Ruled into existence by slice findings 15–16 (`research/validation-slice/2026-08-22-slice-findings.md`), still unbuilt: no skill step writes it today (Plan D polish-pass item 10, gated on the deferred `/fulltext` leg).

**The name is `summary`.** Walk, per `docs/terminology.md` §2, under the author's ruling that **churn is not a cost and the user-facing term takes precedence** (§1; tie-breaker 4, surface fit is absolute): T1 OKF silent (its `description` is a frontmatter field, not body prose); T2 toolchain surfaces name the container, not this artifact (ZotLit's `note` template body, Zotero child notes, CSL `note`/`annote`); T4 offers *summary*, *synopsis*, *précis*; **T6 is near-unanimous on `## Summary` / "source summary page"** — paperclip (79k★), claude-obsidian (11.3k★), SamurAIGPT/llm-wiki-agent (3.4k★), sdyckjq-lab/llm-wiki-skill (2.4k★), obsidian-llm-wiki-local (809★ — schema field `summary`), swarmvault (666★), pi-llm-wiki (524★), tonbistudio/llm-wiki (247★ — page-type enum value `summary`), wiki-skills (179★); the llm-wiki gist itself writes "a summary page in the wiki". T4 and T6 agree. *Page* is dropped from the borrowed phrase — it names the file, and that slot is `literature note`.

**Declined, so they are not re-proposed:** `digest` (adopted earlier the same day and superseded — the sole ecosystem instance is a 9-star repo, and `hexdigest()` is stdlib so the collision residual never fully clears); `synopsis` (zero collisions but no user-facing currency, which the ruling makes decisive); `précis` (same, and it implies a proportional in-order restatement, which an `(inference)`-tagged region is not); `annotation` (exact in annotated-bibliography practice, fatal against Zotero's highlight sense); bare `summary` **as a vault-facing word for anything else** is now spent.

**The glossary entry does NOT land now** (author ruling): a glossary defines what exists, and this artifact has no writer yet. `CONTEXT.md` gains the term — and `research_vault/templates/vault/system/glossary.md` its projection — in the same change that ships the step which authors it. The entry's wording is settled by this ruling; write it when the step ships.

**What the implementer of that step pays, all priced at zero (`docs/terminology.md` §1) but listed so none is discovered late:**

- `research_vault/templates/vault/index.md:10` — "daily activity log (summary: \[[log]\])" is the only *vault-facing* competing use of the word; reword ("rolled up") in the same change, and update its whole-file test pin in the same commit.
- `CONTEXT.md`'s *Log* entry — "summarized in root `log.md`" → same reword, with the vault-glossary projection.
- `research_vault/okf.py:1` ("the log summary artifact") and `inbox.summary()` are dev-facing (T7) and never reach vault prose — rename or leave, implementer's discretion, not a blocker.
- **Third-party surfaces never rename:** arXiv's `<summary>` element and PubMed's `eSummary` endpoint keep their own names. `skills/find-sources/scripts/arxiv_atom.py:93` already translates arXiv's `<summary>` to `abstract` at the boundary — keep that translation exactly, because it is what stops the wire word for *abstract* from reaching the vault as the word for the one thing an abstract may never produce (ADR-level rule, slice finding 16).
- The section heading in the literature-note free region reads `## Summary`, matching the ecosystem the researcher already knows.

