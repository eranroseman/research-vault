# Validation slice — findings log

Plan: docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md. Vault: ~/kh-vault → github.com/eranroseman/kv-vault. Friction is the product: every entry names what the harness did short of its prose.

## Phase 0

1. **scaffold inherits the system default branch** — created `master`; the first push to a `main`-expecting remote failed (`src refspec main does not match any`) and needed a hand rename. Fix class: scaffold sets `--initial-branch=main` (or documents the assumption). → setup-vault fix, post-Q batch candidate.
2. `doctor`'s autoexport guidance printed the exact Windows-side target via wslpath translation — the human step is copy-pasteable from the probe output. (Positive finding; the repair-guidance design working.)
3. `machine-config` probe accepted the minimal `.harness/machine.json` (mailto + empty path_map) on first try.

## Open Phase 0 items

- Human BBT step (target in doctor output above) → flips `autoexport` + `staleness`, unlocks the two `HARNESS_LIVE_AUTOEXPORT_VAULT` tests.
- `backup` warn: needs the author's one-line statement of the Zotero storage backup story (sync? disk image?) — recorded wherever doctor reads it.
