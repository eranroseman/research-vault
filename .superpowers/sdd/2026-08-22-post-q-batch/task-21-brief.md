### Task 21: Spec gap closures + acceptance

**Files:**
- Modify: `docs/superpowers/specs/2026-08-16-foundation-spec.md` (§6 gate rows: metadata, update-notice)
- Modify: `docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md` (second sequencing gate: mark satisfied)

- [ ] **Step 1: Metadata row (§6, ~line 98)** — append: *"A compared field absent on either side is SKIPPED for that field, recorded in the outcome's detail — never folded into MATCHED (closed 2026-08-22, audit gap)."* Then verify the implementation agrees (read `check_metadata`'s absent-field handling; if it silently folds, fix it with a failing-test-first micro-cycle inside this task and note it).

- [ ] **Step 2: Update-notice row (§6, ~line 99)** — append the missing-local-version rule by the four-state definitions: *"an item lacking a local `version` field is SKIPPED for the version leg (the item lacks the field the check needs) — never UNREACHABLE, which is reserved for attempted-and-failed"* — then reconcile the implementation (`_datacite_version_outcome` / arXiv twin report UNREACHABLE "outage — version status unavailable" for a missing local field today; both audit lanes disputed this — settle it by the doctrine definition, failing test first, and record the resolution in the commit body).

- [ ] **Step 3: Acceptance sweep** — re-run the audit's confirmed reproductions for every defect this plan claims (defects 1, 2, 3, 6, the fixity pair, the archive branch): each must now be unreproducible. Full suite offline AND live (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>`, Zotero running). 8/8 hooks.

- [ ] **Step 4: Mark BOTH Plan S sequencing gates satisfied** (one line each, dated, pointing at this plan) — Phases 2–6 and the drill unblock together.

- [ ] **Step 5: Commit** `fix: close spec §6 missing-data gaps; trust-core remediation acceptance` — then merge to main and push in the same motion.


______________________________________________________________________

## Part 3: One sense per term (ruled 2026-08-23)

