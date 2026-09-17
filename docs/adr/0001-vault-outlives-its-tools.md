# The vault outlives its tools

Status: accepted (2026-08-20)

The vault is the researcher's permanent record; research-vault is one tool that operates on
it. The decision: **the vault must remain fully usable — readable, navigable, and adoptable by
other tools — if research-vault disappears.** The vault is therefore plain markdown + YAML
frontmatter in a git repository, with no runtime dependency on research-vault, and its
survivability guarantee is carried by a named external mechanism rather than by
research-vault-private convention.

**Mechanism: conformance with OKF** (Open Knowledge Format — spec:
[GoogleCloudPlatform/open-knowledge-format `SPEC.md`](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)).
**Conformance is pinned, not merely versioned**: the vault targets OKF v0.2 as published at
`open-knowledge-format@ad30107`, `SPEC.md` sha256
`26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101` — a bare version number was
rejected because v0.2 was amended in place the day after adoption, and nothing noticed.

§11's three rules are reproduced verbatim, because paraphrase is what drifted:

1. Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter block.
2. Every frontmatter block contains a non-empty `type` field.
3. Every reserved filename (`index.md`, `log.md`) follows the structure in §8 and §9
   respectively when present.

§3.1 fixes reserved-ness to `index.md` and `log.md` alone. Two exemptions are recorded:
`inbox/` fleeting captures may sit untyped until triage stamps `type: "fleeting"` (this ADR
protects the record, not the airlock); and `wiki/index.md`, written by an adopted compile tool
whose own lint requires frontmatter that OKF forbids on an index — the vault carries this
one-file deviation rather than fork the tool. Both are priced in the deviation register at
[docs/agents/terminology.md](../agents/terminology.md).

**Conformance is structural and semantic.** Beyond §11, the vault adopts OKF's optional
families (actor prefixes, trust tiers, lifecycle values) wherever adoption is additive, since
§4.1 permits producer keys alongside OKF's reserved ones. Deviations from an adopted family are
recorded in that same register, not here — except the load-bearing one: per-claim attribution
renders as pandoc `[@citation-key, locator]` rather than §5.1's `[^id]` footnote, a permanent
mismatch with a toolchain the vault doesn't control. `sources[].id` is still the join key OKF
expects; only the pinpoint locator has no home in OKF v0.2.

**Scope bound:** the vault preserves the *record*, not evidence artifacts. PDFs and snapshots
live in Zotero storage, outside the git boundary, so artifact recoverability is delegated to
Zotero sync/backup, with doctor's persistent warning as the only compensating control.

## Considered Options

**No named mechanism**, relying on markdown + git alone (rejected: portable bytes aren't an
adoptable structure). **Export-boundary-only projection**, emitting a conformant bundle only at
publish time (rejected: insures published output, not the living vault). **Structural
conformance without OKF's vocabulary** (rejected: the vault had already adopted OKF's tier
names and actor prefixes for their own sake, so the vocabulary was buying real interop, not
just structure).

## Consequences

The decision and the mechanism are severable: if OKF stagnates, the mechanism is replaced by
amending this ADR without reopening the decision. Conformance is discharged by the pin and a
probe, not by intention — a hash mismatch is a finding, and reconciling it is the work. The
reserved files are constraints on the vault scaffold, in OKF's shape, not ours; adopting a
family means the vault carries a second spelling of data it already holds, which is the price
of a consumer needing no research-vault knowledge to read the bundle.
