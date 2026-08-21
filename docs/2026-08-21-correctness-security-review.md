# Correctness & security review — integrated post-wave main (7ebcfd4..b38a607)

Date: 2026-08-21. Dedicated pass per superpowers:requesting-code-review (fresh reviewer subagent, five-class brief: evidence-text injection, transactional interleaving, contents:write CI, hand-written inbox lines, URL construction). Critical finding independently re-verified by direct read before recording. No vault exists yet — zero live exposure; all fixes land in the pre-baseline window.

## Findings

### Critical 1 — evidence-controlled `pageLabel`/`title` inject forged in-managed quote claims with a valid managed witness

`render_claim` (notes.py:251) interpolates `annotation['pageLabel']` raw into the claim line; `normalize_annotation`'s `_text` (__main__.py:49) only type-filters, stripping nothing. A page label containing newlines emits attacker-authored extra claim lines inside the managed region; marker count is unchanged so `managed-sha256` stays MATCHED; `parse_claims` marks the forged quote `in_managed=True`; `check_quote` then mints a verified event for text that was never an annotation. The `# {title}` heading (notes.py:109) is the same class. Root cause: the render-boundary neutralization discipline exists (annotationText per-line `> ` prefix, comment whitespace-collapse, `_escape_selector`) but three channels missed it.

**Fix contract:** neutralize at the render boundary — reject or line-strip `pageLabel`, `citekey`, `title` (and every scalar interpolated into managed structure) on `\r`/`\n`; plus a self-verification in `render_note`: re-run `parse_claims` over the rendered managed body and assert exactly the intended claim ids/count before returning (output round-trip honesty — the emitter proves its own canonical form). Regression test per channel.

### Important 2 — `frontmatter._emit_scalar` (frontmatter.py:38) escapes only `\\` and `"`

Evidence strings with line breaks routed into frontmatter scalars (title→aliases notes.py:204, doi/url notes.py:193-196) serialize to YAML the parser cannot read back, or terminate the block early via an embedded `\n---\n` — dropping `managed-sha256`/`generated`. A valid Zotero item can thus produce a machine-projected note whose witness is permanently UNMATCHED (fail-closed DoS that re-poisons on every render). **Fix:** escape control characters in `_emit_scalar` (and/or reject at the render boundary with finding 1).

### Minor 3 — `note_path` citekey guard (notes.py:94-104) rejects `/`, `\`, NUL, dot-segments, absolute — but not `\r`/`\n`

Low reachability (BBT citekeys are charset-restricted); add line-break rejection for depth.

## Held up under scrutiny (checked, no new findings)

Transactional core (private `GIT_INDEX_FILE` trees, HEAD CAS, live-index lock with fstat identity re-validation, rollback that never clobbers a successor — "live index untouched" holds) · contents:write RW workflow (token scope, env-indirected `${{ }}`, validated CSV ingestion) · inbox ack-scoping on hand-written lines · pathcodec on hostile input · hooks fail-open (crash ⇒ exit 0 verified in both).

## Disposition

Fixes are the FIRST task of the pre-baseline batch — they outrank the over-engineering cuts and the maintenance follow-ups, and share the batch's window (all AST churn lands before Plan Q's mutation manifests). Independent verification: `/code-review ultra` (author-triggered) runs AFTER the fixes land, over the trust-critical modules, so it verifies the fix rather than re-finding the known hole.
