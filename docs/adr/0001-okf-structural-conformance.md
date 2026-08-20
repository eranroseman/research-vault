# The vault is a structurally conformant OKF v0.2 bundle

Status: accepted (2026-08-20)

The vault must outlive this harness, and OKF is becoming an ecosystem of agent-facing knowledge tools — so the vault conforms to OKF v0.2's structural rules (parseable frontmatter with non-empty `type` in every machine-written `.md`; root `index.md` with `okf_version`; root `log.md` as a machine-maintained dehydrated tail over the per-day log files). Conformance is cheap because OKF is structural-only and tolerates unknown keys/types by design, so our schema extensions ride inside it; vocabulary is NOT adopted — names stay governed by docs/terminology.md (OKF at T4). Fleeting human notes remain frontmatter-free (Shipman/Marshall rule); OKF consumers tolerate them.

## Considered Options

Export-boundary-only OKF projection (rejected: insures published efforts, not the living vault). Vocabulary-borrowing without structural conformance (rejected: conformance is structural-only and tolerates unknown keys, so it costs almost nothing beyond the version-tracking commitment — the survivability gain is nearly free).

## Consequences

We owe OKF version tracking (young, one-vendor spec — reconciliation on 0.3+). Reserved-file shapes constrain the scaffold. If OKF's evolution trips a real cost class, this decision is re-examined under the cost model — this ADR is information, not constraint.
