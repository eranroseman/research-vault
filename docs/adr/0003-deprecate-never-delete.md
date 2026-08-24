# Vault knowledge-state records deprecate, never delete

Status: accepted (2026-08-20)

Records of what was known, decided, or found — admitted sources and their screening states, verification events, review-inbox findings and their acknowledgments, update notices — change state only by recorded transition (new state, actor, date); they are never silently removed or overwritten. An excluded source is marked `excluded`, not deleted; a superseded claim is marked superseded and points to its successor; a contradiction between sources is preserved as two linked claims with stance links, never resolved by erasing one. The decision exists because the vault's value as a research record depends on negative and outdated knowledge staying inspectable: why a source was excluded, what a claim said before correction, that a finding was seen and acknowledged rather than never raised.

**Scope bound — two boundaries.** *Inner:* this governs knowledge-state records, not prose arrangement. The synthesis layer is freely rewritable by design — reorganizing, rewording, and restructuring synthesis notes is normal work, because they assert arrangement, not evidence. Git history is the recovery net for prose; recorded transitions are the contract for state. *Outer:* this is **vault doctrine only**. Repository artifacts — plans, docs, code, tooling — are outside its jurisdiction entirely: they live under git, deletion loses nothing a reader can't recover, and removing what no longer earns its tree position is normal hygiene. Citing this ADR to keep a dead repo file (a tombstone, a stub, a superseded plan) is a misapplication.

## Considered Options

Delete-with-git-history-as-audit-trail (rejected: history preserves bytes, not meaning — a deleted source's exclusion rationale becomes archaeology instead of a queryable field, and every consumer would need to walk history to know what was ever considered). Free overwrite of state fields (rejected: loses the actor and date that make a transition accountable, and lets contradictions vanish without a trace).

## Consequences

The vault grows monotonically in records; noise management happens by state and filtering (screening states, superseded markers), never by removal. Acknowledgments are standing data scoped to content hashes — they persist and lapse by scope mismatch rather than being cleaned up. Any future compaction or archival feature must preserve transitions, not collapse them.
