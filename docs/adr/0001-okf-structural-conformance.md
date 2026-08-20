# ADR 0001: The vault is a structurally conformant OKF v0.2 bundle

Date: 2026-08-20
Status: Accepted (author ruling)

## Context

The vault's survivability is a core design value: it must outlive this harness (spec §2 already demands "Obsidian-convention but not Obsidian-dependent"). OKF (Open Knowledge Format, help.openalex.org-adjacent ecosystem; spec at GoogleCloudPlatform/knowledge-catalog) is becoming its own ecosystem of agent-facing knowledge tools. A vault readable by that ecosystem is insured against this harness's disappearance and gains its tooling for free.

Two facts make conformance cheap, discovered on re-examination after an earlier ruling ("OKF-derived, documented divergence") had wrongly treated it as impossible:

1. **OKF conformance is structural, not vocabulary-total** — three rules only: parseable YAML frontmatter in every non-reserved `.md`, non-empty `type` in each, reserved files (`index.md`, `log.md`) shaped per spec when present.
2. **OKF's liberality clause tolerates unknown keys and unknown type values by design** — our schema extensions (`check` payloads, our type vocabulary, our provenance fields) ride inside conformance rather than breaking it.

The earlier impossibility ruling was the settled/sunk-cost error class (precedent treated as constraint); the cost model now governs decisions as well as names.

## Decision

The vault is a **structurally conformant OKF v0.2 bundle**:

- Root `index.md` carries `okf_version: "0.2"` frontmatter (the one place OKF permits index frontmatter) and doubles as the vault's home page — a dehydrated listing of the tree.
- Root `log.md` is the reserved chronological-history file, implemented as a **machine-maintained dehydrated tail** over the per-day `log/YYYY-MM-DD.md` files (single writer, regenerated — no second source of truth). Per-day files stay: the Obsidian Daily-notes surface (T1) outranks OKF (T4) in the vocabulary precedence order, and this shape satisfies both.
- Every **machine-written** `.md` carries parseable frontmatter with non-empty `type` — including `inbox/review-queue.md` and `AGENTS.md`.
- **Fleeting human notes are the tolerated residual**: forcing frontmatter on humans violates the Shipman/Marshall formality rule; OKF consumers are instructed to tolerate, and notes gain frontmatter when they graduate through triage.
- **Vocabulary is NOT adopted wholesale** — conformance is structural only. Names remain governed by the terminology decision record (CSL-first precedence stack; OKF sits at T4 with specific adoptions and documented deviations).

## Consequences

**Gained:** the vault is readable by OKF-ecosystem tools without this harness; survivability extends one ecosystem beyond Obsidian; OKF-borrowed vocabulary (actor convention, tier names, `verified` events, `dehydrated`, `canonical`) now sits inside a conformant container rather than a resemblance.

**Owed:** OKF **version tracking** — releases beyond v0.2 create a reconciliation obligation (the promotion-analysis cost of commitment, accepted knowingly for a young, currently one-vendor spec). Reserved-file shapes (`index.md`, `log.md`) are now constraints on the scaffold.

**Bounded:** conformance claims nothing about vocabulary alignment; deviations from OKF terms keep their documented forcing classes. If OKF's evolution ever demands vocabulary or structure that trips a real cost class (surface mismatch, information loss, falsification, collision), conformance is re-examined under the cost model — this ADR is information, not constraint.

## Alternatives considered

- **Export-boundary-only OKF projection** (emit an OKF bundle at publish, like the RO-Crate manifest; interior stays free): rejected because it insures only *published efforts*, not the living vault — the survivability argument is about the whole vault outliving the harness.
- **No conformance** (the prior ruling): rejected on the ecosystem-emergence fact plus the discovery that structural conformance costs ~three template changes and a typed frontmatter line.

## References

Spec §2 (vault substrate, amended 2026-08-20) · docs/2026-08-20-terminology.md §8 (promotion analysis, OKF upgraded to structural conformance target) · §10 rename-wave manifest (implementation rides the wave) · OKF spec: github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
