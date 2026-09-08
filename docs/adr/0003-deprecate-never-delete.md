# Vault knowledge-state records deprecate, never delete

Status: accepted (2026-08-20); amended 2026-09-07 — examples and the acknowledgment-scope sentence follow the ingest redesign, decision unchanged

Records of what was known, decided, or found — captured sources and their lifecycle transitions, verification events, review-inbox findings and their acknowledgments, update notices — change state only by recorded transition (new state, actor, date); they are never silently removed or overwritten. A source that leaves the library is reported (`trashed`, `deleted`, `merged`) and its note is kept, not deleted; a superseded claim is deprecated with a `superseded-by` pointer to its successor; a contradiction between sources is preserved as two linked claims with stance links, never resolved by erasing one. The decision exists because the vault's value as a research record depends on negative and outdated knowledge staying inspectable: what a source's note said when the source left the library, what a claim said before correction, that a finding was seen and acknowledged rather than never raised.

**Scope bound.** Records only, in the vault only. Synthesis prose is freely rewritable (it asserts arrangement, not evidence). Repo artifacts — plans, docs, code — are outside this ADR: deleting them is normal hygiene, and this ADR never justifies keeping a dead file.

## Considered Options

Delete-with-git-history-as-audit-trail (rejected: history preserves bytes, not meaning — a deleted source's exclusion rationale becomes archaeology instead of a queryable field, and every consumer would need to walk history to know what was ever considered). Free overwrite of state fields (rejected: loses the actor and date that make a transition accountable, and lets contradictions vanish without a trace).

## Consequences

The vault grows monotonically in records; noise management happens by state and filtering (lifecycle reason codes, superseded markers, acknowledgments), never by removal. Acknowledgments are standing data identified by a scope derived from the check, the target and the target's content hash — they persist, and lapse when the target's body changes, rather than being cleaned up. Any future compaction or archival feature must preserve transitions, not collapse them.
