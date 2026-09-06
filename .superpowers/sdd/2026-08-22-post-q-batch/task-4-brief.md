### Task 4: find-sources corrections + cross-read wiring (items 5, 7, 11, 12)

Disposition: historical (2026-09-06)

**Files:** Modify: `skills/find-sources/SKILL.md` (+ its `references/` where the cross-read says so); test pins.

- [ ] **Step 1 (C-3 + item 11 fold):** Credential counts align to `redact_url` — the SKILL.md says "several" and defers to `redact_url` as the authority (3 query-string-auth APIs; 6 redacted params live in code, not prose). Mailto: SKILL.md states it is sourced from research-vault config and that vendored scripts don't read it.
- [ ] **Step 2 (C-5):** One vendoring-note line: upstream prose describes upstream's corpus.
- [ ] **Step 3 (item 12):** One vendoring-note section carrying the six upstream-fact annotations — copy verbatim from the cross-read report's triage (docs/2026-08-22-references-cross-read.md). Add the routing guards: no single-DOI lookups via paginate; the openalex row points at `openalex_abstract.py`; `OPENALEX_API_KEY` env caution.
- [ ] **Step 4:** Pins updated same commit; full suite; commit `fix: find-sources credential/vendoring corrections + cross-read wiring`.

