# Selector Escape Hardening — Task

> **STATUS 2026-08-22: items 1–2 merged (d730511); items 3–4 STILL OPEN** — the executing worktree forked from the two-item version of this doc. Verified on main: `subdirectory=core` present in both CI templates; `.detail` at 4 sites in `tests/test_scaffold_live.py`. Remainder is a second pass: items 3 and 4 only, acceptance INCLUDING the live legs (which cannot pass until item 4 lands).

> From the 2026-08-22 local deep review of 1f337a3..HEAD (verdict: sound, ready for Plan Q, two Minors). Single micro-task; do not fold into the rename task (that one is zero-behavior-change by contract).

1. **`notes.py` `_escape_selector`**: extend neutralization to the full serializer `_CONTROL` class (`[\x00-\x1f\x7f\x85  ]`) — entity-escape or strip, matching the existing `\r`/`\n` treatment — so evidence-controlled selector context (PDF-extracted prefix/suffix) has boundary neutralization like every other channel instead of relying on the render_note round-trip backstop alone. Regression test: a context prefix carrying ` - (quote) [@evil] ^c-x` renders with the separator neutralized and the round-trip check quiet.
2. **`frontmatter.py` reject-class comment**: reword "exactly what str.splitlines() treats as a line break" → "a superset of the parser's line-break set" (the class also rejects DEL and non-break C0 — direction safe, wording overstates).

3. **CI templates: stale `#subdirectory=core`** (parked from the package-rename merge; pre-existing — Plan L's flip orphaned it): both `knowledge_harness/templates/ci/*.yml` install lines drop the subdirectory fragment (the package now lives at repo root). Must land before any vault scaffolds from these templates. Update any template test asserting the install line.

4. **Live-leg rename fallout** (found 2026-08-22 by the first live run since Plan R): `tests/test_scaffold_live.py` still reads the pre-unification `.detail` attribute at lines 146-153 — rename to `.reason`, then judged-grep ALL env-gated test files for retired vocabulary (`.detail`, old check ids, `entry_id`, `RepoPathValue`): gated tests are invisible to offline suite-green, so the wave's acceptance never executed them.

Acceptance: **full suite green INCLUDING the live legs** (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>` — Zotero confirmed reachable 2026-08-22); one commit; merge + push in the same motion. (The one-line ruff-format drift at `tests/test_frontmatter.py:86` is Plan Q's canonicalization business — noted, not this task's.)
