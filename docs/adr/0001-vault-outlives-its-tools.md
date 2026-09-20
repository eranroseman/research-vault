# The vault outlives its tools

Status: accepted (2026-08-20)

The vault is the researcher's permanent record; research-vault is one tool that operates on it. The decision: **the vault must remain fully usable — readable, navigable, and adoptable by other tools — if research-vault disappears.** The vault is therefore plain markdown + YAML frontmatter in a git repository, with no runtime dependency on research-vault, and its survivability guarantee is carried by a named external mechanism rather than by research-vault-private convention.

**The mechanism is conformance with the Open Knowledge Format (OKF), pinned, not merely versioned.** The pin — the OKF commit and the `SPEC.md` digest the vault targets — has one writer, `.github/okf-pin.json`; the rules the vault meets, how conformance is discharged and the conformance deviation register are [docs/agents/okf-conformance.md](../agents/okf-conformance.md).

**Scope bound:** the vault preserves the *record*, not evidence artifacts. PDFs and snapshots live in Zotero storage, outside the git boundary, so artifact recoverability is delegated to Zotero sync/backup, with doctor's persistent warning as the only compensating control.

## Considered Options

**No named mechanism**, relying on markdown + git alone (rejected: portable bytes aren't an adoptable structure). **Export-boundary-only projection**, emitting a conformant bundle only at publish time (rejected: insures published output, not the living vault). **Structural conformance without OKF's vocabulary** (rejected: the vault had already adopted OKF's tier names and actor prefixes for their own sake, so the vocabulary was buying real interop, not just structure).

## Consequences

The decision and the mechanism are severable: if OKF stagnates, the mechanism is replaced by amending this ADR without reopening the decision. Conformance is discharged by the pin and a probe, not by intention — a hash mismatch is a finding, and reconciling it is the work. Adopting a family means the vault carries a second spelling of data it already holds, which is the price of a consumer needing no research-vault knowledge to read the bundle.
