# Validation slice — findings log

Plan: docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md. Vault: ~/kh-vault → github.com/eranroseman/kv-vault. Friction is the product: every entry names what the harness did short of its prose.

## Phase 0

1. **scaffold inherits the system default branch** — created `master`; the first push to a `main`-expecting remote failed (`src refspec main does not match any`) and needed a hand rename. Fix class: scaffold sets `--initial-branch=main` (or documents the assumption). → setup-vault fix, post-Q batch candidate.
2. `doctor`'s autoexport guidance printed the exact Windows-side target via wslpath translation — the human step is copy-pasteable from the probe output. (Positive finding; the repair-guidance design working.)
3. `machine-config` probe accepted the minimal `.harness/machine.json` (mailto + empty path_map) on first try.

## Phase 0 — CLOSED (2026-08-22)

4. **Key regeneration executed pre-export** (author-ruled window): formula `authEtal2.lower + year | shorttitle.lower + year`; periods survive BBT sanitization (`abbasian.etal2024` verified); disambiguation postfixes working. 1,407 items exported (2.2 MB sorted CSL JSON).
5. **Formula finding**: the `|` fallback never fires for author-less items — a pattern "succeeds" on year alone (undocumented threshold), yielding 60/1,407 bare-year keys (`2025c`), all webpage/software/dataset items. RULED: accepted; the fix lives at admission (set author/organization when admitting web sources — the enrichment discipline), not in undocumented formula semantics. Reopen only if a bare-year key reaches a literature note.
6. **autoexport MATCHED, staleness MATCHED** on first doctor run after the human step; the on-demand comparison export byte-matches. The wizard-form walkthrough prose was sufficient — no missteps.
7. **24 `HARNESS_LIVE_AUTOEXPORT_VAULT`-gated tests pass** on first run (the gated family was larger than the 2 headline skips).

## Open items

- `backup` warn: author's one-line Zotero storage backup statement still owed.
- memoria citekey sweep (author's other system) after the regeneration — author-owned, priced at ruling time.

## Original Phase 0 open items (retained as written)

- Human BBT step (target in doctor output above) → flips `autoexport` + `staleness`, unlocks the two `HARNESS_LIVE_AUTOEXPORT_VAULT` tests.
- `backup` warn: needs the author's one-line statement of the Zotero storage backup story (sync? disk image?) — recorded wherever doctor reads it.
