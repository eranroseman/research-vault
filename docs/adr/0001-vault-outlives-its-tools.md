# The vault outlives its tools

Disposition: current (2026-09-06)

Status: accepted (2026-08-20)

The vault is the researcher's permanent record; research-vault is one tool that operates on
it. The decision: **the vault must remain fully usable — readable, navigable, and adoptable by
other tools — if research-vault disappears.** The vault is therefore plain markdown + YAML
frontmatter in a git repository, with no runtime dependency on research-vault, and its
survivability guarantee is carried by a named external mechanism rather than by
research-vault-private convention.

**Current mechanism: conformance with OKF** (Open Knowledge Format — spec:
[GoogleCloudPlatform/open-knowledge-format `SPEC.md`](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)),
which was growing an ecosystem of agent-facing knowledge tools at adoption. **Conformance is
pinned, not merely versioned**: the vault targets OKF v0.2 as published at
`open-knowledge-format@ad30107`, `SPEC.md` sha256
`26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`. The pin exists because
v0.2 has already been amended in place without a version bump, so a bare version number is not
an anchor.

§11's three rules are reproduced verbatim rather than paraphrased, because the paraphrase is
what drifted:

1. Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter block.
2. Every frontmatter block contains a non-empty `type` field.
3. Every reserved filename (`index.md`, `log.md`) follows the structure in §8 and §9
   respectively when present.

§3.1 fixes reserved-ness to `index.md` and `log.md` alone, so authorship is not a criterion.
One exemption is recorded: `inbox/` holds knowledge candidates, not knowledge — human quick
capture may sit untyped until the triage stamp adds `type: "fleeting"`, because the record this
ADR protects does not include the airlock, and forcing metadata syntax on quick capture fails
in practice. Agent-written captures are typed at write; the exemption's register row prices the
residual. Rule 3 pulls in §8 — a nested `index.md` carries no frontmatter, and the bundle root
carries `okf_version` and nothing else — and §9 — a `log.md`, at the root or any level below
it, is date-grouped under `## YYYY-MM-DD` headings, newest first. The doctor's structure probes
are gone; verify's `okf-frontmatter`/`okf-structure` checks assert all three rules on the
commit surface, and the weekly CI job re-checks the pinned hash, so neither a drifting vault
nor a drifting spec passes unnoticed.

**Conformance is structural and semantic.** OKF's optional families define a consumer contract
on top of §11's structure — §7's actor prefixes, §5.3's trust tiers, §5.4's lifecycle values —
and the vault adopts each one wherever adoption is additive, because §4.1 admits producer keys
and §11 forbids consumers rejecting them, so the vault's own schema rides alongside OKF's
rather than inside its reserved names. No OKF-reserved key carries a value OKF would misread.
Every family carries a disposition — adopted or declined with a cost class — recorded once in
[docs/terminology.md](../terminology.md); silence is not a disposition.

The deviations that survive that rule are recorded there, not here. The load-bearing one is
per-claim attribution: it renders as pandoc `[@citekey, locator]` rather than §5.1's `[^id]`
footnote, a permanent mismatch with a toolchain the vault does not control (cost class 1). It is
a rendering difference over the same join — `sources[].id` is the citekey, and §5.1 directs
consumers to resolve attribution "through the matching entry, not by parsing the footnote prose"
— except for the pinpoint, which OKF v0.2 has no way to carry at all.

**Scope bound:** the vault preserves the *record*, not the evidence artifacts. PDFs and
snapshots live in Zotero storage, outside the git boundary — git is not the blob store — so
artifact recoverability is delegated to the user's Zotero sync/backup, with doctor's persistent
warning as the only compensating control. At solo scope this is a stated boundary, not a
compliance control.

## Considered Options

Mechanism alternatives, all rejected: **no named mechanism** — rely on markdown + git being
inherently portable (rejected: portable bytes are not an adoptable structure; a successor tool
would inherit files but no contract for navigating them). **Export-boundary-only projection** —
emit a conformant bundle only when publishing (rejected: insures published output, not the
living vault). **Structural conformance without OKF's vocabulary** (rejected on evidence: the
vault had already adopted §5.3's tier names and §7's actor prefixes for their own sake, so the
vocabulary was buying interop while the ADR claimed it could not; what the bound actually
protected was two toolchain contracts, which the deviation register now names individually).
**A bare version number as the anchor** (rejected: v0.2 was amended in place the day after
adoption, and nothing noticed).

## Consequences

The decision and the mechanism are severable: if OKF stagnates or a stronger survivability
standard emerges, the mechanism is replaced by amending this ADR — the decision itself is not
reopened. While OKF is the mechanism, conformance tracks it as it evolves. That obligation is
discharged by the pin and the probe, not by intention: a hash mismatch is a finding, and
reconciling it is the work. Accepted knowingly for a young, currently one-vendor spec.

The reserved files (`index.md`, `log.md`) are constraints on the vault scaffold, and their
shapes are OKF's, not ours. Adopting an OKF family means the vault gains a second spelling of
data it already holds; that redundancy is the price of a consumer needing no research-vault
knowledge to read the bundle. Revisit the mechanism (not the decision) if a future OKF version's
structural rules start imposing real costs on the vault's own tools.
