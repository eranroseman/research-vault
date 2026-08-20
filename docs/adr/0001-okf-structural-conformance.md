# The vault is a structurally conformant OKF v0.2 bundle

Status: accepted (2026-08-20)

The vault must remain usable if this harness disappears, and OKF (Open Knowledge Format — spec: github.com/GoogleCloudPlatform/knowledge-catalog, `okf/SPEC.md`) is growing an ecosystem of agent-facing knowledge tools. The vault therefore satisfies OKF v0.2's structural conformance rules: every machine-written `.md` carries parseable YAML frontmatter with a non-empty `type`; root `index.md` declares `okf_version` and lists the vault tree; root `log.md` is a machine-regenerated summary of recent activity linking the per-day log files. This is cheap because OKF conformance is structural only and explicitly tolerates unknown keys and type values, so all of our schema extensions ride inside it. Two bounds: vocabulary is NOT adopted (naming is governed by docs/terminology.md), and fleeting human-captured notes stay frontmatter-free — forcing metadata syntax on quick capture fails in practice, and OKF instructs consumers to tolerate nonconforming files.

## Considered Options

Export-boundary-only OKF projection — emit an OKF bundle only when publishing (rejected: insures published output, not the living vault). Borrow OKF vocabulary without structural conformance (rejected: the survivability gain is nearly free, so declining it needed a cost that doesn't exist).

## Consequences

We owe OKF version tracking — it is a young, currently one-vendor spec, and releases beyond v0.2 create a reconciliation obligation. The reserved files (`index.md`, `log.md`) become constraints on the vault scaffold. Revisit if conformance ever starts imposing real costs (toolchain mismatch, lost structure, forced misstatement).
