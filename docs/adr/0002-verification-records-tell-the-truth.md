# Verification records tell the truth: four states, MATCHED-only minting

Disposition: current (2026-09-06)

Status: accepted (2026-08-20)

Every mechanical check reports one of four states, and the distinctions are load-bearing: **MATCHED** (the check ran and the claim held), **UNMATCHED** (the check ran and the claim did not hold), **UNREACHABLE** (the check could not run — network down, service absent, file missing), **SKIPPED** (the check does not apply, determined automatically, never by choice). The decision: **an outage is never an accusation** — UNREACHABLE is not UNMATCHED and is never presented as failure — and **only a genuine pass mints a verification record**: a `verified` event `{by, at, check}` is appended only on MATCHED, never on SKIPPED, UNREACHABLE, or any aggregate that merely contains no failures. Verification records are therefore positive evidence that a specific check ran and held, and their absence means exactly "not verified" — never "failed".

**Emptiness is not a pass.** A tier or aggregate derived from checks requires at least one MATCHED result: an empty applicable-check set satisfies "everything applicable passed" vacuously, and vacuous truth certifies nothing. A value research-vault does not have is never written — no padded precision, no placeholder in a field other records key on, no substituting one field for another.

## Considered Options

Binary pass/fail (rejected: collapses "could not check" into one of the poles, so either outages accuse sound claims or they silently launder unverified ones). Minting on "no failures" (rejected: a run where every check was UNREACHABLE would mint the same record as a run where every check held — the record would no longer certify anything).

## Consequences

Verification events accumulate in git history and are never rewritten, so the honesty rule is retroactive by construction: every past record already means what this ADR says. Fail-closed publish gates inherit a real cost — an outage blocks publishing rather than being waved through — accepted because the alternative is records that certify less than they appear to. Trust tiers, the review queue, and any future auditor may consume the four states but may not collapse them.
