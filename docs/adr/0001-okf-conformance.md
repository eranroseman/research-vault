# The vault is a structurally conformant OKF bundle

Status: accepted (2026-08-20)

The vault must remain usable if this harness disappears, and OKF (Open Knowledge Format — spec: github.com/GoogleCloudPlatform/knowledge-catalog, `okf/SPEC.md`) is growing an ecosystem of agent-facing knowledge tools. The vault therefore maintains **structural conformance with OKF at its current version** — v0.2 at adoption, whose rules are: every machine-written `.md` carries parseable YAML frontmatter with a non-empty `type`; root `index.md` declares the OKF version and lists the vault tree; root `log.md` is a machine-regenerated summary of recent activity linking the per-day log files. Conformance is cheap because OKF's rules are structural only and explicitly tolerate unknown keys and type values, so the vault's own schema rides inside them. Two bounds are part of this decision: **conformance is structural, not vocabulary** — OKF tools parse structure, not words, so adopting OKF's words would buy no additional interop while breaking contracts with tools the vault lives in (pandoc/CSL `[@citekey]` citations versus OKF's footnote attribution; stance-typed claim links versus its untyped lineage) — and **fleeting human-captured notes stay frontmatter-free**: forcing metadata syntax on quick capture fails in practice, and OKF instructs consumers to tolerate nonconforming files.

## Considered Options

Pin to OKF v0.2 permanently (rejected: a frozen version stops tracking the ecosystem the decision exists to join). Export-boundary-only OKF projection — emit a bundle only when publishing (rejected: insures published output, not the living vault). Borrow OKF vocabulary without structural conformance (rejected: the survivability gain is nearly free, so declining it needed a cost that doesn't exist).

## Consequences

Conformance tracks OKF as it evolves: each release creates a reconciliation obligation, and that tracking is the decision's substance, not a side cost — accepted knowingly for a young, currently one-vendor spec. The reserved files (`index.md`, `log.md`) are constraints on the vault scaffold. Revisit if a future OKF version's structural rules start imposing real costs on the vault's own tools (toolchain mismatch, lost structure, forced misstatement).
