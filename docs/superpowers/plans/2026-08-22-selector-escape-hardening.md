# Selector Escape Hardening — Task

> From the 2026-08-22 local deep review of 1f337a3..HEAD (verdict: sound, ready for Plan Q, two Minors). Single micro-task; do not fold into the rename task (that one is zero-behavior-change by contract).

1. **`notes.py` `_escape_selector`**: extend neutralization to the full serializer `_CONTROL` class (`[\x00-\x1f\x7f\x85  ]`) — entity-escape or strip, matching the existing `\r`/`\n` treatment — so evidence-controlled selector context (PDF-extracted prefix/suffix) has boundary neutralization like every other channel instead of relying on the render_note round-trip backstop alone. Regression test: a context prefix carrying ` - (quote) [@evil] ^c-x` renders with the separator neutralized and the round-trip check quiet.
2. **`frontmatter.py` reject-class comment**: reword "exactly what str.splitlines() treats as a line break" → "a superset of the parser's line-break set" (the class also rejects DEL and non-break C0 — direction safe, wording overstates).

Acceptance: suite green at baseline; one commit; merge + push in the same motion.
